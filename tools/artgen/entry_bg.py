"""The first view of the city (EntryScene): the old AI vista re-pixelled + a new overlook to stand on.

The plate is `city_ref.jpg` (2048x2048, painterly) resampled onto 356 logical columns (cell 5.75 px, the most common
palette colour of each cell's middle) and cut to its top 200 rows: the storm sky, the Egg Cathedral's vine-split egg
on the left, the Scraper's needle in the middle, the overgrown skyline, the dropship. The bottom of the frame is new,
drawn at the same logical size with the Scraper 1140 camera (horizon row 150, the player's feet on row 178 at depth 15):
a mossy flagstone overlook with a stone balustrade (a broken stretch, ivy, moss cushions), a signpost with a painted
egg pointing on to the Cathedral (the exit right), moss mounds and ferns in the near corners. Shown 3x.

    python3 entry_bg.py <outdir>   # -> plate.png fg.png (356x200), entry.png (1067x600 = assets/images/backgrounds/
                                   #    city.jpg's replacement EntryCity.png), chars.png, guides.png, entry.gpl
"""
import colorsys, math, os, sys
from PIL import Image, ImageDraw
from repix import family_palette, resample_mode, to_canvas, write_gpl, nearest_index
from common import h32
from scraper_bg import LW, LH, K, VX, HY, FL, EYE, proj, Layer, vnoise, mix, clamp, lum

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, 'city_ref.jpg')
ZB = 22.0                                          # the balustrade

FAMILIES = [('glow', lambda h, s, v, c: 0.2 <= h <= 0.42 and s > 0.5 and v > 0.35, 10),     # the green storm light, moss
            ('rust', lambda h, s, v, c: (h < 0.1 or h > 0.95) and s > 0.35 and v > 0.12, 10),
            ('egg', lambda h, s, v, c: v > 0.55 and s < 0.25, 6)]


class Ramps:
    """foreground colours picked from the plate's palette"""
    def __init__(s, pal):
        def near(t): return min(pal, key=lambda c: sum((c[i] - t[i]) ** 2 for i in range(3)))
        s.stone = [near(t) for t in ((14, 17, 15), (24, 29, 25), (36, 42, 36), (50, 57, 48), (66, 74, 62), (84, 92, 78), (104, 112, 96))]
        s.moss = [near(t) for t in ((18, 30, 12), (28, 48, 16), (42, 70, 22), (62, 100, 30), (92, 140, 42), (128, 176, 60))]
        s.wood = [near(t) for t in ((26, 18, 12), (40, 28, 18), (58, 40, 24), (78, 56, 34))]
        s.paint = near((196, 196, 180))

    def pick(s, r, v, x, y, seed=0):
        v += (vnoise(x, y, 1.6, 90 + seed) - 0.5) * 0.08
        return r[int(round(clamp(v) * (len(r) - 1)))]


