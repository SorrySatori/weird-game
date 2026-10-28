"""Fast-travel map of Upper Morkezela as hand-drawn-looking pixel art (ui/MapUI.js, texture 'mapBg').

Native 400x300, shown 2x in the 800x600 map panel. Every landmark stands just above its MapUI node
(node x,y in the 800x600 panel -> ((x + 400) / 2, (y + 300) / 2) here; see LIFT), the roads follow MapUI.connections.

    python3 map_bg.py <outdir>     # -> map.png, map.gpl (palette), layers/<name>.png (for the Aseprite source),
                                   #    map_preview.png (4x)

Layers (bottom -> top): zeme (ground), voda (sea, bay, drain canal, delta), cesty (roads + bridges), stiny (drop
shadows), mesto (forests, filler houses), mista (the landmarks), svetla (lit windows, glows), vineta (translucent
black), ramecek (frame); + voditka (MapUI node / label / title guides, not exported).
"""
import math, os, random, sys
from PIL import Image

W, H = 400, 300
SEED = 521

def hx(s): return (int(s[1:3], 16), int(s[3:5], 16), int(s[5:7], 16))
def ramp(s): return [hx(c) for c in s.split()]

# ---- palette: muted, a little dusky so the green UI labels stay readable ----
MOSS  = ramp('#141a10 #1b2315 #232d1a #2c3820 #364427 #42502f #4f5e38 #5e6c42')
DUST  = ramp('#18181a #212124 #2a2a2d #343437 #3f3f42 #4b4b4d #58585a #6a6a6a')   # Shed district concrete
COBB  = ramp('#17140f #201b15 #29231b #332c22 #3e352a #4a4033 #574c3d #665a49')   # town cobbles
SLATE = ramp('#141518 #1b1d21 #23262b #2c3036 #363a41 #41464e #4e545c #5d636b')   # Scraper quarter
SAND  = ramp('#2a2516 #362f1c #433a23 #51472b #605434 #70623e')
YOLK  = ramp('#1d1a08 #27230b #322d0f #3e3813 #4b4417 #59511c #686021 #7a7128')   # the Yolk Sea
FOAM  = hx('#a39c6a')
OIL   = [hx('#3f6b6a'), hx('#6a3f6b'), hx('#6b5f2f'), hx('#2f5a6b')]
ROAD  = ramp('#1e1912 #2a2319 #362e21 #43392a #514634 #5f5340')
ROOF  = [ramp('#3a2117 #55301f #74432a #925a37 #ad7346'),     # rust tile
         ramp('#252b33 #343c47 #46505d #5a6574 #6f7b8a'),     # slate
         ramp('#2a3420 #3a472b #4c5c37 #5f7044 #738553'),     # moss-grown
         ramp('#352f27 #473f34 #5b5243 #6f6553 #847965')]     # tar paper
WALL  = ramp('#1a1714 #25211c #312c25 #3e382f #4c453a')
INK   = hx('#07080a')
LIGHT = ramp('#5a3a12 #8a5a1c #c4842a #e8b04a #f8dc8a')
SHELL = ramp('#3b3a30 #55533f #73705a #918d72 #aeaa8c #c8c4a5 #dedac0')   # the Egg
RUST  = ramp('#2a130c #451f12 #6a3118 #8f4a22 #b3662d')
GLASS = ramp('#0f2622 #16382f #1f4d3f #2b6652 #3d8466 #5aa883')
RED   = ramp('#2a0b10 #46121a #6a1a26 #8f2634 #b53a45 #d8626a')
VERD  = ramp('#18302a #23453b #31604f #427a63 #5b977a')                   # skyship verdigris
BRASS = ramp('#3a2a12 #5a4219 #7d5c22 #9e7a2f')
FLESH = ramp('#2a2b21 #3a3c2e #4e503d #646650 #7c7e64 #96977a')          # the dead demigod
FIRE  = ramp('#5a1a08 #9a3a0a #d8661a #f8a83a #ffe08a')
CORE  = ramp('#1f5a32 #3f8f5a #7fff8e #c8ffd0')                          # living core / mycelium glow

