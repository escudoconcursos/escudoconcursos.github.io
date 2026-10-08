# -*- coding: utf-8 -*-
"""Gera favicon (ico/png) e as imagens Open Graph 1200x630 do site com o Playwright.
Uso: PYTHONIOENCODING=utf-8 python 07-site/_config/gerar_imagens.py [og-pmpe-soldado-2026.jpg og-gm-sao-goncalo-2026.jpg ...]
Com nomes, gera só essas imagens Open Graph (sem favicon).
"""
import io, pathlib, sys
from PIL import Image
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parent.parent
IMG = RAIZ / "assets" / "img"
F = (RAIZ / "assets" / "fonts").as_uri()
ICONE = (IMG / "escudo-icone.svg").read_text(encoding="utf-8")

FONTES = """
@font-face{font-family:S;src:url('%(f)s/SairaCondensed-Black.woff2');font-weight:900}
@font-face{font-family:S;src:url('%(f)s/SairaCondensed-ExtraBold.woff2');font-weight:800}
@font-face{font-family:S;src:url('%(f)s/SairaCondensed-Bold.woff2');font-weight:700}
@font-face{font-family:A;src:url('%(f)s/Archivo-SemiBold.woff2');font-weight:600}
""" % {"f": F}

BASE = """<!doctype html><meta charset="utf-8"><style>%s
*{margin:0;box-sizing:border-box}
body{width:1200px;height:630px;overflow:hidden;background:#0B1A33;color:#F5F1E6;font-family:S;position:relative}
.bg{position:absolute;inset:0;background:radial-gradient(900px 500px at 95%% -20%%,#1C3A66,transparent 65%%),radial-gradient(700px 420px at -10%% 120%%,#13294D,transparent 60%%)}
.wm{position:absolute;right:-60px;top:-20px;width:560px;opacity:.07}
.wm svg{width:100%%;height:auto}
.logo{position:absolute;left:72px;top:58px;display:flex;align-items:center;gap:14px}
.logo svg{width:44px;height:auto}
.logo b{display:block;font-weight:800;font-size:38px;letter-spacing:.2em;line-height:1}
.logo b i{font-style:normal;color:#C9A24B}
.logo small{display:block;font-weight:700;font-size:14px;letter-spacing:.42em;color:#9DB0CC;margin-top:4px}
.k{font-weight:800;letter-spacing:.22em;text-transform:uppercase;font-size:26px}
h1{font-weight:900;text-transform:uppercase;line-height:.95;letter-spacing:.005em}
.r{height:6px;width:110px;border-radius:3px}
.sub{font-weight:700;text-transform:uppercase;letter-spacing:.09em;color:#9DB0CC;font-size:27px;line-height:1.3}
.pe{position:absolute;left:72px;bottom:46px;right:72px;display:flex;justify-content:space-between;font-weight:800;font-size:24px;letter-spacing:.14em;text-transform:uppercase}
</style><div class="bg"></div><div class="wm">%s</div>
<div class="logo">%s<span><b>ESCU<i>D</i>O</b><small>CONCURSOS</small></span></div>
""" % (FONTES, ICONE, ICONE)

def policial(pasta, brasao, capa, selo, cargo, h1a, h1b, sub, aviso, em, regua, petri):
    """OG do tema policial (fundo tático, giroflex, brasão como selo do concurso e a capa)."""
    return BASE + """<style>
/* tema policial, como os posts e a página: fundo tático, giroflex e o brasão como selo do concurso */
body{background:#060B16}
.bg{background:radial-gradient(560px 320px at 0%% 0%%,rgba(229,57,53,.26),transparent 65%%),radial-gradient(560px 320px at 100%% 0%%,rgba(37,99,235,.26),transparent 65%%),
  linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px) 0 0/48px 48px,linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px) 0 0/48px 48px,
  linear-gradient(180deg,#081023,#050A14)}
.wm{opacity:0}
.giro{position:absolute;left:0;right:0;top:0;height:9px;background:linear-gradient(90deg,#E53935 0 47%%,#111827 47%% 53%%,#2563EB 53%% 100%%);
  -webkit-mask-image:repeating-linear-gradient(90deg,#000 0 58px,transparent 58px 65px)}
.ins{position:absolute;right:-90px;bottom:-120px;width:520px;opacity:.06}
.logo{top:32px}
.selo{position:absolute;left:72px;top:126px;display:flex;align-items:center;gap:20px}
.selo img{height:126px;filter:drop-shadow(0 10px 16px rgba(0,0,0,.6))}
.selo p{border-left:3px solid #C9A24B;padding-left:16px;text-transform:uppercase;line-height:1.05}
.selo span{display:block;font-weight:800;letter-spacing:.3em;font-size:18px;color:#C9A24B}
.selo b{display:block;font-weight:900;font-size:50px;margin:4px 0 2px}
.selo b+span{color:#B7C4D8;letter-spacing:.24em;font-size:19px}
.selo i{display:block;height:6px;width:160px;margin-top:10px;background:linear-gradient(90deg,%s 0 33.3%%,%s 33.3%% 66.6%%,%s 66.6%%)}
.txt{position:absolute;left:72px;top:282px;width:720px}
h1{font-size:72px;white-space:nowrap;text-shadow:0 4px 0 rgba(0,0,0,.45)}
h1 em{font-style:normal;color:%s;display:block}
.r{width:120px;height:6px;border-radius:0;background:linear-gradient(90deg,%s 0 62%%,transparent 62%% 68%%,#C9A24B 68%%);margin:20px 0 18px}
.sub{font-size:25px}
.av{position:absolute;left:72px;bottom:92px;font-family:A;font-weight:600;font-size:19px;color:#93A4BF}
.capa{position:absolute;right:86px;top:84px;width:292px;transform:rotate(-3deg);border-radius:6px;box-shadow:0 30px 60px -16px rgba(0,0,0,.85),0 0 0 2px rgba(201,162,75,.45)}
.pe span:first-child{color:#F5F1E6;letter-spacing:.04em;text-transform:none}
.pe span:last-child{color:#C9A24B}.pe b{color:#F5F1E6}
</style>
<div class="giro"></div><img class="ins" src="%s">
<div class="selo"><img src="%s"><p><span>Concurso</span><b>%s</b><span>%s</span><i></i></p></div>
<div class="txt"><h1>%s<em>%s</em></h1><div class="r"></div>
<p class="sub">%s</p></div>
<p class="av">%s</p>
<img class="capa" src="%s">
<div class="pe"><span>@escudoconcursos</span><span>Material para o <b>SEU</b> edital</span></div>
""" % (petri[0], petri[1], petri[2], em, regua, (IMG / "insignia.svg").as_uri(), (IMG / pasta / brasao).as_uri(),
           selo, cargo, h1a, h1b, sub, aviso, (IMG / pasta / capa).as_uri())


