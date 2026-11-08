"""The Scraper's backyard (ScraperBackyardScene), 1067x600, overcast day, the shared camera (raster3d.py).

An old transit yard behind the Scraper, abandoned for decades, under the huge rusty pipes that arch over it (the
composition of the old AI picture: a giant vertical pipe on the left with its elbow turning off into the sky, a
giant column on the right, a great horizontal pipe crossing high from it and coming down; more pipes behind, the
city's back walls in the haze beyond). The yard's concrete still carries the faded bay lines of the buses; the
peculiar moss of the yard (the "mnemonic" moss, WORLD_HISTORY) grows in the joints and in soft carpets.

The bus: a Before-Time double-decker sunk into the ground up to its upper deck (the inside is AbandonedBusScene: the
lower deck's windows full of earth, the upper floor fallen in). Front on the right: a ramp dug down to its front door
(the way in); the down-pipe has come down on its roof at the rear, crushing it (the torn hole inside). Creepers and
moss use it as a trellis, a few pale shelf fungi on its flank (the journal's "strange growths"). On the left, the
corner of the Scraper's own rear wall with the back door (the way back inside).

    python3 backyard_bg.py <outdir>   ->  backyard.png (= assets/images/backgrounds/ScraperBackyard.png) + backyard_guides.png
"""
import sys, math
from common import h32, make_noise
from shedkit import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = Raster()

PAINTB = ramp('#1d1c17 #29271f #36332a #444035 #534e41 #635d4e #746d5c #877f6b')   # the bus's faded cream
RUSTP = ramp('#120b07 #1b110b #25170f #301e13 #3b2518 #472d1d #533623 #60402a #6d4b33')    # the pipes: dark iron, rust
MOSSY = ramp('#141b13 #1c261a #253222 #2f3e2a #3a4b33 #47593d #556848')
MNEM = ramp('#1a241e #212d26 #29372f #324238 #3c4e43')                              # the mnemonic moss, a cool sheen
BAYL = (128, 112, 70)                                                               # the faded bay paint
EARTHY = ramp('#16120d #1f1912 #292118 #342a1f #403427 #4d3f2f')
DECO = ramp('#151713 #1c1f19 #24271f #2c3027 #353a2f #3f4438 #4a5042')             # the Scraper's stone
DOORW = ramp('#120c08 #1b120c #251911 #312116 #3d291b')

# ---------------------------------------------------------------------------------------------------- the camera's world
BUS_Z0, BUS_Z1 = 21.0, 31.0          # the bus's near and far side
BUS_X0, BUS_X1 = -19.0, 20.0         # rear (left) .. front (right)
SUNK = 7.6                           # how deep it has sunk: the ground cuts it at its upper floor
ROOF = 8.4                           # the roof above the ground (its crown)
DOORX = (13.6, 16.8)                 # the front door (in the near side, down in the ramp)
CRUSH = -11.0                        # where the down-pipe has come down on the roof
PIT = (DOORX[0] - 1.6, 27.0, 16.4, BUS_Z0)   # the pit dug down to the door: x0, x1, z0, z1
RAMPX = DOORX[1] + 1.8               # where its ramp reaches the pit's floor
FLOOR = -SUNK + 0.4

def fog(z): return fog_of(z)


# ---------------------------------------------------------------------------------------------------- sky + the city behind
_s1, _s2 = make_noise(13, 81, 1067, 600), make_noise(48, 82, 1067, 600)
def daysky(x, y, s=0, t=0, z=0, wp=None):
    """the overcast day: a bright, hazy cloud ceiling, a touch darker overhead, long soft cloud bands"""
    tt = max(0.0, min(1.0, y / HY))
    v = 3.4 + 2.8 * tt ** 1.2 + (_s2(x * 0.55, y * 2.6) - 0.5) * 1.5 + (_s1(x * 0.5, y * 2.4) - 0.5) * 0.5
    return tone(SKY, v, x, y)
rs.quad((-1400, 800, 600), (1400, 800, 600), (-1400, -300, 600), daysky, cls='sky')
for k in range(16):                                                                  # the back walls of the city, in haze
    x0 = -110 + k * 15 + (h32(k, 1) % 7); w_ = 10 + h32(k, 2) % 9
    zz = 75 + (h32(k, 3) % 5) * 14; ht = 22 + h32(k, 4) % 30
    base = [concrete(3.0, STONE), concrete(3.4, STUCCO), corrugated(3.0, METAL, 0.6)][h32(k, 5) % 3]
    rs.box(x0, x0 + w_, 0, ht, zz, zz + 12, facade(base, bay=3.4, floors=3.4, y0=1.0, seed=k + 20), concrete(2.4), cls='wall')
for k in range(6):                                                                   # taller towers further off: spires
    x0 = -70 + k * 27 + (h32(k, 6) % 9); w_ = 7 + h32(k, 7) % 6; zz = 150 + (h32(k, 8) % 3) * 20; ht = 48 + h32(k, 9) % 40
    rs.box(x0, x0 + w_, 0, ht, zz, zz + 10, facade(concrete(3.2, STONE), bay=3.0, floors=3.2, seed=k + 60), concrete(2.6), cls='wall')
    rs.quad((x0, ht, zz), (x0 + w_, ht, zz), (x0 + w_ / 2, ht + 10 + h32(k, 10) % 12, zz),
            lambda x, y, s, t, z, wp: fogged(tone(STONE, 2.6, x, y), z), clip=lambda a, b: a + b <= 1.0 and b <= 1.0, cls='wall')


