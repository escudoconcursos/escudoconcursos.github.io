# -*- coding: utf-8 -*-
"""Onda 1 do plano de SEO (07/11/2026) nas páginas de curso. Idempotente: pode rodar quantas vezes quiser.

- H1 com a palavra-chave ("Apostila PM-SP 2026 em PDF") numa linha pequena acima do título grande.
- "% OFF" ao lado do preço riscado.
- Botão de compra no meio da página (depois de "Veja por dentro") e cliques contados no GoatCounter
  (compra-topo, compra-meio, compra-fim, compra-barra).
- Páginas reais do PDF ao lado de cada benefício de "O que você recebe" (usa as imagens da galeria).
- Trilha (Início > Carreira > Curso) com BreadcrumbList e bloco "Outros cursos para você" no fim.

Uso: PYTHONIOENCODING=utf-8 python _config/onda1.py   (depois de seo.py; antes de aplicar.py)
"""
import datetime as dt
import html as H
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
NOMES = json.loads((RAIZ / "_config/nomes.json").read_text(encoding="utf-8"))["cursos"]
DADOS = json.loads((RAIZ / "_config/produtos.json").read_text(encoding="utf-8"))
PRODUTOS = {p["id"]: p for p in DADOS["produtos"]}
CARREIRAS = DADOS["carreiras"]
_BEN = RAIZ / "_config/beneficios.json"
BENEFICIOS = json.loads(_BEN.read_text(encoding="utf-8")) if _BEN.exists() else {}  # {pasta: [{"item": início do texto, "img": "assets/img/x/b-y", "alt": "..."}]}
import importlib.util as _iu
_spec = _iu.spec_from_file_location("hubs", RAIZ / "_config/hubs.py")
HUBS = _iu.module_from_spec(_spec)
_spec.loader.exec_module(HUBS)  # hub_da_carreira() e hub_do_estado(): páginas da onda 2
_ED = RAIZ / "_config/editais.json"
EDITAIS = json.loads(_ED.read_text(encoding="utf-8")) if _ED.exists() else {"aberto": {}, "pre": {}}  # selo do edital
GUIAS = HUBS.guias()  # {curso: {slug do guia, banca, situação}}
BASE = json.loads((RAIZ / "_config/site.json").read_text(encoding="utf-8"))["url_base"]
HOJE = dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).date().isoformat()
ANO = "2026"
e = lambda s: H.escape(str(s), quote=True)
CARREIRA_PLURAL = {"policial": "cursos policiais", "administrativo": "cursos administrativos", "saude": "cursos de saúde",
                   "educacao": "cursos de educação", "tribunais": "cursos de tribunais", "fiscal": "cursos fiscais",
                   "bancaria": "cursos bancários"}


def bloco(html, nome, conteudo, onde):
    """Troca o trecho entre <!-- nome:inicio --> e <!-- nome:fim -->; se não existir, insere com onde(html, trecho)."""
    ini, fim = f"<!-- {nome}:inicio -->", f"<!-- {nome}:fim -->"
    trecho = f"{ini}{conteudo}{fim}"
    if ini in html:
        return re.sub(re.escape(ini) + r".*?" + re.escape(fim), lambda m: trecho, html, flags=re.S), True
    novo = onde(html, trecho)
    return novo, novo != html


def h1_palavra_chave(html, n):
    kw = f"Apostila {n['sigla']} {n.get('ano', ANO)} em PDF"
    m = re.search(r'<h1 id="titulo">(.*?)</h1>', html, flags=re.S)
    if not m:
        return html, False
    dentro = re.sub(r'<span class="h1-kw">.*?</span>\s*', "", m.group(1), flags=re.S)
    novo = f'<h1 id="titulo"><span class="h1-kw">{e(kw)}</span> {dentro}</h1>'
    html = html[:m.start()] + novo + html[m.end():]
    # o kicker do topo ("PM/SP 2026 · Apostila em PDF") repetia a mesma informação: sai, e o H1 assume
    hero = html.find('class="escuro hero"')
    k = re.compile(r'\s*<p class="kicker">[^<]*Apostila em PDF</p>')
    km = k.search(html, hero)
    if km and km.start() < html.find('<h1 id="titulo">'):
        html = html[:km.start()] + html[km.end():]
    return html, True


