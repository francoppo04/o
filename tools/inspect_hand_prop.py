"""Mide, en las animaciones vanilla del juego instalado, cómo queda Bip01_Prop1 (donde el juego cuelga
el arma) respecto de la mano derecha, y Bip01_Prop2 respecto de la izquierda.

Sirve para orientar modelos que se llevan "puestos" (guantes): si la relación mano-prop cambia entre
animaciones, un modelo rígido no puede calzar en todas.

Uso (Python 3, sin dependencias; no copia archivos del juego, solo imprime números):
  python tools/inspect_hand_prop.py "D:/SteamLibrary/steamapps/common/ProjectZomboid/media/anims_X/Bob" > hand_prop.txt
"""
import math
import re
import sys
from pathlib import Path

PATTERN = re.compile(r"knife|1hand|punch|stab|idle|walk|run|sprint|aim", re.I)


def q_mul(a, b):
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b
    return (w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2, w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2, w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2)


def q_mat(q):
    w, x, y, z = q
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]


def m_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def m_inv(m):   # rígida
    r = [[m[j][i] for j in range(3)] for i in range(3)]
    t = [-sum(r[i][k] * m[k][3] for k in range(3)) for i in range(3)]
    return [r[0] + [t[0]], r[1] + [t[1]], r[2] + [t[2]], [0, 0, 0, 1]]


def apply(m, v):
    return [sum(m[i][k] * v[k] for k in range(3)) + m[i][3] for i in range(3)]


def norm(v):
    n = math.sqrt(sum(x * x for x in v)) or 1
    return [x / n for x in v]


def parse(path):
    text = open(path, encoding="latin-1").read()
    parents, rest, stack = {}, {}, []
    rx = re.compile(r"\bFrame\s+(\S+)\s*\{|FrameTransformMatrix\s*\{([^}]*)\}|\}|AnimationSet\s+(\S+)\s*\{|"
                    r"template\s+\w+\s*\{[^}]*\}|Material\s+\S+\s*\{(?:[^{}]|\{[^}]*\})*\}")
    start = None
    for m in rx.finditer(text):
        g = m.group(0)
        if g.startswith("template") or g.startswith("Material"):
            continue
        if m.group(3):
            start = m.end()
            break
        if m.group(1):
            parents[m.group(1)] = stack[-1] if stack else None
            stack.append(m.group(1))
        elif m.group(2) is not None:
            v = [float(x) for x in re.findall(r"-?[\d.]+(?:e-?\d+)?", m.group(2))]
            rest[stack[-1]] = [[v[0], v[4], v[8], v[12]], [v[1], v[5], v[9], v[13]],
                               [v[2], v[6], v[10], v[14]], [0, 0, 0, 1]]
        elif g == "}" and stack:
            stack.pop()
    keys = {}
    if start:
        for am in re.finditer(r"Animation\s*\{\s*\{\s*(\S+)\s*\}(.*?)\n \}", text[start:], re.S):
            k = keys.setdefault(am.group(1), {})
            for km in re.finditer(r"AnimationKey\s*\w*\s*\{\s*(\d+)\s*;\s*\d+\s*;(.*?)\}", am.group(2), re.S):
                t = {"0": "R", "1": "S", "2": "T"}.get(km.group(1))
                if t:
                    k[t] = [(int(e.group(1)), [float(x) for x in e.group(2).replace(",", " ").split()])
                            for e in re.finditer(r"(\d+)\s*;\s*\d+\s*;\s*([-\d.e,\s]+?);;", km.group(2))]
    return parents, rest, keys


def pose(parents, rest, keys, idx):
    G = {}
    for b in parents:
        k = keys.get(b, {})
        if "R" in k:
            e = k["R"][min(idx, len(k["R"]) - 1)][1]
            q = (e[0], -e[1], -e[2], -e[3])           # las .X guardan el conjugado
            r = q_mat(q)
            t = k["T"][min(idx, len(k["T"]) - 1)][1] if "T" in k else [rest[b][i][3] for i in range(3)]
            m = [r[0] + [t[0]], r[1] + [t[1]], r[2] + [t[2]], [0, 0, 0, 1]]
        else:
            m = rest[b]
        p = parents[b]
        G[b] = m_mul(G[p], m) if p in G else m
    return G


def relation(G, side, prop):
    if prop not in G or f"Bip01_{side}_Hand" not in G:
        return None
    inv = m_inv(G[prop])
    w = apply(inv, [G[f"Bip01_{side}_Hand"][i][3] for i in range(3)])
    f1 = apply(inv, [G[f"Bip01_{side}_Finger1"][i][3] for i in range(3)])
    f0 = apply(inv, [G[f"Bip01_{side}_Finger0"][i][3] for i in range(3)])
    k = norm([f1[i] - w[i] for i in range(3)])
    th = [f0[i] - w[i] for i in range(3)]
    d = norm([k[1] * th[2] - k[2] * th[1], k[2] * th[0] - k[0] * th[2], k[0] * th[1] - k[1] * th[0]])
    if side == "L":
        d = [-x for x in d]
    return [round(x * 100, 1) for x in w], [round(x, 2) for x in k], [round(x, 2) for x in d]


def main(folder):
    files = sorted(p for p in Path(folder).iterdir() if p.suffix.lower() == ".x" and PATTERN.search(p.stem))
    print(f"# {len(files)} animaciones en {folder}")
    print("# clip | frame | lado | muñeca en el prop (cm) | nudillos (eje del prop) | dorso")
    for f in files:
        try:
            parents, rest, keys = parse(f)
        except Exception as e:      # noqa: BLE001
            print(f"{f.stem} | error {e}")
            continue
        n = max((len(v["R"]) for v in keys.values() if "R" in v), default=1)
        for idx in sorted({0, n // 2, n - 1}):
            G = pose(parents, rest, keys, idx)
            for side, prop in (("R", "Bip01_Prop1"), ("L", "Bip01_Prop2")):
                r = relation(G, side, prop)
                if r:
                    print(f"{f.stem} | {idx} | {side} | {r[0]} | {r[1]} | {r[2]}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
