"""The Hall -- the old service hall under Shed 521 behind the abandoned office (ShedHallScene), 1067x600, the shared
camera (raster3d.py). After the old AI picture (a long dank corridor in green fluorescent light): the corridor is now
the tunnel running off into the dark from the back wall of a low service hall the player can walk across. Glazed
tiles half fallen off the walls, damp concrete, pipe bundles along the ceiling and down the walls, fluorescent tubes
(two lit, one dead and hanging off its chain), two notices on the right wall, a breach in the left wall, cracked
floor tiles and rubble. The Living Core is fused into the back wall right of the tunnel: an iron socket with roots of
living metal spreading over the wall and the floor, some of them into the tunnel, their veins glowing. The core
itself is the scene's sprite (it vanishes when taken -- the socket stays). The way back is the steel door in the
left wall, a sliver of the stairwell's warm light in its gap.

    python3 hall_bg.py <outdir>   ->  hall.png  (= assets/images/backgrounds/ShedHall.png)
"""
import sys, math, random
from common import h32
from shedkit import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = Raster()
WX, CH, ZB = 24.0, 18.0, 24.0           # the hall: half-width, ceiling, back wall
TW, TH, TZ = 4.5, 13.0, 150.0           # the tunnel: half-width, height (under a lintel), its far end
CORE = (12.0, 5.6)                      # the Living Core's socket on the back wall (X, height)

CONC = ramp('#0b120e #111a14 #18231b #1f2d23 #28382c #314335 #3b4f3f #465b49 #536853')
TILE = ramp('#121c16 #1a271f #233328 #2e4033 #3a4e3f #485d4c #576d5a #687e69 #7b917b')
PIPE = ramp('#0a0f0c #111914 #19231c #222e25 #2c3a2f #37463a #435446')
RUSTG = ramp('#1a1309 #281c0d #382712 #493317')
ROOT = ramp('#070b09 #0d1410 #141e18 #1c2a21 #25372b #2f4535')
VEIN = ramp('#14401f #1f6a30 #2f9444 #4cc05e #86e892 #c4ffcc')
PAPER = ramp('#3a4434 #4c5844 #606c55 #758068 #8a947a')
STEEL = ramp('#0e1310 #161d18 #1f2821 #29342b #344136')
DARK = (5, 9, 7)
TUBE = (214, 238, 206)
WARMS = (150, 112, 60)

# lights: position, strength, radius (the tunnel's tubes only light the tunnel)
LIGHTS = [((-10.0, 14.6, 10.0), 1.0, 13.0), ((9.0, 14.6, 16.5), 0.9, 12.0), ((-8.0, 14.6, 21.0), 0.5, 9.0),
          ((0.0, 12.4, 36.0), 0.55, 6.0), ((0.0, 12.4, 70.0), 0.32, 5.0), ((0.0, 12.4, 104.0), 0.16, 4.0)]
CORE_L = ((CORE[0], CORE[1], ZB - 0.6), 0.9, 6.5)


def lit(X, Y, Z, n):
    s = 0.0
    for (lx, ly, lz), I, r in LIGHTS:
        if (Z < ZB - 0.01) and lz > ZB: continue
        k = 1.0 if (Z > ZB) == (lz > ZB) else 0.25
        dx, dy, dz = lx - X, ly - Y, lz - Z
        d2 = dx * dx + dy * dy + dz * dz; d = math.sqrt(d2) + 1e-6
        ndl = max(0.0, (dx * n[0] + dy * n[1] + dz * n[2]) / d)
        s += k * I * (0.35 + 0.65 * ndl) * r * r / (r * r + d2)
    return s


def corelit(X, Y, Z):
    (lx, ly, lz), I, r = CORE_L
    if Z > ZB + 0.5: return 0.0
    d2 = (lx - X) ** 2 + (ly - Y) ** 2 + (lz - Z) ** 2
    return I * r * r / (r * r + d2 * 1.6)


def dk(c, Z):
    """the tunnel swallows light: fade toward the dark with depth"""
    f = max(0.0, min(0.94, (Z - ZB) / 95.0))
    return mix(c, DARK, f)


def glow(c, g):
    return mix(c, VEIN[3], min(0.55, g * 0.5)) if g > 0.02 else c


