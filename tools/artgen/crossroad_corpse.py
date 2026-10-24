"""The dead demigod v4 — impaled and displayed: a tall stake planted in a cairn at the junction runs up through the body
and out of the chest; the corpse hangs on it 60 px above the flagstones, bony shins and feet dangling toes-down, the
elongated head lolled to one side. A board nailed to the stake carries a painted crown, crossed out — the mob's warning
to any god who would rule the city. Red hooded robe, hands at the hips. Instead of a mushroom-cloud cap the head
continues upward into an elongated, surreal-but-anatomical cranium (sulci, suture, cleft crown). 3 frames 240x500."""
import sys, math, random
from PIL import Image, ImageDraw
from pal_day import *
OUT = sys.argv[1]
FW, FH = 240, 500
MX, FEET = 120, 436
GROUND = FH - 4                                 # the stake's foot; the body hangs above it
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
    # bony shins hanging limp under the torn hem, feet pointing down — he hangs, he does not stand
    for cx, ankle, tilt in ((MX - 11, 418, 0.20), (MX + 13, 411, -0.14)):
        for y in range(HEM - 8, ankle + 1):
            c = cx + (y - HEM) * tilt
            for x in range(int(c - 5), int(c + 6)):
                nx = (x + 0.5 - c) / 4.2
                if abs(nx) > 1: continue
                v = 2.3 - 1.7 * nx * nx + (nB(x, y) - 0.5) * 0.5
                PIX[(x, y)] = ['B', band(v, x, y)]; PART[(x, y)] = 'leg'
        c0 = cx + (ankle - HEM) * tilt
        for x in range(int(c0) - 4, int(c0) + 5): PIX[(x, ankle)] = ['B', 0]; PART[(x, ankle)] = 'leg'   # ankle crease
        for i in range(15):                                                                # the foot, toes down
            y = ankle + 1 + i
            hw = 5.4 - i * 0.18
            c = c0 + i * tilt * 1.2
            for x in range(int(c - hw) - 1, int(c + hw) + 2):
                nx = (x + 0.5 - c) / hw
                if abs(nx) > 1: continue
                v = 2.1 - 1.4 * nx * nx - 0.6 * (i / 16) + (nB(x, y) - 0.5) * 0.4
                if i > 10 and (x - int(c - hw)) % 3 == 0: v -= 1.6                         # the toes
                PIX[(x, y)] = ['B', band(v, x, y)]; PART[(x, y)] = 'leg'
        PIX[(int(c0) - 4, ankle)] = ['B', 4]                                               # ankle knob

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
        for y in range(GROUND - 22, GROUND + 1):
            for x in range(MX + 40, MX + 96):
                d = ((x - MX - 66) / 26.0) ** 2 + ((y - GROUND + 8) / 12.0) ** 2
                if d <= 1 and 0 <= x < FW:
                    v = 1.0 + 3.0 * max(0.0, math.sqrt(1 - d)) - (1.5 if y > GROUND - 6 else 0)
                    g = nA(x * 2.4, y * 1.5)
                    if abs((g * 4) % 1 - 0.5) < 0.055: v -= 2.6
                    PIX[(x, y)] = ['C', band(v, x, y)]; PART[(x, y)] = 'lid'

def line(x0, y0, x1, y1):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    return [(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)) for i in range(n + 1)]

def pole_x(y): return MX - 2 + (GROUND - y) * 0.03

