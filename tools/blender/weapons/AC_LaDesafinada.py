"""AC_LaDesafinada: guitarra eléctrica + hoja de hacha de bombero (Arsenal de Chatarra).

Largo total ~1,04 m, a dos manos, se agarra por el mástil (origen = mano principal, justo
después de la cejuela). Pala de 6 clavijas en línea hacia -X, mástil de arce con diapasón
oscuro (trastes y marcadores en un calco), cuerpo doble cutaway con acabado sunburst hacia +X,
golpeador crema, 2 pastillas negras, puente cromado y 3 perillas. En el borde exterior del
cuerpo (+X, apenas inclinada hacia +Z) una abrazadera de acero atornillada sujeta una hoja de
hacha de bombero con filo curvo pulido y sangre. Grieta en el golpeador.

Frente de la guitarra = -Y (lo que ven la vista 3/4, la silueta y el ícono).

Uso: python3 tools/blender/weapons/AC_LaDesafinada.py
"""
import math
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import bpy  # noqa: E402,F401
from mathutils import Matrix, Vector  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

ID = "AC_LaDesafinada"

# ------------------------------------------------------------------ medidas
NUT_X = -0.05            # cejuela
HEAD_END = -0.236        # punta de la pala
BODY_OFF = 0.24          # el contorno del cuerpo empieza (punta de cuernos) en este X
NECK_END = 0.40          # el talón del mástil entra en el cuerpo hasta aquí
NECK_W0, NECK_W1 = 0.044, 0.057   # ancho del mástil en la cejuela / en el cuerpo
BODY_T = 0.045           # espesor del cuerpo
BF = -BODY_T / 2         # cara frontal del cuerpo (Y)
TILT = 20.0              # inclinación de la hoja hacia +Z (grados)
ANCHOR = (0.65, 0.035)   # origen local de la hoja (x, z)
BLADE_R = 0.18           # radio del filo curvo desde ANCHOR


# ------------------------------------------------------------- materiales
def base_link(m):
    """Devuelve el link RGB base -> mezcla de mugre de un pz.mat."""
    for lk in m.node_tree.links:
        if lk.from_node.type == "RGB" and lk.to_node.type == "MIX" and lk.to_node.blend_type == "MULTIPLY":
            return lk
    raise RuntimeError("no encontré el color base")


def tame(m, bright=0.0):
    """pz.mat suma dirt*0.18 de brillo lineal y lava los oscuros; lo bajamos."""
    for n in m.node_tree.nodes:
        if n.type == "BRIGHTCONTRAST":
            n.inputs["Bright"].default_value = bright
    return m


def radial_mask(nt, center, radii):
    """Socket escalar = distancia elíptica normalizada en XZ desde center (coords de objeto)."""
    L = nt.links
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sub = nt.nodes.new("ShaderNodeVectorMath")
    sub.operation = "SUBTRACT"
    sub.inputs[1].default_value = center
    L.new(coord.outputs["Object"], sub.inputs[0])
    mul = nt.nodes.new("ShaderNodeVectorMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = (1 / radii[0], 0.0, 1 / radii[1])
    L.new(sub.outputs[0], mul.inputs[0])
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    L.new(mul.outputs[0], ln.inputs[0])
    return ln.outputs["Value"]


def sunburst(m, center, radii, stops):
    """Reemplaza el color base de `m` por un degradé radial (sunburst)."""
    nt = m.node_tree
    lk = base_link(m)
    dst = lk.to_socket
    nt.links.remove(lk)
    d = radial_mask(nt, center, radii)
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.interpolation = "EASE"
    while len(cr.elements) < len(stops):
        cr.elements.new(0.5)
    for el, (pos, col) in zip(cr.elements, stops):
        el.position = pos
        el.color = (*col, 1)
    nt.links.new(d, ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], dst)
    return m


def overlay(m, color, fac_socket_builder):
    """Mezcla `color` encima del color final de `m` según un factor 0..1."""
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    prev = bsdf.inputs["Base Color"].links[0].from_socket
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    nt.links.new(fac_socket_builder(nt), mx.inputs["Factor"])
    nt.links.new(prev, mx.inputs["A"])
    mx.inputs["B"].default_value = (*color, 1)
    nt.links.new(mx.outputs["Result"], bsdf.inputs["Base Color"])
    return m


