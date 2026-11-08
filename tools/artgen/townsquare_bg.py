"""The Town Square of Upper Morkezela (TownSquareScene), 1067x600, overcast day, the shared camera (raster3d.py).
After the old art (TownSquare.png): an old-town square of tall stucco tenements narrowing step by step into the street
that runs off to the harbour (the "up" exit), the hazy spires at its end, the skyship Verdigrace drifting over the roofs.
The middle of the square is an oval island of fan-laid cobbles inside a granite kerb; the road of setts curves round it
and runs out towards the viewer (the "down" exit, the way to the Godgraveyard). The right row stands on an arcade
(podloubi: arches on piers, lit shopfronts in the walk behind -- the way on to the Townhall, exit right); on the left
shopfronts with arched doors, a side street whose corner is already overgrown by the Lumen Directorate's living walls
(exit left), closed market stalls under canvas on the right, an old drinking fountain left of the street's mouth.
Weathering is drawn in surface coordinates (stains, patched plaster, soot under the cornices, rain-wash under every sill);
paintpass adds the rest (plaster peeling to brick on the lower floors, cracks, AO, light spill). No free-standing lamp posts: the square's only lamp post is
Chandelier (a Gang-of-Lamps sprite the scene places on the island's left side); the painted lamps are wall lanterns on
iron brackets and one lamp hung on a wire over the street.

    python3 townsquare_bg.py <outdir>   ->  townsquare.png (= assets/images/backgrounds/TownSquare.png)
Fixed points (canvas): the far street (Harbor exit) x ~470..600, y ~230..330; the island's left side round (175, 468)
is kept clear for Chandelier; the walk line y 534 runs across the island; the arcade x ~820..1067 (Townhall side);
the side street on the left x ~136..196 (Lumen side); the skyship ~ x 300..560, y 60..170 (the observable)."""
import sys, math
from PIL import Image
from common import h32
from shedkit import *
from rig import Rig, Mat

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = Raster()
ramp_ = ramp
OCHRE_P = ramp_('#2a2417 #3c3421 #50462c #645838 #776a45 #8a7c54 #9d8f65')
SAGE_P = ramp_('#1d241f #29332b #364237 #435244 #526252 #627360 #73846f')
ROSE_P = ramp_('#291e1d #392a27 #4b3833 #5d4740 #6f574e #82685d #94796c')
CREAM_P = ramp_('#2b2a23 #3e3c31 #535041 #686551 #7d7a63 #918e75 #a4a287')
GREY_P = ramp_('#1b201f #262d2b #323a37 #3f4844 #4d5752 #5c6761 #6c7871')
SLATE_R = ramp_('#121619 #1a2024 #232b30 #2d363c #384249 #444f56')
TILE_R = ramp_('#1e1411 #2c1c16 #3c261d #4d3125 #5d3d2e')
IVY = ramp_('#101a10 #172617 #20341f #2b4428 #375532 #44663c')
BRICK = ([(96, 64, 52), (110, 74, 58), (122, 86, 66), (88, 64, 54)], (84, 80, 72))
SHUTC = [ramp_('#121d16 #1a2a1f #243a2a #2f4a36'), ramp_('#22170f #322217 #452f20 #583d2a'), ramp_('#1b1f25 #262c34 #333b45 #414a56')]

KEYOBJ = {}                                                          # obj id -> paintpass material key ('stucco' peels to brick)
def wall_key(obj, part_fn, along_z): KEYOBJ[obj] = (part_fn, along_z)

# ---------------------------------------------------------------------------------------------------- sky
from shedkit import _scr, _scr2
def sky_day(x, y, s=0, t=0, z=0, wp=None):
    """the overcast day over the square: a pale, hazy cloud deck (lighter than the shed's), long soft bands"""
    tt = max(0.0, min(1.0, y / HY))
    v = 3.7 + 3.1 * tt ** 1.2 + (_scr2(x * 0.55, y * 2.6) - 0.5) * 1.5 + (_scr(x * 0.5, y * 2.4) - 0.5) * 0.5
    return tone(SKY, v, x, y)
rs.quad((-1600, 900, 650), (1600, 900, 650), (-1600, -300, 650), sky_day, cls='sky')

# ---------------------------------------------------------------------------------------------------- the ground
OX, OZ, ORX, ORZ = 2.0, 25.0, 28.0, 13.5                             # the cobbled island (an oval) in the middle
ROAD = 8.5                                                           # the road's width round it
def oval(X, Z):
    """(normalised radius, radial distance in units outside the kerb, angle)"""
    dx, dz = (X - OX) / ORX, (Z - OZ) / ORZ
    q = math.hypot(dx, dz) or 1e-6
    r = math.hypot(X - OX, Z - OZ)
    return q, r * (1 - 1 / q), math.atan2(dz, dx)
def street_half(Z):
    """the far street's half width (the setts) -- the square funnels into it"""
    return 11.0
def puddle(X, Z):
    """rain water standing in the low spots: along the gutter round the island and in the worn ruts of the road --
    crisp-edged, so they read as water (they mirror the sky and the houses), never as stains"""
    if Z > 80: return 0.0
    q, d, _ = oval(X, Z)
    if -0.35 < d < 0.15: return 0.0                                  # the kerb stays dry
    m = wn(2, X * 0.23 + 11.0, Z * 0.36) + (wn(3, X * 1.6, Z * 1.6) - 0.5) * 0.12
    if 0.15 < d < 2.4: m += 0.13                                     # water gathers in the gutter and the ruts
    elif d < 0: return 0.0                                           # the island is crowned: it drains
    return 1.0 if m > 0.74 else 0.0
def ground_kind(X, Z):
    q, d, a = oval(X, Z)
    if d < -0.35: return 'island', q, d, a
    if d < 0.1: return 'kerb', q, d, a
    if d < 0.8: return 'gutter', q, d, a
    if d < ROAD: return 'road', q, d, a
    if Z > 46 and abs(X) < street_half(Z): return 'street', q, d, a
    if d < ROAD + 0.5: return 'kerb2', q, d, a
    return 'pave', q, d, a
def fan(X, Z, x, y, z):
    """fan-laid small cobbles (Bogenpflaster): rows of fish-scale arcs, the stones laid along each arc"""
    A = 6.0; rad = A * 0.66
    j0 = math.floor(Z / (A * 0.5))
    best = None
    for j in (j0 + 1, j0, j0 - 1, j0 - 2):
        cz = j * A * 0.5
        off = (j % 2) * A * 0.5
        i = round((X - off) / A)
        for ii in (i - 1, i, i + 1):
            cx = ii * A + off
            dd = math.hypot(X - cx, (Z - cz) * 1.0)
            if dd < rad and Z >= cz:
                best = (ii, j, dd, math.atan2(Z - cz, X - cx)); break
        if best: break
    if not best: return tone(STONE, 4.0, x, y)
    ii, j, dd, ang = best
    S = 0.44
    ring = math.floor(dd / S); fr = (dd / S) % 1
    seg = ang * dd / S + ring * 0.37
    fs = seg % 1
    ex = 1.1 * z / F / S
    v = 4.6 + (h32(ii, j, ring, int(math.floor(seg))) % 4) * 0.3 - (0.5 if h32(ii, j, ring, int(math.floor(seg)), 3) % 7 == 0 else 0)
    if z < 46 and (fr < ex + 0.05 or fs < ex + 0.06): v = 2.5
    if rad - dd < S * 0.6 + ex * S: v = 3.0 + (0.6 if h32(ii, j, int(ang * 9)) % 2 else 0)        # the edge stones of each arc
    v += 0.5 * (wn(1, X * 2, Z * 2) - 0.5)
    return tone(STONE, v, x, y)
def setts_ring(X, Z, d, a, x, y, z):
    """setts laid in rows along the road, round the island"""
    row = math.floor(d / 0.85)
    L = a * (ORX + ORZ) * 0.5 + d * 0.0
    col = math.floor(L / 1.05 + (row % 2) * 0.5)
    fr = (d / 0.85) % 1; fc = (L / 1.05 + (row % 2) * 0.5) % 1
    v = 4.1 + (h32(col, row, 7) % 4) * 0.3 - (0.7 if h32(col, row, 8) % 6 == 0 else 0)
    ex = 1.05 * z / F / 0.85
    if z < 60 and (fr < ex + 0.04 or fc < ex * 0.9 + 0.04): v = 2.3
    v += 0.5 * (wn(1, X * 2, Z * 2) - 0.5)
    return tone(STONE, v, x, y)
