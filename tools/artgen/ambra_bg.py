"""ARB Ambra -- Dr. Elphi Quarn's dream-game studio on floor 177-Quiet of the Scraper (ScraperAmbraScene), 1067x600.
A double-height loft with a panoramic window over the overcast city far below; the shared camera (raster3d.py).

  left    acoustic felt on the wall (the floor is "Quiet"), three dream recliners with dome helmets on wall arms and
          their cables, a wall monitor with sleep waves, a server rack in the far corner
  back    the panoramic window (the city in haze 177 floors down, a far airship), the backlit ARB AMBRA sign above it,
          a holo-projector with the Cardinal Feast's lizard cardinal, potted plants
  right   Elphi's long walnut desk under shelves of dream cartridges: three monitors, the cartridge burner, a desk lamp,
          her chair
  floor   polished resin that mirrors the window and the ceiling panels, a worn rug in the middle
Elphi stands in front of her desk: feet at canvas (745, 508) = world (12, 0, 17).

    python3 ambra_bg.py <outdir>   ->  ambra.png
"""
import sys, math
from common import ramp, h32, make_noise, band, FONT, draw_text, text_width
from raster3d import Raster, proj, ray, W, H, CX, HY, F, CAMH

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
R = ramp
FELT   = R('#0d1918 #132322 #1a2e2c #213a37 #2a4743 #335450 #3e625d')
FELT2  = R('#0e1820 #142029 #1b2a34 #233440 #2c404c #374d59')
PLAST  = R('#1f2a26 #2a3731 #36453d #43534a #516258 #607167 #718276 #849482')
TEALL  = R('#0f1d1c #162a28 #1e3835 #284843 #335852 #406a62 #4f7d73 #62907f')
RESIN  = R('#0a100f #0f1715 #141e1c #1a2623 #212f2b #293833 #33433d #3f4f48')
WALNUT = R('#170e09 #22150d #2f1d12 #3e2718 #4f3220 #613f29 #764e33')
STEEL  = R('#1b2123 #273032 #343e40 #434e50 #535f60 #667172 #7b8685 #949e9b')
LEATH  = R('#2a261f #3c372d #514a3c #675f4d #7e7560 #968d75 #aea58b')
SKYD   = R('#56685f #637568 #708271 #7e8f7d #8d9c89 #9ca996 #adb8a5 #c0c9b6')
CITY   = R('#26332f #2e3c37 #374540 #414f49 #4b5953 #56645d')
SCREEN = R('#08241a #0e3826 #165036 #22704b #389563 #5bbd83 #9ae8b5')
OCHRE  = R('#2a1b0e #412b17 #5b3e22 #775430 #926a40')
RUST   = R('#2c130d #461f15 #63301f #81432b')
RUGT   = R('#0e2626 #163a38 #205049 #2c665c')
LAMP   = R('#6e5424 #957130 #bb8f3e #d9ad52 #efcb73 #fff0c0')
HOLO   = R('#0f3c3c #1c6666 #309e9a #64d8cf #b4fff4')
LEAF   = R('#122418 #1a3422 #24472c #305d38 #3e7444 #528c52')
POT    = R('#2a1610 #43241a #5e3424 #7a4630 #96593d')
CORD   = R('#0c0e0e #161a1a #222828')
INK = (7, 10, 9)
LABELS = [OCHRE[4], RUST[3], RUGT[3], SCREEN[4], LEATH[5], (124, 74, 112), (150, 120, 60), (70, 96, 140), STEEL[6], (160, 60, 50)]

_nz = [make_noise(1, s, 509, 509) for s in (31, 32, 33, 34)]
def wn(i, a, b): return _nz[i](a + 3000.0, b + 3000.0)              # noise in WORLD units
def ri(r, i): return r[max(0, min(len(r) - 1, int(i)))]
def tone(r, v, x, y): return ri(r, band(v, x, y))
def mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

