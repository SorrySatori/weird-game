"""The Bishop's study inside the Egg Cathedral (EggCathedralStudyScene), 1067x600, the shared camera (raster3d.py).
The first room inside the shell: the Bishop's stone study, and the egg has grown around it and into it.

  the shell   the room is egg-shaped in plan (wide where you stand, narrowing to an apse at the back) and its walls
              curve over into an eggshell vault: below the cornice the study's own grey ashlar, above it the cream,
              pored, faintly translucent shell; stone ribs run up the walls and over the vault towards a crown above
              your head (cathedral_bg.py's stone, the entrance's eggshell)
  the apse    the desk grows straight out of the living wall: its back and its hutch of pigeonholes are fused into a
              mass of muted flesh that spreads its veins over the stone and the shell; tendrils pour over the hutch
              and root the desk's feet into the floor
  the desk    the Bishop's journal under a clear membrane, scrolls sheathed in membrane, an inkwell and a quill,
              candles burning low on tendril cups -- the cathedral keeps them lit; two more candles are held out on
              tendrils hanging from the vault
  the walls   pigeonhole cabinets of membrane-wrapped scrolls between the ribs, a chest with a candle cluster, a
              lectern; her high-backed chair pushed back
  the exits   a pointed doorway in the left wall, a short passage out to the grey daylight of the threshold (the way
              back); in the right wall, past the apse, a stair climbing away into the warm light of the heart (deeper in)
  the floor   worn flagstones, a faded rug, wax on the stones, roots from the desk

    python3 cathedral_study_bg.py <outdir>   ->  study.png  (= assets/images/backgrounds/EggCathedralStudy.png)
Prints the canvas outlines of the two exits and the journal's position (the scene's hotspots)."""
import sys, math
from cathedral_inkit import *
import cathedral_inkit as K

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
K.FOG.update(col=(14, 11, 9), z0=18.0, span=60.0, max=0.28)
rs = Raster()

# ---------------------------------------------------------------------------------------------------- the egg
WX, YS, BV, ZC, CL = 27.5, 9.0, 13.0, 10.0, 15.5        # plan half-axes WX (across) / CL (along), the cornice, the vault
DEG = math.pi / 180

def phi_of(X, Z, d=0.0):
    p = math.atan2((Z - ZC) / (CL - d), X / (WX - d))
    return p + 2 * math.pi if p < -math.pi / 2 else p
def rloc(p, d=0.0): return math.hypot((WX - d) * math.sin(p), (CL - d) * math.cos(p))
_ST = [0.0]
for i in range(1, 2001):                                 # arc length along the plan ellipse, from phi = -pi/2
    p = -math.pi / 2 + 2 * math.pi * i / 2000
    _ST.append(_ST[-1] + rloc(p) * 2 * math.pi / 2000)
def S(p):
    f = (p + math.pi / 2) / (2 * math.pi) * 2000
    i = max(0, min(1999, int(f))); return _ST[i] + (_ST[i + 1] - _ST[i]) * (f - i)

def shell_hit(dx, dy, d=0.0):
    """the composite shell from inside: an elliptic cylinder up to the cornice, half an ellipsoid above it"""
    A, B, C = WX - d, BV - d, CL - d
    a = dx * dx / (A * A) + dy * dy / (B * B) + 1 / (C * C)
    b = 2 * ((CAMH - YS) * dy / (B * B) - ZC / (C * C))
    c = (CAMH - YS) ** 2 / (B * B) + ZC * ZC / (C * C) - 1
    t = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
    Y = CAMH + dy * t
    if Y >= YS:
        X, Z = dx * t, t
        n = (-X / (A * A), -(Y - YS) / (B * B), -(Z - ZC) / (C * C))
        return t, 'vault', n
    a = dx * dx / (A * A) + 1 / (C * C); b = -2 * ZC / (C * C); c = ZC * ZC / (C * C) - 1
    t = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
    X, Z = dx * t, t
    return t, 'wall', (-X / (A * A), 0.0, -(Z - ZC) / (C * C))
def nrm(n):
    l = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1.0
    return (n[0] / l, n[1] / l, n[2] / l)

# ---------------------------------------------------------------------------------------------------- the openings
class Opening:
    def __init__(s, phic, hw, ys, R, L):
        s.phic, s.hw, s.ys, s.R, s.L = phic, hw, ys, R, L
        s.O = (WX * math.cos(phic), 0.0, ZC + CL * math.sin(phic))
        n = nrm((math.cos(phic) / WX, 0.0, math.sin(phic) / CL))
        s.eo = (n[0], n[2]); s.et = (n[2], -n[0])
        s.ang = wall_frame(n[0], n[2])
    def arch(s, u):
        return s.ys + math.sqrt(max(0.0, s.R * s.R - (abs(u) + s.R - s.hw) ** 2))
    def local(s, X, Z):
        dx, dz = X - s.O[0], Z - s.O[2]
        return dx * s.et[0] + dz * s.et[1], dx * s.eo[0] + dz * s.eo[1]
    def P(s, u, Y, e):
        return (s.O[0] + s.et[0] * u + s.eo[0] * e, Y, s.O[2] + s.et[1] * u + s.eo[1] * e)
    def inside(s, X, Y, Z, pad=0.0):
        u, e = s.local(X, Z)
        return e > -3.0 and abs(u) < s.hw + pad and Y < s.arch(u) + pad and Y > -0.5
    def ring(s, X, Y, Z):
        """distance outside the opening's edge (for the dressed surround), or None far from it"""
        u, e = s.local(X, Z)
        if e < -3.0 or abs(u) > s.hw + 1.2: return None
        if Y <= s.ys: return abs(u) - s.hw, Y, True
        R2 = math.hypot(abs(u) + s.R - s.hw, Y - s.ys)
        return R2 - s.R, math.atan2(Y - s.ys, abs(u) + s.R - s.hw), False
    def outline(s, n=14):
        pts = [proj(*s.P(-s.hw, 0.0, 0.0))]
        for i in range(n + 1):
            u = -s.hw + 2 * s.hw * i / n
            pts.append(proj(*s.P(u, s.arch(u), 0.0)))
        pts.append(proj(*s.P(s.hw, 0.0, 0.0)))
        return [(round(x), round(y)) for x, y in pts]

DOOR = Opening(153.5 * DEG, 2.0, 5.6, 2.6, 6.5)          # back out to the threshold
STAIR = Opening(45.0 * DEG, 2.5, 6.1, 3.1, 11.0)        # up to the heart
OPEN = (DOOR, STAIR)
def in_opening(X, Y, Z, pad=0.0): return any(o.inside(X, Y, Z, pad) for o in OPEN)

RIBS = [14, 32, 58, 74, 106, 124, 142, 166]
SCONCE_SPEC = ((74, 6.4, 1.0, 0.8), (106, 6.4, 1.0, 0.6), (58, 5.6, 0.85, 0.5), (124, 5.8, 0.9, 0.9), (142, 5.4, 0.85, 0.55), (32, 5.4, 0.9, 0.75))
SCONCES = [(p_, y_) for (p_, y_, i_, h_) in SCONCE_SPEC]
RIBR = [r * DEG for r in RIBS]
APSE = (0.0, 4.0, ZC + CL)

# ---------------------------------------------------------------------------------------------------- shell shaders
S90 = S(math.pi / 2)
def surf_uv(X, Y, Z, p=None):
    """the shell's own coordinates: u = arc length sideways from the apse's middle line, v = arc length up from the
    floor (both world units)"""
    p = phi_of(X, Z) if p is None else p
    if Y <= YS: return S(p) - S90, Y
    q = min(1.0, (Y - YS) / BV)
    return (S(p) - S90) * math.sqrt(max(0.0, 1 - q * q)), YS + BV * math.asin(q)

