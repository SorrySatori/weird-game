"""Inside the Townhall (TownhallInteriorScene): the council hall, 1067x600, on the shared rasteriser (raster3d.py, the
standard camera: VP (533, 296), F 300, eye 12 units, the walk line y 534 = depth 15). After the old art
(townhall_interior.png): a tall vaulted gothic hall, the great rose window high in the back wall, a raised bench at the
back, candle stands, arches down the sides.

  back     the rose window (twelve lobes round an oculus, like a clock face -- the seal of the house), cool daylight;
           under it the council's bench: a long carved table on a raised platform, seven high-backed chairs behind it
           (the middle one taller, a brass seal on it), ledgers, a great brass stamp, candles; tall iron candelabra at
           both ends; two dark banners; a pointed doorway either side
  left     the records: oak archive cabinets of small drawers between the piers, brass label-holders, a few drawers
           pulled out with papers sticking from them, a rolling ladder; in the third bay a low pointed door (the way
           down to the Ink Tribunal's room)
  right    tall lancets with the overcast day in them, oak wainscot, a long public bench under them
  middle   the public reading dais (two steps up, a stone base with an oak top), a lectern on it; a red runner down
           the aisle; scattered papers -- the hall has had a long siege of poetry
  above    a ribbed quadripartite vault on clustered piers, two iron candle-rings hanging on chains
  floor    polished flagstones that mirror the windows and the candles

    python3 townhall_int_bg.py <outdir>   ->  townhall_interior.png (+ fixed.json: the canvas points the scene uses)"""
import sys, os, math, json
from PIL import Image
from common import h32, ramp, band, make_noise
from raster3d import Raster, proj, ray, W, H, CX, HY, F, CAMH

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
R = ramp
SAND = R('#17140f #201c15 #2a251c #353024 #413b2d #4e4737 #5c5442 #6b624e #7b715b #8c8169 #9d927a')
FLAG = R('#121210 #1a1a17 #23231f #2d2c27 #383630 #44413a #514d45 #5e5a51')
FLAG2 = R('#16120e #1f1913 #29211a #342a21 #40342a #4c3e33 #594a3e')
OAK = R('#110b07 #1a110a #24170e #2f1f13 #3b2818 #48321e #563c25 #64472d #735335')
RED = R('#1a0a09 #270e0c #361311 #461915 #57201a #692820 #7c3227')
BRASS = R('#2e220e #4a3716 #6a5020 #8c6b2c #ae8a3e #cbaa5a #e4ca82')
IRON = R('#0b0c0c #121414 #1a1d1d #232727 #2d3232 #393f3e')
DAYG = R('#3e4c46 #4c5c55 #5c6d65 #6e8077 #82948a #98a99e #b0beb2 #c8d3c6')
PAPER = R('#4a463a #625d4c #7b7560 #948d75 #aca58b #c2bba0')
GLOW = R('#6e5424 #957130 #bb8f3e #d9ad52 #efcb73 #fff0c0')
STAIN = [(132, 98, 46), (52, 98, 96), (118, 44, 40), (84, 66, 108), (96, 112, 60)]
INK = (7, 8, 7)
FOGI = (26, 26, 22)
def fog(z): return max(0.0, min(0.28, (z - 18) / 110.0))

_nz = [make_noise(1, s, 509, 509) for s in (71, 72, 73, 74)]
def wn(i, a, b): return _nz[i](a + 3000.0, b + 3000.0)
def ri(r, i): return r[max(0, min(len(r) - 1, int(i)))]
def tone(r, v, x, y): return ri(r, band(v, x, y))
def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def fg(c, z): return mix(c, FOGI, fog(z))

# ---------------------------------------------------------------------------------------------------- geometry
WX, ZB, YS, YC = 24.0, 44.0, 22.0, 52.0          # half width, back wall, vault springing, crown
VCX = (YC - YS) ** 2 / (2 * WX) - WX / 2         # the pointed arch: centre offset of each half's circle
VCX = ((YC - YS) ** 2 - WX ** 2) / (2 * WX)
VR = WX + VCX
def vault_y(X):
    """the pointed vault's height over X: each half is an arc centred on the far side of the springing line"""
    c = VCX if X <= 0 else -VCX
    return YS + math.sqrt(max(0.0, VR * VR - (X - c) ** 2))
PIERS = (12.0, 20.0, 28.0, 36.0)
ROSE = (0.0, 31.0, 8.6)                          # the rose window: centre X, Y, radius (in the back wall)
PLAT, PLAT_Z = 1.8, 35.2                          # the council platform: height, front
TABLE = (-11.0, 11.0, 37.2, 39.2, 4.7)           # x0, x1, z0, z1, top
DAIS = (-5.0, 5.0, 16.4, 20.6, 1.1)              # x0, x1, z0, z1, top (the poet reads from it, feet ~ z 17.6)
DOOR_T = (22.4, 25.6, 8.6)                       # the Tribunal's door in the left wall: z0, z1, height
WIN_R = ((14.4, 17.6), (22.4, 25.6), (30.4, 33.6))  # the lancets in both side walls (z0, z1)
WIN_Y = (8.2, 20.6)                              # the right ones; the left ones sit over the cabinets
WIN_YL = (11.4, 20.8)

def day(X, Y, Z):
    """the overcast day: from the rose window high in the back, from the lancets (brighter on the right); dark towards
    the camera and up in the vault"""
    d = 0.6 * math.exp(-math.dist((X, Y, Z), (0.0, ROSE[1] - 6.0, ZB)) / 16.0)
    for (z0, z1) in WIN_R:
        d += 0.4 * math.exp(-math.dist((X, Y, Z), (WX, 12.0, (z0 + z1) / 2)) / 7.5)
        d += 0.16 * math.exp(-math.dist((X, Y, Z), (-WX, 15.0, (z0 + z1) / 2)) / 6.0)
    return min(1.0, d) * (0.55 + 0.45 * min(1.0, max(0.0, (Z - 8.0) / 16.0)))