def node(x, y): return ((x + 400) // 2, (y + 300) // 2)

# ui/MapUI.js locations (panel coords) -> map pixels
N = {k: node(*v) for k, v in {
    'skyship': (0, -195), 'crossroad': (0, -120), 'cathedral': (120, -50), 'vox': (230, -120),
    'scraper': (0, 20), 'bus': (190, 10),
    'shed': (-240, -70),
    'square': (-100, 140), 'townhall': (-100, 210), 'lumen': (-220, 160), 'bear': (20, 210), 'cork': (160, 210),
    'harbor': (80, 140), 'delta': (230, 140), 'redmass': (330, 140),
}.items()}
# MapUI draws its node circle ON the node: each landmark stands this many px above it, so the
# circle marks the doorstep and doesn't hide the building
LIFT = {'skyship': 6, 'crossroad': 4, 'cathedral': 16, 'vox': 4, 'scraper': 4, 'bus': 2,
        'shed': 4, 'square': 10, 'townhall': 4, 'lumen': 5, 'bear': 2, 'cork': 4}
ROADS = [('skyship', 'crossroad'), ('crossroad', 'vox'), ('crossroad', 'shed'), ('crossroad', 'cathedral'), ('crossroad', 'scraper'),
         ('scraper', 'bus'),
         ('square', 'townhall'), ('square', 'harbor'), ('square', 'lumen'), ('square', 'bear'), ('bear', 'cork'),
         ('harbor', 'delta'), ('delta', 'redmass'), ('bear', 'scraper')]

def h32(*a):
    h = 2166136261
    for v in a: h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return h

def make_noise(cell, seed):
    rnd = random.Random(seed); gw, gh = W // cell + 3, H // cell + 3
    g = [[rnd.random() for _ in range(gw)] for _ in range(gh)]
    def n(x, y):
        fx, fy = x / cell, y / cell; ix, iy = int(fx), int(fy); tx, ty = fx - ix, fy - iy
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        a = g[iy % gh][ix % gw] * (1 - tx) + g[iy % gh][(ix + 1) % gw] * tx
        b = g[(iy + 1) % gh][ix % gw] * (1 - tx) + g[(iy + 1) % gh][(ix + 1) % gw] * tx
        return a * (1 - ty) + b * ty
    return n

N1, N2, N3 = make_noise(24, SEED), make_noise(9, SEED + 1), make_noise(4, SEED + 2)
def fbm(x, y): return 0.55 * N1(x, y) + 0.3 * N2(x, y) + 0.15 * N3(x, y)

def dither(v, x, y):
    """quantise with a 2x2 ordered dither seam (keeps the hand-pixelled look)"""
    f = math.floor(v); t = v - f
    return f + (1 if t > (0.25, 0.75, 1.0, 0.5)[(x % 2) + 2 * (y % 2)] - 0.125 else 0)

def pick(r, i): return r[max(0, min(len(r) - 1, int(i)))]

class Layer:
    def __init__(self, opaque=False):
        self.px = [[None] * W for _ in range(H)]
        if opaque: self.px = [[(0, 0, 0)] * W for _ in range(H)]
    def put(self, x, y, c):
        if 0 <= x < W and 0 <= y < H and c is not None: self.px[y][x] = c
    def get(self, x, y): return self.px[y][x] if 0 <= x < W and 0 <= y < H else None
    def image(self):
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for y in range(H):
            for x in range(W):
                c = self.px[y][x]
                if c is not None: im.putpixel((x, y), c if len(c) == 4 else (*c, 255))
        return im

# =============================================================================================
# geography
# =============================================================================================

def coast_x(y):
    """x of the eastern shore at row y (sea is east of it): a bay at the harbour, open sea below"""
    pts = [(0, 382), (60, 372), (110, 352), (150, 338), (178, 318), (196, 262), (208, 247), (238, 250), (246, 296), (262, 306), (300, 312)]
    for (y0, x0), (y1, x1) in zip(pts, pts[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0); t = t * t * (3 - 2 * t)
            return x0 + (x1 - x0) * t + (N2(17, y) - 0.5) * 8
    return pts[-1][1]

def in_sea(x, y): return x > coast_x(y)

# the Echo Drain: a canal from the Scraper's drains down into the delta
CANAL = [(226, 178), (240, 186), (256, 192), (272, 200), (288, 208), (302, 214)]
def canal_dist(x, y):
    best = 1e9
    for (ax, ay), (bx, by) in zip(CANAL, CANAL[1:]):
        dx, dy = bx - ax, by - ay; t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
        best = min(best, math.hypot(x - ax - t * dx, y - ay - t * dy))
    return best + (N3(x, y) - 0.5) * 0.8

# sandbars of the delta (land inside the bay)
BARS = [(305, 222, 9, 4), (318, 214, 7, 3), (322, 228, 8, 3), (311, 233, 5, 2)]
def on_bar(x, y): return any(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1 + (N3(x, y) - 0.5) * 0.4 for cx, cy, rx, ry in BARS)
def on_redmass(x, y):
    cx, cy = N['redmass']; return ((x - cx) / 15) ** 2 + ((y - cy - 2) / 9) ** 2 < 1 + (N2(x, y) - 0.5) * 0.5

def is_water(x, y): return (in_sea(x, y) and not on_bar(x, y) and not on_redmass(x, y)) or canal_dist(x, y) < 1.6

# districts: ground ramp + strength by distance
DISTRICTS = [
    (MOSS, (200, 60), 95), (MOSS, (40, 260), 60),          # wilds north (Crossroads) / Lumen gardens edge
    (DUST, (70, 140), 75),                                  # Shed 521 quarter
    (SLATE, (210, 160), 60),                                # the Scraper quarter
    (COBB, (180, 245), 85),                                 # the town
    (SAND, (300, 170), 45),                                 # the shore by the bus
]
def ground_ramp(x, y):
    best, bw = MOSS, 0
    for r, (cx, cy), rad in DISTRICTS:
        w = 1 - math.hypot(x - cx, y - cy) / rad + (N2(x * 1.3, y * 1.3) - 0.5) * 0.5
        if w > bw: best, bw = r, w
    return best

def ground_color(x, y, v):
    """ground colour with the neighbouring district dithered in along the borders"""
    a = ground_ramp(x, y); b = ground_ramp(x + 5, y + 4)
    r = b if (a is not b and (x + y) % 2 == 0) else a
    return pick(r, dither(v, x, y))

# =============================================================================================
# layers
# =============================================================================================

def draw_ground():
    L = Layer(opaque=True)
    for y in range(H):
        for x in range(W):
            r = ground_ramp(x, y)
            v = 2.1 + fbm(x, y) * 3.2
            v -= max(0, (y - 255) / 45) * 0.8        # a little darker toward the bottom (legend + hint)
            L.put(x, y, ground_color(x, y, v))
            if h32(x, y, 3) % 61 == 0: L.put(x, y, pick(r, v + 1.5))   # pebbles / tufts
    return L

def draw_water():
    L = Layer()
    for y in range(H):
        for x in range(W):
            if not is_water(x, y): continue
            if canal_dist(x, y) < 1.6 and not in_sea(x, y):
                L.put(x, y, pick(YOLK, 2 + (N3(x, y) > 0.55))); continue
            depth = (x - coast_x(y)) / 22 + (N1(x * 1.5, y) - 0.5)
            v = 5.2 - min(4.2, depth * 1.6) + (N2(x, y * 2) - 0.5) * 1.2
            c = pick(YOLK, dither(v, x, y))
            # slow wave crests: short horizontal dashes
            if y % 5 == (h32(x // 6) % 5) and (x + h32(y)) % 9 < 3 and depth > 0.4: c = pick(YOLK, v + 1.5)
            # oil sheen: a few thin rainbow slicks, not a carpet
            if N1(x * 2 + 40, y * 2) > 0.8 and (x + 2 * y) % 5 == 0: c = OIL[(x // 3 + y) % len(OIL)]
            L.put(x, y, c)
    # shoreline foam + wet edge
    for y in range(H):
        for x in range(W):
            if L.get(x, y) and in_sea(x, y):
                if any(not is_water(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    L.put(x, y, FOAM if h32(x, y) % 3 else pick(YOLK, 6))
    return L

def bez(a, b, bend):
    (ax, ay), (bx, by) = a, b
    mx, my = (ax + bx) / 2, (ay + by) / 2
    nx, ny = -(by - ay), bx - ax; ln = math.hypot(nx, ny) or 1
    cx, cy = mx + nx / ln * bend, my + ny / ln * bend
    pts, steps = [], int(math.hypot(bx - ax, by - ay) * 1.5) + 2
    for i in range(steps + 1):
        t = i / steps
        pts.append(((1 - t) ** 2 * ax + 2 * (1 - t) * t * cx + t * t * bx, (1 - t) ** 2 * ay + 2 * (1 - t) * t * cy + t * t * by))
    return pts

ROAD_MASK = set()
def draw_roads():
    L = Layer()
    for i, (a, b) in enumerate(ROADS):
        bend = ((h32(i, 9) % 15) - 7) * 0.9
        sea_road = 'redmass' in (a, b)
        for px, py in bez(N[a], N[b], bend):
            rad = 1.6 if sea_road else 2.6
            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    x, y = int(px + dx), int(py + dy); d = math.hypot(dx, dy)
                    if d > rad + 0.6: continue
                    water = is_water(x, y)
                    if sea_road and not water: continue        # the ferry line only shows over water
                    if sea_road:
                        if d < 0.8 and (x + y) % 3 == 0: L.put(x, y, FOAM)
                        continue
                    if water and in_sea(x, y):                  # roads end at the shore (the harbour has piers)
                        continue
                    if water:                                   # a plank bridge where a road crosses the canal
                        L.put(x, y, pick(BRASS, 1 + ((x + y) % 2)) if d < rad - 0.5 else INK)
                    else:
                        edge = d > rad - 0.7
                        v = 3.2 - d * 0.5 + (N3(x * 2, y * 2) - 0.5) * 2.0
                        L.put(x, y, pick(ROAD, 1 if edge else dither(v, x, y)))
                        if not edge and h32(x, y, 5) % 11 == 0: L.put(x, y, pick(ROAD, 5))   # cobble glints
                    ROAD_MASK.add((x, y))
    return L

# ---- drawing helpers ------------------------------------------------------------------------

def outline(L, pts):
    for (x, y) in pts:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in pts: L.put(x + dx, y + dy, INK)

def block(L, x, y, w, d, h, roof, wall=WALL, lit=0.15, seed=0, occ=None):
    """a little building in 3/4 view: roof w x d on top, front wall h below it; outlined"""
    pts = set()
    for yy in range(d):
        for xx in range(w):
            shade = 3 if yy < d * 0.45 else 2          # the far slope catches the light
            if xx == 0 or yy == 0: shade = 4
            if xx == w - 1: shade = 1
            c = pick(roof, shade - (1 if h32(seed, xx, yy) % 9 == 0 else 0))
            L.put(x + xx, y + yy, c); pts.add((x + xx, y + yy))
    for yy in range(h):
        for xx in range(w):
            c = pick(wall, 3 if xx < w - 1 else 1)
            if yy == 0: c = pick(wall, 1)
            L.put(x + xx, y + d + yy, c); pts.add((x + xx, y + d + yy))
    outline(L, pts)
    if occ is not None: occ.update(pts)
    return pts

def disc(L, cx, cy, rx, ry, col_fn):
    pts = set()
    for y in range(int(cy - ry - 1), int(cy + ry + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                L.put(x, y, col_fn(x, y)); pts.add((x, y))
    return pts

def tree(L, x, y, r=3, ramp_=MOSS, cap=False):
    pts = disc(L, x, y, r, r * 0.8, lambda px, py: pick(ramp_, 5 - ((px - x + py - y) > 0) - (h32(px, py) % 5 == 0)))
    outline(L, pts)
    if cap: L.put(x - 1, y - 1, pick(SHELL, 4))

# =============================================================================================
# landmarks (drawn centred on/above their node; the node circle + label are drawn by MapUI on top)
# =============================================================================================

def landmarks():
    L, G = Layer(), Layer()          # G = lights / glows (separate layer)
    occ = set()
    A = {k: (x, y - LIFT.get(k, 0)) for k, (x, y) in N.items()}   # art anchors

    # --- Skyship Verdigrace: hull + gondola, its shadow on the ground below
    sx, sy = A['skyship']
    for dx in range(-12, 13):
        for dy in range(-1, 2):
            if abs(dx) < 11 - abs(dy) * 2: L.put(sx + dx + 3, sy + 13 + dy, pick(MOSS, 0))
    hull = disc(L, sx, sy - 6, 15, 5, lambda x, y: pick(VERD, 4 - (y > sy - 6) - (y > sy - 4) - (x > sx + 9)))
    outline(L, hull)
    for x in range(sx - 13, sx + 14, 4):                         # rib seams
        for y in range(sy - 10, sy - 1):
            if (x, y) in hull and h32(x) % 2 == 0: L.put(x, y, pick(VERD, 1))
    gond = block(L, sx - 5, sy - 1, 10, 2, 2, BRASS, BRASS)
    for x in (sx - 3, sx + 1, sx + 4): G.put(x, sy + 2, LIGHT[3])
    L.put(sx - 16, sy - 7, pick(BRASS, 2)); L.put(sx - 17, sy - 8, pick(BRASS, 3))   # tail fin
    occ |= hull | gond

    # --- Crossroads: the figure on its stake at the junction (backgrounds/crossroad_corpse.png): tall cream headdress,
    #     grey face, red cloak with the spike through the chest, grey hands, the crossed-out crown sign on the post
    cx, cy = A['crossroad']                                       # cy = the foot of the stake
    fig = set()
    def put(x, y, c): L.put(x, y, c); fig.add((x, y))
    for x in range(cx - 2, cx + 3): put(x, cy, pick(STONE_, 3 - (x > cx)))            # stones at the foot
    for y in range(cy - 6, cy):                                                        # the stake
        put(cx, y, pick(WOOD_, 2)); put(cx + 1, y, pick(WOOD_, 1))
    for x in range(cx - 1, cx + 3): put(x, cy - 3, pick(WOOD_, 3))                      # the sign
    put(cx + 1, cy - 3, pick(RED, 4))
    for y in (cy - 6, cy - 5): put(cx - 1, y, pick(SKIN, 2)); put(cx + 2, y, pick(SKIN, 1))   # dangling legs
    for r, y in enumerate(range(cy - 13, cy - 6)):                                     # the cloak, widening down
        hw = 3 + (r >= 3) + (r >= 6)
        for x in range(cx - hw, cx + hw + 2):
            v = 4 if x < cx - 1 else 3 if x < cx + 2 else 2
            if (x - cx) % 2 and r > 1: v -= 1                                          # folds
            put(x, y, pick(RED, v))
    put(cx - 5, cy - 6, pick(SKIN, 2)); put(cx + 6, cy - 6, pick(SKIN, 1))             # hands under the sleeves
    put(cx, cy - 12, pick(STONE_, 5)); put(cx, cy - 11, pick(STONE_, 4))               # the spike + its stain
    put(cx - 1, cy - 10, pick(RED, 1)); put(cx + 1, cy - 10, pick(RED, 1)); put(cx, cy - 10, pick(RED, 0))
    for y in range(cy - 16, cy - 13):                                                  # the face
        for x in range(cx - 1, cx + 3): put(x, y, pick(SKIN, 3 if x < cx + 2 else 2))
    put(cx, cy - 15, INK); put(cx + 1, cy - 15, pick(SKIN, 1)); put(cx + 2, cy - 15, INK)
    for y, (x0_, x1_) in zip(range(cy - 21, cy - 16), ((cx + 1, cx + 3), (cx, cx + 3), (cx, cx + 3), (cx - 1, cx + 2), (cx - 1, cx + 2))):
        for x in range(x0_, x1_ + 1):                                                  # the headdress, leaning a little
            put(x, y, pick(SHELL, 6 if x == x0_ else 4 if x == x1_ else 5))
    put(cx + 1, cy - 19, pick(SHELL, 3))
    outline(L, fig); occ |= fig
    for x in range(cx + 2, cx + 6): L.put(x, cy + 1, pick(MOSS, 0))                    # its shadow

    # --- Egg Cathedral on its hill
    ex, ey = A['cathedral']
    hill = disc(L, ex, ey + 4, 22, 9, lambda x, y: pick(MOSS, 3 + (y < ey + 2) - (x > ex + 12)))
    egg = disc(L, ex, ey - 9, 13, 16, lambda x, y: pick(SHELL, dither(5.2 - (x - ex + 6) / 6 - (y - ey + 20) / 14 + (N3(x * 3, y * 3) - 0.5), x, y)))
    for y in range(ey - 24, ey + 6):                              # the egg's mottled scales
        for x in range(ex - 13, ex + 14):
            if (x, y) in egg and (x * 3 + y * 5) % 11 == 0: L.put(x, y, pick(SHELL, 2))
    outline(L, egg)
    for sp in (-17, -12, 12, 17):                                  # gothic spires flanking the egg
        tx = ex + sp
        for y in range(ey - 10 - (6 if abs(sp) < 15 else 2), ey + 6):
            for w in range(-1, 2):
                L.put(tx + w, y, pick(STONE_, 3 - (w > 0)))
        L.put(tx, ey - 12 - (6 if abs(sp) < 15 else 2), INK); L.put(tx, ey - 11 - (6 if abs(sp) < 15 else 2), pick(STONE_, 4))
    for y in range(ey - 3, ey + 6):                                # the amber door
        for x in range(ex - 2, ex + 3):
            if abs(x - ex) + max(0, ey - y - 1) < 4: G.put(x, y, LIGHT[3 if abs(x - ex) < 1 else 2])
    for y in range(ey + 6, ey + 11): L.put(ex, y, pick(ROAD, 4)); L.put(ex - 1, y, pick(ROAD, 3))   # steps
    occ |= hill | egg

    # --- Voxmarket: the zeppelin hangar seen from its open end -- a ribbed Quonset tunnel running back, the arched
    #     front open on the market (striped stalls, a string of bulbs), more stalls spilling out in front
    vx, vy = A['vox']
    R, LEN = 11, 18                                                # vault radius, how far back it reaches on screen
    arch = lambda x, r=R: math.sqrt(max(0.0, 1 - ((x - vx) / (r + 0.5)) ** 2))
    hang = set()
    for x in range(vx - R, vx + R + 1):
        t = (x - vx) / (R + 0.5); a_ = arch(x)
        top, face = vy - LEN - round(R * a_), vy - round(R * a_)
        for y in range(top, face):                                 # the roof, lit from the upper left
            v = 1.6 + 3.2 * a_ - 1.2 * t
            k = (vy - y - R * a_) / 3.0                            # transverse ribs: arcs parallel to the front arch
            if abs(k - round(k)) < 0.17 and round(k) > 0: v += 1.4
            L.put(x, y, pick(SLATE, dither(v, x, y))); hang.add((x, y))
        for y in range(face, vy + 1):                              # the front end wall
            L.put(x, y, pick(STEEL, 3 if y - face < 1 else 2 - (x > vx + 5))); hang.add((x, y))
    for x in range(vx - 7, vx + 8):                                # the open mouth onto the market
        top = vy - round(8 * arch(x, 7))
        for y in range(top, vy + 1): L.put(x, y, INK if y < vy - 2 else pick(WALL, 1))
        L.put(x, vy - 1, [VIOLET[3], GLASS[3], RUST[4], VIOLET[4]][(x // 2) % 4])          # striped awnings inside
        L.put(x, vy, [VIOLET[1], GLASS[1], RUST[2], VIOLET[2]][(x // 2) % 4])
        if x % 2 == 0: G.put(x, vy - 5 + round(1.5 * (1 - ((x - vx) / 7.5) ** 2)), LIGHT[3] if x % 4 else RED[5])
    outline(L, hang); occ |= hang
    for i, x in enumerate(range(vx - 25, vx + 26, 5)):             # stalls outside
        if abs(x - vx) < R + 2 or abs(x + 2 - vx) < R + 2: continue
        col = [VIOLET, GLASS, RUST, BRASS][i % 4]
        for xx in range(4): L.put(x + xx, vy - 1, pick(col, 4 if xx % 2 else 3)); L.put(x + xx, vy, pick(col, 1))
        L.put(x, vy + 1, INK); L.put(x + 3, vy + 1, INK)
        occ |= {(x + xx, yy) for xx in range(4) for yy in (vy - 1, vy, vy + 1)}

    # --- Scraper 1140: the stepped tower (setbacks, scaffolding, the sign), its top floors rusted over -- the Rust
    #     Choir lives up there; cables sag from it to the poles around. Dr. Elphi's studio and the Rust Domain are
    #     floors of this tower, so they have no landmark of their own.
    tx, ty = A['scraper']
    tw = set()
    SEG = [(10, 15, SCR), (8, 13, SCR), (6, 11, SCR), (3, 6, RUST)]      # (half-width, wall height, ramp) bottom -> top
    base = ty
    for i, (hw, h, rp) in enumerate(SEG):
        for y in range(base - h + 1, base + 1):                    # the front wall: pilasters, dark windows between
            for x in range(tx - hw, tx + hw + 1):
                v = 3 + ((x - tx) % 3 == 0) - (x > tx + hw - 3)
                if x == tx + hw: v = 1
                if x == tx - hw: v = 5
                if rp is SCR and (x - tx) % 3 and (y - base) % 3 == 1 and abs(x - tx) < hw:
                    v = 1
                    if h32(x, y, 11) % 6 == 0: G.put(x, y, LIGHT[2 + h32(x, y, 12) % 2])
                if i == 2 and h32(x, y, 23) % 4 == 0: v = 2; L.put(x, y, pick(RUST, 2)); tw.add((x, y)); continue
                L.put(x, y, pick(rp, v)); tw.add((x, y))
        top = base - h
        for y in (top - 1, top):                                   # the setback ledge (its roof, seen from above)
            for x in range(tx - hw, tx + hw + 1):
                L.put(x, y, pick(rp, 6 if y == top - 1 else 5) if rp is SCR else pick(RUST, 3 - (y == top))); tw.add((x, y))
        if i == 2:                                                 # rust runs down from the Choir's floors
            for x in range(tx - hw + 1, tx + hw):
                for d in range(h32(x, 21) % 6):
                    L.put(x, top + 1 + d, pick(RUST, 1 + (d == 0)))
        base = top - 2
    occ |= {(x, y) for x in range(tx - 16, tx + 17) for y in range(base - 8, ty + 4)}   # a clear forecourt around it
    for y in range(ty - 25, ty - 22):                              # the sign: SCRAPER 1140 in pale letters
        for x in range(tx - 6, tx + 7):
            if (y - ty + 24) != 1 and h32(x, y, 31) % 3: L.put(x, y, pick(SHELL, 5))
    for y in range(ty - 27, ty - 1):                               # scaffolding up the left flank
        L.put(tx - 11, y, pick(BRASS, 1 + (y % 4 == 0)))
        if y % 4 == 0: L.put(tx - 12, y, pick(BRASS, 1))
    for y in range(base - 6, base + 1): L.put(tx, y, pick(RUST, 1))   # the antenna + its warning light
    G.put(tx, base - 7, RED[5])
    for y in range(ty - 3, ty + 1):                                # the lit entrance
        for x in range(tx - 1, tx + 2): G.put(x, y, LIGHT[3 if y > ty - 3 else 2])
    outline(L, tw); occ |= tw
    poles = [(tx - 25, ty - 2), (tx + 24, ty - 4), (tx - 21, ty - 26), (tx + 20, ty - 28)]
    anchors = [(tx - 10, ty - 10), (tx + 10, ty - 11), (tx - 8, ty - 24), (tx + 8, ty - 25)]
    for (px, py), (qx, qy) in zip(poles, anchors):
        for y in range(py - 7, py + 1): L.put(px, y, pick(WOOD_, 2)); occ.add((px, y))
        L.put(px - 1, py - 7, pick(WOOD_, 1)); L.put(px + 1, py - 7, pick(WOOD_, 1))
        n = abs(qx - px)
        for k in range(n + 1):                                     # the cable, sagging between tower and pole
            u = k / max(1, n); x = round(px + (qx - px) * u)
            y = round(py - 7 + (qy - py + 7) * u + 3 * math.sin(math.pi * u))
            if (x, y) not in tw: L.put(x, y, INK)

    # --- the Abandoned Bus
    bx, by = A['bus']
    bus = set()
    for y in range(by - 7, by - 1):
        for x in range(bx - 9, bx + 10):
            c = pick(VERD, 2 if y > by - 4 else 3)
            if y == by - 6 and (x - bx) % 3 == 0: c = INK                            # dead windows
            if y in (by - 5, by - 4) and (x - bx) % 4 in (1, 2) and abs(x - bx) < 8: c = pick(SLATE, 1)
            if h32(x, y, 7) % 7 == 0: c = pick(RUST, 3)
            L.put(x, y, c); bus.add((x, y))
    outline(L, bus); occ |= bus
    for wx in (bx - 6, bx + 6): L.put(wx, by - 1, INK); L.put(wx + 1, by - 1, INK)

    # --- Shed 521: one walled compound -- the steel lattice gate with its green 5 21 displays and the queue of
    #     applicants outside, the yard, the tall wooden shed with its cabin on top, tin offices, rusty white pipes.
    #     (Courtyard, hall, registration and the floors are all inside, so they share this one landmark.)
    shx, shy = A['shed']
    x0, x1, y0 = shx - 26, shx + 26, shy - 22
    yard = set()
    for y in range(y0, shy + 1):
        for x in range(x0, x1 + 1):
            v = 3 + (N3(x * 3, y * 3) > 0.62) - (h32(x, y, 41) % 9 == 0)
            L.put(x, y, pick(DUST, v)); yard.add((x, y))
    for y in range(y0 - 2, shy + 1):                               # the walls: planks on the sides, a plank face at the back
        for x in range(x0 - 1, x1 + 2):
            if y < y0 or x < x0 or x > x1:
                L.put(x, y, pick(WOOD_, 2 if y == y0 - 2 or x in (x0 - 1, x1 + 1) and y % 3 else 1)); yard.add((x, y))
    for y in range(shy - 1, shy + 2):                              # the front wall
        for x in range(x0 - 1, x1 + 2):
            L.put(x, y, pick(WOOD_, 2 if y == shy - 1 else 1 - (x % 4 == 0))); yard.add((x, y))
    outline(L, yard); occ |= yard
    # the tall wooden shed: cross-braced plank walls, lit windows, the sign, a cabin on its roof
    bx0, bw, bh = shx - 16, 18, 13
    block(L, bx0, y0 - 6, bw, 4, bh, ROOF[3], wall=WOOD_, seed=521, occ=occ)
    for k in range(bh):                                            # X bracing
        for xx in (bx0 + 1 + k * 8 // bh, bx0 + 8 - k * 8 // bh, bx0 + 9 + k * 8 // bh, bx0 + 16 - k * 8 // bh):
            L.put(xx, y0 - 2 + k, pick(WOOD_, 3))
    for x in range(bx0 + 4, bx0 + 14): L.put(x, y0, pick(DUST, 6)); L.put(x, y0 + 1, pick(DUST, 5))   # SHED 521
    for x in range(bx0 + 5, bx0 + 13, 2): L.put(x, y0 + 1, INK)
    for (wx, wy) in ((bx0 + 11, y0 + 5), (bx0 + 13, y0 + 5), (bx0 + 11, y0 + 7), (bx0 + 13, y0 + 7), (bx0 + 12, y0 + 6)):
        G.put(wx, wy, LIGHT[3])
    block(L, bx0 + 5, y0 - 12, 8, 3, 4, ROOF[3], wall=WOOD_, seed=7, occ=occ)
    G.put(bx0 + 8, y0 - 8, LIGHT[2])
    # tin offices along the right wall (registration, the floors)
    block(L, shx + 7, y0 + 1, 9, 3, 4, ROOF[1], seed=11, occ=occ)
    block(L, shx + 16, y0 + 6, 8, 3, 4, ROOF[1], seed=12, occ=occ)
    G.put(shx + 10, y0 + 6, LIGHT[2]); G.put(shx + 19, y0 + 11, LIGHT[2])
    # the gate: two lattice towers and a beam over the opening in the front wall
    gx = shx + 4
    gate = set()
    for y in range(shy - 12, shy + 2):
        for x in (gx - 5, gx - 4, gx + 4, gx + 5):
            L.put(x, y, pick(STEEL, 3 if (x + y) % 2 else 1)); gate.add((x, y))
    for y in range(shy - 13, shy - 10):
        for x in range(gx - 6, gx + 7):
            L.put(x, y, pick(STEEL, 3 if (x + y) % 2 else 2)); gate.add((x, y))
    for x in range(gx - 3, gx + 4):
        for y in (shy - 1, shy, shy + 1): L.put(x, y, pick(DUST, 2))  # the opening
    outline(L, gate); occ |= gate
    for (dx0, w) in ((-3, 2), (1, 3)):                             # the 5 | 21 displays
        for x in range(gx + dx0, gx + dx0 + w): G.put(x, shy - 12, CORE[2])
    # the queue of applicants in their coloured cloaks, waiting along the front wall
    for i in range(8):
        x = gx - 8 - i * 2 - (i > 4)
        c = [RED, VIOLET, GLASS, BRASS, RUST, VERD][h32(i, 51) % 6]
        L.put(x, shy + 2, pick(c, 4)); L.put(x, shy + 3, pick(c, 2)); occ |= {(x, shy + 2), (x, shy + 3)}
    # rusty white pipes leaving over the left wall and running off west
    for x in range(x0 - 16, x0 + 6):
        for w in range(2):
            c = pick(SHELL, 5 - w) if h32(x, 61) % 5 else pick(RUST, 3 - w)
            L.put(x, y0 + 4 + w, c); occ.add((x, y0 + 4 + w))
    for y in range(y0 + 4, y0 + 14):
        for w in range(2): L.put(x0 - 16 + w, y, pick(SHELL, 5 - w) if h32(y, 62) % 4 else pick(RUST, 3)); occ.add((x0 - 16 + w, y))

    # --- Town Square: paved circle with a fountain
    qx, qy = A['square']
    plaza = disc(L, qx, qy - 2, 12, 8, lambda x, y: pick(COBB, 5 + ((x + y) % 4 == 0) - (math.hypot(x - qx, (y - qy + 2) * 1.5) > 10)))
    outline(L, plaza); occ |= plaza
    ftn = disc(L, qx, qy - 3, 3, 2, lambda x, y: pick(YOLK, 5))
    outline(L, ftn)

    # --- Townhall: columns + a clock tower
    thx, thy = A['townhall']
    th = block(L, thx - 12, thy - 9, 24, 4, 6, ROOF[1], occ=occ)
    for x in range(thx - 10, thx + 11, 3):
        for y in range(thy - 5, thy + 1): L.put(x, y, pick(SHELL, 3))
    clock = block(L, thx - 2, thy - 20, 5, 3, 9, ROOF[1], occ=occ)
    L.put(thx, thy - 15, pick(SHELL, 5)); L.put(thx, thy - 14, INK)

    # --- Lumen Directorate: the glasshouse among cultivation beds
    lx, ly = A['lumen']
    for row in range(3):
        for x in range(lx - 16, lx + 17):
            y = ly + 4 + row * 2
            if h32(x, row) % 5: L.put(x, y, pick(MOSS, 5 + (x % 3 == 0)))
    gh = set()
    for y in range(ly - 12, ly + 2):
        span = int(12 * math.sqrt(max(0, 1 - ((y - ly + 3) / 15) ** 2))) if y < ly - 3 else 12
        for x in range(lx - span, lx + span + 1):
            c = pick(GLASS, 3 + ((x - lx) % 4 == 0) + (y < ly - 8) - (x > lx + 8))
            L.put(x, y, c); gh.add((x, y))
    outline(L, gh); occ |= gh
    for x in range(lx - 8, lx + 9, 4): G.put(x, ly - 4, CORE[1])

    # --- Burning Bear Street: a row of houses and the bear effigy burning
    bbx, bby = A['bear']
    for i, off in enumerate((-16, -8, 6, 13)):
        block(L, bbx + off, bby - 10 + (i % 2), 6, 3, 5, ROOF[i % 4], lit=0.3, seed=i, occ=occ)
    fire = set()
    for y in range(bby - 9, bby + 1):
        for x in range(bbx - 2, bbx + 3):
            if abs(x - bbx) <= (bby - y) // 3 + 1:
                G.put(x, y, FIRE[min(4, 1 + (bby - y) // 3 + (h32(x, y) % 2))]); fire.add((x, y))
    L.put(bbx - 1, bby - 4, pick(WARM_, 1)); L.put(bbx + 1, bby - 4, pick(WARM_, 1))   # the effigy's ears in the flames
    occ |= fire

    # --- the Screaming Cork: a squat tavern, cork-coloured roof, warm windows
    kx, ky = A['cork']
    block(L, kx - 9, ky - 10, 18, 5, 6, ramp('#3a2a18 #5a4226 #7a5a34 #9a7646'), occ=occ)
    for x in (kx - 6, kx - 3, kx + 2, kx + 5): G.put(x, ky - 2, LIGHT[3]); G.put(x, ky - 1, LIGHT[2])
    L.put(kx, ky - 12, INK); L.put(kx, ky - 11, pick(BRASS, 3))                 # the hanging sign

    # --- the Harbour: piers into the bay, two boats
    hbx, hby = A['harbor']
    for px in (hbx + 4, hbx + 10, hbx + 16):
        for y in range(hby - 6, hby + 5):
            if is_water(px, y): L.put(px, y, pick(BRASS, 2)); L.put(px + 1, y, pick(BRASS, 1))
    for (bx2, by2) in ((hbx + 8, hby + 6), (hbx + 18, hby - 3)):
        boat = set()
        for x in range(bx2 - 3, bx2 + 4):
            for y in range(by2, by2 + 2): L.put(x, y, pick(WOOD_, 2 + (y == by2))); boat.add((x, y))
        outline(L, boat); L.put(bx2, by2 - 2, pick(SHELL, 4)); L.put(bx2, by2 - 1, pick(SHELL, 3))
    for y in range(hby - 8, hby - 3):
        for x in range(hbx - 8, hbx + 1): L.put(x, y, pick(ROOF[0], 2 + (y == hby - 8)))   # a warehouse
    outline(L, {(x, y) for x in range(hbx - 8, hbx + 1) for y in range(hby - 8, hby - 3)})

    # --- Echo Drain Delta: drain mouths spilling into the channels, reeds on the bars
    dx_, dy_ = A['delta']
    for (px, py) in ((dx_ - 13, dy_ - 9), (dx_ - 7, dy_ - 11)):
        pipe = disc(L, px, py, 3, 3, lambda x, y: pick(SLATE, 4 - (x > px)))
        disc(L, px + 1, py, 1.6, 1.6, lambda x, y: INK)
        outline(L, pipe)
        for t in range(5): L.put(px + 2 + t, py + 1 + t // 2, FOAM)
    for i in range(14):
        x, y = dx_ - 10 + h32(i, 4) % 22, dy_ - 4 + h32(i, 5) % 14
        if on_bar(x, y): L.put(x, y, pick(MOSS, 6)); L.put(x, y - 1, pick(MOSS, 7))

    # --- Redmass Island: crimson coral of living metal
    mx, my = A['redmass']
    for i in range(26):
        x = mx - 11 + h32(i, 6) % 22; y = my - 3 + h32(i, 7) % 9
        if not on_redmass(x, y): continue
        hgt = 2 + h32(i, 8) % 5
        for t in range(hgt):
            L.put(x + (t % 2) * (1 if h32(i) % 2 else -1), y - t, pick(RED, 2 + t * 3 // hgt + (h32(i, t) % 2)))
        L.put(x, y - hgt, pick(RED, 5))
    return L, G, occ

STONE_ = ramp('#14151a #1d1f25 #282a31 #34363e #42444c #52545c')
SCR    = ramp('#121815 #1a221e #232d28 #2d3a33 #394840 #47574e #586a5f #6c7f72')   # the Scraper's green-grey
SKIN   = ramp('#2a302f #4a5552 #6a7672 #8b9893')                                 # the staked figure's grey skin
STEEL  = ramp('#1a2228 #2a3640 #3e4f5c #567080 #7896a6')                        # the Shed gate's lattice
VIOLET = ramp('#1e1228 #321c44 #4a2a62 #663a84 #8650a8 #a874c8')                # market awnings
WARM_  = ramp('#1a1310 #2a1f19 #3a2c24 #4a3d34')
WOOD_  = ramp('#2e1a10 #4a2a17 #6b3f22 #8c5a33')

# =============================================================================================
# filler: the rest of the city (houses in the built-up quarters, trees in the green)
# =============================================================================================

def filler(occ):
    """the rest of the city: forest masses in the green, row-house blocks with alleys in the built-up quarters"""
    L, G = Layer(), Layer()
    rnd = random.Random(SEED)
    labels = set()                                             # keep MapUI's labels readable
    for (nx_, ny_) in N.values():
        for y in range(ny_ + 4, ny_ + 15):
            for x in range(nx_ - 22, nx_ + 23): labels.add((x, y))
    def blocked(x, y, pad=1):
        for yy in range(y - pad, y + pad + 1):
            for xx in range(x - pad, x + pad + 1):
                if (xx, yy) in occ or (xx, yy) in ROAD_MASK or (xx, yy) in labels or is_water(xx, yy): return True
        return not (6 <= x < W - 6 and 32 <= y < H - 24)

    # forests: a canopy texture where the noise says "wood", lit from the top left, outlined only at the edge
    canopy = set()
    for y in range(8, H - 8):
        for x in range(8, W - 8):
            if ground_ramp(x, y) is not MOSS: continue
            if fbm(x * 1.4 + 31, y * 1.4) < 0.5 or blocked(x, y, 0): continue
            canopy.add((x, y))
    for (x, y) in canopy:
        # crowns: little bumps every ~4 px, each light on its top-left
        # organic crowns: the nearest of the jittered crown centres around this pixel
        best = None
        for gy in range(y // 5 - 1, y // 5 + 2):
            for gx in range(x // 5 - 1, x // 5 + 2):
                hc = h32(gx, gy, 77)
                ccx, ccy = gx * 5 + hc % 5, gy * 5 + (hc >> 8) % 5
                dd = (x - ccx) ** 2 + (y - ccy) ** 2
                if best is None or dd < best[0]: best = (dd, ccx, ccy)
        _, cx, cy = best
        dx, dy = x - cx, y - cy
        v = 3.2 - (dx + dy) * 0.45 + (N3(x * 3, y * 3) - 0.5) * 1.4
        if (x, y + 1) not in canopy: v -= 1.2                    # crown undersides
        L.put(x, y, pick(MOSS, dither(v, x, y)))
    for (x, y) in canopy:
        for ddx, ddy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            if (x + ddx, y + ddy) not in canopy and not blocked(x + ddx, y + ddy, 0) and L.get(x + ddx, y + ddy) is None:
                L.put(x + ddx, y + ddy, pick(MOSS, 0))
    occ |= canopy

    # city blocks: a loose grid of blocks separated by 2 px alleys; each block a row of narrow houses
    BUILT = (DUST, SLATE, COBB, SAND)
    gx0, gy0 = 4, 34
    rows = []
    for by in range(gy0, H - 26, 11):
        for bx in range(gx0 + (by // 11 % 2) * 7, W - 10, 18):
            r = ground_ramp(bx + 8, by + 5)
            if r not in BUILT or rnd.random() < 0.06: continue
            rows.append((bx, by, r))
    for bx, by, r in rows:
            x = bx
            while x < bx + 16:
                w = rnd.randint(3, 6); d = rnd.randint(3, 4); hgt = rnd.randint(2, 3)
                if r is SLATE: hgt += rnd.randint(1, 4)
                y = by + rnd.randint(0, 1)
                cells = [(xx, yy) for xx in range(x, x + w) for yy in range(y, y + d + hgt)]
                if x + w > bx + 17 or any(blocked(xx, yy, 0) for xx, yy in cells):
                    x += 1; continue
                roof = ROOF[1] if r in (SLATE, DUST) and rnd.random() < 0.55 else ROOF[rnd.randrange(4)]
                pts = block(L, x, y, w, d, hgt, roof, seed=x * 7 + y, occ=occ)
                if w >= 4:                                         # a ridge line along the roof
                    for xx in range(x + 1, x + w - 1): L.put(xx, y + d // 2, pick(roof, 3))
                for xx in range(x + 1, x + w - 1, 2):
                    if rnd.random() < (0.22 if r is not SLATE else 0.35): G.put(xx, y + d + 1 + rnd.randrange(max(1, hgt - 1)), LIGHT[2])
                x += w            # row houses touch (shared walls)
    return L, G

def shadows(base, layers):
    """drop shadows to the lower right of everything standing (baked as darkened ground)"""
    L = Layer()
    for y in range(H):
        for x in range(W):
            if any(l.get(x, y) for l in layers): continue
            src = any(l.get(x - dx, y - dy) for l in layers for dx, dy in ((1, 1), (2, 1), (1, 2)))
            if src:
                c = base.get(x, y)
                if c: L.put(x, y, darken(c, 0.55))
    return L

def frame_layer():
    L = Layer()
    for y in range(H):
        for x in range(W):
            e = min(x, y, W - 1 - x, H - 1 - y)
            if e < 2: L.put(x, y, INK)
            elif e == 2: L.put(x, y, pick(MOSS, 4))
            elif e == 3: L.put(x, y, INK)
    for (cx, cy) in ((6, 6), (W - 7, 6), (6, H - 7), (W - 7, H - 7)):      # corner rivets
        for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)): L.put(cx + dx, cy + dy, pick(BRASS, 3 if (dx, dy) == (0, 0) else 1))
    return L

def darken(c, f): return tuple(int(v * f) for v in c)

def vignette():
    """darker toward the edges, and under MapUI's title (top) and legend + hint (bottom); a layer of
    translucent black, so hand edits in the Aseprite source get the same shading"""
    L = Layer()
    for y in range(H):
        for x in range(W):
            ex = min(x, W - 1 - x) / 40; ey = min(y, H - 1 - y) / 34
            f = 0.62 + 0.38 * min(1, ex, ey)
            if y < 34 and 120 < x < 280: f *= 0.82 + 0.18 * (y / 34)
            if y > 272: f *= 0.8
            f = round(f * 8) / 8                                   # banded, not a smooth airbrush
            if f < 1: L.put(x, y, (0, 0, 0, round((1 - f) * 255)))
    return L

def guides():
    """hidden Aseprite layer: where MapUI puts its node circles (red), labels (cyan), title and legend (yellow)"""
    L = Layer()
    for (nx_, ny_) in N.values():
        for a in range(32):
            t = a * math.pi / 16
            L.put(round(nx_ + 4 * math.cos(t)), round(ny_ + 4 * math.sin(t)), (255, 40, 40))
        for x in range(nx_ - 22, nx_ + 23): L.put(x, ny_ + 4, (40, 220, 255)); L.put(x, ny_ + 14, (40, 220, 255))
        for y in range(ny_ + 4, ny_ + 15): L.put(nx_ - 22, y, (40, 220, 255)); L.put(nx_ + 22, y, (40, 220, 255))
    for x in range(120, 281): L.put(x, 34, (255, 220, 40))
    for x in range(4, W - 4): L.put(x, 272, (255, 220, 40))
    return L

def palette(path):
    """every ramp above as an Aseprite palette (map.gpl)"""
    is_col = lambda c: isinstance(c, tuple) and len(c) == 3 and all(isinstance(v, int) for v in c)
    cols = []
    for v in list(globals().values()):
        ramps = v if isinstance(v, list) and v and isinstance(v[0], list) else [v]
        for r in ramps:
            if isinstance(r, list) and r and all(is_col(c) for c in r):
                cols += [c for c in r if c not in cols]
        if is_col(v) and v not in cols: cols.append(v)
    with open(path, 'w') as fh:
        fh.write('GIMP Palette\nName: Upper Morkezela map\nColumns: 8\n#\n')
        for c in cols: fh.write('%3d %3d %3d\n' % c)

def main(out):
    os.makedirs(os.path.join(out, 'layers'), exist_ok=True)
    ground = draw_ground(); water = draw_water(); roads = draw_roads()
    marks, glow, occ = landmarks()
    town, tglow = filler(occ)
    shade = shadows(ground, [marks, town])
    for y in range(H):                                              # one light layer
        for x in range(W):
            if tglow.get(x, y) and not glow.get(x, y): glow.put(x, y, tglow.get(x, y))
    frame = frame_layer()
    # the same order as the layers of assets/aseprite/UI_Map_400x300.aseprite (map_aseprite.lua)
    layers = [('zeme', ground), ('voda', water), ('cesty', roads), ('stiny', shade), ('mesto', town), ('mista', marks),
              ('svetla', glow), ('vineta', vignette()), ('ramecek', frame)]
    comp = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    for name, lay in layers:
        im = lay.image()
        im.save(os.path.join(out, 'layers', f'{name}.png'))
        comp.alpha_composite(im)
    guides().image().save(os.path.join(out, 'layers', 'voditka.png'))
    palette(os.path.join(out, 'map.gpl'))
    comp.convert('RGB').save(os.path.join(out, 'map.png'))
    comp.convert('RGB').resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(out, 'map_preview.png'))
    print('ok', out)

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '/tmp/map_out')
