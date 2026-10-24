"""Applications -- the paperwork office of the Bureau of Shapes in Shed 521 (ShedApplicationsScene), 1067x600, the
shared camera (raster3d.py). A low, tired open-plan office: a drop ceiling with water-stained tiles (a few missing,
cables hanging out) and fluorescent panels, rows of cubicles with green-screen terminals and pinned forms, filing
cabinets along the right wall, high windows letting in the overcast day on the left, a pneumatic-tube post running
along the ceiling down into the desks, a wall clock, worn linoleum strewn with forms.
Front left: the clerk's desk (towering stacks of forms in triplicate, stamps, an in-tray, a lamp); the clerk sprite
stands in front of it at canvas (250, 522). The doors to the Floors: the left wall near the front, the right wall near
the front (the scene's exits at canvas x ~67 and ~867).

    python3 applications_bg.py <outdir>   ->  applications.png
"""
import sys, math
from common import h32, draw_text, text_width
from shedkit import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = Raster()
WX, CH, ZB = 24.0, 15.0, 38.0
def fog(z): return max(0.0, min(0.25, (z - 20) / 110.0))
FOGI = (40, 50, 44)
def fg(c, z): return mix(c, FOGI, fog(z))
def day(X, Y, Z):
    """the overcast light from the high windows on the left and the panels overhead"""
    return 0.45 * math.exp(-(X + WX) / 14.0) * (0.6 + 0.4 * math.exp(-((Z - 32) / 12) ** 2)) + 0.25 * (Y / CH)
LINO = ramp('#151b17 #1c241f #242e28 #2d3832 #37433c #424f47 #4f5c53')
LINO2 = ramp('#1a1a14 #23231b #2d2d23 #38382c #444435 #514f3f')
WALLU = ramp('#2a2c22 #36392c #444736 #535641 #63664d #74775b #868869')
WALLL = ramp('#13201b #1a2a24 #22352e #2b4239 #354f45 #405d52')
TILE = ramp('#2c2e26 #383a30 #45473b #535546 #626453 #727462')
CRT = ramp('#06140c #0a2214 #10341e #18482a #246238 #3a8450 #66b07a')

# ---------------------------------------------------------------------------------------------------- the shell
def floor_sh(x, y, s, t, z, wp):
    X, _, Z = wp
    i, j = math.floor(X / 1.6), math.floor(Z / 1.6)
    r_ = LINO if (i + j) % 2 else LINO2
    v = 3.0 + 1.6 * day(X, 0, Z) + (wn(0, X * 0.7, Z * 0.7) - 0.5) * 0.7
    if abs(X + 4) < 3.5 and Z < 40: v += 0.5 * (wn(1, X * 2, Z * 0.4) - 0.3)                        # a trodden lane, polished
    if (X / 1.6) % 1 < 0.9 * z / F / 1.6 + 0.02 or (Z / 1.6) % 1 < 0.9 * z * z / (F * CAMH) / 1.6 + 0.02: v -= 0.7
    return fg(tone(r_, v, x, y), z)
rs.quad((-WX, 0, 3), (WX, 0, 3), (-WX, 0, ZB), floor_sh, cls='ground')

MISSING = {(1, 5), (-3, 9)}
def ceil_sh(x, y, s, t, z, wp):
    X, _, Z = wp
    i, j = math.floor(X / 2.4), math.floor(Z / 2.4)
    if (i, j) in MISSING: return (10, 12, 10)                                                      # a missing tile: the dark void
    fu, fv = (X / 2.4) % 1, (Z / 2.4) % 1
    if fu < 1.15 * z / F / 2.4 or fv < 1.15 * z * z / (F * (CH - CAMH)) / 2.4: return fg((52, 54, 46), z)            # the T-bar grid
    v = 2.6 + 0.8 * day(X, CH, Z) + (wn(0, X * 3 + 50, Z * 3) - 0.5) * 0.35
    c = tone(TILE, v, x, y)
    if h32(i, j, 17) % 5 == 0:                                                                       # a water stain in some tiles
        d = math.hypot(fu - 0.5 - (h32(i, j, 18) % 5 - 2) * 0.05, fv - 0.5) * (1 + 0.3 * wn(3, X * 4, Z * 4))
        if d < 0.36: c = mix(c, (88, 70, 40), 0.35 * (1 - d / 0.36) + 0.12)
        if 0.33 < d < 0.37: c = mix(c, (64, 48, 26), 0.55)
    if h32(i, j, 19) % 9 == 0 and (fu - 0.5) ** 2 + (fv - 0.5) ** 2 < 0.004: c = (40, 42, 36)        # a sprinkler head
    return fg(c, z)
