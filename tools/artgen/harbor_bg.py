"""The Harbor (HarborScene), 1067x600, overcast day, the shared camera (raster3d.py via waterkit.WRaster).
After the old art (Harbor.png): where the city meets the Yolk Sea. A plank pier runs across the whole front (the walk
line, z 15); on the left a stone quay carries a ramshackle two-storey timber harbour house with a lean-to annex and a
porch, and in front of it a timber derrick crane -- an A-frame mast, a lattice jib reaching up to the right, the hook
hanging on its chain. The water is the Yolk Sea: thick, muted amber, holding the light more than reflecting it, slow
swells and oil slicks, fading into a fog bank; it mirrors the pier, the piles, the boats and the lamp post. On the right
a short jetty runs out on piles to the lamp post at the dock's end (a cage lantern, lit dim); further out a boathouse on
stilts and the stumps of an older pier; seed-shaped boats far off; the city's chimneys in the haze on the left. A rowboat
is moored at the pier's edge. No people (the Heir and Torchere are the scene's sprites), no mushrooms.

    python3 harbor_bg.py <outdir>   ->  harbor.png (assets/images/backgrounds/Harbor.png)
                                        oilcan.png (assets/images/props/harbor_oilcan.png -- the Oil pickup's world sprite,
                                        drawn into the scene and cut out of a second render; prints where it goes)
Fixed points (canvas): the pier's far edge y ~467 (z 21); the walk line y 534; see the numbers it prints."""
import sys, math
from PIL import Image
from common import h32, ramp, make_noise
from shedkit import *
from waterkit import WRaster, timber, ironround, roundlit, ALGAE, SILT

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = WRaster()
WL = -1.3                                                                          # the sea's surface (the pier is Y 0)
DE = 21.0                                                                          # the pier's far edge
QX = -6.0                                                                          # the quay's water side
DECK = ramp('#15130f #1f1c16 #2a261e #363127 #433d31 #514a3c #615849 #736957 #857964')   # weathered grey-brown boards
YOLK = ramp('#2a2412 #373016 #463c1b #554820 #655525 #75622b #867032 #977f3b')     # the Yolk Sea, muted
GRAN = ramp('#151816 #1d211e #262b27 #303631 #3b423c #474f48 #555d55 #656c63 #757b71')   # quay granite
TAR = ramp('#121212 #1a1a19 #232321 #2d2c29 #383632 #44413b #514d45')              # tar-paper roofs
BRICK = ramp('#2a1612 #3a1f18 #4c2a20 #5e3628 #704333')
IRON = ramp('#121210 #1b1a17 #25231f #302d28 #3c3832 #4a453d #5a5449')            # old dark iron
FOGSKY = ramp('#18221f #1e2a27 #25322e #2c3a35 #34433c #3d4c44 #46554c #506055 #5b6a5e #677466 #727d6e')
WARMFOG = (104, 104, 82)

# ---------------------------------------------------------------------------------------------------- sky, sea
_c1, _c2 = make_noise(13, 61, W, H), make_noise(47, 62, W, H)
def harbor_sky(x, y, s=0, t=0, z=0, wp=None):
    """low overcast over a fog bank: heavy cloud overhead, long soft bands, the fog over the sea faintly warm from below"""
    tt = max(0.0, min(1.0, y / HY))
    v = 3.0 + 6.6 * tt ** 1.5 + (_c2(x * 0.5, y * 2.8) - 0.5) * 2.2 + (_c1(x * 0.5, y * 2.4) - 0.5) * 0.7
    c = tone(FOGSKY, v, x, y)
    if tt > 0.72: c = mix(c, WARMFOG, ((tt - 0.72) / 0.28) ** 2 * 0.32)
    return c
rs.quad((-1400, 800, 600), (1400, 800, 600), (-1400, -300, 600), harbor_sky, cls='sky')

def yolk(x, y, s, t, z, wp):
    """thick standing yellow: long slow swells, crests catching the sky in short dashes, oil in thin rainbow skins"""
    X, _, Z = wp
    near = min(1.0, 26.0 / Z)
    ph = Z * 0.5 + X * 0.03 + wn(0, X * 0.03, Z * 0.06) * 6.0
    v = 3.9 + 0.8 * math.sin(ph) * near + (wn(1, X * 0.12, Z * 0.5) - 0.5) * 1.0 + (1 - near) * 0.9
    P = 0.5 + Z * 0.018                                                            # glints: thin dashes along the crests
    th = Z * Z / (F * (CAMH - WL)) / P
    if (Z / P) % 1 < th * 1.1 and math.sin(ph) > 0.2 and h32(int(X / (1.4 + Z * 0.05)), int(Z / P), 3) % 4 == 0:
        v += 1.7
    elif (Z / P + 0.5) % 1 < th and math.sin(ph) < -0.4 and h32(int(X / (2.0 + Z * 0.05)), int(Z / P), 4) % 3 == 0:
        v -= 1.2                                                                   # troughs
    c = tone(YOLK, v, x, y)
    m = wn(3, X * 0.35, Z * 1.1)                                                   # oil: thin skins near the pier
    if Z < 50 and 0.6 < m < 0.66:
        c = mix(c, [MAUVE[4], TEAL[5], OCHRE[4]][int(m * 300) % 3], 0.3 * near)
    return fogged(c, z)
def yolk_mirror(X, Z):
    return 0.34 + 0.34 * (1 - min(1.0, 26.0 / Z))                                 # thick: it holds light as much as it mirrors
rs.water(WL, -1400, 1400, 3, 590, yolk, strength=yolk_mirror, wobble=1.2)

# ---------------------------------------------------------------------------------------------------- far: city, boats, old piles
for k, (X, hh, Z) in enumerate(((-260, 40, 330), (-215, 26, 300), (-170, 54, 360), (-125, 22, 320), (-300, 30, 340), (-84, 14, 280))):
    # the city across the water: warehouse blocks with rows of windows, in the haze
    rs.box(X - 18, X + 18, WL, hh, Z, Z + 30, windows_sh(concrete(3.0, STONE if k % 2 else STUCCO), cols=4.0, rows=5.0, lit=0.05, seed=k),
           concrete(2.4, STONE), cls='wall')
for (X, hh, Z) in ((-236, 70, 320), (-190, 84, 350), (-150, 58, 310)):                # factory chimneys in the haze
    rs.quad((X - 2.4, WL, Z), (X + 2.4, WL, Z), (X - 2.0, hh, Z), lambda x, y, s, t, z, wp: HAZE[3] if t < 0.95 else HAZE[2], cls='wall')
