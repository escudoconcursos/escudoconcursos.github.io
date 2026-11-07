"""Resposta rápida no topo das páginas dos cursos que mais vendem e FAQPage em todas as páginas.

Rodar depois de editar uma página de produto ou o dicionário RAPIDAS abaixo:
    python -I -X utf8 _config/resposta_rapida.py

Idempotente. Faz duas coisas:
1. Nas páginas listadas em RAPIDAS, põe logo depois do hero um bloco com 3 perguntas e respostas curtas
   (quando é a prova, vagas e salário, como é a prova), entre <!-- resposta-rapida:inicio --> e :fim -->.
2. Em toda página que tem <div class="faq">, grava o FAQPage em JSON-LD (as perguntas do bloco rápido
   mais as do FAQ de baixo), entre <!-- faq-ld:inicio --> e :fim --> antes de </head>.
Por quê: buscadores de IA (ChatGPT já traz cerca de 21% das vendas rastreadas) citam pergunta e resposta curtas.
Os fatos vêm do edital e das fichas em 02-livros; ao mudar data, vagas ou corte, edite aqui e rode de novo.
"""
import html
import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

RAPIDAS = {
    "escrevente-tjsp-2026": {
        "nome": "TJSP Escrevente Técnico Judiciário",
        "quando": "A prova objetiva e a redação do concurso de Escrevente Técnico Judiciário do TJSP são em 14/03/2027, à tarde, aplicadas pela Vunesp (Edital nº 02/2026).",
        "vagas": "É cadastro de reserva, da 2ª à 10ª RAJ, com remuneração de R$ 6.782,54 e exigência de ensino médio.",
        "prova": "A objetiva tem 70 questões de múltipla escolha com cinco alternativas, de A a E, mais redação de 0 a 40 pontos. É preciso acertar pelo menos 8 das 16 questões de Português e 15 das 30 de Direito, e a nota final mínima é 5 (35 acertos).",
        "curso": "87 capítulos, 430 questões comentadas e 2 simulados com redação",
    },
    "tecnico-bancario-banestes-2026": {
        "nome": "Banestes Técnico Bancário",
        "quando": "A prova objetiva do concurso do Banestes para Técnico Bancário é em 24/01/2027, no domingo de manhã, aplicada pela FCC (Edital nº 01/2026). As inscrições vão até 23/11/2026.",
        "vagas": "São 866 postos de cadastro de reserva, com remuneração de R$ 4.552,43 por 30 horas semanais e exigência de ensino médio.",
        "prova": "São 70 questões de múltipla escolha com cinco alternativas, de A a E: 30 de Conhecimentos Gerais (peso 1) e 40 de Específicos (peso 2). A nota final é (Gerais + 2 x Específicos) dividido por 3, e a média mínima é 6,00, sem nota mínima por disciplina.",
        "curso": "139 capítulos, 690 questões comentadas e 2 simulados",
    },
    "agente-administrativo-curitiba-2026": {
        "nome": "Prefeitura de Curitiba Agente Administrativo",
        "quando": "A prova objetiva do concurso de Agente Administrativo da Prefeitura de Curitiba é em 13/12/2026, em fase única, aplicada pela Fundação FAFIPA (Edital Normativo nº 4/2026).",
        "vagas": "São 250 vagas mais cadastro de reserva, com vencimento de R$ 3.027,73 e exigência de ensino médio.",
        "prova": "São 40 questões de múltipla escolha com cinco alternativas, de A a E, cada uma valendo 2,50 pontos: 5 de Português, 5 de Raciocínio Lógico, 5 de Informática, 5 de Legislação e 20 de Conhecimentos Específicos. É preciso fazer 60 dos 100 pontos, ou seja, 24 acertos, sem nota mínima por área. Não há redação nem prova física.",
        "curso": "186 capítulos, 930 questões comentadas e 2 simulados",
    },
    "pcpe-agente-2026": {
        "nome": "PC-PE Agente de Polícia Civil",
        "quando": "As provas objetivas e a redação do concurso de Agente de Polícia da PC-PE são em 07/03/2027, aplicadas pelo Cebraspe (Edital nº 1 PCPE, de 2 de outubro de 2026).",
        "vagas": "São 1.200 vagas para Agente de Polícia, com remuneração de R$ 5.667,92.",
        "prova": "A prova objetiva tem 60 questões de múltipla escolha com cinco alternativas, de A a E, sem desconto por resposta errada, e há uma redação de 30 pontos.",
        "curso": "139 capítulos, 665 questões comentadas, 2 simulados e redação",
    },
    "agente-educativo-aparecida-2026": {
        "nome": "Aparecida de Goiânia Agente Educativo",
        "quando": "A prova objetiva do concurso de Agente Educativo de Aparecida de Goiânia é em 31/01/2027, de manhã (Edital de Abertura nº 01/2026).",
        "vagas": "São 1.663 vagas imediatas e 8.315 de cadastro de reserva, com vencimento de R$ 3.070,76.",
        "prova": "São 40 questões de múltipla escolha com quatro alternativas, de A a D, sem desconto por resposta errada e sem redação para Agente Educativo.",
        "curso": "81 capítulos, 400 questões comentadas e 2 simulados",
    },
    "pmpe-soldado-2026": {
        "nome": "PMPE Soldado",
        "quando": "A prova objetiva e a redação do concurso de Soldado da PM de Pernambuco são em 21/02/2027, aplicadas pelo Instituto AOCP (Edital 001/2026).",
        "vagas": "São 1.250 vagas para Soldado, com soldo de R$ 5.617,92.",
        "prova": "A prova objetiva tem 60 questões de múltipla escolha com cinco alternativas, de A a E, e a redação vale 40 dos 100 pontos.",
        "curso": "116 capítulos, 550 questões comentadas, 2 simulados e redação",
    },
    "cbmpe-soldado-2026": {
        "nome": "CBMPE Soldado Bombeiro",
        "quando": "A prova objetiva e a redação do concurso de Soldado dos Bombeiros de Pernambuco são em 28/02/2027, aplicadas pelo Instituto AOCP (Edital nº 002/2026).",
        "vagas": "São 510 vagas para Soldado, com soldo de R$ 5.617,92.",
        "prova": "A prova objetiva tem 60 questões de múltipla escolha com cinco alternativas, de A a E, e a redação vale 40 dos 100 pontos. O programa inclui Matemática, Física e Biologia.",
        "curso": "142 capítulos, 680 questões comentadas, 2 simulados e redação",
    },
}

