"""Vista previa rápida de un arma HD, para iterar la ficha sin hornear texturas ni exportar.
Escribe en OUT (por defecto art/<ID>/):
  prev_silueta.png  superposición con la referencia: verde = coinciden, rojo = falta en el modelo,
                    azul = sobra en el modelo, gris = zona excluida (accesorios);
  prev_volumen.png  costado, arriba y 3/4 en arcilla (color plano por material, sin textura);
y muestra IoU, triángulos y lo que el relleno sumó a cada pieza.
Uso: python3 tools/blender/guns/hd_preview.py AT_GXP --ref-dir DIR_IMAGENES [--out DIR]
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import hardsurf as hs  # noqa: E402
import hd  # noqa: E402
import pzlib as pz  # noqa: E402


def main():
    args = sys.argv[1:]
    ID = [a for a in args if a.startswith("AT_")][0]
    ref_dir = Path(args[args.index("--ref-dir") + 1])
    out = Path(args[args.index("--out") + 1]) if "--out" in args else pz.ART / ID
    out.mkdir(parents=True, exist_ok=True)
    pz.reset()
    g = hd.Gun(ID)
    P = g.finish(g.build_parts())
    tris = hs.tri_count(P)
    r = None
    if g.sil_json:
        r = hs.silhouette_iou(P, g.ref, g.sil_json, g.sp.get("exclude", []), g.sp.get("holes", []),
                              photo=str(ref_dir / g.sp["img"]), out=str(out / "prev_silueta.png"))
    from mathutils import Vector
    from PIL import Image, ImageDraw
    vs = [o.matrix_world @ v.co for o in P for v in o.data.vertices]
    lo = Vector([min(v[i] for v in vs) for i in range(3)])
    hi = Vector([max(v[i] for v in vs) for i in range(3)])
    c = (lo + hi) / 2
    L = hi.x - lo.x
    H = hi.z - lo.z
    views = [("costado", (0, -1, 0), max(L, 2.5 * H) * 1.04, (1200, 480)),
             ("arriba", (0.0, -0.0001, 1.0), max(L, 5 * (hi.y - lo.y)) * 1.04, (1200, 240)),
             ("3/4", (0.7, -1.0, 0.6), max(L, 2 * H) * 0.95, (1200, 560))]
    sheet = Image.new("RGB", (1200, 1280), (46, 47, 50))
    y = 0
    for name, d, span, size in views:
        p = out / "_prev.png"
        hs.closeup(P, p, tuple(c), dist=1.0, direction=d, size=size, ortho=span, samples=12, light=0.6)
        sheet.paste(Image.open(p).convert("RGB"), (0, y))
        ImageDraw.Draw(sheet).text((8, y + 6), name, fill=(255, 220, 120))
        p.unlink()
        y += size[1]
    sheet.save(out / "prev_volumen.png")
    iou = f"{r[0]:.3f} (falta {r[2]} px, sobra {r[3]} px)" if r else "n/d"
    print(f"[preview] {ID}: IoU {iou}, {tris} triángulos, {len(P)} piezas -> {out}")


if __name__ == "__main__":
    main()
