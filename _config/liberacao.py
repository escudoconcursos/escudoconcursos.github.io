# -*- coding: utf-8 -*-
"""Bloco "O que libera e quando" nas páginas de curso (pode rodar quantas vezes quiser).

Entra na seção da garantia, logo abaixo da caixa dos 7 dias, entre os marcadores
<!-- liberacao:inicio --> e <!-- liberacao:fim -->. Rodar de novo troca o bloco inteiro.

As regras vêm da área de membros de cada curso (MONTAGEM.md em 02-livros e a tabela
00-operacao/LIBERACOES-CURSOS.md). Mudou uma liberação na Hotmart (por exemplo o Simulado 1
passou a ser liberado na compra perto da prova)? Ajuste SIMULADO1 ou SIMULADO2 e rode:
    PYTHONIOENCODING=utf-8 python _config/liberacao.py
Curso novo: acrescentar uma linha em SIMULADO2 (e em SIMULADO1 se fugir do padrão).
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CSS_VERSAO = "21"  # versão de assets/css/escudo.css que tem o estilo .liberacao

SIMULADO1_PADRAO = "30 dias após a compra, para medir onde você está no meio da preparação."
SIMULADO1 = {  # exceções por página: "slug": "texto"
    "policial-penal-pe-2026": "na compra, para medir onde você está logo no início do estudo.",
    "pmesp-soldado-2026": "na compra, para medir onde você está logo no início do estudo.",
    "gm-campinas-2026": "na compra, para medir onde você está logo no início do estudo.",
    "pmmg-cfo-2027": "8 dias após a compra, porque a prova está a poucas semanas.",
    "agente-administrativo-curitiba-2026": "na compra, porque faltam poucas semanas para a prova e você já pode medir onde está.",
}

SIMULADO2 = {
    "pmpe-soldado-2026": "em 14/02/2027, 7 dias antes da prova, para o último teste.",
    "gm-sao-goncalo-2026": "em 17/01/2027, 7 dias antes da prova, para o último teste.",
    "pmal-soldado-2026": "em 10/01/2027, 7 dias antes da prova, para o último teste.",
    "cbmpe-soldado-2026": "em 21/02/2027, 7 dias antes da prova, para o último teste.",
    "pcpe-agente-2026": "em 28/02/2027, 7 dias antes da prova, para o último teste.",
    "agente-educativo-aparecida-2026": "em 24/01/2027, 7 dias antes da prova, para o último teste.",
    "pedagogia-aparecida-2026": "em 24/01/2027, 7 dias antes da prova, para o último teste.",
    "gcm-santana-2026": "em 10/01/2027, 7 dias antes da prova, para o último teste.",
    "gcm-salvador-2026": "em 10/01/2027, 7 dias antes da prova, para o último teste.",
    "gm-recife-2026": "60 dias após a compra, porque ainda não há data de prova marcada.",
    "assistente-semusa-porto-velho-2026": "em 06/12/2026, 7 dias antes da prova, para o último teste.",
    "tecnico-enfermagem-porto-velho-2026": "em 06/12/2026, 7 dias antes da prova, para o último teste.",
    "professor-semed-porto-velho-2026": "em 29/11/2026, 7 dias antes da prova, para o último teste.",
    "soldado-pmsc-2026": "em 06/12/2026, 7 dias antes da prova, para o último teste.",
    "escrevente-tjsp-2026": "em 07/03/2027, 7 dias antes da prova, para o último teste.",
    "assistente-administrativo-contagem-2026": "em 17/01/2027, 7 dias antes da prova, para o último teste.",
    "agente-administrativo-curitiba-2026": "em 06/12/2026, 7 dias antes da prova, para o último teste.",
    "tecnico-bancario-banestes-2026": "em 17/01/2027, 7 dias antes da prova, para o último teste.",
    "tecnico-defensoria-dpe-pb-2026": "em 21/02/2027, 7 dias antes da prova, para o último teste.",
    "policial-penal-pe-2026": "em 14/03/2027, 7 dias antes da prova, para o último teste.",
    "policial-penal-pr-2026": "60 dias após a compra, porque ainda não há data de prova marcada.",
    "pmerj-soldado-2026": "60 dias após a compra, porque ainda não há data de prova marcada.",
    "pmpa-soldado-2026": "60 dias após a compra, porque ainda não há data de prova marcada.",
    "cbm-al-soldado-2026": "em 17/01/2027, 7 dias antes da prova, para o último teste.",
    "pmba-soldado-2026": "60 dias após a compra, porque ainda não há data de prova marcada.",
    "pmesp-soldado-2026": "em 21/02/2027, 7 dias antes da prova, para o último teste.",
    "gm-campinas-2026": "em 14/03/2027, 7 dias antes da prova, para o último teste.",
    "pcac-oficial-investigador-2026": "em 17/01/2027, 7 dias antes da prova, para o último teste.",
    "gm-joinville-2026": "60 dias após a compra, porque ainda não há data de prova marcada.",
    "gm-balneario-camboriu-2026": "60 dias após a compra, porque ainda não há data de prova marcada.",
    "pmmg-cfo-2027": "em 03/01/2027, 7 dias antes da prova, para o último teste.",
    "pmmg-soldado-2026": "60 dias após a compra, porque ainda não há data de prova marcada.",
    "policial-penal-pb-2026": "60 dias após a compra, porque ainda não há data de prova marcada.",
    "pmac-soldado-2026": "60 dias após a compra, porque ainda não há data de prova marcada.",
    "cbmes-soldado-2026": "60 dias após a compra, porque ainda não há data de prova marcada.",
    "pcto-oficial-investigador-2026": "60 dias após a compra, porque ainda não há data de prova marcada.",
    "pcpa-investigador-2026": "60 dias após a compra, porque ainda não há data de prova marcada.",
    "pcpa-escrivao-2026": "60 dias após a compra, porque ainda não há data de prova marcada.",
    "detranpr-agente-2026": "60 dias após a compra, porque ainda não há data de prova marcada.",
    "pmrr-soldado-2026": "60 dias após a compra, porque ainda não há data de prova marcada.",
    "recenseador-ibge-2026": "em 24/01/2027, 7 dias antes da prova, para o último teste.",
}

INI, FIM = "<!-- liberacao:inicio -->", "<!-- liberacao:fim -->"
ICONE_OK = '<svg aria-hidden="true"><use href="#i-check"/></svg>'
ICONE_DATA = '<svg aria-hidden="true"><use href="#i-cal"/></svg>'


def bloco(slug, policial):
    etq = '      <p class="etq"><span>Cronograma</span></p>\n' if policial else ""
    s1 = SIMULADO1.get(slug, SIMULADO1_PADRAO)
    s2 = SIMULADO2[slug]
    return (
        f"    {INI}\n"
        '    <div class="liberacao">\n'
        f"{etq}"
        '      <p class="kicker">Sem surpresa na área de membros</p>\n'
        '      <h2 id="t-liberacao">O que libera <em>e quando</em></h2>\n'
        '      <hr class="regua">\n'
        '      <ul class="entregas">\n'
        f"        <li>{ICONE_OK}<p><strong>Na compra:</strong> todas as disciplinas em PDF, uma por módulo, com a teoria e as questões comentadas. É o curso inteiro, para começar a estudar no mesmo dia.</p></li>\n"
        f"        <li>{ICONE_DATA}<p><strong>8 dias após a compra:</strong> o PDF completo para imprimir. É o mesmo conteúdo dos módulos num arquivo só, liberado depois da garantia de 7 dias.</p></li>\n"
        f"        <li>{ICONE_DATA}<p><strong>Simulado 1:</strong> {s1}</p></li>\n"
        f"        <li>{ICONE_DATA}<p><strong>Simulado 2:</strong> {s2}</p></li>\n"
        "      </ul>\n"
        '      <p class="intro">O PDF completo e os simulados aparecem bloqueados na área de membros até a data de cada um: não é conteúdo faltando, é a liberação programada.</p>\n'
        "    </div>\n"
        f"    {FIM}\n"
    )


def main():
    for slug in SIMULADO2:
        arq = RAIZ / slug / "index.html"
        bruto = arq.read_bytes().decode("utf-8")
        crlf = "\r\n" in bruto
        html = bruto.replace("\r\n", "\n")
        # tira o bloco antigo, se houver
        html = re.sub(r"[ \t]*" + re.escape(INI) + r".*?" + re.escape(FIM) + r"\n", "", html, flags=re.S)
        sec = re.search(r'<section class="secao creme" aria-labelledby="t-garantia">.*?\n  </div>\n</section>', html, flags=re.S)
        if not sec:
            print("SEM SEÇÃO DE GARANTIA:", slug)
            continue
        fim_wrap = sec.end() - len("  </div>\n</section>")
        html = html[:fim_wrap] + bloco(slug, "policial.css" in html) + html[fim_wrap:]
        html = re.sub(r'(assets/css/escudo\.css\?v=)\d+', r"\g<1>" + CSS_VERSAO, html, count=1)
        if crlf:
            html = html.replace("\n", "\r\n")
        arq.write_bytes(html.encode("utf-8"))
        print("ok", slug)


if __name__ == "__main__":
    main()
