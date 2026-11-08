"""The Ink Tribunal's chamber -- the hidden reading room beneath the Townhall (PithReclaimersRoomScene), 1067x600, the
shared camera (raster3d.py). After the old art (ReclaimersRoom.png): a vaulted archive cellar, towering card
catalogues and bookcases, specimen vitrines, a red curtain, green-shaded lamps against warm lanterns, and in the middle
of a cleared floor a glass orb on a pedestal (the Tribunal's cache, the scene's stash hotspot).

  vault   a brick barrel vault on a stone rib, brass pneumatic-tube post running along the crown (the same post as in
          the Bureau's Applications office) down into the registry station; two pendant lamps with green glass shades
  back    five bays between stone pilasters:
            left outer   a bookcase of ledgers, before it a vitrine: a pickled specimen in a jar (an "entry")
            left inner   two tiers of oak card-catalogue drawers, archive boxes on top, a rolling library ladder
            centre       the registry station: pigeonholes of rolled forms and tube canisters, a lit niche holding the
                         Tribunal's ink in a great glass ampulla, the dispatch dial; above it the Tribunal's seal
                         (a pen nib on oxblood enamel in a ticked brass ring)
            right inner  a vitrine with a shard of the Egg Cathedral's shell (an index card tied to it), ledgers above
            right outer  an archway deeper into the stacks, an oxblood velvet curtain drawn aside and tied back
  sides   left: a wall bookcase with a ladder on its rail; right: the framed charter with its wax seal over a bank of
          the Bureau's steel filing cabinets
  floor   worn flagstones; around the pedestal the court circle: rings of curved stones, brass inlay, a polished
          inkstone disc that mirrors the room; a writing desk at the left (banker's lamp, ledger, stamps) with an
          inkpot knocked over on the floor, a docket trolley at the right
The orb itself is composited after the render (a ball lens: the room behind it, inverted).
Fixed points (canvas): the pedestal + orb centred on x 533, y ~368..467 (the stash hotspot); the walk line y 534;
the exit is the bottom edge (stairs back up to the Townhall, behind the camera).

    python3 tribunal_bg.py <outdir>   ->  tribunal.png = assets/images/backgrounds/ReclaimersRoom.png
"""
import sys, math
from PIL import Image
from common import h32
from shedkit import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = Raster()
WX, ZB, SPR, CROWN = 40.0, 36.0, 21.0, 33.0                  # side walls, back wall, vault springing + crown
FOGI = (17, 14, 10)
def fog(z): return max(0.0, min(0.34, (z - 17) / 62.0))
def fg(c, z): return mix(c, FOGI, fog(z))

ASH   = ramp('#0d0b08 #14110d #1b1712 #231e17 #2c251c #362d22 #413628 #4d402f #5a4b37')   # the cellar's ashlar
BRICK = ramp('#100b08 #18100c #211611 #2b1d16 #36251b #422d21 #4f3628')                # the vault's brick
FLAG  = ramp('#0b0a08 #12100c #191611 #211d16 #2a251c #332d22 #3e3629 #4a4131 #574c3a')  # floor flags
INKST = ramp('#060607 #0b0b0d #111114 #18181c #212126 #2c2b31 #3a383f')                 # the polished inkstone disc
OAK   = ramp('#0f0a06 #170f09 #20150c #2a1c10 #352315 #412b1a #4e3420 #5c3d26 #6b482d #7b5636')
BRASS = ramp('#241809 #3a2810 #553b17 #74531f #93702c #b38f40 #d0ae5c #ead08a')
GREEN = ramp('#08180f #0e2618 #163a24 #1f5232 #2b6c42 #3f8a56 #62b077 #9cd8a4 #d2f4d0')  # lamp-shade glass
LAMP  = ramp('#6e4a1c #95682a #bb8a3a #d9aa52 #efc874 #fbe4a6 #fff4d8')
OXB   = ramp('#140505 #210908 #310e0b #431410 #561a15 #6a221b #7f2c22 #94382b')          # oxblood velvet
PARCH = ramp('#2e281e #443b2c #5c513c #766a4f #918463 #ab9e7a #c4b892 #d8cfae')
INKC  = ramp('#04050a #080a14 #0e1120 #161a30 #212643 #2e3458 #47427a #7a72b0')          # the Tribunal's ink
FLUID = ramp('#141e0a #1f2e0e #2e4414 #405c1a #567822 #72962e #96b844')                 # specimen fluid
PALE  = ramp('#3a3426 #534a36 #6e6448 #8a7f5c #a69a72 #c0b58a')                          # the pickled specimen
SHELL = ramp('#3a362a #565040 #746c58 #918870 #ada388 #c7bea0 #ddd5ba')                   # the cathedral eggshell
SPINES = [ramp('#170b06 #24120a #34190e #462314 #5a2f1b #6e3c23'),                      # brown calf
          ramp('#160606 #240a09 #350f0d #481612 #5c1e18 #70281f'),                      # oxblood
          ramp('#1c1408 #2c200d #3e2e13 #523e1a #674f22 #7c612c'),                      # ochre buckram
          ramp('#0a120c #101c13 #17281b #203624 #2a452e #365538'),                      # bottle green
          ramp('#090b12 #0f121d #161a2a #1f2439 #292f49 #353c5a'),                      # ink blue
          ramp('#0d0c0b #161412 #201d1a #2b2723 #37322d #443e37'),                      # black cloth
          ramp('#231a10 #362818 #4b3822 #61492d #785b39 #8f6e46'),                      # tan vellum
          ramp('#170b06 #24120a #34190e #462314 #5a2f1b #6e3c23')]
BOXC = [OCHRE, ramp('#1e1a14 #2c261d #3b3428 #4b4334 #5c5341'), ramp('#24170d #362315 #4a311d #5f4027')]
STEELB = ramp('#111614 #182019 #20291f #283227 #313c2f #3b4738 #475342')                # the Bureau's steel, olive-grey
STEELC = [STEELB, ramp('#141716 #1c201e #252a27 #2e3431 #383f3b #434a45')]

# ---------------------------------------------------------------------------------------------------- light
LAMPS = []                                                       # for the shaders: (X, Y, Z, power, kind)
LIGHTS = []                                                      # for paintpass: (X, Y, Z, rgb, power, radius)
WARMC, GREENC = (1.0, 0.72, 0.40), (0.50, 0.95, 0.58)
def add_light(X, Y, Z, p, kind='point', col=WARMC, pp=None, rad=None):
    LAMPS.append((X, Y, Z, p, kind))
    if pp: LIGHTS.append((X, Y, Z, col, pp, rad))
def lit(X, Y, Z):
    """the lamps' light at a world point (in ramp steps); 'down' lamps are shaded above, the stairwell behind the
    camera spills a little warmth on the near floor"""
    v = 0.35                                                           # the cellar's ambient (lamps everywhere, warm stone)
    for (lx, ly, lz, p, kind) in LAMPS:
        dx, dy, dz = X - lx, Y - ly, Z - lz
        d2 = dx * dx + dy * dy + dz * dz
        if kind == 'down':
            c = -dy / math.sqrt(d2 + 1e-6)
            v += p * (0.06 + max(0.0, c) ** 1.6) / (d2 + 4.0)
        else:
            v += p / (d2 + 2.5)
    v += 0.5 * math.exp(-max(0.0, Z - 6.0) / 6.0) * (1.0 if Y < 1 else 0.5)
    return min(3.2, v)

def ri_(r, v, x, y): return tone(r, v, x, y)
def surf(r, v0, k=0.5, seed=0, lk=1.0):
    """a plain lit surface with a little world-space mottling"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp if wp else (0.0, 0.0, z)
        v = v0 + lk * lit(X, Y, Z) + (wn(seed % 4, X * 1.3 + Z * 1.1, Y * 1.3) - 0.5) * k
        return fg(tone(r, v, x, y), z)
    return sh
def oak(v0, k=0.6, lk=1.0, along='x'):
    """oak with a vertical grain (streaky noise stretched along Y)"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp if wp else (0.0, 0.0, z)
        u = X if along == 'x' else Z
        v = v0 + lk * lit(X, Y, Z) + (wn(1, u * 5.0, Y * 0.5) - 0.5) * k + (wn(2, u * 1.2, Y * 0.2) - 0.5) * 0.4
        return fg(tone(OAK, v, x, y), z)
    return sh
def flat(c):
    return lambda x, y, s, t, z, wp: fg(c, z)

# ---------------------------------------------------------------------------------------------------- the shell
def vault_y(X):
    return SPR + (CROWN - SPR) * math.sqrt(max(0.0, 1 - (X / WX) ** 2))

CC = (0.0, 21.0)                                                    # the court circle's centre: the pedestal
R_IN, R_OUT = 3.4, 9.6
def floor_sh(x, y, s, t, z, wp):
    X, _, Z = wp
    pa, pd = z / F, z * z / (F * CAMH)                                 # a pixel on the floor: across, in depth
    dx, dz = X - CC[0], Z - CC[1]
    r = math.hypot(dx, dz)
    L = lit(X, 0.0, Z)
    vig = -0.022 * abs(X) - 0.5 * max(0.0, 1 - (Z - 9.0) / 5.0)        # darker towards the walls and the near edge
    dust = (wn(0, X * 0.9, Z * 0.9) - 0.5) * 0.55 + (wn(1, X * 3.0, Z * 3.0) - 0.5) * 0.25
    worn = max(0.0, 1 - abs(r - (R_OUT - 1.4)) / 2.2) * 0.3            # the ring trodden smooth round the pedestal
    if r < R_IN:                                                       # the polished inkstone disc
        if r > R_IN - 0.22: return fg(tone(BRASS, min(3.6, 1.6 + L * 0.6), x, y), z)
        v = 1.6 + L * 0.7 + (wn(3, X * 0.8, Z * 0.8) - 0.5) * 0.5
        return fg(tone(INKST, v, x, y), z)
    if r < R_OUT + 0.22:
        a = math.atan2(dz, dx)
        brass_v = min(3.4, 1.2 + L * 0.55 + dust * 1.2)
        gone = wn(2, X * 1.6 + 40, Z * 1.6) > 0.66                    # inlay worn out / prised out in places
        if r > R_OUT or R_IN < r < R_IN + 0.16:
            if gone: return fg(tone(FLAG, 1.4 + L * 0.6, x, y), z)
            return fg(tone(BRASS, brass_v, x, y), z)
        if abs(((a / (2 * math.pi) * 8) % 1) - 0.5) * 2 * math.pi / 8 * r > math.pi / 8 * r - max(0.05, pa * 0.6) and not gone:
            return fg(tone(BRASS, brass_v - 0.3, x, y), z)                  # eight radial lines (a compass)
        ring = math.floor((r - R_IN) / 1.25)
        nseg = 10 + ring * 5
        fa = (a / (2 * math.pi) * nseg + ring * 0.37) % 1
        fr = ((r - R_IN) / 1.25) % 1
        seg = math.floor(a / (2 * math.pi) * nseg + ring * 0.37)
        v = 2.7 + L + vig + dust + worn + (h32(ring, seg, 4) % 5 - 2) * 0.17
        if ring % 2: v -= 0.25                                         # alternate rings of a darker stone
        if fr * 1.25 < max(pd, pa) * 0.9 + 0.03 or fa * 2 * math.pi * r / nseg < pa * 1.1 + 0.03: v -= 1.2
        return fg(tone(FLAG, v, x, y), z)
    # the flags: staggered rows, per-slab tone, joints, a few cracked or sunk slabs
    row = math.floor(Z / 1.9); off = (h32(row, 3) % 10) * 0.23
    col = math.floor((X + off) / 2.3)
    fx, fz = (X + off) / 2.3 - col, Z / 1.9 - row
    v = 2.6 + L + vig + dust + (h32(col, row, 5) % 5 - 2) * 0.2
    if h32(col, row, 6) % 9 == 0: v -= 0.45                            # a darker, sunk slab
    if fx * 2.3 < pa * 1.1 + 0.03 or fz * 1.9 < pd * 1.1 + 0.03: v -= 1.3
    elif fz * 1.9 < pd * 2.4 + 0.06 and h32(col, row, 8) % 3 == 0: v -= 0.5   # a chipped, lower edge
    if h32(col, row, 7) % 11 == 0 and abs((fx - 0.3) - (fz - 0.5) * 0.6) < pa * 0.5 / 2.3 + 0.01: v -= 1.0   # a crack
    if abs(X) < 3.2 and Z < CC[1] - R_OUT: v += 0.35 * (1 - abs(X) / 3.2)  # trodden from the stairs to the circle
    return fg(tone(FLAG, v, x, y), z)
