# -*- coding: utf-8 -*-
"""Avisa Bing, Yandex e outros buscadores do IndexNow que páginas do site mudaram (07/11/2026).
O Bing alimenta a busca do ChatGPT e do Copilot, então isso acelera a entrada das páginas novas lá.

A chave fica publicada na raiz do site em /<CHAVE>.txt (o arquivo tem só a chave).
Uso, DEPOIS do push e de o GitHub Pages publicar (1 a 2 minutos):
    python _config/indexnow.py                 (manda todas as URLs do sitemap.xml)
    python _config/indexnow.py --git HEAD~1    (só as páginas que mudaram desde esse commit)
Resposta 200 ou 202 = recebido. 403 = a chave ainda não está no ar. 422 = URL fora do domínio.
"""
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CHAVE = "ac15e44e3a02785dbe95af6a60f2aeab"
HOST = "escudoconcursos.com.br"
BASE = "https://" + HOST + "/"


def do_sitemap():
    xml = (RAIZ / "sitemap.xml").read_text(encoding="utf-8")
    return re.findall(r"<loc>([^<]+)</loc>", xml)


def do_git(desde):
    nomes = subprocess.run(["git", "-C", str(RAIZ), "diff", "--name-only", desde, "HEAD"],
                           capture_output=True, text=True, check=True).stdout.split()
    urls = set()
    for n in nomes:
        if n.startswith("_config/") or not n.endswith(".html"):
            continue
        if n == "index.html":
            urls.add(BASE)
        elif n.endswith("/index.html"):
            urls.add(BASE + n[: -len("index.html")])
    validas = set(do_sitemap())  # só manda o que está no sitemap (atalhos e páginas noindex ficam de fora)
    return sorted(u for u in urls if u in validas)


def main():
    urls = do_git(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[1] == "--git" else do_sitemap()
    if not urls:
        print("nenhuma URL para avisar")
        return
    corpo = json.dumps({"host": HOST, "key": CHAVE, "keyLocation": BASE + CHAVE + ".txt", "urlList": urls[:10000]}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=corpo, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print("IndexNow:", r.status, "-", len(urls), "URLs")
    except urllib.error.HTTPError as e:
        print("IndexNow recusou:", e.code, e.read()[:200])


if __name__ == "__main__":
    main()
