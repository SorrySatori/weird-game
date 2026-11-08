"""The Gang of Lamps (utils/GangOfLamps.js) -- four sentient street-lamps hiding among the city's own lamps, redrawn as
pixel sheets after the old AI images (Chandelier.png, Sconce.png, Torchere.png, don_girandole.png; all four are now
unused). Each one is a believable member of its district's lamp family -- the same ironwork, glass and light as the
lamps painted into its background -- and shows only small signs of life: a flame that looks round, glints that travel,
a slight lean, a nervous rattle.

  sconce     128x176, TownhallScene (exterior) -- the near-twin of the painted cast-iron lamp at the other side of the
             stair (townhall_bg.py lamp(): base box, fluted pedestal, collar, slim post, four-pane lantern, cap plate,
             dome), built to the same numbers; only its lantern is a little BRASS lamp bolted onto the post (the
             dialog's "little brass lamp bolted to a post"), and the flame inside sits right behind the middle bar,
             so it reads as two small lit eyes. Nervy: the flame darts left to the townhall door and back, ducks, and
             once the brass lamp rattles on its bolts.
  chandelier 128x216, TownSquareScene -- the square has no lamp posts, only caged wall lanterns of blue-grey painted
             iron; she is the one ornate post, in the same blue-grey iron, crowned with an antique-gilt crystal
             chandelier (a frosted globe, six scrolled arms with tulip shades, festoons and pendants of crystal drops).
             Aloof: the whole post leans a little toward the square, the glints run round the lustres, the hot spot in
             the globe looks about, one pendant swings.
  torchere   128x192, HarborScene -- the dock's lamp family (harbor_bg.py: an iron-banded post, a twisted iron finial
             like a splayed hand, a cage lantern): a tall rust-streaked iron post bolted to the planks with banded
             collars, a coil of tarred rope on a hook, a drip pan and an open storm cage with the twisted finial, and in
             it a bare oil flame snapping sideways in the sea wind; it rounds on you, flares, spits sparks.
  don        45x56 LOGICAL, shown at scale 3 in ScraperScene -- Scraper1140.png is the one background with 3x pixels
             (a re-pixelled picture, scraper_bg.py), so Don is drawn on that grid and quantised to its palette
             (scraper.gpl). The godfather: a lamp-headed man in a dark brown suit and tie, white gloves, on a lamp
             post's foot; turned three-quarters to the left, one hand in his pocket (that shoulder lower), the other
             holding a cigar, the head-lamp lighting his own shoulders; the flame in it turns to look, the ember
             breathes, smoke curls up.

Every sheet is a horizontal strip of 8 idle frames (frame meanings in IDLE_NOTES); the game shows them at scale 1
(Don 3), origin bottom-centre; the base's lowest row is H-3 (Don: H-1). Bust portraits are frames of the same sheets
(utils/GangOfLamps.js LAMP_ART).
python3 lamps.py <outdir> [ids...]  ->  <id>.png (sheet) + <id>/<n>.png + lamps.gpl + preview_<id>.png"""
import sys, os, math, random
from PIL import Image
from common import ramp, h32
import rig
from rig import Rig, Mat, norm

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
ONLY = sys.argv[2:]
R = ramp
BAYER = rig.BAYER
TAU = 2 * math.pi


def mix(a, b, t): return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))
def dith(x, y): return BAYER[int(y) % 4][int(x) % 4] / 16 - 0.47
def pick(rmp, v, x, y, amp=0.85):
    i = v * (len(rmp) - 1) + dith(x, y) * amp
    return rmp[max(0, min(len(rmp) - 1, int(round(i))))]


def warmed(rmp, k=0.5, tint=(238, 178, 86)):
    """the same ramp lit by a warm lamp: each step pulled toward the lamp's colour at its own brightness"""
    out = []
    for i, c in enumerate(rmp):
        t = i / (len(rmp) - 1)
        tgt = tuple(min(255, int(tint[j] * (0.22 + 0.9 * t))) for j in range(3))
        out.append(mix(c, tgt, k * (0.35 + 0.65 * t)))
    return out


# materials shared by the three 1x lamps
RUSTY = R('#24120a #3a1d10 #552a16 #6f381d #8a4a26 #a35e33')          # shedkit's RUSTY: orange-brown, never crimson
WARMOUT = (20, 17, 15)

rig.TEX['cast'] = lambda x, y: ((rig.nM(x * 1.5, y * 1.5) - 0.5) * 0.10 + (rig.nF(x * 2.1, y * 2.1) - 0.5) * 0.05
                                - (0.07 if h32(x, y, 31) % 29 == 0 else 0))                 # cast iron: pitted, mottled paint
rig.TEX['gilt'] = lambda x, y: (rig.nF(x * 1.8, y * 1.8) - 0.5) * 0.08 + (0.06 if h32(x, y, 32) % 37 == 0 else 0)
rig.TEX['rust'] = lambda x, y: (rig.nM(x * 2.0, y * 1.2) - 0.5) * 0.16 + (rig.nF(x * 2.6, y * 2.6) - 0.5) * 0.08
rig.TEX['rope'] = lambda x, y: (0.07 if (x + y) % 3 == 0 else -0.03) + (rig.nF(x * 2, y * 2) - 0.5) * 0.08


def mat(rmp, tex='cast', amb=0.14, spec=0.0, outline=WARMOUT): return Mat(rmp, tex, amb, spec, outline=outline)


