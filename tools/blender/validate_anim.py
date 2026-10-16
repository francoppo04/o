"""Validador de animaciones de ataque (Project Zomboid B42) — frame por frame y entre frames.

Uso:
  python3 tools/blender/validate_anim.py AC_RemoMolinete            # anima con el script (acción de Blender)
  python3 tools/blender/validate_anim.py AC_RemoMolinete --glb       # el GLB exportado, releído como el juego
  python3 tools/blender/validate_anim.py AC_RemoMolinete --glb RUTA  # otro GLB
Devuelve código 1 si falla algún criterio. Escribe el informe en art/anims/<NAME>_validacion.txt.

Unidades: centímetros del rig = centímetros del modelo del juego. El personaje mide ~90 unidades y
representa ~1,80 m, así que 1 unidad ≈ 2 cm reales (los umbrales de abajo ya están convertidos).

Qué mide (muestreando SUB muestras por frame):
  contacto   en cada AttackCollisionCheck del AnimSet, la parte que golpea toca la superficie del
             objetivo (|distancia| <= 0,5 u = 1 cm). Antes del primer impacto no lo atraviesa.
             El objetivo es un zombi: después del impacto el arma puede seguir de largo.
  cuerpo     el arma queda a >= 1,5 u (3 cm) de la malla deformada del cuerpo (sin manos/dedos);
             se excluye el tramo del mango dentro de los puños (GRIP_EXCLUDE u alrededor de cada agarre).
  agarre     mano derecha a <= 0,5 u de su punto del mango; mano izquierda sobre el eje del mango
             (radial <= 0,5 u) y sin deslizarse (<= 0,5 u) fuera de las ventanas de mezcla de entrada y
             salida (m_BlendTime / m_BlendOutTime del AnimSet), donde se permite reacomodar el agarre.
  rotacion   ningún hueso gira más de MAX_STEP grados entre muestras; en el GLB, sin cambios de
             hemisferio del cuaternión entre keys consecutivas.
  pies       sin patinar (<= 0,5 u del apoyo inicial) ni atravesar el piso (<= 0,5 u).
  articul.   rodillas 0-140° y hacia adelante; codos 0-155°.
  timing     el impacto coincide con m_TimePc del AnimSet y el primer/último frame calzan con la
             guardia vanilla (<= 1 u y <= 3°).
"""
import argparse
import importlib
import json
import math
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "anims"))

import bpy  # noqa: E402
from mathutils import Matrix, Quaternion, Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

import animkit as ak  # noqa: E402
import animlib as al  # noqa: E402

SUB = 4                 # muestras por frame
CONTACT = 0.5           # u (1 cm)
CLEARANCE = 1.5         # u (3 cm)
GRIP_TOL = 0.5          # u (1 cm)
GRIP_EXCLUDE = 8.0      # u: alrededor de cada agarre no cuentan las muñecas/antebrazos (solo esas partes)
EDGE_STEP = 1.0         # u: muestreo del arma sobre sus aristas
HINGE_TOL = 45.0        # grados: el plano de flexión de codo/rodilla no se aparta más que esto de la bisagra vanilla
WRIST = ("L_Forearm", "R_Forearm")
MAX_STEP = 20.0         # grados por muestra (1/4 de frame)
FOOT_SLIDE = 0.5        # u
FLOOR_TOL = 0.5         # u
GUARD_POS = 1.0         # u
GUARD_ROT = 3.0         # grados
MOD = al.ROOT / "Contents/mods/ArsenalChatarra/42/media"


# ------------------------------------------------------------------ AnimSet
def animset(spec):
    xml = next(MOD.glob(f"AnimSets/player/**/{spec.NAME.replace('Bob_', '')}.xml"), None)
    if xml is None:
        return None, [], 0.15, 0.25
    s = xml.read_text()
    hits = [float(m) for m in re.findall(
        r"<m_EventName>AttackCollisionCheck</m_EventName>\s*<m_TimePc>([\d.]+)</m_TimePc>", s)]
    bi = re.search(r"<m_BlendTime>([\d.]+)<", s)
    bo = re.search(r"<m_BlendOutTime>([\d.]+)<", s)
    return xml, hits, float(bi.group(1)) if bi else 0.15, float(bo.group(1)) if bo else 0.25


