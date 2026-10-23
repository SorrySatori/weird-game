"""The opening shot of the intro: the Hymnar, the sacred giant mushroom of the Obazoba cult, in a cavern deep under the
earth. 1067x1000 -- taller than the screen; the scene pans from the cap down to the temple of the Highest Humenium
Council at its foot.

The Hymnar is NOT the god: Obazoba has no body, he is an ideal. The Hymnar is his shrine -- a colossal mushroom whose
cap is half Growth (pale, scaled, mossy, sprouting) and half Decay (rotting, holed, dripping), the seam between them
stitched with glowing mycelium. Its gills light the cavern. Pilgrims climb a spiral walkway round the stalk, prayer
ribbons hang on ropes from its veil to the cave walls, two stone priests guard the temple door. The scale is the point.

python3 intro_hymnar.py <outdir>  ->  hymnar.png, hymnar_gills.png (gill glow, flared by the scene when the signal
arrives), hymnar_glow.png (veins + lights, pulsed with ADD), hymnar.json (signal path, lanterns, drips)."""
import sys, math, random, json
from PIL import Image
from pal_under import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
W, H = 1067, 1000
CX = 533
img = Image.new('RGB', (W, H), INK); P = img.load()
gil = Image.new('RGBA', (W, H), (0, 0, 0, 0)); GI = gil.load()
glw = Image.new('RGBA', (W, H), (0, 0, 0, 0)); GL = glw.load()
nA, nB, nC, nD = make_noise(60, 41, W, H), make_noise(16, 42, W, H), make_noise(5, 43, W, H), make_noise(30, 44, W, H)
nE, nF = make_noise(9, 45, W, H), make_noise(3, 46, W, H)
BAY4 = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))

def put(x, y, c, glow=False, gill=False):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H:
        P[x, y] = c
        if glow: GL[x, y] = c + (255,)
        if gill: GI[x, y] = c + (255,)

def mix(k1, k2, f, v, x, y):
    """switch between two ramps along an organic (noise) boundary -- never a checkerboard over large areas"""
    return col(k2 if f > nE(x * 1.3 + 17, y * 1.3 + 5) else k1, band(v, x, y))

RIM_Y, CAP_TOP, CAP_RX = 330, 38, 640    # cap: front of the rim, crown, half-width (edges run off the frame)
UND = 74                                  # depth of the underside seen from below
STALK_TOP, BULB_Y, FLOOR_Y = 380, 872, 905
ANN_Y = 462
TX, TY = CX, 966                          # temple stair foot
LANTERNS = []                             # warm lights the scene makes flicker

def rim_y(x):
    u = (x - CX) / CAP_RX
    return RIM_Y - 30 * u * u + 7 * u + 4 * (nD(x * 0.7, 11) - 0.5)
def cap_top(x):
    u = (x - CX) / CAP_RX
    if abs(u) >= 1: return None
    return RIM_Y - (RIM_Y - CAP_TOP) * (1 - u * u) ** 0.5 - 30 * u * u + 7 * u + 6 * (nD(x * 0.5, 23) - 0.5)
def under_y(x):
    u = (x - CX) / CAP_RX
    if abs(u) >= 1: return None
    return rim_y(x) + UND * math.sqrt(1 - u * u) * (1 - 0.3 * u * u)
def stalk_hw(y):
    t = max(0.0, (y - STALK_TOP) / (BULB_Y - STALK_TOP))
    return 82 + 26 * t + 160 * math.exp(-((y - BULB_Y) / 64.0) ** 2) + 30 * max(0.0, (y - BULB_Y) / 40.0)

# ------------------------------------------------------------------ 1. the cavern: haze, rock curtains at three depths
for y in range(H):
    for x in range(W):
        hz = math.exp(-((y - 600) / 360.0) ** 2) * (0.75 + 0.25 * math.exp(-((x - CX) / 600.0) ** 2))
        v = 0.3 + hz * 2.0 + (nA(x, y) - 0.5) * 1.3 + (nB(x * 0.7, y * 0.7) - 0.5) * 0.5
        P[x, y] = col('g', band(max(0.2, v), x, y))

def spikes(rnd, n, x0, x1, lmin, lmax, wmin, wmax):
    return [(rnd.uniform(x0, x1), rnd.uniform(lmin, lmax), rnd.uniform(wmin, wmax)) for _ in range(n)]
def profile(x, base, sp, sharp=1.6):
    v = base
    for (sx, ln, w) in sp:
        d = abs(x - sx) / w
        if d < 1: v += ln * (1 - d) ** sharp
    return v