class Lamp(Rig):
    """rig.Rig + a depth buffer and a little perspective: B = the floor row, the axis leans `lean` px over `htot` px,
    and a horizontal circle at height b (px above the floor) is seen as an ellipse whose depth ratio is
    (beye - b) / F -- the same camera as the background (beye = the feet's canvas y - the horizon 296)."""
    def __init__(s, w, h, B, cx, F, beye, lean=0.0, htot=200.0):
        super().__init__(w, h)
        s.B, s.cx, s.F, s.beye, s.lean, s.htot = B, cx, F, beye, lean, htot
        s.zb = {}

    def axis(s, b): return s.cx + s.lean * b / s.htot
    tilt = None                                                                  # (b0, extra): a head shown a little from above
    def ratio(s, b):
        r_ = (s.beye - b) / s.F
        if s.tilt and b >= s.tilt[0]: r_ += s.tilt[1]
        return r_
    def proj(s, X, b, Z):
        """X right of the axis, b up from the floor, Z toward the viewer -> canvas x, y"""
        return s.axis(b) + X, s.B - b + Z * s.ratio(b)

    def zput(s, x, y, mat_, v, oid, d, fixed=None):
        k = (int(math.floor(x)), int(math.floor(y)))
        if not (0 <= k[0] < s.w and 0 <= k[1] < s.h): return
        if k in s.zb and s.zb[k] > d: return
        s.zb[k] = d
        s.buf[k] = [mat_, v, oid, fixed]

    def fill(s, pts, mat_, n=(0, 0, 1), lift=0.0, vfun=None, d=0.0, group=None, fixedf=None):
        """a flat polygon (canvas coords) with one normal; fixedf(x, y) -> colour or None overrides the shading"""
        oid = s.new(group); n = norm(n)
        ys = [p[1] for p in pts]
        for y in range(int(math.floor(min(ys))), int(math.ceil(max(ys))) + 1):
            yc, xs = y + 0.5, []
            for i in range(len(pts)):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
                if (y0 <= yc < y1) or (y1 <= yc < y0): xs.append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(math.ceil(xs[i] - 0.5)), int(math.floor(xs[i + 1] - 0.5)) + 1):
                    if fixedf:
                        c = fixedf(x, y)
                        if c is not None: s.zput(x, y, None, 0, oid, d, c); continue
                    s.zput(x, y, mat_, s.shade(mat_, n, lift) + (vfun(x, y) if vfun else 0), oid, d)
        return oid

    def lathe(s, prof, mat_, lift=0.0, tex=None, group=None, dz=0.0, ox=0.0, oz=0.0, step=0.33, fixedf=None):
        """a solid of revolution round the (leaning) axis; prof = [(r, b), ...] from the bottom up (outward normal on
        the right of the direction of travel). tex(x, y, th, b) -> tone offset (fluting, rings, stains)."""
        oid = s.new(group)
        for i in range(len(prof) - 1):
            (r0, b0), (r1, b1) = prof[i], prof[i + 1]
            L = math.hypot(r1 - r0, b1 - b0)
            if L < 1e-6: continue
            nr, nb = (b1 - b0) / L, -(r1 - r0) / L
            ns = max(1, int(L / step) + 1)
            for k in range(ns + 1):
                t = k / ns
                r_, b_ = r0 + (r1 - r0) * t, b0 + (b1 - b0) * t
                nth = max(8, int(TAU * r_ / step) + 1)
                for j in range(nth):
                    th = TAU * j / nth
                    c, sn = math.cos(th), math.sin(th)
                    x, y = s.proj(ox + r_ * c, b_, oz + r_ * sn)
                    n = (nr * c, -nb, nr * sn)
                    v = s.shade(mat_, n, lift) + (tex(x, y, th, b_) if tex else 0)
                    if fixedf:
                        col = fixedf(x, y, th, b_, n)
                        if col is not None: s.zput(x, y, None, 0, oid, oz + r_ * sn + dz, col); continue
                    s.zput(x, y, mat_, v, oid, oz + r_ * sn + dz)
        return oid

    def tube3(s, pts, rad, mat_, lift=0.0, group=None, dz=0.0, vfun=None, color=None):
        """a round bar along a 3D polyline [(X, b, Z), ...]; rad may be a number or a function of the fraction"""
        oid = s.new(group)
        P = [s.proj(*p) + (p[2],) for p in pts]
        segs = [math.hypot(P[i + 1][0] - P[i][0], P[i + 1][1] - P[i][1]) for i in range(len(P) - 1)]
        tot = sum(segs) or 1e-6
        acc = 0.0
        for i in range(len(P) - 1):
            (x0, y0, z0), (x1, y1, z1) = P[i], P[i + 1]
            n = max(1, int(segs[i] / 0.3) + 1)
            for k in range(n + 1):
                t = k / n
                f = (acc + segs[i] * t) / tot
                rr = rad(f) if callable(rad) else rad
                cx_, cy_, cz = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t
                for y in range(int(cy_ - rr) - 1, int(cy_ + rr) + 2):
                    for x in range(int(cx_ - rr) - 1, int(cx_ + rr) + 2):
                        dx, dy = x + 0.5 - cx_, y + 0.5 - cy_
                        dd = dx * dx + dy * dy
                        if dd > rr * rr + 0.12: continue
                        if color is not None: s.zput(x, y, None, 0, oid, cz + dz, color); continue
                        u, w = dx / max(rr, 0.5), dy / max(rr, 0.5)
                        nn = (u, w, math.sqrt(max(0.0, 1 - min(1.0, u * u + w * w))))
                        s.zput(x, y, mat_, s.shade(mat_, nn, lift) + (vfun(x, y, f) if vfun else 0), oid, cz + dz + nn[2] * rr * 0.5)
            acc += segs[i]
        return oid

    def glow(s, x, y, colour, d=0.0, oid=None):
        s.zput(x, y, None, 0, oid or s.n, d, colour)

    # ---- post passes on the tone buffer (before render) -------------------------------------------------------
    def relight(s, cx, cy, rad, gain, swap, mask=None):
        """warm light from a lamp: tone up + the material swapped for its warm-lit twin, falling off with distance"""
        for (x, y), e in s.buf.items():
            m = e[0]
            if m is None or m not in swap: continue
            d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.1)
            if d > rad: continue
            k = (1 - d / rad) ** 1.6 * (mask(x, y) if mask else 1.0)
            if k <= 0.02: continue
            e[1] += gain * k
            if k > 0.18 + 0.25 * (dith(x, y) + 0.47): e[0] = swap[m]

    def rust(s, sources, swap, seed=0):
        """rust running down by gravity from bolts and seams: (x, y, length, strength, width) per source"""
        rnd = random.Random(seed)
        for (sx, sy, L, st, wd) in sources:
            xo = 0.0
            for dy in range(int(L)):
                if rnd.random() < 0.18: xo += rnd.choice((-0.5, 0.5))
                fall = (1 - dy / L) ** 1.2 * st
                for w in range(int(wd)):
                    x, y = int(round(sx + xo + w - (wd - 1) / 2)), int(sy + dy)
                    e = s.buf.get((x, y))
                    if not e or e[0] is None or e[0] not in swap: continue
                    if fall * (0.65 + 0.7 * rig.nF(x * 3.1, y * 0.7)) > dith(x, y) + 0.62:
                        e[0] = swap[e[0]]; e[1] += 0.05

    def speckle(s, swap, p, seed=0, region=None):
        for (x, y), e in s.buf.items():
            if e[0] is None or e[0] not in swap: continue
            if region and not region(x, y): continue
            if rig.nM(x * 2.3 + seed, y * 2.3) > 1 - p and h32(x, y, seed) % 3: e[0] = swap[e[0]]


def ellipse_pts(cx, cy, rx, ry, a0=0, a1=TAU, n=40):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * k / n), cy + ry * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]


# ======================================================================================================== SCONCE
# townhall_bg.py: F 600, the lamps' feet at canvas y 446 -> beye 150. The painted twin, measured off townhall.png at
# canvas x 430 (b = px above its base's front edge, canvas y 449): base box b 0-8 + a 4 px top face, fluted pedestal
# b 12-47 (17 wide), collar b 47-53 (17 + a 3 px side), post b 53-119 (7.5 wide) with a small collar at b 77-83, the
# lantern-lit collar b 119-124, the lantern b 124-145 (frame 1 + panes 4/5/5/4 between three 3 px bars + frame 1, and a
# glowing 3 px side face), the cap plate b 145-150 (37 + 4), the dome b 150-166 (26 wide). The twin stands left of the
# vanishing point and shows its right side faces; Sconce stands right of it and shows its left ones.
TH_IRON = R('#0b0c0c #101313 #151919 #1a1e1e #1f2323 #242928 #2a2f2e #303533 #373c39 #40453f #4b5049 #575c53')
TH_BRASS = R('#1e1608 #2e220c #3f2f11 #523e17 #69501f #82662a #9c7e38 #b4964a #ccb064')
TH_GLASS = R('#a87a34 #c08e40 #d0a04a #dcb054 #e6bc5a #ecc25c #f0c660 #f4ce6c #f8da88 #fde8b0')
TH_FLAME = R('#f2b04a #f8c862 #fcdc8e #fff0c4 #fffaea')
SC = dict(W=128, H=176, B=172, cx=64)


