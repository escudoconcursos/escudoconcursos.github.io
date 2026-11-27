# -*- coding: utf-8 -*-
"""Monta a vitrine da página inicial a partir de _config/produtos.json (pode rodar quantas vezes quiser).

- Reescreve, no index.html, o trecho entre <!-- vitrine:inicio --> e <!-- vitrine:fim -->:
  botões de filtro por carreira (só as carreiras que têm curso) e os cartões, já na ordem de urgência
  do dia em que o script rodou. No navegador, o assets/js/site.js refaz a ordem e os selos com a data
  do visitante e esconde o curso no dia seguinte à prova.
- Gera um atalho por curso (ex.: /pmpe/), uma página que redireciona para o curso, para citar em post e story.

Uso: PYTHONIOENCODING=utf-8 python _config/vitrine.py   (depois rode o aplicar.py)
"""
import datetime as dt, html, json, pathlib, re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DADOS = json.loads((RAIZ / "_config" / "produtos.json").read_text(encoding="utf-8"))
CARREIRAS = DADOS["carreiras"]
_NOMES = RAIZ / "_config" / "nomes.json"
NOMES = json.loads(_NOMES.read_text(encoding="utf-8"))["cursos"] if _NOMES.exists() else {}
APELIDOS = {  # outros nomes que o aluno digita na busca da home (07/11/2026)
    "pmesp-soldado-2026": "PMESP PMSP PM SP Polícia Militar", "pmpe-soldado-2026": "PMPE PM PE Polícia Militar",
    "pmal-soldado-2026": "PMAL PM AL Polícia Militar", "pmba-soldado-2026": "PMBA PM BA Polícia Militar",
    "pmerj-soldado-2026": "PMERJ PMRJ PM RJ Polícia Militar", "pmmg-soldado-2026": "PMMG PM MG Polícia Militar Minas Gerais CRS", "policial-penal-pb-2026": "PPPB Polícia Penal Paraíba SEAP Idecan", "pmac-soldado-2026": "PMAC PM AC Polícia Militar Acre Rio Branco IBADE", "cbmes-soldado-2026": "CBMES CBM ES Corpo de Bombeiros Militar Espírito Santo Bombeiro Soldado Combatente Vitória IDECAN", "pcto-oficial-investigador-2026": "PCTO PC TO Polícia Civil Tocantins Palmas Oficial Investigador Agente Escrivão Aroeira", "pcpa-investigador-2026": "PCPA PC PA Polícia Civil Pará Belém Investigador AOCP Seplad", "pcpa-escrivao-2026": "PCPA PC PA Polícia Civil Pará Belém Escrivão AOCP Seplad", "detranpr-agente-2026": "DETRAN DETRANPR DETRAN-PR Agente de Trânsito Paraná Curitiba CTB CONTRAN FUNDASEG", "ppsc-policial-penal-2026": "PPSC PP SC Polícia Penal Santa Catarina Policial Penal SEJURI Florianópolis FEPESE", "pjcmt-investigador-escrivao-2026": "PJCMT PJC MT PCMT PC MT Polícia Civil Mato Grosso Cuiabá Investigador Escrivão UFMT SESP", "pmrr-soldado-2026": "PMRR PM RR Polícia Militar Roraima Boa Vista UERR", "pmpb-soldado-2026": "PMPB PM PB Polícia Militar Paraíba João Pessoa Campina Grande IBFC CFSd", "ppto-policial-penal-2026": "PPTO PP TO Polícia Penal Tocantins Palmas Funcab Policial Penal Técnico em Defesa Social Agente de Execução Penal", "ppba-policial-penal-2026": "PPBA PP BA Polícia Penal Bahia Salvador SEAP FGV Policial Penal Agente Penitenciário", "pcrn-agente-2026": "PCRN PC RN Polícia Civil Rio Grande do Norte Natal FGV Agente de Polícia Civil APC", "ppms-policial-penal-2026": "PPMS PP MS Polícia Penal Mato Grosso do Sul AGEPEN Campo Grande FAPEMS Policial Penal Agente Penitenciário", "pmmt-soldado-2026": "PMMT PM MT Polícia Militar Mato Grosso Cuiabá UFMT Soldado Aluno-a-Soldado Escola de Formação de Praças", "cbmba-soldado-2026": "CBMBA CBM BA Corpo de Bombeiros Militar Bahia Salvador Soldado Bombeiro FCC SAEB", "pmba-cfo-2026": "CFO PMBA CFO PM BA PM-BA Oficial Polícia Militar Bahia Salvador UNEB concurso cfo pmba 2026",
    "seedf-professor-2026": "SEEDF SEE DF Secretaria de Educação do Distrito Federal Brasília Professor Magistério Quadrix",
    "seedf-pedagogia-2026": "SEEDF SEE DF Secretaria de Educação do Distrito Federal Brasília Professor Pedagogia Magistério Quadrix",
    "pmmg-cfo-2027": "CFO PMMG CFO PM MG Cadete Oficial Polícia Militar Minas Gerais CRS",
    "pmerj-cfo-2027": "CFO PMERJ CFO PM RJ PMRJ Oficial Polícia Militar Rio de Janeiro Cesgranrio concurso cfo pmerj 2027",
    "cbmerj-cadete-2027": "CBMERJ CBM RJ CFO CBMERJ Cadete Bombeiros Bombeiro Militar Rio de Janeiro UERJ DSEA concurso cbmerj cadete 2027 cfo bombeiro rj",
    "pmpa-soldado-2026": "PMPA PM PA Polícia Militar",
    "soldado-pmpr-2026": "PMPR PM PR Polícia Militar", "soldado-pmsc-2026": "PMSC PM SC Polícia Militar",
    "cbmpe-soldado-2026": "CBMPE CBM PE Bombeiros Bombeiro Militar", "cbm-al-soldado-2026": "CBMAL CBM AL Bombeiros Bombeiro Militar",
    "pcpe-agente-2026": "PCPE PC PE Polícia Civil", "pcpe-escrivao-2026": "PCPE PC PE Polícia Civil Pernambuco Escrivão Arquivologia Cebraspe", "pcac-oficial-investigador-2026": "PCAC PC AC Polícia Civil",
    "investigador-policia-civil-mg-pcmg-2026": "PCMG PC MG Polícia Civil", "policial-penal-pe-2026": "PPPE Polícia Penal SERES",
    "policial-penal-pr-2026": "PPPR Polícia Penal DEPPEN", "gm-recife-2026": "GCM Recife Guarda Municipal", "gm-joinville-2026": "GCM Joinville Guarda Municipal SC", "gm-pedra-branca-do-amapari-2026": "GM GCM Pedra Branca do Amapari Guarda Municipal Amapá AP Instituto Nazaré", "professor-lingua-portuguesa-seduc-ma-2026": "SEDUC MA Maranhão Professor Língua Portuguesa Português Letras Concurso Unificado do Maranhão FCC SEAD", "professor-matematica-seduc-ma-2026": "SEDUC MA Maranhão Professor Matemática Concurso Unificado do Maranhão FCC SEAD cargo 23", "supervisao-escolar-seduc-ma-2026": "SEDUC MA Maranhão Supervisão Escolar Especialista em Educação Concurso Unificado do Maranhão FCC SEAD Pedagogia", "assistente-tecnico-sead-ma-2026": "SEAD MA Maranhão Assistente Técnico Administração Concurso Unificado do Maranhão FCC Assistente de Administração", "professor-matematica-seduc-sp-2026": "SEDUC SP São Paulo Professor Matemática FGV PEFM Secretaria da Educação Professor de Ensino Fundamental e Médio concurso estadual", "professor-lingua-portuguesa-seduc-sp-2026": "SEDUC SP São Paulo Professor Língua Portuguesa Português Letras PEFM FGV Secretaria da Educação", "professor-fisica-seduc-sp-2026": "SEDUC SP São Paulo Professor Física FGV PEFM Secretaria da Educação Professor de Ensino Fundamental e Médio concurso estadual", "professor-ingles-seduc-sp-2026": "SEDUC SP São Paulo Professor Língua Inglesa Inglês FGV PEFM Secretaria da Educação Professor de Ensino Fundamental e Médio concurso estadual", "professor-ciencias-seduc-sp-2026": "SEDUC SP São Paulo Professor Ciências Biologia Química Física FGV PEFM Secretaria da Educação Professor de Ensino Fundamental e Médio concurso estadual", "professor-seduc-sp-2026": "SEDUC SP São Paulo Professor PEFM FGV Gestão de Sala de Aula Prova Prática Discursiva", "professor-seduc-ma-2026": "SEDUC MA Maranhão Professor Concurso Unificado do Maranhão FCC SEAD Supervisão Escolar", "gcm-angra-dos-reis-2026": "GM GCM Angra dos Reis Guarda Civil Municipal Rio de Janeiro RJ IDIB GCMAR", "gm-maraba-2026": "GCM GM Marabá Maraba Guarda Municipal Pará PA Fadesp", "gm-balneario-camboriu-2026": "GCM GM BC Balneário Camboriú Balneario Guarda Municipal SC Santa Catarina FURB Itapema",
    "gcm-salvador-2026": "GM Salvador Guarda Municipal", "gm-sao-goncalo-2026": "GCM São Gonçalo Guarda Municipal",
    "gcm-santana-2026": "GM Santana Guarda Municipal", "gm-campinas-2026": "GCM Campinas Guarda Civil Municipal Campinas SP Vunesp", "escrevente-tjsp-2026": "TJ SP Tribunal de Justiça",
    "tecnico-defensoria-dpe-pb-2026": "DPEPB Defensoria Pública", "assistente-tecnico-dpe-am-2026": "DPEAM DPE-AM DPE AM Defensoria Pública Amazonas Manaus Assistente Técnico Administrativo Servidores Auxiliares FCC", "ifg-assistente-administracao-2026": "IFG Instituto Federal de Goiás IFG GO Assistente em Administração Técnico-Administrativo em Educação TAE AOCP", "enem-2027": "ENEM 2027 Exame Nacional do Ensino Médio Inep vestibular redação nota 1000 TRI Linguagens Humanas Natureza Matemática SISU ProUni", "trt4-tecnico-administrativo-2026": "TRT TRT4 TRT-4 Tribunal Regional do Trabalho 4ª Região Rio Grande do Sul Porto Alegre Técnico Judiciário Administrativo FCC", "inss-tecnico-seguro-social-2026": "INSS Instituto Nacional do Seguro Social Técnico do Seguro Social Previdência Previdenciário Cebraspe Cespe concurso nacional", "tecnico-bancario-banestes-2026": "Banco Banestes ES",
    "recenseador-ibge-2026": "Censo Recenseador", "ufba-assistente-2026": "UFBA Universidade Federal da Bahia",
}
SITE = json.loads((RAIZ / "_config" / "site.json").read_text(encoding="utf-8"))


