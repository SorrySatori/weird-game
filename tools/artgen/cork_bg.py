"""The Screaming Cork from the street (ScreamingCorkScene), 1067x600, overcast day, the shared camera (raster3d.py).
After the old art (ScreamingCork.png): the oldest timber building in the city -- "the first one raised after the
Collapse" -- seen from close by across the pavement. In the middle the main block: board-and-batten on a rubble plinth,
the double door under a corrugated awning, warm café-curtained windows either side, half-sunk basement windows glowing
red (the club below), the big board with the name in old, peeling orange paint, a top storey with a stepped false
front. Left of it the taller, older tower (clapboard) with a vent pipe bent into a U on its roof and a dark archway
through its ground floor -- the way back to Burning Bear Street; right the lower wing stepping forward with the arched
side door, its own U-pipe and vent stacks. Off the main block's corner hangs the pub sign: a carved cork, screaming,
a corkscrew driven into its top. Flagstones and a strip of setts with puddles in front; hazy roofs, a chimney and the
Scraper behind.

    python3 cork_bg.py <outdir>   ->  cork.png
Fixed points (canvas): the tavern door centred on x 533 (x ~486..580, sill y ~485); the name board x ~362..704,
y ~183..299 (the scene's observable); the archway x ~15..103 (the exit left); Edgar left of the door, feet y 522;
the walk line y 534 runs along the pavement."""
import sys, os, math
from PIL import Image, ImageDraw, ImageFont
from common import h32, draw_text, text_width
from shedkit import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = Raster()
ZF, ZL, ZR = 19.0, 22.0, 17.2                     # the main facade, the left tower, the right wing
CURB = 14.4                                       # the kerb: the walk line (z 15) runs along the pavement
PAINT = ramp('#4e2410 #6e3414 #8e4a1c #ac6026 #c27a32 #d49446')    # the old orange sign paint
CORK = ramp('#2a2016 #42331f #5c4a2e #76603c #8e774c #a48d60 #b8a276')
WINE = (92, 28, 40)

# ---------------------------------------------------------------------------------------------------- sky, ground
rs.quad((-1400, 800, 600), (1400, 800, 600), (-1400, -300, 600), sky, cls='sky')
def puddle(X, Z):
    if CURB - 0.3 < Z < CURB + 0.6 or Z > ZF - 0.5: return 0.0
    m = wn(2, X * 0.2 + 7.0, Z * 0.32) + (wn(3, X * 1.3, Z * 1.3) - 0.5) * 0.1 - (0.08 if Z > CURB else 0)
    return max(0.0, min(1.0, (m - 0.66) * 11))
def street(x, y, s, t, z, wp):
    c = setts(x, y, s, t, z, wp, v0=4.4, mud=-0.04)
    X, _, Z = wp
    if CURB - 1.2 < Z < CURB:                                                       # the gutter along the kerb
        c = mix(c, (18, 24, 22), 0.35 * (1 - (CURB - Z) / 1.2))
    p_ = puddle(X, Z)
    return mix(c, (20, 28, 26), p_ * 0.35) if p_ else c
rs.quad((-90, 0, 3), (90, 0, 3), (-90, 0, CURB), street, cls='ground')
def pavement(x, y, s, t, z, wp):
    """big worn flagstones, cracked; the kerbstones at the front"""
    X, Y, Z = wp
    if Z < CURB + 0.45: return fogged(tone(STONE, 6.2 - (Z - CURB) * 2 + (wn(1, X * 2, 3) - 0.5), x, y), z)
    row = math.floor((Z - CURB) / 1.5); colw = 2.2 + (h32(row, 3) % 3) * 0.3
    col = math.floor(X / colw + row * 0.37)
    fx = (X / colw + row * 0.37) - col; fz = (Z - CURB) / 1.5 - row
    v = 4.8 + (h32(col, row, 4) % 3) * 0.35 - (0.6 if h32(col, row, 5) % 6 == 0 else 0) + (wn(0, X * 1.5, Z * 1.5) - 0.5) * 0.7
    if fx < 0.9 * z / F / colw + 0.02 or fz < 1.1 * z * z / (F * CAMH) / 1.5 + 0.02: v = 2.6
    if h32(col, row, 6) % 7 == 0 and abs((fx - 0.3) - (fz - 0.2) * 0.8) < 0.03: v = 2.8                      # a crack
    c = tone(STONE, v, x, y)
    p_ = puddle(X, Z)
    return fogged(mix(c, (20, 28, 26), p_ * 0.35) if p_ else c, z)
rs.quad((-90, 0.3, CURB), (90, 0.3, CURB), (-90, 0.3, 40), pavement, cls='ground')
rs.quad((-90, 0, CURB), (90, 0, CURB), (-90, 0.3, CURB), lambda x, y, s, t, z, wp: fogged(tone(STONE, 3.4 + t * 2, x, y), z), cls='ground')

# ---------------------------------------------------------------------------------------------------- behind: roofs, a chimney, the Scraper
rs.quad((270, 0, 230), (300, 0, 230), (270, 330, 230),                              # the Scraper in the haze
        lambda x, y, s, t, z, wp: HAZE[4] if (int(s * 9) % 3 == 0 or int(t * 60) % 4 == 0) else HAZE[5], cls='wall')
