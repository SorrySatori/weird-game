"""Scraper 1140 (ScraperScene) -- the user's favourite picture, redrawn as native 1 px pixel art, 1067x600, overcast day.

What stays from the old picture (scraper1140_ref.png + the rooftop of scraper_bg.py), only the rendering changes:
the dark monolith of the Nexicorp tower filling the middle, seen from a roof across the gap, SCRAPER 1140 painted big
on its face in cream (a tall condensed letter, drawn here as strokes), the lit amber grate window above the entrance,
the web of heavy sagging cables (from the tower to a wooden power pole on the left and off to the pipe tower on the
right), needle spires and lattice towers fading into the green-grey haze. The rooftop: wet tar with duckboards and
puddles that mirror the tower and its window, the parapet with its railing and a sagging chain, the stair-house on the
left (a caged lamp over its door = the way down to the Crossroad), the gate with a short suspension footbridge hung
with lamps into the haze (= Enter Scraper), and the pipe-tower platform at the right edge (Don Girandole's perch).

Camera: raster3d with the ROOF'S OWN EYE LEVEL, the one of the old picture and its walkway: horizon y 450, eye 4.2
units (chest height; the player is 6.4 tall, feet on y 534 = depth 15, F 300 -- the same scale as every other
background). raster3d / paintpass read their camera from module globals, patched below before anything is drawn.
The tower's face is turned 6 degrees (its right side recedes), which gives the lettering the slope of the original.

    python3 scraper_native_bg.py <outdir>
    -> scraper.png (= assets/images/backgrounds/Scraper1140.png), guides.png (hot spots, walk line), scraper_native.gpl
Fixed points (canvas): the gate centred on x 533 (pylons 497..569, top y ~379) = "Enter Scraper"; the stair-house
door x ~21..78 (sill y ~525) = the exit left; the lettering x ~510..690, y ~92..215 (the observable); the pipe-tower
platform's front rim at y ~379 from x ~965 to the edge (Don Girandole's feet: (1024, 381)); the walk line y 534.
"""
import sys, os, math, random
from PIL import Image, ImageDraw, ImageFilter

import raster3d, paintpass
HZ, EYE = 450, 4.2                                     # the roof's eye level: horizon row 450, eye 4.2 units up
raster3d.HY = HZ; raster3d.CAMH = EYE
paintpass.HY = HZ; paintpass.CAMH = EYE
from raster3d import Raster, proj, W, H, CX, F
from paintpass import paint
from common import h32, make_noise, band, ramp

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
os.makedirs(OUT, exist_ok=True)
rs = Raster()

def clamp(v, a=0.0, b=1.0): return a if v < a else b if v > b else v
def mix(a, b, t): return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t), int(a[2] + (b[2] - a[2]) * t))
def ri(r, i): return r[max(0, min(len(r) - 1, int(i)))]
def tone(r, v, x, y): return ri(r, band(v, x, y))
_NZ = [make_noise(1, 700 + i, 509, 509) for i in range(10)]
def N(i, a, b): return _NZ[i](a + 3000.0, b + 3000.0)              # value noise in WORLD units (period ~509)

# ---------------------------------------------------------------------------------------------------- palette
# sampled from the old picture (sky 100,119,96; haze 79,100,83; tower face 59,76,64; tower darks 23,25,27; letters
# 171,169,126; window 143,81,34) and stretched into ramps
SKYR = ramp('#53655a #586a5c #5d6f5f #627461 #677863 #6c7c65 #718067 #768469 #7b886b #808c6e #85906f')
HAZEC = (104, 120, 96)                                   # the haze everything far dissolves into
TOWR = ramp('#101413 #151a19 #1a201e #1f2723 #252e29 #2b362f #313e35 #37463b #3d4e42 #445648 #4c5e4f #556756 #5e7060')
INKR = ramp('#0a0c0c #0f1212 #141818 #1a1f1f #212726 #29302e #323a37 #3c4541 #47504b #535c55 #606a61')
STEEL = ramp('#111515 #161b1b #1c2222 #232a29 #2b3331 #343c39 #3e4742 #49524c #555e56 #626b62')
WOODG = ramp('#181814 #1f1f1a #272720 #303027 #3a392e #444336 #4f4e3f #5a5948 #666451')
CONC = ramp('#1a1e1c #212624 #282e2b #303632 #393f3a #424842 #4c524b #575d55 #636a60')
CREAM = ramp('#4a4c3d #5f604b #78785b #92916b #a7a57a #b8b588 #c7c396 #d4d0a4')
AMBER = ramp('#3a2414 #5a3418 #82481e #a95f26 #cb7c31 #e29b43 #f0b961 #f8d48a #ffeabf')
RUSTY = ramp('#24120a #3a1d10 #552a16 #6f381d #8a4a26 #a35e33')
def rust_run(u, Y, src, spacing, seed=0, rate=7):
    """rust bleeding down by gravity from a row of seams / bolts at Y = src (+ k * spacing): narrow, sparse runs
    that fade -- 0..1"""
    c = math.floor(u / 0.16)
    hs = h32(c, seed, 91)
    if hs % rate or N(4, u * 0.5 + seed, 2.0) < 0.42: return 0.0
    dv = (src - Y) % spacing if spacing else src - Y
    if dv < 0: return 0.0
    L = 0.35 + ((hs >> 8) % 100) * 0.022
    return (1 - dv / L) ** 1.3 if dv < L else 0.0
def rusted(c, k, x, y):
    return mix(c, tone(RUSTY, 0.8 + k * 1.8, x, y), min(0.6, k * 0.7)) if k > 0.06 else c
TAR = ramp('#0d100f #121615 #171b1a #1c2120 #222826 #29302d #313834 #3a423d #444c46')

# ---------------------------------------------------------------------------------------------------- fixed geometry
ZB = 22.0                     # the parapet (back edge of the roof)
GAP = 2.6                     # half-width of the gap in the railing where the footbridge starts
ZG = 22.3                     # the gate portal
PATH = (13.7, 16.7)           # the duckboards across the roof (the player's feet: z 15)
ZF, XR, ZH = 17.0, -22.5, 20.6        # the stair-house: front face, its right edge, its back
DOOR = (-29.0, -25.8, 7.1)            # its door: x0, x1, height (0.9 x 2 m)
LAMP = (-27.4, 7.75, 16.55)           # the caged lamp over the door
def house_h(z): return 10.2 - (z - ZF) * 0.6           # the stair-house roof slopes down over the stairs
PT = (48.0, 86.0, 33.0, 41.0, 11.2, 12.0)              # the pipe-tower platform: x0, x1, z0, z1, underside, deck

# the tower: a local frame on its face plane, turned YAW about the vertical (the right side recedes)
YAW = math.radians(6.0)
TO = (0.0, 180.0)                                      # (X, Z) where the footbridge meets the face
TT = (math.cos(YAW), math.sin(YAW)); TN = (-math.sin(YAW), math.cos(YAW))
def tw(a, y, d=0.0): return (TO[0] + a * TT[0] + d * TN[0], y, TO[1] + a * TT[1] + d * TN[1])
def tface(a0, a1, y0, y1, d, sh, cls='prop', cut=False):
    """a quad on (or parallel to, d in front < 0) the tower's face; sh(x, y, u, v, z) gets face coords u = a, v = Y"""
    return rs.quad(tw(a0, y0, d), tw(a1, y0, d), tw(a0, y1, d),
                   lambda x, y, s, t, z, wp: sh(x, y, a0 + s * (a1 - a0), y0 + t * (y1 - y0), z), cls=cls, cut=cut)
def tside(a, y0, y1, d0, d1, sh, cls='prop'):
    """a side wall of a protrusion, perpendicular to the face (u = depth)"""
    return rs.quad(tw(a, y0, d0), tw(a, y0, d1), tw(a, y1, d0),
                   lambda x, y, s, t, z, wp: sh(x, y, d0 + s * (d1 - d0), y0 + t * (y1 - y0), z), cls=cls)
def tunder(a0, a1, y, d0, d1, sh, cls='prop'):
    return rs.quad(tw(a0, y, d0), tw(a1, y, d0), tw(a0, y, d1),
                   lambda x, y_, s, t, z, wp: sh(x, y_, a0 + s * (a1 - a0), d0 + t * (d1 - d0), z), cls=cls)

def sky_col(y):
    """the overcast sky without its texture (the haze target at that height)"""
    t = clamp(y / HZ)
    return mix((88, 106, 90), (112, 127, 101), t ** 1.15)
def haze(c, k, y=None):
    return mix(c, HAZEC if y is None else mix(HAZEC, sky_col(y), 0.5), clamp(k))

# ---------------------------------------------------------------------------------------------------- the sky
_cl = make_noise(90, 801, W, H); _cl2 = make_noise(34, 802, W, H); _ml = make_noise(3, 803, W, H)
def sky(x, y, s, t, z, wp):
    """overcast day: a flat, bright sage cover, a little darker overhead; long soft cloud bands (lit tops, darker
    bellies) and the fine painted mottle of the old picture"""
    tt = clamp(y / HZ)
    v = 2.4 + 6.4 * tt ** 1.05
    c1 = _cl(x * 0.45, y * 2.2); c2 = _cl2(x * 0.5, y * 2.8)
    v += (c1 - 0.5) * 2.0 + (c2 - 0.5) * 1.0
    v += 0.7 * clamp((_cl(x * 0.45, (y - 6) * 2.2) - c1) * 8)                 # a cloud's lit upper rim
    v += (_ml(x, y) - 0.5) * 0.9                                               # mottle
    return tone(SKYR, v, x, y)
rs.quad((-20000, 9000, 6000), (20000, 9000, 6000), (-20000, -9000, 6000), sky, cls='sky')

# ---------------------------------------------------------------------------------------------------- the skyline
def tower_spec(rnd, X0, X1, top, kind, z):
    """a city tower as primitives in world X/Y: tiers (setbacks), crown spikes, a needle; or a lattice mast"""
    w = X1 - X0; prims = []
    if kind == 'lattice':
        prims.append(('lat', X0, X1, top))
        prims.append(('needle', (X0 + X1) / 2, top, top + w * rnd.uniform(0.6, 1.4), w * 0.03))
        return prims
    style = rnd.choice(('gothic', 'gothic', 'stepped', 'block', 'twin'))
    nt = {'gothic': rnd.choice((2, 3)), 'stepped': rnd.choice((3, 4)), 'block': 1, 'twin': 1}[style]
    y0 = -2000.0; a, b = X0, X1
    # tier tops: the body takes most of the height, the setbacks are short
    span = top - Ys(500, z)
    fr = [rnd.uniform(0.05, 0.11) * (i + 1) for i in range(nt - 1)]
    tops = sorted([top - span * f for f in fr] + [top])
    for i, ty in enumerate(tops):
        prims.append(('rect', a, b, y0, ty))
        if style != 'block':                                                   # corner pinnacles on each tier
            ph = w * rnd.uniform(0.18, 0.4) * (1.4 if i == len(tops) - 1 else 0.8)
            pw = (b - a) * rnd.uniform(0.05, 0.09)
            prims.append(('spike', a + pw / 2, ty, ty + ph, pw)); prims.append(('spike', b - pw / 2, ty, ty + ph * rnd.uniform(0.7, 1.1), pw))
        ins = (b - a) * rnd.uniform(0.12, 0.2)
        y0 = ty; a, b = a + ins, b - ins
    if style == 'gothic':                                                      # a tall central spire
        sw = (b - a + 2 * ins) * rnd.uniform(0.16, 0.34)
        prims.append(('spike', (X0 + X1) / 2, top, top + w * rnd.uniform(1.0, 2.2), sw))
        prims.append(('needle', (X0 + X1) / 2, top, top + w * rnd.uniform(2.2, 3.0), w * 0.015))
    elif style == 'twin':                                                      # two shafts with a gap
        g_ = w * rnd.uniform(0.12, 0.22)
        prims.append(('cut', (X0 + X1) / 2 - g_ / 2, (X0 + X1) / 2 + g_ / 2, top - w * rnd.uniform(0.8, 1.6), top + 1))
        for cx in (X0 + w * 0.22, X1 - w * 0.22):
            prims.append(('spike', cx, top, top + w * rnd.uniform(0.4, 0.9), w * 0.2))
    elif style in ('block', 'stepped') and rnd.random() < 0.7:
        for k in range(rnd.choice((1, 2, 3))):                                 # aerial masts
            cx = a + (b - a) * rnd.uniform(0.15, 0.85)
            prims.append(('needle', cx, top, top + w * rnd.uniform(0.3, 1.2), w * 0.02))
    if rnd.random() < 0.3:
        cx = (X0 + X1) / 2 + rnd.uniform(-0.15, 0.15) * w
        prims.append(('needle', cx, top, top + w * rnd.uniform(1.4, 2.6), w * 0.02))
    return prims

