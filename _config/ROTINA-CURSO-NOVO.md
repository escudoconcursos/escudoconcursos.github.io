# Rotina do site para curso novo (ESCUDO)

Atualizada em 07/11/2026. A pasta `_config/` não é publicada pelo GitHub Pages. Todos os scripts são idempotentes: rodar de novo não estraga nada.

No PC, rode tudo de dentro de `G:\Amazon\07-site` com `PYTHONIOENCODING=utf-8 python _config/{script}.py`. O `amostra.py` e o `guias.py` precisam do pacote markdown: `PYTHONIOENCODING=utf-8 uv run --no-project --with markdown python _config/{script}.py`.

## 1. Dados do curso (editar antes de rodar)

| Arquivo | O que pôr |
|---|---|
| `{curso}/index.html` | Página do curso, copiada de uma parecida (mesmo formato do bloco de preço `data-oferta`). |
| `_config/produtos.json` | Cartão da vitrine: id, atalho, carreira, tema, tag, título, itens, imagem, preço, cupom, inscrições, prova, link. |
| `_config/nomes.json` | Sigla, cargo e UF (H1, trilha, "Outros cursos"). |
| `_config/editais.json` | Selo acima do preço. Em "aberto", o edital e a banca; em "pre", o último edital usado como base (vazio se não houver número). |
| `_config/beneficios.json` | Imagens das páginas da apostila ao lado de cada benefício (tiradas do "PDF Completo"). |
| `_config/seo.py` (dicionário BUSCA) | A palavra-chave como o aluno digita no Google. |
| `_config/afiliados.py` (RECRUTAMENTO) | Link da página de recrutamento de afiliados da Hotmart. |
| `_config/amostras/{curso}.md` + `assets/amostras/{curso}.pdf` | Amostra grátis: apresentação e 10 questões (só as questões usam `###`). |
| `_config/guias/concurso-{slug}.md` | Guia do concurso (opcional, com `curso_id` no cabeçalho). |
| `_config/hubs.json` | Só se o curso abrir carreira ou estado que ainda não tem página. |

## 2. Ordem dos scripts

1. `seo.py`
2. `vitrine.py` (home, busca, atalhos como /pmesp/)
3. `hubs.py` (páginas de carreira e estado)
4. `onda1.py` (H1, % OFF, botão do meio, benefícios com imagem, trilha, outros cursos, selo do edital)
5. `amostra.py` (se o curso tiver amostra)
6. `guias.py` (se mexeu em guia ou no "Quem faz"; rodar depois do vitrine.py, que regrava o llms.txt)
7. `afiliados.py` (se mudou afiliados)
8. `aplicar.py` (dados da empresa, endereços absolutos, sitemap)
9. `contador.py` (sempre por último: põe o GoatCounter nas páginas novas e nos atalhos)

Depois: conferir `git -c core.autocrlf=true status`, commit e `git -C G:/Amazon/07-site push origin main`.

## 3. Quando mudar CSS ou JS

Subir a versão em todas as páginas e nos geradores: `escudo.css?v=N` e `site.js?v=N` (strings em `amostra.py`, `hubs.py`, `guia.modelo.html` e `afiliados.modelo.html`).

## 4. Edital novo ou retificação

Trocar a linha do curso em `editais.json` (de "pre" para "aberto" quando sair o edital), atualizar datas em `produtos.json` e rodar `onda1.py`, `vitrine.py`, `hubs.py`, `aplicar.py` e `contador.py`.
