# -*- coding: utf-8 -*-
"""Gera o blog /noticias/ a partir de Markdown (pode rodar quantas vezes quiser). Criado em 08/11/2026.

Entrada:  _config/blog/AAAA-MM-DD-<slug>.md  (cabeçalho YAML simples + corpo em Markdown)
Cabeçalho:
    slug: pmesp-soldado-o-que-estudar          (vira /noticias/<slug>/)
    tipo: noticia | o-que-estudar | rotina
    titulo_seo: "..."   (até 60 caracteres)
    descricao: "..."    (até 160 caracteres)
    h1: "..."
    publicado: 2026-11-08
    atualizado_em: 2026-11-08
    curso_id: pmesp-soldado-2026            (opcional: caixa do curso no fim e link no guia)
    guia: concurso-pm-sp                     (opcional)
    fontes: [{"nome": "Edital DP-4/321/26 (DOESP 05/11/2026)", "url": "https://..."}]
    rascunho: sim                            (opcional: não publica)
Saída:
    /noticias/<slug>/index.html   cada post (Article ou NewsArticle + BreadcrumbList)
    /noticias/index.html          lista com filtro
    /noticias/<categoria>/index.html   editais, o-que-estudar, rotina-de-estudos
    /noticias/feed.xml            RSS 2.0
    bloco "Notícias e dicas" no guia do concurso (marcador blog-guia) e seção no llms.txt (marcador blog)

Ordem: ... guias.py, blog.py, aplicar.py, contador.py  (blog.py depois do guias.py, que regrava os guias).
Uso: PYTHONIOENCODING=utf-8 uv run --no-project --with markdown python _config/blog.py
"""
import datetime, html, json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import markdown

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((RAIZ / "_config" / "site.json").read_text(encoding="utf-8"))
PRODUTOS = json.loads((RAIZ / "_config" / "produtos.json").read_text(encoding="utf-8"))
PRODUTOS = PRODUTOS["produtos"] if isinstance(PRODUTOS, dict) else PRODUTOS
POR_ID = {p["id"]: p for p in PRODUTOS}
MODELO = (RAIZ / "_config" / "blog.modelo.html").read_text(encoding="utf-8")
BASE = (CFG.get("url_base") or "https://escudoconcursos.com.br/").rstrip("/") + "/"
INSTA = "https://www.instagram.com/escudoconcursos/"
SAIDA = RAIZ / "noticias"
CATEGORIAS = {  # tipo -> (pasta, nome no plural, selo)
    "noticia": ("editais", "Notícias de editais", "Notícia"),
    "o-que-estudar": ("o-que-estudar", "O que estudar", "O que estudar"),
    "rotina": ("rotina-de-estudos", "Rotina de estudos", "Rotina de estudos"),
}
CSS_CARREIRA = {"policial": "policial", "educacao": "educacao", "tribunais": "tribunais", "bancario": "bancario"}
TODOS = []  # todos os posts publicados, mais novo primeiro (para o "Leia também")
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro",
         "outubro", "novembro", "dezembro"]


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


def data_br(iso):
    try:
        d = datetime.date.fromisoformat(iso)
    except (TypeError, ValueError):
        return ""
    return "%d de %s de %d" % (d.day, MESES[d.month - 1], d.year)


def md(s):
    h = markdown.markdown(s, extensions=["tables", "sane_lists", "toc"], output_format="html")
    h = h.replace("<table>", '<div class="guia-tabela"><table>').replace("</table>", "</table></div>")
    h = h.replace("<blockquote>", '<blockquote class="guia-resposta">')
    return h


def separa_faq(corpo):
    """Tira '## Perguntas frequentes' do corpo e devolve (corpo_sem_faq, [(pergunta, resposta_md)])."""
    m = re.search(r"^## Perguntas frequentes\s*$", corpo, re.M)
    if not m:
        return corpo, []
    faq = []
    for bloco in re.split(r"^### ", corpo[m.end():], flags=re.M)[1:]:
        q, _, a = bloco.partition("\n")
        faq.append((q.strip(), a.strip()))
    return corpo[: m.start()], faq


