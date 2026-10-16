"""Armas de fuego para Arsenal Táctico (Project Zomboid B42): piezas, materiales y exportación.

Convenciones (verificadas con los modelos vanilla de 42.18 y el código de carga de 42.21):
  * Se modela a la ESCALA DEL JUEGO en metros: X hacia la boca del cañón, Z hacia arriba, Y hacia la
    izquierda; el origen es donde la mano derecha toma la empuñadura (como M16_Rifle / M9_Pistol).
    Referencia vanilla: M16 boca a +0,40, culata a -0,15, riel de mira a z +0,068; M9 boca a +0,144.
  * En el juego los rifles tienen el largo sobre +Y y arriba sobre +Z; las pistolas, arriba sobre -Z
    (models_weapons.txt: Handgun03 scope z -0.046). game_matrix() hace ese pasaje.
  * El juego carga los FBX con MAKE_LEFT_HANDED (espeja Z de los vértices): se exporta S · juego.
  * Los offsets de los attachments van en coordenadas del juego (ya espejadas), como los vanilla.
  * Las partes (miras, linterna) se modelan con la misma convención y el origen en su base de montaje;
    en las pistolas el attachment lleva rotate 180 0 -180 (igual que el "scope" de Handgun03).
"""
import json
import math
import shutil
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

import pzlib as pz

MOD = pz.ROOT / "Contents/mods/ArsenalTactico/42/media"
MODELS = MOD / "models_X/weapons/ArsenalTactico"
TEXTURES = MOD / "textures/weapons/ArsenalTactico"
S = Matrix.Diagonal((1, 1, -1, 1))
ROT_RIFLE = Matrix.Rotation(math.radians(90), 4, "Z")        # X del modelo (boca) -> +Y del juego
FLIP_HANDGUN = Matrix.Rotation(math.pi, 4, "Y")               # arriba -> -Z (convención de pistolas)


def game_matrix(kind):
    return FLIP_HANDGUN @ ROT_RIFLE if kind == "handgun" else ROT_RIFLE


# ------------------------------------------------------------------ materiales
def polymer(name="polimero", color=(0.045, 0.045, 0.05), seed=0.0):
    return pz.mat(name, color, dirt=0.12, rough=0.85, scale=40.0, seed=seed)


def black_metal(name="metal_negro", seed=0.0):
    return pz.mat(name, (0.075, 0.078, 0.085), rust=0.02, dirt=0.10, rough=0.45, scale=30.0, seed=seed)


def fde(name="fde", seed=0.0):
    return pz.mat(name, (0.45, 0.38, 0.27), dirt=0.12, rough=0.8, scale=30.0, seed=seed)


def grey(name="gris", seed=0.0):
    return pz.mat(name, (0.22, 0.23, 0.245), dirt=0.12, rough=0.8, scale=30.0, seed=seed)


def glass(name="vidrio"):
    return pz.mat(name, (0.04, 0.10, 0.16), dirt=0.0, rough=0.15)


def rubber(name="goma"):
    return pz.mat(name, (0.03, 0.03, 0.033), dirt=0.08, rough=0.95)


def brass(name="laton"):
    return pz.mat(name, (0.72, 0.53, 0.18), dirt=0.08, rough=0.4)


def accent(name, color):
    return pz.mat(name, color, dirt=0.05, rough=0.6)


# ------------------------------------------------------------------ piezas
def bx(name, x0, x1, y0, y1, z0, z1, mat, bevel=0.0015):
    """Caja por extremos (metros, coordenadas del modelo)."""
    return pz.box(name, (x1 - x0, y1 - y0, z1 - z0), loc=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
                  mat=mat, bevel=bevel)


def tube(name, x0, x1, r, mat, y=0.0, z=0.0, segs=14, r2=None):
    """Cilindro sobre X (de x0 a x1); r2 = radio en x1 (cono)."""
    return pz.cylinder(name, r, x1 - x0, loc=((x0 + x1) / 2, y, z), rot=(0, 90, 0), mat=mat, segs=segs,
                       r2=r2)


def side(name, pts, thickness, mat, y=0.0, bevel=0.001):
    """Perfil de costado [(x, z), ...] (antihorario) extruido sobre Y."""
    o = pz.extrude(name, pts, thickness, mat=mat, plane="XZ", bevel=bevel)
    o.location.y = y
    return o


