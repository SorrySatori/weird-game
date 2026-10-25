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

def applicant_img(seed, hpx, kind=None, view=None, seated=False, robe=None, skin=None, stone=False,
                  bob=0.0, lean=0.0, nod=0.0, face=None, hands=None, papers=None, page=(0.0, 0.0, 0.0), stamp=False):
    """an applicant drawn with the character renderer (rig.py) at its on-screen height: a hooded robe, sometimes a
    mushroom cap or coral knobs growing out of the hood, or a gas mask; view 'front' | 'back' | 'right' | 'left'.
    Pose knobs for idle frames (rig units, 100 = the figure's height; all 0 = the still figure): bob (shoulders and
    head sink, a breath), lean (shoulders and head shift sideways), nod (the head alone drops), face='front' (a profile
    figure glances at the viewer), hands ((x, y), (x, y)) for a front figure, papers (force on/off) with page (dx, dy,
    lift of the page's free edge), stamp (a rubber stamp in the right hand)"""
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
    if papers is None: papers = h32(seed, 18) % 3 == 0 and not seated
    hx, hy = 40 + hunch * fwd * 0.8 + lean, 19 + hunch * 0.5 + (8 if seated else 0) + bob + nod
    sh_x, sh_y = lean, bob                                                                          # the shoulders follow
    if not seated:
        for fx in ((34, 46) if view != 'right' else (36, 47)):
            r.ellipsoid(*P(fx, 98.5), R_(4.6), R_(2.2), M_boot, lift=-0.1, group='feet')
        body = [(29 + sh_x, 30 + sh_y), (51 + sh_x, 30 + sh_y), (53, 62), (56, 97), (24, 97), (27, 62)]
    else:
        body = [(29 + hunch + sh_x, 36 + sh_y), (51 + hunch + sh_x, 36 + sh_y), (53, 60), (55, 104), (25, 104), (27, 60)]
    if view == 'right': body = [(x - 2 if i in (0, 5, 4) else x, y) for i, (x, y) in enumerate(body)]
    # the far arm (behind the body in profile)
    if view == 'right':
        r.tube(P(36 + sh_x, 34 + hunch * 0.4 + sh_y), P(44 + hunch, 58 if not seated else 52), R_(4.4), R_(5.2), M_robe, lift=-0.25, group='armF')
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
    if (face or view) == 'front':
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
        r.tube(P(42 + sh_x, 34 + hunch * 0.4 + sh_y), hand, R_(4.8), R_(5.6), M_robe, group='armN')
        r.ellipsoid(hand[0] + R_(1.5), hand[1] + R_(2.5), R_(2.4), R_(2.4), M_skin, group='hand')
    elif view == 'front':
        for i, (sx, ex_) in enumerate(((30, 27), (50, 52))):
            hand = P(*hands[i]) if hands else P(ex_ + (6 if (papers and sx > 40) else 0) - (4 if seated else 0), 60 if not seated else 56)
            r.tube(P(sx + sh_x, 34 + hunch * 0.3 + sh_y), hand, R_(4.6), R_(5.6), M_robe, group='arm%d' % sx)
            if stamp and sx > 40:                                                                   # the rubber stamp: knob, handle, pad
                WOODS = Mat(WOOD, 'plain', 0.2)
                r.tube((hand[0], hand[1] + R_(1)), (hand[0], hand[1] + R_(7)), R_(1.2), R_(1.2), WOODS, group='stamp')
                r.poly([(hand[0] - R_(3.2), hand[1] + R_(6.6)), (hand[0] + R_(3.2), hand[1] + R_(6.6)),
                        (hand[0] + R_(3.2), hand[1] + R_(8.6)), (hand[0] - R_(3.2), hand[1] + R_(8.6))], WOODS, group='stamp')
                r.poly([(hand[0] - R_(3.0), hand[1] + R_(8.6)), (hand[0] + R_(3.0), hand[1] + R_(8.6)),
                        (hand[0] + R_(3.0), hand[1] + R_(9.6)), (hand[0] - R_(3.0), hand[1] + R_(9.6))], Mat(RED, 'plain', 0.3), group='pad')
            r.ellipsoid(hand[0], hand[1] + R_(3), R_(2.3), R_(2.4), M_skin, group='hand%d' % sx)
    else:
        for (sx, ex_) in ((30, 28), (50, 52)):
            r.tube(P(sx + sh_x, 34 + sh_y), P(ex_, 60), R_(4.6), R_(5.4), M_robe, lift=-0.05, group='armb%d' % sx)
    if papers and view != 'back':
        pdx, pdy, lift_ = page
        px_, py_ = (P(50 + hunch + pdx, 52 + pdy) if view == 'right' else P(53 + pdx, 50 + pdy))
        r.poly([(px_, py_), (px_ + R_(7), py_ - R_(1) - R_(lift_)), (px_ + R_(7.5), py_ + R_(8) - R_(lift_)), (px_ + R_(0.5), py_ + R_(9))], Mat(PAPER, 'plain', 0.4), group='papers')
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