def sconce(P):
    W, H, B, cx = SC['W'], SC['H'], SC['B'], SC['cx']
    s = Lamp(W, H, B, cx, F=600.0, beye=150.0, lean=-1.0, htot=166.0)
    IRON = mat(TH_IRON, 'cast', 0.10, 0.08)
    IRONL = mat(warmed(TH_IRON, 0.8), 'cast', 0.10, 0.08)
    RUST = mat(RUSTY[:4], 'rust', 0.12)
    BR = mat(TH_BRASS, 'metal', 0.12, 0.5)
    BRL = mat(warmed(TH_BRASS, 0.45, (255, 214, 140)), 'metal', 0.14, 0.5)
    X = s.axis
    rt = P.get('rattle', 0)

    def box(b0, b1, xl, xr, sw, dv, m, lift=0.0, vfun=None, d=0.0, side_lift=0.04, top_lift=0.1, ox=0.0):
        """a cast-iron box seen from right of the vanishing point: the front face [xl, xr] (px from the axis), the
        left side face sw px wide, and a top face dv px deep whose back edge leans sw px toward the VP"""
        xa0, xa1 = X(b0) + ox, X(b1) + ox
        if sw > 0:
            s.fill([(xa0 + xl, B - b0), (xa1 + xl, B - b1), (xa1 + xl - sw, B - b1 - dv), (xa0 + xl - sw, B - b0 - dv)],
                   m, (-1, 0, 0.5), lift + side_lift, d=d - 2)
        if dv > 0:
            s.fill([(xa1 + xl, B - b1), (xa1 + xr, B - b1), (xa1 + xr - sw * 1.2, B - b1 - dv), (xa1 + xl - sw, B - b1 - dv)],
                   m, (0, 0, 1), lift + top_lift, d=d - 1)
        s.fill([(xa0 + xl, B - b0), (xa0 + xr, B - b0), (xa1 + xr, B - b1), (xa1 + xl, B - b1)], m, (0, 0, 1), lift,
               vfun=vfun, d=d)

    # -- the base box (its foot damp and grimy)
    box(0, 8, -9.5, 12.5, 3, 4, IRON, lift=-0.16, vfun=lambda x, y: -0.12 * max(0, (y - (B - 3)) / 3) - 0.06 * ((x - X(0)) / 12), d=-8)
    # -- the fluted pedestal: a plinth moulding, six flutes, a joint every 12 px, the left lit
    box(12, 14, -8.5, 10, 1, 1, IRON, lift=-0.04, d=-6)
    def flutes(x, y):
        b = B - y
        u = (x + 0.5 - X(b) - 1.2) / 8.5
        return -0.22 * u - (0.16 if (u * 3 + 3) % 1 < 0.25 else 0) + (0.07 if b % 12 > 10.4 else 0) - 0.08 * max(0, (30 - b) / 18)
    box(14, 47, -7.3, 9.7, 0, 0, IRON, lift=-0.06, vfun=flutes, d=-5)
    # -- the collar box on the pedestal
    box(47, 53, -6.5, 10.5, 3, 3, IRON, lift=0.0, d=-6, top_lift=0.16)
    # -- the post, a slim round bar, with its small collar
    s.lathe([(3.9, 53), (3.75, 90), (3.6, 119)], IRON, lift=-0.04)
    box(77, 83, -4.5, 6.5, 2, 1, IRON, lift=0.0, d=2)
    # -- the collar under the lantern (catches the lantern's light)
    box(119, 124, -5.5, 7.5, 2, 0, IRON, lift=0.02, d=2)
    # brass bolts holding the little lamp on
    for bx in (-3.5, 5.0):
        s.fill(ellipse_pts(X(121) + bx, B - 121.5, 1.1, 1.1), BR, (-0.5, -0.6, 1), 0.3, d=4)

    # -- the lantern: a little brass lamp bolted on, four panes, the flame right behind the middle bar
    lb0, lb1 = 124, 145
    lx = rt                                                                      # the rattle shifts the lamp a px
    L0 = X(134) + lx - 13.0                                                      # the front face's left edge
    BARS = [(L0 + 5, L0 + 8), (L0 + 13, L0 + 16), (L0 + 21, L0 + 24)]             # panes 4/5/5/4 between 3 px bars
    fx = X(134) + lx + 1.5 + P.get('fx', 0)
    fy = B - 131.5 - P.get('fy', 0)
    fs, bright = P.get('fs', 1.0), P.get('bright', 1.0)
    def hot(x, y):
        dx, dy = (x + 0.5 - fx) / (3.6 * fs), (y + 0.5 - fy) / (4.6 * fs)
        return math.exp(-(dx * dx + dy * dy) * 1.3) * bright
    def glass(x, y, side=False):
        xc, yc = x + 0.5, y + 0.5
        if not side and (xc < L0 + 1 or xc > L0 + 28 or any(a <= xc < b for a, b in BARS)): return None
        if yc < B - lb1 + 1.5 or yc > B - lb0 - 1.5: return None
        tt = (yc - (B - lb1)) / (lb1 - lb0)
        h = hot(x, y)
        v = 0.52 + 0.06 * tt - 0.36 * max(0, 0.2 - tt) / 0.2 + 0.46 * h * h
        if side: v = 0.22 + 0.12 * tt + 0.25 * h
        fdx, fdy = (xc - fx) / (2.6 * fs), (yc - fy - 1.2) / (4.2 * fs)
        tear = fdx * fdx * (1.8 if fdy < 0 else 1.0) + fdy * fdy
        if not side and tear < 1.0:
            return pick(TH_FLAME, 0.25 + 0.75 * (1 - tear) * bright, x, y, 0.5)
        return pick(TH_GLASS, v, x, y, 0.6)
    def frame_v(x, y):          # dark brass bars; only the edge turned to the flame catches it
        xc = x + 0.5
        lit = any((b - 1.0 <= xc < b and xc < fx + 1) or (a <= xc < a + 1.0 and xc > fx - 1) for a, b in BARS)
        return (0.10 + 0.40 * hot(x, y) if lit else 0.04 * hot(x, y))
    s.fill([(L0 - 3, B - lb0), (L0, B - lb0), (L0, B - lb1), (L0 - 3, B - lb1)],
           BR, (-1, 0, 0.4), -0.05, d=0, fixedf=lambda x, y: glass(x, y, True) if x + 0.5 > L0 - 2.4 else None)
    s.fill([(L0, B - lb0), (L0 + 29, B - lb0), (L0 + 29, B - lb1), (L0, B - lb1)],
           BR, (0, 0, 1), -0.24, d=3, fixedf=glass, vfun=frame_v)
    # -- the cap plate and the dome: the twin's cast iron
    box(145, 150, -16.5, 20.5, 4, 0, IRON, lift=0.04, d=0, side_lift=0.02)
    cy0 = B - 150
    s.ellipsoid(X(150) + 1.0, cy0, 13.0, 16.0, IRON, lift=-0.06, flat=0.9, clip=lambda x, y: y + 0.5 <= cy0,
                vfun=lambda x, y, u, w: (0.05 if (u < -0.35 and -0.8 < w < -0.4) else 0) - 0.05 * max(0, w + 0.3) * 3)

    # light: the lantern lights the collar under it (the twin's pale collar) and the cap plate's front a little
    swap = {IRON: IRONL, BR: BRL}
    s.relight(fx, B - lb0, 16, 0.55 * bright, swap, mask=lambda x, y: 1.0 if B - lb0 <= y <= B - 118 else 0.0)
    # a little rust weeping from the collars' seams and the base box's corners
    rsw = {IRON: RUST}
    s.rust([(X(53) - 4, B - 47, 12, 0.40, 1), (X(53) + 7, B - 47, 8, 0.32, 1), (X(83) + 3, B - 77, 8, 0.32, 1),
            (X(8) - 7, B - 8, 6, 0.40, 1), (X(8) + 10, B - 8, 5, 0.35, 1)], rsw, seed=5)
    return s.render(outline=True, shadow=0.08, contact=0.08)


SCONCE_POSE = [  # 0 rest  1 a tremble  2 darts left (to the townhall door)  3 stares there  4 back  5 a glance right
                 # 6 flinch: ducks low, the brass lamp rattles on its bolts  7 recovers
    dict(), dict(fs=0.85, bright=0.88), dict(fx=-3.0), dict(fx=-4.0, fs=1.05, bright=1.06), dict(fx=-1.0, fs=0.95),
    dict(fx=3.0), dict(fy=-3.0, fs=0.7, bright=0.78, rattle=1), dict(fs=0.9, bright=0.95)]


# ======================================================================================================== CHANDELIER
# townsquare_bg.py: F 300, her feet on the island's left rim at canvas y 468 -> beye 172 (we look down on her plinth,
# her head is at eye level, so the ring of arms is seen edge-on). The square's painted lamps are caged wall lanterns of
# blue-grey painted iron with warm glass; she is cast in the same iron, crowned in antique gilt and crystal.
TS_IRON = R('#0d1314 #121a1b #172021 #1c2728 #222e2f #283536 #2f3d3e #374646 #405050 #4b5b5a #586867 #677775')
TS_GILT = R('#17110a #231a0d #312410 #403014 #503d19 #614b1f #735a26 #866a2f #9a7c3b #ae904c #c4a666 #dcc28a')
TS_GLOBE = R('#8a6430 #a47838 #ba8c42 #cc9e4e #dab05a #e6c068 #efcc78 #f6da90 #fbe8b4 #fff4da')
TS_CRYS = R('#3e4a4a #56625f #717d78 #8f9b93 #afb9ae #cfd6c8 #e9eddf #fbfbf1')
TS_FLAME = R('#f2b04a #f8c862 #fcdc8e #fff0c4 #fffaea')
CH = dict(W=128, H=216, B=205, cx=61)        # B = the plinth's axis foot; its front edge is ~8 px lower