def flag(X, Z, x, y, z, v0=4.8):
    """big worn flagstones by the houses"""
    row = math.floor(Z / 1.6); colw = 2.4 + (h32(row, 3) % 3) * 0.3
    col = math.floor(X / colw + row * 0.37)
    fx = (X / colw + row * 0.37) - col; fz = Z / 1.6 - row
    v = v0 + (h32(col, row, 4) % 3) * 0.35 - (0.6 if h32(col, row, 5) % 6 == 0 else 0) + (wn(0, X * 1.5, Z * 1.5) - 0.5) * 0.7
    if z < 70 and (fx < 0.9 * z / F / colw + 0.02 or fz < 1.1 * z * z / (F * CAMH) / 1.6 + 0.02): v = 2.6
    return tone(STONE, v, x, y)
def ground(x, y, s, t, z, wp):
    X, _, Z = wp
    k, q, d, a = ground_kind(X, Z)
    if k == 'island':
        c = fan(X, Z, x, y, z)
        c = mix(c, (118, 126, 108), 0.13 * max(0.0, 1 - q * q))                 # the crowned middle catches the light
    elif k == 'kerb':
        seg = math.floor(a * 40)
        c = tone(STONE, 4.5 + (h32(seg, 5) % 3) * 0.3 - (1.2 if (a * 40) % 1 < max(0.04, z / 400) else 0) - (1.0 if d > -0.05 else 0) + (wn(1, X * 2, Z * 2) - 0.5) * 0.8, x, y)
    elif k == 'gutter': c = tone(STONE, 2.6 + (wn(1, X * 3, Z * 3) - 0.5), x, y)
    elif k in ('road',): c = setts_ring(X, Z, d, a, x, y, z)
    elif k == 'street': c = setts(x, y, s, t, z, wp, v0=4.2)
    elif k == 'kerb2': c = tone(STONE, 5.0 - (0.9 if d > ROAD + 0.35 else 0), x, y)
    else: c = flag(X, Z, x, y, z)
    sh_ = 0.0
    edge = 40.0 if Z < 40 else (34.0 if Z < 62 else 28.0)
    sh_ += 0.32 * max(0.0, min(1.0, (abs(X) - (edge - 14.0)) / 14.0))              # the houses' shade on the paving
    sh_ += 0.16 * max(0.0, min(1.0, (17.0 - Z) / 5.0))                              # and towards us, out of the light
    if sh_: c = mix(c, (14, 20, 19), sh_)
    p_ = puddle(X, Z)
    if p_:
        c = mix(c, (24, 32, 30), 0.25)
        if not (puddle(X, Z - z * 1.5 / F) and puddle(X - z * 1.2 / F, Z) and puddle(X + z * 1.2 / F, Z)):
            c = tone(STONE, 2.0, x, y)                                 # the wet dark rim
    return fogged(c, z)
rs.quad((-140, 0, 2.5), (140, 0, 2.5), (-140, 0, 460), ground, cls='ground')

