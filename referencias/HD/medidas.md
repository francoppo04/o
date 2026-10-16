# Medidas de las armas HD (todas menos la M4)

La M4 tiene su propia ficha en `referencias/AT_M4/medidas.md`. Acá están las otras 18. Las fichas de modelado
están en `tools/blender/guns/hd_specs.py`.

## Cómo se saca la escala

| Origen de la imagen | Armas | Escala |
|---|---|---|
| Foto del usuario (9.webp) | MCX, AK-101, G-19 | 0,802 mm/px, medida con el paso del riel Picatinny (10,01 mm), igual que la M4 |
| Foto enderezada de la Marlin | Marlin 336 | 876 mm (largo publicado del Marlin 336 "Dark") sobre 1332 px |
| Lámina conceptual (11.webp) | las 14 restantes | largo total del arma real más parecida (tabla de abajo), dividido por el largo en px de la lámina |

Se modela en milímetros reales. Después se exporta con el mismo factor de juego que ya se probó:

- fusiles: K = 0,628 (M4);
- pistolas: K = 0,898 (G-19).

## Armas conceptuales: arma real de referencia

Regla: largo total con la culata extendida, tomado de la ficha del fabricante. Si no hay ficha del fabricante,
se usa el valor en el que coinciden varias fuentes. Revisado el 16/10/2026.

| Arma del mod | Arma real | Largo usado | Fuentes y notas |
|---|---|---|---|
| AT_GXP | Glock 34 | 222 mm | Ficha oficial de Glock: 222 mm de largo total. Ojo: 207 mm es solo la corredera. |
| AT_MD34 | Glock 34 | 222 mm | Igual que la anterior. El compensador de la lámina queda dentro de ese largo. |
| AT_GravRecon | Glock 17 | 202 mm | Ficha oficial de Glock (Gen5). |
| AT_VikorS1 | CZ P-10 F | 203 mm | Varias tiendas coinciden en 150 × 32 × 203 mm. |
| AT_FNPR | FNX-45 Tactical | 218 mm | Ficha oficial de FN America: 8,6". No hay ficha del FNP-45 Tactical; el FNX-45 Tactical tiene el mismo cañón de 5,3". |
| AT_FNSAR | FN P90 | 500 mm | Dato publicado. |
| AT_QDX99 | QCW-05 | 500 mm | Wikipedia e IMFDB. La lámina tiene el cañón corto, sin supresor largo. |
| AT_MX4 | CZ Bren 2, 11" | 807 mm | Gunlex: 577 a 807 mm (culata plegada y extendida). 577 mm coincide con la versión pistola (22,8"). Una tienda dice 35,6", pero no cuadra. |
| AT_AUGA5 | Steyr AUG A3, cañón de 20" | 790 mm | Wikipedia. Otras fuentes dan 800 a 805 mm. |
| AT_AG203 | AK-12 | 935 mm | Rostec (fabricante): 875 a 935 mm según la posición de la culata. Wikipedia: 922 mm. |
| AT_Komodo | SIG MCX Spear 13" | 889 mm | Tiendas: 35". Wikipedia: 36". |
| AT_CycloneAGL | Milkor MGL | 778 mm | Wikipedia, con la culata extendida. |
| AT_RPK101 | RPK-74M | 1060 mm | modernfirearms.net. |
| AT_PSR | VSS Vintorez | 894 mm | Wikipedia y modernfirearms.net. |

Cambios respecto de los valores anteriores:

| Arma | Antes | Ahora | Motivo |
|---|---|---|---|
| GXP | 207 mm | 222 mm | 207 mm era el largo de la corredera |
| MD34 | 210 mm | 222 mm | Mismo motivo que la GXP |
| GravRecon | 200 mm | 202 mm | Ficha oficial del Glock 17 |
| VikorS1 | 190 mm | 203 mm | Ficha del CZ P-10 F |
| FNPR | 205 mm | 218 mm | Ficha del FNX-45 Tactical |
| QDX99 | 560 mm | 500 mm | Se descartó el supresor estimado |
| MX4 | 740 mm | 807 mm | Gunlex, culata extendida |
| Komodo | 900 mm | 889 mm | Largo publicado del MCX Spear 13" |
| AG203 | 940 mm | 935 mm | Rostec |

### Enlaces

- Glock 34 Gen4: https://us.glock.com/en/pistols/g34-gen4 y https://eu.glock.com/en/products/pistols/g34-gen4
- Glock 17 Gen5: https://swisswaffen.com/markt/heldef/glock-17-gen-5/pistol-glock-17-gen5-fs-a7274/m8ujbae0qaop
- CZ P-10 F: https://www.broncos.co.nz/firearms/pistols/centerfire/p/cz-p-10f-9mm-black-polymer-pistol
- FNX-45 Tactical: https://fnamerica.com/?p=8501
- QCW-05: https://en.wikipedia.org/wiki/QCW-05 y https://www.imfdb.org/wiki/QCW-05
- CZ Bren 2, 11": https://swisswaffen.com/markt/gunlex/cz-bren-2-mit-langem-handschutz-11-223-rem/me9bioql5vpe
- Steyr AUG: https://en.wikipedia.org/wiki/Steyr_AUG
- AK-12: https://rostec.ru/en/directions/weapons/products-projects/ak-12-ak-15-ak-19-assault-rifles/ y https://en.wikipedia.org/wiki/AK-12
- SIG MCX Spear: https://rainierarms.com/sig-sauer-mcx-spear-7-62x51-sbr-13 y https://en.wikipedia.org/wiki/SIG_MCX_Spear
- Milkor MGL: https://en.wikipedia.org/wiki/Milkor_MGL
- RPK-74M: https://modernfirearms.net/en/machineguns/russia-machineguns/rpk-74-eng/
- VSS: https://en.wikipedia.org/wiki/AS_Val_and_VSS_Vintorez

## Segunda opinión para las armas de la foto

Largo de cada silueta a 0,802 mm/px, comparado con el dato publicado:

| Arma | Medido en la foto | Publicado | Diferencia |
|---|---|---|---|
| G-19 | 178 mm | 185 mm (Glock 19 Gen5) | −4 % |
| AK-101 | 791 mm | 943 mm extendida, 700 mm plegada | La culata de la foto no es la de fábrica |
| MCX | 683 mm | depende de la variante | — |

El tamaño en el juego no cambia: se usa el K de las armas ya probadas. Estas medidas solo deciden los anchos
y las proporciones.

## Siluetas

- **Fotos:** se calcan con GrabCut (`tools/trace_photo.py`).
- **Marlin:** GrabCut arrancando desde el modelo, porque el fondo de madera oscura confunde al calcado automático.
- **Lámina:** se calca el contorno oscuro del dibujo y se rellena desde el borde (`tools/trace_drawing.py`). Las sombras no tienen contorno y quedan afuera.
- Las zonas con accesorios del mod (miras, linternas) no se cuentan en el IoU.