def ambient(wp, n):
    """the soft fill: daylight through the eggshell vault, strongest on what faces up, weak low on the walls"""
    up = n[1] if n else 0.3
    return 0.15 + 0.55 * max(0.0, up) - 0.4 * max(0.0, -up) + 0.3 * min(1.0, wp[1] / 10.0)
K.AMB['fn'] = ambient

def tissue_amount(u, v):
    """how much of the wall the living flesh has taken: a mass around the apse behind the desk, ragged at its edge,
    thinning out upwards"""
    Wd = 7.4 + 1.6 * (wn(5, v * 0.3, 3.0) - 0.5) + 1.2 * (wn(4, v * 0.9, 7.0) - 0.5) - max(0.0, v - 12.0) * 0.5
    top = 16.8 - (u / 6.8) ** 2 * 4.0 + 2.0 * (wn(5, u * 0.35, 11.0) - 0.5)
    lobes = (wn(4, u * 0.35 + 50, v * 0.35) - 0.5) * 0.7 + (wn(1, u * 1.1, v * 0.9) - 0.5) * 0.3
    return min(1.0 - abs(u) / max(0.5, Wd), (top - v) / 2.6) + lobes

# the veins of the egg, seen against its translucent shell like a candled egg's: they spread from the flesh at the apse
VM = VeinMap(-40.0, 40.0, -1.0, 32.0)
for k, (u, v, ang, r, L) in enumerate(((-4.4, 14.6, -0.7, 0.3, 19), (-1.4, 16.4, -0.15, 0.34, 21), (1.9, 16.2, 0.25, 0.32, 20),
                                      (4.6, 14.4, 0.72, 0.3, 19), (-7.0, 10.6, -1.15, 0.22, 14), (7.1, 10.8, 1.2, 0.22, 14),
                                      (-7.6, 5.4, -1.5, 0.15, 8), (7.5, 5.0, 1.5, 0.15, 8))):
    VM.grow(u, v, ang, r, 101 + k * 7, length=L, fork=(1.8, 3.8), bend=0.14, stop=lambda u_, v_: v_ > 27.5 - abs(u_) * 0.1)

def flesh(X, Y, Z, n, x, y, u, v, g):
    """the apse's living tissue: fibres running up, folds, wet ridges, darker crevices; at its ragged edge a thin
    membrane over the stone"""
    warp = (wn(5, u * 0.3, v * 0.3) - 0.5) * 2.0
    f = wn(1, u * 4.2 + warp, v * 0.3)                                                             # fine fibres, running up
    fold = wn(5, u * 0.55 + 0.3 * math.sin(v), v * 0.42)                                           # big soft folds
    val = 2.0 + (f - 0.5) * 1.4 + (fold - 0.5) * 2.6 + min(1.0, g * 3) * 0.4
    if abs(fold - 0.62) < 0.018: val += 3.4                                                        # a wet fold catches the light
    elif abs(fold - 0.62) < 0.04: val += 1.5
    if f > 0.72 and fold > 0.5 and h32(x, y, 5) % 2 == 0: val += 1.8                               # glistening along the fibres
    if f < 0.28: val -= 0.9                                                                        # crevices between the fibres
    vn = VM.sample(u, v)
    if vn and vn[1]: return shade(VEIN, 1.2, (X, Y, Z), n, x, y, gain=2.4, warm=0.3)
    return shade(TISSUE, val, (X, Y, Z), n, x, y, gain=3.0, warm=0.35)

def shell_glow(u, v, x, y):
    """the vault is a lantern: daylight comes through the eggshell, brightest overhead where it is thinnest, and in
    thin patches; returns a ramp value (before any candle-light)"""
    q = max(0.0, min(1.0, (v - YS) / 13.0))
    val = 2.4 + 3.4 * q ** 1.2 + (wn(0, u * 0.14, v * 0.14) - 0.5) * 1.4 + (wn(1, u * 0.7, v * 0.7) - 0.5) * 0.45
    val += (wn(3, u * 0.35 + 7, v * 0.35) - 0.5) * 0.6                                             # the shell's own mottling
    th = wn(4, u * 0.08 + 30, v * 0.08)
    if th > 0.55: val += (th - 0.55) * 7.0                                                         # thin, translucent patches
    elif th < 0.36: val -= (0.36 - th) * 4.0                                                       # thick, dark ones
    val += 2.0 * math.exp(-((v - 29.4) / 4.0) ** 2)                                                 # the crown, thinnest of all
    return val
def red_through(c, k):
    """light through thin flesh: the blue and green are drunk, the red comes through"""
    return mix(c, (c[0] * 0.96, c[1] * 0.5, c[2] * 0.4), k)

def eggshell(X, Y, Z, n, x, y, u, v):
    """the inside of the egg's shell: lit through from outside (the vault is a lantern), cream, mottled, pored;
    candle-light warms it from inside; the veins show against it like a candled egg's, red where they are thin"""
    val = shell_glow(u, v, x, y)
    val += ((h32(x, y, 78) % 5) - 2) * 0.12                                                        # pores
    if h32(x, y, 77) % 67 == 0: val -= 1.0                                                         # freckles
    if wn(3, u * 0.2 + 9, v * 0.2) > 0.64 and abs(wn(2, u * 0.9 + 40, v * 0.45) - 0.5) < 0.011: val -= 2.0   # hairline cracks
    L = lit(X, Y, Z, n); I = 0.3 * L[0] + 0.59 * L[1] + 0.11 * L[2]
    val -= 3.0 * soot(X, Y, Z)
    c = tone(SHELL, val + (2.6 * I / (0.45 + I) if I > 0.01 else 0), x, y)
    if I > 0.01:                                                                                   # candle-light on the shell
        k = min(1.0, I * 1.6) * 0.5
        c = clamp((c[0] * (1 + (L[0] / I - 1) * k), c[1] * (1 + (L[1] / I - 1) * k), c[2] * (1 + (L[2] / I - 1) * k)))
    vn = VM.sample(u, v)
    if vn:
        cov, core = vn
        fade = max(0.2, min(1.0, (28.5 - v) / 5.0))
        if core: c = mix(c, tone(VEIN, 1.0 + (wn(1, u * 3, v * 3) - 0.5), x, y), fade)
        else: c = mix(c, mix(red_through(c, 0.45 + 0.35 * cov), tone(VEIN, 1.8, x, y), max(0.0, cov - 0.4) * 1.1), fade)
    elif wn(2, u * 1.6 + 70, v * 1.6) > 0.8 and h32(int(u * 9 + 999), int(v * 9 + 999), 4) % 4 == 0:
        c = mix(c, tone(SHELL, val - 1.6, x, y), 0.6)                                              # speckles in the shell
    return fogged(c, Z)