def pole(PIX, PART):
    # the stake's shaft below the body: weathered timber, grain cracks, rope lashings, old blood run down from him
    for y in range(HEM - 30, GROUND + 1):
        hw = 5.5 + 1.6 * (y - (HEM - 30)) / (GROUND - HEM + 30)
        c = pole_x(y)
        for x in range(int(c - hw) - 1, int(c + hw) + 2):
            u = (x + 0.5 - c) / hw
            if abs(u) > 1: continue
            v = 3.5 - 1.7 * u - 1.0 * u * u + (nA(x * 3.1, y * 0.25) - 0.5) * 1.6
            if h32(x, 7) % 9 == 0: v -= 1.3
            PIX[(x, y)] = ['D', band(v, x, y)]; PART[(x, y)] = 'pole'
    for dx, ln in ((-3, 30), (1, 18), (-1, 44)):
        for y in range(HEM - 4, HEM + ln):
            k = (int(pole_x(y) + dx), y)
            if PART.get(k) == 'pole' and h32(k[0], y, 2) % 5: PIX[k] = ['R', 1 if y < HEM + ln - 6 else 0]
    for yb in (GROUND - 52, GROUND - 48):
        for x in range(int(pole_x(yb) - 8), int(pole_x(yb) + 9)):
            for dy in (0, 1):
                if PART.get((x, yb + dy)) == 'pole': PIX[(x, yb + dy)] = ['W', 4 if (x + dy) % 3 else 2]

def cairn(PIX, PART):
    # the stones the mob piled round the stake's foot
    rnd = random.Random(21); stones = []
    for i in range(15):
        sx = MX - 2 + rnd.uniform(-30, 30)
        sy = GROUND - 1 - rnd.uniform(0, 13) * (1 - abs(sx - MX + 2) / 34)
        stones.append((sx, sy, rnd.uniform(4.5, 7.5), rnd.uniform(3, 4.8)))
    for sx, sy, rx, ry in sorted(stones, key=lambda t: t[1]):
        for y in range(int(sy - ry) - 1, int(sy + ry) + 2):
            for x in range(int(sx - rx) - 1, int(sx + rx) + 2):
                u, w = (x + 0.5 - sx) / rx, (y + 0.5 - sy) / ry
                d = u * u + w * w
                if d > 1 or y > GROUND: continue
                lam = max(0.0, -0.6 * u - 0.7 * w + 0.5 * math.sqrt(1 - d))
                v = 1.6 + 5.5 * lam + (nB(x * 1.5, y * 1.5) - 0.5) * 1.0 - (1.6 if d > 0.78 else 0)
                PIX[(x, y)] = ['T', band(v, x, y)]; PART[(x, y)] = 'cairn'

def board(PIX, PART):
    # a plank nailed to the stake: a crown painted in pale lime, crossed out in red
    bx, by = MX - 2, GROUND - 32
    def put(lx, ly, val, part='board'):
        k = (bx + lx, by + ly + round(lx * 0.09))
        PIX[k] = val; PART[k] = part
    for ly in range(-8, 9):
        for lx in range(-16, 17):
            v = 3.3 - 0.03 * lx + (nA((bx + lx) * 2.2, (by + ly) * 1.2) - 0.5) * 1.0
            if ly in (0, 1): v -= 1.4 if ly == 0 else -0.4
            put(lx, ly, ['D', band(v, bx + lx, by + ly)])
    crown = [(-8, 5), (-8, -2), (-4, 1), (0, -5), (4, 1), (8, -2), (8, 5), (-8, 5)]
    for (x0, y0), (x1, y1) in zip(crown, crown[1:]):
        for (lx, ly) in line(x0, y0, x1, y1): put(lx, ly, ['C', 4])
    for (x0, y0, x1, y1) in ((-12, -6, 12, 6), (-12, 6, 12, -6)):
        for (lx, ly) in line(x0, y0, x1, y1): put(lx, ly, ['R', 5]); put(lx, ly + 1, ['R', 3])
    for lx, ly in ((-14, -6), (14, -6), (-14, 6), (14, 6)): put(lx, ly, ['T', 8])

