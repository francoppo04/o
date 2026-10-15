"""Primitivas SVG para el concept art de Arsenal de Chatarra.

Cada arma se dibuja en horizontal (mango a la izquierda, cabeza a la derecha)
dentro de un viewBox de 1400x800 con el eje en y=400; la ficha la rota después.
"""
import math
import random

OL = 'stroke="#0b0b0c" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"'
OL_THIN = 'stroke="#0b0b0c" stroke-width="2" stroke-linejoin="round"'

_uid = [0]


def uid(prefix="u"):
    _uid[0] += 1
    return f"{prefix}{_uid[0]}"


DEFS = """
<defs>
  <linearGradient id="gSteel" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#22262a"/><stop offset=".16" stop-color="#5f676f"/>
    <stop offset=".34" stop-color="#e4e9ed"/><stop offset=".5" stop-color="#a3acb4"/>
    <stop offset=".78" stop-color="#4c535a"/><stop offset="1" stop-color="#1b1e21"/>
  </linearGradient>
  <linearGradient id="gSteelDark" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#16181b"/><stop offset=".3" stop-color="#5a6168"/>
    <stop offset=".5" stop-color="#7d868e"/><stop offset=".8" stop-color="#33383d"/>
    <stop offset="1" stop-color="#121416"/>
  </linearGradient>
  <linearGradient id="gSteelBlock" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#1f2327"/><stop offset=".22" stop-color="#6c747c"/>
    <stop offset=".42" stop-color="#c9d0d6"/><stop offset=".62" stop-color="#7a838b"/>
    <stop offset="1" stop-color="#202428"/>
  </linearGradient>
  <linearGradient id="gBlade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#4a5157"/><stop offset=".25" stop-color="#9aa3ab"/>
    <stop offset=".55" stop-color="#d9dfe4"/><stop offset=".72" stop-color="#f6f8fa"/>
    <stop offset=".86" stop-color="#8e979f"/><stop offset="1" stop-color="#3c4248"/>
  </linearGradient>
  <linearGradient id="gBladeV" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#3c4248"/><stop offset=".3" stop-color="#9aa3ab"/>
    <stop offset=".6" stop-color="#e9eef2"/><stop offset="1" stop-color="#5b636a"/>
  </linearGradient>
  <linearGradient id="gForged" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#121315"/><stop offset=".35" stop-color="#2e3236"/>
    <stop offset=".6" stop-color="#4a4f54"/><stop offset=".72" stop-color="#c2c9cf"/>
    <stop offset=".86" stop-color="#eef2f5"/><stop offset="1" stop-color="#7d868d"/>
  </linearGradient>
  <linearGradient id="gWood" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2f1708"/><stop offset=".18" stop-color="#7a4520"/>
    <stop offset=".38" stop-color="#c88d55"/><stop offset=".55" stop-color="#a86d3a"/>
    <stop offset=".82" stop-color="#5e3315"/><stop offset="1" stop-color="#2a1406"/>
  </linearGradient>
  <linearGradient id="gWoodLight" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#5a3a1c"/><stop offset=".2" stop-color="#b98a55"/>
    <stop offset=".4" stop-color="#ead2a6"/><stop offset=".6" stop-color="#cfa774"/>
    <stop offset=".85" stop-color="#8a6236"/><stop offset="1" stop-color="#4a2e12"/>
  </linearGradient>
  <linearGradient id="gRubber" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#050506"/><stop offset=".35" stop-color="#3b3d41"/>
    <stop offset=".5" stop-color="#2a2b2e"/><stop offset="1" stop-color="#070708"/>
  </linearGradient>
  <linearGradient id="gDuct" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3e4246"/><stop offset=".3" stop-color="#9ca2a7"/>
    <stop offset=".45" stop-color="#d3d8dc"/><stop offset=".7" stop-color="#868c91"/>
    <stop offset="1" stop-color="#34383b"/>
  </linearGradient>
  <linearGradient id="gCloth" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#5b5142"/><stop offset=".35" stop-color="#d9ccb0"/>
    <stop offset=".55" stop-color="#efe6d2"/><stop offset="1" stop-color="#6d624f"/>
  </linearGradient>
  <linearGradient id="gRed" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#4a0607"/><stop offset=".3" stop-color="#b3161a"/>
    <stop offset=".5" stop-color="#e2383a"/><stop offset=".8" stop-color="#7d0c0e"/>
    <stop offset="1" stop-color="#3a0405"/>
  </linearGradient>
  <linearGradient id="gYellow" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#5e4106"/><stop offset=".25" stop-color="#d79b12"/>
    <stop offset=".42" stop-color="#ffd85a"/><stop offset=".62" stop-color="#e2a516"/>
    <stop offset="1" stop-color="#4f3604"/>
  </linearGradient>
  <linearGradient id="gGreen" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0f2a12"/><stop offset=".3" stop-color="#2f7a35"/>
    <stop offset=".45" stop-color="#5fb866"/><stop offset=".7" stop-color="#245e29"/>
    <stop offset="1" stop-color="#0c200e"/>
  </linearGradient>
  <linearGradient id="gShade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#000" stop-opacity=".6"/><stop offset=".22" stop-color="#fff" stop-opacity=".16"/>
    <stop offset=".42" stop-color="#fff" stop-opacity="0"/><stop offset=".78" stop-color="#000" stop-opacity=".22"/>
    <stop offset="1" stop-color="#000" stop-opacity=".65"/>
  </linearGradient>
  <linearGradient id="gOrange" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#5a1d02"/><stop offset=".25" stop-color="#d4570f"/>
    <stop offset=".42" stop-color="#ff9a4a"/><stop offset=".65" stop-color="#d9520c"/>
    <stop offset="1" stop-color="#4a1702"/>
  </linearGradient>
  <linearGradient id="gBrassLin" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#4a3204"/><stop offset=".3" stop-color="#c8962a"/>
    <stop offset=".45" stop-color="#fff0b0"/><stop offset=".7" stop-color="#b07f1c"/>
    <stop offset="1" stop-color="#3a2602"/>
  </linearGradient>
  <linearGradient id="gWeb" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#2a2d31"/><stop offset=".5" stop-color="#6c727a"/>
    <stop offset="1" stop-color="#25282b"/>
  </linearGradient>
  <linearGradient id="gPaint" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#1b2631"/><stop offset=".35" stop-color="#3f566b"/>
    <stop offset=".55" stop-color="#5b748a"/><stop offset="1" stop-color="#18222b"/>
  </linearGradient>
  <radialGradient id="gBurst" cx=".52" cy=".45" r=".62">
    <stop offset="0" stop-color="#f6c063"/><stop offset=".35" stop-color="#e0822a"/>
    <stop offset=".7" stop-color="#8e2a0c"/><stop offset="1" stop-color="#1e0703"/>
  </radialGradient>
  <radialGradient id="gIron" cx=".42" cy=".38" r=".7">
    <stop offset="0" stop-color="#5d6267"/><stop offset=".55" stop-color="#2f3337"/>
    <stop offset="1" stop-color="#121315"/>
  </radialGradient>
  <radialGradient id="gConcrete" cx=".4" cy=".35" r=".8">
    <stop offset="0" stop-color="#bdb8ae"/><stop offset=".6" stop-color="#8a857c"/>
    <stop offset="1" stop-color="#4a4741"/>
  </radialGradient>
  <radialGradient id="gEmber" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="#ffe7a0"/><stop offset=".4" stop-color="#ff7a1a" stop-opacity=".8"/>
    <stop offset="1" stop-color="#ff3a00" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="gDisc" cx=".38" cy=".32" r=".75">
    <stop offset="0" stop-color="#f4f7f9"/><stop offset=".45" stop-color="#a7b0b8"/>
    <stop offset=".8" stop-color="#5a626a"/><stop offset="1" stop-color="#2d3237"/>
  </radialGradient>
  <radialGradient id="gBolt" cx=".35" cy=".3" r=".8">
    <stop offset="0" stop-color="#ffffff"/><stop offset=".35" stop-color="#b4bbc2"/>
    <stop offset=".75" stop-color="#4b5258"/><stop offset="1" stop-color="#1c1f22"/>
  </radialGradient>
  <radialGradient id="gBrass" cx=".35" cy=".3" r=".8">
    <stop offset="0" stop-color="#fff6c8"/><stop offset=".35" stop-color="#e3b84a"/>
    <stop offset=".8" stop-color="#7a5510"/><stop offset="1" stop-color="#3a2804"/>
  </radialGradient>
  <radialGradient id="gBlood" cx=".4" cy=".35" r=".85">
    <stop offset="0" stop-color="#a51212"/><stop offset=".55" stop-color="#6a0707"/>
    <stop offset="1" stop-color="#300202"/>
  </radialGradient>
  <radialGradient id="gWeld" cx=".4" cy=".35" r=".8">
    <stop offset="0" stop-color="#e2dccf"/><stop offset=".5" stop-color="#8f7d63"/>
    <stop offset="1" stop-color="#3a2c1c"/>
  </radialGradient>
  <filter id="fRust" filterUnits="userSpaceOnUse" x="-400" y="-400" width="2200" height="1600">
    <feTurbulence type="fractalNoise" baseFrequency="0.022" numOctaves="4" seed="7" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.36  0 0 0 0 0.17  0 0 0 0 0.06  0 0 0 -5 2.45" result="rust0"/>
    <feComponentTransfer in="rust0" result="rust"><feFuncA type="linear" slope=".42"/></feComponentTransfer>
    <feComposite in="rust" in2="SourceGraphic" operator="in" result="rustIn"/>
    <feTurbulence type="fractalNoise" baseFrequency="0.55" numOctaves="2" seed="11" result="fine"/>
    <feColorMatrix in="fine" type="matrix" values="0 0 0 0 0.05  0 0 0 0 0.04  0 0 0 0 0.03  0 0 0 -2.6 1.5" result="specks"/>
    <feComposite in="specks" in2="SourceGraphic" operator="in" result="specksIn"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="rustIn"/><feMergeNode in="specksIn"/></feMerge>
  </filter>
  <filter id="fWear" filterUnits="userSpaceOnUse" x="-400" y="-400" width="2200" height="1600">
    <feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="2" seed="4" result="fine"/>
    <feColorMatrix in="fine" type="matrix" values="0 0 0 0 0.08  0 0 0 0 0.06  0 0 0 0 0.05  0 0 0 -2.4 1.3" result="specks"/>
    <feComposite in="specks" in2="SourceGraphic" operator="in" result="specksIn"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="specksIn"/></feMerge>
  </filter>
  <filter id="fGrain" filterUnits="userSpaceOnUse" x="-400" y="-400" width="2200" height="1600">
    <feTurbulence type="fractalNoise" baseFrequency="0.0025 0.11" numOctaves="3" seed="5" result="g"/>
    <feColorMatrix in="g" type="matrix" values="0 0 0 0 0.16  0 0 0 0 0.07  0 0 0 0 0.02  0 0 0 -4 2.3" result="grain"/>
    <feComposite in="grain" in2="SourceGraphic" operator="in" result="grainIn"/>
    <feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="grainIn"/></feMerge>
  </filter>
  <filter id="fDrop" filterUnits="userSpaceOnUse" x="-400" y="-400" width="2200" height="1600">
    <feGaussianBlur in="SourceAlpha" stdDeviation="16"/>
    <feOffset dx="10" dy="26" result="b"/>
    <feComponentTransfer><feFuncA type="linear" slope=".75"/></feComponentTransfer>
    <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="fGlow" filterUnits="userSpaceOnUse" x="-400" y="-400" width="2200" height="1600">
    <feGaussianBlur stdDeviation="9" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>
"""


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def pts(points):
    return " ".join(f"{f(x)},{f(y)}" for x, y in points)


