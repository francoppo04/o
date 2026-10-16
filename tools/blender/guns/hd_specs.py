"""Fichas de las armas HD (ver hd.py). Coordenadas en píxeles de la imagen de referencia de cada arma;
anchos (w) en mm reales. Escala:
  * fotos del usuario (MCX, AK, G-19): 0,802 mm/px, medido con el paso del riel Picatinny (ver AT_M4);
  * Marlin: largo publicado del Marlin 336 "Dark" (876 mm) sobre la foto enderezada;
  * lámina conceptual: largo del arma real más parecida (referencias/HD/medidas.md).
K = factor real -> juego (fusiles 0,628 como la M4 probada; pistolas 0,898 como la G-19 probada)."""

FOTO = "9.webp"
K_R = 0.000504 / 0.000802          # 0,628: mismo tamaño de juego que las armas ya probadas
K_P = 0.00072 / 0.000802           # 0,898

COLORS = {  # albedo lineal
    "anod": (0.052, 0.054, 0.058), "acero": (0.075, 0.074, 0.072), "pol": (0.06, 0.061, 0.064),
    "goma": (0.035, 0.035, 0.037), "cubierta": (0.30, 0.31, 0.32), "carg": (0.30, 0.32, 0.33),
    "ris": (0.06, 0.058, 0.055), "fde": (0.40, 0.33, 0.22), "fde_osc": (0.25, 0.20, 0.13),
    "od": (0.17, 0.19, 0.12), "od_osc": (0.10, 0.11, 0.075), "plata": (0.55, 0.56, 0.58),
    "marron": (0.30, 0.19, 0.10), "madera": (0.33, 0.19, 0.09), "gris_claro": (0.42, 0.44, 0.45),
    "azul_osc": (0.075, 0.09, 0.12), "laton": (0.62, 0.45, 0.16), "vidrio": (0.03, 0.06, 0.09),
    "naranja": (0.80, 0.28, 0.05), "ahumado": (0.11, 0.095, 0.07), "pavon": (0.08, 0.09, 0.10),
    "gris": (0.16, 0.165, 0.17), "oscuro": (0.018, 0.018, 0.02),
}

SPEC = {}