rs.quad((-WX, CH, 3), (WX, CH, 3), (-WX, CH, ZB), ceil_sh, cls='ceil')
def panel(x, y, s, t, z, wp):
    if s < 0.06 or s > 0.94 or t < 0.05 or t > 0.95: return METAL[3]
    if (s * 4) % 1 < 0.1: return (180, 196, 176)
    return mix((222, 236, 214), (196, 214, 196), abs(s - 0.5) * 1.6)
def dead(x, y, s, t, z, wp):
    if s < 0.06 or s > 0.94 or t < 0.05 or t > 0.95: return METAL[3]
    return (70, 78, 70) if (s * 4) % 1 > 0.1 else (54, 60, 54)
for k, (px_, pz) in enumerate(((-9.6, 9.6), (4.8, 9.6), (-9.6, 19.2), (4.8, 19.2), (-9.6, 28.8), (4.8, 28.8), (-9.6, 4.8), (4.8, 4.8))):
    rs.quad((px_ + 0.2, CH - 0.05, pz + 0.2), (px_ + 4.6, CH - 0.05, pz + 0.2), (px_ + 0.2, CH - 0.05, pz + 2.2),
            dead if k == 5 else panel, cls='prop' if k == 5 else 'emit')

def wall_sh(side):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        if Y < 0.6: return fg(tone(WOOD, 1.4, x, y), z)                                             # skirting
        if Y < 6.2:                                                                                  # the painted dado
            v = 2.6 + 1.2 * day(X, Y, Z) + (wn(1, Z * 0.8 + X, Y * 0.8) - 0.5) * 0.5
            if abs(Y - 6.0) < 0.2: v += 1.2
            return fg(tone(WALLL, v, x, y), z)
        v = 3.0 + 1.4 * day(X, Y, Z) + (wn(0, Z * 0.6 + X, Y * 0.6) - 0.5) * 0.6
        return fg(tone(WALLU, v, x, y), z)
    return sh
def lwall(x, y, s, t, z, wp):
    X, Y, Z = wp
    if 15.0 < Z < 19.0 and Y < 8.0:                                                                 # a doorway to the Floors
        if Z < 15.3 or Z > 18.7 or Y > 7.7: return tone(WOOD, 1.6, x, y)
        v = 0.6 + (Z - 15.3) / 3.4 * 1.4 + (0.6 if Y < 0.5 else 0)                                   # the dim stairwell beyond
        return tone(WALLL, v, x, y) if Y < 6.5 else tone(WALLU, 0.8, x, y)
    for wz in (22.0, 27.5, 33.0):                                                                    # high windows
        if wz < Z < wz + 4.0 and 8.6 < Y < 13.4:
            if Z < wz + 0.2 or Z > wz + 3.8 or Y < 8.8 or Y > 13.2 or abs(Z - wz - 2.0) < 0.12 or abs(Y - 11.0) < 0.1: return METAL[2]
            return tone(SKY, 5.4 + (Y - 8.6) * 0.3, x, y) if h32(int(wz), 3) % 4 else tone(SKY, 3.2, x, y)
    return wall_sh(-1)(x, y, s, t, z, wp)
def rwall(x, y, s, t, z, wp):
    X, Y, Z = wp
    if 17.4 < Z < 21.6 and Y < 8.0:                                                                 # the door to the Floors
        if Z < 17.7 or Z > 21.3 or Y > 7.7: return tone(WOOD, 1.8, x, y)
        if 4.4 < Y < 7.0 and 18.4 < Z < 20.6: return mix(GLOW[0], (60, 70, 60), 0.5) if (x + y) % 3 else GLOW[0]   # frosted pane
        if abs(Y - 3.6) < 0.25 and Z < 18.4: return METAL[5]
        return tone(WARM, 2.4 + (0.5 if int((Z - 17.7) / 0.6) % 2 else 0), x, y)
    return wall_sh(1)(x, y, s, t, z, wp)
