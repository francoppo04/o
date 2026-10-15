"""AC_BateErizo: bate de béisbol de madera + clavos + alambre de púas + medio disco de sierra.

Largo total ~0,84 m, a dos manos. Agarre de la mano principal en el origen (parte baja del mango),
el bate se extiende hacia +X. El disco de sierra queda en el plano XZ, clavado en el lado +Z.

Uso: python3 tools/blender/weapons/AC_BateErizo.py
"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

NAME = "AC_BateErizo"
GRIP = 0.08          # distancia desde el extremo de la perilla hasta el agarre (origen)
LENGTH = 0.842       # largo total del bate

# Perfil del bate: (x desde la perilla, radio). Medidas de un bate de madera adulto,
# con el mango apenas engrosado para que se lea a escala de juego.
PROFILE = [
    (0.000, 0.000),
    (0.004, 0.017),
    (0.011, 0.0262),   # perilla
    (0.022, 0.0252),
    (0.033, 0.0180),
    (0.042, 0.0172),   # inicio de la cinta
    (0.270, 0.0172),   # fin de la cinta
    (0.274, 0.0160),   # escalón cinta -> madera
    (0.340, 0.0172),
    (0.420, 0.0212),
    (0.500, 0.0268),
    (0.580, 0.0312),
    (0.660, 0.0335),
    (0.750, 0.0342),
    (0.800, 0.0332),
    (0.826, 0.0292),
    (0.838, 0.0210),
    (LENGTH, 0.000),
]
TAPE = (0.040, 0.273)

# Disco de sierra (en coordenadas x desde la perilla)
DISC_X = 0.715
DISC_Z = 0.054
DISC_R = 0.090
DISC_T = 0.0034
DISC_CLIP_Z = 0.012

BLOOD_DARK = (0.095, 0.006, 0.004)
BLOOD_RED = (0.21, 0.012, 0.008)
RUST_C = (0.30, 0.11, 0.035)


def radius_at(xr):
    for (x0, r0), (x1, r1) in zip(PROFILE, PROFILE[1:]):
        if x0 <= xr <= x1:
            t = (xr - x0) / (x1 - x0) if x1 > x0 else 0
            return r0 + (r1 - r0) * t
    return 0.0


def wx(xr):
    """x desde la perilla -> x del mundo (agarre en el origen)."""
    return xr - GRIP


# ------------------------------------------------------------ material propio
def gmat(name, color, grime=.3, grime_scale=10.0, grain=0.0, grain_scale=4.0, rust=0.0, rust_scale=14.0,
         blood=0.0, blood_scale=12.0, blood_x=None, seed=0.0, radial=None, tape=None, rough=.7):
    """Material horneable con variación en escala de grises (sin manchas de tinte),
    vetas de madera, óxido, sangre (opcionalmente creciente a lo largo de X) y gradiente radial."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for nd in list(nt.nodes):
        nt.nodes.remove(nd)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = rough
    L = nt.links
    L.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    coord = nt.nodes.new("ShaderNodeTexCoord")
    obj = coord.outputs["Object"]
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    L.new(obj, sep.inputs[0])

    def noise(scale, off, stretch=(1, 1, 1), detail=6.0, r=.6):
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Location"].default_value = (seed * 3.1 + off, seed * 1.7 + off * .6, seed * 2.3 + off * 1.4)
        mp.inputs["Scale"].default_value = stretch
        L.new(obj, mp.inputs["Vector"])
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = scale
        nz.inputs["Detail"].default_value = detail
        nz.inputs["Roughness"].default_value = r
        L.new(mp.outputs["Vector"], nz.inputs["Vector"])
        return nz.outputs["Fac"]

    def ramp(fac, stops):
        rp = nt.nodes.new("ShaderNodeValToRGB")
        cr = rp.color_ramp
        while len(cr.elements) < len(stops):
            cr.elements.new(0.5)
        for el, (pos, c) in zip(cr.elements, stops):
            el.position = pos
            el.color = (*c, 1) if len(c) == 3 else (c[0], c[0], c[0], 1)
        L.new(fac, rp.inputs[0])
        return rp.outputs["Color"]

    def rgb(c):
        n = nt.nodes.new("ShaderNodeRGB")
        n.outputs[0].default_value = (*c, 1)
        return n.outputs[0]

    def mix(a, b, fac=None, blend="MIX"):
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        mx.blend_type = blend
        if fac is None:
            mx.inputs["Factor"].default_value = 1.0
        else:
            L.new(fac, mx.inputs["Factor"])
        L.new(a, mx.inputs["A"])
        L.new(b, mx.inputs["B"])
        return mx.outputs["Result"]

    def math_op(op, a, b):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        for i, v in enumerate((a, b)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]

    col = rgb(color)
    if grain:
        f = noise(grain_scale, 1.0, stretch=(1, 18, 18), detail=4, r=.55)
        g = ramp(f, [(0.28, (1 - grain,)), (0.46, (1,)), (0.60, (1,)), (0.78, (1 - grain * .8,))])
        col = mix(col, g, blend="MULTIPLY")
    if tape:
        pitch, line, dark = tape
        at = math_op("ARCTAN2", sep.outputs["Z"], sep.outputs["Y"])
        t = math_op("ADD", math_op("MULTIPLY", sep.outputs["X"], 1 / pitch), math_op("MULTIPLY", at, 1 / (2 * math.pi)))
        fr = math_op("FRACT", t, 0.0)
        g = ramp(fr, [(0.0, (.88,)), (1 - line, (1,)), (1 - line * .5, (dark,)), (0.999, (.82,))])
        col = mix(col, g, blend="MULTIPLY")
    dist = None
    if radial:
        (rcx, rcz), stops = radial
        dx = math_op("SUBTRACT", sep.outputs["X"], rcx)
        dz = math_op("SUBTRACT", sep.outputs["Z"], rcz)
        dist = math_op("SQRT", math_op("ADD", math_op("MULTIPLY", dx, dx), math_op("MULTIPLY", dz, dz)), 0.0)
        g = ramp(dist, stops)
        col = mix(col, g, blend="MULTIPLY")
    if grime:
        f = noise(grime_scale, 2.0, detail=6, r=.6)
        g = ramp(f, [(0.30, (1 - grime,)), (0.68, (1,))])
        col = mix(col, g, blend="MULTIPLY")
        f2 = noise(grime_scale * 5, 4.0, detail=3, r=.5)
        g2 = ramp(f2, [(0.62, (1,)), (0.70, (1 - grime * .6,))])
        col = mix(col, g2, blend="MULTIPLY")
    if rust:
        f = noise(rust_scale, 5.0, detail=8, r=.65)
        thr = .76 - .36 * rust
        k = ramp(f, [(thr, (0,)), (thr + .05, (1,))])
        rc = mix(rgb(RUST_C), rgb((0.16, 0.06, 0.02)), fac=noise(rust_scale * 3, 6.0))
        col = mix(col, rc, fac=k)
    if blood:
        f = noise(blood_scale, 11.0, detail=8, r=.68)
        if blood_x:
            x0, x1, k = blood_x
            mr = nt.nodes.new("ShaderNodeMapRange")
            mr.clamp = True
            L.new(dist if (dist is not None and radial) else sep.outputs["X"], mr.inputs["Value"])
            mr.inputs["From Min"].default_value = x0
            mr.inputs["From Max"].default_value = x1
            f = math_op("ADD", f, math_op("MULTIPLY", mr.outputs["Result"], k))
        thr = .78 - .34 * blood
        mask = ramp(f, [(thr, (0,)), (thr + .03, (1,))])
        bc = mix(rgb(BLOOD_RED), rgb(BLOOD_DARK), fac=ramp(noise(blood_scale * 2.5, 13.0), [(0.4, (0,)), (0.6, (1,))]))
        col = mix(col, bc, fac=mask)
        # salpicaduras chicas
        sp = noise(blood_scale * 4.5, 17.0, detail=2, r=.5)
        thr2 = .80 - .10 * blood
        mask2 = ramp(sp, [(thr2, (0,)), (thr2 + .02, (1,))])
        col = mix(col, rgb(BLOOD_DARK), fac=mask2)
    L.new(col, bsdf.inputs["Base Color"])
    return m


