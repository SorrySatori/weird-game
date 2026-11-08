"""The great hall of the Lumen Directorate (LumenDirectorateInteriorScene), 1067x600, the shared camera (raster3d.py).
After the old art (LumenDirectorateInterior.png, a golden glowing nave): the same composition in the overcast day --
the light comes in cool through the glass vault, the warm gold (the Directorate's signature) from the far doorway,
the rose window, the lamps.

  the nave     a pointed barrel vault glazed between stone ribs (transverse, diagonal, a ridge rib); clustered
               columns with ivy-wrapped capitals standing in square planters of ferns -- the "biting ferns" that watch
               who comes and goes (their fiddleheads are curled like jaws); pointed arcades into the side aisles,
               festoons of trained ivy along the spandrels
  the aisles   tall leaded windows with the overcast day in them, a low ceiling, floor lamps
  the far end  a flight of steps up to a dais with clipped hedges, the glowing doorway, two stained lancets and the
               rose window over them (a sun of amber and olive glass)
  the floor    polished marble, limestone and olive-green tiles in a checker, the Directorate's brass sun inlaid in
               the middle; it mirrors the doorway, the windows and the columns
  the desks    left: Seldo's, under stacks of forms and permits, a stamp rack, an inkwell, a green-shaded lamp;
               right: the Angle Corrector's, ledgers and drafting tools -- a big brass protractor on a stand, set
               squares, dividers
No people are baked in. The walk line y 534 runs in front of both desks (their fronts stand at depth 18.6).

    python3 lumen_int_bg.py <outdir>   ->  lumen_int.png + lumen_int_points.json"""
import sys, math, json
from PIL import Image
from common import h32, ramp
from raster3d import Raster, proj, ray, W, H, CX, HY, F, CAMH
from pal_day import SKY, FLOWER

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
from common import make_noise, band
_nz = [make_noise(1, s, 509, 509) for s in (61, 62, 63, 64)]
def wn(i, a, b): return _nz[i](a + 3000.0, b + 3000.0)
def ri(r, i): return r[max(0, min(len(r) - 1, int(i)))]
def tone(r, v, x, y): return ri(r, band(v, x, y))
def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def rng(*k):
    h = h32(*k)
    h ^= h >> 16; h = (h * 0x85ebca6b) & 0xffffffff; h ^= h >> 13; h = (h * 0xc2b2ae35) & 0xffffffff; h ^= h >> 16
    return h / 4294967295.0

LIME   = ramp('#17191a #202323 #2a2d2c #353836 #414441 #4e504c #5b5d58 #696a64 #777770 #86857d #95938a #a4a197 #b2aea3')
VERD   = [mix(c, (70, 74, 66), 0.25) for c in ramp('#0f1612 #141e18 #1a271f #213127 #293b2f #314638 #3b5241 #465e4b')]   # olive-green marble
WALNUT = ramp('#140c08 #1e130c #2a1a10 #372316 #452c1c #543724 #64432d')
BRASS  = ramp('#2e2412 #4a3a1a #6b5424 #8e7232 #b09048 #c9aa62 #dcc282')
IRON   = ramp('#0c0e0d #141715 #1d211e #272c28 #323833 #3f4640')
IVY    = ramp('#0f1812 #152218 #1b2c1e #233826 #2b452e #345236 #3f6040 #4b6f4a')
FERN   = ramp('#101a10 #172515 #1f321b #284022 #324f2a #3d5f33 #4b703d')
PAPER  = ramp('#3a3a33 #4d4c43 #615f54 #757266 #898577 #9c9888 #afaa98')
SOIL   = ramp('#120e09 #1b150e #251d14 #30261a')
GLASSV = ramp('#2c3a38 #364644 #415250 #4d5f5c #5a6c68 #687a75 #778882 #879690 #98a59e')   # the overcast day through glass
LANT   = [mix(c, (118, 112, 96), 0.15) for c in ramp('#5c4520 #7d5f2a #9d7835 #b98f42 #cfa553 #e2bd6b #f2d690')]
STAIN  = [(150, 106, 46), (118, 132, 58), (86, 107, 47), (172, 128, 60), (98, 76, 46), (128, 150, 120)]
GREENSHADE = ramp('#10261a #18382a #22503a #2e6a4c')
INK = (8, 10, 9)
FOGC = (52, 62, 58)
def fogk(z): return max(0.0, min(0.35, (z - 24) / 110.0))
def fogged(c, z): return mix(c, FOGC, fogk(z))

WN, WA, ZB = 20.0, 30.0, 50.0             # the colonnade, the aisle wall, the back wall
YC, YS, YA = 19.0, 27.0, 41.0             # the capitals, the vault's springing, its apex
COLZ = (18.0, 28.0, 38.0)
BAY, RIB0 = 10.0, 8.0                     # the vault's bays
CR = 1.7                                  # column radius
DY, ZST0, ZST1 = 3.0, 36.0, 42.0          # the dais, the foot of the steps, the dais front
rs = Raster()
PTS = {}

def masonry(r, u, Y, z, x, y, v0, ch=0.55, L=1.1, seed=0, rough=0.3, weather=0.6, joint=1.2):
    ps = z / F
    row = math.floor(Y / ch); fv = Y / ch - row
    uu = u + (h32(row, seed, 5) % 97) / 97.0 * L * 2.0
    col = math.floor(uu / L); fu = uu / L - col
    c0 = col
    while h32(row, c0, seed) % 3 == 0 and col - c0 < 2: c0 -= 1
    bid = h32(row, c0, seed + 7)
    v = v0 + ((bid % 9) - 4) * 0.08 + (wn(0, u * 0.2 + seed * 7.0, Y * 0.2) - 0.5) * weather + (wn(1, u * 5.0 + (bid % 17), Y * 5.0) - 0.5) * rough
    if fv > 1 - 1.5 * ps / ch: v += 0.3
    if fv < ps / ch or (fu < ps / L and h32(row, col, seed) % 3 != 0): v -= joint
    return tone(r, v, x, y)
