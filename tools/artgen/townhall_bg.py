"""The Townhall from the square (TownhallScene), 1067x600, overcast day, on the shared rasteriser (raster3d.py)
through a medium-long lens (F 600 instead of 300; the eye stays 12 units up, the vanishing point (533, 296), the walk
line y 534 = depth 30.25 at this lens) so the whole house stays frontal like the old picture (townhall.png).

  the house    the seat of the Ink Tribunal: a dark ashlar baroque-gothic block, banded rustication on the ground floor,
               round-arched windows with keystones, a central section between two corner towers with bell-shaped slate
               helmets, a copper dome behind, lower wings with a balustrade, a mansard with oculus dormers and corner
               pavilions with obelisks
  the clock    the Stomach Clock: a bone face with carved numerals and wet, sinewy hands in a brass bezel, ringed by a
               muscular stomach wall that bulges out of the facade; gut-tubes hang from it over the facade and grip
               the cornices, veins creep over the stones, bile stains run down under it; one thin tube feeds a brass
               tap over a stone basin on the podium (the sacred bile)
  the door     the portal on the podium: columns, an entablature, a segmental pediment with a ledger-and-quill
               cartouche, double doors in a deep reveal with notices pasted on them and a brass complaint-slot, warm
               light in the fanlight; a flight of six steps between stepped cheek walls comes forward to the square
  the lamps    one cast-iron street lamp at the foot of the stair on the left; the right spot is left clear for Sconce
               (the Gang of Lamps sprite, utils/GangOfLamps.js) -- the two read as a pair
  the square   big worn flagstones, puddles that mirror the house, stray forms, an advertising column pasted with
               edicts, iron railings on stone piers left and right, tenements in the fog behind, a far spire

    python3 townhall_bg.py <outdir>   ->  townhall.png (+ fixed.json: the canvas points the scene uses)"""
import sys, os, math, json
from PIL import Image
import raster3d, paintpass
raster3d.F = paintpass.F = 600.0                   # a medium-long lens: the facade at ~58 units stays frontal
import shedkit
def fog_of(z): return max(0.0, min(0.8, (z - 64.0) / 75.0))
shedkit.fog_of = fog_of
from shedkit import Raster, proj, ray, wn, tone, mix, fogged, sky, facade, ri
from common import h32, ramp, band
from pal_day import SKY, HAZE, STONE, WOOD, GLOW, METAL, LEAF, FOG, INK

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
F, CX, HY, CAMH, W, H = raster3d.F, raster3d.CX, raster3d.HY, raster3d.CAMH, raster3d.W, raster3d.H
def sx(X, Z): return CX + F * X / Z
def sy(Y, Z): return HY + F * (CAMH - Y) / Z

ASH = ramp('#111310 #191c17 #22261f #2c3028 #363b32 #41463c #4d5247 #5a5f53 #686d60 #787c6d #898d7c')      # the house's ashlar
DRESS = ramp('#24221a #312e23 #3f3b2d #4d4838 #5c5643 #6b654f #7b745d #8b846b #9b947b #aba48b')         # dressings
SLATE = ramp('#121417 #1a1d21 #23272c #2d3238 #383e45 #444b53 #525a62')
VERD = ramp('#13201c #1a2b26 #213731 #29443c #325147 #3c5f53 #476d60 #557c6e #658b7c')                   # old copper
BRASS = ramp('#2e220e #4a3716 #6a5020 #8c6b2c #ae8a3e #cbaa5a #e4ca82')
BONE = ramp('#2f2b20 #433d2d #59523c #70684c #877e5e #9d9471 #b2a985 #c5bd9a #d6cfae #e4dec2')
GUT = ramp('#170c0b #221210 #2e1815 #3b1f1a #482720 #553026 #63392d #714436 #7f5040 #8e5e4e #9d6e5e')
SINEW = ramp('#160a0b #22100f #2f1614 #3d1c19 #4c241f #5b2d26 #6b372e')
BILE = ramp('#2e3010 #4a4c16 #686b1e #8a8c2a #aaa83c #c8c45a')
IRON = ramp('#0b0c0c #121414 #1a1d1d #232727 #2d3232 #393f3e')
PAPER = ramp('#4f4c40 #67634f #807b63 #9a9478 #b2ac8e #c8c2a4')
DOOR = ramp('#120c08 #1b120c #251912 #302117 #3b2a1d #473324 #533d2c')
NIGHTGLASS = ramp('#0e1414 #141c1c #1b2524 #23302e #2c3b38 #36463f #43544c #52635a')
WET = (190, 172, 160)

rs = Raster()
def fz(c, z): return fogged(c, z)

# ---------------------------------------------------------------------------------------------------- geometry
ZC = 58.0                                       # the central section's face
ZT, ZW, ZPV = ZC - 1.7, ZC + 2.0, ZC + 1.0      # the corner towers (forward), the wings (back), the wings' pavilions
XC, XT, XW, XP = 10.5, 14.6, 36.0, 32.4         # half-widths: central section, towers' outer edge, wings, pavilions' inner edge
PODIUM = 2.5                                    # the terrace in front of the door
GF, WGF, WCOR, TCOR = 12.8, 10.8, 20.6, 33.4    # string course (central / wings), the wings' cornice, the towers' cornice
DX, DSPR = 2.9, 9.0                             # the door: half width, the arch springs here (apex DSPR + DX)
ZD = ZC + 1.3                                   # the door leaves, deep in the reveal
CLK = (0.0, 24.4, ZC - 1.8)                     # the clock's centre (X, Y, Z of the face)
R_FACE, R_BEZ, R_GUT = 6.0, 6.6, 9.8            # face, brass bezel, the stomach's outer rim
ZG0 = CLK[2] - 1.7                              # the stomach's crown (it bulges this far forward)
STEPS = 6; ST_RISE, ST_RUN = PODIUM / STEPS, 1.45
ZS0 = ZT - STEPS * ST_RUN                       # the front of the lowest step
SXH = 4.6                                       # the stair's half width (cheek walls 1.0 outside it)
LAMP_X, LAMP_Z, LAMP_H = 8.2, ZS0 + 0.4, 12.5   # the lamps beside the stair foot (left baked, right = Sconce)
WING_BAYS = (18.4, 23.0, 27.6)
TWX = (XC + XT) / 2                             # the towers' axis

def masonry(r, u, Y, z, x, y, v0, ch=0.62, L=1.25, seed=0, rough=0.35, weather=0.9, rust=False):
    """coursed ashlar in surface coordinates: merged blocks, sunk joints, a lit arris on top of each course, a tone per
    block, weathering patches, the odd dirty or replaced block; rust=True: banded rustication (deep, wide V joints)"""
    ps = z / F
    row = math.floor(Y / ch); fv = Y / ch - row
    uu = u + (h32(row, seed, 5) % 97) / 97.0 * L * 2.0
    col = math.floor(uu / L); fu = uu / L - col
    c0 = col
    while h32(row, c0, seed) % 3 == 0 and col - c0 < 2: c0 -= 1
    bid = h32(row, c0, seed + 7)
    v = v0 + ((bid % 9) - 4) * 0.1 + (wn(0, u * 0.22 + seed * 7.0, Y * 0.22) - 0.5) * weather
    v += (wn(1, u * 5.0 + (bid % 17), Y * 5.0) - 0.5) * rough
    if bid % 11 == 0: v -= 0.5
    elif bid % 13 == 0: v += 0.3
    if rust:
        jw = max(0.09, 1.6 * ps / ch)
        if fv < jw: return tone(r, v - 2.2, x, y)                                    # the deep channel
        if fv < jw * 1.8: return tone(r, v - 0.9, x, y)                              # its lower chamfer, in shadow
        if fv > 1 - jw: return tone(r, v + 0.9, x, y)                                # the upper chamfer catches the sky
        if fu < ps / L and h32(row, col, seed) % 2: v -= 1.2
        return tone(r, v, x, y)
    if fv > 1 - 1.5 * ps / ch: v += 0.4
    elif fv < 2.5 * ps / ch: v -= 0.35
    if fv < ps / ch or (fu < ps / L and h32(row, col, seed) % 3 != 0): v -= 1.4
    return tone(r, v, x, y)

def grimy(c, X, Y):
    """soot and rain runs on the pale dressings: patches darker, a run hanging under each one"""
    m = wn(2, X * 0.6 + 31.0, Y * 0.5) + (wn(3, X * 2.6, Y * 0.25) - 0.5) * 0.6
    if m > 0.5: c = mix(c, (30, 30, 24), min(0.45, (m - 0.5) * 1.4))
    return c
def lit(Y, Z):
    """overcast light on a front face: the sky from above, the ground's bounce dark at the foot"""
    return 0.25 * min(1.0, Y / 30.0) - 0.6 * max(0.0, 1 - Y / 2.0)

def bile_stain(c, X, Y):
    """dark, faintly bilious runs down the stones under the stomach"""
    if abs(X) > R_GUT + 1.5 or Y > CLK[1] - 3.0: return c
    top = CLK[1] - math.sqrt(max(0.0, R_GUT ** 2 - X ** 2)) * 0.92
    if Y > top: return c
    m = wn(3, X * 1.9 + 40.0, 3.0)
    ln = 2.0 + 9.0 * wn(2, X * 0.7 + 12.0, 5.0)
    if m < 0.5 or top - Y > ln: return c
    k = (m - 0.5) * 2.2 * (1 - (top - Y) / ln)
    return mix(c, (34, 36, 18), min(0.6, k))