def shell_sh(x, y, a, b, z, wp):
    X, Y, Z = wp
    vault = b > 0.5
    n = nrm(shell_hit_normal(X, Y, Z, vault))
    u, v = surf_uv(X, Y, Z, a)
    g = tissue_amount(u, v)
    if g > 0:
        c = flesh(X, Y, Z, n, x, y, u, v, g)
        if vault or Y >= YS - 0.8:
            if g < 0.3:                                                                            # thin at its edge: the light comes through, red
                base = red_through(eggshell(X, Y, Z, n, x, y, u, v), 0.95)
                c = mix(base, c, (g / 0.3) ** 1.3)
            elif wn(1, u * 2.4 + 0.9 * math.sin(v * 0.6), v * 0.26) > 0.7 and g < 0.5:              # and between the fibres
                c = mix(c, red_through(tone(SHELL, shell_glow(u, v, x, y) - 1.0, x, y), 1.0), 0.45)
        elif g < 0.16:
            c = mix(stone(X, Y, Z, n, x, y, a, u, v, -0.3), c, 0.35 + 0.65 * g / 0.16)
        return c
    for o in OPEN:                                                                                 # dressed surrounds
        r_ = o.ring(X, Y, Z)
        if r_ and 0 <= r_[0] < 0.9:
            d, along, jamb = r_
            if jamb: blk = math.floor(along / 0.8); f = (along / 0.8) % 1
            else: blk = math.floor(along / 0.21) + 50; f = (along / 0.21) % 1
            val = 2.8 + (h32(blk, 3) % 3) * 0.25 - d * 0.9 + (wn(1, X * 3 + Z * 3, Y * 3) - 0.5) * 0.4
            if f < 0.06 * (2 if jamb else 3) or abs(d - 0.86) < 0.05: val -= 1.6
            return shade(GREY, val, wp, n, x, y)
    if not vault and Y < YS - 0.8: return stone(X, Y, Z, n, x, y, a, u, v, g)                    # the study's ashlar
    return eggshell(X, Y, Z, n, x, y, u, v)

def stone(X, Y, Z, n, x, y, p, u, v, g):
    rr, val = masonry(GREY, S(p), Y, Z, x, y, 1.9, ch=0.62, L=1.0, seed=7, pale=SAND)
    val -= 0.7 * math.exp(-Y / 1.2)
    if g > -0.3: val -= (g + 0.3) * 2.0                                                            # stained where the flesh creeps
    val -= 2.6 * soot(X, Y, Z)
    vn = VM.sample(u, v)
    if vn:
        cov, core = vn
        return shade(VEIN, (1.0 if core else 1.8) + (1 - cov), (X, Y, Z), n, x, y, gain=2.4, warm=0.3)
    return shade(rr, val, (X, Y, Z), n, x, y)

def shell_hit_normal(X, Y, Z, vault, d=0.0):
    A, B, C = WX - d, BV - d, CL - d
    if vault: return (-X / (A * A), -(Y - YS) / (B * B), -(Z - ZC) / (C * C))
    return (-X / (A * A), 0.0, -(Z - ZC) / (C * C))

def shell_cast(dx, dy):
    t, kind, n = shell_hit(dx, dy)
    X, Y, Z = dx * t, CAMH + dy * t, t
    if Y < -0.2: return None
    if in_opening(X, Y, Z): return None
    return t, phi_of(X, Z), (1.0 if kind == 'vault' else 0.0), nrm(n)
raycast(rs, shell_cast, shell_sh, cls='wall')

# the cornice: a moulded string course where the stone ends and the shell begins
def cornice_cast(dx, dy):
    t, kind, n = shell_hit(dx, dy, 0.5)
    X, Y, Z = dx * t, CAMH + dy * t, t
    if not (YS - 0.75 < Y < YS + 0.3): return None
    if in_opening(X, Y, Z, 0.9): return None
    p = phi_of(X, Z, 0.5)
    if tissue_amount(*surf_uv(X, Y, Z, p)) > -0.05: return None
    return t, p, (Y - (YS - 0.75)) / 1.05, nrm(n)
def cornice_sh(x, y, a, b, z, wp):
    n = nrm(shell_hit_normal(wp[0], wp[1], wp[2], wp[1] > YS, 0.5))
    v = 2.0 + (2.2 if b > 0.82 else (-1.2 if b > 0.66 else (1.0 + 1.2 * math.sin(b / 0.66 * math.pi))))
    v += (wn(1, S(a) * 2.0, wp[1] * 2) - 0.5) * 0.5
    if (S(a) / 1.6) % 1 < z / F / 1.6: v -= 1.0
    return shade(GREY, v, wp, n, x, y)
raycast(rs, cornice_cast, cornice_sh, cls='wall', rows=range(250, 470))

# the ribs: chamfered stone up the walls (a base at the foot) and over the vault
def rib_cast(dx, dy):
    t, kind, n = shell_hit(dx, dy, 0.85)
    X, Y, Z = dx * t, CAMH + dy * t, t
    if Y < 0: return None
    p = phi_of(X, Z, 0.85)
    s_ = math.sqrt(max(0.0, 1 - ((Y - YS) / (BV - 0.85)) ** 2)) if kind == 'vault' else 1.0
    best = None
    for k, pr in enumerate(RIBR):
        dd = (p - pr) * rloc(p, 0.85) * s_
        hw = 0.62 + (0.25 if Y < 0.9 else 0.0)
        if abs(dd) < hw: best = (k, dd / hw); break
    if best is None: return None
    if tissue_amount(*surf_uv(X, Y, Z, p)) > 0.25: return None
    return t, best[1], best[0] + (0.5 if kind == 'vault' else 0.0), nrm(n)
def rib_sh(x, y, a, b, z, wp):
    X, Y, Z = wp
    vault = (b % 1) > 0.25
    n = nrm(shell_hit_normal(X, Y, Z, vault, 0.85))
    along = (YS + (BV - 0.85) * math.asin(min(1.0, (Y - YS) / (BV - 0.85)))) if vault else Y
    blk = math.floor(along / 0.95); f = (along / 0.95) % 1
    v = 2.2 + (h32(blk, int(b), 9) % 5) * 0.18 + (wn(1, along * 2, a * 3 + b) - 0.5) * 0.7 + (wn(0, along * 0.3, b * 5) - 0.5) * 0.8
    if h32(blk, int(b), 10) % 9 == 0: v -= 0.5                                                     # a darker, dirtier stone
    if h32(blk, int(b), 11) % 13 == 0 and abs(a) > 0.4 and f > 0.6: v -= 1.0                        # a chipped corner
    v += 0.9 * (-a) if abs(a) > 0.55 else 0.0                                                      # chamfers: one lit, one dark
    if abs(a) < 0.12: v += 0.35                                                                    # the roll down the middle
    if f < max(0.05, z / F / 0.95 * 1.1): v -= 1.5                                                 # the joints
    if Y < 0.9: v = 2.6 + (0.8 if Y > 0.75 else 0) - (0.6 if abs(a) > 0.8 else 0)                # the base
    for (sp, sy) in SCONCES:                                                                       # wax run down from the sconce
        if int(b) == RIBS.index(sp) and sy - 3.2 < Y < sy - 0.3:
            col_ = int((a + 1) * 7)
            if h32(col_, sp, 4) % 4 == 0 and Y > sy - 0.5 - (h32(col_, sp, 5) % 5) * 0.3 and abs(a) < 0.6:
                return shade(WAX, 1.2 + (0.6 if h32(col_, 6) % 2 else 0), wp, n, x, y, gain=2.6)
    v -= 2.6 * soot(X, Y, Z)
    vn = VM.sample(*surf_uv(X, Y, Z))
    if vn and vn[0] > 0.3: return shade(VEIN, 1.6 + (0 if vn[1] else 0.8), wp, n, x, y, gain=2.0, warm=0.3)
    return shade(GREY, v, wp, n, x, y)
raycast(rs, rib_cast, rib_sh, cls='wall')