WX, CH, ZB = 26.0, 26.0, 48.0                                         # half width, ceiling, back wall
WIN = (-22.0, 22.0, 2.0, 23.6)                                        # the window on the back wall
def day(X, Y, Z):
    """overcast daylight from the window: strong near it, falling off towards the camera"""
    return math.exp(-(ZB - Z) / 15.0) * (0.55 + 0.45 * math.exp(-(X / 17.0) ** 2))
FOGC = (64, 78, 72)
def fog(z): return max(0.0, min(0.22, (z - 22) / 120.0))
def fogged(c, z): return mix(c, FOGC, fog(z))

rs = Raster()

# ---------------------------------------------------------------------------------------------------- the shell
def floor_sh(x, y, s, t, z, wp):
    X, _, Z = wp
    v = 1.6 + 2.6 * day(X, 0, Z) + (wn(0, X * 0.8, Z * 0.8) - 0.5) * 0.7 + (wn(1, X * 3.0, Z * 0.6) - 0.5) * 0.3
    jw = 0.9 * z / F
    if (X / 3.0) % 1 < jw / 3.0 or (Z / 3.0) % 1 < jw * z / (F * CAMH) * 3.0: v -= 0.9          # slab joints
    # the polished resin mirrors the window and the ceiling panels (traced from the mirrored eye)
    k = ZB / Z; xw, yw = X * k, -CAMH + CAMH * k
    rough = wn(2, X * 0.9, Z * 3.0)
    if WIN[0] < xw < WIN[1] and WIN[2] < yw < WIN[3] and rough > 0.28:
        v += 2.6 * (rough - 0.28) * (1.0 if ((xw - WIN[0]) % 5.5) > 0.5 else 0.3) * min(1.0, (Z - 12) / 14)
    kc = (CH + CAMH) / CAMH; xc, zc = X * kc, Z * kc
    if zc < ZB and abs(abs(xc) - 7.5) < 1.5 and (zc % 6.5) < 5.0 and rough > 0.45: v += 0.9
    return fogged(tone(RESIN, v, x, y), z)
rs.quad((-WX, 0, 3), (WX, 0, 3), (-WX, 0, ZB), floor_sh, cls='ground')

def ceil_sh(x, y, s, t, z, wp):
    X, _, Z = wp
    v = 1.0 + 1.2 * day(X, CH, Z) + (wn(0, X * 0.6 + 9, Z * 0.6) - 0.5) * 0.5
    if (X / 4.0) % 1 < 0.6 * z / F / 4.0 * 3: v -= 0.6
    return fogged(tone(PLAST, v, x, y), z)
rs.quad((-WX, CH, 3), (WX, CH, 3), (-WX, CH, ZB), ceil_sh, cls='ceil')
# light panels in two rows, cable trays, two cross beams
def panel_sh(x, y, s, t, z, wp):
    return mix((208, 228, 210), (160, 190, 170), abs(s - 0.5) * 1.6) if 0.06 < s < 0.94 and 0.03 < t < 0.97 else STEEL[2]
for cx in (-7.5, 7.5):
    for z0 in range(13, 46, 7):
        rs.quad((cx - 1.4, CH - 0.05, z0), (cx + 1.4, CH - 0.05, z0), (cx - 1.4, CH - 0.05, z0 + 5.0), panel_sh, cls='emit')
for zb_ in (20.0, 34.0):
    rs.box(-WX, WX, CH - 1.6, CH, zb_, zb_ + 1.2, lambda x, y, s, t, z, wp: fogged(tone(PLAST, 2.6 + (0.6 if t > 0.85 else 0), x, y), z),
           lambda x, y, s, t, z, wp: PLAST[1], bottom=lambda x, y, s, t, z, wp: fogged(tone(PLAST, 1.6, x, y), z), cls='ceil')

