"""The registration yard of Shed 521 (ShedRegistrationScene), 1067x600, overcast day, the shared camera.
A yard between tenements: a sagging MUTATION SERVICES OPEN banner across it on two poles, a row of prefab service
booths at the back (lit hatches, masked clerks), and in the middle rows of small school desks where applicants --
some with coral or mushroom growths -- hunch over their forms. The front is kept clear: the dream queue (the Mime,
the Vowel Seller, the Hollow Woman) and later the Senior Clerk stand on the walk line around canvas x 363..703.
The way back to the Floors is on the left.

    python3 registration_bg.py <outdir>   ->  registration.png
"""
import sys, math
from common import h32, draw_text, text_width
from shedkit import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = Raster()

rs.quad((-1400, 800, 600), (1400, 800, 600), (-1400, -300, 600), sky, cls='sky')
def yard(x, y, s, t, z, wp):
    return setts(x, y, s, t, z, wp, v0=4.0, mud=-0.08)
rs.quad((-90, 0, 3), (90, 0, 3), (-90, 0, 260), yard, cls='ground')

# ---------------------------------------------------------------------------------------------------- tenements around
rs.quad((-70, 0, 44), (70, 0, 44), (-70, 38, 44), windows_sh(concrete(3.0, STUCCO), cols=3.2, rows=4.0, lit=0.06, seed=21), cls='wall')
rs.box(-80, -27, 0, 32, 20, 44, windows_sh(concrete(2.4, STONE), cols=3.0, rows=4.0, lit=0.05, seed=22),
       windows_sh(concrete(2.8, STONE), cols=3.0, rows=4.0, lit=0.08, seed=23, along_z=True), cls='wall')
rs.box(27, 80, 0, 28, 22, 44, windows_sh(concrete(2.2, STUCCO), cols=3.0, rows=4.0, lit=0.05, seed=24),
       windows_sh(concrete(3.0, STUCCO), cols=3.0, rows=4.0, lit=0.08, seed=25, along_z=True), cls='wall')
for (x0, x1, y0, z0, z1) in ((-28.0, -27.0, 32.0, 20, 44), (27.0, 28.0, 28.0, 22, 44)):
    rs.box(x0, x1, y0, y0 + 1.0, z0, z1, lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 2.4, x, y), z),
           lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 2.0, x, y), z), cls='prop')

# ---------------------------------------------------------------------------------------------------- the service booths
def booth(x0, x1, z0, seed, open_door=True):
    d = 4.2
    def front(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = (X - x0) / (x1 - x0)
        if 0.12 < u < 0.42 and Y < 7.4:                                            # the door, open: a dark inside, a clerk
            if not open_door: return fogged(tone(METAL, 2.0 + (0.5 if (Y * 2) % 1 < 0.1 else 0), x, y), z)
            cu = (u - 0.27) / 0.15; cv = Y / 7.4
            if (cu * 1.6) ** 2 + ((cv - 0.78) / 0.12) ** 2 < 1 or (abs(cu) < 0.55 and 0.25 < cv < 0.7):         # a masked clerk
                if abs(cv - 0.79) < 0.03 and abs(abs(cu) - 0.2) < 0.12: return MYC[3]
                return STONE[1] if cv > 0.7 else (OLIVE[2] if (x + y) % 3 else OLIVE[1])
            return STONE[0]
        if 0.55 < u < 0.9 and 3.4 < Y < 7.0:                                       # the service hatch, lit
            if abs(Y - 3.6) < 0.25: return fogged(tone(WOOD, 3.6, x, y), z)
            cu = (u - 0.72) / 0.17; cv = (Y - 3.4) / 3.6
            if (cu * 1.4) ** 2 + ((cv - 0.6) / 0.25) ** 2 < 1 or (abs(cu) < 0.6 and cv < 0.35):
                if abs(cv - 0.62) < 0.05 and abs(abs(cu) - 0.25) < 0.12: return MYC[3]
                return STONE[1] if cv > 0.4 else OLIVE[1]
            return GLOW[0] if (x + y) % 3 else GLOW[1]
        if abs(Y - 8.6) < 0.3 and 0.3 < u < 0.7: return GLOW[3] if (x % 4) else GLOW[2]                         # a strip light
        return corrugated(3.0, OLIVE, 0.5)(x, y, s, t, z, wp)
    rs.box(x0, x1, 0, 9.6, z0, z0 + d, front, corrugated(2.2, OLIVE, 0.5, along_z=True), top=concrete(2.0), cls='wall')
    rs.box(x0 - 0.5, x1 + 0.5, 9.6, 10.2, z0 - 0.6, z0 + d + 0.4, lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 2.6, x, y), z),
           lambda x, y, s, t, z, wp: RUSTY[1], cls='prop')
booth(-25.0, -15.5, 29.0, 1); booth(-11.0, -1.5, 30.5, 2); booth(3.0, 12.5, 30.0, 3, open_door=False); booth(15.5, 24.5, 28.5, 4)

