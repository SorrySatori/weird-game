"""The sealed gate of the Godgraveyard (GodgraveyardScene before the Townhall's leave), 1067x600, overcast day, the
shared camera (raster3d.py). After the old art (GodgraveyardGate.png): a tall wrought-iron double gate between two
ashlar pillars, each crowned by a lit iron lantern; over the leaves an iron overthrow -- two arched bands with spear
points, scrollwork, a halo crest -- holding the name plate GODGRAVEYARD (the name the old art and the scene use;
`python3 gyard_gate_bg.py <out> noname` renders the plate with a plain emblem instead). The leaves are chained shut: a
heavy chain crossed over the meeting stiles with a big verdigris padlock and an older, greener one under it ("sealed
with the Townhall's wax and older, greener locks"), paper seal strips with red wax across the gap. Low stone walls with
spear-topped railings splay forward from the pillars and run off to both sides; bare trees behind them; a cobbled
lane with mossy joints and puddles runs up to the gate between grass verges. Through and over the gate the field
of dead gods rises out of the fog -- colossal steles, a horned shrine, a crowned head -- the place the gate keeps.
No people, no mushrooms.

    python3 gyard_gate_bg.py <outdir> [noname]   ->  gate.png (assets/images/backgrounds/GodgraveyardGate.png)
Fixed points (canvas): the gate opening x ~436..630 (leaves y ~251..444; the scene's examine zone), the big padlock
~(533, 378); the pillars x ~378..436 / 630..688 (lanterns y ~225..267); the name plate x ~469..597, y ~225..246; the
walk line y 534 runs across the lane in front of the bollards (they stand at depth 16.4, behind it); the exit back to
the Town Square is the bottom edge (the lane behind the viewer)."""
import sys, os, math
from PIL import Image, ImageDraw, ImageFont
from common import h32, draw_text, text_width
import gyard_kit as K
from gyard_kit import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
NONAME = 'noname' in sys.argv[2:]
K.FOGCFG.update(scale=48.0, max=0.9)
fog_of, fogged = K.fog_of, K.fogged
rs = Raster()
ZG = 22.0                    # the pillars' front face
ZL = 23.6                    # the plane of the leaves (the middle of the pillars)
GX0, GX1 = 7.6, 11.4         # the opening's half width, the pillars' outer edge
ZW = 17.5                    # where the side walls run straight across

# ---------------------------------------------------------------------------------------------------- sky
rs.quad((-1400, 800, 600), (1400, 800, 600), (-1400, -300, 600), sky, cls='sky')

# ---------------------------------------------------------------------------------------------------- ground
def lane_half(Z):
    """the cobbled lane's half width: through the gate 6.4, splaying toward the camera"""
    if Z >= ZG: return 6.2
    return 6.4 + (ZG - Z) * 0.42
def puddle(X, Z):
    if Z > 40 or abs(X) > lane_half(Z) - 0.4: return 0.0
    m = wn(2, X * 0.3 + 7.0, Z * 0.32) + (wn(3, X * 1.4, Z * 1.4) - 0.5) * 0.12
    return max(0.0, min(1.0, (m - 0.68) * 10))
def ground(x, y, s, t, z, wp):
    X, _, Z = wp
    lh = lane_half(Z) + (n1(Z * 0.8, 3.0) - 0.5) * 0.9
    if abs(X) < lh:
        c = cobbles(x, y, s, t, z, wp, sc=0.82, v0=4.6, moss=0.55)
        if abs(X) > lh - 0.7: c = mix(c, tone(MOSSR, 2.4, x, y), 0.55)                              # grass creeping in
        return c
    # the verges: dead grass and moss, darker under the walls
    v = 2.4 + (n2(X * 0.9, Z * 0.9) - 0.5) * 1.6 + (n3(X * 4.0, Z * 4.0) - 0.5) * 1.2
    blade = (h32(int(X * 14 + 9999), int(Z * 9 + 9999), 3) % 5 == 0)
    if n1(X * 0.35 + 30, Z * 0.35) > 0.55: c = tone(MOSSR, v + 0.6 + (1.2 if blade else 0), x, y)
    else: c = tone(STRAW, v + (1.4 if blade else 0), x, y)
    return fogged(c, Z)
rs.quad((-160, 0, 3), (160, 0, 3), (-160, 0, 320), ground, cls='ground')