def pedido_html():
    """Bloco "Não achou a sua apostila? Peça para a ESCUDO" (home e páginas de carreira e estado).
    Com "pedido_url" no site.json (App da Web do Apps Script "Pedidos de apostila ESCUDO"), o site envia direto:
    o pedido vai para a planilha e para o e-mail do Mateus. Sem ele, o site.js abre um e-mail pronto."""
    return f"""<aside class="pedido" id="pedir" aria-labelledby="t-pedido" data-pedido data-email="{e(SITE.get('email', ''))}" data-endpoint="{e(SITE.get('pedido_url', ''))}">
      <h3 id="t-pedido">Não achou a sua apostila?</h3>
      <p>Peça para a ESCUDO. Diga o concurso e o cargo: se tiver edital publicado ou previsto, a gente avalia montar o curso e te avisa quando sair.</p>
      <form class="pedido-form" data-pedido-form>
        <label>Concurso <input name="concurso" required maxlength="80" placeholder="Ex.: PM-MG, Prefeitura de Campinas" autocomplete="off" data-pedido-concurso></label>
        <label>Cargo <input name="cargo" maxlength="80" placeholder="Ex.: Soldado, Agente Administrativo" autocomplete="off"></label>
        <label>Seu e-mail ou WhatsApp, para avisarmos <input name="contato" maxlength="120" placeholder="Opcional" autocomplete="email"></label>
        <label class="pedido-isca" aria-hidden="true">Não preencha <input name="site_url" tabindex="-1" autocomplete="off"></label>
        <button class="btn" type="submit">Pedir a minha apostila</button>
      </form>
      <p class="pedido-alt">Se preferir, mande no Instagram <a href="https://ig.me/m/escudoconcursos" data-goatcounter-click="pedido-instagram" data-goatcounter-title="pedido-instagram">@escudoconcursos</a>.</p>
    </aside>"""