def poly(points, fill, extra=OL):
    return f'<polygon points="{pts(points)}" fill="{fill}" {extra}/>'


def path(d, fill, extra=OL):
    return f'<path d="{d}" fill="{fill}" {extra}/>'


def rect(x, y, w, h, fill, rx=0, extra=OL):
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(rx)}" fill="{fill}" {extra}/>'


def circle(cx, cy, r, fill, extra=OL):
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}" {extra}/>'


def ellipse(cx, cy, rx, ry, fill, extra=OL, rot=0):
    t = f' transform="rotate({f(rot)} {f(cx)} {f(cy)})"' if rot else ""
    return f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="{fill}" {extra}{t}/>'


def line(x1, y1, x2, y2, color, w=2, op=1.0):
    return (f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{color}" '
            f'stroke-width="{f(w)}" stroke-opacity="{op}" stroke-linecap="round"/>')


def group(content, transform="", filt=None, extra=""):
    t = f' transform="{transform}"' if transform else ""
    fl = f' filter="url(#{filt})"' if filt else ""
    return f"<g{t}{fl} {extra}>{content}</g>"


def smooth_closed(points):
    """Curva cerrada suave (Catmull-Rom -> Bezier) que pasa por los puntos."""
    n = len(points)
    d = f"M{f(points[0][0])},{f(points[0][1])}"
    for i in range(n):
        p0, p1, p2, p3 = points[i - 1], points[i], points[(i + 1) % n], points[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}"
    return d + "Z"