def off(html):
    def troca(m):
        bloco_ = m.group(0)
        if 'class="off"' in bloco_:
            return bloco_
        de = re.search(r"<s>R\$\s*([\d,]+)</s>", bloco_)
        por = re.search(r'<p class="por"><small>R\$</small>([\d,]+)</p>', bloco_)
        if not (de and por):
            return bloco_
        a, b = float(de.group(1).replace(",", ".")), float(por.group(1).replace(",", "."))
        if a <= b:
            return bloco_
        pct = round((a - b) / a * 100)
        return bloco_.replace("</s> por</p>", f'</s> por <b class="off">{pct}% OFF</b></p>', 1)
    return re.sub(r'<div data-cupom-ate="[^"]*">.*?</div>', troca, html, flags=re.S)


def contador_cliques(html):
    def marca(a_tag, nome):
        if "data-goatcounter-click" in a_tag:
            return a_tag
        return a_tag.replace("<a ", f'<a data-goatcounter-click="{nome}" data-goatcounter-title="{nome}" ', 1)
    html = re.sub(r'<a class="btn" data-observa [^>]*>', lambda m: marca(m.group(0), "compra-topo"), html)
    i = html.find('class="escuro secao cta-final"')
    if i > 0:
        j = html.find('<a class="btn"', i)
        if j > 0:
            k = html.find(">", j) + 1
            html = html[:j] + marca(html[j:k], "compra-fim") + html[k:]
    i = html.find('<div class="barra"')
    if i > 0:
        j = html.find('<a class="btn"', i)
        if j > 0:
            k = html.find(">", j) + 1
            html = html[:j] + marca(html[j:k], "compra-barra") + html[k:]
    return html


def botao_meio(html):
    """Botão de compra no fim de 'Veja por dentro' (antes, entre o topo e o fim da página não havia nenhum)."""
    topo = re.search(r'<a class="btn" (?:data-goatcounter-click="[^"]*" data-goatcounter-title="[^"]*" )?data-observa ([^>]*)>', html)
    sec = re.search(r'<section class="escuro secao" aria-labelledby="t-dentro">.*?</ul>\n', html, flags=re.S)
    if not (topo and sec):
        return html, False
    attrs = re.sub(r'\s*data-observa', "", topo.group(1))
    btn = (f'\n    <div class="compra-meio" data-oferta>\n      <a class="btn" data-goatcounter-click="compra-meio" '
           f'data-goatcounter-title="compra-meio" {attrs}>Quero o meu curso <svg aria-hidden="true"><use href="#i-seta"/></svg></a>\n'
           f'      <p>100% em PDF · Garantia de 7 dias · Pagamento pela Hotmart</p>\n    </div>\n    ')
    return bloco(html, "compra-meio", btn, lambda h, t: h[:sec.end()] + "    " + t + "\n" + h[sec.end():])


REGRAS = [  # (palavras do benefício, prefixos de imagem), em ordem de preferência
    (("páginas", "pdf"), ("capa",)),
    (("capítulos",), ("abertura",)),
    (("questões", "questão", "itens inéditos"), ("questoes",)),
    (("gabarito",), ("gabarito",)),
    (("memorizar", "pegadinha"), ("mapa", "linha", "fluxo")),
    (("memorizar", "pegadinha"), ("quadro", "nao-confunda", "exemplos", "fluxo")),
]