# ---------------------------------------------------------------------------------------------------- sky + far city
rs.quad((-1400, 900, 900), (1400, 900, 900), (-1400, -300, 900), sky, cls='sky')
def haze_block(X0, X1, Z, top, seed):
    def sh(x, y, s, t, z, wp):
        X, Y, _ = wp
        v = 2.6 + t * 1.2 + (wn(2, X * 0.1, Y * 0.1) - 0.5) * 0.6
        if (int(X / 3.2) + int(Y / 3.6)) % 3 == 0 and (X / 3.2) % 1 > 0.4 and (Y / 3.6) % 1 > 0.45 and Y > 3: v -= 0.8
        return mix(tone(HAZE, v, x, y), FOG, 0.35)
    rs.quad((X0, 0, Z), (X1, 0, Z), (X0, top, Z), sh, cls='wall')
for (X0, X1, Z, top, sd) in ((-260, -170, 420, 70, 1), (-170, -120, 380, 92, 2), (130, 210, 400, 84, 3), (210, 300, 440, 66, 4)):
    haze_block(X0, X1, Z, top, sd)
def far_spire(x, y, s, t, z, wp):
    X, Y, _ = wp
    w_ = 3.2 if Y < 60 else 3.2 * max(0.0, 1 - (Y - 60) / 34.0)
    if abs(X - 158.0) > w_: return None
    return mix(tone(HAZE, 2.6 + (0.6 if X < 158 else 0), x, y), FOG, 0.3)
rs.quad((150, 0, 360), (166, 0, 360), (150, 95, 360), far_spire, cls='wall', cut=True)

# ---------------------------------------------------------------------------------------------------- tenements behind the railings
def tenement(X0, X1, Z, top, seed, base_r=STONE, roof=True, bay=5.2, floors=4.4):
    base = shedkit.concrete(3.0, base_r)
    rs.box(X0, X1, 0, top, Z, Z + 18, facade(base, bay=bay, floors=floors, y0=4.0, seed=seed, wf=0.4),
           shedkit.concrete(2.2, base_r), cls='wall')
    rs.box(X0 - 0.6, X1 + 0.6, top, top + 0.9, Z - 0.7, Z + 18, lambda x, y, s, t, z, wp: fz(tone(STONE, 4.6 - t * 2, x, y), z),
           lambda x, y, s, t, z, wp: fz(STONE[2], z), bottom=lambda x, y, s, t, z, wp: fz(STONE[1], z), cls='prop')
    if roof:                                                                          # a steep slate roof leaning back
        rs.quad((X0, top + 0.9, Z + 0.4), (X1, top + 0.9, Z + 0.4), (X0, top + 7.0, Z + 6.0),
                lambda x, y, s, t, z, wp: fz(tone(SLATE, 2.2 + t * 1.6 - (0.9 if (wp[0] * 1.4) % 1 < 0.12 else 0), x, y), z), cls='wall')
        for k in range(2):
            cxm = X0 + (X1 - X0) * (0.3 + 0.4 * k)
            rs.box(cxm - 1.0, cxm + 1.0, top + 3.0, top + 9.5 + (h32(seed, k) % 3), Z + 3.5, Z + 5.5,
                   shedkit.concrete(2.6, STONE), shedkit.concrete(2.0, STONE), cls='wall')          # chimneys
tenement(-118, -78, 108, 40, 11, bay=5.6, floors=4.6); tenement(-78, -46, 120, 48, 12, roof=False, bay=4.8, floors=4.2)
tenement(46, 80, 116, 46, 13, bay=5.0, floors=4.4); tenement(80, 124, 104, 38, 14, bay=6.0, floors=4.8)
rs.box(-78.5, -45.5, 48, 49.0, 119.3, 138, lambda x, y, s, t, z, wp: fz(tone(STONE, 4.0, x, y), z), lambda x, y, s, t, z, wp: fz(STONE[2], z), cls='prop')

# ---------------------------------------------------------------------------------------------------- the square
def puddle(X, Z):
    if Z > ZS0 - 0.3: return 0.0
    m = wn(2, X * 0.16 + 4.0, Z * 0.26) + (wn(3, X * 1.1, Z * 1.1) - 0.5) * 0.12
    return max(0.0, min(1.0, (m - 0.67) * 10))
def flags(x, y, s, t, z, wp):
    """big worn flagstones in rows across the square, a trodden lane to the stair, cracks, moss in the joints"""
    X, _, Z = wp
    D = 3.0
    row = math.floor(Z / D); fz_ = Z / D - row
    Wd = 2.6 + (h32(row, 1) % 3) * 0.5
    uu = X + (h32(row, 2) % 10) / 10.0 * Wd
    col = math.floor(uu / Wd); fx = uu / Wd - col
    ps, psz = z / F, z * z / (F * CAMH)
    sid = h32(col, row, 3)
    v = 4.3 + ((sid % 7) - 3) * 0.17 + (wn(0, X * 0.25, Z * 0.25) - 0.5) * 0.55 + (wn(1, X * 2.0, Z * 0.9) - 0.5) * 0.45
    v -= min(1.1, max(0.0, (36.0 - Z) / 10.0))                                       # darker towards the viewer
    v += 0.55 * math.exp(-(X / 3.6) ** 2) * (1 if Z > 33 else 0)                     # the lane trodden pale to the stair
    if sid % 6 == 0 and abs((fx - 0.25) - fz_ * 0.55) < ps / Wd * 1.3: v -= 1.4      # a crack
    c = tone(ASH, v, x, y)
    if fx < ps / Wd * 1.3 or fz_ < psz / D * 1.3:
        c = tone(ASH, v - 2.0, x, y)
        if wn(2, X * 0.7, Z * 0.7) > 0.58: c = mix(c, LEAF[1], 0.35)                # moss in the joints
    p_ = puddle(X, Z)
    if p_: c = mix(c, (16, 22, 20), p_ * 0.4)
    return fz(c, Z)
rs.quad((-160, 0, 22), (160, 0, 22), (-160, 0, 140), flags, cls='ground')
rs.box(-1.1, 1.1, 0.0, 0.05, 36.0, 37.2, lambda x, y, s, t, z, wp: IRON[0], lambda x, y, s, t, z, wp: IRON[0],
       top=lambda x, y, s, t, z, wp: IRON[0] if (s * 8) % 1 < 0.45 else IRON[3], cls='prop')                       # a drain grate

# ---------------------------------------------------------------------------------------------------- windows
def opening(X, Y, cx, w, y0, y1):
    """inside a round-arched opening: the rectangle up to the springing (y1 - w/2) and the semicircle on it"""
    hw = w / 2.0; ys = y1 - hw
    if abs(X - cx) > hw or Y < y0 or Y > y1: return False
    return Y <= ys or math.hypot(X - cx, Y - ys) <= hw
WINS = []                                        # (cx, w, y0, y1, Z, state, seed)
def win(cx, w, y0, y1, Z, state, seed): WINS.append((cx, w, y0, y1, Z, state, seed))
def surround_of(X, Y, wins, band_=0.38):
    """the dressed architrave, the keystone and the sill around the openings: (dv, kind) or None"""
    for (cx, w, y0, y1, Z, state, seed) in wins:
        hw = w / 2.0
        if not (cx - hw - band_ - 0.6 < X < cx + hw + band_ + 0.6 and y0 - 1.0 < Y < y1 + band_ + 0.8): continue
        ys = y1 - hw
        if abs(X - cx) < 0.48 and y1 - 0.1 < Y < y1 + band_ + 0.5: return (1.4 - (Y - y1) * 0.6, 'key')        # the keystone
        if Y < y0 and Y > y0 - 0.5 and abs(X - cx) < hw + band_ + 0.3: return (1.2 if Y > y0 - 0.16 else -0.6, 'sill')
        if Y <= ys:
            d = abs(X - cx) - hw
            if 0 <= d < band_ and Y >= y0: return (0.9 - d * 1.2, 'jamb')
        else:
            d = math.hypot(X - cx, Y - ys) - hw
            if 0 <= d < band_:
                a = math.degrees(math.atan2(Y - ys, X - cx))
                return (0.9 - d * 1.2 - (1.2 if (a / 22.5) % 1 < 0.07 else 0), 'arch')                          # voussoirs
    return None
def glass_sh(cx, w, y0, y1, Zw, state, seed):
    """the window behind the opening: a fake reveal on the side towards the eye, the frame, glazing bars, and the panes
    -- the overcast sky in them, or warm light, or a dark room with a curtain"""
    hw = w / 2.0
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        if not opening(X, Y, cx, w + 0.9, y0 - 0.45, y1 + 0.45): return None
        if not opening(X, Y, cx, w, y0, y1): return fz(tone(ASH, 2.2, x, y), z)
        rv = 0.55 * abs(cx) / Zw                                                      # how much reveal shows on the inner side
        if (cx < 0 and X > cx + hw - rv) or (cx > 0 and X < cx - hw + rv):
            return fz(tone(ASH, 3.4 - (0.6 if Y > y1 - hw else 0), x, y), z)
        if Y < y0 + 0.22: return fz(tone(DRESS, 2.0, x, y), z)
        u, v = (X - cx + hw) / w, (Y - y0) / (y1 - y0)
        ps = z / F
        bar = max(0.08, ps * 1.1)
        ys = y1 - hw
        k = h32(int(u * 2), int(v * 4), seed)
        if abs(X - cx) < bar * 0.6 or (abs((Y - y0) % 1.7) < bar and Y < ys) or abs(Y - ys) < bar:
            return fz(tone(DOOR, 2.4, x, y), z)                                         # mullion, transoms
        if Y > ys and abs(math.hypot(X - cx, Y - ys) - hw * 0.55) < bar: return fz(tone(DOOR, 2.4, x, y), z)  # the fan
        if state == 'lit':
            g = 1.2 - abs(u - 0.5) * 1.6 + (0.5 if k % 5 == 0 else 0) - (1.2 if k % 7 == 3 else 0) + v * 0.3
            return mix(ri(GLOW, band(g, x, y)), (60, 50, 34), 0.25)
        if state == 'dim':
            return fz(mix(tone(WOOD, 3.2 + v * 1.4 - abs(u - 0.5) * 2.0, x, y), GLOW[1], 0.35 * (1 - abs(u - 0.5) * 1.6)), z)
        if state == 'curtain' and Y < ys:
            fold = (u * 9) % 1
            return fz(mix(tone(GUT, 3.6 + (0.8 if fold < 0.35 else 0) - (0.8 if fold > 0.8 else 0), x, y), (40, 40, 34), 0.5), z)
        c = tone(NIGHTGLASS, 1.8 + v * 3.4 + (1.4 if (u + v * 0.6 + seed * 0.13) % 0.8 < 0.07 else 0) + (wn(3, X * 0.4, Y * 0.2) - 0.5), x, y)
        if state == 'broken' and k % 3 == 0 and v < 0.5: c = IRON[0]
        return fz(c, z)
    return sh
