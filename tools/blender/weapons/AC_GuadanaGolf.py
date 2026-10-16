"""AC_GuadanaGolf: hierro 7 con una hoz soldada a la cabeza y una pelota de golf ensartada en la punta.

A dos manos; agarre en el extremo del grip.
Uso: python3 tools/blender/weapons/AC_GuadanaGolf.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import kit  # noqa: E402

ID = "AC_GuadanaGolf"


def build():
    pz.reset()
    grip = kit.rubber("grip")
    chrome = pz.mat("cromo", pz.CHROME, dirt=.2, seed=1)
    head = pz.mat("cabeza", (0.5, 0.52, 0.55), rust=.25, dirt=.3, seed=2)
    sickle = kit.steel("hoz", rust=.35, blood=.6, seed=3)
    ball = pz.mat("pelota", pz.WHITE, dirt=.2, blood=.55, seed=4)
    parts = [kit.rod("grip", -.03, .24, .014, grip, segs=8, r2=.012),
             kit.rod("vara", .24, .9, .009, chrome, segs=8, r2=.006),
             kit.rod("cuello", .88, .93, .01, chrome, segs=8)]
    # cabeza del hierro 7 (cuelga hacia -Z)
    parts.append(pz.extrude("hierro", [(.9, .01), (.96, .01), (.98, -.08), (.95, -.09), (.89, -.075)], .018,
                            mat=head, bevel=.003))
    # hoz: medialuna que nace arriba de la cabeza, sube y se curva hacia +X; filo en el lado interno
    outer, inner = [], []
    for i in range(9):
        th = math.radians(90 * i / 8)
        outer.append((.91 + .2 * (1 - math.cos(th)), .005 + .26 * math.sin(th)))
        inner.append((.965 + .13 * (1 - math.cos(th)), .005 + .19 * math.sin(th)))
    tip = (1.17, .235)
    pts = outer + [tip] + list(reversed(inner))
    parts.append(pz.extrude("hoz", pts, .006, mat=sickle, taper_edge=list(range(10, 19))))
    parts.append(pz.sphere("pelota", .021, loc=(tip[0], 0, tip[1]), mat=ball, segs=10, rings=7))
    return pz.finish(ID, parts, tex_size=256)


if __name__ == "__main__":
    pz.previews(build(), ID, grip_offset=0.0, hold_rot=(0, -55, 30))