def chandelier(P):
    W, H, B, cx = CH['W'], CH['H'], CH['B'], CH['cx']
    s = Lamp(W, H, B, cx, F=300.0, beye=172.0, lean=3.0, htot=205.0)
    IRON = mat(TS_IRON, 'cast', 0.12, 0.12)
    IRONL = mat(warmed(TS_IRON, 0.7), 'cast', 0.12, 0.12)
    RUST = mat(RUSTY[:5], 'rust', 0.12)
    DARK = mat(TS_IRON[:6], 'cast', 0.1)                                         # paint flaked off to bare iron
    GILT = mat(TS_GILT, 'gilt', 0.12, 0.7)
    GILTL = mat(warmed(TS_GILT, 0.25, (255, 220, 150)), 'gilt', 0.12, 0.7)
    g = P.get('glint', 0.0) * TAU / 8                                            # where the light stands on the lustres
    ex = P.get('eye', 0.0)                                                       # the globe's hot spot looks about
    sway = P.get('sway', 0.0)                                                    # the front pendant's swing
    sag = P.get('sag', 0.0)
    flick = P.get('flick', 0)

    # -- the plinth, the baluster, the column with its knop and collar, the capital
    def iron_tex(x, y, th, b):
        t = 0.0
        if 14 < b < 47: t -= 0.14 if (th * 16 / TAU) % 1 < 0.22 else 0                # fluting on the baluster
        if 60 < b < 140: t -= 0.10 if (th * 8 / TAU) % 1 < 0.2 else 0                 # and on the column
        if b < 12: t -= 0.10 * (12 - b) / 12                                          # the damp, dirty plinth
        return t
    prof = [(13.5, 0), (13.5, 3.5), (12.2, 3.5), (12.2, 6.5), (10.6, 6.5), (10.6, 9), (8.8, 9), (8.8, 11.5), (7.6, 12.5),
            (7.2, 14), (7.8, 18), (8.3, 24), (8.4, 30), (8.0, 36), (7.0, 42), (5.6, 47), (4.6, 51), (5.8, 52), (6.2, 53.5),
            (6.2, 55.5), (4.4, 56.5), (3.4, 57), (3.3, 60), (3.05, 100), (4.4, 101.5), (4.9, 104.5), (4.4, 107.5),
            (3.0, 109), (2.85, 140), (4.2, 141), (4.3, 144), (3.2, 145), (3.0, 146.5), (3.7, 149), (5.0, 151.5),
            (7.0, 153.5), (8.0, 155), (7.6, 156.5), (5.0, 157), (0, 157.2)]
    s.lathe(prof, IRON, lift=-0.02, tex=iron_tex)

    # -- the chandelier. Seen dead edge-on (she is at eye level) its six arms would all sit on one line, so the head is
    #    shown a little from above (a readability cheat of ~10 degrees): a gilt cup holding a round frosted globe, a
    #    small crown, six scrolled arms with tulip shades, U-festoons of crystal drops between them, a pendant under
    #    each shade and a fringe of short drops round the cup.
    s.tilt = (150.0, 0.2)
    GB, GR = 175.5, 7.6                                                          # the globe's centre and radius
    RHO, HC = 23.0, 163.5                                                        # the shades' ring
    ARMS = [TAU * k / 6 + TAU / 36 for k in range(6)]
    def armpts(ph):
        c, sn = math.cos(ph), math.sin(ph)
        pts = [(4.8, 162.0), (8.8, 158.8), (13.4, 157.8), (18.4, 159.2), (21.9, 161.6), (RHO, HC)]
        return [(r * c, h, r * sn) for r, h in pts]
    def drop_col(ph, x, y, extra=0.0):
        """a crystal drop: the warm light inside it, the sky's grey outside, and a glint where the light stands"""
        gl = max(0.0, math.cos(ph - g)) ** 12
        if gl > 0.8: return (255, 246, 222)
        v = 0.42 + 0.22 * math.sin(ph) + 0.45 * gl + extra
        return pick(TS_CRYS, v, x, y, 0.5)
    def globe_px():
        """the frosted globe as emissive pixels: a soft hot spot (the 'eye' that looks about) and a cool sky reflection"""
        cxg, cyg = s.axis(GB), B - GB
        for y in range(int(cyg - GR) - 1, int(cyg + GR) + 2):
            for x in range(int(cxg - GR) - 1, int(cxg + GR) + 2):
                u, w = (x + 0.5 - cxg) / GR, (y + 0.5 - cyg) / GR
                d = u * u + w * w
                if d > 1: continue
                hu, hw = (x + 0.5 - cxg - ex * 2.4) / (GR * 0.5), (y + 0.5 - cyg - 1.0) / (GR * 0.5)
                hot = math.exp(-(hu * hu + hw * hw) * 1.1)
                v = 0.30 + 0.16 * (1 - d) + 0.10 * w + 0.52 * hot - 0.12 * d * d
                col = pick(TS_GLOBE, v, x, y, 0.6)
                if -0.8 < u < -0.3 and -0.78 < w < -0.36: col = mix(col, (206, 216, 202), 0.5 if (x + y) % 2 == 0 else 0.25)
                s.glow(x, y, col, d=math.sqrt(max(0, 1 - d)) * GR)
    def tulip(ph):
        c, sn = math.cos(ph), math.sin(ph)
        X0, Z0 = RHO * c, RHO * sn
        s.lathe([(0, HC - 0.4), (2.6, HC - 0.2), (2.8, HC + 0.7), (1.4, HC + 1.2)], GILT, lift=0.05, ox=X0, oz=Z0)
        def tglass(x, y, th, b, n):
            tt = (b - HC - 1.2) / 5.0
            v = 0.55 + 0.30 * tt - 0.16 * n[0]
            if sn < 0: v -= 0.16
            return pick(TS_GLOBE, v, x, y, 0.6)
        s.lathe([(1.2, HC + 1.2), (1.6, HC + 2.2), (2.6, HC + 4.0), (3.4, HC + 5.6), (3.6, HC + 6.2)], GILT, ox=X0, oz=Z0, fixedf=tglass)
        fxp, fyp = s.proj(X0, HC + 6.6, Z0)                                      # the small flame at the shade's mouth
        up = 1 if (h32(int(ph * 10), flick) % 3 == 0) else 0
        s.glow(fxp, fyp - up, TS_FLAME[4], d=Z0 + 4); s.glow(fxp, fyp + 1 - up, TS_FLAME[2], d=Z0 + 4)
    def pendant(ph, swing=0.0):
        c, sn = math.cos(ph), math.sin(ph)
        X0, Z0 = RHO * c, RHO * sn
        for k, h in enumerate((HC - 1.8, HC - 3.6)):
            x, y = s.proj(X0 + swing * (k + 1) / 3, h, Z0)
            s.glow(x, y, drop_col(ph, x, y, 0.05 * k), d=Z0 + 0.5)
        x, y = s.proj(X0 + swing, HC - 6.4, Z0)                                  # the prism: a little 2x4 diamond
        for (ddx, ddy) in ((0, -1), (-1, 0), (0, 0), (-1, 1), (0, 1), (0, 2)):
            s.glow(x + ddx, y + ddy, drop_col(ph + ddx * 0.5, x + ddx, y + ddy, 0.15 - 0.08 * ddy), d=Z0 + 0.6)
    def festoon(p0, p1):
        A = (RHO * math.cos(p0), HC - 0.8, RHO * math.sin(p0)); Bq = (RHO * math.cos(p1), HC - 0.8, RHO * math.sin(p1))
        L = math.hypot(A[0] - Bq[0], A[2] - Bq[2])
        n = max(4, int(L / 2.1))
        for k in range(1, n):
            t = k / n
            X3, Z3 = A[0] + (Bq[0] - A[0]) * t, A[2] + (Bq[2] - A[2]) * t
            h = A[1] - (5.5 + sag) * math.sin(math.pi * t)
            x, y = s.proj(X3, h, Z3)
            s.glow(x, y, drop_col(math.atan2(Z3, X3), x, y), d=Z3 + 0.4)
    def fringe(front):
        for j in range(14):
            ph = TAU * j / 14
            if (math.sin(ph) >= 0) != front: continue
            X3, Z3 = 6.2 * math.cos(ph), 6.2 * math.sin(ph)
            for k in range(3):
                x, y = s.proj(X3, 162.4 - 2.0 * k, Z3)
                s.glow(x, y, drop_col(ph, x, y, -0.06 * k), d=Z3 + 0.2)
    def pairs(front):
        for k in range(6):
            p0, p1 = ARMS[k], ARMS[(k + 1) % 6] + (TAU if k == 5 else 0)
            if (math.sin((p0 + p1) / 2) >= 0) == front: yield p0, p1
    back = [p for p in ARMS if math.sin(p) < 0]; front = [p for p in ARMS if math.sin(p) >= 0]
    # the back half (behind the globe and the cup)
    for p0, p1 in pairs(False): festoon(p0, p1)
    for ph in back:
        s.tube3(armpts(ph), 0.8, GILT, lift=-0.08); pendant(ph); tulip(ph)
    fringe(False)
    # the cup on the capital, the globe in it, its gallery and the crown
    s.lathe([(0, 157.2), (2.6, 157.4), (3.6, 158.8), (4.6, 161.5), (5.8, 164.2), (6.8, 166.6), (6.6, 167.6), (5.0, 168.0)],
            GILT, lift=0.0, tex=lambda x, y, th, b: (0.14 if abs(b - 165.8) < 0.6 else 0) - (0.12 if (th * 16 / TAU) % 1 < 0.3 and b < 164 else 0))
    globe_px()
    s.lathe([(6.4, 167.0), (7.4, 167.4), (7.4, 168.6), (6.4, 169.0)], GILT, lift=0.1)                # the cup's rolled lip
    s.lathe([(3.4, 182.2), (4.2, 182.6), (4.2, 183.8), (3.0, 184.2), (1.9, 185.4), (2.1, 187.0), (1.4, 188.0), (0.6, 188.4),
             (0.5, 191.6), (0, 192.6)], GILT, lift=0.08)                                       # the crown and the finial
    for k in range(8):
        ph = TAU * k / 8
        if math.sin(ph) < -0.2: continue
        s.tube3([(4.0 * math.cos(ph), 183.6, 4.0 * math.sin(ph)), (4.6 * math.cos(ph), 186.0, 4.6 * math.sin(ph))], 0.5, GILT, lift=0.12)
    # the front half
    fringe(True)
    for p0, p1 in pairs(True): festoon(p0, p1)
    for ph in front:
        s.tube3(armpts(ph), 0.8, GILT, lift=0.02)
        c, sn = math.cos(ph), math.sin(ph)
        s.tube3([(r * c, h, r * sn) for r, h in ((12.0, 158.6), (11.6, 156.6), (12.8, 155.4), (14.0, 156.2), (13.6, 157.2))], 0.5, GILT, lift=0.04)
        pendant(ph, sway if abs(c) < 0.6 else 0.0)
        tulip(ph)

    # light: the globe and the shades light the capital, the boss and the top of the column, warm
    swap = {IRON: IRONL, GILT: GILTL}
    s.relight(s.axis(GB), B - GB + 6, 30, 0.30, swap, mask=lambda x, y: 1.0 if y > B - 170 else 0.4)
    # weather: the paint flaking off the plinth and baluster to dark iron, rust running from the joints
    flake = {IRON: DARK}
    s.speckle(flake, 0.10, seed=11, region=lambda x, y: y > B - 50)
    s.rust([(s.axis(9) - 9, B - 9, 9, 0.5, 1), (s.axis(9) + 7, B - 9, 8, 0.45, 1), (s.axis(56) - 4, B - 56, 16, 0.45, 1),
            (s.axis(56) + 5, B - 56, 12, 0.35, 1), (s.axis(141) + 3, B - 141, 18, 0.32, 1), (s.axis(101) - 3, B - 101, 10, 0.3, 1),
            (s.axis(3.5) - 12, B - 3, 4, 0.5, 2), (s.axis(3.5) + 11, B - 3, 4, 0.5, 2)], {IRON: RUST, DARK: RUST}, seed=12)
    return s.render(outline=True, shadow=0.10, contact=0.10)


