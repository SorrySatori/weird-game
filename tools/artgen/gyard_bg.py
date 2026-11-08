"""The Godgraveyard (GodgraveyardScene with the Townhall's leave), 1067x600, overcast day, the shared camera
(raster3d.py). After the old art (Godgraveyard.png): a misty field of colossal god-tombs under the overcast. Big
monuments near, more and more of them fading into the fog: one-point depth along a broken flagstone path from the
viewer to the great fallen face. Each grave the scene lets you read is carved for its god:
  * Laimig Cel, Who Lost the Game -- the big leaning arched stele on the left: a game board in a gilt ring, a hand of
    cards laid face down (I FOLD), rows of worn inscription; at its foot the stone king, tipped over (he resigned).
  * Sisyla, the Unwaking -- the tall gabled stele: a crescent finial, a great CLOSED eye with lashes in a roundel of
    rays, moon phases, and a blind arcade at its foot: four arches that are not doors (SLEEP HAS NO DOOR).
  * the Fallen God -- a face the size of a house half-swallowed by the mud, tilted back, brows up, eyes and mouth wide
    open (still looking surprised), a crown of stone spikes, a broken godmetal halo standing behind it; a piece of the
    halo lies in the mud to the right.
  * Vhorn the Tally-Keeper -- the narrow stele right of the face: an abacus in its arch, rows of tally marks down a
    sunk panel, the last row unfinished, split by a crack.
  * Liln of Small Mercies -- a small plain limestone headstone among the giants, two cupped hands holding a crust;
    someone has left a few wildflowers.
  * Lietus Kika, of Temporal Confusion -- a stone clock dial on a plinth with too many hours and three hands, one half
    crisp, the other worn as if centuries older.
  * Hvetrdjaana -- the low leaning slab near right: a veiled figure with no face in a niche, rows of a script nobody can
    read, worn nearly away.
On the far left the ossuary niche (a small gabled shrine full of stacked skulls) where Osswine waits -- the pale dry
growth on the skulls is its own sprite (osswine.png; the scene drops it once Osswine is bonded).
No people, no mushrooms (nothing in the scene's text calls for them): moss, lichen, dead grass, heather, mist.

    python3 gyard_bg.py <outdir>   ->  gyard.png    (assets/images/backgrounds/Godgraveyard.png)
                                       osswine.png  (assets/images/props/gyard_osswine.png; prints its top-left)
                                       gyard.json   (canvas hit polygons of the graves, the face, the niche)
                                       gyard.gpl    (Aseprite palette of the ramps, shared with the gate)
"""
import sys, math, json
from PIL import Image
from common import h32
import gyard_kit as K
from gyard_kit import *
from pal_day import FLOWER, LEAF, BONE

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
K.FOGCFG.update(scale=58.0, max=0.88)
fog_of, fogged = K.fog_of, K.fogged
rs = Raster()
HITS = {}
def at_x(x, Z): return (x - CX) * Z / F
def gy(Z): return HY + F * CAMH / Z

# ---------------------------------------------------------------------------------------------------- sky
rs.quad((-1400, 800, 600), (1400, 800, 600), (-1400, -300, 600), sky, cls='sky')

# ---------------------------------------------------------------------------------------------------- ground
PATH = [(1.2, 6.0), (-0.3, 12.0), (0.9, 18.0), (0.1, 24.0), (0.5, 30.0), (0.3, 33.0)]
def path_x(Z):
    if Z <= PATH[0][1]: return PATH[0][0]
    for (x0, z0), (x1, z1) in zip(PATH, PATH[1:]):
        if Z <= z1:
            t = (Z - z0) / (z1 - z0); t = t * t * (3 - 2 * t)
            return x0 + (x1 - x0) * t
    return PATH[-1][0]
MOUNDS = [(-6.0, 17.0, 3.0, 1.4), (6.5, 22.0, 3.4, 1.6), (-9.0, 28.0, 3.0, 1.5), (12.0, 16.0, 2.6, 1.2), (-4.0, 36.0, 3.4, 1.6),
          (9.0, 34.0, 3.0, 1.4), (17.0, 26.0, 2.8, 1.3), (-17.0, 34.0, 3.0, 1.4), (3.5, 44.0, 3.0, 1.5), (-12.0, 48.0, 3.4, 1.6)]
def terrain(X, Z):
    """grave mounds (long low humps) and lumpy earth -- used for shading only, the ground stays flat"""
    hgt = (n1(X * 0.35, Z * 0.35) - 0.5) * 0.9 + (n2(X * 1.3, Z * 1.3) - 0.5) * 0.25
    for (mx, mz, ml, mw) in MOUNDS:
        d = ((X - mx) / mw) ** 2 + ((Z - mz) / ml) ** 2
        if d < 1: hgt += 0.55 * (1 - d) ** 1.5
    return hgt
def puddle(X, Z):
    """no standing water: it read as dark holes in front of the dark stones (kept as a hook for the ground shader)"""
    return 0.0
GL = (-0.4, 0.85, -0.35); _g = math.sqrt(sum(c * c for c in GL)); GL = tuple(c / _g for c in GL)
def ground(x, y, s, t, z, wp):
    X, _, Z = wp
    e = 0.12
    hx = (terrain(X + e, Z) - terrain(X - e, Z)) / (2 * e); hz = (terrain(X, Z + e) - terrain(X, Z - e)) / (2 * e)
    nl = math.sqrt(hx * hx + 1 + hz * hz)
    lit = ((-hx) * GL[0] + GL[1] + (-hz) * GL[2]) / nl - GL[1]
    pd = puddle(X, Z)
    # the flagstone path
    dx = X - path_x(Z)
    pw = 1.9 + (n1(Z * 0.7, 9.0) - 0.5) * 0.5
    if abs(dx) < pw and Z < 33.5 and pd < 0.3:
        row = math.floor(Z / 1.15); off = (row % 2) * 0.9
        col_ = math.floor((dx + off) / 1.8)
        fz, fx = (Z / 1.15) % 1, ((dx + off) / 1.8) % 1
        jz, jx = 1.1 * Z * Z / (F * CAMH) / 1.15, 1.1 * Z / F / 1.8
        lost = h32(col_, row, 3) % 7 == 0 or abs(dx) > pw - 0.35 - 0.3 * h01(row, col_)
        if not lost:
            if fz < jz or fx < jx: return fogged(tone(MUD, 1.6, x, y), Z)
            tilt = (h01(col_, row, 5) - 0.5) * 1.4
            v = 4.6 + tilt + lit * 2.0 + (n3(X * 3, Z * 3) - 0.5) * 0.9 - (0.7 if fz < jz * 2.5 else 0) + (0.5 if fz > 1 - jz * 2 else 0)
            c = tone(GRAVE, v, x, y)
            if n2(X * 1.1 + 40, Z * 1.1) > 0.6 or fx < jx * 3 or fz < jz * 3.5: c = tone(MOSSR, 2.8 + tilt * 0.6 + lit * 2, x, y) if n1(X * 5, Z * 5) > 0.35 else c
            if h32(col_, row, 9) % 5 == 0 and abs(fx - 0.3 - fz * 0.4) < jx * 1.2: c = tone(MUD, 1.4, x, y)       # a crack
            return fogged(c, Z)
    # earth: dark peaty soil under a thin cover of dead grass (speckled in by a world-space hash, so cover fades in and
    # out without hard-edged blobs), a little moss, heather in small clusters
    bv = 2.2 + lit * 2.6 + (n2(X * 0.7, Z * 0.7) - 0.5) * 0.8 + (n3(X * 3.5, Z * 3.5) - 0.5) * 0.7 - 0.7 * clamp((15.5 - Z) / 3.5)
    c = tone(MUD, bv + 1.2, x, y)
    hs = h01(int(X * 18 + 9999), int(Z * 12 + 9999), 7)
    g = n1(X * 0.22 + 30, Z * 0.22) + (n2(X * 1.1, Z * 1.1) - 0.5) * 0.25
    pg = smooth((g - 0.28) / 0.4)
    if hs < pg * 0.8: c = tone(STRAW, bv - 0.2 + (1.0 if hs < pg * 0.25 else 0), x, y)
    elif hs > 0.9 and g > 0.35: c = tone(MOSSR, bv + 0.6, x, y)
    hv = n2(X * 0.45 + 60, Z * 0.45)
    if hv > 0.68 and h01(int(X * 14 + 999), int(Z * 9 + 999), 11) < (hv - 0.68) * 3.5:
        c = tone(HEATH, 1.2 + lit * 2 + (hv - 0.68) * 6, x, y)
    if pd > 0:
        return fogged(mix(c, (16, 20, 19), min(1.0, pd * 1.4) * 0.55), Z)
    return fogged(c, Z)
