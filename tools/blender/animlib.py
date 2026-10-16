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
def load_rig():
    bpy.ops.wm.open_mainfile(filepath=str(RIG_BLEND))
    rig = bpy.data.objects[RIG]
    bpy.context.scene.render.fps = FPS
    for side in ("R", "L"):
        pb = rig.pose.bones
        # brazos en modo IK (el rig viene en FK)
        for bone, fk, ik in ((f"Bip01_{side}_UpperArm", f"CTRL-UpperArmFK.{side}", f"IK-UpperArm.{side}"),
                             (f"Bip01_{side}_Forearm", f"CTRL-ForearmFK.{side}", f"IK-Forearm.{side}")):
            for c in pb[bone].constraints:
                if getattr(c, "subtarget", "") == fk:
                    c.influence = 0.0
                elif getattr(c, "subtarget", "") == ik:
                    c.influence = 1.0
        for c in pb[f"Bip01_{side}_Hand"].constraints:
            c.influence = 1.0 if c.subtarget == f"CTRL-ArmIK.{side}" else 0.0
        for c in pb[f"Bip01_{side}_Forearm"].constraints:
            if c.subtarget.startswith("HLPR-WristTwistFK"):
                c.influence = 0.0
    rig.animation_data_create()
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


class Animator:
    def __init__(self, rig, name, left_hand=18.0, two_hands=True):
        self.rig = rig
        self.pb = rig.pose.bones
        self.left_hand = left_hand          # cm desde el agarre hasta la mano izquierda (sobre el mango)
        self.two_hands = two_hands
        self.action = bpy.data.actions.new(name)
        rig.animation_data.action = self.action
        # relación mano/prop en la pose de reposo del rig = cómo agarra el juego
        pr, hr = rest(rig, "Bip01_Prop1"), rest(rig, "Bip01_R_Hand")
        self.hand_in_prop = pr.inverted() @ hr
        pl, hl = rest(rig, "Bip01_Prop2"), rest(rig, "Bip01_L_Hand")
        self.lhand_in_prop = pl.inverted() @ hl

    def _set(self, bone, m, frame):
        pb = self.pb[bone]
        pb.matrix = m
        bpy.context.view_layer.update()
        pb.keyframe_insert("location", frame=frame)
        pb.keyframe_insert("rotation_quaternion", frame=frame)

    def body(self, frame, hips=0.0, chest=0.0, lean=0.0, crouch=0.0, spine=0.0):
        """Giro de cadera/torso (grados, + = hacia la izquierda del personaje), inclinación hacia
        adelante (lean, grados) y agacharse (crouch, cm)."""
        for bone, yaw, pitch in (("CTRL-Pelvis", hips, 0.0), ("CTRL-Spine1", spine, lean * .4),
                                 ("CTRL-Chest", chest, lean * .6)):
            pb = self.pb[bone]
            pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = (Quaternion((0, 0, 1), math.radians(yaw)) @
                                      Quaternion((1, 0, 0), math.radians(-pitch)))
            pb.keyframe_insert("rotation_quaternion", frame=frame)
        root = self.pb["CTRL-Pelvis"]
        root.location = (0, 0, 0)
        root.location.z = -crouch  # en espacio del hueso; suficiente para un leve agache
        root.keyframe_insert("location", frame=frame)

    def weapon(self, frame, grip, along, head):
        """Keyframe del arma y de las dos manos."""
        m = frame_from(grip, along, head)
        self._set("CTRL-Prop.R", m, frame)
        self._set("CTRL-ArmIK.R", m @ self.hand_in_prop, frame)
        if self.two_hands:
            ml = m @ Matrix.Translation((0, self.left_hand, 0)) @ Matrix.Rotation(math.pi, 4, "Y")
            self._set("CTRL-ArmIK.L", ml @ self.hand_in_prop, frame)

    def finish(self, start, end):
        self.action.frame_range = (start, end)
        self.action.use_frame_range = True
        bpy.context.scene.frame_start, bpy.context.scene.frame_end = start, end
        for fc in _fcurves(self.action):
            for k in fc.keyframe_points:
                k.interpolation = "BEZIER"
        return self.action


def _fcurves(action):
    try:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    yield from bag.fcurves
    except AttributeError:
        yield from action.fcurves


# --------------------------------------------------------------- exportar
def export_glb(rig, action, path):
    """Igual que el exportador del Community Rig (PZ_HumanRig_Export): GLB a 30 fps con
    Dummy01 / Bip01 / Translation_Data y los huesos de deformación horneados."""
    sc = bpy.context.scene
    sc.render.fps = FPS
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


# ------------------------------------------------------------- vista previa
def attach_weapon(rig, weapon_id):
    """Carga el FBX del mod (convención vanilla: metros, largo sobre +Y) y lo cuelga de Bip01_Prop1."""
    fbx = ROOT / "Contents/mods/ArsenalChatarra/42/media/models_X/weapons/ArsenalChatarra" / f"{weapon_id}.fbx"
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    obj = [o for o in bpy.data.objects if o not in before and o.type == "MESH"][0]
    tex = ROOT / f"art/{weapon_id}/{weapon_id}.png"
    m = bpy.data.materials.new(weapon_id)
    m.use_nodes = True
    t = m.node_tree.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(str(tex))
    m.node_tree.links.new(t.outputs["Color"], m.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    obj.data.materials.clear()
    obj.data.materials.append(m)
    obj.matrix_world = Matrix.Identity(4)
    obj.data.transform(Matrix.Scale(100, 4))   # metros del FBX -> centímetros del rig
    obj.parent = rig
    obj.parent_type = "BONE"
    obj.parent_bone = "Bip01_Prop1"
    bone = rig.data.bones["Bip01_Prop1"]
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
