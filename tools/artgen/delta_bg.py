"""The Echo Drain Delta (EchoDrainDeltaScene), 1067x600, overcast day, the shared camera (raster3d.py via waterkit).
After the old art (EchoDrainDelta.png): where the city's runoff fans out into a delta of silt, scrap and dead works.
The near bank of mud and rushes is the walk line; murky water with slow dark currents and an oily skin runs off between
islets into the haze. On the left islet a ruined brick drain-house carries a tall timber lattice tower with two giant
corroded horns -- the echo drains -- breathing faint rings onto the water below them. On the right the distant island:
a ruined pump-house with a smoking chimney, big pipes bent down into the water, faint orange-red crystal growths pulsing
in its pipes (the redmass), and a leaning tower with one horn turned toward the bank. Behind, the silhouettes of more
dead works in the haze. On the near left a broken concrete wall stands in the mud (Palinode's seam is in its crack);
a spit of half-sunk masonry runs from the bank toward the island (the seam crossing). No mushrooms (the fungal bridge,
grown from the player's spores, is its own sprite), no people.

    python3 delta_bg.py <outdir>   ->  delta.png         (assets/images/backgrounds/EchoDrainDelta.png)
                                       delta_bridge.png  (assets/images/props/delta_bridge.png  -- the fungal bridge)
                                       delta_scrap.png   (assets/images/props/delta_scrap.png   -- the Metal Scrap pickup)
Each sprite is the scene rendered once more with it, cut out where it changed (incl. its reflection); the script prints
where each goes (top-left, canvas) and the scene's other fixed points."""
import sys, math
from PIL import Image
from common import h32, ramp, make_noise
from shedkit import *
from waterkit import WRaster, timber, ironround, roundlit, frustum, ALGAE, SILT, REED, LIGHT

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = WRaster()
WL = -0.45                                                                         # the water (the near bank is Y 0)
MURK = ramp('#0f1412 #141b18 #1a231f #212c27 #29352f #323f37 #3c4940 #47544a')     # murky delta water
IRON = ramp('#121210 #1b1a17 #25231f #302d28 #3c3832 #4a453d #5a5449')
BRICK = ramp('#1f1411 #2c1b16 #3a241d #4a2e24 #5a392c #6b4535 #7c5240')
HORN = ramp('#14100c #1e1711 #2a2016 #372a1c #453522 #54412a #644e33')             # corroded bronze-iron of the horns
VERD = ramp('#18241f #20302a #2b3d35 #374b41 #455a4d')                             # verdigris on them
CRYST = ramp('#3a0e0a #5c1a10 #842a16 #a8401e #c85a28 #e07a3a #f0a058')            # the redmass glow
FOGSKY = ramp('#18221f #1e2a27 #25322e #2c3a35 #34433c #3d4c44 #46554c #506055 #5b6a5e #677466 #727d6e')

# ---------------------------------------------------------------------------------------------------- sky
_c1, _c2 = make_noise(13, 81, W, H), make_noise(47, 82, W, H)
def delta_sky(x, y, s=0, t=0, z=0, wp=None):
    tt = max(0.0, min(1.0, y / HY))
    v = 2.8 + 6.8 * tt ** 1.4 + (_c2(x * 0.5, y * 2.8) - 0.5) * 2.2 + (_c1(x * 0.5, y * 2.4) - 0.5) * 0.7
    c = tone(FOGSKY, v, x, y)
    if tt > 0.7: c = mix(c, (96, 102, 84), ((tt - 0.7) / 0.3) ** 2 * 0.3)       # a yellowish smog over the works
    return c
rs.quad((-1400, 800, 600), (1400, 800, 600), (-1400, -300, 600), delta_sky, cls='sky')

# ---------------------------------------------------------------------------------------------------- the water
ECHO = [(-40.0, 47.0, 1.0), (14.0, 43.0, 0.6)]                                     # (X, Z, strength): rings under the horns
def murk(x, y, s, t, z, wp):
    """dark slow water: a current drawn out in long streaks toward the haze, an oily skin, green scum near the banks,
    faint rings spreading from under the horns"""
    X, _, Z = wp
    near = min(1.0, 24.0 / Z)
    flow = wn(0, X * 0.08 + Z * 0.02, Z * 0.35)                                    # streaks running along the channel
    v = 3.0 + (flow - 0.5) * 2.2 * near + (1 - near) * 1.0 + (wn(1, X * 0.6, Z * 1.6) - 0.5) * 0.6
    P = 0.45 + Z * 0.02
    th = Z * Z / (F * (CAMH - WL)) / P
    if (Z / P) % 1 < th * 1.1 and h32(int(X / (1.2 + Z * 0.05)), int(Z / P), 9) % 5 == 0: v += 1.3
    for (ex, ez, k) in ECHO:                                                       # the echo rings
        d = math.hypot(X - ex, (Z - ez) * 1.0)
        if 3 < d < 26:
            ring = abs(((d - 3) / 3.2) % 1 - 0.5)
            if ring < 0.06 + Z * 0.0015: v += 1.1 * k * (1 - d / 26)
    c = tone(MURK, v, x, y)
    m = wn(3, X * 0.3, Z * 0.9)                                                    # oil skin
    if 0.6 < m < 0.64: c = mix(c, [MAUVE[3], TEAL[4], OCHRE[3]][int(m * 400) % 3], 0.25 * near)
    sc = shore_dist(X, Z)                                                          # green scum along the banks
    if sc < 3.0:
        a = (1 - sc / 3.0) * (0.4 + 0.6 * wn(2, X * 1.4, Z * 1.4))
        if a > 0.35: c = mix(c, tone(ALGAE, 2.6 + a * 2, x, y), min(0.85, (a - 0.35) * 2.4))
    return fogged(c, z)

# ---------------------------------------------------------------------------------------------------- the near bank, the islands
def near_shore(X):
    """the near bank's waterline (z) along X: it reaches back on the left (round the broken wall), comes close on the right"""
    return 17.6 + 9.0 * max(0.0, min(1.0, (-X - 10) / 14.0)) + 1.4 * (wn(1, X * 0.18, 7.0) - 0.5) + 0.6 * math.sin(X * 0.21)
ISLES = [  # (cx, cz, rx, rz, seed): islets of silt and rubble, an ellipse with a ragged edge
    (-48.0, 50.0, 30.0, 9.0, 1),      # the twin-horn tower's islet
    (40.0, 50.0, 30.0, 9.5, 2),       # the redmass island
    (-6.0, 92.0, 16.0, 4.0, 3), (70.0, 110.0, 30.0, 5.0, 4), (-95.0, 120.0, 40.0, 6.0, 5), (20.0, 160.0, 26.0, 5.0, 6),
]
def isle_in(X, Z, isle):
    cx, cz, rx, rz, sd = isle
    d = math.hypot((X - cx) / rx, (Z - cz) / rz)
    return d < 1.0 + (wn(2, X * 0.15 + sd * 10, Z * 0.3) - 0.5) * 0.45
