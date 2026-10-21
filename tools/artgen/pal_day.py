"""Overcast-day palette for the Crossroad (teal/olive gloom of the original art) + shared helpers."""
import math, random
from common import hx, ramp, h32, make_noise, band, FONT, text_width, draw_text

SKY   = ramp('#141f1e #1a2827 #21312f #283b38 #30463f #3a5249 #455e55 #526b62')     # overcast, dark top -> hazy horizon
HAZE  = ramp('#1c2825 #243330 #2c3e3a #354945 #3f5550 #4a625c #566e67')             # atmospheric fog
STONE = ramp('#0f1412 #161c19 #1e2622 #27302b #313b35 #3c4740 #48544c #56635a #667468 #778577')   # concrete / masonry
WOOD  = ramp('#120f0b #1c1711 #282017 #352b1f #443827 #544634 #665743')             # dark timber
WARM  = ramp('#2a1d14 #42291a #5c3a24 #7a5033 #946a45 #ad8560')                     # rust, dry wood, leather
GLOW  = ramp('#6e5424 #957130 #bb8f3e #d9ad52 #efcb73')                             # lit windows, lamps
RED   = ramp('#2b0f0d #3f1612 #58201a #732c22 #8c3a2c #a24a37')                     # the corpse's robe
CAP   = ramp('#4a4430 #67603f #857c52 #a39968 #c0b67f #d9d096')                     # pale mushroom cap
BONE  = ramp('#3f4a44 #566359 #6f7c70 #8a9789 #a7b2a3')                             # the face, hands (green-grey bone)
MYC   = ramp('#143a22 #1f5a32 #3f8f5a #7fff8e #c8ffd0 #f0fff2')                     # mycelium / bioluminescence
STUCCO = ramp('#3e3f31 #51523f #65664e #7a7c5f #90926f #a6a883')                    # hangar plaster (Riga market)
LEAF  = ramp('#1b3320 #28482a #3a6336 #4f7f44 #6a9a55 #8db36c')                     # living plants (growth props)
FLOWER = ramp('#c75a55 #e08a4a #f0d070 #e8c3d0 #f6f0e0')                            # blossoms
BLOSSOM = ramp('#6e4652 #95606f #bd8494 #dcaab6 #f0d2d8')                              # spring blossom (cherry trees)
METAL = ramp('#2a3a3c #35494b #41585a #4e6769 #5c7677 #6f8b89 #86a19e')                             # blue-grey sheet-metal roofs
INK   = hx('#070a09')
FOG   = (58, 82, 78)
RAMPS = {'K': SKY, 'H': HAZE, 'T': STONE, 'D': WOOD, 'W': WARM, 'G': GLOW, 'R': RED, 'C': CAP, 'B': BONE, 'M': MYC, 'P': STUCCO, 'E': METAL, 'L': LEAF, 'X': FLOWER, 'Q': BLOSSOM}
ALL = sorted({c for r in RAMPS.values() for c in r} | {INK, FOG})

def nearest(c):
    return min(ALL, key=lambda p: (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2 + (p[2] - c[2]) ** 2)
BAYER2 = [[0, 2], [3, 1]]
def fogged(c, f, x, y):
    """blend toward the haze by depth, quantised with a 2x2 ordered dither, snapped to the palette"""
    if f <= 0.02: return c
    q = math.floor(f * 4 + BAYER2[y % 2][x % 2] / 4) / 4
    if q <= 0: return c
    if q >= 1: return FOG
    return nearest(tuple(int(c[i] + (FOG[i] - c[i]) * q) for i in range(3)))

def write_gpl(path):
    out = ['GIMP Palette', 'Name: Crossroad Overcast', 'Columns: 10', '#']
    for n, r in (('Sky', SKY), ('Haze', HAZE), ('Stone', STONE), ('Wood', WOOD), ('Warm', WARM), ('Glow', GLOW), ('Red', RED), ('Cap', CAP), ('Bone', BONE), ('Myc', MYC), ('Stucco', STUCCO), ('Metal', METAL), ('Leaf', LEAF), ('Flower', FLOWER), ('Blossom', BLOSSOM)):
        for i, c in enumerate(r): out.append('%3d %3d %3d\t%s %d' % (c[0], c[1], c[2], n, i + 1))
    out.append('%3d %3d %3d\tInk' % INK); out.append('%3d %3d %3d\tFog' % FOG)
    open(path, 'w').write('\n'.join(out) + '\n')
    return len(out) - 4