rs.quad((-180, 0, 3), (180, 0, 3), (-180, 0, 340), ground, cls='ground')

# ---------------------------------------------------------------------------------------------------- the field fading into the fog
def far_shape(X, Z, w, h, kind, seed, v0=2.8, fk=0.78):
    """a monument far off: a camera-facing card cut to its shape, a little side light, the fog does the rest"""
    def sh(x, y, s, t, z, wp):
        u = (s - 0.5) * 2; e = (n1(s * 9 + seed, t * 9) - 0.5) * 0.06
        if kind == 'stele':
            if abs(u) > 0.8 + e: return None
            if t > 0.8 and math.hypot(u, (t - 0.8) / 0.2 * 0.8) > 0.8 + e: return None
        elif kind == 'gable':
            if abs(u) > 0.75 + e or t > 0.84 + 0.16 * (1 - abs(u) / 0.75) + e: return None
        elif kind == 'horned':
            body = abs(u) < 0.5 + e and t < 0.6
            hu = abs(u) - 0.5 + 0.28 * math.sin(clamp((t - 0.52) / 0.48) * math.pi * 0.9)
            horn = 0.52 < t < 1.0 and abs(hu) < 0.1 * (1 - (t - 0.52) / 0.48) + 0.02
            dome_ = t < 0.72 and abs(u) < 0.32 * math.sqrt(max(0.0, 1 - ((t - 0.6) / 0.12) ** 2)) if t > 0.6 else False
            if not (body or horn or dome_): return None
        elif kind == 'dome':
            body = t < 0.56 and abs(u) < 0.72 * math.sqrt(max(0.0, 1 - max(0.0, t - 0.28) ** 2 / 0.08)) + e
            ringv = abs(math.hypot(u, (t - 0.8) * 1.3) - 0.24) < 0.05
            if not (body or ringv or (abs(u) < 0.03 and t < 0.68)): return None
        elif kind == 'obelisk':
            if abs(u) > 0.5 * (1 - t * 0.5) + e or (t > 0.9 and abs(u) > (1 - t) * 5 * 0.5): return None
        elif kind == 'hand':                                                            # a colossal stone hand, fingers up
            palm = abs(u) < 0.62 and t < 0.55
            fingers = 0.5 < t and any(abs(u - fc) < 0.11 and t < ft for fc, ft in ((-0.45, 0.82), (-0.15, 0.97), (0.15, 0.95), (0.42, 0.84)))
            thumb = 0.25 < t < 0.6 and abs(u + 0.72 - (t - 0.25) * 0.3) < 0.1
            if not (palm or fingers or thumb): return None
        elif kind == 'wheel':
            d = math.hypot(u, (t - 0.5) * 2 * h / w)
            if d > 1 + e or (0.18 < d < 0.82 and not any(abs(math.sin(math.atan2((t - 0.5), u) - k * math.pi / 4)) < 0.09 for k in range(4))): return None
        elif kind == 'idol':                                                            # a head sunk to the chin, many eyes
            d = math.hypot(u / 0.8, (t - 0.45) / 0.55)
            if d > 1 + e: return None
        v = v0 + (0.7 if u < -0.25 else -0.4 if u > 0.4 else 0) + (n2(X + s * w, t * h) - 0.5) * 1.1
        if kind == 'idol' and any(math.hypot(u - ex, (t - ey) * 1.6) < 0.09 for ex, ey in ((-0.3, 0.55), (0.3, 0.55), (0.0, 0.7), (-0.5, 0.75), (0.5, 0.75))): v -= 1.6
        return fogged(tone(GRAVE, v, x, y), z, fk)
    rs.quad((X - w / 2, -1.2, Z), (X + w / 2, -1.2, Z), (X - w / 2, h - 1.2, Z), sh, cls='wall', cut=True)
FAR = [(552, 150, 30, 64, 'horned', 1), (760, 120, 34, 60, 'dome', 2), (905, 135, 12, 48, 'stele', 3), (1010, 170, 22, 52, 'gable', 4),
       (660, 165, 7, 58, 'obelisk', 5), (400, 140, 10, 56, 'stele', 6), (300, 175, 14, 62, 'gable', 7), (120, 160, 12, 50, 'obelisk', 8),
       (1040, 95, 16, 26, 'hand', 9), (60, 70, 14, 14, 'wheel', 10), (705, 70, 9, 12, 'idol', 11), (965, 78, 7, 16, 'stele', 12),
       (620, 90, 6, 18, 'gable', 13), (865, 90, 5, 22, 'obelisk', 14), (200, 110, 8, 30, 'stele', 15), (480, 110, 6, 26, 'gable', 16)]
for (x, Z, w, h, kind, seed) in FAR:
    far_shape(at_x(x, Z), Z, w, h, kind, seed)
def ribcage(x0, x1, Z, h, seed, fk=0.8):
    """the bones of something enormous far off in the fog: a spine along the ground, ribs curving up out of it"""
    X0, X1 = at_x(x0, Z), at_x(x1, Z)
    w = X1 - X0
    def sh(x, y, s, t, z, wp):
        if t < 0.08 and abs((s * 9) % 1 - 0.5) < 0.42: return fogged(tone(GRAVE, 3.2, x, y), z, fk)        # the spine
        for k in range(7):
            c = 0.1 + k * 0.13
            hk = (0.95 - abs(k - 3) * 0.1)
            if t > hk: continue
            bend = 0.09 * math.sin(t / hk * math.pi * 0.9) * (1 if k < 4 else 1.2)
            if abs(s - c - bend) < 0.016 * (1.4 - t / hk) + 0.004:
                if h01(seed, k) < 0.25 and t > hk * 0.7: return None                         # a broken rib
                return fogged(tone(GRAVE, 3.4 + (0.6 if s < c + bend else -0.4), x, y), z, fk)
        return None
    rs.quad((X0, -1.5, Z), (X1, -1.5, Z), (X0, h - 1.5, Z), sh, cls='wall', cut=True)
ribcage(770, 1000, 210, 70, 1)
for k in range(90):                                                                   # the countless small stones of the field
    Z = 45 + (h32(k, 2) % 2200) / 10.0
    X = at_x(20 + (h32(k, 1) % 1030), Z)
    far_shape(X, Z, 1.6 + (h32(k, 3) % 26) / 10.0, 2.4 + (h32(k, 4) % 50) / 10.0, ['stele', 'gable', 'obelisk', 'stele'][k % 4], 40 + k, v0=2.5, fk=0.8)

# ---------------------------------------------------------------------------------------------------- relief helpers
def arch_d(u, v, w, h):
    """distance inside an arched outline (to its sides and round top)"""
    r = w / 2; vs = h - r
    return r - abs(u) if v < vs else r - math.hypot(u, v - vs)
def gable_d(u, v, w, h, roof):
    side = w / 2 - abs(u)
    top = (h - roof * abs(u) / (w / 2) - v) * math.cos(math.atan2(roof, w / 2))
    return min(side, top)
def band(d, a, b, hgt=0.22):
    """a raised border band between distances a and b inside the outline, rounded"""
    if a < d < b:
        m = (d - a) / (b - a)
        return hgt * math.sin(m * math.pi) ** 0.6
    return 0.0
def glyph(u, v, cw, ch, seed, wv=0.08, worn=0.0, style='rune'):
    """one cell of a script nobody reads any more: 'rune' = a stem with ticks off it (like ogham / runes, never a Latin
    letter or a digit); 'knot' = a small lozenge or hook with a stem"""
    k = h32(seed, 1)
    if worn and h01(seed, 9) < worn: return 0.0
    a, b = u / cw, v / ch
    if not (0.08 < b < 0.92): return 0.0
    hgt = 0.0
    sx = 0.35 + 0.3 * h01(seed, 2)
    hgt = min(hgt, groove(abs(a - sx) * cw, wv, 0.22))                                  # the stem
    for j in range(1 + k % 3):                                                         # ticks off it
        ty = 0.25 + 0.5 * h01(seed, 3, j); side = 1 if h01(seed, 4, j) > 0.5 else -1
        up = 0.18 * (1 if h01(seed, 5, j) > 0.5 else -1)
        hgt = min(hgt, groove(seg_d(a * cw, b * ch, (sx * cw, ty * ch), ((sx + side * 0.42) * cw, (ty + up) * ch)), wv, 0.2))
    if style == 'knot' and (k >> 4) % 2:
        d = abs(abs(a - sx) * cw + abs(b - 0.72) * ch - 0.16 * ch)                          # a lozenge on the stem
        hgt = min(hgt, groove(d, wv, 0.2))
    if (k >> 6) % 4 == 0: hgt = min(hgt, groove(math.hypot((a - sx) * cw, (b - 0.93) * ch), wv * 1.2, 0.22))   # a dot over it
    return hgt