def shore_dist(X, Z):
    """roughly how far the water point (X, Z) is from land, in units"""
    d = max(0.0, Z - near_shore(X))
    for (cx, cz, rx, rz, sd) in ISLES:
        e = math.hypot((X - cx) / rx, (Z - cz) / rz)
        d = min(d, max(0.0, (e - 1.0) * min(rx, rz * 2.2)))
    return d
rs.water(WL, -1400, 1400, 3, 590, murk, strength=lambda X, Z: 0.42 + 0.3 * (1 - min(1.0, 24.0 / Z)), wobble=1.6)

def bank_puddle(X, Z):
    if Z > near_shore(X) - 1.0: return 0.0
    m = wn(2, X * 0.22 + 3.0, Z * 1.1) + (wn(3, X * 2.0, Z * 2.0) - 0.5) * 0.14
    return max(0.0, min(1.0, (m - 0.74) * 10))

def mud(x, y, s, t, z, wp, wet_edge=None):
    """silt and mud, trodden, with stones, scrap bits and rust stains; wetter (and glossier) toward the water"""
    X, _, Z = wp
    v = 3.4 + (wn(0, X * 0.3, Z * 0.3) - 0.5) * 0.9 + (wn(1, X * 1.6, Z * 1.6) - 0.5) * 0.5
    rip = math.sin(Z * 4.2 + X * 0.25 + wn(2, X * 0.4, Z * 0.4) * 7)               # ripple marks the water left in the silt
    if rip > 0.75 and Z < 30: v += 0.6
    elif rip < -0.8 and Z < 30: v -= 0.5
    if Z < 17 and wn(0, X * 0.16 + 40, Z * 0.3) > 0.52:                        # drier crust, cracked into plates
        cx_, cz_ = math.floor(X / 0.9), math.floor(Z / 0.9)
        d1 = d2 = 9.0
        for i_ in (-1, 0, 1):
            for j_ in (-1, 0, 1):
                hh = h32(cx_ + i_, cz_ + j_, 77)
                px_ = (cx_ + i_ + (hh % 100) / 100) * 0.9; pz_ = (cz_ + j_ + (hh // 100 % 100) / 100) * 0.9
                d = math.hypot(X - px_, (Z - pz_) * 1.0)
                if d < d1: d1, d2 = d, d1
                elif d < d2: d2 = d
        if d2 - d1 < 0.04 + z / F * 1.2: v -= 1.4
        else: v += 0.5
    c = tone(SILT, v, x, y)
    pd = bank_puddle(X, Z) if wet_edge is not None else 0.0
    if pd: c = mix(c, (24, 28, 26), pd * 0.5)
    if wet_edge is not None:
        dw = wet_edge(X, Z)
        if dw < 2.0: c = mix(c, (22, 24, 20), (1 - dw / 2.0) * 0.55)
    return fogged(c, z)
def bank(x, y, s, t, z, wp):
    X, _, Z = wp
    if Z > near_shore(X): return None
    return mud(x, y, s, t, z, wp, wet_edge=lambda X, Z: near_shore(X) - Z)
rs.quad((-140, 0, 3), (140, 0, 3), (-140, 0, 40), bank, cls='ground', cut=True)
for isle in ISLES:
    cx, cz, rx, rz, sd = isle
    yl = 0.25 if cz < 80 else 0.6
    def isle_sh(x, y, s, t, z, wp, isle=isle):
        X, _, Z = wp
        if not isle_in(X, Z, isle): return None
        return mud(x, y, s, t, z, wp)
    rs.quad((cx - rx * 1.4, yl, cz - rz * 1.4), (cx + rx * 1.4, yl, cz - rz * 1.4), (cx - rx * 1.4, yl, cz + rz * 1.4), isle_sh, cls='ground', cut=True)
# rushes: clumps along the waterlines (thin blades, dry pale tips)
def rushes(cx, cz, n, h, seed, spread=1.6):
    for k in range(n):
        X = cx + ((h32(seed, k, 1) % 1000) / 1000 - 0.5) * spread * 2
        Z = cz + ((h32(seed, k, 2) % 1000) / 1000 - 0.5) * spread
        hh = h * (0.55 + (h32(seed, k, 3) % 100) / 220)
        lean = ((h32(seed, k, 4) % 100) / 100 - 0.5) * hh * 0.35
        tip = (h32(seed, k, 5) % 3 == 0)
        def blade(x, y, s, t, z, wp, tip=tip):
            v = 1.5 + s * 2.1 + (0.9 if tip and s > 0.75 else 0) + (wn(1, wp[0] * 4, 1.0) - 0.5)
            return fogged(tone(REED, v - abs(t) * 0.6, x, y), z)
        rs.beam((X, 0.0, Z), (X + lean, hh, Z), 0.09, blade, w1=0.03)
        if h32(seed, k, 6) % 7 == 0:                                               # a bulrush head
            rs.beam((X + lean * 0.8, hh * 0.78, Z), (X + lean * 0.86, hh * 0.9, Z), 0.16, lambda x, y, s, t, z, wp: fogged(tone(WARM, 1.6 - t * 0.5, x, y), z))
for i in range(28):                                                                # along the near bank
    X = -62 + i * 4.6 + (h32(i, 1) % 7) * 0.4
    if 3 < X < 24 or h32(i, 4) % 4 == 0: continue                                  # keep the landing at the bridge clear
    rushes(X, near_shore(X) - 0.6, 16 + h32(i, 2) % 14, 2.2 + (h32(i, 3) % 5) * 0.45, i)
for i, (cx, cz) in enumerate(((-70, 45), (-24, 48), (-60, 56), (18, 44), (62, 46), (70, 54), (30, 41.5))):
    rushes(cx, cz, 14, 3.0, 50 + i, spread=2.6)
for i in range(6):                                                                 # a few clumps on the near bank's front edge
    X = [-44, -30, 30, 42, 50, -52][i]
    rushes(X, 6.0 + (h32(i, 8) % 30) / 10, 8, 2.0, 80 + i, spread=1.2)

def stone(X, Z, r, seed):
    """a flat, rounded stone half sunk in the silt"""
    rs.disc(X, r * 0.25, Z, r, lambda x, y, a, b, z, wp: (fogged(tone(STONE, 4.0 - b * 1.6 - a * 0.7 + (wn(1, x * 0.5 + seed, y * 0.5) - 0.5) * 0.8, x, y), z)
                                                            if b < 0.45 - 0.2 * a * a else None))
def driftwood(P0, P1, w, seed):
    rs.beam(P0, P1, w, timber(2.6, WOOD, seed=seed), cap=True)
driftwood((-24.0, 0.2, 16.4), (-19.5, 0.25, 17.4), 0.45, 1); driftwood((-21.0, 0.15, 17.2), (-19.8, 0.5, 16.6), 0.22, 2)
driftwood((-3.0, 0.18, 15.6), (1.6, 0.2, 16.6), 0.4, 3); driftwood((24.0, 0.2, 16.2), (28.0, 0.22, 15.6), 0.4, 4)
for (cx, cz, n, h) in ((-17.0, 11.4, 26, 3.6), (-13.0, 12.6, 12, 2.6), (17.4, 11.6, 30, 3.8), (13.6, 12.8, 10, 2.4)):   # tall clumps framing the front corners
    rushes(cx, cz, n, h, int(cx * 7 + cz), spread=1.8)
def tire(X, Z, seed):
    """a tyre half sunk in the silt"""
    for k in range(14):
        a0, a1 = math.pi * k / 14, math.pi * (k + 1) / 14
        rs.beam((X + 0.75 * math.cos(a0), 0.75 * math.sin(a0) - 0.25, Z), (X + 0.75 * math.cos(a1), 0.75 * math.sin(a1) - 0.25, Z), 0.36,
                lambda x, y, s, t, z, wp: fogged(tone(STONE, 1.6 - t * 0.6 + (0.6 if int(s * 30) % 2 else 0), x, y), z))
tire(-20.5, 15.8, 1); tire(21.5, 15.0, 2)
rs.beam((-7.0, 0.0, 13.4), (-7.3, 0.95, 13.5), 0.95, ironround(2.6, IRON, rust=1.0), w1=1.15)              # a rusted bucket
rs.disc(-7.3, 0.95, 13.48, 0.55, lambda x, y, a, b, z, wp: fogged(tone(IRON, 1.2 + b * 0.6, x, y), z))
for i in range(40):                                                                # dead reeds lying flat in the mud
    X = -26 + (h32(i, 41) % 520) / 10.0; Z = 11.5 + (h32(i, 42) % 60) / 10.0
    if Z > near_shore(X) - 0.5 or 2 < X < 24: continue
    a = (h32(i, 43) % 628) / 100
    L = 0.8 + (h32(i, 44) % 10) * 0.12
    rs.beam((X, 0.03, Z), (X + math.cos(a) * L, 0.05, Z + math.sin(a) * L * 0.5), 0.07, lambda x, y, s, t, z, wp: fogged(tone(REED, 2.6 - s, x, y), z))

# ---------------------------------------------------------------------------------------------------- the horns
def horn_outer(x, y, u, v, z, wp, lit):
    """corroded bronze-iron: lit side to shadow side, verdigris in streaks running back from the mouth, rust, algae beards"""
    X, Y, Z = wp
    val = 1.8 + lit * 3.2 + (wn(1, u * 40, v * 6) - 0.5) * 0.6
    if (u * 28) % 1 < 0.06: val -= 0.6                                             # riveted seams
    if v > 0.93: val += 0.9                                                        # the rolled lip
    c = tone(HORN, val, x, y)
    st = wn(2, u * 70, v * 1.4)                                                    # verdigris runs back from the mouth
    if st > 0.6 + (1 - v) * 0.2: c = mix(c, tone(VERD, val, x, y), 0.55)
    if wn(3, u * 90 + 5, v * 18) > 0.74: c = mix(c, tone(RUSTY, val - 0.6, x, y), 0.4)
    return fogged(c, z)
def horn_inner(x, y, u, v, z, wp, depth):
    """the throat: dark, falling to black, wet"""
    val = 2.6 - depth * 2.6 + (wn(1, u * 30, depth * 8) - 0.5) * 0.8
    if (u * 28) % 1 < 0.08: val -= 0.5
    return fogged(tone(HORN, val, x, y), z)
def horn(throat, mouth, r_throat, r_mouth, seed):
    """a gramophone horn: three frustums flaring toward the mouth, a rolled lip, slime beards hanging off the rim"""
    ax = tuple(mouth[i] - throat[i] for i in range(3))
    pts = [0.0, 0.45, 0.78, 1.0]; rr = [r_throat, r_throat * 1.6, r_mouth * 0.48, r_mouth]
    o = rs.obj()
    for k in range(3):
        C0 = tuple(throat[i] + ax[i] * pts[k] for i in range(3)); C1 = tuple(throat[i] + ax[i] * pts[k + 1] for i in range(3))
        frustum(rs, C0, C1, rr[k], rr[k + 1], horn_outer, horn_inner, n=32, obj=o)
    # slime beards off the lower rim
    L = math.sqrt(sum(a * a for a in ax)); d = tuple(a / L for a in ax)
    ref = (0.0, 1.0, 0.0); e1 = (d[1] * ref[2] - d[2] * ref[1], d[2] * ref[0] - d[0] * ref[2], d[0] * ref[1] - d[1] * ref[0])
    l1 = math.sqrt(sum(a * a for a in e1)) or 1; e1 = tuple(a / l1 for a in e1)
    e2 = (d[1] * e1[2] - d[2] * e1[1], d[2] * e1[0] - d[0] * e1[2], d[0] * e1[1] - d[1] * e1[0])
    for k in range(16):
        a = math.pi * 2 * k / 16
        P = tuple(mouth[i] + (e1[i] * math.cos(a) + e2[i] * math.sin(a)) * r_mouth for i in range(3))
        if P[1] > mouth[1] - r_mouth * 0.2 or h32(seed, k) % 3 == 0: continue
        ln = 0.8 + (h32(seed, k, 2) % 7) * 0.45
        rs.beam(P, (P[0] + 0.1, P[1] - ln, P[2]), 0.28, lambda x, y, s, t, z, wp: fogged(tone(ALGAE, 3.0 - s * 1.5 - t * 0.5, x, y), z), w1=0.06)

def lattice_tower(feet, top_c, top_w, seed, levels=6, wood_v=2.6):
    """four timber legs from feet [(X, Z) x4] to a square top (centre top_c=(X, Y, Z), half-width top_w), ties and X braces"""
    tops = [(top_c[0] - top_w, top_c[1], top_c[2] - top_w), (top_c[0] + top_w, top_c[1], top_c[2] - top_w),
            (top_c[0] - top_w, top_c[1], top_c[2] + top_w), (top_c[0] + top_w, top_c[1], top_c[2] + top_w)]
    base = [(feet[i][0], feet[i][1], feet[i][2]) for i in range(4)]
    alg = lambda wp: 1.0 if wp[1] < 1.2 else 0.0
    for i in range(4):
        rs.beam(base[i], tops[i], 1.1 if i < 2 else 0.9, timber(wood_v if i < 2 else wood_v - 0.8, WOOD, algae=alg, seed=seed + i), w1=0.8)
    def lp(a, b, t): return tuple(a[j] + (b[j] - a[j]) * t for j in range(3))
    for k in range(1, levels + 1):
        t0 = k / (levels + 0.6); t1 = (k + 1) / (levels + 0.6)
        for (i, j) in ((0, 1), (0, 2), (1, 3)):
            a, b = lp(base[i], tops[i], t0), lp(base[j], tops[j], t0)
            rs.beam(a, b, 0.5, timber(wood_v - 0.3, WOOD, seed=seed + 10 * k + i))
            if k < levels and (i, j) == (0, 1):
                a2, b2 = lp(base[i], tops[i], t1), lp(base[j], tops[j], t1)
                rs.beam(a, b2, 0.36, timber(wood_v - 0.6, WOOD, seed=seed + 100 + k)); rs.beam(b, a2, 0.36, timber(wood_v - 0.6, WOOD, seed=seed + 200 + k))
    # a plank platform on top
    rs.box(top_c[0] - top_w - 0.8, top_c[0] + top_w + 0.8, top_c[1] - 0.5, top_c[1], top_c[2] - top_w - 0.8, top_c[2] + top_w + 0.8,
           planks(2.6, WOOD, w=0.5, seed=seed), planks_z(2.0, WOOD, seed=seed + 1), bottom=planks(1.4, WOOD, w=0.5, seed=seed + 2), cls='prop')
    return tops

# ---------------------------------------------------------------------------------------------------- the left islet: the drain-house and the twin-horn tower
def bricks(v0, seed=0, along_z=False):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = Z if along_z else X
        row = math.floor(Y / 0.32); off = (row % 2) * 0.35
        fb = ((u + off) / 0.7) % 1; fv = (Y / 0.32) % 1
        v = v0 + (h32(math.floor((u + off) / 0.7), row, seed) % 4) * 0.3 + (wn(0, u * 0.4, Y * 0.4) - 0.5) * 1.2
        px = z / F
        if px < 0.12 and (fb < px / 0.7 or fv < px / 0.32): v -= 1.4
        c = tone(BRICK, v, x, y)
        if wn(2, u * 0.3 + seed, Y * 0.3) > 0.7: c = mix(c, tone(STONE, v + 0.4, x, y), 0.5)  # render still clinging
        if Y < 1.4 + wn(1, u, 3.0): c = mix(c, tone(ALGAE, v, x, y), 0.6)
        return fogged(c, z)
    return sh
def jagged(top0, top1, X0, X1, seed):
    def clip(a, b):
        u = X0 + (X1 - X0) * a
        hh = top0 + (top1 - top0) * a + (wn(1, u * 0.6 + seed, 2.0) - 0.5) * 3.0 + (h32(int(u * 2), seed) % 3) * 0.4
        return b * (top0 + 2.0) <= hh
    return clip
# the drain-house under the tower
DHX0, DHX1, DHZ0, DHZ1 = -66.0, -30.0, 46.0, 55.0
rs.quad((DHX0, 0.25, DHZ0), (DHX1, 0.25, DHZ0), (DHX0, 8.25, DHZ0), bricks(2.8, 1), clip=jagged(6.0, 4.0, DHX0, DHX1, 3), cls='wall')
rs.quad((DHX1, 0.25, DHZ0), (DHX1, 0.25, DHZ1), (DHX1, 6.25, DHZ0), bricks(2.2, 2, along_z=True), clip=lambda a, b: b * 6 <= 4.0 + (wn(1, a * 9, 1) - 0.5) * 2.5, cls='wall')
for (ax0, ax1) in ((-61.0, -57.0), (-50.0, -46.0), (-39.0, -35.0)):                 # arched culvert mouths, the delta drains out of them
    def culvert(x, y, s, t, z, wp, ax0=ax0, ax1=ax1):
        u = (s - 0.5) * 2
        top = 0.62 + 0.38 * math.sqrt(max(0.0, 1 - u * u))
        if t > top: return None
        rim = abs(u) > 0.82 or t > top - 0.08
        return fogged(tone(STONE, 3.6 if rim else 0.6 + t * 0.6, x, y), z)
    rs.quad((ax0, 0.2, DHZ0 - 0.06), (ax1, 0.2, DHZ0 - 0.06), (ax0, 4.2, DHZ0 - 0.06), culvert, cls='prop', cut=True)
TOWER_A = lattice_tower([(-58.0, 0.25, 47.5), (-38.0, 0.25, 47.5), (-57.0, 0.25, 53.5), (-39.0, 0.25, 53.5)], (-46.0, 30.0, 50.5), 3.0, 30, levels=6, wood_v=2.8)
rs.beam((-44.5, 1.0, 47.0), (-44.5, 30.0, 48.4), 1.5, ironround(2.6, IRON, rust=0.6))   # the drain pipe up to the horns
horn((-44.0, 33.6, 50.0), (-27.5, 41.0, 45.0), 1.2, 9.0, 1)
horn((-44.5, 22.0, 49.2), (-30.0, 23.4, 44.4), 1.0, 6.6, 2)
rs.beam((-44.5, 30.0, 48.4), (-44.0, 33.6, 50.0), 1.3, ironround(2.6, IRON, rust=0.6))
for k in range(3):                                                                 # cables sagging off the tower to the drain-house
    rs.line3((-41.0, 27.0 - k * 3.0, 48.0), (-33.0 + k * 1.2, 5.0 + k * 0.4, 46.2), lambda x, y, s, t, z, wp: fogged(STONE[0], z), w=0.12, sag=1.6 + k * 0.5)

# ---------------------------------------------------------------------------------------------------- the right island: the pump-house of the redmass, its pipes, the one-horn tower
PHX0, PHX1, PHZ0, PHZ1, PHH = 30.0, 52.0, 47.0, 56.0, 8.5
def pump_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    for (wx0, wx1) in ((33.0, 36.0), (41.0, 44.0)):                                # tall arched windows, glassless
        if wx0 < X < wx1 and 2.4 < Y < 6.8 + 0.8 * math.sqrt(max(0.0, 1 - ((X - (wx0 + wx1) / 2) / 1.5) ** 2)) - 0.8:
            glow = (X > 41) and Y < 4.4
            if glow: return tone(CRYST, 1.2 + (4.4 - Y) * 0.6 + (wn(1, X * 2, Y * 2) - 0.5), x, y)   # the red light inside
            return fogged(STONE[0] if (x + y) % 5 else STONE[1], z)
    if 47.0 < X < 50.0 and Y < 5.0: return fogged(STONE[0], z)                     # the doorway
    return bricks(3.0, 7)(x, y, s, t, z, wp)
rs.quad((PHX0, 0.25, PHZ0), (PHX1, 0.25, PHZ0), (PHX0, PHH + 2.25, PHZ0), pump_front, clip=jagged(PHH, PHH - 1.0, PHX0, PHX1, 9), cls='wall')
rs.quad((PHX0, 0.25, PHZ0), (PHX0, 0.25, PHZ1), (PHX0, PHH + 0.25, PHZ0), bricks(2.2, 8, along_z=True), cls='wall')
for k in range(7):                                                                 # the roof's bare rafters
    X = PHX0 + 1.0 + k * 3.2
    if k in (2, 5): continue
    rs.beam((X, PHH - 0.2, PHZ0 + 0.2), (X + 0.3, PHH + 3.2, (PHZ0 + PHZ1) / 2), 0.36, timber(1.8, WOOD, seed=300 + k))
rs.box(PHX0 + 1.0, PHX0 + 10.0, PHH - 0.6, PHH - 0.1, PHZ0 + 0.3, PHZ0 + 4.0, lambda x, y, s, t, z, wp: fogged(tone(METAL, 2.0 + t, x, y), z),
       lambda x, y, s, t, z, wp: fogged(METAL[1], z), top=corrugated(2.6, METAL, 0.9), cls='prop')     # a sheet of the old roof still on
CH = (44.5, 46.8, 50.0, 52.3, 21.0)
rs.box(CH[0], CH[1], 0.25, CH[4], CH[2], CH[3], bricks(3.2, 10), bricks(2.4, 11, along_z=True), cls='wall')   # the chimney (it smokes)
rs.box(CH[0] - 0.4, CH[1] + 0.4, CH[4], CH[4] + 0.6, CH[2] - 0.4, CH[3] + 0.4, lambda x, y, s, t, z, wp: fogged(tone(IRON, 2.6, x, y), z), lambda x, y, s, t, z, wp: fogged(IRON[1], z), cls='prop')
def redpipe(v0, glow_at):
    """a big corroded pipe with the redmass growing through it: crystal clusters in its breaks, faintly lit"""
    base = ironround(v0, IRON, rust=0.75)
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        for (gx, gy, r) in glow_at:
            d = math.hypot(X - gx, Y - gy)
            if d < r:
                k = h32(int(X * 6), int(Y * 6), 5)
                return CRYST[3 + k % 3] if d < r * 0.5 else CRYST[1 + k % 3]
        return base(x, y, s, t, z, wp)
    return sh
GL1 = [(53.5, 3.2, 0.7), (57.8, 8.6, 0.9), (60.6, 4.0, 0.6)]
rs.beam((PHX1 - 0.2, 3.2, 50.0), (56.6, 3.2, 50.0), 1.5, redpipe(2.6, GL1), cap=True)
rs.beam((56.6, 3.2, 50.0), (57.6, 9.0, 50.0), 1.5, redpipe(2.6, GL1), cap=True)
rs.beam((57.6, 9.0, 50.0), (61.2, 9.2, 50.0), 1.5, redpipe(2.8, GL1), cap=True)
rs.beam((61.2, 9.2, 50.0), (61.6, WL - 1.0, 49.6), 1.5, redpipe(2.4, GL1), cap=True)
rs.beam((PHX0 + 0.5, 1.6, PHZ0 - 0.6), (22.0, 1.2, PHZ0 - 3.0), 1.1, redpipe(2.4, [(26.0, 1.4, 0.5)]), cap=True)   # a pipe out to the shore
rs.beam((22.0, 1.2, PHZ0 - 3.0), (18.0, WL - 0.6, 43.0), 1.1, ironround(2.2, IRON, rust=0.8), cap=True)
for (gx, gy, gz) in ((37.5, 0.9, PHZ0 - 0.4), (45.0, 0.5, PHZ0 - 0.3), (52.5, 1.2, PHZ0 - 0.2)):          # crystal veins at the wall's foot
    for k in range(6):
        a = h32(int(gx), k) % 628 / 100
        rs.beam((gx, gy, gz), (gx + math.cos(a) * 0.9, gy + abs(math.sin(a)) * 1.2, gz - 0.1), 0.22,
                lambda x, y, s, t, z, wp: (CRYST[4] if s > 0.6 else CRYST[2]), cls='emit', w1=0.06)
# the one-horn tower, leaning toward the bank
TOWER_B = lattice_tower([(17.0, 0.25, 44.5), (27.0, 0.25, 44.5), (17.5, 0.25, 49.0), (26.5, 0.25, 49.0)], (24.5, 25.0, 47.0), 2.2, 60, levels=5, wood_v=2.4)
horn((24.0, 27.4, 47.0), (11.0, 30.0, 42.5), 1.0, 5.6, 3)

# ---------------------------------------------------------------------------------------------------- far: dead works in the haze
def far_shape(X0, X1, Z, hh, kind, seed):
    def sh(x, y, s, t, z, wp):
        u = s
        if kind == 'tower':                                                        # a lattice tower
            if not (abs(u - 0.5) < 0.5 - t * 0.25): return None
            if not ((abs((u * 3 + t * 9) % 1 - 0.5) < 0.1) or abs(u - 0.5) > 0.42 - t * 0.25 or (t * 9) % 1 < 0.12): return None
        elif kind == 'stack':
            if abs(u - 0.5) > 0.12 - t * 0.03: return None
        elif kind == 'works':                                                      # a ruined hall, broken roofline
            top = 0.75 + (wn(1, u * 6 + seed, 1.0) - 0.5) * 0.5
            if t > top: return None
            if 0.3 < t < 0.6 and (u * 7) % 1 < 0.35 and h32(int(u * 7), seed) % 2: return HAZE[1]
        elif kind == 'hornt':                                                      # a far horn tower
            if t < 0.75 and abs(u - 0.5) < 0.18 - t * 0.08: pass
            elif t >= 0.75 and math.hypot((u - 0.62) * 1.4, (t - 0.86) * 2.2) < 0.18: pass
            else: return None
        return HAZE[2] if (h32(int(u * 20), int(t * 30), seed) % 7) else HAZE[1]
    rs.quad((X0, WL, Z), (X1, WL, Z), (X0, WL + hh, Z), sh, cls='wall', cut=True)
def far_works(X0, X1, Z, hh, sd):
    """a ruined works hall far off: brick and concrete in bays, rows of dark window holes, a broken roofline, its side
    in perspective; the haze takes most of it"""
    def front(x, y, s, t, z, wp):
        X, Y, _ = wp
        top = hh * (0.78 + (wn(1, X * 0.2 + sd * 7, 1.0) - 0.5) * 0.45) + (h32(int(X / 3), sd) % 3) * 1.2
        if Y > top: return None
        bay = (X / 6.0) % 1; fl = (Y / 7.0) % 1
        v = 3.0 + (wn(0, X * 0.3, Y * 0.3) - 0.5) * 1.2 + (0.6 if bay < 0.06 else 0)
        if Y > 3 and 0.25 < bay < 0.75 and 0.35 < fl < 0.8: v = 0.8 + (h32(int(X / 6), int(Y / 7), sd) % 3) * 0.3   # window holes
        if Y > top - 0.8: v += 0.8
        return fogged(tone(BRICK if sd % 2 else STONE, v, x, y), z)
    def side(x, y, s, t, z, wp):
        X, Y, Z_ = wp
        if Y > hh * 0.7 + (wn(1, Z_ * 0.2 + sd, 2.0) - 0.5) * hh * 0.3: return None
        return fogged(tone(STONE, 2.0 + (wn(0, Z_ * 0.3, Y * 0.3) - 0.5), x, y), z)
    rs.quad((X0, WL, Z), (X1, WL, Z), (X0, WL + hh * 1.2, Z), front, cls='wall', cut=True)
    xs = X1 if X1 < 0 else X0
    rs.quad((xs, WL, Z), (xs, WL, Z + 24), (xs, WL + hh * 1.2, Z), side, cls='wall', cut=True)
for (X0, X1, Z, hh, kind, sd) in ((-150, -90, 230, 40, 'works', 1), (-110, -96, 200, 52, 'tower', 2), (-40, -14, 260, 30, 'works', 3),
                                   (-24, -16, 250, 64, 'stack', 4), (30, 80, 240, 34, 'works', 5), (60, 74, 210, 58, 'tower', 6),
                                   (95, 140, 260, 46, 'works', 7), (118, 126, 250, 70, 'stack', 8), (-70, -50, 180, 44, 'hornt', 9),
                                   (6, 22, 170, 38, 'hornt', 10), (140, 170, 200, 30, 'tower', 11), (-210, -160, 260, 50, 'works', 12)):
    if kind == 'works': far_works(X0, X1, Z, hh, sd)
    else: far_shape(X0, X1, Z, hh, kind, sd)
for (X, Z, hh) in ((-12, 110, 14), (8, 118, 20), (-30, 130, 12), (48, 120, 18), (-52, 96, 9)):            # nearer stumps of works
    rs.beam((X, WL - 1, Z), (X + 0.6, hh, Z), 2.2, timber(1.6, WOOD, seed=int(X)))
    rs.beam((X, hh * 0.7, Z), (X + 4.0, hh * 0.45, Z + 1), 0.8, timber(1.4, WOOD, seed=int(X) + 1))

# ---------------------------------------------------------------------------------------------------- the near left: a broken concrete wall in the mud (Palinode's seam)
WWX0, WWX1, WWZ = -27.0, -16.5, 24.0
SEAMX = -21.4
def cwall(x, y, s, t, z, wp):
    X, Y, Z = wp
    if abs(X - SEAMX - math.sin(Y * 1.7) * 0.25) < 0.07 + 0.03 * math.sin(Y * 5): return fogged(STONE[0], z)   # the crack
    v = 3.6 + (wn(0, X * 0.8, Y * 0.8) - 0.5) * 1.4 - (0.8 if (Y % 2.4) < 0.08 else 0) + (0.6 if (X * 0.6) % 1 < 0.04 else 0)
    c = tone(STONE, v, x, y)
    if wn(2, X * 0.9, Y * 0.3) > 0.7: c = mix(c, tone(RUSTY, v - 0.8, x, y), 0.25)  # rust from the rebar
    if Y < 1.2 + wn(1, X, 2.0) * 0.8: c = mix(c, tone(SILT, v - 0.6, x, y), 0.6)
    return fogged(c, z)
rs.quad((WWX0, 0, WWZ), (WWX1, 0, WWZ), (WWX0, 10.0, WWZ), cwall, clip=lambda a, b: b * 10 <= 8.4 - a * 2.4 + (wn(1, a * 12, 3.0) - 0.5) * 2.4 - (3.6 if a > 0.82 else 0), cls='wall')
rs.quad((WWX1, 0, WWZ), (WWX1, 0, WWZ + 1.0), (WWX1, 6.0, WWZ), lambda x, y, s, t, z, wp: fogged(tone(STONE, 2.4, x, y), z), cls='wall')
for k in range(6):                                                                 # rebar sticking out of the break
    X = WWX0 + 1.0 + k * 1.7
    top = 8.4 - (X - WWX0) / (WWX1 - WWX0) * 2.4
    rs.beam((X, top - 0.6, WWZ + 0.4), (X + 0.4 * ((k % 3) - 1), top + 0.9 + (k % 2) * 0.6, WWZ + 0.3), 0.1, lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 2.6 - t, x, y), z))