def skyline_layer(z, kL, specs, seed, dark=(26, 38, 33), detail=1.0):
    """one depth band of towers: one cut quad per tower, inside test against its primitives"""
    px = z / F
    for (X0, X1, top, kind, sd) in specs:
        rnd = random.Random(seed * 1000 + sd)
        prims = tower_spec(rnd, X0, X1, top, kind, z)
        xs = [p[1] for p in prims] + [p[2] if p[0] in ('rect', 'lat') else p[1] for p in prims]
        ymax = max(p[3] if p[0] in ('spike', 'needle') else p[4] if p[0] == 'rect' else p[3] for p in prims)
        bx0, bx1 = min(xs) - 4 * px - max(p[4] if p[0] == 'spike' else 0 for p in prims), max(xs) + 4 * px + max(p[4] if p[0] == 'spike' else 0 for p in prims)
        ribw = rnd.choice((3, 4, 5)) * px
        win = rnd.random() < 0.5
        def sh(x, y, s, t, zz, wp, prims=prims, ribw=ribw, win=win, X0=X0, X1=X1, top=top, sd=sd):
            X, Y = wp[0], wp[1]
            part = None; edge = 0.0; rx = 0.5
            for p in prims:
                k = p[0]
                if k == 'cut':
                    if p[1] <= X <= p[2] and p[3] <= Y <= p[4]: return None
                elif k == 'rect':
                    if p[1] <= X <= p[2] and p[3] <= Y <= p[4]:
                        part = 'body'; rx = (X - p[1]) / max(1e-6, p[2] - p[1])
                        if Y > p[4] - px * 1.1: edge = 1.0                     # the parapet line catches the sky
                        elif X < p[1] + px * 1.1: edge = 0.6                   # the lit left arris
                        break
                elif k == 'spike':
                    _, cx, y0, y1, sw = p
                    if y0 - px <= Y <= y1:
                        hw = max(px * 0.55, sw / 2 * (1 - (Y - y0) / (y1 - y0)) ** 0.9)
                        if abs(X - cx) <= hw: part = 'spike'; rx = 0.5 + (X - cx) / (2 * hw); break
                elif k == 'needle':
                    _, cx, y0, y1, nw = p
                    if y0 - px <= Y <= y1 and abs(X - cx) <= max(px * 0.55, nw): part = 'needle'; break
                elif k == 'lat':
                    _, a, b, ty = p
                    if Y > ty: continue
                    f = clamp((ty - Y) / (ty + 900.0))
                    hw = (b - a) / 2 * (0.12 + 0.88 * f ** 0.6); cx = (a + b) / 2
                    if abs(X - cx) > hw + px * 0.6: continue
                    if abs(abs(X - cx) - hw) < px * 0.9: part = 'leg'; break
                    seg = hw * 1.6
                    q = ((ty - Y) % seg) / seg; ux = (X - cx) / hw
                    if abs(ux - (q * 2 - 1)) < px * 1.3 / hw or abs(ux + (q * 2 - 1)) < px * 1.3 / hw: part = 'brace'; break
                    if (ty - Y) % seg < px * 1.1: part = 'brace'; break
            if part is None: return None
            if part == 'body':
                v = 2.0 - rx * 0.8                                             # soft light from the left
                rb = ((X - X0) / ribw) % 1
                if detail > 0.5: v += 0.55 if rb < 0.3 else (-0.35 if rb > 0.78 else 0)
                if kL < 0.6 and h32(int(X / px), sd, 3) % 7 == 0: v -= 0.7 * clamp((N(5, X * 0.1, Y * 0.02) - 0.3) * 3)   # streaks
                v += edge * 1.4
                if detail > 0.5 and (Y % 9.0) < px * 1.05: v -= 0.5            # floor lines
                if win and detail > 0.5 and h32(int(X / (ribw * 0.5)), int(Y / 9.0), sd) % 11 == 0 and (Y % 9.0) > 3.0: v += 1.3   # a lit/sky-lit pane
                v += (N(3, X * 0.02, Y * 0.012) - 0.5) * 1.0
            elif part == 'spike':
                v = 2.4 - rx * 1.4
            else:
                v = 1.4
            c = mix(dark, (66, 82, 68), clamp(v / 5.5))
            k = kL + (1 - kL) * 0.62 * clamp((90.0 - Y) / (z * 1.25)) ** 0.9  # the bases sink into the mist
            return haze(c, k, y)
        yb = Ys(522, z)                                                    # the parapet hides everything below
        rs.quad((bx0, yb, z), (bx1, yb, z), (bx0, ymax + px * 2, z), sh, cls='prop', cut=True)

def Xs(x, z): return (x - CX) * z / F
def Ys(y, z): return EYE + (HZ - y) * z / F
def layer_specs(z, rnd, x_from, x_to, ytop_lo, ytop_hi, wpx=(30, 70), gap=(-10, 30), lattice=0.12, hero=()):
    specs = list(hero); x = x_from
    while x < x_to:
        wpx_ = rnd.uniform(*wpx)
        yt = rnd.uniform(ytop_lo, ytop_hi)
        kind = 'lattice' if rnd.random() < lattice else 'tower'
        specs.append((Xs(x, z), Xs(x + wpx_, z), Ys(yt, z), kind, len(specs) + 1))
        x += wpx_ + rnd.uniform(*gap)
    return specs

rnd = random.Random(1140)
# the far bands first (they lose the depth test to the nearer ones anyway)
skyline_layer(1500.0, 0.86, layer_specs(1500.0, rnd, -40, 1100, 250, 370, wpx=(24, 60), gap=(-12, 16)), 11)
skyline_layer(900.0, 0.74, layer_specs(900.0, rnd, -40, 1100, 170, 330, wpx=(26, 64), gap=(-8, 26), lattice=0.15), 12)
skyline_layer(540.0, 0.58, layer_specs(540.0, rnd, -30, 1100, 150, 300, wpx=(28, 70), gap=(0, 50), lattice=0.15), 13)
# the near band: the big clusters of the old picture -- left (x 150..230, to y ~110) and right (x 860..1000), the
# thin needle at x ~1040 -- plus a few in between
Z1 = 320.0
hero1 = [(Xs(140, Z1), Xs(232, Z1), Ys(150, Z1), 'tower', 101), (Xs(18, Z1), Xs(96, Z1), Ys(200, Z1), 'tower', 102),
         (Xs(236, Z1), Xs(300, Z1), Ys(262, Z1), 'tower', 103), (Xs(866, Z1), Xs(940, Z1), Ys(178, Z1), 'tower', 104),
         (Xs(944, Z1), Xs(1006, Z1), Ys(214, Z1), 'tower', 105), (Xs(1026, Z1), Xs(1050, Z1), Ys(250, Z1), 'lattice', 106),
         (Xs(770, Z1), Xs(838, Z1), Ys(290, Z1), 'tower', 107), (Xs(300, Z1), Xs(352, Z1), Ys(300, Z1), 'lattice', 108)]
skyline_layer(700.0, 0.62, [(Xs(1034, 700.0), Xs(1046, 700.0), Ys(240, 700.0), 'lattice', 201), (Xs(1037, 700.0), Xs(1043, 700.0), Ys(96, 700.0), 'block', 202)], 15)
skyline_layer(Z1, 0.44, hero1, 14, dark=(22, 33, 29), detail=1.0)

# ---------------------------------------------------------------------------------------------------- the tower
SLAB = (-23.0, 100.0)                         # the lettered face (a range), d = 0
TOPV = 248.0                                  # its top (the crown sits above, out of frame)
WIN = (-13.0, 9.5, 52.0, 96.0)                # the lit grate window: a0, a1, v0, v1
LET_S = (-12.0, 95.0, 186.0, 211.0)           # SCRAPER: a0, a1, v0, v1
LET_N = (17.0, 69.0, 149.5, 180.5)            # 1140

def build_letters():
    """the lettering as a mask in FACE space (4 samples per unit): tall condensed letters drawn as strokes, like the
    old picture's -- uniform stroke, squared curves, a flag on the 1"""
    R = 4
    G = {
        'S': [[(0.92, 0.15), (0.76, 0.04), (0.24, 0.04), (0.08, 0.16), (0.08, 0.36), (0.22, 0.47), (0.78, 0.53), (0.92, 0.64),
               (0.92, 0.85), (0.76, 0.96), (0.24, 0.96), (0.08, 0.85)]],
        'C': [[(0.92, 0.16), (0.76, 0.04), (0.24, 0.04), (0.08, 0.17), (0.08, 0.83), (0.24, 0.96), (0.76, 0.96), (0.92, 0.84)]],
        'R': [[(0.12, 1.0), (0.12, 0.04), (0.72, 0.04), (0.9, 0.15), (0.9, 0.38), (0.72, 0.5), (0.12, 0.5)], [(0.52, 0.5), (0.92, 1.0)]],
        'A': [[(0.06, 1.0), (0.36, 0.04), (0.64, 0.04), (0.94, 1.0)], [(0.2, 0.66), (0.8, 0.66)]],
        'P': [[(0.12, 1.0), (0.12, 0.04), (0.72, 0.04), (0.9, 0.16), (0.9, 0.4), (0.72, 0.53), (0.12, 0.53)]],
        'E': [[(0.9, 0.04), (0.12, 0.04), (0.12, 0.96), (0.9, 0.96)], [(0.12, 0.49), (0.76, 0.49)]],
        '1': [[(0.14, 0.24), (0.52, 0.04), (0.52, 1.0)]],
        '4': [[(0.7, 1.0), (0.7, 0.04), (0.08, 0.7), (0.96, 0.7)]],
        '0': [[(0.26, 0.04), (0.74, 0.04), (0.92, 0.18), (0.92, 0.82), (0.74, 0.96), (0.26, 0.96), (0.08, 0.82), (0.08, 0.18), (0.26, 0.04)]],
    }
    def word(txt, a0, a1, v0, v1, gw=0.62, sp=0.17, stroke=0.15):
        hgt = v1 - v0
        n = len(txt); unit = (a1 - a0) / (n * gw + (n - 1) * sp)              # glyph height scale from the width
        gh = min(hgt, unit)
        wpx, hpx = int((a1 - a0) * R), int(hgt * R)
        im = Image.new('L', (wpx, hpx), 0); d = ImageDraw.Draw(im)
        sw = max(2, int(stroke * gh * R))
        for i, ch in enumerate(txt):
            gx = (i * (gw + sp)) * gh * R
            for stroke_ in G[ch]:
                pts = [(gx + (sw / 2 + (gw * gh * R - sw) * p[0]), sw / 2 + (hpx - sw) * p[1]) for p in stroke_]
                d.line(pts, fill=255, width=sw, joint='curve')
                for p in (pts[0], pts[-1]):                                    # square caps
                    d.rectangle([p[0] - sw / 2, p[1] - sw / 2, p[0] + sw / 2, p[1] + sw / 2], fill=255) if 0 < p[1] < hpx else None
        return im
    return [(LET_S, word('SCRAPER', *LET_S, gw=0.6, sp=0.16, stroke=0.17)), (LET_N, word('1140', *LET_N, gw=0.64, sp=0.22, stroke=0.16))]
LETTERS = build_letters()
def letter_at(u, v):
    """1 inside a stroke, 0.5 within the paint's dark rim, 0 elsewhere"""
    for (a0, a1, v0, v1), im in LETTERS:
        if a0 - 1 <= u <= a1 + 1 and v0 - 1 <= v <= v1 + 1:
            p = im.load(); w_, h_ = im.size
            mx, my = int((u - a0) * 4), int((v1 - v) * 4)
            if 0 <= mx < w_ and 0 <= my < h_ and p[mx, my]: return 1.0
            for (dx, dy) in ((-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2)):
                if 0 <= mx + dx < w_ and 0 <= my + dy < h_ and p[mx + dx, my + dy]: return 0.5
    return 0.0

def wglow(c, u, v, k0=0.55):
    """the grate window's warm light on the tower round it (paintpass's point lights fall off too fast at this size)"""
    du = max(WIN[0] - u, 0.0, u - WIN[1]); dv = max(WIN[2] - v, 0.0, v - WIN[3])
    if dv > 60 or du > 60: return c
    k = k0 * math.exp(-math.hypot(du, dv * 0.8) / 10.0)
    if v < WIN[2]: k *= 1.25                                                  # it falls down onto the bay and the canopy
    return (min(255, int(c[0] + k * 105)), min(255, int(c[1] + k * 52)), min(255, int(c[2] + k * 14)))

def tower_haze(v, x=0, y=0):
    """the tower is near enough to stay dark; its foot sinks into the mist rising from the city below"""
    return 0.08 + 0.58 * clamp((22.0 - v) / 70.0) ** 1.2

def drips(u, v, seed=0, band=13.0):
    """thin dark runs down the face: per ~1 px column a run hangs from one of the bands above, in clusters"""
    c = math.floor(u / 0.62)
    hs = h32(c, seed, 77)
    if hs % 2 or N(4, c * 0.07 + seed, 3.0) < 0.36: return 0.0
    bh = band * (1 + (hs >> 4) % 3)
    top = math.ceil(v / bh) * bh
    L = 4.0 + ((hs >> 8) % 100) * 0.5
    dv = top - v
    if dv > L: return 0.0
    return (1 - dv / L) ** 0.7 * (0.55 + ((hs >> 16) % 5) * 0.12)

# the lettered face has its own ramp: the original's cooler green-grey (44,57,52 .. 61,80,68)
FACER = ramp('#0f1614 #131b18 #17201d #1b2622 #1f2b27 #24312c #293832 #2e3e37 #33453d #394c43 #3f5349 #465a50 #4e6257')
FB, PW, PH = 21.0, 7.0, 7.0                   # floor ledges (~35 px), the concrete panels (3 to a floor)

def _letter_bottoms():
    """per mask column of each word: the lowest painted point (face v) -- where rain picks the paint and dirt up"""
    out = []
    for (a0, a1, v0, v1), im in LETTERS:
        p = im.load(); w_, h_ = im.size; B = []
        for mx in range(w_):
            b = None
            for my in range(h_ - 1, -1, -1):
                if p[mx, my]: b = v1 - (my + 1) / 4.0; break
            B.append(b)
        out.append(((a0, a1, v0, v1), B))
    return out
