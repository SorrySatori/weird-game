"""The sealed cellar under the Scraper (ScraperCellarScene), 1067x600, the shared camera (raster3d.py) -- Ortolan and
Dr. Elphi's old lab, shut for years, still powered. After the old AI picture (a dim lab: a tall glass column on the
left, shelves, a workbench under a hanging lamp, a schematic on the back wall, a panel of switches and a boiler at the
back right, a glass-dome apparatus on a console on the right, a stair down on the left, an arched door, pipes along
the ceiling) and the scene's text:

  left    the Lift-Mother's lower door in the left wall on a landing, the stair coming down from it (the way out),
          shelves of jars, the tall glass column with its brass coil
  back    a sealed arched door (boards nailed over it), the big blueprint of a dreamer's head wired to a game board,
          the workbench under the only lamp that still burns (tools, a board, helmet parts, papers), a stool;
          the switch panel with a few live indicators, the boiler with its gauge
  right   INFINITE FOLD'S MASTER BUILD: "two hands married into one machine" -- Ortolan's half all brass escapements
          and a glass case of little sealed cells, Elphi's half a lattice of dream-ports with cables, between them
          the cradle (a glass dome, the amber light breathing in it); a dust-stiff tarp half pulled off it; the
          helmet waiting on its hook
  floor   concrete tiles, a drain grate, cables snaking to the console, dust, a few papers
Underground: no daylight -- the lamp (warm), the cradle (amber), the indicators (green), the dark corners.

    python3 cellar_bg.py <outdir>   ->  cellar.png (= assets/images/backgrounds/ScraperBasement.png) + cellar_guides.png
"""
import sys, math
from common import h32
from shedkit import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = Raster()
WX, CH, ZB, ZN = 26.0, 20.0, 30.0, 6.0

CONC = ramp('#0d0e0b #131510 #1a1c16 #21241c #292c23 #32362b #3c4034 #474b3e #53584a')
TILE = ramp('#121310 #191a15 #20221b #282a22 #30332a #393c32 #43473b')
STEEL = ramp('#0b0c0b #111312 #181b19 #202421 #292d2a #333834 #3e433f #4a504b')
BRASS = ramp('#1f160a #33240f #4a3515 #63471c #7c5b25 #977232 #b08b44 #c6a35a')
WOODC = ramp('#110c08 #1a120c #241911 #2f2016 #3a281b #463121')
TARP = ramp('#16150f #1e1d16 #28261e #333027 #3e3a2f #4a4538 #565040')
GLASSC = ramp('#0f1715 #15201d #1c2a26 #243530 #2d413b #384e47')
CHALK = ramp('#10140f #161c15 #1d241c #252d23')
PAPER = ramp('#4a4637 #5e5946 #736d57 #888168 #9c957a')
AMBER = [(110, 60, 18), (170, 98, 30), (226, 146, 52), (255, 198, 104), (255, 236, 180)]
IND = [(40, 120, 70), (90, 200, 120), (200, 80, 50), (220, 170, 70)]
FOGC = (16, 18, 15)

LIGHTS = [((-1.0, 12.4, 24.6), 1.35, 18.0, 'w'),          # the lamp over the workbench
          ((15.4, 10.6, 20.4), 0.95, 11.0, 'a'),          # the cradle
          ((11.0, 6.0, 29.0), 0.3, 6.0, 'g'),             # the switch panel's indicators
          ((-24.0, 14.0, 21.6), 0.35, 7.0, 'g'),          # the lift's little lamp over its door
          ((0.0, 9.0, 2.0), 0.3, 30.0, 'w')]              # bounce


def lit(X, Y, Z, n):
    out = {'w': 0.0, 'a': 0.0, 'g': 0.0}
    for (lx, ly, lz), I, r, kind in LIGHTS:
        dx, dy, dz = lx - X, ly - Y, lz - Z
        d2 = dx * dx + dy * dy + dz * dz; d = math.sqrt(d2) + 1e-6
        if d > r: continue
        ndl = max(0.0, (dx * n[0] + dy * n[1] + dz * n[2]) / d)
        out[kind] += I * (0.25 + 0.75 * ndl) * (1 - d / r) ** 1.6
    return out


WARMC, AMBC, GRNC = (180, 136, 80), (230, 140, 50), (90, 170, 110)
def shade(r, base, X, Y, Z, n, x, y, k=4.4):
    L = lit(X, Y, Z, n)
    t = L['w'] + L['a'] + L['g'] * 0.6
    col = tone(r, base - 1.4 + k * t, x, y)
    if L['w'] > 0.06: col = mix(col, WARMC, min(0.16, L['w'] * 0.18))
    if L['a'] > 0.04: col = mix(col, AMBC, min(0.3, L['a'] * 0.45))
    if L['g'] > 0.04: col = mix(col, GRNC, min(0.25, L['g'] * 0.6))
    return col


def dusty(c, z): return mix(c, FOGC, max(0.0, min(0.25, (z - 20) / 40.0)))
FWD, UP, DOWN, RIGHT, LEFT = (0, 0, -1.0), (0, 1.0, 0), (0, -1.0, 0), (1.0, 0, 0), (-1.0, 0, 0)

# ---------------------------------------------------------------------------------------------------- the shell
def floor(x, y, s, t, z, wp):
    X, _, Z = wp
    tx, tz = math.floor(X / 1.8), math.floor(Z / 1.8)
    fx, fz = X / 1.8 - tx, Z / 1.8 - tz
    ex, ez = 0.9 * Z / F / 1.8, 0.9 * Z * Z / (F * CAMH) / 1.8
    v = 3.0 + (h32(tx, tz, 2) % 4) * 0.25 + (wn(0, X * 0.6, Z * 0.6) - 0.5) * 0.7
    if fx < ex or fz < ez: v -= 1.3
    if h32(tx, tz, 5) % 17 == 0: v -= 0.7                                                       # a cracked tile
    c = shade(TILE, v, X, 0, Z, UP, x, y)
    du = wn(2, X * 0.4, Z * 0.4) + 0.25 * (abs(X) / WX) ** 3 + 0.2 * max(0.0, (Z - 30) / 6)        # dust, thick by the walls
    if du > 0.62: c = mix(c, (58, 56, 46), min(0.4, (du - 0.62) * 1.5))
    return dusty(c, Z)
