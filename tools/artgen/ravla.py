"""Ravla, the Rust Choir's forger in the right corner of the Screaming Cork (ScreamingCorkInteriorScene), redrawn from
scratch with the character renderer (rig.py, the Edgar quality bar). The old AI image ravla.png stays only as the
reference for who she is -- no pixels are taken from it (heliodor.py redraws Heliodor the same way).

A gaunt woman hunched over her work at a crate she uses as a desk: dark hair scraped back into a bun with a brush
stuck through it, copper goggles with violet lenses pushed up on her forehead, hollow cheeks, a thin sly mouth; a
worn slate coat with the collar turned up and a patched elbow, a rust waistcoat with copper buttons and a Rust Choir
cog pin over a grimy shirt. Her right hand writes with a pale quill (ink-stained fingers), the left holds the sheet
flat; on the desk an inkwell, the half-forged document with a red seal, and her open forging case (a lid rack of
vials, bottles standing inside). Behind her rises the dark purple tentacle of the old art -- here it curls over her
like an angler's lure and holds a small lantern above her work, so the warm light falls on her face and hands.

128x144 frames, facing the viewer, the crate's foot on y 141 (rows 142-143 empty); an 8-frame idle:
  0 writing           1 the quill runs on along the line   7 ... and on (0-1-7 = a word written left to right)
  2 the quill lifts to the ink                             3 it dips in the inkwell
  4 she glances up at you, one brow raised (the lantern turns with her)   5 the same glance, a blink
  6 a slow breath at the start of the line, the lantern drifts the other way
python3 ravla.py <outdir>  ->  ravla.png (8-frame sheet) + ravla/<n>.png + ravla.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK, h32, make_noise
from rig import Rig, Mat
from feral_toast import ik, lerp
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
W, H = 128, 144
R = ramp
# ramps hue-shift from cool shadows to warm lamp-lit highlights
COAT   = R('#0c0e13 #12161b #192025 #20292d #2a3336 #343e3e #414a47 #4f5751 #60665c')
VEST   = R('#180a09 #27100c #391811 #4d2116 #622b1b #773723 #8d4a2e')
SHIRT  = R('#3a362f #534d44 #6e675a #8a8170 #a49a85 #bbb199')
SKIN   = R('#2c1c1c #43302b #5c433a #77594b #92705e #ab8770 #c19f86 #d4b79c #e3cbb0')
HAIR   = R('#0d090a #161011 #201716 #2b1f1c #372823 #45332b #554037')
COPPER = R('#28110a #44200f #653317 #874920 #a8622c #c47f40 #d99f60 #e9c18a')
TENT   = R('#110913 #1c1022 #281731 #351f40 #43284f #52325f #623d6f #74497f #8a5a92')
WOOD   = R('#19110c #251912 #322319 #402e21 #4f3a2a #5f4733 #6f553d #816548')
LEATH  = R('#1b0c0a #2a140f #3b1d15 #4e271b #623222 #773f2a')
VELVET = R('#1a0c16 #2a1424 #3c1e34 #4e2944')
PAPER  = R('#5a5243 #766c59 #92876f #ada287 #c5bb9e #d9d0b5')
QUILL  = R('#3a3838 #575553 #7a7672 #9e9993 #c0bab1 #ddd7cc')
GLASSG = R('#0b1a13 #142e22 #224734 #35674a #578a66')
GLASSA = R('#2b1506 #4b280b #724013 #9a5e1f #c48838')
GLASSV = R('#1a1026 #2c1b42 #422c5e #5c447e #78609c')
INKC   = R('#090a10 #111428 #1b2142 #2c3660')
SEAL   = R('#2e0806 #4e0f0b #721a12 #94291b #b23e28')
LENS   = [(38, 20, 56), (64, 36, 96), (100, 64, 144), (156, 118, 200), (222, 204, 246)]
FLAME  = [(122, 52, 18), (198, 98, 32), (240, 152, 52), (255, 208, 112), (255, 242, 200)]
LIP    = [(72, 42, 40), (94, 60, 54), (114, 78, 68)]
SUCKER = [(84, 46, 92), (134, 94, 138), (176, 134, 172)]
CORK   = (150, 120, 92)
IRIS   = (52, 62, 50)
PUPIL  = (22, 24, 20)
EYEW   = (196, 182, 162)
STAIN  = (28, 30, 52)
WARMOUT = (30, 20, 17)                                                                    # warm dark outline, never black
TENTOUT = (24, 10, 24)
def mat(rmp, tex, amb, spec=0.0, out=WARMOUT): return Mat(rmp, tex, amb, spec, outline=out)
M = {'coat': mat(COAT, 'wool', 0.2), 'vest': mat(VEST, 'fabric', 0.22, 0.15), 'shirt': mat(SHIRT, 'fabric', 0.26),
     'skin': mat(SKIN, 'skin', 0.3, 0.12), 'hair': mat(HAIR, 'fur', 0.22, 0.3), 'copper': mat(COPPER, 'metal', 0.24, 0.8),
     'tent': mat(TENT, 'skin', 0.2, 0.7, TENTOUT), 'wood': mat(WOOD, 'wood', 0.22), 'leath': mat(LEATH, 'leather', 0.2, 0.35),
     'velvet': mat(VELVET, 'wool', 0.2), 'paper': mat(PAPER, 'plain', 0.4), 'quill': mat(QUILL, 'fur', 0.34),
     'ink': mat(INKC, 'plain', 0.3, 1.0), 'patch': mat(LEATH, 'leather', 0.24, 0.2)}
GLASS = {id(g): mat(g, 'plain', 0.3, 0.9) for g in (GLASSG, GLASSA, GLASSV)}
nWear = make_noise(6, 431, 160, 160)

POSE = [dict(b=0, hand='A', blink=0, look=0, tent=0, fl=0), dict(b=0, hand='B', blink=0, look=0, tent=0, fl=1),
        dict(b=0, hand='lift', blink=0, look=0, tent=0, fl=2), dict(b=0, hand='dip', blink=0, look=0, tent=0, fl=3),
        dict(b=0, hand='pause', blink=0, look=1, tent=1, fl=1), dict(b=0, hand='pause', blink=1, look=1, tent=1, fl=0),
        dict(b=1, hand='A', blink=0, look=0, tent=2, fl=2), dict(b=0, hand='C', blink=0, look=0, tent=0, fl=3)]

# the layout (canvas px)
FLOOR, DESK_FAR, DESK_NEAR = 141, 104, 114
HANDS = {'A': (54, 108), 'B': (57, 108), 'C': (60, 108), 'lift': (47, 103), 'dip': (40, 102), 'pause': (54, 105)}
NIBS = {'dip': (38, 103), 'lift': (49, 105), 'pause': (57, 107)}
HAND_L = (72, 107)                                                                         # her left hand, flat on the sheet


def spline(pts, step=1.2):
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


def lamp_light(r, lx, ly, k, rad):
    """the lantern's warm light on everything near it -- a lift in the tone buffer, so it stays on the ramps
    (hair takes half: it must stay dark)"""
    for (x, y), e in r.buf.items():
        if e[0] is None: continue
        d = math.hypot(x + 0.5 - lx, y + 0.5 - ly)
        if d < rad: e[1] += k * (1 - d / rad) ** 2 * (0.45 if e[0] is M['hair'] else 1.0)


def coat_wear(x, y):
    """a worn coat: broad faded patches and grime; the lamp's side lighter, the far side falling into shadow"""
    return (nWear(x, y) - 0.5) * 0.16 + (62 - x) * 0.006


