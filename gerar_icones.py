# Gera o jogo de icones (favicon, atalho de celular, PWA) a partir do "M" do
# logo. Rode de novo sempre que a marca mudar; nao edite os PNG na mao.
#
# A fonte e o proprio logo do site (logo-dr-marcello.png), nao uma imagem
# solta: o "M" de la e o unico que vai continuar igual quando a marca mudar.
# Ele vem em dois tons escuros, para fundo claro; aqui vira branco solido,
# que e como o icone oficial (21/09/2026) mostra a marca sobre o azul.

from PIL import Image, ImageDraw
from pathlib import Path

FUNDO = (4, 30, 60)          # #041E3C - amostrado do icone oficial
MASTER = 1024

def m_branco(origem: Path) -> Image.Image:
    """O 'M' do logo, recortado e pintado de branco solido."""
    logo = Image.open(origem).convert("RGBA")
    # Primeiro bloco horizontal com tinta = o simbolo; o resto e o texto.
    import numpy as np
    a = np.array(logo.split()[3])
    cols = (a > 10).sum(axis=0)
    ini = next(i for i, v in enumerate(cols) if v > 0)
    fim = ini
    for i in range(ini, len(cols)):
        if cols[i] > 0:
            fim = i
        elif i - fim > 10:
            break
    sim = logo.crop((ini, 0, fim + 1, logo.height))
    sim = sim.crop(sim.split()[3].getbbox())
    branco = Image.new("RGBA", sim.size, (255, 255, 255, 0))
    branco.putalpha(sim.split()[3])
    branco.paste((255, 255, 255), (0, 0), sim.split()[3])
    branco.putalpha(sim.split()[3])
    return branco


def placa(m: Image.Image, lado: int, ocupa: float, raio: float) -> Image.Image:
    """Quadrado azul com o M centralizado. `ocupa` = fracao da largura."""
    img = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if raio > 0:
        d.rounded_rectangle([0, 0, lado - 1, lado - 1], radius=int(lado * raio), fill=FUNDO + (255,))
    else:
        d.rectangle([0, 0, lado - 1, lado - 1], fill=FUNDO + (255,))
    lw = int(lado * ocupa)
    lh = round(m.height * lw / m.width)
    mm = m.resize((lw, lh), Image.LANCZOS)
    img.paste(mm, ((lado - lw) // 2, (lado - lh) // 2), mm)
    return img


def gerar(origem: Path, saida: Path):
    saida.mkdir(parents=True, exist_ok=True)
    m = m_branco(origem)

    # "any": canto arredondado como o icone oficial.
    mestre = placa(m, MASTER, 0.62, 0.22)
    for lado in (512, 192, 128, 64):
        mestre.resize((lado, lado), Image.LANCZOS).save(saida / f"icone-{lado}.png", optimize=True)

    # 16 e 32 nao saem do mestre: encolher o icone inteiro joga o "M" em 10
    # pixels e ele vira mancha. Nesses tamanhos o M ocupa mais da placa e o
    # canto arredonda menos - e o que o navegador mostra na aba, onde a marca
    # precisa ser reconhecida, nao admirada.
    miudo = placa(m, MASTER, 0.80, 0.14)
    for lado in (48, 32, 16):
        miudo.resize((lado, lado), Image.LANCZOS).save(saida / f"icone-{lado}.png", optimize=True)

    # favicon.ico com as tres medidas que o Windows e navegadores antigos pedem.
    miudo.resize((48, 48), Image.LANCZOS).save(
        saida / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)]
    )

    # apple-touch-icon: SEM canto arredondado e SEM transparencia. O iOS aplica
    # a mascara dele por cima; se o arquivo ja vier arredondado, o corte
    # acontece duas vezes e sobra um contorno escuro no canto.
    placa(m, 180, 0.62, 0).convert("RGB").save(saida / "apple-touch-icon.png", optimize=True)

    # maskable (Android): o sistema pode cortar ate 20% de cada borda, entao o
    # M encolhe para caber na zona segura e o azul sangra ate a borda.
    placa(m, 512, 0.48, 0).save(saida / "icone-maskable-512.png", optimize=True)

    for f in sorted(saida.iterdir()):
        print(f"  {f.name}  {f.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    import sys
    gerar(Path(sys.argv[1]), Path(sys.argv[2]))