# ---------------------------------------------------------------------------------------------------- Laimig Cel
LW, LH = 10.6, 23.2
def laimig_relief(u, v):
    hgt = 0.0; tag = None
    d = arch_d(u, v, LW, LH)
    hgt += band(d, 0.3, 0.95, 0.24)
    vs = LH - LW / 2
    # the game board: a gilt ring round a checkered diamond
    bu, bv = u, v - vs + 0.2
    rr = math.hypot(bu, bv)
    if abs(rr - 3.55) < 0.32:
        hgt += 0.26 * math.cos((rr - 3.55) / 0.32 * math.pi / 2); tag = 'gilt'
    elif rr < 3.2:
        ru, rv = (bu + bv) / math.sqrt(2), (bv - bu) / math.sqrt(2)                       # 45 degrees
        if abs(ru) < 2.15 and abs(rv) < 2.15:
            cu, cv = math.floor((ru + 2.15) / 0.717), math.floor((rv + 2.15) / 0.717)
            hgt += -0.16 if (cu + cv) % 2 else 0.02
            fu_, fv_ = ((ru + 2.15) / 0.717) % 1, ((rv + 2.15) / 0.717) % 1
            if min(fu_, fv_, 1 - fu_, 1 - fv_) < 0.08: hgt -= 0.05
        else: hgt -= 0.08
    # a hand of cards, laid face down, fanned from a pivot
    for k, ang in enumerate((-0.42, -0.14, 0.14, 0.42)):
        ca, sa = math.cos(ang), math.sin(ang)
        pu, pv = u - 0.0, v - 7.4
        cu_, cv_ = pu * ca - pv * sa, pu * sa + pv * ca                                    # into the card's frame
        cv_ -= 2.0
        if abs(cu_) < 1.15 and abs(cv_) < 1.65:
            e = min(1.15 - abs(cu_), 1.65 - abs(cv_))
            hh = 0.16 + 0.05 * k
            if e < 0.07: hh -= 0.08
            if 0.18 < e < 0.26: hh -= 0.05                                                  # the inner border of the card's back
            if e > 0.3 and abs((cu_ * 2.2 + cv_ * 1.6) % 0.9 - 0.45) < 0.05: hh -= 0.04     # the pattern on its back
            if e > 0.3 and abs((cu_ * 2.2 - cv_ * 1.6) % 0.9 - 0.45) < 0.05: hh -= 0.04
            hgt = max(hgt, hh) if hgt >= 0 else hh
    # worn inscription: four rows under the cards
    if 1.6 < v < 4.6 and abs(u) < 3.9:
        row = math.floor((v - 1.6) / 0.75); rv_ = (v - 1.6) % 0.75
        cell = math.floor((u + 3.9) / 0.5)
        if rv_ < 0.55: hgt += glyph((u + 3.9) % 0.5, rv_, 0.5, 0.55, h32(row, cell, 77), wv=0.07, worn=0.25 + row * 0.08)
    # a crack from the arch down to the cards, and a chip off the right shoulder
    cd = poly_d(u, v, [(-2.8, 21.6), (-2.2, 19.4), (-2.9, 17.6), (-1.6, 15.0), (-2.0, 12.6)])
    hgt += groove(cd, 0.12, 0.3)
    return hgt, tag
LAIMIG_OUT = arched(LW, LH, rough=0.07, seed=1, chip=(4.6, 19.8, 0.9))
lai = Slab(rs, (at_x(222, 21.0), -0.6, 21.0), LW, LH, 2.2, LAIMIG_OUT, laimig_relief, lean=0.11, yaw=0.32, seed=1, v0=4.4,
           gilt=True, lichen=0.4, moss=0.45, gain=4.4)
heap(rs, lai.at(0, 0)[0], 20.2, 13.0, 2.0, 1)

# the king, tipped over at the foot of the stele -- the god who knew when to lose
KX, KZ, KL = -11.6, 18.8, 7.0
def king_r(t):
    """the piece's profile along its length: a wide base, a waist, a collar, the head, a small cross"""
    if t < 0.12: return 1.25 - (0.12 - t) * 1.5
    if t < 0.2: return 1.25 - (t - 0.12) / 0.08 * 0.35
    if t < 0.55: return 0.9 - math.sin((t - 0.2) / 0.35 * math.pi) * 0.25
    if t < 0.62: return 1.02
    if t < 0.86: return 0.85 * math.sqrt(max(0.0, 1 - ((t - 0.74) / 0.13) ** 2)) + 0.05
    if t < 1.0: return 0.18 if not (0.9 < t < 0.95) else 0.5
    return 0.0
def king(x, y, s, t, z, wp):
    rad = king_r(s)
    a = (t - 0.5) * 2 * 1.3
    if abs(a) > rad: return None
    X_, Y_, _ = wp
    n = -a / max(0.05, rad)                                                            # -1 = the top of the lying piece
    v = 4.4 - n * 1.8 - n * n * 1.4 + (n2(X_ * 2, Y_ * 2) - 0.5) * 1.0
    if s < 0.12 and abs(s - 0.06) < 0.01: v -= 1.0
    if abs(s - 0.2) < 0.012 or abs(s - 0.585) < 0.015: v -= 1.2
    c = tone(LIME, v + 0.6, x, y)
    if n < -0.55 and n1(X_ * 2.6 + 5, Y_ * 2.6) > 0.5: c = mix(c, tone(MOSSR, 3.0 - n, x, y), 0.7)
    elif n1(X_ * 2.4 + 70, Y_ * 2.4) > 0.75: c = mix(c, tone(LICHEN, 3.0 - n, x, y), 0.6)
    return fogged(c, z)
rs.quad((KX - KL / 2, -0.45, KZ), (KX + KL / 2, -0.45, KZ), (KX - KL / 2, 2.35, KZ), king, cls='prop', cut=True)
heap(rs, KX + 0.5, KZ - 0.4, 8.6, 0.55, 2)

# ---------------------------------------------------------------------------------------------------- Sisyla
SW, SH, SR = 10.0, 28.6, 3.0
def sisyla_relief(u, v):
    hgt = 0.0; tag = None
    d = gable_d(u, v, SW, SH, SR)
    hgt += band(d, 0.3, 0.9, 0.24)
    # the roundel of rays and the great closed eye
    eu, ev = u, v - 19.6
    rr = math.hypot(eu, ev)
    if rr < 4.0:
        hgt -= 0.18
        if rr > 3.55: hgt += 0.2 * math.sin((rr - 3.55) / 0.45 * math.pi)                # its raised rim
        ang = math.atan2(ev, eu)
        if 2.55 < rr < 3.4 and (ang * 16 / math.pi) % 1 < 0.42: hgt += 0.12                # rays
        if abs(eu) < 2.6:
            q = (eu / 2.55) ** 2
            crease = 0.2 + 1.15 * (1 - q)                                                   # the lid's crease, an arch
            slit = -0.1 - 0.55 * (1 - q)                                                    # the closed lid's edge, a U
            if slit < ev < crease: hgt += 0.16 + 0.12 * math.sin((ev - slit) / max(0.05, crease - slit) * math.pi)
            hgt += ridge(abs(ev - crease), 0.12, 0.16)
            hgt += groove(abs(ev - slit), 0.15, 0.7)
            for k in range(9):                                                              # lashes hanging from it
                lu = -2.1 + k * 0.525
                ls = -0.1 - 0.55 * (1 - (lu / 2.55) ** 2)
                hgt += groove(seg_d(eu, ev, (lu, ls - 0.08), (lu * 1.18, ls - 0.9)), 0.12, 0.55)
    # three moon phases under the roundel
    for k, mu in enumerate((-2.2, 0.0, 2.2)):
        md = math.hypot(u - mu, v - 13.8)
        if md < 0.62:
            sh_ = math.hypot(u - mu + (0.35 if k == 0 else -0.35 if k == 2 else 0.0), v - 13.8)
            if k == 1 or sh_ > 0.55: hgt += 0.14
            if md > 0.5: hgt -= 0.05
    # worn inscription band
    if 9.6 < v < 11.8 and abs(u) < 3.8:
        row = math.floor((v - 9.6) / 0.72); rv_ = (v - 9.6) % 0.72
        cell = math.floor((u + 3.8) / 0.48)
        if rv_ < 0.52: hgt += glyph((u + 3.8) % 0.48, rv_, 0.48, 0.52, h32(row, cell, 91), wv=0.065, worn=0.3)
    # the blind arcade: four round-headed niches that are no doors, little columns between them
    if 0.6 < v < 7.4 and abs(u) < 3.95:
        k = math.floor((u + 3.95) / 1.975); cu = -3.95 + (k + 0.5) * 1.975
        au = u - cu; aw = 0.72
        top = 6.0 + math.sqrt(max(0.0, aw * aw - au * au))
        if abs(au) < aw and v < top:
            hgt -= 0.42
            if v < 1.05: hgt += 0.2                                                             # the sill
            if abs(au) > aw - 0.1 or top - v < 0.1: hgt += 0.12
        elif abs(au) > 0.82: hgt += 0.12                                                     # the columns
    return hgt, tag