def tentacle(r, P):
    """rises from behind the crate past her right shoulder, curls over like an angler's lure; returns the tip"""
    base = [(27, 130), (25, 116), (22, 102), (21, 88), (23, 74), (27, 60), (29, 46), (31, 34), (35, 23), (40, 15),
            (46, 10), (52, 11), (55, 16), (54, 21), (51, 23)]
    dT = [(0, 0), (1, -1), (-1, 1)][P['tent']]
    n = len(base) - 1
    pts = [(x + dT[0] * (i / n) ** 2, y + dT[1] * (i / n) ** 2) for i, (x, y) in enumerate(base)]
    curve = spline(pts)
    N = len(curve) - 1
    rad = lambda t: 4.8 - 3.9 * t ** 0.75 + 0.35 * math.sin(t * 21)                               # tapering, a little ribbed
    for i in range(N):
        r.tube(curve[i], curve[i + 1], rad(i / N), rad((i + 1) / N), M['tent'], group='tent',
               folds=lambda u, sd: 0.2 if sd > 0.3 else (-0.12 if sd < -0.6 else 0))                     # the paler underside
    for i in range(5, N - 8, 6):                                                                  # suckers along the underside
        (x0, y0), (x1, y1) = curve[i - 1], curve[i + 1]
        dx, dy = x1 - x0, y1 - y0; l = math.hypot(dx, dy) or 1
        rr = rad(i / N)
        sx, sy = curve[i][0] - dy / l * (rr - 1.0), curve[i][1] + dx / l * (rr - 1.0)
        r.fixed(sx, sy, SUCKER[2]); r.fixed(sx + dx / l, sy + dy / l, SUCKER[1]); r.fixed(sx - dy / l * 0.8, sy + dx / l * 0.8, SUCKER[0])
    return curve[-1]