LETB = _letter_bottoms()
def under_letter(u, v):
    """how far below the nearest painted stroke above (None if no letter above in this column)"""
    best = None
    for (a0, a1, v0, v1), B in LETB:
        if a0 <= u < a1 and v < v1:
            mx = int((u - a0) * 4)
            if 0 <= mx < len(B) and B[mx] is not None and v < B[mx]:
                d_ = B[mx] - v
                if best is None or d_ < best: best = d_
    return best

def vent_at(pu, pv):
    """0 = plain panel, 1 = a vent slot, 2 = a blind window"""
    if pv < 3 or pv > 34: return 0
    k = h32(pu, pv, 23) % 41
    return 1 if k < 2 else 2 if k == 2 else 0
def face_free(u, v):
    """no openings / ledge ends under the lettering, in the window's bay or the cornice"""
    if LET_S[2] - 4 < v < LET_S[3] + 5: return False
    if LET_N[2] - 4 < v < LET_N[3] + 4 and LET_N[0] - 6 < u < LET_N[1] + 6: return False
    if -18.0 < u < 14.5 and v < 110.0: return False
    return v < 240.0

def slab_face(x, y, u, v, z):
    """the lettered face: heavy, dark weathered concrete -- floor ledges with soot and rain running down from them,
    panels set in seams with their own tone (patched, a few pale repairs), vent slots and blind windows, a damp dark
    lower third towards the gate, paint washed down from the letters"""
    px = z / F
    au = u - SLAB[0]
    pu, pv = int(math.floor(au / PW)), int(math.floor(v / PH))
    fu, fv = (au / PW) % 1, (v / PH) % 1
    hp = h32(pu, pv, 51)
    val = 8.1 + ((hp % 7) - 3) * 0.12                                         # each panel its own tone, faintly
    patch = hp % 17 == 0 or (hp % 37 == 7 and fu > 0.35 and fv < 0.7)         # patched: newer, darker, smoother
    repair = hp % 31 == 5                                                      # a pale cement repair
    if patch: val -= 0.9
    elif repair: val += 0.9
    grain = 1.0 if not patch else 0.5
    val += ((N(0, u * 0.03, v * 0.016) - 0.5) * 2.0 + (N(1, u * 0.2, v * 0.09) - 0.5) * 1.5) * grain
    val += (N(2, u * 1.6, v * 1.6) - 0.5) * 1.1 * grain                       # fine pitting
    val -= 2.4 * max(0.0, N(9, u * 0.12, v * 0.05) - 0.5) * 2.6 + 1.4 * max(0.0, N(5, u * 0.35, v * 0.16) - 0.55) * 3.0   # dark weather blotches
    val += 0.5 * clamp((v - 140) / 90.0)                                       # the sky lights the upper face
    val -= 1.8 * clamp((v - 228) / 18.0) * clamp((N(3, u * 0.3, 1) - 0.2) * 3)   # soot under the crown
    # the damp lower third: darker, mottled, a wavy tide line where the wet stops
    damp = clamp((92.0 - v) / 70.0)
    val -= 2.0 * damp + 1.8 * damp * max(0.0, N(7, u * 0.25, v * 0.12) - 0.35) * 2.5
    if damp > 0 and h32(int(math.floor(u / 0.62)), 81) % 4 == 0: val -= 0.9 * damp * clamp((N(8, u * 1.1, v * 0.04) - 0.35) * 3)   # wet runs
    tide = 50.0 + (N(8, u * 0.08, 2.0) - 0.5) * 14.0
    if 0 <= tide - v < px * 1.1: val -= 0.9
    elif 0 <= v - tide < px * 1.1: val += 0.4
    # panel seams (worn away in places), a chipped lower edge under each horizontal one
    if fu < px / PW * 0.95 and (h32(pu, pv, 52) % 5 < 2 or patch): val -= 0.9 if not patch else 1.3
    if fv < px / PH * 0.95 and (h32(pu, pv, 53) % 5 < 3 or patch): val -= 0.8
    elif fv < px / PH * 1.9 and h32(pu, pv, 53) % 5 < 3: val += 0.3
    if (patch or repair) and (fu < px / PW * 1.9 or fu > 1 - px / PW * 1.1 or fv > 1 - px / PH * 1.1): val -= 0.6
    # the floor ledges: lit front, dark underside, a shadow under it, soot and rain hanging from it by gravity
    vb = v % FB; below = FB - vb                                               # height above / distance under a ledge
    ledge = face_free(u, v) or not (-18.0 < u < 14.5 and v < 110.0)
    if ledge and vb < px * 1.05: val += 2.0
    elif ledge and vb < px * 2.1: val += 1.0
    elif ledge and below < px * 2.1: val -= 2.8
    elif ledge and below < px * 6.0: val -= 1.3 * (1 - below / (px * 6.0))
    c = math.floor(u / 0.62); kb = int(math.ceil(v / FB))
    hs = h32(c, kb, 77)
    clus = clamp((N(4, c * 0.06 + kb * 3.1, 3.0) - 0.3) * 2.2)
    if hs % 2 == 0 and clus > 0:                                               # streaks: dark soot or pale lime
        L = 4.0 + ((hs >> 8) % 100) * 0.26 * (1.4 if v < 92 else 1.0)
        if below < L:
            k = (1 - below / L) ** 0.8 * clus
            if (hs >> 4) % 7 == 0: val += 1.0 * k
            else: val -= (1.6 + ((hs >> 16) % 4) * 0.4) * k
    val -= 2.4 * max(0.0, N(6, u * 0.18, kb * 5.0) - 0.36) * math.exp(-below / 9.0)   # broad soot curtains under the ledges
    # vent slots and blind windows (with their own soot runs)
    if face_free(u, v):
        vk = vent_at(pu, pv)
        if vk == 1 and abs(fu - 0.5) < 0.2 and 0.5 < fv < 0.66: return haze(tone(FACER, 1.0, x, y), tower_haze(v), y)
        if vk == 2 and abs(fu - 0.5) < 0.22 and 0.22 < fv < 0.86:
            if fv > 0.86 - px / PH * 1.1: val = 2.6
            else: return haze(tone(FACER, 0.8 + (0.8 if fu < 0.34 else 0), x, y), tower_haze(v), y)
        for (vp, f0) in ((pv, 0.5), (pv + 1, 0.5 + 1.0)):
            vk2 = vent_at(pu, vp)
            if vk2 and face_free(u, vp * PH + PH * 0.5) and abs(fu - 0.5) < 0.12 and h32(c, vp, 79) % 2:
                dd = (vp - pv) * PH + (0.22 if vk2 == 2 else 0.5) * PH - fv * PH
                if 0 < dd < 6.0: val -= 1.4 * (1 - dd / 6.0)
    if u < SLAB[0] + px * 1.6: val += 1.6                                      # the left arris catches the sky
    elif u < SLAB[0] + 3.0: val -= 1.2                                         # in the shaft's shadow
    if u > SLAB[1] - px * 1.6: val -= 1.4
    L_ = letter_at(u, v)
    if L_ >= 1:
        cval = 4.8 - (N(8, u * 0.5, v * 0.5) - 0.5) * 1.2
        cval -= 1.8 * drips(u, v, 5) + 1.0 * clamp((N(9, u * 0.9, v * 0.25) - 0.7) * 4)
        peel = N(3, u * 0.7 + 40, v * 0.7) + (N(2, u * 2.2, v * 2.2) - 0.5) * 0.25
        if peel < (0.87 if v < LET_N[3] + 1 else 0.84):
            return haze(tone(CREAM, cval, x, y), tower_haze(v), y)
        val -= 0.4                                                             # paint gone: the stained base under it
    elif L_ > 0: val -= 1.6                                                    # the letters' dirty rim
    else:
        dl = under_letter(u, v)                                                # rain under the letters
        if dl is not None and dl < 18.0:
            hl = h32(c, 61)
            Lw = 3.0 + ((hl >> 8) % 100) * 0.13
            if hl % 6 == 0 and N(9, u * 0.07, 3.0) > 0.5 and dl < Lw:          # the cream washed down in faint runs
                kw = 0.5 * (1 - dl / Lw) ** 1.2
                cf = tone(FACER, val, x, y)
                return haze(mix(cf, CREAM[2 + (1 if (hl >> 4) % 3 == 0 else 0)], kw), tower_haze(v), y)
            if hl % 5 in (1, 2) and dl < Lw * 0.7: val -= 1.5 * (1 - dl / (Lw * 0.7))   # dirt picked up by the paint
            val -= 0.5 * math.exp(-dl / 4.0)                                   # grime collects just under them
    return haze(wglow(tone(FACER, val, x, y), u, v), tower_haze(v), y)

def dark_mass(seed, lights=()):
    """the service shafts on the tower's left: near-black, channelled, ledges, a few lit portholes"""
    def sh(x, y, u, v, z):
        px = z / F
        val = 1.7 + (N(0, u * 0.05 + seed, v * 0.02) - 0.5) * 1.6 + (N(2, u * 1.4, v * 1.4) - 0.5) * 0.7
        g = math.floor((u + seed) / 2.1); fu = ((u + seed) / 2.1) % 1
        kind = h32(g, int(seed * 10), 5) % 5
        if kind == 0: val += 1.0 - fu * 1.8                                    # a pipe: lit left, dark right
        elif kind == 1: val -= 0.9                                             # a recess
        elif kind == 2 and fu < px / 2.1 * 1.1: val += 1.0                     # a plate's edge
        fb = 14.0; vb = v % fb
        if vb < px * 1.1: val += 1.5
        elif vb < px * 2.3: val -= 1.0
        val -= 1.8 * drips(u, v, seed, 14.0)
        for (lu, lv) in lights:
            if abs(u - lu) < px * 1.1 and abs(v - lv) < px * 1.1:
                return haze(tone(AMBER, 4.6 if abs(u - lu) < px * 0.5 else 3.2, x, y), tower_haze(v) * 0.7, y)
        return haze(tone(TOWR, val, x, y), tower_haze(v), y)
    return sh

def flat(r, v0, dv=0.0, glow=0.0):
    def sh(x, y, u, v, z):
        c = tone(r, v0 + dv * (N(1, u * 0.3, v * 0.3) - 0.5), x, y)
        return haze(wglow(c, u, v, glow) if glow else c, tower_haze(v), y)
    return sh

# the main slab, its crown, the dark shafts on its left, the riser on its right, the wider lower wings
tface(SLAB[0], SLAB[1], -700, TOPV, 0.0, slab_face)
tface(SLAB[0] - 1.5, SLAB[1] + 1.5, TOPV, TOPV + 4.0, -1.6, flat(TOWR, 6.0, 1.0))             # the cornice
tunder(SLAB[0] - 1.5, SLAB[1] + 1.5, TOPV, -1.6, 0.0, flat(TOWR, 1.2))
def crown(x, y, u, v, z):
    px = z / F
    val = 3.4 + (N(1, u * 0.1, v * 0.05) - 0.5) * 1.2
    if (u + 2) % 7.0 < px * 1.6: val += 1.2                                    # tall fins
    elif (u + 2) % 7.0 < px * 3: val -= 1.0
    return haze(tone(TOWR, val, x, y), tower_haze(v), y)
tface(-12.0, 84.0, TOPV + 4.0, 420.0, 7.0, crown)
tface(-22.0, -6.0, TOPV + 4.0, TOPV + 26.0, 2.0, dark_mass(41.0))                         # plant rooms on the crown
tface(72.0, 98.0, TOPV + 4.0, TOPV + 16.0, 1.0, dark_mass(43.0))
for (cu, h_, w_) in ((-12.5, 52, 3.0), (-6.0, 34, 1.6), (78.0, 70, 3.2), (84.0, 40, 2.0), (70.0, 30, 1.4), (92.0, 26, 1.8)):   # finials
    v0 = TOPV + 4.0
    tface(cu - w_, cu + w_, v0, v0 + h_, 5.5,
          lambda x, y, u, v, z, cu=cu, w_=w_, v0=v0, h_=h_: (haze(tone(TOWR, 2.0 + (1.2 if u < cu else 0), x, y), tower_haze(v), y)
                                                          if abs(u - cu) <= max(z / F * 0.6, w_ * (1 - (v - v0) / h_) ** 0.7) else None), cut=True)
# the shafts on the left (stepped forward of the face)
LM1, LM2 = (-56.0, -23.0, -3.0, 300.0), (-98.0, -56.0, -6.0, 150.0)
tface(LM1[0], LM1[1], -700, LM1[3], LM1[2], dark_mass(3.0, lights=((-41.0, 128.0), (-30.0, 77.0), (-47.0, 160.0))))
tside(LM1[1], -700, LM1[3], LM1[2], 0.0, flat(TOWR, 1.4, 1.0))
tface(LM2[0], LM2[1], -700, LM2[3], LM2[2], dark_mass(9.0, lights=((-71.0, 98.0), (-88.0, 64.0))))
tside(LM2[1], -700, LM2[3], LM2[2], LM1[2], flat(TOWR, 1.2, 1.0))
# its top: a stepped plant room, a water tank, aerials and two pinnacles (not a row of spikes)
tface(-94.0, -66.0, LM2[3], LM2[3] + 9.0, LM2[2] + 1.5, dark_mass(31.0, lights=((-80.0, LM2[3] + 4.0),)))
tface(-90.0, -78.0, LM2[3] + 9.0, LM2[3] + 15.0, LM2[2] + 3.0, flat(TOWR, 2.4, 1.0))
tunder(-96.0, -54.0, LM2[3], LM2[2] - 1.0, LM2[2], flat(TOWR, 0.6))
tface(-96.5, -54.0, LM2[3] - 1.0, LM2[3] + 0.4, LM2[2] - 1.0, flat(TOWR, 3.6, 1.0))            # the parapet lip
def tank(x, y, u, v, z):
    n = (u + 62.0) / 4.0
    if abs(n) > 1: return None
    return haze(tone(TOWR, 2.8 - n * 1.6 + (1.0 if (v - LM2[3]) % 3.0 < z / F else 0), x, y), tower_haze(v), y)