def plain(r, v0, k=0.5):
    return lambda x, y, s, t, z, wp: fogged(tone(r, v0 + (wn(0, ((wp or (0, 0, 0))[0] + (wp or (0, 0, 0))[2]) * 2, (wp or (0, 0, 0))[1] * 2) - 0.5) * k, x, y), z)
def leaf_sh(r, v0, seed=0, cell=0.36):
    """a surface of small overlapping leaves, lit from above"""
    def f(X, Y, x, y):
        row = math.floor(Y / cell); cu = X / cell + (row % 2) * 0.5; col = math.floor(cu)
        fu, fv = cu - col, Y / cell - row
        k = h32(col, row, seed)
        d = ((fu - 0.5 - (k % 5) * 0.06 + 0.12) / 0.66) ** 2 + ((fv - 0.45) / 0.56) ** 2
        cl = (wn(0, X * 0.9 + seed, Y * 0.9) - 0.5) * 2.0
        if d > 1: return tone(r, v0 - 2.4 + cl * 0.5, x, y)
        return tone(r, v0 + cl + (fv - 0.45) * 2.2 - (fu - 0.5) * 0.8 + ((k >> 4) % 5 - 2) * 0.3, x, y)
    return f
IVYL = leaf_sh(IVY, 4.0, 3)

# lights the analytic floor reflection knows about
DOOR = (0.0, DY, 15.4, 3.7)               # cx, sill, apex, half-width
LANCETS = [(-15.0, 6.0, 17.0, 1.6), (-9.0, 5.0, 18.0, 1.9), (9.0, 5.0, 18.0, 1.9), (15.0, 6.0, 17.0, 1.6)]
ROSE = (0.0, 30.4, 6.4)

def pointed(u, v, w, k=1.5):
    """the half-width of the pointed arch of span 2w (springing at v = 0) passing through (u, v)"""
    u = abs(u)
    if v <= 0: return u
    a = 2 * k - 1; b = 2 * u * (k - 1)
    return (b + math.sqrt(b * b + 4 * a * (u * u + v * v))) / (2 * a)
def apex(w, k=1.5): return math.sqrt(k * k - (k - 1) ** 2) * w

# ---------------------------------------------------------------------------------------------------- the floor
SUNC = (0.0, 27.0)
def floor_sh(x, y, s, t, z, wp):
    """pale limestone slabs, every one framed by a thin band of olive-green marble; a green runner with pale borders
    from the door to the steps, the brass sun let into it; worn, scuffed, a few cracked slabs. The polish is the
    raster mirror (render(mirror=)) -- this shader only darkens the bands' joints a little."""
    X, _, Z = wp
    T, B = 2.6, 0.26
    ps, psz = z / F, z * z / (F * CAMH)
    fu, fv = (X / T + 0.5) % 1, (Z / T) % 1
    i, j = math.floor(X / T + 0.5), math.floor(Z / T)
    sid = h32(i + 99, j + 99, 5)
    du, dv = min(fu, 1 - fu) * T, min(fv, 1 - fv) * T                                 # distance to the slab's edge
    runner = abs(X) < 4.2 and Z < ZST0 - 0.4
    if runner:
        r_, v = VERD, 3.2 + (wn(0, X * 0.4, Z * 0.4) - 0.5) * 1.0
        if abs(abs(X) - 3.75) < 0.2: r_, v = LIME, 6.4                                  # its pale border
        if abs(((X * 1.4 + Z * 0.6) + wn(2, X * 0.8, Z * 0.8) * 3) % 2.6 - 1.3) < 0.05: v += 1.2   # veins
        if (Z / 1.7) % 1 < psz / 1.7 * 0.9 and abs(X) < 3.55: v -= 1.0
    elif du < B * 0.5 or dv < B * 0.5:                                                 # the green bands
        r_, v = VERD, 3.4 + (wn(1, X * 2, Z * 2) - 0.5) * 0.8
        if du < ps * 0.6 or dv < psz * 0.6: v -= 0.8
    else:
        r_ = LIME
        v = 6.0 + ((sid % 7) - 3) * 0.16 + (wn(0, X * 0.35, Z * 0.35) - 0.5) * 0.9 + (wn(1, X * 0.12, Z * 0.12) - 0.5) * 0.7
        if abs(((X * 0.6 - Z * 1.1) + wn(3, X * 0.6, Z * 0.6) * 4) % 3.1 - 1.5) < 0.04: v -= 0.9   # faint veins
        if min(du, dv) < B * 0.5 + ps * 1.2: v -= 0.6                                    # the slab's sunk edge
        if sid % 13 == 0 and abs(((fu - 0.3) - (fv - 0.5) * 0.7)) < ps / T * 1.4: v -= 1.6     # a crack
        if sid % 9 == 4: v -= 0.6                                                        # a duller, stained slab
    # the brass sun let into the middle
    dx, dz = X - SUNC[0], Z - SUNC[1]; d = math.hypot(dx, dz)
    if d < 3.4:
        a = math.atan2(dz, dx)
        if d < 1.1: r_, v = BRASS, 3.4 + (wn(1, X * 4, Z * 4) - 0.5) - (1.0 if abs(d - 0.8) < 0.06 else 0)
        elif abs(d - 3.15) < 0.13: r_, v = BRASS, 3.2
        elif 1.2 < d < 3.0 and abs(((a / (2 * math.pi) * 16) % 1) - 0.5) < 0.5 * (3.0 - d) / 1.8 * 0.85: r_, v = LIME, 8.6 - (d - 1.2) * 0.5
        else: r_, v = VERD, 2.6
    worn = math.exp(-(X / 5.0) ** 2) * (1 if Z < ZST0 else 0)                          # the trodden way is duller
    v += (wn(3, X * 5.0, Z * 5.0) - 0.5) * 0.35 * (1 + worn)                           # scuffs
    c = tone(r_, v - 0.4 * worn, x, y)
    return fogged(c, z)
def floor_gloss(x, y, wp):
    X, _, Z = wp
    if Z > ZST0 - 0.2 and abs(X) < 7.2: return 0.0                                     # (not on the steps)
    worn = math.exp(-(X / 5.0) ** 2) * (1 if Z < ZST0 else 0)
    return max(0.0, 0.34 - 0.16 * worn + (wn(2, X * 0.5, Z * 1.2) - 0.5) * 0.16)
