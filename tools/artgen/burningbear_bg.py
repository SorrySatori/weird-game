"""Burning Bear Street — 1067x600, overcast day, one-point perspective (same engine/palette as the Crossroad / Shed 521).
A cobbled street canyon between old tenements, receding to the hazy Townhall tower. Over the street hang the
festival's stuffed bear-skins on ropes between the facades, with faded pennant bunting; a fire pit in the road.
Variants: growth (ivy, moss, flowers sprouting from the bears' seams, overgrown pit, grass in the setts) and
decay (the bears are BURNING: charred fur, glowing embers, flames and smoke; soot over windows, litter, a bonfire).

    python3 burningbear_bg.py <outdir> [base|growth|decay]   -> bg.png / bg_growth.png / bg_decay.png + bears.json
"""
import sys, math, random, json
from PIL import Image, ImageDraw
from pal_day import *
OUT = sys.argv[1]
VARIANT = sys.argv[2] if len(sys.argv) > 2 else 'base'
GROWTH, DECAY = VARIANT == 'growth', VARIANT == 'decay'
W, H = 1067, 600
CX, HY = 533, 296
F, CAMH = 300.0, 12.0
nA, nB, nC = make_noise(48, 1, W, H), make_noise(13, 2, W, H), make_noise(5, 3, W, H)
nF = make_noise(9, 7, W, H)

def proj(wx, wy, wz): return (CX + F * wx / wz, HY + F * (CAMH - wy) / wz)
def ground_at(x, y):
    wz = F * CAMH / (y - HY); return (x - CX) * wz / F, wz
def fog_of(z): return max(0.0, min(0.82, 1 - math.exp(-(z - 14) / 70.0)))
def pip(pts, u, v):
    inside = False; n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        if (y0 > v) != (y1 > v) and u < x0 + (x1 - x0) * (v - y0) / (y1 - y0): inside = not inside
    return inside
class Face:
    def __init__(self, kind, const, outline, mat, obj):
        self.kind, self.const, self.outline, self.mat, self.obj, self.feats = kind, const, outline, mat, obj, []
    def polygon(self):
        if self.kind == 'front': return [proj(u, v, self.const) for (u, v) in self.outline]
        return [proj(self.const, v, u) for (u, v) in self.outline]
    def uvz(self, x, y):
        if self.kind == 'front':
            z = self.const; return (x - CX) * z / F, CAMH - (y - HY) * z / F, z
        if x == CX: return None
        wz = F * self.const / (x - CX); return wz, CAMH - (y - HY) * wz / F, wz
    def rect(self, u0, v0, u1, v1, kind): self.feats.append(('r', (u0, v0, u1, v1), kind))
    def poly(self, pts, kind): self.feats.append(('p', pts, kind))
    def material_at(self, u, v):
        mat = self.mat
        for (t, g, kind) in self.feats:
            if t == 'r':
                if g[0] <= u < g[2] and g[1] <= v < g[3]: mat = kind
            elif pip(g, u, v): mat = kind
        return mat
FACES = []
def add(f): FACES.append(f); return f
def box(u0, u1, h): return [(u0, 0), (u0, h), (u1, h), (u1, 0)]
def near_z(f): return f.const if f.kind == 'front' else min(u for (u, v) in f.outline)
def arch(u0, u1, v0, vs, n=10):
    r = (u1 - u0) / 2; cu = u0 + r
    return [(u0, v0), (u0, vs)] + [(cu - r * math.cos(math.pi * i / n), vs + r * math.sin(math.pi * i / n)) for i in range(1, n)] + [(u1, vs), (u1, v0)]

# ================================================================== the street canyon
XL, XR = -22.0, 22.0                       # facade planes
KERB = 18.0                                # |wx| of the kerb (setts inside, pavement outside)
WIN_DZ, WIN_W, STOREY, GF = 3.6, 1.8, 9.0, 11.4
BLD = {}
rnd = random.Random(11)
def facade(X, z0, z1, h, mat, obj, passage=None):
    """one tenement: side face at wx=X spanning depth z0..z1, cornice height h, mansard roof strip above."""
    BLD[obj] = (z0, z1, h, mat, X)
    f = add(Face('side', X, box(z0, z1, h + 3.2), mat, obj))
    f.rect(z0, h, z1, h + 3.2, 'roof')
    for u in [z0 + 2.2 + i * 6.0 for i in range(int((z1 - z0 - 3.5) / 6.0))]:
        f.rect(u, h + 0.7, u + 1.5, h + 2.6, 'dormer')
    f.rect(z0, h - 1.3, z1, h, 'cornice'); f.rect(z0, GF - 0.8, z1, GF, 'cornice'); f.rect(z0, 0, z1, 0.9, 'plinth')
    # ground floor: arched doors and shop windows; an archway (průjezd) where an exit leaves the street
    i = 0; u = z0 + 1.3
    while u + 2.6 < z1 - 0.9:
        if passage and u + 2.6 > passage[0] - 0.4 and u < passage[1] + 0.4:
            u = passage[1] + 0.9; continue
        if h32(obj, i) % 3 == 0: f.poly(arch(u, u + 2.4, 0.0, 5.6), 'door')
        else:
            f.poly(arch(u - 0.1, u + 2.7, 1.6, 6.2), 'shopframe'); f.poly(arch(u + 0.15, u + 2.45, 1.9, 6.2), 'shop' if h32(obj, i, 3) % 4 else 'shoplit')
        if h32(obj, i, 5) % 2: f.rect(u + 3.0, 7.8, u + 3.6, 9.4, 'lantern')
        u += 4.3; i += 1
    if passage:
        f.poly(arch(passage[0] - 0.4, passage[1] + 0.4, 0.0, 6.4), 'shopframe')
        f.poly(arch(passage[0], passage[1], 0.0, 6.4), 'passage')
    # upper floors
    k = 0
    while True:
        base = GF + k * STOREY
        if base + 7.6 > h - 1.3: break
        for j, u in enumerate([z0 + 1.6 + n * WIN_DZ for n in range(int((z1 - z0 - 2.2) / WIN_DZ))]):
            r = h32(obj, k, j)
            f.rect(u - 0.2, base + 1.5, u + WIN_W + 0.2, base + 2.0, 'sill')
            f.rect(u, base + 2.0, u + WIN_W, base + 6.8, 'winlit' if r % 9 == 0 else 'shutter' if r % 7 == 1 else 'win')
            f.rect(u - 0.25, base + 6.8, u + WIN_W + 0.25, base + 7.4, 'hood')
            if GROWTH and r % 3 == 0: f.rect(u - 0.1, base + 1.0, u + WIN_W + 0.1, base + 2.0, 'flowerbox')
        f.rect(z0, base + 8.6, z1, base + 9.0, 'band')
        k += 1
    f.rect(z0, 0, z0 + 0.7, h, 'quoin'); f.rect(z1 - 0.7, 0, z1, h, 'quoin')
    # moss / damp streaks under the cornices
    for (v, a) in ((h - 1.3, 2.4), (GF - 0.8, 1.6)):
        u = z0 + 0.8
        while u < z1 - 1:
            if rnd.random() < (0.4 if GROWTH else 0.45): f.rect(u, v - rnd.uniform(0.4, a) * (1.4 if GROWTH else 1.0), u + rnd.uniform(0.3, 0.8), v, 'moss')
            u += rnd.uniform(1.2, 3.4)
    return f