# ---------------------------------------------------------------------------------------------------- bizarre statues
STONEM = ramp('#121612 #1c221c #283027 #353f33 #454f41 #576250 #6c7762 #848e77 #9ea78f')
def mutant_img(seed, hpx, kind):
    """an approved mutation carved in stone: a robed figure on its plinth with the mutation growing out of it --
    'arms' (three pairs of arms out of the robe), 'heads' (a forked neck, three heads), 'tentacles' (the hem splits
    into tentacles over the plinth), 'antlers' (antlers through the hood, arms down to the knees), 'shell' (hunched under
    a spiral shell, one huge claw), 'eyes' (a cluster of eyes in the hood), 'stilts' (stretched, stick-thin, on stilt legs)"""
    k = hpx / 100.0
    Wd, Hd = int(150 * k) + 8, int(120 * k) + 8
    r = Rig(Wd, Hd)
    P = lambda x, y: ((x + 75) * k + 4, (y + 20) * k + 4)                  # x: -75..75 around the axis, y: -20..100
    R_ = lambda v: v * k
    def mossy(x, y, u, w):                                                   # moss settles on what faces up
        return -0.35 if w < -0.45 and h32(int(x / max(1, k * 2)), int(y / max(1, k * 2)), seed) % 3 else 0
    st = Mat(STONEM, 'plain', 0.2)
    MO = Mat(MOSSTONE, 'fur', 0.2)
    def limb(pts, r0, r1, g, lift=0.0):
        n = len(pts) - 1
        for i in range(n):
            r.tube(P(*pts[i]), P(*pts[i + 1]), R_(r0 + (r1 - r0) * i / n), R_(r0 + (r1 - r0) * (i + 1) / n), st, lift=lift, group=g,
                   folds=lambda t, sd: -0.25 if sd > 0.6 else 0)
    def hand(x, y, g, s_=2.8):
        r.ellipsoid(*P(x, y), R_(s_), R_(s_ * 1.1), st, group=g)
    def robe(top_y, w0, w1, bottom=98, lean=0.0, g='robe'):
        pts = [P(-w0 + lean, top_y), P(w0 + lean, top_y), P(w0 + 2, top_y + 18), P(w1, bottom), P(-w1, bottom), P(-w0 - 2, top_y + 18)]
        r.poly(pts, st, group=g, vfun=lambda x, y: -0.3 if int((x / k) * 0.5 + (y / k) * 0.08) % 3 == 0 and y / k > top_y + 30 else 0)
    def hood(hx, hy, rx=9.0, ry=10.5, opening=True, drape=True):
        if drape: r.poly([P(hx - 12, hy + 7), P(hx + 12, hy + 7), P(hx + 14, hy + 16), P(hx - 14, hy + 16)], st, lift=0.05, group='drape')
        r.ellipsoid(*P(hx, hy), R_(rx), R_(ry), st, lift=0.06, group='hood', vfun=mossy)
        if opening: r.ellipsoid(*P(hx + 0.5, hy + 2), R_(rx * 0.62), R_(ry * 0.7), st, lift=-0.7, group='opening')
    stilts = kind == 'stilts'
    if kind == 'tentacles':
        for i in range(8):                                                   # the hem splits into tentacles
            a = -1.35 + i * 0.385
            pts = [(math.sin(a) * 10, 70)]
            for j in range(1, 8):
                t = j / 7
                pts.append((math.sin(a) * (10 + 34 * t) + math.sin(t * 6 + i) * 3.5, 70 + 30 * t - 6 * t * t * (abs(a) < 0.6)))
            limb(pts, 5.6, 1.2, 't%d' % i, lift=-0.12 if abs(a) > 0.9 else 0.0)
        robe(30, 12, 15, bottom=76)
    elif kind == 'shell':
        robe(44, 12, 18, lean=6)
    elif stilts:
        for sx in (-1, 1):
            limb([(sx * 4, 62), (sx * 6, 80), (sx * 7, 99)], 2.0, 1.6, 'leg%d' % sx)
        robe(4, 6, 8, bottom=64)
    else:
        robe(30, 12, 17)
    # the head end of each mutation
    if kind == 'heads':
        for (hx, hy, rr) in ((-15, 4, 6.4), (0, -6, 7.4), (15, 5, 6.2)):
            limb([(0, 30), (hx * 0.5, (30 + hy) / 2 + 4), (hx, hy + 6)], 4.8, 3.8, 'neck%d' % hx)
            hood(hx, hy, rr * 1.25, rr * 1.4, drape=False)
    elif kind == 'eyes':
        hood(0, 18, 11, 12.5, opening=True)
        for i in range(9):
            a = i * 2.39996; d = 1 + (i ** 0.5) * 2.4
            ex, ey = math.cos(a) * d, 20 + math.sin(a) * d
            rr = 2.2 - i * 0.1
            r.ellipsoid(*P(ex, ey), R_(rr), R_(rr), Mat(STONEM, 'plain', 0.34, 0.7), group='eye%d' % i)
            r.fixed(*P(ex + 0.3, ey + 0.3), STONEM[0])
    elif kind == 'shell':
        r.ellipsoid(*P(-12, 46), R_(23), R_(25), Mat(STONEM, 'plain', 0.22, 0.25), group='shell',
                    vfun=lambda x, y, u, w: (-0.4 if abs(math.hypot(u, w) * 6 - math.atan2(w, u) * 0.95) % 1.6 < 0.25 else 0) + mossy(x, y, u, w))
        hood(14, 30, 8, 9)
        limb([(10, 50), (26, 44), (36, 30)], 5.0, 4.4, 'clawarm')
        r.ellipsoid(*P(42, 22), R_(11), R_(7), st, rot=-0.5, group='claw', vfun=mossy)
        r.ellipsoid(*P(47, 33), R_(9), R_(3.8), st, rot=0.45, group='pincer')
    elif stilts:
        hood(0, -8, 4.6, 5.4, drape=False)
    else:
        hood(0, 18)
        if kind == 'antlers':
            def antler(x, y, a, ln, d):
                if d > 3 or ln < 3: return
                x2, y2 = x + math.cos(a) * ln, y - math.sin(a) * ln
                r.tube(P(x, y), P(x2, y2), R_(2.4 - d * 0.5), R_(2.0 - d * 0.45), st, group='antler')
                antler(x2, y2, a + 0.5, ln * 0.7, d + 1); antler(x2, y2, a - 0.45, ln * 0.62, d + 1)
            antler(-4, 10, math.radians(118), 16, 0); antler(4, 10, math.radians(62), 16, 0)
    # arms out of the robe
    if kind == 'arms':
        for (yy, a_up) in ((34, 1.0), (44, 0.15), (54, -0.7)):
            for sx in (-1, 1):
                el = (sx * (22 + 4 * a_up), yy - 6 * a_up + 6)
                hd = (sx * (33 + 8 * (1 - abs(a_up))), yy - 24 * a_up + 4)
                limb([(sx * 11, yy), el, hd], 4.0, 3.0, 'arm%d%d' % (sx, yy))
                hand(hd[0], hd[1], 'h%d%d' % (sx, yy))
    elif kind == 'antlers':
        for sx in (-1, 1):
            limb([(sx * 12, 34), (sx * 17, 58), (sx * 18, 84)], 4.0, 2.8, 'arm%d' % sx)
            hand(sx * 18.5, 87, 'h%d' % sx)
    elif stilts:
        for sx in (-1, 1):
            limb([(sx * 5, 8), (sx * 13, 34), (sx * 11, 62)], 2.0, 1.5, 'arm%d' % sx)
            hand(sx * 11, 64, 'h%d' % sx, 1.8)
    elif kind in ('heads', 'eyes', 'tentacles'):
        for sx in (-1, 1):
            limb([(sx * 12, 34), (sx * 16, 50), (sx * 9, 60)], 4.2, 3.2, 'arm%d' % sx)
            hand(sx * 8, 61, 'h%d' % sx)
    return r.render()

