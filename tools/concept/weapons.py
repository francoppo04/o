"""Ilustraciones de cada arma (SVG) y sus textos para el concept art."""
import math

from art import (OL, OL_THIN, band, barbed_coil, blood, bolt, circle, cylinder, ellipse, f, group,
                 knife_blade, line, nail, path, poly, rect, rr_path, saw_blade, sparkle, weld, wrap)


# ------------------------------------------------------------------ 01
def hachamazo():
    s = ""
    s += cylinder(130, 1075, 400, 40, "url(#gYellow)", filt="fWear")
    s += line(380, 388, 1060, 388, "#fff", 2, .35)
    grip = cylinder(110, 380, 400, 50, "url(#gRubber)", rx=14)
    for x in range(130, 372, 16):
        grip += line(x, 377, x, 423, "#000", 3, .55) + line(x + 2, 378, x + 2, 422, "#6d7075", 1, .5)
    s += grip + ellipse(110, 400, 12, 25, "url(#gRubber)")
    s += band(880, 400, 40, 26) + band(950, 400, 40, 26)
    head = path("M1032,176 L1050,148 L1170,148 L1188,176 L1188,300 L1032,300 Z", "url(#gSteelBlock)")
    head += rect(1050, 148, 120, 14, "#e8edf1", 2, 'stroke="none" opacity=".55"')
    head += line(1036, 178, 1184, 178, "#000", 2, .4)
    head += line(1110, 182, 1110, 296, "#fff", 3, .18)
    s += group(head, filt="fRust")
    s += group(rect(1040, 296, 140, 110, "url(#gSteelDark)", 6), filt="fRust")
    s += bolt(1075, 352, 11) + bolt(1145, 352, 11)
    s += weld(1036, 300, 1184, 300, 6)
    blade = path("M1044,404 L1176,404 L1236,500 Q1170,610 1040,598 Q996,566 984,512 Z", "url(#gBladeV)")
    blade += path("M1054,416 L1166,416 L1206,486 Q1150,560 1050,556 Q1016,534 1008,500 Z", "url(#gRed)",
                  'stroke="#2a0404" stroke-width="2"')
    for x1, y1, x2, y2 in ((1070, 470, 1110, 520), (1130, 450, 1150, 500), (1060, 530, 1100, 540)):
        blade += line(x1, y1, x2, y2, "#d7dde2", 2, .55)
    blade += path("M1236,500 Q1170,610 1040,598", "none", 'stroke="#fff" stroke-width="4" stroke-opacity=".8"')
    s += group(blade, filt="fRust")
    s += weld(1040, 406, 1180, 406, 6)
    s += blood(1150, 560, 34, 3, drops=9, drip=40)
    s += blood(1160, 190, 18, 9, drops=6)
    s += blood(700, 405, 12, 21, drops=5)
    s += sparkle(1226, 512, 26)
    return s


# ------------------------------------------------------------------ 02
def bate_erizo():
    s = ""
    d = ("M120,372 Q96,372 96,400 Q96,428 120,428 L150,428 Q160,418 170,416 L560,418 "
         "Q760,448 980,452 L1230,452 Q1290,452 1290,400 Q1290,348 1230,348 L980,348 Q760,352 560,382 "
         "L170,384 Q160,382 150,372 Z")

    def half(x):
        return 52 if x >= 980 else 18 + (x - 560) / 420 * 34

    back, front = barbed_coil(790, 1250, 400, half, pitch=66)
    # clavos (detrás del bate)
    for i, x in enumerate((830, 905, 980, 1055, 1130, 1205)):
        s += nail(x, 352, -90 - 12 + (i % 3) * 10, 64 + (i % 2) * 12)
    for i, x in enumerate((865, 940, 1020, 1095, 1175)):
        s += nail(x, 448, 90 + 12 - (i % 3) * 10, 60 + (i % 2) * 14)
    s += saw_blade(1170, 330, 120, teeth=30, rot=8)
    s += back
    s += group(path(d, "url(#gWood)") + path(d, "url(#gShade)", 'stroke="none" opacity=".5"'), filt="fGrain")
    s += path("M1080,349 L1262,349", "none", 'stroke="#000" stroke-width="6" stroke-opacity=".55"')
    s += wrap(170, 470, 400, 36, "url(#gCloth)", band=22, slant=12)
    s += front
    s += bolt(1290, 400, 9)
    s += blood(1200, 300, 40, 5, drops=10)
    s += blood(1000, 420, 26, 12, drops=7, drip=36)
    s += blood(880, 385, 14, 14, drops=4)
    s += sparkle(1255, 228, 22)
    return s


