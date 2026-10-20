"""Shed 521 exterior — 1067x600, overcast day, one-point perspective (same engine/palette as the Crossroad).
The top-heavy wooden tower of Shed521.png seen frontally, a chain-link fence with an open gate in front, a rutted dirt
yard with rusty pipes snaking into the building, scrap piles, a low annex, a utility pole with cables, hazy skyline."""
import sys, math, random
from PIL import Image, ImageDraw
from pal_day import *
OUT = sys.argv[1]
W, H = 1067, 600
CX, HY = 533, 296
F, CAMH = 300.0, 12.0
random.seed(5)
nA, nB, nC = make_noise(48, 1, W, H), make_noise(13, 2, W, H), make_noise(5, 3, W, H)

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
    def rect(self, u0, v0, u1, v1, kind, obj=None): self.feats.append(('r', (u0, v0, u1, v1), kind, self.obj if obj is None else obj))
    def poly(self, pts, kind, obj=None): self.feats.append(('p', pts, kind, self.obj if obj is None else obj))
    def material_at(self, u, v):
        mat = self.mat
        for (t, g, kind, obj) in self.feats:
            if t == 'r':
                if g[0] <= u < g[2] and g[1] <= v < g[3]: mat = kind
            elif pip(g, u, v): mat = kind
        return mat
FACES = []
def add(f): FACES.append(f); return f
def box(u0, u1, h): return [(u0, 0), (u0, h), (u1, h), (u1, 0)]
def near_z(f): return f.const if f.kind == 'front' else min(u for (u, v) in f.outline)

# --- far skyline: factory chimneys, gas-holders, a few towers
rnd = random.Random(31); SKYLINE = []
for i in range(60):
    wx = -150 + i * 5 + rnd.uniform(-2, 2); z = rnd.choice((150, 180, 210, 250)); w = rnd.uniform(3, 10); h = rnd.uniform(10, 34)
    SKYLINE.append((wx, z, w, h))
SKYLINE += [(-60, 190, 2.2, 70), (-52, 200, 2.2, 62), (48, 210, 14, 30), (70, 180, 2.5, 76), (22, 240, 5, 60)]
# --- mid-distance sheds / tenements left and right, low, foggy
def shedrow(side, z0, z1, h, obj):
    X = -34 if side < 0 else 36
    f = add(Face('side', X, box(z0, z1, h), 'plaster', obj))
    for u in [z0 + 2 + i * 3.2 for i in range(int((z1 - z0 - 2) / 3.2))]:
        f.rect(u, 2.0, u + 1.6, 4.4, 'win' if h32(obj, int(u * 7)) % 3 else 'winlit')
    f.rect(z0, h - 0.5, z1, h, 'cornice')
shedrow(-1, 48, 78, 9, 40); shedrow(-1, 78, 120, 14, 41); shedrow(1, 50, 80, 11, 42); shedrow(1, 80, 125, 16, 43)
for (z, u0, u1, h, obj) in ((78, -80, -34, 14, 44), (80, 36, 90, 16, 45)):
    f = add(Face('front', z, box(u0, u1, h), 'plaster', obj))
    for u in [u0 + 3 + i * 4 for i in range(int((u1 - u0 - 3) / 4))]:
        f.rect(u, h - 5, u + 1.8, h - 2.4, 'win' if h32(obj, int(u)) % 3 else 'winlit')
    f.rect(u0, h - 0.5, u1, h, 'cornice')
add(Face('front', 95, box(-6, -3.6, 40), 'plaster', 46))                                       # a tall chimney behind the tower

# ================================================================== the tower (front face z=26)
SZ = 26.0
SU0, SU1 = -23.0, 11.0
SH_OUT = [(SU0, 0), (SU0, 10), (SU0 - 1.5, 10), (SU0 - 1.5, 19), (SU0 - 3, 19), (SU0 - 3, 28), (SU0 + 6, 28), (SU0 + 6, 35), (SU1 - 6, 35), (SU1 - 6, 28), (SU1 + 1.5, 28), (SU1 + 1.5, 19), (SU1 + 0.5, 19), (SU1 + 0.5, 10), (SU1, 10), (SU1, 0)]
shed = add(Face('front', SZ, SH_OUT, 'plank', 10))
for (v, a, b) in ((10, SU0 - 1.5, SU1 + 0.5), (19, SU0 - 3, SU1 + 1.5), (28, SU0 + 6, SU1 - 6)):
    shed.rect(a, v - 0.4, b, v + 0.6, 'frame'); shed.rect(a, v - 1.6, b, v - 0.4, 'under')
for (v0, v1, a, b) in ((0, 10, SU0, SU1), (10, 19, SU0 - 1.5, SU1 + 0.5), (19, 28, SU0 - 3, SU1 + 1.5), (28, 35, SU0 + 6, SU1 - 6)):
    shed.rect(a, v0, a + 1.0, v1, 'frame'); shed.rect(b - 1.0, v0, b, v1, 'frame')
    mid = (a + b) / 2
    if v0 < 28:
        shed.rect(mid - 0.5, v0, mid + 0.5, v1, 'frame')
        for (p, q) in ((a + 1, mid - 0.5), (mid + 0.5, b - 1)):
            shed.poly([(p, v0 + 0.3), (p + 0.9, v0 + 0.3), (q, v1 - 0.6), (q - 0.9, v1 - 0.6)], 'brace')
            shed.poly([(q, v0 + 0.3), (q - 0.9, v0 + 0.3), (p, v1 - 0.6), (p + 0.9, v1 - 0.6)], 'brace')
