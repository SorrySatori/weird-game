"""The skyship Verdigrace over the Crossroad: CrossroadScene's look-up cut (skyship.png), drawn natively at 1067x600.

The player stands at the overgrown corpse and looks up. The camera is the shared rasteriser (raster3d.py) with its
own lens for this one shot: pitched 29 degrees up, focal length 700 (the walkable scenes use a level camera, F 300;
raster3d.F / paintpass.F are patched at runtime in this process only, the modules stay untouched), so the ship is
seen from below but still side-on enough to read, and the street's verticals lean in. Everything is built in world
space and turned into the camera's frame; the two big bodies (the gas bladder, the gondola's hull) are ray-marched
implicit shapes, the rest are raster3d quads, discs and lines. paintpass gets WORLD positions and normals, so its
grime, rain-wash and damp follow gravity, not the tilted camera.

The ship is the one SkyshipBoardScene stands on (board_bg.py), in the deck's own coordinates (x along the keel, the
bow with the fiddlehead stem at x -27.6, the cabin from x 17 aft on the far half; z = board Z - 15, the street on the
near side): the moss-green bladder in a slack diamond net (centred over the gondola and lower than on the deck, as in
the old picture), each cell puffed between the cords, spores glowing in its skin, moss dripping off the lower cords,
fan fins at its tail; the gondola's hull of dark strakes with a warm wale and rubbing strake, bound by living-wood
ribs on a living-wood keel, the prow and stern sweeping up, the solid bulwark capped in warm wood, the
twisted living-wood balusters and the top rail, the stem rising into its fiddlehead curl with the lantern hung from
it, the two vine-wrapped stanchions with glowing pods carrying the rigging up, the rope ladder by the bow (the way
up the tree), lit portholes in the stern, a spore-lit underside hung with moss and roots. Captain Liris (liris.py,
scaled down) leans at the rail. Below: the mycelium tree from the corpse climbing to the bow, its flat caps glowing
from beneath; Shed 521's timber crown and the Voxmarket's arch frame the bottom corners (what the Crossroad shows
as the camera tilts up), with the street's cables strung across. Overcast emerald-grey day.

The message box of the cut (600x100 at canvas x 233..833, y 470..570) sits under the ship: keep that band quiet.

    python3 skyship_native_bg.py <outdir> [--fast] [--plan]
        -> <outdir>/skyship.png (= assets/images/backgrounds/skyship.png), <outdir>/skyship_native.gpl,
           <outdir>/guides.png (the message box, for the hidden guide layer of the Aseprite source)
        --plan prints where the landmarks land on screen and stops; --fast skips the painterly pass (layout previews)
"""
import sys, os, math
import raster3d, paintpass
FC = 700.0                                   # this shot's lens (patched into the shared modules for this process only)
raster3d.F = FC
paintpass.F = FC
from raster3d import Raster, W, H, CX, HY, CAMH
from PIL import Image
from common import h32, ramp
from shedkit import wn, tone, mix

OUT = next((a for a in sys.argv[1:] if not a.startswith('--')), '.')
FAST = '--fast' in sys.argv
PLAN = '--plan' in sys.argv
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
BOX = (233, 470, 833, 570)                   # the cut's message box on the canvas

# ---------------------------------------------------------------------------------------------------- palette
SKYC = ramp('#1f3c35 #26473e #2e5347 #375f51 #416b5b #4b7765 #568370 #63907c #719c88 #81a894 #93b5a1')
ENVC = ramp('#0b140d #111e13 #18291a #203421 #293f27 #33492c #3e5431 #4a6037 #586c3e')     # the bladder's skin
NETC = ramp('#17170c #232312 #313018 #403e1f #504d27 #615d30 #736e3a')                     # net cords, ropes
LIVE = ramp('#0d160a #142010 #1c2c14 #253919 #2f461e #3a5424 #46622b #547133')             # living wood, moss
HULL = ramp('#110c08 #1a120c #241a11 #2f2316 #3a2c1b #463521 #533f28')                     # hull strakes
DECK = ramp('#1f120a #2d1a0e #3c2413 #4c2e19 #5d3920 #6f4528 #825232')                     # warm wood: rails, caps
POD = ramp('#2a6420 #46962e #72c442 #aee86c #dcffae')                                       # spore glow (board_bg)
BRASS = ramp('#271c0d #3f2e18 #5a4324 #775b31 #977642 #ba9558')
MEMB = ramp('#0e170f #142114 #1b2c19 #24381f #2e4526 #3a532d #486236')                      # fin membranes
TRUNK = ramp('#0c170e #112015 #182c1b #203923 #2a472b #355634 #42663d #507647')            # the mycelium tree
CAPU = ramp('#1d3a28 #2a5236 #3e6e48 #5b8f60 #8cc08a #c4ecc0')                            # the caps' undersides
MYCG = ramp('#143a22 #1f5a32 #2f7845 #3f8f5a #5fc777 #7fff8e #c8ffd0')                      # its glow (pal_day MYC)
TIMB = ramp('#120d09 #1b140e #251c13 #302419 #3c2d1f #483726 #55412e')                     # Shed 521's planks
STUC = ramp('#2e2f25 #3e3f31 #51523f #65664e #7a7c5f #90926f #a6a883')                     # the Voxmarket's stucco
RUSTY = ramp('#24120a #3a1d10 #552a16 #6f381d #8a4a26 #a35e33')
AMBER = ramp('#5a3a14 #7d5320 #a2702c #c48f3c #e0b055 #f2cf7c')                            # its lit glass, lanterns
WARMG = (255, 196, 110)
INK = (8, 12, 10)


# ---------------------------------------------------------------------------------------------------- the camera
PITCH = math.radians(29.0)
CPI, SPI = math.cos(PITCH), math.sin(PITCH)
EYE = (0.0, 5.6, 0.0)                        # the priest's eyes, at the corpse


def w2c(P):
    """world -> the rasteriser's camera frame (x right, y up with the eye at CAMH, z = depth along the view)"""
    rx, ry, rz = P[0] - EYE[0], P[1] - EYE[1], P[2] - EYE[2]
    return (rx, CAMH + ry * CPI - rz * SPI, ry * SPI + rz * CPI)


def c2w(Pc):
    rx, yc, zc = Pc[0], Pc[1] - CAMH, Pc[2]
    return (rx + EYE[0], yc * CPI + zc * SPI + EYE[1], -yc * SPI + zc * CPI + EYE[2])


def nc2w(n): return (n[0], n[1] * CPI + n[2] * SPI, -n[1] * SPI + n[2] * CPI)
def nw2c(n): return (n[0], n[1] * CPI - n[2] * SPI, n[1] * SPI + n[2] * CPI)
def scr(P): return raster3d.proj(*w2c(P))
def ray_w(x, y):
    dx, dy = raster3d.ray(x, y)
    return nc2w((dx, dy, 1.0))                 # a world direction whose parameter is the camera depth
def norm(v):
    l = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) or 1.0
    return (v[0] / l, v[1] / l, v[2] / l)
def clamp(v, a=0.0, b=1.0): return a if v < a else b if v > b else v


# ---------------------------------------------------------------------------------------------------- the ship's frame
YAW = math.radians(-13.0)                    # the bow (left) swings toward the camera
SO = (-1.0, 53.0, 100.0)                     # the deck's centre line at the board's x 0
CYW, SYW = math.cos(YAW), math.sin(YAW)
def s2w(p): return (SO[0] + CYW * p[0] + SYW * p[2], SO[1] + p[1], SO[2] - SYW * p[0] + CYW * p[2])
def w2s(P):
    dx, dy, dz = P[0] - SO[0], P[1] - SO[1], P[2] - SO[2]
    return (CYW * dx - SYW * dz, dy, SYW * dx + CYW * dz)
def ns2w(n): return (CYW * n[0] + SYW * n[2], n[1], -SYW * n[0] + CYW * n[2])
def nw2s(n): return (CYW * n[0] - SYW * n[2], n[1], SYW * n[0] + CYW * n[2])
def s2c(p): return w2c(s2w(p))
def sscr(p): return scr(s2w(p))


# ---------------------------------------------------------------------------------------------------- light + haze
KEY = norm((0.45, 0.85, -0.3))               # the bright patch of the overcast: high, to the right
SUNDIR = norm((0.5, 0.55, 0.65))             # where that patch sits in the sky (behind the ship's tail)


def light(nw):
    """overcast: a sky dome from above, a soft key from the bright patch, a little bounce from the city below"""
    sky = 0.5 + 0.5 * nw[1]
    key = max(0.0, nw[0] * KEY[0] + nw[1] * KEY[1] + nw[2] * KEY[2])
    return 0.1 + 0.55 * sky + 0.4 * key + 0.06 * max(0.0, -nw[1])


SKYIMG = None                                 # the rendered sky (rows of RGB); SKYSOFT = a blurred copy for the haze
SKYSOFT = None


def haze(c, x, y, P, k=1.0):
    """aerial perspective: blend toward the sky right behind the pixel by distance from the eye"""
    d = math.dist(P, EYE)
    h = (1 - math.exp(-d / 420.0)) * k
    s = SKYSOFT[min(H - 1, max(0, y))][min(W - 1, max(0, x))]
    return mix(c, s, min(0.6, h))