rs.quad((-WX, 0, 3), (-WX, 0, ZB), (-WX, CH, 3), lwall, cls='wall')
rs.quad((WX, 0, 3), (WX, 0, ZB), (WX, CH, 3), rwall, cls='wall')
def back(x, y, s, t, z, wp):
    X, Y, Z = wp
    if -20.0 < X < -15.0 and Y < 8.0:                                                              # a frosted door to the back offices
        if X < -19.7 or X > -15.3 or Y > 7.7: return tone(WOOD, 1.6, x, y)
        if Y > 4.2: return mix((120, 130, 112), (90, 100, 86), (x + y) % 2 * 0.5)
        return tone(WARM, 2.2, x, y)
    return wall_sh(0)(x, y, s, t, z, wp)
rs.quad((-WX, 0, ZB), (WX, 0, ZB), (-WX, CH, ZB), back, cls='wall')
# a dropped bulkhead across the ceiling with an air duct along it, frames the room
def bulk(x, y, s, t, z, wp): return fg(tone(WALLU, 2.6 + (1.0 if t > 0.85 else 0) + (wn(0, wp[0] * 0.6, 3.0) - 0.5) * 0.5, x, y), z)
rs.box(-WX, WX, CH - 1.4, CH, 13.4, 14.6, bulk, bulk, bottom=lambda x, y, s, t, z, wp: fg(tone(WALLU, 1.8, x, y), z), cls='ceil')
def duct(x, y, s, t, z, wp):
    v = 2.6 + (1.0 if t > 0.7 else 0) - (0.8 if (wp[0] / 3.0) % 1 < 0.04 else 0)
    return fg(tone(METAL, v, x, y), z)
rs.box(-WX, WX, CH - 2.4, CH - 1.4, 13.6, 14.4, duct, duct, bottom=lambda x, y, s, t, z, wp: fg(tone(METAL, 1.6, x, y), z), cls='prop')
for gx in (-12.0, 2.0, 16.0):                                                                     # vent grilles on the duct
    rs.quad((gx, CH - 2.3, 13.55), (gx + 2.0, CH - 2.3, 13.55), (gx, CH - 1.5, 13.55),
            lambda x, y, s, t, z, wp: METAL[0] if (t * 6) % 1 < 0.45 else METAL[3], cls='prop')

# the wall clock (stopped at twenty to five), a notice board, the APPLICATIONS sign
def clock(x, y, s, t, z, wp):
    d = math.hypot(s, t)
    if d > 0.86: return METAL[1] if d > 0.95 else METAL[4]
    a = math.atan2(t, s)
    for (ang, ln, w) in ((math.radians(-90 - 0 + 150), 0.45, 0.06), (math.radians(-90 + 240), 0.7, 0.04)):
        px_, py_ = math.cos(ang), math.sin(ang)
        proj_ = s * px_ + t * py_
        if 0 < proj_ < ln and abs(s * py_ - t * px_) < w: return (24, 24, 20)
    if d > 0.72 and int((a + math.pi) / (2 * math.pi) * 12 + 0.5) % 1 == 0 and abs(((a + math.pi) / (2 * math.pi) * 12) % 1 - 0.5) > 0.42: return (40, 40, 34)
    return (214, 210, 186) if d < 0.7 else (196, 192, 170)
rs.disc(6.0, 11.2, ZB - 0.1, 1.2, clock)
def board(x, y, s, t, z, wp):
    if s < 0.04 or s > 0.96 or t < 0.06 or t > 0.94: return tone(WOOD, 1.8, x, y)
    for i in range(10):
        nx, ny = (h32(i, 1) % 80) / 100 + 0.04, (h32(i, 2) % 66) / 100 + 0.08
        if nx < s < nx + 0.16 and ny < t < ny + 0.24:
            c = BONE[4] if i % 3 else BONE[3]
            if int(((t - ny) / 0.24) * 8) % 2 == 0 and 0.15 < (s - nx) / 0.16 < 0.85: c = STONE[4]
            return c
    return tone(WARM, 1.8, x, y)
rs.quad((10.0, 6.8, ZB - 0.1), (17.0, 6.8, ZB - 0.1), (10.0, 10.2, ZB - 0.1), board, cls='prop')
SIGN = (-11.0, -1.0, 11.6, 13.6, ZB - 0.15)
rs.quad((SIGN[0], SIGN[2], SIGN[4]), (SIGN[1], SIGN[2], SIGN[4]), (SIGN[0], SIGN[3], SIGN[4]),
        lambda x, y, s, t, z, wp: tone(WOOD, 1.6, x, y) if s < 0.03 or s > 0.97 or t < 0.1 or t > 0.9 else (58, 40, 26), cls='prop')