# ---------------------------------------------------------------------------------------------------- the roots
def grow(rng, x, y, ang, length, width, out, depth=0, bend=0.35, step=0.35):
    """a branching root as a list of (x, y, w) samples in a plane"""
    for i in range(int(length / step)):
        ang += (rng.random() - 0.5) * bend
        x += math.cos(ang) * step; y += math.sin(ang) * step
        w = width * (1 - i / (length / step)) + 0.05
        out.append((x, y, w))
        if depth < 2 and rng.random() < 0.05:
            grow(rng, x, y, ang + (rng.random() - 0.5) * 1.6, length * 0.45, w * 0.7, out, depth + 1, bend, step)


def rasterise(samples, cell=0.08):
    grid = {}
    for (x, y, w) in samples:
        r = int(w / cell) + 1
        for i in range(-r, r + 1):
            for j in range(-r, r + 1):
                d = math.hypot(i * cell, j * cell)
                if d <= w:
                    k = (int(math.floor(x / cell)) + i, int(math.floor(y / cell)) + j)
                    v = 1 - d / w                      # 1 on the spine, 0 at the edge
                    if v > grid.get(k, -1): grid[k] = v
    return grid, cell


rng = random.Random(1140)
wall_s = []
for k in range(11):                     # over the back wall, out of the socket
    a = k / 11 * 2 * math.pi + rng.random() * 0.4
    grow(rng, CORE[0] + math.cos(a) * 2.0, CORE[1] + math.sin(a) * 2.0, a, 4.5 + rng.random() * 5.0, 0.55, wall_s)
for x0 in (10.6, 12.2, 13.4):           # down to the floor
    grow(rng, x0, CORE[1] - 2.0, -math.pi / 2 + (rng.random() - 0.5) * 0.3, CORE[1] - 1.6, 0.65, wall_s, bend=0.15)
WALL_ROOTS = rasterise(wall_s)
floor_s = []
for (x0, a, ln) in ((10.8, math.pi * 1.12, 15.0), (12.0, math.pi * 1.32, 12.0), (13.2, math.pi * 1.5, 11.0),
                    (12.6, math.pi * 1.62, 13.0), (11.4, math.pi * 1.02, 9.0), (13.8, math.pi * 1.8, 8.0)):
    # floor plane coords (X, Z): start at the wall foot, run toward the camera / toward the tunnel mouth
    grow(rng, x0, ZB - 0.2, a, ln, 0.95, floor_s, bend=0.3)
for (x0, ln) in ((3.6, 34.0), (2.2, 26.0)):                    # two roots crawl off into the tunnel
    grow(rng, x0, ZB - 0.5, math.pi * 0.48, ln, 0.6, floor_s, bend=0.1, step=0.5)
FLOOR_ROOTS = rasterise(floor_s)


def root_at(grid, a, b):
    g, cell = grid
    return g.get((int(math.floor(a / cell)), int(math.floor(b / cell))))


def root_px(v, x, y, a, b, light, seed):
    """living metal: a dark rounded body with a lit ridge, a glowing vein running along the spine in stretches"""
    lv = 1 if light > 0.35 else 0
    c = ROOT[0 + lv] if v < 0.3 else (ROOT[1 + lv] if v < 0.62 else ROOT[2 + lv])
    pulse = wn(2, a * 0.3 + seed, b * 0.3)
    if v > 0.55 and pulse > 0.52: c = VEIN[1] if pulse < 0.6 else (VEIN[2] if pulse < 0.68 else VEIN[3])
    return c


# ---------------------------------------------------------------------------------------------------- the shell
def floor_sh(x, y, s, t, z, wp):
    X, _, Z = wp
    r = root_at(FLOOR_ROOTS, X, Z)
    L = lit(X, 0, Z, (0, 1, 0)); g = corelit(X, 0, Z)
    if r is not None: return dk(glow(root_px(r, x, y, X, Z, L, 3), g * 0.6), Z)
    i, j = math.floor(X / 2.0), math.floor(Z / 2.0)
    if h32(i, j, 61) % 23 == 0 and Z < ZB: return dk(tone(CONC, 0.4 + L, x, y), Z)          # a lifted tile: the bed below
    v = 1.2 + 4.6 * L + (wn(0, X * 0.6, Z * 0.6) - 0.5) * 0.9 + (h32(i, j, 62) % 5 - 2) * 0.12
    fu, fv = (X / 2.0) % 1, (Z / 2.0) % 1
    if fu < 0.9 * z / F / 2.0 + 0.015 or fv < 0.9 * z * z / (F * CAMH) / 2.0 + 0.015: v -= 1.1      # joints
    cr = wn(1, X * 1.3 + i, Z * 1.3 + j)                                                       # cracks
    if abs(cr - 0.5) < 0.012 * (1 + z / 30): v -= 1.2
    if wn(3, X * 0.35, Z * 0.35) > 0.66: v -= 0.6                                              # damp
    return dk(glow(tone(CONC, v, x, y), g), Z)


