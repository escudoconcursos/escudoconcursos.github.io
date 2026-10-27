"""Gera afiliados/index.html: página "Seja afiliado" com os links de recrutamento da Hotmart,
artes para baixar e textos prontos por curso.

Rodar depois de editar produtos.json ou RECRUTAMENTO:
    PYTHONIOENCODING=utf-8 python _config/afiliados.py && PYTHONIOENCODING=utf-8 python _config/aplicar.py
Curso novo: ligar o programa de afiliados na Hotmart e pôr aqui o link de "Página de Recrutamento".
"""
import html
import json
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

RECRUTAMENTO = {
    "pmpe-soldado-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/8003P107926923",
    "gm-sao-goncalo-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/9756G107931430",
    "ufba-assistente-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/4260U107809982",
    "pmal-soldado-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/7234P107943321",
    "cbmpe-soldado-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/7209C107943270",
    "pcpe-agente-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/9694P107949904",
    "agente-educativo-aparecida-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/0383A107951762",
    "pedagogia-aparecida-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/0405A107951804",
    "gcm-santana-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/4285G107956267",
    "assistente-semusa-porto-velho-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/5835S107958655",
    "tecnico-enfermagem-porto-velho-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/5793S107958583",
    "professor-semed-porto-velho-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/7334S107961886",
    "soldado-pmsc-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/9165P108168217",
    # "escrevente-tjsp-2026": "HOTMART_RECRUTAMENTO_TJSP",  # descomentar com o link da Página de Recrutamento (ver 42-TJSP-Escrevente\apostila-escudo\hotmart\SITE-PENDENTE.md)
    "assistente-administrativo-contagem-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/2494P108214111",
    "policial-penal-pr-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/0975P108171821",
}


def br(d):
    a, m, dd = d.split("-")
    return f"{dd}/{m}/{a}"


def main():
    dados = json.loads((RAIZ / "_config/produtos.json").read_text(encoding="utf-8"))
    hoje = date.today().isoformat()
    cursos = []
    for p in sorted(dados["produtos"], key=lambda p: p.get("prova", "9")):
        if p.get("prova", "9") < hoje or p["id"] not in RECRUTAMENTO:
            continue
        concurso, _, banca = p["tag"].partition(" · ")
        cup = p.get("cupom") or {}
        cursos.append({
            "id": p["id"],
            "titulo": p["titulo"],
            "concurso": concurso,
            "banca": banca,
            "itens": ", ".join(p.get("itens", [])).lower(),
            "cupom": cup.get("codigo", ""),
            "cupom_ate": br(cup["ate"]) if cup.get("ate") else "",
            "inscricoes": br(p["inscricoes_ate"]) if p.get("inscricoes_ate") else "",
            "prova": br(p["prova"]) if p.get("prova") else "",
            "recrutar": RECRUTAMENTO[p["id"]],
            "pagina": p["link"] if p["link"].startswith("http") else "../" + p["link"],
            "og": f"../assets/img/og-{p['id']}.jpg" if (RAIZ / f"assets/img/og-{p['id']}.jpg").exists() else "",
            "quadrada": "../" + p["imagem"],
        })

    cards = []
    for c in cursos:
        e = {k: html.escape(v) for k, v in c.items()}
        artes = f'<a href="{e["quadrada"]}" download>Arte quadrada</a>'
        if c["og"]:
            artes += f' · <a href="{e["og"]}" download>Arte horizontal</a>'
        cards.append(f"""      <li class="af-card">
        <p class="af-tag">{e["concurso"]} · {e["banca"]}</p>
        <h3>{e["titulo"]}</h3>
        <p class="af-datas">Inscrições até {e["inscricoes"]} · prova em {e["prova"]}</p>
        <a class="btn" href="{e["recrutar"]}" rel="noopener">Quero me afiliar</a>
        <p class="af-links"><a href="{e["pagina"]}">Ver a página do curso</a> · {artes}</p>
      </li>""")

    pagina = (RAIZ / "_config/afiliados.modelo.html").read_text(encoding="utf-8")
    pagina = pagina.replace("<!-- cards -->", "\n".join(cards))
    pagina = pagina.replace("/*DADOS*/[]", json.dumps(cursos, ensure_ascii=False))
    destino = RAIZ / "afiliados" / "index.html"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(pagina, encoding="utf-8")
    print("ok", destino, len(cursos), "cursos")


if __name__ == "__main__":
    main()
