"""Animaciones de cuerpo completo sobre el Community Rig, partiendo de los ataques vanilla.

Por qué así (lo que fallaba en la primera versión, animlib.Animator):
  * Solo se movían los brazos: sin piernas, peso ni giro de cadera el golpe se ve "de muñeco".
  * El agarre salía de la pose de reposo del rig, que NO es como el juego pone el arma en la mano.
    Acá el agarre se copia de las animaciones vanilla (mano respecto de Bip01_Prop1/Prop2).
  * Interpolación lineal entre pocas poses: el arma viajaba en línea recta y a velocidad constante.

Cómo se arma una animación (ver anims/*.py):
  1. BASE: un ataque vanilla (.X) re-temporizado (timewarp) aporta piernas, cadera, peso y la pose
     de guardia del juego en el primer y último frame (así la mezcla con el idle es invisible).
  2. CUERPO: capas sumadas encima (giro de cadera, torsión de columna, inclinación, agacharse,
     desplazar la cadera, mover los pies); las piernas se resuelven con IK para que los pies no patinen.
  3. ARMA: trayectoria del agarre y de la punta con splines Catmull-Rom (arcos, no rectas) y la
     orientación de la cabeza del arma; los brazos van por IK con el agarre vanilla.
  4. Cabeza: compensa parte del giro para seguir mirando al objetivo.
Todo se hornea frame a frame (30 fps) y se exporta con animlib.export_glb.

Espacio: armature del rig, cm, +Z arriba, el personaje mira a -Y, su derecha es -X.
"""
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Quaternion, Vector

import animlib as al

VANILLA = Path("/home/user/ref/Project-Zomboid-Media-Files/media/anims_X/Bob")
VANILLA_EXTRA = Path("/home/user/ref/pz_weapon_check/anims")
SURVIVORS = Path("/home/user/ref/PZ-42.18/Mods/FADED/Survivors/common/media/anims_X/Zombie")


def vanilla(name):
    for d in (VANILLA, VANILLA_EXTRA, SURVIVORS):
        for ext in (".X", ".x"):
            if (d / f"{name}{ext}").exists():
                return al.load_x(d / f"{name}{ext}")
    raise FileNotFoundError(name)


# ----------------------------------------------------------- interpolación
def _cr(p0, p1, p2, p3, t):
    """Catmull-Rom uniforme."""
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)


EASE = {
    "lin": lambda t: t,
    "io": lambda t: t * t * (3 - 2 * t),            # suave al salir y al llegar
    "in": lambda t: t * t,                          # arranca lento, llega rápido (golpe)
    "out": lambda t: 1 - (1 - t) * (1 - t),         # sale rápido, frena (recuperación)
    "in3": lambda t: t * t * t,
    "out3": lambda t: 1 - (1 - t) ** 3,
}


class Track:
    """Canal animado: {frame: valor} (float o Vector). Spline Catmull-Rom entre keys, con easing
    opcional por tramo: ease={frame_inicio_del_tramo: 'in'|'out'|'io'|...}."""

    def __init__(self, keys, ease=None, default="io"):
        self.f = sorted(keys)
        self.v = [keys[k] if not isinstance(keys[k], (tuple, list)) else Vector(keys[k]) for k in self.f]
        self.ease = ease or {}
        self.default = default

    def __call__(self, frame):
        f, v = self.f, self.v
        if frame <= f[0]:
            return v[0].copy() if isinstance(v[0], Vector) else v[0]
        if frame >= f[-1]:
            return v[-1].copy() if isinstance(v[-1], Vector) else v[-1]
        i = max(j for j in range(len(f) - 1) if f[j] <= frame)
        t = (frame - f[i]) / (f[i + 1] - f[i])
        t = EASE[self.ease.get(f[i], self.default)](t)
        p0 = v[max(i - 1, 0)]
        p3 = v[min(i + 2, len(v) - 1)]
        return _cr(p0, v[i], v[i + 1], p3, t)


def timewarp(pairs):
    """[(frame_nuevo, frame_base), ...] -> función frame_nuevo -> frame_base (lineal por tramos)."""
    pairs = sorted(pairs)

    def fn(frame):
        if frame <= pairs[0][0]:
            return pairs[0][1]
        for (a, fa), (b, fb) in zip(pairs, pairs[1:]):
            if a <= frame <= b:
                return fa + (fb - fa) * (frame - a) / (b - a)
        return pairs[-1][1]
    return fn