def seedboat(X, Z, L):
    """a boat like a seed: a lens of a hull, a stub of a mast"""
    def hull(x, y, s, t, z, wp):
        u = (s - 0.5) * 2
        if t > 0.2 + 0.8 * (1 - u * u): return None
        return fogged(WOOD[1] if t < 0.5 else WOOD[3], z)
    rs.quad((X - L / 2, WL - 0.2, Z), (X + L / 2, WL - 0.2, Z), (X - L / 2, WL + L * 0.2, Z), hull, cls='prop', cut=True)
    rs.beam((X + L * 0.08, WL + L * 0.12, Z), (X + L * 0.12, WL + L * 0.6, Z), 0.3, lambda x, y, s, t, z, wp: fogged(WOOD[1], z))
for (X, Z, L) in ((-34, 150, 7.0), (40, 210, 8.0), (10, 118, 5.5), (-80, 240, 9.0), (88, 170, 6.0)):
    seedboat(X, Z, L)
OLDPIER = []                                                                       # stumps of an older pier, out in the water
for i in range(22):
    X = 6 + (i % 11) * 5.2 + (h32(i, 1) % 5) * 0.4 - 1.0; Z = 50 + (i // 11) * 5.5 + (h32(i, 2) % 5) * 0.5
    if h32(i, 3) % 5 == 0: continue
    hh = WL + 0.6 + (h32(i, 4) % 11) * 0.4
    lean = ((h32(i, 5) % 7) - 3) * 0.12
    OLDPIER.append((X, Z, hh))
    rs.beam((X, WL - 2, Z), (X + lean, hh, Z), 0.7 + (h32(i, 6) % 3) * 0.1, timber(2.0, WOOD, algae=lambda wp: 1.0 if wp[1] < WL + 0.7 else 0.0, seed=i))
for a, b in zip(OLDPIER[:6], OLDPIER[1:7]):                                        # a crossbeam still hanging on
    if abs(a[1] - b[1]) < 1.5 and h32(int(a[0]), 9) % 2:
        rs.beam((a[0], min(a[2], b[2]) - 0.4, a[1]), (b[0], min(a[2], b[2]) - 0.9, b[1]), 0.45, timber(1.8, WOOD, seed=int(a[0])))

# ---------------------------------------------------------------------------------------------------- the boathouse on stilts (far right)
BH = (64.0, 90.0, 56.0, 68.0)
def bh_wall(x, y, s, t, z, wp):
    X, Y, Z = wp
    if 0.36 < s < 0.62 and Y < 4.6: return fogged(STONE[0], z)                    # the boat door, open on darkness
    if 0.12 < s < 0.24 and 4.6 < Y < 6.4: return fogged(GLOW[0] if (x + y) % 4 else GLOW[1], z, 0.6)   # one dim window
    return planks(2.6, WOOD, seed=21)(x, y, s, t, z, wp)
rs.box(BH[0], BH[1], 1.0, 8.4, BH[2], BH[3], bh_wall, planks_z(2.0, WOOD, seed=22), cls='wall')
rs.quad((BH[0] - 1, 8.2, BH[2] - 1.2), (BH[1] + 1, 8.2, BH[2] - 1.2), (BH[0] - 1, 13.0, (BH[2] + BH[3]) / 2),
        lambda x, y, s, t, z, wp: fogged(tone(TAR, 2.8 + (0.7 if (t * 9) % 1 < 0.2 else 0), x, y), z), cls='wall')
rs.quad((BH[0], 0.7, BH[2] - 2.4), (BH[1], 0.7, BH[2] - 2.4), (BH[0], 1.0, BH[2]),
        lambda x, y, s, t, z, wp: fogged(tone(DECK, 3.2, x, y), z), cls='prop')     # its landing stage
for i in range(7):
    X = BH[0] + 0.6 + i * (BH[1] - BH[0] - 1.2) / 6
    rs.beam((X, WL - 2, BH[2] - 2.2), (X, 0.9, BH[2] - 2.2), 0.65, timber(1.8, WOOD, algae=lambda wp: 1.0 if wp[1] < WL + 0.6 else 0.0, seed=i + 40))

# ---------------------------------------------------------------------------------------------------- the pier (the walk line)
def puddle(X, Z):
    return 0.0                                                                     # (no puddles: the water runs off between the boards)
    if Z > DE - 0.6: return 0.0
    m = wn(2, X * 0.55 + 5.0, Z * 0.9) + (wn(3, X * 2.4, Z * 2.4) - 0.5) * 0.14
    return max(0.0, min(1.0, (m - 0.8) * 12))
def boards(x, y, s, t, z, wp, edge=DE):
    """grey weathered boards along the depth, staggered butt joints and nails, dark gaps (the sea glints under them near
    the camera), a few boards missing or patched, slime greening toward the water's edge"""
    X, _, Z = wp
    w = 0.78; pl = math.floor(X / w); fu = X / w - pl
    off = (h32(pl, 5) % 60) / 10.0
    seg = math.floor((Z + off) / 6.0); fz = (Z + off) / 6.0 - seg
    hb = h32(pl, seg, 1)
    gap = 0.9 * z / F / w + 0.035
    if hb % 53 == 0 and Z < edge - 1:                                              # a missing board: the sea below
        return fogged(tone(YOLK, 1.4 + (1.0 if (x * 3 + y) % 7 == 0 else 0), x, y) if fu > gap + 0.1 else DECK[0], z)
    v = 3.9 + (hb % 4) * 0.32 - 1.0 * (wn(0, X * 0.4, Z * 0.2) - 0.5) + (wn(1, X * 3.0, Z * 0.35) - 0.5) * 1.0
    r = DECK
    if hb % 37 == 1: r = WOOD; v += 1.2                                            # a newer, browner patch board
    if fu < gap:
        return fogged(tone(YOLK, 1.2, x, y) if Z < 15 and (x + y) % 3 == 0 else DECK[0], z)
    if fz < 1.0 * Z * Z / (F * CAMH) / 6.0 + 0.004: v -= 1.7                      # butt joint
    if (fz < 0.03 or fz > 0.97) and (abs(fu - 0.25) < 0.06 or abs(fu - 0.75) < 0.06) and Z < 30: v += 1.6   # nails
    if fu < gap + 0.07: v -= 0.7
    if fu > 0.9: v += 0.5                                                          # the lit edge of each board
    v += max(0.0, (Z - 13.0) / 8.0) * 0.6 - max(0.0, (abs(X) - 9.0) / 12.0) * max(0.0, (17.0 - Z) / 5.0) * 0.7   # wet sheen far off, darker near corners
    c = tone(r, v, x, y)
    g = max(0.0, (Z - (edge - 3.0)) / 3.0) * (0.6 + 0.6 * wn(2, X * 0.8, Z * 0.8))
    if g > 0.35: c = mix(c, tone(ALGAE, v - 0.5, x, y), min(0.75, (g - 0.35) * 1.5))
    p_ = puddle(X, Z)
    if p_: c = mix(c, (24, 26, 20), p_ * 0.4)
    return fogged(c, z)
rs.quad((QX, 0, 3), (90, 0, 3), (QX, 0, DE), boards, cls='ground')
rs.quad((-90, 0, 3), (QX, 0, 3), (-90, 0, DE), boards, cls='ground')
rs.beam((QX + 0.2, 0.1, DE - 0.15), (90, 0.1, DE - 0.15), 0.34, timber(2.8, DECK, algae=lambda wp: 0.3))    # the capping log
# the jetty out to the lamp post
JX0, JX1, JZ1 = 25.0, 36.0, 27.0
rs.quad((JX0, 0, DE), (JX1, 0, DE), (JX0, 0, JZ1), lambda x, y, s, t, z, wp: boards(x, y, s, t, z, wp, edge=JZ1), cls='ground')
rs.quad((JX0, -0.5, DE), (JX0, -0.5, JZ1), (JX0, 0.0, DE), lambda x, y, s, t, z, wp: fogged(tone(DECK, 2.4 + t, x, y), z), cls='prop')  # its fascia
pile_algae = lambda wp: 1.0 if wp[1] < WL + 0.55 else (0.5 if wp[1] < WL + 0.9 else 0.0)
for i, Z in enumerate((DE + 1.4, DE + 3.4, JZ1 - 0.3)):
    rs.beam((JX0 + 0.35, WL - 3, Z), (JX0 + 0.35, -0.45, Z), 0.66, timber(2.2, WOOD, algae=pile_algae, seed=i))
    if i < 2:                                                                      # cross braces under the deck
        rs.beam((JX0 + 0.3, WL + 0.15, Z), (JX0 + 0.3, -0.5, Z + 1.9), 0.3, timber(1.6, WOOD, algae=pile_algae, seed=i + 9))
for i, X in enumerate((JX0 + 3.6, JX0 + 7.4, JX1 - 0.4)):
    rs.beam((X, WL - 3, JZ1 - 0.3), (X, -0.45, JZ1 - 0.3), 0.66, timber(2.0, WOOD, algae=pile_algae, seed=i + 20))
rs.quad((JX0, -0.5, JZ1), (JX1, -0.5, JZ1), (JX0, 0.0, JZ1), lambda x, y, s, t, z, wp: fogged(tone(DECK, 2.0 + t, x, y), z), cls='prop')
# mooring posts along the pier's edge, rope round some of them
for i, (X, Z, hh) in enumerate(((-3.0, DE - 0.4, 1.5), (2.4, DE - 0.4, 1.9), (13.2, DE - 0.4, 1.4), (20.6, DE - 0.4, 1.8), (JX1 - 0.9, JZ1 - 0.7, 2.3))):
    rs.beam((X, -0.2, Z), (X, hh, Z), 0.66, timber(3.0, WOOD, seed=i * 3))
    rs.disc(X, hh, Z, 0.33, lambda x, y, a, b, z, wp: fogged(tone(DECK, 4.8 - b * 1.5 - a * 0.5, x, y), z), cls='prop')
    if i in (1, 3, 4):
        for k in range(3):
            rs.beam((X - 0.38, hh - 0.5 - k * 0.15, Z - 0.3), (X + 0.38, hh - 0.45 - k * 0.15, Z - 0.3), 0.14,
                    lambda x, y, s, t, z, wp: fogged(tone(OCHRE, 3.4 - t, x, y), z))

# ---------------------------------------------------------------------------------------------------- the rowboat at the pier
BX0, BX1, BZ0, BZ1 = 1.6, 11.8, 24.4, 27.6
def hull_w(s):                                                                     # half-beam along the hull: a pointed bow (right)
    return 0.5 * (1 - max(0.0, (s - 0.62) / 0.38) ** 1.7) * (1 - max(0.0, (0.06 - s) / 0.06) ** 2 * 0.25)
def boat_side(x, y, s, t, z, wp):
    bottom = (max(0.0, (s - 0.74) / 0.26) ** 2) * 0.95 + (max(0.0, (0.07 - s) / 0.07) ** 2) * 0.4   # the keel rises to bow and stern
    if t < bottom: return None
    v = 2.6 + (1.4 if t > 0.84 else 0) + (0.5 if int(t * 5) % 2 else 0) + 1.6 * (s - 0.5) * 0.3
    c = tone(TEAL, v, x, y)
    if wn(1, wp[0] * 1.6, wp[1] * 3) > 0.62: c = tone(WOOD, v + 0.4, x, y)          # paint gone to bare wood
    if t < 0.32: c = mix(c, tone(ALGAE, 2.4, x, y), 0.65)
    return fogged(c, z)
rs.quad((BX0, WL - 0.25, BZ0 + 0.3), (BX1, WL - 0.25, BZ0 + 0.3), (BX0, WL + 0.85, BZ0 + 0.3), boat_side, cls='prop', cut=True)
def boat_in(x, y, s, t, z, wp):
    hw = hull_w(s)
    if abs(t - 0.5) > hw: return None
    if abs(t - 0.5) > hw - 0.08: return fogged(tone(TEAL, 3.8 - (t - 0.5) * 2, x, y), z)     # the gunwale
    if abs(s - 0.45) < 0.03 or abs(s - 0.18) < 0.028: return fogged(tone(WOOD, 4.4, x, y), z)  # thwarts
    if abs(t - 0.5) < 0.14 and 0.5 < s < 0.68: return fogged(tone(YOLK, 3.0, x, y), z)       # bilge, yolky
    return fogged(tone(WOOD, 2.2 + (0.6 if int(s * 26) % 2 else 0), x, y), z)
rs.quad((BX0, WL + 0.82, BZ0), (BX1, WL + 0.82, BZ0), (BX0, WL + 0.82, BZ1), boat_in, cls='prop', cut=True)
rs.beam((BX0 + 2.4, WL + 0.95, BZ0 + 1.0), (BX0 + 6.4, WL + 1.05, BZ0 + 2.3), 0.16, lambda x, y, s, t, z, wp: fogged(tone(WOOD, 4.0 - t, x, y), z))   # an oar
rs.beam((BX1 - 0.6, WL + 0.9, (BZ0 + BZ1) / 2), (13.2, 1.0, DE - 0.4), 0.07, lambda x, y, s, t, z, wp: fogged(OCHRE[1], z))            # the painter

# ---------------------------------------------------------------------------------------------------- the stone quay (left)
def quay_top(x, y, s, t, z, wp):
    X, _, Z = wp
    row = math.floor(Z / 2.0); colw = 2.4 + (h32(row, 3) % 3) * 0.4
    col = math.floor(X / colw + row * 0.41)
    fx = (X / colw + row * 0.41) - col; fz = Z / 2.0 - row
    v = 4.0 + (h32(col, row, 4) % 3) * 0.4 + (wn(0, X * 1.2, Z * 1.2) - 0.5) * 0.9
    if fx < 0.9 * z / F / colw + 0.02 or fz < 1.1 * z * z / (F * CAMH) / 2.0 + 0.02:
        return fogged(tone(ALGAE, 1.6, x, y), z)
    c = tone(GRAN, v, x, y)
    if wn(3, X * 0.4, Z * 0.4) > 0.6: c = mix(c, tone(SILT, 3.4, x, y), 0.4)
    return fogged(c, z)
rs.quad((-140, 0, DE), (QX, 0, DE), (-140, 0, 80), quay_top, cls='ground')
def quay_side(x, y, s, t, z, wp):
    X, Y, Z = wp
    row = math.floor((Y - WL + 4) / 0.75); bl = 1.6 + (h32(row, 7) % 3) * 0.3
    fb = ((Z + row * 0.7) / bl) % 1; fv = ((Y - WL + 4) / 0.75) % 1
    v = 3.6 + (h32(row, int((Z + row * 0.7) / bl), 8) % 3) * 0.35
    if fb < 0.06 or fv < 0.1: v = 1.6
    c = tone(GRAN, v, x, y)
    if Y < WL + 0.7 + 0.3 * wn(1, Z * 1.5, 2.0): c = tone(ALGAE, v - 0.2, x, y)    # slime at the waterline
    elif wn(2, Z * 2.0, Y * 0.4) > 0.66: c = mix(c, (40, 26, 16), 0.45)           # rust runs from the iron rings
    return fogged(c, z)
rs.quad((QX, WL - 1.5, DE), (QX, WL - 1.5, 80), (QX, 0.0, DE), quay_side, cls='wall')
rs.beam((QX + 0.15, 0.06, DE), (QX + 0.15, 0.06, 64), 0.3, ironround(2.8, STONE, rust=0.35))                # the quay's iron edge
for Z in (25.0, 31.0, 39.0):                                                       # mooring rings in the quay wall
    for k in range(10):
        a0, a1 = math.pi * 2 * k / 10, math.pi * 2 * (k + 1) / 10
        rs.beam((QX + 0.1, -0.7 + 0.35 * math.sin(a0), Z + 0.35 * math.cos(a0)), (QX + 0.1, -0.7 + 0.35 * math.sin(a1), Z + 0.35 * math.cos(a1)),
                0.12, lambda x, y, s, t, z, wp: fogged(RUSTY[3], z))

# ---------------------------------------------------------------------------------------------------- the harbour house
HX0, HX1, HZ0, HZ1, HY1, HRIDGE = -55.0, -15.0, 30.5, 41.5, 12.4, 21.5
WINDOWS = [(-50.5, -46.6, 2.2, 5.4, 'boarded'), (-41.5, -37.6, 2.2, 5.4, 'lit'),
           (-50.0, -46.6, 8.0, 10.8, 'glass'), (-41.0, -37.6, 8.0, 10.8, 'broken'), (-31.8, -28.4, 8.0, 10.8, 'glass'), (-23.0, -19.6, 8.0, 10.8, 'curtain')]
DOOR = (-30.6, -26.6, 6.6)
def house_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    if DOOR[0] < X < DOOR[1] and Y < DOOR[2]:
        if Y > DOOR[2] - 0.3 or X < DOOR[0] + 0.25 or X > DOOR[1] - 0.25: return fogged(WOOD[0], z)
        v = 2.0 + (0.6 if int((X - DOOR[0]) / 0.55) % 2 else 0)
        if abs(Y - 3.3) < 0.18 and X > DOOR[1] - 0.9: v = 4.4
        return fogged(tone(WARM, v, x, y), z)
    for (wx0, wx1, wy0, wy1, kind) in WINDOWS:
        if wx0 - 0.3 < X < wx1 + 0.3 and wy0 - 0.38 < Y < wy0: return fogged(tone(WOOD, 4.2, x, y), z)        # sill
        if wx0 - 0.25 < X < wx1 + 0.25 and wy1 < Y < wy1 + 0.32: return fogged(tone(WOOD, 1.6, x, y), z)       # lintel
        if wx0 < X < wx1 and wy0 < Y < wy1:
            u, v_ = (X - wx0) / (wx1 - wx0), (Y - wy0) / (wy1 - wy0)
            px = z / F
            if abs(u - 0.5) < max(0.05, px / (wx1 - wx0) * 0.7) or abs(v_ - 0.5) < max(0.05, px / (wy1 - wy0) * 0.7): return fogged(WOOD[1], z)
            if kind == 'lit': return GLOW[1] if (x + y) % 3 else GLOW[0]
            if kind == 'boarded':
                if abs(u - v_) < 0.1 or (v_ * 3) % 1 < 0.62: return fogged(tone(WOOD, 3.4 - (0.9 if (v_ * 3) % 1 < 0.1 else 0), x, y), z)
            if kind == 'broken' and abs(math.sin(u * 19) * 0.25 + 0.45 - v_) > 0.14 and u > 0.5: return fogged(STONE[0], z)
            if kind == 'curtain' and v_ > 0.25: return fogged(mix(OCHRE[2], (0, 0, 0), 0.2 + 0.2 * ((u * 7) % 1 < 0.3)), z)
            return fogged(tone(FOGSKY, 3.0 + v_ * 3.6 + (1.2 if (u + v_ * 0.5) % 0.8 < 0.07 else 0), x, y), z, 0.8)
    if abs(Y - 6.9) < 0.2: return fogged(tone(WOOD, 1.4, x, y), z)                # the floor band
    return planks(3.1, WOOD, w=0.7, seed=31)(x, y, s, t, z, wp)
def house_side(x, y, s, t, z, wp):
    X, Y, Z = wp
    if 34.0 < Z < 37.0 and 8.0 < Y < 10.8:                                         # a gable-side window
        if abs(Z - 35.5) < 0.12 or abs(Y - 9.4) < 0.12: return fogged(WOOD[1], z)
        return fogged(tone(FOGSKY, 3.4 + (Y - 8) * 1.0, x, y), z, 0.8)
    return planks_z(2.3, WOOD, w=0.7, seed=32)(x, y, s, t, z, wp)
rs.box(HX0, HX1, 0, HY1, HZ0, HZ1, house_front, house_side, cls='wall')
ZM = (HZ0 + HZ1) / 2
def roof(x, y, s, t, z, wp):
    """tar paper over boards, in courses, patched, a green streak or two"""
    X, Y, Z = wp
    course = math.floor(t * 11); fc = (t * 11) % 1
    v = 3.0 + (0.8 if fc < 0.12 else 0) + (wn(0, X * 0.5, Z * 0.5) - 0.5) * 0.7 - 0.4 * (1 - t)
    sheet = math.floor((X + course * 1.7) / 3.4)
    hk = h32(sheet, course, 5)
    if hk % 9 == 0: v += 0.6                                                       # a newer patch of tar paper
    elif hk % 9 == 1: v -= 0.5
    if abs(((X + course * 1.7) / 3.4) % 1) < 0.03: v -= 0.6                        # sheet seams
    c = tone(TAR, v, x, y)
    if hk % 23 == 2 and 0.2 < fc < 0.9: c = tone(WOOD, 2.6 + fc, x, y)            # torn: the boards show
    if t < 0.12 and wn(3, X * 1.6, 3.0) > 0.55: c = mix(c, tone(ALGAE, 3.0, x, y), 0.55)   # slime along the eaves
    return fogged(c, z)
rs.quad((HX0 - 1.0, HY1 - 0.3, HZ0 - 1.6), (HX1 + 1.2, HY1 - 0.3, HZ0 - 1.6), (HX0 - 1.0, HRIDGE, ZM), roof, cls='wall')
rs.beam((HX0 - 1.0, HRIDGE + 0.05, ZM), (HX1 + 1.2, HRIDGE + 0.05, ZM), 0.4, timber(2.2, TAR))                  # the ridge
def gable(x, y, s, t, z, wp):
    X, Y, Z = wp
    half = (HRIDGE - HY1 + 0.3) * (1 - abs(Z - ZM) / (ZM - HZ0 + 1.6))
    if Y - HY1 + 0.3 > half: return None
    if Y - HY1 + 0.3 > half - 0.35: return fogged(tone(WOOD, 4.2, x, y), z)       # the barge board
    if abs(Z - ZM) < 1.1 and 15.0 < Y < 17.4:                                      # a loft hatch
        return fogged(tone(WOOD, 1.6 + (0.7 if int((Z - ZM) * 3) % 2 else 0), x, y), z)
    return planks(2.6, WOOD, w=0.7, seed=33)(x, y, s, t, z, wp)
rs.quad((HX1 + 0.01, HY1 - 0.3, HZ0 - 1.6), (HX1 + 0.01, HY1 - 0.3, HZ1 + 1.6), (HX1 + 0.01, HRIDGE + 0.5, HZ0 - 1.6), gable, cls='wall', cut=True)
CHIM = (-46.0, -43.4, 17.0, 25.0, 34.0, 36.4)
rs.box(CHIM[0], CHIM[1], CHIM[2], CHIM[3], CHIM[4], CHIM[5],
       lambda x, y, s, t, z, wp: fogged(tone(BRICK, 2.8 + (0.6 if int(wp[1] * 3.5) % 2 else 0) - (1.2 if (wp[0] * 2.5 + int(wp[1] * 3.5) * 0.5) % 1 < 0.12 else 0), x, y), z),
       lambda x, y, s, t, z, wp: fogged(tone(BRICK, 1.6, x, y), z), cls='wall')   # the chimney
rs.box(CHIM[0] - 0.3, CHIM[1] + 0.3, CHIM[3], CHIM[3] + 0.4, CHIM[4] - 0.3, CHIM[5] + 0.3, lambda x, y, s, t, z, wp: fogged(tone(STONE, 3.4, x, y), z),
       lambda x, y, s, t, z, wp: fogged(STONE[2], z), cls='prop')
# the lamp over the door
rs.beam((-28.6, 7.8, HZ0 - 0.05), (-28.6, 7.8, HZ0 - 0.9), 0.12, ironround(2.0, METAL, rust=0.8))
rs.disc(-28.6, 7.3, HZ0 - 0.9, 0.36, lambda x, y, a, b, z, wp: GLOW[3] if a * a + b * b < 0.35 else GLOW[1], cls='emit')
# the annex (left) with a lean-to roof
def annex(x, y, s, t, z, wp):
    X, Y, Z = wp
    if -76.0 < X < -70.0 and Y < 5.4:                                              # a wide shed door, ajar
        return fogged(STONE[0] if X > -73.5 else tone(WOOD, 2.0 + (0.6 if int(X * 2) % 2 else 0), x, y), z)
    return planks(2.7, WOOD, w=0.7, seed=34)(x, y, s, t, z, wp)
rs.box(-96.0, HX0, 0, 8.4, HZ0 - 1.0, HZ1 - 1.0, annex, planks_z(2.0, WOOD, seed=35), cls='wall')
rs.quad((-97.0, 8.2, HZ0 - 2.2), (HX0 + 0.2, 8.2, HZ0 - 2.2), (-97.0, 11.6, HZ1 - 2.0), roof, cls='wall')
# the porch on the right: a lean-to on two posts
rs.quad((HX1, 8.6, HZ0 - 0.4), (HX1 + 6.2, 7.2, HZ0 - 0.4), (HX1, 8.6, HZ1 - 1.6), roof, cls='wall')
for Z in (HZ0, HZ1 - 2.2):
    rs.beam((HX1 + 5.8, 0, Z), (HX1 + 5.8, 7.3, Z), 0.42, timber(2.8, WOOD, seed=int(Z)))
rs.beam((HX1 + 5.8, 7.2, HZ0), (HX1 + 5.8, 7.2, HZ1 - 2.2), 0.32, timber(2.4, WOOD))
# clutter on the quay: barrels, crates, eel traps, a net drying, a coil of rope, an anchor
def barrel(X, Z, h=2.2, r=0.85, seed=0):
    def sh(x, y, s, t, z, wp):
        Y = wp[1]
        v = 3.0 + 2.2 * (roundlit(t) - 0.5)
        if abs((Y % (h / 3)) - 0.12) < 0.1: return fogged(tone(IRON, v + 0.4, x, y) if wn(2, Y * 3, t * 3 + seed) > 0.4 else tone(RUSTY, v - 0.4, x, y), z)    # hoops
        return fogged(tone(WOOD, v + (wn(1, Y * 4, seed) - 0.5), x, y), z)
    rs.beam((X, 0, Z), (X, h, Z), r * 2, sh)
    rs.disc(X, h, Z - 0.05, r * 0.98, lambda x, y, a, b, z, wp: fogged(tone(WOOD, 4.0 - b - (0.8 if abs(a) > 0.85 else 0), x, y), z) if b > -0.45 else None)
barrel(-13.6, 28.0, seed=1); barrel(-11.8, 29.2, seed=2); barrel(-9.2, 24.6, h=2.0, seed=3)
def crate(X0, X1, Y0, Y1, Z0, Z1, seed):
    rs.box(X0, X1, Y0, Y1, Z0, Z1, planks(3.2, WARM, w=0.5, seed=seed), planks(2.4, WARM, w=0.5, seed=seed + 1),
           top=planks(3.8, WARM, w=0.5, vertical=False, seed=seed + 2), cls='prop')
crate(-19.0, -16.4, 0, 2.3, 26.2, 28.6, 40); crate(-18.6, -16.8, 2.3, 3.9, 26.6, 28.2, 43); crate(-22.2, -19.8, 0, 1.8, 27.6, 29.6, 46)
def trap(x, y, s, t, z, wp):
    if (s * 7) % 1 < 0.24 or (t * 4) % 1 < 0.26: return fogged(tone(OCHRE, 2.8 + t, x, y), z)
    return None
for (X, Y0) in ((-10.0, 0.0), (-8.4, 0.0), (-9.2, 1.2)):
    rs.quad((X - 0.75, Y0, 22.8), (X + 0.75, Y0, 22.8), (X - 0.75, Y0 + 1.15, 22.8), trap, cls='prop', cut=True)
def net(x, y, s, t, z, wp):
    sagv = 0.25 * math.sin(s * math.pi)
    if t > 0.96 - sagv * 0.2: return fogged(tone(WOOD, 2, x, y), z)
    if t < 0.15 + sagv: return None
    if (s * 26 + t * 6) % 1 < 0.3 or (s * 26 - t * 6) % 1 < 0.3: return fogged(tone(STONE, 3.6 + t, x, y), z)
    return None
rs.quad((-53.0, 1.0, HZ0 - 0.4), (-43.0, 1.0, HZ0 - 0.4), (-53.0, 6.6, HZ0 - 0.4), net, cls='prop', cut=True)
for X in (-53.0, -43.0):
    rs.beam((X, 0, HZ0 - 0.45), (X, 6.8, HZ0 - 0.45), 0.24, timber(2.6, WOOD))
for k in range(5):                                                                 # a coil of rope on the planks
    r = 0.5 + k * 0.12
    for j in range(14):
        a0, a1 = math.pi * 2 * j / 14, math.pi * 2 * (j + 1) / 14
        rs.beam((-21.5 + r * math.cos(a0), 0.08 + k * 0.03, 19.4 + r * math.sin(a0) * 0.9),
                (-21.5 + r * math.cos(a1), 0.08 + k * 0.03, 19.4 + r * math.sin(a1) * 0.9), 0.15,
                lambda x, y, s, t, z, wp: fogged(tone(OCHRE, 3.2 - t * 0.8, x, y), z))
anc = ironround(2.2, METAL, rust=0.95, seed=7)                                     # an old anchor leaning on the annex
rs.beam((-64.0, 0.2, HZ0 - 1.6), (-63.2, 5.0, HZ0 - 1.4), 0.4, anc)
rs.beam((-65.6, 1.2, HZ0 - 1.6), (-62.6, 0.6, HZ0 - 1.6), 0.35, anc)
rs.beam((-65.6, 1.2, HZ0 - 1.6), (-66.0, 2.0, HZ0 - 1.6), 0.3, anc, cap=True)
rs.beam((-62.6, 0.6, HZ0 - 1.6), (-62.0, 1.4, HZ0 - 1.6), 0.3, anc, cap=True)

# ---------------------------------------------------------------------------------------------------- the crane
CZ = 25.0
rs.box(-42.5, -28.0, 0, 0.9, CZ - 2.2, CZ + 4.2, planks(3.2, WOOD, w=0.6, seed=50), planks_z(2.4, WOOD, seed=51),
       top=planks(3.6, WOOD, w=0.6, vertical=False, seed=52), cls='prop')       # its timber bed
APEX = (-35.0, 24.0, CZ + 0.9)
LEGS = [(-41.6, 0.9, CZ - 1.4), (-29.2, 0.9, CZ - 1.4), (-40.8, 0.9, CZ + 3.6), (-30.0, 0.9, CZ + 3.6)]
for i, P in enumerate(LEGS):
    rs.beam(P, APEX, 1.15 if i < 2 else 0.95, timber(3.0 if i < 2 else 2.0, WOOD, seed=i), w1=0.8)
def lerp3(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
TIES = (0.2, 0.42, 0.62, 0.8)
for k, tt in enumerate(TIES):                                                      # ties and X braces across the front legs
    a, b = lerp3(LEGS[0], APEX, tt), lerp3(LEGS[1], APEX, tt)
    rs.beam(a, b, 0.6, timber(2.6, WOOD, seed=10 + k))
    if k < 3:
        a2, b2 = lerp3(LEGS[0], APEX, TIES[k + 1]), lerp3(LEGS[1], APEX, TIES[k + 1])
        rs.beam(a, b2, 0.42, timber(2.2, WOOD, seed=20 + k)); rs.beam(b, a2, 0.42, timber(2.2, WOOD, seed=30 + k))
rs.beam(lerp3(LEGS[0], APEX, 0.04), lerp3(LEGS[1], APEX, 0.04), 0.5, timber(2.2, WOOD))
for k in range(3):                                                                 # iron straps at the apex
    a = lerp3(LEGS[0], APEX, 0.93 + k * 0.02); b = lerp3(LEGS[1], APEX, 0.93 + k * 0.02)
    rs.beam(a, b, 0.2, ironround(2.4, IRON, rust=0.5, seed=k))
# the jib: two chords and the lacing between them, pivoting at the mast's foot
J0, J1 = (-34.0, 2.8, CZ - 1.8), (-17.0, 31.4, CZ - 1.8)
jl = math.hypot(J1[0] - J0[0], J1[1] - J0[1]); nx, ny = -(J1[1] - J0[1]) / jl, (J1[0] - J0[0]) / jl
def off(P, d): return (P[0] + nx * d, P[1] + ny * d, P[2])
A0, A1, B0, B1 = off(J0, 1.0), off(J1, 0.3), off(J0, -1.0), off(J1, -0.3)
rs.beam(A0, A1, 0.7, timber(3.0, WOOD, seed=60), w1=0.5); rs.beam(B0, B1, 0.7, timber(2.4, WOOD, seed=61), w1=0.5)
N = 12
for k in range(N):
    t0, t1 = k / N, (k + 1) / N
    rs.beam(lerp3(A0, A1, t0), lerp3(B0, B1, (t0 + t1) / 2), 0.34, timber(2.2, WOOD, seed=70 + k))
    rs.beam(lerp3(B0, B1, (t0 + t1) / 2), lerp3(A0, A1, t1), 0.34, timber(2.2, WOOD, seed=80 + k))
rs.box(J1[0] - 0.9, J1[0] + 0.9, J1[1] - 0.9, J1[1] + 0.9, CZ - 2.2, CZ - 1.4, steel(3.0, IRON, rust=0.6), steel(2.0, IRON, rust=0.6), cls='prop')   # the sheave head
rope = lambda x, y, s, t, z, wp: fogged(tone(OCHRE, 1.8 - t * 0.6, x, y), z)
rs.beam((APEX[0], APEX[1] + 0.3, APEX[2] - 0.3), (J1[0] - 0.6, J1[1] + 0.2, CZ - 1.8), 0.17, rope)       # the topping lift
rs.beam((APEX[0] + 0.2, APEX[1] - 0.2, APEX[2] - 0.3), (J1[0] - 0.9, J1[1] - 0.5, CZ - 1.8), 0.14, rope)
HOOKX, HOOKY = J1[0] + 0.1, 22.6
chain = lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 2.8 - t + (1.0 if int(s * 70) % 2 else 0), x, y), z)
rs.beam((HOOKX, J1[1] - 0.9, CZ - 1.8), (HOOKX, HOOKY + 2.5, CZ - 1.8), 0.24, chain)
rs.box(HOOKX - 0.7, HOOKX + 0.7, HOOKY + 1.3, HOOKY + 2.6, CZ - 2.2, CZ - 1.5, steel(3.0, IRON, rust=0.6), steel(2.0, IRON, rust=0.6), cls='prop')   # the block
HOOK = [(HOOKX, HOOKY + 1.3), (HOOKX, HOOKY + 0.1)] + [(HOOKX + 0.9 - 0.9 * math.cos(a), HOOKY + 0.1 - 1.0 * math.sin(a)) for a in [i * math.pi / 8 for i in range(9)]] + [(HOOKX + 1.85, HOOKY + 0.55)]
for a, b in zip(HOOK, HOOK[1:]):
    rs.beam((a[0], a[1], CZ - 1.8), (b[0], b[1], CZ - 1.8), 0.5, ironround(3.2, IRON, rust=0.45, seed=3), cap=True)
