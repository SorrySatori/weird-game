"""Dr. Elphi Quarn, the dream-game designer of ARB Ambra (ScraperAmbraScene, floor 177-Quiet), redrawn with the character
renderer (rig.py, the Edgar quality bar) -- replacing the box-filtered AI portrait (ref/DrElphi.png, derived by
ortolan_elphi.py until now; it stays only as the reference for who she is).
Kept from the old art: curly auburn hair to the shoulders, round teal goggle-glasses, a white lab coat (open, notched
lapels, pens in the breast pocket) over a teal knitted top with a patterned band and knit cuffs at the wrists, a belt with
a small device pouch, teal trousers, dark boots; the green holographic glyph she projects (a ring with a core, a curling
tail, sparks) on her right side, a handheld device in the other hand.
The pose: 3/4 turned to the viewer's left (toward the player, who comes in from the left), her weight on the far leg
(that hip pushed out and up, that shoulder low), the near knee eased forward. The far arm hangs close, the device loose
in the hand by the thigh; the near elbow hangs at her side and the forearm comes forward, palm up -- the glyph floats
over it and lights her hand, sleeve, coat and hair mint-green against the warm key light from the top left.
128x160 frames, soles on y 156 (same sheet format as before: key `drElphiIdle`, 8 frames, the same frame meanings):
  0 rest  1 breath (the hologram bobs)  2 the goggles glint (she blinks behind them)  3 the hologram pulses
  4 it drifts up, sparks shift  5 she glances at the glyph, a ripple runs down its tail and its light spreads a little
  (the old "coat specks twinkle" slot)  6 she taps the device in her hand (thumb down, the screen flares, the glyph's core
  answers)  7 a strand of hair stirs (and the glyph's tail sways)
The scene plays them out of order (0 0 1 1 0 0 3 3 4 4 0 0 2 ...), so every frame is an excursion from frame 0; only
0 -> 3 -> 4 -> 0 turns the glyph's bead and inner ring, one 120-degree step per frame (a full cycle back to rest).
python3 elphi.py <outdir>  ->  elphi.png (8-frame sheet) + elphi/<n>.png + elphi.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK, h32
import rig
from rig import Rig, Mat
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
W, H = 128, 160
R = ramp
COAT  = R('#1f2321 #2c312e #3b413d #4c534e #5f6760 #737b73 #889087 #9da49a #b1b6ab #c3c6bb #d2d3c7 #dedfd3')
TOP   = R('#0b1716 #11211f #182d2a #1f3a36 #274743 #30554f #3b635c #47716a')
KNIT  = R('#3d6a60 #5a877a #7aa294')                                                   # the pattern band's light yarn
TROU  = R('#0b1313 #111c1b #182624 #1f302e #273b38 #304642 #3a514c')
BOOT  = R('#100b09 #1b1310 #281c16 #36261d #453126 #563e30 #684c3b')
BELT  = R('#120d0b #1e1612 #2c211a #3b2c22 #4b392c #5c4737')
SKIN  = R('#3a2119 #563226 #744536 #915b46 #ab7258 #c18a6c #d3a282 #e1b998 #ebcdb0')
HAIR  = R('#1b0d0a #2a120d #3a1a12 #4b2217 #5c2c1c #6c3722 #7c432a #8b5033 #985d3d #a46c4a')
GUN   = R('#111517 #1c2224 #283033 #364144 #475457 #5b6a6c #73858a')
LENS  = R('#173c3a #215450 #2f6e68 #458c83 #69ab9f #9ccdbf #d4efe6')
BRASS = R('#2e220e #4c3a17 #6e5622 #92752f #b39443 #d0b462')
PEN   = R('#0e1c1b #1d3735 #2e5653 #46766f')
HOLO  = [(22, 66, 50), (36, 116, 86), (62, 176, 126), (108, 230, 168), (176, 255, 212), (236, 255, 246)]
MINT  = (120, 240, 184)
EYEW  = (214, 206, 190)
IRIS  = (70, 104, 80)                                                                    # green-grey eyes
PUPIL = (22, 18, 16)
LIP   = [(98, 44, 40), (132, 66, 58), (160, 92, 80)]
WARM_INK = (34, 22, 18)

rig.TEX['coat'] = lambda x, y: ((rig.nF(x * 1.7, y * 1.7) - 0.5) * 0.08 + (rig.nM(x * 1.1 + 20, y * 1.1) - 0.5) * 0.13
                                + (rig.nL(x * 0.6 + 50, y * 0.6) - 0.5) * 0.08
                                + (0.024 if (x + 2 * y) % 3 == 0 else -0.01))            # cotton twill, mottled with wear
rig.TEX['curl'] = lambda x, y: (rig.nF(x * 1.9, y * 1.9) - 0.5) * 0.12
rig.TEX['knit'] = lambda x, y: (rig.nF(x * 2.0, y * 2.0) - 0.5) * 0.10 + (0.05 if (x + (y // 2)) % 2 else -0.04)

def mat(rmp, tex, amb, spec=0.0, out=WARM_INK): return Mat(rmp, tex, amb, spec, outline=out)
M = {'coat': mat(COAT, 'coat', 0.30, 0.04, (32, 30, 26)), 'top': mat(TOP, 'knit', 0.22, 0.0, (10, 16, 15)),
     'trou': mat(TROU, 'fabric', 0.2, 0.0, (10, 14, 13)), 'boot': mat(BOOT, 'leather', 0.2, 0.6),
     'skin': mat(SKIN, 'skin', 0.30, 0.12), 'hand': mat(SKIN, 'skin', 0.28, 0.14), 'hair': mat(HAIR, 'curl', 0.2, 0.22, (24, 10, 7)),
     'gun': mat(GUN, 'metal', 0.22, 0.9, (12, 14, 15)), 'belt': mat(BELT, 'leather', 0.22, 0.4), 'pen': mat(PEN, 'plain', 0.24, 0.8),
     'brass': mat(BRASS, 'metal', 0.26, 0.8)}

POSE = [dict(), dict(b=1, hb=-1), dict(glint=1, blink=1), dict(pulse=1), dict(hb=-2, drift=1), dict(look=1, ripple=1),
        dict(tap=1), dict(stir=1)]
GLYPH = (95.0, 57.0)                                   # the glyph's centre at rest


def mix(a, b, t): return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def spline(pts, step=0.8):
    """Catmull-Rom through the points, resampled about every `step` px"""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        n = max(2, int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / step))
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


# ------------------------------------------------------------------------------------------------------------- the coat
def panel_far(U):
    """the far (viewer's left) coat panel, narrow (she is turned away from it): it bulges over the pushed-out hip"""
    return [(43.4, U(57.0)), (47.0, U(51.6)), (51.0, U(49.0)), (54.5, U(50.5)), (53.5, U(61)), (52.2, U(73)), (51.4, 96), (50.8, 116), (50.4, 132.6),
            (47.0, 133.4), (43.6, 132.8), (40.0, 132.6), (37.0, 131.4), (37.6, 118), (38.4, 104), (39.4, 95), (41.4, U(84)), (42.8, U(68))]


def panel_near(U):
    """the near (viewer's right) panel, broad; it drapes over the eased knee and flares at the hem"""
    return [(64.0, U(48.5)), (71.0, U(49.5)), (76.0, U(51.6)), (79.6, U(54.6)), (80.8, U(61)), (81.0, U(76)), (81.6, 92), (83.2, 108), (85.0, 122),
            (86.8, 134.2), (82.6, 135.6), (78.0, 135.6), (72.4, 136.8), (67.2, 136.3), (66.4, 118), (65.4, 100), (64.8, 88), (64.0, U(75)), (63.0, U(58))]


def coat_v(far, P):
    """folds as light: creases (a dark line + a lit ridge beside it), the knee pushing the cloth, dust on the hem, stains"""
    folds = ([(45.0, 97, -0.07, 0.4), (48.6, 110, -0.01, 0.26), (42.0, 114, -0.05, 0.28)] if far else
             [(71.5, 97, 0.04, 0.38), (76.0, 104, 0.09, 0.34), (69.0, 121, 0.0, 0.24), (80.5, 114, 0.12, 0.26), (73.5, 126, 0.06, 0.2)])
    drags = ([] if far else [((76.5, 64.0), (71.0, 77.0), 0.26), ((79.0, 71.0), (74.0, 84.0), 0.2), ((80.0, 82.0), (77.5, 90.0), 0.14)])
    def v(x, y):
        out = 0.0
        for ((ax, ay), (bx, by), depth) in drags:                                      # the arm brought forward drags the side
            dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
            t = max(0.0, min(1.0, ((x + 0.5 - ax) * dx + (y + 0.5 - ay) * dy) / L2))
            ox, oy = x + 0.5 - (ax + dx * t), y + 0.5 - (ay + dy * t)
            d = (ox * dy - oy * dx) / math.sqrt(L2)
            if abs(d) < 0.55 and 0 < t < 1: out -= depth * math.sin(t * math.pi)
            elif -1.6 < d <= -0.55 and 0 < t < 1: out += depth * 0.4 * math.sin(t * math.pi)
        for (fx, fy, slant, depth) in folds:
            if y < fy: continue
            px = fx + (y - fy) * slant
            d = x + 0.5 - px
            fade = min(1.0, (y - fy) / 6.0)
            if -0.5 <= d < 0.5: out -= depth * fade
            elif 0.5 <= d < 1.5: out += depth * 0.45 * fade                         # the ridge catches the light
        if not far:
            dk = ((x + 0.5 - 72.0) / 6.5) ** 2 + ((y + 0.5 - 120) / 7.0) ** 2         # the eased knee pushes the cloth
            if dk < 1: out += 0.16 * (1 - dk) * (1 if y < 121 else -0.4)
            if x > 79 and y < 100: out -= 0.1                                          # under the hanging arm
        else:
            if x < 42 and y > 96: out -= 0.05
            if x < 47 and y < 101: out -= 0.2 if x > 43 else 0.12                      # in the shadow of the hanging arm
        if y >= 128: out -= (y - 128) * 0.022                                          # dust creeping up the hem
        if y >= 132 + (0 if far else 2): out += 0.12                                    # the hem's fold-over edge
        for (sx_, sy, sr, k) in ((75.5, 113, 1.6, 0.16), (46.5, 124, 1.3, 0.12), (70.5, 84, 1.1, 0.1)):   # old stains
            if (x + 0.5 - sx_) ** 2 + ((y - sy) * 1.3) ** 2 < sr * sr: out -= k
        out -= max(0.0, y - 70) * 0.0016                                               # less light low down
        return out
    return v


def legs(r, P):
    """the weight on the far leg (straight, the foot under her neck); the near one eased, knee forward, foot turned out"""
    far = ((51.6, 93), (54.6, 123), (57.6, 149))
    near = ((66.0, 95), (70.2, 122), (71.0, 150))
    for ((hip, knee, ank), g, lift) in ((far, 'legF', -0.14), (near, 'legN', 0.0)):
        r.tube(hip, knee, 6.0, 4.6, M['trou'], lift=lift, group=g, folds=lambda u, sd: -0.2 if abs(sd + 0.2) < 0.12 and u > 0.25 else 0)
        r.tube(knee, ank, 4.6, 3.6, M['trou'], lift=lift, group=g,
               folds=lambda u, sd: (-0.22 if u > 0.8 and abs(sd) < 0.5 and int(u * 20) % 3 == 0 else 0) + (0.1 if u < 0.08 else 0))
    # ankle boots: the far one points left (she is turned that way), the near one out toward us
    r.tube((57.4, 143), (57.0, 150), 4.2, 4.0, M['boot'], lift=-0.12, group='bootF')
    r.ellipsoid(54.0, 151.4, 6.2, 2.8, M['boot'], lift=-0.12, group='bootF')
    r.ellipsoid(55.6, 149.4, 4.0, 2.0, M['boot'], lift=-0.02, group='bootF')
    r.tube((71.0, 144), (71.6, 152), 4.4, 4.2, M['boot'], group='bootN')
    r.ellipsoid(73.6, 153.4, 6.0, 3.0, M['boot'], group='bootN', rot=0.3)
    r.ellipsoid(72.2, 151.4, 4.2, 2.2, M['boot'], lift=0.08, group='bootN')
    for (x, y) in ((58, 144), (57, 146), (71, 145), (70, 147), (72, 147)): r.darken(x, y, 0.25)   # laces
    r.fixed(48, 151, BOOT[4]); r.fixed(49, 151, BOOT[5]); r.fixed(77, 153, BOOT[5]); r.fixed(78, 154, BOOT[4])   # toe caps
    for x in range(48, 60): r.fixed(x, 154, BOOT[1])                                   # the soles
    for x in range(68, 80): r.fixed(x, 156, BOOT[1])
    r.fixed(80, 155, BOOT[2])


def torso(r, U, P):
    """the teal knitted top from the roll collar to the belt; the patterned band across the chest"""
    pts = [(46.0, U(56)), (53.0, U(50)), (64.0, U(49.5)), (75.0, U(53)), (77.0, U(64)), (75.0, U(78)), (75.5, 90), (60.0, 91.5),
           (50.5, 90), (50.0, U(78)), (46.5, U(64))]
    r.poly(pts, M['top'], round_=0.8, group='top', vfun=lambda x, y: 0.1 if x < 56 else 0)
    r.ellipsoid(57.5, U(63.5), 5.0, 4.2, M['top'], lift=0.05, group='top', flat=0.8)       # the bust under the knit
    r.ellipsoid(67.0, U(64.0), 6.0, 4.4, M['top'], lift=0.0, group='top', flat=0.8)
    # the pattern band: a row of little diamonds between two rows of dots (fair-isle), shaded with the body
    y0 = U(67)
    for x in range(46, 78):
        if (x + 1) % 2 == 0:
            for y in (y0, y0 + 4):
                e = r.buf.get((x, y))
                if e and r.groups[e[2]] == 'top': r.fixed(x, y, KNIT[1] if x < 63 else KNIT[0])
        k = (x - 46) % 4
        for (dy, on) in ((1, k == 1), (2, k in (0, 2)), (3, k == 1)):
            e = r.buf.get((x, y0 + dy))
            if on and e and r.groups[e[2]] == 'top': r.fixed(x, y0 + dy, KNIT[2] if x < 61 else KNIT[1])
    # the belt rides high on the weight-bearing (far) hip; a small device pouch at the front (three status dots)
    r.poly([(50.0, 86.0), (75.5, 88.0), (75.6, 92.0), (50.1, 90.0)], M['belt'], round_=0.8, group='belt')
    for (x, y, c) in ((57, 87, BRASS[4]), (58, 87, BRASS[3]), (57, 88, BRASS[2]), (58, 88, BRASS[1]), (56, 88, BRASS[3])):
        r.fixed(x, y, c)
    r.poly([(61.0, 88.4), (68.6, 88.8), (68.9, 96.8), (61.2, 96.6)], M['gun'], round_=0.6, group='pouch')
    r.poly([(60.8, 88.0), (68.8, 88.4), (68.9, 91.0), (60.9, 90.6)], M['gun'], lift=0.15, round_=0.4, group='pouchflap')
    seam(r, 'pouchflap', 0.25)
    for (x, c) in ((63, HOLO[3]), (65, HOLO[2]), (67, (180, 120, 60))): r.fixed(x, 94, c)


def coat(r, U, P):
    r.ellipsoid(59.5, U(48.0), 11.0, 3.8, M['coat'], lift=-0.12, group='collar')         # the collar round the back of the neck
    r.poly(panel_far(U), M['coat'], round_=0.7, group='coatF', vfun=coat_v(True, P))
    r.poly(panel_near(U), M['coat'], round_=0.75, group='coatN', vfun=coat_v(False, P))
    seam(r, 'coatF', 0.18); seam(r, 'coatN', 0.18)
    # lapels: the far one narrow (turned away), the near one broad with its notch
    lf = [(50.5, U(48.5)), (54.5, U(49.0)), (56.2, U(51.5)), (54.2, U(64)), (52.4, U(73)), (51.6, U(63)), (49.6, U(54))]
    r.poly(lf, M['coat'], lift=0.2, round_=0.5, group='lapelF')
    ln_ = [(63.0, U(47.5)), (70.0, U(49.0)), (75.0, U(54.5)), (72.0, U(57.0)), (74.0, U(59.5)), (64.4, U(75.5)), (62.6, U(60)),
           (62.2, U(51))]
    r.poly(ln_, M['coat'], lift=0.1, round_=0.5, group='lapelN')
    seam(r, 'lapelF', 0.24); seam(r, 'lapelN', 0.26)
    # the breast pocket on the near panel, two pens clipped in it
    for x in range(68, 77): r.darken(x, U(65), 0.32); r.darken(x, U(66), -0.1)
    for y in range(U(66), U(72)): r.darken(76.6, y, 0.16)
    for x in range(68, 77): r.darken(x, U(72), 0.1)
    for (px, top, cap, clip) in ((69, 59, PEN, (196, 204, 198)), (72, 60, [(30, 26, 24), (44, 38, 34), (62, 54, 48), (84, 74, 64)], BRASS[5])):
        for y in range(U(top), U(65)):
            c = cap[3] if y == U(top) else cap[2] if y < U(top) + 2 else cap[1]
            r.fixed(px, y, c); r.fixed(px + 1, y, cap[0] if y > U(top) else cap[2])
        r.fixed(px + 1, U(top + 1), clip); r.fixed(px + 1, U(top + 2), mix(clip, (0, 0, 0), 0.35))
    # hip pockets: a welt line and its shadow
    for x in range(69, 80): r.darken(x, 101 - (x - 69) * 0.1, 0.26); r.darken(x, 102 - (x - 69) * 0.1, -0.08)
    for x in range(40, 50): r.darken(x, 99 + (x - 40) * 0.08, 0.22)
    # buttons down the near edge (the coat is open; the far edge shows the buttonholes)
    for y in (79, 93, 107):
        yy = y if y > 90 else U(y)
        r.fixed(67, yy, COAT[10]); r.fixed(68, yy, COAT[7]); r.fixed(67, yy + 1, COAT[6])
        r.darken(50.5, yy, 0.18); r.darken(49.5, yy, 0.18)


# --------------------------------------------------------------------------------------------------------------- arms
def sleeve(r, sh, el, wr, g, ra=5.0, lift=0.0):
    """a loose lab-coat sleeve: a crease in the elbow, bunching above the cuff, a turned-back cuff"""
    r.tube(sh, el, ra, ra - 0.6, M['coat'], lift=lift, group=g,
           folds=lambda u, sd: (-0.26 if u > 0.82 and abs(sd) < 0.55 else 0) + (0.07 if u < 0.25 and sd < -0.2 else 0)
           + (-0.16 if 0.45 < u < 0.5 and sd > 0 else 0))
    r.tube(el, wr, ra - 0.6, ra - 1.1, M['coat'], lift=lift, group=g,
           folds=lambda u, sd: -0.22 if (0.5 < u < 0.56 or 0.72 < u < 0.77) and abs(sd) < 0.7 else 0)
    dx, dy = wr[0] - el[0], wr[1] - el[1]; L = math.hypot(dx, dy) or 1
    r.tube((wr[0] - dx / L * 2.4, wr[1] - dy / L * 2.4), wr, ra - 0.8, ra - 0.8, M['coat'], lift=lift + 0.14, group=g + 'cuff')
    seam(r, g, 0.22); seam(r, g + 'cuff', 0.18)
    return dx / L, dy / L


def far_arm(r, U, P):
    """hangs close; the device loose in the hand by the thigh, the thumb on its face"""
    sh, el, wr = (45.6, U(59.5)), (41.0, U(81)), (43.2, 101)
    ux, uy = sleeve(r, sh, el, wr, 'armF', ra=4.6, lift=-0.04)
    seam(r, 'armF', 0.16)
    r.tube((wr[0] + ux * 0.5, wr[1] + uy * 0.5), (wr[0] + ux * 2.2, wr[1] + uy * 2.2), 2.9, 2.7, M['top'], lift=0.1, group='cuffF')
    seam(r, 'cuffF', 0.16)
    # the device: a slim dark slab held upright by its outer edge; its screen to us, the thumb resting on it
    tap = P.get('tap', 0)
    r.poly([(45.0, 100.8), (50.4, 100.0), (51.6, 112.4), (46.2, 113.4)], M['gun'], round_=0.5, tilt=-0.15, group='device')
    seam(r, 'device', 0.3)
    for y in range(102, 108):                                                                # the screen, a glyph line on it
        for x in range(47 + (y - 102) // 5, 51 + (y - 102) // 5):
            c = HOLO[3] if tap else HOLO[2]
            if y == 102: c = HOLO[4] if tap else HOLO[3]
            if y == 104 and x in (48, 49): c = HOLO[1]
            if y == 106 and x == 49: c = HOLO[1]
            r.fixed(x, y, c)
    r.fixed(48, 110, GUN[6] if not tap else HOLO[4]); r.fixed(50, 110, GUN[5])                # two keys under it
    r.fixed(48, 111, GUN[2]); r.fixed(50, 111, GUN[2])
    # the hand round its outer edge: the back of the hand and the knuckles to us, the thumb across the front
    r.ellipsoid(44.6, 105.4, 3.0, 4.0, M['hand'], lift=0.02, group='handF')
    for y in (104, 106, 108): r.darken(42, y, 0.22)                                         # the creases between the fingers
    r.darken(43, 109, 0.12)
    r.tube((46.6, 103.2), (48.2 + tap * 0.4, 104.8 + tap * 1.2), 1.2, 1.0, M['hand'], lift=0.1, group='thumbF')
    seam(r, 'thumbF', 0.2)


def near_arm(r, U, P):
    """the elbow hangs at her side, the forearm comes forward, the palm up under the glyph"""
    sh, el, wr = (77.0, U(56.6)), (81.4, U(78)), (88.6, U(79.4))
    ux, uy = sleeve(r, sh, el, wr, 'armN', ra=5.2)
    r.tube((wr[0] + ux * 0.4, wr[1] + uy * 0.4), (wr[0] + ux * 2.4, wr[1] + uy * 2.4), 3.0, 2.7, M['top'], lift=0.08, group='cuffN')
    seam(r, 'cuffN', 0.18)
    hx, hy = 93.0, U(79.4)
    r.ellipsoid(hx, hy, 3.6, 2.5, M['hand'], lift=0.1, group='palm', flat=0.7)               # the palm, cupped, seen from above
    for k in range(4):                                                                       # fingers toward us, tips curled up
        a = (hx + 1.6 + k * 0.2, hy + 0.2 + k * 0.85)
        b = (hx + 4.8 - k * 0.35, hy - 0.4 + k * 1.05)
        r.tube(a, b, 1.0, 0.9, M['hand'], lift=0.06 - k * 0.04, group='fing%d' % k)
        seam(r, 'fing%d' % k, 0.16)
    r.tube((hx - 0.4, hy - 1.4), (hx + 1.8, hy - 3.8), 1.2, 0.95, M['hand'], lift=0.14, group='thumbN')   # the thumb up and back
    seam(r, 'thumbN', 0.2)


# --------------------------------------------------------------------------------------------------------------- head
EY = 32                                              # the eye row (in the head's own table coordinates)
HEAD_DY = 2
FACE_ROWS = {                                        # y: (left edge, right edge) of the face, turned 3/4 to the left
    20: (55.0, 62.0), 21: (53.0, 64.5), 22: (51.8, 66.0), 23: (51.0, 67.0), 24: (50.4, 67.6), 25: (50.0, 68.0),
    26: (49.9, 68.0), 27: (49.9, 68.1), 28: (49.9, 68.1), 29: (50.0, 68.1), 30: (50.0, 68.1), 31: (50.1, 68.1),
    32: (50.2, 68.0), 33: (50.4, 67.9), 34: (50.7, 67.7), 35: (51.1, 67.3), 36: (51.6, 66.8), 37: (52.1, 66.2),
    38: (52.6, 65.4), 39: (53.1, 64.5), 40: (53.7, 63.4), 41: (54.3, 62.2), 42: (54.9, 60.8), 43: (55.6, 59.2), 44: (56.4, 57.8)}
HAIR_SIL = [(47.0, 25), (49.0, 19), (53.0, 15), (58.0, 13), (64.0, 13.6), (70.0, 17.5), (73.6, 24), (75.6, 32), (76.8, 41),
            (77.0, 49), (75.4, 54.4), (71.0, 55.6), (69.0, 50), (66.0, 46), (62.0, 44.5), (55.0, 44.5), (52.4, 41.0), (49.6, 44.0), (48.6, 47.6), (47.4, 47.0), (45.6, 41),
            (45.4, 33)]
# locks: (points, radius, lift); the back ones first. Each is a spiral ringlet (a coiling band of shade along it).
LOCKS_BACK = [
    ([(64.0, 15.0), (71.0, 18.0), (75.0, 25.0), (76.0, 33.0), (76.4, 41.0), (75.8, 48.0), (76.6, 52.6)], 2.1, -0.12),
    ([(66.0, 17.0), (72.5, 23.0), (73.0, 31.0), (71.0, 38.0), (72.0, 46.0), (71.0, 53.0)], 2.0, -0.18),
    ([(54.0, 15.0), (49.0, 17.5), (46.2, 23.5), (45.8, 30.5), (46.4, 37.5), (45.8, 43.5), (47.6, 47.4)], 2.0, -0.08),
]
LOCKS_FRONT = [
    ([(62.0, 16.0), (69.0, 19.0), (72.0, 26.0), (72.4, 33.0), (73.6, 40.0), (72.6, 46.6), (74.0, 51.6)], 2.2, 0.0),
    ([(60.0, 18.0), (66.0, 21.0), (68.6, 27.0), (68.6, 33.5), (69.6, 40.0), (68.8, 45.6)], 2.0, 0.04),
    ([(56.0, 16.0), (51.4, 19.2), (48.8, 25.0), (49.0, 31.0), (48.2, 37.0), (49.0, 42.6)], 1.9, 0.08),
    ([(57.0, 14.0), (61.0, 14.4), (65.0, 16.0), (68.6, 20.0), (70.0, 24.0)], 2.0, 0.16),   # over the top, toward the near side
    ([(56.4, 15.4), (53.2, 18.0), (51.2, 21.4), (50.4, 25.2), (50.4, 27.6)], 1.8, 0.14),   # the fringe over the far temple
]


def squash(pts):
    """the crown's curls sit a little flatter than drawn (less of a puff over the skull)"""
    return [(p[0], p[1] + max(0.0, 20.0 - p[1]) * 0.3) + tuple(p[2:]) for p in pts]


HAIR_SIL = squash(HAIR_SIL)
LOCKS_BACK = [(squash(p), r_, l_) for (p, r_, l_) in LOCKS_BACK]
LOCKS_FRONT = [(squash(p), r_, l_) for (p, r_, l_) in LOCKS_FRONT]


def inside(pts, x, y):
    c = False
    for i in range(len(pts)):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
        if (y0 <= y < y1) or (y1 <= y < y0):
            if x < x0 + (y - y0) * (x1 - x0) / (y1 - y0): c = not c
    return c


def lock(r, pts, rad, lift, g, U, dx_end=0.0, seed=0):
    """a spiral ringlet: curls strung along a spline through pts (unbreathed coordinates), zig-zagging side to side as the
    coil turns, each one its own little volume so the renderer shades the gaps between them; it tapers to the end"""
    pts = [(x + (dx_end * (i / (len(pts) - 1)) ** 2 if dx_end else 0), y) for i, (x, y) in enumerate(pts)]
    path = spline(pts, 0.5)
    acc, out, s = 0.0, [], 0.0
    for i in range(1, len(path)):
        s += math.hypot(path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1])
        if s >= acc: out.append((path[i], i)); acc += 2.1
    n = len(out)
    for k, ((x, y), i) in enumerate(out):
        j = max(1, min(len(path) - 1, i))
        dx, dy = path[j][0] - path[j - 1][0], path[j][1] - path[j - 1][1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        t = k / max(1, n - 1)
        side = 1 if (k + seed) % 2 else -1
        off = side * 0.75 * (1 - 0.3 * t)
        rr = rad * (1 - 0.32 * t ** 1.4)
        jit = ((h32(k, seed, 11) % 100) / 100 - 0.5) * 0.12
        r.ellipsoid(x + nx * off, U(y + ny * off), rr * 1.05, rr * 0.82, M['hair'], rot=math.atan2(dy, dx) + side * 0.5,
                    lift=lift + jit, jag=0.18, group='%s_%d' % (g, k))


def hair_back(r, U, P):
    """the mass of curls behind the face: fuller on the near side and over the near shoulder"""
    b = P.get('b', 0)
    r.ellipsoid(61.0, U(33), 17.0, 22.0, M['hair'], lift=-0.36, group='hairbase', clip=lambda x, y: inside(HAIR_SIL, x + 0.5, y + 0.5 + b - HEAD_DY))
    for k, (pts, rad, lift) in enumerate(LOCKS_BACK):
        lock(r, pts, rad, lift, 'hairB%d' % k, U, seed=k * 3)


BANGS = [(55.6, 14.6), (61.0, 14.4), (66.4, 16.8), (69.6, 21.0), (70.0, 25.0), (68.0, 26.8), (65.6, 25.6), (63.0, 25.2),
         (60.4, 25.6), (57.6, 24.8), (55.0, 25.4), (52.6, 25.0), (51.0, 26.6), (50.2, 23.6), (51.6, 19.4), (53.6, 16.4)]
BANGS = squash(BANGS)
BANG_TOP = squash([(57.2, 16.4, 1.7), (60.6, 16.6, 1.8), (64.2, 18.0, 1.8), (67.4, 20.8, 1.7), (53.6, 18.6, 1.6),
                   (59.0, 20.4, 1.5), (62.8, 21.4, 1.6), (66.2, 23.4, 1.5)])
BANG_ENDS = [(51.6, 25.0, 1.5), (54.2, 24.4, 1.7), (57.0, 24.0, 1.8), (60.0, 24.4, 1.8), (62.8, 24.4, 1.7), (65.6, 25.0, 1.7),
             (68.2, 25.8, 1.6)]


def bangs(r, U, P):
    """the fringe: swept from a side parting across the forehead toward the near temple, its ends curling"""
    def v(x, y):
        yy = y + P.get('b', 0)
        q = (x * 0.9 - yy * 1.6 + 0.6 * math.sin(yy * 1.3)) % 4.2                    # strands combed across, toward the right
        return (-0.26 if q < 1.1 else 0.1 if 2.0 < q < 3.0 else 0) + (0.12 if yy < 19 and x < 60 else 0)
    r.poly([(x, U(y)) for (x, y) in BANGS], M['hair'], lift=0.04, round_=0.6, tilt=-0.4, group='bangs', vfun=v)
    for k, (x, y, rr) in enumerate(BANG_TOP):                                         # curls breaking up the swept mass
        r.ellipsoid(x, U(y), rr * 1.1, rr * 0.85, M['hair'], lift=0.1 - (k % 3) * 0.05, jag=0.2, rot=-0.4 + k * 0.7, group='btop%d' % k)
    for k, (x, y, rr) in enumerate(BANG_ENDS):
        r.ellipsoid(x, U(y), rr * 1.1, rr * 0.85, M['hair'], lift=0.02 - (k % 2) * 0.06, jag=0.18, rot=0.6 + k * 0.4, group='bend%d' % k)
    for y in range(14, 18): r.darken(55 + (1 if y > 16 else 0), U(y), 0.3)          # the parting


def hair_front(r, U, P):
    stir = P.get('stir', 0)
    bangs(r, U, P)
    for k, (pts, rad, lift) in enumerate(LOCKS_FRONT):
        lock(r, pts, rad, lift, 'hairF%d' % k, U, dx_end=(-1.2 if (stir and k == 2) else 0.0), seed=k * 5 + 1)


def neck(r, U):
    r.tube((58.0, U(41)), (59.2, U(50)), 4.2, 4.6, M['skin'], lift=-0.22, group='neck')
    r.ellipsoid(59.2, U(48.6), 7.0, 3.2, M['top'], lift=0.04, group='rollneck', vfun=lambda x, y, u, w: -0.12 if x % 2 == 0 else 0.04)
    seam(r, 'rollneck', 0.2)


def face(r, U, P):
    """the face, painted in clean bands (no dither) so it reads at 1x; key light from the top left"""
    L = rig.norm((-0.55, -0.55, 0.62))
    A = 59.0                                          # where the face looks straight at us (the near cheek plane)
    oid = r.new('face')
    for y, (l, rr) in FACE_ROWS.items():
        for x in range(int(math.floor(l)), int(math.ceil(rr))):
            if x + 0.5 < l or x + 0.5 > rr: continue
            nx = (x + 0.5 - A) / (A - l) if x + 0.5 < A else (x + 0.5 - A) / (rr - A)
            nx = max(-0.98, min(0.98, nx))
            w = (y - 32.5) / 12.5
            n = rig.norm((nx * 0.95, w * 0.75 + (0.3 if y >= 42 else 0), math.sqrt(max(0.05, 1 - nx * nx * 0.85 - w * w * 0.4))))
            v = 0.2 + 0.8 * max(0.0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2])
            if 51 <= x <= 53 and 33 <= y <= 35: v += 0.06                              # the far cheekbone
            if x >= 65: v -= 0.06
            c = SKIN[max(2, min(8, 2 + int(v * 6.6)))]
            if 61 <= x <= 65 and 35 <= y <= 38: c = mix(c, (186, 100, 88), 0.16)       # warmth on the near cheek
            if (x, y) in ((53, 35), (54, 36), (59, 36), (61, 36), (63, 35), (62, 37)): c = mix(c, SKIN[3], 0.3)   # freckles
            r.fixed(x, U(y), c, oid)
    look = P.get('look', 0)
    ey = U(EY)
    for (ex, wdt) in ((60, 3), (52, 2)):                                                 # eyes: the near one wide, the far narrow
        if P.get('blink'):
            for x in range(ex, ex + wdt): r.fixed(x, ey, SKIN[3]); r.fixed(x, ey - 1, SKIN[4])
            continue
        for x in range(ex, ex + wdt): r.fixed(x, ey, EYEW)
        if wdt == 3:
            px = ex + (2 if look else 0)
            r.fixed(px, ey, PUPIL); r.fixed(px + (1 if not look else -1), ey, IRIS)
        else:
            r.fixed(ex + (1 if look else 0), ey, PUPIL)
        for x in range(ex, ex + wdt): r.fixed(x, ey - 1, SKIN[1])                       # the upper lid / lashes
        r.fixed(ex + wdt - (1 if wdt == 3 else 0), ey + 1, SKIN[4])
    # the nose: its bridge on the front line, the shaded side away from the key light, the lit tip turned left
    for y in (33, 34, 35): r.fixed(57, U(y), SKIN[6]); r.fixed(58, U(y), SKIN[4])
    r.fixed(56, U(36), SKIN[7]); r.fixed(55, U(37), SKIN[7]); r.fixed(56, U(37), SKIN[6]); r.fixed(57, U(37), SKIN[5]); r.fixed(58, U(36), SKIN[3])
    r.fixed(56, U(38), SKIN[3]); r.fixed(57, U(38), SKIN[2]); r.fixed(58, U(38), SKIN[3]); r.fixed(59, U(37), SKIN[4])
    # the mouth: set, the near corner turned up -- the tired, businesslike half-smile
    my = U(40)
    for (x, c) in ((54, LIP[1]), (55, LIP[0]), (56, LIP[0]), (57, LIP[0]), (58, LIP[0]), (59, LIP[1])): r.fixed(x, my, c)
    r.fixed(60, my - 1, LIP[1])
    r.fixed(55, my + 1, LIP[2]); r.fixed(56, my + 1, LIP[2]); r.fixed(57, my + 1, LIP[2]); r.fixed(58, my + 1, SKIN[5])
    r.fixed(56, my + 2, SKIN[4]); r.fixed(57, my + 2, SKIN[4])                           # under the lip
    for x in range(56, 60): r.fixed(x, U(44), SKIN[2])                                  # the jaw's shadow line


def goggles(r, U, P):
    """round teal goggle-glasses: thick gunmetal rims, translucent teal lenses, a bridge, the near temple arm"""
    lenses = ((61.4, 3.3, 3.4), (52.7, 2.5, 3.3))     # (cx, rx, ry): the far one foreshortened
    ey = U(EY) + 0.5
    for li, (cx, rx, ry) in enumerate(lenses):
        for y in range(int(ey - ry) - 2, int(ey + ry) + 2):
            for x in range(int(cx - rx) - 2, int(cx + rx) + 2):
                d = math.hypot((x + 0.5 - cx) / rx, (y + 0.5 - ey) / ry)
                if d <= 0.9:
                    e = r.buf.get((x, y))
                    base = e[3] if (e and e[3] is not None) else LENS[2]
                    c = mix(base, LENS[3], 0.5)
                    if y + 0.5 < ey - 0.5 and x + 0.5 < cx: c = mix(c, LENS[5], 0.22)
                    r.fixed(x, y, c)
                elif d <= 1.0 + 0.8 / min(rx, ry):
                    a = math.atan2(y + 0.5 - ey, x + 0.5 - cx)
                    col = GUN[5] if -2.6 < a < -0.9 else (GUN[1] if 0.4 < a < 2.6 else GUN[3])
                    r.fixed(x, y, col)
        gx, gy = int(cx - rx * 0.4), int(ey - ry * 0.5)
        if P.get('glint'):
            for k in range(-1, 3):
                x, y = gx + k, gy + 1 - k
                if math.hypot((x + 0.5 - cx) / rx, (y + 0.5 - ey) / ry) <= 0.95:
                    r.fixed(x, y, (236, 255, 250) if k in (0, 1) else LENS[6])
        else:
            r.fixed(gx, gy, LENS[6] if li == 0 else LENS[5])
    for x in (56, 57): r.fixed(x, U(31), GUN[4])                                       # the bridge over the nose
    r.fixed(56, U(32), GUN[1])
    for x in range(65, 69): r.fixed(x, U(31) + (1 if x > 66 else 0), GUN[2] if x % 2 else GUN[3])   # the temple arm, into the hair
    r.fixed(65, U(30), GUN[5])


def brows(r, U, P):
    by = U(28) - (1 if P.get('look') else 0)
    for (x, dy, c) in ((58, 1, HAIR[3]), (59, 0, HAIR[4]), (60, 0, HAIR[4]), (61, -1, HAIR[4]), (62, -1, HAIR[3]), (63, -1, HAIR[2]), (64, 0, HAIR[2])):
        r.fixed(x, by + dy, c)                                                         # the near brow, arched (sceptical)
    for (x, dy, c) in ((50, 1, HAIR[2]), (51, 0, HAIR[3]), (52, 0, HAIR[4]), (53, 0, HAIR[3]), (54, 1, HAIR[2])):
        r.fixed(x, by + dy + 1, c)


# ----------------------------------------------------------------------------------------------------------- the glyph
def glyph(P):
    """the holographic glyph as its own RGBA layer: a ring with an orbiting bead, a broken inner ring that turns, a bright
    core, ticks over the ring, a tail curling down to her palm, sparks; a soft halo. Returns (layer, centre)."""
    i, pulse, drift = P['_i'], P.get('pulse', 0), P.get('drift', 0)
    cx, cy = GLYPH[0], GLYPH[1] + P.get('hb', 0)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); p = lay.load()
    strokes = {}
    def put(x, y, k):
        x, y = int(math.floor(x)), int(math.floor(y))
        if 0 <= x < W and 0 <= y < H: strokes[(x, y)] = max(strokes.get((x, y), 0), k)
    rr = 6.0 + (0.8 if pulse else 0)
    for a in range(64):                                                               # the ring, brighter on top
        t = a / 64 * 2 * math.pi
        put(cx + math.cos(t) * rr, cy + math.sin(t) * rr * 0.94, 3 if math.sin(t) < -0.3 else 2)
    step = {3: 1, 4: 2}.get(i, 0)                   # 0 -> 3 -> 4 -> 0 turns the mechanism one full third-step cycle;
    spin = step * 2 * math.pi / 9                     # every other frame is an excursion from rest and keeps it still
    for a in range(36):                                                               # the inner ring, in three arcs, turning
        t = a / 36 * 2 * math.pi
        if (t + spin) % (2 * math.pi / 3) < 1.4: put(cx + math.cos(t) * 3.2, cy + math.sin(t) * 3.0, 2)
    ang = -0.9 + step * 2 * math.pi / 3
    put(cx + math.cos(ang) * rr, cy + math.sin(ang) * rr * 0.94, 5)                   # the bead orbiting the ring
    put(cx + math.cos(ang - 0.2) * rr, cy + math.sin(ang - 0.2) * rr * 0.94, 4)
    flash = 1 if P.get('tap') else 0                  # a tap on the device: the core answers
    for (dx, dy) in ((0, 0), (-1, 0), (0, -1), (-1, -1)): put(cx + dx, cy + dy, 5 if (dx, dy) == (-1, -1) or flash else 4)   # the core
    if flash:
        for (dx, dy) in ((1, -1), (-2, -1), (-1, 1), (-1, -3)): put(cx + dx, cy + dy, 2)
    for t in (-1.57, -1.05, -2.09):                                                   # three ticks over the ring
        for k in (1.2, 2.2): put(cx + math.cos(t) * (rr + k), cy + math.sin(t) * (rr + k), 2)
    sway = 1.0 if P.get('stir') else 0.0
    phase = 0.9 if P.get('look') else 0.0             # frame 5: a ripple runs down the tail
    top, bot = cy + rr * 0.94 + 0.5, 77.0
    for k in range(22):                                                               # the tail curling down to the palm
        t = k / 21
        x = cx - 0.5 + math.sin(t * 2.4 * math.pi + 0.3 + phase) * (2.2 - t * 1.2) + sway * math.sin(t * math.pi) - t * 1.5
        put(x, top + t * (bot - top), 3 if k < 6 else 2 if k < 15 else 1)
    for (dx, dy) in ((0, 0), (1, 0), (-1, 0)): put(93.0 + dx, 77.0 + dy - P.get('b', 0), 3 if dx == 0 else 2)  # where it springs from
    sparks = [(-5, -12), (4, -14), (8, -9), (-1, -17), (-9, -6)] + ([(-8, -14), (10, -4), (3, -20)] if pulse else [])
    for j, (sx, sy) in enumerate(sparks):
        up = (2 if drift else 0) + (1 if (pulse and j % 2) else 0)
        x, y = cx + sx + (1 if drift and j % 2 else 0), cy + sy - up
        put(x, y, 4 if j % 2 == 0 else 3)
        if j in (0, 2) or (pulse and j == 5):
            for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)): put(x + dx, y + dy, 1)
    boost = 1 if pulse else 0
    halo = {}
    for (x, y), k in strokes.items():
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                d = math.hypot(dx, dy)
                if d < 0.5 or d > 3.2: continue
                a = int((70 if d < 1.5 else 38 if d < 2.5 else 18) * (1.25 if pulse else 1.0) * (0.6 + 0.12 * k))
                q = (x + dx, y + dy)
                if q not in strokes: halo[q] = max(halo.get(q, 0), a)
    for (x, y), a in halo.items():
        if 0 <= x < W and 0 <= y < H: p[x, y] = MINT + (min(160, a),)
    for (x, y), k in strokes.items():
        p[x, y] = HOLO[min(5, k + boost)] + (255 if k >= 2 else 210,)
    return lay, (cx, cy)