UF_NOME = {"AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "BA": "Bahia", "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás",
           "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PE": "Pernambuco", "PR": "Paraná", "RJ": "Rio de Janeiro",
           "RO": "Rondônia", "SC": "Santa Catarina", "SP": "São Paulo", "BR": "Brasil nacional"}
FUSO = dt.timezone(dt.timedelta(hours=-3))
HOJE = dt.datetime.now(FUSO).date()
e = lambda s: html.escape(str(s), quote=True)


def d(s):
    return dt.date.fromisoformat(s)


SEM_DATA = "2099-12-31"  # curso sem prova marcada nunca sai da vitrine


def ddmm(s, ano=False):
    x = d(s)
    return x.strftime("%d/%m/%Y" if ano else "%d/%m")


def eventos(p):
    """Prazos do curso em ordem: o primeiro que ainda não passou é o que aparece no selo."""
    ev = []
    c = p.get("cupom")
    if c and p.get("prevenda"):  # pré-venda (22/11/2026): sem data, vale até sair o edital
        ev.append({"tipo": "prevenda", "data": SEM_DATA})
    elif c:
        ev.append({"tipo": "cupom", "data": c["ate"]})
    if p.get("inscricoes_ate"):
        ev.append({"tipo": "inscricoes", "data": p["inscricoes_ate"]})
    if p.get("prova"):
        ev.append({"tipo": "prova", "data": p["prova"]})
    else:  # sem edital novo (ex.: Polícia Penal/PR): o cartão não some e o selo diz "Edital previsto"
        ev.append({"tipo": "previsto", "data": SEM_DATA})
    return sorted(ev, key=lambda x: (x["data"], x["tipo"] not in ("cupom", "prevenda")))


