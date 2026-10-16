"""Modelado hard-surface low-poly para armas de Project Zomboid (Blender 5.x como módulo).

Método (ver docs y la skill de armas):
  * Se modela en METROS REALES sobre la referencia (foto de costado calibrada, mm/px medido con el paso
    del riel Picatinny = 10,01 mm). Coordenadas: X hacia la boca, Z arriba, Y a la izquierda del arma.
  * Cada pieza es un sólido de "dos vistas": perfil de costado (de la referencia) ∩ sección real
    (frente o planta, de medidas publicadas). Así salen chaflanes, brocal ensanchado, empuñadura redondeada.
    Torneados (cañón, apagallamas, tubo) con lathe; rieles con Array al paso real.
  * Bisel chico en bordes duros (Harden Normals) + Weighted Normal (Face Area, Keep Sharp), aplicados.
  * Booleanos Exact para huecos (ventanas, ranuras, guardamonte).
  * Textura: color base + AO + curvatura (desgaste) + cavidad (líneas de unión), horneados en Cycles.
"""
import math
from pathlib import Path

import bpy  # noqa: I001
import bmesh
from mathutils import Matrix, Vector

import pzlib as pz


# ------------------------------------------------------------------ referencia (foto calibrada)
class Ref:
    """Píxeles de la foto -> metros reales del modelo. origin_px va a (0, 0); bore_px corrige la
    inclinación; mm_px = milímetros por píxel; flip si la boca apunta a la izquierda."""

    def __init__(self, mm_px, origin_px, bore_px=None, flip=False):
        self.k = mm_px / 1000.0
        self.ox, self.oy = origin_px
        self.s = -1.0 if flip else 1.0
        self.ang = 0.0
        if bore_px:
            (ax, ay), (bx, by) = bore_px
            self.ang = math.atan(-(by - ay) / (self.s * (bx - ax)))

    def pt(self, x, y):
        dx, dz = self.s * (x - self.ox) * self.k, -(y - self.oy) * self.k
        c, s = math.cos(-self.ang), math.sin(-self.ang)
        return (dx * c - dz * s, dx * s + dz * c)

    def px(self, X, Z):
        """Inversa: metros del modelo -> píxeles de la foto."""
        c, s = math.cos(self.ang), math.sin(self.ang)
        dx, dz = X * c - Z * s, X * s + Z * c
        return (self.ox + dx / (self.s * self.k), self.oy - dz / self.k)

    def poly(self, pts):
        from shapely.geometry import Polygon
        if len(pts) == 4 and not isinstance(pts[0], (tuple, list)):
            x0, y0, x1, y1 = pts
            pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        return Polygon([self.pt(*p) for p in pts]).buffer(0)

    def X(self, x, y):
        return self.pt(x, y)[0]

    def Z(self, x, y):
        return self.pt(x, y)[1]


def silhouette(json_path, ref, soften_px=1.0):
    """Silueta calcada (tools/trace_photo.py) en metros del modelo, alisada."""
    import json
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    data = json.loads(Path(json_path).read_text())
    data["shapes"] = [max(data["shapes"], key=lambda sh: len(sh[0]))]     # solo el contorno principal
    polys = [Polygon([ref.pt(*p) for p in ext], [[ref.pt(*p) for p in h] for h in holes]).buffer(0)
             for ext, holes in data["shapes"]]
    g = unary_union(polys)
    r = soften_px * ref.k
    return g.buffer(-r).buffer(2 * r).buffer(-r)


# ------------------------------------------------------------------ mallas base
def _polys(geom):
    if geom.is_empty:
        return []
    if geom.geom_type == "Polygon":
        return [geom]
    return [g for g in getattr(geom, "geoms", []) if g.geom_type == "Polygon" and g.area > 1e-9]


