"""The Rust Domain -- the Rust Choir's floors at the top of the Scraper (RustDomainScene), 1067x600, the shared camera
(raster3d.py). After the old AI picture (a dark cavernous machine hall: stacked machinery with green CRTs either side,
two red-glowing boiler vats in the middle, cables everywhere, a grated walk in front, a cold light far back):

  shell   two office floors of old Nexicorp Tower knocked through into one tall hall: the cut slab of the floor between
          them left as a ledge along both walls, the tower's windows plated over (cold daylight in the seams), a
          coffered concrete ceiling on heavy beams with a broken opening far back where a shaft of overcast daylight
          falls through the haze; concrete columns wrapped in pipes; cast-iron deck plates, corroded, oily
  middle  the Choir's singing machines: two riveted copper boiler-vats with sight-glasses full of churning redmass,
          corroded feeding funnels on their domes, rust coral (redmass bloom, "coral made of blood-coloured steel")
          crawling up their plinths; behind them, under the light, the iron organ -- a rank of rusted pipes on a wind
          chest that the vats feed (the machines "roar to life with a sound like a cathedral organ made of iron")
  left    a workbench crusted with solder and coral (green CRT terminals, a vice, wire), behind it cabinets of gauges
          and a red beacon; redmass seeping off the bench in glowing runnels; a scrap altar (a cog wheel on a pile of
          plates, a dead terminal, offerings), oil drums and crates up front
  right   the same bank in other hands: a workbench with CRTs, the old air-conditioning unit (the one that "remembers
          forty years of cooling office workers"), a rack of blinking lamps; coils of cable on crates up front
  front   the grated walk back to the Lift-Mother (the exit, bottom centre); through the grating the boiler crypts'
          furnace glow far below (Gorj's floors)
No people (Brukk is the scene's sprite), no fungi, no lettering.

    python3 rustdomain_bg.py <outdir>   ->  rust.png  (= assets/images/backgrounds/RustDomain.png)
"""
import sys, math, random
from common import ramp, h32, make_noise, band
from raster3d import Raster, proj, ray, W, H, CX, HY, F, CAMH

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
R = ramp
IRON   = R('#08090a #0d1011 #121617 #181d1e #1f2526 #272e2f #303839 #3a4343 #464f4e #545d5b #66706c')
RUST   = R('#15100b #1c140d #241910 #2e1f12 #392614 #452d17 #52351a #5f3d1e #6d4622 #7c5027 #8c5b2d #9d6734')
COPPER = R('#140b08 #1e110b #29170e #351e12 #422616 #50301b #5f3a21 #704528 #825231 #94603b #a8714a')
VERD   = R('#0e1715 #13201c #1a2b25 #22372f #2c443a #375246 #436152')
PAINT  = R('#0d1315 #12191b #172023 #1d282b #243134 #2c3b3e #354548 #405153')       # the machines' old service paint
DRUMP  = R('#140a09 #1d0f0d #281412 #331a16 #40201b #4d2820')                      # oxblood drum paint
OCHRE  = R('#16110a #20190e #2b2213 #372c18 #44361d #514123 #5f4c2a')              # the AC unit's enamel
CONC   = R('#090a0a #0e100f #131514 #191c1a #1f2320 #262a27 #2e322e #363b36 #40453f #4b5049')
SCREEN = R('#04120a #082011 #0e2f1a #164425 #205d33 #2e7b45 #45a05b #6fc67c #aeeba8')
REDL   = R('#2a0504 #470907 #6d100a #981a10 #c42a18 #ec4a2a #ff8452 #ffc6a0')
FURN   = R('#1e0a04 #331206 #4f1c08 #70290c #963a10 #bc5016 #dc6c22 #f2913a #ffbf6c #ffe4b0')
CORAL  = R('#170507 #26080a #3a0c0f #4f1114 #661719 #7f201f #992c25 #b33c2c')
CABLE  = R('#050606 #0a0c0c #101313 #171b1b #1f2424 #293030')
BRASS  = R('#1a1307 #2c210c #403011 #574217 #6e541e #876828 #a27e35')
DAY    = R('#1b2627 #253435 #324546 #435a5a #587170 #708986 #8ea29c #b0c0b8 #d2dcd2')
ZINC   = R('#0c0f0f #131817 #1a201f #222928 #2b3331 #353e3b #404946 #4c5551 #5a635e #6b736d #7f867f')
WOODR  = R('#0f0a07 #170f0a #20150e #2a1b12 #352217 #412a1c')
INK = (5, 5, 5)
BAY = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

_nz = [make_noise(1, s, 509, 509) for s in (61, 62, 63, 64, 65, 66)]
def wn(i, a, b): return _nz[i](a + 3000.0, b + 3000.0)              # noise in WORLD units
def ri(r, i): return r[max(0, min(len(r) - 1, int(i)))]
def tone(r, v, x, y): return ri(r, band(v, x, y))
def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def dith(x, y): return BAY[y % 4][x % 4] / 16.0 - 0.47

WX, CH, ZB = 30.0, 32.0, 84.0                                          # half width, ceiling, back wall
LEDGE = 15.0                                                           # the cut slab of the floor in between
VAT = [(-3.45, 22.0), (3.45, 22.0)]; VR, VH = 3.05, 10.5               # the two boiler-vats: centres, radius, body top
ORG_Z = 37.0                                                           # the iron organ's pipe line
HOLE = (-6.0, 6.0, 33.0, 40.5)                                         # the broken ceiling: x0, x1, z0, z1
BEAM = (0.0, 36.8)                                                     # the light shaft's centre at the ceiling
GRATE = (-5.0, 5.0, 4.0, 18.6)                                         # the grated walk: x0, x1, z0, z1

# ---------------------------------------------------------------------------------------------------- light
RED, GREEN, WARM, COLD = (1.0, 0.4, 0.18), (0.35, 1.0, 0.5), (1.0, 0.6, 0.3), (0.62, 0.82, 0.86)
LIGHTS = [((-3.0, 5.0, 18.0), RED, 1.4, 8.5), ((3.0, 5.0, 18.0), RED, 1.4, 8.5),
          ((-17.4, 5.2, 22.4), GREEN, 0.5, 6.0), ((17.6, 5.2, 22.4), GREEN, 0.5, 6.0),
          ((-16.8, 10.4, 27.0), GREEN, 0.3, 5.0), ((15.9, 10.8, 27.0), GREEN, 0.3, 5.0),
          ((-12.0, 16.6, 21.0), WARM, 1.15, 10.0), ((13.0, 17.6, 24.5), WARM, 1.05, 10.0),
          ((-24.4, 11.8, 27.4), (1.0, 0.2, 0.1), 0.4, 5.0), ((-14.6, 4.6, 18.6), (1.0, 0.25, 0.1), 0.35, 3.5),
          ((0.0, -2.5, 12.0), (1.0, 0.5, 0.18), 0.55, 5.0),
          ((0.0, 25.0, 32.0), COLD, 1.25, 12.0), ((0.0, 12.0, 33.5), COLD, 0.6, 9.0)]
def illum(X, Y, Z, n):
    tot, cr, cg, cb = 0.0, 0.0, 0.0, 0.0
    for (lx, ly, lz), lc, I, r in LIGHTS:
        dx, dy, dz = lx - X, ly - Y, lz - Z
        d2 = dx * dx + dy * dy + dz * dz
        if d2 > 9 * r * r: continue
        d = math.sqrt(d2) + 1e-6
        ndl = 0.55 if n is None else max(0.0, (dx * n[0] + dy * n[1] + dz * n[2]) / d)
        e = I * (0.15 + 0.85 * ndl) * r * r / (r * r + d2 * 1.5)
        tot += e; cr += lc[0] * e; cg += lc[1] * e; cb += lc[2] * e
    if tot < 1e-4: return 0.0, (1.0, 1.0, 1.0)
    m = max(cr, cg, cb)
    return tot, (cr / m, cg / m, cb / m)
def lit(c, I, lc, k=0.5):
    t = min(k, I * 0.45)
    return tuple(max(0, min(255, int(c[i] * (1 - t + t * 1.85 * lc[i])))) for i in range(3))
FOGC = (13, 18, 18)
def fog(z): return max(0.0, min(0.72, (z - 24) / 64.0))
def fogged(c, z): return mix(c, FOGC, fog(z))
def amb(Y, Z):
    """the hall is dark: less fill high up and far back"""
    return 0.15 - 0.5 * min(1.0, Y / 26.0) - 0.4 * min(1.0, max(0.0, Z - 30) / 40.0)
def shade(r, v, X, Y, Z, n, x, y, z, gain=2.3, tint=0.5):
    I, lc = illum(X, Y, Z, n)
    if r is RUST: tint = min(tint, 0.28)                                                    # rust stays brown under the red glow
    return fogged(lit(tone(r, v + amb(Y, Z) + I * gain, x, y), I, lc, tint), z)

def beam_at(X, Y, Z):
    """the shaft of daylight from the broken ceiling: 0..1, soft-edged, spreading a little as it falls"""
    if Y > CH or Y < 0: return 0.0
    k = (CH - Y) / CH
    cx, cz = BEAM[0] + 0.3 * k, BEAM[1] - 2.6 * k
    hx, hz = 4.6 + 1.8 * k, 3.0 + 1.0 * k
    u, w = (X - cx) / hx, (Z - cz) / hz
    d = u * u + w * w
    if d > 1: return 0.0
    return (1 - d) ** 1.5 * (0.55 + 0.45 * (1 - k))