def _about(pivot, rot3):
    return Matrix.Translation(pivot) @ rot3.to_4x4() @ Matrix.Translation(-pivot)


def _rot(axis, deg):
    return Matrix.Rotation(math.radians(deg), 3, axis)


def _basis(d, pole):
    y = d.normalized()
    z = (pole - y * pole.dot(y)).normalized()
    return Matrix((y.cross(z), y, z)).transposed()


def _aim(z_up, y_along):
    """Base ortonormal con Y = y_along y Z lo más cerca posible de z_up."""
    y = Vector(y_along).normalized()
    z = Vector(z_up)
    z = (z - y * z.dot(y)).normalized()
    return Matrix((y.cross(z), y, z)).transposed()


# ------------------------------------------------------------------ cuerpo
# pose de guardia (y agarre) de cada clase de arma: (clip vanilla, frame)
GRIP_REF = {
    "bat": ("Bob_IdleAimBat", 1),
    "heavy": ("Bob_IdleAim2H_Heavy", 1),
    "spear": ("Bob_WalkBwd_AttackSpear01_Hit", 1),
    "1h": ("Bob_WalkBwd_Attack1Hand01_Hit", 1),
    "fists": ("Bob_WalkBwd_AttackKnife01_Hit", 1),
}

SPINE = ("Bip01_Spine", "Bip01_Spine1", "Bip01_Neck")
SPINE_W = (0.30, 0.45, 0.25)


