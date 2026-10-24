"""Voxmarket -- the market that grew inside the old zeppelin hangar (the Riga-market hangars seen from the Crossroad).
1067x600, overcast day light through the glazing, same camera as the Crossroad (VP 533,296, F 300, eye 12 units).

  hall     the main aisle (VoxMarket): a barrel-vaulted hangar with riveted lattice trusses, a skylight band along the
           crown, catwalks, the radial-glazed gable at the far end, a patched old airship envelope hung under the roof,
           rows of stalls with striped awnings, string lights, a crowd; on the right the curtained way to the auction
           bay, on the left a cross-aisle spilling daylight from the hangar door
  alley    Zerren's lane (VoxmarketMarketScene): a narrow lane of crammed stalls under the side gallery's deck,
           pipes and cables, blade signs and paper lanterns, the bright main hall at the end; Zerren's ampule shelves on the left
  auction  the auction bay (VoxmarketHallScene): a hangar bay closed by violet velvet curtains, a raised stage with
           steps, the auctioneer's lectern, the lot pedestal, rows of chairs, a carpet runner, tall side windows

variants: base | growth (vines on the trusses, moss, flowers, plants behind the glass) | decay (rust, broken skylights
with light shafts, torn faded awnings, shuttered stalls, puddles, litter, smoke)

    python3 voxmarket_bg.py <outdir> <hall|alley|auction> [base|growth|decay]  ->  <scene>[_<variant>].png
"""
import sys, math, random
from PIL import Image
from pal_day import *
FONT['Y'] = ['101', '101', '010', '010', '010']

OUT, SCENE = sys.argv[1], sys.argv[2]
VARIANT = sys.argv[3] if len(sys.argv) > 3 else 'base'
GROWTH, DECAY = VARIANT == 'growth', VARIANT == 'decay'
W, H, CX, HY, F, CAMH = 1067, 600, 533, 296, 300.0, 12.0
INF = 9e9
nA, nB, nC, nF = make_noise(48, 1, W, H), make_noise(13, 2, W, H), make_noise(5, 3, W, H), make_noise(9, 7, W, H)

# ---------------------------------------------------------------------------------------------------- extra palette
def R(s): return ramp(s)
AWN = {
    'red': R('#2e0f0c #4a1912 #6a2418 #8c3322 #ab4a30 #c66a48'), 'ochre': R('#2e2008 #4a340e #6a4c16 #8c661e #ad8230 #c9a04c'),
    'teal': R('#0a2424 #10363a #184c50 #226468 #2f7e80 #4a9a96'), 'violet': R('#1e1028 #2e1a3c #422652 #58346a #704a84 #8c66a0'),
    'green': R('#122410 #1c3618 #284c22 #36642c #4a7e3a #66984e'), 'blue': R('#0e1630 #162246 #20325e #2c4478 #3e5a92 #5a78aa'),
}
CREAM = R('#3a3428 #554c3a #72684e #918566 #b0a482 #ccc2a2')
VELVET = R('#14081a #220e2a #34163e #481e54 #5e286c #763886 #8c4a9c')
BRICK = R('#1e100c #2e1810 #422216 #582e1c #6e3c26 #864e34')
RUSTR = R('#2a1208 #45200e #643014 #85441c #a05a28')
NEON = {'pink': ((255, 79, 168), (150, 40, 96), (70, 22, 50)), 'cyan': ((79, 232, 255), (40, 130, 150), (20, 60, 70)),
        'amber': ((255, 196, 90), (160, 104, 40), (70, 46, 20))}
GOODS = [RED[4], GLOW[2], FLOWER[0], FLOWER[1], FLOWER[2], LEAF[4], CAP[4], BONE[4], AWN['teal'][4], AWN['violet'][4], AWN['blue'][4],
         CREAM[5], WARM[4], STONE[7]]
COLS = list(AWN)

def ri(r, i): return r[max(0, min(len(r) - 1, int(i)))]
def tone(r, v, x, y): return ri(r, band(v, x, y))

# ---------------------------------------------------------------------------------------------------- the buffer
def proj(x, y, z): return (CX + F * x / z, HY + F * (CAMH - y) / z)
def ray(x, y): return ((x + 0.5 - CX) / F, -(y + 0.5 - HY) / F)
G = [[None] * W for _ in range(H)]
ZB = [[INF] * W for _ in range(H)]
SHAFT = [[0] * W for _ in range(H)]
OBJ = [0]
def new_obj():
    OBJ[0] += 1; return OBJ[0]

def put(x, y, z, shader, obj, a=0.0, b=0.0, wp=None):
    if 0 <= x < W and 0 <= y < H and z < ZB[y][x]:
        ZB[y][x] = z; G[y][x] = (shader, obj, a, b, wp)

def pip(pts, u, v):
    inside = False; n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        if (y0 > v) != (y1 > v) and u < x0 + (x1 - x0) * (v - y0) / (y1 - y0): inside = not inside
    return inside

def quad(P0, P1, P3, shader, obj=None, clip=None):
    """a planar parallelogram P0 + s*(P1-P0) + t*(P3-P0), s,t in 0..1, rasterised with per-pixel depth.
    shader(x, y, s, t, z, wp) -> colour (or None = transparent)"""
    obj = obj or new_obj()
    P2 = (P1[0] + P3[0] - P0[0], P1[1] + P3[1] - P0[1], P1[2] + P3[2] - P0[2])
    pts3 = (P0, P1, P2, P3)
    if min(p[2] for p in pts3) <= 0.5: return obj
    sp = [proj(*p) for p in pts3]
    e1 = (P1[0] - P0[0], P1[1] - P0[1], P1[2] - P0[2]); e2 = (P3[0] - P0[0], P3[1] - P0[1], P3[2] - P0[2])
    n = (e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0])
    x0, x1 = max(0, int(min(p[0] for p in sp))), min(W - 1, int(max(p[0] for p in sp)) + 1)
    y0, y1 = max(0, int(min(p[1] for p in sp))), min(H - 1, int(max(p[1] for p in sp)) + 1)
    # solve for s, t with the two largest-magnitude axes of the plane
    ax = sorted(range(3), key=lambda i: abs(n[i]))[:2]
    det = e1[ax[0]] * e2[ax[1]] - e1[ax[1]] * e2[ax[0]] or 1e-9
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if not pip(sp, x + 0.5, y + 0.5): continue
            dx, dy = ray(x, y)
            den = n[0] * dx + n[1] * dy + n[2]
            if abs(den) < 1e-9: continue
            t_ = (n[0] * P0[0] + n[1] * (P0[1] - CAMH) + n[2] * P0[2]) / den
            if t_ <= 0: continue
            wp = (dx * t_, CAMH + dy * t_, t_)
            if t_ >= ZB[y][x]: continue
            q = (wp[0] - P0[0], wp[1] - P0[1], wp[2] - P0[2])
            s = (q[ax[0]] * e2[ax[1]] - q[ax[1]] * e2[ax[0]]) / det
            t = (e1[ax[0]] * q[ax[1]] - e1[ax[1]] * q[ax[0]]) / det
            if clip and not clip(s, t): continue
            put(x, y, t_, shader, obj, s, t, wp)
    return obj

def box(x0, x1, y0, y1, z0, z1, sh_front, sh_side, sh_top=None, obj=None):
    """an axis-aligned box: the face towards the camera (z0), the side facing the aisle and the top"""
    obj = obj or new_obj()
    quad((x0, y0, z0), (x1, y0, z0), (x0, y1, z0), sh_front, obj)
    if x1 < 0: quad((x1, y0, z0), (x1, y0, z1), (x1, y1, z0), sh_side, obj)        # left of the camera: its right side shows
    elif x0 > 0: quad((x0, y0, z0), (x0, y0, z1), (x0, y1, z0), sh_side, obj)
    if sh_top and y1 < CAMH: quad((x0, y1, z0), (x1, y1, z0), (x0, y1, z1), sh_top, obj)
    return obj

def disc(cx, cy, z, r, shader, obj=None):
    obj = obj or new_obj()
    (sx, sy) = proj(cx, cy, z); rr = max(0.6, r * F / z)
    for y in range(int(sy - rr) - 1, int(sy + rr) + 2):
        for x in range(int(sx - rr) - 1, int(sx + rr) + 2):
            d = math.hypot(x + 0.5 - sx, y + 0.5 - sy) / rr
            if d <= 1: put(x, y, z, shader, obj, (x + 0.5 - sx) / rr, (y + 0.5 - sy) / rr)
    return obj

