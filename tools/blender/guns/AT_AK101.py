"""AT_AK101: AK-101 con culata plegable triangular, montura lateral con riel para mira y freno de boca,
calcada de la foto de referencia (guns/siluetas/AT_AK101.json; en esa foto la boca apunta a la izquierda,
por eso flip=True). Misma foto y escala que AT_M4.
Uso: python3 tools/blender/guns/AT_AK101.py [--preview]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import gunkit as gk  # noqa: E402

ID = "AT_AK101"
P_BORE = ((85, 524), (460, 524))     # dos puntos del eje del cañón en la foto
P = gk.Photo(ID, origin_px=(726, 541), origin=(0.006, 0.0), bore_px=P_BORE, scale=0.000504,
             flip=True)
BY = 524
BORE = P.pt(400, BY)[1]


def X(px):
    return P.X(px, BY)


def Z(py):
    return P.pt(400, py)[1]


def magazine(P):
    """Cargador curvo de polímero con nervio perimetral (píxeles de la foto; lo usa también parts.py)."""
    p, dark = gk.polymer(), gk.accent("oscuro", (0.018, 0.018, 0.02))
    mag = P.cut([(500, 538), (597, 538), (592, 620), (568, 775), (430, 775), (430, 700)])
    parts = gk.slab("cargador", mag, 0.022, p, bevel=0.0025, segs=3)
    parts += gk.decal("nervio_cargador", mag.buffer(-0.0035, join_style=2).difference(mag.buffer(-0.0048,
                                                                                            join_style=2)),
                      0.0111, dark, depth=0.0006)
    return parts


def build(preview=False):
    pz.reset()
    m, p = gk.black_metal(), gk.polymer()
    dark = gk.accent("oscuro", (0.018, 0.018, 0.02))
    parts = []

    # --- freno de boca, tubo, base del alza delantera con poste, cañón, tubo de gases, baqueta
    parts.append(gk.lathe_x("freno", [(X(100), P.L(13)), (X(92), P.L(16)), (X(76), P.L(17)), (X(70), P.L(15)),
                                      (X(70), P.L(6))], m, z=BORE, segs=20))
    for i in range(3):
        xa = X(96) + i * 0.0035
        parts += gk.decal(f"puerto{i}", gk.rect(xa, BORE - P.L(9), xa + 0.0018, BORE + P.L(9)), P.L(15.5), dark)
    parts.append(gk.tube("manguito", X(155), X(100), P.L(16), m, z=BORE, segs=20))
    parts += gk.slab("base_alza", P.cut([(155, 470), (196, 470), (198, 547), (155, 547)]), 0.020, m, bevel=0.0015)
    parts += gk.slab("orejas", P.poly([(156, 452), (176, 452), (178, 472), (156, 472)]), 0.014, m, bevel=0.001)
    parts += gk.slab("poste", P.poly([(163, 446), (169, 446), (169, 460), (163, 460)]), 0.003, m, bevel=0.0)
    parts.append(gk.tube("canon", X(272), X(195), P.L(12), m, z=BORE, segs=20))
    parts.append(gk.tube("tubo_gases", X(275), X(196), P.L(13), m, z=Z(486), segs=18))
    parts.append(gk.tube("bloque_gas", X(215), X(196), P.L(17), m, z=Z(486), segs=18))
    parts.append(gk.tube("baqueta", X(420), X(158), P.L(3), m, z=Z(546), segs=8))

    # --- guardamanos: tapa del tubo de gases redondeada arriba, guardamanos inferior con ventilación
    parts.append(gk.lathe_x("guarda_sup", [(X(472), P.L(18)), (X(472), P.L(24)), (X(406), P.L(24)),
                                           (X(400), P.L(22)), (X(276), P.L(22)), (X(270), P.L(18))], p,
                            z=Z(482), segs=22))
    lo = P.cut([(268, 503), (472, 503), (472, 548), (440, 556), (395, 556), (380, 547), (268, 547)])
    parts += gk.slab("guarda_inf", lo, 0.030, p, bevel=0.004, segs=3)
    for i in range(4):
        x = 292 + i * 11
        parts += gk.decal(f"vent{i}", P.poly((x, 510, x + 5, 540)), 0.0151, dark)
    for i, x in enumerate((345, 372)):
        parts += gk.decal(f"nervio{i}", P.poly((x, 506, x + 3, 545)), 0.0152, m, depth=0.001)

    # --- cajón con tapa redondeada, remaches, selector, montura lateral con riel
    parts += gk.slab("cajon", P.cut((468, 462, 786, 542)), 0.024, m, bevel=0.0015)
    parts += gk.slab("tapa", P.cut((476, 452, 770, 474)), 0.025, m, bevel=0.006, segs=4)
    parts += gk.slab("munon", P.cut((466, 470, 500, 545)), 0.026, m, bevel=0.0015)
    for i, (x, y) in enumerate(((480, 520), (490, 532), (742, 528), (754, 528), (548, 532), (560, 532))):
        parts += gk.decal(f"remache{i}", gk.circle(*P.pt(x, y), P.L(3.5), n=10), 0.0123, gk.accent("remache", (0.2, 0.2, 0.21)),
                          depth=0.0012)
    parts += gk.slab("selector", P.poly([(550, 478), (712, 482), (712, 492), (560, 492)]), 0.003, m, y=-0.0133,
                     bevel=0.0005)
    parts += gk.slab("montura", P.cut((598, 455, 700, 536)), 0.006, m, y=0.0145, bevel=0.0012)
    parts += gk.slab("puente", P.poly((596, 440, 702, 456)), 0.030, m, bevel=0.0012)
    zt = Z(440)
    parts += gk.rail("riel", X(700), X(598), zt, m)

    # --- guardamonte, cola, empuñadura texturada
    hole = P.poly([(606, 542), (670, 542), (672, 572), (610, 573)])
    parts += gk.slab("guardamonte", P.poly([(596, 538), (680, 538), (682, 581), (600, 581)]).difference(hole),
                     0.009, m, bevel=0.001)
    parts += gk.slab("cola", P.poly([(646, 543), (655, 543), (659, 566), (651, 568)]), 0.004, m, bevel=0.0006)
    grip = P.cut([(672, 538), (786, 528), (786, 640), (776, 662), (705, 668), (672, 560)])
    parts += gk.slab("empunadura", grip, 0.024, p, bevel=0.0035, segs=3)
    parts += gk.panel("textura", grip.intersection(P.poly((690, 560, 790, 650))), 0.024, gk.rubber(), inset=0.004)

    # --- cargador curvo con nervios y culata plegable triangular
    parts += magazine(P)
    parts += gk.slab("bisagra", P.cut((752, 484, 792, 546)), 0.026, m, bevel=0.0015)
    parts += gk.slab("culata", P.cut((786, 484, 1032, 630)), 0.012, m, bevel=0.0012)
    parts += gk.slab("cantonera", P.cut((1026, 484, 1064, 630)), 0.022, m, bevel=0.002, segs=3)

    obj = gk.finish_gun(ID, parts)
    if preview:
        gk.preview(obj, pz.ART / ID / "preview.png")
    gk.export(obj, ID, "rifle", {
        "muzzle": (X(70), 0, BORE),
        "at_optic": (X(650), 0, zt + 0.006),
        "at_light": (0.228, 0, Z(552) - 0.002),
    })


if __name__ == "__main__":
    build("--preview" in sys.argv)
