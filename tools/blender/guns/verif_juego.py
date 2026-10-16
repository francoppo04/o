"""Verificación sobre lo exportado al mod (FBX del juego), no sobre la escena de Blender:
  * art/<ID>/verif_manos.png: costado y 3/4 con la mano derecha en el origen (empuñadura) y, en fusiles,
    la muñeca izquierda en las dos posiciones medidas en las animaciones vanilla de fusil;
  * art/verif_escala_juego.png: las armas juntas al tamaño de pantalla del juego (la M4, 0,50 m de juego,
    ocupa ~36 px con el personaje de ~125 px de una captura del usuario).
Uso: python3 tools/blender/guns/verif_juego.py [ID ...]   (sin IDs: todas las que tienen attachments.json)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import gunkit as gk  # noqa: E402
import hardsurf as hs  # noqa: E402
import pzlib as pz  # noqa: E402

PX_POR_M = 36 / 0.50                     # píxeles de pantalla por metro de juego (zoom normal)
# muñeca izquierda respecto de Prop1 en las animaciones vanilla de fusil (cm de juego): x lateral, y adelante, z arriba
MUNECAS = (((5.9, 20.1, 1.4), (0.1, 0.9, 0.2)), ((3.1, 17.2, -2.0), (0.9, 0.8, 0.1)))


def load(ID):
    """Importa el FBX del mod y lo devuelve al marco de trabajo (X adelante, Z arriba, metros de juego)."""
    data = json.loads((pz.ART / ID / "attachments.json").read_text())
    pz.reset()
    bpy.ops.import_scene.fbx(filepath=str(gk.MODELS / f"{ID}.fbx"), global_scale=100.0, axis_forward="Y",
                             axis_up="Z", bake_space_transform=True)
    ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    ob.data.transform(ob.matrix_world)
    ob.matrix_world = Matrix.Identity(4)
    M = gk.S @ gk.game_matrix(data["kind"])
    ob.data.transform(M.inverted())
    if M.determinant() < 0:
        ob.data.flip_normals()
    img = pz.ART / ID / f"{ID}.png"
    m = bpy.data.materials.new(ID)
    m.use_nodes = True
    t = m.node_tree.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(str(img))
    m.node_tree.links.new(t.outputs[0], m.node_tree.nodes["Principled BSDF"].inputs[0])
    ob.data.materials.clear()
    ob.data.materials.append(m)
    return ob, data["kind"]


def bounds(ob):
    lo = Vector([min(v.co[i] for v in ob.data.vertices) for i in range(3)])
    hi = Vector([max(v.co[i] for v in ob.data.vertices) for i in range(3)])
    return lo, hi


def manos(ID):
    from PIL import Image
    ob, kind = load(ID)
    lo, hi = bounds(ob)
    marks = [((0.0, 0.0, 0.0), (0.9, 0.2, 0.2))]
    if kind != "handgun":
        marks += [((gy / 100, -gx / 100, gz / 100), col) for (gx, gy, gz), col in MUNECAS]
    objs = [ob] + [pz.sphere(f"mano{i}", 0.012, loc=p, mat=pz.mat(f"mano{i}", c, dirt=0.0), segs=16, rings=10)
                   for i, (p, c) in enumerate(marks)]
    lo = Vector([min(lo[i], *(p[i] for p, _ in marks)) for i in range(3)])
    hi = Vector([max(hi[i], *(p[i] for p, _ in marks)) for i in range(3)])
    c = (lo + hi) / 2
    L = max(hi.x - lo.x, 2.5 * (hi.z - lo.z))
    out = pz.ART / ID
    a, b = out / "_m.png", out / "_m2.png"
    hs.closeup(objs, a, tuple(c), dist=1.0, direction=(0.0, -1.0, 0.0), size=(1200, 480), ortho=L * 1.08, light=0.6)
    hs.closeup(objs, b, tuple(c), dist=1.0, direction=(0.6, -0.6, 0.9), size=(1200, 560), ortho=L * 1.2, light=0.6)
    sheet = Image.new("RGB", (1200, 1040), (46, 47, 50))
    sheet.paste(Image.open(a).convert("RGB"), (0, 0))
    sheet.paste(Image.open(b).convert("RGB"), (0, 480))
    a.unlink()
    b.unlink()
    sheet.save(out / "verif_manos.png")
    return ob


def escala(ids):
    """Cada arma en 3/4 al tamaño de pantalla del juego (x3, sin suavizar) y el nombre."""
    from PIL import Image, ImageDraw
    tiles = []
    for ID in ids:
        ob, _ = load(ID)
        lo, hi = bounds(ob)
        L = hi.x - lo.x
        p = pz.ART / ID / "_g.png"
        hs.closeup([ob], p, tuple((lo + hi) / 2), dist=1.0, direction=(0.55, -1.0, 0.9), size=(1000, 500),
                   ortho=L * 1.05, light=0.8)
        big = Image.open(p).convert("RGB")
        p.unlink()
        w = max(8, round(L * 1.05 * PX_POR_M))
        sm = big.resize((w, max(4, w // 2)), Image.LANCZOS)
        tiles.append((ID, sm.resize((sm.width * 3, sm.height * 3), Image.NEAREST), L))
    cols = 4
    cw = max(t.width for _, t, _ in tiles) + 20
    ch = max(t.height for _, t, _ in tiles) + 30
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw, rows * ch), (70, 72, 74))
    d = ImageDraw.Draw(sheet)
    for i, (ID, t, L) in enumerate(tiles):
        x, y = (i % cols) * cw + 10, (i // cols) * ch + 4
        d.text((x, y), f"{ID[3:]}  {L * PX_POR_M:.0f} px", fill=(255, 220, 120))
        sheet.paste(t, (x, y + 18))
    sheet.save(pz.ART / "verif_escala_juego.png")


if __name__ == "__main__":
    ids = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not ids:
        ids = sorted(p.parent.name for p in pz.ART.glob("AT_*/attachments.json")
                     if (gk.MODELS / f"{p.parent.name}.fbx").exists() and "Mag" not in p.parent.name)
    for ID in ids:
        manos(ID)
        print(f"[verif] {ID}: manos")
    if "--escala" in sys.argv:
        escala(ids)
        print("[verif] escala de juego")
