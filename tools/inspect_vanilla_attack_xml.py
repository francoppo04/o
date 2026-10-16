"""Imprime completos los XML de AnimSets de ataque cuerpo a cuerpo que hacen falta para crear
ataques propios (nodos base, 2 manos, pesada, lanza, cuchillo e idle de 2 manos).

Uso: python tools/inspect_vanilla_attack_xml.py "<carpeta de ProjectZomboid>" > attack_xml.txt
"""
import sys
from pathlib import Path

FILES = [
    "melee/NoWeapon.xml",
    "melee/2handed/2HDefault.xml",
    "melee/2handed/2HDefaultCrit.xml",
    "melee/2handed/2HMiss.xml",
    "melee/2handed/2HOverhead.xml",
    "melee/2handed/SpearDefault.xml",
    "melee/2handed/SpearStab.xml",
    "melee/heavy/HeavyDefault.xml",
    "melee/1handed/1HDefault.xml",
    "melee/1handed/KnifeDefault.xml",
    "idle/Idle2Handed.xml",
]


def main():
    base = Path(sys.argv[1]) / "media" / "AnimSets" / "player"
    for rel in FILES:
        f = base / rel
        print(f"\n----- {rel} -----")
        print(f.read_text(encoding="utf-8", errors="replace").strip() if f.exists() else "(no existe)")
    # cualquier otro archivo de AnimSets que mencione la variable de tipo de ataque
    print("\n----- variables usadas en melee/ -----")
    names = set()
    for f in (base / "melee").rglob("*.xml"):
        t = f.read_text(encoding="utf-8", errors="replace")
        for part in t.split("<m_Name>")[1:]:
            names.add(part.split("<")[0])
    print(", ".join(sorted(names)))


if __name__ == "__main__":
    main()