# ---------------------------------------------------------------------------------------------------- the floor
def floor_sh(x, y, s, t, z, wp):
    X, _, Z = wp
    D = 2.5
    row = math.floor(Z / D); fz = Z / D - row
    Wd = 2.2 + (h32(row, 1) % 3) * 0.5
    uu = X + (h32(row, 2) % 10) / 10.0 * Wd
    col = math.floor(uu / Wd); fx = uu / Wd - col
    ps, psz = z / F, z * z / (F * CAMH)
    sid = h32(col, row, 3)
    rr = SAND if sid % 5 == 0 else GREY
    v = (1.9 if rr is SAND else 2.1) + ((sid % 7) - 3) * 0.1 + (wn(0, X * 0.3, Z * 0.3) - 0.5) * 0.9 + (wn(1, X * 2.6, Z * 1.2) - 0.5) * 0.35
    # worn smooth (a shade paler, polished) along the ways people walked: the doorway -> the desk -> the stair
    for (ax, az, bx, bz) in ((-22.0, 18.5, -2.0, 18.6), (2.0, 18.6, 18.0, 22.5)):
        t_ = max(0.0, min(1.0, ((X - ax) * (bx - ax) + (Z - az) * (bz - az)) / ((bx - ax) ** 2 + (bz - az) ** 2)))
        dd = math.hypot(X - ax - (bx - ax) * t_, Z - az - (bz - az) * t_)
        v += 0.45 * math.exp(-(dd / 1.6) ** 2) * (0.7 + 0.3 * wn(2, X * 0.8, Z * 0.8))
    if sid % 6 == 0 and abs((fx - 0.2) - fz * 0.6) < ps / Wd * 1.2: v -= 1.2                        # a crack
    n = (0.0, 1.0, 0.0)
    du, de = DOOR.local(X, Z)
    if de > 0.2 and abs(du) < DOOR.hw + 0.1:
        return DOOR_GLOW(shade(rr, v - (1.6 if (fx < ps / Wd * 1.3 or fz < psz / D * 1.3) else 0), wp, n, x, y, gain=2.2), wp)
    if fx < ps / Wd * 1.3 or fz < psz / D * 1.3: return shade(rr, v - 1.6, wp, n, x, y, gain=2.2)
    for (cx_, cz_) in WAXSPOTS:                                                                    # old wax on the stones
        if (X - cx_) ** 2 + (Z - cz_) ** 2 < 0.05 + (h32(int(cx_ * 10), int(cz_ * 10)) % 5) * 0.012:
            return shade(WAX, 3.4, wp, n, x, y, gain=2.4)
    return shade(rr, v, wp, n, x, y, gain=3.2)
WAXSPOTS = [(-4.6 + rng(i, 1) * 3, 19.3 + rng(i, 2) * 1.0) for i in range(5)] + \
           [(3.6 + rng(i, 3) * 2.4, 19.4 + rng(i, 4)) for i in range(4)] + [(-17.0 + rng(i, 5) * 2, 21.0 + rng(i, 6) * 1.5) for i in range(5)]
rs.quad((-32, 0, 3), (32, 0, 3), (-32, 0, 40), floor_sh, cls='ground')
for k, (px_, pz_, a_) in enumerate(((-15.6, 20.6, 0.4), (-14.2, 21.4, -0.3), (-9.6, 18.8, 0.9), (6.6, 18.4, -0.6), (12.8, 21.6, 0.2))):
    ca, sa = math.cos(a_), math.sin(a_)
    rs.quad((px_, 0.04 + k * 0.004, pz_), (px_ + ca * 1.0, 0.04 + k * 0.004, pz_ + sa * 1.0), (px_ - sa * 0.75, 0.04 + k * 0.004, pz_ + ca * 0.75),
            lambda x, y, s, t, z, wp: shade(PARCH, 2.6 - (1.0 if (t * 12) % 1 < 0.14 and 0.15 < s < 0.85 else 0) + (wn(1, wp[0] * 3, wp[2] * 3) - 0.5), wp, (0.0, 1.0, 0.0), x, y, gain=2.6))

def rug(x, y, s, t, z, wp):
    X, _, Z = wp
    u, v = abs(s - 0.5) * 2, abs(t - 0.5) * 2
    worn = wn(1, X * 1.1, Z * 1.1) > 0.66 and u < 0.86 and v < 0.86
    if u > 0.93 or v > 0.94:
        if (h32(int(X * 6), int(Z * 6), 3) % 3 == 0) and (u > 0.97 or v > 0.97): return None        # frayed edge
        rmp, val = RUGO, 0.9
    elif u > 0.86 or v > 0.88: rmp, val = RUGO, 1.0 + (0.7 if (int(s * 70) + int(t * 50)) % 2 else 0)
    elif abs(math.hypot(u * 1.3, v) - 0.55) < 0.03: rmp, val = RUGO, 0.9
    elif math.hypot(u * 1.3, v) < 0.55: rmp, val = RUGR, 1.2 + (0.4 if (int(s * 30) + int(t * 22)) % 2 else 0)
    else: rmp, val = RUGR, 1.6 + (wn(2, X * 2, Z * 2) - 0.5)
    if worn: val -= 0.8
    c = shade(rmp, val, wp, (0.0, 1.0, 0.0), x, y, gain=2.6, warm=0.3)
    g_ = (c[0] + c[1] + c[2]) // 3
    return mix(c, (g_, g_, g_ - 2), 0.35)                                                          # faded
rs.quad((-5.4, 0.03, 14.0), (5.4, 0.03, 14.0), (-5.4, 0.03, 18.9), rug, cls='ground', cut=True)

# ---------------------------------------------------------------------------------------------------- the exits
def stone_plane(n, seed, v0=3.2, along='u', O=None, op=None):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u, e = op.local(X, Z)
        rr, v = masonry(GREY, e if along == 'e' else u, Y, z, x, y, v0, ch=0.6, L=0.95, seed=seed, pale=SAND)
        return shade(rr, v, wp, n, x, y)
    return sh
def passage_glow(op, col, k0, k1, amt):
    """the air in a passage fills with the light at its end: mix towards that light with the distance in"""
    def f(c, wp):
        u, e = op.local(wp[0], wp[2])
        if e <= k0: return c
        return mix(c, col, min(1.0, (e - k0) / (k1 - k0)) ** 1.3 * amt)
    return f
STAIR_GLOW = passage_glow(STAIR, (232, 190, 112), 1.0, 9.5, 0.85)
DOOR_GLOW = passage_glow(DOOR, (140, 150, 142), 0.3, 6.5, 0.5)

def passage(op, kind):
    P = op.P
    glow = DOOR_GLOW if kind == 'door' else STAIR_GLOW
    hw, L = op.hw, op.L
    slope = 0.0 if kind == 'door' else 0.62 / 0.82
    def soffit_y(u, e): return op.arch(u) + slope * max(0.0, e - 1.2)
    for sg in (-1, 1):                                                                             # the jambs / passage walls
        ni = (-sg * op.et[0], 0.0, -sg * op.et[1])
        sh0 = stone_plane(ni, 31 + sg, 3.0, 'e', op=op)
        def jamb(x, y, s, t, z, wp, sh0=sh0):
            u, e = op.local(wp[0], wp[2])
            if wp[1] > soffit_y(u, e): return None
            return glow(sh0(x, y, s, t, z, wp), wp)
        rs.quad(P(sg * hw, 0.0, -0.4), P(sg * hw, 0.0, L), P(sg * hw, 18.0, -0.4), jamb, cls='wall', cut=True)
    N = 10                                                                                         # the arched soffit, in strips
    for i in range(N):
        u0, u1 = -hw + 2 * hw * i / N, -hw + 2 * hw * (i + 1) / N
        ss = 1 if kind == 'door' else 6
        for j in range(ss):
            e0, e1 = -0.4 + (L + 0.4) * j / ss, -0.4 + (L + 0.4) * (j + 1) / ss
            def sof(x, y, s, t, z, wp):
                u, e = op.local(wp[0], wp[2])
                v = 2.6 + (0.4 if (e / 0.9) % 1 < 0.1 else 0) - (0.9 if (abs(u) / 0.45) % 1 < 0.12 else 0)
                return glow(shade(GREY, v, wp, (0.0, -1.0, 0.0), x, y), wp)
            rs.quad(P(u0, soffit_y(u0, e0), e0), P(u1, soffit_y(u1, e0), e0), P(u0, soffit_y(u0, e1), e1), sof, cls='ceil')
    return soffit_y

