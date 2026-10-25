"""The entrance of the Egg Cathedral (CathedralEntrance), 1067x600: the user's composition (cathedral_ref.png, painted
2026-10-18) rebuilt on the shared rasteriser so the stone reads like the other backgrounds -- coursed ashlar with
mortar joints and weathered blocks, real recesses, light and grime (paintpass). Seen almost straight on through a
long lens (F 1200), like the user's frontal drawing.
  the portal   a pointed arch in two stepped orders and a hood mould between buttress piers with pinnacles, under a
               crocketed gable (a triangular light, a blind arcade, trefoil spandrels, a finial); plank doors with
               iron straps; the tympanum's glowing glass is the user's pattern
  the nave     the wall above: the big stained-glass window (the user's glass, kept pixel for pixel) between two
               shafts, the stepped frame with the red fillet behind the gable
  the towers   two round sandstone towers: plinth, string courses, a lit lancet, a corbelled cornice, a slate spire
               with a louvre and a finial
  the aisles   brown rubble walls with the user's stained-glass lancets and a dark bay under an arch, the grey
               corner buttresses with string courses
  the shell    the halves of the hatched egg at both edges (the user's silhouette and holes), crystals in the right
  the parvis   worn flagstones, three steps up to the door
Fixed points: the guard stands on the second step (feet y 508), the walk line is y 534, the glowing tympanum spans
y ~240-312 (the examine hotspot), the door is centred.
    python3 cathedral_bg.py <outdir>   ->  cathedral.png"""
import sys, os, math, colorsys
from PIL import Image
import raster3d, paintpass
raster3d.F = paintpass.F = 1200.0                    # a long lens: the facade at ~70 units, frontal like the drawing
import shedkit
shedkit.fog_of = lambda z: 0.0
from shedkit import Raster, proj, wn, tone, mix, LEAF
from common import h32, ramp
from pal_day import INK

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
F, CX, HY, CAMH = raster3d.F, raster3d.CX, raster3d.HY, raster3d.CAMH
REF = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cathedral_ref.png')).convert('RGB')
RP = REF.load()
def X_(x, Z): return (x - CX) * Z / F                 # a canvas x at depth Z -> world X
def Y_(y, Z): return CAMH + (HY - y) * Z / F          # a canvas y at depth Z -> world Y

# the user's colours, stretched into ramps
GREY = ramp('#141211 #1f1c1b #2e2b2a #3d3a38 #4d4947 #5e5a58 #74706b #8a837c #a39c94 #b8aea2')
SAND = ramp('#2a211b #3a2c24 #4a3d34 #5a4a3e #66574a #766553 #857463 #958470 #a5937d #b6a48b #c7b69c')
RUBBLE = ramp('#140f0c #1a1310 #2a1f19 #3a2c24 #4a3d34 #574638 #66574a #766553 #857463')
SLATE = ramp('#121317 #1c1d22 #26282e #31343b #3d4149 #4a4f58 #5a606a')
OAK = ramp('#1a0f09 #2e1a10 #3e2214 #4a2a17 #5a331c #6b3f22 #7d4c2a')
IRON = ramp('#0e0c0b #1c1916 #2a2520 #3a332b #4e4536')
BRASS = ramp('#3b2c14 #6e5523 #a8862f #e0c25a #f2dc86')
EGG = ramp('#3d3a38 #4d4947 #5e5a58 #74706b #8a837c #a39c94 #b8aea2 #cdc3b5 #ddd3c4 #ece4d6 #f4eee2')
REDT = ramp('#2e080c #4a0e15 #6e1420 #8a2230')
GLOWC = ramp('#6e5523 #a8862f #c9a440 #e0c25a #f2dc86 #fff3c0')
CRYST = ramp('#1c0f2a #2e1846 #4a2a6e #6e44a0 #a07ad0 #d8c4f0')
VOID = (11, 8, 7)

# depths (front faces) and the portal's arches
ZD, Z1, Z2, ZP, ZPIER = 70.5, 70.0, 69.5, 69.0, 68.2      # door, order 1, order 2, porch front (gable), piers
ZN, ZT, RT, ZW, ZO, ZE = 72.5, 71.5, 3.3, 74.0, 72.0, 68.8  # nave wall, tower axis + radius, aisles, buttresses, shell
YS = 11.2                                                  # the springing line of the portal arches
W0, W1, W2, WH = 4.75, 5.5, 6.25, 6.55                     # half-widths: door, order 1, order 2, hood mould
AC, AE = 0.88, 0.25                                        # arch aspect, point
GBASE, GAPEX, GHALF = 11.5, 23.0, 8.6                      # the gable: foot, apex, half-width
STEP = 0.2

rs = Raster()
rng = lambda *k: h32(*k) / 4294967295.0