CHANDELIER_POSE = [  # the glint runs round the lustres (a full turn over the 8 frames); the globe's hot spot looks
                     # about; the front pendant swings; the festoons breathe; the tulip flames flicker
    dict(glint=0, eye=0.0, sway=0, sag=0.0, flick=1), dict(glint=1, eye=0.5, sway=0.5, sag=0.3, flick=2),
    dict(glint=2, eye=1.0, sway=1, sag=0.5, flick=3), dict(glint=3, eye=1.0, sway=0.5, sag=0.3, flick=4),
    dict(glint=4, eye=0.5, sway=0, sag=0.0, flick=5), dict(glint=5, eye=0.0, sway=-0.5, sag=-0.3, flick=6),
    dict(glint=6, eye=-0.5, sway=-1, sag=-0.5, flick=7), dict(glint=7, eye=-0.3, sway=-0.5, sag=-0.3, flick=8)]


# ======================================================================================================== TORCHERE
# harbor_bg.py: F 300, her base on the pier planks at canvas y 511 -> beye 215 (the near pier: we look well down onto
# the flange and into the drip pan). The dock's lamp at the jetty end has a banded post, an iron arm and a twisted iron
# finial splayed like a hand; Torchere is its iron cousin, a storm torch: the flame burns bare in an open cage.
HB_IRON = R('#11100e #191815 #22201c #2c2924 #36332c #423e35 #4f4a3f #5d574a #6c6555 #7c7462')
HB_ROPE = R('#1b160f #272016 #352c1e #453a28 #564933 #685a3f #7a6b4c')
HB_TAG = R('#4e4a3c #67624f #827b64 #9a9279 #b0a88c')
HB_FLAME = R('#6e2a10 #a8441a #d26424 #ea8a32 #f6b04a #fcd070 #fee8a8 #fff8e6')
SPARK = [(255, 236, 168), (250, 186, 84), (214, 120, 44)]
TO = dict(W=128, H=200, B=187, cx=64)        # B = the flange's axis foot; its front edge is ~9 px lower


