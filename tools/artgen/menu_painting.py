"""Straighten a phone photo of Marti's menu painting into a flat 1960x1386 picture.

usage: menu_painting.py photo.jpg painting.png [ref.png]

The photo bows a little (lens barrel distortion), so a single perspective transform leaves curved edges: the four
painted edges are measured as polylines and a Coons patch maps them onto the rectangle (PIL MESH transform).
INSET trims the paper's white rim and the shadow it casts on the wall.

ref: an earlier flattening of the same painting (tools/storeart/key_art.jpg = the 2026-11-23 photo). Every hand-placed
coordinate in menu_painting_band.py (the airship, the clock, the Scraper's windows, the characters' outlines) and the
store art's crops are in ITS pixels, and a Coons patch only fixes the edges: inside, two photos still disagree by up
to ~40 px. With ref, the new photo is laid onto it: a grid of patches is matched (high-passed, coarse to fine, so a
darker repaint still matches), outliers in the featureless smoke take their neighbours' median, and the photo is
resampled once through the edges and that displacement field.

The pink tape over the four corners is painted over with what is a little further in (the floor at the bottom, the sky
at the top: the side-band menu layouts show the whole painting).
The edges are for the 2026-11-25 photo (1920x1080, the painting ~1450 px wide); re-measure them for a new photo or a
scan (the 2026-11-23 photo's are in git). With ref they only need to be roughly right.
"""
import statistics
import sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat

W, H = 1960, 1386          # A-format paper, like the WIP photos
INSET = 7
# the painted area's edges in the photo, corner to corner (the corners themselves are under tape: extrapolated from
# quadratic fits; the top right runs into a shadow and was read by eye)
TOP = [(322.0, 25.0), (400, 24.5), (550, 23.9), (700, 24.0), (850, 24.5), (1000, 25.7), (1150, 27.3), (1300, 29.5),
       (1450, 32.3), (1600, 35.6), (1710.3, 38.4)]
BOTTOM = [(291.4, 1047.5), (400, 1054.1), (550, 1061.4), (700, 1066.5), (850, 1069.4), (1000, 1070.1), (1150, 1068.6),
          (1300, 1064.9), (1450, 1059.0), (1600, 1050.9), (1762.2, 1039.7)]
LEFT = [(322.0, 25.0), (318.3, 100), (313.7, 200), (309.5, 300), (305.8, 400), (302.5, 500), (299.5, 600), (297.0, 700),
        (294.9, 800), (293.2, 900), (291.9, 1000), (291.4, 1047.5)]
RIGHT = [(1710.3, 38.4), (1718.4, 100), (1730.3, 200), (1740.5, 300), (1748.9, 400), (1755.6, 500), (1760.6, 600),
         (1763.9, 700), (1765.4, 800), (1765.3, 900), (1763.4, 1000), (1762.2, 1039.7)]
# the tape: where to look for it in the flat painting, and how far in to take what's behind it from
TAPE = [((0, 1225, 115, H), 96), ((1850, 1260, W, H), -84), ((0, 0, 130, 120), 70), ((1800, 0, W, 140), -70)]
STEP = 98                  # the registration grid (painting px)


def along(pts, t, axis):
    a = pts[0][axis] + t * (pts[-1][axis] - pts[0][axis])
    for p, q in zip(pts, pts[1:]):
        if (p[axis] - a) * (q[axis] - a) <= 0:
            f = 0 if q[axis] == p[axis] else (a - p[axis]) / (q[axis] - p[axis])
            return p[0] + f * (q[0] - p[0]), p[1] + f * (q[1] - p[1])
    return pts[0] if t < 0.5 else pts[-1]


def coons(u, v):
    t, b, l, r = along(TOP, u, 0), along(BOTTOM, u, 0), along(LEFT, v, 1), along(RIGHT, v, 1)
    tl, tr, bl, br = TOP[0], TOP[-1], BOTTOM[0], BOTTOM[-1]
    return tuple((1 - v) * t[i] + v * b[i] + (1 - u) * l[i] + u * r[i]
                 - ((1 - u) * (1 - v) * tl[i] + u * (1 - v) * tr[i] + (1 - u) * v * bl[i] + u * v * br[i])
                 for i in (0, 1))


def flatten(photo, disp=None):
    """the photo resampled onto the rectangle; disp(x, y) -> (dx, dy) moves where each output pixel is taken from"""
    def src(x, y):
        dx, dy = disp(x, y) if disp else (0, 0)
        return coons((x + dx + INSET) / (W + 2 * INSET), (y + dy + INSET) / (H + 2 * INSET))
    C = 14
    mesh = []
    for y in range(0, H, C):
        for x in range(0, W, C):
            x1, y1 = min(W, x + C), min(H, y + C)
            quad = (src(x, y), src(x, y1), src(x1, y1), src(x1, y))      # PIL: nw, sw, se, ne
            mesh.append(((x, y, x1, y1), tuple(c for p in quad for c in p)))
    return photo.transform((W, H), Image.MESH, mesh, Image.BICUBIC)


