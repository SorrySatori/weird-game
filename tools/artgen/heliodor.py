"""Heliodor Donjon Vaalstran, the Screaming Cork's barkeep (ScreamingCorkInteriorScene), redrawn with the character
renderer (rig.py, the Edgar quality bar) to show what he says he is: not one creature but a colony living in symbiosis,
each member with its own job -- and its own face -- working in shifts. The old AI art (derived by corkfolk.py) read as a
single leafy man; its green glow, the orange caps and the purple tentacle are kept so he is still recognisable.

The members (all on one stocky body in a stained barkeep's apron, behind the counter):
  * the Speaker -- the head: a pale, smooth fungal face with the colony's green eyes, a few orange caps on top; polite
  * the Mixer -- a pair of jointed crab arms out of the right flank, shaking a copper shaker; its eyes on stalks peer
    over the right shoulder
  * the Polisher -- the purple tentacle from under the left arm, curled round a glass, polishing it with a rag
  * Oorarabaz the Green-faced -- a thick cushion of moss on the left shoulder with a sleeping green face (it wakes only
    for the accounts)
  * the night shift -- a small round creature asleep in the apron's chest pocket
128x192 frames like the old sheet (feet on y 189; the counter covers him from about y 128 down); an 8-frame idle:
  0 the shaker up       1 the shaker down (0-1 = shaking)        2 the shaker up, the tentacle turns the glass
  3 the Speaker blinks  4 Oorarabaz breathes in, the rag moves   5 shift change: the pocket creature wakes, the Mixer's
  6 the pocket creature looks around, the Speaker's eyes glow       eyestalks sink and close
  7 Oorarabaz cracks one eye open (is it time for the accounts?)
python3 heliodor.py <outdir>  ->  heliodor.png (8-frame sheet) + heliodor/<n>.png + heliodor.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK, make_noise
from rig import Rig, Mat
from feral_toast import ik, lerp

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
W, H = 128, 192
R = ramp
FLESH  = R('#26231d #39352c #4f4a3d #686150 #827a65 #9c937b #b5ad93 #ccc5aa #dfd9c0')   # the Speaker's pale fungal skin
CAPS   = R('#2a120a #45200f #663217 #874621 #a65c2d #c1763d #d69652')                   # orange caps (from the old art)
MOSS   = R('#0b160b #122012 #1a2d18 #233b1f #2d4b27 #385c2f #456e37 #548243 #67984f')   # Oorarabaz
CHITIN = R('#1a0806 #2c0e09 #42150d #5a1d11 #742816 #8e361d #a64a29 #bd623a')           # the Mixer's shell
TENT   = R('#110913 #1c1022 #281731 #351f40 #43284f #52325f #623d6f #74497f #8a5a92')   # the Polisher (old art's purple)
APRON  = R('#13100c #1d1813 #28211a #342b21 #41362a #4f4233 #5e4f3d')
SHIRT  = R('#0f1412 #161d1a #1f2823 #29342d #344138 #404f43 #4e5e50')                  # the body under the apron
COPPER = R('#28110a #44200f #653317 #874920 #a8622c #c47f40 #d99f60 #e9c18a')
STEEL  = R('#15181b #24292d #383f45 #50585f #6b747b #8c949a #b2b9be #dde2e5')
GLASS  = R('#1b2626 #2c3d3c #44595a #627a79 #879f9c #b2c8c3 #d8e7e2')
RAG    = R('#3a3428 #554c3c #706552 #8c806a #a69a82')
POCKETC= R('#24201e #38322d #4f4740 #675d54 #80756a #998d80')                           # the night-shift creature
GLOW   = [(31, 90, 50), (63, 143, 90), (127, 255, 142), (200, 255, 208)]
EYEBEAD = (14, 12, 10)
WARMOUT = (26, 20, 15)
TENTOUT = (24, 10, 24)
MOSSOUT = (10, 20, 10)

def mat(rmp, tex, amb, spec=0.0, out=WARMOUT): return Mat(rmp, tex, amb, spec, outline=out)
M = {'flesh': mat(FLESH, 'skin', 0.28, 0.1), 'caps': mat(CAPS, 'skin', 0.24, 0.25), 'moss': mat(MOSS, 'fur', 0.24, 0.0, MOSSOUT),
     'chitin': mat(CHITIN, 'leather', 0.2, 0.7), 'tent': mat(TENT, 'skin', 0.2, 0.6, TENTOUT), 'apron': mat(APRON, 'leather', 0.2, 0.15),
     'shirt': mat(SHIRT, 'wool', 0.2), 'copper': mat(COPPER, 'metal', 0.24, 0.9), 'steel': mat(STEEL, 'metal', 0.22, 1.0), 'glass': mat(GLASS, 'plain', 0.34, 1.0),
     'rag': mat(RAG, 'fabric', 0.3), 'pocketc': mat(POCKETC, 'fur', 0.26)}
nW = make_noise(5, 731, 160, 220)

# pose per frame: sh shaker offset, tp polish phase (0..2), bl Speaker blink, br moss breath, shift (0 day: Mixer
# awake, pocket asleep; 1 changing; 2 the night member looks round), oo Oorarabaz's eye, gl glow boost
POSE = [dict(sh=0, tp=0, bl=0, br=0, shift=0, oo=0, gl=0), dict(sh=1, tp=0, bl=0, br=0, shift=0, oo=0, gl=0),
        dict(sh=0, tp=1, bl=0, br=0, shift=0, oo=0, gl=0), dict(sh=1, tp=1, bl=1, br=0, shift=0, oo=0, gl=0),
        dict(sh=0, tp=2, bl=0, br=1, shift=0, oo=0, gl=0), dict(sh=0, tp=2, bl=0, br=1, shift=1, oo=0, gl=0),
        dict(sh=0, tp=0, bl=0, br=0, shift=2, oo=0, gl=1), dict(sh=0, tp=0, bl=0, br=0, shift=0, oo=1, gl=0)]

HX, HY = 64, 45                                    # the Speaker's head centre
S = 64                                             # the shoulder line
VEST = R('#140a0e #1f1016 #2c1820 #3a212a #492b34 #59363f')                              # a dark plum waistcoat
LIP = [(92, 76, 64), (120, 100, 84), (140, 120, 100)]


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


def cloth(x, y):
    return (nW(x, y) - 0.5) * 0.12


def body(r):
    """a broad barkeep: dark shirt, plum waistcoat, a stained apron from the waist (behind the counter)"""
    M['vest'] = mat(VEST, 'wool', 0.22, 0.1)
    for (a, b) in (((54, 150), (52, 186)), ((74, 150), (76, 186))):
        r.tube(a, b, 7.0, 6.0, M['shirt'], group='leg')
    for fx in (51, 77): r.ellipsoid(fx, 187, 8, 3.5, M['apron'], group='boot')
    r.poly([(38, S + 6), (44, S), (54, S - 3), (74, S - 3), (84, S), (90, S + 6), (89, 96), (86, 150), (42, 150), (39, 96)], M['shirt'],
           group='torso', vfun=cloth)
    stain = lambda x, y: (nW(x * 1.6, y * 1.6) - 0.5) * 0.22 - (0.18 if nW(x * 0.7 + 40, y * 0.7) > 0.72 else 0)
    r.poly([(42, 112), (86, 112), (90, 160), (38, 160)], M['apron'], lift=0.05, group='apron', vfun=stain)
    r.stroke([(40, 112), (88, 112)], 2.0, M['apron'], v=0.5, group='apronband')
    # the waistcoat: a V down to a point, the shirt and its collar inside
    r.poly([(47, S - 1), (57, S - 3), (64, S + 16), (71, S - 3), (81, S - 1), (84, 108), (64, 114), (44, 108)], M['vest'], group='vest',
           vfun=lambda x, y: cloth(x, y) + (0.12 if x < 52 else 0) + (-0.16 if abs(x - 64) < 1 and y > S + 16 else 0))
    for y in (S + 20, S + 27, S + 34, S + 41):                                                   # brass buttons
        r.fixed(64, y, COPPER[6]); r.fixed(64, y + 1, COPPER[3])
    r.poly([(56, S - 5), (62, S + 2), (60, S + 6), (54, S - 1)], M['shirt'], lift=0.18, group='collarL')
    r.poly([(72, S - 5), (66, S + 2), (68, S + 6), (74, S - 1)], M['shirt'], lift=0.1, group='collarR')
    r.poly([(70, 82), (80, 82), (80, 90), (70, 90)], M['vest'], lift=0.14, round_=0.3, group='pocket')   # the breast pocket
    for x in range(70, 81): r.darken(x, 82, -0.2)


def speaker(r, P):
    """the head, painted pixel by pixel on a smooth fungal oval: green-glowing eyes in deep sockets, a short nose, a
    polite closed smile, gill lines down the jaw; orange caps growing out of the crown"""
    r.tube((HX, HY + 9), (HX, S - 1), 5.4, 6.4, M['flesh'], lift=-0.24, group='neck')
    fcx, fcy, frx, fry = HX, HY, 10.4, 12.8
    ey = HY + 1
    lv = (-0.55, -0.55, 0.63); ln = math.sqrt(sum(c * c for c in lv)); lv = tuple(c / ln for c in lv)
    face = set()
    for y in range(int(fcy - fry) - 1, int(fcy + fry) + 2):
        for x in range(int(fcx - frx) - 1, int(fcx + frx) + 2):
            u, w = (x + 0.5 - fcx) / frx, (y + 0.5 - fcy) / fry
            if w > 0.1: u /= max(0.3, 1 - (w - 0.1) ** 1.4 * 0.7)                                  # a narrow jaw
            d = u * u + w * w
            if d > 1: continue
            n = (u, w * 0.8, math.sqrt(max(0.0, 1 - d)))
            v = 0.12 + 0.95 * max(0.0, n[0] * lv[0] + n[1] * lv[1] + n[2] * lv[2])
            v += (nW(x * 3, y * 3) - 0.5) * 0.08
            face.add((x, y))
            r.fixed(x, y, FLESH[max(1, min(8, 1 + int(v * 7.2)))])
    fx = lambda x, y, c: r.fixed(x, y, c)
    def sk(x, y, d):
        e = r.buf.get((int(math.floor(x)), int(math.floor(y))))
        if e and e[3] in FLESH: fx(x, y, FLESH[max(0, min(8, FLESH.index(e[3]) + d))])
    # gill lines down the far cheek and jaw: he is a mushroom, not a man
    for gx in range(int(fcx + 4), int(fcx + 9)):
        for y in range(ey + 2, ey + 11):
            if (gx, y) in face and (gx + y) % 2 == 0 and gx % 2 == 0: sk(gx, y, -1)
    for gx in range(int(fcx - 8), int(fcx - 5)):
        for y in range(ey + 3, ey + 10):
            if (gx, y) in face and gx % 2 == 1 and y % 3: sk(gx, y, -1)
    # brow ridge, deep sockets
    for dx in range(-6, 7):
        if abs(dx) > 1: sk(fcx + dx, ey - 3, +1)
    for ex in (fcx - 4, fcx + 4):
        for (ddx, ddy) in ((-1, -1), (0, -1), (1, -1), (-2, 0), (2, 0), (-1, 1), (0, 1), (1, 1)): sk(ex + ddx, ey + ddy, -2)
    # the eyes: the colony's green light
    for ex in (fcx - 4, fcx + 4):
        if P['bl']:
            for ddx in (-1, 0, 1): fx(ex + ddx, ey, FLESH[2])
            fx(ex - 1, ey - 1, FLESH[4]); fx(ex, ey - 1, FLESH[5]); fx(ex + 1, ey - 1, FLESH[4])
        else:
            core = GLOW[3] if P['gl'] else GLOW[2]
            fx(ex - 1, ey, GLOW[1]); fx(ex, ey, core); fx(ex + 1, ey, GLOW[1] if ex > fcx else GLOW[2])
            fx(ex, ey - 1, GLOW[0]); fx(ex, ey + 1, GLOW[0])
    # nose: short and broad, lit from the left
    fx(fcx - 1, ey + 2, FLESH[6]); fx(fcx - 1, ey + 3, FLESH[7]); fx(fcx, ey + 3, FLESH[5]); fx(fcx + 1, ey + 3, FLESH[3])
    fx(fcx - 1, ey + 4, FLESH[5]); fx(fcx, ey + 4, FLESH[3]); fx(fcx + 1, ey + 4, FLESH[2]); fx(fcx - 2, ey + 4, FLESH[4])
    # mouth: a polite closed smile, the corners up
    my = ey + 7
    for dx in range(-2, 3): fx(fcx + dx, my, LIP[0])
    fx(fcx - 3, my - 1, LIP[0]); fx(fcx + 3, my - 1, LIP[0])
    for dx in (-1, 0, 1): fx(fcx + dx, my + 1, LIP[1] if dx < 1 else LIP[0])
    sk(fcx, my + 2, -1); fx(fcx - 1, my + 3, FLESH[6])
    for x in range(int(fcx - 7), int(fcx + 8)):                                                  # the jaw's shadow on the neck
        ys = [y for y in range(ey, ey + 16) if (x, y) in face]
        if ys: r.darken(x, max(ys) + 1, 0.3); r.darken(x, max(ys) + 2, 0.14)
    # the caps: a cluster on the crown, leaning, the biggest in front
    caps = [(56, 33, 5.2, 2.6, -0.45, 3), (72, 32, 5.8, 2.8, 0.4, 3), (59, 29, 4.2, 2.0, -0.2, 4), (66, 28, 7.2, 3.3, 0.05, 4)]
    for (cx, cy, rx, ry, rot, st) in caps:
        r.tube((cx + 0.3 * (1 if cx > HX else -1), cy + st + 1), (cx, cy + 0.5), 1.3, 1.1, M['flesh'], lift=0.14, group='stem%d' % cx)
    for (cx, cy, rx, ry, rot, st) in caps:
        r.ellipsoid(cx, cy, rx, ry, M['caps'], rot=rot, group='cap%d' % cx,
                    vfun=lambda x, y, u, w: (0.24 if w < -0.25 and u < 0.2 else 0) + (-0.22 if w > 0.5 else 0))
        for k in range(-int(rx) + 1, int(rx)):                                                    # gills under the rim
            if k % 2 == 0: r.darken(cx + k * math.cos(rot), cy + ry * 0.8 + k * math.sin(rot), 0.25)
    for (cx, cy) in ((64, 26), (69, 27), (55, 32), (73, 31)): fx(cx, cy, CAPS[6])               # pale specks


def oorarabaz(r, P):
    """a thick cushion of moss sitting on the left shoulder (strands hanging off it), with a sleeping green face"""
    br = 0.7 * P['br']
    tuft = lambda x, y, u, w: (nW(x * 2.6, y * 2.6) - 0.5) * 0.36 + (-0.18 if (x * 3 + y * 5) % 7 == 0 else 0) - 0.06
    fx_, fy_ = 41, S
    r.ellipsoid(fx_ + 2, fy_ + 7, 9, 6, M['moss'], jag=0.2, lift=-0.1, group='mossback', vfun=tuft)   # over the shoulder's back
    r.ellipsoid(fx_, fy_, 12.5 + br, 10.5 + br, M['moss'], jag=0.14, group='mossface', vfun=tuft)
    for (sx, sy, ln) in ((30, S + 6, 7), (34, S + 9, 9), (47, S + 9, 6), (32, S - 9, 3), (45, S - 10, 3)):
        r.stroke([(sx + (i % 2) * 0.4, sy + (i if sy > S else -i)) for i in range(ln)], 1.0, M['moss'], v=0.42, group='strand')
    return fx_, fy_


def oorarabaz_face(r, P, fx_, fy_):
    """a broad old green face, asleep: heavy lids, a big round nose, the mouth open in a snore"""
    fx = lambda x, y, c: r.fixed(x, y, c)
    ey = fy_ - 2
    for ex in (fx_ - 5, fx_ + 4):
        if P['oo'] and ex > fx_:                                                                # one eye cracked open
            fx(ex - 1, ey - 1, MOSS[7]); fx(ex, ey - 1, MOSS[8]); fx(ex + 1, ey - 1, MOSS[7])
            fx(ex - 1, ey, MOSS[1]); fx(ex, ey, GLOW[2]); fx(ex + 1, ey, MOSS[1])
        else:
            for dx in (-1, 0, 1): fx(ex + dx, ey - 1, MOSS[7] if dx < 1 else MOSS[6])               # the heavy lid
            fx(ex - 2, ey, MOSS[2]); fx(ex - 1, ey + 0, MOSS[0]); fx(ex, ey + 0, MOSS[0]); fx(ex + 1, ey, MOSS[0]); fx(ex + 2, ey, MOSS[2])
        for dx in (-2, -1, 0, 1, 2): fx(ex + dx, ey - 3, MOSS[2] if abs(dx) < 2 else MOSS[3])        # the brow
    for (x, y, c) in ((fx_ - 1, ey + 1, MOSS[7]), (fx_, ey + 1, MOSS[6]), (fx_ - 2, ey + 2, MOSS[6]), (fx_ - 1, ey + 2, MOSS[8]),
                      (fx_, ey + 2, MOSS[6]), (fx_ + 1, ey + 2, MOSS[4]), (fx_ - 2, ey + 3, MOSS[5]), (fx_ - 1, ey + 3, MOSS[6]),
                      (fx_, ey + 3, MOSS[4]), (fx_ + 1, ey + 3, MOSS[2]), (fx_ - 1, ey + 4, MOSS[2]), (fx_, ey + 4, MOSS[1])):
        fx(x, y, c)                                                                                 # the nose
    my = ey + 6
    for dx in (-2, -1, 0, 1): fx(fx_ + dx, my, MOSS[0])
    if P['br']:
        for dx in (-1, 0): fx(fx_ + dx, my + 1, MOSS[0])
    fx(fx_ - 3, my - 1, MOSS[1]); fx(fx_ + 2, my - 1, MOSS[1])


def polisher(r, P):
    """the left sleeve ends in the purple tentacle: it curls round a glass and polishes it with a rag"""
    tp = P['tp']
    sh, el, cuff = (42, S + 6), (34, S + 30), (42, S + 44)
    r.tube(sh, el, 6.0, 5.2, M['shirt'], group='sleeveL', folds=lambda u, sd: -0.2 if abs(sd + 0.3) < 0.12 and 0.2 < u < 0.8 else 0)
    r.ellipsoid(el[0], el[1], 5.0, 5.0, M['shirt'], group='sleeveL')
    r.tube(el, cuff, 5.0, 4.6, M['shirt'], group='sleeveL2')
    r.ellipsoid(cuff[0] + 1, cuff[1], 5.0, 4.0, M['shirt'], lift=0.18, group='cuffL')
    curl = spline([(cuff[0] + 3, cuff[1] + 1), (50, S + 44), (56, S + 40), (59, S + 33), (57, S + 27), (53, S + 25)])
    N = len(curl) - 1
    rad = lambda t: 3.8 - 1.9 * t + 0.25 * math.sin(t * 17)
    for i in range(N):
        r.tube(curl[i], curl[i + 1], rad(i / N), rad((i + 1) / N), M['tent'], group='tent',
               folds=lambda u, sd: 0.22 if sd > 0.3 else (-0.12 if sd < -0.6 else 0))
    for i in range(3, N - 2, 4):
        (x0, y0), (x1, y1) = curl[i - 1], curl[i + 1]
        dx, dy = x1 - x0, y1 - y0; l = math.hypot(dx, dy) or 1
        rr = rad(i / N)
        r.fixed(curl[i][0] - dy / l * (rr - 0.8), curl[i][1] + dx / l * (rr - 0.8), (176, 134, 172))
    # the glass inside the curl, turning as it's polished
    gx, gy = 53, S + 33
    r.poly([(gx - 4.5, gy - 8), (gx + 4.5, gy - 8), (gx + 3.6, gy + 4), (gx - 3.6, gy + 4)], M['glass'], lift=0.12, round_=0.95, group='glass',
           vfun=lambda x, y: (0.5 if x == gx - 3 + tp * 2 and gy - 6 < y < gy + 2 else 0))
    for x in range(int(gx - 4), int(gx + 5)): r.fixed(x, gy - 8, GLASS[6] if (x + tp) % 3 else GLASS[5])
    r.fixed(gx + 2 - tp, gy - 5, (240, 250, 246))
    for x in range(int(gx - 3), int(gx + 4)): r.fixed(x, gy + 4, GLASS[2])
    # the tentacle's tip wraps the glass in front; the rag hangs off the curl
    r.tube((gx - 6, gy - 1), (gx + 2, gy - 3), 2.0, 1.5, M['tent'], lift=0.06, group='tenttip')
    r.tube((gx + 2, gy - 3), (gx + 5, gy + 1), 1.5, 0.9, M['tent'], lift=0.06, group='tenttip')
    rx = gx - 1 + [0, 2, -1][tp]
    r.poly([(rx - 5, gy + 3), (rx + 4, gy + 2), (rx + 5, gy + 10), (rx + 1, gy + 14), (rx - 5, gy + 10)], M['rag'], lift=0.08, group='rag',
           vfun=lambda x, y: -0.18 if (x + 2 * y) % 5 == 0 else 0)


def mixer(r, P):
    """the right sleeve ends in a crab claw: raised, it shakes a copper shaker; the Mixer's eyes stalk up from its wrist"""
    sh = P['sh']
    sho, el = (86, S + 6), (98, S + 26)
    cuff = (96, S + 8 + sh * 2)
    r.tube(sho, el, 6.0, 5.2, M['shirt'], group='sleeveR', folds=lambda u, sd: -0.2 if abs(sd - 0.3) < 0.12 and 0.2 < u < 0.8 else 0)
    r.ellipsoid(el[0], el[1], 5.0, 5.0, M['shirt'], group='sleeveR')
    r.tube(el, cuff, 5.0, 4.6, M['shirt'], group='sleeveR2')
    r.ellipsoid(cuff[0], cuff[1] + 1, 5.0, 4.0, M['shirt'], lift=0.12, group='cuffR')
    seg = lambda u, sd: (-0.28 if abs(u - 0.5) < 0.07 else 0) + (0.18 if sd < -0.3 else 0)
    wrist = (cuff[0] - 1, cuff[1] - 5)
    r.tube((cuff[0], cuff[1] - 1), wrist, 4.4, 4.0, M['chitin'], group='claw', folds=seg)
    # the shaker, tilted a little as it shakes
    tilt = -0.12 if sh else 0.1
    top, bot = (wrist[0] - 1 + tilt * 14, wrist[1] - 17), (wrist[0] - 1, wrist[1] + 1)
    r.tube(bot, top, 3.4, 4.3, M['steel'], group='shaker')                                    # widening to the top
    capt = (top[0] + tilt * 5, top[1] - 5)
    r.tube(top, capt, 4.0, 3.0, M['steel'], lift=0.1, group='shakercap')                       # the cap
    r.ellipsoid(capt[0], capt[1], 1.6, 1.3, M['steel'], lift=0.15, group='shakerknob')
    for k in range(-3, 4): r.darken(top[0] + k, top[1] + 0.5, 0.28)                            # the seam under the cap
    for k in range(3): r.darken(lerp(bot, top, 0.35)[0] - 3 + k * 2.5, lerp(bot, top, 0.35)[1], 0.2)     # its band
    # the pincers round it: a big upper finger and a smaller lower one
    r.tube((wrist[0] + 3, wrist[1]), (wrist[0] - 5, wrist[1] - 8), 3.0, 1.4, M['chitin'], lift=0.08, group='pincerA', folds=seg)
    r.tube((wrist[0] + 3, wrist[1] + 1), (wrist[0] - 5, wrist[1] - 1), 2.2, 1.0, M['chitin'], lift=0.04, group='pincerB')
    if sh == 0:
        r.fixed(capt[0] - 3, capt[1] - 2, (226, 222, 200)); r.fixed(capt[0] + 3, capt[1] - 3, (196, 192, 172))   # flecks of foam
    # the Mixer's eyes on stalks from the wrist (they sink and close when its shift ends)
    sink = 4 if P['shift'] else 0
    for (bx, tx, ty) in ((wrist[0] + 2, wrist[0] + 4, wrist[1] - 9), (wrist[0] + 4, wrist[0] + 8, wrist[1] - 7)):
        tip = (tx, ty + sink)
        r.tube((bx, wrist[1] - 2), tip, 1.1, 0.9, M['chitin'], lift=0.1, group='stalk%d' % bx)
        r.ellipsoid(tip[0], tip[1] - 0.5, 1.6, 1.6, M['chitin'], lift=0.12, group='bead%d' % bx)
    return [(tx, ty + sink) for (bx, tx, ty) in ((0, wrist[0] + 4, wrist[1] - 9), (0, wrist[0] + 8, wrist[1] - 7))]


