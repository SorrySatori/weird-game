"""The gate of Shed 521 (Shed521GateScene), 1067x600, overcast day, the shared camera (raster3d.py).
A long timber-and-corrugated wall across the yard with cabins piled on top; in the middle the riveted steel gate with
an arched rib, the 5 | 21 number boards and the MUTATION FORMS sign, cables and moss hanging off it; through the gate
a street runs into the haze. A queue of applicants (some visibly mutated) waits between stanchions and ropes for the
forms kiosk at the gate's foot; forms litter the setts. On the near right the timber flank of the Floors building with
its door (the exit right); the yard opens to the left (the courtyard).

    python3 gate_bg.py <outdir>   ->  gate.png
"""
import sys, math
from common import h32, FONT, draw_text, text_width
from shedkit import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = Raster()
ZW = 34.0                                                                          # the wall with the gate

# ---------------------------------------------------------------------------------------------------- sky, ground
rs.quad((-1400, 800, 600), (1400, 800, 600), (-1400, -300, 600), sky, cls='sky')
rs.quad((-90, 0, 3), (90, 0, 3), (-90, 0, 260), lambda x, y, s, t, z, wp: setts(x, y, s, t, z, wp), cls='ground')

# ---------------------------------------------------------------------------------------------------- the street beyond
for side in (-1, 1):
    zz = 40.0; k = 0
    while zz < 200:
        ln = 14 + h32(side, k, 1) % 12; ht = 16 + h32(side, k, 2) % 26
        x0, x1 = (-60, -14) if side < 0 else (14, 60)
        base = [concrete(3.2, STUCCO if k % 2 else STONE), planks_z(2.8, WOOD, seed=k), corrugated(3.0, METAL, 0.7, along_z=True)][h32(side, k, 3) % 3]
        rs.box(x0, x1, 0, ht, zz, zz + ln, concrete(2.6), windows_sh(base, cols=2.6, rows=3.4, lit=0.12, seed=k * side, along_z=True), cls='wall')
        zz += ln + (2 if k % 3 else 6); k += 1
rs.quad((-60, 0, 210), (60, 0, 210), (-60, 46, 210), windows_sh(concrete(3.0, STONE), cols=3.0, rows=3.6, lit=0.08, seed=99), cls='wall')
for k, (X, hh) in enumerate(((-26, 70), (8, 58), (30, 84))):                     # far towers in the haze
    rs.quad((X - 5, 0, 330), (X + 5, 0, 330), (X - 5, hh, 330), lambda x, y, s, t, z, wp: HAZE[3] if (int(s * 8) + int(t * 20)) % 7 else HAZE[4], cls='wall')

# ---------------------------------------------------------------------------------------------------- the wall and its cabins
def wall_front(x, y, s, t, z, wp):
    X, Y, _ = wp
    if -31.0 < X < -22.5 and Y < 7.4:                                              # a rolling shutter
        v = 2.0 + (0.8 if (Y * 3.0) % 1 < 0.5 else 0) - (1.0 if Y > 7.0 else 0)
        return fogged(tone(METAL, v, x, y), z)
    if 22.0 < X < 27.0 and Y < 6.8:                                                # a small timber door
        return planks(1.8, WOOD, w=0.6, seed=7)(x, y, s, t, z, wp) if abs(X - 24.5) > 0.08 else WOOD[0]
    if (abs(X) > 13 and (X + 200) % 9.0 < 0.5) or Y > 12.4: return fogged(tone(WOOD, 1.2 if Y < 12.4 else 2.2, x, y), z)   # posts, the top rail
    return planks(3.0, WOOD, seed=1)(x, y, s, t, z, wp)
for (x0, x1) in ((-90, -11.5), (11.5, 90)):
    rs.quad((x0, 0, ZW), (x1, 0, ZW), (x0, 13, ZW), wall_front, cls='wall')