class Body:
    """Hornea una animación de cuerpo completo frame a frame."""

    def __init__(self, rig, name, base, warp=None, grip="bat"):
        self.rig = rig
        self.pb = rig.pose.bones
        self.overreach = 0.0
        self.base = vanilla(base) if isinstance(base, str) else base
        self.warp = warp or (lambda f: f)
        self.action = bpy.data.actions.new(name)
        rig.animation_data.action = self.action
        self.order = sorted((b for b in self.pb if b.name.startswith("Bip01")), key=lambda b: len(b.parent_recursive))
        self.rest = {b.name: al.rest(rig, b.name) for b in self.order}
        # agarre vanilla: matriz de cada mano en el espacio de su prop, tomada de la pose de guardia
        # de cada clase de arma (así el primer y el último frame calzan con el idle del juego)
        clip, fr = GRIP_REF[grip]
        P = al.x_pose(vanilla(clip), fr)
        self.grip_r = P["Bip01_Prop1"].inverted() @ P["Bip01_R_Hand"]
        self.grip_l = P["Bip01_Prop1"].inverted() @ P["Bip01_L_Hand"]
        self.guard = P["Bip01_Prop1"].copy()
        if grip in ("1h", "fists"):   # mano izquierda libre: su relación con Prop2
            self.grip_l = P["Bip01_Prop2"].inverted() @ P["Bip01_L_Hand"]
        # puño en el espacio de cada prop (para los guantes), con los dedos de la pose vanilla
        self.fist_axes = {}
        for side, prop in (("R", "Bip01_Prop1"), ("L", "Bip01_Prop2")):
            inv = P[prop].inverted()
            w = inv @ P[f"Bip01_{side}_Hand"].translation
            f1 = inv @ P[f"Bip01_{side}_Finger1"].translation - w
            f0 = inv @ P[f"Bip01_{side}_Finger0"].translation - w
            k = f1.normalized()
            d = k.cross(f0).normalized() * (1 if side == "R" else -1)
            self.fist_axes[side] = (k, d, w + k * (f1.length * 0.55) - d * 1.5)

    # ---------------------------------------------------------- utilidades
    def _set(self, name, m):
        self.pb[name].matrix = m
        bpy.context.view_layer.update()

    def M(self, name):
        return self.pb[name].matrix.copy()

    def rotate(self, name, rot3, pivot=None):
        """Gira un hueso (y con él sus hijos) en espacio armature alrededor de su cabeza."""
        m = self.M(name)
        self._set(name, _about(pivot if pivot is not None else m.translation, rot3) @ m)

    def two_bone(self, chain, target, pole, end_m=None):
        """IK analítica de dos huesos (brazo o pierna). end_m: matriz final del tercer hueso."""
        up, lo, end = chain
        S = self.M(up).translation
        T = Vector(target)
        r_up, r_lo, r_end = (self.rest[b] for b in chain)
        a = (r_lo.translation - r_up.translation).length
        b = (r_end.translation - r_lo.translation).length
        if (T - S).length > a + b - 0.05:
            over = (T - S).length - (a + b)
            if over > self.overreach:
                self.overreach = over
                self.overreach_who = up.replace("Bip01_", "")
        d = max(min((T - S).length, a + b - 0.05), abs(a - b) + 0.05)
        u = (T - S).normalized()
        x = (a * a + d * d - b * b) / (2 * d)
        h = math.sqrt(max(a * a - x * x, 0))
        p = (pole - u * pole.dot(u))
        p = p.normalized() if p.length > 1e-6 else Vector((0, 0, 1))
        E = S + u * x + p * h
        T = S + u * d
        for bone, head, tip, r, r_next in ((up, S, E, r_up, r_lo), (lo, E, T, r_lo, r_end)):
            cur = self.M(bone)
            # gira el hueso desde su orientación actual para apuntar al siguiente: conserva el giro (roll)
            cur_dir = (self.M(chain[chain.index(bone) + 1]).translation - cur.translation)
            q = cur_dir.rotation_difference(tip - head)
            # corrige el roll para que el plano del codo/rodilla mire al polo
            m = q.to_matrix().to_4x4() @ Matrix.Translation(-cur.translation) @ cur
            m.translation = head
            self._set(bone, m)
        if end_m is not None:
            m = end_m.copy()
            m.translation = T
            self._set(end, m)
        return T

    # ---------------------------------------------------------- capas
    def base_pose(self, frame):
        P = al.x_pose(self.base, self.warp(frame))
        for b in self.order:
            if b.name in P:
                self._set(b.name, P[b.name])
        return P

    def layer(self, hips_yaw=0.0, twist=0.0, lean=0.0, side=0.0, shift=(0, 0, 0), crouch=0.0,
              feet=None, look=0.7, knee_out=0.0):
        """Capas de cuerpo sobre la base (grados / cm). twist = torsión de la columna (+ = hacia la
        izquierda del personaje), lean = inclinación hacia adelante, side = inclinación lateral (+ =
        hacia la izquierda), shift = mover la cadera, crouch = bajar la cadera, feet = {"R"/"L":
        (dx, dy, dz, yaw)} mueve el pie. look = cuánto compensa la cabeza el giro de la columna."""
        feet = feet or {}
        foot_t = {s: self.M(f"Bip01_{s}_Foot") for s in "RL"}
        knee = {s: self.M(f"Bip01_{s}_Calf").translation for s in "RL"}
        head0 = self.M("Bip01_Head")
        pel = self.M("Bip01_Pelvis")
        # cadera: desplazar + girar (arrastra todo el cuerpo; los pies se vuelven a poner con IK)
        root = "Bip01"
        m = self.M(root)
        m = Matrix.Translation(Vector(shift) + Vector((0, 0, -crouch))) @ _about(pel.translation, _rot("Z", hips_yaw)) @ m
        self._set(root, m)
        # columna: torsión, inclinación y lateral repartidas
        for bone, w in zip(SPINE, SPINE_W):
            cur = self.M(bone)
            fwd = Vector((0, -1, 0))
            r = _rot("Z", twist * w) @ Matrix.Rotation(math.radians(-lean * w), 3, Vector((1, 0, 0))) \
                @ Matrix.Rotation(math.radians(side * w), 3, fwd)
            self.rotate(bone, r)
        # cabeza: devuelve parte del giro para mirar al frente
        h = self.M("Bip01_Head")
        d = head0.to_quaternion() @ h.to_quaternion().inverted()
        r = Quaternion().slerp(d, look).to_matrix()
        self._set("Bip01_Head", _about(h.translation, r) @ h)
        # piernas: pies plantados (o movidos) con IK; rodillas hacia donde estaban en la base
        for s in "RL":
            dx, dy, dz, yaw = (list(feet.get(s, ())) + [0, 0, 0, 0])[:4]
            ft = foot_t[s]
            ft = Matrix.Translation((dx, dy, dz)) @ _about(ft.translation, _rot("Z", yaw)) @ ft
            pole = (knee[s] - (self.M(f"Bip01_{s}_Thigh").translation + ft.translation) / 2)
            pole += Vector((knee_out * (1 if s == "L" else -1), 0, 0))
            self.two_bone((f"Bip01_{s}_Thigh", f"Bip01_{s}_Calf", f"Bip01_{s}_Foot"), ft.translation, pole, ft)

    def arm(self, side, hand_m, elbow=None):
        """Brazo por IK hasta la matriz de mano; el codo mira hacia `elbow` (vector) o hacia donde
        estaba en la base."""
        up, fo, ha = (f"Bip01_{side}_UpperArm", f"Bip01_{side}_Forearm", f"Bip01_{side}_Hand")
        sh = self.M(up).translation
        if elbow is None:
            el = self.M(fo).translation
            mid = (sh + hand_m.translation) / 2
            pole = el - mid
            if pole.length < 1:
                pole = Vector((0.3 * (1 if side == "L" else -1), 0.4, -1))
        else:
            pole = Vector(elbow)
        self.two_bone((up, fo, ha), hand_m.translation, pole, hand_m)

    def weapon(self, prop_m, left=None, left_m=None, elbow_r=None, elbow_l=None):
        """Arma en Bip01_Prop1 = prop_m; mano derecha con el agarre vanilla; la izquierda a `left` cm
        sobre el mango (None = suelta, sigue la base) o en la matriz left_m."""
        self._set("Bip01_Prop1", prop_m)
        self.arm("R", prop_m @ self.grip_r, elbow_r)
        if left is not None:
            ml = prop_m @ Matrix.Translation((0, left, 0)) @ self.grip_l
            self.arm("L", ml, elbow_l)
        elif left_m is not None:
            self.arm("L", left_m, elbow_l)

    def props(self, right_m, left_m, elbow_r=None, elbow_l=None):
        """Dos props (guantes): cada mano con el agarre vanilla de una mano."""
        self._set("Bip01_Prop1", right_m)
        self._set("Bip01_Prop2", left_m)
        self.arm("R", right_m @ self.grip_r, elbow_r)
        self.arm("L", left_m @ self.grip_l, elbow_l)

    def fist(self, side, pos, punch, dorsal):
        """Matriz del prop (Prop1 = derecha, Prop2 = izquierda) para que el puño `side` quede con su
        centro en `pos`, los nudillos hacia `punch` y el dorso de la mano hacia `dorsal`."""
        k, d, center = self.fist_axes[side]
        K = Matrix((k, d.cross(k), d)).transposed()
        pk = Vector(punch).normalized()
        pd = Vector(dorsal)
        pd = (pd - pk * pd.dot(pk)).normalized()
        W = Matrix((pk, pd.cross(pk), pd)).transposed()
        R = W @ K.transposed()
        m = R.to_4x4()
        m.translation = Vector(pos) - R @ center
        return m

    def key(self, frame):
        for b in self.order:
            b.keyframe_insert("location", frame=frame)
            b.keyframe_insert("rotation_quaternion", frame=frame)
            if b.rotation_mode != "QUATERNION":
                b.rotation_mode = "QUATERNION"

    def finish(self, start, end):
        a = self.action
        a.frame_range = (start, end)
        a.use_frame_range = True
        bpy.context.scene.frame_start, bpy.context.scene.frame_end = start, end
        return a