def bar(name, p0, p1, thick, mat, width=None):
    """Barra recta entre dos puntos (x, z) del costado, de sección thick x width."""
    p0, p1 = Vector((p0[0], 0, p0[1])), Vector((p1[0], 0, p1[1]))
    d = p1 - p0
    ang = math.degrees(math.atan2(d.z, d.x))
    mid = (p0 + p1) / 2
    return pz.box(name, (d.length, width or thick, thick), loc=tuple(mid), rot=(0, -ang, 0), mat=mat, bevel=0.0008)


def rail(name, x0, x1, z, mat, w=0.021, h=0.006, y=0.0):
    """Riel picatinny: base + dientes cada ~1 cm. z = altura de la base."""
    parts = [bx(f"{name}_base", x0, x1, y - w / 2, y + w / 2, z, z + h * 0.55, mat, bevel=0.0008)]
    n = max(1, int((x1 - x0) / 0.0095))
    for i in range(n):
        xa = x0 + (x1 - x0) * (i + 0.15) / n
        xb = x0 + (x1 - x0) * (i + 0.75) / n
        parts.append(bx(f"{name}_t{i}", xa, xb, y - w / 2 * 0.92, y + w / 2 * 0.92, z + h * 0.5, z + h, mat, bevel=0.0005))
    return parts


def slots(name, x0, x1, z0, z1, y_face, mat, n=4, depth=0.0015):
    """Ranuras M-LOK: rectángulos oscuros apenas hundidos en una cara lateral (y_face con signo)."""
    out = []
    for i in range(n):
        xa = x0 + (x1 - x0) * (i + 0.18) / n
        xb = x0 + (x1 - x0) * (i + 0.82) / n
        y = y_face - math.copysign(depth / 2, y_face)
        out.append(bx(f"{name}{i}", xa, xb, y - depth, y + depth, z0, z1, mat, bevel=0.0))
    return out


def quad_rail(name, x0, x1, zc, r, mat, side_dz=0.0, segs=8):
    """Guardamanos de riel cuádruple: cuerpo octogonal + rieles arriba, abajo y a los costados."""
    body = pz.cylinder(f"{name}_cuerpo", r, x1 - x0, loc=((x0 + x1) / 2, 0, zc), rot=(0, 90, 0), mat=mat,
                       segs=segs, smooth=False)
    body.data.transform(Matrix.Rotation(math.pi / segs, 4, "Z"))     # caras planas arriba/abajo/costados
    parts = [body]
    parts += rail(f"{name}_sup", x0, x1, zc + r * 0.88, mat, w=0.018)
    parts += rail(f"{name}_inf", x0, x1, zc - r * 0.88 - 0.006, mat, w=0.018)
    for sgn, tag in ((1, "izq"), (-1, "der")):
        o = rail(f"{name}_{tag}", x0, x1, 0.0, mat, w=0.018)
        for q in o:
            q.rotation_euler = (math.radians(-90 * sgn), 0, 0)
            q.location = (q.location.x, sgn * (r * 0.88 + q.location.z), zc + side_dz)
        parts += o
    return parts


def mag_curve(name, x_top0, x_top1, length, curve, mat, thickness=0.021, rake=0.012, n=6):
    """Cargador curvo de costado: arriba entre x_top0 y x_top1 (z=0), baja `length` con curva hacia adelante."""
    front, back = [], []
    for i in range(n + 1):
        t = i / n
        dx = rake * t + curve * t * t
        z = -length * t
        back.append((x_top0 + dx, z))
        front.append((x_top1 + dx, z))
    return side(name, front + list(reversed(back)), thickness, mat)   # extrude recalcula las normales


