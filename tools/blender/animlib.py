"""Animaciones de ataque propias sobre el Community Rig de Project Zomboid (Paddlefruit, GPL-3.0).

Idea: cada animación se define como una TRAYECTORIA DEL ARMA (posición del agarre + dirección del
mango + orientación de la cabeza en cada keyframe) más un poco de cuerpo (cadera/torso). Las manos se
resuelven solas con IK: la derecha va al agarre y la izquierda más arriba sobre el mango.

Espacio de trabajo = espacio local del armature del rig: centímetros, +Z arriba, el personaje mira
hacia -Y y su derecha es -X (hombros a ~72 cm, cadera a ~51 cm).

El rig se descarga aparte (no se versiona): ver RIG_BLEND.
"""
import math
import os
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = Path(__file__).resolve().parents[2]
RIG_BLEND = Path(os.environ.get("PZ_RIG_BLEND", "/home/user/ref/rig/PZ_HumanRigV4.blend"))
RIG = "OBJ-HumanRig (0)"
FPS = 30


# ------------------------------------------------------------------ rig
DEFORM_ARM = {s: (f"Bip01_{s}_UpperArm", f"Bip01_{s}_Forearm", f"Bip01_{s}_Hand") for s in ("R", "L")}


def load_rig():
    """Abre el rig y suelta los huesos de deformación (Bip01_*) de los controles: se animan
    directamente, con IK propio para los brazos. Es lo que exporta el GLB."""
    bpy.ops.wm.open_mainfile(filepath=str(RIG_BLEND))
    rig = bpy.data.objects[RIG]
    bpy.context.scene.render.fps = FPS
    for pb in rig.pose.bones:
        if pb.name.startswith("Bip01"):
            for c in list(pb.constraints):
                pb.constraints.remove(c)
            pb.rotation_mode = "QUATERNION"
            pb.location = (0, 0, 0)
            pb.rotation_quaternion = (1, 0, 0, 0)
    rig.animation_data_create()
    bpy.context.view_layer.update()
    return rig


def rest(rig, name):
    return rig.data.bones[name].matrix_local.copy()


def frame_from(grip, along, head):
    """Matriz (espacio armature) del hueso de prop: Y = a lo largo del mango (hacia la cabeza),
    Z = hacia donde se extiende la cabeza/filo, origen = agarre de la mano derecha."""
    y = Vector(along).normalized()
    z = Vector(head)
    z = (z - y * z.dot(y)).normalized()
    x = y.cross(z)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = Vector(grip)
    return m


# Puños: dirección de los nudillos (X) y del dorso (Z) de cada mano expresadas en el espacio de su
# hueso de prop, medidas en la pose de reposo del rig (iguales a las que usa export_mod para las garras).
KNUCKLES = {"R": (Vector((-0.2164, -0.9706, 0.1055)), Vector((-0.9756, 0.219, 0.0137))),
            "L": (Vector((0.9689, 0.2298, 0.0921)), Vector((-0.2323, 0.9725, 0.0169)))}


def fist(side, pos, punch, dorsal=(0, 0, 1)):
    """Matriz del hueso de prop para que el puño `side` esté en `pos` con los nudillos hacia
    `punch` y el dorso hacia `dorsal` (espacio armature)."""
    kx, kz = KNUCKLES[side]
    d = Vector(punch).normalized()
    u = Vector(dorsal)
    u = (u - d * u.dot(d)).normalized()
    W = Matrix((d, u.cross(d), u)).transposed()
    kz = (kz - kx * kz.dot(kx)).normalized()
    K = Matrix((kx, kz.cross(kx), kz)).transposed()
    m = (W @ K.transposed()).to_4x4()
    m.translation = Vector(pos)
    return m


def _basis(d, pole):
    y = d.normalized()
    z = (pole - y * pole.dot(y)).normalized()
    return Matrix((y.cross(z), y, z)).transposed()


def _about(head, rot):
    return Matrix.Translation(head) @ rot.to_4x4() @ Matrix.Translation(-head)