GATE0, GATE1 = SU0 + 3, SU0 + 18
shed.rect(GATE0, 0, GATE1, 8.6, 'gate'); shed.rect(GATE0 - 0.6, 8.5, GATE1 + 0.6, 9.4, 'frame')
shed.rect(GATE0 - 0.6, 0, GATE0, 9.4, 'frame'); shed.rect(GATE1, 0, GATE1 + 0.6, 9.4, 'frame')
shed.rect(GATE1 + 2, 5.2, GATE1 + 3, 7.2, 'lamp2')
shed.rect(SU1 - 7, 3, SU1 - 3.5, 6.5, 'win')                                                     # a barred window by the gate
shed.rect(SU0 + 1.6, 3.2, SU0 + 2.6, 5.2, 'bracket')                                             # flange where the left pipe enters
shed.rect(SU0 + 3.5, 12.5, SU0 + 6.5, 16, 'shutter'); shed.rect(SU1 - 6.5, 12.5, SU1 - 3.5, 16, 'shutter'); shed.rect(SU0 + 13, 21.5, SU0 + 16, 24.5, 'shutter')
shed.rect(SU0 + 19, 12, SU0 + 27, 16, 'glyph')
shed.rect(SU0 + 4.5, 21.0, SU1 - 4.5, 26.5, 'plate'); shed.rect(SU0 + 4.0, 20.7, SU1 - 4.0, 21.3, 'frame'); shed.rect(SU0 + 4.0, 26.3, SU1 - 4.0, 26.9, 'frame')
shed.rect(SU0 + 13, 30, SU0 + 19, 33.5, 'win')
for u in [SU0 - 3 + i * 1.6 for i in range(int((SU1 + 1.5 - (SU0 - 3)) / 1.6) + 1)]:
    shed.rect(u, 28, u + 0.35, 29.6, 'frame')
shed.rect(SU0 - 3, 29.4, SU1 + 1.5, 29.9, 'frame')
shed.rect(SU0 + 6, 35, SU1 - 6, 35.7, 'frame'); shed.rect(SU1 - 9, 35, SU1 - 8.4, 41, 'frame')
# the big rusty pipe climbing the tower's right flank (the "pipe and scrap wood" the observe line talks about)
shed.rect(SU1 - 2.6, 0, SU1 - 1.0, 28.4, 'pipewall')
for v in (4, 9.5, 15, 20.5, 26): shed.rect(SU1 - 3.0, v, SU1 - 0.6, v + 0.6, 'bracket')
shed.poly([(SU1 - 2.6, 28.4), (SU1 - 1.0, 28.4), (SU1 - 1.0, 31.5), (SU1 - 2.0, 32.5), (SU1 - 3.6, 32.5), (SU1 - 3.6, 31.3), (SU1 - 2.6, 31.3)], 'pipewall')
rnd = random.Random(9)
for (v, a, b) in ((10, SU0 - 1.5, SU1 + 0.5), (19, SU0 - 3, SU1 + 1.5), (28, SU0 + 6, SU1 - 6)):
    u = a + 1
    while u < b - 1:
        over_plate = (v == 28 and SU0 + 3.5 < u < SU1 - 3.5)
        if rnd.random() < 0.55 and not over_plate: shed.rect(u, v - 1.6 - rnd.uniform(0.6, 2.4), u + rnd.uniform(0.5, 1.4), v - 0.4, 'moss')
        u += rnd.uniform(1.0, 2.6)
SIGN_SHED = ('SHED 521', *[int(c) for c in proj((SU0 + SU1) / 2 - 0.1, 25.6, SZ)], 4)
# right flank (visible: the tower stands left of the vanishing point); the annex in front hides its lower far part
sside = add(Face('side', SU1, [(SZ, 0), (SZ, 35), (SZ + 2, 35), (SZ + 2, 28), (SZ + 9, 28), (SZ + 9, 19), (SZ + 18, 19), (SZ + 18, 9.5), (SZ + 6, 9.5), (SZ + 6, 0)], 'plank', 11))
sside.rect(SZ, 9.6, SZ + 18, 10.6, 'frame'); sside.rect(SZ, 18.4, SZ + 18, 19, 'frame'); sside.rect(SZ, 27.4, SZ + 9, 28, 'frame')
for u in (SZ + 0.5, SZ + 8, SZ + 17): sside.rect(u, 0, u + 0.8, 19, 'frame')
sside.poly([(SZ + 1.3, 10.3), (SZ + 2.1, 10.3), (SZ + 8, 18), (SZ + 7.2, 18)], 'brace'); sside.rect(SZ + 4, 13, SZ + 6.5, 16, 'shutter'); sside.rect(SZ + 11, 13, SZ + 13.5, 16, 'win')
# low wooden annex against the right flank: shed roof, a door, a window, a stovepipe
ANX0, ANX1, ANZ = SU1 - 0.5, SU1 + 19, 32.0
annex = add(Face('front', ANZ, [(ANX0, 0), (ANX0, 9.5), (ANX1, 7.2), (ANX1, 0)], 'plank', 12))
annex.poly([(ANX0 - 0.5, 9.5), (ANX1 + 0.5, 7.2), (ANX1 + 0.5, 6.6), (ANX0 - 0.5, 8.9)], 'annexroof')
annex.rect(ANX0, 0, ANX0 + 0.8, 9.5, 'frame'); annex.rect(ANX1 - 0.8, 0, ANX1, 7.2, 'frame'); annex.rect(ANX0 + 9, 0, ANX0 + 9.8, 8.4, 'frame')
annex.rect(ANX0 + 3, 0, ANX0 + 6, 5.6, 'door'); annex.rect(ANX0 + 12, 3, ANX0 + 15, 5.4, 'winlit')
annex.rect(ANX0 + 16, 7.5, ANX0 + 16.8, 11.5, 'pipewall')
# the yard fence: chain-link with barbed wire, a gap at the gate path, one leaf swung open
FZ = 21.0
FENCE = [(-70, GATE0 - 1.5, FZ), (GATE1 + 1.5, 70, FZ)]
OPEN_LEAF = (GATE1 + 1.5, FZ, FZ + 4.5)          # (wx, z0, z1) a leaf standing open, swung into the yard