def path(L, R, plate):
    """big wet flagstones in running bond, thin dark joints with moss in them, moss creeping in at the edges, the
    green storm light mirrored in the damp stone toward the balustrade"""
    pp = plate.load()
    for y in range(int(HY) + 1, LH):
        z = FL * EYE / (y + 0.5 - HY)
        if z > ZB: continue
        z2 = FL * EYE / (y + 1.5 - HY)
        for x in range(LW):
            if L.p[x, y][3]: continue
            wx = (x + 0.5 - VX) * z / FL
            j = math.floor(z / 1.25); off = 0.9 if j % 2 else 0.0
            i = math.floor((wx + off) / 1.3)
            i2 = math.floor(((x + 1.5 - VX) * z / FL + off) / 1.3)
            joint = i2 != i or math.floor(z2 / 1.25) != j
            edge = clamp((z - 20.2) / 1.8) + clamp((10.2 - z) / 1.8)
            moss = vnoise(wx * 0.45, z * 0.9, 1, 3) * 0.8 + edge * 0.5
            if joint:
                c = R.moss[1] if moss > 0.55 else R.stone[0]
            elif moss > 0.92:
                c = R.pick(R.moss, 0.25 + 0.3 * vnoise(wx * 3, z * 3, 1, 5), x, y, 2)
            else:
                v = 0.24 + (h32(i, j, 7) % 9 - 4) * 0.02 + (vnoise(wx * 1.5, z * 1.5, 1, 6) - 0.5) * 0.10
                u = ((wx + off) / 1.3) % 1; w = (z / 1.25) % 1
                if h32(i, j, 8) % 6 == 0 and abs(u - w) < 0.025: v -= 0.12                        # a cracked flag
                c = R.pick(R.stone, v, x, y, 3)
                ry = int(2 * HY - y + (vnoise(x * 0.5, y, 1, 21) - 0.5) * 2)                       # damp: the sky
                sheen = 0.08 + 0.42 * clamp((z - 12.5) / 9) ** 1.3
                if vnoise(wx * 0.7, z * 1.4, 1, 22) > 0.72: sheen = min(0.85, sheen + 0.35)          # puddles
                c = mix(c, mix(pp[x, ry] if 0 <= ry < LH else pp[x, 0], (0, 0, 0), 0.2), sheen)
            c = mix(c, (0, 0, 0), 0.3 * clamp(1 - (ZB - z) / 0.9))                                 # under the balustrade
            L.put(x, y, c)


def balustrade(L, R):
    """plinth, balusters, a heavy coping -- a broken stretch where the balusters are gone and the coping fell"""
    def row(h): return proj(0, h, ZB)[1]
    yp0, yp1 = row(0.7), row(0.0)
    yc0, yc1 = row(3.9), row(3.2)
    BREAK = (7.0, 12.8)
    for x in range(LW):
        wx = (x + 0.5 - VX) * ZB / FL
        broken = BREAK[0] < wx < BREAK[1]
        for y in range(int(yp0), int(yp1) + 1):                                    # plinth
            v = 0.42 if y == int(yp0) else 0.22 + (vnoise(x * 0.8, y, 1, 11) - 0.5) * 0.12
            c = R.pick(R.stone, v, x, y, 4)
            if y > yp0 + 1 and vnoise(x * 0.5, 3, 1, 14) > 0.62: c = R.moss[1 + (x + y) % 2]
            L.put(x, y, c)
        if broken:
            if abs(wx - BREAK[0]) < 0.6 or abs(wx - BREAK[1]) < 0.6:              # the broken ends
                jag = int(3 * vnoise(x * 0.9, 1, 1, 12))
                for y in range(int(yc0) + jag, int(yc1) + 1): L.put(x, y, R.pick(R.stone, 0.4, x, y, 5))
            continue
        for y in range(int(yc0), int(yc1) + 1):                                    # coping: a lit top, a dark lip
            v = 0.62 if y == int(yc0) else (0.18 if y == int(yc1) else 0.36 + (vnoise(x * 0.6, y, 1, 13) - 0.5) * 0.1)
            L.put(x, y, R.pick(R.stone, v, x, y, 5))
    bx = -40.0                                                                     # balusters: dark core, lit belly
    while bx < 40:
        if not (BREAK[0] - 0.5 < bx < BREAK[1] + 0.5) or h32(int(bx * 10), 5) % 4 == 0:
            px = int(proj(bx, 0, ZB)[0])
            standing = not (BREAK[0] - 0.5 < bx < BREAK[1] + 0.5)
            y_top = int(yc1) + 1 if standing else int(yp0) - 4
            for y in range(y_top, int(yp0)):
                t = (y - yc1) / max(1, yp0 - yc1)
                belly = 0.4 < t < 0.85
                L.put(px - 1, y, R.stone[1] if not belly else R.stone[2])
                L.put(px, y, R.stone[2] if not belly else R.stone[4])
                L.put(px + 1, y, R.stone[1] if not belly else R.stone[3])
                if belly and 0.52 < t < 0.75: L.put(px + 2, y, R.stone[1]); L.put(px - 2, y, R.stone[1])
        bx += 1.35
    for k in range(12):                                                            # rubble of the fallen coping
        rx = BREAK[0] + 0.3 + (h32(k, 21) % 52) / 10.0; rz = ZB - 0.4 - (h32(k, 22) % 30) / 10.0
        px, py = proj(rx, 0, rz)
        sz = 1 + h32(k, 23) % 3
        for dx in range(sz + 1):
            L.put(px + dx, py - 1, R.stone[4] if dx < sz else R.stone[2]); L.put(px + dx, py, R.stone[1])
            if sz > 2: L.put(px + dx, py - 2, R.stone[3])


