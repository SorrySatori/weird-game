"""Shared pieces for the two rooms INSIDE the Egg Cathedral (cathedral_study_bg.py = the Bishop's study,
cathedral_heart_bg.py = the heart chamber) on the shared rasteriser (raster3d.py, the camera every background uses).

The stone and glass language is the approved entrance's (cathedral_bg.py): grey coursed ashlar with the odd sandstone
block, the cream eggshell, jewel-toned glass, dark oak, brass. Inside, the egg's living tissue has grown over the
stone: muted rose-brown flesh, veins, clear membranes. No daylight but what comes through a doorway; the rooms are lit
by candles (which the cathedral keeps burning) and by the Unborn's amber glow.

  LIGHTS / lit() / shade()   candle-light computed IN the shaders (the light steps the colour up its ramp and warms it;
                             paintpass's own light spill only adds a little on top)
  masonry()                  coursed ashlar in surface coordinates (from cathedral_bg.py)
  raycast()                  analytic surfaces (the egg-shaped shell) written straight into the raster
  obox() / cyl() / hcyl()    oriented boxes, upright and lying cylinders built from quads
  candle() / tendril()       a candle on a tendril cup (and its light), a fleshy tendril as a tapered tube"""
import math
from common import h32, ramp, band, make_noise
from raster3d import Raster, proj, ray, W, H, CX, HY, F, CAMH

# ---------------------------------------------------------------------------------------------------- palette
GREY = ramp('#0f0d0c #141211 #1f1c1b #2e2b2a #3d3a38 #4d4947 #5e5a58 #74706b #8a837c #a39c94 #b8aea2')
SAND = ramp('#1e1813 #2a211b #3a2c24 #4a3d34 #5a4a3e #66574a #766553 #857463 #958470 #a5937d #b6a48b')
EGG = ramp('#1b1918 #262322 #33302e #3d3a38 #4d4947 #5e5a58 #74706b #8a837c #a39c94 #b8aea2 #cdc3b5 #ddd3c4 #ece4d6')
TISSUE = ramp('#120a0a #1d100f #2c1816 #3d221e #4f2d27 #613931 #74463c #885548 #9c6656 #b07967 #c4907d')
SHELL = ramp('#1a1b18 #23251f #2d2f28 #383a31 #44463c #515246 #5f5f52 #6e6d5f #7e7c6c #8f8c7a #a19d89 #b3ad98 #c4bda8')
VEIN = ramp('#140a09 #201010 #2e1714 #3e201b #4f2a22 #60342a')
OAK = ramp('#0e0805 #1a0f09 #2e1a10 #3e2214 #4a2a17 #5a331c #6b3f22 #7d4c2a #8f5b35')
WAX = ramp('#3a3326 #5e5640 #7d735a #9c9075 #b9ae92 #d4cab0 #ebe3cc')
FLAME = ramp('#a8862f #e0c25a #f2dc86 #fff3c0 #fffbe8')
PARCH = ramp('#2e281c #4a4232 #625843 #7c7056 #968a6c #b0a482 #c8bc98')
LEATHER = ramp('#140a08 #22110d #331912 #462318 #5a2e1f #6e3a27')
IRON = ramp('#0e0c0b #1c1916 #2a2520 #3a332b #4e4536')
BRASS = ramp('#3b2c14 #6e5523 #a8862f #e0c25a #f2dc86')
RUGR = ramp('#140808 #210d0c #321412 #451c17 #58251c #6b3022')
RUGO = ramp('#2a1f0e #403016 #5a4420 #74592b #8e6f38')
GLOWC = ramp('#3a2a10 #6e5523 #a8862f #c9a440 #e0c25a #f2dc86 #fff3c0')
INK = (8, 6, 5)

CANDLE = (1.0, 0.70, 0.40)
DAY = (0.72, 0.84, 0.90)
GOLD = (1.0, 0.78, 0.42)