rs.quad((-WX, 0, 3), (WX, 0, 3), (-WX, 0, ZB), floor_sh, cls='ground')

def ashlar(u, Y, z, L, v0=2.4, along=1.0):
    """coursed ashlar blocks in world units: merged lengths per course, sunk joints, per-block tone, a damp foot"""
    ch = 1.15
    row = math.floor(Y / ch)
    ln = 2.1 + (h32(row, 11) % 4) * 0.4
    off = (h32(row, 12) % 10) / 10 * ln
    col = math.floor((u + off) / ln)
    fu, fv = ((u + off) / ln) % 1, (Y / ch) % 1
    pz = z / F * along
    v = v0 + L + (h32(col, row, 13) % 5 - 2) * 0.2 + (wn(0, u * 0.7, Y * 0.7) - 0.5) * 0.55 + (wn(3, u * 2.4, Y * 2.4) - 0.5) * 0.25
    if fv * ch < pz * 1.1 + 0.03 or fu * ln < pz * 1.1 + 0.03: v -= 1.25
    elif fv > 1 - (pz * 1.2 + 0.05) / ch: v += 0.35                    # the lit arris under each joint
    q = h32(col, row, 14)
    if q % 17 == 0: v += 0.5                                           # a newer, paler block
    elif q % 13 == 0: v -= 0.5                                         # a damp one
    v -= 0.9 * max(0.0, 1 - Y / 2.2)                                   # damp foot
    v -= max(0.0, Y - 11.0) * 0.06                                     # the lamps' light dies away up the wall
    return v
SOOT = []                                                              # lamps that blacken the stone above them
def soot(X, Y, Z):
    k = 0.0
    for (lx, ly, lz) in SOOT:
        h = Y - ly
        if 0 < h < 9 and abs(Z - lz) < 3.0:
            k += math.exp(-((X - lx) / (0.6 + 0.16 * h)) ** 2) * (1 - h / 9)
    return min(1.4, k * 1.3)
def salt(u, Y):
    """white efflorescence creeping up the damp foot of the walls"""
    if Y > 2.6: return 0.0
    m = wn(2, u * 1.4 + 17, Y * 2.2) - 0.55 - Y * 0.08
    return 0.9 if m > 0.0 else 0.0

def back_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    vy = vault_y(X)
    if Y > vy: return None
    if 30.2 < X < 37.6 and (Y < 7.6 or math.hypot(X - 33.9, Y - 7.6) < 3.7): return None   # the archway into the stacks
    L = lit(X, Y, Z)
    if vy - Y < 1.3:                                                   # the voussoirs of the lunette's arch
        a = math.atan2(Y - SPR, X / WX * (CROWN - SPR))
        k = math.floor(a / math.pi * 46)
        v = 2.6 + L + (h32(k, 21) % 3) * 0.2
        if ((a / math.pi * 46) % 1) < 0.12 or vy - Y < 0.12 or abs(vy - Y - 1.3) < 0.1: v -= 1.1
        return fg(tone(ASH, v, x, y), z)
    if 29.6 < X < 38.2 and (Y < 8.0 or math.hypot(X - 33.9, Y - 7.6) < 4.3):   # the archway's dressed surround
        return fg(tone(ASH, 3.0 + L - (0.9 if (math.atan2(Y - 7.6, X - 33.9) / math.pi * 9) % 1 < 0.14 and Y > 7.6 else 0), x, y), z)
    v = ashlar(X, Y, z, L) - soot(X, Y, Z)
    c = tone(ASH, v, x, y)
    if salt(X, Y): c = mix(c, (96, 92, 80), 0.35)
    return fg(c, z)
rs.quad((-WX, 0, ZB), (WX, 0, ZB), (-WX, CROWN + 0.5, ZB), back_sh, cls='wall', cut=True)

def side_sh(sign):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        L = lit(X, Y, Z)
        c = tone(ASH, ashlar(Z, Y, z, L, 2.2, along=z / max(1.0, abs(X))) - soot(X, Y, Z), x, y)
        if salt(Z, Y): c = mix(c, (96, 92, 80), 0.35)
        return fg(c, z)
    return sh
rs.quad((-WX, 0, 14), (-WX, 0, ZB), (-WX, SPR, 14), side_sh(-1), cls='wall')
rs.quad((WX, 0, 14), (WX, 0, ZB), (WX, SPR, 14), side_sh(1), cls='wall')

# the brick barrel vault (thin strips along z, smooth-shaded from the arch)
VAULT = rs.obj()
def vault_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    th = math.acos(max(-1.0, min(1.0, -X / WX)))
    u = th * (WX + CROWN - SPR) * 0.5                                  # arc length (roughly)
    row = math.floor(u / 0.62); off = (row % 2) * 0.7
    fu, fz = (u / 0.62) % 1, ((Z + off) / 1.4) % 1
    pz = z / F * 1.4
    L = lit(X, Y, Z)
    v = 1.3 + L * 0.8 + (h32(row, math.floor((Z + off) / 1.4), 31) % 4 - 1.5) * 0.18 + (wn(0, u * 0.6, Z * 0.6) - 0.5) * 0.6
    v += 0.6 * max(0.0, 1 - (Y - SPR) / 3.0)                          # the haunches catch the lamps' light
    if fu * 0.62 < pz * 0.9 + 0.02 or fz * 1.4 < pz * 0.9 + 0.02: v -= 0.8
    if wn(2, u * 0.25, Z * 0.25) > 0.62: v -= 0.5                      # old soot
    return fg(tone(BRICK, v, x, y), z)
N_V = 48
for i in range(N_V):
    a0, a1 = math.pi * i / N_V, math.pi * (i + 1) / N_V
    X0, X1 = -WX * math.cos(a0), -WX * math.cos(a1)
    Y0, Y1 = SPR + (CROWN - SPR) * math.sin(a0), SPR + (CROWN - SPR) * math.sin(a1)
    rs.quad((X0, Y0, 12), (X1, Y1, 12), (X0, Y0, ZB + 0.05), vault_sh, obj=VAULT, cls='ceil')

# a stone rib across the vault on piers against the side walls
def rib(zr, w=1.5, d=1.2):
    obj = rs.obj()
    def face(x, y, s, t, z, wp):
        X, Y, Z = wp
        a = math.atan2(Y - SPR, X / WX * (CROWN - SPR)) if Y > SPR else 0
        k = math.floor(a / math.pi * 30)
        v = 2.5 + lit(X, Y, Z) * 0.9 + (h32(k, 41) % 3) * 0.2 + (wn(1, X * 1.4, Y * 1.4) - 0.5) * 0.5
        if (a / math.pi * 30) % 1 < 0.1 and Y > SPR: v -= 1.0
        return fg(tone(ASH, v, x, y), z)
    def under(x, y, s, t, z, wp):
        X, Y, Z = wp
        return fg(tone(ASH, 1.6 + lit(X, Y, Z) * 0.9 + (wn(1, X * 1.4, Z * 1.4) - 0.5) * 0.5, x, y), z)
    n = 40
    for i in range(n):
        a0, a1 = math.pi * i / n, math.pi * (i + 1) / n
        p0 = (-WX * math.cos(a0), SPR + (CROWN - SPR) * math.sin(a0)); p1 = (-WX * math.cos(a1), SPR + (CROWN - SPR) * math.sin(a1))
        q0 = (-(WX - d) * math.cos(a0), SPR + (CROWN - SPR - d) * math.sin(a0)); q1 = (-(WX - d) * math.cos(a1), SPR + (CROWN - SPR - d) * math.sin(a1))
        rs.quad((q0[0], q0[1], zr), (q1[0], q1[1], zr), (p0[0], p0[1], zr), face, obj=obj, cls='wall')
        rs.quad((q0[0], q0[1], zr), (q1[0], q1[1], zr), (q0[0], q0[1], zr + w), under, obj=obj, cls='wall')
    for sx in (-1, 1):                                                 # the piers, a capital at the springing
        x0, x1 = (-WX, -WX + d) if sx < 0 else (WX - d, WX)
        rs.box(x0, x1, 0, SPR, zr, zr + w, face, under, cls='wall')
        c0, c1 = (x0, x1 + 0.4) if sx < 0 else (x0 - 0.4, x1)
        rs.box(c0, c1, SPR - 0.8, SPR, zr - 0.3, zr + w + 0.3, face, under, bottom=under, cls='wall')
        rs.box(c0, c1, 0, 1.2, zr - 0.3, zr + w + 0.3, face, under, top=under, cls='wall')
rib(23.0, w=1.5, d=1.3)

# pilasters dividing the back wall into five bays
def pil_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    return fg(tone(ASH, ashlar(X * 0.6 + Z, Y, z, lit(X, Y, Z), 2.7) - soot(X, Y, Z), x, y), z)
for px_ in (-26.0, -10.0, 10.0, 26.0):
    rs.box(px_ - 1.3, px_ + 1.3, 0, SPR - 0.9, ZB - 1.2, ZB, pil_sh, pil_sh, cls='wall')
    rs.box(px_ - 1.6, px_ + 1.6, 0, 1.0, ZB - 1.5, ZB, pil_sh, pil_sh, top=surf(ASH, 3.4), cls='wall')
    rs.box(px_ - 1.7, px_ + 1.7, SPR - 0.9, SPR, ZB - 1.6, ZB, surf(ASH, 3.2), surf(ASH, 2.4), bottom=surf(ASH, 1.4), cls='wall')

# ---------------------------------------------------------------------------------------------------- books & drawers
def book_row(u0, u1, seed, hmin, hmax):
    out, u, k = [], u0 + 0.04, 0
    while u < u1 - 0.15:
        q = h32(seed, k, 1)
        if q % 14 == 0: u += 0.3 + (q % 5) * 0.08; k += 1; continue                    # a gap
        if q % 15 == 1:                                                                  # a stack lying flat
            w = min(u1 - u, 1.0 + (q % 4) * 0.12)
            out.append((u, u + w, 'stack', 0.3 * (2 + q % 3), q)); u += w + 0.04; k += 1; continue
        w = 0.22 + (q % 7) * 0.05
        hh = hmin + ((q >> 5) % 100) / 100 * (hmax - hmin)
        out.append((u, min(u1, u + w), 'book', hh, q)); u += w + 0.012; k += 1
    return out
