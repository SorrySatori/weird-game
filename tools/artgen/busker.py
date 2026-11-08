"""The busker of the Town Square (TownSquareScene) and his drum, redrawn with the character renderer (rig.py, the Edgar
quality bar) after the old AI image busker.png (kept: ScraperAmbraScene's cutscene still shows it).

A street musician on a worn four-legged stool, turned a little toward the viewer's right, playing an old acoustic guitar
held the way a guitar is held -- the waist on his right thigh, the neck rising to the viewer's right, the fretting hand
wrapped round the neck from under it, the strumming forearm laid over the lower bout. His head is a carved ball of pale
wood (the grain runs round it, a dry crack, two small dark eye holes and a short cut for a mouth) under a brown felt
fedora with a band; a worn brown jacket with a patched elbow, a knitted ochre scarf, brown trousers, scuffed boots, and
jointed wooden hands. Beside him (the viewer's right) his companion: a little rope-tensioned drum on four spindly
jointed iron legs, the two round sound-holes in its shell reading as eyes; it keeps time.

176x144 frames, soles (boots, stool, the drum's feet) on row 141; an 8-frame idle, two strums per beat:
  0 down-strum, the head dips on the beat, the drum sinks on its legs          1 the hand swings back, his toe lifts
  2 up-strum, the drum rises and taps a foot                                     3 the hand comes up, his toe taps down
  4 down-strum on the next chord (the fretting hand slides down the neck), dip   5 back, toe up
  6 up-strum, the drum taps its other foot, the skin still shivering             7 up, toe down
  8 (not in the idle) the dialog portrait: frame 0 without the drum, his head moved onto the frame's centre line
python3 busker.py <outdir>  ->  busker.png (8 idle frames + the portrait frame) + busker/<n>.png + busker.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK, h32, make_noise
import rig
from rig import Rig, Mat, norm
from feral_toast import ik, lerp
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
W, H = 176, 144
FLOOR = 141
R = ramp
# muted, earthy ramps: cool in the shadows, warm in the light
HEADW  = R('#251a12 #36281b #4a3825 #5f4a32 #745d40 #88704f #9b8361 #ad9673 #bea986 #cdbb99')   # pale carved wood
HAT    = R('#120b07 #1c110b #27170f #331f14 #40281a #4e3220 #5c3c27 #6b472f #7b5338')
BAND   = R('#0d0908 #17110e #221915 #2e221c')
JACKET = R('#110b08 #1a110c #241811 #2f1f16 #3b281c #483122 #553b29 #634631 #72513a #825d43')
SHIRT  = R('#2a2a24 #3e3d34 #545244 #6a6755 #7f7b66')
SCARF  = R('#1b0d0b #2a1310 #3a1b16 #4b241c #5c2e22 #6d392a #7e4533 #8e523d')                    # faded oxblood knit
TROU   = R('#0f0b09 #17110d #201812 #2a2018 #35281e #403024 #4c3a2b')
BOOT   = R('#0c0807 #160f0b #21160f #2d1e14 #3a271a #493221 #593d29')
TOP    = R('#2e1b0d #452912 #5d3818 #74481f #8a5927 #9e6a31 #af7c3e #bd8d4e #c99f63')       # the spruce top, yellowed
SIDES  = R('#160b06 #24120a #33190d #432211 #542b16 #66361c #774122')
BOARD  = R('#0e0806 #170d09 #21130d #2b1a12 #362217')
STRING = R('#4c4840 #6e695e #948e80 #b9b2a0 #d6cfbb')
STOOL  = R('#150f0a #20170f #2d2016 #3a2a1d #483425 #573f2d #674b36 #775840 #88664b')
SHELL  = R('#151509 #1f1f0f #2a2a15 #36351b #434122 #514e2a #605c33 #706b3d #827c49 #948d57')   # olive khaki
SKIN_D = R('#423b2a #5a523b #72694d #8b815f #a39871 #b8ad84 #c9bf98')                              # the vellum head
ROPE   = R('#2b2417 #3f3522 #55482f #6c5d3d #84724c #9b8a5d')
IRON   = R('#0e100f #171a18 #222622 #2e332e #3b413b #4b5149 #5e645a')
BRASS  = R('#2a1d0b #463212 #654a1c #866428 #a67f38 #c29c52')
WARMOUT = (30, 20, 17)
HOLE   = (20, 14, 10)
PICK   = (196, 170, 118)

rig.TEX['tweedb'] = lambda x, y: ((rig.nF(x * 1.7, y * 1.7) - 0.5) * 0.12 + (rig.nM(x * 1.1, y * 1.1) - 0.5) * 0.18
                                  + (rig.nL(x * 0.7 + 40, y * 0.7) - 0.5) * 0.30 + (0.03 if (x + 2 * y) % 3 == 0 else -0.012)
                                  - (0.12 if rig.nL(x * 2.3 + 90, y * 2.3) > 0.78 else 0))                 # worn wool, old stains
rig.TEX['carved'] = lambda x, y: (rig.nF(x * 0.5, y * 1.9) - 0.5) * 0.12 + (rig.nM(x * 1.3, y * 1.3) - 0.5) * 0.06
rig.TEX['felt'] = lambda x, y: (rig.nM(x * 1.6, y * 1.6) - 0.5) * 0.12 + (rig.nF(x * 2.2, y * 2.2) - 0.5) * 0.06
rig.TEX['knit'] = lambda x, y: (0.06 if (x + (y // 2)) % 3 == 0 else -0.03) + (rig.nF(x * 1.5, y * 1.5) - 0.5) * 0.08
def mat(rmp, tex, amb, spec=0.0): return Mat(rmp, tex, amb, spec, outline=WARMOUT)
M = {'head': mat(HEADW, 'carved', 0.26, 0.12), 'hand': mat(HEADW, 'carved', 0.22, 0.1), 'hat': mat(HAT, 'felt', 0.2, 0.05),
     'band': mat(BAND, 'fabric', 0.22), 'jacket': mat(JACKET, 'tweedb', 0.18), 'shirt': mat(SHIRT, 'fabric', 0.24),
     'scarf': mat(SCARF, 'knit', 0.22), 'trou': mat(TROU, 'fabric', 0.2), 'boot': mat(BOOT, 'leather', 0.2, 0.6),
     'top': mat(TOP, 'wood', 0.3, 0.35), 'sides': mat(SIDES, 'wood', 0.24, 0.3), 'board': mat(BOARD, 'wood', 0.22),
     'stool': mat(STOOL, 'wood', 0.22, 0.1), 'shell': mat(SHELL, 'wood', 0.22, 0.15), 'vellum': mat(SKIN_D, 'leather', 0.3),
     'rope': mat(ROPE, 'fabric', 0.26), 'iron': mat(IRON, 'metal', 0.2, 0.7), 'brass': mat(BRASS, 'metal', 0.24, 0.9),
     'patch': mat(TROU, 'leather', 0.22, 0.2)}

# strum: the hand's offset across the strings (+ = down past them); chord: the fretting hand's place on the neck
POSE = [dict(strum=5, nod=1, toe=0, chord=0, dy=2, tap=0, ripple=1), dict(strum=1, nod=0, toe=1, chord=0, dy=1, tap=0, ripple=2),
        dict(strum=-5, nod=0, toe=1, chord=0, dy=0, tap=1, ripple=0), dict(strum=-2, nod=0, toe=0, chord=0, dy=1, tap=0, ripple=0),
        dict(strum=5, nod=1, toe=0, chord=1, dy=2, tap=0, ripple=1), dict(strum=1, nod=0, toe=1, chord=1, dy=1, tap=0, ripple=2),
        dict(strum=-5, nod=0, toe=1, chord=1, dy=0, tap=2, ripple=1), dict(strum=-2, nod=0, toe=0, chord=1, dy=1, tap=0, ripple=0)]

CX = 52                                              # the busker's axis
SH_N, SH_F = (34.0, 59.0), (68.5, 58.5)              # the near (strumming, viewer-left) and far shoulder
GANG = math.radians(-31)                             # the guitar's neck angle (rising to the viewer's right)
GO = (51.0, 88.0)                                    # the sound hole's centre


class Guitar:
    """u along the neck toward the headstock, v across it (+v = below the neck)"""
    def __init__(s, O, ang):
        s.O, s.U = O, (math.cos(ang), math.sin(ang)); s.V = (-s.U[1], s.U[0]); s.ang = ang
    def P(s, u, v=0.0): return (s.O[0] + s.U[0] * u + s.V[0] * v, s.O[1] + s.U[1] * u + s.V[1] * v)
    def local(s, x, y):
        px, py = x + 0.5 - s.O[0], y + 0.5 - s.O[1]
        return px * s.U[0] + py * s.U[1], px * s.V[0] + py * s.V[1]
G = Guitar(GO, GANG)
BOUTS = [(-17.0, 0.0, 13.4, 16.8), (2.0, 0.0, 10.4, 12.6)]   # (u, v, ru, rv): the lower and the upper bout
NECK0, NUT, HEADL = 12.0, 46.0, 10.0


def guitar(r):
    """the old flat-top: a yellowed spruce top with a dark binding, a rosette round the sound hole, a scratched
    pickguard, the bridge with its pins, a rosewood fretboard with frets and dots, the headstock with pegs, strings"""
    ob, on = r.new('guitar'), r.new('guitar')
    xs = [G.P(u, v)[0] for u in (-30, NUT + HEADL + 1) for v in (-17, 17)]
    ys = [G.P(u, v)[1] for u in (-30, NUT + HEADL + 1) for v in (-17, 17)]
    for y in range(int(min(ys)) - 1, int(max(ys)) + 2):
        for x in range(int(min(xs)) - 1, int(max(xs)) + 2):
            u, v = G.local(x, y)
            best = None
            for (cu, cv, ru, rv) in BOUTS:
                d = ((u - cu) / ru) ** 2 + ((v - cv) / rv) ** 2
                if d <= 1 and (best is None or d < best[0]): best = (d, (u - cu) / ru, (v - cv) / rv)
            if best:
                d, nu, nv = best
                if d > 0.88:                                                       # the binding / the side seen at the rim
                    c = SIDES[2] if nv > 0.2 else (SIDES[5] if nv < -0.5 else SIDES[3])
                    if d > 0.95 and nv > 0.3: c = SIDES[1]
                    if 0.88 < d < 0.91 and nv < 0: c = TOP[8]                       # the pale binding catching light
                    r.put(x, y, None, 0, ob, c); continue
                hole = math.hypot(u, v)
                if hole < 4.0: r.put(x, y, None, 0, ob, HOLE if hole < 3.2 or v > 1 else SIDES[1]); continue
                if hole < 5.6:                                                     # the rosette: two rings
                    c = SIDES[2] if 4.5 < hole < 5.0 else TOP[3]
                    r.put(x, y, None, 0, ob, c); continue
                if -19.2 < u < -16.2 and abs(v) < 6.4:                             # the bridge, its pins
                    c = BOARD[3] if u > -16.6 else BOARD[1]
                    if abs(u + 18.4) < 0.5 and int(v + 7) % 2 == 0 and abs(v) < 4.5: c = HEADW[7]
                    r.put(x, y, None, 0, ob, c); continue
                n = norm((G.U[0] * nu * 0.4 + G.V[0] * nv * 0.4, G.U[1] * nu * 0.4 + G.V[1] * nv * 0.4, 1.0))
                val = r.shade(M['top'], n)
                if (u + 0.5) ** 2 / 30 + (v - 8.8) ** 2 / 8 < 1 and v > 5.6:       # the pickguard, worn through in a patch
                    val2 = val - 0.12 + (0.1 if h32(x, y, 3) % 6 == 0 else 0)
                    r.put(x, y, M['sides'], val2, ob); continue
                if -13 < u < -4 and -5 < v < 6 and h32(x, y, 9) % 4 == 0: val -= 0.07                  # strummed thin
                val += (0.04 if int((v + 20) * 0.9) % 3 == 0 else 0) - (0.08 if d > 0.8 else 0)       # the grain, the rim's shade
                r.put(x, y, M['top'], val, ob)
            elif NECK0 <= u <= NUT and abs(v) <= 2.9:
                if abs(v) <= 2.2:
                    fret = (NUT - u) % 4.6 < 0.7 and u > NECK0 + 1
                    dot = int((NUT - u) // 4.6) in (2, 4, 6) and abs(v) < 0.6 and 1.8 < (NUT - u) % 4.6 < 3.0
                    if fret: r.put(x, y, None, 0, on, STRING[1])
                    elif dot: r.put(x, y, None, 0, on, HEADW[5])
                    else: r.put(x, y, M['board'], r.shade(M['board'], (0, -0.2, 0.98)), on)
                else: r.put(x, y, M['sides'], r.shade(M['sides'], (0, -0.4 if v < 0 else 0.5, 0.85)), on)
            elif NUT < u <= NUT + HEADL and abs(v) <= 3.4 - (u - NUT) * 0.06:
                c = r.shade(M['sides'], (0, -0.3, 0.95)) - (0.14 if abs(v) > 2.6 else 0) - (0.2 if u < NUT + 0.8 else 0)
                r.put(x, y, M['sides'], c, on)
    for k in range(2):                                                             # the nut, light bone
        p = G.P(NUT + 0.4, -1.5 + k * 3); r.fixed(p[0], p[1], HEADW[7], on)
    for u in (NUT + 2.6, NUT + 5.4, NUT + 8.2):                                     # the tuning pegs
        for sv in (-4.2, 4.2):
            p = G.P(u, sv); r.fixed(p[0], p[1], STRING[3] if sv < 0 else STRING[1], on)
    for k in range(3):                                                             # strings: bright over the top, dim on the board
        sv = -1.4 + 1.4 * k
        u = -17.6
        while u < NUT:
            p = G.P(u, sv)
            e = r.buf.get((int(p[0]), int(p[1])))
            if e and u > NECK0:
                if k == 1: r.fixed(p[0], p[1], STRING[0], on)
            elif e and math.hypot(u, sv) > 3.3: r.fixed(p[0], p[1], STRING[3] if k == 1 else STRING[2], on)
            u += 0.9


def wood_hand_fist(r, c, ang, g):
    """a carved fist seen from the back: the block of the palm, four jointed fingers curled under it, the thumb on top"""
    x, y = c
    r.ellipsoid(x, y, 3.9, 3.2, M['hand'], rot=ang, group=g)
    for k in range(4):
        fx, fy = x - 2.5 + k * 1.7, y + 2.8 - abs(k - 1.5) * 0.3
        r.ellipsoid(fx, fy, 1.0, 1.3, M['hand'], lift=-0.04, group=g + 'f%d' % k)
        seam(r, g + 'f%d' % k, 0.18)
    for k in range(3): r.darken(x - 1.7 + k * 1.7, y - 0.4, -0.12)                  # the knuckles' carved ridges
    r.tube((x - 2.8, y - 1.9), (x + 1.4, y - 2.8), 1.15, 1.0, M['hand'], lift=0.1, group=g + 't')
    seam(r, g + 't', 0.2)
    r.fixed(x + 2.2, y - 2.6, HEADW[3])                                              # the thumb's joint


def sleeve(r, a, b, ra, rb, g, folds=True, lift=0.0, bag=0.0):
    """a jacket sleeve: a little baggy in the middle, creases at the bend, a lit ridge"""
    r.tube(a, b, ra, rb, M['jacket'], lift=lift, group=g, bulge=(lambda t: bag * math.sin(math.pi * t)) if bag else None,
           folds=(lambda u, sd: (-0.26 if (0.6 < u < 0.66 or 0.8 < u < 0.85) and abs(sd) < 0.75 else 0)
                  + (0.1 if 0.15 < u < 0.5 and -0.6 < sd < -0.3 else 0) - (0.12 if sd > 0.65 else 0)) if folds else None)


def busker(P):
    r = Rig(W, H)
    nod = P['nod']
    # ------------------------------------------------------------------------------------------------ the stool
    for (top, foot) in (((41.0, 103.0), (37.5, FLOOR - 1)), ((61.0, 103.0), (64.5, FLOOR - 1))):          # back legs
        r.tube(top, foot, 1.5, 1.3, M['stool'], lift=-0.25, group='stoolB')
    r.tube((39.0, 123), (63.0, 123), 1.0, 1.0, M['stool'], lift=-0.3, group='rung')
    for (top, foot) in (((44.5, 105.0), (41.0, FLOOR - 1.2)), ((58.0, 105.0), (61.5, FLOOR - 1.2))):       # front legs
        r.tube(top, foot, 1.8, 1.6, M['stool'], group='stoolF', folds=lambda u, sd: 0.12 if sd < -0.4 else 0)
    r.tube((42.0, 129), (60.5, 129), 1.1, 1.1, M['stool'], lift=-0.12, group='rung2')
    r.poly([(35.5, 100.5), (66.5, 100.5), (67.5, 104.5), (34.5, 104.5)], M['stool'], round_=0.4, tilt=0.3, group='seat',
           vfun=lambda x, y: (0.18 if y <= 101 else 0) - (0.22 if y >= 104 else 0) - (0.12 if h32(x, 7) % 7 == 0 else 0))
    # ------------------------------------------------------------------------------------------------ the legs: seated, knees apart
    toe = P['toe']
    for (hip, knee, ank, sx, g) in (((45.0, 98.0), (44.0, 105.5), (39.5, 132.0), -1, 'legN'),
                                    ((61.0, 98.0), (75.5, 102.5), (78.0, 132.0), 1, 'legF')):
        r.tube(hip, knee, 7.0, 6.2, M['trou'], group=g + 't',
               folds=lambda u, sd: (-0.24 if 0.15 < sd < 0.35 and u > 0.35 else 0) + (0.14 if sd < -0.45 else 0))  # the lap lit on top
        r.ellipsoid(knee[0] + sx * 0.8, knee[1] - 0.2, 6.0, 5.0, M['trou'], lift=0.1, group=g + 't')       # the knee
        r.tube((knee[0], knee[1] + 2), ank, 5.4, 4.5, M['trou'], group=g + 's',
               folds=lambda u, sd, sx=sx: (-0.24 if (0.08 < u < 0.14 or 0.7 < u < 0.74 or 0.86 < u < 0.9) and abs(sd) < 0.8 else 0)
                                          + (0.1 if sd < -0.5 else 0))
        seam(r, g + 's', 0.2)
        if sx > 0:                                                                                         # a darned patch on the knee
            r.poly([(knee[0] - 2.5, knee[1] - 3), (knee[0] + 3.5, knee[1] - 3.5), (knee[0] + 4, knee[1] + 2.5), (knee[0] - 2, knee[1] + 3)],
                   M['patch'], lift=0.12, round_=0.5, group='kneepatch', vfun=lambda x, y: -0.1 if (x + y) % 3 == 0 else 0)
            for (x, y) in ((knee[0] - 2.5, knee[1] - 1), (knee[0] - 2.4, knee[1] + 1.5), (knee[0] + 1, knee[1] - 3.6), (knee[0] + 4, knee[1])):
                r.fixed(x, y, TROU[6])
        lift_ = 2 if (toe and sx > 0) else 0                                                               # the far foot taps
        bx = ank[0] + sx * 2.0
        r.tube((ank[0], ank[1] - 1), (ank[0] + sx * 0.5, FLOOR - 4.5), 4.8, 4.6, M['boot'], group=g + 'b')
        r.poly([(bx - 6.5, FLOOR - 6.5 - lift_ * 0.4), (bx + 4.0 + sx * 3, FLOOR - 4.8 - lift_), (bx + 5.8 + sx * 3, FLOOR - 1.5 - lift_),
                (bx + 4.0 + sx * 3, FLOOR - lift_), (bx - 6.5, FLOOR)], M['boot'], round_=0.6, tilt=-0.4, group=g + 'b',
               vfun=lambda x, y, lf=lift_: (0.2 if y <= FLOOR - 5 - lf else 0) - (0.25 if y >= FLOOR - 1 - lf * 0.5 else 0))
        r.fixed(bx + 2 + sx * 3, FLOOR - 4 - lift_, BOOT[6]); r.fixed(bx + 3 + sx * 3, FLOOR - 4 - lift_, BOOT[5])   # a scuffed toe cap
        for x in range(int(bx - 6), int(bx + 6 + sx * 3)): r.fixed(x, FLOOR - (lift_ if x > bx + 1 else 0), BOOT[0])   # the sole
    # ------------------------------------------------------------------------------------------------ the torso: slouched, broad
    def jacket_v(x, y):
        v = (rig.nL(x * 0.9 + 5, y * 0.9) - 0.5) * 0.12
        if y > 70 and (x - 40) % 9 == 0: v -= 0.2                                                          # vertical drapes
        if 61 < y < 66 and x > 62: v -= 0.14                                                                # under the far shoulder
        if y > 92: v -= (y - 92) * 0.02                                                                     # the hem in the lap's shadow
        return v + (CX - x) * 0.004
    r.poly([(31.5, 65), (36, 57.5), (45, 54.5), (59, 54.5), (67.5, 57), (71, 64), (71.5, 82), (72.5, 99), (60, 101.5), (40, 101.5), (32.5, 99), (31.5, 82)],
           M['jacket'], round_=0.85, group='torso', vfun=jacket_v)
    r.poly([(47.5, 54.5), (57.0, 54.5), (55, 73), (50, 73)], M['shirt'], lift=-0.12, group='shirt',
           vfun=lambda x, y: -0.15 if x in (52, 53) and y > 58 else 0)
    for (pts, g) in (([(43, 55), (49, 55), (52.5, 73), (49.0, 82), (44.0, 67)], 'lapelN'),
                     ([(62, 55), (56, 55), (52.6, 73), (56.0, 81), (61.0, 67)], 'lapelF')):
        r.poly(pts, M['jacket'], lift=0.12 if g == 'lapelN' else 0.0, round_=0.5, group=g, vfun=lambda x, y: jacket_v(x, y) * 0.6)
        seam(r, g, 0.24)
    r.fixed(53, 76, BRASS[3]); r.fixed(53, 77, BRASS[1])                                                    # a button
    r.poly([(61, 67), (66, 66.5), (66, 68.5), (61, 69)], M['jacket'], lift=0.1, round_=0.4, group='pocket')  # breast pocket flap
    seam(r, 'pocket', 0.24)
    # the scarf: wound round the neck, one knitted end over the chest with a fringe
    r.ellipsoid(CX + 1.5, 52.5 + nod * 0.5, 10.5, 4.6, M['scarf'], group='scarfw',
                vfun=lambda x, y, u, w: -0.22 if (x + y) % 4 == 0 and abs(w) > 0.35 else 0)
    r.poly([(44.5, 54), (51, 54.5), (49.5, 70), (44.0, 71)], M['scarf'], lift=0.04, round_=0.7, group='scarfe',
           vfun=lambda x, y: -0.18 if y in (59, 64) else 0)
    for k in range(5): r.fixed(44 + k * 1.2, 71 + (k % 2), SCARF[3 + (k % 2)])                              # the fringe
    seam(r, 'scarfe', 0.24)
    # ------------------------------------------------------------------------------------------------ the head
    head(r, P)
    # ------------------------------------------------------------------------------------------------ the fretting arm (far side)
    u_ch = (34.0, 29.0)[P['chord']]
    palm = G.P(u_ch, 4.6)
    el = ik(SH_F, palm, 20.0, 18.0, lambda e: e[1] + e[0] * 0.4)                      # the elbow hangs low at his side
    r.ellipsoid(SH_F[0] - 1.0, SH_F[1] + 1.5, 5.4, 4.6, M['jacket'], lift=0.0, group='armF')               # the shoulder
    sleeve(r, SH_F, el, 6.2, 5.2, 'armF', bag=0.8)
    wr = lerp(el, palm, 0.78)
    sleeve(r, el, wr, 5.2, 4.4, 'foreF', folds=False)
    r.tube(lerp(el, palm, 0.66), wr, 4.6, 4.6, M['jacket'], lift=0.16, group='cuffF')                       # the turned-back cuff
    seam(r, 'armF', 0.2); seam(r, 'foreF', 0.22); seam(r, 'cuffF', 0.2)
    r.tube(wr, palm, 1.8, 2.1, M['hand'], group='wristF')
    r.ellipsoid(palm[0], palm[1], 3.6, 2.9, M['hand'], rot=GANG, group='palmF')
    th = G.P(u_ch + 1.6, -3.2)
    r.ellipsoid(th[0], th[1], 1.5, 1.3, M['hand'], lift=0.1, group='thumbF')                                  # the thumb over the top
    # ------------------------------------------------------------------------------------------------ the guitar
    guitar(r)
    for k, du in enumerate((-2.2, 0.0, 2.2)):                                                              # fingers on the frets
        a, b = G.P(u_ch + du, 3.6), G.P(u_ch + du - 0.3, -0.4 - (k == 1) * 0.6)
        r.tube(a, b, 1.0, 0.85, M['hand'], lift=0.06, group='fingF%d' % k)
        seam(r, 'fingF%d' % k, 0.22)
        r.fixed(b[0], b[1], HEADW[2])
    # ------------------------------------------------------------------------------------------------ the strumming arm (near side)
    elbow = G.P(-16.0, -15.8)                                                         # resting on the lower bout's edge
    hand = G.P(-7.5, P['strum'] * 1.0)
    r.ellipsoid(SH_N[0] + 1.0, SH_N[1] + 1.5, 5.8, 4.8, M['jacket'], lift=0.08, group='armN')
    sleeve(r, SH_N, elbow, 6.4, 5.6, 'armN', bag=0.9)
    pe = lerp(SH_N, elbow, 0.86)                                                     # a leather patch on the elbow
    r.ellipsoid(pe[0] - 1.6, pe[1], 2.6, 3.2, M['patch'], lift=-0.05, group='patch')
    for a_ in (-1.4, -0.5, 0.5, 1.4): r.fixed(pe[0] - 1.6 + math.cos(a_ + 3.14) * 2.8, pe[1] + math.sin(a_) * 3.3, JACKET[7])
    seam(r, 'armN', 0.26)
    wr2 = lerp(elbow, hand, 0.74)
    r.tube(elbow, wr2, 5.4, 4.5, M['jacket'], lift=0.1, group='foreN',
           folds=lambda u, sd: (-0.24 if u < 0.16 and sd > 0 else 0) + (-0.2 if (0.42 < u < 0.47) and abs(sd) < 0.7 else 0) + (0.1 if sd < -0.5 else 0))
    r.tube(lerp(elbow, hand, 0.62), wr2, 4.9, 4.9, M['jacket'], lift=0.22, group='cuffN')
    seam(r, 'foreN', 0.26); seam(r, 'cuffN', 0.22)
    r.tube(wr2, hand, 1.9, 2.2, M['hand'], group='wristN')
    wood_hand_fist(r, hand, GANG + 0.6, 'handN')
    r.fixed(hand[0] + 2.0, hand[1] + 3.4, PICK); r.fixed(hand[0] + 2.0, hand[1] + 4.4, mix(PICK, HOLE, 0.4))  # the pick
    # ------------------------------------------------------------------------------------------------ the drum
    drum(r, P)
    im = r.render()
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y] == (18, 14, 12, 255): px[x, y] = WARMOUT + (255,)
    return im


def head(r, P):
    nod = P['nod']
    hx, hy, rad = 54.0, 37.0 + nod, 11.6
    r.tube((hx - 0.5, hy + 8), (hx - 0.5, 53), 2.3, 2.6, M['head'], lift=-0.3, group='neck')               # a wooden dowel of a neck
    # the ball: the grain rings round it, darker where the brim shades it, a dry crack
    def grain(x, y, u, w):
        g = (y - hy) * 0.9 + (x - hx) ** 2 * 0.04
        return (-0.07 if int(g + 40) % 5 == 0 and u < 0.5 else 0) + (-0.05 if w < -0.2 and u < 0.3 else 0)
    r.ellipsoid(hx, hy, rad, rad * 0.97, M['head'], group='head', vfun=grain)
    top = int(hy - rad)
    for x in range(int(hx - rad), int(hx + rad) + 1):                                 # the brim's shadow over the upper face
        for y in range(top, int(hy - 4)):
            e = r.buf.get((x, y))
            if e and e[0] is M['head']: e[1] -= 0.2 if y < hy - 6 else 0.1
    ey = int(round(hy))
    fx = int(hx) + 1                                                                    # the face sits a little to the right: he's turned
    for (ex, ht) in ((fx - 7, 4), (fx + 3, 4)):                                         # the eye holes, bored deep
        for dy in range(-1, ht - 1):
            r.fixed(ex, ey + dy, HOLE); r.fixed(ex + 1, ey + dy, HOLE)
        r.fixed(ex, ey + ht - 1, HEADW[8]); r.fixed(ex + 1, ey + ht - 1, HEADW[7])     # the lit lower lip of the hole
        r.fixed(ex - 1, ey - 1, HEADW[3]); r.fixed(ex + 2, ey, HEADW[4])
    for dx in range(-3, 1): r.fixed(fx - 1 + dx, ey + 7, HEADW[1])                        # the mouth: one short cut
    for dx in range(-3, 1): r.fixed(fx - 1 + dx, ey + 8, HEADW[6])
    for (x, y) in ((hx - 9, hy - 3), (hx - 8, hy - 2), (hx - 8, hy - 1), (hx - 7, hy)):
        r.fixed(x, y, HEADW[2]); r.fixed(x + 1, y, HEADW[6])                            # a dry crack, its lit edge
    hat(r, hx, hy)


def hat(r, hx, hy):
    """a brown felt fedora, the crown pinched, a dark band, the brim snapped down at the front"""
    by = hy - 7.5
    r.ellipsoid(hx - 0.5, by + 0.5, 17.2, 3.8, M['hat'], lift=-0.1, group='brim',
                vfun=lambda x, y, u, w: (0.12 if w < -0.3 else -0.12 if w > 0.5 else 0) + (-0.2 if abs(u) > 0.88 else 0))
    crown = [(hx - 9.5, by), (hx - 9.2, by - 7), (hx - 7.5, by - 11.5), (hx - 3, by - 13.2), (hx + 2.5, by - 13.5),
             (hx + 7.0, by - 12.0), (hx + 9.0, by - 7.5), (hx + 9.8, by)]
    def dent(x, y):
        v = 0.0
        if abs(x - hx) < 1.0 and y < by - 6: v -= 0.25                                  # the centre crease
        if y < by - 10 and abs(x - hx) < 5: v -= 0.06
        return v
    r.poly(crown, M['hat'], round_=0.9, group='crown', vfun=dent)
    r.poly([(hx - 9.6, by - 3.6), (hx + 9.9, by - 3.6), (hx + 9.9, by - 0.6), (hx - 9.6, by - 0.6)], M['band'], round_=0.9, group='band')
    r.fixed(hx - 7, by - 2.6, BAND[3]); r.fixed(hx - 6, by - 2.6, BAND[3])
    r.poly([(hx - 15.5, by + 1.0), (hx + 15.5, by + 1.0), (hx + 12, by + 3.6), (hx - 12, by + 3.6)], M['hat'], lift=0.08, round_=0.6,
           tilt=-0.5, group='brimF', vfun=lambda x, y: -0.15 if y >= by + 3 else 0.05)
    for x in range(int(hx - 12), int(hx + 12)):
        if h32(x, 5) % 5 == 0: r.darken(x, by + 2, 0.12)                                  # the brim worn through


def drum(r, P):
    """the companion: a rope-tensioned drum on four jointed iron legs; the two sound-holes are its eyes"""
    dx_, dy = 133.0, P['dy']
    top, bot, rx, ry = 89.0 + dy, 116.0 + dy, 16.0, 4.4
    tap = P['tap']
    # legs: from under the shell, a knee out to the side, a foot pad; the back pair first
    legs = [((dx_ - 6.5, bot - 1), (dx_ - 10.5, bot + 9 - dy * 0.3), (dx_ - 7.0, FLOOR - 2.5), 'legB0', True, 0),
            ((dx_ + 7.0, bot - 1), (dx_ + 11.0, bot + 9 - dy * 0.3), (dx_ + 7.5, FLOOR - 2.5), 'legB1', True, 0),
            ((dx_ - 11.5, bot), (dx_ - 18.5 - dy * 0.6, bot + 10 - dy * 0.4), (dx_ - 15.5, FLOOR), 'legF0', False, 2 if tap == 1 else 0),
            ((dx_ + 11.5, bot), (dx_ + 18.5 + dy * 0.6, bot + 10 - dy * 0.4), (dx_ + 15.5, FLOOR), 'legF1', False, 2 if tap == 2 else 0)]
    for (hip, knee, foot, g, back, lift_) in legs:
        foot = (foot[0], foot[1] - lift_)
        rr = 1.0 if back else 1.25
        r.tube(hip, knee, rr + 0.2, rr, M['iron'], lift=-0.22 if back else 0, group=g)
        r.tube(knee, (foot[0], foot[1] - 1.2), rr, rr * 0.8, M['iron'], lift=-0.22 if back else 0, group=g)
        r.ellipsoid(knee[0], knee[1], 1.7, 1.7, M['iron'], lift=0.1 if not back else -0.15, group=g + 'k')        # the knee joint
        r.ellipsoid(foot[0], foot[1] - 0.6, 2.4, 1.2, M['iron'], lift=-0.15 if back else 0.05, group=g + 'f')  # the foot pad
    # the shell: a cylinder, two wooden hoops, the rope laced between them through leather tugs
    def shell_v(x, y):
        u = (x + 0.5 - dx_) / rx
        v = -0.06 * (u > 0.55) + (rig.nL(x * 0.8, y * 1.5 + 9) - 0.5) * 0.16
        if (x * 3 + y) % 13 == 0: v -= 0.1                                              # scratches, old paint
        return v
    r.ellipsoid(dx_, bot, rx, ry, M['stool'], lift=-0.2, group='hoopB')
    r.poly([(dx_ - rx, top), (dx_ + rx, top), (dx_ + rx, bot), (dx_ - rx, bot)], M['shell'], round_=0.95, group='shell', vfun=shell_v)
    r.ellipsoid(dx_, bot, rx, ry, M['shell'], group='shell', clip=lambda x, y: y > bot, vfun=lambda x, y, u, w: shell_v(x, y))
    for (yy, g) in ((bot - 2.5, 'hoopL'), (top + 1.2, 'hoopU')):                        # the hoops round it
        r.poly([(dx_ - rx - 0.6, yy - 1.6), (dx_ + rx + 0.6, yy - 1.6), (dx_ + rx + 0.6, yy + 1.6), (dx_ - rx - 0.6, yy + 1.6)],
               M['stool'], round_=0.95, group=g, vfun=lambda x, y, yy=yy: 0.12 if y < yy - 0.5 else -0.1)
        r.ellipsoid(dx_, yy + 1.6, rx + 0.6, ry, M['stool'], group=g, clip=lambda x, y, yy=yy: y > yy + 1.6)
    ya, yb = top + 3.4, bot - 4.6                                                       # the rope laced in Vs between the hoops
    xs = [dx_ - rx * 0.92 + k * rx * 0.92 / 3 for k in range(7)]
    for k in range(6):
        y0, y1 = (ya, yb) if k % 2 == 0 else (yb, ya)
        for t in range(13):
            q = lerp((xs[k], y0), (xs[k + 1], y1), t / 12)
            r.fixed(q[0], q[1], ROPE[5] if xs[k] < dx_ - 2 else ROPE[4] if xs[k] < dx_ + 6 else ROPE[3])
            r.darken(q[0] + 1, q[1] + 1, 0.2)
    for k in range(7):                                                                  # the leather ears and the lugs at the hoops
        yy = ya if k % 2 == 0 else yb
        r.fixed(xs[k], yy - (1 if k % 2 == 0 else -1), BRASS[3]); r.fixed(xs[k] + 1, yy - (1 if k % 2 == 0 else -1), BRASS[1])
    # the sound-holes: two round dark eyes, the lower inner rim catching light
    for (ex, ey, er) in ((dx_ - 5.5, top + 13.5, 2.6), (dx_ + 5.0, top + 13.0, 2.4)):
        for yy in range(int(ey - er) - 1, int(ey + er) + 2):
            for xx in range(int(ex - er) - 1, int(ex + er) + 2):
                d = math.hypot(xx + 0.5 - ex, (yy + 0.5 - ey) * 0.95)
                if d <= er: r.fixed(xx, yy, HOLE if not (d > er - 0.9 and yy + 0.5 > ey + 0.6) else SHELL[1])
                elif d <= er + 0.8 and yy + 0.5 > ey: r.fixed(xx, yy, SHELL[7])
    # the drum skin: worn vellum, darker where it is played, a ripple on the beat
    rip = P['ripple']
    def skin(x, y, u, w):
        d = math.hypot(u, w)
        v = -0.2 * (d < 0.45) + (rig.nM(x * 2, y * 2) - 0.5) * 0.18
        if rip and abs(d - (0.45 + 0.22 * rip)) < 0.09: v += 0.18
        if rip and abs(d - (0.25 + 0.22 * rip)) < 0.07: v -= 0.12
        return v
    r.ellipsoid(dx_, top, rx - 0.6, ry - 0.6, M['vellum'], group='skin', vfun=skin, flat=0.25)
    r.ellipsoid(dx_, top + 0.2, rx + 0.4, ry + 0.4, M['stool'], lift=0.1, group='rim',
                clip=lambda x, y: ((x + 0.5 - dx_) / (rx - 0.5)) ** 2 + ((y + 0.5 - top) / (ry - 0.5)) ** 2 > 1)
    for k in range(10):                                                                 # small brass tacks on the hoop
        a = k / 10 * 2 * math.pi
        if math.sin(a) < -0.2: continue
        r.fixed(dx_ + math.cos(a) * rx, top + 1.3 + math.sin(a) * ry * 0.4, BRASS[4])


def mix(a, b, t): return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


if __name__ == '__main__':
    os.makedirs(f'{OUT}/busker', exist_ok=True)
    frames = [busker(p) for p in POSE]
    # frame 8: the dialog portrait -- frame 0 without the drum, shifted so his head sits on the frame's centre line
    # (the bust mode of the dialog centres the frame)
    bust = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    bust.paste(frames[0].crop((0, 0, 110, H)), (int(W / 2 - 54), 0))
    frames.append(bust)
    sheet = Image.new('RGBA', (W * len(frames), H), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        im.save(f'{OUT}/busker/{i}.png'); sheet.paste(im, (i * W, 0))
    sheet.save(f'{OUT}/busker.png')
    used = set()
    for im in frames: used |= {px[:3] for px in im.getdata() if px[3]}
    ALL = ([INK, WARMOUT, HOLE, PICK] + HEADW + HAT + BAND + JACKET + SHIRT + SCARF + TROU + BOOT + TOP + SIDES + BOARD + STRING
           + STOOL + SHELL + SKIN_D + ROPE + IRON + BRASS)
    seen, rows = set(), []
    for c in ALL + sorted(used):
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/busker.gpl', 'w').write('GIMP Palette\nName: busker\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT, len(rows), 'colours')