def masonry(r, u, Y, z, x, y, v0, ch=0.55, L=0.9, seed=0, rough=0.35, weather=0.9):
    """coursed ashlar in surface coordinates (u along, Y up): blocks of one, two or three lengths per course, thin
    sunk mortar joints, a lit top arris and a shadowed foot per course, a tone per block, big weathering patches,
    the odd dark (dirty) or pale (replaced) block, tooling grain"""
    ps = z / F
    row = math.floor(Y / ch); fv = Y / ch - row
    uu = u + (h32(row, seed, 5) % 97) / 97.0 * L * 2.0
    col = math.floor(uu / L); fu = uu / L - col
    c0 = col
    while h32(row, c0, seed) % 3 == 0 and col - c0 < 2: c0 -= 1                               # merged blocks
    bid = h32(row, c0, seed + 7)
    v = v0 + ((bid % 9) - 4) * 0.1 + (wn(0, u * 0.22 + seed * 7.0, Y * 0.22) - 0.5) * weather
    v += (wn(1, u * 5.0 + (bid % 17), Y * 5.0) - 0.5) * rough
    if bid % 11 == 0: v -= 0.45
    elif bid % 13 == 0: v += 0.3
    if fv > 1 - 1.5 * ps / ch: v += 0.4
    elif fv < 2.5 * ps / ch: v -= 0.35
    if fv < ps / ch or (fu < ps / L and h32(row, col, seed) % 3 != 0): v -= 1.4                  # the joints
    return tone(r, v, x, y)

# ---------------------------------------------------------------------------------------------------- the arches
def arch_w(X, Y):
    """the half-width of the portal arch passing through (X, Y): all the portal's arches are one family (springing at
    YS, slightly pointed), so this is a radial coordinate across the orders"""
    V = Y - YS
    if V <= 0: return abs(X)
    return math.sqrt((abs(X) + AE * V) ** 2 + (V / AC) ** 2)
def arch_along(X, Y, w):
    """the distance along the arch from the springing (negative down the jambs)"""
    V = Y - YS
    if V <= 0: return V
    return w * math.atan2(V / AC, abs(X) + AE * V) * 1.15

# ---------------------------------------------------------------------------------------------------- windows
def lancet(b, round_=False):
    """the opening test of a window drawn by the user, in canvas pixels: a pointed (or round) arch over a rectangle"""
    x0, y0, x1, y1 = b
    a = (x1 - x0 + 1) / 2.0; cx = (x0 + x1 + 1) / 2.0
    ys = y0 + (a if round_ else a * 1.732)
    def inside(x, y):
        px, py = x + 0.5, y + 0.5
        if not (x0 <= x <= x1 and y0 <= y <= y1): return False
        if py >= ys: return True
        if round_: return math.hypot(px - cx, py - ys) <= a
        return math.hypot(px - (cx + a), py - ys) <= 2 * a and math.hypot(px - (cx - a), py - ys) <= 2 * a
    return inside
def glass(b, Z, cls='prop', round_=False, gain=1.0):
    """the user's stained glass, kept pixel for pixel: a cut quad just in front of the wall over the opening"""
    inside = lancet(b, round_)
    def sh(x, y, s, t, z, wp):
        if not inside(x, y): return None
        return tuple(min(255, int(v * gain)) for v in RP[x, y])
    x0, y0, x1, y1 = b
    rs.quad((X_(x0, Z), Y_(y1 + 1, Z), Z), (X_(x1 + 1, Z), Y_(y1 + 1, Z), Z), (X_(x0, Z), Y_(y0, Z), Z), sh, cls=cls, cut=True)
    return inside
