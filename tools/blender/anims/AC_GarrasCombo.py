"""Garras de Carnicero: combo de box (jab izquierdo, cross derecho, gancho izquierdo).

Desde la guardia de cuchillo del juego sube a guardia de boxeo (puños a la altura del mentón,
pie izquierdo adelante), tira jab-cross-gancho con giro de cadera y pivote de pie en cada golpe y
vuelve a la guardia. 30 frames a 30 fps (1 s). Uso: python3 tools/blender/anims/AC_GarrasCombo.py [--preview]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import animkit as ak  # noqa: E402

NAME = "Bob_AC_GarrasCombo"
WEAPON = "AC_GarrasCarnicero"
FRAMES = 30
HITS = (7, 14, 23)
BASE = "Bob_IdleAimBat"     # postura de piernas: pie izquierdo adelante, como un boxeador diestro
GRIP = "fists"

UP_R = ((-7, -9, 80), (0, -0.45, 0.9), (-0.85, -0.45, 0))      # guardia de boxeo (centro, nudillos, dorso)
UP_L = ((5, -21, 80), (0, -0.45, 0.9), (0.85, -0.45, 0))
FISTS = {
    1: "guard",
    4: {"R": UP_R, "L": UP_L},
    7: {"R": UP_R, "L": ((4, -42, 79), (0.02, -1, 0.04), (0, 0, 1))},          # JAB
    10: {"R": UP_R, "L": UP_L},
    14: {"R": ((-1, -42, 80), (0.06, -1, 0.02), (0, 0, 1)), "L": UP_L},        # CROSS
    18: {"R": UP_R, "L": UP_L},
    20: {"R": UP_R, "L": ((17, -19, 81), (-0.3, -0.7, 0.1), (0, 0, 1))},       # carga del gancho
    23: {"R": UP_R, "L": ((-1, -35, 81), (-0.95, -0.3, 0), (0, 0, 1))},        # GANCHO
    26: {"R": UP_R, "L": UP_L},
    30: "guard",
}
EASE = {1: "io", 4: "in", 7: "out", 10: "in", 14: "out", 18: "io", 20: "in", 23: "out", 26: "io"}
BODY = {
    1: {},
    4: {"crouch": 2, "lean": 6},
    7: {"twist": -22, "hips_yaw": -6, "crouch": 3, "lean": 8, "shift": (0, -2, 0)},
    10: {"crouch": 2, "lean": 6},
    14: {"twist": 40, "hips_yaw": 22, "crouch": 4, "lean": 10, "shift": (1, -4, 0)},
    18: {"twist": 5, "crouch": 2, "lean": 6},
    20: {"twist": 15, "hips_yaw": 8, "crouch": 3, "lean": 6},
    23: {"twist": -42, "hips_yaw": -22, "crouch": 4, "lean": 8, "shift": (-1, -2, 0)},
    26: {"crouch": 2, "lean": 6},
    30: {},
}
FEET = {1: {}, 10: {}, 14: {"R": (0, -1, 1, 28)}, 18: {}, 23: {"L": (0, 0, 1, -22)}, 26: {}, 30: {}}

if __name__ == "__main__":
    ak.build(sys.modules[__name__], preview="--preview" in sys.argv)
