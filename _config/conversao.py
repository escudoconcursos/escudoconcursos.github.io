# -*- coding: utf-8 -*-
"""Captação de quem ainda não vai comprar (22/11/2026, ideias 1 e 4 do estudo de vendas). Idempotente.

1. Lista "Avise-me quando sair o edital" (e-mail e WhatsApp) nas páginas de curso pré-edital (editais.json "pre")
   e nos guias desses cursos. O site.js (bloco 8) manda para o App da Web do Apps Script (pedido_url do site.json)
   com tipo=lista: vira linha na aba "Lista de espera" da planilha. No dia do edital, o disparo do Apps Script
   manda o aviso com o cupom só para quem está na lista daquele curso.
2. Chamada para o simulado grátis (/simulado-{curso}/, gerado pelo simulados.py) nas páginas de curso de edital
   aberto e nos guias, quando o simulado existe.

Uso: PYTHONIOENCODING=utf-8 python _config/conversao.py   (depois de onda1.py e guias.py; antes de aplicar.py)
"""
import html as H
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITE = json.loads((RAIZ / "_config/site.json").read_text(encoding="utf-8"))
NOMES = json.loads((RAIZ / "_config/nomes.json").read_text(encoding="utf-8"))["cursos"]
ED = json.loads((RAIZ / "_config/editais.json").read_text(encoding="utf-8"))
PROD = {p["id"]: p for p in json.loads((RAIZ / "_config/produtos.json").read_text(encoding="utf-8"))["produtos"]}
e = lambda s: H.escape(str(s), quote=True)


def bloco(h, nome, conteudo, onde):
    ini, fim = f"<!-- {nome}:inicio -->", f"<!-- {nome}:fim -->"
    trecho = f"{ini}{conteudo}{fim}"
    if ini in h:
        return re.sub(re.escape(ini) + r".*?" + re.escape(fim), lambda m: trecho, h, flags=re.S)
    return onde(h, trecho)


def nome_curso(cid):
    n = NOMES.get(cid, {})
    return (n.get("sigla", "") + " " + n.get("cargo", "")).strip() or PROD.get(cid, {}).get("titulo", cid)


def form_lista():
    return """<form class="pedido-form lista-form" data-lista-form>
      <label>Seu e-mail <input name="email" type="email" required maxlength="120" placeholder="voce@email.com" autocomplete="email"></label>
      <label>WhatsApp (com DDD) <input name="whatsapp" type="tel" maxlength="20" placeholder="(00) 90000-0000" autocomplete="tel" inputmode="tel"></label>
      <label class="pedido-isca" aria-hidden="true">Não preencha <input name="site_url" tabindex="-1" autocomplete="off"></label>
      <button class="btn" type="submit">Quero o aviso do edital</button>
    </form>"""


def lista_html(cid, onde):
    n = NOMES.get(cid, {})
    p = PROD.get(cid, {})
    attrs = (f'data-lista data-curso="{e(cid)}" data-concurso="{e(n.get("sigla", ""))}" data-cargo="{e(n.get("cargo", ""))}" '
             f'data-origem-bloco="{e(onde)}" data-endpoint="{e(SITE.get("pedido_url", ""))}" data-email="{e(SITE.get("email", ""))}"')
    if onde == "guia":
        return f"""
<aside class="pedido avise-guia" id="avise" aria-labelledby="t-avise" {attrs}>
  <h3 id="t-avise">Avise-me quando sair o edital</h3>
  <p>Deixe seu e-mail e o seu WhatsApp. No dia em que o edital {e(n.get('sigla', ''))} sair, você recebe o resumo (vagas, salário, inscrições e o que mudou no programa) e um cupom só para quem está na lista.</p>
  {form_lista()}
  <p class="pedido-alt">Seus dados ficam só com a ESCUDO e servem só para este aviso.</p>
</aside>
"""
    pre = f' e com a pré-venda de R$ {p["cupom"]["preco"]}' if p.get("prevenda") else ""
    return f"""
<section class="secao creme avise" id="avise" aria-labelledby="t-avise" {attrs}>
  <div class="wrap estreito">
    <p class="kicker">Edital ainda não saiu</p>
    <h2 id="t-avise">Avise-me quando sair o <em>edital {e(n.get('sigla', ''))}</em></h2>
    <p>Deixe seu e-mail e o seu WhatsApp. No dia em que o edital sair, você recebe o resumo (vagas, salário, inscrições e o que mudou no programa) e um cupom só para quem está na lista. Sem spam: só o aviso do edital.</p>
    {form_lista()}
    <p class="lista-nota">Seus dados ficam só com a ESCUDO e servem só para este aviso. Para sair da lista, é só responder o e-mail.</p>
  </div>
</section>
"""


