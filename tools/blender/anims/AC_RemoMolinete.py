"""Remo Destripador: "Molinete" — dos tajos cruzados en X con las dos palas.

Guardia de bate -> carga sobre el hombro derecho -> tajo diagonal con la pala delantera (golpe 1)
-> el remo pasa por arriba del hombro izquierdo -> tajo diagonal inverso con la pala trasera (golpe 2)
-> vuelve a la guardia. Las manos se separan sobre el mango como en un kayak.
36 frames a 30 fps (1,2 s). Uso: python3 tools/blender/anims/AC_RemoMolinete.py [--preview]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import animkit as ak  # noqa: E402

NAME = "Bob_AC_RemoMolinete"
WEAPON = "AC_RemoDestripador"
FRAMES = 36
HITS = (11, 24)
BASE = "Bob_IdleAimBat"
GRIP = "bat"


def _tip(g, d, back=False):
    from mathutils import Vector
    d = Vector(d).normalized()
    return tuple(Vector(g) + d * 45)


# (agarre, punta = hacia la pala delantera, cara del filo; None = la que lleva la trayectoria)
WEAPON_KEYS = {
    1: "guard",
    6: ((-15, 0, 88), _tip((-15, 0, 88), (-0.3, 0.7, 0.65)), None),        # carga sobre el hombro der.
    11: ((0, -27, 66), _tip((0, -27, 66), (0.45, -0.72, -0.52)), None),    # GOLPE 1: pala delantera abajo-izq.
    15: ((10, -19, 60), _tip((10, -19, 60), (0.82, -0.2, -0.53)), None),   # sigue de largo
    19: ((4, -14, 84), _tip((4, -14, 84), (-0.42, -0.3, -0.85)), None),    # vuelta: la pala trasera sube por la izq.
    24: ((-6, -26, 68), _tip((-6, -26, 68), (0.6, 0.55, 0.58)), "back"),   # GOLPE 2: pala trasera abajo-der.
    28: ((-13, -18, 60), _tip((-13, -18, 60), (0.8, 0.22, 0.56)), "back"),
    36: "guard",
}
EASE = {1: "io", 6: "in", 11: "out", 15: "io", 19: "in", 24: "out", 28: "io"}
LEFT = {1: 0.0, 6: 2.0, 11: -10.0, 15: -10.0, 19: 6.0, 24: 18.0, 28: 18.0, 33: 4.0, 36: 0.0}   # cm de la mano izquierda sobre el mango
BODY = {
    1: {},
    6: {"twist": -20, "hips_yaw": -10, "lean": -4, "crouch": -1},
    11: {"twist": 55, "hips_yaw": 30, "lean": 16, "crouch": 5, "shift": (2, -4, 0)},
    15: {"twist": 65, "hips_yaw": 34, "lean": 12, "crouch": 4, "shift": (2, -4, 0)},
    19: {"twist": 35, "hips_yaw": 18, "lean": 2, "crouch": 0},
    24: {"twist": -15, "hips_yaw": -5, "lean": 16, "crouch": 5, "shift": (-1, -4, 0)},
    28: {"twist": -25, "hips_yaw": -10, "lean": 12, "crouch": 4, "shift": (-1, -3, 0)},
    36: {},
}
FEET = {1: {}, 11: {"R": (0, 0, 1, 18)}, 19: {}, 24: {"L": (0, 0, 1, -15)}, 30: {}, 36: {}}

if __name__ == "__main__":
    ak.build(sys.modules[__name__], preview="--preview" in sys.argv)
