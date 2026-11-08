"""The abandoned bus behind the Scraper (AbandonedBusScene), 1067x600 -- where the Bishop was found dead.

A Before-Time double-decker half-buried in the transit yard: its upper floor has rotted through and fallen in, so the
inside is one tall, dark steel hollow. The camera looks ACROSS the bus at its yard-side wall (a bus is narrower than
the walk line is long, so the priest walks along the aisle, front on the left, rear on the right):

  far wall   the lower deck's windows pressed full of earth (it is half-buried), the upper deck's grimy windows with
             the overcast yard and its pipes beyond, a ragged ledge of the upper floor still clinging to the wall with
             a few upper seats on it, the jammed middle door (earth behind its glass), the open front door at the left
             (daylight from the dug-out trench = the way out), long bench seats along the lower deck
  rear       the staircase up to the ledge, the rear windows
  front      the driver's cab behind its glazed partition, the windscreen buried
  roof       ribbed, rusted, pinholed; one torn hole lets a shaft of grey light down onto the place she lies
  growth     the journal's "seats consumed by fungus" and "bioluminescent patches": pale growth eating the upholstery
             and faint green glows near her (on the cloth and the spilled earth, never on the metal -- Brine Scripture
             says the signal never reached the steel)
The Bishop herself is a sprite (dead_bishop.png) lying against the right-hand bench, under the hole.

Camera: the shared VP (533, 296) and eye 12 units, but a wider lens (F 200 instead of 300): the player stands on the
walk line (y 534) at depth 10.08, the far wall is at depth 13 -- the bus is 3.4 m across, the near wall is cut away.

    python3 bus_bg.py <outdir>   ->  bus.png (= assets/images/backgrounds/AbandonedBus.png) + bus_guides.png; prints hot spots
"""
import sys, math
import raster3d, paintpass
raster3d.F = 200.0; paintpass.F = 200.0                 # the wide lens (patch before anything imports F)
from common import h32
from shedkit import *
from raster3d import proj

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
F2 = raster3d.F
rs = Raster()

XL, XR = -26.0, 26.0           # the bus: front (left) .. rear (right)
ZF = 13.0                      # the far wall (inner face)
ZN = 1.0                       # the near wall (cut away, at the camera)
TOP = 14.0                     # the cant rail: the far wall meets the roof
LEDGE = (7.6, 8.2)             # what is left of the upper floor
LWIN = (3.8, 7.0)              # lower deck windows (earth-filled)
UWIN = (9.4, 13.3)             # upper deck windows
FDOOR = (-25.8, -21.2, 7.2)    # the front door: x0, x1, height  (the exit)
MDOOR = (-2.0, 2.0, 7.2)       # the middle door, jammed
STAIR = (16.0, 25.4)           # the rear staircase runs up along the far wall
HOLE = (11.5, 8.8)             # the torn hole in the roof (X, Z) over the body
BODY = (11.0, 10.9)            # where the Bishop lies (X, Z) -- for the light and the growth around her
POOL = (11.8, 11.0)            # the centre of the daylight pool on the floor under the roof hole (on her)

PAINT = ramp('#12110d #1a1813 #23201a #2d2a21 #38342a #444034 #514c3f #5f594b #6e6858')   # the cream enamel, long gone grey
RUSTD = ramp('#170c07 #22120a #2f190e #3d2213 #4c2b18 #5c361f #6d4227')
STEELB = ramp('#0b0d0c #121514 #191d1b #212624 #2a302d #343b38 #3f4743')
SEAT = ramp('#140b0a #1e100e #2a1613 #371d18 #44251e #522d24 #61372b')   # wine-red moquette
SEAT2 = ramp('#0c1212 #121a19 #182322 #1f2d2b #273835 #304440')         # its teal pattern
EARTH = ramp('#0a0806 #110d09 #18130d #201912 #2a2117 #352a1d #413424')
SLAT = ramp('#0d0a07 #15100b #1d160f #261d14 #30251a #3b2e20 #473827')
POLE = ramp('#1a160a #2a2310 #3e3417 #54461e #6b5a27 #826e31')
FUNG = ramp('#2a2a20 #3e3d2e #55533e #6d6a50 #868265 #a09c7c #bab694')    # pale growth
GLASSU = ramp('#2c3532 #37423e #43504b #505e58 #5e6d66 #6d7c74 #7d8c83 #8f9d93')
DAYC = (150, 170, 162)                                   # overcast light
GREEN = MYC

LIGHTS = [  # (pos, intensity, radius, kind)  c = cool daylight, g = the green glow
    ((-23.4, 4.2, 12.4), 0.95, 11.0, 'c'),               # daylight through the open front door
    ((HOLE[0], 14.0, HOLE[1] + 0.6), 1.05, 13.0, 'c'),   # the torn roof hole
    ((-14.4, 11.2, 12.4), 0.55, 8.5, 'c'), ((-6.0, 11.2, 12.4), 0.45, 8.0, 'c'),
    ((6.0, 11.2, 12.4), 0.45, 8.0, 'c'), ((14.4, 11.2, 12.4), 0.5, 8.5, 'c'),
    ((-18.6, 11.2, 12.4), 0.4, 7.0, 'c'), ((18.6, 11.2, 12.4), 0.4, 7.0, 'c'),
    ((-25.4, 11.2, 9.0), 0.5, 8.0, 'c'), ((25.4, 11.2, 9.0), 0.5, 8.0, 'c'),
    ((0.0, 11.0, -4.0), 0.42, 34.0, 'c'),                # the near side's windows, behind the camera
    ((BODY[0] - 1.5, 1.6, 11.8), 0.55, 3.8, 'g'), ((BODY[0] + 3.4, 1.9, 12.2), 0.45, 3.2, 'g'),
    ((-12.5, 1.9, 12.2), 0.4, 3.0, 'g'),
]


def lit(X, Y, Z, n):
    c = g = 0.0
    for (lx, ly, lz), I, r, kind in LIGHTS:
        dx, dy, dz = lx - X, ly - Y, lz - Z
        d2 = dx * dx + dy * dy + dz * dz; d = math.sqrt(d2) + 1e-6
        ndl = max(0.0, (dx * n[0] + dy * n[1] + dz * n[2]) / d)
        if d > r: continue
        v = I * (0.25 + 0.75 * ndl) * (1 - d / r) ** 2
        if kind == 'c': c += v
        else: g += v
    # the shaft under the roof hole: a soft column of light, and the pool of daylight it lays on the floor round her
    sh = math.exp(-((X - HOLE[0] + (15.2 - Y) * 0.04) ** 2 + (Z - HOLE[1] - (15.2 - Y) * 0.14) ** 2) / 4.0)
    pool = math.exp(-((X - POOL[0]) ** 2 / 10.0 + (Z - POOL[1]) ** 2 / 2.6)) * max(0.0, 1 - Y / 5.0)
    pool *= 0.45 + 0.55 * max(0.0, n[1])
    return c + 0.45 * sh + 0.95 * pool + 0.1, g