def wall_px(X, Y, Z, n, x, y, along, seed):
    """lower wall glazed tiles (many fallen), a dark band, damp concrete above"""
    L = lit(X, Y, Z, n); g = corelit(X, Y, Z)
    if Y < 0.5: return glow(tone(CONC, 0.6 + 2.4 * L, x, y), g)                                 # the foot
    if Y < 5.4:
        i, j = math.floor(along / 1.0), math.floor(Y / 1.0)
        gone = wn(seed % 4, along * 0.35, Y * 0.5) > 0.6 + 0.1 * (Y / 5.4) or h32(i, j, seed + 7) % 11 == 0
        if gone:                                                                              # bare render, a broken edge
            v = 0.9 + 3.6 * L + (wn(1, along * 2, Y * 2) - 0.5) * 0.7
            return glow(tone(CONC, v, x, y), g)
        fu, fv = (along / 1.0) % 1, (Y / 1.0) % 1
        if fu < 0.06 or fv < 0.06: return glow(tone(CONC, 0.8 + 2.0 * L, x, y), g)              # grout
        v = 1.6 + 5.4 * L + (h32(i, j, seed) % 5 - 2) * 0.18 + (0.7 if fv > 0.8 else 0)          # glaze catches the tube light
        if h32(i, j, seed + 3) % 7 == 0 and abs(fu - fv) < 0.05: v -= 1.4                        # a crack across a tile
        return glow(tone(TILE, v, x, y), g)
    if Y < 6.0: return glow(tone(TILE, 0.8 + 2.6 * L, x, y), g)                                 # the dark band
    v = 1.0 + 4.4 * L + (wn(0, along * 0.5, Y * 0.5) - 0.5) * 0.9
    if wn(2, along * 0.9, Y * 0.12) > 0.64: v -= 0.8                                           # damp runs from the ceiling
    return glow(tone(CONC, v, x, y), g)


def lwall(x, y, s, t, z, wp):
    X, Y, Z = wp
    if 15.6 < Z < 19.4 and Y < 7.4:                                                           # the steel door back up
        if Z < 15.8 or Y > 7.2: return tone(STEEL, 0.6, x, y)
        if Z > 19.05: return WARMS if Y > 0.3 else tone(STEEL, 0.4, x, y)                      # the gap: stairwell light
        v = 1.2 + 3.0 * lit(X, Y, Z, (1, 0, 0)) + (0.6 if abs(Y - 3.6) < 0.08 else 0)
        if abs(Z - 18.6) < 0.12 and abs(Y - 3.4) < 0.2: return tone(STEEL, 4.0, x, y)          # the push bar's end
        return tone(STEEL, v, x, y)
    if 15.9 < Z < 18.9 and 7.9 < Y < 8.9:                                                     # the exit sign: a running figure
        u, w = (Z - 15.9) / 3.0, (Y - 7.9) / 1.0
        fig = (abs(u - 0.32) < 0.06 and 0.2 < w < 0.75) or (abs(u - 0.32) < 0.09 and abs(w - 0.85) < 0.08) \
            or (abs((u - 0.32) - (w - 0.4) * 0.6) < 0.05 and w < 0.42) or (abs(w - 0.55) < 0.05 and 0.18 < u < 0.48) \
            or (abs(w - 0.5) < 0.07 and 0.6 < u < 0.9)
        return (24, 60, 32) if fig else (118, 220, 132)
    if 21.0 < Z < 24.6 and 0.6 < Y < 6.2:                                                     # a breach into the dark
        e = wn(2, Z * 1.5, Y * 1.5) * 0.9
        if 21.0 + e < Z < 24.6 - e * 0.6 and 0.6 + e * 0.8 < Y < 6.2 - e:
            return (4, 7, 5) if wn(3, Z * 4, Y * 4) > 0.3 else tone(CONC, 0.6, x, y)
    return wall_px(X, Y, Z, (1, 0, 0), x, y, Z, 5)