LEFT = [(7.0, 27, 38.5, 'plaster', 1, (13.0, 16.4)), (27, 45, 47.0, 'stucco', 2, None), (45, 63, 35.0, 'brick', 3, None),
        (63, 86, 43.0, 'plaster', 4, None), (86, 112, 37.0, 'stucco', 5, None), (112, 150, 41.0, 'brick', 6, None)]
RIGHT = [(7.0, 24, 43.0, 'stucco', 11, (13.0, 16.4)), (24, 44, 36.5, 'brick', 12, None), (44, 60, 47.0, 'plaster', 13, None),
         (60, 84, 38.0, 'stucco', 14, None), (84, 110, 44.0, 'plaster', 15, None), (110, 150, 35.0, 'brick', 16, None)]
for (z0, z1, h, mat, obj, pas) in LEFT: facade(XL, z0, z1, h, mat, obj, pas)
for (z0, z1, h, mat, obj, pas) in RIGHT: facade(XR, z0, z1, h, mat, obj, pas)
# the Townhall closing the view: a wide front with a clock tower (the street's "up" exit leads there)
TH = add(Face('front', 215, [(-34, 0), (-34, 30), (-6, 30), (-6, 52), (-4.2, 52), (0, 64), (4.2, 52), (6, 52), (6, 30), (34, 30), (34, 0)], 'plaster', 60))
for u in range(-31, 31, 4):
    if abs(u) > 7: TH.rect(u, 12, u + 1.8, 18, 'win'); TH.rect(u, 21, u + 1.8, 26, 'win')
TH.poly(arch(-3, 3, 0, 8), 'door'); TH.rect(-2.6, 40, 2.6, 46, 'clock'); TH.rect(-34, 29, 34, 30.8, 'cornice')
# skyline: roofs + needle spires in the haze (like the original art)
rnd2 = random.Random(31); SKYLINE = []
for i in range(70):
    wx = -170 + i * 5 + rnd2.uniform(-2, 2); z = rnd2.choice((230, 260, 300)); w = rnd2.uniform(4, 11); h = rnd2.uniform(18, 44)
    SKYLINE.append(('r', wx, z, w, h))
SKYLINE += [('s', -48, 250, 6, 96), ('s', -30, 280, 4, 80), ('s', 34, 260, 5, 104), ('s', 58, 300, 4, 70), ('s', 18, 290, 3, 84)]

# ================================================================== rasterise faces + skyline
layer = Image.new('I', (W, H), 0); ld = ImageDraw.Draw(layer)
FACE_ID = {}
def fid(f):
    if id(f) not in FACE_ID: FACE_ID[id(f)] = (len(FACE_ID) + 1, f)
    return FACE_ID[id(f)][0]
for i, (t, wx, z, w, h) in enumerate(SKYLINE):
    if t == 'r':
        (x0, y0), (x1, y1) = proj(wx - w / 2, h, z), proj(wx + w / 2, 0, z); ld.rectangle([x0, y0, x1, y1], fill=1000 + i)
    else:
        pts = [proj(wx - w / 2, 0, z), proj(wx - w / 2, h * 0.55, z), proj(wx - w * 0.18, h * 0.62, z), proj(wx, h, z), proj(wx + w * 0.18, h * 0.62, z), proj(wx + w / 2, h * 0.55, z), proj(wx + w / 2, 0, z)]
        ld.polygon(pts, fill=1000 + i)
for f in sorted(FACES, key=near_z, reverse=True):
    ld.polygon(f.polygon(), fill=fid(f))
lp = layer.load(); BY_ID = {v[0]: v[1] for v in FACE_ID.values()}
INF = 9e9
M = [[None] * W for _ in range(H)]; Z = [[INF] * W for _ in range(H)]; UV = [[None] * W for _ in range(H)]
PUDDLES = [(-7, 15.5, 2.0, 0.7), (11, 22, 1.6, 0.6), (-12, 30, 1.8, 0.6), (5, 38, 1.4, 0.5), (14, 13.5, 1.2, 0.5)]
PIT = (0.0, 19.5)
for y in range(H):
    for x in range(W):
        v = lp[x, y]
        if v >= 1000: M[y][x] = ('skyline', v); Z[y][x] = SKYLINE[v - 1000][2]; continue
        if v:
            f = BY_ID[v]; r = f.uvz(x, y) or (0.0, 0.0, near_z(f)); u, vv, z = r
            M[y][x] = (f.material_at(u, vv), f.obj); Z[y][x] = z; UV[y][x] = (u, vv, f); continue
        if y > HY:
            wx, wz = ground_at(x, y); aw = abs(wx)
            pr = math.hypot(wx - PIT[0], (wz - PIT[1]) * 1.0)
            if pr < 1.9: k = 'pitstone' if pr > 1.25 else 'ash'
            elif any(((wx - px_) / rx) ** 2 + ((wz - pz) / rz) ** 2 < 1 for (px_, pz, rx, rz) in PUDDLES): k = 'puddle'
            elif aw < KERB - 0.45: k = 'sett'
            elif aw < KERB: k = 'gutter'
            elif aw < KERB + 0.55: k = 'kerb'
            elif GROWTH and aw > XR - 1.3 and wz < 120: k = 'bed'
            else: k = 'pave'
            M[y][x] = (k, 0); Z[y][x] = wz; UV[y][x] = (wx, wz, None)
        else: M[y][x] = ('sky', 0)

# ================================================================== overlays (z-tested)
def put(x, y, key, obj, z, uv=None):
    if 0 <= x < W and 0 <= y < H and z <= Z[y][x]:
        M[y][x] = (key, obj); Z[y][x] = z
        if uv is not None: UV[y][x] = uv
def line3d(p0, p1, sag, key, obj, n=80):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append((proj(p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t - sag * math.sin(math.pi * t), p0[2] + (p1[2] - p0[2]) * t), p0[2] + (p1[2] - p0[2]) * t))
    for ((a, za), (b, zb)) in zip(pts, pts[1:]):
        m = int(math.hypot(b[0] - a[0], b[1] - a[1])) + 1
        for j in range(m + 1):
            put(int(a[0] + (b[0] - a[0]) * j / m), int(a[1] + (b[1] - a[1]) * j / m), key, obj, za - 0.05)
    return pts
def fill_poly(pts, key, obj, z, uv=None):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    for y in range(max(0, int(min(ys))), min(H, int(max(ys)) + 1)):
        for x in range(max(0, int(min(xs))), min(W, int(max(xs)) + 1)):
            if pip(pts, x + 0.5, y + 0.5): put(x, y, key, obj, z, uv)

