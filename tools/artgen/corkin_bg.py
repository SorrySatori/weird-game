"""Inside the Screaming Cork (ScreamingCorkInteriorScene), 1067x600, the shared camera (raster3d.py). After the old
art (ScreamingCorkInterior.png): a tall, dark timber taproom. On the back wall a great stuffed cephalopod spreads its
arms over the name in red light; under it the back bar -- shelves of bottles before a clouded mirror; in front of it
the long counter, behind which Heliodor stands (the counter is also written out as an overlay, counter.png, so the
scene can draw it over him). Left wall: the door to the street (the exit left); back wall: a kitchen door with a
porthole, a coiled tentacle and a framed bottle; at the back right the doorway with the stairs down to the club, lit
red from below, a Feral Toast bill beside it. Round tables with stools, lanterns on chains, a corner on the right with
Ravla's little desk and candle. Corks underfoot.

    python3 corkin_bg.py <outdir>   ->  corkin.png (+ counter.png, the counter over everything behind it)
Heliodor stands at z ~17.4 on the raised boards behind the bar, before the curtained doorway; counter.png holds
what is nearer than him inside his sprite's box.
Fixed points (canvas): exit door x ~35..117 (left wall); the club doorway x ~817..882, y ~321..425; Heliodor behind
the counter at (533, 492) origin bottom; Ravla in the right corner at (960, 524); the walk line y 534."""
import sys, os, math
from PIL import Image, ImageDraw, ImageFont
from common import h32, draw_text, text_width
from shedkit import *
from rig import Rig, Mat
from feral_toast import ik

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = Raster()
WX, CH, ZB = 34.0, 34.0, 28.0
def fog(z): return max(0.0, min(0.3, (z - 16) / 70.0))
FOGI = (22, 24, 18)
def fg(c, z): return mix(c, FOGI, fog(z))
TIMBER = ramp('#100d09 #18140d #211b12 #2b2318 #362c1f #423627 #504230 #5f4f3a')
FLOORW = ramp('#120e09 #1a150e #231c13 #2d2419 #382d20 #443728 #514231')
OCTO = ramp('#1a0a08 #2c120e #421a14 #5a241a #723022 #8a3e2c #a0503a #b8664a')
BRASS = ramp('#2e200c #4a3414 #6a4c1e #8c682a #ae883c #ccaa5a')
NEON = ramp('#5a1018 #8a1a26 #c02a3a #e8506a #ff8aa0 #ffd0da')
GLASSC = [ramp('#0c1a10 #14301c #1e4a2a #2c663a'), ramp('#1e1008 #34200e #4e3216 #6a4620'), ramp('#2a1a08 #4a3010 #6e4c1a #946a28'),
          ramp('#141614 #222624 #343a36 #4a524c'), ramp('#0e1a12 #18301e #24462c #33603c'), ramp('#1c0e12 #2e161c #422028 #582c36')]
BREW = ramp('#1a3a14 #2a5a1c #44842a #6aae3e #9cd866')                             # Heliodor's glowing brew
CORKC = ramp('#2a2016 #42331f #5c4a2e #76603c #8e774c #a48d60')

# ---------------------------------------------------------------------------------------------------- materials
def boards(v0, r=TIMBER, w=0.8, along='x', seed=0, batten=True):
    """vertical boards on a wall: along x (back wall) or along z (side walls); dark joints, battens, grime at the foot"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = X if along == 'x' else Z
        pl = math.floor(u / w); fu = u / w - pl
        v = v0 + (h32(pl, seed, 1) % 3) * 0.3 - 0.6 * (wn(0, u * 0.5, Y * 2.5) - 0.5) - 0.9 * max(0.0, 1 - Y / 2.4)
        px = (z / F if along == 'x' else z * z / (F * max(1.0, abs(X)))) / w
        if batten and fu < max(0.12, 1.3 * px): v += 0.6 if fu < max(0.06, 0.7 * px) else -0.5
        elif fu < 0.9 * px + 0.02: v -= 1.0
        if h32(pl, int(Y * 1.7), seed) % 31 == 0: v -= 0.9
        return fg(tone(r, v, x, y), z)
    return sh
def wainscot(v0, along='x'):
    """horizontal boards on the lower wall, a capping rail"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        if Y > 4.3: return fg(tone(TIMBER, v0 + 1.4 - (Y - 4.3) * 3, x, y), z)
        row = math.floor(Y / 0.6)
        v = v0 + (h32(row, 3) % 3) * 0.3 - (1.2 if (Y / 0.6) % 1 < 0.12 else 0) - 0.8 * max(0.0, 1 - Y / 1.6)
        return fg(tone(TIMBER, v, x, y), z)
    return sh
def floor_sh(x, y, s, t, z, wp):
    """wide old planks running into the room, worn pale along the path from the door to the bar, stains"""
    X, _, Z = wp
    pl = math.floor(X / 1.1); fu = X / 1.1 - pl
    v = 3.0 + (h32(pl, 5) % 3) * 0.3 + (wn(0, X * 0.4, Z * 1.6) - 0.5) * 0.8
    seg = math.floor(Z / (5.0 + h32(pl, 6) % 4))
    if fu < 0.9 * z / F / 1.1 + 0.03: v -= 1.2                                       # joints
    if ((Z / (5.0 + h32(pl, 6) % 4)) % 1) < 0.9 * z * z / (F * CAMH) / 5.0 + 0.01: v -= 0.9   # butt ends
    if abs(Z - 15.2 - (X + 30) * 0.02) < 1.4: v += 0.5 * (1 - abs(Z - 15.2) / 1.4)  # the trodden lane along the bar
    m = wn(2, X * 0.25 + 3, Z * 0.35)
    c = tone(FLOORW, v, x, y)
    if m > 0.7: c = mix(c, (20, 14, 10), min(0.5, (m - 0.7) * 4))                  # old spills
    return fg(c, z)
