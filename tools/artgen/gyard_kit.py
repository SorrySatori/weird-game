"""Shared pieces for the two Godgraveyard backgrounds (gyard_gate_bg.py: the sealed gate; gyard_bg.py: the field of
dead gods) on raster3d.py + shedkit.py: carved stone whose relief is a height field shaded by its own normals (incised
lines, raised rings, faces), lichen and moss on it; slabs that lean and have a real thickness (the front face plus a
stack of back layers that show as the rim on the side facing the vanishing point); round wrought-iron bars; bare trees;
irregular cobbles; earth heaped round the foot of a stone; and a low ground mist laid over the finished render
(world-space banks, quantised with an ordered dither, so it stays pixel art).
Everything is in world units on the shared camera (VP 533, 296, F 300, eye 12; the player is ~6.4 tall, feet on y 534
at depth 15). Own copies only -- the shared modules stay untouched."""
import math
from PIL import Image
from common import h32, make_noise, band
from pal_day import HAZE, GLOW, LEAF, BONE, RED, FOG, INK, ramp
from shedkit import wn, tone, mix, ri, sky
from raster3d import Raster, proj, ray, W, H, CX, HY, F, CAMH

# ---------------------------------------------------------------------------------------------------- palette
GRAVE = ramp('#0f1211 #161a18 #1e2320 #272d29 #313833 #3c433d #484f48 #565d54 #656c61 #767c70 #898e80')   # cool grave stone
LIME = ramp('#15130f #1e1b16 #28241e #332e27 #3f3930 #4c463b #5a5347 #696154 #797062 #8a8172')            # warmer limestone
LICHEN = ramp('#363a2c #474c38 #5a5f46 #6d7255 #808463 #929571')
MOSSR = ramp('#141b11 #1b2516 #23311b #2c3e21 #364b27 #42592e #4f6735')
MUD = ramp('#0d0b09 #14110d #1b1612 #231c16 #2b231b #352b20 #403326 #4b3d2e')
IRON = ramp('#0a0c0d #111417 #191d21 #22282c #2c3338 #384046 #465057 #576169')
VERDI = ramp('#13241e #1b3329 #244436 #2f5644 #3d6a54 #4f8066 #66977b')
WAX = ramp('#260908 #3f0e0b #5a1510 #771f17 #923023 #ab4532 #c25e45')
GILT = ramp('#241f13 #332c1a #453b23 #574a2c #6a5a35 #7d6a3f #8f7a4a #a08b58')
BRONZE = ramp('#14120d #1d1a12 #272218 #322b1e #3e3525 #4b402c #594b34 #67573c')
HEATH = ramp('#1f171b #2a1f25 #352830 #41313a #4c3a44 #57444e')
STRAW = ramp('#1c1b11 #282616 #35321c #434023 #524e2b #625d34 #736c3f')
PAPER = ramp('#5a5648 #747060 #8e8a78 #a8a490 #c0bca6')
MIST = (98, 113, 107)                                                        # the low ground mist, pale and cool

# depth haze: the generators may change these before they build anything (the graveyard is mistier than the gate)
FOGCFG = {'scale': 70.0, 'max': 0.82, 'col': FOG, 'near': 14.0}
def fog_of(z): return max(0.0, min(FOGCFG['max'], 1 - math.exp(-(z - FOGCFG['near']) / FOGCFG['scale'])))
def fogged(c, z, k=1.0): return mix(c, FOGCFG['col'], fog_of(z) * k)

_n1 = make_noise(1, 611, 509, 509); _n2 = make_noise(1, 612, 509, 509); _n3 = make_noise(1, 613, 509, 509)
def n1(a, b): return _n1(a + 3000.0, b + 3000.0)
def n2(a, b): return _n2(a + 3000.0, b + 3000.0)
def n3(a, b): return _n3(a + 3000.0, b + 3000.0)
def h01(*a): return (h32(*a) % 10007) / 10007.0
def clamp(v, a=0.0, b=1.0): return a if v < a else b if v > b else v
def smooth(t): t = clamp(t); return t * t * (3 - 2 * t)

