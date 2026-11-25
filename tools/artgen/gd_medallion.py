"""The Growth/Decay medallion (HUD, top left; ui/GrowthDecayIndicator.js), redrawn as native pixel art after its AI
picture (growthDecay.jpg), pass 2: as dense and saturated as the original. A worn copper disc with a wide band of
engraved runes; the field is split by an S-shaped bronze inlay into growth (teal with an engraved lattice, a thick mossy
segmented root, vines with leaves and fiddleheads, tall glowing blue fungi, a green gem) and decay (cracked rust earth,
dead brown fungi, a spine with ribs, a pile of bones, a skull, debris, an orange gem).
The split shows the balance: frame k is growth = 10*k % (decay = 100 - growth, see GrowthDecaySystem), the green takes
that share of the field and the gem of the leading side glows. Both halves are drawn over the whole field, so whichever
side spreads shows its own growth or rot there.
100x100 frames, 11 of them (growth 0, 10, ..., 100), shown at scale 1 at the top left.
python3 gd_medallion.py <outdir>  ->  gd_medallion.png (11 frames) + gd/<n>.png + gd_medallion.gpl"""
import sys, os, math
from PIL import Image
from common import INK, ramp, h32, make_noise

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
W = 100
CX = CY = 49.5
R_OUT, R_RIM, R_BAND, R_IN = 49.0, 46.0, 36.6, 35.0          # outer edge / rim to rune band / band to inner rim / field

COPPER = ramp('#140e0a #21180f #302315 #40301c #523e24 #66502e #7a6239 #8e7546 #a48a58 #bea36e')   # weathered bronze
BAND   = ramp('#0e0a08 #16100c #201812 #2a2018 #34281e')
RUNE   = ramp('#4a3a26 #64503a #7e6a4e #988462 #b09c78')
TEAL   = ramp('#0c1410 #111c16 #16241c #1c2c22 #223428 #283c2e')                                   # dusk behind the moss
GREEN  = ramp('#121c0e #1a2a14 #22381a #2c4620 #385426 #46622e #567038 #6a8044 #829456')            # moss (the menu's jungle)
BLUEM  = ramp('#1e2620 #2c3a32 #3e5046 #54685c #6e8474 #8aa08e #a8bcaa #cad8c8')                    # pale mycena caps
EARTH  = ramp('#160b06 #22110a #2e170d #3a1d10 #462413 #522b17 #5e331c')
BONE   = ramp('#24160c #3a2616 #523822 #6a4c32 #826246 #9a7a5c #b29474 #c8ae90')
DRYF   = ramp('#1a0e08 #2a1810 #3c2216 #54301e #6a3c22 #7e4628 #96562e #b06a3a')                    # rust (the menu's rust skin)
ROOT   = ramp('#120804 #1e0e08 #2c160c')
GEMG   = ramp('#0c1c14 #12281c #1a3a28 #245034 #326a44 #468a5a #64aa78 #92caa0 #d0ecd8')            # jade
GEMA   = ramp('#1e0c06 #36160a #52220e #6e3214 #8a441c #a65a28 #c0763a #d89a5c #f0c69a')            # oxide
EDGE   = (16, 9, 5)
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
nA, nB, nC = make_noise(3, 701, 120, 120), make_noise(7, 702, 120, 120), make_noise(2, 703, 120, 120)
L = (-0.55, -0.7, 0.45); _l = math.sqrt(sum(c * c for c in L)); L = tuple(c / _l for c in L)

def q(rmp, v, x, y):
    """a continuous ramp position -> a ramp colour with a 4x4 ordered dither"""
    i = v + (BAYER[y % 4][x % 4] / 16 - 0.47) * 0.8
    return rmp[max(0, min(len(rmp) - 1, int(round(i))))]

def polar(x, y):
    dx, dy = x + 0.5 - CX, y + 0.5 - CY
    return math.hypot(dx, dy), math.atan2(dy, dx)

