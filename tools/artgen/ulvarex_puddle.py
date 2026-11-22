"""Ulvarex's puddles: the reflection she lives in (utils/ulvarexEncounter.js), one sheet per place.

A puddle reflects the sky upside down: its far edge (top) holds the horizon, its near edge the sky high up. On an
Oltrac trip hers holds a borrowed sunset instead of the grey sky: a strange horizon of round hills hanging from the far
edge, the sky running gold, rose, plum and indigo toward you, a glitter path of the sun on the ripples, and the sun is
her eye (it opens when she notices you). The reflection is not foreshortened (a mirror image), so the eye stays round.

Sites (each a sheet of 13 frames in a row; the spot = the frame's middle in the scene):
  roof     ScraperScene      the puddle painted into the rooftop (Scraper1140.png), the sunset laid exactly over it
  gate     Shed521GateScene  a new puddle on the cobbles of the yard
  skyship  SkyshipBoardScene a new puddle on the deck planks
Frames: 0-1 eye shut (ripple phases) | 2-3 opening | 4-6 open, looking at you | 7-8 looking left | 9-10 right |
        11 half shut (a blink) | 12 the plain puddle, grey sky (gate + skyship: always there, the sunset fades in over it;
        roof: empty, the background has its own)

python3 ulvarex_puddle.py <outdir> [<bg dir> <preview.png>]  ->  ulvarex_puddle_<site>.png (+ a preview on the bgs)
"""
import sys, os, math
from PIL import Image
from common import make_noise, band, INK, hx, ramp

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'

SUN = ramp('#2a1640 #4a2050 #7a2f55 #b2444c #e0703a #f5b25a #ffe6a0')   # the symbiont HUD's sunset (pal_symb SKY)
# the same sky as water gives it back: darker and duller than the sky itself, the sun and its glitter the only bright
REFL = ramp('#130a1c #1c0f28 #2a1434 #3e1a3c #5a223e #7c2e3e #a4443a #c8683a #e09a4a')
HILL = ramp('#140a1a #1f1026 #2e1834 #4a2440')                          # the borrowed horizon's hills (back-lit)
LID = ramp('#5a1e2c #8a3038 #c0583a')                                   # the eye's rim / lashes
IRIS = ramp('#3a0e18 #7a1e26 #b8402e #e07a3a')
WHITE = hx('#fff6dc')

#            canvas     puddle half-axes  horizon  sun-eye: centre row, half-width, half-height, iris r, disc r
SITES = {
    'roof':    dict(w=104, h=16, ax=50.5, ay=6.6, hz=4, ey=8.6, ea=5.6, eb=3.2, ir=2, R=4.6, look=1,
                    spot=(336, 550), bg='Scraper1140.png', halo=False, plain=None),
    'gate':    dict(w=124, h=36, ax=55, ay=12.5, hz=10, ey=17.5, ea=8.2, eb=4.6, ir=3, R=6.6, look=2,
                    spot=(588, 522), bg='Shed521_gate.png', halo=True,
                    plain=dict(sil=ramp('#101416 #171d1e #20282a'), sky=ramp('#262f31 #313b3d #3e494a #55605f'))),
    'skyship': dict(w=120, h=36, ax=52, ay=12, hz=10, ey=17.5, ea=8.2, eb=4.6, ir=3, R=6.6, look=2,
                    spot=(440, 512), bg='skyship_board.png', halo=True,
                    plain=dict(sil=ramp('#140d09 #1e150e #2b1f14'), sky=ramp('#232a2d #2e373a #3c4649 #58625f'))),
}
FRAMES = [('shut', 0, 0), ('shut', 0, 1), ('open', 0, 2, 0.3), ('open', 0, 0, 0.66),
          ('open', 0, 0), ('open', 0, 1), ('open', 0, 2), ('open', -1, 0), ('open', -1, 1), ('open', 1, 0), ('open', 1, 1),
          ('open', 0, 2, 0.4), ('plain', 0, 0)]


