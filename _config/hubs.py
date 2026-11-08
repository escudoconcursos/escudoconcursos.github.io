# -*- coding: utf-8 -*-
"""Páginas de carreira e de estado (onda 2 do plano de SEO, 07/11/2026). Idempotente.

Entrada: _config/hubs.json (textos e filtros), produtos.json, nomes.json e os guias em _config/guias/.
Saída:
  - /<slug>/index.html de cada página (ex.: /concursos-policiais/, /concursos-pernambuco/), com texto de
    abertura, tabela (concurso, banca, situação, prova, guia), os mesmos cartões da home e links para as
    outras páginas. Dados estruturados: CollectionPage + ItemList + BreadcrumbList.
  - na home, o bloco "Concursos por carreira e por estado" (entre <!-- hubs:inicio --> e <!-- hubs:fim -->);
  - seção "Concursos por carreira e por estado" no llms.txt.
Só entram cursos com prova futura ou sem data (a mesma regra da home). Página sem curso ativo não é gerada.

Uso: PYTHONIOENCODING=utf-8 python _config/hubs.py   (depois de vitrine.py; antes de onda1.py e aplicar.py)
O onda1.py usa hub_da_carreira() e hub_do_estado() daqui para a trilha e o "Ver todos" das páginas de curso.
"""
import html, json, pathlib, re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((RAIZ / "_config" / "site.json").read_text(encoding="utf-8"))
BASE = (CFG.get("url_base") or "https://escudoconcursos.com.br/").rstrip("/") + "/"
HUBS = json.loads((RAIZ / "_config" / "hubs.json").read_text(encoding="utf-8"))["hubs"]
NOMES = json.loads((RAIZ / "_config" / "nomes.json").read_text(encoding="utf-8"))["cursos"]
DADOS = json.loads((RAIZ / "_config" / "produtos.json").read_text(encoding="utf-8"))
UF_EXTRA = {"ufba-assistente-2026": "BA"}  # curso sem página própria (link direto para a Hotmart)
e = lambda s: html.escape(str(s), quote=True)


def _vitrine():
    """Pega cartao(), ativo e afins do vitrine.py sem rodar a parte que grava a home."""
    src = (RAIZ / "_config" / "vitrine.py").read_text(encoding="utf-8")
    cabeca = src[: src.index("\nabertos = [")]
    ns = {"__file__": str(RAIZ / "_config" / "vitrine.py")}
    exec(compile(cabeca, "vitrine.py", "exec"), ns)
    return ns


def uf(pid):
    return NOMES.get(pid, {}).get("uf") or UF_EXTRA.get(pid)


def guarda(pid):
    return NOMES.get(pid, {}).get("sigla", "").startswith(("GM ", "GCM "))


def entra(f, p):
    if "carreira" in f and p.get("carreira") != f["carreira"]:
        return False
    if "guarda" in f and guarda(p["id"]) != f["guarda"]:
        return False
    if "uf" in f and uf(p["id"]) != f["uf"]:
        return False
    return True


def hub_da_carreira(pid):
    """Slug da página de carreira do curso (a primeira que o inclui), ou None."""
    p = next((x for x in DADOS["produtos"] if x["id"] == pid), None)
    for h in HUBS:
        if h["tipo"] == "carreira" and p and entra(h["filtro"], p):
            return h
    return None


def hub_do_estado(pid):
    for h in HUBS:
        if h["tipo"] == "estado" and h["filtro"].get("uf") == uf(pid):
            return h
    return None


def guias():
    """{curso_id: {slug, banca, situacao}} lidos do cabeçalho dos guias."""
    out = {}
    for arq in sorted((RAIZ / "_config" / "guias").glob("concurso-*.md")):
        m = re.match(r"^---\n(.*?)\n---\n", arq.read_text(encoding="utf-8"), re.S)
        if not m:
            continue
        meta = {}
        for linha in m.group(1).splitlines():
            if ":" in linha:
                k, v = linha.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
        ids = meta.get("curso_id", "")
        ids = json.loads(ids) if ids.startswith("[") else [ids]
        for i in ids:
            out[i] = {"slug": meta.get("slug", arq.stem), "banca": meta.get("banca", ""), "situacao": meta.get("situacao", "")}
    return out


def ld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=1) + "\n</script>"


def relativo(cartao_html):
    """Os cartões da home usam caminhos a partir da raiz; aqui a página está uma pasta abaixo."""
    return re.sub(r'(href|src)="(?!https?:|\.\./|#|mailto:)([^"]+)"', r'\1="../\2"', cartao_html)


