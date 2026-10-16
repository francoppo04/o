"""AT_MCX: carabina compacta tipo MCX: guardamanos M-LOK largo negro, culata plegable esqueleto,
empuñadura angulada y cargador translúcido con munición a la vista (como la foto). Escala del juego.
Uso: python3 tools/blender/guns/AT_MCX.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import gunkit as gk  # noqa: E402

ID = "AT_MCX"


def build():
    pz.reset()
    m, p = gk.black_metal(), gk.polymer()
    dark = gk.accent("oscuro", (0.02, 0.02, 0.022))
    smoke = gk.accent("translucido", (0.20, 0.17, 0.12))
    b = gk.brass()
    parts = [
        gk.bx("inferior", -0.036, 0.040, -0.0112, 0.0112, -0.004, 0.031, m),
        gk.side("brocal", [(0.012, 0.004), (0.060, 0.004), (0.058, -0.014), (0.016, -0.014)], 0.026, m),
        gk.bx("superior", -0.048, 0.080, -0.0128, 0.0128, 0.031, 0.053, m),
        gk.bx("eyector", 0.004, 0.040, -0.0133, -0.0126, 0.035, 0.047, dark, bevel=0.0),
        gk.bx("palanca_carga", -0.006, 0.014, 0.0128, 0.017, 0.040, 0.047, m),
        # guardamanos largo M-LOK
        gk.bx("guardamanos", 0.080, 0.246, -0.0165, 0.0165, 0.006, 0.053, m, bevel=0.004),
        gk.tube("freno", 0.246, 0.280, 0.0085, m, z=0.030, segs=8),
        # culata plegable esqueleto
        gk.bx("bisagra", -0.056, -0.048, -0.010, 0.010, 0.010, 0.050, m),
        gk.bar("culata_sup", (-0.160, 0.046), (-0.056, 0.046), 0.008, p, width=0.012),
        gk.bar("culata_inf", (-0.160, -0.022), (-0.056, 0.012), 0.007, p, width=0.012),
        gk.bx("cantonera", -0.168, -0.158, -0.015, 0.015, -0.032, 0.054, gk.rubber()),
        gk.side("empunadura", [(-0.008, -0.002), (0.020, -0.002), (0.004, -0.066), (-0.010, -0.072), (-0.030, -0.064)], 0.023, p),
        gk.bx("guardamonte", -0.002, 0.036, -0.004, 0.004, -0.015, -0.010, m),
        # cargador translúcido (cuerpo ahumado + franja de vainas de latón a la vista)
        gk.mag_curve("cargador", 0.018, 0.054, 0.098, 0.010, smoke, rake=0.006),
        gk.mag_curve("vainas", 0.022, 0.034, 0.088, 0.010, b, thickness=0.0215, rake=0.006),
        gk.side("base_cargador", [(0.020, -0.095), (0.070, -0.095), (0.072, -0.106), (0.022, -0.108)], 0.024, dark),
        gk.side("afg", [(0.150, 0.008), (0.196, 0.008), (0.188, -0.012), (0.166, -0.004)], 0.019, p),
    ]
    parts += gk.rail("riel_sup", -0.046, 0.244, 0.053, m)
    for sgn in (1, -1):
        parts += gk.slots(f"mlok{sgn}", 0.092, 0.236, 0.018, 0.040, sgn * 0.0165, dark, n=5)
    obj = pz.finish(ID, parts, tex_size=512, ao=True)
    gk.export(obj, ID, "rifle", {
        "muzzle": (0.280, 0, 0.030),
        "at_optic": (0.020, 0, 0.059),
        "at_light": (0.225, 0, 0.006),
    })


if __name__ == "__main__":
    build()