rs.quad((-200, 0, 140), (-170, 0, 140), (-200, 74, 140), lambda x, y, s, t, z, wp: HAZE[3] if int(t * 30) % 5 else HAZE[2], cls='wall')
for (X0, X1, Z0, ht, seed) in ((30, 80, 56, 48, 1), (80, 140, 70, 58, 2), (-80, -40, 48, 52, 3), (-130, -80, 70, 68, 4)):
    base = [planks(2.6, WOOD, seed=seed), concrete(3.0, STUCCO), corrugated(2.8, METAL, 0.7)][seed % 3]
    rs.box(X0, X1, 0, ht, Z0, Z0 + 14, facade(base, bay=4.6, floors=4.2, y0=1.0, seed=seed + 30), concrete(2.4), cls='wall')
    rs.box(X0 - 0.6, X1 + 0.6, ht, ht + 0.8, Z0 - 0.6, Z0 + 14, lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 2.2, x, y), z),
           lambda x, y, s, t, z, wp: fogged(RUSTY[1], z), cls='prop')
rs.box(-78, -74.5, 52, 74, 62, 66, concrete(3.4, STONE), concrete(2.6, STONE), cls='wall')                  # a brick chimney
for k in range(4):
    rs.line3((36 + k * 9, 48, 57), (38 + k * 9, 52.5, 57), lambda x, y, s, t, z, wp: fogged(STONE[1], z), w=0.5)   # aerials

# ---------------------------------------------------------------------------------------------------- materials
def battens(v0, r=WOOD, w=0.85, seed=0):
    """vertical boards with a narrow batten over every joint"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        pl = math.floor(X / w); fu = X / w - pl
        v = v0 + (h32(pl, seed, 1) % 3) * 0.3 - 0.6 * (wn(0, X * 0.6, Y * 3.0) - 0.5) - 0.8 * max(0.0, 1 - Y / 2.6)
        bw = max(0.13, 1.3 * z / F / w)
        if fu < bw: v += 0.7 if fu < bw * 0.55 else -0.4                           # the batten: lit face, shadow side
        elif fu < bw + 0.9 * z / F / w: v -= 1.0
        if h32(pl, int(Y * 2.1), seed) % 29 == 0: v -= 0.9
        return fogged(tone(r, v, x, y), z)
    return sh
def clapboard(v0, r=WOOD, h=0.55, seed=0):
    """horizontal overlapping boards: a dark shadow line under each lap"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        row = math.floor(Y / h); fv = Y / h - row
        v = v0 + (h32(row, seed, 2) % 3) * 0.3 - 0.6 * (wn(0, X * 0.3, Y * 0.6) - 0.5) - 0.8 * max(0.0, 1 - Y / 2.6)
        if fv < max(0.12, 1.2 * z / F / h): v -= 1.3
        elif fv > 0.82: v += 0.5
        return fogged(tone(r, v, x, y), z)
    return sh
