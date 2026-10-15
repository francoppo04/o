"""Librería común para modelar armas de Project Zomboid con bpy (Blender como módulo).

Convenciones de cada arma (todas en metros, escala real):
  * El punto de agarre de la mano principal está en el origen (0, 0, 0).
  * El arma se extiende a lo largo de +X (mango hacia -X, cabeza hacia +X).
  * Las hojas/caras planas quedan en el plano XZ (miran hacia ±Y); +Z es "arriba" del arma.

Flujo típico de un script de arma (ver tools/blender/weapons/*.py):
    import pzlib as pz
    pz.reset()
    m = pz.mat("Acero", pz.STEEL, rust=.3)
    head = pz.box("Cabeza", size=(.12, .05, .2), loc=(.8, 0, 0), mat=m)
    ...
    model = pz.finish("AC_Hachamazo", parts)   # une, hornea textura, exporta FBX + PNG
    pz.previews(model, "AC_Hachamazo")         # renders para revisar

Salidas (en art/<Nombre>/): <Nombre>.fbx, <Nombre>.png (textura), preview_*.png, icon_*.png
"""
import math
import os
from pathlib import Path

import bpy  # noqa: I001  (bpy debe importarse antes que bmesh/mathutils)
import bmesh
from mathutils import Euler, Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "art"

# --------------------------------------------------------------- paleta base
STEEL = (0.55, 0.57, 0.60)
STEEL_DARK = (0.22, 0.23, 0.25)
CHROME = (0.78, 0.80, 0.83)
IRON = (0.12, 0.12, 0.13)
RUST = (0.33, 0.14, 0.05)
WOOD = (0.42, 0.24, 0.11)
WOOD_LIGHT = (0.68, 0.48, 0.28)
RUBBER = (0.03, 0.03, 0.035)
DUCT = (0.50, 0.52, 0.54)
CLOTH = (0.80, 0.75, 0.62)
RED = (0.55, 0.04, 0.04)
FIRE_RED = (0.62, 0.05, 0.04)
YELLOW = (0.85, 0.62, 0.06)
WHITE = (0.85, 0.84, 0.80)
BLOOD = (0.22, 0.01, 0.01)
CONCRETE = (0.50, 0.48, 0.44)
BRASS = (0.70, 0.52, 0.16)


# ------------------------------------------------------------------ escena
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 24
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"
    return sc


def _link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def _mesh_obj(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return _link(bpy.data.objects.new(name, me))


def _place(obj, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), mat=None, bevel=0.0, smooth=False):
    obj.location = loc
    obj.rotation_euler = Euler([math.radians(a) for a in rot])
    obj.scale = scale
    if mat is not None:
        obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 1
        mod.limit_method = "ANGLE"
    for p in obj.data.polygons:
        p.use_smooth = smooth
    if smooth:
        obj.data.set_sharp_from_angle(angle=math.radians(40))
    return obj


# ---------------------------------------------------------------- primitivas
def box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, bevel=0.0):
    """Caja de tamaño (x, y, z) en metros, centrada en loc."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    return _place(_mesh_obj(name, bm), loc, rot, mat=mat, bevel=bevel)


def cylinder(name, radius, length, loc=(0, 0, 0), rot=(0, 90, 0), mat=None, segs=10, r2=None, smooth=True, cap=True):
    """Cilindro (o cono truncado si r2) de eje Z local; por defecto rotado para quedar sobre X."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=segs, radius1=radius,
                          radius2=radius if r2 is None else r2, depth=length)
    return _place(_mesh_obj(name, bm), loc, rot, mat=mat, smooth=smooth)


def sphere(name, radius, loc=(0, 0, 0), mat=None, segs=8, rings=6, scale=(1, 1, 1), smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=radius)
    return _place(_mesh_obj(name, bm), loc, scale=scale, mat=mat, smooth=smooth)


