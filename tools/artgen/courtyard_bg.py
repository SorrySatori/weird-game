"""The Mutation Approval Courtyard of Shed 521 (ShedCourtyardScene), 1067x600, overcast day, the shared camera.
A paved court closed by arcaded tenements: the approved mutations stand as mossy stone statues on plinths (six arms,
three heads, tentacles, antlers, a snail shell and a claw, a head of eyes, stilts), a street lamp, the courtyard's sign
on a post at the right. The court opens to the
left (back to the gate). Ortolan stands at canvas (600, 520) -- the middle front is kept clear for him and the player.

    python3 courtyard_bg.py <outdir>   ->  courtyard.png
"""
import sys, math
from common import h32, draw_text, text_width
from shedkit import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
rs = Raster()

rs.quad((-1400, 800, 600), (1400, 800, 600), (-1400, -300, 600), sky, cls='sky')

def flags(x, y, s, t, z, wp):
    """big flagstones, moss in the joints, wet patches"""
    X, _, Z = wp
    row = math.floor(Z / 2.2); col = math.floor(X / 2.6 + (row % 2) * 0.5)
    fx = (X / 2.6 + (row % 2) * 0.5) - col; fz = Z / 2.2 - row
    ex, ez = 1.3 * Z / F / 2.6, 1.3 * Z * Z / (F * CAMH) / 2.2
    v = 3.6 + (h32(col, row, 3) % 4) * 0.3 + (wn(1, X * 1.5, Z * 1.5) - 0.5) * 0.9
    if Z < 90 and (fx < ex or fz < ez):
        c = tone(LEAF, 1.6 + wn(0, X * 3, Z * 3), x, y) if wn(2, X * 0.6, Z * 0.6) > 0.42 else tone(STONE, 1.8, x, y)
        return fogged(c, Z)
    c = tone(STONE, v, x, y)
    if wn(3, X * 0.25, Z * 0.25) > 0.66: c = mix(c, tone(SKY, 4.5, x, y), 0.35)                     # wet, the sky in it
    if h32(col, row, 5) % 9 == 0: c = mix(c, LEAF[1], 0.35)                                          # a mossy slab
    return fogged(c, Z)
rs.quad((-90, 0, 3), (90, 0, 3), (-90, 0, 260), flags, cls='ground')

# ---------------------------------------------------------------------------------------------------- the tenements around
def arcade(base, along_z=False, bay=6.0, arch_h=8.0, seed=0, floors=3.4):
    """a wall with a ground-floor arcade (dark arches) and the tenement's windows above"""
    upper = facade(base, along_z=along_z, bay=bay, floors=floors, y0=arch_h + 0.8, seed=seed)
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = Z if along_z else X
        fu = (u / bay) % 1
        if Y < arch_h:                                                               # the arcade
            half = 0.34; spring = arch_h - 2.4
            inside = abs(fu - 0.5) < half and (Y < spring or ((fu - 0.5) / half) ** 2 + ((Y - spring) / 2.4) ** 2 < 1)
            if inside:
                d = max(0.0, 1 - Y / arch_h)
                return fogged(tone(STONE, 0.6 + 0.8 * (1 - d) * (1 if abs(fu - 0.5) < 0.2 else 0.5), x, y), z)
            if abs(fu - 0.5) < half + 0.05 and Y < arch_h + 0.3: return fogged(tone(STUCCO, 1.6, x, y), z)       # the arch's rim
        if abs(Y - arch_h - 0.4) < 0.4: return fogged(tone(STUCCO, 4.2, x, y), z)                     # a cornice band
        return upper(x, y, s, t, z, wp)
    return sh
ZB_ = 50.0
rs.quad((-60, 0, ZB_), (60, 0, ZB_), (-60, 34, ZB_), arcade(concrete(3.0, STUCCO), bay=6.5, seed=1), cls='wall')
rs.box(-60, 60, 34, 35.2, ZB_ - 1, ZB_ + 1, lambda x, y, s, t, z, wp: fogged(tone(STUCCO, 3.6, x, y), z), lambda x, y, s, t, z, wp: STUCCO[1], cls='prop')
rs.box(-70, -24, 0, 30, 18, ZB_, arcade(concrete(2.4, STUCCO), bay=5.0, seed=4), arcade(concrete(2.8, STUCCO), along_z=True, bay=5.5, seed=2), cls='wall')
rs.box(24, 70, 0, 26, 22, ZB_, arcade(concrete(2.2, STONE), bay=5.0, seed=5), arcade(concrete(3.0, STONE), along_z=True, bay=5.5, seed=3), cls='wall')
balconies(rs, -24.0, 18.0, ZB_, True, 5.5, 3.4, 8.8, 2, 30.0, side=1)
balconies(rs, 24.0, 22.0, ZB_, True, 5.5, 3.4, 8.8, 3, 26.0, side=-1)
for (x0, x1, y0, z0, z1) in ((-25.0, -24.0, 30.0, 18, ZB_), (24.0, 25.0, 26.0, 22, ZB_)):                    # eaves
    rs.box(x0, x1, y0, y0 + 1.0, z0, z1, lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 2.4, x, y), z),
           lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 2.0, x, y), z), cls='prop')