def spines(books, y0, along='x', lk=1.0):
    """the spines of one shelf row: rounded, gilt bands on the calf ones, paper labels, flat stacks"""
    tbl = {}
    for b in books:
        for i in range(int(b[0] * 20), int(b[1] * 20) + 1): tbl.setdefault(i, []).append(b)
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = X if along == 'x' else Z
        hy = Y - y0
        for b in tbl.get(int(u * 20), ()):
            if b[0] <= u < b[1]:
                break
        else:
            return None
        u0, u1, kind, hh, q = b
        if hy > hh: return None
        a = (u - u0) / (u1 - u0)
        L = lit(X, Y, Z) * lk
        if kind == 'stack':
            band_ = math.floor(hy / 0.3); fb = (hy / 0.3) % 1
            r_ = SPINES[h32(q, band_) % len(SPINES)]
            v = 2.2 + L + 0.8 * (1 - abs(2 * fb - 1) ** 2) - 0.4
            if fb < 0.12: return fg(tone(PARCH, 1.4 + L, x, y), z)
            return fg(tone(r_, v, x, y), z)
        r_ = SPINES[q % len(SPINES)]
        v = 1.6 + L + 1.1 * (1 - abs(2 * a - 1) ** 2) + (wn(1, u * 7, Y * 3) - 0.5) * 0.4
        if a < 0.08 or a > 0.94: v -= 1.0
        if q % 3 == 0 and (abs(hh - hy - 0.25) < 0.05 or abs(hy - 0.22) < 0.05 or abs(hh - hy - 0.42) < 0.03):
            return fg(tone(BRASS, 2.2 + L * 0.8, x, y), z)                               # gilt bands
        if q % 4 == 1 and 0.22 < a < 0.78 and abs(hy - hh * 0.62) < 0.14:
            return fg(tone(PARCH, 2.6 + L * 0.8, x, y), z)                               # a paper label
        return fg(tone(r_, v, x, y), z)
    return sh

def drawers(w, h, cols, rows, v0=2.6, seed=0, lk=1.0, along='x', cards=True, steel=False):
    """a face of drawers: dark gaps, a bevelled lit top edge, a brass label holder with its card and a pull"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        fu, fv = s * cols, t * rows
        i, j = min(cols - 1, int(fu)), min(rows - 1, int(fv))
        a, b = fu - i, fv - j
        cw, ch_ = w / cols, h / rows
        pz = z / F if along == 'x' else z * z / (F * max(1.0, abs(X)))
        L = lit(X, Y, Z) * lk
        if a * cw < pz * 1.1 + 0.03 or b * ch_ < pz * 1.1 + 0.03:
            return fg(tone(OAK if not steel else SLATE, 0.6 + L * 0.5, x, y), z)
        q = h32(i, j, seed)
        if abs(a - 0.5) < 0.2 and abs(b - 0.66) < 0.13:
            if abs(a - 0.5) > 0.16 or abs(b - 0.66) > 0.09: return fg(tone(BRASS, 2.6 + L, x, y), z)
            if cards and q % 7: return fg(tone(PARCH, 3.4 + L - (q % 3) * 0.3, x, y), z)
            return fg(tone(OAK, 0.8 + L * 0.5, x, y), z)
        if abs(a - 0.5) < 0.09 and abs(b - 0.34) < 0.08: return fg(tone(BRASS, 3.4 + L, x, y), z)
        r_ = (STEELC[q % 2] if steel else OAK)
        v = v0 + L + (q % 3) * 0.2 + (wn(1, X * 4 + Z * 4, Y * 0.6) - 0.5) * 0.4
        if b > 1 - (pz * 1.2 + 0.03) / ch_: v += 0.6
        if b < (pz * 1.2 + 0.03) / ch_ + 0.08: v -= 0.4
        return fg(tone(r_, v, x, y), z)
    return sh

def bookcase(x0, x1, y0, y1, zf, depth, shelf=2.25, seed=0):
    """a bookcase against the back wall: uprights, shelves, a cornice, rows of books (recessed), a dark back"""
    rs.quad((x0, y0, zf + depth - 0.05), (x1, y0, zf + depth - 0.05), (x0, y1, zf + depth - 0.05), oak(0.6, lk=0.6), cls='prop')
    ys = y0 + 0.5
    k = 0
    while ys + shelf * 0.6 < y1 - 0.3:
        rs.quad((x0 + 0.35, ys, zf + 0.45), (x1 - 0.35, ys, zf + 0.45), (x0 + 0.35, ys + shelf - 0.25, zf + 0.45),
                spines(book_row(x0 + 0.35, x1 - 0.35, seed * 31 + k, shelf * 0.5, shelf * 0.86), ys), cls='prop', cut=True)
        rs.box(x0, x1, ys - 0.2, ys, zf, zf + depth, oak(2.8), oak(2.2), top=oak(3.4), bottom=oak(1.2))
        ys += shelf; k += 1
    rs.box(x0, x1, 0, y0 + 0.5, zf - 0.05, zf + depth, oak(1.8), oak(1.4), top=oak(3.0))               # the plinth
    for ux in (x0, x1 - 0.35):
        rs.box(ux, ux + 0.35, 0, y1, zf - 0.08, zf + depth, oak(2.4), oak(1.8), top=oak(3.0))
    rs.box(x0 - 0.2, x1 + 0.2, y1, y1 + 0.45, zf - 0.3, zf + depth, oak(3.0), oak(2.2), top=oak(3.6), bottom=oak(1.0))

def archive_boxes(x0, x1, y0, z0, z1, seed, layers=3):
    """stacked archive boxes (lids, pull holes, labels), some bundles of files tied with string"""
    for L_ in range(layers):
        u = x0 + (h32(seed, L_) % 3) * 0.2
        yb = y0 + L_ * 1.05
        while u < x1 - 0.8:
            q = h32(seed, L_, int(u * 10))
            w = 1.3 + (q % 4) * 0.25
            if u + w > x1: break
            if q % 6 == 0 and L_ > 0: u += w + 0.1; continue
            r_ = BOXC[q % len(BOXC)]
            def front(x, y, s, t, z, wp, r_=r_, q=q):
                X, Y, Z = wp; Lv = lit(X, Y, Z)
                if t > 0.82: return fg(tone(r_, 3.2 + Lv, x, y), z)                     # the lid's lip
                if abs(s - 0.5) < 0.12 and abs(t - 0.55) < 0.08: return fg(tone(r_, 0.6, x, y), z)   # pull hole
                if 0.16 < s < 0.46 and abs(t - 0.3) < 0.08 and q % 3: return fg(tone(PARCH, 3.0 + Lv, x, y), z)
                return fg(tone(r_, 2.2 + Lv + (wn(1, X * 3, Y * 3) - 0.5) * 0.5, x, y), z)
            rs.box(u, u + w, yb, yb + 1.0, z0, z1, front, surf(r_, 1.6), top=surf(r_, 3.0))
            if q % 3 == 0 and q % 2:                                                      # string round a bundle
                rs.line3((u + w * 0.62, yb, z0 - 0.02), (u + w * 0.62, yb + 1.0, z0 - 0.02), flat(PARCH[2]), w=0.05)
            u += w + 0.06

# ---------------------------------------------------------------------------------------------------- lamps
def lantern(X, Y, Z, s_=1.0):
    """a caged oil lantern standing on a surface: glowing glass, brass frame, cage bars, a cap and a ring"""
    w2, hh = 0.42 * s_, 1.1 * s_
    def glass(x, y, s, t, z, wp):
        if abs(s - 0.5) < 0.05 or s < 0.08 or s > 0.92: return BRASS[1]
        if (s * 4) % 1 < 0.12: return BRASS[2]
        return LAMP[5] if 0.3 < t < 0.7 and 0.25 < s < 0.75 else LAMP[3]
    rs.box(X - w2 - 0.1, X + w2 + 0.1, Y, Y + 0.18 * s_, Z - w2 - 0.1, Z + w2 + 0.1, surf(BRASS, 2.0), surf(BRASS, 1.4), top=surf(BRASS, 3.0))
    rs.box(X - w2, X + w2, Y + 0.18 * s_, Y + hh, Z - w2, Z + w2, glass, glass, cls='emit')
    rs.quad((X - w2 - 0.12, Y + hh, Z - w2), (X + w2 + 0.12, Y + hh, Z - w2), (X, Y + hh + 0.55 * s_, Z - w2),
            lambda x, y, s, t, z, wp: BRASS[3] if t < 1 - abs(s - 0.5) * 2 else None, cls='prop', cut=True)
    rs.disc(X, Y + hh + 0.75 * s_, Z - w2, 0.18 * s_, lambda x, y, s, t, z, wp: None if s * s + t * t < 0.35 else BRASS[2])
    add_light(X, Y + hh * 0.6, Z - w2 - 0.3, 7.0, pp=0.9, rad=8.0)
    SOOT.append((X, Y + hh + 0.8, Z))
def green_lamp(X, Y, Z, s_=1.0):
    """a green glass lamp (the tall kind of the old art): brass foot, a glowing green chimney, a brass cap"""
    rs.box(X - 0.35 * s_, X + 0.35 * s_, Y, Y + 0.3 * s_, Z - 0.35, Z + 0.35, surf(BRASS, 2.6), surf(BRASS, 1.8), top=surf(BRASS, 3.4))
    def glass(x, y, s, t, z, wp):
        u = abs(s - 0.5) * 2
        wd = 0.55 + 0.45 * math.sin(min(1.0, t * 1.15) * math.pi) ** 0.8
        if u > wd: return None
        if (s * 6) % 1 < 0.1 and 0.1 < t < 0.9: return GREEN[4]
        return GREEN[7] if u < 0.3 and 0.3 < t < 0.7 else (GREEN[6] if u < 0.65 else GREEN[5])
    rs.quad((X - 0.42 * s_, Y + 0.3 * s_, Z - 0.36), (X + 0.42 * s_, Y + 0.3 * s_, Z - 0.36), (X - 0.42 * s_, Y + 1.5 * s_, Z - 0.36), glass, cls='emit', cut=True)
    rs.box(X - 0.3 * s_, X + 0.3 * s_, Y + 1.5 * s_, Y + 1.75 * s_, Z - 0.4, Z + 0.3, surf(BRASS, 2.8), surf(BRASS, 2.0), top=surf(BRASS, 3.6))
    add_light(X, Y + 0.9 * s_, Z - 0.7, 4.5, col=GREENC, pp=0.7, rad=7.0)
def pendant(X, Y, Z):
    """a lamp hung on a chain from the vault: a green glass dome shade, the warm opening under it"""
    top = vault_y(X) - 0.3
    rs.line3((X, Y + 1.1, Z), (X, top, Z), lambda x, y, s, t, z, wp: fg(BRASS[1] if (x + y) % 2 else OAK[0], z), w=0.09)
    def shade(x, y, s, t, z, wp):
        u = abs(s - 0.5) * 2
        if t < 0.18:                                                   # the open rim seen from below: the bulb
            return (LAMP[6] if u < 0.35 else LAMP[4]) if u < 1 - (0.18 - t) * 1.2 else None
        wd = 1.0 - (t - 0.18) ** 1.6 * 0.95
        if u > wd: return None
        if t > 0.86: return BRASS[3]
        v = 6.4 - u * 2.2 - (t - 0.18) * 2.0
        return ri(GREEN, band(v, x, y))
    rs.quad((X - 1.35, Y - 0.25, Z), (X + 1.35, Y - 0.25, Z), (X - 1.35, Y + 1.15, Z), shade, cls='emit', cut=True)
    add_light(X, Y - 0.8, Z, 520.0, kind='down', pp=6.0, rad=24.0)
def banker(X, Y, Z):
    """a banker's desk lamp: brass stem, a horizontal green shade, warm light pooled on the desk"""
    rs.box(X - 0.4, X + 0.4, Y, Y + 0.12, Z - 0.25, Z + 0.25, surf(BRASS, 2.6), surf(BRASS, 2.0), top=surf(BRASS, 3.6))
    rs.line3((X, Y + 0.1, Z), (X, Y + 1.05, Z), flat(BRASS[4]), w=0.09)
    def shade(x, y, s, t, z, wp):
        if t < 0.22: return LAMP[5] if 0.08 < s < 0.92 else BRASS[3]
        v = 6.6 - abs(s - 0.5) * 1.5 - (t - 0.22) * 3.4
        return ri(GREEN, band(v, x, y))
    rs.quad((X - 0.85, Y + 0.95, Z - 0.25), (X + 0.85, Y + 0.95, Z - 0.25), (X - 0.85, Y + 1.35, Z - 0.25), shade, cls='emit')
    add_light(X, Y + 0.6, Z - 0.4, 14.0, kind='down', col=WARMC, pp=1.6, rad=7.0)

