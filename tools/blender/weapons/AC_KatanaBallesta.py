"""AC_KatanaBallesta: katana forjada con la ballesta (elástico) de una camioneta.

Mango envuelto en cinturón de seguridad, guarda de piñón de moto y pomo con el ojo enrollado del
elástico. A dos manos; agarre cerca del pomo.
Uso: python3 tools/blender/weapons/AC_KatanaBallesta.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import kit  # noqa: E402

ID = "AC_KatanaBallesta"


def build():
    pz.reset()
    forged = pz.mat("acero_forjado", (0.16, 0.16, 0.17), rust=.4, dirt=.3, seed=1)
    edge = kit.bright_steel("filo", blood=.55, seed=2)
    belt = pz.mat("cinturon", (0.20, 0.21, 0.23), dirt=.4, seed=3)
    brass = pz.mat("habaki", pz.BRASS, dirt=.3, seed=4)
    parts = [kit.rod("tsuka", -.04, .25, .02, belt, segs=8),
             kit.rod("ojo", -.07, -.03, .028, forged, segs=10),
             pz.cylinder("pinion", .048, .012, loc=(.26, 0, 0), mat=forged, segs=14, smooth=False),
             kit.rod("habaki", .265, .3, .016, brass, segs=8)]
    for i in range(6):  # vueltas cruzadas del cinturón
        parts.append(kit.band(f"vuelta{i}", .0 + i * .042, .022, .012, belt))
    # hoja curva: lomo arriba, filo abajo (afilado)
    n = 12
    spine, ed = [], []
    for i in range(n + 1):
        t = i / n
        x = .3 + .68 * t
        sag = .03 * t * t
        spine.append((x, .018 + sag))
        ed.append((x, -.018 + sag * .9))
    tip = (1.03, .045)
    outline = spine + [tip] + list(reversed(ed))
    taper = list(range(n + 2, 2 * n + 3))
    parts.append(pz.extrude("hoja", outline, .008, mat=forged, taper_edge=taper))
    # banda brillante del filo amolado
    parts.append(pz.extrude("filo", [(p[0], p[1] + .002) for p in ed] +
                            [(p[0], p[1] + .011) for p in reversed(ed)], .0085, mat=edge))
    return pz.finish(ID, parts, tex_size=256)


if __name__ == "__main__":
    pz.previews(build(), ID, grip_offset=0.0, hold_rot=(0, -55, 30))