# ---------------------------------------------------------------------------------------------------- the banner
for px_ in (-18.0, 18.0):
    rs.line3((px_, 0.0, 25.0), (px_, 21.0, 25.0), lambda x, y, s, t, z, wp: fogged(tone(WOOD, 2.6 if x % 3 else 1.6, x, y), z), w=0.6)
def banner(x, y, s, t, z, wp):
    if t < 0.07 and int(s * 40) % 3 == 0: return None                                 # a frayed bottom edge
    if 0.83 < s < 0.86 and t < 0.35: return None                                       # a tear
    v = 3.0 + math.sin(s * 30) * 0.35 + (wn(1, s * 40, t * 3) - 0.5) * 0.3 - (0.6 if t > 0.9 or t < 0.12 else 0)
    return fogged(tone(OLIVE, v, x, y), z)
rs.quad((-17.0, 14.0, 25.0), (17.0, 14.0, 25.0), (-17.0, 19.6, 25.0), banner, cls='prop', cut=True)
for (a, b) in (((-18.0, 20.4, 25.0), (-17.0, 19.6, 25.0)), ((18.0, 20.4, 25.0), (17.0, 19.6, 25.0)), ((-18.0, 15.0, 25.0), (-17.0, 14.2, 25.0)), ((18.0, 15.0, 25.0), (17.0, 14.2, 25.0))):
    rs.line3(a, b, lambda x, y, s, t, z, wp: STONE[0], w=0.12)

# ---------------------------------------------------------------------------------------------------- the desks and the applicants
def desk(X, Z, seed):
    top = lambda x, y, s, t, z, wp: fogged(tone(WOOD, 3.6 + (wn(1, s * 8, t * 3) - 0.5), x, y), z)
    rs.box(X - 2.2, X + 2.2, 2.3, 2.6, Z - 1.0, Z + 1.0, top, top, top=top, cls='prop')
    for lx in (X - 2.0, X + 2.0):
        rs.line3((lx, 0.0, Z - 0.8), (lx, 2.3, Z - 0.8), lambda x, y, s, t, z, wp: fogged(METAL[1], z), w=0.2)
    a = (h32(seed, 3) % 60 - 30) / 100.0                                               # forms on the desk
    rs.quad((X - 0.8 + a, 2.62, Z - 0.6), (X + 0.6 + a, 2.62, Z - 0.6), (X - 0.8 + a, 2.62, Z + 0.5),
            lambda x, y, s, t, z, wp: fogged(BONE[4] if int(t * 6) % 2 or s > 0.8 else BONE[2], z), cls='prop')
DESKS = [(-15.0, 19.5), (-6.5, 21.5), (4.0, 21.0), (12.5, 19.8), (-12.0, 25.0), (0.0, 25.8), (10.0, 25.4), (18.5, 24.0)]
for i, (dx, dz) in enumerate(sorted(DESKS, key=lambda d: -d[1])):
    applicant(rs, dx, dz + 0.9, 300 + i, h=7.0, seated=True, view='front')            # behind the desk, writing
    desk(dx, dz, i)
# a few more waiting by the booths
for i, (qx, qz) in enumerate(((-14.0, 27.4), (-12.4, 27.8), (5.0, 28.2), (17.6, 26.8))):
    applicant(rs, qx, qz, 400 + i, h=6.0, view='right' if qx < 0 else 'left')
for k in range(18):                                                                   # dropped forms on the setts
    fx, fz = -20 + (h32(k, 21) % 400) / 10.0, 16.5 + (h32(k, 22) % 100) / 10.0
    a = (h32(k, 23) % 628) / 100.0; c, s_ = math.cos(a) * 0.4, math.sin(a) * 0.4
    rs.quad((fx - c, 0.03, fz - s_), (fx + s_, 0.03, fz - c), (fx - s_, 0.03, fz + c),
            lambda x, y, s, t, z, wp: fogged(BONE[4] if (x + y) % 4 else BONE[2], z), cls='prop')

def letters(col):
    (ax, ay) = proj(-17.0, 19.6, 25.0); (bx, by) = proj(17.0, 14.0, 25.0)
    lines = ['MUTATION SERVICES', 'OPEN']; sc = 4; lh = 5 * sc + 5
    top = int((ay + by) / 2 - (len(lines) * lh - 4) / 2)
    for i, ln in enumerate(lines):
        tw = text_width(ln, sc)
        def put(x, y):
            if 0 <= x < W and 0 <= y < H and col[y][x] != INK:
                col[y][x] = (196, 186, 132) if (x * 5 + y * 3) % 13 else (150, 142, 100)                 # sun-faded paint
        draw_text(put, ln, int((ax + bx) / 2 - tw / 2), top + i * lh, sc)

img = rs.render(INK, fog=fog_of, overlay=letters, light_gain=1.0, grime_gain=1.0, bloom=0.35, stain_gain=0.4)
img.save(f'{OUT}/registration.png')
print('done registration')
