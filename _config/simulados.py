# -*- coding: utf-8 -*-
"""Simulado grátis por curso de edital aberto (22/11/2026, ideia 4 do estudo de vendas). Idempotente.

Entrada: _config/simulados/{curso_id}.json  {"curso_id", "titulo", "banca", "tempo_min", "questoes": [
           {"disciplina", "enunciado", "alternativas": {"A": ...}, "gabarito", "comentario"} ou {"tipo": "ce", ...}]}
Saída:   /simulado-{curso_id}/index.html  (usa o guia.modelo.html; o site.js bloco 9 corrige e libera o gabarito
         depois do e-mail, que vai para a aba "Simulados" da planilha pelo App da Web).
Depois rode conversao.py (chamada para o simulado na página do curso e no guia) e aplicar.py (sitemap).

Uso: PYTHONIOENCODING=utf-8 python _config/simulados.py
"""
import html as H
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITE = json.loads((RAIZ / "_config/site.json").read_text(encoding="utf-8"))
NOMES = json.loads((RAIZ / "_config/nomes.json").read_text(encoding="utf-8"))["cursos"]
PROD = {p["id"]: p for p in json.loads((RAIZ / "_config/produtos.json").read_text(encoding="utf-8"))["produtos"]}
MODELO = (RAIZ / "_config/guia.modelo.html").read_text(encoding="utf-8")
BASE = SITE["url_base"].rstrip("/") + "/"
e = lambda s: H.escape(str(s), quote=True)


def checkout(cid):
    """Link do botão de compra do topo da página do curso (já com cupom e src)."""
    import re
    arq = RAIZ / cid / "index.html"
    if not arq.exists():
        return "../" + cid + "/"
    m = re.search(r'<a [^>]*data-observa [^>]*href="([^"]+)"', arq.read_text(encoding="utf-8"))
    return H.unescape(m.group(1)).replace("src=site", "src=simulado") if m else "../" + cid + "/"


def pagina(dados):
    cid = dados["curso_id"]
    n, p = NOMES.get(cid, {}), PROD.get(cid, {})
    sigla, cargo = n.get("sigla", ""), n.get("cargo", "")
    qtd = len(dados["questoes"])
    slug = f"simulado-{cid}"
    titulo = f"Simulado grátis {sigla} {cargo} 2026: {qtd} questões"
    desc = f"Simulado grátis {sigla} {cargo} com {qtd} questões no estilo {dados.get('banca', 'da banca')}, nota na hora por disciplina e gabarito comentado."
    c = p.get("cupom") or {}
    import datetime as dt
    hoje = dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).date().isoformat()
    preco = f"R$ {c['preco']} com o cupom {c['codigo']}" if c.get("preco") and c.get("ate", "") >= hoje else f"R$ {p.get('preco', 47)}"
    ld = {"@context": "https://schema.org", "@type": "Quiz", "name": titulo, "description": desc, "inLanguage": "pt-BR",
          "educationalLevel": "Concurso público", "about": f"{sigla} {cargo}", "url": BASE + slug + "/",
          "provider": {"@type": "Organization", "name": "ESCUDO Concursos", "url": BASE}}
    corpo = f"""<p class="sim-intro">{qtd} questões do curso ESCUDO {e(sigla)}, no estilo {e(dados.get('banca', 'da banca'))}. Responda no seu tempo (sugestão: {dados.get('tempo_min', qtd * 2)} minutos), clique em <b>Ver minha nota</b> e veja o resultado por disciplina. O gabarito comentado de cada questão sai depois de informar o e-mail.</p>
<div data-simulado data-endpoint="{e(SITE.get('pedido_url', ''))}">
<ol class="sim-lista" data-sim-questoes><li>Carregando as questões...</li></ol>
<p><button class="btn" type="button" data-sim-corrigir>Ver minha nota</button></p>
<div class="sim-caixa" data-sim-resultado hidden aria-live="polite"></div>
<div class="sim-caixa pedido" data-sim-gate hidden>
  <h3>Gabarito comentado grátis</h3>
  <p>Informe o seu e-mail para ver a resposta certa e o comentário de cada questão. Se quiser, deixe o WhatsApp para receber os prazos do concurso.</p>
  <form class="pedido-form">
    <label>Seu e-mail <input name="email" type="email" required maxlength="120" placeholder="voce@email.com" autocomplete="email"></label>
    <label>WhatsApp (opcional) <input name="whatsapp" type="tel" maxlength="20" placeholder="(00) 90000-0000" autocomplete="tel" inputmode="tel"></label>
    <label class="pedido-isca" aria-hidden="true">Não preencha <input name="site_url" tabindex="-1" autocomplete="off"></label>
    <button class="btn" type="submit">Ver o gabarito comentado</button>
  </form>
</div>
<div class="guia-curso" data-sim-final hidden>
  <p><strong>Gostou do nível das questões?</strong> Elas são do curso ESCUDO {e(sigla)} {e(cargo)} em PDF: {e('; '.join(p.get('itens', [])))}. {e(preco)}.</p>
  <a href="{e(checkout(cid))}" data-goatcounter-click="simulado-compra" data-goatcounter-title="simulado-compra {e(cid)}">Quero o curso completo</a>
  <p><a href="../{e(cid)}/" style="background:none;padding:0;color:var(--goldb)!important;text-decoration:underline">Ver tudo o que vem no curso</a></p>
</div>
</div>
<script type="application/json" id="simulado-dados">{json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")}</script>
<p class="guia-rodape"><em>Questões inéditas do curso ESCUDO, no estilo da banca. Material independente, sem vínculo com o órgão nem com a banca.</em></p>"""
    trilha = f'<nav class="guia-trilha" aria-label="Você está em"><a href="../">Início</a> <span aria-hidden="true">›</span> <a href="../{e(cid)}/">Curso {e(sigla)}</a> <span aria-hidden="true">›</span> Simulado grátis</nav>'
    reps = {"{{titulo}}": e(titulo), "{{descricao}}": e(desc), "{{url}}": BASE + slug + "/", "{{slug}}": slug, "{{og_tipo}}": "website",
            "{{css_extra}}": "", "{{ld}}": '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>",
            "{{tema}}": e(p.get("tema", "")), "{{topo_link}}": f'<a class="topo-link" href="../{e(cid)}/">Ver o curso</a>', "{{trilha}}": trilha,
            "{{h1}}": e(f"Simulado grátis {sigla} {cargo}: {qtd} questões com gabarito comentado"), "{{atualizado}}": "Atualizado em 22/11/2026",
            "{{artigo}}": corpo, "{{faq}}": "", "{{razao_social}}": e(SITE["razao_social"]), "{{cnpj}}": e(SITE["cnpj"]),
            "{{endereco}}": e(SITE["endereco"]), "{{email}}": e(SITE["email"])}
    s = MODELO
    for k, v in reps.items():
        s = s.replace(k, v)
    s = s.replace("</body>", '<script src="../assets/js/site.js?v=10" defer></script>\n</body>', 1)
    destino = RAIZ / slug / "index.html"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(s, encoding="utf-8")
    return slug


def main():
    for arq in sorted((RAIZ / "_config/simulados").glob("*.json")):
        dados = json.loads(arq.read_text(encoding="utf-8"))
        assert all(q["gabarito"] in (["C", "E"] if q.get("tipo") == "ce" else q["alternativas"]) for q in dados["questoes"]), arq
        print(pagina(dados), len(dados["questoes"]), "questões")


if __name__ == "__main__":
    main()