for i, (X, Z, r) in enumerate(((-29.0, 23.0, 1.0), (-14.5, 23.4, 0.7), (-25.0, 21.6, 0.6), (-31.5, 25.0, 1.3))):   # chunks broken off it
    rs.box(X - r, X + r, 0, r * 1.1, Z - r * 0.6, Z + r * 0.6, concrete(3.4, STONE), concrete(2.6, STONE), top=concrete(4.2, STONE), cls='prop')

# ---------------------------------------------------------------------------------------------------- the seam: a spit of half-sunk masonry toward the island
SPIT = [(7.0, 19.0), (8.6, 22.0), (10.4, 25.2), (12.2, 28.6), (14.0, 32.0), (15.6, 35.4), (17.2, 38.6), (18.4, 41.2)]
for i in range(30):                                                                # broken slabs awash, barely breaking the surface
    k = i / 29 * (len(SPIT) - 1); j = min(len(SPIT) - 2, int(k)); f = k - j
    X = SPIT[j][0] + (SPIT[j + 1][0] - SPIT[j][0]) * f + ((h32(i, 7) % 100) / 100 - 0.5) * 2.2
    Z = SPIT[j][1] + (SPIT[j + 1][1] - SPIT[j][1]) * f + ((h32(i, 8) % 100) / 100 - 0.5) * 0.8
    if h32(i, 9) % 3 == 0: continue
    w = 0.5 + (h32(i, 1) % 5) * 0.2; d = 0.35 + (h32(i, 2) % 4) * 0.15; a = ((h32(i, 3) % 100) / 100 - 0.5) * 1.2
    ca, sa = math.cos(a), math.sin(a)
    def slab(x, y, s, t, z, wp, i=i):
        u, v = (s - 0.5) * 2, (t - 0.5) * 2
        if max(abs(u), abs(v)) > 0.85 + (wn(1, wp[0] * 3 + i, wp[2] * 3) - 0.5) * 0.5: return None
        c = tone(STONE, 2.6 + (wn(1, wp[0] * 2, wp[2] * 2) - 0.5) * 1.2 + (0.6 if v < -0.6 else 0), x, y)
        return fogged(mix(c, tone(ALGAE, 2.6, x, y), 0.5 if abs(u) > 0.5 or abs(v) > 0.5 else 0.3), z)
    rs.quad((X - w * ca + d * sa, WL + 0.05, Z - w * sa - d * ca), (X + w * ca + d * sa, WL + 0.05, Z + w * sa - d * ca),
            (X - w * ca - d * sa, WL + 0.05, Z - w * sa + d * ca), slab, cls='prop', cut=True)