def shape(site, s):
    """The puddle's water as a set of pixels: an ellipse (the roof's flattened to its painted puddle) with lobes and a
    ragged rim (noise), cleaned of single-pixel spurs."""
    w, h, cx, cy = s['w'], s['h'], s['w'] / 2, s['h'] / 2
    n = make_noise(5, 31 + len(site), w + 8, h + 8)
    lobes = [(0, 0, s['ax'], s['ay'], 2.0)]
    if site == 'roof':
        lobes = [(0, 0, s['ax'], s['ay'], 3.2)]            # flat top and bottom, rounded ends like the painted one
    elif site == 'gate':
        lobes = [(-4, 0, 44, 11.5, 2.0), (-28, 3, 22, 10, 2.0), (20, -3, 24, 9.5, 2.0), (40, 3, 12, 6, 2.0)]
    else:
        lobes = [(2, 0, 40, 11, 2.0), (-22, -3, 24, 9.5, 2.0), (26, 4, 18, 8.5, 2.0), (-40, 2, 10, 5, 2.0)]
    m = set()
    for y in range(h):
        for x in range(w):
            px, py = x + 0.5 - cx, y + 0.5 - cy
            v = max(1 - (abs((px - lx) / ax) ** p + abs((py - ly) / ay) ** p) for lx, ly, ax, ay, p in lobes)
            if v + (0 if site == 'roof' else (n(x, y) - 0.5) * 0.45) > 0:
                m.add((x, y))
    for _ in range(2):
        nb = lambda x, y: sum((x + dx, y + dy) in m for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        m = {p for p in m if nb(*p) >= 2}
        m |= {(x, y) for x in range(w) for y in range(h) if (x, y) not in m and nb(x, y) >= 3}
    return m


def ripple(y, ph):
    return round(0.75 * math.sin(y * 1.9 + ph * 2.1))


def sunset(site, s, m, look, ph, o):
    """One sunset frame: {(x, y): rgb}. `o` = how far the eye is open (0 shut .. 1)."""
    w, h, hz = s['w'], s['h'], s['hz']
    ys = [y for _, y in m]
    top, bot = min(ys), max(ys)
    cx = w / 2
    hills = make_noise(9, 77, w + 8, 8)
    nC = make_noise(4, 78, w + 8, h + 8)
    px = {}
    for (x, y) in m:
        sx = x + ripple(y, ph)                            # the ripples shift the reflection, not the water's edge
        # the borrowed horizon: round hills hanging from the far edge (back-lit rims)
        hill = hz - 1 - round((hills(sx * 0.9, 1) - 0.35) * 5)
        if y < min(hill, hz):
            c = HILL[0] if y < hill - 2 else HILL[1] if y < hill - 1 else HILL[2]
            if y == hill - 1 and abs(x + 0.5 - cx) < s['ax'] * 0.5 and (sx + y) % 2 == 0: c = REFL[6]
            px[(x, y)] = c
            continue
        if y == hz or (y == hill and y < hz):
            d = abs(x + 0.5 - cx) / s['ax']
            px[(x, y)] = SUN[6] if d < 0.2 else SUN[5] if d < 0.5 else REFL[7] if d < 0.8 else REFL[6]
            continue
        # the sky going up = coming toward you: gold, orange, rose, plum, indigo
        t = (y - hz) / max(1, bot - hz)
        # brightest round the sun, falling off toward you and to the sides
        v = 7.6 - t * 6.4 - abs(x + 0.5 - cx) / s['ax'] * 2.4 + (nC(sx, y) - 0.5) * 0.5
        k = max(0, min(8, band(v, sx, y)))
        # wind ripples: short dashes of the next tone up and down, drifting with the phase
        r = (sx * 7 + y * 13 + ph * 5) % 31
        if r == 0 and (x - 1, y) in m: k = min(8, k + 1)
        elif r == 15: k = max(0, k - 1)
        c = REFL[k]
        # thin clouds across the lower sky, their sun-lit edge on the horizon's side
        cl = math.sin(sx * 0.11 + y * 2.3) + (nC(sx * 2, y * 3) - 0.5) * 1.6
        if t > 0.3 and cl > 0.95:
            c = REFL[max(0, k - 2)]
            if (x, y - 1) in m and math.sin(sx * 0.11 + (y - 1) * 2.3) + (nC(sx * 2, (y - 1) * 3) - 0.5) * 1.6 <= 0.95:
                c = REFL[min(8, k + 2)]
        # the sun's glitter path on the ripples, down toward you, every other row
        dd = y - (s['ey'] + s['R']) - 1
        if site != 'roof' and dd > 0 and (y + ph) % 2 == 0:
            half = max(0.0, 4.5 - dd * 0.3)
            gx = cx + ripple(y, ph + 1) * 2
            off = abs(x + 0.5 - gx)
            if off < half and (x * 5 + y * 3 + ph) % 4 != 0:
                c = SUN[5] if off < half * 0.35 else REFL[8] if off < half * 0.7 else REFL[7]
        px[(x, y)] = c

    # the sun: a glowing disc, the eye drawn in it (the almond reaches past the disc: its corners)
    ex, ey, R = cx, s['ey'], s['R']
    for (x, y) in m:
        d = math.hypot(x + 0.5 - ex, y + 0.5 - ey)
        if d <= R + 2.2 and d > R:
            if d < R + 0.9: px[(x, y)] = REFL[8]
            elif (x + y) % 2 == 0: px[(x, y)] = REFL[7]
        elif d <= R:
            px[(x, y)] = SUN[6] if d < R - 1.2 else SUN[5]
    a, b = s['ea'], s['eb'] * o
    for (x, y) in m:
        dx, dy = x + 0.5 - ex, y + 0.5 - ey
        if abs(dx) > a + 0.5: continue
        edge = b * (1 - (dx / a) ** 2) if abs(dx) < a else 0
        if o == 0:
            if abs(dy) < 0.5 and abs(dx) <= a - 0.5:     # shut: one lash line across the sun
                px[(x, y)] = LID[0] if abs(dx) < a - 2 else LID[1]
            continue
        if abs(dy) < edge:
            c = WHITE
            ix, ir = ex + look * s['look'], s['ir']
            di = math.hypot(x + 0.5 - ix, (y + 0.5 - ey) * 1.0)
            if di < ir + 0.4:
                c = IRIS[2] if di > ir - 0.9 else IRIS[1]
                if ir >= 3 and di < ir - 1.6 and (x + y) % 2 == 0: c = IRIS[3]
                if abs(x + 0.5 - ix) < 0.6 and abs(dy) < ir - 0.4: c = INK                  # the slit pupil
            if (x, y) == (int(ix - ir * 0.5), int(ey - b * 0.45)) and o >= 0.6: c = (255, 255, 255)
            px[(x, y)] = c
        elif abs(dy) < edge + 1.05 and abs(dx) < a:
            px[(x, y)] = LID[0] if dy < 0 else LID[1]    # the upper lid's lashes darker than the lower rim
    if site != 'roof':                                    # one brow raised: a thin bright wisp over the right of the eye
        for k in range(6):
            bx = int(ex + 2 + k)
            by = int(ey - s['eb'] - 2.6 - (1 if 1 <= k <= 3 else 0) + (1 if k == 5 else 0))
            if (bx, by) in m and by > hz: px[(bx, by)] = SUN[6] if k < 4 else SUN[5]
    return rim(px, m, light=REFL[6], dark=hx('#120818'))


def plain(site, s, m, ph=0):
    """The puddle as it is without Oltrac: dark water, the things behind it hanging from the far edge, a pale band of
    the overcast sky under them, a few glints; shallow at the rim, so the floor shows through there."""
    P = s['plain']
    w, hz = s['w'], s['hz']
    ys = [y for _, y in m]
    bot = max(ys)
    cx = w / 2
    n = make_noise(7, 91, w + 8, 48)
    px = {}
    for (x, y) in m:
        sx = x + ripple(y, ph)
        far = hz + 1 + round((n(sx * 0.6, 2) - 0.5) * 7)       # the walls / the bulwark behind, upside down
        if y < far:
            px[(x, y)] = P['sil'][0 if y < far - 3 else 1 if y < far - 1 else 2]
            continue
        t = (y - far) / max(1, bot - far)
        # the pale sky just under the silhouettes, darker toward you (the water shows less sky, more depth)
        v = 3.2 - t * 4.2 - abs(x + 0.5 - cx) / s['ax'] * 1.2 + (n(sx * 0.7, y) - 0.5) * 0.5
        k = max(0, min(3, band(v, sx, y)))
        r = (sx * 7 + y * 13) % 29
        if r == 0 and k < 3: k += 1                       # wind ripples
        px[(x, y)] = P['sky'][k]
        if (sx * 11 + y * 5) % 97 == 0 and t < 0.6: px[(x, y)] = P['sky'][3]     # glints
    return rim(px, m, light=P['sky'][3], dark=P['sil'][0], body=215)


def rim(px, m, light, dark, body=255):
    """The water's edge: the far rim catches the light, the near lip is dark, the sides are shallow (the floor shows
    through a little); returns {(x, y): rgba}."""
    out = {}
    inside = lambda x, y: (x, y) in m
    for (x, y), c in px.items():
        a = body
        if not inside(x, y - 1):
            c = light if inside(x, y + 1) and inside(x - 1, y) and inside(x + 1, y) else dark
            a = min(body, 210)
        elif not inside(x, y + 1):
            c, a = dark, min(body, 190)
        elif not inside(x - 1, y) or not inside(x + 1, y):
            c, a = tuple(int(v * 0.85) for v in c), min(body, 170)
        elif not all(inside(x + dx, y + dy) for dx, dy in ((-2, 0), (2, 0), (0, -1), (0, 1))):
            a = min(body, 225 if body == 255 else 200)
        out[(x, y)] = (*c, a)
    return out


def halo(m):
    """The wet floor around the water: a darkening two pixels wide (the plain frame carries it)."""
    near, far = set(), set()
    for (x, y) in m:
        for dx in range(-2, 3):
            for dy in range(-1, 2):
                q = (x + dx, y + dy)
                if q in m: continue
                (near if abs(dx) <= 1 and dy == 0 or (dx == 0) else far).add(q)
    return near, far - near


def build(site):
    s = SITES[site]
    w, h = s['w'], s['h']
    m = shape(site, s)
    sheet = Image.new('RGBA', (w * len(FRAMES), h), (0, 0, 0, 0))
    sp = sheet.load()
    for i, f in enumerate(FRAMES):
        kind, look, ph = f[0], f[1], f[2]
        if kind == 'plain':
            if not s['plain']: continue
            px = plain(site, s, m)
            near, far = halo(m)
            for (x, y) in near | far:
                if 0 <= x < w and 0 <= y < h: sp[i * w + x, y] = (8, 10, 12, 110 if (x, y) in near else 60)
        else:
            px = sunset(site, s, m, look, ph, 0 if kind == 'shut' else (f[3] if len(f) > 3 else 1))
        for (x, y), c in px.items():
            sp[i * w + x, y] = c
    return sheet


def preview(sheets, bgdir, path):
    """Each place: the plain puddle and the open eye on its background, 3x."""
    rows = []
    for site, sheet in sheets.items():
        s = SITES[site]
        w, h = s['w'], s['h']
        bg = Image.open(os.path.join(bgdir, s['bg'])).convert('RGBA')
        x0, y0 = s['spot'][0] - w // 2, s['spot'][1] - h // 2
        box = (x0 - 50, y0 - 40, x0 + w + 50, y0 + h + 24)
        shots = []
        for fi in (12, 0, 4, 7):
            im = bg.copy()
            if fi != 12 or s['plain']:
                if fi != 12 and s['plain']: im.alpha_composite(sheet.crop((12 * w, 0, 13 * w, h)), (x0, y0))
                im.alpha_composite(sheet.crop((fi * w, 0, (fi + 1) * w, h)), (x0, y0))
            shots.append(im.crop(box))
        row = Image.new('RGBA', (sum(c.width for c in shots) + 8 * 3, shots[0].height), (0, 0, 0, 255))
        x = 0
        for c in shots:
            row.paste(c, (x, 0)); x += c.width + 8
        rows.append(row.resize((row.width * 3, row.height * 3), Image.NEAREST))
    W = max(r.width for r in rows)
    out = Image.new('RGBA', (W, sum(r.height + 12 for r in rows)), (0, 0, 0, 255))
    y = 0
    for r in rows:
        out.paste(r, (0, y)); y += r.height + 12
    out.save(path)


if __name__ == '__main__':
    sheets = {site: build(site) for site in SITES}
    for site, sheet in sheets.items():
        sheet.save(os.path.join(OUT, f'ulvarex_puddle_{site}.png'))
        print(site, sheet.size, 'frame', SITES[site]['w'], 'x', SITES[site]['h'])
    if len(sys.argv) > 3:
        preview(sheets, sys.argv[2], sys.argv[3])
