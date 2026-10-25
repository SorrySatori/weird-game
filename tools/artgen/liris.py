"""Captain Liris of the skyship Verdigrace (SkyshipBoardScene), redrawn with the character renderer (rig.py, the Edgar
quality bar) after her old placeholder (captain_liris.png): a weathered sky captain in a deep teal hood, a brass
monocle with an amber lens over her left eye on a strap round the head, auburn strands escaping the hood, a brick-red
scarf, a long open brown coat over an olive tunic with a belt (a brass spyglass hooked at her hip), dark trousers,
tall boots. 128x160 frames, facing the viewer, soles on y 156; an 8-frame idle on a windy deck:
  0 rest  1 inhale  2 blink  3 the monocle's lens ring clicks round (a glint)
  4-5 a gust: the scarf ends and the coat's hem stream right  6 she touches the monocle  7 settling back
python3 liris.py <outdir>  ->  liris.png (8-frame sheet) + liris/<n>.png + liris.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK
from rig import Rig, Mat
from feral_toast import ik
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
R = ramp
HOOD  = R('#0c1d1c #132b29 #1b3a37 #244b47 #2e5d57 #3a7068 #48837a #5a9689')
COAT  = R('#170d08 #24150d #331e12 #432818 #54331e #663f26 #794c30 #8c5b3b')
TUNIC = R('#161a0c #222812 #2f3718 #3d4720 #4c5828 #5d6a32 #6f7c3e')
TROU  = R('#100c0a #1a1410 #251c16 #31251d #3d2f25')
BOOT  = R('#0e0907 #1a110c #271a12 #352319 #442d20 #553a2a')
SKIN  = R('#4a2c1c #66402a #84583b #a0704d #b88862 #cca07a #dcb894 #ead0b0')
HAIR  = R('#1a0c08 #2c140c #421d10 #5a2a16 #713a1e')
SCARF = R('#240c0a #3a1410 #521c16 #6a261c #823226 #9a4232')
GOLD  = R('#2e200a #4e3812 #74561c #9a7628 #bc963a #d8b658 #eed488')
LENS  = [(150, 92, 20), (214, 150, 40), (244, 196, 80), (255, 232, 150), (255, 250, 220)]
EYEW  = (226, 214, 196)
M = {'hood': Mat(HOOD, 'wool', 0.22), 'coat': Mat(COAT, 'wool', 0.2), 'tunic': Mat(TUNIC, 'fabric', 0.22),
     'trou': Mat(TROU, 'fabric', 0.18), 'boot': Mat(BOOT, 'leather', 0.2, 0.6), 'skin': Mat(SKIN, 'plain', 0.32, 0.15),
     'hair': Mat(HAIR, 'fur', 0.2), 'scarf': Mat(SCARF, 'wool', 0.22), 'gold': Mat(GOLD, 'metal', 0.24, 0.8),
     'belt': Mat(BOOT, 'leather', 0.22, 0.4)}

POSE = [dict(b=0, blink=0, click=0, gust=0, touch=0), dict(b=1, blink=0, click=0, gust=0, touch=0),
        dict(b=0, blink=1, click=0, gust=0, touch=0), dict(b=0, blink=0, click=1, gust=0, touch=0),
        dict(b=1, blink=0, click=0, gust=1, touch=0), dict(b=1, blink=0, click=0, gust=2, touch=0),
        dict(b=0, blink=0, click=0, gust=1, touch=2), dict(b=0, blink=0, click=0, gust=0, touch=1)]


def liris(P):
    r = Rig(128, 160)
    b, g = P['b'], P['gust']
    wind = [0, 2, 4][g]
    # legs and boots: a captain's stance, feet a little apart
    for sx in (-1, 1):
        hip = (64 + sx * 5, 96)
        foot = (64 + sx * 7, 150)
        knee = ik(hip, foot, 27, 28, 'right')
        r.tube(hip, knee, 5.6, 4.6, M['trou'], group='leg%d' % sx, folds=lambda u, sd: -0.2 if abs(sd) < 0.12 and u > 0.2 else 0)
        r.tube(knee, (foot[0], foot[1] - 4), 4.6, 4.2, M['trou'], group='leg%d' % sx)
        r.tube((knee[0] + sx * 0.3, knee[1] + 3), (foot[0], foot[1] - 1), 5.2, 4.8, M['boot'], group='boot%d' % sx,
               folds=lambda u, sd: 0.2 if u < 0.07 else (-0.15 if abs(sd) > 0.7 else 0))                 # tall boots, a turned cuff
        r.ellipsoid(foot[0] + sx * 1.5, 153.0, 7.6, 3.4, M['boot'], group='sole%d' % sx)
    # the tunic and belt, the spyglass hooked at the hip
    r.poly([(54, 54 - b), (74, 54 - b), (75, 98), (53, 98)], M['tunic'], group='tunic',
           vfun=lambda x, y: -0.16 if x in (63, 64) and y > 60 else 0)                               # the placket
    for y in (64 - b, 72 - b, 80): r.fixed(64, y, GOLD[4]); r.fixed(64, y + 1, GOLD[1])            # buttons
    r.poly([(52, 86), (76, 86), (76, 91), (52, 91)], M['belt'], group='belt')
    for (x, y, c) in ((62, 87, GOLD[5]), (63, 87, GOLD[3]), (62, 88, GOLD[3]), (65, 87, GOLD[4]), (65, 88, GOLD[2]),
                      (62, 89, GOLD[2]), (63, 89, GOLD[1]), (64, 89, GOLD[3])):
        r.fixed(x, y, c)                                                                           # the buckle
    r.tube((53, 91), (50, 112), 2.2, 1.9, M['gold'], group='spyglass')                             # the spyglass at the belt
    r.tube((52, 99), (52, 101), 2.6, 2.6, M['gold'], lift=0.15, group='spyglass')
    r.tube((50, 111), (50, 113), 2.4, 2.4, M['gold'], lift=0.1, group='spyglass')
    # the coat: two long panels from the shoulders, open over the tunic, the hem catching the wind
    hemL = [(42 + wind * 0.5, 124), (56 + wind * 0.8, 127)]
    hemR = [(73 + wind, 127), (87 + wind * 1.6, 123 - wind * 0.5)]
    r.poly([(50, 56 - b), (58, 52 - b), (59, 60 - b), (58, 90), (hemL[1][0], hemL[1][1]), (hemL[0][0], hemL[0][1]), (45, 92), (47, 72)],
           M['coat'], group='coatL', vfun=lambda x, y: -0.2 if y > 96 and (x * 3 + y) % 17 == 0 else 0)
    r.poly([(70, 52 - b), (78, 56 - b), (81, 72), (83, 92), (hemR[1][0], hemR[1][1]), (hemR[0][0], hemR[0][1]), (70, 90), (69, 60 - b)],
           M['coat'], group='coatR', vfun=lambda x, y: -0.2 if y > 96 and (x * 3 - y) % 17 == 0 else 0)
    r.poly([(58, 52 - b), (61, 58 - b), (59, 78), (55, 74), (54, 58 - b)], M['coat'], lift=0.14, group='lapelL')
    r.poly([(70, 52 - b), (67, 58 - b), (69, 78), (73, 74), (74, 58 - b)], M['coat'], lift=0.14, group='lapelR')
    for x in range(int(hemL[0][0]), int(hemL[1][0])): r.darken(x, int(hemL[0][1] + (x - hemL[0][0]) / (hemL[1][0] - hemL[0][0]) * 3) - 1, -0.12)
    # arms: the left (viewer's left) hangs by the spyglass; the right hangs or rises to the monocle
    shL, shR = (50, 60 - b), (78, 60 - b)
    handL = (46, 100)
    elL = ((shL[0] + handL[0]) / 2 - 2.0, (shL[1] + handL[1]) / 2)
    r.tube(shL, elL, 4.4, 3.8, M['coat'], lift=0.06, group='armL', folds=lambda u, sd: -0.22 if u > 0.86 and sd > 0 else 0)
    r.tube(elL, handL, 3.8, 3.4, M['coat'], lift=0.06, group='armL')
    r.tube((handL[0] + 0.2, handL[1] - 2.5), handL, 3.8, 3.8, M['coat'], lift=0.2, group='armL')        # the turned-back cuff
    r.ellipsoid(handL[0], handL[1] + 2.5, 2.8, 3.2, M['skin'], group='handL')
    for k in range(3): r.tube((handL[0] - 1.6 + k * 1.4, handL[1] + 4), (handL[0] - 2.0 + k * 1.5, handL[1] + 6.5), 0.9, 0.8, M['skin'], group='handL')
    seam(r, 'armL', 0.25)
    touch = P['touch']
    handR = [(82, 100), (79, 74), (72, 41 - b)][touch]
    elR = ik(shR, handR, 21, 20, lambda e: e[1] * 1.4 + e[0] * 0.5) if touch else ((shR[0] + handR[0]) / 2 + 2.0, (shR[1] + handR[1]) / 2)   # the elbow hangs
    # the scarf: wrapped round the neck, two ends; one flying in the wind
    hx, hy = 64, 30 - b
    r.ellipsoid(hx, 52 - b, 10.5, 4.6, M['scarf'], group='scarf', vfun=lambda x, y, u, w: -0.18 if (x - y) % 4 == 0 else 0)
    ends = [(60, 54 - b), (59 + wind * 1.2, 65 - b - wind * 0.6), (60 + wind * 2.4, 74 - b - wind * 1.6)]
    for (a, c) in zip(ends, ends[1:]):
        r.tube(a, c, 3.4, 2.8, M['scarf'], group='scarfEnd')
    fr = ends[-1]
    for k in range(4): r.fixed(fr[0] - 2 + k * 1.3, fr[1] + 3 + (k % 2), SCARF[1])                 # the fringe
    r.tube((68, 54 - b), (70 + wind * 0.6, 63 - b), 3.0, 2.6, M['scarf'], group='scarfEnd2')
    # the head: a deep teal hood, the face inside, auburn strands, the monocle on its strap
    r.ellipsoid(hx, hy + 15, 13.5, 6.2, M['hood'], group='cowl')
    r.ellipsoid(hx, hy, 15.0, 17.0, M['hood'], lift=0.04, group='hood',
                vfun=lambda x, y, u, w: -0.18 if abs(math.atan2(w, u) * 3 % 1 - 0.5) < 0.05 and w < 0.3 else 0)
    r.ellipsoid(hx, hy + 2, 11.2, 13.4, M['hood'], lift=-0.62, group='hoodin')
    # the face: clean hand-pixelled bands (no dither) so the features read at 1x
    L = (-0.45, -0.7, 0.55); ln = math.sqrt(sum(c * c for c in L)); L = tuple(c / ln for c in L)
    fcx, fcy, frx, fry = hx, hy + 4, 9.0, 10.8
    for y in range(int(fcy - fry) - 1, int(fcy + fry) + 2):
        for x in range(int(fcx - frx) - 1, int(fcx + frx) + 2):
            u, w = (x + 0.5 - fcx) / frx, (y + 0.5 - fcy) / fry
            d = u * u + w * w
            if d > 1: continue
            n = (u, w, math.sqrt(1 - d))
            v = 0.25 + 0.75 * max(0.0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2])
            if w < -0.45: v -= 0.28                                                                # the hood's shadow on the brow
            r.fixed(x, y, SKIN[max(1, min(6, 1 + int(v * 5.2)))])
    r.poly([(hx - 10, hy - 8), (hx - 1, hy - 11), (hx + 9, hy - 8), (hx + 10, hy - 3), (hx + 4, hy - 7), (hx - 3, hy - 6), (hx - 8, hy - 2), (hx - 10, hy + 2)],
           M['hair'], group='hair')                                                                # parted hair under the hood's brim
    for (x0, y0, ln, sx) in ((hx - 10, hy + 1, 13, -1), (hx + 10, hy + 0, 12, 1)):                    # long strands down by the cheeks
        for k in range(ln): r.fixed(x0 + (sx if k > 6 else 0), y0 + k, HAIR[2 + (k % 2)]); r.fixed(x0 - sx + (sx if k > 6 else 0), y0 + k, HAIR[1])
    ey = hy + 3
    # her right eye (viewer's left): open, steady; a weathered brow
    ex = hx - 4
    if P['blink']:
        for x in range(ex - 2, ex + 2): r.fixed(x, ey + 1, SKIN[1])
    else:
        for x in range(ex - 2, ex + 2): r.fixed(x, ey, EYEW if x != ex else (40, 52, 46))
        r.fixed(ex - 1, ey, (40, 52, 46)); r.fixed(ex, ey - 1, SKIN[2]); r.fixed(ex - 1, ey + 1, SKIN[2])
        for x in range(ex - 2, ex + 2): r.fixed(x, ey - 1, SKIN[1])                                 # the upper lid
    for x in range(ex - 3, ex + 2): r.fixed(x, ey - 3 + (1 if x == ex - 3 else 0), HAIR[1])        # the brow
    for x in range(hx + 2, hx + 7): r.fixed(x, ey - 5 + (1 if x == hx + 6 else 0), HAIR[1])        # the other brow, over the ring
    # the monocle over her left eye: a brass ring, an amber lens, a strap round the head
    mx, my = hx + 4, ey
    for x in range(int(hx - 8), int(hx + 9)):
        yy = int(my - 4 - 0.18 * (x - mx))
        if abs(x - mx) > 3: r.fixed(x, yy, BOOT[1])
    for a in range(24):
        t = a / 24 * 2 * math.pi
        r.fixed(mx + math.cos(t) * 3.3, my + math.sin(t) * 3.3, GOLD[5] if math.sin(t) < -0.3 else (GOLD[3] if math.cos(t) < 0.3 else GOLD[1]))
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if dx * dx + dy * dy <= 5:
                c = LENS[1] if dy > 0 else LENS[2]
                if dx == -1 and dy == -1: c = LENS[4] if P['click'] else LENS[3]
                r.fixed(mx + dx, my + dy, c)
    if P['click']: r.fixed(mx + 1, my + 1, LENS[3]); r.fixed(mx + 3, my - 3, GOLD[6]); r.fixed(mx + 4, my - 4, (255, 250, 220))
    else: r.fixed(mx + 3, my + 2, GOLD[4])                                                         # the little adjustment knob
    # nose, mouth, a scar on the cheek
    for y in range(hy + 5, hy + 9): r.fixed(hx + 1, y, SKIN[3])                                     # the nose's shaded side
    r.fixed(hx - 1, hy + 7, SKIN[6]); r.fixed(hx, hy + 9, SKIN[2]); r.fixed(hx + 1, hy + 9, SKIN[1])   # its tip, a nostril
    for dx in range(-2, 3): r.fixed(hx + dx, hy + 12, (92, 46, 38) if abs(dx) < 2 else SKIN[2])      # the mouth, set firm
    r.fixed(hx - 1, hy + 13, SKIN[5]); r.fixed(hx, hy + 13, SKIN[5])                                 # the lower lip catches light
    r.fixed(hx - 6, hy + 8, SKIN[3]); r.fixed(hx - 5, hy + 9, SKIN[3]); r.fixed(hx - 6, hy + 9, SKIN[6])   # an old scar
    for k in range(14):                                                                            # the hood's rim
        a = -2.9 + k * 0.21
        r.fixed(hx + math.cos(a) * 10.4, hy + 2 + math.sin(a) * 12.6, HOOD[6 if k % 4 else 5])
    # the right arm last: in front of the scarf/face when it rises to the monocle
    r.tube(shR, elR, 5.4, 4.8, M['coat'], group='armR', folds=lambda u, sd: -0.22 if u > 0.86 and sd < 0 else 0)
    r.tube(elR, handR, 4.8, 4.0, M['coat'], group='armR')
    if touch == 2:
        r.ellipsoid(handR[0] + 2, handR[1], 3.0, 3.4, M['skin'], group='handR')
        r.tube((handR[0], handR[1] - 2), (mx + 2, my + 1), 1.0, 0.9, M['skin'], group='handR')      # a finger on the ring
    else:
        r.ellipsoid(handR[0], handR[1] + 2.5, 3.4, 3.8, M['skin'], group='handR')
        if not touch:
            for k in range(3): r.tube((handR[0] - 1.6 + k * 1.6, handR[1] + 4), (handR[0] - 1.2 + k * 1.7, handR[1] + 7), 1.0, 0.9, M['skin'], group='handR')
    seam(r, 'armR', 0.25); seam(r, 'scarfEnd', 0.15); seam(r, 'lapelL', 0.1); seam(r, 'lapelR', 0.1)
    return r.render()


if __name__ == '__main__':
    os.makedirs(f'{OUT}/liris', exist_ok=True)
    frames = [liris(p) for p in POSE]
    sheet = Image.new('RGBA', (128 * len(frames), 160), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        im.save(f'{OUT}/liris/{i}.png'); sheet.paste(im, (i * 128, 0))
    sheet.save(f'{OUT}/liris.png')
    ALL = [INK] + HOOD + COAT + TUNIC + TROU + BOOT + SKIN + HAIR + SCARF + GOLD + LENS + [EYEW]
    seen, rows = set(), []
    for c in ALL:
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/liris.gpl', 'w').write('GIMP Palette\nName: liris\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT)
