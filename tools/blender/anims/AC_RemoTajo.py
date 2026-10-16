"""Remo Destripador: "Tajo de remo" — un tajo diagonal con la pala delantera, agarre de kayak.

Cuerpo y timing salen del golpe de bate vanilla (Bob_AttackBat01_Hit: piernas plantadas, giro de
cadera y torso, impacto en m_TimePc 0.25); el plano del golpe se inclina para que el tajo baje de
arriba-derecha a abajo-izquierda, la mano izquierda va fija a 14 cm sobre el mango (agarre de kayak)
y la pala delantera toca al zombi en el frame de impacto. La pala trasera queda por fuera del hombro.
31 frames a 30 fps (1 s). Uso:
  python3 tools/blender/anims/AC_RemoTajo.py [--preview]     # hornea y exporta el GLB
  python3 tools/blender/validate_anim.py AC_RemoTajo [--glb]  # valida
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import animkit as ak  # noqa: E402

NAME = "Bob_AC_RemoTajo"
WEAPON = "AC_RemoDestripador"
FRAMES = 31
HITS = (10,)                      # m_TimePc = (10-1)/30 = 0.30 (vanilla: 0.25 bate, 0.32 golpe pesado por arriba)
BASE = "Bob_AttackBat01_Hit"
GRIP = "bat"                      # guardia y agarre de Bob_IdleAimBat
# el golpe vanilla barre por delante entre sus frames 8 y 12: el frame de base que cae en el impacto
# (None) lo elige animkit = el de máximo acercamiento al objetivo (queda ~10,4: casi sin re-temporizar,
# así las velocidades son las vanilla)
# la carga vanilla (frames 1-5) se acorta un poco y el barrido rápido (5-10) se estira: con las dos
# manos fijas al remo el antebrazo izquierdo no puede seguir la velocidad vanilla del bate
WARP_KEYS = [(1, 1), (4, 5), (10, None), (31, 31)]
WARP_SEARCH = (8, 12)             # solo el tramo en que el barrido se mueve (después hay una pausa)
BASE_WEAPON = True                # el arma sigue al prop del golpe vanilla, modificado:
TILT = {1: 0.0, 4: 15.0, 10: 15.0, 14: 0.0, 31: 0.0}    # grados: el barrido horizontal pasa a diagonal
TILT_AXIS = (0, 1, 0)
TILT_PIVOT = (0, -3, 74)          # entre los hombros
# en el impacto la pala delantera tiene que entrar por el hombro-cuello (no por arriba de la cabeza):
# se cabecea el remo alrededor del agarre, así además la pala trasera sube y se aleja del muslo
PITCH = {1: 0.0, 3: 0.0, 10: 20.0, 13: 20.0, 22: 0.0, 31: 0.0}
# manos 3 u hacia la izquierda en el impacto: la pala trasera pasa por fuera del torso. TILT, PITCH y
# GRIP_OFFSET salen de una búsqueda en grilla (margen de la pala trasera con torso/cabeza/piernas,
# alcance del brazo y contacto en la franja hombro-cuello); ver docs/animacion-investigacion.md
GRIP_OFFSET = {1: (0, 0, 0), 5: (0, 0, 0), 10: (3, 0, 0), 13: (3, 0, 0), 20: (0, 0, 0), 31: (0, 0, 0)}
# agarre de kayak: la izquierda se acomoda durante la mezcla de entrada (0,15 s) y de salida (0,25 s)
LEFT = {1: 0.0, 4.5: -6.0, 24: -6.0, 31: 0.0}
KEYS_PER_FRAME = 4                # 120 keys/s: entre keys la interpolación lineal no separa las manos del mango
BODY = {1: {}, 10: {"lean": 6, "crouch": 2}, 19: {}, 31: {}}
# zombi a 72 u (~1,44 m: el remo golpea entre MinRange 0,61 y MaxRange 1,6; 1 u ≈ 2 cm porque el
# personaje mide ~90 u) con torso de ~16 cm de radio real y de 0 a 92 u de alto (como el jugador).
# El tajo entra entre el hombro y el cuello (hit_z): la cabeza del jugador está a ~80 u, los hombros a ~72
TARGET = {"center": (0, -72), "radius": 8.0, "z": (0, 92), "hit_z": (66, 82)}
STRIKE = (38, 62)                 # pala delantera (cm sobre el mango, ejes del prop en Blender)

if __name__ == "__main__":
    ak.build(sys.modules[__name__], preview="--preview" in sys.argv)
    ak.write_animset(sys.modules[__name__], ak.al.ROOT / "Contents/mods/ArsenalChatarra/42/media/AnimSets/player/melee/2handed/AC_RemoTajo.xml")