def cabin(x0, x1, y0, y1, z0, z1, mat, seed, win=True):
    def front(x, y, s, t, z, wp):
        if win and 0.3 < s < 0.62 and 0.35 < t < 0.75:
            if (s - 0.3) % 0.16 < 0.02 or abs(t - 0.55) < 0.02: return WOOD[0]
            return GLOW[0] if h32(seed, 1) % 3 == 0 else STONE[0] if (x + y) % 3 else STONE[1]
        return mat(x, y, s, t, z, wp)
    rs.box(x0, x1, y0, y1, z0, z1, front, mat, top=concrete(2.0), cls='wall')
    rs.box(x0 - 0.5, x1 + 0.5, y1, y1 + 0.5, z0 - 0.5, z1 + 0.5, lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 2.2, x, y), z),
           lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 1.6, x, y), z), cls='prop')          # a rusty roof edge
cabin(-38, -21, 13, 21, 32.5, 37.5, planks(3.2, WOOD, seed=3), 1)
cabin(-19.5, -11.8, 13, 25, 31.5, 36.5, corrugated(3.0, METAL, 0.8), 2)
cabin(-58, -44, 13, 18.5, 33.0, 38.0, corrugated(2.6, METAL, 0.9), 5, win=False)
cabin(11.8, 22.5, 13, 23.5, 31.5, 36.5, planks(2.8, WARM, seed=4), 3)
cabin(24.5, 41.0, 13, 19.5, 32.5, 37.5, corrugated(3.2, METAL, 0.6), 4)
cabin(43.0, 58.0, 13, 22.0, 33.5, 38.5, planks(3.0, WOOD, seed=6), 6)
rs.box(-30.0, -27.6, 21.0, 26.5, 34.0, 36.0, steel(2.2, METAL), steel(1.6, METAL), cls='prop')                    # a water tank
rs.disc(-28.8, 26.6, 35.0, 1.3, lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 3.0 - t * 2 - s, x, y), z) if t < 0.2 else None)

# ---------------------------------------------------------------------------------------------------- the gate
def lattice(x, y, s, t, z, wp):
    """a riveted lattice pylon: two flanges and X braces"""
    X, Y, Z = wp
    ph = (Y / 3.6) % 1.0
    flange = s < 0.18 or s > 0.82
    brace = abs(s - ph) < 0.09 or abs(1 - s - ph) < 0.09
    if not (flange or brace or (Y / 3.6) % 1 < 0.06): return fogged(tone(STONE, 1.0, x, y), z)                  # dark inside
    v = 3.0 - s * 1.2 + (wn(1, Y * 0.5, X) - 0.5) * 0.8
    c = tone(METAL, v, x, y)
    if wn(3, X + Z, Y * 0.3) > 0.62: c = tone(RUSTY, v + 0.6, x, y)
    if flange and (Y * 2.0) % 1 < 0.12: c = METAL[5]
    return fogged(c, z)
GX0, GX1, GTOP = 10.4, 15.0, 29.0                                                  # pylons (inner, outer x), the beam's foot
for (x0, x1) in ((-GX1, -GX0), (GX0, GX1)):
    rs.box(x0, x1, 0, 35.0, 31.0, 35.0, lattice, steel(2.0, METAL, rust=0.6), cls='wall')
def truss(x, y, s, t, z, wp):
    """the beam over the gate: a riveted truss -- top and bottom chords, verticals and diagonals"""
    X, Y, Z = wp
    ph = ((X + 40) / 3.0) % 1.0
    chord = t < 0.16 or t > 0.84
    web = abs(ph - t) < 0.07 or ph < 0.06
    if not (chord or web): return fogged(tone(STONE, 1.2 + (wn(0, X * 0.4, Y) - 0.5), x, y), z)
    return steel(3.0, METAL, rust=0.55)(x, y, s, t, z, wp)
rs.box(-GX1 - 0.6, GX1 + 0.6, GTOP, GTOP + 6.0, 30.6, 35.2, truss, steel(2.2, METAL), bottom=steel(1.4, METAL), cls='wall')
rs.box(-GX1 - 1.2, GX1 + 1.2, GTOP + 6.0, GTOP + 7.0, 30.2, 35.6, lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 2.6, x, y), z),
       lambda x, y, s, t, z, wp: RUSTY[1], cls='prop')