def simulado_html(cid, qtd):
    n = NOMES.get(cid, {})
    return f"""
<section class="secao creme simulado-cta" aria-labelledby="t-simcta">
  <div class="wrap estreito">
    <p class="kicker">Grátis, sem cadastro para começar</p>
    <h2 id="t-simcta">Simulado grátis <em>{e(n.get('sigla', ''))}</em></h2>
    <p>{qtd} questões no estilo da banca, com nota na hora por disciplina. O gabarito comentado sai depois de informar o e-mail.</p>
    <p><a class="btn" href="../simulado-{e(cid)}/" data-goatcounter-click="simulado-cta" data-goatcounter-title="simulado-cta {e(cid)}">Fazer o simulado grátis <svg aria-hidden="true"><use href="#i-seta"/></svg></a></p>
  </div>
</section>
"""


def simulado_guia(cid, qtd):
    n = NOMES.get(cid, {})
    return f"""
<aside class="pedido simulado-guia" aria-label="Simulado grátis">
  <h3>Simulado grátis {e(n.get('sigla', ''))}</h3>
  <p>{qtd} questões no estilo da banca, com nota na hora por disciplina e gabarito comentado.</p>
  <a class="btn" href="../simulado-{e(cid)}/" data-goatcounter-click="simulado-cta" data-goatcounter-title="simulado-cta {e(cid)}">Fazer o simulado grátis</a>
</aside>
"""


def apos_hero(h, t):
    """Depois da primeira seção (o topo com o preço)."""
    i = h.find("</section>", h.find('class="escuro hero"'))
    if i < 0:
        return h
    i += len("</section>")
    return h[:i] + "\n" + t + h[i:]


def antes_faq_guia(h, t):
    for marca in ("<h2>Perguntas frequentes</h2>", '<p class="guia-rodape">', "</article>"):
        i = h.find(marca)
        if i > 0:
            return h[:i] + t + "\n" + h[i:]
    return h


def link_avise(h):
    """Linha discreta logo abaixo do botão do topo: quem não vai comprar agora desce para a lista."""
    alvo = '<ul class="selos">'
    i = h.find(alvo, h.find('id="oferta"'))
    if i < 0:
        return h
    return bloco(h, "avise-link", '<p class="avise-link"><a href="#avise" data-goatcounter-click="avise-link" data-goatcounter-title="avise-link">Ainda não vai comprar? Receba o aviso quando sair o edital</a></p>\n        ',
                 lambda hh, t: hh[:i] + t + hh[i:])


def guias_por_curso():
    g = {}
    for md in (RAIZ / "_config/guias").glob("concurso-*.md"):
        m = re.search(r"^curso_id:\s*(.+)$", md.read_text(encoding="utf-8"), re.M)
        if not m:
            continue
        v = m.group(1).strip()
        ids = json.loads(v) if v.startswith("[") else [v.strip("\"")]
        for cid in ids:
            g.setdefault(cid, []).append(md.stem)
    return g


def main():
    sims = {p.parent.name.replace("simulado-", ""): len(json.loads((RAIZ / "_config/simulados" / (p.parent.name.replace("simulado-", "") + ".json")).read_text(encoding="utf-8"))["questoes"])
            for p in RAIZ.glob("simulado-*/index.html") if (RAIZ / "_config/simulados" / (p.parent.name.replace("simulado-", "") + ".json")).exists()}
    guias = guias_por_curso()
    feitos = []
    for cid in NOMES:
        arq = RAIZ / cid / "index.html"
        if not arq.exists():
            continue
        h = h0 = arq.read_text(encoding="utf-8")
        if cid in ED["pre"]:
            h = bloco(h, "lista-edital", lista_html(cid, "curso"), apos_hero)
            h = link_avise(h)
        if cid in sims:
            h = bloco(h, "simulado-cta", simulado_html(cid, sims[cid]), apos_hero)
        if h != h0:
            arq.write_text(h, encoding="utf-8")
            feitos.append(cid)
    for cid, slugs in guias.items():
        for slug in slugs:
            arq = RAIZ / slug / "index.html"
            if not arq.exists():
                continue
            h = h0 = arq.read_text(encoding="utf-8")
            if cid in ED["pre"] and "lista-edital:inicio" not in h:
                h = bloco(h, "lista-edital", lista_html(cid, "guia"), antes_faq_guia)
            if cid in sims and f"simulado-{cid}/" not in h:
                h = bloco(h, f"simulado-cta-{cid}", simulado_guia(cid, sims[cid]), antes_faq_guia)
            if h != h0:
                arq.write_text(h, encoding="utf-8")
                feitos.append(slug)
    print(len(feitos), "páginas:", ", ".join(feitos))


if __name__ == "__main__":
    main()