def shade(r, base, X, Y, Z, n, x, y, k=4.6):
    c, g = lit(X, Y, Z, n)
    col = tone(r, base - 0.9 + k * c, x, y)
    if c > 0.1: col = mix(col, DAYC, min(0.18, c * 0.16))
    if g > 0.03: col = mix(col, GREEN[2], min(0.45, g * 0.8))
    return col


def dust(c, z):
    return mix(c, (20, 23, 20), max(0.0, min(0.12, (z - 9) / 30.0)))


FWD = (0.0, 0.0, -1.0); UP = (0.0, 1.0, 0.0); DOWN = (0.0, -1.0, 0.0)
RIGHT = (1.0, 0.0, 0.0); LEFT = (-1.0, 0.0, 0.0)

# ---------------------------------------------------------------------------------------------------- what lies beyond
_o1, _o2 = make_noise(9, 71, 1067, 600), make_noise(33, 72, 1067, 600)
def yard(x, y):
    """through the upper windows: the overcast sky over the yard, a huge rusty pipe arching across, the dark back
    walls of the city with a few warm windows"""
    dx, dy = ray(x, y)
    v = 4.2 + dy * 3.0 + (_o2(x * 0.6, y * 2.0) - 0.5) * 1.2
    c = tone(SKY, v, x, y)
    # the back wall of a tenement, low down, with a few lit windows
    if dy < 0.06 + 0.05 * math.sin(dx * 3.0) + 0.04 * (_o1(x, 3) - 0.5):
        c = tone(STONE, 2.0 + (_o1(x * 2, y * 2) - 0.5), x, y)
        if int((dx + 3) * 60) % 3 == 1 and int((dy + 3) * 70) % 4 == 2 and h32(int(dx * 60), int(dy * 70), 4) % 3:
            c = mix(GLOW[0], STONE[2], 0.4) if h32(int(dx * 60), int(dy * 70), 5) % 11 == 0 else STONE[1]
    # the great pipe: a band arching across the sky, and a vertical pipe
    py = 0.28 - 0.05 * (dx - 0.2) ** 2
    if abs(dy - py) < 0.055:
        k = (dy - py) / 0.055
        c = mix(tone(RUSTY, 1.6 - k * 1.2 + (_o1(x * 3, y) - 0.5) * 0.8, x, y), SKY[3], 0.5)
        if (dx * 9) % 1 < 0.05: c = mix(RUSTY[0], SKY[3], 0.45)
    for vx in (-0.95, 0.7):
        if abs(dx - vx) < 0.07 and dy > py - 0.02:
            k = (dx - vx) / 0.07
            c = mix(tone(RUSTY, 1.4 - k * 1.2 + (_o1(x, y * 3) - 0.5) * 0.6, x, y), SKY[3], 0.5)
    return c


def grime_glass(c, X, Y, x, y, seed, y0, y1):
    """dirty glass: a film of grime thick at the bottom, rain runs, smears, sometimes a crack"""
    t = (Y - y0) / (y1 - y0)
    g = 0.42 + 0.35 * max(0.0, 1 - t / 0.35) + 0.25 * (wn(1, X * 1.4, Y * 0.5) - 0.5)
    if (wn(2, X * 6.0, 1.0) > 0.62) and t < 0.7 + 0.3 * wn(3, X * 3, 2): g += 0.25    # runs
    g = max(0.25, min(0.94, g))
    c = mix(c, (34, 36, 30), g)
    if h32(seed, 3) % 3 == 0:                                                        # a crack across the pane
        u = (X - math.floor(X / 4.2) * 4.2) / 4.2
        if abs((t - 0.3) - (u - 0.4) * 0.9 - 0.06 * math.sin(u * 23)) < 0.01: c = mix(c, (96, 104, 96), 0.35)
    return c


def upper_glass(x, y, s, t, z, wp):
    X, Y, _ = wp
    seed = int(math.floor((X + 0.2) / 4.2))
    if h32(seed, 9) % 7 == 3 and Y > UWIN[0] + 1.0 + 1.2 * math.sin(X * 3.1) * 0.5:   # a pane broken out
        return yard(x, y)
    return grime_glass(yard(x, y), X, Y, x, y, seed, UWIN[0], UWIN[1])


def Z_IS_WALL(wp): return wp[2] > ZF + 0.1


def lower_glass(x, y, s, t, z, wp):
    """earth pressed against the glass: soil strata, stones, pale roots; a sliver of grey light over the top of it"""
    X, Y, _ = wp
    if Z_IS_WALL(wp) and (FDOOR[0] - 0.4 < X < FDOOR[1] + 0.4 or MDOOR[0] - 0.4 < X < MDOOR[1] + 0.4): return None
    top = LWIN[1] - 0.5 - 0.9 * wn(0, X * 0.5, 4.0) - 0.4 * math.sin(X * 0.7)
    if Y > top:
        c = mix(yard(x, y), (40, 44, 38), 0.55)
    else:
        v = 1.8 + (top - Y) * -0.15 + (wn(1, X * 2.5, Y * 2.5) - 0.5) * 1.3 + 0.6 * math.sin(Y * 5 + wn(2, X, 1) * 4)
        c = tone(EARTH, v, x, y)
        if wn(3, X * 4.0, Y * 4.0) > 0.74: c = tone(STONE, 3.0 + (wn(0, X * 9, Y * 9) - 0.5) * 2, x, y)  # stones
        r_ = abs(math.sin(X * 2.1 + Y * 0.6 + 3 * wn(1, X * 0.8, Y * 0.8)))
        if r_ < 0.05 and wn(2, X * 1.5, Y * 0.4) > 0.5: c = tone(FUNG, 1.6, x, y)                 # pale roots
    return grime_glass(c, X, Y, x, y, int(math.floor((X + 0.2) / 4.2)) + 50, LWIN[0], LWIN[1])


def trench(x, y, s, t, z, wp):
    """through the open front door: the dug-out trench, a ramp of trodden earth up to the yard, daylight from above"""
    X, Y, _ = wp
    u = max(0.0, min(1.0, (X - FDOOR[0]) / (FDOOR[1] - FDOOR[0])))
    if Y > 5.0 + 1.2 * math.sin(u * 4.0) * 0.4 + (wn(0, X * 3, 2) - 0.5):           # the sky over the trench lip
        return tone(SKY, 6.4 + (Y - 5) * 0.3, x, y)
    v = 3.4 + Y * 0.5 + (wn(1, X * 4, Y * 4) - 0.5) * 1.2 - abs(u - 0.5) * 1.4
    c = tone(EARTH, v + 1.4, x, y)
    return mix(c, (126, 134, 122), min(0.45, 0.1 + Y * 0.07))