# ---------------------------------------------------------------------------------------------------- a U-pipe coming out of the near water on the right, scrap in the mud
UPX, UPZ = 38.0, 29.0
rs.beam((UPX, WL - 1.0, UPZ), (UPX, 6.2, UPZ), 1.6, ironround(2.8, IRON, rust=0.8), cap=True)
rs.beam((UPX, 6.2, UPZ), (UPX + 2.4, 7.4, UPZ), 1.6, ironround(3.0, IRON, rust=0.8), cap=True)
rs.beam((UPX + 2.4, 7.4, UPZ), (UPX + 4.8, 6.2, UPZ), 1.6, ironround(2.8, IRON, rust=0.8), cap=True)
rs.beam((UPX + 4.8, 6.2, UPZ), (UPX + 4.8, WL - 1.0, UPZ), 1.6, ironround(2.4, IRON, rust=0.8), cap=True)
for X in (UPX, UPX + 4.8):                                                         # flanges
    rs.box(X - 1.05, X + 1.05, 2.4, 2.8, UPZ - 1.0, UPZ + 1.0, steel(3.0, IRON, rust=0.5), steel(2.2, IRON, rust=0.5), top=steel(3.6, IRON, rust=0.5), cls='prop')
rs.beam((UPX + 2.4, 7.9, UPZ), (UPX + 2.4, 9.2, UPZ), 0.3, ironround(2.6, IRON, rust=0.6))                  # a valve stem and its wheel
for k in range(12):
    a0, a1 = math.pi * 2 * k / 12, math.pi * 2 * (k + 1) / 12
    rs.beam((UPX + 2.4 + 0.8 * math.cos(a0), 9.2, UPZ + 0.8 * math.sin(a0)), (UPX + 2.4 + 0.8 * math.cos(a1), 9.2, UPZ + 0.8 * math.sin(a1)), 0.16, ironround(2.8, RUSTY, rust=0.2))