for k in range(10):                                                                # weed and tatters hanging off the jib
    tt = 0.2 + k * 0.075
    P = lerp3(B0, B1, tt); ln = 0.8 + (h32(k, 5) % 7) * 0.5
    rs.beam(P, (P[0] + 0.2, P[1] - ln, P[2]), 0.14 + (h32(k, 6) % 3) * 0.06,
            lambda x, y, s, t, z, wp, c=(ALGAE[3] if k % 3 else OCHRE[2]): fogged(c, z), w1=0.06)
rs.beam((-31.0, 1.7, CZ - 2.4), (-33.6, 1.7, CZ - 2.4), 1.3, ironround(3.0, IRON, rust=0.4))           # the winch drum
rs.beam((-30.8, 1.7, CZ - 2.6), (-30.4, 3.0, CZ - 2.6), 0.18, ironround(2.6, IRON, rust=0.4))          # its crank
rs.beam((-34.0, 2.8, CZ - 1.8), (-32.4, 1.9, CZ - 2.4), 0.16, rope)

# ---------------------------------------------------------------------------------------------------- the lamp post at the dock's end
LX, LZ, LTOP = JX1 - 2.4, JZ1 - 1.1, 18.6
rs.beam((LX, -0.1, LZ), (LX, LTOP, LZ), 0.8, timber(3.0, WOOD, seed=90), w1=0.65)
rs.beam((LX + 0.9, 0.0, LZ - 0.4), (LX + 0.1, 3.6, LZ), 0.3, timber(2.4, WOOD, seed=91))           # a strut
for k in range(4):                                                                 # iron bands round the post
    rs.beam((LX - 0.42, 4.0 + k * 3.6, LZ - 0.1), (LX + 0.42, 4.0 + k * 3.6, LZ - 0.1), 0.18, ironround(2.6, IRON, rust=0.5, seed=k))
