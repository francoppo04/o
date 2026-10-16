"""Lector de animaciones DirectX .X de texto (formato de anims_X de Project Zomboid), sin Blender.

parse(path) -> dict con:
  parents   {hueso: padre}
  rest      {hueso: Matrix 4x4 local (convención columna, traslación en la última columna)}
  ticks     ticks por segundo
  keys      {hueso: {"R": [(t, (w,x,y,z))], "S": [...], "T": [...]}}
  name      nombre del AnimationSet
local(anim, bone, t) -> Matrix local interpolada en el tick t.
"""
import re

from mathutils import Matrix, Quaternion, Vector

_TOK = re.compile(r'[{}]|"[^"]*"|[^\s{};,]+|;|,')


def _matrix(vals):
    # .X guarda la matriz por filas con vectores fila: la traspuesta es la convención columna
    return Matrix([vals[0:4], vals[4:8], vals[8:12], vals[12:16]]).transposed()


def parse(path):
    text = open(path, encoding="latin-1").read()
    parents, rest, keys = {}, {}, {}
    ticks, name = 4800, None
    # jerarquía de Frames
    stack = []
    pos = 0
    frame_re = re.compile(r"\bFrame\s+(\S+)\s*\{|FrameTransformMatrix\s*\{([^}]*)\}|\}|AnimTicksPerSecond\s*\{\s*(\d+)|AnimationSet\s+(\S+)\s*\{|template\s+\w+\s*\{[^}]*\}|Material\s+\S+\s*\{(?:[^{}]|\{[^}]*\})*\}")
    for m in frame_re.finditer(text):
        if m.group(0).startswith("template") or m.group(0).startswith("Material"):
            continue
        if m.group(4):
            name = m.group(4)
            anim_start = m.end()
            break
        if m.group(3):
            ticks = int(m.group(3))
        elif m.group(1):
            b = m.group(1)
            parents[b] = stack[-1] if stack else None
            stack.append(b)
        elif m.group(2) is not None:
            vals = [float(v) for v in re.findall(r"-?[\d.]+(?:e-?\d+)?", m.group(2))]
            rest[stack[-1]] = _matrix(vals)
        elif m.group(0) == "}" and stack:
            stack.pop()
    # animaciones
    body = text[anim_start:]
    for am in re.finditer(r"Animation\s*\{\s*\{\s*(\S+)\s*\}(.*?)\n \}", body, re.S):
        bone = am.group(1)
        k = keys.setdefault(bone, {})
        for km in re.finditer(r"AnimationKey\s*(\w*)\s*\{\s*(\d+)\s*;\s*(\d+)\s*;(.*?)\}", am.group(2), re.S):
            ktype = {"0": "R", "1": "S", "2": "T", "4": "M"}[km.group(2)]
            entries = []
            for e in re.finditer(r"(\d+)\s*;\s*(\d+)\s*;\s*([-\d.e,\s]+?);;", km.group(4)):
                vals = tuple(float(v) for v in e.group(3).replace(",", " ").split())
                entries.append((int(e.group(1)), vals))
            k[ktype] = entries
    return {"parents": parents, "rest": rest, "ticks": ticks, "keys": keys, "name": name}


def _sample(entries, t):
    if t <= entries[0][0]:
        return entries[0][1], entries[0][1], 0.0
    for (t0, v0), (t1, v1) in zip(entries, entries[1:]):
        if t0 <= t <= t1:
            return v0, v1, (t - t0) / (t1 - t0) if t1 > t0 else 0.0
    return entries[-1][1], entries[-1][1], 0.0


def duration(anim):
    return max(e[-1][0] for k in anim["keys"].values() for e in k.values() if e)


def local(anim, bone, t, conj=True):
    k = anim["keys"].get(bone)
    if not k or "R" not in k:
        return anim["rest"][bone].copy()
    a, b, f = _sample(k["R"], t)
    qa, qb = Quaternion(a), Quaternion(b)
    q = qa.slerp(qb, f)
    if conj:
        q = q.conjugated()
    m = q.to_matrix().to_4x4()
    if "S" in k:
        a, b, f = _sample(k["S"], t)
        s = Vector(a).lerp(Vector(b), f)
        m = m @ Matrix.Diagonal(s.to_4d())
    if "T" in k:
        a, b, f = _sample(k["T"], t)
        m.translation = Vector(a).lerp(Vector(b), f)
    return m


def globals_at(anim, t, conj=True):
    out = {}
    for b in anim["parents"]:   # orden de aparición: padres antes que hijos
        p = anim["parents"][b]
        m = local(anim, b, t, conj)
        out[b] = out[p] @ m if p else m
    return out
