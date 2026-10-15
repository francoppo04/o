"""AC_PareDefinitivo: señal de PARE/STOP arrancada con poste y base de concreto (Arsenal de Chatarra).

Largo total ~1,20 m, a dos manos, muy pesada. Caño galvanizado de 4 cm con agujeros, empuñadura de
cinta negra en la parte baja, trozo de concreto con varillas oxidadas como contrapeso (-X) y señal
octogonal roja con borde blanco y "STOP" (+X). La señal está montada como en la calle: su "arriba"
es +X (el poste corre por detrás, a lo largo de su eje vertical), la cara con el calco mira a -Y.

Uso: python3 tools/blender/weapons/AC_PareDefinitivo.py
"""
import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

ID = "AC_PareDefinitivo"
OUT = pz.ART / ID

# ------------------------------------------------------------------ medidas (m)
R_POLE = 0.0225                  # caño de ~4,5 cm (apenas exagerado para que se lea)
X_POLE0, X_POLE1 = -0.25, 0.80   # el caño entra en el concreto y termina detrás de la señal
X_TAPE0, X_TAPE1 = -0.130, 0.105
SIGN_HALF = 0.285                # señal de 57 cm entre caras planas
SIGN_CX = 0.30 + SIGN_HALF       # borde inferior plano en x=0.30
SIGN_T = 0.008                   # espesor (exagerado para que el canto se lea)
SIGN_Y = -(R_POLE + 0.003 + SIGN_T / 2)   # la placa va delante del caño (cara frontal hacia -Y)
BOLT_X = (SIGN_CX - 0.235, SIGN_CX + 0.235)
BOLT_Z = 0.036


# ------------------------------------------------------------- helpers de material
def tame(m, bright=0.0):
    """pz.mat suma brillo lineal (dirt*0.18) que lava los colores: lo bajamos."""
    for n in m.node_tree.nodes:
        if n.type == "BRIGHTCONTRAST":
            n.inputs["Bright"].default_value = bright
    return m


def _axis_mask(axis, full, zero):
    def build(nt):
        coord = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(coord.outputs["Object"], sep.inputs["Vector"])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = zero
        mr.inputs["From Max"].default_value = full
        mr.clamp = True
        nt.links.new(sep.outputs[axis], mr.inputs["Value"])
        return mr.outputs["Result"]
    return build