rs = Raster()
N_FRONT, N_UP, N_L, N_R = (0, 0, -1), (0, 1, 0), (1, 0, 0), (-1, 0, 0)

# ---------------------------------------------------------------------------------------------------- materials
def corrosion(u, Y, seed, amount):
    """how rusted a vertical metal surface is here (0..1): broad low-contrast blooms + pitting"""
    b = wn(0, u * 0.7 + seed * 7.3, Y * 0.22) * 0.6 + wn(1, u * 2.4 + seed, Y * 0.9) * 0.4
    r = max(0.0, min(1.0, (b - (0.66 - amount * 0.42)) * 3.2))
    pit = h32(int(u * 11), int(Y * 11), seed) % 19 == 0
    return r, False, pit

def runs(u, Y, levels, seed, spacing=0.55, maxlen=2.4, every=2, w0=0.06):
    """rust run-off hanging from its sources (rivet rows, seams, hoops, clamps, sills, ledges) at the heights in
    `levels`: thin streaks that run straight down with gravity, wander a little, thin out and fade. 0..1"""
    best = 0.0
    m = round(u / spacing)
    for lv in levels:
        d = lv - Y
        if d <= 0 or d > maxlen: continue
        hk = h32(m + 999, int(lv * 10), seed)
        if hk % every: continue
        L = maxlen * (0.3 + 0.7 * (h32(m + 999, int(lv * 10), seed, 2) % 100) / 100.0)
        if d > L: continue
        c = m * spacing + 0.04 * math.sin(d * 2.3 + m) + ((hk >> 8) % 7 - 3) * 0.006
        w = w0 + 0.05 * (1 - d / L) + (0.05 if d < 0.12 else 0)                          # a blot at the source
        if abs(u - c) < w: best = max(best, (1 - d / L) ** 0.6)
    return best

def metal(base, v, u, Y, x, y, seed, amount, ps, run=0.0):
    """pick paint / rust for one pixel (dithered boundary -- no hard camouflage blotches); `run` = a run-off streak
    through this pixel (0..1). Returns (ramp, v)"""
    r_, _, pit = corrosion(u, Y, seed, amount)
    col = RUST if r_ + dith(x, y) * 0.45 > 0.5 else base
    if col is RUST: v += 0.15 + 0.5 * r_
    if run > 0.12 + (dith(x, y) + 0.5) * 0.25: col, v = RUST, v + 0.1 + 0.6 * run          # the run-off: orange-brown, brightest at its source
    if pit: v -= 0.8
    return col, v

def plate(base, v0, n, seed=0, amount=0.5, pw=2.4, ph=1.6, rivets=True, horiz='x', gain=2.3):
    """riveted plate steel with seams; paint worn to rust, rust bleeding from every seam and rivet"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = Z if horiz == 'z' else X
        ps = z / F
        fu, fy = (u / pw) % 1, (Y / ph) % 1
        v = v0 + (wn(3, u * 0.9 + seed, Y * 0.9) - 0.5) * 0.5 + (h32(int(u / pw + 99), int(Y / ph), seed) % 5 - 2) * 0.1
        am = amount + (0.25 if fy > 0.85 else 0)
        top = (math.floor(Y / ph) + 1) * ph - 0.2                                             # the rivet row above
        run = runs(u, Y, (top, top - ph), seed, spacing=0.55, maxlen=ph * (0.5 + amount), every=2 if amount > 0.6 else 3)
        col, v = metal(base, v, u, Y, x, y, seed, am, ps, run)
        if fu < 0.9 * ps / pw or fy < 0.9 * ps / ph: return shade(IRON, v - 1.3, X, Y, Z, n, x, y, z, gain)   # the seam
        if fy * ph < 1.2 * ps or fu * pw < 1.2 * ps: v += 0.5                               # the plate's lit edge
        if rivets and ((abs(fy * ph - 0.2) < 0.9 * ps and (u % 0.55) < 1.2 * ps) or (abs(fu * pw - 0.2) < 0.9 * ps and (Y % 0.55) < 1.2 * ps)):
            return shade(col, v + 1.2, X, Y, Z, n, x, y, z, gain)                             # a rivet head
        return shade(col, v, X, Y, Z, n, x, y, z, gain)
    return sh

def concrete(v0, n, seed=0, stains=0.6, horiz='x', drips=()):
    """board-marked concrete, soot runs; rust bled down it from the steel at the heights in `drips`"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = Z if horiz == 'z' else X
        v = v0 + (wn(3, u * 0.6 + seed, Y * 0.6) - 0.5) * 0.8 + (wn(5, u * 3 + seed, Y * 3) - 0.5) * 0.35
        if (Y / 0.9) % 1 < 1.0 * z / F / 0.9: v -= 0.3                                    # the formwork's board lines
        st = wn(2, u * 4.0 + seed, Y * 0.16)
        if st > 0.72 - stains * 0.1: v -= 0.6                                              # soot and damp runs
        col = CONC
        if drips:
            run = runs(u, Y, drips, seed, spacing=0.8, maxlen=3.6, every=2, w0=0.08)
            if run > 0.15 + (dith(x, y) + 0.5) * 0.3: col, v = RUST, v - 0.1 + 0.7 * run
        return shade(col, v, X, Y, Z, n, x, y, z)
    return sh

def flat(r, v0, n, k=0.4, seed=0):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp if wp else (0, 0, z)
        return shade(r, v0 + (wn(3, X * 2 + Z * 2 + seed, Y * 2) - 0.5) * k, X, Y, Z, n, x, y, z)
    return sh

def box(x0, x1, y0, y1, z0, z1, front, side=None, top=None, cls='prop'):
    """a box with normals baked into its shaders: front/side/top are factories f(n) -> shader"""
    sn = N_L if x1 < 0 else N_R
    return rs.box(x0, x1, y0, y1, z0, z1, front(N_FRONT), (side or front)(sn), top=(top or front)(N_UP) if y1 < CAMH else None,
                  bottom=(side or front)((0, -1, 0)) if y0 > CAMH else None, cls=cls)

def cylinder(cx, cz, r, y0, y1, sh_of, n=32, cls='prop', a0=-math.pi, a1=math.pi):
    """vertical cylinder from facets; sh_of(p0, p1, nrm) -> shader (only the facets facing the camera are drawn)"""
    for i in range(n):
        p0, p1 = a0 + (a1 - a0) * i / n, a0 + (a1 - a0) * (i + 1) / n
        pm = (p0 + p1) / 2
        nrm = (math.sin(pm), 0.0, -math.cos(pm))
        if nrm[0] * (cx + r * math.sin(pm)) + nrm[2] * (cz - r * math.cos(pm)) > 0.2: continue
        P0 = (cx + r * math.sin(p0), y0, cz - r * math.cos(p0)); P1 = (cx + r * math.sin(p1), y0, cz - r * math.cos(p1))
        rs.quad(P0, P1, (P0[0], y1, P0[2]), sh_of(p0, p1, nrm), cls=cls)

def disc_top(cx, cy, cz, r, sh, n=28, cls='prop'):
    """a horizontal disc (a lid) as a fan of triangles"""
    for i in range(n):
        p0, p1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        A = (cx + r * math.sin(p0), cy, cz - r * math.cos(p0)); B = (cx + r * math.sin(p1), cy, cz - r * math.cos(p1))
        rs.quad((cx, cy, cz), A, B, sh, clip=lambda a, b: a + b <= 1.0, cls=cls)

def pipe(P0, P1, w, v0=2.2, r=IRON, rust=0.5, seed=0, cls='prop'):
    """a 3D pipe: lit along its upper edge, rust in long patches, flanges every few units"""
    L = math.dist(P0, P1)
    vert = abs(P1[1] - P0[1]) > 0.7 * L
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        sx, sy = proj(*wp)
        rr = max(0.5, w * F / z / 2)
        acr = ((x + 0.5 - sx) if vert else (y + 0.5 - sy)) / rr                             # -1..1 across the pipe
        v = v0 + (0.9 if -0.75 < acr < -0.2 else 0) - (0.9 if acr > 0.55 else 0)
        al = s * L
        if (al % 3.6) < 0.16 and L > 3: v += 0.7                                             # a flange
        k = wn(1, al * 0.9 + seed * 5.1, 1.0 + seed)
        col = RUST if k + dith(x, y) * 0.3 > 1.0 - rust * 0.55 else r
        if col is RUST: v += 0.4
        return shade(col, v, X, Y, Z, None, x, y, z, gain=2.0)
    return rs.line3(P0, P1, sh, w=w, cls=cls)

def pipe_path(pts, w, **kw):
    for a, b in zip(pts, pts[1:]): pipe(a, b, w, **kw)

# ---------------------------------------------------------------------------------------------------- the shell
def oil(X, Z):
    """oily patches on the deck that shine (0..1)"""
    if Z > 30: return 0.0
    k = wn(4, X * 0.3 + 40, Z * 0.45) * 0.75 + wn(5, X * 1.3, Z * 1.3) * 0.25
    return max(0.0, min(1.0, (k - 0.56) * 6.0))

