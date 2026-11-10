"""The hand-drawn fast-travel map (assets/images/ui/map.png, 1067x600, shown 1:1 by ui/MapUI.js).

The user's own marker sketch (ref/map_sketch.jpg: Shed 521, the Crossroads walker, the skyship, the Voxmarket
hangars, Scraper 1140, the Egg Cathedral, the bus street) is cleaned into ink on paper and kept as it is; the
places it doesn't show yet (the town, the harbour coast) and a town of little houses are drawn round it in the
same marker style: one wobbly ~3.4 px felt-tip line, boxes from separate strokes that overshoot at the corners,
windows as small squares with a dot, no fills or hatching. Everything is drawn 3x and scaled down.
Every house is different (seeded generator); houses are drawn back to front and blank out what they hide.

    python3 handmap.py <outdir> [--debug]   ->  map.png, layers/{papir,skica,dokresleno}.png (+ map_debug.png)
The node coordinates here (NODES) are the ones in MapUI.js `locations` (+ 533.5 / + 300): keep them in sync."""
import sys, os, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageMath, ImageChops

S = 3                                   # supersampling
FW, FH = 1067, 600
W, H = FW * S, FH * S
HERE = os.path.dirname(os.path.abspath(__file__))
SKETCH = os.path.join(HERE, 'ref', 'map_sketch.jpg')
args = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = args[0] if args else '.'
DEBUG = '--debug' in sys.argv

INK = (30, 27, 28)
LW = 3.3                                # marker width in final px (the sketch's lines at its map scale)
FINE = 2.1                              # the same pen pressed lightly, for small details
# the sketch sits at final = SK_X + (orig - SK_O) * SK_S
SK_S, SK_X, SK_Y, SK_OX, SK_OY = 0.30, 20, 34, 80, 370

rnd = random.Random(1140)
_xf = None                               # a temporary transform (a house drawn askew)

# the felt-tip colouring (--color): areas recorded while drawing, filled later with marker strokes. Recording never
# touches `rnd`, so the line drawing stays identical with or without colour.
FILLS = []

def fpoly(pts, color, alpha=0.55, win=False, ang=None, door=False, holes=()):
    if _xf: pts = [_xf(x, y) for x, y in pts]
    FILLS.append({'poly': list(pts), 'color': color, 'alpha': alpha, 'win': win, 'ang': ang, 'door': door, 'holes': list(holes)})

def fline(pts, w, color, alpha=0.45, ang=None):
    if _xf: pts = [_xf(x, y) for x, y in pts]
    FILLS.append({'line': list(pts), 'w': w, 'color': color, 'alpha': alpha, 'win': False, 'ang': ang, 'door': False})

def fseed(x, y, color, alpha=0.45, ang=None, dil=3):
    FILLS.append({'seed': (x, y), 'dil': dil, 'color': color, 'alpha': alpha, 'win': False, 'ang': ang, 'door': False})

def ellpts(cx, cy, rx, ry, a0=0, a1=360, n=24):
    return [(cx + math.cos(math.radians(a0 + (a1 - a0) * i / n)) * rx, cy + math.sin(math.radians(a0 + (a1 - a0) * i / n)) * ry) for i in range(n + 1)]
ink = Image.new('L', (W, H), 0)
dr = ImageDraw.Draw(ink)


# ------------------------------------------------------------------ the pen
def _stamp(x, y, r):
    dr.ellipse((x - r, y - r, x + r, y + r), fill=255)

def _resample(pts, step):
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(d / step))
        for i in range(1, n + 1):
            out.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
    return out

def _catmull(pts, n=10):
    if len(pts) < 3: return pts
    p = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(p) - 2):
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p[i][j]) + (-p[i - 1][j] + p[i + 1][j]) * t +
                                    (2 * p[i - 1][j] - 5 * p[i][j] + 4 * p[i + 1][j] - p[i + 2][j]) * t2 +
                                    (-p[i - 1][j] + 3 * p[i][j] - 3 * p[i + 1][j] + p[i + 2][j]) * t3) for j in (0, 1)))
    out.append(pts[-1])
    return out

def stroke(pts, lw=LW, wob=1.0, smooth=False, dry=False):
    """one pen stroke through pts (final px): a slow wobble + a slight bow, the width breathing a little"""
    if smooth: pts = _catmull(pts)
    if _xf: pts = [_xf(x, y) for x, y in pts]
    pts = [(x * S, y * S) for x, y in pts]
    pts = _resample(pts, 1.2)
    if len(pts) < 2:
        _stamp(pts[0][0], pts[0][1], lw * S / 2); return
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    L = sum(seg)
    amp = wob * min(1.5, 0.25 + L / S * 0.007) * S
    comps = [(amp * a, rnd.uniform(0, 6.283), f / S) for a, f in ((0.55, 1 / 70), (0.3, 1 / 26), (0.15, 1 / 9))]
    bow = rnd.uniform(-1, 1) * min(L * 0.01, 2.0 * S) * wob
    wph = rnd.uniform(0, 6.283)
    r0 = lw * S / 2
    s = 0.0
    tails = []
    for i, (x, y) in enumerate(pts):
        if i: s += seg[i - 1]
        a, b = (pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)])
        tx, ty = b[0] - a[0], b[1] - a[1]; tl = math.hypot(tx, ty) or 1
        nx, ny = -ty / tl, tx / tl
        t = s / L if L else 0
        off = bow * math.sin(math.pi * t) + sum(c * math.sin(6.283 * f * s + ph) for c, ph, f in comps)
        r = r0 * (1 + 0.07 * math.sin(s / S / 11 + wph))
        if t < 0.02 or t > 0.98: r *= 1.06                      # the ink pools where the pen lands and lifts
        px, py = x + nx * off, y + ny * off
        if dry and L > 70 * S and t > 0.78:                      # a fast stroke runs dry: it ends in streaks
            tails.append((px, py, nx, ny, r, t))
        else:
            _stamp(px, py, r)
    if tails:
        for k, f in enumerate((-0.62, 0.0, 0.62)):
            end = rnd.uniform(0.86, 1.0)
            for px, py, nx, ny, r, t in tails:
                if t < end and rnd.random() > 0.08: _stamp(px + nx * f * r, py + ny * f * r, r * 0.4)

def seg(a, b, ov=1.0, **k):
    """a straight line that over- or undershoots its end points a little, like a box corner drawn fast"""
    (x0, y0), (x1, y1) = a, b
    d = math.hypot(x1 - x0, y1 - y0) or 1
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    e0, e1 = rnd.uniform(-0.6, 2.2) * ov, rnd.uniform(-0.6, 2.2) * ov
    stroke([(x0 - ux * e0, y0 - uy * e0), (x1 + ux * e1, y1 + uy * e1)], **k)

def poly(pts, closed=True, **k):
    pp = list(pts) + ([pts[0]] if closed else [])
    for a, b in zip(pp, pp[1:]): seg(a, b, **k)

def box(x0, y0, x1, y1, **k):
    poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], **k)

def ell(cx, cy, rx, ry, a0=0.0, a1=360.0, closed=None, **k):
    """an ellipse (or an arc, degrees, 0 = right, 90 = down) drawn in one go; a full one overshoots its start"""
    full = closed if closed is not None else (a1 - a0 >= 359)
    if full:
        st = rnd.uniform(0, 360); a0, a1 = st, st + 360 + rnd.uniform(8, 22)
    n = max(8, int(abs(a1 - a0) / 6))
    jit = [rnd.uniform(-0.04, 0.04) for _ in range(4)]
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        f = 1 + jit[0] * math.sin(a * 2 + jit[1] * 50) + jit[2] * math.sin(a * 3 + jit[3] * 50)
        pts.append((cx + math.cos(a) * rx * f, cy + math.sin(a) * ry * f))
    stroke(pts, wob=0.5, **k)

def dot(x, y, r=1.6):
    if _xf: x, y = _xf(x, y)
    x, y = x * S, y * S
    for _ in range(3):
        rr = r * S * rnd.uniform(0.8, 1.05)
        _stamp(x + rnd.uniform(-0.4, 0.4) * S, y + rnd.uniform(-0.4, 0.4) * S, rr)

def curve(pts, **k): stroke(pts, smooth=True, **k)

def erase(pts):
    if _xf: pts = [_xf(x, y) for x, y in pts]
    dr.polygon([(x * S, y * S) for x, y in pts], fill=0)

