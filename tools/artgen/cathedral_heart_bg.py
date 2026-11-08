"""The heart of the Egg Cathedral (EggCathedralInteriorScene), 1067x600, the shared camera (raster3d.py). After the
old picture (CathedralHeart.png, its layout kept): a nave of organic gothic piers -- stone shafts grown over by
bundles of living root -- under a pointed vault, and at the back, on a stepped dais, sunk into the end wall like a
window, the great living egg: the Unborn, glowing amber through its membrane, a net of roots over it, shapes moving
inside. The temple the organism made of itself (the journal's words): columns grown like tissue, an altar, an organ,
stained glass.
  left    in the aisle wall a lancet of LIVING glass (cells, not leading; what it remembers: the egg swelling from bare
          ground, a lattice of small lights, the Bishop sealing a door); under it the altar -- no idol, only the dust
          worn away in the shape of two hands -- and a kneeler
  right   the organ, its pipes not metal but ringed like a throat; above it, folded into the wall, the last traces
          of the cathedral's first servants: half-sunk faces and hands
  floor   wet flagstones that mirror the egg's light, roots running out from the dais, candles on iron stands
Light: the egg (warm, strong), candles, and a little grey daylight through the rose window high in the end wall.

    python3 cathedral_heart_bg.py <outdir>   ->  heart.png  (= assets/images/backgrounds/CathedralHeart.png)
Prints the canvas boxes of the hotspots (the egg, the glass, the altar, the organ, the servants)."""
import sys, math
from cathedral_inkit import *
import cathedral_inkit as K

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
K.FOG.update(col=(30, 22, 14), z0=16.0, span=60.0, max=0.32)
rs = Raster()

ZB, WXO, YA = 38.0, 27.0, 26.0          # end wall, aisle walls, aisle vault
PX = 11.0                               # the pier line
YS, YV = 26.0, 47.0                     # the nave vault springs at YS from the piers, apex YV
EGG_C, EGG_A = (0.0, 18.0, 34.0), (11.0, 17.0, 4.6)
ROOT = ramp('#0b0907 #120e0a #1a140e #231b13 #2d2318 #382b1e #443426 #513e2e #5f4936 #6e553f')
BONE = ramp('#1c1915 #29241e #37312a #464037 #565045 #686054 #7a7264 #8d8575 #a09887')
CART = ramp('#1a1614 #26201d #332b27 #413631 #50433c #605148 #72604f #846f5d #967f6c #a8907c')
AMBER = ramp('#1e1209 #2f1d0e #432913 #583619 #6e4520 #85562a #9c6835 #b27c45 #c69257 #d6a86d #e4c088 #f0d8a8')
GLASS = [ramp('#121a26 #1a283a #263a52 #34506c'), ramp('#2a1214 #42191d #5e2429 #7a3238'), ramp('#2a2412 #43391a #605228 #7e6c3a'),
         ramp('#12201a #1a3026 #284636 #38604a'), ramp('#1e1828 #2c223c #3e3254 #54466c')]
EGGL = (1.0, 0.74, 0.40)

def ambient(wp, n):
    up = n[1] if n else 0.3
    return 0.1 + 0.35 * max(0.0, up) - 0.3 * max(0.0, -up)
K.AMB['fn'] = ambient
UP, FRONT = (0.0, 1.0, 0.0), (0.0, 0.0, -1.0)

# the egg's light: one broad source inside its front, one up high, one low over the dais; a cool breath from the rose
light(0.0, 16.0, 27.5, EGGL, 3.6, 34.0, 0.012)
light(0.0, 27.0, 28.5, EGGL, 1.6, 24.0, 0.02)
light(0.0, 4.0, 27.0, EGGL, 2.2, 18.0, 0.03)
light(0.0, 40.0, 34.0, (0.62, 0.72, 0.70), 1.0, 22.0, 0.02)

# ---------------------------------------------------------------------------------------------------- the floor
def wet(X, Z):
    """puddles where the floor dips (a slow noise), a thin film of wet everywhere else"""
    m = wn(3, X * 0.16, Z * 0.22)
    return 0.62 if m > 0.6 else (0.3 if m > 0.54 else 0.12)
def floor_sh(x, y, s, t, z, wp):
    X, _, Z = wp
    D = 2.6
    i, j = math.floor(X / D), math.floor(Z / D)
    fx, fz = X / D - i, Z / D - j
    ps, psz = z / F, z * z / (F * CAMH)
    sid = h32(i, j, 3)
    dark = (i + j) % 2 == 0                                                                        # the old checker of two stones
    rr = GREY
    v = (1.3 if dark else 1.9) + ((sid % 5) - 2) * 0.12 + (wn(0, X * 0.35, Z * 0.35) - 0.5) * 0.8 + (wn(1, X * 2.2, Z * 1.2) - 0.5) * 0.3
    if sid % 7 == 0 and abs((fx - 0.3) - fz * 0.5) < ps / D * 1.2: v -= 1.2                        # a crack
    if fx < ps / D * 1.2 or fz < psz / D * 1.2: v -= 1.5
    return shade(rr, v, wp, UP, x, y, gain=2.6, warm=0.6)
rs.quad((-WXO, 0, 3), (WXO, 0, 3), (-WXO, 0, ZB + 2), floor_sh, cls='ground')