# --- bears: (wx, z, scale, tilt deg, decorations)
BEARS = [(-12.6, 24, 0.74, -4, 'patch'), (0.0, 24, 0.76, 2, 'straps'), (12.4, 24, 0.73, 5, 'x frown'),
         (-6.8, 34, 0.71, 4, 'circle'), (7.0, 34, 0.70, -5, 'torn'),
         (-12.0, 48, 0.70, -3, 'x'), (0.2, 48, 0.71, 3, 'patch frown'), (12.2, 48, 0.69, -2, 'circle'),
         (-5.4, 68, 0.70, 2, 'torn'), (5.6, 68, 0.69, -3, 'straps')]
CABLE_Y = 31.0; BEAR_TOP = 28.4
# plush-bear anatomy, back to front: (part, cx, cy, rx, ry, angle°). Angle tilts the long axis: + = its lower end swings right.
PARTS = [('ear', -2.15, 0.85, 1.05, 1.05, 0), ('ear', 2.15, 0.85, 1.05, 1.05, 0),
         ('leg', -1.8, 11.5, 1.3, 1.75, -14), ('leg', 1.8, 11.5, 1.3, 1.75, 14),
         ('body', 0, 8.3, 3.0, 3.0, 0), ('body', 0, 6.3, 2.45, 2.1, 0),
         ('arm', -2.85, 6.7, 0.95, 1.95, -28), ('arm', 2.85, 6.7, 0.95, 1.95, 28),
         ('head', 0, 2.9, 2.75, 2.35, 0), ('muzzle', 0, 3.85, 1.2, 0.88, 0),
         ('sole', -2.05, 12.55, 1.0, 0.78, -14), ('sole', 2.05, 12.55, 1.0, 0.78, 14),
         ('pad', -3.58, 8.1, 0.6, 0.5, -28), ('pad', 3.58, 8.1, 0.6, 0.5, 28)]
BEAR_BOXES = []
def burnt_off(bi, part, sgn):
    """decay: one limb or ear of some bears has burnt away"""
    return DECAY and ((part == 'ear' and h32(bi, 1) % 3 == 0 and sgn == (1 if h32(bi, 2) % 2 else -1)) or (part in ('arm', 'pad') and h32(bi, 3) % 4 == 0 and sgn == (1 if h32(bi, 4) % 2 else -1)))
def bear_hit(bi, lx, ly):
    hit = None
    for (part, cx_, cy_, rx, ry, ang) in PARTS:
        if burnt_off(bi, part, 1 if cx_ > 0 else -1): continue
        dx_, dy_ = math.sin(math.radians(ang)), math.cos(math.radians(ang))            # long-axis direction (screen, y down)
        px_, py_ = lx - cx_, ly - cy_
        a_ = (px_ * dy_ - py_ * dx_) / rx; b_ = (px_ * dx_ + py_ * dy_) / ry; d = a_ * a_ + b_ * b_
        if d <= 1: hit = (part, a_ * dy_ + b_ * dx_, -a_ * dx_ + b_ * dy_, math.sqrt(1 - d), cx_, cy_)
    return hit
def draw_bear(bi, wx, z, sc, tilt, deco):
    s = F / z * sc; (bx, by) = proj(wx, BEAR_TOP, z)
    ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    x0, x1, y0, y1 = int(bx - 5.4 * s), int(bx + 5.4 * s) + 1, int(by - 0.5 * s), int(by + 14.6 * s) + 1
    BEAR_BOXES.append({'i': bi, 'cx': round(bx, 1), 'top': round(by, 1), 'bottom': round(by + 13.4 * s, 1), 'w': round(8.4 * s, 1), 'z': z})
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            dx, dy = (x - bx) / s, (y - by) / s
            lx, ly = dx * ct + dy * st, -dx * st + dy * ct
            hit = bear_hit(bi, lx, ly)
            if hit: put(x, y, 'bear', bi, z, (hit, lx, ly, deco))
    # the rope from the cable to the scalp
    (rx_, ry_) = proj(wx, CABLE_Y - 0.4 * math.sin(math.pi * (wx - XL) / (XR - XL)) * 1.6, z)
    for y in range(int(ry_), int(by + 0.6 * s)):
        put(int(rx_ + (y - ry_) * 0.0), y, 'rope', 0, z - 0.02)
