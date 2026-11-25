# -*- coding: utf-8 -*-
"""Aviso de pré-venda nos cursos pré-edital (25/11/2026, pedido do Mateus).

Regra: preço padrão R$ 47 (ou R$ 79,90 nos CFO) com o pequeno desconto do cupom de lançamento, e o aviso de que é
preço de pré-venda: quando o edital sair, o curso sobe de preço. Vale para todo curso listado em "pre" no editais.json.
Idempotente (marca "aviso-pre"). Curso pré-edital novo: rodar este script depois de criar a página.
Quando o edital de um curso sair: tirar o curso de "pre" e apagar os spans "aviso-pre" da página dele.

Uso: python -X utf8 _config/aviso_prevenda.py   (depois rodar guias com markdown, aplicar e contador)
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = json.loads((RAIZ / "_config/produtos.json").read_text(encoding="utf-8"))
PRE = json.loads((RAIZ / "_config/editais.json").read_text(encoding="utf-8"))["pre"]
AVISO = '<span class="aviso-pre"> <b>Preço de pré-venda:</b> quando o edital sair, o curso vai subir de preço.</span>'
AVISO_MD = " **Preço de pré-venda:** quando o edital sair, o curso vai subir de preço."


def main():
    for p in DADOS["produtos"]:
        if p["id"] not in PRE:
            continue
        cod = (p.get("cupom") or {}).get("codigo", "")
        arq = RAIZ / p["link"].strip("/") / "index.html"
        if not cod or not arq.exists():
            print("pulei", p["id"])
            continue
        h = arq.read_text(encoding="utf-8")
        n = 0
        if "aviso-pre" not in h:
            # parágrafos de preço com o cupom: insere o aviso logo depois da data do cupom
            h, n = re.subn(r'(<p class="cupom">com o cupom <code>%s</code> até \d\d/\d\d/\d{4}\.)' % re.escape(cod),
                           lambda m: m.group(1) + AVISO, h)
            if n:
                arq.write_text(h, encoding="utf-8")
        g = 0
        for md in (RAIZ / "_config/guias").glob("*.md"):
            t = md.read_text(encoding="utf-8")
            if cod not in t or "Preço de pré-venda:" in t:
                continue
            t2, k = re.subn(r'(com o cupom %s(?: de cada cargo)?,? até \d\d/\d\d/\d{4}\.)' % re.escape(cod),
                            lambda m: m.group(1) + AVISO_MD, t)
            if k:
                md.write_text(t2, encoding="utf-8")
                g += k
        print(p["id"], cod, "página:", n, "guias:", g)


if __name__ == "__main__":
    main()