rs.beam((40.5, WL + 0.1, 24.0), (36.0, 0.6, 21.5), 0.9, ironround(2.2, IRON, rust=0.9), cap=True)        # a half-buried pipe
rs.box(-6.0, -3.6, 0, 0.5, 9.0, 11.4, steel(2.6, IRON, rust=0.9), steel(2.0, IRON, rust=0.9), top=steel(3.2, IRON, rust=0.9), cls='prop')   # a plate in the mud
for k in range(10):                                                                # a wheel rim half sunk
    a0, a1 = math.pi * k / 10, math.pi * (k + 1) / 10
    rs.beam((-38.0 + 1.3 * math.cos(a0), 1.3 * math.sin(a0) - 0.3, 12.0), (-38.0 + 1.3 * math.cos(a1), 1.3 * math.sin(a1) - 0.3, 12.0), 0.22, ironround(2.4, IRON, rust=0.9))

# ---------------------------------------------------------------------------------------------------- smoke (2D, before the painterly pass)
def smoke(col, cls_):
    """soft plumes: gaussian puffs stamped into a density field along a drifting path, blended over the sky only"""
    n1 = make_noise(11, 91, W, H)
    dens = [[0.0] * W for _ in range(H)]
    for (P, length, drift, amount, wmax) in (((45.6, CH[4] + 0.6, 51.0), 300, 220, 0.8, 80), ((-20.0, 66.0, 250.0), 200, 150, 0.45, 56)):
        (sx, sy) = proj(*P)
        for i in range(90):
            a = i / 90.0
            cx = sx + a * drift + math.sin(a * 6) * 10; cy = sy - a * length + a * a * length * 0.3
            r = 4 + a * wmax
            for y in range(int(cy - r * 1.6), int(cy + r * 1.6) + 1):
                for x in range(int(cx - r * 1.6), int(cx + r * 1.6) + 1):
                    if not (0 <= x < W and 0 <= y < H): continue
                    d2 = ((x - cx) ** 2 + (y - cy) ** 2) / (r * r)
                    if d2 > 2.6: continue
                    dens[y][x] += math.exp(-d2 * 1.6) * amount * (1 - a) ** 1.3 * 0.09 * (0.5 + n1(x, y))
    for y in range(H):
        for x in range(W):
            d = dens[y][x]
            if d < 0.01 or cls_[y][x] != 'sky': continue
            k = min(0.75, 1 - math.exp(-d * 1.4))
            c = col[y][x]; sc = (46, 52, 48)
            col[y][x] = tuple(int(c[j] + (sc[j] - c[j]) * k) for j in range(3))

