"""The cast of The Cardinal Feast (CardinalFeastScene, the Bishop's dream cartridge), redrawn with the character
renderer (rig.py, the Edgar quality bar) after the old AI portraits (Emils1-3.png, Pim.png, inquisitor.png,
Marigold.png, Cornelius.png, wren.png, gallow.png -- now only the reference for who they are). Swamp-church folk:
Emils is a fat toad, the rest are tailed lizard / crocodile people. Muted, earthy ramps; the cardinal's red is a
desaturated brick crimson like the rest of the cast.

  emils     128x176 x 24: three poses of 8 idle frames each -- 0-7 reading (a hand to the spectacles, an open book),
            8-15 the toast (a glass of wine raised, the crosier slanted in the other hand), 16-23 the welcome (the crosier
            upright, the other hand open). Soles on y 172.
  pim       128x128 x 8   the young novice: brown habit + cream capelet, a horn through the hood, book, wooden cross
  vesper    128x176 x 8   Inquisitor Vesper Tann: a black-brown habit with a red lining, a candle-crowned staff, a book
  marigold  128x160 x 8   Sister Marigold, the cook: headscarf, apron, stirring a pot of stew on her hip
  cornelius 128x160 x 8   Cornelius Brack: a portly crocodile in a top hat + monocle, coin sack and goblet
  wren      128x144 x 8   Wren: a small lizard in a cream shawl, a letter and a quill
  gallow    128x176 x 8   Gallow the butcher: a burly crocodile, toque, bloodied apron, cleaver, meat + sausages
Every sheet also gets a half-size twin (<id>_t.png, 64 px wide) -- the mini-game is a top-down room where a 128 px
figure would be a giant; the token is box-filtered from the full frame and snapped back onto the character's ramps.
python3 feast_cast.py <outdir> [id ...]  ->  <id>.png + <id>_t.png + <id>/<n>.png + feast_cast.gpl + preview.png"""
import sys, os, math
from PIL import Image
from common import ramp, INK, h32
import rig
from rig import Rig, Mat
from feral_toast import ik
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
R = ramp

# ---- ramps -----------------------------------------------------------------------------------------------------------
TOAD   = R('#11160c #1a2212 #243019 #2f3e20 #3b4d28 #4a5d31 #5a6e3b #6d8047 #829255 #98a568')
THROAT = R('#3a3524 #4f4932 #666042 #7e7754 #968e68 #ada57e #c2ba94 #d4cdaa')
LIZ    = R('#13180e #1d2415 #28311c #333f24 #3f4d2c #4c5b35 #5a6a3f #6a7a4a #7c8a58')
BELLY  = R('#3c3a26 #545033 #6c6743 #857e55 #9c9468 #b1a97c #c4bc92')
CROC   = R('#10160d #192113 #222d19 #2c3a1f #374726 #43552e #506337 #5f7341 #70844c')
ROBE   = R('#140707 #210b0a #300f0d #411411 #521a15 #63221a #742b20 #853527 #95412f')
GOLD   = R('#2e200a #4e3812 #74561c #9a7628 #bc963a #d8b658 #eed488')
LACE   = R('#3e3a31 #57524a #706a5d #8a8472 #a29c88 #b8b29c #cbc5ae')
LEATH  = R('#1c0c0a #2c1410 #3e1d16 #52281e #663428 #7a422f')
PAGES  = R('#5e5948 #77715d #8f8973 #a6a08a #bab49c #ccc6ae')
WINE   = R('#1e0508 #34090f #4e1016 #6a1a1e #84282a')
HABIT  = R('#140d08 #1f150d #2b1c12 #382517 #452e1d #533824 #61422b #6f4d33')
CAPE   = R('#3c3426 #554b37 #6e6249 #877a5c #9e906f #b2a482 #c3b694')
DARK   = R('#0d0b0a #151210 #1d1916 #26201c #2f2822 #3a3029 #453931')
LINING = R('#1e0608 #300a0c #451012 #5a1717 #6e201d')
IRON   = R('#121313 #1c1d1d #282928 #353634 #444441 #55544f #68665e #7d7a70')
STEW   = R('#3a1608 #58240c #763612 #924a1a #a85e26 #ba7434')
WOOD   = R('#24140b #3c230f #553317 #6f4520 #8a582a #a46d37 #bb8447')
BROWN  = R('#160e09 #22160e #2e1e13 #3b2719 #48311f #563b26 #64462d #735236')
SCARF  = R('#3d382c #565041 #706957 #89826d #a29a83 #b7b098 #c9c2ab')
APRON  = R('#47423a #605a4e #7a7363 #948c79 #aaa28d #bdb5a0 #cdc6b2')
MAROON = R('#160809 #230c0e #321114 #42171a #521e20 #622728 #723131')
OCHRE  = R('#24180a #36240f #4a3214 #5e401a #735021 #876029 #9a7133 #ab823f')
STRIPE = R('#121010 #1b1817 #24201e #2e2926 #39332f #443d38')
SACK   = R('#2c2214 #40321e #554428 #6b5734 #806a41 #957d50 #a68f60')
COIN   = R('#3a2a0c #5e4614 #86661e #ad8a2c #ccaa42 #e2c866')
FLESH  = R('#260c0b #3e1513 #561f1c #6c2a24 #7e382e #8e4838 #9c5a46')
STAIN  = R('#2e1210 #45201a #5a2c22')
TOQUE  = R('#4a463c #66604f #807964 #9a937c #b0a990 #c3bca4 #d2ccb6')
EYE_Y  = R('#3e2c08 #6a4c10 #96701c #bc922c #d8b146 #ecce70')
EYE_B  = R('#1e120a #34200f #4c3016 #64421e #7a5628')
EYE_R  = R('#2a0c08 #4a160c #6a2412 #8a361c')
FLAME  = [(120, 52, 18), (196, 98, 30), (236, 156, 56), (250, 210, 120), (255, 244, 206)]
PUPIL  = (14, 10, 8)
SHINE  = (250, 244, 222)
WARM_INK = (34, 20, 14)

# extra textures (in this process only): a heavy velvet with soft mottling, warty toad skin, a scaled hide, dirty linen
rig.TEX['velvet'] = lambda x, y: ((rig.nF(x * 1.5, y * 1.5) - 0.5) * 0.09 + (rig.nM(x * 0.8, y * 1.1) - 0.5) * 0.22
                                  + (rig.nL(x * 0.6 + 17, y * 0.5) - 0.5) * 0.22 + (0.02 if (x + 2 * y) % 3 == 0 else -0.01))
def _warts(x, y):
    v = (rig.nM(x * 1.3, y * 1.3) - 0.5) * 0.14 + (rig.nF(x, y) - 0.5) * 0.05
    k = h32(x // 3, y // 3, 7) % 9
    if k == 0 and x % 3 == 1 and y % 3 == 1: v += 0.16
    if k == 0 and x % 3 == 2 and y % 3 == 2: v -= 0.12
    return v
rig.TEX['warts'] = _warts
def _scales(x, y):
    ox = (y // 3) % 2 * 2
    fx, fy = (x + ox) % 4, y % 3
    return (rig.nM(x, y) - 0.5) * 0.10 + (-0.07 if fx == 3 or fy == 2 else 0.03 if fx == 0 and fy == 0 else 0)
rig.TEX['scales'] = _scales
rig.TEX['linen'] = lambda x, y: ((rig.nF(x * 1.8, y * 1.8) - 0.5) * 0.10 + (rig.nL(x * 0.9 + 60, y * 0.9) - 0.5) * 0.16
                                 + (0.025 if (x + y) % 2 else -0.02))
rig.TEX['coarse'] = lambda x, y: ((rig.nF(x * 1.6, y * 1.6) - 0.5) * 0.12 + (rig.nM(x, y * 1.4) - 0.5) * 0.14
                                  + (0.03 if (x * 2 + y) % 3 == 0 else -0.01))

M = {'toad': Mat(TOAD, 'warts', 0.26, 0.2), 'throat': Mat(THROAT, 'skin', 0.32, 0.12),
     'robe': Mat(ROBE, 'velvet', 0.18, 0.06), 'robe2': Mat(ROBE, 'velvet', 0.14),
     'gold': Mat(GOLD, 'metal', 0.26, 0.8), 'lace': Mat(LACE, 'linen', 0.3),
     'leath': Mat(LEATH, 'leather', 0.22, 0.3), 'pages': Mat(PAGES, 'plain', 0.42),
     'liz': Mat(LIZ, 'scales', 0.26, 0.25), 'belly': Mat(BELLY, 'skin', 0.3, 0.12), 'croc': Mat(CROC, 'scales', 0.24, 0.25),
     'habit': Mat(HABIT, 'coarse', 0.18), 'cape': Mat(CAPE, 'linen', 0.26), 'dark': Mat(DARK, 'coarse', 0.2, 0.05),
     'lining': Mat(LINING, 'velvet', 0.2), 'iron': Mat(IRON, 'metal', 0.22, 0.7), 'stew': Mat(STEW, 'skin', 0.34, 0.5),
     'wood': Mat(WOOD, 'wood', 0.26, 0.2), 'brown': Mat(BROWN, 'coarse', 0.2), 'scarf': Mat(SCARF, 'linen', 0.28),
     'apron': Mat(APRON, 'linen', 0.28), 'maroon': Mat(MAROON, 'wool', 0.2, 0.05), 'ochre': Mat(OCHRE, 'fabric', 0.24, 0.25),
     'stripe': Mat(STRIPE, 'fabric', 0.2), 'sack': Mat(SACK, 'coarse', 0.26), 'coin': Mat(COIN, 'metal', 0.3, 0.9),
     'flesh': Mat(FLESH, 'skin', 0.3, 0.45), 'toque': Mat(TOQUE, 'linen', 0.3), 'wine': Mat(WINE, 'plain', 0.3, 0.6),
     'rope': Mat(CAPE, 'wool', 0.26)}


def mix(a, b, t): return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def group_at(r, x, y):
    e = r.buf.get((int(x), int(y)))
    return r.groups[e[2]] if e else None


def tint(r, x, y, col, t):
    """blend a pixel that is already fixed (or will be rendered) toward col -- only for fixed pixels"""
    e = r.buf.get((int(x), int(y)))
    if e and e[3] is not None: e[3] = mix(e[3], col, t)


BAND_L = [(-0.5, -0.7, 0.55)]          # the key light of the hand-pixelled volumes (mirrored with rig.LIGHT for a flipped figure)


def banded(r, cx, cy, rx, ry, ramp_, group, lo=1, hi=None, clip=None, vfun=None, L=None, flat=1.0, amb=0.2):
    """a clean, hand-pixelled shaded volume (no dither) -- faces, so the features read at 1x"""
    hi = len(ramp_) - 1 if hi is None else hi
    L = L or BAND_L[0]
    if L is not BAND_L[0] and BAND_L[0][0] > 0: L = (-L[0], L[1], L[2])
    ln = math.sqrt(sum(c * c for c in L)); L = tuple(c / ln for c in L)
    oid = r.new(group)
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            u, w = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            d = u * u + w * w
            if d > 1 or (clip and not clip(x, y)): continue
            n = (u * flat, w * flat, math.sqrt(max(0.04, 1 - d * flat * flat)))
            v = amb + (1 - amb) * max(0.0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2])
            if vfun: v += vfun(x, y, u, w)
            k = lo + int(v * (hi - lo + 0.999))
            r.fixed(x, y, ramp_[max(lo, min(hi, k))], oid)
    return oid


def gold_line(r, pts, w=2, glint=True):
    """a gold braid along a polyline: lit on its upper-left side; w 1 or 2 px"""
    out = []
    for (a, b) in zip(pts, pts[1:]):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 1.5) + 1
        for k in range(n + 1):
            t = k / n
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    seen = set()
    for i, (x, y) in enumerate(out):
        p = (int(math.floor(x)), int(math.floor(y)))
        if p in seen: continue
        seen.add(p)
        c = GOLD[4] if (p[0] + p[1]) % 5 else GOLD[5]
        if glint and (p[0] * 7 + p[1] * 3) % 23 == 0: c = GOLD[6]
        r.fixed(p[0], p[1], c)
        if w > 1:
            q = (p[0] + 1, p[1]) if abs(out[min(i + 1, len(out) - 1)][1] - y) >= abs(out[min(i + 1, len(out) - 1)][0] - x) else (p[0], p[1] + 1)
            if q not in seen: r.fixed(q[0], q[1], GOLD[2] if (q[0] + q[1]) % 3 else GOLD[3])


def chain(r, x0, x1, y0, sag, ph=0):
    """a hanging gold chain (a catenary-ish arc) of alternating links"""
    n = int(abs(x1 - x0)) * 2
    last = None
    for k in range(n + 1):
        t = k / n
        x = x0 + (x1 - x0) * t
        y = y0 + sag * (1 - (2 * t - 1) ** 2)
        p = (int(math.floor(x)), int(math.floor(y)))
        if p == last: continue
        last = p
        i = (p[0] + ph) % 3
        r.fixed(p[0], p[1], (GOLD[5], GOLD[3], GOLD[1])[i])
        if i == 0: r.fixed(p[0], p[1] + 1, GOLD[2])


def cross(r, x, y, h=9, w=7, t=2, gem=None, ramp_=GOLD):
    """a gold cross, (x, y) = top of the upright (its left column)"""
    arm = y + h // 3
    for yy in range(y, y + h):
        for xx in range(x, x + t):
            r.fixed(xx, yy, ramp_[5] if xx == x and yy < y + h - 2 else ramp_[3] if xx == x else ramp_[2])
    xl = x - (w - t) // 2
    for xx in range(xl, xl + w):
        for yy in range(arm, arm + t):
            r.fixed(xx, yy, ramp_[5] if yy == arm and xx < x + t else ramp_[4] if yy == arm else ramp_[2])
    r.fixed(x, y, ramp_[6])
    if gem: r.fixed(x + (t - 1) // 2, arm + (t - 1) // 2, gem)
    for yy in range(y + 1, y + h + 1): r.darken(x + t, yy, 0.18)
    for xx in range(xl + 1, xl + w + 1): r.darken(xx, arm + t, 0.18)


def hand(r, c, mat, g, fingers=4, ang=90, spread=22, ln=4.0, curl=0.0, claw=None, pad=None, size=1.0, thumb=None):
    """a hand / forefoot: a palm ellipsoid + fingers fanning around `ang` (degrees, 90 = straight down, screen coords);
    curl shortens + bends them; claw = a ramp for claw tips, pad = a colour for frog finger pads"""
    x, y = c
    r.ellipsoid(x, y, 3.0 * size, 2.8 * size, mat, group=g)
    for k in range(fingers):
        a = math.radians(ang + (k - (fingers - 1) / 2) * spread / max(1, fingers - 1) * 2)
        L = ln * size * (1 - 0.45 * curl) * (0.85 if k in (0, fingers - 1) else 1.0)
        bx, by = x + math.cos(a) * 2.2 * size, y + math.sin(a) * 2.2 * size
        ex, ey = bx + math.cos(a) * L, by + math.sin(a) * L
        if curl:
            b2 = a + math.radians(70 * curl) * (1 if math.cos(a) >= 0 else -1) * (-1 if ang > 90 else 1)
            ex, ey = bx + math.cos(a) * L * 0.6 + math.cos(b2) * L * 0.5, by + math.sin(a) * L * 0.6 + math.sin(b2) * L * 0.5
        r.tube((bx, by), (ex, ey), 1.0 * size, 0.8 * size, mat, group=g + 'f%d' % k)
        seam(r, g + 'f%d' % k, 0.14)
        if pad: r.fixed(ex, ey, pad)
        if claw:
            r.fixed(ex + math.cos(a), ey + math.sin(a), claw[2]); r.fixed(ex + math.cos(a) * 2, ey + math.sin(a) * 2, claw[0])
    if thumb:
        (tx, ty) = thumb
        r.tube((x, y), (x + tx, y + ty), 1.2 * size, 0.9 * size, mat, lift=0.06, group=g + 't')
        seam(r, g + 't', 0.16)


def sheet(frames, path):
    w, h = frames[0].size
    s = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, im in enumerate(frames): s.paste(im, (i * w, 0))
    s.save(path)
    return s


def warm_ink(im):
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y] == (18, 14, 12, 255): px[x, y] = WARM_INK + (255,)
    return im


# ======================================================================================================================
# Cardinal Emils Ven -- a fat toad in a cardinal's mantle, mitre, gold chains, round gold spectacles
# ======================================================================================================================
EMILS_POSE = {
    'read':    [dict(), dict(b=1), dict(look=-1), dict(look=1), dict(blink=1), dict(nudge=1), dict(page=1), dict(puff=1)],
    'toast':   [dict(), dict(b=1), dict(raise_=1), dict(raise_=1, slosh=1), dict(), dict(blink=1), dict(puff=1), dict(b=1, puff=2)],
    'welcome': [dict(), dict(b=1), dict(blink=1), dict(beckon=1), dict(beckon=2), dict(puff=1), dict(look=1), dict(b=1)],
}
EHX, EHY = 64, 61                     # the body's axis, the head's row
TURN = 4                              # a 3/4 turn to the viewer's right: the front line (opening, chains, cross) sits right
                                      # of the axis, the near (left) half of the mantle is wider, the far half narrower
EHEAD = EHX + 3                       # the head turns with the body
MOUTH = lambda dx: EHY + 5.5 + (abs(dx) / 18.0) ** 2 * 1.4 - (1.2 if abs(dx) > 15.5 else 0) - (1.0 if dx > 12 else 0) - (1.0 if dx > 16.5 else 0)