_nz = [make_noise(1, s, 509, 509) for s in (81, 82, 83, 84, 85, 86)]
def wn(i, a, b): return _nz[i](a + 3000.0, b + 3000.0)              # noise in WORLD units
def ri(r, i): return r[max(0, min(len(r) - 1, int(i)))]
def tone(r, v, x, y): return ri(r, band(v, x, y))
def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def clamp(c): return tuple(max(0, min(255, int(v))) for v in c)
rng = lambda *k: h32(*k) / 4294967295.0

# ---------------------------------------------------------------------------------------------------- fog + light
FOG = {'col': (16, 12, 10), 'z0': 16.0, 'span': 70.0, 'max': 0.3}
def fog(z): return max(0.0, min(FOG['max'], (z - FOG['z0']) / FOG['span']))
def fogged(c, z): return mix(c, FOG['col'], fog(z))

LIGHTS = []                                      # (X, Y, Z, (r, g, b), intensity, radius, falloff)
def light(X, Y, Z, col=CANDLE, I=1.0, R=6.0, fall=0.12):
    LIGHTS.append((X, Y, Z, col, I, R, fall))
def lit(X, Y, Z, n=None):
    """the light reaching a surface point: Lambert (with a soft wrap), a candle-like inverse-square falloff that ends
    at the light's radius R, per colour channel"""
    r = g = b = 0.0
    for (lx, ly, lz, c, I, R, fall) in LIGHTS:
        dx, dy, dz = lx - X, ly - Y, lz - Z
        d2 = dx * dx + dy * dy + dz * dz
        if d2 >= R * R: continue
        d = math.sqrt(d2) + 1e-6
        ndl = 0.7 if n is None else max(0.0, (dx * n[0] + dy * n[1] + dz * n[2]) / d)
        k = I * (0.15 + 0.85 * ndl) * (1 - d / R) ** 2 / (1 + fall * d2)
        r += c[0] * k; g += c[1] * k; b += c[2] * k
    return (r, g, b)
def soot(X, Y, Z):
    """candles blacken what is right above them: a plume widening upwards, fading with the height"""
    k = 0.0
    for (lx, ly, lz, c, I, R, fall) in LIGHTS:
        if c is not CANDLE or Y < ly + 0.1: continue
        dy = Y - ly
        if dy > 5.0: continue
        dh = math.hypot(X - lx, Z - lz)
        w = 0.25 + dy * 0.18
        if dh > 2.5 * w + 0.6: continue
        k = max(k, math.exp(-(dh / w) ** 2) * math.exp(-dy / 2.2) * (1 - math.exp(-dy / 0.35)) * min(1.0, I * 1.3))
    return k
AMB = {'fn': None}                               # ambient(wp, n) -> ramp steps (the room's soft fill)
def shade(rmp, v0, wp, n, x, y, gain=3.0, warm=0.55, amb=0.0):
    """a material lit by the room: the light lifts it up its ramp and pulls it towards the light's hue"""
    X, Y, Z = wp
    lr, lg, lb = lit(X, Y, Z, n)
    I = 0.3 * lr + 0.59 * lg + 0.11 * lb
    a = AMB['fn'](wp, n) if AMB['fn'] else 0.0
    c = tone(rmp, v0 + amb + a + gain * (I / (0.35 + I)) * 2.1, x, y)
    if I > 0.01:
        k = min(1.0, I * 1.6) * warm
        c = (c[0] * (1 + (lr / I - 1) * k), c[1] * (1 + (lg / I - 1) * k), c[2] * (1 + (lb / I - 1) * k))
    return fogged(clamp(c), Z)

