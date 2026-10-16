# Investigación: animación del Remo Destripador (B42.21)

Alcance: cómo resuelve el juego (B42) las armas largas a dos manos, dónde quedan las manos, cómo se decide
un golpe y cómo se cargan las animaciones. Las fuentes locales tienen prioridad sobre las web.

## 0. Fuentes locales y su versión

| Ruta | Versión | Uso |
|---|---|---|
| `/home/user/ref/pz-42.21-decomp/42.21.0/decompiled` | **B42.21.0** (Java descompilado; **parcial**: 565 clases, faltan `IsoGameCharacter`, `IsoPlayer` y `SwipeStatePlayer`) | motor |
| `/home/user/ref/PZ-42.18/scripts/generated/` (repo mitcaka/PZ-42.18) | **B42.18** (scripts vanilla `generated/items/weapon.txt`, `models_weapons.txt`) | ítems/modelos B42 |
| `/home/user/ref/PZ-Media/media` y `/home/user/ref/Project-Zomboid-Media-Files/media` (mismo repo Niteghxst, commit de mayo de 2024) | **B41** (`Type = Weapon`, sin `ItemType`) | **únicos AnimSets vanilla disponibles → B41, verificar en B42** |
| `/home/user/ref/pz_weapon_check/anims/*.X` | md5 idéntico al de Project-Zomboid-Media-Files (B41) y a `DmitriShlupkin.../PZ_original_for_reference` (mod B42) | .X vanilla, probablemente sin cambios en B42 (no confirmado) |
| `/home/user/ref/CommunityRig.wiki`, `/home/user/ref/ProjectZomboid_CommunityRig` | Rig V4.0.1 (jul. 2026, Blender 5.1+) | export GLB |
| `/home/user/gotmayonase/pz-modding-guide` | B42.16 | guía general |

## 1. Cómo resuelve vanilla las armas largas a dos manos

### 1a. Scripts de ítem (B42.18, `PZ-42.18/scripts/generated/items/weapon.txt`)
**Existe un remo de kayak de doble pala vanilla: `CanoePadelX2`** (y `CanoePadel` de una pala). Es la referencia prioritaria.

| Ítem | SwingAnim | 2H | MinRange | MaxRange | MinAngle | Swingtime | BaseSpeed | WeaponLength | AttachmentType |
|---|---|---|---|---|---|---|---|---|---|
| **CanoePadelX2** | Bat | true | 0.61 | 1.6 | 0.85 | 2.0 | 0.8 | (por defecto 0.4) | Shovel |
| CanoePadel | Bat | true | 0.61 | 1.6 | 0.85 | 2.0 | 0.85 | (por defecto) | Shovel |
| Shovel / Shovel2 | Bat | true | 0.61 | 1.6 | 0.85 | 2.1 | 0.8 | 0.55 | Shovel |
| Rake | Bat | true | 0.61 | 1.6 | 0.85 | 2.0 | 1.2 | 0.68 | — |
| GardenFork | **Spear** | true | 0.61 | 1.37 | 0.8 | 2.0 | 0.9 | — | — |
| Sledgehammer | **Heavy** | true | 0.7 | 1.35 | 0.8 | 2.0 (MinimumSwingtime 4.0) | 0.9 | 0.65 | — |
| SpearCrafted | Spear | true | 0.98 | 1.4 | 0.8 | 2.0 | — | — | — |
| BaseballBat | Bat | true | 0.61 | 1.25 | 0.75 | 3.0 | 1.0 | 0.5 | — |

Todas las armas largas de barrido (pala, rastrillo, escoba, remos, azada) usan `SwingAnim = Bat` + `IdleAnim = Idle_Weapon2`
+ `RunAnim = Run_Weapon2`. Ninguna tiene un AnimSet propio: comparten los nodos 2H "Bat". Valores de `SwingAnim`
aceptados en 42.21: Bat, Handgun, Heavy, Rifle, Shove, Spear, Stab, Stone, Throw (`decompiled/zombie/scripting/objects/SwingAnim.java`).
El remo del mod (`MaxRange 1.6`, `MinAngle 0.7`, `Swingtime 3.5`) es más lento y tiene un cono más ancho que `CanoePadelX2` (2.0 / 0.85).