ARCH = [(-GX0 + 2 * GX0 * i / 28, 20.0 + 7.0 * math.sin(math.pi * i / 28) ** 0.7, 32.6) for i in range(29)]
for a, b in zip(ARCH, ARCH[1:]):
    rs.line3(a, b, lambda x, y, s, t, z, wp: fogged(tone(METAL, 2.6, x, y) if y % 3 else METAL[1], z), w=1.0)
for i in range(1, 28, 3):                                                         # spokes up to the beam
    rs.line3(ARCH[i], (ARCH[i][0], GTOP, 32.6), lambda x, y, s, t, z, wp: fogged(METAL[1], z), w=0.3)
def board(x, y, s, t, z, wp):
    if s < 0.06 or s > 0.94 or t < 0.08 or t > 0.92: return fogged(tone(RUSTY, 2.4, x, y), z)
    return mix(STONE[0], (16, 40, 38), 0.6)
BOARDS = [(-7.6, -3.0, 19.4, 25.4, '5'), (-2.4, 4.4, 19.4, 25.4, '21')]
for (x0, x1, y0, y1, _) in BOARDS:
    rs.quad((x0, y0, 32.0), (x1, y0, 32.0), (x0, y1, 32.0), board, cls='prop')
    for xc in (x0 + 0.5, x1 - 0.5):
        rs.line3((xc, y1, 32.0), (xc, 26.6, 32.4), lambda x, y, s, t, z, wp: STONE[1], w=0.14)
SIGN = (4.0, 12.4, 14.0, 18.6, 30.2)
rs.quad((SIGN[0], SIGN[2], SIGN[4]), (SIGN[1], SIGN[2], SIGN[4]), (SIGN[0], SIGN[3], SIGN[4]), board, cls='prop')
rs.line3((SIGN[1] - 0.4, SIGN[3], SIGN[4]), (SIGN[1] - 0.4, GTOP, 31.0), lambda x, y, s, t, z, wp: STONE[1], w=0.16)
rs.line3((SIGN[0] + 0.4, SIGN[3], SIGN[4]), (SIGN[0] + 0.4, 23.0, 32.4), lambda x, y, s, t, z, wp: STONE[1], w=0.16)
# cables and moss hanging off the beam and the arch
for k in range(22):
    X0 = -GX0 + k * 0.95 + (h32(k, 3) % 5) * 0.15
    ln = 1.5 + (h32(k, 4) % 9) * 0.6
    col = LEAF[1 + h32(k, 5) % 2] if k % 3 else STONE[0]
    y0 = ARCH[max(0, min(28, int((X0 + GX0) / (2 * GX0) * 28)))][1]
    if -7.8 < X0 < 4.6 and y0 - ln < 25.6: ln = max(0.4, y0 - 25.6)
    rs.line3((X0, y0, 32.8), (X0 + 0.3, y0 - ln, 32.8), lambda x, y, s, t, z, wp, c=col: fogged(c, z), w=0.22)
for k in range(6):
    X0 = SIGN[0] + 0.6 + k * 1.15
    rs.line3((X0, SIGN[2], 31.5), (X0 + 0.1, SIGN[2] - 1.0 - (h32(k, 9) % 4) * 0.5, 31.5), lambda x, y, s, t, z, wp: fogged(LEAF[2], z), w=0.2)
rs.line3((-GX1, 24.0, 33.0), (-28.0, 19.0, 34.5), lambda x, y, s, t, z, wp: STONE[0], w=0.12, sag=1.6)
rs.line3((GX1, 23.0, 33.0), (32.0, 18.0, 34.5), lambda x, y, s, t, z, wp: STONE[0], w=0.12, sag=2.0)
def notices(x, y, s, t, z, wp):
    """a notice board crowded with pinned forms"""
    if s < 0.05 or s > 0.95 or t < 0.07 or t > 0.93: return fogged(tone(WOOD, 1.6, x, y), z)
    k = h32(int(s * 7), int(t * 4), 3)
    if k % 5 and ((s * 7) % 1) < 0.82 and ((t * 4) % 1) < 0.8:
        c = BONE[4] if k % 3 else (BONE[3] if k % 2 else GLOW[3])
        if int(((t * 4) % 1) * 9) % 2 == 0 and 0.15 < (s * 7) % 1 < 0.7: c = STONE[3]
        return fogged(c, z)
    return fogged(tone(WARM, 2.0, x, y), z)
