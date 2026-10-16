"""Piezas reutilizables para las armas del Arsenal (sobre pzlib).

Convención de modelado (igual que pzlib): largo sobre +X, agarre en el origen, caras planas
mirando a ±Y, +Z arriba. export_mod.py convierte después a la convención vanilla (+Y, en metros).
"""
import math

import pzlib as pz

# materiales base listos (colores oscuros/desaturados como las texturas vanilla)
def steel(name="acero", rust=.3, blood=0.0, seed=0.0):
    return pz.mat(name, (0.42, 0.44, 0.46), rust=rust, blood=blood, dirt=.3, seed=seed)


def bright_steel(name="filo", blood=0.0, seed=0.0):
    return pz.mat(name, (0.72, 0.74, 0.76), dirt=.15, blood=blood, seed=seed)


def dark_steel(name="acero_oscuro", rust=.35, seed=0.0):
    return pz.mat(name, (0.16, 0.16, 0.17), rust=rust, dirt=.25, seed=seed)


def wood(name="madera", color=pz.WOOD, seed=0.0):
    return pz.mat(name, color, streaks=True, dirt=.35, seed=seed)


def rubber(name="goma"):
    return pz.mat(name, (0.035, 0.035, 0.04), dirt=.2)


def duct(name="cinta"):
    return pz.mat(name, (0.46, 0.48, 0.50), dirt=.35)


def cloth(name="tela", color=pz.CLOTH):
    return pz.mat(name, color, dirt=.45)


# --------------------------------------------------------------- piezas
def rod(name, x0, x1, r, mat, z=0.0, segs=10, r2=None):
    """Cilindro a lo largo de X entre x0 y x1."""
    return pz.cylinder(name, r, x1 - x0, loc=((x0 + x1) / 2, 0, z), mat=mat, segs=segs, r2=r2)


def band(name, x, r, w, mat, z=0.0):
    """Abrazadera o vuelta de cinta alrededor de un mango sobre X."""
    return pz.cylinder(name, r, w, loc=(x, 0, z), mat=mat, segs=10)


def bolt(name, loc, r, mat, axis="Y", length=None):
    rot = {"X": (0, 90, 0), "Y": (90, 0, 0), "Z": (0, 0, 0)}[axis]
    return pz.cylinder(name, r, length or r * 1.6, loc=loc, rot=rot, mat=mat, segs=6, smooth=False)


def knife(name, x0, length, width, z, mat, thick=0.004, up=True, rot=0.0):
    """Hoja de cuchillo plana (cara hacia ±Y) desde x0 hacia +X; filo hacia -Z si up=True."""
    s = 1 if up else -1
    out = [(x0, z + s * width * .5), (x0 + length * .78, z + s * width * .5),
           (x0 + length, z + s * width * .15),
           (x0 + length * .80, z - s * width * .5), (x0, z - s * width * .5)]
    edge = [3, 4]
    o = pz.extrude(name, out, thick, mat=mat, taper_edge=edge)
    if rot:
        o.rotation_euler.y = math.radians(rot)
    return o


def saw_disc(name, cx, cz, r, mat, teeth=24, thick=0.003, y=0.0):
    """Disco de sierra plano (cara hacia ±Y) con dientes en el contorno."""
    pts = []
    for i in range(teeth):
        a = 2 * math.pi * i / teeth
        b = a + 2 * math.pi / teeth * .65
        pts.append((cx + r * .86 * math.cos(a), cz + r * .86 * math.sin(a)))
        pts.append((cx + r * math.cos(b), cz + r * math.sin(b)))
    o = pz.extrude(name, pts, thick, mat=mat)
    o.location.y = y
    return o


def spike(name, base, direction, length, r, mat):
    """Púa cónica desde base apuntando en direction (vector XZ normalizado)."""
    dx, dz = direction
    ang = math.degrees(math.atan2(dx, dz))
    cx, cz = base[0] + dx * length / 2, base[1] + dz * length / 2
    return pz.cylinder(name, r, length, loc=(cx, 0, cz), rot=(0, ang, 0), mat=mat, segs=6, r2=r * .05, smooth=False)


def decal_png(path, size, draw):
    """Genera un PNG de calco con PIL: draw(ImageDraw, w, h)."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", size, (0, 0, 0))
    draw(ImageDraw.Draw(img), *size)
    img.save(path)
    return path
