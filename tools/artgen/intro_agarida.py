"""The opening shot of the intro: Agarida, the sacred giant mushroom of the Obazoba cult, in a cavern deep under the
earth. 1067x1000 -- taller than the screen; the scene pans from the cap down to the temple of the Highest Humenium
Council at its foot.

Agarida is NOT the god: Obazoba has no body, he is an ideal. Agarida is his shrine -- a colossal mushroom drawn with a
real mushroom's anatomy, seen from the cavern floor:
  * the cap is a ray-cast dome seen from below, so its surface pattern wraps round it and the gills show under the
    margin; half Growth (pale, fibrous, with brown parasol scales and a dark disc, a striate margin with veil tatters,
    troops of small mushrooms) and half Decay (rust-brown, its cuticle cracked into areoles, rot pits, mould, a sagging
    torn margin that drips), the seam stitched with glowing mycelium;
  * the gills are radial lamellae with shorter lamellulae between them; they are the light of the cavern (own layer);
  * the stalk flares into the gills (decurrent lines), carries a hanging membranous ring, and below it the brown
    snakeskin bands of a parasol; it ends in a bulb sheathed in a torn volva; mycelial cords spread over the floor.
Pilgrims climb a spiral walkway round the stalk, prayer ribbons hang on ropes from the ring to the cave walls, two
stone priests guard the temple door carved into the bulb.

python3 intro_agarida.py <outdir>  ->  agarida.png, agarida_gills.png (gill glow, flared by the scene when the signal
arrives), agarida_glow.png (veins + lights, pulsed with ADD), agarida.json (signal path, lanterns, drips)."""
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
nG, nH = make_noise(2, 47, W, H), make_noise(24, 48, W, H)

GILL = {}                                                                                   # gill pixel -> its colour in P
def put(x, y, c, glow=False, gill=False):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H:
        P[x, y] = c
        if glow: GL[x, y] = c + (255,)
        if gill: GI[x, y] = c + (255,); GILL[(x, y)] = c

def mix(k1, k2, f, v, x, y):
    """switch between two ramps along an organic (noise) boundary -- never a checkerboard over large areas"""
    return col(k2 if f > nE(x * 1.3 + 17, y * 1.3 + 5) else k1, band(v, x, y))

BAY4 = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))
def smooth(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)

def norm(v):
    l = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2) or 1.0
    return (v[0] / l, v[1] / l, v[2] / l)

def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

# ------------------------------------------------------------------ 0. geometry
HORIZON = 790                                   # eye level: the cap is seen from below, the volva from just above
def tilt(y): return max(-0.1, min(0.3, (HORIZON - y) / 1500.0))
CAP_R, CAP_H, CAP_D, CAP_L, CAP_U, CAP_T = 512, 236, 54, 24, 16, 0.10   # radius, dome, gill bowl, margin curl, umbo, view
CAP_C = math.sqrt(1 - CAP_T ** 2)
RC_Y = 318                                      # screen y of the rim plane's centre
STALK_TOP, ANN_Y, ANN_L, BULB_Y, FLOOR_Y, VOLVA_Y = 300, 446, 74, 868, 905, 818
TX, TY = CX, 966                                # temple stair foot
LANTERNS = []                                   # warm lights the scene makes flicker
KEY = norm((-0.5, 0.62, 0.6))                   # cool cavern light from the upper left

def stalk_cx(y):
    t = max(0.0, min(1.0, (y - STALK_TOP) / (BULB_Y - STALK_TOP)))
    return CX + 9 * math.sin(math.pi * t)                                                   # a slight living lean
def stalk_hw(y):
    t = max(0.0, (y - STALK_TOP) / (BULB_Y - STALK_TOP))
    return (70 + 28 * t ** 1.4 + 46 * math.exp(-max(0.0, y - STALK_TOP + 16) / 22.0)       # flares into the gills
            + 150 * math.exp(-((y - BULB_Y) / 50.0) ** 2) + 30 * max(0.0, (y - BULB_Y) / 40.0))

# ------------------------------------------------------------------ the cap model + a column ray-caster for it
def cap_model(R, Hc, Dd, Lm, U, wav, sag):
    """profile of a convex cap with an umbo and an in-curled margin; X right, Y up from the rim plane, Z to the viewer"""
    def prof(X, Z):
        r = math.hypot(X, Z); a = math.atan2(X, Z)
        rho = r / (R * wav(a))
        q = min(rho, 1.0)
        sg = sag(a) * q ** 4
        top = (Hc + Lm) * (1 - q ** 2.2) ** 0.55 + U * math.exp(-(q / 0.2) ** 2) - Lm - sg
        bot = Dd * (1 - q ** 1.6) - Lm * smooth(0.7, 1.0, q) - sg
        return top, bot, rho, a
    return prof

