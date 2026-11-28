# Fila de pedidos de indexação no Google (Search Console)

Usada pela tarefa agendada "Indexação diária ESCUDO" (todo dia às 9h). Cota do Google: cerca de 10 pedidos por dia (em 20/11/2026 a cota acabou no 11º).
Quem cria página nova no site (guia, curso, post importante) acrescenta o endereço em "Na fila". Desde 21/11/2026 a tarefa inspeciona a fila e só gasta pedido com o que ainda NÃO está no Google; o que já está indexado sai da fila para "Já estavam no Google (sem pedido)". Os pedidos que sobram vão para as páginas "Detectada" e "Rastreada, mas não indexada" do relatório.

## Reindexar (título novo)

<!-- 23/11/2026: páginas JÁ indexadas cujo título e descrição foram reescritos para subir o CTR (estavam com prazo vencido ou sem a data da prova). Pedir MESMO estando no Google, até 3 por dia, antes da fila; depois do pedido, tirar daqui. -->

<!-- 28/11/2026: guias com muita impressão e CTR baixo (Search Console 19 a 25/11) ganharam título com "Guarda Municipal" e outras palavras da busca. Com "Na fila" vazia, pode usar até 7 pedidos do dia aqui. -->
- https://escudoconcursos.com.br/concurso-gcm-angra-dos-reis/
- https://escudoconcursos.com.br/concurso-gcm-salvador/
- https://escudoconcursos.com.br/concurso-pc-mg/
- https://escudoconcursos.com.br/concurso-gm-campinas/
- https://escudoconcursos.com.br/concurso-cfo-pmmg/
- https://escudoconcursos.com.br/concurso-gcm-santana/
- https://escudoconcursos.com.br/concurso-banestes/

## Na fila


## Pedidos feitos

