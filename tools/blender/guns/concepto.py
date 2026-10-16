"""Las 14 armas de la lámina conceptual (GXP ... PSR) y sus cargadores, a partir de una ficha por arma.

Cada ficha da, en píxeles de la lámina (guns/siluetas/<ID>.json; la lámina no va al repo):
  * kind: "rifle" (animaciones de fusil) o "handgun" (pistolas y las PDW compactas, que se empuñan como
    pistola porque la mano izquierda de las animaciones de fusil quedaría delante de la boca);
  * front/back: extremos en x (boca y culata) y L = largo en el juego -> escala;
  * origin: punto de la empuñadura que va al origen; bore: fila del eje del cañón;
  * parts: piezas. ("s", nombre, región, espesor, material, {opciones}) losa; región = caja (x0,y0,x1,y1) o
    polígono; por defecto se recorta con la silueta (cut=False usa la región tal cual); opciones: hole,
    panel (región con textura), bevel, segs, y.
    ("t", nombre, x0, x1, radio, y, material) tubo; ("l", nombre, [(x, radio), ...], y, material) torneado;
    ("r", nombre, x0, x1, y_base) riel; ("d", nombre, región, material, espesor_de_la_pieza) detalle en las
    dos caras; ("slots", nombre, x0, x1, y0, y1, n, material, espesor) fila de ranuras;
    ("p", x, y, radio, espesor) perno pasante;
  * muzzle / optic / light: puntos de montaje (x, y) en la lámina;
  * mag: cargador (región, espesor, material, opciones) para el arma y el ítem suelto; pmag: cargador de
    pistola genérico (largo, material de la base).
Uso: python3 tools/blender/guns/concepto.py [ID ...] [--preview]   (sin IDs: todas las armas y cargadores)
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import gunkit as gk  # noqa: E402

COLORS = {
    "oscuro": (0.018, 0.018, 0.02), "plata": (0.62, 0.63, 0.65), "acero": (0.42, 0.43, 0.45),
    "oliva": (0.21, 0.23, 0.15), "oliva_osc": (0.13, 0.14, 0.10), "fde_osc": (0.28, 0.23, 0.15),
    "marron": (0.33, 0.21, 0.12), "madera": (0.36, 0.22, 0.12), "gris_claro": (0.50, 0.52, 0.53),
    "azul_osc": (0.10, 0.12, 0.16), "pavon": (0.11, 0.13, 0.14), "gris_carg": (0.42, 0.44, 0.45),
}
_MATS = {}


def mat(key):
    if key not in _MATS:
        f = {"negro": gk.black_metal, "polimero": gk.polymer, "goma": gk.rubber, "fde": gk.fde, "gris": gk.grey,
             "vidrio": gk.glass, "laton": gk.brass}.get(key)
        _MATS[key] = f() if f else gk.accent(key, COLORS[key])
    return _MATS[key]


def serr(name, x0, x1, y0, y1, n, m, thick):
    """Estrías: n ranuras verticales entre x0 y x1."""
    w = (x1 - x0) / n
    return [("d", f"{name}{i}", (x0 + i * w + w * 0.25, y0, x0 + i * w + w * 0.75, y1), m, thick) for i in range(n)]


# ------------------------------------------------------------------ fichas
SPEC = {
    # ---------------------------------------------------------------- pistolas
    "AT_GXP": dict(
        kind="handgun", front=213, back=509, L=0.19, origin=(453, 112), bore=78, muzzle=(213, 78),
        light=(345, 112), pmag=(0.072, "oscuro"),
        parts=[
            ("s", "corredera", [(213, 50), (507, 50), (509, 88), (330, 92), (312, 108), (228, 108), (213, 95)],
             0.021, "pavon", {}),
            ("d", "expulsion", (395, 58, 432, 70), "acero", 0.021),
            *serr("estria", 455, 500, 58, 86, 7, "oscuro", 0.021),
            ("d", "compensador", (232, 60, 300, 70), "oscuro", 0.021),
            ("s", "alza", (488, 44, 505, 52), 0.012, "negro", {"cut": False}),
            ("s", "punto", (222, 45, 236, 52), 0.004, "negro", {"cut": False}),
            ("s", "armazon", [(312, 86), (509, 86), (512, 112), (312, 110)], 0.022, "polimero", {"cut": False}),
            ("s", "guardamonte", [(362, 108), (432, 108), (432, 145), (392, 145), (370, 128)], 0.010, "polimero",
             {"cut": False, "hole": [(384, 111), (424, 111), (422, 136), (395, 136)]}),
            ("s", "cola", [(402, 112), (410, 112), (412, 132), (405, 134)], 0.005, "polimero", {"cut": False}),
            ("s", "empunadura", [(428, 108), (503, 103), (526, 200), (500, 206), (462, 206), (445, 150)], 0.0245,
             "polimero", {"panel": (440, 128, 520, 190), "bevel": 0.0035}),
            ("s", "base", [(455, 192), (524, 189), (527, 204), (458, 206)], 0.0255, "oscuro", {"cut": False}),
        ]),
    "AT_MD34": dict(
        kind="handgun", front=655, back=912, L=0.17, origin=(868, 112), bore=85, muzzle=(655, 85),
        light=(770, 115), pmag=(0.066, "oscuro"),
        parts=[
            ("s", "corredera", [(655, 56), (672, 56), (676, 68), (857, 68), (860, 55), (912, 55), (914, 100),
                                (737, 100), (737, 113), (658, 113)], 0.022, "oliva", {}),
            ("r", "riel", 690, 855, 68),
            *serr("puerto", 665, 732, 76, 96, 4, "oscuro", 0.022),
            *serr("estria", 875, 908, 62, 95, 5, "oscuro", 0.022),
            ("s", "alza", (862, 43, 882, 56), 0.014, "negro", {"cut": False}),
            ("s", "punto", (657, 50, 670, 57), 0.004, "negro", {"cut": False}),
            ("s", "armazon", [(737, 98), (905, 98), (910, 112), (850, 115), (737, 115)], 0.021, "polimero", {}),
            ("s", "guardamonte", [(790, 110), (852, 110), (852, 150), (805, 152), (792, 135)], 0.010, "polimero",
             {"cut": False, "hole": [(806, 113), (845, 113), (840, 140), (812, 142)]}),
            ("s", "cola", [(828, 115), (834, 115), (836, 135), (830, 136)], 0.005, "polimero", {"cut": False}),
            ("s", "empunadura", [(848, 108), (910, 102), (936, 190), (920, 208), (882, 208), (850, 140)], 0.0245,
             "polimero", {"panel": (860, 128, 935, 195), "bevel": 0.0035}),
            ("s", "base", [(880, 200), (930, 195), (935, 210), (882, 212)], 0.0255, "oscuro", {"cut": False}),
        ]),
    "AT_GravRecon": dict(
        kind="handgun", front=213, back=515, L=0.175, origin=(466, 295), bore=266, muzzle=(213, 266),
        light=(370, 298), pmag=(0.074, "plata"),
        parts=[
            ("s", "corredera_del", [(213, 272), (235, 252), (318, 251), (318, 283), (213, 283)], 0.021, "negro", {}),
            ("s", "corredera", [(316, 251), (510, 250), (515, 283), (316, 283)], 0.0212, "plata", {}),
            ("d", "aligerado1", (332, 257, 420, 265), "oscuro", 0.0212),
            ("d", "aligerado2", (432, 262, 480, 270), "oscuro", 0.0212),
            *serr("estria", 470, 508, 256, 280, 6, "acero", 0.0212),
            ("s", "punto", (236, 245, 250, 252), 0.004, "negro", {"cut": False}),
            ("s", "alza", (490, 244, 505, 251), 0.012, "negro", {"cut": False}),
            ("s", "armazon", [(325, 283), (510, 283), (512, 298), (450, 300), (325, 298)], 0.022, "polimero",
             {"cut": False}),
            *serr("riel", 330, 400, 290, 296, 5, "oscuro", 0.022),
            ("s", "guardamonte", [(388, 295), (472, 295), (470, 320), (405, 322), (390, 308)], 0.010, "polimero",
             {"cut": False, "hole": [(402, 298), (455, 298), (452, 315), (410, 316)]}),
            ("s", "cola", [(430, 298), (437, 298), (440, 314), (433, 316)], 0.005, "acero", {"cut": False}),
            ("s", "empunadura", [(446, 290), (510, 284), (524, 345), (517, 395), (470, 395), (452, 330)], 0.0245,
             "polimero", {"panel": (455, 308, 522, 362), "bevel": 0.0035}),
            ("s", "base", [(470, 365), (521, 362), (518, 396), (468, 396)], 0.0255, "plata", {"cut": False}),
        ]),
    "AT_VikorS1": dict(
        kind="handgun", front=688, back=942, L=0.165, origin=(858, 286), bore=262, muzzle=(688, 262),
        light=(730, 292), pmag=(0.072, "oscuro"),
        parts=[
            ("s", "corredera", [(688, 248), (940, 246), (942, 281), (688, 281)], 0.021, "negro", {"cut": False}),
            ("r", "estrias_sup", 700, 800, 248),
            ("s", "aleta", [(800, 250), (806, 233), (818, 236), (830, 250)], 0.012, "negro", {"cut": False}),
            ("d", "expulsion", (850, 254, 910, 264), "acero", 0.021),
            ("s", "armazon", [(688, 279), (915, 279), (915, 292), (700, 292), (700, 305), (688, 305)], 0.022,
             "polimero", {"cut": False}),
            ("s", "guardamonte", [(760, 285), (840, 285), (840, 336), (780, 336), (762, 300)], 0.012, "polimero",
             {"cut": False, "hole": [(792, 292), (832, 292), (830, 320), (798, 320)]}),
            ("s", "cola", [(815, 292), (822, 292), (826, 312), (818, 314)], 0.005, "polimero", {"cut": False}),
            ("s", "empunadura", [(835, 282), (915, 282), (906, 320), (898, 398), (842, 405), (838, 330)], 0.0245,
             "polimero", {"panel": (845, 300, 905, 390), "bevel": 0.0035}),
            ("s", "base", [(838, 395), (898, 388), (902, 402), (842, 410)], 0.0255, "oscuro", {"cut": False}),
        ]),
    "AT_FNPR": dict(
        kind="handgun", front=340, back=532, L=0.165, origin=(468, 505), bore=480, muzzle=(110, 490),
        light=(372, 535), pmag=(0.072, "fde_osc"),
        parts=[
            ("l", "supresor", [(110, 6), (112, 14), (124, 21), (290, 21), (292, 20), (338, 20), (340, 12)], 490,
             "fde_osc"),
            *[("l", f"anillo{i}", [(296 + i * 12, 20.5), (300 + i * 12, 21.5), (304 + i * 12, 20.5)], 490, "fde")
              for i in range(3)],
            ("s", "corredera", [(340, 465), (515, 465), (518, 490), (340, 490)], 0.022, "fde", {"cut": False}),
            *serr("estria", 360, 392, 470, 486, 4, "fde_osc", 0.022),
            *serr("estria_t", 480, 512, 470, 486, 4, "fde_osc", 0.022),
            ("s", "punto_rojo", [(440, 436), (462, 436), (476, 465), (440, 465)], 0.018, "oscuro", {"cut": False}),
            ("d", "lente", (446, 442, 458, 458), "vidrio", 0.018),
            ("s", "alza", (494, 452, 506, 466), 0.012, "negro", {"cut": False}),
            ("s", "punto", (346, 455, 356, 466), 0.004, "negro", {"cut": False}),
            ("s", "placa", (515, 472, 533, 490), 0.020, "fde_osc", {"cut": False}),
            ("s", "armazon", [(340, 488), (520, 488), (520, 505), (445, 508), (395, 508), (340, 505)], 0.022, "fde",
             {"cut": False}),
            ("s", "modulo", [(318, 505), (392, 505), (392, 520), (345, 535), (320, 535)], 0.020, "fde_osc",
             {"cut": False}),
            ("s", "guardamonte", [(395, 505), (445, 505), (445, 532), (405, 532)], 0.010, "fde",
             {"cut": False, "hole": [(410, 508), (437, 508), (435, 525), (412, 525)]}),
            ("s", "cola", [(425, 510), (431, 510), (433, 525), (427, 526)], 0.005, "oscuro", {"cut": False}),
            ("s", "empunadura", [(442, 500), (518, 498), (536, 562), (470, 564), (450, 520)], 0.0245, "fde",
             {"cut": False, "panel": (452, 514, 532, 558), "bevel": 0.0035}),
        ]),
    # ---------------------------------------------------------------- PDW compactas (se empuñan como pistola)
    "AT_FNSAR": dict(
        kind="handgun", front=645, back=1042, L=0.34, origin=(805, 512), bore=490, muzzle=(645, 490),
        optic=(840, 470), light=(680, 560), sil=False,
        mag=([(872, 548), (1000, 548), (992, 592), (882, 592)], 0.038, "oscuro", {}),
        parts=[
            ("s", "receptor", (658, 470, 1035, 505), 0.036, "marron", {"bevel": 0.004, "segs": 3}),
            ("r", "riel", 670, 1030, 470),
            ("t", "boca", 645, 662, 8, 490, "negro"),
            ("d", "ranura_sup", (700, 485, 980, 490), "oscuro", 0.036),
            ("s", "nariz", [(660, 505), (745, 505), (745, 520), (740, 555), (712, 560), (672, 560), (660, 540)],
             0.034, "gris_claro", {"bevel": 0.004, "segs": 3}),
            *serr("ventila", 670, 735, 515, 527, 4, "oscuro", 0.034),
            ("s", "empunadura_del", [(705, 555), (738, 555), (735, 597), (708, 597)], 0.020, "negro",
             {"bevel": 0.003}),
            ("s", "gatillo", [(745, 505), (800, 505), (800, 555), (752, 555)], 0.024, "gris",
             {"hole": [(754, 518), (790, 518), (790, 550), (760, 550)]}),
            ("s", "cola", [(772, 520), (780, 520), (782, 545), (775, 546)], 0.005, "negro", {}),
            ("s", "casco", [(795, 505), (1035, 505), (1035, 548), (995, 552), (960, 562), (825, 612), (812, 600),
                            (795, 560)], 0.036, "gris_claro",
             {"bevel": 0.004, "segs": 3, "hole": [(830, 522), (878, 522), (880, 560), (840, 566), (830, 548)]}),
            ("s", "cantonera", (1028, 470, 1042, 546), 0.038, "goma", {}),
        ]),
    "AT_QDX99": dict(
        kind="handgun", front=108, back=545, L=0.37, origin=(290, 758), bore=708, muzzle=(108, 708),
        optic=(300, 672), light=(130, 742),
        mag=([(380, 760), (452, 760), (452, 801), (380, 801)], 0.034, "oliva", {"cut": False}),
        parts=[
            ("t", "canon", 108, 150, 9, 708, "negro"),
            ("t", "varilla", 112, 150, 6, 731, "negro"),
            ("s", "bloque", (145, 676, 250, 760), 0.030, "negro", {"cut": False, "bevel": 0.003, "segs": 3}),
            *serr("costilla", 150, 200, 700, 755, 5, "oscuro", 0.030),
            ("s", "receptor", (240, 676, 362, 756), 0.028, "negro", {"cut": False}),
            ("r", "riel", 150, 355, 675),
            ("s", "culata", (355, 700, 545, 800), 0.030, "negro", {"bevel": 0.003, "segs": 3}),
            ("d", "marcas", (405, 725, 455, 735), "acero", 0.030),
            ("s", "placa", (500, 700, 546, 806), 0.033, "goma", {}),
            ("s", "empunadura_del", (186, 755, 234, 832), 0.022, "negro", {"bevel": 0.003}),
            *serr("estria_del", 190, 230, 765, 825, 6, "oscuro", 0.022),
            ("s", "guardamonte", (238, 752, 300, 792), 0.012, "negro",
             {"hole": [(250, 760), (288, 760), (288, 786), (252, 786)]}),
            ("s", "empunadura", [(272, 755), (318, 755), (352, 840), (312, 852), (285, 800)], 0.024, "negro",
             {"bevel": 0.003}),
            *serr("estria", 292, 340, 790, 840, 5, "oscuro", 0.024),
        ]),
    # ---------------------------------------------------------------- fusiles
    "AT_MX4": dict(
        kind="rifle", front=605, back=1122, L=0.46, origin=(905, 758), bore=725, muzzle=(605, 725),
        optic=(840, 693), light=(675, 752),
        mag=([(795, 758), (848, 758), (842, 893), (788, 893)], 0.020, "fde", {"cut": False}),
        parts=[
            ("l", "freno", [(605, 12), (608, 18), (648, 18), (652, 13)], 725, "negro"),
            *serr("dientes", 609, 645, 712, 738, 4, "oscuro", 0.0362),
            ("s", "guardamanos", (650, 695, 802, 750), 0.030, "fde", {"bevel": 0.004, "segs": 3}),
            ("slots", "mlok", 660, 795, 712, 724, 4, "oscuro", 0.030),
            ("r", "riel", 652, 1010, 695),
            ("s", "receptor", (798, 692, 1012, 760), 0.026, "fde", {}),
            ("d", "expulsion", (905, 708, 960, 722), "fde_osc", 0.026),
            ("p", 935, 742, 4, 0.026), ("p", 980, 718, 4, 0.026),
            ("s", "afg", (712, 745, 797, 802), 0.018, "fde", {"bevel": 0.003, "segs": 3}),
            ("s", "guardamonte", (845, 755, 902, 792), 0.012, "fde", {}),
            ("s", "empunadura", [(888, 755), (935, 755), (962, 815), (958, 840), (928, 840), (890, 775)], 0.022,
             "fde", {"bevel": 0.003, "segs": 3}),
            ("s", "culata", (1008, 694, 1102, 772), 0.026, "fde", {"bevel": 0.003, "segs": 3}),
            ("s", "cantonera", (1096, 696, 1124, 778), 0.032, "goma", {}),
        ]),
    "AT_AUGA5": dict(
        kind="rifle", front=118, back=548, L=0.49, origin=(290, 995), bore=965, muzzle=(118, 965),
        optic=(260, 925), light=(145, 990),
        mag=([(363, 1000), (420, 1000), (420, 1092), (363, 1092)], 0.020, "gris_carg", {"cut": False}),
        parts=[
            ("l", "apagallamas", [(118, 10), (121, 14), (134, 14), (136, 11)], 965, "negro"),
            ("s", "frente", (125, 925, 348, 990), 0.030, "azul_osc", {"cut": False, "bevel": 0.004, "segs": 3}),
            ("r", "riel", 125, 372, 925),
            ("s", "cuerpo", (340, 940, 548, 1002), 0.034, "azul_osc", {"cut": False, "bevel": 0.005, "segs": 3}),
            ("d", "expulsion", (378, 952, 440, 962), "oscuro", 0.034),
            ("s", "culata_inf", [(418, 995), (548, 995), (548, 1064), (470, 1056), (418, 1012)], 0.034, "azul_osc",
             {"bevel": 0.005, "segs": 3}),
            ("s", "cantonera", (520, 945, 550, 1064), 0.036, "goma", {}),
            ("s", "guarda", [(170, 985), (345, 985), (345, 1000), (302, 1064), (215, 1066), (170, 1000)], 0.026,
             "azul_osc", {"bevel": 0.004, "segs": 3, "hole": [(218, 993), (286, 993), (286, 1050), (228, 1050)]}),
            ("s", "empunadura", [(272, 990), (336, 990), (330, 1064), (290, 1064)], 0.027, "azul_osc",
             {"bevel": 0.004, "segs": 3}),
        ]),
    "AT_AG203": dict(
        kind="rifle", front=590, back=1152, L=0.54, origin=(1018, 985), bore=950, muzzle=(590, 950),
        optic=(930, 930), light=(790, 985),
        mag=([(852, 988), (906, 988), (906, 1094), (855, 1098)], 0.021, "marron",
             {"cut": False, "base": [(848, 1092), (906, 1089), (906, 1107), (850, 1108)]}),
        parts=[
            ("l", "freno", [(590, 9), (593, 13), (604, 13), (606, 10)], 950, "negro"),
            ("s", "poste", (598, 922, 610, 962), 0.010, "negro", {"cut": False}),
            ("l", "tubo", [(604, 11), (608, 13), (742, 13), (746, 11)], 950, "oliva_osc"),
            *[("l", f"anillo{i}", [(630 + i * 28, 13), (632 + i * 28, 14), (642 + i * 28, 14), (644 + i * 28, 13)],
               950, "negro") for i in range(4)],
            ("s", "bloque_gas", (740, 932, 760, 966), 0.020, "negro", {"cut": False}),
            ("s", "guardamanos", (755, 935, 860, 985), 0.030, "negro", {"cut": False, "bevel": 0.004, "segs": 3}),
            ("slots", "mlok", 765, 850, 950, 962, 3, "oscuro", 0.030),
            ("s", "receptor", (855, 933, 1052, 1000), 0.026, "negro", {}),
            ("r", "riel", 760, 1030, 932),
            ("d", "expulsion", (905, 948, 960, 960), "acero", 0.026),
            ("s", "brocal", [(835, 985), (906, 985), (902, 1025), (856, 1030)], 0.024, "negro", {"cut": False}),
            ("s", "guardamonte", (940, 995, 1005, 1016), 0.012, "negro", {}),
            ("s", "cola", [(972, 996), (979, 996), (981, 1012), (975, 1013)], 0.005, "negro", {"cut": False}),
            ("s", "empunadura", [(1003, 985), (1042, 985), (1068, 1050), (1040, 1058), (1010, 1000)], 0.024,
             "negro", {"bevel": 0.003, "segs": 3}),
            ("s", "culata", (1050, 943, 1134, 1034), 0.016, "negro", {}),
            ("s", "cantonera", (1128, 946, 1153, 1034), 0.024, "goma", {}),
        ]),
    "AT_Komodo": dict(
        kind="rifle", front=55, back=560, L=0.52, origin=(403, 1245), bore=1201, muzzle=(55, 1201),
        optic=(330, 1176), light=(232, 1240),
        mag=([(283, 1248), (347, 1248), (338, 1350), (278, 1350)], 0.020, "negro",
             {"cut": False, "base": [(276, 1344), (340, 1344), (338, 1363), (276, 1363)], "base_mat": "plata"}),
        parts=[
            ("s", "supresor", (55, 1179, 197, 1223), 0.030, "negro", {"bevel": 0.005, "segs": 3}),
            *serr("ranura_sup", 75, 185, 1188, 1198, 6, "oscuro", 0.030),
            ("s", "guardamanos", (195, 1176, 312, 1240), 0.030, "plata", {"bevel": 0.004, "segs": 3}),
            *serr("ventila", 200, 305, 1210, 1226, 9, "oscuro", 0.030),
            ("r", "riel", 197, 470, 1178),
            ("s", "punto", (205, 1164, 235, 1178), 0.010, "negro", {"cut": False}),
            ("s", "superior", (305, 1178, 470, 1216), 0.026, "plata", {}),
            ("d", "expulsion", (360, 1195, 420, 1208), "oscuro", 0.026),
            ("s", "inferior", (298, 1212, 470, 1253), 0.024, "negro", {}),
            ("p", 380, 1232, 6, 0.024), ("p", 445, 1228, 5, 0.024),
            ("s", "culata", [(468, 1172), (495, 1172), (560, 1196), (560, 1222), (468, 1222)], 0.028, "plata",
             {"cut": False, "bevel": 0.004, "segs": 3}),
            ("s", "tubo_culata", (468, 1218, 560, 1246), 0.024, "negro", {}),
            ("s", "guardamonte", (350, 1245, 422, 1282), 0.012, "negro", {}),
            ("s", "empunadura", [(390, 1240), (432, 1240), (462, 1310), (452, 1338), (425, 1338), (395, 1270)],
             0.022, "negro", {"bevel": 0.003, "segs": 3}),
        ]),
    "AT_CycloneAGL": dict(
        kind="rifle", front=670, back=1158, L=0.50, origin=(968, 1248), bore=1228, muzzle=(672, 1228),
        optic=(850, 1185), light=(722, 1258),
        parts=[
            ("l", "tubo", [(670, 21), (672, 25), (682, 25), (684, 23), (800, 23)], 1228, "oliva_osc"),
            ("t", "anima", 669.5, 672, 17, 1228, "oscuro"),
            ("s", "base_riel", (680, 1185, 800, 1206), 0.024, "oliva", {"cut": False}),
            ("s", "riel_inf", (680, 1249, 800, 1260), 0.022, "oliva", {"cut": False}),
            ("r", "riel", 680, 990, 1185),
            ("l", "placa_tambor", [(796, 30), (796, 58), (820, 58), (820, 30)], 1257, "oliva"),
            ("l", "tambor", [(818, 50), (820, 53), (900, 53), (902, 50)], 1257, "oliva_osc"),
            *[("l", f"aro{i}", [(830 + i * 22, 53), (832 + i * 22, 55), (840 + i * 22, 55), (842 + i * 22, 53)],
               1257, "negro") for i in range(3)],
            ("s", "receptor", (898, 1180, 1002, 1250), 0.030, "oliva", {"cut": False, "bevel": 0.003}),
            ("p", 925, 1225, 5, 0.030), ("p", 965, 1212, 5, 0.030),
            ("s", "guardamonte", [(900, 1248), (955, 1248), (955, 1290), (905, 1290)], 0.012, "oliva",
             {"cut": False, "hole": [(910, 1255), (948, 1255), (948, 1282), (912, 1282)]}),
            ("s", "cola", [(926, 1252), (933, 1252), (935, 1272), (929, 1274)], 0.005, "negro", {"cut": False}),
            ("s", "empunadura", [(955, 1245), (995, 1240), (1035, 1320), (1018, 1334), (990, 1334), (960, 1278)],
             0.024, "oliva", {"bevel": 0.003, "segs": 3}),
            ("s", "culata", (1000, 1190, 1112, 1250), 0.026, "oliva", {"bevel": 0.003, "segs": 3}),
            ("slots", "ranura", 1025, 1105, 1225, 1232, 3, "oscuro", 0.026),
            ("s", "cantonera", [(1106, 1200), (1158, 1200), (1158, 1304), (1140, 1304), (1106, 1252)], 0.030,
             "oliva", {"bevel": 0.003, "segs": 3}),
        ]),
    "AT_RPK101": dict(
        kind="rifle", front=190, back=990, L=0.62, origin=(743, 1505), bore=1473, muzzle=(190, 1473),
        optic=(640, 1447), light=(420, 1527),
        parts=[
            ("l", "apagallamas", [(190, 8), (193, 11), (212, 11), (215, 8)], 1473, "negro"),
            ("t", "canon", 213, 292, 7, 1473, "negro"),
            ("t", "tubo_gases", 245, 420, 7, 1458, "negro"),
            ("s", "superior", (245, 1445, 700, 1488), 0.026, "negro", {"cut": False, "bevel": 0.003}),
            ("r", "riel", 360, 880, 1446),
            ("s", "guardamanos", [(285, 1485), (700, 1485), (700, 1525), (300, 1530), (285, 1515)], 0.032, "madera",
             {"cut": False, "bevel": 0.004, "segs": 3}),
            *serr("ranura", 360, 690, 1492, 1522, 22, "marron", 0.032),
            ("t", "bipode", 283, 352, 17, 1508, "negro"),
            ("s", "receptor", (695, 1445, 935, 1505), 0.026, "negro", {}),
            ("d", "expulsion", (760, 1460, 840, 1472), "acero", 0.026),
            ("s", "aleta", [(546, 1450), (552, 1368), (562, 1372), (565, 1450)], 0.006, "madera", {"cut": False}),
            ("s", "carrillera", (840, 1440, 945, 1470), 0.028, "madera", {"cut": False, "bevel": 0.003}),
            ("s", "culata", [(900, 1448), (992, 1455), (992, 1566), (870, 1566), (868, 1515)], 0.030, "negro",
             {"bevel": 0.004, "segs": 3}),
            ("s", "empunadura_del", (548, 1523, 594, 1606), 0.022, "negro", {"bevel": 0.003}),
            ("s", "guardamonte", (688, 1500, 742, 1522), 0.012, "negro", {}),
            ("s", "empunadura", [(728, 1505), (772, 1505), (800, 1585), (780, 1594), (758, 1594), (735, 1530)],
             0.024, "negro", {"bevel": 0.003, "segs": 3}),
        ]),
    "AT_PSR": dict(
        kind="rifle", front=165, back=995, L=0.62, origin=(782, 1730), bore=1694, muzzle=(165, 1694),
        light=(520, 1722), sil=False,
        mag=([(628, 1728), (690, 1728), (684, 1803), (628, 1806)], 0.021, "marron", {}),
        parts=[
            ("l", "supresor", [(165, 12), (166, 19), (175, 19), (178, 17), (455, 17), (460, 14)], 1694, "pavon"),
            *[("l", f"aro{i}", [(200 + i * 60, 17), (202 + i * 60, 18), (208 + i * 60, 18), (210 + i * 60, 17)],
               1694, "negro") for i in range(4)],
            ("s", "guardamanos", [(455, 1680), (615, 1680), (615, 1722), (470, 1722), (455, 1712)], 0.028, "negro",
             {"bevel": 0.003, "segs": 3}),
            ("s", "receptor", (610, 1678, 802, 1736), 0.026, "negro", {}),
            ("d", "expulsion", (700, 1690, 770, 1702), "acero", 0.026),
            ("l", "mira", [(598, 10), (600, 16), (618, 16), (626, 11), (790, 11), (800, 14), (830, 15),
                           (832, 11)], 1630, "negro"),
            ("s", "torreta", (650, 1610, 700, 1648), 0.022, "negro", {"bevel": 0.003}),
            ("s", "montura", (640, 1640, 700, 1680), 0.016, "negro", {}),
            ("t", "lente", 597, 599, 14, 1630, "vidrio"),
            ("t", "bipode", 340, 470, 4, 1740, "negro"),
            ("s", "base_bipode", (462, 1720, 492, 1742), 0.020, "negro", {}),
            ("s", "guardamonte", (715, 1712, 765, 1746), 0.012, "negro",
             {"hole": [(722, 1716), (758, 1716), (758, 1740), (726, 1740)]}),
            ("s", "cola", [(742, 1716), (749, 1716), (751, 1736), (745, 1738)], 0.005, "negro", {}),
            ("s", "empunadura", [(766, 1730), (806, 1730), (814, 1795), (782, 1802)], 0.024, "negro",
             {"bevel": 0.003, "segs": 3}),
            ("s", "culata", [(800, 1690), (992, 1690), (992, 1792), (865, 1794), (806, 1802)], 0.024, "negro",
             {"bevel": 0.003, "segs": 3, "hole": [(797, 1714), (875, 1714), (875, 1762), (808, 1762)],
              "hole2": [(888, 1715), (900, 1715), (934, 1761), (888, 1761)],
              "hole3": [(908, 1715), (927, 1715), (927, 1735)], "hole4": [(929, 1739), (951, 1739), (951, 1761)]}),
            ("s", "carrillera", (830, 1683, 890, 1700), 0.026, "madera", {"bevel": 0.003}),
            ("s", "cantonera", (966, 1690, 996, 1794), 0.030, "goma", {}),
        ]),
}

MAG_IDS = {  # cargador suelto -> arma (el modelo sale de la ficha del arma)
    "AT_GXPMag": "AT_GXP", "AT_MD34Mag": "AT_MD34", "AT_GravMag": "AT_GravRecon", "AT_VikorMag": "AT_VikorS1",
    "AT_FNPRMag": "AT_FNPR", "AT_SARMag": "AT_FNSAR", "AT_QDXMag": "AT_QDX99", "AT_MX4Mag": "AT_MX4",
    "AT_AUGMag": "AT_AUGA5", "AT_AG203Mag": "AT_AG203", "AT_KomodoMag": "AT_Komodo", "AT_RPKDrum": "AT_RPK101",
    "AT_PSRMag": "AT_PSR",
}


# ------------------------------------------------------------------ construcción
def photo(ID, sp, origin_px=None):
    rifle = sp["kind"] == "rifle" and ID not in ("AT_FNSAR", "AT_QDX99")
    scale = sp["L"] / abs(sp["back"] - sp["front"])
    return gk.Photo(ID, origin_px=origin_px or sp["origin"], origin=(0.006, -0.002) if rifle else (0.0, 0.0),
                    scale=scale, flip=sp["front"] < sp["back"], silhouette=sp.get("sil", True))


def build_parts(P, sp, ops):
    out = []
    by = sp["bore"]
    for op in ops:
        k = op[0]
        if k == "s":
            _, name, reg, th, m, o = op
            g = P.cut(reg) if o.get("cut", True) else P.poly(reg)
            for hk in ("hole", "hole2", "hole3", "hole4"):
                if hk in o:
                    g = g.difference(P.poly(o[hk]))
            out += gk.slab(name, g, th, mat(m), y=o.get("y", 0.0), bevel=o.get("bevel", 0.0015),
                           segs=o.get("segs", 2))
            if "panel" in o:
                out += gk.panel(f"{name}_tex", g.intersection(P.poly(o["panel"])), th, mat("goma"), inset=0.003)
        elif k == "t":
            _, name, x0, x1, r, y, m = op
            a, b = sorted((P.X(x0, by), P.X(x1, by)))
            out.append(gk.tube(name, a, b, P.L(r), mat(m), z=P.pt(x0, y)[1], segs=20))
        elif k == "l":
            _, name, prof, y, m = op
            pts = sorted(((P.X(x, by), P.L(r)) for x, r in prof), key=lambda q: q[0])
            pts = [(pts[0][0], 0.0)] + pts + [(pts[-1][0], 0.0)]
            out.append(gk.lathe_x(name, pts, mat(m), z=P.pt(prof[0][0], y)[1], segs=22))
        elif k == "r":
            _, name, x0, x1, y = op
            a, b = sorted((P.X(x0, by), P.X(x1, by)))
            out += gk.rail(name, a, b, P.pt(x0, y)[1], mat("negro"))
        elif k == "d":
            _, name, reg, m, th = op
            out += gk.decal(name, P.poly(reg), th / 2 + 0.0003, mat(m))
        elif k == "slots":
            _, name, x0, x1, y0, y1, n, m, th = op
            w = (x1 - x0) / n
            for i in range(n):
                out += gk.decal(f"{name}{i}", P.poly((x0 + i * w + w * 0.12, y0, x0 + i * w + w * 0.88, y1)),
                                th / 2 + 0.0003, mat(m))
        elif k == "p":
            _, x, y, r, th = op
            out.append(gk.pin(f"perno{len(out)}", *P.pt(x, y), P.L(r), mat("negro"), th / 2 + 0.0004))
    return out


def mag_parts(P, sp):
    reg, th, m, o = sp["mag"]
    g = P.cut(reg) if o.get("cut", True) else P.poly(reg)
    out = gk.slab("cargador", g, th, mat(m), bevel=0.0015, segs=2)
    ring = g.buffer(-0.0025, join_style=2).difference(g.buffer(-0.0037, join_style=2))
    out += gk.decal("nervio", ring, th / 2 + 0.0003, mat("oscuro"), depth=0.0006)
    if "base" in o:
        out += gk.slab("base_cargador", P.poly(o["base"]), th + 0.003, mat(o.get("base_mat", "oscuro")),
                       bevel=0.002, segs=3)
    return out


def build_gun(ID, preview=False):
    pz.reset()
    _MATS.clear()
    sp = SPEC[ID]
    P = photo(ID, sp)
    parts = build_parts(P, sp, sp["parts"])
    if "mag" in sp:
        parts += mag_parts(P, sp)
    obj = gk.finish_gun(ID, parts, tex_size=512 if sp["kind"] == "handgun" and sp["L"] < 0.25 else 1024)
    if preview:
        gk.preview(obj, pz.ART / ID / "preview.png")
    by = sp["bore"]
    att = {"muzzle": (P.X(sp["muzzle"][0], by), 0, P.pt(*sp["muzzle"])[1])}
    if "optic" in sp:
        att["at_optic"] = (P.X(sp["optic"][0], by), 0, P.pt(*sp["optic"])[1] + 0.006)
    if "light" in sp:
        att["at_light"] = (P.X(sp["light"][0], by), 0, P.pt(*sp["light"])[1] - 0.001)
    gk.export(obj, ID, sp["kind"], att)


def pistol_mag(length, base):
    """Cargador de pistola (cuerpo de polímero, base y testigos), origen arriba al centro."""
    from shapely.geometry import Polygon
    t = math.tan(math.radians(16))
    body = Polygon([(-0.014, 0.0), (0.012, 0.0), (0.012 - length * t, -length), (-0.014 - length * t, -length)])
    b = length + 0.008
    return (gk.slab("cuerpo", body, 0.018, mat("polimero"), bevel=0.0015) +
            gk.slab("base", Polygon([(-0.016 - length * t, -length + 0.002), (0.014 - length * t, -length + 0.002),
                                     (0.013 - b * t, -b), (-0.017 - b * t, -b)]), 0.021, mat(base), bevel=0.002,
                    segs=3) +
            gk.decal("labio", Polygon([(-0.012, -0.001), (0.010, -0.001), (0.009, -0.004), (-0.011, -0.004)]),
                     0.0091, mat("laton")) +
            [gk.pin(f"testigo{i}", -0.004 - (0.012 + i * 0.015) * t, -0.012 - i * 0.015, 0.0012, mat("oscuro"),
                    0.0091, segs=8) for i in range(int(length / 0.017))])


def drum():
    """Tambor de 75 para la RPK: disco con tapa y cuello de alimentación."""
    m, k = mat("negro"), mat("oscuro")
    disc = pz.cylinder("tambor", 0.042, 0.030, loc=(0.0, 0.0, -0.050), rot=(90, 0, 0), mat=m, segs=28)
    cap = pz.cylinder("tapa", 0.016, 0.034, loc=(0.0, 0.0, -0.050), rot=(90, 0, 0), mat=k, segs=20)
    neck = gk.bx("cuello", -0.016, 0.016, -0.010, 0.010, -0.012, 0.0, m, bevel=0.0015)
    return [disc, cap, neck] + rings_y(0.042, -0.050, m)


def rings_y(r, z, m):
    return [pz.cylinder(f"aro{i}", r + 0.0012, 0.003, loc=(0.0, s * 0.012, z), rot=(90, 0, 0), mat=m, segs=28)
            for i, s in enumerate((-1, 1))]


def build_mag(MID):
    pz.reset()
    _MATS.clear()
    gid = MAG_IDS[MID]
    sp = SPEC[gid]
    if "pmag" in sp:
        parts = pistol_mag(*sp["pmag"])
    elif MID == "AT_RPKDrum":
        parts = drum()
    else:
        reg = sp["mag"][0]
        xs, ys = [p[0] for p in reg], [p[1] for p in reg]
        P = photo(gid, sp, origin_px=((min(xs) + max(xs)) / 2, min(ys)))
        parts = mag_parts(P, sp)
    obj = gk.finish_gun(MID, parts, tex_size=512)
    gk.export(obj, MID, "rifle", {})


if __name__ == "__main__":
    ids = [a for a in sys.argv[1:] if not a.startswith("--")] or list(SPEC) + list(MAG_IDS)
    for i in ids:
        if i in SPEC:
            build_gun(i, "--preview" in sys.argv)
        else:
            build_mag(i)
