"""Palette for the menus (main menu, the ESC menu, save / load / language panels). Aseprite: menu.gpl.
Shares the bronze / moss / vein / bone / wax ramps with the HUD buttons and the symbiont rosary."""
from common import ramp, INK
from pal_symb import VEIN, BONE, CAV, WAX, HUSK, CORD, col
from pal_hud import BRONZE, MOSS, PARCH, SEA, AMANITA, LEATHER

ENAMEL = ramp('#050806 #080d0a #0c1610 #111d15 #16251b #1c3022')                    # the plaques' dark green enamel
IRON   = ramp('#121214 #1c1c1f #29282b #383639 #4a4746 #5f5b57 #77726a #938c80')    # gears
RUST   = ramp('#2a1208 #4a200e #6e3416 #8e4a20 #b0662e')
LEAF   = ramp('#0b170b #142713 #1f3a1b #2e5227 #426b33 #5c8742 #7aa356')            # vines, fern
CAP    = ramp('#1e130a #352210 #4f3418 #6e4a22 #8e632e #ad7f3e #c99c58 #e0bc7c')    # mycena / bracket caps
MADDER = ramp('#1c0e0b #33170f #4c2116 #652c1d #7c3a26 #904a31 #a35e40')            # the fly-agaric, weathered
GLOW   = ramp('#143a22 #1f5a32 #3f8f5a #7fff8e #c8ffd0 #f0fff2')                    # bioluminescence (= VEIN + MYC)

ALL = [INK] + ENAMEL + BRONZE + SEA + IRON + RUST + LEAF + MOSS + CAP + MADDER + HUSK + CORD + BONE + GLOW + AMANITA + WAX + \
      PARCH + LEATHER + CAV + VEIN

def write_gpl(path):
    seen, rows = set(), []
    for c in ALL:
        if c in seen: continue
        seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    with open(path, 'w') as f:
        f.write('GIMP Palette\nName: menu\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
