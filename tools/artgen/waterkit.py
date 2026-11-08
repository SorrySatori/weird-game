"""Shared pieces for the waterside backgrounds (the Harbor, the Echo Drain Delta, Redmass Island) on raster3d.py.

WRaster = raster3d.Raster plus
  * water planes at any height (`water(Yp, ...)`, class 'water'): the reflection is marched up the screen column from the
    eye mirrored under THAT plane (raster3d's own mirror only knows the floor, Y 0), its column wobbled by a world-space
    ripple, and the water keeps no normal so the painterly pass doesn't put damp patches or contact shadows on it
  * wet ground still mirrors through `mirror(x, y, wp)` like Raster.render(mirror=...) (puddles on the planks)
  * `beam()`: a round timber / pipe / rope between two 3D points, shaded across its width (raster3d's line3 is flat),
    used for the crane, the lattice towers, posts, piles and pipes at any angle
Everything else (materials, fog) comes from shedkit.py."""
import math
from raster3d import Raster, proj, W, H, CX, HY, F, CAMH
from shedkit import wn, tone, mix, fogged, fog_of

LIGHT = (-0.45, 0.78, -0.43)                                                      # overcast: from above, a little left

class WRaster(Raster):
    def __init__(s):
        super().__init__()
        s.waters = {}                                                              # obj -> (plane Y, strength(X, Z), wobble)

    def water(s, Yp, X0, X1, Z0, Z1, shader, strength=lambda X, Z: 0.5, wobble=1.5):
        """a horizontal water surface at height Yp; strength(X, Z) = how much of the scene it mirrors (0..1)"""
        o = s.quad((X0, Yp, Z0), (X1, Yp, Z0), (X0, Yp, Z1), shader, cls='water')
        s.waters[o] = (Yp, strength, wobble)
        return o

    def _march(s, col, x, y, Zg, Yp):
        """the colour the reflected ray from the eye meets, walking up column x from row y (screen space: the ray's
        depth at row yy is t * Zg with t = 2d / (yy - HY + d), d = the pixel's distance under the horizon)"""
        d = F * (CAMH - Yp) / Zg
        lo = int(HY - d)
        for yy in range(y - 1, max(-1, lo), -1):
            t = 2 * d / (yy - HY + d) if (yy - HY + d) > 1e-6 else 99.0
            Z = t * Zg
            if s.ZB[yy][x] <= Z + 0.6:
                g = s.G[yy][x]
                if g is not None and g[5] == 'water': continue                     # the water never hides itself
                return col[yy][x]
        return col[max(0, min(H - 1, lo))][x]

    def reflect(s, col, mirror):
        out = {}
        for y in range(HY + 1, H):
            for x in range(W):
                g = s.G[y][x]
                if g is None or g[4] is None: continue
                if g[5] == 'water':
                    Yp, strength, wob = s.waters.get(g[1], (0.0, lambda X, Z: 0.5, 1.5))
                    X, _, Z = g[4]
                    k = strength(X, Z)
                    s.NB[y][x] = None
                    if k <= 0: continue
                    near = min(1.0, 22.0 / Z)
                    dx = int(round((wn(1, X * 0.7, Z * 2.2) - 0.5) * 2 * wob * (0.4 + near) + (wn(2, X * 2.5, Z * 7.0) - 0.5) * wob * near))
                    xx = max(0, min(W - 1, x + dx))
                    out[(x, y)] = (s._march(col, xx, y, Z, Yp), k)
                elif g[5] == 'ground' and mirror:
                    k = mirror(x, y, g[4])
                    if k <= 0: continue
                    out[(x, y)] = (s._march(col, x, y, g[4][2], 0.0), k)
        for (x, y), (c, k) in out.items():
            b = col[y][x]
            col[y][x] = tuple(int(b[i] * (1 - k) + c[i] * k * 0.82) for i in range(3))

    def render(s, ink, fog=lambda z: 0.0, post=None, overlay=None, mirror=None, **kw):
        # always run the reflection pass (water reflects even without a ground mirror)
        return super().render(ink, fog=fog, post=post, overlay=overlay, mirror=(mirror or (lambda x, y, wp: 0.0)), **kw)

    def beam(s, P0, P1, w, shader, cls='prop', w1=None, cap=False):
        """a round beam from P0 to P1, w world units thick (w1 at P1, if it tapers); shader gets s = along (0..1),
        t = across (-1 left .. 1 right on screen), the perspective-correct world point, and a rounded normal"""
        if P0[2] <= 0.5 or P1[2] <= 0.5: return s.obj()
        obj = s.obj()
        w1 = w if w1 is None else w1
        (ax, ay), (bx, by) = proj(*P0), proj(*P1)
        z0, z1 = P0[2], P1[2]
        r0, r1 = max(0.5, w * F / z0 / 2), max(0.5, w1 * F / z1 / 2)
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        if L2 < 1e-6: return obj
        L = math.sqrt(L2); px_, py_ = -dy / L, dx / L                             # the screen perpendicular
        lit_side = -1.0 if (px_ * LIGHT[0] - py_ * LIGHT[1]) > 0 else 1.0           # t = -1 is always the lit side
        x0 = max(0, int(min(ax - r0, bx - r1)) - 1); x1 = min(W - 1, int(max(ax + r0, bx + r1)) + 1)
        y0 = max(0, int(min(ay - r0, by - r1)) - 1); y1 = min(H - 1, int(max(ay + r0, by + r1)) + 1)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                qx, qy = x + 0.5 - ax, y + 0.5 - ay
                t = (qx * dx + qy * dy) / L2
                if cap: t = max(0.0, min(1.0, t))
                elif t < 0 or t > 1: continue
                r = r0 + (r1 - r0) * t
                d = (qx * px_ + qy * py_) - 0.0
                if cap:
                    ex, ey = qx - dx * t, qy - dy * t
                    d = math.copysign(math.hypot(ex, ey), ex * px_ + ey * py_)
                if abs(d) > r: continue
                b = d / r
                iz = (1 - t) / z0 + t / z1
                q = (t / z1) / iz
                wp = (P0[0] + (P1[0] - P0[0]) * q, P0[1] + (P1[1] - P0[1]) * q, P0[2] + (P1[2] - P0[2]) * q)
                nz = math.sqrt(max(0.0, 1 - b * b))
                zz = wp[2] - nz * (w + (w1 - w) * q) * 0.4
                nrm = (b * px_ * 0.9, -b * py_ * 0.9, -nz)
                s.put(x, y, zz, shader, obj, q, b * lit_side, wp, nrm, cls)
        return obj