def floor_sh(x, y, s, t, z, wp):
    X, _, Z = wp
    pz = z * z / (F * CAMH)                                                                  # metres per pixel in depth
    fx, fz = (X / 2.4) % 1, (Z / 2.4) % 1
    v = 2.3 + (wn(0, X * 0.35, Z * 0.35) - 0.5) * 0.7 + (h32(int(X / 2.4 + 50), int(Z / 2.4), 3) % 5 - 2) * 0.12
    v -= 0.5 * max(0.0, abs(X) - 12) / 14                                                   # darker toward the walls
    col = IRON
    r1 = wn(1, X * 0.33 + 11, Z * 0.33) * 0.6 + wn(3, X * 1.3, Z * 1.3) * 0.4
    if r1 + dith(x, y) * 0.25 > 0.64: col, v = RUST, v + 0.1 + (r1 - 0.64) * 1.2             # rust eating the deck, flat patches
    if abs(Z - 15.0) < 2.6 and abs(X) < 22: v += 0.25 * (1 - abs(Z - 15.0) / 2.6)            # the walked strip, rubbed brighter
    if h32(int(Z * 24), int(X * 1.5), 6) % 13 == 0 and Z < 24: v += 0.45                     # scratches along the way people walk
    if h32(int(X * 11), int(Z * 11), 17) % 19 == 0: v -= 0.7                                 # pitting
    if fx < 0.9 * z / F / 2.4 or fz < 0.9 * pz / 2.4: col, v = IRON, v - 1.1                # plate seams
    elif (fx < 0.05 or fx > 0.95) and (fz < 0.05 or fz > 0.95): v += 0.9                     # bolt heads at the corners
    elif fz > 0.88 and h32(int(X / 2.4 + 50), int(Z / 2.4), 4) % 5 == 0: col, v = RUST, v - 0.2      # rust along a seam
    if h32(int(X * 4 + 99), int(Z * 1.5), 5) % 17 == 0 and wn(5, X * 2, Z * 2) > 0.62: v += 0.4      # scuffed bright
    o = oil(X, Z)
    if o > 0: v -= 0.5 * o
    I, lc = illum(X, 0.0, Z, N_UP)
    c = lit(tone(col, v + amb(0, Z) + I * 2.3, x, y), I, lc, 0.4)
    b = beam_at(X, 0.05, Z)
    if b > 0: c = mix(c, DAY[4], 0.5 * b)
    return fogged(c, z)
rs.quad((-WX, 0, 4), (WX, 0, 4), (-WX, 0, ZB), floor_sh, cls='ground')

def ceil_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    if HOLE[0] < X < HOLE[1] and HOLE[2] < Z < HOLE[3]:
        ex = min(X - HOLE[0], HOLE[1] - X, (Z - HOLE[2]) * 1.4, (HOLE[3] - Z) * 1.4)
        if ex > 0.4 + 1.4 * wn(4, X * 0.9, Z * 0.9): return None                            # the hole (cut)
    v = 1.6 + (wn(3, X * 0.5, Z * 0.5) - 0.5) * 0.8
    fx, fz = ((X + 10) / 6.67) % 1, (Z % 14.0) / 14.0                                        # coffers between the ribs
    if fx < 0.08 or fz < 0.05: v += 0.6
    elif fx < 0.14 or fz < 0.09: v -= 0.4
    if wn(2, X * 3.0, Z * 0.25) > 0.74: v -= 0.6                                            # soot over the old fires
    return shade(CONC, v, X, Y, Z, (0, -1, 0), x, y, z, gain=1.8)
rs.quad((-WX, CH, 4), (WX, CH, 4), (-WX, CH, ZB), ceil_sh, cls='ceil', cut=True)
def sky_sh(x, y, s, t, z, wp):                                                               # overcast glare through the hole
    return tone(DAY, 7.0 + (wn(2, wp[0] * 0.5, wp[2] * 0.5) - 0.5) * 1.2, x, y)
rs.quad((HOLE[0] - 3, CH + 2.6, HOLE[2] - 3), (HOLE[1] + 3, CH + 2.6, HOLE[2] - 3), (HOLE[0] - 3, CH + 2.6, HOLE[3] + 3), sky_sh, cls='emit')
# the broken slab's thickness on the far edge of the hole, rebar curling down from its rim
rs.quad((HOLE[0] - 1, CH, HOLE[3] - 0.5), (HOLE[1] + 1, CH, HOLE[3] - 0.5), (HOLE[0] - 1, CH + 2.6, HOLE[3] - 0.5),
        lambda x, y, s, t, z, wp: shade(CONC, 3.4 + (wn(3, wp[0] * 2, wp[1] * 2) - 0.5), *wp, N_FRONT, x, y, z, gain=2.0)
        if t < 0.96 - 0.35 * wn(4, wp[0] * 1.5, 1) else None, cls='wall', cut=True)
for k in range(14):
    X = HOLE[0] + 0.5 + k * 0.85
    Z0 = HOLE[2] + 0.4 + (h32(k, 1) % 5) * 0.2 if k % 2 else HOLE[3] - 0.6
    rs.line3((X, CH, Z0), (X + 0.4 * ((k % 3) - 1), CH - 0.8 - (h32(k, 4) % 5) * 0.35, Z0 + (0.6 if k % 2 else -0.6)),
             lambda x, y, s, t, z, wp: fogged(RUST[5] if (x + y) % 3 else RUST[2], z), w=0.1)

# beams: cross beams, two longitudinal beams
for zb in (29.6, 44.0, 58.0, 72.0):
    box(-WX, WX, CH - 2.2, CH, zb, zb + 1.4, lambda n, zb=zb: concrete(2.2, n, seed=int(zb)), cls='ceil')
for sx in (-1, 1):
    box(sx * 10.0 - 0.7, sx * 10.0 + 0.7, CH - 1.8, CH, 4.0, ZB, lambda n, sx=sx: concrete(1.8, n, seed=3 + sx, horiz='z'), cls='ceil')

# the side walls: concrete piers between the tower's window bays, the windows plated over (cold light in the seams),
# the cut floor slab left as a ledge between the two knocked-through storeys
WIN_Z = [14.0 + 7.5 * k for k in range(10)]
def wall_sh(sx):
    n = (-sx, 0, 0)
    pl = plate(PAINT, 1.5, n, seed=7 + sx, amount=0.3, pw=1.5, ph=2.0, horiz='z')
    cn = concrete(1.7, n, seed=5 + sx, horiz='z', stains=0.4, drips=(2.3, LEDGE - 0.05, LEDGE + 2.5, 26.0))
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        for wz in WIN_Z:
            if wz < Z < wz + 4.6:
                for (y0, y1) in ((2.4, 11.4), (LEDGE + 2.6, LEDGE + 11.0)):
                    if y0 < Y < y1:
                        k = h32(int(wz), int(y0), sx) % 7
                        e = min(Z - wz, wz + 4.6 - Z, Y - y0, y1 - Y)
                        if e < 0.28: return shade(IRON, 2.6, X, Y, Z, n, x, y, z)           # the window frame
                        if k == 0 and e > 0.5 and wz > 34:                                  # a plate gone: the overcast outside
                            return fogged(tone(DAY, 3.4 + (Y - y0) / (y1 - y0) * 1.2 - (0.8 if ((Z - wz) / 1.53) % 1 < 0.08 else 0), x, y), z)
                        seam = ((Z - wz) / 1.53) % 1 < 0.06 or abs(Y - (y0 + y1) / 2) < 0.06
                        if seam and k % 3 == 1 and wz > 20: return fogged(tone(DAY, 3.4, x, y), z)   # daylight in a seam
                        return pl(x, y, s, t, z, wp)
        if LEDGE - 0.3 < Y < LEDGE + 1.2: return shade(CONC, 1.4, X, Y, Z, n, x, y, z)      # behind the ledge
        return cn(x, y, s, t, z, wp)
    return sh
rs.quad((-WX, 0, 4), (-WX, 0, ZB), (-WX, CH, 4), wall_sh(-1), cls='wall')
rs.quad((WX, 0, 4), (WX, 0, ZB), (WX, CH, 4), wall_sh(1), cls='wall')
for sx in (-1, 1):                                                                         # the ledge, rebar hanging off it
    x0, x1 = (-WX, -WX + 1.8) if sx < 0 else (WX - 1.8, WX)
    box(x0, x1, LEDGE, LEDGE + 1.0, 4.0, ZB, lambda n, sx=sx: concrete(2.6, n, seed=9 + sx, stains=0.9, horiz='z', drips=(LEDGE + 0.95,)))
    for k in range(40):
        Z = 6.0 + k * 1.9 + (h32(k, sx) % 7) * 0.2
        xe = x1 if sx < 0 else x0
        rs.line3((xe, LEDGE, Z), (xe + sx * -0.2, LEDGE - 0.4 - (h32(k, sx, 3) % 6) * 0.25, Z + 0.1),
                 lambda x, y, s, t, z, wp: fogged(RUST[4] if (x + y) % 3 else RUST[2], z), w=0.08)
