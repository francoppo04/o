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
# hacia el dorso de la mano y el pulgar del modelo (-Y) hacia el pulgar. Datos medidos en las
# animaciones vanilla del juego instalado (tools/inspect_hand_prop.py, 42.21), en ejes del prop:
#   derecha (Prop1): todas las de una mano / cuchillo (quieto, caminar, apuntar, golpes):
#     muñeca (-1.7, 2.3, 7.2) cm, nudillos (-0.04, 0.12, -0.99), dorso (0.97, -0.25, -0.07)
#   izquierda (Prop2): la máscara "holdingbagleft" (Bob_Idle_Bag, Walk_Bag, IdleAim_Bag, Run_Bag):
#     muñeca (-0.2, 1.3, 8.1) cm, nudillos (0.17, 0.02, -0.98), dorso (-0.98, -0.01, -0.17)
# El juego espeja Z de los vértices del FBX al cargarlo (MAKE_LEFT_HANDED): se exporta S · destino.
# (Las demás armas no se tocan: el usuario las validó en el juego tal como están.)
FBX_Z_MIRROR = Matrix.Diagonal((1, 1, -1, 1))
HAND_DATA = {
    "AC_GarrasCarnicero": ("R", (-1.7, 2.3, 7.2), (-0.04, 0.12, -0.99), (0.97, -0.25, -0.07)),
    "AC_GarrasCarniceroL": ("L", (-0.2, 1.3, 8.1), (0.17, 0.02, -0.98), (-0.98, -0.01, -0.17)),
}
HAND_LENGTH = 8.4    # cm de la muñeca a la base de los dedos (rig)


def glove_axis(side, wrist, knuckles, dorsal):
    """Matriz modelo -> ejes del prop del juego (columnas = destino de X, Y, Z del modelo) y el centro
    del puño (m). El pulgar sale de: derecha dorso = nudillos x pulgar; izquierda al revés."""
    k = Vector(knuckles).normalized()
    d = Vector(dorsal)
    d = (d - k * d.dot(k)).normalized()
    thumb = d.cross(k) if side == "R" else (-d).cross(k)
    m = Matrix((k, -thumb, d)).transposed().to_4x4()         # el pulgar del modelo está en -Y
    center = (Vector(wrist) + k * (HAND_LENGTH * 0.55) - d * 1.5) / 100
    return m, center


AXIS, FIST_CENTER = {}, {}
for _name, (_side, _w, _k, _d) in HAND_DATA.items():
    _m, _c = glove_axis(_side, _w, _k, _d)
    AXIS[_name] = FBX_Z_MIRROR @ _m
    FIST_CENTER[_name] = tuple(FBX_Z_MIRROR.to_3x3() @ _c)
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
