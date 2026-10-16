"""Copia la ficha actual de un arma (hd_specs.SPEC[ID], ya convertida) a hd_fix/<ID>.py para editarla a mano.
Desde ese momento manda el archivo: hd_specs lo carga y reemplaza la ficha entera.
Uso: python3 tools/blender/guns/hd_dump.py AT_GXP [AT_MD34 ...] [--force]"""
import pprint
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import hd_specs  # noqa: E402

for ID in [a for a in sys.argv[1:] if not a.startswith("--")]:
    out = HERE / "hd_fix" / f"{ID}.py"
    if out.exists() and "--force" not in sys.argv:
        print(f"{out} ya existe (usar --force para pisarlo)")
        continue
    sp = hd_specs.SPEC[ID]
    body = pprint.pformat(sp, width=118, sort_dicts=False)
    out.write_text(f'"""Ficha HD de {ID} (editable). Formato de piezas: ver tools/blender/guns/hd.py (build_parts)."""\n'
                   f"SPEC = {body}\n")
    print(f"{ID} -> {out}")
