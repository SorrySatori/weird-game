"""The skyship over the Crossroad (CrossroadScene's look-up cut, the image shown full-screen as the camera tilts up):
the old AI picture kept, re-pixelled and widened to 16:9.

`skyship_ref.png` (1024x1536, portrait) is resampled onto 190 logical columns (cell 5.39 px, the most common palette
colour of each cell's middle) and rows 22..222 are kept: the moss-netted gas bladder with its glowing spores and fins,
the gondola with its lanterns, the hooded captain and the warm cabin windows, the mycelium tree from the corpse with
its glowing bulbs holding the ship. It sits in the middle of a 356x200 frame; the 83 columns on either side are new
sky that carries on the source's own sky row by row (its colour, its cloud banks lower down). The stars are gone
(the game's scenes are overcast days). Shown 3x.

    python3 skyship_bg.py <outdir>   # -> skyship_356.png, skyship.png (1067x600 = assets/images/backgrounds/skyship.png),
                                     #    skyship.gpl
"""
import math, os, sys
from statistics import median
from PIL import Image
from repix import family_palette, resample_mode, to_canvas, write_gpl, nearest_index, lum
from scraper_bg import vnoise, mix, clamp

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, 'skyship_ref.png')
LW, LH, COLS, R0 = 356, 200, 190, 22
X0 = (LW - COLS) // 2

FAMILIES = [('glow', lambda h, s, v, c: 0.16 <= h <= 0.36 and s > 0.45 and v > 0.45, 8),
            ('warm', lambda h, s, v, c: 0.04 <= h <= 0.15 and s > 0.4 and v > 0.3, 5)]


def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    src = Image.open(REF).convert('RGB')
    pal = family_palette(src, FAMILIES, 40, step=3)
    ship = resample_mode(src, pal, cols=COLS).crop((0, R0, COLS, R0 + LH))
    sp = ship.load()
    img = Image.new('RGB', (LW, LH)); p = img.load()
    for y in range(LH):
        for x in range(COLS): p[X0 + x, y] = sp[x, y]
    # the new sky either side: carries on the source's edge -- its colour (smoothed down the rows) and its texture
    for side in (-1, 1):
        cols = range(0, 8) if side < 0 else range(COLS - 8, COLS)
        rows = []
        for y in range(LH):
            px_ = [sp[x, yy] for x in cols for yy in range(max(0, y - 9), min(LH, y + 10))]
            base = tuple(sum(c[i] for c in px_) / len(px_) for i in range(3))
            spread = max(5.0, (sum((lum(c) - lum(base)) ** 2 for c in px_) / len(px_)) ** 0.5)
            rows.append((base, spread))
        for y in range(LH):
            base, spread = rows[y]
            for k in range(X0):
                x = X0 - 1 - k if side < 0 else X0 + COLS + k
                lower = clamp((y - 90) / 70.0)
                n = (vnoise(x * 0.045, y * 0.07, 1, 5) - 0.5) * 1.3 + (vnoise(x * 0.12, y * 0.18, 1, 6) - 0.5) * 0.5
                puff = vnoise(x * 0.035, y * 0.06, 1, 7)
                if lower > 0 and puff > 0.52:                                     # dark cloud masses lower down, lit rims
                    n -= lower * 1.6 * min(1.0, (puff - 0.52) * 6)
                    if puff < 0.56: n += lower * 0.9
                c = tuple(clamp(base[i] + n * spread * 1.1, 0, 255) for i in range(3))
                if k < 10:                                                        # blend into the source edge
                    e = sp[0 if side < 0 else COLS - 1, y]
                    t = (k + 1) / 11.0
                    if (x + y) % 2 == 0: t = min(1.0, t + 0.1)
                    c = mix(e, c, t)
                p[x, y] = tuple(int(v) for v in c)
    # the stars: lone bright pixels in the sky -> their neighbours
    lm = [[lum(p[x, y]) for x in range(LW)] for y in range(LH)]
    for y in range(1, LH - 1):
        for x in range(1, LW - 1):
            nb = [lm[y + dy][x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dx or dy]
            if lm[y][x] - median(nb) > 14 and lm[y][x] < 150 and sum(1 for v in nb if v > lm[y][x] - 8) <= 1:
                cs = sorted((p[x + dx, y + dy] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dx or dy), key=lum)
                p[x, y] = cs[3]
    idx = nearest_index(pal)
    for y in range(LH):
        for x in range(LW): p[x, y] = pal[idx(p[x, y])]
    img.save(os.path.join(out, 'skyship_356.png'))
    to_canvas(img).save(os.path.join(out, 'skyship.png'))
    write_gpl(os.path.join(out, 'skyship.gpl'), 'skyship', pal)
    print('palette', len(pal))


if __name__ == '__main__':
    main()