# ---------------------------------------------------------------------------------------------------- the walls
def end_wall(x, y, s, t, z, wp):
    X, Y, Z = wp
    if abs(X) < PX + 3.5 and Y < 37.5:                                                              # the niche of the egg
        if math.hypot(X / 12.5, (Y - 17.5) / 19.0) < 1.0: return None
    rr, v = masonry(GREY, X, Y, z, x, y, 1.5, ch=1.0, L=1.7, seed=21)
    # the rose window high in the end wall: grey daylight through stone tracery
    d = math.hypot(X, Y - 40.5)
    if d < 5.6:
        ang = math.atan2(Y - 40.5, X)
        spoke = abs(((ang / (2 * math.pi) * 12) % 1) - 0.5) < 0.09
        ring = abs(d - 2.2) < 0.25 or abs(d - 5.3) < 0.3
        lobe = (d > 2.5 and d < 5.0 and math.hypot(d - 3.7, (((ang / (2 * math.pi) * 12) % 1) - 0.5) * 3.0) > 1.15)
        if ring or spoke or lobe or d < 0.8: return shade(GREY, 2.6 + (0.6 if d < 0.8 else 0), wp, FRONT, x, y)
        k = GLASS[h32(int(ang * 3), int(d), 4) % 5]
        return mix(tone(k, 2.2 + (wn(1, X * 2, Y * 2) - 0.5), x, y), (150, 164, 156), 0.35)
    v -= 0.4 * max(0.0, 1 - Y / 3.0)
    return shade(rr, v, wp, FRONT, x, y)
rs.quad((-WXO, 0, ZB), (WXO, 0, ZB), (-WXO, YV + 2, ZB), end_wall, cls='wall', cut=True)

# the niche behind the egg: a dark hollow of root and tissue the egg grew from
def niche(x, y, s, t, z, wp):
    X, Y, Z = wp
    f = wn(1, X * 1.4 + 0.6 * math.sin(Y * 0.5), Y * 0.3)
    v = 1.2 + (f - 0.5) * 2.0 + (wn(5, X * 0.4, Y * 0.4) - 0.5) * 1.4
    if f < 0.3: v -= 0.7
    return shade(ROOT, v, wp, FRONT, x, y, gain=3.4, warm=0.7)
rs.quad((-14, 0, ZB + 1.5), (14, 0, ZB + 1.5), (-14, 38, ZB + 1.5), niche, cls='wall')

def aisle_wall(sg):
    n = (-sg, 0.0, 0.0)
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        rr, v = masonry(GREY, Z, Y, z, x, y, 1.4, ch=1.0, L=1.7, seed=23 + sg)
        v -= 0.6 * math.exp(-Y / 1.5)
        return shade(rr, v, wp, n, x, y)
    return sh
for sg in (-1, 1):
    rs.quad((sg * WXO, 0, 3), (sg * WXO, 0, ZB), (sg * WXO, YA, 3), aisle_wall(sg), cls='wall')
    rs.quad((sg * PX, YA, 3), (sg * WXO, YA, 3), (sg * PX, YA, ZB), lambda x, y, s, t, z, wp: shade(GREY, 1.0 + (wn(0, wp[0] * 0.5, wp[2] * 0.5) - 0.5), wp, (0.0, -1.0, 0.0), x, y), cls='ceil')

# the nave vault: a pointed barrel in strips, ashlar webs
R_V = ((PX) ** 2 + (YV - YS) ** 2) / (2 * PX)
def vault_y(X):
    c = PX - R_V                                                                                   # each half an arc centred across the nave
    return YS + math.sqrt(max(0.0, R_V * R_V - (abs(X) - c) ** 2))
N = 30
for i in range(N):
    X0, X1 = -PX + 2 * PX * i / N, -PX + 2 * PX * (i + 1) / N
    def vsh(x, y, s, t, z, wp):
        X, Y, Z = wp
        rr, v = masonry(GREY, Z, (Y - YS) * 1.3 + abs(X) * 0.4, z, x, y, 1.4, ch=0.8, L=1.2, seed=29)
        return shade(rr, v, wp, (0.0, -1.0, 0.0), x, y)
    rs.quad((X0, vault_y(X0), 3), (X1, vault_y(X1), 3), (X0, vault_y(X0), ZB), vsh, cls='ceil')

# ---------------------------------------------------------------------------------------------------- the egg
EC, EA = EGG_C, EGG_A
def egg_f(X, Y, Z):
    q = (Y - EC[1]) / EA[1]
    rx = EA[0] * (1 - 0.12 * q)                                                                    # an egg: broader below
    return (X / rx) ** 2 + q * q + ((Z - EC[2]) / EA[2]) ** 2 - 1
def egg_hit(dx, dy):
    t = EC[2] - EA[2] - 0.5
    prev = egg_f(dx * t, CAMH + dy * t, t)
    if prev < 0: return None
    while t < EC[2] + 0.5:
        t2 = t + 0.25
        f2 = egg_f(dx * t2, CAMH + dy * t2, t2)
        if f2 < 0:
            a, b = t, t2
            for _ in range(14):
                m = (a + b) / 2
                if egg_f(dx * m, CAMH + dy * m, m) < 0: b = m
                else: a = m
            t = (a + b) / 2
            X, Y, Z = dx * t, CAMH + dy * t, t
            e = 0.02
            g = (egg_f(X + e, Y, Z) - egg_f(X - e, Y, Z), egg_f(X, Y + e, Z) - egg_f(X, Y - e, Z), egg_f(X, Y, Z + e) - egg_f(X, Y, Z - e))
            gl = math.sqrt(sum(c * c for c in g)) or 1.0
            return t, 0.0, 0.0, (g[0] / gl, g[1] / gl, g[2] / gl)
        t = t2
    return None

FORMS = [(-2.6, 17.5, 3.4, 6.4, 0.55), (3.0, 12.6, 4.2, 2.6, -0.9), (2.2, 22.5, 2.0, 4.6, -0.35), (-4.4, 9.6, 2.6, 1.8, 0.2),
         (0.4, 27.0, 2.6, 1.5, 0.9), (4.8, 18.4, 1.2, 3.2, 0.1)]