# --------------------------------------------------------- GLB como el juego
def _glb(path):
    d = Path(path).read_bytes()
    n = struct.unpack_from("<I", d, 12)[0]
    j = json.loads(d[20:20 + n])
    return j, d, 20 + n + 8


def _read(j, d, base, ai):
    a = j["accessors"][ai]
    v = j["bufferViews"][a["bufferView"]]
    k = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}[a["type"]]
    off = base + v.get("byteOffset", 0) + a.get("byteOffset", 0)
    stride = v.get("byteStride", 4 * k)
    return [struct.unpack_from("<" + "f" * k, d, off + stride * i) for i in range(a["count"])]


class GlbAsGame:
    """Lee el GLB y lo convierte como FileTask_LoadAnimation/ImportedSkeleton (42.21):
    MAKE_LEFT_HANDED (Z espejado), posiciones x0,01 y giro -90° en X a cada hueso con keys
    (local' = R^-1 · local · R). Después pasa al rig con animlib (F · X · F, m -> cm)."""

    S = Matrix.Diagonal((1, 1, -1, 1))
    R = Quaternion((1, 0, 0), -math.pi / 2).to_matrix().to_4x4()

    def __init__(self, path):
        j, d, base = _glb(path)
        self.nodes = j["nodes"]
        self.parent = {c: i for i, n in enumerate(self.nodes) for c in n.get("children", [])}
        self.idx = {}
        for i, n in enumerate(self.nodes):   # el hueso Bip01 (hay un objeto armature con el mismo nombre)
            if n["name"].startswith("Bip01") and (n["name"] != "Bip01" or i in self.parent):
                self.idx.setdefault(n["name"], i)
        an = j["animations"][0]
        self.ch = {}
        self.hemi = []
        for c in an["channels"]:
            s = an["samplers"][c["sampler"]]
            t = [x[0] for x in _read(j, d, base, s["input"])]
            v = _read(j, d, base, s["output"])
            self.ch.setdefault(c["target"]["node"], {})[c["target"]["path"]] = (t, v)
            if c["target"]["path"] == "rotation":
                name = self.nodes[c["target"]["node"]]["name"]
                for k in range(1, len(v)):
                    if sum(a * b for a, b in zip(v[k - 1], v[k])) < 0:
                        self.hemi.append((name, round(t[k] * al.FPS + 1, 2)))
        self.t0 = min(tt[0][0] for c in self.ch.values() for tt in c.values())
        self.duration = max(tt[0][-1] for c in self.ch.values() for tt in c.values()) - self.t0

    def _sample(self, i, path, t, default):
        c = self.ch.get(i, {}).get(path)
        if not c:
            return default
        ts, vs = c
        t = min(max(t, ts[0]), ts[-1])
        k = max(j for j in range(len(ts)) if ts[j] <= t)
        if k == len(ts) - 1:
            return vs[k]
        f = (t - ts[k]) / (ts[k + 1] - ts[k])
        if path == "rotation":
            a = Quaternion((vs[k][3], *vs[k][:3]))
            b = Quaternion((vs[k + 1][3], *vs[k + 1][:3]))
            q = a.slerp(b, f)
            return (q.x, q.y, q.z, q.w)
        return tuple(x + (y - x) * f for x, y in zip(vs[k], vs[k + 1]))

    def local(self, i, t):
        n = self.nodes[i]
        tr = self._sample(i, "translation", t, n.get("translation", (0, 0, 0)))
        r = self._sample(i, "rotation", t, n.get("rotation", (0, 0, 0, 1)))
        m = Quaternion((r[3], r[0], r[1], r[2])).to_matrix().to_4x4()
        m.translation = Vector(tr)
        m = self.S @ m @ self.S                       # MAKE_LEFT_HANDED
        m.translation = m.translation * 0.01          # animBonesScaleModifier
        return self.R.inverted() @ m @ self.R         # animBonesRotateModifier (padre ajustado)

    def pose(self, frame):
        """Matrices de los huesos en espacio del juego (desde el hueso Bip01), en el rig (cm)."""
        t = self.t0 + (frame - 1) / al.FPS
        G = {}
        order = sorted(self.idx, key=lambda b: self._depth(self.idx[b]))
        for b in order:
            i = self.idx[b]
            p = self.parent.get(i)
            pn = self.nodes[p]["name"] if p is not None else None
            m = self.local(i, t)
            G[b] = G[pn] @ m if (pn in G and b != "Bip01") else m
        out = {}
        for b, m in G.items():
            m = m.copy()
            m.translation = m.translation * 100
            out[b] = al.X_TO_RIG @ m @ al.X_LOCAL
        return out

    def _depth(self, i):
        d = 0
        while i in self.parent:
            i = self.parent[i]
            d += 1
        return d