def ashlar(u, Y, z, x, y, v0, r=SAND, ch=0.9, L=1.7, seed=0):
    """big coursed blocks of warm stone, thin joints, a tone per block, soot higher up"""
    ps = z / F
    row = math.floor(Y / ch); fv = Y / ch - row
    uu = u + (h32(row, seed, 5) % 97) / 97.0 * L
    col = math.floor(uu / L); fu = uu / L - col
    bid = h32(row, col, seed + 7)
    v = v0 + ((bid % 7) - 3) * 0.16 + (wn(0, u * 0.25 + seed, Y * 0.25) - 0.5) * 1.1 + (wn(1, u * 4.0, Y * 4.0) - 0.5) * 0.4
    if bid % 13 == 0: v -= 0.6
    elif bid % 17 == 0: v += 0.4
    if wn(3, u * 0.9 + seed * 3, 1.0) > 0.62 and (wn(3, u * 0.9 + seed * 3, 1.0) - 0.62) * 30 > (Y % 7.0): v -= 0.5   # runs of damp
    if fv < max(0.04, ps / ch * 0.9) or fu < max(0.025, ps / L * 0.9): v -= 1.3
    elif fv > 1 - ps / ch * 1.2: v += 0.35
    return tone(r, v, x, y)

rs = Raster()

# ---------------------------------------------------------------------------------------------------- the floor
RUN = 2.3                                                                                # the runner's half width
def floor_sh(x, y, s, t, z, wp):
    X, _, Z = wp
    D = 2.6
    i, j = math.floor(X / D + 0.5), math.floor(Z / D)
    fx, fz_ = X / D + 0.5 - i, Z / D - j
    dark = (i + j) % 2 == 0
    r_ = FLAG2 if dark else FLAG
    v = (2.6 if dark else 3.4) + (h32(i, j, 3) % 3) * 0.25 + (wn(0, X * 0.5, Z * 0.5) - 0.5) * 0.9 + 3.0 * day(X, 0, Z)
    v -= 0.9 * max(0.0, 1 - (Z - 9) / 10.0)
    if fx < 0.9 * z / F / D + 0.012 or fz_ < 0.9 * z * z / (F * CAMH) / D + 0.012: v -= 1.4      # joints
    if h32(i, j, 8) % 9 == 0 and abs((fx - 0.3) - (fz_ - 0.2) * 0.7) < 0.02: v -= 1.2         # a crack
    c = tone(r_, v, x, y)
    if abs(X) < RUN and (Z < DAIS[2] - 0.8 or DAIS[3] < Z < PLAT_Z - 1.0):                  # the red runner
        e = RUN - abs(X)
        rv = 2.0 + 2.2 * day(X, 0, Z) + (wn(1, X * 2, Z * 0.5) - 0.5) * 0.7
        if e < 0.28: c = tone(BRASS, 1.6 + rv * 0.5, x, y) if 0.08 < e < 0.2 else tone(RED, rv - 0.8, x, y)
        else:
            c = tone(RED, rv + (0.5 if (abs(X) * 3 + Z * 0.8) % 1.6 < 0.1 else 0), x, y)
            if wn(2, X * 1.2, Z * 0.6) > 0.66: c = mix(c, (70, 52, 40), 0.35)                    # trodden bald
        return fg(c, z)
    for (z0, z1) in WIN_R:                                                                 # the lancets' light on the floor
        q = max(0.0, 1 - abs(Z - (z0 + z1) / 2 - (WX - X) * 0.18) / 2.4) * max(0.0, 1 - (WX - X) / 13.0)
        if q > 0: c = mix(c, (128, 146, 138), 0.22 * q)
    # the open street doors behind the camera: daylight lying on the floor at the front
    k = max(0.0, 1 - abs(X) / 6.5) * max(0.0, 1 - (Z - 9.5) / 6.0)
    if k > 0: c = mix(c, (118, 134, 126), 0.35 * k)
    return fg(c, z)
rs.quad((-WX, 0, 3), (WX, 0, 3), (-WX, 0, ZB), floor_sh, cls='ground')

# ---------------------------------------------------------------------------------------------------- the vault
def vault_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 1.1 + 1.8 * day(X, Y, Z) + (wn(0, X * 0.3, Z * 0.3) - 0.5) * 0.7
    ps = z / F
    for zr in PIERS + (ZB,):                                                                # transverse ribs
        if abs(Z - zr) < 0.55: return fg(tone(SAND, v + 1.4 - abs(Z - zr) * 1.2, x, y), z)
    zs = [3.0] + list(PIERS) + [ZB]
    for a_, b_ in zip(zs, zs[1:]):                                                          # diagonal ribs, the ridge rib
        if a_ <= Z < b_:
            zm, hb = (a_ + b_) / 2, (b_ - a_) / 2
            q = abs(abs(X) / WX - abs(Z - zm) / hb)
            if q < 0.03 + ps * 0.02: return fg(tone(SAND, v + 1.1, x, y), z)
            if abs(X) < 0.35: return fg(tone(SAND, v + 0.8, x, y), z)
    # the webs: thin courses running along the bay, soot
    arc = math.atan2(Y - YS, abs(X)) * 6
    if (arc % 1) < 0.05: v -= 0.6
    v -= 0.8 * max(0.0, (Y - 30) / 22.0) * (wn(2, X * 0.5, Z * 0.5) > 0.45)
    return fg(tone(SAND, v, x, y), z)
NV = 48
for i in range(NV):
    X0, X1 = -WX + 2 * WX * i / NV, -WX + 2 * WX * (i + 1) / NV
    rs.quad((X0, vault_y(X0), 3), (X1, vault_y(X1), 3), (X0, vault_y(X0), ZB), vault_sh, cls='ceil')