def rubble(v0=3.6):
    """the rubble-stone plinth the timber stands on: irregular blocks, dark joints, damp"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        row = math.floor(Y / 0.45); off = (h32(row, 9) % 7) * 0.13
        bw = 0.7 + (h32(row, 8) % 3) * 0.15
        col = math.floor((X + Z + off) / bw)
        fu = ((X + Z + off) / bw) % 1; fv = (Y / 0.45) % 1
        v = v0 + (h32(col, row, 4) % 4) * 0.3 - 0.9 * max(0.0, 1 - Y / 1.2)
        if fu < 1.2 * z / F / bw + 0.04 or fv < 1.2 * z / F / 0.45 + 0.05: v -= 1.4
        return fogged(tone(STONE, v, x, y), z)
    return sh
def glass_warm(x, y, u, v, k):
    """a lit tavern pane: warm, brighter towards the middle, a few darker panes"""
    g = 2.6 - abs(u - 0.5) * 1.6 - abs(v - 0.55) * 1.0 + (0.6 if k % 5 == 0 else 0) - (1.2 if k % 7 == 3 else 0)
    return ri(GLOW, band(g, x, y))
def tavern_window(X0, X1, Y0, Y1, cols=4, rows=3, seed=0, curtain=True):
    """a multi-pane window in a heavy frame: warm light, a café curtain on a rod over the lower half"""
    def fn(x, y, X, Y, z):
        if not (X0 < X < X1 and Y0 < Y < Y1): return None
        fr = 0.32
        if X < X0 + fr or X > X1 - fr or Y < Y0 + fr or Y > Y1 - fr:
            return tone(WOOD, 1.6 + (0.8 if Y > Y1 - fr * 0.4 else 0), x, y)
        u, v = (X - X0 - fr) / (X1 - X0 - 2 * fr), (Y - Y0 - fr) / (Y1 - Y0 - 2 * fr)
        pw = max(0.07, 1.4 * z / F / (X1 - X0))
        cu, cv = (u * cols) % 1, (v * rows) % 1
        if cu < pw * cols or cv < pw * rows * (X1 - X0) / (Y1 - Y0): return WOOD[1]
        k = h32(int(u * cols), int(v * rows), seed)
        if curtain and v < 0.45:
            if abs(v - 0.45) < 0.04: return METAL[3]                                  # the rod
            fold = (u * 22) % 1
            c = tone(RED, 1.8 + (0.9 if fold < 0.3 else 0) - (0.9 if fold > 0.8 else 0) + v * 1.6, x, y)
            return mix(c, (64, 52, 40), 0.35)                                          # faded, smoky
        return glass_warm(x, y, (u * cols) % 1, v, k)
    return fn
def dark_window(X0, X1, Y0, Y1, seed=0, state=None):
    """an upper window: dark glass with the sky in it, shuttered, boarded or lit"""
    def fn(x, y, X, Y, z):
        if not (X0 < X < X1 and Y0 < Y < Y1): return None
        fr = 0.3
        if X < X0 + fr or X > X1 - fr or Y < Y0 + fr or Y > Y1 - fr: return tone(WOOD, 1.8, x, y)
        u, v = (X - X0) / (X1 - X0), (Y - Y0) / (Y1 - Y0)
        if state == 'boarded':
            c = tone(WOOD, 3.2 - (1.4 if (v * 5) % 1 < 0.14 else 0) + (h32(int(v * 5), seed) % 3) * 0.3, x, y)
            if abs(u - (1 - v)) < 0.07: c = tone(WOOD, 4.4, x, y)
            return c
        if state == 'shutter':
            return tone(SHUT[seed % 3], 2.4 - (1.2 if (v * 10) % 1 < 0.25 else 0) - (1.0 if abs(u - 0.5) < 0.03 else 0), x, y)
        if abs(u - 0.5) < 0.05 or abs(v - 0.5) < 0.05: return WOOD[1]                  # the glazing bars
        if state == 'lit': return glass_warm(x, y, (u * 2) % 1, v, h32(int(u * 2), int(v * 2), seed))
        return tone(SKY, 2.4 + v * 2.4 + (0.9 if (u + v * 0.5) % 0.6 < 0.07 else 0), x, y)
    return fn
def first(fns, x, y, X, Y, z):
    for f in fns:
        c = f(x, y, X, Y, z)
        if c is not None: return c
    return None
def beam(v0):
    return lambda x, y, s, t, z, wp: fogged(tone(WOOD, v0 + (0.9 if t > 0.7 else 0) - (h32(int(wp[0] / 3.0), 2) % 2) * 0.3, x, y), z)
def u_pipe(X, Y0, Z, r_, leg, col):
    """a vent pipe bent into an upside-down U"""
    pts = [(X, Y0, Z), (X, Y0 + leg, Z)] + [(X + r_ - r_ * math.cos(math.pi * i / 10), Y0 + leg + r_ * math.sin(math.pi * i / 10), Z) for i in range(11)] + [(X + 2 * r_, Y0 + leg * 0.45, Z)]
    for a, b in zip(pts, pts[1:]):
        rs.line3(a, b, lambda x, y, s, t, z, wp: fogged(tone(col if (wp[1] * 3) % 2 < 1.6 else METAL, 2.8 + (0.8 if wp[0] < X + r_ * 0.5 else 0), x, y), z), w=0.85)

# ---------------------------------------------------------------------------------------------------- the left tower (the oldest part)
TOWER_WIN = [dark_window(-38.0, -34.5, 12.2, 17.2, 1, 'boarded'), dark_window(-30.0, -26.5, 12.2, 17.2, 2),
             dark_window(-38.0, -34.5, 22.0, 27.0, 5), dark_window(-30.0, -26.5, 22.0, 27.0, 6, 'shutter'),
             dark_window(-22.0, -19.0, 22.0, 27.0, 7, 'lit'), tavern_window(-28.0, -21.0, 2.6, 7.4, 4, 3, 9, curtain=False)]
ARCH = (-34.6, 3.2, 4.6)                                                             # the passage through the tower: centre x, half width, spring
def passage(x, y, X, Y, z):
    """a dark archway through the tower's ground floor (the way out to Burning Bear Street), daylight at its far end"""
    cx, w2, sp = ARCH
    d = math.hypot(X - cx, max(0.0, Y - sp))
    if not (abs(X - cx) < w2 + 0.5 and (Y < sp or d < w2 + 0.5)): return None
    if abs(X - cx) > w2 or (Y >= sp and d > w2):                                     # the stone arch
        a = math.degrees(math.atan2(Y - sp, X - cx)) / 15 if Y >= sp else Y / 1.1
        return tone(STONE, 4.0 + (h32(int(a), 5) % 3) * 0.3 - (1.2 if a % 1 < 0.12 else 0), x, y)
    u, v = (X - cx) / w2, Y / (sp + w2)
    if abs(u) < 0.42 and v < 0.62:                                                   # the far end: the street beyond, hazy
        return tone(HAZE, 3.0 + v * 2.2 - abs(u) * 2, x, y)
    return tone(STONE, 0.6 + (1 - abs(u)) * 0.9 - v * 0.6 + (0.5 if (Y * 2.2) % 1 < 0.12 and abs(u) > 0.5 else 0), x, y)
def tower_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    c = passage(x, y, X, Y, z)
    if c is not None: return fogged(c, z)
    if Y < 1.3: return rubble()(x, y, s, t, z, wp)
    if abs(Y - 9.8) < 0.35 or abs(Y - 19.6) < 0.35: return fogged(tone(WOOD, 2.6 + (0.8 if Y % 1 > 0.5 else 0), x, y), z)   # storey beams
    c = first(TOWER_WIN, x, y, X, Y, z)
    if c is not None: return fogged(c, z, 0.85)
    if (X + 60) % 8.0 < 0.5: return fogged(tone(WOOD, 1.4, x, y), z)              # posts
    return clapboard(2.8, WOOD, seed=2)(x, y, s, t, z, wp)
