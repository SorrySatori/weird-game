"""The Scraper's lobby (ScraperInteriorScene) -- what is left of the Nexicorp Tower's art-deco entrance hall, 1067x600,
the shared camera (raster3d.py). After the old AI picture: the Lift-Mother's arched bronze portal in the middle of the
back wall (a mask with closed eyes on its doors, an arc of amber floor lamps, LIFT-MOTHER in brass letters over it),
the SCRAPER 1140 enamel plaque on the right with the panelled door to the backyard under it, the staircase up to the
upper floors rising along the back wall on the left. New for the walkable room: the street doors in the left wall
(overcast daylight in their glass = "Return Outside"), a deserted concierge desk with pigeonholes on the right, a
cracked marble checker floor with a faded runner from the doors to the lift, a coffered ceiling with a half-dead
chandelier, moss hanging from the cornice, two dead palms in brass pots by the lift.

    python3 lobby_bg.py <outdir>   ->  lobby.png  (= assets/images/backgrounds/Scraper_interior.png); prints the hot spots
"""
import sys, math
from common import h32, FONT
from shedkit import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = Raster()
WX, CH, ZB = 26.0, 22.0, 26.0
LIFT_X, LIFT_W, LIFT_H = -2.0, 3.5, 10.5          # portal centre, half-width, spring of the arch
PLAQUE = (7.5, 17.5, 11.0, 15.0)                  # x0, x1, y0, y1 on the back wall
BDOOR = (10.0, 15.0, 7.6)                         # the backyard door: x0, x1, height
EDOOR = (15.6, 21.4, 9.6)                         # the street doors in the left wall: z0, z1, height

MARB1 = ramp('#0c0e0a #13160f #1a1e15 #22271b #2b3123 #353c2b #404834')
MARB2 = ramp('#191710 #221f16 #2c281c #373223 #423c2a #4f4733')
BRASS = ramp('#241b0e #3a2c17 #554122 #725830 #927040 #b48e56 #d4b072')
WALLP = ramp('#101209 #171a10 #1f2316 #282d1d #313725 #3c432e #485038')
WOODD = ramp('#120c07 #1b130b #261b10 #322416 #3f2d1b #4d3822')
MOSSR = ramp('#0f160a #17220e #213013 #2b3f19 #374f20')
RUG = ramp('#1e0c0a #2e1410 #3f1c16 #52261d #643126')
ENAM = ramp('#0a1610 #102218 #173022 #1f3e2c')
GLASS = ramp('#4c5850 #5c6a60 #6e7c70 #808e80 #93a090')
AMBER, AMBER2 = (255, 196, 104), (214, 140, 58)

LIGHTS = [((LIFT_X, 13.0, ZB - 0.5), 0.55, 7.0, 'w'),      # the lift's lamp arc
          ((-1.0, 17.4, 14.0), 0.55, 15.0, 'w'),           # the chandelier (half its bulbs)
          ((-WX + 0.2, 5.0, 18.5), 0.75, 9.0, 'c'),        # daylight through the street doors
          ((18.0, 4.6, 19.0), 0.35, 5.0, 'w')]             # the desk lamp


def lit(X, Y, Z, n):
    w = c = 0.0
    for (lx, ly, lz), I, r, kind in LIGHTS:
        dx, dy, dz = lx - X, ly - Y, lz - Z
        d2 = dx * dx + dy * dy + dz * dz; d = math.sqrt(d2) + 1e-6
        ndl = max(0.0, (dx * n[0] + dy * n[1] + dz * n[2]) / d)
        v = I * (0.3 + 0.7 * ndl) * r * r / (r * r + d2)
        if kind == 'w': w += v
        else: c += v
    return w, c


def shade(r, base, X, Y, Z, n, x, y, k=5.0):
    w, c = lit(X, Y, Z, n)
    col = tone(r, base - 0.55 + 1.25 * k * (w + c), x, y)
    if w > 0.05: col = mix(col, AMBER2, min(0.22, w * 0.3))
    if c > 0.05 and r is not RUG: col = mix(col, (150, 172, 160), min(0.22, c * 0.28))
    return col