# =====================================================================================================
# MCX (foto 9)
SPEC["AT_MCX"] = dict(
    img=FOTO, sil="AT_MCX", mm_px=0.802, origin=(405, 210), bore=((420, 160), (920, 157)), bore_y=158,
    K=K_R, offset=(0.006, -0.002), kind="rifle",
    exclude=[[(280, 0), (980, 0), (980, 111), (280, 111)]],
    holes=[[(456, 202), (502, 202), (504, 230), (462, 233)]],
    parts=[
        ("s", "culata", (100, 122, 336, 272), 18, "anod", {"bevel": 1.5, "segs": 2}),
        ("s", "cantonera", (100, 135, 128, 272), 40, "goma", {"round": True, "bevel": 6}),
        ("s", "bisagra", (334, 125, 368, 212), 26, "anod", {}),
        ("pin", 350, 150, 4, 26),
        ("s", "inferior", (362, 160, 606, 226), 23.6, "anod", {"holes": [[(456, 202), (502, 202), (504, 230),
                                                                         (462, 233)]]}),
        ("s", "guardamonte", (440, 194, 515, 250), 13, "anod",
         {"holes": [[(456, 202), (502, 202), (504, 230), (462, 233)]], "bevel": 1.2}),
        ("s", "cola", [(468, 203), (476, 203), (480, 225), (472, 227)], 5.6, "acero", {"cut": False}),
        ("s", "brocal", (500, 190, 606, 232), 29, "anod", {}),
        ("pin", 447, 182, 3.6, 23.6), ("pin", 470, 183, 3.6, 23.6), ("pin", 530, 172, 3.6, 23.6),
        ("pin", 372, 170, 4, 23.6),
        ("cyl", "selector", 398, 183, 5.5, -14, -11.8, "anod"),
        ("cyl", "reten_cargador", 540, 185, 5.2, -17, -14.5, "acero"),
        ("s", "superior", (345, 119, 580, 163), 30, "anod", {"ct": 3.5}),
        ("box", "palanca_carga", 346, 117, 372, 127, -11, 11, "anod"),
        ("rail", "riel_sup", 372, 882, 119, "top"),
        ("s", "guardamanos", [(578, 119), (886, 116), (886, 206), (578, 206)], 48, "anod",
         {"ct": 6, "cb": 14, "bevel": 1.0, "segs": 2}),
        ("lathe", "canon", [(880, 6.4), (895, 6.4)], 158, "acero"),
        ("lathe", "apagallamas", [(893, 7.2), (898, 9.6), (948, 9.6), (955, 8.0)], 158, "acero", 18),
        ("s", "empunadura", [(345, 200), (436, 205), (436, 240), (424, 335), (345, 335), (335, 255)], 28, "pol",
         {"round": True}),
        ("s", "afg", (728, 190, 808, 258), 34, "pol", {"round": True}),
    ],
    mag=dict(region=(498, 224, 625, 360), w=23, mat="ahumado", o={"bevel": 1.2},
             base=[(519, 357), (612, 354), (614, 372), (523, 374)], base_mat="pol"),
    decals=[
        ("poly", [(452, 134), (540, 134), (540, 158), (452, 158)], (62, 64, 68), "R"),
        ("line", [(458, 146), (534, 146)], 1.2, (20, 20, 22), "R"),
        *[("slot", 652 + i * 45, 125, 686 + i * 45, 138) for i in range(5)],
        *[("poly", [(642 + i * 45, 162), (670 + i * 45, 162), (682 + i * 45, 188), (654 + i * 45, 188)], (8, 8, 9))
          for i in range(5)],
        ("hole", 640, 150, 9, 9),
        *[("slot", 903 + i * 11, 151, 907 + i * 11, 164) for i in range(4)],
        *[("slot", 170 + i * 50, 150, 208 + i * 50, 156) for i in range(3)],
        ("stip", [(358, 240), (430, 243), (418, 312), (360, 306)]),
        ("poly", [(516, 240), (592, 240), (598, 300), (603, 346), (527, 349), (519, 300)], (118, 90, 40)),
        *[("line", [(518, 246 + i * 10.5), (600, 246 + i * 10.5)], 1.6, (25, 22, 16)) for i in range(10)],
        ("text", 430, 178, "SAFE", 3.0, "L"), ("text", 430, 192, "FIRE", 3.0, "L"),
    ],
    att=dict(muzzle=955, optic=(470, 112), light=(861, 184)),
)


def _oct(x, y, r=2.2):
    import math
    return [(x + r * math.cos(i * math.pi / 4), y + r * math.sin(i * math.pi / 4)) for i in range(8)]


