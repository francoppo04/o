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

    def __init__(self, keys, ease=None, default="io", hold=False):
        self.hold = hold     # True: tramo suavizado entre dos keys sin tangentes (no se pasa de largo)
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
        if self.hold:
            return v[i] + (v[i + 1] - v[i]) * t
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


def _blend(a, b, w):
    """Mezcla dos matrices (posición lineal, rotación slerp)."""
    qa, qb = a.to_quaternion(), b.to_quaternion()
    if qa.dot(qb) < 0:
        qb.negate()
    m = qa.slerp(qb, w).to_matrix().to_4x4()
    m.translation = a.translation.lerp(b.translation, w)
    return m


def raised_cos(x, width):
    """1 en x=0, 0 desde |x| >= width, suave."""
    return 0.0 if abs(x) >= width else 0.5 * (1 + math.cos(math.pi * x / width))


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

ELBOW_SMOOTH = 0.6     # filtro temporal del polo del codo (0 = codo de la base, cuadro a cuadro)
ELBOW_MAX_STEP = 6.0   # grados por key que puede girar el polo del codo

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
        self.guard_pose = P
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
        """Gira un hueso y TODO lo que cuelga de él como un bloque rígido, en espacio armature,
        alrededor de su cabeza. Ojo: en el rig las clavículas, los muslos y los props no heredan la
        rotación del padre; si solo se girara el padre, quedarían mirando para otro lado."""
        self.transform_subtree(name, _about(pivot if pivot is not None else self.M(name).translation, rot3))

    def transform_subtree(self, name, T, skip=()):
        bones = [name] + [c.name for c in self.pb[name].children_recursive]
        bones = [b for b in bones if b.startswith("Bip01") and b not in skip]
        bones.sort(key=lambda b: len(self.pb[b].parent_recursive))
        target = {b: T @ self.M(b) for b in bones}
        for b in bones:
            self.pb[b].matrix = target[b]
            bpy.context.view_layer.update()

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
        w = self.guard_weight(frame) if hasattr(self, "guard_weight") else 0.0
        if w > 0:
            G = self.guard_pose
            for b in P:
                if b in G:
                    P[b] = _blend(P[b], G[b], w)
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
        self.transform_subtree(root, Matrix.Translation(Vector(shift) + Vector((0, 0, -crouch)))
                               @ _about(pel.translation, _rot("Z", hips_yaw)), skip=("Bip01_Prop1", "Bip01_Prop2"))
        # columna: torsión, inclinación y lateral repartidas
        for bone, w in zip(SPINE, SPINE_W):
            cur = self.M(bone)
            fwd = Vector((0, -1, 0))
            r = _rot("Z", twist * w) @ Matrix.Rotation(math.radians(-lean * w), 3, Vector((1, 0, 0))) \
                @ Matrix.Rotation(math.radians(side * w), 3, fwd)
            self.rotate(bone, r) if bone != "Bip01_Spine" else self.transform_subtree(
                bone, _about(cur.translation, r), skip=("Bip01_L_Thigh", "Bip01_R_Thigh", "Bip01_L_Calf",
                                                        "Bip01_R_Calf", "Bip01_L_Foot", "Bip01_R_Foot",
                                                        "Bip01_L_Toe0", "Bip01_R_Toe0"))
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
        estaba en la base. La torsión del antebrazo (pronación/supinación) sigue a la mano: así no
        hereda giros de la animación base que la mano ya no hace."""
        up, fo, ha = (f"Bip01_{side}_UpperArm", f"Bip01_{side}_Forearm", f"Bip01_{side}_Hand")
        sh = self.M(up).translation
        if elbow is None:
            el = self.M(fo).translation
            mid = (sh + hand_m.translation) / 2
            pole = el - mid
            if pole.length < 1:
                pole = Vector((0.3 * (1 if side == "L" else -1), 0.4, -1))
            # el codo de la base está pensado para la mano de la base, no para la nuestra: se filtra en
            # el tiempo para que no salte cuando las dos manos difieren (keys en orden creciente)
            prev = getattr(self, "_pole", {}).get(side)
            pole = pole.normalized()
            if prev is not None and getattr(self, "_pole_frame", {}).get(side, -1) < self.frame:
                pole = (prev * ELBOW_SMOOTH + pole * (1 - ELBOW_SMOOTH)).normalized()
                # el polo no puede girar más de ELBOW_MAX_STEP grados por key (evita que el codo se dé vuelta)
                u = (hand_m.translation - sh).normalized()
                a = (prev - u * prev.dot(u)).normalized()
                b = (pole - u * pole.dot(u)).normalized()
                ang = a.angle(b) if a.length and b.length else 0.0
                lim = math.radians(ELBOW_MAX_STEP)
                if ang > lim:
                    pole = a.slerp(b, lim / ang) if hasattr(a, "slerp") else (a * (1 - lim / ang) + b * (lim / ang)).normalized()
            self.__dict__.setdefault("_pole", {})[side] = pole
            self.__dict__.setdefault("_pole_frame", {})[side] = self.frame
        else:
            pole = Vector(elbow)
        base_fo, base_ha = self.M(fo), self.M(ha)
        self.two_bone((up, fo, ha), hand_m.translation, pole, hand_m)
        # pronación: la torsión que la muñeca tendría que hacer DE MÁS respecto de la base pasa al
        # antebrazo (en la base vanilla la muñeca ya trae su propia torsión: esa se respeta)
        rel = (self.rest[fo].inverted() @ self.rest[ha]).to_3x3()

        def wrist_twist(fore, hand):
            resid = hand.to_quaternion() @ (fore.to_3x3() @ rel).to_quaternion().inverted()
            axis = (hand.translation - fore.translation).normalized()
            t = 2 * math.atan2(Vector(resid[1:]).dot(axis), resid[0])
            return (t + math.pi) % (2 * math.pi) - math.pi, axis

        tb, _ = wrist_twist(base_fo, base_ha)
        cur = self.M(fo)
        tn, axis = wrist_twist(cur, hand_m)
        d = (tn - tb + math.pi) % (2 * math.pi) - math.pi
        self._set(fo, _about(cur.translation, Matrix.Rotation(d, 3, axis)) @ cur)
        m = hand_m.copy()
        m.translation = self.M(ha).translation
        self._set(ha, m)

    def weapon(self, prop_m, left=None, left_m=None, elbow_r=None, elbow_l=None):
        """Arma en Bip01_Prop1 = prop_m; mano derecha con el agarre vanilla; la izquierda a `left` cm
        sobre el mango (None = suelta, sigue la base) o en la matriz left_m."""
        self._set("Bip01_Prop1", prop_m)
        self.arm("R", prop_m @ self.grip_r, elbow_r)
        if left is not None:
            ml = prop_m @ Matrix.Translation(AXIS_ALONG * left) @ self.grip_l
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
        """Keyea todos los huesos. Cada cuaternión se pone en el mismo hemisferio que el del frame
        anterior (q y -q son la misma rotación, pero interpolar entre q y -q da la vuelta larga)."""
        prev = getattr(self, "_prevq", {})
        for b in self.order:
            q = b.rotation_quaternion.copy()
            if b.name in prev and q.dot(prev[b.name]) < 0:
                q.negate()
                b.rotation_quaternion = q
            prev[b.name] = q.copy()
            b.keyframe_insert("location", frame=frame)
            b.keyframe_insert("rotation_quaternion", frame=frame)
        self._prevq = prev

    def finish(self, start, end):
        a = self.action
        a.frame_range = (start, end)
        a.use_frame_range = True
        bpy.context.scene.frame_start, bpy.context.scene.frame_end = start, end
        return a


# --------------------------------------------------------------- armas
def prop_matrix(grip, along, face):
    """Hueso de prop en Blender: origen en el agarre. El modelo del juego tiene el mango sobre +Y y
    la cabeza/filo sobre +Z de SUS ejes, que en el hueso de Blender son +Z y +Y (animlib.MESH_TO_RIG):
    acá +Z del hueso = a lo largo del mango, +Y del hueso = hacia el filo/cara."""
    z = Vector(along).normalized()
    y = Vector(face)
    y = (y - z * y.dot(z)).normalized()
    x = y.cross(z)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = Vector(grip)
    return m


AXIS_ALONG = Vector((0, 0, 1))   # mango, en ejes del hueso de prop de Blender
AXIS_FACE = Vector((0, 1, 0))    # filo/cara


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
    guard_tip = body.guard @ (AXIS_ALONG * 45)
    guard_face = (body.guard.to_3x3() @ AXIS_FACE).normalized()

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
    LT = Track(left, ease, hold=True) if left else None     # agarre: sin rebote

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
    elif getattr(spec, "BASE_WEAPON", False):
        path = base_weapon_path(spec, body, ease)
    else:
        wk = {}
        for f, v in spec.WEAPON_KEYS.items():
            wk[f] = (guard_grip, guard_tip, guard_face) if v == "guard" else v
        path = WeaponPath(wk, ease)

    # primer y último frame = guardia vanilla exacta (el juego mezcla desde/hacia el idle de apuntar)
    gb = getattr(spec, "GUARD_BLEND", 3)
    body.guard_weight = lambda f: max(raised_cos(f - 1, gb), raised_cos(f - spec.FRAMES, gb))

    reach = {}
    sub = getattr(spec, "KEYS_PER_FRAME", 2)     # keys por frame de 30 fps (2 = 60 keys/s)
    for k in range(1, (spec.FRAMES - 1) * sub + 2):
        f = 1 + (k - 1) / sub
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
            body.weapon(path(f), left=LT(f) if LT else None,
                        elbow_r=getattr(spec, "ELBOW_R", None), elbow_l=getattr(spec, "ELBOW_L", None))
        if body.overreach > 0.5:
            reach[f] = f"{body.overreach_who}:{body.overreach:.0f}"
        body.key(k)
    if reach:
        print(f"[animkit] {spec.NAME}: brazos/piernas estirados de más (cm) {reach}")
    action = body.finish(1, (spec.FRAMES - 1) * sub + 1)
    rig["keys_per_frame"] = sub         # la escena va a 30*sub fps; el frame f de 30 fps es el 1+(f-1)*sub
    bpy.context.scene.render.fps = al.FPS * sub
    out = al.ROOT / "art" / "anims"
    al.export_glb(rig, action, out / f"{spec.NAME}.glb", fps=al.FPS * sub)
    if (out / f"{spec.NAME}.glb").exists():
        al.fix_glb_hemispheres(out / f"{spec.NAME}.glb")
    if preview:
        if hasattr(spec, "FISTS"):
            al.attach_weapon(rig, spec.WEAPON)
            al.attach_weapon(rig, spec.WEAPON + "L", bone="Bip01_Prop2", tex_id=spec.WEAPON)
        else:
            al.attach_weapon(rig, spec.WEAPON)
        frames = sorted(set(list(range(1, spec.FRAMES + 1, 2)) + list(getattr(spec, "HITS", ())) + [spec.FRAMES]))
        preview_sheet(rig, frames, out / f"{spec.NAME}_sheet.png", gif=out / f"{spec.NAME}.gif",
                      hits=getattr(spec, "HITS", ()), target=getattr(spec, "TARGET", None), sub=sub)
    return rig, action


def preview_sheet(rig, frames, out_png, gif=None, hits=(), size=260, target=None, sub=1):
    """Hoja de contacto: por cada frame (de 30 fps) tres vistas — de frente, de costado (lado derecho
    del personaje) y desde arriba. El cilindro rojo es el objetivo (TARGET); los frames de impacto van
    con borde rojo. sub = keys por frame de la acción."""
    from PIL import Image, ImageDraw
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"   # EEVEE necesita EGL, no disponible sin pantalla
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
    target = target or {"center": (0, -48), "radius": 8.0, "z": (0, 85)}
    h = target["z"][1] - target["z"][0]
    bpy.ops.mesh.primitive_cylinder_add(radius=target["radius"], depth=h)
    post = bpy.context.object
    post.parent = rig
    post.matrix_parent_inverse = Matrix.Identity(4)
    post.location = (*target["center"], target["z"][0] + h / 2)
    mt = bpy.data.materials.new("rojo")
    mt.use_nodes = True
    mt.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.1, 0.1, 1)
    mt.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.45
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
    tgt = rig.matrix_world @ Vector((0, -25, 50))
    views = (("frente (sin objetivo)", math.radians(8), math.radians(-90), 1.6),
             ("costado", math.radians(8), math.radians(180), 1.6),
             ("arriba", math.radians(89), math.radians(-90), 1.6))
    tmp = Path(out_png).parent / "_frames"
    tmp.mkdir(parents=True, exist_ok=True)
    cols = []
    for f in frames:
        k = 1 + (f - 1) * sub
        sc.frame_set(int(k), subframe=k - int(k))
        im = Image.new("RGB", (size, size * len(views)))
        for i, (name, el, az, scale) in enumerate(views):
            post.hide_render = name.startswith("frente")   # desde adelante el objetivo tapa al personaje
            cam.ortho_scale = scale
            co.location = tgt + Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))) * 10
            co.rotation_euler = (tgt - co.location).to_track_quat("-Z", "Y").to_euler()
            sc.render.filepath = str(tmp / f"f{k:03d}_{i}.png")
            bpy.ops.render.render(write_still=True)
            im.paste(Image.open(sc.render.filepath).convert("RGB"), (0, size * i))
            ImageDraw.Draw(im).text((4, size * i + size - 14), name, fill=(230, 230, 230))
        d = ImageDraw.Draw(im)
        d.text((4, 4), f"frame {f}", fill=(255, 255, 0))
        if any(abs(f - hh) < 0.5 for hh in hits):
            d.rectangle((0, 0, size - 1, size * len(views) - 1), outline=(255, 40, 40), width=3)
        cols.append(im)
    per = 8
    rows = (len(cols) + per - 1) // per
    sheet = Image.new("RGB", (min(len(cols), per) * size, rows * size * len(views)), (20, 20, 20))
    for i, im in enumerate(cols):
        sheet.paste(im, ((i % per) * size, (i // per) * size * len(views)))
    sheet.save(out_png)
    if gif:
        cols[0].save(gif, save_all=True, append_images=cols[1:], duration=int(1000 / al.FPS * (frames[1] - frames[0])), loop=0)
    print(f"[animkit] preview {out_png}")

# ------------------------------------------------- arma a partir del clip base
def weapon_local_verts(weapon_id):
    """Vértices del modelo del mod en ejes del hueso de prop de Blender (como attach_weapon)."""
    fbx = al.ROOT / "Contents/mods/ArsenalChatarra/42/media/models_X/weapons/ArsenalChatarra" / f"{weapon_id}.fbx"
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    new = [o for o in bpy.data.objects if o not in before]
    obj = [o for o in new if o.type == "MESH"][0]
    m = al.MESH_TO_RIG @ Matrix.Scale(100, 4)
    verts = [m @ v.co for v in obj.data.vertices]
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    return verts


def target_distance(prop_m, verts, target, strike):
    """Distancia (u) del ARMA ENTERA a la superficie del cilindro objetivo (negativa = adentro) y si
    el punto más cercano es de la parte que golpea (STRIKE). Con todo el arma: una pala que ya cruzó
    el objetivo también "toca" la superficie, pero la de atrás, con el mango adentro."""
    c, r = Vector(target["center"]), target["radius"]
    best = (1e9, None, False)
    for v in verts:
        p = prop_m @ v
        if not (target["z"][0] <= p.z <= target["z"][1]):
            continue
        d = (p.xy - c).length - r
        if d < best[0]:
            is_strike = (strike[0] is None or v.z >= strike[0]) and (strike[1] is None or v.z <= strike[1])
            best = (d, p, is_strike)
    return best


def base_weapon_path(spec, body, ease):
    """Trayectoria del arma = la del prop en el clip base (re-temporizado), inclinada con TILT
    (grados alrededor de TILT_AXIS, pivote TILT_PIVOT), desplazada con GRIP_OFFSET y con un ajuste
    suave alrededor de cada impacto para que la parte que golpea (STRIKE) toque el objetivo."""
    tilt = Track(getattr(spec, "TILT", {1: 0.0, spec.FRAMES: 0.0}), ease, hold=True)
    axis = Vector(getattr(spec, "TILT_AXIS", (0, 1, 0))).normalized()
    pivot = Vector(getattr(spec, "TILT_PIVOT", (0, -3, 74)))
    off = Track({f: Vector(v) for f, v in getattr(spec, "GRIP_OFFSET", {1: (0, 0, 0), spec.FRAMES: (0, 0, 0)}).items()}, ease, hold=True)
    gb = getattr(spec, "GUARD_BLEND", 3)
    G = body.guard

    pitch = Track(getattr(spec, "PITCH", {1: 0.0, spec.FRAMES: 0.0}), ease, hold=True)

    def raw(f):
        m = al.x_pose(body.base, body.warp(f))["Bip01_Prop1"]
        w = max(raised_cos(f - 1, gb), raised_cos(f - spec.FRAMES, gb))
        if w > 0:
            m = _blend(m, G, w)
        m = _about(pivot, Matrix.Rotation(math.radians(tilt(f)), 3, axis)) @ m
        # PITCH: cabecear el arma alrededor del agarre (+ = la punta baja, el extremo de atrás sube)
        along = (m.to_3x3() @ AXIS_ALONG).normalized()
        side = Vector((0, 0, 1)).cross(along)
        if side.length > 1e-3 and pitch(f):
            m = _about(m.translation, Matrix.Rotation(math.radians(pitch(f)), 3, side.normalized())) @ m
        return Matrix.Translation(off(f)) @ m

    target = getattr(spec, "TARGET", None)
    bumps = []
    if target:
        verts = weapon_local_verts(spec.WEAPON)
        strike = getattr(spec, "STRIKE", (None, None))
        width = getattr(spec, "CONTACT_WIDTH", 4.0)
        # 1) timing: el barrido de la base toca al objetivo de costado; el impacto se ubica en el
        #    instante de máximo acercamiento (así antes del impacto no hay penetración)
        if hasattr(spec, "WARP_KEYS"):
            keys = list(spec.WARP_KEYS)
            for i, (fn, fb) in enumerate(keys):
                if fb is None:
                    lo, hi = getattr(spec, "WARP_SEARCH", (max(b for a, b in keys[:i] if b is not None),
                                                           min(b for a, b in keys[i + 1:] if b is not None)))
                    def dist(b):
                        m = _about(pivot, Matrix.Rotation(math.radians(tilt(fn)), 3, axis)) \
                            @ al.x_pose(body.base, b)["Bip01_Prop1"]
                        return target_distance(m, verts, target, strike)[0]
                    ts = [lo + (hi - lo) * k / 80 for k in range(81)]
                    ds = [dist(b) for b in ts]
                    first = next((b for b, d in zip(ts, ds) if d <= 0), None)   # primer toque
                    best = (0, first) if first is not None else min(zip(ds, ts))
                    keys[i] = (fn, best[1])
            body.warp = timewarp(keys)
            print(f"[animkit] {spec.NAME}: timewarp {[(a, round(b, 2)) for a, b in keys]}")
        for _ in range(4):      # iterar: cada ajuste cambia un poco a los demás
            def cur(f):
                return Matrix.Translation(sum((d * raised_cos(f - h, width) for h, d in bumps), Vector())) @ raw(f)
            new = []
            for h in spec.HITS:
                d, p, _ = target_distance(cur(h), verts, target, strike)
                u = Vector((target["center"][0] - p.x, target["center"][1] - p.y, 0)).normalized()
                new.append((h, u * d))
            bumps = [(h, sum((d for hh, d in bumps if hh == h), Vector()) + nd) for h, nd in new]
            if all(abs(target_distance(cur(h), verts, target, strike)[0]) < 0.1 for h in spec.HITS):
                break

    def path(f):
        return Matrix.Translation(sum((d * raised_cos(f - h, getattr(spec, "CONTACT_WIDTH", 4.0)) for h, d in bumps),
                                      Vector())) @ raw(f)
    return path


# ------------------------------------------------------------------ AnimSet
def write_animset(spec, xml_path):
    """Deja en el AnimSet un AttackCollisionCheck por impacto, con m_TimePc calculado del frame."""
    import re
    import uuid
    s = Path(xml_path).read_text()
    param = re.search(r"<m_EventName>AttackCollisionCheck</m_EventName>.*?<m_ParameterValue>(\w+)<", s, re.S).group(1)
    s = re.sub(r"\s*<m_Events x_name=\"[^\"]+\">\s*<m_EventName>AttackCollisionCheck</m_EventName>.*?</m_Events>", "", s, flags=re.S)
    events = "".join(
        f"\n\t<m_Events x_name=\"{uuid.uuid5(uuid.NAMESPACE_URL, f'{spec.NAME}-hit-{h}')}\">\n"
        f"\t\t<m_EventName>AttackCollisionCheck</m_EventName>\n"
        f"\t\t<m_TimePc>{(h - 1) / (spec.FRAMES - 1):.4f}</m_TimePc>\n"
        f"\t\t<m_ParameterValue>{param}</m_ParameterValue>\n\t</m_Events>"
        for h in spec.HITS)
    i = s.index("<m_Events")
    i = s.rfind("\n", 0, i)
    s = s[:i] + events + s[i:]
    Path(xml_path).write_text(s)