def place_windows(wins):
    for (cx, w, y0, y1, Z, state, seed) in wins:
        hw = w / 2.0 + 0.45
        rs.quad((cx - hw, y0 - 0.5, Z + 0.5), (cx + hw, y0 - 0.5, Z + 0.5), (cx - hw, y1 + 0.5, Z + 0.5),
                glass_sh(cx, w, y0, y1, Z + 0.5, state, seed), cls='emit' if state == 'lit' else 'prop', cut=True)

def cutbox(x0, x1, y0, y1, z0, z1, front, side, cls='wall'):
    """a box whose front face may have holes (the shader's None = see through to what is behind)"""
    obj = rs.obj()
    rs.quad((x0, y0, z0), (x1, y0, z0), (x0, y1, z0), front, obj, cls=cls, cut=True)
    if x1 < 0: rs.quad((x1, y0, z0), (x1, y0, z1), (x1, y1, z0), side, obj, cls=cls)
    elif x0 > 0: rs.quad((x0, y0, z0), (x0, y0, z1), (x0, y1, z0), side, obj, cls=cls)
    return obj
def cornice_front(x, y, s, t, z, wp): return fz(grimy(tone(DRESS, 4.6 - (1.3 if t < 0.35 else 0) + (0.8 if t > 0.85 else 0) - (0.5 if 0.5 < t < 0.56 else 0), x, y), wp[0], wp[1]), z)
def cornice_side(x, y, s, t, z, wp): return fz(DRESS[2], z)
def cornice_bottom(x, y, s, t, z, wp): return fz(tone(DRESS, 1.6, x, y), z)
def cheek(v0, seed=41):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        return fz(masonry(ASH, X + Z, Y, z, x, y, v0, ch=0.7, L=1.4, seed=seed), z)
    return sh
def coping(x, y, s, t, z, wp):
    return fz(tone(DRESS, 5.0 + (0.6 if t > 0.7 else 0) + (wn(0, wp[0] * 2, wp[2]) - 0.5) * 0.6, x, y), z)

# ---------------------------------------------------------------------------------------------------- the wings
for sgn in (-1, 1):
    for i, bx in enumerate(WING_BAYS):
        X = sgn * bx
        win(X, 2.4, 2.8, 8.6, ZW, ['lit' if sgn < 0 else 'dim', 'dark', 'dim'][(i + (sgn > 0)) % 3], 10 + i + (sgn > 0) * 5)
        win(X, 2.4, 12.4, 18.4, ZW, ['dark', 'curtain', 'dark'][(i + (sgn < 0)) % 3], 20 + i + (sgn > 0) * 5)
    win(sgn * 34.2, 2.0, 3.0, 8.4, ZPV, 'dark', 30 + (sgn > 0))
    win(sgn * 34.2, 2.0, 12.6, 18.0, ZPV, 'broken' if sgn > 0 else 'dark', 32 + (sgn > 0))
WIN_W = [w_ for w_ in WINS if w_[4] == ZW]; WIN_P = [w_ for w_ in WINS if w_[4] == ZPV]
def wall_sh(wins, v0, seed, string_y=WGF):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        for (cx, w, y0, y1, Zw, st, sd) in wins:
            if opening(X, Y, cx, w, y0, y1): return None
        sr = surround_of(X, Y, wins)
        if sr: return fz(grimy(tone(DRESS, 4.4 + sr[0] + lit(Y, Z) + (wn(1, X * 3, Y * 3) - 0.5) * 0.5, x, y), X, Y), z)
        if abs(Y - string_y) < 0.4: return fz(tone(DRESS, 4.2 + (0.9 if Y > string_y + 0.18 else -0.5 if Y < string_y - 0.22 else 0), x, y), z)
        rust_ = Y < string_y
        c = masonry(ASH, X, Y, z, x, y, v0 + lit(Y, Z) - (0.4 if rust_ else 0), ch=0.85 if rust_ else 0.56, L=1.6 if rust_ else 1.15, seed=seed, rust=rust_)
        return fz(c, z)
    return sh
