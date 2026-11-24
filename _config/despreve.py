# -*- coding: utf-8 -*-
"""Fim da pré-venda de R$ 35 (24/11/2026, pedido do Mateus).

Regra nova: curso pré-edital fica no preço padrão (R$ 47 com o cupom de lançamento XX37 a R$ 37 até 31/12/2026).
O preço só sobe quando o edital sair. Desfaz o prevenda.py: tira "prevenda" do produtos.json, volta o cupom XX37
e troca os textos de "pré-venda R$ 35" nas páginas dos cursos, amostras e guias. Os cursos de edital aberto não mudam.
A promessa de atualização grátis quando sair o edital continua no selo de pré-edital.

Uso: python -X utf8 _config/despreve.py   (depois rodar vitrine, hubs, onda1, amostra, guias, simulados, conversao,
afiliados, llms_cursos, aplicar, contador)
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQ = RAIZ / "_config/produtos.json"
DADOS = json.loads(ARQ.read_text(encoding="utf-8"))
ATE = "2026-12-31"
D = "31/12/2026"
OFF = round((47 - 37) / 47 * 100)  # 21


def trocar(t, v, n):
    """v = cupom XX35, n = cupom XX37."""
    pares = [
        (f'<p class="cupom"><b>Preço de pré-venda</b> com o cupom <code>{v}</code>, até sair o edital. '
         f'Quem compra agora recebe de graça a atualização para o edital novo. Pelo botão, o cupom já vai preenchido.</p>',
         f'<p class="cupom">com o cupom <code>{n}</code> até {D}. Pelo botão, o cupom já vai preenchido.</p>'),
        (f'<p class="cupom"><b>Pré-venda</b> com o cupom <code>{v}</code> até sair o edital, com atualização grátis para o edital novo.</p>',
         f'<p class="cupom">com o cupom <code>{n}</code> até {D}.</p>'),
        ("pré-venda<b>R$ 35</b>", f"com {n}<b>R$ 37</b>"),
        (f"(R$ 35,00 na pré-venda com o cupom {v}, até sair o edital)", f"(R$ 37,00 com o cupom {n} até {D})"),
        (f"por R$ 35 na pré-venda com o cupom {v}, até sair o edital", f"por R$ 37 com o cupom {n} até {D}"),
        (f"por R$ 35 na pré-venda com o cupom {v}", f"por R$ 37 com o cupom {n}"),
        (f"Na pré-venda, de R$ 47 por R$ 35 com o cupom {v} até sair o edital, com atualização grátis quando ele sair.",
         f"De R$ 47 por R$ 37 com o cupom {n} até {D}."),
        (f"Pré-venda com o cupom {v}: R$ 35 até sair o edital, com atualização grátis (preço cheio R$ 47).",
         f"Cupom {n}: R$ 37 até {D} (preço cheio R$ 47)."),
        (f"R$ 47, ou R$ 35 na pré-venda com o cupom {v} até sair o edital, com atualização grátis quando ele sair.",
         f"R$ 47, ou R$ 37 com o cupom {n} até {D}."),
        (f"de R$ 47 por R$ 35 na pré-venda com o cupom {v} até sair o edital, com atualização grátis quando ele sair",
         f"de R$ 47 por R$ 37 com o cupom {n} até {D}"),
        (f"{v} até sair o edital", f"{n} até {D}"),
    ]
    for a, b in pares:
        t = t.replace(a, b)
    return t.replace(v, n)


def pagina(arq, v, n):
    h = arq.read_text(encoding="utf-8")
    h0 = h
    for attr in ("data-cupom-ate", "data-fim-cupom"):
        h = h.replace(f'{attr}="2027-12-31T23:59:59-03:00"', f'{attr}="{ATE}T23:59:59-03:00"')
    h = re.sub(r'(<p class="de">de <s>R\$ 47</s> por <b class="off">)\d+% OFF(</b></p>\s*<p class="por"><small>R\$</small>)35(</p>)',
               lambda m: f"{m.group(1)}{OFF}% OFF{m.group(2)}37{m.group(3)}", h)
    h = trocar(h, v, n)
    if h != h0:
        arq.write_text(h, encoding="utf-8")
        return True
    return False


def main():
    mudou = []
    for p in DADOS["produtos"]:
        c = p.get("cupom") or {}
        v = c.get("codigo", "")
        if not (p.get("prevenda") and v.endswith("35")):
            continue
        n = c.get("_antes") or v[:-2] + "37"
        p["cupom"] = {"codigo": n, "preco": 37, "ate": ATE}
        p.pop("prevenda", None)
        pasta = RAIZ / p["link"].strip("/")
        tocados = [a.relative_to(RAIZ).as_posix() for a in pasta.rglob("index.html") if pagina(a, v, n)]
        for g in (RAIZ / "_config/guias").glob("*.md"):
            t = g.read_text(encoding="utf-8")
            if v in t:
                g.write_text(trocar(t, v, n), encoding="utf-8")
                tocados.append(g.name)
        mudou.append(p["id"])
        print(p["id"], v, "->", n, "|", ", ".join(tocados))
    if mudou:
        ARQ.write_text(json.dumps(DADOS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(len(mudou), "cursos voltaram ao padrão")


if __name__ == "__main__":
    main()