def line3(P0, P1, shader, w=1.0, sag=0.0, n=0):
    obj = new_obj(); n = n or int(math.dist(proj(*P0), proj(*P1))) + 2
    for i in range(n + 1):
        t = i / n
        P = (P0[0] + (P1[0] - P0[0]) * t, P0[1] + (P1[1] - P0[1]) * t - sag * math.sin(math.pi * t), P0[2] + (P1[2] - P0[2]) * t)
        if P[2] <= 0.5: continue
        (sx, sy) = proj(*P); rr = max(0.5, w * F / P[2] / 2)
        for y in range(int(sy - rr), int(sy + rr) + 1):
            for x in range(int(sx - rr), int(sx + rr) + 1):
                put(x, y, P[2] - 0.01, shader, obj, t, 0)
    return obj

# ---------------------------------------------------------------------------------------------------- light
def fog_of(z, k=70.0): return max(0.0, min(0.72, 1 - math.exp(-(z - 16) / k)))
def lam(n):
    """overcast light from the glazing above, a little from the far end"""
    L = (0.12, 0.92, -0.37)
    return max(0.0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2])

# ---------------------------------------------------------------------------------------------------- the hangar shell (ray-cast)
class Shell:
    def __init__(s, wall_x, spring, zend, rib_z0, rib_dz, deck=None, glaze=True):
        s.wx, s.sp, s.zend, s.R = wall_x, spring, zend, wall_x
        s.ribs = [rib_z0 + k * rib_dz for k in range(int((zend - rib_z0) / rib_dz) + 1)]
        s.deck, s.glaze = deck, glaze
        s.obj = {k: new_obj() for k in ('floor', 'wall', 'vault', 'end', 'rib', 'deck')}

    def cast(s):
        for y in range(H):
            for x in range(W):
                dx, dy = ray(x, y)
                best = (INF, None, None)
                if dy < 0:                                                             # floor
                    t = -CAMH / dy; X = dx * t
                    if abs(X) <= s.wx and t <= s.zend: best = (t, 'floor', (X, 0.0, t))
                if dx != 0:                                                            # side walls
                    t = s.wx / abs(dx); Y = CAMH + dy * t
                    if 0 <= Y <= s.sp and t <= s.zend and t < best[0]: best = (t, 'wall', (math.copysign(s.wx, dx), Y, t))
                if s.deck is not None and dy > 0:                                      # a flat deck overhead (the alley)
                    t = (s.deck - CAMH) / dy; X = dx * t
                    if abs(X) <= s.wx and t <= s.zend and t < best[0]: best = (t, 'deck', (X, s.deck, t))
                elif s.deck is None:                                                   # the barrel vault
                    a = dx * dx + dy * dy; b = 2 * dy * (CAMH - s.sp); c = (CAMH - s.sp) ** 2 - s.R ** 2
                    disc_ = b * b - 4 * a * c
                    if a > 0 and disc_ >= 0:
                        t = (-b + math.sqrt(disc_)) / (2 * a); Y = CAMH + dy * t
                        if Y >= s.sp and t <= s.zend and t < best[0]: best = (t, 'vault', (dx * t, Y, t))
                if best[0] > s.zend - 0.01:                                            # the gable / end wall
                    X, Y = dx * s.zend, CAMH + dy * s.zend
                    inside = (abs(X) <= s.wx and 0 <= Y <= s.sp) or (Y > s.sp and X * X + (Y - s.sp) ** 2 <= s.R ** 2) or \
                             (s.deck is not None and abs(X) <= s.wx and 0 <= Y <= s.deck)
                    if inside: best = (s.zend, 'end', (X, Y, s.zend))
                for zr in s.ribs:                                                      # lattice trusses in front
                    if zr >= best[0] or zr < 2: continue
                    X, Y = dx * zr, CAMH + dy * zr
                    if s.deck is None and Y >= s.sp:
                        r = math.hypot(X, Y - s.sp)
                        if s.R - 1.7 <= r <= s.R and s.lattice(math.atan2(Y - s.sp, X) * s.R, s.R - r):
                            best = (zr, 'rib', (X, Y, zr)); break
                    elif s.deck is not None and s.deck - 1.4 <= Y <= s.deck and abs(X) <= s.wx:
                        if s.lattice(X, s.deck - Y, depth=1.4): best = (zr, 'rib', (X, Y, zr)); break
                    if 0 <= Y < (s.sp if s.deck is None else s.deck) and s.wx - 1.3 <= abs(X) <= s.wx:
                        best = (zr, 'column', (X, Y, zr)); break
                if best[1]:
                    t, k, wp = best
                    put(x, y, t, SHELL_SHADERS[k], s.obj.get(k, 1), 0, 0, wp)

    @staticmethod
    def lattice(arc, depth_in, depth=1.7):
        """riveted lattice girder: two chords and zig-zag diagonals"""
        if depth_in < 0.28 or depth_in > depth - 0.28: return True
        ph = (arc / 1.5) % 2.0; d = depth_in / depth
        return abs((ph if ph < 1 else 2 - ph) - d) < 0.16

def shell_floor(x, y, s, t, z, wp):
    X, _, Z = wp
    v = 2.5 + 0.9 * max(0.0, 1 - abs(X) / 10) + (nC(x, y) - 0.5) * 0.7 + (nA(x * 0.7, y * 2.0) - 0.5) * 1.0
    jz = max(0.08, 1.1 * Z * Z / (F * CAMH)); jx = max(0.07, 1.1 * Z / F)
    if (Z / 6.0) % 1 < jz / 6.0 or ((X + 30) / 6.0) % 1 < jx / 6.0: v -= 1.2
    if SCENE == 'hall':
        for rx in (-3.5, 3.5):                                                        # the old airship ground rails
            if abs(X - rx) < 0.22: return fogged(METAL[6] if abs(X - rx) < 0.1 else METAL[3], fog_of(Z), x, y)
        if abs(abs(X) - 6.6) < 0.2 and (Z % 4) < 2.6: return fogged(GLOW[0] if not DECAY else WARM[2], fog_of(Z), x, y)   # faded lane paint
    elif SCENE == 'alley' and nF(X * 3 + 50, Z * 3) > 0.72: v += 0.9                  # straw and sawdust in the lane
    if nF(X * 4 + 13, Z * 1.3) > 0.8: v -= 1.0                                       # oil stains
    if DECAY and nB(X * 9, Z * 2.5) > 0.74:                                          # puddles under the broken glazing
        return fogged(SKY[4] if (x + y) % 2 else STONE[2], fog_of(Z), x, y)
    if GROWTH and ((Z / 6.0) % 1 < jz / 6.0 * 1.5 or ((X + 30) / 6.0) % 1 < jx / 6.0 * 1.5) and nC(x * 0.6, y * 0.6) > 0.55:
        return fogged(LEAF[2] if (x + y) % 2 else LEAF[3], fog_of(Z), x, y)
    v += 1.4 * SHAFT[y][x] * 0.5
    v += LAMPS.glow(X, 0.0, Z) * 2.0 + DAYLIGHT(X, Z)
    c = ri(WARM, band(v - 0.6, x, y)) if LAMPS.glow(X, 0.0, Z) > 0.45 else tone(STONE, v, x, y)
    return fogged(c, fog_of(Z), x, y)

def shell_wall(x, y, s, t, z, wp):
    X, Y, Z = wp
    side = -1 if X < 0 else 1
    if Y < 7.2:                                                                       # brick plinth wall
        course = math.floor(Y / 0.42); bu = Z / 1.1 + (0.5 if course % 2 else 0)
        v = 2.8 + (nA(x, y) - 0.5) * 1.0 - (1.3 if (Y / 0.42) % 1 < 0.2 * Z / 30 or bu % 1 < 0.1 * Z / 30 else 0)
        if Y > 6.7: v += 1.0
        c = tone(BRICK, v, x, y)
        if GROWTH and nC(x, y) > 0.62: c = LEAF[1 + (x + y) % 2]
        return fogged(c, fog_of(Z), x, y)
    # tall industrial steel windows between the columns: small panes, a few opened, overcast light behind
    pu, pv = (Z % SHELL.ribdz) / SHELL.ribdz, (Y - 7.2)
    frame = (Z * 1.0) % 1.6 < 0.16 * Z / 25 or pv % 1.4 < 0.14 * Z / 25 or pv < 0.4
    if frame: c = METAL[1] if not DECAY else RUSTR[1]
    else:
        v = 3.4 + pv * 0.18 + (nB(x, y) - 0.5) * 0.8
        c = tone(SKY, v, x, y)
        if h32(int(Z / 1.6), int(pv / 1.4), side) % 11 == 0: c = STONE[2]
        if GROWTH and pv < 3.6 and nF(Z * 1.1, Y * 1.4) > 0.5: c = LEAF[2 + h32(x, y) % 2]   # shrubs outside pressing on the glass
        if DECAY: c = ri(SKY, max(0, SKY.index(c) - 2)) if c in SKY else c
        if DECAY and h32(int(Z / 1.6), int(pv / 1.4), side + 5) % 5 == 0: c = STONE[0] if (x + y) % 3 else SKY[6]
    return fogged(c, fog_of(Z, 120), x, y)