def bottle(seed, glow=False):
    """a bottle silhouette on a quad: body, shoulder, neck, a cork; colour per seed"""
    r = GLASSC[seed % len(GLASSC)]
    kind = h32(seed, 3) % 3
    def sh(x, y, s, t, z, wp):
        u = abs(s - 0.5) * 2
        neck = 0.24 if kind else 0.3
        sh_t = [0.62, 0.55, 0.72][kind]
        if t > 0.92: return CORKC[3] if u < neck * 0.9 else None
        if t > sh_t:
            w_ = neck + (1 - neck) * max(0.0, 1 - (t - sh_t) / 0.12) ** 2
            if u > w_: return None
        v = 2.6 - u * 1.6 + (1.4 if 0.25 < s < 0.38 and t < sh_t else 0)
        if glow: return ri(BREW, band(3.2 - u * 1.8 + (0.8 if t < sh_t * 0.6 else 0), x, y))
        if 0.2 < t < 0.45 and u < 0.7 and kind != 2: return mix(tone(CORKC, 4.4, x, y), r[2], 0.3)   # a label
        return ri(r, band(v, x, y))
    return sh

# ---------------------------------------------------------------------------------------------------- the shell
rs.quad((-WX, 0, 3), (WX, 0, 3), (-WX, 0, ZB), floor_sh, cls='ground')
def back_wall(x, y, s, t, z, wp):
    X, Y, Z = wp
    if Y < 4.6: return wainscot(2.4)(x, y, s, t, z, wp)
    if abs(Y - 14.0) < 0.3: return fg(tone(TIMBER, 3.6 + (0.6 if Y > 14.1 else 0), x, y), z)        # a picture rail
    return boards(2.3, seed=1)(x, y, s, t, z, wp)
rs.quad((-WX, 0, ZB), (WX, 0, ZB), (-WX, CH, ZB), back_wall, cls='wall')
def side_wall(sign):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        if sign < 0 and 20.6 < Z < 24.4 and Y < 8.4: return None                      # the street doorway
        if Y < 4.6: return wainscot(2.2, 'z')(x, y, s, t, z, wp)
        return boards(2.1, along='z', seed=2 + sign)(x, y, s, t, z, wp)
    return sh
rs.quad((-WX, 0, 3), (-WX, 0, ZB), (-WX, CH, 3), side_wall(-1), cls='wall', cut=True)
rs.quad((WX, 0, 3), (WX, 0, ZB), (WX, CH, 3), side_wall(1), cls='wall')
rs.quad((-WX, CH, 3), (WX, CH, 3), (-WX, CH, ZB), lambda x, y, s, t, z, wp: fg(tone(TIMBER, 1.2 + (0.5 if (wp[0] / 0.9) % 1 < 0.5 else 0), x, y), z), cls='ceil')
for zb in (22.6, 25.2, 27.4):                                                      # the great beams
    rs.box(-WX, WX, CH - 1.8, CH, zb, zb + 0.9, lambda x, y, s, t, z, wp: fg(tone(TIMBER, 2.2, x, y), z), lambda x, y, s, t, z, wp: fg(TIMBER[1], z),
           bottom=lambda x, y, s, t, z, wp: fg(tone(TIMBER, 1.6 + (wn(0, wp[0] * 0.6, 2) - 0.5), x, y), z), cls='ceil')
for X in (-30.5, 30.5):                                                            # posts holding them
    rs.box(X - 0.6, X + 0.6, 0, CH - 1.8, 24.6, 25.8, lambda x, y, s, t, z, wp: fg(tone(TIMBER, 2.6 + (0.6 if s < 0.25 else 0) - (0.6 if s > 0.8 else 0), x, y), z),
           lambda x, y, s, t, z, wp: fg(tone(TIMBER, 1.8, x, y), z), cls='wall')

# ---------------------------------------------------------------------------------------------------- the back wall: doors, trophies
def arched(cx, w2, sp, inner):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        d = math.hypot(X - cx, max(0.0, Y - sp))
        if abs(X - cx) > w2 or (Y >= sp and d > w2):
            a = math.degrees(math.atan2(Y - sp, X - cx)) / 20 if Y >= sp else Y / 1.4
            return fg(tone(TIMBER, 3.6 + (h32(int(a), 5) % 3) * 0.3 - (1.0 if a % 1 < 0.12 else 0), x, y), z)
        return inner(x, y, X, Y, z)
    return sh
