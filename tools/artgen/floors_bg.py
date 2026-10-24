"""The Floors of Shed 521 (Shed521FloorsScene), 1067x600: a cut-away of the bureau's three floors, seen almost
straight on (a long lens: the camera is moved far back so the floors don't converge), like a doll's house.
The floor lines are fixed by the scene: the priest's feet stand at y 520 (ground floor), 340 (first) and 180 (second).
  ground   WELCOME (the reception counter, a ticket machine, a "now serving" counter) and the way back to the gate on
           the left; the big EXIT doors to the yard in the middle; the foot of the stairs on the right
  first    ASSESSMENTS on the left; a ladder hatch down in the middle; the stairs up on the right
  second   REGISTRATION on the left, APPLICATIONS in the middle with its queue; the stairs down on the right
Benches with waiting applicants, filing cabinets, a water cooler, notices, pipes and cables under the slabs, warm
lamps hanging from them.

    python3 floors_bg.py <outdir>   ->  floors.png
"""
import sys, math
import raster3d, paintpass
raster3d.F = paintpass.F = 3000.0                    # a long lens: everything at ~160 units, scaled like depth 16
import shedkit
shedkit.fog_of = lambda z: 0.0                       # indoors: no haze
from shedkit import *
from common import h32, draw_text, text_width

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
F = raster3d.F
ZF = F * CAMH / (520 - HY)                            # the walkway's front edge: the ground floor's feet line on y 520
FLOORS = [0.0, CAMH - (340 - HY) * ZF / F, CAMH - (180 - HY) * ZF / F]   # 0, ~9.6, ~18.2
ZW = ZF + 6.0                                         # the back wall
SLAB = 0.8
XL, XR = -34.0, 34.0
def cx(px): return (px - CX) * ZF / F                 # canvas x -> world x on the front plane
rs = Raster()

# ---------------------------------------------------------------------------------------------------- walls, slabs
def wall_sh(fi):
    base = planks(2.6 + fi * 0.2, WOOD, w=1.1, seed=fi) if fi != 1 else concrete(2.8, STONE)
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        if Y - FLOORS[fi] < 0.9: return fogged(tone(WOOD if fi != 1 else STONE, 1.4, x, y), z)       # the skirting
        return base(x, y, s, t, z, wp)
    return sh
for fi, Y0 in enumerate(FLOORS):
    top = FLOORS[fi + 1] - SLAB if fi < 2 else 30.0
    rs.quad((XL, Y0, ZW), (XR, Y0, ZW), (XL, top, ZW), wall_sh(fi), cls='wall')
    rs.quad((XL, Y0, ZF - 0.2), (XR, Y0, ZF - 0.2), (XL, Y0, ZW), lambda x, y, s, t, z, wp: fogged(tone(WOOD, 2.6 + (0.8 if (wp[0] * 1.2) % 1 < 0.1 else 0), x, y), z), cls='ground')
for fi in (1, 2):
    Y = FLOORS[fi]
    def edge(x, y, s, t, z, wp, fi=fi):
        X = wp[0]
        v = 2.6 + (wn(1, X * 0.6, fi * 3.0) - 0.5) * 0.8 - (1.0 if (X / 4.0) % 1 < 0.05 else 0)
        c = tone(METAL, v, x, y)
        if ((X / 1.0) % 1 < 0.08) and 0.3 < t < 0.7: c = METAL[5]                                         # rivets
        if wn(3, X * 0.9, fi * 7.0) > 0.66: c = tone(RUSTY, v, x, y)
        return c
    rs.box(XL, XR, Y - SLAB, Y, ZF - 0.4, ZW, edge, edge, bottom=lambda x, y, s, t, z, wp: tone(WOOD, 1.6, x, y), cls='prop')
    for k in range(int((XR - XL) / 3.2) + 1):                                                            # railing posts
        X = XL + k * 3.2
        if abs(X) < 2.0 and fi == 1: continue                                                            # the hatch
        rs.line3((X, Y, ZF - 0.3), (X, Y + 2.6, ZF - 0.3), lambda x, y, s, t, z, wp: METAL[1], w=0.14)
    rs.line3((XL, Y + 2.6, ZF - 0.3), (XR, Y + 2.6, ZF - 0.3), lambda x, y, s, t, z, wp: METAL[2], w=0.16)
