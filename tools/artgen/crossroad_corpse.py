"""The dead demigod v3 — full figure: red hooded robe to mid-shin, bony shins and feet, hands at the hips, impaled on a
stake (splintered tip out of the chest). Instead of a mushroom-cloud cap the head continues upward into an elongated,
surreal-but-anatomical cranium: a stretched brain-like form with sulci, a suture, a cleft crown. 3 frames 240x440."""
import sys, math, random
from PIL import Image, ImageDraw
from pal_day import *
OUT = sys.argv[1]
FW, FH = 240, 440
MX, FEET = 120, 436
nA, nB, nC = make_noise(14, 4, FW, FH), make_noise(6, 5, FW, FH), make_noise(3, 6, FW, FH)
HEM, SHOULDER, HOOD_TOP = 398, 262, 232          # robe hem / shoulder line / top of the hood
HEAD_CY, HEAD_RX, HEAD_RY = 190, 27, 46          # the elongated cranium (ellipse-ish, leaning a little)

def new(): return {}, {}
def fill_poly(PIX, PART, pts, name, shade):
    tmp = Image.new('1', (FW, FH), 0); ImageDraw.Draw(tmp).polygon(pts, fill=1); tp = tmp.load()
    for y in range(FH):
        for x in range(FW):
            if tp[x, y]: PIX[(x, y)] = shade(x, y); PART[(x, y)] = name

def legs(PIX, PART):
    # bony shins + feet showing under the hem (the robe is torn short)
    for sgn in (-1, 1):
        cx = MX + sgn * 13
        for y in range(HEM - 6, FEET - 6):
            for x in range(cx - 6, cx + 7):
                nx = (x - cx) / 6.0
                v = 2.2 - 1.6 * nx * nx - 1.0 * max(0.0, (y - 420) / 16) + (nB(x, y) - 0.5) * 0.5
                PIX[(x, y)] = ['B', band(v, x, y)]; PART[(x, y)] = 'leg'
        for y in range(FEET - 7, FEET + 1):                                                # foot: a wedge pointing outward
            ln = 9 + (y - (FEET - 7)) * 2
            for x in range(cx - 6, cx + 6 + sgn * 0 + 1):
                PIX[(x, y)] = ['B', 1 if y > FEET - 2 else 2]; PART[(x, y)] = 'leg'
            for i in range(ln):
                x = cx + sgn * (6 + i)
                PIX[(x, y)] = ['B', 1 if y > FEET - 2 or i > ln - 3 else 2]; PART[(x, y)] = 'leg'
        for i in range(3):                                                                 # toes
            x = cx + sgn * (6 + 9 + 2 * 2 + 4 + i * 3)
            PIX[(x, FEET)] = ['B', 0]; PART[(x, FEET)] = 'leg'

def robe(PIX, PART):
    L = [(MX - 30, HOOD_TOP + 16), (MX - 44, SHOULDER), (MX - 52, SHOULDER + 40), (MX - 56, SHOULDER + 90), (MX - 58, HEM - 10)]
    R = [(MX + 30, HOOD_TOP + 16), (MX + 44, SHOULDER), (MX + 52, SHOULDER + 40), (MX + 56, SHOULDER + 90), (MX + 58, HEM - 10)]
    rnd = random.Random(3); hem = []; x = MX - 58
    while x < MX + 58:
        hem.append((x, HEM - rnd.randint(0, 9))); x += rnd.randint(4, 9)
    pts = L + hem + list(reversed(R))
    def shade(x, y):
        nx = (x - MX) / 56.0
        v = 2.9 - 1.5 * nx * nx - 1.3 * max(0.0, (y - 300) / 110) + (nA(x, y) - 0.5) * 0.8
        if y < SHOULDER + 4: v -= 1.2 * (1 - (y - (HOOD_TOP + 16)) / 18)                  # shadow under the head
        for fx in (-38, -22, -6, 12, 28, 44):
            fxx = MX + fx + 3 * math.sin((y - 300) / 23 + fx)
            if abs(x - fxx) < 1.5 and y > SHOULDER + 14: v -= 1.4
            elif 1.5 <= x - fxx < 3.5 and y > SHOULDER + 14: v += 0.5
        if y > HEM - 12: v -= 1.0
        return ['R', band(v, x, y)]
    fill_poly(PIX, PART, pts, 'robe', shade)
    # arm seams, sleeve mouths and bony hands at the hips
    for sgn in (-1, 1):
        for y in range(SHOULDER + 14, SHOULDER + 112):
            x = MX + sgn * (40 + (y - SHOULDER - 14) * 0.14)
            k = (int(x), y)
            if k in PIX: PIX[k] = ['R', 1]
        my = SHOULDER + 108
        for y in range(my, my + 12):
            for x in range(int(MX + sgn * 46) - 10, int(MX + sgn * 46) + 11):
                if (x, y) in PIX and abs(x - (MX + sgn * 48)) < 10 - (y - my) * 0.5: PIX[(x, y)] = ['R', 0]
        hx0 = MX + sgn * 48; hy = my + 12
        for y in range(hy, hy + 20):
            for x in range(hx0 - 7, hx0 + 8):
                d = ((x - hx0) / 7.0) ** 2 + ((y - hy - 6) / 8.0) ** 2
                if d <= 1: PIX[(x, y)] = ['B', 3 - int(d * 2) - (1 if y > hy + 10 else 0)]; PART[(x, y)] = 'hand'
        for i in range(4):
            fx = hx0 - 5 + i * 3 + (1 if sgn > 0 else 0)
            for y in range(hy + 14, hy + 24 - (i % 2) * 2):
                PIX[(fx, y)] = ['B', 1 if y > hy + 20 else 2]; PART[(fx, y)] = 'hand'; PIX[(fx + 1, y)] = ['B', 1]; PART[(fx + 1, y)] = 'hand'