# ---------------------------------------------------------------------------------------------------- the field beyond (in the fog)
def far_shape(X, Z, w, h, kind, seed, v0=2.6, fk=0.66):
    """a silhouette of the graveyard beyond: a camera-facing card cut to its shape, shaded only a little (the fog
    does the rest)"""
    def sh(x, y, s, t, z, wp):
        u = (s - 0.5) * 2; e = (n1(s * 9 + seed, t * 9) - 0.5) * 0.06
        if kind == 'stele':
            if abs(u) > 0.8 + e: return None
            if t > 0.82 and math.hypot(u, (t - 0.82) / 0.18 * 0.8) > 0.8 + e: return None
        elif kind == 'gable':
            if abs(u) > 0.75 + e or t > 0.84 + 0.16 * (1 - abs(u) / 0.75) + e: return None
            if t > 0.9 and abs(u) < 0.06: pass
        elif kind == 'horned':                                                          # a squat shrine, two horns
            body = abs(u) < 0.55 + e and t < 0.62
            hu = abs(u) - 0.55 + 0.25 * math.sin((t - 0.55) / 0.45 * math.pi * 0.9)
            horn = 0.55 < t < 1.0 and abs(hu) < 0.09 * (1 - (t - 0.55) / 0.45) + 0.02
            if not (body or horn or (t < 0.7 and abs(u) < 0.2)): return None
        elif kind == 'head':                                                            # a crowned head, sunk to the chin
            d = math.hypot(u / 0.62, (t - 0.42) / 0.42)
            spike = t > 0.6 and any(abs(u - k * 0.18) < 0.05 * (1 - (t - 0.6) / 0.4) + 0.01 and t < 0.6 + 0.4 * (1 - abs(k) * 0.18) for k in range(-3, 4))
            if d > 1 + e and not spike: return None
        elif kind == 'dome':                                                            # a dome with a halo ring over it
            body = t < 0.55 and abs(u) < 0.7 * math.sqrt(max(0.0, 1 - max(0.0, t - 0.25) ** 2 / 0.09)) + e
            ring = abs(math.hypot(u, (t - 0.78) * 1.4) - 0.26) < 0.05
            if not (body or ring or (abs(u) < 0.03 and t < 0.66)): return None
        elif kind == 'obelisk':
            if abs(u) > 0.5 * (1 - t * 0.5) + e or (t > 0.9 and abs(u) > (1 - t) * 5 * 0.5): return None
        v = v0 + (0.6 if u < -0.2 else -0.3 if u > 0.4 else 0) + (n2(X + s * w, t * h) - 0.5) * 1.0
        return fogged(tone(GRAVE, v, x, y), z, fk)
    rs.quad((X - w / 2, -1.0, Z), (X + w / 2, -1.0, Z), (X - w / 2, h - 1.0, Z), sh, cls='wall', cut=True)
def at_x(x, Z): return (x - 533) * Z / F                                               # world X that lands on canvas x at depth Z
for (x, Z, w, h, kind, seed) in ((300, 140, 30, 60, 'horned', 4), (225, 100, 10, 50, 'stele', 2), (800, 110, 30, 34, 'head', 1),
                                 (905, 165, 34, 62, 'dome', 5), (705, 95, 12, 44, 'gable', 3), (362, 120, 5, 52, 'obelisk', 6),
                                 (497, 70, 7, 36, 'stele', 7), (586, 76, 8, 40, 'gable', 8), (150, 150, 12, 46, 'gable', 9),
                                 (990, 120, 9, 40, 'stele', 10), (640, 130, 5, 46, 'obelisk', 11), (430, 90, 6, 30, 'stele', 12)):
    far_shape(at_x(x, Z), Z, w, h, kind, seed)
for k in range(40):                                                                   # the countless small stones of the field
    X = -70 + (h32(k, 1) % 1400) / 10.0; Z = 55 + (h32(k, 2) % 1500) / 10.0
    if abs(X) < 4 and Z < 70: continue
    far_shape(X, Z, 2.2 + (h32(k, 3) % 30) / 10.0, 3.0 + (h32(k, 4) % 60) / 10.0, ['stele', 'gable', 'obelisk'][k % 3], 20 + k, v0=2.4, fk=0.75)

