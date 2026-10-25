"""A painterly finishing pass for the procedural backgrounds: grime, wear and light, computed in WORLD / SURFACE
coordinates (never in screen space -- screen-space noise reads as camouflage). Run it on the shaded colours BEFORE the
generator draws its outlines, so the outlines stay crisp.

Per pixel the generator hands over (lists of rows, H x W):
  col  RGB tuple, the generator's shaded colour
  cls  'sky' | 'ground' | 'wall' | 'ceil' | 'prop' | 'emit' | None (None = leave the pixel exactly as it is)
  z    camera depth (None / >= 1e8 for the sky)
  wp   world position (X, Y, Z) or None (then rebuilt from z and the shared camera)
  nrm  unit normal facing the camera side, or None
  sid  surface id; grime streaks run down contiguous pixels of one sid, and edges between sids chip
What it does:
  * contact shadow on the ground around the bases of walls and props (distance on a 0.25 m ground grid)
  * a dark, damp band at the foot of every wall; moss there in the Growth variant, soot in the Decay one
  * soft shadow under anything that overhangs (a ledge, a sill, an awning: a nearer pixel right above), its length
    proportional to how far it sticks out
  * rain-wash streaks under every ledge, sill and top edge, their profile a 1D noise along the surface
  * chipped, lighter paint along the edges between surfaces
  * warm light spilling from emissive pixels (lit windows, lamps, glowing doorways), gathered into point lights in
    world space with Lambert falloff, plus a soft bloom around them
  * shadows tinted cool, low-frequency colour drift and a faint brush grain along each surface
  * everything fades with the generator's fog; the result is requantised with a 4x4 ordered dither
"""
import math
from collections import deque
from PIL import Image, ImageFilter
from common import make_noise, h32

CX, HY, F, CAMH = 533, 296, 300.0, 12.0
BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
OFF = 3000.0

def _n(seed):
    n = make_noise(1, seed, 509, 509)
    return lambda a, b: n(a + OFF, b + OFF)
nS, nL, nD, nR, nG, nB, nBr, nM = (_n(s) for s in (901, 902, 903, 904, 905, 906, 907, 908))

GRIME = {'base': (0.62, 0.58, 0.52), 'growth': (0.56, 0.64, 0.48), 'decay': (0.46, 0.42, 0.40)}
DAMP = {'base': (0.80, 0.78, 0.74), 'growth': (0.66, 0.76, 0.60), 'decay': (0.60, 0.56, 0.54)}
COOL = (0.93, 0.97, 1.04)
SHEEN = (150, 176, 172)                                                # the overcast sky in wet stone
MOSS = [(44, 62, 36), (62, 86, 46), (86, 112, 58)]

def _horiz(wp, nrm):
    """the horizontal coordinate along a vertical surface (streaks hang from it)"""
    if nrm and abs(nrm[0]) > 0.7: return wp[2]
    return wp[0]

def _peel(u, Y, Z, bricks, mortar):
    """plaster fallen off: the brickwork underneath (None = the plaster holds here)"""
    m = nM(u * 0.55, Y * 0.55) + 0.22 * (nS(u * 3.1, Y * 3.1) - 0.5)
    thr = 0.77 - 0.15 * math.exp(-Y / 1.0)
    if m < thr: return None
    if m < thr + 0.025: return 'rim'
    ps = Z / F                                                         # metres per pixel
    row = math.floor(Y / 0.24); off = (row % 2) * 0.27
    col_ = math.floor((u + off) / 0.54)
    c = bricks[h32(col_ + 999, row + 999, 13) % len(bricks)]
    if ps < 0.085:
        fv = (Y / 0.24) % 1; fu = ((u + off) / 0.54) % 1
        if fv < ps / 0.24 * 0.95 or fu < ps / 0.54 * 0.95: return mortar
    return c

