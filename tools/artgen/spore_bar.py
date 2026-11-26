"""The spore gauge (HUD, ui/SporeBar.js): a glass ampule lying in a weathered bronze cradle, the spore fluid inside.

usage: spore_bar.py <outdir>
  spore_bar_frame.png  160x24  the cradle: two bronze end caps with rivets, the rails along the tube, the empty glass
  spore_bar_fill.png   140x36  the fluid, 3 rows of 140x12: moss-mint (plenty), ochre (running low), rust (nearly gone);
                               SporeBar crops it to the level
  spore_bar_glass.png  160x24  the glass's shine, drawn over the fluid
The palettes follow the G/D medallion's (gd_medallion.py: weathered bronze, moss, rust) and the menu's jungle skin.
"""
import os
import random
import sys
from PIL import Image

from common import ramp

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
W, H = 160, 24
TX0, TX1, TY0, TY1 = 10, 150, 6, 18           # the tube's inside (fluid area): 140 x 12
BRONZE = ramp('#140e0a #21180f #302315 #40301c #523e24 #66502e #7a6239 #8e7546 #a48a58 #bea36e')
GLASS = ramp('#070a08 #0a0f0c #0e1511 #121b16 #17221c')
FLUIDS = [
    ramp('#16301f #1f4229 #2a5636 #386c44 #4a8456 #5e9c6a #78b682 #9ad0a0'),   # moss-mint
    ramp('#2a2010 #3a2c14 #4c3a1a #604a22 #76602c #8c7638 #a28c48 #b8a25c'),   # ochre
    ramp('#1a0e08 #2a1810 #3c2216 #54301e #6a3c22 #7e4628 #96562e #b06a3a'),   # rust
]
INK = (8, 6, 4, 255)
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def q(rmp, v, x, y):
    """a continuous ramp position -> a ramp colour, with a 4x4 ordered dither between neighbours"""
    v = max(0.0, min(len(rmp) - 1.0, v))
    i = int(v)
    f = v - i
    if i < len(rmp) - 1 and f * 16 > BAYER[y % 4][x % 4] + 0.5:
        i += 1
    return rmp[i] + (255,)


def frame():
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    px = img.load()
    # the tube: dark glass, a little lighter at the top (the far wall catches some light)
    for y in range(TY0 - 1, TY1 + 1):
        for x in range(TX0 - 1, TX1 + 1):
            t = (y - (TY0 - 1)) / (TY1 - TY0 + 1)
            px[x, y] = q(GLASS, 3.2 - 3.0 * t, x, y)
    # the rails: a thin bronze strip above and below the tube, an ink line toward the glass
    for x in range(TX0 - 2, TX1 + 2):
        for y, v in ((TY0 - 3, 6.2), (TY0 - 2, 3.4), (TY1 + 1, 4.6), (TY1 + 2, 2.0)):
            px[x, y] = q(BRONZE, v - 0.6 * ((x * 7) % 5 == 0), x, y)     # a few worn notches
        px[x, TY0 - 1] = INK
        px[x, TY1] = INK if x in (TX0 - 1, TX1) else px[x, TY1]
    # the caps: bronze, bevelled (light from the top left), a band, two rivets
    for cx0 in (0, W - 12):
        for y in range(1, H - 1):
            for x in range(cx0, cx0 + 12):
                u, v = (x - cx0) / 11, (y - 1) / (H - 3)
                shade = 7.4 - 4.2 * v - 1.6 * u + (0.9 if (x - cx0) in (0, 1) else 0) - (1.2 if (x - cx0) in (10, 11) else 0)
                if (x - cx0) in (3, 8):
                    shade -= 1.6                                                   # the band's grooves
                px[x, y] = q(BRONZE, shade, x, y)
        for x in range(cx0, cx0 + 12):                                             # outline top/bottom
            px[x, 0] = INK; px[x, H - 1] = INK
        for y in range(H):
            px[cx0, y] = INK if y in (0, H - 1) else px[cx0, y]
        for ry in (5, H - 6):                                                       # rivets
            rx = cx0 + 5
            px[rx, ry] = BRONZE[9] + (255,); px[rx + 1, ry] = BRONZE[7] + (255,)
            px[rx, ry + 1] = BRONZE[6] + (255,); px[rx + 1, ry + 1] = BRONZE[2] + (255,)
        # the outer ends: rounded off
        for (x, y) in ((cx0, 1), (cx0, H - 2)) if cx0 == 0 else ((cx0 + 11, 1), (cx0 + 11, H - 2)):
            px[x, y] = INK
        edge = cx0 if cx0 == 0 else cx0 + 11
        for y in range(1, H - 1):
            px[edge, y] = INK
    return img


def fill():
    img = Image.new('RGBA', (TX1 - TX0, (TY1 - TY0) * 3), (0, 0, 0, 0))
    px = img.load()
    fw, fh = TX1 - TX0, TY1 - TY0
    for row, rmp in enumerate(FLUIDS):
        rnd = random.Random(521 + row)
        for y in range(fh):
            for x in range(fw):
                t = y / (fh - 1)
                # brighter in the middle of the tube (the glass is round), darker at the bottom
                v = 5.4 - 3.2 * abs(t - 0.38) * 1.6 - 1.0 * t
                v += 0.6 * ((x * 13 + y * 7) % 11 == 0)                             # a faint grain
                px[x, row * fh + y] = q(rmp, v, x, y)
        # spores suspended in it: little light specks, a few pairs
        for _ in range(26):
            x, y = rnd.randrange(1, fw - 1), rnd.randrange(2, fh - 2)
            px[x, row * fh + y] = rmp[-1] + (255,)
            if rnd.random() < 0.35:
                px[x + 1, row * fh + y] = rmp[-2] + (255,)
    return img


def glass():
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    px = img.load()
    for x in range(TX0, TX1):
        px[x, TY0] = (230, 240, 225, 70)                                            # the top shine
        if TX0 + 6 <= x < TX0 + 40:
            px[x, TY0 + 1] = (240, 248, 236, 110)                                   # a brighter streak at the left
        if x % 9 not in (0, 1):
            px[x, TY1 - 1] = (200, 220, 200, 28)                                    # the bottom's faint reflection
    for y in range(TY0, TY1):                                                       # the glass meets the caps
        px[TX0, y] = (0, 0, 0, 90); px[TX1 - 1, y] = (0, 0, 0, 90)
    return img


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    frame().save(os.path.join(OUT, 'spore_bar_frame.png'))
    fill().save(os.path.join(OUT, 'spore_bar_fill.png'))
    glass().save(os.path.join(OUT, 'spore_bar_glass.png'))
    print('ok', OUT)