def inner_shapes(X, Y):
    """the many shapes inside: soft, overlapping, half-formed -- several possibilities each trying to be the one that
    stays (rotated soft ellipses, a curl cut out of a few); returns a density 0..~1.5"""
    acc = 0.0
    for k, (cx, cy, a, b, rot) in enumerate(FORMS):
        dx, dy = X - cx, Y - cy
        u = dx * math.cos(rot) + dy * math.sin(rot); v = -dx * math.sin(rot) + dy * math.cos(rot)
        d = (u / a) ** 2 + (v / b) ** 2
        m = math.exp(-d * d * 1.4)
        if k == 0 and ((u - a * 0.35) / (a * 0.5)) ** 2 + ((v + b * 0.1) / (b * 0.5)) ** 2 < 1: m *= 0.3   # one curls round a hollow
        acc += m
    return acc + (wn(4, X * 0.45, Y * 0.45) - 0.5) * 0.35

# the roots that net the egg, drawn in its own surface coordinates (angle round it x radius, height)
EVM = VeinMap(-40.0, 40.0, -2.0, 38.0, res=0.08)
EVM.maxdepth = 3
for k in range(8):                                                                                 # from the crown, down over it
    if k in (3, 4): continue
    u0 = (k - 3.5) * 2.2
    EVM.grow(u0 * 0.5, 34.0, math.pi + u0 * 0.06 + (rng(k, 4) - 0.5) * 0.3, 0.26 + rng(k, 5) * 0.08, 300 + k, length=30, fork=(4.0, 8.0), bend=0.05)
for k in range(12):                                                                                # and up from the root mass below
    u0 = (k - 5.5) * 4.6
    EVM.grow(u0, 0.5, (rng(k, 6) - 0.5) * 0.6 + (0.25 if u0 > 0 else -0.25), 0.42, 400 + k, length=16, fork=(3.0, 6.0), bend=0.08)
def egg_sh(x, y, a, b, z, wp):
    X, Y, Z = wp
    n = rs.NB[y][x]
    view = math.sqrt(X * X + (Y - CAMH) ** 2 + Z * Z)
    cos_ = abs((n[0] * X + n[1] * (Y - CAMH) + n[2] * Z) / view)                                   # face-on = thin membrane
    th = math.atan2(X / (EA[0] * (1 - 0.12 * (Y - EC[1]) / EA[1])), (EC[2] - Z) / EA[2])
    su = th * EA[0] * 0.95
    vn = EVM.sample(su, Y)
    if vn:                                                                                         # a root over the membrane
        cov, core = vn
        v = 1.4 + 2.4 * cov + (wn(1, su * 3, Y * 3) - 0.5) * 0.8
        if core: v += 0.6
        L = lit(X, Y, Z, (n[0], n[1], n[2]))
        I = 0.3 * L[0] + 0.59 * L[1] + 0.11 * L[2]
        c = tone(ROOT, v + 1.6 * I / (0.5 + I), x, y)
        if cov < 0.35: c = mix(c, tone(AMBER, 3.0, x, y), 0.5)                                    # its edge, glowing through
        return fogged(c, Z)
    # the glowing membrane: the light from inside through it, dimmer and redder where it is thick (the rim)
    Xi, Yi = X * (EC[2] / Z), CAMH + (Y - CAMH) * (EC[2] / Z)
    inner = inner_shapes(Xi, Yi)
    core_ = math.exp(-((Xi / 6.5) ** 2 + ((Yi - 15.0) / 9.0) ** 2))                               # where the light is, deep inside
    glow = 2.8 + 4.2 * cos_ ** 0.9 + 3.2 * core_ - 3.6 * max(0.0, min(1.2, inner)) ** 1.3 - 0.6 * max(0.0, (Y - EC[1]) / EA[1])
    if 0.55 < inner < 0.75: glow += 0.9                                                             # light catching their edges
    d1, d2, cid = voronoi(su * 1.2, Y * 1.2, 1.3, seed=5, jit=0.9)                                 # the membrane's own cells, faint
    glow += (1.0 - min(1.0, d1 / 0.9)) * 0.5 - (0.6 if d2 - d1 < 0.05 else 0)
    glow += (wn(1, su * 0.8, Y * 0.8) - 0.5) * 0.7
    c = tone(AMBER, glow, x, y)
    if cos_ < 0.5: c = mix(c, (c[0] * 0.78, c[1] * 0.42, c[2] * 0.3), (0.5 - cos_) / 0.5)           # the thick rim, red
    if -0.8 < n[0] < -0.3 and n[1] > 0.2 and cos_ > 0.45 and (x + y) % 2 == 0 and wn(2, su, Y) > 0.4: c = mix(c, (250, 236, 206), 0.3)   # wet sheen
    return c
rows = range(max(0, int(proj(0, EC[1] + EA[1] + 1, EC[2])[1]) - 4), min(H, int(proj(0, 0, EC[2] - EA[2])[1]) + 4))
EGG_OBJ = raycast(rs, egg_hit, egg_sh, cls='emit', rows=rows)

# roots that hold the egg into the wall and run out over the dais and the floor
def root_sh(vb=2.4):
    cache = {}
    def sh(x, y, f, a, z, wp, nr):
        key = (round(wp[0], 0), round(wp[1], 0), round(wp[2], 0))
        L = cache.get(key)
        if L is None:
            L = cache[key] = lit(wp[0], wp[1], wp[2], None)
        I = 0.3 * L[0] + 0.59 * L[1] + 0.11 * L[2]
        tdir = (-wp[0], 16.0 - wp[1], 27.5 - wp[2]); tl = math.sqrt(sum(c * c for c in tdir)) or 1.0
        lam = max(0.0, (nr[0] * tdir[0] + nr[1] * tdir[1] + nr[2] * tdir[2]) / tl)
        v = vb + (wn(1, f * 40 + a, a * 2) - 0.5) * 1.0 + 0.7 * max(0.0, nr[1]) - 0.4 * max(0.0, nr[2])
        c = tone(ROOT, v + 3.2 * I / (0.5 + I) * (0.35 + 0.65 * lam), x, y)
        if I > 0.02:
            k = min(1.0, I) * 0.5
            c = clamp((c[0] * (1 + (L[0] / I - 1) * k), c[1] * (1 + (L[1] / I - 1) * k), c[2] * (1 + (L[2] / I - 1) * k)))
        return fogged(c, z)
    return sh
