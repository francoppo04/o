"""Remo Destripador: "Molinete" — dos remadas diagonales seguidas.

1) levanta la pala delantera sobre el hombro derecho, 2) remada hacia adelante-derecha con la sierra
delantera (golpe 1), 3) gira el remo sobre las manos, 4) remada hacia adelante-izquierda con la
sierra trasera (golpe 2), 5) vuelve a la guardia. 33 frames a 30 fps (~1,1 s).

Uso: python3 tools/blender/anims/AC_RemoMolinete.py [--preview]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import animlib as al  # noqa: E402

NAME = "Bob_AC_RemoMolinete"
WEAPON = "AC_RemoDestripador"
HITS = (13, 25)   # frames de impacto (para los eventos del AnimSet)

# frame: (agarre cm, dirección del mango hacia la pala delantera, hacia dónde mira la cara de la pala)
KEYS = {
    1:  ((-8, -20, 55), (0.45, -0.35, 0.80), (0, -1, 0)),     # guardia: pala delantera arriba-izquierda
    8:  ((-12, -10, 63), (-0.40, 0.25, 0.90), (0, -1, 0)),    # carga sobre el hombro derecho
    13: ((-10, -30, 52), (-0.35, -0.80, -0.15), (0, 0, 1)),   # GOLPE 1: adelante-derecha
    19: ((-2, -26, 60), (0.30, -0.20, 0.95), (-1, 0, 0)),     # giro: la pala trasera baja
    25: ((5, -28, 52), (-0.40, 0.80, 0.30), (0, 0, 1)),       # GOLPE 2: pala trasera adelante-izquierda
    33: ((-8, -20, 55), (0.45, -0.35, 0.80), (0, -1, 0)),     # vuelve a la guardia
}
BODY = {  # frame: (cadera, torso, inclinación)
    1: (0, 0, 5), 8: (-15, -30, 0), 13: (15, 25, 15), 19: (0, 0, 5), 25: (-15, -25, 15), 33: (0, 0, 5),
}


def build():
    rig = al.load_rig()
    an = al.Animator(rig, NAME, left_hand=20.0)
    for f, (grip, along, head) in KEYS.items():
        an.weapon(f, grip, along, head)
        hips, chest, lean = BODY[f]
        an.body(f, hips=hips, chest=chest, lean=lean)
    return rig, an.finish(1, 33)


if __name__ == "__main__":
    rig, action = build()
    out = al.ROOT / "art" / "anims"
    al.export_glb(rig, action, out / f"{NAME}.glb")
    if "--preview" in sys.argv:
        al.attach_weapon(rig, WEAPON)
        al.render_preview(rig, list(range(1, 34, 2)), out / f"{NAME}_sheet.png", gif=out / f"{NAME}.gif")