def hood_face(PIX, PART):
    # hood: a dark cowl rising from the shoulders, open in front; the face inside, green-grey, skull-like
    pts = [(MX - 30, HOOD_TOP + 16), (MX - 22, HOOD_TOP), (MX + 22, HOOD_TOP), (MX + 30, HOOD_TOP + 16), (MX + 44, SHOULDER + 2), (MX - 44, SHOULDER + 2)]
    def shade(x, y):
        v = 2.4 - 1.2 * ((x - MX) / 40.0) ** 2 - 0.8 * max(0.0, (y - HOOD_TOP) / 30) + (nA(x, y) - 0.5) * 0.5
        return ['R', band(v, x, y)]
    fill_poly(PIX, PART, pts, 'hood', shade)
    FCY = HOOD_TOP + 22
    for y in range(FCY - 20, FCY + 26):
        for x in range(MX - 20, MX + 21):
            d = ((x - MX) / 18.0) ** 2 + ((y - FCY) / 23.0) ** 2
            if d <= 1:
                if d > 0.78: PIX[(x, y)] = ['R', 0]; PART[(x, y)] = 'hoodin'
                else:
                    v = 2.1 - 1.2 * d - 1.3 * max(0.0, (y - FCY - 8) / 16) + (nB(x, y) - 0.5) * 0.7
                    PIX[(x, y)] = ['B', band(v, x, y)]; PART[(x, y)] = 'face'
    for (ex, ey) in ((MX - 8, FCY - 6), (MX + 8, FCY - 6)):
        for y in range(ey - 5, ey + 6):
            for x in range(ex - 5, ex + 6):
                d = ((x - ex) / 5.0) ** 2 + ((y - ey) / 5.0) ** 2
                if d <= 1 and PART.get((x, y)) == 'face': PIX[(x, y)] = ['B', 0] if d < 0.6 else ['B', 1]
    for (x, y) in ((MX - 1, FCY + 4), (MX, FCY + 4), (MX + 1, FCY + 4), (MX - 1, FCY + 5), (MX, FCY + 6), (MX + 1, FCY + 5)):
        if PART.get((x, y)) == 'face': PIX[(x, y)] = ['B', 0]
    for x in range(MX - 9, MX + 10):
        y = FCY + 14 + abs(x - MX) // 5
        if PART.get((x, y)) == 'face': PIX[(x, y)] = ['B', 0]
        if PART.get((x, y - 1)) == 'face' and x % 3 == 0: PIX[(x, y - 1)] = ['B', 3]

