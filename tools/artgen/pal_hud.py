"""Palette for the HUD buttons (satchel, map, journal, quest note). Aseprite: hud.gpl.
Shares the wax / vein / bone ramps with the symbiont HUD so the two read as one set."""
from common import ramp, INK
from pal_symb import WAX, VEIN, BONE, CAV, col

LEATHER = ramp('#1a100a #2b1a10 #3f2616 #55341e #6e4528 #8a5a34 #a87244 #c28c58')   # satchel
MOSS    = ramp('#0c1610 #142218 #1c3022 #26402c #325438 #426a46 #568256')            # journal cover
PARCH   = ramp('#2e2416 #4a3c26 #6e5c3c #948058 #b8a374 #d4c292 #e8dab0 #f6eed2')    # paper
BRONZE  = ramp('#22180a #3e2c12 #604418 #86621e #aa842c #c8a444 #e2c674 #f4e4a8')
INKL    = ramp('#241a12 #3e2e20 #5a4632')                                            # ink on paper
SEA     = ramp('#2e4844 #45665e #608478 #86a89a')
ROUTE   = ramp('#7a1e1e #b03030 #d85a4a #f4a070')
AMANITA = ramp('#4a1010 #7e1c1c #b0302a #d8503e')                                    # the toggle's red cap

ALL = [INK] + LEATHER + MOSS + PARCH + BRONZE + INKL + SEA + ROUTE + AMANITA + WAX + VEIN + BONE + CAV

def write_gpl(path):
    seen, rows = set(), []
    for c in ALL:
        if c in seen: continue
        seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    with open(path, 'w') as f:
        f.write('GIMP Palette\nName: hud\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
