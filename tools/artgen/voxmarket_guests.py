"""The Voxmarket auction guests (VoxmarketHallScene; the Heir also at HarborScene / PithReclaimersRoomScene), redrawn with
the character renderer (rig.py, the Edgar / Kloor / Zerren bar) after their old AI pictures (sisterCalyx.png,
HeartbrokerLune.png, silence.png, heirToAquarium.png -- now only references for who they are). Facing the viewer, scale 1,
soles on the bottom rows; 8 calm idle frames each (the scene sequences them with holds).
  sister_calyx      128x176  Sister Calyx of the Ink Tribunal: a tall, stooping figure in a layered dusk-violet robe gone
                             to moss and rags, thorny growths and verdigris knots on the shoulders, a deep hood with two
                             green-glowing eyes and mossy filaments hanging from the dark; a bead belt with a rosary and a
                             vial; in her left (viewer's right) a gnarled staff with a dripping lamp-pod, in her right a
                             moss-caged lantern glowing green. Verdigris hands, ink-black nails.
                             0 rest  1 inhale  2 the lantern swells bright  3 the eyes narrow  4-5 the staff's pod sways and
                             a drip falls  6 she tilts her head toward the lots  7 exhale
  heartbroker_lune  128x192  Heartbroker Lune: tall, in a pointed plum hood and layered robes (gold-trimmed purple over
                             maroon, a parchment tabard with a heart sigil), a cracked bone beak-mask; a brass harness
                             carrying beating hearts in blown-glass globes -- two on arms arching over her shoulders, one in a
                             flask at her chest, a cluster at her hips (red, wax-pale, blue, green); lacquered grey-green
                             gloves, a gothic candle lantern in one hand, the other raised with a dangling heart charm,
                             taloned feet under the hem.
                             0 rest  1 inhale  2 the hearts beat  3 one heart beats out of turn  4 the flame gutters, the
                             raised fingers curl  5 the hearts beat again  6 the mask tilts  7 exhale
  silence           128x128  The Silence Beneath the Stairwell: a small crouching heap of dark, wet, dripping shag under a
                             hood -- almost no face, only a smoother dark where features should be; a heavy clawed paw
                             on the floor, and a narrow hand that comes out of a sleeve-fold to sign: two fingers, five,
                             none. A dark wet patch under it.
                             0 rest  1 the shoulders rise  2 the hand appears, two fingers  3 five  4 none (a fist)
                             5 the hand withdraws  6 the shoulders fall, a drip falls  7 two dim points in the dark
  heir_aquarium     128x176  The Heir to the Yellow Aquarium: a tall man with a green cephalopod head (a knobbed mantle,
                             round amber eyes with bar pupils, a beard of tentacles), the mantle half-translucent with
                             yellow-lit embryos drifting inside; a long rust-brown coat (a brass plaque on the collar)
                             over an olive waistcoat, brown trousers, boots; green webbed hands.
                             0 rest  1 inhale  2 blink (the lids slide up)  3-4 the tentacles drift left, then right
                             5 the embryos turn and brighten  6 the head tilts toward a sound  7 exhale
python3 voxmarket_guests.py <outdir> [ids]  ->  <id>.png sheets + <id>/<n>.png + vox_guests.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK, h32
import rig
from rig import Rig, Mat, norm
from feral_toast import ik, worm, lerp
from symbionts import curve
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
R = ramp
WARM_INK = (30, 20, 18)

# ---------------------------------------------------------------------------------------------------------- palettes
# Sister Calyx
VIOLET = R('#0e0a10 #151018 #1d1621 #251d2a #2e2534 #382e3f #43384a #4f4356 #5b4e62 #685a6e')
MOSS   = R('#16140b #211e10 #2c2815 #39341b #474021 #554e29 #645c32 #746b3c #847a47 #958a53')
RAG    = R('#241e14 #352c1d #483d28 #5c4f34 #706141 #84744f #97875e')
TEAL   = R('#0c1a19 #132824 #1b3832 #244940 #2f5c50 #3c6f61 #4c8373 #5f9786 #77ab98')
BARK   = R('#110b08 #1b130d #261b12 #332418 #412e1e #503925 #60452d')
GLOW   = [(46, 70, 18), (84, 128, 26), (136, 186, 44), (190, 230, 88), (232, 252, 160), (252, 255, 226)]
# Heartbroker Lune
PLUM   = R('#100b12 #170f1a #1f1522 #281a2b #312034 #3a273e #443048 #4f3852 #5a425d #664c68')
MAROON = R('#1a080b #280c10 #381116 #49171c #5b1e22 #6e262a #823033')
GOLD   = R('#22170b #382710 #553d17 #73551f #8f6c29 #a98436 #c09e4c #d6ba70')
PARCH  = R('#3a3022 #504430 #675a40 #7f7152 #968765 #ab9c79 #bdb08e')
GLOVE  = R('#10150f #192018 #232c21 #2e392c #3a4737 #475643 #556550 #64745e #74846c')
BONE   = R('#2e2a22 #474134 #615949 #7b725f #958b75 #ada38b #c3b9a0 #d6cdb4 #e4dcc6')
HEART  = R('#240a0c #3c1014 #58181c #742226 #902e2e #a83e3a #be564c #d07462')
HEARTP = R('#4a3a34 #6a5448 #8a705e #a88c76 #c0a68e #d4bea6')          # wax-pale
HEARTB = R('#141c2c #1e2a40 #2a3a56 #384c6c #4a6082 #607698')          # blue
HEARTG = R('#142012 #1e301a #2a4224 #36562e #466a3a #5a7e4a')          # green
GLASS  = [(70, 78, 86), (112, 124, 132), (160, 172, 178), (206, 216, 220), (240, 246, 248)]
FLAME  = [(120, 50, 16), (190, 96, 28), (236, 156, 52), (252, 206, 104), (255, 240, 190)]
# The Silence
SHAG   = R('#040303 #070605 #0b0908 #0f0d0b #14110e #191512 #1f1a15 #262019 #2f271d #3b3022 #4a3c2a #5e4c33')
SHAND  = R('#1c1916 #29241f #37302a #463e36 #564c43 #675c51 #796d61 #8b7f71')
CLAW   = R('#2c261e #463e31 #635947 #82775f #9c9077')
# The Heir
SQUID  = R('#0b160e #112013 #182a19 #1f3620 #284327 #31512e #3b5f35 #466d3c #527b42 #608948 #70974f #82a457')
EYEA   = [(70, 44, 8), (140, 92, 14), (204, 148, 26), (238, 196, 52), (252, 228, 120)]
YOLK   = [(150, 120, 30), (200, 168, 48), (236, 208, 84), (252, 236, 150)]
COAT   = R('#120a07 #1b0f0a #26150e #311b12 #3d2217 #49291d #553123 #623a29 #6f4430 #7d4e38')
WAIST  = R('#111308 #1a1d0b #24280f #2f3313 #3a3f18 #45491d #515423 #5d5f2a')
TROU   = R('#100b08 #19110d #231812 #2e2018 #39281e #453125')
BOOT   = R('#0e0806 #180e0a #23150f #2f1d15 #3c261b #4a3022 #5a3b2a')

# a few extra textures for the renderer's table
rig.TEX['moss'] = lambda x, y: ((rig.nF(x * 1.8, y * 1.8) - 0.5) * 0.22 + (rig.nM(x * 1.3, y * 1.3) - 0.5) * 0.16
                                + (0.05 if h32(x, y, 3) % 7 == 0 else 0))
rig.TEX['robe'] = lambda x, y: ((rig.nF(x * 1.6, y * 1.6) - 0.5) * 0.10 + (rig.nM(x * 1.0, y * 0.6) - 0.5) * 0.18
                                + (rig.nL(x * 0.7 + 30, y * 0.7) - 0.5) * 0.18 + (0.02 if (x + 2 * y) % 3 == 0 else -0.01))
rig.TEX['shag'] = lambda x, y: ((rig.nF(x * 1.3, y * 0.2) - 0.5) * 0.1 + (rig.nM(x * 0.9, y * 0.5) - 0.5) * 0.14
                                - (0.1 if h32(x, y >> 3, 9) % 5 == 0 else 0))
rig.TEX['squid'] = lambda x, y: ((rig.nM(x * 1.3, y * 1.3) - 0.5) * 0.16 + (rig.nF(x, y) - 0.5) * 0.06
                                 + (0.22 if rig.nL(x * 1.9 + 11, y * 1.9 + 5) > 0.72 else 0))           # lime spots
rig.TEX['tweed'] = lambda x, y: ((rig.nF(x * 1.7, y * 1.7) - 0.5) * 0.10 + (rig.nM(x * 1.1, y * 1.1) - 0.5) * 0.16
                                 + (rig.nL(x * 0.7 + 40, y * 0.7) - 0.5) * 0.22 + (0.025 if (x + 2 * y) % 3 == 0 else -0.01))
rig.TEX['vest'] = lambda x, y: ((rig.nF(x * 2.0, y * 2.0) - 0.5) * 0.10 + (rig.nL(x, y + 30) - 0.5) * 0.16
                                + (0.03 if y % 2 else -0.02))
rig.TEX['lacquer'] = lambda x, y: (rig.nM(x * 0.8, y * 0.8) - 0.5) * 0.06

M = {
    # Calyx
    'violet': Mat(VIOLET, 'robe', 0.16), 'moss': Mat(MOSS, 'moss', 0.18), 'rag': Mat(RAG, 'fabric', 0.2),
    'teal': Mat(TEAL, 'skin', 0.24, 0.2), 'tealgrow': Mat(TEAL, 'moss', 0.26, 0.35), 'bark': Mat(BARK, 'wood', 0.18, 0.1),
    # Lune
    'plum': Mat(PLUM, 'robe', 0.16), 'maroon': Mat(MAROON, 'fabric', 0.18), 'gold': Mat(GOLD, 'metal', 0.26, 0.8),
    'parch': Mat(PARCH, 'fabric', 0.3), 'glove': Mat(GLOVE, 'lacquer', 0.2, 0.7), 'bone': Mat(BONE, 'skin', 0.3, 0.25),
    # Silence
    'shag': Mat(SHAG, 'shag', 0.1), 'shand': Mat(SHAND, 'skin', 0.24, 0.15), 'claw': Mat(CLAW, 'plain', 0.3, 0.4),
    # Heir
    'squid': Mat(SQUID, 'squid', 0.22, 0.3), 'coat': Mat(COAT, 'tweed', 0.17), 'waist': Mat(WAIST, 'vest', 0.2, 0.05),
    'trou': Mat(TROU, 'fabric', 0.2), 'boot': Mat(BOOT, 'leather', 0.2, 0.6),
}


def mix(a, b, t): return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def group_at(r, x, y):
    e = r.buf.get((int(x), int(y)))
    return r.groups[e[2]] if e else None


def color_at(r, x, y):
    """the colour a buffer pixel will get (fixed colour or its ramp at the current tone, no dither)"""
    e = r.buf.get((int(x), int(y)))
    if not e: return None
    if e[3]: return e[3]
    rr = e[0].ramp
    return rr[max(0, min(len(rr) - 1, int(round(e[1] * (len(rr) - 1)))))]


def finish(im, halos=()):
    """warm the renderer's neutral ink; add soft light halos (x, y, radius, colour, strength) on empty pixels"""
    px = im.load()
    W, H = im.size
    for y in range(H):
        for x in range(W):
            if px[x, y] == (18, 14, 12, 255): px[x, y] = WARM_INK + (255,)
    for (hx, hy, rad, col, k) in halos:
        for y in range(int(hy - rad) - 1, int(hy + rad) + 2):
            for x in range(int(hx - rad) - 1, int(hx + rad) + 2):
                if not (0 <= x < W and 0 <= y < H) or px[x, y][3]: continue
                d = math.hypot(x + 0.5 - hx, y + 0.5 - hy) / rad
                if d >= 1: continue
                a = (1 - d) ** 1.6 * k
                if a * 16 < rig.BAYER[y % 4][x % 4] * 0.9 + 1: continue        # a dithered falloff, a few levels only
                px[x, y] = col + (int(min(150, 60 + a * 120)),)
    return im


