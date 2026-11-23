"""The panels' weathered look -- pixel art at the UI's 2x grid (one art pixel = 2 game pixels), instead of clean canvas
shapes. Two moods, after the two panel sets (ui/panelStyle.js):
  apprentice  rot: a rotting workbench, weeds and moss through its cracks, a cracked mouldy leather mat, the satchel,
              a water-stained note on a rusty nail
  office      industrial-biomechanical: a corroded riveted cabinet with flaking paint, verdigris brass, flesh veins clamped
              along the frame, roots, a fogged cracked glass; an index card with rust from its clip, a coffee ring, mould

python3 ui_grime.py <outdir>   ->  <outdir>/<name>.png (assets/images/ui/grime/), shown at scale 2, nearest-neighbour
"""
import sys, os, math, random
from PIL import Image
from common import ramp, hx, band, make_noise
from symbionts import norm, lit

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
os.makedirs(OUT, exist_ok=True)

IRON = ramp('#0f1113 #16191b #1d2124 #252a2d #2f3538 #3a4043 #474d4f #585e5e #6b706d')
RUST = ramp('#1c0e07 #2b150a #3e1e0d #542911 #6c3616 #84451c #9b5624 #b16a2e #c4823d')
PAINT = ramp('#121e1a #182621 #1f3029 #273b33 #31473d #3c5548 #4a6556')
VERD = ramp('#1a302b #24463d #31604f #437a64 #5c967c #7db297')
BRASS = ramp('#261b0b #3a2a10 #523c17 #6b4f1f #846328 #9c7934 #b49144 #c9a95e #dbc282')
MOSS = ramp('#0f160a #16200e #1e2b13 #283818 #33461e #3f5524 #4d652c #5d7735 #728c42 #8aa352')
FLESH = ramp('#170a0c #251013 #36171b #4a2024 #5e2b2d #743936 #8a4a42 #a05f52 #b47a68')
BONE = ramp('#2f2a22 #3f392e #524a3c #675e4d #7d735f #948a73 #aaa088 #c0b79e')
WOOD = ramp('#0e0906 #150e09 #1d140d #261a11 #2f2116 #3a291b #463220 #533c27 #61472f')
LEATHER = ramp('#150b08 #1f100b #2a160f #361c13 #432318 #512b1d #5f3423 #6e3e2b')
FELT = ramp('#0a100c #0e1510 #121b14 #172118 #1c281d #223022')
PAPER = ramp('#4f4536 #665a47 #7e715a #978a6e #ae9f80 #c2b492 #d3c6a3 #e0d5b4 #ebe2c6')
CARD = ramp('#5a5244 #756c5a #918770 #aca288 #c4bb9f #d6ceb3 #e4ddc4 #eee8d3')
OUTL = hx('#120b09')
BLACK = (0, 0, 0)

def clamp(v, a, b): return a if v < a else b if v > b else v

def fbm(seed, W, H, cells=(40, 20, 10, 5), weights=(0.5, 0.26, 0.15, 0.09)):
    ns = [make_noise(c, seed * 7 + i * 131, W + 2 * c, H + 2 * c) for i, c in enumerate(cells)]
    tot = sum(weights)
    return lambda x, y: sum(w * n(x, y) for n, w in zip(ns, weights)) / tot

def col(rmp, v, x, y): return rmp[clamp(band(v, x, y), 0, len(rmp) - 1)]

def lerp(rmp, v):
    """a continuous colour along a ramp (for large calm areas: paper, sheet metal; no banding, so no camouflage)"""
    v = clamp(v, 0, len(rmp) - 1.001); i = int(v)
    return mixc(rmp[i], rmp[i + 1], v - i)

def mixc(a, b, t): return (round(a[0] + (b[0] - a[0]) * t), round(a[1] + (b[1] - a[1]) * t), round(a[2] + (b[2] - a[2]) * t))


class Px:
    """an RGBA pixel buffer"""
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        s.p = s.im.load()
    def ok(s, x, y): return 0 <= x < s.w and 0 <= y < s.h
    def put(s, x, y, c, a=255):
        x, y = int(math.floor(x)), int(math.floor(y))
        if s.ok(x, y): s.p[x, y] = (c[0], c[1], c[2], a)
    def a(s, x, y):
        x, y = int(x), int(y)
        return s.p[x, y][3] if s.ok(x, y) else 0
    def rgb(s, x, y): return s.p[int(x), int(y)][:3]
    def mix(s, x, y, c, t):
        """tint an existing pixel towards c by t (no effect on empty pixels)"""
        x, y = int(math.floor(x)), int(math.floor(y))
        if not s.ok(x, y) or t <= 0: return
        r, g, b, a = s.p[x, y]
        if a == 0: return
        t = min(1.0, t)
        s.p[x, y] = (round(r + (c[0] - r) * t), round(g + (c[1] - g) * t), round(b + (c[2] - b) * t), a)
    def save(s, name): s.im.save(os.path.join(OUT, name + '.png')); print('wrote', name, s.w, s.h)


# ---------------------------------------------------------------------------------------------------------------------
# growth: weeds, ivy, moss, mould; biomechanics: flesh tubes, capillaries, roots

def weeds(P, bx, by, rnd, n=7, hmax=16, up=-1, lean=0.0, dry=0.0):
    """a tuft of weeds: blades bending away from (bx, by); up=-1 grows upwards"""
    for i in range(n):
        h = rnd.uniform(0.45, 1.0) * hmax
        l = lean + rnd.uniform(-0.55, 0.55)
        x0 = bx + rnd.uniform(-2.5, 2.5)
        steps = int(h * 2)
        brown = rnd.random() < dry
        for k in range(steps + 1):
            t = k / max(1, steps)
            x = x0 + l * h * t * t * 0.9
            y = by + up * h * t
            v = 2 + t * 6 + rnd.uniform(-0.6, 0.6)
            c = col(BONE, 2 + t * 4, int(x), int(y)) if brown else col(MOSS, v, int(x), int(y))
            P.put(x, y, c)
        if rnd.random() < 0.3:              # a seed head
            x = x0 + l * h * 0.9; y = by + up * h
            P.put(x, y, BONE[6]); P.put(x + 1, y, BONE[5]); P.put(x, y + up, BONE[4])
    for k in range(rnd.randint(1, 3)):        # a broad leaf low down
        sx = 1 if rnd.random() < 0.5 else -1
        L = rnd.randint(4, 7)
        for j in range(L):
            x = bx + sx * j; y = by + up * (1 + j * 0.45)
            P.put(x, y, MOSS[4 + (j > 1)])
            if 0 < j < L - 1: P.put(x, y - up, MOSS[3])


def leaf(P, x, y, dx, dy, rnd, rot=0.0):
    """a small ivy leaf pointing (dx, dy): 2-3 tones and a dark underside"""
    L = rnd.choice((3, 4, 4, 5))
    yellow = rnd.random() < 0.06 + rot * 0.3
    base = (BONE[:6] if yellow else MOSS[:8])
    for j in range(L):
        w = [1, 2, 2, 1, 1][j] if L >= 4 else [1, 2, 1][j]
        cx, cy = x + dx * j, y + dy * j
        for o in range(-w + 1, w):
            px, py = cx - dy * o, cy + dx * o
            light = 5 if o < 0 else 3
            P.put(px, py, base[min(len(base) - 1, light + (j == 1))])
        P.put(cx - dy * w + dx, cy + dx * w + dy, OUTL)


def ivy(P, x, y, rnd, length=60, dirx=0.0, diry=1.0, wander=0.5, leafy=0.6, rot=0.0):
    """a creeping vine from (x, y) heading (dirx, diry)"""
    a = math.atan2(diry, dirx)
    side = 1
    for k in range(length):
        a += rnd.uniform(-wander, wander) * 0.35
        x += math.cos(a); y += math.sin(a)
        P.put(x, y, MOSS[2] if k % 3 else MOSS[1])
        if k % 3 == 0 and rnd.random() < leafy:
            side = -side
            nx, ny = -math.sin(a) * side, math.cos(a) * side
            leaf(P, x + nx, y + ny, round(nx + math.cos(a) * 0.4), round(ny + math.sin(a) * 0.4) or 1, rnd, rot)
        if rnd.random() < 0.025 and length - k > 10:
            ivy(P, x, y, rnd, (length - k) // 2, math.cos(a + 0.9 * side), math.sin(a + 0.9 * side), wander, leafy, rot)


def moss(P, cx, cy, rx, ry, rnd, f, top_light=True):
    """a clump of moss: dithered greens, lighter on top, fuzzy rim"""
    for y in range(int(cy - ry) - 2, int(cy + ry) + 3):
        for x in range(int(cx - rx) - 2, int(cx + rx) + 3):
            u, w = (x - cx) / rx, (y - cy) / ry
            d = u * u + w * w + (f(x, y) - 0.5) * 0.9
            if d > 1: continue
            if d > 0.75 and rnd.random() < 0.5: continue
            v = 2.5 + (1 - d) * 2.5 + (-w * 1.6 if top_light else 0) + (f(x * 3, y * 3) - 0.5) * 2.5
            P.put(x, y, col(MOSS, v, x, y))
            if rnd.random() < 0.04: P.put(x, y, MOSS[8])


def mould(P, cx, cy, r, rnd, tint=(150, 160, 135), dark=(60, 70, 50), strength=0.75):
    """a mould bloom on a surface: dark core spots, a pale fuzzy ring, spores around"""
    for y in range(int(cy - r * 1.5), int(cy + r * 1.5) + 1):
        for x in range(int(cx - r * 1.5), int(cx + r * 1.5) + 1):
            d = math.hypot(x - cx, (y - cy) * 1.1) / r
            j = rnd.random()
            if d < 0.35 and j < 0.55: P.mix(x, y, dark, strength * 0.8)
            elif d < 1.0 and j < 0.75 - d * 0.3: P.mix(x, y, tint, strength * (1.05 - d * 0.6))
            elif d < 1.5 and j < 0.12: P.mix(x, y, tint, strength * 0.6)


def tube(P, pts, r, rnd, seg=6, clamps=(), ramp_=FLESH, wet=True):
    """a fleshy tube along pts: dark outline, cylinder shading lit from top-left, segment rings, rusty clamps"""
    # resample the path every 0.5 px
    path = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) * 2))
        for i in range(n): t = i / n; path.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    path.append(pts[-1])
    s = 0.0
    out = {}
    rings, at = [], rnd.uniform(4, 10)
    while at < len(path):
        rings.append(at); at += rnd.uniform(9, 22)
    veins = [(rnd.uniform(-0.7, 0.7), rnd.uniform(0, 6.28), rnd.uniform(0.05, 0.12)) for _ in range(3)]
    for i, (x, y) in enumerate(path):
        x2, y2 = path[min(i + 1, len(path) - 1)]; x1, y1 = path[max(i - 1, 0)]
        tx, ty = x2 - x1, y2 - y1; L = math.hypot(tx, ty) or 1; tx, ty = tx / L, ty / L
        nx, ny = -ty, tx
        if i: s += math.hypot(x - path[i - 1][0], y - path[i - 1][1])
        rr = r * (1 + 0.12 * math.sin(s * 0.35) + 0.08 * math.sin(s * 1.3))
        for k in range(-int(rr * 2) - 2, int(rr * 2) + 3):
            d = k / 2
            px, py = int(math.floor(x + nx * d)), int(math.floor(y + ny * d))
            if abs(d) > rr + 0.6:
                continue
            if abs(d) > rr - 0.3:
                out.setdefault((px, py), OUTL); continue
            u = d / rr
            z = math.sqrt(max(0.0, 1 - u * u))
            l = lit(norm((nx * u, ny * u, z)))
            ring = min(abs(s - q) for q in rings) if rings else 9
            v = 1.0 + l * 5.6 - (1.1 if ring < 0.7 else 0.45 if ring < 1.4 else 0) + (rnd.random() - 0.5) * 0.5
            c = col(ramp_, v, px, py)
            for (vo, ph, fr) in veins:
                if abs(u - (vo + 0.25 * math.sin(s * fr * 6 + ph))) < 0.09: c = ramp_[max(0, ramp_.index(c) - 2)] if c in ramp_ else c
            if wet and l > 0.92 and rnd.random() < 0.5: c = ramp_[-1]
            out[(px, py)] = c
        for cs in clamps:
            if abs(s - cs) < 1.6:
                for k in range(-int(rr * 2) - 3, int(rr * 2) + 4):
                    d = k / 2; px, py = int(math.floor(x + nx * d)), int(math.floor(y + ny * d))
                    out[(px, py)] = col(RUST, 3 + (1 - abs(d) / (rr + 1.5)) * 4 + (1 if abs(s - cs) < 0.6 else 0), px, py)
    for (px, py), c in out.items():
        if c is OUTL and P.a(px, py) and (px, py) in out and out[(px, py)] is not OUTL: continue
        P.put(px, py, c)
    return path