def stake(PIX, PART):
    # the splintered point, out through the chest — driven up from below, a little off-centre
    tx, ty, base = MX - 10, SHOULDER + 16, SHOULDER + 50
    for y in range(ty, base + 1):
        t = (y - ty) / (base - ty)
        hw, c = 0.6 + t * 6.2, tx + t * 3
        for x in range(int(c - hw) - 1, int(c + hw) + 2):
            u = (x + 0.5 - c) / max(hw, 0.8)
            if abs(u) > 1: continue
            v = 4.6 - 1.8 * u + (nA(x * 3, y * 0.4) - 0.5) * 1.2 - (4.0 * (t - 0.7) if t > 0.7 else 0)
            PIX[(x, y)] = ['D', band(v, x, y)]; PART[(x, y)] = 'stake'
    for (x, y) in ((tx - 3, ty + 6), (tx - 4, ty + 5), (tx + 3, ty + 9), (tx + 4, ty + 8), (tx - 5, ty + 12), (tx + 6, ty + 15)):
        PIX[(x, y)] = ['D', 5]; PART[(x, y)] = 'stake'
    for (x, y) in ((tx - 1, ty + 2), (tx, ty + 4), (tx + 1, ty + 7)): PIX[(x, y)] = ['R', 2]               # blood on the point
    for y in range(base - 10, base + 26):                                                                  # the wound
        for x in range(tx - 18, tx + 26):
            d = ((x - tx - 3) / 17.0) ** 2 + ((y - base - 4) / 12.0) ** 2
            if d <= 1 and PART.get((x, y)) == 'robe' and h32(x, y, 8) % 3: PIX[(x, y)] = ['R', 0 if d < 0.5 else 1]
    for dx, ln in ((-6, 46), (2, 70), (7, 34)):                                                            # runs down the robe
        for y in range(base + 8, base + ln):
            k = (tx + 3 + dx + (y - base) // 23, y)
            if PART.get(k) == 'robe' and h32(k[0], y, 5) % 6: PIX[k] = ['R', 0]

def shadow(p, PIX):
    for y in range(GROUND - 6, FH):
        for x in range(FW):
            d = ((x - MX) / 64.0) ** 2 + ((y - GROUND - 1) / 5.0) ** 2
            if d < 1 and (x, y) not in PIX and (x + y) % 2 == 0: p[x, y] = (7, 10, 9, 140 if d < 0.6 else 80)

SOFT = {frozenset(('pole', 'board')), frozenset(('robe', 'hoodin')), frozenset(('hoodin', 'face')), frozenset(('head', 'cavity')), frozenset(('robe', 'stake')), frozenset(('hood', 'hoodin')), frozenset(('robe', 'hood'))}
ORDER = ['pole', 'cairn', 'board', 'stakefoot', 'leg', 'robe', 'hood', 'hoodin', 'face', 'hand', 'stake', 'head', 'cavity', 'lid', 'myc', 'tree', 'tcap']
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

LOLL_PIVOT, LOLL = SHOULDER + 2, 0.16                  # the head hangs to the right: rows above the neck slide over
def loll(y): return int(round((LOLL_PIVOT - y) * LOLL)) if y < LOLL_PIVOT else 0

def build(cut=False):
    PIX, PART = new(); pole(PIX, PART); cairn(PIX, PART); board(PIX, PART); legs(PIX, PART); robe(PIX, PART)
    HP, HA = new(); hood_face(HP, HA); head(HP, HA, cut=cut)
    for (x, y), v in HP.items():
        k = (x + loll(y), y)
        if HA[(x, y)] == 'lid': k = (x, y)
        PIX[k] = v; PART[k] = HA[(x, y)]
    stake(PIX, PART)
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
    TREE_TOP, SH = 80, loll(HEAD_CY - HEAD_RY + 2)
    TR = []
    for i in range(101):
        t = i / 100
        TR.append((MX + 4 + SH + 14 * math.sin(t * 3.4 + 0.4) + 5 * math.sin(t * 9) * t, TOP - t * (TOP - TREE_TOP), 8 - 5.5 * t))
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
    for (t, side, ln) in ((0.3, -1, 30), (0.45, 1, 34), (0.6, -1, 27), (0.72, 1, 28), (0.84, -1, 21), (0.92, 1, 19)):
        x, y, w = TR[int(t * 100)]; branch(x, y, math.radians(90 - side * random.randint(44, 64)), ln, w * 0.8, 0)
    top = TR[-1]; CAPS.append((top[0], top[1] - 5, 26, 11))
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