# ------------------------------------------------------------------ 03
def garras():
    s = ""
    # cuchillos (debajo de la cinta, encima del guante)
    knives = ""
    for k, (y, ang, ln) in enumerate(((268, -8, 470), (352, 0, 520), (436, 8, 470))):
        kn = rect(610, y + 4, 170, 34, "url(#gRubber)", 8)
        kn += circle(650, y + 21, 4, "url(#gBolt)", OL_THIN) + circle(700, y + 21, 4, "url(#gBolt)", OL_THIN)
        kn += rect(772, y, 14, 42, "url(#gSteelBlock)", 3, OL_THIN)
        kn += knife_blade(786, y + 2, ln, 40)
        knives += group(kn, f"rotate({ang} 700 {y + 21})")
    # puño
    cuff = rect(300, 300, 190, 200, "url(#gRed)", 34)
    glove_d = ("M450,300 C470,205 640,170 770,198 C890,226 930,330 912,410 C896,486 806,526 700,522 "
               "L520,518 C470,516 446,486 446,452 Z")
    glove = path(glove_d, "url(#gRed)")
    glove += path("M470,312 C520,240 650,215 760,232", "none", 'stroke="#ffb3a8" stroke-width="3" stroke-dasharray="9 7" stroke-opacity=".7"')
    glove += ellipse(640, 250, 120, 34, "#fff", 'stroke="none" opacity=".22"', -8)
    thumb = path("M520,470 C560,450 700,452 772,486 C790,520 700,560 600,548 C540,540 500,510 520,470 Z", "url(#gRed)")
    thumb += path("M560,478 C620,470 700,478 750,496", "none", 'stroke="#000" stroke-width="2" stroke-opacity=".35"')
    s += group(cuff, filt="fWear")
    s += wrap(318, 476, 400, 196, "url(#gCloth)", band=26, slant=6)
    s += group(glove + thumb, filt="fWear")
    s += knives
    # cinta americana que ata los cuchillos al guante
    for x in (628, 720):
        tape = path(f"M{x},196 L{x + 62},190 L{x + 66},530 L{x + 4},534 Z", "url(#gDuct)")
        tape += path(f"M{x},196 l8,-8 l8,8 l10,-7 l10,7 l10,-6 l10,8 l6,-8", "none", 'stroke="#2a2d30" stroke-width="2"')
        for yy in range(220, 520, 26):
            tape += line(x + 6, yy, x + 60, yy - 2, "#fff", 1, .18)
        s += group(tape, filt="fWear")
    s += blood(1180, 352, 30, 31, drops=9)
    s += blood(1090, 470, 22, 32, drops=6, drip=30)
    s += blood(820, 250, 16, 33, drops=5)
    s += sparkle(1300, 372, 24)
    return s


# ------------------------------------------------------------------ 04
def remo():
    s = ""

    def paddle(cx, flip):
        k = -1 if flip else 1
        d = (f"M{cx - 150 * k},388 C{cx - 90 * k},300 {cx + 10 * k},282 {cx + 100 * k},292 "
             f"C{cx + 140 * k},320 {cx + 140 * k},480 {cx + 100 * k},508 C{cx + 10 * k},518 {cx - 90 * k},500 {cx - 150 * k},412 Z")
        p = path(d, "url(#gOrange)")
        p += path(f"M{cx - 80 * k},400 L{cx + 70 * k},400", "none", 'stroke="#000" stroke-width="3" stroke-opacity=".35"')
        return group(p, filt="fWear")

    s += cylinder(220, 1180, 400, 30, "url(#gSteel)", filt="fWear")
    s += paddle(1250, False) + paddle(150, True)
    s += wrap(480, 620, 400, 30, "url(#gRubber)", band=14, slant=8, line_color="#555")
    s += wrap(780, 920, 400, 30, "url(#gRubber)", band=14, slant=8, line_color="#555")
    s += saw_blade(1262, 400, 98, teeth=28, rot=4)
    s += saw_blade(138, 400, 98, teeth=28, rot=22)
    for cx in (138, 1262):
        for a in (0, 120, 240):
            r = math.radians(a + 30)
            s += bolt(cx + 52 * math.cos(r), 400 + 52 * math.sin(r), 6)
    s += blood(1300, 330, 38, 41, drops=10)
    s += blood(1200, 470, 22, 42, drops=6, drip=30)
    s += blood(120, 450, 20, 43, drops=6)
    s += sparkle(1370, 360, 24)
    return s


# ------------------------------------------------------------------ 05
def tridente():
    s = ""
    s += cylinder(90, 830, 400, 34, "url(#gWoodLight)", filt="fGrain")
    s += ellipse(92, 400, 12, 17, "url(#gWoodLight)")
    s += path("M800,380 L900,372 L900,428 L800,420 Z", "url(#gSteelDark)")
    s += band(820, 400, 40, 18, bolt=False)
    tines = ["M900,400 C900,300 940,282 1010,282 L1110,282", "M900,400 L1110,400",
             "M900,400 C900,500 940,518 1010,518 L1110,518"]
    for d in tines:
        s += path(d, "none", 'stroke="#0b0b0c" stroke-width="24" stroke-linecap="round"')
        s += path(d, "none", 'stroke="#59626a" stroke-width="17" stroke-linecap="round"')
        s += path(d, "none", 'stroke="#c9d0d6" stroke-width="5" stroke-linecap="round" stroke-opacity=".8"')
    s = group(s, filt="fRust")
    for y, big in ((282, False), (400, True), (518, False)):
        w = 52 if big else 38
        ln = 290 if big else 240
        s += rect(1030, y - 13, 110, 26, "url(#gRubber)", 6)
        s += knife_blade(1130, y - w * .45, ln, w)
        for x in (1048, 1094):
            s += rect(x, y - 22, 30, 44, "url(#gDuct)", 3, OL_THIN)
    s += blood(1330, 400, 30, 51, drops=9)
    s += blood(1260, 300, 20, 52, drops=6, drip=26)
    s += blood(1000, 470, 14, 53, drops=4)
    s += sparkle(1420, 410, 24)
    return s