# the far roofs, a chimney stack, a water tower over the back wing
rs.quad((-30, 35, 52), (-12, 35, 52), (-30, 42, 52), lambda x, y, s, t, z, wp: fogged(tone(METAL, 2.4 + t, x, y), z), cls='wall')
rs.box(30, 33, 26, 34, 36, 39, concrete(2.6, STONE), concrete(1.8, STONE), cls='prop')

# ---------------------------------------------------------------------------------------------------- statues, mushrooms
# the approved mutations, in stone: the six-armed founder on a tall plinth at the front left, the others around
bizarre_statue(rs, -19.0, 23.0, 30, 'arms', h=14.5, plinth=4.2)
for (sx, sz, sd, kind, hh) in ((-15.0, 33.0, 31, 'tentacles', 9.5), (-11.5, 42.0, 32, 'stilts', 12.0), (14.5, 29.0, 34, 'shell', 9.0),
                               (12.0, 38.5, 35, 'heads', 10.5), (-1.0, 45.5, 36, 'antlers', 11.0), (5.5, 44.0, 37, 'eyes', 9.5)):
    bizarre_statue(rs, sx, sz, sd, kind, h=hh, plinth=2.8)

# ---------------------------------------------------------------------------------------------------- the lamp, the sign
rs.line3((-8.0, 0.0, 22.0), (-8.0, 15.0, 22.0), lambda x, y, s, t, z, wp: fogged(METAL[1] if x % 3 else METAL[2], z), w=0.42)
rs.line3((-8.0, 15.0, 22.0), (-6.4, 15.6, 22.0), lambda x, y, s, t, z, wp: fogged(METAL[1], z), w=0.3)
rs.disc(-6.2, 15.0, 22.0, 0.6, lambda x, y, s, t, z, wp: GLOW[2] if t > 0.0 else METAL[1], cls='emit')
SIGN = (11.4, 19.8, 7.8, 13.2, 22.0)
rs.line3((15.6, 0.0, 22.3), (15.6, 15.5, 22.3), lambda x, y, s, t, z, wp: fogged(tone(RUSTY, 2.2 + (1 if x % 3 == 0 else 0), x, y), z), w=0.55)
def sign_board(x, y, s, t, z, wp):
    if s < 0.04 or s > 0.96 or t < 0.06 or t > 0.94: return fogged(tone(RUSTY, 2.4 + (1.0 if (x + y) % 5 == 0 else 0), x, y), z)
    return mix((18, 22, 20), (40, 24, 20), wn(1, s * 6, t * 3) * 0.5)
rs.quad((SIGN[0], SIGN[2], SIGN[4]), (SIGN[1], SIGN[2], SIGN[4]), (SIGN[0], SIGN[3], SIGN[4]), sign_board, cls='prop')
for k in range(5):                                                                   # cables and moss off the board
    X0 = SIGN[0] + 0.8 + k * 1.8
    rs.line3((X0, SIGN[2], 21.9), (X0 + 0.2, SIGN[2] - 0.8 - (h32(k, 7) % 4) * 0.5, 21.9), lambda x, y, s, t, z, wp: fogged(LEAF[2] if x % 2 else STONE[0], z), w=0.18)
rs.line3((15.6, 15.0, 22.3), (22.0, 20.0, 24.5), lambda x, y, s, t, z, wp: STONE[0], w=0.12, sag=0.8)

def letters(col):
    (ax, ay) = proj(SIGN[0], SIGN[3], SIGN[4]); (bx, by) = proj(SIGN[1], SIGN[2], SIGN[4])
    lines = ['MUTATION', 'APPROVAL', 'COURTYARD']; sc = 2; lh = 5 * sc + 3
    top = int((ay + by) / 2 - (len(lines) * lh - 3) / 2)
    for i, ln in enumerate(lines):
        tw = text_width(ln, sc)
        def put(x, y):
            if 0 <= x < W and 0 <= y < H: col[y][x] = (214, 96, 72) if (x * 7 + y * 3) % 11 else (150, 60, 46)    # flaking red paint
        draw_text(put, ln, int((ax + bx) / 2 - tw / 2), top + i * lh, sc)

img = rs.render(INK, fog=fog_of, overlay=letters, light_gain=1.0, grime_gain=1.0, bloom=0.35, stain_gain=0.3)
img.save(f'{OUT}/courtyard.png')
print('done courtyard')
