"""SEO das páginas de produto: título e descrição com "Apostila", kicker e dados estruturados.

Rodar depois de criar ou editar uma página de produto:
    PYTHONIOENCODING=utf-8 python _config/seo.py

Idempotente. Lê preço e cupom de _config/produtos.json e a palavra-chave de BUSCA abaixo.
Produto novo: acrescentar uma linha em BUSCA (como o concurseiro digita no Google).
"""
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BASE = "https://escudoconcursos.com.br/"

# Nome de busca de cada curso: _config/nomes.json (sigla + cargo), padrão do plano de SEO de 07/11/2026.
NOMES = json.loads((RAIZ / "_config" / "nomes.json").read_text(encoding="utf-8"))["cursos"]
BUSCA = {k: "%s %s" % (v["sigla"], v["cargo"]) for k, v in NOMES.items()}
ANO = "2026"
LIMITE_TITULO, LIMITE_DESC = 60, 155


def titulo_de(n):
    t = f"Apostila {n['sigla']} {ANO} em PDF: {n['cargo']} | ESCUDO"
    return t if len(t) <= LIMITE_TITULO else t.rsplit(" | ", 1)[0]


def numero(html, rotulo):
    m = re.search(r"<li><b>([\d.]+)</b><span>" + rotulo, html)
    return m.group(1) if m else ""


def descricao_de(html, n, p):
    cap, q = numero(html, "capítulos"), numero(html, "questões")
    pre = "Pré-edital" in p.get("tag", "") or p.get("prova") in (None, "2099-12-31")
    edital = "pronta para o próximo edital" if pre else "de acordo com o edital"
    partes = []
    if cap:
        partes.append(f"{cap} capítulos")
    if q:
        partes.append(f"{q} questões comentadas")
    corpo = " e ".join(partes)
    d = f"Apostila {n['sigla']} {ANO} em PDF para {n['cargo']}" + (f": {corpo}, {edital}." if corpo else f", {edital}.")
    if len(d + " Garantia de 7 dias.") <= LIMITE_DESC:
        d += " Garantia de 7 dias."
    return d if len(d) <= LIMITE_DESC else ""


INI, FIM = "<!-- seo:inicio -->", "<!-- seo:fim -->"


def meta(html, attr, nome):
    m = re.search(rf'<meta {attr}="{re.escape(nome)}" content="([^"]*)"', html)
    return m.group(1) if m else ""


def main():
    dados = json.loads((RAIZ / "_config/produtos.json").read_text(encoding="utf-8"))
    produtos = {p["link"].strip("/"): p for p in dados["produtos"] if not p["link"].startswith("http")}
    for pasta, chave in BUSCA.items():
        arq = RAIZ / pasta / "index.html"
        if not arq.exists():
            print("falta", arq)
            continue
        html = arq.read_text(encoding="utf-8")
        p = produtos.get(pasta, {})

        n = NOMES[pasta]
        titulo = titulo_de(n)
        html = re.sub(r"<title>[^<]*</title>", f"<title>{titulo}</title>", html, count=1)
        desc = descricao_de(html, n, p)
        if desc:
            html = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + desc.replace('"', "&quot;") + m.group(2), html, count=1)
        else:
            print("AVISO descrição passou de", LIMITE_DESC, "caracteres:", pasta)

        html = html.replace('content="Curso em PDF (sem videoaulas) para',
                            'content="Apostila em PDF (curso sem videoaulas) para', 1)
        html = re.sub(r'(<p class="kicker">[^<]*?)· Curso em PDF</p>', r"\1· Apostila em PDF</p>", html, count=1)

        preco = p.get("preco", 47)
        # preço cheio: o cupom exige código, e o Google compara com o valor do checkout sem cupom
        oferta = {
            "@type": "Offer",
            "price": f"{preco:.2f}",
            "priceCurrency": "BRL",
            "availability": "https://schema.org/InStock",
            "url": BASE + pasta + "/",
            # produto digital: entrega imediata e sem frete; garantia de 7 dias da Hotmart
            "shippingDetails": {
                "@type": "OfferShippingDetails",
                "shippingRate": {"@type": "MonetaryAmount", "value": "0", "currency": "BRL"},
                "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "BR"},
                "deliveryTime": {
                    "@type": "ShippingDeliveryTime",
                    "handlingTime": {"@type": "QuantitativeValue", "minValue": 0, "maxValue": 0, "unitCode": "DAY"},
                    "transitTime": {"@type": "QuantitativeValue", "minValue": 0, "maxValue": 0, "unitCode": "DAY"},
                },
            },
            "hasMerchantReturnPolicy": {
                "@type": "MerchantReturnPolicy",
                "applicableCountry": "BR",
                "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
                "merchantReturnDays": 7,
                "returnFees": "https://schema.org/FreeReturn",
            },
        }
        ld = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": f"Apostila {n['sigla']} {ANO} em PDF: {n['cargo']}",
            "description": meta(html, "name", "description"),
            "image": meta(html, "property", "og:image"),
            "brand": {"@type": "Brand", "name": "ESCUDO Concursos"},
            "manufacturer": {"@id": BASE + "#organizacao"},
            "category": "Apostila para concurso público",
            "offers": oferta,
        }
        bloco = (f'{INI}\n<script type="application/ld+json">\n'
                 f"{json.dumps(ld, ensure_ascii=False, indent=1)}\n</script>\n{FIM}")
        if INI in html:
            html = re.sub(re.escape(INI) + r".*?" + re.escape(FIM), bloco, html, flags=re.S)
        else:
            html = html.replace("</head>", bloco + "\n</head>", 1)

        arq.write_text(html, encoding="utf-8")
        print("ok", pasta, "|", titulo)


if __name__ == "__main__":
    main()