def road(pts, w=7.0, **k):
    """the sketch's roads: two pen lines either side of a centre line"""
    pp = _catmull(pts, 6) if len(pts) > 2 else pts
    fline(pp, w - 1.5, 'gray', 0.4)
    for side in (-1, 1):
        o = []
        for i, (x, y) in enumerate(pp):
            a, b = pp[max(0, i - 1)], pp[min(len(pp) - 1, i + 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]; tl = math.hypot(tx, ty) or 1
            o.append((x - ty / tl * w / 2 * side, y + tx / tl * w / 2 * side))
        stroke(o, **k)


# ------------------------------------------------------------------ windows, doors, little things
def window(x, y, w, h, kind='sq'):
    """x, y = centre"""
    if kind == 'dash':                                    # the sketch's narrow-house windows: a short upright stroke
        stroke([(x, y - h / 2), (x + rnd.uniform(-0.4, 0.4), y + h / 2)], lw=FINE + 0.3); return
    if kind == 'dots':
        dot(x - w * 0.22, y - h * 0.15, 1.1); dot(x + w * 0.2, y + h * 0.2, 1.1); return
    if kind == 'round':
        ell(x, y, w / 2, h / 2, lw=FINE); return
    if kind == 'arch':
        stroke([(x - w / 2, y + h / 2), (x - w / 2, y - h / 2 + w / 2)], lw=FINE)
        ell(x, y - h / 2 + w / 2, w / 2, w / 2, 180, 360, closed=False, lw=FINE)
        stroke([(x + w / 2, y - h / 2 + w / 2), (x + w / 2, y + h / 2)], lw=FINE)
        seg((x - w / 2, y + h / 2), (x + w / 2, y + h / 2), lw=FINE); return
    box(x - w / 2, y - h / 2, x + w / 2, y + h / 2, lw=FINE, ov=0.6)
    if kind == 'sqdot': dot(x + rnd.uniform(-w, w) * 0.12, y + rnd.uniform(-h, h) * 0.12, 1.0)
    elif kind == 'cross':
        stroke([(x, y - h / 2), (x, y + h / 2)], lw=FINE * 0.8); stroke([(x - w / 2, y), (x + w / 2, y)], lw=FINE * 0.8)
    elif kind == 'half': stroke([(x - w / 2, y), (x + w / 2, y)], lw=FINE * 0.8)

def door(x, yb, w, h, arched=True):
    """x = centre, yb = sill"""
    fpoly([(x - w / 2, yb), (x - w / 2, yb - h + w / 2)] + ellpts(x, yb - h + w / 2, w / 2, w / 2, 180, 360, 8)[1:-1] + [(x + w / 2, yb - h + w / 2), (x + w / 2, yb)]
          if arched else [(x - w / 2, yb), (x - w / 2, yb - h), (x + w / 2, yb - h), (x + w / 2, yb)], 'brown', 0.8, door=True)
    if arched:
        stroke([(x - w / 2, yb), (x - w / 2, yb - h + w / 2)], lw=FINE + 0.2)
        ell(x, yb - h + w / 2, w / 2, w / 2, 180, 360, closed=False, lw=FINE + 0.2)
        stroke([(x + w / 2, yb - h + w / 2), (x + w / 2, yb)], lw=FINE + 0.2)
    else:
        poly([(x - w / 2, yb), (x - w / 2, yb - h), (x + w / 2, yb - h), (x + w / 2, yb)], closed=False, lw=FINE + 0.2)
    dot(x + w * 0.22, yb - h * 0.42, 0.9)

def smoke(x, y, n=3):
    pts = [(x, y)]
    for i in range(1, n * 4):
        pts.append((x + math.sin(i * 1.3) * (2 + i * 0.7) + i * 1.2, y - i * 3.2))
    stroke(pts, lw=FINE * 0.9, smooth=True, wob=0.4)

def tree(x, yb, h):
    """a scribbled round crown on a trunk"""
    stroke([(x, yb), (x + rnd.uniform(-1, 1), yb - h * 0.45)], lw=FINE + 0.4)
    cx, cy, r = x, yb - h * 0.65, h * 0.36
    fpoly(ellpts(cx, cy, r * 0.95, r * 0.85), 'green', 0.7)
    pts = []
    a0 = rnd.uniform(0, 6.28)
    for i in range(int(rnd.uniform(26, 34))):
        a = a0 + i * 0.36
        rr = r * (0.75 + 0.3 * math.sin(i * 1.7)) * (1 - i * 0.012)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.85))
    stroke(pts, lw=FINE, smooth=True, wob=0.3)
    return [(cx - r, cy - r), (cx + r, cy - r), (cx + r, yb), (cx - r, yb)]

def lamp(x, yb, h=22):
    fpoly([(x - 2.6, yb - h - 6), (x + 2.6, yb - h - 6), (x + 2.6, yb - h), (x - 2.6, yb - h)], 'yellow', 0.85)
    stroke([(x, yb), (x, yb - h)], lw=FINE)
    box(x - 2.6, yb - h - 6, x + 2.6, yb - h, lw=FINE * 0.85, ov=0.3)
    stroke([(x - 3.4, yb - h - 6.5), (x, yb - h - 9), (x + 3.4, yb - h - 6.5)], lw=FINE * 0.85)

def waves(x, y, w=9):
    stroke([(x, y), (x + w * 0.25, y - 1.6), (x + w * 0.5, y), (x + w * 0.75, y - 1.6), (x + w, y)], lw=FINE * 0.9, smooth=True, wob=0.2)


# ------------------------------------------------------------------ houses: every one different
WKINDS = ['sq', 'sqdot', 'sqdot', 'cross', 'arch', 'half', 'dash', 'dots', 'round']

def house(x, yb, w, h, kind, r, wk=None, door_at=None, tilt=None):
    """x = left, yb = ground. Drawn a little askew like the sketch's houses (rotation + shear about the foot)."""
    global _xf
    ang = math.radians(tilt if tilt is not None else r.uniform(-2.2, 2.2))
    sh = r.uniform(-0.05, 0.05)
    ox, oy = x + w / 2, yb
    def xf(px_, py_):
        px_ += sh * (oy - py_)
        dx_, dy_ = px_ - ox, py_ - oy
        return ox + dx_ * math.cos(ang) - dy_ * math.sin(ang), oy + dx_ * math.sin(ang) + dy_ * math.cos(ang)
    _xf = xf
    try:
        return _house(x, yb, w, h, kind, r, wk, door_at)
    finally:
        _xf = None

def _house(x, yb, w, h, kind, r, wk, door_at):
    wk = wk or r.choice(WKINDS)
    top = yb - h
    sil = [(x, yb), (x, top), (x + w, top), (x + w, yb)]
    roof, extra = None, None
    if kind == 'gable':
        rh = w * r.uniform(0.38, 0.65); ax = x + w * r.uniform(0.4, 0.6)
        roof = [(x - 2, top), (ax, top - rh), (x + w + 2, top)]
    elif kind == 'shed':
        rh = w * r.uniform(0.25, 0.45)
        roof = [(x - 2, top), (x + w + 2, top - rh)] if r.random() < 0.5 else [(x - 2, top - rh), (x + w + 2, top)]
    elif kind == 'stepped':
        st = r.choice((2, 3)); sw = w / (2 * st + 1); stp = r.uniform(4, 6)
        roof = [(x, top)]
        for i in range(st): roof += [(x + sw * i, top - stp * (i + 1)), (x + sw * (i + 1), top - stp * (i + 1))]
        for i in range(st - 1, -1, -1): roof += [(x + w - sw * (i + 1), top - stp * (i + 1)), (x + w - sw * i, top - stp * (i + 1))]
        roof += [(x + w, top)]
    elif kind in ('dome', 'arch'):
        dh = w * (r.uniform(0.35, 0.5) if kind == 'dome' else r.uniform(0.25, 0.38))
        roof = [(x + w / 2 + math.cos(math.radians(a)) * w / 2, top - math.sin(math.radians(a)) * dh) for a in range(180, -1, -15)]
    elif kind == 'cone':
        rh = w * r.uniform(0.9, 1.4)
        roof = [(x - 1.5, top), (x + w / 2, top - rh), (x + w + 1.5, top)]
    elif kind == 'twin':
        rh = w * r.uniform(0.22, 0.34)
        roof = [(x - 2, top), (x + w * 0.25, top - rh), (x + w * 0.5, top), (x + w * 0.75, top - rh), (x + w + 2, top)]
    elif kind == 'box3d':
        dx, dy = r.uniform(5, 10), r.uniform(4, 7)
        roof = [(x, top), (x + dx, top - dy), (x + w + dx, top - dy), (x + w, top)]
        extra = [(x + w + dx, top - dy), (x + w + dx, yb - dy), (x + w, yb)]
    elif kind == 'flat':
        roof = [(x - 2, top), (x + w + 2, top)]
        if r.random() < 0.5: extra = 'tank' if r.random() < 0.5 else 'mast'
    sil = [(x, yb)] + (roof if roof else [(x, top), (x + w, top)]) + ([extra[0], extra[1]] if kind == 'box3d' else []) + [(x + w, yb)]
    if kind in ('dome', 'arch', 'stepped', 'cone'): sil = [(x, yb), (x, top)] + roof + [(x + w, top), (x + w, yb)]
    erase(sil)
    # colours (own RNG keyed by the spot, so the drawing's randomness is untouched)
    rc = random.Random(int(x * 7919 + yb * 104729))
    wall = rc.choice(('yellow', 'orange', 'blue', 'violet', 'gray', 'red', 'green', 'yellow', 'orange'))
    rcol = rc.choice([c for c in ('red', 'brown', 'blue', 'gray', 'violet', 'orange', 'red', 'brown') if c != wall])
    fpoly([(x, yb), (x, top), (x + w, top), (x + w, yb)], wall, rc.uniform(0.42, 0.55), win=True)
    if kind == 'shed': fpoly([roof[0], roof[1], (x + w, top), (x, top)], rcol, 0.8)
    elif kind == 'box3d':
        fpoly(roof, rcol, 0.8); fpoly([(x + w, top), extra[0], extra[1], extra[2]], wall, 0.75, win=True)
    elif kind in ('gable', 'cone', 'twin', 'stepped', 'dome', 'arch'): fpoly(roof, rcol, 0.8)
    # walls, ground, roof
    seg((x, yb), (x, top)); seg((x + w, yb), (x + w, top))
    seg((x - 1, yb), (x + w + 1, yb), ov=1.6)
    if kind in ('dome', 'arch'):
        stroke(roof, wob=0.4)
        seg((x, top), (x + w, top), ov=0.4)
        if kind == 'dome':
            stroke([(x + w / 2, roof[6][1]), (x + w / 2, roof[6][1] - 6)], lw=FINE); dot(x + w / 2, roof[6][1] - 7, 1.2)
        else:
            ell(x + w / 2, top, w / 2 * 0.5, (top - roof[6][1]) * 0.5, 200, 340, closed=False, lw=FINE * 0.8)
    elif kind == 'shed':
        seg(*roof); seg((x - 2, top), (x + w + 2, top), ov=0.3) if r.random() < 0.5 else None
        if roof[0][1] < top - 1: seg((x, top), roof[0])
        if roof[1][1] < top - 1: seg((x + w, top), roof[1])
    elif roof:
        poly(roof, closed=False)
        if kind in ('gable', 'cone', 'twin'): seg((x - 2, top), (x + w + 2, top), ov=0.5)
    if kind == 'box3d':
        seg(extra[0], extra[1]); seg(extra[1], extra[2])
    if extra == 'tank':
        tx_ = x + w * r.uniform(0.25, 0.55)
        fpoly([(tx_, top - 12), (tx_ + 8, top - 12), (tx_ + 8, top - 6), (tx_, top - 6)], 'gray', 0.7)
        box(tx_, top - 12, tx_ + 8, top - 6, lw=FINE, ov=0.4)
        stroke([(tx_ + 1, top - 6), (tx_ + 0.5, top)], lw=FINE * 0.8); stroke([(tx_ + 7, top - 6), (tx_ + 7.5, top)], lw=FINE * 0.8)
    elif extra == 'mast':
        mx_ = x + w * r.uniform(0.3, 0.7)
        stroke([(mx_, top), (mx_, top - 12)], lw=FINE * 0.8); stroke([(mx_ - 4, top - 9), (mx_ + 4, top - 9)], lw=FINE * 0.7)
    # a chimney now and then, rarely smoking
    if kind in ('gable', 'twin', 'shed', 'stepped', 'flat') and r.random() < 0.4:
        cx = x + w * r.choice((0.25, 0.72)); cy = top - (w * 0.15 if kind == 'gable' else 2)
        fpoly([(cx - 2, cy + 2), (cx - 2, cy - 7), (cx + 2.5, cy - 7), (cx + 2.5, cy + 1)], 'red', 0.75)
        poly([(cx - 2, cy + 2), (cx - 2, cy - 7), (cx + 2.5, cy - 7), (cx + 2.5, cy + 1)], closed=False, lw=FINE + 0.2)
        if r.random() < 0.3: smoke(cx + 0.5, cy - 10, 2)
    # windows: few and not always in a grid, like the sketch's houses
    ws = r.uniform(5.5, 7.5); wh = ws * (r.uniform(1.1, 1.6) if wk in ('arch', 'dash') else r.uniform(0.85, 1.15))
    has_door = h > 16 and r.random() < 0.75
    dx_ = x + w * (r.uniform(0.25, 0.75) if door_at is None else (door_at + 0.5) / max(1, int(w / 12)))
    dw, dh_ = min(8, w * 0.3), min(13, h * 0.4)
    spots = []
    pat = r.choice(('grid', 'scatter', 'scatter', 'column', 'single')) if h > 22 else 'scatter'
    if pat == 'grid':
        cols = max(1, min(3, int((w - 4) / 10))); rows = max(1, min(3, int((h - (dh_ if has_door else 0) - 6) / 12)))
        for rr in range(rows):
            for c in range(cols):
                spots.append((x + w * (c + 0.5) / cols, top + 6 + rr * 12 + wh / 2))
    elif pat == 'column':
        cx = x + w * r.uniform(0.3, 0.7)
        for rr in range(max(1, int((h - (dh_ if has_door else 0) - 6) / 12))): spots.append((cx, top + 6 + rr * 12 + wh / 2))
    elif pat == 'single':
        wk = r.choice(('round', 'arch', 'cross')); ws, wh = ws * 1.3, wh * 1.3
        spots.append((x + w * r.uniform(0.35, 0.65), top + h * 0.35))
    else:
        for _ in range(r.randint(1, 3 if w < 22 else 4)):
            spots.append((x + r.uniform(ws * 0.8, w - ws * 0.8), top + r.uniform(wh * 0.8 + 2, max(wh * 0.8 + 3, h - (dh_ + 4 if has_door else wh)))))
    placed = []
    for (sx_, sy_) in spots:
        if any(abs(sx_ - a) < ws + 2.5 and abs(sy_ - b) < wh + 2.5 for a, b in placed): continue
        if has_door and abs(sx_ - dx_) < (ws + dw) / 2 + 2 and sy_ > yb - dh_ - wh / 2 - 3: continue
        if r.random() < 0.06: continue
        placed.append((sx_, sy_)); window(sx_, sy_, ws, wh, wk)
    if has_door:
        door(dx_, yb, dw, dh_, arched=r.random() < 0.55)
    return [_xf(*p) if _xf else p for p in sil]

