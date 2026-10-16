"""Armas de fuego para Arsenal Táctico (Project Zomboid B42): piezas, materiales y exportación.

Convenciones (verificadas con los modelos vanilla de 42.18 y el código de carga de 42.21):
  * Se modela a la ESCALA DEL JUEGO en metros: X hacia la boca del cañón, Z hacia arriba, Y hacia la
    izquierda; el origen es donde la mano derecha toma la empuñadura (como M16_Rifle / M9_Pistol).
    Referencia vanilla: M16 boca a +0,40, culata a -0,15, riel de mira a z +0,068; M9 boca a +0,144.
  * En el juego los rifles tienen el largo sobre +Y y arriba sobre +Z; las pistolas, arriba sobre -Z
    (models_weapons.txt: Handgun03 scope z -0.046). game_matrix() hace ese pasaje.
  * El juego carga los FBX con MAKE_LEFT_HANDED (espeja Z de los vértices): se exporta S · juego.
  * Los offsets de los attachments van en coordenadas del juego (ya espejadas), como los vanilla.
  * Las partes (miras, linterna) se modelan con la misma convención y el origen en su base de montaje;
    en las pistolas el attachment lleva rotate 180 0 -180 (igual que el "scope" de Handgun03).
"""
import json
import math
import shutil
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

import pzlib as pz

MOD = pz.ROOT / "Contents/mods/ArsenalTactico/42/media"
MODELS = MOD / "models_X/weapons/ArsenalTactico"
TEXTURES = MOD / "textures/weapons/ArsenalTactico"
S = Matrix.Diagonal((1, 1, -1, 1))
ROT_RIFLE = Matrix.Rotation(math.radians(90), 4, "Z")        # X del modelo (boca) -> +Y del juego
FLIP_HANDGUN = Matrix.Rotation(math.pi, 4, "Y")               # arriba -> -Z (convención de pistolas)


def game_matrix(kind):
    return FLIP_HANDGUN @ ROT_RIFLE if kind == "handgun" else ROT_RIFLE


# ------------------------------------------------------------------ materiales
def polymer(name="polimero", color=(0.045, 0.045, 0.05), seed=0.0):
    return pz.mat(name, color, dirt=0.12, rough=0.85, scale=40.0, seed=seed)


def black_metal(name="metal_negro", seed=0.0):
    return pz.mat(name, (0.075, 0.078, 0.085), rust=0.02, dirt=0.10, rough=0.45, scale=30.0, seed=seed)


def fde(name="fde", seed=0.0):
    return pz.mat(name, (0.45, 0.38, 0.27), dirt=0.12, rough=0.8, scale=30.0, seed=seed)


def grey(name="gris", seed=0.0):
    return pz.mat(name, (0.22, 0.23, 0.245), dirt=0.12, rough=0.8, scale=30.0, seed=seed)


def glass(name="vidrio"):
    return pz.mat(name, (0.04, 0.10, 0.16), dirt=0.0, rough=0.15)


def rubber(name="goma"):
    return pz.mat(name, (0.03, 0.03, 0.033), dirt=0.08, rough=0.95)


def brass(name="laton"):
    return pz.mat(name, (0.72, 0.53, 0.18), dirt=0.08, rough=0.4)


def accent(name, color):
    return pz.mat(name, color, dirt=0.05, rough=0.6)


# ------------------------------------------------------------------ piezas
def bx(name, x0, x1, y0, y1, z0, z1, mat, bevel=0.0015):
    """Caja por extremos (metros, coordenadas del modelo)."""
    return pz.box(name, (x1 - x0, y1 - y0, z1 - z0), loc=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
                  mat=mat, bevel=bevel)


def tube(name, x0, x1, r, mat, y=0.0, z=0.0, segs=14, r2=None):
    """Cilindro sobre X (de x0 a x1); r2 = radio en x1 (cono)."""
    return pz.cylinder(name, r, x1 - x0, loc=((x0 + x1) / 2, y, z), rot=(0, 90, 0), mat=mat, segs=segs,
                       r2=r2)


