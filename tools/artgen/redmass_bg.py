"""Redmass Island (RedmassIslandScene), 1067x600, overcast day, the shared camera (raster3d.py via waterkit.WRaster).
The text (not the old AI picture, which showed a windowless boiler room) decides the place: "a small island in the Echo
Drain Delta containing a ruined building where a sentient redmass lives" -- the ruined pump-house seen from the delta
(brick, glassless arched windows, a smoking chimney, big pipes), here from inside. Its front wall is gone and the roof is
down to bare rafters, so it is open to the overcast sky; the old boiler-room composition is kept inside it: pipes along
the walls, a pump with its flywheel, the dead control desk, the arched window in the back wall (the delta in it), a
doorway on the right. The trunk main crosses the hall at knee height and has burst in the middle: that is where the
redmass grows -- "like coral made of blood-coloured steel", tendrils of oxidised iron and orange-red crystal, faintly lit.
Its veins run out over the floor, up the back wall and along the pipes ("the whole island is one slow red muscle").
The left wall has fallen into the water: the way back to the bridge, the delta and its horn towers in the haze beyond.

    python3 redmass_bg.py <outdir>  ->  redmass.png       (assets/images/backgrounds/RedmassIsland.png: the burst pipe
                                                           empty -- the scar left when the redmass is taken)
                                        redmass_heart.png (assets/images/props/redmass_heart.png: the growth itself, with
                                                           the light it throws round it)
                                        redmass_glow.png  (assets/images/props/redmass_glow.png: only its lit crystal, for
                                                           an additive breathing pulse)
Prints where the sprites go (top-left, canvas) and the scene's fixed points."""
import sys, math
from PIL import Image
from common import h32, ramp, make_noise
from shedkit import *
from waterkit import WRaster, timber, ironround, roundlit, frustum, ALGAE, SILT, REED, LIGHT

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = WRaster()
WL = -0.6
IRON = ramp('#121210 #1b1a17 #25231f #302d28 #3c3832 #4a453d #5a5449')
BRICK = ramp('#1f1411 #2c1b16 #3a241d #4a2e24 #5a392c #6b4535 #7c5240 #8c5f4b')
CONC = ramp('#161816 #1e211e #272a26 #31342f #3c3f39 #484a43 #55574f #63645b')
CRYST = ramp('#3a0e0a #5c1a10 #842a16 #a8401e #c85a28 #e07a3a #f0a058')
FLESH = ramp('#1e0c0a #2e120e #431a13 #5a2418 #72301e #8a3e26')                 # the redmass's oxidised steel
FOGSKY = ramp('#18221f #1e2a27 #25322e #2c3a35 #34433c #3d4c44 #46554c #506055 #5b6a5e #677466 #727d6e')
MURK = ramp('#0f1412 #141b18 #1a231f #212c27 #29352f #323f37 #3c4940 #47544a')
HX0, HX1, HZ1, HTOP = -30.0, 30.0, 38.0, 18.0                                      # the hall: side walls, back wall, wall top
PZ, PY, PR = 21.5, 1.7, 1.25                                                        # the trunk main: depth, axis height, radius
HEART = (0.0, PY, PZ)                                                              # where it burst

# ---------------------------------------------------------------------------------------------------- sky, the delta outside
_c1, _c2 = make_noise(13, 101, W, H), make_noise(47, 102, W, H)
def isl_sky(x, y, s=0, t=0, z=0, wp=None):
    tt = max(0.0, min(1.0, y / HY))
    v = 2.8 + 6.8 * tt ** 1.4 + (_c2(x * 0.5, y * 2.8) - 0.5) * 2.2 + (_c1(x * 0.5, y * 2.4) - 0.5) * 0.7
    c = tone(FOGSKY, v, x, y)
    if tt > 0.7: c = mix(c, (96, 102, 84), ((tt - 0.7) / 0.3) ** 2 * 0.3)
    return c
rs.quad((-1400, 800, 600), (1400, 800, 600), (-1400, -300, 600), isl_sky, cls='sky')
def murk(x, y, s, t, z, wp):
    X, _, Z = wp
    near = min(1.0, 24.0 / Z)
    v = 3.0 + (wn(0, X * 0.08 + Z * 0.02, Z * 0.35) - 0.5) * 2.0 * near + (1 - near) * 1.0
    P = 0.45 + Z * 0.02
    if (Z / P) % 1 < Z * Z / (F * (CAMH - WL)) / P * 1.1 and h32(int(X / (1.2 + Z * 0.05)), int(Z / P), 9) % 5 == 0: v += 1.3
    return fogged(tone(MURK, v, x, y), z)
rs.water(WL, -1400, 1400, 3, 590, murk, strength=lambda X, Z: 0.45 + 0.3 * (1 - min(1.0, 24.0 / Z)), wobble=1.6)
def far_tower(X, Z, hh, horns):
    """a horn tower of the delta far off in the haze (seen through the breach and the window)"""
    for (dx, dz) in ((-1.6, 0), (1.6, 0)):
        rs.beam((X + dx, WL, Z + dz), (X + dx * 0.4, hh, Z + dz), 0.9, lambda x, y, s, t, z, wp: fogged(WOOD[2], z))
    for k in range(5):
        Y = hh * (k + 1) / 6
        rs.beam((X - 1.6 * (1 - Y / hh * 0.6), Y, Z), (X + 1.6 * (1 - Y / hh * 0.6), Y, Z), 0.5, lambda x, y, s, t, z, wp: fogged(WOOD[2], z))
    for (hy, r, d) in horns:
        frustum(rs, (X, hy, Z), (X + d * 6, hy + 3.0, Z - 2), 0.6, r,
                lambda x, y, u, v, z, wp, lit: fogged(tone(WOOD, 1.6 + lit * 2.4, x, y), z), lambda x, y, u, v, z, wp, dep: fogged(WOOD[0], z), n=20)
