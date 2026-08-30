# Build para hospedagem (GitHub Pages).
#
# Diferenca para o build.py original: aquele embute tudo em base64 dentro de um
# unico HTML, o que serve para entregar o site como arquivo solto. Para um site
# no ar isso e ruim - o navegador precisa baixar 1,9 MB antes de desenhar
# qualquer coisa, porque o video de 1 MB vira texto dentro do proprio HTML.
#
# Aqui os assets viram arquivos de verdade em dist/assets/. O HTML fica com
# ~30 KB, aparece na hora, e o navegador baixa imagem e video em paralelo e
# guarda em cache nas visitas seguintes.
#
# A saida vai para docs/ porque o GitHub Pages sabe publicar essa pasta
# diretamente da branch principal. Assim um push unico leva codigo e site, sem
# branch separada nem passo extra.
#
# Sem caminho absoluto: roda de onde estiver.

import re
import shutil
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
DIST = ROOT / "docs"

# Numero que recebe os cliques de "agendar". E o mesmo do site atual
# (drmarcelloruiz.com.br), onde a recepcao ja atende.
WHATSAPP = "5511975175747"

# Textos identicos aos do site atual, para a recepcao continuar reconhecendo de
# onde veio o contato.
WA = {
    "geral": "Olá, eu venho do site do Dr. Marcello e gostaria de mais informações sobre o atendimento.",
    "vilamariana": "Olá, eu venho do site do Dr. Marcello e gostaria de mais informações sobre o atendimento na Vila Mariana.",
    "santoandre": "Olá, eu venho do site do Dr. Marcello e gostaria de mais informações sobre o atendimento em Santo André.",
    "santos": "Olá, eu venho do site do Dr. Marcello e gostaria de mais informações sobre o atendimento em Santos.",
}

html = (ROOT / "template.html").read_text(encoding="utf-8")

usados: set[str] = set()


def caminho_asset(match: re.Match) -> str:
    nome = match.group(1).strip()
    if not (ASSETS / nome).exists():
        raise SystemExit(f"asset ausente: {nome}")
    usados.add(nome)
    return f"assets/{nome}"


html = re.sub(r"%%ASSET:([^%]+)%%", caminho_asset, html)
html = re.sub(
    r"%%WA:([a-z]+)%%",
    lambda m: f"https://wa.me/{WHATSAPP}?text=" + quote(WA[m.group(1)]),
    html,
)

if "%%" in html:
    raise SystemExit("sobrou token %% no HTML")

# Limpa builds anteriores. ignore_errors porque em pasta sincronizada (OneDrive,
# Drive) o sistema as vezes segura um arquivo e o rmtree falharia por isso.
shutil.rmtree(DIST, ignore_errors=True)
(DIST / "assets").mkdir(parents=True, exist_ok=True)

(DIST / "index.html").write_text(html, encoding="utf-8")

# Copia so o que o HTML referencia. dr-marcello.png (1,1 MB) e
# logo-dr-marcello.png (225 KB) nao sao usados - ficam de fora.
for nome in sorted(usados):
    shutil.copy2(ASSETS / nome, DIST / "assets" / nome)

# Impede o GitHub Pages de processar os arquivos com Jekyll.
(DIST / ".nojekyll").write_text("", encoding="utf-8")

total = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
print(f"docs/index.html  {(DIST / 'index.html').stat().st_size / 1024:.0f} KB")
for nome in sorted(usados):
    print(f"docs/assets/{nome}  {(ASSETS / nome).stat().st_size / 1024:.0f} KB")
print(f"total: {total / 1024 / 1024:.2f} MB")