def side(name, pts, thickness, mat, y=0.0, bevel=0.001):
    """Perfil de costado [(x, z), ...] (antihorario) extruido sobre Y."""
    o = pz.extrude(name, pts, thickness, mat=mat, plane="XZ", bevel=bevel)
    o.location.y = y
    return o


def bar(name, p0, p1, thick, mat, width=None):
    """Barra recta entre dos puntos (x, z) del costado, de sección thick x width."""
    p0, p1 = Vector((p0[0], 0, p0[1])), Vector((p1[0], 0, p1[1]))
    d = p1 - p0
    ang = math.degrees(math.atan2(d.z, d.x))
    mid = (p0 + p1) / 2
    return pz.box(name, (d.length, width or thick, thick), loc=tuple(mid), rot=(0, -ang, 0), mat=mat, bevel=0.0008)


def rail(name, x0, x1, z, mat, w=0.021, h=0.006, y=0.0):
    """Riel picatinny: base + dientes cada ~1 cm. z = altura de la base."""
    parts = [bx(f"{name}_base", x0, x1, y - w / 2, y + w / 2, z, z + h * 0.55, mat, bevel=0.0008)]
    n = max(1, int((x1 - x0) / 0.0095))
    for i in range(n):
        xa = x0 + (x1 - x0) * (i + 0.15) / n
        xb = x0 + (x1 - x0) * (i + 0.75) / n
        parts.append(bx(f"{name}_t{i}", xa, xb, y - w / 2 * 0.92, y + w / 2 * 0.92, z + h * 0.5, z + h, mat, bevel=0.0005))
    return parts


def slots(name, x0, x1, z0, z1, y_face, mat, n=4, depth=0.0015):
    """Ranuras M-LOK: rectángulos oscuros apenas hundidos en una cara lateral (y_face con signo)."""
    out = []
    for i in range(n):
        xa = x0 + (x1 - x0) * (i + 0.18) / n
        xb = x0 + (x1 - x0) * (i + 0.82) / n
        y = y_face - math.copysign(depth / 2, y_face)
        out.append(bx(f"{name}{i}", xa, xb, y - depth, y + depth, z0, z1, mat, bevel=0.0))
    return out


def quad_rail(name, x0, x1, zc, r, mat):
    """Guardamanos de riel cuádruple: cuerpo octogonal + rieles arriba, abajo y a los costados."""
    parts = [pz.cylinder(f"{name}_cuerpo", r, x1 - x0, loc=((x0 + x1) / 2, 0, zc), rot=(0, 90, 22.5), mat=mat,
                         segs=8, smooth=False)]
    parts += rail(f"{name}_sup", x0, x1, zc + r * 0.88, mat, w=0.018)
    parts += rail(f"{name}_inf", x0, x1, zc - r * 0.88 - 0.006, mat, w=0.018)
    for sgn, tag in ((1, "izq"), (-1, "der")):
        o = rail(f"{name}_{tag}", x0, x1, 0.0, mat, w=0.018)
        for q in o:
            q.rotation_euler = (math.radians(-90 * sgn), 0, 0)
            q.location = (q.location.x, sgn * (r * 0.88 + q.location.z), zc)
        parts += o
    return parts


def mag_curve(name, x_top0, x_top1, length, curve, mat, thickness=0.021, rake=0.012, n=6):
    """Cargador curvo de costado: arriba entre x_top0 y x_top1 (z=0), baja `length` con curva hacia adelante."""
    front, back = [], []
    for i in range(n + 1):
        t = i / n
        dx = rake * t + curve * t * t
        z = -length * t
        back.append((x_top0 + dx, z))
        front.append((x_top1 + dx, z))
    return side(name, front + list(reversed(back)), thickness, mat)   # extrude recalcula las normales