def shell_vault(x, y, s, t, z, wp):
    X, Y, Z = wp
    ang = math.atan2(Y - SHELL.sp, X)                                                 # pi/2 at the crown
    crown = abs(ang - math.pi / 2)
    arc = ang * SHELL.R
    if crown < 0.32 and SHELL.glaze:                                                  # the skylight band
        mull = (Z % 1.8) < 0.18 * Z / 20 or (arc % 1.6) < 0.16 * Z / 20
        if mull: c = METAL[2]
        else:
            c = tone(SKY, 5.8 + (nB(x, y) - 0.5) * 0.8, x, y)
            if GROWTH and nF(Z * 0.7, arc * 0.7) > 0.58: c = LEAF[2 + h32(x, y) % 3]          # plants over the glass
            if DECAY and h32(int(Z / 1.8), int(arc / 1.6), 3) % 4 == 0: c = SKY[7] if (x + y) % 2 else STONE[1]
        return fogged(c, fog_of(Z, 120), x, y)
    # corrugated roof sheeting between purlins, darker towards the springing
    v = 0.7 + 1.5 * (1 - crown / 1.5) + (0.5 if int(arc * 3.0) % 2 else 0) + (nA(x, y) - 0.5) * 0.8 - (0.5 if DECAY else 0)
    if (arc % 4.0) < 0.35: v -= 1.4                                                    # purlins
    c = tone(METAL, v, x, y)
    below = (arc % 4.0) if X < 0 else (4.0 - arc % 4.0)                               # distance down-slope from the purlin above
    if DECAY and nF(Z * 3.2 + 7, arc * 0.3) > 0.6 and below < 2.6 * nF(Z * 1.7, arc * 0.5) + 0.4:
        if below < 0.9 or (x + y) % 2: c = tone(RUSTR, v + 0.1 - below * 0.35, x, y)      # rust bleeding from the purlins
    if GROWTH and crown > 0.9 and nF(Z * 0.9, arc * 0.9) > 0.5 and nF(Z * 3.1, arc * 3.1) > 0.3:
        c = tone(LEAF, 0.8 + v * 0.7 + (nB(x * 2, y * 2) - 0.5) * 1.8, x, y)               # moss creeping up from the springing
    return fogged(c, fog_of(Z, 120), x, y)