# windows in the side walls light the hall a little: soft cold light pools as point lights
for wz in WIN_Z:
    for sx in (-1, 1):
        if h32(int(wz), int(LEDGE + 2.6), sx) % 7 == 0 and wz > 34: LIGHTS.append(((sx * (WX - 2.0), LEDGE + 6.0, wz + 2.3), COLD, 0.35, 6.0))
        if h32(int(wz), int(2.4), sx) % 7 == 0 and wz > 34: LIGHTS.append(((sx * (WX - 2.0), 6.0, wz + 2.3), COLD, 0.35, 6.0))
rs.quad((-WX, 0, ZB), (WX, 0, ZB), (-WX, CH, ZB), concrete(1.6, N_FRONT, seed=21, drips=(8.0, 16.0, 24.0)), cls='wall')

# columns of the old office floors, wrapped in pipes and rust
def column(X, Z, seed):
    box(X - 0.85, X + 0.85, 0, CH - 2.2, Z - 0.85, Z + 0.85, lambda n: concrete(2.2, n, seed=seed, stains=0.9,
        drips=(2.9, 8.9, LEDGE + 0.4, 21.9, CH - 2.3), horiz='z' if n[0] else 'x'))
    for k, dx in enumerate((-1.15, 1.15)):
        pipe((X + dx, 0, Z - 0.6), (X + dx, CH - 2.2, Z - 0.6), 0.34, v0=2.0, rust=0.8, seed=seed + k)
    for yb in (3.0, 9.0, LEDGE + 0.5, 22.0):
        pipe((X - 1.35, yb, Z - 0.95), (X + 1.35, yb, Z - 0.95), 0.18, v0=2.8, r=IRON, rust=0.3, seed=seed + 5)
for Z in (31.0, 45.0, 59.0, 73.0):
    for X in (-21.0, -12.0, 12.0, 21.0):
        column(X, Z, int(Z + X))

# ---------------------------------------------------------------------------------------------------- the iron organ
# a rank of rusted pipes on a wind chest behind the vats, the tallest in the middle, under the light shaft
def organ():
    def chest(n):
        return plate(IRON, 2.2, n, seed=101, amount=0.8, pw=2.0, ph=1.2)
    box(-11.0, 11.0, 0, 3.8, ORG_Z - 1.2, ORG_Z + 2.2, chest, top=lambda n: plate(IRON, 2.6, n, seed=102, amount=0.9, pw=2.0, ph=9))
    N = 15
    for i in range(N):
        k = abs(i - (N - 1) / 2) / ((N - 1) / 2)                                          # 0 middle .. 1 sides
        X = -9.8 + i * 19.6 / (N - 1)
        r = 0.62 - 0.18 * k
        top = 27.0 - 11.5 * k ** 1.25
        if i == 4: top -= 5.5                                                             # a pipe broken short
        mouth = 3.8 + 1.4 + r * 1.6
        mat = COPPER if i % 4 == 1 else ZINC
        seed = 200 + i
        def sh_of(p0, p1, nrm, X=X, r=r, mouth=mouth, mat=mat, seed=seed, top=top):
            def sh(x, y, s, t, z, wp):
                PX, Y, Z = wp
                phi = p0 + (p1 - p0) * s
                if abs(phi) < 0.55 and mouth - 0.55 < Y < mouth + 0.1 + 0.5 * (1 - abs(phi) / 0.55):
                    if Y < mouth: return shade(CABLE, 0.6, PX, Y, Z, nrm, x, y, z)        # the mouth
                    return shade(mat, 3.2, PX, Y, Z, nrm, x, y, z)                         # the upper lip
                u = phi * r * 6
                v = 2.6 + (wn(3, u + seed, Y * 0.6) - 0.5) * 0.6 + 1.2 * math.cos(phi + 0.5) * 0.5
                if top - Y < 0.25: v += 1.0                                                # the cut rim
                run = runs(phi * r, Y, (top - 0.3, mouth + 5.9, mouth + 11.9, mouth + 17.9), seed, spacing=0.22, maxlen=4.5, every=2, w0=0.05)
                col, v = metal(mat, v, u + seed * 3, Y, x, y, seed, 0.45, z / F, run)
                if (Y - mouth) % 6.0 < 0.12: v += 0.8                                      # a seam band
                return shade(col, v, PX, Y, Z, nrm, x, y, z, gain=2.4)
            return sh
        cylinder(X, ORG_Z, r * 0.55, 3.8, 3.8 + 1.4, sh_of, n=10)                         # the conical foot (simplified)
        cylinder(X, ORG_Z, r, 3.8 + 1.4, top, sh_of, n=12)
        disc_top(X, top, ORG_Z, r * 0.8, lambda x, y, s, t, z, wp: (8, 8, 8), n=10)       # the dark open end
    # the vats' feed lines into the chest
    for sx in (-1, 1):
        pipe_path([(sx * 3.45, 1.6, 24.8), (sx * 4.6, 1.6, 30.0), (sx * 6.0, 1.6, ORG_Z - 1.3)], 0.6, v0=2.2, r=COPPER, rust=0.7, seed=120 + sx)
organ()

# ---------------------------------------------------------------------------------------------------- the boiler-vats
def vat_sh(cx, cz):
    def sof(p0, p1, nrm):
        def sh(x, y, s, t, z, wp):
            X, Y, Z = wp
            phi = p0 + (p1 - p0) * s
            u = phi * VR
            ps = z / F
            ph = phi + 0.1 * (cx / 3.45)
            if abs(ph) < 0.42 and 3.2 < Y < 8.6:                                           # the sight-glass
                fr = (0.42 - abs(ph)) * VR
                if fr < 0.2 or Y - 3.2 < 0.2 or 8.6 - Y < 0.2:
                    return shade(BRASS, 2.6 + (1.0 if Y > 8.4 or fr < 0.08 else 0), X, Y, Z, nrm, x, y, z, gain=1.5)
                if (Y - 3.2) % 1.35 < 0.13: return shade(BRASS, 1.8, X, Y, Z, nrm, x, y, z, gain=1.2)
                m = wn(0, u * 2.2 + cx, Y * 1.5) * 0.6 + wn(1, u * 6 + cx, Y * 5) * 0.4
                v = 1.6 + m * 5.2 + 1.6 * max(0.0, 1 - (Y - 3.2) / 1.6) - 0.8 * max(0.0, (Y - 7.0) / 1.6)
                if (x * 3 + y) % 11 == 0 and m > 0.6: v += 1.2                              # bubbles
                if fr < 0.45: v -= 1.0                                                     # the glass's shadowed rim
                return tone(FURN, v, x, y) if m > 0.44 else tone(CORAL, v + 1.0, x, y)
            v = 2.2 + (wn(3, u * 0.8 + cx, Y * 0.8) - 0.5) * 0.6
            cr = wn(5, u * 2.6 + cx, Y * 2.6) * 0.5 + wn(0, u * 0.9 + cx, 3.0) * 0.5 - Y * 0.16
            if cr > 0.36:                                                                   # rust coral crusting up from the plinth
                k = h32(int(u * 14), int(Y * 14), 3) % 4
                return shade(CORAL, 1.6 + k * 0.4 + (cr - 0.36) * 3, X, Y, Z, nrm, x, y, z, gain=1.2, tint=0.3)
            col = COPPER
            hoop = False
            for yb in (1.1, 5.9, 10.0):                                                     # riveted hoops
                if abs(Y - yb) < 0.26:
                    hoop = True
                    v += 0.7 if Y > yb else -0.4
                    if (u % 0.5) < 1.4 * ps: v += 1.0
            if (u % 3.2) < 0.9 * ps: v -= 1.1                                               # the plate seams
            elif (u % 3.2) < 3.0 * ps and (Y % 0.5) < 1.2 * ps: v += 1.0                    # rivets along them
            r_, _, pit = corrosion(u, Y, int(cx * 10), 0.45)
            vd = runs(u, Y, (9.75, 5.65), int(cx * 10) + 3, spacing=0.5, maxlen=3.6, every=3, w0=0.07)      # verdigris weeping from the hoops
            rn = runs(u, Y, (9.75, 5.65, 0.85), int(cx * 10), spacing=0.5, maxlen=2.4, every=2)          # rust from the rivets
            if not hoop and vd > 0.2 + (dith(x, y) + 0.5) * 0.3: col, v = VERD, v + 0.2 + vd * 0.8
            elif not hoop and rn > 0.15 + (dith(x, y) + 0.5) * 0.3: col, v = RUST, v + 0.1 + rn * 0.7
            elif r_ + dith(x, y) * 0.4 > 0.55: col, v = RUST, v + 0.3 + r_ * 0.4
            if pit: v -= 0.7
            return shade(col, v, X, Y, Z, nrm, x, y, z, gain=2.0)
        return sh
    return sof