SIS_OUT = gabled(SW, SH, SR, rough=0.05, seed=2, chip=(-4.6, 4.0, 0.5))
sis = Slab(rs, (at_x(362, 26.0), -0.5, 26.0), SW, SH, 2.6, SIS_OUT, sisyla_relief, lean=-0.035, yaw=0.18, seed=2, v0=4.7,
           lichen=0.42, moss=0.4, gain=4.6)
# the crescent finial on the apex
apex = sis.at(0, SH - 0.1, 0.2)
def crescent(x, y, s, t, z, wp):
    u, v = (s - 0.5) * 2, (t - 0.5) * 2
    if math.hypot(u, v) > 1 or math.hypot(u, v - 0.55) < 0.78: return None
    X_, Y_, _ = wp
    c = tone(GRAVE, 4.6 - u * 1.4 + (0.8 if v < -0.5 else 0) + (n2(X_ * 3, Y_ * 3) - 0.5), x, y)
    if n1(X_ * 2, Y_ * 2) > 0.6: c = tone(LICHEN, 2.6, x, y)
    return fogged(c, z)
rs.quad((apex[0] - 1.3, apex[1] - 0.2, apex[2]), (apex[0] + 1.3, apex[1] - 0.2, apex[2]), (apex[0] - 1.3, apex[1] + 2.4, apex[2]), crescent, cls='wall', cut=True)
heap(rs, sis.at(0, 0)[0] + 0.5, 25.4, 13.5, 1.8, 3)

# ---------------------------------------------------------------------------------------------------- the Fallen God
HZ = 31.0
HW, HHt = 26.0, 30.0
def face_relief(u, v):
    fu, fv = u / (HW / 2), (v - HHt / 2) / (HHt / 2)
    r2 = fu * fu + fv * fv
    hgt = 3.7 * math.sqrt(max(0.0, 1 - r2))
    tag = None
    for sx in (-1, 1):
        ed = ((fu - sx * 0.98) / 0.1) ** 2 + ((fv + 0.02) / 0.2) ** 2                       # ears
        if ed < 1:
            hgt = max(hgt, 1.2 * math.sqrt(1 - ed))
            if ed < 0.45: hgt -= 0.5 * (1 - ed / 0.45)
        ex, ey = sx * 0.31, 0.04
        bd = math.hypot((fu - ex) / 0.24, (fv - ey - 0.03) / 0.22)                           # brows, raised high
        if abs(bd - 1.0) < 0.24: hgt += 0.65 * math.cos((bd - 1.0) / 0.24 * math.pi / 2) * smooth((fv - ey - 0.02) / 0.14)
        sd = math.hypot((fu - ex) / 0.22, (fv - ey) / 0.14)                                 # the socket
        if sd < 1: hgt -= 0.85 * (1 - sd * sd)
        du = (fu - ex) / 0.165
        if abs(du) < 1:                                                                     # the eye: an almond, wide open
            half = 0.075 * (1 - du * du) ** 0.8
            dv = fv - ey
            if abs(dv) < half:
                hgt += 0.7 * math.sqrt(1 - du * du) * math.sqrt(max(0.0, 1 - (dv / half) ** 2)) + 0.1; tag = 'eye'
                idd = math.hypot(fu - ex - sx * 0.008, dv + 0.006) / 0.052
                if abs(idd - 1) < 0.28: hgt -= 0.35; tag = None
                if idd < 0.45: tag = 'hole'
            ld = abs(dv - half - 0.014)
            if ld < 0.022: hgt += 0.4 * (1 - ld / 0.022)                                     # the upper lid
            ld = abs(dv + half + 0.012)
            if ld < 0.016: hgt += 0.22 * (1 - ld / 0.016)                                    # the lower lid
        hgt += groove(seg_d(fu, fv, (sx * 0.12, -0.24), (sx * 0.23, -0.52)), 0.028, 0.45)    # nasolabial folds
        cd = math.hypot((fu - sx * 0.42) / 0.3, (fv + 0.24) / 0.26)                          # cheeks
        if cd < 1: hgt += 0.4 * (1 - cd * cd)
    for wv_ in (0.42, 0.52):                                                                # forehead wrinkles of surprise
        if abs(fu) < 0.4: hgt += groove(abs(fv - wv_ - 0.05 * math.cos(fu * 5)), 0.02, 0.35) * (1 - (fu / 0.4) ** 2)
    # the diadem across the crown: a raised band, empty jewel sockets
    dd = fv - (0.74 - 0.08 * fu * fu)
    if abs(dd) < 0.07 and r2 < 0.97:
        hgt += 0.45 * math.cos(dd / 0.07 * math.pi / 2)
        for k in range(-3, 4):
            jd = math.hypot(fu - k * 0.17, dd)
            if jd < 0.04: hgt -= 0.7; tag = 'hole' if jd < 0.025 else tag
    # the nose
    if -0.32 < fv < 0.08:
        k = (0.08 - fv) / 0.4
        wdt = 0.045 + 0.07 * k
        if abs(fu) < wdt * 1.6: hgt += 1.0 * k ** 0.5 * math.cos(min(1.0, abs(fu) / (wdt * 1.6)) * math.pi / 2) * smooth((fv + 0.33) / 0.08)
    nd = math.hypot(fu / 0.1, (fv + 0.28) / 0.075)
    if nd < 1: hgt += 0.6 * (1 - nd * nd)
    for sx in (-1, 1):
        if math.hypot((fu - sx * 0.05) / 0.022, (fv + 0.34) / 0.014) < 1: tag = 'hole'; hgt -= 0.3
    # the mouth, open: lips round a dark hollow
    md = math.hypot(fu / 0.15, (fv + 0.56) / 0.07)
    if md < 1: tag = 'hole'; hgt -= 1.0
    elif md < 1.55: hgt += 0.5 * math.sin((md - 1) / 0.55 * math.pi) * (1.15 if fv < -0.56 else 1.0)
    # cracks across the face
    hgt += groove(poly_d(fu, fv, [(-0.62, 0.8), (-0.48, 0.52), (-0.55, 0.34), (-0.43, 0.08), (-0.5, -0.2), (-0.36, -0.46)]), 0.02, 0.8)
    hgt += groove(poly_d(fu, fv, [(0.95, -0.12), (0.72, -0.22), (0.6, -0.42), (0.33, -0.5)]), 0.018, 0.7)
    return hgt * 2.4, tag
def face_out(u, v):
    fu, fv = u / (HW / 2), (v - HHt / 2) / (HHt / 2)
    e = (n1(u * 1.4 + 3, v * 1.4) - 0.5) * 0.04
    if fu * fu + fv * fv < 1 + e: return True
    for sx in (-1, 1):
        if ((fu - sx * 0.98) / 0.1) ** 2 + ((fv + 0.02) / 0.2) ** 2 < 1: return True
    return False
head = Slab(rs, (0.0, -3.4, HZ), HW, HHt, 0.05, face_out, face_relief, tilt=0.6, lean=-0.26, seed=5, v0=4.2, gain=5.4,
            lichen=0.3, moss=0.55, ramp_=GRAVE, hgain=0.05, cls='prop')
# the broken halo: a ring of tarnished godmetal sunk into the ground behind the head, a piece broken out of it lies
# in the mud to the right
HR, HRW = 17.2, 1.5
def halo_out(u, v):
    du, dv = u, v - (HR + HRW)
    rr = math.hypot(du, dv); ang = math.degrees(math.atan2(dv, du))
    if abs(rr - HR) > HRW + (n1(ang * 0.3, 2.0) - 0.5) * 0.12: return False
    return not (28 < ang < 62)
