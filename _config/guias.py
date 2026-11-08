# -*- coding: utf-8 -*-
"""Gera os guias de concurso e a página "Quem faz" a partir de Markdown (pode rodar quantas vezes quiser).

Entrada:  _config/guias/concurso-*.md  e  _config/guias/quem-faz.md  (cabeçalho YAML simples + corpo em Markdown)
Saída:    /<slug>/index.html  para cada arquivo, com Article + BreadcrumbList + FAQPage (guias)
          ou Person + Organization (quem-faz).
Também (idempotente, entre marcadores):
  - link "Quem faz" no rodapé de todas as páginas com <footer class="rodape">;
  - link "Guia do concurso" no rodapé da página de cada curso que tem guia;
  - seção "Guias de concurso" no llms.txt.
O sitemap.xml é feito pelo aplicar.py, que já inclui as pastas concurso-*/ e quem-faz/.

Uso: PYTHONIOENCODING=utf-8 python 07-site/_config/guias.py   (depois rodar aplicar.py)
"""
import html, json, pathlib, re

import markdown

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((RAIZ / "_config" / "site.json").read_text(encoding="utf-8"))
PRODUTOS = json.loads((RAIZ / "_config" / "produtos.json").read_text(encoding="utf-8"))
PRODUTOS = PRODUTOS["produtos"] if isinstance(PRODUTOS, dict) else PRODUTOS
POR_ID = {p["id"]: p for p in PRODUTOS}
MODELO = (RAIZ / "_config" / "guia.modelo.html").read_text(encoding="utf-8")
BASE = (CFG.get("url_base") or "https://escudoconcursos.com.br/").rstrip("/") + "/"
CSS_CARREIRA = {"policial": "policial", "educacao": "educacao", "tribunais": "tribunais", "bancario": "bancario"}
INSTA = "https://www.instagram.com/escudoconcursos/"


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


def texto_puro(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"[*_`>#]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def separa_faq(corpo):
    """Tira a seção '## Perguntas frequentes' do corpo e devolve (corpo_sem_faq, [(pergunta, resposta_md)], rodape_md)."""
    m = re.search(r"^## Perguntas frequentes\s*$", corpo, re.M)
    if not m:
        return corpo, [], ""
    antes, resto = corpo[: m.start()], corpo[m.end():]
    rodape = ""
    r = re.search(r"^\*[^*\n].*\*\s*$", resto, re.M)  # linha final em itálico (aviso de independência)
    if r:
        rodape, resto = resto[r.start():].strip(), resto[: r.start()]
    faq = []
    for bloco in re.split(r"^### ", resto, flags=re.M)[1:]:
        p, _, a = bloco.partition("\n")
        faq.append((p.strip(), a.strip()))
    return antes, faq, rodape


def md(s):
    h = markdown.markdown(s, extensions=["tables", "sane_lists"], output_format="html")
    # blocos do curso ganham destaque
    h = re.sub(r"<p><strong>(Cursos? ESCUDO)", r'<p class="guia-curso"><strong>\1', h)
    # tabelas roláveis no celular
    h = h.replace("<table>", '<div class="guia-tabela"><table>').replace("</table>", "</table></div>")
    # resposta rápida
    h = h.replace("<blockquote>", '<blockquote class="guia-resposta">')
    return h


def ld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=1) + "\n</script>"


def produtos_do_guia(meta):
    ids = meta.get("curso_id") or []
    if isinstance(ids, str):
        ids = [i.strip() for i in re.split(r"[,+]", ids) if i.strip()]
    return [POR_ID[i] for i in ids if i in POR_ID]


