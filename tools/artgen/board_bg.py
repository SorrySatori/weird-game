"""Aboard the skyship Verdigrace (SkyshipBoardScene), 1067x600, the shared camera (raster3d.py). The same vessel as the
look-up cut (skyship.png): the deck of the gondola hung under the moss-netted gas bladder. Warm deck planks; the far
bulwark with living-wood balusters and climbing vines curving round to the bow, where the stem rises into a fiddlehead
curl and a lantern hangs; the rope ladder hooked over the rail by the bow (the way back down the mycelium tree =
"Return to city"); the grown dial-board in the middle (a brass-and-chitin pedestal with a green lens -- the floor
counter came from here); the cabin on the right with warm portholes; two vine-wrapped stanchions with glowing pods
carrying the rigging up to the bladder, whose dark underside (net cords, glowing spores, hanging moss) closes the top.
Beyond the rail: the emerald overcast, a cloud sea and, far below in the haze, the city with the Scraper's needle and
the Egg.

    python3 board_bg.py <outdir>   ->  board.png  (= assets/images/backgrounds/skyship_board.png); prints the hot spots
"""
import sys, math
from common import h32
from shedkit import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = Raster()
ZB = 24.0                                   # the far bulwark
BOW_C, BOW_R = (-21.0, 17.6), 6.4           # the bulwark curves round this centre to the bow
STEM = (-27.6, 16.2)                        # the stem post (x, z)
LADDER = (-27.1, 19.6)                      # the rope ladder's hooks on the rail

DECK = ramp('#1c1009 #2a170d #382012 #472917 #56331d #673d23 #7a4a2c')
HULL = ramp('#140e09 #20160d #2b1e12 #372717 #43301d')
LIVE = ramp('#10180b #1a2610 #243416 #2f431c #3b5323 #48642b')
ENV = ramp('#081009 #0d170f #132016 #1a291d #213325 #2a3e2d')
NET = ramp('#262612 #36361a #474522 #59562c')
POD = ramp('#2a6420 #46962e #72c442 #aee86c #dcffae')
BRASSB = ramp('#271c0d #3f2e18 #5a4324 #775b31 #977642 #ba9558')
SKYE = ramp('#1d3a30 #24463a #2c5244 #355e4f #3f6b5a #4a7866 #578572 #66937f #78a28e')
WARMG = (255, 196, 110)


def lit(X, Y, Z, n, k=1.0):
    """overcast light from the open sky beyond the far rail, the bladder's shade overhead, lantern + pod glows"""
    sky = 0.35 + 0.35 * max(0.0, -n[2]) * 0 + 0.25 * max(0.0, n[1]) + 0.3 * max(0.0, n[2] * -1 + 0.0)
    shade = 0.75 + 0.25 * min(1.0, max(0.0, (Z - 12.0) / 12.0))                       # brighter toward the open side
    w = 0.0
    for (lx, ly, lz, I, r) in ((-27.1, 7.4, 15.5, 0.6, 5.0), (20.6, 6.8, 17.2, 0.5, 4.5)):
        d2 = (lx - X) ** 2 + (ly - Y) ** 2 + (lz - Z) ** 2
        w += I * r * r / (r * r + d2)
    g = 0.0
    for (lx, ly, lz) in ((-14.0, 9.0, 23.5), (8.0, 9.6, 23.5), (0.0, 4.6, 21.0)):
        d2 = (lx - X) ** 2 + (ly - Y) ** 2 + (lz - Z) ** 2
        g += 0.35 * 16.0 / (16.0 + d2)
    return (sky * shade) * k, w, g


def shade(r, base, X, Y, Z, n, x, y, k=4.0):
    a, w, g = lit(X, Y, Z, n)
    c = tone(r, base + k * a + 3.0 * w + 1.5 * g, x, y)
    if w > 0.05: c = mix(c, (210, 150, 70), min(0.28, w * 0.45))
    if g > 0.05: c = mix(c, POD[2], min(0.2, g * 0.35))
    return c