def surround(wins):
    """a dressed stone surround and a sill around the windows in a wall: (dv, kind) for a canvas pixel or None"""
    def f(x, y):
        for (b, inside) in wins:
            x0, y0, x1, y1 = b
            if not (x0 - 4 <= x <= x1 + 4 and y0 - 4 <= y <= y1 + 6): continue
            if y1 < y <= y1 + 4 and x0 - 3 <= x <= x1 + 3:                                     # the sill
                return (1.6, 'sill') if y == y1 + 1 else (-1.2 if y == y1 + 4 else 0.6, 'sill')
            near = any(inside(x + dx, y + dy) for dx, dy in ((3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (-2, 2), (2, -2), (-2, -2)))
            if near: return (1.3 if not any(inside(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) else -1.0, 'frame')
        return None
    return f

# ---------------------------------------------------------------------------------------------------- the parvis
def paving(x, y, s, t, z, wp):
    X, _, Z = wp
    D = 2.4
    row = math.floor(Z / D); fz = Z / D - row
    Wd = 2.0 + (h32(row, 1) % 3) * 0.45
    uu = X + (h32(row, 2) % 10) / 10.0 * Wd
    col = math.floor(uu / Wd); fx = uu / Wd - col
    ps, psz = z / F, z * z / (F * CAMH)
    sid = h32(col, row, 3)
    r_ = SAND if sid % 3 == 0 else GREY
    v = (4.4 if r_ is GREY else 4.0) + ((sid % 7) - 3) * 0.16 + (wn(0, X * 0.3, Z * 0.3) - 0.5) * 1.0 + (wn(1, X * 3.0, Z * 1.2) - 0.5) * 0.4
    v -= min(1.6, max(0.0, (63.0 - Z) / 9.0))                                                  # darker towards the viewer
    v += 0.5 * math.exp(-(X / 3.5) ** 2) * (1 if 56 < Z < 64.5 else 0)                         # the trodden way to the steps
    if sid % 6 == 0 and abs((fx - 0.2) - fz * 0.6) < ps / Wd * 1.2: v -= 1.3                   # a crack
    if fx < ps / Wd * 1.3 or fz < psz / D * 1.3:
        c = tone(r_, v - 1.8, x, y)
        return mix(c, LEAF[1], 0.35) if wn(2, X * 0.8, Z * 0.8) > 0.6 else c                   # moss in the joints
    return tone(r_, v, x, y)
rs.quad((-90, 0, 44), (90, 0, 44), (-90, 0, 160), paving, cls='ground')
SX = 6.8
def tread(i):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = 5.0 + (wn(0, X * 0.5, Z * 2.0) - 0.5) * 0.8 + 0.6 * math.exp(-(X / 2.2) ** 2)      # worn hollow in the middle
        if (X + 20) % 2.3 < z / F * 1.2: v -= 1.4
        return tone(GREY, v, x, y)
    return sh
def riser(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 3.2 + (wn(1, X * 0.7, Y * 3.0) - 0.5) * 0.8 + (0.8 if t > 0.75 else 0)                  # the nosing catches the light
    if (X + 20) % 2.3 < z / F * 1.2: v -= 1.2
    return tone(GREY, v, x, y)
for i, (z0, z1) in enumerate(((64.3, 65.3), (65.3, 66.3), (66.3, ZD))):
    rs.box(-SX, SX, 0, STEP * (i + 1), z0, ZD + 0.5, riser, riser, top=tread(i), cls='prop')

# ---------------------------------------------------------------------------------------------------- the nave wall
BIGWIN = (487, 3, 579, 121)
NAVE_WINS = [(BIGWIN, glass(BIGWIN, ZN - 0.05, round_=True))]
nave_sur = surround(NAVE_WINS)
FRX, FRT = 7.4, 22.2                                              # the stepped frame behind the gable: half-width, top
def nave(x, y, s, t, z, wp):
    X, Y, Z = wp
    sr = nave_sur(x, y)
    if Y < FRT and abs(X) < FRX:                                  # the frame: bands stepping in, the red fillet, the dark
        d = min(FRX - abs(X), FRT - Y)
        if d < 0.45: return tone(GREY, 6.6 + 1.2 * math.sin(d / 0.45 * math.pi) - (0.8 if FRT - Y < 0.12 else 0), x, y)
        if d < 0.62: return tone(REDT, 2.4 - (0.6 if abs(X) > FRX - 0.62 and FRT - Y > d else 0), x, y)
        if d < 1.0: return tone(GREY, 7.6 - (d - 0.62) * 3, x, y)
        if d < 1.3: return tone(GREY, 4.6 + (0.6 if FRT - Y < 1.3 and FRT - Y >= abs(X) - FRX + 1.3 else -0.4), x, y)
        if d < 1.45: return tone(SAND, 7.0, x, y)
        return masonry(RUBBLE, X, Y, z, x, y, 1.6 - 0.8 * max(0.0, 1 - (d - 1.45) / 0.8), ch=0.5, L=0.8, seed=31, weather=0.5)
    v0 = 4.4 if abs(X) < 5.3 and Y > FRT else 3.7                 # the window bay is a shade paler
    c = masonry(GREY, X, Y, z, x, y, v0 + (sr[0] if sr else 0), seed=11)
    return c
rs.quad((-13, 0, ZN), (13, 0, ZN), (-13, 31, ZN), nave, cls='wall')
def shaft_sh(cx, cz, r):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        phi = math.atan2(X - cx, -(Z - cz))
        v = 5.0 + 1.6 * math.cos(phi + 0.6) - 0.6
        if (Y - FRT) % 2.2 < z / F * 1.2: v -= 1.2                                               # drums
        return tone(GREY, v + (wn(1, phi * 3, Y * 3) - 0.5) * 0.5, x, y)
    return sh
def cylinder(cx, cz, r, y0, y1, sh, n=40, cls='wall'):
    for i in range(n):
        a0, a1 = -math.pi + 2 * math.pi * i / n, -math.pi + 2 * math.pi * (i + 1) / n
        P0 = (cx + r * math.sin(a0), y0, cz - r * math.cos(a0)); P1 = (cx + r * math.sin(a1), y0, cz - r * math.cos(a1))
        rs.quad(P0, P1, (P0[0], y1, P0[2]), sh, cls=cls)
def cone(cx, cz, r, y0, y1, sh, n=40, cls='wall'):
    for i in range(n):
        a0, a1 = -math.pi + 2 * math.pi * i / n, -math.pi + 2 * math.pi * (i + 1) / n
        P0 = (cx + r * math.sin(a0), y0, cz - r * math.cos(a0)); P1 = (cx + r * math.sin(a1), y0, cz - r * math.cos(a1))
        rs.quad(P0, P1, (cx, y1, cz), sh, clip=lambda a, b: a + b <= 1.0, cls=cls)
for sx in (-1, 1):
    cylinder(sx * 5.75, ZN - 0.3, 0.42, FRT, 31, shaft_sh(sx * 5.75, ZN - 0.3, 0.42), n=16)
for k, (x0, x1, top) in enumerate(((429, 457, 125), (586, 612, 125))):                         # moss on the frame's top
    for j in range(9):
        xx = x0 + (x1 - x0) * j / 8.0 + (h32(k, j) % 3)
        rs.disc(X_(xx, ZN - 0.5), Y_(top, ZN - 0.5), ZN - 0.5, 0.09 + (h32(k, j, 3) % 3) * 0.03,
                lambda x, y, s, t, z, wp, c=j: LEAF[(c + (1 if t < 0 else 0)) % 2] if t < 0.4 else LEAF[0])
    for j in range(3):
        xx = x0 + 4 + j * 9 + (h32(k, j, 4) % 4)
        rs.line3((X_(xx, ZN - 0.45), Y_(top + 1, ZN - 0.45), ZN - 0.45), (X_(xx, ZN - 0.45), Y_(top + 1, ZN - 0.45) - 0.35 - (h32(k, j, 5) % 3) * 0.2, ZN - 0.45),
                 lambda x, y, s, t, z, wp: LEAF[1], w=0.07)

# ---------------------------------------------------------------------------------------------------- the portal
def door_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    ps = z / F
    if abs(X) < 0.06: return OAK[0]                                                              # where the leaves meet
    for yb in (1.95, 5.6, 9.47):                                                                 # the iron straps
        if abs(Y - yb) < 0.2 and abs(X) < W0 - 0.05:
            if abs(X) < 0.32 and abs(Y - yb) > 0.1: break                                         # the strap ends round
            v = 2.4 + (0.8 if Y > yb + 0.08 else 0)
            if abs(((X + 20) / 0.55) % 1 - 0.5) < 0.12 and abs(Y - yb) < 0.08: v = 4.2             # nail heads
            return tone(IRON, v, x, y)
    for hx in (-0.5, 0.5):                                                                       # ring handles
        d = math.hypot(X - hx, (Y - 5.0) * 1.0)
        if 0.22 < d < 0.36 and Y < 5.2: return tone(BRASS, 2.6 if X * hx < hx * hx else 1.6, x, y)
        if d < 0.12 and abs(Y - 5.36) < 0.12: return BRASS[3]
    pl = math.floor((X + 20) / 0.62); fu = (X + 20) / 0.62 - pl
    v = 3.6 + (h32(pl, 5) % 3 - 1) * 0.3 + (wn(1, X * 1.6 + pl, Y * 0.12) - 0.5) * 1.6
    v -= 0.9 * math.exp(-(Y - 0.6) / 1.4)                                                         # the wet, kicked foot
    if fu < ps / 0.62 * 1.2: v -= 1.6
    if h32(pl, int(Y * 1.7), 9) % 19 == 0: v -= 0.8                                             # knots
    return tone(OAK, v, x, y)
rs.quad((-W0, 0.6, ZD), (W0, 0.6, ZD), (-W0, YS, ZD), door_sh, cls='prop')
def tymp_glass(c):
    return c[0] > 150 and c[1] > 110 and c[2] < 140
def tympanum(x, y, s, t, z, wp):
    X, Y, Z = wp
    if Y < YS or arch_w(X, Y) > W0: return None
    if tymp_glass(RP[x, y]): return None                                                         # the glass shows through
    return masonry(GREY, X, Y, z, x, y, 2.6, ch=0.45, L=0.7, seed=41, weather=0.4)
rs.quad((-W0, YS, ZD), (W0, YS, ZD), (-W0, 17.0, ZD), tympanum, cls='wall', cut=True)
def tymp_light(x, y, s, t, z, wp):
    X, Y, Z = wp
    if Y < YS or arch_w(X, Y) > W0: return None
    c = RP[x, y]
    if not tymp_glass(c): return GLOWC[1]
    return tone(GLOWC, 3.6 + (c[0] - 200) / 40.0 + (wn(1, X * 2, Y * 2) - 0.5), x, y)
rs.quad((-W0, YS, ZD + 0.15), (W0, YS, ZD + 0.15), (-W0, 17.0, ZD + 0.15), tymp_light, cls='emit', cut=True)

def order(w_in, w_out, Z, seed, v0):
    """one order of the portal: a moulded ring (a roll between two hollows) with voussoirs in the arch and coursed
    jamb stones below the springing"""
    def sh(x, y, s, t, z, wp):
        X, Y, _ = wp
        w = arch_w(X, Y)
        if w <= w_in or w > w_out: return None
        q = (w - w_in) / (w_out - w_in)
        v = v0 + 1.3 * math.sin(q * math.pi) - (0.9 if q < 0.12 else 0) - (0.5 if q > 0.9 else 0)
        al = arch_along(X, Y, w)
        if al > 0:
            if (al / 0.62) % 1 < z / F / 0.62 * 1.1: v -= 1.4                                     # voussoir joints
            v += 0.35 * (1 if X < 0 else -0.2)                                                       # light from the left
        elif (Y / 0.55) % 1 < z / F / 0.55: v -= 1.4
        v += (wn(1, w * 4 + seed, (al if al > 0 else Y) * 4) - 0.5) * 0.4
        if h32(int((al if al > 0 else Y) / 0.62) + 99, seed) % 9 == 0: v -= 0.4
        return tone(GREY, v, x, y)
    rs.quad((-w_out, 0.6, Z), (w_out, 0.6, Z), (-w_out, 19.0, Z), sh, cls='wall', cut=True)
order(W0, W1, Z1, 1, 4.8)
order(W1, W2, Z2, 2, 5.3)

GSLOPE = (GAPEX - GBASE) / GHALF
NICHES = [(-1.69, 1.44), (0.0, 1.44), (1.69, 1.44)]                     # the blind arcade: centres, widths
NB0, NB1 = 16.95, 19.2
TRI = (21.0, 1.25)                                                      # the triangular light: centre Y, half-width
def gable(x, y, s, t, z, wp):
    X, Y, Z = wp
    ax = abs(X)
    top = GBASE + (GHALF - ax) * GSLOPE
    if Y > top: return None
    w = arch_w(X, Y)
    if w <= W2: return None
    if w <= WH:                                                                                  # the hood mould
        q = (w - W2) / (WH - W2)
        return tone(GREY, 6.0 + 1.2 * math.sin(q * math.pi) - (1.4 if q > 0.8 else 0), x, y)
    dn = (top - Y) * math.cos(math.atan(GSLOPE))                                                 # distance under the rake
    if dn < 0.5:                                                                                 # the coping
        return tone(GREY, 6.4 + (1.2 if dn < 0.12 else 0) - (1.6 if dn > 0.4 else 0) + (wn(1, X * 3, Y * 3) - 0.5) * 0.6, x, y)
    v = 4.3
    for (nx, nw) in NICHES:                                                                      # the blind arcade
        if abs(X - nx) < nw / 2 + 0.12 and NB0 - 0.25 < Y < NB1 + nw / 2 + 0.12:
            r_ = nw / 2
            inner = abs(X - nx) < r_ and NB0 < Y and (Y < NB1 or math.hypot(X - nx, Y - NB1) < r_)
            if inner:
                dv = -2.6 + (0.9 if Y < NB0 + 0.18 else 0) - (0.8 if (Y > NB1 - 0.3 and math.hypot(X - nx, Y - NB1) > r_ - 0.25) else 0)
                return masonry(GREY, X, Y, z, x, y, v + dv, ch=0.5, seed=52, weather=0.3)
            if Y < NB0 or abs(X - nx) >= r_ or (Y >= NB1 and math.hypot(X - nx, Y - NB1) >= r_):
                if NB0 - 0.25 < Y < NB0: return tone(GREY, 6.4 if Y > NB0 - 0.1 else 3.0, x, y)   # the sill
                if abs(X - nx) < r_ + 0.12 and (Y < NB1 or math.hypot(X - nx, Y - NB1) < r_ + 0.12):
                    return tone(GREY, 5.8 + (0.6 if X < nx else -0.4), x, y)                       # the arch rims
    ty, th = TRI                                                                                 # the triangular light
    hh = th * 1.5
    if ty - hh / 2 < Y < ty + hh / 2:
        lim = th * (ty + hh / 2 - Y) / hh
        if ax < lim:
            if ax < lim - 0.32 and Y > ty - hh / 2 + 0.3: return VOID if ax < lim - 0.42 else tone(GREY, 1.6, x, y)
            return tone(GREY, 6.6 - (0.8 if Y < ty - hh / 2 + 0.15 else 0), x, y)
    for sx in (-1, 1):                                                                           # trefoil spandrels
        cx_, cy_ = sx * 3.0, 16.3
        for (dx, dy) in ((0, 0.26), (-0.24, -0.12), (0.24, -0.12)):
            d = math.hypot(X - cx_ - dx, Y - cy_ - dy)
            if d < 0.2: return VOID
            if d < 0.3: return tone(GREY, 6.2, x, y)
    return masonry(GREY, X, Y, z, x, y, v, ch=0.55, L=0.9, seed=51)
rs.quad((-GHALF, 0.6, ZP), (GHALF, 0.6, ZP), (-GHALF, GAPEX + 0.1, ZP), gable, cls='wall', cut=True)
def crocket(x, y, s, t, z, wp):
    return tone(GREY, 6.0 - 2.2 * t + 0.6 * (1 if s < 0 else 0), x, y)

def pier_sh(sx):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = 4.6 + (0.4 if sx < 0 else -0.2)
        for so in (6.0, 10.6):                                                                    # weathered set-offs
            if so - 0.28 < Y < so: return tone(GREY, 6.8 if Y > so - 0.1 else 5.6, x, y)
            if so - 0.42 < Y <= so - 0.28: return tone(GREY, 2.4, x, y)
        if Y > 10.6: v += 0.3
        return masonry(GREY, X, Y, z, x, y, v, ch=0.55, L=0.85, seed=61 + sx)
    return sh
def pier_side(x, y, s, t, z, wp):
    return masonry(GREY, wp[2], wp[1], z, x, y, 3.0, ch=0.55, L=0.85, seed=63)
for sx in (-1, 1):
    x0, x1 = sorted((sx * W2, sx * GHALF))
    rs.box(x0, x1, 0.6, GBASE + 1.3, ZPIER, ZP + 0.2, pier_sh(sx), pier_side, cls='wall')
    pcx = sx * (W2 + GHALF) / 2                                                                    # a pinnacle on each pier
    cone(pcx, ZPIER + 0.6, 0.95, GBASE + 1.3, GBASE + 4.2,
         lambda x, y, s, t, z, wp, pcx=pcx: tone(GREY, 5.4 + (0.7 if wp[0] < pcx else -0.7) - (0.9 if (wp[1] * 3.0) % 1 < 0.15 else 0), x, y), n=12)

# ---------------------------------------------------------------------------------------------------- the towers
def tower_sh(cx, seed):
    win = (315, 223, 325, 276) if cx < 0 else (724, 223, 734, 276)
    ins = lancet(win)
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        phi = math.atan2(X - cx, -(Z - ZT))
        lit = 1.5 * math.cos(phi + 0.5) - 0.7
        if win[0] - 3 <= x <= win[2] + 3 and win[1] - 4 <= y <= win[3] + 5:                       # the lancet's surround
            if win[3] < y <= win[3] + 3: return tone(SAND, 9.0 if y == win[3] + 1 else 5.0, x, y)
            if any(ins(x + dx, y + dy) for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))):
                return tone(SAND, 3.4 if any(ins(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1))) else 8.6, x, y)
        return masonry(SAND, RT * phi, Y, z, x, y, 6.2 + lit, ch=0.6, L=1.0, seed=seed, weather=1.1)
    return sh