def halo_rel(u, v):
    du, dv = u, v - (HR + HRW)
    rr = math.hypot(du, dv); ang = math.degrees(math.atan2(dv, du))
    q = (rr - HR) / HRW
    hgt = 0.9 * math.cos(q * math.pi / 2) - (0.2 if abs(q) < 0.08 else 0)
    if abs(q) < 0.55 and abs(ang % 15 - 7.5) < 0.5: hgt -= 0.25                            # engraved ticks
    return hgt, ('gilt' if abs(q) < 0.45 else 'eye' if q < -0.55 and abs(ang - 120) < 50 else None)
HCY = head.at(0, HHt / 2)[1]                                                            # concentric with the head
halo = Slab(rs, (-0.8, HCY - HR - HRW, HZ + 12.0), 2 * (HR + HRW), 2 * (HR + HRW), 1.6, halo_out, halo_rel, lean=-0.12, yaw=0.08,
            ramp_=BRONZE, lramp=VERDI, lichen=0.4, moss=0.1, v0=4.0, gain=5.5, seed=8, hgain=0.3, wear=0.7, gilt=True)
def halo_piece(x, y, s, t, z, wp):
    u, v = (s - 0.5) * 2, t
    arc_v = 0.25 + 0.5 * (1 - u * u)
    if abs(v - arc_v) > 0.2 or abs(u) > 0.95: return None
    X_, Y_, _ = wp
    val = 3.8 - (v - arc_v) * 7 + (n2(X_ * 1.5, Y_ * 1.5) - 0.5) * 1.2
    c = tone(BRONZE, val, x, y)
    if n1(X_ * 1.2 + 9, Y_ * 1.2) > 0.6: c = mix(c, tone(VERDI, 2.6, x, y), 0.6)
    return fogged(c, z)
rs.quad((15.5, -0.9, 35.0), (23.0, -0.9, 37.0), (15.5, 3.2, 35.0), halo_piece, cls='prop', cut=True)
heap(rs, 19.4, 34.2, 10.0, 1.3, 7)
heap(rs, 0.4, HZ - 1.4, 32.0, 2.2, 4)
heap(rs, -4.0, HZ - 3.6, 14.0, 1.3, 5)
heap(rs, 6.5, HZ - 4.0, 12.0, 1.1, 6)

# ---------------------------------------------------------------------------------------------------- Vhorn
VW, VH = 7.2, 22.0
def vhorn_relief(u, v):
    hgt = 0.0; tag = None
    d = arch_d(u, v, VW, VH)
    hgt += band(d, 0.25, 0.75, 0.22)
    vs = VH - VW / 2
    # the abacus in the arch: a frame, three rods, beads pushed to one side and the other
    au, av = u, v - vs + 0.4
    if abs(au) < 2.4 and abs(av) < 1.7:
        e = min(2.4 - abs(au), 1.7 - abs(av))
        hgt -= 0.2
        if e < 0.22: hgt += 0.32
        for k, rv in enumerate((-0.85, 0.0, 0.85)):
            if abs(av - rv) < 0.06: hgt += 0.05
            for j in range(5):
                bu = (-1.9 + j * 0.42) if (j < [3, 1, 4][k]) else (1.9 - (4 - j) * 0.42)
                bd = math.hypot((au - bu) / 0.2, (av - rv) / 0.26)
                if bd < 1: hgt += 0.26 * math.sqrt(1 - bd * bd)
    # the ledger: rows of tally marks in a sunk panel, the last row unfinished
    pu0, pu1, pv0, pv1 = -2.65, 2.65, 2.0, 15.4
    if pu0 < u < pu1 and pv0 < v < pv1:
        hgt -= 0.16
        e = min(u - pu0, pu1 - u, v - pv0, pv1 - v)
        if e < 0.12: hgt -= 0.06
        rowh = 0.96
        row = math.floor((pv1 - 0.2 - v) / rowh)
        rv_ = (pv1 - 0.2 - v) % rowh
        nrows = int((pv1 - pv0 - 0.4) / rowh)
        gw = 1.22
        g = math.floor((u - pu0 - 0.18) / gw)
        gu = (u - pu0 - 0.18) % gw
        last = row == nrows - 1
        if 0 <= row < nrows and 0.14 < rv_ < 0.8 and 0 <= g < 4:
            n_in = 5
            if last: n_in = max(0, 7 - g * 5) if g < 2 else 0                               # the unfinished row: 5, then 2, then nothing
            for k in range(min(4, n_in)):
                hgt += groove(abs(gu - 0.12 - k * 0.2), 0.07, 0.24)
            if n_in >= 5:
                hgt += groove(seg_d(gu, rv_, (0.0, 0.7), (0.86, 0.22)), 0.07, 0.24)
    # the crack that split the sums
    hgt += groove(poly_d(u, v, [(3.6, 13.2), (1.8, 11.6), (2.2, 9.8), (0.2, 8.4), (0.6, 6.2), (-1.4, 4.6), (-1.0, 2.6), (-2.4, 0.4)]), 0.13, 0.42)
    return hgt, tag
VH_OUT = arched(VW, VH, rough=0.06, seed=3, chip=(-3.2, 15.0, 0.6))
vho = Slab(rs, (at_x(686, 28.0), -0.5, 28.0), VW, VH, 1.9, VH_OUT, vhorn_relief, lean=-0.06, yaw=-0.24, seed=3, v0=4.5,
           lichen=0.36, moss=0.38, ramp_=LIME, gain=4.6)
heap(rs, vho.at(0, 0)[0], 27.3, 10.0, 1.6, 8)

# ---------------------------------------------------------------------------------------------------- Liln
IW, IH = 3.1, 3.9
def liln_relief(u, v):
    hgt = 0.0
    d = arch_d(u, v, IW, IH)
    hgt += band(d, 0.12, 0.32, 0.12)
    # two cupped hands holding a crust
    cd = math.hypot((u) / 0.42, (v - 2.25) / 0.3)
    if cd < 1: hgt += 0.2 * math.sqrt(1 - cd * cd)
    bowl = math.hypot(u / 0.95, (v - 2.3) / 0.75)
    if v < 2.25 and abs(bowl - 1) < 0.16: hgt += 0.14
    for k in range(4):
        fu_ = -0.75 + k * 0.5
        hgt += groove(seg_d(u, v, (fu_, 1.62 + 0.25 * abs(fu_)), (fu_ * 0.9, 1.75 + 0.25 * abs(fu_))), 0.035, 0.1)
    if 0.55 < v < 1.15 and abs(u) < 0.9:
        hgt += groove(abs((v - 0.55) % 0.3 - 0.15), 0.03, 0.12) if abs(u) < 0.9 - (v - 0.55) * 0.3 else 0
    return hgt, None
LILN_OUT = arched(IW, IH, rough=0.03, seed=4)
lil = Slab(rs, (at_x(764, 19.2), -0.25, 19.2), IW, IH, 0.7, LILN_OUT, liln_relief, lean=0.07, yaw=-0.35, seed=4, v0=5.6,
           ramp_=LIME, lichen=0.3, moss=0.3, gain=3.6)
heap(rs, lil.at(0, 0)[0], 18.9, 4.6, 0.6, 9)
def flowers(X, Z, seed):
    """a few wildflowers somebody left: stems, pale heads"""
    for i in range(9):
        a = (h01(seed, i) - 0.5) * 1.4
        tip = (X + a * 0.55, 0.6 + 0.45 * h01(seed, i, 2), Z + (h01(seed, i, 3) - 0.5) * 0.3)
        rs.line3((X + a * 0.1, 0.0, Z), tip, lambda x, y, s, t, z, wp: fogged(tone(LEAF, 1.6 + t, x, y), z), w=0.04)
        col = FLOWER[[3, 4, 2, 3, 4, 3, 1, 4, 3][i]]
        rs.disc(tip[0], tip[1], tip[2] - 0.02, 0.12, lambda x, y, a_, b_, z, wp, c=col: fogged(c if a_ + b_ < 0.5 else mix(c, (40, 30, 30), 0.3), z))
flowers(lil.at(-0.6, 0)[0] - 0.3, 18.6, 1)

# ---------------------------------------------------------------------------------------------------- Lietus Kika
DZ = 30.0; DX = at_x(818, DZ); DR = 4.5
def plinth_sh(v0):
    def sh(x, y, s, t, z, wp):
        X_, Y_, Z_ = wp
        v = v0 + (n2(X_ * 1.5 + Z_, Y_ * 1.5) - 0.5) * 1.2 + (0.9 if t > 0.92 else 0) - (0.8 if 0.45 < t < 0.5 else 0)
        c = tone(GRAVE, v, x, y)
        if n1(X_ * 2.4 + Z_, Y_ * 2.4) > 0.66: c = mix(c, tone(MOSSR, 2.6 + (v - v0) * 0.5, x, y), 0.7)
        return fogged(c, z)
    return sh