def felt_sh(x, y, s, t, z, wp):
    """acoustic felt panels in a grid (the 'Quiet' floor), a dark skirting"""
    _, Y, Z = wp
    if Y < 0.9: return fogged(tone(STEEL, 1.2, x, y), z)
    pz, py = (Z - 3) / 3.6, (Y - 1.4) / 4.2
    gap = 0.9 * z / F
    if Y < 1.4 or Y > 22.4 or (pz % 1) * 3.6 < gap or (py % 1) * 4.2 < gap: return fogged(tone(PLAST, 1.2, x, y), z)
    r_ = FELT if h32(int(pz), int(py), 3) % 3 else FELT2
    v = 2.0 + 1.6 * day(-WX, Y, Z) + 0.5 * (py % 1) + (wn(1, Z * 1.5, Y * 1.5) - 0.5) * 0.25
    return fogged(tone(r_, v, x, y), z)
def lwall_sh(x, y, s, t, z, wp):
    _, Y, Z = wp
    if Y > 22.4: return fogged(tone(PLAST, 2.2 + 1.2 * day(-WX, Y, Z), x, y), z)
    return felt_sh(x, y, s, t, z, wp)
rs.quad((-WX, 0, 3), (-WX, 0, ZB), (-WX, CH, 3), lwall_sh, cls='wall')

def rwall_sh(x, y, s, t, z, wp):
    _, Y, Z = wp
    v = 2.4 + 1.8 * day(WX, Y, Z) + (wn(0, Z * 0.9, Y * 0.9) - 0.5) * 0.6
    if Y < 0.9: v = 1.2
    return fogged(tone(PLAST, v, x, y), z)
rs.quad((WX, 0, 3), (WX, 0, ZB), (WX, CH, 3), rwall_sh, cls='wall')

def back_sh(x, y, s, t, z, wp):
    X, Y, _ = wp
    v = 3.0 + (wn(0, X * 0.9, Y * 0.9) - 0.5) * 0.6 - 0.8 * max(0.0, 1 - Y / 2.0)
    return fogged(tone(PLAST, v, x, y), z)
rs.quad((-WX, 0, ZB), (WX, 0, ZB), (-WX, CH, ZB), back_sh, cls='wall')

# the panoramic window: the city 177 floors down in the haze, a far airship
def _layer(seed, lo, hi, wmin, wmax):
    out, az = [], -0.6
    while az < 0.6:
        w_ = wmin + (h32(int(az * 1000), seed) % 100) / 100 * (wmax - wmin)
        top = lo + (h32(int(az * 1000), seed, 2) % 100) / 100 * (hi - lo)
        spire = h32(int(az * 1000), seed, 3) % 5 == 0
        out.append((az, az + w_, top, spire))
        az += w_ + (h32(int(az * 1000), seed, 4) % 4) * 0.004
    return out
