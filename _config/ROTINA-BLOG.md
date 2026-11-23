# Rotina diária do blog /noticias/ (ESCUDO)

Criada em 08/11/2026. Roda todo dia de manhã na nuvem do Claude Code (Sonnet), sem o PC.
Repositórios: `escudoconcursos/escudoconcursos.github.io` (site, público) e `escudoconcursos/escudo-dados` (privado: fichas, radar, fontes, fila).
Responder e escrever sempre em português do Brasil, sem travessão. Horários sempre de Brasília.

## Regras que não mudam

1. No máximo **2 posts por dia**. Dia sem fato novo e sem pauta boa = nenhum post. Nunca encher linguiça.
2. Notícia só nasce de **documento oficial** (edital, retificação, convocação, resultado) salvo em `escudo-dados/fontes/<slug>/` como .txt. Portal (PCI, Folha Dirigida, Estratégia etc.) e busca na web só servem de alerta; nunca copiar frase deles.
3. Respeitar robots.txt e bloqueio. A VUNESP devolve 403 para script: não contornar. Para VUNESP, usar o Diário Oficial de SP ou a página do concurso no Portal de Concursos de SP.
4. Só concursos do radar (`escudo-dados/radar/radar-dados.json`) ou com curso à venda (`_config/produtos.json`). Concurso descartado pelo Mateus (ver memória do projeto) não entra.
5. Todo post passa no conferidor: `python3 _config/blog_conferir.py --dados ../escudo-dados <arquivo>`. Barrado = não publica; vai para `escudo-dados/fila/` com o motivo.
6. Nunca publicar capítulo, questão ou trecho dos livros. Nunca subir ficha para o repositório público.
7. Não mexer em páginas de curso, home, texto dos guias ou scripts de outras frentes; a rotina só cria e edita arquivos em `_config/blog/`, acrescenta linhas em `_config/guias/atualizacoes.json` e roda os geradores.
8. **O guia é o artigo vivo do concurso** (Mateus 08/11). Cada novidade oficial entra como linha datada no bloco "Últimas atualizações" no topo do guia `/concurso-<slug>/`, a mais nova em cima; o texto antigo continua abaixo e o guia passa a mostrar "Atualizado em" e `dateModified` da novidade mais recente.
   - **Notícia pequena** (autorização do concurso, banca escolhida, comissão formada, retificação pequena, prazo prorrogado, local de prova divulgado): NÃO vira post. Vira só uma linha em `_config/guias/atualizacoes.json` na chave do guia: `{"data": "AAAA-MM-DD", "texto": "1 frase com o fato", "fonte": "link oficial"}`. Não conta no limite de 2 posts.
   - **Notícia grande** (edital publicado, data da prova, gabarito, resultado, convocação): vira post próprio em `_config/blog/` com `tipo: noticia` e `guia: concurso-<slug>`; a linha no guia, com link "Leia a notícia", entra sozinha.
   - Concurso sem guia ainda (só no radar): notícia pequena fica para quando o guia existir; anotar em `escudo-dados/fila/` e seguir.

## Passo a passo

1. Clonar os dois repositórios (o site com `--depth 1`; `git fetch origin main` antes de empurrar). Instalar `pip install markdown pillow fonttools brotli`.
2. Ler `_config/blog-config.json`. Se `publicar_direto` for `false`, trabalhar no ramo `blog` (rebase em `origin/main`) em vez do `main`.
3. **Pautas do dia**: primeiro ler a pauta prévia da semana em `escudo-dados/fila/PAUTA-SEMANA-<segunda AAAA-MM-DD>.md` (combinada com o Mateus) e seguir a linha do dia; novidade oficial passa na frente. Sem pauta da semana, nesta ordem:
   - Mudanças oficiais nos concursos com curso à venda: retificação, prorrogação, locais de prova, gabarito, resultado. Ver a página do concurso na banca (Cebraspe, FCC, FGV, Cesgranrio, AOCP, IBFC, Idecan, Consulplan, IBGP) e o Diário Oficial correspondente.
   - Edital novo de concurso do radar (prefeituras: API do Querido Diário, `https://api.queridodiario.org.br/gazettes?querystring=...`).
   - Datas que vencem nos próximos 3 dias (fim de inscrição, isenção, pagamento, prova) tiradas dos guias em `_config/guias/`: vira lembrete curto.
   - **Antes do "o que estudar" genérico: pauta de busca** (seção "Pautas de busca" no fim deste arquivo). São perguntas que já aparecem no Google para o site e ainda não têm página que responda. Uma por dia, a de cima primeiro, e riscar a usada.
   - Sem fato novo: um post "o que estudar" (por banca e matéria, a partir de `escudo-dados/fichas/`) ou "rotina de estudos" (cronograma até a prova). Não repetir assunto que já tenha post em `_config/blog/`, nem copiar o guia do concurso: o post precisa trazer ângulo novo.