for (cx, cz) in VAT:
    cylinder(cx, cz, VR + 0.4, 0, 0.75, lambda p0, p1, n: plate(IRON, 1.8, n, seed=4, amount=0.8, pw=1.2, ph=0.75), n=36)   # plinth
    cylinder(cx, cz, VR, 0.75, VH, vat_sh(cx, cz), n=44)
    for k in range(6):                                                                      # the dome, ring by ring
        y0, y1 = VH + k * 0.3, VH + (k + 1) * 0.3
        rr = VR * math.cos(math.asin(min(1.0, (k + 0.5) / 6.4)))
        cylinder(cx, cz, rr, y0, y1, lambda p0, p1, n, k=k: (lambda x, y, s, t, z, wp: shade(
            COPPER if wn(1, wp[0] * 3, wp[2] * 3) < 0.66 else VERD, 2.4 + k * 0.32 + (wn(3, wp[0] * 2, wp[2] * 2) - 0.5) * 0.8 + (0.8 if k == 0 and (x % 3 == 0) else 0),
            *wp, (n[0] * 0.75, 0.66, n[2] * 0.75), x, y, z, gain=2.2)), n=36)
    disc_top(cx, VH + 1.8, cz, VR * 0.42, lambda x, y, s, t, z, wp: shade(COPPER, 3.2, *wp, N_UP, x, y, z))
    sx = -1 if cx < 0 else 1
    # the feeding funnel: a corroded cone on a neck, mouth up, a crust of dried redmass down its side
    fx, fz = cx - sx * 0.7, cz - 0.9
    cylinder(fx, fz, 0.42, VH + 1.2, VH + 2.6, lambda p0, p1, n: plate(IRON, 2.2, n, seed=8, amount=0.9, pw=9, ph=9, rivets=False), n=12)
    for k in range(7):
        y0 = VH + 2.6 + k * 0.3
        cylinder(fx, fz, 0.5 + k * 0.3, y0, y0 + 0.3, lambda p0, p1, n, k=k: (lambda x, y, s, t, z, wp: (
            shade(CORAL, 1.8 + (h32(x, y) % 3) * 0.3, *wp, (n[0], 0.5, n[2]), x, y, z, gain=1.0, tint=0.3) if (abs(p0 + 0.3) < 0.3 and wn(2, wp[0] * 4, wp[1] * 2) > 0.5)
            else shade(RUST if wn(1, wp[0] * 5, wp[1] * 5 + k) > 0.45 else IRON, 2.6 + k * 0.18 + (0.9 if k == 6 else 0), *wp, (n[0], 0.5, n[2]), x, y, z, gain=2.0))), n=20)
    # a pressure gauge high on the front
    gx = cx + sx * -1.7
    gz = cz - math.sqrt(VR * VR - 1.7 * 1.7) - 0.2
    rs.disc(gx, 9.1, gz, 0.6, lambda x, y, s, t, z, wp: BRASS[4] if s * s + t * t > 0.62 else
            ((60, 20, 14) if abs(s * 0.55 + t * 0.83) < 0.1 and t < 0.05 and s > -0.1 else mix((176, 168, 140), (110, 104, 86), max(0.0, t))))
    rs.line3((gx, 8.5, gz + 0.05), (gx, 8.0, gz + 0.12), lambda x, y, s, t, z, wp: BRASS[2], w=0.18)
    # a valve wheel on the plinth side
    def wheel(x, y, s, t, z, wp):
        d = math.hypot(s, t)
        if 0.72 < d < 1.0 or (d < 1.0 and (abs(s) < 0.12 or abs(t) < 0.12)) or d < 0.22: return RUST[6] if t < 0 else RUST[3]
        return None
    rs.disc(cx + sx * (VR - 0.6), 2.0, cz - 1.8, 0.65, wheel)
    # pipes: up off the dome into the ceiling, and across to the walls at mid height
    pipe_path([(cx + sx * 1.3, VH + 1.0, cz + 0.6), (cx + sx * 1.3, 13.6, cz + 0.6), (cx + sx * 1.9, 14.6, cz + 2.0),
               (cx + sx * 2.4, 14.6, ORG_Z - 3.0), (cx + sx * 2.4, 3.8, ORG_Z - 1.6)], 0.7, v0=2.2, r=COPPER, rust=0.6, seed=11 + sx)
    pipe_path([(cx - sx * 0.6, VH + 1.4, cz + 1.4), (cx - sx * 0.6, 12.6, cz + 2.4), (cx - sx * 0.6, 12.6, ORG_Z - 2.4), (cx - sx * 0.6, 3.8, ORG_Z - 1.4)],
              0.42, v0=2.0, rust=0.9, seed=13 + sx)
    pipe_path([(cx + sx * VR * 0.75, 2.2, cz - 1.7), (cx + sx * (VR + 1.4), 2.2, cz - 1.7), (cx + sx * (VR + 1.4), 0.3, cz - 1.7),
               (sx * 11.2, 0.3, cz - 1.0)], 0.5, v0=2.0, rust=0.8, seed=15 + sx)
# the small canister left of the vats
cylinder(-8.6, 20.4, 1.15, 0, 3.8, lambda p0, p1, n: plate(IRON, 2.2, n, seed=31, amount=0.9, pw=1.2, ph=1.27), n=24)
disc_top(-8.6, 3.8, 20.4, 1.15, lambda x, y, s, t, z, wp: shade(IRON, 3.0, *wp, N_UP, x, y, z))
pipe_path([(-8.6, 3.8, 20.4), (-8.6, 5.0, 20.4), (-6.4, 5.0, 21.0)], 0.34, v0=2.6, rust=0.6, seed=33)

# rust coral (redmass bloom): branching stalks of blood-coloured steel climbing the plinths, a few tips alive
def coral(cx, cz, rad, n, seed, ymax=2.6, arc=1.7, glow=0.3):
    rng = random.Random(seed)
    for k in range(n):
        a = rng.uniform(-arc, arc)
        rr = rad + rng.uniform(-0.15, 0.35)
        X, Z = cx + math.sin(a) * rr, cz - math.cos(a) * rr
        stalk(X, 0.0, Z, rng.uniform(0.6, ymax), 0.16, rng, glow, depth=0, lean=math.sin(a) * 0.12)
def stalk(X, Y, Z, h, w, rng, glow, depth, lean):
    steps = max(2, int(h / 0.2))
    pts = [(X, Y, Z)]
    for j in range(steps):
        X += lean + rng.uniform(-0.06, 0.06); Y += h / steps; Z -= 0.01
        pts.append((X, Y, Z))
    for j, (a, b) in enumerate(zip(pts, pts[1:])):
        ww = w * (1 - j / steps * 0.6)
        rs.line3(a, b, lambda x, y, s, t, z, wp: shade(CORAL, 1.4 + (0.9 if (x + y) % 4 == 0 else 0) + h32(x, y) % 2 * 0.3, *wp, None, x, y, z, gain=0.9, tint=0.25), w=ww)
        if depth < 2 and j > 1 and rng.random() < 0.22:
            stalk(b[0], b[1], b[2], h * 0.45, ww * 0.7, rng, glow, depth + 1, lean + rng.choice((-0.14, 0.14)))
    tip = pts[-1]
    live = rng.random() < glow
    rs.disc(tip[0], tip[1], tip[2] - 0.02, w * 0.8 + 0.04,
            (lambda x, y, s, t, z, wp: tone(REDL, 5.0 - (s * s + t * t) * 2, x, y)) if live else
            (lambda x, y, s, t, z, wp, tip=tip: shade(CORAL, 2.8 - t, *tip, None, x, y, z, gain=0.9, tint=0.25)), cls='emit' if live else 'prop')
for (cx, cz) in VAT:
    coral(cx, cz, VR + 0.45, 8, int(cx * 7) + 5, ymax=1.3, arc=1.4, glow=0.12)
coral(-8.6, 20.4, 1.2, 10, 77, ymax=1.8, glow=0.2)
coral(0.0, ORG_Z - 1.3, 9.0, 10, 78, ymax=1.6, arc=0.9, glow=0.2)

# ---------------------------------------------------------------------------------------------------- the left bank
def crt(x0, x1, y0, y1, z0, z1, kind, seed):
    """a CRT terminal: a deep case, a curved green screen in a recessed bezel (the screen is its own emissive quad)"""
    def screen(x, y, s, t, z, wp):
        if not (0.11 < s < 0.89 and 0.15 < t < 0.85): return None
        u, v = (s - 0.5) / 0.39, (t - 0.5) / 0.35
        if u * u + v * v > 1.75: return None                                                # rounded corners
        if kind == 9: return fogged(tone(CABLE, 2.6 - (u * u + v * v) + (1.2 if -0.7 < u < -0.3 and v < -0.3 else 0), x, y), z)   # dead glass
        g = 2.8 - (u * u + v * v) * 1.4 + (0.5 if (y % 2) else 0)                           # scanlines, vignette
        if kind == 0 and (t * 11) % 1 < 0.38 and s < 0.2 + (h32(int(t * 11), seed) % 6) * 0.11: g += 2.6   # text rows
        if kind == 1 and abs(t - 0.5 - 0.22 * math.sin(s * 14 + seed)) < 0.035: g += 3.2               # a waveform
        if kind == 2 and (abs(math.hypot(s - 0.5, t - 0.5) - 0.2) < 0.02 or abs(s - 0.5) < 0.012 or abs(t - 0.5) < 0.016): g += 2.8
        if kind == 3 and (h32(int(s * 14), int(t * 10), seed) % 3 == 0) and (t * 10) % 1 < 0.6: g += 2.2    # readouts
        if s < 0.3 and t > 0.62 and (x + y) % 5 == 0: g += 1.0                               # a burnt-in ghost
        return tone(SCREEN, g, x, y)
    def front(n):
        def sh(x, y, s, t, z, wp):
            X, Y, Z = wp
            v = 2.2 + (wn(3, s * 6 + seed, t * 6) - 0.5) * 0.6
            if s < 0.05 or s > 0.95 or t < 0.06: v -= 0.6
            if 0.08 < s < 0.92 and 0.12 < t < 0.88: v -= 1.3                                  # the bezel's recess
            if t > 0.9 and 0.72 < s < 0.8: return tone(REDL, 4.6, x, y)                       # the power lamp
            if t > 0.9 and 0.2 < s < 0.5 and (s * 30) % 1 < 0.5: v += 0.7                     # knobs
            return shade(PAINT, v, X, Y, Z, n, x, y, z, gain=1.6)
        return sh
    rs.box(x0, x1, y0, y1, z0, z1, front(N_FRONT), flat(PAINT, 1.8, N_L if x1 < 0 else N_R),
           top=flat(PAINT, 2.4, N_UP) if y1 < CAMH else None, cls='prop')
    rs.quad((x0, y0, z0 - 0.03), (x1, y0, z0 - 0.03), (x0, y1, z0 - 0.03), screen, cls='prop' if kind == 9 else 'emit', cut=True)

