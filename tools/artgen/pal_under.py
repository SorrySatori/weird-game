"""Underground palette for the intro (the Obazoba's cavern + the Council chamber of the Highest Humenium Council).
Dark cave rock and roots, bioluminescent mycelium as the main light, warm candle accents, robe colours per archpriest."""
import math
from common import hx, ramp, h32, make_noise, band

ROCK  = ramp('#07080a #0c0e0e #121513 #191d19 #21261f #2a3027 #343b30 #3f473a #4b5444 #59634f')   # cave stone
ROCKG = ramp('#08100c #0c1711 #111f16 #16291c #1c3423 #23412a #2b4f32 #345e3b #3e6e45')            # stone lit by the pool
ROOT  = ramp('#0d0a07 #150f0b #1e1610 #281d15 #33261b #3f2f21 #4c3928 #5a4430 #6b5139')            # roots, timber
MYC   = ramp('#0c2418 #123622 #1a4d2e #24683b #34874b #4fa862 #74cc7f #a3eaa3 #d4ffd2 #f4fff2')   # mycelium light
CAP   = ramp('#2a2418 #3b3322 #4e442e #62573a #786b48 #8f8158 #a7986b #bfb07f #d6c897 #ebe0b5')   # pale cap / carved bone-stone
ROT   = ramp('#160b0a #22100d #321611 #451d15 #5a261a #6e3220 #834028 #9a5232')                    # the rotting half
GOLD  = ramp('#3a2610 #5a3a16 #7d531f #a16f2a #c48f3a #e0b050 #f3d27a #fff0c0')                    # candles, embroidery
PURP  = ramp('#120a14 #1c1020 #28172d #35203b #432a4a #52365a #62436b #745480')                    # Varhun
IVORY = ramp('#24221c #33302a #45413a #58534a #6d675c #827b6e #999283 #b0a998 #c7c0ad')            # Tynri
MOSS  = ramp('#0e140c #141d11 #1b2717 #23321e #2c3e25 #364b2d #415935 #4e6a3f')                    # Rhull
BROWN = ramp('#170e08 #22150c #2f1d10 #3e2715 #4f321b #613e22 #764b29 #8c5a31 #a46c3b')            # elders (Thaal's order)
SKIN  = ramp('#21180f #302318 #423123 #55412f #6a523c #80654b #977a5c #ad8f6e #c4a684')            # old human skin
YEL   = ramp('#4a3a08 #74600e #a68c18 #d4b82a #f2dc4a #fff59a')                                    # Tynri's eye-mushrooms
INK   = hx('#040505')
RAMPS = {'R': ROCK, 'g': ROCKG, 'O': ROOT, 'M': MYC, 'C': CAP, 'X': ROT, 'G': GOLD, 'P': PURP, 'I': IVORY,
         'S': MOSS, 'B': BROWN, 'K': SKIN, 'Y': YEL}
ALL = sorted({c for r in RAMPS.values() for c in r} | {INK})

def col(k, v):
    """ramp key + (float) index -> colour, clamped"""
    r = RAMPS[k]
    return r[max(0, min(len(r) - 1, int(v)))]

def write_gpl(path):
    names = (('Rock', ROCK), ('RockLit', ROCKG), ('Root', ROOT), ('Mycelium', MYC), ('Cap', CAP), ('Rot', ROT),
             ('Gold', GOLD), ('Varhun', PURP), ('Tynri', IVORY), ('Rhull', MOSS), ('Elder', BROWN), ('Skin', SKIN),
             ('EyeShroom', YEL))
    out = ['GIMP Palette', 'Name: Obazoba Underground', 'Columns: 10', '#']
    for n, r in names:
        for i, c in enumerate(r): out.append('%3d %3d %3d\t%s %d' % (c[0], c[1], c[2], n, i + 1))
    out.append('%3d %3d %3d\tInk' % INK)
    open(path, 'w').write('\n'.join(out) + '\n')
    return len(out) - 4