def nome_curso(p):
    n = NOMES.get(p["id"])
    return "%s: %s" % (n["sigla"], n["cargo"]) if n else "%s (%s)" % (p["titulo"], p["tag"])


def tabela(prods, G, V):
    linhas = []
    for p in prods:
        g = G.get(p["id"], {})
        href = p["link"] if p["link"].startswith("http") else "../" + p["link"]
        prova = V["ddmm"](p["prova"], True) if p.get("prova") and p["prova"] != V["SEM_DATA"] else "a definir"
        guia = '<a href="../%s/">Guia</a>' % e(g["slug"]) if g.get("slug") else ""
        banca = re.sub(r"\s*\(.*?\)", "", g.get("banca", "")) or "a definir"
        situ = g.get("situacao") or ("pré-edital" if prova == "a definir" else "")
        linhas.append("<tr><td><a href=\"%s\">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                      % (e(href), e(nome_curso(p)), e(banca), e(situ), prova, guia))
    return ('<div class="guia-tabela"><table><thead><tr><th>Concurso</th><th>Banca</th><th>Situação</th><th>Prova</th>'
            '<th>Guia</th></tr></thead><tbody>\n%s\n</tbody></table></div>' % "\n".join(linhas))


def monta(h, prods, ativos_por_hub, G, V, modelo):
    slug, url = h["slug"], BASE + h["slug"] + "/"
    grupo = "Concursos por carreira" if h["tipo"] == "carreira" else "Concursos por estado"
    intro = "\n".join("<p>%s</p>" % e(par) for par in h["intro"])
    cards = "\n".join(relativo(c) for c, _ in sorted((V["cartao"](p) for p in prods), key=lambda t: t[1]))
    outros = lambda tipo: " · ".join('<a href="../%s/">%s</a>' % (x["slug"], e(x["nome"]))
                                     for x in HUBS if x["tipo"] == tipo and x["slug"] != slug and ativos_por_hub.get(x["slug"]))
    artigo = (intro + "\n<h2>Concursos desta página</h2>\n" + tabela(prods, G, V))
    cursos = ('\n    <section class="hub-cursos" aria-labelledby="t-hub-cursos">\n'
              '      <h2 id="t-hub-cursos">Cursos em PDF <em>(%d)</em></h2>\n'
              '      <p class="vitrine-info">Ordenados pelo prazo mais próximo: cupom, inscrições ou prova.</p>\n'
              '      <ul class="produtos" data-vitrine>\n%s\n      </ul>\n'
              '      %s\n'
              '      <nav class="hub-outros" aria-label="Outras páginas de concursos">\n'
              '        <p><b>Por carreira:</b> %s</p>\n        <p><b>Por estado:</b> %s</p>\n'
              '        <p><a href="../#cursos">Ver todos os cursos abertos</a></p>\n      </nav>\n    </section>\n'
              % (len(prods), cards, V["pedido_html"](), outros("carreira"), outros("estado")))
    itens = [{"@type": "ListItem", "position": i + 1, "name": nome_curso(p),
              "url": p["link"] if p["link"].startswith("http") else BASE + p["link"]} for i, p in enumerate(prods)]
    blocos = [
        ld({"@context": "https://schema.org", "@type": "CollectionPage", "name": h["h1"], "description": h["descricao"],
            "url": url, "inLanguage": "pt-BR", "isPartOf": {"@id": BASE + "#site"},
            "mainEntity": {"@type": "ItemList", "numberOfItems": len(itens), "itemListElement": itens}}),
        ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Início", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": grupo, "item": BASE + "#por-carreira"},
            {"@type": "ListItem", "position": 3, "name": h["nome"], "item": url}]}),
    ]
    trilha = ('<nav class="guia-trilha" aria-label="Você está em"><a href="../">Início</a> <span aria-hidden="true">›</span> '
              '<a href="../#por-carreira">%s</a> <span aria-hidden="true">›</span> %s</nav>' % (grupo, e(h["nome"])))
    trocas = {
        "{{titulo}}": e(h["titulo"]), "{{descricao}}": e(h["descricao"]), "{{slug}}": slug, "{{url}}": url,
        "{{og_tipo}}": "website", "{{css_extra}}": "", "{{ld}}": "\n".join(blocos), "{{tema}}": "pagina-hub",
        "{{topo_link}}": '<a class="topo-link" href="../#cursos">Ver os cursos</a>', "{{trilha}}": trilha,
        "{{h1}}": e(h["h1"]), "{{atualizado}}": "Atualizado em %s" % V["HOJE"].strftime("%d/%m/%Y"),
        "{{artigo}}": artigo, "{{faq}}": "",
        "{{razao_social}}": e(CFG.get("razao_social", "")), "{{cnpj}}": CFG.get("cnpj", ""),
        "{{endereco}}": e(CFG.get("endereco", "")), "{{email}}": CFG.get("email", ""),
    }
    s = modelo
    for k, v in trocas.items():
        s = s.replace(k, v)
    s = s.replace(" · por Mateus Vazzoller, ESCUDO Concursos", "")
    s = s.replace("    </article>\n  </div>\n</main>", "    </article>" + cursos + "  </div>\n</main>", 1)
    s = s.replace("</body>", '<script src="../assets/js/site.js?v=8" defer></script>\n</body>', 1)
    destino = RAIZ / slug / "index.html"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(s, encoding="utf-8")