def lantern(r, tip, fl):
    """a ring, a copper cap, a glass globe with the flame, a copper base; returns the flame's centre"""
    lx, ly = int(round(tip[0])) - 1, int(round(tip[1])) + 2
    r.fixed(lx, ly - 1, COPPER[5]); r.fixed(lx + 1, ly - 1, COPPER[3])
    r.poly([(lx - 3, ly + 2), (lx + 4, ly + 2), (lx + 2.5, ly), (lx - 1.5, ly)], M['copper'], group='lantern')
    for y in range(ly + 2, ly + 9):
        for x in range(lx - 3, lx + 4):
            dx, dy = x - lx - 0.5, y - (ly + 5.5)
            if dx * dx / 12.5 + dy * dy / 14 > 1: continue
            dd = math.hypot(dx * 1.2, (dy - [0, 0.6, -0.4, 0.3][fl]))
            c = FLAME[4] if dd < 1.0 else FLAME[3] if dd < 1.9 else FLAME[2] if dd < 2.6 else FLAME[1] if dd < 3.2 else FLAME[0]
            r.fixed(x, y, c)
    r.fixed(lx - 2, ly + 3, (255, 236, 196))                                                      # the glass's glint
    r.poly([(lx - 3, ly + 9), (lx + 4, ly + 9), (lx + 3, ly + 11), (lx - 2, ly + 11)], M['copper'], lift=-0.1, group='lantern')
    return lx + 0.5, ly + 5.5


def desk(r):
    """a crate: its top and its left side seen (the scene's vanishing point lies far to the left)"""
    F, T, N_ = FLOOR, DESK_FAR, DESK_NEAR
    r.poly([(23, T), (28, N_), (28, F), (23, F - 9)], M['wood'], lift=-0.26, round_=0.2, group='desk',
           vfun=lambda x, y: -0.2 if (y - (x - 23) * 1.8) % 9 < 1 else 0)
    r.poly([(28, N_), (116, N_), (116, F), (28, F)], M['wood'], lift=-0.04, round_=0.25, group='desk',
           vfun=lambda x, y: (-0.26 if y in (N_ + 9, N_ + 18) else 0.08 if y in (N_ + 1, N_ + 10, N_ + 19) else 0)
                             + (0.12 if x < 31 or x > 112 else 0) + (-0.2 if x in (31, 112) else 0) - max(0, y - (F - 12)) * 0.014)
    r.poly([(23, T), (111, T), (116, N_), (28, N_)], M['wood'], lift=0.1, round_=0.15, group='desktop',
           vfun=lambda x, y: (-0.2 if y in (T + 3, T + 6) else 0) + (0.14 if y == N_ - 1 else 0))
    for (x, y) in ((29, N_ + 3), (29, N_ + 12), (29, N_ + 21), (114, N_ + 3), (114, N_ + 12), (114, N_ + 21)):   # nails
        r.fixed(x, y, WOOD[1]); r.fixed(x, y - 1, WOOD[6])
    cy = N_ + 13
    for a in range(16):                                                                           # a faded stencilled cog
        t = a / 16 * 2 * math.pi
        r.darken(70 + math.cos(t) * 4.6, cy + math.sin(t) * 3.4, -0.14 if a % 2 else -0.05)
    r.darken(70, cy, -0.08); r.darken(69, cy, -0.08)