for sgn in (-1, 1):
    x0, x1 = sorted((sgn * XT, sgn * XP))
    rs.quad((x0, 0, ZW), (x1, 0, ZW), (x0, WCOR, ZW), wall_sh(WIN_W, 4.0, 3 + (sgn > 0)), cls='wall', cut=True)
    p0, p1 = sorted((sgn * XP, sgn * XW))                                                  # the pavilion at the outer corner
    cutbox(p0, p1, 0, WCOR + 1.4, ZPV, ZW + 6, wall_sh(WIN_P, 4.3, 5 + (sgn > 0)),
           lambda x, y, s, t, z, wp: fz(masonry(ASH, wp[2], wp[1], z, x, y, 2.6, seed=8), z))
    for qx in (p0, p1):                                                                   # quoins on the pavilion's corners
        for k in range(int(WCOR + 1)):
            if k % 2 or k < WGF: continue
            ww = 1.0 if (k // 2) % 2 else 0.65
            a0 = qx if qx == p0 else qx - ww
            rs.quad((a0, k * 1.0, ZPV - 0.06), (a0 + ww, k * 1.0, ZPV - 0.06), (a0, k * 1.0 + 0.95, ZPV - 0.06),
                    lambda x, y, s, t, z, wp: fz(tone(DRESS, 4.4 + (0.8 if t > 0.75 else -0.4 if t < 0.15 else 0) + lit(wp[1], z), x, y), z), cls='wall')
    c0, c1 = sorted((sgn * XT, sgn * (XW + 0.6)))                                          # the cornice and the balustrade on it
    rs.box(c0, c1, WCOR, WCOR + 1.1, ZPV - 0.9, ZW + 6, cornice_front, cornice_side, bottom=cornice_bottom, cls='prop')
    def balus(x, y, s, t, z, wp):
        X, Y, Z = wp
        if Y > WCOR + 2.65: return fz(grimy(tone(DRESS, 4.6 + (0.6 if Y > WCOR + 2.85 else 0), x, y), X, Y), z)  # the rail
        if Y < WCOR + 1.45: return fz(tone(DRESS, 3.8, x, y), z)                                                  # the plinth
        u = (X / 0.66) % 1; v = (Y - WCOR - 1.45) / 1.2
        prof = 0.18 + 0.16 * math.sin(v * math.pi) ** 2 - (0.1 if 0.62 < v < 0.72 else 0)
        if abs(u - 0.5) > prof: return None
        return fz(grimy(tone(DRESS, 4.4 - (u - 0.5) * 5.0, x, y), X, Y + 3.0), z)
    rs.quad((c0, WCOR + 1.1, ZPV - 0.5), (c1, WCOR + 1.1, ZPV - 0.5), (c0, WCOR + 3.0, ZPV - 0.5), balus, cls='prop', cut=True)
    m0, m1 = sorted((sgn * XT, sgn * (XW - 1.0)))                                          # the mansard, slate, oculus dormers
    MB = WCOR + 3.0
    def mansard(x, y, s, t, z, wp, sgn=sgn):
        X, Y, Z = wp
        for bx in WING_BAYS:
            d = math.hypot(X - sgn * bx, Y - (MB + 2.0))
            if d < 1.05: return fz(tone(NIGHTGLASS, 2.4 + (Y - MB - 2.0) * 1.2, x, y), z) if d < 0.72 else fz(tone(DRESS, 4.6 - (Y < MB + 2.0) * 1.0, x, y), z)
        v = 2.4 + t * 1.4 - (0.8 if (X * 1.6) % 1 < 0.1 else 0) + (0.5 if (Y * 2.2) % 1 < 0.12 else 0) + (wn(2, X * 0.4, Y) - 0.5) * 0.6
        return fz(tone(SLATE, v, x, y), z)
    rs.quad((m0, MB, ZW + 1.0), (m1, MB, ZW + 1.0), (m0, MB + 4.2, ZW + 3.0), mansard, cls='wall')
    for px_ in (sgn * (XP + 0.4), sgn * (XW - 0.4)):                                        # obelisks on the pavilion
        rs.box(px_ - 0.55, px_ + 0.55, WCOR + 1.4, WCOR + 2.7, ZPV - 0.3, ZPV + 0.9, lambda x, y, s, t, z, wp: fz(tone(DRESS, 4.2 + (0.6 if t > 0.8 else 0), x, y), z),
               cornice_side, cls='prop')
        def obel(x, y, s, t, z, wp, px_=px_):
            X, Y, Z = wp
            if abs(X - px_) > 0.42 * (1 - (Y - WCOR - 2.7) / 4.6) + 0.02: return None
            return fz(tone(DRESS, 4.4 + (0.6 if X < px_ else -0.5), x, y), z)
        rs.quad((px_ - 0.5, WCOR + 2.7, ZPV + 0.2), (px_ + 0.5, WCOR + 2.7, ZPV + 0.2), (px_ - 0.5, WCOR + 7.3, ZPV + 0.2), obel, cls='prop', cut=True)

# ---------------------------------------------------------------------------------------------------- the dome (behind the clock)
DZ, DR, DB = 68.0, 12.5, 29.6
def drum(x, y, s, t, z, wp):
    X, Y, Z = wp
    a = (X / DR)
    if abs(a) > 1: return None
    for k in range(-2, 3):
        if abs(X - k * 4.6) < 0.9 and DB + 0.9 < Y < DB + 3.4: return fz(tone(NIGHTGLASS, 2.0 + (Y - DB), x, y), z)
        if abs(X - k * 4.6 - 2.3) < 0.32: return fz(tone(DRESS, 4.6, x, y), z)                     # pilasters
    return fz(masonry(ASH, X, Y, z, x, y, 4.2 - abs(a) ** 2 * 1.8, seed=21), z)
rs.quad((-DR, DB - 6, DZ), (DR, DB - 6, DZ), (-DR, DB + 4.2, DZ), drum, cls='wall', cut=True)
rs.box(-DR - 0.6, DR + 0.6, DB + 4.0, DB + 4.8, DZ - 0.6, DZ + 4, cornice_front, cornice_side, bottom=cornice_bottom, cls='prop')
DH = 9.6
def dome(x, y, s, t, z, wp):
    X, Y, Z = wp
    h = Y - (DB + 4.8)
    if h < 0 or h > DH: return None
    rr = DR * math.sqrt(max(0.0, 1 - (h / DH) ** 2)) * (1 - 0.05 * h / DH)
    if abs(X) > rr: return None
    a = X / max(0.01, rr)
    v = 4.4 - abs(a) ** 1.6 * 2.6 - (0.6 if a > 0 else 0) + h * 0.05
    rib = (math.asin(max(-1.0, min(1.0, a))) / (math.pi / 10)) % 1
    if rib < 0.09: v += 1.0                                                                     # the standing-seam ribs
    elif rib < 0.18: v -= 0.6
    c = tone(VERD, v + (wn(2, X * 0.8, Y * 0.5) - 0.5) * 0.8, x, y)
    if wn(3, X * 1.4, Y * 0.3) > 0.66: c = mix(c, (26, 30, 26), 0.4)                           # dark streaks off the seams
    return fz(c, z)
rs.quad((-DR - 0.5, DB + 4.8, DZ + 1), (DR + 0.5, DB + 4.8, DZ + 1), (-DR - 0.5, DB + 4.8 + DH, DZ + 1), dome, cls='wall', cut=True)
def lantern_d(x, y, s, t, z, wp):
    X, Y, Z = wp
    b = DB + 4.8 + DH - 0.4
    if Y < b or Y > b + 7.0: return None
    if Y < b + 3.5:
        if abs(X) > 2.0: return None
        if abs(X) < 1.3 and (X + 1.3) % 0.85 > 0.32 and Y > b + 0.6: return fz(tone(NIGHTGLASS, 3.0, x, y), z)
        return fz(tone(DRESS, 4.4 - (0.8 if X > 0.8 else 0), x, y), z)
    rr = 2.2 * (1 - (Y - b - 3.5) / 3.5)
    if abs(X) > rr: return None
    return fz(tone(VERD, 4.6 - abs(X) / max(0.2, rr) * 2.0, x, y), z)
rs.quad((-2.4, DB + 4.4 + DH, DZ - 0.5), (2.4, DB + 4.4 + DH, DZ - 0.5), (-2.4, DB + 11.4 + DH, DZ - 0.5), lantern_d, cls='wall', cut=True)

# ---------------------------------------------------------------------------------------------------- the central section
win(-7.3, 2.2, PODIUM + 1.6, PODIUM + 7.2, ZC, 'dim', 41); win(7.3, 2.2, PODIUM + 1.6, PODIUM + 7.2, ZC, 'dim', 42)
win(-7.7, 2.0, GF + 2.2, GF + 7.2, ZC, 'dark', 43); win(7.7, 2.0, GF + 2.2, GF + 7.2, ZC, 'curtain', 44)
WIN_C = [w_ for w_ in WINS if w_[4] == ZC]
def door_open(X, Y): return opening(X, Y, 0.0, 2 * DX, PODIUM, DSPR + DX)
def central(x, y, s, t, z, wp):
    X, Y, Z = wp
    if door_open(X, Y): return None
    for (cx, w, y0, y1, Zw, st, sd) in WIN_C:
        if opening(X, Y, cx, w, y0, y1): return None
    sr = surround_of(X, Y, WIN_C)
    if sr: return fz(bile_stain(grimy(tone(DRESS, 4.4 + sr[0] + lit(Y, Z), x, y), X, Y), X, Y), z)
    if abs(Y - GF) < 0.45: return fz(bile_stain(tone(DRESS, 4.3 + (0.9 if Y > GF + 0.2 else -0.6 if Y < GF - 0.25 else 0), x, y), X, Y), z)
    rust_ = Y < GF
    c = masonry(ASH, X, Y, z, x, y, 4.1 + lit(Y, Z) - (0.4 if rust_ else 0), ch=0.85 if rust_ else 0.56, L=1.6 if rust_ else 1.15, seed=2, rust=rust_)
    return fz(bile_stain(c, X, Y), z)
rs.quad((-XC, PODIUM, ZC), (XC, PODIUM, ZC), (-XC, TCOR, ZC), central, cls='wall', cut=True)
rs.box(-XC - 0.4, XC + 0.4, TCOR - 0.8, TCOR + 0.3, ZC - 0.8, ZC + 3, cornice_front, cornice_side, bottom=cornice_bottom, cls='prop')

# the door: the reveal, the leaves, the fanlight
def reveal(x, y, s, t, z, wp):
    X, Y, Z = wp
    return fz(masonry(ASH, Z * 3, Y, z, x, y, 3.0 - (1.0 if Y > DSPR else 0), seed=17), z)
for sg in (-1, 1):
    rs.quad((sg * DX, PODIUM, ZC), (sg * DX, PODIUM, ZD), (sg * DX, DSPR, ZC), reveal, cls='wall')
NOTICES = ((1.2, 5.8, 1.0, 1.35, 1), (2.05, 6.6, 0.8, 1.05, 2), (-1.7, 6.1, 0.9, 1.15, 3))
def leaves(x, y, s, t, z, wp):
    X, Y, Z = wp
    if not door_open(X, Y): return None
    ps = z / F
    if Y > DSPR - 0.15:                                                                 # the fanlight: warm light inside
        d = math.hypot(X, Y - DSPR)
        if d > DX - 0.3 or Y < DSPR + 0.12: return tone(DOOR, 1.4, x, y)
        a = math.degrees(math.atan2(Y - DSPR, X))
        if (a / 30.0) % 1 < 0.12 or abs(d - 1.2) < 0.11: return tone(BRASS, 2.0, x, y)
        return ri(GLOW, band(2.6 - d * 0.35, x, y))
    if abs(X) < max(0.06, ps * 0.9): return tone(DOOR, 0.6, x, y)                      # the meeting stiles
    u = (abs(X) / DX)
    pv = (Y - PODIUM) / (DSPR - PODIUM)
    v = 3.0 + (wn(1, X * 2.0, Y * 0.4) - 0.5) * 0.8 - u * 0.4
    pan = 0.12 < u < 0.86 and (0.08 < pv < 0.44 or 0.52 < pv < 0.92)                   # four raised panels a leaf
    if pan:
        e = min(u - 0.12, 0.86 - u, abs(pv - (0.08 if pv < 0.48 else 0.52)), abs((0.44 if pv < 0.48 else 0.92) - pv))
        if e < 0.03: v -= 1.4
        elif e < 0.06: v += 0.8
    elif (pv * 9) % 1 < 0.06: v -= 0.7
    if abs(pv - 0.48) < 0.03 and 0.0 < u < 0.95: return tone(IRON, 3.0 + (0.8 if (x % 3) == 0 else 0), x, y)   # an iron strap
    if 0.04 < u < 0.14 and abs(pv - 0.5) < 0.05: return tone(BRASS, 4.2, x, y)       # ring pulls
    if X < 0 and 0.35 < u < 0.75 and abs(pv - 0.3) < 0.045:                           # the brass complaint-slot
        return INK if abs(pv - 0.3) < 0.016 and 0.42 < u < 0.68 else tone(BRASS, 4.6 - (pv - 0.3) * 20, x, y)
    for (nx, ny, nw, nh, sd) in NOTICES:                                              # notices pasted on the leaves
        if nx - nw / 2 < X < nx + nw / 2 and ny - nh / 2 < Y < ny + nh / 2:
            fu, fv = (X - nx + nw / 2) / nw, (Y - ny + nh / 2) / nh
            if sd == 3 and fu + (1 - fv) * 0.6 > 1.1: break                               # torn off
            if 0.15 < fu < 0.85 and (fv * 6) % 1 < 0.25 and fv < 0.8: return tone(PAPER, 1.0, x, y)
            if sd == 1 and math.hypot(fu - 0.72, fv - 0.18) < 0.13: return (120, 36, 30)     # a red seal
            return tone(PAPER, 3.4 - fv * 0.8, x, y)
    return tone(DOOR, v, x, y)
rs.quad((-DX, PODIUM, ZD), (DX, PODIUM, ZD), (-DX, DSPR + DX, ZD), leaves, cls='prop', cut=True)
rs.quad((-DX, DSPR + 0.2, ZD - 0.05), (DX, DSPR + 0.2, ZD - 0.05), (-DX, DSPR + DX, ZD - 0.05),
        lambda x, y, s, t, z, wp: (leaves(x, y, s, t, z, wp) if math.hypot(wp[0], wp[1] - DSPR) < DX - 0.3 and wp[1] > DSPR + 0.12 else None), cls='emit', cut=True)
# the portal: columns, entablature, segmental pediment with a ledger-and-quill cartouche
ENT = DSPR + DX - 0.1
def column(cx):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = (X - cx) / 0.42
        if Y < PODIUM + 0.9 or Y > ENT - 0.7: return fz(tone(DRESS, 4.4 - u * 0.8 + (0.8 if (Y % 0.5) > 0.38 else 0), x, y), z)  # base, capital
        fl = (u * 2.5 + 2.5) % 1
        return fz(tone(DRESS, 4.6 - u * 1.4 - (0.7 if fl < 0.25 else 0) + (wn(1, X * 4, Y * 0.5) - 0.5) * 0.5, x, y), z)
    return sh
for cx in (-4.1, 4.1):
    rs.box(cx - 0.42, cx + 0.42, PODIUM, ENT, ZC - 0.9, ZC - 0.1, column(cx), lambda x, y, s, t, z, wp: fz(DRESS[3], z), cls='prop')
rs.box(-5.2, 5.2, ENT, ENT + 1.2, ZC - 1.2, ZC, lambda x, y, s, t, z, wp: fz(tone(DRESS, 4.8 - (1.4 if t < 0.25 else 0) + (0.9 if t > 0.85 else 0) - (0.6 if 0.4 < t < 0.46 else 0), x, y), z),
       cornice_side, bottom=lambda x, y, s, t, z, wp: fz(DRESS[1], z), cls='prop')
PB = ENT + 1.2
def pediment(x, y, s, t, z, wp):
    X, Y, Z = wp
    top = PB + 1.9 * math.sqrt(max(0.0, 1 - (X / 5.5) ** 2))
    if Y > top or abs(X) > 5.5: return None
    if Y > top - 0.4: return fz(tone(DRESS, 5.2 - (Y - top + 0.4) * 2, x, y), z)
    e = math.hypot(X / 1.1, (Y - PB - 0.85) / 0.66)
    if e < 1:                                                                               # the cartouche: a ledger and a quill
        if e > 0.82: return fz(tone(DRESS, 5.4, x, y), z)
        if abs(Y - PB - 0.85 - X * 0.05) < 0.26 and abs(X) < 0.66: return fz(tone(DRESS, 4.0 + (0.8 if X < 0 else 0), x, y), z)
        if abs((X - 0.22) - (Y - PB - 0.85) * 1.6) < 0.07 and Y > PB + 0.8: return fz(tone(DRESS, 2.4, x, y), z)
        return fz(tone(DRESS, 3.0, x, y), z)
    return fz(tone(DRESS, 3.4, x, y), z)
rs.quad((-5.6, PB, ZC - 0.9), (5.6, PB, ZC - 0.9), (-5.6, PB + 2.1, ZC - 0.9), pediment, cls='prop', cut=True)

# the podium, the stair and its cheek walls
def podium_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    if Y > PODIUM - 0.28: return fz(tone(DRESS, 4.6 + (0.7 if Y > PODIUM - 0.1 else 0), x, y), z)
    return fz(masonry(ASH, X, Y, z, x, y, 3.6, ch=0.9, L=1.9, seed=31, rust=True), z)
def terrace(x, y, s, t, z, wp):
    X, Y, Z = wp
    return fz(tone(ASH, 5.0 + (wn(0, X * 0.8, Z * 2) - 0.5) * 0.8 + 0.5 * math.exp(-(X / 3.0) ** 2), x, y), z)
for sg in (-1, 1):
    x0, x1 = sorted((sg * (SXH + 1.0), sg * XC))
    rs.box(x0, x1, 0, PODIUM, ZT, ZC, podium_front, podium_front, top=terrace, cls='wall')
rs.quad((-SXH, PODIUM + 0.01, ZT), (SXH, PODIUM + 0.01, ZT), (-SXH, PODIUM + 0.01, ZC), terrace, cls='prop')
def tread(i):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = 5.2 + (wn(0, X * 0.5, Z * 2.0) - 0.5) * 0.8 + 0.7 * math.exp(-(X / 2.0) ** 2) - i * 0.05
        if (X + 20) % 2.3 < z / F * 1.2: v -= 1.3
        if t < 0.12: v += 0.8                                                               # the nosing
        return fz(tone(ASH, v, x, y), z)
    return sh
def riser(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 3.0 + (wn(1, X * 0.7, Y * 3.0) - 0.5) * 0.8 + (0.9 if t > 0.78 else 0) - (0.6 if t < 0.2 else 0)
    if (X + 20) % 2.3 < z / F * 1.2: v -= 1.1
    return fz(tone(ASH, v, x, y), z)
for i in range(STEPS):
    z0 = ZS0 + i * ST_RUN
    rs.box(-SXH, SXH, 0, ST_RISE * (i + 1), z0, ZT, riser, riser, top=tread(i), cls='prop')
for sg in (-1, 1):
    x0, x1 = sorted((sg * SXH, sg * (SXH + 1.0)))
    for (za, zb, top) in ((ZS0 + 1.3, ZS0 + 4.2, 1.9), (ZS0 + 4.2, ZS0 + 6.6, 2.8), (ZS0 + 6.6, ZT, 3.7)):
        rs.box(x0, x1, 0, top - 0.3, za, zb, cheek(3.6), cheek(3.0), cls='wall')
        rs.box(x0 - 0.13, x1 + 0.13, top - 0.3, top, za - 0.13, zb, coping, coping, top=coping, cls='prop')
    rs.box(x0 - 0.25, x1 + 0.25, 0, 2.2, ZS0 - 0.1, ZS0 + 1.3, cheek(4.0), cheek(3.2), cls='wall')      # the newel at the stair foot
    rs.box(x0 - 0.4, x1 + 0.4, 2.2, 2.55, ZS0 - 0.25, ZS0 + 1.45, coping, coping, top=coping, cls='prop')
    rs.disc((x0 + x1) / 2, 3.1, ZS0 + 0.6, 0.55, lambda x, y, s, t, z, wp: fz(tone(DRESS, 5.6 - s * 1.2 - t * 1.6, x, y), z))

# ---------------------------------------------------------------------------------------------------- the corner towers
def tower_front(sgn):
    tw = []
    cx = sgn * TWX
    tw.append((cx, 1.5, 3.6, 9.4, ZT, 'dark', 51 + (sgn > 0)))
    tw.append((cx, 1.5, GF + 2.0, GF + 7.4, ZT, 'dim' if sgn < 0 else 'dark', 53 + (sgn > 0)))
    OCY = GF + 13.0
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        for (wx, w, y0, y1, Zw, st, sd) in tw:
            if opening(X, Y, wx, w, y0, y1): return None
        d = math.hypot(X - cx, Y - OCY)
        if d < 1.0: return None                                                               # the oculus
        if d < 1.32: return fz(tone(DRESS, 5.0 - (Y < OCY) * 1.2, x, y), z)
        sr = surround_of(X, Y, tw, band_=0.3)
        if sr: return fz(grimy(tone(DRESS, 4.4 + sr[0] + lit(Y, Z), x, y), X, Y), z)
        if abs(Y - GF) < 0.45 or abs(Y - (GF + 9.6)) < 0.35: return fz(tone(DRESS, 4.4 + (0.8 if (Y % 1) > 0.5 else -0.4), x, y), z)
        e = min(abs(X - sgn * XC), abs(X - sgn * XT))                                       # quoins on the corners
        if e < 0.75 + 0.35 * (math.floor(Y / 0.9) % 2) and Y > GF + 0.5:
            return fz(tone(DRESS, 4.2 + (0.7 if (Y / 0.9) % 1 > 0.85 else -0.3 if (Y / 0.9) % 1 < 0.1 else 0) + lit(Y, Z), x, y), z)
        rust_ = Y < GF
        return fz(masonry(ASH, X, Y, z, x, y, 4.3 + lit(Y, Z) - (0.4 if rust_ else 0), ch=0.85 if rust_ else 0.56, L=1.6 if rust_ else 1.15, seed=60 + sgn, rust=rust_), z)
    return sh, tw, OCY
for sgn in (-1, 1):
    x0, x1 = sorted((sgn * XC, sgn * XT))
    sh_, tw_, ocy = tower_front(sgn)
    cutbox(x0, x1, 0, TCOR, ZT, ZC + 4, sh_, lambda x, y, s, t, z, wp: fz(masonry(ASH, wp[2], wp[1], z, x, y, 2.8, seed=64), z))
    place_windows(tw_)
    rs.quad((sgn * TWX - 1.2, ocy - 1.2, ZT + 0.5), (sgn * TWX + 1.2, ocy - 1.2, ZT + 0.5), (sgn * TWX - 1.2, ocy + 1.2, ZT + 0.5),
            lambda x, y, s, t, z, wp: fz(tone(NIGHTGLASS, 2.0 + t * 3, x, y), z), cls='prop')
    rs.box(x0 - 0.45, x1 + 0.45, TCOR, TCOR + 1.1, ZT - 0.8, ZC + 4, cornice_front, cornice_side, bottom=cornice_bottom, cls='prop')
    tcx = sgn * TWX
    TB = TCOR + 1.1
    def turret(x, y, s, t, z, wp, tcx=tcx, TB=TB):
        X, Y, Z = wp
        u = (X - tcx) / 1.55
        if abs(u) > 1: return None
        if abs(u) < 0.3 and TB + 0.5 < Y < TB + 2.0 + 0.45 * math.sqrt(max(0.0, 1 - (u / 0.3) ** 2)): return fz(tone(NIGHTGLASS, 2.0, x, y), z)
        facet = abs(u) > 0.62                                                               # the octagon's turned faces
        return fz(masonry(ASH, X, Y, z, x, y, 4.4 - (1.4 if facet and u > 0 else 0.6 if facet else 0), seed=70), z)
    rs.quad((tcx - 1.55, TB, ZT + 1.2), (tcx + 1.55, TB, ZT + 1.2), (tcx - 1.55, TB + 2.9, ZT + 1.2), turret, cls='wall', cut=True)
    rs.box(tcx - 1.85, tcx + 1.85, TB + 2.9, TB + 3.3, ZT + 0.9, ZT + 4.0, lambda x, y, s, t, z, wp: fz(tone(DRESS, 4.6 - (t < 0.4), x, y), z),
           cornice_side, bottom=lambda x, y, s, t, z, wp: fz(DRESS[1], z), cls='prop')
    HB = TB + 3.3
    def helmet(x, y, s, t, z, wp, tcx=tcx, HB=HB):
        """a bell-shaped baroque helmet in slate with a brass finial"""
        X, Y, Z = wp
        h = (Y - HB) / 3.6
        if h < 0 or h > 1: return None
        if h > 0.78:
            if abs(X - tcx) < 0.12 or math.hypot(X - tcx, Y - HB - 3.1) < 0.28: return fz(tone(BRASS, 3.6 - (X - tcx) * 3, x, y), z)
            return None
        rr = 1.75 * (1.0 + 0.25 * math.sin(h / 0.78 * math.pi * 0.9) - 0.95 * (h / 0.78) ** 2.2)
        if abs(X - tcx) > rr: return None
        a = (X - tcx) / max(0.05, rr)
        v = 3.6 - a * 1.6 - (0.6 if a > 0.35 else 0) + (0.8 if ((Y * 2.6) % 1 < 0.14) else 0) + (0.5 if h < 0.3 else 0)
        return fz(tone(SLATE, v + (wn(1, X * 3, Y) - 0.5) * 0.5, x, y), z)
    rs.quad((tcx - 2.3, HB, ZT + 2.0), (tcx + 2.3, HB, ZT + 2.0), (tcx - 2.3, HB + 3.6, ZT + 2.0), helmet, cls='wall', cut=True)
place_windows([w_ for w_ in WINS if w_[4] in (ZW, ZPV, ZC)])

# ---------------------------------------------------------------------------------------------------- the Stomach Clock
NUMERALS = ['XII', 'I', 'II', 'III', 'IIII', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI']
GLYPH = {'I': ['1', '1', '1', '1', '1'], 'V': ['101', '101', '101', '101', '010'], 'X': ['101', '101', '010', '101', '101']}
NUMS = []
for i, n in enumerate(NUMERALS):
    a = math.radians(90 - i * 30)
    NUMS.append((R_FACE * 0.77 * math.cos(a), R_FACE * 0.77 * math.sin(a), a, n, sum(len(GLYPH[c][0]) + 1 for c in n) - 1))
CELL = 0.24
def on_numeral(X, Y):
    for (cxn, cyn, a, n, wpx) in NUMS:
        dx, dy = X - cxn, Y - cyn
        if dx * dx + dy * dy > 2.0: continue
        r_ = -(a - math.pi / 2)                                                             # upright towards the centre
        u = dx * math.cos(r_) - dy * math.sin(r_); v = dx * math.sin(r_) + dy * math.cos(r_)
        gx = int(math.floor(u / CELL + wpx / 2)); gy = int(math.floor(2.5 - v / CELL))
        if not (0 <= gy < 5 and 0 <= gx < wpx): continue
        cx_ = 0
        for c in n:
            gw = len(GLYPH[c][0])
            if cx_ <= gx < cx_ + gw: return GLYPH[c][gy][gx - cx_] == '1'
            cx_ += gw + 1
    return False
HOUR_A, MIN_A = math.radians(90 - 4.7 * 30), math.radians(90 - 41 * 6)              # twenty to five
def hand_d(X, Y, ang, length, w0):
    """across/along a tapered, sagging sinew hand, or None"""
    ca, sa = math.cos(ang), math.sin(ang)
    al = X * ca + Y * sa; ac = -X * sa + Y * ca
    if al < -0.8 or al > length: return None
    ac -= 0.12 * math.sin(max(0.0, al) / length * math.pi) * length * 0.15
    wdt = w0 * (1.0 - 0.75 * max(0.0, al) / length) + (0.14 if -0.8 < al < 0.2 else 0)
    if abs(ac) > wdt: return None
    return ac / wdt, al / length
def face(x, y, s, t, z, wp):
    X, Y, Z = wp
    X -= CLK[0]; Y -= CLK[1]
    r = math.hypot(X, Y)
    if r > R_FACE: return None
    for (ang, ln, w0, seed) in ((MIN_A, R_FACE * 0.86, 0.3, 1), (HOUR_A, R_FACE * 0.58, 0.42, 2)):
        h_ = hand_d(X, Y, ang, ln, w0)
        if h_:
            ac, al = h_
            v = 3.4 - ac * 2.2 + (1.2 if -0.55 < ac < -0.25 else 0) - (0.9 if (al * 9 + seed) % 1 < 0.12 else 0)
            c = tone(SINEW, v, x, y)
            if -0.6 < ac < -0.35 and (al * 13) % 1 < 0.5: c = mix(c, WET, 0.4)                # a wet glint along it
            return c
    if r < 0.65: return tone(BRASS, 4.4 - (X + Y) * 1.6, x, y)                        # the boss
    v = 5.8 - r / R_FACE * 1.4 + (wn(0, X * 0.6, Y * 0.6) - 0.5) * 1.8 + (wn(1, X * 3, Y * 3) - 0.5) * 0.5
    v -= 1.0 * max(0.0, -Y / R_FACE) ** 2                                              # its lower half in the stomach's shadow
    if R_FACE * 0.92 < r < R_FACE * 0.95 or R_FACE * 0.6 < r < R_FACE * 0.62: v -= 1.6  # the chapter rings
    a = (math.degrees(math.atan2(Y, X)) % 360) / 6.0
    if R_FACE * 0.88 < r < R_FACE * 0.95 and a % 1 < 0.14: v -= 1.8                   # minute ticks
    if on_numeral(X, Y): return tone(SINEW, 1.6 + (0.6 if (x + y) % 3 == 0 else 0), x, y)
    if wn(3, X * 0.9 + 11, Y * 0.9) > 0.6 and abs(wn(2, X * 2.4 + 40, Y * 1.2) - 0.5) < 0.016: v -= 3.0   # hairline cracks in the bone
    m = wn(2, X * 0.5 + 3, Y * 0.5)
    c = tone(BONE, v, x, y)
    if m > 0.62: c = mix(c, (74, 58, 34), min(0.5, (m - 0.62) * 3))                    # old yellow-brown stains
    if r > R_FACE * 0.97: c = mix(c, (30, 22, 16), 0.5)
    return c
def bezel(x, y, s, t, z, wp):
    X, Y, Z = wp
    X -= CLK[0]; Y -= CLK[1]
    r = math.hypot(X, Y)
    if r < R_FACE - 0.05 or r > R_BEZ: return None
    a = math.atan2(Y, X)
    k = (r - R_FACE) / (R_BEZ - R_FACE)
    v = 3.3 + math.sin(a + 0.9) * 1.3 + (1.0 if 0.35 < k < 0.55 else -0.6 if k > 0.8 else 0)
    if (math.degrees(a) % 15) < 1.4 and 0.3 < k < 0.7: v += 1.4                         # rivets
    c = tone(BRASS, v, x, y)
    if wn(3, a * 4, r) > 0.58: c = mix(c, VERD[4], 0.5)                                  # verdigris
    return c
rs.quad((CLK[0] - R_FACE, CLK[1] - R_FACE, CLK[2]), (CLK[0] + R_FACE, CLK[1] - R_FACE, CLK[2]), (CLK[0] - R_FACE, CLK[1] + R_FACE, CLK[2]), face, cls='prop', cut=True)
rs.quad((CLK[0] - R_BEZ, CLK[1] - R_BEZ, CLK[2] - 0.3), (CLK[0] + R_BEZ, CLK[1] - R_BEZ, CLK[2] - 0.3), (CLK[0] - R_BEZ, CLK[1] + R_BEZ, CLK[2] - 0.3), bezel, cls='prop', cut=True)

LIGHT = (-0.45, 0.62, -0.64)                                                           # towards the light: up-left, a little from the front
def lam(n): return max(0.0, n[0] * LIGHT[0] + n[1] * LIGHT[1] + n[2] * LIGHT[2])
def flesh(v, x, y, n, glint, dark_edge):
    c = tone(GUT, v, x, y)
    l_ = lam(n)
    if l_ > 0.86 and glint: c = mix(c, WET, min(0.5, (l_ - 0.86) * 4.5))               # wet
    if dark_edge: c = mix(c, (16, 8, 8), 0.45)
    return c
def gut_ring():
    """the stomach wall around the face: a thick, lumpy, muscular torus bulging out of the facade, with rugae (folds)
    running across it, veins, a wet sheen; drawn per pixel into the raster with its own bulge depth"""
    obj = rs.obj()
    Rm, hw = (R_BEZ + R_GUT) / 2, (R_GUT - R_BEZ) / 2
    x0, x1 = int(sx(-R_GUT - 2.0, ZG0)), int(sx(R_GUT + 2.0, ZG0)) + 1
    y0, y1 = int(sy(CLK[1] + R_GUT + 2.0, ZG0)), int(sy(CLK[1] - R_GUT - 2.4, ZG0)) + 1
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            dx_, dy_ = ray(x, y)
            Zp = CLK[2] - 1.0
            X, Y = dx_ * Zp - CLK[0], (CAMH + dy_ * Zp) - CLK[1]
            r = math.hypot(X, Y); a = math.atan2(Y, X)
            ca, sa = math.cos(a), math.sin(a)
            lump = 0.6 * (wn(0, ca * 2.4 + 20, sa * 2.4) - 0.5) + 0.4 * (wn(1, ca * 6 + 9, sa * 6) - 0.5)
            hwl = hw * (1.0 + lump * 0.7)
            Rml = Rm + lump * 0.6 + 0.6 * max(0.0, -sa) ** 3                               # it sags at the bottom
            u = (r - Rml) / hwl
            if abs(u) > 1: continue
            hgt = math.sqrt(1 - u * u)
            Z = CLK[2] - 0.25 - hgt * (CLK[2] - ZG0) * (1 + lump * 0.5)
            n = (u * ca * 0.9, u * sa * 0.9, -hgt)
            nl = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2); n = (n[0] / nl, n[1] / nl, n[2] / nl)
            warp = wn(2, ca * 3.0 + r * 0.8, sa * 3.0 + 7.0) * 2.6 + wn(1, ca * 7.0 + 3.0, sa * 7.0 + r) * 0.9
            fold = (a * 13.0 / math.pi + warp + u * u * 0.7) % 1                            # rugae across the ring
            vein = abs(wn(0, ca * 8 + 70, sa * 8 + r * 0.7) - 0.5)
            mot = wn(3, ca * 4 + 50, sa * 4 + r)
            def sh(x, y, s, t, z, wp, u=u, hgt=hgt, n=n, fold=fold, vein=vein, mot=mot):
                v = 1.5 + 4.6 * lam(n) + (0.5 if fold < 0.34 else -1.3 if fold > 0.86 else -0.4 if fold > 0.74 else 0) + (mot - 0.5) * 1.8
                c = flesh(v, x, y, n, fold < 0.55 and (x * 7 + y * 3) % 5, abs(u) > 0.9)
                if vein < 0.022 and hgt > 0.3: c = mix(c, (58, 30, 46), 0.55)                 # bluish veins
                return c
            rs.put(x, y, Z, sh, obj, a, u, (X + CLK[0], Y + CLK[1], Z), n, 'prop')
    return obj
gut_ring()

def tube(pts, r0, r1, seed, lip=False, folds=70.0):
    """a gut-tube along a Catmull-Rom path in world units, tapering from r0 to r1: annular folds, a wet highlight on
    the lit side, a dark underside; written per pixel with a cylindrical bulge depth"""
    obj = rs.obj()
    P = [pts[0]] + list(pts) + [pts[-1]]
    path = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        seg = max(4, int(math.dist(proj(*p1), proj(*p2)) * 1.5))
        for k in range(seg):
            t = k / seg
            path.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t +
                                     (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t * t * t) for j in range(3)))
    path.append(pts[-1])
    L = len(path)
    for i, Pw in enumerate(path):
        tt = i / (L - 1)
        rad = r0 + (r1 - r0) * tt ** 0.7
        rad *= 1.0 + 0.14 * math.sin(tt * 34 + seed) + 0.12 * (wn(1, tt * 9 + seed * 3, 2.0) - 0.5)
        if lip and tt > 0.96: rad *= 1.3                                                    # a puckered mouth at the end
        Q = path[min(L - 1, i + 1)]; Pp = path[max(0, i - 1)]
        (ax_, ay_), (bx_, by_) = proj(*Pp), proj(*Q)
        tx, ty = bx_ - ax_, by_ - ay_; tl = math.hypot(tx, ty) or 1.0
        tx, ty = tx / tl, ty / tl; nx_, ny_ = -ty, tx
        (cx_, cy_) = proj(*Pw); rr = max(0.7, rad * F / Pw[2])
        for y in range(int(cy_ - rr) - 1, int(cy_ + rr) + 2):
            for x in range(int(cx_ - rr) - 1, int(cx_ + rr) + 2):
                ddx, ddy = x + 0.5 - cx_, y + 0.5 - cy_
                if ddx * ddx + ddy * ddy > rr * rr: continue
                a = (ddx * nx_ + ddy * ny_) / rr
                if abs(a) > 1: continue
                hgt = math.sqrt(max(0.0, 1 - a * a))
                nrm = (a * nx_, -a * ny_, -hgt)
                def sh(x, y, s, t, z, wp, a=a, nrm=nrm, tt=tt):
                    ring = (tt * folds + seed) % 1
                    v = 1.4 + 4.2 * lam(nrm) - (1.0 if ring < 0.18 else 0) + (wn(2, tt * 20 + seed, a) - 0.5) * 1.0
                    return flesh(v, x, y, nrm, ring > 0.35, abs(a) > 0.86)
                rs.put(x, y, Pw[2] - hgt * rad * 0.8, sh, obj, a, tt, Pw, nrm, 'prop')
    return obj