def selo(p):
    """Mesmo texto que o site.js monta (manter os dois iguais)."""
    ev = [x for x in eventos(p) if d(x["data"]) >= HOJE]
    if not ev:
        return None, "", False
    x = ev[0]
    juntos = x["tipo"] == "cupom" and any(y["tipo"] == "inscricoes" and y["data"] == x["data"] for y in ev)
    txt = {"cupom": "Cupom e inscrições até %s" if juntos else "Cupom até %s",
           "inscricoes": "Inscrições até %s", "prova": "Prova em %s", "previsto": "Edital previsto",
           "prevenda": "Pré-venda até sair o edital"}[x["tipo"]]
    if x["tipo"] not in ("previsto", "prevenda"):
        txt = txt % ddmm(x["data"])
    faltam = (d(x["data"]) - HOJE).days
    if faltam <= 7 and x["tipo"] not in ("previsto", "prevenda"):
        txt += " · último dia" if faltam == 0 else " · faltam %d dia%s" % (faltam, "s" if faltam > 1 else "")
    return x["data"], txt, faltam <= 7


def brl(v):
    """Preço em reais: inteiro sem centavos (47), com centavos em vírgula (59,90)."""
    return v if isinstance(v, int) else ("%.2f" % v).replace(".", ",")


def cartao(p):
    chave, txt, urgente = selo(p)
    c = p.get("cupom")
    ev = json.dumps(eventos(p), ensure_ascii=False, separators=(",", ":"))
    brasao = ('<img class="tag-orgao" src="%s" width="61" height="80" alt="">' % e(p["brasao"])) if p.get("brasao") else ""
    prova = ("Prova %s %s" % ("provável em" if p.get("prova_provavel") else "em", ddmm(p["prova"], True))) if (p.get("prova") and p["prova"] != SEM_DATA) else "Prova: aguardando o edital novo"
    itens = "".join("<li>%s</li>" % e(i) for i in p["itens"]) + "<li>%s</li>" % prova
    if c and p.get("prevenda"):
        valor = ('<p class="valor" data-cupom-ate="%sT23:59:59-03:00">De <s>R$ %s</s> por R$ %s na pré-venda (cupom %s)</p>\n'
                 '          <p class="valor" data-sem-cupom hidden>R$ %s</p>' % (c["ate"], brl(p["preco"]), brl(c["preco"]), e(c["codigo"]), brl(p["preco"])))
    elif c and d(c["ate"]) >= HOJE:
        valor = ('<p class="valor" data-cupom-ate="%sT23:59:59-03:00">De <s>R$ %s</s> por R$ %s com o cupom %s</p>\n'
                 '          <p class="valor" data-sem-cupom hidden>R$ %s</p>' % (c["ate"], brl(p["preco"]), brl(c["preco"]), e(c["codigo"]), brl(p["preco"])))
    else:
        valor = '<p class="valor">R$ %s</p>' % (p['preco'] if isinstance(p['preco'], int) else ('%.2f' % p['preco']).replace('.', ','))
    externo = p["link"].startswith("http")
    n = NOMES.get(p["id"], {})
    busca = " ".join(x for x in [p["titulo"], p["tag"], n.get("sigla", ""), re.sub(r"[\s/-]", "", n.get("sigla", "")), n.get("cargo", ""), n.get("uf", ""),
                                 UF_NOME.get(n.get("uf", ""), ""), CARREIRAS.get(p["carreira"], ""), APELIDOS.get(p["id"], "")] if x)
    return f"""      <li class="produto {e(p['tema'])}" data-oferta data-carreira="{e(p['carreira'])}" data-busca="{e(busca)}" data-eventos='{e(ev)}'>
        <a class="capa" href="{e(p['link'])}" tabindex="-1" aria-hidden="true"><img src="{e(p['imagem'])}" width="560" height="560" loading="lazy" alt="{e(p.get('alt', ''))}"></a>
        <div class="corpo">
          <p class="selo{' urgente' if urgente else ''}" data-selo>{e(txt)}</p>
          <p class="tag">{brasao}{e(p['tag'])}</p>
          <h3>{e(p['titulo'])}</h3>
          <ul>{itens}</ul>
          <p class="carreira-rotulo">{e(CARREIRAS[p['carreira']])}</p>
          {valor}
          <a class="btn{' btn-ouro' if externo else ''}" href="{e(p['link'])}" aria-label="{e(p['botao'] + ': ' + p['titulo'] + ', ' + p['tag'])}">{e(p['botao'])}</a>
        </div>
      </li>""", chave


