"""AT_M4 (versión hard-surface): M4 corta de la foto de referencia (cañón ~11,5", RIS II de 9,55", culata
SOPMOD, empuñadura angulada, cargador STANAG gris).

Medidas: referencias/AT_M4/medidas.md. Escala de la foto 0,802 mm/px, medida con el paso del riel
Picatinny (10,01 mm). Perfil de costado = silueta calcada (guns/siluetas/AT_M4.json); anchos = medidas
publicadas de piezas reales. Se modela en metros reales y se exporta con el factor K de las armas del mod.
Uso: python3 tools/blender/guns/AT_M4.py [--check]   (--check: solo geometría + verificación de silueta)
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import pzlib as pz  # noqa: E402
import hardsurf as hs  # noqa: E402
from shapely.geometry import Polygon  # noqa: E402

ID = "AT_M4"
MM_PX = 0.802                                   # paso Picatinny 10,01 mm = 12,48 px en la foto
REF = hs.Ref(MM_PX, origin_px=(468, 963), bore_px=((380, 889), (1060, 905)))
SIL = HERE / "siluetas" / f"{ID}.json"
# exportación: mismo tamaño y origen que la M4 que ya se probó en el juego (mano izquierda ~0,20)
K = 0.628
OFFSET = (0.006, -0.002)
# zonas de la foto que no son el arma (mira ACOG, linterna y su cable): no cuentan para el IoU
EXCLUDE = [[(452, 770), (690, 770), (690, 850), (452, 850)],
           [(812, 820), (1110, 820), (1110, 889), (1004, 889), (998, 880), (812, 880)],
           [(812, 860), (885, 860), (885, 968), (812, 968)]]
TRIGGER_HOLE = [(513, 962), (579, 962), (586, 972), (584, 992), (520, 994), (511, 983)]

# anchos reales (m): publicados (fuentes en referencias/AT_M4/medidas.md) o, si dice "est.", estimados
W_UPPER = 0.0254       # cajón superior (est. 1,0")
W_LOWER = 0.0236       # cajón inferior, cuerpo (est.)
W_MAGWELL = 0.0290     # brocal (est.; ancho total publicado del inferior 37-38 mm con controles)
W_GRIP = 0.028         # empuñadura (est.)
W_GUARD = 0.013        # guardamonte
W_MAG = 0.0229         # cargador STANAG (est. 0,9")
W_STOCK = 0.061        # SOPMOD (publicado 2,4")
W_STOCK_LOW = 0.026    # patas inferiores de la SOPMOD (est.)
W_AFG = 0.0348         # empuñadura angulada (AFG2 publicado 1,37")
R_BUFFER = 0.0292 / 2  # tubo buffer mil-spec 1,148"


def R(region, minus=()):
    g = SIL_M.intersection(REF.poly(region))
    for m in minus:
        g = g.difference(REF.poly(m))
    return g


def Z(y, x=700):
    return REF.Z(x, y)


def X(x, y=897):
    return REF.X(x, y)


def sec_chamfer(w, z0, z1, ct, cb):
    """Sección YZ rectangular de ancho w entre z0 y z1, con chaflán ct arriba y cb abajo."""
    h = w / 2
    return Polygon([(-h + cb, z0), (h - cb, z0), (h, z0 + cb), (h, z1 - ct), (h - ct, z1), (-h + ct, z1),
                    (-h, z1 - ct), (-h, z0 + cb)])


def mats():
    return {
        "anod": pz.mat("aluminio_anodizado", (0.052, 0.054, 0.058), dirt=0.05, rough=0.5, scale=60),
        "acero": pz.mat("acero_fosfatado", (0.075, 0.074, 0.072), dirt=0.06, rough=0.6, scale=60),
        "pol": pz.mat("polimero", (0.06, 0.061, 0.064), dirt=0.05, rough=0.85, scale=80),
        "goma": pz.mat("goma", (0.035, 0.035, 0.037), dirt=0.04, rough=0.95, scale=80),
        "cubierta": pz.mat("cubierta_expulsion", (0.30, 0.31, 0.32), dirt=0.05, rough=0.4, scale=60),
        "carg": pz.mat("cargador_gris", (0.30, 0.32, 0.33), dirt=0.06, rough=0.55, scale=60),
        "ris": pz.mat("ris", (0.06, 0.058, 0.055), dirt=0.05, rough=0.55, scale=60),
    }


def build_geometry():
    global SIL_M
    pz.reset()
    SIL_M = hs.silhouette(SIL, REF, soften_px=1.0).difference(REF.poly(TRIGGER_HOLE))
    M = mats()
    P = []
    zb = REF.Z(380, 889)                       # eje del cañón (= eje del tubo buffer)

    # --- cajón superior: cuerpo con chaflanes, baja en la zona de la ventana de expulsión
    up_side = R([(444, 857), (667, 857), (667, 933), (590, 933), (588, 904.5), (444, 904.5)])
    up = hs.two_view("superior", up_side, sec_chamfer(W_UPPER, Z(934) - 0.002, Z(857), 0.0035, 0.001), M["anod"])
    # ventana de expulsión (lado derecho, -Y): rebaje + tapa de acero
    win = hs.box("ventana_cut", X(592), X(663), -W_UPPER, -W_UPPER / 2 + 0.0014, Z(931), Z(906), None)
    up = hs.boolean(up, win)
    P.append(up)
    P.append(hs.box("tapa_expulsion", X(594), X(661), -W_UPPER / 2 + 0.0008, -W_UPPER / 2 + 0.0016, Z(929),
                    Z(908), M["cubierta"]))
    P.append(hs.box("nervio_tapa", X(600), X(655), -W_UPPER / 2 + 0.0002, -W_UPPER / 2 + 0.0009, Z(920),
                    Z(916), M["cubierta"]))
    # asistente de cierre: alojamiento cónico al costado derecho + botón
    fa_len = X(528) - X(456)
    fa = pz.cylinder("asistente", 0.0075, fa_len, loc=((X(456) + X(528)) / 2, -W_UPPER / 2 - 0.0035, Z(892)),
                     rot=(0, 90, 0), mat=M["anod"], segs=14, r2=0.0055)
    P.append(fa)
    P.append(pz.cylinder("boton_asistente", 0.0068, 0.008, loc=(X(456) - 0.003, -W_UPPER / 2 - 0.0035, Z(892)),
                         rot=(0, 90, 0), mat=M["acero"], segs=14))
    # deflector de vainas
    defl = Polygon([(X(536), Z(896)), (X(552), Z(896)), (X(552), Z(868)), (X(540), Z(866))])
    defl_o = hs.prism("deflector", defl, -W_UPPER / 2 - 0.004, -W_UPPER / 2 + 0.002, M["anod"], "XZ")
    P.append(defl_o)
    # palanca de carga (atrás, arriba)
    P.append(hs.box("palanca_carga", X(445) - 0.004, X(460), -0.010, 0.010, Z(866), Z(857), M["anod"]))
    P.append(hs.box("traba_palanca", X(447), X(455), 0.009, 0.016, Z(866), Z(859), M["anod"]))
    # riel superior
    rail = hs.picatinny("riel_sup", X(450), X(664), M["anod"], h=Z(849) - Z(857))
    hs.place(rail, 0, (0, 0, Z(857)))
    P += rail

    # --- cajón inferior: cuerpo + brocal ensanchado (sección más ancha abajo)
    lo_side = R([(428, 905.5), (591, 905.5), (591, 934.5), (666, 934.5), (666, 982), (596, 995), (590, 960),
                 (505, 960), (500, 957), (428, 957)])
    body_side = lo_side.intersection(REF.poly((420, 900, 592, 965)))
    well_side = lo_side.intersection(REF.poly((588, 930, 670, 1000)))
    P.append(hs.two_view("inferior", body_side, sec_chamfer(W_LOWER, Z(965) - 0.003, Z(905.5), 0.001, 0.002),
                         M["anod"]))
    flare = Polygon([(-W_MAGWELL / 2, Z(934.5)), (W_MAGWELL / 2, Z(934.5)), (W_MAGWELL / 2 + 0.0015, Z(975)),
                     (W_MAGWELL / 2 + 0.0015, Z(1000) - 0.004), (-W_MAGWELL / 2 - 0.0015, Z(1000) - 0.004),
                     (-W_MAGWELL / 2 - 0.0015, Z(975))])
    well = hs.two_view("brocal", well_side, flare, M["anod"])
    mag_hole = hs.box("brocal_hueco", X(600), X(660), -W_MAG / 2 - 0.0004, W_MAG / 2 + 0.0004, Z(1010), Z(975), None)
    P.append(hs.boolean(well, mag_hole))
    # guardamonte (aro)
    guard_side = R([(503, 955), (596, 955), (596, 1004), (503, 1004)])
    P.append(hs.two_view("guardamonte", guard_side, sec_chamfer(W_GUARD, Z(1006), Z(955), 0.001, 0.0015),
                         M["anod"]))
    trig = Polygon([(X(530), Z(962)), (X(538), Z(962)), (X(545), Z(976)), (X(542), Z(990)), (X(537), Z(990)),
                    (X(539), Z(977))])
    P.append(hs.prism("cola", trig, -0.0028, 0.0028, M["acero"], "XZ"))
    # pernos, selector, retén del cargador, retén del cierre
    for i, (x, y, r) in enumerate(((470, 923, 4.5), (530, 945, 3.2), (557, 935, 3.2), (655, 948, 4.0))):
        P.append(hs.cyl_y(f"perno{i}", X(x), Z(y), r * MM_PX / 1000, -W_LOWER / 2 - 0.0006, W_LOWER / 2 + 0.0006,
                          M["acero"]))
    P.append(hs.cyl_y("selector", X(500), Z(937), 0.0055, -W_LOWER / 2 - 0.0022, -W_LOWER / 2, M["anod"], 16))
    P.append(hs.box("palanca_selector", X(500) - 0.002, X(500) + 0.016, -W_LOWER / 2 - 0.003, -W_LOWER / 2 - 0.0015,
                    Z(937) - 0.0025, Z(937) + 0.0025, M["anod"]))
    P.append(hs.cyl_y("reten_cargador", X(575), Z(942), 0.0052, -W_MAGWELL / 2 - 0.0025, -W_LOWER / 2, M["acero"], 16))
    P.append(hs.box("reten_cierre", X(583), X(596), W_LOWER / 2 - 0.0005, W_LOWER / 2 + 0.0025, Z(930), Z(915),
                    M["anod"]))

    # --- empuñadura (bordes redondeados con bisel grande)
    grip_side = R([(428, 950), (510, 957), (506, 1000), (473, 1114), (404, 1114), (388, 1060)])
    grip = hs.two_view("empunadura", grip_side, sec_chamfer(W_GRIP, Z(1120), Z(950), 0.006, 0.006), M["pol"])
    P.append(grip)

    # --- tubo buffer, tuerca castillo y placa
    P.append(hs.lathe_x("tubo_buffer", [(X(330), 0.0), (X(330), R_BUFFER), (X(418), R_BUFFER), (X(418), 0.0)],
                        M["anod"], z=zb, segs=20))
    P.append(hs.lathe_x("tuerca", [(X(416), 0.0), (X(416), 0.0165), (X(419), 0.0175), (X(428), 0.0175),
                                    (X(430), 0.0165), (X(430), 0.0)], M["acero"], z=zb, segs=12))
    P.append(hs.lathe_x("placa", [(X(429), 0.0), (X(429), 0.0185), (X(433), 0.0185), (X(433), 0.0)], M["acero"],
                        z=zb, segs=20))

    # --- culata SOPMOD: cuerpo con tubos de batería arriba, patas abajo, cantonera
    st_top = R((98, 858, 338, 946))
    from shapely.geometry import Point
    zt = Z(886)                                 # eje de los tubos de batería (publicado: ancho total 61 mm)
    tubes = Polygon([(-0.018, Z(946) - 0.002), (0.018, Z(946) - 0.002), (0.018, zt), (-0.018, zt)])
    for sy in (-1, 1):
        tubes = tubes.union(Point(sy * 0.0175, zt).buffer(0.013, 8))
    tubes = tubes.union(Polygon([(-0.0175, zt), (0.0175, zt), (0.0175, Z(866) + 0.001), (-0.0175, Z(866) + 0.001)]))
    P.append(hs.two_view("culata", st_top, tubes, M["pol"]))
    st_low = R((98, 940, 338, 1040)).simplify(0.0013, preserve_topology=True)
    P.append(hs.two_view("culata_patas", st_low, sec_chamfer(W_STOCK_LOW, Z(1045), Z(938), 0.003, 0.003),
                         M["pol"]))
    pad = R((78, 858, 101, 1040))
    P.append(hs.two_view("cantonera", pad, sec_chamfer(0.044, Z(1045), Z(855), 0.004, 0.004), M["goma"]))

    # --- guardamanos RIS: cuerpo octogonal + 4 rieles
    ris_x0, ris_x1 = X(668), X(998)
    top, bot = Z(850), Z(937.5)
    h_rail = 0.0055
    body_h = (top - bot) - 2 * h_rail
    body = hs.rounded_rect(body_h, body_h, 0.008, n=1, cx=0.0, cy=(top + bot) / 2)
    P.append(hs.prism("ris", body, ris_x0, ris_x1, M["ris"], "YZ"))
    zc = (top + bot) / 2
    for i, (rot, loc) in enumerate(((0, (0, 0, zc + body_h / 2)), (180, (0, 0, zc - body_h / 2)),
                                   (90, (0, -body_h / 2, zc)), (-90, (0, body_h / 2, zc)))):
        r = hs.picatinny(f"riel_ris{i}", ris_x0 + 0.004, ris_x1 - 0.002, M["ris"], h=h_rail)
        hs.place(r, rot, loc)
        P += r
    # tapa trasera del guardamanos
    P.append(hs.prism("ris_tapa", hs.rounded_rect(body_h + 0.002, body_h + 0.002, 0.009, n=1, cy=zc),
                      ris_x0 - 0.004, ris_x0 + 0.002, M["ris"], "YZ"))

    # --- cañón y apagallamas (ranuras con booleano)
    P.append(hs.lathe_x("canon", [(X(992), 0.0), (X(992), 0.0072), (X(1012), 0.0072), (X(1012), 0.0)], M["acero"],
                        z=zb, segs=16))
    fh = hs.lathe_x("apagallamas", [(X(1010), 0.0), (X(1010), 0.0076), (X(1014), 0.0084), (X(1084), 0.0084),
                                    (X(1090), 0.0074), (X(1090), 0.0042), (X(1086), 0.0042), (X(1086), 0.0)],
                    M["acero"], z=zb, segs=16)
    for i, a in enumerate((90, 22.5, 157.5)):       # ranuras arriba y a los costados; cerrado abajo como el A2
        s = hs.box(f"ranura{i}", X(1050), X(1080), -0.0012, 0.0012, 0.004, 0.012, None)
        s.data.transform(__import__("mathutils").Matrix.Rotation(math.radians(a - 90), 4, "X"))
        s.data.transform(__import__("mathutils").Matrix.Translation((0, 0, zb)))
        fh = hs.boolean(fh, s)
    P.append(fh)

    # --- empuñadura angulada
    afg_side = R((786, 937, 892, 1004))
    P.append(hs.two_view("afg", afg_side, sec_chamfer(W_AFG, Z(1006), Z(937), 0.004, 0.006), M["pol"]))

    # --- cargador STANAG (gris) y base
    mag_side = R([(588, 997), (668, 983), (725, 990), (725, 1140), (575, 1140)]).simplify(0.001)
    mag_body = mag_side.intersection(REF.poly([(560, 970), (740, 970), (740, 1112), (560, 1112)]))
    mag_base = mag_side.difference(REF.poly([(560, 970), (740, 970), (740, 1112), (560, 1112)]))
    P.append(hs.two_view("cargador", mag_body, sec_chamfer(W_MAG, Z(1140), Z(970), 0.0015, 0.0015), M["carg"]))
    P.append(hs.two_view("base_cargador", mag_base, sec_chamfer(W_MAG + 0.003, Z(1140), Z(1100), 0.002, 0.002),
                         M["pol"]))
    return P, M


BEVEL = {  # (ancho de bisel en m reales, segmentos); el resto 0,6 mm y 1 segmento
    "empunadura": (0.0105, 4), "culata": (0.006, 3), "culata_patas": (0.004, 2), "cantonera": (0.006, 3),
    "afg": (0.0095, 4), "cargador": (0.0012, 1), "base_cargador": (0.0018, 1), "guardamonte": (0.0012, 1),
    "superior": (0.0007, 1), "inferior": (0.0007, 1), "brocal": (0.0007, 1), "apagallamas": (0.0, 1),
    "tapa_expulsion": (0.0, 1), "nervio_tapa": (0.0, 1),
}


def finish_geometry(P):
    for o in P:
        if o.type != "MESH" or not o.data.polygons:
            continue
        base = o.name.split(".")[0]
        if base.startswith(("riel", "perno")):
            hs.harden(o, width=0.0)
            continue
        w, s = BEVEL.get(base, (0.0006, 1))
        hs.harden(o, width=w, segs=s)
    return P


FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def decals(M):
    """Agujeros del RIS (fila sobre el riel lateral, como la foto) y marcas grabadas del cajón inferior."""
    from PIL import Image, ImageDraw, ImageFont
    out = pz.ART / ID
    out.mkdir(parents=True, exist_ok=True)
    # RIS: imagen que cubre el costado de x=668..998 px, y=850..937,5 px (4 px de imagen por px de foto)
    s = 4
    W, H = int((998 - 668) * s), int((937.5 - 850) * s)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(13):
        cx, cy = (712 + i * 22 - 668) * s, (880 - 850) * s
        rx, ry = 6.2 * s, 5.0 * s
        d.ellipse((cx - rx - 3, cy - ry - 3, cx + rx + 3, cy + ry + 3), fill=(70, 70, 66, 255))   # canto gastado
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(4, 4, 4, 255))
    ris_png = out / "decal_ris.png"
    im.save(ris_png)
    for side in (1, -1):
        hs.add_decal(M["ris"], ris_png, X(668), X(998), Z(937.5), Z(850), side)
    # marcas (lado izquierdo, +Y): selector y datos en el brocal. Se dibuja al revés porque el lado
    # izquierdo se ve espejado respecto de la foto (que muestra el lado derecho).
    x0p, x1p, y0p, y1p = 440, 668, 903, 1000
    W, H = int((x1p - x0p) * s), int((y1p - y0p) * s)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f_small = ImageFont.truetype(FONT, int(3.2 * s))
    f_mid = ImageFont.truetype(FONT, int(4.0 * s))
    ink = (172, 172, 166, 255)
    d.text(((500 - x0p) * s, (922 - y0p) * s), "SAFE", font=f_small, fill=ink, anchor="mm")
    d.text(((520 - x0p) * s, (937 - y0p) * s), "SEMI", font=f_small, fill=ink, anchor="lm")
    d.text(((500 - x0p) * s, (952 - y0p) * s), "AUTO", font=f_small, fill=ink, anchor="mm")
    d.text(((630 - x0p) * s, (945 - y0p) * s), "M4 CARBINE", font=f_mid, fill=ink, anchor="mm")
    d.text(((630 - x0p) * s, (953 - y0p) * s), "CAL 5.56 MM", font=f_small, fill=ink, anchor="mm")
    d.text(((630 - x0p) * s, (961 - y0p) * s), "AT 0419", font=f_small, fill=ink, anchor="mm")
    im = im.transpose(Image.FLIP_LEFT_RIGHT)
    mk = out / "decal_marcas.png"
    im.save(mk)
    # el lado izquierdo espejado: x de la imagen invertida -> se proyecta de x1 a x0
    hs.add_decal(M["anod"], mk, X(x1p), X(x0p), Z(y1p), Z(y0p), 1)
    # cargador: tres nervaduras (medidas en la foto) en las dos caras
    x0p, x1p, y0p, y1p = 575, 735, 970, 1140
    W, H = int((x1p - x0p) * s), int((y1p - y0p) * s)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for (xa, ya), (xb, yb) in (((597, 1000), (613, 1126)), ((616, 997), (641, 1121)), ((637, 992), (662, 1116))):
        P0, P1 = ((xa - x0p) * s, (ya - y0p) * s), ((xb - x0p) * s, (yb - y0p) * s)
        d.line([P0, P1], fill=(20, 21, 22, 255), width=int(1.6 * s))
        d.line([(P0[0] + 2.2 * s, P0[1]), (P1[0] + 2.2 * s, P1[1])], fill=(205, 208, 210, 200), width=int(1.0 * s))
    mg = out / "decal_cargador.png"
    im.save(mg)
    for side in (1, -1):
        hs.add_decal(M["carg"], mg, X(x0p), X(x1p), Z(y1p), Z(y0p), side)
    # empuñadura: panel con punteado antideslizante (zona medida en la foto)
    x0p, x1p, y0p, y1p = 395, 515, 950, 1090
    W, H = int((x1p - x0p) * s), int((y1p - y0p) * s)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    panel = [(450, 982), (479, 991), (467, 1058), (441, 1067), (411, 1058), (436, 996)]
    pp = [((x - x0p) * s, (y - y0p) * s) for x, y in panel]
    d.polygon(pp, fill=(28, 28, 30, 255))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(pp, fill=255)
    dots = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dots)
    for yy in range(0, H, 6):
        for xx in range((yy // 6) % 2 * 3, W, 6):
            dd.ellipse((xx, yy, xx + 2, yy + 2), fill=(95, 96, 100, 255))
    im.paste(dots, (0, 0), Image.composite(dots, Image.new("RGBA", (W, H)), mask).split()[3])
    gp = out / "decal_empunadura.png"
    im.save(gp)
    for side in (1, -1):
        hs.add_decal(M["pol"], gp, X(x0p), X(x1p), Z(y1p), Z(y0p), side)


TEX = 512          # provisorio: igualar al tamaño de las texturas vanilla cuando llegue la medición


def build(check_only=False):
    P, M = build_geometry()
    P = finish_geometry(P)
    print("[AT_M4] piezas", len(P), "triangulos", hs.tri_count(P))
    iou = hs.silhouette_iou(P, REF, SIL, EXCLUDE, [TRIGGER_HOLE])
    print("[AT_M4] IoU silueta %.3f" % iou[0])
    if check_only:
        return P
    decals(M)
    obj = hs.join(P, ID)
    hs.unwrap(obj)
    hs.bake_textures(obj, TEX, pz.ART / ID / f"{ID}.png")
    return obj


# ------------------------------------------------------------------ exportación y verificación
def attachments():
    zb = REF.Z(380, 889)
    return {"muzzle": (X(1090), 0.0, zb),                    # boca del apagallamas
            "at_optic": (X(560), 0.0, Z(849)),               # sobre el riel del cajón
            "at_light": (X(962), 0.0, Z(937.5))}             # bajo el riel inferior, delante de la empuñadura


def to_game(o):
    """Escala real -> tamaño del mod (K) y origen de la empuñadura como la M4 probada en el juego."""
    from mathutils import Matrix
    M = Matrix.Translation((OFFSET[0], 0.0, OFFSET[1])) @ Matrix.Scale(K, 4)
    o.data.transform(M)
    return {k: tuple(M @ __import__("mathutils").Vector(v)) for k, v in attachments().items()}


def export(o):
    import gunkit as gk
    att = to_game(o)
    gk.export(o, ID, "rifle", att)
    return att


def check_fbx_normals(path):
    """Reimporta el FBX y cuenta normales de esquina invertidas respecto de su cara (debe ser ~0)."""
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path))
    o = next(ob for ob in bpy.context.scene.objects if ob.type == "MESH")
    me = o.data
    cn = me.corner_normals
    bad = tot = 0
    for p in me.polygons:
        for li in p.loop_indices:
            tot += 1
            if cn[li].vector.dot(p.normal) < 0.2:
                bad += 1
    return bad, tot, sum(len(p.vertices) - 2 for p in me.polygons)


def verify(o, out):
    """Láminas de verificación: IoU, volumen, escala de juego y manos."""
    import bpy
    from PIL import Image, ImageDraw
    from mathutils import Vector
    S = Path(out)
    S.mkdir(parents=True, exist_ok=True)
    photo = sys.argv[sys.argv.index("--foto") + 1] if "--foto" in sys.argv else None
    iou = hs.silhouette_iou([o], REF, SIL, EXCLUDE, [TRIGGER_HOLE], photo=photo,
                            out=str(S / "verif_silueta.png") if photo else None)
    lo = Vector([min(v.co[i] for v in o.data.vertices) for i in range(3)])
    hi = Vector([max(v.co[i] for v in o.data.vertices) for i in range(3)])
    c = (lo + hi) / 2
    L = hi.x - lo.x
    # volumen: costado, frente, arriba y 3/4
    views = [("der", (0, -1, 0), L * 1.04, (1600, 640)), ("frente", (1, 0, 0), (hi.z - lo.z) * 1.15, (640, 640)),
             ("arriba", (0, 0, 1), L * 1.04, (1600, 320)), ("34", (0.7, -1.0, 0.6), L * 0.95, (1600, 760))]
    tiles = {}
    for name, d, span, size in views:
        p = S / f"_v_{name}.png"
        if name == "arriba":
            hs.closeup([o], p, tuple(c), dist=1.0, direction=(0.0, -0.0001, 1.0), size=size, ortho=span, light=0.55)
        else:
            hs.closeup([o], p, tuple(c), dist=1.0, direction=d, size=size, ortho=span, light=0.55)
        tiles[name] = Image.open(p).convert("RGB")
        p.unlink()
    sheet = Image.new("RGB", (2240, 1720), (46, 47, 50))
    sheet.paste(tiles["der"], (0, 0))
    sheet.paste(tiles["frente"], (1600, 0))
    sheet.paste(tiles["arriba"], (0, 640))
    sheet.paste(tiles["34"], (0, 960))
    dr = ImageDraw.Draw(sheet)
    for txt, xy in (("costado", (10, 8)), ("frente", (1610, 8)), ("arriba", (10, 648)), ("3/4", (10, 968))):
        dr.text(xy, txt, fill=(255, 220, 120))
    sheet.save(S / "verif_volumen.png")
    # escala de juego: en una captura del usuario el personaje mide ~125 px -> la M4 (0,50 m de juego) ~36 px;
    # con el zoom al máximo ~90 px. Render 3/4 sobre gris asfalto, reducido a esos tamaños.
    p = S / "_g.png"
    hs.closeup([o], p, tuple(c), dist=1.0, direction=(0.55, -1.0, 0.9), size=(1200, 600), ortho=L * 1.05, light=0.8)
    big = Image.open(p).convert("RGB")
    p.unlink()
    game = Image.new("RGB", (900, 260), (70, 72, 74))
    x = 10
    for wpx in (36, 60, 90):
        sm = big.resize((int(wpx * 1.05), int(wpx * 1.05 / 2)), Image.LANCZOS)
        up = sm.resize((sm.width * 3, sm.height * 3), Image.NEAREST)
        game.paste(up, (x, 40))
        ImageDraw.Draw(game).text((x, 10), f"{wpx} px (x3)", fill=(255, 220, 120))
        x += up.width + 20
    game.save(S / "verif_escala_juego.png")
    # manos: muñeca izquierda medida en las animaciones vanilla de fusil (respecto de Prop1, cm de juego),
    # pasada a metros reales del modelo; la mano derecha toma la empuñadura en el origen.
    marks = []
    for (gx, gy, gz), col in (((5.9, 20.1, 1.4), (0.1, 0.9, 0.2)), ((3.1, 17.2, -2.0), (0.9, 0.8, 0.1))):
        pos = ((gy / 100 - OFFSET[0]) / K, -(gx / 100) / K, (gz / 100 - OFFSET[1]) / K)
        marks.append((pos, col))
    marks.append((((0 - OFFSET[0]) / K, 0.0, (0 - OFFSET[1]) / K), (0.9, 0.2, 0.2)))
    objs = []
    for i, (pos, col) in enumerate(marks):
        sph = pz.sphere(f"mano{i}", 0.022, loc=pos, mat=pz.mat(f"mano{i}", col, dirt=0.0), segs=16, rings=10)
        objs.append(sph)
    p = S / "_m.png"
    hs.closeup([o] + objs, p, tuple(c), dist=1.0, direction=(0.0, -1.0, 0.0), size=(1600, 640), ortho=L * 1.04,
               light=0.55)
    hand = Image.open(p).convert("RGB")
    p.unlink()
    p = S / "_m2.png"
    hs.closeup([o] + objs, p, tuple(c), dist=1.0, direction=(0.6, -0.6, 0.9), size=(1600, 760), ortho=L * 0.95,
               light=0.55)
    hand2 = Image.open(p).convert("RGB")
    p.unlink()
    for ob in objs:
        bpy.data.objects.remove(ob, do_unlink=True)
    hs_ = Image.new("RGB", (1600, 1400), (46, 47, 50))
    hs_.paste(hand, (0, 0))
    hs_.paste(hand2, (0, 640))
    hs_.save(S / "verif_manos.png")
    return iou


if __name__ == "__main__":
    obj = build("--check" in sys.argv)
    if "--check" not in sys.argv:
        out = pz.ART / ID
        iou = verify(obj, out)
        print("[AT_M4] verificación: IoU %.3f (inter %d, solo foto %d, solo modelo %d)" % iou)
        att = export(obj)
        print("[AT_M4] attachments (juego):", {k: tuple(round(c, 4) for c in v) for k, v in att.items()})
        import gunkit as gk
        bad, tot, tris = check_fbx_normals(gk.MODELS / f"{ID}.fbx")
        print(f"[AT_M4] FBX: {tris} triangulos, normales invertidas {bad}/{tot}")