# ---------------------------------------------------------------------------------------------------- the far wall
WINX = [-18.6, -14.4, -10.2, -6.0, 6.0, 10.2, 14.4, 18.6]   # window bay centres (half-width 1.9), both decks
def in_win(X, Y, y0, y1, half=1.9):
    for c_ in WINX:
        if abs(X - c_) < half and y0 < Y < y1: return c_
    return None


def far_wall(x, y, s, t, z, wp):
    X, Y, Z = wp
    # openings: windows, the doors
    if in_win(X, Y, *LWIN) is not None or in_win(X, Y, *UWIN) is not None: return None
    if (FDOOR[0] < X < FDOOR[1] or MDOOR[0] < X < MDOOR[1]) and Y < FDOOR[2]: return None
    v = 1.6
    # the frames and gaskets round the openings
    for (y0, y1) in (LWIN, UWIN):
        c_ = in_win(X, Y, y0 - 0.3, y1 + 0.3, 2.2)
        if c_ is not None:
            v = 3.6 if (Y > y1 or X < c_) else 1.2
            return shade(STEELB, v, X, Y, Z, FWD, x, y)
    for (x0, x1) in ((FDOOR[0], FDOOR[1]), (MDOOR[0], MDOOR[1])):
        if x0 - 0.35 < X < x1 + 0.35 and Y < FDOOR[2] + 0.35:
            return shade(STEELB, 3.4 if Y > FDOOR[2] else 1.6, X, Y, Z, FWD, x, y)
    # panels: the cream enamel gone grey, rivet lines, rust weeping from the seams and the sills
    r = PAINT
    if Y < 1.2: v = 1.0; r = STEELB                                              # the kick plate
    elif LWIN[1] + 0.3 < Y < LEDGE[0]: v = 1.9                                   # the advert panels' band
    elif Y > UWIN[1] + 0.3: v = 1.9
    if (X % 4.2) < 0.12 or abs(Y - 3.4) < 0.06 or abs(Y - 9.0) < 0.06: v -= 0.9
    if (X % 4.2) < 0.3 and int(Y * 4) % 2 == 0 and r is PAINT: v += 0.6            # rivets
    c = shade(r, v + (wn(0, X * 0.8, Y * 0.8) - 0.5) * 0.7, X, Y, Z, FWD, x, y)
    ru = wn(2, X * 2.2, Y * 0.35) * 0.7 + wn(3, X * 0.6, Y * 0.6) * 0.3
    if r is PAINT and ru > 0.62: c = mix(c, tone(RUSTD, 1.8 + (ru - 0.62) * 6, x, y), min(0.55, (ru - 0.62) * 3))
    # the advert frames between the decks: empty, their posters rotted to grey pulp
    if LWIN[1] + 0.5 < Y < LEDGE[0] - 0.25:
        for c_ in WINX:
            if abs(X - c_) < 1.7:
                if abs(X - c_) > 1.55 or Y < LWIN[1] + 0.62 or Y > LEDGE[0] - 0.37: return shade(STEELB, 3.2, X, Y, Z, FWD, x, y)
                pv = 2.0 + (wn(3, X * 3, Y * 3) - 0.5) * 1.6
                return shade(PAINT, pv, X, Y, Z, FWD, x, y) if h32(int(c_), 2) % 3 else shade(SEAT, pv + 0.4, X, Y, Z, FWD, x, y)
    return dust(c, z)
rs.quad((XL, 0, ZF), (XR, 0, ZF), (XL, TOP, ZF), far_wall, cls='wall', cut=True)
rs.quad((XL, UWIN[0], ZF + 0.25), (XR, UWIN[0], ZF + 0.25), (XL, UWIN[1], ZF + 0.25), upper_glass, cls='emit')
rs.quad((XL, LWIN[0], ZF + 0.25), (XR, LWIN[0], ZF + 0.25), (XL, LWIN[1], ZF + 0.25), lower_glass, cls='wall', cut=True)
# the window reveals (the wall's thickness)
for c_ in WINX:
    for (y0, y1) in (LWIN, UWIN):
        rs.quad((c_ - 1.9, y0, ZF), (c_ + 1.9, y0, ZF), (c_ - 1.9, y0, ZF + 0.25),
                lambda x, y, s, t, z, wp: shade(STEELB, 3.0, *wp, UP, x, y))
# the open front door: the trench outside, the folded leaves
rs.quad((FDOOR[0] - 5, 0, ZF + 1.6), (FDOOR[1] + 1, 0, ZF + 1.6), (FDOOR[0] - 5, FDOOR[2] + 2, ZF + 1.6), trench, cls='emit')
rs.quad((FDOOR[0] - 3, 0, ZF), (FDOOR[1] + 0.5, 0, ZF), (FDOOR[0] - 3, 0, ZF + 1.6),
        lambda x, y, s, t, z, wp: tone(EARTH, 3.4 + t * 1.2 + (wn(0, wp[0] * 3, wp[2] * 3) - 0.5), x, y), cls='ground')
for (xa, sgn) in ((FDOOR[0] + 0.1, 1), (FDOOR[1] - 0.1, -1)):
    def leaf(x, y, s, t, z, wp, sgn=sgn):
        X, Y, Z = wp
        if 0.12 < t < 0.92 and 0.15 < s < 0.85: return mix(trench(x, y, s, t, z, wp), (50, 52, 44), 0.55)
        return shade(STEELB, 2.6 + (0.6 if t > 0.92 else 0), X, Y, Z, (sgn * 1.0, 0, -0.3), x, y)
    rs.quad((xa, 0.05, ZF + 0.1), (xa + sgn * 0.5, 0.05, ZF - 0.55), (xa, FDOOR[2] - 0.1, ZF + 0.1), leaf)
# the jammed middle door: two leaves, glass with earth behind, a step-well
def mid_leaf(x, y, s, t, z, wp):
    X, Y, Z = wp
    u = (X - MDOOR[0]) / (MDOOR[1] - MDOOR[0])
    if 0.08 < (u * 2) % 1 < 0.92 and 0.42 < Y / FDOOR[2] < 0.93: return lower_glass(x, y, s, t, z, (X, LWIN[0] + (Y - 3.0) * 0.6, Z))
    v = 1.5 + (0.5 if (u * 2) % 1 < 0.08 else 0) - (1.2 if abs(u - 0.5) < 0.025 else 0) + (wn(0, X * 2, Y * 2) - 0.5) * 0.6
    if 0.36 < Y / FDOOR[2] < 0.4: v += 0.7
    return dust(shade(PAINT, v, X, Y, Z, FWD, x, y), z)