def head(PIX, PART, cut=False):
    # the elongated cranium: stretched ellipse leaning slightly right, two lobes with a cleft at the crown, brain-like sulci
    def inside(x, y):
        lean = (HEAD_CY - y) * 0.08
        nx = (x - MX - lean) / HEAD_RX; ny = (y - HEAD_CY) / HEAD_RY
        # pinch the waist where the two lobes meet, and a cleft at the top
        w = 1.0 - 0.10 * math.exp(-((ny + 0.25) / 0.25) ** 2)
        cleft = 0.34 * max(0.0, -ny - 0.55) * (1 - min(1.0, abs(nx) * 2.2))
        d = (nx / w) ** 2 + (ny + cleft) ** 2 * (1.0 if ny > 0 else 1.0)
        return d, nx, ny
    for y in range(HEAD_CY - HEAD_RY - 4, HEAD_CY + HEAD_RY + 6):
        for x in range(MX - HEAD_RX - 8, MX + HEAD_RX + 10):
            if not (0 <= x < FW and 0 <= y < FH): continue
            d, nx, ny = inside(x, y)
            if d > 1: continue
            if cut and y < HEAD_CY - 6: continue
            nz = math.sqrt(max(0.0, 1 - d))
            lam = max(0.0, -ny * 0.5 + nz * 0.65 - nx * 0.5)
            v = 1.2 + 4.3 * lam + (nC(x, y) - 0.5) * 0.5
            # sulci: meandering grooves from banded noise
            g = nA(x * 2.4 + 3, y * 1.5)
            if abs((g * 4) % 1 - 0.5) < 0.055 and d < 0.93: v -= 2.6
            elif abs((g * 4) % 1 - 0.5) < 0.1 and d < 0.93: v -= 1.0
            if abs(nx) < 0.04 and ny < 0.3: v -= 1.6                                       # the suture down the middle
            if d > 0.9: v -= 0.8
            PIX[(x, y)] = ['C', band(v, x, y)]; PART[(x, y)] = 'head'
    # the neck of the growth where it sits in the hood
    for y in range(HEAD_CY + HEAD_RY - 8, HOOD_TOP + 4):
        hw = 14 + (y - (HEAD_CY + HEAD_RY - 8)) * 0.6
        for x in range(int(MX - hw), int(MX + hw) + 1):
            v = 1.8 - 1.4 * ((x - MX) / hw) ** 2 - 0.6 * (y - (HEAD_CY + HEAD_RY - 8)) / 10
            if (x, y) not in PIX or PART[(x, y)] in ('hood',): PIX[(x, y)] = ['C', band(v, x, y)]; PART[(x, y)] = 'head'
    # a few wet pores / lichen flecks
    for (x, y), v in list(PIX.items()):
        if PART.get((x, y)) == 'head' and h32(x, y, 6) % 61 == 0: v[1] = max(0, v[1] - 2)
    if cut:
        CUT = HEAD_CY - 6
        for x in range(MX - HEAD_RX - 2, MX + HEAD_RX + 6):
            for y in range(CUT, CUT + 4):
                if PART.get((x, y)) == 'head': PIX[(x, y)] = ['C', 4 if y == CUT else 3]
        for y in range(CUT - 5, CUT + 12):
            for x in range(MX - 24, MX + 27):
                d = ((x - MX - 1) / 24.0) ** 2 + ((y - CUT + 1) / 8.0) ** 2
                if d <= 1:
                    if d > 0.8: PIX[(x, y)] = ['W', 1]; PART[(x, y)] = 'head'
                    else:
                        PIX[(x, y)] = ['T', 0]; PART[(x, y)] = 'cavity'
                        if h32(x, y, 3) % 17 == 0: PIX[(x, y)] = ['B', 3]
                        if d < 0.35 and h32(x, y, 4) % 11 == 0: PIX[(x, y)] = ['R', 5]
        # the severed crown lying at the feet
        for y in range(FEET - 22, FEET + 1):
            for x in range(MX + 64, MX + 118):
                d = ((x - MX - 90) / 26.0) ** 2 + ((y - FEET + 8) / 12.0) ** 2
                if d <= 1 and 0 <= x < FW:
                    v = 1.0 + 3.0 * max(0.0, math.sqrt(1 - d)) - (1.5 if y > FEET - 6 else 0)
                    g = nA(x * 2.4, y * 1.5)
                    if abs((g * 4) % 1 - 0.5) < 0.055: v -= 2.6
                    PIX[(x, y)] = ['C', band(v, x, y)]; PART[(x, y)] = 'lid'

def stake(PIX, PART):
    cy = SHOULDER + 44
    pts = [(MX - 30, cy + 18), (MX - 8, cy - 16), (MX + 2, cy - 12), (MX - 16, cy + 22)]
    def shade(x, y):
        v = 3 if (x - y) % 7 else 1
        if y < cy - 10: v = 4
        return ['W', v]
    fill_poly(PIX, PART, pts, 'stake', shade)
    for (x, y) in ((MX - 8, cy - 18), (MX - 7, cy - 17), (MX - 9, cy - 16), (MX - 4, cy - 16)): PIX[(x, y)] = ['W', 4]; PART[(x, y)] = 'stake'
    for y in range(cy - 4, cy + 30):
        for x in range(MX - 40, MX + 10):
            d = ((x - (MX - 16)) / 24.0) ** 2 + ((y - cy - 10) / 15.0) ** 2
            if d <= 1 and PART.get((x, y)) == 'robe' and h32(x, y, 8) % 3: PIX[(x, y)] = ['R', 0 if d < 0.55 else 1]
    for (x0, y0, x1, y1) in ((MX - 36, cy + 14, MX - 30, cy + 30), (MX - 2, cy + 14, MX + 4, cy + 24), (MX - 20, cy + 16, MX - 18, cy + 32)):
        for y in range(y0, y1):
            for x in range(x0, x1):
                if PART.get((x, y)) == 'robe': PIX[(x, y)] = ['R', 1 if (x + y) % 2 else 2]
    # the stake's foot behind the figure, planted in the flagstones between the feet
    for y in range(FEET - 4, FEET + 2):
        for x in range(MX - 5, MX + 6):
            if (x, y) not in PIX: PIX[(x, y)] = ['D', 1 if x < MX else 0]; PART[(x, y)] = 'stakefoot'

