"""AT_G19: pistola compacta tipo Glock 19 (9 mm). Escala del juego (M9 vanilla de referencia).
Uso: python3 tools/blender/guns/AT_G19.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import gunkit as gk  # noqa: E402

ID = "AT_G19"


def build():
    pz.reset()
    m, p = gk.black_metal(), gk.polymer()
    dark = gk.accent("oscuro", (0.02, 0.02, 0.022))
    parts = [
        gk.bx("corredera", -0.038, 0.118, -0.0115, 0.0115, 0.012, 0.037, m, bevel=0.0025),
        gk.bx("ventana", 0.010, 0.046, -0.0118, -0.0105, 0.024, 0.036, dark, bevel=0.0),
        gk.tube("boca", 0.110, 0.1195, 0.0052, dark, z=0.026, segs=10),
        gk.bx("estrias", -0.034, -0.012, -0.0118, 0.0118, 0.016, 0.034, dark, bevel=0.0),
        gk.bx("armazon", -0.034, 0.112, -0.0105, 0.0105, 0.000, 0.013, p, bevel=0.002),
        gk.bx("alza", -0.030, -0.022, -0.006, 0.006, 0.037, 0.042, m, bevel=0.0),
        gk.bx("punto", 0.104, 0.110, -0.0025, 0.0025, 0.037, 0.041, m, bevel=0.0),
        gk.side("empunadura", [(-0.034, 0.002), (0.010, 0.002), (-0.004, -0.074), (-0.014, -0.080), (-0.046, -0.074)], 0.027, p),
        gk.side("base", [(-0.046, -0.073), (-0.003, -0.073), (-0.004, -0.082), (-0.047, -0.081)], 0.028, dark),
        gk.side("guardamonte", [(0.006, 0.0), (0.050, 0.0), (0.046, -0.022), (0.010, -0.022), (0.010, -0.016), (0.040, -0.016), (0.042, -0.004), (0.010, -0.004)], 0.008, p),
        gk.bx("cola", 0.018, 0.022, -0.002, 0.002, -0.014, 0.0, m, bevel=0.0),
    ]
    parts += gk.rail("riel", 0.060, 0.108, -0.004, p, w=0.016, h=0.005)
    obj = pz.finish(ID, parts, tex_size=256, ao=True)
    gk.export(obj, ID, "handgun", {
        "muzzle": (0.120, 0, 0.026),
        "at_light": (0.084, 0, -0.004),
    })


if __name__ == "__main__":
    build()
