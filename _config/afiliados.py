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
BASE = json.loads((RAIZ / "_config/site.json").read_text(encoding="utf-8"))["url_base"]
import importlib.util as _iu
_spec = _iu.spec_from_file_location("hubs", RAIZ / "_config/hubs.py")
_HUBS = _iu.module_from_spec(_spec)
_spec.loader.exec_module(_HUBS)
GUIAS = _HUBS.guias()  # {curso: {slug do guia}}: os textos levam o link do guia e da amostra (links de fora para o site)

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
    "gcm-salvador-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/2460G108322760",
    "assistente-semusa-porto-velho-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/5835S107958655",
    "tecnico-enfermagem-porto-velho-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/5793S107958583",
    "professor-semed-porto-velho-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/7334S107961886",
    "soldado-pmsc-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/9165P108168217",
    # "escrevente-tjsp-2026": "HOTMART_RECRUTAMENTO_TJSP",  # descomentar com o link da Página de Recrutamento (ver 42-TJSP-Escrevente\apostila-escudo\hotmart\SITE-PENDENTE.md)
    "assistente-administrativo-contagem-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/2494P108214111",
    "tecnico-bancario-banestes-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/4044B108218182",
    "tecnico-defensoria-dpe-pb-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/1465D108236420",
    "investigador-policia-civil-mg-pcmg-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/2102P108238085",
    "gm-recife-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/4551G108328444",
    "soldado-pmpr-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/9752P108251402",
    "agente-administrativo-curitiba-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/1323C108255689",
    "policial-penal-pr-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/0975P108171821",
    "policial-penal-pe-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/5042P108329856",
    "pmerj-soldado-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/1601P108340512",
    "pmpa-soldado-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/2613P108343626",
    "cbm-al-soldado-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/1784C108341073",
    "pmba-soldado-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/2405P108363119",
    "pmesp-soldado-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/2366P108363041",
    "pcac-oficial-investigador-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/0008P108376060",
    "recenseador-ibge-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/1017R108378254",
    "gm-joinville-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/7895G108400713",
    "pmmg-soldado-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/4279P108409894",
    "pmmg-cfo-2027": "https://affiliate.hotmart.com/affiliate-recruiting/view/4428C108410330",
    "policial-penal-pb-2026": "https://affiliate.hotmart.com/affiliate-recruiting/view/5993P108415280",
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
            # textos prontos: pré-edital (sem inscrição e prova 2099-12-31) não mostra data
            "datas": ("Inscrições até %s, prova em %s." % (br(p["inscricoes_ate"]), br(p["prova"]))
                      if p.get("inscricoes_ate") and p.get("prova", "2099") < "2099"
                      else "Prova em %s." % br(p["prova"]) if p.get("prova", "2099") < "2099"
                      else "Pré-edital: o edital novo ainda não foi publicado."),
            "prova_txt": "Prova em %s. " % br(p["prova"]) if p.get("prova", "2099") < "2099" else "",
            "pagina": p["link"] if p["link"].startswith("http") else "../" + p["link"],
            "og": f"../assets/img/og-{p['id']}.jpg" if (RAIZ / f"assets/img/og-{p['id']}.jpg").exists() else "",
            "quadrada": "../" + p["imagem"],
            "guia": BASE + GUIAS[p["id"]]["slug"] + "/" if p["id"] in GUIAS else "",
            "amostra": BASE + p["id"] + "/amostra/" if (RAIZ / p["id"] / "amostra" / "index.html").exists() else "",
        })

    cards = []
    for c in cursos:
        e = {k: html.escape(v) for k, v in c.items()}
        artes = f'<a href="{e["quadrada"]}" download>Arte quadrada</a>'
        if c["og"]:
            artes += f' · <a href="{e["og"]}" download>Arte horizontal</a>'
        guia = ""
        if c["guia"] or c["amostra"]:
            partes = []
            if c["guia"]:
                partes.append(f'Guia do concurso: <a href="{e["guia"]}">{e["guia"]}</a>')
            if c["amostra"]:
                partes.append(f'Amostra grátis: <a href="{e["amostra"]}">{e["amostra"]}</a>')
            guia = '\n        <p class="af-guia">' + "<br>".join(partes) + "</p>"
        datas = []  # pré-edital: sem inscrição e prova 2099-12-31 (data-fantasma da vitrine)
        if c["inscricoes"]:
            datas.append(f'Inscrições até {e["inscricoes"]}')
        if c["prova"] and not c["prova"].endswith("/2099"):
            datas.append(f'prova em {e["prova"]}')
        datas = " · ".join(datas) or "Pré-edital: o edital novo ainda não foi publicado"
        cards.append(f"""      <li class="af-card">
        <p class="af-tag">{e["concurso"]} · {e["banca"]}</p>
        <h3>{e["titulo"]}</h3>
        <p class="af-datas">{datas}</p>
        <a class="btn" href="{e["recrutar"]}" rel="noopener">Quero me afiliar</a>
        <p class="af-links"><a href="{e["pagina"]}">Ver a página do curso</a> · {artes}</p>{guia}
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
