# -*- coding: utf-8 -*-
"""Amostra grátis de cada curso em /<curso>/amostra/ (onda 2 do plano de SEO, 07/11/2026). Idempotente.

Entrada: _config/amostras/<curso>.md, com cabeçalho e corpo em Markdown:
    ---
    curso_id: gm-recife-2026
    pdf: assets/amostras/gm-recife-2026.pdf        (opcional: o mesmo conteúdo em PDF, tirado da apostila)
    atualizado_em: 2026-11-07
    ---
    ## Como é a prova e como usar esta apostila
    (texto da apostila)
    ## 10 questões comentadas
    ### Questão 1
    Enunciado...
    - (A) ...
    - (B) ...
    **Gabarito: B.** Comentário... (tudo do "**Gabarito" até a próxima "### " fica escondido atrás de "Ver gabarito comentado")

Saída: /<curso>/amostra/index.html (modelo dos guias + bloco de preço copiado da página do curso, com sck=site-amostra-<curso>
no checkout), link "Leia uma amostra grátis" na página do curso (<!-- amostra-link -->) e seção no llms.txt.
O sitemap é feito pelo aplicar.py (inclui */amostra/).

Uso: PYTHONIOENCODING=utf-8 python _config/amostra.py   (depois de onda1.py; antes de aplicar.py e contador.py)
"""
import html, json, pathlib, re

import markdown

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((RAIZ / "_config" / "site.json").read_text(encoding="utf-8"))
BASE = (CFG.get("url_base") or "https://escudoconcursos.com.br/").rstrip("/") + "/"
NOMES = json.loads((RAIZ / "_config" / "nomes.json").read_text(encoding="utf-8"))["cursos"]
MODELO = (RAIZ / "_config" / "guia.modelo.html").read_text(encoding="utf-8")
ANO = "2026"
e = lambda s: html.escape(str(s), quote=True)


def le(arq):
    txt = arq.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", txt, re.S)
    meta = {}
    for linha in (m.group(1) if m else "").splitlines():
        if ":" in linha:
            k, v = linha.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta, (m.group(2) if m else txt)


def md(s):
    h = markdown.markdown(s, extensions=["tables", "sane_lists"], output_format="html")
    return h.replace("<table>", '<div class="guia-tabela"><table>').replace("</table>", "</table></div>")  # rola no celular


def questoes(corpo):
    """Esconde o gabarito comentado de cada questão atrás de um <details>."""
    def uma(m):
        cab, texto = m.group(1), m.group(2)
        g = re.search(r"^\*\*Gabarito", texto, re.M)
        if not g:
            return '<div class="am-questao">' + md(cab + texto) + "</div>"
        return ('<div class="am-questao">' + md(cab + texto[: g.start()]) +
                '<details class="am-gabarito"><summary>Ver gabarito comentado</summary>' + md(texto[g.start():]) + "</details></div>")
    return re.sub(r"(^### [^\n]*\n)(.*?)(?=^### |^## |\Z)", lambda m: "\n\n" + uma(m) + "\n\n", corpo, flags=re.S | re.M)


def bloco_preco(curso_html, curso):
    """Copia o bloco de preço do fim da página do curso (cupom, preço e botão) e marca a origem da venda."""
    m = re.search(r'<section class="escuro secao cta-final".*?(<div class="preco" data-oferta>.*?)\s*<ul class="selos">', curso_html, re.S)
    if not m:
        return ""
    p = m.group(1)
    p = re.sub(r"<svg[^>]*>.*?</svg>", "", p, flags=re.S)
    p = p.replace('data-goatcounter-click="compra-fim" data-goatcounter-title="compra-fim"',
                  'data-goatcounter-click="compra-amostra" data-goatcounter-title="compra-amostra"')
    p = re.sub(r'(https://pay\.hotmart\.com/[^"]+)', lambda u: u.group(1) + "&amp;sck=site-amostra-" + curso, p)
    return p + "\n    </div>"