class VeinMap:
    """a branching vein network drawn in a surface's own (u, v) coordinates (world units): trunks grow from roots,
    wander, fork and taper; sample(u, v) -> (coverage 0..1, core) or None"""
    def __init__(s, u0, u1, v0, v1, res=0.06):
        s.u0, s.v0, s.res = u0, v0, res
        s.nu, s.nv = int((u1 - u0) / res) + 1, int((v1 - v0) / res) + 1
        s.g = bytearray(s.nu * s.nv); s.maxdepth = 5
    def stamp(s, u, v, r):
        rr = max(r, s.res * 0.7)
        iu0, iu1 = int((u - rr - s.u0) / s.res), int((u + rr - s.u0) / s.res) + 1
        iv0, iv1 = int((v - rr - s.v0) / s.res), int((v + rr - s.v0) / s.res) + 1
        for iv in range(max(0, iv0), min(s.nv, iv1 + 1)):
            for iu in range(max(0, iu0), min(s.nu, iu1 + 1)):
                d = math.hypot(s.u0 + iu * s.res - u, s.v0 + iv * s.res - v)
                if d > rr: continue
                val = int(min(1.0, (1 - d / rr) * 1.6) * 200) + (55 if d < rr * 0.4 and r > 0.12 else 0)
                k = iv * s.nu + iu
                if val > s.g[k]: s.g[k] = val
    def grow(s, u, v, ang, r, seed, depth=0, length=None, bend=0.16, fork=(2.2, 4.5), stop=None):
        """ang: direction in radians (0 = +v, up the surface); r: radius at the root. A vessel that runs into
        another one joins it and ends there (vessels don't cross)"""
        L = length or (10 + r * 30)
        step = 0.22; travelled = 0.0; nextfork = fork[0] + rng(seed, 1) * (fork[1] - fork[0]); k = 0
        curl = (rng(seed, 9) - 0.5) * 0.05
        guard = 0.9
        while travelled < L and r > 0.022:
            ang += (rng(seed, k, 3) - 0.5) * bend * 2 + curl + math.sin(travelled * 0.9 + seed) * 0.04
            if travelled > guard:                                                                  # about to run into a vessel?
                a_ = s.sample(u + math.sin(ang) * (r * 1.8 + 0.12), v + math.cos(ang) * (r * 1.8 + 0.12))
                if a_ and a_[0] > 0.3:
                    for j in range(4): s.stamp(u + math.sin(ang) * 0.06 * j, v + math.cos(ang) * 0.06 * j, r)
                    break
            sub = max(1, int(step / max(s.res * 0.8, r * 0.5)))
            for j in range(sub):                                                                   # a continuous stroke
                s.stamp(u + math.sin(ang) * step * j / sub, v + math.cos(ang) * step * j / sub, r)
            u += math.sin(ang) * step; v += math.cos(ang) * step
            if stop and stop(u, v): break
            travelled += step; k += 1
            r *= 0.993
            if travelled > nextfork and depth < s.maxdepth:
                side = 1 if rng(seed, k, 5) > 0.5 else -1
                s.grow(u, v, ang + side * (0.5 + rng(seed, k, 6) * 0.5), r * 0.6, seed * 31 + k, depth + 1, L * 0.5, bend * 1.2, fork, stop)
                ang -= side * 0.18; r *= 0.85; guard = travelled + 1.4
                sc = min(1.0, 0.3 + r * 3.0)                                                       # thin vessels fork more often
                nextfork = travelled + (fork[0] + rng(seed, k, 7) * (fork[1] - fork[0])) * sc
    def sample(s, u, v):
        iu, iv = int((u - s.u0) / s.res + 0.5), int((v - s.v0) / s.res + 0.5)
        if 0 <= iu < s.nu and 0 <= iv < s.nv:
            val = s.g[iv * s.nu + iu]
            if val: return (min(1.0, val / 200.0), val > 200)
        return None

