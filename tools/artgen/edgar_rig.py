"""Edgar Eskola, the mišutkenn of the Screaming Cork (ScreamingCorkScene; the `cs_edgar` panel of ScraperAmbraScene's
night cutscene), drawn for real with the character renderer (rig.py) -- replacing edgar.py's box-filtered AI picture
(tools/artgen/ref/EdgarEskola.png, now only the reference for who he is). He must stay the same Edgar, the cast's
quality bar: a bear-man of heavy, realistic build, turned a little toward the viewer's left (his weight on the right
leg, the left boot's toe turned out); a big, wide, round bear head (about 28 % of his height) on a short neck above the
collar, small round ears set high and wide, a lighter muzzle volume ending in a broad dark nose, small eyes under heavy
drooping lids in dark sockets (1 px warm-grey glints), a furrow between the raised inner brows, the mouth line sagging
at the corners; a long worn olive-khaki trench coat with soft sun-faded mottling, open at the top (wide notched lapels,
the dark shirt and waistcoat in the V, the collar's lit edge under the chin), cinched by its belt (buckle, tail and
D-ring hanging) so the cloth blouses above it and the skirts flare below, a patch pocket on the chest and on both hips,
a worn leather patch on the right shoulder, a leather strap across the chest, dark trousers and laced work boots.
His right paw (viewer's left) holds a tied burlap sack out at his hip, the left paw hangs.
The light comes from the upper right like in the old picture (the tavern door is on his right): the renderer's light,
its rim and its cast shadows are mirrored here (EdgarRig) -- rig.py itself is untouched.
128x192 frames like the old sheet, soles on y 189 (the last opaque row is 188); the same 8-frame idle:
  0 rest            1 breath in (head, shoulders and the sack rise a pixel)     2 blink
  3 the right ear twitches                       4-5 the sack sways right / left on its neck
  6 he lowers his head a little (a grumble)      7 head down, eyes shut (a sigh)
python3 edgar_rig.py <outdir>  ->  edgar.png (8-frame sheet) + edgar/<n>.png + edgar_rig.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, h32, make_noise
import rig
from rig import Rig, Mat, norm, BAYER
from feral_toast import ik
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
W, H = 128, 192
SOLE = 188                     # the last opaque row: the soles stand on y 189 like in the old sheet
R = ramp
FUR    = R('#0b0704 #140d07 #1d130a #26190e #301f11 #3a2615 #442c18 #4e331c #593a20 #644225 #6f4a2a #7b5330 #875d37')
MUZZLE = R('#1b130b #271b10 #332316 #3f2c1b #4c3521 #593f27 #66492d #735334 #805d3b #8c6843 #98734c')
NOSE   = R('#070403 #0f0806 #180e0a #22150f #2d1d15 #3a271c #4a3426')
COAT   = R('#0d0904 #150f07 #1e1509 #271b0d #302111 #3a2815 #432f19 #4d371d #573f22 #614727 #6b502c #755932 #806238 #8a6c40')
COATF  = R('#0e0b05 #181208 #221a0c #2c2310 #362b15 #40341a #493c1e #534524 #5d4e29 #67582f #716134 #7b6b3a #857441 #8f7e47')   # sun-faded
VEST   = R('#0d0806 #150d09 #1e130d #271a11 #312116 #3b281b')
STRAP  = R('#120804 #1c0d06 #261209 #30170b #3a1c0e #442111 #4e2714 #592d18 #63341c #6e3b21')
PATCH  = R('#1c0f07 #2a170b #38200f #472913 #563217 #643b1b #72441f #7f4e25')
SACK   = R('#160e06 #21150a #2c1c0d #372311 #422b15 #4e331a #593c1f #654525 #704e2b #7c5832 #876139')
SHIRT  = R('#120806 #1c0d09 #27120c #321810 #3e1f13 #4a2717')
TROU   = R('#090604 #100b07 #17100b #1e160f #261c13 #2e2217 #37291c')
BOOT   = R('#100805 #180c07 #21110a #2a160d #341b10 #3e2113 #482717 #522d1b #5c331f #663a24')
BOOTD  = R('#0e0805 #160d08 #1f130b #29190f #332013 #3d2717 #482e1b #533620 #5e3e25')
CLAW   = R('#16120e #29231c #3e362c #574d40 #716656')
IRON   = R('#100e0c #1c1916 #2a2621 #3a352e #4d463c #61584b #776c5c')
GLINT  = (170, 151, 118)        # a small warm-grey wet glint (not white: white dots read as glowing eyes)
LID    = (28, 17, 10)
EYEC   = (14, 9, 6)
OUTL   = (24, 14, 9)            # the warm dark outline (a touch warmer than the fur's darkest step)

# ---- the light from the upper right (mirrored rig): shade, its rim and the cast shadows -----------------------------
LIGHT = norm((0.5, -0.75, 0.55))
HALF = norm((LIGHT[0], LIGHT[1], LIGHT[2] + 1))
LIGHT_H = norm((0.28, -0.5, 0.82))   # the face takes the door's light more frontally
EXPOSURE = 0.12                 # he stands in an overcast street: a key lower than the renderer's default


class EdgarRig(Rig):
    def shade(self, mat, n, lift=0.0):
        lam = max(0.0, n[0] * LIGHT[0] + n[1] * LIGHT[1] + n[2] * LIGHT[2])
        v = mat.amb + (1 - mat.amb) * lam
        v += 0.12 * max(0.0, -n[0]) ** 3 * (1 - n[2])               # a faint cool rim from the street lamp, left behind
        if mat.spec: v += mat.spec * max(0.0, n[0] * HALF[0] + n[1] * HALF[1] + n[2] * HALF[2]) ** 18
        return v + lift

    def render(self, outline=True, shadow=0.13, contact=0.10):
        buf, G = self.buf, self.groups
        tone = {k: e[1] - EXPOSURE for k, e in buf.items()}
        for (x, y), e in buf.items():
            if e[0] is None: continue
            g = G[e[2]]
            for dx, dy in ((1, -2), (0, -2), (2, -1)):                          # cast shadow from up-right
                q = buf.get((x + dx, y + dy))
                if q and q[2] > e[2] and G[q[2]] != g: tone[(x, y)] -= shadow; break
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):                    # contact line on the behind side
                q = buf.get((x + dx, y + dy))
                if q and q[2] > e[2] and G[q[2]] != g: tone[(x, y)] -= contact; break
        im = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0)); p = im.load()
        for (x, y), e in buf.items():
            mat, oid, fixed = e[0], e[2], e[3]
            if fixed: p[x, y] = fixed + (255,); continue
            r = mat.ramp
            alt = getattr(mat, 'alt', None)
            if alt and alt[1](x, y): r = alt[0]                                   # a second ramp in patches (faded cloth)
            v = tone[(x, y)] + mat.tex(x, y)
            i = v * (len(r) - 1) + (BAYER[y % 4][x % 4] / 16 - 0.47) * 0.85
            p[x, y] = r[max(0, min(len(r) - 1, int(round(i))))] + (255,)
        if outline:
            add = {}
            for (x, y), e in buf.items():
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (x + dx, y + dy)
                    if q in buf or not (0 <= q[0] < self.w and 0 <= q[1] < self.h): continue
                    if q not in add or add[q][0] < e[2]:
                        add[q] = (e[2], e[0].outline if e[0] else OUTL)
            for (x, y), (_, c) in add.items(): p[x, y] = c + (255,)
        return im


# ---- textures: shaggy fur in clumps, a worn cotton drill with mottling and old stains, coarse burlap ----------------
nC = make_noise(3, 211, 320, 320); nS = make_noise(7, 212, 320, 320); nB = make_noise(14, 213, 320, 320)
rig.TEX['bearfur'] = lambda x, y: ((nC(x * 0.85, y * 0.65) - 0.5) * 0.30 + (nS(x * 0.75, y * 0.75) - 0.5) * 0.26
                                   + ((h32(x, y, 77) % 7) - 3) * 0.035 + ((h32(x, y // 2, 79) % 5) - 2) * 0.03)
rig.TEX['drill'] = lambda x, y: ((rig.nF(x * 1.7, y * 1.7) - 0.5) * 0.10 + (nC(x * 1.1 + 50, y * 0.9) - 0.5) * 0.22
                                 + (nS(x * 1.0, y * 1.0) - 0.5) * 0.18 + (nB(x * 0.8 + 30, y * 0.8) - 0.5) * 0.24
                                 + ((h32(x, y, 81) % 5) - 2) * 0.022 + (0.02 if (x + y) % 3 == 0 else -0.01))
rig.TEX['burlap'] = lambda x, y: ((rig.nF(x * 1.5, y * 1.5) - 0.5) * 0.14 + (0.02 if (x % 2 == 0) != (y % 2 == 0) else -0.015)
                                  + (nS(x, y + 40) - 0.5) * 0.18)


def mat(rmp, tex, amb, spec=0.0, out=OUTL): return Mat(rmp, tex, amb, spec, outline=out)


M = {'fur': mat(FUR, 'bearfur', 0.22, 0.05), 'paw': mat(FUR[:10], 'bearfur', 0.16, 0.04), 'muzzle': mat(MUZZLE, 'bearfur', 0.22, 0.06),
     'ear': mat(MUZZLE, 'skin', 0.2), 'nose': mat(NOSE, 'leather', 0.2, 0.9),
     'coat': mat(COAT, 'drill', 0.16, 0.02), 'coatin': mat(COAT, 'drill', 0.06), 'strap': mat(STRAP, 'leather', 0.2, 0.15),
     'patch': mat(PATCH, 'leather', 0.18, 0.2), 'sack': mat(SACK, 'burlap', 0.18), 'shirt': mat(SHIRT, 'wool', 0.16), 'vest': mat(VEST, 'wool', 0.16),
     'trou': mat(TROU, 'fabric', 0.18), 'boot': mat(BOOT, 'leather', 0.18, 0.55), 'bootd': mat(BOOTD, 'leather', 0.16, 0.4),
     'claw': mat(CLAW, 'plain', 0.3, 0.6), 'iron': mat(IRON, 'metal', 0.24, 0.8)}

# the old coat is blotchy: sun-faded yellowish patches against browner stains -- the faded ramp in low-frequency patches
nP = make_noise(9, 215, 320, 320)
for k in ('coat', 'coatin'):
    M[k].alt = (COATF, lambda x, y: nP(x * 1.4, y * 1.1) * 0.6 + nS(x * 1.2 + 70, y * 1.2) * 0.4
                                    + (BAYER[y % 4][x % 4] / 16 - 0.5) * 0.22 > 0.53)          # dithered edges: soft, painterly

POSE = [dict(), dict(b=1), dict(blink=1), dict(ear=1), dict(sway=1), dict(sway=-1), dict(nod=1), dict(nod=2, blink=1)]


def folds(lines, y0, y1, depth=0.42, lit=0.2, side=None):
    """drapery (after brukk.py): each line (xa at y0 -> xb at y1, strength s) is a dark valley with a lit ridge on its
    upper-RIGHT side here (the light is mirrored); side(x, y) adds a broad shading term"""
    def vf(x, y):
        v = 0.0
        if y0 <= y <= y1:
            k = (y - y0) / (y1 - y0)
            for (xa, xb, s) in lines:
                lx = xa + (xb - xa) * k
                d = x + 0.5 - lx
                g = min(1.0, k * 3.0) * s
                if -1.1 < d < 0.9: v -= depth * g
                elif 0.9 <= d < 3.0: v += lit * g
                elif -2.2 < d <= -1.1: v -= depth * 0.4 * g
        if side: v += side(x, y)
        return v
    return vf


def stitch(r, pts, dv=0.16, every=2):
    """a seam line of darker stitches along a polyline"""
    k = 0
    for (a, b) in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b)))
        for i in range(n):
            t = i / n
            if k % every == 0: r.darken(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, dv)
            k += 1


def spline(pts, step=1.0):
    """Catmull-Rom through the points, resampled about every `step` px (after heliodor.py)"""
    Q = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
        n = max(2, int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / step))
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


def band(r, pts, w, mat_, group, lift=0.0, vfun=None):
    """a flat band (strap, belt) of width w along a polyline, rounded across its width"""
    oid = r.new(group)
    P = spline(pts, 0.5)
    for i, (x0, y0) in enumerate(P):
        x1, y1 = P[min(i + 1, len(P) - 1)] if i + 1 < len(P) else (x0 + (x0 - P[i - 1][0]), y0 + (y0 - P[i - 1][1]))
        dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        for k in range(-int(w * 2), int(w * 2) + 1):
            s = k / (w * 2)
            x, y = x0 + nx * s * w / 2, y0 + ny * s * w / 2
            n = norm((nx * s * 0.8, ny * s * 0.8 - 0.25, 1))
            v = r.shade(mat_, n, lift) + (vfun(int(x), int(y), s) if vfun else 0)
            r.put(x, y, mat_, v, oid)
    return P


# =====================================================================================================================
def boot(r, top, ank, toe, mat_, ramp_, g, side):
    """a heavy laced work boot: the shaft creased at the ankle, a row of eyelets and crossed laces down the front, the
    foot with a toe cap, a lighter welt and a dark sole under it, the heel block at the back"""
    r.tube(top, ank, 8.4, 8.6, mat_, group=g + 'shaft',
           folds=lambda u, sd: (-0.24 if 0.72 < u < 0.78 and abs(sd) < 0.8 else 0) + (-0.18 if 0.86 < u < 0.9 and sd < 0.5 else 0)
           + (0.06 if 0.79 <= u < 0.86 else 0) + (-0.12 if sd < -0.65 else 0))
    tx, ty, rx = toe
    r.ellipsoid(tx, ty, rx, 4.9, mat_, rot=-0.04 * side, group=g + 'foot',
                vfun=lambda x, y, u, w: (0.12 if w < -0.4 else 0) + (-0.14 if w > 0.55 else 0))
    cx_ = tx - side * rx * 0.62                                            # the toe cap and its stitched seam
    capr = rx * (0.42 if abs(side) > 0.5 else 0.62)                        # (a frontal boot shows its whole cap)
    r.ellipsoid(cx_, ty + (-0.4 if abs(side) > 0.5 else 0.4), capr, 3.9 if abs(side) > 0.5 else 3.4, mat_, lift=0.05 if abs(side) > 0.5 else 0.0,
                group=g + 'cap', vfun=lambda x, y, u, w: 0.1 if w < -0.3 else 0)
    seam(r, g + 'cap', 0.14)
    seam(r, g + 'shaft', 0.12)
    x0, x1 = int(min(tx - rx, ank[0] - 9)), int(max(tx + rx, ank[0] + 9))
    for x in range(x0, x1 + 1):                                           # welt and sole along the bottom
        if (x, 186) in r.buf:
            r.darken(x, 185, -0.1); r.fixed(x, 186, ramp_[5] if x % 3 else ramp_[4])
            r.fixed(x, 187, ramp_[1]); r.fixed(x, 188, ramp_[0])
    hx = ank[0] + side * 5.5                                              # the heel at the back (a frontal boot hides it)
    for x in (range(int(hx - 3), int(hx + 3)) if side else ()):
        r.fixed(x, 187, ramp_[2]); r.fixed(x, 188, ramp_[0])
    fx = ank[0] - side * 1.0                                              # eyelets and crossed laces down the front
    for k in range(4):
        y = int(top[1] + 3 + k * 3)
        r.fixed(fx - 2, y, ramp_[7]); r.fixed(fx + 2, y, ramp_[6])
        r.fixed(fx - 1, y + 1, ramp_[3]); r.fixed(fx, y + 1, ramp_[4]); r.fixed(fx + 1, y + 1, ramp_[3])
        r.darken(fx, y, 0.18)


def legs(r, P):
    """dark trousers bagging over heavy laced boots; his weight on the right leg (viewer's left, the toe turned out),
    the left boot frontal and in his own shadow"""
    boot(r, (51, 165), (50, 178), (44.0, 182.6, 12.6), M['boot'], BOOT, 'bootW', 1)
    boot(r, (85, 169), (85, 179), (85.0, 183.2, 10.2), M['bootd'], BOOTD, 'bootF', 0.0)
    # the trousers over them, their hems bunched round the boot tops
    r.tube((53, 146), (51, 165), 8.2, 7.8, M['trou'], group='legW',
           folds=lambda u, sd: (-0.22 if abs(sd + 0.15) < 0.1 and u > 0.3 else 0) + (-0.2 if 0.62 < u < 0.68 else 0) + (0.08 if sd > 0.5 else 0))
    r.tube((80, 146), (84, 169), 8.0, 7.6, M['trou'], group='legF',
           folds=lambda u, sd: (-0.22 if abs(sd - 0.2) < 0.1 and u > 0.35 else 0) + (-0.18 if 0.7 < u < 0.76 else 0) + (-0.12 if sd < -0.4 else 0))
    for (cx_, cy_, g) in ((51, 166, 'hemW'), (84.5, 170, 'hemF')):
        r.ellipsoid(cx_, cy_, 9.6, 3.2, M['trou'], lift=0.0, jag=0.12, group=g,
                    vfun=lambda x, y, u, w: (-0.2 if (x * 3 + y) % 7 == 0 else 0) + (0.08 if w < -0.4 else 0))
        seam(r, g, 0.1)


def body_round(cx=70.5, half=36.0, amb=0.16):
    """the two coat panels are halves of one body: shade them as one cylinder (poly's own row rounding would give each
    panel its own dark edge, a false slit down the front)"""
    lam0 = LIGHT[2]
    def f(x, y):
        u = max(-0.97, min(0.97, (x + 0.5 - cx) / half))
        n = (u * 0.92, 0.0, math.sqrt(1 - u * u * 0.85))
        lam = max(0.0, n[0] * LIGHT[0] + n[2] * LIGHT[2])
        return (1 - amb) * (lam - lam0)
    return f


def coat(r, P):
    """the trench coat: open at the top (see upper_coat), cinched by its belt at the waist so it has a shape -- the cloth
    bloused above the belt, the long skirts flaring below it to the shins; the far panel in his own shadow, the near one
    broad and lit; the folds converge on the belt from the chest and fan out from it down the skirts"""
    b = P.get('b', 0)
    U = lambda y: y - b if y < 112 else y
    hem = lambda x, y, y_hem: (-0.12 if y > y_hem - 2 - (h32(x // 3, 3) % 3) and h32(x // 3, 5) % 3 == 0 else 0) - 0.02 * max(0, y - (y_hem - 12))
    body = body_round()
    W_FOLDS = folds([(52, 42, 0.8), (56, 50, 0.9), (59, 57, 0.5)], 112, 157)          # fanning out from the belt
    F_FOLDS = folds([(66, 66, 0.4), (72, 76, 1.0), (79, 87, 1.0), (86, 97, 0.7)], 112, 159)
    def chest(x, y):                                                                  # converging on the belt from above
        v = 0.0
        for (x0, y0, x1, y1, s) in ((47, 80, 54, 107, 0.7), (92, 82, 80, 107, 0.9), (99, 90, 88, 108, 0.7), (86, 96, 77, 108, 0.5)):
            if U(y0) <= y <= y1:
                t = (y - U(y0)) / (y1 - U(y0)); lx = x0 + (x1 - x0) * t
                d = x + 0.5 - lx
                if -0.8 < d < 0.8: v -= 0.26 * s * min(1.0, t * 2.5)
                elif 0.8 <= d < 2.4: v += 0.1 * s * min(1.0, t * 2.5)
        if 99 <= y <= 106: v += (-0.2 if (x * 3 + y) % 4 == 0 else 0.04)              # the cloth bloused over the belt
        return v
    r.poly([(48, U(63)), (41, U(68)), (37, U(75)), (35, U(88)), (37.5, 102), (39.5, 110), (37, 124), (35, 140), (34, 152), (37, 156), (47, 156.5),
            (55, 156), (62, 157), (62, 110), (61, U(86)), (58, U(70))], M['coat'], round_=0.0, group='coatW',
           vfun=lambda x, y: W_FOLDS(x, y) + chest(x, y) + body(x, y) + hem(x, y, 156) - 0.1)
    r.poly([(68, U(62)), (80, U(61)), (91, U(65)), (99, U(71)), (103, U(77)), (105, U(86)), (103, 100), (100.5, 110), (103, 124), (104, 140),
            (104, 157), (90, 159.5), (78, 158.5), (66, 159), (59, 158), (60, 112), (60, U(92)), (63, U(76))], M['coat'], round_=0.0, group='coatF',
           vfun=lambda x, y: F_FOLDS(x, y) + chest(x, y) + body(x, y) + hem(x, y, 159))
    for y in range(104, 159):                                                         # the near panel's front edge
        r.darken(59, y, 0.3); r.darken(60, y, -0.1)


def strap_and_belt(r, P):
    """the cloth belt round the waist (buckled at the front, its tail and D-ring hanging), and over it the leather strap
    slung across the chest, low and steep like in the old picture: from under the far arm down to the near hip"""
    b = P.get('b', 0)
    U = lambda y: y - b if y < 112 else y
    belt = [(39, 107.5), (50, 109.5), (62, 110.5), (75, 110.5), (88, 109), (101, 107)]
    band(r, belt, 5.0, M['coat'], 'belt', lift=-0.08, vfun=lambda x, y, s: (0.16 if s < -0.55 else 0) + (-0.16 if s > 0.7 else 0)
         + body_round()(x, y))
    seam(r, 'belt', 0.3)
    for (x, y) in spline(belt, 1.0):                         # the bloused cloth hangs over it: a lit roll, its shadow on the belt
        r.darken(x, y - 4, -0.12); r.darken(x, y - 3, 0.06)
    bx, by = 77, 108
    for (dx, dy, c) in ((0, 0, IRON[5]), (1, 0, IRON[6]), (2, 0, IRON[5]), (3, 0, IRON[4]), (4, 0, IRON[3]), (0, 1, IRON[4]),
                        (0, 2, IRON[3]), (0, 3, IRON[3]), (4, 1, IRON[2]), (4, 2, IRON[2]), (4, 3, IRON[1]),
                        (0, 4, IRON[2]), (1, 4, IRON[2]), (2, 4, IRON[1]), (3, 4, IRON[1]), (4, 4, IRON[1])):
        r.fixed(bx + dx, by + dy, c)
    for (dx, dy) in ((1, 1), (2, 1), (3, 1), (1, 2), (2, 2), (3, 2), (1, 3), (2, 3), (3, 3)): r.darken(bx + dx, by + dy, 0.1)
    band(r, [(78.5, 112), (78.0, 127), (77.4, 141)], 4.6, M['coat'], 'beltail', lift=0.02,
         vfun=lambda x, y, s: (0.1 if s < -0.6 else 0) + (-0.14 if y in (124, 125) else 0))
    seam(r, 'beltail', 0.24)
    for (dx, dy) in ((0, 0), (1, -1), (2, -1), (3, -1), (4, 0), (4, 1), (4, 2), (3, 3), (2, 3), (1, 3), (0, 2), (0, 1)):
        c = IRON[5] if (dx >= 2 and dy <= 0) else (IRON[2] if dy >= 2 or dx == 0 else IRON[4])
        r.fixed(75 + dx, 142 + dy, c)
    strap = [(42, U(92)), (52, U(100)), (63, 109), (74, 116), (84, 119.5), (92, 120)]
    band(r, strap, 5.2, M['strap'], 'strap', lift=-0.06,
         vfun=lambda x, y, s: (0.14 if s < -0.55 else 0) + (-0.1 if s > 0.7 else 0) + (-0.1 if h32(x, y, 5) % 7 == 0 else 0)
         + (nS(x * 2, y * 2) - 0.5) * 0.2)
    seam(r, 'strap', 0.24)
    stitch(r, spline([(42.5, U(90.5)), (52.5, U(98.5)), (63.5, 107.5), (74.5, 114.5), (84.5, 118)]), 0.12, 3)
    sx, sy = 56, U(103)
    for (ex, ey) in ((-2, -2), (-1, -2), (0, -2), (1, -2), (2, -1), (2, 0), (2, 1), (1, 2), (0, 2), (-1, 2), (-2, 1), (-2, 0), (-2, -1)):
        r.fixed(sx + ex, sy + ey, IRON[5] if (ey < 0 and ex > -2) or ex > 1 else IRON[2])
    r.fixed(sx, sy, STRAP[1]); r.fixed(sx + 1, sy, STRAP[2])


def upper_coat(r, P):
    """the coat open at the top: the collar standing round the back of the neck (a clear lit edge under the chin), wide
    notched lapels falling open, and in the V between them the dark shirt and waistcoat; the patch pocket on the breast"""
    b = P.get('b', 0)
    U = lambda y: y - b
    # the collar round the back of the neck, seen at both sides under the head
    r.poly([(41, U(71)), (43, U(64)), (50, U(61)), (76, U(60)), (86, U(62)), (92, U(69)), (84, U(70)), (72, U(66)), (54, U(67)), (47, U(71))],
           M['coat'], lift=0.04, group='collar', vfun=lambda x, y: (0.16 if y <= U(62) else 0) - (0.1 if x < 50 else 0))
    seam(r, 'collar', 0.2)
    for x in range(42, 92):                                   # its turned edge catches the light
        ys = [y for y in range(U(58), U(73)) if r.buf.get((x, y)) and r.groups[r.buf[(x, y)][2]] == 'collar']
        if ys: r.darken(x, min(ys), -0.18); r.darken(x, min(ys) + 1, -0.08)


def head_shadow(r, P):
    """(after the head) the head's shadow on the collar and the coat's shoulders under the jowls"""
    for x in range(40, 92):
        ys = [y for y in range(40, 80) if r.buf.get((x, y)) and r.groups[r.buf[(x, y)][2]] == 'head']
        if not ys: continue
        yb = max(ys)
        for k, dv in ((1, 0.2), (2, 0.12), (3, 0.06)):
            e = r.buf.get((x, yb + k))
            if e and e[0] is not None and r.groups[e[2]] in ('collar', 'coatW', 'coatF', 'lapelW', 'lapelF', 'shirt', 'neck'): e[1] -= dv


def front_v(r, P):
    """(drawn after the neck) the dark V: the shirt at the throat, the waistcoat below with its buttons; the lapels"""
    b = P.get('b', 0)
    U = lambda y: y - b
    r.poly([(54, U(66)), (71, U(66)), (68, U(78)), (62.5, U(85)), (57, U(78))], M['shirt'], lift=-0.16, group='shirt',
           vfun=lambda x, y: (0.12 if y <= U(67) else 0) + (-0.16 if abs(x + 0.5 - 62.5) < 1 and y > U(70) else 0))
    seam(r, 'shirt', 0.14)
    r.poly([(53, U(73)), (58, U(80)), (62.5, U(86)), (67, U(80)), (72, U(73)), (70, U(100)), (62.5, U(104)), (55, U(100))], M['vest'], group='vest',
           vfun=lambda x, y: (-0.16 if abs(x + 0.5 - 62.5) < 1 else 0) + (nS(x * 2, y * 2) - 0.5) * 0.12)
    for y in (90, 96):
        r.fixed(62, U(y), VEST[5]); r.fixed(63, U(y), VEST[3]); r.fixed(62, U(y) + 1, VEST[1])
    # the far lapel: in the shadow, its rolled inner edge catching a little light
    r.poly([(42, U(69)), (52, U(66)), (57, U(79)), (62.5, U(104)), (57, U(101)), (48, U(85)), (44, U(76))], M['coat'], lift=-0.04, round_=0.5,
           group='lapelW', vfun=lambda x, y: (0.16 if abs(x + 0.5 - (52 + (y - U(66)) * 0.28)) < 1.2 else 0) - (0.1 if x < 47 else 0))
    # the near lapel: broad, lit, notched
    r.poly([(73, U(66)), (84, U(64)), (88, U(70)), (93, U(73)), (87, U(85)), (64, U(105)), (62.5, U(104)), (69, U(84))], M['coat'], lift=0.22,
           round_=0.5, group='lapelF', vfun=lambda x, y: (0.14 if abs(x - (92 - (y - U(74)) * 0.92)) < 1.6 else 0)
           + (-0.12 if abs(x + 0.5 - (73 - (y - U(66)) * 0.28)) < 1.2 else 0))
    seam(r, 'lapelW', 0.24); seam(r, 'lapelF', 0.3)
    for (x, y) in ((87, U(69)), (88, U(70)), (88, U(71))): r.darken(x, y, 0.32)            # the notch
    for k in range(16):                                                                        # the near lapel's shadow on the chest
        t = k / 15
        x, y = 93 - (93 - 65) * t, U(74) + (U(105) - U(74)) * t
        r.darken(x + 1, y + 1, 0.16); r.darken(x + 1, y + 2, 0.08)
    # the chest pocket beside the lapel
    r.poly([(80, U(88)), (93, U(87)), (93, U(100)), (81, U(101))], M['coat'], lift=0.06, round_=0.4, group='pocketC',
           vfun=lambda x, y: (-0.1 if y > U(98) else 0))
    r.poly([(79, U(86)), (94, U(85)), (94, U(90)), (80, U(91))], M['coat'], lift=0.14, round_=0.5, group='flapC',
           vfun=lambda x, y: -0.16 if y == U(90) else 0)
    seam(r, 'pocketC', 0.18); seam(r, 'flapC', 0.22)
    r.fixed(86, U(90), COAT[3]); r.fixed(87, U(90), COAT[7])


def neck(r, P):
    """a short, thick neck of dark fur between the jaw and the collar"""
    b, nod = P.get('b', 0), P.get('nod', 0)
    r.tube((61.5, 58 - b + nod * 0.5), (62.5, 72 - b), 10.5, 10.0, M['fur'], lift=-0.24, jag=0.08, group='neck')


def hip_pockets(r, P):
    for (x0, x1, y0, g, lift) in ((40, 54, 121, 'pocketW', -0.16), (84, 99, 122, 'pocketF', 0.03)):
        r.poly([(x0, y0), (x1, y0 - 0.5), (x1 + 0.5, y0 + 17), (x0 + 0.5, y0 + 17.5)], M['coat'], lift=lift, round_=0.5, group=g,
               vfun=lambda x, y, y0=y0: (-0.1 if y > y0 + 14 else 0) + (-0.12 if nB(x * 1.5, y * 1.5) > 0.7 else 0))
        r.poly([(x0 - 0.5, y0 - 1), (x1 + 0.5, y0 - 1.5), (x1 + 0.5, y0 + 3.5), (x0 - 0.5, y0 + 4)], M['coat'], lift=lift + 0.04, round_=0.5,
               group=g + 'flap', vfun=lambda x, y, y0=y0: -0.16 if y == y0 + 3 else 0)
        seam(r, g, 0.1); seam(r, g + 'flap', 0.14)


def sleeve_near(r, P):
    """the near sleeve hanging straight at his side: heavy cloth, a crease into the elbow, bunching above the cuff"""
    b = P.get('b', 0)
    U = lambda y: y - b if y < 112 else y
    pts = [(89, U(73)), (95, U(70.5)), (100, U(72.5)), (104, U(78)), (106, U(87)), (106.5, U(100)), (105, 110), (102.5, 119), (88.5, 120), (89, 110),
           (89, U(98)), (88, U(85))]
    def vf(x, y):
        v = 0.0
        for (y0, x0, x1, dv) in ((97, 92, 104, 0.24), (101, 95, 105, 0.2), (106, 91, 101, 0.16)):      # elbow creases
            yy = U(y0) + (x - x0) * 0.35
            if x0 <= x <= x1 and abs(y + 0.5 - yy) < 0.8: v -= dv
            if x0 <= x <= x1 and 0.8 <= y + 0.5 - yy < 2.0: v += dv * 0.4
        if y >= 113: v += 0.1 if y < 115 else (0.04 if y < 119 else 0)                                 # the turned cuff
        if y == 112: v -= 0.18
        if x < 91: v -= 0.1
        return v
    r.poly(pts, M['coat'], round_=0.8, group='armF', vfun=vf)
    seam(r, 'armF', 0.26)


def sleeve_far(r, P):
    """the far sleeve: the upper arm down his side, the forearm coming toward us to the sack, the cuff seen end-on"""
    b = P.get('b', 0)
    U = lambda y: y - b
    pts = [(45, U(69)), (40, U(71)), (36, U(76)), (34.5, U(83)), (33.5, U(92)), (34, U(102)), (38, U(108)), (46, U(108)), (47.5, U(96)), (47, U(80))]
    def vf(x, y):
        v = -0.04
        for (y0, x0, x1, dv) in ((U(96), 35, 46, 0.22), (U(100), 36, 46, 0.16)):
            yy = y0 - (x - x0) * 0.3
            if x0 <= x <= x1 and abs(y + 0.5 - yy) < 0.8: v -= dv
        return v
    r.poly(pts, M['coat'], round_=0.85, group='armW', vfun=vf)
    seam(r, 'armW', 0.2)
    r.ellipsoid(36.0, U(101.5), 5.2, 6.8, M['coat'], lift=-0.06, group='cuffW',                     # the cuff turned toward us
                vfun=lambda x, y, u, w: -0.2 if u * u + w * w < 0.3 else 0)
    seam(r, 'cuffW', 0.2)


def shoulder_patch(r, P):
    """a worn leather patch sewn over the near shoulder (the old coat's rust-brown spot)"""
    b = P.get('b', 0)
    cx, cy = 96, 79 - b
    pts = [(cx - 5, cy - 5), (cx + 3, cy - 7), (cx + 7, cy - 1), (cx + 6, cy + 8), (cx - 3, cy + 9), (cx - 6, cy + 3)]
    r.poly(pts, M['patch'], lift=0.02, round_=0.8, group='patch',
           vfun=lambda x, y: (-0.1 if h32(x, y, 9) % 5 == 0 else 0) + (-0.12 if nS(x * 2, y * 2) > 0.6 else 0) + (0.06 if nS(x * 2 + 9, y * 2) > 0.7 else 0))
    stitch(r, pts + [pts[0]], 0.12, 3)


def paw_side(r, c, P):
    """the left paw hanging by the hip: the broad back of the paw toward us, four thick fingers curled a little,
    short dark claws, the thumb turned to the coat"""
    x, y = c
    r.ellipsoid(x - 7.2, y + 1.5, 2.8, 4.8, M['paw'], lift=-0.1, rot=0.25, group='thumbF')
    r.ellipsoid(x, y, 8.2, 8.6, M['paw'], lift=-0.04, group='pawF', jag=0.08, vfun=lambda xx, yy, u, w: 0.06 if w < -0.3 else 0)
    for k in range(4):
        fx = x - 5.4 + k * 3.6
        fy = y + 6.8 - abs(k - 1.6) * 0.9
        r.ellipsoid(fx, fy, 2.4, 3.5, M['paw'], lift=-0.06 - abs(k - 1.6) * 0.03, group='fingF%d' % k)
        seam(r, 'fingF%d' % k, 0.16)
        r.fixed(fx - 0.5, fy + 3.4, CLAW[1]); r.fixed(fx + 0.5, fy + 3.4, CLAW[0])
    seam(r, 'thumbF', 0.1)


def sack(r, c, P):
    """a tied burlap sack, pear-shaped and lumpy: the gathered mouth flaring above the paw, the body hanging under it
    and swinging on its neck"""
    x, y = c                                           # (x, y) = the tie, inside the paw
    sw = P.get('sway', 0)
    rot = -0.12 * sw
    bx, by = x + 0.5 + sw * 1.6, y + 22
    def lumpy(xx, yy, u, w):
        v = (nS(xx * 1.6 + 11, yy * 1.6) - 0.5) * 0.26                                             # what is inside pushes out
        v += -0.24 if abs(u - 0.12 - w * 0.32) < 0.08 and w < 0.45 else 0                         # creases from the neck
        v += -0.2 if abs(u + 0.36 + w * 0.22) < 0.08 and w < 0.3 else 0
        v += -0.16 if w > 0.8 else 0
        return v
    r.tube((x, y + 3), (bx - 0.5 * sw, by - 9), 3.0, 7.6, M['sack'], group='sack',
           folds=lambda u, sd: (-0.22 if abs(sd - 0.1) < 0.12 else 0) + (-0.16 if abs(sd + 0.5) < 0.12 else 0))
    r.ellipsoid(bx, by - 1, 10.8, 10.4, M['sack'], rot=rot, group='sack', vfun=lumpy, jag=0.05)
    r.ellipsoid(bx - 0.6 + sw * 0.5, by + 4.2, 12.2, 7.4, M['sack'], rot=rot, group='sack', vfun=lumpy, jag=0.05)
    # an old patch sewn on with coarse stitches
    px, py = bx - 4 + sw, by + 3
    pts = [(px - 3, py - 3), (px + 3, py - 3.5), (px + 3.5, py + 3), (px - 3, py + 3.5)]
    for yy in range(int(py - 3), int(py + 4)):
        for xx in range(int(px - 3), int(px + 4)):
            e = r.buf.get((xx, yy))
            if e and e[0] is M['sack']: e[1] -= 0.14
    stitch(r, pts + [pts[0]], 0.2, 2)
    # the gathered mouth above the paw: the bunched cloth folded over in floppy, ragged flaps
    r.poly([(x - 4, y - 3), (x - 7, y - 7), (x - 9, y - 11), (x - 5, y - 13), (x - 1, y - 12), (x + 3, y - 14), (x + 7, y - 11), (x + 6, y - 7),
            (x + 4, y - 3)], M['sack'], lift=0.06, round_=0.85, group='sacktuft',
           vfun=lambda xx, yy: (-0.22 if abs((xx - x) - (yy - y + 5) * 0.3) < 0.7 else 0) + (-0.16 if abs((xx - x + 4) + (yy - y + 5) * 0.5) < 0.6 else 0)
           + (0.1 if yy < y - 10 else 0))
    seam(r, 'sacktuft', 0.16)


def paw_grip(r, c, P):
    """the right paw (viewer's left) closed round the sack's neck, the forearm toward us: one heavy furred fist, the
    curled fingers only parted by grooves on its outer face, short dark claws hooked into the burlap"""
    x, y = c
    r.ellipsoid(x, y, 6.8, 7.2, M['paw'], group='pawW', jag=0.07,
                vfun=lambda xx, yy, u, w: (0.08 if w < -0.45 and u > -0.3 else 0) + (-0.08 if u < -0.55 else 0))
    for k in range(3):                                                   # the grooves between the fingers, curving round
        gy = y - 3.2 + k * 3.2
        for xx in range(int(x - 6), int(x + 1)):
            t = (xx - (x - 6)) / 6
            r.darken(xx, gy + t * t * 1.2, 0.26 - t * 0.12)
            r.darken(xx, gy + t * t * 1.2 - 1, -0.06)
    for k in range(4):                                                   # the claws
        ty = int(y - 4.6 + k * 3.2)
        r.fixed(int(x - 7), ty, CLAW[1]); r.fixed(int(x - 7), ty + 1, CLAW[0])
    seam(r, 'pawW', 0.14)


def arms(r, P):
    b = P.get('b', 0)
    # the near arm hangs at his side, the paw by the hip pocket
    sleeve_near(r, P)
    shoulder_patch(r, P)
    paw_side(r, (93.5, 126.5), P)
    # the far arm: the elbow by his side, the forearm toward us and out to the sack
    sack(r, (27, 101 - b), P)
    sleeve_far(r, P)
    paw_grip(r, (28, 101 - b), P)


# ---- the head ---------------------------------------------------------------------------------------------------------
def _ell(x, y, cx, cy, rx, ry):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2


def _seg(x, y, a, b):
    """distance to segment a-b and the parameter t along it"""
    dx, dy = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dy * dy
    t = max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / L2))
    return math.hypot(x - a[0] - dx * t, y - a[1] - dy * t), t