def kitchen_door(x, y, X, Y, z):
    cx = -24.0
    if math.hypot(X - cx, Y - 6.2) < 0.95: return GLOW[1] if math.hypot(X - cx, Y - 6.2) < 0.75 else BRASS[3]   # the porthole
    v = 2.2 + (h32(int((X - cx) / 0.7 + 10), 6) % 3) * 0.3 - (1.1 if ((X - cx) / 0.7) % 1 < 0.1 else 0)
    if abs(Y - 2.2) < 0.12 or abs(Y - 7.6) < 0.12: v = 3.8
    if abs(X - cx - 1.8) < 0.18 and abs(Y - 4.0) < 0.18: return BRASS[4]
    return tone(TIMBER, v, x, y)
rs.quad((-27.6, 0, ZB - 0.05), (-20.4, 0, ZB - 0.05), (-27.6, 10.2, ZB - 0.05), arched(-24.0, 3.0, 7.0, kitchen_door), cls='prop', cut=False)
def club_doorway(x, y, s, t, z, wp):
    """the doorway to the club: steps going down into red light, a handrail"""
    X, Y, Z = wp
    cx, w2, top = 29.5, 2.9, 9.4
    if abs(X - cx) > w2 or Y > top:
        return fg(tone(TIMBER, 1.6 + (0.8 if Y > top + 0.25 or abs(X - cx) > w2 + 0.25 else 0), x, y), z)
    u, v = (X - cx) / w2, Y / top
    step = math.floor(v * 7)
    k = (1 - v) ** 1.6
    if (v * 7) % 1 < 0.16 and v < 0.75: return mix((120, 30, 26), (230, 92, 60), k)               # the lit nosing of a step
    if abs(u + 0.72) < 0.05 and v < 0.85: return BRASS[2]                                           # a handrail
    return mix((14, 6, 6), (150, 36, 30), k * 0.9 * (1 - abs(u) * 0.4))
rs.quad((26.0, 0, ZB - 0.05), (33.0, 0, ZB - 0.05), (26.0, 10.2, ZB - 0.05), club_doorway, cls='emit')
def bill(x, y, s, t, z, wp):
    """a pasted-up bill for Feral Toast: torn corner, a toast with fangs"""
    if s > 0.88 and t > 0.86 and (s - 0.88) + (t - 0.86) > 0.08: return None
    if 0.3 < s < 0.7 and 0.28 < t < 0.62:                                            # the toast
        u, v = (s - 0.5) / 0.2, (t - 0.45) / 0.17
        if u * u + (v - 0.55) ** 2 < 0.55 or (abs(u) < 0.8 and v < 0.6 and v > -0.9):
            if v < -0.5 and abs(u) < 0.6 and (int((u + 1) * 6) % 2): return (236, 228, 210)       # fangs
            return (176, 120, 56) if abs(u) < 0.62 and v < 0.62 else (110, 66, 30)
    return (196, 182, 146) if (x + y) % 5 else (168, 152, 118)
rs.quad((22.6, 4.2, ZB - 0.06), (25.4, 4.2, ZB - 0.06), (22.6, 8.4, ZB - 0.06), bill, cls='prop', cut=True)
def frame(inner):
    def sh(x, y, s, t, z, wp):
        if s < 0.1 or s > 0.9 or t < 0.08 or t > 0.92: return fg(tone(BRASS, 2.6 + (1.0 if t > 0.85 or s < 0.15 else 0), x, y), z)
        return inner(x, y, (s - 0.1) / 0.8, (t - 0.08) / 0.84, z)
    return sh
def bottle_paint(x, y, u, v, z):
    if abs(u - 0.5) < 0.18 and 0.12 < v < 0.62 or (abs(u - 0.5) < 0.07 and v < 0.85 and v > 0.6):
        return mix((38, 70, 40), (90, 140, 70), v)
    return mix((40, 28, 20), (70, 50, 32), (math.sin(u * 9 + v * 4) + 1) / 2)
rs.quad((14.8, 15.6, ZB - 0.08), (19.6, 15.6, ZB - 0.08), (14.8, 21.8, ZB - 0.08), frame(bottle_paint), cls='prop')
def eye_ring(x, y, u, v, z):
    d = math.hypot(u - 0.5, v - 0.5)
    if d < 0.12: return INK if d < 0.05 else (200, 170, 60)
    if d < 0.2: return (220, 212, 190)
    return mix((50, 24, 30), (96, 50, 56), (math.cos(math.atan2(v - 0.5, u - 0.5) * 7) + 1) / 2) if d < 0.42 else (30, 20, 16)
rs.quad((-19.6, 16.0, ZB - 0.08), (-15.2, 16.0, ZB - 0.08), (-19.6, 21.0, ZB - 0.08), frame(eye_ring), cls='prop')
# a single tentacle mounted on a plaque, curled into an S (a trophy from the same catch)
def tentacle_img():
    r = Rig(96, 132)
    MT = Mat(ramp('#2a1c10 #463018 #644626 #826036 #9e7a48 #b8945e'), 'skin', 0.26, 0.4)
    MS = Mat(ramp('#4a3a2a #6a5640 #8a765a #a8967a'), 'skin', 0.3, 0.3)
    r.ellipsoid(48, 22, 20, 14, Mat(TIMBER, 'wood', 0.24, 0.2), group='plaque')
    p_ = [(48 + 22 * math.sin(j / 39 * 2 * math.pi) * (1 - j / 39 * 0.45), 26 + j / 39 * 98) for j in range(40)]
    for j in range(len(p_) - 1):
        u0, u1 = j / 39, (j + 1) / 39
        r.tube(p_[j], p_[j + 1], 7.5 * (1 - u0 * 0.85), 7.5 * (1 - u1 * 0.85), MT, group='arm')
    for j in range(1, 34, 2):
        dx, dy = p_[j + 1][0] - p_[j][0], p_[j + 1][1] - p_[j][1]
        n = math.hypot(dx, dy) or 1
        rr = 7.5 * (1 - j / 39 * 0.85)
        r.ellipsoid(p_[j][0] - dy / n * rr * 0.7, p_[j][1] + dx / n * rr * 0.7, max(1.0, rr * 0.32), max(1.0, rr * 0.32), MS, group='suck%d' % j)
    return r.render()