# ---------------------------------------------------------------------------------------------------- the shell
def on_rug(X, Z):
    return (17.2 <= Z <= 19.8 and X <= -3.2) or (-4.8 <= X <= 0.8 and Z >= 17.2)


def floor_sh(x, y, s, t, z, wp):
    X, _, Z = wp
    n = (0, 1, 0)
    if on_rug(X, Z):
        edge = min(abs(Z - 17.2), abs(Z - 19.8)) if X <= -3.2 and Z < 19.8 else min(abs(X + 4.8), abs(X - 0.8))
        v = 1.2 + (wn(1, X * 2, Z * 2) - 0.5) * 0.8
        if 0.25 < edge < 0.45: v += 1.0                                                          # the border stripe
        if wn(3, X * 0.6, Z * 0.6) > 0.7: v -= 0.6                                               # worn bald
        if edge < 0.08 and h32(int(X * 20), int(Z * 20)) % 3 == 0: return shade(MARB1, 0.8, X, 0, Z, n, x, y)   # fraying
        return shade(RUG, v, X, 0, Z, n, x, y, 3.0)
    if abs(abs(X) - 22.5) < 0.18 or abs(Z - 24.2) < 0.18 * (z / 20): return shade(BRASS, 1.2, X, 0, Z, n, x, y, 3.0)   # brass inlay
    i, j = math.floor(X / 2.6), math.floor(Z / 2.6)
    r_ = MARB1 if (i + j) % 2 else MARB2
    v = 1.4 + (wn(0, X * 0.8, Z * 0.8) - 0.5) * 0.9
    vein = wn(2, X * 0.9 + i * 3, Z * 0.9)
    if abs(vein - 0.5) < 0.02: v += 0.9                                                          # marble veining
    fu, fv = (X / 2.6) % 1, (Z / 2.6) % 1
    if fu < 0.6 * z / F / 2.6 + 0.01 or fv < 0.6 * z * z / (F * CAMH) / 2.6 + 0.01: v -= 0.8
    cr = wn(1, X * 1.1 + i * 7, Z * 1.1)
    if abs(cr - 0.5) < 0.01 * (1 + z / 25):                                                     # cracks with moss in them
        return shade(MOSSR, 1.4, X, 0, Z, n, x, y, 3.0)
    if wn(3, X * 0.3 + 9, Z * 0.3) > 0.7: v -= 0.5                                               # grime
    return shade(r_, v, X, 0, Z, n, x, y, 4.0)
rs.quad((-WX, 0, 3), (WX, 0, 3), (-WX, 0, ZB), floor_sh, cls='ground')


def wall_base(X, Y, Z, n, x, y, along):
    """dark wood wainscot, fluted olive panels above, a cornice, damp"""
    if Y < 4.2:
        if Y > 3.95: return shade(WOODD, 3.2, X, Y, Z, n, x, y, 3.0)                            # the dado rail
        if Y < 0.5: return shade(WOODD, 0.8, X, Y, Z, n, x, y, 2.0)
        pu = (along / 2.2) % 1
        v = 1.8 + (0.9 if pu < 0.06 or pu > 0.94 else 0) + (wn(1, along * 3, Y * 0.5) - 0.5) * 0.6
        if 0.12 < pu < 0.88 and 0.9 < Y < 3.4 and (pu < 0.16 or pu > 0.84 or Y < 1.0 or Y > 3.3): v += 0.7   # panel mouldings
        return shade(WOODD, v, X, Y, Z, n, x, y, 3.0)
    if Y > CH - 2.4:                                                                             # the cornice
        v = 2.0 + (1.2 if (Y - (CH - 2.4)) % 0.6 < 0.2 else 0)
        return shade(WALLP, v, X, Y, Z, n, x, y)
    pil = (along / 6.0) % 1
    if pil < 0.12:                                                                               # fluted pilasters
        v = 2.2 + (0.8 if int(pil / 0.12 * 4) % 2 else 0)
        return shade(WALLP, v, X, Y, Z, n, x, y)
    v = 1.5 + (wn(0, along * 0.5, Y * 0.5) - 0.5) * 0.8
    if wn(2, along * 0.8, Y * 0.1) > 0.66: v -= 0.7                                              # damp running down
    return shade(WALLP, v, X, Y, Z, n, x, y)


