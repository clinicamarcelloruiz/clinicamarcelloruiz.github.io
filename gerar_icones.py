"""Gera todos os icones do site e do PWA do Dr. Marcello.

O simbolo completo do logo funciona bem em tamanho grande, mas perde a leitura
na aba do navegador. Por isso os icones usam uma versao opticamente corrigida:
um M geometrico, com o mesmo gesto inclinado da marca, traco branco mais largo
e espaco negativo suficiente para continuar legivel em 16 x 16 pixels.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter


FUNDO = (4, 30, 60)  # #041E3C
BRANCO = (255, 255, 255, 255)
MASTER = 1024


def fundo(lado: int, raio: float, opaco: bool = False) -> Image.Image:
    """Cria a placa azul com um brilho discreto no canto superior direito."""
    base = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    mascara = Image.new("L", (lado, lado), 0)
    md = ImageDraw.Draw(mascara)
    r = 0 if opaco else round(lado * raio)
    md.rounded_rectangle((0, 0, lado - 1, lado - 1), radius=r, fill=255)

    placa = Image.new("RGBA", (lado, lado), FUNDO + (255,))
    brilho = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    bd = ImageDraw.Draw(brilho)
    bd.ellipse(
        (lado * 0.42, -lado * 0.28, lado * 1.28, lado * 0.58),
        fill=(28, 83, 139, 82),
    )
    brilho = brilho.filter(ImageFilter.GaussianBlur(lado * 0.14))
    placa = Image.alpha_composite(placa, brilho)
    base.paste(placa, (0, 0), mascara)
    return base


def desenhar_m(img: Image.Image, ocupa: float, traco: float) -> None:
    """Desenha um M simples e inequívoco, com pontas e encontros arredondados."""
    lado = img.width
    largura = lado * ocupa
    x0 = (lado - largura) / 2
    x1 = x0 + largura
    topo = lado * 0.255
    base = lado * 0.755
    meio = lado * 0.585
    pontos = [
        (x0, base),
        (x0 + largura * 0.235, topo),
        (x0 + largura * 0.500, meio),
        (x0 + largura * 0.765, topo),
        (x1, base),
    ]
    espessura = max(1, round(lado * traco))
    d = ImageDraw.Draw(img)
    d.line(pontos, fill=BRANCO, width=espessura, joint="curve")
    raio = espessura / 2
    for x, y in pontos:
        d.ellipse((x - raio, y - raio, x + raio, y + raio), fill=BRANCO)


def icone(lado: int, ocupa: float, traco: float, raio: float, opaco: bool = False) -> Image.Image:
    img = fundo(lado, raio, opaco=opaco)
    desenhar_m(img, ocupa, traco)
    return img


def gerar(_origem: Path, saida: Path) -> None:
    saida.mkdir(parents=True, exist_ok=True)

    # Icones comuns e do instalador PWA.
    mestre = icone(MASTER, ocupa=0.66, traco=0.105, raio=0.22)
    for lado in (512, 192, 128, 64):
        mestre.resize((lado, lado), Image.Resampling.LANCZOS).save(
            saida / f"icone-{lado}.png", optimize=True
        )

    # Correcao optica para abas e favoritos: M maior, mais grosso e com menos
    # arredondamento na placa. Assim ele nao vira um triangulo em 16 pixels.
    pequeno = icone(MASTER, ocupa=0.79, traco=0.135, raio=0.15)
    for lado in (48, 32, 16):
        pequeno.resize((lado, lado), Image.Resampling.LANCZOS).save(
            saida / f"icone-{lado}.png", optimize=True
        )

    pequeno.resize((48, 48), Image.Resampling.LANCZOS).save(
        saida / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)]
    )

    # O iOS e o Android aplicam suas proprias mascaras. Nesses dois arquivos o
    # azul vai ate a borda; no maskable o M fica dentro da zona segura central.
    icone(180, ocupa=0.66, traco=0.105, raio=0, opaco=True).convert("RGB").save(
        saida / "apple-touch-icon.png", optimize=True
    )
    icone(512, ocupa=0.50, traco=0.080, raio=0, opaco=True).save(
        saida / "icone-maskable-512.png", optimize=True
    )

    for arquivo in sorted(saida.iterdir()):
        print(f"  {arquivo.name}  {arquivo.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    import sys

    gerar(Path(sys.argv[1]), Path(sys.argv[2]))
