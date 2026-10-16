"""AC_LanzaTijera: media tijera de podar atada con alambre a un mango de jardín verde, con trapo rojo.

Lanza a dos manos: el agarre está a 0,35 m del extremo del mango.
Uso: python3 tools/blender/weapons/AC_LanzaTijera.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import kit  # noqa: E402

ID = "AC_LanzaTijera"


def build():
    pz.reset()
    green = pz.mat("mango_verde", (0.10, 0.30, 0.10), dirt=.4, seed=1)
    blade = kit.bright_steel("hoja", blood=.6, seed=2)
    wire = kit.steel("alambre", rust=.5, seed=3)
    rag = pz.mat("trapo", (0.50, 0.04, 0.03), dirt=.4, seed=4)
    parts = [kit.rod("mango", -.35, 1.0, .015, green, segs=10),
             kit.rod("tapa", -.37, -.34, .017, kit.rubber())]
    # hoja ondulada (filo hacia -Z) y gancho trasero
    edge = []
    for i in range(11):
        x = 1.0 + i * .035
        edge.append((x, -.03 - (.006 if i % 2 else 0)))
    outline = [(.93, .022), (1.25, .03), (1.42, .0)] + list(reversed(edge)) + [(.93, -.022)]
    parts.append(pz.extrude("hoja", outline, .006, mat=blade, taper_edge=list(range(3, 3 + len(edge)))))
    parts.append(pz.extrude("gancho", [(.97, -.02), (1.02, -.02), (.95, -.11), (.93, -.1)], .006, mat=blade))
    parts.append(kit.bolt("perno", (.97, -.006, 0), .012, wire))
    for i in range(5):
        parts.append(kit.band(f"alambre{i}", .9 + i * .02, .02, .008, wire))
    parts.append(kit.band("abrazadera", 1.01, .022, .014, wire))
    # trapo rojo colgando
    parts.append(pz.box("trapo1", (.04, .006, .16), loc=(.87, 0, -.09), rot=(0, 8, 0), mat=rag))
    parts.append(pz.box("trapo2", (.03, .006, .12), loc=(.84, .006, -.07), rot=(0, -10, 0), mat=rag))
    return pz.finish(ID, parts, tex_size=256)


if __name__ == "__main__":
    pz.previews(build(), ID, grip_offset=0.0, hold_rot=(0, -40, 25))