def row(x0, x1, yb, r, kinds=None, hmin=26, hmax=48, wmin=16, wmax=34, gap=(1, 6), skip=None):
    """a street of houses from x0 to x1 standing on yb"""
    x = x0 + r.uniform(0, 3)
    kinds = kinds or ['gable', 'gable', 'shed', 'stepped', 'dome', 'arch', 'cone', 'twin', 'box3d', 'box3d', 'flat', 'flat']
    last = None
    while True:
        k = r.choice([k for k in kinds if k != last]); last = k
        w = r.uniform(wmin, wmax) * (0.7 if k == 'cone' else 1)
        room = x1 - x - (9 if k == 'box3d' else 0)
        if room < wmin * 0.8: break
        w = min(w, room)
        h = r.uniform(hmin, hmax) * (1.2 if k == 'flat' else 1)
        house(x, yb + r.uniform(-1.5, 1.5), w, h, k, r)
        x += w + r.uniform(*gap) + (9 if k == 'box3d' else 0) + (2 if k in ('gable', 'twin', 'shed') else 0)


# ------------------------------------------------------------------ the sketch, cleaned
def sketch_alpha():
    im = Image.open(SKETCH).convert('L')
    w0, h0 = im.size
    small = im.resize((w0 // 8, h0 // 8), Image.BILINEAR)
    bg = small.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(6)).resize((w0, h0), Image.BILINEAR)
    norm = ImageMath.lambda_eval(lambda a: a['convert'](a['min'](a['a'] * 255 / a['b'], 255), 'L'), a=im, b=bg)
    alpha = norm.point(lambda v: max(0, min(255, int((212 - v) * 255 / (212 - 118)))))
    ImageDraw.Draw(alpha).rectangle((0, 0, w0, 60), fill=0)          # the table edge in the photo
    ImageDraw.Draw(alpha).rectangle((0, 0, 40, h0), fill=0)          # the shadow along the left edge
    k = SK_S * S
    big = alpha.resize((int(w0 * k), int(h0 * k)), Image.LANCZOS)
    out = Image.new('L', (W, H), 0)
    out.paste(big, (int(round((SK_X - SK_OX * SK_S) * S)), int(round((SK_Y - SK_OY * SK_S) * S))))
    return out

def sk(ox, oy):
    """a point of the sketch photo in final map px"""
    return SK_X + (ox - SK_OX) * SK_S, SK_Y + (oy - SK_OY) * SK_S


# ------------------------------------------------------------------ paper
def paper():
    r = random.Random(7)
    base = (236, 230, 214)
    def noise(cw, ch, blur, amp):
        n = Image.new('L', (cw, ch)); n.putdata([r.randint(0, 255) for _ in range(cw * ch)])
        return n.resize((FW, FH), Image.BICUBIC).filter(ImageFilter.GaussianBlur(blur)), amp
    lo, a1 = noise(FW // 40 + 2, FH // 40 + 2, 6, 7)
    mid, a2 = noise(FW // 8 + 2, FH // 8 + 2, 1.5, 5)
    fine = Image.new('L', (FW, FH)); fine.putdata([r.randint(0, 255) for _ in range(FW * FH)])
    lp, mp, fp = lo.load(), mid.load(), fine.load()
    img = Image.new('RGB', (FW, FH)); px = img.load()
    for y in range(FH):
        for x in range(FW):
            dx, dy = (x - FW / 2) / (FW / 2), (y - FH / 2) / (FH / 2)
            vig = max(0.0, (dx * dx * 0.8 + dy * dy) - 0.45) * 26
            fold = 0
            if abs(x - FW // 2) <= 1: fold += (-7 if x == FW // 2 else 3)
            if abs(y - FH // 2) <= 1: fold += (-6 if y == FH // 2 else 3)
            v = (lp[x, y] - 128) / 128 * a1 + (mp[x, y] - 128) / 128 * a2 + (fp[x, y] - 128) / 128 * 2.5 - vig + fold
            px[x, y] = (int(base[0] + v), int(base[1] + v * 1.02), int(base[2] + v * 1.1))
    d = ImageDraw.Draw(img)
    for _ in range(260):                                              # paper fibres
        x, y = r.uniform(0, FW), r.uniform(0, FH); a = r.uniform(0, 6.28); l = r.uniform(3, 9)
        c = r.choice((-9, -6, 6))
        p = img.getpixel((int(x), int(y)))
        d.line((x, y, x + math.cos(a) * l, y + math.sin(a) * l + r.uniform(-1.5, 1.5)), fill=tuple(max(0, min(255, q + c)) for q in p), width=1)
    return img


# ================================================================== the map
NODES = {}                                                            # final px; MapUI = these - (533.5, 300)

def draw():
    r = random.Random(521)

    # ---- the sketch's own places (only their nodes; the drawing is the user's)
    NODES['skyship'] = sk(1445, 505)
    NODES['crossroad'] = sk(1430, 872)
    NODES['shed'] = sk(330, 905)
    NODES['vox'] = sk(2025, 850)
    NODES['scraper'] = sk(1300, 1480)
    NODES['cathedral'] = sk(2085, 1270)
    NODES['bus'] = sk(2530, 1490)

    # ---- Burning Bear Street: a side street dropping from the sketch's lower road (its line reaches sk(1585,1672))
    lx, ly = sk(1585, 1672)
    bx = lx - 22                                                        # the street's centre line
    yl = ly - 3                                                         # where it meets the sketch's line
    stroke([(bx - 9, yl), (bx - 9.5, 470), (bx - 8, 548)]); stroke([(bx + 9, yl - 0.5), (bx + 8.5, 480), (bx + 9, 549)])
    # the avenue: Town Square -> Bear St -> the Screaming Cork -> the harbour
    road([(300, 494), (340, 522), (390, 548), (bx, 556), (560, 558), (680, 556), (780, 538), (846, 512)], w=9)
    # the square to the Townhall, and up between the houses to the Lumen Directorate
    road([(208, 478), (172, 471), (154, 471)], w=6)
    road([(226, 456), (210, 414), (190, 386), (150, 368), (118, 366)], w=6)

    # ---- the sea: the coast with the drain's delta cut into it, the water, the island
    curve([(885, 0), (878, 50), (890, 105), (882, 150), (872, 186), (876, 204)])                  # coast above the delta
    curve([(846, 214), (872, 206), (898, 196), (922, 190)])                                      # the delta's north bank
    curve([(846, 236), (872, 244), (892, 258), (904, 280), (898, 320), (896, 368), (884, 420),
           (866, 470), (852, 520), (840, 560), (832, 600)])                                      # its south bank, the coast below
    for (x, y) in [(920, 30), (975, 58), (1035, 32), (1012, 100), (950, 120), (1040, 160), (1046, 250), (996, 296),
                   (940, 336), (1040, 330), (930, 398), (928, 462), (1046, 468), (900, 540), (982, 560), (1040, 545),
                   (880, 590), (966, 505), (926, 150), (1020, 212)]:
        waves(x + r.uniform(-4, 4), y + r.uniform(-3, 3), r.uniform(8, 12))

    # ---- Echo Drain Delta: the drain pipe in its wall, the water splitting round reedy islets, derricks with horns
    def derrick(x, yb, h, d):
        w = h * 0.34
        seg((x - w / 2, yb), (x - w * 0.13, yb - h)); seg((x + w / 2, yb), (x + w * 0.13, yb - h))
        n = 4
        for i in range(n):
            y0 = yb - h * i / n; y1 = yb - h * (i + 1) / n
            hw0 = w / 2 - (w * 0.37) * i / n; hw1 = w / 2 - (w * 0.37) * (i + 1) / n
            stroke([(x - hw0, y0), (x + hw1, y1)], lw=FINE * 0.75); stroke([(x + hw0, y0), (x - hw1, y1)], lw=FINE * 0.75)
            seg((x - hw1, y1), (x + hw1, y1), lw=FINE * 0.8, ov=0.3)
        # the gramophone horn: a bent neck flaring into a wide open mouth
        tx, ty = x, yb - h
        stroke([(tx, ty), (tx + d * 2, ty - 5), (tx + d * 7, ty - 10), (tx + d * 14, ty - 17)], lw=FINE, smooth=True)
        stroke([(tx + d * 2, ty + 1), (tx + d * 8, ty - 1), (tx + d * 15, ty - 3), (tx + d * 24, ty - 5)], lw=FINE, smooth=True)
        mx, my = tx + d * 19, ty - 11
        ca, sa = math.cos(math.radians(-40 * d)), math.sin(math.radians(-40 * d))
        pts = [(mx + math.cos(math.radians(i * 15)) * 4 * ca - math.sin(math.radians(i * 15)) * 9 * sa,
                my + math.cos(math.radians(i * 15)) * 4 * sa + math.sin(math.radians(i * 15)) * 9 * ca) for i in range(26)]
        stroke(pts, lw=FINE, smooth=True, wob=0.3)
        dot(mx - d * 0.5, my + 0.5, 1.3)                                                         # the dark throat
    for isle, reeds in (([(904, 222), (918, 214), (936, 216), (944, 224), (930, 230), (912, 230)], (908, 913, 940)),
                        ([(944, 244), (960, 236), (984, 238), (990, 248), (972, 254), (952, 252)], (948, 986, 991))):
        erase(isle); curve(isle + isle[:2], lw=FINE + 0.3)
        for x in reeds:
            y0 = sum(p[1] for p in isle) / len(isle)
            stroke([(x, y0), (x + r.uniform(-1.5, 1.5), y0 - r.uniform(8, 12))], lw=FINE * 0.75)
            dot(x + 0.3, y0 - r.uniform(11, 13), 1.2)
    derrick(926, 222, 60, 1)
    derrick(968, 245, 44, -1)
    # the drain: a pipe mouth in a wall, pouring into the channel
    seg((842, 204), (842, 246), lw=FINE + 0.3)
    ell(848, 225, 5.5, 7, lw=FINE + 0.3); ell(849, 225, 2.2, 3, lw=FINE * 0.8)
    for k in range(3): stroke([(853, 222 + k * 2.5), (860, 224 + k * 3), (868, 225 + k * 4)], lw=FINE * 0.7, smooth=True)
    for (x, y) in ((884, 218), (896, 236)): waves(x, y, 7)
    NODES['delta'] = (866, 258)
    # the coast path, harbour to delta
    path = _catmull([(858, 470), (874, 420), (884, 368), (884, 318), (876, 276), (868, 262)], 8)
    for i in range(0, len(path) - 3, 5): stroke(path[i:i + 3], lw=FINE * 0.8, wob=0.2)

    # ---- Redmass Island: an island, a roofless brick ruin under a bare roof truss
    isl = [(948, 432), (962, 420), (990, 416), (1022, 420), (1040, 430), (1030, 442), (1000, 446), (968, 444)]
    erase(isl)
    curve(isl + [isl[0], isl[1]])
    ix, iy = 968, 432
    poly([(ix, iy), (ix, iy - 20), (ix + 6, iy - 24), (ix + 10, iy - 19), (ix + 15, iy - 25), (ix + 22, iy - 22), (ix + 26, iy - 28), (ix + 34, iy - 26), (ix + 38, iy - 18), (ix + 42, iy - 22), (ix + 48, iy - 21), (ix + 48, iy)], closed=False)
    window(ix + 12, iy - 10, 7, 9, 'arch'); window(ix + 34, iy - 11, 7, 9, 'arch')
    for (bx_, by_) in [(ix + 4, iy - 4), (ix + 20, iy - 6), (ix + 26, iy - 15), (ix + 42, iy - 6), (ix + 6, iy - 14), (ix + 44, iy - 14)]:
        stroke([(bx_, by_), (bx_ + 4, by_)], lw=FINE * 0.7)
    # the bare truss above the walls
    seg((ix - 4, iy - 30), (ix + 52, iy - 30), lw=FINE)
    poly([(ix - 2, iy - 30), (ix + 24, iy - 44), (ix + 50, iy - 30)], closed=False, lw=FINE)
    seg((ix + 24, iy - 44), (ix + 24, iy - 30), lw=FINE * 0.8)
    seg((ix + 11, iy - 37), (ix + 15, iy - 30), lw=FINE * 0.8); seg((ix + 37, iy - 37), (ix + 33, iy - 30), lw=FINE * 0.8)
    stroke([(ix + 2, iy - 30), (ix + 2, iy - 22)], lw=FINE * 0.8); stroke([(ix + 46, iy - 30), (ix + 46, iy - 23)], lw=FINE * 0.8)
    NODES['redmass'] = (1004, 452)
    # the ferry route from the delta and a little boat on it
    for i in range(10):
        t0, t1 = i / 10, (i + 0.5) / 10
        p = lambda t: (960 + (996 - 960) * t + math.sin(t * 3.14) * 26, 262 + (408 - 262) * t)
        stroke([p(t0), p(t1)], lw=FINE * 0.8)
    stroke([(980, 340), (984, 345), (996, 345), (1000, 340)], lw=FINE, smooth=True); seg((979, 340), (1001, 340), lw=FINE * 0.9)
    stroke([(989, 340), (989, 328)], lw=FINE * 0.8); poly([(990, 329), (997, 337), (990, 337)], lw=FINE * 0.8)

    # ---- the Harbour: a pier into the water, a lattice crane with a hook, a boat shed, crates
    erase([(806, 420), (930, 420), (930, 512), (806, 512)])
    poly([(856, 494), (920, 472), (928, 478), (864, 502)], closed=False)
    seg((856, 494), (864, 502))
    for t in (0.2, 0.4, 0.6, 0.8):
        a = (856 + 64 * t, 494 - 22 * t); b = (864 + 64 * t, 502 - 24 * t)
        stroke([a, b], lw=FINE * 0.7)
        stroke([(b[0], b[1]), (b[0] + 0.3, b[1] + 6)], lw=FINE * 0.9)
    # the crane: a lattice tower, a long jib out over the water, a stay to its mast, a hook on a line
    cx0, cyb, ch = 850, 490, 52
    seg((cx0 - 7, cyb), (cx0 - 4, cyb - ch)); seg((cx0 + 7, cyb), (cx0 + 4, cyb - ch))
    for i in range(5):
        y0 = cyb - ch * i / 5; y1 = cyb - ch * (i + 1) / 5
        stroke([(cx0 - 7 + 3 * i / 5, y0), (cx0 + 7 - 3 * (i + 1) / 5, y1)], lw=FINE * 0.7)
        stroke([(cx0 + 7 - 3 * i / 5, y0), (cx0 - 7 + 3 * (i + 1) / 5, y1)], lw=FINE * 0.7)
    seg((cx0 - 12, cyb - ch), (cx0 + 50, cyb - ch - 4)); seg((cx0 - 4, cyb - ch + 5), (cx0 + 48, cyb - ch - 2.5), lw=FINE)
    stroke([(cx0, cyb - ch), (cx0, cyb - ch - 12)], lw=FINE); stroke([(cx0, cyb - ch - 12), (cx0 + 46, cyb - ch - 4)], lw=1.2)
    stroke([(cx0, cyb - ch - 12), (cx0 - 12, cyb - ch)], lw=1.2)
    box(cx0 - 12, cyb - ch + 1, cx0 - 6, cyb - ch + 6, lw=FINE, ov=0.3)                          # the counterweight
    stroke([(cx0 + 42, cyb - ch - 3), (cx0 + 42, cyb - ch + 22)], lw=1.2)
    stroke([(cx0 + 42, cyb - ch + 22), (cx0 + 42, cyb - ch + 27), (cx0 + 39, cyb - ch + 29), (cx0 + 37, cyb - ch + 26)], lw=FINE, smooth=True)
    house(808, 492, 28, 19, 'gable', random.Random(3), wk='sq', tilt=1.0)                         # the boat shed
    box(833, 486, 840, 493, lw=FINE, ov=0.4); stroke([(833, 486), (840, 493)], lw=FINE * 0.7)
    box(835, 479, 841, 485, lw=FINE, ov=0.4)
    lamp(902, 474, 18)
    NODES['harbor'] = (848, 506)

    # ---- the Screaming Cork: a wooden false-front saloon, a hanging cork sign that screams, barrels
    cx, cyb, cw = 610, 538, 68
    erase([(cx - 6, cyb), (cx - 6, cyb - 66), (cx + cw + 4, cyb - 66), (cx + cw + 4, cyb)])
    seg((cx, cyb), (cx, cyb - 52)); seg((cx + cw, cyb), (cx + cw, cyb - 52))
    poly([(cx - 2, cyb - 52), (cx + 8, cyb - 52), (cx + 8, cyb - 62), (cx + cw - 8, cyb - 62), (cx + cw - 8, cyb - 52), (cx + cw + 2, cyb - 52)], closed=False)
    seg((cx - 2, cyb), (cx + cw + 2, cyb), ov=1.5)
    box(cx + 14, cyb - 47, cx + cw - 14, cyb - 37, lw=FINE)                        # the name board
    stroke([(cx + 18, cyb - 42), (cx + 26, cyb - 43), (cx + 34, cyb - 41), (cx + 44, cyb - 43), (cx + 50, cyb - 42)], lw=FINE * 0.7, smooth=True)
    for wx in (cx + 10, cx + 24, cx + cw - 24, cx + cw - 10):
        window(wx, cyb - 27, 8, 8, 'cross')
    for wx in (cx + 10, cx + cw - 10): window(wx, cyb - 12, 8, 8, 'cross')
    door(cx + cw / 2, cyb, 10, 15, arched=False)
    stroke([(cx + cw / 2 - 9, cyb - 17), (cx + cw / 2 + 9, cyb - 17)], lw=FINE)        # the awning
    for k in range(4): stroke([(cx + cw / 2 - 9 + k * 6, cyb - 17), (cx + cw / 2 - 7 + k * 6, cyb - 14)], lw=FINE * 0.7)
    for y in (cyb - 33, cyb - 20): stroke([(cx + 2, y), (cx + 5, y)], lw=FINE * 0.6); stroke([(cx + cw - 5, y + 1), (cx + cw - 2, y + 1)], lw=FINE * 0.6)
    # the hanging sign: a bracket off the left corner, a cork with a screaming face
    stroke([(cx, cyb - 36), (cx - 14, cyb - 36)], lw=FINE)
    stroke([(cx - 3, cyb - 36), (cx, cyb - 31)], lw=FINE * 0.7)
    stroke([(cx - 12, cyb - 36), (cx - 12, cyb - 33)], lw=FINE * 0.7)
    poly([(cx - 17, cyb - 33), (cx - 7, cyb - 33), (cx - 8, cyb - 20), (cx - 16, cyb - 20)], lw=FINE)
    dot(cx - 14, cyb - 29, 0.9); dot(cx - 10, cyb - 29, 0.9)
    ell(cx - 12, cyb - 24.5, 1.8, 2.4, lw=FINE * 0.8)
    for bx2 in (cx + cw + 6, cx + cw + 13):                                           # barrels
        ell(bx2, cyb - 10, 3, 1.2, lw=FINE * 0.8)
        stroke([(bx2 - 3, cyb - 10), (bx2 - 3.2, cyb)], lw=FINE * 0.9); stroke([(bx2 + 3, cyb - 10), (bx2 + 3.2, cyb)], lw=FINE * 0.9)
        stroke([(bx2 - 3, cyb - 5), (bx2, cyb - 4), (bx2 + 3, cyb - 5)], lw=FINE * 0.6, smooth=True)
    NODES['cork'] = (cx + cw / 2, cyb + 3)

    # ---- Burning Bear Street: a narrow street between two rows, teddy bears hung across it on strings
    # (the houses either side are drawn with the town below; the strings go over the street at the top)

    # ---- the Townhall: a long civic front, a little dome, the big clock gripped by tentacles
    tx, tyb, tw = 32, 486, 120
    erase([(tx - 4, tyb), (tx - 4, tyb - 70), (tx + tw + 4, tyb - 70), (tx + tw + 4, tyb)])
    box(tx, tyb - 40, tx + tw, tyb)
    seg((tx - 3, tyb - 40), (tx + tw + 3, tyb - 40))
    poly([(tx + 42, tyb - 40), (tx + 42, tyb - 50), (tx + 78, tyb - 50), (tx + 78, tyb - 40)], closed=False)
    ell(tx + 60, tyb - 50, 13, 12, 180, 360, closed=False)
    stroke([(tx + 60, tyb - 62), (tx + 60, tyb - 69)], lw=FINE); dot(tx + 60, tyb - 70, 1.3)
    for i in range(5):
        for j, yy in enumerate((tyb - 30, tyb - 13)):
            wx = tx + 10 + i * 9 if i < 3 else tx + tw - 10 - (4 - i) * 9
            wx = [tx + 9, tx + 19, tx + 29, tx + tw - 29, tx + tw - 19, tx + tw - 9][i if i < 3 else i + 1] if i != 4 else tx + tw - 9
            window(wx, yy, 5.5, 8, 'arch')
    window(tx + tw - 19, tyb - 30, 5.5, 8, 'arch'); window(tx + tw - 19, tyb - 13, 5.5, 8, 'arch')
    door(tx + 60, tyb - 3, 10, 13)
    for k in range(3): stroke([(tx + 52 - k * 2, tyb - 3 + k * 1.5), (tx + 68 + k * 2, tyb - 3 + k * 1.5)], lw=FINE * 0.7)
    # the clock over the door and its tentacles
    ccx, ccy = tx + 60, tyb - 29
    erase([(ccx - 12, ccy - 12), (ccx + 12, ccy - 12), (ccx + 12, ccy + 12), (ccx - 12, ccy + 12)])
    ell(ccx, ccy, 10, 10)
    for k in range(12):
        a = k * math.pi / 6
        stroke([(ccx + math.cos(a) * 7.6, ccy + math.sin(a) * 7.6), (ccx + math.cos(a) * 8.6, ccy + math.sin(a) * 8.6)], lw=1.2)
    stroke([(ccx, ccy), (ccx + 0.5, ccy - 6.5)], lw=FINE * 0.8); stroke([(ccx, ccy), (ccx + 4.5, ccy + 2)], lw=FINE * 0.8)
    for sx, pts in [(-1, [(-9, -5), (-16, -10), (-20, -6), (-24, -10)]), (1, [(9, -5), (15, -11), (21, -8), (25, -12)]),
                    (-1, [(-9, 5), (-15, 9), (-17, 15), (-22, 16)]), (1, [(9, 5), (15, 10), (16, 16), (21, 18)])]:
        stroke([(ccx + px_, ccy + py_) for px_, py_ in pts], lw=FINE + 0.2, smooth=True)
        for t in (1, 2): dot(ccx + pts[t][0] + 1, ccy + pts[t][1] + 1.6, 0.7)
    NODES['townhall'] = (tx + 60, tyb + 4)

    # ---- the Lumen Directorate: a gothic front, twin spires, a rose window, lamps and flowerbeds
    lx0, lyb = 46, 352
    erase([(lx0 - 22, lyb + 4), (lx0 - 22, lyb - 104), (lx0 + 122, lyb - 104), (lx0 + 122, lyb + 4)])
    mx = lx0 + 50
    # the nave front
    seg((mx - 24, lyb), (mx - 24, lyb - 48)); seg((mx + 24, lyb), (mx + 24, lyb - 48))
    poly([(mx - 26, lyb - 48), (mx, lyb - 74), (mx + 26, lyb - 48)], closed=False)
    seg((mx - 24, lyb - 48), (mx + 24, lyb - 48), ov=0.5)
    ell(mx, lyb - 58, 7, 7)
    for k in range(6):
        a = k * math.pi / 3
        stroke([(mx, lyb - 58), (mx + math.cos(a) * 6, lyb - 58 + math.sin(a) * 6)], lw=1.3)
    dot(mx, lyb - 77, 1.4)
    # the pointed door
    stroke([(mx - 6, lyb), (mx - 6, lyb - 14), (mx - 3, lyb - 21), (mx, lyb - 24)], lw=FINE + 0.3, smooth=True)
    stroke([(mx + 6, lyb), (mx + 6, lyb - 14), (mx + 3, lyb - 21), (mx, lyb - 24)], lw=FINE + 0.3, smooth=True)
    stroke([(mx, lyb - 24), (mx, lyb)], lw=FINE * 0.7)
    window(mx - 15, lyb - 30, 5, 12, 'arch'); window(mx + 15, lyb - 30, 5, 12, 'arch')
    # the spires
    for sx_ in (-1, 1):
        x0 = mx + sx_ * 24 + (0 if sx_ > 0 else -14)
        box(x0, lyb - 66, x0 + 14, lyb)
        poly([(x0 - 1, lyb - 66), (x0 + 7, lyb - 96), (x0 + 15, lyb - 66)], closed=False)
        dot(x0 + 7, lyb - 98, 1.2)
        window(x0 + 7, lyb - 52, 4.5, 10, 'arch'); window(x0 + 7, lyb - 26, 4.5, 10, 'arch')
    # low wings
    for sx_ in (-1, 1):
        x0 = mx + sx_ * 38 + (-14 if sx_ < 0 else 0)
        poly([(x0, lyb), (x0, lyb - 30), (x0 + 14, lyb - 30), (x0 + 14, lyb)] if sx_ < 0 else [(x0, lyb), (x0, lyb - 30), (x0 + 14, lyb - 30), (x0 + 14, lyb)], closed=False)
        window(x0 + 7, lyb - 16, 5, 10, 'arch')
    seg((mx - 54, lyb), (mx + 54, lyb), ov=1.5)
    # flowerbeds + lamps in front
    for sx_ in (-1, 1):
        fx = mx + sx_ * 30
        box(fx - 12, lyb + 5, fx + 12, lyb + 10, lw=FINE, ov=0.5)
        for k in range(5): ell(fx - 9 + k * 4.5, lyb + 3 + (k % 2), 1.4, 1.4, lw=1.1)
        lamp(mx + sx_ * 15, lyb + 6, 16)
    NODES['lumen'] = (mx, lyb + 8)

    # ---- Town Square: a round cobbled plaza with the fan pattern
    sqx, sqy = 252, 478
    erase([(sqx - 60, sqy - 20), (sqx + 60, sqy - 20), (sqx + 60, sqy + 20), (sqx - 60, sqy + 20)])
    ell(sqx, sqy, 56, 17); ell(sqx, sqy, 16, 5, lw=FINE)
    for k in range(14):
        a = k * math.pi / 7 + 0.1
        stroke([(sqx + math.cos(a) * 20, sqy + math.sin(a) * 6.4), (sqx + math.cos(a) * 50, sqy + math.sin(a) * 15)], lw=FINE * 0.6)
    for k in range(12):
        a = k * math.pi / 6 + 0.35
        ell(sqx + math.cos(a) * 34, sqy + math.sin(a) * 10.5, 2.2, 0.9, a * 57 - 50, a * 57 + 50, closed=False, lw=1.0)
    NODES['square'] = (sqx, sqy)

    # ---- the town: little houses, every one different, back rows first
    r2 = random.Random(1867)
    row(236, 334, 452, r2, hmin=30, hmax=50, wmin=16, wmax=28, gap=(0.5, 3))                 # behind the square
    row(186, 336, 268, r2, hmin=18, hmax=30, wmin=15, wmax=24)                               # under the Shed road
    row(444, 498, 302, r2, kinds=['gable', 'shed', 'cone', 'flat'], hmin=16, hmax=24, wmin=14, wmax=20)   # by the Scraper
    row(176, 334, 360, r2, hmin=24, hmax=40, wmin=15, wmax=26)                               # right of the Directorate
    row(360, bx - 12, 470, r2, hmin=24, hmax=36, wmin=14, wmax=24, gap=(0.5, 2))             # Bear St, west, back
    row(500, 800, 425, r2, hmin=22, hmax=38, wmin=16, wmax=30)                               # under the bus road
    row(384, bx - 12, 527, r2, hmin=26, hmax=40, wmin=14, wmax=22, gap=(0.5, 2))             # Bear St, west
    row(bx + 12, 598, 518, r2, hmin=28, hmax=46, wmin=14, wmax=24, gap=(0.5, 2))             # Bear St, east
    row(bx + 12, 600, 466, r2, hmin=22, hmax=34, wmin=14, wmax=22)                           # Bear St, east, back
    row(696, 792, 522, r2, hmin=20, hmax=32, wmin=14, wmax=24)                               # towards the harbour
    row(800, 864, 196, r2, kinds=['box3d', 'shed', 'flat', 'gable'], hmin=16, hmax=26, wmin=16, wmax=26)   # by the coast
    row(826, 880, 330, r2, hmin=18, hmax=28, wmin=14, wmax=20)
    row(800, 868, 404, r2, hmin=18, hmax=30, wmin=14, wmax=22)
    row(22, 270, 584, r2, hmin=16, hmax=26, wmin=16, wmax=26)                                # under the Townhall

    # the bears over Burning Bear Street: two sagging strings with pennants and a hanging teddy
    for k, (sy, sp) in enumerate(((474, 6), (492, 8))):
        x0, x1 = bx - 22 - k * 3, bx + 22 + k * 3
        pts = [(x0 + (x1 - x0) * t / 10, sy + math.sin(math.pi * t / 10) * sp) for t in range(11)]
        stroke(pts, lw=1.3, smooth=True, wob=0.2)
        for t in ((1, 3, 7, 9) if k == 0 else (2, 8)):
            px_, py_ = pts[t]
            poly([(px_ - 2.2, py_), (px_ + 2.2, py_), (px_, py_ + 4.5)], lw=1.1)
        px_, py_ = pts[5 if k == 0 else 4]
        stroke([(px_, py_), (px_, py_ + 3)], lw=1.1)
        hx, hy = px_, py_ + 7.5
        erase([(hx - 7, hy - 6), (hx + 7, hy - 6), (hx + 7, hy + 13), (hx - 7, hy + 13)])
        ell(hx, hy, 4.0, 3.7, lw=1.6); ell(hx - 3.3, hy - 3.1, 1.5, 1.5, lw=1.3); ell(hx + 3.3, hy - 3.1, 1.5, 1.5, lw=1.3)
        dot(hx - 1.4, hy - 0.5, 0.55); dot(hx + 1.4, hy - 0.5, 0.55)
        ell(hx, hy + 8.2, 4.4, 4.6, lw=1.6)
        stroke([(hx - 4, hy + 6), (hx - 6.8, hy + 9.5)], lw=1.4); stroke([(hx + 4, hy + 6), (hx + 6.8, hy + 9.5)], lw=1.4)
        if k == 1:                                                              # this one does burn
            for f in (-1, 1):
                stroke([(hx + f * 1.5, hy + 12.5), (hx + f * 3.5, hy + 16), (hx + f * 1.8, hy + 19.5)], lw=1.1, smooth=True)
            stroke([(hx, hy + 12.5), (hx + 0.8, hy + 17), (hx - 0.3, hy + 21)], lw=1.1, smooth=True)
    NODES['bear'] = (bx, 512)

    # birds round the skyship
    for (x, y, s_) in ((500, 60, 1.0), (514, 52, 0.8), (352, 96, 0.9)):
        stroke([(x - 4 * s_, y - 2 * s_), (x - 1.5 * s_, y - 0.5 * s_), (x, y + 1 * s_)], lw=1.4, smooth=True, wob=0.2)
        stroke([(x, y + 1 * s_), (x + 1.5 * s_, y - 0.5 * s_), (x + 4 * s_, y - 2 * s_)], lw=1.4, smooth=True, wob=0.2)
    # trees in the gaps
    for (x, yb, h) in [(172, 396, 26), (346, 380, 22), (24, 412, 24), (168, 528, 20), (348, 452, 20), (304, 584, 18), (585, 588, 16), (760, 584, 18), (20, 560, 22)]:
        tree(x, yb, h)


# ================================================================== the felt-tip colouring (--color)
# eight markers, no more (the user's limit); multiplied over the paper like real dye, two layers of strokes per colour
# so where strokes overlap the colour goes darker in streaks
PAL = {'yellow': (246, 212, 76), 'orange': (238, 146, 62), 'red': (212, 74, 66), 'violet': (152, 114, 188),
       'blue': (88, 154, 212), 'green': (108, 174, 94), 'brown': (156, 104, 66), 'gray': (152, 154, 160)}

def colour_fills():
    """the areas of the sketch itself and of the drawn landmarks (houses, roads, trees, lamps, doors record their own)"""
    # --- the sketch: roads
    fseed(200, 190, 'gray', 0.4)                                                         # Shed -> Crossroads -> Voxmarket
    fline([(510, 268), (530, 280), (550, 287), (580, 291)], 10, 'gray', 0.4)
    fline([(438, 364), (520, 366), (620, 368), (700, 370), (722, 371)], 11, 'gray', 0.4)
    # Shed 521
    fpoly([(60, 124), (117, 121), (117, 152), (58, 156)], 'gray', 0.5, win=True)
    fpoly([(117, 121), (139, 117), (138, 141), (117, 152)], 'gray', 0.8)
    fpoly([(64, 123), (72, 117), (138, 115), (142, 121)], 'red', 0.8)
    fpoly([(24, 166), (50, 156), (118, 155), (144, 153), (128, 166)], 'red', 0.75)
    fpoly([(22, 167), (128, 167), (126, 199), (22, 198)], 'blue', 0.5, win=True)
    # the skyship Verdigrace and its gondola
    fpoly(ellpts(431, 45, 47, 13), 'green', 0.65)
    fpoly([(410, 57), (451, 57), (447, 67), (414, 67)], 'brown', 0.8)
    # Voxmarket hangars
    fpoly(ellpts(607, 177, 41, 41, 180, 360), 'orange', 0.6)
    fpoly([(612, 135), (652, 101), (690, 99), (705, 116), (672, 132), (646, 142)], 'orange', 0.8)
    fpoly(ellpts(693, 174, 45, 40, 180, 360), 'blue', 0.55)
    fpoly([(706, 121), (745, 104), (786, 112), (796, 135), (736, 165), (728, 172)], 'blue', 0.8)
    # Scraper 1140, floor by floor
    fpoly([(383, 205), (400, 205), (400, 226), (383, 226)], 'red', 0.75)
    fpoly([(370, 228), (415, 227), (415, 258), (370, 258)], 'blue', 0.55, win=True)
    fpoly([(352, 262), (422, 260), (420, 307), (352, 308)], 'violet', 0.5, win=True)
    fpoly([(343, 310), (432, 308), (434, 362), (343, 362)], 'gray', 0.55, win=True)
    # the Egg Cathedral: shells, the church inside, its door, the platter
    fpoly([(550, 230), (567, 228), (576, 240), (569, 252), (576, 262), (570, 279), (553, 287), (542, 279), (538, 255), (542, 239)], 'yellow', 0.5)
    fpoly([(697, 234), (720, 231), (740, 242), (747, 265), (740, 288), (718, 297), (702, 293), (701, 280), (692, 265), (698, 250)], 'yellow', 0.5)
    fpoly([(582, 292), (585, 228), (598, 212), (608, 230), (612, 252), (640, 245), (648, 215), (660, 222), (668, 232), (682, 222), (695, 240), (698, 296)],
          'violet', 0.5, holes=[ellpts(628, 285, 14, 18, 180, 360) + [(642, 300), (614, 300)]])
    fpoly(ellpts(628, 285, 14, 18, 180, 360) + [(642, 300), (614, 300)], 'brown', 0.75, door=True)
    fpoly([(530, 295), (600, 282), (700, 284), (762, 298), (700, 307), (560, 306)], 'gray', 0.4)
    # the street of narrow houses and the abandoned bus
    for (x0, x1, yt, c) in ((503, 523, 330, 'blue'), (525, 546, 327, 'orange'), (583, 602, 322, 'green'),
                            (629, 648, 321, 'violet'), (672, 690, 329, 'yellow')):
        fpoly([(x0, yt), (x1, yt - 1), (x1, 357), (x0, 358)], c, 0.5)
    fpoly([(702, 331), (795, 321), (797, 356), (702, 362)], 'orange', 0.65,
          holes=[[(707, 333), (727, 333), (727, 349), (707, 349)], [(768, 327), (787, 327), (787, 345), (768, 345)]])
    fpoly([(702, 331), (722, 311), (806, 309), (795, 321)], 'red', 0.75)
    fpoly([(795, 321), (806, 309), (808, 335), (797, 356)], 'orange', 0.85)
    fpoly([(707, 333), (727, 333), (727, 349), (707, 349)], 'blue', 0.6)
    fpoly([(768, 327), (787, 327), (787, 345), (768, 345)], 'blue', 0.6)
    fpoly([(735, 338), (752, 338), (752, 360), (735, 360)], 'brown', 0.75, door=True)

    # --- the sea and the delta
    fpoly([(885, 0), (878, 50), (890, 105), (882, 150), (872, 186), (876, 204), (846, 214), (846, 236), (872, 244), (892, 258),
           (904, 280), (898, 320), (896, 368), (884, 420), (866, 470), (852, 520), (840, 560), (832, 600), (1067, 600), (1067, 0)],
          'blue', 0.5, holes=[[(904, 222), (918, 214), (936, 216), (944, 224), (930, 230), (912, 230)],
                              [(944, 244), (960, 236), (984, 238), (990, 248), (972, 254), (952, 252)],
                              [(948, 432), (962, 420), (990, 416), (1022, 420), (1040, 430), (1030, 442), (1000, 446), (968, 444)],
                              [(856, 494), (920, 472), (928, 478), (864, 502)]])
    for isle in ([(904, 222), (918, 214), (936, 216), (944, 224), (930, 230), (912, 230)],
                 [(944, 244), (960, 236), (984, 238), (990, 248), (972, 254), (952, 252)]):
        fpoly(isle, 'green', 0.65)
    for (x, yb, h, d) in ((926, 222, 60, 1), (968, 245, 44, -1)):
        w = h * 0.34; tx, ty = x, yb - h
        fpoly([(x - w / 2, yb), (x - w * 0.13, ty), (x + w * 0.13, ty), (x + w / 2, yb)], 'gray', 0.45)
        fpoly([(tx, ty), (tx + d * 7, ty - 10), (tx + d * 14, ty - 17), (tx + d * 24, ty - 5), (tx + d * 8, ty - 1), (tx + d * 2, ty + 1)], 'orange', 0.75)
        mx, my = tx + d * 19, ty - 11
        ca, sa = math.cos(math.radians(-40 * d)), math.sin(math.radians(-40 * d))
        fpoly([(mx + math.cos(math.radians(i * 15)) * 4 * ca - math.sin(math.radians(i * 15)) * 9 * sa,
                my + math.cos(math.radians(i * 15)) * 4 * sa + math.sin(math.radians(i * 15)) * 9 * ca) for i in range(25)], 'yellow', 0.85)
    fpoly(ellpts(848, 225, 5.5, 7), 'gray', 0.7)
    # Redmass Island: sand, the brick ruin, the ferry
    fpoly([(948, 432), (962, 420), (990, 416), (1022, 420), (1040, 430), (1030, 442), (1000, 446), (968, 444)], 'yellow', 0.5)
    ix, iy = 968, 432
    fpoly([(ix, iy), (ix, iy - 20), (ix + 6, iy - 24), (ix + 10, iy - 19), (ix + 15, iy - 25), (ix + 22, iy - 22), (ix + 26, iy - 28),
           (ix + 34, iy - 26), (ix + 38, iy - 18), (ix + 42, iy - 22), (ix + 48, iy - 21), (ix + 48, iy)], 'red', 0.65)
    fpoly([(980, 340), (984, 345), (996, 345), (1000, 340)], 'brown', 0.8)
    fpoly([(990, 329), (997, 337), (990, 337)], 'red', 0.7)
    # the harbour
    fpoly([(856, 494), (920, 472), (928, 478), (864, 502)], 'brown', 0.75)
    fpoly([(843, 490), (846, 438), (854, 438), (857, 490)], 'orange', 0.55)
    fline([(838, 437), (900, 434)], 3.5, 'orange', 0.6)
    fpoly([(838, 439), (844, 439), (844, 444), (838, 444)], 'gray', 0.8)
    fpoly([(833, 486), (840, 486), (840, 493), (833, 493)], 'brown', 0.8)
    fpoly([(835, 479), (841, 479), (841, 485), (835, 485)], 'brown', 0.8)

    # --- the Screaming Cork
    cx, cyb, cw = 610, 538, 68
    board = [(cx + 14, cyb - 47), (cx + cw - 14, cyb - 47), (cx + cw - 14, cyb - 37), (cx + 14, cyb - 37)]
    fpoly([(cx, cyb), (cx, cyb - 52), (cx + 8, cyb - 52), (cx + 8, cyb - 62), (cx + cw - 8, cyb - 62), (cx + cw - 8, cyb - 52),
           (cx + cw, cyb - 52), (cx + cw, cyb)], 'brown', 0.55, win=True, holes=[board])
    fpoly(board, 'yellow', 0.8)
    fpoly([(cx - 17, cyb - 33), (cx - 7, cyb - 33), (cx - 8, cyb - 20), (cx - 16, cyb - 20)], 'orange', 0.85)
    fpoly([(cx + cw / 2 - 9, cyb - 17), (cx + cw / 2 + 9, cyb - 17), (cx + cw / 2 + 11, cyb - 14), (cx + cw / 2 - 7, cyb - 14)], 'red', 0.8)
    for bx2 in (cx + cw + 6, cx + cw + 13):
        fpoly([(bx2 - 3, cyb - 11), (bx2 + 3, cyb - 11), (bx2 + 3.2, cyb), (bx2 - 3.2, cyb)], 'brown', 0.8)

    # --- the Townhall
    tx, tyb, tw = 32, 486, 120
    ccx, ccy = tx + 60, tyb - 29
    fpoly([(tx, tyb), (tx, tyb - 40), (tx + tw, tyb - 40), (tx + tw, tyb)], 'orange', 0.5, win=True, holes=[ellpts(ccx, ccy, 10, 10)])
    fpoly([(tx + 42, tyb - 40), (tx + 42, tyb - 50), (tx + 78, tyb - 50), (tx + 78, tyb - 40)], 'orange', 0.5)
    fpoly(ellpts(tx + 60, tyb - 50, 13, 12, 180, 360), 'green', 0.7)
    fpoly(ellpts(ccx, ccy, 10, 10), 'yellow', 0.85)
    for pts in ([(-9, -5), (-16, -10), (-20, -6), (-24, -10)], [(9, -5), (15, -11), (21, -8), (25, -12)],
                [(-9, 5), (-15, 9), (-17, 15), (-22, 16)], [(9, 5), (15, 10), (16, 16), (21, 18)]):
        fline([(ccx + px_, ccy + py_) for px_, py_ in pts], 4, 'red', 0.75)

    # --- the Lumen Directorate
    lyb, mx = 352, 96
    fpoly([(mx - 24, lyb), (mx - 24, lyb - 48), (mx, lyb - 74), (mx + 24, lyb - 48), (mx + 24, lyb)], 'gray', 0.5, win=True,
          holes=[ellpts(mx, lyb - 58, 7, 7)])
    fpoly(ellpts(mx, lyb - 58, 7, 7), 'yellow', 0.85)
    fpoly([(mx - 6, lyb), (mx - 6, lyb - 14), (mx - 3, lyb - 21), (mx, lyb - 24), (mx + 3, lyb - 21), (mx + 6, lyb - 14), (mx + 6, lyb)], 'brown', 0.8, door=True)
    for x0 in (mx - 38, mx + 24):
        fpoly([(x0, lyb), (x0, lyb - 66), (x0 + 14, lyb - 66), (x0 + 14, lyb)], 'gray', 0.5, win=True)
        fpoly([(x0 - 1, lyb - 66), (x0 + 7, lyb - 96), (x0 + 15, lyb - 66)], 'violet', 0.8)
    for x0 in (mx - 52, mx + 38):
        fpoly([(x0, lyb), (x0, lyb - 30), (x0 + 14, lyb - 30), (x0 + 14, lyb)], 'gray', 0.5, win=True)
    for sx_ in (-1, 1):
        fx = mx + sx_ * 30
        fpoly([(fx - 12, lyb + 5), (fx + 12, lyb + 5), (fx + 12, lyb + 10), (fx - 12, lyb + 10)], 'green', 0.75)
        for k in range(5): fpoly(ellpts(fx - 9 + k * 4.5, lyb + 3 + (k % 2), 1.8, 1.8, n=8), 'red', 0.85)

    # --- Town Square
    sqx, sqy = 252, 478
    fpoly(ellpts(sqx, sqy, 56, 17), 'gray', 0.45, holes=[ellpts(sqx, sqy, 16, 5)])
    fpoly(ellpts(sqx, sqy, 16, 5), 'blue', 0.6)

    # --- Burning Bear Street: the street, the bunting, the bears (one burning)
    lx, ly = sk(1585, 1672); bx = lx - 22; yl = ly - 3
    fpoly([(bx - 9, yl), (bx + 9, yl), (bx + 9, 548), (bx - 9, 548)], 'gray', 0.4)
    flags = ['red', 'yellow', 'blue', 'green']
    for k, (sy, sp) in enumerate(((474, 6), (492, 8))):
        x0, x1 = bx - 22 - k * 3, bx + 22 + k * 3
        pts = [(x0 + (x1 - x0) * t / 10, sy + math.sin(math.pi * t / 10) * sp) for t in range(11)]
        for j, t in enumerate((1, 3, 7, 9) if k == 0 else (2, 8)):
            px_, py_ = pts[t]
            fpoly([(px_ - 2.2, py_), (px_ + 2.2, py_), (px_, py_ + 4.5)], flags[(j + k) % 4], 0.85)
        px_, py_ = pts[5 if k == 0 else 4]
        hx, hy = px_, py_ + 7.5
        for e in (ellpts(hx, hy, 4.0, 3.7), ellpts(hx, hy + 8.2, 4.4, 4.6), ellpts(hx - 3.3, hy - 3.1, 1.5, 1.5), ellpts(hx + 3.3, hy - 3.1, 1.5, 1.5)):
            fpoly(e, 'brown', 0.8)
        if k == 1:
            fpoly([(hx - 4, hy + 12.5), (hx + 4, hy + 12.5), (hx + 2.5, hy + 19), (hx, hy + 21.5), (hx - 2.5, hy + 19)], 'orange', 0.85)
            fpoly([(hx - 1.5, hy + 13), (hx + 1.5, hy + 13), (hx, hy + 18)], 'red', 0.85)


def _labels(wall, W_, H_):
    """4-connected regions of the non-ink pixels: (label list, {label: (count, x0, y0, x1, y1)})"""
    wp = wall.tobytes(); lab = [-1 if wp[i] else 0 for i in range(W_ * H_)]
    regs = {}; n = 0
    for s in range(W_ * H_):
        if lab[s]: continue
        n += 1; lab[s] = n; st = [s]; cnt = 0; x0 = y0 = 10 ** 9; x1 = y1 = -1
        while st:
            p = st.pop(); cnt += 1; x, y = p % W_, p // W_
            x0 = min(x0, x); x1 = max(x1, x); y0 = min(y0, y); y1 = max(y1, y)
            if x > 0 and lab[p - 1] == 0: lab[p - 1] = n; st.append(p - 1)
            if x < W_ - 1 and lab[p + 1] == 0: lab[p + 1] = n; st.append(p + 1)
            if y > 0 and lab[p - W_] == 0: lab[p - W_] = n; st.append(p - W_)
            if y < H_ - 1 and lab[p + W_] == 0: lab[p + W_] = n; st.append(p + W_)
        regs[n] = (cnt, x0, y0, x1, y1)
    return lab, regs

def _marker(mask, box_, ang, alpha, layers, r, sp=5.4, lw=7.6):
    """hatch a mask (2x px, cropped at box_) with parallel felt-tip strokes, alternating between the two layers; every
    stroke overshoots or stops short a little at the edges and leaves a darker blot where the pen turned"""
    w, h = mask.size; mp = mask.load()
    th = math.radians(ang)
    dx, dy = math.cos(th), math.sin(th); nx, ny = -dy, dx
    cx, cy = w / 2, h / 2; R = math.hypot(w, h) / 2 + 3
    ox, oy = box_[0], box_[1]
    k = 0; o = -R
    while o <= R:
        runs, start, last, gap, t = [], None, None, 0, -R
        while t <= R:
            xi, yi = int(cx + nx * o + dx * t), int(cy + ny * o + dy * t)
            if 0 <= xi < w and 0 <= yi < h and mp[xi, yi]:
                if start is None: start = t
                last, gap = t, 0
            elif start is not None:
                gap += 1
                if gap > 2: runs.append((start, last)); start = None
            t += 1.5
        if start is not None: runs.append((start, last))
        for t0, t1 in runs:
            t0 -= r.uniform(-1.0, 2.5); t1 += r.uniform(-1.0, 2.5)
            p0 = (ox + cx + nx * o + dx * t0, oy + cy + ny * o + dy * t0)
            p1 = (ox + cx + nx * o + dx * t1, oy + cy + ny * o + dy * t1)
            v = int(255 * alpha * r.uniform(0.88, 1.0))
            L, Lo = layers[k % 2], layers[(k + 1) % 2]
            d = ImageDraw.Draw(L); d.line([p0, p1], fill=v, width=int(lw))
            for p in (p0, p1): d.ellipse((p[0] - lw / 2, p[1] - lw / 2, p[0] + lw / 2, p[1] + lw / 2), fill=v)
            if r.random() < 0.5:
                p = p1 if k % 2 else p0
                ImageDraw.Draw(Lo).ellipse((p[0] - lw * 0.4, p[1] - lw * 0.4, p[0] + lw * 0.4, p[1] + lw * 0.4), fill=int(v * 0.8))
        k += 1
        o += sp + r.uniform(-0.5, 0.5)

def colour_version(a_fin, pap):
    colour_fills()
    K = 2; W2, H2 = FW * K, FH * K
    r = random.Random(4242)
    wall = a_fin.point(lambda v: 255 if v > 100 else 0)
    lab, regs = _labels(wall, FW, FH)
    # the windows: small enclosed pockets of the drawing
    small = Image.new('L', (FW, FH)); sp_ = small.load()
    smallset = {k for k, (c, x0, y0, x1, y1) in regs.items() if c <= 120 and x1 - x0 <= 16 and y1 - y0 <= 18}
    for i, l in enumerate(lab):
        if l in smallset: sp_[i % FW, i // FW] = 255
    small = small.filter(ImageFilter.MaxFilter(3)).resize((W2, H2), Image.NEAREST)
    # seed fills need the regions with the gaps of the sketch closed
    seeds_lab = {}
    layers = {c: [Image.new('L', (W2, H2)), Image.new('L', (W2, H2))] for c in PAL}
    doors = Image.new('L', (W2, H2)); dd = ImageDraw.Draw(doors)
    for f in FILLS:
        if f.get('door'): dd.polygon([(x * K, y * K) for x, y in f['poly']], fill=255)
    winzone = Image.new('L', (W2, H2))
    def mask_of(f):
        m = Image.new('L', (W2, H2)); d = ImageDraw.Draw(m)
        if 'poly' in f:
            d.polygon([(x * K, y * K) for x, y in f['poly']], fill=255)
            for hole in f.get('holes', ()): d.polygon([(x * K, y * K) for x, y in hole], fill=0)
        elif 'line' in f:
            d.line([(x * K, y * K) for x, y in f['line']], fill=255, width=int(f['w'] * K), joint='curve')
        else:
            dil = f['dil']
            if dil not in seeds_lab:
                seeds_lab[dil] = _labels(wall.filter(ImageFilter.MaxFilter(dil)) if dil > 1 else wall, FW, FH)
            sl, sr = seeds_lab[dil]
            x, y = f['seed']; l = sl[int(y) * FW + int(x)]
            if l <= 0 or sr[l][0] > 20000 or (sr[l][1] == 0 and sr[l][3] == FW - 1):
                print('seed skipped', f['seed']); return None
            sm = Image.new('L', (FW, FH)); smp = sm.load()
            for i, v in enumerate(sl):
                if v == l: smp[i % FW, i // FW] = 255
            sm = sm.filter(ImageFilter.MaxFilter(dil + 2))
            m = sm.resize((W2, H2), Image.NEAREST)
        return m
    for f in FILLS:
        m = mask_of(f)
        if m is None: continue
        if f['win']:
            winzone = ImageChops.lighter(winzone, m)
            m = ImageChops.subtract(m, small)
        if not f.get('door'): m = ImageChops.subtract(m, doors)
        bb = m.getbbox()
        if not bb: continue
        ang = f['ang'] if f['ang'] is not None else -48 + r.uniform(-14, 14)
        _marker(m.crop(bb), bb, ang, f['alpha'], layers[f['color']], r)
    wm = ImageChops.subtract(ImageChops.multiply(small, winzone), doors)
    bb = wm.getbbox()
    if bb: _marker(wm.crop(bb), bb, -45, 0.85, layers['yellow'], r, sp=4.5, lw=6)
    base = pap.resize((W2, H2), Image.BICUBIC)
    white = Image.new('RGB', (W2, H2), (255, 255, 255))
    tint_all = Image.new('RGB', (W2, H2), (255, 255, 255))
    for c, pair in layers.items():
        col = Image.new('RGB', (W2, H2), PAL[c])
        for L in pair:
            if L.getbbox() is None: continue
            tint_all = ImageChops.multiply(tint_all, Image.composite(col, white, L))
    base = ImageChops.multiply(base, tint_all)
    out = base.resize((FW, FH), Image.LANCZOS)
    out.paste(Image.new('RGB', (FW, FH), INK), (0, 0), a_fin)
    return out, tint_all.resize((FW, FH), Image.LANCZOS)


def main():
    draw()
    user = sketch_alpha()
    # a felt-tip leaves its line a touch uneven
    r = random.Random(11)
    tex = Image.new('L', (FW // 3 + 2, FH // 3 + 2)); tex.putdata([r.randint(228, 255) for _ in range((FW // 3 + 2) * (FH // 3 + 2))])
    tex = tex.resize((FW, FH), Image.BICUBIC)
    def down(m):
        m = m.resize((FW, FH), Image.LANCZOS)
        return ImageMath.lambda_eval(lambda e: e['convert'](e['a'] * e['t'] / 255, 'L'), a=m, t=tex)
    a_user, a_mine = down(user), down(ink)
    a = ImageChops.lighter(a_user, a_mine)
    pap = paper()
    out = pap.copy(); out.paste(Image.new('RGB', (FW, FH), INK), (0, 0), a)
    os.makedirs(os.path.join(OUT, 'layers'), exist_ok=True)
    out.save(os.path.join(OUT, 'map.png'))
    pap.save(os.path.join(OUT, 'layers', 'papir.png'))
    for name, m in (('skica', a_user), ('dokresleno', a_mine)):           # the Aseprite layers
        l = Image.new('RGBA', (FW, FH), INK + (0,)); l.putalpha(m); l.save(os.path.join(OUT, 'layers', name + '.png'))
    if '--color' in sys.argv:
        cout, tint = colour_version(a, pap)
        cout.save(os.path.join(OUT, 'map_color.png'))
        tint.save(os.path.join(OUT, 'layers', 'barvy.png'))                   # the marker layer alone (multiply)
    if DEBUG:
        d = out.copy(); dd = ImageDraw.Draw(d)
        for k, (x, y) in NODES.items():
            dd.ellipse((x - 6, y - 6, x + 6, y + 6), outline=(200, 30, 30), width=2)
            dd.text((x - 20, y + 9), k, fill=(200, 30, 30))
        d.save(os.path.join(OUT, 'map_debug.png'))
    for k, (x, y) in NODES.items(): print(f"{k:10s} final ({x:6.1f},{y:6.1f})  MapUI ({x - 533.5:6.1f},{y - 300:6.1f})")

main()