# =====================================================================================================
# AK-101 (foto 9; la boca apunta a la izquierda)
_AK_HOLE = [(606, 542), (670, 542), (672, 572), (610, 573)]
SPEC["AT_AK101"] = dict(
    img=FOTO, sil="AT_AK101", mm_px=0.802, origin=(726, 541), bore=((85, 524), (460, 524)), bore_y=524,
    flip=True, K=K_R, offset=(0.006, 0.0), kind="rifle",
    exclude=[[(540, 360), (720, 360), (720, 439), (540, 439)]], holes=[_AK_HOLE],
    parts=[
        ("lathe", "freno", [(70, 12.0), (76, 13.6), (92, 12.8), (100, 10.4)], 524, "pavon", 18),
        ("lathe", "manguito", [(100, 12.8), (155, 12.8)], 524, "pavon", 18),
        ("s", "base_alza", [(155, 470), (196, 470), (198, 547), (155, 547)], 20, "pavon", {}),
        ("s", "orejas", (154, 444, 180, 472), 14, "pavon", {}),
        ("lathe", "canon", [(195, 9.6), (272, 9.6)], 524, "pavon"),
        ("lathe", "tubo_gases", [(196, 10.4), (275, 10.4)], 486, "pavon"),
        ("lathe", "bloque_gas", [(196, 13.6), (215, 13.6)], 486, "pavon"),
        ("lathe", "baqueta", [(158, 2.4), (420, 2.4)], 546, "acero", 8),
        ("lathe", "guarda_sup", [(270, 14.4), (276, 17.6), (400, 17.6), (406, 19.2), (472, 19.2)], 482, "pol", 20),
        ("s", "guarda_inf", [(268, 503), (472, 503), (472, 548), (440, 556), (395, 556), (380, 547), (268, 547)], 46,
         "pol", {"ct": 4, "cb": 12, "bevel": 2, "segs": 2}),
        ("s", "cajon", (468, 462, 786, 542), 30, "pavon", {"ct": 2, "cb": 1.5}),
        ("s", "tapa", (476, 450, 770, 474), 31, "pavon", {"ct": 10, "cb": 0.5}),
        ("s", "munon", (466, 470, 500, 545), 32, "pavon", {}),
        ("s", "montura", (598, 455, 700, 536), 6, "pavon", {"y": 18}),
        ("s", "puente", (596, 440, 702, 456), 32, "pavon", {}),
        ("rail", "riel", 598, 700, 440, "top"),
        ("s", "guardamonte", (594, 536, 684, 584), 10, "pavon", {"holes": [_AK_HOLE], "bevel": 1}),
        ("s", "cola", [(646, 543), (655, 543), (659, 566), (651, 568)], 5.6, "acero", {"cut": False}),
        ("s", "empunadura", [(672, 538), (786, 528), (786, 640), (776, 668), (700, 672), (672, 560)], 30, "pol",
         {"round": True}),
        ("s", "bisagra", (752, 484, 792, 546), 26, "pavon", {}),
        ("s", "culata", (786, 484, 1032, 632), 18, "pavon", {"bevel": 2, "segs": 2}),
        ("s", "cantonera", (1026, 484, 1066, 632), 24, "pavon", {"bevel": 3, "segs": 2}),
    ],
    mag=dict(region=[(500, 538), (597, 538), (592, 620), (568, 778), (425, 778), (425, 700)], w=26, mat="pol",
             o={"bevel": 2.0, "segs": 2}),
    decals=[
        *[("slot", 292 + i * 11, 510, 297 + i * 11, 540) for i in range(4)],
        *[("poly", _oct(x, y), (110, 110, 106)) for x, y in ((480, 520), (490, 532), (742, 528), (754, 528),
                                                              (548, 532), (560, 532))],
        ("line", [(520, 545), (500, 600), (480, 680), (462, 760)], 1.3, (14, 14, 15)),
        ("text", 600, 515, "AK-101  5,56", 3.6, "L"),
        ("stip", [(692, 560), (776, 552), (772, 640), (712, 648)]),
    ],
    att=dict(muzzle=70, optic=(650, 440), light=(285, 552)),
)

