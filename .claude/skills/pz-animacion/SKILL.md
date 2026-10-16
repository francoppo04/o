---
name: pz-animacion
description: Crear o corregir una animación de ataque del mod Arsenal de Chatarra (Project Zomboid B42) con Blender por Python, y validarla frame por frame antes de subirla. Usar para cualquier animación nueva o cambio en tools/blender/anims/, animkit.py, animlib.py o media/AnimSets.
---

# Animaciones de ataque (PZ B42) — checklist

Fuente de verdad: los archivos del juego y el código descompilado (docs/animacion-investigacion.md).
Nada se da por terminado sin la salida del validador y la hoja de contacto revisada.

## Pipeline
1. Script en `tools/blender/anims/AC_<Nombre>.py` (ver `AC_RemoTajo.py` como modelo):
   - `BASE`: un ataque vanilla (.X) aporta piernas, peso y la guardia de inicio y fin.
   - `GRIP`: clase de arma (`bat`, `heavy`, `spear`, `1h`, `fists`) → agarre y guardia vanilla.
   - `BASE_WEAPON = True` + `TILT` / `PITCH` / `GRIP_OFFSET`: el arma sigue al prop vanilla, modificado.
   - `HITS`, `TARGET` (con `hit_z`), `STRIKE` (parte que golpea, cm sobre el mango en ejes de Blender).
   - `WARP_KEYS` con `None` en el impacto: animkit elige el frame de base del primer toque.
   - `LEFT`: mano izquierda sobre el mango. Constante fuera de las ventanas de mezcla.
2. `python3 tools/blender/anims/AC_<Nombre>.py --preview`: hornea (120 keys/s), exporta el GLB, arregla
   los hemisferios de los cuaterniones, escribe el `m_TimePc` en el AnimSet y genera la hoja de contacto.
3. `python3 tools/blender/validate_anim.py AC_<Nombre>` y después `... --glb`. Las dos tienen que dar `RESULTADO: PASA`.
4. Copiar `art/anims/Bob_AC_<Nombre>.glb` a `media/anims_X/Bob/`.
5. Mirar la hoja `art/anims/Bob_AC_<Nombre>_sheet.png` (frente, costado, arriba) y listar lo que esté mal.
6. `python3 tools/check_scripts.py` antes de commitear.

## Criterios del validador (1 u del rig ≈ 2 cm reales; el personaje mide ~90 u)
| Criterio | Umbral |
|---|---|
| Contacto | En el `m_TimePc` toca la PARTE QUE GOLPEA, desde afuera, \|d\| ≤ 0,5 u y dentro de `hit_z`. El arma entera no atraviesa el objetivo antes del impacto. |
| Cuerpo | Arma a ≥ 1,5 u de la malla deformada (sin manos ni dedos; el mango dentro del puño excluido). |
| Agarre | Mano derecha ≤ 0,5 u de su punto. La izquierda sobre el eje (≤ 0,5 u), sin girar más de 10° y sin deslizarse fuera de las ventanas de mezcla. |
| Rotación | ≤ 20° por 1/4 de frame (el golpe vanilla llega a 16°). En el GLB, sin cambios de hemisferio. |
| Pies | Sin patinar (≤ 0,5 u) ni atravesar el piso. |
| Articulaciones | Rodillas 0-140° y hacia la punta del pie; codos ≤ 155°. |
| Timing | Impactos = `m_TimePc` del AnimSet; frames 1 y último iguales a la guardia vanilla (≤ 1 u, ≤ 3°). |

El validador muestrea a mitad de camino entre keys: subir las keys por frame no esconde errores.

## Trampas conocidas (cada una ya costó una iteración)
- **Ejes:** rig = F · X · F (F = intercambiar Y y Z, en el mundo y en cada hueso). En Blender el mango del arma va sobre **+Z** del hueso de prop y el filo sobre **+Y**.
- **Huesos sin herencia de rotación:** en el rig, clavículas, muslos y props no heredan la rotación del padre. Girar el cuerpo con `transform_subtree`, nunca rotando solo el padre.
- **Selección de nodo:** el motor elige por `m_ConditionPriority` y después por cantidad de condiciones; `m_Priority` no cuenta. Los nodos propios llevan `m_ConditionPriority 10`.
- **Golpe:** el acierto es geométrico (ángulo + MaxRange en el instante del evento); el contacto visual es aparte. Vanilla usa **un** `AttackCollisionCheck` cerca de 0.25-0.32.
- **Objetivo:** ponerlo dentro del rango del ítem (MinRange-MaxRange en tiles, 1 tile ≈ 50 u). Si el objetivo está más cerca que la parte que golpea, lo toca el mango.
- **Contacto:** medir con el arma entera. Una pala que ya cruzó también "toca" la superficie de atrás.
- **Splines:** para valores que deben mantenerse (agarre, inclinación), usar `Track(..., hold=True)`; Catmull-Rom se pasa de largo.
- **Codo:** el polo sale de la base, filtrado y con giro máximo por key (`ELBOW_MAX_STEP`); si no, se da vuelta.
- **Antebrazo:** la torsión extra respecto de la base va al antebrazo (pronación), no a la muñeca.
- **Armas con dos extremos** (remo, lanzas): lo que queda detrás de las manos apunta al torso en un golpe tipo bate. Buscar la pose de impacto con la búsqueda en grilla (margen, alcance, contacto) antes de iterar a ojo.

## Probar en el juego
1. En el PC: `git pull` en `%USERPROFILE%\Zomboid\Workshop\MisMods`.
2. Lanzar PZ con `-debug`: en Steam, Propiedades → Opciones de lanzamiento.
3. Equipar el arma desde el inventario, atacar a un zombi quieto y sacar capturas a mitad del golpe.
4. Revisar `%USERPROFILE%\Zomboid\console.txt` con el juego cerrado: líneas con `Bob_AC_`, `AnimSet`, `ArsenalChatarra`, `ERROR` o `WARN` cercanas.
5. Si usa la animación vanilla en lugar de la propia, correr en la consola Lua de debug `print(getPlayer():getVariableString("ACWeapon"))`.
