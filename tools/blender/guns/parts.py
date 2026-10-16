"""Partes de Arsenal Táctico: miras, linterna y cargadores (los de la foto).
Origen en la base de montaje; X hacia adelante, Z hacia arriba (la linterna cuelga hacia -Z).
Uso: python3 tools/blender/guns/parts.py [ID ...]   (sin argumentos: todas)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import gunkit as gk  # noqa: E402


def mount(m, x0=-0.018, x1=0.030):
    return [gk.bx("montura", x0, x1, -0.0105, 0.0105, 0.0, 0.010, m)]


def AT_ACOG():
    m, k = gk.black_metal(), gk.accent("oscuro", (0.02, 0.02, 0.022))
    return mount(m) + [
        gk.bx("cuerpo", -0.030, 0.034, -0.0145, 0.0145, 0.010, 0.040, m, bevel=0.005),
        gk.tube("objetivo", 0.030, 0.050, 0.0150, m, z=0.026, r2=0.0175),
        gk.tube("ocular", -0.048, -0.028, 0.0140, gk.rubber(), z=0.026),
        gk.bx("fibra", -0.016, 0.026, -0.005, 0.005, 0.040, 0.046, gk.accent("fibra", (0.6, 0.12, 0.05))),
        gk.bx("minipunto", -0.010, 0.012, -0.007, 0.007, 0.046, 0.058, k),
        gk.tube("lente", 0.049, 0.051, 0.0160, gk.glass(), z=0.026),
    ]


def AT_LPVO():
    m, t = gk.black_metal(), gk.fde()
    return mount(m, -0.030, 0.040) + [
        gk.tube("anillo1", -0.024, -0.012, 0.0145, m, z=0.030),
        gk.tube("anillo2", 0.024, 0.036, 0.0145, m, z=0.030),
        gk.bx("brazo1", -0.024, -0.012, -0.006, 0.006, 0.008, 0.020, m),
        gk.bx("brazo2", 0.024, 0.036, -0.006, 0.006, 0.008, 0.020, m),
        gk.tube("tubo", -0.050, 0.060, 0.0115, t, z=0.030),
        gk.tube("objetivo", 0.050, 0.086, 0.0130, t, z=0.030, r2=0.0170),
        gk.tube("ocular", -0.082, -0.048, 0.0155, t, z=0.030, r2=0.0125),
        gk.tube("aumento", -0.060, -0.052, 0.0160, m, z=0.030),
        pz.cylinder("torreta_sup", 0.008, 0.012, loc=(0.005, 0, 0.046), rot=(0, 0, 0), mat=t, segs=10),
        pz.cylinder("torreta_lat", 0.008, 0.012, loc=(0.005, -0.016, 0.030), rot=(90, 0, 0), mat=t, segs=10),
        gk.tube("lente", 0.085, 0.087, 0.0160, gk.glass(), z=0.030),
    ]


def AT_HoloSight():
    m = gk.black_metal()
    return mount(m, -0.016, 0.022) + [
        gk.bx("base_alta", -0.016, 0.022, -0.012, 0.012, 0.010, 0.018, m),
        gk.bx("pared_izq", -0.010, 0.016, 0.009, 0.0125, 0.018, 0.046, m, bevel=0.001),
        gk.bx("pared_der", -0.010, 0.016, -0.0125, -0.009, 0.018, 0.046, m, bevel=0.001),
        gk.bx("techo", -0.010, 0.016, -0.0125, 0.0125, 0.043, 0.048, m, bevel=0.001),
        gk.bx("vidrio", 0.002, 0.004, -0.009, 0.009, 0.018, 0.043, gk.glass(), bevel=0.0),
        gk.bx("perilla", -0.008, 0.006, 0.0125, 0.017, 0.020, 0.032, m),
    ]


def AT_Thermal():
    m, o = gk.black_metal(), gk.accent("naranja", (0.85, 0.30, 0.05))
    return mount(m) + [
        gk.bx("cuerpo", -0.050, 0.046, -0.0185, 0.0185, 0.010, 0.050, m, bevel=0.006),
        gk.tube("objetivo", 0.044, 0.070, 0.0170, m, z=0.030, r2=0.0190),
        gk.tube("aro", 0.042, 0.050, 0.0195, o, z=0.030),
        gk.tube("ocular", -0.082, -0.048, 0.0150, gk.rubber(), z=0.030, r2=0.0175),
        gk.tube("lente", 0.069, 0.071, 0.0170, gk.accent("germanio", (0.08, 0.07, 0.10)), z=0.030),
    ] + [pz.cylinder(f"boton{i}", 0.0045, 0.006, loc=(-0.024 + i * 0.014, 0.0, 0.052), rot=(0, 0, 0),
                     mat=gk.rubber(), segs=8) for i in range(3)]


def AT_TacLight():
    m = gk.black_metal()
    return [
        gk.bx("montura", -0.014, 0.016, -0.0095, 0.0095, -0.008, 0.0, m),
        gk.tube("cuerpo", -0.040, 0.030, 0.0085, m, z=-0.016),
        gk.tube("cabeza", 0.028, 0.050, 0.0110, m, z=-0.016, r2=0.0125),
        gk.tube("lente", 0.049, 0.051, 0.0115, gk.accent("lente", (0.85, 0.88, 0.9)), z=-0.016),
        gk.tube("tapa", -0.046, -0.038, 0.0075, gk.rubber(), z=-0.016),
    ]


def AT_LancerMag():
    smoke, b, k = gk.accent("translucido", (0.20, 0.17, 0.12)), gk.brass(), gk.accent("oscuro", (0.02, 0.02, 0.022))
    return [gk.mag_curve("cuerpo", -0.018, 0.018, 0.098, 0.010, smoke, rake=0.004),
            gk.mag_curve("vainas", -0.014, -0.002, 0.088, 0.010, b, thickness=0.0215, rake=0.004),
            gk.side("base", [(-0.016, -0.095), (0.034, -0.095), (0.036, -0.106), (-0.014, -0.108)], 0.024, k)]


def AT_SkullMag():
    g, k = gk.grey("gris_cargador"), gk.accent("oscuro", (0.02, 0.02, 0.022))
    return [gk.mag_curve("cuerpo", -0.018, 0.018, 0.098, 0.010, g, rake=0.004),
            gk.side("calavera", [(-0.016, -0.095), (0.036, -0.095), (0.038, -0.111), (-0.014, -0.113)], 0.026, k),
            gk.bx("ojo1", 0.004, 0.012, 0.0125, 0.0135, -0.106, -0.100, g, bevel=0.0),
            gk.bx("ojo2", 0.018, 0.026, 0.0125, 0.0135, -0.106, -0.100, g, bevel=0.0)]


def AT_AKMag():
    return [gk.mag_curve("cuerpo", -0.017, 0.017, 0.110, 0.042, gk.polymer(), thickness=0.022, rake=0.004)]


def AT_G19Mag():
    k = gk.accent("oscuro", (0.02, 0.02, 0.022))
    return [gk.side("cuerpo", [(-0.014, 0.0), (0.012, 0.0), (-0.002, -0.070), (-0.024, -0.070)], 0.020, gk.polymer()),
            gk.side("base", [(-0.026, -0.068), (0.000, -0.068), (-0.001, -0.076), (-0.027, -0.076)], 0.022, k)]


ALL = {"AT_ACOG": AT_ACOG, "AT_LPVO": AT_LPVO, "AT_HoloSight": AT_HoloSight, "AT_Thermal": AT_Thermal,
       "AT_TacLight": AT_TacLight, "AT_LancerMag": AT_LancerMag, "AT_SkullMag": AT_SkullMag,
       "AT_AKMag": AT_AKMag, "AT_G19Mag": AT_G19Mag}


ICON_ROT = {"AT_HoloSight": (0, 0, -55)}   # que se vea la ventana


def build(ID):
    pz.reset()
    parts = ALL[ID]()
    obj = pz.finish(ID, parts, tex_size=256, ao=True)
    gk.export(obj, ID, "rifle", {}, icon_rot=ICON_ROT.get(ID, (0, 0, 0)))


if __name__ == "__main__":
    for ID in (sys.argv[1:] or ALL):
        build(ID)
