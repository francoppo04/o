"""Partes de Arsenal Táctico: miras, linterna y cargadores (los de la foto).
Origen en la base de montaje; X hacia adelante, Z hacia arriba (la linterna cuelga hacia -Z).
Uso: python3 tools/blender/guns/parts.py [ID ...]   (sin argumentos: todas)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import gunkit as gk  # noqa: E402


def mount(m, x0=-0.018, x1=0.030, h=0.008, w=0.0105):
    """Base de montaje picatinny con tornillo de ajuste del lado derecho."""
    return [gk.bx("montura", x0, x1, -w, w, 0.0, h, m, bevel=0.0012),
            gk.bx("garra", x0 + 0.004, x1 - 0.004, -w - 0.002, -w, -0.002, h * 0.8, m, bevel=0.0006),
            pz.cylinder("perilla_montura", 0.0035, 0.004, loc=((x0 + x1) / 2, -w - 0.003, h * 0.4), rot=(90, 0, 0),
                        mat=m, segs=12)]


def rings(name, x, z, r, mat, n=3, w=0.0012, gap=0.0024, y=0.0):
    """Anillos de agarre (moleteado) alrededor de un tubo sobre X."""
    return [gk.tube(f"{name}{i}", x + i * gap, x + i * gap + w, r, mat, y=y, z=z, segs=20) for i in range(n)]


def AT_ACOG():
    """Mira de combate 4x tipo ACOG: carcasa con fibra óptica y mini punto rojo encima."""
    m, k = gk.black_metal(), gk.accent("oscuro", (0.02, 0.02, 0.022))
    fib = gk.accent("fibra", (0.62, 0.14, 0.05))
    z = 0.024
    return mount(m, -0.020, 0.026) + [
        gk.lathe_x("cuerpo", [(-0.050, 0.0), (-0.050, 0.0105), (-0.034, 0.0115), (-0.026, 0.0105), (0.018, 0.0105),
                              (0.030, 0.0130), (0.052, 0.0135), (0.054, 0.0120), (0.054, 0.0)], m, z=z, segs=24),
        gk.side("carcasa", [(-0.026, 0.008), (0.026, 0.008), (0.020, 0.036), (-0.020, 0.036)], 0.020, m, bevel=0.003),
        gk.side("cuello", [(-0.016, 0.0), (0.020, 0.0), (0.020, 0.012), (-0.016, 0.012)], 0.016, m, bevel=0.001),
        gk.bx("fibra", -0.018, 0.016, -0.0045, 0.0045, 0.036, 0.040, fib, bevel=0.0008),
        gk.bx("minipunto", -0.012, 0.008, -0.007, 0.007, 0.040, 0.050, k, bevel=0.0015),
        gk.bx("ventanita", -0.004, -0.002, -0.005, 0.005, 0.042, 0.049, gk.glass(), bevel=0.0),
        pz.cylinder("torreta_sup", 0.0055, 0.006, loc=(0.010, 0, 0.0355), rot=(0, 0, 0), mat=m, segs=14),
        pz.cylinder("torreta_lat", 0.0055, 0.006, loc=(0.000, -0.012, z), rot=(90, 0, 0), mat=m, segs=14),
        gk.tube("ocular", -0.058, -0.050, 0.0100, gk.rubber(), z=z, segs=20),
        gk.tube("lente", 0.0535, 0.0545, 0.0118, gk.glass(), z=z, segs=20),
        gk.tube("lente_ocular", -0.0585, -0.0578, 0.0072, gk.glass(), z=z, segs=20),
    ] + rings("aro_obj", 0.036, z, 0.0137, m)


def AT_LPVO():
    """Mira variable 1-6x color tierra (como la Vortex de la foto) en montura de una pieza."""
    m, t = gk.black_metal(), gk.fde()
    z = 0.030
    body = gk.lathe_x("tubo", [(-0.084, 0.0), (-0.084, 0.0150), (-0.064, 0.0150), (-0.058, 0.0125),
                               (-0.050, 0.0112), (0.044, 0.0112), (0.058, 0.0150), (0.086, 0.0158),
                               (0.088, 0.0145), (0.088, 0.0)], t, z=z, segs=28)
    return mount(m, -0.030, 0.040) + [
        body,
        gk.tube("anillo1", -0.026, -0.016, 0.0130, m, z=z, segs=24),
        gk.tube("anillo2", 0.026, 0.036, 0.0130, m, z=z, segs=24),
        gk.side("brazo", [(-0.030, 0.006), (0.040, 0.006), (0.036, 0.020), (0.022, 0.020), (0.014, 0.012),
                          (-0.008, 0.012), (-0.014, 0.020), (-0.028, 0.020)], 0.012, m, bevel=0.001),
        gk.tube("aumento", -0.062, -0.054, 0.0156, m, z=z, segs=24),
        gk.bx("palanca_aum", -0.060, -0.056, -0.020, -0.0150, z - 0.002, z + 0.004, m, bevel=0.0005),
        pz.cylinder("torreta_sup", 0.0085, 0.010, loc=(0.005, 0, z + 0.016), rot=(0, 0, 0), mat=t, segs=18),
        pz.cylinder("torreta_lat", 0.0085, 0.010, loc=(0.005, -0.016, z), rot=(90, 0, 0), mat=t, segs=18),
        pz.cylinder("iluminacion", 0.007, 0.008, loc=(0.005, 0.015, z), rot=(90, 0, 0), mat=m, segs=16),
        gk.tube("lente", 0.0875, 0.0885, 0.0140, gk.glass(), z=z, segs=24),
        gk.tube("lente_ocular", -0.0845, -0.0838, 0.0120, gk.glass(), z=z, segs=24),
    ] + rings("estrias_aum", -0.064, z, 0.0158, m, n=3)


def AT_HoloSight():
    """Mira holográfica con capucha (como la de la AK de la foto): ventana rectangular, botones atrás."""
    m = gk.black_metal()
    hood = gk.side("capucha", [(-0.016, 0.016), (0.020, 0.016), (0.020, 0.046), (0.012, 0.050), (-0.008, 0.050),
                               (-0.016, 0.042)], 0.026, m, bevel=0.002)
    return mount(m, -0.020, 0.024) + [
        gk.bx("base_alta", -0.022, 0.024, -0.013, 0.013, 0.008, 0.017, m, bevel=0.0015),
        hood,
        gk.bx("ventana", -0.010, 0.014, -0.0095, 0.0095, 0.021, 0.044, gk.accent("hueco", (0.01, 0.01, 0.012)),
              bevel=0.0),
        gk.bx("vidrio", 0.012, 0.0135, -0.0095, 0.0095, 0.021, 0.044, gk.glass(), bevel=0.0),
        gk.bx("botonera", -0.026, -0.016, -0.009, 0.009, 0.017, 0.030, m, bevel=0.0015),
        pz.cylinder("boton1", 0.0025, 0.003, loc=(-0.0265, -0.004, 0.024), rot=(0, 90, 0), mat=gk.rubber(), segs=10),
        pz.cylinder("boton2", 0.0025, 0.003, loc=(-0.0265, 0.004, 0.024), rot=(0, 90, 0), mat=gk.rubber(), segs=10),
        pz.cylinder("pila", 0.0050, 0.012, loc=(0.004, 0.016, 0.012), rot=(0, 90, 0), mat=m, segs=14),
    ]


def AT_Thermal():
    """Mira térmica (como la de la foto): cuerpo con botonera, aro naranja y ocular de goma acanalado."""
    m, o, r = gk.black_metal(), gk.accent("naranja", (0.85, 0.30, 0.05)), gk.rubber()
    z = 0.030
    return mount(m, -0.024, 0.030) + [
        gk.side("cuerpo", [(-0.050, 0.010), (0.046, 0.010), (0.046, 0.048), (0.030, 0.054), (-0.040, 0.054),
                           (-0.050, 0.046)], 0.036, m, bevel=0.005),
        gk.lathe_x("objetivo", [(0.044, 0.0), (0.044, 0.0175), (0.060, 0.0185), (0.072, 0.0190), (0.072, 0.0)], m,
                   z=z, segs=24),
        gk.tube("aro", 0.046, 0.053, 0.0198, o, z=z, segs=24),
        gk.tube("lente", 0.0715, 0.0725, 0.0165, gk.accent("germanio", (0.08, 0.07, 0.10)), z=z, segs=24),
        gk.lathe_x("ocular", [(-0.086, 0.0), (-0.086, 0.0185), (-0.074, 0.0175), (-0.062, 0.0150),
                              (-0.048, 0.0140), (-0.048, 0.0)], r, z=z, segs=24),
    ] + rings("acanalado", -0.084, z, 0.0188, r, n=4, w=0.0015, gap=0.0042) + [
        pz.cylinder(f"boton{i}", 0.0042, 0.004, loc=(-0.026 + i * 0.013, -0.019, 0.034), rot=(90, 0, 0),
                    mat=r, segs=12) for i in range(4)]


def AT_TacLight():
    """Linterna táctica: montura bajo el riel, cuerpo moleteado y cabeza ancha (corta, para no chocar con
    la empuñadura angulada)."""
    m = gk.black_metal()
    z = -0.016
    return [
        gk.bx("montura", -0.012, 0.016, -0.0095, 0.0095, -0.008, 0.0, m, bevel=0.001),
        pz.cylinder("perilla", 0.0035, 0.004, loc=(0.002, -0.0115, -0.004), rot=(90, 0, 0), mat=m, segs=12),
        gk.lathe_x("cuerpo", [(-0.030, 0.0), (-0.030, 0.0065), (-0.026, 0.0080), (0.020, 0.0080), (0.026, 0.0105),
                              (0.044, 0.0112), (0.046, 0.0105), (0.046, 0.0)], m, z=z, segs=22),
        gk.tube("interruptor", -0.036, -0.029, 0.0060, gk.rubber(), z=z, segs=16),
    ] + rings("moleteado", -0.022, z, 0.0084, m, n=5, w=0.0014, gap=0.0032) + [
        gk.tube("lente", 0.0455, 0.0462, 0.0098, gk.accent("lente", (0.85, 0.88, 0.9)), z=z, segs=22)]


def AT_Granada40():
    """Granada de 40 mm: vaina de aluminio con culote, ojiva verde oliva y franja amarilla (alto explosivo)."""
    al, ol = gk.accent("aluminio", (0.55, 0.56, 0.58)), gk.accent("oliva", (0.24, 0.27, 0.16))
    am = gk.accent("franja", (0.80, 0.62, 0.08))
    return [gk.lathe_x("vaina", [(0.0, 0.0), (0.0, 0.0150), (0.004, 0.0150), (0.004, 0.0138), (0.030, 0.0138),
                                 (0.030, 0.0)], al, segs=24),
            gk.lathe_x("ojiva", [(0.029, 0.0), (0.029, 0.0140), (0.044, 0.0140), (0.056, 0.0105),
                                 (0.064, 0.0050), (0.066, 0.0)], ol, segs=24),
            gk.tube("franja", 0.033, 0.036, 0.0142, am, segs=24),
            gk.tube("culote", -0.0008, 0.0002, 0.0050, gk.brass(), segs=16)]


def _mag_photo(gun, origin_px, **kw):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    mod = __import__(gun)
    P = gk.Photo(gun, origin_px=origin_px, origin=(0.0, 0.0), bore_px=mod.P_BORE, scale=mod.P.k, **kw)
    return mod.magazine(P)


def AT_SkullMag():
    return _mag_photo("AT_M4", (650, 1001))


def AT_LancerMag():
    return _mag_photo("AT_MCX", (553, 227))


def AT_AKMag():
    return _mag_photo("AT_AK101", (548, 539), flip=True)


def AT_G19Mag():
    p, k = gk.polymer(), gk.accent("oscuro", (0.02, 0.02, 0.022))
    from shapely.geometry import Polygon
    body = Polygon([(-0.014, 0.0), (0.012, 0.0), (-0.002, -0.068), (-0.026, -0.068)])
    return (gk.slab("cuerpo", body, 0.018, p, bevel=0.0015) +
            gk.slab("base", Polygon([(-0.028, -0.066), (0.000, -0.066), (-0.001, -0.076), (-0.029, -0.076)]), 0.021,
                    k, bevel=0.002, segs=3) +
            gk.decal("labio", Polygon([(-0.012, -0.001), (0.010, -0.001), (0.009, -0.004), (-0.011, -0.004)]),
                     0.0091, gk.brass()) +
            [gk.pin(f"testigo{i}", -0.004 - i * 0.0034, -0.012 - i * 0.0155, 0.0012, k, 0.0091, segs=8)
             for i in range(4)])


ALL = {"AT_ACOG": AT_ACOG, "AT_LPVO": AT_LPVO, "AT_HoloSight": AT_HoloSight, "AT_Thermal": AT_Thermal,
       "AT_TacLight": AT_TacLight, "AT_LancerMag": AT_LancerMag, "AT_SkullMag": AT_SkullMag,
       "AT_AKMag": AT_AKMag, "AT_G19Mag": AT_G19Mag, "AT_Granada40": AT_Granada40}


ICON_ROT = {"AT_HoloSight": (0, 0, -55)}   # que se vea la ventana


def build(ID):
    pz.reset()
    parts = ALL[ID]()
    obj = gk.finish_gun(ID, parts, tex_size=512)
    gk.export(obj, ID, "rifle", {}, icon_rot=ICON_ROT.get(ID, (0, 0, 0)))


if __name__ == "__main__":
    for ID in (sys.argv[1:] or ALL):
        build(ID)