# ---------------------------------------------------------------------------------------------------- masonry
def masonry(r, u, Y, z, x, y, v0, ch=0.55, L=0.9, seed=0, rough=0.35, weather=0.9, pale=None):
    """coursed ashlar in surface coordinates (u along, Y up): blocks of one, two or three lengths per course, thin
    sunk mortar joints, a lit top arris and a shadowed foot per course, a tone per block, big weathering patches, the
    odd dark (dirty) or pale (sandstone) block, tooling grain. Returns (ramp, value) so the caller can light it."""
    ps = z / F
    row = math.floor(Y / ch); fv = Y / ch - row
    uu = u + (h32(row, seed, 5) % 97) / 97.0 * L * 2.0
    col = math.floor(uu / L); fu = uu / L - col
    c0 = col
    while h32(row, c0, seed) % 3 == 0 and col - c0 < 2: c0 -= 1                               # merged blocks
    bid = h32(row, c0, seed + 7)
    rr = pale if (pale is not None and bid % 7 == 0) else r
    v = v0 + ((bid % 9) - 4) * 0.1 + (wn(0, u * 0.22 + seed * 7.0, Y * 0.22) - 0.5) * weather
    v += (wn(1, u * 5.0 + (bid % 17), Y * 5.0) - 0.5) * rough
    if bid % 11 == 0: v -= 0.45
    elif bid % 13 == 0: v += 0.3
    if fv > 1 - 1.5 * ps / ch: v += 0.4
    elif fv < 2.5 * ps / ch: v -= 0.35
    if fv < ps / ch or (fu < ps / L and h32(row, col, seed) % 3 != 0): v -= 1.4                  # the joints
    return rr, v

def veins(u, v, dens, scale=1.0):
    """living veins over a surface (u, v in world units): ridged noise isolines, thick trunks + fine capillaries,
    only where `dens` (0..1) allows. Returns (strength 0..1, core) or None"""
    if dens <= 0.02: return None
    a = abs(wn(2, u * 0.16 / scale, v * 0.16 / scale) - 0.5)
    w1 = 0.022 * dens
    if a < w1: return (1.0, a < w1 * 0.45)
    b = abs(wn(3, u * 0.45 / scale + 17, v * 0.45 / scale) - 0.5)
    w2 = 0.014 * max(0.0, dens - 0.25)
    if b < w2 and wn(4, u * 0.3, v * 0.3) > 0.45: return (0.55, False)
    return None

# ---------------------------------------------------------------------------------------------------- geometry
def raycast(rs, hit, shader, cls='wall', obj=None, rows=None):
    """an analytic surface: hit(dx, dy) -> (t, a, b, normal) or None for the camera ray through each pixel"""
    obj = obj or rs.obj()
    for y in (rows or range(H)):
        for x in range(W):
            dx, dy = ray(x, y)
            h_ = hit(dx, dy)
            if h_ is None: continue
            t, a, b, nrm = h_
            if t <= 0.5 or t >= rs.ZB[y][x]: continue
            rs.put(x, y, t, shader, obj, a, b, (dx * t, CAMH + dy * t, t), nrm, cls)
    return obj

def frame(O, ang):
    """a horizontal frame at O: e_t (along, angle ang from +X) and e_o (its normal in the floor plane, turned +90 deg)"""
    et = (math.cos(ang), 0.0, math.sin(ang)); eo = (-math.sin(ang), 0.0, math.cos(ang))
    def P(u, Y, e): return (O[0] + et[0] * u + eo[0] * e, Y, O[2] + et[2] * u + eo[2] * e)
    return P, et, eo

def obox(rs, O, ang, u0, u1, y0, y1, e0, e1, front, side=None, top=None, cls='prop', obj=None):
    """a box in the frame (O, ang): u along, e across (e0 = the face towards the camera); draws all faces that can face
    the camera, the raster's depth test sorts them"""
    P, et, eo = frame(O, ang)
    obj = obj or rs.obj(); side = side or front; top = top or front
    rs.quad(P(u0, y0, e0), P(u1, y0, e0), P(u0, y1, e0), front, obj, cls=cls)
    rs.quad(P(u0, y0, e1), P(u1, y0, e1), P(u0, y1, e1), front, obj, cls=cls)
    rs.quad(P(u0, y0, e0), P(u0, y0, e1), P(u0, y1, e0), side, obj, cls=cls)
    rs.quad(P(u1, y0, e0), P(u1, y0, e1), P(u1, y1, e0), side, obj, cls=cls)
    if y1 < CAMH: rs.quad(P(u0, y1, e0), P(u1, y1, e0), P(u0, y1, e1), top, obj, cls=cls)
    else: rs.quad(P(u0, y0, e0), P(u1, y0, e0), P(u0, y0, e1), top, obj, cls=cls)
    return obj

