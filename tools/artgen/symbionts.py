"""Symbiont HUD art -- the six symbionts of the demo + the pods they live in.

Symbionts (32x32, 4 idle frames: 0 rest / 1 breath / 2 blink-or-glint / 3 accent):
  thorne-still  -- a bruise-violet brain nodule with a crown of thorns, one lazy flirting eye, a slime drip (winks)
  neme          -- a luminous green ganglion-bulb with a crown of fronds tipped by light buds and one gold ocellus
  ulvarex       -- an oil-sheen film-lens holding a tiny sunset; the setting sun is its eye (one brow raised)
  brine         -- a curled membrane scroll written with glyph-veins, crusted with salt, dripping brine
  osswine       -- a pale fiddlehead of bone segments unfurling from a knuckle, a cold blue eye in the curl
  palinode      -- a pebble whose right part is "unsaid": only a dashed shimmer where the stone should be
  generic       -- a plain spore blob for any future symbiont without art
Pods (48x58, the HUD "rosary" hanging from the G/D medallion):
  0 open pod (back)  1 its front lip (drawn over the symbiont)  2 sealed pod (locked slot)  3 cord end  4 glow (ADD, tinted)

python3 symbionts.py <outdir>  ->  symbionts.png (4 cols x 7 rows) + symbiont_pods.png (5 frames)
                                   + symb/<id>/<n>.png, pod/<name>.png (for Aseprite) + preview.png"""
import sys, os, math
from PIL import Image
from common import make_noise, band, INK, h32
from pal_symb import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
ORDER = ['thorne-still', 'neme-crownmire', 'ulvarex-borrowed-horizon', 'brine-scripture', 'osswine', 'palinode', 'generic']
nA, nB, nC = make_noise(3, 71, 80, 80), make_noise(2, 72, 80, 80), make_noise(5, 73, 80, 80)

def norm(v):
    l = math.sqrt(sum(c * c for c in v)) or 1
    return tuple(c / l for c in v)

LIGHT = norm((-0.55, -0.7, 0.6))
def lit(n, amb=0.2):
    return max(0.0, n[0] * LIGHT[0] + n[1] * LIGHT[1] + n[2] * LIGHT[2]) * (1 - amb) + amb

class Spr:
    def __init__(s, w=32, h=32):
        s.w, s.h, s.px, s.part = w, h, {}, {}
    def put(s, x, y, c, part='x'):
        x, y = int(math.floor(x)), int(math.floor(y))
        if 0 <= x < s.w and 0 <= y < s.h: s.px[(x, y)] = c; s.part[(x, y)] = part
    def has(s, x, y): return (x, y) in s.px

    def blob(s, cx, cy, rx, ry, shade, part='x'):
        """shade(x, y, n) for every pixel centre inside the ellipse; n = sphere normal"""
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                u, w = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                d = u * u + w * w
                if d > 1: continue
                c = shade(x, y, (u, w, math.sqrt(1 - d)))
                if c: s.put(x, y, c, part)

    def stroke(s, pts, width, colour, part='x'):
        """thick polyline; width(t) / colour(t, x, y) over t in 0..1"""
        n = len(pts) - 1
        for i, (px, py) in enumerate(pts):
            t = i / max(1, n); r = width(t) / 2
            for y in range(int(py - r) - 1, int(py + r) + 2):
                for x in range(int(px - r) - 1, int(px + r) + 2):
                    if (x + 0.5 - px) ** 2 + (y + 0.5 - py) ** 2 <= r * r + 0.15:
                        c = colour(t, x, y)
                        if c: s.put(x, y, c, part)

    def outline(s, c=INK, skip=(), allow=None):
        add = {}
        for (x, y) in s.px:
            if s.part.get((x, y)) in skip: continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q in s.px or not (0 <= q[0] < s.w and 0 <= q[1] < s.h): continue
                if allow and not allow(*q): continue
                add[q] = c
        for q, cc in add.items(): s.px[q] = cc; s.part[q] = 'outline'

    def image(s):
        im = Image.new('RGBA', (s.w, s.h), (0, 0, 0, 0)); p = im.load()
        for (x, y), c in s.px.items(): p[x, y] = (c + (255,)) if len(c) == 3 else c
        return im