# =====================================================================================================
# G-19 (foto 9)
_G19_HOLE = [(200, 336), (257, 336), (259, 352), (252, 364), (206, 364)]
SPEC["AT_G19"] = dict(
    img=FOTO, sil="AT_G19", soften=2.0, mm_px=0.802, origin=(165, 330), bore_y=305, K=K_P, offset=(0.0, 0.0),
    kind="handgun", holes=[_G19_HOLE],
    parts=[
        ("s", "corredera", (118, 285, 340, 320), 25.5, "pavon", {"ct": 4.5, "cb": 1.0, "bevel": 0.8, "segs": 2}),
        ("s", "alza", (128, 281, 142, 292), 12, "pavon", {"cut": False}),
        ("s", "punto", (322, 282, 329, 292), 4, "pavon", {"cut": False}),
        ("lathe", "boca", [(320, 4.6), (331, 4.6)], 305, "oscuro"),         # al ras del frente de la corredera
        ("s", "armazon", [(116, 318), (342, 318), (342, 340), (268, 340), (268, 380), (188, 380), (184, 339),
                          (116, 339)], 28, "pol", {"holes": [_G19_HOLE], "ct": 2, "cb": 3}),
        ("s", "cola", [(220, 330), (230, 330), (233, 358), (226, 361)], 6.2, "pol", {"cut": False}),
        ("s", "empunadura", [(95, 312), (192, 330), (192, 422), (88, 422)], 31, "pol",
         {"round": True, "bevel": 8, "tol": 0.8}),
        ("s", "base", (85, 418, 180, 450), 31, "pol", {"bevel": 3, "segs": 2, "tol": 0.8}),
        ("box", "desarme", 236, 321, 246, 327, -14.6, 14.6, "acero"),
    ],
    decals=[
        ("serr", 128, 176, 293, 317, 8), ("serr", 288, 333, 293, 317, 7),
        ("poly", [(228, 287), (268, 287), (268, 296), (228, 296)], (40, 40, 42), "R"),
        ("slot", 282, 330, 326, 333),
        ("stip", [(120, 348), (182, 348), (166, 404), (108, 402)]),
        ("text", 245, 309, "G19  9x19", 3.0, "L"),
    ],
    att=dict(muzzle=339, light=(312, 337)),
)

# =====================================================================================================
# Marlin 336 táctica (foto enderezada; medida a mano: el fondo de madera no deja calcarla)
_MARLIN_LOOP = [(700, 690), (703, 735), (690, 756), (660, 786), (625, 815), (595, 836), (568, 842), (555, 818),
                (557, 782), (575, 750), (606, 726), (646, 710), (662, 700)]


_MARLIN_CULATA_HUECO = [(230, 778), (443, 778), (442, 738), (474, 742), (480, 784), (228, 834)]


def _band(pts, w):
    from shapely.geometry import LineString
    g = LineString(pts).buffer(w / 2, cap_style=1, join_style=1)
    return [tuple(p) for p in g.exterior.coords][:-1]


def _marlin_palanca():
    from shapely.geometry import Polygon, box
    g = Polygon(_MARLIN_LOOP).buffer(9).union(box(594, 684, 758, 728))
    return [tuple(p) for p in g.exterior.coords][:-1]