def bead(r, a, r0, r1, lift=0.0):
    """light on a rounded ring between r0 and r1 (a bead, lit from the top left)"""
    t = max(-0.98, min(0.98, (r - (r0 + r1) / 2) / ((r1 - r0) / 2)))
    n = (math.cos(a) * t, math.sin(a) * t, math.sqrt(1 - t * t))
    lam = max(0.0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2])
    h = (L[0], L[1], L[2] + 1); hl = math.sqrt(sum(c * c for c in h)); h = tuple(c / hl for c in h)
    spec = max(0.0, n[0] * h[0] + n[1] * h[1] + n[2] * h[2]) ** 14
    return 0.12 + 0.72 * lam + 0.45 * spec + lift

# ---- runes: 28 glyphs, 3-4 x 5, engraved into the band ----------------------------------------------------------------
GLYPHS = [['100', '110', '101', '100', '100'], ['010', '111', '010', '010', '010'], ['101', '101', '010', '101', '101'],
          ['110', '101', '110', '100', '100'], ['010', '101', '111', '010', '010'], ['100', '100', '111', '001', '001'],
          ['011', '010', '110', '010', '011'], ['101', '111', '101', '100', '100'], ['111', '001', '011', '001', '001'],
          ['010', '100', '010', '001', '010'], ['1001', '1010', '1100', '1010', '1001'], ['1111', '1001', '0110', '0100', '0100'],
          ['0110', '1001', '0110', '1001', '0110'], ['1000', '1100', '1010', '1001', '1000'], ['0010', '0110', '1010', '0010', '0111'],
          ['1001', '1001', '1111', '1001', '1001']]

def rune_pixels():
    on = {}
    n = 28
    for k in range(n):
        a = -math.pi / 2 + (k + 0.5) * 2 * math.pi / n
        gx, gy = CX + math.cos(a) * 41.3, CY + math.sin(a) * 41.3
        g = GLYPHS[h32(k, 41) % len(GLYPHS)]
        w = len(g[0])
        x0, y0 = int(round(gx - w / 2)), int(round(gy - 2.5))
        for r, row in enumerate(g):
            for c, bit in enumerate(row):
                if bit == '1': on[(x0 + c, y0 + r)] = True
    return on

# ---- drawing helpers into a layer: dict (x, y) -> (ramp, tone) or ('fix', colour) ----------------------------------------
def catmull(pts, steps=10):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for s in range(steps):
            t = s / steps; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 +
                                    (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1])
    return out

def disc(layer, cx, cy, rx, ry, rmp, base, rng=2.0, rot=0.0, vfun=None):
    c, s = math.cos(rot), math.sin(rot)
    R = max(rx, ry) + 1
    for y in range(int(cy - R) - 1, int(cy + R) + 2):
        for x in range(int(cx - R) - 1, int(cx + R) + 2):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            u, w = (dx * c + dy * s) / rx, (-dx * s + dy * c) / ry
            d = u * u + w * w
            if d > 1: continue
            nz = math.sqrt(1 - d)
            lam = max(0.0, u * L[0] + w * L[1] + nz * L[2])
            layer[(x, y)] = (rmp, base + rng * (lam - 0.5) + (vfun(x, y, u, w) if vfun else 0))