# ---------------------------------------------------------------------------------------------------- the sky
def build_sky():
    """the overcast ceiling seen from below: a cloud deck at 900 units, its noise in world units and stretched along
    the wind (so the masses flatten toward the horizon), thicker darker masses, a luminous patch behind the ship's
    tail, darker straight overhead, a pale haze low down"""
    rows = []
    for y in range(H):
        row = []
        for x in range(W):
            d = norm(ray_w(x, y))
            elev = math.asin(clamp(d[1], -1, 1))
            t = 900.0 / max(0.05, d[1])
            cx, cz = d[0] * t, d[2] * t
            f = 0.58 * wn(0, cx * 0.0021 + 11.0, cz * 0.0046) + 0.29 * wn(1, cx * 0.0062, cz * 0.013) + 0.13 * wn(2, cx * 0.018, cz * 0.036)
            far = clamp(1 - elev / 0.5)
            sg = max(0.0, d[0] * SUNDIR[0] + d[1] * SUNDIR[1] + d[2] * SUNDIR[2])
            v = 4.75 + 1.7 * sg ** 10 + 0.8 * sg ** 3
            th = clamp((f - 0.5) * 3.0, -1, 1)
            v -= th * (1.9 - 1.0 * far)
            v += far * 0.8 - clamp((elev - 0.62) / 0.32) * 1.2
            v += (wn(1, x * 0.02, y * 0.07) - 0.5) * 0.35
            row.append(tone(SKYC, v, x, y))
        rows.append(row)
    return rows


def blur_rows(rows, r=9):
    im = Image.new('RGB', (W, H)); p = im.load()
    for y in range(H):
        for x in range(W): p[x, y] = rows[y][x]
    from PIL import ImageFilter
    im = im.filter(ImageFilter.GaussianBlur(r)); p = im.load()
    return [[p[x, y] for x in range(W)] for y in range(H)]


# ---------------------------------------------------------------------------------------------------- ray-marched bodies
def const(c): return lambda x, y, s, t, z, wp: c


def cast(rs, obj, field, bound, box, colf, step=0.5, nbis=7):
    """ray-march an implicit body (field < 0 inside, in ship coordinates) over the screen box; colf(x, y, p_ship,
    n_ship, P_world, n_world) -> (colour, cls). bound(o, d) -> (t0, t1) in camera depth or None."""
    o = w2s(EYE)
    x0, y0, x1, y1 = box
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            d = nw2s(ray_w(x, y))
            tr = bound(o, d)
            if not tr: continue
            t0, t1 = tr
            t0 = max(t0, 1.0)
            if t0 >= rs.ZB[y][x] or t1 <= t0: continue
            t = t0; hit = None
            p = (o[0] + d[0] * t, o[1] + d[1] * t, o[2] + d[2] * t)
            if field(p) < 0: hit = t
            while hit is None and t < t1:
                t2 = t + step
                p = (o[0] + d[0] * t2, o[1] + d[1] * t2, o[2] + d[2] * t2)
                if field(p) < 0:
                    a, b = t, t2
                    for _ in range(nbis):
                        m = (a + b) * 0.5
                        pm = (o[0] + d[0] * m, o[1] + d[1] * m, o[2] + d[2] * m)
                        if field(pm) < 0: b = m
                        else: a = m
                    hit = b
                t = t2
            if hit is None or hit >= rs.ZB[y][x]: continue
            p = (o[0] + d[0] * hit, o[1] + d[1] * hit, o[2] + d[2] * hit)
            e = 0.06
            n = norm((field((p[0] + e, p[1], p[2])) - field((p[0] - e, p[1], p[2])),
                      field((p[0], p[1] + e, p[2])) - field((p[0], p[1] - e, p[2])),
                      field((p[0], p[1], p[2] + e)) - field((p[0], p[1], p[2] - e))))
            Pw = s2w(p); nw = ns2w(n)
            c, cl = colf(x, y, p, n, Pw, nw)
            if c is None: continue
            rs.put(x, y, hit, const(c), obj, 0.0, 0.0, w2c(Pw), nw2c(nw), cl)


def ellipsoid_bound(C, R):
    def b(o, d):
        ox, oy, oz = (o[0] - C[0]) / R[0], (o[1] - C[1]) / R[1], (o[2] - C[2]) / R[2]
        dx, dy, dz = d[0] / R[0], d[1] / R[1], d[2] / R[2]
        A = dx * dx + dy * dy + dz * dz; B = 2 * (ox * dx + oy * dy + oz * dz); Cc = ox * ox + oy * oy + oz * oz - 1
        disc = B * B - 4 * A * Cc
        if disc < 0: return None
        s = math.sqrt(disc)
        return ((-B - s) / (2 * A), (-B + s) / (2 * A))
    return b


def box_bound(lo, hi):
    def b(o, d):
        t0, t1 = -1e9, 1e9
        for i in range(3):
            if abs(d[i]) < 1e-9:
                if o[i] < lo[i] or o[i] > hi[i]: return None
                continue
            a, c = (lo[i] - o[i]) / d[i], (hi[i] - o[i]) / d[i]
            if a > c: a, c = c, a
            t0, t1 = max(t0, a), min(t1, c)
            if t0 > t1: return None
        return (t0, t1)
    return b


def screen_box(pts, pad=6):
    sp = [sscr(p) for p in pts]
    return (int(min(p[0] for p in sp)) - pad, int(min(p[1] for p in sp)) - pad, int(max(p[0] for p in sp)) + pad, int(max(p[1] for p in sp)) + pad)


def corners(lo, hi): return [(a, b, c) for a in (lo[0], hi[0]) for b in (lo[1], hi[1]) for c in (lo[2], hi[2])]


# ---------------------------------------------------------------------------------------------------- the ship: geometry
BC = (-2.0, 37.0, 0.0)                       # the bladder's centre, half-length, half-height, half-width
BL, BRY, BRZ = 55.0, 19.5, 20.5


def prof(u):
    """the bladder's radius along its length: a blunt nose (bow side, u -1), the fullest a quarter back, a long taper"""
    if u <= -1.0 or u >= 1.0: return 0.0
    if u < -0.3:
        a = (u + 0.3) / 0.7
        return (1 - a * a) ** 0.42
    a = (u + 0.3) / 1.3
    return max(0.0, 1 - a ** 2.1) ** 0.75


def env_field(p):
    qx, qy, qz = p[0] - BC[0], p[1] - BC[1], p[2] - BC[2]
    u = qx / BL
    if u <= -1.0 or u >= 1.0: return 1.0
    return math.sqrt((qy / BRY) ** 2 + (qz / BRZ) ** 2) - prof(u)


def env_point(u, th, lift=0.0):
    """a point on the bladder's skin: u along it, th round it (0 on top, -pi/2 toward the camera, +-pi beneath)"""
    r = prof(u) + lift
    return (BC[0] + u * BL, BC[1] + math.cos(th) * BRY * r, BC[2] + math.sin(th) * BRZ * r)


STEM = (-27.6, 1.2)                          # the stem post (x, z) as on the board
XB0, XB1 = -28.6, 42.0                       # the hull from the bow to the stern


def half_w(x):
    """half the beam at deck level"""
    if x < -19.0:
        t = (-19.0 - x) / 9.6
        return 9.0 * max(0.0, 1 - t ** 1.7) ** 0.75
    if x > 34.0: return 9.0 * math.sqrt(max(0.0, 1 - ((x - 34.0) / 8.0) ** 2))
    return 9.0


def depth(x):
    """how deep the hull goes below the deck: full amidships, the keel sweeping up into the prow and the stern"""
    if x < 4.0:
        t = min(1.0, (4.0 - x) / 32.8)
        return 0.2 + 10.7 * max(0.0, 1 - t ** 2.4) ** 1.6
    t = min(1.0, (x - 4.0) / 38.2)
    return 0.6 + 10.3 * max(0.0, 1 - t ** 2.2) ** 1.3


BW_TOP = 1.95                                # the solid bulwark; balusters above it to the top rail at 3.62


def hull_field(p):
    x, y, z = p
    w = half_w(x)
    if w <= 0.01: return 1.0
    if y > BW_TOP: return y - BW_TOP
    d = depth(x)
    if y >= 0:
        ww = w * (1 + 0.012 * y)
        return abs(z) - ww
    if -y >= d: return -y - d
    ww = w * max(0.0, 1 - (-y / d) ** 1.35) ** 0.85
    return abs(z) - ww


# ---------------------------------------------------------------------------------------------------- plan
def plan():
    pts = {
        'bladder nose': env_point(-0.99, -math.pi / 2), 'bladder tail': env_point(0.99, 0),
        'bladder top (mid)': env_point(-0.25, 0), 'bladder bottom (mid)': env_point(-0.25, math.pi),
        'bladder near side': env_point(-0.25, -math.pi / 2),
        'stem top': (STEM[0] + 1.5, 12.6, STEM[1]), 'bow keel': (-27.0, -0.6, 0), 'stern': (42.0, 1.9, 0),
        'keel (mid)': (6.0, -8.2, 0), 'rail near (mid)': (7.0, 3.6, -9.0), 'cabin roof near': (30.0, 8.7, 9.0),
        'ladder hook': (-24.5, 3.6, -7.0),
    }
    for k, p in pts.items():
        Pw = s2w(p); sx, sy = scr(Pw)
        print(f'{k:22s} screen ({sx:6.1f}, {sy:6.1f})  dist {math.dist(Pw, EYE):6.1f}')
    for (x, y) in ((0, 600), (533, 600), (1066, 600), (533, 0)):
        d = norm(ray_w(x, y)); print('elev at', (x, y), round(math.degrees(math.asin(d[1])), 1))
    print('message box', BOX, '- the keel (and the roots under it) must stay above y', BOX[1])




# ---------------------------------------------------------------------------------------------------- shading helpers
def W_(fn):
    """a raster3d shader working in world space: fn(x, y, s, t, P_world or None)"""
    return lambda x, y, s, t, z, wp: fn(x, y, s, t, c2w(wp) if wp is not None else None)