rs.quad((-WX, 0, ZN), (WX, 0, ZN), (-WX, 0, ZB), floor, cls='ground')
# the drain grate in the middle
def grate(x, y, s, t, z, wp):
    if (s * 14) % 1 < 0.45: return STEEL[0]
    return shade(STEEL, 3.0 if t > 0.05 and t < 0.95 else 2.0, *wp, UP, x, y)
rs.quad((-2.0, 0.02, 17.0), (2.0, 0.02, 17.0), (-2.0, 0.02, 19.6), grate, cls='ground')


def wall_conc(nrm, seed=0):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = Z if abs(nrm[0]) > 0.5 else X
        # cast concrete in lifts, tie holes, damp tide-mark at the foot, a painted dado
        v = 3.0 + (wn(0, u * 0.5, Y * 0.5) - 0.5) * 0.8 + (wn(1, u * 2.4, Y * 2.4) - 0.5) * 0.4
        if (Y % 3.2) < 0.08: v -= 0.8
        if h32(int(u / 2.4), int(Y / 3.2), seed) % 3 == 0 and abs((u % 2.4) - 1.2) < 0.1 and abs((Y % 3.2) - 1.6) < 0.1: v -= 1.4
        r_ = CONC
        if Y < 4.0: r_ = TILE; v -= 0.3                                                        # the dado
        if abs(Y - 4.0) < 0.1: v += 0.8
        c = shade(r_, v, X, Y, Z, nrm, x, y)
        if Y < 1.2 + 0.6 * wn(2, u * 0.7, 3): c = mix(c, (24, 26, 20), 0.4)                   # the damp foot
        return dusty(c, z)
    return sh