def curve(f, n=60): return [f(i / n) for i in range(n + 1)]
def tone(k, v, x, y): return col(k, band(v, x, y))

def drop(s, x, y0, stem, k):
    """a hanging drip: 1px stem, then a 2px bead with a highlight"""
    for i in range(stem): s.put(x, y0 + i, k[2], 'drip')
    b = y0 + stem
    for dx, dy, c in ((0, 0, k[3]), (1, 0, k[2]), (0, 1, k[2]), (1, 1, k[1])): s.put(x + dx, b + dy, c, 'drip')

# --- Thorne-Still -----------------------------------------------------------------------------------------------------
def thorne(f):
    s = Spr(); cx, cy = 16, 19.5
    rx, ry = (11, 8.5) if f == 1 else (10.5, 8)
    for i, (a, L, bend) in enumerate(((-150, 7, 1.8), (-112, 8, 1.2), (-72, 8, -1.2), (-32, 7, -1.8))):
        a = math.radians(a); bx, by = cx + math.cos(a) * rx * 0.75, cy + math.sin(a) * ry * 0.75
        L += 1 if f == 1 else 0; dx, dy = math.cos(a), math.sin(a)
        fn = lambda t: (bx + dx * L * t - dy * bend * t * t, by + dy * L * t + dx * bend * t * t)
        s.stroke(curve(fn, 30), lambda t: 3.4 * (1 - t) + 0.6, lambda t, x, y: THORN[1], 'thorn')
        s.stroke(curve(lambda t: (fn(t)[0] - 0.8, fn(t)[1] - 0.4), 30)[:14], lambda t: 0.9, lambda t, x, y: THORN[3], 'thorn')
    def body(x, y, n):
        v = 0.9 + 4.4 * lit(n)
        g = math.sin((nC(x * 1.4 + 7, y * 1.4 + 3) * 2.2 + x * 0.12) * 6.0)
        if g > 0.55: v -= 1.7                    # sulci
        elif g < -0.35: v += 0.7                 # gyri crowns
        if y < 16 and abs(x + 0.5 - (16 + math.sin(y * 0.8) * 0.6)) < 0.7: v -= 2
        return tone(BRUISE, v, x, y)
    s.blob(cx, cy, rx, ry, body, 'body')
    ex, ey, erx, ery = 13.5, 20.5, 5.0, 3.2
    inside = lambda x, y: abs(y + 0.5 - ey) <= ery * max(0.0, 1 - ((x + 0.5 - ex) / erx) ** 2) ** 0.9
    for y in range(16, 25):                               # the heavy lid, a shade lighter than the brain
        for x in range(8, 20):
            if inside(x, y) and y < 20: s.put(x, y, BRUISE[5] if y < 19 else BRUISE[4], 'lid')
    if f == 2:   # the wink: closed lid with lashes
        for x in range(9, 19):
            u = (x + 0.5 - ex) / erx
            if abs(u) <= 1: s.put(x, 20.6 + 1.2 * (1 - u * u) * 0.0 + (0 if abs(u) < 0.6 else -0.6 if u < 0 else 0), THORN[0], 'eye')
        for x in range(10, 18): s.put(x, 21, BRUISE[4], 'eye')
        s.put(9, 21, THORN[0], 'eye'); s.put(8, 22, THORN[0], 'eye'); s.put(11, 22, THORN[0], 'eye')
    else:
        for y in range(19, 25):
            for x in range(8, 20):
                if not inside(x, y) or y < 20: continue
                c = OOZE[3] if y < 22 else OOZE[2]
                if (x - 14) ** 2 + (y - 20.8) ** 2 <= 3.6: c = BRUISE[1]
                s.put(x, y, c, 'eye')
        for x in range(9, 19):
            if inside(x, 19): s.put(x, 19, THORN[0], 'eye')
        s.put(8, 19, THORN[0], 'eye'); s.put(7, 18, THORN[0], 'eye')      # a lash at the outer corner
        s.put(14, 20, INK, 'eye'); s.put(14, 21, INK, 'eye'); s.put(13, 20, OOZE[4], 'eye')
    for x, y in ((17, 24), (18, 25), (19, 25), (20, 25), (21, 24), (22, 23)): s.put(x, y, BRUISE[0], 'mouth')
    for x, y in ((18, 26), (19, 26), (20, 26)): s.put(x, y, BRUISE[4], 'mouth')
    s.outline()
    if f == 3:
        drop(s, 21, 27, 1, OOZE); drop(s, 21, 30, 0, OOZE)
    else:
        drop(s, 21, 27, 1 if f != 1 else 2, OOZE)
    return s