rs.sprite(tentacle_img(), 24.6, 15.2, ZB - 0.3, tint=lambda c, z: fg(c, z), cls='prop')

# the octopus: a great stuffed cephalopod over the bar, drawn with the character renderer
def octopus_img():
    W_, H_ = 440, 210
    r = Rig(W_, H_)
    M = Mat(OCTO, 'skin', 0.24, 0.5)
    MS = Mat(ramp('#3a2a20 #5a4234 #7a5c4a #9a7a64 #b89a82'), 'skin', 0.3, 0.3)
    cx, cy = W_ / 2, 66
    for side in (-1, 1):                                                           # eight arms, curling out and up
        for i in range(4):
            base = (cx + side * (8 + i * 7), cy + 36 + i * 2)
            ang = math.radians(90 + side * (-34 - i * 24))
            L = 150 - i * 8
            p_ = [base]
            for j in range(1, 26):
                u = j / 25
                ang_j = ang - side * (u ** 2.0) * (2.2 + i * 0.3) + 0.25 * math.sin(i * 1.7 + u * 5)
                last = p_[-1]
                p_.append((last[0] + math.cos(ang_j) * L / 25, last[1] + math.sin(ang_j) * L / 25))
            for j in range(len(p_) - 1):
                u0, u1 = j / 25, (j + 1) / 25
                r.tube(p_[j], p_[j + 1], 9.0 * (1 - u0 * 0.86), 9.0 * (1 - u1 * 0.86), M, group='arm%d%d' % (side, i))
                if j % 2 == 0 and j < 22:                                             # suckers on the underside
                    dx, dy = p_[j + 1][0] - p_[j][0], p_[j + 1][1] - p_[j][1]
                    n = math.hypot(dx, dy) or 1
                    nx, ny = -dy / n * side, dx / n * side
                    rr = 7.0 * (1 - u0 * 0.85)
                    r.ellipsoid(p_[j][0] + nx * rr * 0.75, p_[j][1] + ny * rr * 0.75, max(1.0, rr * 0.35), max(1.0, rr * 0.35), MS, group='suck%d%d' % (side, i))
    r.ellipsoid(cx, cy + 34, 30, 16, M, group='web')                                 # the web between the arms
    r.ellipsoid(cx, cy, 34, 46, M, group='mantle',                                   # the mantle, ribbed like a fan
                vfun=lambda x, y, u, w: -0.35 if (math.atan2(y - cy - 60, x - cx) * 9) % 1 < 0.22 else 0.05)
    for side in (-1, 1):                                                           # the eyes: gold, horizontal pupils
        ex, ey = cx + side * 15, cy + 30
        r.ellipsoid(ex, ey, 9, 7, M, lift=0.1, group='brow%d' % side)
        r.ellipsoid(ex, ey + 1, 6.4, 4.6, Mat(ramp('#5a3a08 #8a6010 #b88a20 #e0b440 #f8dc78'), 'plain', 0.4, 0.6), group='eye%d' % side)
        r.ellipsoid(ex, ey + 1.4, 4.4, 1.2, Mat(ramp('#050505 #121008 #1c1810'), 'plain', 0.3), group='pupil%d' % side)
        r.ellipsoid(ex, ey - 2.6, 7.4, 2.6, M, lift=-0.05, group='lid%d' % side, clip=lambda x, y, ey=ey: y < ey - 1.4)
    return r.render()
OCT = octopus_img()
rs.sprite(OCT, 0.0, 16.0, ZB - 0.4, tint=lambda c, z: fg(c, z), cls='prop')

# ---------------------------------------------------------------------------------------------------- the back bar
BZ = 20.6
def backbar_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    if abs(X) > 10.4 or Y < 1.0 or abs(Y - 4.2) < 0.25 or abs(Y - 7.2) < 0.25 or abs(Y - 10.2) < 0.25:
        return fg(tone(TIMBER, 3.0 + (0.8 if (Y % 3) > 0.15 and Y > 1.0 and abs(X) <= 10.4 else 0) - (0.6 if Y < 1.0 else 0), x, y), z)
    if Y < 4.0:                                                                       # cupboards under the shelves
        return fg(tone(TIMBER, 2.4 + (1.0 if (X / 3.5) % 1 < 0.06 else 0) - (0.8 if abs((X / 3.5) % 1 - 0.5) < 0.04 else 0), x, y), z)
    m = (wn(1, X * 0.8, Y * 0.8) - 0.5) * 1.2                                         # the clouded mirror behind the bottles
    return fg(tone(ramp('#141a16 #1c2620 #26332c #33433a #44564b'), 2.2 + m + (1.2 if (X + Y * 0.6) % 4.0 < 0.3 else 0), x, y), z)