# ---------------------------------------------------------------- componentes

def cylinder(x1, x2, yc, th, fill, rx=None, filt=None, shade=True):
    """Barra/mango cilíndrico horizontal."""
    r = th * 0.22 if rx is None else rx
    body = rect(x1, yc - th / 2, x2 - x1, th, fill, r)
    if shade:
        body += rect(x1, yc - th / 2, x2 - x1, th, "url(#gShade)", r, 'stroke="none"')
    return group(body, filt=filt)


def wrap(x1, x2, yc, th, fill, band=24, slant=12, line_color="#000", filt=None, pad=2):
    """Vendaje/cinta enrollada en diagonal sobre un mango."""
    cid = uid("clip")
    top, bot = yc - th / 2 - pad, yc + th / 2 + pad
    clip = f'<clipPath id="{cid}"><rect x="{f(x1)}" y="{f(top)}" width="{f(x2 - x1)}" height="{f(bot - top)}" rx="{f(th * .2)}"/></clipPath>'
    bands = ""
    x = x1 - slant
    while x < x2 + slant:
        bands += poly([(x, top), (x + band, top), (x + band + slant, bot), (x + slant, bot)], fill,
                      f'stroke="{line_color}" stroke-opacity=".55" stroke-width="2"')
        bands += line(x + band - 3, top, x + band + slant - 3, bot, "#fff", 1.5, .18)
        x += band - 2
    shade = rect(x1, top, x2 - x1, bot - top, "url(#gShade)", th * .2, 'stroke="none"')
    outline = rect(x1, top, x2 - x1, bot - top, "none", th * .2, OL)
    inner = group(bands + shade, extra=f'clip-path="url(#{cid})"')
    return clip + group(inner, filt=filt) + outline