# --- Neme of the Crownmire --------------------------------------------------------------------------------------------
def neme(f):
    s = Spr(); cx, cy = 16, 19.5
    for i, ex in enumerate((10, 14, 18, 22)):
        pts = curve(lambda t: (cx + (ex - cx) * t + math.sin(t * 3 + i) * 0.8, 24 + 7.5 * t), 24)
        s.stroke(pts, lambda t: 1.0, lambda t, x, y: NEME[2] if t < 0.6 else NEME[1], 'root')
    lens = [8, 9, 10, 9, 8]
    tips = []
    for i, a in enumerate((-165, -128, -90, -52, -15)):
        a = math.radians(a); bx, by = cx + math.cos(a) * 4, cy + math.sin(a) * 5
        L = lens[i] + (1 if f == 1 else 0); dx, dy = math.cos(a), math.sin(a); sg = 1 if i % 2 else -1
        fn = lambda t: (bx + dx * L * t - dy * math.sin(t * math.pi) * 1.4 * sg, by + dy * L * t + dx * math.sin(t * math.pi) * 1.4 * sg)
        s.stroke(curve(fn, 30), lambda t: 1.9 if t < 0.2 else 1.0, lambda t, x, y: NEME[3] if t < 0.55 else NEME[4], 'frond')
        tips.append(fn(1.0) + (dx, dy))
    def bulb(x, y, n):
        v = 1.3 + 4.0 * lit(n) + (0.8 if f == 1 else 0)
        for off in (-3, 3):
            if abs(x + 0.5 - (cx + off + 1.2 * math.sin((y - 19) * 0.5))) < 0.5: v -= 1.1
        return tone(NEME, v, x, y)
    s.blob(cx, cy, 6.2 if f == 1 else 5.8, 6.8, bulb, 'bulb')
    for y in range(15, 23):
        for x in range(12, 21):
            d = math.hypot(x + 0.5 - 16, y + 0.5 - 18.5)
            if d <= 1.4: s.put(x, y, GOLD[2] if f != 2 else NEME[1], 'eye')
            elif d <= 2.4: s.put(x, y, NEME[1], 'eye')
    if f == 2:
        s.put(15, 18, GOLD[0], 'eye'); s.put(16, 18, GOLD[0], 'eye')
    else:
        s.put(15, 17, GOLD[3], 'eye')
    s.outline(NEME[0], skip=('root',))
    for tx, ty, dx, dy in tips:
        bx, by = int(tx), int(ty)
        if f == 3:
            for ox in (-1, 0, 1):
                for oy in (-1, 0, 1): s.put(bx + ox, by + oy, NEME[4], 'bud')
            s.put(bx, by, NEME[6], 'bud'); s.put(bx + round(dx * 3), by + round(dy * 3), NEME[5], 'spark')
        else:
            for ox, oy, c in ((0, 0, NEME[5]), (1, 0, NEME[4]), (0, 1, NEME[4]), (1, 1, NEME[3])): s.put(bx + ox, by + oy, c, 'bud')
    return s