def ring_sh(cx, v0, h, cls_top=True):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        phi = math.atan2(X - cx, -(Z - ZT))
        lit = 1.4 * math.cos(phi + 0.5) - 0.6
        q = t
        return tone(SAND, v0 + lit + (1.4 if q > 0.75 else 0) - (1.6 if q < 0.2 else 0) + (wn(1, phi * 6, Y * 4) - 0.5) * 0.5, x, y)
    return sh
def corbels(cx):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        phi = math.atan2(X - cx, -(Z - ZT))
        lit = 1.4 * math.cos(phi + 0.5) - 0.6
        k = (RT * phi / 0.7) % 1
        if k < 0.45: return tone(SAND, 6.0 + lit + (1.0 if t > 0.7 else -0.6 * (1 - t)), x, y)       # a corbel
        return tone(SAND, 2.6 + lit * 0.5, x, y)                                                     # the shadow between
    return sh
def spire(cx):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        phi = math.atan2(X - cx, -(Z - ZT))
        lit = 1.2 * math.cos(phi + 0.5) - 0.4
        rr = max(0.05, 3.7 * (29.2 - Y) / (29.2 - 24.7))
        lat = rr * (phi - math.atan2(-cx, ZT))                                                     # across, facing the camera
        if 24.9 < Y < 27.3 and abs(lat) < 0.95 * (27.3 - Y) / 2.4 + 0.02:                          # the louvre
            lim = 0.95 * (27.3 - Y) / 2.4
            if abs(lat) > lim - 0.2 or Y < 25.1: return tone(GREY, 6.4 + lit, x, y)
            return tone(SLATE, 0.6 + (1.2 if (Y * 6.0) % 1 < 0.3 else 0), x, y)
        row = math.floor(Y / 0.32); fv = Y / 0.32 - row
        u = rr * phi / 0.36 + (row % 2) * 0.5; fu = u % 1
        v = 3.4 + lit + ((h32(int(u), row, 3) % 5) - 2) * 0.18 + (wn(2, phi * 4, Y * 0.8) - 0.5) * 1.0
        if fv < 0.25 + 0.35 * (fu - 0.5) ** 2 * 4: v -= 1.3                                         # the rounded scale butts
        return tone(SLATE, v, x, y)
    return sh