def rock_layer(seed, depth, top_base, top_sp, bot_base, bot_sp):
    """stalactites hanging from the vault and stalagmites rising from the floor; depth 0 far (hazy) .. 1 near"""
    rf = make_noise(7, seed, W, H)
    for x in range(W):
        top = profile(x, top_base, top_sp); bot = bot_base - profile(x, 0, bot_sp)
        light_x = math.exp(-((x - CX) / 420.0) ** 2)
        for y in list(range(0, int(top))) + list(range(int(bot), H)):
            edge = min(abs(y - top), abs(y - bot))
            v = (2.5 - depth * 1.9) + light_x * (0.7 - depth * 0.4) + (nB(x * 1.6, y * 0.25) - 0.5) * 1.0 + (rf(x, y) - 0.5) * 0.5
            if abs((nE(x * 2.5, y * 0.1) * 4) % 1 - 0.5) < 0.07: v -= 0.7                       # flutes down the drip-stone
            if edge < 2: v += 1.0 - depth * 0.6                                              # wet lit lip
            put(x, y, col('g' if depth < 0.5 else 'R', band(max(0.2, v), x, y)))

r = random.Random(3)
rock_layer(71, 0.15, 30, spikes(r, 26, 0, W, 60, 220, 12, 40), 860, spikes(r, 18, 0, W, 40, 170, 14, 46))
rock_layer(72, 0.55, 0, spikes(r, 14, 0, W, 80, 300, 20, 60) + [(0, 900, 120), (W, 900, 130)],
           900, spikes(r, 10, 0, W, 50, 220, 20, 60) + [(0, 500, 140), (W, 500, 150)])
rock_layer(73, 0.95, 0, [(0, 1000, 70), (W, 1000, 80), (130, 160, 50), (940, 180, 60)], 1000, [(0, 300, 120), (W, 300, 130)])

# glow-worms on the vault: threads with a luminous bead
gw = random.Random(17)
for i in range(220):
    x = gw.randint(0, W - 1); y = gw.randint(0, 330)
    if CX - 560 < x < CX + 560 and y > 60 and gw.random() < 0.85: continue
    ln = gw.randint(2, 9)
    for k in range(ln): put(x, y + k, col('M', 1 + (k > ln - 3)))
    put(x, y + ln, col('M', gw.choice((6, 7, 8))), glow=True)

# ------------------------------------------------------------------ 2. lesser mushrooms at depth
def lesser(mx, base, cap_y, cw, sw, depth):
    fog = depth
    for y in range(cap_y, base):
        t = (y - cap_y) / max(1, base - cap_y)
        hw = sw * (1 + 0.35 * t * t)
        for x in range(int(mx - hw), int(mx + hw) + 1):
            u = (x - mx) / hw
            v = 0.8 + 2.4 * max(0.0, -0.4 * u + 0.9 * math.sqrt(max(0.0, 1 - u * u))) - fog * 0.8 + (nB(x * 3, y * 0.3) - 0.5) * 0.6
            v += math.exp(-(y - cap_y) / 18.0) * 1.4                                           # lit by its own gills
            put(x, y, col('g' if fog > 0.6 else 'C', band(max(0.3, v - (0.6 if fog <= 0.6 else 0)), x, y)))
    ry = cw * 0.5
    for y in range(int(cap_y - ry), cap_y + 7):
        for x in range(mx - cw, mx + cw + 1):
            u = (x - mx) / cw
            if y <= cap_y:
                w = (cap_y - y) / ry
                if w > (1 - u * u) ** 0.6: continue
                n = (u, -w, math.sqrt(max(0.0, 1 - u * u - w * w * 0.5)))
                v = 0.8 + 2.6 * max(0.0, -0.35 * n[0] - 0.45 * n[1] + 0.8 * n[2]) + (1 - w) * 0.8 - fog * 0.9
                v += (nB(x * 2, y * 2) - 0.5) * 0.5
                if w < 0.12: v += 1.2                                                          # rim catching the light
                put(x, y, col('g' if fog > 0.6 else 'C', band(max(0.3, v - (0.6 if fog <= 0.6 else 0)), x, y)))
            else:
                if abs(u) > 1 - (y - cap_y) / 9.0: continue
                put(x, y, col('M', 3.2 - abs(u) * 1.8 - fog + (0.8 if x % 3 == 0 else 0)), glow=True)
for args in ((176, 872, 712, 34, 4, 0.85), (896, 866, 700, 40, 5, 0.85), (338, 884, 770, 24, 3, 0.9), (736, 884, 760, 28, 3, 0.9),
             (108, 905, 566, 100, 14, 0.5), (982, 910, 604, 116, 16, 0.45), (262, 930, 724, 58, 8, 0.3), (838, 930, 708, 66, 9, 0.3)):
    lesser(*args)

