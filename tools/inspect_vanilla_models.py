"""Extrae de la instalación de Project Zomboid cómo están armados los modelos vanilla de armas,
para copiar su convención (eje, punto de agarre, escala) en los modelos del mod.

Uso (en la PC con el juego; mejor con Blender para poder leer .fbx):
    blender -b --python tools/inspect_vanilla_models.py -- "C:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid"
Sin Blender (solo lee modelos .X de texto y los scripts):
    python tools/inspect_vanilla_models.py "C:/.../ProjectZomboid"

Imprime, por cada arma de referencia:
  * el bloque "model ..." del script vanilla (mesh, texture, scale, attachments)
  * del archivo de malla: eje más largo, rango en cada eje (dónde está el origen = agarre) y escala
"""
import re
import sys
from pathlib import Path

WEAPONS = ["BaseballBat", "SledgeHammer", "Sledgehammer", "Axe", "WoodAxe", "Shovel",
           "SpearCrafted", "SpearKnife", "Pan", "Katana", "Golfclub", "HuntingKnife"]


def args():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    if not a:
        sys.exit("Falta la ruta de instalación de Project Zomboid")
    return Path(a[0])


def model_blocks(media, names):
    found = {}
    for txt in (media / "scripts").rglob("*.txt"):
        text = txt.read_text(encoding="utf-8", errors="replace")
        for name in names:
            for m in re.finditer(rf"\bmodel\s+{name}\s*\{{", text):
                depth, j = 1, m.end()
                while j < len(text) and depth:
                    depth += {"{": 1, "}": -1}.get(text[j], 0)
                    j += 1
                found.setdefault(name, []).append((txt.relative_to(media), text[m.start():j]))
    return found


def bounds_text_x(path):
    """Lee vértices de un .X de texto (primer bloque Mesh) y matrices de frame."""
    text = path.read_text(errors="replace")
    mats = re.findall(r"FrameTransformMatrix\s*\{([^}]*)\}", text)
    m = re.search(r"\bMesh\b[^{]*\{\s*(\d+)\s*;", text)
    if not m:
        return None, mats
    n = int(m.group(1))
    nums = re.findall(r"(-?\d+\.?\d*(?:[eE][-+]?\d+)?)\s*;\s*(-?\d+\.?\d*(?:[eE][-+]?\d+)?)\s*;\s*(-?\d+\.?\d*(?:[eE][-+]?\d+)?)\s*;",
                      text[m.end():])
    verts = [tuple(map(float, v)) for v in nums[:n]]
    return verts, mats


def bounds_fbx(path):
    import bpy  # noqa: F401  (solo dentro de Blender)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path))
    out = []
    for o in bpy.context.scene.objects:
        if o.type == "MESH":
            raw = [tuple(v.co) for v in o.data.vertices]
            out.append((o.name, raw, tuple(round(s, 4) for s in o.scale), tuple(round(r, 3) for r in o.rotation_euler)))
    return out


def report(label, verts):
    xs, ys, zs = zip(*verts)
    rng = {"X": (min(xs), max(xs)), "Y": (min(ys), max(ys)), "Z": (min(zs), max(zs))}
    longest = max(rng, key=lambda k: rng[k][1] - rng[k][0])
    print(f"    {label}: {len(verts)} vertices, eje mas largo = {longest}")
    for k, (lo, hi) in rng.items():
        print(f"      {k}: {lo:+.4f} .. {hi:+.4f}  (largo {hi - lo:.4f})")


def main():
    root = args()
    media = root / "media"
    blocks = model_blocks(media, WEAPONS)
    for name in WEAPONS:
        if name not in blocks:
            continue
        for rel, block in blocks[name]:
            print(f"\n=== model {name}  ({rel}) ===")
            print(block)
            mesh = re.search(r"mesh\s*=\s*([^,\n]+)", block)
            if not mesh:
                continue
            base = mesh.group(1).strip().replace("\\", "/")
            files = [p for p in (media / "models_X").rglob("*")
                     if p.is_file() and p.with_suffix("").as_posix().lower().endswith(base.lower())]
            for f in files:
                print(f"  malla: {f.relative_to(media)}")
                if f.suffix.lower() == ".fbx":
                    try:
                        for oname, verts, scale, rot in bounds_fbx(f):
                            print(f"    objeto {oname}: escala {scale} rotacion {rot}")
                            report("vertices (espacio local)", verts)
                    except ImportError:
                        print("    (.fbx: correr con Blender para leerlo)")
                elif f.suffix.lower() == ".x":
                    verts, mats = bounds_text_x(f)
                    for mt in mats[:3]:
                        print(f"    FrameTransformMatrix: {' '.join(mt.split())[:200]}")
                    if verts:
                        report("vertices", verts)
                    else:
                        print("    (.X binario o sin Mesh legible)")


if __name__ == "__main__":
    main()