def back(x, y, s, t, z, wp):
    X, Y, Z = wp
    n = (0, 0, -1)
    dx = X - LIFT_X
    # the Lift-Mother: an arched portal, bronze leaves with a mask, the tympanum grille
    r_out, r_in = LIFT_W + 0.9, LIFT_W
    arch_out = abs(dx) <= r_out and (Y <= LIFT_H or math.hypot(dx, Y - LIFT_H) <= r_out)
    if arch_out and Y >= 0:
        inside = abs(dx) <= r_in and (Y <= LIFT_H or math.hypot(dx, Y - LIFT_H) <= r_in)
        if not inside:                                                                          # the fluted frame
            rr = max(abs(dx), math.hypot(dx, Y - LIFT_H) if Y > LIFT_H else abs(dx))
            v = 2.2 + (1.4 if (rr - r_in) / 0.9 < 0.3 else 0) + (0.8 if int((rr - r_in) / 0.9 * 4) % 2 else 0)
            return shade(BRASS, v, X, Y, Z, n, x, y, 3.0)
        if Y > 9.2:                                                                             # the tympanum: a fan grille
            a = math.atan2(Y - LIFT_H + 1.3, dx)
            if int(a / math.pi * 14) % 2 == 0 or math.hypot(dx, Y - LIFT_H + 1.3) < 1.0: return shade(BRASS, 1.8, X, Y, Z, n, x, y, 3.0)
            return (10, 10, 7)
        if abs(dx) < 0.06: return BRASS[0]                                                      # the leaves meet
        if Y > 9.0: return shade(BRASS, 2.6, X, Y, Z, n, x, y, 3.0)
        # the mask (eyes closed) in low relief across both leaves
        fx, fy = dx / 1.9, (Y - 6.4) / 2.6
        d = fx * fx + fy * fy
        v = 1.6 + (wn(1, X * 2, Y * 2) - 0.5) * 0.5
        if d < 1.0:
            v += 0.6
            if d > 0.86: v += 1.4                                                               # the rim catches the light
            for ex in (-0.85, 0.85):                                                            # closed lids
                if abs(dx - ex) < 0.55 and abs((Y - 7.25) + 0.35 * ((dx - ex) / 0.55) ** 2) < 0.07: v = 4.6
            if abs(dx) < 0.18 and 5.5 < Y < 7.2: v += 1.2                                       # the nose
            if abs(dx) < 0.36 and 5.35 < Y < 5.6: v += 1.4
            if abs(dx) < 0.55 and abs(Y - 4.75) < 0.06: v = 0.6                                 # the mouth
        if abs(Y - 2.0) < 0.05 or abs(Y - 9.0) < 0.06: v += 1.0
        return shade(BRASS, v, X, Y, Z, n, x, y, 3.0)
    # the arc of floor lamps over the portal (a brass bar, the bulbs are drawn as emissive discs)
    rr = math.hypot(dx, Y - LIFT_H)
    if Y > LIFT_H and abs(rr - (r_out + 0.55)) < 0.12: return shade(BRASS, 2.8, X, Y, Z, n, x, y, 3.0)
    if LIFT_X + LIFT_W + 1.3 < X < LIFT_X + LIFT_W + 1.9 and 3.3 < Y < 4.9:                  # the call panel
        if abs(Y - 4.3) < 0.18 and abs(X - (LIFT_X + LIFT_W + 1.6)) < 0.14: return AMBER
        return shade(BRASS, 2.4, X, Y, Z, n, x, y, 3.0)
    # the SCRAPER 1140 plaque
    x0, x1, y0, y1 = PLAQUE
    if x0 <= X <= x1 and y0 <= Y <= y1:
        if X < x0 + 0.35 or X > x1 - 0.35 or Y < y0 + 0.35 or Y > y1 - 0.35:
            return shade(BRASS, 2.4 + (1.2 if Y > y1 - 0.15 or X < x0 + 0.12 else 0), X, Y, Z, n, x, y, 3.0)
        return shade(ENAM, 1.2 + (wn(1, X * 3, Y * 3) - 0.5) * 0.6, X, Y, Z, n, x, y, 2.0)
    # the backyard door
    bx0, bx1, bh = BDOOR
    if bx0 - 0.4 <= X <= bx1 + 0.4 and Y <= bh + 0.4:
        if X < bx0 or X > bx1 or Y > bh: return shade(WOODD, 3.0, X, Y, Z, n, x, y, 3.0)      # the architrave
        pu, pv = (X - bx0) / (bx1 - bx0), Y / bh
        v = 1.8
        for (u0, u1, v0, v1) in ((0.12, 0.45, 0.55, 0.9), (0.55, 0.88, 0.55, 0.9), (0.12, 0.45, 0.1, 0.45), (0.55, 0.88, 0.1, 0.45)):
            if u0 < pu < u1 and v0 < pv < v1:
                v = 1.3 + (0.9 if (pu < u0 + 0.03 or pv > v1 - 0.03) else 0)
        if abs(pu - 0.86) < 0.03 and abs(Y - 3.6) < 0.18: return BRASS[5]                       # the knob
        return shade(WOODD, v, X, Y, Z, n, x, y, 3.0)
    # the archway up from the stair landing (dark)
    if -25.0 < X < -21.0 and 10.0 < Y < 16.8 and (Y < 15.0 or math.hypot(X + 23.0, Y - 15.0) < 2.0):
        return (6, 7, 5)
    return wall_base(X, Y, Z, n, x, y, X)