### 1b. Scripts de modelo (B42.18, `PZ-42.18/scripts/generated/models_weapons.txt`)
| Modelo | `attachment world` | `attachment Bip01_Prop2` |
|---|---|---|
| CanoePadelX2 | offset 0 0.18 -0.0104, rotate 0 -90 0 | offset -0.0103 -0.0124 -0.0023, rotate 0 -78.0 0 |
| CanoePadel | offset 0 0.297 -0.0097, rotate 0 -90 0 | igual que X2 |
| Shovel | offset -0.0009 0.2369 -0.0152, rotate 0 -90 0 | offset 0 0 0, rotate 0 -73.05 0 |
| Rake | offset 0 0.3 0.009, rotate 0 90 0 | offset -0.0036 0 0, rotate -2.0 -73.6 1.3 |
| GardenFork | offset 0 0.26 -0.013, rotate 0 -90 0 | rotate 0 -81.7 0 |
| SpearCrafted | offset -0.01 0.29 0 | rotate 180 -88.8 -178.6 |
| BaseballBat | offset -0.0285 0.2419 0 | offset -0.0067 -0.0091 -0.0022, rotate 0 0 0 |
| SledgeHammer | offset -0.0274 0.297 0 | (no tiene) |

Ninguno de estos define `attachment Bip01_Prop1` (solo 10 modelos de `models_weapons.txt` lo hacen, p. ej. `EngineMaul`
o `ScrapMaul`). Ver la sección 2: **con el arma en la mano principal, `Bip01_Prop2` no se usa.**

### 1c. AnimSets (**B41, verificar en B42**; `PZ-Media/media/AnimSets/player/melee/`)
| Nodo | Clip | Condición | m_Priority | Blend in/out | AttackCollisionCheck (m_TimePc) |
|---|---|---|---|---|---|
| 2handed/2HDefault | Bob_AttackBat01_Hit (+ blend 2D con `_HitB`) | Weapon=2handed, AimFloorAnim=false | 4 | 0.15 / 0.25 | **0.25** (uno solo) |
| 2handed/2HOverhead, 2HUppercut | Bat02_Hit / Bat03_Hit | extiende 2HDefault + attackType | — | heredado | 0.25 (heredado) |
| 2handed/2HOnFloor | Bob_AttackFloorBat | extiende 2HDefault | — | — | 0.35 |
| heavy/HeavyDefault | Bob_Attack2H_Heavy01_Hit | Weapon=heavy | 4 | 0.15 / 0.25 | 0.25 |
| heavy/HeavyOverhead | Bob_Attack2H_Heavy02_Hit | attackType=overhead | — | — | 0.32 |
| 2handed/SpearDefault | Bob_AttackSpear02_Hit | Weapon=spear, AttackType=default | 4 | 0.15 / 0.25 | 0.25 (BlockMovement FALSE en 0.5) |
| 2handed/SpearCharge | Bob_AttackSpear01_CritHit | Weapon=spear, AttackType=charge | 4 | 0.10 / — | 0.2 |

Otros eventos de 2HDefault: SetVariable ZombieHitReaction en 0.1, BlockMovement TRUE en 0.1 y FALSE en End,
AttackAnim TRUE en Start y FALSE en End, `SetMeleeDelay` 12 en End y PlaySwingSound en Start. **Todos los nodos vanilla
tienen un único AttackCollisionCheck**; el del mod tiene dos (0.38 y 0.75).
Duraciones de los .X (4800 ticks/s, `/home/user/ref/pz_weapon_check/anims`): AttackBat01/02_Hit = **1,0 s**,
Attack2H_Heavy01_Hit = 2,5 s e IdleAimBat = 0,67 s. Por lo tanto vanilla Bat impacta a 0,25 s del clip, antes del escalado
por `CombatSpeed`. El GLB del mod dura 1,1 s, con impactos en 0,42 s y 0,83 s.
En 42.21 `m_Value` es válido en `m_Conditions` (se parsea según `m_Type`) y `m_ConditionPriority` desempata la selección
antes que la cantidad de condiciones (`decompiled/.../advancedanimation/AnimCondition.java`, `AnimNode.java:279-292`).
Valor por defecto de `m_maxTorsoTwist`: 15 (`AnimNode.java`).

## 2. Dónde van las manos: ¿animación o motor?

**Confirmado en el descompilado (42.21):**
- **El arma se cuelga de `Bip01_Prop1`.** `ModelManager` agrega el modelo del ítem primario en `"Bip01_Prop1"` y el del
  secundario en `"Bip01_Prop2"` **solo si es otro ítem** (`primaryItem != secondaryItem`). Un arma 2H (el mismo ítem en
  ambas manos) genera **un solo modelo, en Prop1** (`decompiled/zombie/core/skinnedmodel/ModelManager.java:698-708`).