class Animator:
    def __init__(self, rig, name, left_hand=18.0, two_hands=True):
        self.rig = rig
        self.pb = rig.pose.bones
        self.left_hand = left_hand          # cm desde el agarre hasta la mano izquierda (sobre el mango)
        self.two_hands = two_hands
        self.action = bpy.data.actions.new(name)
        rig.animation_data.action = self.action
        # relación mano/prop de la pose de reposo = cómo agarra el juego
        self.hand_in_prop = {s: rest(rig, p).inverted() @ rest(rig, f"Bip01_{s}_Hand")
                             for s, p in (("R", "Bip01_Prop1"), ("L", "Bip01_Prop2"))}
        self._pose = {}

    # -------------------------------------------------------------- internos
    def _put(self, bone, m):
        self.pb[bone].matrix = m
        bpy.context.view_layer.update()
        self._pose[bone] = m

    def _key(self, frame):
        for bone in self._pose:
            pb = self.pb[bone]
            pb.keyframe_insert("location", frame=frame)
            pb.keyframe_insert("rotation_quaternion", frame=frame)
        self._pose = {}

    def _reset(self):
        for pb in self.pb:
            if pb.name.startswith("Bip01"):
                pb.location = (0, 0, 0)
                pb.rotation_quaternion = (1, 0, 0, 0)
        bpy.context.view_layer.update()

    def _arm(self, side, hand_m):
        """IK de dos huesos: brazo y antebrazo apuntan a la muñeca, la mano queda en hand_m."""
        up, fo, ha = DEFORM_ARM[side]
        s = 1 if side == "L" else -1
        pole = Vector((s * 0.35, 0.5, -1.0)).normalized()   # codos hacia abajo y atrás
        S = self.pb[up].matrix.translation.copy()
        T = hand_m.translation.copy()
        r_up, r_fo, r_ha = (rest(self.rig, b) for b in (up, fo, ha))
        a = (r_fo.translation - r_up.translation).length
        b = (r_ha.translation - r_fo.translation).length
        d = max(min((T - S).length, a + b - 0.01), abs(a - b) + 0.01)
        u = (T - S).normalized()
        x = (a * a + d * d - b * b) / (2 * d)
        h = math.sqrt(max(a * a - x * x, 0))
        p = (pole - u * pole.dot(u)).normalized()
        E = S + u * x + p * h
        T = S + u * d
        for bone, head, tip, r, r_next in ((up, S, E, r_up, r_fo), (fo, E, T, r_fo, r_ha)):
            rot = _basis(tip - head, pole) @ _basis(r_next.translation - r.translation, pole).transposed()
            m = rot.to_4x4() @ r
            m.translation = head
            self._put(bone, m)
        m = hand_m.copy()
        m.translation = T
        self._put(ha, m)

    # -------------------------------------------------------------- API
    def body(self, frame, hips=0.0, chest=0.0, lean=0.0, crouch=0.0, spine=0.0):
        """Giro de cadera/torso (grados, + = hacia la izquierda del personaje), inclinación hacia
        adelante (lean, grados) y agacharse (crouch, cm). Se aplica antes de las manos."""
        self._reset()
        pel = rest(self.rig, "Bip01_Pelvis")
        m = Matrix.Translation((0, 0, -crouch)) @ _about(pel.translation, Matrix.Rotation(math.radians(hips), 3, "Z")) @ pel
        self._put("Bip01_Pelvis", m)
        for bone, k in (("Bip01_Spine", .4), ("Bip01_Spine1", .6)):
            cur = self.pb[bone].matrix.copy()
            rot = Matrix.Rotation(math.radians((chest - hips) * k + spine * k), 3, "Z") @ \
                Matrix.Rotation(math.radians(lean * k), 3, "X")
            self._put(bone, _about(cur.translation, rot) @ cur)
        self._body_frame = frame

    def weapon(self, frame, grip, along, head, left=None):
        """Keyframe del arma (hueso Bip01_Prop1) y de las dos manos sobre el mango.
        left: cm de la mano izquierda sobre el mango para este keyframe (negativo = detrás de la derecha)."""
        m = frame_from(grip, along, head)
        self._put("Bip01_Prop1", m)
        self._arm("R", m @ self.hand_in_prop["R"])
        if self.two_hands:
            ml = m @ Matrix.Translation((0, self.left_hand if left is None else left, 0)) @ Matrix.Rotation(math.pi, 4, "Y")
            self._arm("L", ml @ self.hand_in_prop["R"] @ Matrix.Rotation(math.pi, 4, "Z"))
        self._key(frame)

    def props(self, frame, right, left):
        """Keyframe de dos props independientes (p.ej. guantes): right/left = matriz del hueso de
        prop (Bip01_Prop1 / Bip01_Prop2) en espacio armature; cada mano lo sostiene como en reposo."""
        self._put("Bip01_Prop1", right)
        self._put("Bip01_Prop2", left)
        self._arm("R", right @ self.hand_in_prop["R"])
        self._arm("L", left @ self.hand_in_prop["L"])
        self._key(frame)

    def finish(self, start, end):
        self.action.frame_range = (start, end)
        self.action.use_frame_range = True
        bpy.context.scene.frame_start, bpy.context.scene.frame_end = start, end
        return self.action


