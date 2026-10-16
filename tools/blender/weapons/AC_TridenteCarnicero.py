"""AC_TridenteCarnicero: horquilla de granja con un cuchillo de carnicero atado en cada diente.

Lanza a dos manos: el agarre está a 0,35 m del extremo del mango.
Uso: python3 tools/blender/weapons/AC_TridenteCarnicero.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import kit  # noqa: E402

ID = "AC_TridenteCarnicero"


def build():
    pz.reset()
    wood = kit.wood("mango", pz.WOOD_LIGHT, seed=1)
    iron = kit.dark_steel("horquilla", rust=.5, seed=2)
    blade = kit.bright_steel("cuchillos", blood=.6, seed=3)
    handle = kit.rubber("mangos_cuchillo")
    tape = kit.duct()
    parts = [kit.rod("mango", -.35, 1.05, .017, wood, segs=10),
             kit.rod("virola", 1.0, 1.1, .02, iron, r2=.013)]
    parts.append(pz.box("travesaño", (.03, .025, .2), loc=(1.11, 0, 0), mat=iron, bevel=.006))
    for i, z in enumerate((-.085, 0, .085)):
        parts.append(kit.rod(f"diente{i}", 1.11, 1.33, .008, iron, z=z, segs=6, r2=.006))
        big = i == 1
        parts.append(pz.box(f"mango{i}", (.11, .02, .026), loc=(1.33, 0, z), mat=handle))
        parts.append(kit.knife(f"cuchillo{i}", 1.38, .26 if big else .2, .06 if big else .042,
                               z, blade, thick=.004))
        for x in (1.29, 1.36):
            parts.append(pz.box(f"cinta{i}_{x}", (.025, .03, .04), loc=(x, 0, z), mat=tape))
    return pz.finish(ID, parts, tex_size=256)


if __name__ == "__main__":
    pz.previews(build(), ID, grip_offset=0.0, hold_rot=(0, -40, 25))
