"""A tiny 3D rasteriser for the procedural interiors (the camera every background shares: 1067x600, VP (533, 296),
focal length 300, eye 12 units above the floor; the player is ~6.4 units tall, feet on y 534 = depth 15).

Planar quads, boxes, discs and 3D lines are rasterised with per-pixel depth, world position and normal; each object
has a shader(x, y, s, t, z, wp) -> colour (None = transparent) and a class for paintpass ('ground', 'wall', 'ceil',
'prop', 'emit'). render() shades, runs the painterly pass (grime, wear, light) and draws depth outlines.
Factored out of voxmarket_bg.py, which keeps its own copy (it ray-casts its shell)."""
import math
from PIL import Image
from paintpass import paint

W, H, CX, HY, F, CAMH = 1067, 600, 533, 296, 300.0, 12.0
INF = 9e9

def proj(x, y, z): return (CX + F * x / z, HY + F * (CAMH - y) / z)
def ray(x, y): return ((x + 0.5 - CX) / F, -(y + 0.5 - HY) / F)

def _pip(pts, u, v):
    inside = False; n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        if (y0 > v) != (y1 > v) and u < x0 + (x1 - x0) * (v - y0) / (y1 - y0): inside = not inside
    return inside

class Raster:
    def __init__(s):
        s.G = [[None] * W for _ in range(H)]                     # (shader, obj, s, t, wp, cls)
        s.ZB = [[INF] * W for _ in range(H)]
        s.NB = [[None] * W for _ in range(H)]
        s.n = 0

    def obj(s):
        s.n += 1; return s.n

    def put(s, x, y, z, shader, obj, a=0.0, b=0.0, wp=None, nrm=None, cls='prop'):
        if 0 <= x < W and 0 <= y < H and z < s.ZB[y][x]:
            s.ZB[y][x] = z; s.G[y][x] = (shader, obj, a, b, wp, cls); s.NB[y][x] = nrm

    def quad(s, P0, P1, P3, shader, obj=None, clip=None, cls='prop', cut=False):
        """the parallelogram P0 + s*(P1-P0) + t*(P3-P0), s, t in 0..1; cut=True makes pixels the shader returns None
        for transparent (it is then called once more while rasterising)"""
        obj = obj or s.obj()
        P2 = (P1[0] + P3[0] - P0[0], P1[1] + P3[1] - P0[1], P1[2] + P3[2] - P0[2])
        pts3 = (P0, P1, P2, P3)
        if min(p[2] for p in pts3) <= 0.5: return obj
        sp = [proj(*p) for p in pts3]
        e1 = (P1[0] - P0[0], P1[1] - P0[1], P1[2] - P0[2]); e2 = (P3[0] - P0[0], P3[1] - P0[1], P3[2] - P0[2])
        n = (e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0])
        nl = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1.0
        nu = (n[0] / nl, n[1] / nl, n[2] / nl)
        if nu[0] * P0[0] + nu[1] * (P0[1] - CAMH) + nu[2] * P0[2] > 0: nu = (-nu[0], -nu[1], -nu[2])   # face the camera
        x0, x1 = max(0, int(min(p[0] for p in sp))), min(W - 1, int(max(p[0] for p in sp)) + 1)
        y0, y1 = max(0, int(min(p[1] for p in sp))), min(H - 1, int(max(p[1] for p in sp)) + 1)
        ax = sorted(range(3), key=lambda i: abs(n[i]))[:2]
        det = e1[ax[0]] * e2[ax[1]] - e1[ax[1]] * e2[ax[0]] or 1e-9
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if not _pip(sp, x + 0.5, y + 0.5): continue
                dx, dy = ray(x, y)
                den = n[0] * dx + n[1] * dy + n[2]
                if abs(den) < 1e-9: continue
                t_ = (n[0] * P0[0] + n[1] * (P0[1] - CAMH) + n[2] * P0[2]) / den
                if t_ <= 0 or t_ >= s.ZB[y][x]: continue
                wp = (dx * t_, CAMH + dy * t_, t_)
                q = (wp[0] - P0[0], wp[1] - P0[1], wp[2] - P0[2])
                a = (q[ax[0]] * e2[ax[1]] - q[ax[1]] * e2[ax[0]]) / det
                b = (e1[ax[0]] * q[ax[1]] - e1[ax[1]] * q[ax[0]]) / det
                if clip and not clip(a, b): continue
                if cut and shader(x, y, a, b, t_, wp) is None: continue
                s.put(x, y, t_, shader, obj, a, b, wp, nu, cls)
        return obj

    def box(s, x0, x1, y0, y1, z0, z1, front, side, top=None, bottom=None, obj=None, cls='prop'):
        """an axis-aligned box: its face towards the camera (z0), the side facing the middle, the top if below the
        eye, the underside if above it"""
        obj = obj or s.obj()
        s.quad((x0, y0, z0), (x1, y0, z0), (x0, y1, z0), front, obj, cls=cls)
        if x1 < 0: s.quad((x1, y0, z0), (x1, y0, z1), (x1, y1, z0), side, obj, cls=cls)
        elif x0 > 0: s.quad((x0, y0, z0), (x0, y0, z1), (x0, y1, z0), side, obj, cls=cls)
        if top and y1 < CAMH: s.quad((x0, y1, z0), (x1, y1, z0), (x0, y1, z1), top, obj, cls=cls)
        if bottom and y0 > CAMH: s.quad((x0, y0, z0), (x1, y0, z0), (x0, y0, z1), bottom, obj, cls=cls)
        return obj

    def disc(s, cx, cy, z, r, shader, obj=None, cls='prop'):
        """a camera-facing disc (s, t = the offset from the centre in radii)"""
        obj = obj or s.obj()
        (sx, sy) = proj(cx, cy, z); rr = max(0.6, r * F / z)
        for y in range(int(sy - rr) - 1, int(sy + rr) + 2):
            for x in range(int(sx - rr) - 1, int(sx + rr) + 2):
                d = math.hypot(x + 0.5 - sx, y + 0.5 - sy) / rr
                if d <= 1:
                    a, b = (x + 0.5 - sx) / rr, (y + 0.5 - sy) / rr
                    nz = math.sqrt(max(0.0, 1 - a * a - b * b))
                    if shader(x, y, a, b, z, None) is None: continue                  # None = transparent
                    s.put(x, y, z - nz * r * 0.5, shader, obj, a, b, None, (a, -b, -nz), cls)
        return obj

    def sprite(s, img, X, Y0, Z, tint=None, cls='prop'):
        """paste a drawn RGBA sprite standing at (X, Y0, Z) (bottom-centre on that point) as a flat card at depth Z;
        tint(c, z) may fog it"""
        obj = s.obj(); (sx, sy) = proj(X, Y0, Z)
        w, h = img.size; bb = img.getbbox() or (0, 0, w, h)
        ox, oy = int(round(sx - w / 2)), int(round(sy - bb[3] + 1))                  # the lowest opaque row on the ground
        px = img.load()
        for j in range(h):
            for i in range(w):
                c = px[i, j]
                if c[3] < 128: continue
                col = c[:3] if tint is None else tint(c[:3], Z)
                s.put(ox + i, oy + j, Z, (lambda x, y, a, b, z, wp, col=col: col), obj, 0, 0, None, (0.0, 0.0, -1.0), cls)
        return obj

    def line3(s, P0, P1, shader, w=1.0, sag=0.0, n=0, cls='prop'):
        obj = s.obj(); n = n or int(math.dist(proj(*P0), proj(*P1))) + 2
        for i in range(n + 1):
            t = i / n
            P = (P0[0] + (P1[0] - P0[0]) * t, P0[1] + (P1[1] - P0[1]) * t - sag * math.sin(math.pi * t), P0[2] + (P1[2] - P0[2]) * t)
            if P[2] <= 0.5: continue
            (sx, sy) = proj(*P); rr = max(0.5, w * F / P[2] / 2)
            for y in range(int(sy - rr), int(sy + rr) + 1):
                for x in range(int(sx - rr), int(sx + rr) + 1):
                    s.put(x, y, P[2] - 0.01, shader, obj, t, 0, P, None, cls)
        return obj

    def render(s, ink, fog=lambda z: 0.0, post=None, overlay=None, **paint_kw):
        """shade every pixel, run paintpass, then darken the farther pixel wherever two objects meet at different
        depths. post(col, cls) draws 2D additions before the painterly pass (they get its light and grime),
        overlay(col) after it (crisp signs and lettering)."""
        col = [[ink] * W for _ in range(H)]
        cls = [[None] * W for _ in range(H)]; wpb = [[None] * W for _ in range(H)]; sid = [[None] * W for _ in range(H)]
        zp = [[None] * W for _ in range(H)]
        for y in range(H):
            for x in range(W):
                g = s.G[y][x]
                if g is None: continue
                shader, obj, a, b, wp, c = g
                cc = shader(x, y, a, b, s.ZB[y][x], wp)
                col[y][x] = ink if cc is None else cc
                cls[y][x] = c; wpb[y][x] = wp; sid[y][x] = obj; zp[y][x] = s.ZB[y][x]
        if post: post(col, cls)
        col = paint(col, cls, zp, wpb, s.NB, sid, fog=fog, **paint_kw)
        if overlay: overlay(col)
        img = Image.new('RGB', (W, H)); ip = img.load()
        for y in range(H):
            for x in range(W): ip[x, y] = col[y][x]
        out = img.copy(); op = out.load()
        for y in range(H - 1):
            for x in range(W - 1):
                g = s.G[y][x]
                if g is None: continue
                for (nx_, ny_) in ((x + 1, y), (x, y + 1)):
                    h_ = s.G[ny_][nx_]
                    if h_ is None or h_[1] == g[1]: continue
                    za, zb = s.ZB[y][x], s.ZB[ny_][nx_]
                    if abs(za - zb) < 0.6 + 0.02 * min(za, zb): continue
                    fx, fy = (x, y) if za > zb else (nx_, ny_)
                    c = ip[fx, fy]
                    k = 0.25 if min(za, zb) < 40 else 0.55
                    op[fx, fy] = tuple(int(ink[i] * (1 - k) + c[i] * k) for i in range(3))
        return out