def prism(name, geom, t0, t1, mat=None, plane="XZ"):
    """Prisma de un polígono (shapely, con agujeros) extruido entre t0 y t1 sobre el eje normal al plano.
    plane="XZ": (u,v)=(x,z), extruido en Y.  "YZ": (u,v)=(y,z), extruido en X.  "XY": (u,v)=(x,y), en Z."""
    from shapely import constrained_delaunay_triangles
    from shapely.geometry import Polygon
    from shapely.geometry.polygon import orient

    def P(u, v, t):
        return {"XZ": (u, t, v), "YZ": (t, u, v), "XY": (u, v, t)}[plane]

    bm = bmesh.new()
    for pg in _polys(geom):
        pg = orient(pg)
        cache = {}

        def V(p, t):
            key = (round(p[0], 8), round(p[1], 8), t)
            if key not in cache:
                cache[key] = bm.verts.new(P(p[0], p[1], t))
            return cache[key]

        for tri in constrained_delaunay_triangles(pg).geoms:
            if not pg.buffer(1e-9).contains(tri.centroid):
                continue
            a, b, c = list(orient(Polygon(tri.exterior.coords)).exterior.coords)[:3]
            for f in ((V(a, t0), V(b, t0), V(c, t0)), (V(c, t1), V(b, t1), V(a, t1))):
                try:
                    bm.faces.new(f)
                except ValueError:
                    pass
        for ring in [pg.exterior] + list(pg.interiors):
            cs = list(ring.coords)[:-1]
            for j in range(len(cs)):
                p, q = cs[j], cs[(j + 1) % len(cs)]
                try:
                    bm.faces.new((V(p, t0), V(q, t0), V(q, t1), V(p, t1)))
                except ValueError:
                    pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # caras planas trianguladas -> n-gonos (mejor bisel y menos triángulos)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), verts=bm.verts, edges=bm.edges)
    o = pz._mesh_obj(name, bm)
    if mat is not None:
        o.data.materials.append(mat)
    return o


def rounded_rect(w, h, r, n=3, cx=0.0, cy=0.0):
    """Rectángulo w x h con esquinas redondeadas (r) o achaflanadas (n=1)."""
    from shapely.geometry import Polygon
    pts = []
    for (sx, sy, a0) in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        ccx, ccy = cx + sx * (w / 2 - r), cy + sy * (h / 2 - r)
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
    return Polygon(pts)


def two_view(name, side, section, mat, plane2="YZ", tol=0.0005):
    """Sólido = perfil de costado (XZ, extruido en Y) ∩ sección (plane2) extruida a lo largo de la pieza.
    tol: simplificación del perfil calcado (m) para no cargar polígonos que no se ven."""
    from shapely.geometry import Polygon
    if isinstance(section, (list, tuple)):
        section = Polygon(section)
    if tol:
        side = side.simplify(tol, preserve_topology=True)
    x0, z0, x1, z1 = side.bounds
    sy0, sv0, sy1, sv1 = section.bounds
    w = max(abs(sy0), abs(sy1)) + 0.01
    a = prism(name, side, -w, w, mat, "XZ")
    if plane2 == "YZ":
        b = prism(name + "_sec", section, x0 - 0.01, x1 + 0.01, None, "YZ")
    else:   # "XY": planta extruida en Z
        b = prism(name + "_sec", section, z0 - 0.01, z1 + 0.01, None, "XY")
    return boolean(a, b, "INTERSECT")


def boolean(a, b, op="DIFFERENCE", keep=False):
    if not b.data.materials and a.data.materials:       # las caras nuevas heredan el material de la pieza
        b.data.materials.append(a.data.materials[0])
    m = a.modifiers.new("bool", "BOOLEAN")
    m.operation = op
    m.solver = "EXACT"
    m.object = b
    _apply(a)
    if not keep:
        bpy.data.objects.remove(b, do_unlink=True)
    return a


def _apply(o):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    for m in list(o.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def lathe_x(name, prof, mat, y=0.0, z=0.0, segs=16):
    """Torneado sobre X: prof = [(x, radio)] (radio 0 en los extremos para cerrar)."""
    return pz.lathe(name, [(r, x - prof[0][0]) for x, r in prof], loc=(prof[0][0], y, z), rot=(0, 90, 0), mat=mat,
                    segs=segs, smooth=True)


def box(name, x0, x1, y0, y1, z0, z1, mat):
    return pz.box(name, (x1 - x0, y1 - y0, z1 - z0), loc=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), mat=mat)