def emils_head(r, P):
    b = P.get('b', 0)
    hx, hy = EHEAD, EHY - b
    look = P.get('look', 0)
    puff = P.get('puff', 0)
    # the skull: wide, flat, warty; the jaw's corners frame the pale throat
    def skull(x, y, u, w):
        v = _warts(x, y) * 1.4
        if w > 0.5: v -= 0.1
        if abs(u) > 0.85: v -= 0.08
        return v
    banded(r, hx, hy, 21.5, 12.5, TOAD, 'skull', lo=1, vfun=skull, flat=0.9)
    # the eye bulges at the top corners
    for i, sx in enumerate((-1, 1)):
        banded(r, hx + sx * 11.5 + 1.3, hy - 6.0, 7.6 * (1 if sx < 0 else 0.88), 6.2, TOAD, 'bulge%d' % i, lo=1, vfun=lambda x, y, u, w: _warts(x, y), flat=0.95)
    for i, sx in enumerate((-1, 1)):                                                 # heavy jowls framing the throat
        banded(r, hx + sx * 13.5, hy + 9.5, 8.0, 8.5, TOAD, 'jowl%d' % i, lo=1, hi=7, vfun=lambda x, y, u, w: _warts(x, y) * 1.3 - 0.06,
               flat=0.9, clip=lambda x, y: y > MOUTH(x + 0.5 - hx) - b - 3)
    # the throat: a huge pale dewlap from the mouth down over the chains -- pear-shaped, sagging, curved wrinkles,
    # swelling on a puff
    ty, trx, try_ = hy + 14 + puff * 0.6, 16.0 + puff * 1.0, 14.5 + puff * 0.8
    def tclip(x, y):
        if y <= MOUTH(x + 0.5 - hx) - b: return False
        w = (y + 0.5 - ty) / try_
        return abs(x + 0.5 - hx - 1.5) <= trx * math.sqrt(max(0.0, 1 - w * w)) * (1 - 0.22 * max(0.0, w))
    def folds(x, y, u, w):
        f = (y - hy) - 3.0 * u * u
        k = int(math.floor(f)) % 4
        v = (-0.2 if k == 0 and abs(u) < 0.92 and w > -0.55 else 0.04 if k == 1 and abs(u) < 0.8 else 0)
        return v + (rig.nM(x * 1.7, y * 1.7) - 0.5) * 0.16 - (0.14 if w > 0.6 else 0) - 0.06 * abs(u)
    oid = banded(r, hx + 1.5, ty, trx, try_, THROAT, 'throat', lo=0, hi=6, vfun=folds, flat=0.85, clip=tclip, amb=0.12)
    for (x, y), e in list(r.buf.items()):                                            # green mottling creeping in at its edges
        if e[2] != oid or e[3] is None: continue
        u = (x + 0.5 - hx) / trx
        if abs(u) > 0.62 and h32(x, y, 21) % 3 == 0 or abs(u) > 0.8 and h32(x, y, 22) % 2 == 0:
            e[3] = mix(e[3], TOAD[4 + (h32(x, y, 23) % 3)], 0.45)
    for dx in range(-15, 16):                                                       # the jaw's shadow on the throat
        y = int(MOUTH(dx) - b) + 1
        e = r.buf.get((hx + dx, y))
        if e and e[3] is not None: e[3] = mix(e[3], THROAT[1], 0.55)
    # the eyes: heavy-lidded toad eyes, gold irises with a horizontal pupil
    for i, sx in enumerate((-1, 1)):
        ex, ey = hx + sx * 11.5 + 0.8, hy - 5
        erx = 4.4 if sx < 0 else 3.8
        if P.get('blink'):
            for x in range(int(ex - 3), int(ex + 4)): r.fixed(x, ey, TOAD[1]); r.fixed(x, ey - 1, TOAD[7]); r.fixed(x, ey + 1, TOAD[4])
            continue
        for yy in range(ey - 3, ey + 4):
            for xx in range(int(ex - 5), int(ex + 6)):
                d = ((xx + 0.5 - ex - 0.5) / erx) ** 2 + ((yy + 0.5 - ey) / 3.2) ** 2
                if d <= 1: r.fixed(xx, yy, EYE_Y[1] if d > 0.75 else EYE_Y[4] if yy < ey else EYE_Y[3] if yy == ey else EYE_Y[2])
        px_ = int(ex) + look
        for xx in range(px_ - 1, px_ + 3): r.fixed(xx, ey, PUPIL)
        r.fixed(px_, ey + 1, PUPIL); r.fixed(px_ + 1, ey + 1, PUPIL)
        r.fixed(int(ex) - 2, ey - 1, SHINE)
        for xx in range(int(ex - 5), int(ex + 6)):                                 # the heavy upper lid, half shut
            r.fixed(xx, ey - 3, TOAD[7] if xx < ex else TOAD[6])
            r.fixed(xx, ey - 2, TOAD[5] if xx < ex else TOAD[4])
            r.fixed(xx, ey - 1, (26, 24, 14)) if abs(xx - ex - 0.5) < 4 else None
        for xx in range(int(ex - 3), int(ex + 4)): r.fixed(xx, ey + 3, TOAD[3])
    # the spectacles: round gold rims, a bridge over the snout; the lenses catch the light
    ny = -1 if P.get('nudge') else 0
    for i, sx in enumerate((-1, 1)):
        cx, cy = hx + sx * 11.5 + 1.3, hy - 4.5 + ny
        for yy in range(int(cy - 7), int(cy + 7)):
            for xx in range(int(cx - 7), int(cx + 7)):
                d = math.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
                if 4.6 < d <= 5.6:
                    a = math.atan2(yy + 0.5 - cy, xx + 0.5 - cx)
                    r.fixed(xx, yy, GOLD[5] if -2.6 < a < -0.8 else (GOLD[1] if 0.5 < a < 2.6 else GOLD[3]))
                elif d <= 4.6:
                    tint(r, xx, yy, (226, 220, 190), 0.10)
        r.fixed(int(cx - 3), int(cy - 3), (255, 250, 230)); r.fixed(int(cx - 2), int(cy - 3), (236, 228, 196))
        r.fixed(int(cx - 3), int(cy - 2), (236, 228, 196))
        for k in range(2): r.fixed(int(cx + sx * (6 + k)), int(cy - 1), GOLD[2 - k])
    by = int(hy - 5 + ny)
    for xx in range(hx - 5, hx + 8): r.fixed(xx, by - (1 if abs(xx - 0.5 - hx) < 3 else 0), GOLD[5] if xx < hx + 1 else GOLD[3])
    # nostrils, the wide mouth (a smug curl at the corners)
    for (x, c1) in ((hx - 3, TOAD[7]), (hx + 4, TOAD[6])):
        r.fixed(x, hy + 1, TOAD[1]); r.fixed(x, hy, c1)
    for dx in range(-19, 20):
        y = MOUTH(dx) - b
        r.fixed(hx + dx, y, (28, 24, 14))
        if abs(dx) < 17: r.fixed(hx + dx, y - 1, TOAD[6] if dx < 0 else TOAD[5])
    r.fixed(hx - 20, hy + 3 - b, (28, 24, 14)); r.fixed(hx + 19, hy + 3 - b, (28, 24, 14))


def mitre(r, P):
    b = P.get('b', 0)
    hx, by = EHEAD, EHY - 10 - b
    pts = [(hx - 13.5, by), (hx - 13.0, by - 12), (hx - 10, by - 21), (hx - 4, by - 28), (hx, by - 30.5),
           (hx + 4, by - 28), (hx + 10, by - 21), (hx + 13.0, by - 12), (hx + 13.5, by)]
    r.poly(pts, Mat(ROBE, 'velvet', 0.22, 0.2), round_=0.85, group='mitre',
           vfun=lambda x, y: (0.08 if y < by - 18 else 0) - (0.05 if (x + y) % 7 == 0 else 0))
    for x in range(int(hx - 13), int(hx + 14)):                                     # the gold circlet, red stones
        for y in range(by - 5, by):
            r.fixed(x, y, GOLD[5] if y == by - 5 else GOLD[4] if y == by - 4 else GOLD[1] if y == by - 1 else GOLD[3])
        if (x - hx) % 5 == 0: r.fixed(x, by - 3, (128, 30, 32)); r.fixed(x, by - 2, (84, 18, 22))
    gold_line(r, [(hx - 13, by - 6), (hx - 12.6, by - 12), (hx - 9.6, by - 20.6), (hx - 3.8, by - 27.6), (hx, by - 30.2)], w=1)
    gold_line(r, [(hx, by - 30.2), (hx + 3.8, by - 27.6), (hx + 9.6, by - 20.6), (hx + 12.6, by - 12), (hx + 13, by - 6)], w=1)
    for y in range(by - 27, by - 5): r.fixed(hx, y, GOLD[4]); r.fixed(hx + 1, y, GOLD[2])  # the upright band
    cross(r, hx, by - 24, h=12, w=10, t=2)


def mantle_width(y, b):
    """half-width of the mantle at row y: sloping shoulders, a toad's belly, a hem that flares and curls in"""
    t = y - (74 - b)
    if t < 0: return 0
    if t < 12: return 15 + 15 * math.sin(t / 12 * math.pi / 2)
    if t < 50: return 30 + 8 * math.sin((t - 12) / 38 * math.pi / 2)
    if t < 88: return 38 + 4.5 * (t - 50) / 38
    return 42.5 - (t - 88) * 0.5


def emils_body(r, P, pose):
    b = P.get('b', 0)
    hx = EHX
    fc = hx + TURN
    WL, WR = lambda y: mantle_width(y, b) * 1.06 + 0.5, lambda y: mantle_width(y, b) * 0.93
    for i, sx in enumerate((-1, 1)):                                                  # webbed toes under the hem
        fx = hx + 2 + sx * 13 + (3 if sx > 0 else 0)
        r.ellipsoid(fx, 169, 7.5, 3.2, M['toad'], group='foot%d' % i)
        for k in range(3):
            dx = (k - 1) * 4.4 + sx * 2
            r.tube((fx + dx * 0.5, 168.5), (fx + dx * 1.15 + sx, 171.3), 1.7, 1.5, M['toad'], group='toe%d%d' % (i, k))
            r.fixed(fx + dx * 1.15 + sx + (1 if dx > 0 else -1), 171, TOAD[8])
            seam(r, 'toe%d%d' % (i, k), 0.15)
    # the cassock in the mantle's front opening: the belly pushes it out; gold buttons down the middle
    r.poly([(fc - 10, 92 - b), (fc + 9, 92 - b), (fc + 13, 120), (fc + 14, 166), (fc - 15, 166), (fc - 14, 120)], M['robe2'],
           round_=0.85, tilt=0.15, group='cassock',
           vfun=lambda x, y: (-0.16 if abs(x + 0.5 - fc) < 1 and y > 100 else 0) + (-0.12 if y > 160 else 0)
           + (0.08 if 108 < y < 124 else 0))
    for y in range(100 - b, 162, 6):
        r.fixed(fc - 1, y, GOLD[5]); r.fixed(fc, y, GOLD[3]); r.fixed(fc - 1, y + 1, GOLD[3]); r.fixed(fc, y + 1, GOLD[1])
    # the mantle: two heavy panels from the shoulders, folds fanning to the hem, open in front
    def mantle_v(x, y):
        t = max(0.0, (y - 84) / 82.0)
        v = 0.0
        for (xt, xb, k) in ((hx - 22, hx - 35, 0.18), (hx - 15, hx - 23, 0.14), (hx + 15, hx + 24, 0.14), (hx + 22, hx + 36, 0.18)):
            fx = xt + (xb - xt) * t
            d = x + 0.5 - fx
            if t > 0.05:
                s = min(1.0, t * 2.5)
                if -1.3 < d < 0.7: v -= k * s
                elif 0.7 <= d < 2.8: v += k * 0.5 * s
        span = 7.0 + t * 6.0
        v += 0.09 * math.sin((x + 0.5 - hx) / span * math.pi + 0.6) * min(1.0, t * 3)
        return v - (0.08 if y > 160 else 0)
    ys = list(range(74 - b, 167))
    hemL = lambda y: y + (1 if y > 160 else 0)                                         # the weight leg's side hangs a pixel lower
    edgeL = [(hx - WL(y), hemL(y)) for y in ys]
    edgeR = [(hx + WR(y), y) for y in ys]
    openL = [(fc - 10 - max(0, y - 92) * 0.06, y) for y in ys if y >= 92 - b]
    openR = [(fc + 9 + max(0, y - 92) * 0.05, y) for y in ys if y >= 92 - b]
    r.poly(edgeL + [(fc - 10.5, 167)] + openL[::-1] + [(fc - 2, 74 - b)], M['robe'], round_=0.7, group='mantleL', vfun=mantle_v)
    r.poly([(fc + 2, 74 - b)] + openR + [(fc + 9.5, 167)] + edgeR[::-1], M['robe'], round_=0.7, group='mantleR', vfun=mantle_v)
    # the free (right) knee pushes the mantle forward: a lit swell, the cloth falling away under it
    for (x, y), e in r.buf.items():
        if e[0] is None or r.groups[e[2]] != 'mantleR': continue
        d = ((x + 0.5 - (fc + 20)) / 7.0) ** 2 + ((y + 0.5 - 140) / 11.0) ** 2
        if d < 1: e[1] += 0.12 * (1 - d) * (1 if y < 142 else -0.6)
    seam(r, 'mantleL', 0.16); seam(r, 'mantleR', 0.16)
    gold_line(r, [openL[0], openL[-1]], w=2)
    gold_line(r, [openR[0], openR[-1]], w=2)
    gold_line(r, [(hx - WL(y) + 1.5, hemL(y)) for y in range(158, 167, 2)] + [(fc - 11, 167)], w=2)
    gold_line(r, [(fc + 10, 166)] + [(hx + WR(y) - 1.5, y) for y in range(166, 157, -2)], w=2)
    for x in range(hx - 46, hx + 42): r.darken(x, 167 + (1 if x < hx - 10 else 0), 0.15); r.darken(x, 168 + (1 if x < hx - 10 else 0), 0.08)


def upper_sleeve(r, sh, el, g):
    r.tube(sh, el, 7.8, 7.2, M['robe'], group=g, folds=lambda u, sd: (-0.2 if u > 0.8 and abs(sd) < 0.5 else 0) + (0.1 if sd < -0.5 else 0))
    seam(r, g, 0.2)


def lower_sleeve(r, el, wr, g, opening=9.0):
    """the forearm half of a cardinal's bell sleeve: a cone widening to the opening, its lower lip sagging; when the
    forearm is raised the wide sleeve slides back toward the elbow and the bare toad forearm shows. Gold edging, a
    lace ruffle. Returns the point where the hand starts."""
    dx, dy = wr[0] - el[0], wr[1] - el[1]; L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    if ny < 0 or (abs(ny) < 0.2 and nx < 0): nx, ny = -nx, -ny
    raised = uy < -0.45
    cl = L * (0.45 if raised else 1.0)
    C = (el[0] + ux * cl, el[1] + uy * cl)
    if raised:
        r.tube(C, wr, 3.4, 3.0, M['toad'], group=g + 'skin')
    sag = 4.0 * abs(ux) + (3.0 if raised else 0)
    m = (el[0] + ux * cl * 0.5, el[1] + uy * cl * 0.5)
    pts = [(el[0] - nx * 7.0, el[1] - ny * 7.0), (m[0] - nx * (7.0 + opening * 0.8) / 2 * 1.04, m[1] - ny * (7.0 + opening * 0.8) / 2 * 1.04),
           (C[0] - nx * opening * 0.8, C[1] - ny * opening * 0.8), (C[0] + ux * 1.4, C[1] + uy * 1.4),
           (C[0] + nx * (opening + sag), C[1] + ny * (opening + sag)),
           (m[0] + nx * (7.4 + opening + sag) / 2 * 1.08, m[1] + ny * (7.4 + opening + sag) / 2 * 1.08), (el[0] + nx * 7.4, el[1] + ny * 7.4)]
    r.poly(pts, M['robe'], round_=0.8, group=g + 'cone',
           vfun=lambda x, y: -0.16 if ((x - el[0]) * nx + (y - el[1]) * ny) > 3 and int((x - el[0]) * ux + (y - el[1]) * uy) % 5 == 0 else 0)
    a, c = (C[0] - nx * opening * 0.8, C[1] - ny * opening * 0.8), (C[0] + nx * (opening + sag), C[1] + ny * (opening + sag))
    gold_line(r, [a, (C[0] + ux * 1.4, C[1] + uy * 1.4), c], w=2, glint=False)
    seam(r, g + 'cone', 0.22)
    lc = (C[0] + ux * 1.5, C[1] + uy * 1.5)
    r.tube((lc[0] - nx * 4.0, lc[1] - ny * 4.0), (lc[0] + nx * 4.4, lc[1] + ny * 4.4), 2.0, 2.0, M['lace'], group=g + 'lace',
           folds=lambda u, sd: -0.22 if int(u * 7) % 2 else 0.04)
    seam(r, g + 'lace', 0.16)
    return (wr[0] + ux * 1.0, wr[1] + uy * 1.0) if raised else (C[0] + ux * 4.0, C[1] + uy * 4.0)


def mozzetta(r, P):
    """the short shoulder cape over the mantle: rounded shoulders, a gold-edged hem, the chains + cross on it"""
    b = P.get('b', 0)
    hx = EHX
    fc = hx + TURN
    top = 74 - b
    def hw(y, sx):
        t = y - top
        return min(34.0, 14 + 21 * math.sin(min(1.0, t / 13) * math.pi / 2)) * (1.06 if sx < 0 else 0.93)
    def hem(x): return 107 - b - 4.0 * ((x - fc) / 34.0) ** 2 + (1 if x < hx - 20 else 0)
    ys = list(range(top, int(hem(hx - 36)) + 1))
    left = [(hx - hw(y, -1), y) for y in ys]
    right = [(hx + hw(y, 1), y) for y in ys if y <= hem(hx + hw(y, 1))][::-1]
    xl, xr = hx - hw(ys[-1], -1), hx + hw(ys[-1], 1)
    bottom = [(x, hem(x)) for x in range(int(xl), int(xr) + 1, 4)]
    r.poly(left + bottom + right, M['robe'], round_=0.85, tilt=-0.1, group='mozz',
           vfun=lambda x, y: (-0.18 if y > top + 10 and abs((x + 0.5 - fc) % 11 - 5.5) < 0.8 else 0) + (-0.12 if y > hem(x + 0.5) - 2 else 0))
    seam(r, 'mozz', 0.22)
    gold_line(r, [(x, hem(x) - 1) for x in range(int(xl) + 1, int(xr), 2)], w=2)
    for (sag, y0, ph) in ((9, 84 - b, 0), (14, 85 - b, 1), (19, 86 - b, 2)):
        chain(r, fc - 22, fc + 19, y0, sag, ph)
    cross(r, fc - 1, 104 - b, h=16, w=11, t=3, gem=(150, 30, 34))


def frog_hand(r, c, g, ang, fingers=4, spread=20, ln=4.6, curl=0.0, thumb=None, size=1.45):
    """a big webbed toad hand with round finger pads"""
    hand(r, c, M['toad'], g, fingers=fingers, ang=ang, spread=spread, ln=ln, curl=curl, size=size, thumb=thumb)
    for k in range(fingers):
        aa = math.radians(ang + (k - (fingers - 1) / 2) * spread / max(1, fingers - 1) * 2)
        L = ln * size * (1 - 0.45 * curl) * (0.85 if k in (0, fingers - 1) else 1.0) + 2.2 * size
        if curl > 0.3: continue
        px_, py_ = c[0] + math.cos(aa) * L, c[1] + math.sin(aa) * L
        r.fixed(px_, py_, TOAD[8]); r.fixed(px_ + math.cos(aa) * 0.9, py_ + math.sin(aa) * 0.9, TOAD[6])