def shadow(p, PIX):
    for y in range(FEET - 6, FH):
        for x in range(FW):
            d = ((x - MX) / 70.0) ** 2 + ((y - FEET + 1) / 6.0) ** 2
            if d < 1 and (x, y) not in PIX and (x + y) % 2 == 0: p[x, y] = (7, 10, 9, 140 if d < 0.6 else 80)

SOFT = {frozenset(('robe', 'hoodin')), frozenset(('hoodin', 'face')), frozenset(('head', 'cavity')), frozenset(('robe', 'stake')), frozenset(('hood', 'hoodin')), frozenset(('robe', 'hood'))}
ORDER = ['stakefoot', 'leg', 'robe', 'hood', 'hoodin', 'face', 'hand', 'stake', 'head', 'cavity', 'lid', 'myc', 'tree', 'tcap']
def finish(PIX, PART, extra=None):
    img = Image.new('RGBA', (FW, FH), (0, 0, 0, 0)); p = img.load()
    shadow(p, PIX)
    if extra:
        for (x, y), c in extra.items(): p[x, y] = c
    for (x, y), (k, i) in PIX.items():
        r = RAMPS[k]; p[x, y] = r[max(0, min(len(r) - 1, int(i)))] + (255,)
    ink = set()
    for (x, y) in PIX:
        a = PART.get((x, y))
        for nx_, ny_ in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx_, ny_) not in PIX: ink.add((x, y)); continue
            b = PART.get((nx_, ny_))
            if a == b or frozenset((a, b)) in SOFT: continue
            if (nx_, ny_) > (x, y):
                ia, ib = ORDER.index(a) if a in ORDER else 0, ORDER.index(b) if b in ORDER else 0
                ink.add((x, y) if ia <= ib else (nx_, ny_))
    for (x, y) in ink:
        if PIX[(x, y)][0] != 'M': p[x, y] = INK + (255,)
    return img

def build(cut=False):
    PIX, PART = new(); legs(PIX, PART); robe(PIX, PART); hood_face(PIX, PART); stake(PIX, PART); head(PIX, PART, cut=cut)
    return PIX, PART