rs.quad((MDOOR[0], 0, ZF + 0.12), (MDOOR[1], 0, ZF + 0.12), (MDOOR[0], FDOOR[2], ZF + 0.12), mid_leaf)

# ---------------------------------------------------------------------------------------------------- the ends
def front_end(x, y, s, t, z, wp):
    """the driver's end: the buried windscreen low, the front upper windows high, steel between"""
    X, Y, Z = wp
    if 3.4 < Y < 7.0 and 3.0 < Z < 12.4: return lower_glass(x, y, s, t, z, (Z * 1.3, Y, X))
    if UWIN[0] < Y < UWIN[1] and 4.0 < Z < 12.2:
        if abs(Z - 8.1) < 0.18: return shade(STEELB, 1.2, X, Y, Z, RIGHT, x, y)
        return grime_glass(yard(x, y), Z, Y, x, y, 7, UWIN[0], UWIN[1])
    v = 2.0 + (wn(0, Z * 0.8, Y * 0.8) - 0.5) * 0.6
    if Y < 1.2: return shade(STEELB, 1.2, X, Y, Z, RIGHT, x, y)
    return dust(shade(PAINT, v, X, Y, Z, RIGHT, x, y), z)
rs.quad((XL, 0, ZN), (XL, 0, ZF), (XL, TOP, ZN), front_end, cls='wall')


def rear_end(x, y, s, t, z, wp):
    X, Y, Z = wp
    if UWIN[0] < Y < UWIN[1] and 4.0 < Z < 12.2:
        return grime_glass(yard(x, y), Z, Y, x, y, 11, UWIN[0], UWIN[1])
    if 3.0 < Y < 6.6 and 6.0 < Z < 12.0: return lower_glass(x, y, s, t, z, (Z * 1.3 + 40, Y, X))
    v = 2.0 + (wn(0, Z * 0.8 + 9, Y * 0.8) - 0.5) * 0.6
    if Y < 1.2: return shade(STEELB, 1.2, X, Y, Z, LEFT, x, y)
    return dust(shade(PAINT, v, X, Y, Z, LEFT, x, y), z)
rs.quad((XR, 0, ZN), (XR, 0, ZF), (XR, TOP, ZN), rear_end, cls='wall')
# glass reveals on the end windows are cheap and read: dark frame bars
for (xx, nrm) in ((XL + 0.05, RIGHT), (XR - 0.05, LEFT)):
    for (y0, y1, z0, z1) in ((UWIN[0], UWIN[1], 4.0, 12.2),):
        rs.line3((xx, y1 + 0.15, z0), (xx, y1 + 0.15, z1), lambda x, y, s, t, z, wp: STEELB[1], w=0.3)
        rs.line3((xx, y0 - 0.15, z0), (xx, y0 - 0.15, z1), lambda x, y, s, t, z, wp: STEELB[3], w=0.3)

# the driver's corner: the dashboard hump under the buried windscreen, the big wheel lying almost flat
# (the driver's seat and wheel went with the front: only the buried windscreen is left at that end)

# ---------------------------------------------------------------------------------------------------- the roof
RIB = 2.6
def roof_h(Z):
    """the roof's cross-section: the cant rail at 14 by the walls, the crown at 15.4"""
    u = (Z - ZN) / (ZF - ZN)
    return TOP + 1.4 * math.sin(math.pi * u) ** 0.7


def roof(x, y, s, t, z, wp):
    X, Y, Z = wp
    # the torn hole over her (light through it) and pinholes of rust
    dh = math.hypot((X - HOLE[0]) / 2.2, (Z - HOLE[1]) / 1.3) + 0.25 * (wn(1, X * 2.4, Z * 2.4) - 0.5)
    if dh < 1.0: return None
    if dh < 3.0 and h32(int(X * 4 + 999), int(Z * 4 + 999), 17) % 71 == 0: return tone(SKY, 3.4, x, y)       # pinholes round the tear
    n = (0.0, -1.0, 0.0)
    v = 2.7 + (wn(0, X * 1.3, Z * 1.3) - 0.5) * 0.7 - 1.5 * max(0.0, (8.0 - Z) / 7.0) + 0.5 * max(0.0, (Z - 10.5) / 2.5)   # dark toward us, catching the windows' light by the far wall
    if (X % RIB) < 0.22: v = 0.5 + (1.6 if X > HOLE[0] - 6 and (X % RIB) > 0.15 else 0)   # the ribs (lit edge by the tear)
    elif (X % RIB) < 0.36: v += 1.2
    elif abs(Z - 7.0) < 0.12 or abs(Z - 3.0) < 0.1 or abs(Z - 11.2) < 0.1: v -= 0.8      # panel seams
    c = shade(PAINT, v, X, Y, Z, n, x, y, k=2.6)
    # rust: blistered spots and runs along the ribs, heavy round the tear
    ru = 0.5 * wn(3, X * 3.4, Z * 3.4) + 0.5 * wn(2, X * 8.0, Z * 2.5)
    if (X % RIB) < 0.6: ru += 0.1
    if dh < 1.8: ru += (1.8 - dh) * 0.45
    if ru > 0.64: c = mix(c, tone(RUSTD, 1.2 + (ru - 0.64) * 4, x, y), min(0.4, (ru - 0.64) * 2.5))
    return dust(c, z)
ZS = [ZN, 2.5, 4.2, 6.0, 8.0, 10.0, 11.6, ZF]
ROOF = rs.obj()                                         # one surface id, so the facets don't occlude each other
for z0, z1 in zip(ZS, ZS[1:]):
    rs.quad((XL, roof_h(z0), z0), (XR, roof_h(z0), z0), (XL, roof_h(z1), z1), roof, obj=ROOF, cls='ceil', cut=True)
# a long dead lamp housing down the middle of the roof, the bell cord, a sagging cable
LAMPZ = 7.4
rs.box(XL + 2, XR - 2, roof_h(LAMPZ) - 0.45, roof_h(LAMPZ) - 0.05, LAMPZ - 0.35, LAMPZ + 0.35,
       lambda x, y, s, t, z, wp: dust(tone(STEELB, 0.9 + (0.9 if (wp[0] % 6.5) < 0.25 else 0), x, y), z),
       lambda x, y, s, t, z, wp: STEELB[1], bottom=lambda x, y, s, t, z, wp: dust(tone(PAINT, 0.8 + (1.4 if (wp[0] % 6.5) > 0.4 and abs(wp[2] - LAMPZ) < 0.2 and h32(int(wp[0] / 6.5), 4) % 3 else 0), x, y), z), cls='ceil')