for sx, cx in ((-1, -12.2), (1, 12.2)):
    cylinder(cx, ZT, RT + 0.35, 0, 1.3, ring_sh(cx, 4.6, 1.3))                                    # plinth
    cylinder(cx, ZT, RT, 1.3, 24.0, tower_sh(cx, 70 + sx))
    for yc in (10.7, 17.9):
        cylinder(cx, ZT, RT + 0.2, yc - 0.2, yc + 0.22, ring_sh(cx, 6.6, 0.42))                   # string courses
    cylinder(cx, ZT, RT + 0.12, 23.4, 24.0, corbels(cx))
    cylinder(cx, ZT, RT + 0.4, 24.0, 24.7, ring_sh(cx, 6.8, 0.7))                                 # the cornice
    cone(cx, ZT, RT + 0.45, 24.7, 29.2, spire(cx), n=48)
    rs.disc(cx, 29.4, ZT - 0.2, 0.22, lambda x, y, s, t, z, wp: tone(BRASS, 2.4 - t * 1.5, x, y))  # the finial ball
for b in ((315, 223, 325, 276), (724, 223, 734, 276)):
    glass(b, ZT - RT - 0.03, cls='emit', gain=1.05)

# ---------------------------------------------------------------------------------------------------- the aisles and buttresses
AISLE_WINS = [(192, 35, 208, 104), (232, 35, 248, 104), (207, 247, 239, 352),
              (807, 39, 823, 100), (847, 39, 863, 100), (820, 271, 854, 418)]