def kit(r):
    """on the desk: the forging case (lid up, a rack of vials), the inkwell, the sheets"""
    cx0, cx1 = 88, 113
    r.poly([(cx0, 79), (cx1, 79), (cx1 - 0.5, 102), (cx0 + 0.5, 102)], M['leath'], lift=-0.02, round_=0.3, group='lid')
    r.poly([(cx0 + 2, 81), (cx1 - 2, 81), (cx1 - 2.5, 100), (cx0 + 2.5, 100)], M['velvet'], round_=0.3, group='lining')
    for k, g in enumerate([GLASSV, GLASSG, GLASSA, GLASSV, GLASSG, GLASSA]):
        x = cx0 + 4.5 + k * 3.3
        r.tube((x, 85), (x, 92), 1.1, 1.1, GLASS[id(g)], group='vial%d' % k)
        r.fixed(x - 0.5, 84, CORK); r.fixed(x - 0.5, 86, g[-1])
    for x in range(cx0 + 2, cx1 - 2): r.fixed(x, 89, LEATH[3] if x % 4 else COPPER[4])          # the strap holding them
    for (x, top, g, w_) in ((91, 93, GLASSG, 2.0), (96, 89, GLASSA, 1.7), (101, 94, GLASSV, 2.2), (106, 91, GLASSG, 1.6), (110, 95, GLASSA, 1.8)):
        r.tube((x, top + 4), (x, 105), w_, w_, GLASS[id(g)], group='bottle%d' % x)
        r.tube((x, top), (x, top + 4), 0.9, 1.0, GLASS[id(g)], group='bottle%d' % x)
        r.fixed(x - 0.5, top - 1, CORK); r.fixed(x - 1, top + 6, g[-1])
    r.poly([(cx0 - 1, 101), (cx1 + 1, 101), (cx1 + 1, 111), (cx0 - 1, 111)], M['leath'], round_=0.3, group='case',
           vfun=lambda x, y: (0.16 if y == 101 else 0) + (-0.16 if y == 106 else 0))
    for (x, y) in ((cx0 - 1, 102), (cx1, 102), (cx0 - 1, 109), (cx1, 109)):
        r.fixed(x, y, COPPER[5]); r.fixed(x + 1 if x < 100 else x - 1, y, COPPER[3])
    r.fixed(100, 104, COPPER[6]); r.fixed(101, 104, COPPER[4]); r.fixed(100, 105, COPPER[3]); r.fixed(101, 105, COPPER[2])   # the clasp
    # the inkwell
    r.ellipsoid(37, 107, 4.2, 2.6, M['ink'], group='inkwell')
    r.tube((37, 102.5), (37, 105), 1.8, 2.0, M['ink'], group='inkwell')
    r.fixed(36, 102, INKC[0]); r.fixed(37, 102, INKC[0]); r.fixed(35, 106, INKC[3]); r.fixed(34, 107, (120, 130, 170))
    # the sheets: one under, the forged document on top with lines of script and a red wax seal
    r.poly([(43, 106), (75, 105), (78, 112), (45, 113)], M['paper'], lift=-0.12, round_=0.1, group='sheet0')
    r.poly([(46, 105), (79, 105.5), (81, 112.5), (48, 112.5)], M['paper'], lift=0.1, round_=0.1, group='sheet1',
           vfun=lambda x, y: 0.04 * ((x * 7 + y * 3) % 5 == 0))
    for row, y in enumerate((107, 109, 111)):
        for x in range(49 + row, 77 - (7 if row == 2 else 0)):
            if h32(x, y, 7) % 3 and not (x <= 52 and y >= 109): r.fixed(x, y, INKC[2] if h32(x, y, 9) % 4 else INKC[1])
    for (x, y, c) in ((50, 110, SEAL[4]), (51, 110, SEAL[3]), (50, 111, SEAL[2]), (51, 111, SEAL[1]), (49, 111, SEAL[2]), (50, 109, SEAL[2])):
        r.fixed(x, y, c)


