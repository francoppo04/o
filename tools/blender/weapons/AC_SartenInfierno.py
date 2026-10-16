"""AC_SartenInfierno: sartén de hierro fundido con una corona de tornillos afilados en el borde.

Una mano; el agarre está cerca del extremo del mango.
Uso: python3 tools/blender/weapons/AC_SartenInfierno.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import kit  # noqa: E402

ID = "AC_SartenInfierno"
R = .13          # radio de la sartén
CX = .33         # centro de la sartén sobre X


def build():
    pz.reset()
    iron = pz.mat("hierro", (0.10, 0.10, 0.11), rust=.35, dirt=.3, blood=.55, seed=1)
    leather = kit.wood("cuero", (0.30, 0.17, 0.08), seed=2)
    spikes = kit.steel("puas", rust=.4, blood=.55, seed=3)
    parts = [kit.rod("mango", -.04, CX - R + .01, .014, iron, segs=8, r2=.017),
             kit.rod("tiento", -.02, .12, .018, leather, segs=8)]
    # cuerpo de la sartén: disco (cara hacia ±Y) con borde
    parts.append(pz.cylinder("fondo", R, .02, loc=(CX, 0, 0), rot=(90, 0, 0), mat=iron, segs=20))
    parts.append(pz.cylinder("borde", R + .008, .045, loc=(CX, .012, 0), rot=(90, 0, 0), mat=iron, segs=20,
                             r2=R + .015))
    # corona de púas en el borde (sin púa donde entra el mango)
    for i in range(12):
        a = 2 * math.pi * i / 12 + .26
        dx, dz = math.cos(a), math.sin(a)
        if dx < -.85:
            continue
        parts.append(kit.spike(f"pua{i}", (CX + R * dx, R * dz), (dx, dz), .06, .009, spikes))
    parts.append(kit.bolt("bulon", (CX, -.014, 0), .022, spikes))
    return pz.finish(ID, parts, tex_size=256)


if __name__ == "__main__":
    pz.previews(build(), ID, grip_offset=0.0, hold_rot=(0, -30, 20))
