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


def titulo_curto(meta, prods, limite=60):
    """<title> do guia em até 60 caracteres (21/11/2026: os títulos tinham 67 a 89 e o Google cortava; CTR 1,6%).
    Com inscrições abertas, o prazo entra logo depois dos dois-pontos ("inscrições até 23/11"), que é o que a
    busca "inscrição concurso X" quer ver. Itens do fim da lista caem até caber; " | ESCUDO" só se sobrar espaço."""
    import datetime
    base = (meta.get("titulo_seo") or meta.get("h1") or "").strip()
    cab, _, resto = base.partition(":")
    itens = [i.strip() for i in re.split(r",\s+|\s+e\s+", resto) if i.strip()]
    hoje = datetime.date.today().isoformat()
    fins = sorted(p.get("inscricoes_ate", "") for p in prods if p.get("inscricoes_ate", "") >= hoje)
    if fins:
        prazo = "inscrições até " + data_br(fins[0])[:5]
        itens = [prazo] + [i for i in itens if "edital" not in i.lower() and "inscri" not in i.lower()]
    else:
        # 23/11/2026 (CTR 1,8%): com a inscrição encerrada, quem busca o concurso quer a data da prova
        # ("prova em 13/12"), que entra no lugar do prazo. Guia sem data de prova fica como está.
        provas = sorted(p.get("prova", "") for p in prods if hoje <= p.get("prova", "") < "2099")
        dp = str(meta.get("data_prova") or "").strip('"')
        if not provas and re.fullmatch(r"\d{4}-\d{2}-\d{2}", dp) and dp >= hoje:
            provas = [dp]
        if provas:
            itens = ["prova em " + data_br(provas[0])[:5]] + [i for i in itens if "prova" not in i.lower() and "inscri" not in i.lower()]

    def junta(lst):
        return cab + (": " + (", ".join(lst[:-1]) + " e " + lst[-1] if len(lst) > 1 else lst[0]) if lst else "")

    while len(itens) > 1 and len(junta(itens)) > limite:
        itens = itens[:-1]
    t = junta(itens)
    return t + " | ESCUDO" if len(t) + 9 <= limite else t


ATUALIZACOES = RAIZ / "_config" / "guias" / "atualizacoes.json"


def data_br(iso):
    return "/".join(reversed(str(iso).split("-")))


def atualizacoes_do_guia(slug):
    """Linha do tempo do concurso (08/11/2026): notícias pequenas de atualizacoes.json + posts de notícia do blog
    com guia: <slug>. Mais nova primeiro. Cada item: (data ISO, texto, link do post ou None, link da fonte oficial ou None)."""
    itens = []
    if ATUALIZACOES.exists():
        for a in json.loads(ATUALIZACOES.read_text(encoding="utf-8")).get(slug, []):
            itens.append((a["data"], a["texto"], a.get("link"), a.get("fonte")))
    for arq in sorted((RAIZ / "_config" / "blog").glob("*.md")):
        m, _ = le(arq)
        if m.get("guia") == slug and m.get("tipo") == "noticia" and str(m.get("rascunho", "")).lower() != "true":
            itens.append((str(m.get("publicado", ""))[:10], m.get("h1") or m.get("titulo_seo", ""),
                          "/noticias/%s/" % m.get("slug", arq.stem[11:]), None))
    return sorted(itens, key=lambda x: x[0], reverse=True)