def bench(x0, x1, z0, z1, seed):
    """a heavy steel workbench, its top crusted with solder and coral, a row of drawers"""
    def top(n):
        def sh(x, y, s, t, z, wp):
            X, Y, Z = wp
            v = 2.6 + (wn(3, X * 1.2 + seed, Z * 1.2) - 0.5) * 0.9
            if h32(int(X * 7), int(Z * 7), seed) % 13 == 0: return shade(BRASS, 4.0, X, Y, Z, n, x, y, z)     # solder beads
            if wn(1, X * 0.9 + seed, Z * 0.9) > 0.68: return shade(CORAL, 2.6 + (h32(x, y) % 3) * 0.5, X, Y, Z, n, x, y, z)
            return shade(IRON, v, X, Y, Z, n, x, y, z)
        return sh
    box(x0, x1, 2.7, 3.0, z0, z1, lambda n: plate(IRON, 2.8, n, seed=seed, amount=0.6, pw=30, ph=9, rivets=False), top=top)
    def front(n):
        def sh(x, y, s, t, z, wp):
            X, Y, Z = wp
            dw = (X - x0) / 2.1
            if 0.07 < dw % 1 < 0.93 and 1.25 < Y < 2.55:                                       # drawers
                if abs(Y - 2.1) < 0.1 and 0.4 < dw % 1 < 0.6: return shade(IRON, 3.6, X, Y, Z, n, x, y, z)   # the pull
                return plate(PAINT, 2.2, n, seed=seed + int(dw), amount=0.7, pw=2.1, ph=9, rivets=False)(x, y, s, t, z, wp)
            if Y < 1.25: return shade(IRON, 0.6, X, Y, Z, n, x, y, z)                          # dark under the bench
            return plate(IRON, 1.6, n, seed=seed, amount=0.5, rivets=False)(x, y, s, t, z, wp)
        return sh
    box(x0 + 0.3, x1 - 0.3, 0, 2.7, z0 + 0.3, z1, front)

def cabinet(x0, x1, y1, z0, z1, seed, dials=6):
    """a cabinet of the old plant: plate steel, a panel of round gauges and a row of toggles, rust running down"""
    pf = plate(PAINT, 1.9, N_FRONT, seed=seed, amount=0.8, pw=(x1 - x0) / 2, ph=2.6)
    def front(n):
        def sh(x, y, s, t, z, wp):
            X, Y, Z = wp
            gx, gy = (X - x0) / 1.3, (Y - (y1 - 3.6)) / 1.3
            if 0 <= gy < 2 and gx > 0.3 and int(gx) < dials:
                fx, fy = gx % 1 - 0.5, gy % 1 - 0.5
                d = math.hypot(fx, fy)
                if d < 0.36:                                                                  # a round gauge
                    ang = math.atan2(fy, fx); nd = (h32(int(gx), int(gy), seed) % 100) / 100 * 2.6 + 0.4
                    if d < 0.27 and abs(math.sin(ang - nd)) < 0.14 and math.cos(ang - nd) > 0: return (36, 22, 16)
                    if d < 0.29:
                        if h32(int(gx), int(gy), seed, 2) % 5 == 0: return shade(CABLE, 1.0, X, Y, Z, n, x, y, z)   # a smashed glass
                        return shade(DAY, 4.2 - d * 4 + (0.6 if fy < -0.1 else 0), X, Y, Z, n, x, y, z, gain=1.2)
                    return shade(BRASS, 3.0 + (0.8 if fy < 0 else 0), X, Y, Z, n, x, y, z)
            if abs(Y - (y1 - 4.4)) < 0.24 and x0 + 0.4 < X < x1 - 0.4:
                return shade(IRON, 4.0 if (X - x0) % 0.5 < 0.18 else 0.8, X, Y, Z, n, x, y, z)   # toggles
            return pf(x, y, s, t, z, wp)
        return sh
    box(x0, x1, 0, y1, z0, z1, front, side=lambda n: plate(PAINT, 1.6, n, seed=seed + 1, amount=0.85, horiz='z'),
        top=lambda n: plate(IRON, 2.4, n, seed=seed + 2, amount=0.9))

bench(-24.0, -11.4, 22.6, 25.6, 41)
crt(-21.0, -16.6, 3.0, 7.0, 23.0, 26.4, 0, 1)
crt(-15.6, -12.6, 3.0, 5.6, 23.4, 25.4, 1, 2)
box(-23.4, -22.0, 3.0, 3.9, 23.0, 24.0, lambda n: flat(IRON, 2.8, n))                       # the vice
box(-23.1, -22.3, 3.9, 4.3, 23.2, 23.8, lambda n: flat(IRON, 3.4, n))
for k in range(5):                                                                          # a hank of wire
    rs.line3((-13.0 + k * 0.1, 3.05, 23.2 + k * 0.05), (-11.8, 3.1 + k * 0.05, 23.6 + k * 0.1),
             lambda x, y, s, t, z, wp: fogged(COPPER[7 - (x + y) % 3], z), w=0.08)
cabinet(-29.6, -21.4, 11.0, 26.0, 30.0, 51, dials=6)
cabinet(-21.4, -12.2, 8.4, 27.2, 30.4, 53, dials=7)
crt(-19.4, -14.2, 8.4, 12.6, 27.6, 30.2, 2, 3)
crt(-26.0, -22.4, 11.0, 14.0, 26.8, 29.4, 3, 4)
rs.disc(-24.4, 11.8, 27.4, 0.5, lambda x, y, s, t, z, wp: tone(REDL, 6.4 - (s * s + t * t) * 3, x, y), cls='emit')   # the red beacon
box(-24.9, -23.9, 11.0, 11.4, 27.0, 27.8, lambda n: flat(IRON, 2.4, n))
pipe_path([(-17.0, 12.6, 29.0), (-17.0, 20.0, 29.0), (-20.0, 23.0, 30.5), (-WX + 1.8, 23.0, 30.5)], 0.6, v0=2.0, rust=0.8, seed=21)
pipe_path([(-27.0, 14.0, 28.4), (-27.0, CH - 0.5, 28.4)], 0.8, v0=1.8, rust=0.9, seed=23)
pipe_path([(-WX + 0.5, 6.0, 12.0), (-WX + 0.5, 6.0, 44.0)], 0.7, v0=1.6, rust=0.9, seed=25)
pipe_path([(-WX + 0.5, 8.4, 12.0), (-WX + 0.5, 8.4, 44.0)], 0.45, v0=1.8, rust=0.7, seed=27)

def runnel(X, Z, seed, pool=1.2):
    """redmass seeping over the bench's edge in a glowing runnel, pooling on the deck"""
    rng = random.Random(seed)
    pts = [(X, 3.0, Z)]
    Y = 3.0
    while Y > 0.05:
        Y -= 0.3; X += rng.uniform(-0.05, 0.05)
        pts.append((X, max(0.02, Y), Z - 0.05))
    for j, (a, b) in enumerate(zip(pts, pts[1:])):
        wj = 0.1 + 0.06 * (j % 3 == 0) + (0.12 if j == 0 else 0)                          # beads along the trickle, a lip at the edge
        rs.line3(a, b, lambda x, y, s, t, z, wp, j=j: tone(CORAL, 4.6, x, y) if (x + j) % 3 == 0 else tone(REDL, 2.8 + (h32(x, y) % 3) * 0.4, x, y), w=wj, cls='emit')
    def pool_sh(x, y, s, t, z, wp):
        PX, _, PZ = wp
        d = math.hypot((PX - X) / pool, (PZ - Z + 0.6) / (pool * 0.7)) + 0.3 * (wn(2, PX * 3, PZ * 3) - 0.5)
        if d > 1: return None
        return tone(REDL, 4.0 - d * 2.4, x, y) if d < 0.75 else tone(CORAL, 2.6, x, y)
    rs.quad((X - pool, 0.03, Z - 0.6 - pool * 0.7), (X + pool, 0.03, Z - 0.6 - pool * 0.7), (X - pool, 0.03, Z - 0.6 + pool * 0.7),
            pool_sh, cls='emit', cut=True)
runnel(-18.6, 22.55, 5, 1.0); runnel(-14.2, 22.55, 6, 0.7)

