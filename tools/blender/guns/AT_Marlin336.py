"""AT_Marlin336: carabina de palanca táctica (.30-30): culata esqueleto con portacartuchos, guardamanos
M-LOK, tubo cargador, riel largo y freno de boca (como la foto). Escala del juego (L94 vanilla de referencia).
Uso: python3 tools/blender/guns/AT_Marlin336.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import gunkit as gk  # noqa: E402

ID = "AT_Marlin336"


def build():
    pz.reset()
    m, p = gk.black_metal(), gk.polymer()
    dark = gk.accent("oscuro", (0.02, 0.02, 0.022))
    b = gk.brass()
    parts = [
        gk.bx("cajon", -0.020, 0.090, -0.0115, 0.0115, -0.004, 0.040, m, bevel=0.003),
        gk.bx("ventana", 0.030, 0.070, -0.0118, -0.0105, 0.010, 0.026, dark, bevel=0.0),
        gk.tube("canon", 0.090, 0.365, 0.0062, m, z=0.030),
        gk.tube("tubo_cargador", 0.090, 0.300, 0.0060, m, z=0.012),
        gk.tube("freno", 0.355, 0.388, 0.0090, m, z=0.030, segs=8),
        gk.bx("guardamanos", 0.095, 0.255, -0.0150, 0.0150, -0.002, 0.040, p, bevel=0.004),
        # palanca (lazo agrandado)
        gk.bar("palanca_a", (0.000, -0.004), (0.010, -0.030), 0.006, m),
        gk.bar("palanca_b", (0.010, -0.030), (0.060, -0.044), 0.006, m),
        gk.bar("palanca_c", (0.060, -0.044), (0.070, -0.010), 0.006, m),
        gk.bar("palanca_d", (0.070, -0.010), (0.060, -0.004), 0.006, m),
        # cuello y culata esqueleto
        gk.side("cuello", [(-0.060, 0.030), (-0.020, 0.036), (-0.020, -0.004), (-0.035, -0.040), (-0.062, -0.030)], 0.024, p),
        gk.bar("culata_sup", (-0.165, 0.036), (-0.060, 0.030), 0.012, p, width=0.022),
        gk.bar("culata_inf", (-0.160, -0.040), (-0.060, -0.030), 0.010, p, width=0.020),
        gk.bx("cantonera", -0.172, -0.160, -0.016, 0.016, -0.048, 0.046, gk.rubber()),
        gk.bx("portacartuchos", -0.140, -0.080, -0.0245, -0.0110, -0.020, 0.024, p),
    ]
    for i in range(5):
        x = -0.134 + i * 0.011
        parts.append(gk.tube(f"cartucho{i}", x, x + 0.006, 0.0035, b, y=-0.026, z=0.002, segs=6))
    parts[-5:] = [pz.cylinder(f"cartucho{i}", 0.0035, 0.032, loc=(-0.131 + i * 0.011, -0.026, 0.002), rot=(0, 0, 0), mat=b, segs=6) for i in range(5)]
    parts += gk.rail("riel_sup", -0.018, 0.150, 0.040, m)
    for sgn in (1, -1):
        parts += gk.slots(f"mlok{sgn}", 0.110, 0.245, 0.010, 0.030, sgn * 0.015, dark, n=4)
    obj = pz.finish(ID, parts, tex_size=512, ao=True)
    gk.export(obj, ID, "rifle", {
        "muzzle": (0.388, 0, 0.030),
        "at_optic": (0.030, 0, 0.046),
        "at_light": (0.205, 0, -0.002),
    })


if __name__ == "__main__":
    build()
