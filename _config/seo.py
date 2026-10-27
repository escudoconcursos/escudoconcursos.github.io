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
BASE = "https://escudoconcursos.github.io/"

BUSCA = {
    "pmpe-soldado-2026": "PMPE Soldado",
    "gm-sao-goncalo-2026": "Guarda Municipal de São Gonçalo",
    "pmal-soldado-2026": "PM/AL Soldado",
    "cbmpe-soldado-2026": "CBMPE Soldado Bombeiro",
    "pcpe-agente-2026": "PC/PE Agente de Polícia",
    "gcm-santana-2026": "GCM Santana/AP",
    "assistente-semusa-porto-velho-2026": "SEMUSA Porto Velho Assistente Administrativo",
    "tecnico-enfermagem-porto-velho-2026": "SEMUSA Porto Velho Técnico em Enfermagem",
    "professor-semed-porto-velho-2026": "SEMED Porto Velho Professor Séries Iniciais",
    "agente-educativo-aparecida-2026": "Aparecida de Goiânia Agente Educativo",
    "pedagogia-aparecida-2026": "Aparecida de Goiânia Professor PE-I Pedagogia",
    "soldado-pmsc-2026": "PM/SC Soldado",
    "escrevente-tjsp-2026": "TJSP Escrevente Técnico Judiciário",
    "assistente-administrativo-contagem-2026": "Prefeitura de Contagem Assistente Administrativo",
    "policial-penal-pr-2026": "Polícia Penal PR Policial Penal",
}

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

        titulo = f"Apostila {chave} 2026 em PDF | ESCUDO Concursos"
        html = re.sub(r"<title>[^<]*</title>", f"<title>{titulo}</title>", html, count=1)

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
            "name": f"Apostila {chave} 2026 em PDF",
            "description": meta(html, "name", "description"),
            "image": meta(html, "property", "og:image"),
            "brand": {"@type": "Brand", "name": "ESCUDO Concursos"},
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