# ------------------------------------------------------------------ exportación
def export(obj, ID, kind, attachments, tex=None, icon=True, icon_rot=(0, 0, 0)):
    """Exporta al mod: FBX orientado como lo espera el juego, textura e ícono; guarda los attachments
    (coordenadas del juego) en art/<ID>/attachments.json para generar el script de modelos.
    attachments: {nombre: (x, y, z) del modelo}."""
    G = game_matrix(kind)
    out = pz.ART / ID
    data = {"kind": kind, "attachments": {k: [round(c, 4) for c in (G @ Vector(v))] for k, v in attachments.items()}}
    lo = Vector([min(v.co[i] for v in obj.data.vertices) for i in range(3)])
    hi = Vector([max(v.co[i] for v in obj.data.vertices) for i in range(3)])
    data["center"] = [round(c, 4) for c in (G @ ((lo + hi) / 2))]
    data["length"] = round((hi - lo).x, 4)
    (out / "attachments.json").write_text(json.dumps(data, indent=1))

    me = obj.data.copy()
    tmp = bpy.data.objects.new(ID + "_export", me)
    bpy.context.scene.collection.objects.link(tmp)
    M = S @ G
    me.transform(M)
    if M.determinant() < 0:
        me.flip_normals()
    MODELS.mkdir(parents=True, exist_ok=True)
    TEXTURES.mkdir(parents=True, exist_ok=True)
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    tmp.select_set(True)
    bpy.context.view_layer.objects.active = tmp
    bpy.ops.export_scene.fbx(filepath=str(MODELS / f"{ID}.fbx"), use_selection=True, global_scale=0.01,
                             apply_unit_scale=False, apply_scale_options="FBX_SCALE_NONE",
                             bake_space_transform=True, axis_forward="Y", axis_up="Z", object_types={"MESH"},
                             mesh_smooth_type="FACE", path_mode="STRIP")
    bpy.data.objects.remove(tmp, do_unlink=True)
    shutil.copyfile(out / f"{ID}.png", TEXTURES / f"{tex or ID}.png")
    if icon:
        render_icon(obj, ID, icon_rot)
    print(f"[gunkit] {ID} -> {MODELS / (ID + '.fbx')}")


def render_icon(obj, ID, rot=(0, 0, 0)):
    """Ícono de inventario 64 y 32 px: el arma de costado, levemente en 3/4, fondo transparente."""
    from PIL import Image
    sc = bpy.context.scene
    for o in list(sc.objects):
        if o is not obj:
            bpy.data.objects.remove(o, do_unlink=True)
    obj.rotation_euler = [math.radians(a) for a in rot]
    bpy.context.view_layer.update()
    lo = Vector([min((obj.matrix_world @ v.co)[i] for v in obj.data.vertices) for i in range(3)])
    hi = Vector([max((obj.matrix_world @ v.co)[i] for v in obj.data.vertices) for i in range(3)])
    c = (lo + hi) / 2
    size = max(hi.x - lo.x, hi.z - lo.z) * 1.22
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.ortho_scale = size
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    co.location = c + Vector((0.12, -1.0, 0.25)).normalized() * 3
    co.rotation_euler = (c - co.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    for rot_l, en in (((55, 0, 30), 3.0), ((60, 0, 200), 1.2)):
        sun = bpy.data.objects.new("sol", bpy.data.lights.new("sol", "SUN"))
        sun.data.energy = en
        sun.rotation_euler = [math.radians(a) for a in rot_l]
        sc.collection.objects.link(sun)
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7
    sc.world = w
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 24
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = 256
    path = pz.ART / ID / "icon_256.png"
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    im = Image.open(path).convert("RGBA")
    for s in (64, 32):
        im.resize((s, s), Image.LANCZOS).save(pz.ART / ID / f"icon_{s}.png")
    (MOD / "textures").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pz.ART / ID / "icon_32.png", MOD / "textures" / f"Item_{ID}.png")


# ------------------------------------------------------------------ detalle
def bevel_more(obj, segments=2, width=None):
    """Más segmentos en el bisel de una pieza (redondea aristas: brillos y lectura de volumen)."""
    m = obj.modifiers.get("bevel")
    if m is None:
        m = obj.modifiers.new("bevel", "BEVEL")
        m.limit_method = "ANGLE"
        m.width = width or 0.002
    m.segments = segments
    if width:
        m.width = width
    try:
        m.harden_normals = True
    except AttributeError:
        pass
    return obj


def smooth(obj, angle=40):
    for p in obj.data.polygons:
        p.use_smooth = True
    obj.data.set_sharp_from_angle(angle=math.radians(angle))
    return obj