def band(x, yc, th, w, fill="url(#gSteel)", bolt=True):
    """Abrazadera metálica alrededor de un mango."""
    s = rect(x, yc - th / 2 - 5, w, th + 10, fill, 3)
    s += rect(x, yc - th / 2 - 5, w, th + 10, "url(#gShade)", 3, 'stroke="none"')
    for k in range(1, 4):
        s += line(x + w * k / 4, yc - th / 2 - 3, x + w * k / 4, yc + th / 2 + 3, "#000", 1.2, .35)
    if bolt:
        s += rect(x + w / 2 - 8, yc - th / 2 - 16, 16, 13, "url(#gSteelBlock)", 2, OL_THIN)
        s += circle(x + w / 2, yc - th / 2 - 10, 4, "url(#gBolt)", OL_THIN)
    return s


def bolt(cx, cy, r=8, fill="url(#gBolt)", hexa=True):
    s = ""
    if hexa:
        hp = [(cx + r * 1.25 * math.cos(math.pi / 3 * k + .3), cy + r * 1.25 * math.sin(math.pi / 3 * k + .3)) for k in range(6)]
        s += poly(hp, "url(#gSteelDark)", OL_THIN)
    s += circle(cx, cy, r, fill, OL_THIN)
    s += circle(cx - r * .3, cy - r * .35, r * .28, "#fff", 'stroke="none" opacity=".7"')
    return s


