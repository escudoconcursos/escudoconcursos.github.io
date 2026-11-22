import json,re,html,sys
MAP={'8677641':'pmpe-soldado-2026','8679930':'gm-sao-goncalo-2026','8686161':'cbmpe-soldado-2026','8686196':'pmal-soldado-2026','8689498':'pcpe-agente-2026','8690337':'agente-educativo-aparecida-2026','8690363':'pedagogia-aparecida-2026','8692662':'gcm-santana-2026','8693880':'tecnico-enfermagem-porto-velho-2026','8693917':'assistente-semusa-porto-velho-2026','8695541':'professor-semed-porto-velho-2026','8796113':'soldado-pmsc-2026','8798104':'escrevente-tjsp-2026','8820157':'assistente-administrativo-contagem-2026','8822423':'tecnico-bancario-banestes-2026','8829173':'tecnico-defensoria-dpe-pb-2026','8839880':'agente-administrativo-curitiba-2026','8875953':'gcm-salvador-2026','8880024':'policial-penal-pe-2026','8886543':'cbm-al-soldado-2026','8899196':'pmesp-soldado-2026','8906942':'pcac-oficial-investigador-2026','8908158':'recenseador-ibge-2026','8926505':'pmmg-cfo-2027','8948400':'gm-campinas-2026','8971547':'trt4-tecnico-administrativo-2026','8992692':'pcpe-escrivao-2026','8994181':'gm-maraba-2026','9000796':'pmerj-cfo-2027','9003338':'cbmerj-cadete-2027','9004187':'gm-pedra-branca-do-amapari-2026','9010382':'gcm-angra-dos-reis-2026','9019567':'assistente-tecnico-sead-ma-2026','9020897':'professor-seduc-ma-2026','9021902':'supervisao-escolar-seduc-ma-2026','9022581':'professor-lingua-portuguesa-seduc-ma-2026','9023093':'professor-matematica-seduc-ma-2026','9028950':'professor-seduc-sp-2026','9029604':'professor-matematica-seduc-sp-2026','9030183':'professor-lingua-portuguesa-seduc-sp-2026','9030783':'professor-fisica-seduc-sp-2026','9031329':'professor-ciencias-seduc-sp-2026','9031767':'professor-ingles-seduc-sp-2026','9033043':'assistente-tecnico-dpe-am-2026'}
d=json.load(open('_config/produtos.json'));items=d if isinstance(d,list) else d.get('produtos',d);items=list(items.values()) if isinstance(items,dict) else items
P={p['id']:p for p in items}
def txt(s):
    s=re.sub(r'<script.*?</script>|<style.*?</style>|<form.*?</form>','',s,flags=re.S)
    s=re.sub(r'</(p|li|h\d|div|tr|summary|details)>','\n',s); s=re.sub(r'<br\s*/?>','\n',s)
    s=html.unescape(re.sub(r'<[^>]+>',' ',s)); s=re.sub(r'[ \t]+',' ',s); s=re.sub(r'\s*\n\s*','\n',s)
    return s.strip().replace('—',',').replace('–','-')
def sec(h,i):
    m=re.search(r'<section[^>]*aria-labelledby="t-%s"[^>]*>(.*?)</section>'%i,h,re.S) or re.search(r'id="t-%s"[^>]*>(.*?)(?=<section|<footer)'%i,h,re.S)
    if not m: return ''
    return txt(m.group(1))
def cut(s,n):
    s=s.strip()
    if len(s)<=n: return s
    s=s[:n]; k=max(s.rfind('. '),s.rfind('\n'))
    return s[:k+1].strip() if k>n*0.5 else s[:n-3]+'...'