# ------------------------------------------------------------------ 3. the floor, glowing mycelial mats, the roots
for y in range(FLOOR_Y - 20, H):
    z = (y - FLOOR_Y + 20) / (H - FLOOR_Y + 20)
    for x in range(W):
        if abs(x - CX) < stalk_hw(min(y, BULB_Y + 30)) and y < BULB_Y + 30: continue
        v = 1.0 + (1 - z) * 0.6 + (nB(x * 0.4, y * 2.5) - 0.5) * 0.9 + math.exp(-((x - CX) / 260.0) ** 2) * 1.2
        mat = nE(x * 0.5, y * 2.0)
        if mat > 0.8 and abs(x - CX) < 420:
            put(x, y, col('M', 1 + (mat > 0.86) + (nF(x, y) > 0.85)), glow=mat > 0.86); continue
        P[x, y] = mix('R', 'g', 1 - abs(x - CX) / 340.0, v, x, y)

def gnarl(x, y, ang, w, n, seed):
    rr = random.Random(seed); pts = []
    for s in range(n):
        x += math.cos(ang) * 2.0; y += math.sin(ang) * 2.0
        ang += (rr.random() - 0.5) * 0.08
        w = max(2.0, w * 0.993 + (0.04 if y > 960 else 0))
        pts.append((x, y, w))
    for (x, y, w) in pts:
        for xx in range(int(x - w), int(x + w) + 1):
            for yy in range(int(y - w * 0.55), int(y + w * 0.55) + 1):
                u = (yy - y) / (w * 0.55 + 0.01)
                v = 1.0 + 2.8 * (1 - abs(u)) - 1.1 * u + (nB(xx * 1.5, yy * 3) - 0.5) * 1.0
                if abs(math.sin(xx * 0.35 + yy * 0.9)) < 0.12: v -= 0.8                          # bark furrows
                put(xx, yy, col('O', band(v, xx, yy)))
    return pts
ROOTS = []
for i, (side, ang, w, n) in enumerate(((1, 0.10, 18, 270), (-1, 0.12, 18, 270), (1, 0.42, 22, 150), (-1, 0.40, 22, 150),
                                      (1, 0.75, 26, 80), (-1, 0.78, 26, 80), (1, -0.06, 12, 230), (-1, -0.05, 12, 230))):
    a = ang if side > 0 else math.pi - ang
    ROOTS.append(gnarl(CX + side * 150, BULB_Y + 14 + (i % 3) * 5, a, w, n, i + 20))

# ------------------------------------------------------------------ 4. the pilgrims' spiral walkway (back half first)
WALK_TH0, WALK_TURNS, WALK_Y0, WALK_Y1 = -0.5, 1.75, 852, 580
def walkway(front):
    th1 = WALK_TH0 + WALK_TURNS * math.tau
    N = 3200
    last_post = last_lamp = -9
    pilgrims = {0.04, 0.075, 0.62}
    for i in range(N + 1):
        f = i / N
        th = WALK_TH0 + (th1 - WALK_TH0) * f
        y = WALK_Y0 + (WALK_Y1 - WALK_Y0) * f
        R = stalk_hw(y) + 9
        x = CX + R * math.sin(th); c = math.cos(th)
        if (c > 0) != front: continue
        if front:
            sh = 2.4 + 2.0 * c + (nB(x, y) - 0.5) * 0.6
            board = int(th / 0.11) % 2
            for k, dv in enumerate((1.8, 0.9, 0.4 + board * 0.5, -0.1, -0.6, -1.2, -1.8)):
                put(x, y + k, col('O', sh + dv))
            if th - last_post > 0.3:                                                        # railing posts
                last_post = th
                for k in range(1, 8): put(x, y - k, col('O', 2.4 + c))
            put(x, y - 6, col('O', 2.0 + c))                                                  # the rope rail
            if th - last_lamp > 1.05 and c > 0.3:                                            # lanterns under the boards
                last_lamp = th
                put(x, y + 5, col('O', 1)); put(x, y + 6, col('O', 1))
                for (dx, dy, v) in ((0, 7, 7), (1, 7, 6), (0, 8, 6), (1, 8, 5), (0, 9, 4)):
                    put(x + dx, y + dy, col('G', v), glow=True)
                LANTERNS.append(dict(x=int(x), y=int(y + 8), r=12))
            for pf in list(pilgrims):                                                        # tiny pilgrims (scale!)
                if abs(f - pf) < 0.0004 and c > 0.2:
                    pilgrims.discard(pf)
                    for yy in range(int(y) - 8, int(y)):
                        for dx in (-1, 0, 1): put(x + dx, yy, col('B', 1 + (dx < 0)))
                    for dx in range(-3, 4): put(x + dx, y - 9, col('C', 6 if abs(dx) < 3 else 4))
                    for dx in range(-2, 3): put(x + dx, y - 10, col('C', 7))
                    put(x + 2, y - 4, col('G', 7), glow=True)
        else:
            for k, dv in enumerate((0.8, 0.4, 0.2, 0.0, -0.2, -0.6)):
                put(x, y + k, col('O', 1.2 + dv))