def hand_fingers(r, base, ang, lens, spread, rad, mat, g, curl=0.0):
    """a fan of fingers from `base` around direction `ang` (radians, screen coords); curl bends the tips back"""
    n = len(lens)
    for k, ln in enumerate(lens):
        a = ang + (k - (n - 1) / 2) * spread
        mid = (base[0] + math.cos(a) * ln * 0.55, base[1] + math.sin(a) * ln * 0.55)
        a2 = a + curl
        tip = (mid[0] + math.cos(a2) * ln * 0.45, mid[1] + math.sin(a2) * ln * 0.45)
        r.tube(base, mid, rad, rad * 0.9, mat, group=g + 'f%d' % k)
        r.tube(mid, tip, rad * 0.9, rad * 0.7, mat, group=g + 'f%d' % k)
        seam(r, g + 'f%d' % k, 0.14)


# ======================================================================================================= the Heir
HEIR_POSE = [dict(b=0), dict(b=1), dict(b=0, blink=1), dict(b=0, sway=-1), dict(b=0, sway=1),
             dict(b=0, yolk=1), dict(b=0, tilt=1), dict(b=1, settle=1)]


def heir(P, f):
    W, H = 128, 176
    r = Rig(W, H)
    cx = 64
    b = P.get('b', 0)
    st = P.get('settle', 0)                                       # exhale: the head settles a beat before the shoulders
    U = lambda y: y - b if (y < 112 and not (st and y < 62)) else y   # the breath lifts everything above the belt
    # legs and boots
    for sx in (-1, 1):
        hip, foot = (cx + sx * 5.5, 110), (cx + sx * 7.5, 163)
        knee = (cx + sx * 6.4, 137)
        r.tube(hip, knee, 6.4, 5.4, M['trou'], group='leg%d' % sx, folds=lambda u, sd: -0.22 if abs(sd) < 0.1 and u > 0.3 else 0)
        r.tube(knee, foot, 5.4, 4.8, M['trou'], group='leg%d' % sx,
               folds=lambda u, sd, sx=sx: (-0.2 if u > 0.8 and abs(sd + sx * 0.3) < 0.14 else 0))
        r.tube((foot[0], foot[1] - 7), (foot[0] + sx * 0.5, foot[1] + 3), 5.0, 5.0, M['boot'], group='boot%d' % sx,
               folds=lambda u, sd: 0.16 if u < 0.12 else 0)
        r.ellipsoid(foot[0] + sx * 1.6, 168.6, 7.6, 3.6, M['boot'], group='boot%d' % sx)
        r.ellipsoid(foot[0] + sx * 0.8, 166.2, 4.8, 2.2, M['boot'], lift=0.1, group='boot%d' % sx)
        r.fixed(foot[0] + sx * 1.6 - 3, 168, BOOT[6]); r.fixed(foot[0] + sx * 1.6 - 2, 168, BOOT[5])
        for x in range(int(foot[0] + sx * 1.6 - 7), int(foot[0] + sx * 1.6 + 8)): r.fixed(x, 172, BOOT[0])   # the sole
    r.poly([(cx - 12, 102), (cx + 12, 102), (cx + 12.5, 114), (cx + 2, 119), (cx, 115), (cx - 2, 119), (cx - 12.5, 114)], M['trou'],
           group='pelvis', vfun=lambda x, y: -0.18 if x in (cx - 1, cx) and y > 108 else 0)
    # the waistcoat: olive, three dark buttons, two welt pockets, its points over the belt
    vest = [(cx - 10, U(66)), (cx + 10, U(66)), (cx + 13, U(80)), (cx + 14, U(98)), (cx + 13, 112), (cx + 1, 117), (cx - 1, 117),
            (cx - 13, 112), (cx - 14, U(98)), (cx - 13, U(80))]
    r.poly(vest, M['waist'], round_=0.9, tilt=0.12, group='vest',
           vfun=lambda x, y: (-0.24 if x == cx and y > U(72) else 0) + (0.1 if x == cx - 1 and y > U(72) else 0) + (-0.1 if y > 108 else 0))
    for y in (84, 94, 104):
        yy = U(y); r.fixed(cx, yy, (44, 30, 20)); r.fixed(cx - 1, yy, (70, 52, 34)); r.fixed(cx, yy + 1, (24, 16, 12))
    for sx in (-1, 1):
        for x in range(cx + sx * 5, cx + sx * 11, sx): r.fixed(x, U(100), WAIST[0]); r.darken(x, U(101), -0.12)
    # the coat: a standing collar, two long panels open over the waistcoat, broad lapels
    r.ellipsoid(cx, U(66), 15, 5.0, M['coat'], lift=-0.12, group='collar')
    def panel_v(sx):
        folds = [(cx + sx * 15.5, 98, 0.10), (cx + sx * 20.5, 108, 0.16), (cx + sx * 13.0, 120, 0.05)]
        def v(x, y):
            out = 0.0
            for (fx, fy, slant) in folds:
                if y < fy: continue
                px = fx + sx * (y - fy) * slant
                d = (x + 0.5 - px) * sx
                if -0.5 <= d < 0.5: out -= 0.3
                elif -1.5 <= d < -0.5: out += 0.12
            if 138 <= y < 148: out -= (y - 138) * 0.016                        # harbour damp creeping up the hem
            for (sx_, sy, sr) in ((-19, 132, 2.2), (21, 104, 1.8), (-22, 92, 1.6), (17, 142, 2.0)):   # salt and old stains
                if (x + 0.5 - (cx + sx_)) ** 2 + ((y - sy) * 1.3) ** 2 < sr * sr: out -= 0.14
            if y >= 148: out += 0.1
            if y >= 150: out -= 0.24
            return out
        return v
    for sx in (-1, 1):
        pts = [(cx + sx * 9, U(63)), (cx + sx * 19, U(67)), (cx + sx * 21.5, U(76)), (cx + sx * 21.5, 102), (cx + sx * 23.5, 128),
               (cx + sx * 25.5, 150), (cx + sx * 17, 152), (cx + sx * 10.5, 152.5), (cx + sx * 10.5, 124),
               (cx + sx * 11.5, 108), (cx + sx * 12.5, U(92)), (cx + sx * 9.6, U(67))]
        r.poly(pts, M['coat'], round_=0.75, group='coat%d' % sx, vfun=panel_v(sx))
        lap = [(cx + sx * 9.2, U(64)), (cx + sx * 14.5, U(67)), (cx + sx * 13.5, U(70)), (cx + sx * 18.5, U(74)), (cx + sx * 12.6, U(93)),
               (cx + sx * 10.6, U(78))]
        r.poly(lap, M['coat'], lift=0.13, round_=0.5, group='lapel%d' % sx)
        seam(r, 'lapel%d' % sx, 0.2)
        x0 = cx + sx * 12.5                                                     # hip-pocket flaps
        r.poly([(x0, 118), (x0 + sx * 9.0, 117.5), (x0 + sx * 9.2, 121.5), (x0, 122)], M['coat'], lift=0.1, round_=0.4, group='flap%d' % sx)
        seam(r, 'flap%d' % sx, 0.28)
    # the brass plaque on the collar (Heir to the Yellow Aquarium)
    for (x, y, c) in ((cx + 12, U(77), GOLD[6]), (cx + 13, U(77), GOLD[5]), (cx + 14, U(77), GOLD[4]), (cx + 15, U(78), GOLD[3]),
                      (cx + 12, U(78), GOLD[5]), (cx + 13, U(78), GOLD[2]), (cx + 14, U(78), GOLD[2]), (cx + 12, U(79), GOLD[3]),
                      (cx + 13, U(79), GOLD[3]), (cx + 14, U(79), GOLD[2]), (cx + 15, U(79), GOLD[1])):
        r.fixed(x, y, c)
    # arms hang at the sides, green webbed hands
    for sx in (-1, 1):
        sh = (cx + sx * 19.5, U(73))
        wr = (cx + sx * 23.5, 117)
        el = ((sh[0] + wr[0]) / 2 - sx * 1.6, (sh[1] + wr[1]) / 2)               # the elbow hangs by the body
        g = 'arm%d' % sx
        r.tube(sh, el, 5.8, 5.0, M['coat'], group=g, folds=lambda u, sd: (-0.24 if u > 0.84 and abs(sd) < 0.5 else 0))
        r.tube(el, wr, 5.0, 4.5, M['coat'], group=g, folds=lambda u, sd: -0.2 if (0.55 < u < 0.6) and abs(sd) < 0.7 else 0)
        r.tube((wr[0], wr[1] - 3), wr, 4.9, 4.9, M['coat'], lift=0.14, group=g + 'cuff')
        seam(r, g, 0.34)
        # a long hand hanging relaxed, the back of it to the viewer, thumb turned in, webbing between the fingers
        hx_, hy_ = wr[0] + sx * 0.2, wr[1] + 0.5
        g = 'hand%d' % sx
        r.ellipsoid(hx_, hy_ + 3.6, 3.2, 4.2, M['squid'], group=g)
        flex = 1 if (f in (5, 6) and sx > 0) else 0
        for k in range(4):
            fx = hx_ - 2.1 + k * 1.4
            ln = 9.6 - abs(k - 1.4) * 1.1
            tip = (fx - sx * 0.7 + (flex * 1.0 if k > 1 else 0), hy_ + 5 + ln - flex * 1.4)
            r.tube((fx, hy_ + 5.5), tip, 1.0, 0.8, M['squid'], group=g + 'f%d' % k)
            seam(r, g + 'f%d' % k, 0.14)
            if k < 3:
                for j in range(2): r.fixed(fx + 0.7, hy_ + 7 + j, SQUID[3])         # the webbing, darker
        r.tube((hx_ - sx * 2.4, hy_ + 2.0), (hx_ - sx * 3.4, hy_ + 7.0), 1.25, 1.0, M['squid'], lift=0.06, group=g + 't')
        seam(r, g + 't', 0.18)
    # the head: a knobbed mantle, two round amber eyes with bar pupils, a beard of tentacles
    tilt = P.get('tilt', 0)
    hx, ey = cx + tilt, U(45)
    sway = P.get('sway', 0)
    # tentacles behind (the outer ones, they hang behind the inner ones)
    def tentacle(x0, y0, ln, curl, r0, g, phase):
        pts = curve(lambda t: (x0 + curl * 5 * t * t + sway * 2.2 * t * t + math.sin(t * 3 + phase) * 0.8,
                               y0 + ln * t - abs(curl) * 3 * t ** 3), 10)
        worm(r, pts, r0, 0.9, M['squid'], g)
        for i in range(3, len(pts) - 1, 2):                                       # suckers on the underside
            px_, py_ = pts[i]
            r.fixed(px_ - curl * 0.6, py_, SQUID[9] if i % 4 == 1 else SQUID[8])
        return pts[-1]
    for (dx, ln, curl, r0) in ((-11, 15, -1.2, 2.6), (11, 16, 1.2, 2.6), (-8, 21, -0.6, 2.9), (8, 22, 0.7, 2.9)):
        tentacle(hx + dx, ey + 9, ln, curl, r0, 'tb%d' % dx, dx)
    # the mantle: a heavy, wet, smooth sac with a few low ridges and warts; inside it a yellow light (the "aquarium"),
    # the embryos drifting in it seen as dark curled shapes against the glow, each with a bright yolk
    def mantle_v(x, y, u, w):
        v = 0.0
        if (x * 5 + y * 3) % 23 == 0 and w < 0.4: v -= 0.1                          # pores
        if abs(u + 0.35 - w * 0.2) < 0.05 and w < 0.2: v -= 0.12                    # two soft ridges down the dome
        if abs(u - 0.4 - w * 0.15) < 0.05 and w < 0.1: v -= 0.1
        return v
    r.ellipsoid(hx + 0.5, ey - 14, 14.5, 18.0, M['squid'], group='mantle', vfun=mantle_v)
    for i, (dx, dy, rx, ry) in enumerate(((-12.5, -12, 3.6, 6.5), (13, -12, 3.2, 6.2), (-7, -28, 5.5, 4.0), (6.5, -29, 5.0, 3.8))):
        r.ellipsoid(hx + dx, ey + dy, rx, ry, M['squid'], lift=0.0, group='mantle', vfun=mantle_v)
    for i in range(9):                                                              # warts round the crown
        a = -2.8 + i * 0.32
        wx, wy = hx + 0.5 + math.cos(a) * 14.2, ey - 14 + math.sin(a) * 17.2
        if h32(i, 3) % 3 == 0: continue
        r.ellipsoid(wx, wy, 1.4, 1.3, M['squid'], lift=0.12, group='mantle')
    yolk = P.get('yolk', 0)
    gx, gy, grx, gry = hx + 0.5, ey - 16, 10.5 + yolk, 11.0 + yolk
    for (x, y), e in list(r.buf.items()):
        if r.groups.get(e[2]) != 'mantle': continue
        d = ((x + 0.5 - gx) / grx) ** 2 + ((y + 0.5 - gy) / gry) ** 2
        if d >= 1: continue
        k = (1 - d) ** 1.3
        c = color_at(r, x, y)
        r.fixed(x, y, mix(c, YOLK[1 + yolk] if k < 0.5 else YOLK[2 + yolk], (0.42 + 0.12 * yolk) * k), e[2])
    drift = [(-4, -19), (3, -14), (5, -22), (-3, -12)]
    for i, (dx, dy) in enumerate(drift):
        ph = f * 0.8 + i * 1.9
        x = int(round(hx + dx + math.sin(ph) * 1.4))
        y = int(round(ey + dy + math.cos(ph * 0.7) * 1.0))
        fc = 1 if (yolk or (i + f) % 3) else -1                                     # in frame 5 they all turn one way
        body = [(0, 0), (-fc, 0), (-fc, 1), (-2 * fc, 1), (0, 1)]
        for (ox, oy) in body:
            if (x + ox, y + oy) in r.buf: r.fixed(x + ox, y + oy, mix(color_at(r, x + ox, y + oy), SQUID[1], 0.6))
        r.fixed(x + fc, y, YOLK[3] if yolk else YOLK[2])                             # the yolk-bright head
    for (x, y) in ((hx - 6, ey - 26), (hx - 5, ey - 27), (hx - 7, ey - 25)):        # a wet highlight on the crown
        if (x, y) in r.buf: r.fixed(x, y, mix(color_at(r, x, y), (230, 240, 190), 0.45))
    # the face below the mantle: the cheeks the tentacles hang from
    r.ellipsoid(hx, ey + 4, 13.0, 9.0, M['squid'], lift=-0.04, group='face')
    # eyes: dark sockets, round amber eyes, bar pupils, a wet glint
    for sx in (-1, 1):
        ex = hx + sx * 6.5
        r.ellipsoid(ex, ey + 0.5, 4.6, 4.2, M['squid'], lift=-0.5, group='socket%d' % sx)
    for sx in (-1, 1):
        ex = int(math.floor(hx + sx * 6.5))
        if P.get('blink'):
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    if dx * dx + dy * dy <= 6: r.fixed(ex + dx, ey + dy, SQUID[3] if dy < 1 else SQUID[2])
            for dx in range(-2, 3): r.fixed(ex + dx, ey + 1, SQUID[1])            # the lid's seam, low (lids slide up)
            continue
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                d2 = dx * dx + dy * dy
                if d2 > 6: continue
                c = EYEA[3] if dy < 0 else EYEA[2]
                if d2 >= 5: c = EYEA[1]
                r.fixed(ex + dx, ey + dy, c)
        look = tilt
        for dx in range(-1, 2): r.fixed(ex + dx + look, ey, (22, 14, 6))          # the bar pupil
        r.fixed(ex - 1, ey - 2, EYEA[4]); r.fixed(ex - 2, ey - 1, EYEA[4])
        r.fixed(ex + 2, ey + 1, EYEA[0])
    # the inner tentacles in front, the middle ones longest, hanging over the collar and waistcoat
    for (dx, ln, curl, r0) in ((-5, 25, -0.35, 3.2), (5, 26, 0.4, 3.2), (-1.5, 29, -0.1, 3.4), (2.5, 27, 0.2, 3.0)):
        tentacle(hx + dx, ey + 8, ln, curl, r0, 'tf%d' % dx, dx * 0.7)
    for k in range(-4, 5):                                                        # the dark mouth-shadow among the roots
        r.darken(hx + k, ey + 8, 0.25)
    im = r.render()
    return finish(im)