# the scrap altar: a cog wheel stood on a pile of stripped plates, a dead terminal, offerings of bolts and a red lamp
def altar(X, Z):
    box(X - 1.9, X + 1.9, 0, 1.0, Z - 1.2, Z + 1.2, lambda n: plate(IRON, 2.2, n, seed=301, amount=1.0, pw=0.9, ph=0.5))
    box(X - 1.5, X + 1.4, 1.0, 1.7, Z - 0.9, Z + 1.0, lambda n: plate(PAINT, 2.2, n, seed=302, amount=1.0, pw=1.1, ph=0.35))
    box(X - 1.1, X + 1.1, 1.7, 2.2, Z - 0.6, Z + 0.8, lambda n: plate(COPPER, 2.4, n, seed=303, amount=0.9, pw=0.8, ph=0.25))
    def cog(x, y, s, t, z, wp):
        d = math.hypot(s, t); a = math.atan2(t, s)
        teeth = 0.86 + (0.14 if (a * 12 / math.pi) % 2 < 1 else 0)
        if d > teeth: return None
        if 0.38 < d < 0.66 and abs(math.sin(a * 3)) > 0.35: return None                       # spokes and holes
        if d < 0.16: return None
        v = 3.0 - t * 1.4 - s * 0.6 + (0.8 if d > 0.82 else 0)
        col = RUST if wn(1, s * 3 + 4, t * 3) > 0.42 else IRON
        return shade(col, v, X, 4.4, Z, None, x, y, z, gain=1.8)
    rs.disc(X, 4.3, Z + 0.3, 2.1, cog)
    crt(X - 0.9, X + 0.7, 2.2, 3.5, Z - 0.5, Z + 0.7, 9, 8)                                # a dead terminal (dark screen)
    for k in range(9):                                                                        # bolts and nuts laid out
        bx = X - 1.6 + k * 0.4; bz = Z - 1.35 - (k % 2) * 0.12
        rs.disc(bx, 1.05, bz, 0.09, lambda x, y, s, t, z, wp: BRASS[4] if t < 0 else BRASS[1])
    rs.disc(X + 1.5, 1.55, Z - 0.6, 0.24, lambda x, y, s, t, z, wp: tone(REDL, 6.0 - (s * s + t * t) * 2, x, y), cls='emit')
    rs.line3((X + 1.5, 1.0, Z - 0.6), (X + 1.5, 1.32, Z - 0.6), lambda x, y, s, t, z, wp: IRON[3], w=0.2)
altar(-14.6, 19.0)

# ---------------------------------------------------------------------------------------------------- the right bank
bench(11.4, 24.0, 22.6, 25.6, 61)
crt(16.4, 20.8, 3.0, 7.0, 23.0, 26.4, 3, 5)
crt(12.4, 15.2, 3.0, 5.4, 23.2, 25.2, 1, 6)
for k in range(3):                                                                          # a stack of stripped circuit boards
    box(21.4, 23.4, 3.0 + k * 0.14, 3.12 + k * 0.14, 23.2 + k * 0.05, 24.6, lambda n, k=k: flat(VERD, 3.0 + k * 0.3, n))
def ac_front(n):
    pa = plate(OCHRE, 2.4, n, seed=71, amount=0.9, pw=4.0, ph=3.0)
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        fx, fy = X - 16.2, Y - 5.6
        d = math.hypot(fx, fy)
        if d < 2.6:                                                                           # the fan grille
            if d > 2.35: return shade(IRON, 3.0, X, Y, Z, n, x, y, z)
            a = math.atan2(fy, fx)
            if (d * 3.2) % 1 < 0.28: return shade(IRON, 2.4 + (0.6 if fy > 0 else 0), X, Y, Z, n, x, y, z)
            if abs(math.sin(a * 3 + d * 0.8)) < 0.22 and d > 0.4: return shade(IRON, 1.6, X, Y, Z, n, x, y, z)   # the blades behind
            if d < 0.45: return shade(IRON, 2.2, X, Y, Z, n, x, y, z)
            return shade(CABLE, 0.6, X, Y, Z, n, x, y, z)
        if Y < 2.6 and (Y * 3.0) % 1 < 0.35: return shade(IRON, 0.9, X, Y, Z, n, x, y, z)     # louvres
        return pa(x, y, s, t, z, wp)
    return sh
box(12.2, 20.2, 0, 9.0, 27.0, 31.0, ac_front, side=lambda n: plate(OCHRE, 1.8, n, seed=72, amount=0.9, horiz='z'),
    top=lambda n: plate(IRON, 2.4, n, seed=73, amount=1.0))
crt(13.6, 18.2, 9.0, 12.6, 27.4, 30.4, 0, 7)
def rack_front(n):
    pr = plate(PAINT, 1.6, n, seed=81, amount=0.6, pw=9, ph=0.71, rivets=False)
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        if (Y * 1.4) % 1 < 0.1: return shade(IRON, 0.8, X, Y, Z, n, x, y, z)
        return pr(x, y, s, t, z, wp)
    return sh
def rack_lamps(x, y, s, t, z, wp):
    X, Y, Z = wp
    if 0.5 < (Y * 1.4) % 1 < 0.72 and ((X - 20.5) * 3.0) % 1 < 0.45 and h32(int(Y * 1.4), int((X - 20.5) * 3), 5) % 3:
        k = h32(int(Y * 1.4), int((X - 20.5) * 3), 9) % 6
        return tone(SCREEN, 5.6, x, y) if k < 2 else (tone(REDL, 4.6, x, y) if k == 2 else (tone(FURN, 6.0, x, y) if k == 3 else None))
    return None
box(20.4, 27.4, 0, 12.4, 26.2, 30.0, rack_front, side=lambda n: plate(PAINT, 1.4, n, seed=82, amount=0.7, horiz='z'))
rs.quad((20.9, 0.5, 26.17), (26.9, 0.5, 26.17), (20.9, 12.0, 26.17), rack_lamps, cls='emit', cut=True)
pipe_path([(16.0, 12.6, 29.0), (16.0, 21.0, 29.0), (WX - 1.8, 21.0, 29.0)], 0.6, v0=2.0, rust=0.8, seed=31)
pipe_path([(24.0, 12.4, 28.0), (24.0, CH - 0.5, 28.0)], 0.7, v0=1.8, rust=0.9, seed=33)
pipe_path([(WX - 0.5, 5.0, 12.0), (WX - 0.5, 5.0, 44.0)], 0.8, v0=1.6, rust=0.9, seed=35)
runnel(19.0, 22.55, 7, 0.9)

# ---------------------------------------------------------------------------------------------------- the near clutter
def drum(X, Z, seed, h=3.0, r=1.05):
    pd = plate(DRUMP if seed % 2 else PAINT, 2.2, N_FRONT, seed=seed, amount=0.9, pw=9, ph=9, rivets=False)
    def sof(p0, p1, n):
        def sh(x, y, s, t, z, wp):
            Y = wp[1]
            if min(abs(Y - h * 0.33), abs(Y - h * 0.66)) < 0.1: return shade(IRON, 3.0, *wp, n, x, y, z)          # the rolling hoops
            if Y > h - 0.12: return shade(IRON, 3.4, *wp, n, x, y, z)
            c = pd(x, y, s, t, z, wp)
            return c
        return sh
    cylinder(X, Z, r, 0, h, sof, n=22)
    disc_top(X, h, Z, r, lambda x, y, s, t, z, wp: shade(IRON, 2.8 + (1.0 if math.hypot(wp[0] - X - 0.45, wp[2] - Z) < 0.18 else 0)
                                                           - (0.6 if math.hypot(wp[0] - X, wp[2] - Z) > r - 0.12 else 0), *wp, N_UP, x, y, z))
