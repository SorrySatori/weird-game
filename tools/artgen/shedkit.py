"""Shared pieces for the Shed 521 grounds (the gate, the mutation courtyard, the registration yard) on raster3d.py:
the overcast sky, world-space material shaders in the Crossroad palette (pal_day) -- weathered timber, corrugated
sheet, riveted steel, concrete, setts -- and people: camera-facing billboard figures (hooded applicants, some of them
visibly mutated), standing or seated."""
import math
from common import h32, make_noise, band
from pal_day import SKY, HAZE, STONE, WOOD, WARM, RED, METAL, LEAF, CAP, MYC, STUCCO, GLOW, BONE, FOG, INK, FLOWER, ramp
from raster3d import Raster, proj, ray, W, H, CX, HY, F, CAMH

_nz = [make_noise(1, s, 509, 509) for s in (41, 42, 43, 44)]
def wn(i, a, b): return _nz[i](a + 3000.0, b + 3000.0)              # noise in WORLD units
_scr = make_noise(13, 45, W, H); _scr2 = make_noise(48, 46, W, H)
def ri(r, i): return r[max(0, min(len(r) - 1, int(i)))]
def tone(r, v, x, y): return ri(r, band(v, x, y))
def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def fog_of(z): return max(0.0, min(0.82, 1 - math.exp(-(z - 14) / 70.0)))
def fogged(c, z, k=1.0): return mix(c, FOG, fog_of(z) * k)

RUSTY = ramp('#24120a #3a1d10 #552a16 #6f381d #8a4a26 #a35e33')
TEAL = ramp('#0e2224 #163234 #1f4446 #2a5858 #376c6a #4a827c')
OCHRE = ramp('#2a1f0e #403016 #5a4420 #74592b #8e6f38')
MAUVE = ramp('#24151f #35202e #4a2c40 #603a53 #774a66')
OLIVE = ramp('#1a1f12 #262d1a #343d23 #444e2d #556138')
SLATE = ramp('#151a20 #20262e #2c343e #39434e #47525e')
ROBES = [RUSTY, TEAL, OCHRE, MAUVE, OLIVE, SLATE, RUSTY, OCHRE]

def sky(x, y, s=0, t=0, z=0, wp=None):
    """the overcast day, darker overhead, hazy at the horizon, long soft cloud bands"""
    tt = max(0.0, min(1.0, y / HY))
    v = 1.2 + 4.6 * tt ** 1.4 + (_scr2(x * 0.55, y * 2.6) - 0.5) * 1.6 + (_scr(x * 0.5, y * 2.4) - 0.5) * 0.5
    return tone(SKY, v, x, y)

def horiz(wp, nrm):
    return wp[2] if nrm is not None and abs(nrm[0]) > 0.7 else wp[0]

def planks(v0, r=WOOD, w=0.9, vertical=True, seed=0, damp=True):
    """weathered boards: dark seams, knots, a grey bleached top, a damp foot"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = X if vertical else Y
        pl = math.floor(u / w); fu = u / w - pl
        v = v0 + (h32(pl, seed, 1) % 3) * 0.35 - 0.6 * (wn(0, u * 0.6, Y * 3.0 if vertical else X * 3.0) - 0.5)
        if fu < 0.9 * z / F / w + 0.04: v -= 1.4                                         # the seams
        if h32(pl, int(Y * 2.3), seed) % 23 == 0: v -= 0.9                                # knots / rot
        if damp: v -= 0.9 * max(0.0, 1 - Y / 2.5)
        return fogged(tone(r, v, x, y), z)
    return sh

def planks_z(v0, r=WOOD, w=0.9, seed=0):
    """boards on a side wall (they run along z)"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        pl = math.floor(Z / w); fu = Z / w - pl
        v = v0 + (h32(pl, seed, 1) % 3) * 0.35 - 0.6 * (wn(0, Z * 0.6, Y * 3.0) - 0.5)
        if fu < 0.9 * z * z / (F * max(1.0, abs(X))) / w + 0.04: v -= 1.4
        if h32(pl, int(Y * 2.3), seed) % 23 == 0: v -= 0.9
        v -= 0.9 * max(0.0, 1 - Y / 2.5)
        return fogged(tone(r, v, x, y), z)
    return sh