# ------------------------------------------------------------------ escena
class Scene:
    def __init__(self, spec, glb=None):
        self.spec = spec
        self.glb = GlbAsGame(glb) if glb else None
        if self.glb:
            self.rig = al.load_rig()
            self.rig.animation_data.action = None
            self.order = sorted((b for b in self.rig.pose.bones if b.name.startswith("Bip01")),
                                key=lambda b: len(b.parent_recursive))
            self.frames = int(round(self.glb.duration * al.FPS)) + 1
            # raíz: el juego aplica su propia transformación de Dummy01/raíz; se alinea una vez con la
            # guardia vanilla en el frame 1 y queda fija (los demás huesos se comparan sin trampa)
            guard = al.x_pose(ak.vanilla(ak.GRIP_REF[spec.GRIP][0]), ak.GRIP_REF[spec.GRIP][1])
            self.root_fix = guard["Bip01"] @ self.glb.pose(1)["Bip01"].inverted()
        else:
            saved = al.export_glb
            al.export_glb = lambda *a, **k: None
            self.rig, _ = ak.build(spec, preview=False)
            al.export_glb = saved
            self.frames = spec.FRAMES
            from bpy_extras import anim_utils
            ad = self.rig.animation_data
            for fc in anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot).fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = "LINEAR"   # el juego interpola lineal entre keys horneadas
        self.weapon = al.attach_weapon(self.rig, spec.WEAPON)
        self.body = bpy.data.objects["OBJ-MaleBody (0)"]
        self.inv = self.rig.matrix_world.inverted()
        hand = {g.index for g in self.body.vertex_groups if any(k in g.name for k in ("Hand", "Finger"))}
        self.keep = [not (v.groups and max(v.groups, key=lambda g: g.weight).group in hand)
                     for v in self.body.data.vertices]
        self.pb = self.rig.pose.bones
        names = {g.index: g.name.replace("Bip01_", "") for g in self.body.vertex_groups}
        self.bone_of = [names.get(max(v.groups, key=lambda g: g.weight).group, "?") if v.groups else "?"
                        for v in self.body.data.vertices]
        P = al.x_pose(ak.vanilla(ak.GRIP_REF[spec.GRIP][0]), ak.GRIP_REF[spec.GRIP][1])
        self.guard = P
        self.hinge = {}
        for s_ in "RL":
            for up, lo, end in ((f"Bip01_{s_}_UpperArm", f"Bip01_{s_}_Forearm", f"Bip01_{s_}_Hand"),
                                (f"Bip01_{s_}_Thigh", f"Bip01_{s_}_Calf", f"Bip01_{s_}_Foot")):
                self.hinge[up] = hinge_normal(P, up, lo, end)
        self.grip_r = P["Bip01_Prop1"].inverted() @ P["Bip01_R_Hand"]
        self.grip_l = P["Bip01_Prop1"].inverted() @ P["Bip01_L_Hand"]

    def go(self, f):
        if self.glb:
            P = self.glb.pose(f)
            for b in self.order:
                if b.name in P:
                    b.matrix = self.root_fix @ P[b.name]
                    bpy.context.view_layer.update()
        else:
            k = 1 + (f - 1) * self.rig.get("keys_per_frame", 1)
            bpy.context.scene.frame_set(int(k), subframe=k - int(k))

    def M(self, b):
        return self.pb[b].matrix.copy()

    def body_tree(self):
        dg = bpy.context.evaluated_depsgraph_get()
        ev = self.body.evaluated_get(dg)
        me = ev.to_mesh()
        mw = self.inv @ self.body.matrix_world
        verts = [mw @ v.co for v in me.vertices]
        polys = [p.vertices[:] for p in me.polygons if all(self.keep[i] for i in p.vertices)]
        zmin = min(v.z for v in verts)
        ev.to_mesh_clear()
        self.poly_bone = [self.bone_of[p[0]] for p in polys]
        return BVHTree.FromPolygons(verts, polys), zmin

    def weapon_verts(self):
        """Puntos del arma: vértices + puntos sobre cada arista cada <= EDGE_STEP u (el mango tiene
        tramos de hasta 17 u sin vértices: un torso o el objetivo podían quedar entre dos)."""
        if not hasattr(self, "_wlocal"):
            me = self.weapon.data
            pts = [v.co.copy() for v in me.vertices]
            for e in me.edges:
                a, b = me.vertices[e.vertices[0]].co, me.vertices[e.vertices[1]].co
                n = int((a - b).length / EDGE_STEP)
                pts += [a.lerp(b, k / (n + 1)) for k in range(1, n + 1)]
            self._wlocal = pts
        m = self.inv @ self.weapon.matrix_world
        return [(m @ v, v.z) for v in self._wlocal]   # v.z = a lo largo del mango