RENDER = dict(fog=fog_of, post=smoke, mirror=lambda x, y, wp: 0.5 * bank_puddle(wp[0], wp[2]) if wp[1] < 0.1 else 0.0,
              light_gain=1.2, grime_gain=0.8, bloom=0.6, stain_gain=0.6, damp_gain=0.3, sheen_gain=0.6)

def P2(X, Y, Z):
    p = proj(X, Y, Z); return (round(p[0]), round(p[1]))

# ---------------------------------------------------------------------------------------------------- sprites: the fungal bridge, the scrap heap
BRIDGE = [(16.0, 17.6), (16.6, 21.0), (17.6, 24.6), (18.4, 28.4), (19.6, 32.0), (20.6, 35.6), (21.4, 39.0), (22.0, 42.4)]
MYCB = ramp('#2a3a22 #3c5230 #567044 #78905a #9cb07a #c4d4a0')
def seg_dist(X, Z, pts):
    best = (9e9, 0.0)
    for i in range(len(pts) - 1):
        (ax, az), (bx, bz) = pts[i], pts[i + 1]
        dx, dz = bx - ax, bz - az; L2 = dx * dx + dz * dz
        t = max(0.0, min(1.0, ((X - ax) * dx + (Z - az) * dz) / L2))
        d = math.hypot(X - ax - dx * t, Z - az - dz * t)
        if d < best[0]: best = (d, (i + t) / (len(pts) - 1))
    return best