def frame_intact(): return finish(*build())
def frame_cut(): return finish(*build(cut=True))
def frame_growth():
    PIX, PART = build()
    random.seed(11)
    for _ in range(12):
        x, y = random.randint(MX - 40, MX + 40), random.randint(HOOD_TOP + 10, SHOULDER + 10)
        if (x, y) not in PIX: continue
        ang = random.uniform(math.radians(60), math.radians(120)); pts = []
        for i in range(random.randint(40, 130)):
            ang += random.uniform(-0.45, 0.45); ang = max(math.radians(20), min(math.radians(160), ang))
            x += math.cos(ang); y += math.sin(ang); xi, yi = int(x), int(y)
            if (xi, yi) not in PIX or PART.get((xi, yi)) in ('head',): break
            pts.append((xi, yi))
        for j, (px_, py_) in enumerate(pts): PIX[(px_, py_)] = ['M', 2 if j % 2 else 1]; PART[(px_, py_)] = 'myc'
        if pts:
            ex, ey = pts[-1]
            for dx in (0, 1):
                for dy in (0, 1): PIX[(ex + dx, ey + dy)] = ['M', 3]; PART[(ex + dx, ey + dy)] = 'myc'
    for (k, v) in list(PIX.items()):
        if PART.get(k) == 'head' and nA(k[0] * 1.3, k[1] * 1.3) > 0.6: v[0] = 'M'; v[1] = 1 if v[1] < 3 else 2
    TOP = HEAD_CY - HEAD_RY + 2
    TR = []
    for i in range(101):
        t = i / 100
        TR.append((MX + 4 + 14 * math.sin(t * 3.4 + 0.4) + 5 * math.sin(t * 9) * t, TOP - t * (TOP - 22), 8 - 5.5 * t))
    def disc(cx, cy, r, i, name='tree'):
        for y in range(int(cy - r), int(cy + r) + 1):
            for x in range(int(cx - r), int(cx + r) + 1):
                if 0 <= x < FW and 0 <= y < FH and (x - cx) ** 2 + (y - cy) ** 2 <= r * r: PIX[(x, y)] = ['M', i]; PART[(x, y)] = name
    def seg(a, b, w0, w1, steps):
        for i in range(steps + 1):
            t = i / steps; disc(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, w0 + (w1 - w0) * t, 1)
    for (a, b) in zip(TR, TR[1:]): seg(a, b, a[2], b[2], 3)
    CAPS = []
    def branch(x, y, ang, ln, w, depth):
        pts = []; cx, cy, a = x, y, ang; n = max(2, int(ln / 4))
        for i in range(n + 1): pts.append((cx, cy)); cx += 4 * math.cos(a); cy -= 4 * math.sin(a); a += 0.07
        for i, (p0, p1) in enumerate(zip(pts, pts[1:])):
            t = i / n; seg(p0, p1, w * (1 - 0.5 * t), w * (1 - 0.5 * (t + 1 / n)), 2)
        ex, ey = pts[-1]
        if depth < 1 and ln > 32: branch(ex, ey, a + (0.7 if math.cos(ang) > 0 else -0.7), ln * 0.5, w * 0.6, depth + 1)
        CAPS.append((ex, ey, max(7, int(ln * 0.4)), max(4, int(ln * 0.16))))
    random.seed(5)
    for (t, side, ln) in ((0.3, -1, 38), (0.45, 1, 44), (0.6, -1, 34), (0.72, 1, 36), (0.84, -1, 26), (0.92, 1, 24)):
        x, y, w = TR[int(t * 100)]; branch(x, y, math.radians(90 - side * random.randint(44, 64)), ln, w * 0.8, 0)
    top = TR[-1]; CAPS.append((top[0], top[1] - 5, 30, 12))
    glow = {}
    for (cx, cy, rx, ry) in CAPS:
        for y in range(int(cy - ry * 1.3), int(cy + ry) + 1):
            for x in range(int(cx - rx), int(cx + rx) + 1):
                if not (0 <= x < FW and 0 <= y < FH): continue
                nx = (x - cx) / rx
                if abs(nx) > 1: continue
                top_y = cy - ry * 1.3 * math.sqrt(1 - nx * nx); bot_y = cy + ry * 0.55 * math.sqrt(1 - nx * nx)
                if top_y <= y <= bot_y:
                    f = (y - top_y) / max(1, bot_y - top_y)
                    i = 5 if f < 0.18 else 4 if f < 0.55 else 3 if f < 0.72 else 2 if f < 0.86 else 1
                    if nx > 0.6 and f < 0.6: i = max(2, i - 1)
                    if h32(x, y, 7) % 23 == 0 and 0.2 < f < 0.7: i = 5
                    PIX[(x, y)] = ['M', i]; PART[(x, y)] = 'tcap'
        for _ in range(4):
            sx, sy = int(cx + random.uniform(-rx, rx)), int(cy - ry * 1.3 - random.randint(3, 16))
            if 0 <= sx < FW and 0 <= sy < FH and (sx, sy) not in PIX: glow[(sx, sy)] = MYC[4] + (200,)
        for y in range(int(cy - ry * 1.3 - 9), int(cy + ry + 9)):
            for x in range(int(cx - rx - 9), int(cx + rx + 9)):
                if not (0 <= x < FW and 0 <= y < FH) or (x, y) in PIX: continue
                d = math.hypot((x - cx) / (rx + 8), (y - cy) / (ry * 1.1 + 8))
                if d < 1 and (x + y) % 2 == 0: glow[(x, y)] = MYC[3] + (int(90 * (1 - d)),)
    for (a, b) in zip(TR, TR[1:]):
        for off in (-0.45, 0.35):
            x, y = int(a[0] + off * a[2]), int(a[1])
            if PART.get((x, y)) == 'tree': PIX[(x, y)] = ['M', 3 if y % 11 else 4]
    return finish(PIX, PART, extra=glow)

frames = [frame_intact(), frame_cut(), frame_growth()]
sheet = Image.new('RGBA', (FW * 3, FH), (0, 0, 0, 0))
for i, f in enumerate(frames):
    sheet.paste(f, (i * FW, 0)); f.save(f'{OUT}/corpse_{i}.png')
sheet.save(f'{OUT}/crossroad_corpse.png')
print('frames', len(frames), FW, FH)
