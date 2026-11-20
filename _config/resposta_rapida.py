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
    "gm-sao-goncalo-2026": {
        "nome": "GM São Gonçalo Guarda Municipal",
        "quando": "A prova objetiva do concurso da Guarda Municipal de São Gonçalo/RJ é em 24/01/2027, de manhã, aplicada pelo Instituto SELECON (Edital nº 001/PMSG/2026), em São Gonçalo, Niterói ou Rio de Janeiro, conforme a escolha feita na inscrição.",
        "vagas": "São 100 vagas imediatas (95 de ampla concorrência e 5 para pessoas com deficiência) e 500 de cadastro de reserva para Guarda Municipal Nível II, com vencimento de R$ 3.172,96, ensino médio e CNH AB, cobrada só na posse.",
        "prova": "São 80 questões de múltipla escolha com quatro alternativas, de A a D, somando 100 pontos: 15 de Português, 20 de Noções de Direito, 15 de Legislação Extravagante, 10 de Informática e 20 de Conhecimentos Específicos, que valem 2 pontos cada (40% da nota). É preciso fazer 50 pontos e não zerar nenhuma disciplina.",
        "curso": "131 capítulos, 650 questões comentadas e 2 simulados de 80 questões",
    },
    "soldado-pmsc-2026": {
        "nome": "PM/SC Soldado",
        "quando": "A prova objetiva e a redação do concurso de Soldado da PM de Santa Catarina são em 13/12/2026, no mesmo dia, aplicadas pelo Instituto AOCP (Edital nº 002/CCP/2026).",
        "vagas": "São 500 vagas para Soldado, todas de ampla concorrência, com remuneração de R$ 8.505,00 mais R$ 550,00 de auxílio-alimentação. Exige nível superior em qualquer área.",
        "prova": "A objetiva tem 60 questões de múltipla escolha com cinco alternativas, de A a E: 26 de Direito, 21 de Legislação e 13 de Conhecimentos Comuns (Português e Informática). É preciso fazer 30 pontos e não zerar nenhuma das três áreas. A redação vale 20 pontos, exige no mínimo 10 e o tema sai de Ordem Pública.",
        "curso": "165 capítulos, 790 questões comentadas, redação e 2 simulados",
    },
    "recenseador-ibge-2026": {
        "nome": "IBGE Recenseador",
        "quando": "A prova objetiva do processo seletivo de Recenseador do IBGE para o 12º Censo Agropecuário é em 31/01/2027, das 13h às 17h, aplicada pela Fundação Cesgranrio (Edital nº 03/2026). As inscrições vão até 25/11/2026.",
        "vagas": "São 27.279 vagas temporárias, com exigência de ensino fundamental completo, parcela fixa de R$ 1.741,00 e parcela variável por produção de até R$ 2.629,00, além de auxílio-alimentação de R$ 1.192,00.",
        "prova": "São 60 questões de múltipla escolha com cinco alternativas, de A a E: 15 de Português, 15 de Matemática e 30 de Conhecimentos Técnicos, tirados da apostila oficial do Censo Agro. É preciso fazer 18 pontos e acertar pelo menos 1 questão em cada disciplina.",
        "curso": "75 capítulos, 370 questões comentadas e 2 simulados de 60 questões",
    },
    "pmesp-soldado-2026": {
        "nome": "PM/SP Soldado",
        "quando": "A prova objetiva e a redação do concurso de Aluno-Soldado da PM de São Paulo estão previstas para 28/02/2027, à tarde, aplicadas pela Fundação VUNESP (Edital nº DP-4/321/26). As inscrições vão até 22/12/2026.",
        "vagas": "São 2.000 cargos de Aluno-Soldado PM, com remuneração básica inicial de R$ 5.482,51, ensino médio e idade de 17 a 30 anos.",
        "prova": "A objetiva tem 60 questões de múltipla escolha com cinco alternativas, de A a E: 20 de Português, 15 de Matemática, 15 de Conhecimentos Gerais, 5 de Informática e 5 de Administração Pública. É preciso fazer 30 pontos, sem nota mínima por disciplina, e há redação no mesmo dia.",
        "curso": "75 capítulos, 345 questões comentadas e 2 simulados de 60 questões",
    },
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
    "pcpe-escrivao-2026": {
        "nome": "PC-PE Escrivão de Polícia Civil",
        "quando": "As provas objetivas e a redação do concurso de Escrivão de Polícia da PC-PE são em 07/03/2027, de manhã, aplicadas pelo Cebraspe (Edital nº 1 PCPE, de 2 de outubro de 2026).",
        "vagas": "São 70 vagas para Escrivão de Polícia, com remuneração de R$ 5.667,92.",
        "prova": "A prova objetiva tem 60 questões de múltipla escolha com cinco alternativas, de A a E, sem desconto por resposta errada, e há uma redação de 30 pontos. Só o Escrivão tem ainda a prova prática de digitação, depois da investigação social.",
        "curso": "145 capítulos, 695 questões comentadas, 2 simulados e redação",
    },
    "gm-pedra-branca-do-amapari-2026": {
        "nome": "GM Pedra Branca do Amapari Guarda Municipal",
        "quando": "A prova objetiva do concurso da Guarda Municipal de Pedra Branca do Amapari é em 31/01/2027, à tarde, aplicada pelo Instituto Nazaré (Edital nº 01/2026, de 5 de novembro de 2026). As inscrições vão até 23/12/2026.",
        "vagas": "São 45 vagas: 28 de ampla concorrência, 2 para pessoas com deficiência e 15 de cadastro de reserva, com vencimento-base de R$ 1.972,19, nível médio e jornada de 40 horas semanais.",
        "prova": "A prova objetiva tem 60 questões de múltipla escolha com cinco alternativas, de A a E, com peso: Conhecimentos Específicos e Legislação valem 60 dos 100 pontos. É preciso fazer o mínimo em cada disciplina e pelo menos 50 pontos no total.",
        "curso": "123 capítulos, 610 questões comentadas e 2 simulados de 60 questões",
    },
    "professor-seduc-sp-2026": {
        "nome": "SEDUC/SP Professor Gestão de Sala de Aula, Discursiva e Prova Prática",
        "quando": "A Prova Objetiva e a Prova Discursiva do concurso de Professor de Ensino Fundamental e Médio da SEDUC/SP estão previstas para 25/04/2027, aplicadas pela FGV (Edital nº 01/2026, publicado em 19/11/2026). As inscrições vão das 16h de 26/11/2026 às 16h de 15/02/2027, e o vídeo da Prova Prática é enviado de 19/03 a 02/04/2027.",
        "vagas": "São 5.000 vagas efetivas de Professor de Ensino Fundamental e Médio, 2.000 de 25 horas semanais (subsídio de R$ 3.478,13) e 3.000 de 40 horas (R$ 5.565,00), mais a lista de contratação temporária (PSS). A taxa de inscrição é de R$ 64,00.",
        "prova": "São 100 pontos: Prova Objetiva (30 questões de A a E, 10 de Gestão de Sala de Aula e 20 de Conhecimentos Específicos, mínimo de 15 pontos), Prova Discursiva (2 questões de até 20 linhas, 20 pontos, mínimo de 10), Prova Prática de Simulação de Aula em vídeo de 5 a 7 minutos (30 pontos, mínimo de 15) e Títulos (20 pontos). O curso cobre as 10 questões de Gestão de Sala de Aula e o método da discursiva e do vídeo, mas não as 20 de Específicos.",
        "curso": "34 capítulos, 155 questões comentadas e 2 simulados de 10 questões com proposta de Prova Discursiva",
    },
    "professor-seduc-ma-2026": {
        "nome": "SEDUC/MA Professor Conhecimentos Gerais e Redação",
        "quando": "A prova objetiva e a redação do Concurso Público Unificado do Maranhão são em 04/04/2027, aplicadas pela FCC (Edital nº 01/2026, de 17 de novembro de 2026). As inscrições vão de 14/12/2026 a 29/01/2027.",
        "vagas": "São 2.000 vagas imediatas de Professor da SEDUC em 17 áreas de atuação, com vencimento de R$ 3.836,25 e jornada de 40 horas semanais. A Supervisão Escolar tem mais 170 vagas e faz a mesma prova de Conhecimentos Gerais. A taxa de inscrição é de R$ 120,00.",
        "prova": "A prova objetiva tem 20 questões de Conhecimentos Gerais (peso 1) e 30 de Conhecimentos Específicos (peso 2), todas de múltipla escolha com cinco alternativas, de A a E, mais uma redação de 20 a 30 linhas. É preciso nota 6,00 para ser habilitado. O curso cobre os Conhecimentos Gerais e a redação, mas não os 30 Específicos de cada área.",
        "curso": "84 capítulos, 405 questões comentadas, redação e 2 simulados de 40 questões de Conhecimentos Gerais",
    },
    "assistente-tecnico-sead-ma-2026": {
        "nome": "SEAD/MA Assistente Técnico Administração",
        "quando": "A prova objetiva é em 04/04/2027, aplicada pela FCC (Edital de Abertura nº 01/2026, de 17 de novembro de 2026, publicado em 18/11/2026), em Balsas, Barra do Corda, Caxias, Colinas, Imperatriz, Pinheiro e São Luís. As inscrições vão de 14/12/2026 a 29/01/2027, só pela internet, com taxa de R$ 60,00 (DARE pago até 01/02/2027).",
        "vagas": "São 91 vagas de Assistente Técnico na SEAD, em oito especialidades, e 30 delas são de Assistente de Administração (mais o cadastro de reserva), com vencimento inicial de R$ 1.631,76 e carga horária de 30 horas. O requisito, segundo o edital, é o certificado de curso técnico de nível médio e a habilitação legal específica (item 2.1.2).",
        "prova": "A prova objetiva tem 50 questões de múltipla escolha com cinco alternativas, de A a E, e dura 3 horas: 20 de Conhecimentos Gerais (peso 1) e 30 de Conhecimentos Específicos (peso 2). A nota é a média ponderada, de 0 a 10, e é preciso tirar 6,00 ou mais. Não há prova discursiva para o nível médio.",
        "curso": "129 capítulos e 640 questões comentadas",
    },
    "professor-lingua-portuguesa-seduc-ma-2026": {
        "nome": "SEDUC/MA Professor de Língua Portuguesa prova completa",
        "quando": "A prova objetiva e a redação do Concurso Público Unificado do Maranhão são em 04/04/2027, aplicadas pela FCC (Edital nº 01/2026, de 17 de novembro de 2026). As inscrições vão de 14/12/2026 a 29/01/2027.",
        "vagas": "São 291 vagas imediatas de Professor de Língua Portuguesa da SEDUC, com vencimento de R$ 3.836,25 e jornada de 40 horas semanais, mais cadastro de reserva. A taxa de inscrição é de R$ 120,00.",
        "prova": "A prova objetiva tem 20 questões de Conhecimentos Gerais (peso 1) e 30 de Conhecimentos Específicos (peso 2), todas de múltipla escolha com cinco alternativas, de A a E, mais uma redação de 20 a 30 linhas. É preciso nota 6,00 para ser habilitado. O curso cobre a prova inteira do cargo: os Gerais, os Específicos de Língua Portuguesa e a redação.",
        "curso": "114 capítulos, 555 questões comentadas, redação e 2 simulados da prova inteira (50 questões e proposta de redação)",
    },
    "professor-matematica-seduc-ma-2026": {
        "nome": "SEDUC/MA Professor de Matemática prova completa",
        "quando": "A prova objetiva e a redação do Concurso Público Unificado do Maranhão são em 04/04/2027, aplicadas pela FCC (Edital nº 01/2026, de 17 de novembro de 2026). As inscrições vão de 14/12/2026 a 29/01/2027.",
        "vagas": "São 277 vagas imediatas de Professor de Matemática da SEDUC (cargo 23), com vencimento de R$ 3.836,25 e jornada de 40 horas semanais. A taxa de inscrição é de R$ 120,00.",
        "prova": "A prova objetiva tem 20 questões de Conhecimentos Gerais (peso 1) e 30 de Conhecimentos Específicos (peso 2), todas de múltipla escolha com cinco alternativas, de A a E, mais uma redação de 20 a 30 linhas. É preciso nota 6,00 para ser habilitado. O Professor de Matemática não faz Matemática e Raciocínio Lógico nos Gerais, porque a Matemática vem nos Específicos. O curso cobre as três partes: Gerais, Específicos e redação.",
        "curso": "110 capítulos, 535 questões comentadas, redação e 2 simulados de 50 questões",
    },
    "supervisao-escolar-seduc-ma-2026": {
        "nome": "SEDUC/MA Supervisão Escolar prova completa",
        "quando": "A prova objetiva e a redação do Concurso Público Unificado do Maranhão são em 04/04/2027, aplicadas pela FCC (Edital nº 01/2026, de 17 de novembro de 2026). As inscrições vão de 14/12/2026 a 29/01/2027.",
        "vagas": "São 170 vagas imediatas de Especialista em Educação: Supervisão Escolar (cargo 10) na SEDUC, com vencimento de R$ 1.918,12 e jornada de 40 horas semanais. A taxa de inscrição é de R$ 120,00.",
        "prova": "A prova objetiva tem 20 questões de Conhecimentos Gerais (peso 1) e 30 de Conhecimentos Específicos (peso 2), todas de múltipla escolha com cinco alternativas, de A a E, mais uma redação de 20 a 30 linhas. É preciso nota 6,00 para ser habilitado. O curso cobre a prova inteira, seguindo o programa publicado no edital.",
        "curso": "121 capítulos, 590 questões comentadas, redação e 2 simulados de 50 questões, com proposta de redação",
    },
    "gcm-angra-dos-reis-2026": {
        "nome": "GCM Angra dos Reis Guarda Civil Municipal",
        "quando": "A prova objetiva e a redação do concurso da Guarda Civil Municipal de Angra dos Reis são em 24/01/2027, à tarde, aplicadas pelo IDIB (Edital nº 01/2026, de 18 de novembro de 2026). As inscrições vão até 21/12/2026.",
        "vagas": "São 200 vagas e 250 de cadastro de reserva, com vencimento de R$ 3.872,27 mais 30% de adicional de periculosidade, nível médio com CNH categoria AB e jornada de 40 horas semanais no edital.",
        "prova": "A prova objetiva tem 60 questões de múltipla escolha com cinco alternativas, de A a E, e vale 80 pontos, com peso 2 nos Conhecimentos Específicos. É preciso fazer 50% dos pontos, 1 ponto em cada disciplina dos Conhecimentos Gerais e 2 nos Específicos. A redação vale de 0 a 30 pontos.",
        "curso": "102 capítulos, 490 questões comentadas, redação e 2 simulados de 60 questões",
    },
    "gm-maraba-2026": {
        "nome": "GCM Marabá Guarda Municipal",
        "quando": "A prova objetiva do concurso da Guarda Municipal de Marabá é em 24/01/2027, de manhã, aplicada pela Fadesp (Edital nº 01/2026 GMM, de 11 de novembro de 2026). As inscrições vão de 17/11 a 28/12/2026.",
        "vagas": "São 127 vagas: 60 imediatas e 67 de cadastro reserva, com salário-base de R$ 2.076,40 mais vantagens, nível médio e CNH categoria AB.",
        "prova": "A prova objetiva tem 40 questões de múltipla escolha com cinco alternativas, de A a E, com peso: Conhecimentos Específicos valem 60 dos 100 pontos e Conhecimentos do Município de Marabá, 20. É preciso fazer pelo menos 60 pontos.",
        "curso": "101 capítulos, 500 questões comentadas e 2 simulados de 40 questões",
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
        # guias /concurso-*/ e posts já trazem o próprio FAQPage (guias.py, blog.py): não duplicar (20/11/2026)
        if faq and "</head>" in txt and '"FAQPage"' not in txt:
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