def spill(im, centre, P):
    """the glyph's light on her: strong on the palm and the cuff, a rim on the edges facing it, a breath on the coat,
    the hair and the near lens. Quantised to three steps so the palette stays small."""
    cx, cy = centre
    px = im.load()
    Rr = 36.0 * (1.12 if P.get('pulse') else 1.08 if P.get('ripple') else 1.0)
    out = {}
    for y in range(H):
        for x in range(W):
            c = px[x, y]
            if c[3] < 255: continue
            d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 0.9)
            if d >= Rr or x < 60: continue
            k = 0.3 * (1 - d / Rr) ** 1.8
            rim = 0
            for (dx, dy) in ((1, 0), (1, -1), (0, -1), (2, 0)):                      # an edge that faces the glyph
                q = (x + dx, y + dy)
                if not (0 <= q[0] < W and 0 <= q[1] < H) or px[q][3] == 0: rim = 1
            if rim and x > 66: k += 0.5 * (1 - d / Rr)
            if y > cy + 16 and x > 87: k += 0.2                                        # the palm under it
            step = 0 if k < 0.07 else 1 if k < 0.2 else 2 if k < 0.36 else 3
            if step: out[(x, y)] = mix(c[:3], MINT, (0.0, 0.13, 0.27, 0.45)[step])
    for (x, y), c in out.items(): px[x, y] = c + (255,)