# ---------------------------------------------------------------------------------------------------- facades
def tenement(P, along_z, u0, u1, h, *, gf=11.4, storey=9.6, bay=5.4, seed=0, ground_floor='shops', lit=0.07, lightv=0.0, win_arch=False, ashlar=False,
             pediments=True, shop_lit=0.5, plinth=1.1, side_sign=1):
    """an old stucco tenement front (u runs along it from its corner u0): a rusticated ground floor with arched doors
    and shop windows (or an arcade, cut out -- see arcade()), a string course, upper floors of windows in moulded
    surrounds with sills, pediments over the first floor, flat hoods above, quoins, a drainpipe, the cornice band.
    Returns (shader, part) -- part(uu, Y) names the piece of the front a point falls on."""
    span = u1 - u0
    nb = max(1, int((span - 1.6) / bay)); pad = (span - nb * bay) / 2
    def bayof(uu):
        b = math.floor((uu - pad) / bay)
        return b, (uu - pad) / bay - b
    def part(uu, Y):
        if uu < 0.9 or uu > span - 0.9:
            return 'quoin'
        if Y < plinth: return 'plinth'
        if h - 1.7 <= Y: return 'cornice'
        if gf <= Y < gf + 0.75: return 'course'
        b, fb = bayof(uu)
        if not (0 <= b < nb): return 'plaster'
        cu = (fb - 0.5) * bay                                            # units from the bay's middle
        if Y < gf:
            if ground_floor == 'arcade':
                spring, w2 = 6.6, bay * 0.36
                dd = math.hypot(cu, max(0.0, Y - spring))
                if abs(cu) < w2 and (Y < spring or dd < w2): return 'open'
                if abs(cu) < w2 + 0.45 and (Y < spring or dd < w2 + 0.45) and Y > spring - 0.3: return 'archivolt'
                return 'rust'
            k = h32(seed, b, 21) % 5
            if k in (0, 3):                                               # an arched door
                spring, w2 = 5.9, 1.35
                dd = math.hypot(cu, max(0.0, Y - spring))
                if abs(cu) < w2 and (Y < spring or dd < w2): return 'door'
                if abs(cu) < w2 + 0.4 and (Y < spring or dd < w2 + 0.4): return 'doorframe'
                return 'rust'
            spring, w2 = 5.6, 1.85                                       # a shop window under a segmental arch
            dd = math.hypot(cu, max(0.0, Y - spring) * 1.6)
            if abs(cu) < w2 and 1.5 < Y and (Y < spring or dd < w2): return 'shop'
            if abs(cu) < w2 + 0.4 and 1.1 < Y and (Y < spring or dd < w2 + 0.4): return 'shopframe'
            return 'rust'
        f = math.floor((Y - gf - 0.75) / storey); fv = (Y - gf - 0.75) - f * storey
        ww = 1.15
        if win_arch:
            top = 6.0
            if abs(cu) < ww and 1.9 < fv and (fv < top or math.hypot(cu, fv - top) < ww): return 'win'
            if abs(cu) < ww + 0.36 and 1.55 < fv and (fv < top or math.hypot(cu, fv - top) < ww + 0.36): return 'surround'
            if abs(cu) < ww + 0.55 and 1.15 < fv < 1.55: return 'sill'
            if fv > top and math.hypot(cu, fv - top) < ww + 0.75 and abs(cu) < 0.3: return 'hood'      # the keystone
            if abs(cu) < ww + 0.36 and 0.3 < fv < 1.15 and f == 0: return 'apron'
            return 'plaster'
        if abs(cu) < ww and 1.9 < fv < 7.1: return 'win'
        if abs(cu) < ww + 0.36 and 1.55 < fv < 7.45: return 'surround'
        if abs(cu) < ww + 0.55 and 1.15 < fv < 1.55: return 'sill'
        if f == 0 and pediments and 7.45 <= fv < 9.2 and abs(cu) < ww + 0.8 - (fv - 7.45) * 0.9: return 'pediment'
        if f > 0 and 7.45 <= fv < 7.95 and abs(cu) < ww + 0.6: return 'hood'
        if abs(cu) < ww + 0.36 and 0.3 < fv < 1.15 and f == 0: return 'apron'
        return 'plaster'
    def winshade(x, y, uu, Y, z):
        b, fb = bayof(uu)
        f = math.floor((Y - gf - 0.75) / storey); fv = (Y - gf - 0.75) - f * storey
        cu = (fb - 0.5) * bay
        wu, wv = (cu + 1.15) / 2.3, (fv - 1.9) / 5.2
        k = h32(seed, b, f, 33) % 100
        px = z / F
        if wv > 1 - max(0.07, px * 1.6 / 5.2) or wu < max(0.06, px * 1.4 / 2.3): return tone(STONE, 0.6, x, y)   # the reveal's shadow
        if k < lit * 100:                                                                 # lit
            if abs(wu - 0.5) < max(0.05, px * 0.7) or abs(wv - 0.62) < max(0.04, px * 0.4): return tone(WOOD, 2.0, x, y)
            if wv < 0.55 and k % 2: return mix(GLOW[0], CURT[k % len(CURT)], 0.45)       # a warm curtain drawn over the light
            return GLOW[0] if (x + y) % 3 else GLOW[1]
        if k < lit * 100 + 16:                                                            # closed louvred shutters
            r_ = SHUTC[k % 3]
            return tone(r_, 2.4 - (1.2 if (wv * 12) % 1 < 0.28 else 0) - (1.0 if abs(wu - 0.5) < 0.04 else 0) + (0.4 if wv > 0.95 else 0), x, y)
        if k < lit * 100 + 19:                                                            # boarded
            c = tone(WOOD, 3.0 - (1.4 if (wv * 4) % 1 < 0.12 else 0), x, y)
            if abs(wu - wv) < 0.08: c = tone(WOOD, 4.2, x, y)
            return c
        if k < lit * 100 + 22:                                                            # a broken pane
            if wu > 0.5 and wv > 0.5 and abs(math.sin(wu * 23 + k) * 0.2 + 0.7 - wv) > 0.1: return STONE[0]
        c = tone(SKY, 1.2 + wv * 2.6 + (0.9 if (wu + wv * 0.45) % 0.75 < 0.07 else 0), x, y)   # glass with the sky in it
        if abs(wu - 0.5) < max(0.045, px * 0.6) or abs(wv - 0.62) < max(0.035, px * 0.35): c = tone(CREAM_P, 2.6, x, y)
        if k % 5 < 2 and wv < 0.6 - (k % 3) * 0.12:                                       # curtains
            c = mix(CURT[k % len(CURT)], (0, 0, 0), 0.3 + 0.2 * ((wu * 8) % 1 < 0.3))
        return c
    def shopshade(x, y, uu, Y, z):
        b, fb = bayof(uu)
        cu = (fb - 0.5) * bay
        wu = (cu + 1.85) / 3.7; wv = (Y - 1.5) / 4.6
        k = h32(seed, b, 41)
        if k % 100 < shop_lit * 100:                                                      # a lit shop: warm glass, goods on shelves
            if abs(wu - 0.5) < 0.04 or abs(wv - 0.7) < 0.03: return tone(WOOD, 1.6, x, y)
            if 0.12 < wv < 0.2 or 0.42 < wv < 0.48: return tone(WOOD, 2.4, x, y)        # shelves
            if wv < 0.42 and (wu * 9) % 1 < 0.55 and h32(int(wu * 9), int(wv * 6), k) % 3: return tone(WARM, 2.6 + (h32(int(wu * 9), 2) % 3) * 0.5, x, y)
            return GLOW[0] if (x + y) % 2 else GLOW[1]
        if k % 7 == 0:                                                                    # a rolled-down iron shutter
            return tone(METAL, 2.2 + (0.8 if (Y * 3.0) % 1 < 0.5 else 0), x, y)
        if abs(wu - 0.5) < 0.04 or abs(wv - 0.7) < 0.03: return tone(WOOD, 1.6, x, y)
        return tone(SKY, 1.4 + wv * 2.0 + (0.8 if (wu + wv * 0.5) % 0.7 < 0.07 else 0), x, y)
    def doorshade(x, y, uu, Y, z):
        b, fb = bayof(uu)
        cu = (fb - 0.5) * bay
        if Y > 5.9 - 0.1:                                                                 # the fanlight
            if abs(cu) < 0.05 or (math.atan2(Y - 5.9, cu) * 4 / math.pi) % 1 < 0.1: return tone(WOOD, 1.4, x, y)
            return GLOW[0] if h32(seed, b, 5) % 3 == 0 else tone(SKY, 2.2, x, y)
        if abs(Y - 5.6) < 0.25: return tone(WOOD, 1.2, x, y)
        if abs(cu) < 0.05: return WOOD[0]
        pv = 2.4 + (0.6 if 1.2 < Y < 5.0 and (abs(cu) % 1.35) > 0.25 and ((Y - 1.2) % 1.9) > 0.25 else 0)   # raised panels
        return tone(SHUTC[h32(seed, b) % 3] if h32(seed, b, 2) % 2 else WOOD, pv, x, y)
    pipe_u = 1.5 if seed % 2 == 0 else span - 1.5                                          # one drainpipe, by a corner
    def weather(uu, Y, z):
        """the wear on the plaster, in surface coordinates: broad stains and patched repairs, soot under the cornice,
        a darker foot, rain-wash streaks hanging under every sill and under the string course"""
        dv = (wn(0, uu * 0.16, Y * 0.11) - 0.5) * 1.1 + (wn(1, uu * 0.6, Y * 0.45) - 0.5) * 0.35
        if h32(int((uu + 40) / 3.1), int(Y / 2.3), seed, 17) % 19 == 0: dv += 0.5                  # a patch of newer plaster
        dv -= 1.1 * math.exp(-max(0.0, h - 1.7 - Y) / 3.2)                                     # soot under the cornice
        dv -= 0.5 * math.exp(-Y / 3.0)
        b, fb = bayof(uu)
        cu = (fb - 0.5) * bay
        if Y > gf + 0.75 and 0 <= b < nb:
            fa = math.ceil((Y - gf - 0.75 - 1.15) / storey)
            sill_y = gf + 0.75 + fa * storey + 1.15
            dd = sill_y - Y
            ln = 2.2 + (h32(seed, b, fa, 5) % 5) * 0.8
            prof = max(0.0, wn(3, uu * 2.4 + seed, 7.0) - 0.35) * 1.6
            if 0 <= dd < ln and abs(cu) < 1.6: dv -= min(1.0, prof) * 1.1 * (1 - dd / ln) ** 1.3
        if Y < gf:
            dd = gf - Y; ln = 1.6 + 2.4 * wn(2, uu * 0.9, 3.0)
            prof = max(0.0, wn(3, uu * 1.9 + 7, 2.0) - 0.4) * 1.8
            if dd < ln: dv -= min(1.0, prof) * 0.9 * (1 - dd / ln)
        if wn(2, uu * 3.3, 11.0) > 0.74: dv -= 0.35 * (1 - min(1.0, max(0.0, (h - Y) / h)))      # long drips from the roof
        return dv
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        uu = (Z if along_z else X) * side_sign - u0
        p = part(uu, Y)
        if p == 'open': return None
        wv = (weather(uu, Y, z) + lightv) if p not in ('win', 'shop', 'door', 'shopframe') else lightv * 0.5
        if ashlar and p == 'plaster':                                                     # dressed stone instead of plaster
            row = math.floor(Y / 1.15); off = (row % 2) * 0.9 + (h32(row, seed) % 3) * 0.3
            bl = math.floor((uu + off) / 1.8)
            fu_, fv_ = ((uu + off) / 1.8) % 1, (Y / 1.15) % 1
            jt = max(0.05, z / F / 1.15 * 1.1)
            v = 2.5 + wv + (h32(bl, row, seed, 7) % 4) * 0.28 - (0.6 if h32(bl, row, 9) % 9 == 0 else 0)
            if fv_ < jt or fu_ < jt * 0.64: v -= 1.3
            elif fv_ > 1 - jt * 1.2: v += 0.4                                             # the lit top arris
            return fogged(tone(GREY_P if seed % 2 else P, v, x, y), z, 0.92)
        if p in ('plaster',): c = tone(P, 2.5 + wv, x, y)
        elif p == 'quoin': c = tone(P, 3.6 + wv + (0.5 if math.floor(Y / 1.1) % 2 else -0.3) - (1.4 if (Y / 1.1) % 1 < max(0.06, z / F / 1.1) else 0), x, y)
        elif p == 'plinth': c = tone(STONE, 2.8 + wv * 0.6 - (1.2 if (uu * 0.8) % 1 < 0.05 else 0), x, y)
        elif p == 'cornice': c = tone(P, 4.0 + wv * 0.5 - (h - Y) * 0.9, x, y)
        elif p == 'course': c = tone(P, 4.2 + wv * 0.5 - (gf + 0.75 - Y) * 2.4, x, y)
        elif p == 'rust':                                                                 # rusticated ground floor: deep joints
            c = tone(P, 2.6 + wv - (1.5 if (Y / 1.25) % 1 < max(0.08, z / F / 1.25 * 1.2) else 0), x, y)
        elif p == 'archivolt': c = tone(P, 3.6 + wv * 0.6 - (0.9 if math.floor(math.atan2(Y - 6.6, (uu % bay)) * 5) % 2 else 0), x, y)
        elif p == 'surround': c = tone(P, 3.9 + wv * 0.7, x, y)
        elif p == 'sill': c = tone(P, 4.4 + wv * 0.5, x, y)
        elif p == 'pediment': c = tone(P, 3.8 + wv * 0.6 + (0.5 if (Y - gf) % storey > 8.3 else 0), x, y)
        elif p == 'hood': c = tone(P, 4.2 + wv * 0.5, x, y)
        elif p == 'apron': c = tone(P, 3.3 + wv * 0.7, x, y)
        elif p == 'win': c = winshade(x, y, uu, Y, z)
        elif p == 'shop': c = shopshade(x, y, uu, Y, z)
        elif p == 'shopframe': c = tone(WOOD, 2.0, x, y)
        elif p == 'door': c = doorshade(x, y, uu, Y, z)
        elif p == 'doorframe': c = tone(P, 3.8 + wv * 0.6, x, y)
        else: c = tone(P, 2.8 + wv, x, y)
        if p not in ('win', 'shop', 'door', 'quoin') and abs(uu - pipe_u) < max(0.14, z / F * 0.6) and Y > 0.4:
            c = tone(METAL, 1.0 + (1.0 if (Y % 3.1) < 0.3 else 0) + (0.6 if uu < pipe_u else 0), x, y)   # the drainpipe, its collars
        return fogged(c, z, 0.92)
    return sh, part