# ---------------------------------------------------------------------------------------------------- the far view
# the city far below: towers as columns of varied width and height in the haze, sparse lit windows
TOWERS = []
_x = 0
while _x < W:
    w_ = 3 + h32(_x, 31) % 8
    top = 40 + h32(_x, 32) % 34 - (14 if h32(_x, 33) % 6 == 0 else 0)
    TOWERS.append((_x, w_, top, h32(_x, 34) % 3))
    _x += w_ + (h32(_x, 35) % 3)
TOP = [None] * W
for (tx, tw, top, k) in TOWERS:
    for xx in range(tx, min(W, tx + tw)): TOP[xx] = (top, k, tx, tw)


def backdrop(x, y, s, t, z, wp):
    """screen-space: the emerald overcast above the horizon; below it a cloud sea, then the city far down in the haze"""
    if y < HY:
        tt = y / HY
        v = 1.4 + 6.0 * tt ** 1.3 + (wn(0, x * 0.012, y * 0.05) - 0.5) * 1.6 + (wn(1, x * 0.04, y * 0.12) - 0.5) * 0.5
        return tone(SKYE, v, x, y)
    d = y - HY
    if d < 16 + (wn(2, x * 0.02, 1.0) - 0.5) * 10:                                       # the cloud sea, billowing
        v = 7.0 - d * 0.1 + (wn(2, x * 0.035, d * 0.25) - 0.5) * 2.4
        return tone(SKYE, v, x, y)
    haze = min(1.0, max(0.0, (d - 16) / 110.0))
    col = tone(SKYE, 5.8 - haze * 1.6 + (wn(3, x * 0.03, d * 0.2) - 0.5) * 0.8, x, y)
    if abs(x - 302) <= 1 and d > 6:                                                       # the Scraper, its needle over the clouds
        return mix(col, (20, 34, 28), 0.55 if x == 302 else 0.35)
    if abs(x - 302) <= 3 and d > 26: return mix(col, (22, 36, 30), 0.45)
    if (x - 214) ** 2 / 30 + (d - 40) ** 2 / 52 < 1:                                      # the Egg, pale in the haze
        return mix(col, (150, 172, 152), 0.55 - 0.1 * ((x - 214) > 1))
    tp = TOP[x]
    if tp and d > tp[0]:
        top, k, tx, tw = tp
        c = mix(col, (26, 44, 36), 0.3 + 0.12 * k - 0.15 * haze)
        if x == tx + tw - 1: c = mix(c, col, 0.3)                                         # a lit edge
        if (y % 3 == 0) and ((x - tx) % 2 == 1) and h32(x, y, 36) % 17 == 0: c = (150, 130, 80)
        return c
    return col


rs.quad((-1400, -900, 700), (1400, -900, 700), (-1400, 800, 700), backdrop, cls='sky')


# ---------------------------------------------------------------------------------------------------- the deck
def deck(x, y, s, t, z, wp):
    X, _, Z = wp
    n = (0, 1, 0)
    k = math.floor(Z / 0.55)
    v = 2.6 + (h32(k, 11) % 7 - 3) * 0.12 + (wn(0, X * 0.5, Z * 2) - 0.5) * 0.7
    if (Z / 0.55) % 1 < 0.9 * z * z / (F * CAMH) / 0.55 + 0.03: v -= 1.4                       # seams
    if ((X + (h32(k, 12) % 60) / 10.0) / 6.0) % 1 < 0.6 * z / F / 6.0 + 0.004: v -= 1.0         # butt joints
    if abs((Z / 0.55) % 1 - 0.5) < 0.12 and ((X + (h32(k, 12) % 60) / 10.0) / 6.0) % 1 < 0.03: v += 1.2   # nails
    if wn(3, X * 0.25, Z * 0.6) > 0.7: v -= 0.6                                               # damp patches
    v += 0.6 * math.exp(-((Z - 15.3) / 1.6) ** 2)                                              # worn along the walk
    if Z > ZB - 1.4 and wn(2, X * 1.2, Z * 2) > 0.55: return shade(LIVE, 1.6, X, 0, Z, n, x, y)  # moss in the lee of the bulwark
    return shade(DECK, v, X, 0, Z, n, x, y)
