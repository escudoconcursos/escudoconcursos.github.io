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
PAGINAS = ["index.html", "pmmg-cfo-2027/index.html", "pmmg-soldado-2026/index.html", "policial-penal-pb-2026/index.html", "pmac-soldado-2026/index.html", "cbmes-soldado-2026/index.html", "seedf-pedagogia-2026/index.html", "seedf-professor-2026/index.html", "pcto-oficial-investigador-2026/index.html", "pcpa-investigador-2026/index.html", "pcpa-escrivao-2026/index.html", "pmrr-soldado-2026/index.html", "gm-joinville-2026/index.html", "gm-balneario-camboriu-2026/index.html", "tecnico-defensoria-dpe-pb-2026/index.html", "pmpe-soldado-2026/index.html", "gm-sao-goncalo-2026/index.html", "pmal-soldado-2026/index.html", "cbmpe-soldado-2026/index.html", "pcpe-agente-2026/index.html", "agente-educativo-aparecida-2026/index.html", "pedagogia-aparecida-2026/index.html", "gcm-santana-2026/index.html", "gcm-salvador-2026/index.html", "gm-recife-2026/index.html", "assistente-semusa-porto-velho-2026/index.html", "tecnico-enfermagem-porto-velho-2026/index.html", "professor-semed-porto-velho-2026/index.html", "soldado-pmsc-2026/index.html", "policial-penal-pr-2026/index.html", "policial-penal-pe-2026/index.html", "escrevente-tjsp-2026/index.html", "assistente-administrativo-contagem-2026/index.html", "tecnico-bancario-banestes-2026/index.html", "investigador-policia-civil-mg-pcmg-2026/index.html", "soldado-pmpr-2026/index.html", "agente-administrativo-curitiba-2026/index.html", "pmerj-soldado-2026/index.html", "pmpa-soldado-2026/index.html", "cbm-al-soldado-2026/index.html", "pmba-soldado-2026/index.html", "pmesp-soldado-2026/index.html", "gm-campinas-2026/index.html", "pcac-oficial-investigador-2026/index.html", "afiliados/index.html", "404.html"]
SITEMAP = ["", "pmmg-cfo-2027/", "pmmg-soldado-2026/", "policial-penal-pb-2026/", "pmac-soldado-2026/", "cbmes-soldado-2026/", "seedf-pedagogia-2026/", "seedf-professor-2026/", "pcto-oficial-investigador-2026/", "pcpa-investigador-2026/", "pcpa-escrivao-2026/", "pmrr-soldado-2026/", "gm-joinville-2026/", "gm-balneario-camboriu-2026/", "tecnico-defensoria-dpe-pb-2026/", "pmpe-soldado-2026/", "gm-sao-goncalo-2026/", "pmal-soldado-2026/", "cbmpe-soldado-2026/", "pcpe-agente-2026/", "agente-educativo-aparecida-2026/", "pedagogia-aparecida-2026/", "gcm-santana-2026/", "gcm-salvador-2026/", "gm-recife-2026/", "assistente-semusa-porto-velho-2026/", "tecnico-enfermagem-porto-velho-2026/", "professor-semed-porto-velho-2026/", "soldado-pmsc-2026/", "policial-penal-pr-2026/", "policial-penal-pe-2026/", "escrevente-tjsp-2026/", "assistente-administrativo-contagem-2026/", "tecnico-bancario-banestes-2026/", "investigador-policia-civil-mg-pcmg-2026/", "soldado-pmpr-2026/", "agente-administrativo-curitiba-2026/", "pmerj-soldado-2026/", "pmpa-soldado-2026/", "cbm-al-soldado-2026/", "pmba-soldado-2026/", "pmesp-soldado-2026/", "gm-campinas-2026/", "pcac-oficial-investigador-2026/", "afiliados/"]


# guias:extra (incluído por guias.py: guias de concurso, Quem faz e cursos que faltavam no sitemap)
_extra = sorted(d.parent.name + "/" for d in RAIZ.glob("concurso-*/index.html"))
if (RAIZ / "quem-faz" / "index.html").exists():
    _extra.append("quem-faz/")
_extra += sorted(d.parent.name + "/" for d in RAIZ.glob("concursos-*/index.html"))  # páginas de carreira e estado (hubs.py)
_extra += sorted(d.parent.parent.name + "/amostra/" for d in RAIZ.glob("*/amostra/index.html"))  # amostras grátis (amostra.py)
_extra += ["noticias/"] if (RAIZ / "noticias" / "index.html").exists() else []  # blog (blog.py)
_extra += sorted("noticias/" + d.parent.name + "/" for d in (RAIZ / "noticias").glob("*/index.html"))
if (RAIZ / "guarda-municipal" / "index.html").exists():
    _extra.append("guarda-municipal/")
if (RAIZ / "recenseador-ibge-2026" / "index.html").exists():
    _extra.append("recenseador-ibge-2026/")
for _u in _extra:
    if _u not in SITEMAP:
        SITEMAP.append(_u)
    if _u + "index.html" not in PAGINAS:
        PAGINAS.append(_u + "index.html")

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
    import subprocess

    def lastmod(u):
        """Data do último commit da página (ajuda o Google a voltar depois de retificação de edital)."""
        alvo = (u or ".") + ("index.html" if u else "/index.html")
        try:
            r = subprocess.run(["git", "-C", str(RAIZ), "log", "-1", "--format=%cs", "--", alvo],
                               capture_output=True, text=True, timeout=20)
            d = r.stdout.strip()
        except Exception:
            d = ""
        return "<lastmod>%s</lastmod>" % d if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) else ""

    urls = "".join("  <url><loc>%s%s</loc>%s</url>\n" % (base, u, lastmod(u)) for u in SITEMAP)
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

# link "Notícias" no topo de todas as páginas (blog.py, 08/11/2026): reaplica aqui porque scripts que rodam
# depois do blog.py (afiliados.py) regeram páginas inteiras
try:
    sys.path.insert(0, str(RAIZ / "_config"))
    from blog import menu_noticias
    if (RAIZ / "noticias" / "index.html").exists():
        menu_noticias()
except Exception as e:  # nunca travar o aplicar por causa do blog
    print("aviso: menu Notícias não aplicado:", e)