RS = root_sh()
for k in range(9):                                                                                 # the egg's roots to the dais / floor
    a0 = -1.25 + k * 2.5 / 8
    x0 = math.sin(a0) * 9.5
    pts = [(x0 * 0.9, 2.0 + abs(math.sin(a0)) * 2.0, 31.0), (x0 * 1.1, 1.85, 29.0 - abs(a0) * 1.2),
           (x0 * 1.5 + math.sin(k) * 1.2, 0.9, 26.0 - abs(a0) * 2.0), (x0 * 2.0 + math.sin(k * 1.7) * 2.0, 0.12, 22.0 - abs(a0) * 2.6 - (k % 3) * 1.2)]
    pipe(rs, pts, 0.55 - 0.04 * abs(k - 4), 0.12, RS, n=7)
for k in range(7):                                                                                 # and up the wall round the niche
    a0 = -1.2 + k * 2.4 / 6
    sx = math.sin(a0) * 12.0; sy = 18.0 + math.cos(a0) * 16.0
    pts = [(sx * 0.95, sy * 0.98, 33.5), (sx * 1.08, sy * 1.02, 35.5), (sx * 1.2 + math.sin(k) * 1.5, sy * 1.05 + 1.5, ZB - 0.3)]
    pipe(rs, pts, 0.45, 0.18, RS, n=7)

# the dais: three steps of worn stone
for i, (x0, z0, y0, y1) in enumerate(((9.5, 24.6, 0.0, 0.6), (8.4, 26.0, 0.6, 1.2), (7.4, 27.4, 1.2, 1.8))):
    def riser(x, y, s, t, z, wp, i=i):
        v = 2.0 + (1.2 if t > 0.82 else 0) + (wn(1, wp[0] * 1.2, wp[1] * 4 + i) - 0.5) * 0.6
        if (wp[0] / 2.1 + i * 0.3) % 1 < 0.04: v -= 1.0
        return shade(GREY, v, wp, FRONT, x, y, gain=3.4, warm=0.6)
    def tread(x, y, s, t, z, wp):
        v = 2.6 + 0.5 * math.exp(-(wp[0] / 2.4) ** 2) + (wn(0, wp[0] * 0.8, wp[2] * 2) - 0.5) * 0.6
        return shade(GREY, v, wp, UP, x, y, gain=3.4, warm=0.6)
    rs.box(-x0, x0, y0, y1, z0, ZB, riser, riser, top=tread)

# ---------------------------------------------------------------------------------------------------- the piers + ribs
def pier(X, Z, seed, h=YS, wide=1.0):
    """a stone shaft grown over by a bundle of living roots that twist up it and splay out into the ribs"""
    rs.box(X - 1.6 * wide, X + 1.6 * wide, 0.0, 0.7, Z - 1.6 * wide, Z + 1.6 * wide,
           lambda x, y, s, t, z, wp: shade(GREY, 2.0 + (0.8 if t > 0.75 else 0), wp, FRONT, x, y, gain=3.0),
           lambda x, y, s, t, z, wp: shade(GREY, 1.6, wp, (1.0 if X < 0 else -1.0, 0.0, 0.0), x, y, gain=3.0),
           top=lambda x, y, s, t, z, wp: shade(GREY, 2.6, wp, UP, x, y, gain=3.0))
    def shaft(x, y, f, a, z, wp, nr):
        rr, v = masonry(GREY, a * 0.9, wp[1], z, x, y, 1.8, ch=0.8, L=0.9, seed=seed)
        return shade(rr, v + 0.6 * max(0.0, -nr[2]), wp, nr, x, y, gain=3.0, warm=0.6)
    pipe(rs, [(X, 0.6, Z), (X, h, Z)], 1.25 * wide, 1.15 * wide, shaft, n=12, cls='wall')
    for k in range(8):                                                                             # the roots climbing it, tight
        ph = k * 2 * math.pi / 8 + seed
        pts = []
        for j in range(15):
            Yj = j * (h + 1.5) / 14
            a = ph + Yj * 0.035 * (1 if k % 2 else -1) + 0.12 * math.sin(Yj * 0.5 + k)
            rad = 1.2 * wide + (1.6 * math.exp(-Yj / 0.9)) + 0.08 * math.sin(Yj * 0.9 + k)
            pts.append((X + math.cos(a) * rad, Yj, Z + math.sin(a) * rad))
        if k % 3 != 2: pipe(rs, pts, 0.42 * wide, 0.26 * wide, RS, n=6)
        else: pipe(rs, pts[:8], 0.36 * wide, 0.2 * wide, RS, n=6)                                    # some end halfway, the stone shows
for (X, Z, sd) in ((-PX, 17.0, 3), (PX, 17.0, 5), (-PX, 25.0, 7), (PX, 25.0, 9), (-14.5, 32.5, 11), (14.5, 32.5, 13)):
    pier(X, Z, sd)

def rib_arc(P0, P1, top, n=18):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((P0[0] + (P1[0] - P0[0]) * t, P0[1] + (P1[1] - P0[1]) * t + (top - max(P0[1], P1[1])) * math.sin(math.pi * t) ** 0.8,
                    P0[2] + (P1[2] - P0[2]) * t))
    return pts
for Z in (17.0, 25.0):                                                                              # transverse arches over the nave
    for dz in (-0.35, 0.35):
        pipe(rs, rib_arc((-PX, YS, Z + dz), (PX, YS, Z + dz), YV - 0.8), 0.5, 0.5, RS, n=6)