def in_hull(X, Z):
    if Z > ZB: return False
    if X < BOW_C[0] and Z > BOW_C[1]:
        return math.hypot(X - BOW_C[0], Z - BOW_C[1]) < BOW_R
    if X < BOW_C[0] - BOW_R: return False
    return True
def deck_cut(x, y, s, t, z, wp):
    return deck(x, y, s, t, z, wp) if in_hull(wp[0], wp[2]) else None
rs.quad((-60, 0, 6), (60, 0, 6), (-60, 0, ZB), deck_cut, cls='ground', cut=True)


# the far bulwark: straight, then round to the bow
def bulwark_pts():
    pts = [(46.0, ZB), (BOW_C[0], ZB)]
    for i in range(1, 11):
        a = math.radians(i * 9)
        pts.append((BOW_C[0] - BOW_R * math.sin(a), BOW_C[1] + BOW_R * math.cos(a)))
    pts.append((STEM[0], STEM[1]))
    return pts
BW = bulwark_pts()
def hull_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    if Y > 1.75: return shade(DECK, 3.4, X, Y, Z, (0, 1, 0), x, y)                           # the cap rail
    v = 1.8 + (wn(1, (X + Z) * 0.6, Y * 3) - 0.5) * 0.6
    if (Y / 0.45) % 1 < 0.12: v -= 0.8                                                        # strakes
    if Y < 0.5 and wn(2, X + Z, 1) > 0.5: return shade(LIVE, 1.4, X, Y, Z, (0, 0, -1), x, y)
    return shade(HULL, v, X, Y, Z, (0, 0, -1), x, y)
for (ax, az), (bx, bz) in zip(BW, BW[1:]):
    rs.quad((bx, 0, bz), (ax, 0, az), (bx, 1.95, bz), hull_sh, cls='wall')
def livewood(base=2.0):
    return lambda x, y, s, t, z, wp: shade(LIVE, base + (0.9 if (x + y) % 3 == 0 else 0), wp[0], wp[1], wp[2], (0, 0, -1), x, y, 3.0)
def along(pts, step):
    """points every `step` units along a polyline"""
    out = []; acc = 0.0
    for (ax, az), (bx, bz) in zip(pts, pts[1:]):
        L = math.hypot(bx - ax, bz - az); u = 0.0
        while u < L:
            if acc <= 0:
                out.append((ax + (bx - ax) * u / L, az + (bz - az) * u / L)); acc = step
            d = min(acc, L - u); u += d; acc -= d
    return out
for k, (px_, pz) in enumerate(along(BW[:-1], 1.25)):                                         # twisted balusters
    wob = 0.18 if k % 2 else -0.18
    rs.line3((px_, 1.95, pz), (px_ + wob, 2.8, pz), livewood(2.4), w=0.2)
    rs.line3((px_ + wob, 2.8, pz), (px_, 3.6, pz), livewood(2.4), w=0.2)
for (ax, az), (bx, bz) in zip(BW[:-1], BW[1:-1]):                                            # the top rail
    rs.line3((ax, 3.62, az), (bx, 3.62, bz), lambda x, y, s, t, z, wp: shade(DECK, 4.2 + (1.2 if y % 2 == 0 else 0), wp[0], wp[1], wp[2], (0, 1, -0.4), x, y), w=0.3)
for k, (px_, pz) in enumerate(along(BW[:-1], 0.9)):                                          # vines along the rail
    if wn(1, px_ * 0.3, pz * 0.3) < 0.48: continue
    rs.line3((px_, 3.55, pz), (px_ + 0.45, 2.4 - (k % 3) * 0.3, pz - 0.05), lambda x, y, s, t, z, wp: tone(LIVE, 3.2 + (x % 2), x, y), w=0.08, sag=0.15)