rs.beam((LX, LTOP - 1.8, LZ), (LX - 3.4, LTOP - 1.4, LZ), 0.34, ironround(3.0, IRON, rust=0.5))   # the arm
rs.beam((LX - 0.2, LTOP - 3.4, LZ), (LX - 2.2, LTOP - 1.6, LZ), 0.18, ironround(2.6, IRON, rust=0.5))
for k in range(5):                                                                 # the twisted iron finial
    a = k / 4
    rs.beam((LX, LTOP, LZ), (LX + (a - 0.5) * 1.8, LTOP + 1.2 + math.sin(a * math.pi) * 0.8, LZ), 0.16, ironround(3.0, IRON, rust=0.5, seed=k), cap=True)
LANT = (LX - 3.05, LTOP - 3.1, LZ)
rs.beam((LANT[0], LTOP - 1.45, LZ), (LANT[0], LANT[1] + 1.15, LZ), 0.1, chain)
def lantern(x, y, s, t, z, wp):
    if s < 0.12 or s > 0.88 or t < 0.08 or t > 0.9 or abs(s - 0.5) < 0.06: return fogged(tone(IRON, 1.8 + t * 2, x, y), z)
    return GLOW[2] if (x + y) % 4 else GLOW[3]
rs.quad((LANT[0] - 0.65, LANT[1] - 0.95, LZ - 0.2), (LANT[0] + 0.65, LANT[1] - 0.95, LZ - 0.2), (LANT[0] - 0.65, LANT[1] + 0.8, LZ - 0.2), lantern, cls='emit')
rs.quad((LANT[0] - 0.85, LANT[1] + 0.8, LZ - 0.4), (LANT[0] + 0.85, LANT[1] + 0.8, LZ - 0.4), (LANT[0], LANT[1] + 1.25, LZ - 0.2),
        lambda x, y, s, t, z, wp: fogged(tone(IRON, 3.6, x, y), z), cls='prop')