# ---------------------------------------------------------------------------------------------------- 2D shapes (face units)
def seg_d(u, v, a, b):
    """distance from (u, v) to the segment a-b"""
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy or 1e-9
    t = clamp(((u - ax) * dx + (v - ay) * dy) / L)
    return math.hypot(u - ax - dx * t, v - ay - dy * t)
def poly_d(u, v, pts):
    return min(seg_d(u, v, a, b) for a, b in zip(pts, pts[1:]))
def groove(d, w, depth):
    """an incised line: a V-cut `w` wide (half-width), `depth` deep"""
    return -depth * (1 - d / w) if d < w else 0.0
def ridge(d, w, height):
    """a raised line, rounded"""
    return height * math.sqrt(1 - (d / w) ** 2) if d < w else 0.0
def dome(d, r, height):
    return height * math.sqrt(max(0.0, 1 - (d / r) ** 2)) if d < r else 0.0
def inside_poly(u, v, pts):
    inside = False; n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        if (y0 > v) != (y1 > v) and u < x0 + (x1 - x0) * (v - y0) / (y1 - y0): inside = not inside
    return inside

# outlines (u across -w/2..w/2, v up 0..h) with a ragged, chipped edge
def arched(w, h, rough=0.06, seed=0, chip=None):
    """a round-topped slab; chip=(u, v, r) bites a piece out of it"""
    r = w / 2; vs = h - r
    def f(u, v):
        e = (n1(u * 2.3 + seed * 7, v * 2.3) - 0.5) * rough * 2
        if chip and math.hypot(u - chip[0], v - chip[1]) < chip[2] + e: return False
        if abs(u) > r + e: return False
        if v > vs: return math.hypot(u, v - vs) < r + e
        return v > -0.5
    return f
def gabled(w, h, roof, rough=0.05, seed=0, chip=None):
    """a house-shaped stele: straight sides, a pitched top `roof` tall"""
    def f(u, v):
        e = (n1(u * 2.3 + seed * 7, v * 2.3) - 0.5) * rough * 2
        if chip and math.hypot(u - chip[0], v - chip[1]) < chip[2] + e: return False
        if abs(u) > w / 2 + e: return False
        top = h - roof * abs(u) / (w / 2)
        return -0.5 < v < top + e
    return f
def rect_o(w, h, rough=0.05, seed=0):
    def f(u, v):
        e = (n1(u * 2.3 + seed * 7, v * 2.3) - 0.5) * rough * 2
        return abs(u) < w / 2 + e and -0.5 < v < h + e
    return f

# ---------------------------------------------------------------------------------------------------- carved stone
LIGHT = (-0.42, 0.62, 0.66)                                                    # overcast: from above, a little from the left
_ll = math.sqrt(sum(c * c for c in LIGHT)); LIGHT = tuple(c / _ll for c in LIGHT)