rs.quad((-25.0, 3.0, 33.9), (-17.0, 3.0, 33.9), (-25.0 , 8.2, 33.9), notices, cls='prop')
# a street lamp right of the gate, a pipe along the wall top
rs.line3((19.0, 0.0, 24.0), (19.0, 14.0, 24.0), lambda x, y, s, t, z, wp: fogged(METAL[1] if x % 3 else METAL[2], z), w=0.4)
rs.line3((19.0, 14.0, 24.0), (17.6, 14.6, 24.0), lambda x, y, s, t, z, wp: fogged(METAL[1], z), w=0.3)
rs.disc(17.4, 14.0, 24.0, 0.55, lambda x, y, s, t, z, wp: GLOW[2] if t > 0.0 else METAL[1], cls='emit')
rs.line3((-90.0, 12.0, 33.6), (-GX1, 12.0, 33.6), lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 2.6 - (1 if y % 3 == 0 else 0), x, y), z), w=0.7)

# ---------------------------------------------------------------------------------------------------- the forms kiosk
def kiosk_front(x, y, s, t, z, wp):
    if 0.12 < s < 0.88 and 0.42 < t < 0.78:                                        # the hatch: a lit clerk inside
        u = (s - 0.5) / 0.38; v = (t - 0.42) / 0.36
        if (u * 1.4) ** 2 + ((v - 0.55) / 0.5) ** 2 < 0.25 or (abs(u) < 0.5 and v < 0.3): return STONE[1] if v > 0.55 else STONE[2]
        return GLOW[1] if (x + y) % 3 else GLOW[2]
    if 0.08 < s < 0.92 and 0.38 < t < 0.42: return fogged(tone(WOOD, 4.0, x, y), z)                          # the counter
    return corrugated(3.4, METAL, 0.6)(x, y, s, t, z, wp)
rs.box(-10.2, -5.8, 0, 7.6, 27.0, 30.4, kiosk_front, corrugated(2.6, METAL, 0.6, along_z=True), top=concrete(2.0), cls='wall')
rs.box(-10.6, -5.4, 7.6, 8.2, 26.4, 30.8, lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 2.6, x, y), z), lambda x, y, s, t, z, wp: RUSTY[1], cls='prop')

# ---------------------------------------------------------------------------------------------------- the near right: the Floors building
def flank(x, y, s, t, z, wp):
    X, Y, Z = wp
    if 20.2 < Z < 24.0 and Y < 7.6:                                                # the door to the Floors
        if Y > 7.2 or Z < 20.5 or Z > 23.7: return WOOD[0]
        v = 1.6 + (0.5 if int((Z - 20.5) / 0.6) % 2 else 0)
        if abs(Y - 3.6) < 0.25 and Z > 23.1: v = 4.5                               # the handle
        return tone(WARM, v, x, y)
    if 25.5 < Z < 28.5 and 8.0 < Y < 12.0: return GLOW[0] if (Y * 2) % 1 > 0.15 and (Z * 1.4) % 1 > 0.1 else WOOD[0]   # a lit window
    return planks_z(3.0, WOOD, seed=12)(x, y, s, t, z, wp)
rs.box(32.0, 70.0, 0, 30.0, 16.0, 31.0, planks(2.6, WOOD, seed=13), flank, cls='wall')
rs.box(31.4, 70.0, 30.0, 31.0, 15.4, 31.6, lambda x, y, s, t, z, wp: RUSTY[1], lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 2.4, x, y), z), cls='prop')
rs.quad((31.9, 7.8, 19.8), (31.9, 7.8, 24.4), (30.6, 8.6, 19.8), lambda x, y, s, t, z, wp: fogged(tone(METAL, 3.0 + s, x, y), z), cls='prop')   # an awning over the door
rs.line3((31.0, 11.0, 22.0), (31.0, 9.4, 22.0), lambda x, y, s, t, z, wp: STONE[0], w=0.12)
rs.disc(31.0, 9.1, 22.0, 0.42, lambda x, y, s, t, z, wp: GLOW[3] if s * s + t * t < 0.5 else GLOW[1], cls='emit')   # a lamp over the door

