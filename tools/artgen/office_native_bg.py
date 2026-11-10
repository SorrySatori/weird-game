"""The abandoned office in Shed 521 (ShedAbandonedOfficeScene), redrawn natively at 1067x600 on the shared camera
(raster3d.py: VP (533, 296), F 300, eye 12 units, the player 6.4 units, feet on y 534 = depth 15), after the old AI
picture (office_ref.png, kept with office_bg.py): the same L-shaped room, one-point view and dim sepia mood.

  light   almost all of it comes through two tall windows of yellowed glass in the left wall: amber shafts through the
          dusty air and pools on the floor (glazing bars in them); deep shadow and occlusion in the corners, under the
          ceiling, under the desks and along the wall bases; a weak column of daylight from a breach in the roof; a
          soft, uneven pool of light on the graffito wall; a final warm grade and a vignette
  left    a tall timber hall turned office long ago: radiators, notice boards shedding their papers, a cupboard in the
          corner, rows of old wooden desks with green-screen terminals (one still lit: the Living Core powers the
          whole Bureau), toppled chairs, filing cabinets, a wall shelf collapsed onto them, pipes along the walls
  back    the doorway "To the Hall" (canvas x 442..497, y 298..416): one leaf swung back, the other gone; beyond it
          the landing of the stair down, an iron handrail dropping away and the Hall's green light rising from below;
          a stopped clock over it, a bookcase beside it fallen in
  roots   the Living Core's dark metal roots have come up the stair: over the threshold, across the floor, along the
          bases of the walls, up the walls and the desk legs
  ceiling a high plank ceiling on timber girders and joists, rotten: boards missing, a breach to the sky with ivy
          pouring through, dead enamel lamps on long cords, sheet-metal ducts, sagging cables; fallen planks below
  right   the graffito wall, frontal: old plaster over brick, fallen off in patches, water-stained, vines down it, moss
          at its foot, and BETTER DECAY THAN CHANGE sprayed big in a dark brown maroon (narrow hand-sprayed strokes with
          a crisp core, a faint overspray, a few short drips, chipped at the edges, the water runs over it); left of it,
          high up, an old opening bricked up long ago (Palinode's tunnel, canvas (662, 212)); a desk pushed against it,
          spray cans at its foot
  front   half-stripped vinyl tiles, paper drifts, roots and cables, a fallen door leaf, toppled chairs; a cabinet at
          the left wall and a desk at the right edge, close to the camera (behind the walk line)
The way back to the stairs is the left edge: warm light from the stairwell door just out of frame falls on the floor.

    python3 office_native_bg.py <outdir>   ->  office.png (= assets/images/backgrounds/ShedAbandonedOffice.png),
                                               guides.png + chars.png (Aseprite reference layers), office-native.gpl
"""
import sys, os, math, random
from PIL import Image, ImageDraw
from common import h32, make_noise, band, ramp
from raster3d import Raster, proj, ray, W, H, CX, HY, F, CAMH

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))

_nz = [make_noise(1, s, 509, 509) for s in (71, 72, 73, 74, 75, 76)]
def wn(i, a, b): return _nz[i](a + 3000.0, b + 3000.0)              # noise in WORLD units
def ri(r, i): return r[max(0, min(len(r) - 1, int(i)))]
def tone(r, v, x, y): return ri(r, band(v, x, y))
def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

# ---------------------------------------------------------------------------------------------------- palette
PLAST = ramp('#13110a #1a170f #221e14 #2a2519 #332d1e #3c3524 #463e2a #504730 #5b5037 #665a3f #726448 #7e6f52')
DADO = ramp('#0e130e #141a13 #1a2319 #212d1f #283826 #30432d #3a4f36')
BRICK = ramp('#170e0a #20130e #2a1912 #352016 #40271b #4c2f21 #583727')
NBRICK = ramp('#191512 #221c17 #2c241d #372d24 #42372c #4e4134')
MORTAR = ramp('#1f1d17 #29271f #343128 #403c31')
PAINT = ramp('#150a0b #1f0f10 #2a1415 #35191b #401e20 #4b2325 #56282a #622e30')     # the graffito: dark brown maroon
WOODD = ramp('#100b07 #18110b #21170f #2b1e14 #36261a #423020 #4f3a27 #5d452f')
TIMBER = ramp('#0b0907 #120e0a #19140e #211a13 #2a2218 #342a1e #3f3325')
TILEA = ramp('#141510 #1a1c15 #21231a #282a20 #2f3226 #373a2c #404333 #4a4d3b')            # olive vinyl
TILEB = ramp('#161510 #1c1a14 #232019 #2a271e #322e24 #3a352a #433d31 #4d4638')            # umber vinyl
SCREED = ramp('#101110 #161714 #1c1e1a #232520 #2b2d27 #33362e #3c3f36')
STEEL = ramp('#0f1110 #161917 #1e221f #272b27 #303530 #3b403a #474c45 #555a51')
RUSTY = ramp('#1e130d #2c1c13 #3c2619 #4c3020 #5c3b28 #6c4630')
BEIGE = ramp('#24221a #322f24 #423e30 #534e3d #655f4b #787159 #8b8368 #9d9577')          # yellowed plastic
CRT = ramp('#051009 #08190e #0c2614 #12361d #1a4a28 #276336 #3b844b #5ea96a #8fd096')
GLASSD = ramp('#0b0f0d #101614 #161e1b #1d2622 #252f2a')
LEAF = ramp('#0c120a #111a0e #172313 #1e2d18 #26381d #2f4423 #3a5129')
MOSS = ramp('#161b0f #1e2514 #262f19 #2f3a1e #394524 #44512a')
PAPER = ramp('#2f2d25 #403d32 #534f41 #67624f #7b755f #8f8870 #a29b82')
SKYW = ramp('#7a6844 #8c784e #9e8858 #b09863 #c2a86e #d2b87a #e0c788 #ecd598')        # overcast, through yellowed glass
FACADE = ramp('#4a4232 #574e3b #645a44 #71664d #7e7256')
ROOT = ramp('#060706 #0c0e0b #131611 #1b1f18 #252a20 #31372a #3f4636 #4f5744')
VEIN = ramp('#11301a #184a24 #22672f')
GREENL = ramp('#08130c #0c1c12 #112818 #17361f #1e4728 #285c33 #34703f')                 # the Hall's light up the stair
ENAMEL = ramp('#121a15 #19241d #213026 #2a3b30 #34473a #3f5444')
CARD = ramp('#1f170e #2b2013 #382a19 #46351f #544027 #624c2f')
CABLE = [(9, 10, 9), (15, 16, 14), (22, 23, 20)]
INK = (6, 6, 4)
ALLRAMPS = [('Plaster', PLAST), ('Dado', DADO), ('Brick', BRICK), ('Infill brick', NBRICK), ('Mortar', MORTAR),
            ('Graffito', PAINT), ('Desk wood', WOODD), ('Timber', TIMBER), ('Vinyl olive', TILEA), ('Vinyl umber', TILEB),
            ('Screed', SCREED), ('Steel', STEEL), ('Rust', RUSTY), ('Beige', BEIGE), ('CRT', CRT), ('Glass', GLASSD),
            ('Ivy', LEAF), ('Moss', MOSS), ('Paper', PAPER), ('Sky', SKYW), ('Facade', FACADE), ('Root', ROOT),
            ('Vein', VEIN), ('Stair green', GREENL), ('Enamel', ENAMEL), ('Cardboard', CARD)]

# ---------------------------------------------------------------------------------------------------- the room
WX = 26.0                  # the left wall (X = -WX)
XE = 1.6                   # the graffito wall's left end
ZG = 21.0                  # the graffito wall (frontal)
ZB = 30.0                  # the back wall
XR = 44.0                  # the graffito wall runs out of frame on the right
CH = 28.0                  # the plank ceiling
DOOR = (-9.1, -3.6, 9.0, 11.8)            # the doorway to the Hall: X0, X1, door height, transom top
WINS = [(15.4, 19.9), (22.4, 26.2)]       # the windows in the left wall (Z ranges), Y 5..19.5
WY0, WY1 = 5.0, 19.5
BREACH = (-14.4, 23.2, 2.3, 1.9)          # the hole in the ceiling: X, Z, half-sizes
HATCH = (9.03, 17.9)                      # the bricked opening on the graffito wall (centre, = canvas (662, 212))
DESKS = []                                # desk footprints (shadow under them)

def fog(z): return max(0.0, min(0.22, (z - 22) / 60.0))
FOGI = (22, 19, 12)                       # the far end sinks into a warm gloom
def fg(c, z): return mix(c, FOGI, fog(z))

# ---------------------------------------------------------------------------------------------------- light
LD = (0.8, -0.5, -0.12)                   # daylight through the windows: into the room, down, a little toward the eye
_ln = math.sqrt(sum(c * c for c in LD)); LDN = tuple(c / _ln for c in LD)
def sun(X, Y, Z):
    """how much window light reaches the point (0..1): traced back along LD to the left wall's windows, soft-edged,
    with the glazing bars' shadows near the wall"""
    if X <= -WX: return 0.0
    t = (X + WX) / LD[0]
    Yw = Y - LD[1] * t; Zw = Z - LD[2] * t
    if Yw < WY0 - 2.0 or Yw > WY1 + 2.0 or Y > CH: return 0.0
    soft = 0.3 + 0.045 * t
    for (z0, z1) in WINS:
        a = min(Zw - z0, z1 - Zw, Yw - WY0, WY1 - Yw)
        if a > -soft:
            k = min(1.0, (a + soft) / (2 * soft))
            pz, py = ((Zw - z0) / (z1 - z0) * 3) % 1, ((Yw - WY0) / (WY1 - WY0) * 6) % 1
            if t < 16 and (min(pz, 1 - pz) < 0.05 or min(py, 1 - py) < 0.04): k *= 0.5
            k *= 0.7 + 0.3 * min(1.0, py * 3)                                                  # grime settled in each pane
            return k * math.exp(-t / 45.0)
    return 0.0
LIGHTS = [((-24.5, 12.0, 17.6), 0.8, 9.0), ((-24.5, 12.0, 24.3), 0.65, 8.0),            # the windows' glow
          ((-14.4, 25.0, 23.2), 0.3, 10.0),                                              # the breach
          ((-29.0, 4.0, 12.5), 0.3, 8.0),                                                # the stairwell door, off left
          ((-6.4, 1.5, 31.5), 0.25, 5.0)]                                                # green light up the stair
def lit(X, Y, Z, n):
    s = 0.03
    for (lx, ly, lz), I, r in LIGHTS:
        dx, dy, dz = lx - X, ly - Y, lz - Z
        d2 = dx * dx + dy * dy + dz * dz; d = math.sqrt(d2) + 1e-6
        ndl = max(0.0, (dx * n[0] + dy * n[1] + dz * n[2]) / d)
        s += I * (0.3 + 0.7 * ndl) * r * r / (r * r + d2)
    ndl = max(0.0, -(n[0] * LDN[0] + n[1] * LDN[1] + n[2] * LDN[2]))
    if ndl > 0: s += 1.3 * ndl * sun(X, Y, Z)
    return s
def ao(X, Y, Z, own):
    """darkness gathering where the room's planes meet (the surface's own plane does not count)"""
    d = []
    if own != 'floor': d.append(Y)
    if own != 'ceil': d.append((CH - Y) * 0.7)
    if own != 'left': d.append(X + WX)
    if X < XE + 0.3:
        if own != 'back': d.append(ZB - Z)
        if Z > ZG and own != 'side': d.append(XE - X)
    elif own != 'gwall': d.append(ZG - Z)
    return math.exp(-max(0.0, min(d)) / 2.4)
def shaft(X, Z):
    """the column of daylight under the breach (0..1)"""
    d = ((X - BREACH[0]) / (BREACH[2] * 1.05)) ** 2 + ((Z - BREACH[1]) / (BREACH[3] * 1.15)) ** 2
    return max(0.0, 1 - d) ** 1.5
def gw_light(X, Y):
    """the graffito wall catches some light, unevenly: brightest left of centre, falling off to the right, the top
    and the foot, blotched"""
    p = math.exp(-((X - 21.0) / 11.5) ** 2 - ((Y - 17.5) / 9.5) ** 2)
    u = 0.74 + 0.52 * wn(5, X * 0.16, Y * 0.16)
    return 0.05 + 1.2 * p * u
def under_desk(X, Z):
    for (x0, x1, z0, z1) in DESKS:
        if x0 - 0.2 < X < x1 + 0.2 and z0 - 0.3 < Z < z1 + 0.2: return True
    return False

rs = Raster()

# ---------------------------------------------------------------------------------------------------- 2D grids (cables, cracks, vines)
def rasterise(samples, cell=0.07):
    grid = {}
    for (x, y, w) in samples:
        r = int(w / cell) + 1
        for i in range(-r, r + 1):
            for j in range(-r, r + 1):
                d = math.hypot(i * cell, j * cell)
                if d <= w:
                    k = (int(math.floor(x / cell)) + i, int(math.floor(y / cell)) + j)
                    v = 1 - (d / w) ** 1.5
                    if v > grid.get(k, -1): grid[k] = v
    return grid, cell
def grid_at(grid, a, b):
    g, cell = grid
    return g.get((int(math.floor(a / cell)), int(math.floor(b / cell))))

cab_s = []
for pts in (((-18.5, 17.4), (-17.0, 15.6), (-12.0, 15.2), (-9.0, 16.4), (-4.0, 15.9), (1.0, 16.8)),       # desk A's cables
            ((19.4, 17.8), (17.6, 16.6), (13.0, 16.2), (11.0, 14.6), (6.0, 14.0)),
            ((-9.0, 21.6), (-11.0, 19.8), (-14.0, 19.4), (-15.4, 17.0))):
    for (a, b) in zip(pts, pts[1:]):
        n = int(math.dist(a, b) / 0.08) + 1
        for k in range(n):
            t = k / n
            X = a[0] + (b[0] - a[0]) * t; Z = a[1] + (b[1] - a[1]) * t
            X += 0.25 * math.sin(Z * 2.1 + a[0]); Z += 0.2 * math.sin(X * 1.7)
            cab_s.append((X, Z, 0.085))
CABLES = rasterise(cab_s, 0.05)
fc_s = []
frng = random.Random(77)
def _fwalk(X, Z, a, ln, w, depth):
    for k in range(int(ln / 0.08)):
        a += (frng.random() - 0.5) * 0.7
        X += math.cos(a) * 0.08; Z += math.sin(a) * 0.08
        fc_s.append((X, Z, w))
        if depth < 2 and frng.random() < 0.025: _fwalk(X, Z, a + (frng.random() - 0.5) * 2.2, ln * 0.45, w * 0.8, depth + 1)