def line_sh(r, v0, k=3.0, nrm=(0.0, -0.3, -1.0), hz=1.0, alt=0.6, ship=True):
    """flat-ish shading for thin things (ropes, balusters, strands): one nominal normal, a dithered highlight"""
    L = light(norm(ns2w(nrm) if ship else nrm))
    def f(x, y, s, t, P):
        c = tone(r, v0 + k * L + (alt if (x + 2 * y) % 3 == 0 else 0.0), x, y)
        return haze(c, x, y, P, hz) if P is not None else c
    return W_(f)


def sline(rs, a, b, sh, w, sag=0.0, cls='prop', n=0):
    """a 3D line between two ship points (sag in world units, straight down)"""
    if sag == 0.0:
        return rs.line3(s2c(a), s2c(b), sh, w=w, cls=cls, n=n)
    pts = [(a[0] + (b[0] - a[0]) * i / 8, a[1] + (b[1] - a[1]) * i / 8 - sag * math.sin(math.pi * i / 8), a[2] + (b[2] - a[2]) * i / 8) for i in range(9)]
    for p, q in zip(pts, pts[1:]): rs.line3(s2c(p), s2c(q), sh, w=w, cls=cls)


def wline(rs, a, b, sh, w, sag=0.0, cls='prop', segs=10):
    """a 3D line between two WORLD points, sagging under its weight"""
    pts = [(a[0] + (b[0] - a[0]) * i / segs, a[1] + (b[1] - a[1]) * i / segs - sag * math.sin(math.pi * i / segs), a[2] + (b[2] - a[2]) * i / segs) for i in range(segs + 1)]
    for p, q in zip(pts, pts[1:]): rs.line3(w2c(p), w2c(q), sh, w=w, cls=cls)


def squad(rs, p0, p1, p3, sh, cls='prop', cut=False):
    return rs.quad(s2c(p0), s2c(p1), s2c(p3), sh, cls=cls, cut=cut)


def wquad(rs, p0, p1, p3, sh, cls='prop', cut=False):
    return rs.quad(w2c(p0), w2c(p1), w2c(p3), sh, cls=cls, cut=cut)


def glow_disc(rs, Pw, r, core=POD[4], mid=POD[3], rim=POD[1]):
    """a small glowing pod / spore (camera-facing)"""
    Pc = w2c(Pw)
    def sh(x, y, s, t, z, wp):
        d = math.hypot(s, t)
        return core if d < 0.4 else mid if d < 0.72 else rim
    rs.disc(Pc[0], Pc[1], Pc[2], r, sh, cls='emit')


# ---------------------------------------------------------------------------------------------------- the bladder
MU, MT = 3.6, 1.25                           # the net: diamonds along / round the bladder


def env_col(x, y, p, n, Pw, nw):
    qx, qy, qz = p[0] - BC[0], p[1] - BC[1], p[2] - BC[2]
    u = qx / BL
    th = math.atan2(qz / BRZ, qy / BRY)
    L = light(nw)
    rl = max(0.15, prof(u))
    wob = (wn(2, u * 5.0, th * 1.6) - 0.5) * 0.34 + (wn(3, u * 14.0, th * 4.0) - 0.5) * 0.08
    a1 = u * MU + th * MT + wob
    a2 = u * MU - th * MT - wob * 0.6
    f1, f2 = a1 % 1.0, a2 % 1.0
    e1, e2 = 0.5 - abs(f1 - 0.5), 0.5 - abs(f2 - 0.5)
    px = math.dist(Pw, EYE) / FC
    g = math.sqrt((MU / BL) ** 2 + (MT / (min(BRY, BRZ) * rl)) ** 2)
    lower = abs(th) > 1.8
    hw = max(0.3, 0.75 * px) * g * (1.35 if lower else 1.0) * (0.8 + 0.5 * wn(1, u * 9.0, th * 3.0))
    knot = e1 < hw * 2.2 and e2 < hw * 2.2                                         # where two cords cross
    if e1 < hw or e2 < hw or knot:                                                 # a cord of the net
        c = tone(NETC, 0.9 + 5.0 * L + (0.8 if min(e1, e2) < hw * 0.45 else 0.0), x, y)
        if knot: c = tone(NETC, 0.5 + 5.0 * L + (0.9 if (x + y) % 2 else 0.2), x, y)
        if lower and wn(3, u * 30, th * 9) > 0.5:                                  # moss clinging to the lower cords
            c = tone(LIVE, 1.4 + 4.6 * L + (0.8 if (x * 3 + y) % 4 == 0 else 0.0), x, y)
        return haze(c, x, y, Pw), 'prop'
    pe = min(e1, e2) / 0.5                                                         # 0 at a cord .. 1 mid-cell
    # each cell is a pillow between the cords: tilt the normal by the pillow's slope
    p1, p2 = f1 - 0.5, f2 - 0.5
    g1 = -math.pi * math.sin(math.pi * p1) * math.cos(math.pi * p2)
    g2 = -math.pi * math.cos(math.pi * p1) * math.sin(math.pi * p2)
    rr_ = prof(u)
    du = (BL, 0.0, 0.0)
    dth = (0.0, -math.sin(th) * BRY * rr_, math.cos(th) * BRZ * rr_)
    T1 = norm((du[0] / (2 * MU) + dth[0] / (2 * MT), du[1] / (2 * MU) + dth[1] / (2 * MT), du[2] / (2 * MU) + dth[2] / (2 * MT)))
    T2 = norm((du[0] / (2 * MU) - dth[0] / (2 * MT), du[1] / (2 * MU) - dth[1] / (2 * MT), du[2] / (2 * MU) - dth[2] / (2 * MT)))
    kq = 0.3
    npl = norm((n[0] - kq * (g1 * T1[0] + g2 * T2[0]), n[1] - kq * (g1 * T1[1] + g2 * T2[1]), n[2] - kq * (g1 * T1[2] + g2 * T2[2])))
    Lp = light(ns2w(npl))
    v = 0.5 + 6.0 * Lp - 1.4 * (1 - pe) ** 3
    v += (wn(0, u * 30, th * 9) - 0.5) * 0.45 + (wn(1, u * 110, th * 34) - 0.5) * 0.35
    c = tone(ENVC, v, x, y)
    li = wn(3, u * 90 + 13, th * 26)                                               # lichen on the skin
    if li > 0.74: c = mix(c, tone(LIVE, 2.6 + 4.0 * Lp, x, y), min(0.6, (li - 0.74) * 6))
    # spores glowing in the skin: one in some cells, most of them on the underside
    i1, i2 = math.floor(a1), math.floor(a2)
    hh = h32(i1 + 500, i2 + 500, 7)
    every = 2 if abs(th) > 2.3 else 3 if lower else 6
    if hh % every == 0:
        cu, cv = 0.32 + ((hh >> 4) & 15) / 42.0, 0.32 + ((hh >> 8) & 15) / 42.0
        rr = 0.035 + ((hh >> 12) & 3) * 0.012
        dd = math.hypot(f1 - cu, f2 - cv)
        if dd < rr * 0.45: return (POD[4] if (hh >> 14) & 1 else POD[3]), 'emit'
        if dd < rr: return POD[2], 'emit'
        if dd < rr * 2.8: c = mix(c, POD[1] if dd < rr * 1.5 else POD[0], 0.6 * (1 - (dd - rr) / (rr * 1.8)))
    return haze(c, x, y, Pw), 'prop'


def fan_fin(rs, O, ax, bx, phi0, phi1, rho, nribs, seed, cls='prop'):
    """a membranous fan fin in ship space: pivot O, the plane spanned by unit vectors ax (phi 0) and bx (phi 90 deg);
    rho(s) = the outline radius for s 0..1 between phi0 and phi1; scalloped between the ribs, a little torn"""
    R = max(rho(i / 40.0) for i in range(41)) + 1.0
    nrm = norm((ax[1] * bx[2] - ax[2] * bx[1], ax[2] * bx[0] - ax[0] * bx[2], ax[0] * bx[1] - ax[1] * bx[0]))
    nwv = ns2w(nrm)
    L = max(light(nwv), light((-nwv[0], -nwv[1], -nwv[2])))
    def P(a, b): return (O[0] + ax[0] * a + bx[0] * b, O[1] + ax[1] * a + bx[1] * b, O[2] + ax[2] * a + bx[2] * b)
    def sh(x, y, s, t, z, wp):
        A, B = (2 * s - 1) * R, (2 * t - 1) * R
        r = math.hypot(A, B); ph = math.atan2(B, A)
        sf = (ph - phi0) / (phi1 - phi0)
        if sf < 0 or sf > 1 or r < 0.3: return None
        fr = (sf * nribs) % 1.0
        edge = rho(sf) * (1 - 0.17 * math.sin(math.pi * fr) ** 1.3)
        if r > edge: return None
        if r > edge * 0.86 and wn(seed % 4, ph * 9 + seed, r * 0.7) > 0.66: return None          # torn
        Pw = c2w(wp)
        px = math.dist(Pw, EYE) / FC
        k = round(sf * nribs); phk = phi0 + k / nribs * (phi1 - phi0)
        dperp = abs(r * math.sin(ph - phk))
        if dperp < max(0.2, 0.75 * px) * (1.5 - 0.7 * r / edge):                                 # a rib
            c = tone(LIVE, 1.0 + 3.6 * L + (0.8 if (x + y) % 3 == 0 else 0), x, y)
            return haze(c, x, y, Pw)
        fine = abs(r * math.sin(ph - (phk + (0.5 if sf * nribs > k else -0.5) / nribs * (phi1 - phi0))))
        v = 1.0 + 3.2 * L + 1.5 * (r / edge) ** 2 + (wn(1, A * 0.9, B * 0.9) - 0.5) * 0.8
        if fine < max(0.12, 0.5 * px): v -= 0.6                                                  # a finer vein
        c = tone(MEMB, v, x, y)
        c = mix(c, SKYSOFT[y][x], 0.12 + 0.3 * (r / edge) ** 2)                                  # light through it
        return haze(c, x, y, Pw)
    squad(rs, P(-R, -R), P(R, -R), P(-R, R), sh, cls=cls, cut=True)