def render_cap(cx, rcy, R, prof, st, step=0.75):
    """orthographic view from below at sin(elevation) st: per screen column, rasterise the cross-section of the solid
    (top curve + underside curve) and keep the surface nearest the viewer. -> {(x, y): (t, surf 0 top / 1 under, Y, Z)}"""
    ct = math.sqrt(1 - st * st)
    best = {}
    for x in range(max(0, int(cx - R * 1.06)), min(W, int(cx + R * 1.06) + 1)):
        X = x + 0.5 - cx
        runs, cur = [], []
        Z = -R * 1.06
        while Z <= R * 1.06:
            top, bot, rho, a = prof(X, Z)
            if rho <= 1: cur.append((Z, top, bot))
            elif cur: runs.append(cur); cur = []
            Z += step
        if cur: runs.append(cur)
        for run in runs:
            poly = [(Z, Yt, 0) for (Z, Yt, Yb) in run] + [(Z, Yb, 1) for (Z, Yt, Yb) in reversed(run)]
            for i in range(len(poly) - 1):
                (Z0, Y0, f0), (Z1, Y1, f1) = poly[i], poly[i + 1]
                y0 = rcy - (Y0 * ct + Z0 * st); y1 = rcy - (Y1 * ct + Z1 * st)
                t0 = -Y0 * st + Z0 * ct; t1 = -Y1 * st + Z1 * ct
                lo, hi = (y0, y1) if y0 <= y1 else (y1, y0)
                for yy in range(math.ceil(lo), math.floor(hi) + 1):
                    k = 0.0 if hi == lo else (yy - y0) / (y1 - y0)
                    t = t0 + (t1 - t0) * k
                    b = best.get((x, yy))
                    if b is None or t > b[0]:
                        best[(x, yy)] = (t, f0 if f0 == f1 else (0 if k < 0.5 else 1), Y0 + (Y1 - Y0) * k, Z0 + (Z1 - Z0) * k)
    return {k: v for k, v in best.items() if 0 <= k[1] < H}

def normal(prof, X, Z, surf):
    i = 1 if surf else 0
    dx = (prof(X + 1, Z)[i] - prof(X - 1, Z)[i]) / 2; dz = (prof(X, Z + 1)[i] - prof(X, Z - 1)[i]) / 2
    return norm((-dx, 1, -dz)) if surf == 0 else norm((dx, -1, dz))

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

# ------------------------------------------------------------------ 2. lesser mushrooms at depth (same anatomy, in the haze)
def lesser(mx, base, cap_y, cw, sw, depth, lean=0.0, ring=False):
    fog = depth
    key, dim = ('g', 0.0) if fog > 0.6 else ('C', 0.6)
    for y in range(cap_y - 4, base):                                                         # stalk with a bulb
        t = (y - cap_y) / max(1, base - cap_y)
        hw = sw * (1 + 0.25 * t * t + 0.9 * math.exp(-((1 - t) / 0.08) ** 2))
        mx_ = mx + lean * (1 - t) * (base - cap_y)
        for x in range(int(mx_ - hw), int(mx_ + hw) + 1):
            u = (x - mx_) / hw
            v = 0.8 + 2.4 * max(0.0, -0.4 * u + 0.9 * math.sqrt(max(0.0, 1 - u * u))) - fog * 0.8 + (nB(x * 3, y * 0.3) - 0.5) * 0.6
            v += math.exp(-(y - cap_y) / 16.0) * 1.6                                           # lit by its own gills
            if ring and abs(y - cap_y - (base - cap_y) * 0.2) < 2: v += 1.0
            put(x, y, col(key, band(max(0.3, v - dim), x, y)))
    mx += lean * (base - cap_y)
    prof = cap_model(cw, cw * 0.46, cw * 0.1, max(1.0, cw * 0.03), 0,
                     lambda a: 1 + 0.03 * math.sin(5 * a + cw) + 0.02 * math.sin(9 * a), lambda a: 0.0)
    st = 0.12
    for (x, y), (t, surf, Yw, Z) in render_cap(mx, cap_y, cw, prof, st, step=1.0).items():
        X = x + 0.5 - mx
        top, bot, rho, a = prof(X, Z)
        N = normal(prof, X, Z, surf)
        if surf == 0:
            d = max(0.0, dot(N, KEY))
            v = 0.8 + 3.6 * d - fog * 0.9 + (nB(x * 2, y * 2) - 0.5) * 0.5 + (nC(a * cw * 2 + 500, rho * 6) - 0.5) * 0.5
            v += 1.2 * (1 - max(0.0, -N[1] * st + N[2] * math.sqrt(1 - st * st))) ** 3           # rim of haze
            put(x, y, col(key, band(max(0.3, v - dim), x, y)))
        else:
            g = (a / math.tau + 0.5) * cw * 1.6
            v = 1.4 + 1.6 * rho - fog * 1.0 + (0.9 if (g % 1) < 0.4 and rho > 0.3 else 0)
            put(x, y, col('M', v), glow=True)
for args in ((176, 872, 712, 34, 4, 0.85, 0.03), (896, 866, 700, 40, 5, 0.85, -0.02), (338, 884, 770, 24, 3, 0.9, 0.05),
             (736, 884, 760, 28, 3, 0.9, -0.04), (108, 905, 566, 100, 14, 0.5, 0.04, True), (982, 910, 604, 116, 16, 0.45, -0.03, True),
             (262, 930, 724, 58, 8, 0.3, -0.05), (838, 930, 708, 66, 9, 0.3, 0.04)):
    lesser(*args)

# ------------------------------------------------------------------ 3. the floor, glowing mycelial mats, mycelial cords
for y in range(FLOOR_Y - 20, H):
    z = (y - FLOOR_Y + 20) / (H - FLOOR_Y + 20)
    for x in range(W):
        v = 1.0 + (1 - z) * 0.6 + (nB(x * 0.4, y * 2.5) - 0.5) * 0.9 + math.exp(-((x - CX) / 260.0) ** 2) * 1.2
        mat = nE(x * 0.5, y * 2.0)
        if mat > 0.8 and abs(x - CX) < 420:
            put(x, y, col('M', 1 + (mat > 0.86) + (nF(x, y) > 0.85)), glow=mat > 0.86); continue
        P[x, y] = mix('R', 'g', 1 - abs(x - CX) / 340.0, v, x, y)

