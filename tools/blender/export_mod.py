"""Copia los modelos terminados de art/<ID>/ al mod y deja un .blend listo para abrir.

Uso: python tools/blender/export_mod.py AC_Hachamazo [AC_Otro ...]

Por cada arma:
  * art/<ID>/<ID>.blend            modelo + textura empaquetada (doble clic en Blender)
  * 42/media/models_X/weapons/ArsenalChatarra/<ID>.fbx   FBX con la convención vanilla (ver abajo)
  * 42/media/textures/weapons/ArsenalChatarra/<ID>.png   textura del modelo
  * 42/media/textures/Item_<ID>.png                      ícono 32x32 renderizado desde el modelo
"""
import math
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "art"
MOD = ROOT / "Contents" / "mods" / "ArsenalChatarra" / "42" / "media"
MODELS = MOD / "models_X" / "weapons" / "ArsenalChatarra"
TEXTURES = MOD / "textures" / "weapons" / "ArsenalChatarra"

# Convención medida en los modelos vanilla (42.21, tools/inspect_vanilla_models.py):
#   bate 0,49 m, mazo 0,69 m, hacha 0,58 m, pala 0,65 m; largo sobre +Y, cabeza ensanchada sobre Z,
#   origen (agarre de la mano derecha) a 2-5 cm del extremo del mango, en metros y sin transformaciones.
# El juego lee los vértices crudos del archivo e ignora la rotación/escala de nodo que agrega Blender,
# así que se hornea todo en los vértices y se exporta sin conversión de ejes.
# Largo final (m) de cada arma, proporcional a su referencia vanilla:
TARGET_LENGTH = {
    "AC_BateErizo": 0.55,       # bate vanilla 0.49 + púas
    "AC_Hachamazo": 0.69,       # mazo vanilla
    "AC_PareDefinitivo": 0.85,  # más largo que el mazo: poste + contrapeso
    "AC_LaDesafinada": 0.70,
    "AC_GarrasCarnicero": 0.38,   # una mano, tipo cuchillo
    "AC_RemoDestripador": 1.10,
    "AC_TridenteCarnicero": 1.20, # lanza: agarre a ~30% del largo
    "AC_PalaTiburon": 0.75,       # pala vanilla 0.65
    "AC_SartenInfierno": 0.45,    # una mano
    "AC_KatanaBallesta": 0.80,
    "AC_LanzaTijera": 1.15,       # lanza
    "AC_GuadanaGolf": 0.75,
}


# Orientación especial: por defecto el largo (X de modelado) va a +Y, como un mango.
# Las garras se llevan puestas: X de modelado (cuchillos) debe ir hacia los nudillos y Z (cuchillos
# arriba) hacia el dorso de la mano. Matrices medidas en el Community Rig en pose de reposo
# (dirección del antebrazo y dorso de la mano expresados en el espacio de Bip01_Prop1 / Bip01_Prop2).
AXIS = {
    "AC_GarrasCarnicero": Matrix(((-0.2164, 0.0364, -0.9756), (-0.9706, 0.0999, 0.219),
                                  (0.1055, 0.9943, 0.0137))).to_4x4(),
    "AC_GarrasCarniceroL": Matrix(((0.9689, 0.0856, -0.2323), (0.2298, 0.0377, 0.9725),
                                   (0.0921, -0.9956, 0.0169))).to_4x4(),
}
# variantes que reutilizan el modelo de otra arma
SOURCE = {"AC_GarrasCarniceroL": "AC_GarrasCarnicero"}
TARGET_LENGTH["AC_GarrasCarniceroL"] = 0.38


def export(name):
    base = SOURCE.get(name, name)
    src = ART / base
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(src / f"{base}.fbx"))
    obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    obj.name = name
    # material con la textura (el FBX solo guarda el nombre del archivo)
    img = bpy.data.images.load(str(src / f"{base}.png"))
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
    if base == name:
        bpy.ops.wm.save_as_mainfile(filepath=str(src / f"{name}.blend"), compress=True)

    # art/ está en convención de modelado (largo sobre +X): rotar 90° en Z (X->Y) y escalar
    length = obj.dimensions.x
    k = TARGET_LENGTH[name] / length
    obj.data.transform(AXIS.get(name, Matrix.Rotation(math.radians(90), 4, "Z")) @ Matrix.Scale(k, 4))
    obj.matrix_world = Matrix.Identity(4)
    for ax in "xyz":
        lo = min(getattr(v.co, ax) for v in obj.data.vertices)
        hi = max(getattr(v.co, ax) for v in obj.data.vertices)
        print(f"[export_mod] {name}: {ax.upper()} {lo:+.3f}..{hi:+.3f}")

    MODELS.mkdir(parents=True, exist_ok=True)
    TEXTURES.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(MODELS / f"{name}.fbx"), use_selection=True, global_scale=0.01,
                             apply_unit_scale=False, apply_scale_options="FBX_SCALE_NONE", bake_space_transform=True,
                             axis_forward="Y", axis_up="Z", object_types={"MESH"}, mesh_smooth_type="FACE",
                             path_mode="STRIP")
    shutil.copyfile(src / f"{base}.png", TEXTURES / f"{base}.png")
    shutil.copyfile(src / "icon_32.png", MOD / "textures" / f"Item_{base}.png")
    print(f"[export_mod] {name} -> mod")


if __name__ == "__main__":
    for n in sys.argv[1:]:
        export(n)