- **El offset que se aplica es el del attachment con el mismo nombre que el hueso.** En `transformToParent`, primero se
  busca el attachment padre (del cuerpo) y después el propio del arma, con id = `parentBoneName` (`"Bip01_Prop1"`), y se
  compone `bone · attachCuerpo · attachArma · meshTransform` (`advancedanimation/AnimatedModel.java:1450-1495`). El cuerpo
  define `attachment Bip01_Prop1` con identidad sobre `bone = Bip01_Prop1` (`PZ-42.18/scripts/generated/models_characters.txt:382`).
  **Por lo tanto, para un arma 2H en la mano principal el `attachment Bip01_Prop2` del modelo no se usa;** solo contaría
  un `attachment Bip01_Prop1`. Si no existe, el origen y los ejes de la malla coinciden con el hueso Prop1.
  La matriz del attachment es `translation(offset) · rotateXYZ(rx,ry,rz)` en grados → radianes, sin invertir
  (`invertAttachmentSelfTransform` es `false` por defecto, `model/ModelInstanceRenderData.java:21,107-113`).
- **No hay IK de manos en el código disponible.** Una búsqueda de `IK`/`HandIK`/`TwoBone`/`inverseKinematic` no da
  resultados. `LeftHandMask`/`RightHandMask` son solo variables de animación para `ReplaceInSecondHand`/`SecondaryAnimMask`
  (`scripting/objects/Item.java:1918-1949`). `AnimationPlayer` aplica twist de torso (máx. 70°) y **re-parenting de huesos**
  (`addBoneReparent`, `AnimationPlayer.java:221,1192-1340`). El hueso reparentado conserva la pose que tenía en cada
  clip, pero sigue al nuevo padre ya mezclado.
- **Jerarquía en los .X vanilla:** `Bip01_Prop1` y `Bip01_Prop2` son **hijos de `Bip01`, no de las manos**
  (`pz_weapon_check/anims/Bob_AttackBat01_Hit.X`, líneas 492/500). En el GLB del mod Prop1 también cuelga de Bip01.
  En consecuencia, la trayectoria del arma la definen las keys de Prop1 y la posición de cada mano la definen las keys
  del brazo. **Que coincidan es trabajo de la animación.**
- **Medición de vanilla** (`python3 -I anim_hands.py`, posición de las muñecas en el marco de Prop1):
  - AttackBat01_Hit, constante durante todo el golpe: R_Hand (-0.022, +0.058, +0.068) y L_Hand entre (+0.04..0.07, -0.00..0.04, -0.02..0.03).
    Ambas manos quedan a menos de 13 cm del origen de Prop1, así que el bate se agarra por la punta con las manos juntas.
  - Attack2H_Heavy01_Hit: R_Hand en Y ≈ +0.25..0.30 y L_Hand en Y ≈ +0.073, o sea ~0,2 m de separación sobre el +Y de Prop1.
  - Prop2 se aleja hasta 0,36 m de la mano izquierda a mitad del golpe Bat02, lo que indica que no se lo trata como mano
    (es irrelevante para un 2H).
- **Third-party, no confirmado en el descompilado:** AnimForge afirma que "the engine reparents the off-hand prop bone
  Bip01_Prop2 onto Bip01_L_Hand for every player (IsoPlayer.onAnimPlayerCreated -> addBoneReparent)"
  (`AnimForge/tools/pz-anim-forge/pzanimforge/x_edit.py:402`). Es Prop2 el que sigue a la mano, no la mano al arma.
  No afecta a un 2H en Prop1.

**Conclusión:** la mano izquierda **la pone la animación**. El motor no la ata al mango.

## 3. Cómo decide el motor si un golpe acierta

Ruta: evento de anim `AttackCollisionCheck` → `CombatManager.attackCollisionCheck` → `calculateHitInfoList` →
`calculateHitListWeapon` (`decompiled/zombie/CombatManager.java:652, 2325, 2027`). El despachador (`SwipeStatePlayer`)
no está en el descompilado parcial. **Es puramente geométrico y no usa ni la malla ni la física del arma:**
- Candidatos: personajes a ≤ 3 tiles (`DistToSquared > 9` descarta), con |ΔZ| < 0.5 y línea de visión libre (`LosUtil.lineClear`).
- Para cada objetivo se toma el punto más cercano entre cabeza (Bip01_Head/HeadNub), pelvis y posición, y el **dot con la
  dirección de mirada** del atacante. Es acertable si `MinAngle ≤ dot ≤ MaxAngle` (MaxAngle 1.0 por defecto; contra un
  objetivo tumbado, MinAngle/1.5) **y** si `owner.isMeleeAttackRange(weapon, target, pos)`, que usa MaxRange/MinRange
  (`CombatManager.java:1581-1655`). `isMeleeAttackRange` está en IsoGameCharacter y no se ve.