rs.line3((XL + 1, TOP - 0.3, ZF - 0.4), (XR - 1, TOP - 0.3, ZF - 0.4), lambda x, y, s, t, z, wp: tone(POLE, 1.2, x, y), w=0.08, sag=0.0)
for (ca, cb, zc, sg) in ((-15.0, -11.0, 10.4, 0.6), (2.0, 4.8, 6.2, 0.4)):                # a couple of torn cables
    rs.line3((ca, roof_h(zc) - 0.3, zc), (cb, roof_h(zc) - 0.6, zc + 0.8), lambda x, y, s, t, z, wp: STEELB[1], w=0.06, sag=sg)
# strips of the roof's lining torn loose, hanging in the dark
for k in range(9):
    lx_ = -23 + k * 5.6 + (h32(k, 41) % 20) / 10.0
    if abs(lx_ - HOLE[0]) < 3: continue
    lz_ = 4.0 + (h32(k, 42) % 60) / 10.0; ln_ = 0.8 + (h32(k, 43) % 6) * 0.35
    for j in range(3):
        rs.line3((lx_ + j * 0.18, roof_h(lz_) - 0.1, lz_), (lx_ + j * 0.18 + 0.1, roof_h(lz_) - ln_ * (1 - j * 0.25), lz_ + 0.1),
                 lambda x, y, s, t, z, wp: tone(PAINT, 0.9 + t * 0.6 + (wn(1, x * 0.3, y * 0.3) - 0.5), x, y), w=0.14)
# beyond the hole: the overcast sky and the pipe that tore it
def hole_sky(x, y, s, t, z, wp):
    dx, dy = ray(x, y)
    c = tone(SKY, 5.0 + (_o2(x, y) - 0.5) * 1.2, x, y)
    if abs(dx * 0.6 + dy * 1.0 - 0.95) < 0.12: c = tone(RUSTY, 1.6 + (_o1(x * 3, y) - 0.5), x, y)   # a pipe across it
    return c
rs.quad((HOLE[0] - 4, 17.5, HOLE[1] - 3), (HOLE[0] + 4, 17.5, HOLE[1] - 3), (HOLE[0] - 4, 17.5, HOLE[1] + 3), hole_sky, cls='emit')
# the hole's torn lip, bent in
for k in range(22):
    a = k / 22 * 2 * math.pi
    px_, pz_ = HOLE[0] + math.cos(a) * 2.05, HOLE[1] + math.sin(a) * 1.2
    ln = 0.25 + (h32(k, 31) % 5) * 0.12
    rs.line3((px_, roof_h(pz_) - 0.05, pz_), (px_ - math.cos(a) * 0.2, roof_h(pz_) - ln, pz_ - math.sin(a) * 0.12),
             lambda x, y, s, t, z, wp: tone(RUSTD, 1.6 - t * 0.8, x, y), w=0.14)

