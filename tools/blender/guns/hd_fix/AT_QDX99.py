"""Ficha HD de AT_QDX99 (editable). Formato de piezas: ver tools/blender/guns/hd.py (build_parts).
Subfusil bullpup de lámina (arma real más parecida: QCW-05, 500 mm). Coordenadas en px de 11.webp."""
import math

OSC = (18, 18, 20)          # líneas de panel
CLARO = (150, 151, 153)     # piezas claras del dibujo


def _ranuras_emp():
    """Estrías horizontales del panel de la empuñadura (panel inclinado)."""
    out = []
    for y in range(784, 834, 4):
        xl = 295 + (y - 781) * 0.316
        xr = min(327 + (y - 781) * 0.408, 347)
        out.append(("line", [(xl, y), (xr, y)], 1.3, OSC))
    return out


def _elipse(cx, cy, rx, ry, n=16):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


SPEC = {'img': '11.webp',
 'sil': 'AT_QDX99',
 'mm_px': 1.1441647597254005,
 'origin': (290, 758),
 'bore_y': 708,
 'flip': True,
 'K': 0.628428927680798,
 'offset': (0.0, 0.0),
 'kind': 'handgun',
 'parts': [
     # bocacha (cañón superior) y tubo inferior
     ('lathe', 'bocacha', [(111, 9.0), (112.5, 10.3), (120, 10.3), (120.5, 12.6), (143.5, 12.6), (144, 11.4),
                           (150, 11.4)], 705, 'anod'),
     ('lathe', 'tapa_tubo', [(111.5, 6.2), (112.5, 7.6), (118.5, 7.6)], 732, 'anod'),
     ('lathe', 'tubo_inf', [(118, 7.0), (149, 7.0)], 732, 'gris'),
     ('s', 'soporte', (129, 736, 149, 743.5), 12, 'anod', {'cut': False}),
     # frente: bloque delantero con aletas
     ('s', 'frente', [(146.5, 674), (174, 674), (177, 684), (213, 684), (213, 763), (161, 763), (157, 770),
                      (146.5, 770)], 38, 'anod', {'bevel': 1.2}),
     ('s', 'aletas', (150.5, 720.5, 209.5, 750), 40, 'anod', {'cut': False, 'ct': 1.0, 'cb': 1.0}),
     # puente superior sobre la ventana, con riel
     ('s', 'puente', [(205, 683), (321, 683), (321, 694), (205, 694)], 24, 'anod', {}),
     ('rail', 'riel', 175, 318, 685, 'top'),
     # palanca de carga (vista por la ventana)
     ('s', 'palanca', [(212, 691), (234, 691), (234, 714), (212, 714)], 14, 'acero', {}),
     # cajón: cuerpo central y brocal del cargador
     ('s', 'cajon', [(209, 689), (322, 689), (322, 711), (359, 711), (359, 719), (462, 719), (462, 770),
                     (455, 769), (390, 761), (390, 746), (219, 746), (219, 761), (209, 761)], 32, 'anod',
      {'holes': [[(213, 687), (297, 687), (302, 699), (299, 708), (288, 708.5), (280.5, 714.5), (213, 714.5)]]}),
     # torre trasera (alza)
     ('s', 'torre', [(316, 685), (321, 672), (343, 672), (345, 676), (359, 676), (361.5, 679), (361.5, 713),
                     (316, 713)], 30, 'anod', {}),
     # tapa superior trasera
     ('s', 'tapa', [(357, 695), (522, 695), (522, 721), (357, 721)], 28, 'anod', {}),
     # armazón inferior (sobre el guardamonte)
     ('s', 'armazon', [(219, 744), (391, 744), (391, 762), (381, 764), (377, 757), (336, 757), (332, 762),
                       (279, 762), (279, 760), (219, 760)], 30, 'anod', {}),
     # culata esqueleto (los huecos salen de la silueta)
     ('s', 'culata', [(455, 716), (522, 716), (522, 806), (453, 806), (453, 768)], 34, 'anod', {}),
     ('s', 'cantonera', [(519.5, 700), (541, 700), (541, 713), (539, 720), (537.5, 735), (537.5, 801),
                         (534.5, 805.5), (527.5, 805.5), (523.5, 801.5), (519.5, 801.5)], 40, 'goma',
      {'cut': False, 'bevel': 2.5, 'segs': 2}),
     # empuñadura delantera con estrías
     ('s', 'empunadura_del', [(191, 748), (226, 748), (226, 788), (234, 797), (234, 823), (231, 826),
                              (209, 826), (206, 830), (203, 830), (196, 826.5), (193, 826)], 29, 'pol',
      {'cut': False, 'round': True}),
     # guardamonte: poste delantero + barra (cierra contra el cajón y la empuñadura)
     ('s', 'guardamonte', [(223, 757), (229.5, 757), (229.5, 786), (236.5, 792.5), (289, 792.5), (292.5, 796.5),
                           (236, 796.5), (229, 795.5), (223, 791)], 11, 'anod', {'cut': False, 'bevel': 1.0}),
     ('s', 'caja_gatillo', [(267, 758), (279, 758), (284, 777), (268, 777.5)], 10, 'acero', {'cut': False}),
     ('s', 'gatillo', [(262, 758), (271, 758), (270.5, 776), (267.5, 781), (263.5, 788), (259, 788.5),
                       (258.5, 786), (265.5, 777.5), (265.5, 766)], 6, 'acero', {'cut': False, 'bevel': 0.8}),
     # empuñadura y talón
     ('s', 'empunadura', [(276, 745), (337, 745), (337, 756), (332, 760), (327.5, 770), (327.5, 782), (351, 830),
                          (352, 833), (311, 844), (308.5, 838), (291, 795), (287, 786), (285, 778), (276, 757)],
      29, 'pol', {'cut': False, 'round': True}),
     ('s', 'talon', [(307, 840), (350, 828.5), (352.5, 837), (351, 840.5), (321, 849.5), (310, 849.5),
                     (308, 845)], 32, 'pol', {'cut': False, 'bevel': 1.5}),
     # tornillos y selector
     ('pin', 336, 730, 3.2, 32),
     ('pin', 228, 731, 3.2, 32),
     ('pin', 231, 792.5, 2.4, 14),
 ],
 'decals': [
     # aletas del frente
     *[('slot', a, 721, a + 2, 749) for a in (153.5, 161.8, 170, 177, 183.6, 190, 196.3, 202.7)],
     ('line', [(148, 713), (212, 713)], 1, OSC),
     ('line', [(148, 719.5), (212, 719.5)], 1, OSC),
     ('line', [(148, 751), (212, 751)], 1, OSC),
     ('line', [(168, 685), (168, 712)], 1, OSC),
     ('poly', [(151, 690), (167, 690), (167, 705), (151, 705)], (92, 93, 96)),
     ('poly', [(161, 680), (172, 680), (172, 682.5), (161, 682.5)], CLARO),
     # visor oval
     ('poly', _elipse(194.5, 702, 14.3, 10.6), OSC),
     ('poly', _elipse(194.5, 702, 13.0, 9.3), (128, 130, 133)),
     # cajón
     ('poly', [(212, 714), (235, 714), (235, 720.5), (212, 720.5)], (112, 113, 116)),
     ('poly', [(239, 754), (277.5, 754), (277.5, 756.5), (239, 756.5)], (118, 119, 121)),
     ('poly', [(280, 735), (294, 735), (294, 738), (280, 738)], CLARO),
     ('line', [(280, 733), (318, 711), (330, 711)], 1, OSC),
     ('line', [(284, 736), (321, 714)], 1, OSC),
     ('line', [(321, 714), (321, 739)], 1, OSC),
     ('poly', _elipse(228, 731, 4.2, 4.2, 12), (160, 40, 34)),        # selector rojo
     ('hole', 228, 731, 2.0, 2.0),
     # torre
     ('line', [(332, 704), (357, 684)], 1, OSC),
     ('line', [(327, 679), (327, 711)], 1, OSC),
     # cuerpo trasero y culata
     ('line', [(362, 711), (520, 711)], 1, OSC),
     ('text', 430, 728, 'QDX MKIII', 8),
     ('line', [(467, 761), (506, 761), (506, 780), (467, 780), (467, 761)], 1, OSC),
     ('line', [(458, 721), (458, 800)], 1.2, OSC),
     ('hole', 510.5, 722, 1.6, 1.6),
     # cargador
     ('poly', [(382, 765), (391, 766), (391, 795), (382, 794)], (128, 135, 108)),
     ('line', [(381, 793.5), (452, 800)], 1, OSC),
     # empuñadura delantera: estrías y división
     *[('line', [(192, y), (207, y)], 1.5, OSC) for y in range(762, 828, 5)],
     ('line', [(208, 758), (208, 826)], 1, OSC),
     # empuñadura: estrías del panel
     *_ranuras_emp(),
 ],
 'holes': [],
 'att': {'muzzle': 111, 'optic': (285, 685), 'light': (130, 742)},
 'fill': False,
 'fill_w': 26,
 'fill_mat': 'anod',
 'fit_lathes': True,
 # óptica del mod y su montura (va aparte)
 'exclude': [[(78, 0), (575, 0), (575, 671), (318, 671), (317, 684), (246, 684), (246, 671), (78, 671)]],
 'mag': {'region': [(380.5, 757), (455, 764), (455, 801), (380.5, 795)],
         'w': 24,
         'mat': 'od',
         'o': {'cut': True, 'bevel': 1.5},
         'base': [(378.5, 793), (452.5, 800), (450.5, 806.5), (446, 807), (428, 805), (412, 802.5), (380, 801.5),
                  (378.5, 800)],
         'base_mat': 'pol'}}