aisle_sur = surround([(b, glass(b, ZW - 0.05)) for b in AISLE_WINS])
def bay(x, y):
    """the dark bay under the arch at the foot of each aisle (the user's arch shape, mirrored on the right)"""
    xx = x if x < CX else 1066 - x
    if not (177 <= xx <= 274 and y <= 236): return None
    th = math.asin(max(-1.0, min(1.0, (xx - 177) / 93.0)))
    ya = 192 - 65 * math.cos(th)
    if y < ya - 5: return None
    return 'ring' if y < ya else 'void'
def aisle(x, y, s, t, z, wp):
    X, Y, Z = wp
    b = bay(x, y)
    if b == 'void': return None
    if b == 'ring':
        k = math.atan2(y - 192, (x if x < CX else 1066 - x) - 177)
        return tone(GREY, 6.8 - (1.4 if int(k * 9) % 2 and (k * 9) % 1 < 0.1 else 0) - (1.0 if bay(x, y + 1) == 'void' else 0), x, y)
    sr = aisle_sur(x, y)
    if sr: return tone(RUBBLE, 5.4 + sr[0], x, y) if sr[1] != 'sill' else tone(GREY, 4.6 + sr[0], x, y)
    return masonry(RUBBLE, X, Y, z, x, y, 4.0, ch=0.42, L=0.66, seed=21, rough=0.5, weather=1.1)