rs.box(DX - 3.3, DX + 3.3, -0.4, 2.6, DZ - 0.6, DZ + 2.6, plinth_sh(4.4), plinth_sh(5.4), top=plinth_sh(5.0), cls='wall')
def dial_relief(u, v):
    du, dv = u, v - DR
    rr = math.hypot(du, dv); ang = math.atan2(du, dv)                                     # 0 = up, clockwise
    worn = clamp((du + 1.0) / 3.0)                                                     # the right half is centuries older
    hgt = 0.0; tag = None
    if rr > DR - 0.55: hgt += 0.24 * math.sin((rr - DR + 0.55) / 0.55 * math.pi)
    if DR - 1.4 < rr < DR - 0.6:                                                         # thirteen hours, unevenly spaced
        for k in range(13):
            a = -math.pi + 2 * math.pi * (k + 0.5 * math.sin(k * 1.7) * 0.4) / 13
            if abs(math.sin((ang - a) / 2)) * rr < 0.11 + (0.08 if k % 3 == 0 else 0): hgt -= 0.24
    if abs(rr - (DR - 1.55)) < 0.06: hgt -= 0.12
    for (a, L, wd) in ((-0.95, 2.1, 0.22), (2.2, 3.0, 0.14), (3.6, 2.6, 0.1)):              # three hands
        tip = (math.sin(a) * L, math.cos(a) * L)
        sd = seg_d(du, dv, (0.0, 0.0), tip)
        if sd < wd: hgt += 0.22 * math.cos(sd / wd * math.pi / 2)
        td = math.hypot(du - tip[0], dv - tip[1])
        if td < wd * 2.2: hgt += 0.12 * (1 - td / (wd * 2.2))
    if rr < 0.5: hgt += 0.3 * math.sqrt(1 - (rr / 0.5) ** 2)
    sd_ = math.hypot(du, dv - 1.6)                                                       # a little sun and a moon
    if sd_ < 0.42: hgt += 0.12
    md_ = math.hypot(du, dv + 1.7)
    if md_ < 0.42 and math.hypot(du + 0.2, dv + 1.6) > 0.32: hgt += 0.12
    return hgt * (1 - 0.65 * worn), tag
DIAL_OUT = lambda u, v: math.hypot(u, v - DR) < DR + (n1(u * 2 + 5, v * 2) - 0.5) * 0.15 * (1 + 2 * clamp((u + 1) / 3))
dia = Slab(rs, (DX, 2.4, DZ + 0.6), 2 * DR, 2 * DR, 1.3, DIAL_OUT, dial_relief, lean=0.09, yaw=-0.4, seed=6, v0=5.3,
           ramp_=LIME, lichen=0.45, moss=0.3, wear=1.3, gain=3.8,
           dark=lambda u, v: 0.6 * clamp((u + 1) / 3) * n2(u * 1.2 + 9, v * 1.2))
heap(rs, DX + 0.2, DZ - 1.0, 9.5, 1.3, 10)

# ---------------------------------------------------------------------------------------------------- Hvetrdjaana
TW, TH = 9.0, 13.4
def hvet_relief(u, v):
    hgt = 0.0; tag = None
    d = arch_d(u, v, TW, TH)
    hgt += band(d, 0.3, 0.9, 0.12)
    vs = TH - TW / 2
    # the niche with the veiled figure that has no face
    nu, nv = u, v - (vs - 1.4)
    nr = 2.4
    inside = (abs(nu) < nr and nv < 2.6) and (nv < 0 or math.hypot(nu, nv) < nr) and nv > -3.0
    inside = (abs(nu) < nr and -2.9 < nv < 0) or (nv >= 0 and math.hypot(nu, nv) < nr)
    if inside:
        hgt -= 0.42
        fd = math.hypot(nu / 0.58, (nv - 0.75) / 0.8)                                      # the veiled head: smooth, no face
        if fd < 1: hgt += 0.6 * math.sqrt(1 - fd * fd)
        else:
            sw = 0.5 + (0.6 - nv) * 0.42 if nv < 0.6 else 0                                  # the veil falls over the shoulders
            if abs(nu) < sw and -2.9 < nv < 0.6:
                fold = 0.08 * math.sin(nu * 9 + nv * 0.6) * clamp((0.6 - nv) / 1.5)
                hgt += 0.34 + fold - 0.12 * (abs(nu) / sw) ** 2
                if abs(nu) < 0.45 and -1.6 < nv < -0.9: hgt += 0.1                         # hands folded under the veil
    # rows of the script nobody can read, worn away more toward the bottom-left
    if 0.9 < v < vs - 4.6 and abs(u) < TW / 2 - 1.0:
        rowh = 0.82
        row = math.floor((v - 0.9) / rowh); rv_ = (v - 0.9) % rowh
        wob = 0.08 * math.sin(u * 0.9 + row)
        cw = 0.56
        cell = math.floor((u + TW / 2 - 1.0) / cw)
        if rv_ + wob < 0.6:
            worn = 0.25 + 0.4 * clamp((2.0 - u) / 6.0) + 0.1 * (6 - row) / 6
            g_ = glyph((u + TW / 2 - 1.0) % cw, rv_ + wob, cw, 0.6, h32(row, cell, 131), wv=0.07, worn=worn, style='knot')
            if g_ < 0: tag = 'gilt'
            hgt += g_
    return hgt, tag
HV_OUT = arched(TW, TH, rough=0.14, seed=7, chip=(-4.3, 10.2, 1.2))
hve = Slab(rs, (at_x(985, 20.6), -0.7, 20.6), TW, TH, 1.3, HV_OUT, hvet_relief, lean=-0.12, yaw=-0.5, tilt=0.06, seed=7, v0=4.3,
           lichen=0.4, moss=0.45, wear=1.5, gilt=True, gain=4.2)
heap(rs, hve.at(0, 0)[0] - 0.4, 19.9, 12.5, 2.0, 11)

# ---------------------------------------------------------------------------------------------------- the ossuary niche (Osswine's)
OX, OZ = at_x(78, 17.6), 17.6
OXW, OYH = 6.0, 7.2
def ossuary_front(x, y, s, t, z, wp):
    X_, Y_, Z_ = wp
    u, v = X_ - OX, Y_
    nu, nv = u, v - 4.6
    opening = (abs(nu) < 1.75 and 1.1 < v < 4.6) or (v >= 4.6 and math.hypot(nu, nv) < 1.75)
    px = z / F
    if opening:
        # stacked skulls in the dark, front ones catching the light: each its own size, tilt and wear; long bones
        # laid between the rows; here and there a gap
        deep = clamp((v - 1.1) / 5.0)
        rowh = 0.74
        row = math.floor((v - 1.1) / rowh); rv = (v - 1.1) % rowh
        if 0.5 < rv < 0.62 and h01(row, 31) < 0.6:                                           # a long bone in the joint
            return fogged(tone(BONEK, 3.0 - deep * 1.6 + (0.6 if rv < 0.55 else -0.4), x, y), z)
        off = (row % 2) * 0.41 + (h01(row, 5) - 0.5) * 0.2
        k = math.floor((nu + 1.75 + off) / 0.82); su = (nu + 1.75 + off) % 0.82 - 0.41
        rs_ = 0.28 + 0.08 * h01(k, row, 7); turn = (h01(k, row, 8) - 0.5) * 0.18
        su -= turn; sv = rv - 0.32 - (h01(k, row, 9) - 0.5) * 0.08
        sk = (su / rs_) ** 2 + (sv / (rs_ * 1.08)) ** 2
        gap = h01(k, row, 11) < 0.12
        if sk < 1 and not gap and row < 6:
            lit = 3.6 - su / rs_ * 1.4 + sv / rs_ * 1.2 - deep * 1.8 - sk * 0.8
            es = rs_ * 0.38
            for ex_ in (-0.36 * rs_ + turn * 0.5, 0.36 * rs_ + turn * 0.5):
                if math.hypot((su - ex_) / es, (sv + 0.02) / (es * 1.05)) < 1: return fogged(tone(BONEK, 0.3 + (0.3 if su > ex_ else 0), x, y), z)
            if abs(su - turn * 0.5) < rs_ * 0.1 and -0.5 * rs_ < sv < -0.25 * rs_: return fogged(tone(BONEK, 0.6, x, y), z)
            if sv < -0.62 * rs_ and int((su / rs_ + 1) * 7) % 2 == 0: return fogged(tone(BONEK, max(0.6, lit - 2.4), x, y), z)
            if h32(int(X_ * 20 + 999), int(Y_ * 20 + 999), 3) % 9 == 0: lit -= 1.0                   # pits, cracks
            return fogged(tone(BONEK, lit + (n2(X_ * 6, Y_ * 6) - 0.5) * 1.0, x, y), z)
        return fogged(tone(GRAVE, 0.4 + (1 - deep) * 0.5, x, y), z)
    # the reveal round the opening
    if (abs(nu) < 2.1 and 0.8 < v < 4.6 and abs(nu) > 1.75) or (v >= 4.6 and 1.75 <= math.hypot(nu, nv) < 2.1):
        return fogged(tone(GRAVE, 5.6 if nu > 0 else 3.0, x, y), z)
    if 0.8 < v < 1.1 and abs(nu) < 1.75: return fogged(tone(GRAVE, 6.0, x, y), z)                                           # the sill
    # rough coursed stone: big uneven blocks, deep joints, lit upper arrises
    bh = 0.9
    row = math.floor(v / bh); off = (row % 2) * 0.6 + h01(row, 3) * 0.5
    bwid = 1.2 + 0.5 * h01(row, math.floor((u + off) / 1.5), 4)
    fu, fv = ((u + off) / 1.5) % 1, (v / bh) % 1
    jit = (n3(X_ * 6, Y_ * 6) - 0.5) * 0.06
    if fu * 1.5 < px * 1.3 + jit or fv * bh < px * 1.3 + jit: return fogged(tone(MUD, 1.2, x, y), z)
    val = 4.4 + (h32(math.floor((u + off) / 1.5), row, 17) % 5 - 2) * 0.4 + (n2(X_ * 2, Y_ * 2) - 0.5) * 1.2 + (0.9 if fv * bh > bh - px * 2.2 else 0) - (0.6 if fv * bh < px * 2.6 else 0)
    c = tone(GRAVE, val, x, y)
    if Y_ < 1.0 + n1(X_ * 2, 3.0) and n1(X_ * 2.4 + 40, Y_ * 2.4) > 0.5: c = mix(c, tone(MOSSR, 2.4 + (val - 4.4) * 0.5, x, y), 0.8)
    elif n1(X_ * 2.6 + 80, Y_ * 2.6) > 0.76: c = mix(c, tone(LICHEN, 2.4, x, y), 0.6)
    run = n3(X_ * 3.0 + 7, 2.0)
    if run > 0.64: c = mix(c, (14, 16, 14), min(0.4, (run - 0.64) * 2.0))
    return fogged(c, z)