# ---------------------------------------------------------------------------------------------------- the back wall, the rose window
def rose_glass(x, y, s, t, z, wp):
    """twelve lobes round an oculus, like the clock outside: tracery bars, muted stained panes, the day behind"""
    X, Y, Z = wp
    dx, dy = X - ROSE[0], Y - ROSE[1]
    r = math.hypot(dx, dy) / ROSE[2]
    if r > 1: return None
    a = math.atan2(dy, dx); seg = (a / (2 * math.pi) * 12) % 1
    ps = z / F / ROSE[2]
    bar = 0.022 + ps * 0.9
    if r > 0.94: return tone(SAND, 4.6 - r * 2, x, y)                                          # the outer moulding
    if r < 0.24:                                                                               # the oculus: a seal
        if abs(r - 0.22) < bar or abs(r - 0.12) < bar: return tone(SAND, 3.0, x, y)
        return mix(tone(DAYG, 5.0 - r * 6, x, y), (150, 120, 70), 0.35) if r < 0.12 else mix(tone(DAYG, 4.4, x, y), STAIN[2], 0.45)
    if abs(r - 0.25) < bar or abs(r - 0.62) < bar * 0.8: return tone(SAND, 3.2, x, y)
    if seg < bar * 2.2 / max(0.3, r): return tone(SAND, 3.0, x, y)                             # radial mullions
    if r < 0.62:                                                                               # the inner petals
        lobe = math.hypot((seg - 0.5) * 2.2, (r - 0.45) / 0.18)
        if abs(lobe - 1.0) < 0.12: return tone(SAND, 3.0, x, y)
        k = int(a / (2 * math.pi) * 12 + 12) % 12
        base = tone(DAYG, 4.0 + (r - 0.25) * 2 - (0.6 if lobe > 1 else 0) + (wn(3, X * 1.5, Y * 1.5) - 0.5) * 1.2, x, y)
        return mix(base, STAIN[k % len(STAIN)], 0.62 if lobe <= 1 else 0.3)
    # the outer trefoils, twelve of them
    fo = math.hypot((seg - 0.5) * 2.6, (r - 0.79) / 0.13)
    if abs(fo - 1.0) < 0.13: return tone(SAND, 3.0, x, y)
    if fo > 1.0: return tone(SAND, 2.6 + (r - 0.62), x, y)
    k = int(a / (2 * math.pi) * 12 + 12) % 12
    return mix(tone(DAYG, 5.4 - abs(seg - 0.5) * 2, x, y), STAIN[(k + 2) % len(STAIN)], 0.3 if k % 2 else 0.12)
rs.quad((-ROSE[2], ROSE[1] - ROSE[2], ZB + 0.3), (ROSE[2], ROSE[1] - ROSE[2], ZB + 0.3), (-ROSE[2], ROSE[1] + ROSE[2], ZB + 0.3),
        rose_glass, cls='emit', cut=True)
DOORS_B = (-19.0, 19.0)
def back_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    if Y > vault_y(X): return None
    d = math.hypot(X - ROSE[0], Y - ROSE[1])
    if d < ROSE[2] - 0.05: return None
    if d < ROSE[2] + 1.0: return fg(tone(SAND, 5.2 - (d - ROSE[2]) * 1.6 + (0.6 if Y > ROSE[1] else -0.4), x, y), z)   # the rose's hood
    for dx_ in DOORS_B:                                                                       # pointed doorways
        if abs(X - dx_) < 2.4 and Y < 9.2:
            ap = 6.6 + math.sqrt(max(0.0, 2.4 ** 2 - (abs(X - dx_) + 1.0) ** 2)) * 1.4
            if Y < ap - 0.5 and abs(X - dx_) < 1.9: return fg(tone(OAK, 2.0 + (0.6 if (X - dx_ + 2) % 0.95 < 0.12 else 0) + 0.8 * day(X, Y, Z), x, y), z)
            if Y < ap: return fg(tone(SAND, 5.0, x, y), z)
    v = 2.5 + 2.6 * day(X, Y, Z) - 0.8 * max(0.0, 1 - Y / 2.0) - 0.7 * max(0.0, (Y - 26.0) / 26.0)
    for cxs in (-14.4, 14.4):                                                                  # soot over the candelabra
        if abs(X - cxs) < 1.6 and 11.0 < Y < 19.0: v -= (1 - abs(X - cxs) / 1.6) * (1 - (Y - 11.0) / 8.0) * 1.4
    if abs(Y - YS) < 0.5: return fg(tone(SAND, v + 1.2 - (0.9 if Y < YS - 0.2 else 0), x, y), z)   # the string course
    return fg(ashlar(X, Y, z, x, y, v, ch=1.1, L=2.1, seed=3), z)
rs.quad((-WX, 0, ZB), (WX, 0, ZB), (-WX, YC + 0.5, ZB), back_sh, cls='wall', cut=True)
for bx in (-15.0, 15.0):                                                                     # banners: the house's seal on dark red
    def banner(x, y, s, t, z, wp, bx=bx):
        X, Y, Z = wp
        u = (X - bx) / 2.2; v = (Y - 10.0) / 10.6
        if v < 0.14 and abs(u) > v / 0.14: return None                                         # a swallowtail
        if v > 0.96: return tone(BRASS, 3.4, x, y) if abs(u) < 1.0 else None                    # the rod
        fold = math.sin(u * 7.0) * 0.5
        c = tone(RED, 2.6 + fold + 1.6 * day(X, Y, Z) - (0.6 if abs(u) > 0.88 else 0), x, y)
        rr_ = math.hypot(u * 2.2, (v - 0.6) * 4.4)
        if abs(rr_ - 0.75) < 0.12 or rr_ < 0.3: c = tone(BRASS, 2.6 + fold + day(X, Y, Z), x, y)   # the seal: a ring round a dot
        return fg(c, z)
    rs.quad((bx - 2.4, 10.0, ZB - 0.25), (bx + 2.4, 10.0, ZB - 0.25), (bx - 2.4, 20.8, ZB - 0.25), banner, cls='prop', cut=True)

# ---------------------------------------------------------------------------------------------------- the side walls and piers
def lancet_open(Z, Y, z0, z1, y0, y1):
    """inside a two-light lancet: the pointed head springs at y1 - 0.9 * width"""
    zc, hw = (z0 + z1) / 2, (z1 - z0) / 2
    if not (z0 < Z < z1 and y0 < Y < y1): return False
    ys = y1 - hw * 1.73
    if Y < ys: return True
    return math.hypot(Z - (zc - hw), Y - ys) < 2 * hw and math.hypot(Z - (zc + hw), Y - ys) < 2 * hw