for sx in (-1, 1):
    x0, x1 = sorted((sx * 13.0, sx * 25.0))
    rs.quad((x0, 0, ZW), (x1, 0, ZW), (x0, 33, ZW), aisle, cls='wall', cut=True)
def bay_back(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 1.2 + 0.8 * max(0.0, (Y - 18.0) / 6.0) * (1 if abs(X) > 15 else 0.5)
    if (X * 1.3) % 1 < 0.08: v += 0.6                                                              # vault ribs in the dark
    return tone(RUBBLE, v, x, y)
for sx in (-1, 1):
    x0, x1 = sorted((sx * 13.0, sx * 26.0))
    rs.quad((x0, 14, ZW + 6), (x1, 14, ZW + 6), (x0, 26, ZW + 6), bay_back, cls='wall')
def buttress(sx):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        dirt = 0.0
        for yc in (10.4, 17.9, 27.6):                                                             # string courses
            if yc - 0.22 < Y < yc + 0.2: return tone(GREY, 6.4 if Y > yc + 0.05 else 5.0, x, y)
            if yc - 0.5 < Y <= yc - 0.22: return tone(GREY, 1.8, x, y)
            if Y < yc and wn(3, X * 1.4, yc) > 0.5: dirt = max(dirt, 1.1 * math.exp(-(yc - Y) / 1.8) * (wn(3, X * 1.4, yc) - 0.5) * 4)
        return masonry(GREY, X, Y, z, x, y, 3.2 + (0.3 if sx < 0 else 0) - dirt, ch=0.62, L=1.2, seed=81 + sx, weather=1.2)
    return sh
def buttress_side(x, y, s, t, z, wp):
    return masonry(GREY, wp[2], wp[1], z, x, y, 2.0, ch=0.62, L=1.2, seed=85)
for sx in (-1, 1):
    xi, xo = X_(175 if sx < 0 else 891, ZO), X_(-10 if sx < 0 else 1077, ZO)
    x0, x1 = sorted((xi, xo))
    rs.box(x0, x1, 0, 34, ZO, ZW, buttress(sx), buttress_side, cls='wall')

# ---------------------------------------------------------------------------------------------------- the shell
def shell_mask():
    """the user's eggshell halves: per row the broken rim (the span from the canvas edge to it, median-filtered so the
    drawing's string-course lines don't leak in) and the holes (dark blobs, not the 1 px outlines)"""
    def isshell(c):
        h, s, v = colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)
        return s < 0.14 and v > 0.42
    def isdark(c): return max(c) < 34
    raw = {-1: [], 1: []}
    for side in (-1, 1):
        lo, hi = (40, 115) if side < 0 else (945, 1040)
        for y in range(0, 508):
            xs = range(0, 260) if side < 0 else range(1066, 800, -1)
            edge, miss = None, 0
            for x in xs:
                c = RP[x, y]
                if isshell(c) or isdark(c): edge, miss = x, 0
                else:
                    miss += 1
                    if miss > 5: break
            raw[side].append(edge if edge is not None and lo <= edge <= hi else None)
    edges = {}
    for side in (-1, 1):
        r = raw[side]; out = []
        for y in range(len(r)):
            win = sorted(v for v in r[max(0, y - 6):y + 7] if v is not None)
            med = win[len(win) // 2] if win else None
            v = r[y] if r[y] is not None and med is not None and abs(r[y] - med) <= 10 else med
            out.append(v)
        for y in range(len(out)):                                                                 # gaps: the nearest row
            if out[y] is None: out[y] = next((out[k] for k in sorted(range(len(out)), key=lambda k: abs(k - y)) if out[k] is not None), None)
        edges[side] = out
    m = {}
    for side in (-1, 1):
        for y in range(0, 508):
            e = edges[side][y]
            span = range(0, e + 1) if side < 0 else range(e, 1067)
            for x in span:
                inner = (e - x) if side < 0 else (x - e)
                dark = y < 495 and inner > 3 and isdark(RP[x, y]) and \
                    sum(isdark(RP[x + dx, y + dy]) for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2) if 0 <= x + dx < 1067 and 0 <= y + dy < 600) >= 12
                m[(x, y)] = 'hole' if dark else 'shell'
    return m, edges