# ---------------------------------------------------------------------------------------------------- the left side wall: a bookcase, a ladder on its rail
def lbc(x, y, s, t, z, wp): return oak(2.0, along='z')(x, y, s, t, z, wp)
rs.quad((-WX + 0.05, 0, 24.8), (-WX + 0.05, 0, 35.4), (-WX + 0.05, 19.6, 24.8), oak(0.6, lk=0.5, along='z'), cls='prop')
ys = 0.6
for k in range(8):
    rs.quad((-WX + 1.2, ys, 25.2), (-WX + 1.2, ys, 35.0), (-WX + 1.2, ys + 2.0, 25.2),
            spines(book_row(25.2, 35.0, 70 + k, 1.1, 1.85), ys, along='z'), cls='prop', cut=True)
    rs.box(-WX, -WX + 1.6, ys - 0.18, ys, 24.8, 35.4, oak(2.6, along='z'), oak(2.6, along='z'), top=oak(3.2, along='z'))
    ys += 2.3
    if ys > 18.8: break
for uz in (24.8, 28.3, 31.8, 35.0):
    rs.box(-WX, -WX + 1.65, 0, 19.6, uz, uz + 0.35, oak(2.4, along='z'), oak(2.0, along='z'), top=oak(3.0))
rs.box(-WX, -WX + 1.9, 19.6, 20.1, 24.6, 35.6, oak(3.0, along='z'), oak(2.6, along='z'), bottom=oak(1.0, along='z'))
rs.line3((-WX + 1.9, 17.6, 24.8), (-WX + 1.9, 17.6, 35.2), flat(BRASS[4]), w=0.1)                       # the ladder rail
for lz in (29.4, 30.6):
    rs.line3((-WX + 4.2, 0.0, lz), (-WX + 2.0, 17.7, lz), oak(3.4, along='z'), w=0.16)
for k in range(1, 15):
    yy = k * 1.2; xx = -WX + 4.2 - yy / 17.7 * 2.2
    rs.line3((xx, yy, 29.4), (xx, yy, 30.6), oak(3.0, along='z'), w=0.11)
green_lamp(-WX + 0.9, 20.1, 31.5)
archive_boxes(-WX + 0.1, -WX + 1.6, 20.1, 25.2, 27.4, 5, layers=1)

# ---------------------------------------------------------------------------------------------------- left outer bay: bookcase + the specimen vitrine
bookcase(-39.4, -28.0, 0.0, 20.4, ZB - 1.7, 1.6, seed=1)
green_lamp(-31.0, 20.85, ZB - 1.2)
archive_boxes(-39.0, -33.0, 20.85, ZB - 1.6, ZB - 0.3, 9, layers=1)

