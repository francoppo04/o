"""Ficha HD de AT_GravRecon (editable). Formato de piezas: ver tools/blender/guns/hd.py (build_parts).
Pistola tipo Glock 17 con cubierta delantera (compensador) oscura y corredera plateada."""

# estrías de la empuñadura: líneas paralelas que suben hacia atrás (pendiente del dibujo)
_ESTRIAS = []
for _i in range(14):
    _yl = 322 + 4.5 * _i
    _xl = 460 + (_yl - 321) * 0.25
    _xr = min(504.0, (484 + 0.55 * (_yl - 314) + 0.11 * _xl) / 1.11)
    if _yl - 0.2 * (_xr - _xl) > 364:          # abajo: terminan antes del escalón de la base
        _xr = 491.0
    _yr = _yl - 0.2 * (_xr - _xl)
    _ESTRIAS.append(("line", [(_xl, _yl), (_xr, _yr)], 1.1, (16, 16, 18)))
    _ESTRIAS.append(("line", [(_xl, _yl + 1.3), (_xr, _yr + 1.3)], 0.6, (78, 79, 84)))

PLATA = (205, 206, 208)
OSC = (24, 24, 26)

SPEC = {'img': '11.webp',
 'sil': 'AT_GravRecon',
 'mm_px': 0.6688741721854304,
 'origin': (466, 295),
 'bore_y': 266,
 'flip': True,
 'K': 0.8977556109725686,
 'offset': (0.0, 0.0),
 'kind': 'handgun',
 'fill': False,
 'parts': [
     # cubierta/compensador delantero: bloque alto + labio en rampa; tapa superior hasta el punto de mira
     ('s', 'cubierta', [(211, 277), (231, 268.5), (231.5, 252.5), (238.5, 248), (317, 248), (317, 255.5),
                        (301, 255.5), (301, 285), (211, 285)], 25, 'anod', {'bevel': 0.8}),
     # punto de mira (domo)
     ('s', 'punto', [(315.5, 256.5), (315.5, 249.5), (319, 246.5), (322, 245.5), (325.5, 246), (329, 250),
                     (331.5, 253.5), (333.5, 256.5)], 6, 'anod', {'round': True}),
     # corredera plateada (trasera inclinada)
     ('s', 'corredera', [(299, 254), (511, 254), (513.5, 257.5), (517.5, 274), (299, 274)], 23.5, 'plata',
      {'bevel': 0.8}),
     # alza con rampa delantera
     ('s', 'alza', [(470, 256.5), (480, 252.5), (487.5, 249), (490, 244), (508.5, 244), (510, 249.5),
                    (513.5, 257)], 13, 'anod', {'bevel': 0.8}),
     # armazón: guardapolvo, techo del guardamonte, cola trasera (beavertail)
     ('s', 'armazon', [(299, 273), (516.5, 273), (515.5, 262.5), (522, 263), (523.5, 267), (525.5, 285),
                       (523.5, 287), (518, 287.5), (510, 288.2), (505, 290.6), (501, 294), (499, 298),
                       (498.5, 301), (446, 301), (441, 297.5), (371.5, 297.5), (371.5, 288.5), (366.5, 288.5),
                       (366.5, 285), (299, 285)], 26, 'pol', {}),
     # dientes del riel bajo el guardapolvo
     ('box', 'diente1', 317, 284, 322, 288, -10, 10, 'pol'),
     ('box', 'diente2', 328, 284, 333.5, 288.3, -10, 10, 'pol'),
     ('box', 'diente3', 340, 284, 345.5, 288.3, -10, 10, 'pol'),
     ('box', 'diente4', 350.5, 284, 355.5, 288.3, -10, 10, 'pol'),
     ('box', 'diente5', 361, 284, 366.5, 288.3, -10, 10, 'pol'),
     # guardamonte cerrado (el hueco viene de la silueta); se le recorta el gatillo
     ('s', 'guardamonte', [(369, 293), (446, 293), (446, 317), (442.5, 319), (436, 325), (389, 323.5),
                           (386, 318), (386, 305), (369, 296)], 11, 'pol',
      {'bevel': 1.6, 'segs': 2,
       'holes': [[(420, 292), (430, 292), (430, 309.7), (427, 310.2), (423.5, 315.8), (416.5, 315.8),
                  (418.5, 309.5), (420.5, 304)]]}),
     # gatillo (cuelga del armazón, dentro del guardamonte)
     ('s', 'gatillo', [(420, 292), (430, 292), (430, 309.7), (427, 310.2), (423.5, 315.8), (416.5, 315.8),
                       (418.5, 309.5), (420.5, 304)], 6, 'acero', {'bevel': 0.6}),
     # empuñadura (frente con dedos, dorso recto); abajo el escalón de la base
     ('s', 'empunadura', [(440, 296), (499.5, 296), (498, 302), (502, 316), (506, 319), (509.5, 326),
                          (512.5, 334), (520, 350), (520, 356), (517.5, 361.5), (495, 369), (494.5, 384.5),
                          (468.5, 391.5), (464, 388), (459, 368), (452, 350), (445, 330), (439, 318)],
      29, 'pol', {'round': True}),
     # base del cargador plateada (en L, abraza el escalón)
     ('s', 'base', [(493, 368), (517, 360), (520.5, 360), (520.5, 385.5), (518, 387.5), (470, 400.5),
                    (465.5, 399), (465, 393), (467.5, 389.5), (493, 383.3)], 30, 'plata',
      {'bevel': 2.5, 'segs': 2}),
     # mandos plateados en relieve
     ('s', 'reten', [(408, 281), (409, 280), (412.5, 280), (416.5, 284), (420, 285), (421.5, 286.5),
                     (421.5, 289), (420, 290.5), (415.5, 290)], 27.6, 'plata', {'cut': False, 'bevel': 0.4}),
     ('s', 'boton', [(451.5, 280.2), (461.5, 280.2), (462, 283.8), (451, 283.8)], 27.6, 'plata',
      {'cut': False, 'bevel': 0.4}),
     ('s', 'suelta_carg', [(447, 309.5), (455.5, 309.2), (456.5, 311), (455.5, 313.2), (446.5, 313.2),
                           (446, 311.5)], 30.5, 'plata', {'cut': False, 'bevel': 0.5}),
     # pernos
     ('pin', 392.3, 287.3, 1.3, 26),
     ('pin', 436.5, 288.5, 1.3, 26),
     ('pin', 485.6, 281.5, 1.7, 26),
     ('pin', 497.8, 288.6, 1.2, 26),
     ('pin', 512.6, 356.3, 1.2, 29),
 ],
 'decals': [
     # cubierta: líneas de despiece y muescas
     ('line', [(239, 254), (300, 254)], 0.8, OSC),
     ('line', [(232, 270), (300, 270)], 0.8, OSC),
     ('line', [(240, 254), (240, 284)], 0.8, OSC),
     ('line', [(299, 255), (299, 284)], 0.9, OSC),
     ('hole', 242, 282.5, 1.4, 1.2),
     ('hole', 283.5, 282.5, 1.4, 1.2),
     # rayas diagonales al frente de la corredera
     ('poly', [(299.5, 255), (320.5, 255), (323, 258), (323.5, 273), (299.5, 273)], (52, 52, 55)),
     ('line', [(300.5, 256), (322, 270)], 1.6, PLATA),
     ('line', [(300.5, 262), (317.5, 271.8)], 1.6, PLATA),
     ('line', [(301, 268), (307.5, 271.8)], 1.4, PLATA),
     ('line', [(306, 256), (311, 258.5)], 1.2, PLATA),
     ('line', [(313, 257.5), (321.5, 261)], 1.2, PLATA),
     ('line', [(330.5, 255), (330.5, 273)], 0.6, (120, 120, 124)),
     # ranura y ventana de expulsión
     ('slot', 351, 258, 392, 263.3),
     ('line', [(352, 266.5), (391, 266.5)], 0.6, (120, 120, 124)),
     ('poly', [(393, 257.5), (410, 257.5), (410, 267.8), (393, 267.8)], (58, 58, 61)),
     ('poly', [(410, 257.5), (436, 257.5), (436, 268), (410, 268)], (22, 22, 24)),
     ('poly', [(412, 259.3), (434, 259.3), (434, 266.3), (412, 266.3)], (96, 96, 99)),
     # tapa trasera con tornillos
     ('line', [(458, 255.5), (456, 260), (455.8, 266), (457.8, 272.8)], 0.9, OSC),
     ('hole', 486.7, 262.2, 2.2, 1.6), ('hole', 498.5, 262.2, 2.0, 1.6),
     ('hole', 477.8, 268.9, 2.0, 1.7), ('hole', 506.7, 268.5, 2.0, 1.8),
     ('hole', 491, 267.4, 0.8, 0.8), ('hole', 499.3, 269.3, 0.8, 0.8), ('hole', 486.7, 270.4, 0.7, 1.0),
     ('hole', 465.6, 261.8, 0.8, 1.2),
     # armazón: barra clara del guardapolvo y juntas
     ('poly', [(344, 276), (405, 276), (405.5, 277.4), (405, 278.8), (344, 278.8)], PLATA),
     ('line', [(475, 276), (475.3, 292), (480, 300.5), (490, 313.5), (496.5, 324)], 0.8, OSC),
     ('line', [(433, 289), (443, 297), (448, 305)], 0.8, OSC),
     ('line', [(299, 273.6), (517, 273.6)], 0.8, OSC),
     # panel estriado de la empuñadura
     ('line', [(451.5, 320), (483, 314), (497, 327), (505, 346), (508, 357)], 0.8, OSC),
 ] + _ESTRIAS,
 'att': {'muzzle': 213, 'light': (342, 288)},
 'fill_w': 24,
 'fill_mat': 'pol',
 'fit_lathes': True}