nJ = make_noise(2, 214, 320, 320)


def head(r, P):
    """the head as one height field (a wide round skull, brows, jowls, jaw) with the muzzle as its own lighter volume
    on it, ending in the broad dark nose; then the features are painted in: small eyes under heavy drooping lids in dark
    sockets, a furrow between the raised inner brows, the mouth line sagging at the corners. It is big (about 28 % of
    his height), sits above the collar on a short neck, the ears high and wide on the skull."""
    b = P.get('b', 0)
    nod = P.get('nod', 0)
    dy = -b + nod
    ear = P.get('ear', 0)
    for (ex, ey, s) in ((46.0, 29.5, -1), (82.6 + ear * 0.8, 30.0 - ear * 1.4, 1)):
        r.ellipsoid(ex, ey + dy, 5.6, 5.4, M['fur'], jag=0.16, group='ear%d' % s, lift=0.0 if s > 0 else -0.08)
        r.ellipsoid(ex + s * 0.5, ey + dy + 1.0, 3.1, 3.2, M['ear'], lift=0.36 if s > 0 else -0.06, group='earin%d' % s,
                    vfun=lambda x, y, u, w: (-0.22 if w < -0.45 else 0) + (-0.1 if u * (1 if s > 0 else -1) < -0.5 else 0))
    cx, cy = 64.0, 43.0 + dy
    mA, mB = (60.8, 45.5 + dy), (58.4, 54.0 + dy)      # the snout: from under the eyes -> the nose
    MR0, MR1 = 5.0, 7.4
    def fields(x, y):
        hs = []
        ang = math.atan2(y - cy, x - cx)
        amp = (0.2 if x < cx else 0.13) * (0.35 + 0.65 * min(1.0, abs(math.cos(ang)) * 1.4))
        jag = (nJ(ang * 7 + 3, 2) - 0.5) * amp + (nJ(ang * 23, 9) - 0.5) * amp * 0.8
        d = _ell(x, y, cx, cy + 0.5, 21.8, 19.4)                                                   # the wide round skull
        if d < 1 + jag: hs.append((15.0 * math.sqrt(max(0.0, 1 - min(d, 1))), 'fur'))
        for (ccx, ccy, rx, ry, hz) in ((48.5, 53.0, 6.6, 8.6, 5.0), (79.5, 52.5, 7.2, 9.0, 5.0)):         # jowls
            d = _ell(x, y, ccx, ccy + dy, rx, ry)
            if d < 1 + jag * 1.6: hs.append((hz * math.sqrt(max(0.0, 1 - min(d, 1))) + 6, 'fur'))
        d = _ell(x, y, 60.0, 61.6 + dy, 10.6, 7.0)                                                  # the jaw, the heavy chin
        if d < 1 + jag: hs.append((7.0 * math.sqrt(max(0.0, 1 - min(d, 1))) + 8, 'fur'))
        for (bx_, by_, brx) in ((53.5, 39.4, 6.8), (70.5, 40.0, 7.2)):                              # a brow over each eye
            d = _ell(x, y, bx_, by_ + dy, brx, 2.8)
            if d < 1: hs.append((13.6 + 2.4 * math.sqrt(1 - d), 'fur'))
        dm, t = _seg(x, y, mA, mB)                                                                  # the muzzle
        rm = MR0 + (MR1 - MR0) * t
        if dm < rm: hs.append((15.0 + 2.5 * t + 4.6 * math.sqrt(max(0.0, 1 - (dm / rm) ** 2)), 'muz'))
        d = _ell(x, y, 58.4, 57.0 + dy, 7.4, 4.0)                                                   # the lip pads round the snout's end
        if d < 1: hs.append((16.5 + 4.0 * math.sqrt(1 - d), 'muz'))
        if not hs: return None
        return max(hs)
    oid = r.new('head')
    H = {}
    for y in range(int(cy - 24), int(cy + 30)):
        for x in range(36, 94):
            f = fields(x + 0.5, y + 0.5)
            if f: H[(x, y)] = f
    for (x, y), (h, m) in H.items():
        hl = H.get((x - 1, y), (h - 3, m))[0]; hr = H.get((x + 1, y), (h - 3, m))[0]
        hu = H.get((x, y - 1), (h - 3, m))[0]; hd = H.get((x, y + 1), (h - 3, m))[0]
        n = norm((-(hr - hl) * 0.5, -(hd - hu) * 0.5, 1.0))
        mat_ = M['muzzle'] if m == 'muz' else M['fur']
        lam = max(0.0, n[0] * LIGHT_H[0] + n[1] * LIGHT_H[1] + n[2] * LIGHT_H[2])
        v = mat_.amb + (1 - mat_.amb) * lam - 0.12
        dm, t = _seg(x + 0.5, y + 0.5, mA, mB)
        rm = MR0 + (MR1 - MR0) * t
        if m == 'fur':
            v -= 0.1                                                                                # dark fur round the paler muzzle
            if dm < rm + 1.6: v -= 0.14                                                             # the muzzle stands out of the face
            if dm < rm + 3.4 and x + 0.5 < mA[0] + (mB[0] - mA[0]) * t: v -= 0.06
            if x + 0.5 < mA[0] - 3 and abs(y + 0.5 - cy - 4) < 10: v += 0.05
            if x > 74 and y > cy + 4: v -= 0.06
            if y > cy + 20 and abs(x - 60) < 9: v -= 0.12                                           # the dark fur of the chin
        else:
            v += 0.08 + 0.08 * max(0.0, 1 - abs(y - (cy + 9)) / 5) - 0.1 * max(0.0, (y - (cy + 13)) / 4)   # tan, darker under the nose
        v -= 0.08 * max(0.0, (y - (cy + 16)) / 10)
        v -= 0.26 * max(0.0, (cy - 4 - y) / 15)                                                    # the crown turns away
        r.put(x, y, mat_, v, oid)
    # ---- painted features ----
    def fix(x, y, c): r.fixed(x, y, c)
    def tone(x, y, d):
        e = r.buf.get((int(math.floor(x)), int(math.floor(y))))
        if e and e[0] is not None: e[1] += d
    ey = int(44 + dy)
    eyes = [(53, ey, -1), (70, ey + 1, 1)]
    for (ex, eyy, s) in eyes:                                                                      # dark sockets
        for ddx in range(-4, 4):
            for ddy in range(-2, 3):
                if abs(ddx + 0.5) * 0.7 + abs(ddy) <= 3.3: tone(ex + ddx, eyy + ddy, -0.32 + 0.06 * abs(ddy))
    for (ex, eyy, s) in eyes:                                                                      # the brows: inner ends raised
        for k in range(-3, 5):
            inner = k * s < 0
            yy = eyy - 3 - (1 if inner and abs(k) >= 1 else 0) - (1 if inner and abs(k) >= 3 else 0) + (1 if nod else 0)
            tone(ex + k, yy, 0.22 if s > 0 else 0.12); tone(ex + k, yy - 1, 0.08 if s > 0 else 0.04)
    for yy in range(int(39 + dy), int(46 + dy)): tone(61, yy, 0.1); tone(62, yy, 0.06)
    for (fx_, fy_) in ((61, 37), (62, 38), (60, 38), (63, 37)):                                     # the furrow between the brows
        tone(fx_, fy_ + dy + (1 if nod else 0), -0.2)
    fix(61, int(36 + dy) + (1 if nod else 0), FUR[3]); fix(62, int(39 + dy) + (1 if nod else 0), FUR[3])
    for (ex, eyy, s) in eyes:
        X = lambda k: ex + k * s                                                                   # k > 0 = toward the outer corner
        lit = s > 0
        if P.get('blink'):                                                                         # the lid down: a lit fold, a dark line
            for k in (-2, -1, 0, 1): fix(X(k), eyy, LID); fix(X(k), eyy - 1, FUR[7] if lit else FUR[5])
            fix(X(2), eyy + 1, LID); fix(X(-1), eyy + 1, FUR[4]); fix(X(0), eyy + 1, FUR[4])
        else:
            for k in (-2, -1, 0, 1): fix(X(k), eyy - 2, FUR[6] if lit else FUR[4])                # the heavy lid's fold of fur
            fix(X(2), eyy - 1, FUR[6] if lit else FUR[4])
            for k in (-2, -1, 0, 1): fix(X(k), eyy - 1, LID)                                     # its lash line, low over the eye
            fix(X(2), eyy, LID); fix(X(3), eyy + 1, FUR[2])                                       # drooping at the outer corner
            fix(X(-2), eyy, FUR[3]); fix(X(-1), eyy, EYEC); fix(X(0), eyy, EYEC); fix(X(1), eyy, EYEC)
            fix(X(-1), eyy, GLINT if lit else (140, 122, 95))                                     # 1 px warm-grey glint
            fix(X(-1), eyy + 1, (40, 26, 16)); fix(X(0), eyy + 1, EYEC)                          # the iris' lower half
        for k in (-1, 0, 1): fix(X(k), eyy + 2, FUR[3] if lit else FUR[2])                        # a tired, dark bag under it
        fix(X(0), eyy + 3, FUR[4]); fix(X(1), eyy + 3, FUR[4])
    # the nose at the muzzle's tip: broad, dark, damp; a highlight from the right, the nostrils
    nx, ny = 58.4, 54.0 + dy
    r.ellipsoid(nx, ny, 5.2, 3.0, M['nose'], group='nose', vfun=lambda x, y, u, w: (0.14 if w < -0.35 else 0) - (0.1 if w > 0.5 else 0))
    nxi, nyi = int(nx), int(ny)
    fix(nxi - 3, nyi + 1, NOSE[0]); fix(nxi - 2, nyi + 1, NOSE[1]); fix(nxi + 2, nyi + 1, NOSE[0]); fix(nxi + 3, nyi + 1, NOSE[1])
    fix(nxi + 1, nyi - 2, NOSE[6]); fix(nxi + 2, nyi - 2, NOSE[5]); fix(nxi, nyi - 2, NOSE[4]); fix(nxi + 3, nyi - 1, NOSE[4])
    # the philtrum down the lip pads, the mouth line under them sagging at the corners, the lower lip, the chin's shadow
    my = int(60.8 + dy) + (1 if nod == 2 else 0)
    for yy in range(nyi + 3, my): fix(nxi, yy, MUZZLE[1])
    for k in range(-8, 9):                                     # flat across the middle, the corners dragged down
        yy = my + (1 if abs(k) >= 3 else 0) + (1 if abs(k) >= 5 else 0) + (1 if abs(k) >= 7 else 0)
        fix(nxi + k, yy, MUZZLE[0] if abs(k) < 3 else FUR[1])
        if abs(k) >= 3: tone(nxi + k, yy - 1, 0.08)            # the cheek fur over the sagging corner catches light
    for k in range(-2, 3): tone(nxi + k, my + 1, 0.06)          # the lower lip
    for k in range(-6, 7): tone(nxi + k, my + 2, -0.12); tone(nxi + k, my + 3, -0.1)
    return cx, cy