PMPE = policial("pmpe", "brasao-pmpe.webp", "capa.webp", "PMPE 2026", "Soldado", "Soldado da", "PM/PE",
                "116 capítulos · 550 questões comentadas · 2 simulados", "Material independente, sem vínculo com a PMPE.",
                "#E25450", "#D9534F", ("#14924A", "#F4C21B", "#DC2B2B"))

GMSG = policial("sao-goncalo", "brasao-sao-goncalo.webp", "capa.webp", "GM São Gonçalo", "2026", "Guarda Municipal de", "São Gonçalo",
                "131 capítulos · 650 questões comentadas · 2 simulados",
                "Material independente, sem vínculo com a Guarda Municipal de São Gonçalo.",
                "#4F8FF7", "#3B82F6", ("#CF2B24", "#2F6FD0", "#018E5D"))


HOME = BASE + """<style>
.txt{position:absolute;left:72px;top:150px;width:900px}
.k{color:#E7C873}
h1{font-size:110px;margin:14px 0 0}
h1 em{font-style:normal;color:#E7C873}
.r{background:linear-gradient(90deg,#E7C873,#C9A24B);margin:28px 0 26px}
.pe span:first-child{color:#F5F1E6;letter-spacing:.04em;text-transform:none}.pe span:last-child{color:#9DB0CC}
</style>
<div class="txt"><p class="k">ESCUDO Concursos</p><h1>Material para<br>o <em>SEU</em> edital</h1><div class="r"></div>
<p class="sub">Cursos em PDF feitos a partir do edital, item por item</p></div>
<div class="pe"><span>@escudoconcursos</span><span>Questões no estilo da banca</span></div>
"""

FAV = """<!doctype html><style>*{margin:0}body{background:transparent}img{display:block;width:%dpx;height:%dpx}</style><img src="%s">"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1200, "height": 630})
    so = sys.argv[1:]
    for nome, doc in [("og-pmpe-soldado-2026.jpg", PMPE), ("og-gm-sao-goncalo-2026.jpg", GMSG), ("og-escudo.jpg", HOME)]:
        if so and nome not in so:
            continue
        tmp = RAIZ / "_config" / "_og.html"
        tmp.write_text(doc, encoding="utf-8")
        pg.goto(tmp.as_uri()); pg.wait_for_timeout(400)
        png = pg.screenshot()
        Image.open(io.BytesIO(png)).convert("RGB").save(IMG / nome, "JPEG", quality=86, optimize=True, progressive=True)
        tmp.unlink()
        print("ok", nome)
    if so:
        b.close()
        sys.exit(0)
    pg2 = b.new_page(viewport={"width": 512, "height": 512})
    tmp = RAIZ / "_config" / "_fav.html"
    tmp.write_text(FAV % (512, 512, (IMG / "favicon.svg").as_uri()), encoding="utf-8")
    pg2.goto(tmp.as_uri()); pg2.wait_for_timeout(200)
    grande = Image.open(io.BytesIO(pg2.screenshot(omit_background=True))).convert("RGBA")
    tmp.unlink()
    b.close()

grande.resize((180, 180), Image.LANCZOS).save(IMG / "apple-touch-icon.png", optimize=True)
grande.save(RAIZ / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
print("ok favicon.ico, apple-touch-icon.png")
