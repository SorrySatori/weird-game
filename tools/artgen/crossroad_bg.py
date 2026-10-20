"""Crossroad background v3 — overcast day, one-point perspective. Changes vs v2: SHED 521 is the ramshackle wooden tower
from Shed521.png (stacked overhanging storeys, timber braces, sign plate high up, cupola, fence), VOXMARKET is a row of
zeppelin-hangar market halls with huge glazed arches (Riga Central Market). The corpse is a separate sprite."""
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
    """vertical building face: 'front' (z=const, u=wx, v=wy) or 'side' (x=const, u=wz, v=wy); outline = list of (u,v)"""
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
    def disc(self, cu, cv, r, kind, obj=None, top_only=False): self.feats.append(('d', (cu, cv, r, top_only), kind, self.obj if obj is None else obj))
    def material_at(self, u, v):
        mat = self.mat
        for (t, g, kind, obj) in self.feats:
            if t == 'r':
                if g[0] <= u < g[2] and g[1] <= v < g[3]: mat = kind
            elif t == 'p':
                if pip(g, u, v): mat = kind
            else:
                cu, cv, r, top_only = g
                if (u - cu) ** 2 + (v - cv) ** 2 <= r * r and (not top_only or v >= cv): mat = kind
        return mat
FACES = []
def add(f): FACES.append(f); return f
def box(u0, u1, h): return [(u0, 0), (u0, h), (u1, h), (u1, 0)]
def arch_outline(u0, u1, shoulder, cu, r, n=28):
    pts = [(u0, 0), (u0, shoulder)]
    for i in range(n + 1):
        a = math.pi - math.pi * i / n
        pts.append((cu + r * math.cos(a), shoulder + r * math.sin(a)))
    pts += [(u1, shoulder), (u1, 0)]
    return pts

# --- far skyline
rnd = random.Random(31)
SKYLINE = []
for i in range(60):
    wx = -150 + i * 5 + rnd.uniform(-2, 2); z = rnd.choice((150, 180, 210, 250)); w = rnd.uniform(3, 9); h = rnd.uniform(14, 40)
    SKYLINE.append((wx, z, w, h))
SKYLINE += [(9, 200, 5, 78), (9.5, 200, 2, 94), (-26, 230, 6, 60), (40, 240, 7, 52)]

# --- left tenements beyond the shed (side faces at wx=-28)
def tenement(X, z0, z1, h, obj, lit):
    f = add(Face('side', X, box(z0, z1, h), 'plaster', obj))
    for fl in range(1, int(h / 5) + 1):
        v0 = fl * 5 - 3.2
        for u in [z0 + 1.5 + i * 3.0 for i in range(int((z1 - z0 - 1.5) / 3.0))]:
            f.rect(u, v0, u + 1.3, v0 + 2.1, 'winlit' if h32(obj, fl, int(u * 10)) % lit == 0 else 'win')
    f.rect(z0, h - 0.6, z1, h, 'cornice')
    return f
tenement(-28, 61, 92, 23, 40, 4); tenement(-28, 92, 130, 18, 41, 3)
add(Face('front', 92, box(-31, -29.5, 27), 'plaster', 44))

# ================================================================== SHED 521 — a top-heavy wooden tower (front face z=36)
SZ = 36.0
SU0, SU1 = -62.0, -28.0            # ground storey span (screen x ~17..300)
# outline: storeys step OUT as they go up (overhangs), narrower cupola on top
SH_OUT = [(SU0, 0), (SU0, 11), (SU0 - 1.5, 11), (SU0 - 1.5, 21), (SU0 - 3, 21), (SU0 - 3, 31), (SU0 + 6, 31), (SU0 + 6, 38.5), (SU1 - 6, 38.5), (SU1 - 6, 31), (SU1 + 1.5, 31), (SU1 + 1.5, 21), (SU1 + 0.5, 21), (SU1 + 0.5, 11), (SU1, 11), (SU1, 0)]
shed = add(Face('front', SZ, SH_OUT, 'plank', 10))
# storey separations: beam + shadow under each overhang
for (v, a, b) in ((11, SU0 - 1.5, SU1 + 0.5), (21, SU0 - 3, SU1 + 1.5), (31, SU0 + 6, SU1 - 6)):
    shed.rect(a, v - 0.4, b, v + 0.6, 'frame'); shed.rect(a, v - 1.6, b, v - 0.4, 'under')
# corner posts per storey + diagonal braces
for (v0, v1, a, b) in ((0, 11, SU0, SU1), (11, 21, SU0 - 1.5, SU1 + 0.5), (21, 31, SU0 - 3, SU1 + 1.5), (31, 38.5, SU0 + 6, SU1 - 6)):
    shed.rect(a, v0, a + 1.0, v1, 'frame'); shed.rect(b - 1.0, v0, b, v1, 'frame')
    mid = (a + b) / 2
    if v0 < 31:
        shed.rect(mid - 0.5, v0, mid + 0.5, v1, 'frame')
        for (p, q) in ((a + 1, mid - 0.5), (mid + 0.5, b - 1)):
            shed.poly([(p, v0 + 0.3), (p + 0.9, v0 + 0.3), (q, v1 - 0.6), (q - 0.9, v1 - 0.6)], 'brace')
            shed.poly([(q, v0 + 0.3), (q - 0.9, v0 + 0.3), (p, v1 - 0.6), (p + 0.9, v1 - 0.6)], 'brace')