def stone_face(relief, outline, ramp_=GRAVE, v0=5.2, gain=3.2, lichen=0.35, moss=0.35, gilt=None, seed=0, wear=1.0,
               dark=None, fogk=1.0, hgain=1.2, lramp=None):
    """the shader of a carved face: relief(u, v) -> (height, tag) in face units -- tag 'hole' = a deep dark opening,
    'gilt' = tarnished gold in the cut, 'eye' = a polished boss; the normal comes from the height field (a step of one
    screen pixel), so incisions get a shadowed upper wall and a lit lower lip. Lichen crusts, moss on the top edge and
    the foot, dark wet runs, all in face coordinates."""
    lramp = lramp or LICHEN
    def sh(x, y, s, t, z, wp, U=None, V=None):
        u, v = U, V
        px = z / F * 1.05
        h0, tag = relief(u, v)
        hx = relief(u + px, v)[0] - relief(u - px, v)[0]
        hy = relief(u, v + px)[0] - relief(u, v - px)[0]
        nx, ny, nz = -hx / (2 * px), -hy / (2 * px), 1.0
        nl = math.sqrt(nx * nx + ny * ny + nz * nz)
        dif = (nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]) / nl - LIGHT[2]
        val = v0 + dif * gain + h0 * hgain
        val += (n2(u * 0.9 + seed * 13, v * 0.9) - 0.5) * 1.1 * wear + (n3(u * 3.1 + seed, v * 3.1) - 0.5) * 0.5 * wear
        if h32(int(u * 9 + 999), int(v * 9 + 999), seed) % 17 == 0: val -= 0.6 * wear                         # pits
        # the ragged edge: a lighter chipped arris just inside the outline, a darker one where it faces down
        edge_up = not outline(u, v + px * 1.5); edge_dn = not outline(u, v - px * 1.5)
        edge_l = not outline(u - px * 1.5, v); edge_r = not outline(u + px * 1.5, v)
        if edge_up or edge_l: val += 0.9
        elif edge_dn or edge_r: val -= 0.7
        if dark is not None: val -= dark(u, v)
        if tag == 'hole': c = tone(ramp_, 0.5 + 0.8 * n3(u * 5 + seed, v * 5) + dif * 0.6, x, y)
        else: c = tone(ramp_, val, x, y)
        if tag == 'gilt' and gilt is not None and n3(u * 4 + 7, v * 4) > 0.4:
            c = mix(c, tone(GILT, 2.6 + dif * 4 + (n2(u * 5, v * 5) - 0.5) * 2, x, y), 0.75)
        if tag == 'eye': c = tone(ramp_, val + 1.4, x, y)
        # lichen: small pale crusts in colonies, speckles round them -- blended into the stone, never solid blobs
        if lichen and tag != 'hole':
            lc = n1(u * 1.7 + seed * 3.7 + 40, v * 1.7 + 11) + (n3(u * 6.0, v * 6.0) - 0.5) * 0.22
            thr = 1 - lichen * 0.34
            if lc > thr:
                lt = tone(lramp, 2.0 + dif * 2.0 + (lc - thr) * 10 + (n2(u * 9, v * 9) - 0.5) * 1.8, x, y)
                c = mix(c, lt, 0.6)
            elif lc > thr - 0.06 and h32(int(u * 14 + 999), int(v * 14 + 999), seed, 3) % 5 == 0:
                c = mix(c, tone(lramp, 2.6, x, y), 0.45)
        # moss: a thin cushion along what faces up (the top edge, the lips of cuts) and speckled at the foot
        if moss and tag != 'hole':
            mn = n2(u * 2.4 + seed * 5 + 80, v * 2.4) + (n3(u * 8, v * 8) - 0.5) * 0.3
            m = moss * ((1.5 if edge_up else 0.0) + max(0.0, 1 - v / 1.4) * 1.2 + max(0.0, -hy / (2 * px)) * 0.5) * mn
            if m > 0.5:
                c = mix(c, tone(MOSSR, 2.2 + dif * 2.6 + (n3(u * 7, v * 7) - 0.5) * 2.0, x, y), 0.8)
        # dark runs under the cuts and down from the top (rain-wash), in face space
        run = n3(u * 2.2 + seed * 9, 2.0)
        if run > 0.8 and tag != 'hole': c = mix(c, (14, 16, 14), min(0.3, (run - 0.8) * 2.5))
        return fogged(c, z, fogk)
    return sh