def ledge(along_z, X, z0, z1, Y0, Y1, out, P, v=4.6):
    """a moulding that sticks out of a front (string course, cornice, sill): a thin box"""
    face = lambda x, y, s, t, z, wp: fogged(tone(P, v + (0.6 if t > 0.6 else -0.3), x, y), z)
    under = lambda x, y, s, t, z, wp: fogged(tone(P, 1.6, x, y), z)
    top = lambda x, y, s, t, z, wp: fogged(tone(P, v + 0.8, x, y), z)
    if along_z:
        xa, xb = (X, X + out) if X < 0 else (X - out, X)
        rs.box(xa, xb, Y0, Y1, z0, z1, face, face, top=top, bottom=under, cls='prop')
    else:
        rs.box(z0, z1, Y0, Y1, X - out, X, face, face, top=top, bottom=under, cls='prop')

def roof(Xf, z0, z1, h, side, depth=7.0, rise=8.0, seed=0, deep=26.0, mat=SLATE_R, gable=True):
    """a mansard roof over a row house: the steep slope from the cornice back into the block, dormers, a gable end
    at the block's near end, chimneys"""
    Xi = Xf + side * depth                                                     # where the slope meets the flat top
    def slope(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = 2.4 + (0.6 if (Y * 2.2) % 1 < 0.5 else 0) - (0.9 if ((Y * 2.2) % 1) < 0.12 else 0) + (h32(int(Z * 1.6), int(Y * 2.2), seed) % 3) * 0.2
        dz = (Z - z0 + 2.0) % 5.4
        if 1.0 < dz < 3.0 and h + 2.0 < Y < h + 5.2:                           # a dormer
            if 1.35 < dz < 2.65 and Y < h + 4.4:
                return fogged(GLOW[0] if h32(int(Z / 5.4), seed, 9) % 7 == 0 else tone(SKY, 1.6 + (Y - h - 2) * 0.5, x, y), z)
            return fogged(tone(GREY_P, 3.6 - (0.8 if Y > h + 4.8 else 0), x, y), z)
        if wn(2, Z * 0.5, Y * 0.7) > 0.62: v -= 0.7                             # moss, patched slates
        return fogged(tone(mat, v, x, y), z)
    rs.quad((Xf - side * 0.6, h, z0), (Xf - side * 0.6, h, z1), (Xi, h + rise, z0), slope, cls='wall')
    if gable:
        def gab(x, y, s, t, z, wp): return fogged(tone(mat, 1.6 + t * 0.6, x, y), z)
        Xd = Xf + side * deep
        rs.quad((Xd, h, z0), (Xf - side * 0.6, h, z0), (Xd, h + rise, z0), gab,
                clip=lambda a, b: a < 1 - ((depth + 0.6) / (deep + 0.6)) * b, cls='wall')
    for k in range(int((z1 - z0) / 9) + 1):                                        # chimneys on the ridge
        if h32(seed, k, 3) % 3 == 0: continue
        zc = z0 + 3 + k * 9 + h32(seed, k) % 4
        if zc > z1 - 1.5: break
        Xc = Xi + side * (1.5 + h32(seed, k, 4) % 3)
        hh = h + rise + 3.0 + h32(seed, k, 5) % 3
        xa, xb = sorted((Xc, Xc + side * 2.2))
        rs.box(xa, xb, h + rise - 1, hh, zc, zc + 1.6, concrete(3.0, ROSE_P), concrete(2.2, ROSE_P), top=concrete(3.6, STONE), cls='wall')
        for j in range(2):                                                         # chimney pots
            rs.box(xa + 0.3 + j * 1.0, xa + 0.9 + j * 1.0, hh, hh + 1.0, zc + 0.4, zc + 1.0, concrete(3.4, TILE_R), concrete(2.6, TILE_R), cls='prop')

def balconies_on(X, side, z0, z1, f, P, seed, gf=11.4, storey=9.6, bay=5.4):
    """wrought-iron balconies on floor f of a row house (side -1 = the left row): a stone slab on brackets, a railing of
    bars, now and then a plant pot or washing hung over it"""
    span = z1 - z0; nb = max(1, int((span - 1.6) / bay)); pad = (span - nb * bay) / 2
    Y = gf + 0.75 + f * storey + 1.3
    d = 1.5
    for b in range(nb):
        if h32(seed, b, f, 61) % 3 == 0: continue
        zc = z0 + pad + (b + 0.5) * bay; w0, w1 = zc - 1.9, zc + 1.9
        xo = X - side * d
        xa, xb = sorted((X, xo))
        slab = lambda x, y, s, t, z, wp: fogged(tone(P, 3.6 if t > 0.5 else 2.0, x, y), z)
        rs.box(xa, xb, Y - 0.35, Y, w0, w1, slab, slab, top=slab, bottom=lambda x, y, s, t, z, wp: fogged(tone(P, 1.4, x, y), z), cls='prop')
        iron = lambda x, y, s, t, z, wp: fogged(METAL[0] if (x + y) % 3 else METAL[1], z)
        rs.quad((xo, Y, w0), (xo, Y, w1), (xo, Y + 2.2, w0),
                lambda x, y, s, t, z, wp: fogged(METAL[0], z) if ((s * 3.8 * 4) % 1 < 0.28 or t > 0.9 or t < 0.08 or abs(t - 0.45) < 0.05) else None, cls='prop', cut=True)
        rs.quad((xo, Y, w0), (X, Y, w0), (xo, Y + 2.2, w0),
                lambda x, y, s, t, z, wp: fogged(METAL[0], z) if ((s * 4) % 1 < 0.3 or t > 0.9) else None, cls='prop', cut=True)
        k = h32(seed, b, f, 62) % 4
        if k == 0:                                                                     # a plant pot
            rs.box(xo + side * 0.6 - 0.35, xo + side * 0.6 + 0.35, Y, Y + 0.8, w0 + 0.6, w0 + 1.3, concrete(3.0, TILE_R), concrete(2.2, TILE_R), cls='prop')
            rs.quad((xo + side * 0.6, Y + 0.8, w0 + 0.5), (xo + side * 0.6, Y + 0.8, w0 + 1.5), (xo + side * 0.6, Y + 2.0, w0 + 0.5),
                    lambda x, y, s, t, z, wp: fogged(tone(IVY, 2.6 + (wn(3, wp[2] * 4, wp[1] * 4) - 0.5) * 2, x, y), z) if (s - 0.5) ** 2 + (t - 0.4) ** 2 < 0.22 else None, cls='prop', cut=True)
        elif k == 1:                                                                   # washing over the rail
            c = CURT[h32(seed, b, 5) % len(CURT)]
            rs.quad((xo - side * 0.05, Y + 0.4, w0 + 0.5), (xo - side * 0.05, Y + 0.4, w0 + 1.8), (xo - side * 0.05, Y + 2.15, w0 + 0.5),
                    lambda x, y, s, t, z, wp, c=c: fogged(mix(c, (0, 0, 0), 0.35 + 0.15 * (int(s * 5) % 2)), z), cls='prop')

def row_house(X, z0, z1, h, P, side, seed, ground_floor='shops', lit=0.07, near=True, deep=30.0, rise=8.0,
              lightv=0.0, win_arch=False, ashlar=False, balc=()):
    """one tenement of a row: a deep block with its front along the square (at x=X, side -1 = the left row facing +x)
    and its return wall facing the camera where the row steps in"""
    sh, part = tenement(P, True, z0, z1, h, seed=seed, ground_floor=ground_floor, lit=lit, lightv=lightv, win_arch=win_arch, ashlar=ashlar)
    for f in balc: balconies_on(X, side, z0, z1, f, P, seed)
    Xd = X + side * deep
    xa, xb = sorted((Xd, X))
    def front(x, y, s, t, z, wp):                                                  # the return: plainer, one column of windows
        Xw, Y, Z = wp
        uu = abs(Xw - X)
        if uu < 0.9: return fogged(tone(P, 4.3 + (0.5 if math.floor(Y / 1.1) % 2 else -0.2), x, y), z)
        if Y < 1.1: return fogged(tone(STONE, 3.0, x, y), z)
        if h - 1.7 <= Y: return fogged(tone(P, 4.4 - (h - Y) * 0.9, x, y), z)
        if 11.4 <= Y < 12.15: return fogged(tone(P, 4.6, x, y), z)
        fv = (Y - 12.15) % 9.6; f = math.floor((Y - 12.15) / 9.6)
        if Y > 12.15 and 2.0 < uu < 4.0 and 1.9 < fv < 7.1:
            k = h32(seed, f, 71) % 9
            if k == 0: return fogged(GLOW[0] if (x + y) % 3 else GLOW[1], z)
            if k < 3: return fogged(tone(SHUTC[k % 3], 2.4 - (1.2 if (fv * 2.3) % 1 < 0.28 else 0), x, y), z)
            return fogged(tone(SKY, 2.0 + (fv - 1.9) * 0.5, x, y), z)
        if Y > 12.15 and 1.65 < uu < 4.35 and 1.55 < fv < 7.45: return fogged(tone(P, 4.6, x, y), z)
        return fogged(tone(P, 3.0 + (wn(0, Xw * 0.3, Y * 0.3) - 0.5) * 0.5, x, y), z)
    side_sh = sh
    if ground_floor == 'arcade':
        obj = rs.box(xa, xb, 11.0, h, z0, z1, front, sh, cls='wall')              # upper floors (the arcade is built below)
        rs.quad((X, 0, z0), (X, 0, z1), (X, 11.0, z0), sh, obj=obj, cls='wall', cut=True)
        rs.quad((xa, 0, z0), (xb, 0, z0), (xa, 11.0, z0), front, obj=obj, cls='wall')
    else:
        obj = rs.box(xa, xb, 0, h, z0, z1, front, sh, cls='wall')
    wall_key(obj, part, True)
    if near:                                                                       # real mouldings: string course, cornice
        ledge(True, X, z0, z1, 11.4, 12.15, 0.45, P)
        ledge(True, X, z0, z1, h - 1.7, h - 0.9, 0.7, P, 4.2)
        ledge(True, X, z0, z1, h - 0.9, h, 1.25, P, 4.8)
    roof(X, z0, z1, h, side, seed=seed, deep=deep, rise=rise)
    return obj

# ---------------------------------------------------------------------------------------------------- the left row
LEFT = [  # X front, z0, z1, height, plaster, seed, look
    (-40.0, 12.0, 34.0, 50.0, OCHRE_P, 1, dict(ashlar=True)),
    (-36.0, 40.0, 58.0, 45.0, SAGE_P, 2, dict(balc=(1,))),
    (-31.0, 58.0, 82.0, 43.0, ROSE_P, 3, dict(win_arch=True)),
    (-24.0, 82.0, 114.0, 40.0, CREAM_P, 4, dict(balc=(2,))),
    (-17.0, 114.0, 160.0, 37.0, GREY_P, 5, dict(ashlar=True)),
    (-16.0, 160.0, 230.0, 41.0, OCHRE_P, 6, {}),
    (-16.0, 230.0, 330.0, 36.0, SAGE_P, 7, {}),
]
for (X, z0, z1, hh, P, sd, look) in LEFT:
    row_house(X, z0, z1, hh, P, -1, sd, near=z0 < 70, lit=0.04, lightv=-0.45, **look)
# the side street between the first two houses (towards the Lumen Directorate): its far wall is the next block's
# flank, already taken by the Directorate's living walls -- ivy over the stucco, a clipped hedge along its foot
def ivy_leaves(x, y, X, Y):
    """ivy as leaves, not noise: overlapping clumps lit from above, dark gaps between them, a few pale new leaves"""
    cx, cy = math.floor(X / 0.55), math.floor(Y / 0.45)
    best, bv = 9.0, 0.0
    for i in (cx - 1, cx, cx + 1):
        for j in (cy - 1, cy, cy + 1):
            px_ = (i + (h32(i, j, 31) % 100) / 100.0) * 0.55; py_ = (j + (h32(i, j, 32) % 100) / 100.0) * 0.45
            d = math.hypot((X - px_) / 0.42, (Y - py_) / 0.34)
            if d < best: best, bv = d, (py_ - Y) / 0.34
    if best > 1.0: return tone(IVY, 0.4, x, y)                                          # the dark between the leaves
    v = 2.6 + bv * 1.4 + (wn(3, X * 0.7, Y * 0.7) - 0.5) * 1.4
    if h32(int(X / 0.55), int(Y / 0.45), 33) % 23 == 0: v += 1.4
    return tone(IVY, v, x, y)
def ivy_wall(x, y, s, t, z, wp):
    X, Y, Z = wp
    top = 9.0 + 16.0 * wn(1, X * 0.18, 4.0) + 14.0 * max(0.0, 1 - (-36.4 - X) / 9.0)    # higher up the corner
    strand = wn(3, X * 2.2, 9.0) > 0.66 and Y < top + 5.0 * wn(2, X * 1.7, 3.0)
    cover = (Y < top + (wn(2, X * 0.9, Y * 0.9) - 0.5) * 3.0) or strand
    if cover:
        return fogged(ivy_leaves(x, y, X, Y), z)
    return fogged(tone(SAGE_P, 3.2 + (wn(0, X * 0.3, Y * 0.3) - 0.5) * 0.6, x, y), z)
rs.quad((-120, 0, 39.95), (-36.4, 0, 39.95), (-120, 42.0, 39.95), ivy_wall, cls='wall')
def hedge(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 2.6 + t * 1.4 + (wn(3, X * 3.0, Y * 3.0 + Z) - 0.5) * 2.0
    if Y > 3.2 + wn(1, X * 1.3, Z) * 1.4: return None
    return fogged(tone(IVY, v, x, y), z)
rs.quad((-120, 0.3, 38.6), (-41.0, 0.3, 38.6), (-120, 4.6, 38.6), hedge, cls='prop', cut=True)
rs.quad((-120, 0.02, 34.0), (-40.0, 0.02, 34.0), (-120, 0.02, 40.0), lambda x, y, s, t, z, wp: fogged(flag(wp[0], wp[2], x, y, z, 4.0), z), cls='ground')

# ---------------------------------------------------------------------------------------------------- the right row on its arcade
RIGHT = [
    (41.0, 12.0, 40.0, 52.0, CREAM_P, 11, 'arcade', dict(win_arch=True)),
    (35.0, 40.0, 62.0, 47.0, OCHRE_P, 12, 'arcade', dict(balc=(1,))),
    (29.0, 62.0, 88.0, 44.0, SAGE_P, 13, 'shops', dict(ashlar=True, balc=(2,))),
    (22.0, 88.0, 120.0, 41.0, ROSE_P, 14, 'shops', {}),
    (17.0, 120.0, 170.0, 38.0, CREAM_P, 15, 'shops', dict(win_arch=True)),
    (16.0, 170.0, 240.0, 42.0, GREY_P, 16, 'shops', {}),
    (16.0, 240.0, 330.0, 35.0, OCHRE_P, 17, 'shops', {}),
]
ARC_D = 5.5                                                                       # the arcade's depth (the walk behind the piers)
def arcade(X, z0, z1, P, seed, bay=5.4):
    span = z1 - z0; nb = max(1, int((span - 1.6) / bay)); pad = (span - nb * bay) / 2
    def back(x, y, s, t, z, wp):                                                  # the back wall: shopfronts and doors, lit
        _, Y, Z = wp
        b = math.floor((Z - z0 - pad) / bay); fb = (Z - z0 - pad) / bay - b
        cu = (fb - 0.5) * bay
        k = h32(seed, b, 81) % 4
        if Y > 9.6: return fogged(tone(P, 1.8, x, y), z)
        if abs(cu) < 1.7 and 0.4 < Y < 7.0:
            if k == 0:
                if abs(cu) < 1.2 and Y < 6.4: return fogged(tone(WOOD, 1.8 + (0.5 if (Y % 1.9) > 0.3 else 0), x, y), z)
                return fogged(tone(WOOD, 1.0, x, y), z)
            if abs(cu) < 0.06 or abs(Y - 4.8) < 0.08: return fogged(tone(WOOD, 1.2, x, y), z)
            if k == 3: return fogged(tone(METAL, 1.6 + (0.6 if (Y * 3) % 1 < 0.5 else 0), x, y), z)
            if Y < 2.0: return fogged(tone(WARM, 2.0 + (h32(int(Z * 3), 2) % 3) * 0.4, x, y), z)
            return fogged(GLOW[0] if (x + y) % 3 else GLOW[1], z)
        if abs(cu) < 2.0 and 0.2 < Y < 7.3: return fogged(tone(WOOD, 1.4, x, y), z)
        return fogged(tone(P, 2.2 + (wn(0, Z * 0.3, Y * 0.3) - 0.5) * 0.5, x, y), z)
    rs.quad((X + ARC_D, 0, z0), (X + ARC_D, 0, z1), (X + ARC_D, 11.0, z0), back, cls='wall')
    floor_ = lambda x, y, s, t, z, wp: fogged(flag(wp[2], wp[0] * 3, x, y, z, 3.8), z)
    rs.quad((X, 0.35, z0), (X + ARC_D, 0.35, z0), (X, 0.35, z1), floor_, cls='ground')
    rs.quad((X, 0.0, z0), (X, 0.0, z1), (X, 0.35, z0), lambda x, y, s, t, z, wp: fogged(tone(STONE, 4.6, x, y), z), cls='prop')
    for b in range(nb):
        zc = z0 + pad + (b + 0.5) * bay; w2 = bay * 0.36; spring = 6.6
        jamb = lambda x, y, s, t, z, wp: fogged(tone(P, 2.4 - (1.2 if (wp[1] / 1.25) % 1 < 0.1 else 0), x, y), z)
        rs.quad((X, 0, zc + w2), (X + 1.4, 0, zc + w2), (X, spring, zc + w2), jamb, cls='wall')     # the far jamb (faces us)
        n = 12
        for j in range(n):                                                        # the soffit, strip by strip
            a0, a1 = math.pi * j / n, math.pi * (j + 1) / n
            P0 = (X, spring + w2 * math.sin(a0), zc + w2 * math.cos(a0))
            P1 = (X, spring + w2 * math.sin(a1), zc + w2 * math.cos(a1))
            rs.quad(P0, P1, (X + 1.4, P0[1], P0[2]), lambda x, y, s, t, z, wp: fogged(tone(P, 1.8 + (0.4 if (wp[1] * 2) % 1 < 0.5 else 0), x, y), z), cls='wall')
        # a lantern on a bracket inside each other arch
        if b % 2 == 0:
            ly = spring + w2 - 1.4
            rs.line3((X + ARC_D, ly + 1.2, zc), (X + ARC_D - 0.8, ly + 1.2, zc), lambda x, y, s, t, z, wp: METAL[0], w=0.12)
            rs.box(X + ARC_D - 1.15, X + ARC_D - 0.45, ly, ly + 1.0, zc - 0.35, zc + 0.35,
                   lambda x, y, s, t, z, wp: GLOW[3] if 0.2 < s < 0.8 and 0.15 < t < 0.85 else METAL[0], lambda x, y, s, t, z, wp: METAL[0], cls='emit')
for (X, z0, z1, hh, P, sd, gfl, look) in RIGHT:
    row_house(X, z0, z1, hh, P, 1, sd, ground_floor=gfl, near=z0 < 70, lit=0.04, lightv=0.1, **look)
    if gfl == 'arcade': arcade(X, z0, z1, P, sd)

# ---------------------------------------------------------------------------------------------------- the end of the street: the city in the haze
def far_house(Xr, zr, wr, hr, seed):
    """a house far down the street: a fogged gable silhouette with a few faint windows"""
    roof_h = 6 + h32(seed, 5) % 8
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        if Y > hr:
            if abs(s - 0.5) * 2 > 1 - (Y - hr) / roof_h: return None
            return HAZE[2] if s < 0.5 else HAZE[3]
        if (X * 0.5) % 1 < 0.3 and (Y * 0.28) % 1 < 0.35 and Y > 4 and h32(int(X * 0.5), int(Y * 0.28), seed) % 9 == 0:
            return HAZE[1] if h32(int(X), int(Y), 3) % 4 else GLOW[0]
        return HAZE[3] if (wn(1, X * 0.3, Y * 0.3) > 0.5) else HAZE[4]
    rs.quad((Xr - wr / 2, 0, zr), (Xr + wr / 2, 0, zr), (Xr - wr / 2, hr + roof_h, zr), sh, cls='wall', cut=True)
for k in range(40):
    Xr = -220 + k * 11 + h32(k, 1) % 6; zr = (350, 390, 430)[h32(k, 2) % 3]; hr = 26 + h32(k, 3) % 24; wr = 8 + h32(k, 4) % 8
    far_house(Xr, zr, wr, hr, k)
def spire(Xs, zs, hb, ht, w):
    """a church tower in the haze: the shaft with belfry openings and a set-back stage, a tall needle spire"""
    def shaft(x, y, s, t, z, wp):
        Y = wp[1]
        if hb - 12 < Y < hb - 4 and (s * 3) % 1 > 0.35 and (s * 3) % 1 < 0.75: return HAZE[1]
        if abs(Y - (hb - 13)) < 0.9: return HAZE[4]
        return HAZE[3] if s < 0.42 else HAZE[4]
    rs.quad((Xs - w / 2, 0, zs), (Xs + w / 2, 0, zs), (Xs - w / 2, hb, zs), shaft, cls='wall')
    rs.quad((Xs - w * 0.36, hb, zs), (Xs + w * 0.36, hb, zs), (Xs - w * 0.36, hb + 6, zs),
            lambda x, y, s, t, z, wp: HAZE[3] if s < 0.45 else HAZE[4], cls='wall')
    rs.quad((Xs - w * 0.36, hb + 6, zs), (Xs + w * 0.36, hb + 6, zs), (Xs - w * 0.36, hb + 6 + ht, zs),
            lambda x, y, s, t, z, wp: (HAZE[3] if s < 0.5 else HAZE[4]) if abs(s - 0.5) < 0.5 * (1 - t) ** 1.2 else None, cls='wall', cut=True)
spire(-50, 380, 64, 58, 16); spire(-20, 430, 58, 40, 11); spire(56, 400, 60, 52, 14)
rs.quad((14, 0, 380), (34, 0, 380), (14, 62, 380), lambda x, y, s, t, z, wp: HAZE[2] if s < 0.4 else HAZE[3], cls='wall')
rs.quad((14, 62, 380), (34, 62, 380), (14, 72, 380), lambda x, y, s, t, z, wp: (HAZE[3] if s < 0.4 else HAZE[2]) if (s * 2 - 1) ** 2 + t ** 2 <= 1 else None, cls='wall', cut=True)
rs.line3((24, 72, 380), (24, 80, 380), lambda x, y, s, t, z, wp: HAZE[3], w=0.9)

# ---------------------------------------------------------------------------------------------------- street furniture
def wall_lantern(X, Y, Z, side, lit=True):
    """an iron bracket off a wall with a caged lantern hanging from it (side: +1 = on the left row's front, sticking out to +x)"""
    arm = 1.6
    rs.line3((X, Y + 1.6, Z), (X + side * arm, Y + 1.6, Z), lambda x, y, s, t, z, wp: fogged(METAL[0], z), w=0.14)
    rs.line3((X, Y + 0.6, Z), (X + side * arm * 0.7, Y + 1.6, Z), lambda x, y, s, t, z, wp: fogged(METAL[0], z), w=0.1)
    cx = X + side * (arm - 0.15)
    rs.box(cx - 0.4, cx + 0.4, Y - 0.2, Y + 1.25, Z - 0.4, Z + 0.4,
           lambda x, y, s, t, z, wp: (GLOW[3] if lit else tone(SKY, 2.4, x, y)) if 0.18 < s < 0.82 and 0.15 < t < 0.82 else fogged(METAL[0], z),
           lambda x, y, s, t, z, wp: (GLOW[2] if lit else METAL[1]) if 0.25 < s < 0.75 and 0.15 < t < 0.82 else fogged(METAL[0], z), cls='emit' if lit else 'prop')
    rs.box(cx - 0.55, cx + 0.55, Y + 1.25, Y + 1.5, Z - 0.55, Z + 0.55, lambda x, y, s, t, z, wp: fogged(METAL[1], z), lambda x, y, s, t, z, wp: fogged(METAL[0], z), cls='prop')
for (Z, lit) in ((22.0, True), (29.5, False)): wall_lantern(-40.0, 8.0, Z, 1, lit)
for (Z, lit) in ((47.0, True), (55.0, True)): wall_lantern(-36.0, 8.0, Z, 1, lit)
for (Z, lit) in ((70.0, True),): wall_lantern(-31.0, 8.0, Z, 1, lit)
for (Z, lit) in ((75.0, True),): wall_lantern(29.0, 8.0, Z, -1, lit)
for (Z, lit) in ((100.0, True),): wall_lantern(22.0, 8.0, Z, -1, lit)
for (Z, lit) in ((95.0, False),): wall_lantern(-24.0, 8.0, Z, 1, lit)

def hanging_sign(X, Z, side, Y=13.6, kind='boot', seed=0):
    """a wrought bracket with a painted board hanging from it -- a picture, no words"""
    arm = 3.2
    rs.line3((X, Y, Z), (X + side * arm, Y, Z), lambda x, y, s, t, z, wp: fogged(METAL[0], z), w=0.16)
    rs.line3((X, Y - 1.6, Z), (X + side * arm * 0.55, Y, Z), lambda x, y, s, t, z, wp: fogged(METAL[0], z), w=0.12)
    x0, x1 = sorted((X + side * 0.7, X + side * (arm - 0.1)))
    def board(x, y, s, t, z, wp):
        u, v = s, t
        if u < 0.07 or u > 0.93 or v < 0.07 or v > 0.93: return fogged(tone(WOOD, 3.4, x, y), z)
        if kind == 'boot':
            if (0.32 < u < 0.52 and 0.32 < v < 0.8) or (0.32 < u < 0.78 and 0.24 < v < 0.42 and (u - 0.78) ** 2 / 0.1 + (v - 0.24) ** 2 / 0.06 < 1.6):
                return fogged(tone(WARM, 1.6 + (0.6 if v > 0.7 else 0), x, y), z)
        elif kind == 'key':
            if (u - 0.3) ** 2 + (v - 0.55) ** 2 < 0.02 and (u - 0.3) ** 2 + (v - 0.55) ** 2 > 0.006: return fogged(GLOW[1], z)
            if 0.42 < u < 0.8 and 0.51 < v < 0.59: return fogged(GLOW[1], z)
            if (0.66 < u < 0.7 or 0.74 < u < 0.78) and 0.4 < v < 0.55: return fogged(GLOW[1], z)
        elif kind == 'tankard':
            if 0.32 < u < 0.6 and 0.22 < v < 0.75: return fogged(tone(METAL, 3.2 - u * 2, x, y), z)
            if 0.6 < u < 0.74 and 0.35 < v < 0.62 and not (0.64 < u < 0.7 and 0.42 < v < 0.55): return fogged(tone(METAL, 2.4, x, y), z)
            if 0.3 < u < 0.62 and 0.75 < v < 0.84: return fogged(BONE[4], z)
        return fogged(tone(SHUTC[seed % 3], 2.6 + (wn(0, u * 5, v * 5) - 0.5), x, y), z)
    for xc in (x0 + 0.3, x1 - 0.3): rs.line3((xc, Y, Z), (xc, Y - 0.9, Z), lambda x, y, s, t, z, wp: fogged(METAL[0], z), w=0.08)
    rs.quad((x0, Y - 3.6, Z + 0.01), (x1, Y - 3.6, Z + 0.01), (x0, Y - 0.9, Z + 0.01), board, cls='prop')
hanging_sign(-36.0, 51.0, 1, kind='boot', seed=1)
hanging_sign(-31.0, 66.0, 1, kind='key', seed=2)
hanging_sign(29.0, 70.0, -1, kind='tankard', seed=0)

def stall(Xc, Zc, w=5.0, d=3.0, seed=0):
    """a closed market stall: a trestle counter, a canvas roof on four poles, the canvas tied down over the goods"""
    x0, x1, z0, z1 = Xc - w / 2, Xc + w / 2, Zc - d / 2, Zc + d / 2
    cv = ramp_('#1f1d17 #2c2a21 #3b382c #4b4738 #5b5644') if seed % 2 else ramp_('#221c18 #30271f #3f3329 #4f4033 #5e4d3e')
    def cloth(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = 3.0 + 0.9 * math.sin((X if abs(X - Xc) < w else Z) * 3.1 + seed) - (0.8 if (s * 6) % 1 < 0.12 else 0)
        if (s * 3 + seed) % 1 < 0.33 and seed % 3 == 0: v -= 0.8                    # faded stripes
        return fogged(tone(cv, v, x, y), z)
    rs.box(x0, x1, 0.0, 3.4, z0, z1, cloth, cloth, top=cloth, cls='prop')           # the goods under the tied canvas
    for (px_, pz) in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
        rs.line3((px_, 0, pz), (px_, 6.6, pz), lambda x, y, s, t, z, wp: fogged(tone(WOOD, 2.4, x, y), z), w=0.22)
    rs.quad((x0 - 0.4, 6.4, z0 - 0.5), (x1 + 0.4, 6.4, z0 - 0.5), (x0 - 0.4, 7.2, z1 + 0.5), cloth, cls='prop')
    rs.quad((x0 - 0.4, 6.4, z0 - 0.5), (x1 + 0.4, 6.4, z0 - 0.5), (x0 - 0.4, 5.6, z0 - 0.5),
            lambda x, y, s, t, z, wp: fogged(tone(cv, 2.2, x, y), z) if (s * 9) % 1 < 0.7 else None, cls='prop', cut=True)   # the scalloped valance
    for k in range(3):                                                              # crates stacked beside it
        rs.box(x1 + 0.4 + (k % 2) * 0.2, x1 + 2.0 + (k % 2) * 0.2, k * 1.2, (k + 1) * 1.2, z0 + 0.2, z0 + 1.6,
               planks(2.8 - k * 0.2, WARM, w=0.5, seed=seed + k), planks(2.2, WARM, w=0.5, seed=seed + k), top=planks(3.4, WARM, w=0.5), cls='prop')
stall(28.0, 50.0, seed=1)
stall(22.5, 60.0, w=4.4, seed=2)

def fountain(Xf, Zf, R=3.2):
    """an old drinking fountain: a round stone basin (a cylinder: shaded camera-facing card + its rim and the water
    inside), a fluted column with a bowl on top, thin threads of water"""
    def basin(x, y, s, t, z, wp):
        u = s * 2 - 1
        v = 4.4 - u * 1.4 - abs(u) ** 3 * 1.6 + (wn(1, wp[0] * 2, wp[1] * 2) - 0.5) * 0.8
        if t > 0.82: v += 0.8                                                           # the lip
        if (wp[1] * 1.6) % 1 < 0.08: v -= 0.8
        if t < 0.25 and wn(2, wp[0] * 3, wp[1] * 3) > 0.5: return fogged(tone(IVY, 1.8, x, y), z)   # moss at the foot
        return fogged(tone(STONE, v, x, y), z)
    rs.quad((Xf - R, 0, Zf), (Xf + R, 0, Zf), (Xf - R, 1.7, Zf), basin, cls='prop')
    def rim(x, y, s, t, z, wp):
        u, w = s * 2 - 1, t * 2 - 1
        d = u * u + w * w
        if d > 1: return None
        if d > 0.72: return fogged(tone(STONE, 5.4 - w * 0.8, x, y), z)
        return fogged(tone(SKY, 3.6 + w * 1.6 + (0.8 if (wn(0, wp[0] * 4, wp[2] * 4) > 0.62) else 0), x, y), z)   # the water mirrors the sky
    rs.quad((Xf - R, 1.7, Zf - R * 0.2), (Xf + R, 1.7, Zf - R * 0.2), (Xf - R, 1.7, Zf + R * 1.8), rim, cls='prop', cut=True)
    def column(x, y, s, t, z, wp):
        u = s * 2 - 1
        v = 4.6 - u * 1.6 + (-0.7 if (s * 6) % 1 < 0.25 else 0)
        return fogged(tone(STONE, v, x, y), z)
    rs.quad((Xf - 0.6, 1.7, Zf + R * 0.8), (Xf + 0.6, 1.7, Zf + R * 0.8), (Xf - 0.6, 6.2, Zf + R * 0.8), column, cls='prop')
    def bowl(x, y, s, t, z, wp):
        u = s * 2 - 1
        if abs(u) > 0.4 + 0.6 * t: return None
        return fogged(tone(STONE, 5.0 - u * 1.2 + t, x, y), z)
    rs.quad((Xf - 2.0, 6.0, Zf + R * 0.8 - 0.1), (Xf + 2.0, 6.0, Zf + R * 0.8 - 0.1), (Xf - 2.0, 7.1, Zf + R * 0.8 - 0.1), bowl, cls='prop', cut=True)
    rs.box(Xf - 0.3, Xf + 0.3, 7.0, 7.9, Zf + R * 0.8 - 0.3, Zf + R * 0.8 + 0.3, concrete(4.0, STONE), concrete(3.0, STONE), cls='prop')
    for dx in (-1.8, 1.8):                                                            # threads of water from the bowl
        rs.line3((Xf + dx, 6.6, Zf + R * 0.8 - 0.2), (Xf + dx * 1.4, 1.9, Zf + R * 0.8 - 0.4),
                 lambda x, y, s, t, z, wp: fogged(tone(SKY, 6.2 if (y % 3) else 5.0, x, y), z), w=0.12)
fountain(-14.5, 43.0, R=3.5)

def bollard(X, Z):
    rs.box(X - 0.5, X + 0.5, 0, 2.2, Z - 0.5, Z + 0.5, concrete(4.2, STONE), concrete(3.2, STONE), top=concrete(5.0, STONE), cls='prop')
    rs.disc(X, 2.2, Z, 0.5, lambda x, y, s, t, z, wp: fogged(tone(STONE, 4.6 - t * 1.5 - s, x, y), z) if t < 0.15 else None, cls='prop')
# a drain grate, litter, a few fallen leaves
rs.box(-6.4, -4.8, 0.0, 0.05, 31.0, 31.8, lambda x, y, s, t, z, wp: METAL[0], lambda x, y, s, t, z, wp: METAL[0],
       top=lambda x, y, s, t, z, wp: METAL[0] if (s * 7) % 1 < 0.45 else STONE[0], cls='ground')
for k in range(22):
    fx, fz = -30 + (h32(k, 41) % 620) / 10.0, 13.0 + (h32(k, 42) % 300) / 10.0
    c = [BONE[3], WARM[3], WARM[2], CAP[2]][k % 4]
    rs.quad((fx - 0.22, 0.03, fz - 0.14), (fx + 0.22, 0.03, fz - 0.14), (fx - 0.22, 0.03, fz + 0.14),
            lambda x, y, s, t, z, wp, c=c: fogged(c if (x + y) % 4 else mix(c, (0, 0, 0), 0.3), z), cls='ground')

# wires across the street with a lamp hung in the middle (a lamp on a wire, not a post)
for (zz, yy, sag) in ((96.0, 30.0, 2.4),):
    rs.line3((-24.0, yy, zz), (22.0, yy, zz), lambda x, y, s, t, z, wp: fogged(STONE[1], z, 0.6), w=0.07, sag=sag)
LZ = 96.0
rs.line3((-1.5, 27.6, LZ), (-1.5, 26.0, LZ), lambda x, y, s, t, z, wp: fogged(METAL[0], z, 0.6), w=0.12)
rs.box(-2.3, -0.7, 24.6, 26.0, LZ - 0.5, LZ + 0.5, lambda x, y, s, t, z, wp: GLOW[3] if 0.2 < s < 0.8 and t < 0.7 else METAL[0],
       lambda x, y, s, t, z, wp: METAL[0], cls='emit')

# ---------------------------------------------------------------------------------------------------- the skyship Verdigrace, far off
SHIP_G = ramp_('#0b1510 #112019 #182c21 #203a2a #2a4934 #36593f #446a4c')
SHIP_N = ramp_('#1f2a17 #2f3d20 #43542b #5a6c38')
SHIP_H = ramp_('#110f0b #1c1912 #29241a #362f22 #453c2b')
SHIP_F = ramp_('#0e1712 #16241b #213426 #2c4432 #38533d')
def skyship_img(K=0.8):
    """the Verdigrace in profile, bow to the left (after skyship.png / skyship_board.png): a living bladder in a net of
    vines with spore lights, a fish's dorsal fin and a forked tail, the gondola-hull with its fiddlehead bow and stern
    fin on vine rigging, tendrils trailing under it. Drawn at K x a 268x150 layout."""
    Wd, Hd = int(268 * K) + 4, int(150 * K) + 4
    r = Rig(Wd, Hd)
    P = lambda x, y: (x * K + 2, y * K + 2)
    R_ = lambda v: v * K
    MG = Mat(SHIP_G, 'skin', 0.24, 0.15, outline=(10, 16, 12)); MN = Mat(SHIP_N, 'fur', 0.3); MH = Mat(SHIP_H, 'wood', 0.22, outline=(12, 10, 8))
    MF = Mat(SHIP_F, 'skin', 0.2, outline=(10, 16, 12))
    cx, cy = 122, 50
    t0 = P(196, 50)
    r.poly([P(196, 46), P(236, 14), P(246, 10), P(238, 30), P(222, 50), P(240, 76), P(246, 90), P(232, 84), P(196, 58)], MF, round_=0.3, group='tail',
           vfun=lambda x, y: -0.2 if int(math.atan2(y - t0[1], x - t0[0]) * 12) % 2 == 0 else 0)
    d0 = P(120, 0)
    r.poly([P(122, 20), P(150, 0), P(170, 2), P(162, 10), P(176, 16), P(186, 26), P(150, 24)], MF, round_=0.3, group='dorsal',
           vfun=lambda x, y: -0.22 if int((x - d0[0]) * 0.55 / K) % 2 == 0 else 0)
    def net(x, y, u, w):
        """an organic net of vines: the edges between jittered cells"""
        gu, gw = u * 6.0, w * 2.6
        best = [9.0, 9.0]
        for i in range(int(math.floor(gu)) - 1, int(math.floor(gu)) + 2):
            for j in range(int(math.floor(gw)) - 1, int(math.floor(gw)) + 2):
                px_ = i + (h32(i, j, 3) % 100) / 100.0; py_ = j + (h32(i, j, 4) % 100) / 100.0
                d = math.hypot(gu - px_, gw - py_)
                if d < best[0]: best = [d, best[0]]
                elif d < best[1]: best[1] = d
        e = best[1] - best[0]
        return -0.34 if e < 0.07 else (0.1 if e < 0.13 else 0.0)
    r.ellipsoid(*P(cx + 36, cy + 2), R_(60), R_(25), MG, group='rear', vfun=net)
    r.ellipsoid(*P(cx, cy), R_(96), R_(34), MG, group='bladder', vfun=net)
    GY = 112
    for k, (xa, xb) in enumerate(((70, 82), (96, 102), (124, 122), (150, 142), (172, 160))):
        r.stroke([P(xa + (xb - xa) * t, cy + 30 + (GY - cy - 30) * t + math.sin(t * 6 + k) * 0.6) for t in [i / 40 for i in range(41)]], max(1.0, R_(1.3)), MN, v=0.35, group='rig')
    for k in range(9):
        x0 = 60 + k * 15 + h32(k, 7) % 6; ln = 8 + h32(k, 8) % 18
        r.stroke([P(x0 + math.sin(j * 0.4 + k) * 1.2, cy + 28 + j) for j in range(ln)], 1.0, MN, v=0.3, group='tendril')
    hull = [P(56, GY - 4), P(176, GY - 6), P(192, GY - 12), P(186, GY + 4), P(166, GY + 14), P(96, GY + 16), P(66, GY + 10)]
    r.poly(hull, MH, round_=0.6, group='hull', vfun=lambda x, y: -0.2 if int((y - P(0, GY)[1]) / K) % 4 == 0 else 0)
    r.poly([P(176, GY - 6), P(200, GY - 26), P(210, GY - 24), P(194, GY - 4)], MF, round_=0.3, group='sternfin')
    r.poly([P(150, GY + 12), P(168, GY + 30), P(176, GY + 30), P(164, GY + 10)], MF, round_=0.3, group='keelfin')
    for j in range(22):                                                                     # the fiddlehead stem
        a = j * 0.42; rad = 9 - j * 0.38
        r.stroke([P(54 - math.sin(a) * rad, GY - 14 + math.cos(a) * rad - j * 0.2)], max(1.2, R_(2.0)), MN, v=0.45, group='stem')
    r.poly([P(104, GY - 4), P(150, GY - 5), P(150, GY - 14), P(106, GY - 14)], MH, lift=0.1, round_=0.4, group='cabin')
    for k in range(4):
        wx, wy = P(112 + k * 9, GY - 10); r.fixed(wx, wy, (210, 176, 110))
    for x in range(60, 176, 3): r.fixed(*P(x, GY - 7), SHIP_H[4])                             # the rail
    for k in range(5):
        x0 = 80 + k * 20; ln = 10 + h32(k, 9) % 16
        r.stroke([P(x0 + math.sin(j * 0.5 + k) * 1.5, GY + 15 + j) for j in range(ln)], 1.0, MN, v=0.28, group='tendril2')
    im = r.render()
    px_ = im.load()
    for (sx, sy) in ((74, 38), (98, 30), (126, 46), (148, 34), (112, 62), (164, 56), (86, 58), (58, 50), (184, 44), (138, 22)):
        sx, sy = (int(v) for v in P(sx, sy))
        if px_[sx, sy][3]:                                                                   # spore lights in the net
            px_[sx, sy] = (150, 236, 150, 255)
    return im
SHIP = skyship_img()
SHIP_AT = (318, 52)                                                                         # its top-left on the canvas
def post(col, cls):
    sp = SHIP.load(); w, h = SHIP.size
    for j in range(h):
        for i in range(w):
            c = sp[i, j]
            if c[3] < 128: continue
            x, y = SHIP_AT[0] + i, SHIP_AT[1] + j
            if not (0 <= x < W and 0 <= y < H) or cls[y][x] != 'sky': continue
            bg = col[y][x]
            k = 0.42 if c[:3] not in ((150, 236, 150), (210, 176, 110)) else 0.2              # the air between: lights stay brighter
            col[y][x] = tuple(int(c[q] + (bg[q] - c[q]) * k) for q in range(3))

# ---------------------------------------------------------------------------------------------------- render
KEY = [[None] * W for _ in range(H)]
for y in range(H):
    for x in range(W):
        g = rs.G[y][x]
        if g is None or g[1] not in KEYOBJ or g[4] is None: continue
        part, along_z = KEYOBJ[g[1]]
        X, Y, Z = g[4]
        if abs(X) < 15: continue
        for (Xf, z0, z1, *_r) in LEFT + RIGHT:
            if abs(abs(X) - abs(Xf)) < 0.05 and z0 <= Z <= z1 and (X < 0) == (Xf < 0):
                if part(Z - z0, Y) in ('plaster', 'rust') and Y < 24 and wn(2, Z * 0.2 + 50, Y * 0.2) > 0.5: KEY[y][x] = 'stucco'
                break
img = rs.render(INK, fog=fog_of, post=post, mirror=lambda x, y, wp: 0.82 * puddle(wp[0], wp[2]),
                light_gain=1.0, grime_gain=1.15, bloom=0.35, stain_gain=1.0,
                key=KEY, peel={'stucco': BRICK}, crack=('stucco',), damp_gain=0.45)
img.save(f'{OUT}/townsquare.png')
print('done townsquare')
