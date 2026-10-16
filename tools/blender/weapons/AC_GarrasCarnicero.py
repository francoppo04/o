"""AC_GarrasCarnicero: guante de boxeo rojo con tres cuchillos de cocina atados con cinta.

Arma de una mano: el origen es el agarre dentro del guante; los cuchillos salen hacia +X.
Uso: python3 tools/blender/weapons/AC_GarrasCarnicero.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import kit  # noqa: E402

ID = "AC_GarrasCarnicero"


def build():
    pz.reset()
    leather = pz.mat("cuero_rojo", (0.48, 0.05, 0.04), dirt=.35, blood=.55, seed=1)
    tape_w = kit.cloth("cinta_deportiva", (0.78, 0.74, 0.64))
    blade = kit.bright_steel("hojas", blood=.6, seed=2)
    handle = kit.rubber("mangos")
    tape = kit.duct("cinta_americana")
    parts = [
        # puño (cuerpo del guante) y pulgar
        pz.sphere("guante", .085, loc=(.03, 0, .01), mat=leather, segs=12, rings=8, scale=(1.25, .95, 1.0)),
        pz.sphere("pulgar", .04, loc=(.06, -.05, -.05), mat=leather, segs=8, rings=6, scale=(1.4, .8, .8)),
        # puño de la muñeca con cinta deportiva
        kit.rod("munieca", -.15, -.04, .058, leather, segs=12, r2=.07),
        kit.rod("vendaje", -.14, -.07, .062, tape_w, segs=12),
    ]
    for i, z in enumerate((.045, .005, -.035)):
        parts.append(pz.box(f"mango{i}", (.11, .03, .022), loc=(.09, 0, z + .065), mat=handle))
        parts.append(kit.knife(f"hoja{i}", .14, .22 - abs(i - 1) * .02, .032, z + .065, blade, thick=.004))
    # dos vueltas de cinta americana sobre nudillos y mangos
    for i, x in enumerate((.06, .12)):
        parts.append(pz.box(f"cinta{i}", (.035, .2, .17), loc=(x, 0, .03), mat=tape, bevel=.01))
    return pz.finish(ID, parts, tex_size=256)


if __name__ == "__main__":
    pz.previews(build(), ID, grip_offset=0.0, hold_rot=(0, -20, 10))
