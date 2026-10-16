"""Verificador de los scripts del mod antes de subir cambios.

Uso: python tools/check_scripts.py [ArsenalChatarra|ArsenalTactico]   (sale con código 1 si hay errores;
sin argumento revisa todos los mods)

Reproduce cómo los lee Project Zomboid:
  * Los comentarios de bloque se ANIDAN: una barra-asterisco dentro de un comentario abre otro nivel
    y deja comentado el resto del archivo sin ningún error en el log.
  * Llaves balanceadas por archivo.
Y valida referencias dentro del mod:
  * cada item ArsenalChatarra.X usado en recetas/Lua existe;
  * WeaponSprite / StaticModel / WorldStaticModel apuntan a un "model" definido;
  * mesh -> models_X/<ruta>.fbx, texture -> textures/<ruta>.png, Icon -> textures/Item_<Icon>.png existen;
  * booleanos en minúscula (como vanilla), JSON de traducción válido, sin BOM ni caracteres no ASCII en .txt.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# mod: (módulo de los ítems, prefijo de los modelos propios)
MODS = {"ArsenalChatarra": ("ArsenalChatarra", "AC_"), "ArsenalTactico": ("Base", "AT_")}
MOD = MEDIA = MODULE = PREFIX = None

errors, warnings = [], []


def err(where, msg):
    errors.append(f"ERROR {where}: {msg}")


def warn(where, msg):
    warnings.append(f"WARN  {where}: {msg}")


def strip_comments(text, where):
    """Quita comentarios con anidamiento como el juego. Reporta niveles abiertos al final."""
    out, depth, i, line = [], 0, 0, 1
    while i < len(text):
        two = text[i:i + 2]
        if two == "/*":
            depth += 1
            if depth > 1:
                err(f"{where}:{line}", "barra-asterisco dentro de un comentario (el juego anida comentarios)")
            i += 2
            continue
        if two == "*/" and depth:
            depth -= 1
            i += 2
            continue
        if two == "//" and not depth:
            j = text.find("\n", i)
            i = len(text) if j < 0 else j
            continue
        ch = text[i]
        if ch == "\n":
            line += 1
        if not depth or ch == "\n":
            out.append(ch)
        i += 1
    if depth:
        err(where, f"{depth} comentario(s) sin cerrar: el resto del archivo queda comentado")
    return "".join(out)


def blocks(text, kind):
    """Devuelve {nombre: cuerpo} de bloques 'kind Nombre { ... }' (con llaves anidadas)."""
    found = {}
    for m in re.finditer(rf"\b{kind}\s+(\w+)\s*\{{", text):
        depth, j = 1, m.end()
        while j < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        found[m.group(1)] = text[m.end():j - 1]
    return found


def prop(body, key):
    m = re.search(rf"^\s*{key}\s*=\s*([^,\n]+),", body, re.M | re.I)
    return m.group(1).strip() if m else None


def main():
    items, models, recipes = {}, {}, {}
    for path in sorted((MEDIA / "scripts").glob("*.txt")):
        where = path.relative_to(ROOT)
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            err(where, "empieza con BOM UTF-8")
        try:
            raw.decode("ascii")
        except UnicodeDecodeError:
            warn(where, "tiene caracteres no ASCII")
        text = strip_comments(raw.decode("utf-8", "replace"), where)
        if text.count("{") != text.count("}"):
            err(where, f"llaves desbalanceadas ({text.count('{')} abren, {text.count('}')} cierran)")
        for n, line in enumerate(text.splitlines(), 1):
            if re.search(r"=\s*(TRUE|FALSE)\s*,", line):
                warn(f"{where}:{n}", "booleano en mayúsculas; vanilla usa true/false")
        items.update(blocks(text, "item"))
        models.update(blocks(text, "model"))
        recipes.update(blocks(text, "craftRecipe"))

    for name, body in items.items():
        for key in ("WeaponSprite", "StaticModel", "WorldStaticModel"):
            ref = prop(body, key)
            if ref and ref.startswith(PREFIX) and ref not in models:
                err(f"item {name}", f"{key} = {ref} no tiene bloque model")
        icon = prop(body, "Icon")
        if icon and not (MEDIA / "textures" / f"Item_{icon}.png").exists():
            err(f"item {name}", f"falta textures/Item_{icon}.png")
    for name, body in models.items():
        mesh, tex = prop(body, "mesh"), prop(body, "texture")
        if mesh and not (MEDIA / "models_X" / f"{mesh}.fbx").exists():
            err(f"model {name}", f"falta models_X/{mesh}.fbx")
        if tex and not (MEDIA / "textures" / f"{tex}.png").exists():
            err(f"model {name}", f"falta textures/{tex}.png")

    # armas de fuego: cargadores, partes y attachments
    for name, body in items.items():
        mag = prop(body, "MagazineType")
        if mag and mag.startswith(f"Base.{PREFIX}") and mag[5:] not in items:
            err(f"item {name}", f"MagazineType = {mag} no existe")
        gun = prop(body, "GunType")
        if gun and gun.startswith(f"Base.{PREFIX}") and gun[5:] not in items:
            err(f"item {name}", f"GunType = {gun} no existe")
        mount = prop(body, "MountOn")
        for g in (mount.split(";") if mount else []):
            if g.startswith(f"Base.{PREFIX}") and g[5:] not in items:
                err(f"item {name}", f"MountOn incluye {g}, que no existe")
        for m in re.finditer(r"^\s*ModelWeaponPart\s*=\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*,", body, re.M):
            part, model, att = m.group(1), m.group(2), m.group(3)
            short = part.split(".")[-1]
            if short.startswith(PREFIX):
                if short not in items:
                    err(f"item {name}", f"ModelWeaponPart: la parte {part} no existe")
                elif f"Base.{name}" not in (prop(items[short], "MountOn") or "").split(";"):
                    err(f"item {name}", f"ModelWeaponPart: {part} no se puede montar (falta en su MountOn)")
                if model not in models:
                    err(f"item {name}", f"ModelWeaponPart: el modelo {model} no existe")
            sprite = prop(body, "WeaponSprite")
            if sprite in models and not re.search(rf"\battachment\s+{att}\b", models[sprite]):
                err(f"item {name}", f"ModelWeaponPart: el modelo {sprite} no tiene attachment {att}")

    used = set()
    for name, body in recipes.items():
        used |= {(f"recipe {name}", i) for i in re.findall(rf"{MODULE}\.(\w+)", body)}
    for path in MEDIA.rglob("*.lua"):
        used |= {(str(path.relative_to(ROOT)), i) for i in re.findall(rf"{MODULE}\.({PREFIX}\w+)", path.read_text())}
    for where, ident in sorted(used):
        if ident not in items:
            err(where, f"{MODULE}.{ident} no existe como item (el mundo no carga si es salida de receta)")

    for path in (MEDIA / "lua" / "shared" / "Translate").rglob("*.json"):
        where = path.relative_to(ROOT)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            err(where, f"JSON inválido: {e}")
            continue
        if path.name == "ItemName.json":
            missing = {f"{MODULE}.{i}" for i in items if i.startswith(PREFIX)} - set(data)
            if missing:
                warn(where, f"sin traducción: {sorted(missing)}")
        if path.name == "Recipes.json":
            missing = set(recipes) - set(data)
            if missing:
                warn(where, f"recetas sin traducción: {sorted(missing)}")

    for line in errors + warnings:
        print(line)
    print(f"[{MOD.parent.name}] {len(items)} items, {len(models)} modelos, {len(recipes)} recetas -> "
          f"{len(errors)} error(es), {len(warnings)} aviso(s)")
    n = len(errors)
    errors.clear()
    warnings.clear()
    return 1 if n else 0


def run(name):
    global MOD, MEDIA, MODULE, PREFIX
    MOD = ROOT / "Contents" / "mods" / name / "42"
    MEDIA = MOD / "media"
    MODULE, PREFIX = MODS[name]
    return main()


if __name__ == "__main__":
    names = sys.argv[1:] or [n for n in MODS if (ROOT / "Contents" / "mods" / n).exists()]
    sys.exit(max(run(n) for n in names))