# ---------------------------------------------------------------- criterios
def _angle(a, b):
    """Ángulo geométrico entre dos orientaciones (q y -q son la misma: 358° = 2°)."""
    ang = math.degrees(a.to_quaternion().rotation_difference(b.to_quaternion()).angle)
    return min(ang, 360 - ang)


def hinge_normal(P, up, lo, end):
    """Normal del plano de flexión en los ejes locales del hueso superior (brazo o muslo)."""
    S, E, T = (P[b].translation for b in (up, lo, end))
    n = (E - S).cross(T - E)
    if n.length < 1e-6:
        return None
    return (P[up].to_3x3().inverted() @ n).normalized()


def _inside(bt, p):
    """Punto dentro de la malla: paridad de cruces en tres rayos, por mayoría (la malla sin manos
    tiene agujeros en las muñecas; con mayoría de 3 rayos un agujero no decide solo)."""
    votes = 0
    for d in (Vector((0.31, 0.17, 0.93)), Vector((-0.6, 0.71, -0.36)), Vector((0.8, -0.55, 0.2))):
        o, n = p.copy(), 0
        for _ in range(40):
            hit = bt.ray_cast(o, d)
            if hit[0] is None:
                break
            n += 1
            o = hit[0] + d * 1e-3
        votes += n % 2
    return votes >= 2