rs.quad((-WX, 0, ZB), (WX, 0, ZB), (-WX, CH, ZB), wall_conc(FWD, 1), cls='wall')
rs.quad((-WX, 0, ZN), (-WX, 0, ZB), (-WX, CH, ZN), wall_conc(RIGHT, 2), cls='wall')
rs.quad((WX, 0, ZN), (WX, 0, ZB), (WX, CH, ZN), wall_conc(LEFT, 3), cls='wall')
def ceil(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 2.2 + (wn(0, X * 0.5, Z * 0.5) - 0.5) * 0.7
    if (Z % 6.0) < 0.9: v -= 0.6                                                                # beams
    return dusty(shade(CONC, v, X, CH, Z, DOWN, x, y, k=3.4), z)
rs.quad((-WX, CH, ZN), (WX, CH, ZN), (-WX, CH, ZB), ceil, cls='ceil')
for zb in (11.0, 17.0, 23.0):
    rs.box(-WX, WX, CH - 1.2, CH, zb, zb + 0.9, lambda x, y, s, t, z, wp: dusty(shade(CONC, 2.0, *wp, FWD, x, y), z),
           lambda x, y, s, t, z, wp: CONC[1], bottom=lambda x, y, s, t, z, wp: dusty(shade(CONC, 1.6, *wp, DOWN, x, y), z), cls='ceil')

# pipes along the ceiling and down the walls
def pipe_z(X, Y, r, z0, z1, rr=STEEL, v0=2.6):
    def sh(x, y, s, t, z, wp):
        a = (s - 0.5) * 2
        v = v0 + 1.4 * (1 - a * a) - 0.6 * a + (1.0 if (wp[2] % 4.0) < 0.2 else 0)
        return dusty(shade(rr, v, *wp, (a, -0.5, -0.7), x, y), z)
    rs.quad((X - r, Y, z0), (X + r, Y, z0), (X - r, Y, z1), sh)
    rs.quad((X - r, Y - r, z0), (X - r, Y + r, z0), (X - r, Y - r, z1), lambda x, y, s, t, z, wp: dusty(shade(rr, v0 - 0.4 + t * 0.8, *wp, LEFT, x, y), z))
for k, (px_, py_, pr) in enumerate(((-17.0, 18.8, 0.55), (-15.6, 18.6, 0.4), (-6.0, 19.0, 0.7), (8.0, 18.7, 0.5), (9.4, 18.9, 0.35), (20.0, 18.6, 0.6))):
    pipe_z(px_, py_, pr, ZN, ZB, STEEL, 2.4)
for (px_, zz) in ((-24.6, 12.0), (-24.0, 27.6), (24.4, 27.0), (23.6, 14.0)):
    rs.line3((px_, 0, zz), (px_, CH, zz), lambda x, y, s, t, z, wp: dusty(shade(STEEL, 2.6 + (1.2 if (wp[1] % 3.0) < 0.2 else 0), *wp, FWD, x, y), z), w=0.6)

# ---------------------------------------------------------------------------------------------------- the left: the landing, the lift door, the stair
LAND = (-WX, -19.6, 8.0, 18.4, 26.0)                      # x0, x1, height, z0, z1
LDOOR = (19.6, 24.2, 8.0, 16.0)                          # the lift door in the left wall: z0, z1, sill, top
def landing_top(x, y, s, t, z, wp): return dusty(shade(STEEL, 2.6 + (0.8 if (wp[2] % 0.5) < 0.1 else 0), *wp, UP, x, y), z)
def landing_front(x, y, s, t, z, wp): return dusty(shade(STEEL, 1.6 + (0.9 if t > 0.92 else 0) - (0.6 if (wp[0] % 2.0) < 0.1 else 0), *wp, FWD, x, y), z)
rs.box(LAND[0], LAND[1], LAND[2] - 0.4, LAND[2], LAND[3], LAND[4], landing_front, landing_front, top=landing_top, bottom=lambda x, y, s, t, z, wp: STEEL[0])
for xx in (-21.0, -19.9):                                                                    # its legs
    rs.line3((xx, 0, LAND[3] + 0.3), (xx, LAND[2] - 0.4, LAND[3] + 0.3), lambda x, y, s, t, z, wp: dusty(shade(STEEL, 2.2, *wp, FWD, x, y), z), w=0.35)
# the stair down from the landing toward us along the left wall
NST = 10; SZ0, SZ1 = 12.6, LAND[3]
for i in range(NST):
    za = SZ1 - (i + 1) * (SZ1 - SZ0) / NST
    h = LAND[2] - (i + 1) * LAND[2] / NST + LAND[2] / NST
    def tread(x, y, s, t, z, wp, i=i): return dusty(shade(STEEL, 2.8 + (1.0 if s > 0.92 or (wp[0] % 0.6) < 0.12 else 0), *wp, UP, x, y), z)
    def riser(x, y, s, t, z, wp): return dusty(shade(STEEL, 1.4, *wp, FWD, x, y), z)
    rs.box(LAND[0], -20.6, h - LAND[2] / NST, h, za, za + (SZ1 - SZ0) / NST + 0.02, riser, riser, top=tread)
# its open side: a stringer, the railing (posts and a rail) down to the floor, and along the landing
rs.quad((-20.6, -0.2, SZ0), (-20.6, LAND[2] - 0.6, SZ1), (-20.6, 0.5, SZ0),
        lambda x, y, s, t, z, wp: dusty(shade(STEEL, 1.6 + (0.9 if t > 0.75 else 0), *wp, RIGHT, x, y), z))
RAIL = lambda x, y, s, t, z, wp: dusty(shade(BRASS, 3.0, *(wp or (0, 0, 20)), FWD, x, y), z)
rs.line3((-20.4, 3.4, SZ0), (-20.4, LAND[2] + 3.4, SZ1), RAIL, w=0.22)
rs.line3((-20.4, LAND[2] + 3.4, SZ1), (-19.8, LAND[2] + 3.4, LAND[4]), RAIL, w=0.22)
for k in range(6):
    zz = SZ0 + k * (SZ1 - SZ0) / 5; hh = (zz - SZ0) / (SZ1 - SZ0) * LAND[2]
    rs.line3((-20.4, hh, zz), (-20.4, hh + 3.4, zz), lambda x, y, s, t, z, wp: dusty(shade(STEEL, 2.4, *wp, FWD, x, y), z), w=0.16)
for zz in (LAND[3] + 2.6, LAND[3] + 5.2, LAND[4] - 0.2):
    rs.line3((-19.8, LAND[2], zz), (-19.8, LAND[2] + 3.4, zz), lambda x, y, s, t, z, wp: dusty(shade(STEEL, 2.4, *wp, FWD, x, y), z), w=0.16)
# the lift door: bronze leaves under an arch, the Lift-Mother's closed-eyed mask, a little lamp over it
def liftdoor(x, y, s, t, z, wp):
    X, Y, Z = wp
    u = (Z - LDOOR[0]) / (LDOOR[1] - LDOOR[0]); v = (Y - LDOOR[2]) / (LDOOR[3] - LDOOR[2])
    arch = 0.82 + 0.18 * math.sqrt(max(0.0, 1 - (2 * u - 1) ** 2))
    if v > arch: return None
    if v > arch - 0.05 or u < 0.05 or u > 0.95: return shade(BRASS, 2.0, X, Y, Z, RIGHT, x, y)
    if abs(u - 0.5) < 0.02: return BRASS[0]
    mv = ((u - 0.5) / 0.2) ** 2 + ((v - 0.55) / 0.2) ** 2                                         # the mask, eyes shut
    if mv < 1:
        if abs(v - 0.58) < 0.025 and 0.18 < abs(u - 0.5) / 0.2 < 0.7: return BRASS[1]
        return shade(BRASS, 3.6 - (v - 0.55) * 3, X, Y, Z, RIGHT, x, y)
    return shade(BRASS, 2.4 + (wn(0, Z * 3, Y * 3) - 0.5) * 0.8 - (0.6 if (v * 8) % 1 < 0.06 else 0), X, Y, Z, RIGHT, x, y)
rs.quad((-WX + 0.05, LDOOR[2], LDOOR[0]), (-WX + 0.05, LDOOR[2], LDOOR[1]), (-WX + 0.05, LDOOR[3], LDOOR[0]), liftdoor, cut=True)
rs.disc(-WX + 0.3, LDOOR[3] + 1.0, (LDOOR[0] + LDOOR[1]) / 2, 0.35, lambda x, y, s, t, z, wp: (110, 190, 140) if s * s + t * t < 0.5 else BRASS[2], cls='emit')

# ---------------------------------------------------------------------------------------------------- the back wall
# shelves of jars on the left of the back wall
for yb in (3.0, 6.0, 9.0, 12.0):
    rs.box(-25.6, -19.4, yb - 0.25, yb, ZB - 2.0, ZB - 0.1, lambda x, y, s, t, z, wp: dusty(shade(WOODC, 3.0, *wp, FWD, x, y), z),
           lambda x, y, s, t, z, wp: WOODC[1], top=lambda x, y, s, t, z, wp: dusty(shade(WOODC, 3.6, *wp, UP, x, y), z))
    xx = -25.2
    while xx < -19.8:
        w_ = 0.5 + (h32(int(xx * 10), int(yb), 3) % 4) * 0.15; hh = 0.9 + (h32(int(xx * 10), int(yb), 4) % 5) * 0.25
        tint = [(60, 80, 52), (88, 70, 40), (50, 62, 70), (90, 58, 52), (70, 74, 62)][h32(int(xx * 10), int(yb), 5) % 5]
        def jar(x, y, s, t, z, wp, tint=tint, hh=hh):
            if t > 0.86: return STEEL[2]                                                        # the lid
            v = 0.6 + (0.5 if abs(s - 0.3) < 0.1 else 0) + (0.25 if t < 0.6 else 0)
            return dusty(mix(tint, (20, 22, 18), 0.55 - v * 0.35), z)
        rs.box(xx, xx + w_, yb, yb + hh, ZB - 1.6, ZB - 1.1, jar, jar)
        xx += w_ + 0.12
# the tall glass column: murky fluid, a brass coil inside, brass caps
GC = (-16.8, 26.8, 1.7)
def glasscol(x, y, s, t, z, wp):
    X, Y, Z = wp
    a = (X - GC[0]) / GC[2]
    coil = abs(((Y * 0.55 + math.asin(max(-1, min(1, a))) / math.pi) % 1) - 0.5) < 0.09 and abs(a) < 0.6
    if coil: return shade(BRASS, 3.4 - abs(a) * 2, X, Y, Z, FWD, x, y)
    v = 2.0 + (1.0 - a * a) * 0.8 + (1.2 if abs(a + 0.55) < 0.07 else 0) + (wn(1, X * 3, Y * 2) - 0.5) * 0.4
    c = shade(GLASSC, v, X, Y, Z, FWD, x, y)
    if Y > 13.4: c = mix(c, (20, 24, 20), 0.5)                                                   # the fluid stops here
    return dusty(c, z)
rs.quad((GC[0] - GC[2], 2.2, GC[1]), (GC[0] + GC[2], 2.2, GC[1]), (GC[0] - GC[2], 15.2, GC[1]), glasscol)
for (y0, y1) in ((0.0, 2.2), (15.2, 16.6)):
    rs.box(GC[0] - GC[2] - 0.3, GC[0] + GC[2] + 0.3, y0, y1, GC[1] - 0.4, GC[1] + 1.6, lambda x, y, s, t, z, wp: dusty(shade(BRASS, 2.6 + (0.8 if t > 0.85 else 0), *wp, FWD, x, y), z),
           lambda x, y, s, t, z, wp: dusty(shade(BRASS, 1.8, *wp, RIGHT, x, y), z), top=lambda x, y, s, t, z, wp: dusty(shade(BRASS, 3.4, *wp, UP, x, y), z))
rs.line3((GC[0], 16.6, GC[1] + 0.6), (GC[0], CH, GC[1] + 0.6), lambda x, y, s, t, z, wp: dusty(shade(STEEL, 2.4, *wp, FWD, x, y), z), w=0.5)
# the sealed arched door: boards nailed across it
SD = (-13.6, -9.4, 8.6)
def sealed(x, y, s, t, z, wp):
    X, Y, Z = wp
    u = (X - SD[0]) / (SD[1] - SD[0]); v = Y / SD[2]
    arch = 0.8 + 0.2 * math.sqrt(max(0.0, 1 - (2 * u - 1) ** 2))
    if v > arch: return None
    for (bv, ang) in ((0.25, 0.08), (0.48, -0.1), (0.7, 0.06)):                                  # the boards
        if abs(v - bv - (u - 0.5) * ang) < 0.05:
            if abs(u - 0.1) < 0.02 or abs(u - 0.9) < 0.02: return STEEL[4]                        # nails
            return dusty(shade(WOODC, 3.6 + (wn(0, X * 4, Y) - 0.5), X, Y, Z, FWD, x, y), z)
    if v > arch - 0.06 or u < 0.06 or u > 0.94: return dusty(shade(CONC, 3.6, X, Y, Z, FWD, x, y), z)
    return dusty(shade(STEEL, 1.6 + (0.6 if (u * 3) % 1 < 0.05 else 0) + (wn(1, X * 2, Y * 2) - 0.5) * 0.6, X, Y, Z, FWD, x, y), z)
rs.quad((SD[0], 0, ZB - 0.06), (SD[1], 0, ZB - 0.06), (SD[0], SD[2], ZB - 0.06), sealed, cut=True)
# the blueprint: a dreamer's head in profile, wired to a game board of cells; chalk annotations as marks only
BP = (-7.0, 5.0, 7.0, 15.4)
def blueprint(x, y, s, t, z, wp):
    X, Y, Z = wp
    u, v = s, 1 - t
    if u < 0.025 or u > 0.975 or v < 0.03 or v > 0.97: return dusty(shade(WOODC, 3.2, X, Y, Z, FWD, x, y), z)
    c = shade(CHALK, 2.4 + (wn(0, X * 2, Y * 2) - 0.5) * 0.6, X, Y, Z, FWD, x, y)
    ln = mix(c, (150, 156, 140), 0.55)
    hx, hy = 0.3, 0.55
    d = math.hypot((u - hx) / 0.14, (v - hy) / 0.24)
    if abs(d - 1) < 0.06 and not (u > hx + 0.08 and v < hy - 0.05): return ln                     # the head's outline
    if abs(v - (hy - 0.24)) < 0.012 and hx - 0.02 < u < hx + 0.16: return ln
    for k in range(5):                                                                           # wires to the board
        yy = hy - 0.12 + k * 0.06
        if 0.42 < u < 0.62 and abs(v - (yy + (u - 0.42) * (0.5 - yy) * 0.6)) < 0.008: return ln
    if 0.64 < u < 0.92 and 0.25 < v < 0.75:                                                       # the board of cells
        if ((u - 0.64) / 0.035) % 1 < 0.12 or ((v - 0.25) / 0.0625) % 1 < 0.14: return ln
        if h32(int((u - 0.64) / 0.035), int((v - 0.25) / 0.0625), 3) % 7 == 0: return mix(c, (150, 156, 140), 0.3)
    if (v > 0.84 or v < 0.14) and (u * 40) % 1 < 0.6 and h32(int(u * 40), int(v * 30), 2) % 3: return mix(c, (150, 156, 140), 0.3)   # scribbles
    return dusty(c, z)
rs.quad((BP[0], BP[2], ZB - 0.08), (BP[1], BP[2], ZB - 0.08), (BP[0], BP[3], ZB - 0.08), blueprint)
# the workbench under the lamp: a scarred top, drawers, tools, a game board, a dismantled helmet, papers; a stool
WB = (-8.4, 6.0, 25.0, 28.0, 3.1)
def benchtop(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 3.2 + (wn(1, X * 0.8, Z * 4) - 0.5) * 0.8 - (0.7 if h32(int(X * 3), int(Z * 3), 2) % 19 == 0 else 0)
    return dusty(shade(WOODC, v, X, Y, Z, UP, x, y), z)
def benchfront(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 2.4 - (0.9 if (X - WB[0]) % 3.5 < 0.08 or abs(Y - 1.6) < 0.05 else 0) + (0.8 if abs((X - WB[0]) % 3.5 - 1.75) < 0.25 and abs(Y - 2.3) < 0.08 else 0)
    return dusty(shade(WOODC, v, X, Y, Z, FWD, x, y), z)
rs.box(WB[0], WB[1], 0, WB[4], WB[2], WB[3], benchfront, lambda x, y, s, t, z, wp: dusty(shade(WOODC, 1.8, *wp, RIGHT, x, y), z), top=benchtop)
def board(x, y, s, t, z, wp):
    return dusty(shade(WOODC, 4.4 if (int(s * 8) + int(t * 8)) % 2 else 2.0, *wp, UP, x, y), z)
rs.quad((-6.8, WB[4] + 0.02, 25.6), (-3.6, WB[4] + 0.02, 25.6), (-6.8, WB[4] + 0.02, 27.4), board)
for k, (px_, pz_, c_) in enumerate(((-5.9, 26.2, (150, 40, 34)), (-4.4, 26.6, (210, 200, 170)), (-5.2, 26.9, (150, 40, 34)))):
    rs.disc(px_, WB[4] + 0.4, pz_, 0.22, lambda x, y, s, t, z, wp, c_=c_: dusty(mix(c_, (0, 0, 0), 0.3 + t * 0.3), z))          # pawns
rs.disc(0.4, WB[4] + 0.7, 26.2, 0.75, lambda x, y, s, t, z, wp: dusty(shade(STEEL, 3.4 - t * 2 - s * 0.8, 0.4, 3.8, 26.2, (s, -t, -0.6), x, y), z) if t < 0.3 else None)   # a helmet shell
for k in range(5):
    rs.quad((1.6 + k * 0.7, WB[4] + 0.02, 25.4 + (k % 2) * 0.3), (2.4 + k * 0.7, WB[4] + 0.02, 25.3 + (k % 2) * 0.3), (1.7 + k * 0.7, WB[4] + 0.02, 26.4),
            lambda x, y, s, t, z, wp: dusty(shade(PAPER, 2.6 + (wn(0, x * 0.5, y) - 0.5), *wp, UP, x, y), z))               # papers
for (tx_, ln_) in ((4.4, 1.4), (5.2, 1.0)):
    rs.line3((tx_, WB[4] + 0.05, 25.8), (tx_ + 0.3, WB[4] + 0.05, 25.8 + ln_), lambda x, y, s, t, z, wp: STEEL[4], w=0.14)   # tools
rs.box(-1.2, 0.6, 0, 2.2, 22.0, 23.6, lambda x, y, s, t, z, wp: dusty(shade(WOODC, 2.0, *wp, FWD, x, y), z),
       lambda x, y, s, t, z, wp: WOODC[1], top=lambda x, y, s, t, z, wp: dusty(shade(WOODC, 3.6, *wp, UP, x, y), z))               # the stool's seat
for (lx_, lz_) in ((-1.0, 22.2), (0.4, 22.2), (-1.0, 23.4), (0.4, 23.4)):
    rs.line3((lx_, 0, lz_), (lx_, 2.0, lz_), lambda x, y, s, t, z, wp: dusty(shade(WOODC, 2.4, *wp, FWD, x, y), z), w=0.2)
# the lamp: a green enamel shade on its cord, the bulb
LMP = (-1.0, 12.4, 25.0)
rs.line3((LMP[0], CH, LMP[2]), (LMP[0], LMP[1] + 1.2, LMP[2]), lambda x, y, s, t, z, wp: STEEL[1], w=0.08)
rs.disc(LMP[0], LMP[1] + 0.3, LMP[2], 1.6, lambda x, y, s, t, z, wp: (dusty(tone(GLASSC, 4.0 - (t + 0.6) * 2.6 - abs(s) * 0.8, x, y), z)
        if abs(s) < 0.25 + (t + 0.85) * 0.75 else None) if -0.85 < t < 0.12 else None)
rs.disc(LMP[0], LMP[1] - 0.25, LMP[2] - 0.1, 0.5, lambda x, y, s, t, z, wp: (255, 236, 190) if t > -0.2 else None, cls='emit')
# the switch panel with its live indicators, cables down to the floor; the boiler with its gauge
SP = (8.0, 13.6, 2.2, 11.4)
def panel(x, y, s, t, z, wp):
    X, Y, Z = wp
    u, v = s, 1 - t
    if u < 0.04 or u > 0.96 or v < 0.03 or v > 0.97: return dusty(shade(STEEL, 3.0, X, Y, Z, FWD, x, y), z)
    cu, cv = int(u * 6), int(v * 9)
    fu, fv = (u * 6) % 1, (v * 9) % 1
    if 0.3 < fu < 0.7 and 0.35 < fv < 0.65:
        k = h32(cu, cv, 7) % 9
        if k == 0: return IND[1]
        if k == 1: return IND[3]
        if k == 2 and cv % 3 == 0: return IND[2]
        return STEEL[1]
    if 0.42 < fu < 0.58 and 0.05 < fv < 0.32: return dusty(shade(STEEL, 4.4, X, Y, Z, FWD, x, y), z)       # toggles
    return dusty(shade(STEEL, 2.0 + (wn(0, X * 3, Y * 3) - 0.5) * 0.5, X, Y, Z, FWD, x, y), z)
rs.box(SP[0], SP[1], SP[2], SP[3], ZB - 1.2, ZB, panel, lambda x, y, s, t, z, wp: dusty(shade(STEEL, 1.6, *wp, RIGHT, x, y), z), cls='emit')
rs.box(SP[0] - 0.3, SP[1] + 0.3, 0, SP[2], ZB - 1.6, ZB, lambda x, y, s, t, z, wp: dusty(shade(STEEL, 1.6, *wp, FWD, x, y), z),
       lambda x, y, s, t, z, wp: STEEL[1], top=lambda x, y, s, t, z, wp: dusty(shade(STEEL, 2.6, *wp, UP, x, y), z))
BO = (19.0, 27.2, 2.4)
def boiler(x, y, s, t, z, wp):
    X, Y, Z = wp
    a = (X - BO[0]) / BO[2]
    v = 1.6 + (1 - a * a) * 1.6 - a * 0.6 + (1.0 if (Y % 3.0) < 0.2 else 0) + (0.8 if (Y % 3.0) < 0.35 and int(a * 6) % 2 == 0 else 0)
    gd = math.hypot(X - (BO[0] - 0.6), Y - 7.6)
    if gd < 0.75:
        if gd > 0.62: return shade(BRASS, 3.6, X, Y, Z, FWD, x, y)
        if abs((X - (BO[0] - 0.6)) * 0.6 + (Y - 7.6) * 0.8) < 0.06 and gd < 0.5: return (40, 30, 24)
        return dusty(mix(PAPER[3], (0, 0, 0), 0.25), z)                                          # the gauge's face
    c = shade(BRASS if Y < 1.4 else STEEL, v, X, Y, Z, FWD, x, y)
    ru = wn(2, X * 1.5, Y * 0.5)
    if ru > 0.62: c = mix(c, tone(RUSTY, 2.0, x, y), 0.5)
    return dusty(c, z)
rs.quad((BO[0] - BO[2], 0, BO[1]), (BO[0] + BO[2], 0, BO[1]), (BO[0] - BO[2], 13.0, BO[1]), boiler)
rs.disc(BO[0], 13.0, BO[1] + 0.2, BO[2], lambda x, y, s, t, z, wp: dusty(tone(STEEL, 3.0 - t * 1.6 - s * 0.5, x, y), z) if t < 0.05 else None)
rs.line3((BO[0], 14.6, BO[1] + 0.6), (BO[0], CH, BO[1] + 0.6), lambda x, y, s, t, z, wp: dusty(shade(STEEL, 2.2, *wp, FWD, x, y), z), w=0.7)

# ---------------------------------------------------------------------------------------------------- the right: Infinite Fold's master build
MB = (9.0, 21.6, 19.0, 22.6)           # x0, x1, z0 (its front), z1
MBH = 8.6                             # the top of its two halves
CR = (15.3, 20.6, 1.15)               # the cradle (dome): centre x, z, radius; it sits on the top at MBH
def mb_base(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 1.8 + (wn(0, X * 2, Y * 2) - 0.5) * 0.6 - (0.9 if abs(Y - 3.9) < 0.06 or (X - MB[0]) % 3.1 < 0.07 else 0)
    if abs(Y - 2.0) < 0.12 and ((X - MB[0]) % 3.1) > 1.2 and ((X - MB[0]) % 3.1) < 1.9: v += 1.2              # drawer pulls
    return dusty(shade(STEEL, v, X, Y, Z, FWD, x, y), z)
rs.box(MB[0], MB[1], 0, 4.0, MB[2], MB[3], mb_base, lambda x, y, s, t, z, wp: dusty(shade(STEEL, 1.4, *wp, LEFT, x, y), z),
       top=lambda x, y, s, t, z, wp: dusty(shade(STEEL, 2.4, *wp, UP, x, y), z))
# Ortolan's half: a brass frame round a glass case of little sealed cells, escapement wheels below it
def ortolan_half(x, y, s, t, z, wp):
    X, Y, Z = wp
    u, v = (X - MB[0]) / 5.4, (Y - 4.0) / (MBH - 4.0)
    if u < 0.05 or u > 0.95 or v < 0.05 or v > 0.95: return dusty(shade(BRASS, 3.0 + (0.8 if v > 0.95 else 0), X, Y, Z, FWD, x, y), z)
    if v < 0.38:                                                                                      # the escapements
        for (gx, gy, gr) in ((0.25, 0.2, 0.15), (0.55, 0.22, 0.12), (0.8, 0.18, 0.1)):
            d = math.hypot((u - gx) * 1.4, v - gy) / gr
            if d < 1:
                tooth = (math.atan2(v - gy, (u - gx) * 1.4) * 8 / math.pi) % 1 < 0.5
                if d > 0.8 and tooth: return BRASS[1]
                if d < 0.25: return BRASS[6]
                return dusty(shade(BRASS, 3.8 - d * 1.2, X, Y, Z, FWD, x, y), z)
        return dusty(shade(STEEL, 0.8, X, Y, Z, FWD, x, y), z)
    cu, cv = int((u - 0.05) / 0.9 * 7), int((v - 0.4) / 0.55 * 5)                                    # the board of sealed cells
    fu, fv = ((u - 0.05) / 0.9 * 7) % 1, ((v - 0.4) / 0.55 * 5) % 1
    if fu < 0.12 or fv < 0.14: return dusty(shade(BRASS, 2.2, X, Y, Z, FWD, x, y), z)
    k = h32(cu, cv, 11) % 6
    c = [(36, 44, 40), (44, 52, 46), (60, 50, 34), (34, 40, 38), (80, 64, 40), (40, 48, 44)][k]
    if fu + fv * 0.4 < 0.32: c = mix(c, (150, 160, 150), 0.25)                                         # glass glint
    return dusty(c, z)
rs.quad((MB[0], 4.0, MB[2] - 0.05), (MB[0] + 5.4, 4.0, MB[2] - 0.05), (MB[0], MBH, MB[2] - 0.05), ortolan_half)
# Elphi's half: a lattice of dream-ports, a few cables plugged in, hanging in loops
def elphi_half(x, y, s, t, z, wp):
    X, Y, Z = wp
    u, v = (X - (MB[1] - 5.6)) / 5.6, (Y - 4.0) / (MBH - 4.0)
    if u < 0.04 or u > 0.96 or v < 0.05 or v > 0.95: return dusty(shade(STEEL, 3.0, X, Y, Z, FWD, x, y), z)
    fu, fv = (u * 12) % 1, (v * 9) % 1
    d = math.hypot(fu - 0.5, fv - 0.5)
    if d < 0.3:
        if d > 0.2: return dusty(shade(BRASS, 3.4, X, Y, Z, FWD, x, y), z)
        return (10, 12, 11) if h32(int(u * 12), int(v * 9), 4) % 11 else (60, 120, 80)
    return dusty(shade(STEEL, 1.8, X, Y, Z, FWD, x, y), z)
rs.quad((MB[1] - 5.6, 4.0, MB[2] - 0.05), (MB[1], 4.0, MB[2] - 0.05), (MB[1] - 5.6, MBH, MB[2] - 0.05), elphi_half)
rs.box(MB[0], MB[1], 4.0, MBH + 0.4, MB[2], MB[3], lambda x, y, s, t, z, wp: STEEL[1],
       lambda x, y, s, t, z, wp: dusty(shade(STEEL, 1.4, *wp, LEFT, x, y), z), top=lambda x, y, s, t, z, wp: dusty(shade(STEEL, 2.6, *wp, UP, x, y), z))
for k in range(3):                                                                                     # cables from the ports, sagging to the floor
    cx_ = MB[1] - 4.6 + k * 1.7
    rs.line3((cx_, 5.0 + (k % 3) * 1.0, MB[2] - 0.2), (cx_ - 1.4 + k * 0.4, 0.15, MB[2] - 1.6 - k * 0.3), lambda x, y, s, t, z, wp: STEEL[1], w=0.14, sag=-0.6)
for k in range(3):                                                                                     # ...and snaking off across the floor
    rs.line3((MB[0] + 2 + k, 0.08, MB[2] - 0.4), (MB[0] - 6 - k * 3, 0.08, MB[2] - 3.5 - k * 1.5), lambda x, y, s, t, z, wp: STEEL[1], w=0.12, sag=0.0)
# the cradle: a brass collar, a glass dome, the amber light in it
rs.box(CR[0] - 1.6, CR[0] + 1.6, MBH + 0.4, MBH + 1.0, CR[1] - 1.4, CR[1] + 1.4, lambda x, y, s, t, z, wp: shade(BRASS, 3.4 + (0.8 if t > 0.7 else 0), *wp, FWD, x, y),
       lambda x, y, s, t, z, wp: shade(BRASS, 2.2, *wp, LEFT, x, y), top=lambda x, y, s, t, z, wp: shade(BRASS, 4.0, *wp, UP, x, y))
def dome(x, y, s, t, z, wp):
    if t > 0.12: return None
    r_ = math.hypot(s, t + 0.5)
    if r_ < 0.42: return AMBER[3] if r_ < 0.2 else AMBER[2]
    if r_ < 0.6: return AMBER[1]
    if abs(s + 0.45) < 0.08 and t < -0.3: return (190, 190, 170)                                         # the glint on the glass
    return mix(GLASSC[2], AMBER[0], 0.35)
rs.disc(CR[0], MBH + 1.0, CR[1], CR[2] * 1.4, dome, cls='emit')
# the helmet on its hook beside the rig
rs.line3((MB[1] + 0.5, 9.6, MB[2] + 0.4), (MB[1] + 0.5, 8.6, MB[2] + 0.4), lambda x, y, s, t, z, wp: BRASS[3], w=0.14)
rs.disc(MB[1] + 0.5, 7.9, MB[2] + 0.4, 0.8, lambda x, y, s, t, z, wp: (shade(STEEL, 3.8 - t * 2.2 - s * 0.8, MB[1] + 0.5, 7.9, MB[2], (s, -t, -0.6), x, y)
        if not (0.05 < t < 0.3) else (40, 72, 58)) if t < 0.5 else None)
rs.line3((MB[1] + 0.5, 7.2, MB[2] + 0.4), (MB[1] - 0.6, 4.6, MB[2] - 0.2), lambda x, y, s, t, z, wp: STEEL[1], w=0.1, sag=-0.4)
# the tarp: stiff with dust, thrown over Ortolan's half and slipping off it, piled on the floor at the left
def tarp(x, y, s, t, z, wp):
    X, Y, Z = wp
    edge = MB[0] + 3.6 + 1.2 * math.sin(Y * 0.9) + 0.6 * wn(0, Y * 2, 1)                              # its ragged right edge
    if X > edge: return None
    if Y < 0.3 + 1.4 * max(0.0, (X - MB[0] + 1.6) / 2.0) * 0 and X > MB[0] + 1: return None
    fold = math.sin(X * 2.6 + Y * 0.5 + 2 * wn(1, X * 0.6, Y * 0.6))
    v = 2.6 + fold * 1.2 + (wn(2, X * 3, Y * 3) - 0.5) * 0.6 + (0.5 if Y > MBH - 0.6 else 0) - (0.8 if fold < -0.7 else 0)
    return dusty(shade(TARP, v, X, Y, Z, (fold * 0.4, 0.3, -0.8), x, y), z)
rs.quad((MB[0] - 0.9, 0.0, MB[2] - 0.35), (MB[0] + 5.2, 0.0, MB[2] - 0.35), (MB[0] - 0.9, MBH + 0.6, MB[2] - 0.35), tarp, cut=True)
rs.quad((MB[0] - 0.9, MBH + 0.6, MB[2] - 0.35), (MB[0] + 4.4, MBH + 0.6, MB[2] - 0.35), (MB[0] - 0.9, MBH + 0.6, MB[3] - 0.4),
        lambda x, y, s, t, z, wp: dusty(shade(TARP, 3.6 + math.sin(wp[0] * 2.2) * 0.6, *wp, UP, x, y), z))
for k in range(4):
    rs.disc(MB[0] - 1.2 + k * 0.5, 0.35 + (k % 2) * 0.15, MB[2] - 1.0 - (k % 3) * 0.4, 0.55,
            lambda x, y, s, t, z, wp: dusty(tone(TARP, 3.4 - t * 1.6 - s * 0.6, x, y), z) if t < 0.25 else None)
# things left on the floor: crates by the stair, a toolbox, papers, a coil of cable, a chair knocked over by the rig
def crate(X, Z, w_, h_, seed):
    sh = lambda v: (lambda x, y, s, t, z, wp: dusty(shade(WOODC, v + (0.8 if (s * 4) % 1 < 0.08 or t < 0.06 or t > 0.94 else 0)
                                                            + (wn(0, wp[0] * 2 + wp[2] * 2, wp[1] * 3) - 0.5) * 0.7, *wp, FWD, x, y), z))
    rs.box(X - w_, X + w_, 0, h_, Z - w_, Z + w_, sh(2.6), sh(1.8), top=sh(3.4))
crate(-13.4, 19.4, 1.4, 2.6, 1); crate(-11.0, 20.6, 1.1, 2.0, 2); crate(-13.0, 19.6, 0.9, 4.4, 3)
rs.box(-6.2, -4.2, 0, 1.0, 16.6, 17.6, lambda x, y, s, t, z, wp: dusty(shade(RUSTY, 3.0, *wp, FWD, x, y), z),
       lambda x, y, s, t, z, wp: dusty(shade(RUSTY, 2.0, *wp, RIGHT, x, y), z), top=lambda x, y, s, t, z, wp: dusty(shade(RUSTY, 3.8, *wp, UP, x, y), z))   # a toolbox
for k in range(9):                                                                                     # papers drifted across the floor
    px_ = -9 + (h32(k, 90) % 180) / 10.0; pz_ = 15.0 + (h32(k, 91) % 90) / 10.0; a_ = (h32(k, 92) % 60) / 100.0
    rs.quad((px_, 0.03, pz_), (px_ + 1.0, 0.03, pz_ + a_), (px_ - a_ * 0.5, 0.03, pz_ + 0.8),
            lambda x, y, s, t, z, wp: dusty(shade(PAPER, 1.6 + (wn(0, wp[0] * 5, wp[2] * 5) - 0.5), *wp, UP, x, y), z))
for k in range(10):                                                                                    # a coil of cable
    a0 = k * 0.7
    rs.line3((5.6 + math.cos(a0) * 1.0, 0.12, 17.0 + math.sin(a0) * 0.6), (5.6 + math.cos(a0 + 0.7) * 1.0, 0.12, 17.0 + math.sin(a0 + 0.7) * 0.6),
             lambda x, y, s, t, z, wp: STEEL[1], w=0.16)
rs.box(5.2, 7.6, 0, 0.5, 15.8, 17.4, lambda x, y, s, t, z, wp: dusty(shade(WOODC, 2.4, *wp, FWD, x, y), z),
       lambda x, y, s, t, z, wp: WOODC[1], top=lambda x, y, s, t, z, wp: dusty(shade(WOODC, 3.4, *wp, UP, x, y), z)) if False else None
# the chair on its back before the rig (someone left in a hurry, long ago)
rs.quad((5.6, 0.2, 18.4), (7.6, 0.2, 18.2), (5.4, 1.8, 19.6), lambda x, y, s, t, z, wp: dusty(shade(WOODC, 2.8, *wp, (0, 0.6, -0.8), x, y), z))
rs.quad((7.6, 0.2, 18.2), (7.8, 0.3, 16.4), (7.6, 1.6, 18.2), lambda x, y, s, t, z, wp: dusty(shade(WOODC, 2.0, *wp, FWD, x, y), z))
for (lx_, lz_) in ((5.8, 18.6), (7.4, 18.4)):
    rs.line3((lx_, 0.3, lz_), (lx_ - 0.2, 1.4, lz_ - 1.8), lambda x, y, s, t, z, wp: dusty(shade(WOODC, 2.6, *wp, FWD, x, y), z), w=0.18)

# cobwebs in the upper corners
def cobweb(cx, cz, side):
    for k in range(7):
        a = k / 6 * math.pi / 2
        rs.line3((cx, CH - 0.1, cz), (cx - side * math.cos(a) * 3.0, CH - 0.1 - math.sin(a) * 3.0, cz), lambda x, y, s, t, z, wp: (70, 72, 64), w=0.03)
    for j in (1.0, 2.0):
        for k in range(6):
            a0, a1 = k / 6 * math.pi / 2, (k + 1) / 6 * math.pi / 2
            rs.line3((cx - side * math.cos(a0) * j, CH - 0.1 - math.sin(a0) * j, cz), (cx - side * math.cos(a1) * j, CH - 0.1 - math.sin(a1) * j, cz),
                     lambda x, y, s, t, z, wp: (62, 64, 56), w=0.03, sag=0.15)
cobweb(-WX + 0.1, ZB - 0.2, -1); cobweb(WX - 0.1, ZB - 0.2, 1)

img = rs.render(INK, fog=lambda z: 0.0, light_gain=0.5, grime_gain=0.55, bloom=0.4, stain_gain=0.25, damp_gain=0.25)
img.save(f'{OUT}/cellar.png')

def P(X, Y, Z): return tuple(int(round(v)) for v in proj(X, Y, Z))
print('stair foot', P(-20.6, 0, SZ0), P(LAND[0], 0, SZ0), 'landing edge', P(LAND[1], LAND[2], LAND[3]), P(LAND[1], LAND[2], LAND[4]))
print('lift door', P(-WX, LDOOR[2], LDOOR[0]), P(-WX, LDOOR[3], LDOOR[1]))
print('master build', P(MB[0], 0, MB[2]), P(MB[1], MBH, MB[2]), 'dome', P(CR[0], MBH + 1.0, CR[1]))
g = img.copy(); gp = g.load()
for y in range(600):
    for x in range(1067):
        if x % 50 == 0 or y % 50 == 0: gp[x, y] = (255, 0, 255) if (x % 100 == 0 or y % 100 == 0) else (120, 0, 120)
g.save(f'{OUT}/cellar_guides.png')
print('done cellar')
