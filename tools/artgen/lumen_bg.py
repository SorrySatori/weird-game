"""The Lumen Directorate headquarters seen from its garden plaza (LumenDirectorateScene), 1067x600, overcast day, the
shared camera (raster3d.py). After the old art (LumenDirectorate.png, a sunset-purple glowing palace): the same
composition, re-keyed to the overcast day -- the warm window light stays as the Directorate's signature, muted.

  the palace   pale limestone, frontal: the central pavilion with the glowing glazed portal, the great traceried
               window and a steep gable with a rose window and a brass sun finial; pinnacled piers; two side bays of
               lit lancets under a balustrade; set-back wings with a loggia arcade, each crowned by a glass
               conservatory dome (plants inside); round end turrets with patina spires. Ivy is TRAINED over all of
               it -- clipped panels on the piers, festoons under every parapet ("living architecture")
  the terrace  a rusticated retaining wall with the archive vent (the Gang of Lamps eavesdrop spot), a flight of steps
               between cheek walls and urns, clipped hedges and flower rows along the facade, lamps
  the plaza    pale setts with a flagged runner up to the steps and a brass sun inlaid in it; two raised stone beds in
               front (flower rows, a spiral of root-tendrils Verrik coaxed into shape, the sealed cold-frame on the
               left one, a clipped shrub on the right one), tall cast-iron lamps; stucco city blocks at the sides
Variants: growth (spring riot: ivy runs wild over the windows and blooms, beds overflow and spill over their walls, the
spirals leaf out, moss in the joints) and decay (dead brown ivy, wilted sallow beds -- the left one blighted grey --
cracked and missing panes, fewer lights, a lamp out, dead leaves on the paving).

    python3 lumen_bg.py <outdir> [base|growth|decay]   ->  lumen.png / lumen_growth.png / lumen_decay.png
                                                          + lumen_points.json (canvas fixed points)
                                                          growth also writes surplus_bloom.png (the harvestable bloom,
                                                          cut out of a second render, top-left printed + in the json)
Fixed points (canvas): the portal x 502..564, y 260..384 (door zone); the vent in the retaining wall x ~300..346,
y ~407..424; the left bed's top x ~110..355, y ~446..497 (the blighted bed in decay); the walk line y 534 runs in
front of both beds (their fronts stand at depth 15.8)."""
import sys, os, math, json
from PIL import Image
from common import h32, ramp
from shedkit import Raster, proj, wn, tone, mix, LEAF, FLOWER, GLOW, HAZE, STUCCO, STONE, METAL, WOOD, INK, F, CX, HY, CAMH, W, H
import shedkit
FOG = (92, 108, 100)                                                   # the haze of a grey day
shedkit.FOG = FOG
from pal_day import BLOSSOM, SKY

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
VARIANT = sys.argv[2] if len(sys.argv) > 2 else 'base'
GROWTH, DECAY = VARIANT == 'growth', VARIANT == 'decay'

LIME   = ramp('#1a1c19 #24261f #2f3129 #3b3d34 #484a40 #56574c #646459 #727166 #817f73 #918e80 #a19d8d #b1ac9b #c0bba9')
PAVE   = ramp('#1b1d1a #252722 #30322c #3c3d36 #484941 #55554c #626157 #706e63 #7e7b6f #8c887b')
PATINA = ramp('#142420 #1b302a #233d35 #2c4a41 #36584d #42665a #507467 #608376')
BRASS  = ramp('#2e2412 #4a3a1a #6b5424 #8e7232 #b09048 #c9aa62')
IRON   = ramp('#0c0e0d #141715 #1d211e #272c28 #323833 #3f4640')
SOIL   = ramp('#120e09 #1b150e #251d14 #30261a #3c3021')
IVY    = ramp('#111a13 #172419 #1d2e1f #253a26 #2e472e #385437 #436241 #50714c')
LUSH   = [mix(c, (90, 96, 84), 0.15) for c in ramp('#122015 #182c1b #1f3a22 #284a2a #315a32 #3c6b3b #4a7e46 #5a9152')]
DEAD   = ramp('#1c1812 #28221a #352d22 #43392b #524735 #625641 #72664e')
SALLOW = ramp('#262619 #333321 #42412a #525034 #625f3f #74704b')
BARK   = ramp('#16120e #211a14 #2d241b #3a2f23 #48392b #574634')
GLASSD = ramp('#141c1b #1b2524 #23302e #2c3b39 #364744 #42534f #50615c #60706a')
FLW = [mix(c, (120, 120, 108), 0.28) for c in FLOWER]                  # overcast-muted blossoms
LANT = [mix(c, (118, 112, 96), 0.18) for c in ramp('#5c4520 #7d5f2a #9d7835 #b98f42 #cfa553 #e2bd6b')]         # lamp glass, warm and a bit dim

# the overcast day: shedkit's sky ramp carried on into a pale haze (the Directorate stands in open sky, the day is
# grey and bright -- its windows are warm rooms by day, not beacons)
SKYD = ramp('#2c3e3a #33463f #3a5249 #455e55 #526b62 #5f786e #6d857a #7b9186 #899d91 #97a89b')
_sk1, _sk2 = shedkit.make_noise(13, 45, W, H), shedkit.make_noise(48, 46, W, H)
def sky(x, y, s=0, t=0, z=0, wp=None):
    tt = max(0.0, min(1.0, y / HY))
    v = 2.4 + 5.4 * tt ** 1.25 + (_sk2(x * 0.55, y * 2.6) - 0.5) * 1.5 + (_sk1(x * 0.5, y * 2.4) - 0.5) * 0.5
    return tone(SKYD, v, x, y)

# ---------------------------------------------------------------------------------------------------- the camera
def fogk(z): return max(0.0, min(0.72, 1 - math.exp(-(z - 18) / 120.0) + 0.3 * max(0.0, min(1.0, (z - 46) / 26.0))))
def fogged(c, z, k=1.0): return mix(c, FOG, fogk(z) * k)
shedkit.fog_of = fogk
def X_(x, Z): return (x - CX) * Z / F
def Y_(y, Z): return CAMH + (HY - y) * Z / F
def rng(*k):
    """a uniform 0..1 from integers (FNV alone correlates calls that differ only in the last argument -> fmix32)"""
    h = h32(*k)
    h ^= h >> 16; h = (h * 0x85ebca6b) & 0xffffffff; h ^= h >> 13; h = (h * 0xc2b2ae35) & 0xffffffff; h ^= h >> 16
    return h / 4294967295.0

YT = 2.4                    # the terrace
ZW = 27.0                   # the retaining wall's face
ZS0 = 22.6                  # the foot of the steps
ZC = 32.6                   # the central pavilion's face
ZP = 34.0                   # the side bays' face
ZO = 37.0                   # the wings' face
ZBED = (15.8, 21.2)         # the front beds: front, back
BEDX = (12.5, 30.0)         # ... inner and outer |X|
BEDH = 1.4

rs = Raster()
PTS = {}

# ---------------------------------------------------------------------------------------------------- materials
def masonry(r, u, Y, z, x, y, v0, ch=0.55, L=1.1, seed=0, rough=0.3, weather=0.8, joint=1.3):
    """coursed ashlar in surface coordinates: blocks of one, two or three lengths per course, sunk joints, a lit top
    arris, a tone per block, weathering patches, the odd dirty or replaced block"""
    ps = z / F
    row = math.floor(Y / ch); fv = Y / ch - row
    uu = u + (h32(row, seed, 5) % 97) / 97.0 * L * 2.0
    col = math.floor(uu / L); fu = uu / L - col
    c0 = col
    while h32(row, c0, seed) % 3 == 0 and col - c0 < 2: c0 -= 1
    bid = h32(row, c0, seed + 7)
    v = v0 + ((bid % 9) - 4) * 0.17 + (wn(0, u * 0.2 + seed * 7.0, Y * 0.2) - 0.5) * weather * 1.5
    v += (wn(1, u * 5.0 + (bid % 17), Y * 5.0) - 0.5) * rough * 1.4
    if bid % 11 == 0: v -= 0.9                                                       # a sooty block
    elif bid % 13 == 0: v += 0.5                                                     # a newer, replaced one
    if fv > 1 - 1.5 * ps / ch: v += 0.4
    elif fv < 2.5 * ps / ch: v -= 0.4
    if fv < ps / ch or (fu < ps / L and h32(row, col, seed) % 3 != 0): v -= joint
    c = tone(r, v, x, y)
    if bid % 5 == 0: c = mix(c, (128, 112, 88), 0.12)                                # warmer and cooler stones
    elif bid % 5 == 1: c = mix(c, (78, 96, 92), 0.1)
    return c
def streaks(u, Y, tops, x, y, c, k=0.55):
    """soot and rain runs hanging from ledges at heights `tops` (in surface coords): clustered, of noisy length"""
    for yt in tops:
        dv = yt - Y
        if 0 < dv < 4.5:
            prof = max(0.0, wn(3, u * 2.4, yt * 3.1) - 0.52) * 3.2 * max(0.0, wn(2, u * 0.45, yt) - 0.35) * 2.0
            ln = 0.6 + 3.6 * wn(1, u * 0.9, yt * 1.7)
            if prof > 0 and dv < ln: c = mix(c, (24, 26, 22), min(0.55, prof * k * (1 - dv / ln) ** 0.7))
    return c

def leafy(X, Y, x, y, r, v0, cell=0.3, seed=0):
    """a surface of small leaves: each cell one leaf, lit on its upper side, dark gaps between them"""
    row = math.floor(Y / cell); off = (row % 2) * 0.5
    cu = X / cell + off; col = math.floor(cu)
    fu, fv = cu - col, Y / cell - row
    k = h32(col, row, seed)
    jx, jy = (k % 7) / 7.0 * 0.3 - 0.15, ((k >> 3) % 7) / 7.0 * 0.3 - 0.15
    d = ((fu - 0.5 - jx) / 0.62) ** 2 + ((fv - 0.5 - jy) / 0.5) ** 2
    if d > 1.0: return tone(r, v0 - 1.7, x, y)
    return tone(r, v0 + (fv - 0.5) * 1.6 + ((k >> 6) % 5 - 2) * 0.22, x, y)

