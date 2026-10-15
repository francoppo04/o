import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pzlib as pz  # noqa: E402

pz.reset()
steel = pz.mat("acero", pz.STEEL, rust=.35, blood=.2, metal=.6, rough=.45)
wood = pz.mat("madera", pz.WOOD, streaks=True, dirt=.4)
parts = [
    pz.cylinder("mango", .018, .7, loc=(.15, 0, 0), mat=wood),
    pz.box("cabeza", (.06, .04, .16), loc=(.52, 0, 0), mat=steel, bevel=.004),
]
m = pz.finish("_Test", parts, tex_size=128)
pz.previews(m, "_Test")