rs.quad((-WA, 0, 3), (WA, 0, 3), (-WA, 0, ZB), floor_sh, cls='ground')

# ---------------------------------------------------------------------------------------------------- the vault
def vault_profile(X):
    """the vault's height over the nave at |X| (a pointed barrel: springing YS at WN, apex YA)"""
    u = abs(X)
    # the right arc's centre (xc, YS): through (WN, YS) and (0, YA)
    xc = (WN * WN - (YA - YS) ** 2) / (2 * WN); R = WN - xc
    return YS + math.sqrt(max(0.0, R * R - (u - xc) ** 2))
RIBZ = [RIB0 + BAY * i for i in range(5)]
def vault_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    ps = z / F
    rw = max(0.32, 1.6 * ps)
    rib = None
    for zr in RIBZ:
        if abs(Z - zr) < rw: rib = 'tr'
    if abs(X) < rw * 0.8: rib = 'ridge'
    zc = (math.floor((Z - RIB0) / BAY) + 0.5) * BAY + RIB0                              # the bay's centre
    if abs(abs(X) / WN - abs(Z - zc) / (BAY / 2)) < rw / (BAY / 2) * 1.2: rib = 'diag'
    if rib:
        v = 7.2 - (Y - YS) / (YA - YS) * 0.8 + (wn(1, X * 2, Z * 2) - 0.5) * 0.6
        return fogged(tone(LIME, v - (1.6 if rib == 'diag' and (X * (Z - zc)) > 0 else 0), x, y), z)
    # glazing: small panes on iron bars, the overcast sky behind, milky glass; olive/amber panes edging the ribs
    q = (Y - YS) / (YA - YS)
    pu, pv = X / 1.1, Z / 1.4
    if (pu % 1) < ps / 1.1 * 1.0 or (pv % 1) < ps / 1.4 * 1.2: return fogged(tone(IRON, 2.6, x, y), z)
    k = h32(math.floor(pu) + 99, math.floor(pv) + 99, 7)
    v = 4.6 + q * 2.6 + ((k % 5) - 2) * 0.25 + (wn(3, X * 0.25, Z * 0.25) - 0.5) * 1.6
    c = tone(GLASSV, v, x, y)
    near_rib = min(abs(Z - zr) for zr in RIBZ) < 1.0 or abs(abs(X) / WN - abs(Z - zc) / (BAY / 2)) < 0.12
    if near_rib and k % 3 == 0: c = mix(c, STAIN[k % 4], 0.55)
    if wn(2, X * 0.4 + 7, Z * 0.4) > 0.66: c = mix(c, (60, 70, 62), 0.35)              # grime / leaves lying on the glass
    return fogged(c, z)
NV = 22
xc_ = (WN * WN - (YA - YS) ** 2) / (2 * WN); R_ = WN - xc_
for side in (-1, 1):
    th0 = 0.0; th1 = math.acos(-xc_ / R_)
    for i in range(NV):
        a0 = th0 + (th1 - th0) * i / NV; a1 = th0 + (th1 - th0) * (i + 1) / NV
        P0 = (side * (xc_ + R_ * math.cos(a0)), YS + R_ * math.sin(a0)); P1 = (side * (xc_ + R_ * math.cos(a1)), YS + R_ * math.sin(a1))
        rs.quad((P0[0], P0[1], 4.0), (P1[0], P1[1], 4.0), (P0[0], P0[1], ZB), vault_sh, cls='emit')

# ---------------------------------------------------------------------------------------------------- the back wall
def back_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    if abs(X) < WN and Y > vault_profile(X): return None
    if abs(X) >= WN and Y > 24.5: return None
    # surrounds of the doorway, the lancets, the rose
    d = pointed(X - DOOR[0], Y - (DOOR[2] - apex(DOOR[3])), DOOR[3])
    if Y > DOOR[1] and d < DOOR[3] + 0.9:
        if d <= DOOR[3]: return None
        q = (d - DOOR[3]) / 0.9
        return fogged(tone(LIME, 6.4 + 1.4 * math.sin(q * math.pi * 2) * (1 - q) - (1.6 if q < 0.12 else 0), x, y), z)
    for (lx, l0, l1, lw) in LANCETS:
        dl = pointed(X - lx, Y - l1, lw)
        if Y > l0 - 0.4 and dl < lw + 0.45:
            if dl <= lw and Y > l0: return None
            return fogged(tone(LIME, 7.6 + (1.0 if Y < l0 else 0) - (1.4 if dl < lw + 0.1 else 0), x, y), z)
    rr = math.hypot(X - ROSE[0], Y - ROSE[1])
    if rr < ROSE[2] + 0.8:
        if rr <= ROSE[2]: return None
        return fogged(tone(LIME, 7.0 + math.sin((rr - ROSE[2]) / 0.8 * math.pi) * 1.4, x, y), z)
    if abs(Y - 24.2) < 0.4 and abs(X) < WN: return fogged(tone(LIME, 8.0 - (2 if Y < 23.9 else 0), x, y), z)   # a string course
    v = 5.2 + 1.2 * math.exp(-((Y - 12) / 14) ** 2)
    return fogged(masonry(LIME, X, Y, z, x, y, v, seed=11), z)
rs.quad((-WA, 0, ZB), (WA, 0, ZB), (-WA, YA + 1, ZB), back_sh, cls='wall', cut=True)
def door_light(x, y, s, t, z, wp):
    """beyond the doorway: a bright, warm, hazy room -- the inner sanctum, too much light to see into"""
    X, Y, Z = wp
    if Y < DOOR[1] or pointed(X - DOOR[0], Y - (DOOR[2] - apex(DOOR[3])), DOOR[3]) > DOOR[3]: return None
    q = (Y - DOOR[1]) / (DOOR[2] - DOOR[1])
    v = 5.6 - abs(X) / DOOR[3] * 1.2 - q * 0.8 + (wn(1, X * 2, Y * 1.5) - 0.5) * 0.6
    if q < 0.08: v += 0.8
    return tone(LANT, v, x, y)