def torchere(P):
    W, H, B, cx = TO['W'], TO['H'], TO['B'], TO['cx']
    s = Lamp(W, H, B, cx, F=300.0, beye=215.0, lean=-2.5, htot=176.0)
    IRON = mat(HB_IRON, 'cast', 0.13, 0.10)
    IRONL = mat(warmed(HB_IRON, 0.55, (240, 150, 70)), 'cast', 0.13, 0.10)
    SOOT = mat(HB_IRON[:5], 'cast', 0.10, 0.05)
    RUST = mat(RUSTY, 'rust', 0.13)
    ROPE = mat(HB_ROPE, 'rope', 0.16)
    TAG = mat(HB_TAG, 'plain', 0.2)
    X = s.axis
    wind, fs, split = P.get('wind', 5.0), P.get('fs', 1.0), P.get('split', 0)
    def iron_tex(x, y, th, b):
        t = (rig.nM(x * 0.9, y * 0.35) - 0.5) * 0.10                                     # dents, uneven paint
        if b < 3: t -= 0.06
        return t
    # -- the flange bolted to the planks, the bell foot, the post
    s.lathe([(12.6, 0), (12.6, 1.5), (9.2, 1.9), (8.7, 2.3), (8.2, 4.0), (7.1, 8.0), (5.8, 13.0), (4.8, 18.0), (4.5, 20.5),
             (5.4, 21.0), (5.7, 23.0), (4.3, 23.6), (3.7, 24.2), (3.55, 80), (3.4, 128), (4.9, 129), (5.1, 132), (3.8, 133),
             (2.7, 134), (2.6, 137.5), (6.5, 139.0), (12.6, 140.8), (13.2, 141.2), (13.2, 142.2), (12.0, 142.4), (10.0, 141.8),
             (5.2, 141.4), (5.0, 141.6), (5.1, 143.0), (5.2, 147.0), (4.4, 147.4), (1.4, 147.6), (1.2, 148.6), (0, 148.8)],
            IRON, lift=-0.02, tex=iron_tex)
    for k in range(4):                                                           # the flange's four bolts
        th = TAU * k / 4 + TAU / 8
        s.lathe([(1.4, 1.5), (1.4, 2.9), (0.9, 3.2), (0, 3.3)], IRON, lift=0.08, ox=10.6 * math.cos(th), oz=10.6 * math.sin(th))
    BANDS = (44, 70, 96, 116)
    for b0 in BANDS:                                                             # riveted bands like the jetty post's
        s.lathe([(3.4, b0), (4.6, b0 + 0.3), (4.7, b0 + 2.6), (3.4, b0 + 2.9)], IRON, lift=0.04,
                tex=lambda x, y, th, b: 0.16 if any(abs(th - a) < 0.22 for a in (math.pi / 2, math.pi / 2 - 0.9, math.pi / 2 + 0.9)) and abs(b - b0 - 1.4) < 0.9 else 0)
    # -- a hook on the post with a coil of tarred rope on it, a pale tally tag tied to the tail (cargo that went astray)
    s.tube3([(3.0, 101.0, 0.8), (6.0, 101.4, 1.0), (7.6, 102.8, 1.0), (7.8, 104.6, 1.0)], 0.7, IRON, lift=0.05)
    cxr, cbr = 9.0, 93.0
    ring = [(cxr + 4.6 * math.sin(a) - 0.6 * math.sin(2 * a), cbr + 8.0 * math.cos(a) + 0.5, 1.6 + 0.8 * math.cos(a)) for a in
            [TAU * k / 28 for k in range(29)]]
    s.tube3(ring, 1.25, ROPE, lift=0.02, vfun=lambda x, y, f: 0.10 if int(f * 40) % 3 == 0 else -0.04)
    s.tube3([(cxr + 4.4, cbr - 4.0, 2.4), (cxr + 4.8, cbr - 9.0, 2.6), (cxr + 4.2, cbr - 14.0, 2.6), (cxr + 4.6, cbr - 17.5, 2.8)], 0.9, ROPE, lift=0.0)
    tx, tb = cxr + 4.6, cbr - 18.5
    s.fill([s.proj(tx - 1.6, tb, 3), s.proj(tx + 1.8, tb, 3), s.proj(tx + 1.8, tb - 4.5, 3), s.proj(tx - 1.6, tb - 4.5, 3)], TAG,
           (-0.3, -0.2, 1), 0.15, d=4, vfun=lambda x, y: -0.35 if (h32(x, y, 7) % 5 == 0) else 0)

    # -- the flame on the wick, snapping sideways in the wind
    fx0, fy0 = s.proj(0, 148.6, 0)
    fh = 21.0 * fs
    def flame():
        for y in range(int(fy0 - fh * 1.25) - 1, int(fy0) + 2):
            t = (fy0 - (y + 0.5)) / fh
            if t < -0.08 or t > 1.0: continue
            xc = fx0 + wind * max(0, t) ** 1.6 + 0.8 * math.sin(t * 7 + split * 2)
            hw = 4.6 * fs * max(0.0, min(1.0, (t + 0.1) * 3.2)) ** 0.6 * (1 - max(0, t)) ** 0.85
            for x in range(int(xc - hw) - 1, int(xc + hw) + 2):
                u = (x + 0.5 - xc) / max(hw, 0.4)
                if abs(u) > 1: continue
                if split and t > 0.55 and abs(u) < 0.28: continue                     # the tip splits into two tongues
                v = 1.0 - 0.55 * abs(u) ** 1.5 - 0.55 * max(0, t) ** 1.2 + 0.1 * (t < 0.12)
                s.glow(x, y, pick(HB_FLAME, v, x, y, 0.55), d=0.5)
    flame()
    for (sx_, sb, c) in P.get('sparks', ()):
        x, y = s.proj(sx_, sb, 0)
        s.glow(x, y, SPARK[c], d=8)

    # -- the storm cage: six iron bars from the pan's lip, bellied, closing to a ring; the finial splayed like a hand
    for k in range(6):
        ph = TAU * k / 6 + TAU / 24
        c, sn = math.cos(ph), math.sin(ph)
        pts = [(r * c, h, r * sn) for r, h in ((12.6, 141.8), (13.6, 147.0), (13.4, 154.0), (11.4, 160.5), (8.2, 166.0), (5.4, 169.6))]
        s.tube3(pts, 0.65, IRON, lift=-0.04 if sn < 0 else 0.02)
    s.lathe([(4.8, 169.0), (5.9, 169.4), (6.0, 171.2), (4.6, 171.6), (2.2, 172.0), (2.0, 173.4), (0, 173.8)], IRON, lift=0.04)
    for k, a in enumerate((-56, -30, -6, 18, 44)):                                 # five twisted prongs
        ar = math.radians(a)
        pts = []
        for j in range(7):
            t = j / 6
            L = 11.0 - abs(a) / 16.0
            rr = L * t
            pts.append((math.sin(ar) * rr + 0.5 * math.sin(t * 6 + k), 173.0 + math.cos(ar) * rr, 0.6 * math.cos(t * 5 + k)))
        s.tube3(pts, lambda f: 0.75 - 0.3 * f, IRON, lift=0.05, vfun=lambda x, y, f: 0.10 if int(f * 9) % 2 else -0.05)

    # light from the flame on the pan, the cage, the ring, the finial and the post below
    swap = {IRON: IRONL}
    s.relight(fx0 + wind * 0.4, fy0 - fh * 0.4, 30 * (0.8 + 0.2 * fs), 0.26 * min(1.2, fs), swap)
    # soot over the flame: the ring, the bars' tops and the prongs
    for (x, y), e in s.buf.items():
        if e[0] in (IRON, IRONL) and y < fy0 - 12 and abs(x - fx0 - 2) < 10:
            e[0] = SOOT if e[0] is IRON else e[0]; e[1] -= 0.10 * max(0.0, min(1.0, (fy0 - 12 - y) / 6))
    # rust running down from every rivet band, the shoulder collar, the bolts; speckles on the foot
    rsrc = []
    for b0 in BANDS:
        for dxr in (-2.5, 0.5, 2.5):
            rsrc.append((X(b0) + dxr, B - b0 + 1, 10 + (h32(b0, int(dxr * 2)) % 9), 0.7, 1))
    rsrc += [(X(129) - 3, B - 128, 16, 0.6, 1), (X(129) + 2, B - 128, 22, 0.7, 1), (X(22) - 4, B - 21, 9, 0.7, 1),
             (X(22) + 3, B - 21, 12, 0.6, 1), (X(141) + 11, B - 142, 4, 0.8, 1), (X(141) - 11, B - 142, 4, 0.8, 1)]
    for k in range(4):
        th = TAU * k / 4 + TAU / 8
        bx, by = s.proj(10.6 * math.cos(th), 1.5, 10.6 * math.sin(th))
        rsrc.append((bx, by + 1, 4, 0.9, 2))
    s.rust(rsrc, {IRON: RUST, IRONL: RUST}, seed=21)
    s.speckle({IRON: RUST}, 0.13, seed=22, region=lambda x, y: y > B - 26)
    return s.render(outline=True, shadow=0.11, contact=0.10)


TORCHERE_POSE = [  # 0 the wind lays the flame over  1 the tip splits  2 a gust, two sparks spat  3 it rounds on you:
                   # straightens and flares  4 holds, burning tall  5 the wind takes it again  6 splits, a spark  7 lays over
    dict(wind=5.0, fs=1.0), dict(wind=6.0, fs=0.95, split=1), dict(wind=8.0, fs=0.9, sparks=((9, 168, 0), (11, 173, 1))),
    dict(wind=1.5, fs=1.18, sparks=((12, 176, 1), (15, 181, 2), (5, 178, 0))), dict(wind=0.5, fs=1.16, split=1),
    dict(wind=4.5, fs=1.02), dict(wind=6.5, fs=0.96, split=1, sparks=((8, 170, 0),)), dict(wind=6.0, fs=1.0, sparks=((10, 178, 2),))]