rs.box(-44.0, -15.2, 0, 29.4, ZL, ZL + 12, tower_front, clapboard(2.4), cls='wall')
rs.box(-44.6, -15.0, 29.4, 30.4, ZL - 0.8, ZL + 12, lambda x, y, s, t, z, wp: fogged(tone(WOOD, 3.4 - t, x, y), z),
       lambda x, y, s, t, z, wp: fogged(WOOD[1], z), bottom=lambda x, y, s, t, z, wp: fogged(WOOD[0], z), cls='prop')     # the eaves
u_pipe(-33.0, 30.4, ZL + 2, 1.6, 2.4, RUSTY); u_pipe(-24.0, 30.4, ZL + 4, 1.1, 1.6, METAL)
rs.box(-41.0, -38.0, 30.4, 33.0, ZL + 1.5, ZL + 4, steel(2.4, METAL, rust=0.7), steel(1.8, METAL), cls='prop')      # a little water tank
rs.line3((-40.2, 29.0, ZL - 0.2), (-40.2, 0.6, ZL - 0.2), lambda x, y, s, t, z, wp: fogged(tone(METAL, 2.0 + (1 if int(wp[1] * 1.5) % 3 == 0 else 0), x, y), z), w=0.5)   # drainpipe

# ---------------------------------------------------------------------------------------------------- the main block
DOOR = (-3.0, 3.0, 8.0)
GROUND_WIN = [tavern_window(-12.6, -5.6, 2.4, 7.4, 4, 3, 11), tavern_window(5.6, 12.6, 2.4, 7.4, 4, 3, 12)]
UPPER_WIN = [dark_window(-10.0, -6.0, 20.4, 24.2, 13, 'lit'), dark_window(-2.0, 2.0, 20.4, 24.2, 14),
             dark_window(6.0, 10.0, 20.4, 24.2, 15, 'shutter')]
def basement(x, y, X, Y, z):
    """half-sunk cellar windows behind bars: the red light of the club below"""
    for (X0, X1) in ((-12.0, -7.6), (7.6, 12.0)):
        if X0 < X < X1 and 0.35 < Y < 1.15:
            if (X - X0) % 0.55 < max(0.1, 1.2 * z / F): return METAL[0]
            k = 1 - abs((X - (X0 + X1) / 2) / ((X1 - X0) / 2))
            return mix((70, 20, 18), (196, 74, 42), k * 0.8 + 0.1 * ((x + y) % 2))
    return None
def door(x, y, X, Y, z):
    x0, x1, top = DOOR
    if not (x0 < X < x1 and Y < top): return None
    if X < x0 + 0.4 or X > x1 - 0.4 or Y > top - 0.45: return tone(WOOD, 1.4 + (0.9 if X < x0 + 0.15 else 0), x, y)   # the frame
    if Y < 0.3: return tone(STONE, 4.6, x, y)                                      # the worn threshold
    if abs(X) < 0.06: return WOOD[0]                                               # the leaves meet
    u = abs(X) / (x1 - 0.4)
    if 0.18 < u < 0.82 and 5.0 < Y < 6.9:                                           # little lit windows in the leaves
        if abs(u - 0.5) < 0.05 or abs(Y - 5.95) < 0.08: return WOOD[1]
        return GLOW[2] if (x + y) % 3 else GLOW[3]
    v = 2.4 + (h32(int(X / 0.75 + 20), 3) % 3) * 0.3 - (1.2 if ((X + 20) / 0.75) % 1 < 0.1 else 0) - 0.4 * (Y < 1.0)
    if abs(Y - 1.6) < 0.2 or abs(Y - 4.2) < 0.2:                                    # iron strap hinges
        if u > 0.35 or abs(Y - 4.2) < 0.2: return tone(STONE, 1.4 + (1.6 if (X * 4) % 1 < 0.2 else 0), x, y)
    if abs(u - 0.12) < 0.06 and abs(Y - 3.6) < 0.3: return GLOW[3]                  # brass handles
    return tone(WOOD, v + 0.6, x, y) if X < 0 else tone(WARM, v - 0.2, x, y)
def main_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    c = door(x, y, X, Y, z)
    if c is not None: return fogged(c, z)
    if Y < 1.4:
        c = basement(x, y, X, Y, z)
        return fogged(c, z) if c is not None else rubble(3.8)(x, y, s, t, z, wp)
    c = first(GROUND_WIN + UPPER_WIN, x, y, X, Y, z)
    if c is not None: return fogged(c, z, 0.85)
    if abs(X) > 14.3: return fogged(tone(WOOD, 1.6 + (0.6 if (X * 4) % 1 < 0.3 else 0), x, y), z)              # corner posts
    return battens(2.8, WOOD, seed=5)(x, y, s, t, z, wp)
rs.box(-15.0, 15.0, 0, 25.0, ZF, ZF + 14, main_front, battens(2.6), cls='wall')
for (Y0, Y1, dz) in ((10.3, 10.9, 0.5), (19.4, 19.9, 0.45), (24.8, 25.8, 0.9)):    # fascias and the top cornice
    rs.box(-15.6, 15.6, Y0, Y1, ZF - dz, ZF, beam(2.8), beam(2.0), top=beam(3.6), bottom=lambda x, y, s, t, z, wp: fogged(WOOD[0], z), cls='prop')
