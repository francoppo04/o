"""Calca la silueta de un arma DIBUJADA (contorno oscuro sobre fondo claro con sombras suaves).
1) contorno = píxeles oscuros, cerrado con una dilatación chica; 2) exterior = relleno desde el borde de la
caja (las sombras no tienen contorno y quedan afuera); 3) interior = todo lo demás; 4) GrabCut afina los
huecos reales (guardamonte, culatas esqueleto) usando interior como "probable" y exterior como "seguro".
Uso: python tools/trace_drawing.py lamina.webp salida.json X0 Y0 X1 Y1 [--dark 95] [--mask]"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("img")
    ap.add_argument("out")
    ap.add_argument("rect", nargs=4, type=int)
    ap.add_argument("--dark", type=int, default=95)
    ap.add_argument("--close", type=int, default=2)
    ap.add_argument("--mask", action="store_true")
    a = ap.parse_args()
    im = cv2.imread(a.img)
    x0, y0, x1, y1 = a.rect
    crop = im[y0:y1, x0:x1].copy()
    g = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    edge = ((g < a.dark) | (hsv[..., 1] > 70)).astype(np.uint8) * 255
    edge = cv2.dilate(edge, np.ones((a.close * 2 + 1, a.close * 2 + 1), np.uint8))
    h, w = edge.shape
    ff = edge.copy()
    m = np.zeros((h + 2, w + 2), np.uint8)
    for (sx, sy) in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)] + [(x, 0) for x in range(0, w, 15)] + \
            [(x, h - 1) for x in range(0, w, 15)] + [(0, y) for y in range(0, h, 15)] + [(w - 1, y) for y in range(0, h, 15)]:
        if ff[sy, sx] == 0:
            cv2.floodFill(ff, m, (sx, sy), 128)
    exterior = (ff == 128)
    interior = ~exterior
    interior = cv2.erode(interior.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=max(0, a.close - 1)) > 0
    gc = np.where(exterior, cv2.GC_BGD, cv2.GC_PR_FGD).astype(np.uint8)
    core = cv2.erode(interior.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    gc[core & (g < a.dark)] = cv2.GC_FGD
    bg, fg = np.zeros((1, 65)), np.zeros((1, 65))
    cv2.grabCut(crop, gc, None, bg, fg, 5, cv2.GC_INIT_WITH_MASK)
    mask = np.where((gc == 1) | (gc == 3), 255, 0).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    full = np.zeros(im.shape[:2], np.uint8)
    full[y0:y1, x0:x1] = mask
    cs, hier = cv2.findContours(full, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    shapes = []
    for i, c in enumerate(cs):
        if hier[0][i][3] != -1 or cv2.contourArea(c) < 60:
            continue
        ext = cv2.approxPolyDP(c, 0.7, True)[:, 0].tolist()
        holes = []
        j = hier[0][i][2]
        while j != -1:
            if cv2.contourArea(cs[j]) >= 15:
                holes.append(cv2.approxPolyDP(cs[j], 0.7, True)[:, 0].tolist())
            j = hier[0][j][0]
        shapes.append([ext, holes])
    Path(a.out).write_text(json.dumps({"photo": Path(a.img).name, "rect": a.rect, "method": "dibujo",
                                       "shapes": shapes}))
    if a.mask:
        cv2.imwrite(str(Path(a.out).with_suffix(".mask.png")), mask)
    print(f"{a.out}: {len(shapes)} contornos")


if __name__ == "__main__":
    main()
