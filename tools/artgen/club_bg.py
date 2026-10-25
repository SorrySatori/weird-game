"""The club under the Screaming Cork (ScreamingCorkClubScene), 1067x600, the shared camera (raster3d.py). After the old
art (ScreamingCorkClub.png): a brick cellar under a shallow barrel vault, brick ribs across it; the stage of old planks
runs wall to wall at the back for Feral Toast (their sprites stand on it); on the back wall the band's painted cloth
banner, and over it, bricked into the vault's end like a rose window, a ring of salvaged speaker cones -- the Noise
God's altar, a few of them breathing a faint green; three industrial lamps over the stage (where the scene draws its
light cones), amp stacks at both ends, a backstage door in the left wall, a gig bill, cables everywhere, salt blooms on
the damp brick, bottle caps and corks on the concrete.

    python3 club_bg.py <outdir>   ->  club.png
Fixed points (canvas): the band's feet on the stage (y 470 front, 452 back; x 0.24 / 0.39 / 0.55 / 0.71 of the width);
the lamps' shades end at y ~118 over x 272 / 515 / 787; the banner x ~426..640, y ~183..280; the way back up to the
tavern is behind the camera (the exit at the bottom edge)."""
import sys, os, math
from PIL import Image, ImageDraw, ImageFont
from common import h32, draw_text, text_width
from shedkit import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = Raster()
WX, ZB, YS, YC = 32.0, 28.0, 18.0, 30.0                                             # half width, back wall, vault spring, crown
R = (WX * WX + (YC - YS) ** 2) / (2 * (YC - YS)); VC = YC - R
def vault_y(X): return VC + math.sqrt(max(0.0, R * R - X * X))
SZ, SH = 16.6, 1.8                                                                  # the stage's front edge and height
def fog(z): return max(0.0, min(0.35, (z - 14) / 55.0))
FOGI = (18, 12, 10)
def fg(c, z): return mix(c, FOGI, fog(z))
BRICK = ramp('#120807 #1c0d0a #28120e #341912 #412017 #4f281c #5e3122 #6d3b2a')
MORTAR = ramp('#151210 #1e1a16 #29241e #342e27')
CONC = ramp('#100f0d #181613 #211e1a #2b2722 #36312b #423c34')
PLANK = ramp('#100c08 #18120c #221a11 #2c2216 #372a1c #433322')
TOLEX = ramp('#0a0a0a #121212 #1b1b1a #252524 #302f2d')
GRILLE = ramp('#14110e #1d1914 #27221b #322b22')
CLOTH = ramp('#121410 #1a1d16 #23271e #2d3226 #383e2f')
CREAM = ramp('#5e5440 #7a6e54 #968a6a #b2a680 #ccc29a')
SALT = (150, 142, 124)

def brick(u, Y, x, y, z, v0=3.4, salt=True):
    """running-bond brick in world units along u (the horizontal along the surface) and Y; damp and salt at the foot"""
    row = math.floor(Y / 0.32); off = (row % 2) * 0.33
    col = math.floor((u + off) / 0.66)
    fu = ((u + off) / 0.66) % 1; fv = (Y / 0.32) % 1
    px = z / F
    if fv < max(0.1, px / 0.32 * 0.9) or fu < max(0.06, px / 0.66 * 0.9):
        c = tone(MORTAR, 1.8 + (wn(1, u * 2, Y * 2) - 0.5), x, y)
    else:
        v = v0 + (h32(col, row, 3) % 4) * 0.35 - (0.8 if h32(col, row, 4) % 9 == 0 else 0) + (wn(0, u * 1.3, Y * 1.3) - 0.5) * 0.8
        c = tone(BRICK, v, x, y)
    damp = max(0.0, 1 - Y / 3.0)
    if salt:
        m = wn(2, u * 0.7, Y * 0.9) + damp * 0.35
        if m > 0.84 and Y < 4: c = mix(c, SALT, min(0.28, (m - 0.84) * 3))       # salt blooms where the damp rises
    return mix(c, (8, 6, 5), damp * 0.35)

