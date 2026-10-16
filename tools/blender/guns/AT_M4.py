"""AT_M4: carabina M4 con guardamanos RIS (tierra oscura), culata SOPMOD, empuñadura angulada y cargador
gris con base de calavera, calcada de la foto de referencia (guns/siluetas/AT_M4.json, coordenadas en
píxeles de esa foto). Escala del juego (largo como la versión anterior, ~0,50 m).
Uso: python3 tools/blender/guns/AT_M4.py [--preview]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import gunkit as gk  # noqa: E402

ID = "AT_M4"
# empuñadura (borde superior, al centro) -> (0,006, -0,002), como el modelo que ya calzaba en las manos
P_BORE = ((380, 889), (1060, 905))     # dos puntos del eje del cañón en la foto
P = gk.Photo(ID, origin_px=(468, 963), origin=(0.006, -0.002), bore_px=P_BORE, scale=0.000504)
BORE = P.pt(700, 897)[1]          # altura del eje del cañón


def X(px):
    return P.pt(px, 897)[0]


def Z(py):
    return P.pt(700, py)[1]


def tube_px(name, x0, x1, r_px, mat, y_px=None, segs=20, y=0.0, r2_px=None):
    z = P.pt(x0, y_px)[1] if y_px else BORE
    return gk.tube(name, X(x0), X(x1), P.L(r_px), mat, y=y, z=z, segs=segs,
                   r2=P.L(r2_px) if r2_px else None)


def magazine(P):
    """Cargador STANAG gris con base de calavera, en píxeles de la foto (lo usa también parts.py)."""
    g = gk.grey("gris_cargador")
    dark = gk.accent("oscuro", (0.018, 0.018, 0.02))
    parts = []
    mag = P.cut([(588, 1000), (712, 1000), (712, 1125), (588, 1125)])
    body = mag.intersection(P.poly((580, 995, 720, 1102)))
    parts += gk.slab("cargador", body, 0.020, g, bevel=0.0015, segs=2)
    for i, (xa, xb) in enumerate(((604, 610), (626, 632))):
        parts += gk.slab(f"nervio{i}", body.intersection(P.poly([(xa, 1003), (xb, 1003), (xb + 14, 1100),
                                                                 (xa + 14, 1100)])), 0.0215, g, bevel=0.0005,
                         segs=1)
    skull = mag.difference(P.poly((580, 995, 720, 1101))).union(P.poly([(612, 1099), (698, 1099), (702, 1124),
                                                                         (616, 1127)]))
    parts += gk.slab("calavera", skull, 0.025, gk.accent("calavera", (0.06, 0.06, 0.065)), bevel=0.002, segs=3)
    for i, xe in enumerate((637, 670)):
        parts += gk.decal(f"ojo{i}", gk.circle(*P.pt(xe, 1110), P.L(8), n=12, sz=1.2), 0.0127, dark, depth=0.001)
    parts += gk.decal("nariz", P.poly([(650, 1116), (658, 1116), (654, 1122)]), 0.0127, dark, depth=0.001)
    return parts


def build(preview=False):
    pz.reset()
    m, p = gk.black_metal(), gk.polymer()
    ris = gk.accent("tierra_oscura", (0.15, 0.125, 0.095))
    dark = gk.accent("oscuro", (0.018, 0.018, 0.02))
    anod = gk.accent("anodizado", (0.10, 0.10, 0.11))
    rub = gk.rubber()
    parts = []

    # --- culata SOPMOD: cuerpo ancho arriba, patas más finas abajo, cantonera de goma
    parts += gk.slab("culata_sup", P.cut((96, 860, 335, 944)), 0.036, p, bevel=0.003, segs=3)
    parts += gk.slab("culata_inf", P.cut((96, 940, 335, 1035)), 0.024, p, bevel=0.002, segs=3)
    parts += gk.slab("cantonera", P.cut((80, 860, 100, 1035)), 0.038, rub, bevel=0.002, segs=3)
    for i, (y0, y1) in enumerate(((955, 975), (985, 1002))):
        parts += gk.decal(f"ranura{i}", P.poly((101, y0, 109, y1)), 0.0122, dark)
    parts += gk.decal("traba", gk.circle(*P.pt(152, 990), P.L(7)), 0.0122, dark)
    # tubo buffer + tuerca castillo + placa
    parts.append(tube_px("buffer", 300, 418, 19, anod))
    parts.append(tube_px("tuerca", 412, 428, 23, m, segs=12))

    # --- cajón inferior (con guardamonte calado) y brocal
    trig_hole = P.poly([(512, 968), (580, 967), (588, 975), (586, 992), (520, 993), (510, 984)])
    lower = P.cut([(423, 905), (712, 905), (716, 1003), (505, 1003), (500, 964), (423, 962)]).difference(trig_hole)
    parts += gk.slab("inferior", lower, 0.0215, m, bevel=0.0012, segs=2)
    parts += gk.slab("brocal", P.cut((588, 935, 716, 1003)), 0.024, m, bevel=0.0015, segs=2)
    guard = P.poly([(503, 960), (594, 960), (594, 1001), (512, 1001), (503, 990)]).difference(trig_hole)
    parts += gk.slab("guardamonte", guard, 0.012, m, bevel=0.001)
    parts += gk.slab("cola", P.poly([(527, 968), (535, 968), (540, 988), (533, 991)]), 0.004, m, bevel=0.0006)
    for i, (x, y, r) in enumerate(((468, 935, 5), (532, 941, 3.5), (560, 943, 3.5), (706, 936, 5))):
        parts.append(gk.pin(f"perno{i}", *P.pt(x, y), P.L(r), m, 0.0115))
    parts.append(gk.screw_y("selector", *P.pt(497, 948), P.L(8), m, -0.0115, depth=0.003))
    parts.append(gk.screw_y("retenida", *P.pt(608, 948), P.L(7), dark, -0.0125, depth=0.003))

    # --- cajón superior, riel, puerta de expulsión, asistente de cierre, deflector, palanca de carga
    parts += gk.slab("superior", P.cut((428, 858, 690, 908)), 0.026, m, bevel=0.0015, segs=2)
    zt = Z(858)
    parts += gk.rail("riel_sup", P.pt(440, 858)[0], P.pt(690, 858)[0], zt, m)
    parts += gk.decal("puerta", P.poly((566, 878, 662, 906)), -0.0132, anod, depth=0.0012, both=False)
    parts += gk.decal("varilla", P.poly((575, 889, 650, 893)), -0.0138, m, depth=0.0008, both=False)
    parts.append(gk.tube("asistente", X(470), X(540), P.L(8), m, y=-0.012, z=Z(888),
                         segs=14))
    parts += gk.slab("deflector", P.poly([(540, 866), (552, 866), (552, 900), (540, 896)]), 0.006, m, y=-0.013,
                     bevel=0.001)
    parts += gk.slab("palanca_carga", P.poly([(430, 858), (452, 858), (452, 868), (430, 866)]), 0.020, m,
                     bevel=0.001)

    # --- guardamanos RIS: cuerpo octogonal, 4 rieles, dos filas de agujeros a cada lado
    x0, x1 = X(690), X(996)
    zc, r = Z(895), P.L(38)
    parts += gk.quad_rail("ris", x0, x1, zc, r, ris, side_dz=Z(915) - zc)
    for i in range(13):
        x = 712 + i * 22
        parts += gk.decal(f"agujero{i}", gk.circle(*P.pt(x, 880), P.L(6), n=12, sx=1.0, sz=0.8), r * 0.93, dark)

    # --- cañón y apagallamas A2 (jaula con ventanas)
    parts.append(tube_px("canon", 990, 1012, 7, m))
    fx0, fx1 = X(1010), X(1090)
    parts.append(gk.lathe_x("apagallamas", [(fx0, P.L(8)), (fx0 + 0.003, P.L(10)), (fx1 - 0.004, P.L(10.5)),
                                            (fx1, P.L(9.5)), (fx1, P.L(5))], m, z=BORE, segs=20))
    for i in range(5):
        xa = fx0 + 0.008 + i * 0.0045
        parts += gk.decal(f"jaula{i}", gk.rect(xa, BORE - P.L(5), xa + 0.0022, BORE + P.L(5)), P.L(10.2), dark)

    # --- empuñadura con panel texturado, empuñadura angulada
    grip = P.cut([(423, 952), (505, 960), (505, 1000), (470, 1105), (418, 1105), (400, 1060)])
    parts += gk.slab("empunadura", grip, 0.022, p, bevel=0.003, segs=3)
    parts += gk.panel("textura", grip.intersection(P.poly((400, 995, 505, 1105))), 0.022, rub, inset=0.003)
    parts += gk.slab("afg", P.cut((788, 930, 888, 998)), 0.017, p, bevel=0.0025, segs=3)

    # --- cargador gris con nervaduras y base de calavera (el mismo modelo que el ítem AT_SkullMag)
    parts += magazine(P)

    obj = gk.finish_gun(ID, parts)
    if preview:
        gk.preview(obj, pz.ART / ID / "preview.png")
    gk.export(obj, ID, "rifle", {
        "muzzle": (X(1090), 0, BORE),
        "at_optic": (X(560), 0, zt + 0.006),
        "at_light": (0.255, 0, zc - r - 0.007),
    })


if __name__ == "__main__":
    build("--preview" in sys.argv)