tface(-66.0, -58.0, LM2[3] + 2.0, LM2[3] + 13.0, LM2[2] + 0.5, tank, cut=True)
for (cu, h_, w_) in ((-96.0, 26, 1.8), (-55.5, 34, 2.0)):
    tface(cu - w_, cu + w_, LM2[3], LM2[3] + h_, LM2[2] - 0.6,
          lambda x, y, u, v, z, cu=cu, w_=w_, h_=h_: (haze(tone(TOWR, 1.6 + (1.0 if u < cu else 0), x, y), tower_haze(v), y)
                                                     if abs(u - cu) <= max(z / F * 0.6, w_ * (1 - (v - LM2[3]) / h_) ** 0.7) else None), cut=True)
for (cu, h_) in ((-80.0, 64.0), (-71.0, 38.0), (-86.0, 30.0)):                            # aerial masts with crossbars
    tface(cu - 0.5, cu + 0.5, LM2[3], LM2[3] + h_, LM2[2] + 0.8, flat(TOWR, 1.4))
    for k in range(1, int(h_ / 12) + 1):
        tface(cu - 3.0 + k * 0.4, cu + 3.0 - k * 0.4, LM2[3] + k * 11.0, LM2[3] + k * 11.0 + 0.7, LM2[2] + 0.8, flat(TOWR, 1.8))
# boxes, cabinets and a platform stuck to the shafts (seen from below: dark undersides)
for (a0, a1, v0, v1, d) in ((-50.0, -42.0, 150.0, 158.0, -6.0), (-36.0, -28.0, 102.0, 107.0, -5.6), (-54.0, -47.0, 60.0, 68.0, -5.8),
                            (-92.0, -84.0, 116.0, 122.0, -8.6), (-70.0, -62.0, 30.0, 37.0, -9.0), (-44.0, -36.0, 220.0, 226.0, -5.4)):
    tface(a0, a1, v0, v1, d, lambda x, y, u, v, z, a0=a0, a1=a1: haze(tone(TOWR, 2.6 + (1.2 if u < a0 + z / F * 1.2 else 0)
                                                                         - (0.8 if (u - a0) % 1.6 < z / F else 0), x, y), tower_haze(v), y))
    tunder(a0, a1, v0, d, -3.0, flat(TOWR, 0.4))
# ledges / gantries round the shafts (thin slabs, seen from below) with railings
for (v_, a0, a1, d) in ((44.0, -100.0, -23.0, -8.5), (86.0, -100.0, -23.0, -8.0), (126.0, -58.0, -23.0, -5.0), (184.0, -58.0, -23.0, -5.0)):
    tface(a0, a1, v_ - 1.2, v_, d, flat(TOWR, 3.2, 1.0))
    tunder(a0, a1, v_ - 1.2, d, d + 3.0, flat(TOWR, 0.8))
    tface(a0, a1, v_, v_ + 3.4, d + 0.2, lambda x, y, u, v, z, v_=v_: (haze(TOWR[2], tower_haze(v), y)
                                                                       if (v > v_ + 3.4 - z / F * 1.1 or (u % 2.6) < z / F * 0.9) else None), cut=True)
# pipes riding up the shafts
for (pu, pw, d, top) in ((-27.0, 1.8, -3.6, 290.0), (-31.5, 1.2, -3.4, 270.0), (-52.0, 2.2, -6.6, 240.0), (-63.0, 1.4, -6.5, 150.0),
                         (-92.0, 2.4, -6.8, 150.0), (-84.0, 1.0, -6.5, 140.0), (-24.6, 0.5, -3.3, 300.0), (-35.0, 0.7, -3.4, 282.0),
                         (-39.0, 0.45, -3.3, 262.0), (-45.5, 0.9, -3.6, 244.0), (-58.6, 0.6, -6.4, 150.0), (-68.0, 0.8, -6.6, 152.0),
                         (-76.0, 0.5, -6.5, 140.0), (-88.6, 0.7, -6.6, 150.0), (-96.4, 0.6, -6.6, 150.0), (-49.0, 0.5, -3.4, 230.0)):
    def pipe_sh(x, y, u, v, z, pu=pu, pw=pw):
        n = (u - pu) / pw
        val = 2.6 - n * 1.8 + (0.8 if (v % 9.0) < z / F * 1.2 else 0)               # lit on the left, flanges
        return haze(tone(TOWR, val, x, y), tower_haze(v), y)
    tface(pu - pw, pu + pw, -700, top, d, pipe_sh)
def scaffold(a0, a1, top, seg=9.0):
    def sh(x, y, u, v, z):
        px = z / F; w_ = a1 - a0
        if v > top: return None
        fu = (u - a0) / w_; q = (v % seg) / seg
        on = (u - a0 < px * 1.1 or a1 - u < px * 1.1 or v % seg < px * 1.1 or abs(fu - q) < px * 1.2 / w_ or abs(fu - (1 - q)) < px * 1.2 / w_)
        return haze(tone(TOWR, 2.2 + (0.8 if u - a0 < px * 1.1 else 0), x, y), tower_haze(v), y) if on else None
    return sh
tface(-105.0, -98.6, -700, 132.0, -8.0, scaffold(-105.0, -98.6, 132.0), cut=True)          # a scaffold up the shaft's flank
tface(-30.0, -24.0, 190.0, 300.0, -4.2, scaffold(-30.0, -24.0, 300.0, 8.0), cut=True)
# the riser on the right edge and the bracket arm on the left where the cables come in
tface(96.0, 106.0, -700, 214.0, -2.5, dark_mass(17.0, lights=((101.0, 140.0),)))
tside(96.0, -700, 214.0, -2.5, 0.0, flat(TOWR, 1.0))
for (cu, h_, w_) in ((99.0, 24, 1.8), (104.0, 14, 1.2)):
    tface(cu - w_, cu + w_, 214.0, 214.0 + h_, -2.6,
          lambda x, y, u, v, z, cu=cu, w_=w_, h_=h_: (haze(tone(TOWR, 1.8, x, y), tower_haze(v), y)
                                                     if abs(u - cu) <= max(z / F * 0.6, w_ * (1 - (v - 214.0) / h_) ** 0.7) else None), cut=True)
tface(-116.0, -98.0, 140.0, 142.4, -10.0, flat(TOWR, 2.4, 1.0))                          # the arm
tunder(-116.0, -98.0, 140.0, -10.0, -7.0, flat(TOWR, 0.8))
for k in range(4):                                                                       # its brace + insulators
    tface(-115.0 + k * 4.4, -114.0 + k * 4.4, 136.0, 140.0, -10.2, flat(TOWR, 3.6))
tface(-110.0, -98.0, 125.0, 127.0, -9.0, flat(TOWR, 1.4))
def column(a0, a1, seed=0.0):
    def sh(x, y, u, v, z):
        px = z / F
        val = 2.8 + (1.5 if u < a0 + px * 1.1 else 0) - (0.9 if u > a1 - px * 1.1 else 0) + (N(2, u * 2, v * 0.4 + seed) - 0.5) * 0.8
        val -= 1.6 * drips(u, v, int(seed) + 13, 13.0)
        if (v + seed) % 13.0 < px * 1.1: val += 0.9                            # bolted joints
        return haze(wglow(tone(TOWR, val, x, y), u, v, 0.3), tower_haze(v), y)
    return sh
for (a0, a1, top) in ((-16.6, -14.4, 104.0), (11.0, 13.2, 104.0), (19.0, 20.4, 128.0), (28.0, 29.6, 140.0), (37.4, 38.6, 112.0),
                      (46.0, 47.8, 140.0), (56.0, 57.2, 126.0), (65.0, 66.6, 140.0), (75.0, 76.2, 118.0), (84.0, 85.8, 140.0), (93.0, 94.2, 132.0)):
    tface(a0, a1, -700, top, -1.2, column(a0, a1, a0))
    tside(a1, -700, top, -1.2, 0.0, flat(TOWR, 1.0))
for v_ in (13.0, 39.0, 65.0, 91.0, 117.0):                                               # ties between them
    tface(13.2, 94.2, v_ - 0.9, v_, -0.9, column(13.2, 94.2, v_ + 0.5))
    tunder(13.2, 94.2, v_ - 0.9, -0.9, 0.0, flat(TOWR, 0.5))
tface(-17.0, 13.6, 104.0, 106.4, -1.6, column(-17.0, 13.6, 3.0))                         # the window bay's lintel
tunder(-17.0, 13.6, 104.0, -1.6, 0.0, flat(TOWR, 0.5))
# the lower wings (the tower broadens towards its foot)
tface(-136.0, -98.0, -700, 58.0, -4.0, dark_mass(23.0, lights=((-121.0, 12.0), (-110.0, 40.0))))
tface(-137.0, -97.0, 56.6, 58.6, -5.0, flat(TOWR, 3.2, 1.0))
for k in range(5):                                                                       # buttress ribs
    a_ = -134.0 + k * 8.0
    tface(a_, a_ + 1.6, -700, 54.0 - k * 4.0, -5.6, column(a_, a_ + 1.6, k * 3.0))
tface(100.0, 128.0, -700, 92.0, -1.6, dark_mass(29.0, lights=((112.0, 64.0),)))
tface(99.4, 128.6, 90.6, 92.6, -2.4, flat(TOWR, 3.2, 1.0))
tface(108.0, 109.6, 92.0, 126.0, -2.0, flat(TOWR, 1.6))
tface(128.0, 150.0, -700, 40.0, -0.8, dark_mass(37.0))
tface(127.4, 150.6, 38.6, 40.6, -1.6, flat(TOWR, 3.0, 1.0))
tface(-150.0, -136.0, -700, 6.0, -2.0, flat(TOWR, 2.4, 1.2))
# the lit grate window over the entrance (emissive) in its frame, and the entrance at the bridge's end
def window(x, y, u, v, z):
    a0, a1, v0, v1 = WIN
    px = z / F
    fu, fv = (u - a0) / (a1 - a0), (v - v0) / (v1 - v0)
    if u - a0 < px * 2.0 or a1 - u < px * 2.0 or v - v0 < px * 2.0 or v1 - v < px * 2.0: return haze(TOWR[1], 0.1)
    cu, cv = (fu * 5) % 1, (fv * 8) % 1
    if cu < px * 5 / (a1 - a0) * 1.2 or cv < px * 8 / (v1 - v0) * 1.2: return haze(TOWR[2], 0.12)    # the iron grate
    k = h32(int(fu * 5), int(fv * 8), 41)
    g = 4.4 - abs(fu - 0.45) * 2.2 - fv * 1.6 + (0.9 if k % 5 == 0 else 0) + (N(4, u * 0.5, v * 0.5) - 0.5) * 1.2
    if k % 11 == 3: g -= 2.6                                                   # a pane boarded / soot-blind
    if k % 13 == 5 and fv > 0.5: return haze(TOWR[1], 0.12)                    # one missing
    return tone(AMBER, g, x, y)
tface(WIN[0], WIN[1], WIN[2], WIN[3], -0.3, window, cls='emit')
tface(WIN[0] - 2.2, WIN[1] + 2.2, WIN[3], WIN[3] + 2.4, -1.4, flat(TOWR, 4.6, 0.8))       # a hood over it
tunder(WIN[0] - 2.2, WIN[1] + 2.2, WIN[3], -1.4, 0.0, flat(TOWR, 0.6))
tface(WIN[0] - 1.6, WIN[1] + 1.6, WIN[2] - 1.6, WIN[2], -0.9, flat(TOWR, 4.2, 0.8, glow=0.6))       # the sill
def entrance(x, y, u, v, z):
    if abs(u) < 2.8 and v < 7.5: return tone(AMBER, 2.4 + (1 - abs(u) / 2.8) * 1.6 - v * 0.15, x, y)
    return None
tface(-2.8, 2.8, 0.0, 7.5, -0.2, entrance, cls='emit', cut=True)
tface(-5.0, 5.0, 8.0, 9.6, -3.0, flat(TOWR, 4.0, glow=0.5))                               # its canopy
tunder(-5.0, 5.0, 8.0, -3.0, 0.0, flat(TOWR, 0.8))