# the pneumatic-tube post: brass tubes along the ceiling, dropping into the desks
BRASS = ramp('#2e2010 #4a3418 #6a4c22 #8c6830 #ae8842 #ccaa60')
def tube_sh(x, y, s, t, z, wp): return fg(tone(BRASS, 2.0 + (1.4 if y % 3 == 0 else 0), x, y), z)
for tx in (-13.0, 10.0):
    rs.line3((tx, CH - 0.3, ZB - 0.5), (tx, CH - 0.3, 8.0), tube_sh, w=0.28)
for (tx, dz, dx, dy) in ((-13.0, 21.5, -16.0, 3.6), (10.0, 31.0, 9.0, 5.2), (-13.0, 31.0, -10.5, 5.2)):
    rs.line3((tx, CH - 0.3, dz), (dx, CH - 0.3, dz), tube_sh, w=0.28)
    rs.line3((dx, CH - 0.3, dz), (dx, dy, dz), tube_sh, w=0.28)
    rs.disc(dx, dy - 0.1, dz, 0.34, lambda x, y, s, t, z, wp: fg(tone(BRASS, 3.6 - t * 2, x, y), z))           # the mouth
rs.line3((-13.0, CH - 0.3, 25.0), (-13.0, CH - 0.3, 25.6), lambda x, y, s, t, z, wp: fg(tone(BRASS, 4.4, x, y), z), w=0.5)   # a canister in transit
for k in range(4):                                                                                 # cables out of the missing tiles
    cx_, cz_ = [(3.4, 12.2), (-6.4, 22.0), (3.0, 12.6), (-6.8, 22.6)][k]
    rs.line3((cx_, CH, cz_), (cx_ + 0.3, CH - 1.2 - k % 3 * 0.6, cz_ + 0.2), lambda x, y, s, t, z, wp: (16, 18, 16), w=0.08, sag=-0.3)

# ---------------------------------------------------------------------------------------------------- cubicles
PART = ramp('#202620 #2a322a #343e34 #404a3e #4c5849 #5a6656')
def partition(x, y, s, t, z, wp):
    X, Y, Z = wp
    if t > 0.93: return fg(tone(METAL, 3.4, x, y), z)                                              # the alu top rail
    v = 2.6 + 0.9 * day(X, Y, Z) + (wn(1, (X + Z) * 3, Y * 3) - 0.5) * 0.4
    c = tone(PART, v, x, y)
    k = h32(int((X + Z) * 1.2), int(Y * 1.5), 7)
    if k % 9 == 0 and 0.3 < t < 0.85: c = BONE[4] if k % 2 else BONE[3]                              # pinned notes
    return fg(c, z)
def terminal(X, Y, Z, seed, facing=1):
    """a green-screen terminal on a desk: a beige box, the glowing screen with lines of text"""
    case = lambda x, y, s, t, z, wp: fg(tone(BONE, 2.4 + t, x, y), z)
    rs.box(X - 1.0, X + 1.0, Y, Y + 1.8, Z - 0.4, Z + 1.6, case, case, top=case, cls='prop')
    def scr(x, y, s, t, z, wp):
        if s < 0.12 or s > 0.88 or t < 0.12 or t > 0.88: return tone(BONE, 3.2, x, y)
        row = int((1 - t) * 8)
        if row % 2 == 0 and s < 0.2 + (h32(row, seed) % 6) * 0.11: return CRT[6]
        return CRT[2] if (x + y) % 2 else CRT[3]
    rs.quad((X - 0.85, Y + 0.25, Z - 0.45), (X + 0.85, Y + 0.25, Z - 0.45), (X - 0.85, Y + 1.6, Z - 0.45), scr, cls='emit')
def chair(X, Z):
    seat = lambda x, y, s, t, z, wp: fg(tone(SLATE, 2.2 + t, x, y), z)
    rs.box(X - 0.9, X + 0.9, 1.9, 2.2, Z, Z + 1.6, seat, seat, top=seat, cls='prop')
    rs.quad((X - 0.9, 2.2, Z + 1.6), (X + 0.9, 2.2, Z + 1.6), (X - 0.9, 4.4, Z + 1.7), seat, cls='prop')
    rs.line3((X, 0.3, Z + 0.8), (X, 1.9, Z + 0.8), lambda x, y, s, t, z, wp: METAL[1], w=0.18)