def greenery(L, R):
    """moss cushions on the coping, ivy over the plinth and down between the balusters"""
    yc0 = proj(0, 3.9, ZB)[1]
    for x in range(LW):
        wx = (x + 0.5 - VX) * ZB / FL
        if 7.0 < wx < 12.8: continue
        m = vnoise(wx * 0.6, 2, 1, 31)
        if m > 0.58:
            hpx = int((m - 0.58) * 8)
            for k in range(hpx + 1):
                L.put(x, int(yc0) - k, R.moss[3] if k == hpx else R.moss[2])
        if vnoise(wx * 1.1, 5, 1, 32) > 0.7:
            ln = 4 + int(vnoise(wx * 3, 7, 1, 33) * 12)
            for k in range(ln):
                yy = int(yc0) + 1 + k
                if (x + k) % 4 == 0: L.put(x + 1, yy, R.moss[3])
                L.put(x, yy, R.moss[2] if k % 3 else R.moss[1])


CATHEDRAL = ['    ###    ',                                                         # 11 wide, centred on cx: the egg
             '   #####   ',                                                         # seated in its spired base
             '   #####   ',
             '  #######  ',
             '  #######  ',
             '# ####### #',
             '# ####### #',
             '## ##### ##',
             '##  ###  ##',
             '###########',
             '###########']


def signpost(L, R):
    """a crooked wooden post by the balustrade, a board painted with the Cathedral (the egg seated in its spired
    base, as on the skyline) and an arrow toward it"""
    sx, sz = 25.0, 19.5
    base, top = proj(sx, 0, sz), proj(sx, 7.0, sz)
    for y in range(int(top[1]), int(base[1]) + 1):
        lean = int((base[1] - y) * 0.05)
        L.put(base[0] + lean - 1, y, R.wood[3]); L.put(base[0] + lean, y, R.wood[2]); L.put(base[0] + lean + 1, y, R.wood[0])
    bx0, by0 = int(base[0]) - 9, int(proj(sx, 6.6, sz)[1])
    BW, BH = 24, 13
    for y in range(by0, by0 + BH):
        for x in range(bx0, bx0 + BW):
            edge = y in (by0, by0 + BH - 1) or x in (bx0, bx0 + BW - 1)
            L.put(x, y, R.wood[0] if edge else R.wood[3 if (y - by0) % 4 else 2])
    for k in range(1, 6):                                                           # the pointed end
        for y in range(by0 + k, by0 + BH - k): L.put(bx0 + BW - 1 + k, y, R.wood[2 if k < 5 else 0])
    cx = bx0 + 7                                                                    # the Cathedral, painted
    for r, row in enumerate(CATHEDRAL):
        for k, ch in enumerate(row):
            if ch == '#': L.put(cx - 5 + k, by0 + 1 + r, R.paint)
    ey = by0 + 6
    for k in range(6): L.put(cx + 7 + k, ey, R.paint)                               # the arrow
    for k in (1, 2): L.put(cx + 12 - k, ey - k, R.paint); L.put(cx + 12 - k, ey + k, R.paint)
    for k in range(5):
        L.put(base[0] - 2 + k, base[1], R.moss[2]); L.put(base[0] - 1 + k % 3, base[1] - 1, R.moss[3])