- Se ordena, se recorta a `MaxHitcount` (1 si la opción "multiHitZombies" está desactivada) y se aplica el daño
  (`CombatManager.java:2361-2385`).
- `WeaponLength` solo se usa en `DoSwingCollisionBoneCheck`, una línea recta hacia adelante de largo `weaponLength + 0.5`
  contra los huesos de la víctima, **y solo en golpes al suelo** (`isAimAtFloor`), para decidir cabeza o piernas
  (`CombatManager.java:491-515, 800-900`).
- Se dispara el evento Lua `OnWeaponSwingHitPoint` (`CombatManager.java:671`).

**→ El "contacto con el poste" es solo visual.** Mecánicamente importan el momento del evento, la orientación del
personaje (forward), MaxRange/MinAngle y la línea de visión. Con dos AttackCollisionCheck, lo esperable es que se
evalúe y se haga daño dos veces por golpe (no confirmado: no hay guard visible en `CombatManager`).

## 4. Carga de .X / .fbx / .glb en B42

- **Orden de búsqueda** para un nombre sin extensión: `media/anims_X/<n>.fbx` → `.glb` → `.x` → `media/anims/<n>.txt`
  (`model/FileTask_AbstractLoadModel.java:56-120`). Si existen dos formatos con el mismo nombre, gana el .fbx.
- **Todos pasan por Assimp con `MAKE_LEFT_HANDED`.** .X **sin modificadores**. **.fbx y .glb de animación:**
  `animBonesScaleModifier = 0.01` (las posiciones de las keys se interpretan en cm) y `animBonesRotateModifier = -90°
  en X` (`model/FileTask_LoadAnimation.java:43-110`). El modificador se aplica por hueso: `R' = R⁻¹·key·R`, conjugado
  si el padre tiene keys o es la raíz, y solo `key·R` en caso contrario (`model/jassimp/ImportedSkeleton.java:257-330`).
  Los huesos **sin keys** no se ajustan, salvo la raíz, así que conviene **keyear todos los huesos** (bake).
  Nombre del clip: lo que sigue a `|` en el nombre de la acción (`ImportedSkeleton.java:333`).
- **Mallas (no animaciones):** .fbx con escala 0.01 y -90X. **.glb de malla con escala 1 y sin rotación**
  (`model/FileTask_LoadMesh.java:81-140`). Es una asimetría a tener en cuenta.
- El Community Rig exporta a .glb con `export_bake_animation=True`, `export_def_bones=True` y modo NLA_TRACKS, y fuerza 30 fps
  (`ProjectZomboid_CommunityRig/PY-PZ_HumanRig.py:5474-5552`). El rig importa los assets con `global_scale=100`
  (`:2158`), por eso el 0.01 del motor cuadra. Mapea `Bip01_Prop1 → CTRL-Prop.R` y `Bip01_Prop2 → CTRL-Prop.L` (`:5151`).