# the stem rising into a fiddlehead curl, a lantern hung from it
rs.line3((STEM[0], 0, STEM[1]), (STEM[0] - 0.6, 7.0, STEM[1]), livewood(2.4), w=0.75)
rs.line3((STEM[0] - 0.6, 7.0, STEM[1]), (STEM[0] - 0.5, 10.4, STEM[1]), livewood(2.4), w=0.66)
cx_, cy_ = STEM[0] + 1.5, 10.6                                                            # the fiddlehead: a curl rolling inward
prev = (STEM[0] - 0.5, 10.4)
for i in range(1, 44):
    a = math.pi + i * 0.17; r = 2.0 * (1 - i / 50)
    p = (cx_ + math.cos(a) * r, cy_ - math.sin(a) * r)
    rs.line3((prev[0], prev[1], STEM[1]), (p[0], p[1], STEM[1]), livewood(2.8 + (0.6 if i % 4 == 0 else 0)), w=0.62 * (1 - i / 52))
    prev = p
def lantern(X, Y, Z):
    frame = lambda x, y, s, t, z, wp: tone(BRASSB, 2.0 + (1.2 if (x + y) % 3 == 0 else 0), x, y)
    rs.box(X - 0.35, X + 0.35, Y - 0.55, Y + 0.45, Z - 0.35, Z + 0.35,
           lambda x, y, s, t, z, wp: WARMG if 0.2 < s < 0.8 and 0.15 < t < 0.85 else BRASSB[2],
           lambda x, y, s, t, z, wp: (214, 150, 70) if 0.2 < s < 0.8 and 0.15 < t < 0.85 else BRASSB[1], top=frame, cls='emit')
    rs.line3((X, Y + 0.45, Z), (X, Y + 0.8, Z), frame, w=0.06)
lantern(STEM[0] + 0.5, 7.4, STEM[1] - 0.7)
rs.line3((STEM[0] - 0.5, 8.4, STEM[1]), (STEM[0] + 0.5, 8.3, STEM[1] - 0.7), lambda x, y, s, t, z, wp: BRASSB[2], w=0.1)

# the rope ladder hooked over the rail by the bow
LX, LZ = LADDER
for dx in (-0.55, 0.55):
    rs.line3((LX + dx, 3.62, LZ), (LX + dx, 4.1, LZ + 0.15), lambda x, y, s, t, z, wp: BRASSB[3], w=0.09)
    rs.line3((LX + dx, 4.1, LZ + 0.15), (LX + dx, 3.4, LZ + 0.5), lambda x, y, s, t, z, wp: BRASSB[3], w=0.09)
    rs.line3((LX + dx, 3.62, LZ - 0.05), (LX + dx * 1.1, 0.05, LZ - 1.4), lambda x, y, s, t, z, wp: tone(NET, 2.4, x, y), w=0.08, sag=0.1)
for k in range(5):                                                                            # rungs, the bottom ones coiled on deck
    hy = 3.2 - k * 0.7; zz = LZ - 0.3 - k * 0.27
    rs.line3((LX - 0.55, hy, zz), (LX + 0.55, hy, zz), lambda x, y, s, t, z, wp: tone(DECK, 3.6, x, y), w=0.1)