ZTB = ZC - 0.8                                                                          # tubes lie just off the facade
cy0 = CLK[1]
tube([(-8.0, cy0 - 5.0, ZG0 + 1.0), (-9.3, cy0 - 8.4, ZTB), (-9.7, GF + 3.6, ZTB), (-10.4, GF + 2.6, ZTB - 0.2), (-11.6, GF + 1.6, ZT - 0.6)], 1.2, 0.42, 1)
tube([(-4.6, cy0 - 8.2, ZG0 + 0.8), (-5.1, GF + 3.2, ZTB), (-5.6, PB + 2.0, ZC - 1.4), (-5.9, PB + 0.4, ZC - 1.5), (-6.4, ENT - 1.8, ZC - 1.1)], 1.0, 0.36, 2, lip=True)
tube([(1.6, cy0 - 9.4, ZG0 + 0.6), (2.0, PB + 2.6, ZC - 1.3), (3.0, PB + 2.3, ZC - 1.4), (4.2, PB + 1.2, ZC - 1.4)], 0.75, 0.3, 3)
tube([(5.6, cy0 - 7.6, ZG0 + 0.8), (6.6, GF + 4.2, ZTB), (8.0, GF + 2.0, ZTB), (8.6, GF - 1.0, ZTB), (8.4, GF - 2.2, ZTB)], 0.95, 0.3, 4, lip=True)
tube([(8.8, cy0 - 3.0, ZG0 + 1.0), (10.4, cy0 - 6.2, ZTB), (11.4, GF + 5.4, ZT - 0.6), (12.4, GF + 3.2, ZT - 0.5), (13.4, GF + 2.2, ZT - 0.7), (15.2, GF + 1.8, ZT - 0.6)], 1.1, 0.42, 5)
tube([(-9.4, cy0 + 2.4, ZG0 + 1.0), (-11.2, cy0 + 5.0, ZT - 0.5), (-12.3, TCOR + 0.4, ZT - 0.9), (-13.3, TCOR + 1.3, ZT - 1.1), (-14.5, TCOR + 1.6, ZT - 0.4)], 0.9, 0.32, 6)
tube([(9.0, cy0 + 3.4, ZG0 + 1.0), (10.6, cy0 + 6.8, ZT - 0.6), (11.2, TCOR + 1.0, ZT - 1.1), (12.3, TCOR + 1.5, ZT - 0.6)], 0.75, 0.3, 7)
tube([(-8.4, cy0 - 7.0, ZG0 + 0.9), (-10.6, GF + 5.2, ZT - 0.5), (-12.4, GF + 2.6, ZT - 0.6), (-13.0, 7.6, ZT - 0.4), (-13.0, 5.0, ZT - 0.4)], 0.5, 0.28, 8)
# veins: thin capillaries creeping out over the stones from the ring
for k, (a0, ln, sd) in enumerate(((195, 5.0, 11), (165, 4.2, 12), (15, 4.6, 13), (-25, 3.8, 14), (218, 3.6, 15), (322, 3.4, 16), (248, 3.0, 17), (292, 3.2, 18), (345, 3.0, 19))):
    a = math.radians(a0); pts = []
    for j in range(5):
        rr_ = R_GUT - 0.6 + ln * j / 4
        aa = a + (wn(1, j * 0.7 + sd, 1.0) - 0.5) * 0.5
        pts.append((rr_ * math.cos(aa), CLK[1] + rr_ * math.sin(aa), ZC - 0.25))
    tube(pts, 0.34, 0.1, sd, folds=24.0)