# ---------------------------------------------------------------------------------------------------- the queue
QUEUE = []
X = -44.0
while X < -12.5:
    QUEUE.append((X, 22.2 + 0.5 * math.sin(X * 0.6) + (h32(int(X * 10), 2) % 5 - 2) * 0.15))
    X += 1.7 + (h32(int(X * 10), 1) % 4) * 0.25
QUEUE += [(-11.0, 23.2), (-9.6, 24.4), (-8.2, 25.5)]
for i, (qx, qz) in enumerate(sorted(QUEUE, key=lambda q: -q[1])):
    applicant(rs, qx, qz, 100 + i, h=5.5 + (h32(i, 2) % 9) * 0.14, view=('right' if h32(i, 3) % 3 else None))
post_rope(rs, [(-42.0 + 6.0 * k, 20.6) for k in range(6)] + [(-10.0, 21.6), (-6.4, 24.0)])
applicant(rs, -3.0, 52.0, 7, h=6.0, view='front'); applicant(rs, 1.6, 66.0, 8, h=6.0, view='back'); applicant(rs, -6.0, 90.0, 9, h=6.1)   # in the street
for k in range(26):                                                               # forms littering the setts
    fx, fz = -24 + (h32(k, 21) % 300) / 10.0, 17.5 + (h32(k, 22) % 80) / 10.0
    a = (h32(k, 23) % 628) / 100.0
    c, s_ = math.cos(a) * 0.45, math.sin(a) * 0.45
    rs.quad((fx - c, 0.03, fz - s_), (fx + s_, 0.03, fz - c), (fx - s_, 0.03, fz + c),
            lambda x, y, s, t, z, wp: fogged(BONE[4] if (x + y) % 4 else BONE[2], z), cls='prop')
for (cx_, cz_) in ((20.0, 19.0), (22.6, 19.6), (21.2, 21.8)):                     # crates by the Floors door
    rs.box(cx_ - 1.1, cx_ + 1.1, 0, 2.2 + (cx_ > 21) * 0.4, cz_, cz_ + 2.0, planks(3.2, WARM, w=0.5, seed=int(cx_)),
           planks(2.4, WARM, w=0.5, seed=int(cz_)), top=planks(4.0, WARM, w=0.5, vertical=False), cls='prop')

# ---------------------------------------------------------------------------------------------------- lettering (crisp)
def letters(col):
    def put_text(txt, x0, x1, y0, y1, z, sc, c):
        (ax, ay) = proj(x0, y1, z); (bx, by) = proj(x1, y0, z)
        lines = txt.split('\n'); lh = 5 * sc + sc
        top = int((ay + by) / 2 - (len(lines) * lh - sc) / 2)
        for i, ln in enumerate(lines):
            tw = text_width(ln, sc)
            draw_text(lambda x, y: (0 <= x < W and 0 <= y < H) and col[y].__setitem__(x, c if (x + y) % 5 else mix(c, (0, 0, 0), 0.2)),
                      ln, int((ax + bx) / 2 - tw / 2), top + i * lh, sc)
    for (x0, x1, y0, y1, txt) in BOARDS:
        put_text(txt, x0, x1, y0, y1, 32.0, 6, (112, 206, 184))
    put_text('MUTATION\nFORMS', SIGN[0], SIGN[1], SIGN[2], SIGN[3], SIGN[4], 2, (112, 206, 184))

img = rs.render(INK, fog=fog_of, overlay=letters, light_gain=1.0, grime_gain=1.0, bloom=0.4, stain_gain=1.0)
img.save(f'{OUT}/gate.png')
print('done gate')