def tube(layer, path, r0, r1, rmp, base, rng=2.2, rings=0, ring_dv=1.2):
    """a shaded tube along a path, radius r0 -> r1; rings = dark segment lines every n samples"""
    n = len(path)
    for i, (px, py) in enumerate(path):
        t = i / max(1, n - 1); r = r0 + (r1 - r0) * t
        (ax, ay), (bx, by) = path[max(0, i - 1)], path[min(n - 1, i + 1)]
        tx, ty = bx - ax, by - ay; tl = math.hypot(tx, ty) or 1; tx, ty = tx / tl, ty / tl
        nx, ny = -ty, tx
        for y in range(int(py - r) - 1, int(py + r) + 2):
            for x in range(int(px - r) - 1, int(px + r) + 2):
                ox, oy = x + 0.5 - px, y + 0.5 - py
                if ox * ox + oy * oy > r * r + 0.3: continue
                sd = (ox * nx + oy * ny) / max(0.5, r)                                   # -1..1 across the tube
                sd = max(-0.98, min(0.98, sd))
                nrm = (nx * sd, ny * sd, math.sqrt(1 - sd * sd))
                lam = max(0.0, nrm[0] * L[0] + nrm[1] * L[1] + nrm[2] * L[2])
                v = base + rng * (lam - 0.5)
                if rings and i % rings == 0: v -= ring_dv
                layer[(x, y)] = (rmp, v)

def stroke(layer, pts, w, rmp, base):
    for (px, py) in pts:
        r = w / 2
        for y in range(int(py - r) - 1, int(py + r) + 2):
            for x in range(int(px - r) - 1, int(px + r) + 2):
                if (x + 0.5 - px) ** 2 + (y + 0.5 - py) ** 2 <= r * r + 0.2:
                    lit = -(x + 0.5 - px) * 0.6 - (y + 0.5 - py) * 0.8
                    layer[(x, y)] = (rmp, base + lit * 0.9)

def leaf(layer, x, y, ang, size, base):
    disc(layer, x + math.cos(ang) * size * 0.9, y + math.sin(ang) * size * 0.9, size, size * 0.62, GREEN, base, 3.2, ang,
         vfun=lambda xx, yy, u, w: -1.0 if abs(w) < 0.12 and u > -0.6 else 0)                 # the midrib

def fiddlehead(layer, cx, cy, r0, sgn, base):
    sp = [(cx + math.cos(t * sgn) * r0 * (1 - t / 12.5), cy + math.sin(t * sgn) * r0 * (1 - t / 12.5)) for t in [k * 0.3 for k in range(40)]]
    stroke(layer, sp, 1.4, GREEN, base)

def mushroom(layer, x, y, rx, ry, stem_h, sw, rmp, base, glow_layer_bg=None, spots=0):
    """a cap at (x, y) on a stem going down stem_h px; gills under the cap"""
    stem = [(x + 0.4 * math.sin(k / max(1, stem_h) * 3), y + k) for k in range(0, int(stem_h) + 1)]
    tube(layer, stem, sw, sw * 1.15, rmp, base - 0.4, 2.0)
    disc(layer, x, y + ry * 0.55, rx * 0.88, ry * 0.42, rmp, base - 2.2, 1.0)                  # the gills' underside
    for k in range(int(-rx * 0.8), int(rx * 0.8) + 1, 2):
        layer[(int(x + k), int(y + ry * 0.62))] = (rmp, base - 3.0)                            # gill lines
    disc(layer, x, y, rx, ry, rmp, base + 0.4, 3.4, vfun=lambda xx, yy, u, w: 0.0 if w < 0.55 else -1.4)
    for k in range(spots):
        sx, sy = x - rx * 0.5 + (h32(k, int(x)) % 100) / 100 * rx, y - ry * 0.55 + (h32(k, int(y)) % 40) / 100 * ry
        layer[(int(sx), int(sy))] = ('fix', rmp[-1])

def bone(layer, a, b, w, base):
    tube(layer, catmull([a, b], 14), w, w, BONE, base, 2.6)
    for (ex, ey) in (a, b):
        ux, uy = b[0] - a[0], b[1] - a[1]; ul = math.hypot(ux, uy) or 1; nx, ny = -uy / ul, ux / ul
        disc(layer, ex + nx * w * 0.7, ey + ny * w * 0.7, w * 0.95, w * 0.95, BONE, base + 0.4, 2.6)
        disc(layer, ex - nx * w * 0.7, ey - ny * w * 0.7, w * 0.95, w * 0.95, BONE, base, 2.6)