# the bile tap and its basin on the podium's left corner
rs.line3((-13.0, 4.9, ZT - 0.4), (-13.0, 4.4, ZT - 1.1), lambda x, y, s, t, z, wp: tone(BRASS, 4.4 - t * 2, x, y), w=0.3)
rs.line3((-13.0, 4.35, ZT - 1.15), (-13.0, 3.6, ZT - 1.15), lambda x, y, s, t, z, wp: BILE[4] if (y % 3) else BILE[5], w=0.11)
def basin_front(x, y, s, t, z, wp):
    return fz(tone(DRESS, 4.4 + (0.9 if t > 0.8 else 0) - (1.0 if t < 0.2 else 0) - abs(s - 0.5) * 1.2, x, y), z)
rs.box(-14.2, -11.8, PODIUM, PODIUM + 1.0, ZT - 2.0, ZT, basin_front, basin_front,
       top=lambda x, y, s, t, z, wp: tone(BILE, 3.0 + (0.8 if (x + y) % 4 == 0 else 0), x, y) if 0.12 < s < 0.88 and 0.15 < t < 0.85 else fz(tone(DRESS, 5.0, x, y), z), cls='prop')
rs.box(-13.6, -12.4, 0, PODIUM, ZT - 1.6, ZT - 0.2, basin_front, basin_front, cls='prop')