# Bloco "Em destaque" no topo da vitrine (23/11/2026, pedido do Mateus: dar destaque aos cursos válidos que ainda
# não venderam). A lista vem de _config/destaque.json (medida na planilha da automação). Mostra 8 por visita,
# em rodízio diário no navegador; todos ficam no HTML para o Google. Curso com prova passada não entra.
def destaque_html():
    arq = RAIZ / "_config" / "destaque.json"
    if not arq.exists():
        return ""
    ids = json.loads(arq.read_text(encoding="utf-8")).get("cursos", [])
    por_id = {p["id"]: p for p in DADOS["produtos"]}
    lista = [por_id[i] for i in ids if i in por_id and (not por_id[i].get("prova") or d(por_id[i]["prova"]) >= HOJE)]
    if not lista:
        return ""

    def prioridade(p):
        ins = p.get("inscricoes_ate")
        aberto = 0 if ins and d(ins) >= HOJE else (1 if p.get("prova") and p["prova"] != SEM_DATA else 2)
        return (aberto, ins or p.get("prova") or SEM_DATA)

    lista.sort(key=prioridade)
    itens = []
    for i, p in enumerate(lista):
        _, txt, _ = selo(p)
        c = p.get("cupom")
        if c and (p.get("prevenda") or d(c["ate"]) >= HOJE):
            preco = "R$ %s com o cupom %s" % (brl(c["preco"]), e(c["codigo"]))
        else:
            preco = "R$ %s" % brl(p["preco"])
        itens.append(
            '<li class="%s" data-ordem="%d"%s><a href="%s" data-goatcounter-click="destaque-home" data-goatcounter-title="destaque-home-%s">'
            '<img src="%s" width="76" height="76" loading="lazy" alt=""><span><b>%s</b><strong>%s</strong><em>%s</em><i>%s</i></span></a></li>'
            % (e(p["tema"]), i, "" if i < 8 else " hidden", e(p["link"]), e(p["id"]), e(p["imagem"]), e(p["tag"]), e(p["titulo"]), e(txt or "Edital previsto"), preco))
    return ('<div class="vitrine-destaque" aria-labelledby="t-destaque"><p class="kicker" id="t-destaque">Em destaque</p>'
            '<p class="vd-sub">Cursos completos, prontos para baixar, que muita gente ainda não conhece. Começar antes da concorrência faz diferença.</p>'
            '<ul data-destaque>%s</ul></div>'
            '<style>.vitrine-destaque{margin:6px 0 26px}.vd-sub{margin:4px 0 12px;color:var(--navy2)}'
            '.vitrine-destaque ul{list-style:none;padding:0;margin:0;display:grid;gap:10px;grid-template-columns:repeat(auto-fill,minmax(270px,1fr))}'
            '.vitrine-destaque a{display:flex;gap:12px;align-items:center;padding:10px;border:1px solid rgba(201,162,75,.6);border-radius:10px;background:#fff;color:var(--navy);text-decoration:none;height:100%%}'
            '.vitrine-destaque a:hover{box-shadow:0 4px 14px rgba(11,26,51,.14)}.vitrine-destaque img{width:76px;height:76px;border-radius:8px;flex:none;object-fit:cover}'
            '.vitrine-destaque span{display:flex;flex-direction:column;gap:2px;min-width:0}.vitrine-destaque b{font-size:.78rem;letter-spacing:.04em;text-transform:uppercase;color:#7a5c17}'
            '.vitrine-destaque strong{font-size:.98rem;line-height:1.25}.vitrine-destaque em{font-style:normal;font-size:.86rem;color:var(--navy3)}'
            '.vitrine-destaque i{font-style:normal;font-weight:700;font-size:.9rem}</style>'
            '<script>(function(){var u=document.querySelector("[data-destaque]");if(!u)return;var h=new Date();h.setHours(0,0,0,0);'
            'var li=[].slice.call(u.children);var n=li.length,k=window.innerWidth<700?4:8;if(n<=k)return;var dia=Math.floor(h.getTime()/864e5);'
            'var ini=(dia*k)%%n;li.forEach(function(x,i){var p=(i-ini+n)%%n;x.hidden=p>=k;x.style.order=p;});u.style.display="grid";})();</script>'
            ) % "".join(itens)