for k in range(40):
    _fwalk(-25.0 + frng.random() * 55.0, 11.5 + frng.random() * 18.0, frng.random() * 6.28, 2.0 + frng.random() * 5.0, 0.035, 0)
FCRACKS = rasterise(fc_s, 0.035)

CRACKS = {}
def _cracks(seed, starts):
    rc = random.Random(seed); pts = []
    def walk(u, Y, a, ln, w, depth):
        for k in range(int(ln / 0.1)):
            a += (rc.random() - 0.5) * 0.8
            u += math.cos(a) * 0.1; Y += math.sin(a) * 0.1
            pts.append((u, Y, w))
            if depth < 2 and rc.random() < 0.03: walk(u, Y, a + (rc.random() - 0.5) * 2.0, ln * 0.4, w * 0.8, depth + 1)
    for (u, Y, a, ln) in starts: walk(u, Y, a, ln, 0.05, 0)
    CRACKS[seed] = rasterise(pts, 0.04)
def crack_at(u, Y, seed):
    g = CRACKS.get(seed)
    return g is not None and grid_at(g, u, Y) is not None
_cracks(1, [(15.4, 19.6, 1.9, 3.0), (19.9, 19.6, 1.2, 4.5), (22.4, 4.9, -1.7, 2.5), (26.2, 19.6, 1.4, 5.0), (19.9, 4.9, -1.2, 2.0),
            (28.0, 27.8, -1.6, 6.0)])
_cracks(2, [(DOOR[0] - 0.5, DOOR[3] + 0.5, 2.2, 5.0), (DOOR[1] + 0.5, DOOR[3] + 0.5, 1.0, 6.0), (-20.0, 27.5, -1.4, 7.0), (-1.0, 27.5, -1.8, 4.0)])
_cracks(3, [(7.4, 14.9, -2.0, 5.0), (10.7, 14.9, -0.9, 4.0), (9.0, 21.0, 1.6, 4.0), (2.2, 25.0, -0.4, 5.0), (33.0, 27.5, -1.9, 9.0),
            (28.0, 14.5, -1.0, 4.0), (16.0, 6.0, -2.3, 3.0), (22.0, 27.8, -1.5, 5.0), (13.0, 27.8, -1.7, 4.0)])

# vines down the walls: stems hanging from the ceiling (u along the wall, Y up), leaves along them
VINES = {}
def _vines(seed, starts, keep=lambda u, Y: True):
    rv = random.Random(seed); stem, leaves = [], []
    def hang(u, Y, ln, w, depth):
        a = -math.pi / 2
        for k in range(int(ln / 0.1)):
            a += (rv.random() - 0.5) * 0.5; a += (-math.pi / 2 - a) * 0.08                      # gravity
            u += math.cos(a) * 0.1; Y += math.sin(a) * 0.1
            if Y < 0.3: break
            if keep(u, Y): stem.append((u, Y, w))
            if rv.random() < 0.12 and keep(u, Y):
                lu = u + (rv.random() - 0.5) * 0.6; ly = Y + (rv.random() - 0.5) * 0.3
                leaves.append((lu, ly, 0.13 + rv.random() * 0.12))
            if depth < 2 and rv.random() < 0.02: hang(u, Y, ln * 0.5, w * 0.8, depth + 1)
    for (u, Y, ln) in starts: hang(u, Y, ln, 0.05, 0)
    VINES[seed] = (rasterise(stem, 0.04), rasterise(leaves, 0.05))
def vine_at(u, Y, seed, x, y, L):
    g = VINES.get(seed)
    if g is None: return None
    lf = grid_at(g[1], u, Y)
    if lf is not None: return tone(LEAF, 1.0 + 4.0 * L + lf * 1.2 - (0.8 if (x + y) % 5 == 0 else 0), x, y)
    if grid_at(g[0], u, Y) is not None: return tone(LEAF, 0.4 + 2.0 * L, x, y)
    return None
vr = random.Random(9)
_vines(1, [(13.0 + vr.random() * 17.0, CH - 0.2, 4.0 + vr.random() * 18.0) for _ in range(24)])
_vines(2, [(-25.0 + vr.random() * 26.0, CH - 0.2, 3.0 + vr.random() * 14.0) for _ in range(16)],
       keep=lambda u, Y: not (DOOR[0] - 0.8 < u < DOOR[1] + 0.8 and Y < DOOR[3] + 1.0))
def _gkeep(u, Y):
    if 6.6 < u < 11.5 and 13.8 < Y < 22.6: return False                                          # Palinode's arch stays clear
    if 10.5 < u < 32.0 and Y < 25.6: return False                                                # ...and the lettering
    return True
_vines(3, [(XE + vr.random() * 6.0, CH - 0.2, 6.0 + vr.random() * 16.0) for _ in range(7)] +
          [(10.0 + vr.random() * 22.0, CH - 0.2, 1.0 + vr.random() * 2.4) for _ in range(12)] +
          [(32.0 + vr.random() * 6.0, CH - 0.2, 6.0 + vr.random() * 18.0) for _ in range(6)], keep=_gkeep)

# ---------------------------------------------------------------------------------------------------- the floor
TILE = 1.6
def puddle(X, Z):
    d = ((X - BREACH[0] + 0.3) / 2.1) ** 2 + ((Z - BREACH[1] + 0.2) / 1.25) ** 2 + (wn(3, X * 1.3, Z * 1.3) - 0.5) * 0.6
    return 1.0 if d < 0.75 else (0.45 if d < 1.0 else 0.0)
def floor_sh(x, y, s, t, z, wp):
    X, _, Z = wp
    ud = under_desk(X, Z)
    sn = 0.0 if ud else sun(X, 0.0, Z)
    L = lit(X, 0, Z, (0, 1, 0)) * (0.35 if ud else 1.0) + 0.6 * shaft(X, Z) + 0.7 * sn
    A = ao(X, 0.0, Z, 'floor') + (0.7 if ud else 0.0)
    c = grid_at(CABLES, X, Z)
    if c is not None: return fg((40, 38, 32) if c > 0.7 else CABLE[2] if c > 0.35 else CABLE[0], z)
    i, j = math.floor(X / TILE), math.floor(Z / TILE)
    fu, fv = (X / TILE) % 1, (Z / TILE) % 1
    jw_u, jw_v = 0.9 * z / F / TILE + 0.012, 0.9 * z * z / (F * CAMH) / TILE + 0.012
    gone = wn(1, X * 0.2 + 7, Z * 0.2) > 0.54 or h32(i, j, 5) % 11 == 0
    pud = puddle(X, Z)
    damp = max(0.0, wn(3, X * 0.3, Z * 0.3) - 0.6) * 2.5 + pud
    dust = max(0.0, wn(4, X * 0.15 + 70, Z * 0.15) - 0.5) * 2.4                                 # dirt and dust trodden in
    if gone:                                                                                     # the bare screed
        v = 1.0 + 6.0 * L + (wn(0, X * 1.4, Z * 1.4) - 0.5) * 0.9 - 1.8 * A
        if (Z * 3.4 + 0.4 * math.sin(X * 5)) % 1 < 0.12 and wn(4, X * 0.8, Z * 0.8) > 0.55: v -= 0.5      # glue combing
        if grid_at(FCRACKS, X, Z) is not None:
            return fg(tone(MOSS, 0.6 + 2.6 * L, x, y) if damp > 0.4 or Z > ZG - 2.5 else tone(SCREED, v - 1.6, x, y), z)
        v -= 0.5 * min(1.0, damp)
        return fg(tone(SCREED, v, x, y), z)
    rr = TILEA if (i + j) % 2 else TILEB
    v = 0.9 + 6.2 * L + (wn(0, X * 0.8, Z * 0.8) - 0.5) * 0.8 + (h32(i, j, 6) % 5 - 2) * 0.14 - 1.8 * A - 0.7 * dust
    if fu < jw_u or fv < jw_v:
        return fg(tone(MOSS, 0.6 + 2.2 * L, x, y) if (Z > ZG - 1.6 and X > XE) or damp > 0.6 else tone(rr, v - 1.6, x, y), z)
    if grid_at(FCRACKS, X, Z) is not None: return fg(tone(rr, v - 1.5, x, y), z)
    k = h32(i, j, 7) % 9
    if k == 0 and fu + fv > 1.55: v += 1.0                                                     # a lifted, curling corner
    if k == 1 and abs(fu - fv) < 0.025: v -= 1.1                                               # a split tile
    v -= 1.1 * min(1.0, damp)
    c = tone(rr, v, x, y)
    if sn > 0.05: c = mix(c, (150, 112, 58), min(0.35, sn * 0.45))                              # the amber pool
    return fg(c, z)
rs.quad((-WX, 0, 3), (XR, 0, 3), (-WX, 0, ZB), floor_sh, cls='ground')

# ---------------------------------------------------------------------------------------------------- walls
def z_of(Z): return max(1.0, Z / 18.0)
def stain(u, Y, seed):
    """water run down the plaster from the ceiling: each column has its own strength, start and length (so the runs
    are vertical and ragged-ended), plus soft mottled blotches; 0..~1.6"""
    col = max(0.0, wn(3, u * 0.9 + seed * 7.0, 11.0) - 0.5) * 2.0 + max(0.0, wn(4, u * 3.1 + seed * 5.0, 17.0) - 0.62) * 1.6
    top = CH - 1.0 - 9.0 * wn(0, u * 0.5 + seed * 3.0, 23.0)
    ln = 3.0 + 12.0 * wn(1, u * 0.6 + seed * 2.0, 29.0)
    run = col * math.exp(-max(0.0, top - Y) / ln) if Y < top else col * 0.6
    blot = max(0.0, wn(5, u * 0.3 + seed * 9.0, Y * 0.3) - 0.58) * 2.5
    return min(1.6, run * 1.2 + blot)
def plaster(X, Y, Z, x, y, u, seed, L, A, dado=True, soot=10.0):
    """old office paint: dark olive dado, ochre plaster above; rising damp, water stains running down from the
    ceiling with tide marks, soot under the ceiling, cracks"""
    if dado and Y < 0.45: return tone(WOODD, 0.6 + 2.4 * L, x, y)                             # skirting
    if dado and Y < 4.6:
        v = 0.6 + 4.6 * L + (wn(1, u * 0.9, Y * 0.9) - 0.5) * 0.6 - 1.6 * A
        if Y > 4.4: v += 1.0                                                                   # the gloss band
        if wn(0, u * 3.2 + seed, Y * 4.0) > 0.8: return tone(PLAST, 0.8 + 4.0 * L - 1.2 * A, x, y)
        if (u * 2.1) % 1 < 0.05 and h32(int(u * 2.1), seed) % 3 == 0 and Y < 2.4: v -= 0.8   # scuffs from chairs
        return tone(DADO, v, x, y)
    v = 0.8 + 7.4 * L + (wn(0, u * 0.35 + seed, Y * 0.35) - 0.5) * 0.5 + (wn(1, u * 2.2, Y * 2.2) - 0.5) * 0.3 - 2.2 * A
    v += (wn(4, u * 6.0 + seed * 13.0, Y * 6.0) - 0.5) * 0.7                                    # a fine mottle (breaks up flat dither fields)
    tide = wn(2, u * 0.25 + seed, 3.0) * 5.0 + 5.0                                             # rising damp
    if Y < tide: v -= 1.0 * min(1.0, (tide - Y) / 2.5)
    if abs(Y - tide) < 0.07 * z_of(Z) and wn(1, u * 0.7, 9.0) > 0.4: v -= 0.8                # its tide line
    v -= stain(u, Y, seed)                                                                     # water runs from the ceiling, damp blotches
    v -= 1.8 * max(0.0, (Y - (CH - soot)) / soot) ** 1.3                                       # soot under the ceiling
    if crack_at(u, Y, seed): v -= 1.6
    return tone(PLAST, v, x, y)
def brickwork(u, Y, x, y, L, z, rr=BRICK, seed=0, bl=0.9, bh=0.27, sloppy=0.0):
    row = math.floor(Y / bh); off = (row % 2) * bl * 0.5
    col = math.floor((u + off + sloppy * (h32(row, seed, 3) % 3) * 0.1) / bl)
    fu = ((u + off + sloppy * (h32(row, seed, 3) % 3) * 0.1) / bl) % 1; fv = (Y / bh) % 1
    pu = z / F
    if fv < pu / bh * 1.0 + 0.02 or fu < pu / bl * 1.0 + 0.01:
        return tone(MORTAR, 0.4 + 3.4 * L, x, y)
    v = 0.6 + 5.6 * L + (h32(col, row, seed) % 5 - 2) * 0.4 + (wn(1, u * 3.0, Y * 3.0) - 0.5) * 0.5
    if fv > 0.75: v += 0.5                                                                     # the top of each brick catches light
    return tone(rr, v, x, y)
def bare(u, Y, patches):
    """plaster fallen off to the brick: > 0 = brick (its light factor: the plaster lip shades the top), < 0 = the broken
    edge (-2 lit from below, -1 in shadow), None = plaster"""
    for (pu, py_, ru, ry) in patches:
        pd = lambda u_, Y_: ((u_ - pu) / ru) ** 2 + ((Y_ - py_) / ry) ** 2 + (wn(3, u_ * 0.9, Y_ * 0.9) - 0.5) * 0.9 + (wn(2, u_ * 3.0, Y_ * 3.0) - 0.5) * 0.25
        dd = pd(u, Y)
        if dd < 1.0:
            if dd > 0.9: return -2 if Y < py_ else -1
            return 0.55 if pd(u, Y + 0.3) >= 0.9 else 1.0
    return None
def bare_px(b, u, Y, x, y, L, z):
    if b > 0: return brickwork(u, Y, x, y, L * b, z)
    return tone(PLAST, 0.6 + 5.0 * L + (1.2 if b < -1 else -0.6), x, y)