def mixer_eyes(r, P, tips):
    for (x, y) in tips:
        if P['shift']:
            r.fixed(x - 1, y - 1, CHITIN[3]); r.fixed(x, y - 1, CHITIN[3])
        else:
            r.fixed(x, y - 1, EYEBEAD); r.fixed(x - 1, y - 2, (200, 190, 170))


def pocket_creature(r, P):
    """the night shift, asleep in the breast pocket -- awake at the change of shift"""
    up = 2 if P['shift'] else 0
    cx, cy = 75, 81 - up
    r.ellipsoid(cx, cy, 4.6, 3.8, M['pocketc'], group='pocketc')
    for ex in (cx - 3, cx + 3): r.ellipsoid(ex, cy - 3.5, 1.4, 2.2, M['pocketc'], lift=0.06, group='pocketear')
    r.poly([(70, 82), (80, 82), (80, 90), (70, 90)], M['vest'], lift=0.14, round_=0.3, group='pocket2')   # the pocket in front
    for x in range(70, 81): r.darken(x, 82, -0.2)
    return cx, cy


def pocket_face(r, P, cx, cy):
    if P['shift'] == 0:
        for ex in (cx - 2, cx + 2): r.fixed(ex, cy, POCKETC[0]); r.fixed(ex - 1, cy - 1, POCKETC[1]); r.fixed(ex + 1, cy - 1, POCKETC[1])
    else:
        look = 1 if P['shift'] == 2 else 0
        for ex in (cx - 2, cx + 2):
            r.fixed(ex - 1, cy - 1, (222, 210, 168)); r.fixed(ex, cy - 1, (222, 210, 168))
            r.fixed(ex - 1, cy, (222, 210, 168)); r.fixed(ex, cy, (222, 210, 168))
            r.fixed(ex - 1 + look, cy, EYEBEAD)