walkway(front=False)

# ------------------------------------------------------------------ 5. the stalk: fibrous, twisting, lit from above by the gills
for y in range(STALK_TOP - 10, BULB_Y + 44):
    hw = stalk_hw(y)
    top = math.exp(-(y - STALK_TOP) / 120.0)
    for x in range(int(CX - hw), int(CX + hw) + 1):
        u = max(-0.999, min(0.999, (x - CX) / hw))
        n = math.sqrt(1 - u * u)
        s = math.asin(u) * 9 + y * 0.0015                                                  # around the cylinder, with a twist
        fib = nC(s * 16 + 3, y * 0.05)
        groove = abs((s * 1.2 + nE(s * 30, y * 0.05) * 0.6) % 1 - 0.5) < 0.035
        diff = max(0.0, -0.42 * u + 0.9 * n)                                               # key light from the front-left
        v = 0.5 + 3.0 * diff + (fib - 0.5) * 0.9 - (0.9 if groove else 0)
        if u > 0.8: v += 0.9 * (u - 0.8) / 0.2                                              # reflected light on the far edge
        if abs(u) > 0.975: v = 0.4
        v += top * 1.7
        v += math.exp(-((y - 930) / 90.0) ** 2) * math.exp(-((x - CX) / 160.0) ** 2) * 1.4  # the temple's warmth
        if nE(x * 1.6 + 50, y * 1.6) > 0.86 and y > 560: P[x, y] = col('S', band(v * 0.8 + 0.8, x, y)); continue   # moss patches
        if abs(u) > 0.9 and top > 0.2 and abs(u) <= 0.975:                                   # green rim light from the gills
            P[x, y] = col('M', 1.5 + top * 3.5); continue
        P[x, y] = col('C', band(max(0.3, v - 0.4), x, y))

# bracket fungi growing out of the stalk (silhouette breakers, same family as the Council's seats)
def shelf(side, y0, size):
    ax = CX + side * (stalk_hw(y0) - 6)
    ry = size * 0.42
    for y in range(int(y0 - ry) - 1, y0 + 4):
        for x in range(int(ax - size - 2), int(ax + size + 3)):
            dx = (x - ax) * side
            if dx < -4: continue
            u = max(0.0, dx) / size
            if y <= y0:
                w = (y0 - y) / ry
                rr = math.hypot(u, w)
                edge = 1 + 0.05 * math.sin(math.atan2(w, u) * 7 + size)
                if rr > edge: continue
                zone = rr * 5 + (nB(x * 2, y * 2) - 0.5) * 0.5
                v = 1.6 + (math.floor(zone) % 2) * 0.9 + w * 1.2 + (nC(x, y) - 0.5) * 0.5
                if rr > edge - 0.1: v = 5.6 if w > 0.3 else 4.6                             # pale growing margin
                put(x, y, col('C', v + 0.6) if rr <= edge - 0.1 else col('C', v + 1.2))
            elif u < 1 - (y - y0) * 0.15:
                put(x, y, col('M', 2.6 - (y - y0) * 0.5) if y == y0 + 1 else col('O', 0.6))
for (side, y0, size) in ((-1, 650, 52), (1, 716, 42), (-1, 768, 30), (1, 616, 26)):
    shelf(side, y0, size)

# ------------------------------------------------------------------ 6. veins: the signal's road (from the city, right) up the stalk
rv = random.Random(12)
def vline(pts, v=4, glow=True):
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for k in range(n):
            x = x0 + (x1 - x0) * k / n; y = y0 + (y1 - y0) * k / n
            put(x, y, col('M', v), glow=glow)
            if rv.random() < 0.05: put(x + 1, y, col('M', v + 2), glow=glow)
