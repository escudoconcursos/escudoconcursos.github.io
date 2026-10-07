# -*- coding: utf-8 -*-
"""Gera favicon (ico/png) e as imagens Open Graph 1200x630 do site com o Playwright.
Uso: PYTHONIOENCODING=utf-8 python 07-site/_config/gerar_imagens.py
"""
import io, pathlib
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

PMPE = BASE + """<style>
.txt{position:absolute;left:72px;top:150px;width:700px}
.k{color:#FF8A80}
h1{font-size:82px;margin:14px 0 0;white-space:nowrap}
h1 em{font-style:normal;color:#D9534F;display:block}
.r{background:linear-gradient(90deg,#FF8A80,#D9534F);margin:26px 0 24px}
.capa{position:absolute;right:86px;top:70px;width:300px;transform:rotate(-3deg);border-radius:6px;box-shadow:0 30px 60px -16px rgba(0,0,0,.8),0 0 0 2px rgba(201,162,75,.45)}
.pe span:first-child{color:#F5F1E6;letter-spacing:.04em;text-transform:none}
.pe span:last-child{color:#D9534F}.pe b{color:#F5F1E6}
</style>
<div class="txt"><p class="k">PMPE 2026 · Curso em PDF</p><h1>Soldado da<em>PM de Pernambuco</em></h1><div class="r"></div>
<p class="sub">116 capítulos · 550 questões comentadas<br>Redação + 2 simulados · Instituto AOCP</p></div>
<img class="capa" src="%s">
<div class="pe"><span>@escudoconcursos</span><span>Material para o <b>SEU</b> edital</span></div>
""" % (IMG / "pmpe" / "capa.webp").as_uri()

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
    for nome, doc in [("og-pmpe-soldado-2026.jpg", PMPE), ("og-escudo.jpg", HOME)]:
        tmp = RAIZ / "_config" / "_og.html"
        tmp.write_text(doc, encoding="utf-8")
        pg.goto(tmp.as_uri()); pg.wait_for_timeout(400)
        png = pg.screenshot()
        Image.open(io.BytesIO(png)).convert("RGB").save(IMG / nome, "JPEG", quality=86, optimize=True, progressive=True)
        tmp.unlink()
        print("ok", nome)
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
