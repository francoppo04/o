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
from mathutils import Matrix, Vector

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
    "AC_RemoDestripador": 0.90,   # 1,10 se veía muy largo en el juego
    "AC_TridenteCarnicero": 1.20, # lanza: agarre a ~30% del largo
    "AC_PalaTiburon": 0.75,       # pala vanilla 0.65
    "AC_SartenInfierno": 0.45,    # una mano
    "AC_KatanaBallesta": 0.80,
    "AC_LanzaTijera": 1.15,       # lanza
    "AC_GuadanaGolf": 0.75,
}


# Orientación especial: por defecto el largo (X de modelado) va a +Y, como un mango.
# Las garras se llevan puestas: X de modelado (cuchillos) va hacia los nudillos, Z (cuchillos arriba)
# hacia el dorso de la mano y el pulgar del modelo (-Y) hacia el pulgar. Ejes medidos en la mano de
# las animaciones vanilla de una mano (cuchillo/puño, tools/blender/animkit.py: Body.fist_axes), que
# es como el juego pone Bip01_Prop1/Prop2 respecto de cada mano. Columnas = destino de X, Y, Z.
# El juego espeja Z de los vértices del FBX al cargarlo (MAKE_LEFT_HANDED): se exporta S · destino.
# (Las demás armas no se tocan: el usuario las validó en el juego tal como están.)
FBX_Z_MIRROR = Matrix.Diagonal((1, 1, -1, 1))
AXIS = {
    "AC_GarrasCarnicero": Matrix(((-0.0435, 0.1217, -0.9916), (-0.258, -0.9603, -0.1066),
                                  (0.9652, -0.2512, -0.0731))).transposed().to_4x4(),
    "AC_GarrasCarniceroL": Matrix(((0.9921, 0.0823, -0.0946), (0.0793, -0.9962, -0.0359),
                                   (-0.0972, 0.0282, -0.9949))).transposed().to_4x4(),
}
# centro del puño (m, espacio del prop) donde va el centro del guante, y centro del guante en art/
FIST_CENTER = {"AC_GarrasCarnicero": (-0.0337, 0.0328, 0.0273), "AC_GarrasCarniceroL": (-0.0302, 0.0124, 0.0424)}
for _k in list(AXIS):
    AXIS[_k] = FBX_Z_MIRROR @ AXIS[_k]
    FIST_CENTER[_k] = (FIST_CENTER[_k][0], FIST_CENTER[_k][1], -FIST_CENTER[_k][2])
MODEL_CENTER = {"AC_GarrasCarnicero": (0.03, 0.0, 0.01)}
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
    axis = AXIS.get(name, Matrix.Rotation(math.radians(90), 4, "Z"))
    if base in MODEL_CENTER:   # centrar el guante en el puño
        obj.data.transform(Matrix.Translation(-Vector(MODEL_CENTER[base])))
    obj.data.transform(axis @ Matrix.Scale(k, 4))
    if name in FIST_CENTER:
        obj.data.transform(Matrix.Translation(FIST_CENTER[name]))
    if axis.determinant() < 0:   # espejado: dar vuelta las caras para que las normales miren afuera
        obj.data.flip_normals()
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
