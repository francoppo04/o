"""Láminas de revisión de Arsenal Táctico: vista lateral de cada arma (art/<ID>/preview.png, primera franja)
y los íconos de cargadores, partes y munición. Las listas salen de tools/build_arsenal_tactico.py.
Uso: python3 tools/sheet_arsenal_tactico.py   -> art/arsenal_tactico_armas.png, art/arsenal_tactico_items.png"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_arsenal_tactico as b  # noqa: E402

ART = b.ART


def guns_sheet(out, cols=3, tw=700, th=300):
    ids = [g for g in b.GUNS if (ART / g / "preview.png").exists()]
    rows = (len(ids) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), (60, 62, 66))
    d = ImageDraw.Draw(sheet)
    for i, g in enumerate(ids):
        im = Image.open(ART / g / "preview.png")
        w, h = im.size
        x, y = (i % cols) * tw, (i // cols) * th
        sheet.paste(im.crop((0, 0, w, h // 3)).resize((tw, th)), (x, y))
        d.text((x + 8, y + 6), g, fill=(255, 220, 120))
    sheet.save(out)
    return out


def items_sheet(out, cols=8, t=180):
    ids = [i for i in list(b.MAGS) + list(b.PARTS) + ["AT_Granada40"] if (ART / i / "icon_256.png").exists()]
    rows = (len(ids) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * t, rows * (t + 20)), (60, 62, 66))
    d = ImageDraw.Draw(sheet)
    for i, p in enumerate(ids):
        ic = Image.open(ART / p / "icon_256.png").convert("RGBA").resize((t - 10, t - 10))
        x, y = (i % cols) * t, (i // cols) * (t + 20)
        sheet.paste(ic, (x + 5, y + 20), ic)
        d.text((x + 4, y + 4), p, fill=(255, 220, 120))
    sheet.save(out)
    return out


if __name__ == "__main__":
    print(guns_sheet(ART / "arsenal_tactico_armas.png"))
    print(items_sheet(ART / "arsenal_tactico_items.png"))
