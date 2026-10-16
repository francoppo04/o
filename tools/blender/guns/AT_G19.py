"""AT_G19: pistola G-19 (5.ª gen.) calcada de la foto de referencia (guns/siluetas/AT_G19.json, misma foto que
AT_M4). Escala de pistola: el largo como la versión anterior (~0,16 m, boca a ~0,125).
Uso: python3 tools/blender/guns/AT_G19.py [--preview]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import gunkit as gk  # noqa: E402

ID = "AT_G19"
P = gk.Photo(ID, origin_px=(165, 330), origin=(0.0, 0.0), scale=0.00072, soften=2.0)
BY = 305
BORE = P.pt(200, BY)[1]


def X(px):
    return P.X(px, BY)


def build(preview=False):
    pz.reset()
    m, p = gk.black_metal(), gk.polymer()
    dark = gk.accent("oscuro", (0.018, 0.018, 0.02))
    parts = []

    # --- corredera con estrías, ventana de expulsión, miras
    slide = P.cut((118, 285, 340, 320))
    parts += gk.slab("corredera", slide, 0.0215, m, bevel=0.0018, segs=3)
    for i in range(8):
        x = 128 + i * 6
        parts += gk.decal(f"estria_t{i}", P.poly((x, 293, x + 2.6, 317)), 0.0109, dark)
    for i in range(7):
        x = 288 + i * 6.5
        parts += gk.decal(f"estria_d{i}", P.poly((x, 293, x + 2.6, 317)), 0.0109, dark)
    parts += gk.slab("ventana", P.poly((228, 287, 268, 291)), 0.017, gk.accent("canon", (0.12, 0.12, 0.13)),
                     bevel=0.0004)
    parts += gk.slab("alza", P.poly((128, 282, 142, 292)), 0.012, m, bevel=0.0006)
    parts += gk.slab("punto", P.poly((322, 283, 329, 292)), 0.004, m, bevel=0.0003)
    front = slide.bounds[2]
    parts.append(gk.tube("boca", front - 0.003, front + 0.0004, P.L(6), dark, z=BORE, segs=14))
    parts += gk.decal("marcas", P.poly((210, 300, 280, 305)), -0.011, gk.accent("grabado", (0.16, 0.16, 0.17)),
                      depth=0.0012, both=False)

    # --- armazón con guardamonte calado, riel, cola con seguro, palancas
    hole = P.poly([(200, 336), (257, 336), (259, 352), (252, 364), (206, 364)])
    frame = P.cut([(116, 318), (337, 318), (337, 337), (268, 337), (268, 376), (190, 376), (184, 339),
                   (116, 339)]).difference(hole)
    parts += gk.slab("armazon", frame, 0.0225, p, bevel=0.0015, segs=3)
    parts += gk.decal("riel", P.poly((282, 330, 326, 333)), 0.0114, dark)
    parts += gk.slab("cola", P.poly([(220, 330), (230, 330), (233, 358), (226, 361)]), 0.0055, p, bevel=0.0006)
    parts += gk.slab("seguro", P.poly([(223, 336), (228, 336), (229, 350), (225, 351)]), 0.0065, dark, bevel=0.0)
    parts += gk.decal("retenida", P.poly((188, 321, 214, 325)), -0.0118, m, depth=0.0015, both=False)
    parts += gk.decal("desarme", P.poly((236, 321, 246, 327)), 0.0118, m, depth=0.0015)

    # --- empuñadura texturada y base del cargador
    # contorno a mano (el calco de la foto sale serruchado): ~16° de inclinación como la G19
    grip = P.poly([(115, 319), (190, 319), (190, 337), (186, 345), (158, 424), (98, 424), (101, 405), (111, 370),
                   (119, 341), (113, 328)])
    parts += gk.slab("empunadura", grip, 0.0245, p, bevel=0.0035, segs=3)
    parts += gk.panel("textura", grip.intersection(P.poly((80, 342, 200, 408))), 0.0245, gk.rubber(),
                      inset=0.0035)
    parts += gk.slab("base", P.poly([(96, 421), (160, 421), (158, 440), (94, 440)]), 0.0255, dark, bevel=0.002, segs=3)

    obj = gk.finish_gun(ID, parts, tex_size=512)
    if preview:
        gk.preview(obj, pz.ART / ID / "preview.png")
    gk.export(obj, ID, "handgun", {
        "muzzle": (front, 0, BORE),
        "at_light": (X(312), 0, P.pt(300, 337)[1] - 0.001),
    })


if __name__ == "__main__":
    build("--preview" in sys.argv)