far_tower(-95.0, 80.0, 30.0, [(31.0, 6.0, 1), (22.0, 4.5, 1)])
far_tower(14.0, 150.0, 26.0, [(27.0, 4.0, -1)])
for (X0, X1, Z, hh) in ((-200, -140, 220, 26), (-60, -20, 200, 18), (30, 70, 230, 30), (80, 120, 180, 14)):
    rs.box(X0, X1, WL, hh, Z, Z + 20, lambda x, y, s, t, z, wp: fogged(tone(STONE, 2.0 + (0.8 if (wp[1] * 0.5) % 1 < 0.15 else 0), x, y), z),
           lambda x, y, s, t, z, wp: fogged(STONE[1], z), cls='wall')

# ---------------------------------------------------------------------------------------------------- veins (the redmass running through the island)
_vn = [make_noise(1, s, 509, 509) for s in (111, 112)]
def vein(a, b, reach, ax, ay):
    """a branching network of thin veins in surface coordinates (a, b), thinning out with the distance from (ax, ay)"""
    d = math.hypot(a - ax, b - ay)
    if d > reach: return 0.0
    r1 = abs(_vn[0](a * 0.9 + 3000, b * 0.9 + 3000) - 0.5)
    r2 = abs(_vn[1](a * 2.1 + 3000, b * 2.1 + 3000) - 0.5)
    k = 1 - d / reach
    w1 = 0.022 * (0.3 + k * 1.4); w2 = 0.012 * k
    return 1.0 if r1 < w1 else (0.6 if r2 < w2 else 0.0)