def nail(x, y, ang, length=70, w=7, bent=0):
    """Clavo saliendo de una superficie en (x, y) con ángulo en grados."""
    tip = length + 16
    g = rect(0, -w / 2, length, w, "url(#gSteel)", 1, OL_THIN)
    g += poly([(length - 1, -w / 2), (tip, 0), (length - 1, w / 2)], "url(#gSteel)", OL_THIN)
    g += line(2, -w / 2 + 1.5, length, -w / 2 + 1.5, "#fff", 1.2, .55)
    g += ellipse(0, 0, 4, w * .9, "url(#gSteelDark)", OL_THIN)
    t = f"translate({f(x)} {f(y)}) rotate({f(ang)})"
    if bent:
        t += f" skewY({f(bent)})"
    return group(g, t)


def weld(x1, y1, x2, y2, r=6):
    """Cordón de soldadura entre dos puntos."""
    n = max(2, int(math.hypot(x2 - x1, y2 - y1) / (r * 1.1)))
    s = ""
    for i in range(n + 1):
        t = i / n
        s += circle(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, r, "url(#gWeld)", 'stroke="#1a120a" stroke-width="1.2"')
    return s


def saw_blade(cx, cy, r, teeth=28, rot=0, filt="fRust", hub=True):
    step = 2 * math.pi / teeth
    p = []
    for i in range(teeth):
        a = i * step + math.radians(rot)
        p.append((cx + r * .86 * math.cos(a), cy + r * .86 * math.sin(a)))
        p.append((cx + r * math.cos(a + step * .62), cy + r * math.sin(a + step * .62)))
        p.append((cx + r * .9 * math.cos(a + step * .75), cy + r * .9 * math.sin(a + step * .75)))
    s = poly(p, "url(#gDisc)")
    for i in range(teeth):  # puntas de carburo
        a = i * step + math.radians(rot) + step * .62
        s += circle(cx + r * .97 * math.cos(a), cy + r * .97 * math.sin(a), r * .025, "#d8dde1", 'stroke="#222" stroke-width="1"')
    s += circle(cx, cy, r * .8, "none", 'stroke="#fff" stroke-opacity=".25" stroke-width="2"')
    s += circle(cx, cy, r * .62, "none", 'stroke="#000" stroke-opacity=".25" stroke-width="1.5"')
    for k in range(4):  # ranuras de expansión
        a = math.radians(rot + 20 + k * 90)
        s += line(cx + r * .55 * math.cos(a), cy + r * .55 * math.sin(a),
                  cx + r * .8 * math.cos(a + .08), cy + r * .8 * math.sin(a + .08), "#111", 3, .8)
        s += circle(cx + r * .8 * math.cos(a + .08), cy + r * .8 * math.sin(a + .08), 3.5, "#111", 'stroke="none"')
    # reflejo
    s += path(f"M{f(cx - r * .7)},{f(cy - r * .1)} A{f(r * .72)},{f(r * .72)} 0 0 1 {f(cx + r * .1)},{f(cy - r * .7)}",
              "none", 'stroke="#fff" stroke-opacity=".45" stroke-width="5" stroke-linecap="round"')
    if hub:
        s += circle(cx, cy, r * .26, "url(#gSteelBlock)")
        s += bolt(cx, cy, r * .11)
    return group(s, filt=filt)