# pennant colours: faded festival red, ochre, bone, dark red
PEN_COLS = 4
def bunting(z, wy, sag, seed, every=1.35):
    pts = line3d((XL, wy, z), (XR, wy, z), sag, 'cable', 0)
    r = random.Random(seed); u = XL + 0.8; k = 0
    while u < XR - 0.8:
        t = (u - XL) / (XR - XL); cy = wy - sag * math.sin(math.pi * t)
        if not (DECAY and r.random() < 0.38):
            ln = 1.5 * (0.55 if DECAY and r.random() < 0.4 else 1.0)
            tri = [proj(u - 0.48, cy, z), proj(u + 0.48, cy, z), proj(u + r.uniform(-0.12, 0.12), cy - ln, z)]
            fill_poly(tri, 'pennant', (k % PEN_COLS) + (10 if DECAY and r.random() < 0.5 else 0), z - 0.03)
        if GROWTH and r.random() < 0.7:                               # leaves and flowers twining along the line
            (lx_, ly_) = proj(u + 0.6, cy, z); rr = max(1, int(0.35 * F / z))
            for ddy in range(-rr, rr + 1):
                for ddx in range(-rr, rr + 1):
                    if ddx * ddx + ddy * ddy <= rr * rr: put(int(lx_) + ddx, int(ly_) + ddy, 'leaf', ddy, z - 0.04)
            if r.random() < 0.35:                                     # a hanging tendril
                for j in range(int(r.uniform(0.8, 2.6) * F / z)): put(int(lx_) + (j // 5) % 2, int(ly_) + j, 'ivy', 0, z - 0.04)
        u += every; k += 1
TREES = [(-19.3, 18.5, 'cherry'), (19.3, 23.0, 'pear'), (-19.3, 29.0, 'young'), (19.3, 36.0, 'cherry'), (-19.3, 44.0, 'pear'),
         (19.3, 53.0, 'young'), (-19.3, 64.0, 'cherry'), (19.3, 78.0, 'pear'), (-19.3, 96.0, 'young')] if GROWTH else []
def tree(wx, z, kind, seed):
    r = random.Random(seed); s_ = F / z
    (tx, ty0) = proj(wx, 0, z); (_, ty1) = proj(wx, 8.2, z); tw = max(1, int(0.34 * s_))
    for y in range(int(ty1), int(ty0) + 1):                                                    # trunk with a slight lean
        lean = int((ty0 - y) * 0.05 * (1 if wx < 0 else -1))
        for dx in range(-tw, tw + 1): put(int(tx) + dx + lean, y, 'trunk', dx, z)
    for _ in range(4):                                                                          # boughs
        ang = math.radians(r.uniform(35, 145)); ln = r.uniform(1.6, 2.8) * s_; (bx, by) = proj(wx, r.uniform(6.2, 8.0), z)
        for j in range(int(ln)): put(int(bx + math.cos(ang) * j), int(by - math.sin(ang) * j), 'trunk', 0, z)
    (gx0, gy) = proj(wx - 0.9, 0, z - 0.6); (gx1, _) = proj(wx + 0.9, 0, z - 0.6)              # iron tree grate
    for x in range(int(gx0), int(gx1) + 1):
        for y in range(int(gy) - max(1, int(0.12 * s_)), int(gy) + 1): put(x, y, 'grate', 0, z - 0.6)
    inward = 1 if wx < 0 else -1                                                                  # crowns lean over the street, clear of the walls
    for _ in range(11):
        cx_ = wx + inward * r.uniform(-0.6, 2.6); cy_ = 10.2 + r.uniform(-1.3, 1.7); rr = r.uniform(1.2, 1.8)
        (ccx, ccy) = proj(cx_, cy_, z); R = rr * s_
        for y in range(int(ccy - R), int(ccy + R) + 1):
            for x in range(int(ccx - R), int(ccx + R) + 1):
                nx, ny = (x - ccx) / R, (y - ccy) / R; d = nx * nx + ny * ny
                if d <= 1 and (d < 0.7 or h32(x, y, seed) % 3): put(x, y, 'crown', (kind, nx, ny, math.sqrt(1 - d)), z - 0.01)
for i, (wx, z, kind) in enumerate(TREES): tree(wx, z, kind, 700 + i)
# far-to-near so nearer ropes, bunting and bears cover farther ones
ROWS = sorted({b[1] for b in BEARS} | {19.0, 29.0, 41.0, 58.0, 90.0}, reverse=True)
for z in ROWS:
    if z in {b[1] for b in BEARS}:
        line3d((XL, CABLE_Y, z), (XR, CABLE_Y, z), 1.6, 'cable', 0)
        for bi, b in enumerate(BEARS):
            if b[1] == z: draw_bear(bi, *b)
        bunting(z, CABLE_Y + 2.6, 1.2, int(z * 7))
    else:
        bunting(z, 33.6 - (z % 3) * 0.6, 1.8, int(z * 13))
json.dump({'variant': VARIANT, 'bears': BEAR_BOXES}, open(f'{OUT}/bears.json', 'w'), indent=1)

# --- fire: tongues as a billboard (pit in the road; on the decay variant the bears themselves burn)
def flames(cx_, base_y, z, width, height, seed, around=False, tau=0.0, sink=None):
    """a fire in a front plane at depth z: a teardrop envelope split into wavering tongues, hottest a little above
    the base. tau (0..2pi) animates it as a seamless loop (waves travel up the tongues, tips flicker).
    around=True (a burning bear): the flames lick round the silhouette and only the hottest spots cover the bear.
    Returns the screen bbox; pixels go to sink(x, y, level)."""
    r = random.Random(seed); ph = r.uniform(0, 6); k = r.uniform(7.5, 10.5); ph2 = r.uniform(0, 6)
    (sx0, sy0) = proj(cx_ - width / 2 - 0.5, base_y + height * 1.05, z); (sx1, sy1) = proj(cx_ + width / 2 + 0.5, base_y - 0.1, z)
    box = (max(0, int(sx0)), max(0, int(sy0)), min(W - 1, int(sx1) + 1), min(H - 1, int(sy1) + 1))
    for y in range(box[1], box[3] + 1):
        for x in range(box[0], box[2] + 1):
            u, v = (x - CX) * z / F, CAMH - (y - HY) * z / F
            t = (v - base_y) / height
            if t > 1 or t < 0: continue
            a = (u - cx_) / (width / 2) + 0.17 * t * math.sin(t * 9 + ph2 - tau) + 0.05 * math.sin(v * 3.1 + ph - tau)
            if abs(a) >= 1: continue
            if t < 0.12 * a * a: continue                                                         # bowl-shaped underside
            tongue = 0.5 + 0.5 * math.cos(a * k + ph + 0.45 * math.sin(tau))
            env = (1 - a * a) ** 0.55 * (0.42 + 0.58 * tongue ** 0.7) * (0.9 + 0.1 * math.sin(tau * 2 + a * 4 + ph))
            if t >= env: continue
            heat = (1 - t / env) * (1 - 0.55 * abs(a)) * min(1.0, (t - 0.12 * a * a + 0.02) / 0.16)
            if heat < 0.2 and (x + y) % 2: continue                                              # soft dithered rim
            if around and M[y][x][0] == 'bear' and heat < 0.62: continue
            sink(x, y, 4 if heat > 0.72 else 3 if heat > 0.55 else 2 if heat > 0.4 else 1 if heat > 0.24 else 0)
    return box
def smoke(cx_, base_y, z, height, spread, seed, thick):
    r = random.Random(seed)
    (bx, by) = proj(cx_, base_y, z)
    for j in range(int(height * F / z)):
        t = j / max(1, height * F / z); y = int(by - j); xw = int((0.6 + spread * t) * F / z)
        xc = bx + 14 * math.sin(t * 5 + seed) * t + 26 * t
        for dx in range(-xw, xw + 1):
            x = int(xc + dx)
            if 0 <= x < W and 0 <= y < H and M[y][x][0] in ('sky', 'skyline', 'cable', 'pennant', 'smoke') and h32(x, y, seed) % (thick + int(t * 3)) == 0:
                M[y][x] = ('smoke', int(t * 10))
def logs(cx_, z, n, ln, seed):
    r = random.Random(seed)
    for i in range(n):
        ang = math.pi * i / n + r.uniform(-0.2, 0.2); dx, dz = math.cos(ang) * ln / 2, math.sin(ang) * ln / 2 * 0.6
        for j in range(41):
            t = j / 40 - 0.5; wx, wz = cx_ + dx * 2 * t, z + dz * 2 * t
            (sx, sy) = proj(wx, 0.35, wz); rr = max(1, int(0.32 * F / wz))
            for ddy in range(-rr, rr + 1):
                for ddx in range(-rr, rr + 1):
                    if ddx * ddx + ddy * ddy <= rr * rr: put(int(sx) + ddx, int(sy) + ddy, 'log', ddy, wz - 0.1)
if not GROWTH: logs(PIT[0], PIT[1], 5 if DECAY else 3, 3.0 if DECAY else 2.2, 4)
FIRES = []                                                                                    # (name, flames() args) -> animated sprite frames
if DECAY:
    for bi, (wx, z, sc, tilt, deco) in enumerate(BEARS):
        FIRES.append((f'b{bi}', (wx, BEAR_TOP - 13.4 * sc, z - 0.3, 10.5 * sc, 19.0 * sc, 300 + bi, True)))
        smoke(wx, BEAR_TOP + 1.5, z, 40, 4.5, 500 + bi, 2)
    FIRES.append(('pit', (PIT[0], 0.3, PIT[1], 4.4, 9.5, 9, False)))
    smoke(PIT[0], 8, PIT[1], 50, 6, 99, 2)
elif not GROWTH:
    FIRES.append(('pit', (PIT[0], 0.3, PIT[1], 2.2, 3.6, 9, False)))
NFRAMES = 6
FIRE_COLS = [RED[5], FLOWER[1], GLOW[3], GLOW[4], FLOWER[2]]
def build_fire_atlas():
    """6-frame loops of every fire, packed into one atlas whose frames are 'trimmed' against the full 1067x600 canvas:
    a sprite at (0,0) with origin (0,0) lands each frame exactly where the fire belongs in the background."""
    if not FIRES: return
    rows = []
    for (name, args) in FIRES:
        frames = []
        for f in range(NFRAMES):
            pix = {}
            box = flames(*args[:6], around=args[6], tau=2 * math.pi * f / NFRAMES, sink=lambda x, y, l: pix.__setitem__((x, y), l))
            frames.append((box, pix))
        rows.append((name, frames))
    fw = {n: fr[0][0][2] - fr[0][0][0] + 1 for (n, fr) in rows}; fh = {n: fr[0][0][3] - fr[0][0][1] + 1 for (n, fr) in rows}
    AW = max(fw[n] * NFRAMES for n in fw); AH = sum(fh.values())
    atlas = Image.new('RGBA', (AW, AH), (0, 0, 0, 0)); ap = atlas.load(); meta = {}; oy = 0
    for (name, frames) in rows:
        for f, (box, pix) in enumerate(frames):
            ox = f * fw[name]
            for (x, y), l in pix.items(): ap[ox + x - box[0], oy + y - box[1]] = FIRE_COLS[l] + (255,)
            meta[f'{name}_{f}'] = {'frame': {'x': ox, 'y': oy, 'w': fw[name], 'h': fh[name]}, 'rotated': False, 'trimmed': True,
                                   'spriteSourceSize': {'x': box[0], 'y': box[1], 'w': fw[name], 'h': fh[name]}, 'sourceSize': {'w': W, 'h': H}}
        oy += fh[name]
    atlas.save(f'{OUT}/fire_{VARIANT}.png')
    json.dump({'frames': meta, 'meta': {'image': f'bbs_fire_{VARIANT}.png', 'size': {'w': AW, 'h': AH}, 'scale': 1}}, open(f'{OUT}/fire_{VARIANT}.json', 'w'))
build_fire_atlas()

# --- growth: ivy climbing the facades from the pavement
if GROWTH:
    random.seed(23)
    WALL = ('plaster', 'stucco', 'brick', 'plinth', 'quoin', 'cornice', 'band', 'sill', 'hood', 'moss', 'shutter')
    for _ in range(16):
        side = random.choice((-1, 1)); z0 = random.uniform(8, 70)
        (x, y) = proj(XL if side < 0 else XR, 0.2, z0); ang = math.radians(90 + random.uniform(-20, 20)); n = random.randint(90, 330)
        for i in range(n):
            ang += random.uniform(-0.35, 0.35); ang = max(math.radians(30), min(math.radians(150), ang))
            x += math.cos(ang); y -= math.sin(ang); xi, yi = int(x), int(y)
            if not (0 <= xi < W and 0 <= yi < H) or M[yi][xi][0] not in WALL + ('ivy', 'ivyleaf'): break
            M[yi][xi] = ('ivy', 0)
            if i % 7 == 3:
                rr = 2 if Z[yi][xi] < 30 else 1
                for dy in range(-rr, rr + 1):
                    for dx in range(-rr, rr + 1):
                        if dx * dx + dy * dy <= rr * rr and 0 <= xi + dx < W and 0 <= yi + dy < H and M[yi + dy][xi + dx][0] in WALL: M[yi + dy][xi + dx] = ('ivyleaf', dy)

# ================================================================== shading
px = [[None] * W for _ in range(H)]
def ramp_i(k, i):
    r = RAMPS[k]; return r[max(0, min(len(r) - 1, int(i)))]
PEN = [RED[4], CAP[3], BONE[3], RED[2]]
FUR = WARM                                    # stuffed bear-skins: dusty ochre-brown
WALL_RAMP = {'plaster': 'T', 'stucco': 'P', 'brick': 'W'}
WALL_BIAS = {'plaster': 0.0, 'stucco': -0.7, 'brick': 0.0}
for y in range(H):
    for x in range(W):
        k, obj = M[y][x]; z = Z[y][x]
        if k == 'sky':
            t = y / HY
            v = 1.4 + 4.4 * t ** 1.3 + (nA(x * 0.55, y * 2.6) - 0.5) * 1.8 + (nB(x * 0.5, y * 2.4) - 0.5) * 0.6
            v += 0.9 * math.exp(-(((x - 520) / 220) ** 2 + ((y - 120) / 110) ** 2))
            if DECAY: v -= 0.8
            if GROWTH: v += 0.7
            px[y][x] = ramp_i('K', band(v, x, y)); continue
        if k == 'smoke': px[y][x] = HAZE[1 if obj < 4 else 2] if DECAY else HAZE[4]; continue
        if k == 'skyline':
            px[y][x] = fogged(HAZE[1] if h32(obj, 3) % 3 else HAZE[2], fog_of(z) * 0.55, x, y); continue
        if k == 'cable': px[y][x] = fogged(STONE[0], fog_of(z) * 0.8, x, y); continue
        if k == 'rope': px[y][x] = fogged(WOOD[2] if (y % 3) else WOOD[1], fog_of(z) * 0.8, x, y); continue
        if k == 'pennant':
            c = PEN[obj % 10]
            if obj >= 10: c = WOOD[1] if (x + y) % 3 else WARM[1]                                     # scorched
            elif (x + y) % 7 == 0: c = STONE[4]
            px[y][x] = fogged(c, fog_of(z) * 0.85, x, y); continue
        if k == 'leaf':
            c = LEAF[3 if obj < -1 else 2 if obj < 1 else 1]
            if h32(x, y, 51) % 4 == 0: c = FLOWER[h32(x, y, 52) % 5]
            px[y][x] = fogged(c, fog_of(z) * 0.7, x, y); continue
        if k == 'ivy': px[y][x] = fogged(LEAF[0] if (x + y) % 3 else LEAF[1], fog_of(z) * 0.7, x, y); continue
        if k == 'ivyleaf':
            c = LEAF[3 if obj < -1 else 2 if obj < 1 else 1] if h32(x, y, 61) % 31 else FLOWER[3]
            px[y][x] = fogged(c, fog_of(z) * 0.7, x, y); continue
        if k == 'trunk': px[y][x] = fogged(WARM[1] if obj < 0 else WARM[3] if obj > 0 else WARM[2], fog_of(z) * 0.8, x, y); continue
        if k == 'grate': px[y][x] = fogged(STONE[1] if (x % 3) else STONE[3], fog_of(z), x, y); continue
        if k == 'crown':
            kind, nx, ny, nz = obj
            lam = -0.4 * nx - 0.6 * ny + 0.7 * nz + (nC(x * 2, y * 2) - 0.5) * 0.5
            if kind == 'cherry': c = ramp_i('Q', band(1.2 + lam * 3.2, x, y))
            elif kind == 'pear': c = FLOWER[4] if lam > 0.55 else STONE[8] if lam > 0.2 else (LEAF[3] if lam > -0.15 else LEAF[2])
            else: c = LEAF[5] if lam > 0.7 else LEAF[4] if lam > 0.3 else LEAF[3] if lam > -0.1 else LEAF[2]
            if kind == 'young' and h32(x, y, 43) % 13 == 0: c = FLOWER[2]
            px[y][x] = fogged(c, fog_of(z) * 0.8, x, y); continue
        if k == 'log': px[y][x] = (WOOD[2] if obj < 0 else WOOD[1]) if (x + y) % 4 else (GLOW[0] if DECAY else WOOD[0]); continue
        if k == 'flame':
            c = [RED[4], WARM[4], GLOW[1], GLOW[3], GLOW[4]][obj]
            px[y][x] = c; continue
        if k == 'bear':
            (part, nx, ny, nz, pcx, pcy), lx, ly, deco = UV[y][x]
            lam = -0.45 * nx - 0.55 * ny + 0.7 * nz
            i = 1.3 + 2.3 * lam + (nC(x * 1.3, y * 1.3) - 0.5) * 0.9 + (0.5 if h32(x, y, obj) % 5 == 0 else 0)
            c = FUR[max(0, min(5, band(i, x, y)))]
            if h32(x // 2, y // 2, obj) % 7 == 0 and part not in ('muzzle', 'pad', 'sole'): c = FUR[max(0, min(5, band(i - 0.9, x, y)))]   # curly plush
            if part in ('muzzle', 'pad', 'sole'): c = CAP[max(0, min(5, band(i + 0.4, x, y)))]
            if part == 'ear' and math.hypot(lx - pcx * 0.9, ly - pcy - 0.15) < 0.55: c = CAP[max(0, min(5, band(i - 0.4, x, y)))]
            # stitched centre seam, eyes, nose, mouth
            if part in ('body', 'head') and abs(lx) < 0.09 and not (part == 'head' and ly > 3.2): c = WOOD[1]
            if part == 'body' and abs(lx) < 0.32 and abs(((ly * 2) % 1) - 0.5) < 0.12: c = WOOD[1]
            for sx in (-1.0, 1.0):
                if math.hypot(lx - sx, ly - 2.55) < 0.29: c = INK if math.hypot(lx - sx + 0.09, ly - 2.47) > 0.1 else STONE[7]
                if 'straps' in deco and abs(ly - 2.45) < 0.6 and abs(lx - sx) < 0.5 and abs((lx - sx) - (ly - 2.45)) < 0.14: c = RED[4]
            if math.hypot((lx) / 0.46, (ly - 3.42) / 0.32) < 1: c = WOOD[0] if math.hypot(lx + 0.12, ly - 3.34) > 0.1 else WARM[2]
            if part == 'muzzle' and abs(lx) < 0.06 and 3.7 < ly < 4.15: c = WOOD[1]
            mouth = 4.2 + (0.22 if 'frown' in deco else -0.24) * (1 - (lx / 0.62) ** 2)
            if part == 'muzzle' and abs(lx) < 0.62 and abs(ly - mouth) < 0.06: c = WOOD[1]
            # festival marks
            if part == 'body':
                if 'x' in deco.split() and (abs(lx - (ly - 8.2) * 0.75) < 0.32 or abs(lx + (ly - 8.2) * 0.75) < 0.32) and abs(ly - 8.2) < 2.0: c = RED[4] if (x + y) % 4 else RED[3]
                if 'straps' in deco and (abs(lx - (ly - 7.6) * 1.1) < 0.36 or abs(lx + (ly - 7.6) * 1.1) < 0.36): c = RED[4] if (x // 2 + y) % 6 else RED[2]
                if 'circle' in deco:
                    rr = math.hypot(lx, ly - 8.3)
                    if abs(rr - 1.25) < 0.2 or (rr < 0.4) or (abs(lx) < 0.12 and rr < 1.25): c = WOOD[1]
                if 'patch' in deco and 0.5 < lx < 2.1 and 8.4 < ly < 10.0:
                    c = BONE[2] if ((x + y) % 2) else BONE[1]
                    if min(lx - 0.5, 2.1 - lx, ly - 8.4, 10.0 - ly) < 0.12 and (x + y) % 2: c = WOOD[1]
                if 'torn' in deco and ((lx + 1.0) / 0.55) ** 2 + ((ly - 9.6) / 0.95) ** 2 < 1:
                    c = CAP[4] if h32(x, y, 7) % 3 else (STONE[8] if h32(x, y, 8) % 2 else CAP[2])      # straw + crumpled notes
            if DECAY:
                ch = nF(x * 1.8 + obj * 17, y * 1.8) + (ly / 14.0) * 0.55
                if ch > 1.05: c = INK if (x + y) % 3 else WOOD[0]
                elif ch > 0.97: c = GLOW[1] if h32(x, y, 31) % 2 else RED[4]                                          # ember rim
                elif ch > 0.85: c = FUR[max(0, min(5, band(i - 2.0, x, y)))]                                           # scorched
            px[y][x] = fogged(c, fog_of(z) * 0.8, x, y); continue
        if k in ('sett', 'gutter', 'kerb', 'pave', 'puddle', 'pitstone', 'ash', 'bed'):
            wx, wz, _ = UV[y][x]; f = fog_of(wz)
            jz = max(0.09, 1.2 * wz * wz / (F * CAMH)); jx = max(0.08, 1.2 * wz / F)
            if k == 'puddle':
                c = SKY[3] if (x + y) % 2 else STONE[2]
                if h32(x, y, 5) % 19 == 0: c = SKY[5]
                if DECAY and h32(x, y, 6) % 9 == 0: c = GLOW[0]                                       # fire reflected
            elif k == 'sett':
                row = math.floor(wz / 0.78); fz = wz / 0.78 - row
                off = 0.55 if row % 2 else 0.0; col = math.floor(wx / 1.1 + off); fx = wx / 1.1 + off - col
                v = 2.7 + (h32(row, col, 3) % 4) * 0.3 + (nC(x, y) - 0.5) * 0.7 - 0.6 * max(0.0, (y - 520) / 80)
                joint = (fz < jz / 0.78 or fx < jx / 1.1) and jz < 0.3
                if joint: v = 1.0
                elif fz > 0.8: v += 0.5                                                              # the near lip of each stone catches light
                c = ramp_i('T', band(v, x, y))
                if joint and GROWTH and nC(x * 0.7, y * 0.7) > 0.75 and wz < 28: c = (LEAF[2] if (x + y) % 2 else LEAF[3]) if h32(x, y, 34) % 9 else FLOWER[4]
                elif not joint and GROWTH and nA(x * 1.3 + 9, y * 1.3) > 0.8 and h32(x, y, 33) % 3 == 0: c = LEAF[1]
                # scorch rings left by past festivals around the pit
                d = math.hypot(wx - PIT[0], wz - PIT[1])
                if d < 4.2 and h32(x, y, 77) % 4 < (3 if d < 2.8 else 1): c = ramp_i('T', max(0, band(v - 1.6, x, y)))
            elif k == 'gutter': c = ramp_i('T', 1 if (x + y) % 4 else 2)
            elif k == 'kerb': c = ramp_i('T', 6 if abs(wx) < KERB + 0.2 else 4)
            elif k == 'pave':
                sl = 2.3; fz = (wz / sl) % 1; fx = ((abs(wx) - KERB) / sl) % 1
                v = 3.6 + (h32(int(wz / sl), int(abs(wx) / sl), int(wx > 0)) % 3) * 0.3 + (nC(x, y) - 0.5) * 0.6
                if (fz < jz / sl or fx < jx / sl) and jz < 0.5: v = 1.6
                c = ramp_i('T', band(v, x, y))
                if GROWTH and any(abs(wx - tx_) < 3.2 and abs(wz - tz_) < 2.6 for (tx_, tz_, _) in TREES) and h32(x, y, 35) % 5 == 0: c = FLOWER[3 + h32(x, y, 36) % 2]   # fallen petals
            elif k == 'bed':
                v = 2.2 + (nC(x, y) - 0.5) * 0.8
                c = LEAF[2 + h32(x // 2, y // 2, 37) % 3] if h32(x, y, 38) % 3 else FLOWER[h32(x // 2, y, 39) % 5]
            elif k == 'pitstone':
                ang = math.atan2(wz - PIT[1], wx - PIT[0]); st = int((ang + math.pi) / (2 * math.pi) * 11)
                v = 3.4 + (h32(st, 5) % 3) * 0.4 - (1.6 if abs(((ang + math.pi) / (2 * math.pi) * 11) % 1 - 0.5) > 0.42 else 0)
                c = ramp_i('T', band(v, x, y))
                if GROWTH and h32(x, y, 3) % 3 == 0: c = LEAF[2]
            else:
                c = STONE[1] if (x + y) % 3 else STONE[2]
                if not GROWTH and h32(x, y, 4) % (5 if DECAY else 13) == 0: c = GLOW[0] if h32(x, y, 5) % 2 else RED[3]
                if GROWTH: c = LEAF[2 + h32(x, y, 6) % 3] if h32(x, y, 7) % 4 else FLOWER[h32(x, y, 8) % 5]
            px[y][x] = fogged(c, f, x, y); continue
        # ---- facades
        u, v, face = UV[y][x]; f = fog_of(z)
        fl = (-0.55 if face.const < 0 else -1.0) if face.kind == 'side' else 0.0
        fl += 0.45 * (v / 40.0)
        b = BLD.get(face.obj)
        if k in ('plaster', 'stucco', 'brick', 'quoin', 'band'):
            rk = WALL_RAMP.get(b[3] if b else 'plaster', 'T') if k in ('quoin', 'band') else WALL_RAMP[k]
            i = 3.0 + fl + WALL_BIAS.get(b[3] if b else 'plaster', 0) + (nA(x * 1.6, y * 1.6) - 0.5) * 1.1 + (nB(x, y) - 0.5) * 0.4
            i -= 1.3 * max(0.0, 1 - v / 3.0)                                                        # damp, grime at street level
            if k == 'brick':
                i -= 0.6
                course = math.floor(v / 0.38); bu = u / 0.95 + (0.5 if course % 2 else 0)
                if (v / 0.38) % 1 < 0.22 * z / 30 or bu % 1 < 0.12 * z / 30: i = 1.5 + fl
                elif h32(course, int(bu), 3) % 5 == 0: i -= 0.6
            if k == 'quoin': i += 0.9 - (0.9 if (v % 1.6) < 0.18 else 0)
            if k == 'band': i += 1.0
            if b and k != 'quoin':                                                                   # streaks under each window
                lu = (u - (b[0] + 1.6)) % WIN_DZ; lvb = (v - GF) % STOREY
                if lu < WIN_W and 0.2 < lvb < 1.5 and nB(x * 3, y) > 0.55: i -= 0.6
                if DECAY and lu < WIN_W + 0.2 and 6.9 < lvb < 9.0 and v > GF and nF(x * 3, y * 0.6) > 0.52: i -= 1.3 + (lvb < 7.9) * 0.8   # soot over windows
            c = ramp_i(rk, band(i, x, y))
        elif k == 'cornice':
            c = ramp_i('T', 5.4 + fl if (v * 12) % 5 > 1 else 3.2 + fl)
            if DECAY and nF(x * 3, y * 1.2) > 0.66: c = STONE[2]
        elif k == 'plinth': c = ramp_i('T', 2.2 + fl * 0.5 if (u * 1.1) % 1 > 0.08 else 1)
        elif k == 'sill': c = ramp_i('T', 5.5 + fl)
        elif k == 'hood': c = ramp_i('T', 4.6 + fl)
        elif k == 'roof':
            i = 2.2 + (nB(x, y) - 0.5) * 0.8 + 0.6 * ((v - b[2]) / 3.2 if b else 0)
            if (u * 1.2) % 1 < 0.1: i -= 1.0
            c = ramp_i('E', band(i, x, y))
        elif k == 'dormer': c = ramp_i('T', 0 if (u * 6) % 4 > 0.6 else 2)
        elif k in ('win', 'winlit', 'shutter') and b:
            lu = (u - (b[0] + 1.6)) % WIN_DZ; lv = (v - GF - 2.0) % STOREY
            frame = lu < 0.14 or lu > WIN_W - 0.14 or lv < 0.14 or lv > 4.66 or abs(lu - WIN_W / 2) < 0.08 or abs(lv - 3.3) < 0.08
            if k == 'shutter':
                c = ramp_i('D', 3 if (lv * 4) % 1 > 0.25 else 2) if abs(lu - WIN_W / 2) > 0.07 else WOOD[1]
                if GROWTH and (lv * 4) % 1 < 0.25: c = LEAF[1]
            elif k == 'winlit':
                c = STONE[3] if frame else (GLOW[0] if lv < 3.3 else GLOW[1])
                f *= 0.5
            else:
                c = STONE[3 + (1 if fl > -0.6 else 0)] if frame else (STONE[0] if lv < 3.0 else SKY[2] if (lu + lv) % 1.6 < 0.4 else STONE[1])
                if DECAY and not frame and abs(((lu * 3.1) % 1) - ((lv * 1.7) % 1)) < 0.09: c = STONE[5]           # cracked panes
                if DECAY and not frame and h32(int(u / WIN_DZ), int(v / STOREY), face.obj) % 6 == 0: c = INK              # smashed out
        elif k in ('win', 'winlit', 'shutter'): c = STONE[1] if (x + y) % 2 else STONE[2]
        elif k == 'flowerbox':
            c = WOOD[2] if (v - GF) % STOREY > 1.45 else (FLOWER[h32(x, y, 5) % 4] if h32(x, y, 6) % 3 == 0 else LEAF[2 + (x + y) % 2])
        elif k == 'door':
            c = ramp_i('D', 1.6 if (u * 3.2) % 1 > 0.12 else 0.6)
            if v < 0.4: c = STONE[1]
        elif k == 'shopframe': c = ramp_i('D', 2.4 + fl * 0.5 if (x + y) % 6 else 1.6)
        elif k == 'shop':
            c = STONE[0] if (v * 2.2) % 1 > 0.08 else STONE[2]
            if (u * 1.3) % 1 < 0.06: c = STONE[2]
            if DECAY and nF(x * 3, y * 3) > 0.6: c = INK
        elif k == 'shoplit':
            c = GLOW[0] if (v * 2.2) % 1 > 0.1 and (u * 1.3) % 1 > 0.07 else STONE[1]
            if h32(x // 2, y // 2, 4) % 9 == 0: c = GLOW[1]
            f *= 0.5
        elif k == 'passage':
            dpt = max(0.0, 1 - v / 6.4); c = INK if (h32(x, y, 3) % 5 or dpt < 0.3) else STONE[0]
            if v < 0.5: c = STONE[1]
        elif k == 'lantern': c = (GLOW[1] if (x + y) % 2 else GLOW[0]) if (DECAY or h32(face.obj, int(u), 2) % 3 == 0) else (STONE[1] if (y % 3) else STONE[3])
        elif k == 'moss':
            drip = nF(x * 4.0, y * 0.5) > (0.42 if GROWTH else 0.5)
            if not drip: c = ramp_i(WALL_RAMP.get(b[3], 'T') if b else 'T', band(2.2 + fl, x, y))
            else: c = (LEAF[1] if (x + y) % 3 else LEAF[2]) if GROWTH else (ramp_i('K', 3) if (x + y) % 3 else ramp_i('T', 2))
        elif k == 'clock': c = BONE[3] if math.hypot(u, v - 43) < 2.4 else STONE[3]
        else: c = STONE[3]
        px[y][x] = fogged(c, f, x, y)
if DECAY:
    random.seed(13)
    for _ in range(40):                                                                           # litter, ash and charred scraps
        cx_, cy_ = random.randint(10, W - 10), random.randint(420, 595)
        if M[cy_][cx_][0] not in ('sett', 'pave', 'gutter'): continue
        for _k in range(random.randint(5, 16)):
            x, y = cx_ + random.randint(-8, 8), cy_ + random.randint(-3, 2)
            if 0 <= x < W and 0 <= y < H and M[y][x][0] in ('sett', 'pave', 'gutter', 'kerb'):
                px[y][x] = [STONE[1], STONE[7], WARM[1], RED[2], WOOD[0], INK, CAP[2]][random.randint(0, 6)]

# ================================================================== outlines
RANK = {'sky': 0, 'skyline': 0, 'cable': 0, 'smoke': 0, 'rope': 1, 'sett': 1, 'gutter': 1, 'kerb': 1, 'pave': 1, 'puddle': 1, 'ash': 1, 'pitstone': 2,
        'pennant': 3, 'bear': 4, 'flame': 5, 'log': 3, 'crown': 3, 'trunk': 3, 'grate': 2, 'bed': 1, 'leaf': 3, 'ivy': 2, 'ivyleaf': 2}
SOFT_PAIRS = [('sky', 'skyline'), ('sky', 'cable'), ('skyline', 'cable'), ('sky', 'smoke'), ('smoke', 'cable'), ('smoke', 'skyline'), ('smoke', 'pennant'), ('rope', 'sky'), ('rope', 'cable'),
              ('sett', 'gutter'), ('gutter', 'kerb'), ('kerb', 'pave'), ('sett', 'puddle'), ('pave', 'puddle'), ('sett', 'ash'), ('pitstone', 'ash'),
              ('plaster', 'cornice'), ('stucco', 'cornice'), ('brick', 'cornice'), ('plaster', 'moss'), ('stucco', 'moss'), ('brick', 'moss'), ('cornice', 'moss'),
              ('plaster', 'band'), ('stucco', 'band'), ('brick', 'band'), ('plaster', 'quoin'), ('stucco', 'quoin'), ('brick', 'quoin'), ('plaster', 'plinth'), ('stucco', 'plinth'), ('brick', 'plinth'),
              ('roof', 'dormer'), ('sill', 'hood'), ('flame', 'smoke'), ('flame', 'sky'), ('ivy', 'ivyleaf'), ('leaf', 'ivy'), ('leaf', 'cable'), ('leaf', 'pennant'),
              ('win', 'sill'), ('win', 'hood'), ('shutter', 'sill'), ('shutter', 'hood'), ('winlit', 'sill'), ('winlit', 'hood'), ('shop', 'shopframe'), ('shoplit', 'shopframe'), ('passage', 'shopframe'),
              ('flowerbox', 'sill'), ('flowerbox', 'win'), ('flowerbox', 'shutter'), ('flowerbox', 'winlit'), ('bed', 'pave'), ('bed', 'kerb'), ('trunk', 'crown')]
for w_ in ('plaster', 'stucco', 'brick', 'quoin', 'band', 'cornice', 'sill', 'hood', 'moss', 'shutter', 'win', 'winlit', 'plinth', 'flowerbox'): SOFT_PAIRS += [('ivy', w_), ('ivyleaf', w_)]
SOFT = {frozenset(p) for p in SOFT_PAIRS}
def rank(k): return RANK.get(k, 2)
for y in range(H):
    for x in range(W):
        a = M[y][x]
        for nx_, ny_ in ((x + 1, y), (x, y + 1)):
            if nx_ >= W or ny_ >= H: continue
            b2 = M[ny_][nx_]
            if a == b2: continue
            ka, kb = a[0], b2[0]
            if frozenset((ka, kb)) in SOFT or (ka == kb and ka in ('sett', 'pave', 'skyline', 'cable', 'smoke', 'leaf', 'ivyleaf', 'pennant', 'flame')): continue
            if ka == kb == 'bear' and a[1] == b2[1]: continue
            if ka == kb == 'crown': continue
            ra, rb = rank(ka), rank(kb)
            if ra != rb: tx, ty = (x, y) if ra < rb else (nx_, ny_)
            else: tx, ty = (x, y) if str(a) > str(b2) else (nx_, ny_)
            if M[ty][tx][0] == 'flame': continue
            z = Z[ty][tx]
            if z < 48: px[ty][tx] = INK
            elif z < 120: px[ty][tx] = fogged(STONE[0], fog_of(z) * 0.7, tx, ty)
img = Image.new('RGB', (W, H)); ip = img.load()
for y in range(H):
    for x in range(W): ip[x, y] = px[y][x]
img.save(f'{OUT}/bg.png' if VARIANT == 'base' else f'{OUT}/bg_{VARIANT}.png')
print('done', VARIANT)