def side_wall(sg):
    wy = WIN_Y if sg > 0 else WIN_YL
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        if sg < 0 and DOOR_T[0] < Z < DOOR_T[1] and Y < DOOR_T[2]:
            zc = (DOOR_T[0] + DOOR_T[1]) / 2; hw = (DOOR_T[1] - DOOR_T[0]) / 2
            if Y < DOOR_T[2] - hw or math.hypot(Z - zc, Y - (DOOR_T[2] - hw)) < hw: return None
        for (z0, z1) in WIN_R:
            if lancet_open(Z, Y, z0, z1, wy[0], wy[1]): return None
            if lancet_open(Z, Y, z0 - 0.45, z1 + 0.45, wy[0] - 0.4, wy[1] + 0.5):                  # the chamfered surround
                return fg(tone(SAND, 3.6 + 2.4 * day(X, Y, Z) + (0.6 if Z < (z0 + z1) / 2 else -0.3), x, y), z)
        v = 2.2 + 2.6 * day(X, Y, Z) - 0.7 * max(0.0, 1 - Y / 2.0)
        if abs(Y - YS) < 0.5: return fg(tone(SAND, v + 1.2 - (0.9 if Y < YS - 0.2 else 0), x, y), z)
        if sg > 0 and Y < 4.2:                                                                       # oak wainscot
            if Y > 3.9: return fg(tone(OAK, 4.0 + day(X, Y, Z) * 2, x, y), z)
            pz = (Z / 2.2) % 1
            return fg(tone(OAK, 2.2 + (0.7 if 0.12 < pz < 0.88 and 0.6 < Y < 3.4 else 0) - (1.0 if pz < 0.05 else 0) + 1.6 * day(X, Y, Z), x, y), z)
        return fg(ashlar(Z, Y, z, x, y, v, ch=1.0, L=1.9, seed=4 if sg < 0 else 6), z)
    return sh
for sg in (-1, 1):
    rs.quad((sg * WX, 0, 3), (sg * WX, 0, ZB), (sg * WX, YS + 0.5, 3), side_wall(sg), cls='wall', cut=True)
def lancet(sg, z0, z1, y0, y1):
    zc, hw = (z0 + z1) / 2, (z1 - z0) / 2
    bright = 1.0 if sg > 0 else 0.55
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        if not lancet_open(Z, Y, z0 - 0.1, z1 + 0.1, y0 - 0.1, y1 + 0.1): return None
        ps = z * z / (F * WX)
        ys = y1 - hw * 1.73
        if (abs(Z - zc) < 0.12 + ps * 0.5 and Y < ys) or not lancet_open(Z, Y, z0 + 0.12, z1 - 0.12, y0 + 0.12, y1 - 0.12):
            return tone(SAND, 3.0 + 2.0 * day(X, Y, Z), x, y)                                       # the mullion, the frame
        if Y > ys:                                                                                   # Y-tracery: the mullion forks
            if abs(math.hypot(Z - z0, Y - ys) - hw) < 0.1 + ps * 0.4 or abs(math.hypot(Z - z1, Y - ys) - hw) < 0.1 + ps * 0.4:
                return tone(SAND, 3.0 + 2.0 * day(X, Y, Z), x, y)
        q = ((Z - z0) / 0.55 + (Y - y0) / 0.8, (Z - z0) / 0.55 - (Y - y0) / 0.8)              # diamond quarries in lead
        if (q[0] % 1) < 0.08 + ps * 0.4 or (q[1] % 1) < 0.08 + ps * 0.4: return tone(IRON, 1.6, x, y)
        dv = (Y - y0) / (y1 - y0)
        c = tone(DAYG, (1.6 + dv * 2.6 + (wn(3, Z * 0.7, Y * 0.35) - 0.5) * 1.6) * bright + 0.6, x, y)
        k = h32(int(q[0]), int(q[1]), 9 + sg)
        if k % 11 == 0: c = mix(c, STAIN[k % len(STAIN)], 0.35)
        elif k % 7 == 0: c = mix(c, (70, 82, 76), 0.4)                                              # an old, clouded quarry
        return c
    return sh
for sg in (-1, 1):
    wy = WIN_Y if sg > 0 else WIN_YL
    for (z0, z1) in WIN_R:
        rs.quad((sg * (WX + 0.4), wy[0] - 0.3, z0 - 0.3), (sg * (WX + 0.4), wy[0] - 0.3, z1 + 0.3), (sg * (WX + 0.4), wy[1] + 0.3, z0 - 0.3),
                lancet(sg, z0, z1, wy[0], wy[1]), cls='emit', cut=True)
        for zz in (z0, z1):                                                                          # the reveals
            rs.quad((sg * WX, wy[0], zz), (sg * (WX + 0.4), wy[0], zz), (sg * WX, wy[1] - (z1 - z0) * 0.6, zz),
                    lambda x, y, s, t, z, wp: fg(tone(SAND, 2.6 + 2.0 * day(*wp), x, y), z), cls='wall')
        x0s, x1s = sorted((sg * (WX - 0.8), sg * WX))
        rs.box(x0s, x1s, wy[0] - 0.45, wy[0], z0 - 0.4, z1 + 0.4, lambda x, y, s, t, z, wp: fg(tone(SAND, 3.6 + 2 * day(*wp), x, y), z),
               lambda x, y, s, t, z, wp: fg(tone(SAND, 3.4 + 2 * day(*wp), x, y), z), top=lambda x, y, s, t, z, wp: fg(tone(SAND, 4.6 + 2 * day(*wp), x, y), z), cls='prop')