def corrugated(v0, r=METAL, rust=0.5, along_z=False):
    """corrugated sheet: ribs every half unit, rust bleeding down from the top and the bolts"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = Z if along_z else X
        v = v0 + 0.8 * math.sin(u * 2 * math.pi / 0.5) * min(1.0, 18 / z) + (wn(1, u * 0.5, Y * 0.5) - 0.5) * 0.6
        ln = 0.5 + 3.0 * wn(3, u * 0.7, 3.0)                                            # rust runs down from the top edge
        if wn(2, u * 3.0, 1.0) > 1 - rust * 0.4 and (1 - t) * 8.0 < ln * rust * 1.3:
            return fogged(tone(RUSTY, v - 0.4 - (1 - t) * 2, x, y), z)
        return fogged(tone(r, v, x, y), z)
    return sh

def steel(v0, r=METAL, rivets=1.2, rust=0.4):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = v0 + (wn(1, X * 0.8 + Z, Y * 0.8) - 0.5) * 0.8
        if (s * 10) % 1 < 0.08 or (t * 6) % 1 < 0.08: v -= 0.8                          # plate seams
        if ((s * 10) % 1 < 0.2 and (t * 6 * rivets) % 1 < 0.12): v += 1.2                # rivets
        c = tone(r, v, x, y)
        ln = 0.4 + 2.4 * wn(3, (X + Z) * 0.8, 5.0)                                     # rust runs down from seams and rivets
        if wn(2, (X + Z) * 2.6, 2.0) > 1 - rust * 0.4 and ((1 - t) * 6) % 1.0 * 1.6 < ln * rust: c = tone(RUSTY, v + 0.2, x, y)
        return fogged(c, z)
    return sh

def concrete(v0, r=STONE):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = v0 + (wn(0, X * 0.5 + Z * 0.5, Y * 0.5) - 0.5) * 0.45 + (wn(1, (X + Z) * 1.6, Y * 0.2) - 0.5) * 0.4 - 0.9 * max(0.0, 1 - Y / 2.0)
        return fogged(tone(r, v, x, y), z)
    return sh

def setts(x, y, s, t, z, wp, v0=4.6, mud=0.0):
    """worn setts in the yard, mud between them"""
    X, _, Z = wp
    SXc, SZc = 1.0, 0.75
    row = math.floor(Z / SZc); col = math.floor(X / SXc + (row % 2) * 0.5)
    fx = (X / SXc + (row % 2) * 0.5) - col; fz = Z / SZc - row
    ex, ez = 1.05 * Z / F / SXc, 1.05 * Z * Z / (F * CAMH) / SZc
    v = v0 + (0.8 if h32(col, row, 7) % 4 == 0 else 0) - (0.8 if h32(col, row, 8) % 5 == 0 else 0)
    if Z < 75 and (fx < ex or fz < ez): v = 2.4
    v += 0.6 * (wn(1, X * 2, Z * 2) - 0.5)
    m = wn(2, X * 0.35, Z * 0.35) + mud + (wn(3, X * 1.5, Z * 1.5) - 0.5) * 0.12
    c = tone(STONE, v, x, y)
    if m > 0.66: c = mix(c, tone(WARM, 1.6 + (wn(0, X * 3, Z * 3) - 0.5), x, y), min(0.55, (m - 0.66) * 6))    # trodden mud
    return fogged(c, Z)

def windows_sh(base, cols=2.4, rows=3.2, lit=0.15, seed=0, along_z=False):
    """a facade with a grid of dark windows (a few lit) over a wall material"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = Z if along_z else X
        fu, fv = (u / cols) % 1, (Y / rows) % 1
        if Y > 2.5 and 0.28 < fu < 0.72 and 0.3 < fv < 0.8:
            k = h32(int(u / cols), int(Y / rows), seed)
            c = GLOW[1] if k % 100 < lit * 100 else STONE[1] if k % 3 else STONE[0]
            return fogged(c, z, 0.8)
        return base(x, y, s, t, z, wp)
    return sh