def pin(name, x, z, r, mat, y_half, segs=10):
    """Perno pasante (se ve en las dos caras): cilindro sobre Y."""
    return pz.cylinder(name, r, 2 * y_half + 0.001, loc=(x, 0, z), rot=(90, 0, 0), mat=mat, segs=segs)


def screw_y(name, x, z, r, mat, y, depth=0.002, segs=8):
    return pz.cylinder(name, r, depth, loc=(x, y, z), rot=(90, 0, 0), mat=mat, segs=segs)


def finish_gun(ID, parts, tex_size=1024, wear=0.15):
    """pz.finish + desgaste de bordes: hornea una máscara de aristas (normal biselada vs. normal real)
    y aclara el color ahí, como el pavonado gastado. Devuelve el objeto final."""
    obj = pz.finish(ID, parts, tex_size=tex_size, ao=True)
    if wear:
        edge_wear(obj, pz.ART / ID / f"{ID}.png", wear)
    return obj


def edge_wear(obj, png, amount=0.22, radius=0.0012):
    from PIL import Image
    sc = bpy.context.scene
    size = Image.open(png).size[0]
    img = bpy.data.images.new("edge_mask", size, size, alpha=False)
    m = bpy.data.materials.new("edge_bake")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    bev = nt.nodes.new("ShaderNodeBevel")
    bev.inputs["Radius"].default_value = radius
    bev.samples = 8
    dot = nt.nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.use_clamp = True
    mul.inputs[1].default_value = 6.0
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    uv = nt.nodes.new("ShaderNodeUVMap")
    uv.uv_map = "UVMap"
    L = nt.links
    L.new(bev.outputs["Normal"], dot.inputs[0])
    L.new(geo.outputs["True Normal"], dot.inputs[1])
    L.new(dot.outputs["Value"], inv.inputs[1])
    L.new(inv.outputs["Value"], mul.inputs[0])
    L.new(mul.outputs["Value"], em.inputs["Color"])
    L.new(em.outputs["Emission"], out.inputs["Surface"])
    L.new(uv.outputs["UV"], tex.inputs["Vector"])
    nt.nodes.active = tex
    old = list(obj.data.materials)
    obj.data.materials.clear()
    obj.data.materials.append(m)
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 16
    sc.render.bake.margin = 4
    bpy.ops.object.bake(type="EMIT")
    obj.data.materials.clear()
    for mt in old:
        obj.data.materials.append(mt)
    mask = list(img.pixels)
    base = Image.open(png).convert("RGB")
    px = base.load()
    w, h = base.size
    for yy in range(h):
        row = (h - 1 - yy) * w
        for xx in range(w):
            e = mask[(row + xx) * 4]
            if e > 0.02:
                r, g, b = px[xx, yy]
                lift = amount * e * 255
                px[xx, yy] = (min(255, int(r + lift * 0.9)), min(255, int(g + lift * 0.92)), min(255, int(b + lift)))
    base.save(png)