# ---------------------------------------------------------------------------------------------------- ivy
# Every region is trained ivy on one wall plane: ('band', x0, x1, y0, y1) a clipped panel, ('swag', x0, x1, ytop, sag,
# th) a festoon hanging under a cornice, ('drape', x0, x1, ytop, ln) a curtain hanging from a parapet (growth),
# ('climb', xc, y0, h, w) a stem climbing from the foot of a wall.
IVYR = {}
def ivy_add(plane, *reg): IVYR.setdefault(plane, []).append(reg)
def ivy_at(plane, X, Y):
    """0 = bare wall, else the ivy's 'thickness' (1 = in the middle of a region, small = its edge)"""
    best = 0.0
    rag = (wn(2, X * 2.2, Y * 2.2) - 0.5) * (0.9 if GROWTH else 0.25 if not DECAY else 0.5)
    for reg in IVYR.get(plane, ()):
        k = reg[0]
        if k == 'band':
            _, x0, x1, y0, y1 = reg
            g = 0.5 if GROWTH else 0.0
            e = min(X - (x0 - g), (x1 + g) - X, Y - (y0 - g), (y1 + g * 2) - Y) + rag * 0.4
        elif k == 'swag':
            _, x0, x1, yt, sag, th = reg
            if not (x0 - 0.6 < X < x1 + 0.6): continue
            q = max(0.0, min(1.0, (X - x0) / (x1 - x0)))
            yc = yt - sag * math.sin(math.pi * q)
            thk = th * (0.6 + 0.4 * math.sin(math.pi * q)) * (1.45 if GROWTH else 1.0)
            e = thk - abs(Y - yc) + rag * 0.35
            for xe in (x0, x1):                                            # the tails hanging at the tie points
                if abs(X - xe) < th * 0.55 and yt - sag * 0.9 - th < Y < yt + 0.1:
                    e = max(e, th * 0.55 - abs(X - xe) + rag * 0.3)
        elif k == 'drape':
            _, x0, x1, yt, ln = reg
            if not (x0 < X < x1) or Y > yt: continue
            L = ln * (0.4 + 0.9 * wn(3, X * 1.1, 3.0) + 0.3 * wn(2, X * 4.0, 9.0))
            e = min(L - (yt - Y), X - x0, x1 - X) * 0.6 + rag * 0.4
        elif k == 'fringe':                                                # trailing ivy clipped to a hem under a ledge
            _, x0, x1, yt, ln = reg
            if not (x0 < X < x1) or Y > yt or Y < yt - ln * 3: continue
            L = ln * (1.0 + 0.18 * math.sin(X * 3.1) + (0.9 * wn(3, X * 1.3, 5.0) if GROWTH else 0))
            e = min(L - (yt - Y), X - x0, x1 - X) + rag * 0.3
        else:                                                              # climb
            _, xc, y0, hh, ww = reg
            if Y < y0 or Y > y0 + hh * 1.2: continue
            q = (Y - y0) / hh
            half = ww * (1.0 - 0.75 * q) + 0.35 * math.sin(Y * 1.7 + xc)
            e = min(half - abs(X - xc - 0.4 * math.sin(Y * 0.9 + xc)), (y0 + hh) - Y) + rag * 0.5
        if e > best: best = e
    if DECAY and best > 0 and wn(3, X * 1.6 + 20, Y * 1.6) > 0.58: return 0.0               # dead patches fallen away
    return best
def ivy_leaf(X, Y, x, y, r, v0, cell=0.42, seed=0):
    """ivy: overlapping leaves in clumps -- each leaf lit on its upper side, the deeper layer dark between them"""
    clump = (wn(0, X * 0.9 + seed, Y * 0.9) - 0.5) * 2.2
    row = math.floor(Y / cell); off = (row % 2) * 0.5
    cu = X / cell + off; col = math.floor(cu)
    fu, fv = cu - col, Y / cell - row
    k = h32(col, row, seed)
    jx, jy = (k % 7) / 7.0 * 0.36 - 0.18, ((k >> 3) % 7) / 7.0 * 0.36 - 0.18
    d = ((fu - 0.5 - jx) / 0.66) ** 2 + ((fv - 0.45 - jy) / 0.56) ** 2
    if d > 1.0: return tone(r, v0 - 1.9 + clump * 0.5, x, y)
    return tone(r, v0 + clump + (fv - 0.45) * 1.8 - (fu - 0.5) * 0.6 + ((k >> 6) % 5 - 2) * 0.25, x, y)
def ivy_col(X, Y, e, x, y, z):
    if DECAY:
        if wn(1, X * 6, Y * 6) > 0.72: return tone(BARK, 1.5 + (0.8 if (x + y) % 2 else 0), x, y)   # bare stems show
        c = ivy_leaf(X, Y, x, y, DEAD, 3.4, cell=0.36, seed=5)
    else:
        r = LUSH if GROWTH else IVY
        c = ivy_leaf(X, Y, x, y, r, 4.3 + min(0.5, e * 0.6), seed=3)
        if GROWTH and wn(1, X * 0.7 + 30, Y * 0.7) > 0.6 and h32(int(X * 7 + 999), int(Y * 7 + 999), 51) % 5 == 0:
            c = FLW[h32(int(X * 7), int(Y * 7), 52) % 5] if h32(int(X * 3), int(Y * 3), 53) % 3 else BLOSSOM[3]
    if e < 0.08: c = mix(c, (10, 14, 10), 0.35)                                               # the clipped edge
    return fogged(c, z)

# ---------------------------------------------------------------------------------------------------- windows
class Win:
    """an opening in a wall plane: a pointed (k > 1) or round (k = 1) arch over jambs, or a circle (rose); lit windows
    are cut quads drawn as emitters just in front of the wall"""
    def __init__(s, plane, cx, y0, ys, w, k=1.5, lit=0.0, lights=2, kind='glass', seed=0):
        s.plane, s.cx, s.y0, s.ys, s.w, s.k, s.lit, s.lights, s.kind, s.seed = plane, cx, y0, ys, w, k, lit, lights, kind, seed
        s.top = ys + math.sqrt(max(0.0, k * k - (k - 1) ** 2)) * w if kind != 'rose' else ys + w
        s.subs = []
        if lights > 1 and kind != 'rose':
            sw = w / lights
            s.subs = [Win(plane, cx - w + sw * (2 * i + 1), y0, ys, sw, k, lights=1) for i in range(lights)]
    def aw(s, X, Y):
        """the half-width of the arch of this window's family passing through (X, Y)"""
        u = abs(X - s.cx)
        if s.kind == 'rose': return math.hypot(u, Y - s.ys)
        v = Y - s.ys
        if v <= 0: return u
        k = s.k
        if k <= 1.001: return math.hypot(u, v)
        a = 2 * k - 1; b = 2 * u * (k - 1)
        return (b + math.sqrt(b * b + 4 * a * (u * u + v * v))) / (2 * a)
    def near(s, X, Y, m=0.8):
        return abs(X - s.cx) < s.w + m and s.y0 - m < Y < s.top + m
WINS = {}
def win_add(*a, **kw):
    w = Win(*a, **kw); WINS.setdefault(w.plane, []).append(w); return w

def opening_shade(plane, X, Y, x, y, z, v_wall):
    """the dressed surround of any opening near (X, Y): a moulded band, the lit sill; None if not near one"""
    for w in WINS.get(plane, ()):
        if not w.near(X, Y, 0.7): continue
        d = w.aw(X, Y)
        if w.kind != 'rose' and Y < w.y0:
            if w.y0 - 0.32 < Y and abs(X - w.cx) < w.w + 0.3:
                return tone(LIME, v_wall + (1.8 if Y > w.y0 - 0.1 else -0.6), x, y)          # the sill
            continue
        if d <= w.w: return tone(LIME, 1.0, x, y)                                            # the reveal (under the glass)
        band = 0.42 if w.kind != 'door' else 0.0
        if d <= w.w + band:
            q = (d - w.w) / band
            up = Y > w.ys
            return tone(LIME, v_wall + 0.8 + 1.0 * math.sin(q * math.pi) - (1.4 if q < 0.18 else 0) + (0.3 if up else 0), x, y)
    return None

def glass_sh(w):
    """the glass of window w: lead cames, tracery (mullions, sub-arches, an oculus), lit panes warm, the rest dark
    with the overcast sky in it; decay cracks and loses panes"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        if w.kind != 'rose' and Y < w.y0: return None
        d = w.aw(X, Y)
        if d > w.w: return None
        ps = z / F
        bar = max(0.09, 0.9 * ps)
        mb = max(0.2, 1.9 * ps)                                                   # tracery bars, at least 2 px
        if w.kind == 'rose':
            r = d / w.w; ang = math.atan2(Y - w.ys, X - w.cx)
            if r > 0.9 or abs(r - 0.36) < bar / w.w: return tone(LIME, 7.0 + (0.8 if Y > w.ys else 0), x, y)
            if r > 0.36 and abs(((ang / (2 * math.pi) * 12) % 1) - 0.5) > 0.5 - bar / (r * w.w) * 12 / (2 * math.pi) * 0.9:
                return tone(LIME, 6.4, x, y)                                                     # spokes
            g = 3.4 - r * 1.6 + (0.6 if r < 0.36 else 0)
            c = tone(LANT, g + (wn(1, X * 3, Y * 3) - 0.5) * 0.8, x, y)
            if 0.36 < r < 0.9 and h32(int(ang * 12 / (2 * math.pi) + 12), 5) % 3 == 0: c = mix(c, (86, 107, 47), 0.35)   # olive glass
            return c
        u = X - w.cx; v = Y - w.ys
        # tracery: mullions between the lights, sub-arches and an oculus in the head
        n = w.lights
        if n > 1:
            sw = w.w / n
            for i in range(1, n):
                if abs(u - (-w.w + 2 * sw * i)) < mb * 0.5 and Y < w.ys + 0.4 * w.w: return tone(LIME, 6.6 - (1.2 if u > -w.w + 2 * sw * i else 0), x, y)
            if v > 0:
                for sub in w.subs:
                    if abs(sub.aw(X, Y) - sw) < mb * 0.5 and Y < sub.top + 0.1: return tone(LIME, 6.4, x, y)
                oc = (w.top - w.ys) * 0.62 + w.ys - 0.15 * w.w
                ro = w.w * 0.36
                if abs(math.hypot(u, Y - oc) - ro) < mb * 0.5: return tone(LIME, 6.4, x, y)
        if w.kind != 'door' and n == 1 and abs(v + (w.ys - w.y0) * 0.35) < bar * 0.5: return tone(LIME, 5.8, x, y)    # a transom
        if abs(d - w.w) < mb * 0.5: return tone(LIME, 3.4, x, y)                                  # the frame
        cw, chh = (0.5, 0.62) if w.kind == 'glass' else (0.62, 0.9)
        if (u / cw) % 1 < bar / cw * 0.55 or (Y / chh) % 1 < bar / chh * 0.55:
            return tone(LANT, 0.6 + w.lit * 0.8, x, y) if w.lit else GLASSD[1]
        pane = (math.floor(u / cw), math.floor(Y / chh))
        k = h32(pane[0] + 999, pane[1] + 999, w.seed)
        if DECAY and k % 31 == 0 and (u / cw) % 1 + (Y / chh) % 1 * 0.6 > 0.35 + 0.3 * ((k >> 5) % 3) / 3:
            return tone(LIME, 1.2 + ((k >> 9) % 2), x, y)                                      # a pane gone (jagged)
        if w.lit:
            g = 1.5 + w.lit * 1.2 - abs(u) / w.w * 0.9 - max(0.0, (Y - w.y0) / max(1.0, w.top - w.y0)) * 0.7
            g += ((k % 5) - 2) * 0.22 + (wn(1, X * 2, Y * 2) - 0.5) * 0.6
            c = tone(LANT, g, x, y)
            sk = 0.28 + max(0.0, (Y - w.y0) / max(1.0, w.top - w.y0)) * 0.34                      # the sky's reflection
            if (u * 0.6 + Y * 0.25) % 3.0 < 0.22: sk += 0.06
            c = mix(c, SKYD[7], sk)
        else:
            g = 2.6 + (Y - w.y0) / max(1.0, w.top - w.y0) * 2.8 + ((k % 5) - 2) * 0.25
            if (u * 0.6 + Y * 0.25) % 2.4 < 0.25: g += 1.2                                        # a sky glint
            c = tone(GLASSD, g, x, y)
        if DECAY and k % 7 == 0 and abs(((u * 3.1 + Y * 1.7) % 1) - ((u * 1.3 - Y * 2.3) % 1)) < 0.08:
            c = tone(GLASSD, 6.5, x, y)                                                            # a crack
        return c
    return sh

def place_glass(w, Z):
    x0, x1 = w.cx - w.w - 0.05, w.cx + w.w + 0.05
    y0 = w.y0 - 0.05 if w.kind != 'rose' else w.ys - w.w - 0.05
    rs.quad((x0, y0, Z - 0.03), (x1, y0, Z - 0.03), (x0, w.top + 0.05, Z - 0.03), glass_sh(w), cls='emit' if w.lit else 'prop', cut=True)

def wall_sh(plane, v0, seed, courses=(), u_of=None, ch=0.55, L=1.1, r=LIME):
    """a limestone wall plane with string courses, the surrounds of its openings and its trained ivy"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = u_of(wp) if u_of else X
        e = ivy_at(plane, u, Y)
        if e > 0: return ivy_col(u, Y, e, x, y, z)
        c = opening_shade(plane, u, Y, x, y, z, v0)
        if c is None:
            for (yc, th) in courses:
                if yc - th < Y < yc + th * 0.6:
                    q = (Y - (yc - th)) / (th * 1.6)
                    c = tone(r, v0 + 1.6 - (2.4 if q < 0.22 else 0) + (0.8 if q > 0.8 else 0) + (wn(1, u * 3, Y * 3) - 0.5) * 0.5, x, y)
                    break
        if c is None:
            c = masonry(r, u, Y, z, x, y, v0 - 1.4 * math.exp(-(Y - YT) / 1.6) - 0.6 * math.exp(-Y / 0.9), ch=ch, L=L, seed=seed)
        tops = [yc - th for (yc, th) in courses]
        for w in WINS.get(plane, ()):
            if abs(u - w.cx) < w.w + 0.4 and w.kind != 'rose': tops.append(w.y0 - 0.3)
        c = streaks(u, Y, tops, x, y, c)
        if ivy_at(plane, u, Y + 0.28) > 0: c = mix(c, (12, 14, 12), 0.45)                          # the ivy's shadow
        return fogged(c, z)
    return sh