# ---------------------------------------------------------------------------------------------------- the graffito
SW = 0.133                                                                                      # stroke width / letter height
LETTER_W = {'B': 0.58, 'E': 0.5, 'T': 0.58, 'R': 0.6, 'D': 0.62, 'C': 0.58, 'A': 0.66, 'Y': 0.64, 'H': 0.6, 'N': 0.62, 'G': 0.64}
def strokes_for(ch, w):
    i = SW / 2
    L, R, T, B, M, C = i, w - i, i, 1 - i, 0.5, w / 2
    def arc(cx, cy, rx, ry, a0, a1, n=18):
        return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
    if ch == 'E': return [[(L, T), (L, B)], [(L + 0.02, T), (R, T)], [(L + 0.02, M - 0.02), (R - 0.07, M - 0.02)], [(L + 0.02, B), (R + 0.01, B)]]
    if ch == 'T': return [[(L - 0.03, T + 0.01), (R + 0.03, T - 0.01)], [(C, T), (C + 0.01, B)]]
    if ch == 'B':
        yb = 0.47
        up = [(L + 0.02, T), (C - 0.04, T)] + arc(C - 0.04, (T + yb) / 2, R - 0.06 - (C - 0.04), (yb - T) / 2, -90, 90)[1:] + [(L + 0.03, yb)]
        lo = [(L + 0.02, yb), (C - 0.02, yb)] + arc(C - 0.02, (yb + B) / 2, R - (C - 0.02), (B - yb) / 2, -90, 90)[1:] + [(L + 0.02, B)]
        return [[(L, T), (L, B)], up, lo]
    if ch == 'R':
        yb = 0.5
        up = [(L + 0.02, T), (C - 0.04, T)] + arc(C - 0.04, (T + yb) / 2, R - 0.03 - (C - 0.04), (yb - T) / 2, -90, 90)[1:] + [(L + 0.03, yb)]
        return [[(L, T), (L, B)], up, [(C - 0.06, yb), (R + 0.01, B)]]
    if ch == 'D':
        return [[(L, T), (L, B)], [(L + 0.02, T), (C - 0.1, T)] + arc(C - 0.1, 0.5, R - (C - 0.1), 0.5 - i, -90, 90)[1:] + [(L + 0.02, B)]]
    if ch == 'C': return [arc(C, 0.5, C - i, 0.5 - i, -40, -318, 26)]
    if ch == 'G': return [arc(C, 0.5, C - i, 0.5 - i, -38, -358, 26), [(C + 0.02, 0.57), (R + 0.01, 0.57)], [(R, 0.57), (R, 0.84)]]
    if ch == 'A': return [[(C - 0.05, T), (L, B)], [(C + 0.05, T), (R, B)], [(C - 0.06, T), (C + 0.06, T)], [(L + 0.12, 0.66), (R - 0.12, 0.66)]]
    if ch == 'Y': return [[(L, T), (C, 0.53)], [(R, T), (C, 0.53)], [(C, 0.53), (C - 0.01, B)]]
    if ch == 'H': return [[(L, T), (L, B)], [(R, T), (R, B)], [(L, M), (R, M - 0.02)]]
    if ch == 'N': return [[(L, B), (L, T), (R, B), (R, T)]]
    raise KeyError(ch)

# the four lines: text, left x, top y, letter height (px), tilt (deg), tracking (x letter height)
LINES = [('BETTER', 726, 106, 50, -1.6, 0.10), ('DECAY', 712, 160, 63, 0.8, 0.09),
         ('THAN', 774, 231, 37, -1.0, 0.13), ('CHANGE', 704, 274, 66, 1.3, 0.07)]
GX0, GY0, GX1, GY1 = 640, 80, 1067, 470                                                      # the field (canvas px)
GWd, GHt = GX1 - GX0, GY1 - GY0

def spray_graffito():
    """BETTER DECAY THAN CHANGE as hand-sprayed strokes: a round nozzle walked along each stroke with a slight
    wobble, swelling and tapering, paint pooling where a stroke starts and ends, a fuzz of overspray, a few short
    drips from the lower edges"""
    grng = random.Random(1140)
    dens = [[0.0] * GWd for _ in range(GHt)]; core = [[-9.0] * GWd for _ in range(GHt)]
    coats = [[0] * GWd for _ in range(GHt)]; mist = [[0.0] * GWd for _ in range(GHt)]; pool = [[0.0] * GWd for _ in range(GHt)]
    seed = 0
    for (txt, x0, y0, hpx, tilt, track) in LINES:
        cx_ = float(x0); ta = math.tan(math.radians(tilt))
        for ch in txt:
            seed += 1
            w = LETTER_W[ch] * (1 + (grng.random() - 0.5) * 0.08)
            hh = hpx * (1 + (grng.random() - 0.5) * 0.07)
            rot = math.radians((grng.random() - 0.5) * 6.0)
            oy = y0 + (cx_ - x0) * ta + (grng.random() - 0.5) * 3.0
            mx, my = cx_ + w * hh / 2, oy + hh / 2
            cr, sr = math.cos(rot), math.sin(rot)
            def tf(p):
                px_, py_ = p[0] * hh - w * hh / 2, p[1] * hh - hh / 2
                return (mx + px_ * cr - py_ * sr, my + px_ * sr + py_ * cr)
            for k, st in enumerate(strokes_for(ch, w)):
                pts = [tf(p) for p in st]
                for (a, b, idx) in ((pts[1], pts[0], 0), (pts[-2], pts[-1], -1)):                # overshoot both ends a little
                    d = math.dist(a, b) or 1
                    ext = hh * (0.01 + grng.random() * 0.035)
                    pts[idx] = (b[0] + (b[0] - a[0]) / d * ext, b[1] + (b[1] - a[1]) / d * ext)
                r0 = SW * hh / 2 * (1 + (grng.random() - 0.5) * 0.12)
                samples = []; acc = 0.0
                for (a, b) in zip(pts, pts[1:]):
                    d = math.dist(a, b); n = max(1, int(d / 0.55))
                    for q in range(n):
                        t = q / n
                        samples.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, acc + d * t, (b[0] - a[0]) / (d or 1), (b[1] - a[1]) / (d or 1)))
                    acc += d
                samples.append((pts[-1][0], pts[-1][1], acc, 0, 0))
                total = acc
                local = {}
                ss = seed * 7 + k
                taper = (grng.random() - 0.4) * 0.36                                           # the can moves off (or in) along the stroke
                for (sx, sy, sd, tx, ty) in samples:
                    j = (wn(4, sd * 0.06 + ss * 3.1, ss) - 0.5) * 2.2                         # the hand's wobble
                    sx += -ty * j; sy += tx * j
                    r = r0 * (1 + (wn(3, sd * 0.05 + ss, 1.0) - 0.5) * 0.36) * (1 - taper * (sd / (total or 1) - 0.5))
                    blob = 0.0
                    if sd < r * 1.4: blob = 1 - sd / (r * 1.4)                                 # paint pools where the nozzle starts
                    if total - sd < r * 1.1: blob = max(blob, 0.6 * (1 - (total - sd) / (r * 1.1)))
                    r *= 1 + 0.16 * blob
                    R2 = r + 2.6
                    for py in range(int(sy - R2), int(sy + R2) + 2):
                        gy = py - GY0
                        if not 0 <= gy < GHt: continue
                        for px in range(int(sx - R2), int(sx + R2) + 2):
                            gx = px - GX0
                            if not 0 <= gx < GWd: continue
                            d = math.hypot(px + 0.5 - sx, py + 0.5 - sy)
                            if d < r + 0.5:
                                dd = 1.0 if d < r - 0.5 else (r + 0.5 - d)
                                key = (gx, gy)
                                if dd > local.get(key, (0.0, -9))[0] or r - d > local.get(key, (0.0, -9.0))[1]:
                                    o = local.get(key, (0.0, -9.0))
                                    local[key] = (max(o[0], dd), max(o[1], r - d))
                                if blob > 0.2 and d < r: pool[gy][gx] += blob * 0.05
                            elif d < R2:
                                mist[gy][gx] += 0.03 * (1 - (d - r) / (R2 - r)) ** 2
                for (gx, gy), (dd, cc) in local.items():
                    if dd > dens[gy][gx]: dens[gy][gx] = dd
                    if cc > core[gy][gx]: core[gy][gx] = cc
                    if dd > 0.5: coats[gy][gx] += 1
            cx_ += w * hh + hpx * track * (1 + (grng.random() - 0.5) * 0.6)
    # a few short drips from the lower edges of the strokes, where the paint pooled
    drip = {}
    for gx in range(GWd):
        for gy in range(GHt - 1):
            if dens[gy][gx] > 0.5 and dens[gy + 1][gx] <= 0.5:
                p = 0.012 + 0.08 * min(1.0, pool[gy][gx])
                rr_ = h32(gx, gy, 99) % 1000 / 1000.0
                if rr_ < p and gx - drip.get(('last', gy), -9) > 4:
                    drip[('last', gy)] = gx
                    ln = 2 + int(-math.log(1 - (h32(gx, gy, 98) % 1000) / 1000.0 * 0.999) * (3 + 4 * min(1.0, pool[gy][gx])))
                    ln = min(ln, 16)
                    for k in range(1, ln + 1):
                        if gy + k >= GHt: break
                        drip[(gx, gy + k)] = 1 if k < ln else 2
                    if gy + ln + 1 < GHt: drip[(gx, gy + ln + 1)] = 2
    return dens, core, coats, mist, pool, drip
DENS, CORE, COATS, MIST, POOL, DRIP = spray_graffito()