def register(ref, flat):
    """disp(x, y): where the spot at (x, y) of ref is in flat (a displacement field on a STEP grid, bilinear)"""
    def hp(im):
        e = im.filter(ImageFilter.GaussianBlur(0.9))
        return ImageChops.subtract(e, e.filter(ImageFilter.GaussianBlur(7.5)), 1, 128)
    ref, flat = ref.convert('L'), flat.convert('L')
    levels = {f: (hp(ref.resize((W // f, H // f), Image.BOX)), hp(flat.resize((W // f, H // f), Image.BOX)))
              for f in (4, 2, 1)}

    def search(f, x, y, dx, dy, rad, half):
        r, m = levels[f]
        ax, ay = round(x / f - half), round(y / f - half)
        a = r.crop((ax, ay, ax + 2 * half, ay + 2 * half))
        bx, by = round((x + dx) / f - half), round((y + dy) / f - half)
        res = sorted((ImageStat.Stat(ImageChops.difference(a, m.crop((bx + i, by + j, bx + i + 2 * half,
                                                                      by + j + 2 * half)))).mean[0], i, j)
                     for j in range(-rad, rad + 1) for i in range(-rad, rad + 1))
        s, i, j = res[0]
        far = next((s2 for s2, i2, j2 in res if max(abs(i2 - i), abs(j2 - j)) >= 3), s)
        return (bx + i - ax) * f, (by + j - ay) * f, far - s

    cols, rows = W // STEP + 1, H // STEP + 1
    g = []
    for r in range(rows):
        g.append([])
        for c in range(cols):
            x, y = min(max(c * STEP, 64), W - 64), min(max(r * STEP, 64), H - 64)
            dx, dy, _ = search(4, x, y, 0, 0, 14, 12)          # +-56 px
            dx, dy, _ = search(2, x, y, dx, dy, 2, 24)
            dx, dy, sure = search(1, x, y, dx, dy, 2, 48)
            g[-1].append([dx, dy, sure])
    for _ in range(3):         # outliers (the smoke has few features) -> their neighbours' median
        for r in range(rows):
            for c in range(cols):
                nb = [g[rr][cc] for rr in range(max(0, r - 1), min(rows, r + 2))
                      for cc in range(max(0, c - 1), min(cols, c + 2)) if (rr, cc) != (r, c)]
                mx, my = statistics.median(n[0] for n in nb), statistics.median(n[1] for n in nb)
                e = g[r][c]
                off = max(abs(e[0] - mx), abs(e[1] - my))
                if off > 6 or (e[2] < 1.5 and off > 2.5):
                    e[0], e[1] = mx, my

    def disp(x, y):
        fx, fy = min(max(x / STEP, 0), cols - 1.0001), min(max(y / STEP, 0), rows - 1.0001)
        c, r = int(fx), int(fy)
        u, v = fx - c, fy - r
        return tuple((1 - u) * (1 - v) * g[r][c][k] + u * (1 - v) * g[r][c + 1][k]
                     + (1 - u) * v * g[r + 1][c][k] + u * v * g[r + 1][c + 1][k] for k in (0, 1))
    return disp


def untape(im):
    px = im.load()
    out = im.copy()
    op = out.load()
    mask = Image.new('L', im.size, 0)
    mp = mask.load()
    for (x0, y0, x1, y1), _ in TAPE:
        for y in range(y0, y1):
            for x in range(x0, x1):
                r, g, b = px[x, y]
                if r > 95 and r - g > 45 and r - b > 30:          # pink, also in the shadow of a corner
                    mp[x, y] = 255
    mask = mask.filter(ImageFilter.MaxFilter(7))
    mp = mask.load()
    for (x0, y0, x1, y1), dx in TAPE:
        for y in range(y0, y1):
            for x in range(x0, x1):
                if mp[x, y]:
                    sx = x + dx
                    while mp[sx, y]:
                        sx += dx
                    op[x, y] = px[sx, y]
    return Image.composite(out, im, mask.filter(ImageFilter.GaussianBlur(1.5)))


if __name__ == '__main__':
    photo = Image.open(sys.argv[1]).convert('RGB')
    flat = flatten(photo)
    if len(sys.argv) > 3:
        flat = flatten(photo, register(Image.open(sys.argv[3]), flat))
    untape(flat).save(sys.argv[2])
