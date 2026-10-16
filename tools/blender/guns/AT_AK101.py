"""AT_AK101: AK corta en 5.56 (tipo AK-101/105): culata plegable triangular, guardamanos negro,
riel lateral para mira, freno de boca y cargador curvo. Escala del juego. Uso: python3 tools/blender/guns/AT_AK101.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import gunkit as gk  # noqa: E402

ID = "AT_AK101"


def build():
    pz.reset()
    m, p = gk.black_metal(), gk.polymer()
    dark = gk.accent("oscuro", (0.02, 0.02, 0.022))
    parts = [
        gk.bx("cajon", -0.050, 0.100, -0.0125, 0.0125, -0.002, 0.036, m),
        gk.tube("tapa", -0.050, 0.098, 0.0125, m, z=0.034, segs=12),
        gk.bx("selector", -0.010, 0.060, -0.0135, -0.0125, 0.012, 0.020, dark, bevel=0.0),
        # montura lateral + plataforma de mira arriba del cajón
        gk.bx("montura", -0.004, 0.064, 0.0125, 0.020, 0.008, 0.040, m),
        gk.bx("puente", -0.004, 0.064, -0.006, 0.020, 0.040, 0.052, m),
        # guardamanos inferior, tubo de gases y guardamanos superior
        gk.bx("guardamanos", 0.100, 0.205, -0.0155, 0.0155, -0.002, 0.030, p, bevel=0.004),
        gk.tube("tubo_gases", 0.100, 0.230, 0.0065, m, z=0.046, segs=10),
        gk.tube("guarda_sup", 0.100, 0.190, 0.0105, p, z=0.044, segs=10),
        gk.tube("canon", 0.205, 0.268, 0.0058, m, z=0.020),
        gk.bx("bloque_gas", 0.222, 0.236, -0.008, 0.008, 0.012, 0.050, m),
        gk.bx("mira_del", 0.244, 0.256, -0.007, 0.007, 0.010, 0.050, m),
        gk.tube("freno", 0.262, 0.298, 0.0092, m, z=0.020, segs=8),
        # culata plegable triangular
        gk.bar("culata_sup", (-0.168, 0.034), (-0.050, 0.032), 0.007, m, width=0.010),
        gk.bar("culata_inf", (-0.168, -0.028), (-0.050, 0.002), 0.007, m, width=0.010),
        gk.bx("culata_pie", -0.176, -0.164, -0.012, 0.012, -0.034, 0.040, m),
        gk.side("empunadura", [(-0.010, 0.000), (0.018, 0.000), (0.002, -0.064), (-0.014, -0.068), (-0.032, -0.060)], 0.024, p),
        gk.bx("guardamonte", -0.004, 0.040, -0.004, 0.004, -0.014, -0.009, m),
        gk.mag_curve("cargador", 0.044, 0.078, 0.110, 0.042, p, thickness=0.022, rake=0.004),
        gk.bx("palanca", 0.070, 0.085, -0.019, -0.0125, 0.022, 0.030, m),
    ]
    parts += gk.rail("riel_inf", 0.130, 0.200, -0.008, m, w=0.018)
    obj = pz.finish(ID, parts, tex_size=512, ao=True)
    gk.export(obj, ID, "rifle", {
        "muzzle": (0.298, 0, 0.020),
        "at_optic": (0.030, 0.007, 0.052),
        "at_light": (0.165, 0, -0.008),
    })


if __name__ == "__main__":
    build()