root = ROOTS[0]
path = [(W + 4, root[-1][1] - root[-1][2] * 0.3)] + [(px_, py_ - w * 0.3) for (px_, py_, w) in reversed(root)]
x0, y0 = path[-1]
yy = y0
while yy > STALK_TOP + 2:
    yy -= 3
    t = (y0 - yy) / (y0 - STALK_TOP)
    path.append((CX + stalk_hw(yy) * (0.55 - 0.45 * t) + 18 * math.sin(yy / 37.0), yy))
vline(path, 5)
for k in range(3):
    ph = rv.random() * 6; pts = []
    for yy in range(BULB_Y + 10, STALK_TOP, -4):
        pts.append((CX + stalk_hw(yy) * (0.8 - 0.25 * k / 2) * math.sin(yy / (80 + k * 17) + ph) * (1 if k % 2 else -1), yy))
    vline(pts, 2 + (k % 2), glow=True)
    for j in range(0, len(pts) - 8, 29):
        bx, by = pts[j]; a = rv.choice((-1, 1)) * 0.9 - math.pi / 2
        br = [(bx + math.cos(a) * i * 2.5, by + math.sin(a) * i * 2.5 + i * i * 0.08) for i in range(rv.randint(4, 8))]
        vline(br, 2, glow=True)

walkway(front=True)

# ------------------------------------------------------------------ 7. the annulus: a torn membrane skirt drooping round the stalk
for y in range(ANN_Y - 20, ANN_Y + 110):
    for x in range(int(CX - 190), int(CX + 191)):
        hw0 = stalk_hw(ANN_Y) + 8
        dx_ = abs(x - CX)
        top = ANN_Y - 16 + 12 * math.sqrt(max(0.0, 1 - (dx_ / hw0) ** 2)) if dx_ <= hw0 else ANN_Y - 16 + (dx_ - hw0) * 2.2
        if y < top: continue
        t = (y - top) / 100.0
        hw = hw0 + 10 + 34 * t
        if abs(x - CX) > hw: continue
        u = (x - CX) / hw
        tear = 70 + 26 * nB(x * 2.2, 7) + 14 * math.sin(x / 7.0) - 18 * u * u + 10 * math.sqrt(max(0.0, 1 - u * u))
        if y - top > tear: continue
        n = math.sqrt(max(0.0, 1 - u * u))
        fold = math.sin(x / 5.0 + 3 * nB(x * 0.5, y * 0.2))
        v = 0.8 + 2.4 * max(0.0, -0.4 * u + 0.9 * n) + fold * 0.8 + math.exp(-(y - top) / 22.0) * 2.0
        if y - top > tear - 3: v -= 1.0
        if y - top < 2: v += 1.0
        P[x, y] = col('C', band(max(0.4, v), x, y))
    # threads of the veil hanging below the tear