def cord(x, y, ang, w, n, seed, depth=0):
    """a mycelial cord (rhizomorph): pale, fibrous, fuzzy at its edges, forking into thinner strands"""
    rr = random.Random(seed); pts = []
    for s in range(n):
        x += math.cos(ang) * 2.0; y += math.sin(ang) * 2.0
        ang += (rr.random() - 0.5) * 0.12
        w = max(1.2, w * 0.993 + (0.04 if y > 960 else 0))
        pts.append((x, y, w))
    for i, (x, y, w) in enumerate(pts):
        hy = w * 0.55 + 0.01
        for xx in range(int(x - w) - 1, int(x + w) + 2):
            for yy in range(int(y - hy) - 2, int(y + hy) + 2):
                u = (yy - y) / hy
                if abs(u) > 1:
                    if abs(u) < 1.5 and h32(xx, yy, seed) % 9 == 0: put(xx, yy, col('C', 2.4 - depth))   # hyphal fuzz
                    continue
                fib = nG(i * 0.7 + seed * 31, (u + 1) * 5.5)
                v = 0.7 + 2.6 * (1 - abs(u)) ** 0.7 - 1.0 * u + (fib - 0.5) * 1.4 - depth * 0.5
                if nE(xx * 2, yy * 2) > 0.72: put(xx, yy, col('R', band(1.4 + v * 0.4, xx, yy))); continue   # soil on it
                put(xx, yy, col('C', band(max(0.4, v), xx, yy)))
    if depth == 0:
        for j in range(40, n - 40, 70 + seed % 23):                                         # forks
            bx, by, bw = pts[j]
            a = math.atan2(pts[j + 1][1] - by, pts[j + 1][0] - bx) + rr.choice((-1, 1)) * rr.uniform(0.3, 0.6)
            cord(bx, by, a, bw * 0.5, rr.randint(14, 30), seed * 7 + j, depth=1)
    for j in range(18, n, rr.randint(26, 40)):                                             # glowing knots
        bx, by, bw = pts[j]
        put(bx, by, col('M', 7), glow=True); put(bx + 1, by, col('M', 5), glow=True); put(bx, by - 1, col('M', 5), glow=True)
    return pts
ROOTS = []
for i, (side, ang, w, n) in enumerate(((1, 0.10, 16, 270), (-1, 0.12, 16, 270), (1, 0.42, 20, 150), (-1, 0.40, 20, 150),
                                      (1, 0.75, 22, 80), (-1, 0.78, 22, 80), (1, -0.06, 10, 230), (-1, -0.05, 10, 230))):
    a = ang if side > 0 else math.pi - ang
    ROOTS.append(cord(CX + side * 165, BULB_Y + 20 + (i % 3) * 5, a, w, n, i + 20))

# ------------------------------------------------------------------ 4. the cap: ray-cast from below, half Growth, half Decay
NOTCHES = [(0.52, 0.05, 0.03), (0.93, 0.07, 0.025), (1.22, 0.04, 0.02), (1.42, 0.06, 0.03)]
def cap_wav(a):
    w = 1 + 0.012 * math.sin(5 * a + 1.3) + 0.008 * math.sin(11 * a + 0.4) + 0.03 * (nH(math.cos(a) * 60 + 300, math.sin(a) * 60 + 300) - 0.5)
    if a > 0.15:                                                                            # the Decay half: torn margin
        for (c, d, wd) in NOTCHES: w -= d * max(0.0, 1 - abs(a - c) / wd)
    return w
def cap_sag(a): return 26 * smooth(0.1, 1.4, a)                                             # the Decay half droops
def seam_a(rho): return -0.02 + 0.05 * math.sin(rho * 9 + 0.8) + 0.07 * (nD(rho * 60, 7) - 0.5)

CAP = cap_model(CAP_R, CAP_H, CAP_D, CAP_L, CAP_U, cap_wav, cap_sag)
def _top(q): return (CAP_H + CAP_L) * (1 - q ** 2.2) ** 0.55 + CAP_U * math.exp(-(q / 0.2) ** 2)
ARC = [0.0]                                                                                 # arc length down a meridian:
for i in range(1, 1001):                                                                    # the cap's texture coordinate
    ARC.append(ARC[-1] + math.hypot(CAP_R / 1000.0, _top(i / 1000.0) - _top((i - 1) / 1000.0)))
def arc(rho):
    i = min(999, int(rho * 1000)); f = rho * 1000 - i
    return ARC[i] + (ARC[i + 1] - ARC[i]) * f
def arc_inv(m):
    lo, hi = 0, 1000
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if ARC[mid] < m: lo = mid
        else: hi = mid
    return hi / 1000.0
CAPPX = render_cap(CX, RC_Y, CAP_R, CAP, CAP_T)
VIEW = (0.0, -CAP_T, CAP_C)
HALF = norm((KEY[0] + VIEW[0], KEY[1] + VIEW[1], KEY[2] + VIEW[2]))