def atualizacoes_html(itens):
    if not itens:
        return ""
    def li(a):
        d, txt, link, fonte = a
        t = html.escape(txt)
        if link:
            t += ' <a href="%s">Leia a notícia</a>' % html.escape(link, quote=True)
        elif fonte:
            t += ' <a href="%s" rel="nofollow noopener" target="_blank">Fonte oficial</a>' % html.escape(fonte, quote=True)
        return '<li><time datetime="%s">%s</time> %s</li>' % (d, data_br(d), t)
    vis, resto = itens[:6], itens[6:]
    s = '<section class="guia-atualizacoes" aria-labelledby="ult-atual">\n<h2 id="ult-atual">Últimas atualizações</h2>\n<ul>%s</ul>' % "".join(li(a) for a in vis)
    if resto:
        s += '<details><summary>Atualizações anteriores</summary><ul>%s</ul></details>' % "".join(li(a) for a in resto)
    return s + "\n</section>\n"


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
    atual = [] if slug == "quem-faz" else atualizacoes_do_guia(slug)
    artigo = atualizacoes_html(atual) + artigo
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
    data = max([str(meta.get("atualizado_em", ""))] + [a[0] for a in atual])
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
        "{{atualizado}}": ("Atualizado em %s" % data_br(data)) if data else "",
        "{{artigo}}": artigo, "{{faq}}": faq_html,
        "{{razao_social}}": html.escape(CFG.get("razao_social", "")), "{{cnpj}}": CFG.get("cnpj", ""),
        "{{endereco}}": html.escape(CFG.get("endereco", "")), "{{email}}": CFG.get("email", ""),
    }
    s = MODELO
    for k, v in trocas.items():
        s = s.replace(k, v)
    if not quem:
        s = s.replace("<title>%s | ESCUDO Concursos</title>" % html.escape(titulo),
                      "<title>%s</title>" % html.escape(titulo_curto(meta, prods)), 1)
    # 21/11/2026: o guia não carregava o site.js, e quem chegava do ChatGPT num guia ia para o curso sem a origem
    # (src) nem a página de entrada (sck) no link de compra da Hotmart.
    s = s.replace("</body>", '<script src="../assets/js/site.js?v=11" defer></script>\n</body>', 1)
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


# Seção "Provas anteriores" em todo guia (20/11/2026): link do site oficial da banca citada no campo `banca`.
# Endereços testados em 20/11/2026. Ordem importa: vale a primeira banca que aparece no texto do campo.
BANCAS = [
    (r"cebraspe", "Cebraspe", "https://www.cebraspe.org.br/concursos/encerrados"),
    (r"\bFCC\b|Carlos Chagas", "Fundação Carlos Chagas (FCC)", "https://www.concursosfcc.com.br/"),
    (r"\bFGV\b", "FGV Conhecimento", "https://conhecimento.fgv.br/concursos"),
    (r"vunesp", "Fundação Vunesp", "https://www.vunesp.com.br/"),
    (r"aocp", "Instituto AOCP", "https://www.institutoaocp.org.br/"),
    (r"idecan", "IDECAN", "https://idecan.org.br/"),
    (r"quadrix", "Instituto Quadrix", "https://www.quadrix.org.br/"),
    (r"ibade", "IBADE", "https://www.ibade.org.br/"),
    (r"cesgranrio", "Fundação Cesgranrio", "https://www.cesgranrio.org.br/"),
    (r"ibgp", "IBGP", "https://www.ibgpconcursos.com.br/"),
    (r"selecon", "Instituto SELECON", "https://selecon.org.br/"),
    (r"idcap", "IDCAP", "https://www.idcap.org.br/"),
    (r"idib", "IDIB", "https://concurso.idib.org.br/"),
    (r"fadesp", "Fadesp", "https://portalfadesp.org.br/"),
    (r"nazar", "Instituto Nazaré", "https://institutonazare.selecao.net.br/"),
    (r"avalia", "Instituto Avalia", "https://avalia.org.br/"),
    (r"verbena", "Instituto Verbena/UFG", "https://www.institutoverbena.ufg.br/"),
    (r"fafipa", "Fundação FAFIPA", "https://www.fafipa.org/"),
    (r"furb", "FURB", "https://www.furb.br/"),
    (r"fepese", "FEPESE", "https://fepese.org.br/"),
    (r"ibfc", "IBFC", "https://www.ibfc.org.br/"),
    (r"uerr", "UERR", "https://www.uerr.edu.br/"),
    (r"ufmt", "UFMT", "https://www.ufmt.br/"),
    (r"\bCRS\b|PMMG", "Centro de Recrutamento e Seleção da PMMG", "https://www.policiamilitar.mg.gov.br/"),
]