def paint(col, cls, z, wp, nrm, sid, fog=lambda z: 0.0, variant='base', lights=(), light_gain=1.0, grime_gain=1.0, bloom=0.35,
          key=None, peel=None, crack=(), stain_gain=1.0, damp_gain=1.0, sheen_gain=1.0):
    """key: material keys per pixel (optional); peel: {key: ([brick colours], mortar)} -- plaster that falls off to brick;
    crack: keys that crack"""
    H, W = len(col), len(col[0])
    peel = peel or {}
    INF = 1e8
    # ---- world positions for every pixel that has a depth
    for y in range(H):
        rz, rw = z[y], wp[y]
        for x in range(W):
            if rw[x] is None and rz[x] is not None and rz[x] < INF:
                d = rz[x]; rw[x] = ((x + 0.5 - CX) * d / F, CAMH - (y + 0.5 - HY) * d / F, d)
    # ---- the ground contact shadow: distance from the bases of walls and props, on a 0.25 m grid
    occ = set()
    for y in range(H):
        for x in range(W):
            c = cls[y][x]
            if (c == 'wall' or c == 'prop') and wp[y][x] is not None and wp[y][x][1] < 0.45:
                occ.add((math.floor(wp[y][x][0] * 4), math.floor(wp[y][x][2] * 4)))
    dist = {c: 0 for c in occ}; q = deque(occ)
    while q:
        c = q.popleft(); d = dist[c]
        if d >= 7: continue
        for nb in ((c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)):
            if nb not in dist: dist[nb] = d + 1; q.append(nb)
    # ---- lights: emissive pixels gathered into world-space clusters
    acc = {}
    emit = Image.new('RGB', (W, H)); ep = emit.load()
    for y in range(H):
        for x in range(W):
            if cls[y][x] != 'emit': continue
            ep[x, y] = col[y][x]
            if x % 2 or y % 2 or wp[y][x] is None: continue
            X, Y, Z = wp[y][x]; n = nrm[y][x] or (0.0, 0.0, -1.0)
            X, Y, Z = X + n[0] * 0.35, Y + n[1] * 0.35, Z + n[2] * 0.35
            a = (2 * Z / F) ** 2 * (1 - fog(Z))
            r, g, b = col[y][x]; lum = (0.3 * r + 0.59 * g + 0.11 * b) / 255
            k = (math.floor(X / 1.5), math.floor(Y / 1.5), math.floor(Z / 1.5))
            e = acc.setdefault(k, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            w = a * lum
            e[0] += X * w; e[1] += Y * w; e[2] += Z * w; e[3] += r * w; e[4] += g * w; e[5] += b * w; e[6] += w
    L = []
    for e in acc.values():
        if e[6] < 0.02: continue
        w = e[6]; L.append((e[0] / w, e[1] / w, e[2] / w, (e[3] / w / 255, e[4] / w / 255, e[5] / w / 255), w, None))
    L += list(lights)
    light = [[None] * W for _ in range(H)]
    for (lx, ly, lz, lc, power, rad) in L:
        r = rad or min(10.0, math.sqrt(3.0 * power / 0.02))
        z0 = max(1.0, lz - r); z1 = lz + r
        xs = [CX + F * (lx + sx * r) / zz for sx in (-1, 1) for zz in (z0, z1)]
        ys = [HY + F * (CAMH - (ly + sy * r)) / zz for sy in (-1, 1) for zz in (z0, z1)]
        bx0, bx1 = max(0, int(min(xs))), min(W - 1, int(max(xs)) + 1)
        by0, by1 = max(0, int(min(ys))), min(H - 1, int(max(ys)) + 1)
        r2 = r * r
        for y in range(by0, by1 + 1):
            rw, rc, rl, rn = wp[y], cls[y], light[y], nrm[y]
            for x in range(bx0, bx1 + 1):
                p = rw[x]
                if p is None or rc[x] is None or rc[x] == 'sky' or rc[x] == 'emit': continue
                dx, dy, dz = lx - p[0], ly - p[1], lz - p[2]
                d2 = dx * dx + dy * dy + dz * dz
                if d2 > r2: continue
                d = math.sqrt(d2) or 1e-6
                n = rn[x]
                ndl = 0.65 if n is None else max(0.0, (n[0] * dx + n[1] * dy + n[2] * dz) / d)
                if ndl <= 0: continue
                fall = (1 - d / r) ** 2
                E = min(0.8, 3.0 * power / (d2 + 1.0)) * ndl * fall * light_gain
                if E < 0.004: continue
                cur = rl[x]
                if cur is None: rl[x] = [lc[0] * E, lc[1] * E, lc[2] * E]
                else: cur[0] += lc[0] * E; cur[1] += lc[1] * E; cur[2] += lc[2] * E
    # ---- recesses: a depth-based ambient occlusion (samples on a ring ~1.1 m wide around each pixel; only nearby
    #      occluders count, so nothing far in front throws a halo)
    RING = [(math.cos(a_ * math.pi / 4), math.sin(a_ * math.pi / 4)) for a_ in range(8)]
    ssao = [[0.0] * W for _ in range(H)]
    for y in range(H):
        rz, rc, ro = z[y], cls[y], ssao[y]
        for x in range(W):
            zz = rz[x]
            if zz is None or zz >= INF or rc[x] in (None, 'sky', 'emit'): continue
            R = max(2.0, min(40.0, 1.1 * F / zz)); hit = 0.0
            for k_, (cx_, cy_) in enumerate(RING):
                rr = R if k_ % 2 else R * 0.5
                sx, sy = int(x + cx_ * rr), int(y + cy_ * rr)
                if 0 <= sx < W and 0 <= sy < H and sid[sy][sx] != sid[y][x]:          # a surface never occludes itself
                    zs = z[sy][sx]
                    if zs is not None and zs < INF:
                        dz = zz - zs
                        if 0.25 < dz < 3.0: hit += 1.0 - dz / 3.0
            ro[x] = hit / 8
    glow = emit.filter(ImageFilter.GaussianBlur(7)).load() if bloom else None
    glow2 = emit.filter(ImageFilter.GaussianBlur(2)).load() if bloom else None
    # ---- per column, top to bottom: surface runs (streak sources) and the last ledge above
    gm, dm = GRIME[variant], DAMP[variant]
    out = [[None] * W for _ in range(H)]
    for x in range(W):
        run_sid, run_v0, ledge = None, 0.0, None
        prev_z = None
        for y in range(H):
            c0 = col[y][x]; k = cls[y][x]; p = wp[y][x]; zz = z[y][x]
            if k is None:
                out[y][x] = c0; run_sid = None; prev_z = zz; continue
            s = sid[y][x]
            if s != run_sid:
                run_sid = s; run_v0 = p[1] if p else 0.0
            if prev_z is not None and zz is not None and zz > prev_z + 0.3 and y > 0 and cls[y - 1][x] not in (None, 'sky', 'emit'):
                pp = wp[y - 1][x]
                if pp is not None: ledge = (pp[1], prev_z)
            prev_z = zz
            r, g, b = c0
            if k == 'sky' or p is None:
                if glow:
                    gr, gg, gb = glow[x, y]
                    r, g, b = r + gr * bloom * 0.6, g + gg * bloom * 0.6, b + gb * bloom * 0.6
                out[y][x] = (r, g, b); continue
            X, Y, Z = p; n = nrm[y][x]
            st = (1 - fog(Z))                                          # effects fade into the haze
            mk = key[y][x] if key else None
            if mk in peel and n is not None and abs(n[1]) < 0.5 and Z < 34:
                pc = _peel(_horiz(p, n), Y, Z, *peel[mk])
                if pc == 'rim': r, g, b = r * 0.72, g * 0.72, b * 0.74
                elif pc is not None:
                    a_ = st * st; f_ = 1 - a_
                    r, g, b = pc[0] * a_ + r * f_, pc[1] * a_ + g * f_, pc[2] * a_ + b * f_
            if mk in crack and st > 0.4:
                u_ = _horiz(p, n) if n is not None and abs(n[1]) < 0.5 else X
                if nD(u_ * 0.4 + 50, Y * 0.4) > 0.62 and abs(nS(u_ * 1.7 + 31, Y * 1.7 + 17) - 0.5) < 0.14 * Z / F * 1.7:
                    r, g, b = r * 0.62, g * 0.62, b * 0.64
            o = 0.0; grime = 0.0; damp = 0.0; chip = 0.0; sheen = 0.0
            vertical = n is not None and abs(n[1]) < 0.5
            if k == 'ground' or (n is not None and n[1] > 0.7):
                dd = dist.get((math.floor(X * 4), math.floor(Z * 4)))
                if dd is not None: o += 0.42 * (1 - dd / 7.5) ** 2
                wet = nD(X * 0.35, Z * 0.35)                           # damp patches on the ground
                if wet > 0.64:
                    damp += min(1.0, (wet - 0.64) * 6) * 0.6
                    if (0.3 * r + 0.59 * g + 0.11 * b) > 62 and st > 0.3: sheen = min(1.0, (wet - 0.64) * 5) * 0.22 * sheen_gain
                damp += max(0.0, nS(X * 1.3, Z * 1.3) - 0.68) * 1.2
                damp += max(0.0, nD(X * 0.12 + 70, Z * 0.12) - 0.55) * 1.3       # big trodden-in dirt patches
            if vertical and k != 'emit':
                o += 0.24 * math.exp(-Y / 0.6)                         # the foot of the wall
                o -= 0.10 * min(1.0, Y / 14.0)                         # ...and the open sky lights its top
                damp += 0.7 * math.exp(-Y / (0.35 + 0.6 * nD(_horiz(p, n) * 1.2, 7.0))) * (0.5 + 0.5 * nS(_horiz(p, n) * 2.0, Y * 2.0))
                if ledge is not None and ledge[1] < Z - 0.3:          # in the shadow of something sticking out above
                    reach = 0.5 + 1.6 * min(3.0, Z - ledge[1])
                    dv = ledge[0] - Y
                    if 0 <= dv < reach: o += 0.32 * (1 - dv / reach) ** 1.5
                if k == 'wall':                                        # rain-wash streaks hanging from the run's top
                    u = _horiz(p, n)
                    clus = max(0.0, nD(u * 0.35, 21.0) - 0.42) * 2.2       # streaks come in clusters
                    prof = (max(0.0, nS(u * 2.6, 3.0) - 0.55) * 2.6 + max(0.0, nL(u * 7.0, 11.0) - 0.68) * 2.0) * min(1.0, clus)
                    ln = 0.5 + 2.8 * nL(u * 0.8, 5.0)
                    dv = run_v0 - Y
                    if dv >= 0 and prof > 0: grime += min(1.0, prof) * math.exp(-dv / ln)
                    grime += 0.4 * stain_gain * max(0.0, nD(u * 0.5, Y * 0.5) - 0.5)    # large faded stains
            elif k == 'ceil':
                o += 0.12
            # chipped edges between surfaces (paint gone, lighter underneath), hashed on the surface
            if k in ('wall', 'prop') and st > 0.4:
                for (ax, ay) in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= ax < W and 0 <= ay < H and sid[ay][ax] != s and cls[ay][ax] not in (None, 'sky'):
                        hu = _horiz(p, n) if n else X
                        if h32(int(hu * 14 + 9999), int(Y * 14 + 9999), 31) % 6 == 0: chip = 1.0
                        break
            o += 0.75 * ssao[y][x]
            o = max(-0.12, min(0.7, o)) * st; grime = min(1.0, grime * grime_gain) * st * 0.8; damp = min(1.0, damp * damp_gain) * st * 0.4
            # colour drift + brush grain in surface coordinates
            if vertical: su, sv = _horiz(p, n), Y
            else: su, sv = X, Z
            drift = 0.05 * st
            r *= 1 + drift * (nR(su * 0.35, sv * 0.35) - 0.5)
            g *= 1 + drift * (nG(su * 0.35, sv * 0.35) - 0.5)
            b *= 1 + drift * (nB(su * 0.35, sv * 0.35) - 0.5)
            if vertical: br = nBr(su * 5.0, sv * 1.4)
            else: br = nBr(su * 1.4, sv * 5.0)
            m = 1 + 0.045 * st * (br - 0.5)
            r, g, b = r * m, g * m, b * m
            # grime and damp
            if grime: r, g, b = r * (1 - grime + grime * gm[0]), g * (1 - grime + grime * gm[1]), b * (1 - grime + grime * gm[2])
            if damp: r, g, b = r * (1 - damp + damp * dm[0]), g * (1 - damp + damp * dm[1]), b * (1 - damp + damp * dm[2])
            if variant == 'growth' and vertical and Y < 0.9 and nM(_horiz(p, n) * 3.0, Y * 3.0) > 0.52 + Y * 0.25 and st > 0.3:
                mc = MOSS[h32(int(X * 9 + 9999), int(Y * 9 + 9999), 3) % 3]
                r, g, b = (r + mc[0] * 2) / 3, (g + mc[1] * 2) / 3, (b + mc[2] * 2) / 3
            # occlusion, cool in the shadows
            if o < 0:
                r, g, b = r * (1 - o), g * (1 - o), b * (1 - o)
            elif o:
                t = min(1.0, o * 1.8)
                r *= (1 - o) * (1 + (COOL[0] - 1) * t); g *= (1 - o) * (1 + (COOL[1] - 1) * t); b *= (1 - o) * (1 + (COOL[2] - 1) * t)
            if chip: r, g, b = r * 1.16 + 5, g * 1.14 + 5, b * 1.10 + 4
            if sheen: r, g, b = r + (SHEEN[0] - r) * sheen, g + (SHEEN[1] - g) * sheen, b + (SHEEN[2] - b) * sheen
            # light spill (tints the surface's own colour, plus a little straight glow) and bloom
            lt = light[y][x]
            if lt:
                r += r * lt[0] * 1.5 + 60 * lt[0] * lt[0]; g += g * lt[1] * 1.5 + 60 * lt[1] * lt[1]; b += b * lt[2] * 1.5 + 60 * lt[2] * lt[2]
            if glow and k != 'emit':
                gr, gg, gb = glow[x, y]
                r, g, b = r + gr * bloom * 0.45, g + gg * bloom * 0.45, b + gb * bloom * 0.45
            elif glow:
                gr, gg, gb = glow2[x, y]
                r, g, b = r + gr * 0.15, g + gg * 0.15, b + gb * 0.15
            out[y][x] = (r, g, b)
    # ---- back to integers, snapped to steps of 4 (no dither: the generators' own dither stays the only one)
    res = [[None] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            c = out[y][x]
            res[y][x] = c if cls[y][x] is None else tuple(max(0, min(255, int(v / 4 + 0.5) * 4)) for v in c)
    return res

def face_engine(px, M, Z, UV, fog, glow, sky=('sky', 'skyline', 'cable'), skip=(), skip_px=(), **kw):
    """adapter for the Face-engine generators (crossroad / shed521 / burningbear): M = (material key, obj), Z = depth,
    UV = (u, v, face) on building faces, (wx, wz, None) on the ground, anything else on props"""
    H, W = len(px), len(px[0])
    CLS = [[None] * W for _ in range(H)]; WP = [[None] * W for _ in range(H)]; NRM = [[None] * W for _ in range(H)]
    SID = [[None] * W for _ in range(H)]; KEY = [[None] * W for _ in range(H)]; ZZ = [[None] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            m = M[y][x]
            if m is None or (x, y) in skip_px: continue
            k, obj = m; KEY[y][x] = k; uv = UV[y][x]; zz = Z[y][x]
            if k in skip: continue
            if k in sky: CLS[y][x] = 'sky'; continue
            ZZ[y][x] = zz
            if uv is not None and len(uv) == 3 and hasattr(uv[2], 'kind'):
                u, v, face = uv
                if face.kind == 'front': WP[y][x] = (u, v, face.const); NRM[y][x] = (0.0, 0.0, -1.0)
                else: WP[y][x] = (face.const, v, u); NRM[y][x] = (1.0 if face.const < 0 else -1.0, 0.0, 0.0)
                CLS[y][x] = 'emit' if px[y][x] in glow else 'wall'; SID[y][x] = (id(face), k)
            elif uv is not None and len(uv) == 3 and uv[2] is None:
                CLS[y][x] = 'ground'; WP[y][x] = (uv[0], 0.0, uv[1]); NRM[y][x] = (0.0, 1.0, 0.0); SID[y][x] = 'ground'
            else:
                if zz is None or zz >= 1e8: continue
                CLS[y][x] = 'emit' if px[y][x] in glow else 'prop'; SID[y][x] = (k, obj)
    return paint(px, CLS, ZZ, WP, NRM, SID, fog=fog, key=KEY, **kw)
