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
7. Não mexer em páginas de curso, home, guias ou scripts de outras frentes; a rotina só cria e edita arquivos em `_config/blog/` e roda os geradores.

## Passo a passo

1. Clonar os dois repositórios (o site com `--depth 1`; `git fetch origin main` antes de empurrar). Instalar `pip install markdown pillow fonttools brotli`.
2. Ler `_config/blog-config.json`. Se `publicar_direto` for `false`, trabalhar no ramo `blog` (rebase em `origin/main`) em vez do `main`.
3. **Pautas do dia**, nesta ordem:
   - Mudanças oficiais nos concursos com curso à venda: retificação, prorrogação, locais de prova, gabarito, resultado. Ver a página do concurso na banca (Cebraspe, FCC, FGV, Cesgranrio, AOCP, IBFC, Idecan, Consulplan, IBGP) e o Diário Oficial correspondente.
   - Edital novo de concurso do radar (prefeituras: API do Querido Diário, `https://api.queridodiario.org.br/gazettes?querystring=...`).
   - Datas que vencem nos próximos 3 dias (fim de inscrição, isenção, pagamento, prova) tiradas dos guias em `_config/guias/`: vira lembrete curto.
   - Sem fato novo: um post "o que estudar" (por banca e matéria, a partir de `escudo-dados/fichas/`) ou "rotina de estudos" (cronograma até a prova). Não repetir assunto que já tenha post em `_config/blog/`, nem copiar o guia do concurso: o post precisa trazer ângulo novo.
4. Salvar o texto do documento oficial em `escudo-dados/fontes/<slug>/<nome>.txt` (PDF: `pdftotext -layout`).
5. Escrever o post em `_config/blog/AAAA-MM-DD-<slug>.md` com o cabeçalho descrito em `blog.py` (tipo, titulo_seo até 60 caracteres, descricao até 160, h1, publicado, atualizado_em, curso_id, guia, ficha se usar, fontes com link oficial, calculado para valores que o post calcula, resumo, capa_titulo, capa_destaque, valido_ate). Padrão editorial (benchmark de 08/11 com Gran, Estratégia, Folha Dirigida, Focus e Solução):
   - Título SEO e H1 dizem a mesma coisa, com o nome do concurso e o fato (ex.: "PM-SP Soldado: inscrições abrem 09/11").
   - Primeiro parágrafo = a resposta (o quê, quando, quanto). Não repetir em "Resposta rápida": a tabela `resumo` (4 a 6 linhas: órgão, banca, vagas, salário, datas) já faz esse papel.
   - Seções H2 curtas, cada uma respondendo a uma pergunta. Datas e planos semanais sempre em tabela, nunca em lista.
   - Fechar com "## Perguntas frequentes" (3 perguntas em H3, resposta de 1 a 3 frases): vira FAQPage no schema.
   - Capa: `capa_titulo` até ~45 caracteres e `capa_destaque` com o trecho que fica em rosa (data, número).
   - `valido_ate` = data em que o post perde a validade (fim de inscrição, prova): depois dela a página mostra aviso de prazo encerrado.
   - Link do documento oficial sempre em `fontes`. No máximo 2 chamadas para o curso (a caixa automática e uma no texto).
   - Sem promessa de aprovação, sem "imperdível", sem emoji, sem afirmação genérica sem fonte.
6. Revisão: reler o post contra a fonte como um revisor exigente (afirmação sem base, data errada, frase parecida com portal, português). Corrigir.
7. Conferidor (regra 5). Barrado: mover para `escudo-dados/fila/` com o motivo e seguir.
8. Gerar: `python3 _config/blog.py && python3 _config/aplicar.py && python3 -I -X utf8 _config/contador.py`.
9. Commit no site (só `_config/blog/`, `noticias/`, `concurso-*/index.html`, `llms.txt`, `sitemap.xml`, `robots.txt`) e push. Commit e push no escudo-dados (fontes e fila).
10. O IndexNow é avisado sozinho pelo GitHub Actions a cada push no `main`.
11. Resumo final em 3 a 5 linhas: posts publicados (link), barrados e motivo, pautas descartadas.

## Quando um fato muda

Retificação de algo já publicado: editar o mesmo post, mudar `atualizado_em` e acrescentar uma linha "Atualização em dd/mm/aaaa: ..." no topo. Não criar post novo para o mesmo fato.