# the big gateway (dark, plank doors), a lamp beside it
shed.rect(SU0 + 9, 0, SU0 + 24, 9, 'gate'); shed.rect(SU0 + 8.4, 8.9, SU0 + 24.6, 9.8, 'frame')
shed.rect(SU0 + 8.4, 0, SU0 + 9, 9.8, 'frame'); shed.rect(SU0 + 24, 0, SU0 + 24.6, 9.8, 'frame')
shed.rect(SU0 + 26, 5.5, SU0 + 27, 7.5, 'lamp2')
# shuttered windows, the glyph plate, the big sign plate, the cupola hatch
shed.rect(SU0 + 4, 14, SU0 + 7, 17.5, 'shutter'); shed.rect(SU1 - 7, 14, SU1 - 4, 17.5, 'shutter'); shed.rect(SU0 + 14, 24, SU0 + 17, 27, 'shutter')
shed.rect(SU0 + 20, 13.5, SU0 + 28, 17.5, 'glyph')
shed.rect(SU0 + 4.5, 23.5, SU1 - 4.5, 29, 'plate'); shed.rect(SU0 + 4.0, 23.2, SU1 - 4.0, 23.8, 'frame'); shed.rect(SU0 + 4.0, 28.8, SU1 - 4.0, 29.4, 'frame')
shed.rect(SU0 + 14, 33, SU0 + 20, 36.5, 'win')
# railing round the top deck + a mast with a chain
for u in [SU0 - 3 + i * 1.6 for i in range(int((SU1 + 1.5 - (SU0 - 3)) / 1.6) + 1)]:
    shed.rect(u, 31, u + 0.35, 32.6, 'frame')
shed.rect(SU0 - 3, 32.4, SU1 + 1.5, 32.9, 'frame')
shed.rect(SU0 + 6, 38.5, SU1 - 6, 39.2, 'frame'); shed.rect(SU1 - 9, 38.5, SU1 - 8.4, 44, 'frame')
# moss hanging off the beams
rnd = random.Random(9)
for (v, a, b) in ((11, SU0 - 1.5, SU1 + 0.5), (21, SU0 - 3, SU1 + 1.5), (31, SU0 + 6, SU1 - 6)):
    u = a + 1
    while u < b - 1:
        over_plate = (v == 31 and SU0 + 3.5 < u < SU1 - 3.5)
        if rnd.random() < 0.55 and not over_plate: shed.rect(u, v - 1.6 - rnd.uniform(0.6, 2.4), u + rnd.uniform(0.5, 1.4), v - 0.4, 'moss')
        u += rnd.uniform(1.0, 2.6)
SIGN_SHED = ('SHED 521', *[int(c) for c in proj((SU0 + SU1) / 2 - 0.1, 28.0, SZ)], 3)
# side face along the street (wx=-28): planks, a lean-to roof, braces
sside = add(Face('side', -28.0, [(SZ, 0), (SZ, 38.5), (SZ + 2, 38.5), (SZ + 2, 31), (SZ + 10, 31), (SZ + 10, 21), (SZ + 24, 21), (SZ + 24, 0)], 'plank', 11))
sside.rect(SZ, 10.6, SZ + 24, 11.6, 'frame'); sside.rect(SZ, 20.4, SZ + 24, 21, 'frame'); sside.rect(SZ, 30.4, SZ + 10, 31, 'frame')
sside.poly([(SZ + 12, 12), (SZ + 24, 12), (SZ + 24, 14.5), (SZ + 12, 16.5)], 'leanto')
for u in (SZ + 0.5, SZ + 8, SZ + 16, SZ + 23):
    sside.rect(u, 0, u + 0.8, 21, 'frame')
sside.poly([(SZ + 1.3, 0.3), (SZ + 2.1, 0.3), (SZ + 8, 10), (SZ + 7.2, 10)], 'brace'); sside.poly([(SZ + 8.8, 0.3), (SZ + 9.6, 0.3), (SZ + 16, 10), (SZ + 15.2, 10)], 'brace')
sside.rect(SZ + 17, 0, SZ + 20, 7, 'door'); sside.rect(SZ + 4, 14, SZ + 6.5, 17, 'shutter')
# chain-link fence flanking the gate path (overlay, z=33)
FENCE = [(SU0 - 4, SU0 + 7, 33.0), (SU0 + 26.5, SU1 + 4, 33.0)]

# ================================================================== VOXMARKET — zeppelin hangars (Riga Central Market)
def hangar(z, u0, u1, shoulder, cu, r, obj, with_front=True):
    apex = shoulder + r
    if with_front:
        f = add(Face('front', z, arch_outline(u0, u1, shoulder, cu, r), 'stucco', obj))
        f.rect(u0, shoulder - 1.3, u1, shoulder, 'cornice2')                                   # impost band
        f.disc(cu, shoulder, r - 1.6, 'fanlight', top_only=True)                               # the great glazed arch
        f.rect(cu - r + 1.6, shoulder - 1.3, cu + r - 1.6, shoulder, 'cornice2')
        f.rect(u0 + 0.6, 0, u0 + 2.0, shoulder + 0.8, 'pilaster2'); f.rect(u1 - 2.0, 0, u1 - 0.6, shoulder + 0.8, 'pilaster2')
        for ou in (cu - r - 0.2, cu + r - 1.4):
            f.rect(ou, 0, ou + 1.6, shoulder + 0.8, 'pilaster2')
        f.poly([(cu - 1.2, apex - 2.2), (cu + 1.2, apex - 2.2), (cu + 0.8, apex + 0.6), (cu - 0.8, apex + 0.6)], 'keystone')
        return f