rs.quad((-DOOR[3], DOOR[1], ZB + 0.6), (DOOR[3], DOOR[1], ZB + 0.6), (-DOOR[3], DOOR[2] + 0.2, ZB + 0.6), door_light, cls='emit', cut=True)
def lancet_glass(lx, l0, l1, lw, seed):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        if Y < l0 or pointed(X - lx, Y - l1, lw) > lw: return None
        ps = z / F
        if abs(X - lx) < max(0.12, ps) : return tone(LIME, 4.0, x, y)                       # the mullion
        pu, pv = (X - lx) / 0.6, Y / 0.8
        if (pu % 1) < ps / 0.6 * 1.2 or (pv % 1) < ps / 0.8 * 1.2: return (40, 34, 24)
        k = h32(math.floor(pu) + 50, math.floor(pv) + 50, seed)
        c = STAIN[k % len(STAIN)]
        c = mix(c, (238, 214, 150), 0.25 + 0.15 * ((k >> 4) % 3))
        return mix(c, (0, 0, 0), 0.12 * ((k >> 7) % 3))
    return sh
for i, (lx, l0, l1, lw) in enumerate(LANCETS):
    rs.quad((lx - lw, l0, ZB + 0.1), (lx + lw, l0, ZB + 0.1), (lx - lw, l1 + apex(lw) + 0.1, ZB + 0.1), lancet_glass(lx, l0, l1, lw, 30 + i), cls='emit', cut=True)
def rose_glass(x, y, s, t, z, wp):
    X, Y, Z = wp
    rr = math.hypot(X - ROSE[0], Y - ROSE[1]) / ROSE[2]
    if rr > 1: return None
    a = math.atan2(Y - ROSE[1], X - ROSE[0])
    ps = z / F / ROSE[2]
    if abs(rr - 0.34) < ps * 1.4 or abs(rr - 0.72) < ps * 1.2 or rr > 0.95: return tone(LIME, 6.4, x, y)
    seg = (a / (2 * math.pi) * (12 if rr > 0.34 else 6)) % 1
    if rr > 0.34 and (seg < ps * 6 / rr or seg > 1 - ps * 6 / rr): return tone(LIME, 5.8, x, y)    # spokes
    if rr < 0.15: return tone(LANT, 6.0, x, y)                                                    # the sun's eye
    if rr < 0.34:                                                                                  # a sun: gold rays
        return tone(LANT, 4.6 - rr * 4 + (0.8 if seg < 0.5 else 0), x, y)
    k = int((a + math.pi) / (2 * math.pi) * 12) + (0 if rr < 0.72 else 12)
    c = STAIN[(k * 7) % len(STAIN)]
    c = mix(c, (236, 210, 150), 0.3 if rr < 0.72 else 0.15)
    if (rr * 18) % 1 < 0.12: c = mix(c, (30, 26, 20), 0.6)
    return c
rs.quad((-ROSE[2], ROSE[1] - ROSE[2], ZB + 0.1), (ROSE[2], ROSE[1] - ROSE[2], ZB + 0.1), (-ROSE[2], ROSE[1] + ROSE[2], ZB + 0.1), rose_glass, cls='emit', cut=True)

# ---------------------------------------------------------------------------------------------------- the arcades and the aisles
def arcade_sh(side):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        if Y > vault_profile(WN) + 0.05: return None
        # the openings between the columns: pointed arches springing at the capitals
        for (za, zb) in zip((8.0,) + COLZ, COLZ + (ZB,)):
            zm, hw = (za + zb) / 2, (zb - za) / 2 - CR * 0.8
            if abs(Z - zm) < hw + 0.7:
                d = pointed(Z - zm, Y - YC, hw)
                if d <= hw: return None
                if d < hw + 0.7:
                    q = (d - hw) / 0.7
                    return fogged(tone(LIME, 7.0 + 1.2 * math.sin(q * math.pi) - (1.4 if q < 0.15 else 0), x, y), z)
        if Y < YC: return None
        if abs(Y - 25.6) < 0.35: return fogged(tone(LIME, 7.6 - (1.8 if Y < 25.4 else 0), x, y), z)   # a string course
        e = ivy_band(Z, Y)
        if e: return fogged(e(x, y), z)
        return fogged(masonry(LIME, Z, Y, z, x, y, 5.6, seed=21 + side), z)
    return sh
def ivy_band(Z, Y):
    """festoons of trained ivy along the arcade's spandrels, hung from the string course"""
    for (za, zb) in zip(COLZ[:-1], COLZ[1:]):
        if za < Z < zb:
            q = (Z - za) / (zb - za)
            yc = 25.0 - 1.4 * math.sin(math.pi * q)
            th = 0.35 + 0.25 * math.sin(math.pi * q) + (wn(2, Z * 2, Y * 2) - 0.5) * 0.2
            if abs(Y - yc) < th: return lambda x, y: IVYL(Z, Y, x, y)
    return None
for side in (-1, 1):
    rs.quad((side * WN, 0, 4.0), (side * WN, 0, ZB), (side * WN, YS + 0.2, 4.0), arcade_sh(side), cls='wall', cut=True)
def aisle_wall(side):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        for zw in (13.0, 23.0, 33.0, 43.0):                                              # tall leaded windows
            if abs(Z - zw) < 2.6 and 3.5 < Y < 18.0 + apex(2.6) * 0.0:
                d = pointed(Z - zw, Y - 15.0, 2.6)
                if Y < 15.0 or d < 2.6:
                    ps = z * z / (F * max(1.0, abs(X)))
                    if d > 2.6 - 0.35 or Y < 3.8: return fogged(tone(LIME, 7.0, x, y), z)
                    if (Z / 0.7) % 1 < ps / 0.7 * 1.3 or (Y / 0.9) % 1 < 0.08: return tone(IRON, 2.0, x, y)
                    v = 5.0 + (Y - 3.5) / 14 * 2.0 + (wn(1, Z, Y) - 0.5) * 0.8
                    return tone(GLASSV, v, x, y)
        return fogged(masonry(LIME, Z, Y, z, x, y, 4.6, seed=31 + side), z)
    return sh
