"""AC_RemoDestripador: remo de kayak de doble pala con un disco de sierra atornillado en cada pala.

A dos manos; el agarre está a un cuarto del largo para que la pala delantera sea la que golpea.
Uso: python3 tools/blender/weapons/AC_RemoDestripador.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import kit  # noqa: E402

ID = "AC_RemoDestripador"


def paddle(name, cx, flip, mat):
    k = -1 if flip else 1
    out = [(cx - .2 * k, .035), (cx - .05 * k, .085), (cx + .14 * k, .09), (cx + .2 * k, .06),
           (cx + .2 * k, -.06), (cx + .14 * k, -.09), (cx - .05 * k, -.085), (cx - .2 * k, -.035)]
    if flip:
        out = list(reversed(out))
    return pz.extrude(name, out, .012, mat=mat, bevel=.003)


def build():
    pz.reset()
    alu = pz.mat("aluminio", (0.55, 0.57, 0.6), dirt=.25, seed=1)
    plastic = pz.mat("pala_naranja", (0.75, 0.25, 0.03), dirt=.3, blood=.55, seed=2)
    saw = kit.steel("disco", rust=.25, blood=.6, seed=3)
    grip = kit.rubber()
    bolts = kit.dark_steel("bulones", rust=.2)
    parts = [kit.rod("caño", -.38, 1.12, .016, alu, segs=10)]
    parts += [kit.rod("grip1", -.05, .12, .019, grip), kit.rod("grip2", .55, .72, .019, grip)]
    parts += [paddle("pala_a", -.56, True, plastic), paddle("pala_b", 1.3, False, plastic)]
    for name, cx in (("sierra_a", -.58), ("sierra_b", 1.32)):
        parts.append(kit.saw_disc(name, cx, 0, .13, saw, teeth=26, y=-.009))
        parts.append(kit.bolt(name + "_eje", (cx, -.014, 0), .016, bolts))
        for dx, dz in ((.06, .04), (-.06, -.04)):
            parts.append(kit.bolt(name + f"_b{dx}", (cx + dx, -.012, dz), .007, bolts))
    return pz.finish(ID, parts, tex_size=256)


if __name__ == "__main__":
    pz.previews(build(), ID, grip_offset=0.0, hold_rot=(0, -55, 30))