hv1 = hangar(28.0, 20.0, 50.0, 14.0, 35.0, 14.5, 20)
# hall 1 lower facade: the hangar's sliding doors — tall steel leaves on a ground rail under a guide girder; the
# middle leaves have been rolled aside (stacked 4+4 at the ends, one even out past the corner) so the market shows through
DOOR_TOP, LEAF_W, D0, D1 = 12.4, 2.48, 22.6, 47.4
hv1.rect(D0, 0, D1, DOOR_TOP, 'opening')
LEAVES = [D0 + i * 2.0 for i in range(4)] + [D1 - LEAF_W - i * 2.0 for i in range(4)]
for lu in LEAVES: hv1.rect(lu, 0, lu + LEAF_W, DOOR_TOP, 'leaf')
OPEN_U0, OPEN_U1 = LEAVES[3] + LEAF_W, LEAVES[7]
hv1.rect(D0 - 0.4, DOOR_TOP, D1 + 0.4, DOOR_TOP + 1.0, 'girder')
hv1.rect(D0 - 0.4, 0, D1 + 0.4, 0.35, 'rail')
hv1.rect(27.0, DOOR_TOP - 0.2, 43.0, DOOR_TOP + 2.4, 'board'); hv1.rect(26.7, DOOR_TOP - 0.5, 43.3, DOOR_TOP - 0.1, 'cornice2'); hv1.rect(26.7, DOOR_TOP + 2.3, 43.3, DOOR_TOP + 2.7, 'cornice2')
SIGN_VOX = ('VOXMARKET', *[int(c) for c in proj(35.0, DOOR_TOP + 1.25, 28.0)], 3)
hv1.rect(20, 0, D0 - 0.4, 1.0, 'plinth'); hv1.rect(D1 + 0.4, 0, 50, 1.0, 'plinth')
RAILS = []          # (the leaf rolled out past the corner + its outside rails were dropped: it read as a stray panel)
# hall 1 flank along the street (wx=20): stucco wall, tall arched windows, barrel roof in sheet metal
hs1 = add(Face('side', 20.0, box(28.0, 56.0, 31.0), 'stucco', 21))
hs1.rect(28.0, 24.6, 56.0, 31.0, 'roofmetal'); hs1.rect(28.0, 24.0, 56.0, 24.7, 'cornice2'); hs1.rect(28.0, 0, 56.0, 1.0, 'plinth')
for u in [30.0 + i * 4.2 for i in range(6)]:
    hs1.rect(u, 3.5, u + 2.4, 11.0, 'winlit' if int(u) % 3 else 'win'); hs1.disc(u + 1.2, 11.0, 1.2, 'winlit' if int(u) % 3 else 'win', top_only=True)
    hs1.rect(u - 0.5, 14.5, u + 2.9, 15.1, 'cornice2'); hs1.rect(u, 15.5, u + 2.4, 20.5, 'win')
hs1.rect(44, 0, 47.5, 6, 'door')
# halls 2 and 3 behind, taller, their arches peeking over the flank roofs
hangar(58.0, 18.0, 58.0, 18.0, 38.0, 20.0, 22)
hs2 = add(Face('side', 20.0, box(58.0, 92.0, 38.0), 'stucco', 23)); hs2.rect(58.0, 31.0, 92.0, 38.0, 'roofmetal'); hs2.rect(58.0, 30.4, 92.0, 31.1, 'cornice2')
for u in [60 + i * 4.5 for i in range(7)]:
    hs2.rect(u, 4, u + 2.2, 12, 'winlit' if int(u) % 3 == 0 else 'win')
hangar(94.0, 18.0, 62.0, 20.0, 40.0, 24.0, 24)
hs3 = add(Face('side', 20.0, box(94.0, 130.0, 44.0), 'stucco', 25)); hs3.rect(94.0, 36.0, 130.0, 44.0, 'roofmetal')

# ================================================================== rasterise
layer = Image.new('I', (W, H), 0); ld = ImageDraw.Draw(layer)
FACE_ID = {}
def fid(f):
    if id(f) not in FACE_ID: FACE_ID[id(f)] = (len(FACE_ID) + 1, f)
    return FACE_ID[id(f)][0]
for i, (wx, z, w, h) in enumerate(SKYLINE):
    (x0, y0), (x1, y1) = proj(wx - w / 2, h, z), proj(wx + w / 2, 0, z)
    ld.rectangle([x0, y0, x1, y1], fill=1000 + i)
def near_z(f): return f.const if f.kind == 'front' else min(u for (u, v) in f.outline)
for f in sorted(FACES, key=near_z, reverse=True):
    ld.polygon(f.polygon(), fill=fid(f))