def ravla(P):
    r = Rig(W, H)
    b, look = P['b'], P['look']
    LX, LY = lantern(r, tentacle(r, P), P['fl'])
    hx, hy = 62, 52 - b - 2 * look                                                               # the head
    S = 70 - b                                                                                    # the shoulder line
    # ---- the turned-up collar (behind the head), the bun and the brush through it
    r.poly([(50, S - 1), (52.5, S - 13), (57.5, S - 12), (58.5, S - 3)], M['coat'], lift=-0.02, group='collarL',
           vfun=lambda x, y: 0.16 if x >= 56 else 0)
    r.poly([(74, S - 1), (71.5, S - 13), (66.5, S - 12), (65.5, S - 3)], M['coat'], lift=-0.1, group='collarR',
           vfun=lambda x, y: 0.12 if x <= 67 else 0)
    r.tube((hx - 3.5, hy - 20.5), (hx + 6, hy - 10.5), 0.75, 0.75, M['wood'], lift=0.34, group='brush')
    r.tube((hx + 6, hy - 10.5), (hx + 7.4, hy - 9), 1.1, 0.8, M['copper'], group='brush')         # the ferrule
    r.fixed(hx + 8, hy - 8.5, HAIR[5]); r.fixed(hx + 8.6, hy - 7.6, HAIR[4])                       # the bristles
    r.ellipsoid(hx + 1, hy - 14.2, 4.9, 4.0, M['hair'], group='bun', lift=-0.04,
                vfun=lambda x, y, u, w: -0.24 if abs((math.atan2(w, u) * 1.1 + math.hypot(u, w) * 4.6) % 1.7 - 0.85) < 0.2 else 0)
    r.tube((hx - 1.2, hy - 17.4), (hx + 0.4, hy - 13.6), 0.6, 0.6, M['wood'], lift=0.34, group='brush2')   # the brush in front of the bun
    # ---- the torso: coat, waistcoat, shirt collar (narrow, the shoulders hunched up toward the ears)
    folds = {52: 1, 53: -1, 56: 1, 57: -1, 68: 1, 69: -1, 72: 1, 73: -1}
    r.poly([(46, S + 2), (51, S - 3), (57, S - 5), (67, S - 5), (73, S - 3), (78, S + 2), (78, 86), (77, 104), (77, 118), (47, 118), (47, 104), (46, 86)],
           M['coat'], group='coat', vfun=lambda x, y: coat_wear(x, y) + (folds.get(x, 0) * 0.12 if y > S + 10 + (x % 5) else 0))
    r.poly([(56, S - 3), (68, S - 3), (66.5, 104), (57.5, 104)], M['vest'], group='vest',
           vfun=lambda x, y: -0.18 if x == 62 and y > S + 7 else 0)
    for y in (S + 10, S + 17, S + 24, S + 31):                                                    # small copper buttons
        r.fixed(62, y, COPPER[4]); r.fixed(62, y + 1, COPPER[1])
    r.poly([(57.5, S - 5), (62, S + 1), (66.5, S - 5), (65.5, S + 3), (62, S + 5), (58.5, S + 3)], M['shirt'], lift=-0.12, group='shirt')
    r.poly([(54, S - 3), (58, S - 5), (62.5, S + 5), (63, S + 23), (60, S + 29), (55, S + 9)], M['coat'], lift=0.1, group='lapelL',
           vfun=lambda x, y: coat_wear(x, y))
    r.poly([(70, S - 3), (66, S - 5), (61.5, S + 5), (61, S + 23), (64, S + 29), (69, S + 9)], M['coat'], lift=0.0, group='lapelR',
           vfun=lambda x, y: coat_wear(x, y))
    r.tube((70.5, S + 8), (70.0, S + 13), 0.7, 0.7, M['wood'], lift=0.3, group='pens')               # pens in the breast pocket
    r.tube((72.5, S + 9), (72.2, S + 13), 0.7, 0.7, M['copper'], group='pens')
    r.fixed(70.5, S + 7, QUILL[4]); r.fixed(72.5, S + 8, COPPER[6])
    r.poly([(68, S + 12), (75, S + 12.5), (74.6, S + 15), (68.3, S + 14.6)], M['coat'], lift=0.12, round_=0.3, group='pocket')
    for x in range(68, 75): r.darken(x, S + 15.6, 0.2)
    for (x, y, c) in ((57, S + 4, COPPER[6]), (56, S + 4, COPPER[4]), (58, S + 4, COPPER[3]), (57, S + 3, COPPER[5]), (57, S + 5, COPPER[2])):
        r.fixed(x, y, c)                                                                           # the Rust Choir's copper cog pin
    # neck: thin, in the head's shadow, mostly hidden by the shirt's high band collar
    r.tube((hx - 1, hy + 8), (hx - 1, S - 2), 2.6, 3.0, M['skin'], lift=-0.36, group='neck')
    r.poly([(hx - 5, S - 10), (hx + 3, S - 10), (hx + 3.6, S - 3), (hx - 5.6, S - 3)], M['shirt'], lift=-0.3, round_=0.95, group='band',
           vfun=lambda x, y: -0.14 if y == S - 6 else 0)
    r.fixed(hx - 1, S - 4, COPPER[5]); r.fixed(hx - 1, S - 3, COPPER[2])                           # the collar stud
    # ---- the upper arms, hanging to the elbows at her sides (elbows back and down, forearms forward to the desk)
    hand = HANDS[P['hand']]
    shL, shR = (50, S + 3), (74, S + 3)
    wr = (hand[0] - 1.5, hand[1] - 2)
    if P['hand'] in ('A', 'B', 'C'):
        elL = (45.5, S + 23.5)                    # writing: the elbow stays planted at her side, only the forearm sweeps the line
    else:
        elL = ik(shL, wr, 21.0, 14.0, lambda e: -e[0] + e[1] * 0.3)     # reaching: the elbow lifts out to the side, never forward
    wrR = (HAND_L[0] + 1.5, HAND_L[1] - 2)
    elR = ik(shR, wrR, 21.0, 14.0, lambda e: e[0] + e[1] * 0.3)
    for (sh, el, g, s) in ((shL, elL, 'armL', 1), (shR, elR, 'armR', -1)):
        r.ellipsoid(sh[0] - s * 0.6, sh[1] - 1, 4.4, 3.8, M['coat'], lift=0.06, group=g)            # the shoulder
        r.tube(sh, el, 4.6, 3.9, M['coat'], lift=0.06, group=g,
               folds=lambda u, sd, s=s: (-0.22 if u > 0.78 and sd * s > 0.25 else 0) + (-0.15 if abs(sd + s * 0.5) < 0.12 and 0.25 < u < 0.7 else 0)
                                        + (0.1 if abs(sd + s * 0.25) < 0.1 and 0.3 < u < 0.65 else 0))
    px, py = lerp(shR, elR, 0.84)                                                                  # a leather patch on her left elbow
    r.ellipsoid(px + 1.8, py, 2.0, 3.0, M['patch'], lift=-0.06, group='patch')
    for a in (-1.2, -0.4, 0.4, 1.2): r.fixed(px + 1.8 + math.cos(a) * 2.2, py + math.sin(a) * 3.2, WOOD[6])   # stitches
    seam(r, 'armL', 0.26); seam(r, 'armR', 0.26)
    head(r, P, hx, hy, LX, LY)
    desk(r)
    kit(r)
    hands(r, P, hand, wr, elL, wrR, elR)
    lamp_light(r, LX, LY, [0.24, 0.21, 0.26, 0.22][P['fl']], 82)
    return r.render()