# ==================================================================================================== the Silence
SIL_POSE = [dict(), dict(rise=1), dict(rise=1, hand='two'), dict(hand='five'), dict(hand='none'), dict(hand='half'),
            dict(rise=-1, drip=1), dict(eyes=1)]


def silence(P, f):
    W, H = 128, 128
    r = Rig(W, H)
    rise = P.get('rise', 0)
    base = 123
    G = 'body'                                                                    # one group: the shag reads as one pelt
    sh = M['shag']
    # the bulk: a sodden cloak slumped down to the left, the hooded head up at the right, a sleeve-fold at its side
    r.ellipsoid(40, 104, 36, 21, sh, rot=-0.18, jag=0.12, group=G)
    r.ellipsoid(58, 84 - rise * 0.5, 30, 30, sh, rot=-0.5, jag=0.1, group=G)
    r.poly([(6, base), (14, 108), (30, 92), (96, 86), (110, 104), (116, base)], sh, group=G)
    r.ellipsoid(96, 78 - rise, 10, 16, sh, rot=0.25, jag=0.1, lift=0.02, group=G)      # the sleeve-fold the hand comes from
    hx, hy = 78, 44 - rise
    r.ellipsoid(hx - 4, hy - 1, 19, 20, sh, rot=-0.5, jag=0.08, lift=0.04, group=G)    # the hood, flowing into the back
    r.ellipsoid(hx - 14, hy + 14, 20, 16, sh, rot=-0.6, jag=0.08, group=G)
    r.ellipsoid(hx + 5, hy + 13, 13, 15, sh, rot=0.2, jag=0.06, group=G)               # the chest under the face
    r.ellipsoid(hx + 3, hy + 8, 11.5, 12.5, sh, lift=-1.2, group='void')               # the dark where a face should be
    # hanging strands: the whole pelt is wet locks hanging from where they grow, ridges catching the light from the top
    # left; the tops start inside the silhouette (found per column) so nothing pokes up like a candle
    ridges = []
    vx, vy, vrx, vry = hx + 3, hy + 9, 10.5, 11.5                                 # keep the face's dark open
    def strand(x0, y0, ln, wob, rr, lift=0.0, grp=G, veil=True):
        if veil and abs(x0 - vx) < vrx:
            top = vy - vry * math.sqrt(max(0.0, 1 - ((x0 - vx) / vrx) ** 2))
            if y0 < top + 6 and y0 + ln > top: ln = max(3.0, top + 2 - y0)
            elif top <= y0 < vy + vry * 0.8:
                y0 = vy + vry * 0.8 + (h32(int(x0 * 3), 5) % 3)                    # locks below the face start under it
                if ln < 8: return (x0, y0)
        pts = curve(lambda t: (x0 + math.sin(t * 2.2 + x0 * 0.7) * wob * t, y0 + ln * t), 5)
        worm(r, pts, rr, 0.7, sh, grp, lift=lift)
        ridges.append((x0, y0, ln, wob, rr))
        return pts[-1]
    def crevices():                                                                # after all locks: a dark crevice on
        for (x0, y0, ln, wob, rr) in ridges:                                       # each lock's shadow side, a lit ridge
            for k in range(int(ln * 2) + 1):                                       # on the other
                t = k / (ln * 2)
                x = x0 + math.sin(t * 2.2 + x0 * 0.7) * wob * t
                y = y0 + ln * t
                rad = rr + (0.7 - rr) * t
                r.darken(x + rad + 0.3, y, 0.3)
                if rr > 1.6: r.darken(x + rad - 0.7, y, 0.1)
                if t < 0.45 and rr > 1.6: r.darken(x - rad * 0.4, y, -0.08)
    tops = {}
    for x in range(W):
        ys = [y for y in range(H) if group_at(r, x, y) == G]
        if ys: tops[x] = min(ys)
    tips = []
    for layer in range(4):                                                         # matted locks over the cloak and hood,
        for i in range(17):                                                        # staggered, clumped, of mixed widths
            x0 = 8 + i * 6.4 + (layer % 2) * 3.2 + (h32(i, layer, 1) % 3) * 0.6
            t0 = tops.get(int(x0))
            if t0 is None: continue
            y0 = t0 + 1.0 + (h32(i, layer, 4) % 3) + layer * (7 + h32(i, layer, 12) % 10)
            if layer == 3: y0 = max(y0, 84 + h32(i, 13) % 12)
            ln = 14 + (h32(i, layer, 11) % 26)
            if y0 + ln > base + 1: ln = base + 1 - y0                              # the hem's locks trail on the floor
            if ln < 5: continue
            rr = 2.0 + (h32(i, layer, 6) % 4) * 0.45
            tips.append(strand(x0, y0, ln, 1.1, rr, lift=(h32(i, layer, 3) % 4) * 0.06 - 0.1 + layer * 0.02))
    for i in range(18):                                                            # the fringe over the face, longest
        x0 = 67 + i * 1.4 + (h32(i, 2) % 2) * 0.5                                  # at the sides, parted in the middle
        y0 = hy - 6 + abs(x0 - 81) * 0.3
        side = min(1.0, abs(x0 - 81) / 11)
        ln = 5 + (h32(i, 7) % 5) + 13 * side
        tips.append(strand(x0, y0, ln, 0.5, 1.15 + (h32(i, 3) % 2) * 0.4, lift=0.06 + (h32(i, 5) % 3) * 0.05, veil=False))
    crevices()
    for k in range(16):                                                            # the hood's brim over the dark: a
        a = -2.7 + k * 0.17                                                        # heavier, lighter roll of wet shag
        r.darken(vx + math.cos(a) * (vrx + 0.5), vy + math.sin(a) * (vry + 0.5), -0.16)
    for (x, y), e in list(r.buf.items()):                                          # wet glints where the light lands
        if e[0] is not sh or r.groups.get(e[2]) != G: continue
        if h32(x, y, 77) % 41 == 0 and e[1] > 0.45: r.fixed(x, y, SHAG[11] if h32(x, y, 3) % 2 else SHAG[10], e[2])
    # the narrow signing hand, out of the sleeve-fold
    hand = P.get('hand')
    sleeve = (99, 70 - rise)
    if hand:
        up = {'two': 1.0, 'five': 1.0, 'none': 0.85, 'half': 0.45}[hand]
        wr = (sleeve[0] + 5 * up, sleeve[1] - 19 * up)
        r.tube(sleeve, wr, 2.4, 1.8, M['shand'], lift=-0.12, group='forearm')
        r.ellipsoid(wr[0], wr[1] - 2.0, 2.8, 3.2, M['shand'], group='palm')
        if hand == 'two':
            hand_fingers(r, (wr[0] - 0.2, wr[1] - 3.6), -math.pi / 2 - 0.06, [7.2, 7.8], 0.2, 0.9, M['shand'], 'fing')
            hand_fingers(r, (wr[0] + 1.4, wr[1] - 2.4), 0.3, [2.6, 2.4], 0.5, 0.85, M['shand'], 'fold', curl=2.0)
        elif hand == 'five':
            hand_fingers(r, (wr[0], wr[1] - 3.6), -math.pi / 2 + 0.06, [5.6, 7.4, 8.0, 7.2, 5.4], 0.26, 0.85, M['shand'], 'fing')
        elif hand == 'none':
            r.ellipsoid(wr[0], wr[1] - 4.4, 2.6, 2.3, M['shand'], lift=0.08, group='fist')
            for k in range(3): r.fixed(wr[0] - 1 + k, wr[1] - 5, SHAND[5 if k == 0 else 4])
        else:
            hand_fingers(r, (wr[0], wr[1] - 3.2), -math.pi / 2 + 0.35, [3.8, 4.2, 3.6], 0.24, 0.8, M['shand'], 'fing', curl=0.9)
        for i in range(4):                                                         # the sleeve's strands over the wrist
            strand(sleeve[0] - 3 + i * 2, sleeve[1] - 4 - i % 2, 7 + i % 3, 0.4, 1.0, lift=0.1, grp='cuff')
    # the heavy paw on the floor at the front, claws curled on the boards
    pw = (80, 113)
    r.tube((72, 94), pw, 6.4, 5.6, sh, lift=0.04, group='paw')
    r.ellipsoid(pw[0] + 3, pw[1] + 3.5, 9.5, 5.6, sh, lift=0.1, group='paw')
    for k in range(4):
        kx = pw[0] - 3 + k * 4.4
        r.tube((kx, pw[1] + 5), (kx + 1.0, base - 1.5), 2.2, 1.7, sh, lift=0.16, group='knuckle%d' % k)
        r.tube((kx + 1.0, base - 2), (kx + 3.4, base + 0.5), 1.2, 0.7, M['claw'], group='claw%d' % k)
        seam(r, 'knuckle%d' % k, 0.2)
    for i in range(8):                                                             # strands hanging over the paw's wrist
        strand(68 + i * 2.1, 90 + (i % 2) * 2, 13 + (i * 5) % 7, 0.5, 1.2, lift=0.02, grp='paw', veil=False)
    # drips: beads at some strand ends that catch the hall's light
    for i, (tx, ty) in enumerate(tips):
        if h32(i, 4) % 4 or ty > base - 5: continue
        n = 1 + h32(i, 8) % 2
        for k in range(n): r.fixed(tx, ty + 1 + k, SHAG[2])
        r.fixed(tx, ty + 1 + n, SHAG[9]); r.fixed(tx, ty + 2 + n, SHAG[4])
    if P.get('drip'):
        r.fixed(86, hy + 20, SHAG[2]); r.fixed(86, hy + 21, SHAG[10]); r.fixed(86, hy + 22, SHAG[5])   # a drip leaves the fringe
        r.fixed(70, 108, SHAG[10]); r.fixed(70, 109, SHAG[6])
    if P.get('eyes'):                                                              # two dim points in the dark, once
        for (x, y) in ((79, hy + 8), (86, hy + 7)):
            r.fixed(x, y, (126, 100, 56)); r.fixed(x + 1, y, (70, 54, 32))
    im = r.render()
    # the wet patch on the floor under it (semi-transparent, behind everything)
    px = im.load()
    for y in range(base - 4, H):
        for x in range(2, 126):
            d = ((x + 0.5 - 62) / 62) ** 2 + ((y + 0.5 - (base + 1)) / 3.6) ** 2
            if d > 1 or px[x, y][3]: continue
            c = SHAG[1] if (x * 7 + y * 3) % 23 else SHAG[7]
            px[x, y] = c + (int(170 * (1 - d) ** 0.5),)
    return finish(im)