def lwall(x, y, s, t, z, wp):
    X, Y, Z = wp
    n = (1, 0, 0)
    z0, z1, h = EDOOR
    if z0 - 0.5 <= Z <= z1 + 0.5 and Y <= h + 2.6:
        if Z < z0 or Z > z1 or (h < Y < h + 0.4): return shade(BRASS, 2.4, X, Y, Z, n, x, y, 3.0)       # the frame
        mid = (z0 + z1) / 2
        if Y > h + 0.4:                                                                          # the sunburst transom
            a = math.atan2(Y - h - 0.4, Z - mid)
            if int(a / math.pi * 12) % 2 == 0: return shade(BRASS, 2.0, X, Y, Z, n, x, y, 3.0)
            return tone(GLASS, 2.4, x, y)
        if abs(Z - mid) < 0.12 or Y < 1.2 or abs(Y - 5.6) < 0.1: return shade(BRASS, 2.6, X, Y, Z, n, x, y, 3.0)
        lz = (Z - z0) % ((z1 - z0) / 2)
        if lz < 0.25 or lz > (z1 - z0) / 2 - 0.25: return shade(BRASS, 2.2, X, Y, Z, n, x, y, 3.0)
        v = 1.4 + Y * 0.17 + (wn(1, Z * 4, Y * 0.4) - 0.5) * 0.9 - (0.9 if wn(3, Z * 3, Y * 0.25) > 0.66 else 0)   # streaked panes
        if Y < 2.4: v -= 0.6
        return tone(GLASS, v, x, y)
    return wall_base(X, Y, Z, n, x, y, Z)


def rwall(x, y, s, t, z, wp):
    X, Y, Z = wp
    n = (-1, 0, 0)
    if 15.4 < Z < 22.6 and 4.6 < Y < 9.8:                                                       # pigeonholes behind the desk
        cu, cv = ((Z - 15.4) / 0.9) % 1, ((Y - 4.6) / 0.86) % 1
        if cu < 0.12 or cv < 0.12: return shade(WOODD, 2.6, X, Y, Z, n, x, y, 3.0)
        k = h32(int((Z - 15.4) / 0.9), int((Y - 4.6) / 0.86), 5)
        if k % 3 == 0 and cv < 0.6: return tone(BONE, 2.2 + (k % 2), x, y)                     # letters nobody collected
        return shade(WOODD, 0.4, X, Y, Z, n, x, y, 2.0)
    return wall_base(X, Y, Z, n, x, y, -Z)


rs.quad((-WX, 0, 1.0), (-WX, 0, ZB), (-WX, CH, 1.0), lwall, cls='wall')
rs.quad((WX, 0, 1.0), (WX, 0, ZB), (WX, CH, 1.0), rwall, cls='wall')
rs.quad((-WX, 0, ZB), (WX, 0, ZB), (-WX, CH, ZB), back, cls='wall')