# ------------------------------------------------------------------ 06
def desafinada():
    s = ""
    # mástil
    s += cylinder(240, 790, 400, 56, "url(#gWoodLight)", rx=6, filt="fGrain")
    s += rect(250, 380, 540, 40, "#3a1f10", 3, 'stroke="#0b0b0c" stroke-width="2"')
    x, gap = 262, 46
    n = 0
    while x < 780:
        s += line(x, 380, x, 420, "#d9dde0", 3)
        n += 1
        if n in (3, 5, 7, 9):
            s += circle(x - gap / 2, 400, 5, "#efe8d8", 'stroke="none"')
        if n == 12:
            s += circle(x - gap / 2, 390, 4.5, "#efe8d8", 'stroke="none"') + circle(x - gap / 2, 410, 4.5, "#efe8d8", 'stroke="none"')
        x += gap
        gap *= .955
    # pala del mástil con clavijas
    head = path("M90,372 C120,338 200,346 252,372 L252,428 C200,440 140,444 96,430 Q78,404 90,372 Z", "url(#gWoodLight)")
    s = group(head, filt="fGrain") + s
    for k in range(6):
        tx = 110 + k * 24
        s = rect(tx - 7, 336 - (k % 2) * 4, 14, 22, "url(#gSteelBlock)", 4, OL_THIN) + s
    # cuerpo
    body = ("M760,330 C720,280 690,230 720,205 C760,180 830,230 880,240 C960,200 1090,190 1170,250 "
            "C1240,300 1250,500 1170,560 C1090,615 960,600 880,560 C830,580 770,615 735,595 C705,570 730,520 760,470 Z")
    # hacha atornillada al borde
    axe = path("M1150,300 L1270,282 Q1370,320 1392,410 Q1370,500 1270,528 L1150,510 Z", "url(#gBladeV)")
    axe += path("M1270,282 Q1370,320 1392,410 Q1370,500 1270,528", "none", 'stroke="#fff" stroke-width="4" stroke-opacity=".75"')
    axe += path("M1300,300 Q1350,350 1362,410 Q1350,470 1300,510", "none", 'stroke="#000" stroke-width="2" stroke-opacity=".25"')
    s += group(axe, filt="fRust")
    s += group(path(body, "url(#gBurst)") + ellipse(930, 300, 150, 40, "#fff", 'stroke="none" opacity=".18"', -10), filt="fWear")
    s += path("M790,300 C820,260 880,270 920,300 L1010,320 L1010,480 L920,500 C880,530 820,540 790,500 C770,460 770,340 790,300 Z",
              "#efe9dc", 'stroke="#0b0b0c" stroke-width="2.5" opacity=".95"')
    for px_ in (880, 960):
        s += rect(px_, 352, 34, 96, "#111214", 6, OL_THIN)
        for k in range(6):
            s += circle(px_ + 17, 362 + k * 15, 3.4, "#c9d0d6", 'stroke="none"')
    s += rect(1062, 360, 44, 80, "url(#gSteelBlock)", 5, OL_THIN)
    for k, (kx, ky) in enumerate(((1050, 500), (1100, 520), (1140, 490))):
        s += circle(kx, ky, 14, "#e8e2d0", OL_THIN) + circle(kx - 4, ky - 4, 4, "#fff", 'stroke="none" opacity=".7"')
    for k in range(6):
        y = 383 + k * 7
        s += line(252, y, 1086, y + (k - 2.5) * 1.5, "#e6eaee", 1.4, .85)
    s += path("M300,383 C320,330 360,320 380,350 C395,372 360,385 340,360", "none", 'stroke="#e6eaee" stroke-width="1.6"')
    s += path("M1000,560 L1030,520 L1020,500 L1060,470", "none", 'stroke="#140402" stroke-width="3"')
    for by in (340, 400, 460):
        s += bolt(1180, by, 9)
    s += blood(1360, 420, 30, 61, drops=9, drip=30)
    s += blood(1060, 300, 22, 62, drops=7)
    s += sparkle(1395, 400, 24)
    return s