# ================================================================== rasterise
layer = Image.new('I', (W, H), 0); ld = ImageDraw.Draw(layer)
FACE_ID = {}
def fid(f):
    if id(f) not in FACE_ID: FACE_ID[id(f)] = (len(FACE_ID) + 1, f)
    return FACE_ID[id(f)][0]
for i, (wx, z, w, h) in enumerate(SKYLINE):
    (x0, y0), (x1, y1) = proj(wx - w / 2, h, z), proj(wx + w / 2, 0, z)
    ld.rectangle([x0, y0, x1, y1], fill=1000 + i)
for f in sorted(FACES, key=near_z, reverse=True):
    ld.polygon(f.polygon(), fill=fid(f))
lp = layer.load(); BY_ID = {v[0]: v[1] for v in FACE_ID.values()}

M = [[None] * W for _ in range(H)]; Z = [[None] * W for _ in range(H)]; UV = [[None] * W for _ in range(H)]
# ground: a rutted dirt track along the front (z 12.5..17.5), a trodden path from the track to the gate
GATE_MID = (GATE0 + GATE1) / 2
PATHS = [((GATE_MID, SZ), (GATE_MID + 2, 15.0), 5.0)]
def path_d(wx, wz):
    best = 9e9
    for (a, b, w) in PATHS:
        dx, dz = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dz * dz
        t = max(0.0, min(1.0, ((wx - a[0]) * dx + (wz - a[1]) * dz) / L2))
        best = min(best, math.hypot(wx - (a[0] + t * dx), wz - (a[1] + t * dz)) - w / 2)
    return best
# ground pipes: world polylines with a radius (cylinders lying on the yard)
PIPES = [([(62, 18.6), (48, 17.9), (36, 18.5), (26, 17.7), (16, 18.4), (6, 17.8), (-4, 18.6), (-12, 18.0), (-18, 19.2)], 0.28)]   # a rubber hose lying in loose waves along the fence line
# elevated district-heating pipelines (insulated, sheet-metal clad, on steel trestles, with expansion loops):
# (z, radius, path in face coords (wx, wy)); the right pair feeds the tower's riser, the left single run leaves frame
PZR = 24.0
ELEV = [(PZR, 0.8, [(66, 4.6), (46, 4.6), (46, 10.0), (36, 10.0), (36, 4.6), (SU1 - 1.8, 4.6), (SU1 - 1.8, 9.5)]),
        (PZR, 0.8, [(66, 6.7), (48.4, 6.7), (48.4, 12.4), (33.6, 12.4), (33.6, 6.7), (SU1 - 4.2, 6.7), (SU1 - 4.2, 8.6), (SU1 - 1.8, 8.6)]),
        (24.5, 0.7, [(-66, 4.2), (-36, 4.2), (-36, 7.6), (-30, 7.6), (-30, 4.2), (SU0 + 2.2, 4.2)])]
TRESTLES = [(PZR, 57, 3.8, 1.4), (PZR, 30, 3.8, 1.4), (PZR, 20, 3.8, 1.4), (24.5, -48, 3.5, 0), (24.5, -62, 3.5, 0)]   # (z, wx, height, strut offset to the upper pipe)
def pipe_at(wx, wz):
    best = None
    for (pts, r) in PIPES:
        for (a, b) in zip(pts, pts[1:]):
            dx, dz = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dz * dz
            t = max(0.0, min(1.0, ((wx - a[0]) * dx + (wz - a[1]) * dz) / L2))
            d = math.hypot(wx - (a[0] + t * dx), wz - (a[1] + t * dz))
            if d <= r and (best is None or d / r < best[0]): best = (d / r, r, (wx - (a[0] + t * dx)) * (dz) - (wz - (a[1] + t * dz)) * dx)
    return best