# --- Ulvarex the Borrowed Horizon -------------------------------------------------------------------------------------
def ulvarex(f):
    s = Spr(); cx, cy, rx, ry, hz = 16, 17.5, 12.5, 9.5, 18
    def film(x, y, n):
        u, w = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
        if u * u + w * w > 0.80:                       # the oil-sheen rim
            seg = int(((math.atan2(w, u) + math.pi) / (2 * math.pi)) * 8 + (f == 1) + 2 * (f == 3)) % 4
            return IRIS[seg]
        if y < hz:
            return tone(SKY, 5.3 - (hz - y) * 0.62, x, y)
        xx = x + (1 if f == 3 and y % 2 else 0)
        dd = y - hz
        if abs(xx + 0.5 - 16) < 4.8 - dd * 0.55 and dd % 2 == 0: return SKY[5] if dd < 3 else SKY[4]
        return tone(WATER, 3.3 - dd * 0.35 + (nB(xx, y) - 0.5) * 0.8, x, y)
    s.blob(cx, cy, rx, ry, film, 'film')
    sun = 4.6 if f != 2 else 0
    for y in range(10, hz):
        for x in range(10, 23):
            d = math.hypot(x + 0.5 - 16, y + 0.5 - hz)
            if d <= sun: s.put(x, y, SKY[6] if d < 2.6 else SKY[5], 'sun')
    if f == 2:
        for x in range(12, 21): s.put(x, hz - 1, SKY[6], 'sun')
        for x in range(13, 20): s.put(x, hz - 2, SKY[4], 'sun')
    else:
        s.put(16, 15, INK, 'sun'); s.put(16, 16, INK, 'sun'); s.put(15, 15, (255, 255, 255), 'sun')
    lift = 0 if f != 2 else 1
    for x, y in ((14, 11), (15, 10), (16, 10), (17, 9), (18, 9), (19, 9), (20, 10)):
        s.put(x, y + lift, WATER[6], 'brow')
    for x, y in ((7, 14), (7, 13), (8, 12), (9, 11), (10, 10)): s.put(x, y, WATER[6], 'glare')
    s.outline(WATER[0])
    return s

# --- Brine Scripture --------------------------------------------------------------------------------------------------
def brine(f):
    s = Spr(); bot = 25 + (1 if f == 1 else 0)
    def edge(y): return 9 + round(0.8 * math.sin(y * 0.7)), 23 + round(0.8 * math.sin(y * 0.7 + 1.3))
    for y in range(8, bot):
        l, r = edge(y)
        for x in range(l, r + 1):
            v = 5.6 - (x - l) * 0.13
            if x == l: v += 0.8
            if (x * 7 + y * 3) % 23 == 0: v -= 1                  # fibres in the membrane
            s.put(x, y, tone(MEMB, v, x, y), 'sheet')
    for ri, gy in enumerate((11, 14, 17, 20, 23)):          # lines of salt-script
        if gy + 1 >= bot: continue
        l, r = edge(gy); x = l + 2; lit_row = (f == 2 and ri == 2)
        while x < r - 1:
            h = h32(x, gy, 11); run = 1 + h % 3
            for k in range(run):
                if x + k < r - 1: s.put(x + k, gy, AMBER[1] if lit_row else MEMB[2], 'glyph')
            if h % 4 == 0: s.put(x, gy - 1, AMBER[1] if lit_row else MEMB[2], 'glyph')      # ascender
            if h % 7 == 0: s.put(x + run - 1, gy + 1, AMBER[0] if lit_row else MEMB[2], 'glyph')
            x += run + 1 + (h >> 4) % 2
        if lit_row: s.put(l + 4, gy - 2, AMBER[2], 'glyph'); s.put(r - 4, gy - 2, AMBER[2], 'glyph')
    def roll(cy, part):
        def sh(x, y, n): return tone(MEMB, 1.6 + 4.6 * lit((0.0, n[1], n[2]), 0.1), x, y)
        s.blob(16, cy, 10, 1.9, sh, part)
        for ex in (6, 25):
            s.put(ex, int(cy) - 1, MEMB[2], part); s.put(ex, int(cy), MEMB[1], part)
    roll(6.5, 'roll'); roll(bot + 1.5, 'roll')
    s.outline(MEMB[0])
    crystals = [(9, 4), (13, 4), (21, 4), (24, 12), (24, 19), (11, bot + 3)]
    for i, (x, y) in enumerate(crystals):
        s.put(x, y, MEMB[7], 'salt'); s.put(x + 1, y, MEMB[6], 'salt'); s.put(x, y + 1, MEMB[6], 'salt'); s.put(x + 1, y + 1, MEMB[4], 'salt')
        if f == 3 and i in (1, 3):
            for dx, dy in ((-1, 0), (2, 0), (0, -1), (1, -1), (0, 2)): s.put(x + dx, y + dy, MEMB[7], 'spark')
    drop(s, 17, bot + 3, 1 if f != 3 else 2, MEMB[2:])
    return s

