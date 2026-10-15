"""Genera las fichas HTML del concept art (una por arma + hoja general).

Uso:  python tools/concept/cards.py && node tools/concept/render.js
Salida: concept/html/*.html -> concept/*.png
"""
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from art import DEFS  # noqa: E402
from weapons import WEAPONS  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "concept" / "html"

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0b0a0a;font-family:Inter,sans-serif;color:#ece6dc}
.card{position:relative;width:1600px;height:900px;overflow:hidden;
  background:radial-gradient(ellipse 60% 70% at 33% 48%,#3a332d 0%,#1e1a17 45%,#0d0b0a 100%)}
.noise{position:absolute;inset:0;opacity:.5;mix-blend-mode:overlay}
.stripe{position:absolute;left:-60px;bottom:38px;width:760px;height:26px;transform:rotate(-2deg);
  background:repeating-linear-gradient(-45deg,#f2b818 0 22px,#141210 22px 44px);opacity:.85;
  box-shadow:0 4px 14px #000a}
.art{position:absolute;left:-6px;top:112px;width:1020px;height:623px}
.panel{position:absolute;right:0;top:0;width:600px;height:900px;padding:58px 56px 0 40px;
  background:linear-gradient(90deg,#0d0b0a00 0%,#0d0b0ad9 14%,#0d0b0af2 100%)}
.num{font:800 15px Inter;letter-spacing:.32em;color:#f2b818}
.num b{color:#c81e1e}
h1{font:900 76px/0.92 'Inter Display';letter-spacing:-.01em;text-transform:uppercase;margin:14px 0 12px;
  color:#f6f0e6;text-shadow:0 3px 0 #000,0 0 28px #c81e1e55}
.tag{font:italic 500 21px/1.35 Inter;color:#d9b77a;margin-bottom:24px}
.combo{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-bottom:24px}
.combo .lbl{font:800 13px Inter;letter-spacing:.24em;color:#8f877c;margin-right:4px}
.chip{font:700 16px Inter;color:#141210;background:#f2b818;padding:7px 13px;border-radius:3px;
  box-shadow:0 2px 0 #7a5a06}
.plus{font:900 24px 'Inter Display';color:#c81e1e}
.intro{font:400 18.5px/1.55 Inter;color:#d8d1c6;margin-bottom:26px}
.stats{display:grid;grid-template-columns:118px 1fr 30px;row-gap:9px;align-items:center;margin-bottom:24px}
.stats .k{font:700 14px Inter;letter-spacing:.14em;text-transform:uppercase;color:#a79f93}
.bar{display:flex;gap:4px}
.bar i{display:block;width:100%;height:13px;background:#2a2622;transform:skewX(-18deg)}
.bar i.on{background:linear-gradient(#ff5a3a,#c81e1e);box-shadow:0 0 8px #c81e1e88}
.stats .v{font:800 15px Inter;color:#f6f0e6;text-align:right}
.special{border-left:5px solid #c81e1e;background:#c81e1e1f;padding:13px 16px;font:500 17px/1.45 Inter;color:#efe7da}
.special b{display:block;font:800 13px Inter;letter-spacing:.26em;color:#ff6b4a;margin-bottom:4px}
.footer{position:absolute;left:44px;top:34px;font:800 15px Inter;letter-spacing:.34em;color:#f2b818}
.footer span{color:#8f877c;font-weight:600;letter-spacing:.2em}
/* hoja general */
.sheet{width:1600px;padding:56px 50px 40px;background:radial-gradient(ellipse at 50% 30%,#2c2622,#0d0b0a 75%)}
.sheet h2{font:900 64px 'Inter Display';text-transform:uppercase;color:#f6f0e6;text-shadow:0 3px 0 #000}
.sheet .sub{font:600 18px Inter;color:#f2b818;letter-spacing:.26em;margin:6px 0 34px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.tile{position:relative;background:#00000055;border:1px solid #ffffff14;border-radius:6px;height:330px;overflow:hidden}
.tile svg{position:absolute;left:0;top:8px;width:500px;height:306px}
.tile .n{position:absolute;left:18px;bottom:14px;font:900 30px 'Inter Display';text-transform:uppercase;color:#f6f0e6;text-shadow:0 2px 0 #000}
.tile .c{position:absolute;left:20px;top:14px;font:800 13px Inter;letter-spacing:.26em;color:#f2b818}
"""

NOISE = """<svg class="noise" width="1600" height="900"><filter id="bgn"><feTurbulence type="fractalNoise"
baseFrequency="0.8" numOctaves="3" seed="2"/><feColorMatrix values="0 0 0 0 .5 0 0 0 0 .45 0 0 0 0 .4 0 0 0 .55 0"/></filter>
<rect width="100%" height="100%" filter="url(#bgn)"/></svg>"""


def weapon_svg(w, angle=-15, cls="art", extra_attrs=""):
    return (f'<svg class="{cls}" viewBox="-20 -40 1440 880" {extra_attrs}>{DEFS}'
            f'<g filter="url(#fDrop)"><g transform="rotate({angle} 700 400)">{w["art"]()}</g></g></svg>')


def page(body):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"


def card(i, w):
    stats = ""
    for k, v in w["stats"].items():
        bars = "".join(f'<i class="{"on" if n < v else ""}"></i>' for n in range(10))
        stats += f'<div class="k">{k}</div><div class="bar">{bars}</div><div class="v">{v}</div>'
    combo = '<span class="plus">+</span>'.join(f'<span class="chip">{html.escape(c)}</span>' for c in w["combo"])
    return page(f"""
<div class="card">{NOISE}
  <div class="footer">ARSENAL DE CHATARRA <span>· PROJECT ZOMBOID B42</span></div>
  {weapon_svg(w)}
  <div class="stripe"></div>
  <div class="panel">
    <div class="num">COMBO <b>{i + 1:02d}</b> / {len(WEAPONS):02d}</div>
    <h1>{html.escape(w['name'])}</h1>
    <div class="tag">{html.escape(w['tagline'])}</div>
    <div class="combo"><span class="lbl">COMBO</span>{combo}</div>
    <p class="intro">{html.escape(w['intro'])}</p>
    <div class="stats">{stats}</div>
    <div class="special"><b>ESPECIAL</b>{html.escape(w['special'])}</div>
  </div>
</div>""")


def sheet():
    tiles = "".join(
        f'<div class="tile"><div class="c">COMBO {i + 1:02d}</div>{weapon_svg(w, -18, "")}'
        f'<div class="n">{html.escape(w["name"])}</div></div>' for i, w in enumerate(WEAPONS))
    return page(f"""<div class="sheet"><h2>Arsenal de Chatarra</h2>
<div class="sub">{len(WEAPONS)} ARMAS COMBINADAS · PROJECT ZOMBOID B42</div><div class="grid">{tiles}</div></div>""")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.html"):
        old.unlink()
    for i, w in enumerate(WEAPONS):
        (OUT / f"{i + 1:02d}_{w['id']}.html").write_text(card(i, w), encoding="utf-8")
    (OUT / "00_arsenal.html").write_text(sheet(), encoding="utf-8")
    print(f"{len(WEAPONS)} fichas + hoja general en {OUT}")


if __name__ == "__main__":
    main()