def monta(meta, corpo, slug):
    url = BASE + slug + "/"
    quem = slug == "quem-faz"
    prods = [] if quem else produtos_do_guia(meta)
    p0 = prods[0] if prods else {}
    tema = p0.get("tema", "")
    carreira = CSS_CARREIRA.get(p0.get("carreira", ""), "")
    corpo_sem_faq, faq, rodape = separa_faq(corpo)
    corpo_sem_faq = re.sub(r"^## Notas para a montagem.*", "", corpo_sem_faq, flags=re.S | re.M)
    corpo_sem_faq = re.sub(r"<!--.*?-->", "", corpo_sem_faq, flags=re.S).rstrip().rstrip("-").rstrip()
    artigo = md(corpo_sem_faq)
    faq_html = ""
    if faq:
        itens = "\n".join(
            "<details><summary>%s</summary>%s</details>" % (html.escape(q), md(a)) for q, a in faq)
        faq_html = '<h2>Perguntas frequentes</h2>\n<div class="faq">\n%s\n</div>' % itens
    if rodape:
        faq_html += "\n" + md(rodape).replace("<p>", '<p class="guia-rodape">', 1)

    titulo = meta.get("titulo_seo") or meta.get("h1")
    desc = meta.get("descricao", "")
    h1 = meta.get("h1") or titulo
    data = meta.get("atualizado_em", "")
    org = {"@type": "Organization", "name": "ESCUDO Concursos", "url": BASE,
           "legalName": CFG.get("razao_social"), "taxID": CFG.get("cnpj"), "sameAs": [INSTA]}
    autor = {"@type": "Person", "name": "Mateus Vazzoller", "url": BASE + "quem-faz/", "sameAs": [INSTA]}
    trilha = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ESCUDO Concursos", "item": BASE},
        {"@type": "ListItem", "position": 2, "name": h1, "item": url}]}
    blocos = []
    if quem:
        blocos.append(ld({"@context": "https://schema.org", "@type": "AboutPage", "name": h1, "url": url,
                          "description": desc,
                          "mainEntity": dict(autor, **{"worksFor": org, "jobTitle": "Editor de materiais para concursos públicos", "description": "Trabalha com concursos públicos desde 2012, formado em Direito (2018), foi editor dos livros da AlfaCon.", "knowsAbout": ["Concursos públicos", "Direito"]})}))
        blocos.append(ld(dict(org, **{"@context": "https://schema.org", "founder": autor,
                                      "address": {"@type": "PostalAddress", "streetAddress": CFG.get("endereco"),
                                                  "addressCountry": "BR"}})))
    else:
        blocos.append(ld({"@context": "https://schema.org", "@type": "Article", "headline": h1[:110],
                          "description": desc, "url": url, "mainEntityOfPage": url, "inLanguage": "pt-BR",
                          "datePublished": data, "dateModified": data, "author": autor, "publisher": org}))
        if faq:
            blocos.append(ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": texto_puro(a)}}
                for q, a in faq]}))
    blocos.append(ld(trilha))

    trilha_html = '<nav class="guia-trilha" aria-label="Você está em"><a href="../">Início</a> <span aria-hidden="true">›</span> %s</nav>' % html.escape(
        "Quem faz" if quem else (meta.get("orgao") and h1.split(":")[0] or h1))
    css_extra = '<link rel="stylesheet" href="../assets/css/%s.css?v=8">' % carreira if carreira else ""
    topo_link = ('<a class="topo-link" href="/%s/">Ver o curso</a>' % p0["id"]) if p0 else '<a class="topo-link" href="../">Ver os cursos</a>'
    trocas = {
        "{{titulo}}": html.escape(titulo), "{{descricao}}": html.escape(desc, quote=True), "{{slug}}": slug,
        "{{url}}": url, "{{og_tipo}}": "profile" if quem else "article", "{{css_extra}}": css_extra,
        "{{ld}}": "\n".join(blocos), "{{tema}}": " ".join(c for c in [tema, "tema-" + carreira if carreira else ""] if c),
        "{{topo_link}}": topo_link, "{{trilha}}": trilha_html, "{{h1}}": html.escape(h1),
        "{{atualizado}}": ("Atualizado em %s" % "/".join(reversed(data.split("-")))) if data else "",
        "{{artigo}}": artigo, "{{faq}}": faq_html,
        "{{razao_social}}": html.escape(CFG.get("razao_social", "")), "{{cnpj}}": CFG.get("cnpj", ""),
        "{{endereco}}": html.escape(CFG.get("endereco", "")), "{{email}}": CFG.get("email", ""),
    }
    s = MODELO
    for k, v in trocas.items():
        s = s.replace(k, v)
    destino = RAIZ / slug / "index.html"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(s, encoding="utf-8")
    return h1, prods


def troca_marcador(s, nome, novo, onde):
    """Substitui o bloco entre <!-- nome:inicio --> e <!-- nome:fim -->, ou insere antes de `onde`."""
    bloco = "<!-- %s:inicio -->%s<!-- %s:fim -->" % (nome, novo, nome)
    if "<!-- %s:inicio -->" % nome in s:
        return re.sub(r"<!-- %s:inicio -->.*?<!-- %s:fim -->" % (nome, nome), lambda _: bloco, s, flags=re.S)
    i = s.find(onde)
    return s if i < 0 else s[:i] + bloco + "\n    " + s[i:]


guias = []
for arq in sorted((RAIZ / "_config" / "guias").glob("*.md")):
    meta, corpo = le(arq)
    slug = meta.get("slug") or arq.stem
    h1, prods = monta(meta, corpo, slug)
    if slug != "quem-faz":
        guias.append((slug, h1, prods, meta))
    print("ok", slug)

# rodapé: link "Quem faz" em todas as páginas; link do guia nas páginas de curso
guia_do_curso = {p["id"]: slug for slug, _, prods, _ in guias for p in prods}
for pag in [RAIZ / "index.html"] + sorted(RAIZ.glob("*/index.html")):
    s = pag.read_text(encoding="utf-8")
    if 'class="rodape"' not in s or "<small>©" not in s:
        continue
    pre = "" if pag.parent == RAIZ else "../"
    links = '<a class="rodape-link" href="%squem-faz/">Quem faz a ESCUDO</a>' % pre
    curso = pag.parent.name
    if curso in guia_do_curso:
        links = '<a class="rodape-link" href="../%s/">Guia do concurso: edital, vagas e o que cai</a> · ' % guia_do_curso[curso] + links
    novo = '<p class="rodape-links">%s</p>' % links
    s2 = troca_marcador(s, "links-rodape", novo, "<small>©")
    if s2 != s:
        pag.write_text(s2, encoding="utf-8")
        print("ok rodapé", pag.relative_to(RAIZ))

# llms.txt
llms = RAIZ / "llms.txt"
if llms.exists():
    s = llms.read_text(encoding="utf-8")
    linhas = "\n".join("- [%s](%s%s/)" % (h1, BASE, slug) for slug, h1, _, _ in guias)
    sec = "\n## Guias de concurso\n\n%s\n\n- [Quem faz a ESCUDO Concursos](%squem-faz/)\n" % (linhas, BASE)
    s = re.sub(r"\n*<!-- guias:inicio -->.*?<!-- guias:fim -->\n*", "\n\n", s, flags=re.S)
    bloco = "<!-- guias:inicio -->%s<!-- guias:fim -->" % sec
    if "\n## Mais" in s:
        s = s.replace("\n## Mais", "\n" + bloco + "\n\n## Mais", 1)
    else:
        s = s.rstrip("\n") + "\n\n" + bloco + "\n"
    llms.write_text(s, encoding="utf-8")
    print("ok llms.txt")