BONEK = ramp('#1f1d17 #34302a #4c473c #655f50 #7e7766 #988f7a #ada48c')
def oss_side(x, y, s, t, z, wp):
    X_, Y_, Z_ = wp
    v = 5.0 + (n2(Z_ * 1.8, Y_ * 1.8) - 0.5) * 1.2 + (n3(Z_ * 5, Y_ * 5) - 0.5) * 0.6 - 0.8 * max(0.0, 1 - Y_ / 1.5)
    if (Y_ / 0.9) % 1 < 0.05: v -= 1.4
    return fogged(tone(GRAVE, v, x, y), z)
rs.box(OX - OXW / 2, OX + OXW / 2, -0.4, OYH, OZ, OZ + 3.2, ossuary_front, oss_side, cls='wall')
def oss_roof(x, y, s, t, z, wp):
    u = (s - 0.5) * 2
    if t > 1 - abs(u) + 0.02: return None
    X_, Y_, _ = wp
    c = tone(GRAVE, 4.6 - u * 0.8 + (n2(X_ * 2, Y_ * 2) - 0.5) * 1.2 + (1.0 if t > 0.92 - abs(u) else 0), x, y)
    if t > 0.75 - abs(u) and n1(X_ * 2.5 + 5, Y_ * 2.5) > 0.45: c = mix(c, tone(MOSSR, 3.0 - u * 0.4, x, y), 0.8)
    return fogged(c, z)
rs.quad((OX - OXW / 2 - 0.5, OYH, OZ - 0.3), (OX + OXW / 2 + 0.5, OYH, OZ - 0.3), (OX - OXW / 2 - 0.5, OYH + 2.4, OZ - 0.3), oss_roof, cls='wall', cut=True)
rs.box(OX - OXW / 2 - 0.4, OX + OXW / 2 + 0.4, OYH - 0.35, OYH, OZ - 0.35, OZ + 3.4, plinth_sh(5.4), oss_side, bottom=plinth_sh(2.2), cls='wall')
heap(rs, OX + 0.4, OZ - 0.4, 8.0, 0.9, 12)

# ---------------------------------------------------------------------------------------------------- mid-ground stones between the graves
def mid_stone(X, Z, w, h, seed, lean=0.0, kind='arched'):
    out = arched(w, h, rough=0.08, seed=seed) if kind == 'arched' else gabled(w, h, w * 0.35, rough=0.06, seed=seed)
    def rel(u, v):
        d = arch_d(u, v, w, h) if kind == 'arched' else gable_d(u, v, w, h, w * 0.35)
        hh = band(d, 0.2, 0.6, 0.18)
        if abs(u) < w * 0.3 and h * 0.3 < v < h * 0.7 and (v * 2.6) % 1 < 0.3 and h01(seed, int(v * 2.6)) < 0.7: hh -= 0.12
        return hh, None
    Slab(rs, (X, -0.5, Z), w, h, w * 0.18, out, rel, lean=lean, yaw=-0.2 if X > 0 else 0.2, seed=seed, v0=4.4, lichen=0.4, moss=0.4)
    heap(rs, X, Z - 0.6, w * 1.4, 1.0, 50 + seed)
for (x, Z, w, h, seed, lean, kind) in ((585, 52, 4.0, 8.0, 21, 0.05, 'arched'), (735, 46, 4.6, 10.0, 22, -0.08, 'gable'),
                                       (782, 62, 3.6, 7.0, 23, 0.1, 'arched'), (1010, 44, 5.0, 12.0, 24, 0.06, 'arched'),
                                       (650, 70, 3.2, 6.0, 25, -0.05, 'gable'), (900, 58, 4.0, 9.0, 26, -0.1, 'arched'),
                                       (20, 46, 5.0, 11.0, 27, 0.08, 'gable'), (128, 60, 4.2, 9.0, 28, -0.06, 'arched'),
                                       (460, 66, 3.6, 7.0, 29, 0.0, 'arched')):
    mid_stone(at_x(x, Z), Z, w, h, seed, lean, kind)

# ---------------------------------------------------------------------------------------------------- ledger stones lying in the grass
def ledger(X, Z, w, l, ang, seed, sink=0.0):
    """a flat grave slab lying in the turf, a little askew, its edges grown over, a worn panel cut in it"""
    ca, sa = math.cos(ang), math.sin(ang)
    P0 = (X - ca * w / 2 + sa * l / 2, 0.06 - sink, Z - sa * w / 2 - ca * l / 2)
    P1 = (P0[0] + ca * w, 0.06 - sink, P0[2] + sa * w)
    P3 = (P0[0] - sa * l, 0.06 - sink + 0.0, P0[2] + ca * l)
    def sh(x, y, s, t, z, wp):
        X_, _, Z_ = wp
        e = min(s, 1 - s, t, 1 - t)
        if e < 0.04 + 0.05 * n1(X_ * 3 + seed, Z_ * 3): return None                          # turf over the edges
        v = 4.2 + (n2(X_ * 1.8 + seed, Z_ * 1.8) - 0.5) * 1.4 + (n3(X_ * 6, Z_ * 6) - 0.5) * 0.6
        if 0.18 < s < 0.82 and 0.15 < t < 0.85 and (min(s - 0.18, 0.82 - s, t - 0.15, 0.85 - t) < 0.025): v -= 1.4   # the panel
        if 0.25 < s < 0.75 and 0.3 < t < 0.7 and h32(int(s * 14), int(t * 9), seed) % 3 == 0 and (s * 14) % 1 < 0.4: v -= 1.0
        c = tone(GRAVE, v, x, y)
        if n1(X_ * 1.6 + seed * 3, Z_ * 1.6) > 0.6 or e < 0.1: c = mix(c, tone(MOSSR, 2.6 + (v - 4.2) * 0.6, x, y), 0.75)
        elif n2(X_ * 2.4 + seed, Z_ * 2.4) > 0.72: c = mix(c, tone(LICHEN, 2.6, x, y), 0.55)
        return fogged(c, z)
    rs.quad(P0, P1, P3, sh, cls='ground', cut=True)