def head(r, P, hx, hy, LX, LY):
    look = P['look']
    fcx, fcy, frx, fry = hx - 1, hy + 1, 8.0, 10.4
    ey = hy + 1                                                                                   # the eye line
    f0 = fcx - 1                                                                                  # features sit a pixel left: a slight turn
    # hair scraped back tight over the skull, streaks running back to the bun; clipped above the ears
    r.ellipsoid(hx, hy - 1.6, 8.6, 11.0, M['hair'], group='head', clip=lambda x, y: y < ey + 2,
                vfun=lambda x, y, u, w: (-0.22 if (x - (hx - 1) - (y - hy) * 0.35 * (x - hx) / 6) % 3 < 0.7 and w < 0.1 else 0) + (0.1 if w < -0.6 else 0))
    lv = (-0.62, -0.5, 0.6); ln = math.sqrt(sum(c * c for c in lv)); lv = tuple(c / ln for c in lv)   # the lamp, up and to her right
    face = set()
    for y in range(int(fcy - fry) - 1, int(fcy + fry) + 2):
        for x in range(int(fcx - frx) - 1, int(fcx + frx) + 2):
            u, w = (x + 0.5 - fcx) / frx, (y + 0.5 - fcy) / fry
            if w > 0.0: u /= max(0.26, 1 - w ** 1.35 * 0.74)                                       # a narrow jaw and chin
            d = u * u + w * w
            if d > 1: continue
            n = (u, w * 0.75, math.sqrt(max(0.0, 1 - d)))
            v = 0.1 + 0.95 * max(0.0, n[0] * lv[0] + n[1] * lv[1] + n[2] * lv[2])
            face.add((x, y))
            r.fixed(x, y, SKIN[max(1, min(7, 1 + int(v * 6.4)))])
    def fx(x, y, c): r.fixed(x, y, c)
    def sk(x, y, d):                                                                              # step a face pixel up/down the ramp
        e = r.buf.get((int(math.floor(x)), int(math.floor(y))))
        if e and e[3] in SKIN: fx(x, y, SKIN[max(0, min(8, SKIN.index(e[3]) + d))])
    # the hairline (a gentle widow's peak), the temples
    for x in range(int(fcx - 9), int(fcx + 10)):
        dx = abs(x + 0.5 - (f0 + 0.5))
        top = hy - 5.5 + dx * 0.34 - (0.6 if dx < 1 else 0)
        for y in range(int(fcy - fry) - 1, int(top) + 1):
            if (x, y) in face: fx(x, y, HAIR[2] if (x * 2 + y) % 5 else HAIR[3])
    # sockets, cheekbones, the hollows under them, the jaw's shaded side and its shadow on the neck
    for (x, y) in ((f0 - 1, ey - 1), (f0 + 1, ey - 1), (f0 - 5, ey + 1), (f0 + 4, ey + 1), (f0 + 5, ey + 1)): sk(x, y, -1)
    for (x, y) in ((f0 - 5, ey + 2), (f0 - 4, ey + 2), (f0 - 6, ey + 2)): sk(x, y, +1)
    for (x, y) in ((f0 - 5, ey + 4), (f0 - 4, ey + 5), (f0 - 5, ey + 5), (f0 - 4, ey + 4), (f0 + 5, ey + 4), (f0 + 5, ey + 5), (f0 + 4, ey + 6),
                   (f0 + 6, ey + 3), (f0 + 6, ey + 4), (f0 + 4, ey + 5)):
        sk(x, y, -2)
    for y in range(ey + 2, ey + 11):
        xs = [x for x in range(int(fcx), int(fcx + 10)) if (x, y) in face]
        if xs: sk(max(xs), y, -1); sk(max(xs) - 1, y, -1 if y > ey + 6 else 0)
    # goggles pushed up on the forehead: round copper eyepieces, violet lenses, a leather strap round the head
    gy = ey - 10
    EP = [' kkkk ', 'CWwwwc', 'CVVVVc', 'cvvvvc', ' cccc ']
    pal = {'k': COPPER[5], 'C': COPPER[4], 'c': COPPER[2], 'W': LENS[4] if look else LENS[3], 'w': LENS[2], 'V': LENS[1], 'v': LENS[0]}
    for gx in (f0 - 6, f0 + 2):
        for j, row in enumerate(EP):
            for i, ch in enumerate(row):
                if ch != ' ': fx(gx + i, gy + j, pal[ch])
    fx(f0, gy + 2, COPPER[4]); fx(f0 + 1, gy + 2, COPPER[3])                                       # the bridge
    for x in range(int(fcx - 10), int(f0 - 6)): fx(x, gy + 2, LEATH[2])
    for x in range(int(f0 + 8), int(fcx + 10)): fx(x, gy + 2, LEATH[1])
    for x in range(int(f0 - 5), int(f0 + 8)):
        if (x, gy + 5) in face: sk(x, gy + 5, -2)                                                  # the goggles' shadow on the brow
    # brows: thin, solid, arched toward the outer end; the near one lifts when she glances up
    for (x0, up, side) in ((f0 - 5, 0, -1), (f0 + 2, look, 1)):
        for k in range(4):
            x = x0 + k
            arch = 1 if (k in (1, 2) if side < 0 else k in (1, 2)) else 0
            fx(x, ey - 3 - arch - up, HAIR[1])
    # eyes: lids lowered over the work, or looking at you, narrow and sly
    for (ex0, wing) in ((int(f0 - 4), -1), (int(f0 + 2), 1)):
        wx = ex0 - 1 if wing < 0 else ex0 + 3
        if look and not P['blink']:
            for k in range(3): fx(ex0 + k, ey - 1, HAIR[0])
            fx(wx, ey, HAIR[1])
            for k in range(3): fx(ex0 + k, ey, EYEW)
            fx(ex0 + 1, ey, PUPIL)
            fx(ex0 + (0 if wing < 0 else 2), ey, SKIN[5] if wing < 0 else EYEW)
            for k in range(3): sk(ex0 + k, ey + 1, -1)
        else:
            drop = 1 if P['blink'] else 0
            for k in range(3): fx(ex0 + k, ey - 1 + drop, SKIN[6] if wing < 0 else SKIN[5])          # the lowered lid catches light
            for k in range(3): fx(ex0 + k, ey + drop, HAIR[0])
            fx(wx, ey + drop, HAIR[1])
            if not drop:
                for k in range(3): sk(ex0 + k, ey + 1, -1)
    # nose: long and thin, its shadow side away from the lamp, a light tip
    for y in range(ey, ey + 4): fx(f0, y, SKIN[6] if y < ey + 2 else SKIN[7])
    for y in range(ey, ey + 4): fx(f0 + 1, y, SKIN[3])
    fx(f0 + 1, ey + 4, SKIN[2]); fx(f0, ey + 4, SKIN[5]); fx(f0 - 1, ey + 4, SKIN[4]); fx(f0 + 2, ey + 4, SKIN[3])
    fx(f0 - 1, ey + 5, SKIN[3]); fx(f0 + 1, ey + 5, SKIN[2])
    # mouth: thin lips, the near corner drawn up in a sly half-smile
    my = ey + 7
    for dx in range(-2, 3): fx(f0 + dx, my, LIP[0])
    fx(f0 + 3, my - 1, LIP[0]); fx(f0 - 3, my, SKIN[3])
    if look: fx(f0 + 4, my - 1, SKIN[3])
    for dx in (-1, 0, 1): fx(f0 + dx, my + 1, LIP[2] if dx == -1 else LIP[1])
    sk(f0, my + 2, -1); fx(f0 - 1, my + 3, SKIN[6]); fx(f0, my + 3, SKIN[5])                       # under the lip, the chin
    for x in range(int(fcx - 6), int(fcx + 7)):                                                    # the jaw's shadow on the collar
        ys = [y for y in range(ey, ey + 14) if (x, y) in face]
        if ys: r.darken(x, max(ys) + 1, 0.3); r.darken(x, max(ys) + 2, 0.14)
    # the near ear; loose strands escaping the bun down both temples
    for (x, y, c) in ((fcx + 8, ey - 1, SKIN[4]), (fcx + 8, ey, SKIN[3]), (fcx + 8, ey + 1, SKIN[4]), (fcx + 9, ey, SKIN[2]),
                      (fcx + 9, ey - 1, SKIN[3]), (fcx + 8, ey + 2, SKIN[2])):
        fx(x, y, c)
    for k in range(11): fx(fcx + 7 + (k > 4) - (k > 9), ey - 5 + k, HAIR[3 if k % 3 else 4])
    for k in range(9): fx(fcx - 8 - (k > 2) + (k > 7), ey - 4 + k, HAIR[3 if k % 2 else 4])