def imagens_beneficios(html, pasta=""):
    """Página real do PDF ao lado de cada benefício de 'O que você recebe'."""
    gal = re.findall(r'<a href="([^"]+-g\.webp)" data-zoom="([^"]*)"><img src="([^"]+)"[^>]*alt="([^"]*)"', html)
    sec = re.search(r'(<section class="secao claro" aria-labelledby="t-recebe">.*?<ul class="entregas(?: com-imagens)?)(">)(.*?)(</ul>)', html, flags=re.S)
    if not (gal and sec):
        return html, False
    nome = lambda src: src.rsplit("/", 1)[1].replace(".webp", "")
    livres = list(gal)
    itens = re.findall(r"<li>.*?</li>|<li class=\"com-img\">.*?</li>", sec.group(3), flags=re.S)
    novos = []
    for li in itens:
        li = re.sub(r'<span class="minis">.*?</span>', "", li, flags=re.S).replace('<li class="com-img">', "<li>")
        texto = re.sub(r"<[^>]+>", " ", li).lower()
        usados = []
        for palavras, prefixos in REGRAS:
            if len(usados) == 2:
                break
            if not any(p in texto for p in palavras):
                continue
            for g in livres:
                if nome(g[2]).startswith(prefixos):
                    usados.append(g)
                    livres.remove(g)
                    break
        if not usados:  # sem página na galeria: usa a página tirada do PDF para este benefício
            limpo = re.sub(r"\s+", " ", texto).strip()
            for b in BENEFICIOS.get(pasta, []):
                if limpo.startswith(re.sub(r"\s+", " ", b["item"]).strip().lower()):
                    src = "../" + b["img"]
                    usados.append((src + "-g.webp", b.get("alt", ""), src + ".webp", "Página da apostila: " + b.get("alt", b["item"])))
                    break
        if usados:
            minis = "".join(
                f'<a class="mini" href="{g[0]}" data-zoom="{g[1]}"><img src="{g[2]}" width="640" height="906" loading="lazy" decoding="async" alt="{g[3]}"></a>'
                for g in usados)
            li = li.replace("<li>", '<li class="com-img">', 1).replace("</p></li>", f"</p><span class=\"minis\">{minis}</span></li>")
        novos.append(li)
    corpo = sec.group(3)
    for velho, novo in zip(itens, novos):
        corpo = corpo.replace(velho, novo, 1)
    classe = sec.group(1) if " com-imagens" in sec.group(1) else sec.group(1) + " com-imagens"
    html = html[:sec.start()] + classe + sec.group(2) + corpo + sec.group(4) + html[sec.end():]
    return html, True


def trilha(html, pasta, n, p):
    car = p.get("carreira", "")
    rotulo = CARREIRAS.get(car, "Cursos")
    hub = HUBS.hub_da_carreira(pasta)
    destino = f"../{hub['slug']}/" if hub and (RAIZ / hub["slug"] / "index.html").exists() else f"../#{car}"
    if hub:
        rotulo = hub["nome"]
    atual = f"{n['sigla']} {n.get('ano', ANO)}: {n['cargo']}"
    nav = (f'<nav class="trilha" aria-label="Você está em"><div class="wrap"><a href="../">Início</a>'
           f'<span aria-hidden="true">›</span><a href="{e(destino)}">{e(rotulo)}</a>'
           f'<span aria-hidden="true">›</span><span aria-current="page">{e(atual)}</span></div></nav>\n')
    html, _ = bloco(html, "trilha", nav, lambda h, t: h.replace('<main id="conteudo">', t + '\n<main id="conteudo">', 1))
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Início", "item": BASE},
        {"@type": "ListItem", "position": 2, "name": rotulo, "item": BASE + destino.replace("../", "")},
        {"@type": "ListItem", "position": 3, "name": atual, "item": BASE + pasta + "/"}]}
    js = '\n<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False, indent=1) + "\n</script>\n"
    html, _ = bloco(html, "trilha-ld", js, lambda h, t: h.replace("</head>", t + "\n</head>", 1))
    return html


def ativo(p):
    prova = p.get("prova")
    return (not prova) or prova >= HOJE