def secao_provas(meta):
    banca = str(meta.get("banca", ""))
    achadas = [(m.start(), nome, url) for pad, nome, url in BANCAS for m in [re.search(pad, banca, re.I)] if m]
    if not achadas:
        return ""
    _, nome, url = min(achadas)
    previsto = "a definir" in banca.lower() or "previsto" in str(meta.get("situacao", "")).lower()
    abre = ("O edital novo ainda não saiu, mas as provas e os gabaritos oficiais do último concurso" if previsto
            else "As provas e os gabaritos oficiais deste concurso e dos anteriores")
    return ("\n\n## Onde estão as provas anteriores?\n\n%s ficam no site da banca, [%s](%s), na área de concursos "
            "(procure o órgão e o cargo; muitas vezes ficam em \"encerrados\"). Baixe só de lá ou do site do próprio órgão: "
            "cópias em outros sites podem estar incompletas, sem as anulações ou com gabarito errado. Resolver a prova "
            "anterior cronometrada, depois de estudar o conteúdo, é o melhor termômetro do nível da banca.\n"
            % (abre, nome, url))


guias = []
for arq in sorted((RAIZ / "_config" / "guias").glob("*.md")):
    if arq.name.startswith("_"):  # arquivos de apoio (ex.: _PROMPT-GUIA.md), não são guias
        continue
    meta, corpo = le(arq)
    slug = meta.get("slug") or arq.stem
    if slug != "quem-faz" and "provas anteriores" not in corpo.lower():
        sp = secao_provas(meta)
        if sp:
            m_faq = re.search(r"^## Perguntas frequentes\s*$", corpo, re.M)
            corpo = corpo[:m_faq.start()].rstrip() + sp + "\n" + corpo[m_faq.start():] if m_faq else corpo.rstrip() + sp
    h1, prods = monta(meta, corpo, slug)
    if slug != "quem-faz":
        guias.append((slug, h1, prods, meta))
    print("ok", slug)

# rodapé: link "Quem faz" em todas as páginas; link do guia nas páginas de curso
_NOMES = json.loads((RAIZ / "_config" / "nomes.json").read_text(encoding="utf-8"))["cursos"]
guia_do_curso = {p["id"]: slug for slug, _, prods, _ in guias for p in prods}
for pag in [RAIZ / "index.html"] + sorted(RAIZ.glob("*/index.html")):
    s = pag.read_text(encoding="utf-8")
    if 'class="rodape"' not in s or "<small>©" not in s:
        continue
    pre = "" if pag.parent == RAIZ else "../"
    links = '<a class="rodape-link" href="%squem-faz/">Quem faz a ESCUDO</a>' % pre
    if (RAIZ / "noticias" / "index.html").exists():  # blog (blog.py), 08/11/2026
        links = '<a class="rodape-link" href="%snoticias/">Notícias e dicas de concursos</a> · ' % pre + links
    curso = pag.parent.name
    if curso in guia_do_curso:
        links = '<a class="rodape-link" href="../%s/">%s</a> · ' % (guia_do_curso[curso], _NOMES.get(curso, {}).get("rotulo_guia") or "Guia do concurso: edital, vagas e o que cai") + links
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

# 22/11/2026: este script regrava os guias do zero e apagava os blocos que o conversao.py insere
# ("Avise-me quando sair o edital" e "Simulado grátis"). Agora ele chama o conversao.py no fim,
# então rodar só o guias.py (como a rotina do blog faz) já devolve os blocos. A Black Friday e a
# pré-venda não dependem disso: ficam no site.js e no produtos.json.
import sys as _sys
_sys.path.insert(0, str(RAIZ / "_config"))
import conversao as _conversao
_conversao.main()