def rho_swept(rmax, tip=0.32, rmin=3.5, lead=4.0):
    """an outline swept back: rises from rmin at the trailing root to rmax at s=tip, falls to `lead` at the front"""
    def f(s):
        if s < tip: return rmin + (rmax - rmin) * (s / tip) ** 0.75
        return lead + (rmax - lead) * (1 - (s - tip) / (1 - tip)) ** 0.85
    return f


def rho_caudal(rmax):
    """a forked tail fan: two lobes (up and down) and a notch in the middle"""
    def f(s):
        return 5.0 + (rmax - 5.0) * (abs(2 * s - 1) ** 0.7) * (1 - 0.25 * (2 * s - 1) ** 6)
    return f


def build_bladder(rs):
    obj = rs.obj()
    lo = (BC[0] - BL, BC[1] - BRY, BC[2] - BRZ); hi = (BC[0] + BL, BC[1] + BRY, BC[2] + BRZ)
    cast(rs, obj, env_field, ellipsoid_bound(BC, (BL, BRY, BRZ)), screen_box(corners(lo, hi)), env_col, step=0.7)
    # fins at the tail: a big caudal fan, a dorsal sail, a ventral fin, a pair to the sides
    fan_fin(rs, env_point(0.86, 0.0, -0.6), (1, 0, 0), (0, 1, 0), -1.05, 1.05, rho_caudal(23.0), 9, 7)
    fan_fin(rs, env_point(0.42, 0.0, -0.1), (1, 0, 0), (0, 1, 0), 0.2, 1.45, rho_swept(21.0, tip=0.3), 6, 1)
    fan_fin(rs, env_point(0.5, math.pi, -0.1), (1, 0, 0), (0, -1, 0), 0.25, 1.35, rho_swept(12.0, lead=3.0), 5, 2)
    fan_fin(rs, env_point(0.6, -math.pi / 2, -0.1), (1, 0, 0), (0, -0.25, -0.97), 0.15, 1.4, rho_swept(16.0), 5, 3)
    fan_fin(rs, env_point(0.6, math.pi / 2, -0.1), (1, 0, 0), (0, -0.25, 0.97), 0.15, 1.4, rho_swept(16.0), 5, 4)
    # moss dripping off the lower cords (hanging from the net's diagonals), a few strands ending in a glowing bead
    for k in range(400):
        hh = h32(k, 61)
        i = ((hh & 63) % 16) - 8
        a2 = ((hh >> 6) & 1023) / 1023.0 * 16 - 8
        u, th = (i + a2) / (2 * MU), (i - a2) / (2 * MT)
        th = abs(th) if k % 3 else th
        if not (-0.92 < u < 0.82) or not (2.05 < abs(th) < 3.05) or (th < 0 and k % 9): continue
        a = env_point(u, th, 0.01)
        ln = 1.2 + ((hh >> 16) & 31) / 5.5 * (1.0 if k % 4 else 0.45) * (0.5 + wn(1, u * 6, 2.0))
        b = (a[0] + 0.2 * math.sin(k * 1.7), a[1] - ln, a[2] - 0.1)
        sline(rs, a, b, line_sh(LIVE, 1.0 + (k % 3) * 0.45, 3.4), 0.2 if k % 3 else 0.13)
        if k % 13 == 0: glow_disc(rs, s2w(b), 0.22)


# ---------------------------------------------------------------------------------------------------- the gondola
PORTS = (24.0, 28.4, 32.8)
ROOT_CLUMPS = (-20.0, -9.0, -1.0, 9.0, 17.0, 27.0, 35.0)
POD_CLUSTERS = ((-14.0, -7.5, 5), (-4.0, -9.4, 7), (5.0, -10.0, 4), (13.0, -9.2, 6), (22.0, -6.8, 4), (31.0, -4.6, 3))


def hull_col(x, y, p, n, Pw, nw):
    hx_, hy, hz = p
    L = light(nw)
    w = max(0.1, half_w(hx_)); d = depth(hx_)
    px = math.dist(Pw, EYE) / FC
    if hy > BW_TOP - max(0.22, 1.2 * px):                                         # the bulwark's cap, warm wood
        c = tone(DECK, 2.0 + 3.6 * L + (0.8 if (x + 2 * y) % 5 == 0 else 0.0), x, y)
        return haze(c, x, y, Pw), 'prop'
    if hy >= 0: g = hy
    else:
        phi = math.atan2(-hy / d, abs(hz) / w)
        g = -phi * (0.6 * w + 0.4 * d) * 1.1
    k = math.floor(g / 0.5); fk = g / 0.5 - k
    off = (h32(k, 12) % 50) / 10.0
    seg = math.floor((hx_ + off) / 5.5)
    v = 0.6 + 4.8 * L + ((h32(k, seg, 3) % 3) - 1) * 0.3 + (wn(1, hx_ * 0.6, g * 2.5) - 0.5) * 0.6
    if fk < max(0.12, 0.9 * px / 0.5): v -= 1.0                                    # strake seams
    if ((hx_ + off) / 5.5) % 1 < max(0.02, 0.9 * px / 5.5): v -= 0.8               # butt joints
    c = tone(HULL, v, x, y)
    cl = 'wall' if hy > -0.55 * d else 'ceil'
    for (w0, w1) in ((-0.45, 0.3), (-3.9, -3.4)):                                  # the wale at deck level, a rubbing strake
        if w0 < hy < w1:
            c = tone(DECK, 1.0 + 3.6 * L + (0.9 if hy > w1 - max(0.12, 0.7 * px) else -0.6 if hy < w0 + max(0.1, 0.6 * px) else 0.0), x, y)
            return haze(c, x, y, Pw), 'wall'
    if hz < 0 and -2.2 < hy < -0.4:                                                # lit portholes in the stern
        for qx in PORTS:
            dd = math.hypot(hx_ - qx, hy + 1.3)
            if dd < 0.64:
                if dd > 0.44: return haze(tone(BRASS, 1.8 + 3 * L + (1 if hy > -1.3 else 0), x, y), x, y, Pw), 'prop'
                return mix(WARMG, (214, 132, 60), dd / 0.44), 'emit'
    rx_ = hx_ + 0.12 * g + 0.15 * math.sin(g * 0.7)                                 # the living-wood ribs binding it
    fr_ = (rx_ + 1.2) / 5.0 - math.floor((rx_ + 1.2) / 5.0)
    rw = max(0.28, 1.3 * px) / 5.0
    if (fr_ < rw or fr_ > 1 - rw) and g < 0.3:
        lit = fr_ < rw * 0.45
        c = tone(LIVE, 1.0 + 4.0 * L + (1.2 if lit else 0.0) + (wn(1, hx_ * 2, g * 4) - 0.5) * 0.5, x, y)
    elif hy < -0.4:
        if fr_ < rw * 3 or fr_ > 1 - rw * 1.6: c = tone(HULL, v - 0.8, x, y)       # the shade beside a rib
        m = wn(2, hx_ * 0.22, g * 0.5) + (wn(3, hx_ * 1.2, g * 1.6) - 0.5) * 0.35 + clamp(-hy / d - 0.5) * 0.3
        if m > 0.62 and -hy > 0.62 * d:                                            # moss toward the keel
            c = tone(LIVE, 0.9 + 4.0 * L + (wn(0, hx_ * 3, g * 3) - 0.5) * 1.4, x, y)
        for (cx_, cg_, n_) in POD_CLUSTERS:                                       # pods clustered under the keel
            dd0 = math.hypot(hx_ - cx_, (g - cg_) * 1.3)
            if dd0 > 2.6: continue
            for j in range(n_):
                hh = h32(int(cx_ * 10), j, 23)
                ox, og = (((hh & 255) / 255.0) - 0.5) * 3.6, (((hh >> 8) & 255) / 255.0 - 0.5) * 2.4
                rr = 0.2 + ((hh >> 16) & 7) * 0.05 * (1.6 if j == 0 else 1.0)
                dd = math.hypot(hx_ - cx_ - ox, g - cg_ - og)
                if dd < rr:
                    bright = j < 2 or (hh >> 20) % 3 == 0
                    if bright: return (POD[4] if dd < rr * 0.4 else POD[3] if dd < rr * 0.72 else POD[2]), 'emit'
                    return (POD[2] if dd < rr * 0.5 else POD[1]), 'emit'
                if dd < rr * 1.8: c = mix(c, POD[0], 0.35)
    return haze(c, x, y, Pw), cl


def rail_z(x, side): return side * half_w(x) * (1 + 0.012 * 3.6)


def lantern(rs, p, size=0.7):
    """a brass lantern with warm glass, in ship space (its front and underside face the street)"""
    hx_, hy, hz = p; s = size / 2
    frame = BRASS[2]
    def glass(x, y, a, b, z, wp):
        if a < 0.18 or a > 0.82 or b < 0.12 or b > 0.88: return frame
        return WARMG if 0.3 < a < 0.7 else (236, 170, 84)
    squad(rs, (hx_ - s, hy - s * 1.3, hz - s), (hx_ + s, hy - s * 1.3, hz - s), (hx_ - s, hy + s * 1.3, hz - s), glass, cls='emit')
    squad(rs, (hx_ - s, hy - s * 1.3, hz - s), (hx_ + s, hy - s * 1.3, hz - s), (hx_ - s, hy - s * 1.3, hz + s),
          lambda x, y, a, b, z, wp: BRASS[1] if (x + y) % 2 else BRASS[2])
    sline(rs, (hx_, hy + s * 1.3, hz), (hx_, hy + s * 1.3 + 0.35, hz), lambda x, y, a, b, z, wp: BRASS[3], 0.08)