def cubicle(x0, x1, z0, z1, seed, chairs=True):
    h = 4.6
    rs.quad((x0, 0, z0), (x1, 0, z0), (x0, h, z0), partition, cls='prop')
    rs.quad((x0, 0, z0), (x0, 0, z1), (x0, h, z0), partition, cls='prop')
    rs.quad((x1, 0, z0), (x1, 0, z1), (x1, h, z0), partition, cls='prop')
    desk = lambda x, y, s, t, z, wp: fg(tone(WOOD, 3.4, x, y), z)
    rs.box(x0 + 0.2, x1 - 0.2, 2.5, 2.8, z1 - 2.0, z1 - 0.2, desk, desk, top=desk, cls='prop')
    terminal((x0 + x1) / 2 + (h32(seed, 1) % 3 - 1) * 0.8, 2.8, z1 - 1.4, seed)
    for k in range(h32(seed, 2) % 3 + 1):                                                          # paper stacks
        px_ = x0 + 0.8 + k * 1.1
        rs.box(px_, px_ + 0.9, 2.8, 2.8 + 0.3 + (h32(seed, k) % 5) * 0.2, z1 - 1.8, z1 - 1.0,
               lambda x, y, s, t, z, wp: fg(BONE[4] if (y % 2) else BONE[2], z), lambda x, y, s, t, z, wp: fg(BONE[3], z),
               top=lambda x, y, s, t, z, wp: fg(BONE[4], z), cls='prop')
    if chairs and h32(seed, 3) % 3: chair((x0 + x1) / 2 + 0.8, z1 - 3.2)
for (x0, x1, z0, seed) in ((-9.5, -3.0, 31.0, 1), (-3.0, 3.5, 31.0, 2), (3.5, 10.0, 31.0, 3), (10.0, 16.5, 31.0, 9),
                           (-9.5, -3.0, 24.5, 4), (-3.0, 3.5, 24.5, 5), (10.0, 16.5, 24.5, 6)):
    cubicle(x0, x1, z0, z0 + 5.5, seed)
# filing cabinets along the right wall, archive boxes on top
for k in range(6):
    zc = 23.2 + k * 2.2
    def cab(x, y, s, t, z, wp, k=k):
        if (t * 4) % 1 < 0.07: return METAL[0]
        if abs(s - 0.5) < 0.14 and abs((t * 4) % 1 - 0.72) < 0.06: return METAL[5]
        if abs(s - 0.5) < 0.2 and abs((t * 4) % 1 - 0.45) < 0.08: return BONE[4]                    # label holders
        return fg(tone(SLATE if k % 3 else METAL, 2.6 + (wn(1, s * 3 + k, t * 3) - 0.5) * 0.5, x, y), z)
    hh = 5.6 - (k % 2) * 0.8
    rs.box(21.6, WX - 0.05, 0, hh, zc, zc + 2.1, cab, cab, top=lambda x, y, s, t, z, wp: fg(tone(METAL, 3.6, x, y), z), cls='prop')
    if h32(k, 9) % 2:
        rs.box(21.9, 23.6, hh, hh + 1.1, zc + 0.3, zc + 1.8, lambda x, y, s, t, z, wp: fg(tone(OCHRE, 3.0, x, y), z),
               lambda x, y, s, t, z, wp: fg(tone(OCHRE, 2.2, x, y), z), top=lambda x, y, s, t, z, wp: fg(tone(OCHRE, 3.8, x, y), z), cls='prop')
# a water cooler, a coat stand, applicants waiting on a bench under the windows
rs.box(-22.8, -21.4, 0, 3.4, 21.0, 22.4, lambda x, y, s, t, z, wp: fg(tone(BONE, 3.0, x, y), z), lambda x, y, s, t, z, wp: fg(BONE[2], z), cls='prop')
rs.disc(-22.1, 4.3, 21.7, 0.9, lambda x, y, s, t, z, wp: SKY[5] if s - t < 0.2 else SKY[3])
for i, bz in enumerate((25.4, 27.2, 29.0)):
    applicant(rs, -21.2, bz, 700 + i, h=6.3, seated=True, view='right')