for (X0, X1) in ((-12.9, -5.3), (5.3, 12.9)):                                       # window sills
    rs.box(X0, X1, 2.05, 2.4, ZF - 0.45, ZF, beam(3.2), beam(2.2), top=beam(4.0), cls='prop')
def false_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    if 27.3 < Y < 27.7 or Y > 28.7: return fogged(tone(WOOD, 3.6, x, y), z)
    return battens(3.0, WOOD, seed=6)(x, y, s, t, z, wp)
rs.box(-8.0, 8.0, 25.8, 27.7, ZF - 0.1, ZF + 0.4, false_front, battens(2.4), cls='wall')
rs.box(-4.5, 4.5, 27.7, 29.0, ZF - 0.1, ZF + 0.4, false_front, battens(2.4), cls='wall')

# the name board: dark planks in a heavy frame; the letters are painted into it (and peel)
SIGN = (-10.6, 10.6, 11.6, 19.0, ZF - 0.45)
LET = {}
def sign_face(x, y, s, t, z, wp):
    X, Y, Z = wp
    x0, x1, y0, y1, _ = SIGN
    if X < x0 + 0.5 or X > x1 - 0.5 or Y < y0 + 0.5 or Y > y1 - 0.5:
        v = 2.6 + (0.9 if (Y > y1 - 0.22 or X < x0 + 0.18) else 0) - (0.8 if (Y < y0 + 0.18 or X > x1 - 0.18) else 0)
        if (abs(X - x0 - 0.27) < 0.13 or abs(X - x1 + 0.27) < 0.13) and (abs(Y - y0 - 0.27) < 0.13 or abs(Y - y1 + 0.27) < 0.13): v = 5.0   # bolts
        return fogged(tone(WOOD, v, x, y), z)
    row = math.floor((Y - y0) / 1.1)
    v = 1.9 + (h32(row, 7) % 3) * 0.25 - (1.0 if ((Y - y0) / 1.1) % 1 < 0.07 else 0) + (wn(0, X * 0.8, Y * 0.8) - 0.5) * 0.5
    board = tone(WOOD, v, x, y)
    if (x, y) in LET:
        peel = wn(2, X * 1.3 + 40, Y * 1.6) + (wn(3, X * 4, Y * 4) - 0.5) * 0.25
        if peel > 0.7: return fogged(tone(WARM, 2.8, x, y) if peel < 0.725 else board, z)                   # paint gone, a pale rim
        return fogged(tone(PAINT, 3.3 + LET[(x, y)] * 1.2 + (wn(1, X * 2, Y * 2) - 0.5) * 0.9 - (0.6 if wn(0, X * 3, Y * 0.5) > 0.7 else 0), x, y), z)
    if (x - 1, y - 1) in LET: return fogged(mix(board, (8, 8, 6), 0.45), z)                                     # the painted drop shadow
    return fogged(board, z)
rs.box(SIGN[0], SIGN[1], SIGN[2], SIGN[3], SIGN[4], ZF, sign_face, beam(2.0), cls='prop')

def build_letters():
    """the two lines of the name as a screen-space mask over the board; 1 = the upper edge of a stroke"""
    x0, x1, y0, y1, z = SIGN
    (ax, ay) = proj(x0 + 0.9, y1 - 0.75, z); (bx, by) = proj(x1 - 0.9, y0 + 0.75, z)
    w, h = int(bx - ax), int(by - ay)
    path = '/usr/share/fonts/TTF/DejaVuSerifCondensed-Bold.ttf'
    im = Image.new('L', (w, h), 0); d = ImageDraw.Draw(im); d.fontmode = '1'
    lines = ['SCREAMING', 'CORK']
    if os.path.exists(path):
        size = 80
        while size > 10:
            f = ImageFont.truetype(path, size)
            bbs = [d.textbbox((0, 0), ln, font=f) for ln in lines]
            th = sum(b[3] - b[1] for b in bbs) + size * 0.14
            if max(b[2] - b[0] for b in bbs) <= w and th <= h: break
            size -= 1
        yy = (h - th) / 2
        for ln, b in zip(lines, bbs):
            d.text(((w - (b[2] - b[0])) / 2 - b[0], yy - b[1]), ln, font=f, fill=255)
            yy += b[3] - b[1] + size * 0.14
    else:                                                                            # no TTF here: the 3x5 pixel font
        sc = 7
        for i, ln in enumerate(lines):
            draw_text(lambda x, y: (0 <= x < w and 0 <= y < h) and im.putpixel((x, y), 255), ln, (w - text_width(ln, sc)) // 2, 6 + i * 6 * sc, sc)
    p = im.load(); m = {}
    for y in range(h):
        for x in range(w):
            if p[x, y]: m[(int(ax) + x, int(ay) + y)] = 1 if (y < 2 or not p[x, y - 1] or not p[x, y - 2]) else 0
    return m
LET.update(build_letters())

# the awning over the door: corrugated sheet on two iron brackets
rs.quad((-5.4, 9.6, ZF), (5.4, 9.6, ZF), (-5.4, 8.6, ZF - 2.8), corrugated(3.4, METAL, 0.8), cls='prop')
rs.quad((-5.4, 8.6, ZF - 2.8), (5.4, 8.6, ZF - 2.8), (-5.4, 8.3, ZF - 2.8), lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 2.4 + t * 1.5, x, y), z), cls='prop')
for X in (-4.7, 4.7):
    rs.line3((X, 6.8, ZF), (X, 8.55, ZF - 2.5), lambda x, y, s, t, z, wp: fogged(METAL[0], z), w=0.16)