# --- the doorway: a short passage out to the cathedral's door and the grey day of the threshold
passage(DOOR, 'door')
def day_end(x, y, s, t, z, wp):
    X, Y, Z = wp
    u, e = DOOR.local(X, Z)
    hw2 = DOOR.hw - 0.35
    inside = abs(u) < hw2 and Y < DOOR.ys - 0.2 + math.sqrt(max(0.0, (DOOR.R - 0.3) ** 2 - (abs(u) + DOOR.R - DOOR.hw) ** 2))
    if not inside:
        rr, v = masonry(GREY, u, Y, z, x, y, 3.6, ch=0.6, L=0.95, seed=44)
        return shade(rr, v, wp, (-DOOR.eo[0], 0.0, -DOOR.eo[1]), x, y)
    if u > hw2 - 0.9 and Y < 6.0:                                                                  # the door leaf, open
        v = 3.4 + (0.6 if (u * 4) % 1 < 0.15 else 0) - (1.0 if abs(Y - 1.6) < 0.12 or abs(Y - 4.4) < 0.12 else 0)
        return mix(tone(OAK, v + 1.0, x, y), (120, 128, 122), 0.25)
    if Y < 1.0:                                                                                    # the parvis outside
        return mix((112, 114, 106), (96, 98, 90), (h32(int(u * 3), int(Y * 9)) % 3) / 3.0)
    k = min(1.0, (Y - 1.0) / 6.0)                                                                  # the grey day, hazy
    return mix((150, 158, 150), (178, 184, 174), k) if (x + y) % 4 else mix((140, 148, 140), (168, 174, 164), k)
rs.quad(DOOR.P(-DOOR.hw - 0.2, 0.0, DOOR.L), DOOR.P(DOOR.hw + 0.2, 0.0, DOOR.L), DOOR.P(-DOOR.hw - 0.2, 10.0, DOOR.L), day_end, cls='emit')
light(*DOOR.P(0.0, 4.2, DOOR.L - 0.6), DAY, 2.4, 6.5)
light(*DOOR.P(0.0, 3.6, 0.4), DAY, 0.9, 6.0)
light(*DOOR.P(0.0, 2.0, -3.0), DAY, 0.35, 6.0)

# --- the stair: up and away into the warm light of the heart
soffit = passage(STAIR, 'stair')
NST = 12
for i in range(NST):
    e0 = 1.2 + i * 0.82; yt = (i + 1) * 0.62
    def riser(x, y, s, t, z, wp, i=i):
        u, e = STAIR.local(wp[0], wp[2])
        v = 2.6 + (1.0 if wp[1] > (i + 1) * 0.62 - 0.08 else 0) + (wn(1, u * 2, wp[1] * 3) - 0.5) * 0.5
        if (u / 1.25 + i * 0.4) % 1 < 0.05: v -= 1.0
        return STAIR_GLOW(shade(GREY, v, wp, (-STAIR.eo[0], 0.0, -STAIR.eo[1]), x, y, gain=3.4), wp)
    def tread(x, y, s, t, z, wp):
        u, e = STAIR.local(wp[0], wp[2])
        v = 3.4 + 0.6 * math.exp(-(u / 0.9) ** 2) + (wn(0, u * 1.5, e * 2) - 0.5) * 0.6        # worn in the middle
        return STAIR_GLOW(shade(GREY, v, wp, (0.0, 1.0, 0.0), x, y, gain=3.4), wp)
    obox(rs, STAIR.O, STAIR.ang, -STAIR.hw, STAIR.hw, 0.0, yt, e0, STAIR.L + 0.5, riser, riser, tread, cls='prop')
def stair_end(x, y, s, t, z, wp):
    X, Y, Z = wp
    u, e = STAIR.local(X, Z)
    if Y > 9.4 + (u + STAIR.hw) * 0.25:                                                            # light from above, round the turn
        return tone(GLOWC, 3.2 + (Y - 9.4) * 0.35 + (wn(1, u * 2, Y) - 0.5) * 0.6, x, y)
    rr, v = masonry(GREY, u, Y, z, x, y, 3.6, ch=0.6, L=0.95, seed=46)
    return shade(rr, v, wp, (-STAIR.eo[0], 0.0, -STAIR.eo[1]), x, y, gain=3.6, warm=0.7)
rs.quad(STAIR.P(-STAIR.hw - 0.2, 0.0, STAIR.L), STAIR.P(STAIR.hw + 0.2, 0.0, STAIR.L), STAIR.P(-STAIR.hw - 0.2, 20.0, STAIR.L), stair_end, cls='emit')
light(*STAIR.P(0.0, 10.5, 8.0), GOLD, 3.0, 8.0)
light(*STAIR.P(0.0, 7.0, 4.0), GOLD, 1.6, 6.5)
light(*STAIR.P(0.0, 4.0, 0.5), GOLD, 0.9, 6.0)
light(*STAIR.P(0.0, 2.5, -2.0), GOLD, 0.5, 5.0)

# ---------------------------------------------------------------------------------------------------- the desk
DZ0, DZ1, DY = 19.6, 23.6, 2.9
def oak(v0, axis='x', grain=9.0, n=(0.0, 0.0, -1.0), flesh_from=None):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        a = X if axis == 'x' else Z
        v = v0 + (wn(1, a * 0.5, Y * grain + Z * 0.3) - 0.5) * 1.0 + (wn(0, a * 2.2, Y * 0.9) - 0.5) * 0.3
        if flesh_from is not None:                                                                 # half wood, half something that pulses
            g = (Z - flesh_from) / 1.6 + (wn(5, X * 0.7, Y * 0.7) - 0.5) * 1.2
            if g > 0.55: return shade(TISSUE, 3.2 + (wn(1, X * 0.8, Y * 0.8) - 0.5) * 2, wp, n, x, y, gain=2.6, warm=0.3)
            if g > 0.4: return shade(VEIN, 1.8, wp, n, x, y)
        return shade(OAK, v, wp, n, x, y, gain=3.0, warm=0.45)
    return sh
