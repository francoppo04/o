"""Genera los iconos de inventario (32x32) y los posters del mod Arsenal de Chatarra.

Uso:  python tools/gen_icons.py
Requiere Pillow. Escribe en Contents/mods/ArsenalChatarra/42/media/textures/,
42/poster.png y preview.png en la raiz del repo.
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
MOD = ROOT / "Contents" / "mods" / "ArsenalChatarra" / "42"
TEX = MOD / "media" / "textures"

OUTLINE = (24, 20, 18, 255)
STEEL = (150, 156, 162, 255)
STEEL_LIGHT = (214, 220, 226, 255)
STEEL_DARK = (92, 98, 106, 255)
RUST = (150, 74, 36, 255)
WOOD = (132, 86, 48, 255)
WOOD_LIGHT = (176, 124, 74, 255)
GRIP = (52, 44, 40, 255)
CLOTH = (206, 190, 150, 255)
CLOTH_DARK = (150, 134, 98, 255)
RED = (184, 32, 32, 255)
WHITE = (238, 238, 238, 255)
BRASS = (230, 190, 70, 255)
BLOOD = (120, 14, 14, 255)


def new():
    return Image.new("RGBA", (32, 32), (0, 0, 0, 0))


def px(img, x, y, c):
    if 0 <= x < 32 and 0 <= y < 32:
        img.putpixel((x, y), c)


def diag(img, x0, y0, x1, c, width=1, side=1):
    """Linea diagonal hacia arriba-derecha desde (x0, y0) hasta x1, con grosor
    hacia abajo-derecha (side=1) o arriba-izquierda (side=-1)."""
    for i in range(x1 - x0 + 1):
        x, y = x0 + i, y0 - i
        for w in range(width):
            px(img, x + (w if side > 0 else 0), y + (w if side > 0 else -w), c)
            if w:
                px(img, x, y + w * side, c)


def outline(img):
    """Contorno oscuro de 1px alrededor de todo lo pintado."""
    src = img.copy()
    for y in range(32):
        for x in range(32):
            if src.getpixel((x, y))[3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < 32 and 0 <= ny < 32 and src.getpixel((nx, ny))[3]:
                    img.putpixel((x, y), OUTLINE)
                    break
    return img


def machete_sierra():
    img = new()
    diag(img, 4, 27, 9, GRIP, 2)                      # mango
    for i in (5, 7, 9):
        px(img, i, 27 - (i - 4), CLOTH_DARK)          # remaches del mango
    diag(img, 9, 24, 11, STEEL_DARK, 3)               # guarda
    diag(img, 11, 21, 27, STEEL, 3)                   # hoja
    diag(img, 12, 22, 27, STEEL_LIGHT, 1)             # filo
    px(img, 28, 5, STEEL_LIGHT)
    for i in range(12, 27, 2):                        # dientes de sierra en el lomo
        px(img, i - 1, 20 - (i - 11) - 1, STEEL_DARK)
        px(img, i, 20 - (i - 11) - 1, STEEL)
    px(img, 20, 15, BLOOD)
    px(img, 21, 15, BLOOD)
    px(img, 23, 12, BLOOD)
    return outline(img)


def hacha_remachada():
    img = new()
    diag(img, 4, 28, 21, WOOD, 2)                     # mango
    diag(img, 5, 28, 21, WOOD_LIGHT, 1)
    head = [(17, 6), (23, 12), (27, 9), (29, 13), (27, 19), (24, 18), (22, 14), (15, 8)]
    ImageDraw.Draw(img).polygon(head, fill=STEEL_DARK)
    ImageDraw.Draw(img).line([(27, 9), (29, 13), (27, 19)], fill=STEEL_LIGHT)  # filo
    ImageDraw.Draw(img).line([(26, 10), (28, 13), (26, 17)], fill=STEEL)
    for x, y in ((18, 8), (21, 11), (24, 13), (20, 9)):
        px(img, x, y, BRASS)                          # remaches
    ImageDraw.Draw(img).line([(14, 5), (12, 3)], fill=RUST, width=2)  # pico trasero
    return outline(img)


def mazo_senal():
    img = new()
    diag(img, 4, 28, 16, STEEL_DARK, 2)               # cano
    diag(img, 5, 28, 16, STEEL, 1)
    for i in (5, 6, 7):
        diag(img, i, 28 - (i - 4) + 1, i, CLOTH, 1)   # cinta del agarre
    cx, cy, r = 22, 9, 8
    octo = [(cx - r // 2, cy - r), (cx + r // 2, cy - r), (cx + r, cy - r // 2), (cx + r, cy + r // 2),
            (cx + r // 2, cy + r), (cx - r // 2, cy + r), (cx - r, cy + r // 2), (cx - r, cy - r // 2)]
    d = ImageDraw.Draw(img)
    d.polygon(octo, fill=WHITE)
    inner = [((x - cx) * 0.78 + cx, (y - cy) * 0.78 + cy) for x, y in octo]
    d.polygon(inner, fill=RED)
    d.line([(cx - 4, cy), (cx + 4, cy)], fill=WHITE)  # franja tipo "PARE"
    d.line([(cx - 3, cy - 2), (cx + 3, cy - 2)], fill=(210, 60, 60, 255))
    for x, y in ((cx - 5, cy - 4), (cx + 5, cy + 4)):
        px(img, x, y, RUST)                           # oxido
    px(img, cx - 1, cy + 3, STEEL_DARK)               # bulon
    return outline(img)


def bate_encadenado():
    img = new()
    for i in range(23):                               # bate que se ensancha
        x, y = 4 + i, 28 - i
        w = 2 if i < 8 else (3 if i < 14 else 4)
        for k in range(w):
            px(img, x + k, y, WOOD)
            px(img, x, y + k, WOOD)
        px(img, x, y, WOOD_LIGHT)
    diag(img, 4, 28, 9, GRIP, 2)                      # cinta del mango
    for i in range(12, 26, 3):                        # cadena envolviendo
        x, y = 4 + i, 28 - i
        px(img, x - 1, y - 1, STEEL_LIGHT)
        px(img, x + 1, y + 1, STEEL)
        px(img, x + 3, y + 3, STEEL_DARK)
        px(img, x + 2, y + 2, STEEL)
    for x, y in ((19, 7), (24, 4), (29, 8), (27, 13)):
        px(img, x, y, STEEL_LIGHT)                    # puntas de clavos
    return outline(img)


def estoque_barra():
    img = new()
    diag(img, 5, 27, 10, CLOTH, 2)                    # mango de trapo
    for i in (6, 8, 10):
        px(img, i, 27 - (i - 5), CLOTH_DARK)
    ImageDraw.Draw(img).line([(9, 18), (14, 23)], fill=STEEL_DARK, width=2)  # guarda
    diag(img, 12, 20, 27, STEEL_DARK, 2)              # barra corrugada
    for i in range(12, 28, 2):
        px(img, i, 20 - (i - 12), RUST)
    diag(img, 13, 20, 27, STEEL, 1)
    px(img, 28, 4, STEEL_LIGHT)                       # punta
    px(img, 29, 3, STEEL_LIGHT)
    return outline(img)


ICONS = {
    "AC_MacheteSierra": machete_sierra,
    "AC_HachaRemachada": hacha_remachada,
    "AC_MazoSenal": mazo_senal,
    "AC_BateEncadenado": bate_encadenado,
    "AC_EstoqueBarra": estoque_barra,
}


def poster(icons):
    """256x256 con los iconos ampliados sobre fondo oscuro."""
    img = Image.new("RGBA", (256, 256), (34, 30, 28, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([6, 6, 249, 249], outline=(150, 74, 36, 255), width=4)
    spots = [(16, 16), (136, 16), (16, 136), (136, 136)]
    for (x, y), icon in zip(spots, icons[:4]):
        img.alpha_composite(icon.resize((104, 104), Image.NEAREST), (x, y))
    img.alpha_composite(icons[4].resize((96, 96), Image.NEAREST), (80, 80))
    return img.convert("RGB")


def main():
    TEX.mkdir(parents=True, exist_ok=True)
    made = []
    for name, fn in ICONS.items():
        icon = fn()
        icon.save(TEX / f"Item_{name}.png")
        made.append(icon)
    p = poster(made)
    p.save(MOD / "poster.png")
    p.save(ROOT / "preview.png")
    print(f"{len(made)} iconos + poster.png + preview.png")


if __name__ == "__main__":
    main()