# ------------------------------------------------------- animaciones vanilla
# Las .X del juego están en convención DirectX (Y arriba, mano izquierda). Pasaje al rig:
#   rig = F · X · F   con F = intercambiar Y y Z (en el mundo y en los ejes de cada hueso) y m -> cm.
# Medido contra la pose de enlace de la malla vanilla (SkinWeights de los .X): con F a ambos lados
# los 28 huesos de la piel coinciden con el reposo del rig (< 1° y < 1,6 cm). Con esto el bate de
# Bob_AttackBat01_Hit golpea hacia adelante y los pies miran al frente.
# Las mallas del juego (armas) están en ejes X del prop: en Blender van con F (MESH_TO_RIG).
X_TO_RIG = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
X_LOCAL = X_TO_RIG
MESH_TO_RIG = X_TO_RIG


def x_globals(anim, tick):
    import xanim
    out = {}
    for b, m in xanim.globals_at(anim, tick).items():
        m = m.copy()
        m.translation = m.translation * 100
        out[b] = X_TO_RIG @ m @ X_LOCAL
    return out


def x_frames(anim):
    """Cantidad de frames a 30 fps de una animación .X (frame 1 = tick 0)."""
    import xanim
    return int(round(xanim.duration(anim) / anim["ticks"] * FPS)) + 1


def x_pose(anim, frame):
    """Matrices (espacio armature del rig) de todos los huesos Bip01 en el frame (30 fps, desde 1)."""
    tick = (frame - 1) / FPS * anim["ticks"]
    return x_globals(anim, tick)


def load_x(path):
    import xanim
    return xanim.parse(str(path))


# --------------------------------------------------------------- exportar
def export_glb(rig, action, path, fps=FPS):
    """Igual que el exportador del Community Rig (PZ_HumanRig_Export): GLB con Dummy01 / Bip01 /
    Translation_Data y los huesos de deformación horneados. fps = keys por segundo de la acción
    (el juego toma los tiempos en segundos: 60 keys/s no cambia la duración)."""
    sc = bpy.context.scene
    sc.render.fps = fps
    dummy = rig.parent
    td = bpy.data.objects["OBJ-TranslationData (0)"]
    mesh = bpy.data.objects["OBJ-MaleBody (0)"]
    names = {dummy: dummy.name, rig: rig.name, td: td.name}
    dummy.name, rig.name, td.name = "Dummy01", "Bip01", "Translation_Data"
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in (dummy, rig, mesh, td):
        o.hide_set(False)
        o.hide_viewport = False
        o.select_set(True)
    bpy.context.view_layer.objects.active = rig
    td.animation_data_create()
    start, end = int(action.frame_range[0]), int(action.frame_range[1])
    tracks = []
    for o in (rig, td):
        o.animation_data.action = action
        tr = o.animation_data.nla_tracks.new()
        tr.name = action.name
        st = tr.strips.new(action.name, start, action)
        st.frame_end = end
        tracks.append((o, tr))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(path), use_selection=True, export_hierarchy_flatten_objs=True,
                              export_bake_animation=True, export_materials="NONE", export_morph=False,
                              export_def_bones=True, export_animation_mode="NLA_TRACKS")
    for o, tr in tracks:
        o.animation_data.nla_tracks.remove(tr)
    for o, n in names.items():
        o.name = n
    print(f"[animlib] {path}")