CAB = (17.0, 40.0, 2.4, 8.95, 8.2)            # the cabin on the board (x 17..40, board z 17.4..23.95, 8.2 high)


def build_cabin(rs):
    """the cabin on the far half of the deck: its front (portholes, the door) shows over the near rail"""
    x0, x1, z0, z1, h = CAB
    nf = light(norm(ns2w((0.0, 0.0, -1.0)))); ne = light(norm(ns2w((-1.0, 0.0, 0.0))))
    def planks(L):
        def sh(x, y, s, t, z, wp):
            P = c2w(wp); p = w2s(P)
            v = 1.6 + 4.2 * L + (wn(1, p[0] * 0.6 + p[2], p[1] * 2) - 0.5) * 0.6
            if (p[1] / 0.6) % 1 < 0.12: v -= 0.8
            for qx in (25.0, 29.4, 33.8):
                d = math.hypot(p[0] - qx, p[1] - 5.0)
                if 0.52 < d < 0.75: return haze(tone(BRASS, 2.4 + 2 * L + (1 if p[1] > 5 else 0), x, y), x, y, P)
            if 19.2 < p[0] < 21.8 and p[1] < 6.4:
                v = 1.2 + 4.0 * L + (0.6 if int((p[0] - 19.4) / 0.55) % 2 else 0)
            return haze(tone(DECK, v, x, y), x, y, P)
        return sh
    squad(rs, (x0, 0.0, z0), (x1, 0.0, z0), (x0, h, z0), planks(nf), cls='wall')
    squad(rs, (x0, 0.0, z0), (x0, 0.0, z1), (x0, h, z0), planks(ne), cls='wall')
    for qx in (25.0, 29.4, 33.8):
        Pc = s2c((qx, 5.0, z0 - 0.06))
        rs.disc(Pc[0], Pc[1], Pc[2], 0.52, lambda x, y, s, t, z, wp: WARMG if math.hypot(s, t) < 0.6 else (214, 140, 66), cls='emit')
    roof = line_sh(LIVE, 1.8, 3.6)
    squad(rs, (x0 - 0.5, h, z0 - 0.5), (x1, h, z0 - 0.5), (x0 - 0.5, h + 0.5, z0 - 0.5), roof, cls='prop')
    squad(rs, (x0 - 0.5, h, z0 - 0.5), (x0 - 0.5, h, z1), (x0 - 0.5, h + 0.5, z0 - 0.5), roof, cls='prop')
    for k in range(16):                                                           # moss hanging off the roof's edge
        mx = x0 - 0.3 + k * 1.45 + (h32(k, 3) % 8) / 10.0
        sline(rs, (mx, h, z0 - 0.5), (mx, h - 0.6 - (h32(k, 4) % 12) / 10.0, z0 - 0.5), line_sh(LIVE, 2.0 + (k % 2) * 0.5, 3.4), 0.13)


def build_gondola(rs):
    obj = rs.obj()
    lo = (XB0 - 0.5, -11.2, -9.5); hi = (XB1 + 0.5, BW_TOP + 0.05, 9.5)
    cast(rs, obj, hull_field, box_bound(lo, hi), screen_box(corners(lo, hi)), hull_col, step=0.3)
    build_cabin(rs)
    wood = line_sh(LIVE, 2.0, 4.0)
    kp = [(xk, -depth(xk) + 0.15, 0.0) for xk in range(-16, 40, 2)]                # the living-wood keel
    for a_, b_ in zip(kp, kp[1:]): sline(rs, a_, b_, line_sh(LIVE, 1.0, 3.2, nrm=(0.0, -1.0, -0.4)), 0.55)
    # twisted living-wood balusters and the top rail, both sides, round the bow
    for side in (-1, 1):
        xs = []
        x_ = XB0 + 2.2
        while x_ < XB1 - 1.6:
            xs.append(x_); x_ += 1.25
        for k, bx_ in enumerate(xs):
            z0 = side * half_w(bx_)
            if abs(z0) < 0.8: continue
            wob = 0.18 if k % 2 else -0.18
            sline(rs, (bx_, BW_TOP, z0), (bx_ + wob, 2.8, z0), wood, 0.22)
            sline(rs, (bx_ + wob, 2.8, z0), (bx_, 3.6, z0), wood, 0.22)
        for a_, b_ in zip(xs, xs[1:]):
            sline(rs, (a_, 3.62, rail_z(a_, side)), (b_, 3.62, rail_z(b_, side)), line_sh(DECK, 2.6, 3.4, alt=0.8), 0.32)
    for k in range(70):                                                           # vines trailing over the near rail
        hh = h32(k, 77)
        vx = XB0 + 3 + ((hh & 1023) / 1023.0) * (XB1 - XB0 - 6)
        if wn(1, vx * 0.25, 3.0) < 0.55: continue
        z0 = rail_z(vx, -1) - 0.05
        ln = 1.0 + ((hh >> 10) & 31) / 8.0
        sline(rs, (vx, 3.55, z0), (vx + 0.3, 3.4 - ln, z0 - 0.25), line_sh(LIVE, 1.8 + (k % 3) * 0.5, 3.4), 0.12)
    # the stem rising out of the bow into the fiddlehead curl; the lantern hung from it
    stem = [(xk, -depth(xk) + 0.25, 0.0) for xk in (-16.0, -19.0, -22.0, -24.5, -26.5, -28.0)]   # the cutwater along the prow's keel
    stem += [(-28.6, 0.6, STEM[1] * 0.5), (STEM[0] - 0.4, 3.0, STEM[1]), (STEM[0] - 0.6, 7.0, STEM[1]), (STEM[0] - 0.5, 10.4, STEM[1])]
    for a_, b_ in zip(stem, stem[1:]):
        sline(rs, a_, b_, wood, 0.8)
    cx_, cy_ = STEM[0] + 1.9, 10.8
    prev = (STEM[0] - 0.5, 10.4)
    for i in range(1, 46):
        a = math.pi + i * 0.17; r = 2.5 * (1 - i / 52)
        q = (cx_ + math.cos(a) * r, cy_ - math.sin(a) * r)
        sline(rs, (prev[0], prev[1], STEM[1]), (q[0], q[1], STEM[1]), line_sh(LIVE, 2.6 + (0.6 if i % 4 == 0 else 0), 4.0), 0.7 * (1 - i / 54))
        prev = q
    sline(rs, (STEM[0] - 0.5, 8.4, STEM[1]), (STEM[0] + 0.5, 8.3, STEM[1] - 0.7), lambda x, y, a, b, z, wp: BRASS[2], 0.1)
    lantern(rs, (STEM[0] + 0.5, 7.4, STEM[1] - 0.7))
    # two lantern posts on the near rail
    for lx in (-17.0, 22.0):
        z0 = rail_z(lx, -1)
        sline(rs, (lx, 3.6, z0), (lx, 6.4, z0), wood, 0.2)
        sline(rs, (lx, 6.4, z0), (lx + 0.8, 6.3, z0 - 0.3), lambda x, y, a, b, z, wp: BRASS[2], 0.08)
        lantern(rs, (lx + 0.8, 5.5, z0 - 0.3), 0.55)
    # the rope ladder by the bow (on the board: hooked over the far rail at x -27.1, z +4.6), hanging to the tree
    LX, LZ = -27.1, 4.6
    rope = line_sh(NETC, 1.8, 4.0)
    for dx in (-0.55, 0.55):
        top = (LX + dx, 3.62, LZ)
        pts = [top] + [(LX + dx * (1 + 0.05 * i) + 0.25 * math.sin(i * 0.5), 3.4 - i * 1.3, LZ + 0.6 + 0.05 * i * i) for i in range(1, 11)]
        for a_, b_ in zip(pts, pts[1:]): sline(rs, a_, b_, rope, 0.1)
    for i in range(1, 19):
        yy = 3.0 - i * 0.68
        j = (3.4 - yy) / 1.3
        zz = LZ + 0.6 + 0.05 * j * j; xo = 0.25 * math.sin(j * 0.5)
        sline(rs, (LX - 0.55 * (1 + 0.05 * j) + xo, yy, zz), (LX + 0.55 * (1 + 0.05 * j) + xo, yy, zz), line_sh(DECK, 2.6, 3.2), 0.1)
    # the stanchions: vine-wrapped living wood with glowing pods, carrying the rigging up into the net
    for side in (-1, 1):
        for sx in (-14.0, 8.0):
            sz = side * 8.7
            top = env_point((sx - BC[0]) / BL, side * (math.pi - 0.55), 0.0)
            sline(rs, (sx, BW_TOP, sz), (sx, top[1], sz), line_sh(LIVE, 1.8, 4.2), 0.36)
            for i in range(44):
                y0, y1 = BW_TOP + i * 0.68, BW_TOP + (i + 1) * 0.68
                if y1 > top[1]: break
                a0, a1 = i * 0.9, (i + 1) * 0.9
                sline(rs, (sx + math.cos(a0) * 0.4, y0, sz + math.sin(a0) * 0.3), (sx + math.cos(a1) * 0.4, y1, sz + math.sin(a1) * 0.3),
                      line_sh(LIVE, 2.8 + (i % 2) * 0.5, 3.4), 0.1)
            for (py_, pr) in ((8.6, 0.55), (10.0, 0.38), (13.4, 0.48)):
                if py_ > top[1] - 1: continue
                glow_disc(rs, s2w((sx + 0.55, py_, sz - side * 0.3)), pr)
    # rigging from both rails up to the bladder's lower cords
    for side in (-1, 1):
        for ax_ in ((-22.0, -6.0, 18.0, 31.0) if side > 0 else (-23.0, -2.0, 14.0, 26.0, 36.0)):
            a = (ax_, 3.62, rail_z(ax_, side))
            u = (ax_ * 1.12 - BC[0]) / BL
            b = env_point(max(-0.9, min(0.8, u)), side * (math.pi - 1.05), 0.0)
            sline(rs, a, b, line_sh(NETC, 1.6, 3.6, alt=0.4), 0.09)
    # roots and moss hanging off the keel in clumps, some ending in glowing beads
    for k in range(70):
        hh = h32(k, 91)
        cl_ = ROOT_CLUMPS[hh % len(ROOT_CLUMPS)]
        kx = cl_ + (((hh >> 4) & 255) / 255.0 - 0.5) * 6.0
        if not (XB0 + 2 < kx < XB1 - 2): continue
        d = depth(kx); zz = (((hh >> 12) & 63) / 63.0 - 0.3) * half_w(kx) * 0.8
        yy = -d * max(0.0, 1 - (abs(zz) / max(0.1, half_w(kx))) ** 2.4) ** (1 / 2.6) + 0.1
        ln = 0.5 + (((hh >> 18) & 63) / 63.0) ** 2 * 6.0
        sw = 0.4 * math.sin(k * 2.3)
        q1 = (kx + sw * 0.2, yy - ln * 0.35, zz - 0.1)
        q2 = (kx + sw * 0.7, yy - ln * 0.7, zz - 0.15)
        b = (kx + sw * 0.6 + 0.3 * math.cos(k), yy - ln, zz - 0.2)
        sh = line_sh(TRUNK if k % 4 == 0 else LIVE, 1.0 + (k % 4) * 0.4, 3.0)
        w_ = 0.18 if k % 3 == 0 else 0.11
        sline(rs, (kx, yy, zz), q1, sh, w_); sline(rs, q1, q2, sh, w_ * 0.85); sline(rs, q2, b, sh, w_ * 0.7)
        if k % 9 == 0: glow_disc(rs, s2w(b), 0.2)
    # the fins of the gondola: a sail at the stern, a small one under the keel
    fan_fin(rs, (39.0, 0.6, 0.0), (1, 0, 0), (0, 1, 0), -0.5, 1.25, rho_swept(11.5, tip=0.42, rmin=4.0, lead=3.0), 6, 5)
    fan_fin(rs, (15.0, -4.9, 0.0), (1, 0, 0), (0, -1, 0), 0.25, 1.35, rho_swept(6.5, rmin=2.0, lead=2.0), 4, 6)