def roundlit(t, s_=0.0):
    """how lit the round side of a beam is (t = across, -1..1) under the overcast light: brighter on the upper left"""
    nz = math.sqrt(max(0.0, 1 - t * t))
    return 0.55 * (-t * 0.55 + nz * 0.6) + 0.35

def timber(v0, r, grain=1.0, algae=None, seed=0):
    """a weathered round timber: lit across its width, a grain along it, darker wet foot; algae(wp) -> 0..1 greens it"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = v0 + 2.2 * (roundlit(t) - 0.5) + (wn(0, (X + Z) * 0.8 + seed, Y * 2.6) - 0.5) * 0.9 * grain
        if wn(3, (X + Z) * 3.0 + seed, Y * 0.5) > 0.72: v -= 0.8                    # cracks along the grain
        c = tone(r, v, x, y)
        if algae:
            a = algae(wp)
            if a > 0: c = mix(c, tone(ALGAE, v + 0.5, x, y), min(1.0, a))
        return fogged(c, z)
    return sh

def ironround(v0, r, rust=0.5, seed=0):
    """a round iron member (a pipe, a hook, a chain): lit across, rust in patches"""
    from shedkit import RUSTY
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = v0 + 2.4 * (roundlit(t) - 0.5) + (wn(1, (X + Z) * 1.1 + seed, Y * 1.1) - 0.5) * 0.7
        c = tone(r, v, x, y)
        m = wn(2, (X + Z) * 1.1 + t * 0.6 + seed, Y * 1.1 + t * 2.4) + (wn(3, (X + Z) * 5 + seed, Y * 5 + t * 3) - 0.5) * 0.3
        if m > 1 - rust * 0.5:                                                     # rust in blotches, darker than fresh paint
            c = mix(c, tone(RUSTY, v - 0.7, x, y), min(0.7, (m - (1 - rust * 0.5)) * 5))
        return fogged(c, z)
    return sh

from common import ramp
ALGAE = ramp('#121a10 #1a2614 #24341a #2f4320 #3c5426 #4c6630')                 # slime and weed at the waterline
SILT = ramp('#141310 #1d1b16 #27241d #322e25 #3e392e #4b4538 #5a5343')           # mud, silt, wet sediment
REED = ramp('#1a1c10 #262916 #34381d #444826 #565a30 #6a6c3c #7e7d4a')            # rushes, dry tips

def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def _mul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def _norm(a):
    l = math.sqrt(_dot(a, a)) or 1.0
    return (a[0] / l, a[1] / l, a[2] / l)

def frustum(rs, C0, C1, r0, r1, outer, inner, n=28, cls='prop', obj=None):
    """a truncated cone from C0 (radius r0) to C1 (radius r1), built from n flat facets (each a parallelogram clipped to
    its trapezoid). outer(x, y, u, v, z, wp, lit) shades the outside, inner(x, y, u, v, z, wp, depth) the inside seen
    through the open end: u = around (0..1), v = along (0 at C0 .. 1 at C1), lit = Lambert under the overcast light,
    depth = how far into the throat (0 at the wide end). The facets share one object id so no outlines run between them."""
    obj = obj or rs.obj()
    ax = _norm(_sub(C1, C0))
    ref = (0.0, 1.0, 0.0) if abs(ax[1]) < 0.9 else (1.0, 0.0, 0.0)
    e1 = _norm(_cross(ax, ref)); e2 = _cross(ax, e1)
    eye = (0.0, CAMH, 0.0)
    wide_is_1 = r1 >= r0
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        d0 = _add(_mul(e1, math.cos(a0)), _mul(e2, math.sin(a0))); d1 = _add(_mul(e1, math.cos(a1)), _mul(e2, math.sin(a1)))
        # the wide edge is the parallelogram's base, the narrow end its clipped far side
        (Cw, rw, Cn, rn) = (C1, r1, C0, r0) if wide_is_1 else (C0, r0, C1, r1)
        W0, W1 = _add(Cw, _mul(d0, rw)), _add(Cw, _mul(d1, rw))
        N0, N1 = _add(Cn, _mul(d0, rn)), _add(Cn, _mul(d1, rn))
        midW = _mul(_add(W0, W1), 0.5); midN = _mul(_add(N0, N1), 0.5)
        P3 = _add(W0, _sub(midN, midW))
        k = rn / rw if rw > 1e-6 else 1.0
        clip = lambda a, b, k=k: abs(a - 0.5) <= 0.5 * (1 - b * (1 - k)) + 0.02
        dm = _norm(_add(d0, d1))
        slope = (rw - rn) / (math.sqrt(_dot(_sub(Cw, Cn), _sub(Cw, Cn))) or 1.0)
        nout = _norm(_sub(dm, _mul(_norm(_sub(Cw, Cn)), slope)))                # outward normal of the facet
        cen = _mul(_add(midW, midN), 0.5)
        facing = _dot(nout, _sub(cen, eye)) < 0
        lit = max(0.0, _dot(nout, (-LIGHT[0], LIGHT[1], -LIGHT[2]) if False else _norm((LIGHT[0], LIGHT[1], LIGHT[2]))))
        def sh(x, y, a, b, z, wp, i=i, k=k, facing=facing, lit=lit):
            f = 1 - b * (1 - k)
            u = (i + max(0.0, min(1.0, (a - 0.5) / max(f, 1e-3) + 0.5))) / n
            v = b if not wide_is_1 else 1 - b
            if facing: return outer(x, y, u, v, z, wp, lit)
            return inner(x, y, u, v, z, wp, b)
        rs.quad(W0, W1, P3, sh, obj, clip=clip, cls=cls)
    return obj

def write_gpl(path):
    """the waterside ramps on top of the shared overcast palette (crossroad-overcast.gpl) for hand edits in Aseprite"""
    import harbor_ramps
    out = ['GIMP Palette', 'Name: Waterside', 'Columns: 8', '#']
    for n, r in harbor_ramps.RAMPS:
        for i, c in enumerate(r): out.append('%3d %3d %3d\t%s %d' % (c[0], c[1], c[2], n, i + 1))
    open(path, 'w').write('\n'.join(out) + '\n')

if __name__ == '__main__':
    import sys
    write_gpl(sys.argv[1] if len(sys.argv) > 1 else 'waterside.gpl')
