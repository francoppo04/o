"""AT_Marlin336: carabina de palanca táctica (tipo Marlin 336 "Dark"): culata esqueleto con portacartuchos,
palanca de lazo grande con cordón, guardamanos M-LOK, tubo cargador y freno de boca. Medida a mano sobre la
foto de referencia enderezada (tools/trace_photo.py --rotate -60.5646; el fondo de madera no deja calcarla
sola): todos los puntos son píxeles de esa foto girada.
Uso: python3 tools/blender/guns/AT_Marlin336.py [--preview]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import gunkit as gk  # noqa: E402

ID = "AT_Marlin336"
P = gk.Photo(ID, origin_px=(590, 695), origin=(0.0, 0.0), scale=0.000405, silhouette=False)
BY = 597
BORE = P.pt(900, BY)[1]


def X(px):
    return P.X(px, BY)


def Z(py):
    return P.pt(900, py)[1]


def build(preview=False):
    pz.reset()
    m, p = gk.black_metal(), gk.polymer()
    dark = gk.accent("oscuro", (0.018, 0.018, 0.02))
    b = gk.brass()
    cord = gk.accent("cordon", (0.07, 0.075, 0.07))
    parts = []

    # --- culata esqueleto: cuerpo con carrillera ranurada, barra inferior, cantonera, portacartuchos
    parts += gk.slab("cantonera", P.poly([(156, 686), (203, 690), (205, 906), (162, 906)]), 0.030, gk.rubber(),
                     bevel=0.003, segs=3)
    for i in range(9):
        y = 700 + i * 22
        parts += gk.decal(f"goma{i}", P.poly([(160, y), (200, y + 6), (200, y + 12), (160, y + 6)]), 0.0151, dark,
                          depth=0.0006)
    parts += gk.slab("culata", P.poly([(200, 690), (448, 682), (472, 700), (472, 792), (200, 802)]), 0.024, p,
                     bevel=0.003, segs=3)
    parts += gk.slab("carrillera", P.poly([(232, 652), (440, 660), (448, 690), (232, 694)]), 0.022, p, bevel=0.003,
                     segs=3)
    for i in range(7):
        x = 246 + i * 28
        parts += gk.decal(f"ranura{i}", P.poly((x, 664, x + 20, 684)), 0.0111, dark)
    parts += gk.slab("barra", P.poly([(200, 850), (482, 784), (500, 808), (204, 880)]), 0.018, p, bevel=0.002,
                     segs=3)
    parts += gk.slab("pata", P.poly([(200, 795), (222, 795), (222, 860), (200, 866)]), 0.020, p, bevel=0.002)
    parts += gk.slab("portacartuchos", P.poly([(214, 722), (432, 718), (434, 792), (216, 796)]), 0.006,
                     gk.accent("placa", (0.05, 0.05, 0.055)), y=-0.0145, bevel=0.0012)
    for i in range(7):
        x, z = P.pt(250 + i * 27, 757)
        parts.append(pz.cylinder(f"cartucho{i}", P.L(7), P.L(56), loc=(x, -0.0175, z), rot=(0, 0, 0), mat=b, segs=10))
        parts.append(pz.cylinder(f"punta{i}", P.L(6), P.L(14), loc=(x, -0.0175, z + P.L(35)), rot=(0, 0, 0),
                                 mat=gk.accent("punta", (0.55, 0.12, 0.08)), segs=10, r2=P.L(2)))
    for i, (x, y) in enumerate(((240, 710), (380, 706), (480, 793))):
        parts.append(gk.screw_y(f"tornillo{i}", *P.pt(x, y), P.L(6), m, -0.0125, depth=0.002))

    # --- garganta / empuñadura (con logo) y cajón con ventana de expulsión y portilla de carga
    wrist = P.poly([(445, 690), (540, 652), (642, 600), (656, 640), (652, 692), (606, 706), (578, 750), (562, 800),
                    (472, 808), (466, 760)])
    parts += gk.slab("garganta", wrist, 0.026, p, bevel=0.004, segs=3)
    parts += gk.panel("textura", wrist.intersection(P.poly((470, 680, 570, 800))), 0.026, gk.rubber(), inset=0.003)
    rec = P.poly([(638, 600), (824, 600), (824, 682), (762, 682), (702, 693), (650, 694)])
    parts += gk.slab("cajon", rec, 0.024, m, bevel=0.002, segs=3)
    parts += gk.decal("expulsion", P.poly((720, 610, 806, 628)), -0.0121, dark, depth=0.0014, both=False)
    parts += gk.decal("portilla", P.poly((746, 638, 800, 655)), -0.0122, gk.accent("portilla", (0.11, 0.11, 0.12)),
                      depth=0.0016, both=False)
    for i, (x, y) in enumerate(((656, 650), (668, 638), (694, 640), (670, 664), (772, 662))):
        parts.append(gk.pin(f"perno{i}", *P.pt(x, y), P.L(4), m, 0.0122))
    parts += gk.slab("martillo", P.poly([(584, 640), (600, 630), (640, 612), (642, 626), (604, 648), (588, 652)]),
                     0.008, m, bevel=0.0008)

    # --- palanca de lazo grande con cordón, cola del disparador
    loop = [(700, 690), (703, 735), (690, 756), (660, 786), (625, 815), (595, 836), (568, 842), (555, 818),
            (557, 782), (575, 750), (606, 726), (646, 710), (662, 700)]
    parts += gk.slab("palanca", P.line(loop, 11), 0.008, m, bevel=0.0012, segs=2)
    parts += gk.slab("cordon", P.line(loop[1:7], 17), 0.0105, cord, bevel=0.002, segs=2)
    for i in range(10):
        x0, y0 = loop[1]
        x1, y1 = loop[6]
        t = (i + 0.5) / 10
        cx, cz = P.pt(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)
        parts += gk.decal(f"vuelta{i}", gk.circle(cx, cz, P.L(3), n=8), 0.0054, dark, depth=0.0008)
    parts += gk.slab("cola", P.poly([(664, 698), (673, 698), (675, 730), (667, 733)]), 0.004, m, bevel=0.0006)

    # --- guardamanos M-LOK, riel superior largo
    fore = P.poly([(822, 590), (1052, 590), (1052, 668), (1010, 680), (822, 684)])
    parts += gk.slab("guardamanos", fore, 0.030, m, bevel=0.004, segs=3)
    for i in range(5):
        x = 842 + i * 40
        parts += gk.decal(f"mlok_a{i}", P.poly((x, 604, x + 30, 616)), 0.0151, dark)
        parts += gk.decal(f"mlok_b{i}", P.poly((x, 646, x + 30, 658)), 0.0151, dark)
    zt = Z(584)
    parts += gk.rail("riel", X(622), X(1050), zt - 0.003, m, h=0.004)
    parts += gk.slab("base_riel", P.poly((622, 584, 1050, 600)), 0.014, m, bevel=0.001)

    # --- cañón, tubo cargador con tapa y abrazadera, freno de boca
    parts.append(gk.tube("canon", X(1050), X(1442), P.L(12), m, z=BORE, segs=22))
    parts.append(gk.tube("tubo_cargador", X(1050), X(1345), P.L(11), m, z=Z(628), segs=20))
    parts.append(gk.lathe_x("tapa_tubo", [(X(1342), P.L(12)), (X(1346), P.L(13)), (X(1372), P.L(13)),
                                          (X(1376), P.L(10)), (X(1376), P.L(4))], m, z=Z(628), segs=20))
    parts += gk.slab("abrazadera", P.poly((1342, 590, 1360, 640)), 0.016, m, bevel=0.0015)
    parts.append(gk.lathe_x("freno", [(X(1438), P.L(13)), (X(1442), P.L(16)), (X(1486), P.L(16)),
                                      (X(1492), P.L(14)), (X(1492), P.L(5))], m, z=BORE, segs=22))
    for i in range(3):
        xa = X(1450) + i * 0.0045
        parts += gk.decal(f"puerto{i}", gk.rect(xa, BORE - P.L(8), xa + 0.0025, BORE + P.L(8)), P.L(15.5), dark)

    obj = gk.finish_gun(ID, parts)
    if preview:
        gk.preview(obj, pz.ART / ID / "preview.png")
    gk.export(obj, ID, "rifle", {
        "muzzle": (X(1492), 0, BORE),
        "at_optic": (X(760), 0, zt + 0.004),
        "at_light": (X(1030), 0, Z(684) - 0.001),
    })


if __name__ == "__main__":
    build("--preview" in sys.argv)