def rwall(x, y, s, t, z, wp):
    X, Y, Z = wp
    for (z0, z1, y0, y1, k) in ((15.6, 17.6, 6.4, 9.2, 0), (18.6, 20.2, 6.8, 9.0, 1)):       # two notices
        if z0 < Z < z1 and y0 < Y < y1:
            u, w = (Z - z0) / (z1 - z0), (Y - y0) / (y1 - y0)
            v = 2.4 + 2.0 * lit(X, Y, Z, (-1, 0, 0)) - (0.8 if wn(1, Z * 3, Y * 3) > 0.7 else 0)
            if (u < 0.05 or u > 0.95 or w < 0.04 or w > 0.96) and h32(int(Z * 9), int(Y * 9)) % 3: v -= 0.8
            if k == 0 and 0.62 < w < 0.9 and 0.15 < u < 0.85 and int(w * 22) % 3 == 0: v -= 1.6      # lines of print
            if k == 0 and w < 0.55 and 0.25 < u < 0.75 and abs(math.sin((u * 3 + w * 2) * 6.0) * 0.06 - ((w * 6) % 1 - 0.5) * 0.12) < 0.02: v -= 1.6   # the waves
            if k == 1 and 0.15 < u < 0.85 and 0.12 < w < 0.88 and int(w * 16) % 2 == 0 and (u - 0.15) < 0.7 * (0.5 + (h32(int(w * 16), 3) % 6) / 10): v -= 1.4
            return tone(PAPER, v, x, y)
    return wall_px(X, Y, Z, (-1, 0, 0), x, y, -Z, 6)


def back(x, y, s, t, z, wp):
    X, Y, Z = wp
    if abs(X) < TW and Y < TH: return None                                                    # the tunnel mouth
    if abs(X) < TW + 0.6:                                                                     # its concrete frame + lintel
        return tone(CONC, 1.4 + 3.4 * lit(X, Y, Z, (0, 0, -1)) + (0.5 if Y > TH else 0), x, y)
    dx, dy = X - CORE[0], Y - CORE[1]; d = math.hypot(dx, dy)
    if d < 2.6:                                                                               # the socket: flange, bolts, the hollow
        if d < 1.9: return tone(ROOT, 0.6 + (1.9 - d) * 0.5, x, y) if d > 1.4 else (6, 14, 9)
        a = math.atan2(dy, dx)
        if abs(((a / (2 * math.pi) * 10) % 1) - 0.5) < 0.12 and abs(d - 2.25) < 0.14: return tone(PIPE, 5.0, x, y)
        return tone(PIPE, 2.0 + (2.6 - d) * 1.5 + (1.0 if dy > 0 else 0), x, y)
    r = root_at(WALL_ROOTS, X, Y)
    if r is not None:
        return glow(root_px(r, x, y, X, Y, lit(X, Y, Z, (0, 0, -1)), 7), corelit(X, Y, Z) * 0.6)
    return wall_px(X, Y, Z, (0, 0, -1), x, y, X, 7)


rs.quad((-WX, 0, 3), (WX, 0, 3), (-WX, 0, ZB), floor_sh, cls='ground')
rs.quad((-WX, 0, 1.0), (-WX, 0, ZB), (-WX, CH, 1.0), lwall, cls='wall')
rs.quad((WX, 0, 1.0), (WX, 0, ZB), (WX, CH, 1.0), rwall, cls='wall')
rs.quad((-WX, 0, ZB), (WX, 0, ZB), (-WX, CH, ZB), back, cls='wall', cut=True)


def ceil_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    L = lit(X, Y, Z, (0, -1, 0))
    v = 0.5 + 2.6 * L + (wn(0, X * 1.6 + 70, Z * 1.6) - 0.5) * 0.45
    if wn(2, X * 0.3, Z * 0.3) > 0.7: v -= 0.3                                                   # water stains
    if (X / 1.2) % 1 < 0.6 * z / F / 1.2 + 0.01: v -= 0.5                                        # shuttering board marks
    return dk(tone(CONC, v, x, y), Z)