def cyl(rs, cx, cz, r, y0, y1, sh, n=14, cls='prop', obj=None):
    """an upright cylinder from facets (the shader gets the world position; its normal is radial)"""
    obj = obj or rs.obj()
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        P0 = (cx + r * math.sin(a0), y0, cz - r * math.cos(a0)); P1 = (cx + r * math.sin(a1), y0, cz - r * math.cos(a1))
        rs.quad(P0, P1, (P0[0], y1, P0[2]), sh, obj, cls=cls)
    return obj

def wall_frame(nx, nz):
    """the frame angle for a box standing against a wall whose outward normal (in the floor plane) is (nx, nz):
    e then runs outwards, so a box from e = -depth to 0 stands on the room's side"""
    return math.atan2(-nx, nz)

def hcyl(rs, P0, P1, r, sh, n=12, cls='prop', obj=None):
    """a lying cylinder along P0 -> P1 (horizontal); the shader's s runs along it, t around it (0 = top)"""
    obj = obj or rs.obj()
    dx, dz = P1[0] - P0[0], P1[2] - P0[2]; L = math.hypot(dx, dz) or 1.0
    px, pz = -dz / L, dx / L                                                                    # horizontal, across
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        def off(a): return (px * r * math.sin(a), r * math.cos(a), pz * r * math.sin(a))
        o0, o1 = off(a0), off(a1)
        Q0 = (P0[0] + o0[0], P0[1] + o0[1], P0[2] + o0[2]); Q1 = (P1[0] + o0[0], P1[1] + o0[1], P1[2] + o0[2])
        Q3 = (P0[0] + o1[0], P0[1] + o1[1], P0[2] + o1[2])
        ring = (a0 + a1) / 2 / (2 * math.pi)
        rs.quad(Q0, Q1, Q3, (lambda x, y, s, t, z, wp, ring=ring: sh(x, y, s, ring, z, wp)), obj, cls=cls)
    for P in (P0, P1):                                                                          # the end caps
        rs.disc(P[0], P[1], P[2], r, (lambda x, y, s, t, z, wp, P=P: sh(x, y, -1.0, math.hypot(s, t), z, P)), obj, cls=cls)
    return obj

def tube(rs, pts, r0, r1, sh, cls='prop', steps=None):
    """a tapered tube through 3D points (a tendril, a root): camera-facing discs along a Catmull-Rom curve; the
    shader's s, t = the offset across the disc, so it can shade a round section (lit from the upper left)"""
    obj = rs.obj()
    def cr(p0, p1, p2, p3, t):
        return tuple(0.5 * (2 * p1[i] + (-p0[i] + p2[i]) * t + (2 * p0[i] - 5 * p1[i] + 4 * p2[i] - p3[i]) * t * t
                            + (-p0[i] + 3 * p1[i] - 3 * p2[i] + p3[i]) * t * t * t) for i in range(3))
    P = [pts[0]] + list(pts) + [pts[-1]]
    seg = len(pts) - 1
    total = 0
    samples = []
    for i in range(seg):
        a, b = proj(*P[i + 1]), proj(*P[i + 2])
        n = steps or max(4, int(math.dist(a, b) / 0.7) + 2)
        for k in range(n):
            samples.append(cr(P[i], P[i + 1], P[i + 2], P[i + 3], k / n))
    samples.append(pts[-1])
    N = len(samples)
    for k, Q in enumerate(samples):
        f = k / max(1, N - 1)
        r = r0 + (r1 - r0) * f
        rs.disc(Q[0], Q[1], Q[2], r, (lambda x, y, s, t, z, wp, f=f, Q=Q: sh(x, y, s, t, z, (Q[0] + s * 0.0, Q[1], Q[2]), f)), obj, cls=cls)
    return obj