PUDDLES = [(-12, 14.0, 2.4, 0.8), (20, 18.5, 2.0, 0.7), (-30, 21, 1.6, 0.6), (8, 23.5, 1.5, 0.5), (36, 15.5, 1.8, 0.6)]
SCRAP = [(-20, 23.5, -14, 24.6), (SU1 + 3, 29.5, SU1 + 9, 30.8), (-50, 23.0, -40, 24.8), (-62, 22.4, -55, 23.6)]        # (wx0, z0, wx1, z1) footprints of junk piles
for y in range(H):
    for x in range(W):
        v = lp[x, y]
        if v >= 1000: M[y][x] = ('skyline', v); Z[y][x] = SKYLINE[v - 1000][1]; continue
        if v:
            f = BY_ID[v]; r = f.uvz(x, y) or (0.0, 0.0, near_z(f)); u, vv, z = r
            M[y][x] = (f.material_at(u, vv), f.obj); Z[y][x] = z; UV[y][x] = (u, vv, f); continue
        if y > HY:
            wx, wz = ground_at(x, y)
            pud = any(((wx - px_) / rx) ** 2 + ((wz - pz) / rz) ** 2 < 1 for (px_, pz, rx, rz) in PUDDLES)
            on_track = 12.3 < wz < 17.6
            d = path_d(wx, wz)
            if pud: M[y][x] = ('puddle', 0)
            elif on_track: M[y][x] = ('track', 0)
            elif d < 0.3 * math.sin(wx * 2.7 + wz * 3.1): M[y][x] = ('path', 0)
            else: M[y][x] = ('dirt', 0)
            Z[y][x] = wz; UV[y][x] = (wx, wz, None)
        else: M[y][x] = ('sky', 0)
# ground pipes (after the ground, before the fence) — raise them a little above the ground plane
for y in range(HY + 1, H):
    for x in range(W):
        if M[y][x][0] not in ('dirt', 'track', 'path', 'puddle'): continue
        wx, wz = ground_at(x, y)
        # a lying cylinder sits ON the ground: sample the ground point slightly behind so the pipe's top shows above its footprint
        hit = pipe_at(wx, wz) or pipe_at(wx, wz + 0.75 * wz / 26)      # the cylinder's top shows above its footprint
        if hit:
            M[y][x] = ('pipe', 0); Z[y][x] = wz; UV[y][x] = (hit[0], hit[1], hit[2])
def put_poly(pts, key, obj, z):
    tmp = Image.new('1', (W, H), 0); ImageDraw.Draw(tmp).polygon(pts, fill=1); tp = tmp.load()
    for y in range(H):
        for x in range(W):
            if tp[x, y]: M[y][x] = (key, obj); Z[y][x] = z
def put_rect(x0, y0, x1, y1, key, obj, z):
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            if 0 <= x < W and 0 <= y < H: M[y][x] = (key, obj); Z[y][x] = z
# scrap piles: heaps of planks and junk (screen-space polygons at their footprint depth)
random.seed(21)
for (x0, z0, x1, z1) in SCRAP:
    (sx0, sy0) = proj(x0, 0, z1); (sx1, sy1) = proj(x1, 0, z0); zc = (z0 + z1) / 2
    hgt = (sy1 - sy0) * 2.2 + 18
    pts = [(sx0, sy1)]
    n = 9
    for i in range(1, n):
        t = i / n; pts.append((sx0 + (sx1 - sx0) * t, sy1 - hgt * math.sin(math.pi * t) * random.uniform(0.6, 1.0)))
    pts.append((sx1, sy1))
    put_poly(pts, 'scrap', int(x0 * 10), zc)
    for k in range(5):                                                                        # planks sticking out
        px0 = sx0 + (sx1 - sx0) * random.uniform(0.1, 0.9); py0 = sy1 - hgt * random.uniform(0.3, 0.8)
        ang = random.uniform(-1.2, -0.3); ln = random.uniform(16, 34)
        put_poly([(px0, py0), (px0 + ln * math.cos(ang), py0 + ln * math.sin(ang)), (px0 + ln * math.cos(ang) + 3, py0 + ln * math.sin(ang) + 1), (px0 + 3, py0 + 1)], 'plankout', k, zc - 0.5)
# barrels by the annex and the gate
for (bx, bz, hh) in ((SU1 + 11, 30.5, 2.6), (SU1 + 13.2, 30.2, 2.6), (GATE1 + 5, 25.2, 2.4), (-36, 23.2, 2.4), (-33.8, 23.0, 2.4)):
    (x0, yb) = proj(bx - 1.0, 0, bz); (x1, yt) = proj(bx + 1.0, hh, bz)
    put_rect(x0, yt, x1, yb, 'barrel', int(bx * 10), bz)
