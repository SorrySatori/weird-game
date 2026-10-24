"""Palette for the symbiont HUD (the six symbionts + the pod "rosary").
Aseprite: symbionts.gpl (copy to ~/.config/aseprite/palettes/)."""
from common import hx, ramp, INK

CORD   = ramp('#2a281e #4a4634 #77715a #a8a084 #d2ccb0')                    # mycelial cord
HUSK   = ramp('#120e0a #1f1810 #2f2518 #433522 #5a482e #73603c #8f7a4e #ab9564')  # pod husk (open)
DRY    = ramp('#100e0c #1c1915 #2a2620 #3a352c #4c463a #615a4a #7a7260')    # sealed, shrivelled pod
CAV    = ramp('#07040a #100a16 #1a1022 #2a1a36 #3d2a4c')                    # pod cavity
VEIN   = ramp('#143a22 #1f5a32 #3f8f5a #7fff8e')                            # bioluminescent veins
LIP    = ramp('#2a1424 #4a2238 #6e3a4e #8e5464')                            # inner lip of the pod
WAX    = ramp('#3a0a0e #6e1420 #a8283a #d24a52')                            # registration seal

BRUISE = ramp('#1e0f1c #35182f #52243f #723451 #934a62 #b86e7a #d898a0')    # Thorne-Still
THORN  = ramp('#140a12 #2a1424 #4a2a3c #6a4458')
OOZE   = ramp('#3b3a12 #6b6a1c #a3a032 #d4d36a #f2f0a8')
NEME   = ramp('#0f2a1a #1b4a2c #2f7a45 #4fb866 #7fff8e #c8ffd0 #f0fff2')     # Neme
GOLD   = ramp('#7a5a1a #c99a3a #f0d27a #fff4cc')
SKY    = ramp('#2a1640 #4a2050 #7a2f55 #b2444c #e0703a #f5b25a #ffe6a0')     # Ulvarex sunset
WATER  = ramp('#0b1424 #13223a #1b3048 #2d4d6c #4a7395 #79a3c0 #b8d6e6')
IRIS   = ramp('#7a5ab8 #4ab8a8 #e0c060 #e07a9a')                            # oil-film rim
MEMB   = ramp('#12302f #1d4446 #2f6463 #4e8a86 #82b5ad #c3ddd6 #e8f5f0 #ffffff')  # Brine Scripture
AMBER  = ramp('#a86a1a #f0c060 #fff0b0')
BONE   = ramp('#1e1b16 #2a2620 #4a443a #6e6656 #958b76 #bdb39b #e2d9c2 #f6f0e0')  # Osswine
COLD   = ramp('#1a2a40 #2a4a6a #5f9ac8 #b8e0ff')
PEBBLE = ramp('#16161a #24242a #34343c #48484f #5e5e68 #787884 #9696a2 #b4b4be')  # Palinode
SHIM   = ramp('#3a2a6a #6a5ac8 #a8b8ff #e8f0ff')

ALL = [INK] + CORD + HUSK + DRY + CAV + VEIN + LIP + WAX + BRUISE + THORN + OOZE + NEME + GOLD + SKY + WATER + IRIS + MEMB + \
      AMBER + BONE + COLD + PEBBLE + SHIM

def col(k, i):
    i = int(i)
    return k[max(0, min(len(k) - 1, i))]

def write_gpl(path):
    seen, rows = set(), []
    for c in ALL:
        if c in seen: continue
        seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    with open(path, 'w') as f:
        f.write('GIMP Palette\nName: symbionts\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
