"""Garras de Carnicero: combo de box con los dos guantes (jab de izquierda, cross de derecha,
gancho de izquierda). Guardia alta, giro de torso en cada golpe. 30 frames a 30 fps (1 s).

Uso: python3 tools/blender/anims/AC_GarrasCombo.py [--preview]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import animlib as al  # noqa: E402

NAME = "Bob_AC_GarrasCombo"
HITS = (6, 15, 24)

FWD = (0, -1, 0)
UP = (0, 0, 1)
GUARD_R = ((-9, -14, 71), (0.15, -0.6, 0.8), (0.3, 0.7, 0.4))   # puño frente a la cara, nudillos arriba
GUARD_L = ((9, -16, 72), (-0.15, -0.6, 0.8), (-0.3, 0.7, 0.4))
# frame: (puño derecho, puño izquierdo, cadera, torso)   puño = (pos, nudillos, dorso)
KEYS = {
    1:  (GUARD_R, GUARD_L, 0, 0),
    6:  (GUARD_R, ((4, -38, 70), FWD, UP), 10, 15),                  # jab
    10: (GUARD_R, GUARD_L, 0, 0),
    15: (((-2, -40, 68), FWD, UP), GUARD_L, 25, 35),                 # cross (las garras de la derecha)
    19: (GUARD_R, GUARD_L, 0, 0),
    24: (GUARD_R, ((-4, -28, 71), (-1, -0.5, 0), (0, 0.3, 1)), -20, -35),   # gancho de izquierda
    30: (GUARD_R, GUARD_L, 0, 0),
}


def build():
    rig = al.load_rig()
    an = al.Animator(rig, NAME, two_hands=False)
    for f, (r, l, hips, chest) in KEYS.items():
        an.body(f, hips=hips, chest=chest, lean=8)
        an.props(f, al.fist("R", *r), al.fist("L", *l))
    return rig, an.finish(1, 30)


if __name__ == "__main__":
    rig, action = build()
    out = al.ROOT / "art" / "anims"
    al.export_glb(rig, action, out / f"{NAME}.glb")
    if "--preview" in sys.argv:
        al.attach_weapon(rig, "AC_GarrasCarnicero")
        al.attach_weapon(rig, "AC_GarrasCarniceroL", bone="Bip01_Prop2", tex_id="AC_GarrasCarnicero")
        al.render_preview(rig, list(range(1, 31, 2)), out / f"{NAME}_sheet.png", gif=out / f"{NAME}.gif")
