"""The Senior Clerk of the Shed 521 registration yard (ShedRegistrationScene), redrawn with the character renderer
(rig.py) after the old sprite (clerk2.png), but no longer a frog and no longer crowned: a tall, stern reptilian
bureaucrat -- a narrow skull under fine scales, a comb of spines webbed with a rust membrane running up the brow and
over the crown, sunken amber eyes with slit pupils under heavy lids and scaly brows, a flat snout with nostril pits,
hollow cheeks, a lipless down-turned mouth, blotches down the temples, a lean neck with pale banded scutes, clawed
fingers; a charcoal suit, a pink shirt, a purple tie, brown shoes. The near hand holds a rubber
stamp at his chest, the far hand a thick ledger at his side. 128x192 frames, facing the viewer, soles on y 189;
an 8-frame idle:
  0 rest          1 inhale (the crest lifts)        2 blink
  3 a disdainful sniff (nostrils flare, eyes narrow)  4 the forked tongue flicks out  5 the eyes slide left
  6-7 he lifts the ledger and knocks it square against his leg
python3 senior_clerk.py <outdir>  ->  senior_clerk.png (8-frame sheet) + senior_clerk/<n>.png + senior_clerk.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK, h32
from rig import Rig, Mat
from feral_toast import ik
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
R = ramp
SKIN   = R('#101a15 #18261e #223429 #2d4435 #3a5642 #4a6a51 #5d8063 #78997a')
BELLY  = R('#2c3a26 #3e4f33 #536643 #6b7e55 #84966a')
CREST  = R('#24100a #3a1a0e #542814 #6e381c #8a4a26')
SPINE  = R('#1e2a1c #34442c #4e5f3e #6b7a52 #8a9668 #a8b07e')
CLAW   = R('#4a4232 #7a6e52 #a89a78 #c8bc98')
TONGUE = R('#3a1422 #6a2a3c #8c3c52')
EYE    = R('#4a360a #7a5a12 #a8801e #d0a630 #eccb5a')
GOLD   = R('#2e200a #4e3812 #74561c #9a7628 #bc963a #d8b658 #eed488')
SUIT   = R('#121216 #1a1a20 #24242b #2f2f37 #3b3b44 #494852 #585761 #6a6972')
SHIRT  = R('#3a2230 #523042 #6c4056 #86526a #a0687e #b98296')
TIE    = R('#160e22 #22152f #2e1d40 #3c2852 #4c3464 #5e4278')
SHOE   = R('#1a0f0a #2a1a10 #3c2618 #503322 #63412c')
LEDGER = R('#1c0c0a #2c1410 #3e1d16 #52281e #663428')
PAGES  = R('#6e6a5a #8a8572 #a6a08a #c0baa2')
WOOD   = R('#2a1a0e #432a16 #5e3c20 #7a502c #946638')
RUBBER = R('#1a0808 #2c0e0e #42161a #5a1e22')
M = {'skin': Mat(SKIN, 'skin', 0.26, 0.35), 'belly': Mat(BELLY, 'skin', 0.26, 0.2), 'crest': Mat(CREST, 'skin', 0.3, 0.2),
     'spine': Mat(SPINE, 'plain', 0.3, 0.3), 'suit': Mat(SUIT, 'wool', 0.2),
     'lapel': Mat(SUIT, 'wool', 0.16), 'shirt': Mat(SHIRT, 'fabric', 0.24), 'tie': Mat(TIE, 'fabric', 0.24, 0.25),
     'shoe': Mat(SHOE, 'leather', 0.2, 0.7), 'ledger': Mat(LEDGER, 'leather', 0.2, 0.3),
     'pages': Mat(PAGES, 'plain', 0.4), 'wood': Mat(WOOD, 'wood', 0.24, 0.2), 'rubber': Mat(RUBBER, 'plain', 0.2)}

POSE = [dict(b=0, blink=0, sniff=0, look=0, tap=0, crest=0), dict(b=1, blink=0, sniff=0, look=0, tap=0, crest=1),
        dict(b=0, blink=1, sniff=0, look=0, tap=0, crest=0), dict(b=1, blink=0, sniff=1, look=0, tap=0, crest=0),
        dict(b=1, blink=0, sniff=2, look=0, tap=0, crest=0), dict(b=0, blink=0, sniff=0, look=1, tap=0, crest=0),
        dict(b=0, blink=0, sniff=0, look=1, tap=1, crest=0), dict(b=0, blink=0, sniff=0, look=0, tap=2, crest=0)]

def senior_clerk(P):
    r = Rig(128, 192)
    b = P['b']
    # legs: a broad, planted stance
    for sx in (-1, 1):
        hip = (64 + sx * 7, 124)
        foot = (64 + sx * 9, 183)
        knee = ik(hip, foot, 30, 30, 'right')
        r.tube(hip, knee, 7.2, 6.0, M['suit'], group='leg%d' % sx, folds=lambda u, sd: -0.25 if abs(sd) < 0.12 and u > 0.15 else 0)
        r.tube(knee, foot, 6.0, 5.2, M['suit'], group='leg%d' % sx, folds=lambda u, sd: -0.22 if abs(sd) < 0.12 else 0)
        r.ellipsoid(foot[0] + sx * 1.5, 185.5, 8.5, 3.6, M['shoe'], group='shoe%d' % sx)
    # the shirt in the jacket's V, the collar wings, the tie
    r.poly([(55, 58 - b), (73, 58 - b), (67, 98), (61, 98)], M['shirt'], group='shirt')
    r.poly([(62, 59 - b), (66, 59 - b), (65.5, 64 - b), (62.5, 64 - b)], M['tie'], group='knot')
    r.poly([(62.5, 64 - b), (65.5, 64 - b), (67, 90), (64, 94), (61, 90)], M['tie'], group='tie',
           vfun=lambda x, y: 0.22 if (x + y) % 6 == 0 else 0)                                         # a fine diagonal weave
    r.poly([(56, 55 - b), (63, 59 - b), (58, 64 - b)], M['shirt'], lift=0.1, group='collarL')
    r.poly([(72, 55 - b), (65, 59 - b), (70, 64 - b)], M['shirt'], lift=0.1, group='collarR')
    # the jacket: two panels that close at one button and open towards the hem
    r.poly([(41, 64 - b), (54, 57 - b), (58, 62 - b), (64, 97), (63, 112), (59, 132), (43, 130), (45, 104), (40, 80)], M['suit'],
           group='jacketL', vfun=lambda x, y: -0.22 if y > 112 and (x * 3 + y) % 23 == 0 else 0)
    r.poly([(74, 57 - b), (87, 64 - b), (88, 80), (83, 104), (85, 130), (69, 132), (65, 112), (64, 97), (70, 62 - b)], M['suit'],
           group='jacketR', vfun=lambda x, y: -0.22 if y > 112 and (x * 3 - y) % 23 == 0 else 0)
    r.poly([(54, 57 - b), (58, 62 - b), (64, 95), (61, 91), (49, 67 - b)], M['lapel'], lift=-0.06, group='lapelL')
    r.poly([(74, 57 - b), (70, 62 - b), (64, 95), (67, 91), (79, 67 - b)], M['lapel'], lift=-0.06, group='lapelR')
    for (x, y) in ((64, 97), (64.5, 108)):                                                         # buttons
        r.fixed(x - 1, y, SUIT[1]); r.fixed(x, y, SUIT[6]); r.fixed(x, y + 1, SUIT[1])
    for x in range(47, 56): r.fixed(x, 77 + (x > 51), SUIT[0])                                    # breast pocket welt
    for x0 in (46, 72):                                                                            # hip pocket flaps
        for x in range(x0, x0 + 11):
            r.fixed(x, 113, SUIT[0]); r.darken(x, 114, 0.12); r.darken(x, 115, 0.08)
    for (x, y, c) in ((51, 70 - b, GOLD[5]), (52, 70 - b, GOLD[3]), (51, 71 - b, GOLD[2]), (52, 71 - b, GOLD[4])):
        r.fixed(x, y, c)                                                                           # a rank pin on the lapel
    # the far (left) arm hangs; its hand carries the ledger at his side and knocks it square
    tap = P['tap']
    lift = [0, 4, -1][tap]
    shL = (44, 67 - b)
    handL = (40, 121 - lift)
    el = ((shL[0] + handL[0]) / 2 - 1, (shL[1] + handL[1]) / 2)                                   # the forearm comes forward, no splay
    r.tube(shL, el, 5.6, 5.0, M['suit'], group='armL', folds=lambda u, sd: -0.25 if u > 0.85 and sd > 0 else 0)
    r.tube(el, handL, 5.0, 4.4, M['suit'], group='armL')
    r.tube((handL[0] + 0.3, handL[1] - 3), (handL[0], handL[1] - 1), 3.6, 3.4, M['shirt'], group='cuffL')
    lx, ly = 30, 118 - lift
    r.poly([(lx + 14, ly - 1), (lx + 17, ly + 1), (lx + 18, ly + 32), (lx + 15, ly + 33)], M['pages'], round_=0.4, group='pages',
           vfun=lambda x, y: -0.18 if y % 2 else 0)                                                # the page edges
    r.poly([(lx, ly), (lx + 14, ly - 1), (lx + 15, ly + 33), (lx + 1, ly + 34)], M['ledger'], round_=0.5, group='ledger',
           vfun=lambda x, y: (0.2 if y in (ly + 6, ly + 27) else 0) - (0.15 if x == lx + 2 else 0))   # spine bands
    for (cx, cy) in ((lx + 1, ly + 1), (lx + 14, ly), (lx + 2, ly + 33), (lx + 15, ly + 32)):        # brass corners
        r.fixed(cx, cy, GOLD[4]); r.fixed(cx + (1 if cx < lx + 8 else -1), cy, GOLD[2])
    for x in range(lx + 5, lx + 11):                                                               # the label
        for y in range(ly + 14, ly + 18): r.fixed(x, y, PAGES[3] if (x + y) % 3 else PAGES[1])
    r.ellipsoid(handL[0] - 1, handL[1] + 1, 3.6, 3.4, M['skin'], group='handL')                     # gripping the top edge
    for k in range(3):
        r.tube((handL[0] - 3 + k * 2.2, handL[1] + 1), (handL[0] - 3.5 + k * 2.3, handL[1] + 5), 1.1, 0.9, M['skin'], group='fingL')
        r.fixed(handL[0] - 3.5 + k * 2.3, handL[1] + 6, CLAW[2]); r.fixed(handL[0] - 3.5 + k * 2.3, handL[1] + 7, CLAW[0])   # claws
    seam(r, 'armL', 0.25)
    # the neck: lean, two tendons running into the collar, pale banded scutes down its front
    hx, hy = 64, 37 - b
    r.tube((hx, hy + 10), (hx, 58 - b), 4.4, 5.4, M['skin'], lift=-0.1, group='neck',
           folds=lambda u, sd: -0.16 if abs(abs(sd) - 0.55) < 0.1 else 0)
    r.poly([(hx - 2.6, hy + 12), (hx + 2.6, hy + 12), (hx + 3.4, 58 - b), (hx - 3.4, 58 - b)], M['belly'], lift=-0.08,
           group='neck', vfun=lambda x, y: -0.16 if (y - hy) % 2 == 0 else 0)
    # the head: a narrow skull under a fine pattern of scales, a long jaw tapering to a blunt chin
    def scales(x, y, k):                                                                           # each scale lit top-left, shaded bottom-right
        ox = (y // k) % 2 * (k // 2)
        cx, cy = (x + ox) // k, y // k
        fx, fy = (x + ox) % k, y % k
        return (h32(cx, cy, 11) % 5 - 2) * 0.025 + (-0.09 if fx == k - 1 or fy == k - 1 else 0.04 if fx == 0 and fy == 0 else 0)
    r.ellipsoid(hx, hy - 5, 13.0, 13.5, M['skin'], group='head', flat=0.9,
                vfun=lambda x, y, u, w: scales(x, y, 4) + (-0.1 if abs(u) > 0.78 else 0))
    def jaw(x, y):
        return y < hy + 2 or (y < hy + 16 and abs(x + 0.5 - hx) < 12 - (y - (hy + 2)) * 0.45)
    def cheeks(x, y, u, w):
        dx, dy = abs(x + 0.5 - hx), y - hy
        v = scales(x, y, 3)
        if 6 <= dx <= 10 and 5 <= dy <= 10: v -= 0.12                                             # hollow under the cheekbone
        if 5 <= dx <= 10 and 2 <= dy <= 3: v += 0.07                                              # the cheekbone's edge
        return v
    r.ellipsoid(hx, hy + 4, 11.8, 12.0, M['skin'], group='head', vfun=cheeks, clip=jaw)
    for x in range(hx - 7, hx + 8):                                                                # the jaw's shadow on the neck
        for y in range(hy + 13, hy + 20):
            if not jaw(x, y) and jaw(x, y - 1): r.darken(x, y, 0.22); r.darken(x, y + 1, 0.12); break
    for k in range(6):                                                                             # darker blotches down each temple
        for sx in (-1, 1):
            x, y = hx + sx * (11.0 - k * 0.6), hy - 9 + k * 3.2
            r.darken(x, y, 0.16); r.darken(x - sx, y, 0.1)
            if k < 4: r.darken(x, y + 1, 0.1)
    # the crest: a comb of bony spines along the skull's midline, webbed with a rust membrane -- low scutes up the
    # forehead, rising into a ragged fan over the crown
    up = 1 if P['crest'] else 0
    spines = [(-6.0, 5), (-3.2, 10), (-0.2, 14), (2.9, 11), (5.8, 6)]                               # (x offset, height over the crown)
    base = hy - 16
    tips = [(hx + dx, base - h - up) for (dx, h) in spines]
    edge = [(hx - 3.5, base + 4)]
    for i, t in enumerate(tips):
        edge.append((t[0], t[1] + 1.5))
        if i < len(tips) - 1: edge.append(((t[0] + tips[i + 1][0]) / 2, max(t[1], tips[i + 1][1]) + 5))
    edge.append((hx + 3.5, base + 4))
    r.poly(edge, M['crest'], round_=0.6, group='crest', vfun=lambda x, y: -0.06 if (x + y) % 4 == 0 else 0)
    for (tx, ty) in tips:                                                                          # the spines that hold it up
        bx = hx + (tx - hx) * 0.6
        r.stroke([(bx + (tx - bx) * t / 16, base + 2 + (ty - base - 2) * t / 16) for t in range(17)], 0.9, M['spine'], v=0.42,
                 group='crest')
        r.fixed(tx, ty, SPINE[5]); r.fixed(tx, ty + 1, SPINE[4])                                     # pale, horny tips
    for k, (y, w, h) in enumerate(((hy - 7, 1.4, 1.6), (hy - 10, 1.7, 2.0), (hy - 13, 2.0, 2.4))):  # scutes running up the brow
        r.poly([(hx - w, y + 1), (hx + w, y + 1), (hx + 0.4, y - h)], M['spine'], round_=0.7, group='scute%d' % k)
        for dx in range(-1, 2): r.darken(hx + dx, y + 2, 0.14)
    sniff = P['sniff']
    look = -1.4 if P['look'] else -0.3
    r.ellipsoid(hx, hy - 4.5 + (0.5 if sniff else 0), 11.5, 2.6, M['skin'], lift=0.1, group='brow')          # the brow
    for i, sx in enumerate((-1, 1)):
        ex, ey = hx + sx * 5.5, hy - 1
        for k in range(3):                                                                         # a row of raised scales over the eye
            r.ellipsoid(ex + sx * (k - 1) * 2.6, ey - 3.6 + abs(k - 1) * 0.4 + (0.5 if sniff else 0), 1.5, 1.2, M['skin'],
                        lift=0.14, group='brow')
        r.ellipsoid(ex, ey, 4.0, 2.5, Mat(EYE, 'plain', 0.4, 0.6), group='eye%d' % i)
        px = ex + look
        for y in range(int(ey - 2), int(ey + 3)): r.fixed(px, y, (12, 10, 8))                      # the slit pupil
        r.fixed(ex - 2 + look * 0.4, ey - 1, (255, 246, 200))
        drop = 1 if sniff else 0                                                                   # narrowed in disdain
        edge = (lambda x, ex=ex, ey=ey, s=-sx * 0.28: ey + 3 if P['blink'] else ey - 1.4 + drop + s * (x + 0.5 - ex))
        r.ellipsoid(ex, ey - 1, 4.6, 3.0, M['skin'], lift=0.08, group='lid%d' % i, clip=lambda x, y, edge=edge: y < edge(x))
        for x in range(int(ex - 4), int(ex + 4)):
            r.fixed(x, min(int(edge(x)), ey + 2), SKIN[0])                                          # the lid's edge
        for x in range(int(ex - 3), int(ex + 3)): r.darken(x, ey + 3, 0.12)                       # the lower lid
    r.tube((hx, hy + 1), (hx, hy + 5), 1.6, 2.4, M['skin'], lift=0.04, group='snout')               # a flat snout
    for x in (hx - 2, hx + 1):                                                                     # nostril pits, flared on a sniff
        r.fixed(x, hy + 5, SKIN[0])
        if sniff: r.fixed(x - 1 if x < hx else x + 1, hy + 5, SKIN[1])
    for dx in range(-6, 7):                                                                        # a lipless, down-turned mouth line
        y = hy + 10 + (dx / 6) ** 2 * 2.0
        r.fixed(hx + dx, y, SKIN[0])
        if abs(dx) < 5: r.darken(hx + dx, y + 1, -0.08)
    if sniff == 2:                                                                                 # the forked tongue flicks out
        for y in range(hy + 11, hy + 14): r.fixed(hx, y, TONGUE[1 if y < hy + 13 else 2])
        r.fixed(hx - 1, hy + 14, TONGUE[2]); r.fixed(hx + 1, hy + 14, TONGUE[2]); r.fixed(hx - 1, hy + 15, TONGUE[1]); r.fixed(hx + 1, hy + 15, TONGUE[1])
    # the near (right) arm: the stamp held upright against the chest
    shR = (86, 67 - b)
    handR = (73, 90)
    el = ik(shR, handR, 20, 19, lambda e: e[1] * 1.5 + e[0] * 0.5)                                  # the elbow hangs at his side
    r.tube(shR, el, 5.6, 5.0, M['suit'], group='armR', folds=lambda u, sd: -0.25 if u > 0.85 and sd < 0 else 0)
    r.tube(el, handR, 5.0, 4.4, M['suit'], group='armR')
    r.tube((el[0] + (handR[0] - el[0]) * 0.82, el[1] + (handR[1] - el[1]) * 0.82), handR, 3.8, 3.6, M['shirt'], group='cuffR')
    sx = handR[0] - 3
    r.ellipsoid(sx, handR[1] - 9, 2.4, 2.2, M['wood'], group='stamp')                               # the knob
    r.tube((sx, handR[1] - 8), (sx, handR[1] + 4), 1.3, 1.5, M['wood'], group='stamp')
    r.poly([(sx - 5, handR[1] + 4), (sx + 5, handR[1] + 4), (sx + 5, handR[1] + 7), (sx - 5, handR[1] + 7)], M['wood'], group='stamp')
    r.poly([(sx - 4.5, handR[1] + 7), (sx + 4.5, handR[1] + 7), (sx + 4.5, handR[1] + 9), (sx - 4.5, handR[1] + 9)], M['rubber'], group='stamp')
    r.ellipsoid(handR[0] - 2, handR[1], 4.0, 3.6, M['skin'], group='handR')                          # the fist round the handle
    for k in range(3):
        r.tube((handR[0] - 1, handR[1] - 2 + k * 2.0), (handR[0] - 5.5, handR[1] - 2.2 + k * 2.1), 1.1, 1.0, M['skin'], group='fingR')
        r.fixed(handR[0] - 6.5, handR[1] - 2.2 + k * 2.1, CLAW[3]); r.fixed(handR[0] - 7.5, handR[1] - 2.2 + k * 2.1, CLAW[1])
    seam(r, 'armR', 0.28)
    return r.render()

if __name__ == '__main__':
    os.makedirs(f'{OUT}/senior_clerk', exist_ok=True)
    frames = [senior_clerk(p) for p in POSE]
    sheet = Image.new('RGBA', (128 * len(frames), 192), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        im.save(f'{OUT}/senior_clerk/{i}.png'); sheet.paste(im, (i * 128, 0))
    sheet.save(f'{OUT}/senior_clerk.png')
    ALL = [INK] + SKIN + BELLY + CREST + SPINE + CLAW + TONGUE + EYE + GOLD + SUIT + SHIRT + TIE + SHOE + LEDGER + PAGES + WOOD + RUBBER
    seen, rows = set(), []
    for c in ALL:
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/senior_clerk.gpl', 'w').write('GIMP Palette\nName: senior_clerk\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT)