# --------------------------------------------------------------- armas
def prop_matrix(grip, along, face):
    """Hueso de prop: origen en el agarre, Y a lo largo del mango (hacia la cabeza del arma),
    Z hacia donde mira el filo/cara de la cabeza."""
    m = _aim(face, along).to_4x4()
    m.translation = Vector(grip)
    return m


class WeaponPath:
    """Trayectoria del arma por keys {frame: (agarre, punta, cara)}: agarre y punta van por splines
    separados (la punta describe arcos) y `cara` orienta el filo. cara None = el filo va hacia donde
    se mueve la punta (o -1 * eso con cara "back")."""

    def __init__(self, keys, ease=None):
        self.grip = Track({f: Vector(k[0]) for f, k in keys.items()}, ease)
        self.tip = Track({f: Vector(k[1]) for f, k in keys.items()}, ease)
        faces = {}
        for f, k in keys.items():
            face = k[2]
            if face is None or isinstance(face, str):
                d = self.tip(f + 0.5) - self.tip(f - 0.5)
                along = (self.tip(f) - self.grip(f)).normalized()
                d = d - along * d.dot(along)
                if d.length < 1e-3:
                    d = Vector((0, -1, 0))
                face = d.normalized() * (-1 if face == "back" else 1)
            faces[f] = Vector(face)
        self.face = Track(faces, ease)

    def __call__(self, frame):
        g = self.grip(frame)
        return prop_matrix(g, self.tip(frame) - g, self.face(frame))




