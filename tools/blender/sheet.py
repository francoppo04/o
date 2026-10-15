"""Arma la hoja de revisión de un arma a partir de los renders de pzlib.previews().

Uso: python tools/blender/sheet.py AC_Hachamazo [AC_Otro ...]
Salida: art/<Nombre>/sheet.png

Escala in-game aproximada (monitor 1080p): con zoom normal un personaje mide ~100 px de alto;
con el zoom más cercano, ~200 px. Los renders isométricos crudos se reducen a esos tamaños
para ver el arma con la cantidad real de píxeles que ocupa en pantalla.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "art"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

RAW_CHAR_PX = 433  # alto del personaje en preview_ingame_raw.png (1,78 m, ortho 3.2 m / 900 px, elevación 30°)


def font(size, bold=True):
    try:
        return ImageFont.truetype(FONT if bold else FONT_R, size)
    except OSError:
        return ImageFont.load_default()


def scaled(img, factor, upscale_to=None):
    """Reduce a escala real de juego y luego amplía con vecino más cercano para poder verlo."""
    w, h = img.size
    small = img.resize((max(1, int(w * factor)), max(1, int(h * factor))), Image.LANCZOS)
    if upscale_to:
        k = upscale_to / small.size[1]
        small = small.resize((int(small.size[0] * k), upscale_to), Image.NEAREST)
    return small


def crop_center(img, frac):
    w, h = img.size
    cw, ch = int(w * frac), int(h * frac)
    return img.crop(((w - cw) // 2, (h - ch) // 2, (w + cw) // 2, (h + ch) // 2))


def center_crop(img, w, h):
    iw, ih = img.size
    x, y = (iw - w) // 2, (ih - h) // 2
    return img.crop((x, y, x + w, y + h))


def build(name, title=None):
    d = ART / name
    W, H = 1800, 1330
    sheet = Image.new("RGB", (W, H), (22, 20, 19))
    dr = ImageDraw.Draw(sheet)
    dr.text((40, 26), (title or name).upper(), font=font(46), fill=(246, 240, 230))
    dr.text((42, 84), "Vista previa del modelo 3D real (FBX + textura). No es una captura del juego.",
            font=font(20, False), fill=(200, 183, 140))

    def label(x, y, t):
        dr.text((x, y), t, font=font(19), fill=(242, 184, 24))

    hero = Image.open(d / "preview_hero.png").convert("RGBA")
    bg = Image.new("RGBA", hero.size, (48, 45, 42, 255))
    bg.alpha_composite(hero)
    sheet.paste(bg.convert("RGB").resize((1000, 571)), (40, 150))
    label(40, 126, "MODELO DE CERCA (perspectiva 3/4)")

    side = Image.open(d / "preview_side.png").convert("RGBA")
    bg = Image.new("RGBA", side.size, (48, 45, 42, 255))
    bg.alpha_composite(side)
    sheet.paste(bg.convert("RGB").resize((700, 350)), (1070, 150))
    label(1070, 126, "SILUETA (lateral)")

    tex = Image.open(d / f"{name}.png").convert("RGB")
    sheet.paste(tex.resize((210, 210), Image.NEAREST), (1070, 520))
    label(1070, 496, f"TEXTURA {tex.size[0]}x{tex.size[1]}")

    icon = Image.open(d / "icon_256.png").convert("RGBA")
    ic64 = icon.resize((64, 64), Image.LANCZOS)
    ic32 = icon.resize((32, 32), Image.LANCZOS)
    ic64.save(d / "icon_64.png")
    ic32.save(d / "icon_32.png")
    slot = Image.new("RGBA", (210, 210), (60, 56, 52, 255))
    slot.alpha_composite(ic64.resize((128, 128), Image.NEAREST), (41, 20))
    slot.alpha_composite(ic32.resize((64, 64), Image.NEAREST), (73, 150 - 4))
    sheet.paste(slot.convert("RGB"), (1310, 520))
    label(1310, 496, "ÍCONO 64/32")

    raw = Image.open(d / "preview_ingame_raw.png").convert("RGB")
    near = scaled(crop_center(raw, .7), 200 / RAW_CHAR_PX)
    normal = scaled(crop_center(raw, .7), 100 / RAW_CHAR_PX)
    label(40, 760, "IN-GAME · ZOOM CERCANO (x2)")
    sheet.paste(center_crop(near.resize((near.size[0] * 2, near.size[1] * 2), Image.NEAREST), 560, 520), (40, 784))
    label(640, 760, "ZOOM NORMAL (x3)")
    sheet.paste(center_crop(normal.resize((normal.size[0] * 3, normal.size[1] * 3), Image.NEAREST), 420, 520), (640, 784))
    ground = Image.open(d / "preview_ground_raw.png").convert("RGB")
    g = scaled(crop_center(ground, .8), 200 / RAW_CHAR_PX * 3.2 / 2.4)
    label(1100, 760, "EN EL SUELO (x2)")
    sheet.paste(center_crop(g.resize((g.size[0] * 2, g.size[1] * 2), Image.NEAREST), 660, 520), (1100, 784))
    # tamaño 1:1 real como referencia
    label(1540, 496, "TAMAÑO REAL")
    one = scaled(crop_center(raw, .7), 100 / RAW_CHAR_PX)
    ow, oh = one.size
    sheet.paste(one.crop(((ow - 220) // 2, (oh - 210) // 2, (ow + 220) // 2, (oh + 210) // 2)), (1540, 520))
    sheet.save(d / "sheet.png")
    print(d / "sheet.png")


if __name__ == "__main__":
    for n in sys.argv[1:]:
        build(n)