def crosier(r, base, top, g, crook_dir=1):
    """a gold crosier from `base` (the foot) to `top` (where the crook starts): a staff, a knop, the curling crook"""
    (bx, by), (tx, ty) = base, top
    r.tube((bx, by), (tx, ty), 1.5, 1.7, M['gold'], group=g)
    dx, dy = tx - bx, ty - by; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
    k = (tx - ux * 5, ty - uy * 5)
    r.ellipsoid(k[0], k[1], 3.0, 3.0, M['gold'], lift=0.08, group=g + 'knop')
    r.tube((tx - ux * 10, ty - uy * 10), (tx - ux * 9, ty - uy * 9), 2.4, 2.4, M['gold'], group=g + 'knop')
    px, py = -uy * crook_dir, ux * crook_dir
    cx, cy = tx + ux * 7 + px * 7, ty + uy * 7 + py * 7
    pts = []
    a0 = math.atan2(ty - cy, tx - cx)
    for i in range(0, 29):
        a = a0 - crook_dir * i / 28 * math.pi * 1.6
        rr = 7.4 - i / 28 * 2.8
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    for (a, c) in zip(pts, pts[1:]):
        r.tube(a, c, 1.9, 1.9, M['gold'], group=g + 'crook')
    r.ellipsoid(pts[-1][0], pts[-1][1], 2.2, 2.2, M['gold'], lift=0.1, group=g + 'crook')
    for d in range(-2, 3): r.fixed(cx + d, cy, GOLD[5]); r.fixed(cx, cy + d, GOLD[5])     # a cross inside the curl
    r.fixed(cx, cy, (150, 30, 34))


def glass(r, c, g, slosh=0):
    """a wine glass held by its stem: c = the hand on the stem"""
    x, y = int(c[0]), int(c[1])
    for yy in range(y - 9, y + 3): r.fixed(x, yy, (176, 172, 156) if yy % 3 else (214, 210, 194))
    for dx in (-2, -1, 0, 1, 2): r.fixed(x + dx, y + 3, (196, 192, 176) if dx < 1 else (140, 136, 122))
    bx, by = x, y - 14
    for yy in range(by - 5, by + 6):
        for xx in range(bx - 6, bx + 7):
            d = ((xx - bx) / 5.2) ** 2 + ((yy + 0.5 - by) / 5.6) ** 2
            if d > 1: continue
            lvl = by - 1 + (slosh * (1 if xx > bx else -1) if slosh else 0)
            if yy >= lvl:
                c_ = WINE[4] if yy == lvl else (WINE[3] if xx < bx else WINE[2])
                if yy > by + 3: c_ = WINE[1]
                r.fixed(xx, yy, c_)
            elif d > 0.7:
                r.fixed(xx, yy, (170, 166, 150))
    r.fixed(bx - 4, by - 2, SHINE); r.fixed(bx - 4, by - 1, (214, 210, 194)); r.fixed(bx - 4, by, (190, 140, 140))


