# -*- coding: utf-8 -*-
"""Confere os fatos de um post do blog contra as fontes antes de publicar (08/11/2026).

Regra: toda data (dd/mm/aaaa ou dd/mm), todo valor em R$, todo percentual e todo número de 3 ou mais
algarismos (vagas, inscritos) que aparece no post precisa aparecer, igual, em pelo menos uma fonte:
  - o guia do concurso (_config/guias/<guia>.md), se o post tiver "guia:";
  - os textos salvos em <dados>/fontes/<slug>/*.txt (documento oficial baixado pela rotina);
  - as fichas em <dados>/fichas/*.md cujo nome bate com "ficha:" do cabeçalho (lista separada por vírgula).
Valores que o próprio post calcula (datas de fases de um cronograma, por exemplo) vão em "calculado:"
no cabeçalho, como lista JSON, e ficam à vista de quem revisa.

Uso: python _config/blog_conferir.py [--dados ../escudo-dados] [--atualizacoes] _config/blog/arquivo.md [...]
(--atualizacoes também confere _config/guias/atualizacoes.json, a linha do tempo dos guias)
Sai com código 1 se algum post falhar, listando o que não foi achado.
"""
import json, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "_config"))


def le(md_path):
    txt = md_path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", txt, re.S)
    meta, corpo = {}, txt
    if m:
        corpo = m.group(2)
        for linha in m.group(1).splitlines():
            if ":" in linha and not linha.startswith(" "):
                k, v = linha.split(":", 1)
                v = v.strip()
                if v.startswith("[") or v.startswith("{"):
                    try:
                        v = json.loads(v)
                    except ValueError:
                        pass
                elif len(v) >= 2 and v[0] == v[-1] == '"':
                    v = v[1:-1]
                meta[k.strip()] = v
    return meta, corpo


PADROES = [
    r"\b\d{2}/\d{2}/\d{4}\b",                 # 22/12/2026
    r"\b\d{1,2}/\d{2}\b(?!/)",                # 09/11
    r"R\$\s?[\d.]+(?:,\d{2})?",               # R$ 5.482,51
    r"\b\d+(?:,\d+)?\s?%",                    # 50%
    r"\b\d{1,3}(?:\.\d{3})+\b",               # 2.000, 27.279
    r"\b\d{3,}\b",                             # 110, 2026 (ano entra aqui também)
]


def normaliza(s):
    s = s.replace(" ", " ")
    s = re.sub(r"R\$\s+", "R$ ", s)
    return re.sub(r"(\d)\s+%", r"\1%", s)


def fatos(corpo):
    corpo = re.sub(r"\]\([^)]*\)", "]", corpo)          # tira URLs de links
    corpo = re.sub(r"<!--.*?-->", "", corpo, flags=re.S)
    achados = []
    usados = []
    for p in PADROES:
        for m in re.finditer(p, corpo):
            if any(a <= m.start() < b for a, b in usados):
                continue
            usados.append((m.start(), m.end()))
            achados.append(normaliza(m.group(0)).strip())
    return sorted(set(achados))


def variantes(f):
    """Formas equivalentes aceitas na fonte (09/11 também vale como 09/11/2026; R$ 110,00 vale R$ 110)."""
    v = {f}
    if re.fullmatch(r"\d{1,2}/\d{2}", f):
        v.add(f.zfill(5))
    if f.startswith("R$ ") and "," not in f:
        v.add(f + ",00")
    if f.startswith("R$ ") and f.endswith(",00"):
        v.add(f[:-3])
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", f):
        v.add(f.replace(".", ""))
    return v


def fontes_do_post(meta, dados):
    textos = []
    g = meta.get("guia")
    if g and (RAIZ / "_config" / "guias" / (g + ".md")).exists():
        textos.append((RAIZ / "_config" / "guias" / (g + ".md")).read_text(encoding="utf-8"))
    if dados:
        for t in sorted((dados / "fontes" / meta.get("slug", "-")).glob("*.txt")):
            textos.append(t.read_text(encoding="utf-8", errors="ignore"))
        fichas = meta.get("ficha") or []
        if isinstance(fichas, str):
            fichas = [x.strip() for x in fichas.split(",") if x.strip()]
        for f in fichas:
            arq = dados / "fichas" / (f if f.endswith(".md") else f + ".md")
            if arq.exists():
                textos.append(arq.read_text(encoding="utf-8"))
    return normaliza("\n".join(textos))


def confere(arq, dados):
    meta, corpo = le(arq)
    texto_fontes = fontes_do_post(meta, dados)
    calculado = {normaliza(str(x)) for x in (meta.get("calculado") or [])}
    ano = re.compile(r"20\d{2}")
    faltam = []
    resumo = " \n".join(str(b) for _, b in (meta.get("resumo") or []))
    extra = "\n".join(str(meta.get(k, "")) for k in ("descricao", "h1", "titulo_seo", "capa_titulo"))
    for f in fatos(corpo + "\n" + extra + "\n" + resumo):
        if f in calculado or ano.fullmatch(f):
            continue
        if not any(v in texto_fontes for v in variantes(f)):
            faltam.append(f)
    if not texto_fontes.strip():
        faltam.insert(0, "(nenhuma fonte encontrada: ponha guia:, ficha: ou salve o documento em fontes/%s/)" % meta.get("slug"))
    if not meta.get("fontes"):
        faltam.insert(0, "(cabeçalho sem 'fontes': todo post precisa do link do documento oficial)")
    return faltam


def confere_atualizacoes(dados):
    """Cada linha de _config/guias/atualizacoes.json: fatos precisam estar no guia ou em <dados>/fontes/<guia>/."""
    arq = RAIZ / "_config" / "guias" / "atualizacoes.json"
    ruim = 0
    if not arq.exists():
        return 0
    for guia, itens in json.loads(arq.read_text(encoding="utf-8")).items():
        if guia.startswith("_"):
            continue
        fontes = fontes_do_post({"guia": guia, "slug": guia}, dados)
        for a in itens:
            faltam = [f for f in fatos(a["texto"]) if not re.fullmatch(r"20\d{2}", f)
                      and not any(v in fontes for v in variantes(f))]
            if not a.get("fonte"):
                faltam.insert(0, "(sem 'fonte')")
            if faltam:
                ruim += 1
                print("BARRADO atualização %s %s\n  não achado nas fontes: %s" % (guia, a["data"], ", ".join(faltam)))
            else:
                print("ok atualização %s %s" % (guia, a["data"]))
    return ruim


def main():
    args = sys.argv[1:]
    dados = None
    if "--dados" in args:
        i = args.index("--dados")
        dados = pathlib.Path(args[i + 1]).resolve()
        del args[i:i + 2]
    ruim = 0
    if "--atualizacoes" in args:
        args.remove("--atualizacoes")
        ruim += confere_atualizacoes(dados)
        if not args:
            sys.exit(1 if ruim else 0)
    if not args:
        args = [str(p) for p in sorted((RAIZ / "_config" / "blog").glob("*.md"))]
    for a in args:
        faltam = confere(pathlib.Path(a), dados)
        if faltam:
            ruim += 1
            print("BARRADO %s\n  não achado nas fontes: %s" % (pathlib.Path(a).name, ", ".join(faltam)))
        else:
            print("ok %s" % pathlib.Path(a).name)
    sys.exit(1 if ruim else 0)


if __name__ == "__main__":
    main()