# ---------------------------------------------------------- receta completa
BODY_FIELDS = ("hips_yaw", "twist", "lean", "side", "crouch")


def _vec_or_guard(v, guard):
    return v


def build(spec, preview=False):
    """Hornea una animación descrita por un módulo/objeto `spec` con:
      NAME, WEAPON, FRAMES, HITS, BASE (clip vanilla de piernas/postura), GRIP (clase),
      WEAPON_KEYS {frame: (agarre, punta, cara) | "guard"}  (cara None = sigue la trayectoria),
      EASE {frame: easing del tramo que empieza ahí},
      LEFT {frame: cm de la mano izquierda sobre el mango} (opcional; sin LEFT la izquierda queda libre),
      BODY {frame: {hips_yaw, twist, lean, side, crouch, shift}}, FEET {frame: {"R": (dx,dy,dz,yaw)}},
      o, para guantes, FISTS {frame: {"R": (pos, nudillos, dorso), "L": (...)}} en lugar de WEAPON_KEYS.
    """
    rig = al.load_rig()
    body = Body(rig, spec.NAME, spec.BASE, getattr(spec, "WARP", None), spec.GRIP)
    ease = getattr(spec, "EASE", {})
    guard_grip = body.guard.translation.copy()
    guard_tip = body.guard @ Vector((0, 45, 0))
    guard_face = body.guard.to_3x3().col[2].normalized()

    def tracks(keys, fields, default=0.0):
        out = {}
        for fld in fields:
            ks = {f: v.get(fld, default) for f, v in keys.items()}
            out[fld] = Track({f: (Vector(x) if isinstance(x, (tuple, list)) else x) for f, x in ks.items()}, ease)
        return out

    B = tracks(spec.BODY, BODY_FIELDS)
    B["shift"] = Track({f: Vector(v.get("shift", (0, 0, 0))) for f, v in spec.BODY.items()}, ease)
    feet_keys = getattr(spec, "FEET", {1: {}, spec.FRAMES: {}})
    FT = {s: Track({f: Vector((list(v.get(s, ())) + [0, 0, 0, 0])[:4]) for f, v in feet_keys.items()}, ease) for s in "RL"}
    left = getattr(spec, "LEFT", None)
    LT = Track(left, ease) if left else None

    if hasattr(spec, "FISTS"):
        fk = {}
        for s in "RL":
            ks = {}
            for f, v in spec.FISTS.items():
                if v == "guard" or v.get(s) == "guard":
                    ks[f] = None
                else:
                    ks[f] = v[s]
            fk[s] = ks
        P0 = al.x_pose(vanilla(GRIP_REF[spec.GRIP][0]), GRIP_REF[spec.GRIP][1])
        guard_props = {"R": P0["Bip01_Prop1"], "L": P0["Bip01_Prop2"]}
        FP = {}
        for s in "RL":
            keys = {}
            for f, v in fk[s].items():
                if v is None:   # guardia vanilla: deducir centro/nudillos/dorso del prop de guardia
                    k, d, c = body.fist_axes[s]
                    g = guard_props[s]
                    v = (g @ c, g.to_3x3() @ k, g.to_3x3() @ d)
                keys[f] = v
            FP[s] = (Track({f: Vector(v[0]) for f, v in keys.items()}, ease),
                     Track({f: Vector(v[1]) for f, v in keys.items()}, ease),
                     Track({f: Vector(v[2]) for f, v in keys.items()}, ease))
    else:
        wk = {}
        for f, v in spec.WEAPON_KEYS.items():
            wk[f] = (guard_grip, guard_tip, guard_face) if v == "guard" else v
        path = WeaponPath(wk, ease)

    reach = {}
    for f in range(1, spec.FRAMES + 1):
        body.frame = f
        body.overreach = 0.0
        body.overreach_who = ""
        body.base_pose(f)
        body.layer(hips_yaw=B["hips_yaw"](f), twist=B["twist"](f), lean=B["lean"](f), side=B["side"](f),
                   shift=B["shift"](f), crouch=B["crouch"](f),
                   feet={s: tuple(FT[s](f)) for s in "RL"})
        if hasattr(spec, "FISTS"):
            mats = {s: body.fist(s, FP[s][0](f), FP[s][1](f), FP[s][2](f)) for s in "RL"}
            body.props(mats["R"], mats["L"])
        else:
            body.weapon(path(f), left=LT(f) if LT else None)
        if body.overreach > 0.5:
            reach[f] = f"{body.overreach_who}:{body.overreach:.0f}"
        body.key(f)
    if reach:
        print(f"[animkit] {spec.NAME}: brazos/piernas estirados de más (cm) {reach}")
    action = body.finish(1, spec.FRAMES)
    out = al.ROOT / "art" / "anims"
    al.export_glb(rig, action, out / f"{spec.NAME}.glb")
    if preview:
        if hasattr(spec, "FISTS"):
            al.attach_weapon(rig, spec.WEAPON)
            al.attach_weapon(rig, spec.WEAPON + "L", bone="Bip01_Prop2", tex_id=spec.WEAPON)
        else:
            al.attach_weapon(rig, spec.WEAPON)
        preview_sheet(rig, list(range(1, spec.FRAMES + 1, 2)), out / f"{spec.NAME}_sheet.png",
                      gif=out / f"{spec.NAME}.gif", hits=getattr(spec, "HITS", ()))
    return rig, action