PANES = []                                                             # glass panes (screen polygons + depth) for the sheen
def vitrine(x0, x1, z0, z1, yb, yt, seed, glow=GREENC):
    """an oak base of drawers, a brass-edged glass case on it (the panes get a sheen after the render), a velvet back
    lit from a lamp hidden in the case's top"""
    rs.box(x0, x1, 0, yb, z0, z1, drawers(x1 - x0, yb - 0.4, 3, 2, 2.4, seed), oak(1.8), top=oak(3.2))
    rs.box(x0 - 0.15, x1 + 0.15, yb - 0.25, yb, z0 - 0.15, z1 + 0.15, oak(3.0), oak(2.2), top=oak(3.6))
    def back(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = 0.5 + lit(X, Y, Z) * 0.3 + 1.5 * math.exp(-((s - 0.5) ** 2 * 3 + (t - 0.85) ** 2 * 2.5)) + (wn(1, X * 4, Y * 4) - 0.5) * 0.4
        return ri(GREEN, band(v, x, y))
    rs.quad((x0, yb, z1 - 0.05), (x1, yb, z1 - 0.05), (x0, yt, z1 - 0.05), back, cls='prop')
    rs.quad((x0, yb + 0.01, z0), (x1, yb + 0.01, z0), (x0, yb + 0.01, z1), lambda x, y, s, t, z, wp: ri(GREEN, band(0.8 + (1 - t) * 0.6, x, y)), cls='prop')
    edge = lambda x, y, s, t, z, wp: fg(tone(BRASS, 2.0 + lit(*wp) * 0.5 + (0.8 if y % 3 == 0 else 0), x, y), z)
    side_x = x1 if x1 < 0 else x0
    for (p, q) in (((x0, yb, z0), (x0, yt, z0)), ((x1, yb, z0), (x1, yt, z0)), ((x0, yt, z0), (x1, yt, z0)),
                   ((x0, yt, z0), (x0, yt, z1)), ((x1, yt, z0), (x1, yt, z1)), ((side_x, yb, z1), (side_x, yt, z1))):
        rs.line3(p, q, edge, w=0.13)
    rs.box(x0 - 0.12, x1 + 0.12, yt, yt + 0.3, z0 - 0.12, z1 + 0.12, surf(BRASS, 1.8), surf(BRASS, 1.4), top=surf(BRASS, 2.6))
    PANES.append(([proj(x0, yb, z0), proj(x1, yb, z0), proj(x1, yt, z0), proj(x0, yt, z0)], z0))
    PANES.append(([proj(side_x, yb, z0), proj(side_x, yb, z1), proj(side_x, yt, z1), proj(side_x, yt, z0)], z0))
    add_light((x0 + x1) / 2, yt - 0.6, z0 + 0.6, 4.0, col=glow, pp=0.7, rad=6.0)

VL = (-37.4, -30.6, 31.0, 33.9, 3.2, 9.4)
vitrine(*VL, 3)
EYEW = ramp('#3a3628 #57513c #777052 #978f6c #b5ad88 #cfc8a4')
def jar(x, y, s, t, z, wp):
    """a tall specimen jar: a brass lid, the shoulders, yellow-green fluid with a meniscus, and in it a great pale eye
    with its nerve trailing below (an "entry" the Tribunal filed)"""
    u = abs(s - 0.5) * 2
    if t > 0.93: return (BRASS[4] if t > 0.965 else BRASS[2]) if u < 0.6 else None   # the lid
    if t > 0.9: return BRASS[1] if u < 0.5 else None                   # the neck
    sh_ = 0.8
    wd = 0.94 if t < sh_ else 0.94 - ((t - sh_) / 0.1) ** 2 * 0.46     # the round shoulders
    if t < 0.05: wd = 0.94 - (0.05 - t) * 4                            # the foot
    if u > wd: return None
    if u > wd - 0.07: return GREEN[5] if s < 0.5 else GREEN[3]         # the glass wall, its edge catching light
    if t > 0.78: return ri(GREEN, band(2.2 - u, x, y))                  # air above the fluid
    if t > 0.765: return FLUID[6]                                      # the meniscus
    ex, ey, er = 0.5, 0.52, 0.27                                       # the eye, in jar space (aspect ~0.6)
    dx, dy = (s - ex) / er, (t - ey) / (er * 0.62)
    d = math.hypot(dx, dy)
    if d < 1.0:
        ix, iy = dx - 0.28, dy + 0.05                                  # it looks a little to the right
        di = math.hypot(ix, iy)
        if di < 0.2: return (16, 12, 8)
        if di < 0.42: return ri(OCHRE, band(4.2 - di * 5 + (0.8 if ix < 0 else 0), x, y))
        if di < 0.47: return OCHRE[1]
        if (h32(int(math.atan2(dy, dx) * 9), 5) % 4 == 0) and 0.55 < d < 0.95 and abs((math.atan2(dy, dx) * 9) % 1 - 0.5) < 0.12:
            return OXB[5]                                              # veins
        return ri(EYEW, band(4.6 - d * 1.6 - dy * 0.8 + (0.6 if dx < -0.3 and dy < 0 else 0), x, y))
    nx_ = 0.5 + 0.06 * math.sin(t * 22)                                # the nerve and its frayed roots
    if t < ey - er * 0.6 and t > 0.12 and abs(s - nx_) < 0.045 + (ey - t) * 0.04: return ri(PALE, band(3.0 - abs(s - nx_) * 20, x, y))
    for k in range(3):
        rx = 0.5 + (k - 1) * 0.1 * (0.3 + (0.3 - t) * 3)
        if 0.08 < t < 0.2 and abs(s - rx - 0.04 * math.sin(t * 40 + k)) < 0.015: return PALE[2]
    v = 2.0 + (1 - u) * 1.4 + (1.2 if 0.16 < s < 0.24 else 0) + (h32(x // 2, y // 3, 5) % 17 == 0) * 1.0
    return ri(FLUID, band(v, x, y))
rs.quad((-35.4, 3.25, 32.6), (-32.6, 3.25, 32.6), (-35.4, 8.9, 32.6), jar, cls='emit', cut=True)
rs.box(-35.6, -32.4, 3.0, 3.25, 32.2, 33.2, surf(BRASS, 1.8), surf(BRASS, 1.4), top=surf(BRASS, 2.4))

# ---------------------------------------------------------------------------------------------------- left inner bay: card catalogues, the ladder
CX0, CX1 = -24.4, -11.6
rs.box(CX0, CX1, 0, 0.5, 33.1, ZB - 0.1, oak(1.6), oak(1.2), top=oak(2.6))
rs.box(CX0, CX1, 0.5, 8.4, 33.3, ZB - 0.1, drawers(CX1 - CX0, 7.9, 9, 7, 2.6, 7), oak(1.8), top=oak(3.0))
rs.box(CX0 - 0.2, CX1 + 0.2, 8.4, 8.9, 33.0, ZB - 0.1, oak(3.2), oak(2.4), top=oak(3.8), bottom=oak(1.2))
rs.box(CX0 + 0.4, CX1 - 0.4, 8.9, 15.7, 33.8, ZB - 0.1, drawers(CX1 - CX0 - 0.8, 6.8, 8, 7, 2.4, 8), oak(1.6), top=oak(3.0))
rs.box(CX0, CX1, 15.7, 16.3, 33.5, ZB - 0.1, oak(3.0), oak(2.2), top=oak(3.6), bottom=oak(1.0))
rs.box(CX0 + 0.8, CX1 - 0.8, 16.3, 20.1, 34.1, ZB - 0.1, drawers(CX1 - CX0 - 1.6, 3.8, 7, 4, 2.2, 9), oak(1.6), top=oak(3.0))
rs.box(CX0 + 0.5, CX1 - 0.5, 20.1, 20.6, 33.9, ZB - 0.1, oak(3.0), oak(2.2), top=oak(3.6), bottom=oak(1.0))
archive_boxes(CX0 + 0.8, CX1 - 3.4, 20.6, 34.2, ZB - 0.3, 11, layers=2)
lantern(-13.6, 20.6, 34.9, 0.9)
rs.line3((CX0, 19.4, 33.9), (CX1, 19.4, 33.9), flat(BRASS[4]), w=0.1)                                     # ladder rail
for lx in (-18.6, -17.2):
    rs.line3((lx, 0.0, 30.0), (lx, 19.6, 33.7), oak(3.4), w=0.17)
    rs.disc(lx, 0.22, 29.9, 0.22, lambda x, y, s, t, z, wp: BRASS[2] if s * s + t * t > 0.3 else BRASS[4])
for k in range(1, 17):
    yy = k * 1.15; zz = 30.0 + yy / 19.6 * 3.7
    rs.line3((-18.6, yy, zz), (-17.2, yy, zz), oak(3.0), w=0.12)

# ---------------------------------------------------------------------------------------------------- centre: the registry station, the seal
SX0, SX1, SZ0 = -4.2, 4.2, 33.6
def station(x, y, s, t, z, wp):
    X, Y, Z = wp
    L = lit(X, Y, Z)
    pz = z / F
    if Y < 0.5: return fg(tone(OAK, 1.4 + L * 0.6, x, y), z)
    if Y < 5.3:                                                        # pigeonholes: rolled forms, tube canisters
        fu, fv = (X - SX0 - 0.3) / 1.11, (Y - 0.6) / 1.15
        i, j = math.floor(fu), math.floor(fv); a, b = fu - i, fv - j
        if i < 0 or i > 6 or a * 1.11 < pz * 1.6 + 0.08 or b * 1.15 < pz * 1.6 + 0.08: return fg(tone(OAK, 2.6 + L, x, y), z)
        q = h32(i, j, 61)
        cx_, cy_ = 0.55, 0.42
        if q % 5 == 0: return fg(tone(OAK, 0.4 + L * 0.3, x, y), z)       # empty
        if q % 5 == 1:                                                  # a brass canister end
            d = math.hypot((a - cx_) * 1.11, (b - cy_) * 1.15)
            if d < 0.36: return fg(tone(BRASS, 3.0 + L - d * 3, x, y), z)
            return fg(tone(OAK, 0.6 + L * 0.3, x, y), z)
        for (ox, oy) in ((0.3, 0.3), (0.7, 0.32), (0.5, 0.68), (0.25, 0.7), (0.78, 0.7)):   # rolled forms
            d = math.hypot((a - ox) * 1.11, (b - oy) * 1.15)
            if d < 0.17: return fg(tone(PARCH, 4.4 + L - d * 6 - (0.8 if d < 0.05 else 0), x, y), z)
        return fg(tone(OAK, 0.6 + L * 0.3, x, y), z)
    if Y < 5.75: return fg(tone(OAK, 3.4 + L, x, y), z)
    if abs(X) < 2.3 and (Y < 9.5 or math.hypot(X, Y - 9.5) < 2.3) and Y > 6.1: return None   # the niche
    if Y < 12.4:
        d = max(abs(X) - 2.3, 0)
        edge = abs(X) < 2.75 and (Y < 9.5 or math.hypot(X, Y - 9.5) < 2.75)
        v = 2.5 + L + (wn(1, X * 5, Y * 0.5) - 0.5) * 0.6
        if edge: v += 0.8 if X < 0 else 0.3
        if abs(abs(X) - 3.55) < 0.12 or abs(Y - 6.1) < 0.1: v -= 0.8         # carved panel lines
        return fg(tone(OAK, v, x, y), z)
    if Y < 13.0:
        if (X * 2.5) % 1 < 0.45 and Y < 12.75: return fg(tone(OAK, 1.6 + L, x, y), z)   # dentils
        return fg(tone(OAK, 3.2 + L, x, y), z)
    return fg(tone(OAK, 3.6 + L, x, y), z)
rs.quad((SX0, 0, SZ0), (SX1, 0, SZ0), (SX0, 13.6, SZ0), station, cls='prop', cut=True)
rs.box(SX0 - 0.35, SX1 + 0.35, 13.6, 14.2, SZ0 - 0.35, ZB - 0.1, oak(3.4), oak(2.4), top=oak(3.8), bottom=oak(1.2))
def niche(x, y, s, t, z, wp):
    """the niche's lining, lit warm from a hidden lamp above the ampulla"""
    X, Y, Z = wp
    k = math.exp(-(X * X) / 2.6 - ((Y - 11.0) ** 2) / 5.0)
    if k > 0.55: return ri(LAMP, band(0.4 + (k - 0.55) * 7.0, x, y))
    return ri(OAK, band(3.0 + k * 9.0, x, y))
rs.quad((-2.4, 6.0, 34.9), (2.4, 6.0, 34.9), (-2.4, 11.9, 34.9), niche, cls='emit')
rs.box(-2.3, 2.3, 6.0, 6.25, 33.7, 34.9, oak(3.0), oak(2.4), top=oak(3.8))
def ampulla(x, y, s, t, z, wp):
    """the Tribunal's ink in a great glass ampulla: a round belly, a long neck, a brass stopper, a violet sheen"""
    X, Y, Z = wp
    u = s - 0.5
    if t > 0.93: return BRASS[5] if abs(u) < 0.09 else None
    if t > 0.88: return BRASS[3] if abs(u) < 0.07 else None
    r_belly = 0.42
    by = 0.33
    d = math.hypot(u, (t - by) * 0.86)
    if t > by and abs(u) < 0.075 + max(0.0, 0.55 - t) * 0.9: inside = True
    else: inside = d < r_belly
    if not inside: return None
    edge = d > r_belly - 0.04 if t < by + 0.3 else abs(u) > 0.06
    if edge: return INKC[5]
    if t > 0.62: return INKC[4] if abs(u + 0.03) < 0.012 else (INKC[1] if t > 0.66 else INKC[3])   # the meniscus in the neck
    v = 1.6 - u * 1.4 + (2.4 if abs(u + 0.2 - (t - by) * 0.2) < 0.035 and d < 0.34 else 0) + (1.6 if math.hypot(u + 0.16, t - 0.5) < 0.04 else 0)
    return ri(INKC, band(v, x, y))
rs.quad((-1.8, 6.25, 34.5), (1.8, 6.25, 34.5), (-1.8, 11.6, 34.5), ampulla, cls='prop', cut=True)
add_light(0.0, 10.6, 33.6, 9.0, pp=1.2, rad=6.0)
# the dispatch dial on top
def dial(x, y, s, t, z, wp):
    d = math.hypot(s, t)
    if d > 0.88: return BRASS[2] if d > 0.96 else BRASS[5]
    a = math.atan2(t, s)
    if d > 0.68 and abs(((a / (2 * math.pi) * 16) % 1) - 0.5) > 0.38: return OAK[2]
    hx_, hy_ = math.cos(math.radians(-62)), math.sin(math.radians(-62))
    if 0 < s * hx_ + t * hy_ < 0.62 and abs(s * hy_ - t * hx_) < 0.05: return OAK[1]
    return PARCH[6] if d < 0.6 else PARCH[5]
rs.box(-1.7, 1.7, 14.2, 15.0, 34.2, 35.6, oak(3.0), oak(2.2), top=oak(3.6))
rs.box(-1.9, 1.9, 15.0, 18.0, 34.6, 35.6, surf(BRASS, 1.6), surf(BRASS, 1.2), bottom=surf(BRASS, 0.8))
rs.disc(0.0, 16.5, 34.5, 1.35, dial)
# pneumatic tubes: along the vault, down the back wall beside the pilasters, into the dial's drum (the Bureau's tube post)
def tube_sh(x, y, s, t, z, wp): return fg(tone(BRASS, 1.3 + (1.0 if y % 3 == 0 else 0) + lit(*wp) * 0.25, x, y), z)
for sx in (-1, 1):
    X = sx * 8.5; yv = vault_y(X) - 0.5; zt = ZB - 0.4
    yv = vault_y(X) - 2.2
    rs.disc(X, yv + 0.2, ZB - 0.1, 0.5, lambda x, y, s, t, z, wp: (12, 10, 8) if s * s + t * t < 0.5 else ASH[5])   # the hole in the wall
    rs.line3((X, yv, zt), (X, 16.6, zt), tube_sh, w=0.3)
    rs.line3((X, 16.6, zt), (sx * 1.9, 16.6, zt), tube_sh, w=0.3)
    for yy in (19.0, 24.5, 29.0):
        rs.box(X - 0.3, X + 0.3, yy, yy + 0.25, ZB - 0.75, ZB - 0.05, surf(BRASS, 1.2), surf(BRASS, 1.0))   # brackets
# cast-iron pipes from the Townhall above (the right outer bay)
IRON = ramp('#0b0b0a #121211 #1a1918 #232220 #2d2b28 #383532')
def pipe_sh(x, y, s, t, z, wp): return fg(tone(IRON, 1.6 + (1.2 if y % 4 == 1 or x % 4 == 1 else 0) + lit(*wp) * 0.6, x, y), z)
rs.line3((28.4, vault_y(28.4) - 0.6, ZB - 0.5), (28.4, 0.0, ZB - 0.5), pipe_sh, w=0.55)
rs.line3((39.0, SPR + 0.5, ZB - 0.5), (39.0, 5.0, ZB - 0.5), pipe_sh, w=0.55)
rs.line3((28.4, 19.4, ZB - 0.55), (39.0, 19.4, ZB - 0.55), pipe_sh, w=0.45)
for (px_, py_) in ((28.4, 7.0), (28.4, 14.0), (28.4, 25.0), (39.0, 12.0)):
    rs.box(px_ - 0.45, px_ + 0.45, py_, py_ + 0.3, ZB - 1.0, ZB - 0.05, surf(IRON, 1.6), surf(IRON, 1.2))
rs.box(38.4, 39.6, 1.8, 2.6, ZB - 1.2, ZB - 0.05, surf(IRON, 1.8), surf(IRON, 1.4), top=surf(IRON, 2.4))   # a valve box
# two banners of the Tribunal flanking its seal: oxblood, the nib in brass, a fringe, hung from rods
def banner(x, y, s, t, z, wp):
    X, Y, Z = wp
    tail = 0.12 * (1 - abs(s - 0.5) * 2)                               # a swallow-tail point at the bottom
    if t < tail: return None
    L = lit(X, Y, Z)
    if t < tail + 0.035: return ri(BRASS, band(1.8 + L * 0.5 + (x % 2), x, y))
    if s < 0.05 or s > 0.95: return fg(tone(OXB, 1.6 + L, x, y), z)
    fold = math.sin(s * math.pi * 3.0 + 0.4) * (0.4 + 0.6 * t)
    u, v = (s - 0.5) / 0.32, -(t - 0.58) / 0.2                         # the nib, small, pointing down
    half = 0.0
    if -0.9 < v < -0.3: half = 0.55
    elif -0.3 <= v < 0.9: half = 0.75 * (1 - (v + 0.3) / 1.2)
    if abs(u) < half and not (abs(u) < 0.08 and v < 0.2) and math.hypot(u, v + 0.25) > 0.14:
        return ri(BRASS, band(2.6 + L * 0.6 - u * 0.8 + fold * 0.6, x, y))
    v_ = 2.4 + fold * 1.2 + L * 0.9 + (wn(1, X * 3, Y * 0.5) - 0.5) * 0.4 + (0.6 if t > 0.92 else 0)
    return fg(tone(OXB, v_, x, y), z)
for sx in (-1, 1):
    bx = sx * 6.1
    rs.quad((bx - 1.25, 18.3, ZB - 0.25), (bx + 1.25, 18.3, ZB - 0.25), (bx - 1.25, 29.4, ZB - 0.25), banner, cls='prop', cut=True)
    rs.line3((bx - 1.55, 29.45, ZB - 0.3), (bx + 1.55, 29.45, ZB - 0.3), flat(BRASS[2]), w=0.14)
    for fx_ in (bx - 1.6, bx + 1.6): rs.disc(fx_, 29.45, ZB - 0.32, 0.17, lambda x, y, s, t, z, wp: BRASS[4] if s + t < 0 else BRASS[2])
# the Tribunal's seal on the lunette
def seal(x, y, s, t, z, wp):
    d = math.hypot(s, t)
    if d > 0.97: return BRASS[1]
    if d > 0.83:
        a = math.atan2(t, s)
        if abs(((a / (2 * math.pi) * 32) % 1) - 0.5) > 0.36 and d < 0.93: return BRASS[2]
        return ri(BRASS, band(4.6 - s * 1.4 - t * 1.2 + (0.6 if d > 0.93 else 0), x, y))
    if d > 0.78: return BRASS[0]
    u, v = s / 0.74, t / 0.74                                          # the nib, pointing down
    half = 0.0
    if -0.62 < v < -0.22: half = 0.2 + math.sqrt(max(0.0, 1 - ((v + 0.22) / 0.4) ** 2)) * 0.14
    elif -0.22 <= v < 0.78: half = 0.34 * (1 - (v + 0.22) / 1.0) ** 0.9
    if abs(u) < half:
        if abs(u) < 0.025 and 0.05 < v < 0.76: return INKC[1]               # the slit
        if math.hypot(u, v - 0.02) < 0.07: return INKC[1]                  # the breather hole
        if v < -0.4 and abs(v + 0.4) < 0.025: return BRASS[2]
        return ri(BRASS, band(5.2 - u * 3.2 - (v + 0.6) * 0.8, x, y))
    if math.hypot(u, (v - 0.86) * 0.8) < 0.07: return INKC[3]               # a drop of ink at the tip
    return ri(OXB, band(4.2 - d * 2.6 - s * 0.8, x, y))
rs.disc(0.0, 25.4, ZB - 0.15, 3.3, seal)
# flanking shelves: jars + bottles (left), ledger boxes + a green lamp (right)
rs.quad((-8.4, 0, ZB - 0.25), (-5.0, 0, ZB - 0.25), (-8.4, 15.4, ZB - 0.25), oak(0.8, lk=0.6), cls='prop')
for ux in (-8.4, -5.35):
    rs.box(ux, ux + 0.35, 0, 15.4, 33.8, ZB - 0.2, oak(2.4), oak(1.8))
rs.box(-8.4, -5.0, 0, 0.6, 33.8, ZB - 0.2, oak(1.6), oak(1.2), top=oak(2.8))
for k, yy in enumerate((2.6, 5.4, 8.2, 11.0, 13.8)):
    rs.box(-8.6, -4.8, yy - 0.2, yy, 33.7, ZB - 0.2, oak(3.0), oak(2.2), top=oak(3.4))
    for j in range(4):
        jx = -7.95 + j * 0.7 + (h32(k, j, 3) % 3) * 0.05
        hh = 1.0 + (h32(k, j, 4) % 4) * 0.3
        fl = [FLUID, GREEN, BOXC[0], FLUID][h32(k, j, 5) % 4]
        def sjar(x, y, s, t, z, wp, fl=fl, q=h32(k, j, 6)):
            u = abs(s - 0.5) * 2
            if t > 0.86: return BRASS[3] if u < 0.8 else None
            if u > 0.95: return None
            if t > 0.72: return fl[1]
            v = 2.0 + (1 - u) * 1.4 + (1.0 if 0.22 < s < 0.32 else 0) + (lit(*wp) * 0.6 if wp else 0)
            if q % 3 == 0 and 0.35 < t < 0.6 and u < 0.5: return PALE[3]
            return ri(fl, band(v, x, y))
        if jx + 0.6 < -5.4: rs.quad((jx, yy, 34.6), (jx + 0.6, yy, 34.6), (jx, yy + min(hh, 2.4), 34.6), sjar, cls='prop', cut=True)
rs.box(-8.6, -4.8, 15.4, 15.7, 33.7, ZB - 0.2, oak(3.0), oak(2.2), top=oak(3.4))
lantern(-6.6, 15.7, 34.6, 0.9)
rs.box(5.0, 8.6, 0, 0.5, 33.7, ZB - 0.2, oak(1.4), oak(1.2), top=oak(2.6))
rs.box(5.0, 8.6, 0.5, 15.4, 33.9, ZB - 0.2, drawers(3.6, 14.9, 2, 13, 2.4, 23), oak(1.8), top=oak(3.0))
rs.box(4.8, 8.8, 15.4, 15.7, 33.7, ZB - 0.2, oak(3.0), oak(2.2), top=oak(3.4))
archive_boxes(5.1, 8.6, 15.7, 34.0, ZB - 0.3, 21, layers=1)
green_lamp(7.9, 15.7, 34.3)

# ---------------------------------------------------------------------------------------------------- right inner bay: the eggshell vitrine, ledgers above
VR = (13.6, 21.4, 30.6, 33.6, 3.0, 9.2)
vitrine(*VR, 5, glow=(1.0, 0.92, 0.75))
def shard(x, y, s, t, z, wp):
    """a broken piece of the Egg Cathedral's shell, like the bottom of a giant egg: the convex outside below the
    front rim, the concave inside seen above it up to the back rim, a thick layered break along both rims"""
    X, Y, Z = wp
    u = (s - 0.5) * 2.0                                                # -1..1 across
    if abs(u) > 1: return None
    bot = 0.9 - 0.9 * math.sqrt(max(0.0, 1 - u * u))                   # the egg's round bottom (t from 0)
    if t < bot * 0.55: return None
    front = 0.46 + 0.16 * u - 0.07 * math.sin(u * 5.3 + 1) - 0.025 * math.sin(u * 19 + 2) + (0.1 if 0.28 < u < 0.46 else 0) - (0.06 if -0.7 < u < -0.52 else 0)
    back = 0.9 - 0.22 * u * u - 0.08 * math.sin(u * 4.1 + 2) - 0.02 * math.sin(u * 23) - (0.16 if -0.42 < u < -0.18 else 0) - (0.05 if 0.5 < u < 0.62 else 0)
    if t > back: return None
    if abs(u) > 0.96 * math.sqrt(max(0.0, 1 - ((t - 0.95) / 0.95) ** 2)) + 0.02: return None
    L = lit(X, Y, Z) * 0.4
    q = h32(int((u + 1) * 22 + t * 7), int(t * 26 - u * 5), 77)
    if t < front:                                                      # the outside, lit from the upper left
        if front - t < 0.035: return ri(SHELL, band(5.4 + L, x, y))
        n = -u * 0.55 + (1 - t / max(0.01, front)) * -0.6
        v = 3.8 + n * 1.6 + L - (0.9 if q % 11 == 0 else 0)
        if (h32(x // 2, y // 2, 79) % 19) == 0: v -= 0.6               # speckles
        return ri(SHELL, band(v, x, y))
    if back - t < 0.03: return ri(SHELL, band(5.0 + L, x, y))
    v = 2.0 + u * 1.2 + (t - front) * 1.4 + L - (0.8 if q % 9 == 0 else 0)   # the inside: shaded the other way
    c = ri(SHELL, band(v, x, y))
    if h32(int(u * 30), int(t * 40), 78) % 17 == 0: c = mix(c, (66, 92, 74), 0.5)   # a trace of membrane
    return c
rs.quad((15.0, 3.7, 32.2), (20.0, 3.7, 32.2), (15.0, 8.7, 32.2), shard, cls='prop', cut=True)
rs.line3((17.5, 3.0, 32.4), (17.5, 4.4, 32.4), flat(BRASS[3]), w=0.14)                                  # its stand
rs.box(16.6, 18.4, 3.0, 3.25, 31.8, 32.8, surf(BRASS, 2.4), surf(BRASS, 1.8), top=surf(BRASS, 3.0))
rs.line3((18.9, 6.6, 32.15), (19.6, 4.6, 32.0), flat(PARCH[3]), w=0.04)                                 # the string...
rs.quad((19.2, 3.5, 31.9), (20.5, 3.6, 31.9), (19.2, 4.6, 31.9), lambda x, y, s, t, z, wp: PARCH[6] if (t * 5) % 1 > 0.25 or s < 0.15 else INKC[3], cls='prop')   # ...and the index card
# a bracketed wall shelf of ledgers over it
for k, yy in enumerate((10.6, 13.0, 15.4, 17.8)):
    rs.quad((12.4, yy, 35.2), (23.6, yy, 35.2), (12.4, yy + 2.1, 35.2),
            spines(book_row(12.4, 23.6, 90 + k, 1.2, 1.95), yy), cls='prop', cut=True)
    rs.box(12.0, 24.0, yy - 0.22, yy, 34.4, ZB - 0.05, oak(3.0), oak(2.2), top=oak(3.6), bottom=oak(1.0))
    for bx in (12.6, 23.2):
        rs.quad((bx, yy - 1.0, ZB - 0.06), (bx + 0.2, yy - 1.0, ZB - 0.06), (bx, yy - 0.2, ZB - 0.06), flat(OAK[1]), cls='prop')
rs.box(12.0, 24.0, 20.0, 20.25, 34.4, ZB - 0.05, oak(3.0), oak(2.2), top=oak(3.6), bottom=oak(1.0))
green_lamp(14.0, 20.25, 35.0)
archive_boxes(16.0, 23.6, 20.25, 34.6, ZB - 0.2, 31, layers=1)
lantern(22.4, 3.0, 31.6, 0.85)

# ---------------------------------------------------------------------------------------------------- right outer bay: the archway, the curtain
def passage_wall(x, y, s, t, z, wp):
    X, Y, Z = wp
    dark = max(0.0, (Z - 36.0) / 12.0)
    fv = (Y / 1.8) % 1
    if fv < 0.12: v = 1.6
    else:
        k = h32(int(Z / 0.5), int(Y / 1.8), 83)
        v = 2.4 + (k % 4) * 0.35 - (0.8 if (Z / 0.5) % 1 < 0.15 else 0)
    v += lit(X, Y, Z) - dark * 2.2
    r_ = BOXC[h32(int(Z / 0.5), int(Y / 1.8), 84) % 3] if fv >= 0.12 else OAK
    return fg(tone(r_, v, x, y), z)
rs.quad((30.2, 0, 35.9), (30.2, 0, 50.0), (30.2, 11.4, 35.9), passage_wall, cls='wall')
rs.quad((37.6, 0, 35.9), (37.6, 0, 50.0), (37.6, 11.4, 35.9), passage_wall, cls='wall')
rs.quad((30.2, 0, 35.9), (37.6, 0, 35.9), (30.2, 0, 50.0), lambda x, y, s, t, z, wp: fg(tone(FLAG, 2.2 + lit(*wp) - (wp[2] - 36) / 7.0, x, y), z), cls='ground')
rs.quad((30.2, 11.4, 35.9), (37.6, 11.4, 35.9), (30.2, 11.4, 50.0), flat(BRICK[1]), cls='ceil')
rs.quad((30.2, 0, 50.0), (37.6, 0, 50.0), (30.2, 11.4, 50.0), flat(OAK[0]), cls='wall')
rs.line3((33.9, 11.4, 46.0), (33.9, 8.0, 46.0), flat(OAK[0]), w=0.06)
rs.box(33.6, 34.2, 7.0, 7.9, 45.7, 46.3, lambda x, y, s, t, z, wp: LAMP[3] if 0.2 < s < 0.8 else BRASS[1], lambda x, y, s, t, z, wp: LAMP[2], cls='emit')
add_light(33.9, 7.4, 45.5, 5.0, pp=0.6, rad=7.0)
# the curtain: a valance with a fringe over the arch, the panel drawn aside to the right and tied back
CZ_ = ZB - 0.75
def x_left(Y):
    return 30.0 + (12.1 - Y) / 6.1 * 4.9 if Y >= 6.0 else 34.9 - (6.0 - Y) / 6.0 * 1.6
def curtain(x, y, s, t, z, wp):
    X, Y, Z = wp
    if Y > 11.0:                                                       # the valance, swagged
        sw = 11.0 + 0.5 * abs(math.sin((X - 29.4) / 9.4 * math.pi * 2.0))
        if Y < sw - 0.12: return None
        if Y < sw: return ri(BRASS, band(3.0 + (x % 2), x, y))            # the fringe
        v = 3.2 + 1.2 * math.sin((X - 29.4) * 3.1) + lit(X, Y, Z) * 0.8
        return fg(tone(OXB, v, x, y), z)
    xl = x_left(Y)
    if X < xl: return None
    if abs(Y - 6.0) < 0.35 and X < 37.2:                               # the tieback cord
        return ri(BRASS, band(4.0 - abs(Y - 6.0) * 4 + math.sin(X * 9) * 0.6, x, y))
    if 34.7 < X < 35.4 and 4.4 < Y < 5.7:                              # its tassel
        return ri(BRASS, band(3.2 + (0.8 if x % 2 else 0) - (5.7 - Y) * 0.6, x, y))
    p = (X - xl) / max(0.4, 38.3 - xl)
    pleat = math.sin(p * math.pi * 2 * (4.0 + 3.0 * math.exp(-((Y - 6.0) / 2.2) ** 2)) + Y * 0.08)
    v = 3.0 + 1.5 * pleat + lit(X, Y, Z) * 0.9 - (1.4 if p < 0.04 else 0) - 0.5 * max(0.0, 1 - Y / 1.5)
    v += (wn(1, X * 2, Y * 0.4) - 0.5) * 0.5
    return fg(tone(OXB, v, x, y), z)
rs.quad((29.4, 0, CZ_), (38.6, 0, CZ_), (29.4, 12.6, CZ_), curtain, cls='prop', cut=True)
rs.line3((29.0, 12.5, CZ_ - 0.05), (39.0, 12.5, CZ_ - 0.05), flat(BRASS[3]), w=0.16)
for fx_ in (29.0, 39.0): rs.disc(fx_, 12.5, CZ_ - 0.1, 0.24, lambda x, y, s, t, z, wp: BRASS[5] if s + t < 0 else BRASS[2])
lantern(26.0, 11.6, ZB - 1.6, 0.9)                                     # on a bracket on the pilaster
rs.box(25.2, 26.8, 11.35, 11.6, ZB - 2.4, ZB - 1.2, surf(OAK, 2.0), surf(OAK, 1.6), top=surf(OAK, 2.8))
lantern(-26.0, 11.6, ZB - 1.6, 0.9)
rs.box(-26.8, -25.2, 11.35, 11.6, ZB - 2.4, ZB - 1.2, surf(OAK, 2.0), surf(OAK, 1.6), top=surf(OAK, 2.8))

# ---------------------------------------------------------------------------------------------------- the right side wall: the charter, the Bureau's cabinets
def charter(x, y, s, t, z, wp):
    """a framed charter: gilt frame, parchment with lines of a clerk's hand, a red wax seal on a ribbon"""
    X, Y, Z = wp
    L = lit(X, Y, Z)
    if s < 0.07 or s > 0.93 or t < 0.06 or t > 0.94:
        return fg(tone(BRASS, 2.6 + L + (0.8 if t > 0.94 or s < 0.07 else 0), x, y), z)
    if s < 0.1 or s > 0.9 or t < 0.09 or t > 0.91: return fg(tone(OAK, 1.2 + L, x, y), z)
    c = tone(PARCH, 3.6 + L + (wn(1, Z * 2, Y * 2) - 0.5) * 0.8 - max(0.0, abs(s - 0.5) - 0.3) * 4, x, y)
    sx_, sy_ = 0.62, 0.22
    d = math.hypot((s - sx_) * 1.0, (t - sy_) * 1.6)
    if d < 0.09: return ri(OXB, band(5.0 - d * 30 + (1 if s < sx_ else 0), x, y))
    if 0.14 < t < sy_ and (abs(s - sx_ + (sy_ - t) * 0.8) < 0.025 or abs(s - sx_ - (sy_ - t) * 0.6) < 0.025): return OXB[4]
    if 0.82 < t < 0.86 and 0.25 < s < 0.75: return INKC[2]             # the heading
    if 0.3 < t < 0.78 and 0.16 < s < 0.84 and ((t - 0.3) * 18) % 1 < 0.32:
        ln = math.floor((t - 0.3) * 18)
        if s < 0.84 - (h32(ln, 5) % 4) * 0.08 and h32(int(s * 40), ln, 6) % 5: return mix(c, INKC[2], 0.7)
    return c
rs.quad((WX - 0.06, 7.4, 26.6), (WX - 0.06, 7.4, 31.6), (WX - 0.06, 14.6, 26.6), charter, cls='prop')
for k in range(5):
    zc = 24.8 + k * 2.05
    hh = 5.4 - (k % 2) * 0.7
    rs.box(37.7, WX - 0.05, 0, hh, zc, zc + 2.0, surf(STEELB, 2.0, lk=0.7), drawers(2.0, hh, 1, 4, 2.2, 30 + k, along='z', steel=True, lk=0.7),
           top=surf(STEELB, 2.8, lk=0.7))
    if k % 2 == 0: archive_boxes(37.9, 39.9, hh, zc + 0.2, zc + 1.8, 40 + k, layers=1)
green_lamp(38.8, 4.7, 27.8)

# ---------------------------------------------------------------------------------------------------- the floor: desk, trolley, the pedestal
DX0, DX1, DZ0, DZ1, DY = -27.0, -19.0, 24.0, 26.4, 3.1
def desk_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    if t > 0.88: return fg(tone(OAK, 4.2 + lit(X, Y, Z), x, y), z)
    if 0.3 < s < 0.7:                                                  # the kneehole
        if t < 0.66: return fg(tone(OAK, 0.4 + lit(X, Y, Z) * 0.3, x, y), z)
    return drawers(DX1 - DX0, DY, 5, 3, 2.6, 52)(x, y, s, t, z, wp)
rs.box(DX0, DX1, 0, DY, DZ0, DZ1, desk_front, oak(2.0), top=oak(4.0))
rs.box(DX0 + 0.3, DX1 - 0.3, 0, 0.12, DZ0 + 0.2, DZ1 - 0.2, oak(0.6), oak(0.6))
banker(-25.8, DY, DZ0 + 1.4)
def ledger(x, y, s, t, z, wp):
    """the open register: two pages of entries, a ribbon"""
    if abs(s - 0.5) < 0.03: return PARCH[2]
    if s < 0.03 or s > 0.97 or t < 0.05 or t > 0.95: return SPINES[1][3]
    if ((t * 14) % 1) < 0.28 and 0.1 < (s % 0.5) / 0.5 < 0.9 and h32(int(s * 30), int(t * 14), 9) % 4: return PARCH[3]
    if 0.6 < s < 0.63 and t < 0.4: return OXB[5]
    return PARCH[6] if s < 0.5 else PARCH[5]
rs.quad((-23.8, DY + 0.06, DZ0 + 0.5), (-21.0, DY + 0.06, DZ0 + 0.5), (-23.8, DY + 0.06, DZ0 + 2.0), ledger, cls='prop')
rs.box(-20.4, -19.8, DY, DY + 0.5, DZ0 + 0.9, DZ0 + 1.5, surf(INKC, 2.4), surf(INKC, 1.6), top=surf(INKC, 1.2))   # the inkwell
rs.line3((-20.1, DY + 0.4, DZ0 + 1.2), (-19.6, DY + 1.9, DZ0 + 1.5), flat(PARCH[6]), w=0.07)            # a quill
rs.box(-20.0, -19.2, DY, DY + 1.3, DZ0 + 1.6, DZ0 + 2.3, lambda x, y, s, t, z, wp: PARCH[6] if y % 2 else (PARCH[4] if h32(y, 3) % 3 else OXB[5]),
       lambda x, y, s, t, z, wp: PARCH[5], top=lambda x, y, s, t, z, wp: PARCH[6])                      # forms in triplicate
for k, sx in enumerate((-22.2, -21.8, -21.4)):                                                           # the stamp rack
    rs.line3((sx, DY + 0.5, DZ0 + 2.15), (sx, DY + 1.1, DZ0 + 2.15), lambda x, y, s, t, z, wp, k=k: (OXB[5], INKC[3], OAK[5])[k], w=0.24)
    rs.disc(sx, DY + 1.25, DZ0 + 2.15, 0.15, lambda x, y, s, t, z, wp: OAK[6])
rs.box(-22.5, -21.1, DY, DY + 0.5, DZ0 + 1.9, DZ0 + 2.4, oak(3.0), oak(2.4), top=oak(3.4))
# the chair pushed back
rs.box(-24.6, -22.6, 2.0, 2.3, DZ1 + 0.5, DZ1 + 2.3, oak(2.6), oak(2.0), top=oak(3.4))
rs.quad((-24.6, 2.3, DZ1 + 2.3), (-22.6, 2.3, DZ1 + 2.3), (-24.6, 5.2, DZ1 + 2.4), oak(2.4), cls='prop')
for lx_ in (-24.4, -22.8): rs.line3((lx_, 0.0, DZ1 + 0.7), (lx_, 2.0, DZ1 + 0.7), oak(2.0), w=0.16)
# the knocked-over inkpot and its spill (the floor under the desk's corner)
def spill(x, y, s, t, z, wp):
    X, _, Z = wp
    dx, dz = X + 18.6, Z - 23.0
    r = math.hypot(dx * 1.0, dz * 1.4) + (wn(1, X * 2.2, Z * 2.2) - 0.5) * 0.7 + 0.25 * math.sin(math.atan2(dz, dx) * 5)
    if r > 1.25: return None
    if r > 1.08: return INKC[0]
    if math.hypot(dx + 0.4, dz + 0.2) < 0.2: return INKC[4]                  # the lamp caught in it
    return INKC[1] if (x + y) % 5 else INKC[2]
rs.quad((-20.6, 0.02, 21.4), (-16.6, 0.02, 21.4), (-20.6, 0.02, 24.6), spill, cls='prop', cut=True)
rs.box(-18.0, -17.2, 0.0, 0.5, 23.7, 24.3, surf(INKC, 2.2), surf(INKC, 1.6), top=surf(INKC, 2.6))
# the docket trolley (right)
TX0, TX1, TZ0, TZ1 = 22.0, 27.6, 22.6, 24.4
for yy in (0.6, 2.2, 3.6):
    rs.box(TX0, TX1, yy - 0.18, yy, TZ0, TZ1, oak(3.0), oak(2.2), top=oak(3.6))
for yy, sd in ((0.6, 120), (2.2, 121)):
    rs.quad((TX0 + 0.2, yy, TZ0 + 0.35), (TX1 - 0.2, yy, TZ0 + 0.35), (TX0 + 0.2, yy + 1.5, TZ0 + 0.35),
            spines(book_row(TX0 + 0.2, TX1 - 0.2, sd, 0.9, 1.45), yy), cls='prop', cut=True)
for ux in (TX0, TX1 - 0.2):
    rs.box(ux, ux + 0.2, 0.3, 4.4, TZ0, TZ0 + 0.2, oak(2.6), oak(2.0))
    rs.disc(ux + 0.1, 0.24, TZ0 - 0.1, 0.24, lambda x, y, s, t, z, wp: BRASS[1] if s * s + t * t > 0.4 else BRASS[3])
rs.line3((TX1 - 0.1, 4.4, TZ0 + 0.1), (TX1 + 0.4, 4.9, TZ0 + 0.1), flat(BRASS[4]), w=0.12)
archive_boxes(TX0 + 0.1, TX1 - 0.1, 3.6, TZ0 + 0.1, TZ1 - 0.1, 66, layers=1)
# stacks of ledgers framing the near corners
for (bx, bz, n, sd) in ((-29.6, 19.6, 6, 1), (-28.0, 20.4, 3, 2), (29.0, 20.0, 5, 3)):
    for k in range(n):
        q = h32(sd, k)
        w_ = 1.4 + (q % 3) * 0.15; d_ = 1.0 + (q % 2) * 0.12; off = ((q >> 3) % 5 - 2) * 0.06
        r_ = SPINES[q % len(SPINES)]
        def lfront(x, y, s, t, z, wp, r_=r_):
            if s > 0.9: return fg(tone(PARCH, 3.4 + lit(*wp), x, y), z)
            return fg(tone(r_, 2.4 + lit(*wp) + 0.8 * (1 - abs(2 * t - 1) ** 2), x, y), z)
        rs.box(bx + off, bx + off + w_, k * 0.34, k * 0.34 + 0.32, bz, bz + d_, lfront, surf(PARCH, 2.6), top=surf(r_, 3.2))
for k in range(13):                                                                                   # a few loose forms
    fx, fz = [(-14.4, 30.6), (-9.8, 31.8), (11.4, 30.4), (16.4, 27.6), (-31.4, 29.0), (31.4, 25.0), (-12.0, 26.4), (24.6, 29.6), (-6.6, 17.4),
              (12.2, 15.2), (-17.6, 14.4), (19.8, 18.6), (-22.4, 19.6)][k]
    a = (h32(k, 23) % 628) / 100.0; c, s_ = math.cos(a) * 0.38, math.sin(a) * 0.38
    rs.quad((fx - c, 0.03, fz - s_), (fx + s_, 0.03, fz - c), (fx - s_, 0.03, fz + c),
            lambda x, y, s, t, z, wp: fg(PARCH[5] if (x + y) % 4 else PARCH[3], z), cls='prop')

# the pedestal (octagonal bronze, brass bands); the orb is composited after the render
PZ, PY, OR = CC[1], 3.4, 1.85
def octa(v0, r=BRASS):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        f = 0 if s < 0.29 else (1 if s < 0.71 else 2)
        v = v0 + (0.7, 0.0, -0.6)[f] + lit(X, Y, Z) * 0.45 + (wn(1, X * 6, Y * 6) - 0.5) * 0.5
        if abs(s - 0.29) < 0.02 or abs(s - 0.71) < 0.02: v += 0.7
        if t > 0.9: v += 0.6                                           # the lit top arris
        return fg(tone(r, v, x, y), z)
    return sh
BRONZE = ramp('#120c06 #1d140a #2a1d0f #382715 #47321b #573e22 #684a2a')
def shaft(x, y, s, t, z, wp):
    X, Y, Z = wp
    if 0.36 < s < 0.64 and 0.4 < t < 0.75:                             # a plaque with an ink drop
        u, v = (s - 0.5) / 0.14, (t - 0.575) / 0.175
        if abs(u) > 0.86 or abs(v) > 0.86: return ri(BRASS, band(2.8 + lit(X, Y, Z) * 0.4, x, y))
        dd = math.hypot(u * 1.4, (v + 0.22) * 1.4)
        if dd < 0.5 or (-0.1 < v < 0.7 and abs(u) < 0.5 * (1 - (v + 0.1) / 0.8) ** 1.4): return INKC[2]
        return ri(BRASS, band(1.8 + lit(X, Y, Z) * 0.4, x, y))
    return octa(2.0, BRONZE)(x, y, s, t, z, wp)
rs.box(-1.6, 1.6, 0.0, 0.2, PZ - 1.6, PZ + 1.6, octa(1.8, BRONZE), octa(1.4, BRONZE), top=octa(2.8, BRONZE))
rs.box(-1.4, 1.4, 0.2, 0.6, PZ - 1.4, PZ + 1.4, octa(2.2, BRONZE), octa(1.8, BRONZE), top=octa(2.6, BRONZE))
rs.box(-1.0, 1.0, 0.6, 2.75, PZ - 1.0, PZ + 1.0, shaft, octa(1.6, BRONZE))
rs.box(-1.3, 1.3, 2.75, 3.15, PZ - 1.3, PZ + 1.3, octa(2.6, BRONZE), octa(2.0, BRONZE), top=octa(3.2, BRONZE), bottom=octa(1.0, BRONZE))
rs.box(-0.85, 0.85, 3.15, PY, PZ - 0.85, PZ + 0.85, octa(1.4), octa(1.0), top=octa(1.0, BRONZE))

# ---------------------------------------------------------------------------------------------------- the pendant lamps, the orb's own faint light
pendant(-7.6, 16.4, 20.6)
pendant(7.6, 16.4, 20.6)
add_light(0.0, PY + OR, PZ - 0.5, 0.0, col=(0.7, 0.85, 0.8), pp=0.5, rad=5.0)

def mirror(x, y, wp):
    X, _, Z = wp
    r = math.hypot(X - CC[0], Z - CC[1])
    if r < R_IN - 0.2: return 0.24
    if r < R_OUT: return 0.12 * (1 if wn(2, X * 0.5 + 9, Z * 0.5) > 0.5 else 0.4)
    return 0.0

def _inpoly(pts, u, v):
    inside = False; n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        if (y0 > v) != (y1 > v) and u < x0 + (x1 - x0) * (v - y0) / (y1 - y0): inside = not inside
    return inside
def glass_sheen(img):
    """the vitrines' panes: a faint cool cast and two diagonal glints where nothing nearer stands before the glass"""
    ip = img.load()
    for (pts, zg) in PANES:
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        x0, x1, y0, y1 = int(min(xs)), int(max(xs)) + 1, int(min(ys)), int(max(ys)) + 1
        w_, h_ = max(1, x1 - x0), max(1, y1 - y0)
        for y in range(max(0, y0), min(H, y1)):
            for x in range(max(0, x0), min(W, x1)):
                if not _inpoly(pts, x + 0.5, y + 0.5) or rs.ZB[y][x] < zg - 0.2: continue
                d = (x - x0) / w_ + (y - y0) / h_ * 0.6
                k = 0.08
                if abs(d - 0.42) < 0.035 or abs(d - 0.56) < 0.012: k = 0.3
                c = ip[x, y]
                ip[x, y] = mix(c, (168, 196, 184), k)
def orb(img):
    """the ball lens: the room behind it, inverted and squeezed, a cool tint, a curl of mist in the glass, a Fresnel
    rim, the highlight of the pendant lamps, the bronze claws holding it"""
    (cx, cy) = proj(0.0, PY + OR - 0.12, PZ); rr = OR * F / PZ
    src = img.copy(); sp = src.load(); ip = img.load()
    for y in range(int(cy - rr) - 2, int(cy + rr) + 3):
        for x in range(int(cx - rr) - 2, int(cx + rr) + 3):
            a, b = (x + 0.5 - cx) / rr, (y + 0.5 - cy) / rr
            d = math.hypot(a, b)
            if d > 1.0: continue
            k = 2.2 - 1.0 * d * d
            sx_, sy_ = int(cx - a * rr * k), int(cy - b * rr * k * 0.8 - rr * 0.9)
            c = sp[max(0, min(W - 1, sx_)), max(0, min(H - 1, sy_))]
            c = mix(c, (52, 70, 64), 0.2)
            sw = wn(3, a * 2.2 + math.sin(b * 3.0) * 0.8 + 7, b * 2.2 + 3) + 0.25 * math.sin(math.atan2(b, a) * 2 + d * 6)
            mist = max(0.0, sw - 0.5) * 2.0 * (0.5 + 0.5 * max(0.0, b + 0.4))
            c = mix(c, (128, 150, 140), min(0.62, mist + 0.12))
            fr = max(0.0, d - 0.7) / 0.3
            c = mix(c, (150, 176, 164), fr ** 2 * 0.35) if b < 0.2 else mix(c, (10, 12, 10), fr ** 2 * 0.55)
            for (hx_, hy_, r0) in ((-0.4, -0.46, 0.1), (0.5, -0.18, 0.045)):   # the pendants caught in the glass
                e = math.hypot((a - hx_) * 1.2, b - hy_)
                if e < r0: c = (236, 240, 214)
                elif e < r0 * 2.0: c = mix(c, (214, 226, 196), 0.4)
            if 0.82 < d < 0.92 and -2.6 < math.atan2(b, a) < -1.9: c = mix(c, (200, 214, 196), 0.5)   # a thin rim glint
            if d > 0.95: c = mix(c, (8, 10, 9), 0.75)
            ip[x, y] = tuple(max(0, min(255, int(v / 4 + 0.5) * 4)) for v in c)
    # three bronze claws rising from the cup round the orb's lower half
    def dot(px_, py_, c):
        if 0 <= px_ < W and 0 <= py_ < H: ip[px_, py_] = c
    for side in (-1, 1):
        for k in range(14):
            tt = k / 13.0
            ang = math.radians(150 - tt * 42) if side < 0 else math.radians(30 + tt * 42)
            px_ = cx + math.cos(ang) * rr * 1.02; py_ = cy + math.sin(ang) * rr * 1.02
            dot(int(px_), int(py_), BRASS[2]); dot(int(px_) - side, int(py_), BRASS[4] if side < 0 else BRASS[1])
            dot(int(px_) + side, int(py_), (14, 10, 6))
    for k in range(int(rr * 0.4)):
        py_ = int(cy + rr * 0.98 - k)
        dot(int(cx) - 1, py_, BRASS[4]); dot(int(cx), py_, BRASS[3]); dot(int(cx) + 1, py_, BRASS[1])
    dot(int(cx), int(cy + rr * 0.98 - rr * 0.4), BRASS[5])

img = rs.render(INK, fog=fog, mirror=mirror, lights=LIGHTS, light_gain=1.2, grime_gain=0.5, bloom=0.55, stain_gain=0.2, damp_gain=0.2)
glass_sheen(img)
orb(img)
img.save(f'{OUT}/tribunal.png')
# the palette for hand touch-ups in Aseprite (the ramps this room is painted from)
with open(f'{OUT}/tribunal.gpl', 'w') as fh:
    fh.write('GIMP Palette\nName: tribunal\nColumns: 9\n#\n')
    seen = set()
    for name, r in (('ash', ASH), ('brick', BRICK), ('flag', FLAG), ('inkstone', INKST), ('oak', OAK), ('brass', BRASS), ('green', GREEN),
                    ('lamp', LAMP), ('oxblood', OXB), ('parchment', PARCH), ('ink', INKC), ('fluid', FLUID), ('shell', SHELL),
                    ('steel', STEELB), ('iron', IRON), ('bronze', BRONZE)) + tuple(('spine%d' % i, sp) for i, sp in enumerate(SPINES[:7])):
        for i, c in enumerate(r):
            if c in seen: continue
            seen.add(c); fh.write('%3d %3d %3d %s %d\n' % (c[0], c[1], c[2], name, i))
print('done tribunal')