class Slab:
    """a slab standing on `base` (its front face's bottom centre): w wide, h tall, thick deep, leaning sideways by
    `lean` (radians, + = top to the right), tilted back by `tilt`, turned by `yaw` (+ = its right edge further away).
    Its front face is rasterised once; the back layers (same object id, so no outline inside) make the visible rim."""
    def __init__(s, rs, base, w, h, thick, outline, relief, lean=0.0, tilt=0.0, yaw=0.0, cls='wall', rim_v=None, **kw):
        s.rs, s.w, s.h = rs, w, h
        R = (math.cos(yaw), 0.0, math.sin(yaw))
        N = (-math.sin(yaw), 0.0, math.cos(yaw))
        U = tuple(math.cos(lean) * a + math.sin(lean) * b for a, b in zip((0.0, 1.0, 0.0), R))
        U = tuple(math.cos(tilt) * a + math.sin(tilt) * b for a, b in zip(U, N))
        s.R, s.U, s.N = R, U, N
        P0 = tuple(base[i] - R[i] * w / 2 for i in range(3))
        P1 = tuple(P0[i] + R[i] * w for i in range(3)); P3 = tuple(P0[i] + U[i] * h for i in range(3))
        s.P0, s.P1, s.P3 = P0, P1, P3
        face = stone_face(relief, outline, **kw)
        ramp_ = kw.get('ramp_', GRAVE); seed = kw.get('seed', 0); fogk = kw.get('fogk', 1.0)
        def front(x, y, a, b, z, wp):
            u, v = (a - 0.5) * w, b * h
            if not outline(u, v): return None
            return face(x, y, a, b, z, wp, U=u, V=v)
        s.obj = rs.obj()
        rs.quad(P0, P1, P3, front, obj=s.obj, cls=cls, cut=True)
        # the rim: how far the back face moves on screen decides how many layers it takes
        def corners(off): return [proj(*(p[i] + N[i] * off for i in range(3))) for p in (P0, P1, P3, tuple(P1[i] + P3[i] - P0[i] for i in range(3)))]
        a0, a1 = corners(0.0), corners(thick)
        shift = max(math.hypot(p[0] - q[0], p[1] - q[1]) for p, q in zip(a0, a1))
        n = max(1, int(shift / 0.8) + 1)
        # the rim faces the vanishing point: lit if that is to the right of the light (the stone stands right of centre)
        side_lit = base[0] > 0
        rv = rim_v if rim_v is not None else (4.6 if side_lit else 3.0)
        def rim(x, y, a, b, z, wp):
            u, v = (a - 0.5) * w, b * h
            if not outline(u, v): return None
            X_, Y_, Z_ = wp                                                           # world noise: no stripes across the layers
            val = rv + (n2(X_ * 1.6 + Z_ * 1.6 + 50, Y_ * 1.6) - 0.5) * 1.2 - 0.6 * max(0.0, 1 - v / 2.0)
            return fogged(tone(ramp_, val, x, y), z, fogk)
        for k in range(1, n + 1):
            off = thick * k / n
            Q0 = tuple(P0[i] + N[i] * off for i in range(3)); Q1 = tuple(P1[i] + N[i] * off for i in range(3)); Q3 = tuple(P3[i] + N[i] * off for i in range(3))
            rs.quad(Q0, Q1, Q3, rim, obj=s.obj, cls=cls, cut=True)

    def at(s, u, v, d=0.0):
        """the world point of face coordinates (u, v), d in front of the face"""
        return tuple(s.P0[i] + s.R[i] * (u + s.w / 2) + s.U[i] * v - s.N[i] * d for i in range(3))
    def screen(s, u, v):
        return proj(*s.at(u, v))
    def outline_px(s, outline, n=48):
        """the face's outline on screen (for the scene's hit polygons): sampled round the boundary"""
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n
            cu, cv = 0.0, s.h * 0.5
            du, dv = math.sin(a), math.cos(a)
            r = 0.0; step = max(s.w, s.h) / 200
            while outline(cu + du * (r + step), cv + dv * (r + step)) and r < max(s.w, s.h): r += step
            pts.append(s.screen(cu + du * r, cv + dv * r))
        return pts