def blood(x, y, s, seed, drops=8, drip=0, op=.93):
    rnd = random.Random(seed)
    n = 13
    p = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = s * rnd.uniform(.55, 1.0)
        p.append((x + rr * math.cos(a), y + rr * .8 * math.sin(a)))
    out = path(smooth_closed(p), "url(#gBlood)", f'stroke="none" opacity="{op}"')
    for _ in range(drops):
        a = rnd.uniform(0, 2 * math.pi)
        d = s * rnd.uniform(1.1, 2.6)
        rr = s * rnd.uniform(.05, .17)
        cx, cy = x + d * math.cos(a), y + d * .8 * math.sin(a)
        out += ellipse(cx, cy, rr * rnd.uniform(1.2, 2.4), rr, "url(#gBlood)",
                       f'stroke="none" opacity="{op}"', math.degrees(a))
    if drip:
        out += path(f"M{f(x - s * .25)},{f(y)} q{f(s * .05)},{f(drip * .7)} {f(s * .1)},{f(drip)} "
                    f"a{f(s * .09)},{f(s * .09)} 0 1 0 {f(s * .16)},0 q{f(s * .02)},{f(-drip * .5)} {f(s * .12)},{f(-drip)} Z",
                    "url(#gBlood)", f'stroke="none" opacity="{op}"')
    out += ellipse(x - s * .25, y - s * .3, s * .22, s * .09, "#fff", 'stroke="none" opacity=".3"', -20)
    return out


def barbed_wire(x1, x2, yc, amp, period=60, barbs_every=2):
    """Alambre de púas enrollado (onda) entre x1 y x2."""
    d = f"M{f(x1)},{f(yc - amp)}"
    x = x1
    up = True
    while x < x2:
        nx = min(x + period / 2, x2)
        d += f" Q{f((x + nx) / 2 + 8)},{f(yc)} {f(nx)},{f(yc + (amp if up else -amp))}"
        up = not up
        x = nx
    s = path(d, "none", 'stroke="#0b0b0c" stroke-width="8" stroke-linecap="round"')
    s += path(d, "none", 'stroke="#8d969e" stroke-width="4.5" stroke-linecap="round"')
    s += path(d, "none", 'stroke="#e9eef2" stroke-width="1.5" stroke-opacity=".7" stroke-linecap="round"')
    x = x1 + period / 4
    k = 0
    while x < x2:
        if k % barbs_every == 0:
            y = yc + (amp * .2 if k % 2 else -amp * .2)
            for a in (35, -35, 145, -145):
                r = math.radians(a)
                s += line(x, y, x + 15 * math.cos(r), y + 15 * math.sin(r), "#0b0b0c", 5)
                s += line(x, y, x + 15 * math.cos(r), y + 15 * math.sin(r), "#b5bdc4", 2.2)
        x += period / 2
        k += 1
    return s


def knife_blade(x, y, length, width, fill="url(#gBlade)", serrated=False, tanto=False):
    """Hoja de cuchillo apuntando a la derecha; (x, y) = base del lomo."""
    spine = y
    edge = y + width
    tip_x = x + length
    if tanto:
        d = f"M{f(x)},{f(spine)} L{f(tip_x - width * .5)},{f(spine)} L{f(tip_x)},{f(spine + width * .45)} L{f(tip_x - width * .3)},{f(edge)} L{f(x)},{f(edge)} Z"
    else:
        d = (f"M{f(x)},{f(spine)} L{f(tip_x - length * .22)},{f(spine)} Q{f(tip_x - length * .05)},{f(spine + width * .1)} {f(tip_x)},{f(spine + width * .55)} "
             f"Q{f(tip_x - length * .25)},{f(edge + width * .05)} {f(x + length * .3)},{f(edge)} L{f(x)},{f(edge)} Z")
    s = path(d, fill)
    # bisel del filo
    s += path(f"M{f(x)},{f(edge - width * .28)} L{f(x + length * .32)},{f(edge - width * .28)} Q{f(tip_x - length * .25)},{f(edge - width * .2)} {f(tip_x - 4)},{f(spine + width * .55)}",
              "none", 'stroke="#fff" stroke-opacity=".55" stroke-width="2"')
    s += line(x + 6, spine + 3, tip_x - length * .24, spine + 3, "#fff", 1.6, .5)
    if serrated:
        k = x + 10
        while k < x + length * .35:
            s += circle(k, edge, 4, "#2a2e33", 'stroke="none"')
            k += 13
    return s