- Wiki del rig: 30 FPS ("If your animations are animated at framerates lower or higher than 30 FPS, they will play
  slower or faster", `CommunityRig.wiki/Creating-an-animation-for-a-mod.md`). GLB en lugar de FBX solo por tamaño
  (`Exporting-Animations.md`). En Known-Issues: "IK/FK snapping can have slight inconsistencies in rotation and positioning".
  En Future-Work, **"Weapon attachments (held items...)" no está implementado**: el rig no muestra el arma en la mano.
- **Problemas de ejes conocidos (third party):** AnimForge trabaja directo sobre .x "so they load byte-for-byte the way the
  game loads a vanilla clip - no coordinate-convention drift" (README, https://github.com/AlexVDefi/AnimForge).
  Su `prop_fix.py` dice que el exportador glTF de Blender deja **`Bip01_Prop1`/`Prop2` con la orientación de reposo
  girada 90°** respecto de lo que espera PZ. Lo corrigen post-multiplicando -90° en X sobre cada key de rotación del
  hueso prop. Esto está documentado para clips de recarga y **no está verificado para el Community Rig**.
  rcpz-tools replica el "attach" haciendo que el hueso prop del cuerpo reproduzca la transformación absoluta del prop
  del clip en el marco del personaje (`rcpz-tools/web/src/render/anim.ts:144-160`). En `character-core.js:182,242`
  dice que, por defecto, el arma va en Prop1 con identidad.

## 5. Web

| Recurso | Estado |
|---|---|
| pzwiki.net/wiki/Animation, Creating_custom_animations, Importing assets | **no accesible** (DNS ENOTFOUND) |
| github.com/gotmayonase/pz-modding-guide | clon local: solo trae que "Bip01_Prop1 is the right-hand prop bone; Bip01_Prop2 is the left-hand bone" y que FBX es lo seguro para mallas (`visual-assets.md:69,94`). No dice nada de ataques |
| github.com/AlexVDefi/AnimForge | accesible (clonado en el scratchpad). Ver §2 y §4 |
| github.com/AlexVDefi/rcpz-tools | accesible (clonado). Ver §4 |
| steamcommunity.com/...?id=3035712003 (templates B41) | **no accesible** (DNS) |
| docs.blender.org (IK, Child Of, cuaterniones, Euler Filter) | **no accesible** (DNS). Notas de conocimiento general, sin verificar contra el manual: |

- *IK constraint*: lleva el extremo de la cadena (mano) al Target. La Pole Target orienta el codo y `Chain Length = 2` limita la cadena a antebrazo y brazo.
- *Child Of*: hace que un hueso o control siga a otro (p. ej. el IK de la mano izquierda hijo de `CTRL-Prop.R`). Usar "Set Inverse" en el frame de referencia. Se puede animar su influencia.
- Constraints y controles **no se exportan**: hay que **hornear (Bake Action, Visual Keying)** sobre los huesos `Bip01_*`. El exportador del rig ya hace `export_bake_animation`.
- *Cuaterniones vs Euler*: interpolar en cuaterniones evita el gimbal lock en giros grandes. Si se usa Euler, *Euler Filter* (Graph Editor › Channel › Discontinuity (Euler) Filter) corrige los saltos de ±180°.

## 6. Buenas prácticas de ataque (con fuente)

- **El primer y el último frame coinciden con la pose de aim.** En AttackBat01/02_Hit, t=0 y t=4800 dan posiciones de
  manos idénticas y coinciden con `Bob_IdleAimBat` (Prop1 +Y en raíz (0.42,0.57,0.71) en las tres; medido con `anim_hands.py`).
- **Duración e impacto:** Bat dura 1,0 s con impacto al 25 % y Heavy 2,5 s también al 25 % (HeavyOverhead 32 %).
  BlockMovement se activa en 0.1 (§1c).
- **Blend:** in 0.15 / out 0.25 en los nodos de ataque 2H. La salida a idle va por `Bob_AimToIdle_Bat` con blend 0.5 y
  speedScale 1.3 (B41).
- 30 fps (wiki del rig). Keyear todos los huesos (§4). Un solo AttackCollisionCheck por nodo (§1c).

## No confirmado / contradicciones

1. Todos los AnimSets vanilla disponibles localmente son **B41**: los m_TimePc, blends y transiciones de B42 pueden haber cambiado.
2. `SwipeStatePlayer` (el despachador de AttackCollisionCheck) y `IsoGameCharacter.isMeleeAttackRange` faltan en el
   descompilado. No se verificó si dos AttackCollisionCheck en un mismo nodo producen dos golpes. Tampoco cómo
   `CombatSpeed` escala el clip según Swingtime/BaseSpeed.
3. Qué huesos reparentea el motor para el jugador (AnimForge dice Prop2→L_Hand). El mecanismo existe, pero las llamadas están en `IsoPlayer`, ausente.
4. Rotación de 90° de los prop bones en GLB exportados desde Blender (AnimForge): sin verificar con el Community Rig.
5. Contradicción aparente: los modelos vanilla 2H solo definen `attachment Bip01_Prop2`, pero el código usa `Bip01_Prop1`
   para el primario. Según el código, ese attachment Prop2 solo aplica si el ítem va en la mano secundaria. La guía de
   gotmayonase muestra un ejemplo con `attachment Bip01_Prop1`. **Hay que verificarlo in-game** (Debug › Render ›
   primaryHandBone / weaponHitPoint, `ModelSlotDebugRenderData.java:74-78,175`).
6. Que los .X de `pz_weapon_check` sean idénticos en B42 se infiere por el md5 contra la copia de un mod B42; no está confirmado.