rs.quad((LANT[0] - 0.7, LANT[1] - 0.95, LZ - 0.3), (LANT[0] + 0.7, LANT[1] - 0.95, LZ - 0.3), (LANT[0] - 0.7, LANT[1] - 1.2, LZ - 0.3),
        lambda x, y, s, t, z, wp: fogged(tone(IRON, 2.4, x, y), z), cls='prop')

# ---------------------------------------------------------------------------------------------------- chimney smoke (2D, before the painterly pass)
def smoke(col, cls_):
    (sx, sy) = proj((CHIM[0] + CHIM[1]) / 2, CHIM[3] + 0.4, (CHIM[4] + CHIM[5]) / 2)
    n1 = make_noise(9, 71, W, H)
    for i in range(170):
        a = i / 170.0
        cx = sx + a * 120 + math.sin(a * 6) * 6; cy = sy - a * 150 + a * a * 40
        r = 3 + a * 26
        for y in range(int(cy - r), int(cy + r) + 1):
            for x in range(int(cx - r), int(cx + r) + 1):
                if not (0 <= x < W and 0 <= y < H) or cls_[y][x] != 'sky': continue
                d = math.hypot(x - cx, y - cy) / r
                if d > 1: continue
                k = (1 - d) ** 2 * (1 - a) * 0.05 * (0.5 + n1(x * 1.0, y * 1.0))
                c = col[y][x]
                col[y][x] = tuple(int(c[j] + (HAZE[2][j] - c[j]) * min(0.6, k * 3)) for j in range(3))