# ---------------------------------------------------------------------------------------------------- railings on stone piers
def pier(X, Z, h=6.4):
    rs.box(X - 0.7, X + 0.7, 0, h, Z - 0.7, Z + 0.7, cheek(4.0), cheek(3.0), cls='wall')
    rs.box(X - 0.9, X + 0.9, h, h + 0.42, Z - 0.9, Z + 0.9, coping, coping, top=coping, cls='prop')
    rs.disc(X, h + 1.0, Z, 0.52, lambda x, y, s, t, z, wp: fz(tone(DRESS, 5.4 - s * 1.2 - t * 1.6, x, y), z))
def railing(x0, x1, Z):
    rs.box(x0, x1, 0, 1.0, Z - 0.4, Z + 0.4, cheek(3.6), cheek(3.0), top=coping, cls='wall')
    def bars(x, y, s, t, z, wp):
        X, Y, _ = wp
        if 4.7 < Y < 4.98 or 1.5 < Y < 1.78: return fz(tone(IRON, 2.6, x, y), z)
        u = (X / 0.52) % 1
        top = 5.6 + (0.42 * (1 - abs(u - 0.5) * 6) if abs(u - 0.5) < 0.17 else 0)
        if Y > top: return None
        if abs(u - 0.5) < max(0.11, (z / F) / 0.52 * 0.7): return fz(tone(IRON, 2.2 + (1.0 if u < 0.5 else 0) + (1.4 if Y > 5.6 else 0), x, y), z)
        return None
    rs.quad((x0, 1.0, Z), (x1, 1.0, Z), (x0, 6.2, Z), bars, cls='prop', cut=True)