# elevated pipelines + trestles: overlay in face space (z=const planes), rounded corners come free from the distance test
def pipe_dist(path, u, v):
    best = None; acc = 0.0
    for (a, b) in zip(path, path[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy)
        t = max(0.0, min(1.0, ((u - a[0]) * dx + (v - a[1]) * dy) / (L * L)))
        qx, qy = a[0] + t * dx, a[1] + t * dy; d = math.hypot(u - qx, v - qy)
        if best is None or d < best[0]: best = (d, acc + t * L, u - qx, v - qy)
        acc += L
    return best
for (pz, pr, path) in ELEV:
    us = [p[0] for p in path]; vs = [p[1] for p in path]
    (x0, y1) = proj(min(us) - pr, min(vs) - pr, pz); (x1, y0) = proj(max(us) + pr, max(vs) + pr, pz)
    for y in range(max(0, int(y0)), min(H, int(y1) + 2)):
        for x in range(max(0, int(x0)), min(W, int(x1) + 2)):
            u, v = (x - CX) * pz / F, CAMH - (y - HY) * pz / F
            d, along, du, dv = pipe_dist(path, u, v)
            if d <= pr: M[y][x] = ('hpipe', int(pz * 10)); Z[y][x] = pz; UV[y][x] = (d, pr, along, du, dv, pz)
for (tz, tu, th, strut) in TRESTLES:
    (x0, yb) = proj(tu - 0.28, 0, tz); (x1, yt) = proj(tu + 0.28, th, tz)
    for y in range(int(yt), int(yb) + 1):
        for x in range(int(x0), int(x1) + 1):
            if 0 <= x < W and 0 <= y < H and M[y][x][0] != 'hpipe': M[y][x] = ('trestle', 0); Z[y][x] = tz
    (cx0, cy0) = proj(tu - 1.3, th, tz); (cx1, cy1) = proj(tu + 1.3, th + 0.35, tz)                      # crossbeam under the pipes
    for y in range(int(cy1), int(cy0) + 1):
        for x in range(int(cx0), int(cx1) + 1):
            if 0 <= x < W and 0 <= y < H and M[y][x][0] != 'hpipe': M[y][x] = ('trestle', 0); Z[y][x] = tz
    if strut:
        (sx0, sy0) = proj(tu + strut - 0.14, th, tz); (sx1, sy1) = proj(tu + strut + 0.14, th + 2.1, tz)
        for y in range(int(sy1), int(sy0) + 1):
            for x in range(int(sx0), int(sx1) + 1):
                if 0 <= x < W and 0 <= y < H and M[y][x][0] != 'hpipe': M[y][x] = ('trestle', 0); Z[y][x] = tz
# utility pole with a crossarm, right of the yard; cables to the tower top and off to the right edge
PX, PZ = 30.0, 20.0
(px0, pyb) = proj(PX - 0.35, 0, PZ); (px1, pyt) = proj(PX + 0.35, 24, PZ)
put_rect(px0, pyt, px1, pyb, 'pole', 0, PZ)
(ax0, ay0) = proj(PX - 2.2, 22.6, PZ); (ax1, ay1) = proj(PX + 2.2, 23.2, PZ); put_rect(ax0, ay0, ax1, ay1, 'pole', 1, PZ)
def cable(p0, p1, sag, n=40, z=30):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(proj(p0[0] + (p1[0] - p0[0]) * t, p0[2] + (p1[2] - p0[2]) * t - sag * math.sin(math.pi * t), p0[1] + (p1[1] - p0[1]) * t))
    for (a, b) in zip(pts, pts[1:]):
        n2 = int(math.hypot(b[0] - a[0], b[1] - a[1])) + 1
        for j in range(n2 + 1):
            x, y = int(a[0] + (b[0] - a[0]) * j / n2), int(a[1] + (b[1] - a[1]) * j / n2)
            if 0 <= x < W and 0 <= y < H and M[y][x][0] in ('sky', 'skyline', 'plaster', 'win', 'winlit', 'cornice', 'moss'): M[y][x] = ('cable', 0); Z[y][x] = z
cable((PX - 2.0, PZ, 22.8), (SU1 - 7, SZ, 35.2), 1.6); cable((PX + 2.0, PZ, 22.8), (90, 14, 20), 3.0)
cable((PX - 1.4, PZ, 23.0), (SU0 + 6.5, SZ, 35.1), 2.2)
(mx0, my0) = proj(SU1 - 8.7, 41, SZ); (mx1, my1) = proj(SU0 + 7, 35.1, SZ)
for j in range(0, 60):
    t = j / 59; x, y = int(mx0 + (mx1 - mx0) * t), int(my0 + (my1 - my0) * t + 10 * math.sin(math.pi * t))
    if 0 <= x < W and 0 <= y < H and M[y][x][0] == 'sky': M[y][x] = ('cable', 0); Z[y][x] = SZ
# a thin plume from the tower's pipe top
(sx_, sy_) = proj(SU1 - 2.8, 32.6, SZ)
random.seed(4)
for j in range(70):
    t = j / 70; x = int(sx_ + 18 * t + 6 * math.sin(t * 9)); y = int(sy_ - t * 120)
    for dx in range(-int(2 + 7 * t), int(2 + 7 * t) + 1):
        if 0 <= x + dx < W and 0 <= y < H and M[y][x + dx][0] == 'sky' and h32(x + dx, y, 2) % (2 + int(t * 4)) == 0: M[y][x + dx] = ('smoke', int(t * 10)); Z[y][x + dx] = SZ
def branch(x, y, ang, ln, wdt, depth):
    if depth > 4 or ln < 3: return
    x2, y2 = x + ln * math.cos(ang), y - ln * math.sin(ang); n = int(ln) + 1
    for j in range(n + 1):
        px_, py_ = int(x + (x2 - x) * j / n), int(y + (y2 - y) * j / n)
        for k in range(max(1, int(wdt))):
            if 0 <= px_ + k < W and 0 <= py_ < H: M[py_][px_ + k] = ('weed', 0); Z[py_][px_ + k] = 12
    branch(x2, y2, ang + random.uniform(0.3, 0.8), ln * 0.68, wdt * 0.7, depth + 1)
    branch(x2, y2, ang - random.uniform(0.3, 0.8), ln * 0.66, wdt * 0.7, depth + 1)
random.seed(77)
for (wx_, wy_, ln) in ((40, 600, 40), (120, 604, 26), (1010, 602, 44), (950, 606, 26), (700, 606, 18), (300, 604, 16)):
    branch(wx_, wy_, math.radians(90 + random.uniform(-12, 12)), ln, 3, 0)
TEXT = set()
for (txt, cx_, ty, sc) in [SIGN_SHED]:
    w = text_width(txt, sc); draw_text(lambda x, y: TEXT.add((x, y)), txt, cx_ - w // 2, ty, sc)

# ================================================================== shading
px = [[None] * W for _ in range(H)]
def setc(x, y, c): px[y][x] = c
def ramp_i(k, i):
    r = RAMPS[k]; return r[max(0, min(len(r) - 1, int(i)))]
def face_light(face, v): return (-1 if face.kind == 'side' else 0) + 0.5 * (v / 30.0)
for y in range(H):
    for x in range(W):
        k, obj = M[y][x]; z = Z[y][x]
        if k == 'sky':
            t = y / HY
            v = 1.0 + 4.6 * t ** 1.4 + (nA(x * 0.55, y * 2.6) - 0.5) * 1.8 + (nB(x * 0.5, y * 2.4) - 0.5) * 0.6
            v += 0.9 * math.exp(-(((x - 760) / 260) ** 2 + ((y - 80) / 90) ** 2))
            setc(x, y, ramp_i('K', band(v, x, y))); continue
        if k == 'smoke': setc(x, y, HAZE[5] if obj < 5 else HAZE[4]); continue
        if k == 'skyline':
            c = HAZE[1] if h32(obj, 3) % 3 else HAZE[2]
            if h32(x // 2, y // 3, 4) % 37 == 0 and y < HY - 3 and x % 2 and y % 3 == 1: c = GLOW[1]
            setc(x, y, fogged(c, fog_of(z) * 0.6, x, y)); continue
        if k == 'cable': setc(x, y, fogged(STONE[0], fog_of(z), x, y)); continue
        if k == 'weed': setc(x, y, STONE[0] if (x + y) % 5 else STONE[1]); continue
        if k == 'pole': setc(x, y, fogged(ramp_i('D', 2 if (x + y) % 7 else 1), fog_of(z), x, y)); continue
        if k == 'scrap':
            i = 1.6 + (nB(x * 2, y * 2) - 0.5) * 2.2 + (0.8 if (x // 3 + y // 2) % 5 == 0 else 0)
            c = ramp_i('D', band(i, x, y)) if h32(x // 4, y // 3, 6) % 4 else ramp_i('W', 1 + h32(x // 4, y // 3, 7) % 3)
            setc(x, y, fogged(c, fog_of(z), x, y)); continue
        if k == 'plankout': setc(x, y, fogged(ramp_i('D', 3 if (x + y) % 6 else 2), fog_of(z), x, y)); continue
        if k == 'barrel':
            (bx, bz) = next(((b[0], b[1]) for b in ((SU1 + 11, 30.5), (SU1 + 13.2, 30.2), (GATE1 + 5, 25.2), (-36, 23.2), (-33.8, 23.0)) if int(b[0] * 10) == obj), (0, z))
            (cx_, _) = proj(bx, 0, bz); rw = 1.0 * F / bz; dx = (x - cx_) / rw
            i = 2.2 - abs(dx) * 1.8 + (0.5 if dx < -0.2 else 0)
            if (y % 9) in (3, 4): i = 0.5
            setc(x, y, fogged(ramp_i('W', band(i, x, y)), fog_of(z), x, y)); continue
        if k == 'pipe':
            dn, r, side = UV[y][x][0], UV[y][x][1], UV[y][x][2]
            i = 2.4 - 1.8 * dn * dn + (0.4 if side > 0 else 0)
            setc(x, y, fogged(ramp_i('T', band(i, x, y)), fog_of(z), x, y)); continue
        if k == 'hpipe':
            d, r, along, du, dv, fz = UV[y][x]
            dn = d / r; lam = (-du * 0.35 + dv * 0.9) / r
            i = 2.6 + 1.9 * lam - 1.3 * dn * dn + (nC(x, y) - 0.5) * 0.4
            seam = along % 1.5
            if seam < 0.11: i -= 2.2                                                                  # segment joints of the cladding
            elif seam < 0.2: i += 0.6
            rust = nA(x * 1.7 + 11, y * 1.7) > 0.56 or (seam < 0.5 and dv < 0 and h32(int(along * 4), 3) % 3 == 0)
            if rust and seam >= 0.11: c = WARM[max(0, min(5, int(1.6 + lam * 1.4 - dn * 1.2)))]
            else: c = ramp_i('E', band(i, x, y))
            setc(x, y, fogged(c, fog_of(fz), x, y)); continue
        if k == 'trestle': setc(x, y, fogged(ramp_i('T', 3 if (x % 4) else 2), fog_of(z), x, y)); continue
        if k in ('dirt', 'track', 'path', 'puddle'):
            wx, wz, _ = UV[y][x]
            if k == 'puddle':
                c = SKY[3] if (x + y) % 2 else STONE[2]
                if h32(x, y, 5) % 23 == 0: c = SKY[4]
            elif k == 'track':
                v = 2.4 + (nB(x, y) - 0.5) * 1.4 + (nC(x, y) - 0.5) * 0.6 - 0.5 * max(0.0, (y - 500) / 100)
                for rz in (13.6, 16.2):                                                              # cart ruts
                    if abs(wz - rz) < 0.25: v -= 1.2
                    elif abs(wz - rz) < 0.5: v += 0.4
                c = ramp_i('T', band(v, x, y))
                if h32(x, y, 9) % 120 == 0: c = STONE[5]
            elif k == 'path':
                v = 3.0 + (nB(x, y) - 0.5) * 1.2 + (nC(x, y) - 0.5) * 0.5
                c = ramp_i('T', band(v, x, y))
            else:
                v = 2.3 + (nB(x, y) - 0.5) * 1.5 + (nC(x, y) - 0.5) * 0.7 - 0.5 * max(0.0, (y - 500) / 100)
                c = ramp_i('T', band(v, x, y))
                if h32(x, y, 9) % 97 == 0 and wz < 60: c = STONE[5]
                if h32(x // 2, y // 2, 10) % 53 == 0 and wz < 40: c = STONE[1]
                if nA(x * 1.4, y * 1.4) > 0.64 and wz < 70 and (x + y) % 2: c = ramp_i('K', 3)        # moss / weeds patches
            setc(x, y, fogged(c, fog_of(wz), x, y)); continue
        u, v, face = UV[y][x]; f = fog_of(z); fl = face_light(face, v)
        if k == 'plaster':
            i = 3 + fl + (nA(x * 2, y * 2) - 0.5) * 1.2
            if (v % 5) < 0.12 * z / 30: i -= 1
            c = ramp_i('T', band(i, x, y))
        elif k == 'cornice': c = ramp_i('T', 6 if (v * 20) % 7 > 1 else 4)
        elif k == 'win': c = ramp_i('T', 0 if ((u * 10) % 11 > 1 and (v * 10) % 13 > 1) else 1)
        elif k == 'winlit':
            c = GLOW[0] if ((u * 10) % 11 > 1 and (v * 10) % 13 > 1) else STONE[1]
            if h32(x // 2, y // 2, 2) % 7 == 0: c = GLOW[1]
            f *= 0.45
        elif k == 'plank':
            pw = 0.9; pl = math.floor(u / pw); fu = u / pw - pl
            i = 3.2 + fl + (h32(pl, obj, 1) % 3) * 0.35 - 0.6 * (nA(x * 1.5, y) - 0.5)
            if fu < 0.14 * z / 36: i -= 1.6
            if h32(pl, int(v * 2.3), 2) % 19 == 0: i -= 0.9
            i -= 0.9 * max(0.0, 1 - v / 3.5)
            c = ramp_i('D', band(i, x, y))
        elif k == 'frame': c = ramp_i('D', 1 if ((x + y) % 9) else 0)
        elif k == 'brace': c = ramp_i('D', 1.5 if (x % 7) else 0.5)
        elif k == 'under': c = ramp_i('D', 0)
        elif k == 'bracket': c = ramp_i('T', 2 if (x % 5) else 1)
        elif k == 'gate':
            pl = math.floor((u - GATE0) / 1.3); fu = (u - GATE0) / 1.3 - pl
            i = 1.2 + (h32(pl, 1) % 2) * 0.5 - (1.0 if fu < 0.12 else 0) - 0.8 * max(0.0, 1 - v / 3)
            if abs(u - GATE_MID) < 0.12: i = 0
            if abs(v - 3) < 0.25 or abs(v - 6.2) < 0.25: i = 0.3
            c = ramp_i('D', band(i, x, y))
        elif k == 'shutter': c = ramp_i('D', 2 if (v * 4) % 2 < 1 else 1)
        elif k == 'glyph':
            c = ramp_i('T', 4 if ((x + y) % 5) else 3)
            gu, gv = (u - (SU0 + 19)) * 3, (v - 12) * 3
            if (int(gu) % 4 in (1, 2)) and (int(gv) % 4 in (1, 2)) and h32(int(gu) // 4, int(gv) // 4, 5) % 3: c = GLOW[1]
        elif k == 'plate': c = ramp_i('T', 5 if ((x + y) % 7) else 4)
        elif k == 'moss': c = ramp_i('K', 3) if ((x + y) % 3) else ramp_i('T', 4)
        elif k == 'lamp2': c = GLOW[2] if (x + y) % 2 else STONE[1]
        elif k == 'annexroof': c = ramp_i('D', 2 if (y % 3) else 1)
        elif k == 'door': c = ramp_i('D', 1 if (u * 7) % 3 > 0.4 else 0)
        elif k == 'pipewall':
            dn = ((u - (SU1 - 1.8)) / 0.8) if face.obj == 10 else ((u - (ANX0 + 16.4)) / 0.4)
            i = 2.6 - 1.9 * dn * 0.6 - 1.3 * dn * dn + (nC(x, y) - 0.5) * 0.4
            seam = v % 1.5
            if seam < 0.11: i -= 2.2
            elif seam < 0.2: i += 0.6
            if nA(x * 1.7 + 11, y * 1.7) > 0.56 and seam >= 0.11: c = WARM[max(0, min(5, int(1.8 - dn * 1.2)))]
            else: c = ramp_i('E', band(i, x, y))
        else: c = STONE[3]
        setc(x, y, fogged(c, f, x, y))
for (x, y) in TEXT:
    if 0 <= x < W and 0 <= y < H and M[y][x][0] == 'plate': setc(x, y, GLOW[1] if (x + y) % 9 else GLOW[0])
# chain-link fence overlay with barbed wire + the open leaf standing into the yard
def fence_span(u0, u1, z, kind='front'):
    if kind == 'front':
        (x0, yb) = proj(u0, 0, z); (x1, yt) = proj(u1, 3.6, z)
    x0, x1, yb, yt = int(x0), int(x1), int(yb), int(yt)
    for y in range(yt, yb + 1):
        for x in range(x0, x1 + 1):
            if not (0 <= x < W and 0 <= y < H): continue
            if (x + y) % 9 == 0 or (x - y) % 9 == 0: setc(x, y, fogged(STONE[1], fog_of(z), x, y))
    for u in [u0 + i * 2.6 for i in range(int((u1 - u0) / 2.6) + 1)] + [u1]:
        (xp, _) = proj(u, 0, z)
        for y in range(yt - 4, yb + 1):
            for dx in (-1, 0, 1):
                if 0 <= int(xp) + dx < W and 0 <= y < H: setc(int(xp) + dx, y, STONE[1 if dx else 2])
    for x in range(x0, x1 + 1):
        if 0 <= x < W:
            setc(x, yt, STONE[2]); setc(x, yt - 3 + (1 if (x // 3) % 2 else 0), STONE[1])
            if x % 6 == 0: setc(x, yt - 4, STONE[2])
for (u0, u1, z) in FENCE: fence_span(u0, u1, z)
# the open leaf: a 'side'-oriented panel at wx=OPEN_LEAF[0] from z0 to z1 (swung open into the yard)
(lx, z0, z1) = OPEN_LEAF
pts = [proj(lx, 0, z0), proj(lx, 3.6, z0), proj(lx, 3.6, z1), proj(lx, 0, z1)]
tmp = Image.new('1', (W, H), 0); ImageDraw.Draw(tmp).polygon(pts, fill=1); tp = tmp.load()
for y in range(H):
    for x in range(W):
        if tp[x, y] and ((x + y) % 7 == 0 or (x - y) % 7 == 0): setc(x, y, STONE[1])
for (a, b) in ((pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[3]), (pts[3], pts[0])):
    n = int(math.hypot(b[0] - a[0], b[1] - a[1])) + 1
    for j in range(n + 1):
        x, y = int(a[0] + (b[0] - a[0]) * j / n), int(a[1] + (b[1] - a[1]) * j / n)
        if 0 <= x < W and 0 <= y < H: setc(x, y, STONE[2])

# ================================================================== outlines
RANK = {'sky': 0, 'skyline': 0, 'cable': 0, 'smoke': 0, 'dirt': 1, 'track': 1, 'path': 1, 'puddle': 1, 'weed': 4, 'pole': 3, 'pipe': 2, 'scrap': 2, 'plankout': 3, 'barrel': 2, 'hpipe': 3, 'trestle': 2}
SOFT_PAIRS = [('sky', 'skyline'), ('dirt', 'track'), ('dirt', 'path'), ('track', 'path'), ('dirt', 'puddle'), ('track', 'puddle'), ('path', 'puddle'), ('sky', 'cable'), ('skyline', 'cable'), ('sky', 'smoke'), ('smoke', 'cable'),
              ('plaster', 'cable'), ('plaster', 'cornice'), ('win', 'plaster'), ('winlit', 'plaster'), ('win', 'cable'), ('winlit', 'cable'), ('moss', 'cable'),
              ('plank', 'frame'), ('plank', 'brace'), ('plank', 'under'), ('frame', 'under'), ('frame', 'brace'), ('plank', 'moss'), ('frame', 'moss'), ('under', 'moss'),
              ('plank', 'shutter'), ('plank', 'glyph'), ('plate', 'frame'), ('plank', 'lamp2'), ('plank', 'annexroof'), ('frame', 'annexroof'), ('plank', 'door'), ('plank', 'win'), ('plank', 'winlit'),
              ('plank', 'bracket'), ('pipewall', 'bracket'), ('frame', 'bracket'), ('scrap', 'plankout'), ('gate', 'frame'), ('hpipe', 'pipewall'), ('trestle', 'hpipe')]
SOFT = {frozenset(p) for p in SOFT_PAIRS}
def rank(k): return RANK.get(k, 2)
for y in range(H):
    for x in range(W):
        a = M[y][x]
        for nx_, ny_ in ((x + 1, y), (x, y + 1)):
            if nx_ >= W or ny_ >= H: continue
            b = M[ny_][nx_]
            if a == b: continue
            ka, kb = a[0], b[0]
            if frozenset((ka, kb)) in SOFT or (ka == kb and ka in ('dirt', 'track', 'skyline', 'weed', 'cable', 'smoke', 'scrap', 'pipe', 'hpipe')): continue
            ra, rb = rank(ka), rank(kb)
            if ra != rb: tx, ty = (x, y) if ra < rb else (nx_, ny_)
            else: tx, ty = (x, y) if str(a) > str(b) else (nx_, ny_)
            if (tx, ty) in TEXT: continue
            z = Z[ty][tx] or 300
            if z < 48: px[ty][tx] = INK
            elif z < 110: px[ty][tx] = fogged(STONE[0], fog_of(z) * 0.7, tx, ty)
img = Image.new('RGB', (W, H)); ip = img.load()
for y in range(H):
    for x in range(W): ip[x, y] = px[y][x]
img.save(f'{OUT}/bg.png')
print('done')