def fungal_bridge(rs):
    """the bridge the player's spores grew: a mat of mycelium and knotted roots floating on the water from the bank's
    soft sediment to the island, pale caps sprouting along it, the newest ones faintly lit"""
    def mat(x, y, s, t, z, wp):
        X, _, Z = wp
        d, u = seg_dist(X, Z, BRIDGE)
        wdt = 1.7 + 0.5 * math.sin(u * 13) + (wn(1, X * 0.8, Z * 0.8) - 0.5) * 0.8
        if d > wdt: return None
        v = 3.0 + (1 - d / wdt) * 1.6 + (wn(0, X * 2.4, Z * 2.4) - 0.5) * 1.6
        c = tone(MYCB, v, x, y)
        if wn(3, X * 3.0, Z * 1.0) > 0.66: c = tone(WOOD, v, x, y)                # roots knotted through it
        if d > wdt - 0.35: c = mix(c, tone(ALGAE, 2.0, x, y), 0.5)
        return fogged(c, z)
    rs.quad((10.0, WL + 0.14, 16.0), (28.0, WL + 0.14, 16.0), (10.0, WL + 0.14, 44.0), mat, cls='ground', cut=True)
    for k in range(26):                                                            # caps
        u = (h32(k, 1) % 1000) / 1000
        i = min(len(BRIDGE) - 2, int(u * (len(BRIDGE) - 1))); f = u * (len(BRIDGE) - 1) - i
        X = BRIDGE[i][0] + (BRIDGE[i + 1][0] - BRIDGE[i][0]) * f + ((h32(k, 2) % 100) / 100 - 0.5) * 2.4
        Z = BRIDGE[i][1] + (BRIDGE[i + 1][1] - BRIDGE[i][1]) * f
        hh = 0.25 + (h32(k, 3) % 5) * 0.12; r = 0.22 + (h32(k, 4) % 5) * 0.07
        lit_ = h32(k, 5) % 3 == 0
        rs.beam((X, WL + 0.1, Z), (X, WL + 0.1 + hh, Z), r * 0.5, lambda x, y, s, t, z, wp: fogged(tone(CAP, 3.0 - t * 0.5, x, y), z))
        rs.disc(X, WL + 0.1 + hh, Z, r, (lambda x, y, a, b, z, wp: (MYC[3] if b < -0.2 else MYC[2]) if b < 0.35 else None) if lit_ else
                (lambda x, y, a, b, z, wp: fogged(tone(CAP, 4.4 - b * 2 - a * 0.5, x, y), z) if b < 0.35 else None), cls='emit' if lit_ else 'prop')
