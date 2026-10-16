"""AT_M4: carabina M4 con guardamanos de riel cuádruple FDE, culata SOPMOD, empuñadura angulada y
cargador gris con base de calavera (como la foto). Escala del juego (M16 vanilla de referencia).
Uso: python3 tools/blender/guns/AT_M4.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import gunkit as gk  # noqa: E402

ID = "AT_M4"


def build():
    pz.reset()
    m, p, t, g = gk.black_metal(), gk.polymer(), gk.fde(), gk.grey("gris_cargador")
    dark = gk.accent("oscuro", (0.025, 0.025, 0.028))
    parts = [
        # cajón inferior con brocal y superior con puerta de expulsión
        gk.bx("inferior", -0.036, 0.040, -0.0112, 0.0112, -0.004, 0.031, m),
        gk.side("brocal", [(0.012, 0.004), (0.060, 0.004), (0.058, -0.014), (0.016, -0.014)], 0.026, m),
        gk.bx("superior", -0.042, 0.074, -0.0125, 0.0125, 0.031, 0.052, m),
        gk.bx("eyector", 0.004, 0.040, -0.0131, -0.0124, 0.035, 0.047, dark, bevel=0.0),
        gk.tube("asist", -0.012, 0.004, 0.0045, m, y=-0.012, z=0.046, segs=8),
        gk.bx("palanca_carga", -0.050, -0.040, -0.011, 0.011, 0.045, 0.051, m),
        # cañón y apagallamas
        gk.tube("canon", 0.240, 0.312, 0.0055, m, z=0.030),
        gk.tube("apagallamas", 0.300, 0.334, 0.0078, m, z=0.030, segs=8),
        gk.bx("punto", 0.228, 0.238, -0.003, 0.003, 0.055, 0.070, m),
        gk.bx("alza", -0.030, -0.019, -0.006, 0.006, 0.057, 0.069, m),
        # culata SOPMOD sobre tubo buffer
        gk.tube("tubo_buffer", -0.140, -0.036, 0.0105, m, z=0.033),
        gk.side("culata", [(-0.166, 0.052), (-0.105, 0.049), (-0.098, 0.022), (-0.112, 0.004),
                           (-0.130, -0.026), (-0.168, -0.032)], 0.032, p),
        gk.bx("cantonera", -0.172, -0.164, -0.0165, 0.0165, -0.034, 0.054, gk.rubber()),
        # empuñadura, guardamonte, cola del disparador
        gk.side("empunadura", [(-0.008, -0.002), (0.020, -0.002), (0.004, -0.066), (-0.010, -0.072), (-0.030, -0.064)], 0.023, p),
        gk.bx("guardamonte", -0.002, 0.036, -0.004, 0.004, -0.015, -0.010, m),
        gk.bx("cola", 0.014, 0.018, -0.0015, 0.0015, -0.012, -0.002, m, bevel=0.0),
        # cargador STANAG gris con base de calavera
        gk.mag_curve("cargador", 0.018, 0.054, 0.098, 0.010, g, rake=0.006),
        gk.side("calavera", [(0.020, -0.095), (0.074, -0.095), (0.076, -0.111), (0.022, -0.113)], 0.026, dark),
        # empuñadura angulada
        gk.side("afg", [(0.112, 0.008), (0.160, 0.008), (0.152, -0.010), (0.128, -0.004)], 0.02, p),
    ]
    parts += gk.rail("riel_sup", -0.040, 0.074, 0.052, m)
    parts += gk.quad_rail("ris", 0.076, 0.240, 0.030, 0.0185, t)
    obj = pz.finish(ID, parts, tex_size=512, ao=True)
    gk.export(obj, ID, "rifle", {
        "muzzle": (0.334, 0, 0.030),
        "at_optic": (0.010, 0, 0.058),
        "at_light": (0.205, 0, 0.005),
    })


if __name__ == "__main__":
    build()