- 20/11/2026: https://escudoconcursos.com.br/ , /noticias/pcpe-agente-isencao-ate-12-11/ , /concurso-banestes/ , /concurso-gm-sao-goncalo/ , /concurso-pc-ac/ , /concurso-dpe-pb/ , /concurso-gcm-salvador/ , /concurso-gm-recife/ , /concurso-gcm-santana/ , /cbm-al-soldado-2026/ , /concurso-cfo-pmmg/
- 21/11/2026: /concurso-gcm-angra-dos-reis/ , /concurso-gm-maraba/ , /concurso-gm-pedra-branca-do-amapari/ , /concurso-trt4-tecnico/ , /concurso-cadete-cbmerj/ , /concurso-cbm-es/ , /concurso-cfo-pmerj/ , /concurso-detran-pr/ , /concurso-gm-balneario-camboriu/ , /concurso-gm-campinas/ (todas já estavam no Google; Marabá foi pedido duas vezes porque a aba fechou no meio; a cota não acabou)
- 22/11/2026 (rodada das 19h30): /concurso-dpe-am-assistente/ (fila) , /concurso-inss-tecnico/ (fila) , /pmpe-soldado-2026/ (fila) , /pcpe-escrivao-2026/ (fila) , /gm-recife-2026/ (fila) , /pmerj-soldado-2026/ (fila) , /pmpa-soldado-2026/ (fila) , /soldado-pmpr-2026/ (fila) , /policial-penal-pe-2026/ (fila) , /policial-penal-pb-2026/ (fila). Todas "O URL não está no Google". O 1º pedido (DPE-AM) deu "Ops... algo deu errado" e passou na 2ª tentativa. Parou em 10 pelo limite da tarefa, sem aviso de cota excedida.
- 23/11/2026 (rodada das 13h28): nenhum pedido. O Chrome estava aberto, mas a extensão Claude in Chrome não conectou (3 tentativas, nenhum navegador ligado à conta). A fila ficou intacta para a próxima rodada.
- 23/11/2026 (2ª tentativa, 14h18): a extensão conectou. /investigador-policia-civil-mg-pcmg-2026/ inspecionada ("O URL não está no Google"), mas o pedido deu "A cota foi excedida" já no 1º clique; provavelmente os 10 pedidos da rodada de 22/11 às 19h30 ainda contam na cota (não confirmado). Nenhum pedido feito; a fila continua inteira. Rodar a próxima depois das 19h30 ou só amanhã.
- 23/11/2026 (16h45, frente do site): /investigador-policia-civil-mg-pcmg-2026/ inspecionada de novo ("O URL não está no Google") e o pedido deu "A cota foi excedida" outra vez. Sitemap reenviado no Search Console e IndexNow mandado (200, 210 URLs). Relatório de páginas ainda é o de 21/11 (28 detectadas, 12 rastreadas). Criada a seção Reindexar (título novo).
- 24/11/2026 (rodada das 13h25): /concurso-semed-porto-velho/ (reindexar) , /concurso-aparecida-de-goiania-educacao/ (reindexar) , /noticias/gm-sao-goncalo-inscricoes-ate-18-11/ (reindexar) , /investigador-policia-civil-mg-pcmg-2026/ (fila) , /pcac-oficial-investigador-2026/ (fila) , /pcpa-escrivao-2026/ (fila) , /seedf-pedagogia-2026/ (fila) , /cbmes-soldado-2026/ (fila) , /pmmg-cfo-2027/ (fila) , /concurso-pc-pe/ (fila). As 3 de reindexar estavam no Google; as 7 da fila, "O URL não está no Google". O pedido do PCMG deu "Ops... algo deu errado" e passou na 2ª tentativa. Parou em 10 pelo limite da tarefa, sem aviso de cota excedida; relatórios Detectada/Rastreada não foram usados.
- 25/11/2026 (rodada das 13h27): /concurso-ufba-assistente-administracao/ (reindexar) , /concurso-semusa-porto-velho/ (reindexar) , /noticias/dpepb-inscricoes-ate-13-11/ (reindexar) , /ppms-policial-penal-2026/ (fila) , /concursos-mato-grosso-do-sul/ (fila) , /concurso-pm-ba/ (fila) , /concurso-pm-sc/ (fila) , /concursos-rondonia/ (detectada) , /guarda-municipal/ (detectada). As 3 de reindexar estavam no Google; as 4 da fila e as 2 detectadas, "O URL não está no Google". Parou em 9 por falta de candidato, sem aviso de cota excedida: os relatórios Detectada (28) e Rastreada (12) ainda são de 15/11 e todo o resto já foi pedido nos últimos 14 dias ou já está no Google (inspecionadas sem pedido: /concursos-parana/ e /concursos-mato-grosso/ e os posts /noticias/policial-penal-pe-conhecimentos-especificos-o-que-estudar/ , /noticias/banestes-tecnico-bancario-conhecimentos-bancarios-o-que-estudar/ , /noticias/pm-sp-soldado-rotina-de-estudos-para-quem-trabalha/). A seção Reindexar ficou vazia.
- 26/11/2026 (rodada das 12h55): /professor-fisica-seduc-sp-2026/ (rastreada) , /professor-lingua-portuguesa-seduc-sp-2026/ (rastreada). Reindexar e Na fila estavam vazias. Relatório atualizado: Detectada 7 (todas /afiliados/, /amostra/ ou pedidas em 25/11) e Rastreada 23. O 3º pedido (/professor-ciencias-seduc-sp-2026/, "O URL não está no Google") deu "A cota foi excedida": provavelmente os 9 pedidos de 25/11 às 13h27 ainda contavam (janela de 24 h). Os 9 candidatos restantes da Rastreada foram para "Na fila". Próxima rodada de preferência depois das 13h30.
- 27/11/2026 (rodada das 12h55): /professor-ciencias-seduc-sp-2026/ (fila) , /professor-seduc-sp-2026/ (fila) , /professor-ingles-seduc-sp-2026/ (fila) , /professor-seduc-ma-2026/ (fila) , /gm-maraba-2026/ (fila) , /pmerj-cfo-2027/ (fila) , /cbmerj-cadete-2027/ (fila). Reindexar estava vazia. As 7 deram "O URL não está no Google" e "Indexação solicitada" sem erro. Parou em 7 por falta de candidato, sem aviso de cota excedida: relatório igual ao de 26/11 (Detectada 7, todas /afiliados/, /amostra/ ou pedidas em 25/11; Rastreada 23, todas pedidas nos últimos 14 dias, já indexadas, variantes com ?src= ou /assets/amostras/). /assistente-administrativo-contagem-2026/ (Rastreada) foi inspecionada e já está no Google.

## Já estavam no Google (sem pedido)

- 22/11/2026: /pcpe-agente-2026/ , /ppsc-policial-penal-2026/ , /pjcmt-investigador-escrivao-2026/ , /concurso-gm-joinville/ , /concurso-pc-mg/ , /concurso-pc-pa/ , /concurso-pc-to/ , /concurso-pjc-mt/ , /concurso-pm-ac/ , /concurso-pm-mg/ , /concurso-pm-pa/ , /concurso-pm-pr/ , /concurso-pm-rj/ , /concurso-pm-rr/ , /concurso-policia-penal-pb/ , /concurso-policia-penal-pr/ , /concurso-policia-penal-sc/ , /concurso-seedf-professor/ , /concurso-unificado-ma/
- 24/11/2026: nenhum (as 9 inspecionadas da fila estavam fora do Google)
- 25/11/2026: nenhum da fila (as 4 estavam fora do Google). Dos relatórios, já indexadas e sem pedido: /concursos-parana/ , /concursos-mato-grosso/ , /noticias/policial-penal-pe-conhecimentos-especificos-o-que-estudar/ , /noticias/banestes-tecnico-bancario-conhecimentos-bancarios-o-que-estudar/ , /noticias/pm-sp-soldado-rotina-de-estudos-para-quem-trabalha/
- 26/11/2026: nenhum (fila vazia; as 3 inspecionadas da Rastreada estavam fora do Google)
- 27/11/2026: /noticias/gm-campinas-inscricoes-abrem-25-11/ (fila) , /noticias/curitiba-agente-cronograma-3-semanas/ (fila). Da Rastreada, já indexada e sem pedido: /assistente-administrativo-contagem-2026/
