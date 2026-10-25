"""Scraper 1140 (ScraperScene) -- a faithful pixel-art rebuild of the old AI background (the user's favourite picture).

The sky, the misty skyline, the tower and its cables ARE the original (`scraper1140_ref.png`, 1536x1024): it is a
384x256 picture blown up 4x, so every 4x4 block is sampled back to one logical pixel, the frame is cut to 356x200
(grid x 14..370, y 0..200) and everything is locked to one palette; the two figures baked on the right are painted
out from the haze around them (exemplar inpainting). The foreground is new, drawn at the same logical resolution:
a wet tar roof to walk on (duckboards, puddles mirroring the scene), the parapet and its railing with a sagging chain,
the stair-house on the left (its door = the exit to the Crossroad), the gate and the footbridge into the fog
(= the way into the Scraper). The roof has its own eye level, the old walkway's: horizon at row 150 (canvas 450); the
player's feet (canvas y 534 = row 178) stand at depth 15.
The game shows the picture 3x: 356 * 3 = 1068, cropped to 1067x600.

    python3 scraper_bg.py <outdir> [reuse]   # reuse = take <outdir>/plate_raw.png instead of resampling + inpainting again
    -> plate.png, bridge.png, fg.png (356x200 layers), scraper_356.png (composite), scraper.png (1067x600 =
       assets/images/backgrounds/Scraper1140.png), chars.png + guides.png (overlays), scraper.gpl (palette)
"""
import colorsys, math, os, random, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, 'scraper1140_ref.png')
LW, LH, X0, K = 356, 200, 14, 3              # logical frame, its offset in the 384x256 grid, display scale
VX, HY, FL, EYE = 177.5, 150.0, 100.0, 4.2   # deck camera in logical px (feet of the player: row 178 at z 15)
ZB = 22.0                                     # back edge of the roof (the parapet + railing)
GAP = 2.6                                     # half-width of the railing gap where the footbridge starts


def proj(x, h, z): return (VX + FL * x / z, HY + FL * (EYE - h) / z)
def pixels(im): return [im.getpixel((x, y)) for y in range(im.size[1]) for x in range(im.size[0])]
def lum(c): return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
def mix(a, b, t): return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))
def clamp(v, a=0.0, b=1.0): return a if v < a else b if v > b else v


def h32(*a):
    h = 2166136261
    for v in a:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return h / 4294967296.0


def vnoise(x, y, cell, seed):
    """smooth value noise in [0, 1)"""
    gx, gy = x / cell, y / cell
    ix, iy = math.floor(gx), math.floor(gy); fx, fy = gx - ix, gy - iy
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = h32(ix, iy, seed), h32(ix + 1, iy, seed)
    c, d = h32(ix, iy + 1, seed), h32(ix + 1, iy + 1, seed)
    return (a + (b - a) * fx) + ((c + (d - c) * fx) - (a + (b - a) * fx)) * fy


# ---------------------------------------------------------------- 1. the plate (the original, re-pixelled)