for side in (-1, 1):
    rs.quad((side * WA, 0, 3), (side * WA, 0, ZB), (side * WA, 24.5, 3), aisle_wall(side), cls='wall')
    rs.quad((side * WN, 24.0, 3), (side * WA, 24.0, 3), (side * WN, 24.0, ZB),
            lambda x, y, s, t, z, wp: fogged(tone(LIME, 2.6 + (1.0 if (wp[2] % 12) < 0.4 else 0) + (wn(0, wp[0], wp[2]) - 0.5) * 0.6, x, y), z), cls='ceil')

# ---------------------------------------------------------------------------------------------------- the columns
def cylinder(cx, cz, r, y0, y1, sh, n=20, cls='wall'):
    for i in range(n):
        a0, a1 = -math.pi + 2 * math.pi * i / n, -math.pi + 2 * math.pi * (i + 1) / n
        P0 = (cx + r * math.sin(a0), y0, cz - r * math.cos(a0)); P1 = (cx + r * math.sin(a1), y0, cz - r * math.cos(a1))
        if (P0[2] + P1[2]) / 2 > cz + r * 0.3: continue
        rs.quad(P0, P1, (P0[0], y1, P0[2]), sh, cls=cls)
def column_sh(cx, cz):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        phi = math.atan2(X - cx, -(Z - cz))
        lit = 1.3 * math.cos(phi - 0.4 * (1 if cx > 0 else -1)) - 0.5                       # light from the nave
        sh_ = (phi * 8 / math.pi) % 1                                                         # clustered shafts
        v = 6.0 + lit + (0.9 if 0.2 < sh_ < 0.5 else -0.5 if sh_ > 0.85 else 0)
        # ivy wrapping the upper shaft
        if Y > 12.5 + 2.5 * wn(1, phi * 2 + cx, 1.0) and wn(2, phi * 3 + cx, Y * 0.9) > 0.5 - (Y - 12.5) * 0.04:
            return fogged(IVYL(phi * CR * 2 + cx, Y, x, y), z)
        if (Y / 2.4) % 1 < 0.04: v -= 1.0                                                     # drum joints
        return fogged(tone(LIME, v + (wn(1, phi * 3, Y * 2) - 0.5) * 0.5, x, y), z)
    return sh
def capital_sh(cx, cz):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        phi = math.atan2(X - cx, -(Z - cz))
        if wn(3, phi * 4 + cx, Y * 3) > 0.3: return fogged(IVYL(phi * 3 + cx * 7, Y * 1.3, x, y), z)   # foliage
        return fogged(tone(LIME, 7.0 + 1.2 * math.cos(phi) - t * 1.5, x, y), z)
    return sh
for side in (-1, 1):
    for cz in COLZ:
        cx = side * WN
        cylinder(cx, cz, CR + 0.45, 0, 0.7, lambda x, y, s, t, z, wp: fogged(tone(LIME, 5.4 + t * 1.6 + (wn(1, wp[0] * 3, wp[2] * 3) - 0.5) * 0.6, x, y), z), n=16)
        cylinder(cx, cz, CR + 0.25, 0.7, 1.0, lambda x, y, s, t, z, wp: fogged(tone(LIME, 7.4 - (1.6 if t < 0.3 else 0), x, y), z), n=16)
        cylinder(cx, cz, CR, 1.0, YC - 1.2, column_sh(cx, cz), n=24)
        cylinder(cx, cz, CR + 0.6, YC - 1.2, YC + 0.4, capital_sh(cx, cz), n=24)
        cylinder(cx, cz, CR + 0.8, YC + 0.4, YC + 0.9, plain(LIME, 7.8), n=16)
        # hanging tails of ivy from the capital
        for k in range(4):
            a = (k / 4.0 - 0.4) * 2.0
            ax = cx + math.sin(a) * (CR + 0.7); az = cz - math.cos(a) * (CR + 0.7)
            ln = 1.0 + rng(k, cz, side) * 2.6
            for m in range(int(ln / 0.25)):
                rs.disc(ax + math.sin(m * 0.8 + k) * 0.12, YC - 1.2 - m * 0.25, az - 0.1, 0.2 - m * 0.006,
                        lambda x, y, s_, t_, z, wp, m=m: fogged(tone(IVY, 4.4 - t_ * 1.6 - s_ * 0.5 - m * 0.03 + (0.8 if (x + y) % 3 == 0 else 0), x, y), z) if s_ * s_ + t_ * t_ < 0.9 and h32(x, y, m) % 4 else None)

