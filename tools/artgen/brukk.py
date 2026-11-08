"""Brukk, Keeper of the Rust Choir (RustDomainScene), redrawn with the character renderer (rig.py, the Edgar quality bar)
after the old art (Brukk.png): a massive man the machines have been growing metal into, turned a little to his right
(toward the viewer's left, where the player stands), his weight on his right leg -- that hip high, that shoulder low.
A peaked conductor's cap with a winged brass badge; under its peak the face is a tarnished copper respirator mask: a
dark visor band with two forge-red eye slits, a muzzle grille of broad slats, a ribbed filter canister at the jaw.
A heavy greatcoat gone to rags and rust: wide lapels, a broad belt cinching it (the cloth bloused above, breaking into
deep folds below), a thick hem fraying into rust-red tatters, sleeves widening to ragged cuffs, rusted studs on the
shoulders; a rust waistcoat, an iron plate grown into the breastbone with a seam that glows when it clicks, a chain
slung from shoulder to hip; copper-skinned hands. The baton rests in his right hand, held low and forward; the left hand
hangs half closed at his side. Boots wound with chain. 128x192 frames, soles on y 189; an 8-frame calm idle:
  0 rest            1 inhale (the chest seam glows)      2 the eyes dim (his blink)
  3 the baton lifts a little                           4 the beat: the baton dips
  5 the head inclines, listening to the machines       6 the same, the eyes flare, the chest clicks, the hand opens
  7 exhale, settling
python3 brukk.py <outdir>  ->  brukk.png (8-frame sheet) + brukk/<n>.png + brukk.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK, h32
from rig import Rig, Mat
from feral_toast import ik
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
R = ramp
COAT   = R('#0a0807 #110e0b #191410 #211b15 #2a221b #342a21 #3f3228 #4b3c2f #584637 #665140 #755d4a')
TATTER = R('#1c0d08 #2b130b #3c1b0f #4f2414 #622d19 #75381f')
VEST   = R('#1e0d08 #2d140b #3e1c0f #502514 #632f19')
TROU   = R('#0b0a09 #13110f #1c1916 #25211d #2f2a25')
BOOT   = R('#0a0807 #120e0b #1b1510 #241c16 #2e241c #3a2e24 #46382c')
CAP    = R('#09090a #101012 #18181b #212125 #2a2a2f #35353b #424249')
COPPER = R('#170d08 #24140c #341d11 #452717 #58321e #6c3f26 #814d2f #965d39 #a86d45 #b98054')
VERDI  = R('#14211c #1c2f27 #273e33 #335040 #42624f')
IRONC  = R('#0e0f10 #181a1c #232629 #2f3337 #3c4146 #4b5157 #5c6368 #70777c')
RUSTC  = R('#1e140c #2c1d10 #3d2815 #50341b #644222 #78502a #8c5f33')
BRASS  = R('#2a1d09 #463210 #654a18 #866422 #a5802f #c39d42 #ddbd62 #f0d88a')
EYE    = [(60, 8, 5), (124, 20, 10), (196, 48, 20), (248, 112, 52), (255, 186, 120), (255, 236, 200)]
M = {'coat': Mat(COAT, 'wool', 0.12), 'coatin': Mat(COAT, 'wool', 0.06), 'tatter': Mat(TATTER, 'fabric', 0.18),
     'vest': Mat(VEST, 'fabric', 0.2), 'trou': Mat(TROU, 'fabric', 0.16), 'boot': Mat(BOOT, 'leather', 0.18, 0.5),
     'cap': Mat(CAP, 'wool', 0.18), 'peak': Mat(CAP, 'leather', 0.16, 0.9), 'copper': Mat(COPPER, 'metal', 0.24, 0.7),
     'skin': Mat(COPPER, 'skin', 0.26, 0.35), 'iron': Mat(IRONC, 'metal', 0.22, 0.7), 'rust': Mat(RUSTC, 'metal', 0.22, 0.2),
     'brass': Mat(BRASS, 'metal', 0.26, 0.9), 'belt': Mat(BOOT, 'leather', 0.2, 0.45)}

POSE = [dict(b=0, eye=0, beat=0, hand=0, tilt=0, chest=0), dict(b=1, eye=0, beat=0, hand=0, tilt=0, chest=1),
        dict(b=0, eye=1, beat=0, hand=0, tilt=0, chest=0), dict(b=1, eye=0, beat=1, hand=0, tilt=0, chest=0),
        dict(b=0, eye=0, beat=2, hand=0, tilt=0, chest=0), dict(b=0, eye=0, beat=0, hand=0, tilt=1, chest=0),
        dict(b=0, eye=2, beat=0, hand=1, tilt=1, chest=2), dict(b=1, eye=0, beat=0, hand=0, tilt=0, chest=0)]


def tatters(r, pts, seed, mat, length, group):
    """heavy strips of rotten cloth hanging (straight down) off a hem polyline"""
    k = 0
    for (a, b) in zip(pts, pts[1:]):
        L = math.dist(a, b); n = max(1, int(L / 4.2))
        for i in range(n):
            t = (i + 0.5) / n
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            if h32(seed, k) % 4 == 0: k += 1; continue                                    # a gap
            w = 2.0 + (h32(seed, k, 1) % 3) * 0.9
            ln = length * (0.35 + (h32(seed, k, 2) % 10) / 12.0)
            sw = ((h32(seed, k, 3) % 5) - 2) * 0.4
            r.poly([(x - w / 2, y - 2), (x + w / 2, y - 2), (x + w * 0.35 + sw, y + ln * 0.7), (x + sw * 1.5, y + ln), (x - w * 0.3 + sw, y + ln * 0.6)],
                   mat, round_=0.5, group=group, vfun=lambda xx, yy: -0.12 if (xx + 2 * yy) % 5 == 0 else 0)
            k += 1


def chain_line(r, pts, group, step=2.0):
    """iron links along a polyline: a ring (with its hole) then an edge-on link, some of them rusted"""
    seg = []
    for a, b in zip(pts, pts[1:]):
        L = math.dist(a, b); n = max(1, int(L / step))
        for i in range(n):
            t = i / n
            seg.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    for i, (x, y) in enumerate(seg):
        mat = M['rust'] if h32(i, 7) % 3 == 0 else M['iron']
        if i % 2 == 0: r.ellipsoid(x, y, 1.7, 1.4, mat, lift=0.12, group=group, vfun=lambda xx, yy, u, w: -0.7 if u * u + w * w < 0.25 else 0)
        else: r.ellipsoid(x, y, 1.2, 0.7, mat, lift=0.3, group=group)


def folds(lines, y0, y1, depth=0.42, lit=0.2, side=None):
    """drapery: each line (xa at y0 -> xb at y1) is a dark valley with a lit ridge on its upper-left side; side(x, y)
    may darken the plane turned away from the light"""
    def vf(x, y):
        v = 0.0
        if y0 <= y <= y1:
            k = (y - y0) / (y1 - y0)
            for (xa, xb, s) in lines:
                lx = xa + (xb - xa) * k
                d = x + 0.5 - lx
                g = min(1.0, k * 3.0) * s
                if -0.9 < d < 1.1: v -= depth * g
                elif -3.0 < d <= -0.9: v += lit * g
                elif 1.1 <= d < 2.2: v -= depth * 0.4 * g
        if side: v += side(x, y)
        return v
    return vf


def sleeve(r, sh, el, wr, g, seed):
    """a heavy greatcoat sleeve shoulder -> elbow -> wrist, widening to a ragged cuff; a crease at the elbow"""
    r.ellipsoid(sh[0], sh[1] + 1, 8.6, 7.6, M['coat'], group=g, vfun=lambda x, y, u, w: 0.1 if w < -0.4 and u < 0.2 else 0)   # the shoulder's mass
    r.tube(sh, el, 7.4, 6.6, M['coat'], group=g, folds=lambda u, sd: (-0.3 if u > 0.82 and abs(sd) < 0.4 else 0) + (0.12 if sd < -0.45 else 0)
           + (-0.22 if abs((u - 0.45) - sd * 0.18) < 0.035 and sd > -0.3 else 0))                       # one long diagonal crease
    r.tube(el, wr, 6.6, 8.0, M['coat'], group=g, folds=lambda u, sd: (-0.24 if abs((u - 0.3) + sd * 0.2) < 0.04 and sd > -0.5 else 0)
           + (-0.24 if abs((u - 0.66) - sd * 0.16) < 0.04 and sd > -0.2 else 0) + (0.12 if sd < -0.5 else 0) + (-0.12 if sd > 0.6 else 0))
    dx, dy = wr[0] - el[0], wr[1] - el[1]; L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    for k in range(4):                                                      # rags hanging off the cuff
        bx = wr[0] + (-uy) * (k - 1.5) * 3.0
        by = wr[1] + ux * (k - 1.5) * 3.0 - 1
        ln = 3 + (h32(seed, k) % 4) * 1.5
        r.poly([(bx - 1.2, by), (bx + 1.2, by), (bx + 0.6, by + ln), (bx - 0.6, by + ln + 1)], M['tatter'], round_=0.4, group=g + 'rag')
    seam(r, g, 0.24)


def hand_baton(r, c, tip):
    """the right hand closed round the baton, the back of the hand toward us, the baton running out low and forward"""
    x, y = c
    dx, dy = tip[0] - x, tip[1] - y; L = math.hypot(dx, dy) or 1
    r.tube((x - dx / L * 4.5, y - dy / L * 4.5), tip, 1.1, 0.65, M['iron'], group='baton')           # the butt shows behind the fist
    r.fixed(tip[0], tip[1], IRONC[7])
    r.ellipsoid(x, y, 4.0, 4.0, M['skin'], group='fistR')
    for k in range(4):                                                      # the curled fingers wrapped over the baton
        r.ellipsoid(x - 3.0 + k * 0.6, y - 2.4 + k * 1.7, 1.5, 1.1, M['skin'], lift=0.08, group='fistR')
    r.tube((x + 1.5, y - 2.8), (x - 2.0, y - 3.6), 1.3, 1.1, M['skin'], lift=0.12, group='thumbR')       # the thumb along the baton
    r.fixed(x + 1, y + 1, VERDI[3]); r.fixed(x + 2, y, COPPER[2])                                        # tarnish, a weld scar
    seam(r, 'thumbR', 0.2); seam(r, 'fistR', 0.12)


def hand_side(r, c, opened):
    """the left hand hanging half closed at his side, the back of it toward us, the fingers curled toward the coat"""
    x, y = c
    r.ellipsoid(x, y, 3.8, 4.4, M['skin'], group='palmL')
    for k in range(4):
        fx = x - 2.4 + k * 1.6
        if opened: r.tube((fx, y + 3.2), (fx - 0.6 + k * 0.4, y + 9.0 - abs(k - 1.5) * 0.6), 1.15, 0.9, M['skin'], group='fingL%d' % k)
        else:
            r.tube((fx, y + 3.2), (fx - 0.4, y + 6.6 - abs(k - 1.5) * 0.4), 1.2, 1.1, M['skin'], group='fingL%d' % k)
            r.ellipsoid(fx - 0.8, y + 7.2 - abs(k - 1.5) * 0.4, 1.2, 1.0, M['skin'], lift=-0.12, group='fingL%d' % k)   # the curled tips
        seam(r, 'fingL%d' % k, 0.16)
    r.tube((x - 3.2, y + 0.5), (x - 4.2, y + 5.0), 1.4, 1.1, M['skin'], lift=0.06, group='thumbL')
    for (dx, dy) in ((0, -1), (1, -2), (-1, 0)): r.fixed(x + dx, y + dy, VERDI[3])
    seam(r, 'thumbL', 0.18)


def brukk(P):
    r = Rig(128, 192)
    b, beat, tilt = P['b'], P['beat'], P['tilt']
    side = lambda x, y: -0.3 if x > 88 + (y - 60) * 0.1 else 0.0               # the near flank, turned from the light
    # ---- the coat's lining, seen between the open skirts
    r.poly([(48, 108), (76, 110), (82, 166), (44, 166)], M['coatin'], lift=-0.28, group='lining')
    # ---- legs: his weight on the right leg (viewer's left), straight under the high hip; the left leg eased out
    hipW, footW = (53, 114), (49, 183)
    hipF, footF = (72, 118), (85, 183)
    kneeW = ik(hipW, footW, 36, 34, 'left'); kneeF = ik(hipF, footF, 35, 33, 'right')
    for (hip, knee, foot, sx, g) in ((hipW, kneeW, footW, -1, 'W'), (hipF, kneeF, footF, 1, 'F')):
        r.tube(hip, knee, 8.4, 7.2, M['trou'], group='leg' + g)
        r.tube(knee, (foot[0], foot[1] - 8), 7.2, 6.8, M['trou'], group='leg' + g)
        bt = (knee[0] + (foot[0] - knee[0]) * 0.3, knee[1] + (foot[1] - knee[1]) * 0.3)
        r.tube(bt, (foot[0], foot[1] - 2), 7.8, 7.4, M['boot'], group='boot' + g,
               folds=lambda u, sd: 0.24 if u < 0.06 else (-0.16 if abs(sd) > 0.72 else (-0.2 if 0.55 < u < 0.6 else 0)))
        tx = foot[0] + (-4 if g == 'W' else 3)                                 # the toe turns the way he faces / out
        r.ellipsoid(tx, 185.4, 10.4, 4.2, M['boot'], group='toe' + g)
        for x in range(int(tx - 10), int(tx + 11)): r.fixed(x, 189, BOOT[0])   # the sole's welt
        kx, ky = bt[0] + (foot[0] - bt[0]) * 0.25, bt[1] + (foot[1] - bt[1]) * 0.25
        chain_line(r, [(kx - 8, ky - 2), (kx + 8, ky + 2)], 'bchain' + g, step=1.9)    # chain wound round the shaft
        chain_line(r, [(kx - 8, ky + 6), (kx + 8, ky + 9)], 'bchain' + g, step=1.9)
    # ---- the waistcoat and the chest between the lapels (the body's front line sits left of centre: he is turned)
    r.poly([(50, 56 - b), (70, 56 - b), (71, 104), (49, 104)], M['vest'], group='vest',
           vfun=lambda x, y: (-0.16 if x == 60 and y > 62 else 0) + (-0.12 if (x * 2 + y) % 13 == 0 else 0))
    for y in (66 - b, 96):
        r.fixed(60, y, BRASS[4]); r.fixed(60, y + 1, BRASS[1])
    r.ellipsoid(59, 79 - b, 6.6, 7.6, M['iron'], group='plate', vfun=lambda x, y, u, w: (-0.28 if abs(u) > 0.8 else 0) + (0.08 if w < -0.5 else 0))
    for a in range(8):
        t = a / 8 * 2 * math.pi
        r.fixed(59 + math.cos(t) * 5.2, 79 - b + math.sin(t) * 6.0, IRONC[7] if math.sin(t) < 0 else IRONC[2])   # rivets
    glow = [EYE[1], EYE[3], EYE[4]][P['chest']]
    for y in range(74 - b, 85 - b):
        r.fixed(59, y, glow if 75 - b < y < 84 - b else EYE[1]); r.fixed(58, y, IRONC[0])
    if P['chest'] == 2:
        for (dx, yy) in ((1, 77), (1, 81), (-2, 79), (2, 79)): r.fixed(59 + dx, yy - b, EYE[2])
    # ---- the greatcoat: two panels with real drape; the near (viewer-right) panel wider, its flank in shadow
    hemW = [(53, 163), (46, 165), (39, 163), (31, 160)]
    hemF = [(67, 164), (75, 166), (84, 164), (92, 165), (101, 161)]
    r.poly([(42, 60 - b), (51, 53 - b), (55, 60 - b), (56, 100), (53, 108), (54, 116)] + hemW + [(32, 122), (36, 104), (37, 84), (38, 68)],
           M['coat'], group='coatW', vfun=folds([(40, 33, 1.0), (47, 44, 1.0), (52, 51, 0.6)], 110, 164, side=lambda x, y: 0.06 if x < 40 else 0))
    r.poly([(70, 53 - b), (84, 56 - b), (92, 62 - b), (95, 80), (93, 104), (96, 116)] + hemF[::-1] + [(66, 116), (65, 108), (64, 100), (66, 60 - b)],
           M['coat'], group='coatF', vfun=folds([(70, 72, 0.7), (78, 82, 1.0), (86, 91, 1.0), (92, 99, 0.8)], 110, 165, side=side))
    # bloused cloth above the belt: short folds pulled toward it
    for (x0, y0, x1, y1) in ((40, 92, 45, 104), (88, 90, 84, 104), (92, 96, 90, 105)):
        for k in range(10):
            t = k / 9; x = int(x0 + (x1 - x0) * t); y = int(y0 + (y1 - y0) * t)
            r.darken(x, y, 0.22); r.darken(x - 1, y, -0.1)
    # the hem's thickness: a lit lip, then the heavy tatters below it
    for pts, g in ((hemW, 'hemW'), (hemF, 'hemF')):
        for (a, c) in zip(pts, pts[1:]):
            n = int(abs(c[0] - a[0])) + 1
            for i in range(n):
                t = i / n; x = a[0] + (c[0] - a[0]) * t; y = a[1] + (c[1] - a[1]) * t
                r.darken(x, y - 2, -0.14); r.darken(x, y - 1, 0.12)
    tatters(r, hemW[::-1], 11, M['tatter'], 13, 'ragW')
    tatters(r, hemF, 12, M['tatter'], 13, 'ragF')
    # wide lapels, the near one broad and catching the light
    r.poly([(51, 53 - b), (55, 59 - b), (57, 98), (54, 94), (45, 66 - b)], M['coat'], lift=0.14, group='lapelW',
           vfun=lambda x, y: 0.12 if x <= 47 + (y - 60) * 0.25 else 0)
    r.poly([(70, 53 - b), (65, 59 - b), (63, 100), (67, 94), (80, 70 - b), (78, 60 - b)], M['coat'], lift=0.18, group='lapelF',
           vfun=lambda x, y: (0.16 if abs(x - (78 - (y - 62) * 0.32)) < 1.2 else 0) - (0.1 if x > 74 else 0))
    # the belt over the coat (it tilts with his hips), the iron buckle, a pouch on the near hip
    r.poly([(36, 101), (95, 105), (95, 112), (36, 108)], M['belt'], group='belt', vfun=lambda x, y: 0.14 if y == int(101 + (x - 36) * 0.068) else 0)
    for (dx, dy, c) in ((0, 0, IRONC[6]), (1, 0, IRONC[5]), (2, 0, IRONC[5]), (3, 0, IRONC[4]), (4, 0, IRONC[3]), (0, 1, IRONC[5]), (0, 2, IRONC[4]),
                        (0, 3, IRONC[3]), (4, 1, IRONC[2]), (4, 2, IRONC[2]), (4, 3, IRONC[1]), (1, 3, IRONC[2]), (2, 3, IRONC[1]), (3, 3, IRONC[1]), (2, 1, IRONC[0]), (2, 2, IRONC[0])):
        r.fixed(57 + dx, 103 + dy, c)
    r.poly([(80, 109), (90, 110), (90, 123), (80, 123)], M['belt'], round_=0.7, group='pouch', vfun=lambda x, y: 0.16 if y == 110 else (-0.2 if y == 113 else 0))
    # the chain slung over the coat, shoulder to hip, a loop hanging off the belt
    chain_line(r, [(45, 64 - b), (54, 76), (64, 90), (76, 102), (86, 107)], 'chain1')
    chain_line(r, [(40, 108), (38, 116), (41, 123), (45, 118), (46, 110)], 'chain2', step=1.9)
    for (sx_, sy_, rr) in ((36, 140, 3.0), (95, 134, 2.6), (44, 88, 2.0), (86, 152, 3.2)):              # rust soaked into the cloth
        for y in range(int(sy_ - rr), int(sy_ + rr * 1.8)):
            for x in range(int(sx_ - rr), int(sx_ + rr) + 1):
                d = ((x - sx_) / rr) ** 2 + ((y - sy_) / (rr * 1.8)) ** 2
                e = r.buf.get((x, y))
                if d < 1 - 0.45 * (h32(x, y, 31) % 7) / 7 and e and e[0] is M['coat']: e[0] = M['tatter']; e[1] -= 0.12
    # the high ragged collar behind and round the neck
    r.poly([(45, 45 - b), (48, 48 - b), (51, 43 - b), (54, 49 - b), (60, 52 - b), (68, 49 - b), (73, 45 - b), (77, 49 - b), (80, 47 - b),
            (82, 56 - b), (72, 60 - b), (52, 60 - b), (43, 56 - b)], M['coat'], lift=0.08, group='collar',
           vfun=lambda x, y: (-0.14 if (x + y) % 5 == 0 else 0) + (0.1 if y < 48 - b else 0) + side(x, y))
    # rusted studs on the shoulders (the near one shows three, the far one two)
    for (bx, by, sx) in ((80, 56, 1), (85, 58, 1), (90, 61, 1), (48, 59, -1), (43, 62, -1)):
        tip = (bx + sx * 1.6, by - b - 5.2)
        r.poly([(bx - 1.7, by - b + 1), (bx + 1.7, by - b + 1), tip], M['rust'], round_=0.7, group='stud%d%d' % (bx, by))
        r.fixed(tip[0], tip[1], RUSTC[6])
    # ---- arms close to the coat: elbows down and back; the baton low and forward, the free hand at his side
    shW, shF = (46, 67 - b), (87, 63 - b)
    elW = (shW[0] + 1.5, shW[1] + 27)                                        # elbows hang just under the shoulders, a touch back
    elF = (shF[0] + 2.5, shF[1] + 27)
    handW = [(38, 115), (37, 110), (39, 117)][beat]                          # the forearm comes forward to the baton hand
    tip = [(19, 138), (15, 127), (24, 144)][beat]
    handF = (89, 115) if not P['hand'] else (88, 112)
    sleeve(r, shF, elF, handF, 'armF', 22)
    hand_side(r, (handF[0] - 0.5, handF[1] + 3.5), P['hand'])
    sleeve(r, shW, elW, handW, 'armW', 21)
    hand_baton(r, (handW[0] - 0.5, handW[1] + 3.5), tip)
    # ---- the head, turned with the body: the copper mask, the respirator, the canister, the cap
    hx, hy = 59 + tilt, 40 - b + tilt                                        # hx: the mask's centre line
    r.ellipsoid(hx + 2, hy + 4, 11.5, 12.6, M['copper'], group='head', vfun=lambda x, y, u, w: (-0.22 if u > 0.72 else 0) + (0.08 if u < -0.5 else 0))
    # the visor band across the eyes: a dark recessed strip with a lit upper rim
    for y in range(int(hy - 3), int(hy + 3)):
        for x in range(int(hx - 10), int(hx + 12)):
            e = r.buf.get((x, y))
            if e and e[0] is M['copper']:
                e[1] -= 0.5 if y > hy - 3 else 0.0
                if y == int(hy - 3): e[1] += 0.25
    for (ex, w) in ((hx - 6, 4), (hx + 2, 6)):                               # the far eye slit narrower than the near one
        k = [(4, 3, 2), (2, 1, 1), (5, 4, 3)][P['eye']]
        for i in range(w):
            end = i == 0 or i == w - 1
            r.fixed(ex + i, hy - 1, EYE[k[1]] if end else EYE[k[0]])
            r.fixed(ex + i, hy, EYE[k[2]] if not end else EYE[1])
        if P['eye'] == 2:
            for i in range(1, w - 1): r.fixed(ex + i, hy - 2, EYE[2])
    # the respirator: a rounded muzzle of broad slats under the visor, its rim lit on top
    def muzzle(x, y, u, w):
        gap = (x - (hx - 6)) % 4 == 0 and -0.6 < w < 0.75 and abs(u) < 0.86
        return (-0.75 if gap else 0.1) + (0.18 if w < -0.55 else 0) - (0.2 if w > 0.7 else 0)
    r.ellipsoid(hx, hy + 8, 8.0, 5.6, M['copper'], lift=0.12, group='muzzle', vfun=muzzle)
    r.fixed(hx - 2, hy + 3, COPPER[8]); r.fixed(hx - 1, hy + 3, COPPER[7])                             # a hot spot on the nose bridge
    for (x, y) in ((hx - 9, hy - 1), (hx + 11, hy - 1), (hx - 7, hy + 8), (hx + 8, hy + 8)):
        r.fixed(x, y, COPPER[8]); r.fixed(x + (1 if x > hx else -1), y + 1, COPPER[2])                 # rivets
    for k in range(5):
        r.fixed(hx - 5 + (h32(k, 3) % 11), hy + 12 + (h32(k, 5) % 3), VERDI[2 + k % 2])               # verdigris where it sweats
    # the filter canister on the near jaw, ribbed, its hose into the collar
    r.tube((hx + 12, hy + 14), (hx + 15, 54 - b), 1.4, 1.4, M['rust'], group='hose')
    r.tube((hx + 9.5, hy + 6.5), (hx + 12.5, hy + 13.0), 3.6, 3.6, M['iron'], group='canister',
           folds=lambda u, sd: -0.38 if int(u * 7) % 2 == 0 and 0.12 < u < 0.88 else 0.06)
    r.ellipsoid(hx + 12.8, hy + 13.4, 3.4, 1.5, M['rust'], lift=0.12, group='canister2')
    # the cap: crown, band, the peak casting its shadow over the visor, the winged badge
    r.ellipsoid(hx + 2, hy - 12, 15.5, 7.4, M['cap'], group='crown', vfun=lambda x, y, u, w: (0.14 if w < -0.35 and u < 0.3 else 0) - (0.12 if (x * 2 + y) % 11 == 0 else 0) - (0.12 if u > 0.6 else 0))
    r.poly([(hx - 12, hy - 11), (hx + 15, hy - 10), (hx + 14, hy - 5), (hx - 11, hy - 6)], M['cap'], lift=-0.14, group='band',
           vfun=lambda x, y: -0.15 if y == int(hy - 6) else 0)
    r.ellipsoid(hx - 1, hy - 4.6, 14.0, 3.2, M['peak'], lift=0.05, group='peak', clip=lambda x, y: y > hy - 6)
    for x in range(int(hx - 11), int(hx + 13)):                              # the peak's shadow over the visor band
        r.darken(x, int(hy - 2.6), 0.35); r.darken(x, int(hy - 2.6) + 1, 0.15)
    for (dx, dy, c) in ((0, -9, BRASS[6]), (-1, -9, BRASS[4]), (1, -9, BRASS[4]), (0, -8, BRASS[3]), (0, -10, BRASS[5]),
                        (-2, -10, BRASS[5]), (-3, -10, BRASS[4]), (-4, -11, BRASS[3]), (-3, -9, BRASS[2]), (-5, -11, BRASS[2]),
                        (2, -10, BRASS[5]), (3, -10, BRASS[4]), (4, -11, BRASS[3]), (3, -9, BRASS[2]), (5, -11, BRASS[2])):
        r.fixed(hx + dx, hy + dy, c)
    seam(r, 'collar', 0.14); seam(r, 'lapelW', 0.14); seam(r, 'lapelF', 0.16); seam(r, 'band', 0.12); seam(r, 'belt', 0.14)
    return r.render()


if __name__ == '__main__':
    os.makedirs(f'{OUT}/brukk', exist_ok=True)
    frames = [brukk(p) for p in POSE]
    sheet = Image.new('RGBA', (128 * len(frames), 192), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        im.save(f'{OUT}/brukk/{i}.png'); sheet.paste(im, (i * 128, 0))
    sheet.save(f'{OUT}/brukk.png')
    ALL = [INK] + COAT + TATTER + VEST + TROU + BOOT + CAP + COPPER + VERDI + IRONC + RUSTC + BRASS + EYE
    seen, rows = set(), []
    for c in ALL:
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/brukk.gpl', 'w').write('GIMP Palette\nName: brukk\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT)