pipe(rs, rib_arc((-14.5, YS, 32.5), (14.5, YS, 32.5), YV - 0.5), 0.6, 0.6, RS, n=6)
for sg in (-1, 1):                                                                                 # the arcade along each side
    pipe(rs, rib_arc((sg * PX, YS - 1.0, 17.0), (sg * PX, YS - 1.0, 25.0), YS + 3.0), 0.45, 0.45, RS, n=6)
    pipe(rs, rib_arc((sg * PX, YS - 1.0, 25.0), (sg * 14.5, YS - 1.0, 32.5), YS + 3.0), 0.45, 0.45, RS, n=6)
    pipe(rs, rib_arc((sg * PX, YS - 1.0, 9.0), (sg * PX, YS - 1.0, 17.0), YS + 3.0), 0.45, 0.45, RS, n=6)
    for Z in (17.0, 25.0):                                                                          # diagonal ribs across the aisle
        pipe(rs, rib_arc((sg * PX, YS - 1.5, Z), (sg * WXO, YS - 1.5, Z), YA + 2.5), 0.4, 0.4, RS, n=6)

# ---------------------------------------------------------------------------------------------------- left: glass, altar
GW = (19.5, 27.5, 7.0, 21.0)                       # the lancet in the left aisle wall: z0, z1, sill, spring
def glass_sh(x, y, s, t, z, wp):
    """living glass: cells instead of leading, slowly remembering -- top: a robed figure with her hand on a door;
    middle: a lattice of small lights; bottom: the egg swelling from bare ground"""
    X, Y, Z = wp
    zc = (GW[0] + GW[1]) / 2; hw = (GW[1] - GW[0]) / 2
    u = Z - zc
    top = GW[3] + hw * 1.6 * math.sqrt(max(0.0, 1 - (abs(u) / hw) ** 2))
    if abs(u) > hw or Y < GW[2] or Y > top: return None
    if abs(u) > hw - 0.35 or Y < GW[2] + 0.35 or Y > top - 0.35:
        return shade(GREY, 2.4, wp, (1.0, 0.0, 0.0), x, y)                                         # the stone frame
    d1, d2, cid = voronoi(u * 1.0, Y * 1.0, 0.62, seed=17)
    if d2 - d1 < 0.05: return tone(ROOT, 1.0, x, y)                                               # cell walls, living
    base = GLASS[(0, 0, 3, 4, 0, 3, 1)[cid % 7]]; val = 1.0 + (cid % 3) * 0.35 + (1 - d1 / 0.8) * 0.7
    # what it remembers
    if Y < GW[2] + 3.6:                                                                             # the egg from bare ground
        if Y < GW[2] + 1.0: base, val = GLASS[2], 1.4
        elif ((u) / 1.5) ** 2 + ((Y - GW[2] - 2.2) / 1.6) ** 2 < 1: base, val = GLASS[2], 3.2
    elif Y < GW[2] + 8.6:                                                                           # a lattice of small lights
        gu, gv = (u + 3) % 0.9, (Y - GW[2] - 3.6) % 0.9
        if math.hypot(gu - 0.45, gv - 0.45) < 0.14: base, val = GLASS[3], 3.6
    else:                                                                                           # the Bishop, sealing a door
        fy = Y - (GW[2] + 8.6)
        if -2.6 < u < -0.6 and fy < 6.0:
            if math.hypot(u + 1.6, fy - 5.0) < 0.6: base, val = GLASS[2], 3.0                       # her head
            elif abs(u + 1.6) < 0.9 - 0.12 * (4.6 - min(fy, 4.6)) * -0.25 and fy < 4.4: base, val = GLASS[1], 2.8   # the robe
        if 0.6 < u < 2.8 and fy < 5.4:
            if abs(u - 1.7) < 0.95 and (fy < 4.4 or math.hypot(u - 1.7, fy - 4.4) < 0.95): base, val = GLASS[0], 1.2   # the door
        if abs(fy - 3.0) < 0.22 and -0.8 < u < 1.0: base, val = GLASS[2], 2.8                       # her arm to it
    c = tone(base, val + (wn(1, u * 3, Y * 3) - 0.5) * 0.5 + (Y - GW[2]) * 0.03, x, y)
    return mix(c, (96, 94, 84), 0.3)
rs.quad((-WXO + 0.05, GW[2], GW[0]), (-WXO + 0.05, GW[2], GW[1]), (-WXO + 0.05, GW[3] + 7, GW[0]), glass_sh, cls='emit', cut=True)
light(-WXO + 1.5, 15.0, (GW[0] + GW[1]) / 2, (0.62, 0.62, 0.78), 1.4, 12.0, 0.03)

ALT = (-26.4, -21.8, 20.6, 25.6, 3.5)             # the altar: x0, x1, z0, z1, height
def altar_side(n):
    def sh(x, y, s, t, z, wp):
        rr, v = masonry(GREY, wp[2] + wp[0], wp[1], z, x, y, 2.2, ch=0.6, L=0.8, seed=41)
        if wp[1] > ALT[4] - 0.45: v += 0.9                                                          # the moulded top slab
        return shade(rr, v, wp, n, x, y, gain=3.0)
    return sh
