# -*- coding: utf-8 -*-
"""Capa 1200x630 dos posts do blog (og:image e imagem do topo), no padrão visual ESCUDO. 08/11/2026.

Chamado pelo blog.py. Precisa de: pip install pillow fonttools brotli
As fontes woff2 do site viram ttf em _config/.fontes/ (pasta ignorada pelo git) na primeira vez.
"""
import pathlib, textwrap

from PIL import Image, ImageDraw, ImageFont

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CACHE = RAIZ / "_config" / ".fontes"
NAVY, NAVY2 = (6, 11, 22), (14, 26, 51)
CREME, OURO, ROSA, CINZA = (246, 241, 230), (201, 162, 75), (255, 138, 178), (160, 172, 196)


def fonte(nome, tam):
    CACHE.mkdir(exist_ok=True)
    ttf = CACHE / (nome + ".ttf")
    if not ttf.exists():
        from fontTools.ttLib import TTFont
        f = TTFont(str(RAIZ / "assets" / "fonts" / (nome + ".woff2")))
        f.flavor = None
        f.save(str(ttf))
    return ImageFont.truetype(str(ttf), tam)


def quebra(draw, texto, f, largura):
    """Quebra o texto em linhas que cabem na largura."""
    palavras, linhas, atual = texto.split(), [], ""
    for p in palavras:
        teste = (atual + " " + p).strip()
        if draw.textlength(teste, font=f) <= largura:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def fundo_foto(im, foto):
    """Foto ocupando o lado direito, com degradê navy da esquerda para o texto ficar legível."""
    f = Image.open(foto).convert("RGB")
    alvo_w, alvo_h = 700, 630
    esc = max(alvo_w / f.width, alvo_h / f.height)
    f = f.resize((int(f.width * esc) + 1, int(f.height * esc) + 1), Image.LANCZOS)
    x0 = (f.width - alvo_w) // 2
    f = f.crop((x0, 0, x0 + alvo_w, alvo_h))
    im.paste(f, (1200 - alvo_w, 0))
    veu = Image.new("RGBA", (1200, 630))
    dv = ImageDraw.Draw(veu)
    for x in range(1200):
        if x < 560:
            a = 255
        elif x < 820:
            a = int(255 - (x - 560) / 260 * 215)
        else:
            a = 40
        dv.line([(x, 0), (x, 630)], fill=NAVY + (min(a, 255),))
    im.paste(veu, (0, 0), veu)


def gera(destino, titulo, selo, produto_img=None, destaque=None, foto=None):
    im = Image.new("RGB", (1200, 630), NAVY)
    d = ImageDraw.Draw(im)
    if foto and pathlib.Path(foto).exists():
        fundo_foto(im, foto)
        d = ImageDraw.Draw(im)
        produto_img = None
    largura_foto = 640 if foto and pathlib.Path(foto).exists() else None
    # fundo com leve degradê e grade (só sem foto)
    for y in (range(630) if not foto else []):
        t = y / 630
        d.line([(0, y), (1200, y)], fill=tuple(int(NAVY[i] + (NAVY2[i] - NAVY[i]) * t) for i in range(3)))
    for x in (range(0, 1200, 60) if not foto else []):
        d.line([(x, 0), (x, 630)], fill=(18, 30, 52))
    for y in (range(0, 630, 60) if not foto else []):
        d.line([(0, y), (1200, y)], fill=(18, 30, 52))
    d.rectangle([0, 0, 1200, 8], fill=OURO)
    logo = Image.open(RAIZ / "_config" / "blog-logo.png").convert("RGB")
    im.paste(logo, (66, 36))
    largura = largura_foto or 1068
    if produto_img and pathlib.Path(produto_img).exists():
        p = Image.open(produto_img).convert("RGBA")
        p.thumbnail((330, 440))
        im.paste(p, (1200 - p.width - 60, 630 - p.height - 70), p)
        largura = 1200 - p.width - 60 - 66 - 40
    # selo
    fs = fonte("SairaCondensed-Bold", 30)
    selo = selo.upper()
    w = d.textlength(selo, font=fs)
    d.rounded_rectangle([66, 140, 66 + w + 36, 186], radius=23, fill=OURO)
    d.text((84, 144), selo, font=fs, fill=NAVY)
    # título
    for tam in (78, 70, 62, 56, 50):
        ft = fonte("SairaCondensed-Black", tam)
        linhas = quebra(d, titulo.upper(), ft, largura)
        if len(linhas) <= 4:
            break
    y = 212
    for i, l in enumerate(linhas):
        x = 66
        marcadas = set(destaque.upper().split()) if destaque else set()
        for pal in l.split():
            d.text((x, y), pal, font=ft, fill=ROSA if pal.strip(":,.") in marcadas else CREME)
            x += d.textlength(pal + " ", font=ft)
        y += int(tam * 1.02)
    d.rectangle([66, y + 26, 156, y + 32], fill=ROSA)
    d.rectangle([168, y + 26, 214, y + 32], fill=OURO)
    fr = fonte("Archivo-SemiBold", 24)
    d.text((66, 572), "escudoconcursos.com.br/noticias  ·  por Mateus Vazzoller", font=fr, fill=CINZA)
    destino = pathlib.Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    im.save(destino, "JPEG", quality=86, optimize=True, progressive=True)
    return destino