def validate(spec, glb=None):
    sc = Scene(spec, glb)
    n = sc.frames
    xml, hits_pc, blend_in, blend_out = animset(spec)
    target = getattr(spec, "TARGET", {"center": (0, -48), "radius": 8.0, "z": (0, 85)})
    strike = getattr(spec, "STRIKE", (None, None))     # tramo del arma que golpea (cm a lo largo del mango)
    tc, tr = Vector(target["center"]), target["radius"]
    hit_frames = [1 + pc * (n - 1) for pc in hits_pc]
    win = (1 + blend_in * al.FPS, n - blend_out * al.FPS)
    fails = {k: [] for k in ("contacto", "cuerpo", "agarre", "rotacion", "pies", "articulaciones", "timing")}
    worst = {k: None for k in fails}

    def note(k, f, val, msg):
        fails[k].append((f, val, msg))

    # muestrear también a mitad de camino entre keys (si no, más keys esconderían el error de interpolación)
    kpf = (max(len(c["rotation"][0]) for c in sc.glb.ch.values() if "rotation" in c) - 1) / (n - 1) \
        if sc.glb else sc.rig.get("keys_per_frame", 1)
    sub = max(SUB, int(round(kpf)) * 2)
    samples = [1 + i / sub for i in range((n - 1) * sub + 1)]
    for hf in hit_frames:
        if hf not in samples:
            samples.append(hf)
    samples.sort()
    prev = None
    feet0 = None
    floor = None
    lslide_ref = None
    min_target_before = (1e9, 0)
    for f in samples:
        sc.go(f)
        bt, zmin = sc.body_tree()
        if floor is None:
            floor = zmin
        wv = sc.weapon_verts()
        prop = sc.M("Bip01_Prop1")
        grips = [(prop @ sc.grip_r).translation]
        # agarre
        rh = sc.M("Bip01_R_Hand")
        e = (rh.translation - (prop @ sc.grip_r).translation).length
        if e > GRIP_TOL:
            note("agarre", f, e, f"mano derecha a {e:.1f} u de su punto del mango")
        lh_in = prop.inverted() @ sc.M("Bip01_L_Hand")
        rel = lh_in @ sc.grip_l.inverted()              # = Traslación(a lo largo del mango) si agarra bien
        along = rel.translation.dot(Vector((0, 0, 1)))
        radial = (rel.translation - Vector((0, 0, along))).length
        grips.append((prop @ (sc.grip_l @ Matrix.Translation((0, 0, along)))).translation)
        if radial > GRIP_TOL:
            note("agarre", f, radial, f"mano izquierda fuera del mango ({radial:.1f} u)")
        twist = _angle(rel, Matrix.Identity(4))
        if twist > 10:
            note("agarre", f, twist, f"mano izquierda girada {twist:.0f}° respecto del agarre")
        if win[0] <= f <= win[1]:
            if lslide_ref is None:
                lslide_ref = along
            if abs(along - lslide_ref) > GRIP_TOL:
                note("agarre", f, abs(along - lslide_ref), f"mano izquierda se desliza {along - lslide_ref:+.1f} u sobre el mango")
        # cuerpo
        worst_c = (1e9, None, "")
        for p, z in wv:
            loc, nrm, idx, dist = bt.find_nearest(p)
            if loc is None:
                continue
            bone = sc.poly_bone[idx]
            if bone in WRIST and any((p - g).length < GRIP_EXCLUDE for g in grips):
                continue       # el mango dentro del puño toca la muñeca: no cuenta
            if dist >= 15:
                d = dist       # a más de 15 u de la superficie no puede estar adentro (el torso tiene ~20 u)
            else:
                d = -dist if _inside(bt, p) else dist     # dentro de la malla = negativo
            if d < worst_c[0]:
                worst_c = (d, z, bone)
        if worst_c[0] < CLEARANCE:
            part = "pala trasera" if worst_c[1] is not None and worst_c[1] < 0 else "pala delantera/mango"
            note("cuerpo", f, worst_c[0], f"{part} a {worst_c[0]:+.1f} u del cuerpo ({worst_c[2]})")
        # objetivo: con el arma ENTERA (una pala que cruzó también "toca" la superficie de atrás)
        inz = [(p, z) for p, z in wv if target["z"][0] <= p.z <= target["z"][1]]
        dists = [((p.xy - tc).length - tr, p, z) for p, z in inz]
        dt, pc, zc = min(dists, key=lambda x: x[0]) if dists else (1e9, None, None)
        is_strike = zc is not None and (strike[0] is None or zc >= strike[0]) and (strike[1] is None or zc <= strike[1])
        if hit_frames and f < hit_frames[0] - 1e-6 and dt < -CONTACT:
            note("contacto", f, dt, f"atraviesa al objetivo antes del impacto ({dt:+.1f} u)")
        for hf in hit_frames:
            if abs(f - hf) < 1e-6:
                if abs(dt) > CONTACT:
                    note("contacto", f, dt, f"en el impacto (m_TimePc) el arma está a {dt:+.1f} u de la superficie")
                if not is_strike:
                    note("contacto", f, 0, "en el impacto lo más cercano al objetivo no es la parte que golpea")
                zone = target.get("hit_z", target["z"])
                if pc is not None and not (zone[0] <= pc.z <= zone[1]):
                    note("contacto", f, 0, f"toca a {pc.z:.0f} u de alto, fuera de la franja de golpe {zone}")
                over = [p for p, z in wv if (p.xy - tc).length < tr - CONTACT and target["z"][0] <= p.z]
                if over:
                    note("contacto", f, len(over), f"{len(over)} vértices del arma adentro del objetivo en el impacto")
        if hit_frames and f < hit_frames[0]:
            min_target_before = min(min_target_before, (dt, f))
        # rotación
        cur = {b.name: b.matrix.copy() for b in sc.pb if b.name.startswith("Bip01") and "_end" not in b.name}
        if prev:
            for b, m in cur.items():
                a = _angle(prev[b], m)
                if a * sub / SUB > MAX_STEP:
                    note("rotacion", f, a * sub / SUB, f"{b.replace('Bip01_', '')} gira a {a * sub / SUB:.0f}° por 1/{SUB} de frame")
        prev = cur
        # pies y piso
        ft = {s: sc.M(f"Bip01_{s}_Foot").translation for s in "RL"}
        if feet0 is None:
            feet0 = ft
        for s in "RL":
            d = (ft[s].xy - feet0[s].xy).length
            if d > FOOT_SLIDE:
                note("pies", f, d, f"pie {s} patina {d:.1f} u")
        if zmin < floor - FLOOR_TOL:
            note("pies", f, floor - zmin, f"atraviesa el piso {floor - zmin:.1f} u")
        # articulaciones
        for s in "RL":
            th, ca, fo = (sc.M(f"Bip01_{s}_{b}").translation for b in ("Thigh", "Calf", "Foot"))
            knee = math.degrees((ca - th).angle(fo - ca))
            fwd = sc.M(f"Bip01_{s}_Toe0").translation - fo      # la rodilla mira hacia la punta del pie
            fwd.z = 0
            fwd.normalize()
            out = (ca - (th + fo) / 2).dot(fwd)
            if knee > 140 or (knee > 10 and out < -0.5):
                note("articulaciones", f, knee, f"rodilla {s} {knee:.0f}° {'hacia atrás' if out < -0.5 else ''}")
            sh, el, wr = (sc.M(f"Bip01_{s}_{b}").translation for b in ("UpperArm", "Forearm", "Hand"))
            elbow = math.degrees((el - sh).angle(wr - el))
            if elbow > 155:
                note("articulaciones", f, elbow, f"codo {s} {elbow:.0f}°")
            # sentido: con el codo/rodilla doblado (> 15°) el plano de flexión tiene que ser el vanilla
            cur = {b.name: b.matrix for b in sc.pb if b.name.startswith("Bip01")}
            for up, lo, end, name, flex in ((f"Bip01_{s}_UpperArm", f"Bip01_{s}_Forearm", f"Bip01_{s}_Hand", "codo", elbow),
                                            (f"Bip01_{s}_Thigh", f"Bip01_{s}_Calf", f"Bip01_{s}_Foot", "rodilla", knee)):
                ref, nn = sc.hinge.get(up), hinge_normal(cur, up, lo, end)
                if ref is not None and nn is not None and flex > 15:
                    dev = math.degrees(ref.angle(nn))
                    if dev > HINGE_TOL:
                        note("articulaciones", f, dev, f"{name} {s} doblado al revés: {dev:.0f}° fuera de la bisagra vanilla (flexión {flex:.0f}°)")
    # timing
    if not hits_pc:
        note("timing", 0, 0, "el AnimSet no tiene AttackCollisionCheck")
    spec_hits = getattr(spec, "HITS", ())
    for hf, sh in zip(hit_frames, spec_hits):
        if abs(hf - sh) > 0.5:
            note("timing", hf, hf - sh, f"m_TimePc da el frame {hf:.2f}, el impacto diseñado es el {sh}")
    if len(spec_hits) != len(hit_frames):
        note("timing", 0, 0, f"{len(hit_frames)} AttackCollisionCheck en el AnimSet, {len(spec_hits)} impactos en el script")
    for f in (1, n):
        sc.go(f)
        for b, g in sc.guard.items():
            if b not in sc.pb or b.startswith("Bip01_Prop2") or "Dress" in b or "BackPack" in b:
                continue
            m = sc.M(b)
            dp = (m.translation - g.translation).length
            dr = _angle(m, g)
            if dp > GUARD_POS or dr > GUARD_ROT:
                note("timing", f, max(dp, dr), f"frame {f} no calza con la guardia vanilla en {b.replace('Bip01_', '')} ({dp:.1f} u, {dr:.0f}°)")
                break
    if sc.glb and sc.glb.hemi:
        for b, fr in sc.glb.hemi[:10]:
            note("rotacion", fr, 180, f"GLB: {b.replace('Bip01_', '')} cambia de hemisferio en la key del frame {fr}")

    # informe
    src = f"GLB releído como el juego ({glb})" if glb else "acción de Blender (antes de exportar)"
    lines = [f"Validación de {spec.NAME} — {src}",
             f"{n} frames, {sub} muestras por frame ({len(samples)} muestras); AnimSet: {xml.name if xml else 'no encontrado'}; "
             f"impactos (m_TimePc {hits_pc}) en los frames {[round(h, 2) for h in hit_frames]}",
             f"objetivo: cilindro centro {tuple(target['center'])} radio {tr} u; antes del impacto, distancia mínima "
             f"{min_target_before[0]:+.1f} u (frame {min_target_before[1]})", ""]
    ok = True
    for k, lst in fails.items():
        if not lst:
            lines.append(f"PASA   {k}")
            continue
        ok = False
        frames = sorted({round(f, 2) for f, _, _ in lst})
        w = max(lst, key=lambda x: abs(x[1]))
        lines.append(f"FALLA  {k}: {len(lst)} problemas en {len(frames)} muestras "
                     f"(frames {frames[0]}–{frames[-1]}); peor: frame {round(w[0], 2)}: {w[2]}")
        for f, _, msg in lst[:6]:
            lines.append(f"         frame {round(f, 2):6}: {msg}")
    lines.append("")
    lines.append("RESULTADO: " + ("PASA" if ok else "FALLA"))
    report = "\n".join(lines)
    out = al.ROOT / "art" / "anims" / f"{spec.NAME}_validacion{'_glb' if glb else ''}.txt"
    out.write_text(report + "\n")
    print(report)
    return ok


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("anim")
    ap.add_argument("--glb", nargs="?", const="")
    a = ap.parse_args(argv)
    spec = importlib.import_module(a.anim)
    glb = None
    if a.glb is not None:
        glb = a.glb or str(al.ROOT / "art" / "anims" / f"{spec.NAME}.glb")
    sys.exit(0 if validate(spec, glb) else 1)