LIRIS = os.path.join(REPO, 'assets/images/characters/liris_idle.png')


def build_liris(rs, p=(3.0, 0.0, -8.25)):
    """Captain Liris at the near rail, her redrawn sprite (frame 0) scaled to her size up there and leaned with the
    verticals; the bulwark hides her below the chest"""
    src = Image.open(LIRIS).convert('RGBA').crop((0, 0, 128, 160))
    bb = src.getbbox(); fig = src.crop(bb)
    f0, f1 = sscr(p), sscr((p[0], p[1] + 6.3, p[2]))
    hpx = math.hypot(f1[0] - f0[0], f1[1] - f0[1])
    ang = math.degrees(math.atan2(f1[0] - f0[0], f0[1] - f1[1]))
    w = max(3, round(fig.width * hpx / fig.height))
    small = fig.resize((w, max(4, round(hpx))), Image.BOX)
    if abs(ang) > 2: small = small.rotate(-ang, resample=Image.NEAREST, expand=True)
    px = small.load()
    for j in range(small.height):
        for i in range(small.width):
            c = px[i, j]
            px[i, j] = (c[0], c[1], c[2], 255 if c[3] > 110 else 0)
    Pw = s2w(p); Pc = w2c(Pw)
    hz_ = lambda c, z: mix(c, (110, 150, 132), 0.22)
    rs.sprite(small, Pc[0], Pc[1], Pc[2], tint=hz_, cls='prop')
    return hpx


# ---------------------------------------------------------------------------------------------------- the mycelium tree
def bez(P0, P1, P2, P3, t):
    m = 1 - t
    return tuple(m * m * m * P0[i] + 3 * m * m * t * P1[i] + 3 * m * t * t * P2[i] + t * t * t * P3[i] for i in range(3))


def tube(rs, pts, radii, colf, cls='prop'):
    """a tube along world points (radius per point); colf(x, y, u, across, P_world, n_world) -> colour"""
    obj = rs.obj()
    n_all = len(pts)
    for i in range(n_all - 1):
        A, B = w2c(pts[i]), w2c(pts[i + 1])
        if A[2] <= 0.6 or B[2] <= 0.6: continue
        (ax_, ay_), (bx_, by_) = raster3d.proj(*A), raster3d.proj(*B)
        dl = math.hypot(bx_ - ax_, by_ - ay_) or 1.0
        tx_, ty_ = (bx_ - ax_) / dl, (by_ - ay_) / dl
        steps = int(dl / 0.8) + 1
        for k in range(steps):
            f = k / steps
            C = (A[0] + (B[0] - A[0]) * f, A[1] + (B[1] - A[1]) * f, A[2] + (B[2] - A[2]) * f)
            r = radii[i] + (radii[i + 1] - radii[i]) * f
            u = (i + f) / (n_all - 1)
            sx, sy = raster3d.proj(*C); rr = max(0.6, r * FC / C[2])
            for yy in range(int(sy - rr) - 1, int(sy + rr) + 2):
                if yy < 0 or yy >= H: continue
                for xx in range(int(sx - rr) - 1, int(sx + rr) + 2):
                    if xx < 0 or xx >= W: continue
                    a, b = (xx + 0.5 - sx) / rr, (yy + 0.5 - sy) / rr
                    d2 = a * a + b * b
                    if d2 > 1: continue
                    nz = math.sqrt(1 - d2)
                    z = C[2] - nz * r
                    if z >= rs.ZB[yy][xx]: continue
                    across = -a * ty_ + b * tx_
                    nc = (a, -b, -nz)
                    Pc = (C[0] + a * r, C[1] - b * r, C[2] - nz * r)
                    Pw = c2w(Pc); nw = nc2w(nc)
                    col = colf(xx, yy, u, across, Pw, nw)
                    rs.put(xx, yy, z, const(col), obj, 0.0, 0.0, Pc, nc, cls)


def trunk_col(base=1.4):
    def f(x, y, u, across, Pw, nw):
        L = light(nw)
        v = base + 4.4 * L + (wn(0, u * 140, across * 3) - 0.5) * 0.9
        if abs(across) > 0.72: v -= 0.7                                                  # the strand's turned-away edge
        c = tone(TRUNK, v, x, y)
        if wn(2, u * 50, across * 2) > 0.68: c = mix(c, MYCG[3], 0.3)                  # a faint glow in the fibres
        return haze(c, x, y, Pw)
    return f


def cap(rs, Cw, R, seed):
    """a flat cap of the tree seen from beneath (the growth sprite's caps): gills round a dark stalk, glowing
    toward the pale rim"""
    ng = 22 + seed % 7
    def sh(x, y, s, t, z, wp):
        a, b = 2 * s - 1, 2 * t - 1
        r = math.hypot(a, b); ang = math.atan2(b, a)
        edge = 1 - 0.12 * wn(seed % 4, ang * 2.5 + seed * 3.1, 0.5)
        if r > edge: return None
        if r < 0.14: return TRUNK[3] if (x + y) % 2 else TRUNK[2]
        if r > edge - 0.07: return CAPU[5] if r > edge - 0.035 else CAPU[4]
        gl = abs(((ang / (2 * math.pi)) * ng) % 1 - 0.5)
        k = 0.6 + 2.6 * (r / edge) ** 1.6 + (0.8 if gl < 0.14 else 0.0) + (0.5 if (x + y) % 2 else 0)
        return CAPU[min(4, int(k))]
    wquad(rs, (Cw[0] - R, Cw[1], Cw[2] - R), (Cw[0] + R, Cw[1], Cw[2] - R), (Cw[0] - R, Cw[1], Cw[2] + R), sh, cls='emit', cut=True)


TREE_CROWN_S = (-25.8, -12.5, 1.5)           # where the tree tops out, under the bow (ship space)
TREE_BASE = (-4.2, 1.0, 21.0)                # out of the corpse's crown, below the frame (world)


