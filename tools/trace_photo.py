"""Calca la silueta de un arma desde una foto de costado (GrabCut) y la guarda como contornos en píxeles.

Las fotos de referencia NO van al repo; solo el contorno (JSON) que usan los scripts de tools/blender/guns.
Uso (requiere opencv-python-headless y numpy):
  python tools/trace_photo.py foto.webp tools/blender/guns/siluetas/AT_M4.json X0 Y0 X1 Y1 [--rotate GRADOS]
  --rotate: gira la foto (antihorario, en grados) antes de calcar, para dejar el cañón horizontal.
Las coordenadas (rectángulo y contornos) son de la foto ya girada.
"""
import argparse
import json
import math
from pathlib import Path

import cv2
import numpy as np


def rotate(im, deg):
    h, w = im.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), deg, 1.0)
    c, s = abs(M[0, 0]), abs(M[0, 1])
    W, H = int(h * s + w * c), int(h * c + w * s)
    M[0, 2] += W / 2 - w / 2
    M[1, 2] += H / 2 - h / 2
    return cv2.warpAffine(im, M, (W, H), borderValue=(40, 40, 40))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("out")
    ap.add_argument("rect", nargs=4, type=int)
    ap.add_argument("--rotate", type=float, default=0.0)
    ap.add_argument("--iters", type=int, default=8)
    ap.add_argument("--mask", action="store_true", help="guarda también la máscara (para revisar)")
    a = ap.parse_args()
    im = cv2.imread(a.photo)
    if a.rotate:
        im = rotate(im, a.rotate)
    x0, y0, x1, y1 = a.rect
    m = np.zeros(im.shape[:2], np.uint8)
    bg, fg = np.zeros((1, 65)), np.zeros((1, 65))
    cv2.grabCut(im, m, (x0, y0, x1 - x0, y1 - y0), bg, fg, a.iters, cv2.GC_INIT_WITH_RECT)
    mask = np.where((m == 1) | (m == 3), 255, 0).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    cs, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    shapes = []
    for i, c in enumerate(cs):
        if hier[0][i][3] != -1 or cv2.contourArea(c) < 40:
            continue
        ext = cv2.approxPolyDP(c, 0.7, True)[:, 0].tolist()
        holes = []
        j = hier[0][i][2]
        while j != -1:
            if cv2.contourArea(cs[j]) >= 12:
                holes.append(cv2.approxPolyDP(cs[j], 0.7, True)[:, 0].tolist())
            j = hier[0][j][0]
        shapes.append([ext, holes])
    Path(a.out).write_text(json.dumps({"photo": Path(a.photo).name, "rotate": a.rotate, "rect": a.rect,
                                       "shapes": shapes}))
    if a.mask:
        cv2.imwrite(str(Path(a.out).with_suffix(".mask.png")), mask[y0:y1, x0:x1])
    print(f"{a.out}: {len(shapes)} contornos, {sum(len(s[0]) for s in shapes)} puntos")


if __name__ == "__main__":
    main()