# ======================================================================================================== DON GIRANDOLE
# Scraper1140.png is the original picture re-pixelled at 3x (356x200 logical, scraper_bg.py), so the Don is drawn on
# that grid (45x56 logical, shown at scale 3) and quantised to its palette (scraper.gpl). He sits on the pipe tower's
# platform above the roof's horizon, so he is seen a little from below.
SCRAPER_PAL = [(7, 8, 9), (16, 15, 17), (21, 19, 22), (23, 25, 27), (25, 28, 30), (27, 32, 34), (29, 36, 38), (31, 39, 41),
               (45, 38, 29), (33, 43, 44), (36, 47, 47), (39, 50, 45), (40, 52, 50), (44, 57, 52), (56, 54, 43), (48, 63, 55),
               (53, 69, 59), (72, 64, 49), (55, 74, 65), (59, 76, 64), (61, 80, 68), (80, 78, 57), (64, 84, 71), (69, 88, 74),
               (73, 93, 78), (75, 97, 81), (79, 100, 83), (90, 97, 74), (84, 104, 85), (92, 109, 89), (109, 110, 72),
               (100, 119, 96), (104, 118, 92), (107, 123, 97), (112, 125, 97), (114, 127, 99), (117, 130, 103), (123, 136, 111),
               (131, 137, 108), (138, 143, 113), (151, 155, 121), (165, 163, 123), (175, 165, 118), (171, 169, 126),
               (183, 181, 139), (71, 56, 36), (99, 73, 42), (121, 89, 47), (143, 81, 34), (155, 97, 50), (146, 120, 58),
               (162, 117, 33), (188, 141, 53), (232, 160, 72), (255, 214, 140)]
DN_SUIT = [(7, 8, 9), (16, 15, 17), (21, 19, 22), (45, 38, 29), (56, 54, 43), (71, 56, 36), (99, 73, 42)]
DN_SUITL = [(21, 19, 22), (45, 38, 29), (71, 56, 36), (99, 73, 42), (121, 89, 47), (155, 97, 50)]
DN_CREAM = [(72, 64, 49), (109, 110, 72), (138, 143, 113), (165, 163, 123), (183, 181, 139)]
DN_BRZ = [(7, 8, 9), (21, 19, 22), (45, 38, 29), (71, 56, 36), (99, 73, 42), (121, 89, 47), (146, 120, 58), (188, 141, 53)]
DN_TIE = [(21, 19, 22), (71, 56, 36), (121, 89, 47), (146, 120, 58), (162, 117, 33)]
DN_GLOW = [(143, 81, 34), (162, 117, 33), (188, 141, 53), (232, 160, 72), (255, 214, 140)]
DN_SMOKE = [(123, 136, 111), (138, 143, 113), (151, 155, 121), (165, 163, 123)]
DN_OUT = (16, 15, 17)
DN = dict(W=45, H=56, B=55, cx=22)


def quantise(im, pal):
    p = im.load(); cache = {}
    for y in range(im.height):
        for x in range(im.width):
            c = p[x, y]
            if c[3] == 0: continue
            k = c[:3]
            if k not in cache: cache[k] = min(pal, key=lambda q: (q[0] - k[0]) ** 2 * 0.3 + (q[1] - k[1]) ** 2 * 0.59 + (q[2] - k[2]) ** 2 * 0.11)
            p[x, y] = cache[k] + (255,)
    return im