ht = random.Random(8)
for i in range(26):
    x = CX + ht.randint(-150, 150)
    y0 = ANN_Y + 50 + ht.randint(0, 40)
    if P[x, y0] == INK: continue
    for k in range(ht.randint(8, 30)): put(x + (k // 9) * (1 if i % 2 else -1), y0 + k, col('C', 2.6 - k * 0.04))

# ------------------------------------------------------------------ 8. prayer ropes from the veil to the cave walls
RIB = [col('X', 4), col('G', 4), col('I', 6), col('S', 5), col('P', 5), col('X', 6), col('G', 6)]
def rope(x0, y0, x1, y1, sag, seed, lamps=(0.33, 0.68)):
    rr = random.Random(seed)
    n = int(abs(x1 - x0) * 1.2)
    lamp_i = {int(n * t) for t in lamps}
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)
        put(x, y, col('O', 2)); put(x, y - 1, col('O', 3.5))
        if i % 7 == 0 and 0.04 < t < 0.96:                                                   # ribbons
            c = rr.choice(RIB); ln = rr.randint(3, 8)
            for k in range(1, ln): put(x + (k > ln // 2) * (1 if rr.random() < 0.5 else 0), y + k, c)
        if i in lamp_i:
            for k in range(1, 5): put(x, y + k, col('O', 1))
            for (dx, dy, v) in ((0, 5, 7), (1, 5, 6), (0, 6, 7), (1, 6, 5), (0, 7, 5), (-1, 6, 4)):
                put(x + dx, y + dy, col('G', v), glow=True)
            LANTERNS.append(dict(x=int(x), y=int(y + 6), r=14))
rope(CX - 128, 528, 14, 418, 44, 1)
rope(CX + 128, 528, W - 12, 436, 48, 2)
rope(CX - 96, 482, 60, 330, 30, 3, lamps=(0.5,))
rope(CX + 96, 482, W - 50, 344, 34, 4, lamps=(0.5,))

# ------------------------------------------------------------------ 9. the temple at the foot, guarded by two stone priests
def temple():
    for y in range(TY - 150, TY - 8):
        for x in range(TX - 112, TX + 113):
            arch = TY - 150 + (112 - math.sqrt(max(0, 112 ** 2 - (x - TX) ** 2))) * 0.9
            if y < arch: continue
            put(x, y, col('R', 0.6 + (nB(x, y) - 0.5) * 0.8))
    for (y0, y1, hw) in ((TY - 118, TY - 96, 46), (TY - 96, TY - 64, 66), (TY - 64, TY - 18, 90)):
        for y in range(y0, y1):
            for x in range(TX - hw, TX + hw + 1):
                u = (x - TX) / hw
                v = 2.0 + 1.4 * (1 - u * u) - 0.9 * max(0.0, u) + (nC(x * 2, y * 2) - 0.5) * 0.8
                if y == y0: v += 1.8
                elif y == y0 + 1: v += 0.8
                if (y - y0) % 8 == 7 or (x + ((y - y0) // 8) * 6) % 15 == 0: v -= 1.0         # ashlar
                put(x, y, col('C', band(v, x, y)))
    for y in range(TY - 92, TY - 70):                                                       # the Hymnar's sign over the door
        for x in range(TX - 30, TX + 31):
            u = (x - TX) / 30.0
            if y < TY - 92 + 22 * (1 - (1 - u * u) ** 0.5) or y > TY - 76: continue
            put(x, y, col('C', 5.4 - abs(u) * 1.5 + (0.8 if y > TY - 79 else 0)))
    for y in range(TY - 76, TY - 64):
        for x in range(TX - 5, TX + 6): put(x, y, col('C', 4.5 - abs(x - TX) * 0.3))
    for cxo in (-76, -50, 50, 76):
        for y in range(TY - 64, TY - 18):
            for dx in range(-4, 5):
                put(TX + cxo + dx, y, col('C', 5.0 - abs(dx) * 0.55 - (0.9 if dx > 1 else 0) + (0.8 if y in (TY - 64, TY - 63) else 0)))
    for y in range(TY - 60, TY - 18):                                                       # the lit doorway
        for x in range(TX - 20, TX + 21):
            arch = TY - 60 + (20 - math.sqrt(max(0, 400 - (x - TX) ** 2))) * 0.7
            if y < arch: continue
            d = abs(x - TX) / 20
            put(x, y, col('G', 6.6 - d * 2.4 - (TY - 18 - y) * 0.015), glow=True)
    for y in range(TY - 36, TY - 18): put(TX - 4, y, INK); put(TX - 3, y, INK)               # someone in the door
    put(TX - 4, TY - 38, INK); put(TX - 3, TY - 38, INK); put(TX - 4, TY - 37, INK); put(TX - 3, TY - 37, INK)
    for x in range(TX - 7, TX + 1): put(x, TY - 40, INK)
    for i in range(8):                                                                      # stair
        y = TY - 18 + i * 3
        for x in range(TX - 26 - i * 5, TX + 27 + i * 5):
            put(x, y, col('C', 4.4 - i * 0.25 - (1 if (x - TX) > 14 + i * 4 else 0)))
            put(x, y + 1, col('C', 2.4)); put(x, y + 2, col('C', 1.4))

def statue(sx, base, face):
    """a hooded stone priest under a broad cap, holding a lantern before him"""
    for y in range(base - 8, base):                                                         # plinth
        for x in range(sx - 16, sx + 17):
            put(x, y, col('C', 3.6 - (x - sx) / 16 * 1.2 + (1.2 if y == base - 8 else 0) - (0.8 if y > base - 3 else 0)))
    for y in range(base - 58, base - 8):                                                    # robe
        t = (y - (base - 58)) / 50
        hw = 7 + 6 * t
        for x in range(int(sx - hw), int(sx + hw) + 1):
            u = (x - sx) / hw
            v = 1.4 + 2.6 * max(0.0, -0.45 * u + 0.85 * math.sqrt(max(0.0, 1 - u * u))) + (nC(x * 2, y) - 0.5) * 0.6
            if (x - sx + 40) % 5 == 0 and t > 0.2: v -= 0.8                                   # folds
            put(x, y, col('C', v))
    for y in range(base - 70, base - 56):                                                   # hood
        for x in range(sx - 7, sx + 8):
            u, w = (x - sx) / 7.0, (y - (base - 62)) / 8.0
            if u * u + w * w <= 1: put(x, y, col('C', 2.0 + 2.4 * max(0.0, -0.4 * u - 0.3 * w + 0.7)))
    for x in range(sx - 3 + face, sx + 4 + face): put(x, base - 62, col('C', 0.6)); put(x, base - 61, col('C', 0.6))
    for y in range(base - 80, base - 67):                                                   # broad cap
        for x in range(sx - 18, sx + 19):
            u, w = (x - sx) / 18.0, (base - 68 - y) / 12.0
            if w < 0 or w > (1 - u * u) ** 0.7: continue
            put(x, y, col('C', 2.0 + 3.0 * (1 - w) * max(0.0, 1 - abs(u + 0.3)) + (1 if w < 0.12 else 0)))
    for x in range(sx - 18, sx + 19): put(x, base - 67, col('M', 2.6 - abs(x - sx) / 18))
    lx, ly = sx + face * 9, base - 40                                                       # the lantern
    for k in range(4): put(lx, ly - 4 + k, col('C', 2))
    for (dx, dy, v) in ((0, 0, 8), (1, 0, 7), (-1, 0, 6), (0, 1, 7), (1, 1, 6), (-1, 1, 5), (0, 2, 5), (0, -1, 6)):
        put(lx + dx, ly + dy, col('G', v), glow=True)
    LANTERNS.append(dict(x=lx, y=ly + 1, r=18))
temple()
statue(TX - 150, TY + 4, 1)
statue(TX + 150, TY + 4, -1)

# ------------------------------------------------------------------ 10. the cap: half Growth, half Decay
def seam_x(y):
    return CX + 16 * math.sin(y / 27.0) + 22 * (nD(5, y) - 0.5)
def cap_halfwidth(y):
    k = (RIM_Y - y) / (RIM_Y - CAP_TOP)
    return CAP_RX * math.sqrt(max(0.0, 1 - k * k)) if k < 1 else 0
for x in range(W):
    ct = cap_top(x)
    if ct is None: continue
    rim = rim_y(x)
    for y in range(max(0, int(ct)), int(rim) + 1):
        t = max(0.0, (y - ct) / max(1.0, rim - ct))                 # 0 crown .. 1 rim
        hwid = max(30.0, cap_halfwidth(y))
        xr = max(-0.999, min(0.999, (x - CX) / hwid))
        side = abs(xr) ** 3
        sil = y - ct
        lam = 0.12 + 0.8 * t ** 1.8 - 0.35 * side + 0.3 * max(0.0, -xr) * (1 - t) ** 1.5   # + a cool key light upper left
        ring_t = (y - CAP_TOP) / (RIM_Y - CAP_TOP)
        k = int(ring_t * 34)
        fy = ring_t * 34 - k
        nsc = 26 + k * 7
        jit = (h32(k, 1) % 100) / 100.0
        phi = math.asin(xr) / math.pi + 0.5 + jit / nsc
        ci = int(phi * nsc)
        fx = phi * nsc - ci
        cell = h32(k, ci, 5) % 100
        sw = 0.34 + 0.25 * ((h32(k, ci, 6) % 100) / 100.0)
        scale = (((fx - 0.5) / sw) ** 2 + ((fy - 0.6) * 2.6) ** 2 < 1) and k > 1 and cell > 48 + ring_t * 40
        growth = x < seam_x(y)
        if growth:
            v = 1.0 + 4.2 * lam + (nB(x, y) - 0.5) * 0.5
            if scale:
                v = 1.0 + 3.4 * lam + (1.4 if fy > 0.82 else 0)
                P[x, y] = col('O', band(v + 1.6, x, y)) if cell > 70 else col('C', band(v, x, y))
                continue
            if cell < 12 and t > 0.35 and fy < 0.5: P[x, y] = col('S', band(1.5 + 3 * lam, x, y)); continue   # moss tufts
            if sil < 3: v += 1.6
            P[x, y] = col('C', band(min(8.5, v), x, y))
        else:
            v = 0.5 + 3.2 * lam + (nB(x, y) - 0.5) * 0.8
            if scale:
                if cell < 35: v = 0.2                                                               # rotted out: holes
                elif cell < 60: v = 0.5 + 2.0 * lam + (1.2 if fy > 0.82 else 0)
                else: v += 0.8 + (1.2 if fy > 0.85 else 0)
            if nC(x * 1.5, y * 1.5) > 0.84 and t > 0.25: v += 1.5                                  # wet slime glints
            if sil < 3: v += 1.2
            P[x, y] = col('X', band(max(0.0, v), x, y))
    g = x < seam_x(rim)                                                                         # the thick lip of the rim
    put(x, rim, col('C', 6.6) if g else col('X', 5)); put(x, rim - 1, col('C', 5.2) if g else col('X', 3.4))
    put(x, rim - 2, col('C', 3.4) if g else col('X', 1.6))
for y in range(0, RIM_Y + 1):                                                                   # the seam, stitched with mycelium
    sx = seam_x(y)
    if cap_top(int(sx)) is None or y < cap_top(int(sx)): continue
    put(sx, y, col('M', 5), glow=True); put(sx + 1, y, col('M', 3), glow=True)
    k = y % 11
    if k < 4: put(sx - 1 - k, y + k, col('M', 4), glow=True); put(sx + 2 + k, y + k, col('M', 4), glow=True)
r = random.Random(9)
for i in range(90):                                                                             # growth: sprouting mushrooms
    x = r.randint(0, CX - 50); base = rim_y(x) - r.randint(4, 60)
    if base < (cap_top(x) or 0) + 6: continue
    h = r.randint(3, 10)
    for yy in range(int(base) - h, int(base) + 1): put(x, yy, col('C', 6.5))
    cw = r.randint(1, 3)
    for dx in range(-cw, cw + 1): put(x + dx, int(base) - h, col('C', 8 if abs(dx) < cw else 6))
    if r.random() < 0.35: put(x, int(base) - h - 1, col('M', 6), glow=True)
drips = []
for i in range(30):                                                                             # decay: drips from the rotting rim
    x = r.randint(CX + 40, W - 1); y0 = rim_y(x)
    ln = r.randint(6, 46)
    for yy in range(int(y0), int(y0 + ln)): put(x, yy, col('X', 3 - (yy - y0) / ln))
    put(x, y0 + ln, col('X', 6)); put(x, y0 + ln + 1, col('X', 4)); put(x + 1, y0 + ln, col('X', 3))
    drips.append(dict(x=x, y=int(y0 + ln)))

# ------------------------------------------------------------------ 11. the gills (their own glow layer) + threads from the rim
for x in range(W):
    uy = under_y(x)
    if uy is None: continue
    rim = rim_y(x)
    for y in range(int(rim) + 1, int(uy) + 1):
        if abs(x - CX) < stalk_hw(y) - 2 and y >= STALK_TOP - 10: continue
        d = (y - rim) / max(1.0, uy - rim)
        ex, ey = (x - CX) / CAP_RX, max(0.0, (y - RIM_Y + 6)) / UND
        rho = math.hypot(ex, ey); th = math.atan2(ey, ex)
        gi = th * 58 / math.pi + nB(x * 0.25, y * 0.5) * 0.9
        gid = int(math.floor(gi))
        edge = abs(gi - gid - 0.5) > 0.38
        lum = (h32(gid, 17) % 4)
        side = min(1.0, abs(ex) / 0.75)
        if edge and rho > 0.16 and (side < 0.6 or (h32(gid, 3) % 3 == 0 and side < 0.95)):
            v = 1.6 + lum * 0.7 + (1 - rho) * 1.4 - d * 0.4 - side * 1.2
            put(x, y, col('M', v), gill=True)
            GI[x, y] = col('M', min(9, v + 2.4)) + (255,)
        else:
            put(x, y, col('M', 0.4 + (0.6 if d < 0.15 else 0) + (nC(x, y) > 0.7) * 0.6))
    if abs(x - CX) >= stalk_hw(uy + 1) - 2: put(x, uy + 1, col('M', 0.6))
for i in range(46):                                                                             # luminous threads off the gills
    x = r.randint(10, W - 10)
    if abs(x - CX) < 110: continue
    y0 = under_y(x)
    if y0 is None: continue
    ln = r.randint(8, 54)
    for k in range(ln): put(x, y0 + 1 + k, col('M', 1.4 + (k > ln - 4) * 1.2))
    put(x, y0 + ln + 1, col('M', 7), glow=True)

# keep only glow that is actually visible
for y in range(H):
    for x in range(W):
        g = GL[x, y]
        if g[3] and tuple(P[x, y]) != tuple(g[:3]): GL[x, y] = (0, 0, 0, 0)
img.save(f'{OUT}/hymnar.png')
gil.save(f'{OUT}/hymnar_gills.png')
glw.save(f'{OUT}/hymnar_glow.png')
step = max(1, len(path) // 110)
json.dump(dict(size=[W, H], signal=[[round(px_), round(py_)] for (px_, py_) in path[::step]] + [[round(path[-1][0]), round(path[-1][1])]],
               temple=dict(x=TX, y=TY - 40), drips=drips[:14], rimY=RIM_Y, lanterns=LANTERNS),
          open(f'{OUT}/hymnar.json', 'w'), indent=1)
print('ok', OUT, len(LANTERNS), 'lanterns')