# ---------------------------------------------------------------------------------------------------- plants
def mound(X, Y, Z, r, ramp_, v0, seed, ragged=0.25):
    def sh(x, y, s, t, z, wp):
        d = s * s + t * t
        if d > 0.62 and h32(x, y, seed) % 3 == 0 and ragged > 0: return None
        if d > 0.9 and h32(x, y, seed + 1) % 2 == 0: return None
        v = v0 - s * 0.7 - t * 1.5 + ((h32(x // 2, y // 2, seed) % 5) - 2) * 0.25
        if h32(x, y, seed + 2) % 7 == 0: v -= 1.4
        return fogged(tone(ramp_, v, x, y), z)
    rs.disc(X, Y, Z, r, sh)
def fern(X, Y0, Z, size, seed):
    """a crown of arching fronds; the tips curl into fiddleheads with a row of pale teeth -- the biting ferns"""
    n = 9
    for f in range(n):
        a = f / n * 2 * math.pi + seed
        if math.cos(a) > 0.75: continue                                                          # the back ones are hidden
        ln = size * (0.75 + 0.35 * rng(seed, f))
        pts = []
        for m in range(14):
            q = m / 13.0
            rr = ln * q
            h = ln * (0.9 * q - 0.75 * q * q) + 0.3
            pts.append((X + math.sin(a) * rr, Y0 + h, Z - math.cos(a) * rr * 0.8, q))
        for (p0, p1) in zip(pts, pts[1:]):
            q = p0[3]
            rs.line3(p0[:3], p1[:3], lambda x, y, s, t, z, wp: fogged(FERN[2], z), w=0.07)
            # leaflets either side, shrinking to the tip
            w_ = 0.42 * (1 - q) + 0.08
            for sd in (-1, 1):
                lx = p0[0] + math.cos(a) * w_ * sd * 0.9; lz = p0[2] + math.sin(a) * w_ * sd * 0.6
                rs.line3(p0[:3], (lx, p0[1] - w_ * 0.35, lz), lambda x, y, s, t, z, wp, q=q: fogged(tone(FERN, 4.6 - q * 1.2 - t * 1.0 + (0.6 if (x + y) % 3 == 0 else 0), x, y), z), w=0.11)
        # the fiddlehead: a tight curl at the tip, with teeth
        tip = pts[-1]
        for m in range(8):
            ang = m / 8 * 1.6 * math.pi
            rr = 0.32 * (1 - m / 10)
            P = (tip[0] + math.sin(a) * rr * math.cos(ang), tip[1] + rr * math.sin(ang), tip[2] - math.cos(a) * rr * 0.8 * math.cos(ang))
            rs.disc(P[0], P[1], P[2] - 0.05, 0.1, lambda x, y, s, t, z, wp: fogged(FERN[3] if t < 0 else FERN[1], z))
            if m % 2 == 1: rs.disc(P[0], P[1] - 0.12, P[2] - 0.1, 0.045, lambda x, y, s, t, z, wp: (196, 190, 160))
def planter(X0, X1, Z0, Z1, h, seed, fern_at=None, ferns=3):
    def face(x, y, s, t, z, wp):
        X, Y, Z = wp
        if t > 0.86: return fogged(tone(LIME, 8.4 - (1.8 if t < 0.9 else 0), x, y), z)
        u = X if abs(wp[2] - Z0) < 0.05 else Z
        if 0.25 < t < 0.7 and abs(((u * 1.2) % 2) - 1) < 0.5: return fogged(tone(LIME, 5.2 - (0.8 if t < 0.32 else 0), x, y), z)   # a carved panel
        return fogged(tone(LIME, 6.6 + (wn(1, u * 2, Y * 2) - 0.5) * 0.6, x, y), z)
    rs.box(X0, X1, 0, h, Z0, Z1, face, face, top=lambda x, y, s, t, z, wp: fogged(tone(SOIL, 2.0 + (wn(0, wp[0] * 2, wp[2] * 2) - 0.5) * 1.4, x, y), z), cls='prop')
    for i in range(int((X1 - X0) * (Z1 - Z0) * 1.6)):
        mound(X0 + 0.3 + rng(seed, i, 1) * (X1 - X0 - 0.6), h + 0.25, Z0 + 0.3 + rng(seed, i, 2) * (Z1 - Z0 - 0.6), 0.35 + rng(seed, i, 3) * 0.25, IVY, 3.8, seed + i)
    for f in range(ferns):
        fx = X0 + (f + 0.5) / ferns * (X1 - X0); fz = Z0 + (Z1 - Z0) * (0.4 + 0.2 * rng(seed, f, 9))
        fern(fx, h, fz, 2.2 + rng(seed, f, 8) * 0.8, seed * 13 + f)

# planters round the column bases (the old art's greenery at the foot of every pillar)
for side in (-1, 1):
    for cz in COLZ[:2]:
        cx = side * WN
        a, b = sorted((cx - side * 2.4, cx + side * 0.6))
        planter(a, b, cz - 2.6, cz - CR + 0.2, 1.2, 100 + int(cz) + side * 5, ferns=2)
# the dais, the steps and the hedges up there
def dais_face(x, y, s, t, z, wp):
    X, Y, Z = wp
    if Y > DY - 0.3: return fogged(tone(LIME, 8.6 - (1.6 if Y < DY - 0.22 else 0), x, y), z)
    return fogged(masonry(LIME, X, Y, z, x, y, 5.6, ch=0.6, L=1.4, seed=41), z)
rs.box(-WN, WN, 0, DY, ZST1, ZB, dais_face, dais_face, top=floor_sh, cls='wall')
NST = 12; RISE = DY / NST; RUN = (ZST1 - ZST0) / NST
def tread(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 8.0 + (wn(0, X * 0.6, Z * 2) - 0.5) * 0.6 + 0.5 * math.exp(-(X / 2.5) ** 2)
    k = ZB / max(Z, 1) ; xw, yw = X * k, Y + (Y + CAMH) * (k - 1)
    if abs(xw) < DOOR[3] * 1.5: v += 0.8                                                        # the doorway's glow on the stone
    return fogged(tone(LIME, v, x, y), z)
def riser(x, y, s, t, z, wp):
    return fogged(tone(LIME, 5.4 + (1.0 if t > 0.75 else 0) + (wn(1, wp[0], wp[1] * 4) - 0.5) * 0.6, x, y), z)
for i in range(NST):
    rs.box(-7.0, 7.0, 0, RISE * (i + 1), ZST0 + RUN * i, ZST1 + 0.3, riser, riser, top=tread, cls='prop')
for side in (-1, 1):
    a, b = sorted((side * 7.0, side * 8.2))
    rs.box(a, b, 0, DY + 1.1, ZST0 - 0.4, ZST1 + 0.4, plain(LIME, 7.2), plain(LIME, 5.4), top=plain(LIME, 8.8), cls='prop')
    rs.box(a - 0.2, b + 0.2, 0, 2.0, ZST0 - 1.4, ZST0 - 0.2, plain(LIME, 7.6), plain(LIME, 5.6), top=plain(LIME, 9.0), cls='prop')  # newel
    rs.disc(side * 7.6, 2.5, ZST0 - 0.9, 0.5, lambda x, y, s, t, z, wp: fogged(tone(BRASS, 4.0 - t * 2 - s, x, y), z))
    # clipped hedges on the dais either side of the steps
    a, b = sorted((side * 9.4, side * 18.6))
    def hedge(x, y, s, t, z, wp):
        X, Y, Z = wp
        return fogged(leaf_sh(IVY, 4.2 if t > 0.5 else 3.4, 7, cell=0.26)(X + Z, Y + Z * 0.3, x, y), z)
    rs.box(a, b, DY, DY + 2.4, ZST1 + 0.6, ZST1 + 3.0, hedge, hedge, top=hedge, cls='prop')
    planter(a + 0.5, a + 3.0, ZST1 + 4.0, ZST1 + 6.0, DY + 1.0, 130 + side, ferns=1) if side < 0 else planter(b - 3.0, b - 0.5, ZST1 + 4.0, ZST1 + 6.0, DY + 1.0, 130 + side, ferns=1)

# ---------------------------------------------------------------------------------------------------- the desks
def walnut(v0, seed=0):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = v0 + (wn(1, (X + Z) * 0.7, Y * 9.0) - 0.5) * 0.9
        return fogged(tone(WALNUT, v, x, y), z)
    return sh
def desk(X0, X1, Z0, Z1, h=2.7, seed=0):
    def front(x, y, s, t, z, wp):
        X, Y, Z = wp
        if t > 0.9: return fogged(tone(WALNUT, 4.6, x, y), z)
        u = (X - X0) / (X1 - X0)
        if 0.05 < u < 0.95 and 0.12 < t < 0.82 and abs(((u * 3) % 1) - 0.5) < 0.42:          # three fielded panels
            q = abs(((u * 3) % 1) - 0.5) / 0.42
            return fogged(tone(WALNUT, 2.8 + (0.8 if q > 0.85 else 0) + (wn(1, X * 3, Y * 6) - 0.5) * 0.8, x, y), z)
        return walnut(3.6, seed)(x, y, s, t, z, wp)
    rs.box(X0, X1, 0, h, Z0, Z1, front, walnut(2.8, seed), top=walnut(4.8, seed), cls='prop')
    rs.box(X0 - 0.2, X1 + 0.2, h, h + 0.18, Z0 - 0.2, Z1 + 0.2, walnut(5.0, seed), walnut(4.0, seed), top=walnut(5.4, seed), cls='prop')
    return h + 0.18
def stack(X, Y0, Z, w, d, h, seed, kind='paper'):
    """a stack of forms (paper edges in bands) or books (coloured spines)"""
    def side(x, y, s, t, z, wp):
        if kind == 'paper':
            v = 3.2 - (1.0 if (wp[1] * 14) % 1 < 0.2 else 0) + ((h32(int(wp[1] * 14), seed) % 3) - 1) * 0.3
            return fogged(tone(PAPER, v, x, y), z)
        k = h32(int(wp[1] / 0.32), seed)
        c = [(92, 44, 36), (54, 72, 50), (120, 92, 50), (50, 58, 74), (96, 86, 70)][k % 5]
        return fogged(mix(c, (0, 0, 0), 0.4 if (wp[1] / 0.32) % 1 < 0.15 else 0.1), z)
    top = lambda x, y, s, t, z, wp: fogged(tone(PAPER, 4.0 if kind == 'paper' else 3.6, x, y), z)
    rs.box(X - w / 2, X + w / 2, Y0, Y0 + h, Z - d / 2, Z + d / 2, side, side, top=top, cls='prop')

# Seldo's desk (left), drowned in forms
LD = (-17.4, -8.6, 18.6, 21.2)
yt = desk(LD[0], LD[1], LD[2], LD[3], seed=1)
for i, (sx_, h) in enumerate(((-16.4, 1.6), (-15.4, 2.4), (-14.2, 1.1), (-12.6, 0.7), (-9.6, 1.9))):
    stack(sx_, yt, 19.6 + rng(i, 3) * 0.8, 0.9, 1.1, h, 60 + i)
stack(-11.0, yt, 20.2, 1.0, 1.0, 0.9, 70, kind='books')
rs.quad((-13.6, yt + 0.02, 19.2), (-11.2, yt + 0.02, 19.2), (-13.6, yt + 0.02, 20.4),
        lambda x, y, s, t, z, wp: fogged(tone(PAPER, 6.4 - (1.2 if abs(s - 0.5) < 0.04 else 0) - (0.8 if (t * 9) % 1 < 0.15 and abs(s - 0.5) > 0.08 else 0), x, y), z), cls='prop')  # an open ledger
rs.box(-15.9, -15.1, yt, yt + 0.5, 20.6, 21.0, plain(IRON, 1.6), plain(IRON, 1.2), top=lambda x, y, s, t, z, wp: (12, 14, 18), cls='prop')  # an inkwell
rs.line3((-15.4, yt + 0.4, 20.8), (-15.0, yt + 1.4, 20.7), lambda x, y, s, t, z, wp: (196, 188, 160), w=0.08)    # the quill
rs.box(-10.2, -9.0, yt, yt + 1.0, 20.4, 20.9, walnut(3.0), walnut(2.4), cls='prop')                               # a stamp rack
for k in range(4): rs.line3((-10.0 + k * 0.28, yt + 1.0, 20.5), (-10.0 + k * 0.28, yt + 1.5, 20.5), lambda x, y, s, t, z, wp: (40, 30, 22), w=0.12)
rs.line3((-12.2, yt, 20.6), (-12.2, yt + 1.7, 20.6), lambda x, y, s, t, z, wp: BRASS[2], w=0.1)                  # the green-shaded lamp
rs.disc(-12.2, yt + 1.9, 20.4, 0.55, lambda x, y, s, t, z, wp: (GREENSHADE[3] if t < -0.1 else GREENSHADE[1]) if t < 0.25 else (LANT[5] if abs(s) < 0.7 else None), cls='emit')
# the Angle Corrector's desk (right): ledgers and drafting tools
RD = (8.6, 17.4, 18.6, 21.2)
yt = desk(RD[0], RD[1], RD[2], RD[3], seed=2)
stack(16.4, yt, 20.0, 1.0, 1.2, 1.3, 80, kind='books'); stack(15.2, yt, 20.3, 0.9, 1.0, 0.6, 81)
rs.quad((9.8, yt + 0.02, 19.0), (12.6, yt + 0.02, 19.0), (9.8, yt + 0.02, 20.4),
        lambda x, y, s, t, z, wp: fogged(tone(PAPER, 6.2 - (1.6 if abs((s - 0.3) * 1.2 - (t - 0.4)) < 0.03 or abs(s - 0.62) < 0.02 else 0), x, y), z), cls='prop')   # a drawing with construction lines
def protractor(x, y, s, t, z, wp):
    """a big brass protractor standing on its foot: the half disc, degree ticks, a hairline arm"""
    u, v = s * 2 - 1, 1 - t
    d = math.hypot(u, v)
    if v < 0 or d > 1: return None
    a = math.atan2(v, u)
    if d > 0.86:
        if (a / math.pi * 36) % 1 < 0.35 and d < 0.95: return BRASS[1]
        return tone(BRASS, 4.6 - u * 1.2, x, y)
    if d < 0.14: return tone(BRASS, 3.6, x, y)
    if abs(a - 1.05) < 0.03: return BRASS[5]                                                     # the arm
    if d < 0.8: return None
    return tone(BRASS, 3.0, x, y)
rs.quad((13.0, yt + 0.6, 20.6), (15.8, yt + 0.6, 20.6), (13.0, yt + 2.0, 20.6), protractor, cls='prop', cut=True)
rs.line3((14.4, yt, 20.7), (14.4, yt + 0.6, 20.7), lambda x, y, s, t, z, wp: BRASS[2], w=0.18)
rs.quad((11.2, yt + 0.04, 20.0), (12.6, yt + 0.04, 20.0), (11.2, yt + 0.04, 21.0),
        lambda x, y, s, t, z, wp: fogged(tone(WALNUT, 4.4, x, y), z) if (s + t < 1.0 and s + t > 0.72) or s < 0.1 or t < 0.1 else None, cls='prop', cut=True)   # a set square
rs.line3((10.0, yt + 0.05, 20.7), (10.6, yt + 0.9, 20.8), lambda x, y, s, t, z, wp: (150, 150, 140), w=0.06)        # dividers
rs.line3((11.0, yt + 0.05, 20.7), (10.6, yt + 0.9, 20.8), lambda x, y, s, t, z, wp: (150, 150, 140), w=0.06)
rs.box(9.0, 9.9, yt, yt + 0.7, 20.6, 21.0, plain(BRASS, 2.4), plain(BRASS, 1.8), top=plain(BRASS, 3.4), cls='prop')  # a brass lantern
rs.box(9.1, 9.8, yt + 0.7, yt + 1.6, 20.65, 20.95, lambda x, y, s, t, z, wp: LANT[5] if 0.15 < s < 0.85 else BRASS[1], lambda x, y, s, t, z, wp: BRASS[1], cls='emit')
rs.disc(9.45, yt + 1.75, 20.6, 0.3, lambda x, y, s, t, z, wp: fogged(tone(BRASS, 3.0 - t, x, y), z))

# ---------------------------------------------------------------------------------------------------- lamps, corner ferns
def floor_lamp(X, Z, h):
    rs.box(X - 0.6, X + 0.6, 0, 0.4, Z - 0.6, Z + 0.6, plain(BRASS, 2.4), plain(BRASS, 1.8), top=plain(BRASS, 3.2), cls='prop')
    rs.line3((X, 0.4, Z), (X, h, Z), lambda x, y, s, t, z, wp: fogged(tone(BRASS, 3.0 - ((x + 0.5 - proj(*wp)[0]) * 0.8), x, y), z), w=0.2)
    rs.box(X - 0.55, X + 0.55, h, h + 1.2, Z - 0.55, Z + 0.55,
           lambda x, y, s, t, z, wp: LANT[5] if 0.15 < s < 0.85 and 0.1 < t < 0.9 else BRASS[1], lambda x, y, s, t, z, wp: LANT[3], cls='emit')
    rs.disc(X, h + 1.45, Z - 0.1, 0.42, lambda x, y, s, t, z, wp: fogged(tone(BRASS, 3.4 - t * 1.6, x, y), z))
for side in (-1, 1):
    floor_lamp(side * 16.2, 23.6, 7.0)                                                    # behind each desk's outer end
    floor_lamp(side * 12.0, 34.6, 6.2)                                                    # either side of the steps' foot
    planter(side * 20.5 - 1.6, side * 20.5 + 1.6, 9.8, 12.4, 1.1, 150 + side, ferns=2)

# ---------------------------------------------------------------------------------------------------- render
def P(X, Y, Z): x, y = proj(X, Y, Z); return [round(x), round(y)]
PTS['doorway'] = [P(-DOOR[3], DOOR[1], ZB), P(DOOR[3], DOOR[2], ZB)]
PTS['desk_left_front'] = [P(LD[0], 0, LD[2]), P(LD[1], 2.9, LD[2])]
PTS['desk_right_front'] = [P(RD[0], 0, RD[2]), P(RD[1], 2.9, RD[2])]
PTS['rose'] = P(ROSE[0], ROSE[1], ZB)
def mirror_floor(col, cls):
    """the polished floor mirrors the hall: march the ray from the eye mirrored under the floor up the pixel's column
    until it passes behind something that is not floor (raster3d's own reflect() stops on the floor itself here)"""
    out = {}
    for y in range(HY + 1, H):
        for x in range(W):
            g = rs.G[y][x]
            if g is None or g[5] != 'ground' or g[4] is None: continue
            k = floor_gloss(x, y, g[4])
            if k <= 0: continue
            Zg = g[4][2]; t = 1.0; step = max(0.012, 0.5 / Zg); hit = None
            while t < 6.0:
                t += step
                Z = Zg * t; Yw = CAMH * (t - 1)
                yy = int(HY + F * (CAMH - Yw) / Z)
                if yy < 0: break
                if yy >= y: continue
                h_ = rs.G[yy][x]
                if h_ is not None and h_[5] != 'ground' and rs.ZB[yy][x] <= Z + 0.6: hit = col[yy][x]; break
            if hit is not None: out[(x, y)] = (hit, k)
    for (x, y), (c, k) in out.items():
        b = col[y][x]
        col[y][x] = tuple(int(b[i] * (1 - k) + c[i] * k * 0.85) for i in range(3))
img = rs.render(INK, fog=fogk, post=mirror_floor, light_gain=0.8, grime_gain=1.2, bloom=0.4, stain_gain=0.8, damp_gain=0.3)
img.save(f'{OUT}/lumen_int.png')
json.dump(PTS, open(f'{OUT}/lumen_int_points.json', 'w'), indent=1)
print('done interior', PTS)