def add_splat(m, color, amount, scale, seed, lo=.38, hi=.78, mask=None):
    """Capa de manchas encima del color base (mugre, óxido, sangre). mask(nt) -> socket 0..1."""
    nt = m.node_tree
    L = nt.links
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    prev = bsdf.inputs["Base Color"].links[0].from_socket
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Location"].default_value = (seed, seed * .7, seed * 1.3)
    L.new(coord.outputs["Object"], mp.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 8
    nz.inputs["Roughness"].default_value = .65
    L.new(mp.outputs["Vector"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    thr = hi - (hi - lo) * amount
    ramp.color_ramp.elements[0].position = thr
    ramp.color_ramp.elements[1].position = min(thr + .03, 1.0)
    src = nz.outputs["Fac"]
    if mask is not None:
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        L.new(src, mul.inputs[0])
        L.new(mask(nt), mul.inputs[1])
        src = mul.outputs[0]
    L.new(src, ramp.inputs["Fac"])
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    L.new(ramp.outputs["Color"], mx.inputs["Factor"])
    L.new(prev, mx.inputs["A"])
    mx.inputs["B"].default_value = (*color, 1)
    L.new(mx.outputs["Result"], bsdf.inputs["Base Color"])
    return m


def edge_wear(m, color, amount=1.0, dist=0.012):
    """Desgaste en aristas convexas (AO 'inside' cortado con ruido)."""
    nt = m.node_tree
    L = nt.links
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    prev = bsdf.inputs["Base Color"].links[0].from_socket
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.inside = True
    ao.only_local = True
    ao.samples = 16
    ao.inputs["Distance"].default_value = dist
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    L.new(ao.outputs["AO"], inv.inputs[1])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 60
    nz.inputs["Detail"].default_value = 4
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    L.new(inv.outputs[0], mul.inputs[0])
    L.new(nz.outputs["Fac"], mul.inputs[1])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.10 / max(amount, 1e-3)
    ramp.color_ramp.elements[1].position = 0.10 / max(amount, 1e-3) + 0.06
    L.new(mul.outputs[0], ramp.inputs["Fac"])
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    L.new(ramp.outputs["Color"], mx.inputs["Factor"])
    L.new(prev, mx.inputs["A"])
    mx.inputs["B"].default_value = (*color, 1)
    L.new(mx.outputs["Result"], bsdf.inputs["Base Color"])
    return m


DRIED = (0.10, 0.010, 0.006)
RUST_D = (0.24, 0.075, 0.022)


def materials():
    M = {}
    g = tame(pz.mat("galvanizado", (0.36, 0.37, 0.38), rust=.22, dirt=.35, rough=.5, scale=26, seed=1), .01)
    add_splat(g, (0.20, 0.205, 0.21), .45, 9, 3.0)                                  # manchas de zinc
    add_splat(g, RUST_D, .55, 14, 7.0, mask=_axis_mask("X", 0.30, 0.10))             # óxido hacia la señal
    add_splat(g, DRIED, .40, 22, 4.0, mask=_axis_mask("X", 0.30, 0.18))              # sangre que chorreó
    M["pipe"] = g
    M["hole"] = pz.mat("agujero", (0.015, 0.012, 0.010), dirt=0.0, rough=1)
    M["tape"] = tame(pz.mat("cinta", (0.020, 0.020, 0.022), dirt=.35, rough=.6, scale=34, seed=2), .004)
    c = tame(pz.mat("concreto", (0.23, 0.22, 0.20), dirt=.55, rough=1, scale=11, seed=3), .0)
    add_splat(c, (0.05, 0.048, 0.044), .45, 55, 5.0)                                 # poros
    add_splat(c, (0.12, 0.09, 0.055), .50, 7, 9.0)                                   # tierra
    add_splat(c, DRIED, .40, 16, 2.0)                                                # sangre
    edge_wear(c, (0.40, 0.39, 0.36), .8, dist=.02)                                   # aristas rotas más claras
    M["concrete"] = c
    M["rebar"] = tame(pz.mat("varilla", (0.26, 0.095, 0.030), rust=.0, dirt=.6, rough=.9, scale=60, seed=4), .0)
    al = tame(pz.mat("aluminio", (0.40, 0.41, 0.42), rust=.0, dirt=.4, rough=.5, scale=14, seed=5), .01)
    add_splat(al, (0.16, 0.15, 0.13), .40, 7, 6.0)                                   # mugre de calle
    add_splat(al, DRIED, .40, 16, 8.0, mask=_axis_mask("X", SIGN_CX + 0.30, SIGN_CX))
    M["alu"] = al
    b = tame(pz.mat("bulon", (0.44, 0.44, 0.45), rust=.45, dirt=.3, rough=.4, scale=60, seed=6), .01)
    M["bolt"] = b
    M["clamp"] = tame(pz.mat("abrazadera", (0.30, 0.31, 0.32), rust=.35, dirt=.35, rough=.5, scale=40, seed=7), .01)
    M["decal"] = pz.image_mat("calco_stop", make_decal(), rough=.5)
    return M


# ------------------------------------------------------------- calco STOP (PIL)
def _noise(rng, size, cell):
    """Ruido de valor suave (0..1) del tamaño `size` con celdas de `cell` px."""
    n = max(2, size // cell)
    small = Image.fromarray((rng.random((n, n)) * 255).astype(np.uint8))
    return np.asarray(small.resize((size, size), Image.BICUBIC), dtype=np.float32) / 255.0


def _octagon(cx, cy, half):
    r = half / math.cos(math.pi / 8)
    return [(cx + r * math.cos(math.pi / 8 + k * math.pi / 4), cy + r * math.sin(math.pi / 8 + k * math.pi / 4))
            for k in range(8)]


def make_decal(S=512):
    rng = np.random.default_rng(9)
    rnd = random.Random(9)
    RED = (146, 20, 19)
    WHITE = (222, 216, 204)
    img = Image.new("RGB", (S, S), RED)
    d = ImageDraw.Draw(img)
    c = S / 2
    d.polygon(_octagon(c, c, c * 0.975), fill=WHITE)      # margen rojo fino + borde blanco ancho
    d.polygon(_octagon(c, c, c * 0.865), fill=RED)
    # texto STOP (letras altas y gruesas, estiradas a la caja de la señal real)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 200)
    tl = Image.new("L", (900, 260), 0)
    ImageDraw.Draw(tl).text((12, 2), "STOP", font=f, fill=255, stroke_width=11, stroke_fill=255)
    tl = tl.crop(tl.getbbox()).resize((int(S * 0.76), int(S * 0.31)), Image.LANCZOS)
    img.paste(WHITE, (int(c - tl.width / 2), int(c - tl.height / 2)), tl)

    a = np.asarray(img, dtype=np.float32)
    # decoloración por sol: rojo más apagado arriba-izquierda, manchas pálidas (como la ficha)
    fade = _noise(rng, S, 64) * 0.6 + _noise(rng, S, 16) * 0.4
    pale = np.clip((fade - 0.60) / 0.14, 0, 1)[..., None] * 0.35
    a = a * (1 - pale) + np.array([178, 120, 108], np.float32) * pale
    a *= (0.86 + 0.20 * _noise(rng, S, 24))[..., None]
    # rayones / pintura saltada (gris aluminio)
    chip = _noise(rng, S, 9)
    chipm = np.clip((chip - 0.86) / 0.04, 0, 1)[..., None] * 0.8
    a = a * (1 - chipm) + np.array([150, 150, 146], np.float32) * chipm
    # óxido/mugre en el borde exterior
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    dx, dy = np.abs(xx - c), np.abs(yy - c)
    dist_flat = np.maximum.reduce([dx, dy, (dx + dy) / math.sqrt(2)])      # distancia "octogonal"
    edge = np.clip((dist_flat - c * 0.90) / (c * 0.08), 0, 1)
    rust = np.clip((_noise(rng, S, 10) * 0.7 + 0.3 * _noise(rng, S, 40) + edge * 0.55 - 0.72) / 0.10, 0, 1)
    rust = (rust * edge)[..., None]
    a = a * (1 - rust) + np.array([96, 50, 24], np.float32) * rust
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

    # sangre: salpicadura grande hacia la esquina de golpe (arriba a la derecha) + gotas
    blood = Image.new("L", (S, S), 0)
    bd = ImageDraw.Draw(blood)
    for _ in range(26):
        ang = rnd.uniform(-0.9, 0.6)
        rr = rnd.uniform(0.45, 0.98) * c
        x, y = c + rr * math.cos(ang - 0.6), c + rr * math.sin(ang - 0.6)
        s = rnd.uniform(5, 26) * (1.25 - rr / c * 0.5)
        bd.ellipse((x - s, y - s * rnd.uniform(.6, 1.1), x + s, y + s), fill=255)
    for _ in range(40):
        x, y = rnd.uniform(c * 0.9, S * 0.97), rnd.uniform(S * 0.03, c * 1.2)
        s = rnd.uniform(2, 6)
        bd.ellipse((x - s, y - s, x + s, y + s), fill=255)
    for _ in range(4):                                                   # chorreados hacia abajo
        x, y = rnd.uniform(c * 1.05, S * 0.85), rnd.uniform(c * 0.25, c * 0.7)
        w = rnd.uniform(4, 7)
        bd.rounded_rectangle((x - w, y, x + w, y + rnd.uniform(40, 110)), radius=w, fill=255)
    blood = blood.filter(ImageFilter.GaussianBlur(1.5))
    bm_ = np.asarray(blood, np.float32)[..., None] / 255 * 0.92
    a = np.asarray(img, np.float32)
    bcol = np.array([78, 9, 7], np.float32) * (0.8 + 0.4 * _noise(rng, S, 12))[..., None]
    a = a * (1 - bm_) + bcol * bm_
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

    # agujeros de bala: centro oscuro, anillo de metal pelado
    d = ImageDraw.Draw(img)
    for (hx, hy) in ((0.30, 0.30), (0.71, 0.70), (0.62, 0.22)):
        x, y = hx * S, hy * S
        d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=(165, 160, 152))
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(22, 18, 16))
    # la textura va en UV (u=X del arma = "arriba" de la señal): rotar 90° horario
    img = img.rotate(-90)
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / "decal_stop.png"
    img.save(p)
    return p


# ------------------------------------------------------------- geometría
def bend(u, v):
    """Abolladuras de la placa. u: hacia +X (arriba de la señal) desde el centro, v: hacia +Z.
    Devuelve el desplazamiento en Y (+ = hacia atrás). Lejos de la línea del caño (v=0)."""
    dy = 0.0
    if v > 0.12:                                            # solapa lateral doblada hacia atrás
        dy += 1.9 * (v - 0.12) ** 2 * (1.0 + 0.9 * max(u, 0) / SIGN_HALF)
    dy += 0.016 * math.exp(-((u + 0.10) ** 2 + (v + 0.15) ** 2) / 0.0035)   # abolladura de golpe
    if v < -0.10:                                           # canto opuesto apenas torcido hacia adelante
        dy -= 0.35 * (v + 0.10) ** 2 * max(0.0, -u / SIGN_HALF + 0.3)
    return dy


def sign_plate(mat_front, mat_back):
    """Placa octogonal abollada: anillos concéntricos (16 puntos) para poder doblarla.
    Cara frontal (-Y) con el calco, dorso y canto de aluminio."""
    fr = [0.0, 0.38, 0.68, 0.88, 1.0]
    R = SIGN_HALF / math.cos(math.pi / 8)
    bm = bmesh.new()

    def ring_pts(f):
        pts = []
        for k in range(8):
            a0 = math.pi / 8 + k * math.pi / 4
            a1 = a0 + math.pi / 4
            p0 = (R * math.cos(a0), R * math.sin(a0))
            p1 = (R * math.cos(a1), R * math.sin(a1))
            pts.append((p0[0] * f, p0[1] * f))
            pts.append(((p0[0] + p1[0]) / 2 * f, (p0[1] + p1[1]) / 2 * f))
        return pts

    layers = []
    for side in (-1, 1):
        rings = []
        for f in fr:
            if f == 0:
                rings.append([bm.verts.new((SIGN_CX, SIGN_Y + side * SIGN_T / 2 + bend(0, 0), 0))])
                continue
            r = []
            for (u, v) in ring_pts(f):
                r.append(bm.verts.new((SIGN_CX + u, SIGN_Y + side * SIGN_T / 2 + bend(u, v), v)))
            rings.append(r)
        layers.append(rings)
    front, back = layers
    for rings, mi in ((front, 0), (back, 0)):
        c0 = rings[0][0]
        for i in range(16):
            j = (i + 1) % 16
            bm.faces.new((c0, rings[1][i], rings[1][j])).material_index = mi
        for a, b in zip(rings[1:], rings[2:]):
            for i in range(16):
                j = (i + 1) % 16
                bm.faces.new((a[i], b[i], b[j], a[j])).material_index = mi
    fo, bo = front[-1], back[-1]
    for i in range(16):
        j = (i + 1) % 16
        bm.faces.new((fo[i], fo[j], bo[j], bo[i])).material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("senal")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new("senal", me)
    bpy.context.scene.collection.objects.link(obj)
    me.materials.append(mat_front)
    me.materials.append(mat_back)
    for p in me.polygons:
        p.use_smooth = True
    me.set_sharp_from_angle(angle=math.radians(40))
    pz.project_uv_front(obj, ("x", "z"))
    uv = me.uv_layers["UVMap"]
    for p in me.polygons:                                   # dorso: v espejado (se lee "STOP", no espejado)
        if p.material_index == 0 and p.normal.y > 0:
            for li in p.loop_indices:
                uv.data[li].uv.y = 1.0 - uv.data[li].uv.y
    return obj


def rod(name, p0, p1, radius, mat, segs=6):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    o = pz.cylinder(name, radius, d.length, loc=(p0 + p1) / 2, rot=(0, 0, 0), mat=mat, segs=segs, smooth=False)
    o.rotation_euler = d.to_track_quat("Z", "X").to_euler()
    return o


def concrete_chunk(mat):
    """Trozo de la base de concreto: perfil de revolución irregular alrededor del caño, sacudido al azar."""
    prof = [(0.045, -0.365), (0.085, -0.345), (0.108, -0.300), (0.112, -0.245), (0.100, -0.200),
            (0.072, -0.172), (0.034, -0.163)]
    o = pz.lathe("concreto", prof, loc=(0, 0, 0), rot=(0, 90, 0), mat=mat, segs=7, smooth=False)
    # lathe con rot (0,90,0): z local -> -X... corregimos con la posición real luego del transform
    rnd = random.Random(4)
    for v in o.data.vertices:
        k = 0.35 if v.co.z > -0.168 else 1.0          # el anillo por donde entra el caño casi no se mueve
        v.co.x += rnd.uniform(-0.016, 0.016) * k
        v.co.y += rnd.uniform(-0.016, 0.016) * k
        v.co.z += rnd.uniform(-0.010, 0.010) * k
    return o


def build():
    pz.reset()
    M = materials()
    parts = []
    # --- caño galvanizado
    parts.append(pz.cylinder("cano", R_POLE, X_POLE1 - X_POLE0, loc=((X_POLE0 + X_POLE1) / 2, 0, 0),
                             mat=M["pipe"], segs=10))
    # agujeros del poste (tramo visible entre cinta y señal, a ambos lados)
    for x in (0.150, 0.200, 0.250):
        parts.append(pz.box("agujero", (0.011, 2 * R_POLE + 0.0012, 0.010), loc=(x, 0, 0), mat=M["hole"]))
    # tapa superior del caño, apenas visible detrás de la señal
    # --- cinta negra: espiral de vueltas superpuestas (perfil dentado)
    prof = []
    z, step = 0.0, 0.0375
    L = X_TAPE1 - X_TAPE0
    while z < L - 1e-4:
        prof += [(R_POLE + 0.0048, z), (R_POLE + 0.0030, min(z + step - 0.004, L))]
        z += step
    prof = [(R_POLE + 0.0005, 0.0)] + prof + [(R_POLE + 0.0005, L)]
    parts.append(pz.lathe("cinta", prof, loc=(X_TAPE0, 0, 0), rot=(0, 90, 0), mat=M["tape"], segs=8, smooth=False))
    # punta de cinta suelta
    parts.append(pz.box("cinta_punta", (0.030, 0.003, 0.016), loc=(X_TAPE1 - 0.012, -(R_POLE + 0.0055), 0.006),
                        rot=(0, 0, 8), mat=M["tape"]))
    # --- concreto + varillas
    ch = concrete_chunk(M["concrete"])
    parts.append(ch)
    parts.append(rod("varilla1", (-0.30, 0.01, 0.04), (-0.385, 0.03, 0.175), 0.0075, M["rebar"]))
    parts.append(rod("varilla2", (-0.28, -0.03, -0.03), (-0.33, -0.10, -0.165), 0.0075, M["rebar"]))
    parts.append(rod("varilla3a", (-0.32, 0.03, -0.01), (-0.43, 0.09, -0.03), 0.0075, M["rebar"]))
    parts.append(rod("varilla3b", (-0.43, 0.09, -0.03), (-0.47, 0.10, -0.085), 0.0075, M["rebar"]))
    # --- señal
    parts.append(sign_plate(M["decal"], M["alu"]))
    # --- abrazaderas en U: banda alrededor del caño + silla + 4 bulones (cabeza al frente, tuerca atrás)
    for bx in BOLT_X:
        parts.append(pz.cylinder("abrazadera", R_POLE + 0.0035, 0.020, loc=(bx, 0, 0), mat=M["clamp"], segs=10))
        parts.append(pz.box("silla", (0.022, 0.005, 0.098), loc=(bx, SIGN_Y + SIGN_T / 2 + 0.0022, 0),
                            mat=M["clamp"], bevel=0.0015))
        for bz in (-BOLT_Z, BOLT_Z):
            off = bend(bx - SIGN_CX, bz)
            yf = SIGN_Y - SIGN_T / 2 + off
            parts.append(pz.cylinder("bulon", 0.0115, 0.006, loc=(bx, yf - 0.0025, bz), rot=(90, 0, 0),
                                     mat=M["bolt"], segs=8, r2=0.0075, smooth=False))
            parts.append(pz.cylinder("tuerca", 0.0085, 0.008, loc=(bx, SIGN_Y + SIGN_T / 2 + 0.0085, bz),
                                     rot=(90, 0, 0), mat=M["bolt"], segs=6, smooth=False))
    return parts


HOLD = dict(grip_offset=0.0, hold_rot=(-10, -50, 30))


def main(hold=None):
    parts = build()
    model = pz.finish(ID, parts, tex_size=256)
    pz.previews(model, ID, **(hold or HOLD))
    return model


if __name__ == "__main__":
    main()