# ---------------------------------------------------------------------------------------------------- cables
CABLES = []                                                                  # (pts) for 1 px lines, drawn into the G-buffer
def cable(P0, P1, sag, col_fn, thick=1, cls=None, near2=0.0):
    """a sagging cable between two world points, 1 px (or `thick`) wide, clean pixel steps (no doubled corners)"""
    obj = rs.obj()
    def at(t):
        return (P0[0] + (P1[0] - P0[0]) * t, P0[1] + (P1[1] - P0[1]) * t - sag * 4 * t * (1 - t), P0[2] + (P1[2] - P0[2]) * t)
    pts = []; t = 0.0; dt = 1e-3; prev = None
    while t <= 1.0 + 1e-9:                                                    # adaptive steps: < 0.6 px on screen
        P = at(min(1.0, t))
        if P[2] > 0.6:
            sx, sy = proj(*P)
            if prev is not None and math.hypot(sx - prev[0], sy - prev[1]) > 0.6 and dt > 1e-6:
                t -= dt; dt *= 0.5; t += dt; continue
            q = (int(math.floor(sx)), int(math.floor(sy)))
            if not pts or pts[-1][0] != q: pts.append((q, P, min(1.0, t)))
            if prev is not None and math.hypot(sx - prev[0], sy - prev[1]) < 0.2: dt *= 1.6
            prev = (sx, sy)
            if -50 > sx or sx > W + 50 or sy > H + 50 or sy < -400: dt = max(dt, 2e-3)
        if t >= 1.0: break
        t += dt
    keep = []
    for i, (q, P, t) in enumerate(pts):                                       # drop L-corners
        if keep and i < len(pts) - 1:
            p0, p2 = keep[-1][0], pts[i + 1][0]
            if abs(p0[0] - p2[0]) == 1 and abs(p0[1] - p2[1]) == 1: continue
        keep.append((q, P, t))
    for (q, P, t) in keep:
        sh = lambda x, y, s, t_, z, wp, t=t, P=P: col_fn(x, y, t, P)
        for k in range(2 if P[2] < near2 else thick):
            rs.put(q[0], q[1] + k, P[2] - 0.02, sh, obj, t, 0, P, None, cls)
    return obj
def cab_col(base=INKR[1], k=0.0):
    def f(x, y, t, P):
        z = P[2]
        hz = clamp(0.0 if z < 40 else (z - 40) / 520.0) + k
        return mix(base, HAZEC, clamp(hz))
    return f

