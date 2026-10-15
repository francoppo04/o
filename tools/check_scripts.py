"""Verificador de los scripts del mod antes de subir cambios.

Uso: python tools/check_scripts.py   (sale con código 1 si hay errores)

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
MOD = ROOT / "Contents" / "mods" / "ArsenalChatarra" / "42"
MEDIA = MOD / "media"
MODULE = "ArsenalChatarra"

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
            if ref and ref.startswith("AC_") and ref not in models:
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

    used = set()
    for name, body in recipes.items():
        used |= {(f"recipe {name}", i) for i in re.findall(rf"{MODULE}\.(\w+)", body)}
    for path in MEDIA.rglob("*.lua"):
        used |= {(str(path.relative_to(ROOT)), i) for i in re.findall(rf"{MODULE}\.(\w+)", path.read_text())}
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
            missing = {f"{MODULE}.{i}" for i in items} - set(data)
            if missing:
                warn(where, f"sin traducción: {sorted(missing)}")
        if path.name == "Recipes.json":
            missing = set(recipes) - set(data)
            if missing:
                warn(where, f"recetas sin traducción: {sorted(missing)}")

    for line in errors + warnings:
        print(line)
    print(f"{len(items)} items, {len(models)} modelos, {len(recipes)} recetas -> "
          f"{len(errors)} error(es), {len(warnings)} aviso(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