def ceil_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    cu, cv = (X / 4.0) % 1, (Z / 4.0) % 1
    v = 0.9 + (wn(0, X * 0.5, Z * 0.5) - 0.5) * 0.6
    if cu < 0.14 or cv < 0.14: v += 0.8                                                         # the coffer ribs
    elif 0.2 < cu < 0.8 and 0.2 < cv < 0.8: v -= 0.4
    if wn(2, X * 0.25, Z * 0.25) > 0.68: v -= 0.5
    return shade(WALLP, v, X, Y, Z, (0, -1, 0), x, y, 3.0)
rs.quad((-WX, CH, 0.8), (WX, CH, 0.8), (-WX, CH, ZB), ceil_sh, cls='ceil')

# ---------------------------------------------------------------------------------------------------- the stair
STEPS = 16
for k in range(STEPS):
    xr = -8.0 - k * 1.0; xl = xr - 1.0; h = 0.6 * (k + 1)
    def tread(x, y, s, t, z, wp, h=h):
        return shade(MARB2, 2.2 + (1.0 if s > 0.92 else 0), wp[0], wp[1], wp[2], (0, 1, 0), x, y, 3.0)
    def riser(x, y, s, t, z, wp):
        return shade(WOODD, 1.6, wp[0], wp[1], wp[2], (1, 0, 0), x, y, 3.0)
    def string(x, y, s, t, z, wp):
        return shade(WALLP, 1.8 + (0.8 if t > 0.92 else 0), wp[0], wp[1], wp[2], (0, 0, -1), x, y, 3.0)
    rs.box(xl, xr, 0, h, 22.6, ZB - 0.01, string, riser, top=tread, cls='prop')
rs.box(-WX + 0.01, -24.0, 0, 9.6, 22.6, ZB - 0.01, lambda x, y, s, t, z, wp: shade(WALLP, 1.6, wp[0], wp[1], wp[2], (0, 0, -1), x, y, 3.0),
       lambda x, y, s, t, z, wp: shade(WALLP, 1.4, wp[0], wp[1], wp[2], (1, 0, 0), x, y, 3.0),
       top=lambda x, y, s, t, z, wp: shade(MARB2, 2.0, wp[0], wp[1], wp[2], (0, 1, 0), x, y, 3.0), cls='prop')     # the landing
def rail(x, y, s, t, z, wp): return shade(BRASS, 2.6 + (1.4 if y % 3 == 0 else 0), wp[0], wp[1], wp[2], (0, 1, -0.3), x, y, 3.0)
rs.line3((-7.6, 3.6, 22.7), (-24.0, 3.6 + 9.6, 22.7), rail, w=0.18)
rs.line3((-24.0, 13.2, 22.7), (-24.0, 13.2, 25.8), rail, w=0.18)
for k in range(0, STEPS + 1, 1):
    bx = -7.7 - k * 1.0; bh = 0.6 * k
    rs.line3((bx, bh, 22.75), (bx, bh + 3.6 - 0.3, 22.75), lambda x, y, s, t, z, wp: shade(BRASS, 1.8, wp[0], wp[1], wp[2], (0, 0, -1), x, y, 3.0), w=0.07 if k % 4 else 0.16)
rs.line3((-7.6, 0, 22.7), (-7.6, 4.2, 22.7), rail, w=0.32)                                   # the newel post

# ---------------------------------------------------------------------------------------------------- the concierge desk
def desk_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    if t > 0.92: return shade(BRASS, 3.0, X, Y, Z, (0, 0.5, -1), x, y, 3.0)
    v = 1.8 + (0.9 if (s * 6) % 1 < 0.08 else 0) + (wn(1, X * 2, Y * 2) - 0.5) * 0.5
    return shade(WOODD, v, X, Y, Z, (0, 0, -1), x, y, 3.0)
