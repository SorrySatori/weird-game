"""A local on Burning Bear Street stuffing a bear for the Bear Burning Festival (BurningBearStreetScene, an ambient
figure -- utils/AmbientNpc.js): a hooded citizen (shedkit.applicant_img, the same people as the Shed's) beside a slumped,
stitched bear effigy -- the same brown teddy-like bears that hang over the street -- sitting on a crate with its belly
seam open and straw sticking out. A basket of things to be rid of (bottles, letters) stands at the citizen's feet.
The loop: he looks at the bear, reaches into the basket, lifts a bottle, shoves it into the bear (the belly bulges), pats
the bear, wipes his brow.

python3 bearstuffer.py <outdir>  ->  bear_stuffer.png (sheet) + bear_stuffer/<n>.png + bear_stuffer/durations.txt
                                     + bearstuffer.gpl; prints the frame size and the figure's height (top)"""
import sys, os, math
from PIL import Image
from rig import Rig, Mat
from shedkit import applicant_img, SLATE
from pal_day import WOOD, ramp

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
FW, FH = 140, 128                         # frame; the citizen's feet and the crate stand on the bottom row
HPX = 112                                 # the citizen's height on the pavement (a step behind the priest's 128)

FUR = ramp('#22150c #352214 #4b311d #624128 #7a5434 #936842 #ab7e52')        # the effigies' brown plush
PATCH = ramp('#4a3826 #64503a #806a4e #9c8566 #b6a07e #ccb894')               # muzzle, belly patch, paw pads
STRAW = ramp('#4a3a12 #6e5a1e #96802e #b89e44 #d4bc62')
GLASS = ramp('#0e2214 #1a3a22 #2a5a34 #3e7e48 #5aa064 #8cc890')
STITCH = (28, 18, 12)