def pipe(rs, pts, r0, r1, sh, n=8, cls='prop', obj=None):
    """a tube through 3D points built from facets (a frustum per segment): cheap for long, thick things -- piers,
    ribs, roots, organ pipes. The shader gets sh(x, y, f, a, z, wp, nrm): f = 0..1 along the whole tube, a = the angle
    round it (0 = up / towards -z), nrm = the outward normal at that pixel"""
    obj = obj or rs.obj()
    seglen = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(seglen) or 1.0
    acc = 0.0
    for i in range(len(pts) - 1):
        P0, P1 = pts[i], pts[i + 1]
        f0, f1 = acc / total, (acc + seglen[i]) / total
        acc += seglen[i]
        ax = [P1[k] - P0[k] for k in range(3)]; L = math.sqrt(sum(c * c for c in ax)) or 1e-6
        ax = [c / L for c in ax]
        ref = (0.0, 0.0, -1.0) if abs(ax[2]) < 0.9 else (0.0, 1.0, 0.0)
        b1 = [ax[1] * ref[2] - ax[2] * ref[1], ax[2] * ref[0] - ax[0] * ref[2], ax[0] * ref[1] - ax[1] * ref[0]]
        bl = math.sqrt(sum(c * c for c in b1)) or 1.0; b1 = [c / bl for c in b1]
        b2 = [ax[1] * b1[2] - ax[2] * b1[1], ax[2] * b1[0] - ax[0] * b1[2], ax[0] * b1[1] - ax[1] * b1[0]]
        r = r0 + (r1 - r0) * (f0 + f1) / 2
        def mk(P0=P0, ax=ax, L=L, f0=f0, f1=f1, b1=b1, b2=b2):
            def facet(x, y, s, t, z, wp):
                q = [wp[k] - P0[k] for k in range(3)]
                along = max(0.0, min(L, q[0] * ax[0] + q[1] * ax[1] + q[2] * ax[2]))
                nr = [q[k] - ax[k] * along for k in range(3)]; nl = math.sqrt(sum(c * c for c in nr)) or 1.0
                nr = (nr[0] / nl, nr[1] / nl, nr[2] / nl)
                ang = math.atan2(nr[0] * b2[0] + nr[1] * b2[1] + nr[2] * b2[2], nr[0] * b1[0] + nr[1] * b1[1] + nr[2] * b1[2])
                return sh(x, y, f0 + (f1 - f0) * along / L, ang, z, wp, nr)
            return facet
        facet = mk()
        for j in range(n):
            a0, a1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
            o0 = [r * (math.cos(a0) * b1[k] + math.sin(a0) * b2[k]) for k in range(3)]
            o1 = [r * (math.cos(a1) * b1[k] + math.sin(a1) * b2[k]) for k in range(3)]
            Q0 = tuple(P0[k] + o0[k] for k in range(3)); Q1 = tuple(P0[k] + o1[k] for k in range(3))
            Q3 = tuple(P1[k] + o0[k] for k in range(3))
            rs.quad(Q0, Q1, Q3, facet, obj, cls=cls)
    return obj

def voronoi(u, v, cell, seed=0, jit=0.85):
    """distance to the nearest cell point, to the second nearest, and the nearest cell's id (u, v in world units)"""
    iu, iv = math.floor(u / cell), math.floor(v / cell)
    d1 = d2 = 9e9; cid = 0
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            cu, cv = iu + a, iv + b
            pu = (cu + 0.5 + (rng(cu, cv, seed) - 0.5) * jit) * cell
            pv = (cv + 0.5 + (rng(cu, cv, seed + 1) - 0.5) * jit) * cell
            d = math.hypot(u - pu, v - pv)
            if d < d1: d2, d1, cid = d1, d, h32(cu, cv, seed)
            elif d < d2: d2 = d
    return d1, d2, cid