# ---------------------------------------------------------------------------------------------------- earth, weeds
def heap(rs, X, Z, w, h, seed, Y0=-0.3, mat=None, cls='prop'):
    """earth heaped against something: a camera-facing card with a lumpy top, darker toward its foot, clods and
    dead grass on the crest"""
    def sh(x, y, s, t, z, wp):
        u = (s - 0.5) * 2
        top = (1 - abs(u) ** 1.6) * (0.75 + 0.5 * n1(s * 6 + seed * 3, seed)) + (n2(s * 22 + seed, 3.0) - 0.5) * 0.12
        if t > top: return None
        X_, Y_, Z_ = wp
        near_top = (top - t) * h
        v = 2.8 + 1.4 * (t / max(0.05, top)) - (0.9 if h32(int(X_ * 6 + 999), int(Y_ * 6 + 999), seed) % 7 == 0 else 0) + (n3(X_ * 2, Y_ * 2) - 0.5) * 1.2
        c = tone(MUD, v, x, y)
        if near_top < 0.35 and n1(X_ * 3 + seed, Y_ * 3) > 0.45: c = tone(STRAW, 2.0 + (n2(X_ * 9, Y_ * 2) - 0.5) * 3, x, y)
        elif mat: c = mat(c, X_, Y_, Z_, x, y)
        return fogged(c, z)
    rs.quad((X - w / 2, Y0, Z), (X + w / 2, Y0, Z), (X - w / 2, Y0 + h, Z), sh, cls=cls, cut=True)

def tuft(rs, X, Z, seed, h=1.2, n=7, ramp_=STRAW, spread=0.6, v0=2.6, w=0.06):
    """a tuft of dry grass: blades in two segments (a darker foot, a thinner paler tip) arching outward"""
    for i in range(n):
        a = (h01(seed, i, 1) - 0.5) * 2
        hh = h * (0.45 + 0.65 * h01(seed, i, 2))
        b0 = (X + a * 0.12, -0.05, Z + (h01(seed, i, 4) - 0.5) * 0.3)
        tip = (X + a * spread + (h01(seed, i, 3) - 0.5) * 0.3, hh * (1 - 0.25 * abs(a)), b0[2] + (h01(seed, i, 6) - 0.5) * 0.3)
        mid = (b0[0] + (tip[0] - b0[0]) * 0.35, hh * 0.6, (b0[2] + tip[2]) / 2)
        lit = 0.9 if a < 0 else 0.0
        c0 = tone(ramp_, v0 - 0.7 + (h01(seed, i, 5) - 0.5) * 1.2, 0, 0)
        c1 = tone(ramp_, v0 + 0.5 + lit + (h01(seed, i, 7) - 0.5) * 1.4, 0, 0)
        rs.line3(b0, mid, lambda x, y, s, t, z, wp, c=c0: fogged(c, z), w=w)
        rs.line3(mid, tip, lambda x, y, s, t, z, wp, c=c1: fogged(c, z), w=w * 0.5)

# ---------------------------------------------------------------------------------------------------- iron
def bar_v(rs, X, Y0, Y1, Z, w=0.32, rust=0.15, seed=0, obj=None, cls='prop'):
    """a round wrought-iron bar standing in the plane z = Z: shaded across (lit left edge, a dark core), rust blooms"""
    def sh(x, y, s, t, z, wp):
        a = s * 2 - 1
        v = 3.2 - a * 1.6 - a * a * 1.4
        if s < 0.2: v += 0.6
        c = tone(IRON, v, x, y)
        if n1(X * 4 + 20, wp[1] * 0.5 + seed) > 1 - rust * 0.6: c = tone(RUSTI, v - 0.4, x, y)
        return fogged(c, z)
    return rs.quad((X - w / 2, Y0, Z), (X + w / 2, Y0, Z), (X - w / 2, Y1, Z), sh, obj=obj, cls=cls)
RUSTI = ramp('#1e130d #2b1a11 #3b2416 #4b2e1c #5b3923')

def iron_line(rs, P0, P1, w=0.22, v0=2.6, sag=0.0, cls='prop'):
    return rs.line3(P0, P1, lambda x, y, s, t, z, wp: fogged(tone(IRON, v0 + (0.8 if (x + y) % 5 == 0 else 0), x, y), z), w=w, sag=sag, cls=cls)

def iron_curve(rs, pts, w=0.2, v0=2.6, cls='prop'):
    for a, b in zip(pts, pts[1:]): iron_line(rs, a, b, w, v0, cls=cls)