def elphi(P, i):
    P = dict(P); P['_i'] = i
    r = Rig(W, H)
    b = P.get('b', 0)
    U = lambda y: (y - b) if isinstance(y, int) else y - b
    # behind the legs: the inside of the coat's back, in shadow
    r.poly([(43, 96), (76, 96), (80, 134), (40, 134)], M['coat'], lift=-0.5, round_=0.5, group='coatback',
           vfun=lambda x, y: -0.1 if (x * 3) % 7 == 0 else 0)
    legs(r, P)
    torso(r, U, P)
    coat(r, U, P)
    near_arm(r, U, P)
    far_arm(r, U, P)
    Uh = lambda y: U(y + HEAD_DY)                    # the head sits HEAD_DY lower than its tables (a short neck, tucked in the collar)
    Un = lambda y: U(y + 1)
    hair_back(r, Uh, P)
    neck(r, Un)
    face(r, Uh, P)
    goggles(r, Uh, P)
    brows(r, Uh, P)
    hair_front(r, Uh, P)
    im = r.render(shadow=0.14, contact=0.11)
    px = im.load()
    for y in range(H):
        for x in range(W):
            if px[x, y] == (18, 14, 12, 255): px[x, y] = WARM_INK + (255,)
    lay, centre = glyph(P)
    spill(im, centre, P)
    im.alpha_composite(lay)
    return im.crop((0, 1, W, H + 1))                  # drawn a row low: the sole's outline lands on y 156 like the old sheet