INI_R, FIM_R = "<!-- resposta-rapida:inicio -->", "<!-- resposta-rapida:fim -->"
INI_L, FIM_L = "<!-- faq-ld:inicio -->", "<!-- faq-ld:fim -->"
ANCORA = "<!-- O CONCURSO -->"


def esc(t):
    return html.escape(t, quote=False)


def perguntas_rapidas(d):
    n = d["nome"]
    return [
        (f"Quando é a prova do concurso {n}?", d["quando"]),
        (f"Quantas vagas e qual o salário no concurso {n}?", d["vagas"]),
        (f"Como é a prova do concurso {n} e como me preparo?",
         d["prova"] + f" O curso em PDF da ESCUDO segue o edital item por item, com {d['curso']}, e tem 7 dias de garantia pela Hotmart."),
    ]


def bloco_rapido(d):
    itens = "\n".join(
        f'      <details open><summary>{esc(q)}</summary><p>{esc(a)}</p></details>'
        for q, a in perguntas_rapidas(d)
    )
    return (
        f"{INI_R}\n"
        '<section class="secao claro" aria-labelledby="t-rapida">\n'
        '  <div class="wrap">\n'
        '    <p class="kicker">Resposta rápida</p>\n'
        f'    <h2 id="t-rapida">O essencial sobre o <em>concurso</em></h2>\n'
        '    <hr class="regua">\n'
        '    <div class="faq">\n'
        f"{itens}\n"
        "    </div>\n"
        "  </div>\n"
        "</section>\n\n"
        f"{FIM_R}\n\n"
    )


def tira_tags(t):
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()


def main():
    feitas_r = feitas_l = 0
    for pagina in sorted(RAIZ.glob("*/index.html")):
        pasta = pagina.parent.name
        txt = pagina.read_text(encoding="utf-8")
        orig = txt

        # 1. bloco de resposta rápida
        txt = re.sub(re.escape(INI_R) + r".*?" + re.escape(FIM_R) + r"\n\n", "", txt, flags=re.S)
        if pasta in RAPIDAS:
            if ANCORA not in txt:
                print("sem âncora:", pasta)
            else:
                txt = txt.replace(ANCORA, bloco_rapido(RAPIDAS[pasta]) + ANCORA, 1)
                feitas_r += 1

        # 2. FAQPage em JSON-LD com todas as perguntas da página
        txt = re.sub(r"\n?" + re.escape(INI_L) + r".*?" + re.escape(FIM_L), "", txt, flags=re.S)
        faq = re.findall(r"<details(?: open)?><summary>(.*?)</summary><p>(.*?)</p></details>", txt, re.S)
        if faq and "</head>" in txt:
            ld = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": tira_tags(q),
                     "acceptedAnswer": {"@type": "Answer", "text": tira_tags(a)}}
                    for q, a in faq
                ],
            }
            script = f'{INI_L}\n<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n{FIM_L}'
            txt = txt.replace("</head>", script + "\n</head>", 1)
            feitas_l += 1

        if txt != orig:
            pagina.write_text(txt, encoding="utf-8")
    print(f"resposta rápida em {feitas_r} páginas, FAQPage em {feitas_l} páginas")


if __name__ == "__main__":
    main()