RENDER = dict(fog=fog_of, post=smoke, mirror=lambda x, y, wp: 0.5 * puddle(wp[0], wp[2]) if wp[2] < DE - 0.5 else 0.0,
              light_gain=1.1, grime_gain=0.8, bloom=0.5, stain_gain=0.6, damp_gain=0.25, sheen_gain=0.5)

def P2(X, Y, Z):
    p = proj(X, Y, Z); return (round(p[0]), round(p[1]))

# ---------------------------------------------------------------------------------------------------- the oil can (a pickup: its own sprite)
OILX, OILZ = -10.5, 18.6
def oilcan(rs):
    """a dented jerrycan-ish oil tin standing in its own spill (a dark sheen with a thin rainbow skin on the boards)"""
    def can(x, y, s, t, z, wp):
        v = 3.6 + 2.0 * (roundlit(t) - 0.5)
        Y = wp[1]
        if 0.55 < Y < 0.75: v += 1.0                                               # the pressed rib
        c = tone(RED, v, x, y)
        if wn(2, wp[0] * 6 + wp[2] * 6, Y * 6) > 0.6: c = tone(RUSTY, v, x, y)    # paint gone to rust
        if Y < 0.25: c = tone(STONE, v - 1.4, x, y)
        return fogged(c, z)
    rs.beam((OILX, 0.0, OILZ), (OILX, 1.15, OILZ), 0.9, can)
    rs.disc(OILX, 1.15, OILZ - 0.02, 0.44, lambda x, y, a, b, z, wp: fogged(tone(RED, 4.6 - b * 1.6, x, y), z) if b > -0.4 else None)
    rs.beam((OILX + 0.12, 1.2, OILZ), (OILX + 0.18, 1.5, OILZ), 0.24, ironround(3.0, METAL, rust=0.6))   # the spout
    rs.beam((OILX - 0.32, 1.25, OILZ), (OILX + 0.0, 1.5, OILZ), 0.1, ironround(2.6, METAL, rust=0.6))    # the handle
    rs.beam((OILX + 0.0, 1.5, OILZ), (OILX + 0.3, 1.25, OILZ), 0.1, ironround(2.6, METAL, rust=0.6))
    def spill(x, y, s, t, z, wp):
        X, _, Z = wp
        d = math.hypot((X - OILX - 0.5) / 1.3, (Z - OILZ + 0.15) / 0.7)
        if d > 1 + (wn(1, X * 3, Z * 3) - 0.5) * 0.5: return None
        c = (22, 20, 16)
        if 0.55 < d < 0.75: c = [MAUVE[3], TEAL[4], OCHRE[3]][int(d * 15) % 3]
        return fogged(c, z)
    rs.quad((OILX - 1.2, 0.015, OILZ - 1.0), (OILX + 2.2, 0.015, OILZ - 1.0), (OILX - 1.2, 0.015, OILZ + 0.8), spill, cls='prop', cut=True)