# ---------------------------------------------------------------------------------------------------- the pole on the left
POLE = (-27.3, 19.8)                                                         # (X, Z): behind the stair-house, on the roof
POLE_TOP = 30.5
ARMS = (29.2, 25.0, 20.8)
def wood_pole(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 2.4 + (1.2 if s < 0.35 else -0.4 if s > 0.75 else 0) + (N(2, X * 4, Y * 0.6) - 0.5) * 1.2
    if h32(int(Y * 1.8), 3) % 9 == 0 and 0.3 < s < 0.7: v -= 1.0              # cracks, bolts
    return mix(tone(WOODG, v, x, y), HAZEC, 0.06)
rs.box(POLE[0] - 0.32, POLE[0] + 0.32, 6.0, POLE_TOP, POLE[1], POLE[1] + 0.6, wood_pole, wood_pole, cls='prop')
for k, ay in enumerate(ARMS):                                                  # crossarms + insulators
    w_ = (3.4, 4.2, 3.0)[k]
    rs.box(POLE[0] - w_, POLE[0] + w_, ay - 0.35, ay, POLE[1] - 0.25, POLE[1] + 0.1, wood_pole, wood_pole, cls='prop')
    for j in range(-2, 3):
        if j == 0: continue
        ix = POLE[0] + j * w_ / 2.4
        rs.box(ix - 0.12, ix + 0.12, ay, ay + 0.45, POLE[1] - 0.2, POLE[1] + 0.05,
               lambda x, y, s, t, z, wp: (96, 110, 98) if t > 0.6 else (52, 62, 58), lambda x, y, s, t, z, wp: (40, 48, 46), cls='prop')
    rs.line3((POLE[0] - w_ * 0.8, ay - 0.3, POLE[1] - 0.2), (POLE[0], ay - 2.2, POLE[1] - 0.2), lambda x, y, s, t, z, wp: WOODG[1], w=0.14)
rs.box(POLE[0] - 0.5, POLE[0] + 0.5, ARMS[2] - 4.6, ARMS[2] - 2.9, POLE[1] - 0.6, POLE[1] - 0.1,          # a transformer pot
       lambda x, y, s, t, z, wp: tone(STEEL, 3.6 - abs(s - 0.4) * 3 + (1.0 if t > 0.85 else 0), x, y), lambda x, y, s, t, z, wp: STEEL[2], cls='prop')

# cables: the pole -> the tower's arm and shafts (their sag shows the weight), more off to the left, the tower's right
ARM = tw(-114.0, 141.0, -10.3)
for k, (ay, j) in enumerate(((ARMS[0], -2), (ARMS[0], 2), (ARMS[1], -1), (ARMS[1], 1), (ARMS[2], -2))):
    w_ = (3.4, 4.2, 3.0)[min(2, (0, 0, 1, 1, 2)[k])]
    P0 = (POLE[0] + j * w_ / 2.4, ay + 0.4, POLE[1])
    tgt = [ARM, tw(-104.0, 126.0, -9.0), tw(-99.0, 86.0, -8.6), tw(-60.0, 182.0, -5.2), tw(-99.0, 44.0, -8.8)][k]
    cable(P0, tgt, (16, 22, 26, 30, 30)[k], cab_col(INKR[2]), near2=120.0)
for (P0, P1, sg) in (((-160.0, 92.0, 80.0), tw(-100.0, 148.0, -6.5), 14.0), ((-130.0, 60.0, 70.0), tw(-98.0, 112.0, -8.0), 18.0),
                     ((-60.0, 120.0, 120.0), tw(-90.0, 160.0, -6.5), 10.0), ((POLE[0] - 2.5, ARMS[0] + 0.4, POLE[1]), (-70.0, 40.0, 28.0), 3.0),
                     ((POLE[0] + 2.5, ARMS[1] + 0.4, POLE[1]), (-60.0, 32.0, 40.0), 4.5), ((-240.0, 150.0, 140.0), tw(-80.0, 220.0, -6.5), 22.0)):
    cable(P0, P1, sg, cab_col(INKR[2]), near2=100.0)
# loops hanging off the tower's left side
for (a0, v0, a1, v1, sg) in ((-114.0, 140.0, -99.0, 118.0, 10.0), (-112.0, 139.0, -98.0, 100.0, 16.0), (-98.0, 86.0, -86.0, 70.0, 8.0),
                             (-58.0, 184.0, -44.0, 172.0, 9.0), (-98.0, 44.0, -80.0, 30.0, 6.0)):
    cable(tw(a0, v0, -9.0), tw(a1, v1, -8.0), sg, cab_col(INKR[1]))
# the right: from the riser to the pipe tower's mast and off the right edge
MAST = (70.0, 25.6, 39.0)
for (v_, sg, tgt) in ((168.0, 26.0, (MAST[0] - 0.4, MAST[1], MAST[2])), (132.0, 20.0, (MAST[0] + 0.4, MAST[1] - 1.8, MAST[2])),
                      (196.0, 34.0, (150.0, 70.0, 90.0)), (110.0, 22.0, (120.0, 40.0, 60.0)), (150.0, 30.0, (220.0, 90.0, 140.0))):
    cable(tw(103.0, v_, -2.7), tgt, sg, cab_col(INKR[2]), near2=120.0)
cable(tw(104.0, 80.0, -2.7), (200.0, 30.0, 110.0), 14.0, cab_col(INKR[2]))

# ---------------------------------------------------------------------------------------------------- the footbridge
BR_END = 178.5
def bfog(z): return clamp((z - 24.0) / 150.0) ** 0.8 * 0.85
def bridge_deck(x, y, s, t, z, wp):
    X, _, Z = wp
    v = 3.0 + (1.0 if abs(X) < 1.2 else 0) - (1.4 if (Z / 0.55) % 1 < 0.9 * Z * Z / (F * EYE) / 0.55 else 0) + (h32(int(Z / 0.55), 5) % 3) * 0.3
    if abs(abs(X) - 2.25) < 0.18: v = 1.2
    return mix(tone(WOODG, v, x, y), HAZEC, bfog(Z))
rs.quad((-2.25, 0.0, ZG), (2.25, 0.0, ZG), (-2.25, 0.0, BR_END), bridge_deck, cls='ground')
rs.quad((-2.25, -0.6, ZG), (2.25, -0.6, ZG), (-2.25, 0.0, ZG), lambda x, y, s, t, z, wp: STEEL[1], cls='prop')
for side in (-1, 1):
    z = ZG + 2.2
    while z < BR_END:                                                        # posts
        rs.box(side * 2.25 - 0.08, side * 2.25 + 0.08, 0.0, 3.6, z, z + 0.16,
               lambda x, y, s, t, zz, wp: mix(INKR[2], HAZEC, bfog(zz)), lambda x, y, s, t, zz, wp: mix(INKR[1], HAZEC, bfog(zz)), cls='prop')
        z += 2.6 + (z - ZG) * 0.03
    cable((side * 2.25, 3.6, ZG + 0.2), (side * 2.25, 3.6, BR_END), 0.0, lambda x, y, t, P: mix(INKR[4], HAZEC, bfog(P[2])))
    cable((side * 2.25, 1.6, ZG + 0.2), (side * 2.25, 1.6, BR_END), 0.0, lambda x, y, t, P: mix(INKR[1], HAZEC, bfog(P[2])))
    # the main cable: from the gate's top down to the handrail and up to the tower's canopy
    cable((side * 2.45, 9.3, ZG + 0.3), (side * 2.6, 26.0, BR_END - 2.0), 15.0, lambda x, y, t, P: mix(INKR[1], HAZEC, bfog(P[2])))
    z = ZG + 3.0
    while z < 120:                                                           # hangers
        t_ = (z - ZG - 0.3) / (BR_END - 2.0 - ZG - 0.3)
        hy = 9.3 + (26.0 - 9.3) * t_ - 15.0 * 4 * t_ * (1 - t_)
        if hy > 3.9:
            cable((side * 2.3, 3.6, z), (side * 2.4, hy, z), 0.0, lambda x, y, t, P: mix(INKR[2], HAZEC, bfog(P[2])))
        z += 3.0
# lamps hung along the bridge, warm, fading into the haze
z = 30.0
while z < 170:
    for side in (-1, 1):
        X = side * 2.25
        k = clamp((z - 30) / 140.0)
        rs.disc(X, 5.4, z, max(0.18, 0.22 * z / 60),
                lambda x, y, s, t, zz, wp, k=k: mix(AMBER[7] if s * s + t * t < 0.3 else AMBER[5], HAZEC, k * 0.55), cls='emit')
        cable((X, 5.6, z), (X, 6.8 if z < 60 else 6.0, z), 0.0, lambda x, y, t, P: mix(INKR[1], HAZEC, bfog(P[2])))
    z *= 1.28

# ---------------------------------------------------------------------------------------------------- the gate (Enter Scraper)
def pylon(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 3.0 + (1.2 if s < 0.3 else -0.6 if s > 0.7 else 0) + (N(2, X * 3, Y * 0.8) - 0.5) * 0.9
    if (Y % 1.3) < 0.13: v += 1.0                                           # riveted bands
    if (Y % 1.3) > 1.17: v -= 0.8
    c = tone(STEEL, v, x, y)
    ln = 0.5 + 2.0 * N(3, X * 6, 3.0)
    c = rusted(c, rust_run(X * 3 + Z, Y, 0.0, 1.3, 4), x, y)              # rust running from the bands
    return c
for side in (-1, 1):
    x0, x1 = (side * 2.2, side * 2.7) if side > 0 else (side * 2.7, side * 2.2)
    rs.box(x0, x1, 0.0, 9.5, ZG, ZG + 0.5, pylon, pylon, cls='prop')
    rs.box(x0 - 0.04, x1 + 0.04, 9.5, 9.85, ZG - 0.05, ZG + 0.55, lambda x, y, s, t, z, wp: STEEL[5], lambda x, y, s, t, z, wp: STEEL[3], cls='prop')
    rs.box((x0 + x1) / 2 - 0.1, (x0 + x1) / 2 + 0.1, 9.85, 10.6, ZG + 0.15, ZG + 0.35, lambda x, y, s, t, z, wp: STEEL[4], lambda x, y, s, t, z, wp: STEEL[2], cls='prop')
    for i in range(5):                                                       # knee braces under the lintel
        fx = side * (2.2 - i * 0.22); fy = 8.6 - i * 0.22
        rs.box(fx - 0.1, fx + 0.1, fy - 0.12, fy + 0.12, ZG, ZG + 0.3, lambda x, y, s, t, z, wp: STEEL[2], lambda x, y, s, t, z, wp: STEEL[1], cls='prop')
    # the gate's lattice leaves, folded open against the pylons
    rs.quad((side * 2.75, 0.4, ZG - 0.1), (side * 3.35, 0.4, ZG - 0.9), (side * 2.75, 7.6, ZG - 0.1),
            lambda x, y, s, t, z, wp: (STEEL[2] if (s < 0.12 or s > 0.88 or t < 0.04 or t > 0.96 or abs(((s * 3 + t * 6) % 1) - 0.5) < 0.1
                                                    or abs(((s * 3 - t * 6) % 1) - 0.5) < 0.1) else None), cls='prop', cut=True)
rs.box(-3.3, 3.3, 8.85, 9.5, ZG - 0.1, ZG + 0.6, pylon, pylon, bottom=lambda x, y, s, t, z, wp: STEEL[0], cls='prop')      # the lintel
# a string of bulbs sagging between the pylons
for i in range(8):
    t_ = (i + 0.5) / 8
    bx = -2.1 + 4.2 * t_; by = 8.55 - 1.35 * 4 * t_ * (1 - t_)
    rs.disc(bx, by - 0.12, ZG - 0.15, 0.1, lambda x, y, s, t, z, wp: AMBER[8] if s * s + t * t < 0.4 else AMBER[6], cls='emit')
cable((-2.2, 8.6, ZG - 0.15), (2.2, 8.6, ZG - 0.15), 1.35, lambda x, y, t, P: INKR[1])

# ---------------------------------------------------------------------------------------------------- the pipe tower (right edge)
x0, x1, z0, z1, yu, yd = PT
def rim(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 3.2 + (1.4 if t > 0.75 else 0) - (0.8 if t < 0.2 else 0) + (N(2, X * 2, 1) - 0.5) * 0.8
    if (X % 1.4) < 0.18 and 0.3 < t < 0.7: v += 1.4                         # rivets
    c = tone(STEEL, v, x, y)
    c = rusted(c, rust_run(X, Y, yd - 0.15, 0, 6, 5), x, y)
    return mix(c, HAZEC, 0.1)
def under(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 1.4 + (1.0 if (X % 3.0) < 0.3 else 0) + (0.8 if (Z % 2.6) < 0.25 else 0) + (N(2, X, Z) - 0.5) * 0.8
    return mix(tone(STEEL, v, x, y), HAZEC, 0.1)
rs.box(x0, x1, yu - 0.5, yd, z0, z1, rim, rim, bottom=under, cls='prop')
for k in range(5):                                                                       # beams under the deck
    bz = z0 + 1.0 + k * 1.6
    rs.box(x0 + 0.5, x1, yu - 1.1, yu - 0.5, bz, bz + 0.35, lambda x, y, s, t, z, wp: mix(STEEL[1], HAZEC, 0.1),
           lambda x, y, s, t, z, wp: STEEL[1], bottom=lambda x, y, s, t, z, wp: mix(STEEL[0], HAZEC, 0.1), cls='prop')
def vcyl(cx, cz, r, y0, y1, sh, n=12, cls='prop'):
    """a vertical cylinder from facets (its camera-facing half); sh(x, y, wp, nx)"""
    for i in range(n):
        a0 = -math.pi / 2 + math.pi * i / n; a1 = -math.pi / 2 + math.pi * (i + 1) / n
        P0 = (cx + r * math.sin(a0), y0, cz - r * math.cos(a0)); P1 = (cx + r * math.sin(a1), y0, cz - r * math.cos(a1))
        nx = math.sin((a0 + a1) / 2)
        rs.quad(P0, P1, (P0[0], y1, P0[2]), lambda x, y, s, t, z, wp, nx=nx: sh(x, y, wp, nx), cls=cls)
def pipe_sh(seed, hoops=4.0):
    def sh(x, y, wp, nx):
        X, Y, Z = wp
        v = 3.2 - nx * 1.4 - abs(nx) ** 3 * 1.6 + (N(2, Y * 0.4, seed) - 0.5) * 0.8
        if (Y + seed) % hoops < 0.28: v += 1.3                                # flanges
        elif (Y + seed) % hoops < 0.4: v -= 1.0
        c = tone(STEEL, v, x, y)
        c = rusted(c, rust_run(nx * 3 + seed, Y, hoops - seed % hoops, hoops, int(seed), 4), x, y)
        return mix(c, HAZEC, 0.1)
    return sh
for (px_, pz_, r_, sd) in ((60.0, z0 + 4.0, 1.5, 1.0), (55.4, z0 + 3.0, 0.55, 2.0), (65.0, z0 + 3.2, 0.7, 3.0), (52.6, z0 + 5.0, 0.4, 4.0),
                           (69.0, z0 + 4.6, 0.5, 5.0), (73.5, z0 + 5.5, 0.45, 6.0)):                 # the pipes it stands on
    vcyl(px_, pz_, r_, -40.0, yu - 0.5, pipe_sh(sd, 3.4 + sd * 0.4))
for (sx_, ex_) in ((49.0, 58.6), (80.0, 61.4), (56.0, 59.0), (74.0, 61.0)):                             # struts
    rs.line3((sx_, yu - 0.6, z0 + 1.2), (ex_, yu - 7.5, z0 + 3.0), lambda x, y, s, t, z, wp: mix(STEEL[1], HAZEC, 0.1), w=0.3)
# a gooseneck pipe through the deck, the railing on its back edge, the mast the cables tie to
for i in range(14):
    a_ = math.pi * i / 13
    P0 = (78.0 + 1.6 - 1.6 * math.cos(a_), yd + 4.0 + 1.6 * math.sin(a_), z1 - 2.0)
    a2 = math.pi * (i + 1) / 13
    P1 = (78.0 + 1.6 - 1.6 * math.cos(a2), yd + 4.0 + 1.6 * math.sin(a2), z1 - 2.0)
    rs.line3(P0, P1, lambda x, y, s, t, z, wp: mix(STEEL[3], HAZEC, 0.12), w=0.7)
rs.line3((78.0, yd, z1 - 2.0), (78.0, yd + 4.0, z1 - 2.0), lambda x, y, s, t, z, wp: mix(STEEL[3], HAZEC, 0.12), w=0.7)
rs.line3((81.2, yd + 4.0, z1 - 2.0), (81.2, yd + 2.6, z1 - 2.0), lambda x, y, s, t, z, wp: mix(STEEL[2], HAZEC, 0.12), w=0.7)
for k in range(9):
    px_ = x0 + 1.0 + k * 4.4
    rs.box(px_ - 0.1, px_ + 0.1, yd, yd + 3.4, z1 - 0.5, z1 - 0.3, lambda x, y, s, t, z, wp: mix(INKR[2], HAZEC, 0.1),
           lambda x, y, s, t, z, wp: INKR[1], cls='prop')
cable((x0, yd + 3.4, z1 - 0.4), (x1, yd + 3.4, z1 - 0.4), 0.0, lambda x, y, t, P: mix(INKR[4], HAZEC, 0.1))
cable((x0, yd + 1.8, z1 - 0.4), (x1, yd + 1.8, z1 - 0.4), 0.0, lambda x, y, t, P: mix(INKR[1], HAZEC, 0.1))
rs.box(MAST[0] - 0.22, MAST[0] + 0.22, yd, MAST[1] + 1.0, MAST[2], MAST[2] + 0.4, lambda x, y, s, t, z, wp: mix(tone(STEEL, 2.4 + (1 if s < 0.4 else 0), x, y), HAZEC, 0.1),
       lambda x, y, s, t, z, wp: STEEL[1], cls='prop')
rs.box(MAST[0] - 2.4, MAST[0] + 2.4, MAST[1] - 0.3, MAST[1], MAST[2] - 0.2, MAST[2] + 0.2, lambda x, y, s, t, z, wp: mix(STEEL[3], HAZEC, 0.1),
       lambda x, y, s, t, z, wp: STEEL[1], cls='prop')

# ---------------------------------------------------------------------------------------------------- the roof
def _pud(x, y, w, h):
    """a puddle given on the canvas (centre, width, height in px) -> world (X, Z, rx, rz)"""
    Z = F * EYE / (y - HZ)
    return ((x - CX) * Z / F, Z, w / 2 * Z / F, h / 2 * F * EYE / (y - HZ) ** 2)
PUDDLES = [_pud(533, 566, 104, 40),                                           # the big one: the tower and its window in it
           _pud(170, 578, 150, 20), _pud(338, 549, 96, 13), _pud(64, 558, 70, 10), _pud(770, 570, 170, 22),
           _pud(960, 591, 130, 14), _pud(890, 549, 84, 10), _pud(640, 588, 60, 8), _pud(410, 594, 90, 9),
           _pud(300, 516, 86, 6), _pud(708, 519, 130, 7), _pud(880, 513, 60, 5), _pud(160, 512, 40, 4)]
def puddle(X, Z):
    best = 0.0
    for (px_, pz, rx, rz) in PUDDLES:
        d = ((X - px_) / rx) ** 2 + ((Z - pz) / rz) ** 2 + (N(6, X * 1.1, Z * 1.6) - 0.5) * 0.7
        if d < 1.0: best = max(best, clamp((1.0 - d) * 5))
    return best
SEAMS = (9.6, 12.1, 18.4, 20.7)
PATCHES = [(-21.0, -15.5, 9.2, 10.8), (4.0, 8.5, 19.6, 21.0), (22.0, 28.0, 11.4, 13.0), (-6.0, -2.6, 17.6, 19.4)]
def walk(X, Z):
    if PATH[0] <= Z <= PATH[1]: return 'path'
    if abs(X) < 2.25 and PATH[1] < Z < ZB + 0.4: return 'gate'
    if DOOR[0] - 0.4 <= X <= DOOR[1] + 0.4 and PATH[1] < Z < ZF: return 'door'
    return None
def roof(x, y, s, t, z, wp):
    X, _, Z = wp
    px = Z / F
    v = 4.3 + (N(0, X * 0.25, Z * 0.6) - 0.5) * 1.4 + (N(1, X * 2.2, Z * 2.2) - 0.5) * 0.7
    for sz in SEAMS:                                                          # lapped bitumen seams
        dz = Z - sz
        if 0 <= dz < px * Z / EYE * 0.9: v -= 1.3
        elif -px * Z / EYE * 1.2 < dz < 0: v += 0.8
    for (a, b, c_, d) in PATCHES:                                             # repair patches
        if a <= X <= b and c_ <= Z <= d:
            v -= 0.5
            if min(X - a, b - X) < px * 1.1 or min(Z - c_, d - Z) < px * Z / EYE * 1.1: v -= 1.0
    hg = h32(int(X * 9), int(Z * 9), 3) % 41
    if hg == 0: v += 1.8                                                      # gravel caught in the tar
    elif hg == 1: v -= 1.2
    return tone(TAR, v, x, y)
rs.quad((-80.0, 0.0, 5.0), (90.0, 0.0, 5.0), (-80.0, 0.0, ZB), roof, cls='ground')
# the duckboards (a hair above the tar; their front edges cast the contact shadow)
def boards(kind):
    def sh(x, y, s, t, z, wp):
        X, _, Z = wp
        px = Z / F
        if kind == 'path':
            k = math.floor(X / 0.95); fu = X / 0.95 - k
            v = 4.0 + (h32(k, 11) % 4) * 0.3 + (N(2, k * 3.1, Z * 2) - 0.5) * 0.9
            if fu < px / 0.95 * 1.1: v = 1.0                                   # the gaps
            if abs(Z - PATH[0]) < px * Z / EYE or abs(Z - PATH[1]) < px * Z / EYE * 1.2: v -= 1.2
            v += 0.9 * math.exp(-((Z - 15.2) / 0.9) ** 2)                     # worn pale where everyone walks
            if h32(k, 13) % 19 == 0 and Z < 15.0: v = 1.4                      # a missing board
        else:
            k = math.floor(Z / 0.55); fz = Z / 0.55 - k
            v = 3.8 + (h32(k, 17) % 3) * 0.3 + (N(2, X * 2, k * 3.3) - 0.5) * 0.8
            if fz < px * Z / EYE / 0.55 * 1.1: v = 1.0
            if abs(abs(X) - 2.25) < px * 1.1: v -= 1.0
        return tone(WOODG, v, x, y)
    return sh
rs.quad((-80.0, 0.12, PATH[0]), (90.0, 0.12, PATH[0]), (-80.0, 0.12, PATH[1]), boards('path'), cls='ground')
rs.quad((-80.0, 0.0, PATH[0]), (90.0, 0.0, PATH[0]), (-80.0, 0.12, PATH[0]), lambda x, y, s, t, z, wp: WOODG[1], cls='ground')
rs.quad((-2.25, 0.12, PATH[1]), (2.25, 0.12, PATH[1]), (-2.25, 0.12, ZB + 0.4), boards('gate'), cls='ground')
rs.quad((DOOR[0] - 0.4, 0.12, PATH[1]), (DOOR[1] + 0.4, 0.12, PATH[1]), (DOOR[0] - 0.4, 0.12, ZF), boards('gate'), cls='ground')

# ---------------------------------------------------------------------------------------------------- the parapet + railing
def parapet(x, y, s, t, z, wp):
    X, Y, Z = wp
    row = math.floor(Y / 0.35); off = (row % 2) * 0.45
    fu = ((X + off) / 0.9) % 1; fv = (Y / 0.35) % 1
    v = 3.2 + (h32(math.floor((X + off) / 0.9), row, 5) % 4) * 0.3 + (N(2, X * 0.6, Y) - 0.5) * 1.0
    if fu < 0.9 * Z / F / 0.9 or fv < 0.9 * Z / F / 0.35: v -= 1.1             # block joints
    return tone(CONC, v, x, y)
def coping(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 6.0 + (N(2, X * 0.8, 1.0) - 0.5) * 1.4 - (1.2 if (X % 2.4) < Z / F * 1.1 else 0)
    return tone(CONC, v, x, y)
def coping_front(x, y, s, t, z, wp):
    return tone(CONC, 4.4 + (N(2, wp[0] * 0.8, 2.0) - 0.5), x, y)
for (a, b) in ((XR, -GAP), (GAP, 90.0)):
    rs.box(a, b, 0.0, 0.9, ZB, ZB + 0.8, parapet, parapet, cls='wall')
    rs.box(a - 0.05, b + 0.05, 0.9, 1.15, ZB - 0.12, ZB + 0.9, coping_front, coping_front, top=coping, cls='prop')
def steel_dark(v0):
    def sh(x, y, s, t, z, wp):
        c = tone(STEEL, v0 + (1.0 if s < 0.4 else 0), x, y)
        if N(4, wp[0] * 4, wp[1] * 2) > 0.8: c = mix(c, RUSTY[2], 0.5)
        return c
    return sh
posts = []
for side in (-1, 1):
    X = GAP + 0.2
    while X < 70:
        if side < 0 and -X < XR + 0.3: break
        posts.append(side * X); X += 2.9 + (h32(int(X * 10), side) % 5 - 2) * 0.1
posts.sort()
for X in posts:
    lean = 0.25 if h32(int(X * 10), 7) % 9 == 0 else 0.0                     # the odd bent post
    rs.box(X - 0.07, X + 0.07, 1.15, 3.4, ZB + 0.25, ZB + 0.4, steel_dark(2.2), steel_dark(1.6), cls='prop')
    if lean: rs.line3((X, 2.6, ZB + 0.3), (X + lean, 3.4, ZB + 0.3), lambda x, y, s, t, z, wp: STEEL[2], w=0.12)
for side in (-1, 1):
    a = side * (GAP + 0.2); b = 70.0 if side > 0 else XR + 0.3
    cable((a, 3.42, ZB + 0.32), (b, 3.42, ZB + 0.32), 0.0, lambda x, y, t, P: STEEL[5] if (x * 7 + y) % 9 else STEEL[3], thick=2, cls='prop')
for p, q in zip(posts, posts[1:]):
    if p < 0 < q: continue
    cable((p, 2.35, ZB + 0.3), (q, 2.35, ZB + 0.3), 0.32, lambda x, y, t, P: STEEL[1] if int(x) % 3 else STEEL[4], cls='prop')

# roof clutter by the railing: two drums, a turbine vent, a crate, a low vent box
def drum(X, Z, r=0.95, h_=2.6, seed=0):
    def sh(x, y, s, t, z, wp):
        n = s * 2 - 1
        v = 3.6 - n * 1.6 - abs(n) ** 3 * 1.4 + (N(2, s * 9 + seed, t * 3) - 0.5) * 0.8
        if abs(t - 0.2) < 0.03 or abs(t - 0.55) < 0.03 or abs(t - 0.9) < 0.03: v += 1.2
        c = tone(STEEL, v, x, y)
        if N(4, s * 6 + seed, t * 2.5) > 0.66: c = mix(c, tone(RUSTY, 0.8 + (1 - abs(n)) * 1.6, x, y), 0.4)
        c = rusted(c, rust_run(s * 6 + seed, t * 2.6, 2.6 * 0.9, 2.6 * 0.35, 9, 6), x, y)
        return c
    rs.quad((X - r, 0.0, Z), (X + r, 0.0, Z), (X - r, h_, Z), sh, cls='prop')
    rs.quad((X - r, h_, Z - r), (X + r, h_, Z - r), (X - r, h_, Z + r),
            lambda x, y, s, t, z, wp: (tone(STEEL, 4.2 - (1.6 if (2 * s - 1) ** 2 + (2 * t - 1) ** 2 > 0.8 else 0)
                                             + (1.0 if abs(s - 0.75) < 0.06 and abs(t - 0.5) < 0.1 else 0), x, y)
                                       if (2 * s - 1) ** 2 + (2 * t - 1) ** 2 < 1 else None), cls='prop', cut=True)
drum(17.4, 20.6, seed=1); drum(19.6, 21.0, seed=2); drum(18.5, 19.5, r=0.9, h_=2.4, seed=3)
def vent(X, Z, r=1.0):
    def body(x, y, s, t, z, wp):
        n = s * 2 - 1
        return tone(STEEL, 3.4 - n * 1.6 + (1.0 if t > 0.92 else 0), x, y)
    rs.quad((X - r * 0.7, 0.0, Z), (X + r * 0.7, 0.0, Z), (X - r * 0.7, 1.6, Z), body, cls='prop')
    def dome(x, y, s, t, z, wp):
        n = s * 2 - 1; hh = t
        if n * n + (hh * 1.0) ** 2 > 1: return None
        v = 3.8 - n * 1.6 + hh * 1.2
        if ((math.asin(clamp(n / max(0.05, math.sqrt(max(0.0, 1 - hh * hh))), -1, 1)) * 4.5) % 1) < 0.35: v -= 1.4    # the vanes
        c = tone(STEEL, v, x, y)
        return mix(c, tone(RUSTY, 1.6 + hh, x, y), 0.55) if N(4, s * 7, t * 7) > 0.72 else c
    rs.quad((X - r, 1.6, Z), (X + r, 1.6, Z), (X - r, 1.6 + r * 1.1, Z), dome, cls='prop', cut=True)
vent(11.6, 21.0)
def crate(X0, X1, Y1, Z0, seed):
    def front(x, y, s, t, z, wp):
        if s < 0.07 or s > 0.93 or t < 0.08 or t > 0.92: return tone(WOODG, 4.6, x, y)
        if abs(s - t) < 0.06: return tone(WOODG, 4.2, x, y)
        return tone(WOODG, 2.6 + (h32(int(s * 4), seed) % 3) * 0.3 - (0.9 if (s * 4) % 1 < 0.1 else 0), x, y)
    rs.box(X0, X1, 0.0, Y1, Z0, Z0 + (X1 - X0), front, front, top=lambda x, y, s, t, z, wp: tone(WOODG, 4.4 - (0.9 if (s * 4) % 1 < 0.12 else 0), x, y), cls='prop')
crate(25.6, 27.8, 2.0, 20.0, 5); crate(26.0, 27.4, 3.3, 20.3, 6)
rs.box(-16.0, -12.6, 0.0, 1.5, 20.2, 21.6, lambda x, y, s, t, z, wp: tone(STEEL, 3.0 + (1.2 if t > 0.85 else 0) - (0.8 if (s * 8) % 1 < 0.15 and t < 0.8 else 0), x, y),
       lambda x, y, s, t, z, wp: tone(STEEL, 2.2, x, y), top=lambda x, y, s, t, z, wp: tone(STEEL, 4.6, x, y), cls='prop')       # a louvred vent box

# ---------------------------------------------------------------------------------------------------- the stair-house
def panel_steel(side):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = Z * 1.3 if side else X
        v = 3.0 + (0.6 if side else 0) + (N(0, u * 0.4, Y * 0.3) - 0.5) * 1.2 + (N(2, u * 3, Y * 3) - 0.5) * 0.5
        s_ = (u + 40) % 1.6
        if s_ < Z / F * 1.1: v -= 1.3                                         # panel seams
        elif s_ < Z / F * 2.2: v += 0.6
        elif abs(s_ - 0.8) < 0.07 and (Y * 3) % 1 < 0.25: v += 1.2            # rivets
        if abs(Y - 4.0) < 0.14 or abs(Y - 8.0) < 0.14: v += 1.2               # the bands
        elif abs(Y - 3.84) < 0.08 or abs(Y - 7.84) < 0.08: v -= 1.0
        if N(3, u * 3, Y * 3) > 0.8 and Y > 2: v += 0.8                       # dents catching the sky
        c = tone(STEEL, v, x, y)
        ln = 0.6 + 2.2 * N(5, u * 2, 3.0)                                     # rust running down from the rivets and bands
        if Y < 8.1: c = rusted(c, rust_run(u, Y, 7.86, 4.0, 11 + side), x, y)
        return c
    return sh
def house_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    D0, D1, DH = DOOR
    if D0 <= X <= D1 and Y <= DH:                                             # the door: frame, steel leaf, a barred vent
        if X < D0 + 0.22 or X > D1 - 0.22 or Y > DH - 0.25: return tone(STEEL, 1.2 + (1.4 if X < D0 + 0.08 else 0), x, y)
        v = 2.4 + (0.6 if abs(((X - D0) % 1.4) - 0.7) < 0.08 else 0) + (N(2, X * 3, Y * 2) - 0.5) * 0.8
        if 4.7 < Y < 5.8 and D0 + 0.7 < X < D1 - 0.7:
            return tone(STEEL, 0.6, x, y) if int((X - D0) * 7) % 2 else mix(tone(AMBER, 1.0, x, y), STEEL[1], 0.35)
        if abs(X - (D1 - 0.55)) < 0.12 and abs(Y - 3.3) < 0.16: return tone(STEEL, 6.0, x, y)
        if Y < 0.6: v -= 0.8
        c = tone(STEEL, v, x, y)
        if Y < 2.6: c = mix(c, tone(RUSTY, 1.0 + Y * 0.4, x, y), 0.45 * clamp((N(4, X * 5, Y * 0.6) - 0.6) * 4))
        return c
    if -25.0 <= X <= -23.6 and 3.4 <= Y <= 5.0:                               # a fuse box
        return tone(STEEL, 3.6 + (1.4 if Y > 4.85 else 0) - (1.0 if X > -23.75 else 0), x, y)
    if abs(X + 24.3) < 0.09 and Y > 5.0: return STEEL[1]                      # its conduit
    if abs(X - (XR - 0.45)) < 0.16: return tone(STEEL, 1.6 + (1.2 if int(Y * 2.5) % 5 == 0 else 0), x, y)   # drainpipe
    return panel_steel(0)(x, y, s, t, z, wp)
rs.quad((-60.0, 0.0, ZF), (XR, 0.0, ZF), (-60.0, house_h(ZF), ZF), house_front, cls='wall')
def house_side(x, y, s, t, z, wp):
    X, Y, Z = wp
    if Y > house_h(Z): return None
    if 19.9 < Z < 20.4 and 7.4 < Y < 8.6:                                     # a small barred window up the stairs
        return STEEL[0] if (int(Z * 9) % 2 == 0 or Y > 8.45) else mix(tone(AMBER, 0.8, x, y), STEEL[1], 0.4)
    if 18.9 < Z < 19.8:                                                       # the iron ladder up to the roof
        if abs(Z - 19.0) < 0.07 or abs(Z - 19.7) < 0.07: return STEEL[1]
        if (Y * 3.2) % 1 < 0.25: return STEEL[1]
    return panel_steel(1)(x, y, s, t, z, wp)
rs.quad((XR, 0.0, ZF), (XR, 0.0, ZH), (XR, 10.4, ZF), house_side, cls='wall', cut=True)
rs.quad((-60.0, house_h(ZF) - 0.05, ZF - 0.12), (XR + 0.12, house_h(ZF) - 0.05, ZF - 0.12), (-60.0, house_h(ZF) + 0.3, ZF - 0.12),
        lambda x, y, s, t, z, wp: tone(STEEL, 4.8 if t > 0.5 else 1.2, x, y), cls='prop')                     # the roof's lip
# the awning over the door (seen from under), its brackets; the caged lamp
rs.quad((DOOR[0] - 0.7, 8.2, ZF), (DOOR[1] + 0.7, 8.2, ZF), (DOOR[0] - 0.7, 7.9, ZF - 1.3),
        lambda x, y, s, t, z, wp: tone(STEEL, 1.6 + (0.8 if (wp[0] * 4) % 1 < 0.4 else 0), x, y), cls='prop')
rs.quad((DOOR[0] - 0.7, 7.9, ZF - 1.3), (DOOR[1] + 0.7, 7.9, ZF - 1.3), (DOOR[0] - 0.7, 7.7, ZF - 1.3),
        lambda x, y, s, t, z, wp: mix(tone(STEEL, 2.6, x, y), RUSTY[2], 0.35), cls='prop')
rs.line3((LAMP[0], 7.55, ZF), (LAMP[0], 7.55, LAMP[2] - 0.05), lambda x, y, s, t, z, wp: STEEL[1], w=0.1)
def lamp(x, y, s, t, z, wp):
    """the glass globe in its cage (t = 0 at the bottom)"""
    u = (s - 0.5) * 2; v = (t - 0.55) / 0.45
    if u * u + v * v > 1: return None
    if abs(u) < 0.14 or abs(abs(u) - 0.62) < 0.13 or abs(v + 0.2) < 0.12: return STEEL[1]      # the cage wires
    return AMBER[8] if u * u + (v + 0.1) ** 2 < 0.22 else AMBER[6] if u * u + v * v < 0.6 else AMBER[4]
rs.quad((LAMP[0] - 0.34, LAMP[1] - 0.9, LAMP[2]), (LAMP[0] + 0.34, LAMP[1] - 0.9, LAMP[2]), (LAMP[0] - 0.34, LAMP[1] - 0.15, LAMP[2]), lamp, cls='emit', cut=True)
rs.quad((LAMP[0] - 0.22, LAMP[1] - 0.16, LAMP[2] - 0.05), (LAMP[0] + 0.22, LAMP[1] - 0.16, LAMP[2] - 0.05), (LAMP[0] - 0.46, LAMP[1] + 0.05, LAMP[2] - 0.05),
        lambda x, y, s, t, z, wp: STEEL[3] if t > 0.6 else STEEL[1], cls='prop')                                  # the hood
rs.box(LAMP[0] - 0.08, LAMP[0] + 0.08, LAMP[1] - 1.05, LAMP[1] - 0.9, LAMP[2] - 0.05, LAMP[2] + 0.05, lambda x, y, s, t, z, wp: STEEL[2], lambda x, y, s, t, z, wp: STEEL[1], cls='prop')
# a railing on its roof and a vent stack
for k in range(6):
    X = -38.0 + k * 3.1
    if X > XR: break
    rs.box(X - 0.08, X + 0.08, house_h(18.0), house_h(18.0) + 3.0, 18.0, 18.15, steel_dark(2.0), steel_dark(1.4), cls='prop')
cable((-40.0, house_h(18.0) + 3.0, 18.05), (XR + 0.3, house_h(18.0) + 3.0, 18.05), 0.0, lambda x, y, t, P: STEEL[4], cls='prop')
cable((-40.0, house_h(18.0) + 1.6, 18.05), (XR + 0.3, house_h(18.0) + 1.6, 18.05), 0.0, lambda x, y, t, P: STEEL[1], cls='prop')
rs.box(-36.6, -35.4, house_h(19.0), house_h(19.0) + 3.6, 19.0, 19.8, steel_dark(2.4), steel_dark(1.6), cls='prop')
rs.box(-36.9, -35.1, house_h(19.0) + 3.6, house_h(19.0) + 4.0, 18.9, 19.9, lambda x, y, s, t, z, wp: STEEL[4], lambda x, y, s, t, z, wp: STEEL[2], cls='prop')
cable((POLE[0] - 1.0, ARMS[2] + 0.4, POLE[1]), (-33.0, house_h(18.5) + 0.2, 18.6), 1.0, cab_col(INKR[1]))          # the drop to the house

# the clad heating pipe across the near left: a cylinder of facets, lit from the sky above
def hcyl(x0, x1, cy, cz, r, sh, n=10, cls='prop'):
    for i in range(n):
        a0 = math.pi / 2 - math.pi * i / n; a1 = math.pi / 2 - math.pi * (i + 1) / n
        P0 = (x0, cy + r * math.sin(a0), cz - r * math.cos(a0)); P1 = (x1, P0[1], P0[2])
        P3 = (x0, cy + r * math.sin(a1), cz - r * math.cos(a1))
        ny = math.sin((a0 + a1) / 2)
        rs.quad(P0, P1, P3, lambda x, y, s, t, z, wp, ny=ny: sh(x, y, wp, ny), cls=cls)
def clad(x, y, wp, ny):
    X, Y, Z = wp
    v = 3.6 + ny * 2.6 + (N(2, X * 0.8, 1) - 0.5) * 0.8
    if ny > 0.85: v += 0.8                                                    # the sky's sheen along its top
    if (X % 2.2) < 0.09: v -= 1.8                                             # the cladding's laps
    elif (X % 2.2) < 0.17: v += 0.9
    if -21.0 < X < -19.4 and ny > -0.3: return tone(WOODG, 1.6 + (N(3, X * 8, Y * 6) - 0.5) * 2, x, y)   # torn: the lagging shows
    return tone(STEEL, v, x, y)
hcyl(-60.0, -11.0, 0.62, 9.1, 0.42, clad)
for X in (-30.0, -18.0):
    rs.box(X - 0.12, X + 0.12, 0.0, 0.3, 9.0, 9.3, lambda x, y, s, t, z, wp: STEEL[1], lambda x, y, s, t, z, wp: STEEL[0], cls='prop')
def clad_v(x, y, wp, nx):
    v = 4.0 - nx * 1.2 - abs(nx) ** 3 * 1.8 + (N(2, wp[1] * 2, 3) - 0.5) * 0.6
    if (wp[1] % 0.5) < 0.05: v -= 1.4
    return tone(STEEL, v, x, y)
vcyl(-10.9, 9.1, 0.44, 0.0, 1.04, clad_v, n=10)                                       # its elbow down into the roof
rs.quad((-11.34, 1.04, 8.66), (-10.46, 1.04, 8.66), (-11.34, 1.04, 9.54),
        lambda x, y, s, t, z, wp: (tone(STEEL, 5.6 - t * 1.4, x, y) if (2 * s - 1) ** 2 + (2 * t - 1) ** 2 < 1 else None), cls='prop', cut=True)
rs.box(-10.0, -9.2, 0.0, 0.18, 8.7, 9.5, lambda x, y, s, t, z, wp: STEEL[1], lambda x, y, s, t, z, wp: STEEL[0],
       top=lambda x, y, s, t, z, wp: tone(STEEL, 2.4, x, y), cls='prop')                                     # its foot plate

# odds and ends on the roof: a drain grate, a coil of old cable, a dropped plank
def grate(x, y, s, t, z, wp):
    if s < 0.08 or s > 0.92 or t < 0.08 or t > 0.92: return tone(STEEL, 3.4, x, y)
    return tone(STEEL, 0.6, x, y) if (s * 7) % 1 < 0.45 else tone(STEEL, 2.8, x, y)
rs.quad((5.2, 0.02, 11.6), (6.6, 0.02, 11.6), (5.2, 0.02, 12.4), grate, cls='prop')
for k in range(5):                                                                   # the coil: loops of cable lying flat
    r_ = 0.62 - k * 0.07; cx_, cz_ = -14.6 + k * 0.03, 10.4
    pts = [(cx_ + r_ * math.cos(a_ * math.pi / 14), 0.06 + k * 0.035, cz_ + r_ * 0.8 * math.sin(a_ * math.pi / 14)) for a_ in range(29)]
    for P0, P1 in zip(pts, pts[1:]):
        rs.line3(P0, P1, lambda x, y, s, t, z, wp: INKR[3] if (x + y) % 3 else INKR[5], w=0.09, cls='prop')
rs.line3((-14.0, 0.06, 10.6), (-12.2, 0.04, 11.6), lambda x, y, s, t, z, wp: INKR[3], w=0.09, sag=-0.1, cls='prop')
rs.box(15.0, 18.6, 0.0, 0.16, 12.2, 12.75, lambda x, y, s, t, z, wp: tone(WOODG, 2.4, x, y), lambda x, y, s, t, z, wp: WOODG[1],
       top=lambda x, y, s, t, z, wp: tone(WOODG, 4.0 + (N(2, wp[0] * 3, 1) - 0.5) * 1.6 - (1.2 if (wp[0] * 2.2) % 1 < 0.08 else 0), x, y), cls='prop')

# ---------------------------------------------------------------------------------------------------- render
LIGHTS = [(LAMP[0], LAMP[1] - 0.6, LAMP[2] - 0.6, (1.0, 0.72, 0.38), 0.9, 7.5),
          (0.0, 7.8, ZG - 0.6, (1.0, 0.76, 0.42), 0.45, 5.0),
          (tw((WIN[0] + WIN[1]) / 2, (WIN[2] + WIN[3]) / 2, -9.0)[0], (WIN[2] + WIN[3]) / 2, tw(0, 0, -9.0)[2], (1.0, 0.64, 0.3), 22.0, 44.0),
          (0.0, 6.0, BR_END - 6.0, (1.0, 0.66, 0.32), 4.0, 14.0)]
def pfog(z):
    if z is None: return 1.0
    return min(0.9, 0.62 * clamp((z - 30.0) / 100.0) + 0.28 * clamp((z - 130.0) / 600.0))

def wet_reflect(col):
    """wet roof: puddles mirror the scene sharply (the tower, its window, the railing), the tar film dully. The
    mirrored ray climbs its screen column; it hits the first surface that is nearer than the ray at that row."""
    REF = {}
    for y in range(HZ + 1, H):
        for x in range(W):
            g = rs.G[y][x]
            if g is None or g[5] != 'ground' or g[4] is None: continue
            X, Y, Z = g[4]
            if Z > ZB + 0.5: continue                                         # the footbridge's planks
            k = puddle(X, Z)
            film = 0.0 if walk(X, Z) else 0.22 + 0.3 * clamp((N(7, X * 0.3, Z * 0.7) - 0.38) * 3)
            if walk(X, Z): film = 0.06
            if k <= 0 and film <= 0: continue
            d = y + 0.5 - HZ
            rip = int(round((N(8, X * 2.0, Z * 7.0) - 0.5) * 1.6)) if k > 0 else 0
            hit = None
            yy = y - 1
            lim = max(0, int(HZ - d) + 1)
            while yy >= lim:
                t = 2 * d / ((yy + 0.5 - HZ) + d)
                Zr = Z * t
                gg = rs.G[yy][x]
                if gg is not None and gg[5] != 'ground' and rs.ZB[yy][x] <= Zr * 1.005 + 0.2:
                    hit = col[max(0, min(H - 1, yy + rip))][x]; break
                yy -= 1
            if hit is None: hit = col[max(0, int(HZ - d))][x]
            REF[(x, y)] = (hit, k, film)
    # the film reflects a softened image
    im = Image.new('RGB', (W, H)); ip = im.load()
    for (x, y), (c, k, f) in REF.items(): ip[x, y] = c
    bl = im.filter(ImageFilter.BoxBlur(2)).load()
    for (x, y), (c, k, f) in REF.items():
        b = col[y][x]
        if k > 0:
            kk = 0.82 * k
            rc = mix(mix(c, sky_col(2 * HZ - y), 0.22), (10, 14, 14), 0.1)
            col[y][x] = mix(b, rc, kk)
            if k < 0.35: col[y][x] = mix(col[y][x], (20, 26, 25), 0.4)      # the dark wet rim of the puddle
        else:
            rc = mix(mix(bl[x, y], sky_col(2 * HZ - y), 0.3), (14, 18, 18), 0.12)
            col[y][x] = mix(b, rc, f)

def render(ink=(8, 10, 10)):
    """raster3d's render with our own wet roof and depth outlines only on the near things (far edges stay soft in the
    haze, cables and spires stay 1 px)"""
    G, ZBuf = rs.G, rs.ZB
    col = [[ink] * W for _ in range(H)]
    cls = [[None] * W for _ in range(H)]; wpb = [[None] * W for _ in range(H)]; sid = [[None] * W for _ in range(H)]
    zp = [[None] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            g = G[y][x]
            if g is None: continue
            shader, obj, a, b, wp, c = g
            cc = shader(x, y, a, b, ZBuf[y][x], wp)
            col[y][x] = ink if cc is None else cc
            cls[y][x] = c; wpb[y][x] = wp; sid[y][x] = obj; zp[y][x] = ZBuf[y][x]
    wet_reflect(col)
    col = paint(col, cls, zp, wpb, rs.NB, sid, fog=pfog, lights=LIGHTS, light_gain=1.0, grime_gain=1.1, bloom=0.4,
                stain_gain=0.8, damp_gain=0.3, sheen_gain=0.6)
    img = Image.new('RGB', (W, H)); ip = img.load()
    for y in range(H):
        for x in range(W): ip[x, y] = col[y][x]
    out = img.copy(); op = out.load()
    for y in range(H - 1):
        for x in range(W - 1):
            g = G[y][x]
            if g is None or g[5] is None: continue
            for (nx_, ny_) in ((x + 1, y), (x, y + 1)):
                h_ = G[ny_][nx_]
                if h_ is None or h_[1] == g[1] or h_[5] is None: continue
                za, zb = ZBuf[y][x], ZBuf[ny_][nx_]
                if min(za, zb) > 60 or abs(za - zb) < 0.6 + 0.02 * min(za, zb): continue
                fx, fy = (x, y) if za > zb else (nx_, ny_)
                c = ip[fx, fy]
                op[fx, fy] = mix(ink, c, 0.35)
    return out

img = render()
img.save(f'{OUT}/scraper.png')

# ---------------------------------------------------------------------------------------------------- guides + palette
g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
KX = W / 800
def gbox(x, y, w, h, col, label):
    x, w = round(x * KX), round(w * KX)
    d.rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], outline=col)
    d.text((x - w / 2 + 2, y - h / 2 - 12), label, fill=col)
gbox(400, 470, 100 / KX, 200, (90, 220, 255), 'VSTUP -> Scraper (brana)')
gbox(50, 470, 80, 200, (90, 220, 255), 'EXIT -> krizovatka (dvere)')
gbox(750, 470, 80, 200, (90, 220, 255), 'EXIT -> Burning Bear St')
gbox(447, 160, 200, 170, (255, 210, 60), 'POZOROVANI: SCRAPER 1140')
d.rectangle([1024 - 67, 381 - 168, 1024 + 67, 381], outline=(255, 120, 200)); d.text((960, 200), 'DON (dev)', fill=(255, 120, 200))
for x in range(0, W, 8): d.line([(x, 534), (x + 4, 534)], fill=(255, 80, 80))
d.text((4, 536), 'cara nohou y534 (hrac 128px)', fill=(255, 80, 80))
for x in range(0, W, 8): d.line([(x, HZ), (x + 4, HZ)], fill=(200, 200, 90))
d.text((4, HZ - 12), 'horizont strechy y450 (oko 4.2)', fill=(200, 200, 90))
g.save(f'{OUT}/guides.png')

q = img.quantize(colors=96, method=Image.Quantize.MEDIANCUT)
pal = q.getpalette()[:96 * 3]
cols = sorted({tuple(pal[i:i + 3]) for i in range(0, len(pal), 3)}, key=lambda c: (0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]))
with open(f'{OUT}/scraper_native.gpl', 'w') as f:
    f.write('GIMP Palette\nName: Scraper 1140 native\nColumns: 12\n#\n')
    for c in cols: f.write('%3d %3d %3d\tScraper\n' % c)
print('done scraper', f'{OUT}/scraper.png')
for nm, P in (('gate L', (-2.7, 9.5, ZG)), ('gate R', (2.7, 0, ZG)), ('door L', (DOOR[0], 0, ZF)), ('door R', (DOOR[1], DOOR[2], ZF)),
              ('rim L', (x0, yd, z0)), ('win', tw(WIN[0], WIN[3])), ('win2', tw(WIN[1], WIN[2])),
              ('SCRAPER tl', tw(LET_S[0], LET_S[3])), ('SCRAPER br', tw(LET_S[1], LET_S[2])), ('1140 bl', tw(LET_N[0], LET_N[2])), ('1140 br', tw(LET_N[1], LET_N[2]))):
    print(nm, tuple(round(v) for v in proj(*P)))