# ---------------------------------------------------------------------------------------------------- geometry helpers
def cylinder(cx, cz, r, y0, y1, sh, n=24, cls='wall'):
    for i in range(n):
        a0, a1 = -math.pi + 2 * math.pi * i / n, -math.pi + 2 * math.pi * (i + 1) / n
        P0 = (cx + r * math.sin(a0), y0, cz - r * math.cos(a0)); P1 = (cx + r * math.sin(a1), y0, cz - r * math.cos(a1))
        if (P0[2] + P1[2]) / 2 > cz + r * 0.2: continue
        rs.quad(P0, P1, (P0[0], y1, P0[2]), sh, cls=cls)
def cone(cx, cz, r, y0, y1, sh, n=24, cls='wall'):
    for i in range(n):
        a0, a1 = -math.pi + 2 * math.pi * i / n, -math.pi + 2 * math.pi * (i + 1) / n
        P0 = (cx + r * math.sin(a0), y0, cz - r * math.cos(a0)); P1 = (cx + r * math.sin(a1), y0, cz - r * math.cos(a1))
        if (P0[2] + P1[2]) / 2 > cz + r * 0.3: continue
        rs.quad(P0, P1, (cx, y1, cz), sh, clip=lambda a, b: a + b <= 1.0, cls=cls)
def tri(P0, P1, P2, sh, cls='prop'):
    rs.quad(P0, P1, P2, sh, clip=lambda a, b: a + b <= 1.0, cls=cls)
def plain(r, v0, k=0.5):
    return lambda x, y, s, t, z, wp: fogged(tone(r, v0 + (wn(0, (wp[0] + wp[2]) * 2, wp[1] * 2) - 0.5) * k, x, y), z)
def finial(X, Y0, Z, h=1.4, sun=False):
    """a brass ball on a spike; the central one carries the Directorate's sun (a ring of rays)"""
    rs.line3((X, Y0, Z), (X, Y0 + h, Z), lambda x, y, s, t, z, wp: fogged(BRASS[2] if x % 2 else BRASS[1], z), w=0.14)
    if sun:
        def sun_sh(x, y, s, t, z, wp):
            d = math.hypot(s, t); a = math.atan2(t, s)
            if d < 0.42: return tone(BRASS, 4.4 - (s + t) * 1.6, x, y)
            if d < 1.0 and abs(((a / (2 * math.pi) * 12) % 1) - 0.5) < 0.5 * (1 - d) * 1.1: return tone(BRASS, 3.6 - d, x, y)
            return None
        rs.disc(X, Y0 + h + 0.4, Z - 0.1, 1.0, sun_sh, cls='prop')
    else:
        rs.disc(X, Y0 + h, Z - 0.1, 0.22, lambda x, y, s, t, z, wp: fogged(tone(BRASS, 3.8 - (s + t) * 1.5, x, y), z))

# ---------------------------------------------------------------------------------------------------- sky and the city beyond
rs.quad((-1400, 800, 600), (1400, 800, 600), (-1400, -300, 600), sky, cls='sky')
def skyline(seed, Z, lo, hi, x0, x1, step):
    X = x0
    while X < x1:
        wd = step * (0.6 + rng(int(X), seed) * 0.9)
        top = lo + rng(int(X), seed, 2) * (hi - lo)
        k = h32(int(X), seed, 3)
        sh = lambda x, y, s, t, z, wp, k=k: HAZE[3 + (k % 2)] if (int(t * 40) % 5 or k % 3) else HAZE[2]
        rs.quad((X, 0, Z), (X + wd, 0, Z), (X, top, Z), sh, cls='wall')
        if k % 4 == 0: rs.quad((X + wd * 0.4, top, Z), (X + wd * 0.5, top, Z), (X + wd * 0.4, top + (hi - lo) * 0.6, Z), sh, cls='wall')
        X += wd + step * 0.15 * (k % 3)
skyline(5, 260, 18, 46, -330, 330, 22)
skyline(6, 180, 10, 30, -260, 260, 16)

# ---------------------------------------------------------------------------------------------------- the plaza
def puddle(X, Z):
    if Z > ZS0 - 0.3: return 0.0
    m = wn(2, X * 0.5 + 7.0, Z * 0.8) + (wn(3, X * 2.2, Z * 2.2) - 0.5) * 0.08 - (0.04 if abs(X) > 7 else 0)
    if GROWTH: m -= 0.02
    if DECAY: m += 0.02
    return max(0.0, min(1.0, (m - 0.74) * 14))
SUN_C = (0.0, 18.6)
def sun_inlay(X, Z, x, y, z):
    """a brass sun let into the runner: a ring, twelve pale stone rays, a brass disc"""
    dx, dz = X - SUN_C[0], (Z - SUN_C[1]) * 1.0
    d = math.hypot(dx, dz)
    if d > 3.0: return None
    a = math.atan2(dz, dx)
    tarn = 1.6 if DECAY else 0.0
    if d < 1.0: return tone(BRASS, 3.0 - tarn + (wn(1, X * 4, Z * 4) - 0.5) * 1.2 - (0.8 if abs(d - 0.7) < 0.07 else 0), x, y)
    if abs(d - 2.75) < 0.12: return tone(BRASS, 2.8 - tarn + (wn(1, X * 4, Z * 4) - 0.5), x, y)
    if 1.1 < d < 2.6 and abs(((a / (2 * math.pi) * 12) % 1) - 0.5) < 0.5 * (2.6 - d) / 1.5 * 0.85:
        return tone(LIME, 9.2 - (d - 1.1) * 0.6 + (wn(0, X * 3, Z * 3) - 0.5) * 0.6, x, y)
    return None
def plaza(x, y, s, t, z, wp):
    X, _, Z = wp
    ps, psz = z / F, z * z / (F * CAMH)
    c = sun_inlay(X, Z, x, y, z)
    if c is None:
        if abs(X) < 6.3:                                                            # the flagged runner to the steps
            D = 1.8; row = math.floor(Z / D); fz = Z / D - row
            Wd = 2.1; uu = X + 6.3 + (row % 2) * 1.05; col = math.floor(uu / Wd); fx = uu / Wd - col
            sid = h32(col, row, 3)
            v = 6.2 + ((sid % 7) - 3) * 0.15 + (wn(0, X * 0.3, Z * 0.3) - 0.5) * 0.9 + (wn(1, X * 3.0, Z * 1.2) - 0.5) * 0.35
            v += 0.5 * math.exp(-(X / 2.4) ** 2)                                     # trodden pale in the middle
            j = fx < ps / Wd * 1.2 or fz < psz / D * 1.2
            if sid % 9 == 0 and abs((fx - 0.25) - fz * 0.5) < ps / Wd * 1.3: v -= 1.6     # a crack
            if sid % 6 == 1: v -= 0.5 + (wn(2, X * 1.4, Z * 1.4) - 0.5) * 0.8                # a stained flag
            v += (wn(3, X * 6.0, Z * 2.0) - 0.5) * 0.5                                       # tooling grain
            if fx > 1 - ps / Wd * 3 or fz > 1 - psz / D * 3: v += 0.6                        # the worn arris
            c = tone(PAVE, v - (2.0 if j else 0), x, y)
            if j and GROWTH: c = mix(c, LUSH[3], 0.55)
        elif abs(X) < 6.75:                                                          # its kerb
            c = tone(LIME, 7.4 - (1.6 if abs(X) > 6.62 else 0) + (wn(1, X, Z * 2) - 0.5) * 0.6, x, y)
        else:                                                                        # setts in running bond
            SXc, SZc = 0.8, 0.6
            row = math.floor(Z / SZc); col = math.floor(X / SXc + (row % 2) * 0.5)
            fx = (X / SXc + (row % 2) * 0.5) - col; fz = Z / SZc - row
            k = h32(col, row, 7)
            v = 4.9 + (k % 5 - 2) * 0.3 + (wn(0, X * 0.25, Z * 0.25) - 0.5) * 1.3 + (wn(1, X * 2, Z * 2) - 0.5) * 0.5
            v += 0.45 * (1 - abs(fx - 0.5) * 2) * (1 - abs(fz - 0.5) * 2)                  # worn, rounded tops
            if k % 19 == 0: v -= 1.1                                                     # sunken
            elif k % 23 == 0: v += 0.8                                                   # a newer stone
            if k % 7 == 0 and fx < 0.3 and fz > 0.6: v -= 0.9                            # a chipped corner
            j = fx < 1.0 * ps / SXc + 0.04 or fz < 1.0 * psz / SZc + 0.04
            c = tone(PAVE, v - (1.9 if j else 0), x, y)
            if j and GROWTH and wn(3, X * 0.6, Z * 0.6) > 0.4: c = mix(c, LUSH[2], 0.6)
            elif j and not DECAY and wn(3, X * 0.6, Z * 0.6) > 0.72: c = mix(c, IVY[2], 0.4)
    if DECAY:                                                                        # dead leaves blown across
        cx_, cz_ = math.floor(X * 2.5), math.floor(Z * 2.5)
        k = h32(cx_ + 999, cz_ + 999, 61)
        if k % 11 == 0 or (k % 5 == 0 and wn(2, X * 0.5, Z * 0.5) > 0.6):
            lx, lz = (k % 13) / 13.0 * 0.6 + 0.2, ((k >> 4) % 13) / 13.0 * 0.6 + 0.2
            if ((X * 2.5 - cx_ - lx) / 0.32) ** 2 + ((Z * 2.5 - cz_ - lz) / 0.2) ** 2 < 1:
                c = tone(DEAD, 3.0 + (k >> 8) % 3, x, y) if (k >> 6) % 4 else tone(SALLOW, 2.4, x, y)
    # light falloff: a shade darker towards the viewer and out to the sides
    c = mix(c, (14, 16, 14), 0.22 * max(0.0, min(1.0, (17.5 - Z) / 12.0)) + 0.12 * min(1.0, abs(X) / 45.0))
    p_ = puddle(X, Z)
    if p_ > 0: c = mix(c, (30, 36, 34), 0.25 if p_ < 0.35 else 0.12)                 # wet rim, then the mirror
    return fogged(c, z)