def bear_img(bulge=0.0, straw=1.0):
    """the effigy slumped on a crate, 100x100: head lolling left, belly seam open (straw, bulging when stuffed)"""
    r = Rig(100, 100)
    M_f, M_p, M_w = Mat(FUR, 'fur', 0.22), Mat(PATCH, 'fur', 0.25), Mat(WOOD, 'wood', 0.2)
    r.poly([(18, 74), (82, 74), (82, 99), (18, 99)], M_w, round_=0.2, group='crate')                     # the crate
    r.stroke([(18, 86), (82, 86)], 1.0, color=WOOD[1], group='crate_slat')
    for (a, b) in (((36, 70), (28, 84)), ((64, 70), (74, 84))):                                         # legs, feet
        r.tube(a, b, 8.5, 8.0, M_f, group='leg')
    for fx in (27, 75):
        r.ellipsoid(fx, 87, 8.0, 6.0, M_f, group='foot')
        r.ellipsoid(fx + 1, 88, 4.6, 3.6, M_p, lift=0.05, group='pad')
    bx = 50
    r.ellipsoid(bx, 57, 23 * (1 + bulge), 21 * (1 + bulge * 0.6), M_f, group='body')                   # the body
    r.ellipsoid(bx + 1, 62, 9.5 * (1 + bulge), 10.5 * (1 + bulge * 0.6), Mat(PATCH[:4], 'fur', 0.2), lift=-0.06, group='belly')
    for (a, b) in (((29, 45), (21, 70)), ((71, 45), (80, 68))):                                         # limp arms
        r.tube(a, b, 7.0, 6.5, M_f, group='arm')
    r.ellipsoid(44, 25, 17, 15, M_f, rot=-0.25, group='head')                                          # head lolls left
    for (ex, ey) in ((31, 12), (55, 9)):
        r.ellipsoid(ex, ey, 5.6, 5.4, M_f, group='ear')
        r.ellipsoid(ex + 0.5, ey + 0.6, 2.8, 2.6, M_p, lift=-0.05, group='ear_in')
    r.ellipsoid(41, 31, 7.4, 5.2, M_p, rot=-0.25, group='muzzle')
    im = r.render()
    px = im.load()
    def dot(x, y, c):
        if 0 <= x < 100 and 0 <= y < 100: px[x, y] = c + (255,)
    for (x, y) in ((40, 28), (41, 28), (42, 28), (41, 29)): dot(x, y, (24, 14, 10))                    # nose
    for (ex, ey) in ((35, 21), (49, 19)):                                                              # button eyes
        for dx in (0, 1):
            for dy in (0, 1): dot(ex + dx, ey + dy, (16, 14, 14))
        dot(ex, ey, (120, 110, 100))
    for (x0, y0, x1, y1) in ((52, 23, 58, 29), (58, 23, 52, 29)):                                      # a stitched X patch
        n = 7
        for i in range(n): dot(round(x0 + (x1 - x0) * i / (n - 1)), round(y0 + (y1 - y0) * i / (n - 1)), STITCH)
    for y in range(36, 79, 3): dot(bx + (1 if (y // 3) % 2 else 0), y, STITCH)                         # the seam down the front
    # the open belly: a dark slit, straw (and the neck of something) sticking out; more of it when stuffed full
    sx, sy, sh = bx + 1, 60, int(9 + bulge * 30)
    for y in range(sy - sh, sy + sh + 1):
        w = int(1.6 * math.sqrt(max(0.0, 1 - ((y - sy) / sh) ** 2)))
        for x in range(sx - w, sx + w + 1): dot(x, y, (14, 9, 6))
    for i in range(int(7 + straw * 6)):
        ang = -1.9 + i * 0.38; ln = 3 + (i * 7) % 5 + int(bulge * 25)
        y0 = sy - sh + 3 + (i * 5) % (2 * sh - 4)
        for t in range(ln):
            x = sx + (1 if i % 2 else -1) * (2 + t * abs(math.cos(ang))); y = y0 - t * 0.5 * math.sin(ang)
            dot(round(x), round(y), STRAW[2 + (t + i) % 3])
    return im

def basket_img():
    """a wicker basket of things to be rid of: bottles, a bundle of letters"""
    r = Rig(40, 32)
    M_b = Mat(ramp('#2a1c0e #3e2a16 #573c20 #72502c #8c663a #a47e4c'), 'wool', 0.22)
    for (x, top, c) in ((13, 2, GLASS), (22, 5, GLASS), (29, 9, ramp('#3a1414 #5a2020 #7e3030 #a24646 #c06464'))):
        r.tube((x, 22), (x, top + 6), 2.6, 2.4, Mat(c, 'plain', 0.2, 0.5), group='bottle%d' % x)
        r.tube((x, top + 6), (x, top), 1.2, 1.1, Mat(c, 'plain', 0.2, 0.5), group='neck%d' % x)
    r.poly([(6, 12), (34, 10), (37, 15), (3, 17)], Mat(ramp('#6e6450 #8c826a #aaa088 #c8bea4 #e0d8c0'), 'plain', 0.3), group='letters')
    r.poly([(2, 16), (38, 16), (35, 31), (5, 31)], M_b, round_=0.4, group='basket',
           vfun=lambda x, y: -0.18 if (int(x) + int(y) * 2) % 4 == 0 else 0)
    r.stroke([(3, 16), (37, 16)], 1.2, color=(58, 40, 22), group='rim')
    return r.render()

def bottle(px, x, y):
    """the bottle in his hand (neck up), 4x9"""
    for dy in range(9):
        for dx in range(4 if dy > 2 else 2):
            xx = x + dx + (1 if dy <= 2 else 0); yy = y + dy
            c = GLASS[1] if dx == 0 else GLASS[3] if dx == 1 else GLASS[2]
            if dy == 0: c = (90, 60, 34)                                   # the cork
            if 0 <= xx < FW and 0 <= yy < FH: px[xx, yy] = c + (255,)

# frames: (citizen pose, bear bulge, bottle in hand (hand index) or None, hold ms)
POSES = [
    (dict(), 0.0, None, 1400),                                                          # looks at his bear
    (dict(hands=((12, 82), (30, 72)), bob=4.0, lean=-3.0), 0.0, None, 600),             # into the basket
    (dict(hands=((26, 52), (44, 60)), bob=1.0, lean=-1.0), 0.0, 0, 500),                # a bottle out
    (dict(hands=((50, 64), (62, 61)), bob=1.0, lean=2.0), 0.0, 1, 450),                 # into the belly with it
    (dict(hands=((52, 67), (64, 64)), bob=2.0, lean=3.5), 0.10, None, 650),             # shove -- the belly bulges
    (dict(hands=((50, 61), (64, 55)), bob=1.0, lean=2.0), 0.06, None, 500),             # a pat
    (dict(hands=((30, 62), (44, 22)), bob=0.5), 0.04, None, 1000),                      # wipes his brow
    (dict(), 0.02, None, 900),
]
SEED = 611                                                                              # a hooded, olive-robed citizen

if __name__ == '__main__':
    os.makedirs(f'{OUT}/bear_stuffer', exist_ok=True)
    basket = basket_img()
    sheet = Image.new('RGBA', (FW * len(POSES), FH), (0, 0, 0, 0))
    pal = set(); tops = []
    for i, (pose, bulge, held, hold) in enumerate(POSES):
        fr = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
        fr.alpha_composite(bear_img(bulge, 1.0 + bulge * 6), (30, FH - 100))
        man = applicant_img(SEED, HPX, kind='hood', view='front', robe=SLATE, papers=False, **pose)
        mb = man.getbbox()[3]
        ox, oy = 4, FH - mb
        fr.alpha_composite(man, (ox, oy))
        fr.alpha_composite(basket, (0, FH - 32))
        if held is not None:                                                            # the bottle in that hand
            k = HPX / 100.0
            hx, hy = pose['hands'][held]
            bottle(fr.load(), int(ox + hx * k + 3 - 1), int(oy + hy * k + 3 - 6))
        fr.save(f'{OUT}/bear_stuffer/{i}.png'); sheet.paste(fr, (i * FW, 0))
        pal.update(c[:3] for _, c in fr.getcolors(1 << 16) if c[3])
        tops.append(FH - man.getbbox()[1] - oy)
    sheet.save(f'{OUT}/bear_stuffer.png')
    open(f'{OUT}/bear_stuffer/durations.txt', 'w').write(' '.join(str(p[3]) for p in POSES) + '\n')
    rows = ['%3d %3d %3d\t#%02x%02x%02x' % (c + c) for c in sorted(pal)]
    open(f'{OUT}/bearstuffer.gpl', 'w').write('GIMP Palette\nName: bearstuffer\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print(f'bear_stuffer {FW}x{FH} x{len(POSES)}  top {max(tops)}  holds {[p[3] for p in POSES]}')