def rr_path(x, y, w, h, r):
    """Rectángulo redondeado como subpath (para recortes con evenodd)."""
    return (f"M{f(x + r)},{f(y)} H{f(x + w - r)} A{f(r)},{f(r)} 0 0 1 {f(x + w)},{f(y + r)} V{f(y + h - r)} "
            f"A{f(r)},{f(r)} 0 0 1 {f(x + w - r)},{f(y + h)} H{f(x + r)} A{f(r)},{f(r)} 0 0 1 {f(x)},{f(y + h - r)} "
            f"V{f(y + r)} A{f(r)},{f(r)} 0 0 1 {f(x + r)},{f(y)} Z")


def sparkle(x, y, s=22):
    d = (f"M{f(x)},{f(y - s)} Q{f(x + s * .12)},{f(y - s * .12)} {f(x + s)},{f(y)} Q{f(x + s * .12)},{f(y + s * .12)} {f(x)},{f(y + s)} "
         f"Q{f(x - s * .12)},{f(y + s * .12)} {f(x - s)},{f(y)} Q{f(x - s * .12)},{f(y - s * .12)} {f(x)},{f(y - s)} Z")
    return group(path(d, "#fff", 'stroke="none" opacity=".9"') + circle(x, y, s * .18, "#fff", 'stroke="none"'), filt="fGlow")


def barbed_coil(x1, x2, yc, half_at, pitch=64):
    """Alambre de púas enrollado en hélice sobre un cilindro.
    half_at(x) da el medio grosor del cilindro en x. Devuelve (detrás, delante)."""
    back = front = ""
    x = x1
    while x + pitch / 2 <= x2:
        h1, h2 = half_at(x) + 5, half_at(x + pitch / 2) + 5
        fx = f"M{f(x)},{f(yc - h1)} Q{f(x + pitch * .3)},{f(yc)} {f(x + pitch / 2)},{f(yc + h2)}"
        bx2 = x + pitch
        h3 = half_at(min(bx2, x2)) + 5
        bk = f"M{f(x + pitch / 2)},{f(yc + h2)} Q{f(x + pitch * .8)},{f(yc)} {f(bx2)},{f(yc - h3)}"
        back += path(bk, "none", 'stroke="#0b0b0c" stroke-width="7" stroke-linecap="round"')
        back += path(bk, "none", 'stroke="#5d656c" stroke-width="3.5" stroke-linecap="round"')
        for d in (fx,):
            front += path(d, "none", 'stroke="#0b0b0c" stroke-width="8" stroke-linecap="round"')
            front += path(d, "none", 'stroke="#9aa3ab" stroke-width="4.5" stroke-linecap="round"')
            front += path(d, "none", 'stroke="#f0f4f7" stroke-width="1.5" stroke-opacity=".75" stroke-linecap="round"')
        mx, my = x + pitch * .27, yc - h1 * .05
        for a in (40, -40, 140, -140):
            r = math.radians(a)
            front += line(mx, my, mx + 16 * math.cos(r), my + 16 * math.sin(r), "#0b0b0c", 5)
            front += line(mx, my, mx + 16 * math.cos(r), my + 16 * math.sin(r), "#c2cad1", 2.2)
        x += pitch
    return back, front