bench = lambda x, y, s, t, z, wp: fg(tone(WOOD, 3.2, x, y), z)
rs.box(-23.6, -20.4, 1.6, 2.0, 24.4, 30.4, bench, bench, top=bench, cls='prop')
applicant(rs, 6.5, 23.6, 720, h=6.3, view='front')                                                       # a clerk at a cubicle
applicant(rs, -5.0, 30.2, 721, h=6.3, seated=True, view='back')
for k in range(24):                                                                                 # forms on the floor
    fx, fz = -18 + (h32(k, 21) % 360) / 10.0, 16.0 + (h32(k, 22) % 200) / 10.0
    if -10 < fx < 17 and fz > 23: continue
    a = (h32(k, 23) % 628) / 100.0; c, s_ = math.cos(a) * 0.4, math.sin(a) * 0.4
    rs.quad((fx - c, 0.03, fz - s_), (fx + s_, 0.03, fz - c), (fx - s_, 0.03, fz + c),
            lambda x, y, s, t, z, wp: fg(BONE[4] if (x + y) % 4 else BONE[2], z), cls='prop')

# ---------------------------------------------------------------------------------------------------- the clerk's desk
DX0, DX1, DZ0, DZ1 = -24.0, -15.0, 19.5, 22.0
def desk_front(x, y, s, t, z, wp):
    if t > 0.9: return tone(WOOD, 4.4, x, y)
    if (s * 3) % 1 < 0.03: return WOOD[0]
    if abs((t * 3) % 1 - 0.5) < 0.08 and abs((s * 3) % 1 - 0.5) < 0.1: return BRASS[4]
    return planks(3.0, WARM, w=0.8, seed=51)(x, y, s, t, z, wp)
rs.box(DX0, DX1, 0, 3.0, DZ0, DZ1, desk_front, planks(2.4, WARM, seed=52), top=planks(4.2, WARM, vertical=False), cls='prop')
for k, (px_, hh) in enumerate(((-23.0, 2.6), (-21.9, 4.2), (-20.8, 1.6), (-17.0, 3.2), (-16.0, 2.0))):   # stacks of forms
    lean = (h32(k, 5) % 3 - 1) * 0.15
    rs.box(px_ + lean, px_ + 1.0 + lean, 3.0, 3.0 + hh, DZ0 + 0.6, DZ0 + 1.8,
           lambda x, y, s, t, z, wp: BONE[4] if y % 2 else (BONE[2] if h32(y, 3) % 3 else (200, 120, 110)),
           lambda x, y, s, t, z, wp: BONE[3], top=lambda x, y, s, t, z, wp: BONE[4], cls='prop')
rs.box(-19.6, -18.2, 3.0, 3.6, DZ0 + 0.5, DZ0 + 1.6, lambda x, y, s, t, z, wp: tone(METAL, 3.0, x, y),
       lambda x, y, s, t, z, wp: METAL[2], top=lambda x, y, s, t, z, wp: BONE[4], cls='prop')                   # the in-tray
for k, sx in enumerate((-18.0, -17.6)):                                                                        # rubber stamps
    rs.line3((sx, 3.0, DZ0 + 0.5), (sx, 3.6, DZ0 + 0.5), lambda x, y, s, t, z, wp, k=k: (RED[4], TEAL[4])[k], w=0.3)
    rs.disc(sx, 3.8, DZ0 + 0.5, 0.22, lambda x, y, s, t, z, wp: WOOD[3])
rs.line3((-15.6, 3.0, DZ0 + 1.0), (-15.8, 5.6, DZ0 + 1.3), lambda x, y, s, t, z, wp: METAL[2], w=0.12)            # the desk lamp
rs.disc(-16.2, 5.6, DZ0 + 1.2, 0.5, lambda x, y, s, t, z, wp: GLOW[4] if t > 0.15 else (GLOW[2] if t > -0.2 else METAL[2]), cls='emit')
rs.box(-24.0, -23.6, 0, 3.0, DZ0, DZ1, lambda x, y, s, t, z, wp: (26, 24, 20), lambda x, y, s, t, z, wp: (26, 24, 20), cls='prop')

def letters(col):
    (ax, ay) = proj(SIGN[0], SIGN[3], SIGN[4]); (bx, by) = proj(SIGN[1], SIGN[2], SIGN[4])
    txt = 'APPLICATIONS'; sc = 2; tw = text_width(txt, sc)
    def put(x, y):
        if 0 <= x < W and 0 <= y < H: col[y][x] = (210, 186, 120) if (x * 3 + y) % 7 else (160, 140, 90)
    draw_text(put, txt, int((ax + bx) / 2 - tw / 2), int((ay + by) / 2 - 5), sc)

img = rs.render(INK, fog=fog, overlay=letters, light_gain=1.1, grime_gain=0.6, bloom=0.4, stain_gain=0.3, damp_gain=0.25)
img.save(f'{OUT}/applications.png')
print('done applications')