def shell_rib(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 2.2 + (nB(x, y) - 0.5) * 0.8 + 0.5 * (Y > 30)
    c = tone(METAL, v, x, y)
    if h32(x, y, 3) % 23 == 0: c = METAL[6]                                            # rivets
    if DECAY and nF(X * 1.4 + Z, Y * 0.6) > 0.55: c = tone(RUSTR, v, x, y)
    if GROWTH and nF(X * 0.8 + Z, Y * 0.8) > 0.62: c = LEAF[1 + (x + y) % 3]
    return fogged(c, fog_of(Z), x, y)

def shell_column(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 2.6 + (0.8 if abs(abs(X) - SHELL.wx + 0.9) < 0.3 else 0) + (nB(x, y) - 0.5) * 0.6
    c = tone(METAL, v, x, y)
    if DECAY and nF(Z * 2.0, Y * 0.4) > 0.55: c = tone(RUSTR, v, x, y)
    if GROWTH and nF(Z * 2.0 + 5, Y * 0.25) > 0.45 - Y * 0.012: c = LEAF[1 + (x + y) % 3]     # ivy up the columns
    return fogged(c, fog_of(Z), x, y)

def shell_end(x, y, s, t, z, wp):
    X, Y, Z = wp
    if SHELL.deck is not None:                                                         # the alley opens onto the bright main hall
        v = 4.6 + (nB(x, y) - 0.5) * 0.8 - (1.4 if Y < 3 else 0)
        return fogged(tone(HAZE, v, x, y), 0.55, x, y)
    if Y > SHELL.sp - 0.5:                                                             # the radial-glazed arch
        r = math.hypot(X, Y - SHELL.sp); a = math.atan2(Y - SHELL.sp, X)
        mull = (a * 16 / math.pi) % 1 < 0.08 * 20 / max(4, r) or r % 4.0 < 0.3 or r > SHELL.R - 0.8
        c = METAL[2] if mull else tone(SKY, 5.6 - r * 0.06, x, y)
        return fogged(c, 0.45, x, y)
    if abs(X) < 9 and Y < 13:                                                          # the great sliding doors
        c = tone(METAL, 2.4 + (0.6 if (X % 1.2) < 0.15 else 0) + (nB(x, y) - 0.5) * 0.6, x, y)
        if abs(X) < 0.15: c = METAL[0]
        return fogged(c, 0.4, x, y)
    v = 3.0 + (nA(x, y) - 0.5) * 0.8
    return fogged(tone(BRICK, v, x, y), 0.45, x, y)

def shell_deck(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 1.2 + (0.6 if (X % 1.0) < 0.5 else 0) + (nB(x, y) - 0.5) * 0.6               # planked underside of the gallery
    if (Z % 5.0) < 0.6: v -= 1.0
    c = tone(WOOD, v, x, y)
    if DECAY and nF(X * 1.5 + 9, Z * 0.8) > 0.62: c = WOOD[0] if (x + y) % 3 else STONE[0]          # rotten, missing boards
    if GROWTH and nF(X * 0.9, Z * 0.9) > 0.55 and nF(X * 3, Z * 3) > 0.35:
        c = tone(LEAF, 1.0 + (nB(x * 2, y * 2) - 0.5) * 2.0, x, y)                                     # moss on the deck
    return fogged(c, fog_of(Z), x, y)

SHELL_SHADERS = {'floor': shell_floor, 'wall': shell_wall, 'vault': shell_vault, 'rib': shell_rib, 'column': shell_column,
                 'end': shell_end, 'deck': shell_deck}

# ---------------------------------------------------------------------------------------------------- lamps (warm pools)
class Lamps:
    def __init__(s): s.pts = []
    def add(s, X, Y, Z, r=4.0): s.pts.append((X, Y, Z, r))
    def glow(s, X, Y, Z):
        g = 0.0
        for (lx, ly, lz, r) in s.pts:
            d = math.sqrt((X - lx) ** 2 + (Y - ly) ** 2 * 0.25 + (Z - lz) ** 2)
            if d < r: g += (1 - d / r) ** 1.5
        return min(1.0, g)
LAMPS = Lamps()
DAY = []
def DAYLIGHT(X, Z):
    g = 0.0
    for (dx, dz, r) in DAY:
        d = math.hypot(X - dx, (Z - dz) * 1.4)
        if d < r: g += 1.6 * (1 - d / r)
    return g

def bulb(X, Y, Z, col=None):
    LAMPS.add(X, Y - 3, Z, 5.0)
    c = col or GLOW[4]
    disc(X, Y, Z, 0.32, lambda x, y, s, t, z, wp: c if s * s + t * t < 0.45 else GLOW[2])

# ---------------------------------------------------------------------------------------------------- stalls
def awning_shader(col, obj_seed, torn=False):
    r = AWN[col]
    def sh(x, y, s, t, z, wp):
        stripe = int(t * 7) % 2 == 0
        if torn and nF(x * 2.2 + obj_seed, y * 1.6) > 0.62: return None
        v = 3.2 + 1.2 * s + (nB(x, y) - 0.5) * 0.6
        if s > 0.93: v -= 1.2                                                           # the hem
        c = tone(r, v - (1.4 if DECAY else 0), x, y) if stripe else tone(CREAM, v - (1.6 if DECAY else 0.4), x, y)
        return fogged(c, fog_of(z) * 0.9, x, y)
    return sh

def plain(r, v0, tex=0.6, k=0.9):
    def sh(x, y, s, t, z, wp): return fogged(tone(r, v0 + (nB(x, y) - 0.5) * tex, x, y), fog_of(z) * k, x, y)
    return sh

def goods_shader(seed, dens=0.55, rows=3):
    def sh(x, y, s, t, z, wp):
        cell = (int(s * 9), int(t * rows))
        h = h32(cell[0], cell[1], seed)
        if h % 100 < dens * 100 and (t * rows) % 1 > 0.2:
            c = GOODS[h % len(GOODS)]
            if (x + y) % 5 == 0: c = STONE[7]
            return fogged(c, fog_of(z) * 0.85, x, y)
        return fogged(WOOD[1] if (t * rows) % 1 <= 0.2 else WOOD[0], fog_of(z) * 0.85, x, y)
    return sh

def sign_shader(seed, neon=None, glyphs=True):
    def sh(x, y, s, t, z, wp):
        if neon:
            on = h32(int(s * 14), int(t * 4), seed) % 3 != 0 and 0.15 < t < 0.85 and 0.08 < s < 0.92
            return NEON[neon][0] if on and (x + y) % 3 else NEON[neon][2]
        if glyphs and 0.15 < t < 0.85 and 0.1 < s < 0.9 and h32(int(s * 10), int(t * 3), seed) % 3 == 0: return CREAM[5]
        return fogged(tone(WOOD, 2.6 + (nB(x, y) - 0.5), x, y), fog_of(z), x, y)
    return sh

def stall(side, xin, depth, z0, z1, col, seed, shut=False, torn=False, sign=None):
    """a market stall against the aisle. side -1 = left of the aisle (its counter faces +x)"""
    xo = xin + side * depth
    xl, xr = min(xin, xo), max(xin, xo)
    face = xr if side < 0 else xl                                                       # the counter's front plane
    back = xl if side < 0 else xr
    wood = plain(WOOD, 2.6)
    paint = plain(AWN[col], 2.2 - (1.0 if DECAY else 0))
    if not shut:
        quad((back, 0, z0), (back, 0, z1), (back, 8.4, z0), goods_shader(seed, 0.5, 4))          # shelves at the back
        quad((face, 0, z0), (face, 0, z1), (face, 3.4, z0), paint)                                 # counter front
        quad((face - side * 2.2, 3.4, z0), (face - side * 2.2, 3.4, z1), (face, 3.4, z0), goods_shader(seed + 7, 0.7, 2))  # counter top
    else:                                                                                           # shuttered with planks
        quad((face, 0, z0), (face, 0, z1), (face, 8.2, z0), lambda x, y, s, t, z, wp: fogged(tone(WOOD, 2.0 + (0.8 if int(t * 9) % 2 else 0) + (nB(x, y) - 0.5), x, y), fog_of(z), x, y))
    if not shut: quad((xl, 0, z0), (xr, 0, z0), (xl, 3.4, z0), plain(WOOD, 2.0))                  # the counter's end
    else: quad((xl, 0, z0), (xr, 0, z0), (xl, 8.6, z0), plain(WOOD, 1.6))
    for zz in (z0, z1):                                                                             # corner posts
        quad((face - 0.25, 0, zz), (face + 0.25, 0, zz), (face - 0.25, 9.0, zz), plain(WOOD, 3.0))
        quad((back - 0.25, 0, zz), (back + 0.25, 0, zz), (back - 0.25, 9.6, zz), plain(WOOD, 2.4))
    if not shut:                                                                                    # a drape tied back at the open end
        quad((back, 4.4, z0 + 0.05), (back + side * -2.6, 4.4, z0 + 0.05), (back, 9.4, z0 + 0.05),
             lambda x, y, s, t, z, wp, c=col: fogged(tone(AWN[c], 2.6 + math.sin(s * 18) * 0.9 - (1.2 if DECAY else 0), x, y), fog_of(z), x, y) if s < 0.55 + 0.45 * t else None)
    # the awning, sloping down over the aisle; scalloped valance
    lo = face + side * -2.4
    torn_ = torn or (DECAY and h32(seed, 9) % 2 == 0)
    quad((back, 9.6, z0), (back, 9.6, z1), (lo, 7.6, z0), awning_shader(col, seed, torn_))
    for k in range(int((z1 - z0) / 1.2)):
        zc = z0 + 0.6 + k * 1.2
        disc(lo, 7.6, zc, 0.55, lambda x, y, s, t, z, wp, c=col: fogged(tone(AWN[c], 2.4 - (1.2 if DECAY else 0), x, y), fog_of(z), x, y) if t > -0.1 else None)
    if not shut:
        bulb(face - side * 1.2, 7.0, (z0 + z1) / 2)
        for k in range(3):                                                                         # bundles hanging from the awning
            zc = z0 + (k + 0.6) * (z1 - z0) / 3.3
            if h32(seed, k) % 2: line3((lo + side * 0.2, 7.6, zc), (lo + side * 0.2, 5.6 - (h32(seed, k, 2) % 3) * 0.5, zc), lambda x, y, s, t, z, wp, kk=k: fogged(GOODS[h32(seed, kk) % len(GOODS)], fog_of(z), x, y), w=0.55)
    if sign:
        quad((face - side * 0.1, 10.0, z0 + 0.6), (face - side * 0.1, 10.0, z1 - 0.6), (face - side * 0.1, 12.2, z0 + 0.6), sign)
    if GROWTH:
        for k in range(2):                                                                         # flower pots on the counter
            zc = z0 + 1.0 + k * (z1 - z0 - 2.0)
            disc(face - side * 0.6, 4.0, zc, 0.75, lambda x, y, s, t, z, wp: fogged(FLOWER[h32(x, y) % 5] if h32(x, y, 3) % 3 == 0 else LEAF[2 + (x + y) % 3], fog_of(z), x, y))

# ---------------------------------------------------------------------------------------------------- people (billboards)
def person(X, Z, seed, height=6.2, seated=False):
    r = random.Random(seed)
    kind = r.choice(('hood', 'hat', 'bare', 'hood', 'cap'))
    coat = r.choice((STONE[1], STONE[2], WOOD[1], WARM[2], AWN['violet'][2], AWN['teal'][2], AWN['red'][2], METAL[2], AWN['ochre'][2], AWN['blue'][2], AWN['green'][2]))
    accent = r.choice((AWN['red'][3], AWN['ochre'][4], CREAM[4], AWN['teal'][4], FLOWER[0], GLOW[2]))
    h = height * r.uniform(0.86, 1.08) * (0.72 if seated else 1.0)
    bag = r.choice((0, 0, 1, -1))
    obj = new_obj()
    def sh(x, y, s, t, z, wp):
        # s 0..1 across (-1..1 body width units), t 0..1 up
        u = (s - 0.5) * 2
        if t > 0.86:                                                                     # head
            if (u / 0.36) ** 2 + ((t - 0.925) / 0.075) ** 2 > 1:
                if kind == 'hat' and 0.9 < t < 0.95 and abs(u) < 0.6: return fogged(STONE[0], fog_of(z), x, y)
                return None
            c = coat if kind == 'hood' else (BONE[2] if kind == 'bare' else STONE[0] if kind == 'hat' else accent)
            return fogged(c, fog_of(z), x, y)
        if t > 0.80:
            if abs(u) > 0.62: return None
            return fogged(accent if kind != 'hood' else coat, fog_of(z), x, y)               # scarf
        if t > 0.36:
            w = 0.5 + (0.8 - t) * 0.35 * (1.3 if kind == 'hood' else 1) - (0.12 if t > 0.74 else 0)
            if abs(u) > w: return None
            c = coat if abs(u) < w - 0.14 else STONE[0]
            if bag and 0.4 < t < 0.55 and u * bag > 0.2: c = accent                     # a basket / bag on the hip
            return fogged(c, fog_of(z), x, y)
        if seated: return None
        if abs(u) > 0.5 or (abs(u) < 0.08 and t < 0.32): return None                     # legs
        return fogged(STONE[0] if (x + y) % 3 else STONE[1], fog_of(z), x, y)
    quad((X - 1.2, 0, Z), (X + 1.2, 0, Z), (X - 1.2, h, Z), sh, obj)

def crowd(xs, zs, n, seed, avoid=lambda X, Z: False):
    r = random.Random(seed); placed = 0; tries = 0
    while placed < n and tries < n * 20:
        tries += 1
        X, Z = r.uniform(*xs), r.uniform(*zs)
        if avoid(X, Z): continue
        person(X, Z, r.randint(0, 99999)); placed += 1

# ---------------------------------------------------------------------------------------------------- the airship envelope
def envelope(cx, cy, cz, rx, ry, rz):
    obj = new_obj()
    for y in range(H):
        for x in range(W):
            dx, dy = ray(x, y)
            # ray-ellipsoid
            ox, oy, oz = -cx, CAMH - cy, -cz
            a = (dx / rx) ** 2 + (dy / ry) ** 2 + (1 / rz) ** 2
            b = 2 * (ox * dx / rx ** 2 + oy * dy / ry ** 2 + oz / rz ** 2)
            c = (ox / rx) ** 2 + (oy / ry) ** 2 + (oz / rz) ** 2 - 1
            d = b * b - 4 * a * c
            if d < 0: continue
            t = (-b - math.sqrt(d)) / (2 * a)
            if t <= 0 or t >= ZB[y][x]: continue
            wp = (dx * t, CAMH + dy * t, t)
            if DECAY and nF(x * 1.4, y * 1.4) > 0.66 and wp[1] < cy: continue               # torn, hanging in strips
            put(x, y, t, envelope_shader(cx, cy, cz, rx, ry, rz), obj, 0, 0, wp)
def envelope_shader(cx, cy, cz, rx, ry, rz):
    PATCH = [CAP[2], CAP[3], BONE[2], AWN['red'][2], AWN['ochre'][2], CREAM[3], AWN['teal'][2]]
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        n = ((X - cx) / rx ** 2, (Y - cy) / ry ** 2, (Z - cz) / rz ** 2); l = math.sqrt(sum(c * c for c in n)); n = tuple(c / l for c in n)
        v = 1.4 + 3.6 * lam(n)
        gore = int((math.atan2(Y - cy, X - cx) + math.pi) / (2 * math.pi) * 12); ring = int((Z - cz + rz) / 6)
        r_ = CAP if h32(gore, ring) % 4 else CREAM
        if h32(gore, ring, 5) % 7 == 0: c = tone(AWN[COLS[h32(gore, ring) % len(COLS)]], v - 0.6, x, y)
        else: c = tone(r_, v, x, y)
        if (Z - cz + rz) % 6 < 0.25 or ((math.atan2(Y - cy, X - cx) + math.pi) / (2 * math.pi) * 12) % 1 < 0.04: c = WOOD[1]   # seams
        if GROWTH and nF(x * 0.9, y * 0.9) > 0.58: c = LEAF[1 + (x + y) % 3]
        return fogged(c, fog_of(Z, 120), x, y)
    return sh

# ---------------------------------------------------------------------------------------------------- shafts of light
def shaft(X0, Z0, X1, Z1, top, w=2.0):
    """a dusty beam from a skylight at height top down to the floor between (X0,Z0) and (X1,Z1)"""
    for k in range(4):
        pts = [proj(X0 - w, top, Z0), proj(X0 + w, top, Z0), proj(X1 + w * 1.6, 0, Z1), proj(X1 - w * 1.6, 0, Z1)]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        for y in range(max(0, int(min(ys))), min(H, int(max(ys)) + 1)):
            for x in range(max(0, int(min(xs))), min(W, int(max(xs)) + 1)):
                if pip(pts, x + 0.5, y + 0.5) and (x + y + k) % 2 == 0: SHAFT[y][x] = min(2, SHAFT[y][x] + 1)
        w *= 0.7

# ==================================================================================================== scenes
SHELL = None
def scene_hall():
    global SHELL
    SHELL = Shell(32, 15, 150, 10, 12); SHELL.ribdz = 12
    # stalls along the central aisle (|x| 7..15), gaps for cross aisles; the near right holds the way to the auction
    for side in (-1, 1):
        z = 17.0 if side < 0 else 30.0                     # on the right a cross-aisle leads to the auction portal
        k = 0
        while z < 118:
            ln = 9.0 + (h32(side, k) % 3) * 1.5
            col = COLS[h32(side, k, 3) % len(COLS)]
            shut = DECAY and h32(side, k, 4) % 4 == 0
            stall(side, 7.0 * side, 8.0, z, z + ln, col, side * 100 + k, shut=shut,
                  sign=sign_shader(side * 10 + k) if h32(side, k, 5) % 2 else None)
            z += ln + (4.0 if k % 3 == 2 else 1.2); k += 1
    # outer rows against the walls
    for side in (-1, 1):
        z = 20.0 if side < 0 else 33.0
        while z < 110:
            stall(side, side * 23.5, 8.0, z, z + 10, COLS[h32(side, int(z)) % len(COLS)], int(z) + side * 7,
                  shut=DECAY and h32(side, int(z), 2) % 3 == 0)
            z += 12
    # the way to the auction bay: an arched portal in the hangar's right wall, at the end of a carpeted cross-aisle
    auction_portal(31.85, 25.0)
    # catwalks along both walls with railings
    for side in (-1, 1):
        xw = side * 32; xi = side * 28.8
        quad((xi, 15.0, 4), (xi, 15.0, 145), (xw, 15.0, 4), plain(METAL, 1.6, 0.4))
        line3((xi, 17.6, 6), (xi, 17.6, 145), lambda x, y, s, t, z, wp: fogged(METAL[3], fog_of(z), x, y), w=0.18)
        for zz in range(6, 145, 3): line3((xi, 15.0, zz), (xi, 17.6, zz), lambda x, y, s, t, z, wp: fogged(METAL[2], fog_of(z), x, y), w=0.14)
    # string lights across the aisle
    for zz in (24, 38, 54, 72, 92):
        line3((-7, 11.5, zz), (7, 11.5, zz), lambda x, y, s, t, z, wp: fogged(STONE[0], fog_of(z), x, y), w=0.1, sag=1.4)
        for k in range(9):
            u = -6.3 + k * 1.58; sag = 1.4 * math.sin(math.pi * (u + 7) / 14)
            if not (DECAY and h32(zz, k) % 3 == 0):
                disc(u, 11.2 - sag, zz, 0.22, lambda x, y, s, t, z, wp, kk=k: [GLOW[4], FLOWER[0], AWN['teal'][5], FLOWER[2]][kk % 4])
    # the old airship envelope, patched, hung under the vault in the far half
    for zz in (46, 62, 78, 94):
        for sx in (-1, 1):
            line3((-13 + sx * 4.0, 31.5, zz), (-13 + sx * 6.0, 44.0, zz), lambda x, y, s, t, z, wp: fogged(STONE[1], fog_of(z), x, y), w=0.12)
    envelope(-13.0, 28.5, 72.0, 6.2, 5.0, 30.0)
    for i, zz in enumerate(SHELL.ribs[1:9]):
        for side in (-1, 1):
            if (i + side) % 3 == 0: continue
            x0 = side * (9.5 + (i % 2) * 2.0)
            ytop = 15 + math.sqrt(max(0.0, 32 ** 2 - x0 ** 2)) - 2.0
            col = COLS[h32(i, side, 7) % len(COLS)]
            torn = DECAY and h32(i, side) % 2 == 0
            quad((x0, ytop, zz - 0.3), (x0 + 2.0, ytop, zz - 0.3), (x0, ytop - 9.0, zz - 0.3), banner(col, i * 7 + side, torn))
    for zz in (30, 46, 64, 84):
        pts = [(-7 + k * 1.4, 0, zz) for k in range(11)]
        line3((-7, 13.8, zz + 1), (7, 13.8, zz + 1), lambda x, y, s, t, z, wp: fogged(STONE[0], fog_of(z), x, y), w=0.08, sag=1.0)
        for k in range(10):
            u = -6.3 + k * 1.4; sag = 1.0 * math.sin(math.pi * (u + 7) / 14)
            if DECAY and h32(zz, k, 4) % 3 == 0: continue
            col = COLS[(k + zz) % len(COLS)]
            quad((u - 0.5, 13.8 - sag, zz + 1), (u + 0.5, 13.8 - sag, zz + 1), (u - 0.5, 12.4 - sag, zz + 1),
                 lambda x, y, s, t, z, wp, c=col: fogged(AWN[c][4], fog_of(z), x, y) if abs(s - 0.5) < 0.5 * (1 - t) else None)
    for zz in SHELL.ribs[1:9]:
        for xx in (-4.5, 4.5):
            line3((xx, 44.0, zz), (xx, 21.0, zz), lambda x, y, s, t, z, wp: fogged(STONE[0], fog_of(z), x, y), w=0.08)
            quad((xx - 1.3, 20.2, zz), (xx + 1.3, 20.2, zz), (xx - 0.4, 21.2, zz),
                 lambda x, y, s, t, z, wp: fogged(tone(AWN['green'], 2.6 + s, x, y), fog_of(z), x, y) if abs(s - 0.5) < 0.17 + 0.33 * (1 - t) else None)
            if not (DECAY and h32(int(zz), int(xx)) % 2): bulb(xx, 19.9, zz)
    if GROWTH:
        for zr in SHELL.ribs[1:10]:
            for k in range(7):
                a = math.radians(30 + k * 20 + (h32(int(zr), k) % 9))
                X0, Y0 = math.cos(a) * 30.6, 15 + math.sin(a) * 30.6
                ln = 3 + h32(int(zr), k, 2) % 8
                line3((X0, Y0, zr), (X0 + 0.4, Y0 - ln, zr), lambda x, y, s, t, z, wp: fogged(LEAF[1 + (x + y) % 2], fog_of(z), x, y), w=0.25)
                for j in range(0, ln, 2):
                    jx = ((h32(int(zr), k, j) % 7) - 3) * 0.15
                    disc(X0 + 0.2 + jx, Y0 - j - 0.5, zr - 0.05, 0.3 + (h32(int(zr), k, j, 4) % 5) * 0.09,
                         lambda x, y, s, t, z, wp: fogged((LEAF[3] if s + t < -0.3 else LEAF[2] if s + t < 0.4 else LEAF[1]) if h32(x, y, 9) % 9 else FLOWER[h32(x, y) % 5], fog_of(z), x, y))
    if DECAY:
        rr = random.Random(3)
        for _ in range(26):
            X, Z = rr.uniform(-6.5, 6.5), rr.uniform(16, 60)
            if abs(X) < 1.2 and Z < 30: continue
            col = rr.choice((STONE[5], CREAM[3], WARM[2], RED[2], STONE[2]))
            quad((X - 0.4, 0.03, Z), (X + 0.4, 0.03, Z), (X - 0.4, 0.03, Z + 0.5), lambda x, y, s, t, z, wp, c=col: fogged(c, fog_of(z), x, y))
    for (xx, zz, kind) in ((-11.5, 18.0, 'crate'), (-9.6, 19.5, 'sack'), (-12.0, 21.0, 'barrel'), (12.5, 19.5, 'crate'), (14.6, 20.6, 'sack'),
                           (-10.5, 33.0, 'crate'), (11.0, 36.0, 'barrel'), (-12.4, 46.0, 'sack')):
        prop(xx, zz, kind)
    # crowd in the aisle, mid to far (the near aisle is left to the player, Kloor and the exits)
    crowd((-6, 6), (27, 60), 30, 5, avoid=lambda X, Z: Z < 34 and abs(X) < 1.6)
    crowd((-6.5, 6.5), (60, 115), 40, 15)
    crowd((-21, -16), (30, 100), 10, 25)
    crowd((16, 21), (30, 100), 10, 26)
    crowd((-5.5, 5.5), (19, 26), 3, 6, avoid=lambda X, Z: abs(X) < 2.5)
    # dust in the light from the skylights
    for zz in (30, 54, 78):
        shaft(0, zz, -2 + (zz % 7), zz - 10, 44)
    if DECAY:
        for zz in (42, 66): shaft(3, zz, 6, zz - 6, 44, 1.4)
    # daylight spilling in through the cross-aisle from the hangar door, near left
    DAY.append((-22, 13, 16.0))

def banner(col, seed, torn=False):
    def sh(x, y, s, t, z, wp):
        if t > 0.9 and int(s * 8) % 2: return None                                               # notched hem
        if torn and nF(x * 2 + seed, y * 1.2) > 0.6: return None
        r = AWN[col]
        v = 3.4 + math.sin(s * 9 + seed) * 0.6 + (nB(x, y) - 0.5) * 0.5 - (1.2 if DECAY else 0)
        c = tone(r, v, x, y)
        if 0.25 < s < 0.75 and 0.3 < t < 0.55: c = tone(CREAM, v + 0.4, x, y) if h32(int(s * 6), int(t * 9), seed) % 2 else c   # an emblem
        if t < 0.06: c = WOOD[2]
        if GROWTH and nF(x * 1.3, y * 0.8) > 0.6: c = LEAF[1 + (x + y) % 3]
        return fogged(c, fog_of(z), x, y)
    return sh

def curtain_shader(seed, gap=None, dark=0.0):
    def sh(x, y, s, t, z, wp):
        if gap and gap[0] < s < gap[1] and t < 0.82:                                      # the parted opening
            dpt = (s - gap[0]) / (gap[1] - gap[0])
            return fogged(VELVET[0] if (x + y) % 4 else VELVET[1], fog_of(z), x, y)
        fold = math.sin(s * 40 + seed) * 0.5 + 0.5
        v = 2.0 + 2.6 * fold ** 1.5 + (nB(x, y) - 0.5) * 0.4 - (0.8 if t < 0.08 else 0) - dark
        if gap and t < 0.82 and abs(s - gap[0]) < 0.05: v += 1.0                         # the gathered edge catches light
        if DECAY and nF(s * 90 + seed, t * 46) > 0.62: v -= 0.9                                    # moth-eaten, stained
        c = tone(VELVET, v, x, y)
        if t > 0.94: c = GLOW[1] if (x // 2 + y) % 3 else GLOW[0]                          # gold fringe on top
        return fogged(c, fog_of(z) * 0.8, x, y)
    return sh

def auction_portal(XW, ZC, half=4.6, top=12.8):
    """a brick arch with a parted velvet curtain in the side wall (plane x = XW), a gavel sign over it, two lanterns,
    and a carpet running to it across the floor from the main aisle"""
    ar = 3.6                                                                          # the opening: 7.2 wide, arched top
    def portal(x, y, s, t, z, wp):
        Zp, Yp = wp[2] - ZC, wp[1]
        r_open = math.hypot(Zp, Yp - 8.4) if Yp > 8.4 else abs(Zp)
        if r_open < ar:                                                               # inside: the curtain, parted in the middle
            if abs(Zp) < 0.9 + 0.5 * (1 - Yp / 12): return fogged(VELVET[0] if (x + y) % 3 else VELVET[1], fog_of(z), x, y)
            fold = math.sin(Zp * 9) * 0.5 + 0.5
            v = 1.8 + 2.4 * fold ** 1.5 - (0.8 if DECAY and nF(Zp * 9 + 3, Yp * 4) > 0.6 else 0)
            return fogged(tone(VELVET, v, x, y), fog_of(z), x, y)
        if r_open < ar + 1.0:                                                         # stone voussoirs and jambs
            k = int((math.atan2(Yp - 8.4, Zp) if Yp > 8.4 else (Yp - 8.4)) * 4)
            v = 3.6 + (0.6 if k % 2 else 0) + (nB(x, y) - 0.5) * 0.6 - (1.2 if r_open > ar + 0.85 else 0)
            return fogged(tone(STONE, v - (0.8 if DECAY else 0), x, y), fog_of(z), x, y)
        return None
    quad((XW, 0, ZC - half), (XW, 0, ZC + half), (XW, top, ZC - half), portal)
    quad((XW - 0.05, top + 0.2, ZC - 2.6), (XW - 0.05, top + 0.2, ZC + 2.6), (XW - 0.05, top + 2.2, ZC - 2.6), sign_shader(77, glyphs=False))
    gavel_sign(XW - 0.1, top + 1.2, ZC)
    for dz in (-half - 0.6, half + 0.6):                                               # lanterns on brackets
        line3((XW, 9.0, ZC + dz), (XW - 0.9, 9.0, ZC + dz), lambda x, y, s, t, z, wp: fogged(METAL[2], fog_of(z), x, y), w=0.15)
        bulb(XW - 0.9, 8.4, ZC + dz)
    quad((7.5, 0.02, ZC - 1.6), (XW, 0.02, ZC - 1.6), (7.5, 0.02, ZC + 1.6),
         lambda x, y, s, t, z, wp: fogged(tone(VELVET, 2.6 + (1.1 if t < 0.1 or t > 0.9 else 0) + (nB(x, y) - 0.5) * 0.5 - (1.2 if DECAY and nF(wp[0] * 2, wp[2] * 2) > 0.55 else 0), x, y), fog_of(z), x, y))
    LAMPS.add(XW - 3, 3.0, ZC, 6.0)

def gavel_sign(X, Y, Z):
    """a painted gavel on the sign board (no words, both languages read it)"""
    (sx, sy) = proj(X, Y, Z); s_ = F / Z * 0.16
    for (gx, gy) in [(i, 0) for i in range(-4, 2)] + [(i, -1) for i in range(-4, 2)] + [(2, j) for j in range(-3, 3)] + [(3, j) for j in range(-3, 3)] + [(4, j) for j in range(-3, 3)]:
        for ddx in range(int(s_) + 1):
            for ddy in range(int(s_) + 1):
                put(int(sx + gx * s_) + ddx, int(sy + gy * s_) + ddy, Z - 0.3, lambda x, y, s, t, z, wp: GLOW[3], new_obj())

def scene_alley():
    global SHELL
    SHELL = Shell(22, 16, 72, 6, 8, deck=16.0, glaze=False); SHELL.ribdz = 8
    # the lane is narrow: stall backs against walls at |x| 13 -- except Zerren's niche at the near left
    quad((-13.0, 0, 22.0), (-13.0, 0, 72.0), (-13.0, 16.0, 22.0), wall_shader(True, 1))
    quad((13.0, 0, 9.0), (13.0, 0, 72.0), (13.0, 16.0, 9.0), wall_shader(True, 2))
    quad((-22.0, 0, 22.0), (-13.0, 0, 22.0), (-22.0, 16.0, 22.0), wall_shader(False, 3))
    # a shuttered shop in the near right wall, with a lamp over it
    quad((12.9, 0, 10.0), (12.9, 0, 15.0), (12.9, 9.0, 10.0), lambda x, y, s, t, z, wp: fogged(tone(METAL if not DECAY else RUSTR, 2.4 + (0.9 if (t * 30) % 1 < 0.5 else 0), x, y), fog_of(z), x, y))
    quad((12.8, 9.0, 9.6), (12.8, 9.0, 15.4), (12.8, 10.6, 9.6), sign_shader(91))
    bulb(12.0, 11.4, 12.5)
    # Zerren's niche: shelves of sound-ampules and a gramophone horn behind his counter (a sprite), a canopy, a rug
    quad((-21.4, 0, 9.0), (-21.4, 0, 22.0), (-21.4, 10.5, 9.0), ampule_shelves)
    horn(-19.8, 10.0, 12.5)
    quad((-21.6, 11.4, 9.0), (-21.6, 11.4, 21.9), (-13.0, 9.6, 9.0), awning_shader('violet', 31))
    quad((-20.5, 0.02, 12.0), (-14.0, 0.02, 12.0), (-20.5, 0.02, 21.0), lambda x, y, s, t, z, wp: fogged(tone(AWN['red'], 2.0 + (1.0 if int(s * 8 + t * 8) % 2 else 0), x, y), fog_of(z), x, y))
    LAMPS.add(-17, 3, 15, 6.0)
    bulb(-16.5, 9.0, 15.5)
    # the lane: stalls crammed on both sides
    for side in (-1, 1):
        z = 23.0 if side < 0 else 15.6; k = 0
        while z < 68:
            ln = 6.0 + (h32(side, k, 8) % 3) * 1.2
            col = COLS[h32(side, k, 9) % len(COLS)]
            stall(side, 4.5 * side, 8.3, z, z + ln, col, 500 + side * 50 + k, shut=DECAY and k % 3 == 2)
            if k % 2 == 0 and z < 50:                                             # a blade sign sticking out into the lane
                bs = side * 4.6; zc = z + 0.8
                quad((bs, 12.4, zc), (bs - side * 2.6, 12.4, zc), (bs, 14.0, zc), sign_shader(700 + k * 3 + side, neon=('amber' if (k + side) % 3 == 0 else None)))
            z += ln + 0.5; k += 1
    # paper lanterns strung across the lane
    for zz in range(18, 66, 6):
        line3((-4.5, 13.6, zz), (4.5, 13.6, zz + 1), lambda x, y, s, t, z, wp: fogged(STONE[0], fog_of(z), x, y), w=0.08, sag=0.8)
        for k in range(4):
            u = -3.2 + k * 2.1
            if DECAY and h32(zz, k) % 3 == 0: continue
            col = COLS[(zz + k) % len(COLS)]
            disc(u, 13.0 - 0.5 * math.sin(math.pi * (u + 4.5) / 9), zz + 0.5, 0.55, lambda x, y, s, t, z, wp, c=col: fogged(AWN[c][5] if s + t < 0 else AWN[c][4], fog_of(z) * 0.6, x, y))
            LAMPS.add(u, 9.0, zz + 0.5, 3.0)
    # pipes and cables under the deck
    for (xx, yy, w, c) in ((-11.5, 15.2, 0.8, METAL[3]), (-10.0, 15.4, 0.5, RUSTR[2] if DECAY else METAL[4]), (11.5, 15.1, 0.9, METAL[2]), (9.0, 15.5, 0.35, AWN['red'][2])):
        line3((xx, yy, 3), (xx, yy, 70), lambda x, y, s, t, z, wp, cc=c: fogged(cc, fog_of(z), x, y), w=w)
    crowd((-3.2, 3.2), (22, 64), 18, 9)
    crowd((-4.0, -3.0), (24, 50), 4, 11)
    crowd((3.0, 4.0), (20, 50), 4, 12)
    for zz in (30, 46):                                                           # steam from a food stall
        shaft(-3.0, zz, -2.0, zz - 2, 15, 1.2)
    if GROWTH:
        for zz in range(8, 66, 3):
            for xx in (-12.6, 12.6, -5.0, 5.0):
                ln = 2 + h32(zz, int(xx)) % 6
                line3((xx, 16, zz), (xx, 16 - ln, zz), lambda x, y, s, t, z, wp: fogged(LEAF[1 + (x + y) % 3], fog_of(z), x, y), w=0.3)
                disc(xx, 16 - ln, zz - 0.05, 0.4, lambda x, y, s, t, z, wp: fogged(FLOWER[h32(x, y) % 5] if h32(x, y, 2) % 3 == 0 else LEAF[3], fog_of(z), x, y))

def ampule_shelves(x, y, s, t, z, wp):
    rows = 5; rr = (t * rows) % 1; row = int(t * rows)
    if rr < 0.12: return fogged(WOOD[2], fog_of(z), x, y)                                  # shelf boards
    cell = int(s * 14)
    if (s * 14) % 1 < 0.6 and rr < 0.75:
        tint = [AWN['teal'][4], AWN['violet'][4], GLOW[2], AWN['red'][4], LEAF[4], AWN['blue'][4]][h32(cell, row) % 6]
        if rr > 0.6: return fogged(STONE[6], fog_of(z), x, y)                              # stoppers
        return fogged(tint if (x + y) % 3 else STONE[7], fog_of(z), x, y)
    return fogged(WOOD[0], fog_of(z), x, y)

def horn(X, Y, Z):
    (sx, sy) = proj(X, Y, Z); s_ = F / Z
    for i in range(int(2.2 * s_)):
        r = 0.18 * s_ + i * 0.35
        for a in range(0, 360, 6):
            px_ = int(sx + i * 0.6 + math.cos(math.radians(a)) * r * 0.35)
            py_ = int(sy - i * 0.25 + math.sin(math.radians(a)) * r * 0.5)
            put(px_, py_, Z - 0.5, lambda x, y, s, t, z, wp: GLOW[1] if (x + y) % 3 else GLOW[3], new_obj())

def wall_shader(posters=True, seed=0):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        course = math.floor(Y / 0.42); bu = Z / 1.1 + (0.5 if course % 2 else 0)
        v = 2.4 + (nA(x, y) - 0.5) * 1.0 - (1.2 if (Y / 0.42) % 1 < 0.2 * Z / 30 or bu % 1 < 0.1 * Z / 30 else 0)
        c = tone(BRICK, v - (0.8 if DECAY else 0), x, y)
        if posters:                                                                    # pasted bills, peeling
            cell = (int(Z / 2.6), int((Y - 3) / 3.4))
            if 3.0 < Y < 13 and h32(cell[0], cell[1], seed) % 3 == 0 and (Z % 2.6) > 0.25 and ((Y - 3) % 3.4) > 0.3:
                pc = [CREAM[4], AWN['red'][4], AWN['ochre'][4], AWN['teal'][4], BONE[3]][h32(cell[0], cell[1], seed, 2) % 5]
                if DECAY and nF(x * 2, y * 2) > 0.5: pc = CREAM[1]
                c = pc if (h32(x // 2, y // 2, seed) % 4) else STONE[1]
        if GROWTH and nF(Z * 1.4, Y * 0.5) > 0.55 - Y * 0.012 and nF(Z * 4.0, Y * 4.0) > 0.3:
            c = tone(LEAF, 1.2 + (nB(x * 2, y * 2) - 0.5) * 2.2 + Y * 0.06, x, y)                     # ivy
        return fogged(c, fog_of(Z), x, y)
    return sh

def scene_auction():
    global SHELL
    SHELL = Shell(26, 15, 34.5, 12, 11, glaze=True); SHELL.ribdz = 11
    # the velvet backdrop closing the bay, with a gold-fringed pelmet
    quad((-26, 0, 34.0), (26, 0, 34.0), (-26, 21, 34.0), curtain_shader(seed=3))
    quad((-26, 19.5, 33.6), (26, 19.5, 33.6), (-26, 23.5, 33.6), lambda x, y, s, t, z, wp: fogged(tone(VELVET, 3.4 + math.sin(s * 30) * 0.8, x, y) if t > 0.15 else (GLOW[1] if (x + y) % 2 else GLOW[0]), fog_of(z), x, y))
    # side drapes swagged in front of the side windows
    for side in (-1, 1):
        quad((side * 25.8, 0, 14), (side * 25.8, 0, 33.5), (side * 25.8, 15, 14), curtain_shader(seed=5 + side, dark=1.4))
    # the stage: planked top, a dark skirt, steps in the middle of its front
    stage_top = lambda x, y, s, t, z, wp: fogged(tone(WOOD, 3.2 + (0.7 if (wp[0] * 1.0) % 1 < 0.5 else 0) + LAMPS.glow(*wp) * 1.5 + (nB(x, y) - 0.5) * 0.5 - (1.0 if DECAY and nF(x, y) > 0.6 else 0), x, y), fog_of(z), x, y)
    quad((-11, 3.0, 20.0), (11, 3.0, 20.0), (-11, 3.0, 33.5), stage_top)
    quad((-11, 0, 20.0), (11, 0, 20.0), (-11, 3.0, 20.0), lambda x, y, s, t, z, wp: fogged(tone(VELVET, 1.6 + math.sin(s * 70) * 0.6, x, y) if t < 0.85 else GLOW[1], fog_of(z), x, y))
    for k in range(3):                                                                         # steps down to the floor
        zf = 20.0 - (k + 1) * 1.2; hgt = 3.0 - (k + 1) * 1.0
        if hgt <= 0: break
        quad((-3.2, hgt, zf), (3.2, hgt, zf), (-3.2, hgt, zf + 1.2), stage_top)
        quad((-3.2, 0, zf), (3.2, 0, zf), (-3.2, hgt, zf), plain(WOOD, 1.6))
    # the auctioneer's lectern and the lot pedestal with the Dream Egg under a glass bell
    box(2.6, 4.6, 3.0, 7.4, 24.0, 25.5, plain(WOOD, 2.8), plain(WOOD, 2.0), plain(WOOD, 3.6))
    quad((2.6, 6.6, 23.95), (4.6, 6.6, 23.95), (2.6, 7.4, 23.95), lambda x, y, s, t, z, wp: GLOW[2] if (x + y) % 2 else GLOW[1])
    box(7.0, 9.0, 3.0, 6.4, 27.0, 29.0, plain(STONE, 4.0), plain(STONE, 2.8), plain(STONE, 5.2))
    disc(8.0, 8.0, 27.5, 1.3, lambda x, y, s, t, z, wp: (VELVET[6] if s * s + t * t > 0.75 else (CAP[5] if t < -0.2 else CAP[3])) if not GROWTH else (LEAF[4] if s * s + t * t > 0.75 else CAP[4]))
    LAMPS.add(8.0, 8.0, 27.5, 4.0)
    # lamp clusters over the stage
    for xx in (-7, 0, 7):
        line3((xx, 26, 26), (xx, 15.5, 26), lambda x, y, s, t, z, wp: fogged(STONE[0], fog_of(z), x, y), w=0.1)
        for k in range(3): bulb(xx - 0.6 + k * 0.6, 15.2 - (k % 2) * 0.4, 26)
    # a carpet runner from the steps towards the camera, rows of folding chairs on both sides, behind the bidders
    quad((-2.8, 0.02, 4.0), (2.8, 0.02, 4.0), (-2.8, 0.02, 16.4), lambda x, y, s, t, z, wp: fogged(tone(VELVET, 2.6 + (1.0 if s < 0.08 or s > 0.92 else 0) + (nB(x, y) - 0.5) * 0.6 - (1.2 if DECAY and nF(x, y) > 0.55 else 0), x, y), fog_of(z), x, y))
    for side in (-1, 1):
        for row in range(4):
            zz = 22.0 + row * 3.0
            for c in range(4):
                xx = side * (13.0 + c * 2.6)
                chair(xx, zz, (side, row, c))
    crowd((-24, -13), (22, 31), 6, 21, avoid=lambda X, Z: False)
    crowd((13, 24), (22, 31), 5, 22)
    shaft(-14, 26, -16, 18, 38, 2.2); shaft(13, 30, 15, 22, 38, 2.0)
    if DECAY: shaft(0, 28, 2, 20, 38, 1.6)

def prop(X, Z, kind):
    if kind == 'crate':
        sh = lambda x, y, s, t, z, wp: fogged(tone(WOOD, 3.0 + (0.8 if (s * 3) % 1 < 0.15 or (t * 3) % 1 < 0.15 else 0) + (nB(x, y) - 0.5) * 0.6, x, y), fog_of(z), x, y)
        box(X - 1.4, X + 1.4, 0, 2.6, Z, Z + 2.4, sh, plain(WOOD, 2.2), plain(WOOD, 3.6))
        if not DECAY:
            for k in range(5):
                disc(X - 1.0 + k * 0.5, 2.9, Z + 0.6 + (k % 2) * 0.6, 0.38, lambda x, y, s, t, z, wp, kk=k: fogged([RED[4], GLOW[2], LEAF[4], FLOWER[1], CAP[4]][kk], fog_of(z), x, y))
    elif kind == 'sack':
        disc(X, 1.3, Z, 1.4, lambda x, y, s, t, z, wp: fogged(tone(CREAM, 3.4 - t * 1.6 - s * 0.8 + (nB(x, y) - 0.5), x, y), fog_of(z), x, y))
        disc(X + 0.3, 2.4, Z - 0.05, 0.6, lambda x, y, s, t, z, wp: fogged(tone(CREAM, 2.6 - t, x, y), fog_of(z), x, y))
    else:
        quad((X - 1.0, 0, Z), (X + 1.0, 0, Z), (X - 1.0, 3.0, Z), lambda x, y, s, t, z, wp: fogged(tone(METAL if not DECAY else RUSTR, 2.0 + 2.2 * math.sin(s * math.pi) + (-1.2 if (t * 3) % 1 < 0.12 else 0), x, y), fog_of(z), x, y))

def chair(X, Z, seed):
    if DECAY and h32(*seed) % 4 == 0: return                                                 # chairs gone / stacked away
    wood = plain(WOOD, 2.6)
    quad((X - 0.8, 2.4, Z), (X + 0.8, 2.4, Z), (X - 0.8, 2.4, Z + 1.4), plain(WOOD, 3.4))   # seat
    quad((X - 0.8, 2.4, Z + 1.4), (X + 0.8, 2.4, Z + 1.4), (X - 0.8, 5.0, Z + 1.4), wood)   # back
    for lx in (X - 0.7, X + 0.7):
        line3((lx, 0, Z + 0.1), (lx, 2.4, Z + 0.1), lambda x, y, s, t, z, wp: fogged(METAL[2], fog_of(z), x, y), w=0.12)

# ==================================================================================================== render
{'hall': scene_hall, 'alley': scene_alley, 'auction': scene_auction}[SCENE]()
SHELL.cast()
img = Image.new('RGB', (W, H)); ip = img.load()
for y in range(H):
    for x in range(W):
        g = G[y][x]
        if g is None: ip[x, y] = INK; continue
        shader, obj, s, t, wp = g
        c = shader(x, y, s, t, ZB[y][x], wp)
        if c is None: c = INK
        if DECAY and y < 330 and nA(x * 0.5, y * 1.4) > 0.5:
            c = nearest(tuple(int(ch * 0.78 + 58 * 0.22) for ch in c))
        if SHAFT[y][x] and shader is not shell_floor:                                          # dusty beams over everything
            if (x + y) % 2 == 0 or SHAFT[y][x] > 1: c = nearest(tuple(min(255, int(ch * 1.12 + 10)) for ch in c))
        ip[x, y] = c
# outlines: where two objects meet at different depths, darken the farther pixel
px2 = img.copy(); p2 = px2.load()
for y in range(H - 1):
    for x in range(W - 1):
        g = G[y][x]
        if g is None: continue
        for (nx_, ny_) in ((x + 1, y), (x, y + 1)):
            h_ = G[ny_][nx_]
            if h_ is None or h_[1] == g[1]: continue
            za, zb = ZB[y][x], ZB[ny_][nx_]
            if abs(za - zb) < 0.6 + 0.02 * min(za, zb): continue
            fx, fy = (x, y) if za > zb else (nx_, ny_)
            zn = min(za, zb)
            p2[fx, fy] = INK if zn < 40 else fogged(STONE[0], fog_of(zn) * 0.6, fx, fy)
name = SCENE if VARIANT == 'base' else f'{SCENE}_{VARIANT}'
px2.save(f'{OUT}/{name}.png')
print('done', name)