# ================================================================================================== Sister Calyx
CALYX_POSE = [dict(b=0), dict(b=1), dict(b=0, bright=1), dict(b=0, narrow=1), dict(b=0, sway=-2, drip=1),
              dict(b=0, sway=1, drip=2), dict(b=0, tilt=-1), dict(b=1, settle=1)]


def glow_px(r, x, y, k):
    """one lit pixel of a glow source, k = 0..5 on the GLOW ramp"""
    r.fixed(x, y, GLOW[max(0, min(5, k))])


def calyx(P, f):
    W, H = 128, 176
    r = Rig(W, H)
    cx, base = 58, 171
    b = P.get('b', 0)
    st = P.get('settle', 0)                                      # exhale: the head settles a beat before the shoulders
    U = lambda y: y - b if (y < 100 and not (st and y < 58)) else y
    tilt = P.get('tilt', 0)
    bright = P.get('bright', 0)
    halos = []
    # thorny growths behind her: curved thorns out of the shoulders and the back of the hood, verdigris knots on them
    def hook(p0, ang, ln, curl, r0, g):
        pts, x, y, a = [], p0[0], p0[1], ang
        for _ in range(10):
            pts.append((x, y)); x += math.cos(a) * ln / 9; y += math.sin(a) * ln / 9; a += curl / 9
        worm(r, pts, r0, 0.5, M['bark'], g)
        return pts
    for (p0, ang, ln, curl, r0) in (((cx - 17, U(62)), -2.3, 20, 1.4, 2.6), ((cx - 22, U(70)), -2.9, 13, 1.2, 1.9),
                                    ((cx - 7, U(32)), -2.2, 13, 1.3, 2.0), ((cx + 15, U(60)), -0.9, 12, -1.3, 2.0)):
        pts = hook(p0, ang, ln, curl, r0, 'thorn')
        k = pts[2]
        r.ellipsoid(k[0], k[1], 2.0, 1.7, M['tealgrow'], lift=0.08, group='tknot')
    # roots spreading from the hem on the floor
    for (x0, x1, y1) in ((cx - 36, cx - 50, base + 1), (cx - 24, cx - 34, base + 2), (cx + 30, cx + 46, base + 1), (cx + 20, cx + 28, base + 2)):
        pts = curve(lambda t: (x0 + (x1 - x0) * t, base - 4 + (y1 - base + 4) * t - 2 * math.sin(t * math.pi)), 6)
        worm(r, pts, 2.0, 0.6, M['bark'], 'root')
    # the robe: a dark back layer, the ragged rag-and-moss underlayer in the opening, two front panels, all tattered
    FOLDS = [(-30, 0.42), (-22, 0.30), (-15, 0.16), (-10, 0.05), (11, -0.04), (17, -0.14), (24, -0.27), (31, -0.38)]
    def robe_v(x, y):
        v = 0.0
        t = max(0.0, (y - 70) / 100.0)
        for (fx, spread) in FOLDS:                                                  # long folds fanning out to the hem
            px = cx + fx * 0.55 + fx * 0.45 * t - spread * 6 * t + math.sin(y * 0.11 + fx) * 0.6
            d = x + 0.5 - px
            if -0.5 <= d < 0.5: v -= 0.26
            elif 0.5 <= d < 1.5: v += 0.08
            elif -2.5 <= d < -0.5: v -= 0.06
        if y > base - 10: v -= 0.08
        return v
    def tatters(x0, x1, n, s0, deep=9):
        pts = []
        for k in range(n + 1):
            x = x0 + (x1 - x0) * k / n
            y = base + 1 - (h32(k, s0) % 3) if k % 2 == 0 else base - 4 - h32(k, s0, 7) % deep
            pts.append((x + (h32(k, s0, 3) % 3 - 1) * 0.8, y))
        return pts
    back = [(cx - 20, U(62)), (cx + 20, U(62)), (cx + 31, 112), (cx + 41, base - 6)] + tatters(cx + 41, cx - 43, 18, 1) + [(cx - 31, 112)]
    r.poly(back, M['violet'], lift=-0.22, group='robeback', vfun=robe_v)
    under = [(cx - 8, U(76)), (cx + 8, U(76)), (cx + 14, base - 6)] + tatters(cx + 14, cx - 14, 8, 3, 6) + [(cx - 14, base - 6)]
    r.poly(under, M['rag'], lift=-0.42, group='under', vfun=lambda x, y: (-0.2 if (x + (y // 4)) % 5 == 0 else 0) + (-0.1 if y > 150 else 0))
    for k in range(5):                                                              # rag strips hanging in the opening
        x0 = cx - 7 + k * 3.0
        y0 = U(98) + (k * 7) % 12
        r.poly([(x0, y0), (x0 + 2.4, y0), (x0 + 2.0 + (k % 2), 146 + h32(k, 2) % 16), (x0 + 0.8, 149 + h32(k, 5) % 14)],
               M['moss'] if k % 2 else M['rag'], lift=-0.1 + 0.05 * (k % 3), group='under')
    for sx in (-1, 1):
        if sx < 0:
            pts = [(cx - 22, U(62)), (cx - 4, U(66)), (cx - 3, U(84)), (cx - 6, 104), (cx - 4, 122), (cx - 8, 140), (cx - 6, 154),
                   (cx - 10, base - 6)] + tatters(cx - 10, cx - 45, 11, 4) + [(cx - 33, 108)]
        else:
            pts = [(cx + 22, U(62)), (cx + 4, U(66)), (cx + 4, U(86)), (cx + 7, 106), (cx + 5, 126), (cx + 9, 144), (cx + 7, 156),
                   (cx + 10, base - 6)] + tatters(cx + 10, cx + 41, 10, 6) + [(cx + 31, 108)]
        r.poly(pts, M['violet'], round_=0.8, group='panel%d' % sx, vfun=robe_v)
        seam(r, 'panel%d' % sx, 0.22)
    # the moss creeps up the cloth from the hem and down from the shoulders: a material change, not a sticker
    for (x, y), e in r.buf.items():
        if e[0] is not M['violet'] or r.groups.get(e[2]) not in ('panel-1', 'panel1', 'robeback'): continue
        m = rig.nL(x * 1.5 + 7, y * 1.5) * 0.7 + rig.nM(x * 2.2, y * 2.2) * 0.3
        bias = max(0.0, (y - 120) / 50.0) * 0.32 + (0.2 if y < 74 else 0)
        if m + bias > 0.78: e[0] = M['moss']; e[1] -= 0.06
        elif m + bias > 0.74: e[1] -= 0.12                                          # damp at the moss' edge
    for i, (x, y) in enumerate(((cx - 22, 140), (cx + 18, 128), (cx - 12, 162), (cx + 27, 156))):
        for j, (dx, dy) in enumerate(((0, 0), (1.6, -1.2), (-1.4, -1.4), (0.4, -2.6))[:3 + i % 2]):   # verdigris knots
            r.ellipsoid(x + dx, y + dy, 1.3 + (h32(j, i) % 2) * 0.4, 1.2, M['tealgrow'], lift=0.0 + 0.05 * j, group='knot%d' % i)
    # the bead belt, a rosary with a pale pendant, the ink vial
    belt = curve(lambda t: (cx - 15 + 30 * t, U(94) + 3 * math.sin(t * math.pi)), 30)
    for i, (x, y) in enumerate(belt):
        c = RAG[5] if i % 2 else RAG[2]
        if i in (7, 16, 25): c = GLOW[3 + bright]
        r.fixed(x, y, c); r.fixed(x, y + 1, RAG[1] if c != GLOW[3 + bright] else GLOW[2])
    ros = curve(lambda t: (cx + 1 + 1.5 * math.sin(t * 2.5), U(97) + 20 * t), 20)
    for i, (x, y) in enumerate(ros):
        r.fixed(x, y, RAG[5] if i % 3 == 0 else RAG[3])
    px_, py_ = ros[-1]
    for (dx, dy) in ((0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (-1, 2), (1, 2)):
        r.fixed(px_ + dx, py_ + dy, BONE[6] if dy < 3 else BONE[4])
    r.fixed(px_ + 1, py_ + 3, BONE[2])
    vx = cx + 11
    for k in range(6): r.fixed(vx, U(97) + k, (34, 36, 60) if k > 1 else RAG[4]); r.fixed(vx + 1, U(97) + k, (18, 18, 34) if k > 1 else RAG[2])
    r.fixed(vx, U(99), (120, 130, 170))
    # the right arm (viewer's left): the moss-caged lantern held out low
    shL = (cx - 19, U(68))
    hand = (cx - 35, U(94))
    el = ik(shL, hand, 17, 16, 'down')
    r.tube(shL, el, 6.4, 5.8, M['violet'], group='armL', folds=lambda u, sd: -0.2 if u > 0.85 and sd > 0 else 0)
    r.tube(el, hand, 5.8, 5.0, M['violet'], group='armL')
    cuff = lerp(el, hand, 0.55)                                                     # the wide sleeve hangs in rags
    drape = [(el[0] + 3, el[1] - 2), (hand[0] + 3, hand[1] - 3), (hand[0] + 2, hand[1] + 6), (hand[0] + 5, hand[1] + 12),
             (cuff[0] + 1, cuff[1] + 16), (cuff[0] + 4, cuff[1] + 11), (el[0] + 4, el[1] + 12), (el[0] + 6, el[1] + 4)]
    r.poly(drape, M['violet'], lift=0.02, group='sleeveL', vfun=lambda x, y: -0.2 if (x * 3 + y) % 7 == 0 else 0)
    seam(r, 'armL', 0.28); seam(r, 'sleeveL', 0.2)
    lx, ly = hand[0], hand[1] + 14
    glow = 3 + bright
    r.tube((hand[0], hand[1] + 2), (lx, ly - 7), 0.8, 0.8, M['bark'], group='lhandle')
    r.ellipsoid(lx, ly - 6, 6.0, 2.8, M['moss'], lift=0.1, jag=0.3, group='ltop')               # moss on the cap
    core = []
    for y in range(int(ly - 5), int(ly + 7)):
        for x in range(int(lx - 6), int(lx + 7)):
            d = ((x + 0.5 - lx) / 5.6) ** 2 + ((y + 0.5 - ly - 0.5) / 6.2) ** 2
            if d > 1: continue
            core.append((x, y, d))
    oid = r.new('lcore')
    for (x, y, d) in core:
        k = glow + 1 if d < 0.25 else (glow if d < 0.6 else glow - 1)
        r.fixed(x, y, GLOW[max(0, min(5, k))], oid)
    for k in range(5):                                                             # the cage: bark ribs over the glow
        t = -0.8 + k * 0.4
        for y in range(int(ly - 6), int(ly + 7)):
            yy = (y + 0.5 - ly - 0.5) / 6.2
            if abs(yy) > 1: continue
            x = lx + t * 5.6 * math.sqrt(max(0.0, 1 - yy * yy))
            r.fixed(x, y, BARK[3] if t < 0 else BARK[2])
    for x in range(int(lx - 5), int(lx + 6)): r.fixed(x, ly + 6, BARK[2]); r.fixed(x, ly - 5, BARK[3])
    for (dx, n) in ((-3, 4 + (f % 3)), (0, 6 - (f % 2)), (3, 3 + ((f + 1) % 3))):         # glowing drips
        for k in range(n): r.fixed(lx + dx, ly + 7 + k, GLOW[2] if k < n - 1 else GLOW[3])
    r.ellipsoid(hand[0] + 1.0, hand[1] - 1.0, 3.0, 2.6, M['teal'], group='palmL')               # the back of the hand
    for k in range(3):                                                              # fingers hooked through the ring
        y = hand[1] + 0.6 + k * 1.5
        r.tube((hand[0] + 2.4, y - 1.2), (hand[0] - 2.4, y), 0.95, 0.85, M['teal'], group='gripL%d' % k)
        r.tube((hand[0] - 2.4, y), (hand[0] - 1.6, y + 1.6), 0.85, 0.75, M['teal'], group='gripL%d' % k)
        seam(r, 'gripL%d' % k, 0.16)
        r.fixed(hand[0] - 1, y + 2, (20, 18, 26))                                   # ink-black nails
    r.tube((hand[0] + 2.2, hand[1] - 2.2), (hand[0] - 0.4, hand[1] - 2.8), 1.1, 0.9, M['teal'], lift=0.08, group='gripLt')
    halos.append((lx + 0.5, ly + 0.5, 13 + 2 * bright, GLOW[3], 0.5 + 0.25 * bright))
    # the head: a deep hood (peak bent back), the dark inside, two green eyes, mossy filaments hanging from the dark
    hx, hy = cx + 1 + tilt, U(46)                                                  # she stoops: the head low between
    r.ellipsoid(cx - 1, U(60), 23, 9.5, M['violet'], lift=0.04, group='cowl')       # rounded, raised shoulders
    r.ellipsoid(hx, hy, 15.5, 18.5, M['violet'], lift=0.06, group='hood',
                vfun=lambda x, y, u, w: (-0.18 if abs(math.atan2(w, u) * 3 % 1 - 0.5) < 0.06 and w < 0.2 else 0))
    r.poly([(hx - 12, hy - 8), (hx - 7, hy - 20), (hx - 5, hy - 27), (hx + 2, hy - 21), (hx + 10, hy - 12)], M['violet'], lift=0.1, group='hood')
    for (x, y), e in r.buf.items():                                                # the hood and cowl gone mossy in places
        if r.groups.get(e[2]) not in ('hood', 'cowl') or e[0] is not M['violet']: continue
        m = rig.nL(x * 1.7 + 3, y * 1.7 + 9) * 0.7 + rig.nM(x * 2.4, y * 2.4) * 0.3
        if m > 0.7: e[0] = M['moss']; e[1] -= 0.08
    r.ellipsoid(hx + 0.5, hy + 3, 10.5, 13, M['violet'], lift=-1.0, group='void')
    for i in range(7):                                                             # filaments hanging from the dark
        x0 = hx - 6 + i * 2.1 + (h32(i, 22) % 3 - 1) * 0.7
        ln = 4 + (h32(i, 21) % 9)
        y0 = hy + 6 + h32(i, 23) % 3
        for k in range(ln):
            x = x0 + math.sin(k * 0.45 + i * 1.3) * 0.9
            r.fixed(x, y0 + k, MOSS[1 + (k % 4 == 1) + (i % 3 == 0)] if k < ln - 1 else MOSS[5])
    ey = hy - 1
    for sx in (-1, 1):
        ex = int(hx + sx * 4 - (1 if sx < 0 else 0))
        if P.get('narrow'):
            for dx in (-1, 0, 1): glow_px(r, ex + dx, ey + 1, 3)
            glow_px(r, ex, ey + 1, 5)
        else:
            for (dx, dy, k) in ((0, 0, 5), (1, 0, 4), (0, 1, 4), (1, 1, 3), (-1, 0, 2), (2, 1, 2), (0, -1, 2), (1, 2, 2)):
                glow_px(r, ex + dx, ey + dy, k)
        halos.append((ex + 1, ey + 1, 5, GLOW[2], 0.3))
    for k in range(16):                                                            # the hood's rim, catching light
        a = -2.8 + k * 0.19
        r.fixed(hx + 0.5 + math.cos(a) * 10.4, hy + 3 + math.sin(a) * 13, VIOLET[7 if k < 8 else 5])
    # the left arm (viewer's right): the gnarled staff with its thorn crown and the dripping lamp-pod
    sx_ = cx + 35
    staff = curve(lambda t: (sx_ + math.sin(t * 9) * 0.9, 16 + (base - 16) * t), 30)
    worm(r, staff, 2.3, 2.0, M['bark'], 'staff')
    for (x0, y0, x1, y1) in ((sx_, 18, sx_ - 7, 6), (sx_, 17, sx_ + 6, 4), (sx_ + 1, 19, sx_ + 9, 12), (sx_ - 1, 20, sx_ - 8, 15)):
        pts = curve(lambda t: (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t - 2 * math.sin(t * math.pi)), 6)
        worm(r, pts, 1.8, 0.5, M['bark'], 'crown')
    for j in range(4): r.ellipsoid(sx_ - 3 + j * 2.4, 15 + (j % 2) * 2, 1.7, 1.5, M['tealgrow'], lift=0.15, group='crownk')
    sway = P.get('sway', 0)
    vine = curve(lambda t: (sx_ + 4 + (6 + sway) * t, 16 + 18 * t + 2 * math.sin(t * 3)), 8)
    worm(r, vine, 1.0, 0.8, M['moss'], 'vine')
    px0, py0 = vine[-1]
    r.ellipsoid(px0, py0 + 6, 6.4, 7.2, M['moss'], jag=0.3, group='pod')
    for y in range(int(py0 + 1), int(py0 + 12)):                                   # the glow through the split husk
        for x in range(int(px0 - 4), int(px0 + 5)):
            d = ((x + 0.5 - px0) / 4.2) ** 2 + ((y + 0.5 - py0 - 6.5) / 4.6) ** 2
            if d < 1 and (d < 0.45 or (x * 3 + y * 5) % 4): glow_px(r, x, y, (5 if d < 0.15 else 4 if d < 0.5 else 3) - (0 if bright else (d > 0.5)))
    for k in range(5): r.fixed(px0 - 4 + k * 2, py0 + 2 + (k % 2) * 8, MOSS[3])          # husk strands over it
    halos.append((px0 + 0.5, py0 + 6.5, 12 + bright, GLOW[3], 0.55 + 0.2 * bright))
    drip = P.get('drip', 0)
    for (dx, n) in ((-1, 3), (2, 2)):
        for k in range(n): r.fixed(px0 + dx, py0 + 13 + k, GLOW[2] if k < n - 1 else GLOW[3])
    if drip == 1: r.fixed(px0, py0 + 14, GLOW[2]); r.fixed(px0, py0 + 15, GLOW[4])
    if drip == 2: r.fixed(px0 - 1, py0 + 21, GLOW[4]); r.fixed(px0 - 1, py0 + 20, GLOW[2])
    shR = (cx + 19, U(68))
    handR = (sx_ - 0.5, U(84))
    elR = ik(shR, handR, 13, 12, 'down')
    r.tube(shR, elR, 6.2, 5.6, M['violet'], group='armR', folds=lambda u, sd: -0.2 if u > 0.85 and sd < 0 else 0)
    r.tube(elR, (handR[0] - 2, handR[1] + 1), 5.6, 5.0, M['violet'], group='armR')
    dr = [(elR[0] - 2, elR[1] + 2), (handR[0] - 3, handR[1] + 2), (handR[0] - 2, handR[1] + 12), (elR[0] + 3, elR[1] + 14), (elR[0] - 1, elR[1] + 10)]
    r.poly(dr, M['violet'], lift=-0.04, group='sleeveR', vfun=lambda x, y: -0.2 if (x * 3 - y) % 7 == 0 else 0)
    seam(r, 'armR', 0.28); seam(r, 'sleeveR', 0.2)
    r.ellipsoid(handR[0], handR[1], 3.4, 3.0, M['teal'], group='palmR')                     # the hand round the staff
    for k in range(3):
        y = handR[1] - 1.5 + k * 1.6
        r.tube((handR[0] - 2.4, y), (handR[0] + 2.8, y + 0.4), 0.95, 0.9, M['teal'], group='gripR%d' % k)
        seam(r, 'gripR%d' % k, 0.16)
        r.fixed(handR[0] + 3, y + 0.4, (20, 18, 26))
    im = r.render()
    return finish(im, halos)


# =============================================================================================== Heartbroker Lune
LUNE_POSE = [dict(b=0), dict(b=1), dict(b=0, beat='all'), dict(b=0, beat='odd'), dict(b=0, gutter=1, curl=1),
             dict(b=1, beat='all', curl=1), dict(b=0, tilt=1), dict(b=1, settle=1)]
M['heart'] = Mat(HEART, 'skin', 0.28, 0.6)
M['heartp'] = Mat(HEARTP, 'skin', 0.3, 0.5)
M['heartb'] = Mat(HEARTB, 'skin', 0.28, 0.6)
M['heartg'] = Mat(HEARTG, 'skin', 0.28, 0.6)


def heart_in_globe(r, gx, gy, rad, mat, beat, g, neck=False, cap=True):
    """a blown-glass globe (dark glass, reflections, a brass cap) with a beating heart inside"""
    oid = r.new(g + 'glass')
    for y in range(int(gy - rad) - 1, int(gy + rad) + 2):                           # the glass: dark, tinted by the heart
        for x in range(int(gx - rad) - 1, int(gx + rad) + 2):
            d = math.hypot(x + 0.5 - gx, y + 0.5 - gy) / rad
            if d > 1: continue
            c = mix((30, 22, 30), (54, 40, 48), max(0.0, 1 - d) * 0.6)
            r.put(x, y, None, 0, oid, c)
    k = 1.0 + (0.14 if beat else 0)
    hr = rad * 0.62 * k
    for sx in (-1, 1):
        r.ellipsoid(gx + sx * hr * 0.42, gy - hr * 0.18, hr * 0.52, hr * 0.5, mat, group=g + 'heart')
    r.poly([(gx - hr * 0.9, gy - hr * 0.05), (gx + hr * 0.9, gy - hr * 0.05), (gx + hr * 0.15, gy + hr * 0.8), (gx, gy + hr * 0.95),
            (gx - hr * 0.15, gy + hr * 0.8)], mat, group=g + 'heart', round_=0.9)
    r.tube((gx + hr * 0.2, gy - hr * 0.7), (gx + hr * 0.35, gy - hr * 1.1), hr * 0.16 + 0.4, hr * 0.12 + 0.3, mat, lift=-0.1, group=g + 'heart')   # a vessel stub
    for a in range(int(rad * 7)):                                                    # rim and reflections
        t = a / int(rad * 7) * 2 * math.pi
        x, y = gx + math.cos(t) * (rad - 0.4), gy + math.sin(t) * (rad - 0.4)
        c = GLASS[1]
        if -2.6 < t - math.pi < -1.4 or (math.pi * 0.9 < t < math.pi * 1.35): c = GLASS[2]
        if 0.3 < t < 1.2: c = GLASS[2]
        r.fixed(x, y, c)
    r.fixed(gx - rad * 0.45, gy - rad * 0.5, GLASS[4]); r.fixed(gx - rad * 0.45 + 1, gy - rad * 0.5, GLASS[3])
    r.fixed(gx - rad * 0.55, gy - rad * 0.3, GLASS[3])
    r.fixed(gx + rad * 0.5, gy + rad * 0.45, GLASS[2])
    if cap:
        r.ellipsoid(gx, gy - rad - 0.4, max(2.2, rad * 0.42), 1.4, M['gold'], group=g + 'cap')
        if neck: r.tube((gx, gy - rad - 1), (gx, gy - rad - 4), 2.0, 2.0, M['gold'], lift=0.05, group=g + 'cap')
        r.fixed(gx, gy + rad + 0.6, GOLD[4]); r.fixed(gx, gy + rad + 1.6, GOLD[2])        # the finial


def chain(r, a, b, sag=2.0, step=1.0):
    n = max(2, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
    for i in range(n + 1):
        t = i / n
        x = a[0] + (b[0] - a[0]) * t
        y = a[1] + (b[1] - a[1]) * t + sag * math.sin(t * math.pi)
        r.fixed(x, y, GOLD[5] if i % 2 else GOLD[2])


def lune(P, f):
    W, H = 128, 192
    r = Rig(W, H)
    cx, base = 66, 188
    b = P.get('b', 0)
    st = P.get('settle', 0)                                      # exhale: the head settles a beat before the shoulders
    U = lambda y: y - b if (y < 100 and not (st and y < 62)) else y
    beat = P.get('beat')
    halos = []
    # the brass harness arms rising from behind the shoulders and arching out, the globes hanging from their ends
    def rod(pts, g):
        worm(r, pts, 1.2, 1.0, M['gold'], g)
    def crook(sx):                                                                  # up from behind the shoulder, then a
        pts = []                                                                    # shepherd's-crook arc outward and down
        for i in range(13):
            t = i / 12
            pts.append((cx + sx * (12 + 9 * t), U(74) - 58 * t))
        ox, oy = pts[-1]
        for i in range(1, 11):
            a = math.pi * i / 10
            pts.append((ox + sx * 7 * (1 - math.cos(a)), oy - 6 * math.sin(a)))
        return pts
    rodL, rodR = crook(-1), crook(1)
    rod(rodL, 'rodL'); rod(rodR, 'rodR')
    endL, endR = rodL[-1], rodR[-1]
    # feet: grey-green talons under the hem
    for sx in (-1, 1):
        fx = cx + sx * 7
        for k in (-1, 0, 1):
            tip = (fx + k * 4.2 + sx * 0.5, base - 0.5)
            r.tube((fx, base - 5), tip, 2.0, 1.2, M['glove'], group='foot%d' % sx)
            r.fixed(tip[0] + k, tip[1] + 0.5, BONE[2]); r.fixed(tip[0] + k * 1.5, tip[1] - 0.3, BONE[3])
    # the robes: the outer plum back layer, the maroon inner robe, the parchment tabard, the two front panels
    def tatters(x0, x1, n, s0, deep=10):
        pts = []
        for k in range(n + 1):
            x = x0 + (x1 - x0) * k / n
            y = base - 2 - (h32(k, s0) % 3) if k % 2 == 0 else base - 7 - h32(k, s0, 7) % deep
            pts.append((x, y))
        return pts
    FOLDS = [(-28, 0.4), (-19, 0.25), (-12, 0.1), (12, -0.1), (19, -0.25), (27, -0.4)]
    def robe_v(x, y):
        v = (rig.nL(x * 0.9 + 17, y * 0.9) - 0.5) * 0.22                             # worn, sun-faded patches
        if y > base - 26: v -= (y - (base - 26)) * 0.008                             # the hem drags through the market
        for (sx_, sy, sr) in ((-22, 150, 3.0), (18, 132, 2.4), (-9, 172, 2.6), (25, 166, 2.2)):
            if (x + 0.5 - (cx + sx_)) ** 2 + ((y - sy) * 1.4) ** 2 < sr * sr: v -= 0.16   # old stains
        t = max(0.0, (y - 76) / 110.0)
        for (fx, sp) in FOLDS:
            px = cx + fx * 0.5 + fx * 0.6 * t - sp * 5 * t + math.sin(y * 0.1 + fx) * 0.6
            d = x + 0.5 - px
            if -0.5 <= d < 0.5: v -= 0.26
            elif 0.5 <= d < 1.5: v += 0.08
        return v
    back = [(cx - 17, U(72)), (cx + 17, U(72)), (cx + 27, 128), (cx + 36, base - 6)] + tatters(cx + 36, cx - 38, 16, 2) + [(cx - 28, 128)]
    r.poly(back, M['plum'], lift=-0.25, group='back', vfun=robe_v)
    inner = [(cx - 9, U(84)), (cx + 9, U(84)), (cx + 16, base - 6)] + tatters(cx + 16, cx - 16, 8, 5, 14) + [(cx - 16, base - 6)]
    r.poly(inner, M['maroon'], group='inner', vfun=lambda x, y: (-0.22 if (x - cx + y // 9) % 6 == 0 else 0) + (-0.1 if y > 170 else 0))
    tab = [(cx - 5, 100), (cx + 4, 100), (cx + 5, 146), (cx + 3, 143), (cx + 1, 149), (cx - 2, 144), (cx - 4, 148), (cx - 6, 142)]
    r.poly(tab, M['parch'], lift=-0.22, round_=0.5, group='tabard', vfun=lambda x, y: -0.12 if (x * 7 + y * 3) % 13 == 0 else 0)
    for (x, y) in ((cx - 3, 116), (cx - 2, 116), (cx, 117), (cx + 2, 116), (cx - 3, 121), (cx - 1, 121), (cx + 1, 121), (cx + 3, 122),
                   (cx - 2, 126), (cx, 126), (cx + 2, 127), (cx - 3, 131), (cx + 1, 131), (cx + 2, 132)):
        r.fixed(x, y, PARCH[1])                                                       # faded marks (no legible text)
    for (dx, dy) in ((-1, 0), (1, 0), (-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1), (-1, 2), (0, 2), (1, 2), (0, 3)):
        r.fixed(cx + dx, 106 + dy, HEART[4] if dy < 2 else HEART[3])                 # the heart sigil
    for sx in (-1, 1):
        if sx < 0:
            pts = [(cx - 17, U(72)), (cx - 6, U(80)), (cx - 7, 120), (cx - 12, 160), (cx - 13, base - 6)] + tatters(cx - 13, cx - 40, 8, 7) + [(cx - 29, 126)]
        else:
            pts = [(cx + 17, U(72)), (cx + 6, U(80)), (cx + 7, 120), (cx + 11, 160), (cx + 12, base - 6)] + tatters(cx + 12, cx + 38, 8, 9) + [(cx + 28, 126)]
        r.poly(pts, M['plum'], round_=0.8, group='panel%d' % sx, vfun=robe_v)
        seam(r, 'panel%d' % sx, 0.24)
        # gold trim down the panel's inner edge
        edge = [(cx + sx * 6, U(80)), (cx + sx * 7, 120), (cx + sx * (12 if sx > 0 else 12), 160), (cx + sx * 12.5, base - 7)]
        for (p0, p1) in zip(edge, edge[1:]):
            n = int(abs(p1[1] - p0[1]))
            for i in range(n):
                t = i / n
                x, y = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
                r.fixed(x - sx * 0.5, y, GOLD[5] if int(y) % 3 else GOLD[3])
                if int(y) % 7 == 0: r.fixed(x - sx * 1.5, y, GOLD[6])
    # the belt, the cluster of hip globes on chains
    for x in range(cx - 15, cx + 16):
        r.fixed(x, 97, GOLD[5]); r.fixed(x, 98, GOLD[3] if x % 3 else GOLD[4]); r.fixed(x, 99, GOLD[1])
    for (dx, dy, c) in ((-1, -1, GOLD[6]), (0, -1, GOLD[6]), (1, -1, GOLD[5]), (-2, 0, GOLD[5]), (2, 0, GOLD[2]), (-1, 2, GOLD[2]), (1, 2, GOLD[1])):
        r.fixed(cx + dx, 98 + dy, c)
    hips = [(-21, 114, 6.0, 'heart', 0), (-10, 123, 6.4, 'heartp', 1), (11, 119, 6.0, 'heart', 2), (22, 111, 5.0, 'heartb', 3), (15, 132, 4.0, 'heartg', 4)]
    for (dx, y, rad, mat, i) in hips:
        top = (cx + dx * 0.55, 99)
        chain(r, top, (cx + dx, y - rad - 1.5), sag=0.5)
        bt = beat == 'all' or (beat == 'odd' and i == 3)
        heart_in_globe(r, cx + dx, y, rad, M[mat], bt, 'hip%d' % i)
    # the capelet over the shoulders, scalloped, gold-trimmed
    cap = [(cx - 10, U(64)), (cx + 10, U(64)), (cx + 19, U(72)), (cx + 22, U(80)), (cx + 16, U(84)), (cx + 9, U(82)), (cx + 3, U(85)),
           (cx - 3, U(85)), (cx - 9, U(82)), (cx - 16, U(84)), (cx - 22, U(80)), (cx - 19, U(72))]
    r.poly(cap, M['plum'], lift=0.04, group='capelet', vfun=lambda x, y: -0.18 if (x - cx) % 7 == 3 and y > U(72) else 0)
    for (p0, p1) in zip(cap[3:11], cap[4:12]):
        for i in range(8):
            t = i / 8
            r.fixed(p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t, GOLD[4] if i % 2 else GOLD[5])
    # the chest flask with the biggest heart
    heart_in_globe(r, cx, U(91), 8.0, M['heart'], beat in ('all', 'odd'), 'flask', neck=True)
    # the hood (pointed, bent back), its maroon lining, the bone beak-mask
    tilt = P.get('tilt', 0)
    hx, hy = cx + tilt, U(40)
    r.ellipsoid(hx, hy + 2, 15.5, 19, M['plum'], lift=0.06, group='hood',
                vfun=lambda x, y, u, w: (-0.2 if abs(math.atan2(w, u) * 3 % 1 - 0.5) < 0.06 and w < 0.3 else 0))
    r.poly([(hx - 12, hy - 6), (hx - 7, hy - 20), (hx - 4, hy - 29), (hx + 3, hy - 20), (hx + 11, hy - 8)], M['plum'], lift=0.1, group='hood')
    r.ellipsoid(hx, hy + 4, 10.5, 14.5, M['maroon'], lift=-0.25, group='lining')
    r.ellipsoid(hx, hy + 5, 8.6, 12.4, M['maroon'], lift=-0.95, group='hvoid')
    for k in range(18):                                                              # gold edging round the hood's opening
        a = -2.95 + k * 0.33
        r.fixed(hx + math.cos(a) * 10.6, hy + 4 + math.sin(a) * 14.6, GOLD[5] if k % 2 else GOLD[3])
    r.ellipsoid(hx, hy + 1, 6.8, 8.0, M['bone'], group='mask')
    beak = curve(lambda t: (hx + 0.5 + 1.5 * t + 3.6 * t * t * (1 + tilt * 0.4), hy + 5 + 25 * t), 10)
    worm(r, beak, 4.4, 0.7, M['bone'], 'mask')
    for i in range(2, 9):                                                            # the beak's ridge and its shade
        x, y = beak[i]
        r.fixed(x - 1, y, BONE[7] if i < 6 else BONE[6])
        r.darken(x + 2, y, 0.2)
    for sx in (-1, 1):                                                               # empty eye holes, a dim red behind
        ex = hx + (-4 if sx < 0 else 2)
        for (dx, dy) in ((0, 0), (1, 0), (0, 1), (1, 1), (0, -1), (1, -1)):
            r.fixed(ex + dx, hy + dy, (16, 8, 10))
        r.fixed(ex + 1, hy, (92, 24, 22) if not beat else (128, 34, 28))
        r.fixed(ex - 1, hy - 2, BONE[3]); r.fixed(ex + 2, hy - 2, BONE[3])
    for (x, y) in ((hx + 3, hy - 6), (hx + 4, hy - 5), (hx + 4, hy - 4), (hx + 5, hy - 3), (hx - 5, hy + 4), (hx - 4, hy + 5)):
        r.fixed(x, y, BONE[2])                                                         # cracks
    r.fixed(hx + 1, hy + 6, BONE[1]); r.fixed(hx + 3, hy + 6, BONE[1])                 # nostril slits
    # the lantern arm (viewer's left): held out, the wide sleeve hanging in a gold-trimmed fall
    shL = (cx - 17, U(76))
    handL = (cx - 36, U(97))
    elL = ik(shL, handL, 15, 14, 'down')
    r.tube(shL, elL, 6.0, 5.4, M['plum'], group='armL', folds=lambda u, sd: -0.2 if u > 0.85 and sd > 0 else 0)
    r.tube(elL, (handL[0] + 3, handL[1] - 1), 5.4, 4.6, M['plum'], group='armL')
    fall = [(elL[0] + 4, elL[1] - 3), (handL[0] + 4, handL[1] - 3), (handL[0] + 5, handL[1] + 9), (handL[0] + 9, handL[1] + 15),
            (elL[0] + 2, elL[1] + 20), (elL[0] + 6, elL[1] + 14), (elL[0] + 7, elL[1] + 4)]
    r.poly(fall, M['plum'], lift=0.0, group='fallL', vfun=lambda x, y: -0.2 if (x * 2 + y) % 6 == 0 else 0)
    for (p0, p1) in zip(fall[1:5], fall[2:6]):
        for i in range(10):
            t = i / 10
            r.fixed(p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t, GOLD[4] if i % 2 else GOLD[5])
    seam(r, 'armL', 0.28); seam(r, 'fallL', 0.2)
    # the lantern: a hook, a peaked cap, four brass bars, glass panes lit by a candle, a heart charm under it
    lx, ly = handL[0] - 0.5, handL[1] + 4
    r.tube((lx, ly - 3), (lx, ly + 1), 0.7, 0.7, M['gold'], group='lant')
    r.poly([(lx - 1.5, ly + 1), (lx + 1.5, ly + 1), (lx + 6, ly + 6), (lx - 6, ly + 6)], M['gold'], round_=0.6, group='lant')
    gut = P.get('gutter', 0)
    body_top, body_bot = ly + 6, ly + 23
    oid = r.new('lglass')
    for y in range(int(body_top), int(body_bot)):
        for x in range(int(lx - 5), int(lx + 6)):
            dfl = math.hypot((x + 0.5 - lx) / 5.0, (y + 0.5 - (ly + 14)) / 8.0)
            c = mix(FLAME[1], (60, 34, 24), min(1.0, dfl * 0.9))
            r.put(x, y, None, 0, oid, c)
    for k in range(5):                                                               # the candle and its flame
        r.fixed(lx, ly + 17 + k, (222, 206, 170) if k < 4 else (180, 160, 130)); r.fixed(lx + 1, ly + 17 + k, (186, 168, 136))
    fl = [(0, 16, 4), (0, 15, 3), (0, 14, 2), (1, 15, 2)] if not gut else [(0, 16, 3), (1, 15, 2), (1, 14, 1)]
    for (dx, y, k) in fl: r.fixed(lx + dx, ly + y, FLAME[k])
    for bx in (-5, -2, 2, 5):
        for y in range(int(body_top), int(body_bot)): r.fixed(lx + bx, y, GOLD[4] if bx < 0 else GOLD[2])
    r.poly([(lx - 6, body_bot), (lx + 6, body_bot), (lx + 5, body_bot + 3), (lx - 5, body_bot + 3)], M['gold'], round_=0.6, group='lant')
    r.tube((lx, body_bot + 3), (lx, body_bot + 6), 1.2, 0.6, M['gold'], group='lant')
    chain(r, (lx, body_bot + 6), (lx + 0.5, body_bot + 11), sag=0.3)
    for (dx, dy, c) in ((-1, 0, HEART[5]), (1, 0, HEART[4]), (-1, 1, HEART[4]), (0, 1, HEART[4]), (1, 1, HEART[3]), (0, 2, HEART[2]),
                        (-2, -1, HEART[5]), (2, -1, HEART[3])):
        r.fixed(lx + 0.5 + dx, body_bot + 12 + dy, c)
    halos.append((lx + 0.5, ly + 15, 15 - 3 * gut, FLAME[2], 0.5 - 0.15 * gut))
    # the gloved hand holding the hook from above
    r.ellipsoid(handL[0] + 1.2, handL[1] - 0.5, 3.0, 2.6, M['glove'], group='handL')
    for k in range(4):
        x0 = handL[0] + 2.4 - k * 1.5
        r.tube((x0, handL[1] + 0.5), (x0 - 1.0, handL[1] + 4.0 - abs(k - 1.5) * 0.6), 0.85, 0.7, M['glove'], group='handLf%d' % k)
        seam(r, 'handLf%d' % k, 0.14)
    # the raised arm (viewer's right): the sleeve fallen back to the elbow, a thin gloved forearm, long fingers, a heart charm
    curl = P.get('curl', 0)
    shR = (cx + 17, U(76))
    handR = (cx + 35, U(68))
    elR = (cx + 25, U(96))
    r.tube(shR, elR, 6.0, 5.4, M['plum'], group='armR', folds=lambda u, sd: -0.2 if u > 0.85 and sd < 0 else 0)
    fallR = [(elR[0] - 5, elR[1] - 4), (elR[0] + 5, elR[1] - 3), (elR[0] + 7, elR[1] + 10), (elR[0] + 3, elR[1] + 18),
             (elR[0] - 1, elR[1] + 12), (elR[0] - 6, elR[1] + 6)]
    r.poly(fallR, M['plum'], group='fallR', vfun=lambda x, y: -0.2 if (x * 2 - y) % 6 == 0 else 0)
    for (p0, p1) in zip(fallR[1:4], fallR[2:5]):
        for i in range(8):
            t = i / 8
            r.fixed(p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t, GOLD[4] if i % 2 else GOLD[5])
    seam(r, 'armR', 0.26)
    r.tube((elR[0] + 1, elR[1] - 3), (handR[0], handR[1] + 3), 2.9, 2.2, M['glove'], group='foreR')
    for y in (int(handR[1] + 7), int(handR[1] + 8)):                                  # a gold bracelet
        for dx in (-2, -1, 0, 1, 2): r.fixed(handR[0] + 0.5 + dx + (handR[1] + 8 - y) * 0, y, GOLD[5] if dx < 1 else GOLD[3])
    r.ellipsoid(handR[0], handR[1] + 0.5, 3.0, 3.4, M['glove'], group='palmR')
    lens = [6.6, 8.2, 7.8, 6.4]
    for k, ln in enumerate(lens):                                                     # long fingers, held up, gently splayed
        a = -math.pi / 2 - 0.55 + k * 0.32
        mid = (handR[0] + math.cos(a) * ln * 0.5, handR[1] - 1.5 + math.sin(a) * ln * 0.5)
        a2 = a + (0.9 if curl and k > 0 else 0.2)
        tip = (mid[0] + math.cos(a2) * ln * 0.5, mid[1] + math.sin(a2) * ln * 0.5)
        r.tube((handR[0] + (k - 1.5) * 1.1, handR[1] - 1.5), mid, 0.95, 0.85, M['glove'], group='fR%d' % k)
        r.tube(mid, tip, 0.85, 0.65, M['glove'], group='fR%d' % k)
        seam(r, 'fR%d' % k, 0.14)
    r.tube((handR[0] - 2.2, handR[1] + 0.5), (handR[0] - 4.2, handR[1] - 2.0), 1.0, 0.8, M['glove'], group='tR')
    sw = math.sin(f * 0.8) * 0.8
    chain(r, (handR[0] + 1.5, handR[1] + 1), (handR[0] + 3 + sw, handR[1] + 15), sag=0.4)
    chain(r, (handR[0] - 0.5, handR[1] + 2), (handR[0] + 0.5 + sw, handR[1] + 10), sag=0.3)
    hx2, hy2 = handR[0] + 3 + sw, handR[1] + 17
    for (dx, dy, c) in ((-1, 0, HEART[5]), (1, 0, HEART[4]), (-1, 1, HEART[4]), (0, 1, HEART[4]), (1, 1, HEART[3]), (0, 2, HEART[2]),
                        (-2, -1, HEART[6]), (2, -1, HEART[3])):
        r.fixed(hx2 + dx, hy2 + dy, c)
    r.fixed(handR[0] + 0.5 + sw, handR[1] + 11, GOLD[6])
    # the two overhead globes, on short chains from the rod ends
    for (end, sx, mat, i) in ((endL, -1, 'heart', 5), (endR, 1, 'heart', 6)):
        gx, gy = end[0], end[1] + 15
        chain(r, (end[0], end[1] + 1), (gx, gy - 8), sag=0.0)
        bt = beat == 'all' or (beat == 'odd' and i == 5)
        heart_in_globe(r, gx, gy, 7.0, M[mat], bt, 'top%d' % i)
        chain(r, (gx, gy + 9), (gx + sx * 0.5, gy + 15), sag=0.2)
        r.fixed(gx + sx * 0.5, gy + 16, GOLD[6]); r.fixed(gx + sx * 0.5, gy + 17, GOLD[3])
    im = r.render()
    return finish(im, halos)


CAST = {'sister_calyx': (calyx, CALYX_POSE), 'heartbroker_lune': (lune, LUNE_POSE), 'heir_aquarium': (heir, HEIR_POSE), 'silence': (silence, SIL_POSE)}
PAL = ([INK, WARM_INK] + VIOLET + MOSS + RAG + TEAL + BARK + GLOW + PLUM + MAROON + GOLD + PARCH + GLOVE + BONE + HEART + HEARTP
       + HEARTB + HEARTG + GLASS + FLAME + SHAG + SHAND + CLAW + SQUID + EYEA + YOLK + COAT + WAIST + TROU + BOOT)

if __name__ == '__main__':
    only = sys.argv[2].split(',') if len(sys.argv) > 2 else list(CAST)
    for cid in only:
        fn, poses = CAST[cid]
        os.makedirs(f'{OUT}/{cid}', exist_ok=True)
        frames = [fn(p, i) for i, p in enumerate(poses)]
        w, h = frames[0].size
        sheet = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
        for i, im in enumerate(frames):
            im.save(f'{OUT}/{cid}/{i}.png'); sheet.paste(im, (i * w, 0))
        sheet.save(f'{OUT}/{cid}.png')
    seen, rows = set(), []
    for c in PAL:
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/vox_guests.gpl', 'w').write('GIMP Palette\nName: vox_guests\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT)