_MARLIN_PALANCA = _marlin_palanca()
_MM_MARLIN = 876 / 1332                       # Marlin 336 Dark: 876 mm de largo
SPEC["AT_Marlin336"] = dict(
    img="marlin_rot.png", sil="AT_Marlin336", mm_px=_MM_MARLIN, origin=(590, 695), bore_y=597,
    K=0.000405 / (_MM_MARLIN / 1000), offset=(0.0, 0.0), kind="rifle",
    # la silueta de esta foto es ruidosa (fondo de madera): solo mide, no recorta ni rellena
    sil_cut=False, fill=False,
    # mira telescópica y linterna: accesorios del mod, fuera de la comparación
    # (y el borde inferior de la cantonera, donde el calcado se mete en la sombra)
    exclude=[[(560, 440), (1100, 440), (1100, 583), (560, 583)], [(1058, 612), (1280, 612), (1280, 662), (1058, 662)],
             [(100, 898), (260, 898), (260, 960), (100, 960)]],
    holes=[_MARLIN_CULATA_HUECO],
    parts=[
        ("s", "cantonera", [(156, 686), (203, 690), (205, 906), (162, 906)], 42, "goma", {"round": True, "bevel": 6}),
        # culata esqueleto: cuerpo con portacartuchos arriba, barra abajo, hueco entre los dos
        ("s", "culata", [(200, 690), (448, 678), (486, 672), (488, 742), (474, 740), (442, 736), (445, 778),
                         (200, 778)], 36, "pol", {"bevel": 3, "segs": 2}),
        ("s", "carrillera", [(232, 662), (430, 643), (442, 650), (448, 690), (232, 694)], 34, "pol",
         {"bevel": 5, "segs": 3}),
        ("s", "barra", [(200, 836), (482, 784), (500, 808), (204, 880)], 22, "pol", {"bevel": 3, "segs": 2}),
        ("s", "pata", [(200, 776), (230, 776), (230, 846), (200, 852)], 24, "pol", {}),
        ("s", "portacartuchos", [(230, 700), (440, 700), (440, 776), (230, 776)], 6, "gris", {"y": -21}),
        *[("vcyl", f"cartucho{i}", 265 + i * 22.8, 728, 770, 4.6, -24.5, "laton") for i in range(7)],
        ("s", "garganta", [(445, 680), (486, 676), (515, 686), (575, 664), (640, 641), (656, 640), (652, 692),
                           (606, 706), (578, 750), (562, 800), (472, 808), (466, 760)], 32, "pol",
         {"round": True, "bevel": 8}),
        ("s", "cajon", [(638, 600), (824, 600), (824, 682), (762, 682), (702, 693), (650, 694)], 28, "pavon",
         {"ct": 4}),
        ("s", "martillo", [(582, 664), (588, 640), (604, 633), (614, 636), (608, 652), (600, 662)], 8, "pavon", {}),
        # palanca: contorno del aro (con la parte que corre bajo el cajón) recortado con la silueta de la foto,
        # que da los dos huecos (aro y gatillo)
        ("s", "palanca", _MARLIN_PALANCA, 8, "pavon", {"sil": True, "bevel": 1.2, "segs": 2}),
        ("s", "cordon", _band(_MARLIN_LOOP[1:7], 17), 11, "gris", {"round": True, "bevel": 4, "sil": True}),
        ("s", "cola", [(664, 698), (673, 698), (675, 730), (667, 733)], 5, "acero", {}),
        ("s", "guardamanos", [(822, 590), (1052, 590), (1052, 666), (1010, 677), (822, 681)], 50, "pavon",
         {"ct": 8, "cb": 12, "bevel": 1, "segs": 2}),
        ("s", "base_riel", (622, 584, 1050, 600), 18, "pavon", {}),
        ("rail", "riel", 622, 1050, 584, "top"),
        ("lathe", "canon", [(1050, 8.6), (1418, 8.6)], 597.5, "pavon", 16),
        ("lathe", "tubo_cargador", [(1050, 7.2), (1370, 7.2)], 627, "pavon", 16),
        ("lathe", "tapa_tubo", [(1368, 7.6), (1370, 8.4), (1392, 8.4), (1394, 8.0), (1405, 8.0), (1408, 6.5)],
         627, "pavon", 16),
        ("s", "abrazadera", (1373, 607, 1385, 618), 10, "pavon", {"cut": False}),
        ("lathe", "freno", [(1413, 9.6), (1416, 10.2), (1484, 10.2), (1488, 9.0)], 597.5, "pavon", 18),
        ("s", "base_mira", [(1329, 584), (1333, 571), (1395, 571), (1395, 584)], 9, "pavon", {"cut": False}),
        ("s", "mira", (1351, 557, 1384, 572), 6, "pavon", {"cut": False}),
        ("pin", 656, 650, 2.6, 28), ("pin", 668, 638, 2.6, 28), ("pin", 694, 640, 2.6, 28),
        ("pin", 670, 664, 2.6, 28), ("pin", 772, 662, 2.6, 28),
    ],
    decals=[
        *[("slot", 246 + i * 28, 664, 266 + i * 28, 684) for i in range(7)],
        *[("slot", 842 + i * 40, 604, 872 + i * 40, 616) for i in range(5)],
        *[("slot", 842 + i * 40, 646, 872 + i * 40, 658) for i in range(5)],
        ("slot", 720, 610, 806, 628, "R"),
        ("poly", [(746, 638), (800, 638), (800, 655), (746, 655)], (58, 58, 60), "R"),
        *[("slot", 1440 + i * 14, 589, 1446 + i * 14, 601) for i in range(3)],
        *[("slot", x - 10, y - 3, x + 10, y + 4) for x, y in ((290, 838), (332, 830), (377, 820), (422, 810))],
        ("poly", [(1352, 557), (1383, 557), (1383, 560), (1352, 560)], (90, 210, 70)),
        ("stip", [(478, 690), (560, 668), (565, 740), (500, 790), (475, 780)]),
        *[("line", [(158 + 0, 700 + i * 22), (200, 706 + i * 22)], 2.0, (14, 14, 15)) for i in range(9)],
        ("text", 735, 668, "336  .30-30 WIN", 3.4, "L"),
    ],
    att=dict(muzzle=1488, optic=(760, 584), light=(1035, 684)),
)