def pier_sh(sg, zp):
    """a clustered pier: three round shafts on each face, dark grooves between them, a moulded base and capital"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        side = abs(abs(X) - (WX - 1.5)) < 0.05
        u = ((Z - (zp - 0.95)) / 1.9) if side else ((abs(X) - (WX - 1.5)) / 1.5)
        f = (u * 3) % 1
        v = 2.4 + 2.6 * day(X, Y, Z) + 1.3 * math.sin(f * math.pi) - (1.2 if f < 0.08 or f > 0.92 else 0)
        v -= 0.7 if side else 0
        v += (wn(1, X * 2 + Z * 2, Y * 0.4) - 0.5) * 0.5
        if Y < 1.5: v += (0.8 if 1.1 < Y < 1.35 else -0.4)                                          # the base mouldings
        if YS - 1.4 < Y < YS: v += 0.5 + (0.9 if (Y * 3) % 1 < 0.4 else -0.5)                       # the capital
        return fg(tone(SAND, v, x, y), z)
    return sh
for sg in (-1, 1):
    for zp in PIERS:
        x0, x1 = sorted((sg * WX, sg * (WX - 1.5)))
        rs.box(x0, x1, 0, YS, zp - 0.95, zp + 0.95, pier_sh(sg, zp), pier_sh(sg, zp), cls='wall')
# iron lanterns on the piers: warm pools on the stone
def wall_lantern(sg, zp, Y=9.6):
    X = sg * (WX - 2.3)
    rs.line3((sg * (WX - 1.5), Y + 1.4, zp), (X, Y + 1.4, zp), lambda x, y, s, t, z, wp: IRON[2], w=0.14)
    rs.box(X - 0.45, X + 0.45, Y, Y + 1.1, zp - 0.45, zp + 0.45,
           lambda x, y, s, t, z, wp: (GLOW[4] if 0.18 < s < 0.82 and 0.15 < t < 0.85 else IRON[1]) if abs(s - 0.5) > 0.07 else IRON[0],
           lambda x, y, s, t, z, wp: GLOW[3] if 0.2 < s < 0.8 and 0.15 < t < 0.85 else IRON[1], cls='emit')
    rs.quad((X - 0.55, Y + 1.1, zp - 0.45), (X + 0.55, Y + 1.1, zp - 0.45), (X, Y + 1.6, zp - 0.45),
            lambda x, y, s, t, z, wp: IRON[2] if t < 1 - abs(s - 0.5) * 2 else None, cls='prop', cut=True)
for sg in (-1, 1):
    for zp in (20.0, 28.0): wall_lantern(sg, zp)

# ---------------------------------------------------------------------------------------------------- the Tribunal's door (left wall, second bay)
def tdoor(x, y, s, t, z, wp):
    X, Y, Z = wp
    zc, hw = (DOOR_T[0] + DOOR_T[1]) / 2, (DOOR_T[1] - DOOR_T[0]) / 2
    if Y > DOOR_T[2] - hw and math.hypot(Z - zc, Y - (DOOR_T[2] - hw)) > hw: return None
    if abs(Z - zc + 0.6) < 0.16 and abs(Y - 4.0) < 0.16: return tone(BRASS, 4.6, x, y)                 # the ring
    if abs(Y - 1.6) < 0.16 or abs(Y - 6.2) < 0.16: return tone(IRON, 2.4 + (1 if Z < zc else 0), x, y)   # strap hinges
    pl = ((Z - DOOR_T[0]) / 0.53) % 1
    v = 2.8 + 1.8 * day(X, Y, Z) + (0.6 if pl < 0.14 else 0) - (1.0 if pl > 0.92 else 0) + (wn(1, Z * 3, Y * 0.6) - 0.5) * 0.6
    return fg(tone(OAK, v, x, y), z)
rs.quad((-WX - 0.5, 0, DOOR_T[0]), (-WX - 0.5, 0, DOOR_T[1]), (-WX - 0.5, DOOR_T[2], DOOR_T[0]), tdoor, cls='prop', cut=True)
for zz in DOOR_T[:2]:                                                                        # the reveal's jambs
    rs.quad((-WX - 0.5, 0, zz), (-WX + 0.02, 0, zz), (-WX - 0.5, DOOR_T[2] - 1.6, zz), lambda x, y, s, t, z, wp: fg(tone(SAND, 3.4 + 2 * day(*wp), x, y), z), cls='wall')
def tdoor_arch(x, y, s, t, z, wp):
    """the door's moulded pointed surround, standing proud of the wall"""
    X, Y, Z = wp
    zc, hw = (DOOR_T[0] + DOOR_T[1]) / 2, (DOOR_T[1] - DOOR_T[0]) / 2
    yb = DOOR_T[2] - hw
    d = math.hypot(Z - zc, Y - yb) if Y > yb else abs(Z - zc)
    if d < hw or d > hw + 0.55: return None
    return fg(tone(SAND, 3.8 + 2.4 * day(X, Y, Z) + (0.8 if d < hw + 0.2 else 0) - (0.6 if Z > zc else 0), x, y), z)
rs.quad((-WX + 0.06, 0, DOOR_T[0] - 0.6), (-WX + 0.06, 0, DOOR_T[1] + 0.6), (-WX + 0.06, DOOR_T[2] + 0.6, DOOR_T[0] - 0.6), tdoor_arch, cls='prop', cut=True)

# ---------------------------------------------------------------------------------------------------- the archive cabinets (left)
CAB = []
for (a_, b_) in ((3.0, 11.05), (12.95, 19.05), (20.95, 27.05), (28.95, 35.05)):
    if a_ < DOOR_T[1] and b_ > DOOR_T[0]:
        CAB += [(a_, DOOR_T[0] - 0.35), (DOOR_T[1] + 0.35, b_)]
    else:
        CAB.append((a_, b_))
CAB_X, CAB_H, DW, DH = -WX + 1.6, 9.6, 0.92, 0.62
def cab_front(z0, z1, seed):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        v0 = 2.4 + 2.2 * day(X, Y, Z)
        if Y > CAB_H - 0.55 or Y < 0.45 or Z < z0 + 0.22 or Z > z1 - 0.22:                  # the carcass, the cornice, the plinth
            return fg(tone(OAK, v0 + (1.2 if Y > CAB_H - 0.25 else 0.4 if Y > CAB_H - 0.55 else -0.6), x, y), z)
        zz = (Z - z0 - 0.22) / DW; yy = (Y - 0.45) / DH
        i, j = math.floor(zz), math.floor(yy); fu, fv = zz - i, yy - j
        k = h32(i, j, seed)
        ps = z * z / (F * WX) / DW
        if fu < 0.05 + ps or fv < 0.07 + ps * 1.2: return fg(tone(OAK, v0 - 1.4, x, y), z)
        if 0.3 < fu < 0.7 and 0.55 < fv < 0.8: return fg(tone(PAPER, 2.0 + day(X, Y, Z) * 2, x, y), z)   # the label
        if 0.38 < fu < 0.62 and 0.24 < fv < 0.38: return tone(BRASS, 3.4 + day(X, Y, Z) * 2, x, y)          # the pull
        return fg(tone(OAK, v0 + (k % 3) * 0.25 + (wn(1, Z * 3, Y * 2) - 0.5) * 0.4, x, y), z)
    return sh