# ---------------------------------------------------------------------------------------------------- people
def person(rs, X, Z, seed, h=6.2, seated=False, kind=None, Y0=0.0, facing=None, glow_eyes=None, papers=None):
    """a hooded applicant as a camera-facing billboard with its own dark outline; kind: None (by seed) | 'hood' |
    'cap' (a mushroom cap grows out of the hood) | 'coral' (coral knobs sprout from it) | 'mask' (a gas mask, two
    green eyes)"""
    k = h32(seed, 11)
    kind = kind or ['hood', 'hood', 'cap', 'coral', 'mask', 'hood', 'coral', 'hood', 'hood'][k % 9]
    robe = ROBES[h32(seed, 12) % len(ROBES)]
    front = facing if facing is not None else (h32(seed, 13) % 3 != 0)
    lean = ((h32(seed, 14) % 7) - 3) * 0.01
    hunch = (h32(seed, 17) % 3) * 0.02
    papers = papers if papers is not None else (h32(seed, 18) % 3 == 0)
    side = 1 if h32(seed, 15) % 2 else -1
    hh = h * (0.6 if seated else 1.0)
    w = h * 0.56
    head_y = 0.86 - hunch
    glow = glow_eyes if glow_eyes is not None else (kind == 'mask')
    CORALS = [((h32(seed, 30 + i) % 9 - 4) * 0.025, 0.93 + (h32(seed, 40 + i) % 5) * 0.02, 0.04 + (h32(seed, 50 + i) % 3) * 0.015) for i in range(5)]
    def part(u, v):
        hu = u - lean * 2 - hunch * side * 0.6
        if kind == 'cap' and ((hu / 0.3) ** 2 + ((v - head_y - 0.09) / 0.055) ** 2 < 1) and v > head_y + 0.07: return 'cap'
        if kind == 'coral' and any(math.hypot(hu - cx, v - cy) < cr for (cx, cy, cr) in CORALS): return 'coral'
        if (hu / 0.135) ** 2 + ((v - head_y) / 0.11) ** 2 < 1 or (abs(hu) < 0.16 and head_y - 0.12 < v < head_y - 0.02): return 'hood'
        sh_y = 0.76 - hunch
        if v < sh_y:
            rw = 0.2 + 0.06 * max(0.0, 1 - v / 0.55) - 0.1 * max(0.0, (v - sh_y + 0.08) / 0.08) ** 2
            if abs(u - lean * v * 2) < rw and not (v < 0.035 and abs(u - lean * v * 2) < 0.025): return 'robe'
            if 0.4 < v < 0.68 and rw - 0.01 < (u - lean * v * 2) * side < rw + 0.065: return 'arm'
            if papers and 0.42 < v < 0.52 and rw + 0.02 < (u - lean * v * 2) * side < rw + 0.12: return 'paper'
        return None
    def sh(x, y, s, t, z, wp):
        u = s - 0.5; v = t * (0.6 if seated else 1.0) + (0.4 if seated else 0.0)
        p = part(u, v)
        if p is None: return None
        du = 1.0 / (w * F / z); dv = 1.0 / (hh * F / z) * (0.6 if seated else 1.0)
        edge = any(part(u + a * du, v + b * dv) is None for (a, b) in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        light = -u * 2.6
        if p == 'cap': c = tone(CAP, 3.6 - (v - head_y) * 12 + light, x, y)
        elif p == 'coral':
            hu = u - lean * 2 - hunch * side * 0.6
            near = min(math.hypot(hu - cx, v - cy) / cr for (cx, cy, cr) in CORALS)
            c = tone(RED, 5.0 - near * 2.4 + light, x, y) if near > 0.35 else FLOWER[0]
        elif p == 'paper': c = BONE[4] if (x + y) % 3 else BONE[3]
        elif p == 'hood':
            hu = u - lean * 2 - hunch * side * 0.6
            opening = ((hu - 0.015) / 0.09) ** 2 + ((v - head_y + 0.01) / 0.08) ** 2
            if front and opening < 1 and kind != 'coral':
                if kind == 'mask':
                    if abs(v - head_y + 0.005) < 0.014 and abs(abs(hu - 0.015) - 0.03) < 0.014: return MYC[3] if glow else STONE[4]
                    return STONE[2] if v > head_y - 0.03 else STONE[1]
                if opening > 0.55 or v > head_y + 0.035: return STONE[0]                         # the hood's shadow
                return BONE[2] if hu < 0.01 else BONE[1]
            c = tone(robe, 3.0 + light + (v - head_y) * 5, x, y)
        else:
            fold = -0.7 if int((u + 0.5) * 22 + v * 3) % 5 == 0 else 0
            hem = -1.2 * max(0.0, 1 - v / 0.1)
            rim = 0.9 if p == 'robe' and u < 0 and part(u - 2.0 / (w * F / z), v) is None else 0             # the lit edge
            c = tone(robe, 2.6 + light + fold + hem + rim + (0.5 if p == 'arm' else 0) - (0.3 if not front else 0), x, y)
            if p == 'arm' and v < 0.44: c = BONE[1]                                                          # a hand
        if edge: c = mix(c, INK, 0.65)
        return fogged(c, z)
    rs.quad((X - w / 2, Y0, Z), (X + w / 2, Y0, Z), (X - w / 2, Y0 + hh, Z), sh, cut=True, cls='prop')

def post_rope(rs, pts, z_of=None):
    """queue stanchions with a sagging rope between them"""
    for (X, Z) in pts:
        rs.line3((X, 0.0, Z), (X, 2.8, Z), lambda x, y, s, t, z, wp: fogged(METAL[2] if t < 0.9 else GLOW[2], z), w=0.18)
        rs.disc(X, 0.1, Z, 0.35, lambda x, y, s, t, z, wp: fogged(METAL[1], z))
    for (a, b) in zip(pts, pts[1:]):
        rs.line3((a[0], 2.6, a[1]), (b[0], 2.6, b[1]), lambda x, y, s, t, z, wp: fogged(RED[2], z), w=0.1, sag=0.5)

# ---------------------------------------------------------------------------------------------------- people, drawn
from rig import Rig, Mat
SKINP = ramp('#2c2a24 #45413a #605a4f #7d7566 #9a917e #b4ab96')
BOOTS = ramp('#0e0c0a #1a1612 #26201a #342c24')
CORALR = ramp('#3a1414 #5e2020 #84302c #a8463a #c8644e #e08a6e')
PAPER = ramp('#6e6a5c #8e8a78 #b0ac98 #d0ccb6')

def applicant_img(seed, hpx, kind=None, view=None, seated=False, robe=None, skin=None, stone=False):
    """an applicant drawn with the character renderer (rig.py) at its on-screen height: a hooded robe, sometimes a
    mushroom cap or coral knobs growing out of the hood, or a gas mask; view 'front' | 'back' | 'right' | 'left'"""
    kind = kind or ['hood', 'hood', 'cap', 'coral', 'mask', 'hood', 'coral', 'hood', 'hood'][h32(seed, 11) % 9]
    view = view or ['front', 'right', 'right', 'back', 'front', 'right'][h32(seed, 13) % 6]
    robe = robe or ROBES[h32(seed, 12) % len(ROBES)]
    flip = view == 'left'
    if flip: view = 'right'
    k = hpx / 100.0
    top = 30 if seated else 0
    Wd, Hd = int(80 * k) + 6, int((104 - top) * k) + 6
    r = Rig(Wd, Hd)
    P = lambda x, y: (x * k + 3, (y - top) * k + 3)
    R_ = lambda v: v * k
    M_robe = Mat(robe, 'wool', 0.2); M_skin = Mat(skin or SKINP, 'skin', 0.24); M_boot = Mat(BOOTS, 'leather', 0.18, 0.3)
    hunch = (h32(seed, 17) % 3) * 2.0 + (6.0 if seated else 0.0)
    fwd = 1.0 if view == 'right' else 0.0
    papers = h32(seed, 18) % 3 == 0 and not seated
    hx, hy = 40 + hunch * fwd * 0.8, 19 + hunch * 0.5 + (8 if seated else 0)
    if not seated:
        for fx in ((34, 46) if view != 'right' else (36, 47)):
            r.ellipsoid(*P(fx, 98.5), R_(4.6), R_(2.2), M_boot, lift=-0.1, group='feet')
        body = [(29, 30), (51, 30), (53, 62), (56, 97), (24, 97), (27, 62)]
    else:
        body = [(29 + hunch, 36), (51 + hunch, 36), (53, 60), (55, 104), (25, 104), (27, 60)]
    if view == 'right': body = [(x - 2 if i in (0, 5, 4) else x, y) for i, (x, y) in enumerate(body)]
    # the far arm (behind the body in profile)
    if view == 'right':
        r.tube(P(36, 34 + hunch * 0.4), P(44 + hunch, 58 if not seated else 52), R_(4.4), R_(5.2), M_robe, lift=-0.25, group='armF')
    r.poly([P(*q) for q in body], M_robe, group='body',
           vfun=lambda x, y: -0.22 if int((x / k) * 0.55 + (y / k) * 0.12) % 3 == 0 and y / k > 40 - top else 0)
    # the hood: a drape over the shoulders and the hood itself
    r.poly([P(hx - 13, hy + 6), P(hx + 11, hy + 6), P(hx + 13, hy + 16), P(hx - 15, hy + 16)], M_robe, lift=0.05, group='drape')
    r.ellipsoid(*P(hx - (2.5 if view == 'right' else 0), hy), R_(10.5), R_(12.0), M_robe, lift=0.06, group='hood')
    if kind == 'cap':
        r.ellipsoid(*P(hx, hy - 11), R_(16.0), R_(4.6), Mat(MOSSTONE if stone else CAP, 'skin', 0.25), group='cap',
                    vfun=lambda x, y, u, w: -0.3 if w > 0.55 else (0.15 if (int(x / k * 0.7) + int(y / k)) % 5 == 0 else 0))
    if kind == 'coral':
        for i in range(5):
            cx = hx - 6 + (h32(seed, 30 + i) % 13); cy = hy - 10 - (h32(seed, 40 + i) % 7)
            r.ellipsoid(*P(cx, cy), R_(2.4 + (h32(seed, 50 + i) % 3)), R_(2.8 + (h32(seed, 60 + i) % 3)), Mat(MOSSTONE if stone else CORALR, 'skin', 0.3), group='coral')
    if view == 'front':
        r.ellipsoid(*P(hx + 0.5, hy + 2), R_(6.8), R_(8.6), M_robe, lift=-0.7, group='opening')
        if kind == 'mask':
            r.ellipsoid(*P(hx + 0.5, hy + 3), R_(4.8), R_(5.8), Mat(STONE, 'metal', 0.2, 0.4), lift=-0.1, group='face')
            for ex in (-2, 2): r.fixed(*P(hx + 0.5 + ex, hy + 2), MYC[3])
            r.ellipsoid(*P(hx + 0.5, hy + 8), R_(2.2), R_(1.8), Mat(STONE, 'metal', 0.2), lift=-0.2, group='filter')
        elif kind != 'coral':
            r.ellipsoid(*P(hx + 0.5, hy + 3.5), R_(4.4), R_(5.6), M_skin, lift=-0.35, group='face')
            for ex in (-1.8, 1.8): r.fixed(*P(hx + 0.5 + ex, hy + 2.6), SKINP[0])
        else:
            r.ellipsoid(*P(hx + 0.5, hy + 3.5), R_(4.4), R_(5.6), M_skin, lift=-0.35, group='face')
            for (ex, ey, er) in ((-2.2, 1.0, 1.6), (1.6, 4.5, 1.3), (2.4, 0.5, 1.0)):                  # coral knobs on the face
                r.ellipsoid(*P(hx + 0.5 + ex, hy + 3.5 + ey), R_(er), R_(er), Mat(MOSSTONE if stone else CORALR, 'skin', 0.3), group='knob')
    elif view == 'right':
        r.ellipsoid(*P(hx + 5.5, hy + 2), R_(4.6), R_(8.0), M_robe, lift=-0.7, group='opening')
        if kind == 'mask':
            r.ellipsoid(*P(hx + 6.5, hy + 3), R_(3.6), R_(5.0), Mat(STONE, 'metal', 0.2, 0.4), group='face')
            r.fixed(*P(hx + 8, hy + 2), MYC[3])
        elif kind != 'coral':
            r.ellipsoid(*P(hx + 6.5, hy + 3.5), R_(3.2), R_(5.2), M_skin, lift=-0.25, group='face')
            r.ellipsoid(*P(hx + 9.0, hy + 3.0), R_(1.2), R_(1.4), M_skin, lift=-0.1, group='face')
    # the near arm, hands, papers
    if view == 'right':
        hand = P(47 + hunch, 58 if not seated else 54)
        r.tube(P(42, 34 + hunch * 0.4), hand, R_(4.8), R_(5.6), M_robe, group='armN')
        r.ellipsoid(hand[0] + R_(1.5), hand[1] + R_(2.5), R_(2.4), R_(2.4), M_skin, group='hand')
    elif view == 'front':
        for (sx, ex_) in ((30, 27), (50, 52)):
            hand = P(ex_ + (6 if (papers and sx > 40) else 0) - (4 if seated else 0), 60 if not seated else 56)
            r.tube(P(sx, 34 + hunch * 0.3), hand, R_(4.6), R_(5.6), M_robe, group='arm%d' % sx)
            r.ellipsoid(hand[0], hand[1] + R_(3), R_(2.3), R_(2.4), M_skin, group='hand%d' % sx)
    else:
        for (sx, ex_) in ((30, 28), (50, 52)):
            r.tube(P(sx, 34), P(ex_, 60), R_(4.6), R_(5.4), M_robe, lift=-0.05, group='armb%d' % sx)
    if papers and view != 'back':
        px_, py_ = (P(50 + hunch, 52) if view == 'right' else P(53, 50))
        r.poly([(px_, py_), (px_ + R_(7), py_ - R_(1)), (px_ + R_(7.5), py_ + R_(8)), (px_ + R_(0.5), py_ + R_(9))], Mat(PAPER, 'plain', 0.4), group='papers')
    im = r.render()
    if flip:
        from PIL import ImageOps
        im = ImageOps.mirror(im)
    return im

def applicant(rs, X, Z, seed, h=6.0, seated=False, Y0=0.0, **kw):
    """a drawn applicant standing (or sitting) at (X, Y0, Z), sized for its depth"""
    img = applicant_img(seed, F * h * (0.72 if seated else 1.0) / Z, seated=seated, **kw)
    rs.sprite(img, X, Y0, Z, tint=lambda c, z: fogged(c, z))

MOSSTONE = ramp('#1a201a #262e25 #343e31 #43503e #55634c #6a785c #82906e')
CAPR = ramp('#2a120c #461d12 #64291a #823a24 #9c4e31 #b4683f')
GILL = ramp('#2a261e #3e382c #565040 #706852')

def mushroom_img(seed, hpx, cap=None):
    """a giant mushroom drawn with the character renderer: a leaning, swollen stem, a broad cap with pale scales,
    dark gills underneath"""
    k = hpx / 100.0
    capw = 34 + h32(seed, 1) % 18
    Wd, Hd = int((capw * 2 + 10) * k) + 6, int(104 * k) + 6
    r = Rig(Wd, Hd)
    cx = Wd / 2
    P = lambda x, y: (cx + x * k, y * k + 3)
    lean = ((h32(seed, 2) % 9) - 4) * 1.6
    M_stem = Mat(CAP, 'fur', 0.22); M_cap = Mat(cap or (CAPR if h32(seed, 3) % 2 else MOSSTONE), 'skin', 0.24, 0.2)
    r.tube(P(0, 100), P(lean * 0.5, 62), 12 * k, 9 * k, M_stem, group='stem', bulge=lambda t: (1 - t) ** 3 * 6 * k)
    r.tube(P(lean * 0.5, 62), P(lean, 34), 9 * k, 7.5 * k, M_stem, group='stem', bulge=lambda t: math.sin(t * 9 + seed) * 1.2 * k)
    r.ellipsoid(*P(0, 99), 15 * k, 3.5 * k, Mat(MOSSTONE, 'fur', 0.2), group='base')
    r.ellipsoid(*P(lean, 34), capw * 0.82 * k, 7 * k, Mat(GILL, 'fabric', 0.15), lift=-0.25, group='gills',
                vfun=lambda x, y, u, w: -0.3 if int(x / k * 0.8) % 3 == 0 else 0)
    r.ellipsoid(*P(lean, 26), capw * k, 20 * k, M_cap, flat=0.85, group='cap',
                clip=lambda x, y: y < P(0, 34)[1],
                vfun=lambda x, y, u, w: (0.35 if h32(int(x / k / 4), int(y / k / 3), seed) % 7 == 0 and w < 0.3 else 0))
    for i in range(int(capw / 4)):                                                # lichen strands hanging off the rim
        sx = lean - capw * 0.9 + i * 8 + h32(seed, 70 + i) % 4
        if h32(seed, 80 + i) % 3: continue
        ln = 6 + h32(seed, 90 + i) % 14
        r.stroke([P(sx, 33 + j) for j in range(ln)], max(1.0, 1.6 * k), Mat(MOSSTONE, 'fur', 0.2), v=0.35, group='lichen')
    return r.render()

def mushroom(rs, X, Z, seed, h=14.0, **kw):
    rs.sprite(mushroom_img(seed, F * h / Z, **kw), X, 0.0, Z, tint=lambda c, z: fogged(c, z))

def statue(rs, X, Z, seed, h=8.0, plinth=2.4, kind=None):
    """an approved mutant on a plinth: a mossy stone applicant, larger than life"""
    rs.box(X - 1.9, X + 1.9, 0, plinth, Z - 1.4, Z + 1.4, concrete(3.2, MOSSTONE), concrete(2.4, MOSSTONE), top=concrete(4.0, MOSSTONE), cls='prop')
    rs.box(X - 2.2, X + 2.2, plinth, plinth + 0.35, Z - 1.6, Z + 1.6, concrete(3.8, STONE), concrete(2.8, STONE), top=concrete(4.4, STONE), cls='prop')
    img = applicant_img(seed, F * h / Z, kind=kind, view='front', robe=MOSSTONE, skin=MOSSTONE, stone=True)
    rs.sprite(img, X, plinth + 0.35, Z - 0.2, tint=lambda c, z: fogged(c, z))
