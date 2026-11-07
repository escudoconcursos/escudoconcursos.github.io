"""Contador de visitas GoatCounter (grátis, sem cookies, sem dados pessoais) em todas as páginas do site.

Conta: https://escudoconcursos.goatcounter.com (criada pelo Mateus em 06/11/2026).
Rodar depois de criar uma página nova:
    python -I -X utf8 _config/contador.py

Idempotente: troca o bloco entre <!-- contador:inicio --> e <!-- contador:fim --> antes de </body>.
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
INI, FIM = "<!-- contador:inicio -->", "<!-- contador:fim -->"
BLOCO = (
    f'{INI}\n'
    '<script data-goatcounter="https://escudoconcursos.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>\n'
    f'{FIM}'
)


def main():
    paginas = [RAIZ / "index.html", RAIZ / "404.html"] + sorted(RAIZ.glob("*/index.html"))
    feitas = 0
    for p in paginas:
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8")
        orig = txt
        txt = re.sub(r"\n?" + re.escape(INI) + r".*?" + re.escape(FIM), "", txt, flags=re.S)
        if "</body>" not in txt:
            continue
        txt = txt.replace("</body>", BLOCO + "\n</body>", 1)
        if txt != orig:
            p.write_text(txt, encoding="utf-8")
            feitas += 1
    print(f"contador em {feitas} páginas")


if __name__ == "__main__":
    main()