# a lamp right of the door
rs.line3((4.0, 7.6, ZF), (4.0, 7.6, ZF - 0.8), lambda x, y, s, t, z, wp: METAL[0], w=0.12)
rs.box(3.7, 4.3, 6.3, 7.3, ZF - 1.0, ZF - 0.6, lambda x, y, s, t, z, wp: GLOW[3] if 0.2 < s < 0.8 and 0.15 < t < 0.85 else METAL[0],
       lambda x, y, s, t, z, wp: METAL[0], cls='emit')

# the hanging sign: a carved cork, screaming, with a corkscrew driven into its top
HX, HZ = -18.4, ZF - 0.6
BR = 15.6                                                                            # the bracket's height
rs.line3((-15.0, BR, HZ), (HX - 1.1, BR, HZ), lambda x, y, s, t, z, wp: METAL[0], w=0.2)          # the bracket
rs.line3((-15.0, BR - 1.6, HZ), (-16.8, BR, HZ), lambda x, y, s, t, z, wp: METAL[0], w=0.14)
CK = (9.4, 13.6, 1.3)                                                                # the cork: bottom, top, radius
def cork(x, y, s, t, z, wp):
    """a carved wooden cork, its face cut deep into it: sunken sockets, staring eyes, a howling mouth with teeth"""
    u = s * 2 - 1
    taper = 0.88 + 0.12 * t
    if abs(u) > taper: return None
    if t < 0.05 and abs(u) > taper * math.sqrt(max(0.0, 1 - ((0.05 - t) / 0.05) ** 2)): return None
    X, Y, Z = wp
    n = u / taper
    v = 3.6 - n * 1.6 - abs(n) ** 3 * 1.5 + (wn(1, X * 6, Y * 6) - 0.5) * 0.9
    if h32(int(X * 9), int(Y * 9), 3) % 9 == 0: v -= 1.4                               # pores
    if abs(n - 0.62 + t * 0.2) < 0.03 and 0.15 < t < 0.5: v -= 1.6                     # a split in the wood
    if t < 0.1: return tone(CORK, v, x, y) if t > 0.07 else mix(tone(CORK, v, x, y), WINE, 0.6)   # the wine-stained end
    ex, ey = abs(n) - 0.37, (t - 0.7) / 0.11
    so = (ex / 0.27) ** 2 + ey ** 2
    if so < 1:                                                                        # the eye sockets, carved in
        if (ex / 0.17) ** 2 + ((t - 0.69) / 0.065) ** 2 < 1:                           # the eyeball, staring
            if (ex / 0.07) ** 2 + ((t - 0.69) / 0.045) ** 2 < 1: return INK
            return BONE[3] if t > 0.69 else BONE[2]
        return tone(CORK, 1.2 + ey * 0.8 - (0.5 if ex * (1 if n > 0 else -1) > 0 else 0), x, y)
    br = t - (0.84 - (abs(n) - 0.37) * 0.4)                                           # brows, wrenched up at the middle
    if abs(ex + 0.02) < 0.26 and abs(br) < 0.025: return tone(CORK, 0.6, x, y)
    if abs(n) < 0.09 and 0.52 < t < 0.6: return tone(CORK, 1.6 - n * 4, x, y)        # the nose ridge's shadow
    mo = (n / 0.3) ** 2 + ((t - 0.3) / 0.19) ** 2
    if mo < 1.25 and mo >= 1: return tone(CORK, 5.2 if t < 0.3 else 1.2, x, y)       # the lips: lit below, shadowed above
    if mo < 1:
        if t > 0.42 and (n * 12) % 1 < 0.6 and abs(n) < 0.22: return BONE[2]             # the upper teeth
        return mix(INK, (110, 30, 26), max(0.0, 0.7 - mo) * 0.9)                        # the throat, dark red deep inside
    return tone(CORK, v, x, y)
rs.quad((HX - CK[2], CK[0], HZ - CK[2] * 0.6), (HX + CK[2], CK[0], HZ - CK[2] * 0.6), (HX - CK[2], CK[1], HZ - CK[2] * 0.6), cork, cls='prop', cut=True)
for i in range(18):                                                                 # the corkscrew's helix, its handle, the chain
    a0, a1 = i * 0.9, (i + 1) * 0.9
    p0 = (HX + 0.32 * math.cos(a0), CK[1] + i * 0.07, HZ - 0.8 + 0.32 * math.sin(a0) * 0.3)
    p1 = (HX + 0.32 * math.cos(a1), CK[1] + (i + 1) * 0.07, HZ - 0.8 + 0.32 * math.sin(a1) * 0.3)
    rs.line3(p0, p1, lambda x, y, s, t, z, wp, a0=a0: METAL[5] if math.cos(a0) < -0.3 else METAL[2], w=0.11)
rs.line3((HX, CK[1] + 1.26, HZ - 0.8), (HX, CK[1] + 1.7, HZ - 0.8), lambda x, y, s, t, z, wp: METAL[2], w=0.13)
rs.line3((HX - 0.9, CK[1] + 1.75, HZ - 0.8), (HX + 0.9, CK[1] + 1.75, HZ - 0.8), lambda x, y, s, t, z, wp: tone(WARM, 3.4, x, y), w=0.32)
rs.line3((HX, CK[1] + 1.85, HZ - 0.8), (HX - 0.15, BR, HZ - 0.4), lambda x, y, s, t, z, wp: METAL[1] if (x + y) % 2 else METAL[0], w=0.1)

