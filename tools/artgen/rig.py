"""A small renderer for character sprites (used by feral_toast.py).

Volumes (ellipsoids, tapered tubes, row-rounded polygons) are drawn into a TONE buffer -- material + a continuous light
value + the volume's draw order -- and only then turned into pixels:
  * cast shadows: a volume in front darkens what lies behind it, offset down-right (key light from the top left)
  * contact lines: the behind side of every overlap edge gets a little ambient occlusion
  * material texture (fabric weave, denim twill, leather, fur streaks, mottled skin, brushed metal), quantised onto the
    material's ramp with a 4x4 ordered dither
  * a warm dark outline per material instead of pure black
"""
import math
from PIL import Image
from common import make_noise, h32

def norm(v):
    l = math.sqrt(sum(c * c for c in v)) or 1
    return tuple(c / l for c in v)

LIGHT = norm((-0.5, -0.75, 0.55))
HALF = norm((LIGHT[0], LIGHT[1], LIGHT[2] + 1))
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
nF, nM, nL = make_noise(2, 101, 320, 320), make_noise(4, 102, 320, 320), make_noise(9, 103, 320, 320)

TEX = {
    'plain':   lambda x, y: (nF(x, y) - 0.5) * 0.05,
    'fabric':  lambda x, y: (nF(x * 1.6, y * 1.6) - 0.5) * 0.10 + (0.02 if (x + y) % 2 else -0.02),
    'denim':   lambda x, y: (nF(x * 1.5, y * 1.5) - 0.5) * 0.10 - (0.05 if (x - y) % 3 == 0 else 0),
    'leather': lambda x, y: (nM(x * 1.2, y * 1.2) - 0.5) * 0.10,
    'skin':    lambda x, y: (nM(x * 1.4, y * 1.4) - 0.5) * 0.12 + (nF(x, y) - 0.5) * 0.05,
    'fur':     lambda x, y: (nF(x * 0.7, y * 0.24) - 0.5) * 0.26 + (nM(x, y) - 0.5) * 0.08,
    'metal':   lambda x, y: (nL(x * 0.8, y * 0.8) - 0.5) * 0.07 + (0.05 if h32(x, y >> 2, 5) % 41 == 0 else 0),
    'wood':    lambda x, y: (nF(x * 0.35, y * 2.2) - 0.5) * 0.12,
    'wool':    lambda x, y: (nF(x * 2.0, y * 2.0) - 0.5) * 0.14 + (0.03 if (x // 2 + y) % 2 else -0.03),
}

class Mat:
    def __init__(self, ramp, tex='plain', amb=0.16, spec=0.0, outline=None):
        self.ramp, self.tex, self.amb, self.spec = ramp, TEX[tex], amb, spec
        self.outline = outline or tuple(int(c * 0.55) for c in ramp[0])

class Rig:
    def __init__(self, w, h):
        self.w, self.h, self.buf, self.n, self.groups = w, h, {}, 0, {}

    # ---- primitives -------------------------------------------------------------------------------------------
    def new(self, group=None):
        self.n += 1
        self.groups[self.n] = group if group is not None else self.n
        return self.n

    def shade(self, mat, n, lift=0.0):
        lam = max(0.0, n[0] * LIGHT[0] + n[1] * LIGHT[1] + n[2] * LIGHT[2])
        v = mat.amb + (1 - mat.amb) * lam
        v += 0.18 * max(0.0, n[0]) ** 3 * (1 - n[2])                 # a cool rim from the stage behind, right
        if mat.spec: v += mat.spec * max(0.0, n[0] * HALF[0] + n[1] * HALF[1] + n[2] * HALF[2]) ** 18
        return v + lift

    def put(self, x, y, mat, v, oid, fixed=None):
        x, y = int(math.floor(x)), int(math.floor(y))
        if 0 <= x < self.w and 0 <= y < self.h: self.buf[(x, y)] = [mat, v, oid, fixed]

    def fixed(self, x, y, color, oid=None):
        self.put(x, y, None, 0, oid or self.n, color)

    def ellipsoid(self, cx, cy, rx, ry, mat, rot=0.0, lift=0.0, flat=1.0, jag=0.0, group=None, vfun=None, clip=None):
        oid = self.new(group); c, s = math.cos(rot), math.sin(rot); R = max(rx, ry) * (1 + jag) + 1
        for y in range(int(cy - R) - 1, int(cy + R) + 2):
            for x in range(int(cx - R) - 1, int(cx + R) + 2):
                dx, dy = x + 0.5 - cx, y + 0.5 - cy
                u, w = (dx * c + dy * s) / rx, (-dx * s + dy * c) / ry
                d = u * u + w * w
                lim = 1.0 if not jag else 1 + jag * (nF(math.atan2(w, u) * 9 + cx, 3) - 0.35) * 2
                if d > lim or (clip and not clip(x, y)): continue
                d = min(d, 0.999)
                nu, nw = u * flat, w * flat
                n = norm((nu * c - nw * s, nu * s + nw * c, math.sqrt(1 - d)))
                v = self.shade(mat, n, lift) + (vfun(x, y, u, w) if vfun else 0)
                self.put(x, y, mat, v, oid)
        return oid

    def tube(self, a, b, ra, rb, mat, lift=0.0, bulge=None, folds=None, jag=0.0, group=None, clip=None):
        """tapered limb a->b; bulge(t) adds to the radius, folds(t, side) adds to the light (creases)"""
        oid = self.new(group)
        (ax, ay), (bx, by) = a, b
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1e-6; L = math.sqrt(L2)
        R = max(ra, rb) + 3
        for y in range(int(min(ay, by) - R), int(max(ay, by) + R) + 1):
            for x in range(int(min(ax, bx) - R), int(max(ax, bx) + R) + 1):
                px, py = x + 0.5 - ax, y + 0.5 - ay
                t = max(0.0, min(1.0, (px * dx + py * dy) / L2))
                r = ra + (rb - ra) * t + (bulge(t) if bulge else 0)
                if jag: r *= 1 + jag * (nF(t * L * 0.9 + ax, (px * dy - py * dx) / L * 0.5 + 7) - 0.4)
                ox, oy = px - dx * t, py - dy * t
                d = math.hypot(ox, oy)
                if d > r or (clip and not clip(x, y)): continue
                sx, sy = ox / r, oy / r
                n = (sx, sy, math.sqrt(max(0.0, 1 - sx * sx - sy * sy)))
                side = (ox * dy - oy * dx) / (L * r)
                v = self.shade(mat, n, lift) + (folds(t, side) if folds else 0)
                self.put(x, y, mat, v, oid)
        return oid

    def poly(self, pts, mat, lift=0.0, round_=0.9, tilt=0.0, group=None, vfun=None):
        """polygon filled row by row; each row is rounded like a cylinder across its own span"""
        oid = self.new(group)
        ys = [p[1] for p in pts]
        for y in range(int(math.floor(min(ys))), int(math.ceil(max(ys))) + 1):
            yc, xs = y + 0.5, []
            for i in range(len(pts)):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
                if (y0 <= yc < y1) or (y1 <= yc < y0): xs.append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                xl, xr = xs[i], xs[i + 1]; mid, half = (xl + xr) / 2, max(0.5, (xr - xl) / 2)
                for x in range(int(math.ceil(xl - 0.5)), int(math.floor(xr - 0.5)) + 1):
                    u = max(-0.98, min(0.98, (x + 0.5 - mid) / half)) * round_
                    n = norm((u, tilt, math.sqrt(max(0.05, 1 - u * u))))
                    v = self.shade(mat, n, lift) + (vfun(x, y) if vfun else 0)
                    self.put(x, y, mat, v, oid)
        return oid

    def stroke(self, pts, w, mat=None, v=0.5, color=None, group=None):
        oid = self.new(group)
        for (px, py) in pts:
            r = w / 2
            for y in range(int(py - r) - 1, int(py + r) + 2):
                for x in range(int(px - r) - 1, int(px + r) + 2):
                    if (x + 0.5 - px) ** 2 + (y + 0.5 - py) ** 2 <= r * r + 0.15:
                        if color: self.put(x, y, None, 0, oid, color)
                        else: self.put(x, y, mat, v, oid)
        return oid

    def darken(self, x, y, dv):
        e = self.buf.get((int(x), int(y)))
        if e and e[0] is not None: e[1] -= dv

    # ---- finishing ----------------------------------------------------------------------------------------------
    def render(self, outline=True, shadow=0.13, contact=0.10):
        buf, G = self.buf, self.groups
        tone = {k: e[1] for k, e in buf.items()}
        for (x, y), e in buf.items():
            if e[0] is None: continue
            g = G[e[2]]
            for dx, dy in ((-1, -2), (0, -2), (-2, -1)):                         # cast shadow from up-left
                q = buf.get((x + dx, y + dy))
                if q and q[2] > e[2] and G[q[2]] != g: tone[(x, y)] -= shadow; break
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):                    # contact line on the behind side
                q = buf.get((x + dx, y + dy))
                if q and q[2] > e[2] and G[q[2]] != g: tone[(x, y)] -= contact; break
        im = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0)); p = im.load()
        for (x, y), e in buf.items():
            mat, oid, fixed = e[0], e[2], e[3]
            if fixed: p[x, y] = fixed + (255,); continue
            r = mat.ramp
            v = tone[(x, y)] + mat.tex(x, y)
            i = v * (len(r) - 1) + (BAYER[y % 4][x % 4] / 16 - 0.47) * 0.85
            p[x, y] = r[max(0, min(len(r) - 1, int(round(i))))] + (255,)
        if outline:
            add = {}
            for (x, y), e in buf.items():
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (x + dx, y + dy)
                    if q in buf or not (0 <= q[0] < self.w and 0 <= q[1] < self.h): continue
                    if q not in add or add[q][0] < e[2]:
                        add[q] = (e[2], e[0].outline if e[0] else (18, 14, 12))
            for (x, y), (_, c) in add.items(): p[x, y] = c + (255,)
        return im
