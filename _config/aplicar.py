# -*- coding: utf-8 -*-
"""Aplica _config/site.json nas páginas do site (pode rodar quantas vezes quiser).

- Preenche os elementos marcados com data-cfg="chave" (razão social, CNPJ, endereço, e-mail).
- O e-mail vira link mailto: quando tiver "@".
- Se "url_base" estiver preenchida (ex.: https://usuario.github.io/escudo/), deixa absolutos os
  endereços marcados com data-abs (og:image, og:url, canonical, links da 404), que o WhatsApp e o
  Instagram exigem, e gera sitemap.xml + a linha Sitemap do robots.txt.

Uso: PYTHONIOENCODING=utf-8 python 07-site/_config/aplicar.py
"""
import html, json, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((RAIZ / "_config" / "site.json").read_text(encoding="utf-8"))
PAGINAS = ["index.html", "pmpe-soldado-2026/index.html", "gm-sao-goncalo-2026/index.html", "404.html"]
SITEMAP = ["", "pmpe-soldado-2026/", "gm-sao-goncalo-2026/"]

base = (CFG.get("url_base") or "").strip()
if base and not base.endswith("/"):
    base += "/"


def preenche(m):
    abre, tag, chave, _, fecha = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
    if chave not in CFG:
        return m.group(0)
    valor = str(CFG[chave])
    if chave == "email":
        href = "mailto:" + valor if "@" in valor else "#contato"
        abre = re.sub(r'href="[^"]*"', 'href="%s"' % html.escape(href, quote=True), abre)
    return abre + html.escape(valor, quote=False) + fecha


def absoluto(m):
    tag = m.group(0)
    caminho = m.group(1)
    return re.sub(r'\b(href|content)="[^"]*"', lambda a: '%s="%s"' % (a.group(1), base + caminho), tag, count=1)


pendentes = set()
for rel in PAGINAS:
    p = RAIZ / rel
    s = p.read_text(encoding="utf-8")
    s = re.sub(r'(<(\w+)\b[^>]*\bdata-cfg="(\w+)"[^>]*>)(.*?)(</\2>)', preenche, s, flags=re.S)
    if base:
        s = re.sub(r'<(?:link|meta|a)\b[^>]*\bdata-abs="([^"]*)"[^>]*>', absoluto, s)
    p.write_text(s, encoding="utf-8")
    pendentes |= set(re.findall(r'data-cfg="\w+"[^>]*>\s*(\[[^\]]+\])', s))
    print("ok", rel)

robots = "User-agent: *\nAllow: /\n"
if base:
    urls = "".join("  <url><loc>%s%s</loc></url>\n" % (base, u) for u in SITEMAP)
    (RAIZ / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % urls,
        encoding="utf-8")
    robots += "\nSitemap: %ssitemap.xml\n" % base
    print("ok sitemap.xml")
(RAIZ / "robots.txt").write_text(robots, encoding="utf-8")

if pendentes:
    print("Ainda faltam:", ", ".join(sorted(pendentes)))
if not base:
    print("Aviso: url_base vazia; og:image e og:url continuam relativos (o WhatsApp precisa do endereço absoluto).")
