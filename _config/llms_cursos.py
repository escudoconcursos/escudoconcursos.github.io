# -*- coding: utf-8 -*-
"""Seção "Cursos" do llms.txt gerada de _config/produtos.json (21/11/2026).

Antes a lista era escrita à mão, tinha só parte dos cursos e apontava para os atalhos (/pmpe/), que são páginas
de redirecionamento com noindex. Agora: todos os cursos, endereço canônico, preço, prova, inscrições e o guia
do concurso, para o ChatGPT e outros buscadores de IA citarem a página certa.

Uso: python -I -X utf8 _config/llms_cursos.py   (idempotente; rodar depois de mexer em produtos.json ou nos guias)
"""
import json
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://escudoconcursos.com.br/"
INI, FIM = "<!-- cursos:inicio -->", "<!-- cursos:fim -->"
HOJE = __import__("datetime").date.today().isoformat()


def data_br(iso):
    return "/".join(reversed(iso.split("-"))) if iso else ""


def guias():
    saida = {}
    for arq in (RAIZ / "_config" / "guias").glob("concurso-*.md"):
        m = re.search(r"^curso_id:\s*(.+)$", arq.read_text(encoding="utf-8"), re.M)
        for i in re.findall(r"[a-z0-9-]+-20\d\d", m.group(1) if m else ""):
            saida.setdefault(i, arq.stem)
    return saida


def main():
    prods = json.loads((RAIZ / "_config" / "produtos.json").read_text(encoding="utf-8"))["produtos"]
    g = guias()
    linhas = ["## Cursos", ""]
    for p in prods:
        link = p.get("link", "")
        if link.startswith("http") or not (RAIZ / link / "index.html").exists():
            continue
        pid = link.strip("/")
        partes = ["; ".join(p.get("itens", []))]
        preco = p.get("preco")
        if preco:
            txt = "R$ %s" % ("%.2f" % preco).replace(".", ",").replace(",00", "")
            cupom = p.get("cupom") or {}
            if isinstance(cupom, dict) and cupom.get("preco") and cupom.get("ate", "9999") >= HOJE:
                txt += " (R$ %s com o cupom %s)" % (("%.2f" % cupom["preco"]).replace(".", ",").replace(",00", ""), cupom.get("codigo", ""))
            partes.append(txt)
        if p.get("prova") and p["prova"] != "2099-12-31":
            partes.append("Prova em " + data_br(p["prova"]))
        if p.get("inscricoes_ate"):
            partes.append(("Inscrições até " if p["inscricoes_ate"] >= HOJE else "Inscrições encerradas em ") + data_br(p["inscricoes_ate"]))
        if pid in g:
            partes.append("Guia do concurso: %s%s/" % (BASE, g[pid]))
        nome = "%s: %s" % (p.get("tag", "").split(" · ")[0], p.get("titulo", ""))
        linhas.append("- [Apostila em PDF %s](%s%s/): %s" % (nome, BASE, pid, ". ".join(x for x in partes if x)))
    bloco = INI + "\n" + "\n".join(linhas) + "\n" + FIM
    arq = RAIZ / "llms.txt"
    s = arq.read_text(encoding="utf-8")
    if INI in s:
        s = re.sub(re.escape(INI) + r".*?" + re.escape(FIM), lambda m: bloco, s, flags=re.S)
    else:  # primeira vez: troca a lista escrita à mão (de "## Cursos" até o marcador das amostras)
        s = re.sub(r"## Cursos\n.*?(?=<!-- amostras:inicio -->)", lambda m: bloco + "\n\n", s, count=1, flags=re.S)
    arq.write_text(s, encoding="utf-8")
    print("ok llms.txt:", len(linhas) - 2, "cursos")


if __name__ == "__main__":
    main()