# =====================================================================================================
# Las 14 de la lámina conceptual: mismas coordenadas que concepto.py, anchos reales en mm y escala del arma
# real más parecida (largo publicado). Ver referencias/HD/medidas.md.
LAMINA = "11.webp"
ANALOGO = {  # ID: (largo real en mm, arma real de referencia) — fuentes en referencias/HD/medidas.md
    "AT_GXP": (222, "Glock 34"), "AT_MD34": (222, "Glock 34 (con el compensador dentro del largo)"),
    "AT_GravRecon": (202, "Glock 17"), "AT_VikorS1": (203, "CZ P-10 F"),
    "AT_FNPR": (218, "FNX-45 Tactical"), "AT_FNSAR": (500, "FN P90"),
    "AT_QDX99": (500, "QCW-05"), "AT_MX4": (807, "CZ Bren 2 de 11\" (culata extendida)"),
    "AT_AUGA5": (790, "Steyr AUG A3 (cañón 20\")"), "AT_AG203": (935, "AK-12"),
    "AT_Komodo": (889, "SIG MCX Spear 13\""),
    "AT_CycloneAGL": (778, "Milkor MGL"), "AT_RPK101": (1060, "RPK-74M"), "AT_PSR": (894, "VSS Vintorez"),
}
_MAT = {"negro": "anod", "polimero": "pol", "goma": "goma", "fde": "fde", "gris": "gris", "vidrio": "vidrio",
        "laton": "laton", "oscuro": "oscuro", "plata": "plata", "acero": "acero", "oliva": "od",
        "oliva_osc": "od_osc", "fde_osc": "fde_osc", "marron": "marron", "madera": "madera",
        "gris_claro": "gris_claro", "azul_osc": "azul_osc", "pavon": "pavon", "gris_carg": "carg"}
_ROUND = ("empunadura", "afg", "cantonera", "culata", "carrillera", "base", "nariz", "casco", "guarda")


def _srgb(c):
    return tuple(int(255 * (v ** (1 / 2.2))) for v in c)


