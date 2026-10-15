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

Para traer cambios nuevos: `git pull` dentro de `MisMods`. Después, en el juego: **Mods**, activar el mod y empezar una partida nueva (los scripts de ítems y recetas solo se recargan al reiniciar el juego).

## Mods

### Arsenal de Chatarra (`ArsenalChatarra`)

Armas cuerpo a cuerpo hechas por sobrevivientes con chatarra.

| Arma | ID | Tipo | Daño | Receta |
|---|---|---|---|---|
| Machete de Sierra | `ArsenalChatarra.AC_MacheteSierra` | Hoja larga, 2 manos | 2.2–3.2 | Machete + 2 chatarra (martillo, sierra) · Herrería 2 |
| Hacha Remachada | `ArsenalChatarra.AC_HachaRemachada` | Hacha, 2 manos, tala | 1.1–2.5 | Hacha + 2 chatarra + 6 clavos (martillo) · Herrería 2 |
| Mazo de Señal de Pare | `ArsenalChatarra.AC_MazoSenal` | Contundente pesada | 2.2–3.8 | Caño + 4 chatarra + 8 clavos (martillo, sierra) · Herrería 3 |
| Bate Encadenado | `ArsenalChatarra.AC_BateEncadenado` | Contundente, 2 manos | 1.2–1.8 | Bate + 2 chatarra + 6 clavos (martillo) · Carpintería 1 |
| Estoque de Barra | `ArsenalChatarra.AC_EstoqueBarra` | Hoja corta, 1 mano | 0.9–1.5 | 2 chatarra + mango chico + tela (martillo) · Herrería 3 |

También aparecen como loot en garajes, cajas de herramientas, ferreterías y tiendas de camping.

**Estado (v0.1):** íconos propios. Los modelos 3D en mano son los vanilla (machete, hacha, mazo, bate, cuchillo) como placeholder hasta tener modelos propios.

## Estructura

```
workshop.txt, preview.png          metadatos de Workshop
Contents/mods/ArsenalChatarra/42/  el mod (mod.info, media/scripts, media/lua, media/textures)
tools/gen_icons.py                 regenera íconos y posters (python tools/gen_icons.py)
```