def corners(L, R):
    """dark mossy rocks and ferns in the near corners (low: they never reach the walk line)"""
    for (cx, cz, rad, seed) in ((-19.5, 9.0, 2.6, 1), (-15.8, 8.7, 1.4, 2), (19.0, 8.9, 2.2, 3), (23.6, 9.4, 1.8, 4)):
        for y in range(int(HY) + 1, LH):
            for x in range(LW):
                z = FL * EYE / (y + 0.5 - HY); wx = (x + 0.5 - VX) * z / FL
                d = math.hypot((wx - cx) / rad, (z - cz) / (rad * 0.5))
                hgt = 1.1 * max(0.0, 1 - d * d)
                if hgt <= 0: continue
                yy = int(proj(wx, hgt, z)[1])
                for k in range(yy, y + 1):
                    if 0 <= k < LH:
                        v = 0.2 + 0.3 * (1 - d) + (vnoise(wx * 3, z * 3, 1, seed) - 0.5) * 0.25
                        rock = vnoise(wx * 1.5, z * 1.5, 1, seed + 5) > 0.62
                        c = R.pick(R.stone, v * 0.9, x, k, seed) if rock else R.pick(R.moss, v, x, k, seed)
                        if k == yy and not rock: c = R.moss[3]
                        L.put(x, k, c)
        for f in range(7):                                                          # ferns: arched fronds
            a = (f / 6 - 0.5) * 2.2
            p0 = proj(cx, 0.9, cz)
            ln = 8 + h32(f, seed) % 6
            dirx = math.sin(a)
            for t in range(ln):
                px = p0[0] + dirx * t * 1.2; py = p0[1] - t * 0.8 * math.cos(a) + (t * t) * 0.07
                L.put(px, py, R.moss[2])
                if t % 2 == 0 and t > 1: L.put(px + 1, py + 1, R.moss[3]); L.put(px - 1, py + 1, R.moss[1])


def overlays():
    ch = Image.open(os.path.join(HERE, 'chars.png')).convert('RGBA').resize((LW, LH), Image.NEAREST)
    g = Image.new('RGBA', (LW, LH), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    kx = 1067 / 800
    d.rectangle([(780 * kx - 20 * kx) / K, 370 / K, (780 * kx + 20 * kx) / K - 1, 570 / K - 1], outline=(255, 200, 80, 255))
    d.rectangle([(600 - 40) / K, (530 - 128) / K, (600 + 40) / K, 530 / K], outline=(127, 255, 142, 255))   # Master Thaal
    d.line([(0, 178), (LW, 178)], fill=(255, 80, 80, 255))
    return ch, g


def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    src = Image.open(REF).convert('RGB')
    pal = family_palette(src, FAMILIES, 36, step=3)
    plate = resample_mode(src, pal).crop((0, 0, LW, LH))
    R = Ramps(pal)
    fg = Layer()
    balustrade(fg, R)
    greenery(fg, R)
    path(fg, R, plate)
    signpost(fg, R)
    corners(fg, R)
    idx = nearest_index(pal)
    q = fg.im.copy(); qp = q.load()
    for y in range(LH):
        for x in range(LW):
            c = qp[x, y]
            if c[3]: qp[x, y] = pal[idx(c[:3])] + (255,)
    comp = plate.convert('RGBA'); comp.alpha_composite(q)
    plate.save(os.path.join(out, 'plate.png')); q.save(os.path.join(out, 'fg.png'))
    comp.convert('RGB').save(os.path.join(out, 'entry_356.png'))
    to_canvas(comp.convert('RGB')).save(os.path.join(out, 'entry.png'))
    ch, g = overlays(); ch.save(os.path.join(out, 'chars.png')); g.save(os.path.join(out, 'guides.png'))
    write_gpl(os.path.join(out, 'entry.gpl'), 'entry-city', pal)
    print('palette', len(pal))


if __name__ == '__main__':
    main()
