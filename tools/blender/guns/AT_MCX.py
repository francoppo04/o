"""AT_MCX: carabina compacta tipo MCX con guardamanos M-LOK largo, culata plegable esqueleto, empuñadura
angulada y cargador translúcido con las vainas a la vista, calcada de la foto de referencia
(guns/siluetas/AT_MCX.json, píxeles de esa foto; misma foto y escala que AT_M4).
Uso: python3 tools/blender/guns/AT_MCX.py [--preview]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import gunkit as gk  # noqa: E402

ID = "AT_MCX"
P_BORE = ((420, 160), (920, 157))     # dos puntos del eje del cañón en la foto
P = gk.Photo(ID, origin_px=(405, 210), origin=(0.006, -0.002), bore_px=P_BORE, scale=0.000504)
BY = 158                           # fila del eje del cañón en la foto
BORE = P.pt(700, BY)[1]


def X(px):
    return P.X(px, BY)


def Z(py):
    return P.pt(700, py)[1]


def magazine(P):
    """Cargador translúcido: cuerpo ahumado, ventana con vainas de latón, base (píxeles de la foto)."""
    smoke = gk.accent("translucido", (0.12, 0.105, 0.075))
    b = gk.accent("laton_vainas", (0.40, 0.30, 0.12))
    dark = gk.accent("oscuro", (0.018, 0.018, 0.02))
    parts = []
    mag = P.poly([(505, 226), (600, 226), (606, 300), (615, 366), (528, 372), (511, 300)])
    body = mag.intersection(P.poly((495, 220, 630, 360)))
    parts += gk.slab("cargador", body, 0.020, smoke, bevel=0.0015)
    win = body.buffer(-0.0048, join_style=2).intersection(P.poly((495, 240, 630, 352)))
    parts += gk.slab("vainas", win, 0.0212, b, bevel=0.0004, segs=1)
    for i in range(10):
        y = 246 + i * 10.5
        parts += gk.decal(f"vaina{i}", win.intersection(P.poly((490, y, 630, y + 2.2))), 0.0107, dark, depth=0.0006)
    parts += gk.slab("base", mag.difference(P.poly((495, 220, 630, 358))), 0.023, dark, bevel=0.002, segs=3)
    return parts


def build(preview=False):
    pz.reset()
    m, p = gk.black_metal(), gk.polymer()
    dark = gk.accent("oscuro", (0.018, 0.018, 0.02))
    anod = gk.accent("anodizado", (0.10, 0.10, 0.11))
    parts = []

    # --- culata plegable esqueleto + bisagra
    parts += gk.slab("culata", P.cut((100, 122, 336, 272)), 0.016, p, bevel=0.002, segs=3)
    parts += gk.slab("cantonera", P.cut((100, 135, 128, 272)), 0.026, gk.rubber(), bevel=0.002, segs=3)
    for i in range(3):
        x = 170 + i * 50
        parts += gk.decal(f"ranura{i}", P.poly((x, 150, x + 38, 156)), 0.0081, dark)
    parts += gk.slab("bisagra", P.cut((334, 125, 368, 212)), 0.024, m, bevel=0.0015)
    parts.append(gk.pin("bisagra_perno", *P.pt(350, 150), P.L(5), m, 0.0125))

    # --- cajón inferior, guardamonte calado, cola, controles
    hole = P.poly([(456, 202), (502, 202), (504, 230), (462, 233)])
    parts += gk.slab("inferior", P.cut((362, 160, 606, 226)).difference(hole), 0.0215, m, bevel=0.0012)
    guard = P.poly([(445, 196), (512, 196), (512, 238), (452, 240)]).difference(hole)
    parts += gk.slab("guardamonte", guard, 0.012, m, bevel=0.001)
    parts += gk.slab("cola", P.poly([(468, 203), (476, 203), (480, 225), (472, 227)]), 0.004, m, bevel=0.0006)
    parts += gk.slab("brocal", P.cut((500, 190, 606, 232)), 0.024, m, bevel=0.0015)
    for i, (x, y, r) in enumerate(((447, 182, 4), (470, 183, 4), (530, 172, 4), (372, 170, 5))):
        parts.append(gk.pin(f"perno{i}", *P.pt(x, y), P.L(r), m, 0.0115))
    parts.append(gk.screw_y("selector", *P.pt(398, 183), P.L(8), m, -0.0115, depth=0.003))
    parts.append(gk.screw_y("retenida", *P.pt(540, 185), P.L(7), dark, -0.0125, depth=0.003))

    # --- cajón superior con riel corrido, puerta de expulsión, palanca de carga
    parts += gk.slab("superior", P.cut((345, 119, 580, 163)), 0.025, m, bevel=0.0015)
    zt = Z(117)
    parts += gk.rail("riel_sup", X(372), X(882), zt, m)
    parts += gk.decal("puerta", P.poly((452, 134, 540, 158)), -0.0128, anod, depth=0.0012, both=False)
    parts += gk.slab("palanca_carga", P.poly([(346, 117), (372, 117), (372, 127), (346, 127)]), 0.022, m,
                     bevel=0.001)

    # --- guardamanos M-LOK: ranuras largas arriba, oblicuas abajo, agujero del regulador
    hg = P.cut([(578, 115), (884, 112), (884, 178), (840, 198), (578, 200)])
    parts += gk.slab("guardamanos", hg, 0.034, m, bevel=0.004, segs=3)
    for i in range(5):
        x = 652 + i * 45
        parts += gk.decal(f"mlok_a{i}", P.poly((x, 125, x + 34, 138)), 0.0171, dark)
        parts += gk.decal(f"mlok_b{i}", P.poly([(x - 10, 162), (x + 18, 162), (x + 30, 188), (x + 2, 188)]),
                          0.0171, dark)
    parts += gk.decal("regulador", gk.circle(*P.pt(640, 150), P.L(9), n=16), 0.0171, dark)
    parts += gk.decal("regulador_c", gk.circle(*P.pt(640, 150), P.L(5), n=12), 0.0175, m)

    # --- cañón y apagallamas
    parts.append(gk.tube("canon", X(880), X(895), P.L(8), m, z=BORE))
    parts.append(gk.lathe_x("apagallamas", [(X(893), P.L(9)), (X(898), P.L(12)), (X(948), P.L(12)),
                                            (X(955), P.L(10)), (X(955), P.L(5))], m, z=BORE, segs=20))
    for i in range(4):
        xa = X(905) + i * 0.0055
        parts += gk.decal(f"puerto{i}", gk.rect(xa, BORE - P.L(6), xa + 0.0025, BORE + P.L(6)), P.L(11.6), dark)

    # --- empuñadura texturada y empuñadura angulada
    grip = P.cut([(350, 200), (434, 205), (434, 240), (420, 322), (352, 318), (340, 255)])
    parts += gk.slab("empunadura", grip, 0.022, p, bevel=0.003, segs=3)
    parts += gk.panel("textura", grip.intersection(P.poly((330, 240, 440, 325))), 0.022, gk.rubber(), inset=0.003)
    parts += gk.slab("afg", P.cut((728, 190, 808, 258)), 0.017, p, bevel=0.0025, segs=3)

    # --- cargador translúcido (el mismo modelo que el ítem AT_LancerMag)
    parts += magazine(P)

    obj = gk.finish_gun(ID, parts)
    if preview:
        gk.preview(obj, pz.ART / ID / "preview.png")
    gk.export(obj, ID, "rifle", {
        "muzzle": (X(955), 0, BORE),
        "at_optic": (X(470), 0, zt + 0.006),
        "at_light": (0.236, 0, Z(186) - 0.006),
    })


if __name__ == "__main__":
    build("--preview" in sys.argv)