def foundation(x, y, s, t, z, wp):
    """the ground floor's sill and the foundation under it: cellar grates, a damp, mossy plinth"""
    X, Y, Z = wp
    if Y > -0.9: return tone(METAL, 2.2 + (1.0 if (X / 1.0) % 1 < 0.08 and Y > -0.6 else 0), x, y)
    if -4.6 < Y < -2.0 and (X / 7.0) % 1 < 0.32:                                                     # cellar grates
        if ((X / 7.0) % 1) * 7.0 % 0.5 < 0.12 or abs(Y + 3.3) < 0.1: return METAL[1]
        return STONE[0]
    v = 2.4 + (wn(0, X * 0.6, Y * 0.6) - 0.5) * 0.8 - 0.6 * max(0.0, (Y + 7) / 7 - 0.8)
    c = tone(STONE, v, x, y)
    if Y < -5.0 and wn(2, X * 0.8, Y) > 0.5: c = mix(c, LEAF[1], 0.4)
    return c
rs.quad((XL, -8.0, ZF - 0.3), (XR, -8.0, ZF - 0.3), (XL, 0.0, ZF - 0.3), foundation, cls='wall')
rs.box(XL, XR, 26.5, 27.6, ZF - 0.6, ZW, lambda x, y, s, t, z, wp: tone(RUSTY, 1.8, x, y), lambda x, y, s, t, z, wp: RUSTY[1],
       bottom=lambda x, y, s, t, z, wp: tone(WOOD, 1.2, x, y), cls='prop')

# pipes and cables under the slabs, lamps hanging from them
for fi, Y in enumerate(FLOORS):
    ceil = (FLOORS[fi + 1] - SLAB) if fi < 2 else 26.5
    rs.line3((XL, ceil - 0.6, ZW - 0.6), (XR, ceil - 0.6, ZW - 0.6), lambda x, y, s, t, z, wp: tone(RUSTY, 2.6 + (1 if y % 3 == 0 else 0), x, y), w=0.7)
    rs.line3((XL, ceil - 1.4, ZW - 0.4), (XR, ceil - 1.4, ZW - 0.4), lambda x, y, s, t, z, wp: tone(METAL, 2.2, x, y), w=0.4)
    for k in range(5):
        X0 = XL + 6 + k * 12.5 + (h32(fi, k) % 4)
        rs.line3((X0, ceil - 0.2, ZF + 2.0), (X0 + 6.0, ceil - 0.2, ZF + 2.4), lambda x, y, s, t, z, wp: STONE[0], w=0.12, sag=1.2)
    for X0 in ((-26.0, -4.0, 14.0) if fi == 0 else ((-22.0, 9.0) if fi == 1 else (-26.0, 10.0, 24.0))):
        rs.line3((X0, ceil, ZF + 2.5), (X0, ceil - 1.4, ZF + 2.5), lambda x, y, s, t, z, wp: STONE[0], w=0.1)
        rs.disc(X0, ceil - 1.8, ZF + 2.5, 0.55, lambda x, y, s, t, z, wp: (GLOW[3] if t > 0.1 else METAL[1]), cls='emit')

# ---------------------------------------------------------------------------------------------------- doors and signs
SIGNS = []
def door(X, fi, w=3.4, h=6.6, sign=None, kind='plain', lit=False):
    Y = FLOORS[fi]
    def sh(x, y, s, t, z, wp):
        if s < 0.06 or s > 0.94 or t > 0.95: return tone(WOOD, 1.2, x, y)                          # the frame
        if kind == 'double':
            if abs(s - 0.5) < 0.02: return WOOD[0]
            if 0.62 < t < 0.88 and (0.12 < s < 0.44 or 0.56 < s < 0.88): return SKY[6] if (x + y) % 3 else SKY[5]    # daylight in the panes
            return tone(METAL, 2.6 + (0.6 if (s * 8) % 1 < 0.1 else 0), x, y)
        if lit and 0.55 < t < 0.85 and 0.2 < s < 0.8: return GLOW[1] if (x + y) % 3 else GLOW[0]        # a frosted pane, lit
        v = 2.6 + (0.6 if 0.2 < s < 0.8 and (0.15 < t < 0.45 or 0.55 < t < 0.85) else 0)                # panels
        if abs(s - 0.84) < 0.04 and abs(t - 0.45) < 0.03: v = 5.0                                         # the handle
        return tone(WARM, v, x, y)
    rs.quad((X - w / 2, Y, ZW - 0.05), (X + w / 2, Y, ZW - 0.05), (X - w / 2, Y + h, ZW - 0.05), sh, cls='prop')
    if sign:
        sw = max(w + 1.0, len(sign) * 0.62 + 1.0)
        rs.quad((X - sw / 2, Y + h + 0.3, ZW - 0.15), (X + sw / 2, Y + h + 0.3, ZW - 0.15), (X - sw / 2, Y + h + 1.7, ZW - 0.15),
                lambda x, y, s, t, z, wp: (tone(RUSTY, 2.4, x, y) if s < 0.03 or s > 0.97 or t < 0.1 or t > 0.9 else (14, 34, 30)), cls='prop')
        SIGNS.append((sign, X - sw / 2, X + sw / 2, Y + h + 0.3, Y + h + 1.7))