def gera_story(destino, titulo, selo, destaque=None, foto=None, chamada="Toque no link e leia a notícia completa"):
    """Arte de story 1080x1920 do post (Instagram/WhatsApp), no mesmo padrão da capa. 10/11/2026."""
    W, H = 1080, 1920
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(NAVY[i] + (NAVY2[i] - NAVY[i]) * t) for i in range(3)))
    topo_foto = 0
    if foto and pathlib.Path(foto).exists():
        f = Image.open(foto).convert("RGB")
        alvo_h = 900
        esc = max(W / f.width, alvo_h / f.height)
        f = f.resize((int(f.width * esc) + 1, int(f.height * esc) + 1), Image.LANCZOS)
        x0 = (f.width - W) // 2
        im.paste(f.crop((x0, 0, x0 + W, alvo_h)), (0, 0))
        veu = Image.new("RGBA", (W, alvo_h))
        dv = ImageDraw.Draw(veu)
        for y in range(alvo_h):
            a = 60 if y < 520 else min(255, int(60 + (y - 520) / 380 * 195))
            dv.line([(0, y), (W, y)], fill=NAVY + (a,))
        im.paste(veu, (0, 0), veu)
        topo_foto = 760
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 10], fill=OURO)
    logo = Image.open(RAIZ / "_config" / "blog-logo.png").convert("RGB")
    im.paste(logo, (72, 90))
    y = max(topo_foto, 560)
    fs = fonte("SairaCondensed-Bold", 44)
    selo = selo.upper()
    w = d.textlength(selo, font=fs)
    d.rounded_rectangle([72, y, 72 + w + 50, y + 66], radius=33, fill=OURO)
    d.text((97, y + 6), selo, font=fs, fill=NAVY)
    y += 110
    marcadas = set(destaque.upper().split()) if destaque else set()
    for tam in (120, 108, 96, 86, 76):
        ft = fonte("SairaCondensed-Black", tam)
        linhas = quebra(d, titulo.upper(), ft, W - 144)
        if len(linhas) <= 5:
            break
    for l in linhas:
        x = 72
        for pal in l.split():
            d.text((x, y), pal, font=ft, fill=ROSA if pal.strip(":,.") in marcadas else CREME)
            x += d.textlength(pal + " ", font=ft)
        y += int(tam * 1.02)
    d.rectangle([72, y + 30, 222, y + 40], fill=ROSA)
    d.rectangle([240, y + 30, 316, y + 40], fill=OURO)
    # faixa da chamada (o adesivo de link do Instagram fica por cima dela)
    fc = fonte("Archivo-SemiBold", 40)
    d.rounded_rectangle([72, 1560, W - 72, 1690], radius=28, outline=OURO, width=4)
    for i, l in enumerate(quebra(d, chamada, fc, W - 220)[:2]):
        d.text((W // 2, 1600 + i * 50 + (25 if len(quebra(d, chamada, fc, W - 220)) == 1 else 0)), l, font=fc, fill=CREME, anchor="mm")
    fr = fonte("Archivo-SemiBold", 32)
    d.text((W // 2, 1800), "escudoconcursos.com.br/noticias", font=fr, fill=CINZA, anchor="mm")
    destino = pathlib.Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    im.save(destino, "JPEG", quality=86, optimize=True, progressive=True)
    return destino