rs.quad((-WX, CH, 1.0), (WX, CH, 1.0), (-WX, CH, ZB), ceil_sh, cls='ceil')
def beam(x, y, s, t, z, wp):
    X, Y, Z = wp
    return tone(CONC, 0.9 + 2.6 * lit(X, Y, Z, (0, -1, 0)) + (0.8 if Y < CH - 0.9 else 0), x, y)
for bz in (8.0, 14.0, 20.0):                                                                    # cross beams
    rs.box(-WX, WX, CH - 1.0, CH, bz, bz + 0.9, beam, beam, bottom=beam, cls='ceil')
# a riveted air duct and a cable tray along the hall, hung under the beams
def duct(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 1.2 + 3.6 * lit(X, Y, Z, (0, -1, 0)) + (0.9 if t > 0.8 else 0)
    if (Z / 2.4) % 1 < 0.05: v -= 1.0
    elif abs((Z / 2.4) % 1 - 0.1) < 0.03 and int(Y * 4) % 2 == 0: v += 1.2
    return dk(tone(PIPE, v, x, y), Z)
rs.box(-17.0, -13.4, CH - 3.2, CH - 1.0, 3.0, ZB - 0.2, duct, duct, bottom=duct, cls='prop')
for hz in (6.0, 12.0, 18.0):
    rs.line3((-17.2, CH - 1.0, hz), (-17.2, CH - 3.4, hz), lambda x, y, s, t, z, wp: tone(PIPE, 1.4, x, y), w=0.1)
    rs.line3((-13.2, CH - 1.0, hz), (-13.2, CH - 3.4, hz), lambda x, y, s, t, z, wp: tone(PIPE, 1.4, x, y), w=0.1)
def tray(x, y, s, t, z, wp):
    X, Y, Z = wp
    return dk(tone(PIPE, 1.0 + 3.0 * lit(X, Y, Z, (0, -1, 0)) + (1.0 if (Z * 2) % 1 < 0.1 else 0), x, y), Z)
rs.box(10.5, 13.5, CH - 2.4, CH - 2.1, 3.0, ZB - 0.2, tray, tray, bottom=tray, cls='prop')
for k in range(5):                                                                              # cables sagging off the tray
    cz = 5.0 + k * 3.7
    rs.line3((13.4, CH - 2.2, cz), (13.4, CH - 2.2, cz + 2.6), lambda x, y, s, t, z, wp: (12, 16, 13), w=0.09, sag=-0.9 - k % 2 * 0.6)

# the tunnel: walls, floor, ceiling, tubes, its far dark end
def t_floor(x, y, s, t, z, wp):
    X, _, Z = wp
    r = root_at(FLOOR_ROOTS, X, Z)
    L = lit(X, 0, Z, (0, 1, 0))
    if r is not None: return dk(root_px(r, x, y, X, Z, L, 3), Z)
    v = 1.0 + 4.8 * L + (wn(0, X * 0.6, Z * 0.6) - 0.5) * 0.9
    if abs(X) < 0.06 * z / 30 + 0.04: v -= 0.8                                                 # the drain channel
    return dk(tone(CONC, v, x, y), Z)
def t_wall(side):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        return dk(wall_px(X, Y, Z, (-side, 0, 0), x, y, Z * side, 8 + (side > 0)), Z)
    return sh
def t_ceil(x, y, s, t, z, wp):
    X, Y, Z = wp
    return dk(tone(CONC, 0.8 + 3.4 * lit(X, Y, Z, (0, -1, 0)), x, y), Z)
rs.quad((-TW, 0, ZB), (TW, 0, ZB), (-TW, 0, TZ), t_floor, cls='ground')
rs.quad((-TW, 0, ZB), (-TW, 0, TZ), (-TW, TH, ZB), t_wall(-1), cls='wall')
rs.quad((TW, 0, ZB), (TW, 0, TZ), (TW, TH, ZB), t_wall(1), cls='wall')
rs.quad((-TW, TH, ZB), (TW, TH, ZB), (-TW, TH, TZ), t_ceil, cls='ceil')
rs.quad((-TW, 0, TZ), (TW, 0, TZ), (-TW, TH, TZ), lambda x, y, s, t, z, wp: DARK, cls='wall')

# fluorescent fixtures: housings + glowing diffusers; one dead, hanging by a chain
def housing(x, y, s, t, z, wp): return dk(tone(PIPE, 1.6 + (1.2 if t > 0.6 else 0), x, y), wp[2])
def diffuser(x, y, s, t, z, wp):
    if s < 0.04 or s > 0.96: return dk(tone(PIPE, 2.4, x, y), wp[2])
    return dk(mix(TUBE, (170, 206, 166), abs(t - 0.5) * 1.4), wp[2] * 0.6)
for (fx, fz, on) in ((-10.0, 10.0, True), (9.0, 16.5, True), (-8.0, 21.0, True), (0.0, 36.0, True), (0.0, 53.0, False),
                     (0.0, 70.0, True), (0.0, 87.0, False), (0.0, 104.0, True)):
    hy = 15.2 if fz < ZB else TH                                                                 # pendants in the hall
    if fz < ZB:
        for rx in (fx - 1.8, fx + 1.8): rs.line3((rx, CH - 1.0, fz), (rx, hy, fz), lambda x, y, s, t, z, wp: tone(PIPE, 1.6, x, y), w=0.06)
    rs.box(fx - 2.2, fx + 2.2, hy - 0.55, hy - 0.05, fz - 0.35, fz + 0.35, housing, housing, cls='prop')
    if on:
        rs.quad((fx - 2.0, hy - 0.57, fz - 0.25), (fx + 2.0, hy - 0.57, fz - 0.25), (fx - 2.0, hy - 0.57, fz + 0.25),
                diffuser, cls='emit')
    else:
        rs.quad((fx - 2.0, hy - 0.57, fz - 0.25), (fx + 2.0, hy - 0.57, fz - 0.25), (fx - 2.0, hy - 0.57, fz + 0.25),
                lambda x, y, s, t, z, wp: dk(tone(PIPE, 2.0, x, y), wp[2]), cls='prop')
# the dead one: one chain gave, it hangs at a slant
rs.line3((4.0, CH - 1.0, 12.4), (4.0, 15.0, 12.4), lambda x, y, s, t, z, wp: tone(PIPE, 2.4, x, y), w=0.06)
rs.line3((4.0, 14.9, 12.4), (7.6, 12.6, 12.6), housing, w=0.5)

# pipe bundles along the ceiling, into the tunnel; drops down the back wall with valves
def pipe_sh(k):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = 1.0 + 3.4 * lit(X, Y, Z, (0, -1, 0)) + (1.2 if (y + k) % 3 == 0 else 0)
        c = tone(PIPE, v, x, y)
        if wn(1, X * 0.8 + Z * 0.8 + k, Y) > 0.7: c = tone(RUSTG, 1.0 + v * 0.4, x, y)
        return dk(c, Z)
    return sh
for k, (px_, py_) in enumerate(((-21.6, 16.6), (-20.6, 16.0), (-22.4, 15.8), (20.8, 16.6), (21.8, 15.9))):
    rs.line3((px_, py_, 3.0), (px_, py_, ZB - 0.3), pipe_sh(k), w=0.45 - 0.08 * (k % 2))
    rs.line3((px_, py_, ZB - 0.3), (math.copysign(TW + 1.2 + 0.5 * (k % 3), px_), py_, ZB - 0.3), pipe_sh(k), w=0.4)
    rs.line3((math.copysign(TW + 1.2 + 0.5 * (k % 3), px_), py_, ZB - 0.3), (math.copysign(TW - 0.6 - 0.5 * (k % 3), px_), 12.4 - 0.3 * k, ZB - 0.3), pipe_sh(k), w=0.4)
for k, (px_, py_) in enumerate(((-3.8, 12.6), (3.6, 12.5), (-3.2, 12.0))):
    rs.line3((px_, py_, ZB - 0.3), (px_, py_, TZ), pipe_sh(k + 5), w=0.32)
for k, px_ in enumerate((-7.0, -6.2, 18.5)):                                                   # drops to the floor
    rs.line3((px_, CH - 0.8, ZB - 0.35), (px_, 0.0, ZB - 0.35), pipe_sh(k + 9), w=0.34)
    rs.disc(px_, 3.4 + k * 0.6, ZB - 0.75, 0.55, lambda x, y, s, t, z, wp: tone(RUSTG, 2.6, x, y) if math.hypot(s, t) > 0.55 or abs(s) < 0.15 or abs(t) < 0.15 else (8, 12, 9))

# rubble along the walls, a fallen ceiling slab, scraps of paper
def rubble(x, y, s, t, z, wp): return tone(CONC, 1.4 + 3.6 * lit(wp[0], wp[1], wp[2], (0, 1, 0)) + (h32(x, y, 5) % 3) * 0.3, x, y)
for k in range(46):
    side = -1 if k % 2 else 1
    rx = side * (WX - 0.8 - (h32(k, 31) % 40) / 10.0)
    rz = 12.0 + (h32(k, 32) % 115) / 10.0
    if side > 0 and rz > 21.0: rx = side * (WX - 0.8 - (h32(k, 31) % 18) / 10.0)
    sz = 0.25 + (h32(k, 33) % 6) / 10.0
    rs.box(rx - sz, rx + sz, 0, sz * 0.8, rz - sz, rz + sz, rubble, rubble, top=rubble, cls='prop')
rs.box(-15.0, -11.4, 0, 0.5, 18.2, 20.6, rubble, rubble, top=rubble, cls='prop')                # a slab fallen from above
for k in range(10):
    fx, fz = -20 + (h32(k, 41) % 400) / 10.0, 12.5 + (h32(k, 42) % 100) / 10.0
    a = (h32(k, 43) % 628) / 100.0; c, s_ = math.cos(a) * 0.35, math.sin(a) * 0.35
    rs.quad((fx - c, 0.03, fz - s_), (fx + s_, 0.03, fz - c), (fx - s_, 0.03, fz + c),
            lambda x, y, s, t, z, wp: tone(PAPER, 2.6 + (x + y) % 2, x, y), cls='prop')

PUDDLES = [(-6.0, 14.2, 3.2, 1.0), (5.5, 19.0, 2.6, 0.8), (14.0, 13.4, 2.2, 0.7), (-16.0, 21.0, 2.0, 0.6), (0.3, 30.0, 1.6, 2.4)]
def puddle(X, Z):
    k = 0.0
    for (px_, pz, rx, rz) in PUDDLES:
        d = ((X - px_) / rx) ** 2 + ((Z - pz) / rz) ** 2 + (wn(3, X * 1.2, Z * 1.2) - 0.5) * 0.5
        if d < 1.0: k = max(k, 1.0 if d < 0.8 else 0.5)
    return k
from common import FONT
def stencil(col):
    """a faded stencilled 521 over the tunnel (numbers read in both languages)"""
    txt = '521'; sc = 5
    tw = sum(len(FONT[ch][0]) * sc + sc for ch in txt) - sc
    (cx, cy) = proj(0, 15.4, ZB)
    x0, y0 = int(cx - tw / 2), int(cy - 2.5 * sc)
    for i, ch in enumerate(txt):
        for r, row in enumerate(FONT[ch]):
            for c_, bit in enumerate(row):
                if bit != '1': continue
                for dy in range(sc):
                    for dx in range(sc):
                        x, y = x0 + c_ * sc + dx, y0 + r * sc + dy
                        if (dx == sc - 1 and c_ < len(row) - 1 and row[c_ + 1] == '1'): continue          # stencil bridges
                        if h32(x, y, 77) % 9 == 0: continue                                              # worn paint
                        col[y][x] = mix(col[y][x], (150, 168, 140), 0.55)
                        if r == 4 and dy == sc - 1 and h32(x, 78) % 4 == 0:                              # a drip
                            for k in range(1, 2 + h32(x, 79) % 4): col[y + k][x] = mix(col[y + k][x], (150, 168, 140), 0.4)
        x0 += len(FONT[ch][0]) * sc + sc
img = rs.render(INK, mirror=lambda x, y, wp: 0.6 * puddle(wp[0], wp[2]), overlay=stencil,
                light_gain=1.0, grime_gain=0.8, bloom=0.5, stain_gain=0.35, damp_gain=0.5)
img.save(f'{OUT}/hall.png')
print('done hall; core socket on screen at', [round(v) for v in proj(CORE[0], CORE[1], ZB)])
