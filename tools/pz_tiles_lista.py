"""Genera la lista de hojas de tiles del juego para el catálogo de Modo Creativo (plan B cuando
getWorld():getAllTilesName() viene vacío fuera del modo debug).
Lee los .tiles de la carpeta media del juego (definiciones de tiles: nombre de la hoja y cantidad de tiles)
y escribe Contents/mods/ModoCreativo/42/media/lua/client/ModoCreativo_Tiles.lua con solo
{nombre_de_hoja = cantidad}: ningún archivo ni imagen del juego va al repo.
Uso: python tools/pz_tiles_lista.py "D:/SteamLibrary/steamapps/common/ProjectZomboid/media"
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Contents/mods/ModoCreativo/42/media/lua/client/ModoCreativo_Tiles.lua"


class Lector:
    def __init__(self, data, endian):
        self.d, self.p, self.e = data, 0, endian

    def entero(self):
        v = struct.unpack_from(self.e + "i", self.d, self.p)[0]
        self.p += 4
        return v

    def texto(self):
        fin = self.d.index(b"\n", self.p)
        s = self.d[self.p:fin].decode("utf-8", "replace")
        self.p = fin + 1
        return s


def leer(path, endian):
    data = path.read_bytes()
    r = Lector(data, endian)
    if data[:4] == b"tdef":
        r.p = 4
        r.entero()                       # versión
    n = r.entero()
    if not 0 < n < 20000:
        raise ValueError(f"cantidad de hojas rara: {n}")
    hojas = {}
    for _ in range(n):
        nombre = r.texto()
        r.texto()                        # imagen
        w, h = r.entero(), r.entero()
        r.entero()                       # número de hoja
        cant = r.entero()
        if not (nombre.isprintable() and 0 <= cant <= 4096 and 0 <= w <= 256 and 0 <= h <= 256):
            raise ValueError(f"hoja rara: {nombre!r} {cant}")
        for _ in range(cant):
            for _ in range(r.entero()):
                r.texto()
                r.texto()
        hojas[nombre] = max(hojas.get(nombre, 0), cant)
    return hojas


def main():
    media = Path(sys.argv[1])
    archivos = sorted(media.glob("*.tiles")) + sorted(media.glob("**/tiledefinitions*.tiles"))
    hojas, vistos = {}, set()
    for f in archivos:
        if f in vistos:
            continue
        vistos.add(f)
        for e in ("<", ">"):
            try:
                h = leer(f, e)
                print(f"{f.name}: {len(h)} hojas ({'little' if e == '<' else 'big'} endian)")
                for k, v in h.items():
                    hojas[k] = max(hojas.get(k, 0), v)
                break
            except Exception as ex:          # noqa: BLE001
                err = ex
        else:
            print(f"{f.name}: no se pudo leer ({err})")
    if not hojas:
        sys.exit("no se encontró ninguna hoja de tiles")
    lineas = ["-- Generado por tools/pz_tiles_lista.py: hojas de tiles del juego y cuántos tiles tiene cada una.",
              "-- Solo nombres y cantidades (plan B del catálogo de Modo Creativo).",
              "ModoCreativo = ModoCreativo or {}", "ModoCreativo.TILESETS = {"]
    for k in sorted(hojas):
        lineas.append(f'    ["{k}"] = {hojas[k]},')
    lineas.append("}")
    OUT.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"{len(hojas)} hojas -> {OUT}")


if __name__ == "__main__":
    main()