def add_splat(m, color, amount, scale, seed, lo=.38, hi=.78, mask=None):
    """Manchas (sangre, óxido) encima del color de `m`, opcionalmente limitadas por una máscara."""
    def build(nt):
        L = nt.links
        coord = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Location"].default_value = (seed, seed * .7, seed * 1.3)
        L.new(coord.outputs["Object"], mp.inputs["Vector"])
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = scale
        nz.inputs["Detail"].default_value = 8
        nz.inputs["Roughness"].default_value = .65
        L.new(mp.outputs["Vector"], nz.inputs["Vector"])
        src = nz.outputs["Fac"]
        if mask is not None:
            mul = nt.nodes.new("ShaderNodeMath")
            mul.operation = "MULTIPLY"
            L.new(src, mul.inputs[0])
            L.new(mask(nt), mul.inputs[1])
            src = mul.outputs[0]
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        thr = hi - (hi - lo) * amount
        ramp.color_ramp.elements[0].position = thr
        ramp.color_ramp.elements[1].position = min(thr + .03, 1.0)
        L.new(src, ramp.inputs["Fac"])
        sep = nt.nodes.new("ShaderNodeSeparateColor")
        L.new(ramp.outputs["Color"], sep.inputs["Color"])
        return sep.outputs[0]
    return overlay(m, color, build)


def edge_band(center, r0, r1):
    """Máscara 0..1 que crece con la distancia (circular, XZ) a center entre r0 y r1."""
    def build(nt):
        d = radial_mask(nt, center, (1.0, 1.0))
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = r0
        mr.inputs["From Max"].default_value = r1
        mr.clamp = True
        nt.links.new(d, mr.inputs["Value"])
        return mr.outputs["Result"]
    return build


def fretboard_decal(path):
    """Calco del diapasón: palisandro oscuro, trastes plateados en su posición real y marcadores."""
    W, H = 1024, 64
    length = NECK_END - 0.005 - NUT_X
    scale_len = 0.648
    img = Image.new("RGB", (W, H), (62, 36, 22))
    dr = ImageDraw.Draw(img)
    # vetas
    for i in range(0, H, 5):
        dr.line([(0, i), (W, i + 2)], fill=(54, 31, 19), width=2)

    def px(d):
        return int(d / length * W)
    frets = [scale_len * (1 - 2 ** (-n / 12)) for n in range(0, 21)]
    for d in frets[1:]:
        if d < length:
            x = px(d)
            dr.rectangle([x - 2, 0, x + 1, H], fill=(178, 176, 168))
    for n in (3, 5, 7, 9, 15, 17, 19):
        if n < len(frets) and frets[n] < length:
            x = px((frets[n - 1] + frets[n]) / 2)
            dr.ellipse([x - 9, H / 2 - 9, x + 9, H / 2 + 9], fill=(232, 226, 210))
    x = px((frets[11] + frets[12]) / 2)
    for yy in (H * .27, H * .73):
        dr.ellipse([x - 8, yy - 8, x + 8, yy + 8], fill=(232, 226, 210))
    img.save(path)
    return path


def blade_xz(u, v):
    t = math.radians(TILT)
    return (ANCHOR[0] + u * math.cos(t) - v * math.sin(t), ANCHOR[1] + u * math.sin(t) + v * math.cos(t))


def hold_euler(d, toward_cam=0.5):
    """Euler (grados, XYZ) que apunta el arma (+X) hacia `d` y gira el frente (-Y) entre el
    costado derecho del personaje (-Y) y la cámara isométrica según toward_cam."""
    d = Vector(d).normalized()
    cam = Vector((0.612, -0.612, 0.5)).normalized()
    c = Vector((0, -1, 0)).lerp(cam, toward_cam)
    n = (c - c.dot(d) * d).normalized()
    y = -n
    z = d.cross(y)
    M = Matrix((d, y, z)).transposed()
    return tuple(round(math.degrees(a), 1) for a in M.to_euler("XYZ"))