rs.quad((-120, 0, 3), (120, 0, 3), (-120, 0, ZW + 0.1), plaza, cls='ground')

# ---------------------------------------------------------------------------------------------------- the retaining wall, the vent
VENT = (-21.0, -17.0, 0.55, 1.85)
def retaining(x, y, s, t, z, wp):
    X, Y, Z = wp
    if Y > YT - 0.05: return fogged(tone(LIME, 8.6, x, y), z)
    c = masonry(LIME, X, Y, z, x, y, 5.2 - 1.2 * math.exp(-Y / 0.6), ch=0.6, L=1.3, seed=21, rough=0.5, weather=1.0, joint=1.6)
    vx0, vx1, vy0, vy1 = VENT
    if vx0 - 0.35 < X < vx1 + 0.35 and vy0 - 0.35 < Y < vy1 + 0.35:               # the dressed frame of the vent
        c = tone(LIME, 7.6 if Y > vy1 or X < vx0 else 5.4, x, y)
    if DECAY and wn(3, X * 0.3 + 4, Y * 0.3) > 0.62 and abs(wn(2, X * 1.4 + 40, Y * 0.6) - 0.5) < 0.012 * z: c = tone(LIME, 1.4, x, y)   # cracks
    return fogged(c, z)
for side in (-1, 1):
    x0, x1 = sorted((side * 7.0, side * 120.0))
    rs.box(x0, x1, 0, YT, ZW, ZW + 0.8, retaining, retaining, cls='wall')
    rs.box(x0, x1, YT, YT + 0.32, ZW - 0.28, ZW + 0.6, plain(LIME, 8.8, 0.6), plain(LIME, 6.0), top=plain(LIME, 9.6, 0.5),
           bottom=plain(LIME, 3.0), cls='prop')                                     # the coping
def vent_sh(x, y, s, t, z, wp):
    """a bronze grille of horizontal louvres; warm light from the archive rooms between them"""
    X, Y, _ = wp
    if s < 0.05 or s > 0.95 or t < 0.08 or t > 0.92: return tone(BRASS, 1.6 + (1.2 if t > 0.92 else 0), x, y)
    q = (t * 6.0) % 1
    if q < 0.42: return tone(BRASS, 2.2 + q * 3.0 + (wn(1, X * 6, Y * 6) - 0.5) * 0.8 - (1.4 if DECAY else 0), x, y)
    if abs(s - 0.5) < 0.025: return BRASS[0]
    return tone(LANT, 0.7 + (1 - abs(s - 0.5) * 2) * 1.3 - (0.6 if DECAY else 0), x, y)
rs.quad((VENT[0], VENT[2], ZW - 0.04), (VENT[1], VENT[2], ZW - 0.04), (VENT[0], VENT[3], ZW - 0.04), vent_sh, cls='emit')