# ---------------------------------------------------------------------------------------------------- pipes
def _frame(A, B):
    ax = (B[0] - A[0], B[1] - A[1], B[2] - A[2]); L = math.sqrt(sum(c * c for c in ax)) or 1
    a = (ax[0] / L, ax[1] / L, ax[2] / L)
    ref = (0, 1, 0) if abs(a[1]) < 0.9 else (0, 0, 1)
    u = (a[1] * ref[2] - a[2] * ref[1], a[2] * ref[0] - a[0] * ref[2], a[0] * ref[1] - a[1] * ref[0])
    ul = math.sqrt(sum(c * c for c in u)); u = (u[0] / ul, u[1] / ul, u[2] / ul)
    v = (a[1] * u[2] - a[2] * u[1], a[2] * u[0] - a[0] * u[2], a[0] * u[1] - a[1] * u[0])
    return a, u, v, L


def pipe_sh(A, B, r, seed, ring=6.0, t0=0.0, moss=True):
    """overcast light on a cylinder: lit on top, dark below, flange rings, rust in runs, moss on the top of the
    horizontal ones"""
    a, u, v, L = _frame(A, B)
    horiz = abs(a[1]) < 0.5
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        q = (X - A[0], Y - A[1], Z - A[2])
        along = q[0] * a[0] + q[1] * a[1] + q[2] * a[2]
        n = (q[0] - a[0] * along, q[1] - a[1] * along, q[2] - a[2] * along)
        nl = math.sqrt(sum(c * c for c in n)) or 1; n = (n[0] / nl, n[1] / nl, n[2] / nl)
        lum = 0.45 + 0.4 * n[1] + 0.16 * (-n[2]) - 0.06 * n[0]
        ang = math.atan2(n[0] * v[0] + n[1] * v[1] + n[2] * v[2], n[0] * u[0] + n[1] * u[1] + n[2] * u[2]); arc = ang * r
        grain = (wn(0, (along + t0) * 0.45, arc * 0.45 + seed * 7) - 0.5) * 1.2 + (wn(3, (along + t0) * 2.2, arc * 2.2 + seed * 7) - 0.5) * 0.7
        v_ = 0.9 + 5.4 * lum + grain
        al = along + t0
        if ring and (al % ring) < 0.45: v_ += 0.9 if (al % ring) < 0.12 else -0.4                     # flange rings
        if ring and abs((al % ring) - 0.32) < 0.06 and h32(int(math.atan2(n[1], n[0]) * 6), int(al / ring), 3) % 2 == 0: v_ += 1.1   # bolts
        c = tone(RUSTP, v_, x, y)
        sc = 0.6 * wn(2, al * 2.2, arc * 2.2 + seed * 7) + 0.4 * wn(1, al * 6, arc * 6 + seed)          # scaling: small dark flakes
        if sc > 0.64: c = tone(RUSTP, v_ - 0.9 + (wn(1, al * 9, arc * 9) - 0.5) * 0.8, x, y)
        elif sc > 0.625 and h32(int(al * 12), int(arc * 12), seed) % 3 == 0: c = tone(RUSTP, v_ + 0.8, x, y)   # their lifted rims
        if not horiz and wn(1, arc * 1.6 + seed * 7, Y * 0.1) > 0.58 and wn(3, arc * 6, Y * 0.4) > 0.42:   # runs of rust and soot down it
            c = mix(c, (30, 20, 14), 0.3)
        if horiz and n[1] < -0.2 and wn(3, al * 5.0, seed) > 0.55: c = mix(c, RUSTP[1], 0.45)          # drip line under it
        if moss and horiz and n[1] > 0.55 and wn(1, al * 1.2, seed + 5) > 0.42:                         # moss along its top
            c = tone(MOSSY, 2.4 + n[1] * 2.2 + (wn(0, al * 4, seed) - 0.5) * 1.4, x, y)
        if not horiz and Y < 2.4: c = mix(c, (20, 22, 16), (2.4 - Y) / 2.4 * 0.55)                       # dirt splash at the foot
        return fogged(c, z)
    return sh


def pipe(A, B, r, seed=0, n=24, ring=6.0, t0=0.0, moss=True, cls='prop'):
    a, u, v, L = _frame(A, B)
    sh = pipe_sh(A, B, r, seed, ring, t0, moss)
    obj = rs.obj()
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        P0 = tuple(A[k] + r * (math.cos(a0) * u[k] + math.sin(a0) * v[k]) for k in range(3))
        P1 = tuple(A[k] + r * (math.cos(a1) * u[k] + math.sin(a1) * v[k]) for k in range(3))
        P3 = tuple(P0[k] + (B[k] - A[k]) for k in range(3))
        rs.quad(P0, P1, P3, sh, obj=obj, cls=cls)
    return L


def elbow(C, d1, d2, R, r, seed=0, steps=7):
    """a 90-degree bend round centre C: from C + R*d1 to C + R*d2 (d1, d2 unit axes)"""
    pts = [tuple(C[k] + R * (math.cos(t * math.pi / 2) * d1[k] + math.sin(t * math.pi / 2) * d2[k]) for k in range(3)) for t in [i / steps for i in range(steps + 1)]]
    for A, B in zip(pts, pts[1:]): pipe(A, B, r, seed, n=20, ring=0)