# --- Osswine ----------------------------------------------------------------------------------------------------------
def osswine(f):
    s = Spr()
    def knuckle(x, y, n):
        v = 1.8 + 4.8 * lit(n)
        if (x, y) in ((13, 27), (14, 27), (14, 28)): v = 0.6
        return tone(BONE, v, x, y)
    for sg in (-1, 1):                                       # two dry rootlets under the knuckle
        rt = curve(lambda t: (16 + sg * (4 + 4 * t), 29 + 2.2 * t), 12)
        s.stroke(rt, lambda t: 0.9, lambda t, x, y: BONE[3], 'hair')
    s.blob(16, 27.5, 6.8, 3.4, knuckle, 'knuckle')
    r0, turns, C = (6.6, 1.1, (18.6, 10.0)) if f == 1 else (6.0, 1.25, (18.0, 10.5))
    sx, sy = C[0] - r0, C[1]
    def path(t):
        if t < 0.4:                                     # the stem, out of the knuckle
            u = t / 0.4
            return (16 + (sx - 16) * u + math.sin(u * math.pi) * 1.0, 25.5 + (sy - 25.5) * u)
        u = (t - 0.4) / 0.6; th = math.pi + u * turns * 2 * math.pi
        r = r0 * (1 - 0.8 * u)
        return (C[0] + r * math.cos(th), C[1] + r * math.sin(th))
    pts = curve(path, 200)
    for i in range(len(pts) - 1, -1, -1):              # tip first, so the thicker stem overlaps it
        t = i / (len(pts) - 1)
        x0, y0 = pts[i]; x1, y1 = pts[i + 1] if i < len(pts) - 1 else (2 * x0 - pts[i - 1][0], 2 * y0 - pts[i - 1][1])
        tx, ty = norm((x1 - x0, y1 - y0, 0))[:2]
        nx, ny = -ty, tx
        w = 3.4 if t < 0.55 else 3.4 - (t - 0.55) * 4.4
        for k in range(-7, 8):
            o = k * 0.25
            if abs(o) > w / 2: continue
            side = (nx * (-0.6) + ny * (-0.8)) * (1 if o > 0 else -1)
            v = 5.0 + 1.7 * side * min(1, abs(o) / max(0.5, w / 2))
            s.put(x0 + nx * o, y0 + ny * o, col(BONE, v), 'frond')
    acc, prev = 0.0, pts[0]
    for i, p in enumerate(pts[1:], 1):                  # vertebral joints every ~3 px
        acc += math.hypot(p[0] - prev[0], p[1] - prev[1]); prev = p
        if acc >= 3.0 and i < len(pts) - 30:
            acc = 0.0
            x0, y0 = p; x1, y1 = pts[i + 1]
            tx, ty = norm((x1 - x0, y1 - y0, 0))[:2]
            for o in (-1, 0, 1): s.put(x0 - ty * o, y0 + tx * o, BONE[3], 'frond')
    drift = 1 if f == 3 else 0
    for t0 in (0.62, 0.7):                              # dry threads hanging from the curl
        bx, by = path(t0)
        hair = curve(lambda t: (bx + 0.6 * t + drift * t, by + 2 + 4 * t), 10)
        s.stroke(hair, lambda t: 0.9, lambda t, x, y: BONE[4] if t < 0.5 else BONE[3], 'hair')
    s.outline(skip=('hair',))
    ex, ey = int(C[0]), int(C[1])
    if f == 2:
        for dx, dy in ((-1, 0), (2, 0), (0, -1), (1, -1), (0, 2), (1, 2)): s.put(ex + dx, ey + dy, COLD[1], 'eye')
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)): s.put(ex + dx, ey + dy, COLD[2], 'eye')
        s.put(ex, ey, COLD[3], 'eye')
    else:
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)): s.put(ex + dx, ey + dy, COLD[1], 'eye')
        s.put(ex, ey, COLD[2], 'eye')
    return s