door(cx(147), 0, sign='WELCOME', lit=True)
door(cx(600), 0, w=6.2, h=7.2, sign='EXIT', kind='double')
door(cx(267), 1, sign='ASSESSMENTS')
door(cx(200), 2, sign='REGISTRATION', lit=True)
door(cx(533), 2, sign='APPLICATIONS', lit=True)

# ---------------------------------------------------------------------------------------------------- the stairs (right) and the hatch (middle)
def flight(x0, y0, x1, y1, z0, z1, steps=12):
    for i in range(steps):
        xa = x0 + (x1 - x0) * i / steps; xb = x0 + (x1 - x0) * (i + 1) / steps
        ya = y0 + (y1 - y0) * (i + 1) / steps
        rs.box(min(xa, xb), max(xa, xb), ya - 0.25, ya, z0, z1, lambda x, y, s, t, z, wp: tone(WOOD, 3.4, x, y),
               lambda x, y, s, t, z, wp: WOOD[1], top=lambda x, y, s, t, z, wp: tone(WOOD, 4.4, x, y), cls='prop')
    rs.line3((x0, y0 + 0.2, z0 - 0.1), (x1, y1 + 0.2, z0 - 0.1), lambda x, y, s, t, z, wp: tone(METAL, 1.6, x, y), w=0.45)
    rs.line3((x0, y0 + 3.0, z0 - 0.2), (x1, y1 + 3.0, z0 - 0.2), lambda x, y, s, t, z, wp: METAL[2], w=0.15)
flight(cx(780), 0.0, cx(1010), FLOORS[1], ZW - 3.0, ZW - 0.6)
flight(cx(1050), FLOORS[1], cx(860), FLOORS[2], ZW - 2.6, ZW - 0.4)
HX = cx(533)
rs.quad((HX - 1.6, FLOORS[1] - SLAB - 0.01, ZF - 0.5), (HX + 1.6, FLOORS[1] - SLAB - 0.01, ZF - 0.5), (HX - 1.6, FLOORS[1] + 0.01, ZF - 0.5),
        lambda x, y, s, t, z, wp: STONE[0], cls='prop')                                                     # the hatch in the slab
for lx in (HX - 1.0, HX + 1.0):
    rs.line3((lx, 0.0, ZF + 1.2), (lx, FLOORS[1] + 1.4, ZF + 1.2), lambda x, y, s, t, z, wp: tone(METAL, 2.4, x, y), w=0.18)
for k in range(1, 12):
    yy = k * (FLOORS[1] + 1.0) / 12
    rs.line3((HX - 1.0, yy, ZF + 1.2), (HX + 1.0, yy, ZF + 1.2), lambda x, y, s, t, z, wp: METAL[2], w=0.12)

# ---------------------------------------------------------------------------------------------------- furniture and people
# ground floor: the reception counter under WELCOME, a ticket machine, a "now serving" counter, a bench
W0 = cx(147)
rs.box(W0 - 4.2, W0 - 3.2, 0, 4.4, ZW - 1.6, ZW - 0.8, lambda x, y, s, t, z, wp: (RED[4] if 0.6 < t < 0.75 else tone(RED, 2.4, x, y)), lambda x, y, s, t, z, wp: RED[1], cls='prop')
rs.quad((W0 + 4.0, 7.0, ZW - 0.1), (W0 + 7.4, 7.0, ZW - 0.1), (W0 + 4.0, 8.4, ZW - 0.1), lambda x, y, s, t, z, wp: (8, 10, 9) if 0.06 < s < 0.94 and 0.1 < t < 0.9 else STONE[1], cls='prop')
applicant(rs, W0 + 5.6, ZW - 1.0, 590, h=6.4, view='front', kind='mask')                                 # the clerk behind the counter
def counter(x, y, s, t, z, wp):
    if t > 0.86: return tone(WOOD, 4.4, x, y)                                                       # the worn top
    if (s * 6) % 1 < 0.05: return WOOD[0]
    return planks(3.0, WARM, w=0.6, seed=41)(x, y, s, t, z, wp)
rs.box(W0 + 2.4, W0 + 9.0, 0, 3.4, ZW - 2.4, ZW - 1.6, counter, planks(2.4, WARM, seed=42), top=planks(4.0, WARM, vertical=False), cls='prop')
def bench(X, fi, w=6.0, sitters=2, seed=0):
    Y = FLOORS[fi]
    seat = lambda x, y, s, t, z, wp: tone(WOOD, 3.2 + (0.6 if t > 0.6 else 0), x, y)
    for k in range(sitters):
        applicant(rs, X - w / 2 + (k + 0.5) * w / sitters, ZW - 1.0, seed + k, h=6.4, seated=True, Y0=Y + 0.9,
                  view=['front', 'right', 'left'][h32(seed, k) % 3])
    rs.box(X - w / 2, X + w / 2, Y + 1.6, Y + 2.0, ZW - 1.6, ZW - 0.2, seat, seat, top=seat, cls='prop')
    for lx in (X - w / 2 + 0.3, X + w / 2 - 0.3):
        rs.line3((lx, Y, ZW - 1.2), (lx, Y + 1.6, ZW - 1.2), lambda x, y, s, t, z, wp: METAL[1], w=0.2)