for (x0, x1) in ((-11.0, -3.4), (3.4, 11.0)):
    rs.box(x0, x1, 0, 12.0, BZ, BZ + 1.4, backbar_front, lambda x, y, s, t, z, wp: fg(tone(TIMBER, 2.0, x, y), z), cls='wall')
def curtain(x, y, s, t, z, wp):
    """the doorway to the back room between the cabinets: a heavy, grimy curtain"""
    X, Y, Z = wp
    fold = (X * 1.6 + math.sin(Y * 0.7) * 0.25) % 1
    v = 2.0 + (1.0 if fold < 0.35 else 0) - (1.0 if fold > 0.8 else 0) - max(0.0, 1 - Y / 2.0) * 0.8 + (wn(1, X * 2, Y * 0.5) - 0.5) * 0.6
    return fg(tone(ramp('#140808 #200c0c #2e1212 #3e1a18 #502420 #64302a'), v, x, y), z)
rs.quad((-3.4, 0, BZ + 1.2), (3.4, 0, BZ + 1.2), (-3.4, 12.0, BZ + 1.2), curtain, cls='wall')
rs.box(-3.6, 3.6, 10.6, 12.0, BZ + 0.9, BZ + 1.3, lambda x, y, s, t, z, wp: fg(tone(TIMBER, 2.6 + t, x, y), z),
       lambda x, y, s, t, z, wp: fg(TIMBER[1], z), bottom=lambda x, y, s, t, z, wp: fg(TIMBER[0], z), cls='prop')   # its lintel
rs.box(-11.6, 11.6, 12.0, 12.6, BZ - 0.4, BZ + 1.4, lambda x, y, s, t, z, wp: fg(tone(TIMBER, 3.8 - t, x, y), z),
       lambda x, y, s, t, z, wp: fg(TIMBER[2], z), cls='prop')
for (Y0, row) in ((4.45, 0), (7.45, 1), (10.45, 2)):                                 # the bottles
    X = -10.0
    k = 0
    while X < 9.6:
        if -3.5 < X + 0.4 < 3.5:                                                     # the doorway: no shelves
            X = 3.6; continue
        bw = 0.55 + (h32(row, k, 1) % 3) * 0.12
        bh = 1.5 + (h32(row, k, 2) % 4) * 0.25
        if bh > 2.5 - row * 0.1: bh = 2.4
        seed = h32(row, k, 3)
        glow = seed % 19 == 0
        rs.quad((X, Y0, BZ - 0.2), (X + bw, Y0, BZ - 0.2), (X, Y0 + bh, BZ - 0.2), bottle(seed, glow), cls='emit' if glow else 'prop', cut=True)
        X += bw + 0.08 + (h32(row, k, 4) % 3) * 0.06
        k += 1
# the name in red light on a board over the back bar
SIGN = (-7.6, 7.6, 12.8, 16.2, BZ - 0.3)
rs.quad((SIGN[0], SIGN[2], SIGN[4]), (SIGN[1], SIGN[2], SIGN[4]), (SIGN[0], SIGN[3], SIGN[4]),
        lambda x, y, s, t, z, wp: fg(tone(TIMBER, 1.4 + (1.2 if s < 0.02 or s > 0.98 or t < 0.04 or t > 0.96 else 0), x, y), z), cls='prop')