def monta(arq):
    meta, corpo = le(arq)
    curso = meta["curso_id"]
    n = NOMES[curso]
    curso_html = (RAIZ / curso / "index.html").read_text(encoding="utf-8")
    slug = curso + "/amostra"
    url = BASE + slug + "/"
    nome = "%s %s: %s" % (n["sigla"], ANO, n["cargo"])
    titulo = "Amostra grátis da apostila %s %s em PDF" % (n["sigla"], ANO)
    h1 = "Amostra grátis da apostila %s %s: %s" % (n["sigla"], ANO, n["cargo"])
    desc = ("Leia grátis a apresentação da apostila %s %s para %s e 10 questões comentadas no formato da banca. "
            "Baixe também em PDF." % (n["sigla"], ANO, n["cargo"]))[:155]
    pdf = meta.get("pdf", "")
    tem_pdf = pdf and (RAIZ / pdf).exists()
    topo = ('<div class="am-topo"><p>Esta é uma amostra do curso em PDF <a href="../">%s</a>: a apresentação da apostila, '
            'como a prova funciona e 10 questões com gabarito comentado, do jeito que estão no material.</p>%s</div>'
            % (e(nome), ('<a class="am-pdf" data-goatcounter-click="amostra-pdf-%s" data-goatcounter-title="amostra-pdf-%s" '
                         'href="../../%s" download>Baixar a amostra em PDF</a>' % (curso, curso, e(pdf))) if tem_pdf else ""))
    corpo = re.sub(r"<!--.*?-->", "", corpo, flags=re.S)
    artigo = topo + "\n" + md(questoes(corpo)).replace("<p><div", "<div").replace("</div></p>", "</div>")
    preco = bloco_preco(curso_html, curso)
    fim = ('\n<section class="escuro secao cta-final am-fim" aria-labelledby="t-am-fim">\n  <div class="wrap">\n'
           '    <p class="kicker">%s</p>\n    <h2 id="t-am-fim">Gostou? O curso tem <em>o programa inteiro</em></h2>\n'
           '    %s\n    <p class="am-voltar"><a href="../">Ver tudo o que vem no curso</a></p>\n  </div>\n</section>\n'
           % (e(nome), preco))
    blocos = [
        {"@context": "https://schema.org", "@type": "LearningResource", "name": h1, "description": desc, "url": url,
         "inLanguage": "pt-BR", "isAccessibleForFree": True, "learningResourceType": "Amostra de apostila",
         "educationalLevel": "Concurso público", "datePublished": meta.get("atualizado_em", ""),
         "author": {"@type": "Person", "name": "Mateus Vazzoller", "url": BASE + "quem-faz/"},
         "publisher": {"@id": BASE + "#organizacao"}, "isPartOf": {"@type": "Product", "name": nome, "url": BASE + curso + "/"}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Início", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": nome, "item": BASE + curso + "/"},
            {"@type": "ListItem", "position": 3, "name": "Amostra grátis", "item": url}]},
    ]
    ld = "\n".join('<script type="application/ld+json">\n%s\n</script>' % json.dumps(b, ensure_ascii=False, indent=1) for b in blocos)
    trilha = ('<nav class="guia-trilha" aria-label="Você está em"><a href="../../">Início</a> <span aria-hidden="true">›</span> '
              '<a href="../">%s</a> <span aria-hidden="true">›</span> Amostra grátis</nav>' % e(nome))
    data = meta.get("atualizado_em", "")
    trocas = {
        "{{titulo}}": e(titulo), "{{descricao}}": e(desc), "{{slug}}": slug, "{{url}}": url, "{{og_tipo}}": "article",
        "{{css_extra}}": "", "{{ld}}": ld, "{{tema}}": "pagina-amostra",
        "{{topo_link}}": '<a class="topo-link" href="../#oferta">Ver o curso</a>', "{{trilha}}": trilha, "{{h1}}": e(h1),
        "{{atualizado}}": ("Atualizado em %s" % "/".join(reversed(data.split("-")))) if data else "",
        "{{artigo}}": artigo, "{{faq}}": "",
        "{{razao_social}}": e(CFG.get("razao_social", "")), "{{cnpj}}": CFG.get("cnpj", ""),
        "{{endereco}}": e(CFG.get("endereco", "")), "{{email}}": CFG.get("email", ""),
    }
    s = MODELO
    for k, v in trocas.items():
        s = s.replace(k, v)
    # a página fica duas pastas abaixo da raiz
    s = re.sub(r'(href|src)="\.\./(?!\.\./)', r'\1="../../', s)
    s = s.replace('href="../../#oferta"', 'href="../#oferta"').replace('<a href="../../">%s</a>' % e(nome), '<a href="../">%s</a>' % e(nome))
    s = s.replace("</main>", "</main>" + fim, 1)
    s = s.replace("</body>", '<script src="../../assets/js/site.js?v=6" defer></script>\n</body>', 1)
    destino = RAIZ / curso / "amostra" / "index.html"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(s, encoding="utf-8")

    # link na página do curso, logo depois do botão do meio ("Veja por dentro")
    link = ('\n    <p class="amostra-link"><a href="amostra/" data-goatcounter-click="amostra-abrir-%s" data-goatcounter-title="amostra-abrir-%s">'
            'Leia uma amostra grátis: a apresentação e 10 questões comentadas</a></p>\n    ' % (curso, curso))
    marcado = "<!-- amostra-link:inicio -->%s<!-- amostra-link:fim -->" % link
    if "<!-- amostra-link:inicio -->" in curso_html:
        curso_html = re.sub(r"<!-- amostra-link:inicio -->.*?<!-- amostra-link:fim -->", lambda _: marcado, curso_html, flags=re.S)
    elif "<!-- compra-meio:fim -->" in curso_html:
        curso_html = curso_html.replace("<!-- compra-meio:fim -->", "<!-- compra-meio:fim -->\n    " + marcado, 1)
    (RAIZ / curso / "index.html").write_text(curso_html, encoding="utf-8")
    print("ok", slug, "(PDF)" if tem_pdf else "(sem PDF)")
    return h1, url


def main():
    feitos = [monta(a) for a in sorted((RAIZ / "_config" / "amostras").glob("*.md"))]
    llms = RAIZ / "llms.txt"
    if llms.exists() and feitos:
        t = llms.read_text(encoding="utf-8")
        t = re.sub(r"\n*<!-- amostras:inicio -->.*?<!-- amostras:fim -->\n*", "\n\n", t, flags=re.S)
        bloco = ("<!-- amostras:inicio -->\n## Amostras grátis\n\n%s\n<!-- amostras:fim -->"
                 % "\n".join("- [%s](%s)" % (h, u) for h, u in feitos))
        t = t.replace("<!-- guias:inicio -->", bloco + "\n\n<!-- guias:inicio -->", 1) if "<!-- guias:inicio -->" in t else t.rstrip("\n") + "\n\n" + bloco + "\n"
        llms.write_text(t, encoding="utf-8")
        print("ok llms.txt")


if __name__ == "__main__":
    main()