def altar_top(x, y, s, t, z, wp):
    """no idol: only dust, worn away where someone knelt and leaned, in the shape of two hands"""
    X, Y, Z = wp
    v = 3.6 + (wn(1, X * 3, Z * 3) - 0.5) * 0.6                                                    # pale dust
    for (hx, hz, mirror) in ((-23.1, 22.2, 1), (-23.1, 24.0, -1)):
        u, w = (X - hx), (Z - hz) * mirror
        palm = (u / 0.42) ** 2 + (w / 0.36) ** 2 < 1
        fingers = any(abs(w - fw) < 0.07 and 0.3 < u < 0.3 + fl for fw, fl in ((-0.24, 0.42), (-0.08, 0.55), (0.08, 0.52), (0.22, 0.4)))
        thumb = abs(w - (0.3 + (0.2 - u) * 0.6)) < 0.08 and -0.05 < u < 0.25
        if palm or fingers or thumb: v = 1.6
    return shade(GREY, v, wp, UP, x, y, gain=3.0)
rs.box(ALT[0], ALT[1], 0.0, ALT[4], ALT[2], ALT[3], altar_side(FRONT), altar_side((1.0, 0.0, 0.0)), top=altar_top)
rs.box(ALT[0] - 0.3, ALT[1] + 0.3, ALT[4] - 0.4, ALT[4], ALT[2] - 0.3, ALT[3] + 0.3, altar_side(FRONT), altar_side((1.0, 0.0, 0.0)), top=altar_top)
def kneel(x, y, s, t, z, wp):
    return shade(OAK, 2.4 + (wn(1, wp[0] * 4, wp[2] * 4) - 0.5) * 0.6, wp, UP, x, y)
rs.box(-21.2, -19.8, 0.0, 0.9, 21.2, 25.0, kneel, kneel, top=lambda x, y, s, t, z, wp: shade(RUGR, 2.2 - (0.8 if abs(wp[2] - 23.1) < 0.9 and abs(wp[0] + 20.5) < 0.4 else 0), wp, UP, x, y))
candle(rs, -22.4, ALT[4], 21.0, 1.0, I=0.9, R=7.0); candle(rs, -22.6, ALT[4], 25.2, 0.7, I=0.7, R=6.0)

# ---------------------------------------------------------------------------------------------------- right: organ, servants
def organ_pipe(rad):
    """the pipes are not metal: cartilage, ringed like a throat, a dark mouth low on each"""
    def sh(x, y, f, a, z, wp, nr):
        X, Y, Z = wp
        ring = (Y / 0.3) % 1
        v = 1.4 + 1.5 * max(0.0, -nr[2] * 0.6 - nr[0] * 0.5) - (1.0 if ring < 0.2 else 0) + (0.7 if 0.28 < ring < 0.4 else 0)
        v += (wn(1, a * 2 + rad * 9, Y * 0.6) - 0.5) * 0.9
        if f > 0.93: v -= 0.8                                                                        # the dark inside of the bell
        if f < 0.16 and 0.06 < f and abs(a) < 0.55: return tone(CART, 0.6, x, y)                    # the mouth
        c = shade(CART, v, wp, nr, x, y, gain=3.0, warm=0.5)
        return mix(c, (c[0] * 1.12, c[1] * 0.9, c[2] * 0.86), 0.6)                                   # flesh, not stone
    return sh
ORG = (23.6, 27.0, 18.5, 26.5)                       # the organ case along the right aisle wall: x0, x1, z0, z1
for k in range(11):
    Z = ORG[2] + 0.5 + k * (ORG[3] - ORG[2] - 1.0) / 10
    hgt = 5.0 + 5.4 * math.sin(math.pi * (k + 0.5) / 11) + (h32(k, 3) % 3) * 0.5
    r = 0.36 + 0.2 * math.sin(math.pi * (k + 0.5) / 11)
    X = 25.8 - (k % 2) * 0.9
    bend = (h32(k, 5) % 5 - 2) * 0.15
    top = (X - 0.6 - bend, 3.2 + hgt, Z + bend * 0.6)
    pipe(rs, [(X, 3.2, Z), (X + bend * 0.4, 3.2 + hgt * 0.45, Z + bend * 0.3), (X - 0.2 + bend * 0.2, 3.2 + hgt * 0.85, Z + bend * 0.5), top], r, r * 0.72, organ_pipe(r), n=8)
    pipe(rs, [top, (top[0] - 0.25, top[1] + 0.5, top[2])], r * 0.8, r * 1.35, organ_pipe(r), n=8)   # the flared lip
def case_sh(n):
    return lambda x, y, s, t, z, wp: shade(OAK, 2.2 + (wn(1, wp[2] * 2, wp[1] * 6) - 0.5) * 0.8 - (1.0 if abs(wp[1] - 1.6) < 0.08 else 0), wp, n, x, y)
rs.box(ORG[0], ORG[1], 0.0, 3.2, ORG[2], ORG[3], case_sh((-1.0, 0.0, 0.0)), case_sh(FRONT), top=lambda x, y, s, t, z, wp: shade(OAK, 3.2, wp, UP, x, y))
def manual(x, y, s, t, z, wp):
    Z = wp[2]
    k = (Z / 0.22) % 1
    if wp[1] > 2.7: return shade(BONE, 4.4 - (1.6 if k < 0.18 else 0), wp, UP, x, y)
    return shade(OAK, 1.6, wp, (-1.0, 0.0, 0.0), x, y)
rs.box(21.6, 23.6, 2.4, 2.85, 19.8, 25.2, manual, manual, top=manual)
rs.box(20.4, 21.6, 0.0, 1.5, 21.2, 23.8, kneel, kneel, top=kneel)                                  # the bench
candle(rs, 23.0, 3.2, 19.3, 0.8, I=0.6, R=5.0); candle(rs, 23.0, 3.2, 25.9, 0.6, I=0.45, R=4.5)

SRV = (18.6, 30.4, 14.5, 25.0)                       # the servants: a membrane in the right aisle wall above the organ
# (Z, Y, kind, scale, tilt): faces and hands pressing against it from the other side
FIG = [(20.5, 21.4, 'face', 1.35, 0.15), (21.9, 18.8, 'hand', 1.25, -0.3), (23.6, 22.2, 'face', 1.45, -0.1), (25.0, 18.2, 'hand', 1.3, 0.25),
       (26.0, 20.9, 'face', 1.25, 0.2), (28.2, 22.3, 'face', 1.35, -0.2), (28.9, 18.9, 'hand', 1.2, -0.15), (23.2, 16.4, 'hand', 1.1, 0.4)]