def book_open(r, c, w, h, g, tilt=0.0, page=0):
    """an open book held in front of the belly: a dark leather cover framing two bowed parchment pages with lines of
    text, the block of pages showing at the bottom edge, a red ribbon"""
    x, y = c
    hw = w / 2
    def yt(xx): return y - h / 2 - tilt * (xx - x)
    r.poly([(x - hw - 2, yt(x - hw - 2) - 1), (x + hw + 2, yt(x + hw + 2) - 1), (x + hw + 2, yt(x + hw + 2) + h + 3),
            (x - hw - 2, yt(x - hw - 2) + h + 3)], M['leath'], round_=0.3, group=g + 'cover')
    for sx in (-1, 1):
        x0, x1 = (x - hw, x) if sx < 0 else (x, x + hw)
        bow = lambda xx: 1.8 * math.sin(min(1.0, abs(xx - x) / hw) * math.pi)       # the pages bow up off the gutter
        pts = [(x0, yt(x0) - bow(x0)), ((x0 + x1) / 2, yt((x0 + x1) / 2) - bow((x0 + x1) / 2)), (x1, yt(x1) - bow(x1)),
               (x1, yt(x1) + h - bow(x1)), ((x0 + x1) / 2, yt((x0 + x1) / 2) + h - bow((x0 + x1) / 2)), (x0, yt(x0) + h - bow(x0))]
        def lines(xx, yy, x0=x0, x1=x1, sx=sx):
            rel = yy - (yt(xx) - bow(xx))
            if abs(xx + 0.5 - x) < 2 or xx < x0 + 2 or xx > x1 - 3 or rel < 2 or rel > h - 2: return 0.06 if sx < 0 else -0.04
            return -0.45 if (int(rel) % 2 == 1 and h32(xx // 2 + sx * 31, int(rel), 3) % 6) else (0.06 if sx < 0 else -0.04)
        r.poly(pts, Mat(PAGES[:5], 'plain', 0.36), round_=0.5, tilt=-0.5, group=g + 'p%d' % sx, vfun=lines)
    for yy in range(int(yt(x) - 1), int(yt(x) + h + 1)): r.darken(x, yy, 0.28); r.darken(x - 1, yy, 0.1)
    for xx in range(int(x - hw), int(x + hw)):                                      # the page block's edge
        yb = int(yt(xx) + h - (1.8 * math.sin(min(1.0, abs(xx - x) / hw) * math.pi)))
        r.fixed(xx, yb + 1, PAGES[2] if xx % 2 else PAGES[1])
    if page:
        r.poly([(x + hw - 6, yt(x + hw - 6) - 3), (x + hw, yt(x + hw) - 2), (x + hw - 1.5, yt(x + hw) + 4)], M['pages'], lift=0.3, group=g + 'turn')
    for k, (dx, dy) in enumerate(((0, 0), (0, 1), (1, 2), (1, 3), (0, 4))):
        r.fixed(x + dx, yt(x) + h + 1 + dy, (128, 30, 32) if k < 3 else (88, 20, 24))


def emils(pose, P):
    r = Rig(128, 176)
    b = P.get('b', 0)
    hx = EHX
    shL, shR = (hx - 27, 88 - b), (hx + 27, 88 - b)
    if pose == 'welcome':
        crosier(r, (24, 171), (24, 44), 'crosier', crook_dir=1)
    emils_body(r, P, pose)
    # the arms: elbow / wrist per pose (the elbows hang at the sides)
    if pose == 'read':
        n = P.get('nudge', 0)
        elL, wrL = (25, 95 - b), (42, 68 - b - n)
        elR, wrR = (101, 103 - b), (99, 117)
    elif pose == 'toast':
        up = 2 if P.get('raise_') else 0
        elL, wrL = (22, 96 - b), (29, 66 - b - up)
        elR, wrR = (101, 101 - b), (93, 108)
    else:
        elL, wrL = (29, 98 - b), (26, 109)
        bk = P.get('beckon', 0)
        elR, wrR = (99, 102 - b), (107, 104 - b)
    upper_sleeve(r, shL, elL, 'armLu'); upper_sleeve(r, shR, elR, 'armRu')
    if pose == 'toast': crosier(r, (60, 164), (106, 60), 'crosier', crook_dir=-1)
    raisedL = pose in ('read', 'toast')
    if not raisedL: hL = lower_sleeve(r, elL, wrL, 'armL', opening=8.0)
    if pose == 'read': book_open(r, (85, 108), 28, 16, 'book', tilt=0.14, page=P.get('page', 0))
    hR = lower_sleeve(r, elR, wrR, 'armR', opening=8.5)
    mozzetta(r, P)
    emils_head(r, P)
    mitre(r, P)
    if raisedL: hL = lower_sleeve(r, elL, wrL, 'armL', opening=7.5)
    if pose == 'read':
        frog_hand(r, (hL[0] + 2, hL[1] - 3), 'handL', ang=-62, fingers=3, spread=12, ln=4.2, thumb=(3, 0))
        frog_hand(r, (hR[0] - 1, hR[1] - 1), 'handR', ang=200, fingers=3, spread=10, ln=4.0, curl=0.35)
    elif pose == 'toast':
        glass(r, (hL[0] + 1, hL[1] - 4), 'glass', slosh=P.get('slosh', 0))
        frog_hand(r, (hL[0] + 1, hL[1] - 2), 'handL', ang=0, fingers=3, spread=10, ln=3.6, curl=0.85, thumb=(-1, -4))
        frog_hand(r, (hR[0] - 3, hR[1] - 1), 'handR', ang=200, fingers=3, spread=10, ln=3.8, curl=0.85)
    else:
        frog_hand(r, (hL[0] - 1, hL[1] + 1), 'handL', ang=-10, fingers=3, spread=10, ln=3.6, curl=0.85)
        frog_hand(r, (hR[0] + 1, hR[1] - 1), 'handR', ang=-25 - bk * 12, fingers=4, spread=16, ln=4.6,
                  curl=[0, 0.55, 0.3][bk], thumb=(0, -4.5))
    return warm_ink(r.render())


def emils_frames():
    out = []
    for pose in ('read', 'toast', 'welcome'):
        out += [emils(pose, P) for P in EMILS_POSE[pose]]
    return out


# ======================================================================================================================
# the lizard folk: a shared 3/4 head (snout to the viewer's right) or a frontal one, clawed hands and feet, tails
# ======================================================================================================================
CLAW = R('#2a2418 #4a4232 #7a6e52 #a89a78 #c8bc98')
HORN = R('#2a1a0c #46301a #64482a #82623a #9e7c4c #b8965e')


def scale_v(x, y, u, w):
    return _scales(x, y) * 1.3 + (rig.nM(x * 1.5, y * 1.5) - 0.5) * 0.08


def lizard_eye(r, ex, ey, rx, ry, eye, look=(0, 0), lid=0.25, blink=False, low=0.0, skin=None, brow=0):
    """a round reptile eye: coloured iris, a big pupil, a glint; `lid` = how far the upper lid comes down (0..1),
    `low` = how far the lower lid comes up (a smile), `brow` = -1 worried (inner end up) / +1 angry (inner end down)"""
    skin = skin or LIZ
    x0, x1 = int(math.floor(ex - rx)), int(math.ceil(ex + rx))
    y0, y1 = int(math.floor(ey - ry)), int(math.ceil(ey + ry))
    top = ey - ry + 2 * ry * (1.0 if blink else lid)
    bot = ey + ry - 2 * ry * low
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = ((x + 0.5 - ex) / rx) ** 2 + ((y + 0.5 - ey) / ry) ** 2
            if d > 1: continue
            if y + 0.5 < top or y + 0.5 > bot:
                r.fixed(x, y, skin[5] if y + 0.5 < top and y + 0.5 > top - 1.5 else skin[3]); continue
            c = eye[1] if d > 0.72 else (eye[3] if y + 0.5 < ey else eye[2])
            if y + 0.5 > ey + ry * 0.4 and d <= 0.72: c = eye[4] if len(eye) > 4 else eye[3]   # light pools in the lower iris
            r.fixed(x, y, c)
    if not blink:
        px_, py_ = ex + look[0] * rx * 0.25, ey + look[1] * ry * 0.2
        pr = min(rx, ry) * 0.5
        for y in range(int(py_ - pr) - 1, int(py_ + pr) + 2):
            for x in range(int(px_ - pr) - 1, int(px_ + pr) + 2):
                if ((x + 0.5 - px_) ** 2 + (y + 0.5 - py_) ** 2) <= pr * pr and top <= y + 0.5 <= bot:
                    r.fixed(x, y, PUPIL)
        gx, gy = int(ex - rx * 0.4), int(max(top + 0.5, ey - ry * 0.45))
        r.fixed(gx, gy, SHINE)
        if rx > 3: r.fixed(gx + 1, gy, mix(SHINE, eye[3], 0.4))
    for x in range(x0, x1 + 1):                                                    # the lid's dark edge
        dx = (x + 0.5 - ex) / rx
        if abs(dx) > 1: continue
        yt = top + brow * dx * 0.0
        if y0 <= yt <= y1 + 1 and not blink:
            r.fixed(x, int(yt), skin[0] if abs(dx) < 0.85 else skin[1])
        if blink: r.fixed(x, int(ey + ry * 0.2), skin[0])
    if brow:                                                                        # a brow ridge over it
        for x in range(x0 - 1, x1 + 2):
            dx = (x + 0.5 - ex) / rx
            y = ey - ry - 1.2 - brow * dx * ry * 0.35 * (1 if ex > 0 else 1)
            r.fixed(x, int(y), skin[6]); r.fixed(x, int(y) + 1, skin[2])


def lizard_head(r, hx, hy, P, skin, belly, eye, s=1.0, snout=9.0, expr='neutral', front=False, teeth=False, gid='head'):
    """a reptile head; 3/4 to the viewer's right unless `front`. (hx, hy) = the cranium's middle. Returns a dict of
    useful points (eye centres, chin)"""
    b = P.get('b', 0)
    hy = hy - b
    look = P.get('look', (0, 0))
    blink = P.get('blink', False)
    lid = {'neutral': 0.22, 'worried': 0.12, 'narrow': 0.48, 'warm': 0.2, 'angry': 0.32, 'smug': 0.4}[expr]
    low = {'warm': 0.25, 'smug': 0.15}.get(expr, 0.0)
    brow = {'worried': -1, 'angry': 1, 'narrow': 1}.get(expr, 0)
    pts = {}
    if not front:
        banded(r, hx, hy, 10.5 * s, 9.5 * s, skin, gid, lo=1, vfun=scale_v, flat=0.95)
        mt = lambda x: hy + 6.4 * s + (x - hx) * 0.06 - (1.2 * s if (expr in ('warm', 'smug') and x < hx - 1 * s) else 0)
        banded(r, hx + 7.5 * s, hy + 3.6 * s, snout * s, 5.6 * s, skin, gid + 'snout', lo=1, vfun=scale_v, flat=0.92,
               clip=lambda x, y: y <= mt(x) + 0.5)
        banded(r, hx + 6.0 * s, hy + 7.4 * s, (snout - 1.2) * s, 3.6 * s, belly, gid + 'jaw', lo=1, hi=len(belly) - 2,
               vfun=lambda x, y, u, w: (rig.nM(x * 2, y * 2) - 0.5) * 0.1, clip=lambda x, y: y > mt(x) - 0.5)
        tip = hx + 7.5 * s + snout * s
        for x in range(int(hx - 3 * s), int(tip - 0.5)):                             # the mouth line
            r.fixed(x, int(mt(x)), (28, 22, 14))
            r.fixed(x, int(mt(x)) - 1, skin[2]) if x > hx else None
        cx = int(hx - 3 * s)
        if expr in ('warm', 'smug'): r.fixed(cx - 1, int(mt(cx)) - 1, (28, 22, 14))
        if teeth:
            for x in range(int(hx + 1 * s), int(tip - 2), 3): r.fixed(x, int(mt(x)) + 1, (200, 190, 160)); r.fixed(x, int(mt(x)) - 1, (176, 166, 138))
        r.fixed(int(tip - 2.5), int(hy + 1.2 * s), skin[0]); r.fixed(int(tip - 3.5), int(hy + 1.2 * s), skin[1])   # a nostril
        near = (hx - 2.2 * s, hy - 1.0 * s)
        far = (hx + 6.4 * s, hy - 1.6 * s)
        lizard_eye(r, far[0], far[1], 2.4 * s, 3.5 * s, eye, look=look, lid=lid, blink=blink, low=low, skin=skin, brow=brow)
        lizard_eye(r, near[0], near[1], 3.9 * s, 4.3 * s, eye, look=look, lid=lid, blink=blink, low=low, skin=skin, brow=brow)
        pts.update(near=near, far=far, chin=(hx + 4 * s, hy + 10 * s), tip=(tip, hy + 3 * s), mouth=lambda x: mt(x))
    else:
        banded(r, hx, hy, 11.0 * s, 10.0 * s, skin, gid, lo=1, vfun=scale_v, flat=0.95)
        mt = lambda x: hy + 7.2 * s + (abs(x + 0.5 - hx) / (snout * s)) ** 2 * 0.8 - (1.0 * s if expr in ('warm', 'smug') and abs(x + 0.5 - hx) > snout * s * 0.75 else 0)
        banded(r, hx, hy + 4.8 * s, snout * s, 5.0 * s, skin, gid + 'snout', lo=1, vfun=scale_v, flat=0.9,
               clip=lambda x, y: y <= mt(x) + 0.5, L=(-0.4, -0.5, 0.75))
        banded(r, hx, hy + 8.4 * s, (snout - 1.0) * s, 3.4 * s, belly, gid + 'jaw', lo=1, hi=len(belly) - 2,
               vfun=lambda x, y, u, w: (rig.nM(x * 2, y * 2) - 0.5) * 0.1, clip=lambda x, y: y > mt(x) - 0.5)
        for x in range(int(hx - snout * s + 1), int(hx + snout * s)):
            r.fixed(x, int(mt(x)), (28, 22, 14))
        if teeth:
            for x in range(int(hx - snout * s + 3), int(hx + snout * s - 2), 3): r.fixed(x, int(mt(x)) - 1, (200, 190, 160))
        for sx in (-1, 1): r.fixed(int(hx + sx * 2 * s - (1 if sx < 0 else 0)), int(hy + 2.6 * s), skin[0])
        for i, sx in enumerate((-1, 1)):
            e = (hx + sx * 5.2 * s, hy - 1.2 * s)
            lizard_eye(r, e[0], e[1], 3.6 * s, 4.0 * s, eye, look=look, lid=lid, blink=blink, low=low, skin=skin,
                       brow=brow * sx if brow else 0)
            pts['e%d' % i] = e
        pts.update(chin=(hx, hy + 11 * s), mouth=lambda x: mt(x))
    return pts


def claw_hand(r, c, mat, g, ang, fingers=3, spread=16, ln=4.0, curl=0.0, size=1.2, thumb=None, claws=True):
    hand(r, c, mat, g, fingers=fingers, ang=ang, spread=spread, ln=ln, curl=curl, size=size, thumb=thumb,
         claw=CLAW if claws and curl < 0.5 else None)


def lizard_foot(r, x, y, mat, g, sx=1, toes=3, w=1.0):
    """a clawed foot planted on the ground line y, toes splayed to the front"""
    r.ellipsoid(x, y - 2.0, 5.6 * w, 2.8, mat, group=g)
    for k in range(toes):
        dx = (k - (toes - 1) / 2) * 3.6 * w + sx * 0.6
        r.tube((x + dx * 0.45, y - 1.6), (x + dx * 1.1, y + 0.2), 1.5, 1.2, mat, group=g + 't%d' % k)
        seam(r, g + 't%d' % k, 0.15)
        r.fixed(x + dx * 1.1 + (1 if dx > 0.5 else -1 if dx < -0.5 else 0), y + 0.4, CLAW[3])
        r.fixed(x + dx * 1.1 + (1 if dx > 0.5 else -1 if dx < -0.5 else 0), y + 1.0, CLAW[1])


def lizard_tail(r, base, pts, r0, mat, g, r1=1.2, belly=None):
    """a tail out from behind the body, along pts; a pale underside stripe when `belly`"""
    pts = [base] + pts
    n = len(pts) - 1
    for i in range(n):
        ra = r0 + (r1 - r0) * i / n
        rb = r0 + (r1 - r0) * (i + 1) / n
        r.tube(pts[i], pts[i + 1], ra, rb, mat, group=g,
               folds=lambda u, sd: (0.18 if sd > 0.5 else 0) + (-0.1 if int(u * 5) % 2 else 0))


def shade_under(r, ycut, groups, col, t, fade=7.0):
    """darken fixed pixels of `groups` above row ycut (a hood's / hat brim's shadow on the brow), fading over `fade` rows"""
    for (x, y), e in r.buf.items():
        if e[3] is None or r.groups[e[2]] not in groups or y >= ycut: continue
        e[3] = mix(e[3], col, min(1.0, t * (ycut - y) / fade + t * 0.3))


def tail_scutes(r, pts, mat, g, h0=3.4, h1=1.2, every=5.0):
    """a crocodile's ridge: small triangular scutes along the upper side of a tail path (drawn before the tail)"""
    segs = list(zip(pts, pts[1:]))
    total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs)
    d, k = every * 0.6, 0
    while d < total - 2:
        acc = 0
        for (a, b) in segs:
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            if acc + L >= d:
                t = (d - acc) / L
                x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
                nx, ny = uy, -ux
                if ny > 0: nx, ny = -nx, -ny
                h = h0 + (h1 - h0) * d / total
                r.poly([(x - ux * 2.2, y - uy * 2.2), (x + ux * 2.2, y + uy * 2.2), (x + nx * (h + 3.2), y + ny * (h + 3.2))], mat, round_=0.5,
                       group=g + 'sc%d' % k)
                break
            acc += L
        d += every; k += 1


def knee_swell(r, groups, cx, cy, rx, ry, dv=0.13):
    """the free leg's knee pushing the cloth forward: a lit swell, the cloth falling away below it (tone only)"""
    for (x, y), e in r.buf.items():
        if e[0] is None or r.groups[e[2]] not in groups: continue
        d = ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2
        if d < 1: e[1] += dv * (1 - d) * (1 if y < cy + 2 else -0.7)


def hood(r, hx, hy, rx, ry, mat, inner, g, horn=None, b=0):
    """a deep hood behind the head: the cowl, its shadowed inside; optionally a horn pushed through it"""
    r.ellipsoid(hx, hy - b, rx, ry, mat, group=g, flat=0.9, vfun=lambda x, y, u, w: -0.16 if (abs(u + 0.15) < 0.06 and w < -0.2) else 0)
    banded(r, hx + rx * 0.16, hy + ry * 0.12 - b, rx * 0.78, ry * 0.8, inner, g + 'in', lo=0, hi=2,
           L=(0.4, 0.6, 0.6), amb=0.0)
    if horn:
        (x0, y0), (x1, y1) = horn
        r.tube((x0, y0 - b), (x1, y1 - b), 2.6, 0.9, Mat(HORN, 'plain', 0.3, 0.3), group=g + 'horn',
               folds=lambda u, sd: -0.14 if int(u * 6) % 2 else 0)


# ======================================================================================================================
# Brother Pim -- the young novice: brown habit, cream capelet, a horn through the hood, a book, a wooden cross
# ======================================================================================================================
EYE_H = R('#1e140a #3a2812 #5c4020 #7e5a2c #a07a3e')
PIM_POSE = [dict(), dict(b=1), dict(blink=True), dict(look=(0, -1)), dict(look=(0, -1), tap=1), dict(flick=1),
            dict(gulp=1), dict(b=1, flick=2)]


def habit_sleeve(r, sh, el, wr, mat, g, cuff=4.6):
    r.tube(sh, el, 5.2, 4.8, mat, group=g, folds=lambda u, sd: (-0.2 if u > 0.82 and abs(sd) < 0.5 else 0))
    r.tube(el, wr, 4.8, cuff, mat, group=g, folds=lambda u, sd: (-0.18 if 0.5 < u < 0.56 and abs(sd) < 0.7 else 0) + (0.08 if sd < -0.5 else 0))
    seam(r, g, 0.22)
    dx, dy = wr[0] - el[0], wr[1] - el[1]; L = math.hypot(dx, dy) or 1
    return (wr[0] + dx / L * 2.2, wr[1] + dy / L * 2.2)


def pim(P):
    r = Rig(128, 128)
    b = P.get('b', 0)
    fl = P.get('flick', 0)
    tip = [(16, 102), (13, 99), (18, 100)][fl]
    lizard_tail(r, (52, 112), [(40, 118), (28, 120), (19, 116), (15, 109), tip], 4.6, M['liz'], 'tail', r1=1.0, belly=True)
    lizard_foot(r, 54, 125, M['liz'], 'footL', sx=-1)
    lizard_foot(r, 71, 125, M['liz'], 'footR', sx=1)
    def habit_v(x, y):
        t = (y - 62) / 60.0
        v = 0.08 * math.sin((x + 0.5 - 62) / (5 + t * 3) * math.pi + 1.0) * min(1.0, t * 3)
        return v - (0.1 if y > 119 else 0)
    r.poly([(48, 62 - b), (76, 62 - b), (80, 80), (83, 104), (86, 121), (74, 123), (62, 122.5), (50, 123), (38, 121), (41, 104), (44, 80)],
           M['habit'], round_=0.8, group='habit', vfun=habit_v)
    for x in range(38, 87): r.darken(x, 123, 0.12)
    knee_swell(r, ('habit',), 73, 106, 6.0, 10.0)
    # the rope belt, its knotted ends, a leather pouch on the right hip
    r.poly([(43, 90), (81, 90), (81.5, 93), (42.5, 93)], M['rope'], round_=0.9, group='belt', vfun=lambda x, y: -0.16 if (x + y) % 3 == 0 else 0)
    r.tube((55, 92), (53, 108), 1.3, 1.2, M['rope'], group='ropeend', folds=lambda u, sd: -0.15 if int(u * 8) % 2 else 0)
    for (x, y) in ((54.5, 100), (53, 108)): r.ellipsoid(x, y, 1.9, 1.6, M['rope'], group='knot')
    r.poly([(74, 93), (84, 93), (85, 104), (82, 107), (75, 106), (73, 102)], M['leath'], round_=0.7, group='pouch')
    r.poly([(73.5, 93), (84.5, 93), (84, 97), (74, 97)], M['leath'], lift=0.12, round_=0.5, group='pouchflap')
    r.fixed(79, 96, GOLD[3]); r.fixed(79, 97, GOLD[1])
    # the left arm (viewer's left) holds the open book against the belly
    shL = (48, 66 - b)
    wr = habit_sleeve(r, shL, (42, 84), (47, 95), M['habit'], 'armL', cuff=5.0)
    book_open(r, (55, 89), 22, 12, 'book', tilt=-0.12, page=0)
    claw_hand(r, (wr[0] + 1, wr[1] + 1), M['liz'], 'handL', ang=-20, fingers=3, spread=12, ln=3.2, curl=0.5)
    # the cream capelet over the shoulders, a wooden cross on a cord
    def hemc(x): return 79 - b - 3.5 * ((x - 62) / 22.0) ** 2
    cap = [(52, 56 - b), (72, 56 - b), (79, 62 - b), (84, 72 - b)] + [(x, hemc(x)) for x in range(84, 39, -4)] + [(40, 72 - b), (45, 62 - b)]
    r.poly(cap, M['cape'], round_=0.85, tilt=-0.1, group='capelet',
           vfun=lambda x, y: (-0.14 if abs((x + 0.5 - 62) % 9 - 4.5) < 0.7 and y > 64 else 0) + (-0.1 if y > hemc(x) - 2 else 0))
    seam(r, 'capelet', 0.2)
    for k in range(10): r.fixed(57 + k * 0.5, 58 - b + k * 1.6, CAPE[0]); r.fixed(67 - k * 0.5, 58 - b + k * 1.6, CAPE[0])   # the cord
    cross(r, 61, 72 - b, h=10, w=8, t=2, ramp_=WOOD)
    # the hood, the head (worried), a horn through the hood
    hood(r, 54, 44, 15.0, 17.0, M['habit'], HABIT, 'hood', horn=((45, 31), (40, 21)), b=b)
    g = P.get('gulp', 0)
    hd = lizard_head(r, 54, 46, P, LIZ, BELLY, EYE_H, s=1.15, snout=9.6, expr='worried')
    shade_under(r, 41 - b, ('head', 'headsnout'), HABIT[1], 0.5)
    if g:
        for x in range(58, 64): r.darken(x, 58 - b, 0.0); tint(r, x, 57 - b, BELLY[3], 0.4)
    # the right arm: up to the chin, the elbow hanging at his side
    t = P.get('tap', 0)
    shR = (76, 66 - b)
    wr = habit_sleeve(r, shR, (82, 86 - b), (70, 70 - b - t), M['habit'], 'armR', cuff=4.4)
    claw_hand(r, (wr[0] - 1, wr[1] - 2), M['liz'], 'handR', ang=-122, fingers=3, spread=12, ln=3.8, curl=0.3, thumb=(-3, 2), size=1.35)
    return warm_ink(r.render())


def pim_frames(): return [pim(P) for P in PIM_POSE]


# ======================================================================================================================
# Inquisitor Vesper Tann -- a tall hooded lizard in black-brown with a red lining, a candle-crowned staff, a book
# ======================================================================================================================
VESPER_POSE = [dict(fl=0), dict(b=1, fl=1), dict(fl=2), dict(blink=True, fl=0), dict(look=(-1, 0), fl=1),
               dict(look=(-1, 0), fl=2), dict(swing=1, fl=0), dict(b=1, swing=2, fl=1)]
HOURG = [(70, 56, 30), (120, 96, 52), (176, 150, 96), (214, 196, 150)]


def candle(r, x, y, fl):
    """a stub of candle standing on (x, y) with a flickering flame"""
    for yy in range(y - 9, y + 1):
        for xx in range(x - 1, x + 2):
            r.fixed(xx, yy, PAGES[4] if xx == x - 1 else PAGES[3] if xx == x else PAGES[1])
    r.fixed(x + 1, y - 6, PAGES[4]); r.fixed(x + 1, y - 5, PAGES[3])                     # a drip
    h = [6, 7, 5][fl]
    lean = [0, 1, -1][fl]
    for k in range(h):
        t = k / max(1, h - 1)
        xx = x + (lean if t > 0.5 else 0)
        c = FLAME[4] if t < 0.35 else FLAME[3] if t < 0.65 else FLAME[2]
        r.fixed(xx, y - 10 - k, c)
        if t < 0.55: r.fixed(xx - 1, y - 10 - k, FLAME[2]); r.fixed(xx + 1, y - 10 - k, FLAME[1])
    r.fixed(x, y - 10, (40, 30, 20))


def inq_staff(r, x, top, bottom, P):
    """the inquisitor's staff: an iron shaft, a cross-shaped finial with a red stone, a candle on top, two chains with
    little censers hanging from the arms"""
    r.tube((x, bottom), (x, top + 8), 1.4, 1.6, M['iron'], group='staff')
    for y in range(top + 30, bottom, 22): r.tube((x, y), (x, y + 2), 2.2, 2.2, M['iron'], lift=0.1, group='staffring')
    cy = top + 6
    r.tube((x - 8, cy), (x + 8, cy), 1.6, 1.6, M['iron'], group='finial')
    r.tube((x, cy - 7), (x, cy + 9), 1.8, 1.6, M['iron'], group='finial')
    for (ex, ey) in ((x - 9, cy), (x + 9, cy), (x, cy - 8), (x, cy + 10)):
        r.ellipsoid(ex, ey, 1.8, 1.8, M['iron'], lift=0.15, group='finial')
    r.ellipsoid(x, cy, 3.0, 3.0, M['iron'], lift=0.1, group='boss')
    for (dx, dy, c) in ((-1, -1, (176, 52, 44)), (0, -1, (140, 30, 30)), (-1, 0, (120, 24, 26)), (0, 0, (88, 16, 20))):
        r.fixed(x + dx, cy + dy, c)
    r.fixed(x - 1, cy - 1, (220, 120, 100))
    candle(r, x, cy - 8, P.get('fl', 0))
    sw = [0, 2, -1][P.get('swing', 0)]
    for (sx, ln) in ((-1, 16), (1, 20)):                                             # chains + censers
        x0, y0 = x + sx * 9, cy + 2
        x1, y1 = x0 + sw * (1 if sx < 0 else 0.6), y0 + ln
        for k in range(ln):
            t = k / ln
            r.fixed(x0 + (x1 - x0) * t, y0 + k, IRON[5] if k % 2 else IRON[2])
        r.ellipsoid(x1, y1 + 2.5, 2.4, 2.6, M['iron'], lift=0.05, group='censer%d' % sx)
        r.fixed(x1, y1 + 5.5, IRON[2]); r.fixed(x1, y1 + 6.5, IRON[1])


def vesper(P):
    r = Rig(128, 176)
    b = P.get('b', 0)
    hx = 66
    lizard_tail(r, (54, 160), [(42, 166), (30, 167), (21, 162), (16, 154), (18, 147)], 4.4, M['liz'], 'tail', r1=1.0, belly=True)
    for (fx, sx) in ((58, -1), (76, 1)):
        r.ellipsoid(fx, 168.5, 6.0, 4.0, Mat(DARK, 'leather', 0.24, 0.5), group='boot%d' % sx)
        lizard_foot(r, fx + sx, 172, M['liz'], 'foot%d' % sx, sx=sx, w=0.9)
    # the habit
    def habit_v(x, y):
        t = (y - 70) / 98.0
        return 0.08 * math.sin((x + 0.5 - hx) / (4 + t * 4) * math.pi) * min(1.0, t * 3) - (0.1 if y > 164 else 0)
    r.poly([(54, 66 - b), (78, 66 - b), (82, 110), (86, 168), (66, 169), (46, 168), (50, 110)], M['dark'], round_=0.8, group='habit', vfun=habit_v)
    # the cape: two panels open in front, the red lining along their inner edges, dull gold braid
    fc = hx + 3                                                                      # the front line, turned right
    for sx in (-1, 1):
        o = [(fc + sx * 6, 64 - b), (fc + sx * 10, 70 - b), (fc + sx * 9, 116), (fc + sx * 13, 168)]
        out = [(hx + sx * 33, 166), (hx + sx * 28, 118), (hx + sx * 22, 80 - b), (hx + sx * 15, 64 - b)]
        r.poly(o + out, M['dark'], round_=0.7, group='cape%d' % sx,
               vfun=lambda x, y, sx=sx: 0.09 * math.sin((x + 0.5 - hx) / (5 + (y - 70) / 98 * 5) * math.pi + 0.8) * min(1.0, max(0, (y - 70) / 30)))
        seam(r, 'cape%d' % sx, 0.18)
        lin = [(fc + sx * 9.5, 72 - b), (fc + sx * 8.5, 116), (fc + sx * 12.5, 168), (fc + sx * 15.5, 167), (fc + sx * 11.5, 116), (fc + sx * 11.5, 72 - b)]
        r.poly(lin, M['lining'], round_=0.5, group='lining%d' % sx)
        for (a, c) in zip(o[1:], o[2:]):
            n = int(abs(c[1] - a[1]))
            for k in range(n):
                t = k / n
                xx, yy = a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t
                r.fixed(xx, yy, GOLD[3] if k % 3 else GOLD[4]); r.fixed(xx - sx, yy, GOLD[1])
        for xx in range(int(min(fc + sx * 13, hx + sx * 33)), int(max(fc + sx * 13, hx + sx * 33)) + 1):
            r.fixed(xx, 166 + (1 if abs(xx - hx) < 20 else 0), GOLD[2] if xx % 2 else GOLD[1])
    knee_swell(r, ('cape1', 'habit'), fc + 14, 132, 7.0, 12.0)
    # belt, the hourglass at the hip, a chain
    r.poly([(52, 104), (80, 104), (80.5, 108), (51.5, 108)], M['leath'], round_=0.8, group='belt')
    r.fixed(69, 105, GOLD[4]); r.fixed(70, 105, GOLD[3]); r.fixed(69, 106, GOLD[2]); r.fixed(70, 106, GOLD[1])
    hgx, hgy = 77, 112
    for yy in range(hgy, hgy + 14):
        t = (yy - hgy) / 13
        w = 3.5 * abs(t - 0.5) * 2 + 0.6
        for xx in range(int(hgx - w), int(hgx + w) + 1):
            sand = (t > 0.62 and t < 0.95) or (t > 0.32 and t < 0.5 and abs(xx - hgx) < w - 0.5)
            r.fixed(xx, yy, HOURG[2] if sand and xx < hgx else HOURG[1] if sand else (120, 120, 112) if xx == int(hgx - w) else (64, 64, 60))
    for xx in range(hgx - 4, hgx + 5): r.fixed(xx, hgy - 1, GOLD[3]); r.fixed(xx, hgy + 14, GOLD[2])
    for yy in range(hgy - 1, hgy + 15): r.fixed(hgx - 5, yy, GOLD[2]); r.fixed(hgx + 5, yy, GOLD[1])
    for k in range(10): r.fixed(61 + k * 0.4, 108 + k * 1.4, IRON[5] if k % 2 else IRON[2])
    cross(r, 64, 122, h=8, w=6, t=2, ramp_=IRON)
    # the staff in the left hand
    inq_staff(r, 34, 21, 171, P)
    shL = (54, 70 - b)
    wr = habit_sleeve(r, shL, (46, 90 - b), (38, 101), M['dark'], 'armL', cuff=5.6)
    for k in range(5): r.fixed(wr[0] + 2 - k * 0.2, wr[1] - 4 + k, LINING[3])
    claw_hand(r, (36, 103), M['liz'], 'handL', ang=0, fingers=3, spread=10, ln=3.4, curl=0.85)
    # the hood, the head (narrow, judging), a horn
    hood(r, 63, 45, 15.0, 17.5, M['dark'], DARK, 'hood', horn=((54, 31), (49, 20)), b=b)
    lizard_head(r, 63, 47, P, LIZ, BELLY, EYE_R, s=1.0, snout=10.5, expr='narrow')
    shade_under(r, 42 - b, ('head', 'headsnout'), DARK[1], 0.55)
    cross(r, 68, 80 - b, h=9, w=7, t=2, ramp_=GOLD)
    # the book on the right forearm
    shR = (78, 70 - b)
    wr = habit_sleeve(r, shR, (88, 92 - b), (84, 92), M['dark'], 'armR', cuff=5.6)
    book_open(r, (80, 85), 22, 12, 'book', tilt=0.12)
    claw_hand(r, (wr[0] + 1, wr[1]), M['liz'], 'handR', ang=200, fingers=3, spread=10, ln=3.6, curl=0.3)
    return warm_ink(r.render())


def vesper_frames(): return [vesper(P) for P in VESPER_POSE]


# ======================================================================================================================
# Sister Marigold -- the cook: headscarf, ruffled collar, brown dress, a cream apron with flowers, stirring a pot of stew
# ======================================================================================================================
MARIGOLD_POSE = [dict(st=k, b=(1 if k in (2, 3) else 0)) for k in range(6)] + [dict(st=0, blink=True), dict(st=0, b=1)]
FLOWER = [(150, 82, 40), (186, 112, 52), (110, 120, 60), (80, 92, 46)]


def pot(r, cx, cy, st):
    """an iron pot of orange stew, seen a little from above; a wisp of steam"""
    r.ellipsoid(cx, cy + 2, 15.0, 10.5, M['iron'], group='pot', flat=0.9)
    for sx in (-1, 1):
        r.tube((cx + sx * 14, cy - 5), (cx + sx * 18, cy - 4), 1.4, 1.4, M['iron'], group='pothandle%d' % sx)
        r.tube((cx + sx * 18, cy - 4), (cx + sx * 18, cy + 1), 1.4, 1.4, M['iron'], group='pothandle%d' % sx)
    for yy in range(int(cy - 9), int(cy - 2)):
        for xx in range(int(cx - 16), int(cx + 17)):
            d = ((xx + 0.5 - cx) / 15.2) ** 2 + ((yy + 0.5 - (cy - 5.5)) / 3.6) ** 2
            if d > 1: continue
            if d > 0.62: r.fixed(xx, yy, IRON[6] if yy < cy - 6 else IRON[3])
            else:
                k = 4 if (xx + yy * 2 + st) % 5 == 0 else 3 if xx < cx else 2
                r.fixed(xx, yy, STEW[k])
    for (dx, dy) in ((-5, -6), (3, -5), (7, -6)):
        r.fixed(cx + dx, cy + dy, STEW[5]); r.fixed(cx + dx + 1, cy + dy, (160, 150, 90))   # bits of something in it
    ph = st % 4
    for k in range(7):                                                               # steam
        x = cx - 4 + (ph - 2) * 0.6 + math.sin((k + ph) * 0.9) * 2
        y = cy - 11 - k * 2 - ph * 0.5
        if (k + ph) % 3 != 0: r.fixed(x, y, (148, 140, 126) if k < 4 else (120, 114, 104))


def rolled_sleeve(r, sh, el, wr, g, mat=None, skin=None):
    """a sleeve rolled up past the elbow: cloth to just below the elbow (a fat rolled cuff), then the bare forearm"""
    mat = mat or M['brown']; skin = skin or M['liz']
    dx, dy = wr[0] - el[0], wr[1] - el[1]; L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    r.tube(el, wr, 4.4, 3.2, skin, group=g + 'skin', bulge=lambda u: 0.6 * math.sin(min(1.0, u * 2) * math.pi))
    r.tube(sh, el, 5.6, 5.4, mat, group=g, folds=lambda u, sd: (-0.2 if u > 0.8 and abs(sd) < 0.5 else 0) + (0.08 if sd < -0.5 else 0))
    r.tube(el, (el[0] + ux * 3, el[1] + uy * 3), 6.0, 5.8, mat, lift=0.14, group=g + 'roll',
           folds=lambda u, sd: -0.2 if 0.45 < u < 0.6 else 0)
    seam(r, g, 0.2); seam(r, g + 'roll', 0.2)


def marigold(P):
    r = Rig(128, 160)
    b = P.get('b', 0)
    hx = 62
    lizard_tail(r, (46, 140), [(34, 148), (24, 151), (16, 147), (12, 139), (14, 132)], 5.0, M['liz'], 'tail', r1=1.0, belly=True)
    lizard_foot(r, 56, 156, M['liz'], 'footL', sx=-1, w=1.1)
    lizard_foot(r, 72, 156, M['liz'], 'footR', sx=1, w=1.1)
    def hw(y):
        t = y - (64 - b)
        if t < 14: return 10 + 13 * math.sin(t / 14 * math.pi / 2)
        if t < 54: return 23 + 12 * math.sin((t - 14) / 40 * math.pi / 2)
        return 35 - ((t - 54) / 35.0) ** 2 * 6
    ys = list(range(64 - b, 153))
    r.poly([(hx - hw(y), y) for y in ys] + [(hx + hw(y), y) for y in ys[::-1]], M['brown'], round_=0.85, group='dress',
           vfun=lambda x, y: 0.08 * math.sin((x + 0.5 - hx) / 6 * math.pi) * (1 if y > 118 else 0) - (0.1 if y > 149 else 0))
    for x in range(hx - 33, hx + 34): r.darken(x, 153, 0.15)
    # the keys at her left hip
    for k, (dx, ln) in enumerate(((-1, 9), (1, 7), (3, 10))):
        x0 = 34 + dx
        r.tube((x0, 112), (x0 + dx * 0.4, 112 + ln), 0.9, 0.9, M['iron'], group='key%d' % k)
        r.fixed(x0 + dx * 0.4 + 1, 112 + ln, IRON[5]); r.fixed(x0 + dx * 0.4 + 1, 111 + ln, IRON[3])
    for a in range(16):
        t = a / 16 * 2 * math.pi
        r.fixed(35 + math.cos(t) * 3, 110 + math.sin(t) * 2.2, IRON[6] if math.sin(t) < 0 else IRON[3])
    # the apron: bib + skirt, flowers embroidered along its foot, ties at the waist
    ap = [(hx - 12, 78 - b), (hx + 12, 78 - b), (hx + 14, 98), (hx + 24, 104), (hx + 27, 146), (hx, 148), (hx - 27, 146), (hx - 24, 104), (hx - 14, 98)]
    def apron_v(x, y):
        v = 0.07 * math.sin((x + 0.5 - hx) / 5 * math.pi + 0.5) * (1 if y > 104 else 0)
        return v - (0.1 if 96 <= y <= 98 else 0)
    r.poly(ap, M['apron'], round_=0.8, group='apron', vfun=apron_v)
    seam(r, 'apron', 0.18)
    for (fx, fy) in ((hx - 18, 136), (hx - 9, 140), (hx + 1, 137), (hx + 11, 140), (hx + 19, 136), (hx - 13, 129), (hx + 6, 130)):
        r.fixed(fx, fy, FLOWER[1]); r.fixed(fx + 1, fy, FLOWER[0]); r.fixed(fx, fy - 1, FLOWER[1]); r.fixed(fx - 1, fy, FLOWER[0])
        r.fixed(fx, fy + 1, FLOWER[0]); r.fixed(fx + 1, fy + 2, FLOWER[2]); r.fixed(fx + 2, fy + 1, FLOWER[3]); r.fixed(fx - 2, fy + 2, FLOWER[2])
    for x in range(hx - 25, hx + 26): r.fixed(x, 145 + (1 if abs(x - hx) < 14 else 0), APRON[2] if x % 2 else APRON[1])
    cross(r, hx - 1, 84 - b, h=8, w=6, t=2, ramp_=GOLD)
    for k in range(7): r.fixed(hx - 5 + k * 0.7, 76 - b + k, GOLD[2]); r.fixed(hx + 5 - k * 0.7, 76 - b + k, GOLD[2])
    # the right arm round the pot on her hip
    shR = (hx + 20, 76 - b)
    rolled_sleeve(r, shR, (hx + 31, 96 - b), (hx + 41, 106), 'armR')
    st = P.get('st', 0)
    pot(r, hx + 30, 114, st)
    claw_hand(r, (hx + 45, 108), M['liz'], 'handR', ang=150, fingers=3, spread=10, ln=3.4, curl=0.8, size=1.3)
    # the left arm stirs: the spoon's bowl circles in the stew
    a = st / 6 * 2 * math.pi
    bowl = (hx + 28 + 6 * math.cos(a), 108 + 1.4 * math.sin(a))
    hnd = (hx + 10 + 3 * math.cos(a), 94 + 1.0 * math.sin(a))
    top = (hnd[0] - (bowl[0] - hnd[0]) * 0.55, hnd[1] - (bowl[1] - hnd[1]) * 0.55)
    shL = (hx - 22, 74 - b)
    rolled_sleeve(r, (hx - 20, 76 - b), (hx - 18, 100 - b), (hnd[0] - 4, hnd[1] + 2), 'armL')
    r.tube(top, (bowl[0] - 1, bowl[1] - 1), 1.1, 1.0, M['wood'], group='spoon')
    claw_hand(r, (hnd[0] - 1, hnd[1] + 1), M['liz'], 'handL', ang=-30, fingers=3, spread=10, ln=3.2, curl=0.85, size=1.3)
    # ruffled collar, headscarf, the head (warm)
    r.ellipsoid(hx, 69 - b, 12.0, 4.4, M['scarf'], group='collar', vfun=lambda x, y, u, w: -0.16 if x % 3 == 0 and w > 0 else 0)
    for x in range(hx - 11, hx + 12, 3): r.fixed(x, 73 - b, SCARF[1])
    hood(r, 59, 44, 16.0, 16.0, M['scarf'], SCARF, 'scarf', b=b)
    lizard_head(r, 59, 48, P, LIZ, BELLY, EYE_Y, s=1.15, snout=9.0, expr='warm')
    shade_under(r, 42 - b, ('head', 'headsnout'), SCARF[1], 0.4)
    band = [(44, 40 - b), (52, 33 - b), (62, 31 - b), (71, 33 - b), (75, 38 - b), (72, 39 - b), (62, 35 - b), (52, 37 - b), (46, 43 - b)]
    r.poly(band, M['scarf'], lift=0.12, round_=0.7, group='scarfband', vfun=lambda x, y: -0.14 if (x + y) % 4 == 0 else 0)
    seam(r, 'scarfband', 0.2)
    r.ellipsoid(63, 63 - b, 2.8, 2.2, M['scarf'], lift=-0.08, group='knot')            # the knot under the chin
    r.tube((62, 64 - b), (60, 69 - b), 1.4, 1.1, M['scarf'], lift=-0.1, group='knot2')
    r.tube((64, 64 - b), (67, 68 - b), 1.4, 1.1, M['scarf'], lift=-0.1, group='knot2')
    return warm_ink(r.render())


def marigold_frames(): return [marigold(P) for P in MARIGOLD_POSE]


# ======================================================================================================================
# Cornelius Brack -- a portly crocodile in a top hat and monocle: frock coat, gold waistcoat, coin sack, goblet
# ======================================================================================================================
CORNELIUS_POSE = [dict(), dict(b=1), dict(glint=1), dict(blink=True), dict(swirl=1), dict(sip=1), dict(jingle=1), dict(b=1)]
HAT = R('#140c08 #1e130c #2a1a10 #362215 #432a1a #50331f')


def cornelius(P):
    r = Rig(128, 160)
    b = P.get('b', 0)
    hx = 64
    tp = [(50, 140), (38, 148), (26, 151), (16, 148), (10, 140), (10, 133)]
    tail_scutes(r, tp[1:], M['croc'], 'tailridge', h0=2.6, h1=0.8)
    lizard_tail(r, tp[0], tp[1:], 5.6, M['croc'], 'tail', r1=1.2, belly=True)
    for (x, y, k) in ((30, 156, 0), (36, 157, 1), (42, 156, 2), (34, 154, 1), (88, 157, 0), (94, 156, 2), (47, 157, 1)):   # spilled coins
        r.fixed(x, y, COIN[4 - k % 2]); r.fixed(x + 1, y, COIN[3]); r.fixed(x + 2, y, COIN[2]); r.fixed(x + 1, y - 1, COIN[5])
    stripes = lambda u, sd: (-0.3 if int((sd + 1) * 5) % 2 else 0.04)                 # short striped legs: the left one
    r.tube((hx - 8, 117), (hx - 9, 150), 8.0, 7.0, M['stripe'], group='leg-1', folds=stripes)   # straight under the weight,
    r.tube((hx + 10, 118), (hx + 13, 135), 8.0, 7.4, M['stripe'], group='leg1', folds=stripes)  # the right eased out, knee
    r.tube((hx + 13, 135), (hx + 16, 151), 7.4, 6.8, M['stripe'], group='leg1', folds=stripes)  # a little bent
    lizard_foot(r, hx - 10, 156, M['croc'], 'foot-1', sx=-1, toes=4, w=1.2)
    lizard_foot(r, hx + 18, 157, M['croc'], 'foot1', sx=1, toes=4, w=1.25)
    # spines over the left shoulder (the ridge down the back of the neck)
    for k in range(4):
        x, y = 44 + k * 3, 66 - b - k * 2
        r.poly([(x - 2.5, y + 4), (x + 2.5, y + 4), (x + 0.5, y - 3)], M['croc'], round_=0.6, group='spine%d' % k)
    # the frock coat (behind), the gold waistcoat over the belly, the coat's fronts + lapels
    r.poly([(hx - 22, 66 - b), (hx + 22, 66 - b), (hx + 30, 90), (hx + 31, 128), (hx + 28, 142), (hx - 28, 142), (hx - 31, 128), (hx - 30, 90)],
           M['maroon'], round_=0.8, group='coatback')
    fc = hx + 2                                                                      # the front line, turned right
    def vest_v(x, y):
        return (0.1 if (x * 2 + y) % 7 == 0 else -0.04 if (x * 2 - y) % 7 == 0 else 0)
    r.poly([(fc - 11, 72 - b), (fc + 11, 72 - b), (fc + 21, 92), (fc + 23, 108), (fc + 19, 122), (fc, 126), (fc - 19, 122), (fc - 23, 108), (fc - 21, 92)],
           M['ochre'], round_=0.9, tilt=0.1, group='vest', vfun=vest_v)
    for y in range(84 - b, 122, 7):
        r.fixed(fc - 1, y, GOLD[5]); r.fixed(fc, y, GOLD[3]); r.fixed(fc - 1, y + 1, GOLD[2]); r.fixed(fc, y + 1, GOLD[1])
        if P.get('b'): r.darken(fc - 2, y, 0.2); r.darken(fc + 1, y, 0.2)              # the buttons strain
    for x in range(fc - 1, fc + 18):                                                   # the watch chain
        t = (x - fc) / 18
        r.fixed(x, 96 + 6 * math.sin(t * math.pi), GOLD[5] if x % 2 else GOLD[2])
    r.poly([(fc - 20, 116), (fc + 20, 116), (fc + 19, 120), (fc - 19, 120)], M['leath'], round_=0.9, group='belt')
    for (dx, dy, c) in ((-3, 0, 4), (-2, 0, 5), (-1, 0, 5), (0, 0, 4), (1, 0, 3), (2, 0, 3), (-3, 1, 3), (2, 1, 1), (-3, 2, 3), (2, 2, 1), (-3, 3, 2), (-2, 3, 1), (-1, 3, 1), (0, 3, 1), (1, 3, 1), (2, 3, 1)):
        r.fixed(fc + dx, 116 + dy, GOLD[c])
    for sx in (-1, 1):
        r.poly([(fc + sx * 11, 70 - b), (hx + sx * 22, 66 - b), (hx + sx * 30, 90), (hx + sx * 31, 128), (hx + sx * 28, 142), (fc + sx * 20, 142),
                (fc + sx * 22, 112), (fc + sx * 21, 92)], M['maroon'], round_=0.7, group='coat%d' % sx)
        r.poly([(fc + sx * 11, 70 - b), (fc + sx * 17, 72 - b), (fc + sx * 21, 90), (fc + sx * 18, 86)], M['maroon'], lift=0.12, round_=0.5, group='lapel%d' % sx)
        seam(r, 'coat%d' % sx, 0.2); seam(r, 'lapel%d' % sx, 0.15)
    # the cravat + a cross pin
    r.poly([(fc - 7, 69 - b), (fc + 7, 69 - b), (fc + 5, 74 - b), (fc - 5, 74 - b)], M['lace'], round_=0.8, group='collar')
    for k, (y, w) in enumerate(((75, 5.2), (80, 6.0), (85, 6.4))):                   # a lace jabot, three falls of frills
        r.poly([(fc - w * 0.6, y - 3 - b), (fc + w * 0.6, y - 3 - b), (fc + w, y + 2 - b), (fc - w, y + 2 - b)], M['lace'], round_=0.8,
               tilt=-0.2, group='jabot%d' % k, vfun=lambda x, y: -0.2 if x % 2 == 0 and y % 3 == 2 else 0)
        seam(r, 'jabot%d' % k, 0.2)
    cross(r, fc - 1, 74 - b, h=7, w=5, t=2)
    # the coin sack in the left hand
    j = P.get('jingle', 0)
    shL = (hx - 24, 72 - b)
    habit_sleeve(r, shL, (hx - 31, 94 - b), (hx - 30, 104), M['maroon'], 'armL', cuff=5.0)
    r.ellipsoid(30, 118 + j, 10.5, 11.5, M['sack'], group='sack', vfun=lambda x, y, u, w: -0.16 if (x * 3 + y) % 9 == 0 and w > -0.4 else 0)
    r.tube((31, 106 + j), (31, 108 + j), 3.6, 4.4, M['sack'], group='sackneck')
    r.ellipsoid(31, 105 + j, 4.0, 1.8, M['sack'], lift=0.12, group='sacklip')
    for (dx, c) in ((-2, 5), (0, 4), (2, 5)): r.fixed(31 + dx, 104 + j, COIN[c])
    for k in range(5): r.fixed(26 + k * 2, 108 + j, (60, 44, 24))                       # the drawstring
    claw_hand(r, (hx - 32, 104 + j), M['croc'], 'handL', ang=90, fingers=3, spread=12, ln=3.2, curl=0.9, size=1.3)
    # the head (smug), monocle, top hat
    hd = lizard_head(r, 62, 46, P, CROC, BELLY, EYE_Y, s=1.1, snout=12.0, expr='smug', teeth=True)
    ex, ey = hd['near']
    for a in range(28):
        t = a / 28 * 2 * math.pi
        r.fixed(ex + math.cos(t) * 5.6, ey + math.sin(t) * 5.6, GOLD[5] if math.sin(t) < -0.3 else GOLD[2] if math.cos(t) > 0.2 else GOLD[3])
    if P.get('glint'):
        r.fixed(int(ex) - 2, int(ey) - 3, (255, 250, 230)); r.fixed(int(ex) - 1, int(ey) - 2, (255, 250, 230)); r.fixed(int(ex) - 3, int(ey) - 4, SHINE)
    for k in range(22): r.fixed(ex - 4 + k * 0.15, ey + 6 + k * 1.3, GOLD[2] if k % 2 else GOLD[4])   # the monocle's chain
    hb = 34 - b
    r.ellipsoid(63, hb, 17.0, 3.4, Mat(HAT, 'wool', 0.22, 0.2), group='brim')
    r.poly([(51, hb), (75, hb), (76, hb - 20), (52, hb - 21)], Mat(HAT, 'wool', 0.22, 0.15), round_=0.9, group='crown',
           vfun=lambda x, y: (0.06 if y < hb - 18 else 0))
    for x in range(51, 76):
        for y in range(hb - 6, hb - 1): r.fixed(x, y, MAROON[2] if y > hb - 6 else MAROON[3])
    for (dx, dy) in ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (0, 1), (4, 1), (0, 2), (4, 2), (0, 3), (1, 3), (2, 3), (3, 3), (4, 3)):
        r.fixed(54 + dx, hb - 6 + dy, GOLD[5] if dy == 0 else GOLD[3])
    r.ellipsoid(64, hb - 21, 12.2, 2.0, Mat(HAT, 'wool', 0.3, 0.2), lift=0.1, group='crowntop')
    shade_under(r, hb + 5, ('head', 'headsnout'), CROC[1], 0.35, fade=5)
    # the goblet raised in the right hand
    up = 2 if P.get('sip') else 0
    shR = (hx + 24, 72 - b)
    gh = (hx + 34, 74 - up)
    habit_sleeve(r, shR, (hx + 33, 96 - b), (gh[0] + 1, gh[1] + 6), M['maroon'], 'armR', cuff=5.0)
    gx, gy = gh[0], gh[1] - 10
    for yy in range(gy - 5, gy + 3):
        for xx in range(gx - 5, gx + 6):
            d = ((xx - gx) / 5.0) ** 2 + ((yy + 0.5 - (gy - 2)) / 4.6) ** 2
            if d > 1 or yy < gy - 5: continue
            r.fixed(xx, yy, GOLD[5] if xx < gx - 2 else GOLD[3] if xx < gx + 2 else GOLD[1])
    for xx in range(gx - 4, gx + 5): r.fixed(xx, gy - 5 + (P.get('swirl', 0) if xx > gx else 0), WINE[3] if xx < gx else WINE[2])
    for yy in range(gy + 3, gy + 9): r.fixed(gx, yy, GOLD[4]); r.fixed(gx + 1, yy, GOLD[2])
    for xx in range(gx - 3, gx + 4): r.fixed(xx, gy + 9, GOLD[3])
    r.fixed(gx - 1, gy, (150, 30, 34))
    claw_hand(r, (gh[0], gh[1] - 2), M['croc'], 'handR', ang=180, fingers=3, spread=10, ln=3.0, curl=0.9, size=1.3)
    return warm_ink(r.render())