def hands(r, P, hand, wr, elL, wrR, elR):
    # the forearms over the desk: frayed cuffs, the shirt cuff showing
    for (el, w, g, s) in ((elL, wr, 'foreL', 1), (elR, wrR, 'foreR', -1)):
        r.tube(el, w, 4.0, 3.3, M['coat'], lift=0.08, group=g, folds=lambda u, sd, s=s: -0.22 if u < 0.18 and sd * s > 0 else 0)
        r.tube(lerp(el, w, 0.78), lerp(el, w, 0.98), 3.7, 3.7, M['coat'], lift=0.2, jag=0.2, group=g)
        seam(r, g, 0.22)
    # her left hand flat on the sheet: back of the hand, four long fingers spread toward the viewer, the thumb inward
    hx2, hy2 = HAND_L
    r.tube((wrR[0], wrR[1] - 0.5), (hx2 + 0.5, hy2 - 0.5), 2.0, 2.0, M['shirt'], group='cuffR')
    r.ellipsoid(hx2, hy2 + 0.5, 3.7, 2.7, M['skin'], group='handR')
    for k in range(4):
        x0 = hx2 - 2.6 + k * 1.8
        r.tube((x0, hy2 + 2), (x0 - 0.5 - k * 0.1, hy2 + 6.2 - abs(k - 1.4) * 0.6), 0.8, 0.7, M['skin'], group='fingR')
    r.tube((hx2 - 3.2, hy2 + 0.5), (hx2 - 6.6, hy2 + 2.2), 1.0, 0.8, M['skin'], group='fingR')
    for k in range(4): r.darken(hx2 - 2.0 + k * 1.8, hy2 + 6.8 - abs(k - 1.4) * 0.6, 0.2)          # finger shadows on the paper
    for k in range(3): r.darken(hx2 - 1.8 + k * 1.8, hy2 - 0.6, -0.12)                            # knuckles in the light
    # the quill: the nib on the sheet, the shaft up toward her right shoulder, a pale vane
    hx1, hy1 = hand
    nib = NIBS.get(P['hand'], (hx1 + 3, hy1 + 3))
    ang = {'dip': (-0.12, -1), 'lift': (-0.2, -1)}.get(P['hand'], (-0.3, -1))
    L_ = 21; al = math.hypot(*ang); ux, uy = ang[0] / al, ang[1] / al; top = (nib[0] + ux * L_, nib[1] + uy * L_)
    vane_l, vane_r = [], []
    for i in range(13):                                                                           # a leaf: narrow, wider on the outer side
        t = 0.34 + i / 12 * 0.66
        cx_, cy_ = nib[0] + ux * L_ * t, nib[1] + uy * L_ * t
        wv = math.sin(min(1.0, (t - 0.34) / 0.62) * math.pi * 0.92)
        vane_l.append((cx_ + uy * 1.2 * wv, cy_ - ux * 1.2 * wv))
        vane_r.append((cx_ - uy * 2.4 * wv, cy_ + ux * 2.4 * wv))
    r.poly(vane_l + vane_r[::-1], M['quill'], lift=0.42, round_=0.7, group='quill',
           vfun=lambda x, y: -0.12 if (x + y * 2) % 7 == 0 else 0)                                 # a few split barbs
    r.stroke([lerp(nib, top, t / 22) for t in range(23)], 0.8, color=QUILL[2], group='rachis')     # the shaft
    r.fixed(top[0], top[1], QUILL[4])
    r.fixed(nib[0], nib[1], INKC[0])
    # the writing hand: shirt cuff, the hand on its side round the shaft, the thumb over it, ink on the fingertips
    r.tube((wr[0], wr[1] - 0.5), (hx1 - 0.5, hy1 - 0.5), 2.0, 2.0, M['shirt'], group='cuffL')
    for k in range(3):                                                                            # the curled fingers under the hand
        r.ellipsoid(hx1 - 1.6 + k * 1.5, hy1 + 2.0 + k * 0.3, 1.3, 1.2, M['skin'], lift=-0.12, group='curlL')
    r.ellipsoid(hx1, hy1, 3.6, 2.7, M['skin'], group='handL', rot=-0.35, lift=0.06)
    for k in range(3): r.darken(hx1 - 2.2 + k * 1.5, hy1 - 2.0 + k * 0.4, -0.14)                  # the knuckles in the light
    r.tube((hx1 + 1.6, hy1 + 1.0), (nib[0] - 0.4, nib[1] - 0.9), 0.95, 0.8, M['skin'], group='indexL')
    r.tube((hx1 - 0.8, hy1 - 1.2), (hx1 + 2.6, hy1 + 0.2), 1.05, 0.9, M['skin'], lift=0.12, group='thumbL')
    r.fixed(nib[0] - 0.7, nib[1] - 1.2, STAIN); r.fixed(hx1 - 1.6, hy1 + 3.0, STAIN)


if __name__ == '__main__':
    os.makedirs(f'{OUT}/ravla', exist_ok=True)
    frames = [ravla(p) for p in POSE]
    sheet = Image.new('RGBA', (W * len(frames), H), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        im.save(f'{OUT}/ravla/{i}.png'); sheet.paste(im, (i * W, 0))
    sheet.save(f'{OUT}/ravla.png')
    used = set()
    for im in frames: used |= {px[:3] for px in im.getdata() if px[3]}
    ALL = ([INK, WARMOUT, TENTOUT] + COAT + VEST + SHIRT + SKIN + HAIR + COPPER + TENT + WOOD + LEATH + VELVET + PAPER + QUILL
           + GLASSG + GLASSA + GLASSV + INKC + SEAL + LENS + FLAME + LIP + SUCKER + [CORK, IRIS, PUPIL, EYEW, STAIN])
    seen, rows = set(), []
    for c in ALL + sorted(used):
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/ravla.gpl', 'w').write('GIMP Palette\nName: ravla\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT, len(rows), 'colours')
