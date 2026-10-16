"""AC_PalaTiburon: pala con bordes amolados en dientes de sierra y una boca de tiburón pintada.

A dos manos; agarre junto a la empuñadura en D.
Uso: python3 tools/blender/weapons/AC_PalaTiburon.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402
import kit  # noqa: E402

ID = "AC_PalaTiburon"


def shark(d, w, h):
    d.rectangle((0, 0, w, h), fill=(38, 52, 66))
    d.ellipse((w * .55, h * .18, w * .66, h * .32), fill=(235, 232, 225))
    d.ellipse((w * .59, h * .21, w * .64, h * .29), fill=(10, 10, 12))
    mouth = [(w * .45, h * .55), (w * .97, h * .48), (w * .55, h * .82)]
    d.polygon(mouth, fill=(110, 14, 18))
    for i in range(7):
        x = w * (.5 + i * .065)
        d.polygon([(x, h * (.54 - i * .01)), (x + w * .03, h * (.64 - i * .01)), (x + w * .06, h * (.53 - i * .01))],
                  fill=(240, 236, 228))
    for x in (.3, .35, .4):
        d.line((w * x, h * .3, w * x - w * .02, h * .55), fill=(16, 24, 32), width=max(2, w // 60))


def build():
    pz.reset()
    out = pz.ART / ID
    out.mkdir(parents=True, exist_ok=True)
    decal = kit.decal_png(out / "decal_tiburon.png", (256, 192), shark)
    wood = kit.wood("mango", seed=1)
    steel = kit.steel("filo", rust=.3, blood=.6, seed=2)
    paint = pz.image_mat("pintura_tiburon", decal)
    iron = kit.dark_steel("cubo")
    parts = [kit.rod("mango", -.02, .82, .018, wood, segs=10)]
    # empuñadura en D
    parts += [pz.box("d_trav", (.025, .03, .12), loc=(-.075, 0, 0), mat=wood, bevel=.006),
              pz.box("d_sup", (.07, .025, .02), loc=(-.04, 0, .05), mat=wood),
              pz.box("d_inf", (.07, .025, .02), loc=(-.04, 0, -.05), mat=wood)]
    parts.append(kit.rod("cubo", .8, .95, .026, iron, r2=.03))
    # hoja: contorno con dientes amolados en los dos bordes largos
    top, bot = [], []
    for i in range(9):
        x = .95 + i * .028
        top += [(x, .1), (x + .014, .118)]
        bot += [(x, -.1), (x + .014, -.118)]
    outline = [(.94, -.03), (.94, .03)] + top + [(1.2, .1), (1.3, 0), (1.2, -.1)] + list(reversed(bot))
    parts.append(pz.extrude("hoja", outline, .006, mat=steel))
    # cara pintada (calco) un poco por delante de cada lado
    for side, y in (("a", -.0035), ("b", .0035)):
        face = pz.extrude(f"pintura_{side}", [(.97, -.085), (1.19, -.085), (1.26, 0), (1.19, .085), (.97, .085)],
                          .001, mat=paint)
        face.location.y = y
        pz.project_uv_front(face)
        parts.append(face)
    return pz.finish(ID, parts, tex_size=256)


if __name__ == "__main__":
    pz.previews(build(), ID, grip_offset=0.0, hold_rot=(0, -55, 35))