ledger(-4.6, 13.6, 2.4, 3.6, 0.22, 1)
ledger(4.8, 21.5, 2.2, 3.2, -0.3, 2, sink=0.02)
ledger(-15.0, 24.0, 2.6, 3.8, 0.1, 3)
ledger(13.0, 14.6, 2.0, 3.0, -0.12, 4)
# a votive at Laimig's foot: a glass jar with a candle still burning -- someone keeps leaving offerings here
VX, VZ = lai.at(2.6, 0)[0], 19.3
def votive(x, y, s, t, z, wp):
    """a jar of smoky glass, the flame bright in its middle, a dark rim"""
    if t > 0.86: return tone(IRON, 2.0, x, y)
    if 0.36 < s < 0.64 and 0.38 < t < 0.78: return ri(GLOW, 3.6 if 0.44 < s < 0.56 and t > 0.5 else 2.4)
    return mix(ri(GLOW, 0.6 + (0.6 if 0.25 < s < 0.75 else 0)), (40, 34, 24), 0.35 if t < 0.25 else 0.15)
rs.box(VX - 0.2, VX + 0.2, 0.0, 0.66, VZ, VZ + 0.4, votive, lambda x, y, s, t, z, wp: mix(ri(GLOW, 0.4), (36, 30, 22), 0.4), cls='emit')

# ---------------------------------------------------------------------------------------------------- weeds
for k in range(70):
    Z = 9.0 + (h32(k, 1) % 260) / 10.0
    X = at_x(10 + h32(k, 2) % 1047, Z)
    if abs(X - path_x(Z)) < 2.4 or puddle(X, Z) > 0: continue
    heather = k % 3 == 0
    tuft(rs, X, Z, 300 + k, h=0.6 + (h32(k, 3) % 10) / 10.0, n=10 if heather else 12, ramp_=HEATH if heather else STRAW,
         spread=0.5, v0=2.6 if heather else 2.0, w=0.03)
for k in range(18):                                                                   # taller dead grass in the near corners
    side = -1 if k % 2 else 1
    Z = 8.6 + (h32(k, 6) % 40) / 10.0
    X = side * (11.0 + (h32(k, 5) % 90) / 10.0)
    if puddle(X, Z) > 0: continue
    tuft(rs, X, Z, 400 + k, h=1.5 + (h32(k, 7) % 12) / 10.0, n=16, ramp_=STRAW if k % 4 else HEATH, spread=0.9, v0=1.8, w=0.025)
for k in range(12):                                                                   # stone rubble
    Z = 12 + (h32(k, 11) % 200) / 10.0; X = at_x(30 + h32(k, 12) % 1000, Z)
    if abs(X - path_x(Z)) < 2.2 or puddle(X, Z) > 0: continue
    r = 0.18 + (h32(k, 13) % 10) / 30.0
    rs.disc(X, r * 0.5, Z, r, lambda x, y, a, b, z, wp: fogged(tone(GRAVE, 5.0 - a * 1.4 - b * 1.8, x, y), z) if b < 0.45 else None)

# ---------------------------------------------------------------------------------------------------- render (twice: without and with Osswine)
RENDER = dict(fog=fog_of, light_gain=1.0, grime_gain=0.9, bloom=0.3,
              stain_gain=0.8, damp_gain=1.0)
MIST = dict(top=3.6, dens=0.026, banks=0.7, far=0.6, horizon=0.85,
            wisps=((-40, -12, 2.8, 30.0, 1.5), (8, 40, 3.0, 40.0, 1.8), (-20, 10, 4.2, 55.0, 2.2), (14, 60, 2.2, 24.0, 1.1)),
            glow=(560, 300, 420, (150, 162, 150), 0.5))
img = rs.render(INK, **RENDER)
ground_mist(img, rs, **MIST)
img.save(f'{OUT}/gyard.png')
write_gpl(f'{OUT}/gyard.gpl')
print('done gyard')

def poly(slab, out, n=40):
    return [(round(p[0]), round(p[1])) for p in slab.outline_px(out, n)]
HITS['laimig'] = poly(lai, LAIMIG_OUT)
HITS['sisyla'] = poly(sis, SIS_OUT)
HITS['vhorn'] = poly(vho, VH_OUT)
HITS['liln'] = poly(lil, LILN_OUT, 24)
HITS['lietus'] = poly(dia, DIAL_OUT)
HITS['hvetrdjaana'] = poly(hve, HV_OUT)
HITS['face'] = poly(head, face_out)
c0 = proj(OX - OXW / 2 - 0.5, -0.4, OZ); c1 = proj(OX + OXW / 2 + 0.5, OYH + 2.4, OZ)
HITS['niche'] = [(round(c0[0]), round(c1[1])), (round(c1[0]), round(c1[1])), (round(c1[0]), round(c0[1])), (round(c0[0]), round(c0[1]))]
HITS['niche_opening'] = [round(v) for v in proj(OX, 3.0, OZ)]
HITS['phor_spot'] = [round(v) for v in proj(path_x(16.5) + 4.0, 0.0, 16.5)]
json.dump(HITS, open(f'{OUT}/gyard.json', 'w'), indent=1)
print(json.dumps({k: (min(p[0] for p in v), min(p[1] for p in v), max(p[0] for p in v), max(p[1] for p in v)) if isinstance(v[0], tuple) else v for k, v in HITS.items()}))

# ---------------------------------------------------------------------------------------------------- Osswine: pale dry filaments on the skulls
def osswine(rs):
    """something pale and dry unfurled over the stacked skulls -- not a plant, not quite: brittle bone-white threads
    that branch and curl out of the niche, a few seed-like knots on them"""
    BW = ramp('#4c4a40 #5f5c50 #737060 #878372 #9a9683 #aca894')
    def thread(P, ang, L, w, d, k):
        if d == 0 or w < 0.012: return
        n = 4
        for i in range(n):
            ang += (h01(k, i, 3) - 0.5) * 0.7
            Q = (P[0] + math.sin(ang) * L / n, P[1] + math.cos(ang) * L / n, P[2] - 0.02)
            col = BW[min(5, 2 + d // 2 + (1 if h01(k, i) > 0.5 else 0))]
            rs.line3(P, Q, lambda x, y, s, t, z, wp, c=col: fogged(c, z), w=w, cls='prop')
            P = Q
            if i == 1 and d > 1: thread(P, ang + (0.8 if k % 2 else -0.8), L * 0.6, w * 0.7, d - 1, k * 3 + 1)
        if h01(k, 7) < 0.5: rs.disc(P[0], P[1], P[2] - 0.03, 0.055, lambda x, y, a, b, z, wp: fogged(BW[5] if a + b < 0 else BW[3], z), cls='prop')
        thread(P, ang + (h01(k, 8) - 0.5), L * 0.55, w * 0.65, d - 1, k * 3 + 2)
    Zf = OZ - 0.12
    for j, (sx, sy, ang) in enumerate(((-0.9, 2.4, -0.5), (-0.3, 3.3, -0.15), (0.4, 2.9, 0.35), (1.0, 2.0, 0.8), (0.1, 4.4, 0.1), (-1.1, 4.0, -0.8), (1.1, 3.8, 0.6), (-0.5, 1.6, -1.2), (0.7, 1.4, 1.1))):
        thread((OX + sx, sy, Zf), ang, 0.9 + h01(j, 1) * 0.6, 0.05, 3, 10 + j)
n0 = rs.n
osswine(rs)
img2 = rs.render(INK, **RENDER)
ground_mist(img2, rs, **MIST)
BOX = tuple(int(v) for v in (proj(OX - 4.5, 7.6, OZ)[0], proj(OX, 7.6, OZ)[1], proj(OX + 4.5, 0.0, OZ)[0], proj(OX, 0.0, OZ)[1]))
spr = Image.new('RGBA', (BOX[2] - BOX[0], BOX[3] - BOX[1]), (0, 0, 0, 0))
p0, p1, ps = img.load(), img2.load(), spr.load()
mine = lambda x, y: rs.G[y][x] is not None and rs.G[y][x][1] > n0
for y in range(max(0, BOX[1]), min(H, BOX[3])):
    for x in range(max(0, BOX[0]), min(W, BOX[2])):
        edge = any(0 <= x + dx < W and 0 <= y + dy < H and mine(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if mine(x, y) or (edge and max(abs(p0[x, y][i] - p1[x, y][i]) for i in range(3)) > 6):
            ps[x - BOX[0], y - BOX[1]] = p1[x, y] + (255,)
bb = spr.getbbox()
spr.crop(bb).save(f'{OUT}/osswine.png')
print('done osswine: place its top-left at', (BOX[0] + bb[0], BOX[1] + bb[1]), 'size', (bb[2] - bb[0], bb[3] - bb[1]))