def edgar(P):
    r = EdgarRig(W, H)
    legs(r, P)
    coat(r, P)
    hip_pockets(r, P)
    upper_coat(r, P)
    neck(r, P)
    front_v(r, P)
    strap_and_belt(r, P)
    arms(r, P)
    head(r, P)
    head_shadow(r, P)
    im = r.render()
    px = im.load()
    for y in range(SOLE + 1, H):                     # the soles are the bottom: no outline row under them (as in the old sheet)
        for x in range(W): px[x, y] = (0, 0, 0, 0)
    return im


def sheet(frames, path):
    s = Image.new('RGBA', (W * len(frames), H), (0, 0, 0, 0))
    for i, im in enumerate(frames): s.paste(im, (i * W, 0))
    s.save(path)


if __name__ == '__main__':
    os.makedirs(f'{OUT}/edgar', exist_ok=True)
    frames = [edgar(p) for p in POSE]
    for i, im in enumerate(frames): im.save(f'{OUT}/edgar/{i}.png')
    sheet(frames, f'{OUT}/edgar.png')
    ALL = ([OUTL, EYEC, GLINT, LID] + FUR + MUZZLE + NOSE + COAT + COATF + VEST + STRAP + PATCH + SACK + SHIRT + TROU + BOOT + BOOTD + CLAW + IRON)
    seen, rows = set(), []
    for c in ALL:
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/edgar_rig.gpl', 'w').write('GIMP Palette\nName: edgar_rig\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT, len(rows), 'colours')