def scroll(cx, cy, Z, r0, turns=1.4, sign=1, start=0.0, n=40, plane='xy'):
    """points of a wrought-iron C-scroll (an Archimedean spiral) in the plane z = Z"""
    pts = []
    for i in range(n + 1):
        a = start + sign * 2 * math.pi * turns * i / n
        r = r0 * (1 - 0.8 * i / n)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r, Z))
    return pts

# ---------------------------------------------------------------------------------------------------- bare trees
BARK = ramp('#0c0b0a #131110 #1a1714 #221e1a #2b2620 #353028 #403930')
def tree(rs, X, Z, seed, h=22.0, trunk=1.1, lean=0.0, side=0, twig=0.03, limbs=4, fogk=1.0):
    """a bare, gnarled tree: a tapered trunk card (cylinder-shaded, furrowed, moss on the lit side), then limbs grown
    as chains of short bending segments that taper, throw side branches alternately and fork at their ends down to
    one-pixel twigs. side < 0 / > 0 sends the crown that way (to frame a picture)."""
    def trunk_sh(x, y, s, t, z, wp):
        X_, Y_, Z_ = wp
        wid = 1 - 0.45 * t + 0.25 * max(0.0, 0.12 - t) / 0.12                              # a flared foot
        a = (s - 0.5) * 2 / wid
        if abs(a) > 1 + (n2(Y_ * 3 + seed, seed) - 0.5) * 0.18: return None
        v = 2.8 - a * 1.5 - a * a * 1.2 + (n1(X_ * 6, Y_ * 1.4 + seed) - 0.5) * 1.2
        if n3(a * 2.5 + seed, Y_ * 0.9) > 0.64: v -= 1.1                                    # bark furrows
        if t < 0.1: v -= 1.0 * (1 - t / 0.1)
        c = tone(BARK, v, x, y)
        if a < -0.15 and n1(X_ * 2 + 9, Y_ * 2) > 0.5: c = tone(MOSSR, 1.4 + (1 - t) * 1.0 - a * 0.6, x, y)   # moss on the lit side
        return fogged(c, z, fogk)
    th = h * 0.36
    top = (X + lean * th, th, Z)
    rs.quad((X - trunk * 1.25, -0.25, Z), (X + trunk * 1.25, -0.25, Z), (X - trunk * 1.25 + lean * th, th + trunk, Z), trunk_sh, cls='prop', cut=True)
    k_ = [0]
    def seg(P, Q, w):
        lit = 0.6 if w > 0.25 else 0.0
        col = tone(BARK, 1.8 + lit + (h01(seed, k_[0]) - 0.5) * 0.8, 0, 0)
        rs.line3(P, Q, lambda x, y, s, t, z, wp, c=col: fogged(c, z, fogk), w=w, cls='prop')
    def grow(P, ang, w, length, gen):
        k_[0] += 1; kk = k_[0]
        n = max(3, int(length / max(0.5, w * 2.2)))
        step = length / n
        w_end = w * 0.55
        for i in range(n):
            if w < twig: return
            bend = (h01(seed, kk, i) - 0.5) * 0.55 + side * 0.03 * gen
            if gen >= 2: bend += 0.06 * math.copysign(1.0, math.sin(ang))                  # outer branches droop out
            ang += bend
            wz = (h01(seed, kk, i, 5) - 0.5) * step * 0.6
            Q = (P[0] + math.sin(ang) * step, P[1] + math.cos(ang) * step, P[2] + wz)
            wq = w + (w_end - w) / (n - i)
            seg(P, Q, w)
            # a side branch now and then, alternating sides
            if gen < 4 and i > 0 and i < n - 1 and h01(seed, kk, i, 9) < 0.5:
                sgn = 1 if (i + kk) % 2 else -1
                grow(Q, ang + sgn * (0.45 + 0.45 * h01(seed, kk, i, 3)), w * 0.55, length * (0.45 + 0.25 * h01(seed, kk, i, 4)), gen + 1)
            P, w = Q, wq
        if gen < 5 and w >= twig:                                                         # fork at the end
            for sgn in (-1, 1):
                grow(P, ang + sgn * (0.3 + 0.3 * h01(seed, kk, sgn + 7)), w * 0.72, length * 0.62, gen + 1)
    for j in range(limbs):
        a0 = -0.95 + 1.9 * (j + 0.5) / limbs + side * 0.3 + (h01(seed, j, 1) - 0.5) * 0.3 + lean * 0.4
        grow((top[0] + (j - limbs / 2) * trunk * 0.3, top[1], Z), a0, trunk * (0.75 if abs(a0) < 0.6 else 0.6), h * (0.26 + 0.08 * h01(seed, j, 2)), 0)