# ---------------------------------------------------------------------------------------------------- the dial-board
def brass(base): return lambda x, y, s, t, z, wp: shade(BRASSB, base + (1.0 if t > 0.88 else 0) + (0.8 if s > 0.8 else 0), wp[0], wp[1], wp[2], (0, 0, -1), x, y, 3.0)
rs.box(-1.0, 1.0, 0, 3.0, 20.6, 21.6, brass(1.6), brass(1.2), top=brass(2.4), cls='prop')            # pedestal
rs.box(-1.4, 1.4, 0, 0.5, 20.3, 21.9, brass(1.2), brass(1.0), top=brass(2.0), cls='prop')            # foot
rs.box(-1.2, 1.2, 3.0, 3.5, 20.2, 21.4, brass(2.2), brass(1.6), top=lambda x, y, s, t, z, wp: (BRASSB[4] if (x // 2 + y) % 3 else (60, 180, 80)), cls='prop')   # the lever panel
def lens(x, y, s, t, z, wp):
    d = math.hypot(s / 0.78, t)
    if d > 0.86: return tone(BRASSB, 3.0 + (1.0 if t > 0.3 else 0), x, y)
    a = math.atan2(t, s)
    c = mix(POD[1], POD[3], max(0.0, 0.6 - d))
    if abs(d - 0.5) < 0.04 or (int((a + math.pi) / (2 * math.pi) * 12) % 2 == 0 and abs(d - 0.7) < 0.05): c = POD[0]
    if abs(math.atan2(t, s) - 1.1) < 0.08 and d < 0.6: c = (220, 255, 200)                          # the needle
    return c
rs.disc(0.0, 4.7, 20.5, 1.3, lens, cls='emit')
for sx in (-1.55, 1.55):                                                                              # side dials
    rs.disc(sx, 4.4, 20.6, 0.35, lambda x, y, s, t, z, wp: BRASSB[4] if math.hypot(s, t) > 0.6 else BRASSB[1])
for k in range(6):                                                                                    # grown tendrils round it
    a = k / 6 * 2 * math.pi
    rs.line3((math.cos(a) * 1.1, 0.2, 21.1 + math.sin(a) * 0.6), (math.cos(a) * 0.9, 2.6 + (k % 3) * 0.6, 21.1 + math.sin(a) * 0.5),
             lambda x, y, s, t, z, wp: tone(LIVE, 2.6 + (y % 2), x, y), w=0.1, sag=-0.2)

# ---------------------------------------------------------------------------------------------------- the cabin
CAB = (17.0, 40.0, 17.4, ZB - 0.05, 8.2)
def cab_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    if 19.2 < X < 21.8 and Y < 6.4:                                                                   # the door
        if X < 19.4 or X > 21.6 or Y > 6.2: return shade(HULL, 1.0, X, Y, Z, (0, 0, -1), x, y)
        if math.hypot(X - 20.5, Y - 4.6) < 0.5: return WARMG if math.hypot(X - 20.5, Y - 4.6) < 0.36 else BRASSB[3]
        if abs(X - 21.25) < 0.1 and abs(Y - 3.1) < 0.12: return BRASSB[5]
        return shade(DECK, 2.2 + (0.6 if int((X - 19.4) / 0.55) % 2 else 0), X, Y, Z, (0, 0, -1), x, y)
    for px_ in (25.0, 29.4, 33.8):                                                                    # portholes
        d = math.hypot(X - px_, Y - 5.0)
        if d < 0.75:
            if d > 0.56: return tone(BRASSB, 3.4 + (1 if Y > 5.0 else 0), x, y)
            return mix(WARMG, (200, 120, 50), d / 0.56)
    v = 2.0 + (wn(1, X * 0.6, Y * 2) - 0.5) * 0.6
    if (Y / 0.6) % 1 < 0.1: v -= 0.8
    return shade(DECK, v, X, Y, Z, (0, 0, -1), x, y)
def cab_side(x, y, s, t, z, wp):
    X, Y, Z = wp
    d = math.hypot(Z - 21.0, Y - 5.0)
    if d < 0.7: return tone(BRASSB, 3.2, x, y) if d > 0.52 else mix(WARMG, (200, 120, 50), d / 0.52)
    v = 1.8 + (wn(1, Z * 0.6, Y * 2) - 0.5) * 0.6
    if (Y / 0.6) % 1 < 0.1: v -= 0.8
    return shade(DECK, v, X, Y, Z, (-1, 0, 0), x, y)
rs.box(CAB[0], CAB[1], 0, CAB[4], CAB[2], CAB[3], cab_front, cab_side, cls='wall')
roof = lambda x, y, s, t, z, wp: shade(LIVE, 1.8 + (1.2 if t > 0.7 else 0) + (wn(2, wp[0], wp[2]) - 0.5), wp[0], wp[1], wp[2], (0, 1, 0), x, y, 3.0)
rs.box(CAB[0] - 0.5, CAB[1], CAB[4], CAB[4] + 0.5, CAB[2] - 0.5, CAB[3], roof, roof, top=roof, bottom=lambda x, y, s, t, z, wp: tone(HULL, 1.0, x, y), cls='prop')
for k in range(14):                                                                                   # moss hanging off the roof edge
    mx = CAB[0] - 0.3 + k * 1.6 + (h32(k, 3) % 8) / 10.0
    rs.line3((mx, CAB[4], CAB[2] - 0.45), (mx, CAB[4] - 0.6 - (h32(k, 4) % 12) / 10.0, CAB[2] - 0.45), lambda x, y, s, t, z, wp: tone(LIVE, 2.4 + (y % 2), x, y), w=0.12)
lantern(20.6, 6.8, CAB[2] - 0.45)

# crates and a coil of rope
def crate(X0, X1, Y0, Y1, Z0, Z1):
    sh = lambda x, y, s, t, z, wp: shade(DECK, 2.2 + (1.2 if s < 0.06 or s > 0.94 or t < 0.06 or t > 0.94 or abs(s - t) < 0.05 else 0), wp[0], wp[1], wp[2], (0, 0, -1), x, y)
    rs.box(X0, X1, Y0, Y1, Z0, Z1, sh, sh, top=sh, cls='prop')
crate(11.6, 14.0, 0, 2.4, 21.2, 23.6); crate(14.2, 16.4, 0, 2.2, 21.6, 23.8); crate(12.2, 14.2, 2.4, 4.4, 21.6, 23.4)
for ring in range(6):                                                                                 # the rope coil
    r = 1.35 - ring * 0.16; hh = 0.1 + ring * 0.035
    pts = [(-11.0 + math.cos(a / 16 * 2 * math.pi) * r, -0 + hh, 19.6 + math.sin(a / 16 * 2 * math.pi) * r * 0.9) for a in range(17)]
    for p, q in zip(pts, pts[1:]):
        rs.line3(p, q, lambda x, y, s, t, z, wp: tone(NET, 2.6 + (1 if (x + y) % 3 == 0 else 0), x, y), w=0.13)

# ---------------------------------------------------------------------------------------------------- the stanchions, rigging, bladder
for (sx, sz) in ((-14.0, ZB - 0.3), (8.0, ZB - 0.3)):
    rs.line3((sx, 0, sz), (sx, 34.0, sz), livewood(2.0), w=0.36)
    for i in range(40):                                                                               # a vine spiralling up it
        y0, y1 = i * 0.75, (i + 1) * 0.75
        a0, a1 = i * 0.9, (i + 1) * 0.9
        rs.line3((sx + math.cos(a0) * 0.4, y0, sz + math.sin(a0) * 0.3), (sx + math.cos(a1) * 0.4, y1, sz + math.sin(a1) * 0.3),
                 lambda x, y, s, t, z, wp: tone(LIVE, 3.0 + (x % 2), x, y), w=0.1)
    for (py_, pr) in ((8.6, 0.55), (10.0, 0.38), (13.4, 0.48)):                                      # glowing pods
        rs.disc(sx + 0.55, py_, sz - 0.3, pr, lambda x, y, s, t, z, wp: POD[4] if math.hypot(s - 0.2, t - 0.2) < 0.35 else (POD[3] if math.hypot(s, t) < 0.75 else POD[1]), cls='emit')

ENV_C, ENV_R = (0.0, 47.0, 36.0), (70.0, 17.0, 30.0)
def env_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    nx, ny, nz = (X - ENV_C[0]) / ENV_R[0] ** 2, (Y - ENV_C[1]) / ENV_R[1] ** 2, (Z - ENV_C[2]) / ENV_R[2] ** 2
    l = math.sqrt(nx * nx + ny * ny + nz * nz); nx, ny, nz = nx / l, ny / l, nz / l
    u = (X - ENV_C[0]) / ENV_R[0]
    th = math.atan2((Z - ENV_C[2]) / ENV_R[2], (Y - ENV_C[1]) / ENV_R[1])
    rim = (1 - abs(ny)) ** 0.7
    v = 1.3 + 3.2 * rim + (wn(0, X * 0.35, Z * 0.35) - 0.5) * 1.1 + (wn(1, X * 1.4, Z * 1.4) - 0.5) * 0.5
    a1 = u * 9 + th * 2.6 + wn(2, X * 0.15, Z * 0.15) * 0.6                                           # a diamond mesh, a little slack
    a2 = u * 9 - th * 2.6 + wn(3, X * 0.15, Z * 0.15) * 0.6
    tol = 0.035 * max(1.0, z / 36)
    if abs((a1 % 1) - 0.5) > 0.5 - tol or abs((a2 % 1) - 0.5) > 0.5 - tol:
        return tone(NET, 1.4 + 2.0 * rim + (0.6 if (x + y) % 3 == 0 else 0), x, y)                      # the net cords
    cell = (int(u * 40), int(th * 12))
    if h32(cell[0], cell[1], 9) % 13 == 0:                                                             # spores glowing in the skin
        cu, ct = (u * 40) % 1, (th * 12) % 1
        dd = ((cu - 0.5) * 1.0) ** 2 + ((ct - 0.5) * 2.2) ** 2
        if dd < 0.05: return POD[3] if dd < 0.015 else POD[1]
    return tone(ENV, v, x, y)
for y in range(0, HY):
    for x in range(W):
        dx, dh = (x + 0.5 - CX) / F, -(y + 0.5 - HY) / F
        ox, oy, oz = -ENV_C[0], CAMH - ENV_C[1], -ENV_C[2]
        A = (dx / ENV_R[0]) ** 2 + (dh / ENV_R[1]) ** 2 + (1 / ENV_R[2]) ** 2
        B = 2 * (ox * dx / ENV_R[0] ** 2 + oy * dh / ENV_R[1] ** 2 + oz / ENV_R[2] ** 2)
        C = (ox / ENV_R[0]) ** 2 + (oy / ENV_R[1]) ** 2 + (oz / ENV_R[2]) ** 2 - 1
        disc = B * B - 4 * A * C
        if disc < 0: continue
        tz = (-B - math.sqrt(disc)) / (2 * A)
        if tz <= 0: continue
        wpp = (tz * dx, CAMH + tz * dh, tz)
        rs.put(x, y, tz, env_sh, 99999, 0, 0, wpp, None, 'ceil')
for k in range(70):                                                                                   # moss hanging from the bladder
    u = (h32(k, 61) % 1000) / 1000 * 1.6 - 0.8
    zz = ENV_C[2] - ENV_R[2] * (0.25 + (h32(k, 62) % 600) / 1000)
    xx = ENV_C[0] + ENV_R[0] * u
    yy = ENV_C[1] - ENV_R[1] * math.sqrt(max(0.0, 1 - u * u - ((zz - ENV_C[2]) / ENV_R[2]) ** 2)) + 0.3
    ln = 1.5 + (h32(k, 63) % 50) / 10.0
    rs.line3((xx, yy, zz), (xx + 0.2, yy - ln, zz), lambda x, y, s, t, z, wp: tone(LIVE, 1.6 + (y % 3) * 0.5, x, y), w=0.18)
    if k % 9 == 0: rs.disc(xx + 0.2, yy - ln - 0.15, zz, 0.18, lambda x, y, s, t, z, wp: POD[3], cls='emit')
for (ax, az) in ((-34.0, ZB), (-14.0, ZB - 0.3), (8.0, ZB - 0.3), (30.0, ZB), (44.0, ZB), (-24.0, 21.0)):   # rigging to the bladder
    top_y = ENV_C[1] - ENV_R[1] * 0.92
    rs.line3((ax, 3.6 if ax not in (-14.0, 8.0) else 34.0, az), (ax * 0.8, top_y, az + 6.0), lambda x, y, s, t, z, wp: tone(NET, 2.0, x, y), w=0.08)

img = rs.render(INK, light_gain=1.0, grime_gain=0.5, bloom=0.55, stain_gain=0.2, damp_gain=0.04, sheen_gain=0.0)
img.save(f'{OUT}/board.png')
lx, ly = proj(0, 4.7, 20.5)
print('dial lens', round(lx), round(ly), 'pedestal foot y', round(proj(0, 0, 20.3)[1]))
print('ladder x', round(proj(LADDER[0], 0, LADDER[1])[0]), 'rail y', round(proj(0, 3.6, LADDER[1])[1]))
print('cabin front x from', round(proj(CAB[0], 0, CAB[2])[0]), 'door x', [round(proj(19.2, 0, CAB[2])[0]), round(proj(21.8, 0, CAB[2])[0])])