# ---------------------------------------------------------------------------------------------------- the cellar
def floor_sh(x, y, s, t, z, wp):
    X, _, Z = wp
    i, j = math.floor(X / 2.4), math.floor(Z / 2.4)
    v = 2.8 + (h32(i, j, 5) % 3) * 0.3 + (wn(0, X * 0.6, Z * 0.6) - 0.5) * 0.9
    if (X / 2.4) % 1 < 0.9 * z / F / 2.4 + 0.01 or (Z / 2.4) % 1 < 0.9 * z * z / (F * CAMH) / 2.4 + 0.01: v -= 1.0
    c = tone(CONC, v, x, y)
    m = wn(2, X * 0.7, Z * 0.9)
    if m > 0.8: c = mix(c, (10, 8, 6), min(0.3, (m - 0.8) * 3))                       # old spills
    return fg(c, z)
rs.quad((-WX, 0, 3), (WX, 0, 3), (-WX, 0, SZ), floor_sh, cls='ground')
def back_wall(x, y, s, t, z, wp):
    X, Y, Z = wp
    if Y > vault_y(X): return None
    return fg(brick(X, Y, x, y, z), z)
rs.quad((-WX, 0, ZB), (WX, 0, ZB), (-WX, YC, ZB), back_wall, cls='wall', cut=True)
def side(sign):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        return fg(brick(Z, Y, x, y, z, v0=3.0), z)
    return sh
for sg in (-1, 1):
    rs.quad((sg * WX, 0, 3), (sg * WX, 0, ZB), (sg * WX, YS, 3), side(sg), cls='wall')
N = 40
for i in range(N):                                                                  # the vault, in strips
    X0, X1 = -WX + 2 * WX * i / N, -WX + 2 * WX * (i + 1) / N
    def vsh(x, y, s, t, z, wp):
        X, Y, Z = wp
        arc = R * math.atan2(X, Y - VC)
        c = brick(Z, arc + 40, x, y, z, v0=2.6, salt=False)
        m = wn(3, X * 1.1, Z * 0.9)
        if m > 0.8: c = mix(c, (10, 8, 6), min(0.25, (m - 0.8) * 2.5))             # water stains seeping through
        return fg(c, z)
    rs.quad((X0, vault_y(X0), 3), (X1, vault_y(X1), 3), (X0, vault_y(X0), ZB), vsh, cls='ceil')