# ---------------------------------------------------------------------------------------------------- pillars
def ashlar(v0=4.6, ramp_=GRAVE, bh=1.45, bw=2.0, along_z=False, seed=0):
    """coursed ashlar: blocks of their own tone, sunk joints, a lit upper arris and a shadowed lower one, lichen"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = Z if along_z else X
        row = math.floor(Y / bh); off = (row % 2) * bw * 0.5 + h01(row, seed) * 0.3
        col_ = math.floor((u + off) / bw)
        fu, fv = ((u + off) / bw) % 1, (Y / bh) % 1
        px = z / F
        if fu * bw < px * 1.1 or fv * bh < px * 1.1: return fogged(tone(ramp_, 1.2, x, y), z)
        v = v0 + (h32(col_, row, seed) % 5 - 2) * 0.35 + (n2(u * 1.3 + seed, Y * 1.3) - 0.5) * 1.2 + (n3(u * 5, Y * 5) - 0.5) * 0.5
        if fv * bh > bh - px * 2.2: v += 1.0
        elif fv * bh < px * 2.4: v -= 0.8
        if (1 - fu) * bw < px * 2: v -= 0.5
        c = tone(ramp_, v, x, y)
        lc = n1(u * 1.5 + seed * 3 + 15, Y * 1.5) + (n3(u * 6, Y * 6) - 0.5) * 0.2
        if lc > 0.76: c = tone(LICHEN, 1.6 + (v - v0) * 0.5 + (n2(u * 8, Y * 8) - 0.5) * 1.4, x, y) if lc > 0.78 else mix(c, (16, 18, 14), 0.4)
        if Y < 0.9 + n1(u * 1.5, 4.0) * 1.4 and n2(u * 2.5 + 7, Y * 2.5) > 0.5: c = tone(MOSSR, 2.2 + (v - v0) * 0.5 + (n3(u * 7, Y * 7) - 0.5) * 1.6, x, y)
        run = n3(u * 3.0 + seed * 9, 2.0)
        if run > 0.66: c = mix(c, (14, 16, 14), min(0.4, (run - 0.66) * 2.0))                            # rain-wash runs
        return fogged(c, z)
    return sh
def cap_sh(v0):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = v0 + (n2(X * 1.4, Z * 1.4 + Y) - 0.5) * 1.2
        c = tone(GRAVE, v, x, y)
        if n1(X * 1.2 + 4, Z * 1.2) > 0.55: c = tone(MOSSR, 3.0 + (v - v0) * 0.6, x, y)
        return fogged(c, z)
    return sh
LANTERNS = []
for sgn in (-1, 1):
    x0, x1 = (-GX1, -GX0) if sgn < 0 else (GX0, GX1)
    rs.box(x0 - 0.35, x1 + 0.35, 0, 1.5, ZG - 0.35, ZG + 3.85, ashlar(4.0, seed=3 + sgn), ashlar(3.4, along_z=True, seed=5 + sgn), top=cap_sh(4.6), cls='wall')
    rs.box(x0, x1, 1.5, 13.0, ZG, ZG + 3.5, ashlar(4.8, seed=7 + sgn), ashlar(4.0 if sgn < 0 else 5.2, along_z=True, seed=9 + sgn), cls='wall')
    rs.box(x0 - 0.5, x1 + 0.5, 13.0, 13.7, ZG - 0.5, ZG + 4.0, cap_sh(5.4), cap_sh(4.4), bottom=cap_sh(2.2), cls='wall')   # the cornice
    rs.box(x0 + 0.2, x1 - 0.2, 13.7, 14.3, ZG + 0.2, ZG + 3.3, cap_sh(4.8), cap_sh(4.0), cls='wall')
    # a sunk panel with a carved roundel (an eye in a ring of rays) on the pillar's face
    pcx = (x0 + x1) / 2
    def panel(x, y, s, t, z, wp, pcx=pcx):
        """a sunk panel: shadowed upper and left reveals, a lit sill, a carved halo (a ring with short rays) in it"""
        X, Y, _ = wp
        px = z / F
        u, v = (s - 0.5) * 2.6, (t - 0.5) * 4.6
        if t > 1 - px * 2 / 4.6 or s < px * 2 / 2.6: val = 2.0                                     # reveals in shadow
        elif t < px * 2 / 4.6 or s > 1 - px * 2 / 2.6: val = 5.8                                   # lit sill
        else:
            d = math.hypot(u, v - 0.9)
            val = 3.4 + (n2(X * 3 + pcx, Y * 3) - 0.5) * 1.0
            if abs(d - 0.62) < 0.13: val = 5.0 if v - 0.9 > -0.2 else 4.2                         # the ring
            elif abs(d - 0.62) < 0.2: val = 2.4
            elif 0.82 < d < 1.08 and (math.atan2(v - 0.9, u) * 8 / math.pi) % 1 < 0.3: val = 4.6   # rays
        c = tone(GRAVE, val, x, y)
        run = n3(X * 3.0 + pcx, 2.0)
        if run > 0.62: c = mix(c, (14, 16, 14), min(0.4, (run - 0.62) * 2.0))
        return fogged(c, z)
    rs.quad((pcx - 1.3, 5.6, ZG - 0.02), (pcx + 1.3, 5.6, ZG - 0.02), (pcx - 1.3, 10.2, ZG - 0.02), panel, cls='wall')
    LANTERNS.append((pcx, 14.3, ZG + 1.75))

def lantern(cx, y0, zc):
    """an iron lantern: four glass panes lit warm behind a cage of bars, a pointed cap, a ring on top"""
    def glass(x, y, s, t, z, wp):
        if s < 0.12 or s > 0.88 or t < 0.08 or t > 0.9: return fogged(tone(IRON, 2.6 - s, x, y), z)
        if abs(s - 0.5) < 0.05: return fogged(IRON[1], z)
        if abs(t - 0.52) < 0.04: return fogged(IRON[2], z)
        v = 3.4 - abs(s - 0.5) * 2.4 + (0.4 if (x + y) % 3 == 0 else 0) - (1.2 if t > 0.78 else 0)
        return ri(GLOW, v)
    def side(x, y, s, t, z, wp):
        if s < 0.15 or s > 0.85 or t < 0.08 or t > 0.9: return fogged(tone(IRON, 1.6, x, y), z)
        return ri(GLOW, 1.8 + (0.6 if (x + y) % 3 == 0 else 0))
    rs.box(cx - 0.62, cx + 0.62, y0, y0 + 0.25, zc - 0.62, zc + 0.62, lambda x, y, s, t, z, wp: fogged(tone(IRON, 2.8, x, y), z),
           lambda x, y, s, t, z, wp: fogged(tone(IRON, 1.8, x, y), z), top=lambda x, y, s, t, z, wp: fogged(IRON[3], z), cls='prop')
    rs.box(cx - 0.5, cx + 0.5, y0 + 0.25, y0 + 1.9, zc - 0.5, zc + 0.5, glass, side, cls='emit')
    def capf(x, y, s, t, z, wp):
        u = (s - 0.5) * 2
        if abs(u) > 1 - t ** 0.8: return None
        return fogged(tone(IRON, 3.4 - u * 1.4 - t, x, y), z)
    rs.quad((cx - 0.75, y0 + 1.9, zc - 0.55), (cx + 0.75, y0 + 1.9, zc - 0.55), (cx - 0.75, y0 + 2.9, zc - 0.55), capf, cls='prop', cut=True)
    rs.quad((cx - 0.75, y0 + 1.9, zc + 0.6), (cx + 0.75, y0 + 1.9, zc + 0.6), (cx - 0.75, y0 + 2.75, zc + 0.6), capf, cls='prop', cut=True)
    rs.disc(cx, y0 + 3.15, zc - 0.5, 0.26, lambda x, y, a, b, z, wp: fogged(tone(IRON, 3.6 - a - b, x, y), z) if a * a + b * b > 0.2 else None)
for (cx, y0, zc) in LANTERNS: lantern(cx, y0, zc)

# ---------------------------------------------------------------------------------------------------- the leaves
def leaf_top(X): return 12.0 + 2.6 * math.sqrt(max(0.0, 1 - (X / GX0) ** 2))
def spear(X, Y, Z, h=0.95, w=0.34):
    """a spearhead finial: a lozenge on a collar"""
    def sh(x, y, s, t, z, wp):
        u = (s - 0.5) * 2
        if t < 0.18: return fogged(tone(IRON, 3.0 - u, x, y), z) if abs(u) < 0.55 else None
        tt = (t - 0.18) / 0.82
        if abs(u) > (tt / 0.35 if tt < 0.35 else (1 - tt) / 0.65): return None
        return fogged(tone(IRON, 3.6 - u * 1.8 + (0.6 if tt > 0.7 else 0), x, y), z)
    rs.quad((X - w / 2, Y, Z), (X + w / 2, Y, Z), (X - w / 2, Y + h, Z), sh, cls='prop', cut=True)
def ring(cx, cy, Z, r, w=0.12, n=20):
    iron_curve(rs, [(cx + math.cos(2 * math.pi * i / n) * r, cy + math.sin(2 * math.pi * i / n) * r, Z) for i in range(n + 1)], w=w, v0=2.8)
BARS = [-GX0 + 0.2 + i * 0.62 for i in range(int((2 * GX0 - 0.4) / 0.62) + 1)]
for X in BARS:
    if abs(X) < 0.3: continue
    top = leaf_top(X)
    bar_v(rs, X, 0.35, top + 0.1, ZL, w=0.26, rust=0.3, seed=int(X * 10))
    spear(X, top, ZL)
for X in BARS[:-1]:                                                                  # dog bars between them at the foot
    Xm = X + 0.31
    if abs(Xm) < 0.3: continue
    bar_v(rs, Xm, 0.35, 3.3, ZL, w=0.2, rust=0.4, seed=int(Xm * 10) + 5)
    spear(Xm, 3.3, ZL, h=0.5, w=0.24)
for X in (-GX0, GX0, -0.18, 0.18):                                                    # the stiles
    bar_v(rs, X, 0.2, leaf_top(X) + 0.2, ZL - 0.05, w=0.42 if abs(X) > 1 else 0.36, rust=0.35, seed=int(X * 10) + 11)
def rail(Y, w=0.3):
    for (a, b) in ((-GX0, -0.18), (0.18, GX0)):
        rs.quad((a, Y - w / 2, ZL - 0.06), (b, Y - w / 2, ZL - 0.06), (a, Y + w / 2, ZL - 0.06),
                lambda x, y, s, t, z, wp: fogged(tone(IRON, 2.2 + t * 1.6 + (0.5 if (x * 3 + y) % 7 == 0 else 0), x, y), z), cls='prop')
for Y in (0.5, 3.3, 4.5, 10.4):
    rail(Y)
for (a, b) in ((-GX0, -0.18), (0.18, GX0)):                                            # the arched top rail
    pts = [(a + (b - a) * i / 24, 0.0, ZL - 0.06) for i in range(25)]
    pts = [(p[0], leaf_top(p[0]) - 0.1, p[2]) for p in pts]
    iron_curve(rs, pts, w=0.32, v0=3.0)
for i, X in enumerate(BARS[:-1]):                                                     # rings between the band rails, scrolls up top
    Xm = X + 0.31
    if abs(Xm) < 0.4: continue
    ring(Xm, 3.9, ZL - 0.08, 0.26, w=0.09, n=14)
    y0 = 10.4; y1 = leaf_top(Xm) - 0.15
    if y1 - y0 > 1.0:
        sgn = 1 if Xm < 0 else -1
        iron_curve(rs, scroll(Xm, y0 + 0.55, ZL - 0.08, 0.28, turns=1.2, sign=sgn, start=-math.pi / 2), w=0.08, v0=2.8)
        if y1 - y0 > 2.2: iron_curve(rs, scroll(Xm, y0 + 1.5, ZL - 0.08, 0.3, turns=1.2, sign=-sgn, start=math.pi / 2), w=0.08, v0=2.8)
# hinges: heavy straps on the hinge stiles
for sgn in (-1, 1):
    for Y in (1.6, 8.6):
        rs.quad((sgn * GX0 - 0.35 * sgn, Y, ZL - 0.12), (sgn * GX0 - 1.4 * sgn, Y, ZL - 0.12), (sgn * GX0 - 0.35 * sgn, Y + 0.42, ZL - 0.12),
                lambda x, y, s, t, z, wp: fogged(tone(IRON, 2.0 + t * 1.6, x, y), z), cls='prop')

# ---------------------------------------------------------------------------------------------------- the overthrow
ZO = ZL - 0.1
YC, R0 = 11.64, 7.96                                                                  # the inner arch: through the pillar tops, peak 19.6
def arc(R, n=60, X0=-GX0, X1=GX0):
    out = []
    for i in range(n + 1):
        X = X0 + (X1 - X0) * i / n
        out.append((X, YC + math.sqrt(max(0.0, R * R - X * X)), ZO))
    return out
inner, outer = arc(R0), arc(R0 + 1.5, X0=-GX0 - 0.6, X1=GX0 + 0.6)
inner = [(p[0], max(p[1], 13.9), p[2]) for p in inner]; outer = [(p[0], max(p[1], 13.9), p[2]) for p in outer]
iron_curve(rs, inner, w=0.34, v0=3.0); iron_curve(rs, outer, w=0.36, v0=3.2)
for i in range(1, 12):                                                                # spokes and scrolls between the bands
    a = math.pi * (0.1 + 0.8 * i / 12)
    p0 = (math.cos(a) * R0, YC + math.sin(a) * R0, ZO); p1 = (math.cos(a) * (R0 + 1.5), YC + math.sin(a) * (R0 + 1.5), ZO)
    if p0[1] < 14.0: continue
    iron_line(rs, p0, p1, w=0.14, v0=2.8)
for i in range(11):                                                                   # rings between the spokes
    a = math.pi * (0.1 + 0.8 * (i + 0.5) / 12)
    R = R0 + 0.75
    if YC + math.sin(a) * R < 14.4: continue
    ring(math.cos(a) * R, YC + math.sin(a) * R, ZO, 0.42, w=0.1, n=16)
for i in range(13):                                                                   # upright spikes along the outer band
    X = -GX0 + 0.6 + (2 * GX0 - 1.2) * i / 12
    Y = YC + math.sqrt(max(0.0, (R0 + 1.5) ** 2 - X * X))
    if Y < 14.2 or abs(X) < 1.0: continue
    L = 0.7 + 0.5 * (1 - abs(X) / GX0)
    bar_v(rs, X, Y - 0.1, Y + L, ZO, w=0.16, rust=0.1, seed=i)
    spear(X, Y + L, ZO, h=0.7, w=0.3)
# the crest: a halo of rays round a ring, on a spike
CY = YC + R0 + 1.5 + 1.6
ring(0.0, CY, ZO, 0.9, w=0.16, n=28); ring(0.0, CY, ZO, 0.45, w=0.1, n=18)
for k in range(16):
    a = 2 * math.pi * k / 16
    L = 0.55 if k % 2 else 0.95
    iron_line(rs, (math.cos(a) * 1.0, CY + math.sin(a) * 1.0, ZO), (math.cos(a) * (1.0 + L), CY + math.sin(a) * (1.0 + L), ZO), w=0.1, v0=3.0)
iron_line(rs, (0.0, YC + R0 + 1.5, ZO), (0.0, CY - 0.9, ZO), w=0.16, v0=3.0)
# the plate hangs from the inner band on two short bars
for sgn in (-1, 1):
    X = sgn * 4.0
    iron_line(rs, (X, 17.5, ZO), (X, YC + math.sqrt(R0 * R0 - X * X), ZO), w=0.14, v0=2.8)
# the name plate
PL = (-5.0, 5.0, 15.95, 17.6, ZO - 0.05)
def plate(x, y, s, t, z, wp):
    X, Y, Z = wp
    if s < 0.025 or s > 0.975 or t < 0.09 or t > 0.91: return fogged(tone(IRON, 2.8 + t * 1.2, x, y), z)
    v = 6.2 + (n2(X * 2.4, Y * 2.4) - 0.5) * 1.4 + (n3(X * 7, Y * 7) - 0.5) * 0.8 - (1.4 if t < 0.25 else 0)
    c = tone(LIME, v, x, y)
    if n1(X * 4.0 + 9, Y * 2.0) > 0.7: c = tone(RUSTI, 2.6, x, y)                      # rust bleeding through the enamel
    elif n1(X * 4.0 + 9, Y * 2.0) > 0.66: c = mix(c, (60, 44, 30), 0.4)
    if (x, y) in LET: c = tone(IRON, 1.2 + LET[(x, y)] * 1.4, x, y)
    elif (x - 1, y - 1) in LET: c = mix(c, (20, 18, 14), 0.4)
    return fogged(c, z)
LET = {}
rs.quad((PL[0], PL[2], PL[4]), (PL[1], PL[2], PL[4]), (PL[0], PL[3], PL[4]), plate, cls='prop')
for sgn in (-1, 1):                                                                   # the plate's end scrolls
    iron_curve(rs, scroll(sgn * 5.45, 16.78, ZO - 0.05, 0.62, turns=1.25, sign=-sgn, start=0.0 if sgn > 0 else math.pi), w=0.14, v0=3.0)

def build_letters():
    (ax, ay) = proj(PL[0] + 0.5, PL[3] - 0.2, PL[4]); (bx, by) = proj(PL[1] - 0.5, PL[2] + 0.2, PL[4])
    w, h = int(bx - ax), int(by - ay)
    im = Image.new('L', (w, h), 0); d = ImageDraw.Draw(im); d.fontmode = '1'
    path = '/usr/share/fonts/TTF/DejaVuSerifCondensed-Bold.ttf'
    if NONAME:                                                                        # an emblem only: a ring and two rays
        cxm, cym = w // 2, h // 2
        for yy in range(h):
            for xx in range(w):
                r = math.hypot(xx - cxm, (yy - cym) * 1.2)
                if abs(r - h * 0.33) < 1.2 or (abs(yy - cym) < 1 and h * 0.5 < abs(xx - cxm) < w * 0.42): im.putpixel((xx, yy), 255)
    elif os.path.exists(path):
        size = 40
        while size > 6:
            f = ImageFont.truetype(path, size); bb = d.textbbox((0, 0), 'GODGRAVEYARD', font=f)
            if bb[2] - bb[0] <= w and bb[3] - bb[1] <= h: break
            size -= 1
        d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], (h - (bb[3] - bb[1])) / 2 - bb[1]), 'GODGRAVEYARD', font=f, fill=255)
    else:
        draw_text(lambda x, y: (0 <= x < w and 0 <= y < h) and im.putpixel((x, y), 255), 'GODGRAVEYARD', (w - text_width('GODGRAVEYARD', 2)) // 2, 2, 2)
    p = im.load(); m = {}
    for y in range(h):
        for x in range(w):
            if p[x, y]: m[(int(ax) + x, int(ay) + y)] = 1 if (y < 1 or not p[x, y - 1]) else 0
    return m
LET.update(build_letters())

# ---------------------------------------------------------------------------------------------------- the seals: chain, padlocks, wax
ZC = ZL - 0.3
def link_chain(P0, P1, n, sag=0.0):
    """a heavy chain: links alternately seen face-on (a ring) and edge-on (a bar)"""
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        def at(t): return (P0[0] + (P1[0] - P0[0]) * t, P0[1] + (P1[1] - P0[1]) * t - sag * math.sin(math.pi * t), ZC)
        a, b = at(t0), at(t1)
        if i % 2 == 0:
            cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            ang = math.atan2(b[1] - a[1], b[0] - a[0])
            pts = []
            for k in range(17):
                th = 2 * math.pi * k / 16
                ex, ey = math.cos(th) * 0.36, math.sin(th) * 0.2
                pts.append((cx + ex * math.cos(ang) - ey * math.sin(ang), cy + ex * math.sin(ang) + ey * math.cos(ang), ZC))
            iron_curve(rs, pts, w=0.13, v0=4.6)
        else:
            iron_line(rs, (a[0], a[1], ZC - 0.05), (b[0], b[1], ZC - 0.05), w=0.16, v0=3.8)
link_chain((-2.6, 8.4), (2.6, 5.4), 12, sag=0.3)
link_chain((-2.6, 5.4), (2.6, 8.4), 12, sag=0.3)
link_chain((-2.6, 8.4), (-2.6, 5.4), 6); link_chain((2.6, 5.4), (2.6, 8.4), 6)
def padlock(cx, cy, Z, w, h, ramp_, worn, seed):
    """a padlock: a verdigris-green body, darker round the keyhole, a shackle arc"""
    def body(x, y, s, t, z, wp):
        u, v = (s - 0.5) * 2, t
        if v < 0.3 and math.hypot(u, (0.3 - v) / 0.3) > 1: return None
        X, Y, _ = wp
        val = 3.6 - u * 1.2 + (n2(X * 6 + seed, Y * 6) - 0.5) * 2.0 * worn + (0.8 if v > 0.86 else 0)
        c = tone(ramp_, val, x, y)
        if abs(u) < 0.13 and 0.35 < v < 0.6 or (math.hypot(u, (v - 0.62) * 1.2) < 0.17): c = tone(IRON, 0.6, x, y)   # keyhole
        elif n1(X * 9 + seed, Y * 9) > 0.7 and worn > 0.5: c = tone(RUSTI, 2.4, x, y)
        return fogged(c, z)
    rs.quad((cx - w / 2, cy - h, Z), (cx + w / 2, cy - h, Z), (cx - w / 2, cy, Z), body, cls='prop', cut=True)
    pts = [(cx + math.cos(math.pi * k / 16) * w * 0.32, cy + math.sin(math.pi * k / 16) * h * 0.5, Z + 0.02) for k in range(17)]
    iron_curve(rs, pts, w=0.16, v0=3.6)
padlock(0.0, 6.5, ZC - 0.25, 1.45, 1.7, VERDI, 0.6, 1)                                 # the big one, at the crossing
padlock(0.25, 2.9, ZC - 0.2, 0.85, 1.0, ramp('#18261d #213529 #2c4836 #3a5e46 #4c7658'), 1.0, 2)   # older, greener
iron_line(rs, (-0.4, 3.0, ZC - 0.1), (-0.4, 4.4, ZC - 0.1), w=0.1, v0=2.6); iron_line(rs, (0.9, 3.0, ZC - 0.1), (0.9, 4.4, ZC - 0.1), w=0.1, v0=2.6)
def seal_strip(Y, X0, X1, Z, seed):
    """a paper seal strip pasted across the meeting stiles, a red wax seal pressed on its middle, a torn ribbon"""
    def paper(x, y, s, t, z, wp):
        X, Yw, _ = wp
        if t < 0.08 + 0.1 * n1(X * 8 + seed, 1.0) or t > 0.92 - 0.1 * n1(X * 8 + seed, 2.0): return None
        v = 3.2 + (n2(X * 4 + seed, Yw * 4) - 0.5) * 1.6 - (1.0 if (h32(int(X * 6 + 99), seed) % 5 == 0) else 0)
        c = tone(PAPER, v, x, y)
        if 0.3 < t < 0.7 and abs(s - 0.5) > 0.16 and (int((X + 9) * 7) % 3 == 0) and h32(int((X + 9) * 7), seed) % 3: c = tone(PAPER, 1.0, x, y)   # stamped text
        if n1(X * 2 + seed, Yw * 2) > 0.62: c = mix(c, (60, 52, 34), 0.45)                       # water stains
        return fogged(c, z)
    rs.quad((X0, Y - 0.32, Z), (X1, Y - 0.32, Z), (X0, Y + 0.32, Z), paper, cls='prop', cut=True)
    def wax(x, y, a, b, z, wp):
        d = math.hypot(a, b)
        e = 0.9 + 0.1 * math.sin(math.atan2(b, a) * 5 + seed)
        if d > e: return None
        v = 4.0 - (a + b) * 1.2 - (1.4 if abs(d - 0.55) < 0.08 else 0) + (1.0 if d < 0.25 and (x + y) % 2 else 0)
        return fogged(tone(WAX, v, x, y), z)
    rs.disc((X0 + X1) / 2 + 0.05, Y, Z - 0.06, 0.48, wax, cls='prop')
    for k, dx in enumerate((-0.15, 0.2)):
        rs.line3(((X0 + X1) / 2 + dx, Y - 0.3, Z - 0.05), ((X0 + X1) / 2 + dx * 2.2, Y - 1.3 - k * 0.3, Z - 0.05),
                 lambda x, y, s, t, z, wp: fogged(tone(WAX, 2.6 + (1 if (x + y) % 3 else 0), x, y), z), w=0.12)
seal_strip(10.0, -1.5, 1.6, ZL - 0.2, 3)
seal_strip(1.6, -1.3, 1.4, ZL - 0.2, 4)

# ---------------------------------------------------------------------------------------------------- walls with railings
def wall_line(A, B, seed):
    """a low ashlar wall from A to B (x, z on the ground) with a coping, spear railings on it"""
    (ax, az), (bx, bz) = A, B
    L = math.hypot(bx - ax, bz - az)
    def face(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = s * L
        row = math.floor(Y / 1.0); off = (row % 2) * 0.8
        fu = ((u + off) / 1.6) % 1; fv = (Y / 1.0) % 1
        px = z / F
        if fu * 1.6 < px * 1.1 or fv < px * 1.1: return fogged(tone(GRAVE, 1.4, x, y), z)
        v = 4.2 + (h32(math.floor((u + off) / 1.6), row, seed) % 5 - 2) * 0.4 + (n2(u * 1.3, Y * 1.3) - 0.5) * 1.2
        c = tone(GRAVE, v, x, y)
        if n1(u * 0.8 + seed, Y * 0.8) > 0.58: c = tone(MOSSR, 2.6 + (v - 4.2) * 0.5, x, y)
        return fogged(c, z)
    rs.quad((ax, 0, az), (bx, 0, bz), (ax, 2.0, az), face, cls='wall')
    nx, nz = -(bz - az) / L, (bx - ax) / L                                          # into the wall (away from the lane)
    if nz < 0: nx, nz = -nx, -nz
    rs.quad((ax, 2.0, az), (bx, 2.0, bz), (ax + nx * 1.1, 2.0, az + nz * 1.1), cap_sh(5.2), cls='wall')
    rs.quad((ax, 2.0, az), (bx, 2.0, bz), (ax, 2.3, az), cap_sh(5.8), cls='wall')
    k = 0; d = 0.35
    mx, mz = nx * 0.55, nz * 0.55
    while d < L - 0.2:
        X, Z = ax + (bx - ax) * d / L + mx, az + (bz - az) * d / L + mz
        rs.line3((X, 2.3, Z), (X, 8.0, Z), lambda x, y, s, t, z, wp: fogged(tone(IRON, 2.4 + (0.6 if y % 4 == 0 else 0), x, y), z), w=0.2)
        rs.line3((X, 8.0, Z), (X, 8.9, Z), lambda x, y, s, t, z, wp: fogged(tone(IRON, 3.2 - t, x, y), z), w=0.32 * (1.0), n=6)
        d += 0.68; k += 1
    for Y in (2.9, 7.4):
        rs.line3((ax + mx, Y, az + mz), (bx + mx, Y, bz + mz), lambda x, y, s, t, z, wp: fogged(tone(IRON, 2.6, x, y), z), w=0.22)
for sgn in (-1, 1):
    wall_line((sgn * (GX1 + 0.35), ZG + 1.6), (sgn * 19.0, ZW), 20 + sgn)
    wall_line((sgn * 19.0, ZW), (sgn * 75.0, ZW), 30 + sgn)
    # a square pier where the wall turns
    rs.box(sgn * 19.0 - 0.9, sgn * 19.0 + 0.9, 0, 4.2, ZW - 0.9, ZW + 0.9, ashlar(4.6, bh=1.05, bw=1.0, seed=40 + sgn),
           ashlar(4.0, bh=1.05, bw=1.0, along_z=True, seed=42 + sgn), top=cap_sh(5.0), cls='wall')
    rs.box(sgn * 19.0 - 1.1, sgn * 19.0 + 1.1, 4.2, 4.7, ZW - 1.1, ZW + 1.1, cap_sh(5.6), cap_sh(4.4), top=cap_sh(5.8), cls='wall')
    rs.disc(sgn * 19.0, 5.25, ZW, 0.6, lambda x, y, a, b, z, wp: fogged(tone(GRAVE, 5.4 - a * 1.5 - b * 1.5, x, y), z))

# ---------------------------------------------------------------------------------------------------- trees
tree(rs, -27.0, 29.0, 3, h=36.0, trunk=1.0, lean=-0.08, side=-1, limbs=4)
tree(rs, 28.0, 32.0, 5, h=38.0, trunk=1.1, lean=0.06, side=1, limbs=4)
tree(rs, -46.0, 54.0, 7, h=30.0, trunk=0.9, lean=0.1, side=-1, limbs=3, fogk=0.8)
tree(rs, 47.0, 60.0, 9, h=28.0, trunk=0.9, lean=-0.08, side=1, limbs=3, fogk=0.8)
tree(rs, -16.0, 48.0, 11, h=24.0, trunk=0.7, lean=-0.04, limbs=3, fogk=0.8)

# ---------------------------------------------------------------------------------------------------- foreground
def bollard(X, Z, seed):
    def sh(x, y, s, t, z, wp):
        u = (s - 0.5) * 2
        if t > 0.85 and math.hypot(u, (t - 0.85) / 0.15 * 0.9) > 1.0: return None
        X_, Y_, _ = wp
        v = 4.4 - u * 1.2 + (n2(X_ * 3, Y_ * 3) - 0.5) * 1.4 + (0.8 if t > 0.8 else 0)
        c = tone(GRAVE, v, x, y)
        if n1(X_ * 2 + seed, Y_ * 2) > 0.55 or t < 0.2: c = tone(MOSSR, 2.6 - u * 0.6, x, y)
        return fogged(c, z)
    rs.quad((X - 0.8, -0.1, Z), (X + 0.8, -0.1, Z), (X - 0.8, 2.3, Z), sh, cls='prop', cut=True)
    rs.quad((X + (0.8 if X < 0 else -0.8), -0.1, Z), (X + (0.8 if X < 0 else -0.8), -0.1, Z + 1.4), (X + (0.8 if X < 0 else -0.8), 2.0, Z),
            lambda x, y, s, t, z, wp: fogged(tone(GRAVE, 2.8, x, y), z), cls='prop')
bollard(-8.4, 16.4, 1); bollard(8.4, 16.4, 2)
for k in range(46):                                                                    # grass and weeds on the verges
    side = -1 if k % 2 else 1
    Z = 11.0 + (h32(k, 1) % 120) / 10.0
    X = side * (lane_half(Z) + 0.4 + (h32(k, 2) % 140) / 10.0)
    tuft(rs, X, Z, 100 + k, h=0.7 + (h32(k, 3) % 10) / 10.0, n=12, ramp_=STRAW if k % 3 else MOSSR, spread=0.6, w=0.03, v0=2.0)
for k in range(16):                                                                    # taller dead grass in the near corners
    side = -1 if k % 2 else 1
    X = side * (13.0 + (h32(k, 5) % 80) / 10.0); Z = 9.0 + (h32(k, 6) % 40) / 10.0
    tuft(rs, X, Z, 200 + k, h=1.6 + (h32(k, 7) % 12) / 10.0, n=16, ramp_=STRAW, spread=0.9, v0=1.8, w=0.025)
DLEAF = ramp('#2a1d12 #3c2a18 #4f3820 #634629')
for k in range(30):                                                                    # dead leaves on the cobbles
    fx = (h32(k, 21) % 120 - 60) / 10.0; fz = 12.0 + (h32(k, 22) % 140) / 10.0
    a = (h32(k, 23) % 628) / 100.0; c_, s_ = math.cos(a) * 0.22, math.sin(a) * 0.22
    col = tone(DLEAF, 1 + h32(k, 24) % 3, 0, 0)
    rs.quad((fx - c_, 0.02, fz - s_), (fx + s_, 0.02, fz - c_), (fx - s_, 0.02, fz + c_), lambda x, y, s, t, z, wp, c=col: fogged(c, z), cls='prop')

# ---------------------------------------------------------------------------------------------------- render
img = rs.render(INK, fog=fog_of, overlay=None,
                light_gain=1.1, grime_gain=1.0, bloom=0.4, stain_gain=1.0, damp_gain=1.0)
ground_mist(img, rs, top=4.0, dens=0.018, banks=0.7, far=0.62, horizon=0.85,
            wisps=((-30, -3, 2.6, 40.0, 1.6), (4, 26, 3.4, 52.0, 2.0), (-60, -20, 2.0, 28.0, 1.2), (18, 60, 1.8, 30.0, 1.1)),
            glow=(533, 300, 380, (150, 164, 150), 0.6))
img.save(f'{OUT}/gate.png')
print('done gate', 'noname' if NONAME else '')