# ------------------------------------------------------------------ modelo
def build():
    pz.reset()
    tmp = Path(tempfile.mkdtemp(prefix="desafinada_"))

    maple = tame(pz.mat("arce", (0.58, 0.36, 0.14), streaks=True, dirt=.3, seed=1.0), .01)
    board = pz.image_mat("diapason", fretboard_decal(tmp / "fretboard.png"))
    body_m = pz.mat("sunburst", (1, 1, 1), dirt=.22, scale=14, seed=2.0)
    sunburst(body_m, (0.53, 0, -0.005), (0.205, 0.165), [
        (0.00, (0.80, 0.42, 0.07)),
        (0.45, (0.72, 0.24, 0.03)),
        (0.68, (0.40, 0.06, 0.012)),
        (0.86, (0.07, 0.016, 0.005)),
        (1.00, (0.025, 0.009, 0.004)),
    ])
    tame(body_m, .0)
    add_splat(body_m, (0.16, 0.008, 0.006), .55, 30, 7.0, mask=edge_band((0.70, 0, 0.06), 0.13, 0.03))
    guard = tame(pz.mat("golpeador", (0.70, 0.64, 0.50), dirt=.3, seed=3.0), .02)
    black = tame(pz.mat("pastillas", (0.02, 0.02, 0.022), dirt=.2), .0)
    chrome = tame(pz.mat("cromo", pz.CHROME, dirt=.25, rust=.05, metal=.8, rough=.3), .03)
    knob_m = tame(pz.mat("perillas", (0.74, 0.70, 0.58), dirt=.2), .02)
    crack_m = tame(pz.mat("grieta", (0.012, 0.009, 0.007), dirt=.0), .0)
    clamp_m = tame(pz.mat("abrazadera", (0.20, 0.21, 0.22), rust=.35, dirt=.35, seed=4.0), .0)
    bolt_m = tame(pz.mat("bulones", (0.42, 0.42, 0.40), rust=.25, dirt=.3, seed=5.0), .0)
    blade_m = pz.mat("hoja", (0.20, 0.21, 0.22), rust=.22, dirt=.35, metal=.7, rough=.4, scale=24, seed=6.0)
    tame(blade_m, .0)
    acx, acz = ANCHOR
    overlay(blade_m, (0.90, 0.91, 0.92), edge_band((acx, 0, acz), BLADE_R - .042, BLADE_R - .032))
    add_splat(blade_m, (0.24, 0.010, 0.008), .55, 16, 9.0, mask=edge_band((acx, 0, acz), 0.08, 0.15))

    parts = []
    # --- pala (6 en línea, se ensancha hacia +Z como una Strat)
    head = [(NUT_X, -NECK_W0 / 2), (-0.09, -0.025), (-0.15, -0.027), (-0.20, -0.023), (-0.226, -0.013),
            (HEAD_END, 0.006), (-0.233, 0.030), (-0.217, 0.046), (-0.19, 0.052), (-0.14, 0.054),
            (-0.10, 0.055), (-0.078, 0.050), (-0.064, 0.036), (NUT_X, NECK_W0 / 2)]
    head_y = -0.017
    parts.append(pz.extrude("pala", head, 0.014, loc=(0, head_y, 0), mat=maple, bevel=.002))
    for i in range(6):
        x = -0.088 - i * 0.0255
        parts.append(pz.cylinder(f"poste{i}", .0055, .012, loc=(x, head_y - .007 - .006, .036),
                                 rot=(90, 0, 0), mat=chrome, segs=6))
        parts.append(pz.box(f"llave{i}", (.013, .007, .030), loc=(x, head_y + .007 + .0035, .057),
                            mat=chrome))
    # --- mástil de arce y diapasón
    neck = [(NUT_X - .012, -NECK_W0 / 2), (0.33, -NECK_W1 / 2), (NECK_END, -NECK_W1 / 2),
            (NECK_END, NECK_W1 / 2), (0.33, NECK_W1 / 2), (NUT_X - .012, NECK_W0 / 2)]
    parts.append(pz.extrude("mastil", neck, 0.022, loc=(0, -0.015, 0), mat=maple, bevel=.006))
    fb = [(NUT_X, -NECK_W0 / 2), (0.33, -NECK_W1 / 2), (NECK_END - .005, -NECK_W1 / 2),
          (NECK_END - .005, NECK_W1 / 2), (0.33, NECK_W1 / 2), (NUT_X, NECK_W0 / 2)]
    fbo = pz.extrude("diapason", fb, 0.006, loc=(0, -0.029, 0), mat=board)
    pz.project_uv_front(fbo, ("x", "z"))
    parts.append(fbo)
    parts.append(pz.box("cejuela", (.005, .008, NECK_W0), loc=(NUT_X, -0.030, 0), mat=knob_m))

    # --- cuerpo doble cutaway (contorno local u=0 en la punta de los cuernos)
    body_uv = [(0.450, 0.000), (0.446, 0.050), (0.430, 0.090), (0.400, 0.125), (0.360, 0.150),
               (0.310, 0.160), (0.260, 0.155), (0.220, 0.140), (0.180, 0.127), (0.140, 0.131),
               (0.100, 0.145), (0.060, 0.156), (0.025, 0.151), (0.000, 0.135), (0.005, 0.115),
               (0.030, 0.095), (0.060, 0.070), (0.090, 0.045), (0.092, 0.000), (0.088, -0.045),
               (0.075, -0.060), (0.055, -0.082), (0.040, -0.104), (0.035, -0.122), (0.046, -0.141),
               (0.075, -0.150), (0.120, -0.141), (0.170, -0.131), (0.220, -0.141), (0.270, -0.156),
               (0.320, -0.161), (0.370, -0.150), (0.410, -0.125), (0.435, -0.090), (0.447, -0.045)]
    body = [(BODY_OFF + u, v) for u, v in body_uv]
    parts.append(pz.extrude("cuerpo", body, BODY_T, mat=body_m, bevel=.006))

    # --- golpeador, pastillas, puente, perillas
    gy = BF - 0.0015
    guard_xz = [(0.345, -0.038), (0.362, -0.068), (0.405, -0.086), (0.460, -0.090), (0.508, -0.076),
                (0.536, -0.048), (0.546, -0.005), (0.540, 0.040), (0.518, 0.072), (0.475, 0.094),
                (0.420, 0.104), (0.376, 0.094), (0.352, 0.070), (0.345, 0.040)]
    parts.append(pz.extrude("golpeador", guard_xz, 0.003, loc=(0, gy, 0), mat=guard, bevel=.001))
    for i, x in enumerate((0.432, 0.505)):
        parts.append(pz.box(f"pastilla{i}", (.024, .008, .078), loc=(x, gy - .0015 - .004, 0.0),
                            mat=black, bevel=.003))
    parts.append(pz.box("puente", (.036, .009, .084), loc=(0.600, BF - .0045, 0.0), mat=chrome, bevel=.003))
    for i, (x, z) in enumerate(((0.545, -0.118), (0.585, -0.106), (0.620, -0.085))):
        parts.append(pz.cylinder(f"perilla{i}", .0115, .013, loc=(x, BF - .0065, z), rot=(90, 0, 0),
                                 mat=knob_m, segs=8, r2=.0095))
    # grieta: sobre el golpeador y su continuación sobre la madera
    def strip(pts, w):
        left, right = [], []
        for i, (x, z) in enumerate(pts):
            a = pts[max(i - 1, 0)]
            b = pts[min(i + 1, len(pts) - 1)]
            tx, tz = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(tx, tz) or 1
            nx, nz = -tz / ln * w / 2, tx / ln * w / 2
            left.append((x + nx, z + nz))
            right.append((x - nx, z - nz))
        return right + left[::-1]
    crack_g = [(0.474, -0.085), (0.466, -0.070), (0.477, -0.057), (0.463, -0.041), (0.472, -0.027),
               (0.462, -0.012)]
    parts.append(pz.extrude("grieta_g", strip(crack_g, .0055), 0.0008, loc=(0, gy - .0016, 0), mat=crack_m))
    crack_b = [(0.486, -0.152), (0.478, -0.130), (0.485, -0.110), (0.474, -0.086)]
    parts.append(pz.extrude("grieta_c", strip(crack_b, .006), 0.0008, loc=(0, BF - .0004, 0), mat=crack_m))

    # --- hoja de hacha + abrazadera atornillada al borde exterior
    blade_uv = [(0.0, -0.045), (0.075, -0.048), (0.110, -0.074)]
    R = BLADE_R
    for a in (-40, -20, 0, 20, 40):
        blade_uv.append((R * math.cos(math.radians(a)), R * math.sin(math.radians(a))))
    blade_uv += [(0.110, 0.074), (0.075, 0.048), (0.0, 0.045)]
    blade = [blade_xz(u, v) for u, v in blade_uv]
    parts.append(pz.extrude("hoja", blade, 0.012, mat=blade_m, taper_edge=[3, 4, 5, 6, 7]))
    cu0, cu1, ch = -0.010, 0.075, 0.112
    cx, cz = blade_xz((cu0 + cu1) / 2, 0)
    parts.append(pz.box("abrazadera", (cu1 - cu0, BODY_T + .007, ch), loc=(cx, 0, cz), rot=(0, -TILT, 0),
                        mat=clamp_m, bevel=.004))
    for i, (u, v) in enumerate(((0.014, -0.033), (0.014, 0.033), (0.055, 0.0))):
        x, z = blade_xz(u, v)
        for s in (-1, 1):
            parts.append(pz.cylinder(f"bulon{i}{s}", .0085, .006, loc=(x, s * (BODY_T / 2 + .0035 + .003), z),
                                     rot=(90, 30, 0), mat=bolt_m, segs=6, smooth=False))
    return parts


HOLD = dict(grip_offset=0.0, hold_rot=hold_euler((0.78, 0.0, 0.62), toward_cam=0.7))

if __name__ == "__main__":
    model = pz.finish(ID, build(), tex_size=256)
    print("[desafinada] hold", HOLD)
    pz.previews(model, ID, **HOLD)