def lathe(name, profile, loc=(0, 0, 0), rot=(0, 90, 0), mat=None, segs=10, smooth=True):
    """Sólido de revolución: profile = [(radio, z), ...] de abajo hacia arriba, eje Z local."""
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        ring = []
        for i in range(segs):
            a = 2 * math.pi * i / segs
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        for i in range(segs):
            j = (i + 1) % segs
            bm.faces.new((a[i], a[j], b[j], b[i]))
    if profile[0][0] > 1e-4:
        bm.faces.new(list(reversed(rings[0])))
    if profile[-1][0] > 1e-4:
        bm.faces.new(rings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    return _place(_mesh_obj(name, bm), loc, rot, mat=mat, smooth=smooth)


def extrude(name, outline, thickness, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, bevel=0.0, plane="XZ", taper_edge=None):
    """Prisma a partir de un contorno 2D [(u, v), ...] (antihorario), extruido `thickness` centrado.
    plane="XZ": u->X, v->Z, espesor en Y (hojas, placas). plane="XY": espesor en Z.
    taper_edge: lista de índices del contorno cuyo espesor se reduce a ~0 (filo afilado)."""
    bm = bmesh.new()
    n = len(outline)
    h = thickness / 2
    front, back = [], []
    for i, (u, v) in enumerate(outline):
        t = h * (0.08 if taper_edge and i in taper_edge else 1.0)
        if plane == "XZ":
            front.append(bm.verts.new((u, -t, v)))
            back.append(bm.verts.new((u, t, v)))
        else:
            front.append(bm.verts.new((u, v, -t)))
            back.append(bm.verts.new((u, v, t)))
    f1 = bm.faces.new(front)
    f2 = bm.faces.new(list(reversed(back)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((front[i], front[j], back[j], back[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # triangula las tapas para contornos cóncavos
    bmesh.ops.triangulate(bm, faces=[f for f in (f1, f2) if f.is_valid])
    return _place(_mesh_obj(name, bm), loc, rot, mat=mat, bevel=bevel)


def ring_points(cx, cy, r, n, start=0.0):
    return [(cx + r * math.cos(start + 2 * math.pi * i / n), cy + r * math.sin(start + 2 * math.pi * i / n)) for i in range(n)]


# --------------------------------------------------------------- materiales
def _nodes(m):
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return nt, bsdf


def mat(name, color, rust=0.0, dirt=0.25, rough=0.7, metal=0.0, scale=18.0, streaks=False, blood=0.0, seed=0.0):
    """Material procedural horneable.
    rust: 0-1 cantidad de manchas de óxido. dirt: variación/mugre. streaks: vetas (madera/cepillado).
    blood: 0-1 salpicaduras de sangre seca."""
    m = bpy.data.materials.new(name)
    nt, bsdf = _nodes(m)
    L = nt.links
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Location"].default_value = (seed * 3.1, seed * 1.7, seed * 2.3)
    L.new(coord.outputs["Object"], mapping.inputs["Vector"])
    if streaks:
        mapping.inputs["Scale"].default_value = (1.0, 14.0, 14.0)
    base = nt.nodes.new("ShaderNodeRGB")
    base.outputs[0].default_value = (*color, 1)
    col = base.outputs[0]

    # variación / mugre
    n1 = nt.nodes.new("ShaderNodeTexNoise")
    n1.inputs["Scale"].default_value = scale
    n1.inputs["Detail"].default_value = 6
    L.new(mapping.outputs["Vector"], n1.inputs["Vector"])
    dark = nt.nodes.new("ShaderNodeMix")
    dark.data_type = "RGBA"
    dark.blend_type = "MULTIPLY"
    dark.inputs["Factor"].default_value = dirt
    L.new(col, dark.inputs["A"])
    L.new(n1.outputs["Color"], dark.inputs["B"])
    col = dark.outputs["Result"]
    bri = nt.nodes.new("ShaderNodeBrightContrast")
    bri.inputs["Bright"].default_value = dirt * 0.18
    L.new(col, bri.inputs["Color"])
    col = bri.outputs["Color"]

    def splat(amount, color2, sc, lo, hi, seed_off):
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = sc
        nz.inputs["Detail"].default_value = 8
        nz.inputs["Roughness"].default_value = .65
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Location"].default_value = (seed_off, seed_off * .7, seed_off * 1.3)
        L.new(mapping.outputs["Vector"], mp.inputs["Vector"])
        L.new(mp.outputs["Vector"], nz.inputs["Vector"])
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        thr = hi - (hi - lo) * amount
        ramp.color_ramp.elements[0].position = thr
        ramp.color_ramp.elements[1].position = min(thr + 0.04, 1.0)
        L.new(nz.outputs["Fac"], ramp.inputs["Fac"])
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        L.new(ramp.outputs["Color"], mx.inputs["Factor"])
        c2 = nt.nodes.new("ShaderNodeRGB")
        c2.outputs[0].default_value = (*color2, 1)
        return mx, c2

    if rust > 0:
        mx, c2 = splat(rust, RUST, scale * .45, .38, .78, 5.0 + seed)
        L.new(col, mx.inputs["A"])
        L.new(c2.outputs[0], mx.inputs["B"])
        col = mx.outputs["Result"]
    if blood > 0:
        mx, c2 = splat(blood, BLOOD, scale * .9, .45, .82, 11.0 + seed)
        L.new(col, mx.inputs["A"])
        L.new(c2.outputs[0], mx.inputs["B"])
        col = mx.outputs["Result"]
    L.new(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    m["pz_color"] = list(color)
    return m


def image_mat(name, image_path, uv="UVMap", rough=0.7):
    """Material con imagen (calcos: texto STOP, golpeador, etc.). Usa el UV `uv` original."""
    m = bpy.data.materials.new(name)
    nt, bsdf = _nodes(m)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(image_path))
    uvn = nt.nodes.new("ShaderNodeUVMap")
    uvn.uv_map = uv
    nt.links.new(uvn.outputs["UV"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    return m


def project_uv_front(obj, axes=("x", "z")):
    """UV planar simple (para calcos) usando las coordenadas locales normalizadas."""
    me = obj.data
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers["UVMap"]
    co = [v.co for v in me.vertices]
    ia, ib = ("xyz".index(axes[0]), "xyz".index(axes[1]))
    amin, amax = min(c[ia] for c in co), max(c[ia] for c in co)
    bmin, bmax = min(c[ib] for c in co), max(c[ib] for c in co)
    for loop in me.loops:
        c = me.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = ((c[ia] - amin) / (amax - amin or 1), (c[ib] - bmin) / (bmax - bmin or 1))


# ----------------------------------------------------- unir, hornear, exportar
def _apply_all(objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        for mod in list(o.modifiers):
            bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def tri_count(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def finish(name, parts, tex_size=256, ao=True, export=True):
    """Une las partes, crea UV atlas, hornea color (+AO) a una textura y exporta FBX + PNG.
    Devuelve el objeto final con un único material texturizado."""
    out = ART / name
    out.mkdir(parents=True, exist_ok=True)
    for p in parts:
        if not p.data.uv_layers:
            p.data.uv_layers.new(name="UVMap")
    _apply_all(parts)
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = name
    me = obj.data
    # atlas UV
    atlas = me.uv_layers.new(name="atlas")
    me.uv_layers.active = atlas
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.02, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.pack_islands(margin=0.01, rotate=True)
    bpy.ops.object.mode_set(mode="OBJECT")

    sc = bpy.context.scene
    sc.cycles.samples = 16
    imgs = {}
    for kind in (["DIFFUSE", "AO"] if ao else ["DIFFUSE"]):
        img = bpy.data.images.new(f"{name}_{kind}", tex_size, tex_size, alpha=False)
        for m in me.materials:
            nt = m.node_tree
            node = nt.nodes.get("__bake") or nt.nodes.new("ShaderNodeTexImage")
            node.name = "__bake"
            node.image = img
            uvn = nt.nodes.get("__bakeuv") or nt.nodes.new("ShaderNodeUVMap")
            uvn.name = "__bakeuv"
            uvn.uv_map = "atlas"
            nt.links.new(uvn.outputs["UV"], node.inputs["Vector"])
            for n in nt.nodes:
                n.select = False
            node.select = True
            nt.nodes.active = node
        sc.render.bake.margin = 4
        if kind == "DIFFUSE":
            sc.render.bake.use_pass_direct = False
            sc.render.bake.use_pass_indirect = False
            sc.render.bake.use_pass_color = True
            bpy.ops.object.bake(type="DIFFUSE")
        else:
            sc.cycles.samples = 64
            bpy.ops.object.bake(type="AO")
        imgs[kind] = img

    # combinar color * AO suave y guardar PNG 8 bits
    px = list(imgs["DIFFUSE"].pixels)
    if ao:
        aop = list(imgs["AO"].pixels)
        for i in range(0, len(px), 4):
            k = 0.55 + 0.45 * aop[i]
            px[i] *= k
            px[i + 1] *= k
            px[i + 2] *= k
    final = bpy.data.images.new(f"{name}_tex", tex_size, tex_size, alpha=False)
    final.pixels = px
    final.filepath_raw = str(out / f"{name}.png")
    final.file_format = "PNG"
    final.save()

    # material final único
    fm = bpy.data.materials.new(name)
    nt, bsdf = _nodes(fm)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(out / f"{name}.png"))
    tex.interpolation = "Linear"
    uvn = nt.nodes.new("ShaderNodeUVMap")
    uvn.uv_map = "atlas"
    nt.links.new(uvn.outputs["UV"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.85
    me.materials.clear()
    me.materials.append(fm)
    for uv in [u for u in me.uv_layers if u.name != "atlas"]:
        me.uv_layers.remove(uv)
    me.uv_layers["atlas"].name = "UVMap"
    uvn.uv_map = "UVMap"

    if export:
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.ops.export_scene.fbx(filepath=str(out / f"{name}.fbx"), use_selection=True,
                                 global_scale=1.0, apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL",
                                 axis_forward="-Z", axis_up="Y", object_types={"MESH"},
                                 mesh_smooth_type="FACE", use_mesh_modifiers=True, path_mode="STRIP")
    print(f"[pzlib] {name}: {tri_count(obj)} triangulos, textura {tex_size}px -> {out}")
    return obj


# ------------------------------------------------------------- vistas previas
def _cam(name, loc, target, ortho_scale=None, lens=50):
    cam = bpy.data.cameras.new(name)
    if ortho_scale:
        cam.type = "ORTHO"
        cam.ortho_scale = ortho_scale
    else:
        cam.lens = lens
    o = _link(bpy.data.objects.new(name, cam))
    o.location = loc
    d = Vector(target) - Vector(loc)
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = o
    return o


def _world(strength=1.0, color=(0.55, 0.57, 0.62)):
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*color, 1)
    bg.inputs["Strength"].default_value = strength
    bpy.context.scene.world = w


def _sun(rot=(50, 10, 35), energy=3.0):
    s = bpy.data.lights.new("sol", "SUN")
    s.energy = energy
    s.angle = math.radians(8)
    o = _link(bpy.data.objects.new("sol", s))
    o.rotation_euler = Euler([math.radians(a) for a in rot])
    return o


def _render(path, w, h, samples=24, transparent=True):
    sc = bpy.context.scene
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    sc.cycles.samples = samples
    sc.render.film_transparent = transparent
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def _bounds(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def _ground(size=6.0, tile=1.0):
    """Suelo tipo Zomboid: pasto con baldosas tenues de 1 m."""
    m = bpy.data.materials.new("suelo")
    nt, bsdf = _nodes(m)
    coord = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3.0
    noise.inputs["Detail"].default_value = 10
    nt.links.new(coord.outputs["Object"], noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.10, 0.16, 0.06, 1)
    ramp.color_ramp.elements[1].color = (0.24, 0.30, 0.12, 1)
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    checker = nt.nodes.new("ShaderNodeTexChecker")
    checker.inputs["Scale"].default_value = size / tile
    checker.inputs["Color1"].default_value = (1, 1, 1, 1)
    checker.inputs["Color2"].default_value = (.9, .9, .9, 1)
    nt.links.new(coord.outputs["Generated"], checker.inputs["Vector"])
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    nt.links.new(ramp.outputs["Color"], mul.inputs["A"])
    nt.links.new(checker.outputs["Color"], mul.inputs["B"])
    nt.links.new(mul.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 1.0
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size / 2)
    o = _mesh_obj("suelo", bm)
    o.data.materials.append(m)
    return o


def mannequin():
    """Sobreviviente genérico low-poly (1,78 m) para dar escala, estilo Zomboid.
    Devuelve (raiz, matriz_mano_derecha) — la mano mira hacia +X del personaje."""
    skin = mat("piel", (0.72, 0.52, 0.40), dirt=.1)
    shirt = mat("remera", (0.25, 0.32, 0.42), dirt=.3)
    pants = mat("jean", (0.16, 0.20, 0.30), dirt=.3)
    shoes = mat("zapatillas", (0.08, 0.07, 0.07), dirt=.2)
    hair = mat("pelo", (0.12, 0.08, 0.05), dirt=.2)
    parts = []
    # piernas
    for s in (-1, 1):
        parts.append(cylinder("pierna", .075, .82, loc=(0, s * .1, .45), rot=(0, 0, 0), mat=pants, segs=8, r2=.065))
        parts.append(box("zapato", (.26, .11, .08), loc=(.05, s * .1, .04), mat=shoes))
    # torso
    parts.append(cylinder("torso", .19, .62, loc=(0, 0, 1.18), rot=(0, 0, 0), mat=shirt, segs=10, r2=.21))
    parts[-1].scale = (0.75, 1.15, 1.0)
    parts.append(cylinder("cuello", .05, .08, loc=(0, 0, 1.52), rot=(0, 0, 0), mat=skin, segs=8))
    parts.append(sphere("cabeza", .115, loc=(0.01, 0, 1.64), mat=skin, segs=12, rings=8, scale=(1, .9, 1.1)))
    parts.append(sphere("pelo", .12, loc=(-0.01, 0, 1.68), mat=hair, segs=12, rings=8, scale=(1, .95, .8)))
    # brazo izquierdo colgando (el personaje mira hacia +X; su izquierda es +Y)
    parts.append(cylinder("brazoI", .05, .62, loc=(0, .27, 1.15), rot=(0, 0, -0), mat=shirt, segs=8, r2=.04))
    parts.append(sphere("manoI", .05, loc=(0, .27, .82), mat=skin))
    # brazo derecho hacia adelante sosteniendo
    sh = Vector((0, -.27, 1.43))
    hand = Vector((.38, -.24, 1.05))
    d = hand - sh
    mid = (sh + hand) / 2
    arm = cylinder("brazoD", .05, d.length, loc=mid, rot=(0, 0, 0), mat=shirt, segs=8, r2=.04)
    arm.rotation_euler = d.to_track_quat("Z", "X").to_euler()
    parts.append(arm)
    parts.append(sphere("manoD", .05, loc=hand, mat=skin))
    for p in parts:
        p["mannequin"] = True
    return parts, hand


def previews(obj, name, grip_offset=0.0, hold_rot=(0, -55, 0)):
    """Genera vistas previas en art/<name>/:
      preview_hero.png      modelo grande (3/4), para ver la forma y la textura
      preview_ingame.png    personaje + arma con cámara isométrica de Zomboid (zoom cercano y normal)
      preview_ground.png    el arma tirada en el suelo (vista isométrica)
      icon_64.png / icon_32.png  ícono de inventario renderizado desde el modelo
    hold_rot: rotación (grados) del arma en la mano para la toma in-game."""
    out = ART / name
    sc = bpy.context.scene
    for o in list(sc.objects):
        if o is not obj:
            bpy.data.objects.remove(o, do_unlink=True)
    lo, hi = _bounds(obj)
    length = (hi - lo).length
    center = (lo + hi) / 2

    # --- hero: perspectiva 3/4, luz de estudio
    _world(0.9, (0.45, 0.46, 0.5))
    _sun((55, 0, 40), 3.5)
    _cam("cam_hero", center + Vector((length * .45, -length * 2.1, length * .8)), center, lens=50)
    _render(out / "preview_hero.png", 1400, 800, samples=32)
    # vista lateral pura (silueta)
    for o in [o for o in sc.objects if o.type == "CAMERA"]:
        bpy.data.objects.remove(o, do_unlink=True)
    _cam("cam_side", center + Vector((0, -length * 2, 0)), center, ortho_scale=length * 1.1)
    _render(out / "preview_side.png", 1400, 700, samples=24)

    # --- icono: diagonal, ortográfica, fondo transparente
    for o in [o for o in sc.objects if o.type == "CAMERA"]:
        bpy.data.objects.remove(o, do_unlink=True)
    obj.rotation_euler = Euler((0, math.radians(-45), 0))
    bpy.context.view_layer.update()
    lo2, hi2 = _bounds(obj)
    c2 = (lo2 + hi2) / 2
    _cam("cam_icon", c2 + Vector((0, -3, 0)), c2, ortho_scale=max(hi2.x - lo2.x, hi2.z - lo2.z) * 1.08)
    _render(out / "icon_256.png", 256, 256, samples=32)
    obj.rotation_euler = Euler((0, 0, 0))

    # --- in-game: personaje + arma en la mano, cámara isométrica (30° de elevación, 45° de azimut)
    for o in [o for o in sc.objects if o.type == "CAMERA"]:
        bpy.data.objects.remove(o, do_unlink=True)
    body, hand = mannequin()
    ground = _ground()
    obj.location = hand + Vector((0, 0, 0))
    obj.rotation_euler = Euler([math.radians(a) for a in hold_rot])
    obj.location = hand - (obj.rotation_euler.to_matrix() @ Vector((grip_offset, 0, 0)))
    target = Vector((0.15, 0, 0.9))
    el, az = math.radians(30), math.radians(-45)
    dist = 20
    camloc = target + Vector((math.cos(el) * math.cos(az) * dist, math.cos(el) * math.sin(az) * dist, math.sin(el) * dist))
    _cam("cam_iso", camloc, target, ortho_scale=3.2)
    sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.1
    _render(out / "preview_ingame_raw.png", 900, 900, samples=24, transparent=False)

    # --- arma tirada en el suelo
    for o in body:
        bpy.data.objects.remove(o, do_unlink=True)
    lo3, hi3 = _bounds(obj)
    obj.rotation_euler = Euler((math.radians(90), 0, math.radians(20)))
    bpy.context.view_layer.update()
    lo3, hi3 = _bounds(obj)
    obj.location -= Vector(((lo3.x + hi3.x) / 2, (lo3.y + hi3.y) / 2, lo3.z))
    target = Vector((0, 0, 0))
    camloc = target + Vector((math.cos(el) * math.cos(az) * dist, math.cos(el) * math.sin(az) * dist, math.sin(el) * dist))
    for o in [o for o in sc.objects if o.type == "CAMERA"]:
        bpy.data.objects.remove(o, do_unlink=True)
    _cam("cam_ground", camloc, target, ortho_scale=2.4)
    _render(out / "preview_ground_raw.png", 900, 900, samples=24, transparent=False)
    print(f"[pzlib] previews -> {out}")
