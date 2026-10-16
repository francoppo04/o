# AT_M4: medidas de referencia

Arma de referencia: la M4 de la foto del usuario (cañón corto ~11,5", guardamanos RIS II de 9,55", culata
SOPMOD, empuñadura angulada, cargador STANAG gris). La foto no se sube al repo; solo su silueta calcada
(`tools/blender/guns/siluetas/AT_M4.json`).

## Escala de la foto
- Paso del riel Picatinny medido en la foto (autocorrelación sobre el riel superior del RIS): **12,48 px**.
- Norma MIL-STD-1913: 10,01 mm entre ranuras → **0,802 mm/px**.
- Control: tubo buffer 30,5 mm en la foto vs. 29,2 mm publicado (mil-spec 1,148").

## Medidas (mm)
| Pieza | Foto (0,802 mm/px) | Segunda opinión publicada | Usado |
|---|---|---|---|
| Largo total | 804 | M4A1: 757–838 según culata | foto |
| Guardamanos | 245 | DD RIS II Mk18: 9,55" = 243; M4A1: 12,25" = 311 | foto |
| Del cajón a la boca | 319 | cañón 14,5" daría ~394 → este es ~11,5" | foto |
| Riel | — | paso 10,01, ranura 5,23, profundidad 3,0, ancho 21,2 | norma |
| Tubo buffer Ø | 30,5 | 29,2 (1,148" mil-spec) | publicado |
| Culata SOPMOD | 200 largo | 188 × 61 × 124 (LMT/B5) | foto (largo), publicado (ancho) |
| Empuñadura angulada | 76 × 48 | AFG2: 119 × 49 × 35 ancho | foto (perfil), publicado (ancho) |
| RIS: alto con rieles | 70 | DD RIS II: 57,2 × 56,6 | foto (otro modelo o réplica) |
| Cajón superior: ancho | — | sin dato publicado | 25,4 (est.) |
| Cajón inferior: ancho | — | 37–38 total con controles | 23,6 cuerpo, 29 brocal (est.) |
| Cargador: espesor | — | sin dato confiable | 22,9 (est. 0,9") |
| Empuñadura: ancho | — | sin dato | 28 (est.) |
| Apagallamas | 64 × Ø16,8 | A2: 1,75" de largo (KAK) | foto |

Exportación: modelado en metros reales; al juego con K = 0,628 y el origen de la empuñadura de la M4 ya
probada (mano izquierda de las animaciones vanilla de fusil a ~0,20 m sobre el guardamanos).

## Fuentes
- Wikipedia, M4 carbine; Colt, ficha de la M4; Royal Australian Navy, M4A1.
- Daniel Defense RIS II 12,25" (Primary Arms) y Mk 18 RIS II 9,55" (Brownells).
- Wikipedia, Picatinny rail (MIL-STD-1913 / STANAG 2324).
- Buffer tube mil-spec vs comercial (Brownells y otros).
- LMT SOPMOD / B5 Enhanced SOPMOD (fichas de venta); Magpul AFG2 (Primary Arms).
- KAK Industry A2 birdcage (Brownells).