def outros(html, pasta, n, p):
    car, uf = p.get("carreira"), n.get("uf")
    cands = []
    for pid, q in PRODUTOS.items():
        if pid == pasta or q.get("link", "").startswith("http") or pid not in NOMES or not ativo(q):
            continue
        nq = NOMES[pid]
        peso = (0 if nq.get("uf") == uf else 1, 0 if q.get("carreira") == car else 1, q.get("prova") or "2099-12-31")
        cands.append((peso, pid, q, nq))
    cands.sort()
    escolhidos = [c for c in cands if c[0][0] == 0 or c[0][1] == 0][:4]
    if not escolhidos:
        return html
    cards = "".join(
        f'\n      <li><a href="../{e(q["link"])}"><img src="../{e(q["imagem"])}" width="560" height="560" loading="lazy" decoding="async" alt="{e(q.get("alt", ""))}">'
        f'<span class="o-tag">{e(q.get("tag", ""))}</span><b>{e(q.get("titulo", nq["cargo"]))}</b></a></li>'
        for _, pid, q, nq in escolhidos)
    guia = ""
    g = GUIAS.get(pasta)
    if g and (RAIZ / g["slug"] / "index.html").exists():
        guia = f'<a href="../{g["slug"]}/">Guia do concurso: edital, vagas e o que cai</a> · '
    plural = CARREIRA_PLURAL.get(car, "cursos")
    hub, est = HUBS.hub_da_carreira(pasta), HUBS.hub_do_estado(pasta)
    existe = lambda h: h and (RAIZ / h["slug"] / "index.html").exists()
    todos = f'<a href="../{hub["slug"]}/">Ver todos: {e(hub["nome"].lower() if hub["tipo"] == "carreira" and hub["slug"] != "guarda-municipal" else hub["nome"])}</a>' if existe(hub) else f'<a href="../#{e(car)}">Ver todos os {plural}</a>'
    if existe(est):
        todos += f' · <a href="../{est["slug"]}/">Concursos {e(est["em"])}</a>' 
    sec = (f'\n<section class="secao creme outros" aria-labelledby="t-outros">\n  <div class="wrap">\n'
           f'    <p class="kicker">Continue estudando</p>\n    <h2 id="t-outros">Outros cursos <em>para você</em></h2>\n'
           f'    <ul class="outros-lista">{cards}\n    </ul>\n'
           f'    <p class="outros-links">{guia}{todos}</p>\n  </div>\n</section>\n')
    html, _ = bloco(html, "outros", sec, lambda h, t: h.replace("\n</main>", "\n" + t + "\n</main>", 1))
    return html


def selo_edital(html, pasta):
    """Selo logo acima do preço do topo: "De acordo com o Edital nº X · banca" ou, no pré-edital, a base usada."""
    a, pre = EDITAIS["aberto"].get(pasta), EDITAIS["pre"].get(pasta)
    if a:
        txt = f'De acordo com o <b>{e(a["edital"])}</b> · {e(a["banca"])}'
        cls = "selo-edital"
    elif pre is not None:
        base = f"o último edital (<b>{e(pre)}</b>)" if pre else "o último edital do cargo"
        txt = f"Pré-edital: baseado n{base}. Atualizado quando sair o novo"
        cls = "selo-edital selo-pre"
    else:
        return html, False
    sel = f'<p class="{cls}"><svg aria-hidden="true"><use href="#i-escudo"/></svg><span>{txt}</span></p>\n      '
    return bloco(html, "selo-edital", sel, lambda h, t: h.replace('<div class="preco" id="oferta" data-oferta>', t + '<div class="preco" id="oferta" data-oferta>', 1))


def main():
    for pasta, n in NOMES.items():
        arq = RAIZ / pasta / "index.html"
        if not arq.exists():
            print("falta", arq)
            continue
        html = arq.read_text(encoding="utf-8")
        p = PRODUTOS.get(pasta, {})
        html, ok_h1 = h1_palavra_chave(html, n)
        html, ok_selo = selo_edital(html, pasta)
        html = off(html)
        html, ok_meio = botao_meio(html)
        html = contador_cliques(html)
        html, ok_img = imagens_beneficios(html, pasta)
        html = trilha(html, pasta, n, p)
        html = outros(html, pasta, n, p)
        arq.write_text(html, encoding="utf-8")
        avisos = [x for x, ok in (("sem H1", ok_h1), ("sem botão do meio", ok_meio), ("sem imagens nos benefícios", ok_img), ("sem selo do edital", ok_selo)) if not ok]
        print("ok", pasta, ("| " + ", ".join(avisos)) if avisos else "")


if __name__ == "__main__":
    main()