def rib(zr):
    """a brick arch across the vault on two pilasters, its voussoirs radial"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        vy = vault_y(X)
        if abs(X) > WX - 1.1 and Y < YS:
            return fg(brick(Y * 0.0 + X * 0.0 + Y, Y, x, y, z, v0=3.6), z) if True else None
        if vy - 1.1 < Y <= vy:
            a = math.atan2(X, Y - VC) * R / 0.42
            fa = a % 1; fr = (vy - Y) / 1.1
            if fa < max(0.08, z / F / 0.42) or abs(fr - 0.5) < 0.04: return fg(tone(MORTAR, 1.6, x, y), z)
            return fg(tone(BRICK, 3.8 + (h32(int(a), 7) % 3) * 0.3 - fr * 0.8, x, y), z)
        return None
    rs.quad((-WX, 0, zr), (WX, 0, zr), (-WX, YC, zr), sh, cls='wall', cut=True)
rib(21.0); rib(25.0)

# ---------------------------------------------------------------------------------------------------- the stage
def stage_top(x, y, s, t, z, wp):
    X, Y, Z = wp
    pl = math.floor(Z / 0.7); fu = (Z / 0.7) % 1
    seg = math.floor((X + (h32(pl, 2) % 7)) / 5.0)
    v = 3.0 + (h32(pl, seg, 3) % 3) * 0.3 + (wn(0, X * 0.5, Z * 2) - 0.5) * 0.8
    if fu < 0.9 * z * z / (F * (CAMH - SH)) / 0.7 + 0.02: v -= 1.2
    if ((X + (h32(pl, 2) % 7)) / 5.0) % 1 < 0.9 * z / F / 5.0 + 0.004: v -= 0.9
    if abs(Z - 17.4 - math.sin(X * 0.3) * 0.4) < 0.08 and -26 < X < 26: return fg((30, 30, 28), z)            # a cable
    if h32(int(X), int(Z * 2), 9) % 37 == 0: v += 1.2                                                          # tape marks
    return fg(tone(PLANK, v, x, y), z)
rs.quad((-WX, SH, SZ), (WX, SH, SZ), (-WX, SH, ZB), stage_top, cls='ground')
def stage_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    if Y > SH - 0.2: return fg(tone(PLANK, 4.2, x, y), z)                          # the worn nosing
    v = 2.0 + (h32(int(Y / 0.45), 5) % 3) * 0.3 - (1.0 if (Y / 0.45) % 1 < 0.1 else 0) - (0.6 if (X / 6.0) % 1 < 0.02 else 0)
    if wn(1, X * 0.8, Y) > 0.68: v -= 0.8                                           # kicked, scuffed
    return fg(tone(PLANK, v, x, y), z)
rs.quad((-WX, 0, SZ), (WX, 0, SZ), (-WX, SH, SZ), stage_front, cls='prop')

# ---------------------------------------------------------------------------------------------------- the banner, the speaker altar, the bill
BAN = (-10.0, 10.0, 13.6, 22.4, ZB - 0.12)
def banner_mask():
    x0, x1, y0, y1, z = BAN
    (ax, ay) = proj(x0 + 1.2, y1 - 1.1, z); (bx, by) = proj(x1 - 1.2, y0 + 1.3, z)
    w, h = int(bx - ax), int(by - ay)
    path = '/usr/share/fonts/TTF/DejaVuSansCondensed-Bold.ttf'
    im = Image.new('L', (w, h), 0); d = ImageDraw.Draw(im); d.fontmode = '1'
    lines = ['FERAL', 'TOAST']
    if os.path.exists(path):
        size = 70
        while size > 8:
            f = ImageFont.truetype(path, size)
            bbs = [d.textbbox((0, 0), ln, font=f) for ln in lines]
            th = sum(b[3] - b[1] for b in bbs) + size * 0.18
            if max(b[2] - b[0] for b in bbs) <= w and th <= h: break
            size -= 1
        yy = (h - th) / 2
        for ln, b in zip(lines, bbs):
            d.text(((w - (b[2] - b[0])) / 2 - b[0], yy - b[1]), ln, font=f, fill=255)
            yy += b[3] - b[1] + size * 0.18
    else:
        for i, ln in enumerate(lines):
            draw_text(lambda x, y: (0 <= x < w and 0 <= y < h) and im.putpixel((x, y), 255), ln, (w - text_width(ln, 5)) // 2, 4 + i * 34, 5)
    p = im.load()
    return {(int(ax) + x, int(ay) + y) for y in range(h) for x in range(w) if p[x, y]}
LET = banner_mask()
def banner(x, y, s, t, z, wp):
    """painted cloth nailed at the top corners: it sags between them, folds hang down from the nails, the hem is torn"""
    X, Y, Z = wp
    sag = 0.35 * math.sin(s * math.pi)
    if t > 1 - sag / (BAN[3] - BAN[2]): return None
    hem = 0.05 + 0.04 * math.sin(s * 37) + 0.03 * math.sin(s * 91)
    if t < hem: return None
    fold = math.sin(s * math.pi * 7 + math.sin(t * 3) * 0.6)
    v = 2.6 + fold * 0.7 * (0.4 + 0.6 * t) + (wn(1, X * 1.5, Y * 1.5) - 0.5) * 0.6
    if (x, y) in LET:
        wear = wn(2, X * 2.2, Y * 2.2)
        if wear < 0.72: return fg(tone(CREAM, 2.8 + fold * 0.6 + (wn(0, X * 3, Y * 3) - 0.5), x, y), z)       # the paint, cracked
    if math.hypot(s - 0.03, t - 0.97) < 0.012 or math.hypot(s - 0.97, t - 0.97) < 0.012: return fg(RUSTY[3], z)   # nails
    return fg(tone(CLOTH, v, x, y), z)
rs.quad((BAN[0], BAN[2], BAN[4]), (BAN[1], BAN[2], BAN[4]), (BAN[0], BAN[3], BAN[4]), banner, cls='prop', cut=True)
SPK = []                                                                             # the speaker altar over the banner
for ring, (rad, n, rr) in enumerate(((8.6, 13, 1.05), (6.2, 9, 0.75))):
    for k in range(n):
        a = math.pi * (0.06 + 0.88 * k / (n - 1))
        X, Y = rad * math.cos(a), 21.6 + rad * math.sin(a) * 0.82
        if Y + rr > vault_y(X) - 0.3: continue
        SPK.append((X, Y, rr * (0.85 + (h32(ring, k, 1) % 4) * 0.08), h32(ring, k, 2)))
SPK.append((0.0, 25.4, 1.5, 7))                                                     # the big one at the crown
for (X, Y, rr, seed) in SPK:
    alive = seed % 4 == 0
    def cone(x, y, s, t, z, wp, rr=rr, seed=seed, alive=alive):
        d = math.hypot(s, t)
        if d > 1: return None
        if d > 0.86: return fg(tone(METAL, 1.4 + (1.2 if t < -0.3 else 0), x, y), z)                     # the basket rim
        if d > 0.78: return fg((26, 22, 18), z)                                                           # the surround
        if d < 0.24:
            if alive: return MYC[3] if d < 0.12 else MYC[2]                                               # it breathes green
            return fg(tone(TOLEX, 3.2 - t * 1.5, x, y), z)                                                # the dust cap
        v = 1.6 + (d - 0.24) * 2.2 - t * 0.8 + (0.6 if (d * 9) % 1 < 0.2 else 0)
        if seed % 5 == 1 and abs(math.atan2(t, s) - 0.8) < 0.1: return fg((8, 6, 5), z)                   # a torn cone
        c = tone(TOLEX, v, x, y)
        return mix(c, MYC[1], 0.35 * (1 - d)) if alive else fg(c, z)
    rs.disc(X, Y, ZB - 0.25, rr, cone, cls='emit' if alive else 'prop')
def gig(x, y, s, t, z, wp):
    """a gig bill: GIG in black, a toast with fangs, lines of small print, a torn corner"""
    if s < 0.1 and t > 0.88: return None
    if 0.15 < s < 0.85 and 0.72 < t < 0.92: return (24, 20, 16) if (int(s * 14) % 4 != 3) else (176, 160, 120)
    if 0.3 < s < 0.7 and 0.4 < t < 0.66:
        u, v = (s - 0.5) / 0.2, (t - 0.53) / 0.13
        if u * u + v * v < 1: return (150, 96, 40) if v > -0.6 else (232, 226, 206)
    if 0.12 < s < 0.88 and t < 0.34 and int(t * 22) % 2 == 0 and h32(int(s * 9), int(t * 22), 3) % 3: return (60, 52, 40)
    return (178, 162, 124) if (x + y) % 6 else (150, 136, 102)
rs.quad((13.2, 15.2, ZB - 0.12), (16.6, 15.2, ZB - 0.12), (13.2, 19.8, ZB - 0.12), gig, cls='prop', cut=True)

# ---------------------------------------------------------------------------------------------------- lamps (the scene's light cones start at their shades)
for sx in (272, 515, 787):
    LZ = 20.0
    X = (sx - CX) * LZ / F
    Yb = CAMH + (HY - 118) * LZ / F
    top = vault_y(X) - 0.15
    rs.line3((X, Yb + 1.1, LZ), (X, top, LZ), lambda x, y, s, t, z, wp: fg((18, 16, 14), z), w=0.09)
    rs.quad((X - 1.15, Yb, LZ), (X + 1.15, Yb, LZ), (X - 1.15, Yb + 1.2, LZ),
            lambda x, y, s, t, z, wp: (fg(tone(METAL, 2.0 + (1.2 if s < 0.35 else 0) - t, x, y), z) if abs(s - 0.5) * 2 < 0.22 + 0.78 * (1 - t) ** 0.55 else None),
            cls='prop', cut=True)
    rs.quad((X - 1.1, Yb, LZ - 0.45), (X + 1.1, Yb, LZ - 0.45), (X - 1.1, Yb, LZ + 0.45),
            lambda x, y, s, t, z, wp: (GLOW[4] if (2 * s - 1) ** 2 + (2 * t - 1) ** 2 < 0.35 else GLOW[2]) if (2 * s - 1) ** 2 + (2 * t - 1) ** 2 < 1 else None,
            cls='emit', cut=True)

# ---------------------------------------------------------------------------------------------------- amps, the backstage door, the cellar's clutter
def cab(x0, x1, y0, y1, z0, head=False):
    def front(x, y, s, t, z, wp):
        if s < 0.06 or s > 0.94 or t < 0.06 or t > 0.94:
            if (s < 0.1 or s > 0.9) and (t < 0.1 or t > 0.9): return fg(METAL[3], z)                   # corner protectors
            return fg(tone(TOLEX, 2.4, x, y), z)
        if head:
            if 0.55 < t < 0.75 and int(s * 10) % 2 == 0 and 0.2 < s < 0.9: return fg(METAL[4], z)       # knobs
            return fg(tone(TOLEX, 1.6, x, y), z)
        if t > 0.86: return fg(tone(TOLEX, 3.0, x, y), z) if not (0.4 < s < 0.6) else fg(METAL[4], z)   # a logo plate
        return fg(tone(GRILLE, 2.0 + (0.6 if (x + y) % 2 else 0), x, y), z)
    rs.box(x0, x1, y0, y1, z0, z0 + 2.0, front, lambda x, y, s, t, z, wp: fg(tone(TOLEX, 1.8, x, y), z),
           top=lambda x, y, s, t, z, wp: fg(tone(TOLEX, 3.2, x, y), z), cls='prop')
for sg in (-1, 1):
    xa, xb = sorted((sg * 30.6, sg * 25.4))
    cab(xa, xb, SH, SH + 3.6, 24.0); cab(xa, xb, SH + 3.6, SH + 7.2, 24.0); cab(xa + 0.3, xb - 0.3, SH + 7.2, SH + 8.6, 24.2, head=True)
def backstage(x, y, s, t, z, wp):
    X, Y, Z = wp
    cz, w2, sp = 21.0, 1.7, SH + 6.0
    d = math.hypot(Z - cz, max(0.0, Y - sp))
    if abs(Z - cz) > w2 + 0.5 or (Y >= sp and d > w2 + 0.5) or Y < SH: return None
    if abs(Z - cz) > w2 or (Y >= sp and d > w2): return fg(tone(BRICK, 4.4 - (1.0 if int(math.atan2(Y - sp, Z - cz) * 6) % 2 else 0), x, y), z)
    v = 1.8 + (h32(int((Z - cz) / 0.6 + 10), 6) % 3) * 0.3 - (1.0 if ((Z - cz) / 0.6) % 1 < 0.1 else 0)
    if abs(Y - SH - 3.6) < 0.18 and Z > cz + 0.9: return fg(METAL[4], z)
    return fg(tone(PLANK, v + 1.0, x, y), z)
rs.quad((-WX + 0.05, 0, 18.5), (-WX + 0.05, 0, 23.5), (-WX + 0.05, 10.5, 18.5), backstage, cls='prop', cut=True)
rs.line3((-26.0, SH + 0.02, 24.0), (-14.0, SH + 0.02, 19.0), lambda x, y, s, t, z, wp: fg((26, 26, 24), z), w=0.12)   # cables to the amps
rs.line3((26.0, SH + 0.02, 24.0), (16.0, SH + 0.02, 20.5), lambda x, y, s, t, z, wp: fg((26, 26, 24), z), w=0.12)
def crate(X0, Z0, seed, Y0=0.0):
    def front(x, y, s, t, z, wp):
        if s < 0.08 or s > 0.92 or t < 0.1 or t > 0.9: return fg(tone(PLANK, 4.0, x, y), z)
        return fg(tone(PLANK, 2.2 + (0.8 if (s * 5) % 1 < 0.5 and t > 0.5 else 0), x, y), z)
    def top(x, y, s, t, z, wp):
        if (s * 4) % 1 < 0.55 and (t * 3) % 1 < 0.65: return fg(tone(LEAF, 0.6 + (1.4 if (x + y) % 3 == 0 else 0), x, y), z)
        return fg((12, 10, 8), z)
    rs.box(X0, X0 + 2.0, Y0, Y0 + 1.2, Z0, Z0 + 1.4, front, lambda x, y, s, t, z, wp: fg(tone(PLANK, 2.6, x, y), z), top=top, cls='prop')
crate(-29.0, 15.0, 1); crate(-28.8, 15.1, 2, 1.2); crate(-26.7, 15.2, 3); crate(26.4, 15.0, 4)
for k in range(46):                                                                 # caps and corks on the concrete
    fx, fz = -30 + (h32(k, 61) % 600) / 10.0, 10.0 + (h32(k, 62) % 66) / 10.0
    c = [CORK if False else GLOW[1], (120, 92, 60), METAL[4], (140, 108, 70)][k % 4]
    rs.disc(fx, 0.08, fz, 0.13, lambda x, y, s, t, z, wp, c=c: fg(c if t < 0.2 else mix(c, (0, 0, 0), 0.4), z))

img = rs.render(INK, fog=fog, light_gain=1.2, grime_gain=0.7, bloom=0.5, stain_gain=0.3, damp_gain=0.35)
img.save(f'{OUT}/club.png')
print('done club')