# ---------------------------------------------------------------------------------------------------- the right wing (steps forward)
def arched_door(x, y, X, Y, z):
    cx, w2, spring = 25.4, 2.9, 5.6
    d = math.hypot(X - cx, max(0.0, Y - spring))
    if abs(X - cx) < w2 + 0.55 and (Y < spring or d < w2 + 0.55):
        if abs(X - cx) > w2 or (Y >= spring and d > w2):                             # the stone arch around it
            a = math.degrees(math.atan2(Y - spring, X - cx)) / 18 if Y >= spring else Y / 1.2
            return tone(STONE, 4.4 + (h32(int(a), 5) % 3) * 0.3 - (1.2 if a % 1 < 0.1 else 0), x, y)
        if Y < 0.3: return tone(STONE, 4.4, x, y)
        v = 2.2 + (h32(int((X - cx) / 0.7 + 10), 6) % 3) * 0.3 - (1.2 if ((X - cx) / 0.7) % 1 < 0.1 else 0)
        if (abs(Y - 2.0) < 0.1 or abs(Y - 6.4) < 0.1) or (((X - cx) / 0.7) % 1 < 0.2 and (Y * 1.4) % 1 < 0.12): v = 4.2   # straps, studs
        if abs(X - cx - 2.0) < 0.2 and abs(Y - 3.8) < 0.2: return GLOW[2]
        return tone(WOOD, v, x, y)
    return None
WING_WIN = [tavern_window(17.0, 21.4, 2.6, 7.4, 3, 3, 21, curtain=False), tavern_window(30.2, 34.6, 2.6, 7.4, 3, 3, 22),
            dark_window(17.4, 21.4, 11.8, 16.8, 23, 'shutter'), dark_window(23.4, 27.4, 11.8, 16.8, 24),
            dark_window(29.6, 33.6, 11.8, 16.8, 25, 'lit')]
def wing_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    c = arched_door(x, y, X, Y, z)
    if c is not None: return fogged(c, z)
    if Y < 1.3: return rubble(3.6)(x, y, s, t, z, wp)
    c = first(WING_WIN, x, y, X, Y, z)
    if c is not None: return fogged(c, z, 0.85)
    if abs(Y - 9.6) < 0.35: return fogged(tone(WOOD, 2.6 + (0.8 if Y > 9.8 else 0), x, y), z)
    if X < 16.2 or (X - 15.6) % 12.0 < 0.5: return fogged(tone(WOOD, 1.5, x, y), z)
    return battens(3.4 if Y < 9.6 else 3.0, WOOD, seed=8)(x, y, s, t, z, wp)
rs.box(15.6, 44.0, 0, 19.6, ZR, ZR + 12, wing_front, planks_z(2.6, WOOD, seed=9), cls='wall')
rs.box(15.0, 44.0, 19.6, 20.6, ZR - 0.9, ZR + 12, lambda x, y, s, t, z, wp: fogged(tone(WOOD, 3.2 - t, x, y), z),
       lambda x, y, s, t, z, wp: fogged(WOOD[1], z), bottom=lambda x, y, s, t, z, wp: fogged(WOOD[0], z), cls='prop')
rs.quad((22.6, 18.2, ZR), (28.2, 18.2, ZR), (22.6, 17.6, ZR - 1.5), corrugated(3.0, METAL, 0.9), cls='prop')     # a pent roof over the middle window
u_pipe(19.0, 20.6, ZR + 3, 1.5, 2.6, METAL)
for k, X in enumerate((27.0, 28.6, 30.6)):                                           # vent stacks with caps
    hh = 22.6 + k * 1.0
    rs.box(X - 0.3, X + 0.3, 20.6, hh, ZR + 6, ZR + 6.7, steel(2.4, METAL, rust=0.8), steel(1.6, METAL), cls='prop')
    rs.box(X - 0.7, X + 0.7, hh, hh + 0.4, ZR + 5.7, ZR + 7.0, lambda x, y, s, t, z, wp: fogged(METAL[2], z), lambda x, y, s, t, z, wp: fogged(METAL[1], z), cls='prop')
rs.line3((23.5, 20.6, ZR + 2), (23.5, 22.6, ZR + 2), lambda x, y, s, t, z, wp: fogged(STONE[1], z), w=0.35)         # a stovepipe
rs.line3((16.0, 19.0, ZR - 0.4), (16.0, 0.4, ZR - 0.4), lambda x, y, s, t, z, wp: fogged(tone(METAL, 2.2 + (1 if int(wp[1] * 1.5) % 3 == 0 else 0), x, y), z), w=0.5)

# cables strung between the houses
rs.line3((-15.0, 23.0, ZF), (-26.0, 27.5, ZL), lambda x, y, s, t, z, wp: STONE[0], w=0.1, sag=1.0)
rs.line3((15.0, 22.5, ZF), (24.0, 18.6, ZR), lambda x, y, s, t, z, wp: STONE[0], w=0.1, sag=0.8)
rs.line3((-44.0, 24.0, ZL), (-19.0, 15.6, 14.6), lambda x, y, s, t, z, wp: STONE[0], w=0.09, sag=1.4)