def preview_sheet(rig, frames, out_png, gif=None, hits=(), size=260):
    """Dos vistas por frame: 3/4 desde adelante-derecha (como suele verse en el juego) y cenital.
    Un poste rojo marca dónde estaría el zombi (45 cm adelante). Los frames de golpe van con borde."""
    from PIL import Image, ImageDraw
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "CYCLES"
    if sc.render.engine == "CYCLES":
        sc.cycles.samples = 6
    sc.render.resolution_x = sc.render.resolution_y = size
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (.42, .45, .40, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.6
    sc.world = w
    for o in bpy.data.objects:
        if o.type == "MESH" and ("Female" in o.name or "Skeleton" in o.name or "Dress" in o.name or o.name.startswith("WGT")):
            o.hide_render = True
    # poste objetivo y piso (en el espacio del rig: hijo del armature para heredar escala)
    bpy.ops.mesh.primitive_cylinder_add(radius=3, depth=80, location=(0, -45, 40))
    post = bpy.context.object
    post.parent = rig
    post.matrix_parent_inverse = Matrix.Identity(4)
    post.location = (0, -45, 40)
    mt = bpy.data.materials.new("rojo")
    mt.diffuse_color = (0.8, 0.1, 0.1, 1)
    if mt.node_tree is None:
        mt.use_nodes = True
    mt.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.1, 0.1, 1)
    post.data.materials.append(mt)
    sun = bpy.data.objects.new("sol", bpy.data.lights.new("sol", "SUN"))
    sun.data.energy = 3
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    sc.collection.objects.link(sun)
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    sc.camera = co
    target = rig.matrix_world @ Vector((0, -15, 55))
    views = ((math.radians(32), math.radians(-60), 2.2), (math.radians(88), math.radians(-90), 2.4))
    tmp = Path(out_png).parent / "_frames"
    tmp.mkdir(parents=True, exist_ok=True)
    cols = []
    for f in frames:
        sc.frame_set(f)
        pair = []
        for i, (el, az, scale) in enumerate(views):
            cam.ortho_scale = scale
            co.location = target + Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))) * 10
            co.rotation_euler = (target - co.location).to_track_quat("-Z", "Y").to_euler()
            sc.render.filepath = str(tmp / f"f{f:03d}_{i}.png")
            bpy.ops.render.render(write_still=True)
            pair.append(Image.open(sc.render.filepath).convert("RGB"))
        im = Image.new("RGB", (size, size * 2))
        im.paste(pair[0], (0, 0))
        im.paste(pair[1], (0, size))
        d = ImageDraw.Draw(im)
        d.text((4, 4), str(f), fill=(255, 255, 0))
        if any(abs(f - h) <= 1 for h in hits):
            d.rectangle((0, 0, size - 1, size * 2 - 1), outline=(255, 40, 40), width=3)
        cols.append(im)
    per = 9
    rows = (len(cols) + per - 1) // per
    sheet = Image.new("RGB", (min(len(cols), per) * size, rows * size * 2), (20, 20, 20))
    for i, im in enumerate(cols):
        sheet.paste(im, ((i % per) * size, (i // per) * size * 2))
    sheet.save(out_png)
    if gif:
        cols[0].save(gif, save_all=True, append_images=cols[1:], duration=int(1000 / al.FPS * (frames[1] - frames[0])), loop=0)
    print(f"[animkit] preview {out_png}")