ZR_ = ZC + 0.6
for sgn in (-1, 1):
    pts_ = [sgn * 37.0, sgn * 44.5, sgn * 52.0, sgn * 59.5]
    for a_, b_ in zip(pts_, pts_[1:]):
        railing(min(a_, b_) + 0.7, max(a_, b_) - 0.7, ZR_)
    for p_ in pts_: pier(p_, ZR_)

# ---------------------------------------------------------------------------------------------------- the street lamp (left; Sconce stands on the right)
def lamp(X, Z, Hh=LAMP_H):
    k = Hh / 13.2
    def iron(v0):
        return lambda x, y, s, t, z, wp: fz(tone(IRON, v0 + (1.2 if wp is not None and wp[0] < X - 0.1 else 0), x, y), z)
    rs.box(X - 0.85, X + 0.85, 0, 0.5 * k, Z - 0.85, Z + 0.85, iron(2.0), iron(1.4), top=iron(3.0), cls='prop')
    def pedestal(x, y, s, t, z, wp):
        u = (wp[0] - X) / 0.66
        if abs(u) > 1: return None
        fl = (u * 3 + 3) % 1
        return fz(tone(IRON, 2.6 - u * 1.2 - (0.8 if fl < 0.25 else 0) + (0.8 if (wp[1] % 1.0) > 0.86 else 0), x, y), z)
    rs.quad((X - 0.66, 0.5 * k, Z - 0.7), (X + 0.66, 0.5 * k, Z - 0.7), (X - 0.66, 3.5 * k, Z - 0.7), pedestal, cls='prop', cut=True)
    rs.box(X - 0.8, X + 0.8, 3.5 * k, 3.85 * k, Z - 0.8, Z + 0.8, iron(2.6), iron(1.6), cls='prop')
    rs.line3((X, 3.85 * k, Z), (X, 9.8 * k, Z), lambda x, y, s, t, z, wp: fz(tone(IRON, 2.4 + (1.2 if x < sx(X, Z) else 0), x, y), z), w=0.4)
    rs.box(X - 0.45, X + 0.45, 6.6 * k, 7.0 * k, Z - 0.45, Z + 0.45, iron(2.6), iron(1.6), cls='prop')
    rs.box(X - 0.6, X + 0.6, 9.8 * k, 10.2 * k, Z - 0.6, Z + 0.6, iron(2.6), iron(1.6), cls='prop')
    def lantern(x, y, s, t, z, wp):
        if abs(s - 0.5) < 0.05 or abs(s - 0.2) < 0.05 or abs(s - 0.8) < 0.05 or t < 0.07 or t > 0.93: return IRON[1]
        return ri(GLOW, band(3.0 - abs(s - 0.5) * 2 + t * 0.8, x, y))
    rs.box(X - 1.05, X + 1.05, 10.2 * k, 12.0 * k, Z - 0.85, Z + 0.85, lantern, lambda x, y, s, t, z, wp: ri(GLOW, band(1.8, x, y)), cls='emit')
    rs.box(X - 1.45, X + 1.45, 12.0 * k, 12.35 * k, Z - 1.1, Z + 1.1, iron(2.6), iron(1.6), bottom=iron(1.0), cls='prop')
    rs.disc(X, 12.7 * k, Z, 1.0, lambda x, y, s, t, z, wp: fz(tone(IRON, 3.0 - s * 1.0 - t * 1.2, x, y), z) if t < 0.3 else None)
lamp(-LAMP_X, LAMP_Z)

# ---------------------------------------------------------------------------------------------------- an advertising column pasted with edicts
def edict_column(X, Z, r=1.35, h=8.4):
    """a dark green iron advertising column with a copper cap; edicts, forms and a faded poster pasted on it"""
    NOTE = []
    for k in range(14):
        ang = -1.3 + (h32(k, 61) % 260) / 100.0
        Yc = 1.4 + (h32(k, 62) % 560) / 100.0
        NOTE.append((ang, Yc, 0.22 + (h32(k, 63) % 3) * 0.08, 0.5 + (h32(k, 64) % 4) * 0.18, k))
    def sh(x, y, s, t, z, wp):
        Xw, Y, _ = wp
        u = (Xw - X) / r
        if abs(u) > 1: return None
        shade = -abs(u) ** 2 * 1.8 - (0.6 if u > 0 else 0)
        if Y < 0.7: return fz(tone(ASH, 3.6 + shade, x, y), z)                                # the stone foot
        if Y > h - 0.9:
            if Y > h - 0.45 and abs(u) > 0.92 - (Y - h + 0.45) * 1.4: return None
            return fz(tone(VERD, 4.2 + shade + (0.7 if Y > h - 0.5 else 0), x, y), z)        # the copper cap
        if abs(Y - (h - 1.2)) < 0.15 or abs(Y - 1.0) < 0.15: return fz(tone(VERD, 3.6 + shade, x, y), z)   # rings
        ang = math.asin(max(-1.0, min(1.0, u)))
        for (a0, Yc, aw, hh, k) in NOTE:
            if abs(ang - a0) < aw and abs(Y - Yc) < hh / 2:
                fu = (ang - a0 + aw) / (2 * aw); fv = (Y - Yc + hh / 2) / hh
                if k % 5 == 0 and fu + fv * 0.3 > 1.0: break                                 # torn
                pc = tone(PAPER, 2.4 + shade + (wn(1, Xw * 5, Y * 3) - 0.5) * 0.6 - (k % 3) * 0.4, x, y)
                if k % 4 == 2: pc = mix(pc, (98, 50, 38), 0.5)                               # a faded red poster
                if 0.14 < fu < 0.86 and (fv * 8) % 1 < 0.3 and 0.12 < fv < 0.72: pc = tone(PAPER, 0.6 + shade, x, y)
                if k % 3 == 1 and math.hypot(fu - 0.72, fv - 0.86) < 0.11: pc = (108, 34, 28)     # a seal
                if wn(2, Xw * 3, Y) > 0.62: pc = mix(pc, (34, 34, 26), 0.4)                   # rain-soaked
                return fz(pc, z)
        return fz(tone(VERD, 2.0 + shade + (wn(0, Xw * 2, Y * 0.6) - 0.5) * 0.8, x, y), z)
    rs.quad((X - r, 0, Z), (X + r, 0, Z), (X - r, h + 0.6, Z), sh, cls='prop', cut=True)
edict_column(-21.0, 41.0)

# ---------------------------------------------------------------------------------------------------- stray forms on the square
for k in range(16):
    fx_, fzz = -36 + (h32(k, 41) % 720) / 10.0, 25.0 + (h32(k, 42) % 210) / 10.0
    if abs(fx_) < 6.5 and fzz > ZS0 - 1: continue
    sk = (h32(k, 43) % 60 - 30) / 100.0
    rs.quad((fx_ - 0.4, 0.03, fzz - 0.3 + sk), (fx_ + 0.4, 0.03, fzz - 0.3 - sk), (fx_ - 0.4, 0.03, fzz + 0.3 + sk),
            lambda x, y, s, t, z, wp: fz(tone(PAPER, 2.8 + (0.8 if (x + y) % 5 else -0.6) - (0.8 if (t * 5) % 1 < 0.2 and 0.2 < s < 0.8 else 0), x, y), z), cls='ground')

# ---------------------------------------------------------------------------------------------------- render
img = rs.render(INK, fog=fog_of, mirror=lambda x, y, wp: 0.65 * puddle(wp[0], wp[2]),
                light_gain=1.1, grime_gain=1.4, bloom=0.4, stain_gain=1.5, damp_gain=0.45)
img.save(os.path.join(OUT, 'townhall.png'))

# the fixed points the scene uses (canvas coordinates)
door_poly = [(round(sx(DX, ZD)), round(sy(PODIUM, ZD)))]
for k in range(0, 13):
    a = math.pi * k / 12
    door_poly.append((round(sx(DX * math.cos(a), ZD)), round(sy(DSPR + DX * math.sin(a), ZD))))
door_poly.append((round(sx(-DX, ZD)), round(sy(PODIUM, ZD))))
FIXED = {
    'door_poly': door_poly,
    'stair_foot_y': round(sy(0, ZS0)), 'stair_x': (round(sx(-SXH - 1.0, ZS0)), round(sx(SXH + 1.0, ZS0))),
    'clock_centre': (round(sx(CLK[0], CLK[2])), round(sy(CLK[1], CLK[2]))),
    'clock_r_px': round(R_GUT * F / ZG0),
    'lamp_left_feet': (round(sx(-LAMP_X, LAMP_Z)), round(sy(0, LAMP_Z))),
    'sconce_feet': (round(sx(LAMP_X, LAMP_Z)), round(sy(0, LAMP_Z))),
    'lamp_height_px': round(13.7 * F / LAMP_Z),
    'basin': (round(sx(-13.0, ZT)), round(sy(PODIUM + 1.0, ZT))),
    'wing_x': (round(sx(-XW, ZW)), round(sx(XW, ZW))),
    'column_feet': (round(sx(-21.0, 41.0)), round(sy(0, 41.0))),
}
json.dump(FIXED, open(os.path.join(OUT, 'fixed.json'), 'w'), indent=1)
print('done townhall', FIXED)