bench(cx(370), 0, w=6.5, sitters=3, seed=500)
# first floor: filing cabinets, a water cooler, a bench, a notice board
for k in range(4):
    X0 = cx(360) + k * 2.2
    def cab(x, y, s, t, z, wp):
        if (t * 4) % 1 < 0.06: return METAL[0]
        if abs(s - 0.5) < 0.12 and abs((t * 4) % 1 - 0.7) < 0.06: return METAL[5]
        return tone(SLATE if k % 2 else METAL, 2.6 + (wn(1, s * 3 + k, t * 3) - 0.5) * 0.6, x, y)
    rs.box(X0, X0 + 2.0, FLOORS[1], FLOORS[1] + 5.0 - (k % 2) * 0.6, ZW - 1.8, ZW - 0.2, cab, lambda x, y, s, t, z, wp: METAL[1], cls='prop')
rs.box(cx(720), cx(720) + 1.6, FLOORS[1], FLOORS[1] + 3.4, ZW - 1.4, ZW - 0.3, lambda x, y, s, t, z, wp: tone(STUCCO, 3.6, x, y), lambda x, y, s, t, z, wp: STUCCO[1], cls='prop')
rs.disc(cx(720) + 0.8, FLOORS[1] + 4.3, ZW - 0.9, 0.9, lambda x, y, s, t, z, wp: SKY[5] if s - t < 0.3 else SKY[3])                    # the bottle
bench(cx(160), 1, w=4.8, sitters=2, seed=520)
def notices(x, y, s, t, z, wp):
    k = h32(int(s * 5), int(t * 3), 9)
    if s < 0.04 or s > 0.96 or t < 0.06 or t > 0.94: return tone(WOOD, 1.6, x, y)
    if k % 4 and (s * 5) % 1 < 0.8 and (t * 3) % 1 < 0.8:
        c = BONE[4] if k % 3 else BONE[3]
        if 0.2 < (s * 5) % 1 < 0.7 and int(((t * 3) % 1) * 10) % 3 == 0: c = STONE[4]
        return c
    return tone(WARM, 2.0, x, y)
rs.quad((cx(450), FLOORS[1] + 3.0, ZW - 0.1), (cx(450) + 4.0, FLOORS[1] + 3.0, ZW - 0.1), (cx(450), FLOORS[1] + 6.0, ZW - 0.1), notices, cls='prop')
# second floor: the queue at APPLICATIONS, a bench at REGISTRATION
for i, X in enumerate((cx(533) + 2.2, cx(533) + 3.9, cx(533) + 5.5, cx(533) + 7.2)):
    applicant(rs, X, ZW - 1.2 - (i % 2) * 0.5, 540 + i, h=6.2, Y0=FLOORS[2], view='left')
bench(cx(330), 2, w=4.4, sitters=2, seed=560)
rs.quad((cx(700), FLOORS[2] + 2.6, ZW - 0.1), (cx(700) + 3.6, FLOORS[2] + 2.6, ZW - 0.1), (cx(700), FLOORS[2] + 5.4, ZW - 0.1), notices, cls='prop')

def letters(col):
    for (txt, x0, x1, y0, y1) in SIGNS:
        (ax, ay) = proj(x0, y1, ZW); (bx, by) = proj(x1, y0, ZW)
        sc = 2; tw = text_width(txt, sc)
        def put(x, y):
            if 0 <= x < W and 0 <= y < H: col[y][x] = (124, 214, 168) if (x + y) % 5 else (90, 170, 130)
        draw_text(put, txt, int((ax + bx) / 2 - tw / 2), int((ay + by) / 2 - 5), sc)
    (ax, ay) = proj(W0 + 4.0, 8.4, ZW); (bx, by) = proj(W0 + 7.4, 7.0, ZW)                          # NOW SERVING: 17
    draw_text(lambda x, y: (0 <= x < W and 0 <= y < H) and col[y].__setitem__(x, (220, 70, 50)), '17', int((ax + bx) / 2 - 7), int((ay + by) / 2 - 5), 2)

img = rs.render(INK, fog=lambda z: 0.0, overlay=letters, light_gain=1.2, grime_gain=0.8, bloom=0.45, stain_gain=0.4, damp_gain=0.4)
img.save(f'{OUT}/floors.png')
print('done floors')