def letter_mask():
    x0, x1, y0, y1, z = SIGN
    (ax, ay) = proj(x0 + 0.5, y1 - 0.35, z); (bx, by) = proj(x1 - 0.5, y0 + 0.35, z)
    w, h = int(bx - ax), int(by - ay)
    path = '/usr/share/fonts/TTF/DejaVuSansCondensed-Bold.ttf'
    im = Image.new('L', (w, h), 0); d = ImageDraw.Draw(im); d.fontmode = '1'
    lines = ['SCREAMING', 'CORK']
    if os.path.exists(path):
        size = 60
        while size > 8:
            f = ImageFont.truetype(path, size)
            bbs = [d.textbbox((0, 0), ln, font=f) for ln in lines]
            th = sum(b[3] - b[1] for b in bbs) + size * 0.2
            if max(b[2] - b[0] for b in bbs) <= w and th <= h: break
            size -= 1
        yy = (h - th) / 2
        for ln, b in zip(lines, bbs):
            d.text(((w - (b[2] - b[0])) / 2 - b[0], yy - b[1]), ln, font=f, fill=255)
            yy += b[3] - b[1] + size * 0.2
    else:
        for i, ln in enumerate(lines):
            draw_text(lambda x, y: (0 <= x < w and 0 <= y < h) and im.putpixel((x, y), 255), ln, (w - text_width(ln, 4)) // 2, 2 + i * 26, 4)
    p = im.load()
    return {(int(ax) + x, int(ay) + y) for y in range(h) for x in range(w) if p[x, y]}
LET = letter_mask()
def neon(x, y, s, t, z, wp):
    if (x, y) not in LET: return None
    edge = not ((x - 1, y) in LET and (x + 1, y) in LET and (x, y - 1) in LET and (x, y + 1) in LET)
    return NEON[3] if edge else (NEON[5] if (x + y) % 4 == 0 else NEON[4])
rs.quad((SIGN[0], SIGN[2], SIGN[4] - 0.05), (SIGN[1], SIGN[2], SIGN[4] - 0.05), (SIGN[0], SIGN[3], SIGN[4] - 0.05), neon, cls='emit', cut=True)

# ---------------------------------------------------------------------------------------------------- the counter (over Heliodor)
CZ = 16.0
def counter_front(x, y, s, t, z, wp):
    X, Y, Z = wp
    if Y > 3.7: return fg(tone(TIMBER, 3.4, x, y), z)
    if Y < 0.5: return fg(tone(TIMBER, 1.4, x, y), z)                                 # the kick board
    pan = (X + 11.0) / 2.5
    fu = pan % 1
    if fu < 0.08 or fu > 0.92 or Y < 0.8 or Y > 3.4: return fg(tone(TIMBER, 2.8 + (0.6 if fu < 0.04 else 0), x, y), z)   # stiles, rails
    v = 2.0 + (h32(int(pan), 2) % 3) * 0.25 + (0.6 if abs(fu - 0.5) < 0.3 and abs(Y - 2.1) < 1.0 else 0) - (0.5 if abs(fu - 0.5) > 0.36 else 0)
    return fg(tone(TIMBER, v, x, y), z)
(rs.box(-11.0, 9.0, 0, 3.9, CZ, CZ + 1.4, counter_front, lambda x, y, s, t, z, wp: fg(tone(TIMBER, 2.2, x, y), z), cls='prop'))
def top_sh(x, y, s, t, z, wp):
    X, Y, Z = wp
    v = 3.4 + (wn(0, X * 0.8, Z * 3) - 0.5) * 0.8 + (0.8 if (Z - CZ) < 0.15 else 0)
    if math.hypot(X + 4.0, Z - CZ - 0.7) < 0.35 or math.hypot(X - 3.0, Z - CZ - 0.9) < 0.3: v -= 1.2   # glass rings
    return fg(tone(TIMBER, v, x, y), z)
(rs.box(-11.4, 9.4, 3.9, 4.3, CZ - 0.35, CZ + 1.6, lambda x, y, s, t, z, wp: fg(tone(TIMBER, 3.0 + t, x, y), z),
                   lambda x, y, s, t, z, wp: fg(TIMBER[2], z), top=top_sh, cls='prop'))
(rs.line3((-11.0, 0.7, CZ - 0.4), (9.0, 0.7, CZ - 0.4), lambda x, y, s, t, z, wp: BRASS[4] if y % 2 else BRASS[2], w=0.18))   # the foot rail
for X in (-9.0, -4.0, 1.0, 6.0):
    (rs.line3((X, 0.7, CZ - 0.4), (X, 0.7, CZ), lambda x, y, s, t, z, wp: BRASS[2], w=0.12))
def glass_sh(x, y, s, t, z, wp):
    u = abs(s - 0.5) * 2
    if u > 0.75 + t * 0.25: return None
    if t > 0.55: return (186, 192, 176) if u > 0.6 + t * 0.25 else (60, 70, 62)
    return (196, 150, 70) if u < 0.6 else (150, 110, 50)
for (X, Z) in ((-7.6, CZ + 0.5), (-2.4, CZ + 0.8), (7.4, CZ + 0.4)):              # mugs of something amber
    (rs.quad((X - 0.32, 4.3, Z), (X + 0.32, 4.3, Z), (X - 0.32, 5.2, Z), glass_sh, cls='prop', cut=True))
def jar_sh(x, y, s, t, z, wp):
    """a big jar of brine with pale eyes floating in it"""
    u = abs(s - 0.5) * 2
    if t > 0.86: return BRASS[2] if u < 0.8 else None
    if u > 0.95: return None
    for (ex, ey) in ((0.35, 0.3), (0.62, 0.5), (0.42, 0.66), (0.66, 0.22)):
        d = math.hypot((s - ex) * 1.2, t - ey)
        if d < 0.08: return INK if d < 0.03 else ((220, 214, 190) if d < 0.065 else (150, 60, 50))
    return mix((60, 74, 50), (110, 130, 84), (1 - u) * 0.8)
(rs.quad((-5.6, 4.3, CZ + 0.6), (-4.2, 4.3, CZ + 0.6), (-5.6, 6.2, CZ + 0.6), jar_sh, cls='prop', cut=True))
(rs.quad((4.2, 4.3, CZ + 0.7), (4.8, 4.3, CZ + 0.7), (4.2, 6.3, CZ + 0.7), bottle(7), cls='prop', cut=True))

# ---------------------------------------------------------------------------------------------------- furniture
def round_table(X, Z, r=1.9, h=3.3, seed=0):
    rs.quad((X - r, h, Z - r * 0.9), (X + r, h, Z - r * 0.9), (X - r, h, Z + r * 0.9),
            lambda x, y, s, t, z, wp: (fg(tone(TIMBER, 3.6 + (wn(0, wp[0] * 2, wp[2] * 2) - 0.5) - (1.2 if (2 * s - 1) ** 2 + (2 * t - 1) ** 2 > 0.82 else 0), x, y), z)
                                       if (2 * s - 1) ** 2 + (2 * t - 1) ** 2 < 1 else None), cls='prop', cut=True)
    rs.quad((X - r, h - 0.35, Z - r * 0.9 + 0.01), (X + r, h - 0.35, Z - r * 0.9 + 0.01), (X - r, h, Z - r * 0.9 + 0.01),
            lambda x, y, s, t, z, wp: fg(tone(TIMBER, 2.2 + (1 - abs(s - 0.5) * 2) * 0.8, x, y), z) if abs(s - 0.5) < 0.48 else None, cls='prop', cut=True)
    rs.line3((X, 0, Z), (X, h - 0.3, Z), lambda x, y, s, t, z, wp: fg(tone(TIMBER, 2.0, x, y), z), w=0.5)
    rs.line3((X - 1.0, 0.1, Z), (X + 1.0, 0.1, Z), lambda x, y, s, t, z, wp: fg(TIMBER[1], z), w=0.3)
    if seed % 2: rs.quad((X - 0.6, h, Z - 0.2), (X - 0.1, h, Z - 0.2), (X - 0.6, h + 1.4, Z - 0.2), bottle(seed + 11), cls='prop', cut=True)
    else: rs.disc(X + 0.4, h + 0.25, Z, 0.32, lambda x, y, s, t, z, wp: CORKC[4] if t < 0.3 else CORKC[2])
def stool(X, Z, h=2.2):
    rs.quad((X - 0.75, h, Z - 0.6), (X + 0.75, h, Z - 0.6), (X - 0.75, h, Z + 0.6),
            lambda x, y, s, t, z, wp: fg(tone(TIMBER, 3.6, x, y), z) if (2 * s - 1) ** 2 + (2 * t - 1) ** 2 < 1 else None, cls='prop', cut=True)
    rs.quad((X - 0.75, h - 0.3, Z - 0.6), (X + 0.75, h - 0.3, Z - 0.6), (X - 0.75, h, Z - 0.6),
            lambda x, y, s, t, z, wp: fg(tone(TIMBER, 2.4, x, y), z), cls='prop')
    for dx in (-0.5, 0.0, 0.5):
        rs.line3((X + dx, 0, Z - 0.3 + abs(dx) * 0.4), (X + dx * 0.6, h - 0.3, Z - 0.3 + abs(dx) * 0.2), lambda x, y, s, t, z, wp: fg(TIMBER[2], z), w=0.18)
round_table(-27.0, 25.0, seed=1); stool(-29.4, 24.4); stool(-24.4, 24.0)
round_table(-19.0, 20.4, seed=2); stool(-21.6, 19.6); stool(-16.4, 19.4); stool(-19.4, 22.8)
round_table(17.0, 22.4, seed=3); stool(14.4, 21.6); stool(19.6, 21.4)
for (X, Z) in ((-6.0, CZ - 0.4), (-1.0, CZ - 0.45), (4.0, CZ - 0.35)):             # stools tucked under the counter's lip
    stool(X, Z, h=2.6)
# barrels stacked at the back right, clear of the club door
def barrel_q(X, Y0, Z, h=2.6, r=1.05, seed=0):
    def sh(x, y, s, t, z, wp):
        u = s * 2 - 1; bul = 1.0 - 0.1 * (2 * t - 1) ** 2
        if abs(u) > bul: return None
        n = u / bul
        v = 3.0 - n * 1.5 - abs(n) ** 3 * 1.3 + (h32(int((n + 1) * 7), seed) % 3) * 0.25 - (0.9 if ((n + 1) * 7) % 1 < 0.12 else 0)
        if abs(t - 0.18) < 0.04 or abs(t - 0.82) < 0.04: return fg(tone(BRASS, 1.6 - n, x, y), z)
        return fg(tone(TIMBER, v + 0.4, x, y), z)
    rs.quad((X - r, Y0, Z), (X + r, Y0, Z), (X - r, Y0 + h, Z), sh, cls='prop', cut=True)
barrel_q(18.2, 0, 26.4, seed=1); barrel_q(20.4, 0, 26.6, seed=2); barrel_q(19.3, 2.6, 26.5, seed=3)
# Ravla's corner: a small desk against the right wall, papers, ink, a candle
def desk_top(x, y, s, t, z, wp):
    X, Y, Z = wp
    if (h32(int(X * 3), int(Z * 3), 9) % 5 == 0): return fg(tone(BONE, 3.4, x, y), z)                     # papers
    return fg(tone(TIMBER, 3.6, x, y), z)
rs.box(30.0, WX, 0, 3.2, 19.2, 23.0, lambda x, y, s, t, z, wp: fg(tone(TIMBER, 2.2, x, y), z),
       lambda x, y, s, t, z, wp: fg(tone(TIMBER, 2.8 - (0.8 if wp[1] < 2.8 and wp[1] > 0.4 and (wp[2] * 1.2) % 1 < 0.06 else 0), x, y), z), top=desk_top, cls='prop')
rs.line3((31.6, 3.2, 20.6), (31.6, 4.0, 20.6), lambda x, y, s, t, z, wp: (226, 214, 180), w=0.22)          # the candle
rs.disc(31.6, 4.25, 20.6, 0.2, lambda x, y, s, t, z, wp: GLOW[4] if t > -0.2 else GLOW[2], cls='emit')
rs.disc(31.0, 3.45, 21.6, 0.28, lambda x, y, s, t, z, wp: INK if t < 0.4 else BRASS[3])                       # an ink pot

# ---------------------------------------------------------------------------------------------------- lanterns on chains
def lantern(X, Y, Z):
    rs.line3((X, Y + 1.3, Z), (X, CH - 1.8, Z), lambda x, y, s, t, z, wp: fg(BRASS[1] if (x + y) % 2 else TIMBER[0], z), w=0.08)
    rs.box(X - 0.5, X + 0.5, Y, Y + 1.2, Z - 0.5, Z + 0.5, lambda x, y, s, t, z, wp: (GLOW[4] if 0.2 < s < 0.8 and 0.15 < t < 0.85 else BRASS[1]) if abs(s - 0.5) > 0.06 else BRASS[0],
           lambda x, y, s, t, z, wp: GLOW[2] if 0.2 < s < 0.8 and 0.15 < t < 0.85 else BRASS[1], cls='emit')
    rs.quad((X - 0.65, Y + 1.2, Z - 0.5), (X + 0.65, Y + 1.2, Z - 0.5), (X, Y + 1.8, Z - 0.5),
            lambda x, y, s, t, z, wp: BRASS[2] if t < 1 - abs(s - 0.5) * 2 else None, cls='prop', cut=True)
lantern(-15.0, 19.0, 19.0); lantern(-9.0, 21.5, 23.6); lantern(13.0, 19.5, 20.0); lantern(-27.0, 18.0, 25.0); lantern(26.0, 18.5, 24.0)
# the street door in the left wall (the exit), ajar: the overcast day in the crack and spilling in
def door_frame(x, y, s, t, z, wp):
    X, Y, Z = wp
    if 20.6 < Z < 24.4 and Y < 8.4: return None
    return fg(tone(TIMBER, 1.6 + (1.0 if Y > 8.65 or Z < 20.35 or Z > 24.65 else 0), x, y), z)
rs.quad((-WX + 0.05, 0, 20.2), (-WX + 0.05, 0, 24.8), (-WX + 0.05, 8.8, 20.2), door_frame, cls='prop', cut=True)
def outside(x, y, s, t):
    """through the door: the wet setts, the hazy house across the street, its windows, the overcast sky above"""
    if t < 0.1: return tone(STONE, 4.4 + (1.0 if (x + y) % 3 == 0 else 0), x, y)
    if t > 0.9: return tone(SKY, 6.4, x, y)
    if 0.2 < t < 0.8 and (s * 3.2) % 1 > 0.35 and (s * 3.2) % 1 < 0.75 and ((t - 0.2) * 3.3) % 1 > 0.3: return tone(HAZE, 2.4, x, y)
    return tone(HAZE, 4.4 + (t - 0.1) * 1.5, x, y)
rs.quad((-WX - 0.05, 0, 20.6), (-WX - 0.05, 0, 24.4), (-WX - 0.05, 8.4, 20.6),
        lambda x, y, s, t, z, wp: outside(x, y, s, t), cls='emit')                    # the street outside
def leaf(x, y, s, t, z, wp):
    """the door leaf swung into the room a little: planks, a small window, the latch"""
    if 0.3 < s < 0.75 and 0.62 < t < 0.85: return tone(SKY, 3.6 + t * 2, x, y) if abs(s - 0.52) > 0.04 else TIMBER[1]
    if abs(t - 0.46) < 0.025 and s > 0.82: return BRASS[4]
    return fg(tone(TIMBER, 2.8 + (h32(int(s * 5), 7) % 3) * 0.3 - (1.1 if (s * 5) % 1 < 0.08 else 0) + s * 0.6, x, y), z)
rs.quad((-WX + 0.1, 0, 24.3), (-WX + 2.6, 0, 23.3), (-WX + 0.1, 8.3, 24.3), leaf, cls='prop')        # hinged at the far jamb
rs.quad((-WX + 0.2, 0.02, 20.7), (-WX + 5.0, 0.02, 20.9), (-WX + 0.2, 0.02, 23.2),
        lambda x, y, s, t, z, wp: mix(fg(tone(FLOORW, 4.4, x, y), z), (120, 140, 132), 0.25 * (1 - s)), cls='ground')   # daylight on the floor

# corks underfoot
for k in range(40):
    fx, fz = -30 + (h32(k, 51) % 600) / 10.0, 9.0 + (h32(k, 52) % 120) / 10.0
    if -11.5 < fx < 9.5 and CZ - 0.5 < fz < CZ + 1.8: continue
    rs.disc(fx, 0.12, fz, 0.16, lambda x, y, s, t, z, wp: CORKC[4] if t < 0 else CORKC[2])

img = rs.render(INK, fog=fog, light_gain=1.15, grime_gain=0.6, bloom=0.5, stain_gain=0.3, damp_gain=0.2)
img.save(f'{OUT}/corkin.png')
# everything nearer than Heliodor inside his sprite's box (the counter, its stools and what stands on it): the scene
# draws this over him
HEL_X, HEL_YB, HEL_Z = 533, 492, 17.3                                                # his sprite's bottom-centre, his depth
HEL_BOX = (HEL_X - 70, HEL_YB - 200, HEL_X + 72, HEL_YB + 4)
ov = Image.new('RGBA', img.size, (0, 0, 0, 0)); op = ov.load(); ip = img.load()
for y in range(HEL_BOX[1], HEL_BOX[3]):
    for x in range(HEL_BOX[0], HEL_BOX[2]):
        if rs.G[y][x] is not None and rs.ZB[y][x] < HEL_Z: op[x, y] = ip[x, y] + (255,)
ov.save(f'{OUT}/counter.png')
print('done corkin')
