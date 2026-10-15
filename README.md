# Mods de Project Zomboid (Build 42)

Este repositorio es una carpeta de Workshop local: se clona dentro de
`%USERPROFILE%\Zomboid\Workshop\` y el juego carga los mods de `Contents/mods/` en la lista de mods.

## Instalación para probar

```
cd %USERPROFILE%\Zomboid\Workshop
git clone https://github.com/francoppo04/o MisMods
cd MisMods
git checkout claude/exciting-curie-1kuso7
```

Para traer cambios nuevos: `git pull` dentro de `MisMods`. Después, en el juego: **Mods**, activar el mod y empezar una partida nueva (los scripts de ítems, recetas y modelos solo se recargan al reiniciar el juego).

## Mods

### Arsenal de Chatarra (`ArsenalChatarra`) — v0.2

Armas combinadas cuerpo a cuerpo al estilo Dead Rising, con modelos 3D propios.

| Arma | ID | Tipo | Daño | Cómo se consigue |
|---|---|---|---|---|
| Hachamazo | `ArsenalChatarra.AC_Hachamazo` | Hacha pesada, 2 manos, tala árboles | 1.8–3.4 | Hacha de bombero + mazo + 2 chatarra (martillo) · Herrería 3 · loot de bomberos/herramientas |
| Bate Erizo | `ArsenalChatarra.AC_BateErizo` | Contundente, 2 manos, hasta 3 zombis | 1.3–2.1 | Bate + 12 clavos + 2 chatarra (martillo) · Carpintería 2 · loot de garajes |
| PARE Definitivo | `ArsenalChatarra.AC_PareDefinitivo` | Contundente muy pesada, derribo casi seguro | 2.4–4.2 | Caño + 6 chatarra + 4 clavos (martillo, sierra) · Herrería 4 · loot de herramientas |
| La Desafinada | `ArsenalChatarra.AC_LaDesafinada` | Hacha, 2 manos; cada swing hace ruido y atrae zombis | 1.5–2.6 | Solo loot (tiendas de música, salas de ensayo) |

## Antes de subir cambios

```
python tools/check_scripts.py
```

Verifica los scripts como los lee el juego (comentarios anidados, llaves, ítems de recetas, modelos y archivos referenciados).

## Estructura

```
workshop.txt, preview.png             metadatos de Workshop
Contents/mods/ArsenalChatarra/42/     el mod
  media/scripts/                      ítems, modelos y recetas
  media/models_X/weapons/ArsenalChatarra/   modelos 3D (.fbx)
  media/textures/                     íconos (Item_*.png) y texturas de modelos
  media/lua/                          loot, sonido de La Desafinada, traducciones (EN/ES)
art/<arma>/                           fuente de cada modelo: .blend (abrir con doble clic), .fbx, textura y renders de revisión (sheet.png)
tools/blender/                        pipeline de modelado (pzlib.py), scripts de cada arma y exportación al mod
tools/concept/                        fichas de concepto de las 12 armas planeadas
```

### Modelos 3D

Para regenerar un modelo después de cambiar su script:

```
python tools/blender/weapons/AC_Hachamazo.py      # modela, hornea textura, exporta y renderiza
python tools/blender/sheet.py AC_Hachamazo        # hoja de revisión art/AC_Hachamazo/sheet.png
python tools/blender/export_mod.py AC_Hachamazo   # copia FBX (escala 0.01), textura e ícono al mod
```

Requiere `pip install bpy` (Blender como módulo de Python).
