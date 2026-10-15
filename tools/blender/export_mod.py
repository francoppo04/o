"""Copia los modelos terminados de art/<ID>/ al mod y deja un .blend listo para abrir.

Uso: python tools/blender/export_mod.py AC_Hachamazo [AC_Otro ...]

Por cada arma:
  * art/<ID>/<ID>.blend            modelo + textura empaquetada (doble clic en Blender)
  * 42/media/models_X/weapons/ArsenalChatarra/<ID>.fbx   FBX a escala 0.01 (convención de Zomboid)
  * 42/media/textures/weapons/ArsenalChatarra/<ID>.png   textura del modelo
  * 42/media/textures/Item_<ID>.png                      ícono 32x32 renderizado desde el modelo
"""
import shutil
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "art"
MOD = ROOT / "Contents" / "mods" / "ArsenalChatarra" / "42" / "media"
MODELS = MOD / "models_X" / "weapons" / "ArsenalChatarra"
TEXTURES = MOD / "textures" / "weapons" / "ArsenalChatarra"


def export(name):
    src = ART / name
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(src / f"{name}.fbx"))
    obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    obj.name = name
    # material con la textura (el FBX solo guarda el nombre del archivo)
    img = bpy.data.images.load(str(src / f"{name}.png"))
    m = obj.data.materials[0] if obj.data.materials else bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if not obj.data.materials:
        obj.data.materials.append(m)
    img.pack()
    bpy.ops.wm.save_as_mainfile(filepath=str(src / f"{name}.blend"), compress=True)

    MODELS.mkdir(parents=True, exist_ok=True)
    TEXTURES.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(MODELS / f"{name}.fbx"), use_selection=True, global_scale=0.01,
                             axis_forward="-Z", axis_up="Y", object_types={"MESH"}, mesh_smooth_type="FACE",
                             path_mode="STRIP")
    shutil.copyfile(src / f"{name}.png", TEXTURES / f"{name}.png")
    shutil.copyfile(src / "icon_32.png", MOD / "textures" / f"Item_{name}.png")
    print(f"[export_mod] {name} -> mod")


if __name__ == "__main__":
    for n in sys.argv[1:]:
        export(n)