def voro(q, m, cell, seed):
    """distance-to-crack measure of a Voronoi tiling (small = on a crack)"""
    gx, gy = math.floor(q / cell), math.floor(m / cell)
    d1 = d2 = 1e9
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            h = h32(gx + i, gy + j, seed)
            px_ = (gx + i + (h % 1000) / 1000.0) * cell; py_ = (gy + j + ((h // 1000) % 1000) / 1000.0) * cell
            d = (q - px_) ** 2 + (m - py_) ** 2
            if d < d1: d2 = d1; d1 = d
            elif d < d2: d2 = d
    return math.sqrt(d2) - math.sqrt(d1)

def scale_at(rho, a):
    """the parasol scales of the Growth half: concentric rings of teardrop scales pointing at the margin.
    -> None, ('scale', edge 0..1, fy) or ('shadow',)"""
    ring_w = 21.0
    mr = arc(rho)
    k = int(mr / ring_w); fy = mr / ring_w - k
    nc = max(5, int(round(math.tau * arc_inv((k + 0.5) * ring_w) * CAP_R / 25.0)))
    ph = (a / math.tau + 0.5) * nc + (h32(k, 1) % 1000) / 1000.0
    ci = int(math.floor(ph)); fx = ph - ci; ci %= nc
    hs = h32(k, ci, 5)
    p = 0.97 if rho < 0.3 else max(0.0, 0.97 - (rho - 0.3) * 2.1)
    if (hs % 1000) / 1000.0 >= p: return None
    cxs = 0.5 + ((hs >> 10) % 100 - 50) / 260.0; cys = 0.4
    sx = 0.36 + ((hs >> 17) % 100) / 900.0; sy = 0.52
    dy = (fy - cys) / sy
    wdy = sx * (1 - 0.5 * (dy + 1) / 2)
    if -1 <= dy <= 1:
        span = wdy * math.sqrt(max(0.0, 1 - dy * dy))
        if abs(fx - cxs) < span: return ('scale', abs(fx - cxs) / max(0.01, span), dy)
    if 1 < dy < 1.35 and abs(fx - cxs) < wdy * 0.5: return ('shadow',)
    return None

UNDER = {}                                                                                  # underside pixels, shaded below
for (x, y), (t, surf, Yw, Z) in CAPPX.items():
    X = x + 0.5 - CX
    top, bot, rho, a = CAP(X, Z)
    rho = min(rho, 1.0)
    if surf == 1: UNDER[(x, y)] = (rho, a, Z); continue
    N = normal(CAP, X, Z, 0)
    d = max(0.0, dot(N, KEY)); nv = max(0.0, dot(N, VIEW))
    rim = (1 - nv) ** 3
    spec = max(0.0, dot(N, HALF)) ** 24
    lit = 0.16 + 0.84 * d
    q, m = a * rho * CAP_R + 3000, arc(rho)                                                 # surface coords (px, >= 0: the
                                                                                            # value noise needs positive input)
    fib = nG(q * 0.9 + 400, m * 0.07)                                                       # radial fibrils
    ds = (a - seam_a(rho)) * rho * CAP_R                                                    # signed distance to the seam
    if abs(ds) < 1.3 and rho > 0.04:
        put(x, y, col('M', 5.4 - abs(ds)), glow=True); continue
    mk = m % 11
    if mk < 3.2 and abs(ds) < 5.5 - mk * 1.3 and rho > 0.08:                                # stitches across it
        put(x, y, col('M', 4), glow=True); continue
    if ds < 0:                                                                              # ---- Growth
        v = 0.9 + 6.8 * lit + (fib - 0.5) * 1.1 + rim * 1.4 + (nB(q * 0.5 + 90, m * 0.5) - 0.5) * 0.5
        if rho > 0.93: v += (rho - 0.93) * 18 * (0.5 + 0.5 * nv)                            # thin translucent margin
        if rho < 0.17:                                                                      # the dark disc round the umbo
            vb = 1.0 + 5.0 * lit + (nC(q * 0.8, m * 0.8) - 0.5) * 1.4 + rim + (2.0 if rho < 0.05 and d > 0.6 else 0)
            P[x, y] = col('O', band(vb, x, y)); continue
        sc = scale_at(rho, a)
        if sc and sc[0] == 'scale':
            vb = 1.0 + 4.4 * lit + (fib - 0.5) * 1.6 + rim * 0.8
            if sc[2] < -0.55: vb += 1.0                                                     # scale's upper edge, lit
            elif sc[2] > 0.7: vb += 0.7                                                     # its curled-up tip
            elif sc[1] > 0.8: vb -= 0.8
            P[x, y] = col('O', band(vb, x, y)); continue
        if sc: v -= 1.6                                                                     # the tip's little shadow
        if rho > 0.9:                                                                       # striate margin
            g = (a / math.tau + 0.5) * 330
            if abs(g % 1 - 0.5) < 0.16 and rho > 0.9 + 0.06 * ((h32(int(g), 9) % 100) / 100.0): v -= 1.3
        P[x, y] = col('C', band(min(9.4, max(0.5, v)), x, y))
    else:                                                                                   # ---- Decay
        v = 0.5 + 4.3 * lit + (fib - 0.5) * 0.7 + rim * 1.0
        cell = 12 + rho * 9
        crack = voro(q, m, cell, 77)
        up = voro(q, m - 1.5, cell, 77)                                                     # the crack just above?
        pit = nH(q * 2.0 + 200, m * 2.0)
        if pit > 0.79 and rho > 0.3:                                                        # rot pits
            if pit > 0.82: P[x, y] = col('X', 0.2 + (nF(x, y) > 0.75) * 0.9); continue
            v += 2.0                                                                        # their wet lip
        elif crack < 0.9 + rho * 0.9 and rho > 0.14:                                        # areolate cracks
            P[x, y] = col('C', 1.2 + 1.6 * lit) if rho > 0.7 and h32(x, y) % 4 == 0 else col('X', 0.4 + lit); continue
        elif up < 0.9 + rho * 0.9 and rho > 0.14: v += 1.3                                  # a plate's lifted, lit edge
        mould = nE(q * 0.9 + 700, m * 0.9)
        if mould > 0.82 and 0.3 < rho < 0.92 and h32(x, y, 3) % 3:                          # mould fuzz
            P[x, y] = col('C', band(3.0 + 4.0 * lit + (nF(x, y) - 0.5) * 2, x, y)); continue
        v += spec * 1.6                                                                     # slime sheen
        if rho > 0.92: v -= (rho - 0.92) * 10
        P[x, y] = col('X', band(min(7.4, max(0.0, v)), x, y))

# the gills: radial lamellae, every 2nd/4th a shorter lamellula; light of the cavern, so they get their own layer
NG = 320
GV = {k: (v[1] / math.tau + 0.5) * NG for k, v in UNDER.items()}
for (x, y), (rho, a, Z) in UNDER.items():
    g = GV[(x, y)]
    fp = 0.0
    for nb in ((x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)):
        if nb in GV:
            dg = abs(GV[nb] - g)
            fp = max(fp, min(dg, NG - dg))
    gi = int(g); fr = g - gi
    tier = 0 if gi % 4 == 0 else 1 if gi % 2 == 0 else 2
    exists = rho > (0.24, 0.45, 0.7)[tier]
    decay = a > seam_a(rho) and a > -0.1
    base = 0.5 + 1.9 * smooth(0.22, 1.0, rho) + (nB(x, y) - 0.5) * 0.4
    if rho > 0.965:                                                                         # the margin's underside lip
        put(x, y, col('X', 2.6 + (rho > 0.985)) if decay else col('C', 3.2 + (rho > 0.985) * 1.4)); continue
    amp = max(0.0, 1 - fp * 2.6) if exists else 0.0                                         # dense gills fade to their mean
    wave = math.cos(math.tau * (fr - 0.5))
    on = amp > 0.25 and wave * amp > 0.55 + (BAY4[y % 4][x % 4] / 16.0 - 0.5) * 0.3
    side = exists and not on and wave * amp > -0.1
    lum = (h32(gi, 17) % 4) * 0.35
    if decay:
        broken = nE(g * 3.0, rho * 30) > 0.62
        if on and not broken:                                                               # a dim, sick glow
            put(x, y, col('M', base + 0.6 + lum * 0.5) if nE(x, y) > 0.7 else col('X', 2.4 + base * 0.8 + lum), gill=True)
            GI[x, y] = col('M', min(9, base + 1.2 + lum)) + (255,)
        else: put(x, y, col('X', 0.4 + base * 0.5))
        continue
    if on:
        v = base + 2.2 + lum
        put(x, y, col('M', v), gill=True); GI[x, y] = col('M', min(9, v + 2.4)) + (255,)
    elif side:
        v = base + 0.9 + lum * 0.5
        put(x, y, col('M', v), gill=True); GI[x, y] = col('M', min(9, v + 1.5)) + (255,)
    else:
        put(x, y, col('M', base * 0.7))

# ------------------------------------------------------------------ 5. the pilgrims' spiral walkway (back half first)
WALK_TH0, WALK_TURNS, WALK_Y0, WALK_Y1 = -0.5, 1.75, 840, 580
def walkway(front):
    th1 = WALK_TH0 + WALK_TURNS * math.tau
    N = 3200
    last_post = last_lamp = -9
    pilgrims = {0.04, 0.075, 0.62}
    for i in range(N + 1):
        f = i / N
        th = WALK_TH0 + (th1 - WALK_TH0) * f
        y0 = WALK_Y0 + (WALK_Y1 - WALK_Y0) * f
        R = stalk_hw(y0) + 9
        c = math.cos(th)
        x = stalk_cx(y0) + R * math.sin(th); y = y0 - R * c * tilt(y0)                       # a helix in perspective
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

# ------------------------------------------------------------------ 6. the stalk: fibrous, flaring into the gills, lit by them
def under_gills(x, y):
    """is the front of the stalk at this pixel below the gill surface and not behind the cap's near margin?"""
    hw = stalk_hw(y); X = x + 0.5 - CX
    Zs = math.sqrt(max(0.0, hw * hw - X * X))
    Yw = ((RC_Y - y) - Zs * CAP_T) / CAP_C
    if Yw > CAP(X, Zs)[1]: return False
    c = CAPPX.get((x, y))
    return c is None or c[0] < -Yw * CAP_T + Zs * CAP_C

APEX_Y = int(RC_Y - CAP_D * CAP_C) - 4
for y in range(APEX_Y - 30, BULB_Y + 44):
    hw = stalk_hw(y); cx = stalk_cx(y)
    gl = math.exp(-max(0.0, y - (APEX_Y + 8)) / 55.0)                                       # green light from the gills
    tl = tilt(y)
    for x in range(int(cx - hw), int(cx + hw) + 1):
        if y < STALK_TOP + 30 and not under_gills(x, y): continue
        u = max(-0.999, min(0.999, (x - cx) / hw))
        nz = math.sqrt(1 - u * u)
        th = math.asin(u); sa = th * 92
        diff = max(0.0, -0.45 * u + 0.89 * nz)
        fib = nG(sa * 1.4 + 900, y * 0.045)
        v = 1.5 + 4.3 * diff + (fib - 0.5) * 1.2
        if u > 0.82: v += 0.8 * (u - 0.82) / 0.18                                           # reflected light, far edge
        if abs(u) > 0.975: v = 0.5
        v += math.exp(-((y - 930) / 90.0) ** 2) * math.exp(-((x - CX) / 160.0) ** 2) * 1.4  # the temple's warmth
        if nA(x * 2.2 + 30, y * 1.6) > 0.78: v -= 0.7                                        # bruised, older patches
        y0 = y + hw * nz * tl                                                               # band coordinate in perspective
        if y < STALK_TOP + 48 and abs((sa / 4.6) % 1 - 0.5) < 0.18 and \
                y < STALK_TOP + 14 + 34 * ((h32(int(sa / 4.6), 4) % 100) / 100.0):           # decurrent gill lines
            v -= 1.1
        snake = None
        if y0 > ANN_Y + ANN_L + 6:                                                          # snakeskin below the ring
            yb = y0 + 9 * (nB(sa * 0.5 + 300, 77) - 0.5)                                     # bands wander a little
            per = 19 + 8 * (yb - ANN_Y) / 420
            bi = int(yb / per); fy = yb / per - bi
            ca = sa + 200 + (h32(bi, 2) % 40)                                               # chunks of skin, offset per band
            chl = 9 + (h32(bi, math.floor(ca / 20), 3) % 22)
            ci = math.floor(ca / chl); cf = ca / chl - ci
            hb = h32(bi, ci, 6)
            pk = 0.3 + (hb >> 8) % 40 / 100.0                                               # where the patch hangs lowest
            dep = (0.22 + (hb % 100) / 230.0) * (1 - 0.8 * (abs(cf - pk) / max(pk, 1 - pk)) ** 1.3)
            dep *= smooth(BULB_Y - 20, BULB_Y - 110, y0) * smooth(ANN_Y + ANN_L + 6, ANN_Y + ANN_L + 40, y0)
            gap = cf < 0.1 or hb % 4 == 0 or fy < 0.08 * ((hb >> 4) % 3)
            if fy < dep and not gap:
                snake = 0.5 + 3.4 * diff + (fib - 0.5) * 1.0 + (0.8 if fy < 0.1 else 0) + (u > 0.8) * 0.6 - (dep - fy < 0.06) * 0.5
            elif dep <= fy < dep + 0.1 and not gap: v -= 0.8                                # its shadow on the paler skin
        if snake is not None:
            P[x, y] = col('O', band(snake + 2.3, x, y)); continue
        if gl * (0.6 + 0.4 * abs(u)) > 0.5 + (BAY4[y % 4][x % 4] / 16.0 - 0.5) * 0.3:        # bathed in the gills' green
            P[x, y] = col('M', band(v * 0.55 + gl * 3.0, x, y)); continue
        P[x, y] = col('C', band(max(0.3, v - 0.2), x, y))

# ------------------------------------------------------------------ 7. the volva: the torn sac the bulb sits in
VLOBES = [(-0.92, 20), (-0.68, 58), (-0.42, 30), (-0.12, 44), (0.18, 66), (0.46, 28), (0.7, 52), (0.93, 24)]
CAPSET = {c: i for i, c in enumerate(RAMPS['C'])}
def volva_rim(u):
    h = 0.0
    for (c, ht) in VLOBES: h = max(h, ht * max(0.0, 1 - abs(u - c) / 0.16) ** 1.7)
    return VOLVA_Y + 34 - h + 3 * math.sin(u * 23)
for y in range(VOLVA_Y - 6, FLOOR_Y + 30):
    hv = stalk_hw(min(y, BULB_Y + 30)) * 1.04 + 16
    for x in range(int(CX - hv), int(CX + hv) + 1):
        u = max(-0.999, min(0.999, (x - CX) / hv))
        rim = volva_rim(u)
        if y < rim: continue
        nz = math.sqrt(1 - u * u)
        diff = max(0.0, -0.45 * u + 0.89 * nz)
        fold = math.sin(u * 26 + nB(x * 0.4, y * 0.4) * 5 + (y - rim) * 0.05)                # membrane folds from the lobes
        v = 1.8 + 3.6 * diff + fold * 0.6 + (nC(x * 1.4, y * 0.7) - 0.5) * 0.6
        if y - rim < 2: v += 1.8                                                            # the torn lip
        elif y - rim < 4: v += 0.6
        v -= max(0.0, (y - 878) / 26.0) * 1.4                                               # soil at its foot
        if abs(u) > 0.97: v = 0.4
        if nE(x * 1.8, y * 1.8) > 0.84 and y > 880: P[x, y] = col('O', band(1.0 + diff * 2.5, x, y)); continue
        P[x, y] = col('C', band(max(0.3, v), x, y))
    for x in range(int(CX - hv), int(CX + hv) + 1):                                         # the bulb shadowed by the lip
        u = max(-0.999, min(0.999, (x - CX) / hv)); rim = volva_rim(u)
        if int(rim) == y:                                                                   # the lobe's edge against the bulb
            for k, dv in ((1, 9), (2, 2.2), (3, 1.4), (4, 0.8), (5, 0.4)):
                yy = y - k
                if 0 <= yy < H and tuple(P[x, yy]) in CAPSET:
                    put(x, yy, col('C', 0.8) if dv > 5 else col('C', max(0.4, CAPSET[tuple(P[x, yy])] - dv)))

# ------------------------------------------------------------------ 8. veins: the signal's road (from the city, right) up the stalk
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
    path.append((stalk_cx(yy) + stalk_hw(yy) * (0.55 - 0.45 * t) * 0.85 + 14 * math.sin(yy / 37.0), yy))
vline(path, 5)
for k in range(3):
    ph = rv.random() * 6; pts = []
    for yy in range(BULB_Y + 10, STALK_TOP + 10, -4):
        pts.append((stalk_cx(yy) + stalk_hw(yy) * (0.8 - 0.25 * k / 2) * math.sin(yy / (80 + k * 17) + ph) * (1 if k % 2 else -1), yy))
    vline(pts, 2 + (k % 2), glow=True)
    for j in range(0, len(pts) - 8, 29):
        bx, by = pts[j]; a = rv.choice((-1, 1)) * 0.9 - math.pi / 2
        br = [(bx + math.cos(a) * i * 2.5, by + math.sin(a) * i * 2.5 + i * i * 0.08) for i in range(rv.randint(4, 8))]
        vline(br, 2, glow=True)

walkway(front=True)

# ------------------------------------------------------------------ 9. the ring: a hanging membranous skirt, striate above
def ring_hw(y): return stalk_hw(ANN_Y) + 3 + 40 * max(0.0, (y - ANN_Y) / ANN_L) ** 1.15
RB = ring_hw(ANN_Y + ANN_L)
def ring_edge(u, far=False):
    """screen y of the skirt's lower edge at u (-1..1): the near half hangs higher (we look up at it)"""
    nz = math.sqrt(max(0.0, 1 - u * u))
    tatter = 5 * math.sin(u * 17 + 1) + 7 * (nB(u * 90 + 300, 40 if far else 9) - 0.5) + (6 if h32(int(u * 40), 3) % 5 == 0 else 0)
    return ANN_Y + ANN_L + tatter + (1 if far else -1) * RB * nz * tilt(ANN_Y + ANN_L)
for y in range(ANN_Y - 6, int(ANN_Y + ANN_L + RB * tilt(ANN_Y) + 12)):
    cx = stalk_cx(y)
    for x in range(int(cx - RB - 2), int(cx + RB + 3)):
        ub = (x - cx) / RB
        if abs(ub) > 1: continue
        hw = ring_hw(min(y, ANN_Y + ANN_L))
        top = ANN_Y - 6 + 6 * math.sqrt(max(0.0, 1 - min(1.0, abs(x - cx) / (stalk_hw(ANN_Y) + 3)) ** 2))
        if y < top or abs(x - cx) > hw: continue
        near = ring_edge(ub)
        if y > near:                                                                        # inside of the far half
            if y <= ring_edge(ub, far=True) and abs(x - cx) > stalk_hw(y) - 1:
                P[x, y] = col('C', band(0.6 + (nB(x, y) - 0.5) * 0.6 + 0.8 * max(0.0, ub), x, y))
            continue
        u = max(-0.999, min(0.999, (x - cx) / hw)); nz = math.sqrt(1 - u * u)
        fold = math.sin(u * 7.5 * math.pi / 2 + 3 * nB(x * 0.5, y * 0.2))
        v = 1.0 + 2.8 * max(0.0, -0.45 * u + 0.89 * nz) + fold * 0.75 + (nC(x * 2, y * 0.3) - 0.5) * 0.5
        lt = math.exp(-(y - top) / 14.0)
        if y - top < 26 and x % 3 == 0: v -= 0.6                                             # striations from the gills
        if near - y < 3: v += 1.3                                                            # the thick, rolled lower edge
        if near - y < 1: v -= 1.6
        if abs(u) > 0.97: v = 0.5
        if lt > 0.78 + (BAY4[y % 4][x % 4] / 16.0 - 0.5) * 0.3: P[x, y] = col('M', band(v * 0.6 + lt * 2.6, x, y)); continue
        P[x, y] = col('C', band(max(0.4, v), x, y))
ht = random.Random(8)                                                                       # shreds hanging off it
for i in range(22):
    x = int(stalk_cx(ANN_Y + ANN_L) + ht.uniform(-RB * 0.95, RB * 0.95))
    ub = (x - stalk_cx(ANN_Y + ANN_L)) / RB
    y0 = int(ring_edge(ub))
    for k in range(ht.randint(4, 18)): put(x + (k // 7) * (1 if i % 2 else -1), y0 + k, col('C', 2.8 - k * 0.06))

# ------------------------------------------------------------------ 10. prayer ropes from the ring to the cave walls
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
RY = ANN_Y + ANN_L - 14
rope(int(stalk_cx(RY) - RB + 6), RY, 14, 418, 44, 1)
rope(int(stalk_cx(RY) + RB - 6), RY, W - 12, 436, 48, 2)
rope(int(stalk_cx(RY) - RB * 0.7), RY - 26, 60, 360, 30, 3, lamps=(0.5,))
rope(int(stalk_cx(RY) + RB * 0.7), RY - 26, W - 50, 372, 34, 4, lamps=(0.5,))

# ------------------------------------------------------------------ 11. the temple carved into the bulb, two stone priests
def temple():
    for y in range(TY - 150, TY - 8):
        for x in range(TX - 112, TX + 113):
            arch = TY - 150 + (112 - math.sqrt(max(0, 112 ** 2 - (x - TX) ** 2))) * 0.9
            if y < arch: continue
            put(x, y, col('R', 0.6 + (nB(x, y) - 0.5) * 0.8))
            if y - arch < 2: put(x, y, col('C', 3.6))                                      # the cut edge of the flesh
    for (y0, y1, hw) in ((TY - 118, TY - 96, 46), (TY - 96, TY - 64, 66), (TY - 64, TY - 18, 90)):
        for y in range(y0, y1):
            for x in range(TX - hw, TX + hw + 1):
                u = (x - TX) / hw
                v = 2.0 + 1.4 * (1 - u * u) - 0.9 * max(0.0, u) + (nC(x * 2, y * 2) - 0.5) * 0.8
                if y == y0: v += 1.8
                elif y == y0 + 1: v += 0.8
                if (y - y0) % 8 == 7 or (x + ((y - y0) // 8) * 6) % 15 == 0: v -= 1.0         # ashlar
                put(x, y, col('C', band(v, x, y)))
    for y in range(TY - 92, TY - 70):                                                       # Agarida's sign over the door
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

# ------------------------------------------------------------------ 12. the cap's margin: veil tatters, a troop of small mushrooms, drips
def rim_screen(a):
    """screen position of the cap margin at azimuth a (0 = towards the viewer, + = right)"""
    R = CAP_R * cap_wav(a); X, Z = R * math.sin(a), R * math.cos(a)
    Y = CAP(X * 0.999, Z * 0.999)[1]
    return CX + X, RC_Y - (Y * CAP_C + Z * CAP_T)
r = random.Random(9)
for i in range(70):                                                                         # Growth: veil remnants on the margin
    a = r.uniform(-1.5, -0.05)
    if a > seam_a(1.0) - 0.02: continue
    x, y = rim_screen(a)
    ln, wd = r.randint(3, 13), r.randint(1, 4)
    for k in range(ln):
        hw = wd * (1 - k / ln)
        for dx in range(-int(hw), int(hw) + 1): put(x + dx + (k // 5) * (1 if i % 2 else -1), y + k, col('C', 5.2 - k * 0.22 - (dx > 0) * 0.8))
seen = []
for i in range(400):                                                                        # Growth: a troop of small mushrooms
    if len(seen) >= 16: break
    a = r.uniform(-1.35, -0.12); rho = r.uniform(0.5, 0.88)
    rr_ = rho * CAP_R * cap_wav(a); X, Z = rr_ * math.sin(a), rr_ * math.cos(a)
    if a > seam_a(rho) - 0.05: continue
    Y = CAP(X, Z)[0]
    x, y = int(CX + X), int(RC_Y - (Y * CAP_C + Z * CAP_T))
    if CAPPX.get((x, y), (0, 1))[1] != 0 or any(abs(x - sx) < 26 and abs(y - sy) < 16 for (sx, sy) in seen): continue
    seen.append((x, y))
    for j in range(r.randint(1, 4)):                                                        # a cluster of 1-4
        mx, h, cw = x + r.randint(-7, 7), r.randint(5, 13), r.randint(2, 4)
        base = y + r.randint(-1, 2)
        lean = r.uniform(-0.25, 0.25)
        for k in range(h): put(mx + lean * k, base - k, col('C', 6.2 - (k < 2) * 1.5))
        put(mx + lean * h + 1, base - h // 2, col('C', 3))
        top = base - h
        for dy in range(-cw, 1):
            span = int(cw * math.sqrt(max(0.0, 1 - (dy / (cw + 0.5)) ** 2)) + (1 if dy == 0 else 0))
            for dx in range(-span, span + 1):
                put(mx + lean * h + dx, top + dy, col('O', 7.4 - (dx > 0) * 2.2 - (dy == -cw) * -0.6) if dy < 0 else col('M', 3), glow=dy == 0)
        if r.random() < 0.3: put(mx + lean * h, top - cw - 1, col('M', 6), glow=True)
drips = []
for i in range(60):                                                                         # Decay: slime hanging from the margin
    a = r.uniform(0.08, 1.55)
    if a < seam_a(1.0) + 0.04: continue
    x, y0 = rim_screen(a)
    ln = r.randint(4, 40)
    for yy in range(int(y0), int(y0 + ln)): put(x, yy, col('X', 3.2 - (yy - y0) / ln))
    put(x, y0 + ln, col('X', 6)); put(x, y0 + ln + 1, col('X', 4)); put(x + 1, y0 + ln, col('X', 3))
    drips.append(dict(x=int(x), y=int(y0 + ln)))
for i in range(46):                                                                         # luminous threads off the gills
    a = r.uniform(-1.5, 1.5)
    x, y0 = rim_screen(a + math.pi if abs(a) < 0.9 else a)
    if abs(x - CX) < 140 or a > 0.6: continue
    ln = r.randint(8, 50)
    for k in range(ln): put(x, y0 + 1 + k, col('M', 1.4 + (k > ln - 4) * 1.2))
    put(x, y0 + ln + 1, col('M', 7), glow=True)

# keep only glow that is actually visible
for y in range(H):
    for x in range(W):
        g = GL[x, y]
        if g[3] and tuple(P[x, y]) != tuple(g[:3]): GL[x, y] = (0, 0, 0, 0)
for (x, y), c in GILL.items():                                                              # ... and gills nothing covers
    if tuple(P[x, y]) != tuple(c): GI[x, y] = (0, 0, 0, 0)
img.save(f'{OUT}/agarida.png')
gil.save(f'{OUT}/agarida_gills.png')
glw.save(f'{OUT}/agarida_glow.png')
step = max(1, len(path) // 110)
r.shuffle(drips)
json.dump(dict(size=[W, H], signal=[[round(px_), round(py_)] for (px_, py_) in path[::step]] + [[round(path[-1][0]), round(path[-1][1])]],
               temple=dict(x=TX, y=TY - 40), drips=drips[:14], rimY=RC_Y - 10, lanterns=LANTERNS),
          open(f'{OUT}/agarida.json', 'w'), indent=1)
print('ok', OUT, len(LANTERNS), 'lanterns')