# ---------------------------------------------------------------------------------------------------- the steps
NST = 8; RISE = YT / NST; RUN = (ZW - ZS0) / NST
def tread(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 7.0 + (wn(0, X * 0.5, Z * 2.0) - 0.5) * 0.8 + 0.7 * math.exp(-(X / 2.0) ** 2) - (1.4 if (X + 20) % 2.4 < z / F * 1.2 else 0)
    c = tone(PAVE, v, x, y)
    if DECAY and h32(int(X * 3 + 99), int(Z * 3), 62) % 11 == 0 and ((X * 3) % 1 - 0.5) ** 2 + ((Z * 3) % 1 - 0.5) ** 2 < 0.1: c = tone(DEAD, 3.2, x, y)
    if GROWTH and (X + 20) % 2.4 < z / F * 1.6: c = mix(c, LUSH[3], 0.5)
    return fogged(c, z)
def riser(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 4.6 + (wn(1, X * 0.7, Y * 3.0) - 0.5) * 0.7 + (1.0 if t > 0.78 else 0) - (1.2 if (X + 20) % 2.4 < z / F * 1.2 else 0)
    return fogged(tone(LIME, v, x, y), z)
for i in range(NST):
    rs.box(-7.0, 7.0, 0, RISE * (i + 1), ZS0 + RUN * i, ZW + 0.5, riser, riser, top=tread, cls='prop')
def cheek_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    c = masonry(LIME, Z, Y, z, x, y, 6.0, ch=0.6, L=1.2, seed=31)
    return fogged(c, z)
for side in (-1, 1):
    x0, x1 = sorted((side * 7.0, side * 8.5))
    rs.box(x0, x1, 0, YT + 0.6, ZS0 + 1.2, ZW + 0.2, wall_sh('cheek%d' % side, 6.2, 33), cheek_sh,
           top=plain(LIME, 8.8, 0.4), cls='wall')
    # a pedestal at the foot carries an urn
    px0, px1 = sorted((side * 6.8, side * 9.4))
    rs.box(px0, px1, 0, 1.9, ZS0 - 0.6, ZS0 + 1.4, wall_sh('ped%d' % side, 6.6, 35), cheek_sh, top=plain(LIME, 9.0, 0.4), cls='wall')
    rs.box(px0 - 0.15, px1 + 0.15, 1.9, 2.15, ZS0 - 0.75, ZS0 + 1.55, plain(LIME, 9.2, 0.3), plain(LIME, 7.0), top=plain(LIME, 9.8, 0.3), cls='prop')

def urn(X, Y0, Z, r=0.95, h=1.5):
    def sh(x, y, s, t, z, wp):
        u = s * 2 - 1; q = 1 - t                                             # q: 0 at the foot, 1 at the lip
        prof = 0.38 + 0.62 * math.sin(min(1.0, q * 1.25) * math.pi * 0.62) if q < 0.86 else 0.92 + (0.1 if q > 0.93 else 0)
        if q < 0.12: prof = 0.42 + q * 1.2
        if abs(u) > prof: return None
        n = u / prof
        v = 6.4 - n * 2.4 - abs(n) ** 3 * 1.6 + (1.2 if 0.86 < q < 0.93 else 0) - (1.4 if 0.84 < q < 0.86 else 0)
        if abs(q - 0.55) < 0.03: v -= 1.2                                     # a moulded band
        return fogged(tone(LIME, v + (wn(1, u * 4, q * 4) - 0.5) * 0.6, x, y), z)
    rs.quad((X - r, Y0, Z), (X + r, Y0, Z), (X - r, Y0 + h, Z), sh, cls='prop', cut=True)

# ---------------------------------------------------------------------------------------------------- plants
def mound(X, Y, Z, r, ramp_, v0, seed, ragged=0.25):
    """a soft clump of foliage, lit from above-left, a ragged leafy rim"""
    def sh(x, y, s, t, z, wp):
        d = s * s + t * t
        if d > 0.62 and h32(x, y, seed) % 3 == 0 and ragged > 0: return None
        if d > 0.9 and h32(x, y, seed + 1) % 2 == 0: return None
        v = v0 - s * 0.7 - t * 1.5 + ((h32(x // 2, y // 2, seed) % 5) - 2) * 0.25
        if h32(x, y, seed + 2) % 7 == 0: v -= 1.4                             # gaps between the leaves
        return fogged(tone(ramp_, v, x, y), z)
    rs.disc(X, Y, Z, r, sh)
def bloom(X, Y, Z, r, col, seed):
    def sh(x, y, s, t, z, wp):
        if s * s + t * t > 0.85: return None
        c = col
        if t < -0.2 and s < 0.2: c = mix(col, (255, 250, 235), 0.25)
        elif t > 0.3: c = mix(col, (0, 0, 0), 0.3)
        return fogged(c, z)
    rs.disc(X, Y, Z, r, sh)
FOLI = LUSH if GROWTH else SALLOW if DECAY else IVY
def flower_bed(X0, X1, Z0, Z1, Y0, seed, rows=None, spill=0.0, sick=False, border=False):
    """rows of flowers across a bed (the Directorate plants in precise bands of one colour, edged with clipped box);
    growth crowds and overflows them, decay leaves them wilted"""
    rows = rows or [0, 1, 2, 3]
    if border:                                                               # the clipped box edging along the front
        hedge(X0, X1, Y0, Y0 + 0.55, Z0, Z0 + 0.5, seed + 77)
        Z0 += 0.55
    n = int((X1 - X0) * (Z1 - Z0) * (4.2 if GROWTH else 2.0 if DECAY else 3.4))
    for i in range(n):
        X = X0 + rng(seed, i, 1) * (X1 - X0)
        Z = Z0 + rng(seed, i, 2) * (Z1 - Z0)
        q = (Z - Z0) / (Z1 - Z0)
        band = rows[min(len(rows) - 1, int(q * len(rows)))]
        r = 0.34 + rng(seed, i, 3) * 0.26
        if sick:
            mound(X, Y0 + r * 0.3, Z, r * 0.8, DEAD, 2.4 + rng(seed, i, 4) * 1.8, seed + i)
            if rng(seed, i, 6) < 0.3: bloom(X + 0.1, Y0 + r * 0.45, Z - 0.1, 0.11, tone(DEAD, 4.6, 0, 0), seed + i)
            continue
        hgt = 0.55 if not DECAY else 0.35
        mound(X, Y0 + r * hgt, Z, r, FOLI, 3.4 + rng(seed, i, 4) * 1.4 - (0.6 if DECAY else 0), seed + i)
        nb = 4 if GROWTH else (1 if DECAY else 3)
        for j in range(nb):
            if DECAY and rng(seed, i, j, 9) < 0.45: continue
            fx = X + (rng(seed, i, j, 7) - 0.5) * r * 1.5
            fy = Y0 + r * (hgt + 0.55) + rng(seed, i, j, 8) * r * 0.4 - (0.25 if DECAY else 0)
            colr = FLW[band] if not GROWTH or rng(seed, i, j, 10) < 0.55 else (FLW[h32(seed, i, j) % 5] if rng(seed, i, j, 11) < 0.7 else BLOSSOM[3])
            if DECAY: colr = mix(colr, (92, 74, 50), 0.6)
            bloom(fx, fy, Z - 0.2, 0.15 + rng(seed, i, j, 12) * 0.07 + (0.04 if GROWTH else 0), colr, seed + i * 7 + j)
    if spill > 0:                                                            # trailing flowers spilling over the front wall
        for i in range(int((X1 - X0) * spill * 4)):
            X = X0 + rng(seed, i, 21) * (X1 - X0)
            ln = 0.3 + rng(seed, i, 22) * 1.0
            for k in range(int(ln / 0.16)):
                mound(X + math.sin(k * 0.7 + i) * 0.08, Y0 - k * 0.16, Z0 - 0.25, 0.16, FOLI, 4.0 - k * 0.15, seed + i * 31 + k, ragged=0)
                if k % 2 == 1: bloom(X + 0.08, Y0 - k * 0.16, Z0 - 0.35, 0.09, FLW[(i + k) % 5] if rng(i, k, 3) > 0.25 else BLOSSOM[3], seed + k)

def hedge(X0, X1, Y0, Y1, Z0, Z1, seed):
    """a clipped box hedge: crisp planes of small leaves; growth lets it go shaggy and flower, decay browns it"""
    r_ = LUSH if GROWTH else IVY
    def face(x, y, s, t, z, wp, top=False):
        X, Y, Z = wp
        c = leafy(X + Z, Y if not top else Z, x, y, r_, (5.0 if top else 3.6) + (wn(0, X * 0.6, Z * 0.6) - 0.5) * 0.8, cell=0.22, seed=seed)
        if DECAY and wn(3, X * 0.7 + seed, Y * 0.7 + Z * 0.7) > 0.5: c = mix(c, tone(DEAD, 3.6 if top else 2.8, x, y), 0.75)
        if GROWTH and h32(int(X * 6 + 999), int(Y * 6 + Z * 6 + 999), seed) % 17 == 0: c = FLW[h32(int(X * 6), int(Z * 6), 3) % 5]
        return fogged(c, z)
    rs.box(X0, X1, Y0, Y1, Z0, Z1, face, face, top=lambda x, y, s, t, z, wp: face(x, y, s, t, z, wp, True), cls='prop')
    if GROWTH:                                                              # shoots sticking out of the clipped top
        for i in range(int((X1 - X0) * 2.2)):
            X = X0 + rng(seed, i, 41) * (X1 - X0)
            mound(X, Y1 + 0.15, Z0 + rng(seed, i, 42) * (Z1 - Z0), 0.25 + rng(seed, i, 43) * 0.2, LUSH, 4.6, seed + i)

def spiral(X, Y0, Z, h, r0, seed):
    """the root-tendrils Verrik coaxed into a spiral: a woody tendril winding up round an invisible cone"""
    turns = 3.2; n = 90
    pts = []
    for i in range(n + 1):
        q = i / n
        a = q * turns * 2 * math.pi + seed
        rr = r0 * (1 - 0.78 * q)
        pts.append((X + rr * math.cos(a), Y0 + h * q, Z + rr * math.sin(a) * 0.9, q))
    if DECAY: pts = pts[:int(n * 0.82)]                                     # its top has snapped off
    for (a, b) in zip(pts, pts[1:]):
        q = a[3]
        def sh(x, y, s, t, z, wp, q=q):
            sx, sy = proj(*wp)
            dx = x + 0.5 - sx
            if DECAY: rr_ = DEAD
            elif GROWTH: rr_ = BARK
            else: rr_ = BARK
            v = 3.4 - dx * 0.6 + (1.0 if (y + int(q * 40)) % 4 == 0 else 0)
            return fogged(tone(rr_, v + (1.4 if DECAY else 0), x, y), z)
        rs.line3(a[:3], b[:3], sh, w=0.34 * (1 - 0.55 * q) + 0.08)
    for i, p in enumerate(pts[::4]):                                        # leaf tufts along it
        if DECAY and i % 3: continue
        rr_ = LUSH if GROWTH else DEAD if DECAY else IVY
        mound(p[0] + 0.05, p[1] + 0.1, p[2] - 0.2, 0.22 + (0.16 if GROWTH else 0), rr_, 4.4, seed * 7 + i, ragged=0.1)
        if GROWTH and i % 2 == 0: bloom(p[0], p[1] + 0.3, p[2] - 0.35, 0.16, FLW[i % 5] if i % 3 else BLOSSOM[4], seed + i)

def shrub_ball(X, Y0, Z, r, seed):
    """a clipped ball on a short clean stem"""
    rs.line3((X, Y0, Z), (X, Y0 + r * 0.9, Z), lambda x, y, s, t, z, wp: fogged(BARK[2], z), w=0.2)
    def sh(x, y, s, t, z, wp):
        d = s * s + t * t
        if GROWTH and d > 0.8 and h32(x, y, seed) % 2: return None
        if DECAY and d > 0.5 and h32(x // 2, y // 2, seed) % 3 == 0: return None
        c = leafy(s * 4 + seed, t * 4, x, y, LUSH if GROWTH else DEAD if DECAY else IVY, 4.6 - s * 1.0 - t * 1.6, cell=0.28, seed=seed)
        if GROWTH and h32(x, y, seed + 9) % 11 == 0: c = BLOSSOM[3] if h32(x, y, 3) % 2 else FLW[2]
        return fogged(c, z)
    rs.disc(X, Y0 + r * 1.8, Z, r, sh)

# ---------------------------------------------------------------------------------------------------- lamps
def lamp(X, Y0, Z, h, seed, out=False, big=True):
    """a cast-iron lamp post with a glazed lantern; `out` = dead, a pane broken"""
    def post(x, y, s, t, z, wp):
        sx, _ = proj(*wp); dx = x + 0.5 - sx
        v = 2.4 - dx * 0.9 + (1.2 if (int(wp[1] * 3.0) % 7 == 0) else 0)
        return fogged(tone(IRON, v, x, y), z)
    rs.box(X - 0.45, X + 0.45, Y0, Y0 + 0.9, Z - 0.45, Z + 0.45, plain(IRON, 2.6), plain(IRON, 1.6), top=plain(IRON, 3.4), cls='prop')
    rs.line3((X, Y0 + 0.9, Z), (X, Y0 + h, Z), post, w=0.26 if big else 0.2)
    lw, lh = (0.62, 1.5) if big else (0.48, 1.1)
    Yl = Y0 + h
    def lant(x, y, s, t, z, wp):
        if s < 0.12 or s > 0.88 or t < 0.06 or t > 0.94 or abs(s - 0.5) < 0.06: return tone(IRON, 1.6, x, y)
        if out:
            if s > 0.5 and t < 0.5 and abs((s - 0.5) * 2 - t * 2) < 0.18: return (12, 12, 11)
            return tone(GLASSD, 2.6 + t * 2.0, x, y)
        return tone(LANT, 3.6 + (1 - abs(s - 0.5) * 2) * 1.0 - t * 0.8, x, y)
    rs.box(X - lw, X + lw, Yl, Yl + lh, Z - lw, Z + lw, lant, lant, cls='prop' if out else 'emit')
    cone(X, Z, lw + 0.25, Yl + lh, Yl + lh + 0.7, lambda x, y, s, t, z, wp: fogged(tone(IRON, 2.6 - t * 1.2, x, y), z), n=8, cls='prop')
    rs.disc(X, Yl + lh + 0.85, Z - 0.1, 0.13, lambda x, y, s, t, z, wp: fogged(BRASS[3], z))
    rs.box(X - lw - 0.1, X + lw + 0.1, Yl - 0.18, Yl, Z - lw - 0.1, Z + lw + 0.1, plain(IRON, 2.2), plain(IRON, 1.6), cls='prop')

# ---------------------------------------------------------------------------------------------------- the palace
# --- the central pavilion
PV = 9.4
DOOR = win_add('pav', 0.0, YT, 9.0, 3.3, 1.5, lit=1.0, lights=2, kind='door', seed=1)
GREAT = win_add('pav', 0.0, 16.4, 22.4, 4.4, 1.5, lit=0.75 if not DECAY else 0.45, lights=3, seed=2)
ROSE = win_add('gable', 0.0, 0, 33.4, 2.2, kind='rose', lit=0.8 if not DECAY else 0.5, seed=3)
PV_COURSES = [(15.5, 0.38), (29.3, 0.5)]
ivy_add('pav', 'fringe', -PV, -4.5, 15.1, 0.5); ivy_add('pav', 'fringe', 4.5, PV, 15.1, 0.5)
ivy_add('pav', 'fringe', -PV, PV, 28.9, 0.45)
ivy_add('pav', 'swag', -PV + 0.4, -4.6, 28.6, 2.2, 0.5)
ivy_add('pav', 'swag', 4.6, PV - 0.4, 28.6, 2.2, 0.5)
ivy_add('pav', 'swag', -4.0, 4.0, 15.0, 0.7, 0.42)                      # a garland over the portal's head
if GROWTH:
    ivy_add('pav', 'drape', -PV, -3.0, 28.8, 6.0); ivy_add('pav', 'drape', 3.0, PV, 28.8, 6.0)
    ivy_add('pav', 'climb', -6.0, YT, 22.0, 1.6); ivy_add('pav', 'climb', 6.2, YT, 20.0, 1.5)
rs.box(-PV, PV, YT, 29.8, ZC, ZP, wall_sh('pav', 7.4, 41, PV_COURSES), plain(LIME, 5.0), cls='wall')
place_glass(DOOR, ZC); place_glass(GREAT, ZC)
# the portal's orders (stepped rings) and a hood with a little crocketed gable
def order_ring(w_in, w_out, Z, v0):
    def sh(x, y, s, t, z, wp):
        X, Y, _ = wp
        d = DOOR.aw(X, Y)
        if Y < YT or d <= w_in or d > w_out: return None
        q = (d - w_in) / (w_out - w_in)
        v = v0 + 1.4 * math.sin(q * math.pi) - (1.2 if q < 0.15 else 0)
        if Y > DOOR.ys and (math.atan2(Y - DOOR.ys, X) * 7) % 1 < 0.06: v -= 1.1               # voussoir joints
        if Y < DOOR.ys and (Y / 0.6) % 1 < 0.06: v -= 1.1
        return fogged(tone(LIME, v, x, y), z)
    rs.quad((-w_out, YT, Z), (w_out, YT, Z), (-w_out, 16.0, Z), sh, cls='wall', cut=True)
order_ring(3.3, 3.85, ZC - 0.2, 7.4)
order_ring(3.85, 4.4, ZC - 0.4, 8.0)
def hood(x, y, s, t, z, wp):
    X, Y, _ = wp
    top = 15.1
    if Y > top + 0.05 or abs(X) > 4.6: return None
    d = DOOR.aw(X, Y)
    if d <= 4.4: return None
    if top - Y < 0.32: return tone(LIME, 9.2 - (2.2 if top - Y > 0.22 else 0), x, y)               # the coping
    if d < 4.75: return tone(LIME, 8.8 + (0.6 if Y > DOOR.ys else 0), x, y)                         # the hood mould
    e = ivy_at('pav', X, Y)
    if e > 0: return ivy_col(X, Y, e, x, y, z)
    for sx in (-1, 1):                                                          # trefoils in the spandrels
        cx_, cy_ = sx * 3.3, 14.6
        for (dx, dy) in ((0, 0.22), (-0.2, -0.1), (0.2, -0.1)):
            dd = math.hypot(X - cx_ - dx, Y - cy_ - dy)
            if dd < 0.16: return tone(LIME, 1.4, x, y)
            if dd < 0.24: return tone(LIME, 8.6, x, y)
    return fogged(masonry(LIME, X, Y, z, x, y, 7.0, seed=45), z)
rs.quad((-4.7, 8.0, ZC - 0.3), (4.7, 8.0, ZC - 0.3), (-4.7, 15.2, ZC - 0.3), hood, cls='wall', cut=True)
# a small balcony under the great window
rs.box(-5.2, 5.2, 15.7, 16.1, ZC - 1.0, ZC, plain(LIME, 8.6), plain(LIME, 6.0), top=plain(LIME, 9.6), bottom=plain(LIME, 3.0), cls='prop')
def baluster(x, y, s, t, z, wp):
    X, Y, _ = wp
    if t > 0.84: return tone(LIME, 9.0 if t > 0.92 else 7.0, x, y)
    q = (X * 2.2) % 1
    w_ = 0.18 + 0.12 * math.sin(t / 0.84 * math.pi)
    if abs(q - 0.5) < w_: return tone(LIME, 7.6 - (q - 0.5) * 3.0, x, y)
    return None
rs.quad((-5.2, 16.1, ZC - 0.95), (5.2, 16.1, ZC - 0.95), (-5.2, 17.0, ZC - 0.95), lambda x, y, s, t, z, wp: fogged(baluster(x, y, s, t, z, wp), z) if baluster(x, y, s, t, z, wp) else None, cls='prop', cut=True)
# the cornice and the gable with the rose window
rs.box(-PV - 0.3, PV + 0.3, 29.4, 30.2, ZC - 0.5, ZP, plain(LIME, 8.4), plain(LIME, 5.6), top=plain(LIME, 9.4), bottom=plain(LIME, 3.0), cls='prop')
GB, GA, GH = 30.2, 38.0, 7.2                                                     # the gable: foot, apex, half-width
ivy_add('gable', 'swag', -6.2, -2.6, 31.9, 0.9, 0.36); ivy_add('gable', 'swag', 2.6, 6.2, 31.9, 0.9, 0.36)
if GROWTH: ivy_add('gable', 'drape', -GH, GH, GA - 1.0, 4.0)
gwall = wall_sh('gable', 7.6, 47)
def gable(x, y, s, t, z, wp):
    X, Y, _ = wp
    top = GB + (GH - abs(X)) * (GA - GB) / GH
    if Y > top: return None
    dn = (top - Y)
    if dn < 0.45: return fogged(tone(LIME, 9.0 + (0.8 if dn < 0.14 else 0) - (2.0 if dn > 0.34 else 0), x, y), z)
    return gwall(x, y, s, t, z, wp)
rs.quad((-GH, GB, ZC - 0.3), (GH, GB, ZC - 0.3), (-GH, GA + 0.1, ZC - 0.3), gable, cls='wall', cut=True)
place_glass(ROSE, ZC - 0.3)
for i in range(7):                                                               # crockets up the rakes
    q = (i + 0.6) / 7.4
    for sx in (-1, 1):
        X = sx * GH * (1 - q); Y = GB + (GA - GB) * q
        rs.disc(X + sx * 0.2, Y + 0.24, ZC - 0.35, 0.18, lambda x, y, s, t, z, wp: fogged(tone(LIME, 6.8 - t * 2.4 - s * 0.8, x, y), z))
finial(0.0, GA - 0.1, ZC - 0.3, h=1.0, sun=True)
# the piers either side, pinnacled
def pier(X0, X1, Z0, Z1, top, pin, plane):
    rs.box(X0, X1, YT, top, Z0, Z1, wall_sh(plane, 7.8, 51, [(top - 4.0, 0.32), (12.0, 0.3)]), plain(LIME, 5.6), top=plain(LIME, 9.0), cls='wall')
    rs.box(X0 - 0.2, X1 + 0.2, top, top + 0.5, Z0 - 0.2, Z1, plain(LIME, 8.8), plain(LIME, 6.0), top=plain(LIME, 9.6), cls='prop')
    cx, cz = (X0 + X1) / 2, (Z0 + Z1) / 2
    hw = (X1 - X0) / 2
    cone(cx, cz, hw * 0.95, top + 0.5, top + 0.5 + pin, lambda x, y, s, t, z, wp: fogged(tone(LIME, 7.8 + (0.8 if wp[0] < cx else -0.9) - (0.9 if (wp[1] * 2.6) % 1 < 0.12 else 0), x, y), z), n=8)
    for k in range(3):                                                           # crockets on the pinnacle
        Y = top + 0.5 + pin * (0.25 + 0.22 * k); rr = hw * 0.95 * (1 - (0.25 + 0.22 * k))
        for sx in (-1, 1): rs.disc(cx + sx * (rr + 0.1), Y, cz - 0.3, 0.17, lambda x, y, s, t, z, wp: fogged(tone(LIME, 8.4 - t * 2, x, y), z))
    finial(cx, top + 0.5 + pin - 0.1, cz - 0.1, h=0.5)
for sx in (-1, 1):
    x0, x1 = sorted((sx * PV, sx * (PV + 1.9)))
    ivy_add('pier%d' % sx, 'band', x0 + 0.25, x1 - 0.25, YT + 1.2, 8.5)
    ivy_add('pier%d' % sx, 'fringe', x0, x1, 28.0, 0.5)
    if GROWTH: ivy_add('pier%d' % sx, 'climb', (x0 + x1) / 2, YT, 30.0, 1.4)
    pier(x0, x1, ZC - 0.6, ZP, 32.4, 4.6, 'pier%d' % sx)

# --- the side bays
SB0, SB1 = PV + 1.9, 23.2
SB_COURSES = [(13.4, 0.36), (25.4, 0.5)]
for sx in (-1, 1):
    plane = 'bay%d' % sx
    for i, cxu in enumerate((14.4, 19.9)):
        cx = sx * cxu
        win_add(plane, cx, 3.6, 9.4, 1.75, 1.5, lit=(0.0 if (DECAY and i == (sx > 0)) else 0.9), lights=2, seed=10 + i + sx * 5)
        win_add(plane, cx, 15.0, 21.4, 1.75, 1.5, lit=(0.6 if (i + (sx > 0)) % 2 == 0 and not DECAY else 0.0), lights=2, seed=20 + i + sx * 5)
    for cxu in (14.4, 19.9):                                                       # festoons over the upper windows, under the parapet
        ivy_add(plane, 'swag', sx * cxu - 2.6, sx * cxu + 2.6, 25.0, 1.5, 0.42)
    ivy_add(plane, 'fringe', min(sx * SB0, sx * SB1), max(sx * SB0, sx * SB1), 13.0, 0.55)
    if GROWTH:
        ivy_add(plane, 'drape', min(sx * SB0, sx * SB1), max(sx * SB0, sx * SB1), 25.2, 9.0)
        ivy_add(plane, 'climb', sx * 21.8, YT, 14.0, 1.8); ivy_add(plane, 'climb', sx * 12.6, YT, 11.0, 1.4)
    x0, x1 = sorted((sx * SB0, sx * SB1))
    rs.box(x0, x1, YT, 25.8, ZP, ZP + 6, wall_sh(plane, 7.0, 61 + sx, SB_COURSES), plain(LIME, 5.0), cls='wall')
    for w in WINS[plane]: place_glass(w, ZP)
    # the balustraded parapet
    rs.box(x0 - 0.2, x1 + 0.2, 25.8, 26.3, ZP - 0.4, ZP + 0.4, plain(LIME, 8.6), plain(LIME, 6.0), top=plain(LIME, 9.6), bottom=plain(LIME, 3.2), cls='prop')
    rs.quad((x0, 26.3, ZP - 0.3), (x1, 26.3, ZP - 0.3), (x0, 27.4, ZP - 0.3), lambda x, y, s, t, z, wp: (fogged(baluster(x, y, s, t, z, wp), z) if baluster(x, y, s, t, z, wp) else None), cls='prop', cut=True)
    rs.box(x0 - 0.1, x1 + 0.1, 27.4, 27.75, ZP - 0.4, ZP + 0.3, plain(LIME, 8.8), plain(LIME, 6.0), top=plain(LIME, 9.8), cls='prop')
    for i in range(int(abs(SB1 - SB0) * 2.2)):                                    # the roof garden behind the balustrade
        X = x0 + (i + 0.5) / (abs(SB1 - SB0) * 2.2) * (x1 - x0)
        mound(X, 27.6 + rng(i, sx, 3) * 0.4, ZP + 0.9, 0.55 + rng(i, sx, 4) * 0.3, FOLI, 3.6, 400 + i + sx * 50, ragged=0.2)
        if GROWTH and i % 2 == 0: bloom(X, 28.3, ZP + 0.4, 0.16, FLW[i % 5] if i % 3 else BLOSSOM[3], i)
    # a thin buttress between the two windows and the corner pier
    mx0, mx1 = sorted((sx * 16.6, sx * 17.7))
    rs.box(mx0, mx1, YT, 27.75, ZP - 0.8, ZP, wall_sh(plane, 7.6, 63), plain(LIME, 5.4), top=plain(LIME, 9.0), cls='wall')
    cone(sx * 17.15, ZP - 0.4, 0.5, 27.75, 30.2, lambda x, y, s, t, z, wp: fogged(tone(LIME, 7.8 - t * 1.6, x, y), z), n=6)
    finial(sx * 17.15, 30.1, ZP - 0.45, h=0.4)
    cx0, cx1 = sorted((sx * SB1, sx * (SB1 + 1.8)))
    ivy_add('corner%d' % sx, 'band', cx0 + 0.25, cx1 - 0.25, YT + 1.0, 7.5)
    ivy_add('corner%d' % sx, 'fringe', cx0, cx1, 24.0, 0.5)
    pier(cx0, cx1, ZP - 0.8, ZP + 2.0, 28.4, 3.6, 'corner%d' % sx)
    # the roof behind the parapet, patina copper with standing seams
    rs.quad((x0, 26.4, ZP + 0.6), (x1, 26.4, ZP + 0.6), (x0, 31.0, ZP + 7.5),
            lambda x, y, s, t, z, wp: fogged(tone(PATINA, 3.4 + t * 1.6 - (1.2 if (wp[0] * 1.6) % 1 < 0.12 else 0) + (wn(1, wp[0], wp[2]) - 0.5) * 0.8, x, y), z), cls='wall')

# --- the wings
WG0, WG1 = SB1 + 1.8, 42.4
for sx in (-1, 1):
    plane = 'wing%d' % sx
    for i, cxu in enumerate((28.4, 33.6, 38.8)):
        win_add(plane, sx * cxu, YT, 7.6, 1.95, 1.5, kind='loggia', lit=0.0, lights=1, seed=40 + i)
        win_add(plane, sx * cxu, 12.2, 16.0, 1.35, 1.5, lit=(0.55 if (i + (sx > 0)) % 3 != 1 and not DECAY else 0.0), lights=1, seed=50 + i + sx)
        ivy_add(plane, 'swag', sx * cxu - 2.4, sx * cxu + 2.4, 19.2, 1.2, 0.36)
    ivy_add(plane, 'fringe', min(sx * WG0, sx * WG1), max(sx * WG0, sx * WG1), 10.5, 0.5)
    ivy_add(plane, 'climb', sx * 26.0, YT, 8.0, 1.0)
    if GROWTH:
        ivy_add(plane, 'drape', min(sx * WG0, sx * WG1), max(sx * WG0, sx * WG1), 19.6, 7.5)
        ivy_add(plane, 'climb', sx * 31.0, YT, 12.0, 2.2); ivy_add(plane, 'climb', sx * 41.4, YT, 16.0, 2.0)
    x0, x1 = sorted((sx * WG0, sx * WG1))
    rs.box(x0, x1, YT, 19.8, ZO, ZO + 8, wall_sh(plane, 6.6, 71 + sx, [(10.9, 0.34), (19.4, 0.45)]), plain(LIME, 4.8), cls='wall')
    for w in WINS[plane]:
        if w.kind == 'loggia':
            def loggia(x, y, s, t, z, wp, w=w):
                """the shadowed loggia behind the arch: a lit door at its back, the vault's dark"""
                X, Y, Z = wp
                if Y < w.y0 or w.aw(X, Y) > w.w: return None
                u = (X - w.cx) / w.w; q = (Y - w.y0) / (w.top - w.y0)
                if abs(u) < 0.38 and q < 0.62:
                    if abs(u) > 0.32 or q > 0.56: return tone(LIME, 2.4, x, y)
                    if DECAY and w.seed % 2: return tone(GLASSD, 1.6 + q, x, y)
                    return tone(LANT, 2.6 - q * 1.2 + (0.5 if abs(u) < 0.1 else 0), x, y)
                return tone(LIME, 1.4 + (1 - q) * 1.2 - abs(u) * 0.6 + (0.6 if Y < w.y0 + 0.3 else 0), x, y)
            rs.quad((w.cx - w.w, w.y0, ZO - 0.02), (w.cx + w.w, w.y0, ZO - 0.02), (w.cx - w.w, w.top + 0.05, ZO - 0.02), loggia, cls='emit' if not DECAY else 'prop', cut=True)
        else:
            place_glass(w, ZO)
    rs.box(x0 - 0.2, x1 + 0.2, 19.8, 20.3, ZO - 0.4, ZO + 0.4, plain(LIME, 8.6), plain(LIME, 6.0), top=plain(LIME, 9.6), bottom=plain(LIME, 3.2), cls='prop')
    rs.quad((x0, 20.3, ZO - 0.3), (x1, 20.3, ZO - 0.3), (x0, 21.3, ZO - 0.3), lambda x, y, s, t, z, wp: (fogged(baluster(x, y, s, t, z, wp), z) if baluster(x, y, s, t, z, wp) else None), cls='prop', cut=True)
    rs.box(x0 - 0.1, x1 + 0.1, 21.3, 21.65, ZO - 0.4, ZO + 0.3, plain(LIME, 8.8), plain(LIME, 6.0), top=plain(LIME, 9.8), cls='prop')
    for i in range(int(abs(WG1 - WG0) * 2.0)):                                    # the roof garden behind the balustrade
        X = x0 + (i + 0.5) / (abs(WG1 - WG0) * 2.0) * (x1 - x0)
        mound(X, 21.5 + rng(i, sx, 5) * 0.4, ZO + 0.9, 0.55 + rng(i, sx, 6) * 0.3, FOLI, 3.6, 500 + i + sx * 50, ragged=0.2)
        if GROWTH and i % 2 == 1: bloom(X, 22.2, ZO + 0.4, 0.16, FLW[(i + 2) % 5], i + 9)
    rs.quad((x0, 20.4, ZO + 0.6), (x1, 20.4, ZO + 0.6), (x0, 23.0, ZO + 8.0),
            lambda x, y, s, t, z, wp: fogged(tone(PATINA, 3.0 + t * 1.4 - (1.2 if (wp[0] * 1.6) % 1 < 0.12 else 0), x, y), z), cls='wall')

    # the conservatory dome: a drum, then a hemisphere of glass panes on iron ribs, plants pressing inside
    DX, DZ, DR, DY = sx * 33.6, 45.0, 6.4, 23.4
    def drum(x, y, s, t, z, wp, DX=DX, DZ=DZ):
        X, Y, Z = wp
        phi = math.atan2(X - DX, -(Z - DZ))
        if abs(Y - (DY - 1.0)) < 0.45 and abs(((phi / (2 * math.pi) * 16) % 1) - 0.5) < 0.18: return fogged(tone(LANT if not DECAY else GLASSD, 2.4, x, y), z)
        return fogged(masonry(LIME, DR * phi, Y, z, x, y, 7.0 + 1.0 * math.cos(phi + 0.5), ch=0.5, L=1.0, seed=81), z)
    cylinder(DX, DZ, DR + 0.25, 21.6, DY, drum, n=32)
    def dome_sh(x, y, s, t, z, wp, DX=DX, DZ=DZ, sx=sx):
        X, Y, Z = wp
        phi = math.atan2(X - DX, -(Z - DZ)); el = math.asin(max(-1.0, min(1.0, (Y - DY) / DR)))
        ps = z / F
        lon = (phi / (2 * math.pi) * 24) % 1; lat = (el / (math.pi / 2) * 6) % 1
        if lon < ps * 3.2 or lon > 1 - ps * 1.2 or lat < ps * 2.6: return fogged(tone(IRON, 2.4 + (0.8 if lon < ps * 1.4 else 0), x, y), z)
        pane = (int(phi / (2 * math.pi) * 24 + 48), int(el / (math.pi / 2) * 6))
        k = h32(pane[0], pane[1], 83 + sx)
        if DECAY and k % 5 == 0: return (20, 20, 18)                                                    # a pane missing
        q = el / (math.pi / 2)
        v = 4.0 + q * 2.6 + math.cos(phi + 0.6) * 0.9 + ((k % 5) - 2) * 0.25                          # the sky in the glass
        c = tone(GLASSD, v, x, y)
        plants = wn(2, phi * 9 + sx * 5, q * 5)
        if q < 0.7 and plants > 0.48 - (0.12 if GROWTH else 0) + q * 0.25:                               # fronds behind the glass
            c = mix(c, tone(LUSH if GROWTH else DEAD if DECAY else IVY, 2.6 + (plants - 0.5) * 4, x, y), 0.7)
        if not DECAY and q < 0.35 and k % 4 == 0: c = mix(c, LANT[2], 0.35)                           # lamps inside
        if GROWTH and q < 0.5 and k % 3 == 0: c = mix(c, (190, 200, 180), 0.2)                          # condensation
        if DECAY and k % 7 == 1: c = mix(c, (28, 24, 18), 0.5)                                          # grime
        return fogged(c, z)
    NL, NE = 32, 8
    for i in range(NL):
        a0 = -math.pi + 2 * math.pi * i / NL; a1 = a0 + 2 * math.pi / NL
        if math.cos((a0 + a1) / 2) < -0.2: continue
        for j in range(NE):
            e0 = (math.pi / 2) * j / NE; e1 = (math.pi / 2) * (j + 1) / NE
            P = lambda a, e: (DX + DR * math.cos(e) * math.sin(a), DY + DR * math.sin(e), DZ - DR * math.cos(e) * math.cos(a))
            tri(P(a0, e0), P(a1, e0), P(a0, e1), dome_sh, cls='prop')
            tri(P(a1, e1), P(a0, e1), P(a1, e0), dome_sh, cls='prop')
    rs.disc(DX, DY + DR + 0.4, DZ - 0.4, 0.5, lambda x, y, s, t, z, wp: fogged(tone(IRON, 2.8 - t * 1.4, x, y), z))
    finial(DX, DY + DR + 0.6, DZ - 0.5, h=1.0)

    # the end turret: a round tower, slit windows, a corbelled cornice, a patina spire
    TX, TZ, TR = sx * 44.0, 38.8, 2.3
    ivy_add('turret%d' % sx, 'climb', 0.0, YT, 11.0 if not GROWTH else 18.0, 1.4)
    def turret(x, y, s, t, z, wp, TX=TX, TZ=TZ):
        X, Y, Z = wp
        phi = math.atan2(X - TX, -(Z - TZ)); u = TR * phi
        e = ivy_at('turret%d' % (1 if TX > 0 else -1), u, Y)
        if e > 0: return ivy_col(u, Y, e, x, y, z)
        lit = 1.4 * math.cos(phi + 0.5) - 0.6
        if abs(u) < 0.32 and (6.0 < Y < 9.0 or 14.0 < Y < 17.0): return tone(LANT if (not DECAY and Y < 10) else GLASSD, 2.0, x, y)
        if abs(u) < 0.55 and (5.7 < Y < 9.3 or 13.7 < Y < 17.3): return tone(LIME, 8.4 + lit, x, y)
        return fogged(masonry(LIME, u, Y, z, x, y, 6.8 + lit, ch=0.55, L=0.9, seed=91), z)
    cylinder(TX, TZ, TR, YT, 23.0, turret, n=28)
    cylinder(TX, TZ, TR + 0.35, 23.0, 23.7, lambda x, y, s, t, z, wp: fogged(tone(LIME, 8.6 - (1.6 if t < 0.3 else 0), x, y), z), n=28)
    def spire(x, y, s, t, z, wp, TX=TX, TZ=TZ):
        X, Y, Z = wp
        phi = math.atan2(X - TX, -(Z - TZ))
        lit = 1.2 * math.cos(phi + 0.5) - 0.4
        row = math.floor(Y / 0.34); u = (phi * 6 + (row % 2) * 0.5)
        v = 3.4 + lit + ((h32(int(u * 3), row, 5) % 5) - 2) * 0.18 + (wn(2, phi * 4, Y * 0.8) - 0.5) * 0.8
        if (Y / 0.34) % 1 < 0.22: v -= 1.1
        return fogged(tone(PATINA, v, x, y), z)
    cone(TX, TZ, TR + 0.45, 23.7, 30.2, spire, n=28)
    finial(TX, 30.1, TZ - 0.3, h=0.9)

# ---------------------------------------------------------------------------------------------------- the terrace
def terrace(x, y, s, t, z, wp):
    X, _, Z = wp
    D = 1.6; row = math.floor(Z / D); fz = Z / D - row
    Wd = 1.8; uu = X + (row % 2) * 0.9; col = math.floor(uu / Wd); fx = uu / Wd - col
    v = 5.6 + (h32(col, row, 9) % 5 - 2) * 0.18 + (wn(0, X * 0.3, Z * 0.3) - 0.5) * 0.8
    if fx < z / F / Wd * 1.2 or fz < z * z / (F * CAMH) / D * 1.2: v -= 1.8
    c = tone(PAVE, v, x, y)
    if DECAY and h32(int(X * 3 + 99), int(Z * 3), 63) % 13 == 0 and ((X * 3) % 1 - 0.5) ** 2 + ((Z * 3) % 1 - 0.5) ** 2 < 0.1: c = tone(DEAD, 3.0, x, y)
    return fogged(c, z)
rs.quad((-120, YT, ZW), (120, YT, ZW), (-120, YT, 70), terrace, cls='ground')
# the city houses at the sides, behind the terrace: several houses with setbacks, balconies, chimneys, in the haze
HOUSES = ((51.0, 62.0, 49.0, 33.0, STUCCO, 2.0, 8), (62.0, 71.0, 53.0, 37.0, STONE, 3.4, 9), (71.0, 84.0, 50.5, 30.0, STUCCO, 2.6, 10),
          (84.0, 100.0, 58.0, 35.0, STONE, 3.0, 11), (100.0, 150.0, 64.0, 31.0, STUCCO, 2.2, 12))
for sx in (-1, 1):
    for (a, b, zf, ht, mat, v0, seed) in HOUSES:
        x0, x1 = sorted((sx * a, sx * b))
        base = shedkit.concrete(v0, mat)
        rs.box(x0, x1, 0, ht, zf, zf + 20.0, shedkit.facade(base, bay=4.4, floors=4.4, y0=3.6, seed=seed + sx * 7, wf=0.36), base, cls='wall')
        shedkit.balconies(rs, zf, x0 + 1.0, x1 - 1.0, False, 4.4, 4.4, 3.6, seed + sx * 3, ht, every=3)
        rs.box(x0 - 0.6, x1 + 0.6, ht, ht + 0.9, zf - 0.6, zf + 20.0, plain(mat, v0 + 1.6), plain(mat, v0), bottom=plain(mat, 0.6), cls='prop')
        rs.quad((x0, ht + 0.9, zf + 0.3), (x1, ht + 0.9, zf + 0.3), (x0, ht + 5.5, zf + 7.0),
                lambda x, y, s, t, z, wp: fogged(tone(METAL, 1.8 + t * 1.4 - (0.8 if (wp[0] * 1.2) % 1 < 0.1 else 0), x, y), z), cls='wall')
        for k in range(2):                                                                # chimneys
            cxh = x0 + (x1 - x0) * (0.25 + 0.5 * k) + (rng(seed, k) - 0.5) * 2
            if rng(seed, k, sx) < 0.4: continue
            rs.box(cxh - 0.5, cxh + 0.5, ht + 0.9, ht + 3.4 + rng(seed, k, 2) * 1.4, zf + 2.5, zf + 3.5, shedkit.concrete(2.4, STONE), shedkit.concrete(1.6, STONE), cls='prop')
# hedges and flower rows along the facade, the wings' beds, the terrace lamps
for sx in (-1, 1):
    a, b = sorted((sx * 11.6, sx * 22.8))
    hedge(a, b, YT, YT + 1.7, ZP - 2.3, ZP - 0.2, 101 + sx)
    flower_bed(a, b, ZP - 3.6, ZP - 2.3, YT, 111 + sx, rows=[3, 4] if sx < 0 else [4, 3])
    a, b = sorted((sx * 25.0, sx * 41.6))
    hedge(a, b, YT, YT + 1.5, ZO - 2.1, ZO - 0.2, 121 + sx)
    flower_bed(a, b, ZO - 3.2, ZO - 2.1, YT, 131 + sx, rows=[1, 0])
    lamp(sx * 9.4, YT, 28.4, 5.0, 140 + sx, big=False, out=(DECAY and sx > 0))
    urn(sx * 8.1, 2.15, ZS0 + 0.4)
    mound(sx * 8.1, 3.55, ZS0 + 0.3, 0.7, FOLI, 4.0, 150 + sx, ragged=0.3)
    for j in range(5 if not DECAY else 2):
        bloom(sx * 8.1 + (j - 2) * 0.28, 3.75 + (j % 2) * 0.25, ZS0 - 0.15, 0.15, FLW[(j + (sx > 0)) % 5] if not DECAY else tone(DEAD, 4.6, 0, 0), 160 + j)
    if GROWTH:
        for j in range(8):
            mound(sx * 8.1 + (rng(j, sx) - 0.5) * 1.4, 2.4 - j * 0.12, ZS0 - 0.7, 0.2, LUSH, 4.0, 170 + j, ragged=0)

# ---------------------------------------------------------------------------------------------------- the front beds
def bed_face(sx):
    plane = 'bedf%d' % sx
    if GROWTH: ivy_add(plane, 'drape', -40, 40, BEDH, 0.9)
    return wall_sh(plane, 6.6, 201 + sx, [(BEDH - 0.1, 0.18)], ch=0.5, L=1.0)
def bed_top(x, y, s, t, z, wp):
    X, Y, Z = wp
    ax = abs(X)
    edge = min(ax - BEDX[0], BEDX[1] - ax, Z - ZBED[0], ZBED[1] - Z)
    if edge < 0.42: return fogged(tone(LIME, 9.0 - (1.6 if edge > 0.34 else 0) + (wn(1, X * 2, Z * 2) - 0.5) * 0.6, x, y), z)   # coping
    c = tone(SOIL, 2.4 + (wn(0, X * 1.5, Z * 1.5) - 0.5) * 1.6, x, y)
    if DECAY and X < 0: c = mix(c, (96, 92, 82), 0.45 + 0.2 * wn(2, X * 2, Z * 2))       # the blighted bed: crusted grey
    return fogged(c, z)
for sx in (-1, 1):
    x0, x1 = sorted((sx * BEDX[0], sx * BEDX[1]))
    rs.box(x0, x1, 0, BEDH, ZBED[0], ZBED[1], bed_face(sx), wall_sh('beds%d' % sx, 5.0, 203, u_of=lambda wp: wp[2], ch=0.5, L=1.0),
           top=bed_top, cls='wall')
    inner = sx * BEDX[0]
    # rows: the Directorate plants in bands (cream at the front, then coral, gold, rose)
    sick = DECAY and sx < 0
    flower_bed(x0 + 0.5, x1 - 0.5, ZBED[0] + 0.45, ZBED[1] - 0.45, BEDH, 211 + sx, rows=[4, 0, 2, 3] if sx < 0 else [4, 1, 2, 0],
               spill=(0.5 if GROWTH else 0.0), sick=sick, border=not sick)
    spiral(sx * 24.4, BEDH, 18.4, 5.4, 1.15, 7 + sx)
    lamp(sx * 27.4, BEDH, 19.2, 9.6, 220 + sx, out=(DECAY and sx < 0))
    if sx > 0: shrub_ball(16.4, BEDH, 19.8, 1.25, 231)
# the sealed cold-frame at the back of the left bed (Verrik keeps the cultivar behind glass)
def coldframe(x, y, s, t, z, wp):
    X, Y, Z = wp
    if s < 0.05 or s > 0.95 or t < 0.08 or t > 0.92 or abs(s - 0.5) < 0.03: return fogged(tone(WOOD, 3.0 if t > 0.5 else 2.0, x, y), z)
    c = tone(GLASSD, 3.8 + t * 1.6, x, y)
    if t < 0.55 and wn(2, X * 4, Y * 4) > 0.45: c = mix(c, tone(DEAD if DECAY else IVY, 2.4, x, y), 0.6)     # the cultivar inside
    if DECAY and abs((s * 3) % 1 - t) < 0.06: c = tone(GLASSD, 6.6, x, y)
    return fogged(c, z)
rs.box(-19.0, -16.4, BEDH, BEDH + 1.1, 20.0, 21.0, coldframe, coldframe,
       top=lambda x, y, s, t, z, wp: fogged(tone(GLASSD, 5.0 + (wn(1, wp[0] * 2, wp[2] * 2) - 0.5), x, y), z), cls='prop')

# ---------------------------------------------------------------------------------------------------- points for the scene
def P(X, Y, Z): x, y = proj(X, Y, Z); return [round(x), round(y)]
PTS['portal'] = [P(-DOOR.w, YT, ZC), P(DOOR.w, YT, ZC), P(0, DOOR.top, ZC)]
PTS['vent'] = [P(VENT[0], VENT[3], ZW), P(VENT[1], VENT[2], ZW)]
PTS['bed_left_top'] = [P(-BEDX[1], BEDH, ZBED[1]), P(-BEDX[0], BEDH, ZBED[0])]
PTS['bed_right_top'] = [P(BEDX[0], BEDH, ZBED[1]), P(BEDX[1], BEDH, ZBED[0])]
PTS['great_window'] = [P(-GREAT.w, GREAT.y0, ZC), P(GREAT.w, GREAT.top, ZC)]
PTS['gable_apex'] = P(0, GA, ZC)
PTS['steps'] = [P(-7, 0, ZS0), P(7, YT, ZW)]

KW = dict(variant=VARIANT, light_gain=0.6, grime_gain=1.7, bloom=0.22, stain_gain=1.6, damp_gain=0.8)
MIRROR = lambda x, y, wp: 0.75 * puddle(wp[0], wp[2])
NAME = 'lumen' if VARIANT == 'base' else 'lumen_' + VARIANT
if GROWTH:
    # the surplus bloom: a swollen, over-ripe flower head on the right bed -- rendered into a second pass and cut out
    # (pixels of the bloom's objects, plus a 1-px outline where the two renders differ) so the scene can harvest it
    n_before = rs.n
    img0 = rs.render(INK, fog=fogk, mirror=MIRROR, **KW)
    SBX, SBZ = 21.0, 17.6
    rs.line3((SBX, BEDH, SBZ), (SBX + 0.2, BEDH + 1.6, SBZ), lambda x, y, s, t, z, wp: fogged(LUSH[3] if x % 2 else LUSH[2], z), w=0.18)
    for k in range(5):
        a = k * 2 * math.pi / 5
        mound(SBX + math.cos(a) * 0.55, BEDH + 1.4 + math.sin(a) * 0.3, SBZ - 0.2, 0.42, LUSH, 4.2, 300 + k, ragged=0)
    def pod(x, y, s, t, z, wp):
        d = s * s + t * t
        if d > 1: return None
        v = 3.8 - s * 1.0 - t * 1.6
        if abs((math.atan2(t, s) * 5 / math.pi) % 1 - 0.5) < 0.08 and d > 0.15: v -= 1.2       # petal seams
        c = tone(ramp('#5a2f3a #7a4250 #9c5c6a #bd7e88 #d8a4aa #ecc6c4'), v, x, y)
        if d < 0.08: c = (226, 214, 150)                                                     # the pollen eye
        return c
    rs.disc(SBX + 0.2, BEDH + 2.3, SBZ - 0.5, 0.75, pod, cls='emit')
    img1 = rs.render(INK, fog=fogk, mirror=MIRROR, **KW)
    a = img0.load(); b = img1.load()
    mask = set((x, y) for y in range(H) for x in range(W) if rs.G[y][x] is not None and rs.G[y][x][1] > n_before)
    xs = [p[0] for p in mask]; ys = [p[1] for p in mask]
    bx0, by0, bx1, by1 = min(xs) - 1, min(ys) - 1, max(xs) + 2, max(ys) + 2
    spr = Image.new('RGBA', (bx1 - bx0, by1 - by0), (0, 0, 0, 0)); sp = spr.load()
    for y in range(by0, by1):
        for x in range(bx0, bx1):
            if (x, y) in mask or (a[x, y] != b[x, y] and any((x + dx, y + dy) in mask for dx in (-1, 0, 1) for dy in (-1, 0, 1))):
                sp[x - bx0, y - by0] = b[x, y] + (255,)
    spr.save(f'{OUT}/surplus_bloom.png')
    PTS['surplus_bloom'] = {'topleft': [bx0, by0], 'size': list(spr.size), 'centre_bottom': [(bx0 + bx1) // 2, by1]}
    img0.save(f'{OUT}/{NAME}.png')
else:
    img = rs.render(INK, fog=fogk, mirror=MIRROR, **KW)
    img.save(f'{OUT}/{NAME}.png')
json.dump(PTS, open(f'{OUT}/lumen_points.json' if VARIANT == 'base' else f'{OUT}/lumen_points_{VARIANT}.json', 'w'), indent=1)
print('done', VARIANT, PTS)