# ---------------------------------------------------------------------------------------------------- cobbles
def cobble_cell(X, Z, sc):
    gx, gz = X / sc, Z / sc
    ix, iz = math.floor(gx), math.floor(gz)
    best = (9.0, None); second = 9.0
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            cx_, cz_ = ix + dx, iz + dz
            px_ = cx_ + 0.2 + 0.6 * h01(cx_, cz_, 1); pz_ = cz_ + 0.2 + 0.6 * h01(cx_, cz_, 2)
            d = (gx - px_) ** 2 + (gz - pz_) ** 2
            if d < best[0]: second = best[0]; best = (d, (cx_, cz_, px_, pz_))
            elif d < second: second = d
    return math.sqrt(second) - math.sqrt(best[0]), best[1], gx, gz

def cobbles(x, y, s, t, z, wp, sc=0.85, v0=4.4, ramp_=GRAVE, moss=0.5):
    """irregular rounded cobbles (a jittered Voronoi in world X, Z): lit on their far-left shoulder, dark mud and moss
    in the joints, a few sunk or missing"""
    X, _, Z = wp
    edge, cell, gx, gz = cobble_cell(X, Z, sc)
    ex = 1.1 * Z / F / sc + 1.1 * Z * Z / (F * CAMH) / sc * 0.35                        # one pixel, roughly, in cell units
    cid = cell[:2]
    if edge < ex * 1.2 or h32(cid[0], cid[1], 5) % 23 == 0:                           # the joint (or a lost stone)
        c = tone(MUD, 2.4 + (n1(X * 3, Z * 3) - 0.5) * 2, x, y)
        if n2(X * 1.6, Z * 1.6) > 0.5 - moss * 0.3: c = tone(MOSSR, 2.4 + (n3(X * 5, Z * 5) - 0.5) * 2, x, y)
        return fogged(c, Z)
    dx, dz = gx - cell[2], gz - cell[3]
    lit = -dx * 1.3 + dz * 1.0                                                          # the far-left shoulder catches the sky
    v = v0 + (h32(cid[0], cid[1], 7) % 5 - 2) * 0.35 + lit * 1.2 - (0.8 if edge < ex * 2.6 else 0) + (n3(X * 4, Z * 4) - 0.5) * 0.7
    c = tone(ramp_, v, x, y)
    if n1(X * 0.5 + 9, Z * 0.5) > 0.62 and edge < 0.18: c = tone(MOSSR, 3.0 + lit, x, y)
    return fogged(c, Z)

