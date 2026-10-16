"""Referencia ampliada con grilla de píxeles y el contorno de cada pieza de la ficha, para leer coordenadas.
Escribe art/<ID>/prev_grilla.png (no va al repo: lleva la imagen de referencia).
  * líneas finas cada 10 px y numeradas cada 50 px (coordenadas de la imagen de referencia);
  * piezas "s" en colores con su nombre; caños ("lathe") como rectángulos; huecos en rojo.
Uso: python3 tools/blender/guns/hd_grid.py AT_GXP --ref-dir DIR_IMAGENES [--zona X0 Y0 X1 Y1] [--sin-piezas]
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import hd_specs  # noqa: E402

ART = HERE.parent.parent.parent / "art"
COLS = [(255, 80, 80), (80, 200, 255), (255, 210, 60), (120, 255, 120), (255, 120, 255), (255, 160, 60),
        (160, 140, 255), (60, 255, 220)]


def main():
    from PIL import Image, ImageDraw, ImageFont
    a = sys.argv[1:]
    ID = [x for x in a if x.startswith("AT_")][0]
    sp = hd_specs.SPEC[ID]
    ref_dir = Path(a[a.index("--ref-dir") + 1])
    im = Image.open(ref_dir / sp["img"]).convert("RGB")
    if "--zona" in a:
        i = a.index("--zona")
        x0, y0, x1, y1 = (int(v) for v in a[i + 1:i + 5])
    else:
        J = json.loads((HERE / "siluetas" / f"{sp['sil']}.json").read_text())
        ext = max(J["shapes"], key=lambda s: len(s[0]))[0]
        x0, y0 = min(p[0] for p in ext) - 25, min(p[1] for p in ext) - 25
        x1, y1 = max(p[0] for p in ext) + 25, max(p[1] for p in ext) + 25
    x0, y0 = max(0, x0), max(0, y0)
    k = max(2, round(1600 / (x1 - x0)))
    crop = im.crop((x0, y0, x1, y1)).resize(((x1 - x0) * k, (y1 - y0) * k), Image.LANCZOS)
    crop = Image.blend(crop, Image.new("RGB", crop.size, (255, 255, 255)), 0.25)
    d = ImageDraw.Draw(crop, "RGBA")
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)

    def P(x, y):
        return ((x - x0) * k, (y - y0) * k)

    for x in range((x0 // 10) * 10, x1 + 1, 10):
        d.line([P(x, y0), P(x, y1)], fill=(0, 0, 0, 120 if x % 50 == 0 else 35), width=1)
        if x % 50 == 0:
            d.text((P(x, y0)[0] + 2, 2), str(x), fill=(0, 0, 160, 255), font=font)
    for y in range((y0 // 10) * 10, y1 + 1, 10):
        d.line([P(x0, y), P(x1, y)], fill=(0, 0, 0, 120 if y % 50 == 0 else 35), width=1)
        if y % 50 == 0:
            d.text((2, P(x0, y)[1] + 2), str(y), fill=(0, 0, 160, 255), font=font)
    if "--sin-piezas" not in a:
        ops = list(sp["parts"])
        if "mag" in sp:
            ops.append(("s", "cargador", sp["mag"]["region"], 0, "", {}))
            if "base" in sp["mag"]:
                ops.append(("s", "base_cargador", sp["mag"]["base"], 0, "", {}))
        for i, op in enumerate(ops):
            col = COLS[i % len(COLS)]
            if op[0] == "s":
                reg = op[2]
                if len(reg) == 4 and not isinstance(reg[0], (tuple, list)):
                    reg = [(reg[0], reg[1]), (reg[2], reg[1]), (reg[2], reg[3]), (reg[0], reg[3])]
                d.polygon([P(*p) for p in reg], outline=col + (255,), width=2)
                for h in (op[5] if len(op) > 5 else {}).get("holes", []):
                    d.polygon([P(*p) for p in h], outline=(255, 0, 0, 255), width=2)
                cx = sum(p[0] for p in reg) / len(reg)
                cy = sum(p[1] for p in reg) / len(reg)
                d.text(P(cx, cy), op[1], fill=col + (255,), font=font, anchor="mm", stroke_width=2,
                       stroke_fill=(0, 0, 0, 255))
            elif op[0] == "lathe":
                xs = [p[0] for p in op[2]]
                r = max(p[1] for p in op[2]) / sp["mm_px"]
                d.rectangle([P(min(xs), op[3] - r), P(max(xs), op[3] + r)], outline=col + (255,), width=2)
                d.text(P(min(xs) + 4, op[3] - r - 6), op[1], fill=col + (255,), font=font, stroke_width=2,
                       stroke_fill=(0, 0, 0, 255))
        for h in sp.get("holes", []):
            d.polygon([P(*p) for p in h], outline=(255, 0, 0, 255), width=2)
    out = ART / ID
    out.mkdir(parents=True, exist_ok=True)
    crop.save(out / "prev_grilla.png")
    print(f"[grilla] {ID}: zona ({x0},{y0})-({x1},{y1}) x{k} -> {out / 'prev_grilla.png'}")


if __name__ == "__main__":
    main()