abertos = [p for p in DADOS["produtos"] if not p.get("prova") or d(p["prova"]) >= HOJE]
cartoes = sorted((cartao(p) for p in abertos), key=lambda t: t[1])
usadas = [k for k in CARREIRAS if any(p["carreira"] == k for p in abertos)]
botoes = ['<button type="button" class="chip" data-filtro="" aria-pressed="true">Todas <span data-conta="">%d</span></button>' % len(abertos)]
botoes += ['<button type="button" class="chip" data-filtro="%s" aria-pressed="false">%s <span data-conta="%s">%d</span></button>'
           % (k, e(CARREIRAS[k]), k, sum(p["carreira"] == k for p in abertos)) for k in usadas]

bloco = """<!-- vitrine:inicio (gerado por _config/vitrine.py a partir de produtos.json; não editar à mão) -->
    %s
    <div class="busca" data-busca-caixa hidden>
      <label for="busca-curso">Busque o seu concurso</label>
      <input id="busca-curso" type="search" placeholder="Ex.: PM-SP, Recife, Bahia, Soldado" autocomplete="off" enterkeyhint="search" data-busca-campo>
    </div>
    <div class="filtros" role="group" aria-label="Filtrar cursos por carreira" data-filtros hidden>
      %s
    </div>
    <p class="vitrine-info" data-vitrine-info aria-live="polite">Ordenados pelo prazo mais próximo: cupom, inscrições ou prova.</p>
    <ul class="produtos" data-vitrine>
%s
    </ul>
    <p class="vitrine-vazia" data-sem-resultado hidden>Nenhum curso com esse nome. Tente a sigla (PM-SP), a cidade ou o estado, ou <a href="#pedir" data-pedir-busca>peça este curso para a ESCUDO</a>.</p>
    <p class="vitrine-vazia" data-vazia%s>Novos cursos em breve. Acompanhe no Instagram <a href="https://www.instagram.com/escudoconcursos/">@escudoconcursos</a>.</p>
    %s
    <!-- vitrine:fim -->""" % (destaque_html(), "\n      ".join(botoes), "\n".join(t[0] for t in cartoes), "" if not abertos else " hidden", pedido_html())

idx = RAIZ / "index.html"
s = idx.read_text(encoding="utf-8")
novo, n = re.subn(r"<!-- vitrine:inicio.*?<!-- vitrine:fim -->", lambda m: bloco, s, flags=re.S)
if n != 1:
    raise SystemExit("index.html sem os marcadores <!-- vitrine:inicio --> e <!-- vitrine:fim -->")