def cyl_y(name, x, z, r, y0, y1, mat, segs=12):
    """Cilindro sobre Y (pernos, botones)."""
    return pz.cylinder(name, r, y1 - y0, loc=(x, (y0 + y1) / 2, z), rot=(90, 0, 0), mat=mat, segs=segs)


PITCH = 0.01001        # MIL-STD-1913: paso entre ranuras
SLOT = 0.00523         # ancho de ranura
RAIL_W = 0.0212        # ancho del riel (0,835")


def picatinny(name, x0, x1, mat, h=0.0055, depth=0.003):
    """Riel Picatinny sobre +Z con base en z=0, centrado en y=0, de x0 a x1: base en cola de milano + dientes
    con Array a 10,01 mm. Rotar/mover después para los costados o abajo."""
    w = RAIL_W
    base_h = h - depth
    sec = [(-w / 2 + 0.002, 0.0), (w / 2 - 0.002, 0.0), (w / 2, base_h * 0.45), (w / 2 - 0.0015, base_h),
           (-w / 2 + 0.0015, base_h), (-w / 2, base_h * 0.45)]
    from shapely.geometry import Polygon
    base = prism(name, Polygon(sec), x0, x1, mat, "YZ")
    tooth_l = PITCH - SLOT
    tsec = Polygon([(-w / 2 + 0.0016, base_h - 0.0002), (w / 2 - 0.0016, base_h - 0.0002), (w / 2 - 0.0024, h),
                    (-w / 2 + 0.0024, h)])
    n = max(1, int((x1 - x0 - tooth_l) / PITCH) + 1)
    start = x0 + ((x1 - x0) - ((n - 1) * PITCH + tooth_l)) / 2
    tooth = prism(name + "_d", tsec, start, start + tooth_l, mat, "YZ")
    bm = bmesh.new()
    bm.from_mesh(tooth.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.z < -0.9], context="FACES")   # cara oculta
    bm.to_mesh(tooth.data)
    bm.free()
    arr = tooth.modifiers.new("array", "ARRAY")
    arr.count = n
    arr.use_relative_offset = False
    arr.use_constant_offset = True
    arr.constant_offset_displace = (PITCH, 0, 0)
    nf = len(tooth.data.polygons)
    _apply(tooth)
    # grupo y número de copia por cara: después de unir, todos los dientes de un riel comparten la UV
    gid = abs(hash(name)) % 100000 + 1
    a1 = tooth.data.attributes.new("tooth_grp", "INT", "FACE")
    a2 = tooth.data.attributes.new("tooth_copy", "INT", "FACE")
    for i in range(len(tooth.data.polygons)):
        a1.data[i].value = gid
        a2.data[i].value = i // nf
    return [base, tooth]


def place(objs, rot_x_deg=0.0, loc=(0, 0, 0)):
    R = Matrix.Rotation(math.radians(rot_x_deg), 4, "X")
    T = Matrix.Translation(Vector(loc))
    for o in objs:
        o.data.transform(T @ R)
    return objs


def harden(o, width=0.0006, segs=2, angle=30):
    """Bisel chico en bordes duros + normales endurecidas + Weighted Normal; aplicado. width=0: solo normales."""
    if width:
        b = o.modifiers.new("bevel", "BEVEL")
        b.width = width
        b.segments = segs
        b.limit_method = "ANGLE"
        b.angle_limit = math.radians(angle)
        b.use_clamp_overlap = True
        b.harden_normals = True
        b.miter_outer = "MITER_ARC"
    o.data.set_sharp_from_angle(angle=math.radians(50))     # aristas vivas que el bisel no tocó
    wn = o.modifiers.new("wn", "WEIGHTED_NORMAL")
    wn.mode = "FACE_AREA"
    wn.keep_sharp = True
    wn.weight = 50
    for p in o.data.polygons:
        p.use_smooth = True
    _apply(o)
    return o


def tri_count(objs):
    return sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs)