def texto_puro(s):
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"[*_`>#]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def resumo_html(itens):
    """Tabela 'Resumo' logo depois do primeiro parágrafo. itens = [["Vagas", "2.000"], ...]."""
    if not itens:
        return ""
    linhas = "".join("<tr><th>%s</th><td>%s</td></tr>" % (html.escape(str(a)), md(str(b))[3:-4] if str(b) else "")
                     for a, b in itens)
    return '<div class="guia-tabela blog-resumo"><table><tbody>%s</tbody></table></div>' % linhas


def sumario_html(artigo):
    h2 = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', artigo)
    if len(h2) < 4:
        return ""
    itens = "".join('<li><a href="#%s">%s</a></li>' % (i, t) for i, t in h2)
    return '<nav class="blog-sumario" aria-label="Neste texto"><strong>Neste texto</strong><ol>%s</ol></nav>' % itens


AUTOR_HTML = ('<aside class="blog-autor"><strong>Quem escreve:</strong> Mateus Vazzoller trabalha com concursos públicos desde 2012, '
              'é formado em Direito e foi editor dos livros da AlfaCon. Todo texto aqui sai do edital e dos documentos oficiais, '
              'com o link da fonte no fim. <a href="../../quem-faz/">Conheça a ESCUDO</a></aside>')


def ld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=1) + "\n</script>"


def preenche(trocas):
    s = MODELO
    for k, v in trocas.items():
        s = s.replace(k, v)
    return s


def rodape_trocas():
    return {"{{razao_social}}": html.escape(CFG.get("razao_social", "")), "{{cnpj}}": CFG.get("cnpj", ""),
            "{{endereco}}": html.escape(CFG.get("endereco", "")), "{{email}}": CFG.get("email", "")}


def caixa_curso(p, slug):
    preco = p.get("preco")
    cupom = p.get("cupom") or {}
    hoje = datetime.date.today().isoformat()
    oferta = ""
    if cupom.get("codigo") and cupom.get("preco") and (cupom.get("ate") or "9999") >= hoje:
        oferta = " De R$ %s por R$ %s com o cupom %s até %s." % (
            preco, cupom["preco"], cupom["codigo"], "/".join(reversed(cupom["ate"].split("-"))))
    elif preco:
        oferta = " R$ %s." % preco
    itens = ", ".join(p.get("itens") or [])
    if "edital" not in itens:
        itens += ", de acordo com o edital"
    return ('<p class="guia-curso"><strong>Curso ESCUDO %s em PDF:</strong> %s.%s<br>'
            '<a href="../../%s?src=blog-%s">Ver o curso</a></p>') % (
        html.escape(p.get("titulo", "")), html.escape(itens), html.escape(oferta), p.get("link", p["id"] + "/"), slug)


def credito_html(f, adaptada):
    """Crédito exigido pela licença livre (CC BY): autor, licença, link e aviso de adaptação."""
    txt = "Foto: %s" % html.escape(f.get("credito", ""))
    if f.get("url"):
        txt += ' (<a href="%s" rel="nofollow noopener" target="_blank">%s, via Wikimedia Commons</a>)' % (
            html.escape(f["url"], quote=True), html.escape(f.get("licenca", "licença livre")))
    if f.get("legenda"):
        txt = html.escape(f["legenda"]) + ". " + txt
    if adaptada:
        txt += ". Imagem recortada e com texto sobreposto."
    return "<figcaption>%s</figcaption>" % txt