def don(P):
    W, H, B, cx = DN['W'], DN['H'], DN['B'], DN['cx']
    s = Lamp(W, H, B, cx, F=400.0, beye=-30.0)
    rig.TEX['suit'] = lambda x, y: (rig.nM(x * 0.8, y * 0.8) - 0.5) * 0.06
    SUIT = Mat(DN_SUIT, 'suit', 0.18, 0.0, outline=DN_OUT)
    SUITL = Mat(DN_SUITL, 'suit', 0.18, 0.0, outline=DN_OUT)
    CREAM = Mat(DN_CREAM, 'plain', 0.22, 0.0, outline=DN_OUT)
    BRZ = Mat(DN_BRZ, 'metal', 0.14, 0.45, outline=DN_OUT)
    BRZL = Mat(DN_BRZ[1:] + [(232, 160, 72)], 'metal', 0.16, 0.45, outline=DN_OUT)
    FOOT = Mat(DN_BRZ[:5], 'metal', 0.12, 0.3, outline=DN_OUT)
    TIE = Mat(DN_TIE, 'plain', 0.2, 0.2, outline=DN_OUT)
    ex, ember, lift_h, sm = P.get('eye', 0.0), P.get('ember', 0.5), P.get('hand', 0), P.get('smoke', 0)
    hb = P.get('breath', 0)                                                      # the shoulders rise a px on the breath
    Y = lambda y: y - hb if y < 36 else y

    def settle():                                                                # rig-drawn shapes sit at depth 0
        for k in s.buf:
            s.zb.setdefault(k, 0.0)
    # He is turned three-quarters to the viewer's left (toward the roof where the player stands): his right side is the
    # far one. Far arm: the elbow tucked at his side, the forearm forward with the cigar. Near arm: the hand deep in his
    # pocket, the elbow out a little and back, that shoulder lower.
    hy = 32.6 - lift_h
    s.tube((12.6, Y(28.0)), (11.4, 36.2), 2.4, 2.2, SUIT, lift=-0.10, group='farup')                       # far upper arm
    # the jacket: broad shoulders, the near side wider and bellied, the waist going into the post's cup
    jacket = [(18.6, Y(24.8)), (14.0, Y(25.4)), (11.4, Y(27.0)), (10.8, Y(30.0)), (11.4, 34.0), (12.6, 38.6), (14.6, 43.0),
              (15.0, 45.6), (14.4, 47.8), (29.8, 47.8), (29.4, 45.6), (31.6, 42.4), (33.2, 39.0), (33.6, 36.0), (33.4, Y(33.0)),
              (34.0, Y(29.6)), (32.6, Y(27.2)), (28.0, Y(25.8)), (23.6, Y(25.0))]
    def cloth(x, y):
        v = 0.12 * math.exp(-((x - 28.5) ** 2 / 8 + (y - 38.5) ** 2 / 10))        # the belly catches the light
        v -= 0.10 * max(0, (x - 30.5) / 3)                                         # the near side turned away
        return v
    s.poly(jacket, SUIT, lift=-0.04, round_=0.85, vfun=cloth, group='body')
    # the lapels (rolled, catching the light on their edges), the shirt, the tie, the pocket square
    s.poly([(15.6, Y(25.4)), (17.8, Y(25.6)), (19.6, 36.4), (18.8, 36.6), (14.6, Y(29.8)), (14.8, Y(26.8))], SUIT, lift=0.24, round_=0.2, group='lapel')
    s.poly([(23.2, Y(25.6)), (26.4, Y(25.4)), (27.8, Y(27.6)), (25.0, Y(31.0)), (20.4, 36.6), (19.8, 36.4)], SUIT, lift=0.16, round_=0.2, group='lapel')
    s.poly([(17.8, Y(25.6)), (23.2, Y(25.6)), (20.6, 34.2), (19.4, 34.2)], CREAM, lift=0.08, round_=0.4, group='shirt')
    s.poly([(19.4, Y(25.9)), (21.4, Y(25.9)), (21.2, Y(27.5)), (19.6, Y(27.5))], TIE, lift=0.16, round_=0.4, group='tie')
    s.poly([(19.6, Y(27.5)), (21.2, Y(27.5)), (21.6, 33.4), (20.4, 35.0), (19.2, 33.4)], TIE, lift=0.02, round_=0.5,
           vfun=lambda x, y: 0.14 if (x + y) % 3 == 0 else 0, group='tie')
    s.poly([(26.4, Y(30.4)), (27.2, Y(29.4)), (27.8, Y(30.2)), (28.6, Y(29.6)), (29.2, Y(30.8)), (26.6, Y(31.0))], CREAM, lift=0.12, group='body')
    # folds: strain from the button across the belly, creases under the near arm, the opening below the button
    for pts, c in (([(21.0, 38.6), (24.0, 37.6), (27.0, 37.4)], (16, 15, 17)), ([(21.0, 40.4), (24.6, 41.0)], (16, 15, 17)),
                   ([(31.6, Y(31.2)), (29.8, 33.6)], (16, 15, 17)), ([(20.2, 41.2), (19.8, 44.0), (19.2, 47.4)], (7, 8, 9)),
                   ([(13.4, 38.0), (14.6, 42.6)], (16, 15, 17))):
        s.stroke(pts, 0.7, color=c, group='body')
    for by in (37.4, 41.0):
        s.fixed(20.4, by, (121, 89, 47)); s.fixed(20.4, by + 1, (21, 19, 22))
    s.stroke([(27.6, 42.2), (30.8, 42.0)], 0.8, color=(21, 19, 22), group='body')                           # the hip pocket
    # the near arm: shoulder, the elbow out and back, the forearm going in to the pocket
    s.tube((32.4, Y(28.6)), (34.4, 36.4), 2.5, 2.3, SUIT, lift=0.0, group='near')
    s.tube((34.4, 36.4), (30.4, 42.2), 2.3, 1.9, SUIT, lift=-0.04, group='near')
    s.stroke([(33.6, 35.4), (34.8, 36.8)], 0.7, color=(16, 15, 17), group='near')                         # the elbow crease
    # the far forearm and the cigar hand (a white glove), in front of the body's far edge
    s.tube((11.6, 36.2), (8.6, hy + 1.2), 2.1, 1.8, SUIT, lift=0.08, group='farlo')
    s.stroke([(9.6, hy + 1.8), (10.4, hy + 2.4)], 1.0, color=(109, 110, 72), group='farlo')                 # the shirt cuff
    s.ellipsoid(7.8, hy + 0.2, 2.0, 1.8, CREAM, lift=0.08, group='hand')
    s.fixed(6.4, hy - 0.8, (183, 181, 139)); s.fixed(7.4, hy - 1.2, (165, 163, 123))                      # knuckles
    settle()
    # -- the lamp-post foot he stands in: its cup's rim in front of his jacket's hem
    s.lathe([(7.2, 0), (7.2, 1.2), (6.4, 1.8), (5.2, 3.0), (4.2, 4.6), (3.7, 6.2), (4.6, 7.0), (5.7, 7.6), (6.6, 8.6),
             (7.0, 9.6), (6.6, 10.2), (5.8, 9.8)], FOOT, lift=-0.02)
    # -- the brass collar where a neck would be, and the head: a lantern, turned with him
    s.axis = lambda b: 20.4
    s.lathe([(0, 28.0 + hb), (2.8, 28.1 + hb), (3.4, 29.0 + hb), (3.2, 30.4 + hb), (2.3, 30.8 + hb), (2.1, 32.2 + hb)], BRZ, lift=0.04)
    s.lathe([(2.1, 32.2 + hb), (3.4, 33.0 + hb), (4.4, 33.9 + hb), (4.7, 34.5 + hb), (4.2, 34.9 + hb)], BRZ, lift=0.05)
    gy0, gy1 = B - 34.9 - hb, B - 44.0 - hb                                                     # glass bottom / top rows
    corner = 18.8                                                                               # the near vertical corner bar
    fx, fy = 19.4 + ex, B - 38.8 - hb
    oid = s.new()
    for y in range(int(gy1), int(gy0) + 1):
        t = (gy0 - (y + 0.5)) / (gy0 - gy1)                                                    # 0 bottom .. 1 top
        hw = 4.2 + 1.5 * t
        xl, xr = 20.4 - hw - 0.4, 20.4 + hw - 0.4
        for x in range(int(xl), int(xr) + 1):
            xc = x + 0.5
            if xc < xl or xc > xr: continue
            if abs(xc - corner) < 0.7 or xc - xl < 0.9 or xr - xc < 0.9 or t < 0.1 or t > 0.92:
                s.put(x, y, BRZ, 0.32 + (0.22 if xc < corner else 0.0) + 0.2 * (t > 0.92), oid); continue
            d = math.hypot((xc - fx) / 2.0, (y + 0.5 - fy) / 2.8)
            v = 0.32 + 0.16 * (1 - t) + 0.55 * math.exp(-d * d) - (0.20 if xc > corner else 0)        # the right pane turned away
            if d < 0.7: v = 1.0
            s.fixed(x, y, pick(DN_GLOW, v, x, y, 0.3))
    ey = B - 44.0 - hb                                                                          # the eaves and the roof
    s.poly([(12.8, ey + 1.4), (28.0, ey + 1.4), (27.2, ey - 0.2), (13.6, ey - 0.2)], BRZ, lift=0.10, round_=0.2)
    s.poly([(14.0, ey - 0.2), (18.8, ey - 5.2), (18.8, ey - 0.2)], BRZ, lift=0.20, round_=0.1)
    s.poly([(18.8, ey - 5.2), (26.6, ey - 0.2), (18.8, ey - 0.2)], BRZ, lift=-0.08, round_=0.1)
    s.ellipsoid(19.0, ey - 6.2, 1.3, 1.2, BRZ, lift=0.15)
    s.stroke([(19.0, ey - 7.4), (19.0, ey - 8.8)], 0.9, BRZ, v=0.55)
    # the lamp lights his own shoulders, lapels, collar and the cigar hand
    swap = {SUIT: SUITL, BRZ: BRZL, FOOT: FOOT}
    s.relight(fx, fy + 3, 12.5, 0.32, swap, mask=lambda x, y: 1.0 if y < 33 else 0.0)
    old = rig.BAYER
    rig.BAYER = [[7.5 + (v - 7.5) * 0.3 for v in row] for row in BAYER]                       # the picture has no regular dither
    try:
        im = s.render(outline=True, shadow=0.12, contact=0.10)
    finally:
        rig.BAYER = old
    p = im.load()
    # the cigar (held loosely, the tip up), its band, the ember; then the smoke -- all without an outline
    cig = [(6.0, hy - 1.4), (5.0, hy - 1.9), (4.0, hy - 2.4), (3.0, hy - 2.9)]
    for k, (qx, qy) in enumerate(cig):
        p[int(qx), int(qy)] = ((188, 141, 53) if k == 0 else (71, 56, 36)) + (255,)
    p[2, int(hy - 3.4)] = DN_GLOW[2 + int(round(ember * 2))] + (255,)
    for k in range(13):
        t = ((k + sm * 1.6) / 13.0) % 1.0
        qx = 1.8 + 1.5 * math.sin(t * 6.5 + 0.8) + t * 2.0
        qy = hy - 4.6 - t * 15.0
        if h32(k, sm, 5) % 4 == 0 or not (0 <= qx < W and 0 <= qy < H): continue
        if p[int(qx), int(qy)][3]: continue
        p[int(qx), int(qy)] = DN_SMOKE[min(3, int((1 - t) * 3.2))] + (255,)
    return quantise(im, SCRAPER_PAL)


DON_POSE = [  # 0 rest  1 the ember breathes, the smoke rises  2 the flame turns to the viewer's left (toward the player)
              # 3 holds there  4 the cigar hand lifts a px, the ember glows  5 the breath, the flame comes back
              # 6 it glances right  7 settle
    dict(smoke=0, ember=0.3), dict(smoke=1, ember=0.8), dict(smoke=2, eye=-1.2, ember=0.5), dict(smoke=3, eye=-1.6, ember=0.3),
    dict(smoke=4, eye=-0.8, hand=1, ember=1.0), dict(smoke=5, breath=1, ember=0.6), dict(smoke=6, eye=1.0, ember=0.3),
    dict(smoke=7, ember=0.4)]


LAMPS = {
    'sconce': (sconce, SCONCE_POSE, SC),
    'chandelier': (chandelier, CHANDELIER_POSE, CH),
    'torchere': (torchere, TORCHERE_POSE, TO),
    'don': (don, DON_POSE, DN),
}


def build(lid):
    fn, poses, geo = LAMPS[lid]
    frames = [fn(p) for p in poses]
    os.makedirs(f'{OUT}/{lid}', exist_ok=True)
    W, H = frames[0].size
    sheet = Image.new('RGBA', (W * len(frames), H), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        im.save(f'{OUT}/{lid}/{i}.png'); sheet.paste(im, (i * W, 0))
    sheet.save(f'{OUT}/{lid}.png')
    return frames


if __name__ == '__main__':
    used = set()
    for lid in LAMPS:
        if ONLY and lid not in ONLY: continue
        fr = build(lid)
        for im in fr: used |= {px[:3] for px in im.getdata() if px[3]}
        print('ok', lid)
    rows = ['%3d %3d %3d\t#%02x%02x%02x' % (c + c) for c in sorted(used, key=lambda c: (sum(c), c))]
    open(f'{OUT}/lamps.gpl', 'w').write('GIMP Palette\nName: lamps\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