def drape(P, ln, seed, kind='vine'):
    """creepers / old cables hanging off a pipe"""
    for k in range(3):
        dx = (h32(seed, k) % 10 - 5) * 0.12
        L_ = ln * (0.6 + (h32(seed, k, 2) % 5) * 0.12)
        sh = (lambda x, y, s, t, z, wp: fogged(tone(MOSSY, 1.6 + (1.2 if (x + y) % 3 == 0 else 0) - t * 0.6, x, y), z)) if kind == 'vine' \
            else (lambda x, y, s, t, z, wp: fogged((22, 20, 18), z))
        rs.line3((P[0] + dx, P[1], P[2]), (P[0] + dx * 2 + 0.2, P[1] - L_, P[2] - 0.2), sh, w=0.16 if kind == 'vine' else 0.09, sag=-0.3)


# P1: the giant on the left, its elbow turning off to the left into the sky
P1 = (-16.0, 17.0, 2.2)
pipe((P1[0], 0, P1[1]), (P1[0], 21.0, P1[1]), P1[2], seed=1, ring=5.2, cls='wall')
elbow((P1[0] - 4.2, 21.0, P1[1]), (1, 0, 0), (0, 1, 0), 4.2, P1[2], seed=1)
pipe((P1[0] - 4.2, 25.2, P1[1]), (-60, 25.2, P1[1]), P1[2], seed=2, ring=5.2)
# a lower branch from the left edge into P1
pipe((-50, 12.8, 17.6), (P1[0] - 2.2, 12.8, 17.6), 1.5, seed=3, ring=4.4)
rs.box(P1[0] - 2.9, P1[0] - 2.1, 10.8, 14.8, 15.6, 19.6, lambda x, y, s, t, z, wp: fogged(tone(RUSTP, 2.4, x, y), z),
       lambda x, y, s, t, z, wp: fogged(tone(RUSTP, 1.6, x, y), z))                     # its flange on the big one
# the thin pipe at the far left edge
pipe((-27.5, 0, 14.0), (-27.5, 40, 14.0), 1.0, seed=4, ring=3.0)
# P4: the giant column on the right, full height
P4 = (29.0, 18.0, 2.0)
pipe((P4[0], 0, P4[1]), (P4[0], 40.0, P4[1]), P4[2], seed=5, ring=5.6, cls='wall')
# P5: the great pipe crossing high from it, and its down-leg coming down onto the bus's roof
P5Y, P5Z, P5R = 17.0, 22.4, 1.9
pipe((P4[0] - 1.0, P5Y, P5Z), (CRUSH + 3.4, P5Y, P5Z), P5R, seed=6, ring=6.0)
rs.box(P4[0] - 2.6, P4[0] + 0.6, P5Y - 2.6, P5Y + 2.6, P5Z - 2.6, P5Z + 2.6, lambda x, y, s, t, z, wp: fogged(tone(RUSTP, 3.0 - t * 1.4, x, y), z),
       lambda x, y, s, t, z, wp: fogged(tone(RUSTP, 1.8, x, y), z))                      # a junction box where it meets the column
elbow((CRUSH + 3.4, P5Y - 3.4, P5Z), (0, 1, 0), (-1, 0, 0), 3.4, P5R, seed=6)
pipe((CRUSH, P5Y - 3.4, P5Z), (CRUSH, ROOF - 1.4, P5Z), P5R, seed=7, ring=6.0, moss=False)
# behind: more pipes arching through the yard, smaller in the haze
pipe((-40, 11.0, 44.0), (8.0, 11.0, 44.0), 1.5, seed=8, ring=5.0)
elbow((8.0, 7.0, 44.0), (0, 1, 0), (1, 0, 0), 4.0, 1.5, seed=8)
pipe((12.0, 7.0, 44.0), (12.0, 0, 44.0), 1.5, seed=9, ring=5.0)
pipe((-6.0, 0, 50.0), (-6.0, 14.0, 50.0), 1.4, seed=10, ring=4.0)
elbow((-1.0, 14.0, 50.0), (-1, 0, 0), (0, 1, 0), 5.0, 1.4, seed=10)
pipe((-1.0, 19.0, 50.0), (40.0, 19.0, 50.0), 1.4, seed=11, ring=4.0)
pipe((34.0, 0, 38.0), (34.0, 9.0, 38.0), 1.6, seed=12, ring=4.0)
elbow((30.0, 9.0, 38.0), (1, 0, 0), (0, 1, 0), 4.0, 1.6, seed=12)
pipe((30.0, 13.0, 38.0), (16.0, 13.0, 38.0), 1.6, seed=13, ring=4.0)
pipe((-34.0, 0, 34.0), (-34.0, 22.0, 34.0), 1.8, seed=14, ring=4.6)
pipe((-34.0, 15.0, 34.0), (-16.0, 15.0, 34.0), 1.3, seed=15, ring=4.0)
# creepers and old cables hanging off the high pipe; cables strung between the giants
for k, xx in enumerate((22.0, 15.0, 9.5, 3.0, -4.0)): drape((xx, P5Y - P5R + 0.1, P5Z - 0.6), 3.5 + (k % 3) * 1.6, 30 + k)
for k, xx in enumerate((-22.0, -30.0)): drape((xx, 25.2 - P1[2] + 0.1, P1[1] - 0.6), 4.0 + k * 2, 40 + k)
rs.line3((P1[0] + 2.4, 18.0, P1[1]), (P4[0] - 2.4, 21.0, P4[1]), lambda x, y, s, t, z, wp: fogged((24, 22, 20), z), w=0.08, sag=3.4)
rs.line3((P1[0] + 2.4, 15.0, P1[1]), (CRUSH, 14.0, P5Z), lambda x, y, s, t, z, wp: fogged((24, 22, 20), z), w=0.07, sag=1.6)