def graffito_at(x, y, wall_c, L, X, Y):
    """the paint over the wall colour at canvas (x, y): a crisp, matte core with a 1 px edge, chipped off in sharp
    flakes, the water runs over it; a faint narrow overspray; None = bare wall"""
    gx, gy = x - GX0, y - GY0
    if not (0 <= gx < GWd and 0 <= gy < GHt): return None
    d = DENS[gy][gx]
    pv = 1.0 + 3.9 * L                                                                         # (the lit centre lands mid-ramp, not clamped at its top)
    if d > 0.2:
        chip = wn(2, X * 2.2 + 40, Y * 2.2) + 0.3 * (wn(4, X * 8.0, Y * 8.0) - 0.5)            # paint chipped off with the plaster skin
        if (chip > 0.78 and CORE[gy][gx] < 2.2) or h32(x // 2, y // 2, 63) % 131 == 0 or h32(x, y, 61) % 173 == 0:
            return None                                                                         # chipped at the edges, flaked inside, never cut through
        v = pv
        if COATS[gy][gx] > 1: v -= 0.4                                                         # a second coat where strokes cross
        v -= 0.25 * min(1.0, POOL[gy][gx])
        v -= 0.8 * stain(X, Y, 3)                                                               # the water runs over the paint too
        paint = tone(PAINT, v, x, y)
        return paint if d > 0.5 else mix(paint, wall_c, 0.5)                                   # one pixel of edge, no more
    dr = DRIP.get((gx, gy))
    if dr: return tone(PAINT, pv - (0.4 if dr == 2 else 0.1), x, y)
    m = MIST[gy][gx]
    if m > 0.04 and h32(x, y, 62) % 1000 < min(0.16, m * 0.3) * 1000: return mix(wall_c, tone(PAINT, pv, x, y), 0.4)
    return None

# ---------------------------------------------------------------------------------------------------- the graffito wall
HY0, HSPR = HATCH[1] - 3.0, HATCH[1] + 1.4                                                    # sill, the arch's springing line
def hatch_part(X, Y):
    """the bricked opening: 'infill' inside, 'arch' the voussoirs, 'sill', 'rim' the broken plaster round it"""
    dx = X - HATCH[0]
    if HY0 - 0.35 < Y < HY0 and abs(dx) < 1.95: return 'sill'
    if Y < HSPR:
        inside = abs(dx) < 1.62 and Y >= HY0
    else:
        rr = math.hypot(dx, Y - HSPR)
        inside = rr < 1.62
        if 1.62 <= rr < 2.1: return 'arch'
    if inside: return 'infill'
    e = 0.55 + 0.55 * wn(3, X * 1.3, Y * 1.3)
    if Y < HSPR: dd = max(abs(dx) - 1.62, HY0 - Y if Y < HY0 else 0)
    else: dd = math.hypot(dx, Y - HSPR) - 2.1
    if dd < e and Y > HY0 - 1.4: return 'rim'
    return None

PATCHES = [(30.5, 17.0, 3.2, 2.6), (19.0, 5.6, 2.8, 1.5), (2.6, 2.6, 1.0, 1.7), (36.5, 6.0, 2.4, 3.2), (4.5, 24.5, 2.2, 1.6)]
def gwall(x, y, s, t, z, wp):
    X, Y, Z = wp
    L = gw_light(X, Y) + 0.5 * lit(X, Y, Z, (0, 0, -1))
    A = ao(X, Y - (5.0 if Y > 18 else 0.0), Z, 'gwall')                                          # (the ceiling's gloom stays higher up here)
    L *= 1 - 0.75 * A
    hp = hatch_part(X, Y)
    if hp == 'infill':
        return brickwork(X - HATCH[0], Y, x, y, L * 0.9, z, NBRICK, 7, bl=0.78, bh=0.25, sloppy=1.0)
    if hp == 'arch':
        a = math.atan2(Y - HSPR, X - HATCH[0]); k = int((a / math.pi) * 9)
        if abs(((a / math.pi) * 9) % 1) < 0.12: return tone(MORTAR, 0.6 + 3.0 * L, x, y)
        return tone(BRICK, 0.8 + 5.4 * L + (h32(k, 3) % 3 - 1) * 0.4, x, y)
    if hp == 'sill': return tone(PLAST, 0.8 + 8.0 * L + (1.2 if Y > HY0 - 0.08 else 0), x, y)
    vn = vine_at(X, Y, 3, x, y, L)
    if vn is not None: return vn
    for (px_, py_, rx, ry) in PATCHES:
        pd = lambda X_, Y_: ((X_ - px_) / rx) ** 2 + ((Y_ - py_) / ry) ** 2 + (wn(3, X_ * 0.9, Y_ * 0.9) - 0.5) * 0.9 + (wn(2, X_ * 3.0, Y_ * 3.0) - 0.5) * 0.25
        dd = pd(X, Y)
        if dd < 1.0:
            if dd > 0.9: return tone(PLAST, 0.6 + 7.0 * L + (1.4 if Y < py_ else -0.6), x, y)
            return brickwork(X, Y, x, y, L * (0.55 if pd(X, Y + 0.3) >= 0.9 else 1.0), z)
    if X < XE + 0.9 + 0.5 * wn(1, 3.0, Y * 0.8) and wn(0, 9.0, Y * 0.35) > 0.42:
        return brickwork(X, Y, x, y, L, z)
    if hp == 'rim':
        return brickwork(X, Y, x, y, L * (0.55 if hatch_part(X, Y + 0.3) is None else 0.85), z)
    c = plaster(X, Y, Z, x, y, X, 3, L * 1.25, A * 0.3, dado=False, soot=2.8)
    if Y < 1.4 + 1.2 * wn(1, X * 0.7, 2.0) and X < 22:                                        # moss along the damp foot
        if wn(0, X * 2.5, Y * 2.5) > 0.42 - 0.2 * (1.4 - Y): c = tone(MOSS, 0.6 + 3.6 * L + (wn(2, X * 4, Y * 4) - 0.5), x, y)
    g = graffito_at(x, y, c, L, X, Y)
    return g if g is not None else c
rs.quad((XE, 0, ZG), (XR, 0, ZG), (XE, CH, ZG), gwall, cls='wall')
def gside(x, y, s, t, z, wp):
    X, Y, Z = wp
    L = lit(X, Y, Z, (-1, 0, 0)); A = ao(X, Y, Z, 'side')
    if wn(0, Z * 0.5, Y * 0.35) > 0.5: return fg(brickwork(Z, Y, x, y, L * (1 - 0.6 * A), z), z)
    return fg(plaster(X, Y, Z, x, y, Z, 4, L, A, dado=False), z)
rs.quad((XE, 0, ZG), (XE, 0, ZB), (XE, CH, ZG), gside, cls='wall')

# ---------------------------------------------------------------------------------------------------- the left wall + windows
def in_window(Z, Y):
    for k, (z0, z1) in enumerate(WINS):
        if z0 < Z < z1 and WY0 < Y < WY1: return k
    return None
def notice(u, w_, L, x, y, seed):
    if u < 0.06 or u > 0.94 or w_ < 0.05 or w_ > 0.95: return tone(WOODD, 1.0 + 3.0 * L, x, y)
    for i in range(7):
        nx, ny = (h32(i, seed, 1) % 70) / 100 + 0.06, (h32(i, seed, 2) % 60) / 100 + 0.08
        if h32(i, seed, 3) % 3 == 2: continue                                                  # fallen
        if nx < u < nx + 0.24 and ny < w_ < ny + 0.28:
            return tone(PAPER, 1.4 + 4.0 * L - (0.8 if int((w_ - ny) / 0.28 * 7) % 2 else 0), x, y)
    return tone(WOODD, 1.2 + 3.0 * L + (wn(1, u * 6, w_ * 6) - 0.5) * 0.7, x, y)
def lwall(x, y, s, t, z, wp):
    X, Y, Z = wp
    if in_window(Z, Y) is not None: return None
    L = lit(X, Y, Z, (1, 0, 0)); A = ao(X, Y, Z, 'left')
    if 20.5 < Z < 21.9 and 6.2 < Y < 9.6: return fg(notice((Z - 20.5) / 1.4, (Y - 6.2) / 3.4, L, x, y, 1), z)
    if 27.0 < Z < 28.6 and 7.0 < Y < 10.4: return fg(notice((Z - 27.0) / 1.6, (Y - 7.0) / 3.4, L, x, y, 2), z)
    vn = vine_at(Z, Y, 1, x, y, L)
    if vn is not None: return fg(vn, z)
    b = bare(Z, Y, ((21.0, 23.5, 1.6, 2.4), (28.2, 13.0, 1.2, 1.8), (17.0, 2.2, 1.4, 1.0), (13.5, 21.0, 1.8, 3.0), (24.5, 2.6, 1.6, 1.2)))
    if b is not None: return fg(bare_px(b, Z, Y, x, y, L, z), z)
    return fg(plaster(X, Y, Z, x, y, Z, 1, L, A), z)
rs.quad((-WX, 0, 3), (-WX, 0, ZB), (-WX, CH, 3), lwall, cls='wall', cut=True)

def outside(x, y):
    """the yard seen through the window: the tenement opposite in the haze, the overcast sky"""
    dx, dy = ray(x, y)
    if dx < 0:
        t_ = -52.0 / dx; Yh = CAMH + dy * t_; Zh = t_
        roof = 30.0 + 2.5 * math.sin(Zh * 0.21) + (3.0 if (Zh % 17) < 2.2 else 0)
        if Yh < roof:
            fz, fy = (Zh / 3.4) % 1, (Yh / 4.2) % 1
            win = 0.3 < fz < 0.75 and 0.25 < fy < 0.8
            v = 2.6 + (Yh / 30.0) * 0.8 + (wn(1, Zh * 0.4, Yh * 0.4) - 0.5) * 0.6
            c = tone(FACADE, v - (1.6 if win else 0) - (0.8 if fy < 0.12 else 0), x, y)
            return mix(c, SKYW[4], 0.35)
    v = 4.0 + max(0.0, -dy) * 9 + (wn(3, dx * 7, dy * 30) - 0.5) * 1.0
    return tone(SKYW, v + 0.8, x, y)
def window_sh(k):
    z0, z1 = WINS[k]
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u, w_ = (Z - z0) / (z1 - z0), (Y - WY0) / (WY1 - WY0)
        fr = 0.32 * z_of(z) / (z1 - z0)
        if u < fr or u > 1 - fr or w_ < fr * (z1 - z0) / (WY1 - WY0) or w_ > 1 - fr * (z1 - z0) / (WY1 - WY0):
            return fg(tone(WOODD, 1.6, x, y), z)
        cu, cw = u * 3, w_ * 6
        mu = 0.3 / (z1 - z0); mw = 0.6 / (WY1 - WY0)
        if cu % 1 < mu or cw % 1 < mw: return fg(tone(WOODD, 1.0, x, y), z)
        pi, pj = int(cu), int(cw)
        c = outside(x, y)
        broken = h32(pi, pj, k, 41) % 5 == 0
        g = VINES.get(1)
        if g is not None and (grid_at(g[1], Z, Y) is not None or grid_at(g[0], Z, Y) is not None):
            return tone(LEAF, 0.4 + (0.8 if grid_at(g[1], Z, Y) is not None else 0), x, y)      # vines hanging across, against the light
        iv = wn(0, Z * 1.4 + k * 9, Y * 1.4)                                                  # ivy outside, against the light
        if Y > 15.5 + 2.0 * wn(1, Z * 0.7, 1.0 + k) and iv > 0.55: return tone(LEAF, 0.8 + (iv - 0.55) * 4, x, y)
        if not broken:
            fv = cw % 1
            c = mix(c, (236, 190, 100), 0.4)                                                   # yellowed, nicotine-stained glass
            c = mix(c, (96, 74, 38), 0.04 + 0.34 * max(0.0, 0.32 - fv) / 0.32)                 # dirt settled at the bottom of each pane
            if wn(2, Z * 4.0, Y * 0.6) > 0.66: c = mix(c, (90, 72, 40), 0.3)                   # streaks
        return c
    return sh
for k, (z0, z1) in enumerate(WINS):
    rs.quad((-WX - 0.5, WY0, z0), (-WX - 0.5, WY0, z1), (-WX - 0.5, WY1, z0), window_sh(k), cls='emit')
    def reveal(x, y, s, t, z, wp): return fg(tone(PLAST, 1.6 + 4.0 * lit(*wp, (0, 0, 1)), x, y), z)
    rs.quad((-WX, WY0, z1), (-WX - 0.5, WY0, z1), (-WX, WY1, z1), reveal, cls='wall')
    rs.quad((-WX, WY1, z0), (-WX - 0.5, WY1, z0), (-WX, WY1, z1), reveal, cls='wall')
    sill = lambda x, y, s, t, z, wp: fg(tone(WOODD, 1.6 + 3.6 * lit(*wp, (0, 1, 0)), x, y), z)
    rs.box(-WX - 0.5, -WX + 0.45, WY0 - 0.35, WY0, z0 - 0.4, z1 + 0.4, sill, sill, top=sill, cls='prop')
    def rad(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = 0.4 + 3.0 * lit(X, Y, Z, (1, 0, 0)) + (0.8 if (Z * 2.6) % 1 < 0.3 else -0.3) + (0.4 if Y > 3.6 else 0)
        if wn(1, Z * 5, Y * 0.6) > 0.74 and Y < 3.4: return fg(tone(RUSTY, 0.6 + v * 0.4, x, y), z)
        return fg(tone(STEEL, v, x, y), z)
    rs.box(-WX + 0.05, -WX + 0.75, 0.9, 3.9, max(z0 + 0.6, 17.6), z1 - 0.6, rad, rad, top=rad, cls='prop')

# ---------------------------------------------------------------------------------------------------- the back wall + the doorway
def back(x, y, s, t, z, wp):
    X, Y, Z = wp
    if DOOR[0] < X < DOOR[1] and Y < DOOR[3]: return None
    L = lit(X, Y, Z, (0, 0, -1)); A = ao(X, Y, Z, 'back')
    if -22.6 < X < -20.4 and 7.6 < Y < 10.6:                                                 # a fuse box, its door gone
        if abs(X + 21.5) < 0.9 and 7.9 < Y < 10.3:
            if (Y * 3) % 1 < 0.25 and abs(X + 21.5) < 0.7: return fg((34, 30, 22), z)
            return fg(tone(STEEL, 0.2 + 1.6 * L, x, y), z)
        return fg(tone(STEEL, 0.8 + 3.0 * L + (0.6 if Y > 10.4 else 0), x, y), z)
    vn = vine_at(X, Y, 2, x, y, L)
    if vn is not None: return fg(vn, z)
    b = bare(X, Y, ((-19.5, 21.0, 2.4, 1.8), (-1.2, 15.5, 1.3, 2.2), (-24.0, 4.0, 1.5, 2.0), (-11.0, 17.0, 1.6, 1.2)))
    if b is not None: return fg(bare_px(b, X, Y, x, y, L, z), z)
    return fg(plaster(X, Y, Z, x, y, X, 2, L, A), z)
rs.quad((-WX, 0, ZB), (XE + 0.5, 0, ZB), (-WX, CH, ZB), back, cls='wall', cut=True)
def frame(x, y, s, t, z, wp): return fg(tone(WOODD, 0.8 + 3.6 * lit(*wp, (0, 0, -1)) + (0.6 if t > 0.5 else 0), x, y), z)
rs.box(DOOR[0] - 0.45, DOOR[0], 0, DOOR[3] + 0.45, ZB - 0.25, ZB, frame, frame, cls='prop')
rs.box(DOOR[1], DOOR[1] + 0.45, 0, DOOR[3] + 0.45, ZB - 0.25, ZB, frame, frame, cls='prop')
rs.box(DOOR[0] - 0.45, DOOR[1] + 0.45, DOOR[3], DOOR[3] + 0.5, ZB - 0.25, ZB, frame, frame, bottom=frame, cls='prop')
rs.box(DOOR[0], DOOR[1], DOOR[2], DOOR[2] + 0.3, ZB - 0.15, ZB, frame, frame, bottom=frame, cls='prop')
def transom(x, y, s, t, z, wp):
    X, Y, Z = wp
    u = (X - DOOR[0]) / (DOOR[1] - DOOR[0])
    if (u * 3) % 1 < 0.07: return tone(WOODD, 1.0, x, y)
    if int(u * 3) == 1: return None                                                          # a pane gone
    return mix(tone(GREENL, 1.2 + (Y - DOOR[2]) * 0.4, x, y), (60, 54, 34), 0.25)
rs.quad((DOOR[0], DOOR[2] + 0.3, ZB - 0.1), (DOOR[1], DOOR[2] + 0.3, ZB - 0.1), (DOOR[0], DOOR[3], ZB - 0.1), transom, cls='prop', cut=True)
# one leaf still hangs on the left jamb, swung back almost square to the wall (the other lies in the foreground)
HING = (DOOR[0] + 0.1, ZB - 0.2); LEAFW = DOOR[1] - DOOR[0]
ang = math.radians(76)
LX, LZ = HING[0] + math.cos(ang) * LEAFW * 0.98, HING[1] - math.sin(ang) * LEAFW * 0.98
def leaf(x, y, s, t, z, wp):
    X, Y, Z = wp
    L = lit(X, Y, Z, (math.sin(ang), 0, -math.cos(ang)))
    if 0.08 < s < 0.92 and 0.55 < t < 0.92:
        if abs((s - 0.5) * 2.2 - (t - 0.7) * 3) < 0.04 or abs(s - 0.3 - (t - 0.6) * 0.5) < 0.03: return tone(GLASSD, 1.0, x, y)
        return mix(tone(PLAST, 2.4 + 4.0 * L, x, y), (60, 64, 46), 0.4)
    if s < 0.05 or s > 0.95 or t < 0.03 or abs(t - 0.53) < 0.025 or t > 0.96: return tone(WOODD, 1.0 + 3.6 * L, x, y)
    v = 1.6 + 4.4 * L + (wn(1, s * 3, t * 20) - 0.5) * 0.7
    if 0.15 < s < 0.85 and 0.08 < t < 0.48 and (abs(s - 0.15) < 0.02 or abs(s - 0.85) < 0.02 or abs(t - 0.08) < 0.015 or abs(t - 0.48) < 0.015): v -= 1.0
    return tone(WOODD, v, x, y)
rs.quad((HING[0], 0.15, HING[1]), (LX, 0.15, LZ), (HING[0], DOOR[2] - 0.1, HING[1]), leaf, cls='prop')
rs.line3((LX + 0.12, 4.1, LZ + 0.5), (LX + 0.32, 4.1, LZ + 0.9), lambda x, y, s, t, z, wp: STEEL[5], w=0.12)
def clock(x, y, s, t, z, wp):
    d = math.hypot(s, t)
    if d > 0.84: return fg(tone(WOODD, 1.2 - t, x, y), z)
    if abs(s * 0.6 - t * 0.8 - 0.1) < 0.03 and s > -0.2: return fg(PLAST[2], z)                  # a crack in the glass
    for (an, ln, w_) in ((math.radians(200), 0.45, 0.07), (math.radians(-60), 0.68, 0.045)):      # twenty to five, for ever
        px_, py_ = math.cos(an), math.sin(an)
        pr = s * px_ + t * py_
        if 0 < pr < ln and abs(s * py_ - t * px_) < w_: return (20, 18, 13)
    a = math.atan2(t, s)
    if d > 0.66 and abs(((a / (2 * math.pi)) * 12) % 1 - 0.5) > 0.44: return (32, 28, 20)
    return fg(tone(PLAST, 4.4 - d * 2, x, y), z)
rs.disc(-6.4, 14.4, ZB - 0.2, 0.95, clock)

# beyond: the landing, the stairwell's far wall in the Hall's green light, the handrail dropping away
def landing(x, y, s, t, z, wp):
    X, _, Z = wp
    return tone(SCREED, 1.0 + (Z - ZB) * 0.25 + (wn(0, X * 2, Z * 2) - 0.5) * 0.6, x, y)
rs.quad((DOOR[0] - 3, 0, ZB), (DOOR[1] + 3, 0, ZB), (DOOR[0] - 3, 0, 33.0), landing, cls='ground')
def stairwall(x, y, s, t, z, wp):
    X, Y, Z = wp
    g = max(0.0, 1 - (Y + 2.0) / 15.0)
    v = 1.0 + 5.6 * g * g + (wn(1, X * 1.2, Y * 1.2) - 0.5) * 0.6
    if (Y + 0.3 * X) % 3.0 < 0.12: v -= 0.6
    return tone(GREENL, v, x, y)
rs.quad((DOOR[0] - 6, -12, 37.5), (DOOR[1] + 6, -12, 37.5), (DOOR[0] - 6, 14, 37.5), stairwall, cls='emit')
for sx in (DOOR[0] - 1.2, DOOR[1] + 1.2):
    rs.quad((sx, -12, ZB + 0.3), (sx, -12, 37.5), (sx, 14, ZB + 0.3),
            lambda x, y, s, t, z, wp: tone(GREENL, 0.4 + 2.6 * max(0.0, 1 - (wp[1] + 4) / 15.0) ** 2, x, y), cls='wall')
def rail(x, y, s, t, z, wp): return tone(STEEL, 1.0 + 1.6 * (1 - t), x, y)
rs.line3((DOOR[0] + 0.6, 3.4, 33.2), (DOOR[1] + 1.0, -2.6, 36.0), rail, w=0.18)
rs.line3((DOOR[0] + 0.6, 0.0, 33.0), (DOOR[0] + 0.6, 3.5, 33.0), rail, w=0.2)
rs.line3((DOOR[0] + 2.6, -1.2, 34.0), (DOOR[0] + 2.6, 2.4, 34.0), rail, w=0.16)

# ---------------------------------------------------------------------------------------------------- the ceiling
def in_hole(X, Z, pad=0.0):
    return ((X - BREACH[0]) / (BREACH[2] + pad)) ** 2 + ((Z - BREACH[1]) / (BREACH[3] + pad)) ** 2 + \
        (wn(2, X * 1.3, Z * 1.3) - 0.5) * 0.9 + (wn(4, X * 4.0, Z * 0.6) - 0.5) * 0.7
def ceil_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    hole = in_hole(X, Z)
    if hole < 1.0: return None
    L = lit(X, Y, Z, (0, -1, 0)); A = ao(X, Y, Z, 'ceil')
    bd = math.floor(Z / 0.75); fb = (Z / 0.75) % 1
    if h32(bd, int(math.floor(X / 6.0)), 11) % 5 == 0 and wn(1, X * 0.4, Z * 0.4) > 0.35: return None   # a board gone
    v = 0.3 + 2.4 * L + (h32(bd, 3) % 3) * 0.25 + (wn(0, X * 0.3, Z * 3.0) - 0.5) * 0.6 - 0.8 * A
    if fb < 0.9 * z * z / (F * (CH - CAMH)) / 0.75 + 0.03: v -= 0.8
    if wn(3, X * 0.25, Z * 0.25) > 0.62: v -= 0.6
    if hole < 1.35: v -= 0.8
    return fg(tone(TIMBER, v, x, y), z)
rs.quad((-WX, CH, 3), (XR, CH, 3), (-WX, CH, ZB), ceil_sh, cls='ceil', cut=True)
def void(x, y, s, t, z, wp):
    X, Y, Z = wp
    k = (CH - CAMH) / (Y - CAMH); Xc, Zc = X * k, Z * k                                          # back down the view ray to the boards
    if ((Xc - BREACH[0]) / (BREACH[2] + 0.5)) ** 2 + ((Zc - BREACH[1]) / (BREACH[3] + 0.5)) ** 2 < 1.0:
        if (X - BREACH[0] + 1.1) % 2.6 < 0.45: return tone(TIMBER, 0.4 + (0.6 if (X - BREACH[0] + 1.1) % 2.6 < 0.12 else 0), x, y)
        if (Z % 1.1) < 0.14 and wn(1, X * 0.8, Z) > 0.4: return tone(TIMBER, 0.8, x, y)
        if wn(2, X * 2.0, Z * 2.0) > 0.6: return tone(LEAF, 0.6 + (wn(2, X * 2.0, Z * 2.0) - 0.6) * 6, x, y)
        return tone(SKYW, 4.0 + (wn(3, X, Z) - 0.5) * 1.4, x, y)
    return None
rs.quad((-WX, CH + 3.5, 3), (XR, CH + 3.5, 3), (-WX, CH + 3.5, ZB), void, cls='emit', cut=True)
rs.quad((-WX, CH + 0.1, 3), (XR, CH + 0.1, 3), (-WX, CH + 0.1, ZB),
        lambda x, y, s, t, z, wp: (8, 7, 5) if ((wp[0] - BREACH[0]) / (BREACH[2] + 0.5)) ** 2 + ((wp[2] - BREACH[1]) / (BREACH[3] + 0.5)) ** 2 > 1.0 else None,
        cls='ceil', cut=True)
def bounce(X, Z):
    """warm light thrown up from the sunlit floor and the windows onto the undersides of the ceiling timbers"""
    return 0.55 * math.exp(-((X + 12.0) / 11.0) ** 2 - ((Z - 19.0) / 8.0) ** 2) + 0.35 * math.exp(-((X + WX) / 6.0) ** 2)
def girder(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 0.6 + 2.8 * lit(X, Y, Z, (0, -1, 0)) + 2.6 * bounce(X, Z) + (wn(0, Z * 0.4 + X, Y * 4) - 0.5) * 0.6 + (0.7 if Y < CH - 0.9 else 0)
    return fg(tone(TIMBER, v, x, y), z)
for gx in (-24.0, -17.6, -11.2, -4.8):
    rs.box(gx - 0.45, gx + 0.45, CH - 1.6, CH, 3.0, ZB, girder, girder, bottom=girder, cls='ceil')
rs.box(-WX, XE, CH - 1.3, CH, ZB - 0.9, ZB, girder, girder, bottom=girder, cls='ceil')        # the wall plates
rs.box(XE, XR, CH - 1.3, CH, ZG - 0.9, ZG, girder, girder, bottom=girder, cls='ceil')
# joists across the room on the girders, cut where the roof came in; a few broken ends hanging
for k in range(17):
    jz = 4.6 + k * 1.55
    if jz > ZB - 1.2: break
    segs = [(-WX, XE if jz > ZG - 0.4 else XR)]
    if BREACH[1] - BREACH[3] - 0.4 < jz < BREACH[1] + BREACH[3] + 0.3:
        segs = [(-WX, BREACH[0] - BREACH[2] - 0.2 - (h32(k, 5) % 3) * 0.3), (BREACH[0] + BREACH[2] + 0.3 + (h32(k, 6) % 3) * 0.3, XE)]
    for (a, b) in segs:
        rs.box(a, b, CH - 0.85, CH - 0.05, jz, jz + 0.42, girder, girder, bottom=girder, cls='ceil')
# broken boards and joist ends hanging from the breach
for k, (bx, bz, dx, dz, ln) in enumerate(((-16.4, 22.0, -0.4, 0.5, 4.2), (-12.6, 24.6, 0.6, 0.2, 3.0), (-15.0, 25.0, 0.1, 0.4, 2.2),
                                          (-13.0, 21.6, 0.9, -0.3, 5.0), (-16.9, 24.1, -0.5, 0.2, 3.4))):
    def hb(x, y, s, t, z, wp, k=k): return fg(tone(TIMBER, 0.8 + 2.0 * (1 - t) + (wn(1, s * 9, t * 9 + k) - 0.5), x, y), z)
    rs.quad((bx, CH, bz), (bx + 0.75, CH, bz), (bx + dx, CH - ln, bz + dz), hb, cls='prop')
# sheet-metal ducts on hangers: one along the room, one across the back
def duct(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 1.0 + 3.0 * lit(X, Y, Z, (0, -1, -0.3)) + 2.0 * bounce(X, Z) + (0.8 if t > 0.82 else 0)
    if ((Z if abs(wp[0] + 20.5) < 1.5 else X) / 2.6) % 1 < 0.05: v -= 1.0                     # the seams
    if wn(1, X * 0.7 + Z * 0.7, Y * 2) > 0.7: return fg(tone(RUSTY, 0.6 + v * 0.4, x, y), z)
    return fg(tone(STEEL, v, x, y), z)
rs.box(-22.0, -19.0, CH - 5.2, CH - 3.0, 3.0, ZB - 1.0, duct, duct, bottom=duct, cls='prop')
rs.box(-WX + 0.3, XE - 0.2, CH - 4.4, CH - 2.8, ZB - 3.4, ZB - 2.0, duct, duct, bottom=duct, cls='prop')
for hz in (6.0, 11.0, 16.0, 21.0, 26.0):
    for hx in (-21.8, -19.2): rs.line3((hx, CH - 1.6, hz), (hx, CH - 3.0, hz), lambda x, y, s, t, z, wp: fg(STEEL[1], z), w=0.08)
for hx in (-22.0, -14.0, -6.0, -1.0):
    rs.line3((hx, CH - 0.8, ZB - 2.7), (hx, CH - 2.8, ZB - 2.7), lambda x, y, s, t, z, wp: fg(STEEL[1], z), w=0.08)
# cables sagging between the girders, one dangling loose
def cab3(x, y, s, t, z, wp): return fg((34, 32, 26) if (x + y) % 3 == 0 else CABLE[2], z)
for (a, b, sag) in (((-24.0, CH - 1.6, 9.0), (-17.6, CH - 1.6, 12.0), 2.2), ((-17.6, CH - 1.6, 13.0), (-11.2, CH - 1.6, 15.5), 3.0),
                    ((-11.2, CH - 1.6, 17.0), (-4.8, CH - 1.6, 19.5), 2.4), ((-24.0, CH - 1.6, 19.0), (-17.6, CH - 1.6, 26.0), 3.6),
                    ((-4.8, CH - 1.6, 9.0), (1.0, CH - 1.0, 14.0), 2.6), ((-11.2, CH - 1.6, 26.0), (-4.8, CH - 1.6, 27.5), 1.6)):
    rs.line3(a, b, cab3, w=0.08, sag=sag)
rs.line3((-4.8, CH - 1.6, 16.0), (-5.6, 18.0, 16.4), cab3, w=0.08, sag=-0.6)
rs.line3((-11.2, CH - 1.6, 22.0), (-10.2, 15.5, 21.6), cab3, w=0.07, sag=-0.4)

# pipes along the walls, on brackets
def pipe(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 0.6 + 3.0 * lit(X, Y, Z, (0.5, 0.5, -0.7)) + (1.2 if (x + y) % 4 == 0 else 0)
    if wn(1, X * 0.8 + Z * 0.8, Y) > 0.68: return fg(tone(RUSTY, 0.6 + v * 0.4, x, y), z)
    return fg(tone(STEEL, v, x, y), z)
rs.line3((-WX, 13.6, ZB - 0.35), (XE, 13.6, ZB - 0.35), pipe, w=0.38)                         # along the back wall
rs.line3((-WX, 14.3, ZB - 0.3), (XE, 14.3, ZB - 0.3), pipe, w=0.26)
for px_ in (-23.0, -13.6, 0.6):
    rs.line3((px_, CH - 1.0, ZB - 0.35), (px_, 0.0, ZB - 0.35), pipe, w=0.32)
rs.line3((-WX + 0.35, 22.0, 3.0), (-WX + 0.35, 22.0, ZB), pipe, w=0.4)                           # along the left wall
rs.line3((-WX + 0.35, 22.0, 21.2), (-WX + 0.35, 3.9, 21.2), pipe, w=0.3)
rs.line3((34.6, CH - 1.0, ZG - 0.4), (34.6, 0.0, ZG - 0.4), pipe, w=0.55)                        # a cast-iron downpipe on the graffito wall
for by in (4.0, 11.0, 18.0, 25.0):
    rs.box(34.2, 35.0, by, by + 0.3, ZG - 0.75, ZG - 0.02, pipe, pipe, cls='prop')

# ---------------------------------------------------------------------------------------------------- ivy through the breach
def ivy_leaf(X, Y, Z, r, seed):
    lv = 0.8 + (seed % 3) * 0.45 + 3.0 * lit(X, Y, Z, (0, 0.3, -1))
    flip = 1 if seed % 2 else -1
    def sh(x, y, s, t, z, wp):
        s *= flip
        if not ((s / 0.8) ** 2 + (t + 0.15) ** 2 < 1 and abs(s) < (1.05 - t) * 0.62): return None
        v = lv - t * 1.0 - s * 0.7
        if abs(s) < 0.09 and t > -0.6: v -= 0.8
        return fg(tone(LEAF, v, x, y), z)
    rs.disc(X, Y, Z, r, sh)
def ivy_strand(X0, Z0, Y0, length, seed, sway=0.6, dens=3):
    pts = []
    for k in range(int(length / 0.35)):
        Y = Y0 - k * 0.35
        X = X0 + sway * math.sin(k * 0.23 + seed) * min(1.0, k / 6)
        Z = Z0 + 0.3 * math.sin(k * 0.17 + seed * 2)
        pts.append((X, Y, Z))
    for (a, b) in zip(pts, pts[1:]):
        rs.line3(a, b, lambda x, y, s, t, z, wp: fg(LEAF[0], z), w=0.07, n=3)
    for k, (X, Y, Z) in enumerate(pts):
        if h32(k, seed, 3) % 5 >= dens: continue
        side = 1 if h32(k, seed) % 2 else -1
        ivy_leaf(X + side * 0.22, Y - 0.08, Z - 0.05, 0.2 + (h32(k, seed, 4) % 4) * 0.045, h32(k, seed, 2))
irng = random.Random(31)
for k in range(13):
    a = irng.random() * 6.28; r_ = 0.6 + irng.random() * 1.4
    ivy_strand(BREACH[0] + math.cos(a) * r_ * BREACH[2] * 0.8, BREACH[1] + math.sin(a) * r_ * BREACH[3] * 0.8, CH - 0.2,
               3.0 + irng.random() * 14.0, 30 + k, dens=4)
for k, (Z0, ln) in enumerate(((19.0, 7.5), (16.2, 4.0), (25.6, 6.5), (23.0, 3.5), (17.6, 2.5))):    # in through the broken panes
    ivy_strand(-WX + 0.35, Z0, WY1 - 0.3, ln, 50 + k, sway=0.25)
def climber(X0, Z0, height, seed):
    pts = []; X = X0
    for k in range(int(height / 0.3)):
        Y = 0.2 + k * 0.3; X += 0.12 * math.sin(k * 0.4 + seed)
        pts.append((X, Y, Z0))
    for (a, b) in zip(pts, pts[1:]): rs.line3(a, b, lambda x, y, s, t, z, wp: fg(LEAF[0], z), w=0.06, n=3)
    for k, (X, Y, Z) in enumerate(pts):
        if h32(k, seed, 3) % 4 == 0: continue
        for side in (-1, 1):
            if h32(k, seed, side + 5) % 3 == 0: continue
            ivy_leaf(X + side * 0.24, Y, Z - 0.12, 0.2 + (h32(k, seed, side) % 4) * 0.04 * (1 - Y / (height + 2)), h32(k, seed, side, 9))
for k, (X0, hh) in enumerate(((2.0, 9.5), (3.1, 6.0), (4.4, 3.5), (5.6, 2.2), (6.8, 1.4))):
    climber(X0, ZG - 0.15, hh, 70 + k)

# dead enamel lamps on long cords
def lamp(X, Z, Yl, tilt=0.0):
    rs.line3((X, CH - 0.8, Z), (X + tilt, Yl + 0.9, Z), lambda x, y, s, t, z, wp: fg(CABLE[1], z), w=0.06)
    def shade(x, y, s, t, z, wp):
        if t < -0.55: return fg(tone(ENAMEL, 1.0 - s, x, y), z) if abs(s) < 0.22 else None
        if t <= 0.1:
            if abs(s) > 0.3 + 0.7 * ((t + 0.55) / 0.65) ** 0.6: return None
            v = 2.0 - t * 1.2 - s * 1.6 + (0.9 if -0.45 < s < -0.25 else 0)
            if wn(1, s * 5 + X, t * 5) > 0.76: return fg(tone(STEEL, 0.6, x, y), z)
            return fg(tone(ENAMEL, v, x, y), z)
        if t < 0.42:
            if (s / 1.0) ** 2 + ((t - 0.2) / 0.22) ** 2 > 1: return None
            if (s / 0.86) ** 2 + ((t - 0.22) / 0.16) ** 2 > 1: return fg(tone(ENAMEL, 2.6 - s, x, y), z)
            if abs(s) < 0.14 and t > 0.16: return (16, 14, 10)
            return fg(tone(ENAMEL, 0.3, x, y), z)
        return None
    rs.disc(X + tilt, Yl, Z, 1.0, shade)
lamp(-19.0, 20.0, 15.0); lamp(-8.6, 26.5, 17.0, 0.0); lamp(-2.4, 19.0, 14.0, 0.5)

# ---------------------------------------------------------------------------------------------------- furniture
def wood(v0, grain='x', n=(0, 0.6, -0.8)):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        g = (X if grain == 'x' else Z)
        v = v0 + 3.4 * lit(X, Y, Z, n) + (wn(1, g * 0.6, Y * 12.0 if grain != 'top' else Z * 8.0) - 0.5) * 0.9
        return fg(tone(WOODD, v, x, y), z)
    return sh
def drawers_front(x0, x1):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = 1.2 + 3.4 * lit(X, Y, Z, (0, 0, -1)) + (wn(1, X * 0.6, Y * 12) - 0.5) * 0.8
        fy = (Y / 0.84) % 1
        if fy < 0.06 * z_of(z) or s < 0.04 or s > 0.96: v -= 1.4
        if abs(fy - 0.62) < 0.07 and abs(s - 0.5) < 0.12: return fg((96, 74, 38) if (x + y) % 3 else (66, 50, 26), z)
        return fg(tone(WOODD, v, x, y), z)
    return sh
def crt(X, Y, Z, on, seed, w=1.6):
    case = lambda x, y, s, t, z, wp: fg(tone(BEIGE, 0.8 + 3.8 * lit(*wp, (0, 0.5, -0.8)) + (0.6 if t > 0.8 else 0), x, y), z)
    rs.box(X - w / 2, X + w / 2, Y, Y + w * 0.88, Z, Z + w * 0.7, case, case, top=case, cls='prop')
    rs.box(X - w * 0.33, X + w * 0.33, Y + 0.1, Y + w * 0.7, Z + w * 0.7, Z + w * 1.15, case, case, top=case, cls='prop')
    def scr(x, y, s, t, z, wp):
        if s < 0.1 or s > 0.9 or t < 0.12 or t > 0.9: return tone(BEIGE, 1.4 + 2.6 * lit(*wp, (0, 0, -1)), x, y)
        if on:
            row = int((1 - t) * 9)
            if row % 2 == 0 and 0.16 < s < 0.2 + (h32(row, seed) % 6) * 0.11: return CRT[7]
            if row == 7 and 0.16 < s < 0.22 and (x // 2) % 2: return CRT[8]
            return CRT[3] if (x + y) % 2 else CRT[4]
        v = 0.6 + (1.6 if abs((s - 0.3) - (0.8 - t) * 0.6) < 0.08 else 0) + (wn(2, s * 4 + seed, t * 4) - 0.5) * 0.6
        return tone(GLASSD, v, x, y)
    rs.quad((X - w / 2 + 0.05, Y + 0.08, Z - 0.03), (X + w / 2 - 0.05, Y + 0.08, Z - 0.03), (X - w / 2 + 0.05, Y + w * 0.82, Z - 0.03), scr,
            cls='emit' if on else 'prop')
    kb = lambda x, y, s, t, z, wp: fg(tone(BEIGE, 1.6 + 2.0 * lit(*wp, (0, 1, 0)) + (1.0 if (x + y) % 2 and t > 0.3 else 0), x, y), z)
    rs.box(X - w * 0.45, X + w * 0.45, 2.8, 2.95, Z - 1.3, Z - 0.5, kb, kb, top=kb, cls='prop')
def paper_at(fx, fz, Y, seed, size=0.42):
    a = (h32(seed, 3) % 628) / 100.0; c, s_ = math.cos(a) * size, math.sin(a) * size
    lv = 1.0 + (h32(seed, 4) % 3) * 0.5
    rs.quad((fx - c, Y + 0.02, fz - s_), (fx + s_, Y + 0.02, fz - c), (fx - s_, Y + 0.02, fz + c),
            lambda x, y, s, t, z, wp, lv=lv: fg(tone(PAPER, lv + 5.0 * lit(*wp, (0, 1, 0)) - (0.9 if (t * 8) % 1 < 0.2 and 0.15 < s < 0.85 else 0), x, y), z), cls='prop')
def papers(X0, X1, Z0, Z1, Y, n, seed):
    for k in range(n):
        fx = X0 + (h32(k, seed, 1) % 100) / 100 * (X1 - X0); fz = Z0 + (h32(k, seed, 2) % 100) / 100 * (Z1 - Z0)
        paper_at(fx, fz, Y + k * 0.004, h32(k, seed, 7))
def drift(cx, cz, rx, rz, n, seed):
    """a drift of paper blown into a heap: dense in the middle, layered"""
    for k in range(n):
        r_ = math.sqrt((h32(k, seed, 1) % 1000) / 1000.0); a = (h32(k, seed, 2) % 628) / 100.0
        paper_at(cx + math.cos(a) * r_ * rx, cz + math.sin(a) * r_ * rz, 0.01 + (1 - r_) * 0.18 + k * 0.002, h32(k, seed, 3), 0.36 + (h32(k, seed, 4) % 3) * 0.06)
def desk(x0, x1, z0, z1, ped, seed, drawer_out=False):
    top = 2.75
    rs.box(x0, x1, top - 0.2, top, z0, z1, wood(1.6), wood(1.2), top=wood(2.2, 'top', (0, 1, 0)), cls='prop')
    px0, px1 = (x0 + 0.1, x0 + 2.2) if ped == 'left' else (x1 - 2.2, x1 - 0.1)
    rs.box(px0, px1, 0.1, top - 0.2, z0 + 0.15, z1 - 0.2, drawers_front(px0, px1), wood(0.8), cls='prop')
    lx0, lx1 = (x1 - 0.45, x1 - 0.15) if ped == 'left' else (x0 + 0.15, x0 + 0.45)
    rs.box(lx0, lx1, 0, top - 0.2, z0 + 0.15, z0 + 0.45, wood(1.0), wood(0.6), cls='prop')
    rs.box(lx0, lx1, 0, top - 0.2, z1 - 0.5, z1 - 0.2, wood(0.6), wood(0.4), cls='prop')
    rs.quad((x0 + 0.3, 0.6, z1 - 0.25), (x1 - 0.3, 0.6, z1 - 0.25), (x0 + 0.3, top - 0.2, z1 - 0.25), wood(0.2), cls='prop')
    if drawer_out:
        rs.box(px0 + 0.12, px1 - 0.12, 1.0, 1.62, z0 - 0.9, z0 + 0.3, drawers_front(px0, px1), wood(1.0),
               top=lambda x, y, s, t, z, wp: fg(tone(PAPER, 1.6 + (t * 3 % 1 < 0.3) * 0.8, x, y), z), cls='prop')
    DESKS.append((x0, x1, z0, z1))
    return ((lx0 + lx1) / 2, z0 + 0.3)                                                          # the free front leg (roots climb it)
def chair(X, Z, face=1.0, tip=0.0):
    cloth = lambda x, y, s, t, z, wp: fg(tone(DADO, 0.6 + 3.2 * lit(*wp, (0, 0.3, -1)) + (wn(1, s * 5, t * 5) - 0.5) * 0.6, x, y), z)
    rs.box(X - 0.9, X + 0.9, 1.75, 2.05, Z - 0.8, Z + 0.8, cloth, cloth, top=cloth, cls='prop')
    bz = Z + 0.85 * face
    rs.quad((X - 0.85, 2.1, bz), (X + 0.85, 2.1, bz), (X - 0.85 + tip, 4.4, bz + 0.15 * face), cloth, cls='prop')
    rs.line3((X, 0.35, Z), (X, 1.75, Z), lambda x, y, s, t, z, wp: fg(STEEL[2], z), w=0.17)
    for a in range(5):
        an = a * 2 * math.pi / 5 + 0.3
        rs.line3((X, 0.35, Z), (X + math.cos(an) * 1.2, 0.12, Z + math.sin(an) * 1.2), lambda x, y, s, t, z, wp: fg(STEEL[1], z), w=0.16)
def tcl(x, y, s, t, z, wp): return fg(tone(DADO, 0.6 + 3.2 * lit(*wp, (0, 0.6, -0.8)) + (wn(1, s * 5, t * 5) - 0.5) * 0.6, x, y), z)
def tst(x, y, s, t, z, wp): return fg(tone(STEEL, 0.8 + 3.0 * lit(*wp, (0, 0.6, -0.8)) + (1.0 if t < 0.3 else 0), x, y), z)
def toppled_chair(CHX, CHZ, side=False):
    """a swivel chair on its back (the star base toward the camera), or on its side (the base toward +X)"""
    if not side:
        rs.box(CHX - 0.95, CHX + 0.95, 0.0, 0.3, CHZ + 0.4, CHZ + 2.6, tcl, tcl, top=tcl, cls='prop')
        rs.box(CHX - 0.9, CHX + 0.9, 0.15, 1.9, CHZ, CHZ + 0.35, tcl, tcl, top=tcl, cls='prop')
        rs.line3((CHX, 1.0, CHZ - 0.02), (CHX - 0.1, 1.0, CHZ - 1.1), tst, w=0.18)
        for a in range(5):
            an = a * 2 * math.pi / 5 + 0.4
            ex, ey = CHX - 0.1 + math.cos(an) * 1.15, 1.0 + math.sin(an) * 1.15
            rs.line3((CHX - 0.1, 1.0, CHZ - 1.1), (ex, max(0.12, ey), CHZ - 1.25), tst, w=0.16)
            rs.disc(ex, max(0.18, ey), CHZ - 1.3, 0.16, lambda x, y, s, t, z, wp: fg(tone(STEEL, 0.4 + (1.4 if t < -0.3 else 0), x, y), z))
    else:
        rs.box(CHX - 2.6, CHX - 0.4, 0.0, 0.3, CHZ - 0.95, CHZ + 0.95, tcl, tcl, top=tcl, cls='prop')
        rs.box(CHX - 0.35, CHX, 0.15, 1.9, CHZ - 0.9, CHZ + 0.9, tcl, tcl, top=tcl, cls='prop')
        rs.line3((CHX + 0.02, 1.0, CHZ), (CHX + 1.1, 1.0, CHZ + 0.1), tst, w=0.18)
        for a in range(5):
            an = a * 2 * math.pi / 5 + 0.2
            ez, ey = CHZ + 0.1 + math.cos(an) * 1.15, 1.0 + math.sin(an) * 1.15
            rs.line3((CHX + 1.1, 1.0, CHZ + 0.1), (CHX + 1.25, max(0.12, ey), ez), tst, w=0.16)
def plank(A, B, w, h, seed, v0=1.0):
    """a fallen ceiling plank from A to B (its bottom centre line), w wide, h thick"""
    dx, dz = B[0] - A[0], B[2] - A[2]; ln = math.hypot(dx, dz) or 1
    px, pz = -dz / ln * w / 2, dx / ln * w / 2
    def P(base, sd, up): return (base[0] + sd * px, base[1] + up * h, base[2] + sd * pz)
    obj = rs.obj()
    def sh(kv):
        def f(x, y, s, t, z, wp):
            v = v0 + kv + 3.0 * lit(*wp, (0, 1, 0)) + (wn(1, s * 30 + seed, t * 3) - 0.5) * 1.0
            if (s * 7 + seed) % 1 < 0.04: v -= 0.8                                               # a nail hole, a split
            return fg(tone(TIMBER, v, x, y), z)
        return f
    rs.quad(P(A, -1, 1), P(B, -1, 1), P(A, 1, 1), sh(1.0), obj=obj)
    rs.quad(P(A, -1, 0), P(B, -1, 0), P(A, -1, 1), sh(0.0), obj=obj)
    rs.quad(P(A, 1, 0), P(B, 1, 0), P(A, 1, 1), sh(0.0), obj=obj)
    rs.quad(P(A, -1, 0), P(A, 1, 0), P(A, -1, 1), sh(-0.4), obj=obj)
    rs.quad(P(B, -1, 0), P(B, 1, 0), P(B, -1, 1), sh(-0.4), obj=obj)
def cabinet(x0, x1, z0, z1, hh, seed, drawer=None):
    def cab(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = 0.8 + 3.6 * lit(X, Y, Z, (0, 0.3, -1)) + (wn(1, X * 2 + seed, Y * 2) - 0.5) * 0.5
        fy = (Y / (hh / 4)) % 1
        if fy < 0.06: v -= 1.2
        if abs(fy - 0.7) < 0.06 and abs(s - 0.5) < 0.13: v += 2.0
        if abs(fy - 0.45) < 0.08 and abs(s - 0.5) < 0.18: return fg(tone(PAPER, 1.6, x, y), z)
        c = tone(STEEL, v, x, y)
        if wn(2, X * 3 + seed, Y * 0.8) > 0.76: c = tone(RUSTY, 0.6 + v * 0.5, x, y)
        return fg(c, z)
    def side(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = 0.6 + 3.4 * lit(X, Y, Z, (1 if X < 0 else -1, 0, 0)) + (wn(1, Z * 2 + seed, Y * 2) - 0.5) * 0.5
        if wn(2, Z * 2 + seed, Y * 0.6) > 0.76: return fg(tone(RUSTY, 0.6 + v * 0.5, x, y), z)
        return fg(tone(STEEL, v, x, y), z)
    rs.box(x0, x1, 0, hh, z0, z1, cab, side, top=lambda x, y, s, t, z, wp: fg(tone(STEEL, 1.6 + 3.0 * lit(*wp, (0, 1, 0)), x, y), z), cls='prop')
    if drawer:
        y0 = drawer
        rs.box(x0 + 0.1, x1 - 0.1, y0, y0 + hh / 4 - 0.15, z0 - 1.4, z0, lambda x, y, s, t, z, wp: fg(tone(STEEL, 1.2, x, y), z),
               lambda x, y, s, t, z, wp: fg(STEEL[1], z), top=lambda x, y, s, t, z, wp: fg(tone(PAPER, 1.8 + (y % 2) * 0.6, x, y), z), cls='prop')

# desk A: near left, the lit terminal (the Core still feeds the Bureau's lines)
LEGS = []
LEGS.append(desk(-22.0, -15.2, 16.6, 19.0, 'left', 1, drawer_out=True))
crt(-17.0, 2.75, 17.6, True, 3)
papers(-21.6, -19.0, 16.9, 18.6, 2.75, 5, 11)
rs.box(-20.0, -19.5, 2.75, 3.25, 17.1, 17.6, lambda x, y, s, t, z, wp: fg(tone(PLAST, 3.4, x, y), z), lambda x, y, s, t, z, wp: fg(PLAST[2], z),
       top=lambda x, y, s, t, z, wp: (14, 11, 8), cls='prop')
chair(-18.0, 15.6, face=-1.0)
LEGS.append(desk(-12.0, -6.4, 21.4, 23.6, 'right', 2))
crt(-10.0, 2.75, 22.1, False, 4)
papers(-8.8, -6.8, 21.6, 23.2, 2.75, 4, 12)
LEGS.append(desk(-3.0, 1.3, 25.0, 27.2, 'left', 3))
crt(-0.6, 2.75, 25.6, False, 5, w=1.5)
chair(-1.0, 23.4, face=-1.0, tip=0.3)
LEGS.append(desk(-25.4, -19.8, 25.6, 27.8, 'right', 4))
crt(-23.0, 2.75, 26.2, False, 6)
papers(-21.4, -20.2, 25.9, 27.4, 2.75, 3, 13)
LEGS.append(desk(-20.4, -14.6, 21.6, 23.8, 'left', 6))
crt(-17.6, 2.75, 22.2, False, 8)
chair(-22.6, 24.6, face=-1.0)
# filing cabinets left of the doorway; the wall shelf above them gave way and slid onto them
for k, (cx0, hh) in enumerate(((-16.8, 5.4), (-14.9, 4.6), (-13.0, 5.4))):
    cabinet(cx0, cx0 + 1.8, ZB - 1.9, ZB - 0.1, hh, k, drawer=(2.6 if k == 1 else None))
rs.box(-18.2, -17.9, 8.6, 9.2, ZB - 0.6, ZB - 0.05, pipe, pipe, cls='prop')                      # the bracket that held
plank((-18.0, 9.2, ZB - 0.4), (-12.6, 5.45, ZB - 0.9), 1.0, 0.18, 5, v0=0.6)
for k in range(5):
    box_x = -16.6 + k * 0.9
    rs.box(box_x, box_x + 0.7, 5.45 if box_x > -14.6 else 4.65, (5.45 if box_x > -14.6 else 4.65) + 0.5 + (k % 2) * 0.3, ZB - 1.6, ZB - 0.9,
           lambda x, y, s, t, z, wp: fg(tone(CARD, 1.4 + 3.0 * lit(*wp, (0, 0, -1)), x, y), z), lambda x, y, s, t, z, wp: fg(CARD[1], z),
           top=lambda x, y, s, t, z, wp: fg(tone(CARD, 2.4, x, y), z), cls='prop')
drift(-14.0, ZB - 3.6, 2.8, 1.4, 26, 14)
# a tall cupboard in the back left corner, its door hanging open
def cupb(v0):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = v0 + 3.0 * lit(X, Y, Z, (0.7, 0, -0.7)) + (wn(1, Z * 0.6 + X, Y * 9) - 0.5) * 0.8
        if (Y / 3.0) % 1 < 0.04: v -= 1.0
        return fg(tone(WOODD, v, x, y), z)
    return sh
rs.box(-WX + 0.05, -WX + 2.2, 0, 9.4, ZB - 2.6, ZB - 0.05, cupb(0.6), cupb(1.0), top=cupb(0.8), cls='prop')
rs.quad((-WX + 2.2, 0.3, ZB - 2.6), (-WX + 3.8, 0.3, ZB - 4.0), (-WX + 2.2, 9.0, ZB - 2.6), cupb(1.4), cls='prop')

# the desk against the graffito wall: a telephone, a dead terminal
LEGS.append(desk(17.8, 25.2, 17.8, 20.2, 'right', 5))
crt(23.0, 2.75, 18.6, False, 7, w=1.5)
def phone(x, y, s, t, z, wp): return fg(tone(STEEL, 0.6 + 2.6 * lit(*wp, (0, 1, 0)) + (0.8 if t > 0.7 else 0), x, y), z)
rs.box(19.2, 20.4, 2.75, 3.25, 18.4, 19.2, phone, phone, top=phone, cls='prop')
rs.box(19.1, 20.5, 3.25, 3.5, 18.5, 18.8, phone, phone, top=phone, cls='prop')
rs.line3((20.4, 3.0, 18.8), (20.9, 0.1, 17.4), lambda x, y, s, t, z, wp: fg(CABLE[2], z), w=0.05, sag=-0.4)
papers(18.6, 21.6, 18.0, 19.8, 2.75, 3, 15)
chair(15.6, 18.0, face=1.0)
for k, (cx_, cz_, up) in enumerate(((8.6, 20.2, True), (10.0, 19.6, False), (11.4, 20.4, True), (12.6, 19.3, False))):
    can = lambda x, y, s, t, z, wp, k=k: fg(tone(PAINT if k % 2 == 0 else STEEL, 2.0 + (1.6 if s < 0.35 else 0) + (0.8 if t > 0.75 else 0), x, y), z)
    if up: rs.box(cx_ - 0.22, cx_ + 0.22, 0, 1.0, cz_ - 0.22, cz_ + 0.22, can, can, top=lambda x, y, s, t, z, wp: fg(STEEL[4], z), cls='prop')
    else: rs.box(cx_ - 0.5, cx_ + 0.5, 0, 0.42, cz_ - 0.2, cz_ + 0.2, can, can, top=can, cls='prop')
def rub(v0, rr):
    return lambda x, y, s, t, z, wp: fg(tone(rr, v0 + 3.4 * lit(*wp, (0, 1, 0)) + (h32(x, y, 5) % 3) * 0.3, x, y), z)
for k in range(30):                                                                              # fallen from round the bricked opening
    rx = 6.6 + (h32(k, 81) % 60) / 10.0; rz = ZG - 0.25 - (h32(k, 82) % 14) / 10.0
    sz = 0.12 + (h32(k, 83) % 5) / 18.0 * (1.2 - abs(rx - 9.0) / 5)
    rr = BRICK if h32(k, 84) % 3 == 0 else PLAST
    rs.box(rx - sz, rx + sz, 0, sz * 0.9, rz - sz, rz + sz, rub(2.0, rr), rub(1.4, rr), top=rub(2.8, rr), cls='prop')
# the bookcase right of the doorway: two shelves gave, the binders slid off into a heap
def shelfw(x, y, s, t, z, wp): return fg(tone(WOODD, 0.6 + 3.2 * lit(*wp, (0, 0, -1)), x, y), z)
BKX0, BKX1 = -2.9, 1.3
rs.box(BKX0, BKX0 + 0.25, 0, 8.6, ZB - 1.4, ZB - 0.05, shelfw, shelfw, cls='prop')
rs.box(BKX1 - 0.25, BKX1, 0, 8.6, ZB - 1.4, ZB - 0.05, shelfw, shelfw, cls='prop')
rs.quad((BKX0, 0, ZB - 0.06), (BKX1, 0, ZB - 0.06), (BKX0, 8.6, ZB - 0.06), lambda x, y, s, t, z, wp: fg(tone(WOODD, 0.3, x, y), z), cls='prop')
BINDERS = [(40, 46, 34), (58, 36, 28), (36, 44, 48), (64, 58, 40), (44, 50, 34), (30, 30, 26)]
def binder(P0, P1, P3, bc):
    def spine(x, y, s, t, z, wp):
        if 0.55 < t < 0.75 and 0.25 < s < 0.75: return fg(mix(bc, (120, 112, 88), 0.45), z)
        return fg(mix(bc, (0, 0, 0), max(0.0, 0.5 - 0.6 * lit(*wp, (0, 0.5, -1)))), z)
    rs.quad(P0, P1, P3, spine, cls='prop')
for k, yb in enumerate((0.4, 2.5)):
    rs.box(BKX0, BKX1, yb - 0.18, yb, ZB - 1.4, ZB - 0.05, shelfw, shelfw, top=shelfw, cls='prop')
    xb = BKX0 + 0.3
    while xb < BKX1 - 0.5:
        bw = 0.34 + (h32(int(xb * 10), k) % 3) * 0.06
        if h32(int(xb * 10), k, 2) % 4 == 0: xb += 0.6; continue
        lean = 0.0 if h32(int(xb * 10), k, 3) % 4 else 0.35
        binder((xb, yb, ZB - 1.3), (xb + bw, yb, ZB - 1.3), (xb + lean, yb + 1.6, ZB - 1.3), BINDERS[h32(int(xb * 10), k, 4) % len(BINDERS)])
        xb += bw + 0.03
plank((BKX0 + 0.25, 3.0, ZB - 0.8), (BKX1 - 0.3, 5.1, ZB - 0.7), 1.2, 0.16, 8, v0=0.2)          # a shelf hanging by one end
plank((BKX0 + 0.25, 6.7, ZB - 0.8), (BKX1 - 0.25, 6.7, ZB - 0.8), 1.2, 0.16, 9, v0=0.2)
for k in range(14):                                                                              # the heap of binders at its foot
    bx = BKX0 + 0.2 + (h32(k, 91) % 40) / 10.0; bz = ZB - 1.6 - (h32(k, 92) % 22) / 10.0; a = (h32(k, 93) % 628) / 100.0
    by = 0.05 + (k % 4) * 0.18
    c, s_ = math.cos(a), math.sin(a)
    binder((bx, by, bz), (bx + c * 0.9, by, bz + s_ * 0.9), (bx - s_ * 1.4, by + 0.05, bz + c * 1.4), BINDERS[k % len(BINDERS)])
def box_(X0, X1, Z0, Z1, Hh, seed):
    def f(v0):
        def sh(x, y, s, t, z, wp):
            v = v0 + 3.0 * lit(*wp, (0, 0.5, -0.8)) + (wn(1, s * 3 + seed, t * 3) - 0.5) * 0.6
            if abs(s - 0.5) < 0.06: v += 0.9
            return fg(tone(CARD, v, x, y), z)
        return sh
    rs.box(X0, X1, 0, Hh, Z0, Z1, f(1.4), f(0.8), top=f(2.4), cls='prop')
box_(-24.6, -22.6, 22.2, 23.8, 1.6, 1); box_(-24.4, -23.0, 22.4, 23.6, 2.6, 2); box_(13.6, 15.6, 19.0, 20.6, 1.4, 3)
box_(-6.0, -4.4, 26.6, 28.0, 1.2, 4); box_(26.6, 28.6, 19.2, 20.6, 2.0, 5)
chair(-11.0, 20.0, face=-1.0)

# close to the camera (behind the walk line): a cabinet at the left wall, a desk running out of frame on the right
cabinet(-WX + 0.05, -WX + 2.3, 15.3, 17.2, 5.8, 7)
drift(-22.6, 14.2, 1.8, 0.9, 14, 21)
LEGS.append(desk(22.8, 31.5, 15.4, 17.7, 'left', 9))
crt(27.6, 2.75, 16.0, False, 9, w=1.5)
papers(23.4, 26.4, 15.6, 17.4, 2.75, 6, 22)
toppled_chair(19.4, 12.6, side=True)

# ---------------------------------------------------------------------------------------------------- the foreground
def fallen(x, y, s, t, z, wp):
    X, _, Z = wp
    L = lit(X, 0.3, Z, (0, 1, 0))
    if s < 0.04 or s > 0.96 or t < 0.03 or t > 0.97 or abs(t - 0.47) < 0.02: return fg(tone(WOODD, 1.0 + 3.6 * L, x, y), z)
    if 0.52 < t < 0.92 and 0.1 < s < 0.9: return tone(GLASSD, 0.4 + (h32(x, y, 3) % 4 == 0) * 2.0, x, y)
    return fg(tone(WOODD, 1.6 + 4.0 * L + (wn(1, Z * 6, X * 0.5) - 0.5) * 0.8, x, y), z)
rs.quad((5.6, 0.12, 12.1), (11.0, 0.12, 13.6), (4.2, 0.12, 14.9), fallen, cls='prop')
papers(7.0, 9.0, 12.6, 13.8, 0.14, 2, 16)
toppled_chair(-0.6, 12.4)
toppled_chair(-12.6, 12.6, side=True)
# fallen ceiling planks: a heap under the breach, more across the floor, one leaning on desk B
for k, (A, B) in enumerate((((-17.0, 0.0, 22.4), (-12.4, 0.0, 24.6)), ((-16.4, 0.18, 24.9), (-11.6, 0.3, 21.8)), ((-15.0, 0.36, 21.6), (-13.6, 0.1, 25.8)),
                            ((-12.6, 0.0, 25.4), (-12.2, 3.2, 23.2)), ((-5.6, 0.0, 17.2), (1.6, 0.0, 18.4)), ((3.0, 0.0, 15.6), (9.0, 0.0, 16.9)),
                            ((-6.0, 0.0, 20.2), (-6.6, 2.8, 22.2)), ((14.0, 0.0, 17.0), (19.6, 0.0, 16.0)), ((-25.0, 0.0, 19.6), (-20.0, 0.0, 20.6)))):
    plank(A, B, 0.9 if k % 3 else 1.2, 0.2, k, v0=0.6 + (k % 3) * 0.3)
for k in range(70):                                                                              # plaster and lath fallen from the ceiling
    rx = -24.0 + (h32(k, 71) % 480) / 10.0; rz = 13.0 + (h32(k, 72) % 160) / 10.0
    if rx > XE and rz > ZG - 0.4: continue
    if abs(rz - 15.0) < 0.6: continue
    near = math.hypot(rx - BREACH[0], rz - BREACH[1]) < 4.0
    sz = 0.08 + (h32(k, 73) % 5) / 30.0 * (2.0 if near else 1.0)
    rr = TIMBER if h32(k, 74) % 3 == 0 else PLAST
    rs.box(rx - sz, rx + sz, 0, sz * 0.8, rz - sz, rz + sz, rub(1.4, rr), rub(0.8, rr), top=rub(2.2, rr), cls='prop')
# paper drifts: against the walls, under the desks, across the floor
for k, (cx_, cz_, rx_, rz_, n) in enumerate(((-24.0, 20.8, 1.6, 1.4, 18), (-8.0, 19.4, 3.0, 1.4, 22), (4.0, 19.6, 2.4, 0.9, 16),
                                              (-3.0, 13.4, 3.4, 1.2, 18), (11.0, 16.6, 3.0, 1.3, 16), (-19.0, 24.4, 2.2, 1.0, 14),
                                              (17.0, 20.2, 2.2, 0.5, 12), (-9.0, 28.2, 2.6, 0.9, 14), (-14.0, 14.0, 2.4, 1.0, 12))):
    drift(cx_, cz_, rx_, rz_, n, 40 + k)
papers(12.0, 20.0, 13.0, 17.0, 0.0, 6, 18)

# ---------------------------------------------------------------------------------------------------- the Living Core's roots
def tube(P0, P1, w, seed, vein=True):
    """a stretch of root as a lit tube: shaded across its width toward the light (upper left), a faint green pulse"""
    a = proj(*P0); b = proj(*P1)
    ddx, ddy = b[0] - a[0], b[1] - a[1]; ln = math.hypot(ddx, ddy) or 1.0
    px, py = -ddy / ln, ddx / ln
    if px * -0.55 + py * -0.83 < 0: px, py = -px, -py
    rpx = max(0.7, w * F / ((P0[2] + P1[2]) / 2) / 2)
    Lm = lit((P0[0] + P1[0]) / 2, (P0[1] + P1[1]) / 2 + w, (P0[2] + P1[2]) / 2, (0, 1, 0))
    def sh(x, y, s, t, z, P):
        n = ((x + 0.5 - a[0]) * px + (y + 0.5 - a[1]) * py) / rpx                              # +1 the lit edge, -1 the shadow edge
        v = 1.6 + n * 2.2 + 3.0 * Lm
        if vein and n > 0.0:
            pulse = wn(2, P[0] * 0.8 + seed, P[2] * 0.8 + P[1])
            if pulse > 0.6: return VEIN[0] if pulse < 0.67 else (VEIN[1] if pulse < 0.72 else VEIN[2])
        if n > 0.45 and wn(5, P[0] * 3, P[2] * 3 + P[1]) > 0.5: v += 1.6                       # a dull metal sheen along the top
        return fg(tone(ROOT, v, x, y), z)
    rs.line3(P0, P1, sh, w=w, n=max(2, int(ln) + 1), cls='prop')
def root_floor(X, Z, a, length, w0, rng, depth=0, step=0.3):
    pts = [(X, w0 * 0.5, Z, w0)]
    n = int(length / step)
    for i in range(n):
        a += (rng.random() - 0.5) * 0.45
        X += math.cos(a) * step; Z += math.sin(a) * step
        if X < -WX + 0.3 or Z < 11.0 or Z > 33.0 or (X > XE and Z > ZG - 0.3): break
        w = w0 * (1 - i / n) + 0.05
        pts.append((X, w * 0.5, Z, w))
        if depth < 2 and rng.random() < 0.05:
            root_floor(X, Z, a + (rng.random() - 0.5) * 2.0, length * 0.45, w * 0.7, rng, depth + 1, step)
    for p, q in zip(pts, pts[1:]): tube(p[:3], q[:3], (p[3] + q[3]) / 2, 1)
def root_wall(u0, a, length, w0, rng, plane, step=0.25):
    """a root climbing a wall: plane 'back' (u = X), 'gwall' (u = X), 'left' (u = Z)"""
    u, Y = u0, 0.2; pts = []
    n = int(length / step)
    for i in range(n):
        a += (rng.random() - 0.5) * 0.5 + (math.pi / 2 - a) * 0.05
        u += math.cos(a) * step; Y += math.sin(a) * step
        w = w0 * (1 - i / n) + 0.04
        if plane == 'back': P = (u, Y, ZB - w * 0.5 - 0.05)
        elif plane == 'gwall': P = (u, Y, ZG - w * 0.5 - 0.05)
        else: P = (-WX + w * 0.5 + 0.05, Y, u)
        pts.append((P, w))
    for (p, wp_), (q, wq) in zip(pts, pts[1:]): tube(p, q, (wp_ + wq) / 2, 2)
def root_base(u0, u1, plane, w, rng, step=0.3):
    """a root running along the foot of a wall"""
    pts = []; u = u0; d = 1 if u1 > u0 else -1
    while (u - u1) * d < 0:
        jit = (rng.random() - 0.5) * 0.15
        if plane == 'back': P = (u, w * 0.5, ZB - w * 0.5 - 0.1 + jit)
        elif plane == 'gwall': P = (u, w * 0.5, ZG - w * 0.5 - 0.1 + jit)
        else: P = (-WX + w * 0.5 + 0.1 + jit, w * 0.5, u)
        pts.append(P); u += step * d
    for p, q in zip(pts, pts[1:]): tube(p, q, w, 3, vein=False)
def root_leg(lx, lz, height, w, rng):
    pts = []; a = rng.random() * 6.28
    Y = 0.1
    while Y < height:
        pts.append((lx + math.cos(a) * 0.32, Y, lz + math.sin(a) * 0.32)); a += 0.55; Y += 0.12
    for p, q in zip(pts, pts[1:]): tube(p, q, w, 4, vein=False)
rrng = random.Random(521)
for (x0, a, ln, w0) in ((-7.6, math.pi * 1.42, 18.0, 0.32), (-5.2, math.pi * 1.55, 16.0, 0.3), (-6.6, math.pi * 1.25, 15.0, 0.28),
                        (-4.4, math.pi * 1.72, 14.0, 0.26), (-8.4, math.pi * 1.08, 14.0, 0.26), (-4.0, math.pi * 1.9, 12.0, 0.24),
                        (-6.0, math.pi * 1.48, 20.0, 0.3), (-8.8, math.pi * 1.0, 16.0, 0.22), (-5.6, math.pi * 1.62, 22.0, 0.3),
                        (-7.0, math.pi * 1.33, 22.0, 0.28), (-4.8, math.pi * 1.8, 18.0, 0.26)):
    root_floor(x0, 32.5, a, ln, w0 * 2.0, rrng)
root_base(-9.6, -25.6, 'back', 0.4, rrng); root_base(-3.2, 1.4, 'back', 0.34, rrng)
root_base(2.0, 24.0, 'gwall', 0.4, rrng); root_base(29.0, 17.0, 'left', 0.34, rrng)
for (u0, ln) in ((-11.0, 4.5), (-20.5, 6.5), (-24.8, 3.0), (-1.6, 3.5)):
    root_wall(u0, math.pi / 2 + (rrng.random() - 0.5) * 0.6, ln, 0.3, rrng, 'back')
for (u0, ln) in ((3.4, 5.0), (13.5, 3.5), (21.0, 4.5), (6.4, 2.6)):
    root_wall(u0, math.pi / 2 + (rrng.random() - 0.5) * 0.6, ln, 0.34, rrng, 'gwall')
for (u0, ln) in ((21.0, 3.8), (27.4, 5.5)):
    root_wall(u0, math.pi / 2 + (rrng.random() - 0.5) * 0.5, ln, 0.3, rrng, 'left')
for (lx, lz) in LEGS[:4]: root_leg(lx, lz, 2.4, 0.2, rrng)

# ---------------------------------------------------------------------------------------------------- overlay: the light in the air, the grade
SHAFT_TINT = (226, 168, 84)
COL_TINT = (176, 160, 120)
def finish(col):
    # the window light through the dusty air: march each view ray through the room (at half resolution)
    acc = {}
    for y in range(40, H, 2):
        for x in range(0, 700, 2):
            dx, dy = ray(x, y)
            zb = min(rs.ZB[y][x], ZB)
            a = 0.0; Z = 11.0 + (h32(x, y, 3) % 100) / 100 * 0.6
            while Z < zb:
                X = dx * Z; Y = CAMH + dy * Z
                if X > -WX and 0 < Y < CH: a += sun(X, Y, Z)
                Z += 0.6
            if a > 0.01: acc[(x, y)] = a
    for (x, y), a in acc.items():
        for (xx, yy) in ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)):
            if xx >= W or yy >= H: continue
            k = min(0.34, a * 0.028)
            if (xx + yy) % 2 and k < 0.05: continue
            c = col[yy][xx]
            col[yy][xx] = tuple(min(255, int(c[i] + (SHAFT_TINT[i] - c[i]) * k)) for i in range(3))
    # the column of daylight under the breach
    for y in range(0, H):
        for x in range(240, 460):
            dx, dy = ray(x, y)
            a = 0.0; zb = rs.ZB[y][x]
            for k in range(14):
                Z = BREACH[1] - 2.8 + k * 0.4
                if Z >= zb: break
                X = dx * Z; Y = CAMH + dy * Z
                if not 0 < Y < CH: continue
                sx = ((X - BREACH[0] + (CH - Y) * 0.05) / (BREACH[2] * 0.95)) ** 2 + ((Z - BREACH[1]) / (BREACH[3] * 1.1)) ** 2
                if sx < 1: a += (1 - sx) * (0.55 + 0.45 * Y / CH) * 0.4
            if a > 0.01:
                k = min(0.14, a * 0.09)
                if (x + y) % 2 and k < 0.03: continue
                c = col[y][x]
                col[y][x] = tuple(int(c[i] + (COL_TINT[i] - c[i]) * k) for i in range(3))
    # dust motes in the light
    drng = random.Random(4)
    for k in range(260):
        X = -24.0 + drng.random() * 24.0; Y = drng.random() * 20.0; Z = 13.0 + drng.random() * 14.0
        s_ = sun(X, Y, Z)
        if s_ < 0.25: continue
        sx, sy = proj(X, Y, Z); sx, sy = int(sx), int(sy)
        if 0 <= sx < W and 0 <= sy < H and rs.ZB[sy][sx] > Z:
            col[sy][sx] = mix(col[sy][sx], (240, 206, 140), 0.5 * s_)
    # the warm grade (sepia, the shadows warm and deep) and a vignette, back on the 4-step grid
    for y in range(H):
        vy = (y - 320) / 300.0
        row = col[y]
        for x in range(W):
            vx = (x - 533) / 533.0
            vg = max(0.5, 1 - 0.26 * vx * vx - (0.42 if vy > 0 else 0.24) * vy * vy - (0.12 * (-vy) * (1 - max(0.0, vx)) if vy < 0 else 0))
            r, g, b = row[x]
            lum = (0.3 * r + 0.59 * g + 0.11 * b) / 255
            vg += (1 - vg) * min(1.0, max(0.0, lum - 0.35) * 2.5)                                 # the glowing windows keep their light
            curve = 0.86 + 0.14 * min(1.0, lum * 2.2)                                          # crush the darks a little
            r, g, b = r * vg * curve, g * vg * curve * 0.94, b * vg * curve * 0.74
            row[x] = tuple(max(0, min(255, int(v / 4 + 0.5) * 4)) for v in (r, g, b))

img = rs.render(INK, fog=fog, overlay=finish, mirror=lambda x, y, wp: 0.4 * puddle(wp[0], wp[2]),
                light_gain=1.0, grime_gain=0.9, bloom=0.5, stain_gain=0.5, damp_gain=0.5,
                lights=[(-30.0, 5.0, 13.0, (1.0, 0.72, 0.42), 10.0, 18.0),                     # the stairwell door, off left
                        (-6.4, 2.5, 32.5, (0.35, 0.85, 0.45), 0.8, 5.0),                         # the Hall's green, up the stair
                        (BREACH[0], 3.0, BREACH[1], (0.95, 0.9, 0.72), 2.0, 7.0)])               # where the column lands
img.save(f'{OUT}/office.png')

# ---------------------------------------------------------------------------------------------------- reference layers for Aseprite
KX = W / 800
g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
def zone(cx, cy, w, h, col):
    d.rectangle([cx * KX - w * KX / 2, cy - h / 2, cx * KX + w * KX / 2, cy + h / 2], outline=col)
zone(50, 470, 50, 200, (255, 200, 80, 255))                                                     # back to the stairs
zone(352, 362, 50, 140, (127, 255, 142, 255))                                                   # to the Hall
d.ellipse([662 - 22, 212 - 42, 662 + 22, 212 + 42], outline=(190, 230, 200, 255))              # Palinode's tunnel
for x in range(0, W, 8): d.line([(x, 534), (x + 4, 534)], fill=(255, 80, 80, 255))
for x in range(0, W, 8): d.line([(x, 296), (x + 4, 296)], fill=(200, 200, 90, 255))
d.rectangle([811, 12, 1043, 88], outline=(120, 160, 255, 255))                                  # HUD buttons
g.save(f'{OUT}/guides.png')
pr = Image.open(os.path.join(HERE, '../../assets/images/characters/priest.png')).convert('RGBA').crop((0, 0, 128, 128))
ch = Image.new('RGBA', (W, H), (0, 0, 0, 0))
for cx_ in (250, 470, 760):
    ch.alpha_composite(pr, (cx_ - 64, 534 - 128))
ch.save(f'{OUT}/chars.png')
out = ['GIMP Palette', 'Name: Shed 521 abandoned office (native)', 'Columns: 8', '#']
for (nm, r) in ALLRAMPS:
    for i, c in enumerate(r): out.append('%3d %3d %3d\t%s %d' % (c[0], c[1], c[2], nm, i + 1))
open(f'{OUT}/office-native.gpl', 'w').write('\n'.join(out) + '\n')
print('done office; doorway', [round(v) for v in proj(DOOR[0], DOOR[3], ZB)], [round(v) for v in proj(DOOR[1], 0, ZB)],
      'hatch', [round(v) for v in proj(*HATCH, ZG)], 'wall edge x', round(proj(XE, 0, ZG)[0]))