# ---------------------------------------------------------------------------------------------------- the floor
def floor(x, y, s, t, z, wp):
    """the hall's concrete slab: cast in bays, cracked, silt and rubble drifted in at the front, the veins over it"""
    X, _, Z = wp
    if X < HX0 - 0.1:                                                             # outside: the island's silt
        v = 3.2 + (wn(0, X * 0.4, Z * 0.4) - 0.5) * 1.2
        c = tone(SILT, v, x, y)
        if wn(2, X * 1.2, Z * 1.2) > 0.6: c = mix(c, tone(ALGAE, v, x, y), 0.5)
        return fogged(c, z)
    if Z < FRONT:                                                                 # in front of where the front wall stood: the island
        v = 3.4 + (wn(0, X * 0.35, Z * 0.35) - 0.5) * 1.0 + (wn(1, X * 1.8, Z * 1.8) - 0.5) * 0.5
        rip = math.sin(Z * 4.0 + X * 0.3 + wn(2, X * 0.4, Z * 0.4) * 7)
        if rip > 0.8: v += 0.5
        if wn(0, X * 0.16 + 40, Z * 0.3) > 0.5:                                    # drier crust, cracked into plates
            cx_, cz_ = math.floor(X / 0.9), math.floor(Z / 0.9)
            d1 = d2 = 9.0
            for i_ in (-1, 0, 1):
                for j_ in (-1, 0, 1):
                    hh = h32(cx_ + i_, cz_ + j_, 77)
                    d = math.hypot(X - (cx_ + i_ + (hh % 100) / 100) * 0.9, Z - (cz_ + j_ + (hh // 100 % 100) / 100) * 0.9)
                    if d < d1: d1, d2 = d, d1
                    elif d < d2: d2 = d
            v += -1.4 if d2 - d1 < 0.04 + z / F * 1.2 else 0.4
        c = tone(SILT, v, x, y)
        if FRONT - Z < 1.2 and wn(1, X * 2, 5.0) > 0.4: c = mix(c, tone(CONC, 3.0, x, y), 0.6)   # broken slab edge
        return fogged(c, z)
    bx, bz = math.floor(X / 4.0), math.floor(Z / 4.0); fx, fz = X / 4.0 - bx, Z / 4.0 - bz
    v = 3.8 + (h32(bx, bz, 3) % 3) * 0.3 + (wn(0, X * 0.5, Z * 0.5) - 0.5) * 1.0 + (wn(1, X * 2.4, Z * 2.4) - 0.5) * 0.5
    if fx < 0.9 * z / F / 4.0 + 0.008 or fz < 1.1 * z * z / (F * CAMH) / 4.0 + 0.006: v -= 1.6     # the bay joints
    if h32(bx, bz, 5) % 3 == 0 and abs((fx - 0.2) - (fz - 0.6) * 0.7 + 0.15 * math.sin(fz * 9)) < 0.012 + z / F * 0.3: v -= 1.4   # a crack
    v -= 1.1 * max(0.0, 1 - (HX1 - X) / 4.0) + 0.6 * max(0.0, (Z - 30) / 8.0)       # darker toward the walls and the back
    for (ox, oz, r) in ((-17.0, 29.0, 3.4), (-10.0, 32.6, 2.4), (HX1 - 3.5, 9.0, 2.2)):   # oil and rust soaked in under the machines
        d = math.hypot(X - ox, (Z - oz) * 1.3) / r
        if d < 1 + (wn(1, X * 1.5, Z * 1.5) - 0.5) * 0.5: v -= 1.0 * (1 - d * 0.5)
    c = tone(CONC, v, x, y)
    sl = wn(2, X * 0.25, Z * 0.5) + max(0.0, (18 - Z) / 10.0) * 0.5 - (0.0 if X < -18 else 0.1)   # silt drifted in
    if sl > 0.62: c = mix(c, tone(SILT, v - 0.4, x, y), min(0.85, (sl - 0.62) * 3))
    vv = vein(X, Z, 10.0, HEART[0], HEART[2]) if abs(Z - PZ) > PR or abs(X) > 2.0 else 0.0
    if vv == 1.0: c = mix(c, tone(FLESH, 1.6 + (wn(1, X * 6, Z * 6) - 0.5) + 1.4 * max(0.0, 1 - math.hypot(X, Z - PZ) / 10), x, y), 0.85)
    elif vv: c = mix(c, tone(FLESH, 1.4, x, y), 0.5)
    return fogged(c, z)
FRONT = 17.0
def floor_puddle(X, Z):
    if X < HX0 or Z > FRONT - 0.5: return 0.0
    m = wn(3, X * 0.5 + 11, Z * 1.0) + (wn(2, X * 2.0, Z * 2.0) - 0.5) * 0.12
    return max(0.0, min(1.0, (m - 0.76) * 10))
rs.quad((-60, 0, 3), (HX1, 0, 3), (-60, 0, HZ1), floor, cls='ground')
rs.quad((HX0 - 6, 0, 3), (HX0 - 6, 0, HZ1 + 10), (HX0 - 6, WL - 0.5, 3), lambda x, y, s, t, z, wp: fogged(tone(SILT, 2.2 - t, x, y), z), cls='wall')  # the island's edge

# ---------------------------------------------------------------------------------------------------- walls
def bricks(v0, seed=0, along_z=False, veins=None):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = Z if along_z else X
        row = math.floor(Y / 0.32); off = (row % 2) * 0.35
        col_ = math.floor((u + off) / 0.7)
        fb = ((u + off) / 0.7) % 1; fv = (Y / 0.32) % 1
        v = v0 + (h32(col_, row, seed) % 4) * 0.3 + (wn(0, u * 0.4, Y * 0.4) - 0.5) * 1.0
        px = z / F
        if px < 0.12 and (fb < px / 0.7 * 1.1 or fv < px / 0.32 * 1.1): v -= 1.5
        c = tone(BRICK, v, x, y)
        if h32(col_, row, seed + 1) % 17 == 0: c = tone(BRICK, v - 1.0, x, y)    # a burnt brick
        if wn(2, u * 0.3 + seed, Y * 0.3) > 0.74: c = mix(c, tone(STONE, v + 0.4, x, y), 0.35)   # old whitewash
        if Y < 1.2 + wn(1, u, 3.0) * 0.8: c = mix(c, tone(SILT, v - 0.6, x, y), 0.5)
        if veins:
            vv = vein(u, Y, *veins)
            if vv == 1.0: c = mix(c, tone(FLESH, 1.8 + (wn(1, u * 6, Y * 6) - 0.5), x, y), 0.8)
        return fogged(c, z)
    return sh
WIN = (-5.0, 5.0, 5.0, 12.4)                                                       # the arched window in the back wall
DOOR = (14.0, 18.6, 8.2)
def back_wall(x, y, s, t, z, wp):
    X, Y, Z = wp
    archtop = WIN[3] + 2.2 * math.sqrt(max(0.0, 1 - (X / ((WIN[1] - WIN[0]) / 2)) ** 2)) - 2.2
    if WIN[0] < X < WIN[1] and WIN[2] < Y < archtop + 2.2: return None            # open: the delta beyond
    if WIN[0] - 0.5 < X < WIN[1] + 0.5 and WIN[2] - 0.5 < Y < WIN[2]: return fogged(tone(CONC, 4.6, x, y), z)   # the sill
    if WIN[0] - 0.6 < X < WIN[1] + 0.6 and Y >= WIN[2] and Y < archtop + 2.9 and (X < WIN[0] + 0.0 or X > WIN[1] or Y > archtop + 2.2):
        return fogged(tone(BRICK, 2.6 + (0.6 if int((math.atan2(Y - (WIN[3] - 2.2), X) * 8)) % 2 else 0), x, y), z)   # the brick arch
    if DOOR[0] < X < DOOR[1] and Y < DOOR[2]: return None                          # the doorway
    return bricks(3.0, 3, veins=(8.0, 0.0, 0.0))(x, y, s, t, z, wp)
rs.quad((HX0, 0, HZ1), (HX1, 0, HZ1), (HX0, HTOP, HZ1), back_wall, cls='wall', cut=True)
rs.quad((DOOR[0], 0, HZ1 + 0.6), (DOOR[1], 0, HZ1 + 0.6), (DOOR[0], DOOR[2], HZ1 + 0.6),
        lambda x, y, s, t, z, wp: fogged(tone(STONE, 0.6 + t * 0.8, x, y), z), cls='wall')          # darkness through the doorway
rs.quad((DOOR[0], 0, HZ1), (DOOR[0], 0, HZ1 + 0.6), (DOOR[0], DOOR[2], HZ1), lambda x, y, s, t, z, wp: fogged(tone(BRICK, 1.6, x, y), z), cls='wall')
for k in range(3):                                                                 # the window's last iron mullions
    X = WIN[0] + (k + 1) * (WIN[1] - WIN[0]) / 4
    if k == 1: rs.beam((X, WIN[2], HZ1 + 0.1), (X, WIN[3] + 1.6, HZ1 + 0.1), 0.18, ironround(2.4, IRON, rust=0.6))
    else: rs.beam((X, WIN[2], HZ1 + 0.1), (X + 0.6 * (k - 1), WIN[2] + 3.4, HZ1 + 0.1), 0.16, ironround(2.4, IRON, rust=0.6))
rs.beam((WIN[0], 8.4, HZ1 + 0.1), (WIN[0] + 3.2, 8.2, HZ1 + 0.1), 0.14, ironround(2.2, IRON, rust=0.6))
# the right wall: intact, high windows, the pipes along it
def right_wall(x, y, s, t, z, wp):
    X, Y, Z = wp
    for zc in (14.0, 22.0, 30.0):
        if abs(Z - zc) < 1.8 and 11.0 < Y < 15.4: return None                     # clerestory windows, glassless
    return bricks(2.4, 5, along_z=True)(x, y, s, t, z, wp)
rs.quad((HX1, 0, 3), (HX1, 0, HZ1), (HX1, HTOP, 3), right_wall, cls='wall', cut=True)
# the left wall: fallen into the water at the front, a broken stub at the back
def left_wall(x, y, s, t, z, wp):
    X, Y, Z = wp
    top = HTOP - 0.0
    if Z < 31.0:
        top = 1.0 + max(0.0, (Z - 26.0)) * 1.8 + (wn(1, Z * 0.8, 2.0) - 0.5) * 1.6
    top += (h32(int(Z * 2.0), 7) % 3) * 0.25
    if Y > top: return None
    return bricks(2.2, 9, along_z=True)(x, y, s, t, z, wp)
rs.quad((HX0, 0, 18.0), (HX0, 0, HZ1), (HX0, HTOP, 18.0), left_wall, cls='wall', cut=True)
for i in range(22):                                                                # the rubble of it, spilling out to the water
    X = HX0 + ((h32(i, 1) % 100) / 100 - 0.6) * 7; Z = 19 + (h32(i, 2) % 100) / 100 * 11
    sz = 0.4 + (h32(i, 3) % 5) * 0.2
    rs.box(X - sz, X + sz, 0, sz * 0.8, Z - sz * 0.6, Z + sz * 0.6, bricks(2.6, 20 + i), bricks(2.0, 40 + i, along_z=True), top=bricks(3.6, 60 + i), cls='prop')
# rafters and what is left of the roof
for k, Z in enumerate((17.0, 22.0, 27.0, 32.0, 37.0)):
    if k == 2:                                                                     # one broken, hanging down
        rs.beam((HX0 + 0.5, HTOP - 0.2, Z), (-6.0, HTOP - 0.6, Z), 0.75, timber(2.2, WOOD, seed=k), cap=True)
        rs.beam((-5.4, HTOP - 0.8, Z), (-1.5, 11.0, Z - 0.6), 0.7, timber(2.0, WOOD, seed=k + 9), cap=True)
        continue
    if k == 4: continue                                                            # one gone altogether
    rs.beam((HX0 + 0.3, HTOP - 0.2, Z), (HX1 - 0.3, HTOP - 0.2, Z), 0.8, timber(1.8, WOOD, seed=k))
    rs.beam((-0.2, HTOP - 0.2, Z), (-0.2, HTOP + 4.6, Z), 0.5, timber(1.6, WOOD, seed=k + 20))                # king post
    rs.beam((HX0 + 1.0, HTOP, Z), (0.0, HTOP + 5.0, Z), 0.6, timber(1.6, WOOD, seed=k + 30))
    if k != 1: rs.beam((HX1 - 1.0, HTOP, Z), (0.0, HTOP + 5.0, Z), 0.6, timber(1.4, WOOD, seed=k + 40))
    else: rs.beam((HX1 - 1.0, HTOP, Z), (9.0, HTOP + 3.4, Z), 0.6, timber(1.4, WOOD, seed=k + 40), cap=True)   # snapped
rs.quad((6.0, HTOP + 3.0, 31.0), (6.0, HTOP + 3.0, 38.4), (HX1 + 1.0, HTOP - 0.4, 31.0), corrugated(2.0, IRON, 1.0, along_z=True), cls='wall')   # sheets still on
rs.quad((-30.5, HTOP - 0.4, 35.0), (-30.5, HTOP - 0.4, 38.4), (-14.0, HTOP + 2.8, 35.0), corrugated(1.8, IRON, 1.0, along_z=True), cls='wall')
rs.quad((14.0, HTOP + 1.6, 26.0), (19.0, HTOP + 0.4, 26.5), (14.6, 10.0, 26.6), corrugated(1.6, IRON, 1.0), cls='prop')   # one torn loose, hanging

# ---------------------------------------------------------------------------------------------------- the machinery
IR = lambda v, rust=0.7, seed=0: ironround(v, IRON, rust=rust, seed=seed)
def redpipe(v0, seed=0, reach=8.0, at=None):
    """a pipe with the redmass's veins running along it"""
    base = ironround(v0, IRON, rust=0.75, seed=seed)
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        c = base(x, y, s, t, z, wp)
        u = X + Z
        if abs(_vn[0](u * 1.3 + 3000 + seed, t * 2.0 + 3000) - 0.5) < 0.05 and (at is None or math.hypot(X - at[0], Z - at[2]) < reach):
            c = tone(FLESH, 1.8 + (1 - abs(t)) * 1.0, x, y)
        return c
    return sh
# along the right wall: two big pipes, flanged, one turning down into the floor at the front
for (Y, r, v) in ((3.2, 1.0, 2.8), (6.8, 0.8, 2.4)):
    rs.beam((HX1 - 1.4, Y, 9.0 if Y < 5 else 4.0), (HX1 - 1.4, Y, HZ1), r * 2, IR(v, 0.5, int(Y * 10)))
    for Z in range(12, 38, 4):
        rs.beam((HX1 - 1.4, Y, Z), (HX1 - 1.4, Y, Z + 0.35), r * 2 + 0.4, IR(v + 0.4, 0.5, Z))
rs.beam((HX1 - 1.4, 3.2, 9.0), (HX1 - 3.4, 3.0, 9.0), 2.0, IR(2.8, 0.8), cap=True)
rs.beam((HX1 - 3.4, 3.0, 9.0), (HX1 - 3.6, -0.2, 9.0), 2.0, IR(2.6, 0.8), cap=True)
rs.beam((HX1 - 1.4, 6.8, 30.0), (HX1 - 1.4, 0.0, 30.0), 1.2, IR(2.4, 0.8), cap=True)
# the pump on the left: a big cylinder, its flywheel, a pipe down into the main
PX, PZ2 = -17.0, 31.0
rs.beam((PX, 0, PZ2), (PX, 8.4, PZ2), 4.2, IR(2.8, 0.6, 7))
rs.disc(PX, 8.4, PZ2 - 0.05, 2.1, lambda x, y, a, b, z, wp: fogged(tone(IRON, 3.6 - b * 1.6 - a * 0.6, x, y), z) if b > -0.35 else None)
for k in range(24):
    a0, a1 = math.pi * 2 * k / 24, math.pi * 2 * (k + 1) / 24
    rs.beam((PX + 2.6, 5.0 + 2.8 * math.sin(a0), PZ2 + 2.8 * math.cos(a0)), (PX + 2.6, 5.0 + 2.8 * math.sin(a1), PZ2 + 2.8 * math.cos(a1)), 0.5, IR(3.0, 0.5, k))
for k in range(6):
    a = math.pi * 2 * k / 6 + 0.3
    rs.beam((PX + 2.6, 5.0, PZ2), (PX + 2.6, 5.0 + 2.6 * math.sin(a), PZ2 + 2.6 * math.cos(a)), 0.22, IR(2.6, 0.5, k))
rs.beam((PX + 2.0, 5.0, PZ2), (PX + 3.0, 5.0, PZ2), 0.6, IR(3.0, 0.4))
rs.beam((PX + 1.6, 2.2, PZ2 - 1.4), (PX + 6.0, 2.2, PZ - 0.2), 1.0, redpipe(2.6, seed=3))
rs.beam((PX + 6.0, 2.2, PZ - 0.2), (PX + 6.6, PY + 0.6, PZ), 1.0, IR(2.6, 0.7), cap=True)
# the control desk under the window, dials dead, veins over it
def desk_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    for k in range(4):
        cx_, cy_ = -13.0 + k * 1.9, 2.4
        if math.hypot(X - cx_, Y - cy_) < 0.55:
            if math.hypot(X - cx_, Y - cy_) < 0.42:
                if abs((X - cx_) * 0.6 - (Y - cy_)) < 0.05: return fogged(STONE[0], z)    # the needle
                return fogged(tone(PAPER, 2.6, x, y), z)
            return fogged(tone(IRON, 4.4, x, y), z)
    c = steel(2.6, IRON, rust=0.8)(x, y, s, t, z, wp)
    vv = vein(X, Y, 6.0, -9.0, 0.0)
    if vv: c = tone(FLESH, 2.2 + vv, x, y)
    return c
rs.box(-14.4, -6.2, 0, 3.4, 33.6, 36.0, desk_front, steel(2.0, IRON, rust=0.8), top=steel(3.4, IRON, rust=0.8), cls='prop')
rs.quad((-14.4, 3.4, 34.4), (-6.2, 3.4, 34.4), (-14.4, 5.0, 35.6), lambda x, y, s, t, z, wp: fogged(tone(IRON, 2.4 + t * 1.2, x, y), z), cls='prop')   # the sloping panel
for k in range(5):
    rs.beam((-13.6 + k * 1.8, 3.6, 34.6), (-13.5 + k * 1.8, 4.2, 34.9), 0.14, lambda x, y, s, t, z, wp: fogged(PAPER[2] if s > 0.7 else IRON[1], z))   # levers
for k in range(4):                                                                 # cables from the desk into the floor
    rs.line3((-12.0 + k * 1.4, 0.4, 33.4), (-9.0 + k * 2.2, 0.05, 29.0 - k), lambda x, y, s, t, z, wp: fogged(STONE[0], z), w=0.14, sag=-0.2)

# ---------------------------------------------------------------------------------------------------- the trunk main and its burst
def main_pipe(x, y, s, t, z, wp):
    """the trunk main: heavy cast iron, flanged, rust in sheets, veins of redmass in it thickening toward the burst"""
    X, Y, Z = wp
    c = ironround(2.8, IRON, rust=0.55, seed=11)(x, y, s, t, z, wp)
    if abs(X) < 2.6:                                                               # the burst: a ragged hole on the pipe's upper front,
        dv = (t + 0.25) / 0.62                                                     # its lips torn back and gone grey (t: -1 top .. 1 bottom)
        rr = math.hypot(X / 1.9, dv)
        ang = math.atan2(dv, X / 1.9)
        jag = 1.0 + 0.22 * math.sin(ang * 7 + 1.3) + 0.12 * math.sin(ang * 13)
        if rr < jag * 0.8:
            return fogged(tone(IRON, 0.2 + rr * 0.8 + (0.6 if dv > 0.4 else 0), x, y), z)   # the hollow inside
        if rr < jag:
            return fogged(tone(STONE, 4.4 - (rr / jag) * 1.6 + (wn(1, X * 5, t * 3) - 0.5), x, y), z)   # the lips
    vv = abs(_vn[0](X * 0.8 + 3000, t * 1.6 + 3000) - 0.5) < 0.012 + 0.06 * max(0.0, 1 - abs(X) / 7.0)
    if vv and abs(X) < 8: c = tone(FLESH, 1.6 + (1 - abs(t)) * 1.2 + max(0.0, 1 - abs(X) / 4.0), x, y)
    return c
rs.beam((HX0 - 8.0, PY, PZ), (HX1, PY, PZ), PR * 2, main_pipe)
for X in (-24.0, -15.0, -6.5, 7.0, 16.0, 25.0):                                    # flanges and saddles
    rs.beam((X, PY, PZ), (X + 0.4, PY, PZ), PR * 2 + 0.5, IR(3.2, 0.6, int(X)))
    rs.box(X - 0.6, X + 1.0, 0, PY - 0.6, PZ - 0.9, PZ + 0.9, concrete(3.4, CONC), concrete(2.6, CONC), top=concrete(4.0, CONC), cls='prop')
# ---------------------------------------------------------------------------------------------------- clutter: a barrow, a ladder, a tool rack
rs.beam((22.0, 0.0, 33.0), (25.6, 9.6, 37.4), 0.25, timber(2.4, WOOD, seed=70)); rs.beam((23.2, 0.0, 33.0), (26.8, 9.6, 37.4), 0.25, timber(2.0, WOOD, seed=71))
for k in range(9):
    a = (k + 0.5) / 9
    rs.beam((22.0 + 3.6 * a, 9.6 * a, 33.0 + 4.4 * a), (23.2 + 3.6 * a, 9.6 * a, 33.0 + 4.4 * a), 0.16, timber(2.2, WOOD, seed=72 + k))
rs.box(9.0, 12.4, 0.6, 1.8, 30.0, 32.0, planks(2.6, WOOD, w=0.5, seed=80), planks(2.0, WOOD, w=0.5, seed=81), top=planks(1.8, WOOD, w=0.5, vertical=False, seed=82), cls='prop')   # a barrow
for (X, Z) in ((9.4, 30.2), (12.0, 30.2)):
    rs.beam((X, 0, Z), (X, 0.7, Z), 0.18, timber(2.0, WOOD))
for k in range(12):
    a0, a1 = math.pi * 2 * k / 12, math.pi * 2 * (k + 1) / 12
    rs.beam((13.0, 0.55 + 0.55 * math.sin(a0), 31.0 + 0.55 * math.cos(a0)), (13.0, 0.55 + 0.55 * math.sin(a1), 31.0 + 0.55 * math.cos(a1)), 0.14, IR(2.4, 0.6))

def found_clip(a, b):                                                             # the foundation's broken top
    X = HX0 + (HX1 - HX0) * a
    hh = 0.25 + max(0.0, wn(1, X * 0.22, 9.0) - 0.35) * 2.6 + (h32(int(X * 1.4), 95) % 3) * 0.08
    return b * 1.6 <= hh
rs.quad((HX0, 0, FRONT), (HX1, 0, FRONT), (HX0, 1.6, FRONT), bricks(3.0, 900), clip=found_clip, cls='wall')
for (Y, r) in ((6.4, 0.55), (8.4, 0.4)):                                           # pipes along the back wall, dropping into the floor
    rs.beam((HX0 + 0.5, Y, HZ1 - 0.7), (HX1 - 0.5, Y, HZ1 - 0.7), r * 2, IR(2.6, 0.5, int(Y)))
for (X, Y, r) in ((-24.0, 6.4, 0.55), (-3.0, 8.4, 0.4), (10.0, 6.4, 0.55), (22.0, 8.4, 0.4)):
    rs.beam((X, Y, HZ1 - 0.7), (X, 0.0, HZ1 - 0.7), r * 2, IR(2.4, 0.5, int(X)), cap=True)
    rs.beam((X, 2.0, HZ1 - 0.7), (X, 2.25, HZ1 - 0.7), r * 2 + 0.4, IR(3.0, 0.4, int(X)))
rs.beam((-26.0, 0.0, 26.0), (-26.0, 13.0, 26.0), 1.1, IR(2.6, 0.6, 3), cap=True)          # a riser by the broken wall, torn off at the top
rs.beam((-26.0, 13.0, 26.0), (-25.2, 14.2, 26.0), 1.1, IR(2.2, 0.8, 4), cap=True)

# rubble fallen from the roof and the walls, a rafter down across the floor, weeds where the light gets in
def heap(cx, cz, n, spread, seed):
    for i in range(n):
        X = cx + ((h32(seed, i, 1) % 100) / 100 - 0.5) * spread * 2
        Z = cz + ((h32(seed, i, 2) % 100) / 100 - 0.5) * spread
        d = math.hypot((X - cx) / spread, (Z - cz) / (spread * 0.5))
        sz = 0.22 + (h32(seed, i, 3) % 5) * 0.09
        Y0 = max(0.0, (1 - d) * spread * 0.35)
        rs.box(X - sz * 1.4, X + sz * 1.4, Y0, Y0 + sz, Z - sz * 0.7, Z + sz * 0.7, bricks(2.8, seed + i), bricks(2.0, seed + i + 50, along_z=True),
               top=bricks(3.8, seed + i + 90), cls='prop')
heap(-21.0, 17.5, 26, 2.6, 300); heap(18.0, 27.0, 18, 2.0, 400); heap(-8.0, 30.5, 12, 1.4, 500); heap(23.5, 16.0, 14, 1.6, 600)
rs.beam((6.0, 0.35, 15.6), (17.0, 2.6, 19.4), 0.8, timber(2.0, WOOD, seed=700), cap=True)                       # a fallen rafter
rs.beam((12.0, 1.7, 17.6), (13.4, 0.0, 16.8), 0.5, timber(1.8, WOOD, seed=701), cap=True)
for i in range(16):                                                                # weeds near the breach and in the cracks
    X = HX0 + 1.0 + (h32(i, 81) % 120) / 10.0; Z = 15.0 + (h32(i, 82) % 140) / 10.0
    for k in range(6):
        hh = 0.5 + (h32(i, k, 83) % 10) / 9
        lean = ((h32(i, k, 84) % 100) / 100 - 0.5) * 0.8
        rs.beam((X + k * 0.06, 0, Z), (X + k * 0.06 + lean, hh, Z), 0.07, lambda x, y, s, t, z, wp: fogged(tone(REED, 1.6 + s * 2.0, x, y), z), w1=0.02)
for k in range(3):                                                                 # cables hanging from the rafters
    X = -20.0 + k * 13.0
    rs.line3((X, HTOP - 0.3, 22.0 + k * 5), (X + 2.0, 9.0 + k * 2.0, 22.4 + k * 5), lambda x, y, s, t, z, wp: fogged(STONE[0], z), w=0.12, sag=0.6)

def P2(X, Y, Z):
    p = proj(X, Y, Z); return (round(p[0]), round(p[1]))

def glow_cls(col, cls_):
    """a few spots along the veins glow (they light the floor round them a little)"""
    for y in range(HY, H):
        for x in range(W):
            g = rs.G[y][x]
            if g is None or g[5] != 'ground' or g[4] is None: continue
            X, _, Z = g[4]
            if math.hypot(X - HEART[0], Z - HEART[2]) > 11: continue
            if math.hypot(X - HEART[0], Z - HEART[2]) > 6: continue
            if vein(X, Z, 10.0, HEART[0], HEART[2]) == 1.0 and h32(int(X * 3), int(Z * 3), 9) % 7 == 0:
                col[y][x] = CRYST[2]; cls_[y][x] = 'emit'
RENDER = dict(fog=fog_of, post=glow_cls, mirror=lambda x, y, wp: 0.6 * floor_puddle(wp[0], wp[2]),
              light_gain=1.3, grime_gain=0.9, bloom=0.7, stain_gain=0.8, damp_gain=0.15, sheen_gain=0.5)

# ---------------------------------------------------------------------------------------------------- the redmass (its own sprite)
def growth(rs, glow=1.0):
    """coral of blood-coloured steel: oxidised iron tendrils rising and branching out of the burst, crystal clusters
    (orange-red, lit from within) along them and at their tips, a seething knot of it filling the tear"""
    def tendril_sh(x, y, s, t, z, wp):
        v = 1.8 + 2.4 * (roundlit(t) - 0.5) + s * 0.8 + (wn(1, wp[0] * 5, wp[1] * 5) - 0.5) * 0.9
        c = tone(FLESH, v, x, y)
        if abs(t) < 0.25 and h32(int(wp[1] * 9), int(wp[0] * 9), 3) % 4 == 0: c = tone(CRYST, 1.6 + s * 1.4, x, y)   # a lit seam
        return fogged(c, z)
    def crystal(X, Y, Z, r, k):
        """a cluster of three or four pointed crystals"""
        for j in range(1 + k % 2):
            a = 0.6 + (h32(k, j, 1) % 190) / 100                                   # mostly upward, fanned
            L = r * (1.6 + (h32(k, j, 2) % 100) / 80)
            tip = (X + math.cos(a) * L * 0.8, Y + math.sin(a) * L, Z - 0.1 - (h32(k, j, 3) % 40) / 100)
            def cs(x, y, s, t, z, wp, j=j):
                v = 1.4 + s * 2.8 * glow + (0.9 if t < -0.2 else -0.8 if t > 0.3 else 0)          # a lit facet, a dark facet
                return tone(CRYST, v, x, y)
            rs.beam((X, Y, Z), tip, r * 0.6, cs, w1=0.0, cls='emit')
    rng = [h32(i, 51) for i in range(200)]
    def branch(P, d, length, w, depth, k):
        if depth == 0 or length < 0.4:
            crystal(P[0], P[1], P[2], 0.25 + w * 0.25, k)
            return
        a = math.atan2(d[1], d[0])
        n = 5
        pts = [P]
        for i in range(n):
            a += ((rng[(k + i) % 200] % 100) / 100 - 0.5) * 0.5
            q = pts[-1]
            pts.append((q[0] + math.cos(a) * length / n, q[1] + math.sin(a) * length / n, q[2] - 0.05 * length / n))
        for i in range(n):
            rs.beam(pts[i], pts[i + 1], w * (1 - i / n * 0.5), tendril_sh, w1=w * (1 - (i + 1) / n * 0.5), cap=True)
        if rng[k % 200] % 3 == 0: crystal(pts[2][0], pts[2][1], pts[2][2], 0.22 + w * 0.2, k + 7)
        for b in range(2):
            da = (0.5 + (rng[(k * 3 + b) % 200] % 60) / 100) * (1 if b else -1)
            branch(pts[-1], (math.cos(a + da), math.sin(a + da)), length * 0.6, w * 0.7, depth - 1, k * 2 + b + 1)
    X0, Y0, Z0 = HEART[0], PY + 0.5, PZ - 0.4
    for i, (ang, L, w) in enumerate(((1.57, 4.6, 1.0), (1.2, 4.0, 0.85), (1.95, 4.2, 0.9), (0.6, 3.2, 0.7), (2.55, 3.0, 0.66), (1.4, 3.4, 0.6))):
        branch((X0 + (i - 2.5) * 0.5, Y0, Z0 - (i % 2) * 0.3), (math.cos(ang), math.sin(ang)), L, w * 1.15, 2, 10 + i * 17)
    def knot(x, y, a, b, z, wp):                                                   # the mass in the tear
        r = math.hypot(a, b)
        if r > 0.97: return None
        v = 1.4 + (1 - r) * 1.8 - b * 1.2 - a * 0.4 + (wn(1, x * 0.35, y * 0.35) - 0.5) * 1.2
        if abs(wn(2, x * 0.25, y * 0.25) - 0.5) < 0.04: return tone(CRYST, 2.0 + (1 - r) * 2.4 * glow, x, y)   # lit seams
        return tone(FLESH, v, x, y)
    for k in range(9):                                                             # a lumpy mass filling the tear
        a = k / 9 * math.pi
        rr = 0.7 + (h32(k, 71) % 5) * 0.16
        rs.disc(X0 + math.cos(a) * (1.4 - rr * 0.3), PY + 0.4 + math.sin(a) * 0.9 + (h32(k, 72) % 3) * 0.15, PZ - 1.0 - k * 0.02, rr, knot, cls='prop')
    for k in range(9):                                                             # crystals breaking through the knot
        a = (h32(k, 61) % 628) / 100
        crystal(X0 + math.cos(a) * 1.4, PY + 0.6 + abs(math.sin(a)) * 0.8, PZ - 1.5, 0.32, 100 + k)
    for k in range(8):                                                             # roots gripping the pipe either side
        sgn = 1 if k % 2 else -1
        rs.beam((X0 + sgn * 1.6, PY + 0.8, PZ - 1.0), (X0 + sgn * (2.6 + k * 0.5), PY + 1.1 - k * 0.15, PZ - 1.3 + k * 0.04), 0.45, tendril_sh, w1=0.1, cap=True)

if __name__ == '__main__':
    img = rs.render(INK, **RENDER)
    img.save(f'{OUT}/redmass.png')
    print('done redmass island')
    print('heart (burst) at', P2(*HEART), '| window', P2(WIN[0], WIN[3], HZ1), P2(WIN[1], WIN[2], HZ1), '| doorway', P2(DOOR[0], DOOR[2], HZ1), P2(DOOR[1], 0, HZ1),
          '| breach', P2(HX0, 0, 18), P2(HX0, 0, 28), '| pipe top/bottom', P2(0, PY + PR, PZ), P2(0, PY - PR, PZ))
    n0 = rs.n
    growth(rs)
    img2 = rs.render(INK, **RENDER)
    img2.save(f'{OUT}/redmass_with_heart.png')
    (hx, hy) = P2(*HEART)
    BOX = (hx - 150, hy - 230, hx + 150, hy + 70)
    spr = Image.new('RGBA', (BOX[2] - BOX[0], BOX[3] - BOX[1]), (0, 0, 0, 0))
    glw = Image.new('RGBA', spr.size, (0, 0, 0, 0))
    p0, p1, ps, pg = img.load(), img2.load(), spr.load(), glw.load()
    mine = lambda x, y: rs.G[y][x] is not None and rs.G[y][x][1] > n0
    for y in range(BOX[1], BOX[3]):
        for x in range(BOX[0], BOX[2]):
            ch = max(abs(p0[x, y][i] - p1[x, y][i]) for i in range(3))
            edge = any(mine(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if mine(x, y) or (edge and ch > 6):
                ps[x - BOX[0], y - BOX[1]] = p1[x, y] + (255,)
                if mine(x, y) and rs.G[y][x][5] == 'emit':
                    pg[x - BOX[0], y - BOX[1]] = p1[x, y] + (255,)
            elif ch > 5:                                                           # the light it throws on the pipe and floor
                ps[x - BOX[0], y - BOX[1]] = p1[x, y] + (min(255, 60 + ch * 12),)
    bb = spr.getbbox()
    spr.crop(bb).save(f'{OUT}/redmass_heart.png'); glw.crop(bb).save(f'{OUT}/redmass_glow.png')
    print('done heart: top-left', (BOX[0] + bb[0], BOX[1] + bb[1]), 'size', (bb[2] - bb[0], bb[3] - bb[1]), 'burst', (hx, hy))