def fix_glb_hemispheres(path):
    """El exportador glTF vuelve a muestrear la pose y puede invertir el signo de algún cuaternión
    entre keys. q y -q son la misma rotación, pero interpolar entre ellos da la vuelta larga:
    se reescribe cada key de rotación en el hemisferio de la anterior."""
    import json
    import struct
    d = bytearray(Path(path).read_bytes())
    n = struct.unpack_from("<I", d, 12)[0]
    j = json.loads(bytes(d[20:20 + n]))
    base = 20 + n + 8
    fixed = 0
    for an in j.get("animations", []):
        for c in an["channels"]:
            if c["target"]["path"] != "rotation":
                continue
            a = j["accessors"][an["samplers"][c["sampler"]]["output"]]
            v = j["bufferViews"][a["bufferView"]]
            off = base + v.get("byteOffset", 0) + a.get("byteOffset", 0)
            stride = v.get("byteStride", 16)
            prev = None
            for i in range(a["count"]):
                q = list(struct.unpack_from("<4f", d, off + stride * i))
                if prev is not None and sum(x * y for x, y in zip(q, prev)) < 0:
                    q = [-x for x in q]
                    struct.pack_into("<4f", d, off + stride * i, *q)
                    fixed += 1
                prev = q
    Path(path).write_bytes(bytes(d))
    return fixed


# ------------------------------------------------------------- vista previa
def attach_weapon(rig, weapon_id, bone="Bip01_Prop1", fbx_id=None, tex_id=None):
    """Carga el FBX del mod (convención vanilla: metros, largo sobre +Y) y lo cuelga de Bip01_Prop1."""
    fbx = ROOT / "Contents/mods/ArsenalChatarra/42/media/models_X/weapons/ArsenalChatarra" / f"{fbx_id or weapon_id}.fbx"
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    obj = [o for o in bpy.data.objects if o not in before and o.type == "MESH"][0]
    tex = ROOT / f"art/{tex_id or weapon_id}/{tex_id or weapon_id}.png"
    m = bpy.data.materials.new(weapon_id)
    m.use_nodes = True
    t = m.node_tree.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(str(tex))
    m.node_tree.links.new(t.outputs["Color"], m.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    obj.data.materials.clear()
    obj.data.materials.append(m)
    obj.matrix_world = Matrix.Identity(4)
    obj.data.transform(Matrix.Scale(100, 4))   # metros del FBX -> centímetros del rig
    obj.data.transform(MESH_TO_RIG)              # ejes del prop del juego -> ejes del hueso en Blender
    obj.data.flip_normals()
    obj.parent = rig
    obj.parent_type = "BONE"
    obj.parent_bone = bone
    bone = rig.data.bones[bone]
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = (0, -bone.length, 0)       # el hijo de hueso arranca en la cola: volver a la cabeza
    return obj


def render_preview(rig, frames, out_png, gif=None, size=360):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 8
    sc.cycles.device = "CPU"
    sc.render.resolution_x = sc.render.resolution_y = size
    sc.render.film_transparent = False
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (.42, .45, .40, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.6
    sc.world = w
    for o in bpy.data.objects:
        if o.type == "MESH" and ("Female" in o.name or "Skeleton" in o.name or "Dress" in o.name or o.name.startswith("WGT")):
            o.hide_render = True
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.ortho_scale = 2.0
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    el, az = math.radians(30), math.radians(-60)
    target = Vector((0, 0, .5))
    co.location = target + Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))) * 10
    co.rotation_euler = (target - co.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    sun = bpy.data.objects.new("sol", bpy.data.lights.new("sol", "SUN"))
    sun.data.energy = 3
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    sc.collection.objects.link(sun)
    from PIL import Image
    imgs = []
    tmp = Path(out_png).parent / "_frames"
    tmp.mkdir(parents=True, exist_ok=True)
    for f in frames:
        sc.frame_set(f)
        sc.render.filepath = str(tmp / f"f{f:03d}.png")
        bpy.ops.render.render(write_still=True)
        imgs.append(Image.open(sc.render.filepath).convert("RGB"))
    cols = min(len(imgs), 6)
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * size, rows * size), (20, 20, 20))
    for i, im in enumerate(imgs):
        sheet.paste(im, ((i % cols) * size, (i // cols) * size))
    sheet.save(out_png)
    if gif:
        imgs[0].save(gif, save_all=True, append_images=imgs[1:], duration=int(1000 / FPS * (frames[1] - frames[0])), loop=0)
    print(f"[animlib] preview {out_png}")