for n_, (z0, z1) in enumerate(CAB):
    rs.box(-WX, CAB_X, 0, CAB_H, z0, z1, lambda x, y, s, t, z, wp: fg(OAK[1], z), lambda x, y, s, t, z, wp: fg(OAK[1], z),
           top=lambda x, y, s, t, z, wp: fg(tone(OAK, 3.4, x, y), z), cls='prop')
    rs.quad((CAB_X + 0.01, 0, z0), (CAB_X + 0.01, 0, z1), (CAB_X + 0.01, CAB_H, z0), cab_front(z0, z1, n_ + 3), cls='prop')
    # drawers pulled out, papers sticking out of them
    for d_ in range(3):
        k = h32(n_, d_, 21)
        if k % 3 == 0: continue
        nz = int((z1 - z0 - 0.44) / DW); ny = int((CAB_H - 1.0) / DH)
        if nz < 1: continue
        i, j = k % nz, (k // 7) % ny
        zd, yd = z0 + 0.22 + i * DW, 0.45 + j * DH
        out = 0.6 + (k % 5) * 0.25
        rs.box(CAB_X, CAB_X + out, yd + 0.04, yd + DH - 0.05, zd + 0.05, zd + DW - 0.05,
               lambda x, y, s, t, z, wp: fg(tone(OAK, 3.4 + 2 * day(*wp) if wp else 3.4, x, y), z),
               lambda x, y, s, t, z, wp: fg(tone(OAK, 2.6 + 2 * day(*wp) if wp else 2.6, x, y), z),
               top=lambda x, y, s, t, z, wp: fg(tone(PAPER, 2.6 + 2 * day(*wp), x, y), z), cls='prop')
        if k % 2:                                                                          # a sheaf hanging out
            rs.quad((CAB_X + out - 0.1, yd + DH - 0.1, zd + 0.15), (CAB_X + out - 0.1, yd + DH - 0.1, zd + DW - 0.2), (CAB_X + out + 0.25, yd - 0.4, zd + 0.15),
                    lambda x, y, s, t, z, wp: fg(tone(PAPER, 3.2 + 2 * day(*wp) - ((t * 6) % 1 < 0.2) * 0.8, x, y), z), cls='prop')
# a rolling ladder on its rail
LZ = 31.0
rs.line3((CAB_X + 0.3, CAB_H - 0.3, LZ - 2.0), (CAB_X + 0.3, CAB_H - 0.3, LZ + 2.6), lambda x, y, s, t, z, wp: tone(BRASS, 3.2, x, y), w=0.12)
for dz in (0.0, 1.1):
    rs.line3((CAB_X + 0.3, CAB_H - 0.2, LZ + dz), (CAB_X + 2.6, 0.0, LZ + dz - 0.3), lambda x, y, s, t, z, wp: fg(tone(OAK, 4.0, x, y), z), w=0.16)
for k in range(1, 9):
    f_ = k / 9.0
    rs.line3((CAB_X + 0.3 + 2.3 * f_, CAB_H - 0.2 - (CAB_H - 0.2) * f_, LZ), (CAB_X + 0.3 + 2.3 * f_, CAB_H - 0.2 - (CAB_H - 0.2) * f_, LZ + 0.8),
             lambda x, y, s, t, z, wp: fg(tone(OAK, 3.4, x, y), z), w=0.1)

# ---------------------------------------------------------------------------------------------------- the right: the public bench
rs.box(WX - 2.6, WX - 0.2, 1.7, 2.05, 12.6, 35.0, lambda x, y, s, t, z, wp: fg(tone(OAK, 3.2 + 1.5 * day(*wp), x, y), z),
       lambda x, y, s, t, z, wp: fg(tone(OAK, 2.6 + 1.5 * day(*wp), x, y), z), top=lambda x, y, s, t, z, wp: fg(tone(OAK, 4.4 + 2 * day(*wp), x, y), z), cls='prop')
for zl in (13.2, 19.0, 24.8, 30.4, 34.4):
    rs.box(WX - 2.4, WX - 0.4, 0, 1.7, zl, zl + 0.4, lambda x, y, s, t, z, wp: fg(tone(OAK, 2.0 + day(*wp), x, y), z),
           lambda x, y, s, t, z, wp: fg(tone(OAK, 1.6 + day(*wp), x, y), z), cls='prop')

# ---------------------------------------------------------------------------------------------------- the council's bench at the back
def platform_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 2.8 + 2.0 * day(X, Y, Z)
    if Y > PLAT - 0.25: return fg(tone(OAK, v + 1.4, x, y), z)
    return fg(ashlar(X, Y, z, x, y, v, ch=0.9, L=2.2, seed=12), z)
rs.box(-17.0, 17.0, 0, PLAT, PLAT_Z, ZB, platform_front, platform_front, top=lambda x, y, s, t, z, wp: fg(tone(OAK, 3.2 + 2.2 * day(*wp) + (0.6 if (wp[0] * 1.1) % 1 < 0.08 else 0), x, y), z), cls='prop')
rs.box(-16.0, 16.0, 0, PLAT / 2, PLAT_Z - 1.0, PLAT_Z, platform_front, platform_front,
       top=lambda x, y, s, t, z, wp: fg(tone(SAND, 4.6 + 2.0 * day(*wp), x, y), z), cls='prop')
# the high-backed chairs behind the table
CHAIRS = (-9.6, -6.4, -3.2, 0.0, 3.2, 6.4, 9.6)
for cxp in CHAIRS:
    top = 12.4 if cxp == 0 else 10.6
    def chair(x, y, s, t, z, wp, cxp=cxp, top=top):
        X, Y, Z = wp
        u = (X - cxp) / 1.25
        if abs(u) > 1: return None
        ap = top - 1.6 + 1.6 * math.sqrt(max(0.0, 1 - u * u)) - abs(u) * 0.4                 # a pointed crest
        if Y > ap: return None
        v = 2.6 + 2.2 * day(X, Y, Z)
        if abs(u) > 0.78 or Y > ap - 0.4: return fg(tone(OAK, v + 0.8 - u * 0.6, x, y), z)      # the frame
        if cxp == 0 and math.hypot(u * 1.25, Y - (top - 2.6)) < 0.7:                          # the brass seal on the councilor's chair
            return tone(BRASS, 3.8 - (Y - top + 2.6) * 1.4, x, y) if math.hypot(u * 1.25, Y - (top - 2.6)) > 0.3 else tone(BRASS, 2.0, x, y)
        lin = math.sin((u * 3.5) * math.pi) * 0.4                                             # linenfold carving
        return fg(tone(OAK, v + lin - 0.2, x, y), z)
    rs.quad((cxp - 1.3, PLAT, 40.2), (cxp + 1.3, PLAT, 40.2), (cxp - 1.3, top + 0.2, 40.2), chair, cls='prop', cut=True)
x0t, x1t, z0t, z1t, topt = TABLE
def table_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 2.6 + 2.2 * day(X, Y, Z)
    if Y > topt - 0.5: return fg(tone(OAK, v + 1.0, x, y), z)
    pan = (X - x0t) / 2.0
    fu = pan % 1
    if fu < 0.07 or Y < PLAT + 0.35: return fg(tone(OAK, v - 0.8, x, y), z)
    arch = (Y - PLAT - 0.35) / (topt - PLAT - 0.85)
    if arch > 0.62 and abs(fu - 0.5) > 0.42 - (arch - 0.62) * 1.1: return fg(tone(OAK, v - 0.3, x, y), z)   # gothic arcading
    return fg(tone(OAK, v + 0.5 - abs(fu - 0.5) * 1.2, x, y), z)
def table_top(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 3.6 + 2.4 * day(X, Y, Z) + (wn(0, X * 0.8, Z * 3) - 0.5) * 0.6
    c = tone(OAK, v, x, y)
    if wn(2, X * 1.4, Z * 2.0) > 0.6: c = mix(c, tone(PAPER, 3.4 + day(X, Y, Z) * 2, x, y), 0.85)            # papers strewn
    return fg(c, z)
rs.box(x0t, x1t, PLAT, topt, z0t, z1t, table_front, table_front, top=table_top, cls='prop')
def ledger(X, Z, w, h, seed):
    rs.box(X - w / 2, X + w / 2, topt, topt + h, Z - 0.5, Z + 0.5,
           lambda x, y, s, t, z, wp: fg(tone(RED if seed % 2 else OAK, 2.4 + 1.4 * day(*wp) + (1.2 if (t * 5) % 1 < 0.2 else 0), x, y), z),
           lambda x, y, s, t, z, wp: fg(tone(PAPER, 2.2 + day(*wp), x, y), z),
           top=lambda x, y, s, t, z, wp: fg(tone(RED if seed % 2 else OAK, 3.4 + 1.4 * day(*wp), x, y), z), cls='prop')
ledger(-7.8, 38.0, 1.6, 0.9, 1); ledger(-7.6, 38.0, 1.4, 0.45, 2); ledger(5.6, 38.2, 1.5, 0.7, 3); ledger(8.6, 37.9, 1.2, 1.3, 4)
rs.box(-1.4, -0.4, topt, topt + 0.5, 37.8, 38.6, lambda x, y, s, t, z, wp: tone(BRASS, 3.0 + 2 * day(*wp), x, y),
       lambda x, y, s, t, z, wp: tone(BRASS, 2.4, x, y), top=lambda x, y, s, t, z, wp: tone(BRASS, 4.0, x, y), cls='prop')     # the great stamp
rs.line3((-0.9, topt + 0.5, 38.2), (-0.9, topt + 1.7, 38.2), lambda x, y, s, t, z, wp: tone(OAK, 3.6, x, y), w=0.28)
rs.disc(-0.9, topt + 1.9, 38.2, 0.32, lambda x, y, s, t, z, wp: tone(OAK, 4.4 - t * 2, x, y))
rs.disc(2.0, topt + 0.3, 37.9, 0.3, lambda x, y, s, t, z, wp: INK if t < 0.2 else tone(IRON, 2.0, x, y))                   # an inkwell
def candle(X, Y0, Z, h=0.9, stick=True):
    if stick:
        rs.line3((X, Y0, Z), (X, Y0 + 0.5, Z), lambda x, y, s, t, z, wp: tone(BRASS, 3.6, x, y), w=0.22)
        Y0 += 0.5
    rs.line3((X, Y0, Z), (X, Y0 + h, Z), lambda x, y, s, t, z, wp: (206, 196, 168) if x % 2 else (178, 166, 138), w=0.2, cls='prop')
    rs.disc(X, Y0 + h + 0.22, Z - 0.05, 0.17, lambda x, y, s, t, z, wp: GLOW[5] if t > -0.1 else GLOW[3], cls='emit')
for cxp in (-10.0, -4.2, 3.4, 10.2): candle(cxp, topt, 38.0)
# tall iron candelabra at the platform's ends
for cxp in (-14.4, 14.4):
    zc = 37.4
    rs.box(cxp - 0.9, cxp + 0.9, PLAT, PLAT + 0.4, zc - 0.9, zc + 0.9, lambda x, y, s, t, z, wp: tone(IRON, 2.4, x, y), lambda x, y, s, t, z, wp: tone(IRON, 1.6, x, y), cls='prop')
    rs.line3((cxp, PLAT + 0.4, zc), (cxp, PLAT + 8.4, zc), lambda x, y, s, t, z, wp: tone(IRON, 2.4 + (1.0 if x % 3 == 0 else 0), x, y), w=0.3)
    rs.line3((cxp - 1.5, PLAT + 8.4, zc), (cxp + 1.5, PLAT + 8.4, zc), lambda x, y, s, t, z, wp: tone(IRON, 2.6, x, y), w=0.2)
    for dx in (-1.5, 0.0, 1.5):
        rs.line3((cxp + dx, PLAT + 8.4, zc), (cxp + dx, PLAT + 8.8, zc), lambda x, y, s, t, z, wp: tone(IRON, 3.0, x, y), w=0.3)
        candle(cxp + dx, PLAT + 8.8, zc, h=1.1 + (0.3 if dx == 0 else 0), stick=False)

# ---------------------------------------------------------------------------------------------------- the public reading dais
dx0, dx1, dz0, dz1, dtop = DAIS
def dais_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 2.6 + 2.0 * day(X, Y, Z)
    if Y > dtop - 0.22: return fg(tone(OAK, v + 1.6, x, y), z)                                  # the oak nosing
    return fg(ashlar(X + Z, Y, z, x, y, v + 0.6, ch=0.55, L=1.4, seed=21), z)
def dais_top(x, y, s, t, z, wp):
    X, Y, Z = wp
    pl = (X / 0.8) % 1
    v = 3.2 + 2.2 * day(X, Y, Z) + (wn(0, X * 0.4, Z * 2.0) - 0.5) * 0.6 - (1.0 if pl < 0.06 else 0)
    v += 0.6 * math.exp(-(X / 1.6) ** 2) * (1 if Z < dz0 + 2.5 else 0)                         # worn where the readers stand
    c = tone(OAK, v, x, y)
    if abs(X + 1.4) < 0.5 and abs(Z - 18.2) < 0.3: c = tone(RED, 1.0, x, y)                     # an ink stain, or worse
    return fg(c, z)
rs.box(dx0, dx1, 0, dtop, dz0, dz1, dais_front, dais_front, top=dais_top, cls='prop')
rs.box(dx0 + 1.0, dx1 - 1.0, 0, dtop / 2, dz0 - 0.8, dz0, dais_front, dais_front, top=dais_top, cls='prop')
# the lectern: a slanted desk on a turned pedestal, off to the right of the dais
LX, LZ = 3.0, 19.6
rs.box(LX - 0.7, LX + 0.7, dtop, dtop + 0.35, LZ - 0.6, LZ + 0.6, lambda x, y, s, t, z, wp: fg(tone(OAK, 3.2 + day(*wp), x, y), z),
       lambda x, y, s, t, z, wp: fg(tone(OAK, 2.4, x, y), z), top=lambda x, y, s, t, z, wp: fg(tone(OAK, 4.0, x, y), z), cls='prop')
rs.line3((LX, dtop + 0.35, LZ), (LX, dtop + 3.4, LZ), lambda x, y, s, t, z, wp: fg(tone(OAK, 3.4 + (1.0 if x % 2 else 0), x, y), z), w=0.42)
rs.quad((LX - 1.15, dtop + 3.3, LZ - 0.7), (LX + 1.15, dtop + 3.3, LZ - 0.7), (LX - 1.15, dtop + 4.3, LZ + 0.5),
        lambda x, y, s, t, z, wp: fg(tone(OAK, 3.6 + day(*wp) * 2, x, y) if (s < 0.06 or s > 0.94 or t < 0.1) else tone(PAPER, 3.4 + day(*wp) * 2 - ((t * 7) % 1 < 0.25) * 0.8, x, y), z), cls='prop')

# ---------------------------------------------------------------------------------------------------- the iron candle-rings on chains
for cxp, zc, yc in ((-8.6, 27.0, 16.0), (8.6, 27.0, 16.0)):
    rs.line3((cxp, yc + 0.3, zc), (cxp, vault_y(cxp) - 0.2, zc), lambda x, y, s, t, z, wp: IRON[1] if (x + y) % 2 else IRON[3], w=0.12)
    for k in range(3):
        a = k * 2 * math.pi / 3
        rs.line3((cxp, yc + 3.0, zc), (cxp + math.cos(a) * 2.2, yc, zc + math.sin(a) * 2.2), lambda x, y, s, t, z, wp: IRON[2], w=0.06)
    n = 28
    for k in range(n):
        a0, a1 = k * 2 * math.pi / n, (k + 1) * 2 * math.pi / n
        rs.line3((cxp + math.cos(a0) * 2.2, yc, zc + math.sin(a0) * 2.2), (cxp + math.cos(a1) * 2.2, yc, zc + math.sin(a1) * 2.2),
                 lambda x, y, s, t, z, wp: tone(IRON, 2.6 + (1.0 if (wp and wp[2] < zc) else 0), x, y), w=0.22)
    for k in range(6):
        a = k * 2 * math.pi / 6 + 0.3
        candle(cxp + math.cos(a) * 2.2, yc + 0.1, zc + math.sin(a) * 2.2, h=0.8, stick=False)

# ---------------------------------------------------------------------------------------------------- the siege's leftovers: papers, a toppled chair
for k in range(26):
    fx_, fzz = -18 + (h32(k, 81) % 3600) / 100.0, 11.0 + (h32(k, 82) % 2200) / 100.0
    if dx0 - 0.5 < fx_ < dx1 + 0.5 and dz0 - 1.5 < fzz < dz1 + 0.5: continue
    sk = (h32(k, 83) % 60 - 30) / 100.0
    rs.quad((fx_ - 0.35, 0.03, fzz - 0.25 + sk), (fx_ + 0.35, 0.03, fzz - 0.25 - sk), (fx_ - 0.35, 0.03, fzz + 0.25 + sk),
            lambda x, y, s, t, z, wp: fg(tone(PAPER, 2.8 + 2.0 * day(*wp) - ((t * 5) % 1 < 0.22 and 0.2 < s < 0.8) * 1.0, x, y), z), cls='ground')
# a chair knocked over in the aisle on the right
def chair_side(x, y, s, t, z, wp): return fg(tone(OAK, 2.6 + 1.6 * day(*wp), x, y), z)
rs.box(11.0, 13.6, 0.0, 0.35, 23.0, 24.4, chair_side, chair_side, top=chair_side, cls='prop')
rs.box(10.4, 11.0, 0.0, 2.4, 23.1, 24.3, chair_side, chair_side, top=chair_side, cls='prop')
rs.quad((13.6, 0.35, 23.0), (16.2, 1.2, 23.0), (13.6, 0.35, 24.4), chair_side, cls='prop')

img = rs.render(INK, fog=fog, mirror=lambda x, y, wp: 0.0 if abs(wp[0]) < RUN and wp[2] < PLAT_Z else 0.22 + 0.12 * (wn(2, wp[0] * 0.4, wp[2] * 0.4) > 0.5),
                light_gain=1.15, grime_gain=0.85, bloom=0.5, stain_gain=0.55, damp_gain=0.25)
img.save(os.path.join(OUT, 'townhall_interior.png'))

def P(X, Y, Z): return (round(proj(X, Y, Z)[0]), round(proj(X, Y, Z)[1]))
zc, hw = (DOOR_T[0] + DOOR_T[1]) / 2, (DOOR_T[1] - DOOR_T[0]) / 2
tdoor_poly = [P(-WX, 0, DOOR_T[0]), P(-WX, 0, DOOR_T[1]), P(-WX, DOOR_T[2] - hw, DOOR_T[1])] + \
             [P(-WX, DOOR_T[2] - hw + hw * math.sin(math.pi * k / 8), zc + hw * math.cos(math.pi * k / 8)) for k in range(1, 8)] + \
             [P(-WX, DOOR_T[2] - hw, DOOR_T[0])]
FIXED = {
    'poet_feet_y_z17_6': P(0, dtop, 17.6)[1], 'dais_front_y': P(0, 0, dz0 - 0.8)[1], 'dais_x': (P(dx0, 0, dz0)[0], P(dx1, 0, dz0)[0]),
    'tribunal_door_poly': tdoor_poly,
    'cabinet_near': [P(CAB_X, 0, 13.0), P(CAB_X, CAB_H, 19.0)],
    'rose_centre': P(*ROSE[:2], ZB), 'rose_r_px': round(ROSE[2] * F / ZB),
    'table_x': (P(x0t, topt, z0t)[0], P(x1t, topt, z0t)[0]),
}
json.dump(FIXED, open(os.path.join(OUT, 'fixed_int.json'), 'w'), indent=1)
print('done townhall_interior', FIXED)