# ------------------------------------------------------------------ revisión rápida de geometría
def clay(objs, path, size=1400):
    """Renders de arcilla (sin textura) para revisar forma: costado derecho, frente, arriba y 3/4."""
    from PIL import Image
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 12
    sc.render.film_transparent = False
    if "clay_sun" not in bpy.data.objects:
        for nm, rot, en in (("clay_sun", (50, 10, 30), 3.0), ("clay_sun2", (65, 0, 210), 1.2)):
            sun = bpy.data.objects.new(nm, bpy.data.lights.new(nm, "SUN"))
            sun.data.energy = en
            sun.rotation_euler = [math.radians(a) for a in rot]
            sc.collection.objects.link(sun)
        w = bpy.data.worlds.new("clay_w")
        w.use_nodes = True
        w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.45, 0.46, 0.48, 1)
        w.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
        sc.world = w
    lo = Vector((min(min((o.matrix_world @ v.co)[i] for v in o.data.vertices) for o in objs) for i in range(3)))
    hi = Vector((max(max((o.matrix_world @ v.co)[i] for v in o.data.vertices) for o in objs) for i in range(3)))
    c = (lo + hi) / 2
    cam = bpy.data.objects.get("clay_cam") or bpy.data.objects.new("clay_cam", bpy.data.cameras.new("clay_cam"))
    if cam.name not in sc.collection.objects:
        sc.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    sc.camera = cam
    views = [("der", Vector((0, -1, 0)), max(hi.x - lo.x, 2 * (hi.z - lo.z)) * 1.05, (2, 1)),
             ("frente", Vector((1, 0, 0)), max(hi.y - lo.y, hi.z - lo.z) * 1.15, (1, 1)),
             ("arriba", Vector((0, 0, 1)), max(hi.x - lo.x, 2 * (hi.y - lo.y)) * 1.05, (2, 1)),
             ("34", Vector((0.55, -1, 0.55)), (hi.x - lo.x) * 1.0, (2, 1))]
    tiles = []
    for name, d, span, (ax, ay) in views:
        cam.data.ortho_scale = span
        cam.location = c + d.normalized() * 2
        up = Vector((0, 1, 0)) if name == "arriba" else Vector((0, 0, 1))
        cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y" if name != "arriba" else "Y").to_euler()
        if name == "arriba":
            cam.rotation_euler = (0, 0, 0)
        sc.render.resolution_x = size if ax == 2 else size // 2
        sc.render.resolution_y = size // 2
        p = str(path) + f".{name}.png"
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        tiles.append(Image.open(p).convert("RGB"))
        Path(p).unlink()
    W = size + size // 2
    sheet = Image.new("RGB", (W, size), (40, 40, 40))
    sheet.paste(tiles[0], (0, 0))
    sheet.paste(tiles[1], (size, 0))
    sheet.paste(tiles[2], (0, size // 2))
    sheet.paste(tiles[3].resize((size // 2, size // 4)), (size, size // 2))
    sheet.save(path)
    return path


# ------------------------------------------------------------------ verificación de silueta
def silhouette_iou(objs, ref, sil_json, exclude_px=(), holes_px=(), photo=None, out=None, pad=30):
    """IoU entre la silueta lateral del modelo (proyección ortográfica de todos los triángulos sobre XZ,
    llevada a píxeles de la foto con ref.px) y la silueta calcada de la referencia. Las zonas exclude_px
    (accesorios que no son el arma) no cuentan. Devuelve (iou, imagen superpuesta)."""
    import json
    import numpy as np
    from PIL import Image, ImageDraw
    data = json.loads(Path(sil_json).read_text())
    data["shapes"] = [max(data["shapes"], key=lambda sh: len(sh[0]))]     # solo el contorno del arma
    allpts = [p for ext, _ in data["shapes"] for p in ext]
    x0 = int(min(p[0] for p in allpts)) - pad
    y0 = int(min(p[1] for p in allpts)) - pad
    x1 = int(max(p[0] for p in allpts)) + pad
    y1 = int(max(p[1] for p in allpts)) + pad
    W, H = x1 - x0, y1 - y0

    def canvas():
        return Image.new("L", (W, H), 0)

    ref_m = canvas()
    d = ImageDraw.Draw(ref_m)
    for ext, holes in data["shapes"]:
        d.polygon([(x - x0, y - y0) for x, y in ext], fill=255)
        for h in holes:
            d.polygon([(x - x0, y - y0) for x, y in h], fill=0)
    for h in holes_px:
        d.polygon([(x - x0, y - y0) for x, y in h], fill=0)
    mod_m = canvas()
    d = ImageDraw.Draw(mod_m)
    for o in objs:
        mw = o.matrix_world
        vs = [mw @ v.co for v in o.data.vertices]
        for p in o.data.polygons:
            pts = [ref.px(vs[i].x, vs[i].z) for i in p.vertices]
            d.polygon([(x - x0, y - y0) for x, y in pts], fill=255)
    exc = canvas()
    d = ImageDraw.Draw(exc)
    for poly in exclude_px:
        d.polygon([(x - x0, y - y0) for x, y in poly], fill=255)
    A = np.array(ref_m) > 127
    B = np.array(mod_m) > 127
    keep = np.array(exc) < 128
    inter = (A & B & keep).sum()
    union = ((A | B) & keep).sum()
    iou = inter / max(union, 1)
    img = None
    if photo:
        base = Image.open(photo).convert("RGB").crop((x0, y0, x1, y1))
        arr = (np.array(base).astype(float) * 0.35)
        arr[A & B & keep] = arr[A & B & keep] * 0.4 + np.array([60, 200, 90]) * 0.6
        arr[A & ~B & keep] = arr[A & ~B & keep] * 0.3 + np.array([235, 60, 50]) * 0.7
        arr[~A & B & keep] = arr[~A & B & keep] * 0.3 + np.array([70, 120, 255]) * 0.7
        arr[~keep] = arr[~keep] * 0.5 + np.array([120, 120, 120]) * 0.5
        img = Image.fromarray(arr.clip(0, 255).astype("uint8"))
        if out:
            img.save(out)
    return iou, int(inter), int((A & ~B & keep).sum()), int((~A & B & keep).sum())


# ------------------------------------------------------------------ calcos proyectados (marcas, agujeros)
def add_decal(mat, image_path, x0, x1, z0, z1, side=1):
    """Pinta una imagen RGBA sobre las caras del material que miran a ±Y (side), proyectada en X-Z
    (coordenadas de objeto = mundo, porque las piezas se unen con transformaciones aplicadas)."""
    nt = mat.node_tree
    L = nt.links
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    src = bsdf.inputs["Base Color"].links[0].from_socket if bsdf.inputs["Base Color"].links else None
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sep.inputs["Vector"])
    mu = nt.nodes.new("ShaderNodeMath")
    mu.operation = "MULTIPLY_ADD"
    mu.inputs[1].default_value = 1.0 / (x1 - x0)
    mu.inputs[2].default_value = -x0 / (x1 - x0)
    L.new(sep.outputs["X"], mu.inputs[0])
    mv = nt.nodes.new("ShaderNodeMath")
    mv.operation = "MULTIPLY_ADD"
    mv.inputs[1].default_value = 1.0 / (z1 - z0)
    mv.inputs[2].default_value = -z0 / (z1 - z0)
    L.new(sep.outputs["Z"], mv.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    L.new(mu.outputs[0], comb.inputs["X"])
    L.new(mv.outputs[0], comb.inputs["Y"])
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(str(image_path))
    img.extension = "CLIP"
    L.new(comb.outputs["Vector"], img.inputs["Vector"])
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sepn = nt.nodes.new("ShaderNodeSeparateXYZ")
    L.new(geo.outputs["True Normal"], sepn.inputs["Vector"])
    face = nt.nodes.new("ShaderNodeMath")
    face.operation = "GREATER_THAN"
    face.inputs[1].default_value = 0.6
    if side > 0:
        L.new(sepn.outputs["Y"], face.inputs[0])
    else:
        neg = nt.nodes.new("ShaderNodeMath")
        neg.operation = "MULTIPLY"
        neg.inputs[1].default_value = -1.0
        L.new(sepn.outputs["Y"], neg.inputs[0])
        L.new(neg.outputs[0], face.inputs[0])
    fac = nt.nodes.new("ShaderNodeMath")
    fac.operation = "MULTIPLY"
    L.new(img.outputs["Alpha"], fac.inputs[0])
    L.new(face.outputs[0], fac.inputs[1])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    L.new(fac.outputs[0], mix.inputs["Factor"])
    if src is not None:
        L.new(src, mix.inputs["A"])
    else:
        mix.inputs["A"].default_value = bsdf.inputs["Base Color"].default_value
    L.new(img.outputs["Color"], mix.inputs["B"])
    L.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    return mat


# ------------------------------------------------------------------ unir, UV, hornear
def join(objs, name):
    for o in objs:
        if not o.data.materials or any(m is None for m in o.data.materials):
            print(f"[hardsurf] aviso: {o.name} sin material")
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    o.name = name
    o.data.name = name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o


def unwrap(o, margin=0.004):
    """UV del arma unida: Smart UV Project, después los dientes de cada riel se apilan sobre el primero
    (Array los dejó con la misma topología y orden) y se empaqueta fusionando solo esas islas."""
    me = o.data
    while me.uv_layers:
        me.uv_layers.remove(me.uv_layers[0])
    me.uv_layers.new(name="UVMap")
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=margin, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    grp = me.attributes.get("tooth_grp")
    if grp:
        cpy = me.attributes["tooth_copy"]
        uv = me.uv_layers["UVMap"].data
        groups = {}
        for p in me.polygons:
            g = grp.data[p.index].value
            if g:
                groups.setdefault(g, {}).setdefault(cpy.data[p.index].value, []).append(p)
        for copies in groups.values():
            first = copies[0]
            for k, faces in copies.items():
                if k == 0:
                    continue
                for pa, pb in zip(first, faces):
                    for la, lb in zip(pa.loop_indices, pb.loop_indices):
                        uv[lb].uv = uv[la].uv
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.pack_islands(margin=margin, rotate=True, merge_overlap=True)
    bpy.ops.object.mode_set(mode="OBJECT")


def _bake(o, size, kind, setup=None, samples=16):
    """Hornea un mapa a una imagen nueva y devuelve sus píxeles (numpy HxWx4). setup(mat) cambia los
    materiales para los horneados de emisión y devuelve una función que los restaura."""
    import numpy as np
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    img = bpy.data.images.new(f"bake_{kind}", size, size, alpha=False, float_buffer=True)
    restore = setup(o) if setup else None
    for m in o.data.materials:
        nt = m.node_tree
        node = nt.nodes.new("ShaderNodeTexImage")
        node.name = "__bake"
        node.image = img
        for n in nt.nodes:
            n.select = False
        node.select = True
        nt.nodes.active = node
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    sc.render.bake.margin = 6
    if kind == "DIFFUSE":
        sc.render.bake.use_pass_direct = False
        sc.render.bake.use_pass_indirect = False
        sc.render.bake.use_pass_color = True
    bpy.ops.object.bake(type=kind)
    for m in o.data.materials:
        n = m.node_tree.nodes.get("__bake")
        if n:
            m.node_tree.nodes.remove(n)
    if restore:
        restore()
    a = np.array(img.pixels[:], dtype=np.float32).reshape(size, size, 4)
    bpy.data.images.remove(img)
    return a


def _emission_setup(build):
    """Reemplaza temporalmente todos los materiales por uno de emisión armado por build(nt) -> socket."""
    def setup(o):
        old = list(o.data.materials)
        m = bpy.data.materials.new("__emit")
        m.use_nodes = True
        nt = m.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        em = nt.nodes.new("ShaderNodeEmission")
        nt.links.new(build(nt), em.inputs["Color"])
        nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
        for i in range(len(o.data.materials)):
            o.data.materials[i] = m

        def restore():
            for i, mt in enumerate(old):
                o.data.materials[i] = mt
        return restore
    return setup


def _edges(nt, radius):
    bev = nt.nodes.new("ShaderNodeBevel")
    bev.inputs["Radius"].default_value = radius
    bev.samples = 8
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    dot = nt.nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    nt.links.new(bev.outputs["Normal"], dot.inputs[0])
    nt.links.new(geo.outputs["True Normal"], dot.inputs[1])
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    nt.links.new(dot.outputs["Value"], inv.inputs[1])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.use_clamp = True
    mul.inputs[1].default_value = 7.0
    nt.links.new(inv.outputs[0], mul.inputs[0])
    return mul.outputs[0]


def _cavity(nt, distance):
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.inputs["Distance"].default_value = distance
    ao.only_local = True
    ao.samples = 16
    return ao.outputs["AO"]


def bake_textures(o, size, png, edge_radius=0.0009, cavity_dist=0.004, wear=0.55, ao_dist=0.04):
    """Color base + AO + curvatura (desgaste en aristas) + cavidad (líneas de unión, rincones)."""
    import numpy as np
    from PIL import Image
    sc = bpy.context.scene
    if sc.world is None:
        sc.world = bpy.data.worlds.new("w")
    sc.world.light_settings.distance = ao_dist
    base = _bake(o, size, "DIFFUSE", samples=4)[..., :3]
    ao = _bake(o, size, "AO", samples=64)[..., 0]
    edge = _bake(o, size, "EMIT", _emission_setup(lambda nt: _edges(nt, edge_radius)), samples=16)[..., 0]
    cav = _bake(o, size, "EMIT", _emission_setup(lambda nt: _cavity(nt, cavity_dist)), samples=32)[..., 0]
    # composición (espacio lineal) -> sRGB
    col = base * (0.30 + 0.70 * ao[..., None]) * (0.20 + 0.80 * np.clip(cav, 0, 1)[..., None] ** 1.6)
    worn = np.minimum(np.maximum(base, base * 4.0 + 0.10), 0.62)       # aristas gastadas: metal claro
    e = np.clip(edge * 1.4, 0, 1)[..., None] * wear
    col = col * (1 - e) + worn * e
    srgb = np.where(col <= 0.0031308, col * 12.92, 1.055 * np.power(np.clip(col, 0, 1), 1 / 2.4) - 0.055)
    out = (np.clip(srgb, 0, 1) * 255).astype(np.uint8)[::-1]
    Image.fromarray(out, "RGB").save(png)
    maps = {"ao": ao, "edge": edge, "cav": cav}
    for k, v in maps.items():
        Image.fromarray((np.clip(v, 0, 1) * 255).astype(np.uint8)[::-1], "L").save(str(png).replace(".png", f"_{k}.png"))
    # material final con la textura
    fm = bpy.data.materials.new(o.name + "_tex")
    nt, bsdf = pz._nodes(fm)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(png))
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.7
    o.data.materials.clear()
    o.data.materials.append(fm)
    return o


def closeup(objs, path, center, dist=0.35, direction=(0.6, -1.0, 0.45), size=(1400, 900), ortho=None, samples=32,
            light=1.0):
    """Primer plano con luz de estudio (Cycles)."""
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    if "cu_key" not in bpy.data.objects:
        for nm, rot, en in (("cu_key", (55, 5, 35), 4.0), ("cu_fill", (70, 0, 200), 1.5), ("cu_rim", (-35, 0, 120), 2.0)):
            sun = bpy.data.objects.new(nm, bpy.data.lights.new(nm, "SUN"))
            sun.data.energy = en * light
            sun.rotation_euler = [math.radians(a) for a in rot]
            sc.collection.objects.link(sun)
    w = bpy.data.worlds.new("cu_w")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.32, 0.33, 0.35, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6 * light
    sc.world = w
    cam = bpy.data.objects.get("cu_cam") or bpy.data.objects.new("cu_cam", bpy.data.cameras.new("cu_cam"))
    if cam.name not in sc.collection.objects:
        sc.collection.objects.link(cam)
    c = Vector(center)
    cam.location = c + Vector(direction).normalized() * dist
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    if ortho:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = ortho
    else:
        cam.data.type = "PERSP"
        cam.data.lens = 50
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return path