def sheet(frames, path):
    s = Image.new('RGBA', (W * len(frames), H), (0, 0, 0, 0))
    for i, im in enumerate(frames): s.paste(im, (i * W, 0))
    s.save(path)


def write_gpl(frames, path):
    """the ramps first, then the mixed colours (spill, lenses) by frequency, up to 256"""
    seen, rows = set(), []
    for c in ([INK, WARM_INK] + COAT + TOP + KNIT + TROU + BOOT + BELT + SKIN + HAIR + GUN + LENS + BRASS + PEN + HOLO
              + [MINT, EYEW, IRIS, PUPIL] + LIP):
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    extra = {}
    for im in frames:
        for y in range(H):
            for x in range(W):
                c = im.getpixel((x, y))
                if c[3] == 255 and c[:3] not in seen: extra[c[:3]] = extra.get(c[:3], 0) + 1
    for c, _ in sorted(extra.items(), key=lambda kv: -kv[1])[:256 - len(rows)]:
        seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(path, 'w').write('GIMP Palette\nName: elphi\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')


if __name__ == '__main__':
    os.makedirs(f'{OUT}/elphi', exist_ok=True)
    frames = [elphi(p, i) for i, p in enumerate(POSE)]
    for i, im in enumerate(frames): im.save(f'{OUT}/elphi/{i}.png')
    sheet(frames, f'{OUT}/elphi.png')
    write_gpl(frames, f'{OUT}/elphi.gpl')
    print('ok', OUT)