def desk_side(x, y, s, t, z, wp): return shade(WOODD, 1.4 + (1.0 if t > 0.92 else 0), wp[0], wp[1], wp[2], (-1, 0, 0), x, y, 3.0)
def desk_top(x, y, s, t, z, wp): return shade(MARB1, 2.6 + (wn(0, wp[0] * 2, wp[2] * 2) - 0.5) * 0.8, wp[0], wp[1], wp[2], (0, 1, 0), x, y, 3.0)
rs.box(15.5, 22.4, 0, 3.7, 17.6, 20.8, desk_front, desk_side, top=desk_top, cls='prop')
rs.line3((17.4, 3.7, 19.4), (17.6, 5.2, 19.6), lambda x, y, s, t, z, wp: BRASS[3], w=0.1)          # the banker's lamp
rs.disc(17.8, 5.2, 19.5, 0.55, lambda x, y, s, t, z, wp: (36, 92, 52) if t > -0.1 else AMBER, cls='emit')
rs.disc(20.2, 3.9, 18.6, 0.28, lambda x, y, s, t, z, wp: BRASS[5] if t > 0.2 else BRASS[3])     # the bell
for k in range(4):                                                                              # a ledger and loose sheets
    rs.quad((16.2 + k * 0.5, 3.72, 18.0 + k * 0.3), (17.0 + k * 0.5, 3.72, 18.0 + k * 0.3), (16.2 + k * 0.5, 3.72, 18.6 + k * 0.3),
            lambda x, y, s, t, z, wp: tone(BONE, 2.6 + (x + y) % 2, x, y), cls='prop')

# ---------------------------------------------------------------------------------------------------- palms, chandelier, moss
POT = lambda x, y, s, t, z, wp: shade(BRASS, 2.0 + 1.6 * max(0.0, s - 0.55), wp[0], wp[1], wp[2], (0, 0, -1), x, y, 3.0)
for px_ in (LIFT_X - 6.4, LIFT_X + 6.8):
    rs.box(px_ - 0.9, px_ + 0.9, 0, 2.2, ZB - 2.6, ZB - 0.9, POT, POT, top=lambda x, y, s, t, z, wp: (14, 12, 8), cls='prop')
    for k in range(7):                                                                          # dead fronds, drooping
        a = k / 7 * 2 * math.pi + px_
        ex, ez = px_ + math.cos(a) * 2.4, ZB - 1.75 + math.sin(a) * 1.2
        rs.line3((px_, 2.2, ZB - 1.75), (px_ + math.cos(a) * 0.8, 5.6 + (k % 3) * 0.7, ZB - 1.75 + math.sin(a) * 0.4),
                 lambda x, y, s, t, z, wp: tone(OCHRE, 1.4 + (x % 2), x, y), w=0.09)
        rs.line3((px_ + math.cos(a) * 0.8, 5.6 + (k % 3) * 0.7, ZB - 1.75 + math.sin(a) * 0.4), (ex, 3.4 + (k % 2), ez),
                 lambda x, y, s, t, z, wp: tone(OCHRE, 1.8 + (y % 2), x, y), w=0.22, sag=0.4)

CX_, CZ_ = -1.0, 14.0                                                                           # the chandelier
rs.line3((CX_, CH, CZ_), (CX_, 18.6, CZ_), lambda x, y, s, t, z, wp: BRASS[2], w=0.08)
for k in range(8):
    a = k / 8 * 2 * math.pi
    bx, bz = CX_ + math.cos(a) * 2.2, CZ_ + math.sin(a) * 1.1
    rs.line3((CX_, 18.4, CZ_), (bx, 17.4, bz), lambda x, y, s, t, z, wp: BRASS[3], w=0.07)
    on = k % 3 != 1
    rs.disc(bx, 17.2, bz, 0.26, (lambda x, y, s, t, z, wp: AMBER if math.hypot(s, t) < 0.6 else AMBER2) if on else
            (lambda x, y, s, t, z, wp: (30, 26, 18)), cls='emit' if on else 'prop')
rs.disc(CX_, 18.2, CZ_, 0.5, lambda x, y, s, t, z, wp: BRASS[4] if t > 0 else BRASS[2])