# ------------------------------------------------------------------ calcado desde foto
class Photo:
    """Silueta calcada de una foto de costado (tools/trace_photo.py) y pasaje píxel -> modelo.

    La foto muestra el lado DERECHO del arma con la boca hacia la derecha (como las referencias):
    x de la foto -> +X del modelo, arriba de la foto -> +Z. origin_px es el punto de la foto que va a
    origin (x, z) del modelo; bore_px = dos puntos del eje del cañón (corrigen la inclinación);
    scale = metros del modelo por píxel."""

    def __init__(self, ID, origin_px, origin=(0.0, 0.0), bore_px=None, scale=0.0005, flip=False, silhouette=True,
                 soften=1.0):
        from shapely.geometry import Polygon
        from shapely.ops import unary_union
        self.ox, self.oy = origin_px
        self.o = origin
        self.k = scale
        self.s = -1.0 if flip else 1.0          # flip: la boca apunta a la izquierda de la foto
        if bore_px:
            (ax, ay), (bx_, by) = bore_px
            dx, dz = self.s * (bx_ - ax), -(by - ay)
            self.ang = math.atan(dz / dx) if dx else 0.0                # inclinación del cañón en la foto
        else:
            self.ang = 0.0
        if not silhouette:
            self.sil = Polygon([(-9, -9), (9, -9), (9, 9), (-9, 9)])      # sin calco: cut() = la región
            return
        data = json.loads((Path(__file__).resolve().parent / "guns/siluetas" / f"{ID}.json").read_text())
        polys = []
        for ext, holes in data["shapes"]:
            pg = Polygon([self.pt(*p) for p in ext], [[self.pt(*p) for p in h] for h in holes])
            polys.append(pg.buffer(0))
        self.sil = unary_union(polys)
        if soften:      # alisa el serrucho del calco (abre y cierra `soften` píxeles)
            r = soften * scale
            self.sil = self.sil.buffer(-r).buffer(2 * r).buffer(-r)

    def pt(self, x, y):
        dx, dz = self.s * (x - self.ox) * self.k, -(y - self.oy) * self.k
        c, s = math.cos(-self.ang), math.sin(-self.ang)
        return (self.o[0] + dx * c - dz * s, self.o[1] + dx * s + dz * c)

    def L(self, px):
        return px * self.k

    def poly(self, pts):
        from shapely.geometry import Polygon
        if len(pts) == 4 and not isinstance(pts[0], (tuple, list)):
            x0, y0, x1, y1 = pts
            pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        return Polygon([self.pt(*p) for p in pts]).buffer(0)

    def line(self, pts, width_px):
        """Barra de ancho width_px siguiendo una polilínea (palancas, aros)."""
        from shapely.geometry import LineString
        return LineString([self.pt(*p) for p in pts]).buffer(self.L(width_px) / 2, cap_style=1, join_style=1)

    def X(self, px, bore_y):
        return self.pt(px, bore_y)[0]

    def cut(self, region, minus=()):
        """Silueta recortada por una región (caja x0,y0,x1,y1 o polígono, en píxeles de la foto)."""
        g = self.sil.intersection(self.poly(region))
        for m in minus:
            g = g.difference(self.poly(m))
        return g


def _polys(geom):
    if geom.is_empty:
        return []
    if geom.geom_type == "Polygon":
        return [geom]
    return [g for g in getattr(geom, "geoms", []) if g.geom_type == "Polygon" and g.area > 1e-7]


def slab(name, geom, thick, mat, y=0.0, bevel=0.0012, segs=2, simplify=0.00025, min_area=4e-6, smooth=True):
    """Extruye sobre Y un polígono (shapely, coordenadas x-z del modelo; admite agujeros) con bisel
    redondeado. Devuelve una lista de objetos (uno por pedazo)."""
    import bmesh
    from shapely import constrained_delaunay_triangles
    from shapely.geometry import Polygon
    from shapely.geometry.polygon import orient
    out = []
    for i, pg in enumerate(_polys(geom.simplify(simplify, preserve_topology=True) if simplify else geom)):
        if pg.area < min_area:
            continue
        pg = orient(pg)
        bm = bmesh.new()
        h = thick / 2
        tris = [t for t in constrained_delaunay_triangles(pg).geoms if pg.buffer(1e-7).contains(t.centroid)]
        vmap = {}

        def V(p, side):
            key = (round(p[0], 7), round(p[1], 7), side)
            if key not in vmap:
                vmap[key] = bm.verts.new((p[0], side * h, p[1]))
            return vmap[key]

        for t in tris:
            a, b, c = list(orient(Polygon(t.exterior.coords)).exterior.coords)[:3]
            bm.faces.new((V(a, -1), V(b, -1), V(c, -1)))     # cara -Y (derecha)
            bm.faces.new((V(c, 1), V(b, 1), V(a, 1)))        # cara +Y
        for ring in [pg.exterior] + list(pg.interiors):
            cs = list(ring.coords)[:-1]
            for j in range(len(cs)):
                p, q = cs[j], cs[(j + 1) % len(cs)]
                try:
                    bm.faces.new((V(p, -1), V(q, -1), V(q, 1), V(p, 1)))
                except ValueError:
                    pass
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        o = pz._mesh_obj(f"{name}{i}", bm)
        o.location.y = y
        o.data.materials.append(mat)
        if bevel:
            m = o.modifiers.new("bevel", "BEVEL")
            m.width = min(bevel, thick * 0.4)
            m.segments = segs
            m.limit_method = "ANGLE"
            m.angle_limit = math.radians(50)
        if smooth:
            # paredes suaves (contornos curvos, bisel redondeado); tapas planas para no manchar el sombreado
            for p in o.data.polygons:
                p.use_smooth = abs(p.normal.y) < 0.5
            o.data.set_sharp_from_angle(angle=math.radians(35))
        out.append(o)
    return out


