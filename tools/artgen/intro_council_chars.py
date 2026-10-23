"""The Highest Humenium Council (intro) -- seated archpriests as animated sprites.

Back row (128x176 frames, cut where the table's far edge hides them, sleeves + hands lying on the table top):
  Varhun  -- presiding; the left half of his face long since turned into a fungal organism; purple robe, gold stole,
             a tiered bracket-fungus mitre.
  Tynri   -- her eyes are two small yellow fruiting bodies; ivory robe under a lace veil ("veiled lady" stinkhorn),
             a dark bell cap.
  Rhull   -- the youngest, still mostly human; moss robe, a small button cap, keeps the minutes in a book.
Table ends (200x350 frames, nearer the camera, cropped by the screen bottom):
  elder_l -- an old councillor of Thaal's order, asleep under a huge spotted parasol cap.
  elder_r -- a morel-capped elder with a crook whose bulb glows.

Light comes from the pool of liquid mycelium in front of / below them: faces are lit from below, cap undersides glow.
Sheets: back row = 8 frames (0-3 idle, 4-7 talk); elders = 4 idle frames.

python3 intro_council_chars.py <outdir>  ->  council_<id>.png (sheet) + <id>/<n>.png (frames, for Aseprite)."""
import sys, os, math, random
from PIL import Image
from pal_under import *
from intro_layout import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
nA, nB, nC = make_noise(9, 31, 400, 400), make_noise(4, 32, 400, 400), make_noise(2, 33, 400, 400)
nF = make_noise(2, 34, 400, 400)

def norm(v):
    l = math.sqrt(sum(c * c for c in v)) or 1
    return tuple(c / l for c in v)