lp = layer.load(); BY_ID = {v[0]: v[1] for v in FACE_ID.values()}

# signpost at the junction (z=19)
POST_Z = 19.0; POST_X = CX + 2
(_, POST_TOP) = proj(0, 25.5, POST_Z); (_, POST_BOT) = proj(0, 0, POST_Z)
POST_TOP, POST_BOT = int(POST_TOP), int(POST_BOT) + 4
ARMS = [('SHED 521', -1, 21.0), ('SCRAPER', 1, 19.2), ('CATHEDRAL', -1, 17.4), ('VOXMARKET', 1, 15.6)]
SIGNS = [SIGN_SHED, SIGN_VOX]; ARM_PIX = {}
for i, (txt, sgn, wy) in enumerate(ARMS):
    (_, ay) = proj(0, wy, POST_Z); ay = int(ay); L = text_width(txt, 2) + 24
    if sgn < 0: pts = [(POST_X, ay - 10), (POST_X - L + 10, ay - 10), (POST_X - L, ay), (POST_X - L + 10, ay + 10), (POST_X, ay + 10)]
    else: pts = [(POST_X, ay - 10), (POST_X + L - 10, ay - 10), (POST_X + L, ay), (POST_X + L - 10, ay + 10), (POST_X, ay + 10)]
    ARM_PIX[i] = pts
    tx = POST_X - L + 7 if sgn < 0 else POST_X + 11
    SIGNS.append((txt, tx + text_width(txt, 2) // 2, ay - 5, 2))

M = [[None] * W for _ in range(H)]; Z = [[None] * W for _ in range(H)]; UV = [[None] * W for _ in range(H)]
ROADS = [((0, 18), (0, 7), 11.0), ((0, 18), (0, 300), 8.5), ((0, 18), (-45.5, 34), 8.0), ((0, 18), (35, 28), 7.5)]
def road_d(wx, wz):
    best = 9e9
    for (a, b, w) in ROADS:
        dx, dz = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dz * dz
        t = max(0.0, min(1.0, ((wx - a[0]) * dx + (wz - a[1]) * dz) / L2))
        best = min(best, math.hypot(wx - (a[0] + t * dx), wz - (a[1] + t * dz)) - w / 2)
    return min(best, math.hypot(wx, wz - 18) - 7.5)
PUDDLES = [(-7, 14.5, 2.2, 0.8), (10, 23, 1.8, 0.7), (-21, 31, 2.2, 0.7), (17, 41, 1.8, 0.6), (4, 11, 1.6, 0.6), (-13, 21, 1.4, 0.5)]
for y in range(H):
    for x in range(W):
        v = lp[x, y]
        if v >= 1000: M[y][x] = ('skyline', v); Z[y][x] = SKYLINE[v - 1000][1]; continue
        if v:
            f = BY_ID[v]; r = f.uvz(x, y) or (0.0, 0.0, near_z(f)); u, vv, z = r
            M[y][x] = (f.material_at(u, vv), f.obj); Z[y][x] = z; UV[y][x] = (u, vv, f); continue
        if y > HY:
            wx, wz = ground_at(x, y); d = road_d(wx, wz)
            pud = any(((wx - px_) / rx) ** 2 + ((wz - pz) / rz) ** 2 < 1 for (px_, pz, rx, rz) in PUDDLES)
            M[y][x] = ('puddle', 0) if pud else ('road', 0) if d < 0.25 * math.sin(wx * 3.1 + wz * 2.3) + 0.1 else ('kerb', 0) if (d < 0.6 and wz < 80) else ('dirt', 0)
            Z[y][x] = wz; UV[y][x] = (wx, wz, None)
        else: M[y][x] = ('sky', 0)
def put_poly(pts, key, obj, z=POST_Z):
    tmp = Image.new('1', (W, H), 0); ImageDraw.Draw(tmp).polygon(pts, fill=1); tp = tmp.load()
    for y in range(H):
        for x in range(W):
            if tp[x, y]: M[y][x] = (key, obj); Z[y][x] = z
def put_rect(x0, y0, x1, y1, key, obj, z=POST_Z):
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            if 0 <= x < W and 0 <= y < H: M[y][x] = (key, obj); Z[y][x] = z
put_rect(POST_X - 7, POST_TOP, POST_X + 7, POST_BOT, 'post', 0)
put_rect(POST_X - 10, POST_TOP - 7, POST_X + 10, POST_TOP, 'post', 1)
put_poly([(POST_X - 10, POST_TOP - 7), (POST_X, POST_TOP - 20), (POST_X + 10, POST_TOP - 7)], 'post', 1)
put_rect(POST_X - 15, POST_BOT - 9, POST_X + 15, POST_BOT, 'postbase', 0)
for i, pts in ARM_PIX.items():
    put_poly(pts, 'arm', i + 1)
    (_, ay) = proj(0, ARMS[i][2], POST_Z); put_rect(POST_X - 8, int(ay) - 2, POST_X + 8, int(ay) + 2, 'bolt', 0)
def cable(p0, p1, sag, n=40):
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(proj(p0[0] + (p1[0] - p0[0]) * t, p0[2] + (p1[2] - p0[2]) * t - sag * math.sin(math.pi * t), p0[1] + (p1[1] - p0[1]) * t))
    for (a, b) in zip(pts, pts[1:]):
        n2 = int(math.hypot(b[0] - a[0], b[1] - a[1])) + 1
        for j in range(n2 + 1):
            x, y = int(a[0] + (b[0] - a[0]) * j / n2), int(a[1] + (b[1] - a[1]) * j / n2)
            if 0 <= x < W and 0 <= y < H and M[y][x][0] in ('sky', 'skyline', 'plaster', 'win', 'winlit', 'cornice', 'stucco', 'roofmetal', 'cornice2', 'fanlight'): M[y][x] = ('cable', 0); Z[y][x] = 45
cable((-28, 40, 24.5), (20, 44, 25.5), 2.2); cable((-28, 48, 21.5), (20, 50, 22.5), 1.8); cable((-28, 57, 25.5), (20, 60, 26), 2.6)
(lx, ly) = proj(-4, 23.3 - 2.2, 45); put_rect(lx - 3, ly + 1, lx + 3, ly + 9, 'lamp', 0); put_rect(lx - 1, ly - 3, lx + 1, ly + 1, 'cable', 0)
# the shed's chain of the mast
(mx0, my0) = proj(SU1 - 8.7, 44, SZ); (mx1, my1) = proj(SU0 + 7, 38.6, SZ)
for j in range(0, 60):
    t = j / 59; x, y = int(mx0 + (mx1 - mx0) * t), int(my0 + (my1 - my0) * t + 10 * math.sin(math.pi * t))
    if 0 <= x < W and 0 <= y < H and M[y][x][0] == 'sky': M[y][x] = ('cable', 0); Z[y][x] = SZ
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
for (wx_, wy_, ln) in ((60, 600, 46), (140, 604, 30), (24, 596, 26), (990, 602, 42), (1040, 598, 30), (930, 606, 24), (250, 606, 18), (820, 604, 16)):
    branch(wx_, wy_, math.radians(90 + random.uniform(-12, 12)), ln, 3, 0)
TEXT = set()
for (txt, cx_, ty, sc) in SIGNS:
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
            v += 0.9 * math.exp(-(((x - 300) / 260) ** 2 + ((y - 80) / 90) ** 2))
            setc(x, y, ramp_i('K', band(v, x, y))); continue
        if k == 'skyline':
            c = HAZE[1] if h32(obj, 3) % 3 else HAZE[2]
            if h32(x // 2, y // 3, 4) % 37 == 0 and y < HY - 3 and x % 2 and y % 3 == 1: c = GLOW[1]
            setc(x, y, fogged(c, fog_of(z) * 0.6, x, y)); continue
        if k == 'cable': setc(x, y, fogged(STONE[0], fog_of(z), x, y)); continue
        if k == 'lamp':
            lx_, ly_ = proj(-4, 21.1, 45); setc(x, y, GLOW[1] if (abs(x - lx_) < 2 and 3 < y - ly_ < 7) else STONE[0]); continue
        if k == 'weed': setc(x, y, STONE[0] if (x + y) % 5 else STONE[1]); continue
        if k in ('post', 'arm', 'bolt', 'postbase'): continue
        if k in ('road', 'dirt', 'puddle', 'kerb'):
            wx, wz, _ = UV[y][x]
            if k == 'puddle':
                c = SKY[3] if (x + y) % 2 else STONE[2]
                if h32(x, y, 5) % 23 == 0: c = SKY[4]
            elif k == 'road':
                SXc, SZc = 1.0, 0.75
                row = math.floor(wz / SZc); col = math.floor(wx / SXc + (row % 2) * 0.5)
                fx = (wx / SXc + (row % 2) * 0.5) - col; fz = wz / SZc - row
                eps_x, eps_z = 1.05 * wz / F / SXc, 1.05 * wz * wz / (F * CAMH) / SZc
                i = 5.2 + (0.8 if h32(col, row, 7) % 4 == 0 else 0) - (0.8 if h32(col, row, 8) % 5 == 0 else 0)
                if wz < 75 and (fx < eps_x or fz < eps_z): i = 2.5
                i += 0.6 * (nB(x, y) - 0.5) - 0.6 * max(0.0, (y - 520) / 80)
                c = ramp_i('T', band(i, x, y))
            elif k == 'kerb': c = ramp_i('T', 1.5 + (nB(x, y) - 0.5))
            else:
                v = 2.3 + (nB(x, y) - 0.5) * 1.5 + (nC(x, y) - 0.5) * 0.7 - 0.5 * max(0.0, (y - 500) / 100)
                c = ramp_i('T', band(v, x, y))
                if h32(x, y, 9) % 97 == 0 and wz < 60: c = STONE[5]
                if h32(x // 2, y // 2, 10) % 53 == 0 and wz < 40: c = STONE[1]
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
        # ---- shed (wood)
        elif k == 'plank':
            pw = 0.9; pl = math.floor(u / pw); fu = u / pw - pl
            i = 3.2 + fl + (h32(pl, obj, 1) % 3) * 0.35 - 0.6 * (nA(x * 1.5, y) - 0.5)
            if fu < 0.14 * z / 36: i -= 1.6                                           # plank seams
            if h32(pl, int(v * 2.3), 2) % 19 == 0: i -= 0.9                            # knots / rot
            i -= 0.9 * max(0.0, 1 - v / 3.5)                                           # damp base
            c = ramp_i('D', band(i, x, y))
        elif k == 'frame': c = ramp_i('D', 1 if ((x + y) % 9) else 0)
        elif k == 'brace': c = ramp_i('D', 1.5 if (x % 7) else 0.5)
        elif k == 'under': c = ramp_i('D', 0)
        elif k == 'gate':
            pl = math.floor((u - (SU0 + 9)) / 1.3); fu = (u - (SU0 + 9)) / 1.3 - pl
            i = 1.2 + (h32(pl, 1) % 2) * 0.5 - (1.0 if fu < 0.12 else 0) - 0.8 * max(0.0, 1 - v / 3)
            if abs(u - (SU0 + 16.5)) < 0.12: i = 0
            if abs(v - 3) < 0.25 or abs(v - 6.5) < 0.25: i = 0.3
            c = ramp_i('D', band(i, x, y))
        elif k == 'shutter': c = ramp_i('D', 2 if (v * 4) % 2 < 1 else 1)
        elif k == 'glyph':
            c = ramp_i('T', 4 if ((x + y) % 5) else 3)
            gu, gv = (u - (SU0 + 20)) * 3, (v - 13.5) * 3
            if (int(gu) % 4 in (1, 2)) and (int(gv) % 4 in (1, 2)) and h32(int(gu) // 4, int(gv) // 4, 5) % 3: c = GLOW[1]     # cryptic lit glyphs
        elif k == 'plate': c = ramp_i('T', 5 if ((x + y) % 7) else 4)
        elif k == 'moss': c = ramp_i('K', 4 if ((x + y) % 3) else 3)
        elif k == 'lamp2': c = GLOW[2] if (x + y) % 2 else STONE[1]
        elif k == 'leanto': c = ramp_i('D', 2 if (y % 3) else 1)
        elif k == 'door': c = ramp_i('D', 1 if (u * 7) % 3 > 0.4 else 0)
        # ---- hangars (stucco, glass, metal)
        elif k == 'stucco':
            i = 3.2 + fl + (nA(x * 1.6, y * 1.6) - 0.5) * 1.0 + (nB(x, y) - 0.5) * 0.5
            i -= 1.2 * max(0.0, 1 - v / 3.0)                                          # grime at the base
            if h32(int(u * 0.7), 7) % 6 == 0 and (u * 0.7) % 1 < 0.08 and v > 4: i -= 0.8     # streaks
            c = ramp_i('P', band(i, x, y))
        elif k == 'cornice2': c = ramp_i('P', 5 if (v * 20) % 6 > 1 else 3)
        elif k == 'pilaster2': c = ramp_i('P', 4.4 + fl if (u * 8) % 5 > 0.5 else 2.5)
        elif k == 'keystone': c = ramp_i('P', 5)
        elif k == 'plinth': c = ramp_i('T', 3 if (u * 3) % 2 > 0.2 else 2)
        elif k == 'roofmetal':
            i = 2.6 + fl * 0.5 + (nB(x, y) - 0.5) * 0.8 + 0.8 * ((v - 24) / 8)
            if (u * 1.3) % 1 < 0.08: i -= 1.2                                          # standing seams
            c = ramp_i('E', band(i, x, y))
        elif k == 'fanlight':
            # radial + concentric glazing bars over a warm, dusk-lit interior
            cu, cv, r = 35.0, 14.0, 12.9
            if obj == 22: cu, cv, r = 38.0, 18.0, 18.4
            elif obj == 24: cu, cv, r = 40.0, 20.0, 22.4
            du, dv = u - cu, v - cv; rr = math.hypot(du, dv) / r; ang = math.degrees(math.atan2(dv, du))
            bar = (ang % 15) < 1.1 * z / 28 or abs(rr - 0.62) < 0.03 or abs(rr - 0.86) < 0.03 or rr > 0.97
            if bar: c = ramp_i('P', 1)
            else:
                g = 2.6 - 1.4 * rr + (nB(x * 2, y * 2) - 0.5) * 0.9
                c = GLOW[max(0, min(4, int(g)))]
                if h32(int(u * 2), int(v * 2), 3) % 9 == 0: c = GLOW[max(0, min(4, int(g) - 1))]
            f *= 0.6
        elif k == 'market':
            cu = 35.0; hw = 0.5 + 1.2 * max(0.0, 1 - v / 7.4)
            if abs(u - cu) < hw and v < 7.4:
                t = v / 7.4; c = GLOW[2] if t > 0.55 else GLOW[1] if t > 0.25 else GLOW[0]
                if (x + y) % 7 == 0: c = GLOW[1]
                if abs(u - cu + 0.5) < 0.25 and v < 1.6: c = WOOD[0]
            elif v < 1.8:
                c = WARM[2] if (x + y) % 3 else WARM[1]
                if abs(u - cu) < hw + 1.2: c = WARM[3] if (x + y) % 3 else WARM[2]
            elif v < 4.6:
                if v > 4.0: c = [RED[3], STONE[6], WARM[1], STONE[6]][int(u * 2.2) % 4]
                elif v > 3.6: c = WOOD[2]
                else:
                    c = WOOD[1] if (int(u * 3) + int(v * 3)) % 2 else WOOD[0]
                    if 2.4 < v < 3.2 and int(u * 4) % 2 == 0: c = [WARM[4], GLOW[1], RED[4], STONE[6]][int(u * 4) % 4]
            else:
                i = 1.2 + (nB(x, y) - 0.5) * 0.8 + 0.8 * max(0.0, 1 - abs(u - cu) / 4)
                c = WARM[max(0, min(5, int(i)))]
                if 6.3 < v < 6.9 and (u * 1.7) % 1 < 0.25: c = GLOW[3]
        elif k == 'girder':
            c = ramp_i('E', 1 if ((v * 6) % 1 < 0.18) else 2)
            if (u * 1.6) % 1 < 0.07 and 0.25 < (v * 6) % 1 < 0.75: c = ramp_i('E', 3)                       # rivets
        elif k == 'rail': c = ramp_i('T', 1 if (u * 4) % 1 > 0.1 else 2)
        elif k == 'leaf':
            # one tall steel door leaf: riveted frame, corrugated sheet infill, a band of small panes, a low X-brace
            if face.obj == 26: lu, lw = u - 18.0, 2.5
            elif u < OPEN_U0 + 0.1: lu, lw = (u - D0) % 2.0, (LEAF_W if u >= LEAVES[3] else 2.0)
            else: lu, lw = (D1 - u) % 2.0, (LEAF_W if u <= LEAVES[7] + LEAF_W else 2.0)
            lu = max(0.0, min(lw, lu))
            frame_ = lu < 0.2 or lu > lw - 0.2 or v < 0.55 or v > DOOR_TOP - 0.5 or abs(v - 9.2) < 0.14 or abs(v - 4.6) < 0.12
            if frame_:
                c = ramp_i('E', 1)
                if ((lu * 4) % 1 < 0.12 and (v * 1.3) % 1 < 0.1) or ((v * 4) % 1 < 0.12 and (lu * 1.3) % 1 < 0.1): c = ramp_i('E', 3)   # rivets
            elif 9.45 < v < 11.75 and 0.4 < lu < lw - 0.4:
                pane = (abs(lu - lw / 2) < 0.08) or (abs(v - 10.6) < 0.08)
                c = ramp_i('E', 1) if pane else (GLOW[0] if h32(int(lu * 3), int(v * 3), face.obj) % 4 else STONE[1])
            else:
                i = 2.3 + fl + (0.7 if (lu * 6) % 1 < 0.5 else 0) + (nB(x, y) - 0.5) * 0.5 - 0.6 * max(0.0, 1 - v / 2.5)
                if v < 9.0 and (abs(lu / lw - v / 9.0) < 0.05 or abs(1 - lu / lw - v / 9.0) < 0.05): i = 1.0           # X-brace
                c = ramp_i('E', band(i, x, y))
            if face.obj == 26: f = fog_of(27.6)
        elif k == 'opening':
            # the market hall seen through the doors: a lit central aisle narrowing into depth, stalls stepping back in
            # three ever-dimmer rows, a dark vault with hanging lamps and banners
            t = v / DOOR_TOP; cu = 35.0
            hw = 0.4 + 2.4 * max(0.0, 1 - t * 1.25)
            if abs(u - cu) < hw and v < 9.6:
                c = GLOW[1] if t < 0.3 else GLOW[0] if t < 0.6 else WARM[3]
                if (x + y) % 5 == 0: c = WARM[3] if t < 0.3 else WARM[2]
                if (abs(u - cu + 0.9) < 0.3 and v < 2.0) or (abs(u - cu - 1.4) < 0.25 and 1.0 < v < 3.2): c = WOOD[0]   # figures
            elif v < 1.3: c = WARM[2] if (x + y) % 3 else WARM[1]
            elif v < 4.4:                                                                       # near stalls
                if v > 3.8: c = [RED[3], STONE[6], WARM[1], STONE[6]][int(u * 2.2) % 4]
                elif v > 3.4: c = WOOD[2]
                else:
                    c = WOOD[1] if (int(u * 3) + int(v * 3)) % 2 else WOOD[0]
                    if 2.2 < v < 3.0 and int(u * 4) % 2 == 0: c = [WARM[4], GLOW[1], RED[4], STONE[6]][int(u * 4) % 4]
            elif v < 6.6:                                                                       # middle row, dimmer
                if v > 6.2: c = [RED[1], STONE[4], WARM[0], STONE[4]][int(u * 3) % 4]
                else: c = WOOD[0] if (int(u * 5) + int(v * 5)) % 2 else WARM[0]
            elif v < 8.4:                                                                       # far row, almost dark
                c = WARM[0] if (x + y) % 2 else WOOD[0]
                if 8.0 < v < 8.3 and (u * 2.5) % 1 < 0.2: c = GLOW[1]                               # far lantern string
            else:
                i = 1.0 + (nB(x, y) - 0.5) * 0.7 + 0.6 * max(0.0, 1 - abs(u - cu) / 4)
                c = WARM[max(0, min(5, int(i)))]
                if 10.0 < v < 10.6 and (u * 0.8) % 1 < 0.14: c = GLOW[3]                            # hanging lamps
                if 10.6 <= v < 11.2 and (u * 0.8) % 1 < 0.05: c = WOOD[0]
                if v > 11.0 and int(u * 1.2) % 2 == 0 and v > 11.0 + (u * 1.2 % 1) * 1.2: c = [RED[1], WARM[1], STONE[2], WOOD[1]][int(u * 1.2) % 4]
        elif k == 'board': c = ramp_i('T', 2 if (y % 3) else 1)
        else: c = STONE[3]
        setc(x, y, fogged(c, f, x, y))
for y in range(H):
    for x in range(W):
        k, obj = M[y][x]
        if k == 'post':
            i = 3 if x < POST_X - 3 else (2 if x < POST_X + 3 else 1)
            if obj == 1: i = 2
            if y % 19 == 0: i -= 1
            setc(x, y, ramp_i('D', i))
        elif k == 'postbase': setc(x, y, ramp_i('T', 4 if y % 3 else 3))
        elif k == 'arm':
            i = 3.0 if (y % 3) else 2.5
            if h32(x // 5, y // 4, obj) % 13 == 0: i -= 1
            setc(x, y, ramp_i('D', i))
        elif k == 'bolt': setc(x, y, STONE[2])
for (x, y) in TEXT:
    if 0 <= x < W and 0 <= y < H:
        k = M[y][x][0]
        if k == 'arm': setc(x, y, ramp_i('T', 7))
        elif k == 'plate': setc(x, y, GLOW[1] if (x + y) % 9 else GLOW[0])
        elif k == 'board': setc(x, y, ramp_i('P', 5))
# chain-link fence overlay in front of the shed (mesh + posts + barbed wire), gap at the gate path
for (u0, u1, z) in FENCE:
    (x0, yb) = proj(u0, 0, z); (x1, yt) = proj(u1, 3.6, z); x0, x1, yb, yt = int(x0), int(x1), int(yb), int(yt)
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

# the doors' outside rails on the ground, running left from the hangar corner
for (z, wx0, wx1) in RAILS:
    (x0, yr) = proj(wx0, 0, z); (x1, _) = proj(wx1, 0, z)
    for x in range(int(x0), int(x1) + 1):
        if 0 <= x < W and 0 <= int(yr) < H and M[int(yr)][x][0] in ('dirt', 'road', 'kerb', 'puddle'):
            setc(x, int(yr), fogged(STONE[1], fog_of(z), x, int(yr))); setc(x, int(yr) - 1, fogged(STONE[4], fog_of(z), x, int(yr) - 1))
# ================================================================== outlines
RANK = {'sky': 0, 'skyline': 0, 'cable': 0, 'road': 1, 'dirt': 1, 'puddle': 1, 'kerb': 1, 'weed': 4, 'post': 3, 'arm': 3, 'bolt': 3, 'postbase': 3, 'lamp': 3}
SOFT_PAIRS = [('sky', 'skyline'), ('road', 'dirt'), ('dirt', 'puddle'), ('road', 'puddle'), ('road', 'kerb'), ('dirt', 'kerb'), ('sky', 'cable'), ('skyline', 'cable'),
              ('plaster', 'cable'), ('plaster', 'cornice'), ('win', 'plaster'), ('winlit', 'plaster'), ('win', 'cable'), ('winlit', 'cable'),
              ('plank', 'frame'), ('plank', 'brace'), ('plank', 'under'), ('frame', 'under'), ('frame', 'brace'), ('plank', 'moss'), ('frame', 'moss'), ('under', 'moss'),
              ('plank', 'shutter'), ('plank', 'glyph'), ('plate', 'frame'), ('plank', 'lamp2'), ('plank', 'leanto'), ('frame', 'leanto'),
              ('stucco', 'cornice2'), ('stucco', 'pilaster2'), ('pilaster2', 'cornice2'), ('stucco', 'keystone'), ('stucco', 'plinth'), ('stucco', 'roofmetal'), ('cornice2', 'roofmetal'),
              ('stucco', 'win'), ('stucco', 'winlit'), ('fanlight', 'cornice2'), ('fanlight', 'keystone'), ('market', 'pilaster2'), ('market', 'cornice2'), ('board', 'cornice2'),
              ('stucco', 'board'), ('stucco', 'cable'), ('leaf', 'girder'), ('opening', 'leaf'), ('opening', 'girder'), ('opening', 'rail'), ('leaf', 'rail'), ('stucco', 'girder'), ('stucco', 'rail'), ('board', 'girder'), ('board', 'fanlight'), ('fanlight', 'girder'), ('pilaster2', 'girder'), ('pilaster2', 'leaf'), ('pilaster2', 'rail'), ('cornice2', 'girder'), ('pilaster2', 'opening'), ('opening', 'board'), ('girder', 'cable'), ('roofmetal', 'cable'), ('fanlight', 'cable'), ('cornice2', 'cable'), ('arm', 'bolt'), ('post', 'bolt'), ('plank', 'door'), ('plank', 'win')]
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
            if frozenset((ka, kb)) in SOFT or (ka == kb and ka in ('road', 'dirt', 'skyline', 'weed', 'cable', 'kerb')): continue
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
