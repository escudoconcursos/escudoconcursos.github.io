# -*- coding: utf-8 -*-
"""Monta a vitrine da página inicial a partir de _config/produtos.json (pode rodar quantas vezes quiser).

- Reescreve, no index.html, o trecho entre <!-- vitrine:inicio --> e <!-- vitrine:fim -->:
  botões de filtro por carreira (só as carreiras que têm curso) e os cartões, já na ordem de urgência
  do dia em que o script rodou. No navegador, o assets/js/site.js refaz a ordem e os selos com a data
  do visitante e esconde o curso no dia seguinte à prova.
- Gera um atalho por curso (ex.: /pmpe/), uma página que redireciona para o curso, para citar em post e story.

Uso: PYTHONIOENCODING=utf-8 python _config/vitrine.py   (depois rode o aplicar.py)
"""
import datetime as dt, html, json, pathlib, re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DADOS = json.loads((RAIZ / "_config" / "produtos.json").read_text(encoding="utf-8"))
CARREIRAS = DADOS["carreiras"]
FUSO = dt.timezone(dt.timedelta(hours=-3))
HOJE = dt.datetime.now(FUSO).date()
e = lambda s: html.escape(str(s), quote=True)


def d(s):
    return dt.date.fromisoformat(s)


def ddmm(s, ano=False):
    x = d(s)
    return x.strftime("%d/%m/%Y" if ano else "%d/%m")


def eventos(p):
    """Prazos do curso em ordem: o primeiro que ainda não passou é o que aparece no selo."""
    ev = []
    c = p.get("cupom")
    if c:
        ev.append({"tipo": "cupom", "data": c["ate"]})
    if p.get("inscricoes_ate"):
        ev.append({"tipo": "inscricoes", "data": p["inscricoes_ate"]})
    ev.append({"tipo": "prova", "data": p["prova"]})
    return sorted(ev, key=lambda x: (x["data"], x["tipo"] != "cupom"))


def selo(p):
    """Mesmo texto que o site.js monta (manter os dois iguais)."""
    ev = [x for x in eventos(p) if d(x["data"]) >= HOJE]
    if not ev:
        return None, "", False
    x = ev[0]
    juntos = x["tipo"] == "cupom" and any(y["tipo"] == "inscricoes" and y["data"] == x["data"] for y in ev)
    txt = {"cupom": "Cupom e inscrições até %s" if juntos else "Cupom até %s",
           "inscricoes": "Inscrições até %s", "prova": "Prova em %s"}[x["tipo"]] % ddmm(x["data"])
    faltam = (d(x["data"]) - HOJE).days
    if faltam <= 7:
        txt += " · último dia" if faltam == 0 else " · faltam %d dia%s" % (faltam, "s" if faltam > 1 else "")
    return x["data"], txt, faltam <= 7


def cartao(p):
    chave, txt, urgente = selo(p)
    c = p.get("cupom")
    ev = json.dumps(eventos(p), ensure_ascii=False, separators=(",", ":"))
    brasao = ('<img class="tag-orgao" src="%s" width="61" height="80" alt="">' % e(p["brasao"])) if p.get("brasao") else ""
    itens = "".join("<li>%s</li>" % e(i) for i in p["itens"]) + "<li>Prova em %s</li>" % ddmm(p["prova"], True)
    if c and d(c["ate"]) >= HOJE:
        valor = ('<p class="valor" data-cupom-ate="%sT23:59:59-03:00">De <s>R$ %s</s> por R$ %s com o cupom %s</p>\n'
                 '          <p class="valor" data-sem-cupom hidden>R$ %s</p>' % (c["ate"], p["preco"], c["preco"], e(c["codigo"]), p["preco"]))
    else:
        valor = '<p class="valor">R$ %s</p>' % p["preco"]
    externo = p["link"].startswith("http")
    return f"""      <li class="produto {e(p['tema'])}" data-oferta data-carreira="{e(p['carreira'])}" data-eventos='{e(ev)}'>
        <a class="capa" href="{e(p['link'])}" tabindex="-1" aria-hidden="true"><img src="{e(p['imagem'])}" width="560" height="560" loading="lazy" alt=""></a>
        <div class="corpo">
          <p class="selo{' urgente' if urgente else ''}" data-selo>{e(txt)}</p>
          <p class="tag">{brasao}{e(p['tag'])}</p>
          <h3>{e(p['titulo'])}</h3>
          <ul>{itens}</ul>
          <p class="carreira-rotulo">{e(CARREIRAS[p['carreira']])}</p>
          {valor}
          <a class="btn{' btn-ouro' if externo else ''}" href="{e(p['link'])}" aria-label="{e(p['botao'] + ': ' + p['titulo'] + ', ' + p['tag'])}">{e(p['botao'])}</a>
        </div>
      </li>""", chave


abertos = [p for p in DADOS["produtos"] if d(p["prova"]) >= HOJE]
cartoes = sorted((cartao(p) for p in abertos), key=lambda t: t[1])
usadas = [k for k in CARREIRAS if any(p["carreira"] == k for p in abertos)]
botoes = ['<button type="button" class="chip" data-filtro="" aria-pressed="true">Todas <span data-conta="">%d</span></button>' % len(abertos)]
botoes += ['<button type="button" class="chip" data-filtro="%s" aria-pressed="false">%s <span data-conta="%s">%d</span></button>'
           % (k, e(CARREIRAS[k]), k, sum(p["carreira"] == k for p in abertos)) for k in usadas]

bloco = """<!-- vitrine:inicio (gerado por _config/vitrine.py a partir de produtos.json; não editar à mão) -->
    <div class="filtros" role="group" aria-label="Filtrar cursos por carreira" data-filtros hidden>
      %s
    </div>
    <p class="vitrine-info" data-vitrine-info aria-live="polite">Ordenados pelo prazo mais próximo: cupom, inscrições ou prova.</p>
    <ul class="produtos" data-vitrine>
%s
    </ul>
    <p class="vitrine-vazia" data-vazia%s>Novos cursos em breve. Acompanhe no Instagram <a href="https://www.instagram.com/escudoconcursos/">@escudoconcursos</a>.</p>
    <!-- vitrine:fim -->""" % ("\n      ".join(botoes), "\n".join(t[0] for t in cartoes), "" if not abertos else " hidden")

idx = RAIZ / "index.html"
s = idx.read_text(encoding="utf-8")
novo, n = re.subn(r"<!-- vitrine:inicio.*?<!-- vitrine:fim -->", lambda m: bloco, s, flags=re.S)
if n != 1:
    raise SystemExit("index.html sem os marcadores <!-- vitrine:inicio --> e <!-- vitrine:fim -->")
idx.write_text(novo, encoding="utf-8")
print("ok index.html: %d curso(s) aberto(s), carreiras: %s" % (len(abertos), ", ".join(usadas) or "nenhuma"))

for p in DADOS["produtos"]:
    if not p.get("atalho"):
        continue
    destino = p["link"] if p["link"].startswith("http") else "../" + p["link"]
    pasta = RAIZ / p["atalho"]
    pasta.mkdir(exist_ok=True)
    (pasta / "index.html").write_text(f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>ESCUDO Concursos: {e(p['titulo'])}</title>
<meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={e(destino)}">
<link rel="canonical" href="{e(destino)}"></head>
<body><p><a href="{e(destino)}">{e(p['titulo'])}, {e(p['tag'])}</a></p></body></html>
""", encoding="utf-8")
    print("ok atalho /%s/ -> %s" % (p["atalho"], destino))
