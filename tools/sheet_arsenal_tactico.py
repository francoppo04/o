"""Lámina de revisión de Arsenal Táctico: vista lateral de cada arma (art/<ID>/preview.png, primera franja)
y los íconos de las partes. Uso: python3 tools/sheet_arsenal_tactico.py [salida.png]"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ART = Path(__file__).resolve().parents[1] / "art"
GUNS = ["AT_M4", "AT_MCX", "AT_AK101", "AT_G19", "AT_Marlin336"]
PARTS = ["AT_ACOG", "AT_LPVO", "AT_HoloSight", "AT_Thermal", "AT_TacLight",
         "AT_SkullMag", "AT_LancerMag", "AT_AKMag", "AT_G19Mag"]


def main(out):
    tiles = []
    for g in GUNS:
        im = Image.open(ART / g / "preview.png")
        w, h = im.size
        tiles.append((g, im.crop((0, 0, w, h // 3)).resize((900, 300))))
    sheet = Image.new("RGB", (1800, 300 * 3 + 260), (60, 62, 66))
    d = ImageDraw.Draw(sheet)
    for i, (g, t) in enumerate(tiles):
        x, y = (i % 2) * 900, (i // 2) * 300
        sheet.paste(t, (x, y))
        d.text((x + 10, y + 8), g, fill=(255, 220, 120))
    for i, p in enumerate(PARTS):
        ic = Image.open(ART / p / "icon_256.png").convert("RGBA").resize((190, 190))
        x, y = 10 + i * 198, 300 * 3 + 50
        sheet.paste(ic, (x, y), ic)
        d.text((x, y - 18), p, fill=(255, 220, 120))
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(ART / "arsenal_tactico_detalle.png"))