def _from_concept():
    import concepto
    for ID, sp in concepto.SPEC.items():
        real, _ = ANALOGO[ID]
        mm_px = real / abs(sp["back"] - sp["front"])
        pistol = sp["kind"] == "handgun" and ID not in ("AT_FNSAR", "AT_QDX99")
        K = K_P if pistol else K_R
        f = 1.0 if pistol else 0.75

        def W(th):
            return max(4.0, th / K * 1000 * f)
        use_sil = sp.get("sil", True)
        parts, decals, holes = [], [], []
        for op in sp["parts"]:
            k = op[0]
            if k == "s":
                _, name, reg, th, m, o = op
                no = {"cut": not name.startswith(("cola", "poste", "punto", "alza", "aleta", "torreta", "montura"))}
                hl = [o[h] for h in ("hole", "hole2", "hole3", "hole4") if h in o]
                if hl:
                    no["holes"] = hl
                    holes += hl
                if name.startswith(_ROUND) or name.endswith("_del"):
                    no["round"] = True
                if "panel" in o:
                    x0, y0, x1, y1 = o["panel"]
                    decals.append(("stip", [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]))
                parts.append(("s", name, reg, W(th), _MAT[m], no))
            elif k == "t":
                _, name, x0, x1, r, y, m = op
                parts.append(("lathe", name, [(x0, r * mm_px), (x1, r * mm_px)], y, _MAT[m]))
            elif k == "l":
                _, name, prof, y, m = op
                parts.append(("lathe", name, [(x, r * mm_px) for x, r in prof], y, _MAT[m], 20))
            elif k == "r":
                _, name, x0, x1, y = op
                parts.append(("rail", name, x0, x1, y, "top"))
            elif k == "d":
                _, name, reg, m, th = op
                if len(reg) == 4 and not isinstance(reg[0], (tuple, list)):
                    x0, y0, x1, y1 = reg
                    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
                else:
                    pts = list(reg)
                if m == "oscuro":
                    if len(reg) == 4 and not isinstance(reg[0], (tuple, list)):
                        decals.append(("slot", *reg))
                    else:
                        decals.append(("poly", pts, (8, 8, 9)))
                else:
                    decals.append(("poly", pts, _srgb(COLORS[_MAT[m]])))
            elif k == "slots":
                _, name, x0, x1, y0, y1, n, m, th = op
                w = (x1 - x0) / n
                for i in range(n):
                    decals.append(("slot", x0 + i * w + w * 0.12, y0, x0 + i * w + w * 0.88, y1))
            elif k == "p":
                _, x, y, r, th = op
                parts.append(("pin", x, y, r * mm_px, W(th)))
        spec = dict(img=LAMINA, sil=ID, mm_px=mm_px, origin=sp["origin"], bore_y=sp["bore"],
                    flip=sp["front"] < sp["back"], K=K, offset=(0.0, 0.0) if sp["kind"] == "handgun" else (0.006, -0.002),
                    kind=sp["kind"], parts=parts, decals=decals, holes=holes,
                    att=dict(muzzle=sp["muzzle"][0]), fill_w=24 if pistol else 26,
                    fill_mat="pol" if pistol else "anod", fit_lathes=True)
        if "optic" in sp:
            spec["att"]["optic"] = sp["optic"]
            lo, hi = min(sp["front"], sp["back"]), max(sp["front"], sp["back"])
            spec["exclude"] = [[(lo - 30, 0), (hi + 30, 0), (hi + 30, sp["optic"][1] - 1), (lo - 30, sp["optic"][1] - 1)]]
        if "light" in sp:
            spec["att"]["light"] = sp["light"]
        if "mag" in sp:
            reg, th, m, o = sp["mag"]
            md = dict(region=reg, w=W(th), mat=_MAT[m], o={"cut": True, "bevel": 1.5})
            if "base" in o:
                md["base"] = o["base"]
                md["base_mat"] = _MAT[o.get("base_mat", "oscuro")]
            spec["mag"] = md
        SPEC[ID] = spec


_from_concept()


FIX_ERRORS = {}       # ID -> error al cargar su ficha de hd_fix (hd.Gun(ID) se niega a seguir con la ficha vieja)


def _load_fixes():
    """Fichas corregidas a mano (hd_fix/<ID>.py, creadas con hd_dump.py): reemplazan la ficha entera.
    Un error en una ficha solo frena a esa arma, no a las demás."""
    import importlib.util
    import traceback
    from pathlib import Path
    for f in sorted((Path(__file__).resolve().parent / "hd_fix").glob("AT_*.py")):
        try:
            spec = importlib.util.spec_from_file_location(f"hd_fix_{f.stem}", f)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            SPEC[f.stem] = mod.SPEC
        except Exception:
            FIX_ERRORS[f.stem] = traceback.format_exc()


_load_fixes()