def glow_light(r, pts, k, rad):
    """the colony's green eyes light what is near them (a lift in the tone buffer, so it stays on the ramps)"""
    for (x, y), e in r.buf.items():
        if e[0] is None: continue
        d = min(math.hypot(x + 0.5 - px, y + 0.5 - py) for (px, py) in pts)
        if d < rad: e[1] += k * (1 - d / rad) ** 2


def heliodor(P):
    r = Rig(W, H)
    body(r)
    cx, cy = pocket_creature(r, P)
    tips = mixer(r, P)
    polisher(r, P)
    fx_, fy_ = oorarabaz(r, P)
    speaker(r, P)
    if not P['bl']: glow_light(r, [(HX - 4, HY + 1), (HX + 4, HY + 1)], 0.16 + 0.08 * P['gl'], 10)
    oorarabaz_face(r, P, fx_, fy_)
    pocket_face(r, P, cx, cy)
    mixer_eyes(r, P, tips)
    return r.render()


if __name__ == '__main__':
    os.makedirs(f'{OUT}/heliodor', exist_ok=True)
    frames = [heliodor(p) for p in POSE]
    sheet = Image.new('RGBA', (W * len(frames), H), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        im.save(f'{OUT}/heliodor/{i}.png'); sheet.paste(im, (i * W, 0))
    sheet.save(f'{OUT}/heliodor.png')
    used = set()
    for im in frames: used |= {c[1][:3] for c in im.getcolors(1 << 16) if c[1][3]}
    seen, rows = set(), []
    for c in [INK, WARMOUT, TENTOUT, MOSSOUT] + FLESH + CAPS + MOSS + CHITIN + TENT + APRON + SHIRT + COPPER + GLASS + RAG + POCKETC + VEST + STEEL + LIP + GLOW + sorted(used):
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/heliodor.gpl', 'w').write('GIMP Palette\nName: heliodor\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT, len(rows), 'colours')