out={}
for hid,pid in MAP.items():
    p=P[pid]; h=open(pid+'/index.html').read()
    nome=p['titulo']; tag=p['tag']; banca=tag.split('·')[-1].strip()
    c=p.get('cupom') or {}; preco=str(p['preco']).replace('.',',')
    oferta=f"R$ {preco}"+(f", ou R$ {str(c['preco']).replace('.',',')} com o cupom {c['codigo']}"+(f" até {c['ate'][8:10]}/{c['ate'][5:7]}/{c['ate'][:4]}" if c.get('ate') else '') if c.get('codigo') else '')
    itens='; '.join(p['itens'])
    rap=sec(h,'rapida'); conc=sec(h,'concurso'); fmt=sec(h,'formato'); rec=sec(h,'recebe'); mod=sec(h,'modulos'); sim=sec(h,'simulados'); quem=sec(h,'quem'); lib=sec(h,'liberacao'); faq=sec(h,'faq')
    f={}
    f['p1']=cut(f"Curso em PDF ESCUDO para {nome} ({tag}), montado a partir do edital, item por item: {itens}. É teoria direta ao ponto, questões no estilo da banca com gabarito comentado e simulados no formato da prova. Preço: {oferta}. Acesso imediato pela Hotmart e garantia de 7 dias.\n"+rap,1000)
    f['p2']=cut(f"Resolve o problema de quem precisa estudar exatamente o que o edital de {nome} cobra, sem perder tempo com material genérico ou desatualizado. O curso organiza todo o conteúdo programático em capítulos, com a lei na versão em vigor e questões no padrão da banca ({banca}), para o aluno chegar à prova tendo visto e treinado cada item.\n"+conc,1000)
    f['p3']=cut(f"Para quem vai fazer o concurso de {nome} e quer um material completo, objetivo e barato para estudar pelo edital, inclusive quem está começando ou tem pouco tempo e prefere ler e resolver questões a assistir videoaulas.\n"+quem,1000)
    f['p4']=cut(f"Não é a melhor opção para quem quer videoaulas (o curso é 100% em PDF, sem vídeo), para quem precisa de correção individual de redação ou acompanhamento de professor, e para quem vai fazer outro concurso ou outro cargo: o material segue só o edital de {nome}. Também não serve como material impresso enviado pelo correio: é produto digital.",1000)
    f['p5']=cut("Na prática o aluno estuda capítulo por capítulo: cada um traz a teoria do item do edital e, no fim, questões no estilo da banca com gabarito comentado. Depois treina com os simulados no formato da prova.\n"+fmt,1000)
    f['p6']=cut("O acesso é imediato depois da confirmação do pagamento, pela área de membros da Hotmart (no navegador ou no app da Hotmart). Os capítulos ficam disponíveis para leitura online.\n"+lib,1000)
    f['o']=cut("Perguntas que mais aparecem antes da compra e como respondemos:\n"+faq+f"\nQuanto custa? {oferta}, pagamento único pela Hotmart (Pix, boleto ou cartão). Tem garantia? Sim, 7 dias pela Hotmart com reembolso integral.",6000)
    f['d']=cut(f"O curso é feito para o edital de {nome}, não é apostila genérica adaptada. Cada item do conteúdo programático vira pelo menos um capítulo, e o que não está no edital fica de fora. A legislação é conferida na fonte oficial, na versão vigente, incluindo leis estaduais e municipais quando o edital cobra. As questões são inéditas, escritas no padrão da banca ({banca}), com gabarito comentado, e os simulados seguem o formato da prova. Gabaritos e números do edital são conferidos antes da publicação e o curso é atualizado quando sai retificação.\nQuem faz: o professor e autor Mateus Vazzoller, que trabalha com concursos desde 2012, é formado em Direito e foi editor dos livros da AlfaCon, uma das maiores preparatórias do país.\nE o preço é baixo: {oferta}, contra centenas de reais de um cursinho.\n"+rec,6000)
    f['c']=cut(mod+"\n"+sim,6000)
    f['r']=cut(f"O curso de {nome} é novo, feito para o edital atual, e a prova ainda não aconteceu, então não temos aprovados deste concurso para mostrar e não prometemos aprovação. O que o aluno ganha ao aplicar o conteúdo: sabe exatamente o que estudar, cobre todo o edital em um material só, treina com questões no estilo da banca e chega à prova testado pelos simulados, sabendo administrar o tempo e conhecendo a nota de corte. O autor tem a experiência de editor dos livros da AlfaCon, preparatória que divulga mais de 308 mil alunos aprovados.",6000)
    out[hid]=f
json.dump(out,open(sys.argv[1],'w'),ensure_ascii=False)
print(len(out)); k='8798104'; [print(x,len(v),'|',v[:300].replace('\n',' / ')) for x,v in out[k].items()]