def build_tree(rs):
    """three strands braided round each other, climbing from the corpse to the bow, caps on short shoots"""
    crown = s2w(TREE_CROWN_S)
    P0 = TREE_BASE
    P1 = (P0[0] - 3.0, P0[1] + 26.0, P0[2] + 18.0)
    P2 = (crown[0] + 9.0, crown[1] - 20.0, crown[2] - 12.0)
    N = 220
    axis = []
    for i in range(N + 1):
        t = i / N
        p = bez(P0, P1, P2, crown, t)
        axis.append((p[0] + math.sin(t * 3.1 * math.pi) * 1.6 * (1 - 0.6 * t), p[1], p[2] + math.cos(t * 3.1 * math.pi) * 1.2))
    R0 = [0.62 * (1 - t / N) ** 1.1 + 0.22 for t in range(N + 1)]
    for k in range(3):
        pts, rad = [], []
        for i, p in enumerate(axis):
            a = i * 0.16 + k * 2 * math.pi / 3
            off = R0[i] * 0.55
            pts.append((p[0] + math.cos(a) * off, p[1] + math.sin(a) * off * 0.3, p[2] + math.sin(a) * off))
            rad.append(R0[i] * 0.52)
        tube(rs, pts, rad, trunk_col(1.3 + 0.3 * k))
    # side shoots ending in caps, bigger toward the crown
    shoots = ((0.5, 1.0, 2.2, 1.5), (0.6, -1.0, 2.4, 1.7), (0.7, 1.0, 2.8, 2.0), (0.78, -1.0, 2.6, 1.9), (0.85, 1.0, 3.0, 2.4),
              (0.91, -1.0, 2.4, 2.2), (0.96, 1.0, 1.8, 2.6))
    for k, (t, side, ln, R) in enumerate(shoots):
        i = int(t * N); p = axis[i]
        d = norm((side * 0.75, 0.9, 0.3 * ((k % 3) - 1)))
        q = (p[0] + d[0] * ln, p[1] + d[1] * ln, p[2] + d[2] * ln)
        m = ((p[0] + q[0]) / 2 + side * 0.2, (p[1] + q[1]) / 2 + 0.3, (p[2] + q[2]) / 2)
        tube(rs, [p, m, q], [R0[i] * 0.38, R0[i] * 0.3, 0.16], trunk_col(1.7))
        cap(rs, (q[0], q[1] + 0.1, q[2]), R, k + 3)
    cap(rs, (crown[0] + 0.3, crown[1] + 0.3, crown[2]), 2.8, 17)
    return crown


# ---------------------------------------------------------------------------------------------------- the street framing the bottom
SHED_X0, SHED_X1, SHED_Z, SHED_Y = -132.0, -38.0, 92.0, 29.0      # Shed 521's front (it faces the junction)
HUT = (-64.0, -45.0, 38.0)                   # the crown hut: x from, x to, its top


def shed_face(x, y, s, t, z, wp):
    """Shed 521 from below: weathered vertical planks, the cross-braced frame and its girts on the front, nail rust,
    a bleached top and damp under the eaves, a missing board here and there"""
    X, Y, Z = c2w(wp)
    side = abs(X - SHED_X1) < 0.05 and Z > SHED_Z + 0.05
    u = Z if side else X
    pl = math.floor(u / 0.9); fu = u / 0.9 - pl
    dist = math.dist((X, Y, Z), EYE); px = dist / FC
    vd = ((X - EYE[0]) / dist, (Y - EYE[1]) / dist, (Z - EYE[2]) / dist)
    foot = px / max(0.15, math.sqrt(max(0.0, 1 - (vd[2] if side else vd[0]) ** 2)))     # world units per pixel along the boards
    L = light((1.0, 0.0, 0.0) if side else (0.0, 0.0, -1.0))
    v = 0.9 + 3.6 * L + (h32(pl, 5) % 3) * 0.3 - 0.7 * (wn(0, u * 0.6, Y * 3.0) - 0.5) + 0.5 * (wn(1, u * 0.15, Y * 0.12) - 0.5)
    if fu < max(0.1, 1.0 * foot / 0.9) and (not side or pl % 2 == 0): v -= 1.2
    if h32(pl, int(Y * 2.3), 9) % 23 == 0: v -= 0.8
    if h32(pl, int(Y / 3.0), 11) % 97 == 0 and not side: return haze(tone(TIMB, 0.2, x, y), x, y, (X, Y, Z), 0.9)   # a missing board
    c = tone(TIMB, v, x, y)
    if not side:
        pu, py = (u - SHED_X0) / 11.0, (Y - 5.0) / 8.0
        fz, fy = pu % 1, py % 1
        bw = max(0.03, 1.1 * px / 10.0)
        bay = h32(math.floor(pu), math.floor(py), 17) % 3                                         # 0: an X, 1: one brace, 2: bare
        br = (abs(fz - fy) < bw * 2.4 and bay < 2) or (abs(fz + fy - 1) < bw * 2.4 and bay == 0)
        if br or fy < bw * 3.2 or fz < bw * 2.6:                                                     # braces, girts, posts
            top_edge = fy < bw * 3.2 and fy > bw * 2.2
            c = tone(TIMB, 2.2 + 3.4 * L + (0.9 if top_edge or fz < bw else 0) + (wn(2, u * 0.5, Y * 0.5) - 0.5) * 0.6, x, y)
            if h32(int(u * 1.5), int(Y * 1.5), 19) % 9 == 0: c = mix(c, tone(RUSTY, 2.4, x, y), 0.6)   # a rusty bolt
        elif 0 < fy - bw * 3.2 < 0.06: c = tone(TIMB, v - 0.9, x, y)                                 # the shadow under a girt
    if Y > SHED_Y - 2.2: c = mix(c, tone(TIMB, v - 1.0, x, y), 0.5 * clamp((Y - SHED_Y + 2.2) / 2.2))  # damp under the eaves
    return haze(c, x, y, (X, Y, Z), 0.9)


def roof_edge(x, y, s, t, z, wp):
    """the eaves' fascia and the corrugated roof edge, rust running off it"""
    X, Y, Z = c2w(wp)
    v = 1.4 + (0.8 if (X * 2.0) % 1 < 0.5 else 0.0)
    c = tone(TIMB, v, x, y)
    if wn(3, X * 0.4, 1.0) > 0.58: c = mix(c, tone(RUSTY, 2.0, x, y), 0.6)
    return haze(c, x, y, (X, Y, Z), 0.9)


VOX_C, VOX_Z, VOX_RO, VOX_RI = (60.0, 12.0), 85.0, 21.0, 17.0


def vox_stucco(x, y, s, t, z, wp):
    """the Voxmarket's arched front from below: the stucco band (rust running from its bolts), the keystone"""
    X, Y, Z = c2w(wp)
    r = math.hypot(X - VOX_C[0], Y - VOX_C[1]); ang = math.atan2(Y - VOX_C[1], X - VOX_C[0])
    if Y >= VOX_C[1] and r > VOX_RO: return None
    if Y >= VOX_C[1] and r < VOX_RI: return None
    v = 2.2 + 1.8 + (wn(0, X * 0.5, Y * 0.5) - 0.5) * 0.9 - 0.8 * clamp((r - VOX_RI) / (VOX_RO - VOX_RI) - 0.6)
    c = tone(STUC, v, x, y)
    if Y >= VOX_C[1]:
        k = round(ang / (math.pi / 14)); ba = k * math.pi / 14                                    # bolts on the band
        bxp, byp = VOX_C[0] + math.cos(ba) * (VOX_RO - 1.1), VOX_C[1] + math.sin(ba) * (VOX_RO - 1.1)
        if math.hypot(X - bxp, Y - byp) < 0.4: return haze(tone(RUSTY, 2.5, x, y), x, y, (X, Y, Z), 0.9)
        if abs(X - bxp) < 0.3 and 0 < byp - Y < 2.5 + 3 * wn(1, bxp, 3.0) and h32(k, 3) % 3: c = mix(c, tone(RUSTY, 3.0, x, y), 0.55)
        if abs(r - VOX_RI) < 0.4: c = tone(STUC, v - 1.4, x, y)
        if abs(ang - math.pi / 2) < 0.07: c = tone(STUC, v + 0.8, x, y)                             # keystone
    if wn(2, X * 0.3, Y * 0.3) > 0.62: c = mix(c, tone(RUSTY, 2.0, x, y), 0.35)                     # rust blooms
    return haze(c, x, y, (X, Y, Z), 0.9)


def vox_glass(x, y, s, t, z, wp):
    """its glazed fan: iron bars, most panes holding the grey sky, a few lit amber from inside"""
    X, Y, Z = c2w(wp)
    r = math.hypot(X - VOX_C[0], Y - VOX_C[1]); ang = math.atan2(Y - VOX_C[1], X - VOX_C[0])
    if Y < VOX_C[1] or r > VOX_RI + 0.4: return None
    px = math.dist((X, Y, Z), EYE) / FC
    mw = max(0.14, 0.6 * px)
    if abs(((ang / (math.pi / 12)) % 1) - 0.5) > 0.5 - mw / max(1.0, r) * 1.8 or min(abs(r - rr) for rr in (5.0, 10.5, 15.0)) < mw or r < 2.0:
        return mix(tone(RUSTY, 0.6, x, y), (34, 40, 38), 0.5)                                       # iron glazing bars
    pane = h32(int(ang / (math.pi / 12)), int(r / 5.0), 4)
    if pane % 3 == 0:                                                                               # the grey sky in the glass
        c = mix(SKYSOFT[y][x], (40, 52, 46), 0.35 + 0.2 * ((pane >> 2) % 2))
        return haze(mix(c, AMBER[1], 0.15), x, y, (X, Y, Z), 0.9)
    c = tone(AMBER, 0.2 + (pane >> 3) % 2 * 0.7 + (wn(1, X * 0.8, Y * 0.8) - 0.5) * 0.8 + 0.5 * clamp(1 - r / VOX_RI), x, y)
    return haze(mix(c, (44, 54, 48), 0.35), x, y, (X, Y, Z), 0.9)                                  # a dim glow from inside


