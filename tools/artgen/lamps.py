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
  don        136x168, ScraperScene, on the pipe tower's platform (native 1 px like Scraper1140.png, scraper_native_bg.py;
             seen a little from below). The godfather: a portly lamp-post gentleman in a dark brown three-piece suit
             with a chalk pinstripe -- the jacket open over a strained waistcoat (buttons, a gold watch chain), peaked
             lapels, a pocket square, a starched collar and an ochre silk tie; white kid gloves. He stands in a
             gadrooned bronze lamp-post cup and is turned three-quarters to the viewer's left (toward the player): the
             near hand deep in the jacket's hip pocket (that shoulder lower, the elbow out and back), the far one raised
             with a banded cigar between the first two fingers. His head is a brass lantern (glass panes in a frame,
             eaves, a seamed roof, a finial) with a flame on a burner inside -- the "eye" -- and its light falls on his
             own shoulders, lapels and the cigar hand. The flame turns to look, the ember breathes, smoke curls up.

Every sheet is a horizontal strip of 8 idle frames (frame meanings in the *_POSE lists); the game shows them at scale
1, origin bottom-centre; the base's lowest row is H-3 (Don: H-1). Bust portraits are frames of the same sheets
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
# Native 1 px, 136x168, shown at scale 1 on Scraper1140.png (scraper_native_bg.py): the sprite's centre at canvas x 1024,
# its bottom at y 381 on the pipe tower's platform, which stands well above the roof's horizon (y 450) -- so he is seen
# a little from below (the cup's rim, the lantern's base plate and its eaves show their undersides). b = px above the
# cup's foot (row 167). His body is a parametric surface (elliptic sections, a belly, one shoulder lower) turned DN_YAW
# toward the viewer's left; the cloth (jacket, lapels, waistcoat, shirt, tie) is mapped onto it by its own coordinates,
# so the open jacket, the strained waistcoat, the pinstripe and the folds all wrap round him.
DN_SUIT = R('#0f0b09 #150f0c #1b1310 #221814 #2a1e18 #32241c #3b2b21 #453226 #4f3a2c #5a4232 #664b39')
DN_SHIRT = R('#37332a #4b463a #615a4b #78705d #8f8771 #a69e86 #bbb49b #cec8ae #ded9c2')
DN_TIE = R('#1f150b #2d1e0e #3d2912 #4f3517 #61421c #745121 #866028 #977032')
DN_GLOVE = R('#3c3933 #534f46 #6b665a #847e6f #9c9786 #b4af9b #cac6b0 #dcd8c4 #eae7d7')
DN_BRASS = R('#17110a #21180d #2c2011 #382915 #44321a #513c1f #5f4725 #6e522b #7d5e33 #8e6c3d #a07c4a #b48f5c')
DN_GLASS = R('#4e3216 #66401a #7f501f #985f25 #ad6f2c #c18035 #d29240 #e0a54e #ecbb68 #f5d08a #fbe4b4')
DN_BRONZE = R('#100c09 #17110d #1f1711 #281e15 #32261a #3d2e1f #483725 #54412c #614b33 #6e563b')
DN_VERD = R('#1d2822 #27352d #314238 #3c5043')
DN_CIGAR = R('#1d130c #29190f #372214 #462b19 #56351f #674026')
DN_EMBER = R('#4a1a0c #7a2a10 #b04418 #d86a28 #f39a44 #ffc878 #fff0c8')
DN_ASH = R('#55534d #75726a #96928a')
DN_CHAIN = R('#4a3a1c #7a6230 #b09550 #dcc282')
DN_SKY = (166, 180, 160)                                                      # the overcast sky caught on the glass
DN_SMOKE = (196, 199, 188)
DN_OUT = (17, 12, 10)
DN = dict(W=136, H=168, B=167, cx=66)
DN_YAW, DN_HYAW = math.radians(28), math.radians(25)                         # the body's and the lantern's turn
DN_HX, DN_HZ = -2.0, 3.5                                                     # the head's axis from the body's (screen x, z)

rig.TEX['suit'] = lambda x, y: ((rig.nF(x * 1.7, y * 1.7) - 0.5) * 0.12 + (rig.nM(x * 0.7, y * 0.7) - 0.5) * 0.08
                                 + (0.03 if (x + 2 * y) % 3 == 0 else 0))          # worsted: grain, mottle, twill
rig.TEX['kid'] = lambda x, y: (rig.nF(x * 1.2, y * 1.2) - 0.5) * 0.05


def spl(tab, b):
    """Catmull-Rom through (b, value) control points, clamped at the ends"""
    if b <= tab[0][0]: return tab[0][1]
    if b >= tab[-1][0]: return tab[-1][1]
    i = 0
    while tab[i + 1][0] < b: i += 1
    t = (b - tab[i][0]) / (tab[i + 1][0] - tab[i][0])
    p0, p1, p2, p3 = tab[max(0, i - 1)][1], tab[i][1], tab[i + 1][1], tab[min(len(tab) - 1, i + 2)][1]
    return 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)


def segd(px, py, ax, ay, bx, by):
    """distance from p to the segment ab"""
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1e-9
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - dx * t, py - ay - dy * t)


# the body: half-widths of the far (his right) and near (his left) side, the half-depth, the belly, the neck's lean
TOR_AF = [(31, 25), (38, 27.5), (46, 29.5), (54, 29.5), (62, 28), (70, 26.8), (77, 26.6), (82, 25.6), (84.5, 23.4),
          (86.6, 17.5), (88.2, 11.5), (89.2, 9.6), (92, 9.2)]
TOR_AN = [(31, 25), (38, 27.5), (46, 29.5), (54, 30), (62, 28.5), (70, 27.5), (75, 27.2), (78.5, 26.0), (81, 23.4),
          (83.2, 17.0), (85.0, 11.5), (86.2, 9.6), (92, 9.2)]