def cornelius_frames(): return [cornelius(P) for P in CORNELIUS_POSE]


# ======================================================================================================================
# Wren -- a small lizard in a cream hooded shawl, a letter and a quill; keys, a pouch, a vial at her belt
# ======================================================================================================================
WREN_POSE = [dict(), dict(b=1), dict(blink=True), dict(write=1), dict(write=2), dict(look=(0, -1)), dict(look=(0, -1), blink=True), dict(b=1)]


def wren(P):
    """3/4 to the viewer's right, her weight on the left leg: that hip up, that shoulder down, the right knee eased forward
    under the robe, the right foot turned out; the shawl hangs longer on the near side"""
    r = Rig(128, 144)
    b = P.get('b', 0)
    hx = 62
    fc = hx + 3                                                                      # the front line, turned right
    lizard_tail(r, (48, 128), [(36, 134), (26, 136), (18, 132), (14, 124), (16, 118)], 4.2, M['liz'], 'tail', r1=1.0, belly=True)
    lizard_foot(r, 56, 140, M['liz'], 'footL', sx=-1)
    lizard_foot(r, 73, 141, M['liz'], 'footR', sx=1, w=1.05)
    shLy, shRy = 68 - b, 65 - b
    robe = [(47, shLy), (77, shRy), (81, 96), (84, 116), (86, 134), (76, 137), (62, 137.5), (41, 138), (42, 112), (43, 96)]
    def robe_v(x, y):
        v = 0.08 * math.sin((x + 0.5 - fc) / 5 * math.pi + 0.4) * (1 if y > 98 else 0) - (0.1 if y > 134 else 0)
        d = ((x + 0.5 - 76) / 6.0) ** 2 + ((y + 0.5 - 116) / 9.0) ** 2                  # the eased right knee
        if d < 1: v += 0.14 * (1 - d) * (1 if y < 118 else -0.7)
        if 41 < x < 47 and y > 100: v -= 0.06                                          # the straight weight leg's shadowed side
        return v
    r.poly(robe, M['brown'], round_=0.8, group='robe', vfun=robe_v)
    for x in range(41, 87): r.darken(x, 138 if x < 62 else 137, 0.12)
    # the belt rides high on the weight-bearing hip; the rag apron hangs from it
    bl, br = 89, 92
    belt_y = lambda x: bl + (br - bl) * (x - 41) / 42.0
    rag = [(fc - 12, belt_y(fc - 12) + 2), (fc + 11, belt_y(fc + 11) + 2), (fc + 14, 126)] + \
          [(fc + 14 - k * 2.8, 126 + (4 if k % 2 else 0) + (h32(k, 4) % 3)) for k in range(11)] + [(fc - 15, 127)]
    r.poly(rag, M['apron'], round_=0.7, group='rag', vfun=lambda x, y: (-0.12 if (x * 3 + y * 5) % 11 == 0 else 0) + (-0.1 if (rig.nM(x * 2, y * 2) > 0.62) else 0))
    seam(r, 'rag', 0.16)
    r.poly([(41, belt_y(41)), (83, belt_y(83)), (83.5, belt_y(83) + 4), (40.5, belt_y(41) + 4)], M['leath'], round_=0.8, group='belt')
    r.poly([(38, 94), (47, 94), (48, 103), (45, 106), (39, 105), (37, 101)], M['leath'], round_=0.7, group='pouch')
    r.poly([(37.5, 94), (47.5, 94), (47, 98), (38, 98)], M['leath'], lift=0.12, round_=0.5, group='pouchflap')
    for k, (dx, ln) in enumerate(((0, 7), (2, 9))):
        r.tube((52 + dx, 96), (52 + dx * 1.3, 96 + ln), 0.8, 0.8, M['iron'], group='key%d' % k)
        r.fixed(53 + dx * 1.3, 96 + ln, IRON[5])
    for a in range(12):
        t = a / 12 * 2 * math.pi
        r.fixed(53 + math.cos(t) * 2.2, 95 + math.sin(t) * 1.8, IRON[6] if math.sin(t) < 0 else IRON[3])
    for yy in range(99, 107):                                                         # a vial of something dark
        for xx in range(78, 81):
            r.fixed(xx, yy, (70, 92, 90) if yy < 101 else (30, 26, 40) if xx > 78 else (60, 56, 80))
    r.fixed(79, 98, LEATH[4]); r.fixed(80, 98, LEATH[3]); r.fixed(78, 101, (160, 180, 176))
    w = P.get('write', 0)
    elL, elR = (45, 88 - b), (81, 86 - b)
    r.tube((49, shLy + 2), elL, 5.2, 4.8, M['brown'], group='armLu')
    r.tube((76, shRy + 3), elR, 5.2, 4.8, M['brown'], group='armRu')
    # the shawl: over head and shoulders, longer and fuller on the near (left) side, ragged edges
    def shawl_v(x, y): return (-0.12 if abs((x + 0.5 - fc) % 8 - 4) < 0.7 and y > 72 else 0) + (rig.nM(x * 2, y * 2) - 0.5) * 0.1
    sh = [(50, shLy - 10), (74, shRy - 9), (83, shRy + 2), (87, 84)] + [(87 - k * 2.4, 89 + (h32(k, 7) % 4)) for k in range(5)] + \
         [(fc + 9, 86), (fc + 4, 78), (fc - 4, 78), (fc - 8, 88)] + [(fc - 9 - k * 2.6, 94 + k * 0.8 + (h32(k, 8) % 4)) for k in range(6)] + [(35, 96), (37, shLy + 4)]
    r.poly(sh, M['scarf'], round_=0.8, group='shawl', vfun=shawl_v)
    seam(r, 'shawl', 0.2)
    # the head, 3/4, soft and worried, in the shawl's hood
    hood(r, 59, 44, 15.0, 16.5, M['scarf'], SCARF, 'hood', b=b)
    hd = lizard_head(r, 59, 47, P, LIZ, BELLY, EYE_B, s=1.05, snout=8.0, expr='worried')
    shade_under(r, 40 - b, ('head', 'headsnout'), SCARF[1], 0.45)
    for (cx, cy) in ((56, 52), (68, 52)):                                            # a faint blush
        for dx in range(-1, 2): tint(r, cx + dx, cy - b, (160, 86, 70), 0.3)
    for k in range(9):                                                                # the shawl's edge crossing under the chin
        r.fixed(49 + k * 1.7, 59 - b + (k * 0.5), SCARF[1]); r.fixed(49 + k * 1.7, 60 - b + (k * 0.5), SCARF[4])
    # hands at the chest, elbows in at her sides: the letter in the left, the quill writing in the right
    r.tube(elL, (55, 82), 4.8, 4.6, M['brown'], group='armL'); seam(r, 'armL', 0.22)
    wl = (57, 82)
    lp = [(56, 67), (70, 66), (71, 84), (57, 85)]
    r.poly(lp, Mat(PAGES[:5], 'plain', 0.4), round_=0.4, tilt=-0.3, group='letter',
           vfun=lambda x, y: -0.4 if (y - 67 - (x - 56) * -0.07) % 3 < 1 and 57 < x < 69 and h32(x // 2, y, 5) % 5 else 0)
    seam(r, 'letter', 0.3)
    claw_hand(r, (wl[0] + 1, wl[1] - 1), M['liz'], 'handL', ang=-20, fingers=3, spread=10, ln=3.0, curl=0.8, size=1.2)
    r.tube(elR, (73, 80 - w * 0.5), 4.8, 4.6, M['brown'], group='armR'); seam(r, 'armR', 0.22)
    wr = (71, 79 - w * 0.5)
    qx, qy = wr[0] - 3 + [0, -1, 1][w], wr[1] - 2
    for k in range(16):                                                               # the quill: a pale feather, a dark nib
        x, y = qx + k * 0.55, qy - k * 1.0
        r.fixed(x, y, (60, 50, 40) if k < 3 else (196, 190, 172) if k % 2 else (168, 160, 140))
        if k > 4: r.fixed(x + 1, y, (150, 144, 126) if k % 2 else (120, 114, 100))
    claw_hand(r, (wr[0] - 1, wr[1] - 1), M['liz'], 'handR', ang=200, fingers=3, spread=10, ln=3.0, curl=0.8, size=1.2)
    return warm_ink(r.render())


def wren_frames(): return [wren(P) for P in WREN_POSE]


# ======================================================================================================================
# Gallow -- the butcher: a burly crocodile, chef's toque, bloodied apron, a cleaver, a slab of meat + sausages
# ======================================================================================================================
GALLOW_POSE = [dict(), dict(b=1), dict(tap=1), dict(tap=2), dict(blink=True), dict(look=(1, 0)), dict(sway=1), dict(b=1, sway=2)]


def gallow(P):
    r = Rig(128, 176)
    b = P.get('b', 0)
    hx = 64
    tp = [(48, 156), (36, 162), (24, 164), (15, 159), (11, 151), (12, 144)]
    tail_scutes(r, tp[1:], M['croc'], 'tailridge', h0=3.0, h1=0.8)
    lizard_tail(r, tp[0], tp[1:], 6.0, M['croc'], 'tail', r1=1.2, belly=True)
    for sx in (-1, 1):                                                               # the weight on the left leg, the right
        top, ft = (hx + sx * 11, 124), ((hx - 10, 162) if sx < 0 else (hx + 16, 163))  # one set out, its foot turned
        r.tube(top, ft, 9.5, 8.4, M['brown'], group='leg%d' % sx,
               folds=lambda u, sd: (-0.22 if abs(sd) < 0.12 and u > 0.3 else 0) + (-0.12 if 0.5 < u < 0.54 else 0))
        r.tube(ft, (ft[0], ft[1] + 3), 9.2, 9.2, M['brown'], lift=0.12, group='cuff%d' % sx)
        seam(r, 'cuff%d' % sx, 0.2)
        lizard_foot(r, ft[0] + sx * 1, 172 if sx < 0 else 173, M['croc'], 'foot%d' % sx, sx=sx, toes=4, w=1.35)
    # the torso: a barrel chest, a thick neck, bare scaled shoulders with a ridge of spines along each
    for sx in (-1, 1):
        for k in range(4):
            x, y = hx + sx * (14 + k * 5.5), 73 - b + k * 2.2 + (k * 0.8 if sx > 0 else 0)
            r.poly([(x - 2.8, y + 5), (x + 2.8, y + 5), (x + sx * 1.2, y - 3.5)], M['croc'], round_=0.6, group='spine%d%d' % (sx, k))
    r.poly([(hx - 22, 72 - b), (hx + 22, 74 - b), (hx + 34, 87 - b), (hx + 32, 106), (hx + 27, 128), (hx - 27, 128), (hx - 32, 104), (hx - 34, 84 - b)],
           M['croc'], round_=0.85, group='torso')
    r.tube((hx - 1, 62 - b), (hx - 1, 76 - b), 10.5, 12.0, M['croc'], group='neck', folds=lambda u, sd: -0.14 if abs(abs(sd) - 0.5) < 0.08 else 0)
    fc = hx + 2                                                                      # the apron's middle, turned right
    # the apron + its neck strap; old brown blood in smears and wiped handprints, a ragged hem
    r.tube((fc - 15, 82 - b), (fc - 8, 68 - b), 1.7, 1.7, M['leath'], group='strap')
    r.tube((fc + 15, 82 - b), (fc + 8, 68 - b), 1.7, 1.7, M['leath'], group='strap')
    ap = [(fc - 17, 81 - b), (fc + 17, 81 - b), (fc + 19, 108), (fc + 27, 114), (fc + 29, 150)] + \
         [(fc + 29 - k * 4, 150 + (3 if k % 2 else 0) + h32(k, 9) % 3) for k in range(15)] + [(fc - 29, 150), (fc - 27, 114), (fc - 19, 108)]
    def apron_v(x, y):
        v = (rig.nM(x * 1.6 + 30, y * 1.6) - 0.5) * 0.14
        return v + 0.08 * math.sin((x + 0.5 - fc) / 6 * math.pi) * (1 if y > 116 else 0) - (0.1 if 106 < y < 110 else 0)
    r.poly(ap, M['apron'], round_=0.8, group='apron', vfun=apron_v)
    seam(r, 'apron', 0.18)
    for (x, y), e in list(r.buf.items()):
        if r.groups[e[2]] != 'apron': continue
        n = rig.nM(x * 0.8 + 11, y * 0.8 + 5) + (rig.nF(x * 1.6, y * 1.6) - 0.5) * 0.3
        if n > 0.77 and y > 108: r.fixed(x, y, STAIN[2] if n < 0.81 else STAIN[1])
    for (x0, y0) in ((fc + 20, 118), (fc + 23, 124), (fc - 24, 122)):                  # where he wipes his hands
        for k in range(9):
            if (k + x0) % 4: r.fixed(x0 + (k % 3) - 1, y0 + k, STAIN[2] if k % 2 else STAIN[1])
    r.poly([(fc - 27, 112), (fc + 27, 112), (fc + 27.5, 116), (fc - 27.5, 116)], M['leath'], round_=0.85, group='belt')
    for (dx, dy) in ((0, 0), (1, 0), (2, 0), (3, 0), (0, 1), (3, 1), (0, 2), (3, 2), (0, 3), (1, 3), (2, 3), (3, 3)):
        r.fixed(fc - 2 + dx, 112 + dy, IRON[6] if dy == 0 else IRON[4])
    r.poly([(fc - 27, 116), (fc - 16, 116), (fc - 16, 128), (fc - 19, 131), (fc - 25, 130), (fc - 27, 126)], M['leath'], round_=0.7, group='pouch')
    r.tube((fc + 20, 116), (fc + 22, 138), 1.0, 1.0, M['iron'], group='ladle')
    r.ellipsoid(fc + 22.5, 141, 3.6, 3.0, M['iron'], group='ladlebowl')
    cross(r, fc - 1, 88 - b, h=9, w=7, t=2, ramp_=GOLD)
    for k in range(9): r.fixed(fc - 5 + k * 0.5, 77 - b + k * 1.2, LEATH[2]); r.fixed(fc + 5 - k * 0.5, 77 - b + k * 1.2, LEATH[2])
    # the head (scowling, 3/4), a scar over the snout, the toque
    hd = lizard_head(r, 59, 54, P, CROC, BELLY, EYE_Y, s=1.25, snout=11.0, expr='angry', teeth=True)
    for k in range(6): r.fixed(66 + k, 49 - b + k * 0.9, CROC[7]); r.fixed(66 + k, 50 - b + k * 0.9, CROC[1])
    tb = 45 - b
    r.tube((59, tb), (59, tb - 7), 10.5, 10.5, M['toque'], group='toqueband', folds=lambda u, sd: -0.1 if int((sd + 1) * 4) % 2 else 0)
    for (dx, dy, rr) in ((-7, -11, 7.0), (7, -11, 7.0), (0, -14, 8.0), (-4, -17, 5.6), (5, -17, 5.6)):
        r.ellipsoid(59 + dx, tb + dy, rr, rr * 0.86, M['toque'], group='toquepuff', jag=0.04)
    seam(r, 'toquepuff', 0.12)
    for (x, y) in ((54, tb - 4), (55, tb - 3), (63, tb - 13)): tint(r, x, y, STAIN[2], 0.0)
    shade_under(r, tb + 4, ('head', 'headsnout'), CROC[1], 0.4, fade=5)
    # the left arm: the cleaver rests on his shoulder like a parade rifle (lifted off it and set down again on a tap);
    # the elbow hangs at his side, the forearm comes up to the fist in front of the shoulder
    t = P.get('tap', 0)
    up = [0, 3, 0][t]
    shL = (hx - 31, 84 - b)
    el = (hx - 37, 108 - b)
    fist = (hx - 28, 90 - b - up)
    blade_c = (hx - 36, 70 - b - up * 1.6)
    ang = math.radians(-128 + up * 3)                                                # the handle runs up and back from the fist
    hdir = (math.cos(ang), math.sin(ang))
    hend = (fist[0] + hdir[0] * 9, fist[1] + hdir[1] * 9)
    nx, ny = -hdir[1], hdir[0]                                                       # across the handle (the blade's width)
    if ny > 0: nx, ny = -nx, -ny
    blade = [(hend[0] - hdir[0] * 1, hend[1] - hdir[1] * 1), (hend[0] + hdir[0] * 15, hend[1] + hdir[1] * 15),
             (hend[0] + hdir[0] * 15 + nx * 12, hend[1] + hdir[1] * 15 + ny * 12), (hend[0] - hdir[0] * 1 + nx * 11, hend[1] - hdir[1] * 1 + ny * 11)]
    r.ellipsoid(shL[0] + 1, shL[1], 10.0, 9.0, M['croc'], group='deltL')
    r.tube(shL, el, 8.6, 7.6, M['croc'], group='armLu', bulge=lambda u: 1.2 * math.sin(u * math.pi), folds=lambda u, sd: 0.08 if sd < -0.4 else 0)
    r.poly(blade, M['iron'], round_=0.25, tilt=-0.4, group='blade',
           vfun=lambda x, y: (-0.22 if (rig.nM(x * 3, y * 3) > 0.66) else 0) + (0.3 if ((x - hend[0]) * nx + (y - hend[1]) * ny) > 10 else 0))
    hole = (hend[0] + hdir[0] * 11 + nx * 3, hend[1] + hdir[1] * 11 + ny * 3)
    for (dx, dy) in ((0, 0), (1, 0), (0, 1), (1, 1)): r.fixed(hole[0] + dx, hole[1] + dy, (36, 32, 30))
    for k in range(7): r.fixed(hend[0] + hdir[0] * (2 + k * 2) + nx * 10.5, hend[1] + hdir[1] * (2 + k * 2) + ny * 10.5, STAIN[1] if k % 2 else STAIN[2])
    r.tube(fist, hend, 1.8, 1.8, M['wood'], group='handle')
    r.tube(el, fist, 7.4, 5.0, M['croc'], group='armLl', bulge=lambda u: 1.4 * math.sin(min(1.0, u * 1.5) * math.pi))
    seam(r, 'armLl', 0.24)
    claw_hand(r, (fist[0] + 1, fist[1]), M['croc'], 'handL', ang=0, fingers=3, spread=10, ln=3.6, curl=0.9, size=1.6)
    # the right arm: a slab of meat in the fist, a string of sausages swinging
    sw = [0, 1.5, -1.0][P.get('sway', 0)]
    shR = (hx + 31, 87 - b)
    r.ellipsoid(shR[0] - 1, shR[1], 10.0, 9.0, M['croc'], group='deltR')
    elR = (hx + 38, 109 - b)
    fr = (hx + 35, 123)
    r.tube(shR, elR, 8.6, 7.6, M['croc'], group='armRu', bulge=lambda u: 1.2 * math.sin(u * math.pi))
    r.tube(elR, fr, 7.4, 5.0, M['croc'], group='armRl', bulge=lambda u: 1.0 * math.sin(min(1.0, u * 1.6) * math.pi))
    seam(r, 'armRl', 0.22)
    for k in range(6):
        c = (fr[0] - 1 + sw * (k / 5) ** 1.5 * 3 - k * 0.3, fr[1] + 7 + k * 6.0)
        r.ellipsoid(c[0], c[1], 2.8, 3.5, M['flesh'], lift=-0.05, group='sausage%d' % k)
        r.fixed(c[0], c[1] - 3.4, CAPE[2])
    r.ellipsoid(fr[0] + 8, fr[1] - 5, 6.6, 9.6, M['flesh'], rot=0.35, group='meat',
                vfun=lambda x, y, u, w: (0.26 if abs(u * 0.7 + w * 0.7 - 0.3) < 0.08 or abs(u * 0.7 + w * 0.7 + 0.35) < 0.07 else 0) + (0.3 if u > 0.82 else 0))
    for k in range(5): r.fixed(fr[0] + 13, fr[1] - 11 + k * 2.5, (200, 184, 160))       # the bone end
    claw_hand(r, (fr[0], fr[1] + 1), M['croc'], 'handR', ang=180, fingers=3, spread=10, ln=3.6, curl=0.9, size=1.6)
    return warm_ink(r.render())


def gallow_frames(): return [gallow(P) for P in GALLOW_POSE]


# ======================================================================================================================
# the rest of the table: Otho Pinescale, the Goodfennow Twins, Deacon Foyle, Old Mother Quill
# ======================================================================================================================
RUST   = R('#170905 #241009 #34170d #451f12 #562817 #67321d #783d24 #89492c')
NEWT   = R('#1e2119 #2c3124 #3c4231 #4e5540 #616951 #757d63 #899177 #9ea58b')
LAVEN  = R('#1e1b24 #2a2633 #373244 #453f55 #554e66 #655e77 #766f88 #888199 #9a94aa')
VIOLET = R('#1c1224 #2a1a36 #3a2448 #4a2f5a #5b3b6b')
DALM   = R('#0e1610 #16211a #1f2d23 #293a2d #344737 #405542 #4d634d #5b7259')
GREY   = R('#121211 #1b1b19 #252522 #302f2b #3c3b36 #4a4842 #59574f #69665d #7a776c')
OLDSK  = R('#14160f #1e2117 #292c1f #343828 #404432 #4d523d #5b6049 #6a6f56')
BLIND  = R('#5e6466 #7c8284 #9aa0a0 #b6bab8 #cacdca')
CHEESE = R('#4a3610 #6e5218 #927024 #b08c34 #c8a64a #dabe66')
GLASSG = R('#0e1a12 #16281c #20382a #2c4a38 #3a5e48')
SILVER = R('#2a2a2c #44444a #626268 #828288 #a2a2a6 #c2c2c4')
M.update({'rust': Mat(RUST, 'wool', 0.2, 0.05), 'newt': Mat(NEWT, 'skin', 0.3, 0.3), 'laven': Mat(LAVEN, 'fabric', 0.26, 0.3),
          'violet': Mat(VIOLET, 'fabric', 0.24, 0.3), 'dalm': Mat(DALM, 'velvet', 0.2, 0.1), 'grey': Mat(GREY, 'coarse', 0.22),
          'oldsk': Mat(OLDSK, 'warts', 0.24, 0.1), 'cheese': Mat(CHEESE, 'skin', 0.36, 0.2), 'bottle': Mat(GLASSG, 'plain', 0.3, 0.9),
          'silver': Mat(SILVER, 'metal', 0.3, 0.8)})


def pine_crest(r, hx, hy, s, b, mat):
    """Otho's namesake: overlapping pine-cone scale plates over the crown and down the nape"""
    for k, (dx, dy, rr) in enumerate(((-8, -7, 3.4), (-4, -9.5, 3.6), (0.5, -10.5, 3.6), (5, -9.5, 3.2), (-10.5, -2.5, 3.0), (-11, 2.5, 2.8))):
        x, y = hx + dx * s, hy - b + dy * s
        r.poly([(x - rr, y + rr * 0.6), (x + rr, y + rr * 0.6), (x + rr * 0.5, y - rr * 0.9), (x - rr * 0.2, y - rr * 1.2)], mat, round_=0.6,
               group='pine%d' % k, vfun=lambda xx, yy, y=y: 0.12 if yy < y - 1 else -0.06)
        seam(r, 'pine%d' % k, 0.18)


OTHO_POSE = [dict(), dict(sway=-1), dict(b=1), dict(sway=1), dict(toast=1), dict(toast=1, blink=True), dict(hic=1), dict(sway=-1, b=1)]


def otho(P):
    """the over-served wine merchant: rust doublet, orange trim, a wine-stained shirt, a bottle raised to the cardinal,
    a wedge of cheese, a satchel; pine-cone scale plates on his crown; flushed, grinning, swaying"""
    r = Rig(128, 160)
    b = P.get('b', 0) + (1 if P.get('hic') else 0)
    sw = P.get('sway', 0)
    hx = 62 + sw
    tp = [(48, 140), (36, 148), (25, 150), (16, 146), (12, 138), (14, 131)]
    lizard_tail(r, tp[0], tp[1:], 5.0, M['liz'], 'tail', r1=1.0, belly=True)
    for (fx, sx) in ((52, -1), (73, 1)):                                              # breeches + travel boots, a sailor's stance
        r.tube((fx + sx * 1 - sw * 0.5, 118), (fx + sx * 2, 140), 7.0, 6.2, M['brown'], group='leg%d' % sx)
        r.tube((fx + sx * 2, 136), (fx + sx * 2, 151), 6.4, 6.0, Mat(LEATH, 'leather', 0.22, 0.5), group='boot%d' % sx,
               folds=lambda u, sd: 0.18 if u < 0.1 else 0)
        r.ellipsoid(fx + sx * 3, 154, 7.4, 3.4, Mat(LEATH, 'leather', 0.22, 0.5), group='sole%d' % sx)
    # the doublet over a round belly, open at the neck over a stained shirt; orange trim, a satchel on its strap
    def dv(x, y): return (0.1 if (x + y) % 6 == 0 else 0) - (0.1 if y > 120 else 0)
    r.poly([(hx - 8, 66 - b), (hx + 8, 66 - b), (hx + 19, 71 - b), (hx + 25, 82), (hx + 30, 98), (hx + 31, 110), (hx + 27, 122), (hx + 14, 128), (hx, 129),
            (hx - 14, 128), (hx - 27, 122), (hx - 31, 110), (hx - 30, 98), (hx - 25, 82), (hx - 19, 71 - b)],
           M['rust'], round_=0.92, tilt=0.12, group='doublet', vfun=dv)
    r.poly([(hx - 5, 70 - b), (hx + 7, 70 - b), (hx + 4, 92 - b), (hx - 1, 94 - b)], M['lace'], round_=0.7, group='shirt')
    for (x, y) in ((hx + 1, 82 - b), (hx + 2, 83 - b), (hx + 1, 84 - b), (hx + 3, 86 - b)): r.fixed(x, y, WINE[2])
    for k in range(10):                                                              # the orange trim + buttons down the front
        y = 94 + k * 3.2
        if y < 126: r.fixed(hx + 2 + (k % 2) * 0, y, OCHRE[6] if k % 2 else OCHRE[4]); r.fixed(hx + 3, y, OCHRE[3])
    for x in range(int(hx - 26), int(hx + 27)): r.fixed(x, 123 + abs(x - hx) * 0.08, OCHRE[5] if x % 3 else OCHRE[3])
    r.tube((hx - 16, 72 - b), (hx + 22, 112), 1.4, 1.4, M['leath'], group='strap')
    r.poly([(hx + 18, 108), (hx + 32, 108), (hx + 33, 124), (hx + 29, 127), (hx + 19, 126), (hx + 17, 120)], M['leath'], round_=0.7, group='satchel')
    r.poly([(hx + 17.5, 108), (hx + 32.5, 108), (hx + 32, 114), (hx + 18, 114)], M['leath'], lift=0.12, round_=0.5, group='satchelflap')
    # left hand: a wedge of cheese held at the belly
    cx, cy = hx - 20, 104
    habit_sleeve(r, (hx - 22, 76 - b), (hx - 29, 96 - b), (cx - 2, cy + 2), M['rust'], 'armL', cuff=5.2)
    r.poly([(cx - 6, cy - 4), (cx + 9, cy - 8), (cx + 8, cy + 1), (cx - 5, cy + 3)], M['cheese'], round_=0.4, tilt=-0.4, group='cheese',
           vfun=lambda x, y: -0.3 if h32(x, y, 13) % 9 == 0 else 0)
    claw_hand(r, (cx - 1, cy + 2), M['liz'], 'handL', ang=-30, fingers=3, spread=10, ln=3.0, curl=0.85, size=1.25)
    # the head: flushed, grinning, half-lidded; the pine crest
    r.tube((hx - 1, 56 - b), (hx, 70 - b), 6.6, 7.4, M['liz'], group='neck', folds=lambda u, sd: -0.14 if abs(abs(sd) - 0.5) < 0.08 else 0)
    r.poly([(hx - 7, 64 - b), (hx + 8, 64 - b), (hx + 5, 72 - b), (hx - 4, 72 - b)], M['lace'], round_=0.7, group='collar')
    pine_crest(r, hx - 2, 50, 1.1, b, Mat(LIZ, 'scales', 0.26, 0.25))
    hd = lizard_head(r, hx - 2, 50, P, LIZ, BELLY, EYE_Y, s=1.1, snout=10.0, expr='smug', teeth=True)
    for (cx2, cy2) in ((hx - 6, 55), (hx + 6, 54)):                                   # wine-flushed cheeks
        for dx in range(-2, 3):
            for dy in range(-1, 2): tint(r, cx2 + dx, cy2 + dy - b, (150, 60, 50), 0.32)
    # right hand: the bottle raised to the cardinal (higher on a toast), the elbow down at his side
    up = 4 if P.get('toast') else 0
    bt = (hx + 32, 66 - up)
    wr = habit_sleeve(r, (hx + 22, 76 - b), (hx + 33, 96 - b), (bt[0], bt[1] + 9), M['rust'], 'armR', cuff=5.2)
    tilt = -0.25
    r.tube((bt[0] - 3, bt[1] + 8), (bt[0] + 1, bt[1] - 8), 3.6, 3.4, M['bottle'], group='bottle')
    r.tube((bt[0] + 1, bt[1] - 8), (bt[0] + 2.5, bt[1] - 15), 1.5, 1.3, M['bottle'], group='bottle')
    r.tube((bt[0] + 2.5, bt[1] - 15), (bt[0] + 3, bt[1] - 17), 1.6, 1.6, Mat(WOOD, 'wood', 0.3), group='cork')
    for k in range(5): r.fixed(bt[0] - 2 + k * 0.6, bt[1] + 1 - k * 2.2, (200, 210, 190))      # a glint on the glass
    for (dx, dy) in ((-3, 0), (-2, 0), (-3, 1), (-2, 1), (-1, 1)): r.fixed(bt[0] + dx + 1, bt[1] + dy + 2, CAPE[4])   # the label
    claw_hand(r, (bt[0] - 1, bt[1] + 3), M['liz'], 'handR', ang=180, fingers=3, spread=10, ln=3.2, curl=0.9, size=1.3)
    return warm_ink(r.render())


def otho_frames(): return [otho(P) for P in OTHO_POSE]


TWINS_POSE = [dict(), dict(b=1), dict(lookA=1), dict(lookB=1), dict(blink=True), dict(fan=1), dict(lorg=1), dict(lookA=1, lookB=1)]


class _mirror_light:
    """render a figure facing the other way: mirror the key light, draw, then flip the image -- the light stays top-left"""
    def __enter__(self):
        self.saved = (rig.LIGHT, rig.HALF, BAND_L[0])
        rig.LIGHT = (-rig.LIGHT[0], rig.LIGHT[1], rig.LIGHT[2]); rig.HALF = (-rig.HALF[0], rig.HALF[1], rig.HALF[2])
        BAND_L[0] = (0.5, -0.7, 0.55)
    def __exit__(self, *a):
        rig.LIGHT, rig.HALF, BAND_L[0] = self.saved


def twin(P, which):
    """one Goodfennow: a slender marsh-noble newt with a low dorsal crest, a silver circlet, a lavender silk coat with a
    ruff, violet facings. A holds a fan, B a lorgnette; both face right here (B is drawn mirrored)"""
    r = Rig(72, 144)
    b = P.get('b', 0)
    hx = 34
    look = (1, 0) if P.get('look' + which) else (0, 0)
    tp = [(26, 126), (18, 133), (10, 135), (5, 130)]
    lizard_tail(r, tp[0], tp[1:], 3.4, M['newt'], 'tail', r1=0.9, belly=True)
    lizard_foot(r, 29, 140, M['newt'], 'footL', sx=-1, w=0.85)
    lizard_foot(r, 41, 140, M['newt'], 'footR', sx=1, w=0.85)
    r.poly([(hx - 7, 64 - b), (hx + 7, 64 - b), (hx + 12, 70 - b), (hx + 11, 90), (hx + 10, 98), (hx + 17, 118), (hx + 20, 136), (hx - 18, 137), (hx - 15, 118),
            (hx - 9, 98), (hx - 10, 90), (hx - 12, 70 - b)], M['laven'], round_=0.85, group='coat',
           vfun=lambda x, y: 0.08 * math.sin((x + 0.5 - hx) / 4 * math.pi + 0.3) * (1 if y > 98 else 0) - (0.1 if y > 133 else 0))
    for k in range(18): r.fixed(hx + 2 + k * 0.1, 70 - b + k * 3.6, VIOLET[3] if k % 2 else VIOLET[2])   # the violet facing
    for k in range(5): r.fixed(hx + 4, 76 - b + k * 6, SILVER[4]); r.fixed(hx + 4, 77 - b + k * 6, SILVER[1])
    r.poly([(hx - 17, 135), (hx + 19, 135), (hx + 20, 137), (hx - 18, 137)], M['violet'], round_=0.5, group='hem')
    r.poly([(hx - 10, 94), (hx + 11, 94), (hx + 11, 99), (hx - 10, 99)], M['violet'], round_=0.8, group='sash')
    r.tube((hx + 5, 99), (hx + 7, 110), 1.6, 1.2, M['violet'], group='sashend')
    for sx in (-1, 1): r.ellipsoid(hx + sx * 10, 70 - b, 4.6, 3.8, M['laven'], lift=0.1, group='puff%d' % sx,
                                   vfun=lambda x, y, u, w: -0.18 if x % 2 == 0 else 0)
    # arms: hands meet at the waist; A has a closed / fluttering fan, B lifts a lorgnette
    wl = habit_sleeve(r, (hx - 9, 70 - b), (hx - 12, 90 - b), (hx - 3, 98), M['laven'], 'armL', cuff=3.6)
    if which == 'A':
        f = P.get('fan', 0)
        if f:
            for k in range(7):
                a = math.radians(-150 + k * 16)
                r.tube((hx + 2, 98), (hx + 2 + math.cos(a) * 11, 98 + math.sin(a) * 11), 1.2, 1.6, M['violet'], group='fan%d' % k)
        else:
            r.tube((hx + 1, 98), (hx + 9, 88), 1.6, 2.0, M['violet'], group='fan')
        hr = habit_sleeve(r, (hx + 9, 70 - b), (hx + 12, 90 - b), (hx + 4, 99), M['laven'], 'armR', cuff=3.6)
        claw_hand(r, (hr[0] - 1, hr[1]), M['newt'], 'handR', ang=200, fingers=3, spread=8, ln=2.6, curl=0.8, size=1.0, claws=False)
    else:
        l = P.get('lorg', 0)
        hr = habit_sleeve(r, (hx + 9, 70 - b), (hx + 13, 90 - b), (hx + 9, 80 - b - l * 12) if l else (hx + 4, 99), M['laven'], 'armR', cuff=3.6)
        lx, ly = hr[0] + 1, hr[1] - 7
        r.tube((hr[0], hr[1]), (lx, ly), 0.8, 0.8, M['silver'], group='lorg')
        for a in range(14):
            t = a / 14 * 2 * math.pi
            r.fixed(lx + 1 + math.cos(t) * 2.4, ly - 2 + math.sin(t) * 2.0, SILVER[5] if math.sin(t) < 0 else SILVER[2])
        claw_hand(r, (hr[0], hr[1]), M['newt'], 'handR', ang=200, fingers=3, spread=8, ln=2.6, curl=0.8, size=1.0, claws=False)
    claw_hand(r, (wl[0] + 1, wl[1]), M['newt'], 'handL', ang=-10, fingers=3, spread=8, ln=2.6, curl=0.8, size=1.0, claws=False)
    # the ruff, the head (refined, a little haughty), the crest, the circlet
    r.ellipsoid(hx, 66 - b, 10.0, 4.0, M['lace'], group='ruff', vfun=lambda x, y, u, w: -0.22 if x % 2 == 0 else 0.04)
    for k in range(9):                                                               # a low dorsal crest over the crown
        x = hx - 9 + k * 1.6
        h = 2.6 * math.sin(k / 8 * math.pi) + 0.6
        for y in range(int(36 - b - h - (8 - abs(k - 4)) * 0.4), int(38 - b - (8 - abs(k - 4)) * 0.4)): r.fixed(x, y, NEWT[2] if k % 2 else NEWT[3])
    pp = dict(P); pp['look'] = look
    r.tube((hx - 1, 52 - b), (hx, 64 - b), 3.6, 4.0, M['newt'], group='neck')
    r.ellipsoid(hx, 64 - b, 9.0, 3.6, M['lace'], group='ruff2', vfun=lambda x, y, u, w: -0.22 if x % 2 == 0 else 0.04)
    lizard_head(r, hx - 1, 47, pp, NEWT, LACE, EYE_B, s=0.9, snout=8.0, expr='smug')
    for x in range(hx - 10, hx + 7):
        y = 38 - b + abs(x + 1 - hx) * 0.12
        r.fixed(x, y, SILVER[5] if x % 3 == 0 else SILVER[3]); r.fixed(x, y + 1, SILVER[1])
    r.fixed(hx - 2, 37 - b, VIOLET[4]); r.fixed(hx - 2, 36 - b, SILVER[5])
    return warm_ink(r.render())


def twins(P):
    im = Image.new('RGBA', (128, 144), (0, 0, 0, 0))
    a = twin(P, 'A')
    with _mirror_light():
        bb = twin(P, 'B').transpose(Image.FLIP_LEFT_RIGHT)
    im.alpha_composite(bb, (54, 0))                                                 # shoulder to shoulder, so both faces
    im.alpha_composite(a, (2, 0))                                                    # fit the 2x dialog bust
    return im


def twins_frames(): return [twins(P) for P in TWINS_POSE]


FOYLE_POSE = [dict(), dict(tr=1), dict(tr=2, b=1), dict(tr=2), dict(look=(-1, 0)), dict(look=(-1, 0), blink=True), dict(tr=1), dict(b=1)]


def foyle(P):
    """the deacon: a slim, smiling skink in a green dalmatic over a white alb, the deacon's stole slung across from his
    left shoulder; he holds the household ledger open and runs a claw down its columns"""
    r = Rig(128, 160)
    b = P.get('b', 0)
    hx = 63
    fc = hx + 3
    tp = [(50, 140), (38, 147), (27, 150), (18, 147), (13, 139), (15, 132)]
    lizard_tail(r, tp[0], tp[1:], 4.0, M['liz'], 'tail', r1=0.9, belly=True)
    lizard_foot(r, 57, 156, M['liz'], 'footL', sx=-1)
    lizard_foot(r, 72, 157, M['liz'], 'footR', sx=1)
    r.poly([(hx - 12, 70 - b), (hx + 12, 70 - b), (hx + 18, 120), (hx + 19, 152), (hx - 18, 153), (hx - 17, 120)], M['lace'], round_=0.8, group='alb',
           vfun=lambda x, y: -0.14 if (x - fc) % 5 == 0 and y > 128 else 0)
    def dalm_v(x, y):
        v = 0.08 * math.sin((x + 0.5 - fc) / 5 * math.pi) * (1 if y > 100 else 0)
        if abs(x + 0.5 - (fc - 9)) < 2.2 or abs(x + 0.5 - (fc + 8)) < 2.2: v += 0.0
        return v - (0.1 if y > 132 else 0)
    r.poly([(hx - 16, 70 - b), (hx + 16, 70 - b), (hx + 22, 88), (hx + 23, 134), (hx - 24, 135), (hx - 23, 88)], M['dalm'], round_=0.85, group='dalm', vfun=dalm_v)
    for sx in (-9, 8):                                                               # the dalmatic's two gold clavi
        for y in range(int(74 - b), 134):
            r.fixed(fc + sx, y, GOLD[3] if y % 4 else GOLD[4]); r.fixed(fc + sx + 1, y, GOLD[1])
    for x in range(hx - 23, hx + 24): r.fixed(x, 132, GOLD[3] if x % 2 else GOLD[2])
    knee_swell(r, ('dalm', 'alb'), fc + 12, 124, 6.0, 10.0)
    # the stole: from the left shoulder across the chest to the right hip (a deacon wears it so)
    for k in range(40):
        t = k / 39
        x, y = hx - 13 + t * 30, 72 - b + t * 46
        for d in range(-2, 3): r.fixed(x + d * 0.5, y - d * 0.9, GOLD[4] if d < 0 else GOLD[3] if d == 0 else GOLD[2])
    cross(r, hx, 94 - b, h=6, w=5, t=2)
    # the ledger in the left hand, the right claw running down a column
    tr = P.get('tr', 0)
    wl = habit_sleeve(r, (hx - 14, 74 - b), (hx - 20, 96 - b), (hx - 12, 104), M['dalm'], 'armL', cuff=6.4)
    lx, ly = hx - 6, 98
    r.poly([(lx - 11, ly - 7), (lx + 11, ly - 9), (lx + 12, ly + 5), (lx - 10, ly + 7)], M['leath'], round_=0.3, group='ledgercover')
    for sx in (-1, 1):
        x0, x1 = (lx - 10, lx) if sx < 0 else (lx, lx + 11)
        r.poly([(x0, ly - 6.5 - (x0 - lx) * 0.09), (x1, ly - 6.5 - (x1 - lx) * 0.09), (x1, ly + 4.5 - (x1 - lx) * 0.09), (x0, ly + 4.5 - (x0 - lx) * 0.09)],
               Mat(PAGES[:5], 'plain', 0.4), round_=0.5, tilt=-0.4, group='ledgerp%d' % sx,
               vfun=lambda x, y: -0.4 if (y % 2 == 0 and (x % 5) != 0 and abs(x - lx) > 1) else (-0.2 if x % 5 == 0 else 0))
    for y in range(ly - 7, ly + 6): r.darken(lx, y, 0.25)
    claw_hand(r, (wl[0], wl[1] + 1), M['liz'], 'handL', ang=-30, fingers=3, spread=10, ln=3.0, curl=0.8, size=1.2)
    tip = (lx + 6, ly - 4 + tr * 3)
    habit_sleeve(r, (hx + 14, 74 - b), (hx + 21, 96 - b), (tip[0] + 7, tip[1] + 5), M['dalm'], 'armR', cuff=6.4)
    claw_hand(r, (tip[0] + 4, tip[1] + 2), M['liz'], 'handR', ang=200, fingers=2, spread=6, ln=3.4, curl=0.2, size=1.15)
    # the head: a narrow, glossy skink head, smiling
    r.tube((hx - 1, 54 - b), (hx, 68 - b), 4.6, 5.2, M['liz'], group='neck')
    r.ellipsoid(hx, 68 - b, 9.0, 3.4, M['lace'], group='amice')
    hd = lizard_head(r, hx - 1, 49, P, LIZ, BELLY, EYE_Y, s=1.05, snout=10.5, expr='smug')
    for (x, y) in ((hx - 6, 42), (hx - 3, 40), (hx + 1, 40)): r.fixed(x, y - b, LIZ[8])  # the gloss of smooth scales
    return warm_ink(r.render())


def foyle_frames(): return [foyle(P) for P in FOYLE_POSE]


QUILL_POSE = [dict(), dict(b=1), dict(cup=1), dict(cup=2), dict(cup=1), dict(murmur=1), dict(tilt=1), dict(b=1, tilt=1)]


def quill(P):
    """Old Mother Quill: an ancient, hunched, blind swamp-lizard under a long grey veil, milky eyes, a deeply creased
    hide; a gnarled stick in one hand, a cup of wine in the other"""
    r = Rig(128, 144)
    b = P.get('b', 0)
    hx = 60
    tl = P.get('tilt', 0)
    tp = [(50, 128), (38, 134), (27, 136), (18, 132), (13, 125)]
    lizard_tail(r, tp[0], tp[1:], 4.6, M['oldsk'], 'tail', r1=1.0, belly=True)
    lizard_foot(r, 56, 140, M['oldsk'], 'footL', sx=-1)
    lizard_foot(r, 71, 141, M['oldsk'], 'footR', sx=1)
    # the walking stick on her left, gripped at chest height
    r.tube((36, 141), (40, 84), 1.5, 1.8, M['wood'], group='stick', folds=lambda u, sd: -0.2 if int(u * 9) % 3 == 0 else 0)
    r.ellipsoid(40.5, 82, 2.6, 2.4, M['wood'], group='stickknob')
    # the hunched body under the veil: the back bows forward, the veil falls to the ground in heavy folds
    def veil_v(x, y):
        v = 0.09 * math.sin((x + 0.5 - hx) / 5 * math.pi + 0.7) * (1 if y > 90 else 0)
        return v - (0.12 if y > 136 else 0)
    r.poly([(hx - 16, 66 - b), (hx - 8, 56 - b), (hx + 4, 58 - b), (hx + 16, 68), (hx + 22, 84), (hx + 24, 104), (hx + 26, 138), (hx + 6, 140),
            (hx - 20, 139), (hx - 22, 104), (hx - 21, 80)], M['grey'], round_=0.85, group='veil', vfun=veil_v)
    knee_swell(r, ('veil',), hx + 12, 118, 6.0, 10.0)
    # the left hand on the stick, the right holding the cup (it rises to her mouth to sip)
    habit_sleeve(r, (hx - 14, 72 - b), (hx - 19, 92 - b), (41, 86), M['grey'], 'armL', cuff=4.6)
    claw_hand(r, (40, 87), M['oldsk'], 'handL', ang=0, fingers=3, spread=10, ln=3.2, curl=0.9, size=1.25)
    c = P.get('cup', 0)
    cup = [(hx + 14, 96), (hx + 14, 82), (hx + 12, 70)][c]
    habit_sleeve(r, (hx + 14, 72 - b), (hx + 20, 94 - b), (cup[0] + 3, cup[1] + 6), M['grey'], 'armR', cuff=4.6)
    for yy in range(int(cup[1] - 6), int(cup[1] + 1)):
        for xx in range(int(cup[0] - 3), int(cup[0] + 4)):
            r.fixed(xx, yy, IRON[5] if xx < cup[0] - 1 else IRON[3] if xx < cup[0] + 2 else IRON[1])
    for xx in range(int(cup[0] - 2), int(cup[0] + 3)): r.fixed(xx, cup[1] - 6, WINE[3] if c < 2 else IRON[6])
    for yy in range(int(cup[1] + 1), int(cup[1] + 4)): r.fixed(cup[0], yy, IRON[4])
    for xx in range(int(cup[0] - 2), int(cup[0] + 3)): r.fixed(xx, cup[1] + 4, IRON[3])
    claw_hand(r, (cup[0] + 1, cup[1] - 1), M['oldsk'], 'handR', ang=180, fingers=3, spread=10, ln=2.8, curl=0.9, size=1.2)
    # the head: low and forward on a creased neck, the veil's hood over it; blind milky eyes, a murmuring mouth
    hhx, hhy = hx + 8 + tl, 64 + tl
    r.tube((hx, 70 - b), (hhx - 2, hhy + 6 - b), 6.0, 5.0, M['oldsk'], group='neck', folds=lambda u, sd: -0.2 if int(u * 7) % 2 else 0)
    hood(r, hhx - 5, hhy - 4, 15.5, 14.0, M['grey'], GREY, 'hood', b=b)
    hd = lizard_head(r, hhx, hhy, P, OLDSK, BELLY, BLIND, s=1.05, snout=10.0, expr='narrow')
    for (x, y), e in list(r.buf.items()):                                            # the eyes: no pupils, only cloud
        if e[3] in (PUPIL, SHINE): e[3] = BLIND[3]
    for k in range(5):                                                               # deep creases on the cheek and snout
        r.fixed(hhx - 6 + k * 2, hhy + 3 - b + (k % 2), OLDSK[1])
        r.fixed(hhx + 3 + k * 2, hhy - 1 - b + (k % 2), OLDSK[2])
    if P.get('murmur'):
        mt = hd['mouth']
        for x in range(int(hhx + 1), int(hhx + 8)): r.fixed(x, int(mt(x)) + 1, (40, 24, 20))
    shade_under(r, hhy - 6 - b, ('head', 'headsnout'), GREY[1], 0.45)
    return warm_ink(r.render())


def quill_frames(): return [quill(P) for P in QUILL_POSE]


CAST = {'emils': (emils_frames, 128, 176), 'pim': (pim_frames, 128, 128), 'vesper': (vesper_frames, 128, 176),
        'marigold': (marigold_frames, 128, 160), 'cornelius': (cornelius_frames, 128, 160), 'wren': (wren_frames, 128, 144),
        'gallow': (gallow_frames, 128, 176), 'otho': (otho_frames, 128, 160), 'twins': (twins_frames, 128, 144),
        'foyle': (foyle_frames, 128, 160), 'quill': (quill_frames, 128, 144)}


def token(im, pal, cache):
    """half size: a 2x2 box filter over the opaque pixels (a cell with <2 opaque pixels drops out), the colour snapped back
    onto the character's own colours so the token stays crisp pixel art"""
    w, h = im.size
    src = im.load()
    out = Image.new('RGBA', (w // 2, h // 2), (0, 0, 0, 0)); p = out.load()
    for y in range(h // 2):
        for x in range(w // 2):
            acc = [0, 0, 0]; a = 0; dark = 0
            for dy in (0, 1):
                for dx in (0, 1):
                    c = src[x * 2 + dx, y * 2 + dy]
                    if c[3]:
                        a += 1
                        for i in range(3): acc[i] += c[i]
            if a < 2: continue
            c = tuple(int(acc[i] / a) for i in range(3))
            if c not in cache: cache[c] = min(pal, key=lambda q: (q[0] - c[0]) ** 2 * 3 + (q[1] - c[1]) ** 2 * 4 + (q[2] - c[2]) ** 2 * 2)
            p[x, y] = cache[c] + (255,)
    # a dark rim again where the figure meets the transparent surround (the box filter softened the outline)
    q = out.copy().load()
    for y in range(h // 2):
        for x in range(w // 2):
            if not q[x, y][3]: continue
            edge = any(not (0 <= x + dx < w // 2 and 0 <= y + dy < h // 2) or not q[x + dx, y + dy][3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if edge: p[x, y] = mix(q[x, y][:3], WARM_INK, 0.55) + (255,)
    return out


def rebuild_tokens(d):
    """<d>/<id>.png sheets (e.g. exported from Aseprite after touch-ups) -> <d>/<id>_t.png half-size token sheets"""
    for cid, (fn, w, h) in CAST.items():
        sh = Image.open(f'{d}/{cid}.png').convert('RGBA')
        frames = [sh.crop((i * w, 0, i * w + w, h)) for i in range(sh.width // w)]
        pal = sorted({c[:3] for im in frames for c in im.get_flattened_data() if c[3]}) if hasattr(Image.Image, 'get_flattened_data') else sorted({c[:3] for im in frames for c in im.getdata() if c[3]})
        cache = {}
        sheet([token(im, pal, cache) for im in frames], f'{d}/{cid}_t.png')
        print(cid, 'token sheet', len(frames))


if __name__ == '__main__' and OUT == '--tokens':
    rebuild_tokens(sys.argv[2])
elif __name__ == '__main__':
    ids = sys.argv[2:] or list(CAST)
    os.makedirs(OUT, exist_ok=True)
    allc = set()
    for cid in ids:
        fn, w, h = CAST[cid]
        frames = fn()
        os.makedirs(f'{OUT}/{cid}', exist_ok=True)
        os.makedirs(f'{OUT}/{cid}_t', exist_ok=True)
        for i, im in enumerate(frames): im.save(f'{OUT}/{cid}/{i}.png')
        sheet(frames, f'{OUT}/{cid}.png')
        pal = sorted({c[:3] for im in frames for c in im.get_flattened_data() if c[3]}) if hasattr(Image.Image, 'get_flattened_data') else sorted({c[:3] for im in frames for c in im.getdata() if c[3]})
        allc |= set(pal)
        cache = {}
        toks = [token(im, pal, cache) for im in frames]
        for i, im in enumerate(toks): im.save(f'{OUT}/{cid}_t/{i}.png')
        sheet(toks, f'{OUT}/{cid}_t.png')
        print(cid, len(frames), len(pal), 'colours')
    rows = ['%3d %3d %3d\t#%02x%02x%02x' % (c + c) for c in sorted(allc, key=lambda c: (0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]))]
    if len(ids) == len(CAST):
        open(f'{OUT}/feast_cast.gpl', 'w').write('GIMP Palette\nName: feast_cast\nColumns: 16\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT)