UP, FRONT, RIGHT, LEFT = (0.0, 1.0, 0.0), (0.0, 0.0, -1.0), (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0)
# the top, its moulded edge, the apron with a drawer, two pedestals with drawers; the knee hole dark
rs.box(-6.1, 6.1, DY - 0.28, DY, DZ0, DZ1, oak(4.6, n=FRONT), oak(4.0, n=LEFT), top=oak(4.4, 'x', 1.5, UP, flesh_from=22.4))
def pedestal(x0, x1):
    def front(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = 3.2 + (wn(1, X * 0.6, Y * 6) - 0.5) * 0.8
        for yb in (0.75, 1.5):
            if abs(Y - yb) < 0.05: v -= 1.4
        if abs(Y - 0.32) < 0.32 and t < 0.2: v -= 0.6
        for yb in (0.4, 1.1, 1.8):                                                                 # brass pulls
            if abs(Y - yb) < 0.07 and abs(X - (x0 + x1) / 2) < 0.28: return shade(BRASS, 2.6, wp, FRONT, x, y)
        if Y < 0.18: v -= 0.8
        return shade(OAK, v, wp, FRONT, x, y)
    rs.box(x0, x1, 0.0, DY - 0.28, DZ0 + 0.15, DZ1 - 0.1, front, oak(2.6, 'z', n=RIGHT if x0 > 0 else LEFT, flesh_from=21.8))
pedestal(-5.9, -3.3); pedestal(3.3, 5.9)
def apron(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 3.0 + (wn(1, X * 0.6, Y * 6) - 0.5) * 0.8 - (1.3 if abs(X) > 1.5 and abs(X) < 1.6 else 0)
    if abs(X) < 0.3 and abs(Y - 2.35) < 0.06: return shade(BRASS, 2.8, wp, FRONT, x, y)
    return shade(OAK, v, wp, FRONT, x, y)
rs.box(-3.3, 3.3, 2.05, DY - 0.28, DZ0 + 0.2, DZ1 - 0.2, apron, apron)
rs.quad((-3.3, 0.0, DZ1 - 0.6), (3.3, 0.0, DZ1 - 0.6), (-3.3, 2.05, DZ1 - 0.6),
        lambda x, y, s, t, z, wp: shade(OAK, 0.9, wp, FRONT, x, y, gain=1.0), cls='prop')

# the hutch of pigeonholes against the apse, scrolls in every hole, sheathed in membrane
HZ0, HZ1, HX = 23.4, 25.0, 5.2
def pigeon(x, y, s, t, z, wp):
    X, Y, Z = wp
    cols, rows = 5, 4
    cu = (X + HX - 0.25) / ((2 * HX - 0.5) / cols); cv = (Y - 3.3) / ((8.3 - 3.3) / rows)
    if X < -HX + 0.25 or X > HX - 0.25 or Y < 3.3 or Y > 8.3 or (cu % 1) < 0.08 or (cv % 1) < 0.1:
        v = 3.8 + (wn(1, X * 0.5, Y * 7) - 0.5) * 0.8 + (0.7 if (cv % 1) < 0.04 else 0)
        return shade(OAK, v, wp, FRONT, x, y)
    ci, cj = int(cu), int(cv)
    fu, fv = (cu % 1 - 0.08) / 0.92, (cv % 1 - 0.1) / 0.9
    # the rolled scrolls inside: two or three rows of round ends
    nscroll = 2 + h32(ci, cj, 4) % 3
    if h32(ci, cj, 5) % 7 == 0: nscroll = 0                                                       # one empty hole
    for k in range(nscroll * 2):
        sx_ = 0.2 + (k % nscroll) * 0.6 / max(1, nscroll - 1) if nscroll > 1 else 0.5
        sy_ = 0.25 + (k // nscroll) * 0.42
        r = 0.16 + (h32(ci, cj, k) % 3) * 0.02
        dd = math.hypot(fu - sx_, (fv - sy_) * 1.25)
        if dd < r:
            if dd > r * 0.82: return shade(PARCH, 2.0, wp, FRONT, x, y)
            spiral = (math.atan2(fv - sy_, fu - sx_) / (2 * math.pi) + dd / r * 3) % 1
            v = 3.8 + (0.6 if spiral < 0.2 else 0) - (fv - sy_) * 3
            if fu - sx_ < -r * 0.3 and fv - sy_ < -r * 0.3: v += 1.4                             # the membrane's gloss
            return shade(PARCH, v, wp, FRONT, x, y)
    return shade(OAK, 1.0 + fv * 0.6, wp, FRONT, x, y, gain=1.4)
rs.box(-HX, HX, DY, 8.6, HZ0, HZ1, pigeon, oak(3.0, 'z', n=LEFT, flesh_from=24.2))
rs.box(-HX - 0.3, HX + 0.3, 8.6, 9.1, HZ0 - 0.25, HZ1, oak(4.6, n=FRONT), oak(3.4, 'z', n=LEFT), bottom=oak(1.8, n=(0.0, -1.0, 0.0)))

# on the desk: the journal under its membrane, membrane-sheathed scrolls, an inkwell, a quill
JX, JZ = -0.3, 20.8
def journal(x, y, s, t, z, wp):
    X, Y, Z = wp
    if Y > DY + 0.24: return shade(LEATHER, 3.6 + (wn(1, X * 3, Z * 3) - 0.5) * 1.2 - (1.0 if abs(X - JX - 1.05) < 0.06 else 0), wp, UP, x, y, gain=3)
    if t < 0.5 and Z < JZ + 0.1: return shade(PARCH, 4.4 - (1.0 if (Y * 40) % 1 < 0.3 else 0), wp, FRONT, x, y)   # the page edges
    return shade(LEATHER, 2.6, wp, FRONT, x, y)
rs.box(JX - 1.2, JX + 1.2, DY, DY + 0.3, JZ, JZ + 1.7, journal, journal, top=journal)
rs.line3((JX + 0.6, DY + 0.31, JZ + 0.2), (JX + 0.75, DY + 0.05, JZ - 0.15), lambda *a: (110, 30, 26), w=0.06)   # the ribbon
def membrane(x, y, s, t, z, wp):
    X, Y, Z = wp
    e = min(s, 1 - s, t, 1 - t)
    if e < 0.025 and h32(x, y, 2) % 3: return (120, 104, 92)                                      # its edge, a little thicker
    d = (s * 0.8 + t * 0.6) % 1                                                                    # the gloss: two soft diagonal streaks
    if 0.18 < d < 0.22 or 0.62 < d < 0.64: return (226, 214, 190) if 0.2 < s < 0.9 else None
    if (0.15 < d < 0.25 or 0.6 < d < 0.66) and (x + y) % 2 == 0 and 0.15 < s < 0.92: return (170, 156, 136)
    return None
rs.quad((JX - 1.55, DY + 0.36, JZ - 0.3), (JX + 1.55, DY + 0.36, JZ - 0.3), (JX - 1.55, DY + 0.36, JZ + 2.0), membrane, cls='prop', cut=True)
def scroll_sh(v0):
    def sh(x, y, s, t, z, wp):
        if s < 0:                                                                                  # the end: a rolled spiral
            sp = (t * 3) % 1
            return shade(PARCH, 3.0 + (0.8 if sp < 0.25 else 0), wp, FRONT, x, y)
        v = v0 + 2.2 * math.cos(t * 2 * math.pi + 0.6) - 0.6
        if 0.04 < t < 0.1 or (s * 9) % 1 < 0.04: v += 1.6                                         # the membrane's highlights
        return shade(PARCH, v, wp, UP, x, y)
    return sh
hcyl(rs, (-5.4, DY + 0.24, 22.4), (-2.2, DY + 0.24, 22.8), 0.24, scroll_sh(3.0))
hcyl(rs, (-5.1, DY + 0.66, 22.7), (-2.6, DY + 0.66, 22.9), 0.2, scroll_sh(2.6))
hcyl(rs, (2.0, DY + 0.22, 22.6), (4.6, DY + 0.22, 22.1), 0.22, scroll_sh(3.2))
rs.box(1.6, 2.2, DY, DY + 0.5, 20.5, 21.1, lambda x, y, s, t, z, wp: shade(IRON, 1.6 + t, wp, FRONT, x, y),
       lambda x, y, s, t, z, wp: shade(IRON, 1.2, wp, RIGHT, x, y), top=lambda x, y, s, t, z, wp: (12, 10, 9))  # the inkwell
rs.line3((1.9, DY + 0.5, 20.8), (2.6, DY + 1.9, 21.4), lambda x, y, s, t, z, wp: (196, 188, 168) if s > 0.35 else (90, 84, 70), w=0.07)
for i in range(4):                                                                                 # loose sheets
    a0 = -0.3 + i * 0.2
    rs.quad((1.0 + i * 0.25, DY + 0.01 + i * 0.005, 19.9 + i * 0.1), (2.6 + i * 0.3, DY + 0.01 + i * 0.005, 19.85 + i * 0.15 + a0),
            (1.0 + i * 0.25, DY + 0.01 + i * 0.005, 21.1 + i * 0.1), lambda x, y, s, t, z, wp: shade(PARCH, 4.2 - (1.2 if (t * 14) % 1 < 0.12 and 0.15 < s < 0.85 else 0), wp, UP, x, y))

# candles on tendril cups, burning low; the cathedral keeps them lit
def cup(X, Y0, Z, r=0.42):
    rs.disc(X, Y0 - 0.05, Z - 0.05, r, lambda x, y, s, t, z, wp: tone(TISSUE, 4.2 - t * 2.2 - s * 0.8, x, y) if t > -0.25 else None)
cup(-4.4, DY + 0.1, 20.8); cup(4.5, DY + 0.1, 21.3)
candle(rs, -4.6, DY, 20.7, 1.25, I=1.1, R=8.0); candle(rs, -4.1, DY, 21.1, 0.7, I=0.6, lean=0.5); candle(rs, -4.9, DY, 21.2, 0.45, I=0.4)
candle(rs, 4.4, DY, 21.2, 0.95, I=1.0, R=8.0, lean=-0.4); candle(rs, 4.9, DY, 20.9, 0.55, I=0.5)
candle(rs, 0.6, 9.1, 24.0, 0.8, I=0.8)                                                             # on top of the hutch

# her chair, pushed back from the desk
def chair_sh(v0, n):
    return lambda x, y, s, t, z, wp: shade(OAK, v0 + (wn(1, wp[0] * 2 + wp[2] * 2, wp[1] * 5) - 0.5) * 0.8, wp, n, x, y)
CO, CA = (-7.6, 0.0, 19.4), -0.55
obox(rs, CO, CA, -1.0, 1.0, 1.8, 2.1, -1.0, 1.0, chair_sh(3.8, FRONT), chair_sh(3.0, LEFT), chair_sh(4.4, UP))
def seat_cloth(x, y, s, t, z, wp): return shade(RUGR, 3.2 + (wn(1, wp[0] * 3, wp[2] * 3) - 0.5), wp, UP, x, y)
obox(rs, CO, CA, -0.85, 0.85, 2.1, 2.22, -0.85, 0.85, seat_cloth, seat_cloth, seat_cloth)
for (lu, le) in ((-0.9, -0.9), (0.9, -0.9), (-0.9, 0.9), (0.9, 0.9)):
    obox(rs, CO, CA, lu - 0.1, lu + 0.1, 0.0, 1.8, le - 0.1, le + 0.1, chair_sh(2.6, FRONT), chair_sh(2.0, LEFT), chair_sh(3, UP))
def chair_back(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 3.2 + (wn(1, X * 2 + Z * 2, Y * 5) - 0.5) * 0.8
    if 0.12 < s < 0.88 and 0.25 < t < 0.8: v -= 0.9                                                # the carved panel
    if 0.12 < s < 0.88 and 0.25 < t < 0.8 and abs(math.hypot((s - 0.5) * 1.6, (t - 0.55) * 1.0) - 0.18) < 0.03: v += 1.4
    if t > 0.9: v += 0.8
    return shade(OAK, v, wp, (0.5, 0.0, -0.85), x, y)
obox(rs, CO, CA, -1.0, 1.0, 2.1, 6.4, 0.85, 1.05, chair_back, chair_sh(2.4, LEFT), chair_sh(4.6, UP))
for sg in (-1, 1): obox(rs, CO, CA, sg * 1.0 - 0.12, sg * 1.0 + 0.12, 6.4, 6.85, 0.8, 1.1, chair_sh(4.0, FRONT))   # finials

# ---------------------------------------------------------------------------------------------------- the walls
def at_wall(phid):
    p = phid * DEG
    O = (WX * math.cos(p), 0.0, ZC + CL * math.sin(p))
    n = nrm((math.cos(p) / WX, 0.0, math.sin(p) / CL))
    return O, wall_frame(n[0], n[2]), (-n[0], 0.0, -n[2])
def cabinet(phid, w, h, seed, cols=3, rows=5):
    """a tall cabinet of pigeonholes against the wall, every hole full of scrolls sheathed in membrane"""
    O, ang, nin = at_wall(phid)
    ef, eb = -1.6, -0.15
    def front(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = s * w - w / 2
        cu = (u + w / 2 - 0.25) / ((w - 0.5) / cols); cv = (Y - 0.9) / ((h - 1.4) / rows)
        if u < -w / 2 + 0.25 or u > w / 2 - 0.25 or Y < 0.9 or Y > h - 0.5 or (cu % 1) < 0.07 or (cv % 1) < 0.08:
            v = 3.4 + (wn(1, u * 0.5 + seed, Y * 7) - 0.5) * 0.9 + (0.6 if (cv % 1) < 0.035 else 0) - (0.9 if Y < 0.5 else 0)
            return shade(OAK, v, wp, nin, x, y)
        ci, cj = int(cu), int(cv)
        fu, fv = (cu % 1 - 0.07) / 0.93, (cv % 1 - 0.08) / 0.92
        if h32(ci, cj, seed) % 9 == 0:                                                             # a bundle of loose sheets
            if fv < 0.45: return shade(PARCH, 3.0 + (1.0 if (fv * 30) % 1 < 0.3 else 0), wp, nin, x, y)
            return shade(OAK, 0.9, wp, nin, x, y, gain=1.2)
        ns = 2 + h32(ci, cj, seed + 1) % 2
        for k in range(ns * 3):
            sx_ = 0.18 + (k % ns) * 0.64 / max(1, ns - 1)
            sy_ = 0.2 + (k // ns) * 0.3
            r = 0.12 + (h32(ci, cj, k, seed) % 3) * 0.015
            dd = math.hypot(fu - sx_, (fv - sy_) * 1.6)
            if dd < r and h32(ci, cj, k, 9) % 6:
                if dd > r * 0.8: return shade(PARCH, 1.8, wp, nin, x, y)
                v = 3.6 - (fv - sy_) * 4 + (0.6 if (dd / r * 3) % 1 < 0.25 else 0)
                if fu - sx_ < -r * 0.3 and fv - sy_ < -r * 0.25: v += 1.5
                return shade(PARCH, v, wp, nin, x, y)
        return shade(OAK, 1.0 + fv * 0.5, wp, nin, x, y, gain=1.2)
    side = lambda x, y, s, t, z, wp: shade(OAK, 2.6 + (wn(1, wp[2] * 3, wp[1] * 6) - 0.5), wp, (0.0, 0.0, -1.0), x, y)
    top = lambda x, y, s, t, z, wp: shade(OAK, 4.2, wp, UP, x, y)
    obox(rs, O, ang, -w / 2, w / 2, 0.0, h, ef, eb, front, side, top)
    obox(rs, O, ang, -w / 2 - 0.2, w / 2 + 0.2, h, h + 0.4, ef - 0.25, eb, lambda x, y, s, t, z, wp: shade(OAK, 4.4 - (1.2 if t < 0.3 else 0), wp, nin, x, y), side, top)
    return O, ang
cabinet(115, 5.0, 7.6, 3)
cabinet(66, 5.0, 7.6, 5)

def chest(phid, w, h, seed):
    O, ang, nin = at_wall(phid)
    def front(x, y, s, t, z, wp):
        u = s * w - w / 2; Y = wp[1]
        v = 3.0 + (wn(1, u * 0.6 + seed, Y * 6) - 0.5) * 0.9
        if abs(Y - (h - 0.35)) < 0.06 or abs(abs(u) - (w / 2 - 0.4)) < 0.06: v -= 1.2
        if abs(u) < 0.25 and abs(Y - (h - 0.8)) < 0.22: return shade(IRON, 2.6, wp, nin, x, y)       # the lock plate
        for su in (-w / 2 + 0.6, w / 2 - 0.6):
            if abs(u - su) < 0.12: return shade(IRON, 1.8 + (0.6 if (Y * 4) % 1 < 0.2 else 0), wp, nin, x, y)   # iron straps
        return shade(OAK, v, wp, nin, x, y)
    obox(rs, O, ang, -w / 2, w / 2, 0.0, h, -1.9, -0.2, front, front,
         lambda x, y, s, t, z, wp: shade(OAK, 3.8 + (wn(1, wp[0] * 2, wp[2] * 2) - 0.5), wp, UP, x, y))
    return O, ang, nin
O, ang, nin = chest(133, 4.4, 2.2, 11)
P_, et, eo = frame(O, ang)
for k, (u, e, hh) in enumerate(((-1.3, -1.1, 1.1), (-0.8, -0.8, 0.6), (-0.4, -1.3, 0.85), (1.1, -1.0, 0.4))):
    X_, _, Z_ = P_(u, 0.0, e)
    candle(rs, X_, 2.2, Z_, hh, r=0.15, I=0.45 if k else 0.6)
X_, _, Z_ = P_(0.9, 0.0, -1.1)                                                                     # a stack of sheathed scrolls
hcyl(rs, (X_ - 0.6, 2.42, Z_ - 0.2), (X_ + 0.7, 2.42, Z_ + 0.2), 0.2, scroll_sh(3.0))
hcyl(rs, (X_ - 0.5, 2.78, Z_ - 0.1), (X_ + 0.6, 2.78, Z_ + 0.25), 0.17, scroll_sh(2.8))

# a lectern by the right wall with a heavy book open on it
O, ang, nin = at_wall(22)
P_, et, eo = frame(O, ang)
LX, _, LZ = P_(0.0, 0.0, -2.6)
cyl(rs, LX, LZ, 0.28, 0.0, 4.0, lambda x, y, s, t, z, wp: shade(OAK, 3.0 + 1.4 * math.cos(math.atan2(wp[0] - LX, -(wp[2] - LZ)) + 0.6), wp, None, x, y), n=10)
rs.box(LX - 0.9, LX + 0.9, 0.0, 0.3, LZ - 0.9, LZ + 0.9, lambda x, y, s, t, z, wp: shade(OAK, 2.6, wp, FRONT, x, y),
       lambda x, y, s, t, z, wp: shade(OAK, 2.0, wp, LEFT, x, y), top=lambda x, y, s, t, z, wp: shade(OAK, 3.4, wp, UP, x, y))
def lect_top(x, y, s, t, z, wp):
    if 0.08 < s < 0.92 and 0.1 < t < 0.92:
        if abs(s - 0.5) < 0.02: return shade(PARCH, 2.0, wp, (0.0, 0.7, -0.7), x, y)
        v = 4.4 - abs(s - 0.5) * 2.4 - (1.1 if (t * 16) % 1 < 0.14 and 0.14 < abs(s - 0.5) * 2 < 0.85 else 0)
        return shade(PARCH, v, wp, (0.0, 0.7, -0.7), x, y)
    return shade(LEATHER, 3.0, wp, (0.0, 0.7, -0.7), x, y)
rs.quad((LX - 1.0, 4.0, LZ - 0.5), (LX + 1.0, 4.0, LZ - 0.5), (LX - 1.0, 4.7, LZ + 0.5), lect_top)

# ---------------------------------------------------------------------------------------------------- living tissue
TS = tissue_tube(3.4)
# tendrils pouring from the apse over the hutch and down to the desk; roots from the pedestals into the floor
for pts, r0, r1 in (
        ([(-2.6, 14.5, 25.4), (-3.6, 10.6, 25), (-4.9, 9.2, 24.2), (-5.6, 6.0, 23.8), (-5.9, 3.2, 23.4)], 0.55, 0.3),
        ([(2.2, 15.0, 25.4), (3.4, 10.8, 25), (4.9, 9.3, 24.3), (5.7, 6.2, 23.8), (6.0, 3.1, 23.5)], 0.55, 0.3),
        ([(-0.6, 13.0, 25.5), (-0.9, 10.0, 24.8), (-1.6, 9.2, 23.8), (-2.4, 9.15, 23.3)], 0.45, 0.22),
        ([(0.8, 12.6, 25.5), (1.4, 9.9, 24.8), (2.6, 9.2, 23.6), (3.2, 8.4, 23.25)], 0.4, 0.18),
        ([(-5.6, 1.6, 23.6), (-6.4, 0.5, 23.4), (-7.6, 0.15, 22.8), (-9.8, 0.1, 22.4)], 0.4, 0.12),
        ([(5.7, 1.6, 23.6), (6.6, 0.5, 23.2), (8.2, 0.15, 22.6), (10.0, 0.1, 23.1)], 0.4, 0.12),
        ([(-3.4, 0.3, 23.2), (-3.0, 0.12, 21.8), (-2.2, 0.08, 20.6)], 0.22, 0.08),
        ([(3.4, 0.3, 23.2), (3.9, 0.12, 22), (4.6, 0.08, 21.2)], 0.2, 0.08)):
    tube(rs, pts, r0, r1, TS)
# on the rib shafts the cathedral holds out candles on tendrils of its own, wax running down the stone below
def sconce(phid, Y, I=0.6, h=0.7, lean=0.0):
    p = phid * DEG
    A, C = WX - 0.85, CL - 0.85
    B = (A * math.cos(p), Y, ZC + C * math.sin(p))
    nn = nrm((math.cos(p) / A, 0.0, math.sin(p) / C)); ni = (-nn[0], 0.0, -nn[2])
    M = (B[0] + ni[0] * 0.5, Y - 0.35, B[2] + ni[2] * 0.5)
    E = (B[0] + ni[0] * 1.05, Y + 0.25, B[2] + ni[2] * 1.05)
    tube(rs, [(B[0] - ni[0] * 0.1, Y + 0.6, B[2] - ni[2] * 0.1), (B[0] + ni[0] * 0.15, Y - 0.1, B[2] + ni[2] * 0.15), M, E], 0.24, 0.16, TS)
    tube(rs, [(B[0], Y + 1.4, B[2]), (B[0] + ni[0] * 0.05, Y + 0.7, B[2] + ni[2] * 0.05)], 0.1, 0.18, TS)   # its root up the stone
    cup(E[0], E[1] + 0.1, E[2], 0.34)
    candle(rs, E[0], E[1] + 0.05, E[2], h, r=0.14, I=I, R=7.0, lean=lean)
for phid, Y, I, h in SCONCE_SPEC:
    sconce(phid, Y, I, h)

# ---------------------------------------------------------------------------------------------------- render
img = rs.render(INK, fog=K.fog, light_gain=0.8, grime_gain=0.5, bloom=0.5, stain_gain=0.15, damp_gain=0.15, sheen_gain=0.3)
img.save(f'{OUT}/study.png')
print('door outline', DOOR.outline())
print('stair outline', STAIR.outline())
print('journal on screen', [round(v) for v in proj(JX, DY + 0.3, JZ + 0.85)])
print('desk front corners', [round(v) for v in proj(-6.1, DY, DZ0)], [round(v) for v in proj(6.1, 0, DZ0)])
print('hutch top', [round(v) for v in proj(0, 9.1, HZ0)])