LAYERS = [(_layer(11, -0.004, -0.045, 0.01, 0.03), 0.55), (_layer(12, -0.03, -0.09, 0.015, 0.04), 0.3), (_layer(13, -0.08, -0.17, 0.03, 0.06), 0.0)]
EGG = (-0.17, -0.006, 0.022, 0.03)                                                       # the Egg Cathedral's dome, far off
def outside(x, y):
    dx, dy = ray(x, y)
    if dy > 0.0 or (dy > -0.004):
        if (dx - EGG[0]) ** 2 / EGG[2] ** 2 + (dy - EGG[1]) ** 2 / EGG[3] ** 2 < 1 and dy > -0.004:
            return mix(CITY[3], SKYD[3], 0.5)
        v = 4.0 + dy * 9.0 + (wn(3, dx * 6, dy * 70) - 0.5) * 0.9 + (wn(2, dx * 20, dy * 160) - 0.5) * 0.3   # long cloud bands
        if 0.24 < dx < 0.29 and 0.05 < dy < 0.062 + 0.006 * math.sin((dx - 0.24) / 0.05 * math.pi):
            return SKYD[1]                                                               # an airship far off
        return tone(SKYD, v, x, y)
    hit = None
    for (towers, haze) in LAYERS:
        for (a0, a1, top, spire) in towers:
            if a0 < dx < a1 and (dy < top or (spire and abs(dx - (a0 + a1) / 2) < 0.0015 and dy < top + 0.025)):
                hit = (haze, a0, a1, top)
        if hit and hit[0] == haze: pass
    if hit:
        haze, a0, a1, top = hit
        c = CITY[1] if haze == 0.0 else CITY[2]
        if (dx - a0) < 0.003: c = CITY[3]                                                # the lit edge
        if haze == 0.0 and int((dx - a0) * 700) % 3 == 1 and int(-dy * 700) % 4 == 2 and h32(x // 2, y // 2, 7) % 6 == 0:
            c = (150, 132, 92)                                                           # a lit window
        return mix(c, SKYD[2], haze + 0.15 * max(0.0, 1 + dy * 6))
    v = 3.2 + dy * 10 + (wn(3, dx * 40, dy * 120) - 0.5) * 0.8                          # the haze over the roofs
    return tone(CITY, v + 1.4, x, y)
def window_sh(x, y, s, t, z, wp):
    X, Y, _ = wp
    mull = 0.18 + 0.2 * z / F * 3
    if (X - WIN[0]) % 5.0 < mull or abs(Y - 15.0) < mull * 0.8 or Y - WIN[2] < 0.4 or WIN[3] - Y < 0.4:
        return STEEL[1] if (X - WIN[0]) % 5.0 < mull * 0.5 else STEEL[3]
    return outside(x, y)
rs.quad((WIN[0], WIN[2], ZB - 0.05), (WIN[1], WIN[2], ZB - 0.05), (WIN[0], WIN[3], ZB - 0.05), window_sh, cls='emit')
rs.box(WIN[0] - 0.4, WIN[1] + 0.4, WIN[2] - 0.6, WIN[2], ZB - 1.0, ZB, lambda x, y, s, t, z, wp: STEEL[3],
       lambda x, y, s, t, z, wp: STEEL[2], top=lambda x, y, s, t, z, wp: tone(STEEL, 4.2, x, y), cls='prop')          # the sill

# ---------------------------------------------------------------------------------------------------- the left: dream rigs
def plain(r, v0, k=0.6, seed=0):
    return lambda x, y, s, t, z, wp: fogged(tone(r, v0 + (wn(seed, (wp or (x, y, z))[0] * 2 + (wp or (x, y, z))[2] * 2, (wp or (x, y, z))[1] * 2) - 0.5) * k, x, y), z)
def leather(v0):
    def sh(x, y, s, t, z, wp):
        v = v0 - (0.6 if (s * 6) % 1 < 0.1 else 0) + (wn(1, wp[0] * 1.5 + wp[2] * 1.5, wp[1] * 1.5) - 0.5) * 0.4 + 0.8 * day(*wp)
        return fogged(tone(TEALL, v, x, y), z)
    return sh
def recliner(zc):
    rs.box(-22.5, -16.0, 0, 1.3, zc - 1.0, zc + 1.0, plain(STEEL, 1.6), plain(STEEL, 2.6), plain(STEEL, 3.2))
    rs.box(-24.6, -13.4, 1.3, 2.4, zc - 1.7, zc + 1.7, leather(2.6), leather(3.4), leather(4.4))
    rs.quad((-21.0, 2.4, zc - 1.7), (-21.0, 2.4, zc + 1.7), (-24.3, 7.4, zc - 1.7), leather(4.0))                   # the backrest
    rs.quad((-21.0, 2.4, zc - 1.7), (-24.3, 7.4, zc - 1.7), (-21.0, 1.3, zc - 1.7), leather(2.2), clip=lambda a, b: a + b < 1.0)
    rs.quad((-13.4, 2.4, zc - 1.7), (-13.4, 2.4, zc + 1.7), (-12.0, 0.9, zc - 1.7), leather(3.0))                   # the footrest
    # the helmet on its wall arm, the visor faintly lit, cables down to the floor
    rs.line3((-WX, 13.0, zc + 0.6), (-23.6, 10.6, zc + 0.3), lambda x, y, s, t, z, wp: fogged(STEEL[4], z), w=0.32)
    rs.line3((-23.6, 10.6, zc + 0.3), (-23.4, 9.4, zc), lambda x, y, s, t, z, wp: fogged(STEEL[3], z), w=0.26)
    def helmet(x, y, s, t, z, wp):
        if t > 0.55: return None if t > 0.75 else STEEL[1]                                                         # the open rim
        if 0.18 < t < 0.42 and s > -0.5: return SCREEN[2] if (x + y) % 3 else SCREEN[3]                         # the visor band
        v = 4.4 - t * 2.0 - s * 1.2 + (0.9 if s * s + t * t < 0.14 and s < 0 and t < 0 else 0)
        return fogged(tone(STEEL, v, x, y), z)
    rs.disc(-23.2, 8.4, zc, 1.05, helmet)
    rs.line3((-23.6, 8.2, zc + 0.7), (-25.4, 0.1, zc + 1.6), lambda x, y, s, t, z, wp: CORD[1], w=0.16, sag=-1.2)
    rs.line3((-22.4, 8.0, zc + 0.9), (-24.8, 0.1, zc + 2.2), lambda x, y, s, t, z, wp: CORD[2], w=0.12, sag=-0.8)
for zc in (18.4, 25.8, 33.2): recliner(zc)
def eeg_sh(x, y, s, t, z, wp):
    if s < 0.04 or s > 0.96 or t < 0.06 or t > 0.94: return STEEL[1]
    for k, ph in ((0.3, 0.0), (0.55, 1.7), (0.8, 3.1)):
        w_ = k + 0.07 * math.sin(s * 40 + ph) * math.sin(s * 7 + ph) + (0.05 if (s * 13 + ph) % 1 < 0.06 else 0)
        if abs(t - w_) < 0.025: return SCREEN[6] if k < 0.5 else SCREEN[5]
    return SCREEN[0] if (x + y) % 2 else SCREEN[1]
rs.quad((-WX + 0.1, 9.0, 36.5), (-WX + 0.1, 9.0, 41.5), (-WX + 0.1, 13.4, 36.5), eeg_sh, cls='emit')
def rack_front(x, y, s, t, z, wp):
    if (t * 14) % 1 < 0.12: return STEEL[0]
    if s > 0.72 and (s * 30) % 1 < 0.4 and (t * 14) % 1 > 0.5 and h32(int(t * 14), int(s * 30), 2) % 3: return SCREEN[5] if h32(int(t * 14), 3) % 4 else LAMP[3]
    return fogged(tone(STEEL, 1.6 + (wn(0, s * 9, t * 9) - 0.5) * 0.6, x, y), z)
rs.box(-25.6, -21.4, 0, 15.0, 42.0, 46.0, rack_front, plain(STEEL, 1.8), cls='prop')

# ---------------------------------------------------------------------------------------------------- the back: plants, holo
def potted(X, Z, h, seed):
    rs.box(X - 1.2, X + 1.2, 0, 2.4, Z - 1.0, Z + 1.0, plain(POT, 2.6), plain(POT, 1.8), plain(POT, 1.2))
    for k in range(int(h * 7)):                                                           # broad drooping leaves
        a = h32(seed, k) % 360 * math.pi / 180; Y = 2.8 + (h32(seed, k, 3) % 100) / 100 * h
        r_ = (0.4 + (h32(seed, k, 2) % 10) * 0.16) * (0.5 + 0.7 * (Y - 2.8) / h)
        sh = 3.0 + (h32(seed, k, 5) % 3) * 0.5
        rs.disc(X + math.cos(a) * r_ * 1.6, Y - abs(math.cos(a)) * 0.6, Z - 0.2 + math.sin(a) * 0.8, 0.45 + (h32(seed, k, 4) % 5) * 0.07,
                lambda x, y, s, t, z, wp, sh=sh: fogged(tone(LEAF, sh - t * 1.4 - s * 0.6 + 1.0 * day(0, 6, z), x, y), z) if abs(s - t) < 0.75 else None)
potted(-16.8, 44.6, 9.0, 3); potted(17.4, 44.4, 6.5, 8)
rs.box(9.6, 11.6, 0, 2.0, 38.6, 40.6, plain(STEEL, 2.0), plain(STEEL, 2.8), plain(STEEL, 3.6))
def holo(x, y, s, t, z, wp):
    """the lizard cardinal of The Cardinal Feast, slowly turning in a cone of light (dotted, like a hologram)"""
    u, v = s - 0.5, 1 - t                                                                  # v: 0 at the bottom
    if abs(u) > 0.08 + 0.42 * v: return None
    body = (abs(u) < 0.13 - 0.06 * v and v < 0.62) or ((u / 0.11) ** 2 + ((v - 0.7) / 0.08) ** 2 < 1) or \
           (abs(u) < 0.05 * (1 - (v - 0.76) / 0.18) and 0.76 < v < 0.94) or (0.68 < v < 0.73 and 0.04 < u < 0.2)   # robe, head, mitre, snout
    if body: return HOLO[4] if y % 2 else HOLO[3]
    if (x + y) % 2 or y % 3 == 0: return None
    return HOLO[2] if v < 0.3 else HOLO[1]
rs.quad((8.2, 2.0, 39.6), (13.0, 2.0, 39.6), (8.2, 9.5, 39.6), holo, cls='emit', cut=True)

# ---------------------------------------------------------------------------------------------------- the right: Elphi's desk
def walnut(v0):
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = v0 + (wn(1, Z * 0.7, Y * 9.0) - 0.5) * 0.9 + 0.7 * day(X, Y, Z)
        return fogged(tone(WALNUT, v, x, y), z)
    return sh
rs.box(19.0, 23.6, 2.65, 2.95, 15.2, 35.2, walnut(3.4), walnut(4.0), walnut(4.6))
rs.box(19.4, 23.4, 0, 2.65, 15.4, 18.6, walnut(2.4), walnut(3.0))
rs.box(19.4, 23.4, 0, 2.65, 31.8, 35.0, walnut(2.4), walnut(3.0))
for zd in (15.4, 31.8):                                                                    # drawer pulls
    for yy in (0.8, 1.6, 2.3): rs.line3((19.35, yy, zd + 0.9), (19.35, yy, zd + 2.3), lambda x, y, s, t, z, wp: STEEL[5], w=0.08)
def screen_sh(kind):
    def sh(x, y, s, t, z, wp):
        if s < 0.05 or s > 0.95 or t < 0.07 or t > 0.93: return STEEL[1]
        if kind == 0:                                                                      # dream waves
            for k in (0.35, 0.65):
                if abs(t - k - 0.12 * math.sin(s * 18 + k * 9)) < 0.03: return SCREEN[6]
        elif kind == 1:                                                                    # code
            if (t * 14) % 1 < 0.45 and s < 0.15 + (h32(int(t * 14), 4) % 7) * 0.11: return SCREEN[5] if (x % 3) else SCREEN[4]
        else:                                                                              # the cartridge's map
            if abs(math.hypot(s - 0.5, (t - 0.5) * 0.7) - 0.25) < 0.03 or (abs(s - 0.5) < 0.02) or abs(t - 0.5) < 0.02: return SCREEN[5]
        return SCREEN[1] if (x + y) % 2 else SCREEN[2]
    return sh
for i, z0 in enumerate((18.8, 23.2, 27.6)):
    rs.line3((21.6, 2.95, z0 + 1.9), (21.6, 3.7, z0 + 1.9), lambda x, y, s, t, z, wp: STEEL[2], w=0.3)
    rs.box(20.7, 21.1, 3.7, 6.3, z0, z0 + 3.8, lambda x, y, s, t, z, wp: STEEL[1], screen_sh(i), cls='emit')
rs.box(19.8, 20.6, 2.95, 3.1, 20.0, 26.0, plain(STEEL, 2.4), plain(STEEL, 3.0), plain(STEEL, 4.2))          # keyboard
def burner(x, y, s, t, z, wp):
    if 0.35 < t < 0.5 and 0.2 < s < 0.8: return LAMP[4] if (x + y) % 2 else LAMP[3]                       # the glowing slot
    return fogged(tone(STEEL, 2.6 + (wn(0, s * 5, t * 5) - 0.5) * 0.5, x, y), z)
rs.box(20.0, 22.8, 2.95, 4.3, 30.4, 33.4, plain(STEEL, 2.2), burner, plain(STEEL, 3.8))
rs.disc(21.0, 3.15, 16.6, 0.5, lambda x, y, s, t, z, wp: STEEL[2])                                           # the desk lamp
rs.line3((21.0, 3.1, 16.6), (20.4, 6.1, 16.9), lambda x, y, s, t, z, wp: STEEL[3], w=0.14)
rs.line3((20.4, 6.1, 16.9), (19.4, 6.0, 17.6), lambda x, y, s, t, z, wp: STEEL[3], w=0.14)
rs.disc(19.2, 5.8, 17.6, 0.62, lambda x, y, s, t, z, wp: LAMP[5] if t > 0.25 else (WALNUT[1] if t < -0.2 else STEEL[2]), cls='emit')
# her chair, pushed back from the desk
rs.box(15.8, 18.4, 2.0, 2.6, 21.6, 24.0, plain(LEATH, 1.4), plain(LEATH, 2.0), plain(LEATH, 2.8))
rs.box(18.0, 18.5, 2.6, 6.4, 21.6, 24.0, plain(LEATH, 1.2), plain(LEATH, 1.8))
rs.line3((17.1, 0.4, 22.8), (17.1, 2.0, 22.8), lambda x, y, s, t, z, wp: STEEL[2], w=0.25)
for a in range(5):
    an = a * 2 * math.pi / 5
    rs.line3((17.1, 0.4, 22.8), (17.1 + math.cos(an) * 1.5, 0.15, 22.8 + math.sin(an) * 1.5), lambda x, y, s, t, z, wp: STEEL[1], w=0.18)
# shelves of dream cartridges on the right wall, above the desk
for yb in (8.0, 11.0, 14.0, 17.0, 20.0):
    rs.box(23.4, WX, yb - 0.25, yb, 15.2, 35.2, walnut(3.0), walnut(3.6), top=walnut(4.2), bottom=walnut(1.6))
    z = 15.5
    while z < 34.8:
        w_ = 0.42 + (h32(int(z * 10), int(yb)) % 4) * 0.08
        hh = 1.5 + (h32(int(z * 10), int(yb), 2) % 5) * 0.16
        if h32(int(z * 10), int(yb), 3) % 11 == 0: z += 0.9; continue                                     # a gap
        lab = LABELS[h32(int(z * 10), int(yb), 4) % len(LABELS)]
        def spine(x, y, s, t, z_, wp, lab=lab, k=h32(int(z * 10), int(yb), 5) % 3):
            if 0.3 < t < 0.55 and 0.15 < s < 0.85: return lab
            return fogged(mix((22, 26, 26), (58, 64, 62), 0.3 + 0.25 * k), z_)
        rs.box(23.7, 25.6, yb, yb + hh, z, z + w_, lambda x, y, s, t, z_, wp: (30, 34, 34), spine)
        z += w_ + 0.05
# the elevator door at the near right is behind the camera; a coat stand by the desk, Elphi's coat on it
rs.line3((17.6, 0.0, 33.6), (17.6, 8.4, 33.6), lambda x, y, s, t, z, wp: WALNUT[2], w=0.2)
rs.disc(17.6, 6.6, 33.5, 1.0, lambda x, y, s, t, z, wp: fogged(tone(LEATH, 4.8 - t * 2.4, x, y), z))

# ---------------------------------------------------------------------------------------------------- the rug
def rug(x, y, s, t, z, wp):
    X, _, Z = wp
    u, v = abs(s - 0.5) * 2, abs(t - 0.5) * 2
    dim = 0.35
    worn = wn(1, X * 1.2, Z * 1.2) > 0.68 and u < 0.8 and v < 0.85                                       # trodden bald
    if u > 0.9 or v > 0.93: c = tone(RUST, 2.2, x, y)
    elif u > 0.84 or v > 0.88: c = tone(OCHRE, 3.4 if (int(s * 60) + int(t * 60)) % 2 else 2.6, x, y)
    elif abs(math.hypot(u * 1.4, v) - 0.5) < 0.05 or abs(u - v * 0.7) < 0.03: c = tone(OCHRE, 3.6, x, y)
    elif math.hypot(u * 1.4, v) < 0.5: c = tone(RUGT, 2.4 + (0.6 if (int(s * 24) + int(t * 24)) % 2 else 0), x, y)
    else: c = tone(RUST, 2.6 + (wn(2, X * 2, Z * 2) - 0.5), x, y)
    if worn: c = mix(c, OCHRE[2], 0.45)
    return fogged(mix(c, (0, 0, 0), dim), z)
rs.quad((-6.5, 0.02, 15.0), (6.5, 0.02, 15.0), (-6.5, 0.02, 29.0), rug, cls='ground')

# ---------------------------------------------------------------------------------------------------- the sign
def sign(col):
    """ARB AMBRA, backlit on the wall above the window, with the studio's emblem (a ring between two dots)"""
    (sx, sy) = proj(0, 24.6, ZB)
    txt = 'ARB AMBRA'; tw = text_width(txt, 2)
    pts = set(); draw_text(lambda x, y: pts.add((x, y)), txt, int(sx - tw // 2 + 16), int(sy - 4), 2)
    ex, ey = int(sx - tw // 2 - 12), int(sy + 1)
    for dy in range(-6, 7):
        for dx in range(-14, 14):
            r_ = math.hypot(dx, dy)
            if 3.0 <= r_ <= 5.2 or math.hypot(dx + 10, dy) <= 2.2 or math.hypot(dx - 10, dy) <= 2.2: pts.add((ex + dx, ey + dy))
    for (x, y) in pts:
        if 0 <= x < W and 0 <= y < H:
            col[y][x] = SCREEN[6]
            if (x + 1, y + 1) not in pts and x + 1 < W and y + 1 < H: col[y + 1][x + 1] = mix(col[y + 1][x + 1], (0, 0, 0), 0.6)

# a dark fascia over the window carries the sign
rs.quad((WIN[0] - 1.0, WIN[3] + 0.3, ZB - 0.3), (WIN[1] + 1.0, WIN[3] + 0.3, ZB - 0.3), (WIN[0] - 1.0, CH - 0.2, ZB - 0.3),
        lambda x, y, s, t, z, wp: tone(PLAST, 0.8 + (0.6 if t < 0.08 else 0), x, y), cls='prop')
img = rs.render(INK, fog=fog, overlay=sign, light_gain=1.0, grime_gain=0.55, bloom=0.45, stain_gain=0.15, damp_gain=0.2)
img.save(f'{OUT}/ambra.png')
print('done ambra')