def capillaries(P, x, y, rnd, n=30, a=None, depth=0, colr=FLESH[3], t=0.55):
    """thin veins spreading over a surface (tints what is there)"""
    a = rnd.uniform(0, 2 * math.pi) if a is None else a
    for k in range(n):
        a += rnd.uniform(-0.5, 0.5)
        x += math.cos(a); y += math.sin(a)
        P.mix(x, y, colr, t * (1 - k / n * 0.6))
        if depth < 3 and rnd.random() < 0.08:
            capillaries(P, x, y, rnd, int((n - k) * 0.6), a + rnd.choice((-0.8, 0.8)), depth + 1, colr, t * 0.8)


def root(P, x, y, rnd, n=40, a=math.pi / 2, w=2.0):
    """a pale root creeping from (x, y), thinning"""
    for k in range(n):
        a += rnd.uniform(-0.35, 0.35)
        x += math.cos(a); y += math.sin(a)
        ww = max(0.6, w * (1 - k / n))
        for o in range(-int(ww), int(ww) + 1):
            px, py = x - math.sin(a) * o * 0.8, y + math.cos(a) * o * 0.8
            P.put(px, py, BONE[min(5, 3 + (o < 0) + (k % 5 == 0))] if abs(o) < ww else BONE[1])
        if rnd.random() < 0.07 and n - k > 6:
            root(P, x, y, rnd, (n - k) // 2, a + rnd.choice((-0.9, 0.9)), ww * 0.6)


def rivet(P, x, y, rust=0.0):
    """a 3x3 rivet head lit from the top-left, rust round it"""
    for dx, dy, c in ((0, 0, IRON[7]), (1, 0, IRON[6]), (2, 0, IRON[4]), (0, 1, IRON[6]), (1, 1, IRON[5]), (2, 1, IRON[3]),
                      (0, 2, IRON[4]), (1, 2, IRON[3]), (2, 2, IRON[1])):
        P.put(x + dx, y + dy, mixc(c, RUST[4], rust))
    P.put(x + 3, y + 1, IRON[0]); P.put(x + 1, y + 3, IRON[0]); P.put(x + 3, y + 3, IRON[0])


def streak(P, x, y, rnd, L, colr, t0=0.55):
    """a rust / verdigris drip running down from (x, y)"""
    for k in range(L):
        if rnd.random() < 0.15: x += rnd.choice((-1, 1)) * 0.5
        P.mix(x, y + k, colr, t0 * (1 - k / L) ** 1.3)
        if k < L * 0.4 and rnd.random() < 0.4: P.mix(x + 1, y + k, colr, t0 * 0.5 * (1 - k / L))


def vignette(P, strength=0.75, inner=0.45):
    for y in range(P.h):
        for x in range(P.w):
            u, v = (x / P.w - 0.5) * 2, (y / P.h - 0.5) * 2
            d = max(0.0, math.hypot(u * 0.9, v) - inner) / (1.25 - inner)
            P.mix(x, y, BLACK, min(1.0, d * strength))


# ---------------------------------------------------------------------------------------------------------------------
# iron: plates, paint, rust

def iron_surface(P, x0, y0, x1, y1, seed, paint=0.55, rustiness=0.5, f=None, base=3.0):
    """corroded iron with flaking industrial paint over [x0, x1) x [y0, y1)"""
    f = f or fbm(seed, P.w, P.h)
    g = fbm(seed + 5, P.w, P.h, cells=(14, 7, 3), weights=(0.5, 0.3, 0.2))
    for y in range(y0, y1):
        for x in range(x0, x1):
            n, m = f(x, y), g(x, y)
            low = (y - y0) / max(1, y1 - y0)
            r = n * 0.7 + m * 0.5 + low * 0.25 * rustiness
            painted = m * 0.6 + n * 0.5 < paint
            if r > 1.05 - rustiness * 0.5:              # rust through
                v = 2 + (m - 0.3) * 6 + (n - 0.5) * 2
                c = col(RUST, v, x, y)
                if random.random() < 0.06: c = RUST[1]       # pitting
            elif painted:
                v = base - 0.4 + (n - 0.5) * 3 + (m - 0.5) * 1.5
                c = col(PAINT, v, x, y)
            else:
                v = base + (n - 0.5) * 3 + (m - 0.5) * 2
                c = col(IRON, v, x, y)
            P.put(x, y, c)
    # chipped paint edges: a light lip where the paint ends
    for y in range(y0 + 1, y1 - 1):
        for x in range(x0 + 1, x1 - 1):
            c = P.rgb(x, y)
            if c in PAINT and P.rgb(x + 1, y + 1) not in PAINT and P.rgb(x + 1, y + 1) not in RUST:
                P.put(x, y, PAINT[min(len(PAINT) - 1, PAINT.index(c) + 2)])


def bevel(P, x0, y0, x1, y1, hi=0.35, lo=0.55, w=1):
    for k in range(w):
        for x in range(x0 + k, x1 - k): P.mix(x, y0 + k, (230, 220, 190), hi * (1 - k / w)); P.mix(x, y1 - 1 - k, BLACK, lo * (1 - k / w))
        for y in range(y0 + k, y1 - k): P.mix(x0 + k, y, (230, 220, 190), hi * 0.7 * (1 - k / w)); P.mix(x1 - 1 - k, y, BLACK, lo * (1 - k / w))


def brass(P, x0, y0, x1, y1, seed, patina=0.45):
    f = fbm(seed, P.w, P.h, cells=(10, 5, 3), weights=(0.5, 0.3, 0.2))
    for y in range(y0, y1):
        for x in range(x0, x1):
            n = f(x, y)
            v = 4.2 - (y - y0) / max(1, y1 - y0) * 2.4 + (n - 0.5) * 2.4
            c = col(BRASS, v, x, y)
            if n > 1 - patina * 0.75 or (y > y1 - 3 and n > 0.45): c = col(VERD, 1.5 + (n - 0.5) * 5, x, y)
            P.put(x, y, c)
    bevel(P, x0, y0, x1, y1, 0.4, 0.6)


# ---------------------------------------------------------------------------------------------------------------------
# the office: backdrop, cabinet, glass, index card, clip

def backdrop_office():
    W, H = 534, 300
    P = Px(W, H); rnd = random.Random(11); random.seed(11)
    f = fbm(3, W, H)
    # plates in staggered rows
    rows = [0, 34, 92, 150, 208, 262, 300]
    for ri in range(len(rows) - 1):
        y0, y1 = rows[ri], rows[ri + 1]
        x = -rnd.randint(0, 60)
        while x < W:
            w = rnd.randint(90, 140)
            iron_surface(P, max(0, x), y0, min(W, x + w), y1, 30 + ri * 7 + x, paint=0.42, rustiness=0.55, f=f, base=2.6)
            bevel(P, max(0, x), y0, min(W, x + w), y1, 0.18, 0.7)
            for xx in range(max(0, x) + 4, min(W, x + w) - 3, 9):
                rivet(P, xx, y0 + 3, rust=rnd.random() * 0.6)
                if rnd.random() < 0.35: streak(P, xx + 1, y0 + 6, rnd, rnd.randint(8, 34), RUST[5], 0.5)
            x += w
    # the brass pipe along the top, flanges, verdigris dripping
    py = 13
    for x in range(W):
        for d in range(-6, 7):
            u = d / 6.5
            if abs(u) > 1: continue
            z = math.sqrt(1 - u * u); l = lit(norm((0, u, z)))
            n = f(x * 2, py + d)
            c = col(BRASS, 1 + l * 6.5 + (n - 0.5) * 2, x, py + d)
            if n > 0.62: c = col(VERD, 1 + l * 4, x, py + d)
            P.put(x, py + d, c)
        P.put(x, py - 7, OUTL); P.put(x, py + 7, OUTL)
    for fx in range(40, W, 118):
        for x in range(fx - 3, fx + 4):
            for d in range(-9, 10):
                u = d / 9.5; z = math.sqrt(max(0, 1 - u * u)); l = lit(norm((0, u, z)))
                P.put(x, py + d, col(BRASS, 0.8 + l * 5 + (x == fx - 3) * 1.5, x, py + d))
        rivet(P, fx - 1, py - 8, 0.5); rivet(P, fx - 1, py + 5, 0.5)
        streak(P, fx, py + 10, rnd, rnd.randint(20, 60), VERD[3], 0.55)
        streak(P, fx + 2, py + 10, rnd, rnd.randint(10, 30), VERD[4], 0.4)
    # flesh tubes along the bottom, clamped, with capillaries; roots from the top-right
    tube(P, [(-5, 288), (60, 283), (130, 290), (205, 279), (270, 286), (330, 276), (400, 284), (470, 274), (540, 281)], 5.5, rnd,
         clamps=(70, 200, 330, 470))
    tube(P, [(-5, 270), (30, 266), (60, 272), (95, 262), (118, 236), (122, 200), (116, 160), (124, 120), (120, 80), (112, 40), (114, 24)], 3.0, rnd,
         clamps=(60, 170, 250))
    tube(P, [(540, 250), (515, 246), (500, 220), (504, 180), (498, 120), (502, 60), (496, 22)], 3.5, rnd, clamps=(40, 140, 230))
    for _ in range(22):
        capillaries(P, rnd.uniform(0, W), rnd.uniform(240, 296), rnd, rnd.randint(14, 40))
    for _ in range(6):
        root(P, rnd.uniform(380, 534), 0, rnd, rnd.randint(30, 70), math.pi / 2 + rnd.uniform(-0.6, 0.6), 1.8)
    # moss in the bottom corners and weeds out of the floor seam
    fm = fbm(77, W, H, cells=(6, 3), weights=(0.6, 0.4))
    for cx in (12, 60, 350, 522):
        moss(P, cx, 296, rnd.randint(14, 26), 9, rnd, fm)
    for bx in (8, 30, 90, 180, 300, 362, 430, 520):
        weeds(P, bx, 299, rnd, n=rnd.randint(5, 9), hmax=rnd.randint(10, 20), dry=0.2)
    ivy(P, 2, 32, rnd, 120, 0.15, 1, 0.6, 0.7, rot=0.2)
    vignette(P, 0.85, 0.35)
    P.save('backdrop_office')


CAB_W, CAB_H, CAB_IN, CAB_DIV, CAB_M = 330, 235, 12, 4, 12    # the drawer 660 x 470 at 2x; margin for the overgrowth


def cabinet():
    W, H, M, IN = CAB_W, CAB_H, CAB_M, CAB_IN
    P = Px(W + 2 * M, H + 2 * M); rnd = random.Random(5); random.seed(5)
    X0, Y0 = M, M
    f = fbm(8, P.w, P.h)
    # frame
    iron_surface(P, X0, Y0, X0 + W, Y0 + H, 41, paint=0.62, rustiness=0.45, f=f, base=3.4)
    bevel(P, X0, Y0, X0 + W, Y0 + H, 0.4, 0.8, 2)
    # inside: damp felt, dividers
    IX, IY, IW, IH = X0 + IN, Y0 + IN, W - 2 * IN, H - 2 * IN
    ff = fbm(9, P.w, P.h, cells=(18, 8, 4, 2), weights=(0.4, 0.3, 0.2, 0.1))
    for y in range(IY, IY + IH):
        for x in range(IX, IX + IW):
            n = ff(x, y)
            v = 2.2 + (n - 0.5) * 3 - max(0, 3 - (y - IY)) * 0.6 - max(0, 3 - (x - IX)) * 0.6
            P.put(x, y, col(FELT, v, x, y))
    for _ in range(14): mould(P, rnd.uniform(IX, IX + IW), rnd.uniform(IY, IY + IH), rnd.uniform(3, 9), rnd, (110, 125, 100), (20, 26, 18), 0.5)
    for _ in range(10): streak(P, rnd.uniform(IX, IX + IW), IY, rnd, rnd.randint(10, 50), (40, 48, 30), 0.35)   # damp running down
    COLS, ROWS, D = 5, 3, CAB_DIV
    CW, CH = (IW - (COLS - 1) * D) / COLS, (IH - (ROWS - 1) * D) / ROWS
    for i in range(1, COLS):
        x0 = round(IX + i * (CW + D) - D)
        iron_surface(P, x0, IY, x0 + D, IY + IH, 60 + i, paint=0.5, rustiness=0.6, f=f, base=3.8)
        bevel(P, x0, IY, x0 + D, IY + IH, 0.4, 0.6)
        for x in range(x0 + D, x0 + D + 2):
            for y in range(IY, IY + IH): P.mix(x, y, BLACK, 0.45 if x == x0 + D else 0.2)
    for j in range(1, ROWS):
        y0 = round(IY + j * (CH + D) - D)
        iron_surface(P, IX, y0, IX + IW, y0 + D, 70 + j, paint=0.5, rustiness=0.6, f=f, base=3.8)
        bevel(P, IX, y0, IX + IW, y0 + D, 0.4, 0.6)
        for x in range(IX, IX + IW):
            P.mix(x, y0 + D, BLACK, 0.45); P.mix(x, y0 + D + 1, BLACK, 0.2)
            if rnd.random() < 0.05: streak(P, x, y0 + D, rnd, rnd.randint(4, 16), RUST[5], 0.45)
        for i in range(1, COLS):
            rivet(P, round(IX + i * (CW + D) - D), y0, 0.5)
    for y in range(IY, IY + 5):
        for x in range(IX, IX + IW): P.mix(x, y, BLACK, 0.5 * (1 - (y - IY) / 5))
    for x in range(IX, IX + 5):
        for y in range(IY, IY + IH): P.mix(x, y, BLACK, 0.45 * (1 - (x - IX) / 5))
    # rivets round the frame, rust running from them
    for x in range(X0 + 5, X0 + W - 5, 11):
        rivet(P, x, Y0 + 4, rnd.random() * 0.7); rivet(P, x, Y0 + H - 8, rnd.random() * 0.7)
        if rnd.random() < 0.4: streak(P, x + 1, Y0 + H - 5, rnd, rnd.randint(4, 10), RUST[5], 0.6)
    for y in range(Y0 + 16, Y0 + H - 12, 11):
        rivet(P, X0 + 4, y, rnd.random() * 0.7); rivet(P, X0 + W - 8, y, rnd.random() * 0.7)
        if rnd.random() < 0.5: streak(P, X0 + 5, y + 3, rnd, rnd.randint(6, 16), RUST[5], 0.5)
    # corner plates
    for cx, cy in ((X0, Y0), (X0 + W - 18, Y0), (X0, Y0 + H - 18), (X0 + W - 18, Y0 + H - 18)):
        iron_surface(P, cx, cy, cx + 18, cy + 18, 90 + cx + cy, paint=0.2, rustiness=0.8, f=f, base=4.2)
        bevel(P, cx, cy, cx + 18, cy + 18, 0.45, 0.8)
        for dx, dy in ((3, 3), (12, 3), (3, 12), (12, 12)): rivet(P, cx + dx, cy + dy, 0.4)
    # the brass handle and the title plate
    brass(P, X0 + W // 2 - 35, Y0 + H - 7, X0 + W // 2 + 35, Y0 + H - 2, 13, 0.55)
    brass(P, X0 + W // 2 - 48, Y0 + 1, X0 + W // 2 + 48, Y0 + 11, 14, 0.4)
    for dx in (-45, 43): rivet(P, X0 + W // 2 + dx, Y0 + 4, 0.3)
    # a flesh tube along the top, clamped, down the right side and into the frame; capillaries on the iron
    tube(P, [(X0 + 70, Y0 - 2), (X0 + 120, Y0 - 6), (X0 + 190, Y0 - 3), (X0 + 260, Y0 - 7), (X0 + W - 6, Y0 - 2), (X0 + W + 4, Y0 + 20),
             (X0 + W + 2, Y0 + 80), (X0 + W + 6, Y0 + 140), (X0 + W + 3, Y0 + 200), (X0 + W - 4, Y0 + H - 14)], 3.2, rnd,
         clamps=(30, 120, 210, 300, 420))
    tube(P, [(X0 + 70, Y0 - 2), (X0 + 52, Y0 + 2), (X0 + 40, Y0 + 7)], 2.4, rnd)
    for _ in range(18):
        capillaries(P, X0 + W + rnd.uniform(-10, -2), Y0 + rnd.uniform(10, H - 10), rnd, rnd.randint(8, 22), a=math.pi + rnd.uniform(-0.6, 0.6))
    for _ in range(8):
        capillaries(P, X0 + rnd.uniform(60, W - 10), Y0 + rnd.uniform(1, 4), rnd, rnd.randint(6, 14), a=math.pi / 2 + rnd.uniform(-0.6, 0.6))
    # roots hanging into the top row from the frame's seam
    for x in (IX + 20, IX + 105, IX + 230, IX + 290):
        root(P, x, IY, rnd, rnd.randint(6, 12), math.pi / 2 + rnd.uniform(-0.4, 0.4), 0.8)
    # growth: ivy down the left side, moss and weeds on the bottom
    ivy(P, X0 + 3, Y0 + 2, rnd, 150, -0.05, 1, 0.55, 0.75, rot=0.25)
    ivy(P, X0 + 20, Y0 + 1, rnd, 60, 1, 0.2, 0.6, 0.7, rot=0.25)
    fm = fbm(55, P.w, P.h, cells=(6, 3), weights=(0.6, 0.4))
    for cx, rx in ((X0 + 8, 16), (X0 + 90, 10), (X0 + W - 30, 20)):
        moss(P, cx, Y0 + H + 1, rx, 6, rnd, fm)
    for bx in (X0 + 2, X0 + 14, X0 + 40, X0 + 120, X0 + 230, X0 + W - 40, X0 + W - 14):
        weeds(P, bx, Y0 + H + 4, rnd, n=rnd.randint(5, 9), hmax=rnd.randint(8, 18), dry=0.3)
    P.save('cabinet')


def cabinet_glass():
    IW, IH = CAB_W - 2 * CAB_IN, CAB_H - 2 * CAB_IN
    P = Px(IW, IH); rnd = random.Random(21)
    f = fbm(22, IW, IH, cells=(30, 12, 5), weights=(0.5, 0.3, 0.2))
    for y in range(IH):
        for x in range(IW):
            n = f(x, y)
            a = 0
            if n > 0.56: a = int((n - 0.56) * 260)            # a grime film
            edge = min(x, y, IW - 1 - x, IH - 1 - y)
            if edge < 6: a += int((6 - edge) * 10)
            if y > IH - 14: a += int((y - (IH - 14)) * 4)     # condensation low down
            # faint reflections
            dd = (x + y * 0.55) % 120
            if 14 < dd < 22 or 40 < dd < 42: a = max(a, 16)
            if a: P.put(x, y, (190, 200, 185) if (dd < 45 and a <= 18) else (70, 72, 56), min(110, a))
    for _ in range(80):                                        # droplets on the lower glass
        x, y = rnd.uniform(4, IW - 4), rnd.uniform(IH - 24, IH - 3)
        P.put(x, y, (200, 210, 200), 90); P.put(x + 1, y + 1, (40, 44, 36), 80)
    def crack(x, y, a, n, depth=0):
        for k in range(n):
            a += rnd.uniform(-0.35, 0.35)
            x += math.cos(a); y += math.sin(a)
            P.put(x, y, (205, 212, 205), 85)
            P.put(x + 1, y + 1, (20, 20, 16), 55)
            if depth < 2 and rnd.random() < 0.05: crack(x, y, a + rnd.choice((-0.9, 0.9)), (n - k) // 2, depth + 1)
    crack(IW - 4, 8, math.pi * 0.82, 70); crack(IW - 4, 8, math.pi * 0.62, 40)
    crack(30, IH - 4, -math.pi * 0.3, 45)
    P.save('cabinet_glass')


def stains_on_paper(P, rnd, f, x0, y0, x1, y1, ramp_, rust_at=None, coffee=None, mould_at=(), tide=None, fox=40, blot=0.6):
    """age a paper: edges, foxing, a tide line, a coffee ring, rust round a pin / clip, mould in a corner"""
    W, H = x1 - x0, y1 - y0
    for y in range(y0, y1):
        for x in range(x0, x1):
            if not P.a(x, y): continue
            edge = min(x - x0, y - y0, x1 - 1 - x, y1 - 1 - y)
            if edge < 5: P.mix(x, y, (110, 80, 40), (5 - edge) * 0.07 + f(x * 2, y * 2) * 0.1)
            n = f(x, y)
            if n > 0.64: P.mix(x, y, (120, 90, 50), (n - 0.64) * blot)
    for _ in range(fox):                                       # foxing: rust-brown dots in little clusters
        cx, cy = rnd.uniform(x0 + 3, x1 - 3), rnd.uniform(y0 + 3, y1 - 3)
        for _ in range(rnd.randint(1, 5)):
            P.mix(cx + rnd.uniform(-3, 3), cy + rnd.uniform(-3, 3), (130, 80, 40), rnd.uniform(0.25, 0.6))
    if tide:                                                   # a dried water stain with a dark tide line
        tx, ty, tr = tide
        g = fbm(99, P.w, P.h, cells=(8, 4), weights=(0.6, 0.4))
        for y in range(int(ty - tr * 1.6), int(ty + tr * 1.6)):
            for x in range(int(tx - tr * 1.6), int(tx + tr * 1.6)):
                d = math.hypot(x - tx, y - ty) / tr + (g(x, y) - 0.5) * 0.7
                if d < 0.92: P.mix(x, y, (150, 125, 80), 0.18)
                elif d < 1.02: P.mix(x, y, (105, 75, 40), 0.55)
    if coffee:                                                 # a coffee ring
        cx, cy, r = coffee
        for k in range(int(r * 8)):
            a = k / (r * 8) * math.pi * 2
            if 0.3 < (a % (math.pi * 2)) < 0.55: continue
            for dr in (-0.5, 0, 0.6):
                P.mix(cx + math.cos(a) * (r + dr), cy + math.sin(a) * (r + dr) * 0.92, (100, 62, 30), 0.45 if dr == 0 else 0.22)
        for y in range(int(cy - r), int(cy + r)):
            for x in range(int(cx - r), int(cx + r)):
                if math.hypot(x - cx, y - cy) < r - 1: P.mix(x, y, (140, 100, 55), 0.07)
    if rust_at:                                                # rust bleeding from a nail / a clip
        rx, ry, rr = rust_at
        for y in range(int(ry - rr * 2), int(ry + rr * 3)):
            for x in range(int(rx - rr * 2), int(rx + rr * 2)):
                d = math.hypot(x - rx, (y - ry) * (0.6 if y > ry else 1)) / rr
                if d < 1.6: P.mix(x, y, RUST[5], max(0, 0.6 - d * 0.35) + f(x * 3, y * 3) * 0.15)
    for mx, my, mr in mould_at:
        mould(P, mx, my, mr, rnd, (120, 135, 110), (40, 52, 36), 0.7)
        for _ in range(int(mr * 3)):
            P.mix(mx + rnd.uniform(-mr * 2, mr * 2), my + rnd.uniform(-mr * 2, mr * 2), (60, 75, 50), 0.4)


def labels_office():
    for k in range(3):
        W, H = 50, 9
        P = Px(W, H); rnd = random.Random(200 + k)
        f = fbm(201 + k, W, H, cells=(10, 4), weights=(0.6, 0.4))
        for y in range(H):
            for x in range(W):
                if (x in (0, W - 1) or y in (0, H - 1)) and f(x * 5, y * 5) < 0.3: continue
                P.put(x, y, col(CARD, 5.6 + (f(x, y) - 0.5) * 2, x, y))
        for x in range(W):
            P.mix(x, 0, (110, 85, 50), 0.35); P.mix(x, H - 1, (70, 50, 30), 0.5)
        for y in range(H): P.mix(0, y, (110, 85, 50), 0.35); P.mix(W - 1, y, (70, 50, 30), 0.45)
        for _ in range(8): P.mix(rnd.uniform(0, W), rnd.uniform(0, H), (130, 80, 40), rnd.uniform(0.2, 0.5))
        for _ in range(2): streak(P, rnd.uniform(2, W - 2), 0, rnd, rnd.randint(3, 8), RUST[5], 0.35)
        P.put(1, 1, RUST[4]); P.put(W - 2, 1, RUST[4])          # two pins
        P.save(f'label_office_{k}')


def card_office():
    W, H = 156, 238
    P = Px(W, H); rnd = random.Random(31)
    f = fbm(32, W, H, cells=(24, 10, 4), weights=(0.5, 0.3, 0.2))
    for y in range(H):
        for x in range(W):
            P.put(x, y, col(CARD, 6.3 + (f(x, y) - 0.5) * 1.6, x, y))
    for x in range(W):                                         # the red head line and the blue rules, faded and broken
        if f(x * 3, 26) > 0.3: P.mix(x, 26, (200, 60, 50), 0.6)
        for yy in range(37, H - 4, 10):
            yr = yy + (x * 0.012)
            if f(x * 2, yr * 3) > 0.32: P.mix(x, int(yr) + (1 if (x // 37) % 2 else 0) * 0, (110, 150, 190), 0.38)
    # a torn bottom-right corner
    for y in range(H - 16, H):
        for x in range(W - 16, W):
            if (x - (W - 16)) + (y - (H - 16)) > 16 + (f(x * 4, y * 4) - 0.5) * 6: P.put(x, y, BLACK, 0)
    stains_on_paper(P, rnd, f, 0, 0, W, H, CARD, rust_at=(19, 3, 5), coffee=(141, 168, 13),
                    mould_at=((W - 12, H - 22, 4), (4, 120, 3)), tide=(150, 96, 15), fox=34)
    # a greasy thumbprint
    for y in range(-6, 7):
        for x in range(-5, 6):
            d = math.hypot(x, y * 0.85)
            if d < 6 and int(d * 1.6) % 2 == 0: P.mix(140 + x, 60 + y, (90, 70, 50), 0.12)
    P.save('card_office')


def clip_office():
    """a rusty paper clip, 11 x 24"""
    P = Px(11, 24)
    pts_outer = [(1, 22), (1, 3), (2, 1), (8, 1), (9, 3), (9, 18)]
    pts_inner = [(3, 19), (3, 5), (4, 4), (6, 4), (7, 5), (7, 21), (6, 22), (2, 22)]
    for pts, c in ((pts_outer, 0), (pts_inner, 1)):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            n = max(abs(x1 - x0), abs(y1 - y0)) * 2
            for i in range(n + 1):
                t = i / max(1, n); x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                v = 3.5 + (1 if x < 4 else -0.5) + (math.sin(y * 1.7) * 0.6)
                P.put(x, y, col(IRON, v + 2, int(x), int(y)) if (int(y) * 7 + int(x)) % 5 else RUST[5])
    P.save('clip_office')


# ---------------------------------------------------------------------------------------------------------------------
# the apprentice: backdrop, mat with the satchel, note, nail

def backdrop_apprentice():
    W, H = 534, 300
    P = Px(W, H); rnd = random.Random(17); random.seed(17)
    grain = fbm(41, W * 4, H, cells=(60, 24, 8), weights=(0.5, 0.3, 0.2))
    f = fbm(42, W, H)
    y = 0; planks = []
    while y < H:
        h = rnd.randint(38, 52); planks.append((y, min(H, y + h))); y += h
    for pi_, (y0, y1) in enumerate(planks):
        off = rnd.uniform(0, 400); base = rnd.uniform(2.6, 3.6)
        for yy in range(y0, y1):
            for x in range(W):
                g = grain(x * 0.25 + off, yy * 2.2 + pi_ * 7)
                n = f(x, yy)
                v = base + (g - 0.5) * 4 + (n - 0.5) * 1.5
                if abs(g - 0.5) < 0.012: v -= 1.5                  # grain lines
                if n > 0.66: v -= (n - 0.66) * 8                    # rot
                P.put(x, yy, col(WOOD, v, x, yy))
        for x in range(W):                                          # the gap between planks
            P.put(x, y0, WOOD[0]); P.put(x, min(H - 1, y0 + 1), WOOD[1])
            P.mix(x, min(H - 1, y0 + 2), (200, 170, 120), 0.08)
        for _ in range(rnd.randint(1, 3)):                          # cracks along the grain
            cx, cy = rnd.uniform(0, W), rnd.uniform(y0 + 6, y1 - 6)
            for k in range(rnd.randint(30, 120)):
                cx += 1; cy += rnd.uniform(-0.3, 0.3)
                P.put(cx, cy, WOOD[0])
        for _ in range(rnd.randint(2, 4)):                          # nail heads
            nx_, ny_ = rnd.uniform(10, W - 10), y0 + rnd.uniform(4, 10)
            P.put(nx_, ny_, RUST[6]); P.put(nx_ + 1, ny_, RUST[4]); P.put(nx_, ny_ + 1, RUST[3]); P.put(nx_ + 1, ny_ + 1, RUST[2])
            streak(P, nx_, ny_ + 2, rnd, rnd.randint(4, 12), RUST[4], 0.3)
    # damp patches, mould, water rings
    for _ in range(9): mould(P, rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(6, 16), rnd, (90, 100, 70), (10, 12, 8), 0.45)
    # weeds through the gaps, moss along the edges, ivy over the wood
    fm = fbm(66, W, H, cells=(6, 3), weights=(0.6, 0.4))
    for (y0, _y1) in planks[1:]:
        for _ in range(rnd.randint(3, 6)):
            x = rnd.choice((rnd.uniform(0, 18), rnd.uniform(377, 396), rnd.uniform(518, 534), rnd.uniform(0, W)))
            weeds(P, x, y0 + 1, rnd, n=rnd.randint(4, 8), hmax=rnd.randint(7, 15), dry=0.25)
    for cx, cy, rx in ((6, 40, 14), (8, 160, 18), (4, 270, 16), (386, 20, 14), (386, 290, 18), (528, 120, 14), (528, 230, 16), (200, 296, 30), (470, 4, 26)):
        moss(P, cx, cy, rx, rx * 0.6, rnd, fm)
    ivy(P, 0, 4, rnd, 140, 1, 0.25, 0.6, 0.7, rot=0.3)
    ivy(P, 533, 296, rnd, 130, -1, -0.4, 0.6, 0.7, rot=0.3)
    ivy(P, 388, 299, rnd, 90, 0.1, -1, 0.6, 0.7, rot=0.3)
    vignette(P, 0.8, 0.35)
    P.save('backdrop_apprentice')


MAT_W, MAT_H, MAT_M = 360, 270, 12


def satchel(P, ox, oy, rot, rnd):
    """the satchel tipped on its back, mouth to the right, drawn in its own rotated frame (art pixels, about 84 x 60)"""
    ca, sa = math.cos(rot), math.sin(rot)
    f = fbm(71, 140, 120, cells=(8, 4, 2), weights=(0.5, 0.3, 0.2))
    def loc(x, y):
        dx, dy = x - ox, y - oy
        return dx * ca + dy * sa, -dx * sa + dy * ca
    def body(u, v):                       # a soft rounded bag
        if not (0 <= u <= 78 and 4 <= v <= 56): return False
        r = 9
        cu, cv = min(max(u, r), 78 - r), min(max(v, 4 + r), 56 - r)
        return (u - cu) ** 2 + (v - cv) ** 2 <= r * r
    flap_edge = lambda u: 30 + 5 * (1 - ((u - 39) / 40) ** 2)
    def region(u, v):
        if ((u - 79) / 5.5) ** 2 + ((v - 30) / 21) ** 2 < 1: return 'mouth'
        if body(u, v): return 'flap' if v < flap_edge(u) else 'body'
        # the strap, lying in a loop to the right
        for k in range(40):
            t = k / 39
            sx = (1 - t) ** 3 * 74 + 3 * (1 - t) ** 2 * t * 112 + 3 * (1 - t) * t * t * 116 + t ** 3 * 78
            sy = (1 - t) ** 3 * 8 + 3 * (1 - t) ** 2 * t * -8 + 3 * (1 - t) * t * t * 62 + t ** 3 * 54
            if (u - sx) ** 2 + (v - sy) ** 2 < 4.2: return 'strap'
        return None
    X = range(int(ox - 10), int(ox + 130)); Y = range(int(oy - 30), int(oy + 90))
    reg = {}
    for y in Y:
        for x in X:
            u, v = loc(x + 0.5, y + 0.5)
            r = region(u, v)
            if r: reg[(x, y)] = (r, u, v)
            elif ((u - 40) / 46) ** 2 + ((v - 60) / 9) ** 2 < 1: P.mix(x, y, BLACK, 0.45)      # its shadow
    for (x, y), (r, u, v) in reg.items():
        n = f(u * 1.3, v * 1.3)
        if r == 'mouth':
            d = ((u - 79) / 5.5) ** 2 + ((v - 30) / 21) ** 2
            P.put(x, y, LEATHER[0] if d < 0.7 else LEATHER[2]); continue
        lift = {'flap': 1.0, 'body': 0.0, 'strap': 0.6}[r]
        vv = 2.6 + lift + (1 - v / 56) * 1.6 - (u / 80) * 0.8 + (n - 0.5) * 2.4
        c = col(LEATHER, vv, x, y)
        if n > 0.78: c = mixc(c, (150, 135, 105), 0.25)                        # scuffed
        if r == 'body' and v < flap_edge(u) + 2.2: c = LEATHER[1]             # the flap's shadow
        if r == 'flap' and flap_edge(u) - 2.6 < v < flap_edge(u) - 1.6 and int(u) % 3: c = (175, 145, 100)   # stitching
        if r == 'flap' and 34 <= u <= 44 and v > 12:                          # the tongue
            c = col(LEATHER, vv - 0.8, x, y)
        if 33 <= u <= 45 and 27 <= v <= 36:                                   # the buckle: tarnished brass frame
            inner = 35.5 <= u <= 42.5 and 29.5 <= v <= 33.5
            c = (col(BRASS, 4.5 + (n - 0.5) * 3 - (v - 27) * 0.3, x, y) if not inner else LEATHER[1])
            if not inner and n > 0.6: c = VERD[3]
        P.put(x, y, c)
    for (x, y), (r, u, v) in reg.items():                                    # a warm dark outline
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in reg: P.put(x + dx, y + dy, OUTL)
    mould(P, ox + 14, oy + 44, 6, rnd, (130, 140, 110), (30, 30, 20), 0.6)
    for _ in range(2): capillaries(P, ox + 14, oy + 44, rnd, rnd.randint(8, 14), colr=(190, 185, 160), t=0.3)


def desk_mat():
    W, H, M = MAT_W, MAT_H, MAT_M
    P = Px(W + 2 * M, H + 2 * M); rnd = random.Random(9); random.seed(9)
    X0, Y0 = M, M
    f = fbm(19, P.w, P.h)
    cr = fbm(20, P.w, P.h, cells=(9, 4), weights=(0.6, 0.4))
    R = 7
    def inside(x, y):
        cx, cy = min(max(x, X0 + R), X0 + W - R), min(max(y, Y0 + R), Y0 + H - R)
        return (x - cx) ** 2 + (y - cy) ** 2 <= R * R + (f(x * 4, y * 4) - 0.5) * 18
    # shadow under the mat
    for y in range(Y0 + 3, Y0 + H + 5):
        for x in range(X0 + 2, X0 + W + 4):
            P.put(x, y, BLACK, 140)
    for y in range(Y0, Y0 + H):
        for x in range(X0, X0 + W):
            if not inside(x + 0.5, y + 0.5): continue
            n, c_ = f(x, y), cr(x, y)
            cx, cy = (x - X0) / W - 0.5, (y - Y0) / H - 0.5
            v = 3.6 - math.hypot(cx, cy) * 2.6 + (n - 0.5) * 2.2
            c = col(LEATHER, v, x, y)
            if abs(c_ - 0.5) < 0.004 + 0.012 * min(1.0, math.hypot(cx, cy) * 1.8): c = LEATHER[1]   # craquelure, worse at the edges
            elif n > 0.66: c = mixc(c, (120, 95, 70), (n - 0.66) * 1.6)  # worn patches
            P.put(x, y, c)
    # damp rot spreading in from the edges, scratches
    damp = fbm(23, P.w, P.h, cells=(30, 14, 6), weights=(0.5, 0.3, 0.2))
    for y in range(Y0, Y0 + H):
        for x in range(X0, X0 + W):
            if not P.a(x, y): continue
            e = min(x - X0, y - Y0, X0 + W - 1 - x, Y0 + H - 1 - y)
            d = damp(x, y) + max(0, 30 - e) / 60
            if d > 0.62: P.mix(x, y, (16, 14, 8), min(0.55, (d - 0.62) * 2.2))
            if 0.6 < d < 0.625: P.mix(x, y, (110, 90, 60), 0.3)          # the tide line of the damp
    for _ in range(14):
        sx, sy, a = rnd.uniform(X0 + 20, X0 + W - 20), rnd.uniform(Y0 + 20, Y0 + H - 20), rnd.uniform(-0.6, 0.6)
        for k in range(rnd.randint(8, 30)):
            P.mix(sx + math.cos(a) * k, sy + math.sin(a) * k, (150, 120, 90), 0.3)
    # rings, a burn, mould
    for (cx, cy, r) in ((300, 70, 13), (250, 210, 9)):
        for k in range(int(r * 8)):
            a = k / (r * 8) * math.pi * 2
            P.mix(X0 + cx + math.cos(a) * r, Y0 + cy + math.sin(a) * r * 0.9, (20, 8, 6), 0.55)
    for y in range(-8, 9):
        for x in range(-11, 12):
            d = math.hypot(x / 11, y / 8)
            if d < 1: P.mix(X0 + 330 + x, Y0 + 240 + y, (8, 5, 4), (1 - d) * 0.8 + f(x * 4, y * 4) * 0.1)
    for (cx, cy, r) in ((120, 230, 9), (60, 150, 6), (330, 140, 7), (180, 40, 5)):
        mould(P, X0 + cx, Y0 + cy, r, rnd, (135, 140, 110), (30, 26, 18), 0.55)
    # a tear in the leather: the rotten board shows through and weeds come up
    tx, ty = X0 + 262, Y0 + 250
    for y in range(ty - 12, ty + 13):
        for x in range(tx - 20, tx + 21):
            d = ((x - tx) / 15) ** 2 + ((y - ty) / 7) ** 2 + (f(x * 5, y * 5) - 0.5) * 0.8
            if d < 1: P.put(x, y, col(WOOD, 2.5 + (f(x * 3, y) - 0.5) * 3 - (1.5 if d > 0.8 else 0), x, y))
            elif d < 1.25: P.put(x, y, LEATHER[0] if d < 1.12 else (120, 85, 60))
    weeds(P, tx - 5, ty + 3, rnd, n=7, hmax=12, dry=0.2); weeds(P, tx + 6, ty + 4, rnd, n=5, hmax=9, dry=0.3)
    moss(P, tx + 2, ty + 5, 8, 3, rnd, fbm(72, P.w, P.h, cells=(6, 3), weights=(0.6, 0.4)))
    # big rusty nails through the mat's corners, rust bleeding into the leather
    for (cx, cy) in ((X0 + 8, Y0 + H - 9), (X0 + W - 10, Y0 + 7), (X0 + W - 10, Y0 + H - 9)):
        for y in range(cy - 7, cy + 12):
            for x in range(cx - 7, cx + 8):
                d = math.hypot(x - cx, (y - cy) * (0.6 if y > cy else 1))
                if d < 7: P.mix(x, y, RUST[3], 0.5 - d * 0.06 + f(x * 3, y * 3) * 0.15)
        for y in range(cy - 2, cy + 3):
            for x in range(cx - 2, cx + 3):
                d = math.hypot(x - cx, y - cy)
                if d < 2.6: P.put(x, y, col(RUST, 2 + (3 - d) * 1.6 - (x - cx + y - cy) * 0.5, x, y))
        P.put(cx + 2, cy + 2, OUTL); P.put(cx + 3, cy + 1, OUTL)
    # pale roots creeping in over the bottom-left corner
    for _ in range(4): root(P, X0 + rnd.uniform(-8, 30), Y0 + H + 6, rnd, rnd.randint(25, 60), -math.pi / 2 + rnd.uniform(-0.2, 0.9), 1.6)
    satchel(P, X0 + 18, Y0 + 16, -0.22, rnd)
    # the torn bottom-right corner, weeds from under it; moss creeping on the left; ivy over the top-right
    fm = fbm(70, P.w, P.h, cells=(6, 3), weights=(0.6, 0.4))
    moss(P, X0 + 2, Y0 + H - 30, 12, 30, rnd, fm)
    moss(P, X0 + W - 6, Y0 + H - 4, 22, 8, rnd, fm)
    for bx in (X0 + W - 30, X0 + W - 14, X0 + W + 2, X0 + 6, X0 + 160):
        weeds(P, bx, Y0 + H + 6, rnd, n=rnd.randint(5, 9), hmax=rnd.randint(10, 18), dry=0.3)
    ivy(P, X0 + W + 8, Y0 - 6, rnd, 110, -0.6, 1, 0.55, 0.75, rot=0.3)
    P.save('desk_mat')


def card_apprentice():
    W, H = 125, 238
    P = Px(W, H); rnd = random.Random(41)
    f = fbm(43, W, H, cells=(24, 10, 4), weights=(0.5, 0.3, 0.2))
    for y in range(H):
        for x in range(W):
            # ragged edges
            e = min(x, W - 1 - x, y, H - 1 - y)
            if e < 2 and f(x * 5, y * 5) < 0.35: continue
            P.put(x, y, lerp(PAPER, 6.6 + (f(x, y) - 0.5) * 1.2 + (random.random() - 0.5) * 0.25))
    # a torn top-right corner and a fold across
    for y in range(0, 18):
        for x in range(W - 18, W):
            if (W - 1 - x) + y < 12 + (f(x * 4, y * 4) - 0.5) * 6: P.put(x, y, BLACK, 0)
    for x in range(W):
        yy = 150 - x * 0.18
        P.mix(x, yy, (255, 245, 220), 0.25); P.mix(x, yy + 1, (90, 70, 40), 0.25)
    stains_on_paper(P, rnd, f, 0, 0, W, H, PAPER, rust_at=(W / 2, 5, 4), coffee=(116, 232, 13),
                    mould_at=((W - 6, 150, 5), (4, 40, 3)), tide=(118, 185, 18), fox=44)
    P.save('card_apprentice')


def diary():
    """the apprentice's journal: a grimy old diary lying open, spiral-bound, pages stained and foxed, scraps sticking out;
    534 x 300 with the page areas where ui/panels/journalScreens.js writes (pages 96-432 and 440-764 at 2x)"""
    W, H = 534, 300
    P = Px(W, H); rnd = random.Random(61); random.seed(61)
    f = fbm(62, W, H)
    X0, Y0, X1, Y1 = 34, 5, 396, 296                 # the cover
    PY0, PY1 = 13, 288                                # the pages
    for y in range(Y0 + 5, Y1 + 4):                   # its shadow
        for x in range(X0 + 4, X1 + 5): P.put(x, y, BLACK, 150)
    # scraps tucked in, sticking out over the top edge (under the pages)
    for (sx, sw, sh, tone) in ((70, 34, 14, (120, 100, 70)), (150, 22, 10, (150, 160, 165)), (262, 40, 12, (175, 160, 120)), (318, 18, 16, (100, 80, 55))):
        for y in range(Y0 - 4, Y0 - 4 + sh):
            for x in range(sx, sx + sw):
                if y < Y0 and f(x * 5, y * 5) < 0.3: continue
                P.put(x, y, mixc(tone, (0, 0, 0), 0.25 * f(x, y) + (0.2 if x in (sx, sx + sw - 1) else 0)))
    # the cover: worn dark leather, rubbed corners and edges, cracks
    cr = fbm(64, W, H, cells=(9, 4), weights=(0.6, 0.4))
    for y in range(Y0, Y1):
        for x in range(X0, X1):
            cx, cy = min(x - X0, X1 - 1 - x), min(y - Y0, Y1 - 1 - y)
            if cx + cy < 4: continue
            n = f(x, y)
            v = 2.6 + (n - 0.5) * 2.2 + (random.random() - 0.5) * 0.4
            c = lerp(LEATHER, v)
            if min(cx, cy) < 2: c = mixc(c, (150, 120, 90), 0.3)                  # rubbed edges
            if cx < 12 and cy < 12 and n > 0.4: c = mixc(c, (160, 135, 100), 0.35)
            if abs(cr(x, y) - 0.5) < 0.012: c = LEATHER[0]
            P.put(x, y, c)
    # page blocks: stacked edges outside, calm aged paper inside, darker into the gutter and the edges
    pages = [(48, 216), (220, 382)]
    pf = fbm(63, W, H, cells=(40, 16, 6), weights=(0.5, 0.3, 0.2))
    for (px0, px1) in pages:
        left = px0 == 48
        for y in range(PY0 - 2, PY1 + 3):
            for x in range(px0 - 4 if left else px0, px1 + (0 if left else 4)):
                outer = (left and x < px0) or (not left and x >= px1) or y < PY0 or y >= PY1
                if outer:                                                   # the stack of page edges
                    d = (px0 - x) if (left and x < px0) else (x - px1 + 1) if (not left and x >= px1) else 0
                    if y < PY0 or y >= PY1: d = max(d, (PY0 - y) if y < PY0 else (y - PY1 + 1))
                    P.put(x, y, mixc(PAPER[4 - min(3, d)], (60, 45, 30), 0.15 if (x + y) % 3 else 0.35)); continue
                n = pf(x, y)
                edge = min(x - px0, px1 - 1 - x, y - PY0, PY1 - 1 - y)
                gutter = (px1 - x) if left else (x - px0)
                v = 6.5 + (n - 0.5) * 1.5 - max(0, 7 - edge) * 0.22 - max(0, 12 - gutter) * 0.22 + (random.random() - 0.5) * 0.3
                P.put(x, y, lerp(PAPER, v))
    for (px0, px1) in pages:
        stains_on_paper(P, rnd, pf, px0, PY0, px1, PY1, PAPER, fox=70, blot=0.35)
    stains_on_paper(P, rnd, pf, 220, PY0, 382, PY1, PAPER, coffee=(350, 248, 16), fox=0, blot=0)
    stains_on_paper(P, rnd, pf, 48, PY0, 216, PY1, PAPER, tide=(72, 262, 24), mould_at=((54, 26, 5), (377, 160, 4)), fox=0, blot=0)
    # grubby thumbs on the outer edges, older pencil writing rubbed out
    for (ex, ey) in ((52, 90), (52, 200), (378, 70), (378, 230), (150, 284), (300, 284)):
        for y in range(-10, 11):
            for x in range(-7, 8):
                d = math.hypot(x / 7, y / 10)
                if d < 1 and P.a(ex + x, ey + y) and int(d * 9) % 2 == 0: P.mix(ex + x, ey + y, (70, 55, 40), 0.13 * (1 - d) + 0.05)
    for (px0, px1) in pages:
        for k in range(rnd.randint(5, 8)):
            yy = rnd.uniform(PY0 + 20, PY1 - 20); xx = px0 + rnd.uniform(14, 40); L = rnd.uniform(40, px1 - px0 - 40)
            for j in range(int(L)):
                if f(xx * 9 + j * 3, yy * 9) > 0.45: P.mix(xx + j, yy + math.sin(j * 0.9) * 1.2, (110, 100, 90), 0.12)
    # lice and squashed bugs (it is a lousy diary)
    for (bx, by) in ((200, 120), (236, 200), (300, 266), (120, 60), (355, 110)):
        for dx, dy, c in ((0, 0, (30, 22, 16)), (1, 0, (45, 34, 24)), (0, 1, (45, 34, 24)), (-1, 1, (60, 40, 30)), (2, -1, (60, 40, 30))):
            P.put(bx + dx, by + dy, c)
        for k in range(rnd.randint(4, 8)): P.mix(bx + k, by + 1 + k * 0.3, (90, 50, 35), 0.4 * (1 - k / 8))
    for _ in range(14):
        lx, ly = rnd.uniform(52, 378), rnd.uniform(PY0 + 4, PY1 - 4)
        P.put(lx, ly, (70, 55, 40)); P.put(lx + 1, ly, (95, 75, 55))
    # a cigarette burn at the bottom of the left page
    for y in range(-6, 7):
        for x in range(-8, 9):
            d = math.hypot(x / 8, y / 6) + (f(x * 6 + 400, y * 6) - 0.5) * 0.5
            if d < 0.6: P.put(130 + x, 279 + y, (18, 11, 6))
            elif d < 1: P.mix(130 + x, 279 + y, (90, 55, 25), 0.55)
    # the Stomach Clock doodle and a spiral, in faded ink, top of the right page
    ink = (60, 52, 70)
    for k in range(64):
        a = k / 64 * math.pi * 2
        P.mix(349 + math.cos(a) * 7.5, 31 + math.sin(a) * 7.5, ink, 0.55)
    for k in range(6): P.mix(349, 31 - k, ink, 0.55); P.mix(349 + k * 0.8, 31 + k * 0.4, ink, 0.55)
    a = 0.0
    while a < 16:
        r = 0.5 + a * 0.45
        P.mix(326 + math.cos(a) * r, 31 + math.sin(a) * r, ink, 0.5); a += 0.15
    # spiral binding: rusty rings through punched holes
    for y in range(PY0 + 6, PY1 - 6, 12):
        for x in (211, 225):
            P.put(x, y, (20, 14, 10)); P.put(x + 1, y, (20, 14, 10)); P.put(x, y + 1, (40, 30, 20))
        for k in range(-9, 10):
            t = k / 9.0
            xx = 218 + k * 0.85; yy = y + 1 - math.sqrt(max(0, 1 - t * t)) * 3.2
            c = col(IRON, 5.5 - abs(t) * 2 + (0 if (k + y) % 4 else -1), int(xx), int(yy))
            if f(xx * 7, yy * 7) > 0.6: c = RUST[5]
            P.put(xx, yy, c); P.put(xx, yy + 1, OUTL if abs(t) < 0.9 else c)
    for y in range(PY0, PY1):
        for x in range(214, 222): P.mix(x, y, BLACK, 0.35 - abs(x - 218) * 0.05)
    # a rusty paper clip on the right page's edge holding a torn scrap; a strip of old tape on the left
    for y in range(PY0 + 2, PY0 + 34):
        for x in range(366, 384):
            if f(x * 4, y * 4) > 0.22 and not (x > 380 and y > PY0 + 26): P.put(x, y, lerp(PAPER, 4.6 + (f(x, y) - 0.5) * 1.5))
    for y in range(PY0 - 4, PY0 + 22):
        P.put(377, y, IRON[6] if y % 6 else RUST[5]); P.put(381, y, IRON[4] if y % 7 else RUST[4])
    for x in range(377, 382): P.put(x, PY0 - 5, IRON[5]); P.put(x, PY0 + 22, IRON[3])
    for y in range(PY1 - 32, PY1 - 18):
        for x in range(40, 68):
            if abs((y - (PY1 - 25)) - (x - 54) * 0.35) < 4.5: P.mix(x, y, (205, 190, 145), 0.55)
    # a dried weed pressed between the pages, sticking out at the bottom of the right page
    for k in range(44):
        x, y = 300 + k * 0.55, Y1 + 2 - k * 1.1
        P.put(x, y, BONE[3])
        if k % 5 == 0: P.put(x - 1, y - 1, BONE[4]); P.put(x + 1, y - 1, BONE[2])
    P.save('diary')


def plate():
    """the apprentice's quest board: a rusty sheet of metal, overgrown, people have sprayed and scribbled on it; 534 x 300"""
    W, H = 534, 300
    P = Px(W, H); rnd = random.Random(81); random.seed(81)
    f = fbm(82, W, H)
    g = fbm(83, W, H, cells=(70, 30, 12), weights=(0.5, 0.3, 0.2))
    vs = fbm(85, W * 3, H, cells=(24, 10, 4), weights=(0.5, 0.3, 0.2))       # streaky, read stretched down the sheet
    chips = fbm(86, W, H, cells=(8, 4, 2), weights=(0.5, 0.3, 0.2))
    PAINTS = [(78, 88, 92), (86, 92, 74), (104, 92, 66), (96, 70, 62)]      # faded industrial paint
    seams = [0, 142, 290, 418, 534]
    for si in range(len(seams) - 1):
        x0, x1 = seams[si], seams[si + 1]
        paint = PAINTS[si % len(PAINTS)]
        for y in range(H):
            for x in range(x0, x1):
                n, m = f(x, y), g(x + si * 50, y)
                dent = math.sin((x - x0) / (x1 - x0) * math.pi) * 0.5 + (m - 0.5) * 1.2
                metal = lerp(IRON, 3.0 + dent + (n - 0.5) * 1.2 + (random.random() - 0.5) * 0.35)
                painted = m * 0.7 + chips(x, y) * 0.5 > 0.52
                c = mixc(metal, paint, 0.55) if painted else metal
                streak_ = vs(x * 3 + si * 90, y * 0.33)
                rust = streak_ * 0.75 + (y / H) ** 2 * 0.45 + (0.2 if (x - x0) < 6 or (x1 - x) < 4 else 0) + (n - 0.5) * 0.3
                if rust > 0.74:
                    c = lerp(RUST, 2.2 + (rust - 0.74) * 9 + (chips(x, y) - 0.5) * 2)
                    if random.random() < 0.05: c = RUST[1]
                elif rust > 0.66:
                    c = mixc(c, RUST[4], (rust - 0.66) * 6)
                if 0.5 < m * 0.7 + chips(x, y) * 0.5 < 0.52 and rust < 0.66: c = mixc(c, (150, 145, 130), 0.3)   # the paint's edge
                P.put(x, y, c)
        for y in range(H):                                             # the overlap at the seam, a row of rivets
            P.put(x0, y, IRON[1]); P.put(x0 + 1, y, IRON[6]); P.put(x0 + 2, y, IRON[4])
            if y % 14 == 5: rivet(P, x0 + 3, y, 0.6)
            if y % 14 == 5 and rnd.random() < 0.5: streak(P, x0 + 4, y + 4, rnd, rnd.randint(10, 40), RUST[5], 0.5)
    for _ in range(40): streak(P, rnd.uniform(0, W), rnd.uniform(0, H * 0.6), rnd, rnd.randint(14, 70), RUST[4], 0.35)
    # old buffed-out graffiti: grey painted-over patches, a faded tag or two
    for _ in range(6):
        bx, by, bw, bh = rnd.uniform(0, W - 80), rnd.uniform(10, H - 60), rnd.uniform(40, 110), rnd.uniform(18, 40)
        for y in range(int(by), int(by + bh)):
            for x in range(int(bx), int(bx + bw)):
                if f(x * 3, y * 3) > 0.25: P.mix(x, y, (70, 72, 70), 0.55)
    for _ in range(5):
        tx, ty, colr = rnd.uniform(20, W - 60), rnd.uniform(20, H - 40), rnd.choice(((150, 60, 50), (60, 90, 140), (170, 150, 60)))
        a = rnd.uniform(0, 6)
        for k in range(rnd.randint(60, 140)):
            a += rnd.uniform(-0.5, 0.5)
            tx += math.cos(a) * 0.8; ty += math.sin(a) * 0.5
            P.mix(tx, ty, colr, 0.35); P.mix(tx + 1, ty, colr, 0.2)
    # weeds all along the bottom, moss up the seams, ivy over the top corners
    fm = fbm(84, W, H, cells=(6, 3), weights=(0.6, 0.4))
    for x in range(0, W, 9):
        weeds(P, x + rnd.uniform(-3, 3), H + 1, rnd, n=rnd.randint(5, 10), hmax=rnd.randint(10, 26), dry=0.25)
    for cx in (40, 150, 300, 420, 500):
        moss(P, cx, H - 2, rnd.randint(16, 30), 8, rnd, fm)
    for sx in seams[1:-1]:
        for k in range(3): moss(P, sx + rnd.uniform(-3, 3), H - rnd.uniform(10, 70), rnd.randint(3, 6), rnd.randint(6, 14), rnd, fm)
    ivy(P, 0, 2, rnd, 150, 0.9, 0.5, 0.6, 0.75, rot=0.25)
    ivy(P, 533, 0, rnd, 170, -0.4, 1, 0.6, 0.75, rot=0.25)
    ivy(P, 0, 296, rnd, 120, 0.3, -1, 0.6, 0.7, rot=0.25)
    vignette(P, 0.7, 0.4)
    P.save('plate')


def stall():
    """the apprentice's market stall: rotting planks, a torn mouldy awning, rusty brackets, a grimy chalk board, weeds;
    534 x 300 matching ui/panels/shopScreens.js buildStall (shelves at 170 / 295 / 420, the board at 668,78 108x176)"""
    W, H = 534, 300
    P = Px(W, H); rnd = random.Random(91); random.seed(91)
    f = fbm(92, W, H)
    grain = fbm(93, W * 4, H, cells=(60, 24, 8), weights=(0.5, 0.3, 0.2))
    for y in range(H):                                     # the dark behind
        for x in range(W): P.put(x, y, lerp(WOOD, 0.6 + (f(x, y) - 0.5) * 0.8 - y / H * 0.4))
    def planks(x0, y0, x1, y1, ph, seed, base=3.0, horiz=True):
        for y in range(y0, y1):
            for x in range(x0, x1):
                k = (y - y0) // ph if horiz else (x - x0) // ph
                g = grain(x * 0.25 + k * 97 + seed, y * 2.2 + k * 13) if horiz else grain(y * 0.25 + k * 97 + seed, x * 2.2)
                n = f(x, y)
                v = base + ((k * 37) % 5 - 2) * 0.15 + (g - 0.5) * 3 + (n - 0.5) * 1.2
                if abs(g - 0.5) < 0.012: v -= 1.3
                if n > 0.66: v -= (n - 0.66) * 7                                     # rot
                c = lerp(WOOD, v + (random.random() - 0.5) * 0.3)
                if (y - y0) % ph == 0 if horiz else (x - x0) % ph == 0: c = WOOD[0]
                P.put(x, y, c)
    planks(12, 22, 328, 236, 11, 0, base=3.7)              # the back wall
    for _ in range(8): mould(P, rnd.uniform(14, 326), rnd.uniform(24, 230), rnd.uniform(4, 10), rnd, (95, 105, 72), (14, 16, 10), 0.45)
    for _ in range(16): streak(P, rnd.uniform(14, 326), rnd.uniform(24, 90), rnd, rnd.randint(20, 90), (20, 24, 14), 0.35)
    for x0 in (7, 326):                                    # the posts
        planks(x0, 14, x0 + 9, 236, 9, 40 + x0, base=2.2, horiz=False)
        for y in range(14, 236): P.mix(x0 + 1, y, (200, 170, 130), 0.08)
    for sy in (85, 147, 210):                              # the shelves, rusty brackets
        for y in range(sy + 6, sy + 13):
            for x in range(16, 326): P.mix(x, y, BLACK, 0.4 * (1 - (y - sy - 6) / 7))
        planks(16, sy, 326, sy + 6, 6, 70 + sy, base=5.6)
        for x in range(16, 326): P.mix(x, sy, (225, 190, 140), 0.35); P.mix(x, sy + 5, BLACK, 0.35)
        for bx in (24, 170, 312):
            for k in range(9):
                for w_ in range(0, max(1, 7 - k)):
                    P.put(bx + w_, sy + 6 + k, lerp(RUST, 2.5 + (f(bx * 3 + w_, k * 3) - 0.5) * 3 + (1 if w_ == 0 else 0)))
            streak(P, bx + 2, sy + 15, rnd, rnd.randint(6, 18), RUST[4], 0.45)
        for _ in range(3):                                 # weeds and moss gone wild on the shelves
            wx = rnd.choice((rnd.uniform(18, 40), rnd.uniform(300, 324), rnd.uniform(18, 324)))
            weeds(P, wx, sy, rnd, n=rnd.randint(3, 6), hmax=rnd.randint(5, 11), dry=0.35)
        moss(P, rnd.uniform(20, 320), sy + 1, rnd.uniform(5, 10), 2, rnd, fbm(94 + sy, W, H, cells=(6, 3), weights=(0.6, 0.4)))
    # the awning: faded stripes, scalloped, torn, stained, a hole, moss along its top
    for x in range(4, 337):
        stripe = ((x - 4) // 21) % 2
        cx = 4 + ((x - 4) // 21) * 21 + 10.5
        for y in range(0, 31):
            if y > 20 and (x - cx) ** 2 + (y - 20) ** 2 > 10.5 ** 2: continue
            if y > 26 and f(x * 4, y * 4) < 0.35: continue             # frayed edge
            n = f(x, y)
            base = (125, 52, 44) if stripe == 0 else (196, 182, 150)
            c = mixc(base, (60, 55, 40), 0.35 + (n - 0.5) * 0.5 + y / 31 * 0.1)
            if n > 0.68: c = mixc(c, (50, 60, 35), 0.4)                   # mould
            if y < 3: c = mixc(c, BLACK, 0.4)
            P.put(x, y, c)
    for (hx_, hy_, hr) in ((96, 14, 4), (250, 9, 3)):                        # holes, the dark showing through
        for y in range(hy_ - hr, hy_ + hr + 1):
            for x in range(hx_ - hr, hx_ + hr + 1):
                if math.hypot(x - hx_, (y - hy_) * 1.3) < hr + (f(x * 6, y * 6) - 0.5) * 2: P.put(x, y, WOOD[0])
    for _ in range(10): streak(P, rnd.uniform(6, 334), 2, rnd, rnd.randint(8, 24), (60, 50, 35), 0.4)
    fm = fbm(97, W, H, cells=(6, 3), weights=(0.6, 0.4))
    for cx in (30, 120, 200, 290):
        moss(P, cx, 1, rnd.uniform(10, 20), 3, rnd, fm)
    ivy(P, 336, 0, rnd, 110, 0.1, 1, 0.55, 0.75, rot=0.3)
    # the chalk board, hung by a string from the post: a warped frame, a smeared board
    BX, BY, BW, BH = 334, 39, 54, 88
    for k in range(30):
        t = k / 29
        P.put(330 + (BX + 10 - 330) * t, 30 + (BY - 30) * t, BONE[4]); P.put(330 + (BX + BW - 10 - 330) * t, 30 + (BY - 30) * t, BONE[4])
    planks(BX, BY, BX + BW, BY + BH, 4, 300, base=3.2, horiz=False)
    for y in range(BY + 4, BY + BH - 4):
        for x in range(BX + 4, BX + BW - 4):
            n = f(x * 2, y * 2)
            c = lerp(ramp('#141a17 #1b2420 #232e29 #2c3833'), 1.4 + (n - 0.5) * 1.6)
            if abs(math.hypot(x - BX - 26, y - BY - 50) - 22) < 4 and n > 0.4: c = mixc(c, (200, 205, 195), 0.08)   # old wiped chalk
            P.put(x, y, c)
    for _ in range(40): P.mix(rnd.uniform(BX + 4, BX + BW - 4), rnd.uniform(BY + 4, BY + BH - 4), (220, 225, 215), 0.25)
    rivet(P, BX + 1, BY + 1, 0.8); rivet(P, BX + BW - 4, BY + 1, 0.8)
    # the counter: a thick rotten plank, a front of boards, weeds at its foot
    planks(0, 233, W, 241, 8, 500, base=5.0)
    for x in range(W): P.mix(x, 233, (215, 180, 135), 0.2); P.mix(x, 241, BLACK, 0.5); P.mix(x, 242, BLACK, 0.3)
    planks(0, 243, W, H, 32, 600, base=3.3, horiz=False)
    for _ in range(5): mould(P, rnd.uniform(0, W), rnd.uniform(246, 296), rnd.uniform(5, 12), rnd, (95, 105, 72), (14, 16, 10), 0.5)
    for (cx_, cy_) in ((60, 236), (420, 237)):                              # cup rings on the counter top
        for k in range(48):
            a = k / 48 * math.pi * 2
            P.mix(cx_ + math.cos(a) * 6, cy_ + math.sin(a) * 2, (25, 15, 8), 0.5)
    for x in range(0, W, 7):
        weeds(P, x + rnd.uniform(-2, 2), H + 1, rnd, n=rnd.randint(3, 8), hmax=rnd.randint(8, 22), dry=0.3)
    for cx in (20, 250, 500):
        moss(P, cx, H - 1, rnd.uniform(14, 26), 6, rnd, fm)
    vignette(P, 0.45, 0.55)
    P.save('stall')


MANILA = ramp('#4e3b22 #67502d #806538 #997b44 #ae8f51 #c1a160 #d0b170 #dcbf80')
WHITE = ramp('#77746a #918d82 #aaa699 #c1bdaf #d4d0c2 #e2ded1 #ebe8dc #f2efe5')


def paper_sheet(P, x0, y0, x1, y1, rmp, seed, base=6.2, amp=1.2, torn=0.0, dog=0):
    """a calm aged sheet over [x0, x1) x [y0, y1) with a slightly ragged edge; dog = a folded corner (px) top-right"""
    f = fbm(seed, P.w, P.h, cells=(40, 16, 6), weights=(0.5, 0.3, 0.2))
    for y in range(y0, y1):
        for x in range(x0, x1):
            e = min(x - x0, x1 - 1 - x, y - y0, y1 - 1 - y)
            if e < 1 and f(x * 6, y * 6) < torn: continue
            if dog and (x1 - 1 - x) + (y - y0) < dog: continue
            v = base + (f(x, y) - 0.5) * amp - max(0, 4 - e) * 0.25 + (random.random() - 0.5) * 0.25
            P.put(x, y, lerp(rmp, v))
    if dog:                                                       # the folded-over corner
        for y in range(y0, y0 + dog):
            for x in range(x1 - dog, x1):
                if (x1 - 1 - x) + (y - y0) < dog and (x - (x1 - dog)) < (y - y0) + 1:
                    P.put(x, y, lerp(rmp, base - 1.6))
    return f


def age(P, x0, y0, x1, y1, seed, strength=1.0, damp=0.3, rnd=None):
    """wear a sheet: blotchy discolouring, damp rising from the bottom with a tide line, grubby edges, thumb smudges"""
    rnd = rnd or random.Random(seed)
    lo = fbm(seed + 1, P.w, P.h, cells=(60, 26, 10), weights=(0.55, 0.3, 0.15))
    dl = fbm(seed + 2, P.w * 4, P.h, cells=(14, 6, 3), weights=(0.5, 0.3, 0.2))
    hgt = y1 - y0
    for y in range(y0, y1):
        for x in range(x0, x1):
            if not P.a(x, y): continue
            e = min(x - x0, x1 - 1 - x, y - y0, y1 - 1 - y)
            g = lo(x, y)
            if g > 0.48: P.mix(x, y, (125, 95, 52), min(0.4, (g - 0.48) * 1.0 * strength))
            if damp:
                level = y1 - hgt * damp * (0.85 + 0.3 * dl(x * 1.6, 3))   # how high the damp got here
                if y > level: P.mix(x, y, (112, 88, 50), 0.14 * strength)
                elif y > level - 1: P.mix(x, y, (95, 68, 36), 0.38 * strength)
            if e < 7: P.mix(x, y, (60, 45, 28), (7 - e) * 0.05 * strength)
    for _ in range(int(5 * strength) + 2):                            # grubby thumbs near the edges
        side = rnd.random()
        ex = x0 + rnd.uniform(4, 14) if side < 0.3 else x1 - rnd.uniform(4, 14) if side < 0.6 else rnd.uniform(x0 + 10, x1 - 10)
        ey = rnd.uniform(y0 + 10, y1 - 10) if side < 0.6 else y1 - rnd.uniform(4, 12)
        for yy in range(-9, 10):
            for xx in range(-7, 8):
                d = math.hypot(xx / 7, yy / 9)
                if d < 1 and P.a(ex + xx, ey + yy) and int(d * 9) % 2 == 0: P.mix(ex + xx, ey + yy, (55, 42, 30), 0.16 * (1 - d) + 0.04)


def shadow(P, x0, y0, x1, y1, a=140, dx=3, dy=4):
    for y in range(y0 + dy, y1 + dy):
        for x in range(x0 + dx, x1 + dx):
            if P.ok(x, y) and P.a(x, y) == 0: P.put(x, y, BLACK, a)


def staple(P, x, y, horiz=True):
    for k in range(6):
        P.put(x + (k if horiz else 0), y + (0 if horiz else k), IRON[6] if k % 2 else IRON[5])
    stains_rust = [(x + (2 if horiz else 0), y + (0 if horiz else 2))]
    for (sx, sy) in stains_rust:
        for yy in range(sy - 3, sy + 8):
            for xx in range(sx - 4, sx + 6):
                d = math.hypot(xx - sx, (yy - sy) * (0.6 if yy > sy else 1))
                if d < 5: P.mix(xx, yy, RUST[4], 0.35 - d * 0.06)


def folder_office():
    """the office journal: a stained manila folder on the corroded wall, the typed index sheet clipped in, a vein crawling
    over its corner; 534 x 300, transparent round it (ui/panels/journalScreens.js buildDossier: FOLDER 30,64 1010x524,
    IDX 50,86 652x488, the fold at x 714)"""
    W, H = 534, 300
    P = Px(W, H); rnd = random.Random(111); random.seed(111)
    FX0, FY0, FX1, FY1 = 15, 32, 520, 294
    shadow(P, FX0, FY0, FX1, FY1, 150, 4, 5)
    tmp = Px(W, H)
    f = paper_sheet(tmp, FX0, FY0, FX1, FY1, MANILA, 112, base=5.2, amp=1.6, torn=0.25)
    for y in range(H):
        for x in range(W):
            if tmp.a(x, y): P.p[x, y] = tmp.p[x, y]
    age(P, FX0, FY0, FX1, FY1, 114, 1.1, 0.25, rnd)
    for y in range(FY0, FY1):                                     # the fold of the folder
        P.mix(357, y, (60, 40, 20), 0.4); P.mix(358, y, (240, 220, 170), 0.18)
    stains_on_paper(P, rnd, f, FX0, FY0, FX1, FY1, MANILA, coffee=(470, 270, 15), tide=(400, 70, 30),
                    mould_at=((22, 285, 7), (512, 40, 5), (300, 290, 4)), fox=90, blot=0.45)
    # the index sheet, stapled in
    IX0, IY0, IX1, IY1 = 25, 43, 351, 287
    shadow(P, IX0, IY0, IX1, IY1, 90, 2, 3)
    g = paper_sheet(P, IX0, IY0, IX1, IY1, WHITE, 113, base=5.7, amp=1.1, torn=0.1)
    age(P, IX0, IY0, IX1, IY1, 115, 0.7, 0.16, rnd)
    stains_on_paper(P, rnd, g, IX0, IY0, IX1, IY1, WHITE, coffee=(330, 262, 12), mould_at=((30, 280, 4),), fox=50, blot=0.3)
    staple(P, IX0 + 10, IY0 + 3); staple(P, IX1 - 18, IY0 + 3)
    for sx in (IX0 + 12, IX1 - 16): streak(P, sx, IY0 + 5, rnd, rnd.randint(18, 40), RUST[4], 0.5)
    # a vein along the folder's top edge, clamped, out from behind it on the right
    tube(P, [(FX1 + 10, FY0 + 40), (FX1 + 2, FY0 + 12), (FX1 - 20, FY0 - 2), (FX1 - 110, FY0), (FX1 - 200, FY0 - 3), (FX1 - 300, FY0 - 1)], 2.8, rnd, clamps=(30, 120, 220))
    for _ in range(14): capillaries(P, rnd.uniform(FX1 - 290, FX1 - 8), FY0 + rnd.uniform(1, 3), rnd, rnd.randint(8, 20), a=math.pi / 2 + rnd.uniform(-0.7, 0.7), t=0.45)
    # a vein crawling up over the folder's bottom-left corner, capillaries seeping into the manila
    tube(P, [(-4, 270), (6, 262), (14, 250), (18, 236), (16, 220), (20, 206)], 2.6, rnd, clamps=(18,))
    for _ in range(10): capillaries(P, rnd.uniform(14, 24), rnd.uniform(206, 262), rnd, rnd.randint(8, 18), a=rnd.uniform(-0.8, 0.8))
    for _ in range(6): capillaries(P, rnd.uniform(360, 518), 292, rnd, rnd.randint(8, 16), a=-math.pi / 2 + rnd.uniform(-0.6, 0.6), t=0.4)
    P.save('folder_office')


def tray_office():
    """the office quest log: a corroded riveted in-tray with a flesh tube clamped along its rim; 534 x 300, transparent
    round it (ui/panels/questScreens.js buildForms: TRAY 26,66 676x504)"""
    W, H = 534, 300
    P = Px(W, H); rnd = random.Random(121); random.seed(121)
    X0, Y0, X1, Y1 = 13, 33, 351, 285
    shadow(P, X0, Y0, X1, Y1, 160, 3, 4)
    f = fbm(122, W, H)
    iron_surface(P, X0, Y0, X1, Y1, 123, paint=0.6, rustiness=0.5, f=f, base=2.6)
    for y in range(Y0 + 5, Y1 - 5):                               # the tray's floor, damp
        for x in range(X0 + 5, X1 - 5):
            P.mix(x, y, (12, 16, 12), 0.45)
    bevel(P, X0, Y0, X1, Y1, 0.35, 0.8, 2)
    bevel(P, X0 + 5, Y0 + 5, X1 - 5, Y1 - 5, 0.0, 0.0)
    for y in range(Y0 + 5, Y0 + 9):
        for x in range(X0 + 5, X1 - 5): P.mix(x, y, BLACK, 0.5 - (y - Y0 - 5) * 0.12)
    for x in range(X0 + 6, X1 - 6, 12):
        rivet(P, x, Y0 + 1, rnd.random() * 0.7); rivet(P, x, Y1 - 4, rnd.random() * 0.7)
        if rnd.random() < 0.4: streak(P, x + 1, Y1 - 1, rnd, rnd.randint(4, 12), RUST[5], 0.6)
    for y in range(Y0 + 14, Y1 - 8, 12):
        rivet(P, X0 + 1, y, rnd.random() * 0.7); rivet(P, X1 - 4, y, rnd.random() * 0.7)
    for _ in range(8): mould(P, rnd.uniform(X0 + 8, X1 - 8), rnd.uniform(Y0 + 8, Y1 - 8), rnd.uniform(3, 7), rnd, (110, 125, 100), (20, 26, 18), 0.45)
    tube(P, [(X1 + 8, Y0 + 60), (X1 + 2, Y0 + 30), (X1 - 20, Y0 - 3), (X1 - 120, Y0 - 1), (X1 - 200, Y0 - 4), (X1 - 260, Y0 - 1)], 3.0, rnd, clamps=(40, 130, 220))
    for _ in range(12): capillaries(P, rnd.uniform(X1 - 250, X1 - 10), Y0 + rnd.uniform(1, 4), rnd, rnd.randint(6, 14), a=math.pi / 2 + rnd.uniform(-0.6, 0.6))
    fm = fbm(124, W, H, cells=(6, 3), weights=(0.6, 0.4))
    for cx in (X0 + 10, X0 + 140, X1 - 20):
        moss(P, cx, Y1 + 1, rnd.uniform(10, 18), 4, rnd, fm)
    for bx in (X0 + 4, X0 + 60, X0 + 200, X1 - 10):
        weeds(P, bx, Y1 + 4, rnd, n=rnd.randint(4, 8), hmax=rnd.randint(8, 14), dry=0.3)
    P.save('tray_office')


def forms_office():
    """three stained forms for the in-tray, 322 x 30 each, punched on the left (questScreens.js buildForms rows)"""
    for k in range(3):
        W, H = 322, 30
        P = Px(W, H); rnd = random.Random(130 + k)
        f = paper_sheet(P, 0, 0, W, H, WHITE, 131 + k, base=5.3, amp=1.2, torn=0.15)
        age(P, 0, 0, W, H, 135 + k, 0.9, 0.0, rnd)
        for y in range(4, H - 2, 5):                               # the punched holes
            P.put(7, y, (40, 40, 36)); P.put(8, y, (60, 58, 52)); P.put(7, y + 1, (70, 66, 60))
        for x in range(12, W - 4):
            if f(x * 3, 9) > 0.4: P.mix(x, 9, (120, 130, 120), 0.25)
        stains_on_paper(P, rnd, f, 0, 0, W, H, WHITE, fox=25, blot=0.3,
                        coffee=(rnd.uniform(200, 300), rnd.uniform(8, 22), 9) if k == 1 else None,
                        mould_at=((W - 6, H - 5, 3),) if k == 2 else ())
        staple(P, 14, 1)
        streak(P, 16, 3, rnd, rnd.randint(8, 20), RUST[4], 0.5)
        P.save(f'form_office_{k}')


def catalogue_office():
    """the office shop: a yellowed mail-order catalogue page, stained, clipped, with its printed rules and grid;
    534 x 300, transparent round it (shopScreens.js buildCatalogue: PG 28,30 678x552, GRID 44,128 215x136)"""
    W, H = 534, 300
    P = Px(W, H); rnd = random.Random(141); random.seed(141)
    X0, Y0, X1, Y1 = 14, 15, 353, 291
    shadow(P, X0, Y0, X1, Y1, 160, 4, 5)
    f = paper_sheet(P, X0, Y0, X1, Y1, PAPER, 142, base=6.5, amp=1.2, torn=0.2, dog=12)
    age(P, X0, Y0, X1, Y1, 143, 1.0, 0.2, rnd)
    for y in range(Y0, Y1):                                        # yellowed into the binding on the left
        for x in range(X0, X0 + 14): P.mix(x, y, (120, 90, 40), 0.22 * (1 - (x - X0) / 14))
    ink = (42, 29, 16)
    for x in range(X0 + 10, X1 - 10):                              # the masthead rules and the foot rule
        if f(x * 4, 50) > 0.18: P.mix(x, Y0 + 35, ink, 0.85); P.mix(x, Y0 + 36, ink, 0.6)
        if f(x * 4, 54) > 0.25: P.mix(x, Y0 + 38, ink, 0.6)
        if f(x * 4, 58) > 0.25: P.mix(x, Y1 - 20, ink, 0.6)
    gx, gy, cw, ch = 22, 64, 107.5, 68
    for i in (1, 2):
        x = round(gx + i * cw)
        for y in range(gy + 3, gy + 3 * ch - 3):
            if y % 3: P.mix(x, y, (60, 40, 20), 0.28)
    for j in (1, 2):
        y = gy + j * ch
        for x in range(gx + 3, round(gx + 3 * cw) - 3):
            if x % 3: P.mix(x, y, (60, 40, 20), 0.28)
    stains_on_paper(P, rnd, f, X0, Y0, X1, Y1, PAPER, coffee=(300, 262, 14), tide=(40, 250, 26),
                    mould_at=((346, 284, 5), (20, 22, 4)), fox=80, blot=0.4)
    # a rusty bulldog clip at the top, rust bled into the paper; veins seeping through from below at the bottom edge
    for y in range(Y0 - 6, Y0 + 6):
        for x in range(170, 194):
            P.put(x, y, lerp(IRON, 4 - (y - Y0 + 6) * 0.18 + (f(x * 5, y * 5) - 0.5) * 2) if f(x * 3, y * 3) < 0.62 else RUST[4])
    for x in range(170, 194): P.put(x, Y0 - 7, OUTL); P.put(x, Y0 + 6, OUTL)
    for yy in range(Y0 + 6, Y0 + 16):
        for xx in range(168, 196): P.mix(xx, yy, RUST[4], 0.3 * (1 - (yy - Y0 - 6) / 10))
    for _ in range(8): capillaries(P, rnd.uniform(40, 340), Y1 - 1, rnd, rnd.randint(8, 18), a=-math.pi / 2 + rnd.uniform(-0.7, 0.7), t=0.4)
    for _ in range(3): root(P, X0 + rnd.uniform(-6, 20), Y1 + 4, rnd, rnd.randint(25, 50), -math.pi / 2 + rnd.uniform(0.1, 0.8), 1.4)
    tube(P, [(X1 + 30, Y1 - 30), (X1 + 6, Y1 - 40), (X1 - 6, Y1 - 60), (X1 - 2, Y1 - 120), (X1 + 8, Y1 - 160)], 2.6, rnd, clamps=(40, 110))
    P.save('catalogue_office')


def nail():
    """a rusty nail head driven through the note, 7 x 7"""
    P = Px(7, 7)
    for y in range(7):
        for x in range(7):
            d = math.hypot(x - 3, y - 3)
            if d < 3.2:
                l = lit(norm(((x - 3) / 3.2, (y - 3) / 3.2, math.sqrt(max(0, 1 - (d / 3.2) ** 2)))))
                P.put(x, y, col(RUST, 1 + l * 6, x, y))
            elif d < 3.8: P.put(x, y, OUTL)
    P.save('nail')


if __name__ == '__main__':
    which = sys.argv[2:] or ['backdrop_office', 'cabinet', 'cabinet_glass', 'card_office', 'clip_office', 'labels_office',
                             'backdrop_apprentice', 'desk_mat', 'card_apprentice', 'nail', 'diary', 'plate', 'stall',
                             'folder_office', 'tray_office', 'forms_office', 'catalogue_office']
    for name in which:
        globals()[name]()
