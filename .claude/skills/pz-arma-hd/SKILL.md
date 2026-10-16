---
name: pz-arma-hd
description: Crear o corregir el modelo 3D de un arma de fuego del mod Arsenal Táctico (Project Zomboid B42) con calidad real, usando la canalización HD (hd.py, hd_specs.py, hd_fix/, siluetas/), y verificarlo antes de subirlo. Usar para cualquier arma nueva, cambio de forma, de medidas o de textura en tools/blender/guns/.
---

# Armas HD (PZ B42): checklist

Una arma no está terminada sin cuatro cosas:
- el IoU de la silueta;
- la lámina de volumen revisada;
- las manos verificadas sobre el FBX exportado;
- la escala de juego.

La M4 (`tools/blender/guns/AT_M4.py`) es el arma de referencia, hecha a mano. Las demás salen de fichas.

## 1. Referencia y medidas (sin tocar el modelo)
- **Imagen de costado.** Foto o lámina. Las fotos del usuario NO van al repo; solo van la silueta calcada (JSON) y las medidas.
- **Escala.**
  - Foto: el paso del riel Picatinny (10,01 mm), medido por autocorrelación (fotos del usuario: 0,802 mm/px).
  - Lámina: el largo total del arma real más parecida, sacado de la ficha del fabricante.
  - Siempre una segunda opinión con medidas publicadas de armas existentes (≥ 2 fuentes). Se anota en `referencias/HD/medidas.md` (o en `referencias/<ID>/medidas.md`).
  - Ojo con lo que mide cada dato publicado: el Glock 34 tiene 207 mm de corredera y 222 mm de largo total.
- **Si falta un dato, se le pide al usuario.** No se inventan proporciones.
- **Tamaño en el juego:** `juego = K · real + offset`. Fusiles: K = 0,628 y offset (0,006, −0,002). Pistolas: K = 0,898 y offset (0, 0). No se cambian: son los ya probados en el juego.

## 2. Silueta (`tools/blender/guns/siluetas/<ID>.json`)
| Caso | Cómo se calca |
|---|---|
| Foto con fondo claro | `python3 tools/trace_photo.py foto salida.json X0 Y0 X1 Y1 --mask` (GrabCut) |
| Dibujo | `python3 tools/trace_drawing.py ...` (contorno oscuro y relleno desde el borde; las sombras quedan afuera) |
| Fondo difícil (madera oscura) | GrabCut arrancando desde el modelo. En la ficha va `sil_cut=False, fill=False`: la silueta solo mide, y cada pieza la usa con `{"sil": True}` |

Revisar a ojo:
- Los huecos interiores (guardamonte, culatas esqueleto, aro de palanca) tienen que estar abiertos. Si el calcado los rellena, van en `holes` de la ficha.
- Las piezas finas (postes, diagonales) que el calcado perdió se agregan al JSON.
- Las sombras y la mesa no son el arma.
- Los accesorios del mod (miras, linternas) van en `exclude`.

## 3. Ficha (`tools/blender/guns/hd_fix/<ID>.py`)
- Para arrancar: `python3 tools/blender/guns/hd_dump.py <ID>`. Copia la ficha convertida; desde ahí manda el archivo.
- Formato: `build_parts`, `solid` y `plan_fill` en `hd.py`. Coordenadas en píxeles de la referencia; anchos en mm reales.

Piezas:
- **`("s", nombre, región, ancho_mm, material, opciones)`**: perfil de costado ∩ sección real (dos vistas), con bisel y normales ponderadas.
  - Opciones: `holes`, `round`, `bevel`/`segs`, `ct`/`cb`, `y` (piezas laterales), `cut`, `grow`, `sil`.
- **`lathe`**: caños y supresores. Con `fit_lathes`, el radio y el centro se ajustan a la silueta.
- **`rail`**: Picatinny, con un array al paso real.
- **`pin`, `cyl`, `vcyl`, `box`**.
- **`mag`**: cuerpo y base del cargador.
- **`decals`**: ranuras, estrías, picado, textos. Los textos van espejados en el lado izquierdo para que se lean.

Reglas:
- **Cada componente visible es su propia pieza, en su lugar.** Los polígonos se leen sobre la grilla (`hd_grid.py`, con `--zona` para ampliar). Nunca a ojo.
- **Guardamonte cerrado** si el dibujo lo muestra cerrado. **Gatillo** dentro del guardamonte. **Nada flotante**, roto ni serruchado. Las piezas que se tocan se solapan un poco.
- **Anchos reales:**

  | Tipo | Pieza | Ancho (mm) |
  |---|---|---|
  | Pistola | corredera | 23-26 |
  | Pistola | armazón | 25-28 |
  | Pistola | empuñadura | 28-32 |
  | Pistola | guardamonte | 9-12 |
  | Pistola | gatillo | 5-6 |
  | Fusil | cajón | 24-32 |
  | Fusil | guardamanos | 40-55 |
  | Fusil | culata | 30-45 |
  | Fusil | cargador 5,56 | 20-26 |
  | Fusil | cargador 7,62 | 25-30 |
- **Relleno automático:** suma lo que falta a la pieza vecina. Sirve para retoques, no para tapar polígonos malos. Cuando las piezas cubren el dibujo, va `"fill": False`.
- **Presupuesto:** pistolas ≤ 4500 triángulos; fusiles ≤ 13000. Textura de 512 px (provisoria, hasta medir el estándar vanilla).

## 4. Iterar
- `python3 tools/blender/guns/hd_preview.py <ID> --ref-dir <dir de imágenes>` (unos 15 s). Escribe:
  - `art/<ID>/prev_silueta.png`: verde = coincide, rojo = falta, azul = sobra, gris = excluido;
  - `art/<ID>/prev_volumen.png`: costado, arriba y 3/4.
- Mirar las dos imágenes contra la referencia. Corregir y repetir.

## 5. Construir y exportar
- `python3 tools/blender/guns/hd.py <ID> --ref-dir <dir>`. Hace todo esto:
  - dibuja las calcomanías;
  - hornea color, AO, bordes y cavidades, con desgaste en las aristas;
  - exporta el FBX con normales personalizadas;
  - genera el ícono y `art/<ID>/attachments.json`.
- Láminas que deja: `art/<ID>/verif_silueta.png` y `verif_volumen.png`.

## 6. Verificar (sin esto no está terminada)
| Prueba | Umbral |
|---|---|
| Silueta | IoU ≥ 0,90 (objetivo 0,92) |
| Volumen | Revisar costado, frente, arriba y 3/4: nada flotante, abierto, serruchado ni plano donde el dibujo tiene volumen |
| Manos | `python3 tools/blender/guns/verif_juego.py <ID>` sobre el FBX del mod. La derecha (rojo) va en la empuñadura. La muñeca izquierda (verde/amarillo, animaciones vanilla de fusil) va sobre el guardamanos |
| Escala de juego | `python3 tools/blender/guns/verif_juego.py --escala`: la M4 ocupa ~36 px con el personaje de ~125 px |

## 7. Al mod
1. `python3 tools/build_arsenal_tactico.py`
2. `python3 tools/check_scripts.py`: 0 errores.
3. Commit y push.
   - No van al repo: fotos ni archivos de juego vanilla.
   - Ya están en `.gitignore`: `verif_*`, `prev_*` y los mapas `_ao`/`_edge`/`_cav`.