TOR_BD = [(31, 20), (38, 22.5), (46, 23.5), (54, 23), (62, 21), (70, 19), (77, 17.5), (82, 16), (86, 12), (89, 9.4), (92, 9)]
TOR_ZC = [(31, 3), (38, 5), (46, 6.5), (54, 6), (62, 4), (70, 2), (78, 0.5), (92, 0)]
TOR_ZN = [(76, 0), (89, 4.0), (92, 4.0)]
# the cloth, in his own X (px from the front line) and b
J_EDGE = [(31, 14), (40, 13), (50, 11), (57, 9.0), (66, 8.3), (76, 7.6), (86, 7.0), (92, 6.6)]     # the open jacket
V_NECK = [(63, 0), (67, 1.6), (76, 3.9), (84, 5.6), (92, 6.6)]                                       # the waistcoat's V
T_HALF = [(60, 2.9), (70, 2.7), (80, 2.1), (85, 1.6), (86, 1.4)]                                  # the tie
L_WIDE = [(56, 0), (62, 3.6), (68, 6.6), (74, 9.2), (79, 11.4), (84, 12.4)]                           # the lapels
V_BUTTONS = (66.5, 60.5, 54.5, 48.5, 42.5, 36.5)
# the jacket's relief in his (X, b): (X0, b0, X1, b1, height px (- = a crease), half-width)
J_FOLDS = [(19.0, 68.0, 22.0, 45.0, -0.35, 0.6),                                    # the near front's dart
           (20.0, 76.0, 23.0, 62.0, 0.55, 1.5), (23.0, 62.0, 26.5, 48.0, 0.55, 1.5),  # drape off the near lapel
           (22.5, 75.5, 12.0, 59.0, -0.55, 0.8), (25.5, 71.0, 15.5, 56.5, -0.45, 0.8),  # drag from the shoulder to the
           (14.0, 57.0, 11.5, 50.0, -0.35, 0.7),                                     # button over the belly
           (23.0, 50.5, 29.0, 49.0, -0.5, 0.7), (24.5, 53.5, 29.5, 52.5, -0.4, 0.7),  # creases above the pocketed arm
           (-11.0, 56.0, -13.5, 36.0, 0.5, 1.4), (-15.5, 54.0, -18.0, 38.0, -0.4, 0.8),  # the far front hanging open
           (-12.5, 76.0, -21.0, 66.0, -0.35, 0.8),                                   # drag across the far chest
           (20.5, 46.0, 26.5, 63.0, -0.75, 0.8), (24.0, 45.0, 28.5, 58.0, -0.6, 0.8),  # pulled from the pocket up to the
           (17.5, 47.0, 21.0, 56.0, -0.45, 0.8),                                     # armpit by the hand in it
           (-23.0, 66.5, -28.5, 64.5, -0.6, 0.8), (-22.0, 62.0, -28.0, 59.5, -0.55, 0.8),  # bunched under the far arm
           (-24.0, 71.0, -27.5, 70.0, -0.4, 0.8)]


class DonRig(Lamp):
    """Lamp + the normal and depth of every pixel, for the head-lamp's light on his own clothes"""
    def __init__(s, *a, **k):
        super().__init__(*a, **k)
        s.nrm, s._n, s.zoff = {}, (0.0, 0.0, 1.0), 0.0          # zoff: a part's forced depth order, not its place
        s.part = {}

    def shade(s, mat_, n, lift=0.0):
        s._n = n
        return super().shade(mat_, n, lift) + 0.10 * max(0.0, -n[1])          # the overcast sky above

    def zput(s, x, y, mat_, v, oid, d, fixed=None):
        k = (int(math.floor(x)), int(math.floor(y)))
        if not (0 <= k[0] < s.w and 0 <= k[1] < s.h): return
        if k in s.zb and s.zb[k] > d: return
        s.zb[k] = d
        s.buf[k] = [mat_, v, oid, fixed]
        s.nrm[k] = (s._n, d - s.zoff)

    def zell(s, cx, cy, rx, ry, mat_, d, lift=0.0, rot=0.0, flat=1.0, group=None, vfun=None):
        """an ellipsoid in canvas coords at depth d"""
        oid = s.new(group); c, sn = math.cos(rot), math.sin(rot); Rr = max(rx, ry) + 1
        for y in range(int(cy - Rr) - 1, int(cy + Rr) + 2):
            for x in range(int(cx - Rr) - 1, int(cx + Rr) + 2):
                dx, dy = x + 0.5 - cx, y + 0.5 - cy
                u, w = (dx * c + dy * sn) / rx, (-dx * sn + dy * c) / ry
                dd = u * u + w * w
                if dd > 1: continue
                nu, nw = u * flat, w * flat
                n = norm((nu * c - nw * sn, nu * sn + nw * c, math.sqrt(max(0.0, 1 - min(dd, 0.999)))))
                v = s.shade(mat_, n, lift) + (vfun(x, y, u, w) if vfun else 0)
                s.zput(x, y, mat_, v, oid, d + n[2] * min(rx, ry))
        return oid

    def ztube(s, a, b, ra, rb, mat_, d, lift=0.0, group=None, vfun=None):
        """a tapered round bar a->b in canvas coords at depth d; vfun(x, y, t, side) adds to the tone"""
        oid = s.new(group)
        (ax, ay), (bx, by) = a, b
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1e-6; L = math.sqrt(L2)
        Rr = max(ra, rb) + 2
        for y in range(int(min(ay, by) - Rr), int(max(ay, by) + Rr) + 1):
            for x in range(int(min(ax, bx) - Rr), int(max(ax, bx) + Rr) + 1):
                px, py = x + 0.5 - ax, y + 0.5 - ay
                t = max(0.0, min(1.0, (px * dx + py * dy) / L2))
                r_ = ra + (rb - ra) * t
                ox, oy = px - dx * t, py - dy * t
                dd = math.hypot(ox, oy)
                if dd > r_: continue
                sx, sy = ox / r_, oy / r_
                n = (sx, sy, math.sqrt(max(0.0, 1 - sx * sx - sy * sy)))
                side = (ox * dy - oy * dx) / (L * r_)
                v = s.shade(mat_, n, lift) + (vfun(x, y, t, side) if vfun else 0)
                s.zput(x, y, mat_, v, oid, d + n[2] * r_ * 0.5)
        return oid


