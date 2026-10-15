"""AC_Hachamazo: hacha de bombero + cabeza de mazo soldada (Arsenal de Chatarra).

Largo total ~0,92 m, a dos manos. Mango de fibra de vidrio amarillo con empuñadura de goma negra
estriada; dos abrazaderas cerca de la cabeza. Cabeza perpendicular al mango (plano XZ):
mazo de acero hacia +Z, hoja de hacha de bombero roja en abanico hacia -Z, cordones de soldadura
entre ambas y 2 bulones en el ojo.

Uso: python3 tools/blender/weapons/AC_Hachamazo.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import bpy  # noqa: E402,F401
import bmesh  # noqa: E402

ID = "AC_Hachamazo"

# ------------------------------------------------------------------ medidas
X_END = -0.085        # extremo inferior del mango (pomo de goma)
X_TOP = 0.835         # extremo superior del mango (asoma apenas del ojo)
HX = 0.785            # eje de la cabeza (centro del ojo) sobre X
EYE_W, EYE_D, EYE_H = 0.092, 0.060, 0.100     # ojo: ancho en X, espesor en Y, alto en Z
MAL_W, MAL_D, MAL_H = 0.112, 0.090, 0.165     # bloque de mazo (exagerado ~15% para leerse en juego)
R_HANDLE = 0.0205


# ------------------------------------------------------------- materiales
def add_splat(m, color, amount, scale, seed, lo=.38, hi=.78, mask=None):
    """Agrega una capa de manchas (pintura saltada, mugre, etc.) encima del color base de `m`.
    mask: función(nt) -> socket escalar 0..1 que limita dónde aparecen las manchas."""
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
        # la máscara reduce el ruido antes del umbral: menos manchas, pero opacas (no se "lavan")
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        L.new(src, mul.inputs[0])
        L.new(mask(nt), mul.inputs[1])
        src = mul.outputs[0]
    L.new(src, ramp.inputs["Fac"])
    fac = ramp.outputs["Color"]
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    L.new(fac, mx.inputs["Factor"])
    L.new(prev, mx.inputs["A"])
    mx.inputs["B"].default_value = (*color, 1)
    L.new(mx.outputs["Result"], bsdf.inputs["Base Color"])
    return m


def tame(m, bright=0.0):
    """pz.mat suma `dirt*0.18` de brillo lineal: levanta los negros y lava los colores saturados
    (la goma queda gris, el rojo rosado). Lo reducimos para conservar colores tipo Zomboid."""
    for n in m.node_tree.nodes:
        if n.type == "BRIGHTCONTRAST":
            n.inputs["Bright"].default_value = bright
    return m


def z_mask(z_full, z_zero):
    """Máscara según Z del objeto: 1 en z_full, 0 en z_zero (lineal, recortada)."""
    def build(nt):
        coord = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(coord.outputs["Object"], sep.inputs["Vector"])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = z_zero
        mr.inputs["From Max"].default_value = z_full
        mr.clamp = True
        nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
        return mr.outputs["Result"]
    return build


def x_mask(x_full, x_zero):
    def build(nt):
        coord = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(coord.outputs["Object"], sep.inputs["Vector"])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = x_zero
        mr.inputs["From Max"].default_value = x_full
        mr.clamp = True
        nt.links.new(sep.outputs["X"], mr.inputs["Value"])
        return mr.outputs["Result"]
    return build


def edge_wear(m, color, amount=1.0, dist=0.012):
    """Desgaste en aristas convexas (AO 'inside'): el metal brilla o la pintura salta en los bordes."""
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
    # cortar con ruido para que el desgaste sea irregular
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


def add_ripples(m, color, scale=70.0, amount=.55):
    """Ondas del cordón de soldadura (bandas a lo largo de X con distorsión)."""
    nt = m.node_tree
    L = nt.links
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    prev = bsdf.inputs["Base Color"].links[0].from_socket
    coord = nt.nodes.new("ShaderNodeTexCoord")
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type = "BANDS"
    wv.bands_direction = "X"
    wv.inputs["Scale"].default_value = scale
    wv.inputs["Distortion"].default_value = 1.5
    wv.inputs["Detail"].default_value = 2
    L.new(coord.outputs["Object"], wv.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = .35
    ramp.color_ramp.elements[1].position = .75
    L.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    k = nt.nodes.new("ShaderNodeMath")
    k.operation = "MULTIPLY"
    k.inputs[1].default_value = amount
    L.new(ramp.outputs["Color"], k.inputs[0])
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    L.new(k.outputs[0], mx.inputs["Factor"])
    L.new(prev, mx.inputs["A"])
    mx.inputs["B"].default_value = (*color, 1)
    L.new(mx.outputs["Result"], bsdf.inputs["Base Color"])
    return m


# ------------------------------------------------------------ geometría
def blade(name, levels, cols, mat_paint, mat_steel, rim_cols=(0, -1)):
    """Hoja en abanico construida por filas (desde el ojo hasta el filo).
    levels: [(z_centro, curva, mitad_atras, mitad_adelante, espesor), ...]; la curva baja el centro
    de la fila (filo convexo). cols: posiciones 0..1 de las columnas a lo ancho.
    La última franja (bisel del filo) y las columnas `rim_cols` son acero sin pintar; el resto, pintura."""
    bm = bmesh.new()
    nc = len(cols)
    rows_f, rows_b = [], []
    for z, curve, hb, hf, th in levels:
        rf, rb = [], []
        for s in cols:
            x = HX - hb + (hb + hf) * s
            zz = z - curve * (1 - (2 * s - 1) ** 2)
            rf.append(bm.verts.new((x, -th / 2, zz)))
            rb.append(bm.verts.new((x, th / 2, zz)))
        rows_f.append(rf)
        rows_b.append(rb)
    nl = len(levels)
    rims = {c % (nc - 1) for c in rim_cols}
    for r in range(nl - 1):
        edge_row = r == nl - 2
        for i in range(nc - 1):
            mi = 1 if (edge_row or (i in rims and r > 0)) else 0
            bm.faces.new((rows_f[r][i], rows_f[r][i + 1], rows_f[r + 1][i + 1], rows_f[r + 1][i])).material_index = mi
            bm.faces.new((rows_b[r][i + 1], rows_b[r][i], rows_b[r + 1][i], rows_b[r + 1][i + 1])).material_index = mi
        # lados (canto de la hoja: acero)
        bm.faces.new((rows_f[r + 1][0], rows_b[r + 1][0], rows_b[r][0], rows_f[r][0])).material_index = 1
        bm.faces.new((rows_f[r][-1], rows_b[r][-1], rows_b[r + 1][-1], rows_f[r + 1][-1])).material_index = 1
    for i in range(nc - 1):
        bm.faces.new((rows_f[0][i + 1], rows_f[0][i], rows_b[0][i], rows_b[0][i + 1])).material_index = 1
        bm.faces.new((rows_f[-1][i], rows_f[-1][i + 1], rows_b[-1][i + 1], rows_b[-1][i])).material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    me.materials.append(mat_paint)
    me.materials.append(mat_steel)
    return obj


DRIED = (0.10, 0.010, 0.006)   # sangre seca (más oscura que pz.BLOOD, se lee sobre el rojo)


def materials():
    """Paleta tipo Zomboid: colores sólidos algo desaturados y oscuros (valores lineales)."""
    M = {}
    y = tame(pz.mat("fibra_amarilla", (0.70, 0.42, 0.022), dirt=.22, rough=.45, scale=9, seed=1), .0)
    add_splat(y, (0.11, 0.075, 0.03), .45, 14, 3.0, mask=x_mask(0.16, 0.42))        # mugre de manos
    add_splat(y, (0.30, 0.20, 0.03), .35, 40, 12.0)                                  # rayones/opacidad
    add_splat(y, pz.BLOOD, .22, 22, 8.0, mask=x_mask(0.74, 0.50))                   # gotas cerca de la cabeza
    M["yellow"] = y
    M["rubber"] = tame(pz.mat("goma", (0.016, 0.016, 0.018), dirt=.35, rough=.9, scale=30, seed=2), .004)
    st = tame(pz.mat("acero_mazo", (0.24, 0.245, 0.255), rust=.42, dirt=.4, rough=.5, scale=20, seed=3), .01)
    add_splat(st, (0.26, 0.085, 0.025), .75, 16, 13.0, mask=z_mask(0.06, 0.15))     # óxido junto a la soldadura
    add_splat(st, DRIED, .45, 30, 4.0, mask=z_mask(0.215, 0.18))                    # sangre cerca de la cara
    edge_wear(st, (0.52, 0.53, 0.54), .9)
    M["steel"] = st
    fc = tame(pz.mat("cara_golpe", (0.34, 0.345, 0.35), rust=.15, dirt=.35, rough=.4, scale=40, seed=10), .0)
    add_splat(fc, DRIED, .35, 40, 7.0)
    M["face"] = fc
    ey = tame(pz.mat("acero_ojo", (0.095, 0.097, 0.10), rust=.50, dirt=.4, rough=.6, scale=26, seed=4), .005)
    edge_wear(ey, (0.35, 0.35, 0.36), .8)
    add_splat(ey, (0.24, 0.08, 0.025), .45, 20, 15.0)
    M["eye"] = ey
    rd = tame(pz.mat("rojo_hoja", (0.40, 0.020, 0.014), rust=.15, dirt=.3, rough=.55, scale=16, seed=5), .0)
    add_splat(rd, (0.26, 0.26, 0.27), .28, 30, 6.0)                                 # pintura saltada
    edge_wear(rd, (0.40, 0.40, 0.41), 1.0)
    add_splat(rd, DRIED, .85, 16, 9.0, mask=z_mask(-0.17, -0.07))                  # sangre seca hacia el filo
    M["red"] = rd
    ed = tame(pz.mat("filo", (0.47, 0.48, 0.49), rust=.08, dirt=.18, rough=.3, scale=30, seed=6), .0)
    add_splat(ed, pz.BLOOD, .75, 18, 2.0, mask=z_mask(-0.20, -0.12))
    add_splat(ed, DRIED, .45, 40, 5.0, mask=z_mask(-0.21, -0.15))
    M["edge"] = ed
    wd = tame(pz.mat("soldadura", (0.20, 0.155, 0.10), rust=.30, dirt=.5, rough=.8, scale=120, seed=7), .0)
    add_ripples(wd, (0.045, 0.035, 0.025), 90, .8)
    M["weld"] = wd
    M["clamp"] = tame(pz.mat("abrazadera", (0.46, 0.47, 0.49), rust=.2, dirt=.35, rough=.4, scale=40, seed=8), .01)
    M["bolt"] = tame(pz.mat("bulon", (0.50, 0.48, 0.42), rust=.3, dirt=.3, scale=40, seed=9), .01)
    return M


def build():
    pz.reset()
    # Nota: los colores se hornean como color difuso; `metal` > 0 oscurece el horneado (el pase
    # de color difuso de Cycles excluye la parte metálica), así que los aceros usan metal=0.
    M = materials()
    parts = []
    # --- mango de fibra (ovalado: más alto en Z que ancho en Y). Empieza dentro de la goma.
    x0 = 0.12
    h = pz.cylinder("mango", R_HANDLE, X_TOP - x0, loc=((X_TOP + x0) / 2, 0, 0),
                    mat=M["yellow"], segs=10, r2=R_HANDLE * 1.05)
    h.scale = (1.0, 0.80, 1.0)
    parts.append(h)

    # --- empuñadura de goma estriada (perfil de revolución sobre +X)
    prof = [(0.010, 0.0), (0.0255, 0.003), (0.0278, 0.013), (0.0248, 0.024)]
    z = 0.024
    for _ in range(9):
        prof += [(0.0256, z + 0.007), (0.0229, z + 0.022)]
        z += 0.022
    prof += [(0.0218, z + 0.012), (0.0207, z + 0.024)]
    g = pz.lathe("empunadura", prof, loc=(X_END, 0, 0), mat=M["rubber"], segs=8, smooth=False)
    g.scale = (1.0, 0.84, 1.0)
    parts.append(g)

    # --- abrazaderas metálicas cerca de la cabeza
    for x in (0.612, 0.672):
        c = pz.cylinder("abrazadera", R_HANDLE * 1.20, 0.017, loc=(x, 0, 0), mat=M["clamp"], segs=10)
        c.scale = (1.0, 0.84, 1.0)
        parts.append(c)
        parts.append(pz.box("tornillo_abr", (0.015, 0.016, 0.011), loc=(x, 0, R_HANDLE * 1.20 + 0.003),
                            mat=M["clamp"], bevel=0.002))

    # --- ojo (pieza central que abraza el mango) con 2 bulones pasantes
    parts.append(pz.box("ojo", (EYE_W, EYE_D, EYE_H), loc=(HX, 0, 0), mat=M["eye"], bevel=0.010))
    for dx in (-0.024, 0.024):
        parts.append(pz.cylinder("bulon", 0.0115, EYE_D + 0.012, loc=(HX + dx, 0, 0.006), rot=(90, 0, 0),
                                 mat=M["bolt"], segs=6, smooth=False))

    # --- bloque de mazo hacia +Z
    z0 = EYE_H / 2 + 0.006
    parts.append(pz.box("mazo", (MAL_W, MAL_D, MAL_H), loc=(HX, 0, z0 + MAL_H / 2), mat=M["steel"], bevel=0.012))
    parts.append(pz.box("cara_golpe", (MAL_W - .018, MAL_D - .018, 0.012),
                        loc=(HX, 0, z0 + MAL_H + 0.004), mat=M["face"], bevel=0.003))

    # --- cordones de soldadura (mazo-ojo y ojo-hoja)
    parts.append(pz.box("sold_sup", (MAL_W + 0.006, MAL_D + 0.005, 0.017), loc=(HX, 0, z0 - 0.002),
                        mat=M["weld"], bevel=0.006))
    parts.append(pz.box("sold_inf", (EYE_W + 0.005, EYE_D + 0.006, 0.015), loc=(HX, 0, -EYE_H / 2 - 0.003),
                        mat=M["weld"], bevel=0.005))

    # --- hoja de hacha de bombero en abanico hacia -Z (cara roja, filo y canto de acero)
    levels = [
        # z,      curva, mitad atrás, mitad adelante, espesor
        (-0.044, 0.000, 0.037, 0.037, 0.038),
        (-0.095, 0.004, 0.039, 0.044, 0.030),
        (-0.138, 0.010, 0.055, 0.064, 0.021),
        (-0.173, 0.020, 0.080, 0.093, 0.013),
        (-0.200, 0.030, 0.091, 0.106, 0.003),
    ]
    parts.append(blade("hoja", levels, (0.0, 0.085, 0.5, 0.915, 1.0), M["red"], M["edge"]))
    return parts


def main(hold=None):
    parts = build()
    model = pz.finish(ID, parts, tex_size=256)
    pz.previews(model, ID, **(hold or HOLD))
    return model


HOLD = dict(grip_offset=0.0, hold_rot=(-15, -52, 35))

if __name__ == "__main__":
    main()
