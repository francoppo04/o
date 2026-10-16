"""Constructor genérico de armas "HD" (el proceso de AT_M4.py, en fichas): sólidos de dos vistas sobre una
referencia calibrada en mm/px, torneados, rieles Picatinny con Array, pernos; bisel + normales endurecidas;
detalles finos (ranuras, estrías, ventilaciones, marcas) pintados en la textura; bakeo de color, AO,
curvatura y cavidad; verificación (IoU de silueta, volumen, escala de juego, manos) y exportación.

Las fichas están en hd_specs.py (coordenadas en píxeles de la imagen de referencia de cada arma).
Uso: python3 tools/blender/guns/hd.py ID [ID ...] [--check] [--ref-dir DIR]
  --check: solo geometría + IoU (rápido).  --ref-dir: carpeta con las imágenes de referencia (para las
  láminas de verificación superpuestas; las imágenes no van al repo).
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import pzlib as pz  # noqa: E402
import hardsurf as hs  # noqa: E402
from shapely.geometry import Point, Polygon  # noqa: E402

import hd_specs  # noqa: E402

COLORS = hd_specs.COLORS


class Gun:
    def __init__(self, ID):
        self.ID = ID
        self.sp = hd_specs.SPEC[ID]
        sp = self.sp
        self.ref = hs.Ref(sp["mm_px"], sp["origin"], sp.get("bore"), sp.get("flip", False))
        self.sil_json = HERE / "siluetas" / f"{sp['sil']}.json" if sp.get("sil") else None
        self.sil = None
        if self.sil_json:
            self.sil = hs.silhouette(self.sil_json, self.ref, sp.get("soften", 1.0))
            for h in sp.get("holes", []):
                self.sil = self.sil.difference(self.ref.poly(h))
        self.mats = {}
        self.by = sp["bore_y"]

    # --- coordenadas
    def X(self, x):
        return self.ref.X(x, self.by)

    def Z(self, y):
        return self.ref.Z(self.sp["origin"][0], y)

    def mm(self, v):
        return v / 1000.0

    def mat(self, key):
        if key not in self.mats:
            self.mats[key] = pz.mat(f"{key}", COLORS[key], dirt=0.05, rough=0.6, scale=60)
        return self.mats[key]

    def region(self, reg, cut=True):
        g = self.ref.poly(reg)
        if cut and self.sil is not None and self.sp.get("sil_cut", True):     # sil_cut False: silueta solo para medir
            g = self.sil.intersection(g)
        return g

    # --- piezas
    def solid(self, name, reg, w_mm, mat, o):
        if o.get("raw"):
            from shapely import wkt
            side = wkt.loads(reg)
        else:
            side = self._side(reg, o)
            if name in getattr(self, "extra", {}):
                side = side.union(self.extra[name].buffer(0.0006).intersection(self.sil.buffer(0.0002)))
                side = side.buffer(0.0003).buffer(-0.0003)
        if side.is_empty:
            print(f"[hd] {self.ID}: {name} vacío")
            return []
        # tolerancia de ~1 px de la referencia: borra la escalera de píxeles de los bordes diagonales
        tol = self.mm(o["tol"]) if "tol" in o else max(0.0005, 1.0 * self.sp["mm_px"] / 1000)
        side = side.simplify(tol, preserve_topology=True)
        x0, z0, x1, z1 = side.bounds
        w = self.mm(w_mm)
        ct = self.mm(o.get("ct", min(0.12 * w_mm, 3.0)))
        cb = self.mm(o.get("cb", min(0.07 * w_mm, 2.0)))
        if o.get("sec") == "round":                      # sección redondeada (tubos, empuñaduras)
            r = min(w / 2 - 1e-4, (z1 - z0) / 2 - 1e-4, self.mm(o.get("r", 0.42 * w_mm)))
            sec = hs.rounded_rect(w, (z1 - z0) + 0.004, r, n=4, cy=(z0 + z1) / 2)
        else:
            sec = hs_sec(w, z0 - 0.002, z1 + 0.002, ct, cb)
        ob = hs.two_view(name, side, sec, self.mat(mat), tol=0)
        if o.get("y"):
            ob.data.transform(__import__("mathutils").Matrix.Translation((0, self.mm(o["y"]), 0)))
        ob["bevel"] = (self.mm(o.get("bevel", 0.6)), o.get("segs", 1))
        if o.get("round"):
            ob["bevel"] = (min(self.mm(o.get("bevel", 0.33 * w_mm)), w / 2 - 0.0005), o.get("segs", 3))
        return [ob]

    def build_parts(self):
        self.plan_fill()
        P = []
        for op in self.sp["parts"]:
            k = op[0]
            if k == "s":
                _, name, reg, w, m, *rest = op
                P += self.solid(name, reg, w, m, rest[0] if rest else {})
            elif k == "lathe":
                _, name, prof, y, m, *rest = op
                pts, z = self.lathe_fit(prof, y)
                pts = [(pts[0][0], 0.0)] + pts + [(pts[-1][0], 0.0)]
                ob = hs.lathe_x(name, pts, self.mat(m), z=z, segs=rest[0] if rest else 16)
                ob["bevel"] = (0.0, 1)
                P.append(ob)
            elif k == "rail":
                _, name, x0, x1, y, where, *rest = op
                a, b = sorted((self.X(x0), self.X(x1)))
                r = hs.picatinny(name, a, b, self.mat(rest[1] if len(rest) > 1 else "anod"))
                z = self.Z(y)
                half = self.mm(rest[0]) if rest else 0.0
                rot, loc = {"top": (0, (0, 0, z)), "bottom": (180, (0, 0, z)), "right": (90, (0, -half, z)),
                            "left": (-90, (0, half, z))}[where]
                hs.place(r, rot, loc)
                for ob in r:
                    ob["bevel"] = (0.0, 1)
                P += r
            elif k == "pin":
                _, x, y, r, w = op
                ob = hs.cyl_y(f"perno{len(P)}", self.X(x), self.Z(y), self.mm(r), -self.mm(w) / 2 - 0.0006,
                              self.mm(w) / 2 + 0.0006, self.mat("acero"))
                ob["bevel"] = (0.0, 1)
                P.append(ob)
            elif k == "cyl":
                _, name, x, y, r, y0, y1, m = op
                ob = hs.cyl_y(name, self.X(x), self.Z(y), self.mm(r), self.mm(y0), self.mm(y1), self.mat(m), 16)
                ob["bevel"] = (0.0003, 1)
                P.append(ob)
            elif k == "vcyl":                       # cilindro vertical (cartuchos)
                _, name, x, y0, y1, r, yy, m = op
                za, zb = self.Z(y1), self.Z(y0)
                ob = pz.cylinder(name, self.mm(r), zb - za, loc=(self.X(x), self.mm(yy), (za + zb) / 2), rot=(0, 0, 0),
                                 mat=self.mat(m), segs=10)
                ob["bevel"] = (0.0, 1)
                P.append(ob)
            elif k == "box":
                _, name, x0, y0, x1, y1, w0, w1, m = op
                a, b = sorted((self.X(x0), self.X(x1)))
                ob = hs.box(name, a, b, self.mm(w0), self.mm(w1), self.Z(y1), self.Z(y0), self.mat(m))
                ob["bevel"] = (0.0004, 1)
                P.append(ob)
        if "mag" in self.sp:
            P += self.mag_parts()
        P += self.fill()
        return P

    def plan_fill(self):
        """Lo que la silueta tiene y ninguna pieza cubre se reparte entre las piezas vecinas (crece su perfil
        de costado y conserva su ancho y sección). Lo que no toca ninguna pieza queda como relleno aparte."""
        self.extra, self.orphans = {}, []
        if self.sil is None or self.sp.get("fill") is False:
            return
        from shapely.geometry import box as _box
        from shapely.ops import unary_union
        feet = []
        for op in self.sp["parts"]:
            k = op[0]
            if k == "s":
                o = op[5] if len(op) > 5 else {}
                feet.append((op[1], self._side(op[2], o), not o.get("y") and o.get("grow", True)))
            elif k == "lathe":
                pts, z = self.lathe_fit(op[2], op[3])
                r = max(rr for _, rr in pts)
                feet.append((op[1], _box(pts[0][0], z - r, pts[-1][0], z + r), False))
            elif k == "rail" and op[5] == "top":
                a, b = sorted((self.X(op[2]), self.X(op[3])))
                feet.append((op[1], _box(a, self.Z(op[4]), b, self.Z(op[4]) + 0.0055), False))
        if "mag" in self.sp:
            mg = self.sp["mag"]
            feet.append(("cargador", self._side(mg["region"], mg.get("o", {})), True))
            if "base" in mg:
                feet.append(("base_cargador", self.region(mg["base"], False), True))
        rest = self.sil.difference(unary_union([f for _, f, _ in feet]).buffer(0.0004))
        for e in self.sp.get("exclude", []):
            rest = rest.difference(self.ref.poly(e))
        rest = rest.buffer(-0.0006).buffer(0.0008).intersection(self.sil)        # sin astillas
        pieces = [p for p in getattr(rest, "geoms", [rest]) if p.geom_type == "Polygon" and p.area > 6e-6]
        grown = 0.0
        for p in pieces:
            near = p.buffer(0.0015)
            best = max(((near.intersection(f).area, n) for n, f, ok in feet if ok and not f.is_empty),
                       default=(0.0, None))
            if best[0] > 2e-7:
                self.extra[best[1]] = unary_union([self.extra.get(best[1], p), p])
                grown += p.area
            elif p.buffer(-0.002).area > 0 and p.area > 3e-5:     # suelto: solo si es macizo (≥4 mm de espesor)
                self.orphans.append(p)
        lost = sum(p.area for p in self.orphans)
        if pieces:
            print(f"[hd] {self.ID}: faltante {grown * 1e6:.0f} mm2 sumado a {sorted(self.extra)}; "
                  f"suelto {lost * 1e6:.0f} mm2 en {len(self.orphans)} piezas")

    def fill(self):
        if not self.orphans:
            return []
        from shapely.geometry import MultiPolygon
        g = MultiPolygon(self.orphans) if len(self.orphans) > 1 else self.orphans[0]
        return self.solid("relleno", g.wkt, self.sp.get("fill_w", 22), self.sp.get("fill_mat", "pol"),
                          {"raw": True, "bevel": 1.0})

    def lathe_fit(self, prof, y):
        """Perfil de una pieza de revolución en metros. Con fit_lathes, el centro y el radio se ajustan a la
        silueta (mediana de 9 cortes verticales) si la medición es confiable: radio dentro de ±25 % y centro a
        menos de 0,4 radios del dibujado; si no, queda lo dibujado (caños tapados por otras piezas)."""
        pts = sorted(((self.X(x), self.mm(r)) for x, r in prof), key=lambda q: q[0])
        z = self.Z(y)
        if self.sil is None or not self.sp.get("fit_lathes") or len(pts) < 2:
            return pts, z
        from shapely.geometry import LineString
        import statistics
        rmax = max(r for _, r in pts)
        a, b = pts[0][0], pts[-1][0]
        cs, rs = [], []
        for i in range(9):
            x = a + (b - a) * (0.1 + 0.8 * i / 8)
            cut = LineString([(x, z - 3 * rmax), (x, z + 3 * rmax)]).intersection(self.sil)
            segs = [g for g in getattr(cut, "geoms", [cut]) if g.geom_type == "LineString" and g.length > 0]
            if not segs:
                continue
            seg = min(segs, key=lambda g: abs((g.bounds[1] + g.bounds[3]) / 2 - z))
            lo, hi = seg.bounds[1], seg.bounds[3]
            cs.append((lo + hi) / 2)
            rs.append((hi - lo) / 2)
        if len(rs) < 5:
            return pts, z
        c, r = statistics.median(cs), statistics.median(rs)
        if not (0.75 < r / rmax < 1.25 and abs(c - z) < 0.4 * rmax):
            return pts, z
        k = r / rmax
        return [(x, rr * k) for x, rr in pts], c

    def _side(self, reg, o):
        side = self.region(reg, o.get("cut", True))
        if o.get("sil") and self.sil is not None and not self.sp.get("sil_cut", True):   # recorte pieza a pieza
            side = side.intersection(self.sil)
        for h in o.get("holes", []):
            side = side.difference(self.ref.poly(h))
        return side

    def mag_parts(self):
        mg = self.sp["mag"]
        o = dict(mg.get("o", {}))
        out = self.solid("cargador", mg["region"], mg["w"], mg["mat"], o)
        if "base" in mg:
            out += self.solid("base_cargador", mg["base"], mg["w"] + 3, mg.get("base_mat", "pol"),
                              {"cut": False, "bevel": 1.5})
        return out

    # --- terminación
    def finish(self, P):
        for ob in P:
            if ob.type != "MESH" or not ob.data.polygons:
                continue
            w, s = ob.get("bevel", (0.0006, 1))
            hs.harden(ob, width=float(w), segs=int(s))
        return P

    def decals(self):
        """Dibuja los detalles finos en dos imágenes (lado derecho tal cual la referencia, lado izquierdo
        espejado para que el texto se lea) y las proyecta sobre todos los materiales."""
        from PIL import Image, ImageDraw, ImageFont
        ops = self.sp.get("decals", [])
        if not ops:
            return
        xs = [p[0] for p in self.bbox_px()]
        ys = [p[1] for p in self.bbox_px()]
        x0p, x1p, y0p, y1p = min(xs) - 10, max(xs) + 10, min(ys) - 10, max(ys) + 10
        s = 4
        W, H = int((x1p - x0p) * s), int((y1p - y0p) * s)
        font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        imgs = {"R": Image.new("RGBA", (W, H), (0, 0, 0, 0)), "L": Image.new("RGBA", (W, H), (0, 0, 0, 0))}

        def P(x, y):
            return ((x - x0p) * s, (y - y0p) * s)

        dark, rim = (6, 6, 7, 255), (78, 78, 74, 255)
        for op in ops:
            k, side = op[0], (op[-1] if isinstance(op[-1], str) and op[-1] in ("R", "L", "RL") else "RL")
            for sd in side if side != "RL" else "RL":
                d = ImageDraw.Draw(imgs[sd])
                if k == "slot":
                    _, a, b, c, e, *_ = op
                    d.rounded_rectangle([P(a - 1, b - 1), P(c + 1, e + 1)], radius=s * 1.5, fill=rim)
                    d.rounded_rectangle([P(a, b), P(c, e)], radius=s * 1.2, fill=dark)
                elif k == "hole":
                    _, x, y, rx, ry, *_ = op
                    d.ellipse([P(x - rx - 0.8, y - ry - 0.8), P(x + rx + 0.8, y + ry + 0.8)], fill=rim)
                    d.ellipse([P(x - rx, y - ry), P(x + rx, y + ry)], fill=dark)
                elif k == "serr":
                    _, a, c, b, e, n, *_ = op
                    wv = (c - a) / n
                    for i in range(n):
                        xa = a + i * wv
                        d.rectangle([P(xa + wv * 0.2, b), P(xa + wv * 0.55, e)], fill=dark)
                        d.rectangle([P(xa + wv * 0.55, b), P(xa + wv * 0.7, e)], fill=rim)
                elif k == "poly":
                    _, pts, col, *_ = op
                    d.polygon([P(*p) for p in pts], fill=tuple(col) + (255,))
                elif k == "line":
                    _, pts, wpx, col, *_ = op
                    d.line([P(*p) for p in pts], fill=tuple(col) + (255,), width=int(wpx * s))
                elif k == "stip":
                    _, pts, *_ = op
                    pp = [P(*p) for p in pts]
                    d.polygon(pp, fill=(26, 26, 28, 255))
                    mask = Image.new("L", (W, H), 0)
                    ImageDraw.Draw(mask).polygon(pp, fill=255)
                    dots = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    dd = ImageDraw.Draw(dots)
                    bx = [p[0] for p in pp]
                    byy = [p[1] for p in pp]
                    for yy in range(int(min(byy)), int(max(byy)), 6):
                        for xx in range(int(min(bx)) + (yy // 6) % 2 * 3, int(max(bx)), 6):
                            dd.ellipse((xx, yy, xx + 2, yy + 2), fill=(92, 93, 97, 255))
                    imgs[sd].paste(dots, (0, 0), Image.composite(dots, Image.new("RGBA", (W, H)), mask).split()[3])
                elif k == "text":
                    _, x, y, txt, size, *_ = op
                    f = ImageFont.truetype(font, int(size * s))
                    if sd == "L":     # lado izquierdo: misma ubicación, letras espejadas para que se lean
                        tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                        ImageDraw.Draw(tmp).text(P(x, y), txt, font=f, fill=(170, 170, 164, 255), anchor="mm")
                        bb = tmp.getbbox()
                        if bb:
                            glyph = tmp.crop(bb).transpose(Image.FLIP_LEFT_RIGHT)
                            imgs[sd].alpha_composite(glyph, (bb[0], bb[1]))
                    else:
                        d.text(P(x, y), txt, font=f, fill=(170, 170, 164, 255), anchor="mm")
        out = pz.ART / self.ID
        out.mkdir(parents=True, exist_ok=True)
        for sd, img in imgs.items():
            p = out / f"decal_{sd}.png"
            img.save(p)
            for m in self.mats.values():
                hs.add_decal(m, p, self.X(x0p), self.X(x1p), self.Z(y1p), self.Z(y0p), -1 if sd == "R" else 1)

    def bbox_px(self):
        pts = []
        for op in self.sp["parts"]:
            if op[0] == "s":
                reg = op[2]
                if len(reg) == 4 and not isinstance(reg[0], (tuple, list)):
                    pts += [(reg[0], reg[1]), (reg[2], reg[3])]
                else:
                    pts += list(reg)
        return pts

    def attachments(self):
        a = self.sp["att"]
        zb = self.Z(self.by)
        out = {"muzzle": (self.X(a["muzzle"]), 0.0, zb)}
        if "optic" in a:
            out["at_optic"] = (self.X(a["optic"][0]), 0.0, self.Z(a["optic"][1]) + 0.0055)
        if "light" in a:
            out["at_light"] = (self.X(a["light"][0]), 0.0, self.Z(a["light"][1]))
        return out

    def to_game(self, ob):
        from mathutils import Matrix, Vector
        K = self.sp["K"]
        off = self.sp["offset"]
        M = Matrix.Translation((off[0], 0.0, off[1])) @ Matrix.Scale(K, 4)
        ob.data.transform(M)
        return {k: tuple(M @ Vector(v)) for k, v in self.attachments().items()}


def hs_sec(w, z0, z1, ct, cb):
    h = w / 2
    ct = min(ct, h * 0.9, (z1 - z0) * 0.45)
    cb = min(cb, h * 0.9, (z1 - z0) * 0.45)
    return Polygon([(-h + cb, z0), (h - cb, z0), (h, z0 + cb), (h, z1 - ct), (h - ct, z1), (-h + ct, z1),
                    (-h, z1 - ct), (-h, z0 + cb)])


def iou(g, P):
    sp = g.sp
    if not g.sil_json:
        return None
    return hs.silhouette_iou(P, g.ref, g.sil_json, sp.get("exclude", []), sp.get("holes", []))


def build(ID, check=False, ref_dir=None, tex=512):
    pz.reset()
    g = Gun(ID)
    P = g.build_parts()
    P = g.finish(P)
    tris = hs.tri_count(P)
    r = iou(g, P)
    print(f"[hd] {ID}: {len(P)} piezas, {tris} triángulos, IoU {r[0]:.3f}" if r else
          f"[hd] {ID}: {len(P)} piezas, {tris} triángulos, IoU n/d (sin silueta calcada)")
    if check:
        return g, P, r
    g.decals()
    ob = hs.join(P, ID)
    hs.unwrap(ob)
    hs.bake_textures(ob, tex, pz.ART / ID / f"{ID}.png")
    if ref_dir:
        verify(g, ob, ref_dir)
    import gunkit as gk
    att = g.to_game(ob)
    gk.export(ob, ID, g.sp["kind"], att)
    return g, ob, r


def verify(g, ob, ref_dir):
    """Láminas de verificación (fuera del repo: llevan la imagen de referencia)."""
    from PIL import Image, ImageDraw
    from mathutils import Vector
    S = pz.ART / g.ID
    img = Path(ref_dir) / g.sp["img"]
    if g.sil_json and img.exists():
        hs.silhouette_iou([ob], g.ref, g.sil_json, g.sp.get("exclude", []), g.sp.get("holes", []), photo=str(img),
                          out=str(S / "verif_silueta.png"))
    lo = Vector([min(v.co[i] for v in ob.data.vertices) for i in range(3)])
    hi = Vector([max(v.co[i] for v in ob.data.vertices) for i in range(3)])
    c = (lo + hi) / 2
    L = hi.x - lo.x
    H = hi.z - lo.z
    views = [("der", (0, -1, 0), max(L, 2.5 * H) * 1.04, (1600, 640)),
             ("frente", (1, 0, 0), max(H, hi.y - lo.y) * 1.15, (640, 640)),
             ("arriba", (0.0, -0.0001, 1.0), max(L, 5 * (hi.y - lo.y)) * 1.04, (1600, 320)),
             ("34", (0.7, -1.0, 0.6), max(L, 2 * H) * 0.95, (1600, 760))]
    tiles = {}
    for name, d, span, size in views:
        p = S / f"_v_{name}.png"
        hs.closeup([ob], p, tuple(c), dist=1.0, direction=d, size=size, ortho=span, light=0.55)
        tiles[name] = Image.open(p).convert("RGB")
        p.unlink()
    sheet = Image.new("RGB", (2240, 1720), (46, 47, 50))
    sheet.paste(tiles["der"], (0, 0))
    sheet.paste(tiles["frente"], (1600, 0))
    sheet.paste(tiles["arriba"], (0, 640))
    sheet.paste(tiles["34"], (0, 960))
    dr = ImageDraw.Draw(sheet)
    dr.text((10, 8), g.ID, fill=(255, 220, 120))
    sheet.save(S / "verif_volumen.png")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ref_dir = sys.argv[sys.argv.index("--ref-dir") + 1] if "--ref-dir" in sys.argv else None
    if ref_dir in args:
        args.remove(ref_dir)
    for ID in args or list(hd_specs.SPEC):
        build(ID, "--check" in sys.argv, ref_dir)