def _bump(u, w, a, b): q = 1 - (u / a) ** 2 - (w / b) ** 2; return q ** 1.4 if q > 0 else 0.0     # soft, no rim
def servants_h(Z, Y):
    """a height field: faces and hands of the cathedral's first servants pressing the membrane out from behind"""
    h = 0.0
    for (zc, yc, kind, sc, tilt) in FIG:
        du, dw = (Z - zc) / sc, (Y - yc) / sc
        u = du * math.cos(tilt) - dw * math.sin(tilt); w = du * math.sin(tilt) + dw * math.cos(tilt)
        if abs(u) > 1.6 or abs(w) > 1.8: continue
        if kind == 'face':
            f = 0.42 * _bump(u, w, 0.62, 0.85) + 0.1 * _bump(u, w - 0.35, 0.55, 0.18)                # the head, the brow
            f += 0.12 * _bump(u, w + 0.02, 0.1, 0.3)                                                 # the nose
            f += 0.18 * _bump(u, w + 1.0, 0.9, 0.5)                                                   # the neck and shoulders, sinking
            f -= 0.08 * (_bump(u - 0.24, w - 0.18, 0.16, 0.11) + _bump(u + 0.24, w - 0.18, 0.16, 0.11))   # eye hollows
            f -= 0.09 * _bump(u, w + 0.45, 0.16, 0.13)                                               # an open mouth
        else:
            f = 0.3 * _bump(u, w, 0.36, 0.42)                                                        # the palm
            for k, (fx, fl) in enumerate(((-0.33, 0.5), (-0.12, 0.66), (0.1, 0.64), (0.3, 0.52))):
                f = max(f, 0.22 * _bump(u - fx - (w - 0.3) * fx * 0.25, w - 0.42 - fl / 2, 0.085, fl / 2))
            f = max(f, 0.2 * _bump(u + 0.42 + (w + 0.1) * 0.5, w + 0.05, 0.09, 0.28))                  # the thumb
        h = max(h, f * sc)
    return h
def servants_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    zc, yc, hz, hy = (SRV[0] + SRV[1]) / 2, (SRV[2] + SRV[3]) / 2 + 0.6, (SRV[1] - SRV[0]) / 2, (SRV[3] - SRV[2]) / 2
    e_ = (1 - ((Z - zc) / hz) ** 2 - ((Y - yc) / hy) ** 2) * 2.4 + (wn(1, Z * 0.7, Y * 0.7) - 0.5) * 1.8 + (wn(4, Z * 2, Y * 0.5) - 0.5) * 0.8
    if e_ <= 0:
        rr, v = masonry(GREY, Z, Y, z, x, y, 1.4, ch=1.0, L=1.7, seed=24)
        if e_ > -0.6 and abs(wn(2, Z * 1.4, Y * 1.4) - 0.5) < 0.03: return shade(TISSUE, 1.2, wp, (-1.0, 0.0, 0.0), x, y)   # veins out over the stone
        return shade(rr, v - (0.5 if e_ > -0.4 else 0), wp, (-1.0, 0.0, 0.0), x, y)
    h = servants_h(Z, Y)
    e = 0.05
    gz = (servants_h(Z + e, Y) - servants_h(Z - e, Y)) / (2 * e); gy = (servants_h(Z, Y + e) - servants_h(Z, Y - e)) / (2 * e)
    f = wn(1, Z * 1.1, Y * 0.4)
    v = 1.0 + (f - 0.5) * 0.9 - (0.6 if e_ < 0.35 else 0)                                           # the membrane, stretched
    v += h * 2.4 + (-gz * 1.0 + gy * 0.8)                                                          # the shapes pressing it out
    if h > 0.02 and (wn(2, Z * 4, Y * 4) > 0.62): v += 0.5                                         # the membrane thin over them
    nl = math.sqrt(1 + gz * gz + gy * gy)
    c = shade(TISSUE, v, wp, (-1.0 / nl, gy / nl, -gz / nl), x, y, gain=2.2, warm=0.5)
    return mix(c, shade(GREY, v + 0.6, wp, (-1.0, 0.0, 0.0), x, y, gain=2.2), 0.3)
rs.quad((WXO - 0.05, SRV[2] - 3.0, SRV[0] - 3.0), (WXO - 0.05, SRV[2] - 3.0, SRV[1] + 3.0), (WXO - 0.05, SRV[3] + 3.0, SRV[0] - 3.0), servants_sh, cls='wall')

# ---------------------------------------------------------------------------------------------------- candles on stands
def stand(X, Z, h=5.0, arms=3):
    iron = lambda x, y, f, a, z, wp, nr: shade(IRON, 1.6 + max(0.0, -nr[0] * 0.6 - nr[2] * 0.5) * 1.4, wp, nr, x, y, gain=2.4)
    pipe(rs, [(X, 0.0, Z), (X, h, Z)], 0.12, 0.09, iron, n=6)
    rs.box(X - 0.6, X + 0.6, 0.0, 0.18, Z - 0.6, Z + 0.6, lambda x, y, s, t, z, wp: shade(IRON, 2.0, wp, FRONT, x, y),
           lambda x, y, s, t, z, wp: shade(IRON, 1.5, wp, (1.0, 0.0, 0.0), x, y), top=lambda x, y, s, t, z, wp: shade(IRON, 2.4, wp, UP, x, y))
    for k in range(arms):
        dx = (k - (arms - 1) / 2) * 0.9
        if dx: pipe(rs, [(X, h - 0.6, Z), (X + dx, h - 0.4, Z)], 0.07, 0.07, iron, n=5)
        candle(rs, X + dx, h - 0.35, Z, 0.6 + (h32(k, int(X * 10)) % 3) * 0.25, r=0.15, I=0.8, R=7.0)