# ---------------------------------------------------------------------------------------------------- the low mist
BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def ground_mist(img, rs, top=3.2, dens=0.024, banks=0.6, far=0.5, col=MIST, levels=7, sky_rows=None, wisps=(), glow=None, horizon=0.0):
    """lay a mist that hugs the ground over the finished picture: for every pixel the length of its ray inside the
    layer under `top` (world units), times a world-space bank pattern on the ground under it; plus `wisps`
    [(X0, X1, Y, Z, thick)] -- thin sheets hanging in front of things. Quantised to `levels` steps with a 4x4 ordered
    dither, so it stays crisp pixel art."""
    p = img.load()
    for y in range(H):
        for x in range(W):
            zz = rs.ZB[y][x]
            g_ = rs.G[y][x]
            if g_ is not None and g_[5] == 'sky': zz = 1e9                             # the sky card counts as sky
            dx, dy = ray(x, y)
            if zz >= 1e8:                                                             # the sky: haze thickening to the horizon
                Z = 600.0; Yp = CAMH + dy * Z
            else:
                Z = zz; Yp = CAMH + dy * Z
            if Yp >= top:
                t0 = None
            else:
                t0 = (CAMH - top) / (CAMH - Yp) if CAMH - Yp > 1e-6 else 1.0
            a = 0.0
            if t0 is not None and t0 < 1.0:
                L = Z * (1 - t0)
                bx, bz = dx * Z * (0.5 + 0.5 * t0), Z * (0.5 + 0.5 * t0)
                bank = 1 - banks + banks * (n2(bx * 0.06 + 40, bz * 0.11) * 0.7 + n3(bx * 0.17, bz * 0.3) * 0.5)
                a = 1 - math.exp(-dens * L * bank)
                a *= 1 - 0.55 * clamp((Yp - 0.0) / top) if zz < 1e8 else 1.0                # thinner over tall things
            a = max(a, far * clamp((Z - 60) / 260) if zz < 1e8 else far * (0.3 + 0.7 * clamp(y / HY) ** 2.2))
            if horizon:                                                               # sky and far ground melt together
                a = max(a, horizon * clamp(1 - abs(y + 0.5 - HY - 6) / 26.0) ** 1.5 * (1.0 if zz >= 1e8 else clamp((Z - 50) / 100)))
            for (X0, X1, Yw, Zw, th) in wisps:
                if zz > Zw and dx * Zw > X0 and dx * Zw < X1:
                    Yr = CAMH + dy * Zw
                    if abs(Yr - Yw) < th:
                        k = (1 - abs(Yr - Yw) / th) * n2(dx * Zw * 0.35 + Zw, Yr * 1.2) * 0.9
                        a = 1 - (1 - a) * (1 - k * 0.55)
            if a <= 0.01: continue
            q = math.floor(a * levels + BAYER4[y % 4][x % 4] / 16) / levels
            if q <= 0: continue
            q = min(0.92, q)
            c = p[x, y]; mc = col
            if glow:                                                                  # the mist lit brighter somewhere
                gx, gy, gr, gc, gk = glow
                d = math.hypot((x - gx) / gr, (y - gy) / (gr * 0.55))
                if d < 1: mc = tuple(int(col[i] + (gc[i] - col[i]) * gk * (1 - d) ** 1.5) for i in range(3))
            p[x, y] = tuple(int(c[i] + (mc[i] - c[i]) * q) for i in range(3))
    return img

# ---------------------------------------------------------------------------------------------------- the Aseprite palette
def write_gpl(path):
    """the Godgraveyard ramps (+ the shared overcast sky / haze / glow) as an Aseprite palette (hand touch-ups)"""
    from pal_day import SKY, HAZE
    bone = ramp('#1f1d17 #34302a #4c473c #655f50 #7e7766 #988f7a #ada48c')
    out = ['GIMP Palette', 'Name: Godgraveyard', 'Columns: 10', '#']
    for n, r in (('Sky', SKY), ('Haze', HAZE), ('Grave', GRAVE), ('Lime', LIME), ('Lichen', LICHEN), ('Moss', MOSSR), ('Mud', MUD),
                 ('Straw', STRAW), ('Heath', HEATH), ('Iron', IRON), ('Rust', RUSTI), ('Verdigris', VERDI), ('Bronze', BRONZE),
                 ('Gilt', GILT), ('Wax', WAX), ('Paper', PAPER), ('Bark', BARK), ('Bone', bone), ('Glow', GLOW)):
        for i, c in enumerate(r): out.append('%3d %3d %3d\t%s %d' % (c[0], c[1], c[2], n, i + 1))
    out.append('%3d %3d %3d\tMist' % MIST)
    open(path, 'w').write('\n'.join(out) + '\n')