def flame_sh(x, y, s, t, z, wp):
    """a candle flame: a teardrop, white-gold core"""
    if t > 0.25: w = 0.5 * math.sqrt(max(0.0, 1 - ((t - 0.25) / 0.72) ** 2))                    # the round foot
    else: w = 0.5 * max(0.0, (t + 1) / 1.25) ** 1.4                                               # up to a tip
    if abs(s) > w or t > 0.97: return None
    k = abs(s) / max(0.05, w)
    return FLAME[4] if k < 0.35 and t > -0.4 else (FLAME[3] if k < 0.7 else FLAME[1])

def candle(rs, X, Y0, Z, h, r=0.16, I=0.55, R=5.5, lean=0.0):
    """a candle burning low: wax with runs down its side, a pool on the top, a flame (emissive) and its light"""
    def wax(x, y, s, t, z, wp):
        X_, Y_, Z_ = wp
        a = math.atan2(X_ - X, -(Z_ - Z))
        n = (math.sin(a), 0.0, -math.cos(a))
        run = (h32(int(a * 6 + 40), int(X * 10), 3) % 5 == 0) and (Y0 + h - Y_) < 0.25 + (h32(int(a * 6 + 40), 5) % 7) * 0.08
        v = 2.4 + 1.2 * math.cos(a + 0.7) + (0.9 if run else 0) + (wn(1, a * 3, Y_ * 6) - 0.5) * 0.4
        return shade(WAX, v, wp, n, x, y, gain=2.6, warm=0.35)
    cyl(rs, X, Z, r, Y0, Y0 + h, wax, n=10)
    rs.disc(X, Y0 + h + 0.01, Z, r * 0.9, lambda x, y, s, t, z, wp: WAX[5] if s * s + t * t < 0.4 else WAX[4])
    rs.line3((X, Y0 + h, Z - 0.01), (X + lean * 0.1, Y0 + h + 0.12, Z - 0.01), lambda *a: (24, 18, 12), w=0.03)
    rs.disc(X + lean * 0.12, Y0 + h + 0.32, Z - 0.02, 0.2, flame_sh, cls='emit')
    light(X + lean * 0.12, Y0 + h + 0.35, Z - 0.3, CANDLE, I, R)

def tissue_tube(vmax=4.6):
    """a fleshy tendril's shader for tube(): a round section lit from the upper left, a dark rim, a wet highlight,
    the room's light on top"""
    def sh(x, y, s, t, z, wp, f):
        d2 = s * s + t * t
        v = vmax - 0.6 * f - 1.5 * (s * 0.55 + t * 0.8) - 1.6 * d2 * d2
        if (s + 0.38) ** 2 + (t + 0.42) ** 2 < 0.035: v += 2.6                                   # the wet glint
        elif (s + 0.3) ** 2 + (t + 0.35) ** 2 < 0.09 and (x + y) % 2: v += 1.2
        if wn(2, (wp[0] + wp[2]) * 3.0 + s, wp[1] * 3.0 + t) > 0.7: v -= 0.9                       # mottling
        L = lit(wp[0], wp[1], wp[2], None)
        I = 0.3 * L[0] + 0.59 * L[1] + 0.11 * L[2]
        a = AMB['fn'](wp, (0.0, -t, -0.5)) if AMB['fn'] else 0.0
        c = tone(TISSUE, v + a + 3.0 * I / (0.45 + I) * 1.6, x, y)
        if I > 0.01:
            k = min(1.0, I * 1.6) * 0.4
            c = clamp((c[0] * (1 + (L[0] / I - 1) * k), c[1] * (1 + (L[1] / I - 1) * k), c[2] * (1 + (L[2] / I - 1) * k)))
        return fogged(c, z)
    return sh