# --- Palinode ---------------------------------------------------------------------------------------------------------
def palinode(f):
    s = Spr(); cx, cy, rx, ry = 15.5, 18.5, 11.5, 8.5
    def shape(x, y):
        u, w = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
        th = math.atan2(w, u)
        return math.hypot(u, w) / (1 + 0.07 * math.sin(3 * th + 1) + 0.04 * math.sin(5 * th + 2))
    open_ = 1 if f == 1 else 0
    def seam(y): return 23 - (y - 9) * 0.42 + (0.4, 0.0, -0.4, 0.0, 0.2)[y % 5] - open_
    for y in range(6, 30):
        for x in range(2, 30):
            d = shape(x, y)
            if d > 1: continue
            if x + 0.5 < seam(y):
                n = ((x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry, math.sqrt(max(0.0, 1 - d * d)))
                v = 1.2 + 5.2 * lit(n) + (nB(x * 1.7, y * 1.7) - 0.5) * 0.9
                if h32(x, y, 3) % 31 == 0: v -= 2
                s.put(x, y, tone(PEBBLE, v, x, y), 'stone')
            elif d > 0.86:
                if (x + y) % 2 == 0: s.put(x, y, SHIM[2] if (x + y + 2 * f) % 6 == 0 else SHIM[1], 'gap')
            elif f == 3:
                if (x + y) % 2 == 0: s.put(x, y, PEBBLE[2], 'gap')
            else:
                h = h32(x, y, f)
                if h % 17 == 0: s.put(x, y, SHIM[3], 'gap')
                elif h % 9 == 0: s.put(x, y, SHIM[1], 'gap')
    for y in range(6, 30):                              # the cut face glows
        xs = [x for x in range(2, 30) if s.part.get((x, y)) == 'stone']
        if xs and shape(max(xs) + 1, y) <= 0.95:
            s.put(max(xs), y, SHIM[3], 'stone')
            if len(xs) > 1: s.put(max(xs) - 1, y, SHIM[2] if open_ else PEBBLE[1], 'stone')
    s.outline(skip=('gap',), allow=lambda x, y: shape(x, y) > 1 and x + 0.5 < seam(y) + 1.5)
    return s

# --- generic fallback -------------------------------------------------------------------------------------------------
def generic(f):
    s = Spr()
    for i in range(6):
        a = i / 6 * 2 * math.pi + 0.3; L = 9 + (1 if f == 1 else 0)
        pts = curve(lambda t: (16 + math.cos(a) * L * t + math.sin(t * 3) * 0.6, 17 + math.sin(a) * L * t), 20)
        s.stroke(pts, lambda t: 1.0, lambda t, x, y: NEME[3] if t < 0.6 else NEME[2], 'fil')
    s.blob(16, 17, 6 + (0.4 if f == 1 else 0), 6, lambda x, y, n: tone(NEME, 1.2 + 4.2 * lit(n), x, y), 'blob')
    for i, (x, y) in enumerate(((13, 15), (18, 14), (15, 19), (19, 18))):
        s.put(x, y, NEME[6] if (f == 2 and i == 1) or (f == 3) else NEME[5], 'dot')
    s.outline(NEME[0], skip=('fil',))
    return s

DRAW = {'thorne-still': thorne, 'neme-crownmire': neme, 'ulvarex-borrowed-horizon': ulvarex, 'brine-scripture': brine,
        'osswine': osswine, 'palinode': palinode, 'generic': generic}

# --- pods -------------------------------------------------------------------------------------------------------------
PW, PH, PCX = 48, 58, 24
def cord_x(y): return PCX + round(1.2 * math.sin(2 * math.pi * y / PH))

def draw_cord(s, y0, y1):
    for y in range(y0, y1):
        x = cord_x(y)
        for i in range(3):
            v = (2, 3, 4, 3)[(y + i) % 4] - (1 if i == 2 else 0)
            s.put(x - 1 + i, y, CORD[v], 'cord')

def husk_hw(y, rx, cy=30, ry=23):
    t = (y + 0.5 - cy) / ry
    if abs(t) >= 1: return 0
    return rx * math.sqrt(1 - t * t) * (0.85 + 0.15 * (y - 7) / 46)

def husk(s, rx, k, wrinkle):
    for y in range(5, 56):
        hw = husk_hw(y, rx)
        for x in range(PCX - 22, PCX + 22):
            dx = x + 0.5 - PCX
            if hw <= 0 or abs(dx) > hw: continue
            nx, ny = dx / hw, (y + 0.5 - 30) / 23
            n = norm((nx * 0.9, ny * 0.8, math.sqrt(max(0.05, 1 - nx * nx - (ny * 0.8) ** 2))))
            v = 0.9 + 5.4 * lit(n, 0.15) + (nB(x * 1.2, y * 1.2) - 0.5) * 0.8
            ru = math.asin(max(-1, min(1, nx))) / (math.pi / 2)
            fr = (ru * 3.5 + 0.5) % 1
            groove = fr < 0.12
            if groove: v -= 1.8
            elif fr < 0.26: v += 0.8
            if wrinkle and abs(math.sin(y * 0.9 + nC(x, y) * 4)) < 0.16: v -= 1.2
            s.put(x, y, tone(k, v, x, y), 'husk')
            if groove and not wrinkle and 10 < y < 52 and int(ru * 3.5 + 0.5) % 2 == 0 and h32(x, y) % 3:
                s.put(x, y, VEIN[1] if (y + x) % 5 else VEIN[2], 'vein')

def open_hw(y): return 15 * max(0.0, 1 - ((y + 0.5 - 31) / 18) ** 2) ** 0.75 * (1 + 0.05 * math.sin(y * 1.3) + 0.04 * math.sin(y * 0.5 + 2))

def pod_open():
    s = Spr(PW, PH); draw_cord(s, 0, PH)
    husk(s, 19, HUSK, False)
    for y in range(12, 50):
        ow = open_hw(y)
        for x in range(PCX - 16, PCX + 16):
            dx = x + 0.5 - PCX
            if abs(dx) < ow - 1.1:
                v = 1.0 + 2.4 * (y - 13) / 36 + 1.0 * dx / 15
                s.put(x, y, tone(CAV, v, x, y), 'cavity')
            elif abs(dx) < ow:                           # the fleshy inner lip
                s.put(x, y, LIP[2] if (dx < 0 and y < 34) or y > 42 else LIP[1], 'lip')
            elif abs(dx) < ow + 1.2 and s.has(x, y):
                s.put(x, y, HUSK[7] if dx < 0 and y < 36 else HUSK[6] if y > 40 else HUSK[5], 'rim')
    for x in range(PCX - 3, PCX + 4):                   # the top rim of the slit
        for y in range(12, 15):
            if s.part.get((x, y)) in ('cavity', 'lip') and s.part.get((x, y - 1)) not in ('cavity', 'lip'): s.put(x, y - 1, HUSK[6], 'rim')
    s.outline()
    return s

def open_bottom(x):
    dx = abs(x + 0.5 - PCX)
    ys = [y for y in range(12, 50) if open_hw(y) > dx]
    return (max(ys) + 1) if ys else None

def pod_lip(open_img):
    im = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); p, q = im.load(), open_img.load()
    for x in range(PCX - 18, PCX + 18):
        b = open_bottom(x)
        if b is None: b = 34 + int(abs(x + 0.5 - PCX) * 0.3)
        for y in range(max(b, 32), PH):
            if q[x, y][3]: p[x, y] = q[x, y]
    return im