def build_street(rs):
    # Shed 521's front and its flank toward the junction, the eaves, the crown hut with its dark window
    wquad(rs, (SHED_X0, 0.0, SHED_Z), (SHED_X1, 0.0, SHED_Z), (SHED_X0, SHED_Y, SHED_Z), shed_face, cls='wall')
    wquad(rs, (SHED_X1, 0.0, SHED_Z), (SHED_X1, 0.0, SHED_Z + 40), (SHED_X1, SHED_Y, SHED_Z), shed_face, cls='wall')
    wquad(rs, (SHED_X0, SHED_Y, SHED_Z - 0.2), (SHED_X1 + 0.2, SHED_Y, SHED_Z - 0.2), (SHED_X0, SHED_Y + 0.9, SHED_Z - 0.2), roof_edge, cls='prop')
    def hut(x, y, s, t, z, wp):
        X, Y, Z = c2w(wp)
        if HUT[0] + 5 < X < HUT[1] - 5 and SHED_Y + 3.0 < Y < HUT[2] - 1.6:                              # its dark window
            return mix(tone(TIMB, 1.0, x, y), SKYSOFT[y][x], 0.18 if (X * 1.3) % 1 < 0.5 else 0.08)
        return shed_face(x, y, s, t, z, wp)
    wquad(rs, (HUT[0], SHED_Y, SHED_Z + 4.0), (HUT[1], SHED_Y, SHED_Z + 4.0), (HUT[0], HUT[2], SHED_Z + 4.0), hut, cls='wall')
    wquad(rs, (HUT[0] - 0.6, HUT[2], SHED_Z + 3.8), (HUT[1] + 0.6, HUT[2], SHED_Z + 3.8), (HUT[0] - 0.6, HUT[2] + 0.8, SHED_Z + 3.8), roof_edge, cls='prop')
    # the Voxmarket's arch: glass behind, the stucco band in front
    wquad(rs, (VOX_C[0] - VOX_RO, VOX_C[1] - 14, VOX_Z + 0.5), (VOX_C[0] + VOX_RO, VOX_C[1] - 14, VOX_Z + 0.5),
          (VOX_C[0] - VOX_RO, VOX_C[1] + VOX_RO, VOX_Z + 0.5), vox_glass, cls='emit', cut=True)
    wquad(rs, (VOX_C[0] - VOX_RO - 1.5, VOX_C[1] - 14, VOX_Z), (VOX_C[0] + VOX_RO + 1.5, VOX_C[1] - 14, VOX_Z),
          (VOX_C[0] - VOX_RO - 1.5, VOX_C[1] + VOX_RO, VOX_Z), vox_stucco, cls='wall', cut=True)
    # the street's cables, one with a hanging lamp
    cab = line_sh(INK_R, 1.0, 1.0, alt=0.0, ship=False)
    a = (SHED_X1 + 0.2, SHED_Y - 1.5, SHED_Z + 2.0)
    b = (VOX_C[0] + math.cos(math.radians(152)) * 19.0, VOX_C[1] + math.sin(math.radians(152)) * 19.0, VOX_Z - 0.3)
    wline(rs, a, b, cab, 0.08, sag=4.0)
    wline(rs, (SHED_X1 + 0.2, SHED_Y - 4.0, SHED_Z + 14.0), (VOX_C[0] - VOX_RO + 3.0, VOX_C[1] + 7.0, VOX_Z - 0.3), cab, 0.08, sag=5.0)
    f = 0.42
    lamp = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f - 4.0 * math.sin(math.pi * f) - 1.4, a[2] + (b[2] - a[2]) * f)
    wline(rs, (lamp[0], lamp[1] + 1.4, lamp[2]), (lamp[0], lamp[1] + 0.35, lamp[2]), cab, 0.07, segs=2)
    Pc = w2c(lamp)
    rs.disc(Pc[0], Pc[1], Pc[2], 0.4, lambda x, y, s, t, z, wp: AMBER[5] if math.hypot(s, t) < 0.5 else AMBER[3], cls='emit')


INK_R = ramp('#0b100e #121a17 #1a2420')


# ---------------------------------------------------------------------------------------------------- spores in the air
def build_spores(rs):
    """spores drifting down from the ship on the wind (the journal says so): a few motes under the hull"""
    for k in range(9):
        hh = h32(k, 131)
        p = (-26 + ((hh & 1023) / 1023.0) * 58, -14 - ((hh >> 10) & 255) / 255.0 * 16, -12 + ((hh >> 18) & 63) / 63.0 * 8)
        Pw = s2w(p)
        glow_disc(rs, Pw, 0.3 + ((hh >> 24) & 3) * 0.05, core=POD[3], mid=POD[2], rim=mix(POD[1], (110, 150, 130), 0.4))


# ---------------------------------------------------------------------------------------------------- render (world frame for paintpass)
def render(rs, lights=(), **kw):
    col = [[None] * W for _ in range(H)]
    cls = [[None] * W for _ in range(H)]; wpb = [[None] * W for _ in range(H)]
    sid = [[None] * W for _ in range(H)]; zp = [[None] * W for _ in range(H)]; nb = [[None] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            g = rs.G[y][x]
            if g is None:
                col[y][x] = SKYIMG[y][x]; cls[y][x] = 'sky'; continue
            shader, obj, a, b, wp, c = g
            z = rs.ZB[y][x]
            cc = shader(x, y, a, b, z, wp)
            col[y][x] = SKYIMG[y][x] if cc is None else cc
            cls[y][x] = c; sid[y][x] = obj; zp[y][x] = z
            if wp is None: wp = ((x + 0.5 - CX) * z / FC, CAMH - (y + 0.5 - HY) * z / FC, z)
            wpb[y][x] = c2w(wp)
            n = rs.NB[y][x]
            nb[y][x] = nc2w(n) if n is not None else None
    if not FAST:
        col = paintpass.paint(col, cls, zp, wpb, nb, sid, fog=lambda Z: clamp((Z - 15.0) / 220.0, 0.0, 0.5), lights=lights, **kw)
    img = Image.new('RGB', (W, H)); ip = img.load()
    for y in range(H):
        for x in range(W): ip[x, y] = tuple(int(v) for v in col[y][x])
    out = img.copy(); op = out.load()
    for y in range(H - 1):
        for x in range(W - 1):
            g = rs.G[y][x]
            for (nx_, ny_) in ((x + 1, y), (x, y + 1)):
                h_ = rs.G[ny_][nx_]
                if g is None and h_ is None: continue
                if g is None or h_ is None:                       # against the sky: tops catch the overcast, the rest a dark rim
                    fx, fy = (nx_, ny_) if g is None else (x, y)
                    if cls[fy][fx] == 'emit': continue
                    c = ip[fx, fy]
                    if g is None and ny_ == y + 1:
                        s_ = ip[x, y]
                        op[fx, fy] = tuple(int(c[i] * 0.72 + s_[i] * 0.28) for i in range(3))
                        continue
                    k = 0.8 if ny_ == y + 1 else 0.86
                elif h_[1] == g[1]: continue
                else:
                    za, zb = rs.ZB[y][x], rs.ZB[ny_][nx_]
                    if abs(za - zb) < 0.6 + 0.02 * min(za, zb): continue
                    fx, fy = (x, y) if za > zb else (nx_, ny_)
                    if cls[fy][fx] == 'emit': continue
                    c = ip[fx, fy]
                    k = 0.4 if min(za, zb) < 30 else 0.72
                op[fx, fy] = tuple(int(INK[i] * (1 - k) + c[i] * k) for i in range(3))
    return out


def write_gpl(path):
    groups = (('Sky', SKYC), ('Bladder', ENVC), ('Net', NETC), ('Living wood', LIVE), ('Hull', HULL), ('Deck', DECK), ('Spore glow', POD),
              ('Brass', BRASS), ('Membrane', MEMB), ('Tree', TRUNK), ('Mycelium glow', MYCG), ('Shed timber', TIMB),
              ('Stucco', STUC), ('Rust', RUSTY), ('Amber', AMBER))
    out = ['GIMP Palette', 'Name: Skyship look-up (native)', 'Columns: 10', '#']
    for n, r in groups:
        for i, c in enumerate(r): out.append('%3d %3d %3d\t%s %d' % (c[0], c[1], c[2], n, i + 1))
    out.append('%3d %3d %3d\tInk' % INK); out.append('%3d %3d %3d\tLantern' % WARMG)
    open(path, 'w').write('\n'.join(out) + '\n')


def main():
    global SKYIMG, SKYSOFT
    if PLAN:
        plan(); return
    os.makedirs(OUT, exist_ok=True)
    SKYIMG = build_sky()
    SKYSOFT = blur_rows(SKYIMG)
    rs = Raster()
    build_street(rs)
    crown = build_tree(rs)
    build_gondola(rs)
    hpx = build_liris(rs)
    build_bladder(rs)
    build_spores(rs)
    lights = []
    for p in ((STEM[0] + 0.5, 7.4, STEM[1] - 0.7), (-16.2, 5.5, -9.6), (22.8, 5.5, -9.6)):
        Pw = s2w(p); lights.append((Pw[0], Pw[1], Pw[2], (1.0, 0.72, 0.4), 0.5, 7.0))
    for qx in PORTS:
        Pw = s2w((qx, -1.3, -half_w(qx) - 0.5)); lights.append((Pw[0], Pw[1], Pw[2], (1.0, 0.7, 0.38), 0.25, 4.0))
    img = render(rs, lights=lights, light_gain=1.0, grime_gain=0.45, bloom=0.5, stain_gain=0.25, damp_gain=0.15, sheen_gain=0.0)
    img.save(os.path.join(OUT, 'skyship.png'))
    write_gpl(os.path.join(OUT, 'skyship_native.gpl'))
    gd = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gp = gd.load()                     # the guide layer: the message box
    x0, y0, x1, y1 = BOX
    for yy in range(y0, y1 + 1):
        for xx in range(x0, x1 + 1):
            edge = xx in (x0, x0 + 1, x1 - 1, x1) or yy in (y0, y0 + 1, y1 - 1, y1)
            gp[xx, yy] = (127, 255, 142, 255) if edge else (10, 39, 18, 120)
    gd.save(os.path.join(OUT, 'guides.png'))
    print('liris px', round(hpx, 1), 'crown', [round(v) for v in scr(crown)])


if __name__ == '__main__':
    main()