SHELL, SHELL_EDGE = shell_mask()
def shell(x, y, s, t, z, wp):
    """the eggshell: matte, faintly mottled and freckled, convex (lit from the upper left), a thin bright broken rim,
    the holes dark with the shell's thickness showing on their lower lip, crystals grown in the right half"""
    k = SHELL.get((x, y))
    if k is None: return None
    X, Y, Z = wp
    side = -1 if x < CX else 1
    e = SHELL_EDGE[side][min(y, 507)]
    inner = (e - x) if side < 0 else (x - e)                                                      # px from the rim
    if k == 'hole':
        if side > 0 and wn(3, X * 6.0, Y * 6.0) > 0.56:                                           # crystals in the right half
            f = wn(2, X * 9.0, Y * 9.0)
            return tone(CRYST, 1.5 + f * 4.0 + (1.0 if (x + 2 * y) % 7 == 0 else 0), x, y)
        if SHELL.get((x, y + 1)) == 'shell' or SHELL.get((x, y + 2)) == 'shell': return tone(EGG, 4.6, x, y)   # the lip: the shell's thickness
        return VOID if SHELL.get((x, y - 1)) == 'hole' else tone(EGG, 1.0, x, y)
    if SHELL.get((x, y + 1)) == 'hole': return tone(EGG, 2.6, x, y)                                # shadow on the hole's upper edge
    if SHELL.get((x, y - 1)) == 'hole': return tone(EGG, 9.4, x, y)                                # the lit outer edge of the lip
    if inner <= 1: return tone(EGG, 9.4 if inner == 1 else 5.6, x, y)                            # the broken rim
    width = max(20, e + 1 if side < 0 else 1067 - e)
    u = 1.0 - inner / width                                                                       # 0 at the canvas edge, 1 at the rim
    v = 5.0 + 1.5 * math.sin(min(1.0, u * 1.25) * math.pi / 2) - 0.7 * u ** 6                       # convex: it turns away at both sides
    if side > 0: v -= 0.4                                                                         # the light comes from the left
    v += 0.4 * (1 - y / 500.0)
    v += (wn(0, X * 0.18, Y * 0.18) - 0.5) * 1.1 + (wn(1, X * 0.9, Y * 0.9) - 0.5) * 0.4           # soft greyish patches
    v += ((h32(x, y, 78) % 5) - 2) * 0.14                                                         # the pores of the shell
    if h32(x, y, 77) % 61 == 0: v -= 1.2                                                          # freckles
    if wn(3, X * 0.25 + 9, Y * 0.25) > 0.62 and abs(wn(2, X * 1.1 + 40, Y * 0.5) - 0.5) < 0.01:   # a few hairline cracks
        v -= 2.2
    return tone(EGG, v, x, y)
for sx in (-1, 1):
    x0, x1 = (0, 270) if sx < 0 else (800, 1067)
    rs.quad((X_(x0, ZE), 0, ZE), (X_(x1, ZE), 0, ZE), (X_(x0, ZE), Y_(-2, ZE), ZE), shell, cls='wall', cut=True)

img = rs.render(INK, fog=lambda z: 0.0, light_gain=1.1, grime_gain=1.0, bloom=0.4, stain_gain=0.9, damp_gain=0.8)
img.save(f'{OUT}/cathedral.png')
print('done cathedral')