if __name__ == '__main__':
    img = rs.render(INK, **RENDER)
    img.save(f'{OUT}/harbor.png')
    print('done harbor')
    print('deck edge y', P2(0, 0, DE)[1], '| lamp foot', P2(LX, 0, LZ), 'lantern', P2(*LANT), '| hook', P2(HOOKX, HOOKY, CZ),
          '| boat', P2(BX0, WL, BZ0), P2(BX1, WL, BZ0), '| house door', P2(DOOR[0], 0, HZ0), P2(DOOR[1], DOOR[2], HZ0))
    n0 = rs.n
    oilcan(rs)
    img2 = rs.render(INK, **RENDER)
    (ox, oy) = P2(OILX, 0, OILZ)
    BOX = (ox - 40, oy - 50, ox + 60, oy + 20)
    spr = Image.new('RGBA', (BOX[2] - BOX[0], BOX[3] - BOX[1]), (0, 0, 0, 0))
    p0, p1, ps = img.load(), img2.load(), spr.load()
    mine = lambda x, y: rs.G[y][x] is not None and rs.G[y][x][1] > n0
    for y in range(BOX[1], BOX[3]):
        for x in range(BOX[0], BOX[2]):
            edge = any(mine(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if mine(x, y) or (edge and max(abs(p0[x, y][i] - p1[x, y][i]) for i in range(3)) > 6):
                ps[x - BOX[0], y - BOX[1]] = p1[x, y] + (255,)
    bb = spr.getbbox()
    spr.crop(bb).save(f'{OUT}/oilcan.png')
    img2.save(f'{OUT}/harbor_with_oil.png')
    print('done oil can: top-left', (BOX[0] + bb[0], BOX[1] + bb[1]), 'size', (bb[2] - bb[0], bb[3] - bb[1]), 'foot', (ox, oy))