# ------------------------------------------------------------------ 07
def pala_tiburon():
    s = ""
    dpath = rr_path(54, 342, 150, 116, 42) + " " + rr_path(82, 366, 92, 68, 24)
    s += group(f'<path d="{dpath}" fill="url(#gWood)" fill-rule="evenodd" {OL}/>', filt="fGrain")
    s += cylinder(190, 940, 400, 38, "url(#gWood)", filt="fGrain")
    s += path("M900,376 L1012,364 L1012,436 L900,424 Z", "url(#gSteelDark)")
    for x in (930, 975):
        s += bolt(x, 400, 7)
    # dientes amolados en los bordes
    teeth = []
    for x in range(1010, 1260, 26):
        teeth += [(x, 252), (x + 13, 228), (x + 26, 252)]
    teeth_b = []
    for x in range(1010, 1260, 26):
        teeth_b += [(x, 548), (x + 13, 572), (x + 26, 548)]
    s += poly([(1010, 260)] + teeth + [(1260, 260)], "url(#gBladeV)")
    s += poly([(1010, 540)] + teeth_b + [(1260, 540)], "url(#gBladeV)")
    spade = "M1000,250 L1180,250 C1260,250 1330,330 1352,400 C1330,470 1260,550 1180,550 L1000,550 Q984,400 1000,250 Z"
    paint = "M1012,268 L1176,268 C1246,268 1308,336 1326,400 C1308,464 1246,532 1176,532 L1012,532 Q1000,400 1012,268 Z"
    body = path(spade, "url(#gBladeV)") + path(paint, "url(#gPaint)", 'stroke="none"')
    # boca de tiburón pintada
    body += path("M1150,430 Q1250,425 1322,402 Q1270,505 1160,470 Z", "#5a0b10", 'stroke="#0b0b0c" stroke-width="2"')
    for k in range(7):
        tx = 1160 + k * 22
        ty = 430 - k * 3.5
        body += poly([(tx, ty), (tx + 10, ty + 20), (tx + 20, ty - 2)], "#f4efe6", 'stroke="#0b0b0c" stroke-width="1.2"')
    for k in range(6):
        tx = 1172 + k * 22
        ty = 470 - k * 9 + (k * k) * .6
        body += poly([(tx, ty), (tx + 10, ty - 18), (tx + 20, ty - 1)], "#f4efe6", 'stroke="#0b0b0c" stroke-width="1.2"')
    body += circle(1220, 340, 20, "#f4efe6", OL_THIN) + circle(1226, 342, 10, "#0b0b0c", 'stroke="none"')
    body += circle(1222, 337, 3.5, "#fff", 'stroke="none"')
    body += path("M1110,320 q-10,30 0,60 M1090,326 q-10,28 0,52 M1070,332 q-9,26 0,46", "none", 'stroke="#0d1620" stroke-width="4"')
    s += group(body, filt="fRust")
    s += path("M1352,400 C1330,470 1260,550 1180,550", "none", 'stroke="#fff" stroke-width="3" stroke-opacity=".6"')
    s += blood(1320, 410, 26, 71, drops=8, drip=30)
    s += blood(1130, 268, 16, 72, drops=5)
    s += sparkle(1350, 395, 24)
    return s


# ------------------------------------------------------------------ 08
def sarten():
    s = ""
    s += cylinder(230, 830, 400, 46, "url(#gSteelDark)", rx=20, filt="fWear")
    s += ellipse(278, 400, 26, 13, "#050506", OL_THIN)
    s += wrap(360, 640, 400, 46, "url(#gWood)", band=30, slant=10)
    s += path("M800,372 C840,370 860,340 880,330 L880,470 C860,460 840,430 800,428 Z", "url(#gSteelDark)")
    cx, cy, R = 1040, 400, 205
    spikes = ""
    for k in range(14):
        a = 2 * math.pi * k / 14 + .12
        if abs(math.cos(a) + 1) < .12:
            continue  # sin púa donde entra el mango
        g = rect(0, -9, 46, 18, "url(#gSteel)", 2, OL_THIN) + poly([(44, -11), (86, 0), (44, 11)], "url(#gSteel)", OL_THIN)
        g += line(48, -5, 80, -1, "#fff", 1.5, .6)
        spikes += group(g, f"translate({f(cx + (R - 12) * math.cos(a))} {f(cy + (R - 12) * math.sin(a))}) rotate({f(math.degrees(a))})")
    s += spikes
    pan = circle(cx, cy, R, "url(#gIron)")
    pan += circle(cx, cy, R - 16, "none", 'stroke="#000" stroke-width="5" stroke-opacity=".45"')
    for r in (150, 110, 70):
        pan += circle(cx, cy, r, "none", 'stroke="#fff" stroke-width="1.2" stroke-opacity=".12"')
    pan += ('<path id="arcTxt" d="M{a},{b} A135,135 0 0 1 {c},{b}" fill="none"/>'
            .format(a=f(cx - 135), b=f(cy), c=f(cx + 135)))
    pan += ('<text font-family="Inter Display" font-weight="900" font-size="30" letter-spacing="6" fill="#000" fill-opacity=".45">'
            '<textPath href="#arcTxt" startOffset="50%" text-anchor="middle">No. 10 · CAST IRON</textPath></text>')
    pan += ellipse(cx - 70, cy - 90, 90, 30, "#fff", 'stroke="none" opacity=".12"', -30)
    s += group(pan, filt="fWear")
    for k in range(6):
        a = 2 * math.pi * k / 6
        s += bolt(cx + 120 * math.cos(a), cy + 120 * math.sin(a), 9)
    s += circle(cx, cy, 36, "url(#gSteelBlock)") + bolt(cx, cy, 15)
    s += blood(cx + 120, cy - 60, 34, 81, drops=10)
    s += blood(cx - 40, cy + 150, 20, 82, drops=6, drip=26)
    s += sparkle(cx + 270, cy - 10, 22)
    return s