def don(P):
    W, H, B, cx = DN['W'], DN['H'], DN['B'], DN['cx']
    s = DonRig(W, H, B, cx, F=1200.0, beye=-90.0)
    ct, st = math.cos(DN_YAW), math.sin(DN_YAW)
    SUIT = Mat(DN_SUIT, 'suit', 0.11, 0.04, outline=DN_OUT)
    SHIRT = Mat(DN_SHIRT, 'plain', 0.24, 0.0, outline=DN_OUT)
    TIE = Mat(DN_TIE, 'plain', 0.18, 0.35, outline=DN_OUT)
    GLOVE = Mat(DN_GLOVE, 'kid', 0.30, 0.10, outline=DN_OUT)
    BRASS = Mat(DN_BRASS, 'metal', 0.14, 0.55, outline=DN_OUT)
    BRONZE = Mat(DN_BRONZE, 'metal', 0.14, 0.35, outline=DN_OUT)
    VERD = Mat(DN_VERD, 'rust', 0.14, outline=DN_OUT)
    WARM = (246, 176, 92)
    SUITL = Mat(warmed(DN_SUIT, 0.42, WARM), 'suit', 0.11, 0.04, outline=DN_OUT)
    SHIRTL = Mat(warmed(DN_SHIRT, 0.4, WARM), 'plain', 0.24, outline=DN_OUT)
    TIEL = Mat(warmed(DN_TIE, 0.35, WARM), 'plain', 0.18, 0.35, outline=DN_OUT)
    GLOVEL = Mat(warmed(DN_GLOVE, 0.35, WARM), 'kid', 0.30, 0.10, outline=DN_OUT)
    BRASSL = Mat(warmed(DN_BRASS, 0.4, (255, 214, 140)), 'metal', 0.16, 0.55, outline=DN_OUT)
    ex, fs, bright = P.get('eye', 0.0), P.get('fs', 1.0), P.get('bright', 1.0)
    ember, sm, hand = P.get('ember', 0.5), P.get('smoke', 0), P.get('hand', 0)

    def rot(X, Z): return X * ct - Z * st, X * st + Z * ct

    # -------------------------------------------------------------------------------- the body (one surface)
    def section(b):
        return (spl(TOR_AF, b), spl(TOR_AN, b), spl(TOR_BD, b), spl(TOR_ZC, b), spl(TOR_ZN, b))

    def surf(X, b, dz=0.0):
        """the point on his front at his own X (px from the front line) and height b -> canvas x, y, depth"""
        aF, aN, bd, zc, zn = section(b)
        a = aN if X > 0 else aF
        sn_ = max(-0.999, min(0.999, X / a)); c = math.sqrt(1 - sn_ * sn_)
        Z = bd * c + zc * c * c + zn + dz
        xr, zr = rot(X, Z)
        x, y = s.proj(xr, b, zr)
        return x, y, zr

    def height(X, b, front, part):
        """the cloth's relief (px, + outward): folds, drape, strain"""
        h = 0.0
        if part == 'vest':
            for bk in V_BUTTONS:                                                  # strain smiles between the buttons
                ax = abs(X)
                if 0.9 < ax < 6.0:
                    yb = bk - 2.2 + 0.11 * ax ** 1.45
                    h -= 0.55 * math.exp(-((b - yb) / 0.7) ** 2) * min(1.0, (6.0 - ax) / 2.0)
            return h
        if part != 'jacket' or not front: return h
        e = spl(J_EDGE, b)
        if X > 0 and b < 60:                                                      # the near front drapes round the belly
            h += 0.9 * math.exp(-((X - e - 5.5) / 2.0) ** 2) * min(1.0, (60 - b) / 8)
            h -= 0.7 * math.exp(-((X - e - 9.5) / 1.4) ** 2) * min(1.0, (58 - b) / 10) if b < 58 else 0
        if X < 0 and b < 58:
            h += 0.7 * math.exp(-((-X - e - 4.0) / 1.8) ** 2) * min(1.0, (58 - b) / 8)
        for (ax_, ay_, bx_, by_, hh, wd) in J_FOLDS:
            if min(ax_, bx_) - 3 < X < max(ax_, bx_) + 3 and min(ay_, by_) - 3 < b < max(ay_, by_) + 3:
                h += hh * math.exp(-(segd(X, b, ax_, ay_, bx_, by_) / wd) ** 2)
        return h

    def cloth(X, b, front):
        """which cloth is at his (X, b): 'tie' 'shirt' 'vest' 'lapel' 'jacket' (+ the lapel's distance from its edge)"""
        if front:
            e = spl(J_EDGE, b)
            ax = abs(X)
            if ax < e:
                vn = spl(V_NECK, b) if b > 63 else 0.0
                if ax < vn:
                    return ('tie' if b < 86.5 and abs(X + 0.3) < spl(T_HALF, b) else 'shirt'), 0
                return 'vest', 0
            d = ax - e
            if b > 56 and d < spl(L_WIDE, b) and b < 81.0 + 0.62 * d: return 'lapel', d
            if X > 0 and 15.6 < X < 22.4 and 69.6 + 0.12 * (X - 15.6) < b:              # the pocket square
                zz = [(15.6, 1.2), (16.8, 3.8), (17.9, 1.6), (19.2, 4.6), (20.4, 1.4), (21.4, 3.2), (22.4, 0.8)]
                for i in range(len(zz) - 1):
                    if zz[i][0] <= X <= zz[i + 1][0]:
                        tt = (X - zz[i][0]) / (zz[i + 1][0] - zz[i][0]); hgt = zz[i][1] + (zz[i + 1][1] - zz[i][1]) * tt
                peak = 70.0 + 0.12 * (X - 15.6) + hgt
                if b < peak: return 'square', 0
        return 'jacket', 0

    def hp(X, b, Z):
        xr, zr = rot(X, Z)
        return xr, b, zr
    # the far arm (his right): the upper arm down his side, mostly behind him -- drawn first, so it lies behind
    SF, EF = (-24.0, 77.5, -1.5), (-34.0, 60.5, -2.0)
    s.zoff = -40; s.tube3([hp(*SF), hp(*EF)], lambda f: 6.6 - 0.8 * f, SUIT, lift=-0.06, group='farup', dz=-40)
    s.zoff = 0.0
    O = {k: s.new(k) for k in ('shirt', 'tie', 'vest', 'jacket', 'lapel', 'square')}
    MAT = {'shirt': SHIRT, 'tie': TIE, 'vest': SUIT, 'jacket': SUIT, 'lapel': SUIT, 'square': SHIRT}

    def body(region=None, dz=0.0, oid=None):
        b = 31.0
        while b <= 92.0:
            aF, aN, bd, zc, zn = section(b)
            daF = (spl(TOR_AF, b + 0.3) - spl(TOR_AF, b - 0.3)) / 0.6
            daN = (spl(TOR_AN, b + 0.3) - spl(TOR_AN, b - 0.3)) / 0.6
            dbd = (spl(TOR_BD, b + 0.3) - spl(TOR_BD, b - 0.3)) / 0.6
            dzc = (spl(TOR_ZC, b + 0.3) - spl(TOR_ZC, b - 0.3)) / 0.6
            dzn = (spl(TOR_ZN, b + 0.3) - spl(TOR_ZN, b - 0.3)) / 0.6
            nS = int(TAU * max(aF, aN, bd) / 0.33)
            for j in range(nS):
                sa = -math.pi + TAU * (j + 0.5) / nS
                c, sn_ = math.cos(sa), math.sin(sa)
                a, da = (aN, daN) if sn_ > 0 else (aF, daF)
                cp = max(0.0, c)
                X, Z = a * sn_, bd * c + zc * cp * cp + zn
                dPs = (a * c, 0.0, -bd * sn_ - 2 * zc * cp * sn_)
                dPb = (da * sn_, 1.0, dbd * c + dzc * cp * cp + dzn)
                nX = dPs[1] * dPb[2] - dPs[2] * dPb[1]
                nB = dPs[2] * dPb[0] - dPs[0] * dPb[2]
                nZ = dPs[0] * dPb[1] - dPs[1] * dPb[0]
                nx_, nz_ = rot(nX, nZ)
                if nz_ < -0.25 * math.sqrt(nX * nX + nB * nB + nZ * nZ): continue
                front = c > 0.15
                part, ld = cloth(X, b, front)
                if region and not region(X, b, part): continue
                n = [nx_, -nB, nz_]
                L = math.sqrt(sum(q * q for q in n)); n = [q / L for q in n]
                # relief: tilt the normal by the height field's slope (across = along his X, up = along b)
                h0 = height(X, b, front, part)
                if part in ('vest', 'jacket'):
                    gx = (height(X + 0.5, b, front, part) - height(X - 0.5, b, front, part))
                    gb = (height(X, b + 0.5, front, part) - height(X, b - 0.5, front, part))
                    if gx or gb:
                        tx, tz = rot(1.0, 0.0)
                        n = [n[0] - gx * tx * 0.9, n[1] + gb * 0.9, n[2] - gx * tz * 0.9]
                        L = math.sqrt(sum(q * q for q in n)); n = [q / L for q in n]
                xr, zr = rot(X, Z)
                x, y = s.proj(xr, b, zr)
                m = MAT[part]
                v = s.shade(m, n, 0.0) + 0.10 * min(0.0, h0)
                if part == 'lapel':
                    v += 0.05 + (0.16 if ld < 1.1 else 0) - (0.06 if spl(L_WIDE, b) - ld < 1.0 else 0)
                elif part == 'vest':
                    v -= 0.07                                                     # in the jacket's shade
                elif part == 'shirt':
                    v -= 0.04 + 0.18 * max(0.0, 1 - abs(abs(X) - spl(V_NECK, b)) / 1.5) * (b < 84)
                elif part == 'tie':
                    v += (0.10 if (int(math.floor(X * 1.0 + b * 0.9)) % 4 == 0) else 0)   # a woven diagonal stripe
                if part in ('jacket', 'vest'):
                    u = a * sa
                    if (u + 40) % 5.5 < 0.75: v += 0.05                           # a chalk pinstripe, round the body
                k_ = (int(math.floor(x)), int(math.floor(y)))
                if s.zb.get(k_, -1e9) <= zr + dz: s.part[k_] = part
                s.zput(x, y, m, v, oid or O[part], zr + dz)
            b += 0.33

    body()
    # seams: the open jacket's edges throw a shade into the opening and catch the light on their own edge; the lapels
    # shade the cloth under their outer edge
    adj = {}
    for k_, pt in s.part.items():
        for dx_, dy_ in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0)):
            q = s.part.get((k_[0] + dx_, k_[1] + dy_))
            if q and q != pt: adj.setdefault(k_, {})[q] = min(adj.get(k_, {}).get(q, 9), abs(dx_) + abs(dy_))
    for k_, qs in adj.items():
        pt, e = s.part[k_], s.buf.get(k_)
        if not e: continue
        jd = min(qs.get('jacket', 9), qs.get('lapel', 9))
        if pt in ('vest', 'shirt', 'tie') and jd < 9: e[1] -= 0.26 if jd == 1 else 0.10
        elif pt in ('jacket', 'lapel') and min(qs.get('vest', 9), qs.get('shirt', 9), qs.get('tie', 9)) == 1: e[1] += 0.12
        elif pt == 'jacket' and qs.get('lapel', 9) == 1: e[1] -= 0.22
        elif pt == 'jacket' and qs.get('lapel', 9) == 2: e[1] -= 0.08
    # waistcoat buttons, the watch chain from the middle button to the near pocket (it vanishes under the jacket)
    for bk in V_BUTTONS:
        x, y, z = surf(0.2, bk)
        s.zput(x, y, None, 0, s.new('vbtn'), z + 1, (122, 96, 58)); s.zput(x, y + 1, None, 0, s.n, z + 1, (24, 17, 12))
    oc, last, k = s.new('chain'), None, 0
    for i in range(0, 60):
        X = 0.6 + i * 0.2
        bb = 54.0 - 4.4 * math.sin(math.pi * min(1.0, X / 12.0)) + 0.3
        if X > spl(J_EDGE, bb) - 0.3: break
        x, y, z = surf(X, bb)
        if (int(x), int(y)) == last: continue
        last = (int(x), int(y))
        s.zput(x, y, None, 0, oc, z + 1, DN_CHAIN[(3, 2, 1)[k % 3]]); k += 1
    # jacket buttons on the open near front, the breast pocket's welt, the near hip pocket (the hand goes in there)
    for bk in (56.0, 46.0):
        X = spl(J_EDGE, bk) + 2.2
        x, y, z = surf(X, bk)
        s.zput(x, y, None, 0, s.new('jbtn'), z + 1, (64, 50, 38)); s.zput(x + 1, y, None, 0, s.n, z + 1, (40, 30, 23))
        s.zput(x, y + 1, None, 0, s.n, z + 1, (22, 16, 12))
    for i in range(0, 34):
        X = 15.4 + i * 0.2
        x, y, z = surf(X, 69.4 + 0.12 * (X - 15.4))
        s.darken(x, y, 0.22)

    # -------------------------------------------------------------------------------- arms
    s.zoff = 40
    # the near arm (his left): the shoulder lower, the elbow out and back, the hand deep in the hip pocket
    SN, EN, WN = (24.5, 74.0, -1.5), (31.5, 53.5, -6.5), (25.5, 41.5, 12.5)
    s.tube3([hp(*SN), hp(*EN)], lambda f: 6.8 - 0.9 * f, SUIT, lift=0.0, group='nearup', dz=40,
            vfun=lambda x, y, f: -0.10 * max(0.0, f - 0.75) * 4 * (0.5 + 0.5 * math.sin(x * 2.1 + y)))
    s.tube3([hp(*EN), hp(*WN)], lambda f: 5.7 - 0.8 * f, SUIT, lift=0.02, group='nearlo', dz=42,
            vfun=lambda x, y, f: (-0.12 if (f < 0.3 and (x + 2 * y) % 5 == 0) else 0))
    ex_, ey_ = s.proj(*hp(*EN))
    for (a_, l_) in ((2.5, 4.5), (2.9, 3.5), (2.1, 3.0)):                         # bunched in the crook of the elbow
        for i in range(int(l_ * 2)):
            s.darken(ex_ - 2.4 + math.cos(a_) * i * 0.5, ey_ - 0.8 + math.sin(a_) * i * 0.5, 0.15)
    # the hip pocket's flap over the wrist, and the hand's knuckles pressing the cloth below it
    def flap_region(X, b, part): return part == 'jacket' and 19.5 < X < 29.0 and 40.6 < b < 43.6 - 0.05 * (X - 19.5)
    s.zoff = 60; body(region=flap_region, dz=60, oid=s.new('flap'))
    s.zoff = 40
    bx_, by_, _ = surf(24.5, 37.6)
    for (x, y), e in s.buf.items():
        if e[2] != O['jacket']: continue
        u_, w_ = (x + 0.5 - bx_) / 4.6, (y + 0.5 - by_) / 3.0
        if u_ * u_ + w_ * w_ < 1: e[1] += 0.10 * (-w_ - 0.2 * u_)

    # the far forearm: from the elbow at his side forward and up to the cigar hand; creases bunch in the elbow's crook
    wx, wb, wz = -36.0, 70.5 + hand, 9.5
    s.tube3([hp(*EF), (wx, wb, wz)], lambda f: 5.9 - 1.1 * f, SUIT, lift=0.08, group='farlo', dz=40,
            vfun=lambda x, y, f: (-0.16 if (f < 0.34 and (x - 2 * y) % 5 == 0) else 0) + 0.08 * f)
    hx, hy = s.proj(wx, wb, wz)                                                   # the wrist on the canvas
    for (ax_, ay_, bx2, by2) in ((hx + 2.6, hy + 6.0, hx + 5.4, hy + 8.4), (hx + 1.0, hy + 3.4, hx + 4.4, hy + 6.6)):
        for i in range(9):                                                        # the sleeve's long folds
            q = (ax_ + (bx2 - ax_) * i / 8, ay_ + (by2 - ay_) * i / 8)
            s.darken(q[0], q[1], 0.16)
    hd = 300.0
    s.zoff = hd - wz
    # the shirt cuff, then the white glove, seen from the back: the back of the hand turned up toward the lamp, the
    # cigar between the first two fingers, the last two curled into the palm, the thumb along underneath
    s.ztube((hx + 1.4, hy + 1.4), (hx - 0.4, hy - 0.4), 3.1, 2.9, SHIRT, hd, lift=0.10, group='cuff')
    s.ztube((hx - 6.2, hy + 2.6), (hx - 7.6, hy + 4.0), 1.15, 1.0, GLOVE, hd + 1, lift=-0.16, group='pinky')
    s.ztube((hx - 7.0, hy + 1.2), (hx - 9.4, hy + 2.6), 1.25, 1.1, GLOVE, hd + 2, lift=-0.10, group='ring')
    s.ztube((hx - 9.4, hy + 2.6), (hx - 8.6, hy + 4.0), 1.1, 1.0, GLOVE, hd + 2, lift=-0.16, group='ring')
    s.zell(hx - 3.9, hy - 0.8, 4.4, 3.4, GLOVE, hd + 3, lift=0.04, rot=-0.22, group='back',
           vfun=lambda x, y, u, w: (-0.10 if abs(u * 0.9 + w * 0.5 - 0.15) < 0.12 and u < 0.4 else 0))
    s.ztube((hx - 2.0, hy + 2.6), (hx - 6.6, hy + 4.2), 1.5, 1.3, GLOVE, hd + 4, lift=-0.04, group='thumb')
    s.ztube((hx - 6.6, hy + 4.2), (hx - 8.8, hy + 3.6), 1.25, 1.05, GLOVE, hd + 4, lift=-0.02, group='thumb')
    s.ztube((hx - 7.4, hy - 0.6), (hx - 11.2, hy - 0.2), 1.35, 1.2, GLOVE, hd + 5, lift=-0.04, group='middle')
    s.ztube((hx - 11.2, hy - 0.2), (hx - 12.0, hy + 1.3), 1.15, 1.0, GLOVE, hd + 5, lift=-0.10, group='middle')
    s.ztube((hx - 7.0, hy - 3.4), (hx - 10.8, hy - 4.2), 1.35, 1.2, GLOVE, hd + 6, lift=0.10, group='index')
    s.ztube((hx - 10.8, hy - 4.2), (hx - 12.0, hy - 2.8), 1.15, 1.05, GLOVE, hd + 6, lift=0.02, group='index')
    for (kx, ky) in ((hx - 7.0, hy - 3.6), (hx - 7.4, hy - 1.0), (hx - 7.0, hy + 1.2)):
        e = s.buf.get((int(kx), int(ky)))
        if e and e[0] is GLOVE: e[1] += 0.12                                      # the knuckles catch the light
    for (gx, gy) in ((hx - 3.0, hy - 2.2), (hx - 2.2, hy - 0.6)):                 # the glove's stitched points
        s.darken(gx, gy, 0.14); s.darken(gx - 1, gy - 0.4, 0.10)

    s.zoff = 0.0
    # -------------------------------------------------------------------------------- the lamp-post foot
    def foot_tex(x, y, th, b):
        t = 0.0
        if 21.5 < b < 31.0: t += 0.20 * math.sin(th * 18)                         # gadroons round the bowl
        if 31.6 < b < 33.0 and int(th * 30 / TAU * 2) % 2 == 0: t += 0.18         # a bead under the lip
        if b < 6: t -= 0.10 * (6 - b) / 6                                         # the damp, dirty foot
        return t
    s.lathe([(23.0, 0), (23.0, 2.6), (21.6, 3.4), (21.6, 5.0), (19.4, 5.8), (17.0, 7.4), (15.0, 9.6), (13.8, 10.6),
             (15.2, 11.6), (15.6, 13.2), (14.2, 14.6), (11.6, 15.6), (11.0, 17.8), (12.6, 18.8), (12.6, 20.4), (11.6, 21.2),
             (13.2, 22.2), (17.2, 24.2), (21.0, 26.6), (24.6, 29.0), (27.0, 31.0), (28.0, 31.6), (28.0, 33.0), (29.4, 33.6),
             (30.6, 34.6), (30.9, 36.2), (30.2, 37.4), (28.6, 37.9), (27.4, 37.9)], BRONZE, lift=-0.04, tex=foot_tex)
    # verdigris in the cove and under the bowl, where the rain sits
    s.speckle({BRONZE: VERD}, 0.16, seed=41, region=lambda x, y: (B - 11 < y < B - 5) or (B - 23 < y < B - 20))

    # -------------------------------------------------------------------------------- the neck, the shirt collar, the tie knot
    s.lathe([(5.8, 84.0), (5.6, 88.0), (5.4, 90.8), (6.9, 91.6), (7.4, 93.0), (6.6, 94.2), (5.2, 95.0), (5.0, 96.6),
             (6.0, 97.6), (8.6, 99.0), (11.2, 100.2), (12.4, 100.8)], BRASS, lift=0.0, ox=DN_HX, oz=DN_HZ,
            tex=lambda x, y, th, b: -0.12 * max(0.0, (b - 96.0) / 4.0))
    s.lathe([(7.0, 87.4), (7.3, 87.6), (7.3, 90.6), (6.9, 91.0)], SHIRT, lift=-0.10, ox=DN_HX, oz=DN_HZ + 0.2)
    def onneck(X, b, dz):                                                         # on the collar ring's front
        x, y, _ = surf(X, b, dz - 9.6); return (x, y)
    nz0 = 9.6
    for sgn in (-1, 1):                                                           # the collar's wings
        pts = [onneck(sgn * 1.0, 90.4, nz0 + 0.6), onneck(sgn * 7.6, 90.2, nz0 - 2.6), onneck(sgn * 6.0, 82.0, nz0 - 0.6),
               onneck(sgn * 1.2, 85.0, nz0 + 0.8)]
        ys_ = [q[1] for q in pts]; xs_ = [q[0] for q in pts]
        def wing(x, y, sgn=sgn, ys_=ys_, xs_=xs_):                                 # starched: a few clean tones
            if y + 0.5 > max(ys_) - 1.0: return DN_SHIRT[4]                       # the shaded point's lower edge
            if sgn < 0: return DN_SHIRT[6] if x + 0.5 < (min(xs_) + max(xs_)) / 2 else DN_SHIRT[7]
            return DN_SHIRT[8] if x + 0.5 < min(xs_) + 0.55 * (max(xs_) - min(xs_)) else DN_SHIRT[6]
        s.fill(pts, SHIRT, (0, 0, 1), lift=0.0, d=40 + (1 if sgn > 0 else 0), group='wing%d' % sgn, fixedf=wing)
    kx0 = onneck(0, 86, nz0 + 1)[0]
    s.fill([onneck(-2.4, 89.4, nz0 + 0.8), onneck(2.2, 89.4, nz0 + 0.8), onneck(1.4, 84.8, nz0 + 1.2), onneck(-1.6, 84.8, nz0 + 1.2)],
           TIE, (0, 0, 1), lift=0.0, d=44, group='knot',
           fixedf=lambda x, y: DN_TIE[6] if x + 0.5 < kx0 - 0.4 else (DN_TIE[5] if x + 0.5 < kx0 + 1.4 else DN_TIE[3]))

    # -------------------------------------------------------------------------------- the head: a brass lantern
    ch, sh = math.cos(DN_HYAW), math.sin(DN_HYAW)
    def lp(X, b, Z):
        return s.proj(DN_HX + X * ch - Z * sh, b, DN_HZ + X * sh + Z * ch)
    def faces(b0, b1, h0, h1):
        """the front face (his front, turned toward the viewer's left), his left side, the underside -- canvas quads"""
        fr = [lp(-h0, b0, h0), lp(h0, b0, h0), lp(h1, b1, h1), lp(-h1, b1, h1)]
        sd = [lp(h0, b0, h0), lp(h0, b0, -h0), lp(h1, b1, -h1), lp(h1, b1, h1)]
        un = [lp(-h0, b0, h0), lp(h0, b0, h0), lp(h0, b0, -h0), lp(-h0, b0, -h0)]
        return fr, sd, un
    NF = lambda ty: (-sh, ty, ch)
    NS = lambda ty: (ch, ty, sh)
    # the roof: a square pyramid, its front face toward the sky's light
    rb0, rb1, rh0, rh1 = 132.0, 143.5, 16.6, 2.8
    fr, sd, _ = faces(rb0, rb1, rh0, rh1)
    streak = lambda x, y: (rig.nF(x * 2.6, y * 0.35) - 0.5) * 0.30                  # weathering run down the roof
    roof = (s.fill(fr, BRASS, NF(-0.75), lift=-0.20, d=300, group='roof', vfun=streak),
            s.fill(sd, BRASS, NS(-0.75), lift=-0.34, d=300, group='roof', vfun=streak))
    def toneline(p0, p1, dv, dx=0):
        n_ = int(max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1])) * 2) + 1
        for i in range(n_ + 1):
            q = (p0[0] + (p1[0] - p0[0]) * i / n_ + dx, p0[1] + (p1[1] - p0[1]) * i / n_)
            e = s.buf.get((int(math.floor(q[0])), int(math.floor(q[1]))))
            if e and e[2] in roof: e[1] += dv
    lerp2 = lambda a, b, u: (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
    for u in (0.22, 0.44, 0.66, 0.86):                                            # the roof's standing seams
        toneline(lerp2(fr[0], fr[1], u), lerp2(fr[3], fr[2], u), 0.20); toneline(lerp2(fr[0], fr[1], u), lerp2(fr[3], fr[2], u), -0.12, 1)
    for u in (0.35, 0.7):
        toneline(lerp2(sd[0], sd[1], u), lerp2(sd[3], sd[2], u), 0.08)
    toneline(fr[1], fr[2], 0.16)                                                  # the hip catches the sky
    # the eaves: a plate overhanging the glass; seen from below, its underside catches the glass's light
    eb0, eb1, eh = 129.4, 132.0, 17.6
    fr, sd, un = faces(eb0, eb1, eh, eh)
    s.fill(un, BRASSL, (0, 1, 0.3), lift=0.22, d=301, group='eaves')
    s.fill(fr, BRASS, NF(0), lift=-0.06, d=302, group='eaves', vfun=lambda x, y: 0.24 if y < min(fr[2][1], fr[3][1]) + 1.2 else 0)
    s.fill(sd, BRASS, NS(0), lift=-0.04, d=302, group='eaves')
    # the top rail and the base plate
    for (b0, b1, hh) in ((127.0, 129.4, 13.7), (99.6, 102.6, 11.8)):
        fr, sd, un = faces(b0, b1, hh, hh)
        s.fill(un, BRASS, (0, 1, 0.3), lift=-0.20, d=303, group='rail%d' % b0)
        s.fill(fr, BRASS, NF(0), lift=0.02, d=304, group='rail%d' % b0)
        s.fill(sd, BRASS, NS(0), lift=-0.06, d=304, group='rail%d' % b0)
    # the glass: four panes in a brass frame (two seen), the flame inside -- its "eye" -- and its light on the panes
    gb0, gb1, gh0, gh1 = 102.6, 127.0, 10.2, 13.0
    fr, sd, _ = faces(gb0, gb1, gh0, gh1)
    fx0, fy0 = lp(0.0, 112.0, 0.0)
    fx, fy = fx0 + ex, fy0 - (fs - 1.0) * 2.0
    def uv(q, x, y):
        """inverse bilinear: where (x, y) lies on the quad q (u across from the left, t up from the bottom)"""
        u, t = 0.5, 0.5
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = q
        for _ in range(6):
            px = (1 - u) * (1 - t) * x0 + u * (1 - t) * x1 + u * t * x2 + (1 - u) * t * x3
            py = (1 - u) * (1 - t) * y0 + u * (1 - t) * y1 + u * t * y2 + (1 - u) * t * y3
            dux, duy = (1 - t) * (x1 - x0) + t * (x2 - x3), (1 - t) * (y1 - y0) + t * (y2 - y3)
            dtx, dty = (1 - u) * (x3 - x0) + u * (x2 - x1), (1 - u) * (y3 - y0) + u * (y2 - y1)
            det = dux * dty - dtx * duy or 1e-9
            ex_, ey_ = x + 0.5 - px, y + 0.5 - py
            u += (ex_ * dty - ey_ * dtx) / det; t += (dux * ey_ - duy * ex_) / det
        return u, t
    def hot(x, y, k=1.0):
        dx_, dy_ = (x + 0.5 - fx) / (5.5 * k), (y + 0.5 - fy) / (7.5 * k)
        return math.exp(-(dx_ * dx_ + dy_ * dy_)) * bright
    def glass(q, side, wpx):
        def f(x, y):
            u, t = uv(q, x, y)
            bar = 1.7 / wpx
            if u < bar or u > 1 - bar or t < 0.05 or t > 0.95: return None          # the frame: shaded brass
            h_ = hot(x, y, 1.25 if side else 1.0)
            v = 0.30 + 0.12 * (1 - t) + 0.62 * h_ - 0.30 * max(0.0, t - 0.70) / 0.30   # the soot at the top
            v -= 0.10 * max(0.0, abs(u - 0.5) - 0.3) / 0.2                               # darker toward the posts
            if side: v = 0.16 + 0.08 * (1 - t) + 0.42 * h_ - 0.20 * max(0.0, t - 0.70) / 0.30
            col = pick(DN_GLASS, max(0.0, min(1.0, v)), x, y, 0.55)
            if not side:
                # the flame: a tear leaning a little the way it looks, a white core, a dark burner under it
                fdx = (x + 0.5 - fx + (fy - (y + 0.5)) * 0.10 * (ex / 3.0)) / (2.6 * fs)
                fdy = (y + 0.5 - fy) / (5.0 * fs)
                tear = fdx * fdx * (2.0 if fdy < 0 else 1.0) + fdy * fdy
                if tear < 1.0: return pick(TH_FLAME, 0.15 + 0.85 * (1 - tear) * bright, x, y, 0.5)
                bdx, bdy = (x + 0.5 - fx0) / 3.8, (y + 0.5 - (fy0 + 5.6)) / 1.7          # the burner under the wick
                if bdx * bdx + bdy * bdy < 1.0 and bdy > -0.6:
                    return DN_BRASS[9] if bdy < -0.1 else (DN_BRASS[4] if bdx < 0.2 else DN_BRASS[2])
                if abs((u - 0.16) + (1 - t) * 0.45 - 0.42) < 0.035 and t > 0.3:      # the sky caught on the glass
                    col = mix(col, DN_SKY, 0.45)
            return col
        return f
    fw = math.hypot(fr[1][0] - fr[0][0], fr[1][1] - fr[0][1])
    sw = math.hypot(sd[1][0] - sd[0][0], sd[1][1] - sd[0][1])
    s.fill(sd, BRASS, NS(0.11), lift=-0.06, d=305, group='glass', fixedf=glass(sd, True, sw))
    s.fill(fr, BRASS, NF(0.11), lift=0.0, d=306, group='glass', fixedf=glass(fr, False, fw),
           vfun=lambda x, y: 0.30 * hot(x, y, 1.6))
    # the finial: a chimney cap, a ring, a ball and a spike
    s.lathe([(3.4, 143.2), (3.2, 145.6), (4.4, 146.2), (4.4, 147.2), (3.0, 147.6), (2.0, 148.0)], BRASS, lift=0.0,
            ox=DN_HX, oz=DN_HZ, dz=320)
    s.lathe([(0.0, 147.6), (2.2, 148.2), (3.1, 150.2), (3.1, 151.4), (2.2, 153.4), (0.9, 154.0), (1.1, 155.0), (0.8, 158.0),
             (0.0, 160.6)], BRASS, lift=0.06, ox=DN_HX, oz=DN_HZ, dz=321)

    # -------------------------------------------------------------------------------- light
    # the head-lamp lights what faces it: his shoulders, the lapels' tops, the collar, the cigar hand; the base plate
    # throws a shadow straight down on his collar
    fz = DN_HZ
    swap = {SUIT: SUITL, SHIRT: SHIRTL, TIE: TIEL, GLOVE: GLOVEL, BRASS: BRASSL}
    for (x, y), e in s.buf.items():
        m = e[0]
        if m not in swap or (x, y) not in s.nrm: continue
        if y < fy + 4 and m is BRASS: continue
        n, d = s.nrm[(x, y)]
        lx, ly, lz = fx - (x + 0.5), fy - (y + 0.5), fz - d
        dist = math.sqrt(lx * lx + ly * ly + lz * lz) or 1.0
        lam = max(0.0, (n[0] * lx + n[1] * ly + n[2] * lz) / dist)
        down = (y + 0.5 - fy)
        cone = 1.0 if down < 8 else min(1.0, max(0.0, (math.hypot(x + 0.5 - fx, d - fz) / (down - 8) - 0.25) * 2.5))
        k = lam * cone / (1.0 + (dist / 44.0) ** 2) * bright
        if k <= 0.02: continue
        e[1] += 0.5 * k
        if k > 0.12 + 0.34 * (dith(x, y) + 0.47): e[0] = swap[m]
    im = s.render(outline=True, shadow=0.11, contact=0.09)
    p = im.load()

    # -------------------------------------------------------------------------------- the cigar, its ember, the smoke
    # held between the first two fingers, the lit end out to the left and a little up; drawn without an outline
    c0x, c0y = hx - 10.0, hy - 2.2
    ang = math.radians(198 - hand * 2)
    ln = 12.0
    dx_, dy_ = math.cos(ang), math.sin(ang)
    tip = (c0x + dx_ * ln, c0y + dy_ * ln)
    for i in range(int(ln * 3) + 1):
        t = i / (ln * 3)
        qx, qy = c0x + dx_ * ln * t, c0y + dy_ * ln * t
        for w_, col in ((0, DN_CIGAR[4] if t < 0.85 else DN_CIGAR[3]), (1, DN_CIGAR[1])):
            X_, Y_ = int(math.floor(qx)), int(math.floor(qy)) + w_
            if (X_, Y_) in s.buf: continue
            if 0.12 < t < 0.24: col = (150, 112, 52) if w_ == 0 else (96, 40, 30)                 # the band
            p[X_, Y_] = col + (255,)
    tx_, ty_ = int(math.floor(tip[0])), int(math.floor(tip[1]))
    p[tx_ + 1, ty_] = DN_ASH[2] + (255,); p[tx_ + 1, ty_ + 1] = DN_ASH[0] + (255,)
    e_ = max(0.0, min(1.0, ember))
    p[tx_, ty_] = DN_EMBER[3 + int(round(e_ * 3))] + (255,)
    p[tx_, ty_ + 1] = DN_EMBER[2 + int(round(e_ * 2))] + (255,)
    if e_ > 0.6: p[tx_ - 1, ty_] = DN_EMBER[2] + (255,)
    # a thin wisp rising from the ember, wavering, thinning and fading out as it climbs
    for i in range(70):
        t = i / 70.0
        rise = t * 46.0
        ph = sm * 0.8
        qx = tip[0] - 0.5 + 2.6 * math.sin(rise * 0.17 - ph) * t ** 0.6 + 1.6 * math.sin(rise * 0.05 + ph * 0.5) * t + t * 4.0
        qy = tip[1] - 1.5 - rise
        a_ = int(235 * (1 - t) ** 0.9 * (0.78 + 0.22 * math.sin(i * 0.9 + sm)))
        if a_ < 30 or h32(i, sm, 9) % 9 == 0: continue
        for (ox_, oy_, k_) in ((0, 0, 1.0), (1 if t > 0.35 else 0, 0, 0.5 if t > 0.35 else 0)):
            X_, Y_ = int(math.floor(qx)) + ox_, int(math.floor(qy)) + oy_
            if not (0 <= X_ < W and 0 <= Y_ < H) or p[X_, Y_][3] == 255: continue
            p[X_, Y_] = DN_SMOKE + (max(p[X_, Y_][3], int(a_ * k_)),)
    # the breath: everything above the waistcoat's top button rises a pixel
    if P.get('breath', 0):
        cut = int(B - 64)
        src = im.copy()
        for y in range(0, cut):
            for x in range(W):
                p[x, y] = src.getpixel((x, y + 1))
    return im


DON_POSE = [  # 0 rest  1 the ember breathes, the smoke rises  2 the flame turns to the viewer's left (toward the player)
              # 3 holds there  4 the cigar hand lifts, the ember glows  5 the breath, the flame comes back
              # 6 it glances right  7 settle
    dict(smoke=0, ember=0.3), dict(smoke=1, ember=0.8), dict(smoke=2, eye=-2.6, ember=0.5, fs=1.04),
    dict(smoke=3, eye=-3.4, ember=0.3, fs=1.06, bright=1.05), dict(smoke=4, eye=-1.6, hand=2, ember=1.0),
    dict(smoke=5, breath=1, ember=0.6), dict(smoke=6, eye=2.2, ember=0.3, fs=0.96), dict(smoke=7, ember=0.4)]

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