4. Salvar o texto do documento oficial em `escudo-dados/fontes/<slug>/<nome>.txt` (PDF: `pdftotext -layout`).
5. Escrever o post em `_config/blog/AAAA-MM-DD-<slug>.md` com o cabeçalho descrito em `blog.py` (tipo, titulo_seo até 60 caracteres, descricao até 160, h1, publicado, atualizado_em, curso_id, guia, ficha se usar, fontes com link oficial, calculado para valores que o post calcula, resumo, capa_titulo, capa_destaque, valido_ate). Padrão editorial (benchmark de 08/11 com Gran, Estratégia, Folha Dirigida, Focus e Solução):
   - PERTENCIMENTO (Mateus 08/11): texto e imagem precisam fazer o leitor se ver dentro da corporação ou do órgão daquele concurso. Usar o nome, a farda, a sigla, a cidade e o dia a dia do cargo (ex.: "a farda cinza da PM-SP", "o Soldado PM de 2ª Classe"); falar com o candidato como futuro integrante. Foto sempre da própria corporação ou órgão do post, nunca genérica de outra polícia ou estado; sem foto da corporação certa, usar a capa padrão.
   - Título SEO e H1 dizem a mesma coisa, com o nome do concurso e o fato (ex.: "PM-SP Soldado: inscrições abrem 09/11").
   - Primeiro parágrafo = a resposta (o quê, quando, quanto). Não repetir em "Resposta rápida": a tabela `resumo` (4 a 6 linhas: órgão, banca, vagas, salário, datas) já faz esse papel.
   - Seções H2 curtas, cada uma respondendo a uma pergunta. Datas e planos semanais sempre em tabela, nunca em lista.
   - Fechar com "## Perguntas frequentes" (3 perguntas em H3, resposta de 1 a 3 frases): vira FAQPage no schema.
   - Capa: `capa_titulo` até ~45 caracteres e `capa_destaque` com o trecho que fica em rosa (data, número).
   - `valido_ate` = data em que o post perde a validade (fim de inscrição, prova): depois dela a página mostra aviso de prazo encerrado.
   - Fotos (campo `fotos`, lista JSON; a 1ª vai para a capa, as outras antes do 2º, 3º... H2): só de licença livre do Wikimedia Commons (CC BY, CC BY-SA, CC0 ou domínio público), de preferência as do Governo do estado vindas do Flickr oficial. Baixar a miniatura de 1280px de `upload.wikimedia.org` com User-Agent `EscudoBlogBot/1.0 (https://escudoconcursos.com.br)` e calma entre pedidos (o Commons devolve 429), salvar em `_config/blog/fotos/` e preencher arquivo, credito, licenca, url (página do arquivo no Commons), alt e legenda (sem números, que o conferidor não cobre). Nunca foto de portal, banca, Google Imagens ou rede social; nunca político em destaque, protesto, ocorrência ou pessoa em situação constrangedora: só formatura, desfile, viatura, treinamento. Sem foto boa = post sem foto (a capa sai no padrão).
   - O blog.py gera sozinho `noticias/<slug>/story.jpg` (1080x1920) para o story do Instagram. No resumo final, listar o link de cada story.jpg e do post com `?src=insta-story`, para quem agenda no Meta Business Suite.
   - Link do documento oficial sempre em `fontes`. No máximo 2 chamadas para o curso (a caixa automática e uma no texto).
   - Sem promessa de aprovação, sem "imperdível", sem emoji, sem afirmação genérica sem fonte.
6. Revisão: reler o post contra a fonte como um revisor exigente (afirmação sem base, data errada, frase parecida com portal, português). Corrigir.
7. Conferidor (regra 5). Barrado: mover para `escudo-dados/fila/` com o motivo e seguir.
   Linhas novas de `atualizacoes.json` também passam no conferidor: `python3 _config/blog_conferir.py --dados ../escudo-dados --atualizacoes` (documento oficial salvo em `escudo-dados/fontes/concurso-<slug>/`).