# ------------------------------------------------------------------ 09
def pare():
    s = ""
    # bloque de concreto de la base
    conc = path("M30,330 L90,305 L160,322 L178,370 L170,452 L120,492 L50,486 L20,430 Z", "url(#gConcrete)")
    for k, (x, y, r) in enumerate(((60, 350, 6), (110, 340, 4), (140, 420, 7), (70, 450, 5), (120, 470, 3), (45, 400, 4), (150, 360, 3))):
        conc += circle(x, y, r, "#5d5952", 'stroke="#2a2824" stroke-width="1"')
    for x1, y1, x2, y2 in ((60, 320, 30, 250), (130, 470, 110, 560), (40, 470, -10, 520)):
        s += line(x1, y1, x2, y2, "#0b0b0c", 13) + line(x1, y1, x2, y2, "#7a4a2a", 8) + line(x1, y1, x2, y2, "#c48858", 2.5, .7)
    s += group(conc, filt="fWear")
    s += cylinder(150, 1200, 400, 36, "url(#gSteel)", filt="fRust")
    for x in range(260, 1100, 220):
        s += circle(x, 400, 5, "#121416", 'stroke="none"')
    s += wrap(200, 440, 400, 40, "url(#gRubber)", band=18, slant=10, line_color="#666")
    cx, cy, R = 1090, 400, 230
    pts_ = [(cx + R * math.cos(math.radians(22.5 + 45 * k)), cy + R * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]
    inner = [(cx + (R - 22) * math.cos(math.radians(22.5 + 45 * k)), cy + (R - 22) * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]
    sign = poly(pts_, "#ece8de")
    sign += poly(inner, "url(#gRed)", 'stroke="none"')
    sign += ('<text x="{x}" y="{y}" text-anchor="middle" font-family="Inter Display" font-weight="900" font-size="104" '
             'fill="#f4f0e6" letter-spacing="2">STOP</text>').format(x=f(cx), y=f(cy + 37))
    sign += path(f"M{f(cx - 200)},{f(cy - 120)} L{f(cx + 60)},{f(cy + 210)}", "none", 'stroke="#000" stroke-width="10" stroke-opacity=".22"')
    sign += path(f"M{f(cx - 196)},{f(cy - 126)} L{f(cx + 64)},{f(cy + 204)}", "none", 'stroke="#fff" stroke-width="3" stroke-opacity=".25"')
    for dx, dy in ((-120, -150), (140, 120), (60, -160)):
        sign += circle(cx + dx, cy + dy, 9, "#0d0d0d", 'stroke="#d6d0c4" stroke-width="3"')
    s += group(sign, filt="fRust")
    s += poly(pts_, "none", 'stroke="#f7fafc" stroke-width="5" stroke-opacity=".8" stroke-linejoin="round"')
    s += poly(pts_, "none", OL)
    for bx in (910, 1272):
        s += rect(bx - 14, 360, 28, 80, "url(#gSteelBlock)", 6, OL_THIN)
        s += bolt(bx, 365, 8) + bolt(bx, 435, 8)
    s += blood(cx + 160, cy - 60, 34, 91, drops=9, drip=34)
    s += blood(cx - 170, cy + 80, 22, 92, drops=6)
    s += sparkle(cx + R + 8, cy - 70, 24)
    return s


# ------------------------------------------------------------------ 10
def katana():
    s = ""
    # hoja (ballesta forjada)
    blade = "M490,372 Q900,366 1352,322 Q1300,388 1240,398 Q900,432 490,430 Z"
    b = path(blade, "url(#gForged)")
    ham = "M500,412"
    for k in range(30):
        x = 520 + k * 25
        y = 410 - (x - 500) * .035 + (6 if k % 2 else -4)
        ham += f" Q{f(x - 12)},{f(y - 8)} {f(x)},{f(y)}"
    b += path(ham, "none", 'stroke="#fff" stroke-width="3" stroke-opacity=".55"')
    b += path("M1352,322 Q1300,388 1240,398 Q900,432 490,430", "none", 'stroke="#fff" stroke-width="3" stroke-opacity=".9"')
    b += circle(640, 388, 9, "#0a0a0b", 'stroke="#6c737a" stroke-width="2"')
    b += ('<text x="700" y="392" font-family="Inter" font-weight="800" font-size="14" letter-spacing="3" '
          'fill="#000" fill-opacity=".55">GM 15590 · 1987</text>')
    s += group(b, filt="fWear")
    # habaki y tsuba (piñón de moto visto de canto)
    s += path("M448,364 L498,368 L498,434 L448,438 Z", "url(#gBrassLin)")
    tsuba = rect(422, 300, 28, 200, "url(#gSteelBlock)", 4)
    for y in range(300, 500, 16):
        tsuba += rect(418, y + 3, 36, 9, "url(#gSteelBlock)", 2, OL_THIN)
    s += group(tsuba, filt="fRust")
    # tsuka con cinturón de seguridad en rombos
    cid = "tsukaClip"
    s += f'<clipPath id="{cid}"><rect x="150" y="372" width="276" height="56" rx="10"/></clipPath>'
    weave = rect(150, 372, 276, 56, "#121314", 10, 'stroke="none"')
    for x in range(120, 440, 46):
        weave += poly([(x, 372), (x + 26, 372), (x + 54, 428), (x + 28, 428)], "url(#gWeb)", 'stroke="#000" stroke-width="2"')
    for x in range(120, 440, 46):
        weave += poly([(x + 54, 372), (x + 28, 372), (x, 428), (x + 26, 428)], "url(#gWeb)", 'stroke="#000" stroke-width="2"')
        weave += line(x + 40, 380, x + 14, 420, "#c9ced3", 1, .35)
    weave += rect(150, 372, 276, 56, "url(#gShade)", 10, 'stroke="none"')
    s += group(weave, extra=f'clip-path="url(#{cid})"') + rect(150, 372, 276, 56, "none", 10)
    # pomo: ojo enrollado de la ballesta
    eye = f'<path d="M150,400 m-46,0 a46,46 0 1,0 92,0 a46,46 0 1,0 -92,0 M150,400 m-24,0 a24,24 0 1,1 48,0 a24,24 0 1,1 -48,0" fill="url(#gForged)" fill-rule="evenodd" {OL}/>'
    s += group(eye, filt="fRust") + circle(150, 400, 22, "#1a1a1c", 'stroke="#000" stroke-width="2"') + circle(150, 400, 10, "url(#gBolt)", OL_THIN)
    s += blood(1290, 370, 18, 101, drops=6, drip=22)
    s += sparkle(1350, 322, 26)
    return s


# ------------------------------------------------------------------ 11
def lanza_tijera():
    s = ""
    # trapo rojo atado (detrás)
    rag = path("M940,415 C930,480 960,540 940,610 C980,560 990,500 1000,430 Z", "url(#gRed)")
    rag += path("M965,420 C975,500 1010,540 1020,600 C1040,540 1030,480 1010,425 Z", "url(#gRed)")
    s += group(rag, filt="fWear")
    s += cylinder(80, 1010, 400, 32, "url(#gGreen)", filt="fWear")
    s += rect(56, 382, 34, 36, "url(#gRubber)", 10)
    # gancho trasero
    hook = path("M980,410 C960,470 920,520 860,540 C900,500 920,460 940,410 Z", "url(#gBladeV)")
    s += group(hook, filt="fRust")
    # hoja ondulada de tijera de podar
    blade_d = "M940,372 L1180,360 Q1300,356 1372,392 L1290,402"
    xs = list(range(1290, 1000, -26))
    for x in xs:
        blade_d += f" Q{f(x - 13)},{f(434 - (x - 1000) * .06)} {f(x - 26)},{f(422 - (x - 1000) * .07)}"
    blade_d += " L940,428 Z"
    bl = path(blade_d, "url(#gBlade)")
    bl += path("M1372,392 L1290,402", "none", 'stroke="#fff" stroke-width="3" stroke-opacity=".8"')
    bl += line(960, 380, 1300, 372, "#fff", 2, .45)
    bl += circle(990, 400, 14, "url(#gSteelBlock)", OL_THIN) + bolt(990, 400, 7)
    s += group(bl, filt="fRust")
    # ataduras de alambre y abrazaderas
    s += wrap(900, 960, 400, 40, "url(#gSteel)", band=8, slant=4, line_color="#222")
    s += band(1020, 400, 52, 22)
    s += blood(1330, 395, 22, 111, drops=8, drip=26)
    s += blood(1150, 380, 14, 112, drops=5)
    s += sparkle(1380, 392, 24)
    return s


# ------------------------------------------------------------------ 12
def guadana_golf():
    s = ""
    s += path("M370,384 L1120,394 L1120,406 L370,416 Z", "url(#gSteel)")
    s += line(380, 391, 1110, 398, "#fff", 2, .6)
    s += cylinder(90, 390, 400, 40, "url(#gRubber)", rx=12)
    for x in range(110, 380, 12):
        s += line(x, 383, x, 417, "#55585d", 1.4, .6)
    s += rect(240, 381, 40, 38, "#e8e2d0", 0, 'stroke="none" opacity=".85"')
    s += ellipse(90, 400, 10, 19, "url(#gRubber)")
    # hoz soldada (curva hacia arriba y adelante)
    sickle = "M1150,392 C1310,384 1380,260 1300,150 Q1270,112 1218,108 C1290,170 1300,300 1150,360 Z"
    sk = path(sickle, "url(#gBladeV)")
    sk += path("M1218,108 C1290,170 1300,300 1150,360", "none", 'stroke="#fff" stroke-width="4" stroke-opacity=".85"')
    sk += path("M1236,124 C1300,190 1300,300 1180,352", "none", 'stroke="#000" stroke-width="2" stroke-opacity=".3"')
    s += group(sk, filt="fRust")
    # cabeza del hierro 7
    head = path("M1100,388 L1160,380 L1222,402 L1240,520 Q1236,548 1204,548 L1146,542 Q1130,500 1118,420 Z", "url(#gSteelBlock)")
    for k in range(6):
        head += line(1150, 440 + k * 16, 1222, 438 + k * 16, "#000", 2, .35)
    head += ('<text x="1188" y="425" text-anchor="middle" font-family="Inter Display" font-weight="900" '
             'font-size="30" fill="#000" fill-opacity=".5">7</text>')
    s += group(head, filt="fRust")
    s += weld(1150, 388, 1215, 372, 6)
    # pelota de golf ensartada
    ball = circle(1232, 140, 30, "#f2f0ea")
    for dx, dy in ((-12, -10), (2, -16), (14, -6), (-16, 6), (-2, 2), (12, 10), (-6, 16), (8, 22)):
        ball += circle(1232 + dx, 140 + dy, 3.2, "#c9c5ba", 'stroke="none"')
    ball += ellipse(1222, 128, 10, 6, "#fff", 'stroke="none" opacity=".8"', -30)
    s += ball
    s += blood(1240, 150, 16, 121, drops=5)
    s += blood(1260, 300, 26, 122, drops=8, drip=30)
    s += sparkle(1300, 155, 24)
    return s


WEAPONS = [
    {"id": "AC_Hachamazo", "name": "Hachamazo",
     "tagline": "Media herramienta de bombero, media maza de demolición.",
     "combo": ["Mazo", "Hacha de bombero"],
     "intro": "Alguien en el cuartel de bomberos de Riverside decidió que una sola herramienta no alcanzaba. "
              "Soldó la cabeza de un mazo encima de un hacha de bombero y le puso abrazaderas al mango. "
              "Es pesada, lenta y no perdona: de un lado aplasta, del otro parte en dos.",
     "stats": {"Daño": 9, "Velocidad": 3, "Alcance": 6, "Aguante": 8, "Derribo": 9},
     "special": "Doble cabeza: tala árboles y rompe puertas como un hacha, y tumba zombis como un mazo.",
     "art": hachamazo},
    {"id": "AC_BateErizo", "name": "Bate Erizo",
     "tagline": "Clavos, alambre de púas y un disco de sierra. Sin piedad.",
     "combo": ["Bate de béisbol", "Clavos", "Disco de sierra"],
     "intro": "El bate de la liga infantil de Muldraugh, mejorado con todo lo que había en el garaje. "
              "Clavos por todos lados, alambre de púas enrollado y un disco de sierra clavado en la punta. "
              "Cada golpe desgarra, y lo que queda enganchado sale con él.",
     "stats": {"Daño": 7, "Velocidad": 7, "Alcance": 6, "Aguante": 6, "Derribo": 6},
     "special": "Desgarro: alta chance de crítico y golpea hasta 3 zombis por swing.",
     "art": bate_erizo},
    {"id": "AC_GarrasCarnicero", "name": "Garras de Carnicero",
     "tagline": "Tres cuchillos de cocina en cada puño. Pelea como un animal.",
     "combo": ["Guante de boxeo", "Cuchillos de cocina", "Cinta americana"],
     "intro": "Un boxeador amateur de West Point se quedó sin munición, pero no sin ideas. "
              "Pegó con cinta americana tres cuchillos de cocina sobre los nudillos de su guante. "
              "A corta distancia es una licuadora: golpes rápidos que no dejan respirar.",
     "stats": {"Daño": 5, "Velocidad": 10, "Alcance": 2, "Aguante": 5, "Derribo": 2},
     "special": "Ráfaga: el ataque más rápido del arsenal. Apuñala en cadena casi sin cansarte.",
     "art": garras},
    {"id": "AC_RemoDestripador", "name": "Remo Destripador",
     "tagline": "Dos discos de sierra y el alcance de un remo de kayak.",
     "combo": ["Remo de kayak", "Disco de sierra ×2"],
     "intro": "Del alquiler de kayaks del río Ohio a la primera línea. Un disco de sierra atornillado en cada pala "
              "convierte el remo en un molino. Se maneja con las dos manos y barre todo lo que tiene adelante.",
     "stats": {"Daño": 6, "Velocidad": 5, "Alcance": 9, "Aguante": 5, "Derribo": 5},
     "special": "Barrido: alcance enorme y golpea hasta 4 zombis por swing.",
     "art": remo},
    {"id": "AC_TridenteCarnicero", "name": "Tridente Carnicero",
     "tagline": "Una horquilla de granja con cuchillos de carnicero en cada diente.",
     "combo": ["Horquilla", "Cuchillos de carnicero", "Cinta americana"],
     "intro": "En las granjas de las afueras de Rosewood sobraban horquillas y faltaban armas. "
              "Tres cuchillos de carnicero atados a los dientes la convierten en un tridente "
              "que mantiene a los muertos a distancia.",
     "stats": {"Daño": 6, "Velocidad": 5, "Alcance": 9, "Aguante": 6, "Derribo": 4},
     "special": "Ensarte: alcance de lanza y remate rápido a zombis en el suelo.",
     "art": tridente},
    {"id": "AC_LaDesafinada", "name": "La Desafinada",
     "tagline": "Rock pesado de verdad: una guitarra eléctrica con un hacha en el cuerpo.",
     "combo": ["Guitarra eléctrica", "Hacha de bombero"],
     "intro": "La banda del bar de Louisville no llegó al último show, pero su guitarra sí. "
              "Con la hoja de un hacha atornillada al cuerpo y las cuerdas reventadas, todavía suena: "
              "cada golpe retumba por toda la calle.",
     "stats": {"Daño": 7, "Velocidad": 5, "Alcance": 6, "Aguante": 5, "Derribo": 6},
     "special": "Acorde final: cada golpe hace ruido y atrae zombis cercanos. Alto daño, alto riesgo.",
     "art": desafinada},
    {"id": "AC_PalaTiburon", "name": "Pala Tiburón",
     "tagline": "Bordes serruchados y una boca de tiburón pintada a mano.",
     "combo": ["Pala", "Amoladora", "Pintura"],
     "intro": "Un veterano de March Ridge afiló los bordes de su pala en dientes de sierra y le pintó "
              "una boca de tiburón, como los aviones de su abuelo. Corta, empuja y todavía sirve para cavar.",
     "stats": {"Daño": 6, "Velocidad": 5, "Alcance": 7, "Aguante": 8, "Derribo": 5},
     "special": "Herramienta: sigue funcionando como pala para cavar y enterrar.",
     "art": pala_tiburon},
    {"id": "AC_SartenInfierno", "name": "Sartén del Infierno",
     "tagline": "Hierro fundido, púas alrededor y ni una sola tortilla.",
     "combo": ["Sartén de hierro", "Tornillos", "Amoladora"],
     "intro": "La sartén favorita de la abuela, ahora con una corona de tornillos afilados alrededor del borde. "
              "Es corta y pesada, pero cada golpe suena como una campana y deja a los zombis viendo estrellas.",
     "stats": {"Daño": 6, "Velocidad": 6, "Alcance": 3, "Aguante": 9, "Derribo": 8},
     "special": "Campanazo: alta chance de derribar y casi irrompible.",
     "art": sarten},
    {"id": "AC_PareDefinitivo", "name": "PARE Definitivo",
     "tagline": "La señal de tránsito arrancada con su base de concreto incluida.",
     "combo": ["Señal de PARE", "Caño", "Bloque de concreto"],
     "intro": "Alguien arrancó la señal de una esquina de Muldraugh con poste y todo, incluido el bloque de concreto. "
              "Los bordes del octágono están amolados y el concreto hace de contrapeso. "
              "Lenta, brutal y completamente ilegal.",
     "stats": {"Daño": 9, "Velocidad": 2, "Alcance": 8, "Aguante": 9, "Derribo": 10},
     "special": "Ley de tránsito: derribo casi garantizado y golpea hasta 3 zombis, pero cansa muchísimo.",
     "art": pare},
    {"id": "AC_KatanaBallesta", "name": "Katana de Ballesta",
     "tagline": "Forjada con el elástico de una camioneta. Honor de taller mecánico.",
     "combo": ["Ballesta de camioneta", "Cinturón de seguridad", "Piñón de moto"],
     "intro": "El mecánico de Rosewood veía demasiadas películas de samuráis. Forjó la hoja con una ballesta "
              "de camioneta, envolvió el mango con cinturón de seguridad y usó un piñón de moto como guarda. "
              "Ligera, filosa y sorprendentemente resistente.",
     "stats": {"Daño": 8, "Velocidad": 7, "Alcance": 7, "Aguante": 8, "Derribo": 3},
     "special": "Filo de resorte: el crítico más alto entre las hojas largas y gran durabilidad.",
     "art": katana},
    {"id": "AC_LanzaTijera", "name": "Lanza Tijera",
     "tagline": "Media tijera de podar atada a un palo largo. Jardinería defensiva.",
     "combo": ["Mango de jardín", "Tijera de podar", "Alambre"],
     "intro": "Desarmada, cada mitad de una tijera de podar es una hoja larga y ondulada. "
              "Atada con alambre y abrazaderas a un mango de jardín, mantiene a los zombis a dos metros. "
              "El trapo rojo es para encontrarla rápido en la oscuridad.",
     "stats": {"Daño": 5, "Velocidad": 6, "Alcance": 10, "Aguante": 5, "Derribo": 3},
     "special": "Distancia segura: el mayor alcance del arsenal. Ataca antes que nadie.",
     "art": lanza_tijera},
    {"id": "AC_GuadanaGolf", "name": "Guadaña de Golf",
     "tagline": "Un hierro 7, una hoz soldada y una pelota que nunca salió del green.",
     "combo": ["Palo de golf", "Hoz"],
     "intro": "El club de campo de Louisville cerró sus puertas, pero alguien siguió jugando. "
              "Una hoz soldada a la cabeza de un hierro 7 forma un gancho que engancha y corta en el mismo swing. "
              "La pelota en la punta quedó ahí como trofeo.",
     "stats": {"Daño": 7, "Velocidad": 7, "Alcance": 7, "Aguante": 6, "Derribo": 4},
     "special": "Swing completo: corte en arco amplio que golpea a varios zombis a la vez.",
     "art": guadana_golf},
]
