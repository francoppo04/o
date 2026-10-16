"""Extrae de la instalación de Project Zomboid cómo están conectadas las animaciones de ataque
cuerpo a cuerpo (AnimSets XML + archivos de animación), para replicar la estructura en el mod.

Uso (en la PC con el juego, Python normal):
    python tools/inspect_vanilla_anims.py "C:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid" > anims.txt

Imprime:
  1. el árbol de carpetas de media/AnimSets/player (solo nombres)
  2. el XML completo de los nodos de ataque/reposo cuerpo a cuerpo (bate, pesada, lanza, cuchillo)
  3. los archivos de animación de ataque en media/anims_X (nombre, tamaño, formato)
"""
import re
import sys
from pathlib import Path

KEYS = re.compile(r"bat|heavy|spear|stab|melee|2handed|twohand|attack", re.I)
MAX_FILES = 40


def main():
    if len(sys.argv) < 2:
        sys.exit("Falta la ruta de instalación de Project Zomboid")
    media = Path(sys.argv[1]) / "media"
    animsets = media / "AnimSets" / "player"

    print("=== 1. ARBOL media/AnimSets/player ===")
    for d in sorted(p for p in animsets.rglob("*") if p.is_dir()):
        files = sorted(f.name for f in d.iterdir() if f.is_file())
        print(f"{d.relative_to(animsets)}/  ({len(files)}) {', '.join(files[:25])}{' ...' if len(files) > 25 else ''}")

    print("\n=== 2. XML DE ATAQUE CUERPO A CUERPO ===")
    shown = 0
    for f in sorted(animsets.rglob("*.xml")):
        rel = f.relative_to(animsets).as_posix()
        text = f.read_text(encoding="utf-8", errors="replace")
        if not (KEYS.search(rel) and ("melee" in rel.lower() or "attack" in rel.lower() or "bat" in text.lower())):
            continue
        if shown >= MAX_FILES:
            print(f"(... más archivos omitidos: {rel})")
            continue
        print(f"\n----- {rel} -----")
        print(text.strip())
        shown += 1

    print("\n=== 3. ANIMACIONES DE ATAQUE EN anims_X ===")
    for f in sorted((media / "anims_X").rglob("*")):
        if f.is_file() and re.search(r"attack|bat|heavy|spear|stab|swing", f.name, re.I):
            head = f.read_bytes()[:16]
            kind = "texto" if head.startswith(b"xof") and b"txt" in head else ("binario" if f.suffix.lower() == ".x" else f.suffix)
            print(f"{f.relative_to(media)}  {f.stat().st_size // 1024} KB  {kind}")


if __name__ == "__main__":
    main()