# ---------------------------------------------------------------------------------------------------- the ledge (the upper floor that is left)
def boards(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 2.6 + (wn(0, X * 0.5, Z * 3) - 0.5) * 0.8 + (0.4 if h32(int(X / 0.9), 4) % 3 == 0 else 0)
    if (X / 0.9) % 1 < 0.1: v -= 1.0
    return dust(shade(SLAT, v, X, Y, Z, UP, x, y), z)
def ledge_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    return shade(STEELB if t < 0.5 else SLAT, 1.8 + (wn(1, X * 3, Y) - 0.5) * 0.8, X, Y, Z, FWD, x, y)
x0 = XL
while x0 < XR - 0.1:
    w_ = 1.2 + (h32(int(x0 * 10), 3) % 5) * 0.6
    x1 = min(XR, x0 + w_)
    d = 1.0 + (h32(int(x0 * 10), 4) % 6) * 0.22                    # how much of the floor still sticks out
    if STAIR[0] - 1 < x0 < STAIR[1]: d = max(d, 1.9)                # the landing over the stairs holds
    if h32(int(x0 * 10), 5) % 9 == 0 and not (STAIR[0] < x0 < STAIR[1]): d = 0.35   # fallen right back to the wall
    rs.box(x0, x1, LEDGE[0], LEDGE[1], ZF - d, ZF, ledge_front, ledge_front, top=boards,
           bottom=lambda x, y, s, t, z, wp: STEELB[1])
    if d > 1.0 and h32(int(x0 * 10), 6) % 3 == 0:                  # a joist stub sticking out, splintered
        jx = x0 + w_ * 0.5
        rs.box(jx - 0.18, jx + 0.18, LEDGE[0] + 0.05, LEDGE[1] - 0.05, ZF - d - 0.9, ZF - d, ledge_front, ledge_front,
               top=lambda x, y, s, t, z, wp: shade(SLAT, 3.0, *wp, UP, x, y))
    x0 = x1 + 0.02
# upper-deck seats still on the ledge (seen from the side: high backs facing the front)
def seat_profile(u, v, ang=0.0):
    """a double seat seen from the side, facing the front (left): the cushion, the backrest leaning back, a chrome
    grab rail on top, a steel leg. u, v in units from its front-bottom corner; returns a part name or None"""
    if ang:
        ca, sa = math.cos(ang), math.sin(ang)
        u, v = u * ca + v * sa, -u * sa + v * ca
    if 0.0 <= u <= 1.55 and 1.05 <= v <= 1.55 - 0.12 * (u < 0.15): return 'cush'
    bu = 1.45 + (v - 1.3) * 0.16                                        # the backrest leans back
    if 1.3 <= v <= 3.75 and bu <= u <= bu + 0.38 + 0.1 * math.sin((v - 1.3) / 2.45 * math.pi): return 'back'
    if 3.55 <= v <= 3.95 and bu - 0.15 <= u <= bu + 0.3: return 'rail'
    if abs(u - 0.35) < 0.09 and 0.0 <= v < 1.05: return 'leg'
    if abs(u - 1.3) < 0.07 and 0.0 <= v < 1.05: return 'leg'
    return None


def useat(xs, ang=0.0, y0=LEDGE[1], zc=ZF - 1.45, seed=0):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        part = seat_profile(X - xs, Y - y0, ang)
        if part is None: return None
        if part == 'rail': return tone(STEELB, 5.2 if (Y - y0) > 3.8 else 3.6, x, y)
        if part == 'leg': return STEELB[2]
        rim = 1.0 if seat_profile(X - xs + 0.12, Y - y0 + 0.12, ang) is None else 0.0     # backlit by the window
        v = 1.6 + (wn(1, X * 5, Y * 5) - 0.5) * 0.7 + rim * 1.4 + (0.4 if part == 'cush' else 0)
        if h32(int(X * 3 + 99), int(Y * 3 + 99), seed) % 7 == 0: v -= 0.8                 # torn
        return dust(tone(SEAT, v, x, y), z)
    rs.quad((xs - 0.6, y0 - 0.6, zc), (xs + 3.0, y0 - 0.6, zc), (xs - 0.6, y0 + 4.4, zc), sh, cut=True)
for k, xs in enumerate((-18.0, -9.6, 6.8, 11.0)): useat(xs, seed=k)
useat(-13.8, ang=-0.55, y0=LEDGE[1] - 0.9, zc=ZF - 1.9, seed=7)          # one tipped half over the broken edge

# straps hanging off the ledge's front rail, the rail itself
rs.line3((XL + 3, LEDGE[0] - 0.15, ZF - 1.2), (STAIR[0] - 1, LEDGE[0] - 0.15, ZF - 1.2), lambda x, y, s, t, z, wp: tone(POLE, 2.2, x, y), w=0.14)
for k, sx in enumerate((-19.6, -16.8, -11.0, -7.4, 4.4, 8.2, 13.6)):
    L_ = 1.0 + (h32(k, 2) % 3) * 0.25
    rs.line3((sx, LEDGE[0] - 0.15, ZF - 1.2), (sx + 0.05, LEDGE[0] - L_, ZF - 1.2), lambda x, y, s, t, z, wp: STEELB[2], w=0.1)
    if h32(k, 3) % 4: rs.disc(sx + 0.05, LEDGE[0] - L_ - 0.22, ZF - 1.2, 0.26, lambda x, y, s, t, z, wp: (STEELB[3] if (s * s + t * t) > 0.45 else None))
# a few pale strands of growth hanging off the ledge's broken edge
for k in range(16):
    sx = -22 + k * 2.7 + (h32(k, 7) % 10) * 0.12
    if STAIR[0] - 1 < sx < STAIR[1] + 1: continue
    L_ = 0.5 + (h32(k, 8) % 7) * 0.25
    rs.line3((sx, LEDGE[0], ZF - 1.1), (sx + 0.1, LEDGE[0] - L_, ZF - 1.15), lambda x, y, s, t, z, wp: tone(FUNG, 0.6 + t * 0.6, x, y), w=0.05)

# ---------------------------------------------------------------------------------------------------- the stairs at the rear
NST = 11
for i in range(NST):
    xa = STAIR[0] + i * (STAIR[1] - STAIR[0]) / NST
    xb = STAIR[1]
    h = (i + 1) * LEDGE[1] / NST
    def tread(x, y, s, t, z, wp, i=i):
        X, Y, Z = wp
        v = 2.4 + (wn(1, Z * 3, i) - 0.5) * 0.6 + (1.0 if (Z % 0.5) < 0.12 else 0)          # chequer-plate ribs
        return dust(shade(STEELB, v, X, Y, Z, UP, x, y), z)
    def riser(x, y, s, t, z, wp, i=i):
        X, Y, Z = wp
        if (X - STAIR[0]) / (STAIR[1] - STAIR[0]) * NST % 1 > 0.18: return dust(shade(STEELB, 0.7, X, Y, Z, FWD, x, y), z)   # under the stair: dark
        return dust(shade(STEELB, 1.8 + (0.8 if t > 0.88 else 0), X, Y, Z, FWD, x, y), z)
    rs.box(xa, xa + (STAIR[1] - STAIR[0]) / NST + 0.02, h - LEDGE[1] / NST, h, ZF - 1.7, ZF, riser, riser, top=tread)
# the stair's side stringer, a dark steel band along the steps' front edge
rs.quad((STAIR[0], -0.1, ZF - 1.72), (STAIR[1], LEDGE[1] - 0.6, ZF - 1.72), (STAIR[0], 0.5, ZF - 1.72),
        lambda x, y, s, t, z, wp: dust(shade(STEELB, 1.4 + (0.9 if t > 0.8 else 0), *wp, FWD, x, y), z))
# the dark under the stair
rs.quad((STAIR[0] + 0.6, 0, ZF - 0.05), (STAIR[1], 0, ZF - 0.05), (STAIR[0] + 0.6, LEDGE[0], ZF - 0.05),
        lambda x, y, s, t, z, wp: STEELB[0] if wp[1] < (wp[0] - STAIR[0]) / (STAIR[1] - STAIR[0]) * LEDGE[1] else None, cut=True)
rs.line3((STAIR[0] - 0.2, 3.2, ZF - 1.8), (STAIR[1] - 0.2, LEDGE[1] + 3.0, ZF - 1.8), lambda x, y, s, t, z, wp: tone(POLE, 3.0, x, y), w=0.2)
for k in range(4):
    px_ = STAIR[0] + 0.4 + k * 2.6
    rs.line3((px_, (px_ - STAIR[0]) / (STAIR[1] - STAIR[0]) * LEDGE[1] + 0.4, ZF - 1.8),
             (px_, (px_ - STAIR[0]) / (STAIR[1] - STAIR[0]) * LEDGE[1] + 3.1, ZF - 1.8), lambda x, y, s, t, z, wp: tone(POLE, 2.2, x, y), w=0.16)

# ---------------------------------------------------------------------------------------------------- the lower deck: benches, poles
def upholstery(n, v0=2.4):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        # moquette: a teal lattice on wine red, rubbed bald, slit, eaten by pale growth
        pat = ((X * 2.2) % 1 < 0.18) or (((Y + Z) * 2.2) % 1 < 0.18)
        c = shade(SEAT, v0 + (wn(1, X * 2.6, (Y + Z) * 2.6) - 0.5) * 0.7, X, Y, Z, n, x, y)
        if pat: c = mix(c, shade(SEAT2, v0, X, Y, Z, n, x, y), 0.35)
        bald = wn(2, X * 1.1, (Y + Z) * 1.1)
        if bald > 0.66: c = mix(c, tone(EARTH, 3.0, x, y), 0.45)
        if abs(math.sin(X * 1.3 + 2 * wn(3, X, Y + Z))) < 0.04 and wn(0, X * 0.6, 3) > 0.55: c = tone(FUNG, 3.6, x, y)  # foam in a slit
        g = growth_at(X, Y, Z)
        if g > 0: c = mix(c, tone(FUNG, 2.0 + g * 3.2 + (wn(3, X * 5, (Y + Z) * 5) - 0.5) * 1.4, x, y), min(1.0, g * 1.6))
        return dust(c, z)
    return sh


def growth_at(X, Y, Z):
    """how far the pale growth has eaten the cloth here: thick around her, patches on the left"""
    g = 0.0
    d = math.hypot(X - BODY[0], (Y - 1.5) * 1.5)
    g = max(g, 1.0 - d / 6.0)
    d2 = math.hypot(X + 12.5, (Y - 1.8) * 1.5)
    g = max(g, 0.8 - d2 / 4.0)
    g += (wn(0, X * 1.6, (Y + Z) * 1.6) - 0.5) * 0.9
    return max(0.0, g - 0.18)


BENCHES = [(-18.0, -3.2), (3.2, STAIR[0] - 0.4)]
for (bx0, bx1) in BENCHES:
    rs.box(bx0, bx1, 0.0, 1.4, ZF - 1.7, ZF, lambda x, y, s, t, z, wp: dust(shade(STEELB, 1.6, *wp, FWD, x, y), z),
           lambda x, y, s, t, z, wp: shade(STEELB, 2.0, *wp, RIGHT, x, y))
    rs.box(bx0, bx1, 1.4, 1.95, ZF - 1.85, ZF - 0.2, upholstery(FWD, 2.6), upholstery(RIGHT, 2.2), top=upholstery(UP, 3.2))
    rs.quad((bx0, 1.95, ZF - 0.3), (bx1, 1.95, ZF - 0.3), (bx0, 4.1, ZF - 0.05), upholstery((0, 0.3, -1), 2.8))
    for xx in (bx0, bx1):
        rs.line3((xx, 0.0, ZF - 1.75), (xx, LEDGE[0], ZF - 1.75), lambda x, y, s, t, z, wp: dust(tone(POLE, 2.4 + (1.2 if (wp or (0, 0, 0))[1] % 1.7 < 0.1 else 0) + (0.8 if (x % 3) == 0 else 0), x, y), z), w=0.2)

# the fungal clusters on the seats (caps on short stems, pale, the nearest ones faintly lit)
def clump(X, Y, Z, n, seed, glow=False):
    for k in range(n):
        a = h32(seed, k) % 360 * math.pi / 180
        r_ = 0.25 + (h32(seed, k, 2) % 10) * 0.08
        cx_, cz_ = X + math.cos(a) * r_ * 1.4, Z + math.sin(a) * r_ * 0.5
        hgt = 0.25 + (h32(seed, k, 3) % 6) * 0.1
        rs.line3((cx_, Y, cz_), (cx_ + 0.05, Y + hgt, cz_), lambda x, y, s, t, z, wp: tone(FUNG, 2.2 + t * 1.5, x, y), w=0.09)
        rad = 0.14 + (h32(seed, k, 4) % 5) * 0.035
        if glow and k % 3 == 0:
            rs.disc(cx_ + 0.05, Y + hgt + 0.04, cz_, rad, lambda x, y, s, t, z, wp: GREEN[3] if t < 0.1 else GREEN[2], cls='emit')
        else:
            rs.disc(cx_ + 0.05, Y + hgt + 0.04, cz_, rad, lambda x, y, s, t, z, wp: tone(FUNG, 4.6 - t * 2.6 - s * 0.6, x, y) if t < 0.45 else None)
clump(BODY[0] - 3.4, 1.95, ZF - 1.0, 9, 3, glow=True)
clump(BODY[0] + 3.0, 1.95, ZF - 0.9, 7, 4, glow=True)
clump(-12.4, 1.95, ZF - 1.0, 8, 5, glow=True)
clump(-6.4, 1.95, ZF - 0.8, 4, 6)
clump(13.8, 1.95, ZF - 0.7, 4, 7)

# bioluminescent patches: faint green blooms on the cloth and the spilled earth
for (gx, gy, gz, gr) in ((BODY[0] - 1.6, 2.6, ZF - 0.35, 0.55), (BODY[0] + 3.6, 3.0, ZF - 0.2, 0.4), (-12.6, 2.8, ZF - 0.3, 0.45),
                         (-14.6, 0.5, ZF - 2.6, 0.38), (BODY[0] - 3.8, 0.05, ZF - 2.2, 0.3)):
    rs.disc(gx, gy, gz, gr, lambda x, y, s, t, z, wp: (GREEN[3] if s * s + t * t < 0.18 else GREEN[2]) if (s * s + t * t) < 0.7 and h32(x, y, 3) % 3 else None, cls='emit')

# ---------------------------------------------------------------------------------------------------- the earth that broke in
#   one lower pane gave way: soil poured through it over the bench and fanned out on the floor (a talus slope)
EW = -14.4                                                                                    # the broken window's bay
def heap(cx, w, hmax, zc, seed, foot=False):
    """a heap of soil as a card facing the camera: an irregular dome silhouette, shaded as if rounded (light from the
    windows above and the door at the left), clods and stones in it"""
    def prof(u):
        return hmax * max(0.0, 1 - abs(u) ** 2.2) ** 0.8 * (0.88 + 0.24 * wn(0, (cx + u * w) * 1.1, seed))
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = (X - cx) / w
        hp = prof(u)
        if Y > hp or abs(u) > 1: return None
        dh = (prof(u + 0.02) - prof(u - 0.02)) / (0.04 * w)
        nx = -dh / math.sqrt(1 + dh * dh); ny = 1 - (Y / max(0.1, hp)) * 0.7
        bump = wn(1, X * 2.6, Y * 2.6 + seed) - 0.5
        v = 1.9 + 1.4 * ny + 0.6 * (-nx) + bump * 1.3 + (0.7 if hp - Y < 0.1 else 0)
        c = shade(EARTH, v, X, Y, Z, (nx * 0.6, 0.6, -0.5), x, y, k=2.4)
        if wn(3, X * 5.0, Y * 5.0 + seed) > 0.8: c = tone(EARTH, 4.6 + bump * 2, x, y)                     # a lighter clod
        if wn(2, X * 9.0, Y * 9.0 + seed) > 0.84: c = tone(STONE, 2.6, x, y)                                  # a stone
        return dust(c, z)
    rs.quad((cx - w, 0, zc), (cx + w, 0, zc), (cx - w, hmax * 1.3, zc), sh, cls='prop', cut=True)
heap(EW, 3.3, 4.6, ZF - 1.95, 3)           # poured over the bench from the broken pane
heap(EW + 0.4, 4.4, 1.9, ZF - 2.35, 5)     # slumped over the seat's edge
heap(EW + 1.0, 5.4, 0.7, ZF - 2.75, 7)     # fanned out on the floor
for k in range(4):                                                                            # roots hanging out of the hole
    rx = EW - 1.2 + k * 0.8
    rs.line3((rx, LWIN[1] - 0.4 - (k % 3) * 0.3, ZF + 0.1), (rx + (k % 2 - 0.5) * 0.6, LWIN[0] + 1.6 - (k % 3) * 0.4, ZF - 0.6),
             lambda x, y, s, t, z, wp: tone(EARTH, 2.4 + t, x, y), w=0.07, sag=-0.25)
for k in range(7):                                                                            # clods rolled further out
    cx_ = EW - 3.0 + (h32(k, 21) % 60) / 10.0; cz_ = ZF - 3.3 - (h32(k, 22) % 9) / 10.0; r_ = 0.18 + (h32(k, 23) % 5) * 0.06
    rs.disc(cx_, r_ * 0.6, cz_, r_, lambda x, y, s, t, z, wp: tone(EARTH, 3.0 - t * 1.6 - s * 0.5, x, y) if t < 0.55 else None)

# ---------------------------------------------------------------------------------------------------- the floor
def floor(x, y, s, t, z, wp):
    X, _, Z = wp
    # wooden slats along the bus with steel strips, worn grey down the aisle, dirt, leaves, flakes of rust
    pl = math.floor(Z / 0.42)
    v = 2.2 + (h32(pl, 1) % 3) * 0.3 + (wn(0, X * 0.4, Z * 3.0) - 0.5) * 0.8
    if (Z / 0.42) % 1 < 0.14: v -= 1.1
    if abs(Z - 9.4) < 0.08 or abs(Z - 12.0) < 0.08: return dust(shade(STEELB, 3.0, X, 0, Z, UP, x, y), z)
    if h32(int(X / 1.6), pl, 3) % 13 == 0: v -= 0.8                                  # a rotten slat
    c = shade(SLAT, v, X, 0, Z, UP, x, y, k=3.6)
    m = wn(2, X * 0.35, Z * 0.9)
    if m > 0.55: c = mix(c, tone(EARTH, 2.6 + (wn(3, X * 3, Z * 3) - 0.5) * 1.5, x, y), min(0.85, (m - 0.55) * 4))
    if X < -10 and m + (-10 - X) * 0.06 > 0.6: c = mix(c, tone(EARTH, 3.0, x, y), 0.6)      # earth trodden in from the door
    if h32(int(X * 6 + 999), int(Z * 6 + 999), 5) % 97 == 0: c = mix(c, tone(RUSTD, 2.2, x, y), 0.6)   # rust flakes
    if h32(int(X * 5 + 999), int(Z * 5 + 999), 6) % 131 == 0: c = mix(c, tone(WARM, 1.6, x, y), 0.6)  # a dead leaf
    return dust(c, z)
rs.quad((XL, 0, 3.0), (XR, 0, 3.0), (XL, 0, ZF), floor, cls='ground')
# fallen boards from the upper floor and a seat frame, near the walls
for k, (bx, bz, ln, ang) in enumerate(((-7.6, 12.0, 3.2, 0.1), (-1.2, 11.6, 2.4, -0.3), (17.2, 10.6, 2.2, 0.5), (-19.8, 10.8, 1.6, -0.2))):
    rs.box(bx, bx + ln, 0.0, 0.22, bz, bz + 0.5, lambda x, y, s, t, z, wp: shade(SLAT, 2.2, *wp, FWD, x, y),
           lambda x, y, s, t, z, wp: shade(SLAT, 1.6, *wp, RIGHT, x, y), top=lambda x, y, s, t, z, wp: shade(SLAT, 3.0 + (wn(0, wp[0] * 3, 1) - 0.5), *wp, UP, x, y))
rs.line3((19.4, 0.1, 11.0), (21.0, 1.6, 11.6), lambda x, y, s, t, z, wp: STEELB[3], w=0.14)
rs.line3((21.0, 1.6, 11.6), (22.4, 0.1, 11.2), lambda x, y, s, t, z, wp: STEELB[2], w=0.14)

def beam(col):
    """the grey shaft from the torn roof down onto where she lies: a faint additive column, dusty"""
    (hx, hy) = proj(HOLE[0], roof_h(HOLE[1]), HOLE[1]); (bx, by) = proj(BODY[0] + 0.5, 0.0, BODY[1] + 0.6)
    for y in range(int(hy), int(by)):
        t = (y - hy) / (by - hy)
        cx_ = hx + (bx - hx) * t; half = 16 + 46 * t
        for x in range(int(cx_ - half - 4), int(cx_ + half + 5)):
            if not (0 <= x < W): continue
            d = abs(x - cx_) / half
            if d > 1.15: continue
            a = 0.3 * (1 - min(1.0, d) ** 2) * (0.6 + 0.4 * math.sin(t * math.pi * 0.9)) * (0.75 + 0.5 * wn(1, x * 0.02, y * 0.11))
            if (x + y) % 2 and a < 0.05: continue
            if d < 0.8 and h32(x, y, 77) % 173 == 0: a = 0.85                              # dust hanging in the light
            c = col[y][x]
            col[y][x] = tuple(min(255, int(c[i] + (DAYC[i] - c[i] * 0.4) * a)) for i in range(3))
    # where it lands: a soft lit ellipse on the floor and the bench front round her
    (px_, py_) = proj(POOL[0], 0.0, POOL[1])
    for y in range(int(py_ - 60), int(py_ + 26)):
        for x in range(int(px_ - 150), int(px_ + 150)):
            if not (0 <= x < W and 0 <= y < H): continue
            d = ((x - px_) / 140.0) ** 2 + ((y - py_) / (22.0 if y > py_ else 58.0)) ** 2
            if d > 1: continue
            a = 0.16 * (1 - d) ** 1.5
            if (x + y) % 2 and a < 0.03: continue
            c = col[y][x]
            col[y][x] = tuple(min(255, int(c[i] + (DAYC[i] - c[i] * 0.35) * a)) for i in range(3))


img = rs.render((6, 8, 7), overlay=beam, fog=lambda z: 0.0, light_gain=0.3, grime_gain=0.7, bloom=0.3, stain_gain=0.35, damp_gain=0.35)
img.save(f'{OUT}/bus.png')

# hot spots (canvas)
def P(X, Y, Z): return tuple(int(round(v)) for v in proj(X, Y, Z))
print('walk line depth', 2400 / 238)
print('front door x', P(FDOOR[0], 0, ZF)[0], P(FDOOR[1], 0, ZF)[0], 'y', P(FDOOR[0], FDOOR[2], ZF)[1], P(FDOOR[0], 0, ZF)[1])
print('body', P(BODY[0], 0, BODY[1]), 'scale px/unit', F2 / BODY[1])
print('hole', P(HOLE[0], 15, HOLE[1]))
g = img.copy(); gp = g.load()
for y in range(600):
    for x in range(1067):
        if x % 50 == 0 or y % 50 == 0: gp[x, y] = (255, 0, 255) if (x % 100 == 0 or y % 100 == 0) else (120, 0, 120)
g.save(f'{OUT}/bus_guides.png')
print('done bus')