SCRAPX, SCRAPZ = 2.0, 16.2
def scrap_heap(rs):
    """a heap of rusty scrap sifted out of the silt: a dented plate, a bent pipe, a cog, a spring of wire"""
    rs.box(SCRAPX - 0.9, SCRAPX + 0.5, 0, 0.18, SCRAPZ - 0.5, SCRAPZ + 0.6, steel(2.8, IRON, rust=1.4), steel(2.0, IRON, rust=1.4),
           top=steel(3.4, IRON, rust=1.4), cls='prop')
    rs.quad((SCRAPX - 0.8, 0.15, SCRAPZ - 0.2), (SCRAPX + 0.2, 0.15, SCRAPZ - 0.4), (SCRAPX - 0.6, 0.9, SCRAPZ - 0.1),
            lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 3.0 + s - (0.8 if (s * 5) % 1 < 0.15 else 0), x, y), z), cls='prop')       # a plate leaning
    rs.beam((SCRAPX - 0.2, 0.25, SCRAPZ - 0.3), (SCRAPX + 0.9, 0.55, SCRAPZ - 0.1), 0.34, ironround(2.8, IRON, rust=0.9), cap=True)  # the pipe
    rs.beam((SCRAPX + 0.9, 0.55, SCRAPZ - 0.1), (SCRAPX + 1.1, 1.1, SCRAPZ - 0.2), 0.3, ironround(3.0, IRON, rust=0.9), cap=True)
    def cog(x, y, a, b, z, wp):
        r = math.hypot(a, b); ang = math.atan2(b, a)
        teeth = 0.8 + 0.2 * (math.cos(ang * 8) > 0)
        if r > teeth or r < 0.22: return None
        return fogged(tone(IRON, 3.6 - b * 1.4 - a * 0.4 if r > 0.4 else 2.0, x, y), z)
    rs.disc(SCRAPX + 0.45, 0.45, SCRAPZ - 0.6, 0.45, cog)
    for k in range(8):                                                             # wire
        a0, a1 = k * 0.8, (k + 1) * 0.8
        rs.beam((SCRAPX - 0.6 + k * 0.08, 0.2 + 0.18 * math.sin(a0), SCRAPZ - 0.55 + 0.15 * math.cos(a0)),
                (SCRAPX - 0.6 + (k + 1) * 0.08, 0.2 + 0.18 * math.sin(a1), SCRAPZ - 0.55 + 0.15 * math.cos(a1)), 0.05,
                lambda x, y, s, t, z, wp: fogged(RUSTY[3], z))

def cut_sprite(img, img2, n0, box, name, keep_changed=False):
    spr = Image.new('RGBA', (box[2] - box[0], box[3] - box[1]), (0, 0, 0, 0))
    p0, p1, ps = img.load(), img2.load(), spr.load()
    mine = lambda x, y: rs.G[y][x] is not None and rs.G[y][x][1] > n0
    for y in range(max(0, box[1]), min(H, box[3])):
        for x in range(max(0, box[0]), min(W, box[2])):
            ch = max(abs(p0[x, y][i] - p1[x, y][i]) for i in range(3))
            edge = any(0 <= x + dx < W and 0 <= y + dy < H and mine(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if mine(x, y) or (edge and ch > 6) or (keep_changed and ch > 10 and rs.G[y][x] is not None and rs.G[y][x][5] == 'water'):
                ps[x - box[0], y - box[1]] = p1[x, y] + (255,)
    bb = spr.getbbox()
    spr.crop(bb).save(f'{OUT}/{name}.png')
    print('done', name, ': top-left', (box[0] + bb[0], box[1] + bb[1]), 'size', (bb[2] - bb[0], bb[3] - bb[1]))

if __name__ == '__main__':
    img = rs.render(INK, **RENDER)
    img.save(f'{OUT}/delta.png')
    print('done delta')
    print('seam crack', P2(SEAMX, 4.0, WWZ), P2(SEAMX, 0, WWZ), '| spit', [P2(X, WL, Z) for (X, Z) in SPIT[::2]],
          '| bridge ends', P2(BRIDGE[0][0], WL, BRIDGE[0][1]), P2(BRIDGE[-1][0], WL, BRIDGE[-1][1]),
          '| island shore', P2(22, 0.25, 43), '| horn mouths', P2(-27, 45, 45), P2(-29.5, 26.8, 44.4), P2(11, 30, 42.5))
    n0 = rs.n
    fungal_bridge(rs)
    img2 = rs.render(INK, **RENDER)
    a, b = P2(10.0, WL, 16.0), P2(28.0, WL, 44.0)
    cut_sprite(img, img2, n0, (min(a[0], b[0]) - 120, 300, max(a[0], b[0]) + 140, 600), 'delta_bridge', keep_changed=True)
    img2.save(f'{OUT}/delta_with_bridge.png')
    rs2 = rs
    n1 = rs.n
    scrap_heap(rs)
    img3 = rs.render(INK, **RENDER)
    (sx, sy) = P2(SCRAPX, 0, SCRAPZ)
    cut_sprite(img2, img3, n1, (sx - 50, sy - 50, sx + 60, sy + 20), 'delta_scrap')
    print('scrap foot', (sx, sy))
