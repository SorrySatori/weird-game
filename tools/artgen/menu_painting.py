"""Straighten the phone photo of Marti's finished menu painting (2026-11-23) into a flat 1960x1386 picture.

usage: menu_painting.py photo.jpg painting.png

The photo bows a little (lens barrel distortion), so a single perspective transform leaves curved edges: the four
painted edges are measured as polylines and a Coons patch maps them onto the rectangle (PIL MESH transform).
INSET trims the paper's white rim and the shadow it casts on the wall.
The pink tape over the four corners is painted over with what is a little further in (the floor at the bottom, the sky
at the top: the side-band menu layouts show the whole painting).
The coordinates are for the 2026-11-23 photo (2048x1467); re-measure them for a new photo or a scan.
"""
import sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter

W, H = 1960, 1386          # A-format paper, like the WIP photos
INSET = 7
# the painted area's edges in the photo, corner to corner (the corners themselves are under tape: extrapolated)
TOP = [(42, 31), (200, 30), (500, 23), (900, 21), (1300, 20), (1650, 23), (1992, 24)]
BOTTOM = [(36, 1431), (200, 1429), (500, 1430), (1000, 1428.6), (1400, 1423), (1700, 1416), (1850, 1416), (2025, 1413)]
LEFT = [(42, 31), (40, 150), (35, 300), (30, 500), (28, 800), (30, 1000), (33, 1200), (36, 1431)]
RIGHT = [(1992, 24), (1998, 200), (2008, 400), (2017, 700), (2021, 950), (2025, 1150), (2026, 1330), (2025, 1413)]
# the tape: where to look for it in the flat painting, and how far in to take what's behind it from
TAPE = [((0, 1225, 115, H), 96), ((1855, 1285, W, H), -84), ((0, 0, 130, 120), 70), ((1830, 0, W, 120), -70)]


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


def flatten(photo):
    def src(x, y):
        return coons((x + INSET) / (W + 2 * INSET), (y + INSET) / (H + 2 * INSET))
    C = 28
    mesh = []
    for y in range(0, H, C):
        for x in range(0, W, C):
            x1, y1 = min(W, x + C), min(H, y + C)
            quad = (src(x, y), src(x, y1), src(x1, y1), src(x1, y))      # PIL: nw, sw, se, ne
            mesh.append(((x, y, x1, y1), tuple(c for p in quad for c in p)))
    return photo.transform((W, H), Image.MESH, mesh, Image.BICUBIC)


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
                if r > 140 and r - g > 55 and r - b > 35:
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
    painting = untape(flatten(Image.open(sys.argv[1]).convert('RGB')))
    painting.save(sys.argv[2])