def lathe_x(name, prof, mat, y=0.0, z=0.0, segs=20, smooth=True):
    """Sólido de revolución sobre X: prof = [(x, radio), ...] en coordenadas del modelo."""
    x0 = prof[0][0]
    return pz.lathe(name, [(r, x - x0) for x, r in prof], loc=(x0, y, z), rot=(0, 90, 0), mat=mat, segs=segs,
                    smooth=smooth)


def decal(name, geom, y_face, mat, depth=0.0008, both=True):
    """Detalle pegado a una cara lateral (ranuras, ventanas, paneles): lámina fina en y = ±y_face."""
    out = []
    for s in ((1, -1) if both else (math.copysign(1, y_face),)):
        out += slab(f"{name}{'i' if s > 0 else 'd'}", geom, depth, mat, y=s * abs(y_face), bevel=0.0, smooth=False,
                    min_area=1e-8, simplify=0)
    return out


def panel(name, geom, thick, mat, inset=0.002, bevel=0.0006):
    """Panel en relieve dentro de una pieza (texturado de empuñadura, guardamanos): contorno achicado
    `inset` y apenas más grueso que la pieza."""
    return slab(name, geom.buffer(-inset, join_style=2), thick + 0.0012, mat, bevel=bevel, segs=1, min_area=1e-7)


def circle(x, z, r, n=16, sx=1.0, sz=1.0):
    from shapely.geometry import Polygon
    return Polygon([(x + sx * r * math.cos(2 * math.pi * i / n), z + sz * r * math.sin(2 * math.pi * i / n))
                    for i in range(n)])


def rect(x0, z0, x1, z1):
    from shapely.geometry import box as sbox
    return sbox(min(x0, x1), min(z0, z1), max(x0, x1), max(z0, z1))


def preview(obj, path, size=1400):
    """Lámina de revisión: costado derecho, costado izquierdo y 3/4 de arriba (Cycles, fondo gris)."""
    from PIL import Image
    sc = bpy.context.scene
    keep = obj
    lo = Vector([min(v.co[i] for v in keep.data.vertices) for i in range(3)])
    hi = Vector([max(v.co[i] for v in keep.data.vertices) for i in range(3)])
    c = (lo + hi) / 2
    span = max(hi.x - lo.x, 2 * (hi.z - lo.z)) * 1.08
    if "rev_cam" not in bpy.data.objects:
        cam = bpy.data.objects.new("rev_cam", bpy.data.cameras.new("rev_cam"))
        sc.collection.objects.link(cam)
        for rot_l, en in (((55, 0, 30), 2.2), ((60, 0, 200), 1.0), ((-30, 0, 120), 0.5)):
            sun = bpy.data.objects.new("rev_sol", bpy.data.lights.new("rev_sol", "SUN"))
            sun.data.energy = en
            sun.rotation_euler = [math.radians(a) for a in rot_l]
            sc.collection.objects.link(sun)
    cam = bpy.data.objects["rev_cam"]
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = span
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.35, 0.36, 0.38, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    sc.world = w
    sc.render.film_transparent = False
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 24
    sc.render.resolution_x = size
    sc.render.resolution_y = int(size * 0.5)
    tiles = []
    for i, d in enumerate((Vector((0, -1, 0.02)), Vector((0, 1, 0.02)), Vector((0.5, -1, 0.7)))):
        cam.location = c + d.normalized() * 3
        cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.camera = cam
        p = str(path) + f".{i}.png"
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        tiles.append(Image.open(p))
    W, H = tiles[0].size
    sheet = Image.new("RGB", (W, H * 3))
    for i, t in enumerate(tiles):
        sheet.paste(t, (0, i * H))
        Path(str(path) + f".{i}.png").unlink()
    sheet.save(path)
    sc.render.film_transparent = True