class Fig:
    def __init__(s, w, h, light):
        s.w, s.h, s.px, s.part = w, h, {}, {}
        s.L = norm(light)
    def put(s, x, y, c, part='x'):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < s.w and 0 <= y < s.h:
            s.px[(x, y)] = c; s.part[(x, y)] = part
    def get(s, x, y): return s.px.get((int(x), int(y)))
    def lit(s, n, amb=0.25):
        return max(0.0, n[0] * s.L[0] + n[1] * s.L[1] + n[2] * s.L[2]) * (1 - amb) + amb

    def dome(s, cx, cy, rx, ry, k, base, span, part, half=None, tex=0.0, pool_k=None, clip=None):
        """shaded ellipsoid; half='top' keeps y<=cy; pool_k: ramp for strongly down-facing (pool-lit) pixels"""
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            if half == 'top' and y > cy: continue
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                u, w = (x - cx) / rx, (y - cy) / ry
                d = u * u + w * w
                if d > 1: continue
                if clip and not clip(x, y): continue
                n = (u, w, math.sqrt(max(0.0, 1 - d)))
                v = base + span * s.lit(n) + (nB(x + 50, y + 50) - 0.5) * tex
                if pool_k and n[1] > 0.55 and s.L[1] > 0.3: s.put(x, y, col(pool_k, v - 1.5), part); continue
                s.put(x, y, col(k, band(v, x, y)), part)

    def poly(s, pts, shade, part, clip=None):
        """fill polygon; shade(x, y) -> colour"""
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
                if (y0 <= y + 0.5 < y1) or (y1 <= y + 0.5 < y0):
                    xs.append(x0 + (y + 0.5 - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(math.ceil(xs[i] - 0.5)), int(math.floor(xs[i + 1] - 0.5)) + 1):
                    if clip and not clip(x, y): continue
                    c = shade(x, y)
                    if c: s.put(x, y, c, part)

    def cut_below(s, cut):
        for (x, y) in list(s.px):
            if y > cut(x): del s.px[(x, y)]; s.part.pop((x, y), None)

    def outline(s, skip=()):
        """1px dark outline around the silhouette (darkest step of the neighbouring material)"""
        add = {}
        for (x, y), c in s.px.items():
            if s.part.get((x, y)) in skip: continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q not in s.px and 0 <= q[0] < s.w and 0 <= q[1] < s.h:
                    add[q] = INK
        for q, c in add.items(): s.px[q] = c; s.part[q] = 'outline'

    def image(s):
        im = Image.new('RGBA', (s.w, s.h), (0, 0, 0, 0)); p = im.load()
        for (x, y), c in s.px.items(): p[x, y] = c + (255,)
        return im

def robe_body(f, cx, top, cut, hw_top, hw_bot, k, base, span, folds, part='robe'):
    """a seated torso from the neck line down past the cut: shoulders slope, vertical folds, cylinder shading"""
    sh = top + 12
    pts = [(cx - 10, top), (cx + 10, top), (cx + hw_top, sh), (cx + hw_top + 3, sh + 10), (cx + hw_bot, cut + 4),
           (cx - hw_bot, cut + 4), (cx - hw_top - 3, sh + 10), (cx - hw_top, sh)]
    def shade(x, y):
        hw = hw_top + (hw_bot - hw_top) * max(0, (y - sh)) / max(1, cut - sh)
        u = max(-1, min(1, (x - cx) / (hw + 2)))
        n = (u, 0.25 if y > sh else -0.6, math.sqrt(max(0.0, 1 - u * u)))
        v = base + span * f.lit(n) + (nA(x + 9, y * 0.4) - 0.5) * 0.6
        for fx in folds:
            fxx = cx + fx + 2 * math.sin((y - top) / 9 + fx)
            if abs(x - fxx) < 1.0 and y > sh + 4: v -= 1.6
            elif 1.0 <= x - fxx < 2.6 and y > sh + 4: v += 0.7
        return col(k, band(v, x, y))
    f.poly(pts, shade, part)

def sleeve(f, sgn, cx, shoulder_y, cut, k, base, span, mouth_x, mouth_y, width=15):
    """an arm in a wide sleeve: from the shoulder down the body's side, the forearm lying on the table toward the middle"""
    ox = cx + sgn * 44
    pts = [(ox - sgn * 6, shoulder_y + 6), (ox + sgn * 6, shoulder_y + 10), (ox + sgn * 10, cut + 2),
           (mouth_x + sgn * 4, mouth_y + width * 0.55), (mouth_x - sgn * 2, mouth_y + width * 0.5),
           (mouth_x - sgn * 3, mouth_y - width * 0.45), (ox - sgn * 12, cut - 18)]
    def shade(x, y):
        t = max(0.0, min(1.0, (y - shoulder_y) / (cut + 10 - shoulder_y)))
        axis_x = ox + (mouth_x - ox) * t * t
        u = max(-1, min(1, (x - axis_x) / 12.0))
        n = (u * 0.8, 0.3 + 0.5 * t, math.sqrt(max(0.0, 1 - 0.64 * u * u)))
        v = base + span * f.lit(n) + (nA(x * 2, y) - 0.5) * 0.5
        if (int(x * 0.7 + y * 0.9 * sgn) % 9) == 0 and t > 0.3: v -= 0.9                # sleeve creases
        return col(k, band(v, x, y))
    f.poly(pts, shade, 'sleeve')
    # the dark mouth of the sleeve
    for y in range(int(mouth_y - width * 0.42), int(mouth_y + width * 0.48)):
        for x in range(int(mouth_x - sgn * 4), int(mouth_x + sgn * 1) + (1 if sgn < 0 else 0), -sgn if sgn > 0 else 1):
            pass
    for y in range(int(mouth_y - width * 0.4), int(mouth_y + width * 0.45)):
        e = abs((y - mouth_y) / (width * 0.45))
        for i in range(0, 4 - int(e * 3)):
            f.put(mouth_x - sgn * (2 + i), y, col(k, 0), 'sleeve')

def hand(f, x, y, sgn, k='K', base=2.0, span=5.0, ring=False, fingers=4, length=7):
    """an old hand lying on the table, fingers pointing toward the middle (sgn = direction)"""
    for yy in range(y - 4, y + 5):
        for xx in range(x - 6, x + 7):
            u, w = (xx - x) / 6.5, (yy - y) / 4.5
            if u * u + w * w > 1: continue
            n = (u * 0.5, w * 0.6 + 0.4, 0.8)
            f.put(xx, yy, col(k, base + span * f.lit(n) * 0.9), 'hand')
    for i in range(fingers):
        fy = y - 3 + i * 2 + (1 if i == fingers - 1 else 0)
        ln = length - abs(i - 1.3) * 1.2
        for j in range(int(ln)):
            fx = x + sgn * (5 + j)
            f.put(fx, fy, col(k, base + span * 0.6 - (1 if j == int(ln) - 1 else 0)), 'hand')
        f.put(x + sgn * (5 + int(ln)), fy, col(k, 1), 'hand')
        if i < fingers - 1:
            for j in range(int(ln) - 1): f.put(x + sgn * (5 + j), fy + 1, col(k, base - 0.5), 'hand')
    if ring: f.put(x + sgn * 7, y - 1, col('G', 6), 'hand'); f.put(x + sgn * 8, y - 1, col('G', 4), 'hand')

def hood(f, cx, cy, rx, ry, k, base, span, open_rx, open_ry, ocy):
    """a hood around the head with an oval opening (left dark for the face to be drawn into)"""
    f.dome(cx, cy, rx, ry, k, base, span, 'hood', tex=0.5)
    for y in range(int(cy), int(cy + ry * 1.25)):                                                 # hood drape onto shoulders
        t = (y - cy) / (ry * 1.25)
        hw = rx * (1.0 + 0.45 * t)
        for x in range(int(cx - hw), int(cx + hw) + 1):
            if (x, y) in f.px and f.part[(x, y)] != 'hood': continue
            u = (x - cx) / hw
            v = base + span * f.lit((u, 0.3, math.sqrt(max(0.0, 1 - u * u)))) - t * 0.6
            f.put(x, y, col(k, band(v, x, y)), 'hood')
    for y in range(int(ocy - open_ry) - 2, int(ocy + open_ry) + 3):                               # the inside of the opening
        for x in range(int(cx - open_rx) - 2, int(cx + open_rx) + 3):
            u, w = (x - cx) / (open_rx + 2), (y - ocy) / (open_ry + 2)
            if u * u + w * w <= 1:
                f.put(x, y, col(k, 0) if u * u + w * w > 0.86 else INK, 'hoodin')

def face(f, cx, cy, rx, ry, k='K', base=1.4, span=5.2):
    f.dome(cx, cy, rx, ry, k, base, span, 'face', tex=0.4)

def shade_hood_edge(f, cx, ocy, open_rx, open_ry, k):
    """thin lit rim along the bottom of the hood opening"""
    for a in range(20, 161, 4):
        x = cx + (open_rx + 2) * math.cos(math.radians(a)); y = ocy + (open_ry + 2) * math.sin(math.radians(a))
        f.put(x, y, col(k, 5), 'hood')

# ============================================================== back row
def back_fig(name):
    ax, ay = seat_anchor(name)
    top = ay - FRAME_H
    x0 = ax - FRAME_W // 2
    lx = max(-0.6, min(0.6, (POOL['cx'] - ax) / 380.0))
    f = Fig(FRAME_W, FRAME_H, (lx, 0.62, 0.78))
    cut = lambda fx: back_edge_y(x0 + fx) - top
    return f, cut

def ink_cap(f, cx, base_y, rx, height, drip, lean=-3):
    """Varhun's crown: a young shaggy ink cap -- a tall cream bell with a tan crown and a shaggy silhouette, its rim
    flaring, blackening and melting into ink that runs down onto the hood (growth and decay in one crown)"""
    top = base_y - height
    for y in range(top, base_y + 1):
        t = (y - top) / height
        hw = rx * (1 - (1 - t) ** 2.2) ** 0.5 * (1 - 0.06 * t)
        if t > 0.2: hw += (nC(y * 3.1, 7) - 0.5) * 2.6                                      # shaggy silhouette
        if t > 0.84: hw += (t - 0.84) / 0.16 * 4.5                                          # the rim flares as it melts
        mx = cx + lean * (1 - t) ** 1.5
        for x in range(int(mx - hw) - 1, int(mx + hw) + 2):
            if abs(x - mx) > hw: continue
            if t > 0.9 and (h32(x, 77) % 5 == 0) and y > base_y - 2: continue                  # frayed edge
            u = max(-1.0, min(1.0, (x - mx) / max(1.0, hw)))
            n = (u, -0.55 + 0.6 * t, math.sqrt(max(0.0, 1 - u * u)))
            L = f.lit(n, 0.35)
            if t > 0.88: f.put(x, y, col('R', 0.6 + (1.6 if abs(u) < 0.5 and (x + y) % 4 == 0 else 0)), 'ink'); continue
            if t > 0.8: f.put(x, y, col('R', 2.4 + L * 1.6), 'ink'); continue
            if t > 0.72: f.put(x, y, col('I', 2.6 + L * 2.4), 'cap'); continue
            if t < 0.16: f.put(x, y, col('O', band(3.2 + 3.0 * L, x, y)), 'cap'); continue      # tan crown
            v = 3.4 + 4.6 * L + (nB(x * 3, y * 0.4) - 0.5) * 1.0
            if nF(x * 2.3 + 9, y * 1.9) > 0.8:                                                   # brown flakes, lit tip
                f.put(x, y, col('O', 3.0 + L)); f.put(x, y - 1, col('C', min(8.6, v + 1.5)), 'cap'); continue
            f.put(x, y, col('C', band(min(8.4, v), x, y)), 'cap')
    # ink running down from the rim onto the hood
    x0 = int(cx - rx - 4)
    for i, ln in enumerate(drip):
        x = x0 + i
        if ln < 3 or (x, base_y) not in f.px: continue
        for k in range(ln):
            q = (x, base_y + 1 + k)
            if f.part.get(q) in ('face', 'eye', 'glow', 'beard', 'hoodin'): break
            f.put(x, base_y + 1 + k, col('R', 0.5), 'ink')
            f.put(x - 1, base_y + 1 + k, col('I', 2.6), 'ink') if k < ln - 1 and f.part.get((x - 1, base_y + 1 + k)) == 'hood' else None
        f.put(x, base_y + ln + 1, col('R', 3.0), 'ink')

def draw_varhun(st):
    f, cut = back_fig('varhun')
    cx = 64; b = -st['breath']
    hcy = 82 + b                                                     # head centre
    robe_body(f, cx, hcy + 22, 160, 40, 46, 'P', 1.0, 5.0, (-30, -20, 20, 31))
    # gold stole down the front
    for sgn in (-1, 1):
        def stole(x, y, sgn=sgn):
            t = (y - (hcy + 22))
            v = 1.6 + 2.6 * f.lit((sgn * 0.2, 0.2, 0.95)) + (nB(x, y) - 0.5) * 0.6
            if (y - hcy) % 9 in (0,) : v -= 1.6
            ex = abs(x - (cx + sgn * 13)); ey = (y - hcy - 4) % 9 - 4
            if abs(math.hypot(ex, ey) - 2.2) < 0.7: v += 2.2
            return col('G', band(v, x, y))
        xi, xo = cx + sgn * 8, cx + sgn * 18
        f.poly([(cx + sgn * 6, hcy + 22), (cx + sgn * 14, hcy + 22), (xo, 160), (xi, 160)], stole, 'stole')
    hood(f, cx, hcy - 3, 26, 27, 'P', 0.8, 5.0, 15, 18, hcy + 2)
    # the face: right half old human, left half (viewer's right) fungal
    fcx, fcy = cx, hcy + 3
    face(f, fcx, fcy, 13, 17)
    for y in range(fcy - 17, fcy + 18):
        for x in range(fcx, fcx + 15):
            q = (x, y)
            if f.part.get(q) != 'face': continue
            u, w = (x - fcx) / 13, (y - fcy) / 17
            n = (u, w, math.sqrt(max(0.0, 1 - u * u - w * w)))
            g = nA(x * 3.0, y * 1.2)
            v = 1.6 + 4.0 * f.lit(n) + (0.9 if abs((g * 5) % 1 - 0.5) < 0.12 else 0)          # gill ridges
            if x - fcx < 2 + 2 * math.sin(y / 3.0): continue                                    # ragged seam
            f.put(x, y, col('C', band(v, x, y)), 'fungal')
    # shelf fungi sprouting from the fungal cheek and temple
    for (sx, sy, r) in ((fcx + 12, fcy + 3, 6), (fcx + 14, fcy - 6, 4), (fcx + 10, fcy + 11, 4)):
        for y in range(sy - 2, sy + 2):
            for x in range(sx - 1, sx + r + 1):
                u = (x - sx) / (r + 0.5); w = (y - sy + 0.5) / 2.2
                if u >= 0 and u * u + w * w <= 1:
                    f.put(x, y, col('C', 6.5 if y == sy - 2 else 4.6 if y < sy + 1 else 3), 'fungal')
        f.put(sx + r, sy, INK)
    # eyes: human eye (viewer's left) deep-set with a brow; the fungal eye a glowing pore
    ey = fcy - 3
    blink = st['blink']
    for x in range(fcx - 9, fcx - 2): f.put(x, ey - 3, col('K', 1), 'brow')                      # brow shadow
    for x in range(fcx - 10, fcx - 2): f.put(x, ey - 4, col('K', 6) if x % 2 else col('I', 8), 'brow')  # white bushy brow
    if blink:
        for x in range(fcx - 8, fcx - 3): f.put(x, ey, col('K', 1), 'eye')
    else:
        for x in range(fcx - 8, fcx - 3): f.put(x, ey - 1, col('K', 1), 'eye'); f.put(x, ey + 1, col('K', 2), 'eye')
        f.put(fcx - 7, ey, col('I', 7), 'eye'); f.put(fcx - 6, ey, col('M', 1), 'eye'); f.put(fcx - 5, ey, INK, 'eye'); f.put(fcx - 4, ey, col('I', 6), 'eye')
    gl = 6 + st['glow']
    for (dx, dy, dv) in ((5, 0, 0), (6, 0, 0), (5, -1, -1), (6, 1, -1), (4, 0, -2), (7, 0, -2), (5, 1, -1), (6, -1, -1)):
        f.put(fcx + dx, ey + dy, col('M', gl + dv), 'glow')
    # nose (human side lit from below), mouth, beard
    for y in range(ey + 1, ey + 9): f.put(fcx - 1, y, col('K', 2), 'face')
    f.put(fcx - 2, ey + 9, col('K', 7), 'face'); f.put(fcx - 1, ey + 9, col('K', 7), 'face'); f.put(fcx - 3, ey + 8, col('K', 2), 'face')
    my = ey + 13
    m = st['mouth']
    beard_top = my + 1
    for y in range(beard_top, fcy + 30):                                                           # long thin pale beard
        t = (y - beard_top) / (fcy + 30 - beard_top)
        hw = 9 * (1 - t) + 2
        for x in range(int(fcx - 2 - hw), int(fcx + 2 + hw * 0.4) + 1):
            v = 4.0 + 3.6 * (1 - t) + (2.0 if (x + y // 2) % 3 == 0 else 0) - (1.6 if abs(x - fcx) > hw - 1 else 0)
            f.put(x, y, col('I', min(8, v)), 'beard')
    for x in range(fcx - 6, fcx + 4):                                                             # mustache
        f.put(x, my - 1, col('I', 6 if x % 2 else 7), 'beard')
    for x in range(fcx - 4, fcx + 3):
        f.put(x, my, INK if m else col('K', 1), 'mouth')
    for y in range(my + 1, my + 1 + m):
        for x in range(fcx - 3 + (y - my > 1), fcx + 2 - (y - my > 1)): f.put(x, y, col('X', 1), 'mouth')
    if m: f.put(fcx - 3, my + m, col('K', 2), 'mouth')
    shade_hood_edge(f, cx, hcy + 2, 15, 18, 'P')
    ink_cap(f, cx, hcy - 20, 17, 48, [0, 0, 0, 3, 0, 9, 0, 0, 5, 0, 0, 0, 13, 0, 0, 4, 0, 0, 0, 0, 7, 0, 0, 11, 0, 0, 3, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0])
    f.cut_below(cut)
    # sleeves and old hands on the table
    for sgn in (-1, 1):
        lift = st['gesture'] if sgn < 0 else 0
        sleeve(f, sgn, cx, hcy + 34, cut(cx + sgn * 44), 'P', 1.0, 4.6, cx + sgn * 24, 160 - lift, 15)
    hand(f, cx - 16, 160 - st['gesture'], 1, ring=True)
    hand(f, cx + 16, 161, -1)
    f.outline()
    return f

def draw_tynri(st):
    f, cut = back_fig('tynri')
    cx = 64; b = -st['breath']
    hcy = 88 + b
    robe_body(f, cx, hcy + 20, 158, 36, 42, 'I', 1.4, 5.6, (-24, -8, 10, 26))
    hood(f, cx, hcy - 2, 22, 24, 'I', 1.2, 5.6, 12, 16, hcy + 2)
    fcx, fcy = cx, hcy + 2
    face(f, fcx, fcy, 10, 15, 'K', 2.6, 5.0)                                            # pale narrow face
    # sharp cheek shadows
    for y in range(fcy + 1, fcy + 8):
        f.put(fcx - 7, y, col('K', 3), 'face'); f.put(fcx + 7, y, col('K', 3), 'face')
    ey = fcy - 3
    # the eyes are two small yellow fruiting bodies growing out of the sockets
    for sgn in (-1, 1):
        sx = fcx + sgn * 4
        f.put(sx, ey + 1, col('K', 0), 'eye'); f.put(sx - sgn, ey + 1, col('K', 1), 'eye'); f.put(sx + sgn, ey + 1, col('K', 1), 'eye')
        if st['blink']:
            continue
        stem = [(sx, ey), (sx, ey - 1), (sx + sgn, ey - 2), (sx + sgn, ey - 3)]
        for (x, y) in stem: f.put(x, y, col('Y', 2), 'eyeshroom'); f.put(x - sgn, y, col('Y', 1), 'eyeshroom')
        capx, capy = sx + sgn * 1, ey - 5
        g = st['glow'] // 2
        for dx in range(-3, 4): f.put(capx + dx, capy, col('Y', 4 + g - (1 if abs(dx) == 3 else 0)), 'eyeshroom')
        for dx in range(-2, 3): f.put(capx + dx, capy - 1, col('Y', 5 if dx != sgn * 2 else 4), 'eyeshroom')
        for dx in range(-1, 2): f.put(capx + dx, capy - 2, col('Y', 5), 'eyeshroom')
        for dx in range(-3, 4): f.put(capx + dx, capy + 1, col('Y', 0) if abs(dx) < 3 else col('Y', 1), 'eyeshroom')
    # thin nose, pursed lips
    for y in range(ey + 2, ey + 8): f.put(fcx, y, col('K', 4), 'face')
    f.put(fcx + 1, ey + 8, col('K', 2), 'face'); f.put(fcx, ey + 8, col('K', 7), 'face')
    my = ey + 11; m = st['mouth']
    for x in range(fcx - 3, fcx + 4): f.put(x, my, col('X', 3) if abs(x - fcx) < 3 else col('K', 2), 'mouth')
    if m:
        for x in range(fcx - 2, fcx + 2): f.put(x, my + 1, INK, 'mouth')
        if m > 1:
            for x in range(fcx - 1, fcx + 2): f.put(x, my + 2, col('X', 1), 'mouth')
    f.put(fcx + 4, my - 1, col('K', 3), 'mouth')                                                       # a sardonic corner
    shade_hood_edge(f, cx, hcy + 2, 12, 16, 'I')
    # bell cap: a dark olive stinkhorn head with a slimy sheen, and the lace veil hanging from it
    bcy = hcy - 24
    for y in range(bcy - 22, bcy + 8):
        t = (y - (bcy - 22)) / 30.0
        hw = 6 + 18 * math.sqrt(max(0.0, t)) * (1 - 0.15 * t)
        for x in range(int(cx - hw), int(cx + hw) + 1):
            u = (x - cx) / hw
            n = (u, -0.4 + t * 0.6, math.sqrt(max(0.0, 1 - u * u)))
            cell = (int((x + 0.5 * y) / 4) + int(y / 3)) % 2
            v = 1.2 + 3.4 * f.lit(n, 0.3) + cell * 0.6
            if abs(u) > 0.9: v -= 0.8
            f.put(x, y, col('S', band(v, x, y)), 'cap')
    for (gx, gy) in ((cx - 8, bcy - 10), (cx - 7, bcy - 11), (cx + 4, bcy - 4), (cx - 3, bcy - 16)):
        f.put(gx, gy, col('S', 7), 'cap')
    f.put(cx, bcy - 23, col('S', 3), 'cap')
    # the lace veil: from the cap rim down over the hood and shoulders
    vtop = bcy + 6
    for y in range(vtop, 150):
        t = (y - vtop) / (150 - vtop)
        hw = 24 + 30 * t
        for x in range(int(cx - hw), int(cx + hw) + 1):
            if abs(x - cx) < 15 - t * 4 and y < hcy + 22: continue                                # leave the face clear
            if f.part.get((x, y)) in ('face', 'eye', 'eyeshroom', 'mouth'): continue
            if ((x + y) % 6 == 0 or (x - y) % 6 == 0) and y % 1 == 0:
                f.put(x, y, col('I', 8 if t < 0.5 else 7), 'veil')
        if abs(int(hw) - (y % 3)) >= 0:
            f.put(cx - hw, y, col('I', 7), 'veil'); f.put(cx + hw, y, col('I', 6), 'veil')
    f.cut_below(cut)
    for sgn in (-1, 1):
        sleeve(f, sgn, cx, hcy + 32, cut(cx + sgn * 44), 'I', 1.4, 5.0, cx + sgn * 20, 160, 14)
    # long thin fingers steepled near the middle
    hand(f, cx - 12, 159, 1, base=2.4, span=5.0, fingers=4, length=9)
    hand(f, cx + 12, 160, -1, base=2.4, span=5.0, fingers=4, length=9)
    f.outline()
    return f

def draw_rhull(st):
    f, cut = back_fig('rhull')
    cx = 64; b = -st['breath']
    hcy = 90 + b
    robe_body(f, cx, hcy + 19, 158, 38, 44, 'S', 1.0, 5.6, (-26, -12, 6, 22))
    hood(f, cx, hcy - 1, 21, 22, 'S', 1.0, 5.6, 13, 15, hcy + 2)
    fcx, fcy = cx, hcy + 2
    face(f, fcx, fcy, 11, 14, 'K', 2.0, 5.6)
    ey = fcy - 2
    # young eyes (a nervous glance to the side), soft brows
    for sgn in (-1, 1):
        ex = fcx + sgn * 5
        for x in range(ex - 2, ex + 2): f.put(x, ey - 3, col('O', 3), 'brow')
        if st['blink']:
            for x in range(ex - 2, ex + 2): f.put(x, ey, col('K', 1), 'eye')
        else:
            f.put(ex - 2, ey, col('I', 7), 'eye'); f.put(ex - 1, ey, col('I', 8), 'eye')
            f.put(ex, ey, INK, 'eye'); f.put(ex + 1, ey, col('O', 4), 'eye')
            f.put(ex - 1, ey - 1, col('K', 2), 'eye'); f.put(ex, ey - 1, col('K', 2), 'eye')
    # nose, a lopsided smirk
    f.put(fcx, ey + 4, col('K', 3), 'face'); f.put(fcx, ey + 5, col('K', 3), 'face'); f.put(fcx - 1, ey + 6, col('K', 2), 'face'); f.put(fcx, ey + 6, col('K', 7), 'face')
    my = ey + 9; m = st['mouth']
    for x in range(fcx - 3, fcx + 4): f.put(x, my - (1 if x == fcx + 3 else 0), col('K', 1) if not m else INK, 'mouth')
    for y in range(my + 1, my + 1 + m):
        for x in range(fcx - 2, fcx + 3): f.put(x, y, col('X', 1) if y < my + m else col('X', 3), 'mouth')
    # a patch of white mycelial fuzz on the cheek (the first sign of the change)
    for (dx, dy) in ((6, 3), (7, 3), (7, 4), (8, 4), (6, 5), (8, 2), (5, 4)):
        f.put(fcx + dx, fcy + dy, col('I', 8), 'face')
    shade_hood_edge(f, cx, hcy + 2, 13, 15, 'S')
    # a small round button cap
    f.dome(cx, hcy - 21, 17, 11, 'C', 2.4, 4.4, 'cap', half='top', tex=0.4)
    for x in range(cx - 17, cx + 18):
        f.put(x, hcy - 21, col('C', 6.5), 'cap'); f.put(x, hcy - 20, col('M', 3) if abs(x - cx) < 14 else col('C', 2), 'capunder')
    for (sx, sy) in ((cx - 6, hcy - 28), (cx + 5, hcy - 25), (cx - 11, hcy - 24), (cx + 1, hcy - 30)):
        f.put(sx, sy, col('C', 3), 'cap')
    # little orange mushrooms on the shoulder
    for (sx, sy) in ((cx + 32, hcy + 28), (cx + 37, hcy + 30), (cx + 28, hcy + 30)):
        f.put(sx, sy + 1, col('C', 5), 'shroom'); f.put(sx, sy + 2, col('C', 4), 'shroom')
        for dx in (-1, 0, 1): f.put(sx + dx, sy, col('G', 4 if dx else 5), 'shroom')
    f.cut_below(cut)
    # the minute-book open on the table
    bx, by = cx, 162
    for y in range(by - 6, by + 8):
        for x in range(bx - 18, bx + 19):
            t = (y - by + 6) / 14
            if abs(x - bx) > 17 - t * 1: continue
            v = 7 - abs(x - bx) / 18 * 1.5 - (2.5 if abs(x - bx) < 1 else 0)
            if (y - by) % 3 == 0 and 3 < abs(x - bx) < 15 and (x * 7 + y) % 5: v -= 2.2       # lines of minutes
            f.put(x, y, col('C', v), 'book')
    for x in range(bx - 19, bx + 20): f.put(x, by + 8, col('O', 2), 'book')
    for sgn in (-1, 1):
        sleeve(f, sgn, cx, hcy + 30, cut(cx + sgn * 44), 'S', 1.0, 5.0, cx + sgn * 30, 160, 14)
    hand(f, cx - 22, 160, 1, base=2.2, span=5.4, length=6)
    # right hand holds a quill
    hand(f, cx + 22, 158 - st['gesture'], -1, base=2.2, span=5.4, length=6)
    for i in range(14):
        f.put(cx + 18 - i // 2, 156 - st['gesture'] - i, col('I', 8 if i > 6 else 6), 'quill')
        if i > 6: f.put(cx + 19 - i // 2, 156 - st['gesture'] - i, col('I', 5), 'quill')
    f.outline()
    return f

# ============================================================== the elders at the table's ends (drawn facing right)
def elder_body(f, k, base, span, b):
    """big seated robe seen three-quarter, turned toward the table on the right; cropped by the frame bottom"""
    pts = [(84, 118 + b), (138, 118 + b), (160, 132 + b), (176, 156 + b), (186, 214), (194, END_H + 2), (6, END_H + 2),
           (14, 220), (26, 168 + b), (50, 136 + b)]
    def shade(x, y):
        u = max(-1, min(1, (x - 104) / 86.0))
        n = (u, 0.1 + 0.3 * max(0, (y - 240) / 100), math.sqrt(max(0.0, 1 - u * u)))
        v = base + span * f.lit(n, 0.12) + (nA(x * 0.8, y * 0.35) - 0.5) * 0.7
        for fx in (-62, -40, -18, 6, 30, 58):
            fxx = 104 + fx + 3 * math.sin(y / 17 + fx)
            if abs(x - fxx) < 1.2 and y > 160: v -= 1.4
            elif 1.2 <= x - fxx < 3.4 and y > 160: v += 0.6
        if y > 300: v -= (y - 300) / 50 * 1.2                                         # sinks into the dark below
        return col(k, band(v, x, y))
    f.poly(pts, shade, 'robe')

def elder_hood(f, hx, hy, k, base, span, ox, oy, orx, ory):
    f.dome(hx, hy, 36, 40, k, base, span, 'hood', tex=0.6)
    for y in range(int(oy - ory) - 2, int(oy + ory) + 3):
        for x in range(int(ox - orx) - 2, int(ox + orx) + 3):
            u, w = (x - ox) / (orx + 2), (y - oy) / (ory + 2)
            if u * u + w * w <= 1:
                f.put(x, y, col(k, 0) if u * u + w * w > 0.84 else INK, 'hoodin')

def rim(f, k, top_v=7):
    """green rim light from the pool along the right-hand edge of the silhouette"""
    for (x, y), c in list(f.px.items()):
        if (x + 1, y) not in f.px and f.part.get((x, y)) not in ('outline', 'glow', 'eye'):
            f.px[(x, y)] = col('M', 3 if y > 200 else 4)
            if (x - 1, y) in f.px and f.part.get((x - 1, y)) not in ('glow', 'eye'): f.px[(x - 1, y)] = col('M', 2)

def draw_elder_l(st):
    """asleep under a huge spotted parasol cap, arms folded in the sleeves"""
    f = Fig(END_W, END_H, (0.8, 0.45, 0.4))
    b = st['breath']
    hx, hy = 112, 96 + b + st.get('nod', 0)
    elder_body(f, 'B', 0.0, 2.6, b)
    elder_hood(f, hx, hy, 'B', 0.4, 4.0, hx + 14, hy + 10, 16, 21)
    # closed eyes: two dim slits low in the void (head drooped)
    for sgn in (-1, 1):
        ex = hx + 14 + sgn * 7
        for dx in range(-2, 3): f.put(ex + dx, hy + 14 + (1 if abs(dx) == 2 else 0), col('G', 2 + st['glow'] // 2), 'eye')
    # folded arms: the sleeves meet in front of the belly
    for y in range(180 + b, 246 + b):
        for x in range(22, 184):
            yc = 206 + b + (x - 100) * 0.12 + 10 * ((x - 100) / 82.0) ** 2
            u = (y - yc) / (24 - 6 * ((x - 100) / 82.0) ** 2)
            if abs(u) > 1 or abs(x - 100) > 82 - 4 * abs(u): continue
            n = (0.25, u * 0.9, math.sqrt(max(0.0, 1 - u * u * 0.8)))
            v = 0.3 + 3.0 * f.lit(n, 0.12) + (nA(x, y) - 0.5) * 0.6
            if abs(x - 104) < 2: v = 0.6                                                    # where the sleeves meet
            if (x * 3 + y * 2) % 23 == 0: v -= 1
            f.put(x, y, col('B', band(v, x, y)), 'sleeve')
    # a cord belt with a spore pouch
    for x in range(30, 182): f.put(x, 250 + int(2 * math.sin(x / 20)), col('C', 3 if x % 4 else 5), 'belt')
    f.dome(140, 268, 9, 11, 'C', 1.2, 4, 'pouch', tex=0.6)
    # the parasol cap: wide, flat, tilted forward over the sleeping face, pale scales/spots, gills lit from below
    ccx, ccy, crx, cry = hx + 8, hy - 34, 76, 22
    tilt = math.radians(10 + st.get('nod', 0) * 2)
    for y in range(int(ccy - cry - 20), int(ccy + cry + 20)):
        for x in range(int(ccx - crx - 10), int(ccx + crx + 10)):
            dx, dy = x - ccx, y - ccy
            rx_ = dx * math.cos(tilt) + dy * math.sin(tilt); ry_ = -dx * math.sin(tilt) + dy * math.cos(tilt)
            u, w = rx_ / crx, ry_ / cry
            if w <= 0.15:
                d = u * u + min(0.0, w) ** 2
                prof = -(1 - abs(u) ** 2.2) ** 0.6 - 0.25 * math.exp(-(u / 0.15) ** 2)
                if abs(u) > 1 or w < prof: continue
                if w > 0:
                    if abs(u) < 0.96: f.put(x, y, col('M', 3.6 - abs(u) * 2 + (0.8 if int(rx_) % 3 == 0 else 0)), 'capunder'); continue
                n = (u, -0.6 + 0.6 * (w - prof), 0.6)
                v = 1.6 + 4.6 * f.lit(n, 0.3) + (nB(x, y) - 0.5) * 0.6
                spot = nC(rx_ * 0.5 + 99, ry_ * 0.9 + 9)
                if spot > 0.78 and w < -0.12: f.put(x, y, col('C', 7.5 if spot > 0.86 else 6), 'cap'); continue
                f.put(x, y, col('X', band(v, x, y)), 'cap')
    rim(f, 'B')
    f.outline()
    return f

def draw_elder_r(st):
    """awake, a tall honeycombed morel cap, amber eyes in the dark of the hood, a crook with a glowing bulb"""
    f = Fig(END_W, END_H, (0.8, 0.45, 0.4))
    b = st['breath']
    hx, hy = 106, 92 + b
    elder_body(f, 'X', 0.0, 2.5, b)
    elder_hood(f, hx, hy, 'X', 0.3, 3.8, hx + 15, hy + 4, 15, 22)
    for sgn in (-1, 1):                                                                       # amber eyes
        ex, ey = hx + 15 + sgn * 6, hy + 1
        if st['blink']:
            for dx in range(-1, 2): f.put(ex + dx, ey + 1, col('G', 3), 'eye')
        else:
            f.put(ex, ey, col('G', 7), 'eye'); f.put(ex + 1, ey, col('G', 6), 'eye')
            f.put(ex, ey + 1, col('G', 5), 'eye'); f.put(ex + 1, ey + 1, col('G', 4), 'eye')
    # a liberty cap: tall conical, radially striated, a sharp nipple on top
    mcx, mby = hx + 2, hy - 26
    for y in range(mby - 66, mby + 4):
        t = (y - (mby - 66)) / 70.0
        hw = 1 + 34 * (t ** 0.85) * (1 - 0.12 * t) if t > 0.06 else 1.5
        for x in range(int(mcx - hw), int(mcx + hw) + 1):
            u = (x - mcx) / max(1.0, hw)
            n = (u, -0.5 + 0.6 * t, math.sqrt(max(0.0, 1 - u * u)))
            v = 1.4 + 4.0 * f.lit(n, 0.25) - (1.0 - t) * 1.2 + (nB(x, y) - 0.5) * 0.4
            if abs(math.sin(math.asin(max(-1, min(1, u))) * 9)) < 0.18 and t > 0.25: v -= 1.3       # striations
            if t > 0.93: v = 1.0 + 2.6 * f.lit(n, 0.3)                                             # inrolled rim
            f.put(x, y, col('G' if t < 0.5 else 'O', band(v - (1.6 if t < 0.5 else -1.0), x, y)), 'cap')
    for x in range(int(mcx - 34), int(mcx + 35)):
        if (x, mby + 4) in f.px: f.put(x, mby + 4, col('M', 3 - abs(x - mcx) / 20), 'capunder')

    # the crook in the near hand
    sx = 176
    for y in range(26, END_H):
        for dx in range(-2, 3):
            v = 3.2 - abs(dx) * 0.9 + (1.4 if dx == 1 else 0) - (y > 300) * 1.5 + (0.6 if (y // 5) % 4 == 0 else 0)
            f.put(sx + dx, y, col('O', v), 'staff')
    for a in range(0, 200, 4):                                                               # the curl at the top
        r = 13 - a / 40.0
        x = sx - 13 + r * math.cos(math.radians(a)); y = 26 - r * math.sin(math.radians(a)) * 1.1
        for dx in range(-2, 2):
            for dy in range(-1, 2): f.put(x + dx, y + dy, col('O', 3.4 + (dy < 0)), 'staff')
    # bulb hanging from the curl
    bx, by = sx - 22, 36
    f.put(bx, by - 4, col('O', 2), 'staff'); f.put(bx, by - 3, col('O', 2), 'staff')
    for y in range(by - 2, by + 6):
        for x in range(bx - 4, bx + 5):
            d = ((x - bx) / 4.2) ** 2 + ((y - by - 2) / 4.4) ** 2
            if d <= 1: f.put(x, y, col('M', 8 - d * 3 + st['glow'] * 0.3), 'glow')
    # the hand around the staff
    f.dome(sx - 2, 196 + b, 9, 8, 'K', 1.0, 4.4, 'hand')
    for i in range(4): f.put(sx + 3, 191 + b + i * 3, col('K', 2), 'hand'); f.put(sx + 4, 191 + b + i * 3, col('K', 4), 'hand')
    # sleeve reaching to the hand
    for y in range(150 + b, 206 + b):
        t = (y - 150 - b) / 56
        x0, x1 = int(150 + 6 * t), int(170 + 2 * t)
        for x in range(x0, x1):
            u = (x - (x0 + x1) / 2) / ((x1 - x0) / 2 + 0.1)
            v = 0.4 + 3.6 * f.lit((u, 0.2, 0.9), 0.12) + (nA(x, y) - 0.5) * 0.5
            f.put(x, y, col('X', band(v, x, y)), 'sleeve')
    rim(f, 'X')
    f.outline()
    return f

# ============================================================== frames
# 0 rest, 1 inhale (upper body 1px up), 2 blink, 3 rest with a stronger eye-glow; 4-7 talk (mouth only, body still)
IDLE = [dict(breath=0, mouth=0, blink=False, glow=0, gesture=0), dict(breath=1, mouth=0, blink=False, glow=0, gesture=0),
        dict(breath=0, mouth=0, blink=True, glow=0, gesture=0), dict(breath=0, mouth=0, blink=False, glow=2, gesture=0)]
TALK = [dict(breath=0, mouth=1, blink=False, glow=1, gesture=0), dict(breath=0, mouth=3, blink=False, glow=2, gesture=0),
        dict(breath=0, mouth=2, blink=False, glow=2, gesture=0), dict(breath=0, mouth=0, blink=False, glow=1, gesture=0)]

def sheet(name, drawer, states, fw, fh):
    os.makedirs(f'{OUT}/{name}', exist_ok=True)
    sh = Image.new('RGBA', (fw * len(states), fh), (0, 0, 0, 0))
    for i, st in enumerate(states):
        im = drawer(st).image()
        im.save(f'{OUT}/{name}/{i}.png')
        sh.paste(im, (i * fw, 0))
    sh.save(f'{OUT}/council_{name}.png')

if __name__ == '__main__':
    for name, fn in (('varhun', draw_varhun), ('tynri', draw_tynri), ('rhull', draw_rhull)):
        sheet(name, fn, IDLE + TALK, FRAME_W, FRAME_H)
    # 0 rest, 1 inhale, 2 the sleeper's head sinks / the waker's bulb glows, 3 blink
    E_IDLE = [dict(breath=0, glow=0, blink=False, nod=0), dict(breath=1, glow=1, blink=False, nod=0),
              dict(breath=0, glow=3, blink=False, nod=1), dict(breath=0, glow=1, blink=True, nod=0)]
    sheet('elder_l', draw_elder_l, E_IDLE, END_W, END_H)
    sheet('elder_r', draw_elder_r, E_IDLE, END_W, END_H)
    # a preview of everyone in their seats (locked layer in the chamber's Aseprite template)
    prev = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for name in ('tynri', 'varhun', 'rhull', 'elder_l', 'elder_r'):
        fr = Image.open(f'{OUT}/{name}/0.png')
        if name == 'elder_r': fr = fr.transpose(Image.FLIP_LEFT_RIGHT)
        ax, ay = seat_anchor(name)
        prev.alpha_composite(fr, (ax - fr.width // 2, ay - fr.height))
    prev.save(f'{OUT}/council_preview.png')
    print('ok')
