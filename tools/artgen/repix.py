"""Re-pixelling the old AI backgrounds the user wants kept (Shed abandoned office, ...): the source is pseudo pixel
art with an irregular block grid (~4.5-5 px), so every logical pixel takes the MOST COMMON palette colour of the middle
of its cell (crisp edges, no blended seams), on a palette built per colour family so small but important families
(the red paint of a graffito, warm window light, moss) keep their own ramps. The result is shown 3x in the game like
scraper_bg.py (356 logical columns * 3 = 1068 -> 1067).
"""
import colorsys
from collections import Counter
from PIL import Image

LW, LH, K = 356, 200, 3


def lum(c): return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def kmeans_pal(px, n):
    if not px: return []
    n = min(n, len(set(px)))
    strip = Image.new('RGB', (len(px), 1)); strip.putdata(px)
    q = strip.quantize(colors=n, method=Image.Quantize.MAXCOVERAGE, kmeans=8)
    pal = q.getpalette()[:3 * n]
    used = sorted(set(q.getpixel((x, 0)) for x in range(q.size[0])))
    return [tuple(pal[3 * i:3 * i + 3]) for i in used]


def family_palette(src, families, rest, step=2):
    """families: [(name, test(h, s, v, rgb) -> bool, n colours)], checked in order; everything else gets `rest` colours"""
    buckets = {f[0]: [] for f in families}; other = []
    p = src.load(); W, H = src.size
    for y in range(0, H, step):
        for x in range(0, W, step):
            c = p[x, y]; h, s, v = colorsys.rgb_to_hsv(*(t / 255 for t in c))
            for name, test, _ in families:
                if test(h, s, v, c): buckets[name].append(c); break
            else: other.append(c)
    pal = []
    for name, _, n in families: pal += kmeans_pal(buckets[name], n)
    pal += kmeans_pal(other, rest)
    out = []
    for c in pal:
        if c not in out: out.append(c)
    return sorted(out, key=lum)


def nearest_index(pal):
    cache = {}
    def f(c):
        r = cache.get(c)
        if r is None:
            def d(i):
                q = pal[i]; rm = (c[0] + q[0]) / 2
                return (2 + rm / 256) * (c[0] - q[0]) ** 2 + 4 * (c[1] - q[1]) ** 2 + (2 + (255 - rm) / 256) * (c[2] - q[2]) ** 2
            r = cache[c] = min(range(len(pal)), key=d)
        return r
    return f


def resample_mode(src, pal, cols=LW, inner=0.6):
    """the whole source width -> `cols` logical columns (square cells); returns the logical image (all rows)"""
    W, H = src.size; cell = W / cols; rows = int(H / cell)
    sp = src.load(); idx = nearest_index(pal)
    q = [[idx(sp[x, y]) for x in range(W)] for y in range(H)]
    out = Image.new('RGB', (cols, rows)); op = out.load()
    m = (1 - inner) / 2
    for j in range(rows):
        y0, y1 = int(j * cell + cell * m), int(j * cell + cell * (1 - m))
        for i in range(cols):
            x0, x1 = int(i * cell + cell * m), int(i * cell + cell * (1 - m))
            cnt = Counter(q[y][x] for y in range(y0, min(H, y1 + 1)) for x in range(x0, min(W, x1 + 1)))
            op[i, j] = pal[cnt.most_common(1)[0][0]]
    return out


def to_canvas(logical):
    """356x200 logical -> the 1067x600 game image (3x hard pixels)"""
    return logical.resize((logical.size[0] * K, logical.size[1] * K), Image.NEAREST).crop((0, 0, 1067, 600))


def write_gpl(path, name, pal):
    with open(path, 'w') as f:
        f.write('GIMP Palette\nName: %s\nColumns: 8\n#\n' % name)
        for c in pal: f.write('%3d %3d %3d\n' % c)