# ---------------------------------------------------------------------------------------------------- the Scraper's rear wall (left)
SCX, SCZ0, SCZ1 = -25.0, 8.0, 22.0
SDOOR = (17.0, 20.4, 8.2)            # the back door in it: z0, z1, height
def scraper_wall(x, y, s, t, z, wp):
    X, Y, Z = wp
    if SDOOR[0] < Z < SDOOR[1] and Y < SDOOR[2]:
        u = (Z - SDOOR[0]) / (SDOOR[1] - SDOOR[0])
        if Y > SDOOR[2] - 0.35 or u < 0.06 or u > 0.94: return fogged(tone(DECO, 1.6, x, y), z)
        pv = 2.0 + (0.8 if (Y % 2.6) < 0.2 or abs(u - 0.5) < 0.03 else 0) - (0.6 if 0.12 < u < 0.88 and 0.6 < (Y % 2.6) < 2.2 else 0)
        c = tone(DOORW, pv + (wn(0, Z * 4, Y * 2) - 0.5) * 0.8, x, y)
        if abs(u - 0.82) < 0.04 and abs(Y - 4.0) < 0.12: c = GLOW[2]                                       # the brass handle
        return c
    if SDOOR[0] - 0.6 < Z < SDOOR[1] + 0.6 and Y < SDOOR[2] + 0.8: return tone(DECO, 4.4 if Y > SDOOR[2] + 0.4 else 3.0, x, y)   # the stone surround
    # stone courses, art-deco fluting near the corner, grime
    row = math.floor(Y / 1.6); off = (row % 2) * 1.7 + (h32(row, 3) % 5) * 0.3
    col = math.floor((Z + off) / 3.4)
    v = 2.4 + (h32(row, col, 9) % 5) * 0.2 + (wn(0, Z * 0.5, Y * 0.5) - 0.5) * 1.0 + (wn(2, Z * 2.5, Y * 2.5) - 0.5) * 0.5
    if (Y % 1.6) < 0.09 or ((Z + off) % 3.4) < 0.07: v -= 1.0
    if Z > SCZ1 - 2.2 and (Z * 2.5) % 1 < 0.28 and Y > 1.5: v += 0.7                                  # the fluted pilaster at its corner
    if Y < 1.2: v -= 0.9
    return fogged(tone(DECO, v, x, y), z)
rs.quad((SCX, 0, SCZ0), (SCX, 0, SCZ1), (SCX, 60, SCZ0), scraper_wall, cls='wall')
rs.quad((SCX, 0, SCZ1), (SCX - 6, 0, SCZ1), (SCX, 60, SCZ1), lambda x, y, s, t, z, wp: fogged(tone(DECO, 2.0 + (wn(1, wp[0], wp[1] * 0.5) - 0.5), x, y), z), cls='wall')
# the lamp over the back door (dead) and two worn steps
rs.box(SCX, SCX + 0.6, SDOOR[2] + 1.2, SDOOR[2] + 1.9, 18.2, 19.2, lambda x, y, s, t, z, wp: tone(METAL, 1.6, x, y), lambda x, y, s, t, z, wp: tone(METAL, 2.6, x, y))
for i, (hh, dd) in enumerate(((0.45, 1.6), (0.9, 0.8))):
    rs.box(SCX, SCX + dd, 0, hh, SDOOR[0] - 0.6, SDOOR[1] + 0.6, concrete(3.6 - i * 0.4, DECO), concrete(3.0, DECO), top=concrete(4.4, DECO), cls='prop')


# ---------------------------------------------------------------------------------------------------- the bus, sunk to its upper deck
def bus_side(x, y, s, t, z, wp):
    """its near flank above the ground: the upper deck's windows, the old cream-and-maroon livery gone grey and rusty,
    the creepers and moss climbing it"""
    X, Y, Z = wp
    if DOORX[0] < X < DOORX[1] and Y < -0.2: return None                                               # the front door, down in the ramp
    if Y < 0 and not (PIT[0] < X < PIT[1]): return None
    # the ends are rounded: cut the corners off the flank's silhouette
    for (xe, sgn) in ((BUS_X0, 1), (BUS_X1, -1)):
        d = (X - xe) * sgn
        if d < 1.6 and Y > 7.4 - 1.6 + math.sqrt(max(0.0, 1.6 * 1.6 - (1.6 - d) ** 2)): return None
    if BUS_X0 + 1.4 < X < BUS_X1 - 2.0 and 2.0 < Y < 5.6:
        bay = (X - BUS_X0 - 1.4) / 4.2; fu = bay % 1
        if 0.07 < fu < 0.93 and 2.2 < Y < 5.4:                                                       # the windows
            k = h32(int(bay), 7)
            wv = (Y - 2.2) / 3.2
            if k % 5 == 0 and wv > 0.3 + 0.2 * math.sin(fu * 9):                                       # broken out: dark inside
                return fogged(tone(PAINTB, 0.3, x, y), z)
            c = tone(SKY, 2.0 + wv * 1.6 + (0.8 if (fu + wv * 0.5) % 0.6 < 0.05 else 0), x, y)          # the sky in the dirty glass
            return fogged(mix(c, (30, 32, 27), 0.55 + 0.3 * max(0.0, 0.4 - wv)), z)
        return fogged(tone(STEELBUS, 1.4 + (0.8 if Y > 5.3 else 0), x, y), z)                          # the pillars, the rubber
    maroon = Y < 1.9 or 5.9 < Y < 6.5
    r_ = MAROON if maroon else PAINTB
    v = (2.6 if maroon else 3.6) + (wn(0, X * 0.8, Y * 0.8) - 0.5) * 0.9 + (wn(2, X * 3, Y * 3) - 0.5) * 0.4
    if Y > 6.6: v += 0.5                                                                              # the coving catches the sky
    if abs(Y - 1.95) < 0.08 or abs(Y - 5.85) < 0.06: v -= 1.2                                          # beading
    c = tone(r_, v, x, y)
    ru = wn(2, X * 1.5, Y * 0.35) + (0.08 if maroon else 0)
    if ru > 0.56: c = mix(c, tone(RUSTP, 3.0 + (ru - 0.56) * 4, x, y), min(0.75, (ru - 0.56) * 3.5))
    if Y < 1.0 + 0.9 * wn(1, X * 0.6, 3): c = tone(MOSSY, 2.0 + (wn(3, X * 4, Y * 4) - 0.5) * 1.6, x, y)  # moss creeping up from the ground
    return fogged(c, z)