for k in range(30):                                                                             # moss from the cornice
    side = k % 3
    if side == 0: px_, pz = -WX + 0.15, 4.0 + (h32(k, 3) % 210) / 10.0
    elif side == 1: px_, pz = WX - 0.15, 4.0 + (h32(k, 3) % 210) / 10.0
    else: px_, pz = -WX + (h32(k, 4) % 520) / 10.0, ZB - 0.15
    ln = 1.5 + (h32(k, 5) % 50) / 10.0
    rs.line3((px_, CH - 2.4, pz), (px_ + (h32(k, 6) % 3 - 1) * 0.4, CH - 2.4 - ln, pz),
             lambda x, y, s, t, z, wp: tone(MOSSR, 1.2 + (y % 3) * 0.6, x, y), w=0.12 + (k % 3) * 0.05)

for k in range(18):                                                                             # plaster fallen from the coffers
    fx, fz = -16 + (h32(k, 41) % 300) / 10.0, 12.5 + (h32(k, 42) % 110) / 10.0
    if on_rug(fx, fz): continue
    sz = 0.15 + (h32(k, 43) % 4) / 10.0
    rs.box(fx - sz, fx + sz, 0, sz * 0.6, fz - sz, fz + sz, lambda x, y, s, t, z, wp: tone(WALLP, 3.0 + (x % 2), x, y),
           lambda x, y, s, t, z, wp: tone(WALLP, 2.0, x, y), top=lambda x, y, s, t, z, wp: tone(WALLP, 3.6, x, y), cls='prop')

# the lamp bulbs on the arc over the portal
for k in range(9):
    a = math.radians(18 + k * 18)
    bx, by = LIFT_X + math.cos(a) * (LIFT_W + 1.45), LIFT_H + math.sin(a) * (LIFT_W + 1.45)
    rs.disc(bx, by, ZB - 0.15, 0.24, lambda x, y, s, t, z, wp: AMBER if math.hypot(s, t) < 0.55 else AMBER2, cls='emit')


def letters(col):
    def text(txt, X0, X1, Y, sc, c1, c2):
        (ax, ay) = proj(X0, Y, ZB); (bx, by) = proj(X1, Y, ZB)
        tw = sum(len(FONT[ch][0]) * sc + sc for ch in txt) - sc
        x0 = int((ax + bx) / 2 - tw / 2); y0 = int(ay - 2.5 * sc)
        for ch in txt:
            for r, row in enumerate(FONT[ch]):
                for c_, bit in enumerate(row):
                    if bit != '1': continue
                    for dy in range(sc):
                        for dx in range(sc):
                            x, y = x0 + c_ * sc + dx, y0 + r * sc + dy
                            col[y][x] = c1 if (dy == 0 or dx == 0) else c2
            x0 += len(FONT[ch][0]) * sc + sc
    text('LIFT-MOTHER', LIFT_X - 4, LIFT_X + 4, 15.9, 2, (196, 166, 98), (140, 112, 60))
    x0, x1, y0, y1 = PLAQUE
    text('SCRAPER', x0, x1, y0 + (y1 - y0) * 0.72, 2, (208, 186, 120), (160, 136, 80))
    text('1140', x0, x1, y0 + (y1 - y0) * 0.3, 2, (208, 186, 120), (160, 136, 80))
FONT['-'] = ['000', '000', '111', '000', '000']

img = rs.render(INK, overlay=letters, light_gain=1.0, grime_gain=0.7, bloom=0.5, stain_gain=0.3, damp_gain=0.3)
img.save(f'{OUT}/lobby.png')
lx, ly = proj(LIFT_X, 5.5, ZB)
print('lift centre', round(lx), round(ly), 'portal', [round(proj(LIFT_X - LIFT_W - 0.9, 0, ZB)[0]), round(proj(LIFT_X + LIFT_W + 0.9, 0, ZB)[0])],
      'top', round(proj(0, LIFT_H + LIFT_W + 0.9, ZB)[1]), 'floor', round(proj(0, 0, ZB)[1]))
print('backyard door x', [round(proj(BDOOR[0], 0, ZB)[0]), round(proj(BDOOR[1], 0, ZB)[0])], 'y', [round(proj(0, BDOOR[2], ZB)[1]), round(proj(0, 0, ZB)[1])])
print('street doors x', [round(proj(-WX, 0, EDOOR[0])[0]), round(proj(-WX, 0, EDOOR[1])[0])], 'y top', round(proj(0, EDOOR[2], EDOOR[0])[1]),
      'sill', round(proj(0, 0, EDOOR[0])[1]))