def fontes_html(fontes):
    if not fontes:
        return ""
    itens = []
    for f in fontes:
        if isinstance(f, dict):
            nome, url = f.get("nome", ""), f.get("url", "")
        else:
            nome, url = str(f), ""
        itens.append('<li><a href="%s" rel="nofollow noopener" target="_blank">%s</a></li>' % (html.escape(url, quote=True), html.escape(nome))
                     if url else "<li>%s</li>" % html.escape(nome))
    return '<aside class="blog-fontes"><h2>Fonte oficial</h2><ul>%s</ul></aside>' % "".join(itens)


def monta_post(meta, corpo):
    slug = meta["slug"]
    tipo = meta.get("tipo", "noticia")
    pasta, _, selo = CATEGORIAS.get(tipo, CATEGORIAS["noticia"])
    url = BASE + "noticias/" + slug + "/"
    p = POR_ID.get(meta.get("curso_id", ""))
    carreira = CSS_CARREIRA.get((p or {}).get("carreira", ""), "")
    tema = (p or {}).get("tema", "")
    titulo = meta.get("titulo_seo") or meta.get("h1")
    h1 = meta.get("h1") or titulo
    desc = meta.get("descricao", "")
    pub = meta.get("publicado", "")
    atu = meta.get("atualizado_em") or pub
    corpo = re.sub(r"<!--.*?-->", "", corpo, flags=re.S).strip()
    corpo, faq = separa_faq(corpo)
    artigo = md(corpo)
    # resumo depois do primeiro parágrafo; sumário depois do resumo
    extra = resumo_html(meta.get("resumo") or [])
    extra += sumario_html(artigo)
    if extra:
        i = artigo.find("</p>")
        artigo = artigo[: i + 4] + "\n" + extra + artigo[i + 4:] if i >= 0 else extra + artigo
    # capa
    from blog_capa import gera
    img_prod = (RAIZ / p["imagem"]) if p and p.get("imagem") else None
    fotos = meta.get("fotos") or []
    foto_capa = (RAIZ / "_config" / "blog" / "fotos" / fotos[0]["arquivo"]) if fotos else None
    gera(SAIDA / slug / "capa.jpg", meta.get("capa_titulo") or h1, selo, img_prod, meta.get("capa_destaque"), foto_capa)
    capa_alt = "%s: %s" % (selo, h1)
    capa = '<figure class="blog-capa"><img src="capa.jpg" alt="%s" width="1200" height="630">%s</figure>' % (
        html.escape(capa_alt, quote=True), credito_html(fotos[0], True) if fotos else "")
    # demais fotos: antes do 2º, 3º... H2
    for n, f in enumerate(fotos[1:], start=2):
        src = RAIZ / "_config" / "blog" / "fotos" / f["arquivo"]
        if not src.exists():
            continue
        from PIL import Image
        im = Image.open(src).convert("RGB")
        im.thumbnail((1200, 1200))
        nome = "foto-%d.jpg" % n
        im.save(SAIDA / slug / nome, "JPEG", quality=82, optimize=True, progressive=True)
        fig = '<figure class="blog-foto"><img src="%s" alt="%s" width="%d" height="%d" loading="lazy">%s</figure>\n' % (
            nome, html.escape(f.get("alt", ""), quote=True), im.width, im.height, credito_html(f, False))
        pos = [m.start() for m in re.finditer(r"<h2", artigo)]
        if len(pos) >= n:
            artigo = artigo[:pos[n - 1]] + fig + artigo[pos[n - 1]:]
    # aviso de prazo vencido
    aviso = ""
    va = str(meta.get("valido_ate", ""))
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", va) and va < datetime.date.today().isoformat():
        aviso = ('<p class="blog-aviso"><strong>Atenção:</strong> este texto é de %s e o prazo de que ele trata terminou em %s. '
                 'Veja a situação atual no guia do concurso.</p>') % (data_br(pub), data_br(va))
    artigo = aviso + capa + artigo
    if p:
        artigo += "\n" + caixa_curso(p, slug)
    faq_html = ""
    if faq:
        faq_html = '<h2 id="perguntas-frequentes">Perguntas frequentes</h2>\n<div class="faq">%s</div>' % "".join(
            "<details><summary>%s</summary>%s</details>" % (html.escape(q), md(a)) for q, a in faq)
    rel = []
    if meta.get("guia") and (RAIZ / meta["guia"] / "index.html").exists():
        rel.append('<a href="../../%s/">Guia completo do concurso: edital, vagas e o que cai</a>' % meta["guia"])
    rel.append('<a href="../">Mais notícias e dicas de concursos</a>')
    leia = ""
    outros = [m for m in TODOS if m["slug"] != slug and (m.get("guia") == meta.get("guia") or m.get("tipo") == tipo)][:3]
    if outros:
        leia = '<h2 id="leia-tambem">Leia também</h2><ul class="blog-lista">%s</ul>' % "".join(item_lista(m, "../") for m in outros)
    relacionados = AUTOR_HTML + leia + '<p class="rodape-links">%s</p>' % " · ".join(rel)

    org = {"@type": "Organization", "name": "ESCUDO Concursos", "url": BASE,
           "legalName": CFG.get("razao_social"), "taxID": CFG.get("cnpj"), "sameAs": [INSTA],
           "logo": {"@type": "ImageObject", "url": BASE + "assets/img/apple-touch-icon.png"}}
    autor = {"@type": "Person", "name": "Mateus Vazzoller", "url": BASE + "quem-faz/", "sameAs": [INSTA]}
    blocos = [
        ld({"@context": "https://schema.org", "@type": "NewsArticle" if tipo == "noticia" else "Article",
            "headline": h1[:110], "description": desc, "url": url, "mainEntityOfPage": url, "inLanguage": "pt-BR",
            "datePublished": pub, "dateModified": atu, "author": autor, "publisher": org,
            "articleSection": CATEGORIAS.get(tipo, CATEGORIAS["noticia"])[1],
            "image": url + "capa.jpg"}),
        ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "ESCUDO Concursos", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": "Notícias e dicas", "item": BASE + "noticias/"},
            {"@type": "ListItem", "position": 3, "name": h1, "item": url}]}),
    ]
    if faq:
        blocos.append(ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": texto_puro(a)}} for q, a in faq]}))
    trilha = ('<nav class="guia-trilha" aria-label="Você está em"><a href="../../">Início</a> <span aria-hidden="true">›</span> '
              '<a href="../">Notícias e dicas</a> <span aria-hidden="true">›</span> <a href="../%s/">%s</a></nav>') % (pasta, html.escape(selo))
    datas = "Publicado em %s" % data_br(pub)
    if atu and atu != pub:
        datas += ", atualizado em %s" % data_br(atu)
    trocas = {
        "{{titulo}}": html.escape(titulo), "{{descricao}}": html.escape(desc, quote=True),
        "{{slug}}": "noticias/" + slug, "{{url}}": url, "{{og_tipo}}": "article",
        "{{css_extra}}": ('<link rel="stylesheet" href="../../assets/css/%s.css?v=8">' % carreira) if carreira else "",
        "{{ld}}": "\n".join(blocos), "{{tema}}": " ".join(c for c in [tema, "tema-" + carreira if carreira else ""] if c),
        "{{topo_link}}": ('<a class="topo-link" href="../../%s?src=blog-%s">Ver o curso</a>' % (p.get("link", p["id"] + "/"), slug)) if p
        else '<a class="topo-link" href="../../">Ver os cursos</a>',
        "{{trilha}}": trilha, "{{h1}}": html.escape(h1), "{{selo}}": '<span class="blog-selo">%s</span>' % html.escape(selo),
        "{{atualizado}}": datas, "{{artigo}}": artigo, "{{faq}}": faq_html,
        "{{tw_card}}": "summary_large_image",
        "{{og_imagem}}": '<meta property="og:image" content="%scapa.jpg">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">' % url, "{{fontes}}": fontes_html(meta.get("fontes")),
        "{{relacionados}}": relacionados, "{{raiz}}": "../../",
    }
    trocas.update(rodape_trocas())
    destino = SAIDA / slug / "index.html"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(preenche(trocas), encoding="utf-8")


def item_lista(meta, pre):
    selo = CATEGORIAS.get(meta.get("tipo", "noticia"), CATEGORIAS["noticia"])[2]
    return '<li><span class="blog-selo">%s</span><a href="%s%s/">%s</a><p>%s · %s</p></li>' % (
        html.escape(selo), pre, meta["slug"], html.escape(meta.get("h1", "")), data_br(meta.get("publicado", "")),
        html.escape(meta.get("descricao", "")))


def monta_lista(posts, pasta=None):
    """Índice geral (pasta=None) ou de uma categoria."""
    if pasta:
        tipo = next(t for t, c in CATEGORIAS.items() if c[0] == pasta)
        nome = CATEGORIAS[tipo][1]
        posts = [m for m in posts if m.get("tipo", "noticia") == tipo]
        h1 = "%s: concursos públicos" % nome
        desc = {"noticia": "Editais publicados, inscrições, retificações, provas e resultados de concursos, sempre com o link do documento oficial.",
                "o-que-estudar": "O que estudar para cada concurso: matérias, número de questões, pesos e por onde começar, a partir do edital.",
                "rotina": "Rotinas e cronogramas de estudo para concursos, contados até a data da prova."}[tipo]
        raiz, pre, url, slug = "../../", "../", BASE + "noticias/%s/" % pasta, "noticias/%s" % pasta
    else:
        h1 = "Notícias e dicas de concursos públicos"
        desc = "Notícias de editais com link oficial, o que estudar para cada concurso e rotinas de estudo, por Mateus Vazzoller, da ESCUDO Concursos."
        raiz, pre, url, slug = "../", "", BASE + "noticias/", "noticias"
    filtros = ['<a href="%s"%s>Tudo</a>' % (pre or "./", "" if pasta else ' aria-current="page"')]
    for t, (pa, nome, _) in CATEGORIAS.items():
        filtros.append('<a href="%s%s/"%s>%s</a>' % (pre, pa, ' aria-current="page"' if pa == pasta else "", nome))
    corpo = '<p>%s</p><nav class="blog-filtros" aria-label="Filtrar">%s</nav>' % (html.escape(desc), "".join(filtros))
    corpo += ('<ul class="blog-lista">%s</ul>' % "".join(item_lista(m, ("../" if pasta else "")) for m in posts)) if posts \
        else "<p>Os primeiros textos desta seção saem em breve.</p>"
    trilha = '<nav class="guia-trilha" aria-label="Você está em"><a href="%s">Início</a>%s</nav>' % (
        raiz, (' <span aria-hidden="true">›</span> <a href="../">Notícias e dicas</a>' if pasta else ""))
    lista_ld = ld({"@context": "https://schema.org", "@type": "CollectionPage", "name": h1, "url": url, "description": desc,
                   "inLanguage": "pt-BR", "hasPart": [{"@type": "Article", "headline": m.get("h1", ""),
                                                       "url": BASE + "noticias/" + m["slug"] + "/"} for m in posts[:30]]})
    trocas = {"{{titulo}}": html.escape(h1), "{{descricao}}": html.escape(desc, quote=True), "{{slug}}": slug,
              "{{url}}": url, "{{og_tipo}}": "website", "{{css_extra}}": "", "{{ld}}": lista_ld, "{{tema}}": "",
              "{{topo_link}}": '<a class="topo-link" href="%s">Ver os cursos</a>' % raiz, "{{trilha}}": trilha,
              "{{h1}}": html.escape(h1), "{{selo}}": "", "{{atualizado}}": "Atualizado em %s" % data_br(datetime.date.today().isoformat()),
              "{{artigo}}": corpo, "{{faq}}": "", "{{fontes}}": "", "{{relacionados}}": "", "{{raiz}}": raiz,
              "{{tw_card}}": "summary", "{{og_imagem}}": '<meta property="og:image" content="%sassets/img/og-escudo.jpg">' % BASE}
    trocas.update(rodape_trocas())
    s = preenche(trocas).replace(" · por <a href=\"%squem-faz/\">Mateus Vazzoller</a>, ESCUDO Concursos" % raiz, "")
    destino = (SAIDA / pasta / "index.html") if pasta else (SAIDA / "index.html")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(s, encoding="utf-8")


def monta_feed(posts):
    def rfc(iso):
        d = datetime.datetime.fromisoformat(iso).replace(hour=7, tzinfo=datetime.timezone(datetime.timedelta(hours=-3)))
        return d.strftime("%a, %d %b %Y %H:%M:%S -0300")
    itens = "".join(
        "<item><title>%s</title><link>%snoticias/%s/</link><guid>%snoticias/%s/</guid><pubDate>%s</pubDate>"
        "<description>%s</description></item>\n" % (html.escape(m.get("h1", "")), BASE, m["slug"], BASE, m["slug"],
                                                    rfc(m["publicado"]), html.escape(m.get("descricao", "")))
        for m in posts[:30])
    (SAIDA / "feed.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>\n'
        "<title>ESCUDO Concursos: notícias e dicas</title><link>%snoticias/</link>"
        "<description>Notícias de editais, o que estudar e rotinas de estudo para concursos públicos.</description>"
        "<language>pt-BR</language>\n%s</channel></rss>\n" % (BASE, itens), encoding="utf-8")


def troca_marcador(s, nome, novo, onde):
    bloco = "<!-- %s:inicio -->%s<!-- %s:fim -->" % (nome, novo, nome)
    if "<!-- %s:inicio -->" % nome in s:
        return re.sub(r"<!-- %s:inicio -->.*?<!-- %s:fim -->" % (nome, nome), lambda _: bloco, s, flags=re.S)
    i = s.find(onde)
    return s if i < 0 else s[:i] + bloco + "\n" + s[i:]


def liga_guias(posts):
    """Bloco 'Notícias e dicas deste concurso' no fim do guia, com até 5 posts."""
    por_guia = {}
    for m in posts:
        if m.get("guia"):
            por_guia.setdefault(m["guia"], []).append(m)
    for pag in sorted(RAIZ.glob("concurso-*/index.html")):
        s = pag.read_text(encoding="utf-8")
        lista = por_guia.get(pag.parent.name, [])[:5]
        novo = ""
        if lista:
            novo = '<h2>Notícias e dicas deste concurso</h2><ul class="blog-lista">%s</ul>' % "".join(
                item_lista(m, "../noticias/") for m in lista)
        s2 = troca_marcador(s, "blog-guia", novo, "    </article>")
        if s2 != s:
            pag.write_text(s2, encoding="utf-8")
            print("ok guia", pag.parent.name)


def liga_llms(posts):
    llms = RAIZ / "llms.txt"
    if not llms.exists():
        return
    s = llms.read_text(encoding="utf-8")
    linhas = "\n".join("- [%s](%snoticias/%s/)" % (m.get("h1", ""), BASE, m["slug"]) for m in posts[:40])
    sec = "\n## Notícias e dicas\n\n- [Todas as notícias e dicas](%snoticias/)\n%s\n" % (BASE, linhas)
    s = re.sub(r"\n*<!-- blog:inicio -->.*?<!-- blog:fim -->\n*", "\n\n", s, flags=re.S)
    bloco = "<!-- blog:inicio -->%s<!-- blog:fim -->" % sec
    if "\n## Mais" in s:
        s = s.replace("\n## Mais", "\n" + bloco + "\n\n## Mais", 1)
    else:
        s = s.rstrip("\n") + "\n\n" + bloco + "\n"
    llms.write_text(s, encoding="utf-8")


def menu_noticias():
    """Link "Notícias" no topo de todas as páginas do site (marcador menu-noticias), antes do botão do topo. 08/11/2026."""
    n = 0
    for pag in [RAIZ / "index.html", RAIZ / "404.html"] + sorted(RAIZ.glob("*/index.html")) + sorted(RAIZ.glob("*/*/index.html")):
        rel = pag.relative_to(RAIZ).as_posix()
        if rel.startswith(("noticias/", "_config/", "assets/")) or not pag.exists():
            continue
        s = pag.read_text(encoding="utf-8")
        i = s.find('<header class="topo">')
        if i < 0:
            continue
        fim = s.find("</header>", i)
        pre = "/" if rel == "404.html" else "../" * rel.count("/")
        link = '<a class="topo-link topo-noticias" href="%snoticias/" style="margin-left:auto">Notícias</a>' % pre
        cab = s[i:fim]
        if "<!-- menu-noticias:inicio -->" in cab:
            novo = re.sub(r"<!-- menu-noticias:inicio -->.*?<!-- menu-noticias:fim -->",
                          lambda _: "<!-- menu-noticias:inicio -->%s<!-- menu-noticias:fim -->" % link, cab, flags=re.S)
        else:
            j = cab.find('<a class="topo-link"')
            bloco = "<!-- menu-noticias:inicio -->%s<!-- menu-noticias:fim -->\n    " % link
            novo = cab[:j] + bloco + cab[j:] if j >= 0 else cab.replace("  </div>", "    " + bloco.strip() + "\n  </div>", 1)
        if novo != cab:
            pag.write_text(s[:i] + novo + s[fim:], encoding="utf-8")
            n += 1
    print("ok menu Notícias em %d páginas" % n)


def main():
    posts, slugs, corpos = [], set(), {}
    reservadas = {c[0] for c in CATEGORIAS.values()}
    for arq in sorted((RAIZ / "_config" / "blog").glob("*.md")):
        meta, corpo = le(arq)
        if str(meta.get("rascunho", "")).lower() in ("sim", "true", "1"):
            print("rascunho, fica de fora:", arq.name)
            continue
        slug = meta.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", arq.stem)
        meta["slug"] = slug
        if slug in reservadas or slug in slugs:
            sys.exit("ERRO: slug repetido ou reservado: %s (%s)" % (slug, arq.name))
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(meta.get("publicado", ""))):
            sys.exit("ERRO: 'publicado' faltando ou fora do formato AAAA-MM-DD em %s" % arq.name)
        tit = meta.get("titulo_seo") or ""
        if len(tit) > 60:
            print("aviso: titulo_seo com %d caracteres (máx. 60) em %s" % (len(tit), arq.name))
        slugs.add(slug)
        posts.append(meta)
        corpos[slug] = corpo
    posts.sort(key=lambda m: (m.get("publicado", ""), m["slug"]), reverse=True)
    TODOS[:] = posts
    for meta in posts:
        monta_post(meta, corpos[meta["slug"]])
        print("ok noticias/%s/" % meta["slug"])
    # apaga páginas de posts que saíram (rascunho ou arquivo removido)
    for d in SAIDA.glob("*/index.html") if SAIDA.exists() else []:
        nome = d.parent.name
        if nome not in slugs and nome not in reservadas:
            d.unlink()
            try:
                d.parent.rmdir()
            except OSError:
                pass
            print("removido noticias/%s/" % nome)
    monta_lista(posts)
    for pasta, _, _ in CATEGORIAS.values():
        monta_lista(posts, pasta)
    monta_feed(posts)
    liga_guias(posts)
    liga_llms(posts)
    print("ok índice, categorias, feed.xml e llms.txt (%d posts)" % len(posts))


if __name__ == "__main__":
    main()
    menu_noticias()