idx.write_text(novo, encoding="utf-8")
print("ok index.html: %d curso(s) aberto(s), carreiras: %s" % (len(abertos), ", ".join(usadas) or "nenhuma"))

for p in DADOS["produtos"]:
    if not p.get("atalho"):
        continue
    destino = p["link"] if p["link"].startswith("http") else "../" + p["link"]
    pasta = RAIZ / p["atalho"]
    pasta.mkdir(exist_ok=True)
    (pasta / "index.html").write_text(f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>ESCUDO Concursos: {e(p['titulo'])}</title>
<meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={e(destino)}">
<link rel="canonical" href="{e(destino)}"></head>
<body><p><a href="{e(destino)}">{e(p['titulo'])}, {e(p['tag'])}</a></p></body></html>
""", encoding="utf-8")
    print("ok atalho /%s/ -> %s" % (p["atalho"], destino))

# Faixa "Inscrições terminando" no topo da home (23/11/2026, pedido do Mateus: destacar os concursos
# com inscrição perto do fim, que é quando o curso vende). Até 6 cursos: os de DESTAQUE_PRAZOS e os da última semana.
# Cursos que mais vendem: entram na faixa desde 45 dias antes do fim da inscrição (os outros, só na última semana).
DESTAQUE_PRAZOS = {"escrevente-tjsp-2026", "pcpe-agente-2026", "pcpe-escrivao-2026", "assistente-tecnico-dpe-am-2026"}


def faixa_prazos():
    abertas = [p for p in DADOS["produtos"] if p.get("inscricoes_ate") and d(p["inscricoes_ate"]) >= HOJE]
    fixos = [p for p in abertas if p["id"] in DESTAQUE_PRAZOS and d(p["inscricoes_ate"]) <= HOJE + dt.timedelta(days=45)]
    perto = [p for p in abertas if p not in fixos and d(p["inscricoes_ate"]) <= HOJE + dt.timedelta(days=7)]
    lista = sorted(fixos + sorted(perto, key=lambda p: p["inscricoes_ate"])[:max(0, 6 - len(fixos))], key=lambda p: p["inscricoes_ate"])
    if not lista:
        return "<!-- prazos:inicio --><!-- prazos:fim -->"
    itens = []
    for p in lista:
        itens.append('<li data-ate="%s"><a href="%s" data-goatcounter-click="prazo-home" data-goatcounter-title="prazo-home-%s"><b>%s</b> %s · inscrições até %s</a></li>'
                     % (p["inscricoes_ate"], e(p["link"]), e(p["id"]), e(p["tag"]), e(p["titulo"]), ddmm(p["inscricoes_ate"])))
    return ('<!-- prazos:inicio (gerado por _config/vitrine.py) --><div class="prazos-home"><p class="kicker">Inscrições terminando</p>'
            '<ul>%s</ul></div><style>.prazos-home{margin-top:22px}.prazos-home ul{list-style:none;padding:0;margin:8px 0 0;display:grid;gap:8px}'
            '.prazos-home a{display:block;padding:10px 14px;border:1px solid rgba(212,175,90,.55);border-radius:8px;color:inherit;text-decoration:none}'
            '.prazos-home a:hover{background:rgba(212,175,90,.12)}.prazos-home b{color:#d4af5a;margin-right:6px}</style>'
            '<script>(function(){var h=new Date();h.setHours(0,0,0,0);document.querySelectorAll(".prazos-home li[data-ate]").forEach(function(li){'
            'if(new Date(li.dataset.ate+"T23:59:59-03:00")<h)li.remove();});var u=document.querySelector(".prazos-home ul");'
            'if(u&&!u.children.length)u.parentNode.remove();})();</script><!-- prazos:fim -->') % "".join(itens)


s = idx.read_text(encoding="utf-8")
faixa = faixa_prazos()
if "<!-- prazos:inicio" in s:
    s = re.sub(r"<!-- prazos:inicio.*?<!-- prazos:fim -->", lambda m: faixa, s, flags=re.S)
else:
    s = s.replace('item por item, na ordem do conteúdo programático, com questões no estilo da banca e gabarito comentado.</p>',
                  'item por item, na ordem do conteúdo programático, com questões no estilo da banca e gabarito comentado.</p>\n    ' + faixa, 1)
idx.write_text(s, encoding="utf-8")
print("ok faixa de prazos na home")