def pod_sealed():
    s = Spr(PW, PH); draw_cord(s, 0, PH)
    husk(s, 15, DRY, True)
    for y in range(11, 49):
        x = PCX + (1 if (y // 6) % 2 else 0) - 1
        s.put(x, y, DRY[0], 'seam')
        if y % 4 == 2:
            for dx in range(-2, 3): s.put(x + dx, y, CORD[3] if abs(dx) < 2 else CORD[2], 'stitch')
    def wax(x, y, n):
        d = math.hypot(x + 0.5 - PCX, y + 0.5 - 30)
        v = 0.6 + 3.0 * lit(n)
        if 1.5 < d < 2.4 or d < 0.8: v = 0.8
        return tone(WAX, v, x, y)
    s.blob(PCX, 30, 3.8, 3.4, wax, 'wax')
    s.put(PCX + 1, 34, WAX[2], 'wax'); s.put(PCX + 1, 35, WAX[1], 'wax')
    s.outline()
    return s

def pod_end():
    s = Spr(PW, PH); draw_cord(s, 0, 9)
    s.blob(PCX, 9.5, 3.2, 2.4, lambda x, y, n: tone(CORD, 1.2 + 3.4 * lit(n), x, y), 'knot')
    s.outline()
    for i, dx in enumerate((-7, -4, -1, 2, 5, 8)):
        pts = curve(lambda t: (PCX + dx * t + math.sin(t * 3 + i) * 0.7, 11 + (8 + i % 3 * 3) * t), 24)
        s.stroke(pts, lambda t: 1.0, lambda t, x, y: CORD[3] if t < 0.5 else CORD[2], 'hypha')
        ex, ey = pts[-1]; s.put(ex, ey, VEIN[3] if i % 2 else VEIN[2], 'tip')
    return s

def pod_glow():
    im = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); p = im.load()
    for y in range(PH):
        for x in range(PW):
            d = math.hypot((x + 0.5 - PCX) / 15, (y + 0.5 - 31) / 17)
            a = 150 if d < 0.42 else 90 if d < 0.72 else 40 if d < 1.0 else 0
            if 0.38 < d < 0.46 or 0.68 < d < 0.76 or 0.96 < d < 1.04:   # dithered seams between the bands
                if (x + y) % 2: a = {150: 90, 90: 40, 40: 0, 0: 0}[a]
            if a: p[x, y] = (255, 255, 255, a)
    return im

# --- output -----------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    sheet = Image.new('RGBA', (32 * 4, 32 * len(ORDER)), (0, 0, 0, 0))
    for r, sid in enumerate(ORDER):
        os.makedirs(f'{OUT}/symb/{sid}', exist_ok=True)
        for fr in range(4):
            im = DRAW[sid](fr).image()
            im.save(f'{OUT}/symb/{sid}/{fr}.png'); sheet.paste(im, (fr * 32, r * 32))
    sheet.save(f'{OUT}/symbionts.png')
    os.makedirs(f'{OUT}/pod', exist_ok=True)
    op = pod_open().image()
    pieces = [('open', op), ('lip', pod_lip(op)), ('sealed', pod_sealed().image()), ('end', pod_end().image()), ('glow', pod_glow())]
    pods = Image.new('RGBA', (PW * len(pieces), PH), (0, 0, 0, 0))
    for i, (n, im) in enumerate(pieces):
        im.save(f'{OUT}/pod/{n}.png'); pods.paste(im, (i * PW, 0))
    pods.save(f'{OUT}/symbiont_pods.png')
    write_gpl(f'{OUT}/symbionts.gpl')
    print('ok', OUT)