MAROON = ramp('#1a0d0c #261412 #331b18 #42231f #522c26 #62362e')
STEELBUS = ramp('#121412 #1b1e1b #252925 #2f3430')
rs.quad((BUS_X0, -SUNK, BUS_Z0), (BUS_X1, -SUNK, BUS_Z0), (BUS_X0, 7.4, BUS_Z0), bus_side, cls='wall', cut=True)


def roof_h(Z):
    u = (Z - BUS_Z0) / (BUS_Z1 - BUS_Z0)
    return 7.4 + (ROOF - 7.4) * math.sin(math.pi * u) ** 0.6


def bus_roof(x, y, s, t, z, wp):
    X, Y, Z = wp
    dc = abs(X - CRUSH)
    if dc < 4.5 and Z < BUS_Z0 + 6:                                                                   # crushed under the pipe
        v = 1.8 + (wn(1, X * 3, Z * 3) - 0.5) * 2.0
        return fogged(tone(RUSTP, v, x, y), z)
    v = 4.4 + (wn(0, X * 0.9, Z * 0.9) - 0.5) * 0.9 - (0.6 if (X % 2.6) < 0.15 else 0)
    c = tone(PAINTB, v, x, y)
    ru = wn(3, X * 1.2, Z * 1.2)
    if ru > 0.55: c = mix(c, tone(RUSTP, 2.8 + (ru - 0.55) * 4, x, y), min(0.8, (ru - 0.55) * 3))
    if wn(1, X * 0.7, Z * 0.7) > 0.6: c = mix(c, tone(MOSSY, 3.2, x, y), 0.6)                            # moss mats on the roof
    return fogged(c, z)
ZS = [BUS_Z0, 22.2, 24.0, 26.0, 28.0, 30.0, BUS_Z1]
ROOFO = rs.obj()
for z0, z1 in zip(ZS, ZS[1:]):
    def clipcr(a, b, z0=z0, z1=z1):
        return True
    rs.quad((BUS_X0 + 0.6, roof_h(z0), z0), (BUS_X1 - 0.8, roof_h(z0), z0), (BUS_X0 + 0.6, roof_h(z1), z1), bus_roof, obj=ROOFO, cls='prop')
# the rounded ends: the rear (left) and the front (right) seen at an angle
def bus_end(sign):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        if 1.8 < Y < 5.6 and BUS_Z0 + 1.2 < Z < BUS_Z1 - 1.5 and (sign > 0 or Z < BUS_Z0 + 5):
            return fogged(mix(tone(SKY, 3.4 + (Y - 1.8) * 0.5, x, y), (34, 36, 30), 0.5), z)
        return fogged(tone(PAINTB, 2.6 + (wn(0, Z, Y) - 0.5) * 0.8 - (0.8 if Y < 1.2 else 0), x, y), z)
    return sh
rs.quad((BUS_X0, -0.5, BUS_Z0), (BUS_X0 + 0.2, -0.5, BUS_Z1), (BUS_X0, 7.4, BUS_Z0), bus_end(-1), cls='wall')
rs.quad((BUS_X1, -0.5, BUS_Z0), (BUS_X1 - 0.3, -0.5, BUS_Z1), (BUS_X1, 7.4, BUS_Z0), bus_end(1), cls='wall')
# a few pale shelf fungi on its flank and creepers trellised over it
for k, (fx, fy) in enumerate(((-15.2, 6.4), (-14.6, 6.0), (-6.4, 0.9), (1.2, 6.5), (8.6, 0.7), (9.1, 1.1))):
    rs.disc(fx, fy, BUS_Z0 - 0.2, 0.32 + (k % 2) * 0.1,
            lambda x, y, s, t, z, wp: fogged(tone(CAP, 3.6 - t * 2.0 - s * 0.4, x, y), z) if t < 0.25 else None)
for k in range(9):
    x0 = BUS_X0 + 2 + k * 4.3 + (h32(k, 50) % 10) * 0.1
    rs.line3((x0, ROOF - 0.6, BUS_Z0 + 0.4), (x0 + 0.5, 0.3 + (h32(k, 51) % 4) * 0.8, BUS_Z0 - 0.15),
             lambda x, y, s, t, z, wp: fogged(tone(MOSSY, 2.0 + (1.2 if (x + y) % 3 == 0 else 0), x, y), z), w=0.14, sag=-0.4)