# ---------------------------------------------------------------------------------------------------- props
def barrel(X, Z, h=2.7, r=1.05, seed=0):
    def sh(x, y, s, t, z, wp):
        u = s * 2 - 1
        bul = 1.0 - 0.1 * (2 * t - 1) ** 2
        if abs(u) > bul: return None
        n = u / bul
        v = 3.4 - n * 1.5 - abs(n) ** 3 * 1.4 + (h32(int((n + 1) * 7), seed) % 3) * 0.25
        if ((n + 1) * 7) % 1 < 0.12: v -= 0.9                                          # staves
        if abs(t - 0.18) < 0.04 or abs(t - 0.82) < 0.04: return fogged(tone(METAL, 2.6 - n * 1.2, x, y), z)   # hoops
        return fogged(tone(WARM, v - 0.6, x, y), z)
    rs.quad((X - r, 0.3, Z), (X + r, 0.3, Z), (X - r, 0.3 + h, Z), sh, cls='prop', cut=True)
    rs.quad((X - r * 0.9, 0.3 + h, Z), (X + r * 0.9, 0.3 + h, Z), (X - r * 0.9, 0.3 + h, Z + r * 1.6),
            lambda x, y, s, t, z, wp: (fogged(tone(WARM, 3.8 - (1.4 if abs(s - 0.5) * 2 > 0.92 else 0), x, y), z) if (2 * s - 1) ** 2 + (2 * t - 1) ** 2 < 1 else None),
            cls='prop', cut=True)
barrel(5.4, ZF - 1.4, seed=1); barrel(7.6, ZF - 1.1, h=2.5, seed=2)
def crate(X0, X1, Y0, Y1, Z0, seed):
    def front(x, y, s, t, z, wp):
        if s < 0.08 or s > 0.92 or t < 0.1 or t > 0.9: return fogged(tone(WARM, 3.4, x, y), z)
        if (s * 4) % 1 < 0.12: return fogged(WOOD[1], z)
        return fogged(tone(WOOD, 1.0 + (0.8 if (s * 4) % 1 > 0.6 else 0), x, y), z) if t > 0.55 else fogged(tone(WARM, 2.6, x, y), z)
    def top(x, y, s, t, z, wp):                                                       # empty bottles standing in it
        if (s * 4) % 1 < 0.5 and (t * 3) % 1 < 0.6: return fogged(tone(LEAF, 1.4 + (1.6 if (x + y) % 3 == 0 else 0), x, y), z)
        return fogged(WOOD[0], z)
    rs.box(X0, X1, Y0, Y1, Z0, Z0 + 1.6, front, planks(2.4, WARM, w=0.5, seed=seed), top=top, cls='prop')
crate(-5.4, -3.6, 0.3, 1.4, ZF - 1.7, 31); crate(-5.3, -3.5, 1.4, 2.5, ZF - 1.65, 32)
def bench(X0, X1, Z0):
    rs.box(X0, X1, 1.55, 1.85, Z0, Z0 + 1.2, beam(3.2), beam(2.2), top=beam(4.0), cls='prop')
    for X in (X0 + 0.4, X1 - 0.6):
        rs.box(X, X + 0.25, 0.3, 1.55, Z0 + 0.2, Z0 + 1.0, beam(1.6), beam(1.2), cls='prop')
bench(-13.8, -9.4, ZF - 1.3)
# a street lamp on the left, by the passage to Burning Bear Street
rs.line3((-21.4, 0.3, 15.4), (-21.4, 15.0, 15.4), lambda x, y, s, t, z, wp: METAL[1] if x % 3 else METAL[2], w=0.4)
rs.line3((-21.4, 15.0, 15.4), (-22.6, 15.5, 15.4), lambda x, y, s, t, z, wp: METAL[1], w=0.26)
rs.box(-23.3, -22.5, 13.8, 15.1, 15.0, 15.7, lambda x, y, s, t, z, wp: GLOW[2] if 0.2 < s < 0.8 and 0.15 < t < 0.85 else METAL[0],
       lambda x, y, s, t, z, wp: METAL[0], cls='emit')
for k in range(14):                                                                 # litter: corks, bottle shards, paper
    fx, fz = -30 + (h32(k, 41) % 600) / 10.0, 9.0 + (h32(k, 42) % 80) / 10.0
    c = [CORK[4], LEAF[2], BONE[3], CORK[3]][k % 4]
    rs.quad((fx - 0.25, 0.03, fz - 0.15), (fx + 0.25, 0.03, fz - 0.15), (fx - 0.25, 0.03, fz + 0.15),
            lambda x, y, s, t, z, wp, c=c: fogged(c if (x + y) % 4 else mix(c, (0, 0, 0), 0.3), z), cls='prop')
rs.box(-1.0, 1.0, 0.0, 0.06, 11.0, 11.8, lambda x, y, s, t, z, wp: METAL[0], lambda x, y, s, t, z, wp: METAL[0],
       top=lambda x, y, s, t, z, wp: METAL[0] if (s * 7) % 1 < 0.45 else STONE[0], cls='prop')                     # a drain grate

img = rs.render(INK, fog=fog_of, mirror=lambda x, y, wp: 0.7 * puddle(wp[0], wp[2]),
                light_gain=1.0, grime_gain=1.2, bloom=0.35, stain_gain=1.2)
img.save(f'{OUT}/cork.png')
print('done cork')