# ------------------------------------------------------------------ exportación
def export(obj, ID, kind, attachments, tex=None, icon=True, icon_rot=(0, 0, 0)):
    """Exporta al mod: FBX orientado como lo espera el juego, textura e ícono; guarda los attachments
    (coordenadas del juego) en art/<ID>/attachments.json para generar el script de modelos.
    attachments: {nombre: (x, y, z) del modelo}."""
    G = game_matrix(kind)
    out = pz.ART / ID
    data = {"kind": kind, "attachments": {k: [round(c, 4) for c in (G @ Vector(v))] for k, v in attachments.items()}}
    lo = Vector([min(v.co[i] for v in obj.data.vertices) for i in range(3)])
    hi = Vector([max(v.co[i] for v in obj.data.vertices) for i in range(3)])
    data["center"] = [round(c, 4) for c in (G @ ((lo + hi) / 2))]
    data["length"] = round((hi - lo).x, 4)
    (out / "attachments.json").write_text(json.dumps(data, indent=1))

    me = obj.data.copy()
    tmp = bpy.data.objects.new(ID + "_export", me)
    bpy.context.scene.collection.objects.link(tmp)
    M = S @ G
    me.transform(M)
    if M.determinant() < 0:
        me.flip_normals()
    MODELS.mkdir(parents=True, exist_ok=True)
    TEXTURES.mkdir(parents=True, exist_ok=True)
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    tmp.select_set(True)
    bpy.context.view_layer.objects.active = tmp
    bpy.ops.export_scene.fbx(filepath=str(MODELS / f"{ID}.fbx"), use_selection=True, global_scale=0.01,
                             apply_unit_scale=False, apply_scale_options="FBX_SCALE_NONE",
                             bake_space_transform=True, axis_forward="Y", axis_up="Z", object_types={"MESH"},
                             mesh_smooth_type="FACE", path_mode="STRIP")
    bpy.data.objects.remove(tmp, do_unlink=True)
    shutil.copyfile(out / f"{ID}.png", TEXTURES / f"{tex or ID}.png")
    if icon:
        render_icon(obj, ID, icon_rot)
    print(f"[gunkit] {ID} -> {MODELS / (ID + '.fbx')}")


def render_icon(obj, ID, rot=(0, 0, 0)):
    """Ícono de inventario 64 y 32 px: el arma de costado, levemente en 3/4, fondo transparente."""
    from PIL import Image
    sc = bpy.context.scene
    for o in list(sc.objects):
        if o is not obj:
            bpy.data.objects.remove(o, do_unlink=True)
    obj.rotation_euler = [math.radians(a) for a in rot]
    bpy.context.view_layer.update()
    lo = Vector([min((obj.matrix_world @ v.co)[i] for v in obj.data.vertices) for i in range(3)])
    hi = Vector([max((obj.matrix_world @ v.co)[i] for v in obj.data.vertices) for i in range(3)])
    c = (lo + hi) / 2
    size = max(hi.x - lo.x, hi.z - lo.z) * 1.22
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.ortho_scale = size
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    co.location = c + Vector((0.12, -1.0, 0.25)).normalized() * 3
    co.rotation_euler = (c - co.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    for rot_l, en in (((55, 0, 30), 3.0), ((60, 0, 200), 1.2)):
        sun = bpy.data.objects.new("sol", bpy.data.lights.new("sol", "SUN"))
        sun.data.energy = en
        sun.rotation_euler = [math.radians(a) for a in rot_l]
        sc.collection.objects.link(sun)
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7
    sc.world = w
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 24
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = 256
    path = pz.ART / ID / "icon_256.png"
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    im = Image.open(path).convert("RGBA")
    for s in (64, 32):
        im.resize((s, s), Image.LANCZOS).save(pz.ART / ID / f"icon_{s}.png")
    (MOD / "textures").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pz.ART / ID / "icon_32.png", MOD / "textures" / f"Item_{ID}.png")