def main():
    V = _vitrine()
    G = guias()
    modelo = (RAIZ / "_config" / "guia.modelo.html").read_text(encoding="utf-8")
    ativos = [p for p in DADOS["produtos"] if not p.get("prova") or V["d"](p["prova"]) >= V["HOJE"]]
    por_hub = {h["slug"]: [p for p in ativos if entra(h["filtro"], p)] for h in HUBS}
    feitos = []
    for h in HUBS:
        prods = sorted(por_hub[h["slug"]], key=lambda p: p.get("prova") or "2099-12-31")
        if not prods:
            print("pulado (sem curso aberto):", h["slug"])
            continue
        monta(h, prods, por_hub, G, V, modelo)
        feitos.append((h, len(prods)))
        print("ok %s (%d curso%s)" % (h["slug"], len(prods), "s" if len(prods) > 1 else ""))

    # home: atalhos para as páginas, logo depois da vitrine
    chips = lambda tipo: "\n".join('        <a class="chip" href="%s/">%s <span>%d</span></a>' % (h["slug"], e(h["nome"]), n)
                                   for h, n in feitos if h["tipo"] == tipo)
    bloco = ('\n<section class="secao creme hubs" id="por-carreira" aria-labelledby="t-hubs">\n  <div class="wrap">\n'
             '    <p class="kicker">Encontre o seu concurso</p>\n'
             '    <h2 id="t-hubs">Concursos por carreira <em>e por estado</em></h2>\n    <hr class="regua">\n'
             '    <h3>Por carreira</h3>\n    <div class="hubs-lista">\n%s\n    </div>\n'
             '    <h3>Por estado</h3>\n    <div class="hubs-lista">\n%s\n    </div>\n  </div>\n</section>\n'
             % (chips("carreira"), chips("estado")))
    idx = RAIZ / "index.html"
    s = idx.read_text(encoding="utf-8")
    fim_vitrine = s.find("<!-- vitrine:fim -->")
    fecha = s.find("</section>", fim_vitrine) + len("</section>")
    marcado = "<!-- hubs:inicio -->%s<!-- hubs:fim -->" % bloco
    if "<!-- hubs:inicio -->" in s:
        s = re.sub(r"<!-- hubs:inicio -->.*?<!-- hubs:fim -->", lambda _: marcado, s, flags=re.S)
    else:
        s = s[:fecha] + "\n\n" + marcado + s[fecha:]
    idx.write_text(s, encoding="utf-8")
    print("ok index.html (bloco por carreira e estado)")

    llms = RAIZ / "llms.txt"
    if llms.exists():
        t = llms.read_text(encoding="utf-8")
        t = re.sub(r"\n*<!-- hubs:inicio -->.*?<!-- hubs:fim -->\n*", "\n\n", t, flags=re.S)
        linhas = "\n".join("- [%s](%s%s/)" % (h["h1"], BASE, h["slug"]) for h, _ in feitos)
        bloco = "<!-- hubs:inicio -->\n## Concursos por carreira e por estado\n\n%s\n<!-- hubs:fim -->" % linhas
        t = t.replace("<!-- guias:inicio -->", bloco + "\n\n<!-- guias:inicio -->", 1) if "<!-- guias:inicio -->" in t else t.rstrip("\n") + "\n\n" + bloco + "\n"
        llms.write_text(t, encoding="utf-8")
        print("ok llms.txt")


if __name__ == "__main__":
    main()