8. Gerar: `python3 _config/guias.py && python3 _config/blog.py && python3 _config/aplicar.py && python3 -I -X utf8 _config/contador.py`.
9. Commit no site (só `_config/blog/`, `_config/guias/atualizacoes.json`, `noticias/`, `concurso-*/index.html`, `llms.txt`, `sitemap.xml`, `robots.txt`) e push. Commit e push no escudo-dados (fontes e fila).
10. O IndexNow é avisado sozinho pelo GitHub Actions a cada push no `main`.
11. Resumo final em 3 a 5 linhas: posts publicados (link), barrados e motivo, pautas descartadas.

## Quando um fato muda

Retificação de algo já publicado: editar o mesmo post, mudar `atualizado_em` e acrescentar uma linha "Atualização em dd/mm/aaaa: ..." no topo. Não criar post novo para o mesmo fato. E acrescentar a linha da mudança em `_config/guias/atualizacoes.json` (se for pequena) para ela aparecer no topo do guia.

## Post de prazo não morre no prazo (20/11/2026)

Post de "inscrições até", "isenção até" ou "pagamento até" continua recebendo busca depois da data, só que com outra pergunta ("quando sai o resultado da isenção"). Em 20/11 o post da isenção da PC-PE tinha 59 impressões na posição 5 e nenhum clique, porque o título ainda falava do prazo vencido. Regra: no dia seguinte ao prazo, reescrever o MESMO post (mesmo slug) para a etapa seguinte do edital (resultado provisório, recurso, resultado final, local de prova), trocando `titulo_seo`, `descricao`, `h1`, `capa_titulo`, `capa_destaque`, o primeiro parágrafo, a tabela `resumo` e `valido_ate` (nova data), com a linha "Atualização em dd/mm/aaaa" no topo. Conta como post do dia. Modelo: `_config/blog/2026-11-10-pcpe-agente-isencao-ate-12-11.md`.

## Pautas de busca (Search Console de 20/11/2026)

Consultas que já trazem impressão ao site e ainda não têm resposta própria. Sempre com a fonte oficial, como qualquer post.

1. IBGE Recenseador: o que cai em Conhecimentos Técnicos a partir da apostila oficial do 12º Censo Agro (30 das 60 questões; inscrições até 25/11). Busca: "conteúdo do documento estudo dos conhecimentos técnicos 12º censo agropecuário".
2. Policial Penal PE: resultado da isenção (aplicar a regra acima ao post de 20/11 em 23/11).
3. Banestes: o que faz o Técnico Bancário do Banestes (atribuições do edital, jornada de 30 horas, salário). Busca: "o que faz um técnico bancário do banestes".
4. PM-SP Soldado: como é a prova (60 questões, redação, nota mínima de 30) e onde achar provas anteriores da VUNESP no site oficial. Busca: "prova soldado pm sp 2026 pdf". Nunca hospedar PDF de prova da banca; só apontar o link oficial.
5. CBM-PE Soldado: como é a prova do AOCP e onde estão as provas anteriores oficiais. Buscas: "prova cbmpe pdf", "apostila cbmpe pdf", "concurso bombeiros pe".
6. PM-PE Soldado: datas que faltam até a prova de 21/02/2027 (o guia está na posição 24 para "concurso pm pe", com 133 impressões; um post novo e atual com link para o guia ajuda).
7. Aparecida de Goiânia: o que faz o Agente Educativo (busca "agente educativo", 44 impressões na posição 5).

## Prioridade de vendas: fim de inscrição (23/11/2026, pedido do Mateus)
O curso vende quando a inscrição está para fechar e para quase a zero depois. Nos concursos abaixo, nos últimos 10 dias de inscrição, há um post por concurso a cada 3 ou 4 dias, na frente do "o que estudar" genérico (fato oficial novo continua na frente de tudo): lembrete do prazo, o que estudar com o tempo que falta e o link do curso com src=blog. Ângulo novo a cada post, sem repetir o guia.
- TJSP Escrevente: inscrições até 10/12/2026 (posts em 30/11, 04/12 e 08/12).
- PC-PE Agente e Escrivão: inscrições até 16/12/2026 (posts em 06/12, 10/12 e 14/12).
- DPE-AM Assistente: inscrições de 30/11/2026 a 04/01/2027 (post na abertura, 30/11, e nos últimos 10 dias: 26/12, 30/12 e 02/01).
A faixa "Inscrições terminando" da home (vitrine.py, DESTAQUE_PRAZOS) já mostra esses cursos; os stories das 20h já priorizam guia com inscrição perto do fim.
