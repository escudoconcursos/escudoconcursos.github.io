# -*- coding: utf-8 -*-
"""APOSENTADO em 24/11/2026: o Mateus mandou voltar ao preço padrão (XX37) nos pré-edital; ver despreve.py. Não rodar.

Pré-venda dos cursos pré-edital (22/11/2026, ideia 3 do estudo de vendas, aprovada pelo Mateus a R$ 35).

Troca o cupom de lançamento XX37 (R$ 37 até 31/12) pelo cupom de pré-venda XX35 (R$ 35, 25,53% na Hotmart, sem data de fim),
"válido até sair o edital", com a promessa de atualização grátis. Só cursos de R$ 47 listados em "pre" no editais.json.
Idempotente. Marca "prevenda": true no produtos.json (vitrine.py, afiliados.py e llms_cursos.py leem essa marca).

Quando sair o edital de um curso: tirar "prevenda" e trocar o cupom no produtos.json (volta ao padrão XX37 com data),
mover o curso para "aberto" no editais.json, desativar o cupom XX35 na Hotmart e rodar a rotina de edital novo.

Uso: PYTHONIOENCODING=utf-8 python _config/prevenda.py   (depois rodar vitrine, hubs, onda1, guias, afiliados, aplicar, contador)
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQ = RAIZ / "_config/produtos.json"
DADOS = json.loads(ARQ.read_text(encoding="utf-8"))
PRE = json.loads((RAIZ / "_config/editais.json").read_text(encoding="utf-8"))["pre"]
ATE = "2027-12-31"  # data técnica: a pré-venda não tem data, acaba quando sai o edital
PRECO = 35
OFF = round((47 - PRECO) / 47 * 100)


def br(s):
    a, m, d = s.split("-")
    return f"{d}/{m}/{a}"


def pagina(p, velho, novo, data_velha):
    arq = RAIZ / p["link"] / "index.html"
    if not arq.exists():
        return "sem página"
    h = arq.read_text(encoding="utf-8")
    h0 = h
    dv = br(data_velha)
    for attr in ("data-cupom-ate", "data-fim-cupom"):
        h = h.replace(f'{attr}="{data_velha}T23:59:59-03:00"', f'{attr}="{ATE}T23:59:59-03:00"')
    h = h.replace(f"offDiscount={velho}", f"offDiscount={novo}")
    h = h.replace(f'<p class="cupom">com o cupom <code>{velho}</code> até {dv}. Pelo botão, o cupom já vai preenchido.</p>',
                  f'<p class="cupom"><b>Preço de pré-venda</b> com o cupom <code>{novo}</code>, até sair o edital. '
                  f'Quem compra agora recebe de graça a atualização para o edital novo. Pelo botão, o cupom já vai preenchido.</p>')
    h = h.replace(f'<p class="cupom">com o cupom <code>{velho}</code> até {dv}.</p>',
                  f'<p class="cupom"><b>Pré-venda</b> com o cupom <code>{novo}</code> até sair o edital, com atualização grátis para o edital novo.</p>')
    h = re.sub(r'(<div data-cupom-ate="%sT23:59:59-03:00">\s*<p class="de">de <s>R\$ 47</s> por <b class="off">)\d+%% OFF(</b></p>\s*<p class="por"><small>R\$</small>)37(</p>)' % ATE,
               lambda m: f"{m.group(1)}{OFF}% OFF{m.group(2)}{PRECO}{m.group(3)}", h)
    h = h.replace(f"com {velho}<b>R$ 37</b>", f"pré-venda<b>R$ {PRECO}</b>")
    h = h.replace(f"(R$ 37,00 com o cupom {velho} até {dv})", f"(R$ {PRECO},00 na pré-venda com o cupom {novo}, até sair o edital)")
    h = h.replace(f"por R$ 37 com o cupom {velho} até {dv}", f"por R$ {PRECO} na pré-venda com o cupom {novo}, até sair o edital")
    h = h.replace(f"por R$ 37 com o cupom {velho}", f"por R$ {PRECO} na pré-venda com o cupom {novo}")
    h = h.replace(f"{velho} até {dv}", f"{novo} até sair o edital")
    h = h.replace(velho, novo)
    if h != h0:
        arq.write_text(h, encoding="utf-8")
    resto = [m.group(0) for m in re.finditer(r".{0,60}R\$ ?37\b.{0,40}", h)]
    return ("ok" if h != h0 else "sem mudança") + (" | sobrou R$ 37: " + " || ".join(resto[:3]) if resto else "")


def guias(velho, novo, data_velha):
    for g in (RAIZ / "_config/guias").glob("*.md"):
        t = g.read_text(encoding="utf-8")
        if velho not in t:
            continue
        t2 = t.replace(f"De R$ 47 por R$ 37 com o cupom {velho} até {br(data_velha)}.",
                       f"Na pré-venda, de R$ 47 por R$ {PRECO} com o cupom {novo} até sair o edital, com atualização grátis quando ele sair.")
        t2 = t2.replace(f"{velho} até {br(data_velha)}", f"{novo} até sair o edital").replace(f"R$ 37 com o cupom {velho}", f"R$ {PRECO} com o cupom {novo}").replace(velho, novo)
        if t2 != t:
            g.write_text(t2, encoding="utf-8")
            print("   guia", g.name)


def main():
    mudou = False
    for p in DADOS["produtos"]:
        if p["id"] not in PRE or p.get("preco") != 47:
            continue
        c = p.get("cupom") or {}
        velho = c.get("codigo", "")
        if p.get("prevenda") and velho.endswith("35"):
            novo, velho_real, data_velha = velho, c.get("_antes", ""), c.get("_antes_ate", "")
        else:
            if not velho.endswith("37"):
                print("pulei", p["id"], velho)
                continue
            novo, velho_real, data_velha = velho[:-2] + "35", velho, c["ate"]
            p["cupom"] = {"codigo": novo, "preco": PRECO, "ate": ATE, "_antes": velho_real, "_antes_ate": data_velha}
            p["prevenda"] = True
            mudou = True
        print(p["id"], velho_real, "->", novo, "|", pagina(p, velho_real, novo, data_velha) if velho_real else "já feito")
        if velho_real:
            guias(velho_real, novo, data_velha)
    if mudou:
        ARQ.write_text(json.dumps(DADOS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