drum(-22.6, 17.4, 1); drum(-20.2, 18.4, 2, h=2.8); drum(-24.4, 19.8, 3)
box(-WX, -25.4, 0, 2.6, 16.0, 18.8, lambda n: plate(WOODR, 2.8, n, seed=91, amount=0.3, pw=0.7, ph=9, rivets=False))
box(-29.4, -26.0, 2.6, 4.4, 16.6, 18.6, lambda n: plate(WOODR, 3.0, n, seed=92, amount=0.3, pw=0.6, ph=9, rivets=False))
box(19.0, 25.6, 0, 2.5, 17.2, 19.8, lambda n: plate(WOODR, 2.8, n, seed=93, amount=0.3, pw=0.7, ph=9, rivets=False))
def coil(cx, cy, cz, r, turns, w, seed):
    """a coil of heavy cable lying flat, turn on turn"""
    for k in range(turns):
        yy = cy + k * w * 0.85
        rr = r - k * 0.05 + (h32(seed, k) % 3) * 0.05
        n = 36
        pts = [(cx + rr * math.cos(2 * math.pi * i / n), yy + 0.04 * math.sin(i * 1.3 + k), cz + rr * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            front = math.sin(2 * math.pi * (i + 0.5) / n) < 0                                    # the near half of the turn
            def sh(x, y, s, t, z, wp, front=front, k=k):
                sx, sy = proj(*wp); rr_ = max(0.5, w * F / z / 2)
                acr = (y + 0.5 - sy) / rr_
                v = 2.0 + (1.2 if acr < -0.3 else 0) - (0.8 if acr > 0.5 else 0) + (0.4 if front else -0.4)
                return shade(CABLE, v, *wp, None, x, y, z, gain=1.6)
            rs.line3(a, b, sh, w=w)
coil(22.4, 2.7, 18.6, 2.2, 5, 0.42, 1); coil(27.4, 0.2, 18.0, 1.9, 4, 0.4, 2); coil(23.4, 0.2, 21.6, 1.6, 3, 0.36, 3)
drum(18.0, 20.8, 4, h=3.2)

def cable(pts, w, seed, rise=0.06):
    """a cable snaking over the deck"""
    rng = random.Random(seed)
    path = []
    for a, b in zip(pts, pts[1:]):
        n = int(math.dist(a, b) / 0.35) + 1
        for i in range(n):
            t = i / n
            path.append((a[0] + (b[0] - a[0]) * t + rng.uniform(-0.1, 0.1), a[1] + (b[1] - a[1]) * t + rise,
                         a[2] + (b[2] - a[2]) * t + rng.uniform(-0.1, 0.1)))
    path.append(pts[-1])
    def sh(x, y, s, t, z, wp):
        sx, sy = proj(*wp); rr_ = max(0.5, w * F / z / 2)
        acr = (y + 0.5 - sy) / rr_
        return shade(CABLE, 2.0 + (1.3 if acr < -0.2 else 0) - (0.6 if acr > 0.5 else 0), *wp, None, x, y, z, gain=1.8)
    for a, b in zip(path, path[1:]):
        rs.line3(a, b, sh, w=w)
cable([(-5.8, 0, 20.0), (-9.0, 0, 18.0), (-12.6, 0, 18.6), (-17.0, 0, 21.4), (-18.0, 0, 22.4)], 0.3, 1)
cable([(-4.0, 0, 19.2), (-6.0, 0, 16.4), (-11.0, 0, 15.6), (-17.0, 0, 16.2), (-26.0, 0, 15.0)], 0.32, 2)
cable([(5.4, 0, 19.6), (8.6, 0, 17.4), (13.0, 0, 18.0), (16.4, 0, 22.4)], 0.3, 3)
cable([(3.6, 0, 19.0), (6.4, 0, 15.8), (12.0, 0, 15.2), (19.0, 0, 16.6), (25.0, 0, 15.0)], 0.34, 4)
cable([(-1.0, 0, 19.2), (-0.6, 0, 17.6), (1.4, 0, 17.0), (2.2, 0, 19.0)], 0.26, 5)
cable([(-7.4, 0, 20.4), (-7.8, 0, 24.0), (-10.4, 0, 27.0)], 0.3, 6)
cable([(7.0, 0, 21.0), (9.6, 0, 26.0), (12.0, 0, 27.4)], 0.3, 7)

# ---------------------------------------------------------------------------------------------------- the grated walk
def grate_sh(x, y, s, t, z, wp):
    X, _, Z = wp
    ps = z / F
    e = min(X - GRATE[0], GRATE[1] - X)
    if e < 0.4: return shade(IRON, 2.6 + (0.9 if e > 0.28 else 0), X, 0, Z, N_UP, x, y, z)          # the channel frame
    bar = (X % 0.42) < max(0.12, 1.0 * ps) or (Z % 1.4) < max(0.16, 1.0 * z * z / (F * CAMH))
    if bar:
        col, v = metal(IRON, 2.4 + (0.7 if (Z % 1.4) < 0.08 else 0), X, Z, x, y, 23, 0.5, ps)
        return shade(col, v, X, 0, Z, N_UP, x, y, z, gain=2.4)
    g = 0.5 + 2.2 * math.exp(-((X - 1.0) ** 2) / 8.0) * (0.5 + 0.5 * wn(2, X * 0.5, Z * 0.45)) - max(0.0, (Z - 13.0) * 0.4)
    return tone(FURN, g, x, y) if g > 1.0 else tone(CABLE, g + 1.4, x, y)                         # the crypts' glow below
rs.quad((GRATE[0], 0.01, GRATE[2]), (GRATE[1], 0.01, GRATE[2]), (GRATE[0], 0.01, GRATE[3]), grate_sh, cls='emit')

# ---------------------------------------------------------------------------------------------------- the ceiling's hangings
def chain(X, Z, y1, seed):
    def sh(x, y, s, t, z, wp):
        Y = wp[1]
        if (Y * 2.6) % 1 < 0.22: return None
        return shade(RUST if h32(int(Y * 2.6), seed) % 3 else IRON, 2.6 + (0.8 if (Y * 2.6) % 1 > 0.7 else 0), *wp, None, x, y, z, gain=1.6)
    rs.line3((X, CH - 1.8, Z), (X, y1, Z), sh, w=0.16)
    rs.line3((X, y1, Z), (X + 0.3, y1 - 0.5, Z), lambda x, y, s, t, z, wp: fogged(IRON[4], z), w=0.12)        # the hook
rng = random.Random(9)
for k in range(34):
    X = rng.uniform(-25, 25); Z = rng.choice((30.3, 44.7, 58.7, 72.7)) + rng.uniform(-0.2, 0.5)
    if abs(X) < 7.5 and Z < 50: continue
    chain(X, Z, rng.uniform(15, 25), k)
for k, (a, b, sag) in enumerate((((-22, CH - 2.2, 29.6), (-6, CH - 2.2, 29.6), 4.0), ((6, CH - 2.2, 29.6), (24, CH - 2.2, 29.6), 3.0),
                                 ((-26, CH - 2.2, 58.0), (-12, CH - 2.2, 58.0), 3.4), ((10, CH - 2.2, 58.0), (26, CH - 2.2, 58.0), 4.4),
                                 ((-10, CH - 1.8, 18.0), (-10, CH - 1.8, 34.0), 5.0), ((10, CH - 1.8, 20.0), (10, CH - 1.8, 40.0), 6.0),
                                 ((-26, CH - 2.2, 44.0), (-14, CH - 2.2, 44.0), 2.6))):
    rs.line3(a, b, lambda x, y, s, t, z, wp: shade(CABLE, 2.2 + (0.8 if (x + y) % 6 == 0 else 0), *wp, None, x, y, z, gain=1.4), w=0.3, sag=sag)
for (yy, zz, w_, sd) in ((26.6, 20.6, 0.9, 41), (27.8, 21.4, 0.6, 42)):                    # a pipe run across the hall, near the camera
    pipe_path([(-WX, yy, zz), (-9.0, yy, zz), (-8.6, yy, zz + 0.0), (WX, yy, zz)], w_, v0=1.6, rust=0.8, seed=sd)
for X0 in (-23.0, -17.0, 15.0, 22.0):
    rs.line3((X0, 26.2, 20.6), (X0 + 4.0, 26.2, 20.6), lambda x, y, s, t, z, wp: shade(CABLE, 2.0, *wp, None, x, y, z, gain=1.2), w=0.24, sag=2.6 + (X0 % 3))
def cage_lamp(X, Y, Z):
    """a caged work lamp hanging on its cord, a tin shade over it"""
    rs.line3((X, Y + 0.9, Z), (X, CH - 1.8, Z), lambda x, y, s, t, z, wp: shade(CABLE, 2.0, *wp, None, x, y, z), w=0.1)
    rs.disc(X, Y, Z, 0.8, lambda x, y, s, t, z, wp: (tone(FURN, 7.8 - (s * s + t * t) * 3.0, x, y) if (int((s + 1) * 4) % 2 or t > 0.45) else BRASS[1]), cls='emit')
    rs.quad((X - 1.4, Y + 0.55, Z - 0.4), (X + 1.4, Y + 0.55, Z - 0.4), (X - 1.4, Y + 1.3, Z - 0.4),
            lambda x, y, s, t, z, wp: fogged(BRASS[3 if t > 0.55 else 1], z) if t < 1 - abs(s - 0.5) * 1.3 else None, cut=True)
cage_lamp(-12.0, 17.2, 21.0); cage_lamp(13.0, 18.2, 24.5)


# ---------------------------------------------------------------------------------------------------- post: the light shaft
def post(col, cls):
    """volumetric haze: the shaft of daylight from the broken ceiling (marched along each view ray up to the pixel's
    depth) with rust dust hanging in it"""
    x0, x1 = int(proj(-12, CH, 30)[0]), int(proj(12, CH, 30)[0])
    for y in range(0, 470):
        for x in range(x0, x1):
            g = rs.G[y][x]
            zmax = rs.ZB[y][x] if g is not None else 200.0
            dx, dy = ray(x, y)
            acc = 0.0
            for i in range(30):
                z = 29.0 + i * 0.55
                if z >= zmax: break
                acc += beam_at(dx * z, CAMH + dy * z, z) * 0.55
            if acc <= 0: continue
            a = min(0.5, acc * 0.085)
            c = col[y][x]
            col[y][x] = mix(c, DAY[6], a)
            if h32(x, y, 77) % 61 == 0 and acc > 1.2: col[y][x] = mix(col[y][x], RUST[10], 0.7)   # a mote of rust dust in the light

img = rs.render(INK, fog=fog, post=post, mirror=lambda x, y, wp: 0.42 * oil(wp[0], wp[2]),
                light_gain=0.8, grime_gain=0.7, bloom=0.5, stain_gain=0.3, damp_gain=0.3)
img.save(f'{OUT}/rust.png')
print('done rust')