stand(-8.4, 23.4, 5.4); stand(8.4, 23.4, 5.4)
stand(-15.0, 15.8, 4.2, 1); stand(16.2, 16.4, 4.6, 1)
for (X, Z, hh) in ((-6.6, 25.2, 0.8), (-5.9, 25.5, 0.5), (6.2, 25.3, 0.7), (6.9, 25.0, 0.45), (-4.8, 26.7, 0.6), (5.0, 26.8, 0.5)):
    candle(rs, X, 0.6 if Z < 26 else 1.2, Z, hh, r=0.14, I=0.55, R=5.0)

# ---------------------------------------------------------------------------------------------------- render
from PIL import Image, ImageFilter
def air_glow(col):
    """the haze in the nave lit by the egg: a wide, soft bloom of everything that glows"""
    em = Image.new('RGB', (W, H)); ep = em.load()
    for y in range(H):
        for x in range(W):
            g = rs.G[y][x]
            if g is not None and g[5] == 'emit':
                c = col[y][x]; ep[x, y] = (c[0], c[1], c[2]) if c[0] > 90 else (0, 0, 0)
    small = em.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BILINEAR)
    sp = small.load()
    for y in range(H):
        for x in range(W):
            g = rs.G[y][x]
            k = 0.12 if (g is not None and g[1] == EGG_OBJ) else 1.0                               # the egg itself stays unclipped
            gr, gg, gb = sp[x, y]; c = col[y][x]
            col[y][x] = (min(255, int(c[0] + gr * 0.42 * k)), min(255, int(c[1] + gg * 0.36 * k)), min(255, int(c[2] + gb * 0.26 * k)))
def mirror(x, y, wp): return wet(wp[0], wp[2])
img = rs.render(INK, fog=K.fog, mirror=mirror, overlay=air_glow, light_gain=0.8, grime_gain=0.45, bloom=0.65, stain_gain=0.15, damp_gain=0.12, sheen_gain=0.5)
img.save(f'{OUT}/heart.png')

# the Unborn moving: frames of the egg alone in which the shapes inside drift, turn and swell (a loop); each frame is
# the finished background plus the change of the egg's own shading (the egg takes almost none of the air glow, so
# nothing clips), so frame 0 is the background exactly
NF = 12
BASE = list(FORMS)
eggpx = [(x, y) for y in range(H) for x in range(W) if rs.G[y][x] is not None and rs.G[y][x][1] == EGG_OBJ]
x0e, x1e = min(p[0] for p in eggpx), max(p[0] for p in eggpx); y0e, y1e = min(p[1] for p in eggpx), max(p[1] for p in eggpx)
ew, eh = x1e - x0e + 1, y1e - y0e + 1
def shade_egg():
    out = {}
    for (x, y) in eggpx:
        g = rs.G[y][x]
        out[(x, y)] = g[0](x, y, g[2], g[3], rs.ZB[y][x], g[4])
    return out
c0 = shade_egg()
ip = img.load()
sheet = Image.new('RGBA', (ew * NF, eh), (0, 0, 0, 0)); sp = sheet.load()
for k in range(NF):
    ph = 2 * math.pi * k / NF
    FORMS[:] = [(cx + 0.9 * (math.sin(ph + i * 1.7) - math.sin(i * 1.7)), cy + 0.8 * (math.cos(ph * (1 if i % 2 else -1) + i) - math.cos(i)),
                 a * (1 + 0.1 * (math.sin(ph + i) - math.sin(i))), b * (1 + 0.1 * (math.cos(ph + i * 2) - math.cos(i * 2))),
                 rot + 0.25 * (math.sin(ph + i * 0.9) - math.sin(i * 0.9))) for i, (cx, cy, a, b, rot) in enumerate(BASE)]
    ck = shade_egg() if k else c0
    for (x, y) in eggpx:
        b_ = ip[x, y]; a_ = c0[(x, y)]; n_ = ck[(x, y)]
        sp[k * ew + x - x0e, y - y0e] = tuple(max(0, min(255, b_[i] + n_[i] - a_[i])) for i in range(3)) + (255,)
FORMS[:] = BASE
sheet.save(f'{OUT}/egg_anim.png')
print('egg frames', NF, 'x', ew, 'x', eh, 'top-left', x0e, y0e)
def box(pts):
    xs = [proj(*p)[0] for p in pts]; ys = [proj(*p)[1] for p in pts]
    return [round(min(xs)), round(min(ys)), round(max(xs)), round(max(ys))]
print('egg', box([(-EA[0], 1.0, EC[2] - EA[2]), (EA[0], 1.0, EC[2] - EA[2]), (0, EC[1] + EA[1], EC[2]), (-EA[0], EC[1], EC[2] - 1)]))
print('glass', box([(-WXO, GW[2], GW[0]), (-WXO, GW[2], GW[1]), (-WXO, GW[3] + 6.4, (GW[0] + GW[1]) / 2)]))
print('altar', box([(ALT[0], 0, ALT[2]), (ALT[1], 0, ALT[2]), (ALT[1], ALT[4] + 1.0, ALT[3]), (ALT[0], ALT[4], ALT[3])]))
print('organ', box([(ORG[0], 0, ORG[2]), (ORG[0], 0, ORG[3]), (25.8, 19.0, ORG[2] + 5), (ORG[1], 3.2, ORG[3])]))
print('servants', box([(WXO, SRV[2], SRV[0]), (WXO, SRV[3], SRV[0]), (WXO, SRV[2], SRV[1]), (WXO, SRV[3], SRV[1])]))