# ---- the growth half --------------------------------------------------------------------------------------------------
def growth_layer():
    G = {}
    for y in range(W):
        for x in range(W):
            v = 1.8 + (nA(x, y) - 0.5) * 1.6 + (nB(x, y) - 0.5) * 1.2
            if (x + y) % 7 == 0 or (x - y) % 7 == 0: v -= 0.55                                # an engraved lattice
            elif (x + y) % 7 == 1 or (x - y) % 7 == 1: v += 0.3
            G[(x, y)] = (TEAL, v)
    # a carpet of small leaves over the whole field (what shows when growth spreads over the decay side)
    for k in range(120):
        x, y = 14 + h32(k, 31) % 72, 14 + h32(k, 32) % 72
        leaf(G, x, y, (h32(k, 33) % 628) / 100, 1.2 + (h32(k, 34) % 3) * 0.3, 2.6 + (h32(k, 35) % 3) * 0.5)
    for k in range(28):                                                                      # thin creeping stems in between
        x, y = 14 + h32(k, 36) % 72, 14 + h32(k, 37) % 72
        a = (h32(k, 38) % 628) / 100
        stroke(G, catmull([(x, y), (x + math.cos(a) * 5, y + math.sin(a) * 5), (x + math.cos(a + 0.8) * 9, y + math.sin(a + 0.8) * 9)], 6), 1.0, GREEN, 3.0)
    # vines with bigger leaves and curled fronds
    for pts, curl in (([(18, 70), (22, 58), (17, 46), (24, 34), (30, 22)], (31, 20, 3.2, 1)),
                      ([(38, 86), (34, 76), (40, 66), (36, 56)], (36, 54, 3.0, -1)),
                      ([(56, 20), (62, 28), (60, 38), (66, 46)], (67, 47, 2.8, 1)),
                      ([(48, 86), (54, 78), (52, 68)], (53, 66, 2.6, -1)),
                      ([(70, 60), (76, 66), (84, 62)], (85, 61, 2.4, 1))):
        path = catmull(pts, 12)
        stroke(G, path, 2.0, GREEN, 5.0)
        for i in range(4, len(path) - 2, 5):
            (x0, y0), (x1, y1) = path[i - 1], path[i + 1]
            ang = math.atan2(y1 - y0, x1 - x0) + (1.2 if (i // 5) % 2 else -1.2)
            leaf(G, path[i][0], path[i][1], ang, 2.5, 5.6)
        fiddlehead(G, *curl, 5.8)
    # the thick mossy root, segmented, curving up the growth side
    root = catmull([(46, 88), (40, 76), (28, 66), (24, 52), (30, 40)], 14)
    tube(G, root, 3.8, 2.4, GREEN, 4.8, 3.6, rings=4, ring_dv=2.0)
    for i in range(2, len(root), 6):                                                         # moss tufts on its back
        G[(int(root[i][0]) - 2, int(root[i][1]) - 2)] = (GREEN, 7.6)
    # tall glowing blue fungi: a light on the ground round them, then stems and caps
    FUNGI = ((34, 22, 7.6, 4.0, 15, 1.6), (21, 40, 5.6, 3.0, 11, 1.3), (44, 50, 4.4, 2.4, 8, 1.1),
             (20, 74, 3.6, 2.0, 6, 0.9), (30, 82, 2.8, 1.6, 4, 0.8), (14, 58, 2.6, 1.4, 4, 0.7))
    for (mx, my, rx, ry, sh, sw) in FUNGI:
        for y in range(int(my - rx - 3), int(my + sh + 4)):
            for x in range(int(mx - rx - 5), int(mx + rx + 6)):
                d = math.hypot((x + 0.5 - mx) / (rx + 2), (y + 0.5 - my) / (rx + 2) * 0.8)
                e = G.get((x, y))
                if e and e[0] is TEAL and d < 1.4: G[(x, y)] = (TEAL, e[1] + (1.4 - d) * 2.0)
    for (mx, my, rx, ry, sh, sw) in FUNGI:
        mushroom(G, mx, my, rx, ry, sh, sw, BLUEM, 4.6, spots=int(rx / 2))
    return G

# ---- the decay half ---------------------------------------------------------------------------------------------------
def decay_layer():
    D = {}
    for y in range(W):
        for x in range(W):
            v = 2.4 + (nA(x + 40, y) - 0.5) * 1.8 + (nC(x, y) - 0.5) * 1.4
            ridge = abs(nB(x * 1.6 + 30, y * 1.6) - 0.5)                                      # cracks in the dry earth
            if ridge < 0.03: v -= 1.8
            elif ridge < 0.06: v += 0.6
            D[(x, y)] = (EARTH, v)
    # debris over the whole field: bone chips, pebbles, tiny dead caps (what shows when decay spreads)
    for k in range(110):
        x, y = 14 + h32(k, 1) % 72, 14 + h32(k, 2) % 72
        kind = h32(k, 3) % 5
        if kind < 2:
            a = (h32(k, 4) % 628) / 100
            bone(D, (x, y), (x + math.cos(a) * 4, y + math.sin(a) * 4), 0.8, 4.2)
        elif kind == 2: disc(D, x, y, 1.4, 1.0, EARTH, 5.0, 2.0)
        elif kind == 3: disc(D, x, y, 1.8, 1.1, DRYF, 3.6, 2.6)
        else: D[(x, y)] = (BONE, 5.0); D[(x + 1, y)] = (BONE, 3.4)
    for pts in ([(52, 20), (60, 26), (57, 36)], [(86, 42), (78, 48), (82, 56)], [(56, 88), (62, 80), (58, 72)],
                [(14, 40), (22, 46), (18, 56)], [(26, 78), (34, 72), (30, 64)]):
        stroke(D, catmull(pts, 10), 1.2, ROOT, 1.4)
    # dead brown fungi, top right
    for (mx, my, rx, ry, sh, sw) in ((70, 20, 7.8, 3.8, 13, 1.7), (82, 32, 5.2, 2.7, 9, 1.3), (60, 30, 4.0, 2.2, 7, 1.1)):
        mushroom(D, mx, my, rx, ry, sh, sw, DRYF, 4.4, spots=3)
    # a spine with ribs curving off it
    sp = catmull([(56, 42), (64, 46), (72, 52), (78, 62)], 14)
    for i in range(0, len(sp) - 1, 4):
        (x0, y0) = sp[i]; (x1, y1) = sp[min(i + 2, len(sp) - 1)]
        ang = math.atan2(y1 - y0, x1 - x0)
        if i % 8 == 0:                                                                      # a pair of ribs
            for side in (-1, 1):
                rb = [(x0 + math.cos(ang + side * 1.6 + t * side * 0.9) * (2 + t * 7), y0 + math.sin(ang + side * 1.6 + t * side * 0.9) * (2 + t * 7))
                      for t in [k / 8 for k in range(9)]]
                tube(D, rb, 1.1, 0.7, BONE, 4.4, 2.4)
        disc(D, x0, y0, 2.4, 1.8, BONE, 4.8, 3.0, ang)
        D[(int(x0 + math.cos(ang) * 2.4), int(y0 + math.sin(ang) * 2.4))] = (BONE, 0.6)
    # a pile of bones, a skull
    for (a, b, w) in (((58, 76), (80, 66), 1.9), ((63, 86), (74, 60), 1.8), ((72, 82), (86, 74), 1.5), ((52, 66), (60, 58), 1.2),
                      ((80, 48), (86, 56), 1.1)):
        bone(D, a, b, w, 4.6)
    disc(D, 66, 70, 4.6, 4.0, BONE, 4.8, 3.2)                                                # the skull
    disc(D, 67, 74, 3.0, 1.8, BONE, 3.8, 2.4)                                                # its jaw
    for (x, y, v) in ((64, 70, 0.0), (65, 70, 0.0), (64, 71, 0.4), (68, 70, 0.0), (69, 70, 0.2), (68, 71, 0.4), (66, 72, 0.6),
                      (65, 75, 1.0), (67, 75, 1.0), (69, 75, 1.0)):
        D[(x, y)] = (BONE, v)
    return D

GL, DL = growth_layer(), decay_layer()
RUNES = rune_pixels()

# ---- the boundary: an S, tilted; growth on its left. `off` is solved per frame for the share of the field ---------
def xb(y, off):
    t = (CY - (y + 0.5)) / R_IN
    return CX + off + 7.5 * math.sin(math.pi * t) + 9.0 * t

FIELD = [(x, y) for y in range(W) for x in range(W) if polar(x, y)[0] < R_IN]

def solve(share):
    if share <= 0: return -200.0
    if share >= 1: return 200.0
    lo, hi = -60.0, 60.0
    for _ in range(40):
        mid = (lo + hi) / 2
        n = sum(1 for (x, y) in FIELD if x + 0.5 < xb(y, mid))
        if n / len(FIELD) < share: lo = mid
        else: hi = mid
    return (lo + hi) / 2

# ---- the gems -------------------------------------------------------------------------------------------------------
def gem(p, gx, gy, rmp, lvl):
    """a cut diamond 15x19 in a copper bezel; lvl 0..1 = how much it glows"""
    hw, hh = 7.0, 9.0
    up = lvl * 2.6
    if lvl > 0.3:                                                                                   # the halo on the field
        reach = 1.0 + lvl * 0.9
        for y in range(int(gy - hh * reach) - 1, int(gy + hh * reach) + 2):
            for x in range(int(gx - hw * reach) - 1, int(gx + hw * reach) + 2):
                d = abs(x + 0.5 - gx) / hw + abs(y + 0.5 - gy) / hh
                if 1.08 < d < reach and polar(x, y)[0] < R_IN:
                    c = p[x, y]; m = rmp[6]
                    k = 0.5 * lvl * (1 - (d - 1.08) / (reach - 1.08))
                    if (x + y) % 2 == 0 or k > 0.25:
                        p[x, y] = tuple(int(c[i] + (m[i] - c[i]) * k) for i in range(3)) + (255,)
    for y in range(int(gy - hh) - 1, int(gy + hh) + 2):
        for x in range(int(gx - hw) - 1, int(gx + hw) + 2):
            u, w = (x + 0.5 - gx) / hw, (y + 0.5 - gy) / hh
            d = abs(u) + abs(w)
            if d > 1.0: continue
            if d > 0.86:
                p[x, y] = (COPPER[8] if u + w < -0.2 else (COPPER[5] if u + w < 0.3 else COPPER[2])) + (255,); continue
            if d < 0.38: v = 5.4 - (u + w) * 1.6                                                          # the table
            elif u <= 0 and w <= 0: v = 4.6
            elif u > 0 and w <= 0: v = 3.4
            elif u <= 0 and w > 0: v = 2.6
            else: v = 1.4
            if abs(d - 0.38) < 0.07 or abs(u) < 0.045 or abs(w) < 0.035: v -= 0.7                      # facet edges
            if 0.55 < d < 0.62 and u + w < 0: v += 0.8                                                  # an inner reflection
            p[x, y] = q(rmp, v + up - 1.0, x, y) + (255,)
    tx, ty = int(gx - 2), int(gy - 4)
    p[tx, ty] = (rmp[8] if lvl > 0.4 else rmp[6]) + (255,)                                              # the glint
    if lvl > 0.6:
        p[tx + 1, ty] = rmp[7] + (255,); p[tx, ty + 1] = rmp[7] + (255,); p[tx - 1, ty - 1] = rmp[8] + (255,)

GEM_G, GEM_A = (46.0, 28.5), (53.5, 70.5)

def frame(growth):
    off = solve(growth / 100)
    im = Image.new('RGBA', (W, W), (0, 0, 0, 0)); p = im.load()
    for y in range(W):
        for x in range(W):
            r, a = polar(x, y)
            if r >= R_OUT + 0.6: continue
            if r >= R_OUT - 0.4: p[x, y] = EDGE + (255,); continue
            if r >= R_RIM:                                                                           # the outer rim, worn copper
                v = bead(r, a, R_RIM, R_OUT - 0.4) * 8.0 + (nC(x, y) - 0.5) * 1.4
                if h32(x, y, 21) % 13 == 0: v -= 1.8                                                 # dents and wear
                p[x, y] = q(COPPER, v, x, y) + (255,); continue
            if r >= R_BAND:                                                                          # the rune band, recessed
                v = 2.0 + (nA(x, y) - 0.5) * 1.6
                tl = math.cos(a) * L[0] + math.sin(a) * L[1]                                         # > 0 = the top-left side
                if R_RIM - r < 1.4 and tl > 0.1: v -= 1.6
                if r - R_BAND < 1.4 and tl < -0.1: v -= 1.6
                if (x, y) in RUNES: p[x, y] = q(RUNE, 2.4 + tl * 1.6 + (nC(x, y) - 0.5) * 1.2, x, y) + (255,); continue
                if (x - 1, y - 1) in RUNES: v -= 1.4                                                 # engraved: a dark lip
                elif (x + 1, y + 1) in RUNES: v += 0.8                                               # and a lit one
                p[x, y] = q(BAND, v, x, y) + (255,); continue
            if r >= R_IN:                                                                            # the inner rim
                p[x, y] = q(COPPER, bead(r, a, R_IN, R_BAND) * 7.0 - 0.6, x, y) + (255,); continue
            # the field
            side = GL if x + 0.5 < xb(y, off) else DL
            e = side[(x, y)]
            if e[0] == 'fix': p[x, y] = e[1] + (255,); continue
            rmp, v = e
            tl = math.cos(a) * L[0] + math.sin(a) * L[1]
            if R_IN - r < 3.0 and tl > 0.15: v -= (3.0 - (R_IN - r)) * 0.6                           # the rim's shadow
            p[x, y] = q(rmp, v, x, y) + (255,)
    # the copper inlay along the boundary
    if 0 < growth < 100:
        for y in range(W):
            bx = xb(y, off)
            for (x, c) in ((int(math.floor(bx)) - 1, COPPER[8]), (int(math.floor(bx)), COPPER[4]), (int(math.floor(bx)) + 1, None)):
                if polar(x, y)[0] >= R_IN - 0.3: continue
                if c: p[x, y] = c + (255,)
                else:
                    cc = p[x, y]; p[x, y] = tuple(int(ch * 0.55) for ch in cc[:3]) + (255,)                # its shadow
    gem(p, *GEM_G, GEMG, max(0.0, min(1.0, (growth - 20) / 80)))
    gem(p, *GEM_A, GEMA, max(0.0, min(1.0, (80 - growth) / 80)))
    return im


if __name__ == '__main__':
    os.makedirs(f'{OUT}/gd', exist_ok=True)
    frames = [frame(g) for g in range(0, 101, 10)]
    sheet = Image.new('RGBA', (W * len(frames), W), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        im.save(f'{OUT}/gd/{i}.png'); sheet.paste(im, (i * W, 0))
    sheet.save(f'{OUT}/gd_medallion.png')
    ALL = [INK, EDGE] + COPPER + BAND + RUNE + TEAL + GREEN + BLUEM + EARTH + BONE + DRYF + ROOT + GEMG + GEMA
    seen, rows = set(), []
    for c in ALL:
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/gd_medallion.gpl', 'w').write('GIMP Palette\nName: gd_medallion\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT)