# the pit dug down to the front door along the bus's flank: a ramp of trodden earth from the yard on the right down
# to a level floor before the door, planks laid on it as steps, a rope on stakes along its edge
def pit_earth(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 3.6 + (wn(1, X * 2.5, Z * 2.5) - 0.5) * 1.4 + (0.9 if h32(int(Z * 3), int(X * 3), 4) % 9 == 0 else 0) - 0.12 * (-Y)
    c = tone(EARTHY, v, x, y)
    if wn(0, X * 0.8, Z * 0.8) > 0.62: c = mix(c, tone(MOSSY, 2.6, x, y), 0.5)
    return fogged(c, z)
rs.quad((PIT[0], FLOOR - 0.2, BUS_Z0 + 0.4), (PIT[1] + 1, FLOOR - 0.2, BUS_Z0 + 0.4), (PIT[0], 0.05, BUS_Z0 + 0.4),
        lambda x, y, s, t, z, wp: fogged(tone(EARTHY, 2.0 + (wn(0, wp[0] * 2, wp[1] * 2) - 0.5) * 1.6 + (wn(2, wp[0] * 6, wp[1] * 6) - 0.5) * 0.8, x, y), z), cls='wall')
rs.quad((RAMPX, FLOOR, PIT[2]), (PIT[1], 0.0, PIT[2]), (RAMPX, FLOOR, PIT[3]), pit_earth, cls='ground')
rs.quad((PIT[0], FLOOR, PIT[2]), (RAMPX, FLOOR, PIT[2]), (PIT[0], FLOOR, PIT[3]), pit_earth, cls='ground')
for k in range(6):                                                                                     # planks laid as steps
    xx = RAMPX + 0.8 + k * (PIT[1] - RAMPX - 1.6) / 6; yy = FLOOR + (xx - RAMPX) / (PIT[1] - RAMPX) * (-FLOOR)
    rs.box(xx - 0.35, xx + 0.35, yy, yy + 0.2, PIT[2] + 0.6, PIT[3] - 0.4, lambda x, y, s, t, z, wp: fogged(tone(WOOD, 2.6, x, y), z),
           lambda x, y, s, t, z, wp: fogged(tone(WOOD, 2.0, x, y), z), top=lambda x, y, s, t, z, wp: fogged(tone(WOOD, 4.2 + (wn(0, wp[2] * 2, wp[0]) - 0.5), x, y), z))
prev = None
for k in range(5):                                                                                     # the rope on its stakes
    xx = RAMPX + k * (PIT[1] - RAMPX) / 4; yy = FLOOR + (xx - RAMPX) / (PIT[1] - RAMPX) * (-FLOOR)
    rs.line3((xx, yy, PIT[2] + 0.3), (xx, yy + 3.0, PIT[2] + 0.3), lambda x, y, s, t, z, wp: fogged(tone(WOOD, 3.0, x, y), z), w=0.2)
    if prev: rs.line3((prev[0], prev[1] + 2.7, PIT[2] + 0.3), (xx, yy + 2.7, PIT[2] + 0.3), lambda x, y, s, t, z, wp: fogged(tone(WARM, 2.4, x, y), z), w=0.08, sag=0.4)
    prev = (xx, yy)
def busdoor(x, y, s, t, z, wp):
    """the open front door: the folded leaves at its sides, the dark inside with a faint green glow far in"""
    if s < 0.12 or s > 0.88: return tone(STEELBUS, 2.4 + (0.8 if 0.3 < t < 0.8 and (s < 0.06 or s > 0.94) else 0), x, y)
    if t > 0.93: return tone(STEELBUS, 3.0, x, y)
    g = max(0.0, 0.5 - abs(t - 0.35)) * 0.3
    return mix(tone(DOORW, 0.6, x, y), MYC[1], g)
rs.quad((DOORX[0], FLOOR, BUS_Z0 + 0.15), (DOORX[1], FLOOR, BUS_Z0 + 0.15), (DOORX[0], -0.2, BUS_Z0 + 0.15), busdoor, cls='prop')


# ---------------------------------------------------------------------------------------------------- the far yard: its wall, junk
BRICK = ramp('#1a110d #24170f #2f1e14 #3a2619 #462e1f #523726')
def brickwall(x, y, s, t, z, wp):
    X, Y, Z = wp
    row = math.floor(Y / 0.5); off = (row % 2) * 0.6
    v = 2.6 + (h32(math.floor((X + off) / 1.2), row, 4) % 4) * 0.3 + (wn(0, X * 0.4, Y * 0.4) - 0.5) * 0.8
    if (Y % 0.5) < 0.08 or ((X + off) % 1.2) < 0.08: v -= 0.8
    if Y > 5.4: v = 3.4                                                                              # its coping
    c = tone(BRICK, v, x, y)
    if wn(2, X * 0.3, Y * 0.3) > 0.6: c = mix(c, tone(MOSSY, 2.6, x, y), 0.5)
    return fogged(c, z)
rs.quad((-90, 0, 58), (90, 0, 58), (-90, 6.0, 58), brickwall, cls='wall')
rs.quad((-90, 6.0, 58), (90, 6.0, 58), (-90, 6.0, 59), lambda x, y, s, t, z, wp: fogged(tone(STONE, 3.8, x, y), z), cls='wall')
def barrel(X, Z, seed, tipped=False):
    sh = lambda x, y, s, t, z, wp: fogged(tone(RUSTP if seed % 2 else METAL, 2.2 + (1.2 if abs(s - 0.5) < 0.3 else 0) - (0.9 if (t * 3) % 1 < 0.08 else 0)
                                                + (wn(0, wp[0] * 3, wp[1] * 3) - 0.5), x, y), z)
    if tipped: pipe((X - 1.5, 0.95, Z), (X + 1.5, 0.95, Z), 0.95, seed=70 + seed, n=14, ring=1.0, moss=False)
    else:
        pipe((X, 0, Z), (X, 3.0, Z), 0.95, seed=70 + seed, n=14, ring=1.0, moss=False)
        rs.disc(X, 3.0, Z, 0.95, lambda x, y, s, t, z, wp: fogged(tone(RUSTP, 1.2 + (1.0 if s * s + t * t > 0.7 else 0), x, y), z))
for k, (bx, bz, tp) in enumerate(((22.5, 25.0, False), (24.8, 26.4, False), (23.8, 23.4, True), (-28.0, 40.0, False), (-25.5, 41.5, True))):
    barrel(bx, bz, k, tp)
for k in range(4):                                                                                   # a stack of tyres
    rs.box(27.0, 29.6, k * 0.75, k * 0.75 + 0.7, 30.0, 32.0, lambda x, y, s, t, z, wp: fogged(tone(STONE, 1.0 + (0.6 if 0.3 < s < 0.7 else 0), x, y), z),
           lambda x, y, s, t, z, wp: fogged(tone(STONE, 0.8, x, y), z), top=lambda x, y, s, t, z, wp: fogged(tone(STONE, 0.6 + (1.4 if 0.25 < s < 0.75 and 0.25 < t < 0.75 else 0), x, y), z))
# the old depot shed on the right: corrugated walls gone to rust, its big door hanging, a yard lamp on a post
SHED = (31.0, 47.0, 40.0, 50.0, 9.0)                 # x0, x1, z0, z1, eaves
rs.box(SHED[0], SHED[1], 0, SHED[4], SHED[2], SHED[3], corrugated(2.2, RUSTP, 0.5), corrugated(1.8, RUSTP, 0.5, along_z=True), cls="wall")
rs.quad((SHED[0] - 0.5, SHED[4], SHED[2] - 0.6), (SHED[1] + 0.5, SHED[4], SHED[2] - 0.6), (SHED[0] - 0.5, SHED[4] + 3.4, SHED[2] + 4.0),
        corrugated(2.0, METAL, 0.9), cls="prop")
rs.quad((SHED[0] + 3.0, 0.0, SHED[2] - 0.05), (SHED[0] + 9.0, 0.0, SHED[2] - 0.05), (SHED[0] + 3.0, 7.2, SHED[2] - 0.05),
        lambda x, y, s, t, z, wp: fogged(tone(STONE, 0.6 + (0.6 if s < 0.05 or s > 0.95 or t > 0.96 else 0), x, y), z), cls='prop')     # the dark doorway
rs.quad((SHED[0] + 9.0, 0.3, SHED[2] - 0.1), (SHED[0] + 12.4, 0.0, SHED[2] - 1.6), (SHED[0] + 9.0, 7.0, SHED[2] - 0.1), corrugated(3.0, METAL, 0.9))   # its door, ajar
rs.line3((26.0, 0, 34.0), (26.0, 13.0, 34.0), lambda x, y, s, t, z, wp: fogged(tone(METAL, 1.8, x, y), z), w=0.35)
rs.line3((26.0, 13.0, 34.0), (24.4, 13.6, 34.0), lambda x, y, s, t, z, wp: fogged(tone(METAL, 1.8, x, y), z), w=0.3)
rs.disc(24.2, 13.2, 34.0, 0.5, lambda x, y, s, t, z, wp: fogged(tone(METAL, 1.4 + (1.6 if t > 0.3 else 0), x, y), z))
# a bus-stop shelter's skeleton by the far wall: posts and a few corrugated sheets left on its roof
for xx in (-12.0, -4.0):
    rs.line3((xx, 0, 50.0), (xx, 7.2, 50.0), lambda x, y, s, t, z, wp: fogged(tone(METAL, 2.2, x, y), z), w=0.3)
rs.quad((-12.6, 7.2, 49.0), (-6.0, 7.4, 49.0), (-12.6, 7.2, 51.6), corrugated(3.0, METAL, 0.8), cls='prop')

# ---------------------------------------------------------------------------------------------------- the yard's ground
def puddle(X, Z):
    if Z > 30 or Z < 9: return 0.0
    m = wn(2, X * 0.2 + 7.0, Z * 0.3) + (wn(3, X * 1.4, Z * 1.4) - 0.5) * 0.1
    return max(0.0, min(1.0, (m - 0.72) * 12))


def yard(x, y, s, t, z, wp):
    X, _, Z = wp
    if PIT[0] < X < PIT[1] and PIT[2] < Z < BUS_Z0 + 0.2: return None                                    # the pit down to the bus
    # cracked concrete slabs of the old bus bays, setts where they're gone, moss in the joints and in carpets
    sx_, sz_ = math.floor(X / 4.0), math.floor(Z / 4.0)
    fx, fz = X / 4.0 - sx_, Z / 4.0 - sz_
    ex, ez = 1.0 * Z / F / 4.0, 1.0 * Z * Z / (F * CAMH) / 4.0
    hs = h32(sx_, sz_, 3)
    gone = wn(1, X * 0.12, Z * 0.12) > 0.7
    if gone: c = setts(x, y, s, t, z, wp, v0=3.2, mud=0.15)
    else:
        v = 3.4 + (hs % 5) * 0.22 - (hs % 3 == 0) * 0.5 + (wn(0, X * 0.8, Z * 0.8) - 0.5) * 0.9 + (wn(1, X * 3.0, Z * 3.0) - 0.5) * 0.5
        if fx < ex or fz < ez: v = 2.0
        cr = abs(math.sin(X * 0.9 + Z * 0.4 + 3 * wn(3, X * 0.2, Z * 0.2)))
        if cr < 0.025 * (1 + 30 / max(10, Z)) and wn(0, X * 0.5 + 9, Z * 0.5) > 0.5: v = 2.2              # cracks
        c = tone(STONE, v, x, y)
        # the faded bay lines (yellow), every 8 units across, and a stop line
        for bx in (-24.0, -16.0, -8.0, 0.0, 8.0, 16.0, 24.0):
            if abs(X - bx) < 0.16 and h32(int(Z * 0.8), int(bx), 5) % 5 and Z < 40:
                c = mix(c, BAYL, 0.45 * (0.5 + 0.5 * wn(2, X * 3, Z * 3)))
        if abs(Z - 12.0) < 0.2 and h32(int(X * 0.8), 7) % 4: c = mix(c, BAYL, 0.35)
    m = wn(0, X * 0.3 + 40, Z * 0.3) + 0.14 * math.exp(-((Z - BUS_Z0) / 2.5) ** 2) + 0.16 * math.exp(-((X - P1[0]) ** 2 + (Z - P1[1]) ** 2) / 20) \
        + 0.12 * math.exp(-((X - SCX) / 4.0) ** 2)
    edge = m + (wn(3, X * 4, Z * 4) - 0.5) * 0.12
    if edge > 0.64 or (not gone and (fx < ex * 2.2 or fz < ez * 2.2) and m > 0.46):                    # the mnemonic moss
        mv = 1.4 + (m - 0.55) * 5 + (wn(3, X * 5, Z * 5) - 0.5) * 1.6 + (wn(1, X * 14, Z * 14) - 0.5) * 0.8
        c = tone(MNEM if wn(1, X * 0.6 + 3, Z * 0.6) > 0.55 else MOSSY, mv, x, y)
        if h32(int(X * 7 + 999), int(Z * 7 + 999), 9) % 211 == 0: c = MNEM[4]                           # its faint glints
    p_ = puddle(X, Z)
    if p_: c = mix(c, (18, 24, 22), p_ * 0.35)
    return fogged(c, Z)
rs.quad((-120, 0, 3), (120, 0, 3), (-120, 0, 300), yard, cls='ground', cut=True)

# rubble heaps in the near corners (broken slabs, bricks, a bent rail), weeds
def rubble(cx, cz, rad, seed, n=26):
    for k in range(n):
        a = h32(seed, k) % 360 * math.pi / 180; d = (h32(seed, k, 2) % 100) / 100 * rad
        X, Z = cx + math.cos(a) * d, cz + math.sin(a) * d * 0.6
        hgt = (1 - d / rad) * rad * 0.5 + 0.2
        w_ = 0.5 + (h32(seed, k, 3) % 5) * 0.2
        kind = h32(seed, k, 4) % 3
        r_ = [STONE, STONE, BRICK][kind]
        rs.box(X - w_, X + w_, 0, hgt, Z - w_ * 0.6, Z + w_ * 0.6,
               lambda x, y, s, t, z, wp, r_=r_, k=k: fogged(tone(r_, 2.6 + (k % 3) * 0.4 + (wn(0, wp[0] * 2, wp[1] * 2) - 0.5), x, y), z),
               lambda x, y, s, t, z, wp, r_=r_: fogged(tone(r_, 1.8, x, y), z),
               top=lambda x, y, s, t, z, wp, r_=r_: fogged(tone(r_, 3.8 + (wn(1, wp[0] * 2, wp[2] * 2) - 0.5), x, y), z))
rubble(-21.0, 12.4, 3.0, 1)
rubble(19.5, 12.2, 2.8, 2)
for k in range(30):                                                                                     # dry weeds in the cracks
    X = -40 + (h32(k, 60) % 800) / 10.0; Z = 9 + (h32(k, 61) % 260) / 10.0
    if abs(X - P1[0]) < 3 or (BUS_X0 < X < BUS_X1 and Z > BUS_Z0 - 1): continue
    for j in range(3):
        rs.line3((X + j * 0.1, 0, Z), (X + j * 0.25 - 0.2, 0.6 + (h32(k, j) % 4) * 0.25, Z),
                 lambda x, y, s, t, z, wp: fogged(tone(MOSSY, 2.4 + t * 1.6, x, y), z), w=0.06)

img = rs.render(INK, fog=fog, mirror=lambda x, y, wp: 0.6 * puddle(wp[0], wp[2]), light_gain=0.9, grime_gain=0.9, bloom=0.3,
                peel=None)
img.save(f'{OUT}/backyard.png')

def P(X, Y, Z): return tuple(int(round(v)) for v in proj(X, Y, Z))
print('scraper door', P(SCX, 0, SDOOR[0]), P(SCX, SDOOR[2], SDOOR[1]))
print('pit', P(PIT[0], 0, PIT[2]), P(PIT[1], 0, PIT[2]), P(PIT[0], 0, PIT[3]), P(PIT[1], 0, PIT[3]), 'door', P(DOORX[0], 0, BUS_Z0), P(DOORX[1], -SUNK + 0.4, BUS_Z0))
print('bus', P(BUS_X0, ROOF, BUS_Z0), P(BUS_X1, 0, BUS_Z0))
g = img.copy(); gp = g.load()
for y in range(600):
    for x in range(1067):
        if x % 50 == 0 or y % 50 == 0: gp[x, y] = (255, 0, 255) if (x % 100 == 0 or y % 100 == 0) else (120, 0, 120)
g.save(f'{OUT}/backyard_guides.png')
print('done backyard')