# ------------------------------------------------------------ helpers de malla
def mk(name, bm, material, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    me.materials.append(material)
    for p in me.polygons:
        p.use_smooth = smooth
    return obj


def basis(d):
    d = Vector(d).normalized()
    a = d.orthogonal().normalized()
    b = d.cross(a).normalized()
    return d, a, b


def spike(name, base, direction, length, r, material, sides=4, shaft=0.74, embed=0.014, twist=0.0):
    """Clavo: caña prismática + punta piramidal. `base` en la superficie, sale hacia `direction`."""
    d, a, b = basis(direction)
    bm = bmesh.new()
    start = Vector(base) - d * embed
    ang = [twist + 2 * math.pi * i / sides for i in range(sides)]
    r0 = [bm.verts.new(start + (a * math.cos(t) + b * math.sin(t)) * r) for t in ang]
    mid = start + d * (embed + length * shaft)
    r1 = [bm.verts.new(mid + (a * math.cos(t) + b * math.sin(t)) * r * 0.92) for t in ang]
    tip = bm.verts.new(start + d * (embed + length))
    for i in range(sides):
        j = (i + 1) % sides
        bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
        bm.faces.new((r1[i], r1[j], tip))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mk(name, bm, material, smooth=True)


def bipyramid(bm, center, u, half, r):
    """Púa doble (octaedro estirado) a lo largo de u."""
    d, a, b = basis(u)
    c = Vector(center)
    t0 = bm.verts.new(c + d * half)
    t1 = bm.verts.new(c - d * half)
    ring = [bm.verts.new(c + (a * math.cos(t) + b * math.sin(t)) * r) for t in
            (0, math.pi / 2, math.pi, 3 * math.pi / 2)]
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((ring[i], ring[j], t0))
        bm.faces.new((ring[j], ring[i], t1))


def tube(bm, pts, r, sides=4, up_fn=None):
    """Tubo a lo largo de una polilínea; la sección se orienta con up_fn(p) (radial del bate)."""
    rings = []
    n = len(pts)
    for i, p in enumerate(pts):
        if i == 0:
            t = (pts[1] - pts[0]).normalized()
        elif i == n - 1:
            t = (pts[-1] - pts[-2]).normalized()
        else:
            t = (pts[i + 1] - pts[i - 1]).normalized()
        up = up_fn(p) if up_fn else Vector((0, 0, 1))
        up = (up - t * up.dot(t)).normalized()
        side = t.cross(up).normalized()
        ring = []
        for k in range(sides):
            ang = math.pi / 4 + 2 * math.pi * k / sides
            ring.append(bm.verts.new(p + (up * math.cos(ang) + side * math.sin(ang)) * r))
        rings.append(ring)
    for ra, rb in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            bm.faces.new((ra[k], ra[j], rb[j], rb[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])


def radial_of(p):
    v = Vector((0, p.y, p.z))
    return v.normalized() if v.length > 1e-6 else Vector((0, 0, 1))


# ------------------------------------------------------------------ modelo
pz.reset()

cx, cz = wx(DISC_X), DISC_Z
m_wood = gmat("madera", (0.52, 0.31, 0.15), grime=.28, grime_scale=9, grain=.42, grain_scale=3.5, seed=1.0,
              blood=.45, blood_scale=11, blood_x=(0.25, 0.70, 0.11))
m_tape = gmat("cinta", (0.60, 0.565, 0.47), grime=.26, grime_scale=14, seed=3.0, tape=(0.024, .18, .58),
              blood=.12, blood_scale=16)
m_nail = gmat("clavos", (0.31, 0.315, 0.33), grime=.25, grime_scale=30, rust=.35, rust_scale=40, seed=2.0,
              blood=.30, blood_scale=30)
m_wire = gmat("alambre", (0.13, 0.125, 0.12), grime=.2, grime_scale=30, rust=.55, rust_scale=40, seed=4.0,
              blood=.25, blood_scale=30)
m_disc = gmat("disco", (0.40, 0.41, 0.43), grime=.22, grime_scale=22, rust=.20, rust_scale=26, seed=5.0,
              blood=.40, blood_scale=17, blood_x=(0.045, 0.085, 0.14),
              radial=((cx, cz), [(0.0, (.50,)), (0.026, (.58,)), (0.029, (.95,)), (0.068, (.95,)),
                                 (0.071, (1.30,)), (0.2, (1.30,))]))
m_nut = gmat("tuerca", (0.12, 0.12, 0.13), grime=.2, grime_scale=40, rust=.3, rust_scale=50, seed=6.0)

parts = []

# --- bate (un solo torno con dos materiales: madera / cinta)
bat = pz.lathe("bate", [(r, x) for x, r in PROFILE], loc=(-GRIP, 0, 0), mat=m_wood, segs=10)
bat.data.materials.append(m_tape)
for p in bat.data.polygons:
    if TAPE[0] <= p.center.z <= TAPE[1]:
        p.material_index = 1
parts.append(bat)

# --- clavos: anillos de púas a lo largo del barril, en todas direcciones
rng = random.Random(7)
rows = [0.470, 0.540, 0.610, 0.680, 0.750]
n = 0
for ri, xr in enumerate(rows):
    base_ang = 0 if ri % 2 == 0 else 30
    for k in range(6):
        phi = base_ang + 60 * k + rng.uniform(-9, 9)
        # no clavar donde está el disco (arriba, cerca de la punta)
        if xr > 0.60 and abs(((phi - 90 + 180) % 360) - 180) < 40:
            continue
        x = xr + rng.uniform(-0.008, 0.008)
        R = radius_at(x)
        radial = Vector((0, math.cos(math.radians(phi)), math.sin(math.radians(phi))))
        tilt = math.radians(rng.uniform(-14, 14))
        d = (radial * math.cos(tilt) + Vector((1, 0, 0)) * math.sin(tilt)).normalized()
        base = Vector((wx(x), 0, 0)) + radial * (R - 0.001)
        parts.append(spike(f"clavo{n}", base, d, rng.uniform(0.074, 0.088), 0.0050, m_nail,
                           twist=rng.uniform(0, 1.5)))
        n += 1

# --- alambre de púas en hélice sobre el barril
bm = bmesh.new()
W_R = 0.0030
x0, x1 = 0.425, 0.800
turns = 6.0
per_turn = 8
steps = int(turns * per_turn)
pts = []
for i in range(steps + 1):
    t = i / steps
    xr = x0 + (x1 - x0) * t
    ang = 2 * math.pi * turns * t + 0.4
    rr = (radius_at(xr) + W_R) / math.cos(math.pi / per_turn)
    if i in (0, steps):
        rr = radius_at(xr) - 0.004   # las puntas del alambre quedan metidas en la madera
    pts.append(Vector((wx(xr), math.cos(ang) * rr, math.sin(ang) * rr)))
tube(bm, pts, W_R, sides=4, up_fn=radial_of)
# púas del alambre: una "X" cada 4 vértices
for i in range(3, steps - 1, 4):
    p = pts[i]
    t = (pts[i + 1] - pts[i - 1]).normalized()
    rho = radial_of(p)
    q = t.cross(rho).normalized()
    c = p + rho * 0.002
    bipyramid(bm, c, (rho * 0.7 + q), 0.016, 0.0018)
    bipyramid(bm, c, (rho * 0.7 - q), 0.016, 0.0018)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
parts.append(mk("alambre", bm, m_wire))

# --- medio disco de sierra clavado arriba, cerca de la punta
teeth = 20
pitch = 2 * math.pi / teeth
depth = 0.015
a_start = math.asin((DISC_CLIP_Z - DISC_Z) / DISC_R)        # ángulo donde el arco entra en la madera
a_end = math.pi - a_start
outline = [(cx + DISC_R * math.cos(a_start) - 0.004, DISC_CLIP_Z)]
a = a_start
while a < a_end:
    outline.append((cx + DISC_R * math.cos(a), cz + DISC_R * math.sin(a)))                      # punta
    g = a + pitch * 0.78
    if g < a_end:
        outline.append((cx + (DISC_R - depth) * math.cos(g), cz + (DISC_R - depth) * math.sin(g)))  # garganta
    a += pitch
outline.append((cx + DISC_R * math.cos(a_end) + 0.004, DISC_CLIP_Z))
parts.append(pz.extrude("disco", outline, DISC_T, mat=m_disc))
# arandela + tuerca en el centro del disco
parts.append(pz.cylinder("arandela", 0.0175, 0.0075, loc=(cx, 0, cz), rot=(90, 0, 0), mat=m_nut, segs=10, smooth=False))
parts.append(pz.cylinder("tuerca", 0.0105, 0.016, loc=(cx, 0, cz), rot=(90, 30, 0), mat=m_nut, segs=6, smooth=False))

model = pz.finish(NAME, parts, tex_size=256)
pz.previews(model, NAME, grip_offset=0.0, hold_rot=(0, -58, 40))