def bizarre_statue(rs, X, Z, seed, kind, h=10.0, plinth=2.8):
    rs.box(X - 2.4, X + 2.4, 0, plinth, Z - 1.6, Z + 1.6, concrete(3.2, MOSSTONE), concrete(2.4, MOSSTONE), top=concrete(4.0, MOSSTONE), cls='prop')
    rs.box(X - 2.7, X + 2.7, plinth, plinth + 0.35, Z - 1.8, Z + 1.8, concrete(3.8, STONE), concrete(2.8, STONE), top=concrete(4.4, STONE), cls='prop')
    img = mutant_img(seed, F * h / Z, kind)
    rs.sprite(img, X, plinth + 0.35, Z - 0.2, tint=lambda c, z: fogged(c, z))

# ---------------------------------------------------------------------------------------------------- tenement facades
SHUT = [ramp('#122016 #1a2e20 #24402c #305439'), ramp('#24170e #352215 #4a301e #603f28'), ramp('#1a1e26 #252b36 #323a48 #414b5c')]
CURT = [(118, 62, 52), (150, 128, 82), (90, 104, 120), (122, 92, 120), (168, 160, 140)]
def facade(base, along_z=False, bay=5.0, floors=3.6, y0=0.0, seed=0, wf=0.38, pipe_every=3):
    """a tenement wall: rows of windows -- dark glass with the sky in it, lit, shuttered, boarded, broken, curtained --
    with sills, lintels, grime runs under them, and drainpipes every few bays"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = Z if along_z else X
        if Y < y0: return base(x, y, s, t, z, wp)
        fu = (u / bay) % 1; fv = ((Y - y0) / floors) % 1
        bi, fi = math.floor(u / bay), math.floor((Y - y0) / floors)
        px = z / F                                                                  # metres per pixel
        if bi % pipe_every == 0 and abs(fu - 0.06) < max(0.025, px / bay * 0.7):      # a drainpipe
            return fogged(tone(METAL, 1.6 + (1.2 if (Y % 2.6) < 0.25 else 0) + (0.6 if fu < 0.06 else 0), x, y), z)
        lo, hi = 0.5 - wf / 2, 0.5 + wf / 2
        k = h32(bi, fi, seed)
        inw = lo < fu < hi and 0.24 < fv < 0.8
        if lo - 0.03 < fu < hi + 0.03 and 0.18 < fv < 0.24: return fogged(tone(STUCCO, 4.4 - (fv - 0.18) * 20, x, y), z)   # the sill
        if lo - 0.01 < fu < hi + 0.01 and 0.8 < fv < 0.85: return fogged(tone(STUCCO, 2.0, x, y), z)                      # the lintel
        if not inw:
            c = base(x, y, s, t, z, wp)
            if lo < fu < hi and fv < 0.18 and wn(2, u * 3 + bi, 1.0) > 0.45:                                             # grime run under the sill
                c = mix(c, (20, 24, 20), (0.18 - fv) / 0.18 * 0.35)
            return c
        wu, wv = (fu - lo) / wf, (fv - 0.24) / 0.56
        state = k % 100
        if state < 4: c = GLOW[1] if (x + y) % 3 else GLOW[2]                                                           # lit
        elif state < 16:                                                                                                  # shutters
            r_ = SHUT[k % 3]
            c = tone(r_, 2.4 - (1.2 if (wv * 9) % 1 < 0.25 else 0) - (1.0 if abs(wu - 0.5) < 0.03 else 0), x, y)
            if k % 7 == 0 and wu > 0.5: c = STONE[0]                                                                     # one leaf open
        elif state < 22:                                                                                                  # boarded up
            c = tone(WOOD, 3.0 - (1.4 if (wv * 4) % 1 < 0.12 else 0), x, y)
            if abs(wu - wv) < 0.08 or abs(1 - wu - wv) < 0.08: c = tone(WOOD, 4.2, x, y)
        elif state < 27:                                                                                                  # broken
            jag = abs(math.sin(wu * 23 + k) * 0.3 + 0.35 - wv)
            c = STONE[0] if jag > 0.12 else tone(SKY, 4.4, x, y)
        else:                                                                                                             # glass
            c = tone(SKY, 2.2 + wv * 2.6 + (0.8 if (wu + wv * 0.4) % 0.7 < 0.08 else 0), x, y)
            if abs(wu - 0.5) < max(0.04, px / (bay * wf) * 0.6) or abs(wv - 0.36) < max(0.04, px / (floors * 0.56) * 0.6): c = tone(STUCCO, 2.0, x, y)
            if state < 45 and wv > 0.5 - (k % 3) * 0.1:                                                                  # a curtain
                c = mix(CURT[k % len(CURT)], (0, 0, 0), 0.25 + 0.2 * ((wu * 7) % 1 < 0.3))
        return fogged(c, z, 0.85)
    return sh

def balconies(rs, wall, z0, z1, along_z, bay, floors, y0, seed, top, side=1, every=4):
    """little iron balconies stuck to a facade: a concrete slab, a railing, sometimes laundry or a plant pot"""
    u = z0 + bay * 0.5
    while u < z1:
        bi = math.floor(u / bay)
        for fi in range(1, int((top - y0) / floors)):
            if h32(bi, fi, seed + 77) % every: continue
            Y = y0 + fi * floors + 0.2 * floors
            w0, w1 = u - bay * 0.32, u + bay * 0.32
            d = 1.3 * side
            slab = lambda x, y, s, t, z, wp: fogged(tone(STONE, 3.6 if t > 0.5 else 2.2, x, y), z)
            if along_z:
                xa, xb = sorted((wall, wall + d))
                rs.box(xa, xb, Y - 0.3, Y, w0, w1, slab, slab, top=slab, bottom=slab, cls='prop')
                for zz in (w0, w1): rs.line3((wall + d, Y, zz), (wall + d, Y + 1.6, zz), lambda x, y, s, t, z, wp: fogged(METAL[1], z), w=0.12)
                rs.line3((wall + d, Y + 1.6, w0), (wall + d, Y + 1.6, w1), lambda x, y, s, t, z, wp: fogged(METAL[1], z), w=0.12)
                rs.quad((wall + d, Y, w0), (wall + d, Y, w1), (wall + d, Y + 1.5, w0),
                        lambda x, y, s, t, z, wp: fogged(METAL[1], z) if (s * 14) % 1 < 0.25 or t < 0.08 else None, cls='prop', cut=True)
                if h32(bi, fi, seed) % 3 == 0:                                                  # laundry over the railing
                    c = CURT[h32(bi, fi, 5) % len(CURT)]
                    rs.quad((wall + d - 0.05, Y + 0.4, w0 + 0.4), (wall + d - 0.05, Y + 0.4, w0 + 1.6), (wall + d - 0.05, Y + 1.7, w0 + 0.4),
                            lambda x, y, s, t, z, wp, c=c: fogged(mix(c, (0, 0, 0), 0.15 * (int(s * 5) % 2)), z), cls='prop')
            else:
                rs.box(w0, w1, Y - 0.3, Y, wall - d, wall, slab, slab, top=slab, bottom=slab, cls='prop')
                rs.quad((w0, Y, wall - d), (w1, Y, wall - d), (w0, Y + 1.5, wall - d),
                        lambda x, y, s, t, z, wp: fogged(METAL[1], z) if (s * 14) % 1 < 0.25 or t > 0.92 else None, cls='prop', cut=True)
        u += bay