def resample():
    src = Image.open(REF).convert('RGB'); sp = src.load(); W, H = src.size
    im = Image.new('RGB', (LW, LH)); p = im.load()
    for j in range(LH):
        for i in range(LW):
            g = i + X0; r = gg = b = 0
            for dy in (1, 2):                 # the 2x2 centre of the block (x blocks start at 4g+1, y at 4j)
                for dx in (2, 3):
                    c = sp[min(W - 1, 4 * g + dx), min(H - 1, 4 * j + dy)]
                    r += c[0]; gg += c[1]; b += c[2]
            p[i, j] = (r // 4, gg // 4, b // 4)
    return im


def paint_out_figures(im):
    """the two people on the old walkway (logical x 278..342) -> the haze and towers behind them"""
    p = im.load(); W, H = im.size
    box, seeds = (276, 138, 342, LH), [(294, 165), (331, 168), (295, 190), (331, 190)]
    M, st = set(), list(seeds)
    while st:
        x, y = st.pop()
        if (x, y) in M or not (box[0] <= x < box[2] and box[1] <= y < box[3]) or lum(p[x, y]) > 52: continue
        M.add((x, y)); st += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    M |= {(x + dx, y + dy) for x, y in M for dx in (-1, 0, 1) for dy in (-1, 0, 1)
          if box[0] <= x + dx < box[2] and box[1] <= y + dy < box[3]}
    FILL = 178                                  # below this the deck covers everything
    known = [[(x, y) not in M for x in range(W)] for y in range(H)]
    R = 2
    cands = [(x, y) for y in range(116, 176) for x in range(230, 346, 1 + (y & 1))
             if R <= x < W - R and y + R < H and all(known[y + dy][x + dx] for dy in range(-R, R + 1) for dx in range(-R, R + 1))]
    rnd = random.Random(7)
    todo = {q for q in M if q[1] < FILL}
    for q in M:
        if q[1] >= FILL: p[q] = (24, 28, 30)
    while todo:
        x, y = max(todo, key=lambda q: (sum(known[q[1] + dy][q[0] + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                                            if 0 <= q[1] + dy < H and 0 <= q[0] + dx < W), -q[1]))
        nb = [(dx, dy, p[x + dx, y + dy]) for dy in range(-R, R + 1) for dx in range(-R, R + 1)
              if 0 <= x + dx < W and 0 <= y + dy < H and known[y + dy][x + dx]]
        best = []; cut = 1 << 60
        for cx, cy in cands:
            s = 0
            for dx, dy, a in nb:
                b = p[cx + dx, cy + dy]
                s += (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2
                if s > cut: break
            else:
                best.append((s, cx, cy))
                if len(best) > 24:
                    best.sort(); best = best[:6]; cut = best[0][0] * 1.15 + 1
        best.sort(); lim = best[0][0] * 1.15 + 1
        _, cx, cy = rnd.choice([b for b in best[:6] if b[0] <= lim])
        p[x, y] = p[cx, cy]; known[y][x] = True; todo.discard((x, y))
    return im


# ---------------------------------------------------------------- 2. the palette

def build_palette(plate):
    greens, warm, cream = [], [], []
    for c in pixels(plate):
        h, s, v = colorsys.rgb_to_hsv(*(t / 255 for t in c))
        if v > 0.58 and s < 0.32: cream.append(c)
        elif s > 0.42 and v > 0.22 and 0.02 < h < 0.17: warm.append(c)
        else: greens.append(c)

    def kq(px, n):
        strip = Image.new('RGB', (len(px), 1)); strip.putdata(px)
        q = strip.quantize(colors=n, method=Image.Quantize.MAXCOVERAGE, kmeans=8)
        pal = q.getpalette()[:3 * n]
        used = sorted(set(pixels(q)))
        return [tuple(pal[3 * i:3 * i + 3]) for i in used]
    pal = kq(greens, 40) + kq(warm, 8) + kq(cream, 4)
    # the foreground's own needs: a deepest ink and warmer lamp light (the plate's window has the rest)
    pal += [(7, 8, 9), (255, 214, 140), (232, 160, 72)]
    out = []
    for c in pal:
        if c not in out: out.append(c)
    return sorted(out, key=lambda c: (lum(c) > 0 and colorsys.rgb_to_hsv(*(t / 255 for t in c))[1] > 0.4, lum(c)))


class Quant:
    def __init__(s, pal): s.pal = pal; s.cache = {}

    def __call__(s, c):
        c = c[:3]
        r = s.cache.get(c)
        if r is None:
            def d(q):
                rm = (c[0] + q[0]) / 2
                return (2 + rm / 256) * (c[0] - q[0]) ** 2 + 4 * (c[1] - q[1]) ** 2 + (2 + (255 - rm) / 256) * (c[2] - q[2]) ** 2
            r = s.cache[c] = min(s.pal, key=d)
        return r

    def image(s, im):
        out = im.copy(); p = out.load()
        for y in range(im.size[1]):
            for x in range(im.size[0]):
                c = p[x, y]
                if len(c) == 4:
                    if c[3]: p[x, y] = s(c) + (255,)
                else: p[x, y] = s(c)
        return out


# ---------------------------------------------------------------- 3. the foreground

class Layer:
    def __init__(s):
        s.im = Image.new('RGBA', (LW, LH), (0, 0, 0, 0)); s.p = s.im.load()

    def put(s, x, y, c):
        x, y = int(math.floor(x)), int(math.floor(y))
        if 0 <= x < LW and 0 <= y < LH: s.p[x, y] = tuple(c[:3]) + (255,)

    def line(s, a, b, c, dots=None):
        (x0, y0), (x1, y1) = a, b
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n + 1):
            t = i / max(1, n)
            if dots and (i % dots[0]) >= dots[1]: continue
            s.put(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, c)

    def vline(s, x, y0, y1, c):
        for y in range(int(math.floor(y0)), int(math.floor(y1)) + 1): s.put(x, y, c)

    def hline(s, x0, x1, y, c):
        for x in range(int(math.floor(x0)), int(math.floor(x1)) + 1): s.put(x, y, c)


def catenary(L, a, b, sag, c, step=0.25):
    """a sagging cable between two screen points"""
    (x0, y0), (x1, y1) = a, b
    n = int(max(abs(x1 - x0), abs(y1 - y0)) / step) + 1
    for i in range(n + 1):
        t = i / n
        L.put(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + sag * 4 * t * (1 - t), c)


class Inks:
    """the foreground ramp, taken from the plate's own darks (the original foreground is near-black, sky-rimmed)"""
    def __init__(s, pal):
        g = [c for c in pal if colorsys.rgb_to_hsv(*(t / 255 for t in c))[1] < 0.42 and lum(c) < 150]
        def near(t): return min(g, key=lambda c: sum((c[i] - t[i]) ** 2 for i in range(3)))
        s.k0 = near((7, 8, 9)); s.k1 = near((15, 17, 19)); s.k2 = near((23, 28, 29)); s.k3 = near((33, 42, 42))
        s.k4 = near((47, 60, 57)); s.k5 = near((64, 82, 76)); s.k6 = near((84, 104, 92))
        s.ramp = sorted({s.k0, s.k1, s.k2, s.k3, s.k4, s.k5, s.k6}, key=lum)
        s.w0, s.w1, s.w2 = near((60, 40, 22)), (232, 160, 72), (255, 214, 140)

    def tone(s, v, x=0, y=0, seed=0):
        """v in 0..1 over the ramp; clustered noise instead of a dither pattern (the plate's own grain)"""
        v += (vnoise(x, y, 1.6, 77 + seed) - 0.5) * 0.07 + (h32(x, y, seed) - 0.5) * 0.015
        return s.ramp[int(round(clamp(v) * (len(s.ramp) - 1)))]


# units: the player is 6.4 tall (1.8 m), so 1 unit ~ 0.28 m; the eye (4.2) sits at the player's chest, as in the old picture
PATH = (13.7, 16.7)              # the duckboards across the roof (the player's feet: z 15)
ZF, XR, ZH = 17.0, -22.5, 20.6   # the stair-house: front face depth, its right edge, its back
DOOR = (-29.0, -25.8, 7.1)       # its door (x0, x1, height): 0.9 x 2 m
LAMP = (-27.4, 7.6, 16.8)        # the caged lamp over the door
def house_h(z): return 10.2 - (z - ZF) * 0.6    # the roof slopes down to the back, over the stairs


def reflected(x, y, z, far, wall, blur=0):
    """what a wet floor point at (x, y), depth z mirrors: the mirrored ray climbs EYE/z per unit of depth; where it
    crosses the parapet plane it sees the parapet or the railing (layer `wall`), above them the far scene; a rough
    surface (blur > 0) smears the far image (puddles stay sharp)"""
    h = (ZB - z) * EYE / z
    if h < 3.5:
        yw = int(HY + FL * (EYE - h) / ZB)
        if 0 <= yw < LH:
            c = wall.p[x, yw]
            if c[3]: return c[:3]
    ry = int(2 * HY - y)
    if not blur: return far[x, ry] if 0 <= ry < LH else far[x, 0]
    acc = [0, 0, 0]; n = 0
    for yy in range(ry - blur, ry + blur + 1):
        for xx in (x - 1, x, x + 1):
            c = far[min(LW - 1, max(0, xx)), min(LH - 1, max(0, yy))]
            acc[0] += c[0]; acc[1] += c[1]; acc[2] += c[2]; n += 1
    return (acc[0] // n, acc[1] // n, acc[2] // n)


def roof(L, far, ink):
    """a wet tar roof with a duckboard walk (branches to the footbridge and to the door); puddles mirror the scene"""
    puddles = [(0.6, 11.4, 2.6, 0.75), (11.5, 10.8, 2.8, 0.8), (-9.5, 13.0, 2.0, 0.55), (24.0, 12.2, 2.4, 0.6),
               (9.5, 17.6, 2.4, 0.55), (27.5, 17.2, 3.4, 0.8), (-12.0, 18.6, 1.8, 0.5)]
    seams = [9.4, 11.95, 18.3, 20.65]
    patches = [(-21.0, -15.5, 9.2, 10.6), (4.0, 8.5, 20.9, 21.6), (22.0, 28.0, 11.6, 12.9)]
    for y in range(int(HY) + 1, LH):
        z = FL * EYE / (y + 0.5 - HY)
        if z > ZB: continue
        zt, zb = FL * EYE / (y - HY) if y > HY else 1e9, FL * EYE / (y + 1 - HY)
        for x in range(LW):
            if L.p[x, y][3]: continue                               # the parapet already owns the pixel
            wx = (x + 0.5 - VX) * z / FL
            if wx < XR and z > ZF: continue                         # under the stair-house
            path = PATH[0] <= z <= PATH[1]
            branch = (abs(wx) < 2.25 and z > PATH[1]) or (DOOR[0] - 0.4 <= wx <= DOOR[1] + 0.4 and PATH[1] < z < ZF)
            if path or branch:
                if path:
                    k = math.floor(wx / 1.0); gap = math.floor((x + 1.5 - VX) * z / FL / 1.0) != k
                    v = 0.50 + (h32(k, 11) - 0.5) * 0.08 + (vnoise(k, z * 4, 1, 12) - 0.5) * 0.06
                    if abs(z - PATH[0]) < 0.12 or abs(z - PATH[1]) < 0.16: v = 0.36   # the battens under the ends
                    if gap: v = 0.20
                    v += 0.06 * math.exp(-((z - 15.2) / 1.0) ** 2)                   # worn where everyone walks
                    if h32(k, 13) > 0.94 and z < 15.0: v = 0.16                       # a missing board
                else:
                    v = 0.44 + (vnoise(wx * 2, z * 2, 1, 14) - 0.5) * 0.10
                    if (zt - zb) < 0.45 and math.floor(z / 0.55) != math.floor(zb / 0.55): v = 0.26
                    if abs(abs(wx) - 2.25) < 0.1 * z / 15: v = 0.22
                refl_k = 0.05 + 0.10 * clamp((z - 13) / 8)
            else:
                v = 0.24 + (vnoise(wx * 0.45, z * 0.9, 1, 5) - 0.5) * 0.12 + (vnoise(wx * 3, z * 5, 1, 6) - 0.5) * 0.03
                if any(zb <= s_ <= zt for s_ in seams): v -= 0.08
                elif any(zb <= s_ + 0.12 * z / 12 <= zt for s_ in seams): v += 0.04
                for (a, b, c_, d) in patches:
                    if a <= wx <= b and c_ <= z <= d:
                        v -= 0.04
                        if min(wx - a, b - wx) < 0.12 * z / 12 or zb <= c_ <= zt or zb <= d <= zt: v -= 0.05
                if h32(x, y, 3) > 0.988: v += 0.10                                    # grit
                refl_k = 0.10 + 0.42 * clamp((z - 9.0) / 9.0) ** 1.3
                for (px_, pz, rx, rz) in puddles:
                    d = ((wx - px_) / rx) ** 2 + ((z - pz) / rz) ** 2 + (vnoise(wx * 2.5, z * 3, 1, 9) - 0.5) * 0.6
                    if d < 1.0: refl_k = 0.82 if d < 0.8 else 0.52
            if wx < XR + 1.2 and z > ZF - 1.0:                       # contact shadows: the house, the parapet
                v -= 0.10 * clamp(1 - max(0, wx - XR) / 1.2) * clamp(1 - max(0, ZF - z))
            v -= 0.08 * clamp(1 - (ZB - z) / 0.8)
            c = ink.tone(v, x, y, 2)
            rc = reflected(x, y + int((vnoise(x * 0.4, y * 2, 1, 21) - 0.5) * 2), z, far, L, 0 if refl_k >= 0.5 else 2)
            c = mix(c, mix(rc, (0, 0, 0), 0.18), refl_k)
            dl = math.hypot(wx - LAMP[0], (z - LAMP[2]) * 1.6)
            if dl < 5.0: c = mix(c, ink.w1, 0.34 * (1 - dl / 5.0) ** 2)
            L.put(x, y, c)


def parapet(L, ink):
    """the low wall along the back edge (a lit coping, a stained face) with the railing on it"""
    yc0, yc1, yf = proj(0, 1.05, ZB)[1], proj(0, 0.88, ZB)[1], proj(0, 0, ZB)[1]
    for x in range(LW):
        wx = (x + 0.5 - VX) * ZB / FL
        if abs(wx) < GAP: continue
        end = abs(abs(wx) - GAP) < 0.25
        L.put(x, int(yc0), ink.k5 if h32(x, 1) > 0.15 else ink.k4)
        L.put(x, int(yc1), ink.k3)
        for y in range(int(yc1) + 1, int(yf) + 1):
            v = 0.27 + (vnoise(x * 0.7, y * 0.3, 1, 31) - 0.5) * 0.14 - (0.10 if y == int(yc1) + 1 else 0)
            v -= 0.08 * (vnoise(x * 1.5, 1, 1, 33) > 0.7)
            L.put(x, y, ink.k4 if end else ink.tone(v, x, y, 3))
    # railing: posts on the coping, a pipe top rail, a chain sagging between the posts (as on the old walkway)
    ytop, ybot = proj(0, 3.4, ZB)[1], yc0
    posts = []
    for side in (-1, 1):
        x = GAP + 0.2
        while x < 42:
            posts.append(side * x); x += 2.9 + (h32(x * 10, side) - 0.5) * 0.4
    posts.sort()
    for wx in posts:
        px = proj(wx, 0, ZB)[0]
        lean = 1 if h32(wx * 10, 7) > 0.88 else 0                         # the odd bent post
        for y in range(int(ytop), int(ybot)):
            L.put(px + (lean if y < ytop + 4 else 0), y, ink.k1)
        L.put(px + lean, int(ytop) - 1, ink.k3)
    for side in (-1, 1):
        x0 = proj(side * (GAP + 0.2), 0, ZB)[0]; x1 = 0 if side < 0 else LW
        lo, hi = min(x0, x1), max(x0, x1)
        for x in range(int(lo), int(hi) + 1):
            L.put(x, int(ytop), ink.k1)
            L.put(x, int(ytop) - 1, ink.k4 if h32(x, 5) > 0.35 else ink.k3)
    for a, b in zip(posts, posts[1:]):
        if a < 0 < b: continue
        pa, pb = proj(a, 2.35, ZB), proj(b, 2.35, ZB)
        n = int(pb[0] - pa[0]) * 3
        for i in range(n + 1):
            t = i / n
            x = pa[0] + (pb[0] - pa[0]) * t; y = pa[1] + 2.4 * 4 * t * (1 - t)
            L.put(x, y, ink.k1 if (int(x) % 3) else ink.k3)


def footbridge(plate, ink):
    """a suspension footbridge from the gap in the parapet into the fog toward the tower; lamps along it (no number
    plate on the gate: the tower's own sign says 1140 already)"""
    pp = plate.load()
    ZE, HW, HR = 420.0, 2.25, 3.6
    B = Layer()

    def put(x, y, c, z, emit=False):
        x, y = int(math.floor(x)), int(math.floor(y))
        if not (0 <= x < LW and 0 <= y < LH): return
        a = math.exp(-(z - ZB) / (150.0 if emit else 60.0))
        if a < 0.06: return
        B.p[x, y] = mix(pp[x, y], c, a) + (255,)
    for y in range(int(HY) + 1, int(proj(0, 0, ZB)[1]) + 1):             # the deck (worn planks, a lighter middle)
        z = FL * EYE / (y + 0.5 - HY)
        if z < ZB or z > ZE: continue
        x0, x1 = proj(-HW, 0, z)[0], proj(HW, 0, z)[0]
        for x in range(int(math.floor(x0)), int(math.floor(x1)) + 1):
            u = abs((x + 0.5 - VX) * z / FL) / HW
            put(x, y, ink.k3 if u < 0.55 and h32(x, y, 15) > 0.25 else ink.k2, z)
    for side in (-1, 1):                                                   # posts, handrail, lower rope
        z = ZB + 2.2
        while z < ZE:
            (px, pyb), (_, pyt) = proj(side * HW, 0, z), proj(side * HW, HR, z)
            for y in range(int(math.floor(pyt)), int(math.floor(pyb)) + 1): put(px, y, ink.k1, z)
            z += 2.5 + (z - ZB) * 0.02
        z = ZB
        while z < ZE:
            dz = 0.02 * z
            put(*proj(side * HW, HR, z), ink.k4, z)
            put(*proj(side * HW, HR * 0.45, z), ink.k1, z)
            z += dz
    hangers = []
    for side in (-1, 1):                                                   # main cables + hangers
        z = ZB + 0.3
        while z < ZE:
            t = (z - ZB) / (ZE - ZB)
            h = max(9.3 + (40.0 - 9.3) * t - 17.0 * 4 * t * (1 - t) ** 1.4, HR + 0.6)
            put(*proj(side * (HW + 0.15), h, z), ink.k1, z)
            if z < 110 and abs((z - ZB) % 3.0) < 0.01 * z: hangers.append((side, z, h))
            z += 0.01 * z
    for side, z, h in hangers:
        (px, y0), (_, y1) = proj(side * HW, HR, z), proj(side * (HW + 0.15), h, z)
        for y in range(int(math.floor(y1)), int(math.floor(y0)) + 1): put(px, y, ink.k2, z)
    z = 30.0                                                               # lamps hung from the hangers, into the fog
    while z < 260:
        for side in (-1, 1):
            px, py = proj(side * HW, 6.0, z)
            put(px, py, ink.w2 if z < 60 else ink.w1, z, emit=True)
            if z < 45: put(px, py - 1, ink.k1, z)
        z *= 1.32
    zp = ZB + 0.3                                                          # the portal at the bridge head
    yt, yg = proj(0, 9.5, zp)[1], proj(0, 0, zp)[1]
    for side in (-1, 1):
        px = int(proj(side * (HW + 0.35), 0, zp)[0])
        for y in range(int(yt) - 1, int(yg) + 1):
            B.p[px, y] = ink.k1 + (255,)
            B.p[px + side, y] = (ink.k4 if side > 0 else ink.k2) + (255,)
            if (y - int(yt)) % 4 == 2: B.p[px - side, y] = ink.k1 + (255,)    # rivet bands
        B.p[px, int(yt) - 2] = ink.k3 + (255,)                                 # finials
        for i in range(6):                                                     # knee braces
            B.p[int(px - side * (1 + i * 0.7)), int(yt + 2 + i * 0.7)] = ink.k1 + (255,)
    xa, xb = int(proj(-(HW + 1.0), 0, zp)[0]), int(proj(HW + 1.0, 0, zp)[0])
    for x in range(xa, xb + 1):
        B.p[x, int(yt)] = ink.k4 + (255,)
        B.p[x, int(yt) + 1] = (ink.k1 if x % 2 else ink.k2) + (255,)
    return B


def stair_house(L, ink):
    """the stair-head on the left (its door = the way down to the Crossroad), roof clutter and the antenna mast"""
    D0, D1, DH = DOOR
    HT = house_h(ZF)
    def face_px(wx, h, side):
        v = (0.25 if not side else 0.33) + (vnoise(wx * 2, h * 2, 1, 41 + side) - 0.5) * 0.06
        s_ = (wx + 40) % 1.6
        if s_ < 0.16: v -= 0.09
        elif abs(s_ - 0.8) < 0.12 and (int(h * 3) % 2 == 0): v += 0.05                    # rivets
        if abs(h - 4.0) < 0.13 or abs(h - 8.0) < 0.13: v += 0.09                          # the bands
        v -= 0.12 * clamp((0.7 - h) / 0.7)                                                 # wet foot
        v -= 0.10 * (vnoise(wx * 5, h * 0.5, 1, 43 + side) > 0.70) * clamp((HT - 0.6 - h) / 3)  # rain streaks
        v += 0.06 * (vnoise(wx * 3, h * 3, 1, 45 + side) > 0.82) * clamp((h - 2) / 3)      # sky-lit dents
        return v
    for y in range(LH):                                   # front face
        for x in range(LW):
            wx = (x + 0.5 - VX) * ZF / FL; h = EYE - (y + 0.5 - HY) * ZF / FL
            if wx > XR or h < 0 or h > HT + 0.25: continue
            if h > HT - 0.3: c = ink.k4 if h > HT + 0.1 else ink.k1        # the roof's front edge
            else: c = ink.tone(face_px(wx, h, 0), x, y, 4)
            if D0 <= wx <= D1 and h <= DH:                              # the door: frame, steel leaf, a grille
                if wx < D0 + 0.22 or wx > D1 - 0.22 or h > DH - 0.25: c = ink.k0
                else:
                    c = ink.tone(0.20 + 0.05 * (abs(((wx - D0) % 1.2) - 0.6) < 0.1), x, y, 5)
                    if 4.6 < h < 5.7 and D0 + 0.7 < wx < D1 - 0.7:
                        c = ink.w0 if (int((wx - D0) * 6) % 2) else ink.k0
                    if abs(wx - (D1 - 0.5)) < 0.12 and abs(h - 3.3) < 0.15: c = ink.k5
            elif abs(wx - (XR - 0.45)) < 0.14 and h < HT - 0.3:          # drainpipe at the corner
                c = ink.k1 if (int(h * 2.5) % 5) else ink.k3
            elif -25.0 <= wx <= -23.7 and 3.6 <= h <= 5.0:              # a fuse box, its conduit up
                c = ink.k3 if h > 4.85 else ink.k2
            elif abs(wx + 24.35) < 0.1 and h > 5.0: c = ink.k1
            dl = math.hypot(wx - LAMP[0], (h - LAMP[1]) * 1.2)
            if dl < 3.4 and not (D0 <= wx <= D1 and h <= DH): c = mix(c, ink.w1, 0.42 * (1 - dl / 3.4) ** 2)
            L.put(x, y, c)
    for y in range(LH):                                   # side face (x = XR): faces the open sky over the gap
        for x in range(LW):
            if x + 0.5 - VX >= 0: continue
            z = FL * XR / (x + 0.5 - VX)
            if not (ZF <= z <= ZH): continue
            h = EYE - (y + 0.5 - HY) * z / FL
            top = house_h(z)
            if h < 0 or h > top + 0.25: continue
            if h > top - 0.3: c = ink.k4 if h > top + 0.1 else ink.k1
            else:
                c = ink.tone(face_px(z * 1.3, h, 1), x, y, 6)
                if abs((z - ZF) % 1.2) < 0.08 * z / 17: c = ink.tone(0.22, x, y, 6)
                if 19.9 < z < 20.4 and 7.6 < h < 8.7:                 # a small barred window up the stairs
                    c = ink.k0 if (int(z * 9) % 2 == 0 or h > 8.55) else ink.k1
                if 18.9 < z < 19.8 and h < top:                       # the iron ladder up to the roof
                    if abs(z - 19.0) < 0.09 * z / 17 or abs(z - 19.7) < 0.09 * z / 17: c = ink.k1
                    elif (h * 3.2) % 1 < 0.28: c = ink.k1
            L.put(x, y, c)
    xc = proj(XR, 0, ZF)[0]                               # the near corner catches the sky
    L.vline(xc, proj(XR, HT, ZF)[1] + 1, proj(XR, 0, ZF)[1], ink.k4)
    a, b = proj(D0 - 0.6, 8.1, 16.3), proj(D1 + 0.6, 8.1, 16.3)           # the awning, seen from under
    c_, d_ = proj(D0 - 0.6, 8.1, ZF), proj(D1 + 0.6, 7.9, 16.3)
    for y in range(int(c_[1]), int(d_[1]) + 1): L.hline(a[0], b[0], y, ink.k1)
    L.hline(a[0], b[0], int(d_[1]) + 1, ink.k3)
    lx, ly = proj(LAMP[0], LAMP[1] - 0.25, LAMP[2])                       # the caged lamp
    L.put(lx, ly, ink.w2); L.put(lx + 1, ly, ink.w1); L.put(lx, ly + 1, ink.w1); L.put(lx + 1, ly + 1, ink.w0)
    L.put(lx - 1, ly, ink.k1); L.put(lx + 2, ly, ink.k1); L.put(lx, ly - 1, ink.k1); L.put(lx + 1, ly - 1, ink.k1)
    def box(x0, x1, h0, h1, z, v, louvres=False):
        a, b = proj(x0, h1, z), proj(x1, h0, z)
        for y in range(int(a[1]), int(b[1]) + 1):
            for x in range(int(a[0]), int(b[0]) + 1):
                c = ink.tone(v, x, y, 7)
                if louvres and (y - int(a[1])) % 2 == 1 and a[0] < x < b[0]: c = ink.k1
                L.put(x, y, c)
        L.hline(a[0], b[0], int(a[1]) - 1, ink.k4)
        L.vline(b[0], a[1], b[1], ink.k3)
    box(-30.6, -26.6, 9.8, 12.2, 17.7, 0.22, louvres=True)              # a fan housing
    box(-26.0, -24.6, 9.8, 10.9, 17.9, 0.26)                             # a junction box
    p0, p1 = proj(-23.6, 9.6, 17.6), proj(-23.6, 12.6, 17.6)            # a pipe up, an elbow, down the corner
    for dx in (0, 1): L.vline(p0[0] + dx, p1[1], p0[1], ink.k1 if dx else ink.k3)
    q = proj(-22.4, 12.6, 17.6)
    L.hline(p1[0], q[0] + 1, p1[1], ink.k3); L.hline(p1[0], q[0] + 1, p1[1] + 1, ink.k1)
    L.vline(q[0] + 1, q[1], proj(-22.4, 9.8, 17.6)[1], ink.k1)
    p0, p1 = proj(-31.4, 9.8, 18.0), proj(-31.4, 14.4, 18.0)            # a flue with a cowl
    L.vline(p0[0], p1[1], p0[1], ink.k1); L.vline(p0[0] + 1, p1[1], p0[1], ink.k2)
    L.hline(p0[0] - 1, p0[0] + 2, p1[1] - 1, ink.k1); L.hline(p0[0] - 1, p0[0] + 2, p1[1] - 2, ink.k3)
    yr0, yr1 = proj(0, HT + 3.0, 17.3)[1], proj(0, HT, 17.3)[1]          # a short railing on the roof edge
    xa, xb = proj(-41, 0, 17.3)[0], proj(XR + 0.3, 0, 17.3)[0]
    L.hline(xa, xb, int(yr0), ink.k1)
    x = xb
    while x >= xa:
        L.vline(x, yr0, yr1, ink.k1); x -= 6
    mx, mz = -25.6, 18.6                                                  # the antenna mast
    top = proj(mx, 29.0, mz); base = proj(mx, 9.6, mz)
    L.vline(top[0], top[1], base[1], ink.k1); L.vline(top[0] + 1, top[1] + 8, base[1], ink.k2)
    arms = []
    for hh, w in ((28.0, 1.0), (25.4, 1.6), (22.6, 2.2), (19.2, 1.3)):
        a, b = proj(mx - w, hh, mz), proj(mx + w, hh, mz)
        L.hline(a[0], b[0], int(a[1]), ink.k1)
        L.put(a[0], a[1] - 1, ink.k3); L.put(b[0], b[1] - 1, ink.k3)
        arms.append((a, b))
    for gx in (-31.5, -22.8):
        L.line(proj(mx, 20.0, mz), proj(gx, 9.8, 17.6), ink.k2, dots=(3, 2))
    return {'arms': arms}


def ray(x, y): return ((x + 0.5 - VX) / FL, -(y + 0.5 - HY) / FL)       # the pixel's ray: (dx, dh) per unit of depth


def cylinder(L, far, ink, cx, cz, r, h0, h1, seed, ribs=0.0, lid=True):
    """an upright cylinder on the roof (drum, vent neck): ray-traced, lit from the open sky on the right, a wet lid"""
    xl, xr_ = int(proj(cx - r, 0, cz)[0]) - 1, int(proj(cx + r, 0, cz)[0]) + 1
    yt, yb = int(proj(0, h1, cz - r)[1]) - 2, int(proj(0, h0, cz - r)[1]) + 1
    for y in range(max(0, yt), min(LH, yb + 1)):
        for x in range(max(0, xl), min(LW, xr_ + 1)):
            dx, dh = ray(x, y)
            A, B, C = dx * dx + 1, -2 * (cx * dx + cz), cx * cx + cz * cz - r * r
            disc = B * B - 4 * A * C
            hit = None
            if disc >= 0:
                t = (-B - math.sqrt(disc)) / (2 * A); h = EYE + t * dh
                if h0 <= h <= h1: hit = ('body', t, h)
            if hit is None and lid and dh < 0:
                t = (h1 - EYE) / dh
                if (t * dx - cx) ** 2 + (t - cz) ** 2 <= r * r: hit = ('lid', t, h1)
            if hit is None: continue
            kind, t, h = hit
            if kind == 'body':
                # pixel-art cylinder shading across the silhouette: dark core, a sky-lit band, a reflected rim
                u = (x + 0.5 - (xl + 1)) / max(1.0, (xr_ - 1) - (xl + 1))
                v = 0.14 + 0.18 * clamp(u / 0.6) + (0.20 if 0.62 < u < 0.86 else 0) - (0.12 if u > 0.93 else 0)
                if h > h1 - 0.16: v = 0.60
                if ribs and ((h - h0) % ribs) < 0.09 * t / 12 + 0.04: v += 0.12
                v -= 0.08 * clamp((0.5 - h) / 0.5)
                c = ink.tone(v, x, y, seed)
            else:
                d = math.hypot(t * dx - cx, t - cz) / r
                c = ink.tone(0.52 if d > 0.78 else 0.30, x, y, seed + 1)
                ry = int(2 * HY - y)
                c = mix(c, far[x, ry] if 0 <= ry < LH else far[x, 0], 0.30)
                if abs(t * dx - (cx + r * 0.4)) < 0.12 and abs(t - (cz - r * 0.2)) < 0.12: c = ink.k0   # a bung
            L.put(x, y, c)


def dome(L, ink, cx, ch, cz, r, seed):
    """the turbine head of a roof ventilator: a ribbed half-sphere"""
    for y in range(int(proj(0, ch + r, cz)[1]) - 1, int(proj(0, ch, cz - r)[1]) + 2):
        for x in range(int(proj(cx - r, 0, cz)[0]) - 1, int(proj(cx + r, 0, cz)[0]) + 2):
            dx, dh = ray(x, y)
            # |(t dx - cx, EYE + t dh - ch, t - cz)| = r
            A = dx * dx + dh * dh + 1
            B = 2 * (dx * (-cx) + dh * (EYE - ch) - cz)
            C = cx * cx + (EYE - ch) ** 2 + cz * cz - r * r
            disc = B * B - 4 * A * C
            if disc < 0: continue
            t = (-B - math.sqrt(disc)) / (2 * A)
            px, ph, pz = t * dx - cx, EYE + t * dh - ch, t - cz
            if ph < 0: continue
            nx, nh = px / r, ph / r
            u = (x + 0.5 - proj(cx - r, 0, cz)[0]) / max(1.0, proj(cx + r, 0, cz)[0] - proj(cx - r, 0, cz)[0])
            v = 0.16 + 0.22 * clamp(nh) + 0.16 * clamp(u / 0.6) + (0.14 if 0.62 < u < 0.86 else 0)
            if (math.atan2(pz, px) * 10 / math.pi) % 1 < 0.4: v -= 0.12           # the vanes
            L.put(x, y, ink.tone(v, x, y, seed))


def roof_props(L, far, ink):
    """a turbine vent, two drums and a skylight on the roof; a pipe run in sheet-metal cladding across the near left"""
    cylinder(L, far, ink, 15.8, 19.0, 0.5, 0, 1.0, 8, lid=False)          # the vent: neck, throat, turbine head
    cylinder(L, far, ink, 15.8, 19.0, 1.0, 1.0, 1.9, 8, ribs=0.3, lid=False)
    dome(L, ink, 15.8, 1.9, 19.0, 1.05, 8)
    cylinder(L, far, ink, 27.6, 20.9, 1.05, 0, 3.2, 11, ribs=1.05)        # two oil drums by the parapet
    cylinder(L, far, ink, 24.9, 20.2, 1.05, 0, 3.2, 10, ribs=1.05)
    x0, x1, z0, z1, hh = -17.0, -11.6, 19.0, 21.2, 1.4                    # a skylight: kerb + glass mirroring the sky
    for y in range(int(HY) + 1, LH):
        for x in range(LW):
            wx = (x + 0.5 - VX) * z0 / FL; h = EYE - (y + 0.5 - HY) * z0 / FL
            if x0 <= wx <= x1 and 0 <= h <= hh:
                L.put(x, y, ink.k4 if h > hh - 0.12 else ink.tone(0.22, x, y, 9)); continue
            z = FL * (EYE - hh) / (y + 0.5 - HY)
            wx = (x + 0.5 - VX) * z / FL
            if x0 <= wx <= x1 and z0 <= z <= z1:
                ry = int(2 * HY - y - 3)
                c = mix(far[x, ry] if 0 <= ry < LH else far[x, 0], (0, 0, 0), 0.22)
                if abs((wx - x0) % 1.15) < 0.12 * z / 19: c = ink.k1                  # glazing bars
                L.put(x, y, c)


def near_pipe(L, ink):
    """a district-heating pipe in sheet-metal cladding along the near left, on low stands, diving into the roof"""
    zc, hc, r, xe = 8.55, 0.95, 0.55, -6.0
    for y in range(int(HY) + 1, LH):
        for x in range(LW):
            # intersect the pixel ray with the horizontal cylinder (axis along x at depth zc, height hc)
            dyr = (y + 0.5 - HY) / FL                                   # ray: height = EYE - dyr * z
            best = None
            for s in range(-12, 13):
                z = zc + s * r / 12
                h = EYE - dyr * z
                if (z - zc) ** 2 + (h - hc) ** 2 <= r * r:
                    best = (z, h); break
            if not best: continue
            z, h = best
            wx = (x + 0.5 - VX) * z / FL
            if wx > xe: continue
            ny = (h - hc) / r
            v = 0.24 + 0.44 * clamp(ny + 0.2) ** 1.1 + (0.16 if 0.55 < ny < 0.78 else 0) + (vnoise(wx * 3, h * 9, 1, 61) - 0.5) * 0.04
            sx = (wx + 60) % 2.1
            if sx < 0.09: v -= 0.16                                                   # cladding seams + rivets
            elif sx < 0.18: v += 0.10
            elif abs(sx - 0.30) < 0.05 and (int(ny * 6) % 2 == 0): v -= 0.12
            if vnoise(wx * 1.4, 1, 1, 63) > 0.74 and ny < 0.5: v -= 0.07           # dents, dirt
            L.put(x, y, ink.tone(v, x, y, 12))
    # the elbow down into the roof and a flange
    a = proj(xe, hc + r, zc); b = proj(xe + 1.1, hc + r, zc)
    for y in range(int(a[1]), int(proj(0, 0, zc)[1]) + 1):
        for x in range(int(a[0]), int(b[0]) + 1):
            u = (x + 0.5 - a[0]) / max(1.0, b[0] - a[0])
            L.put(x, y, ink.tone(0.14 + 0.30 * u, x, y, 13))
    L.vline(int(a[0]), a[1], proj(0, 0, zc)[1], ink.k3)
    for wx in (-11.0, -16.0, -21.0, -26.0, -31.0, -36.0):                  # stands under the pipe
        p0, p1 = proj(wx, 0, zc), proj(wx, hc - r, zc)
        L.vline(p0[0], p1[1], p0[1], ink.k1); L.put(p0[0] - 1, p0[1], ink.k1); L.put(p0[0] + 1, p0[1], ink.k1)


def debris(L, ink):
    """a few small things on the near roof: a tin, a crumpled sheet of paper, half a brick, a bottle cap"""
    def at(x, z): return proj(x, 0, z)
    x, y = at(6.4, 10.3); L.put(x, y - 1, ink.k5); L.put(x + 1, y - 1, ink.k3); L.put(x, y, ink.k3); L.put(x + 1, y, ink.k1)
    x, y = at(-3.8, 9.4)
    for dx, dy, c in ((0, 0, ink.k6), (1, 0, ink.k5), (2, 0, ink.k6), (1, -1, ink.k6), (0, 1, ink.k3), (2, 1, ink.k3)):
        L.put(x + dx, y + dy, c)
    x, y = at(-17.5, 12.7)
    for dx in range(4): L.put(x + dx, y - 1, ink.k4 if dx < 3 else ink.k3); L.put(x + dx, y, ink.k1)
    x, y = at(22.0, 13.1); L.put(x, y, ink.k4)


def wires(L, ink, house):
    """cables from the mast's arms into the tower's left scaffold (the plate's own cables carry on from there)"""
    (a1, b1), (a2, b2) = house['arms'][1], house['arms'][2]
    catenary(L, (b1[0], b1[1]), (110, 70), 9.0, ink.k2, step=0.3)
    catenary(L, (b2[0], b2[1]), (117, 90), 7.0, ink.k2, step=0.3)
    catenary(L, (a2[0], a2[1]), (0, 118), 4.0, ink.k2, step=0.3)


# ---------------------------------------------------------------- 4. overlays for the Aseprite source

def overlays():
    chars = Image.open(os.path.join(HERE, 'chars.png')).convert('RGBA')
    # the scale figures stand on canvas y 534; shrink to the logical frame (nearest)
    ch = chars.resize((LW, LH), Image.NEAREST)
    g = Image.new('RGBA', (LW, LH), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    def zone(cx, cy, w, h, col):         # 1067-canvas coords -> logical
        d.rectangle([(cx - w / 2) / K, (cy - h / 2) / K, (cx + w / 2) / K - 1, (cy + h / 2) / K - 1], outline=col)
    kx = 1067 / 800
    zone(400 * kx, 470, 100 * kx, 200, (127, 255, 142, 255))      # Enter Scraper (footbridge)
    zone(50 * kx, 470, 40 * kx, 200, (255, 200, 80, 255))         # to the Crossroad (stair-house door)
    zone(750 * kx, 470, 80 * kx, 200, (255, 200, 80, 255))        # to Burning Bear Street (right edge)
    zone(430 * kx, 170, 240 * kx, 150, (120, 180, 255, 255))      # examine: the sign
    d.line([(0, 178), (LW, 178)], fill=(255, 80, 80, 255))        # the walk line (feet)
    return ch, g


def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    reuse = len(sys.argv) > 2 and sys.argv[2] == 'reuse' and os.path.exists(os.path.join(out, 'plate_raw.png'))
    if reuse: raw = Image.open(os.path.join(out, 'plate_raw.png')).convert('RGB')
    else:
        raw = paint_out_figures(resample()); raw.save(os.path.join(out, 'plate_raw.png'))
    pal = build_palette(raw)
    Q = Quant(pal)
    plate = Q.image(raw)
    ink = Inks(pal)
    bridge = footbridge(plate, ink)
    far = plate.convert('RGBA'); far.alpha_composite(bridge.im); far = far.convert('RGB').load()
    fg = Layer()
    parapet(fg, ink)
    roof(fg, far, ink)
    roof_props(fg, far, ink)
    near_pipe(fg, ink)
    debris(fg, ink)
    house = stair_house(fg, ink)
    wires(fg, ink, house)
    bridge_q, fg_q = Q.image(bridge.im), Q.image(fg.im)
    comp = plate.convert('RGBA'); comp.alpha_composite(bridge_q); comp.alpha_composite(fg_q)
    comp = comp.convert('RGB')
    plate.save(os.path.join(out, 'plate.png')); bridge_q.save(os.path.join(out, 'bridge.png'))
    fg_q.save(os.path.join(out, 'fg.png')); comp.save(os.path.join(out, 'scraper_356.png'))
    comp.resize((LW * K, LH * K), Image.NEAREST).crop((0, 0, 1067, 600)).save(os.path.join(out, 'scraper.png'))
    ch, g = overlays(); ch.save(os.path.join(out, 'chars.png')); g.save(os.path.join(out, 'guides.png'))
    with open(os.path.join(out, 'scraper.gpl'), 'w') as f:
        f.write('GIMP Palette\nName: scraper-1140\nColumns: 8\n#\n')
        for c in pal: f.write('%3d %3d %3d\n' % c)
    print('palette', len(pal), 'colours')


if __name__ == '__main__':
    main()
