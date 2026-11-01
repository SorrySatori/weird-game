"""Ortolan Smelc, the board-game designer (ShedCourtyardScene on Day 1, BurningBearStreetScene on Day 2), redrawn with
the character renderer (rig.py, the Edgar quality bar) -- replacing the box-filtered cartoon (Ortolan.png / ortolan4.png,
now only a reference for who he is). An old, stocky worldwright: a bald pate in a ragged horseshoe of white hair, bushy
white brows, small round brass spectacles with a faint amber tint, a ruddy bulbous nose, a walrus moustache and a full
white beard down onto his chest; a long, worn brown coat (open, broad lapels, permit forms sticking out of the left
pocket) over an olive waistcoat with horn buttons and a brass watch chain, dark trousers, old brogues. His left hand
holds a red-lacquered pawn at his chest, the right one hangs (ortolan4: it grips his lapel, the elbow out and down).
  ortolan   128x160, soles on y 156
  ortolan4  128x160, the same man at the same height plus the pair the Shed approved: in rolled-up shirtsleeves, newer
            pinker skin, coming out from under the waistcoat and holding a small wooden game board at his hips
8 idle frames, the same meaning in both sheets (the scenes share one frame order):
  0 rest  1 inhale  2 blink  3 the spectacles catch the light  4 "hm": brows up, the moustache works (ortolan4: a lower
  thumb lifts off the board)  5 the pawn comes up  6 he studies it, eyes on it (ortolan4: the board comes up a pixel)
  7 exhale (the head settles first)
python3 ortolan.py <outdir>  ->  ortolan.png ortolan4.png (sheets) + ortolan/<n>.png ortolan4/<n>.png + ortolan.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK
import rig
from rig import Rig, Mat
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
R = ramp
COAT  = R('#110a06 #1b0f09 #26150d #321c11 #3e2416 #4b2c1b #593521 #673e28 #774930 #885639')
VEST  = R('#0e1209 #171e0f #202915 #2a341b #354021 #414c29 #4e5a31 #5c683a')
SHIRT = R('#29231b #3e362a #554b3b #6b5f4c #81745d #958870 #a69a80')
TROU  = R('#0f0b09 #18120f #211914 #2b211a #352920 #403228')
SHOE  = R('#110a07 #1d120c #2a1a11 #392418 #4a2f20 #5c3c29 #6e4a33')
SKIN  = R('#361d14 #4f2d1e #6a3c28 #845034 #9c6242 #b27652 #c58b64 #d4a07a #e1b693')
NEWSK = R('#45221c #643126 #834533 #9f5a43 #b67056 #c8876a #d79f80 #e3b69a')
ROSE  = R('#56231e #733128 #8e4134 #a55442 #b96852 #c87e66')
HAIR  = R('#282522 #3d3935 #534e48 #6a645d #827c73 #9a948a #b1ab9f #c6c1b5 #d8d4c9')
STACH = R('#2b261f #423b31 #595144 #716758 #897e6c #a19582 #b8ac96 #ccc1a9 #dcd3bc')   # yellowed by pipe smoke
GOLD  = R('#2a1c09 #463210 #6a4e1a #8e6c25 #b08a35 #cfab52 #e8cc84')
WOOD  = R('#24140b #3c230f #553317 #6f4520 #8a582a #a46d37 #bb8447 #cf9c5c')
RED   = R('#2e0f0c #4a1712 #682219 #842f21 #9c3f2b #b4553a')
PAPER = R('#4f493a #696350 #847c66 #9d957c #b2aa90 #c3bba1')
INKC  = (48, 30, 26)
PUPIL = (30, 20, 16)
EYEW  = (206, 192, 172)
TINT  = (232, 176, 86)
WARM_INK = (38, 22, 16)

# extra textures in the renderer's table: a worn tweed with Edgar-like mottling and stains, streaky white hair, a fine
# waistcoat twill
rig.TEX['tweed'] = lambda x, y: ((rig.nF(x * 1.7, y * 1.7) - 0.5) * 0.10 + (rig.nM(x * 1.1, y * 1.1) - 0.5) * 0.16
                                 + (rig.nL(x * 0.7 + 40, y * 0.7) - 0.5) * 0.24 + (0.025 if (x + 2 * y) % 3 == 0 else -0.01))
rig.TEX['beard'] = lambda x, y: ((rig.nF(x * 1.3 + 2.0 * math.sin(y * 0.23), y * 0.2) - 0.5) * 0.40
                                 + (rig.nM(x * 0.8, y * 0.8) - 0.5) * 0.08)
rig.TEX['vest'] = lambda x, y: (rig.nF(x * 2.0, y * 2.0) - 0.5) * 0.10 + (rig.nL(x, y + 30) - 0.5) * 0.12 + (0.03 if y % 2 else -0.02)
M = {'coat': Mat(COAT, 'tweed', 0.17), 'vest': Mat(VEST, 'vest', 0.2, 0.05), 'shirt': Mat(SHIRT, 'fabric', 0.24),
     'trou': Mat(TROU, 'fabric', 0.2), 'shoe': Mat(SHOE, 'leather', 0.2, 0.7), 'skin': Mat(SKIN, 'skin', 0.3, 0.15),
     'newskin': Mat(NEWSK, 'skin', 0.32, 0.2), 'hair': Mat(HAIR, 'beard', 0.26, 0.08), 'stache': Mat(STACH, 'beard', 0.3, 0.1),
     'hand': Mat(SKIN, 'skin', 0.24, 0.12), 'newhand': Mat(NEWSK, 'skin', 0.26, 0.15), 'gold': Mat(GOLD, 'metal', 0.26, 0.8),
     'wood': Mat(WOOD, 'wood', 0.28, 0.25), 'red': Mat(RED, 'plain', 0.26, 0.9), 'paper': Mat(PAPER, 'plain', 0.4)}

POSE = [dict(bt=0, bh=0), dict(bt=1, bh=1), dict(bt=0, bh=0, blink=1), dict(bt=0, bh=0, glint=1),
        dict(bt=0, bh=0, hm=1), dict(bt=0, bh=0, pawn=1, look=1), dict(bt=0, bh=0, pawn=2, look=1, brow=1, board=1),
        dict(bt=1, bh=0)]


def mix(a, b, t): return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def group_at(r, x, y):
    e = r.buf.get((int(x), int(y)))
    return r.groups[e[2]] if e else None


def hand_hang(r, w, sx, mat, g):
    """a relaxed hanging hand below the wrist w; sx = which side of the body (-1 viewer-left), the thumb turns inward"""
    x, y = w
    r.ellipsoid(x, y + 3.4, 3.1, 3.9, mat, group=g)
    for k in range(4):                                                        # fingers, curled a little toward the thigh
        fx = x - 2.0 + k * 1.3
        r.tube((fx, y + 5.8), (fx - sx * 0.5, y + 9.4 - abs(k - 1.5) * 0.5), 0.95, 0.85, mat, group=g + 'f%d' % k)
        seam(r, g + 'f%d' % k, 0.16)
    r.tube((x - sx * 2.1, y + 2.4), (x - sx * 2.9, y + 6.4), 1.2, 1.0, mat, lift=0.06, group=g + 't')
    seam(r, g + 't', 0.2)


def pawn(r, px, py, mat, g):
    """a turned wooden pawn standing on (px, py)"""
    r.ellipsoid(px, py - 0.6, 2.1, 1.1, mat, group=g)
    r.tube((px, py - 1.2), (px, py - 4.2), 1.45, 0.85, mat, group=g)
    r.ellipsoid(px, py - 4.4, 1.6, 0.7, mat, lift=0.1, group=g)
    r.ellipsoid(px, py - 6.0, 1.8, 1.8, mat, lift=0.05, group=g)


def hand_hold(r, c, sx, mat, g, turn=0):
    """a hand holding the pawn up between thumb and curled fingers; c = the back of the hand, fingers wrap toward -sx"""
    x, y = c
    r.ellipsoid(x + sx * 0.8, y, 3.3, 3.3, mat, group=g)
    px = x - sx * 1.2
    pawn(r, px, y - 2.4, M['red'], g + 'p')
    if turn: r.fixed(px + 1, y - 9.6, RED[5]); r.fixed(px + 1, y - 6.4, RED[4])     # it turns: the glint moves
    for k in range(3):
        r.tube((x + sx * 1.7, y - 1.2 + k * 1.7), (x - sx * 2.5, y - 1.0 + k * 1.8), 1.05, 0.95, mat, group=g + 'f%d' % k)
        seam(r, g + 'f%d' % k, 0.16)
    r.tube((x + sx * 1.5, y - 2.6), (x - sx * 2.3, y - 3.4), 1.1, 0.9, mat, lift=0.08, group=g + 't')


def hand_lapel(r, c, sx, mat, g):
    """a hand gripping the coat's lapel: the back of the hand to us, the fingers curled over the edge toward -sx"""
    x, y = c
    r.ellipsoid(x, y, 3.2, 3.4, mat, group=g)
    for k in range(3):
        r.tube((x - sx * 0.6, y - 1.8 + k * 1.7), (x - sx * 3.2, y - 1.2 + k * 1.8), 1.0, 0.9, mat, lift=0.04, group=g + 'f%d' % k)
        seam(r, g + 'f%d' % k, 0.16)


def sleeve(r, sh, el, wr, g, mat=None):
    """a coat sleeve shoulder -> elbow -> wrist: a crease in the elbow, bunching above the cuff, a turned-back cuff"""
    mat = mat or M['coat']
    r.tube(sh, el, 5.8, 5.0, mat, group=g, folds=lambda u, sd: (-0.24 if u > 0.84 and abs(sd) < 0.5 else 0) + (0.08 if u < 0.2 and sd < -0.3 else 0))
    r.tube(el, wr, 5.0, 4.4, mat, group=g, folds=lambda u, sd: -0.2 if (0.55 < u < 0.6 or 0.72 < u < 0.76) and abs(sd) < 0.7 else 0)
    dx, dy = wr[0] - el[0], wr[1] - el[1]; L = math.hypot(dx, dy) or 1
    r.tube((wr[0] - dx / L * 2.8, wr[1] - dy / L * 2.8), wr, 4.8, 4.8, mat, lift=0.14, group=g + 'cuff')
    seam(r, g, 0.22)


def head(r, hx, ey, P):
    """(hx, ey): the face's axis (between two pixel columns) and the eye row"""
    brow = 1 if (P.get('brow') or P.get('hm')) else 0
    look = P.get('look', 0)
    r.ellipsoid(hx, ey + 0.5, 13.0, 9.6, M['hair'], lift=-0.16, group='hairback')     # the fringe behind the head
    for sx in (-1, 1):
        r.ellipsoid(hx + sx * 10.6, ey + 2.0, 2.3, 3.7, M['skin'], group='ear%d' % sx)
        r.fixed(hx + sx * 10.6 - (1 if sx > 0 else 0), ey + 2, SKIN[2])
    # the face: clean hand-pixelled bands so the features read at 1x
    L = rig.norm((-0.5, -0.65, 0.6))
    cy, rx, ry = ey - 2.5, 10.4, 13.8
    face = {}
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(hx - rx) - 1, int(hx + rx) + 2):
            u, w = (x + 0.5 - hx) / rx, (y + 0.5 - cy) / ry
            if w > 0.3: u /= max(0.45, 1 - (w - 0.3) * 0.5)                    # the jaw narrows
            d = u * u + w * w
            if d > 1: continue
            n = (u * 0.92, w * 0.9, math.sqrt(max(0.05, 1 - d * 0.82)))
            v = 0.16 + 0.84 * max(0.0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2])
            dx, dy = x + 0.5 - hx, y - ey
            for sx in (-1, 1):                                                 # deep sockets under the brows
                if abs(dx - sx * 4.5) <= 3.4 and -2 <= dy <= 1: v -= 0.14 if dy < 0 else 0.06
            if dy in (-9, -7) and abs(dx) <= 5.5 and (x * 7 + y) % 5: v -= 0.09  # forehead lines
            if abs(dx) >= 7.5 and -7 <= dy <= -1: v -= 0.07                   # temples
            if -15 <= dy <= -12 and -5 <= dx <= -1: v += 0.12                 # the pate shines
            face[(x, y)] = v
    oid = r.new('face')
    for (x, y), v in face.items():
        c = SKIN[max(1, min(8, 1 + int(v * 7.6)))]
        dx, dy = x + 0.5 - hx, y - ey
        for sx in (-1, 1):                                                     # ruddy cheeks
            if (dx - sx * 6.5) ** 2 + ((dy - 4) * 1.3) ** 2 <= 6: c = mix(c, ROSE[3 + (sx < 0)], 0.42)
        r.fixed(x, y, c, oid)
    for (x, y) in ((hx + 4, ey - 11), (hx + 5, ey - 11), (hx - 6, ey - 9), (hx + 6, ey - 6)):   # age spots
        if (x, y) in face: r.fixed(x, y, mix(r.buf[(x, y)][3], SKIN[2], 0.5))
    for (x, y) in ((hx - 3, ey - 14), (hx - 1, ey - 15), (hx + 2, ey - 14), (hx + 1, ey - 15)):   # strands combed over
        if (x, y) in face: r.fixed(x, y, HAIR[5]); r.fixed(x + 1, y, HAIR[4])
    # eyes: small, old, deep-set
    for sx in (-1, 1):
        ex = int(math.floor(hx + sx * 4.5 - 0.5))                              # the eye's middle column
        if P.get('blink'):
            for x in range(ex - 1, ex + 2): r.fixed(x, ey, SKIN[2]); r.fixed(x, ey - 1, SKIN[4])
        else:
            for x in range(ex - 1, ex + 2): r.fixed(x, ey, EYEW)
            r.fixed(ex + look, ey, PUPIL)
            if look == 0: r.fixed(ex + sx, ey, mix(EYEW, SKIN[3], 0.4))       # the iris' rim toward the temple
            for x in range(ex - 1, ex + 2): r.fixed(x, ey - 1, SKIN[1])     # the upper lid's lash line
        r.fixed(ex - 1, ey + 2, SKIN[3]); r.fixed(ex, ey + 2, SKIN[3]); r.fixed(ex + 1, ey + 2, SKIN[4])   # bags
    # the nose: long, bulbous, ruddy at the tip
    nose = {(0, 1): 6, (1, 1): 4, (0, 2): 6, (1, 2): 4, (0, 3): 7, (1, 3): 4,
            (-1, 4): 5, (0, 4): 7, (1, 4): 5, (2, 4): 3, (-1, 5): 6, (0, 5): 7, (1, 5): 5, (2, 5): 2,
            (-1, 6): 4, (0, 6): 5, (1, 6): 4, (2, 6): 2}
    for (dx, dy), k in nose.items():
        c = SKIN[k]
        if dy >= 4: c = mix(c, ROSE[min(5, k - 1)], 0.5)
        r.fixed(hx - 1 + dx, ey + dy, c)
    r.fixed(hx - 2, ey + 7, SKIN[2]); r.fixed(hx - 1, ey + 7, SKIN[3]); r.fixed(hx, ey + 7, SKIN[3]); r.fixed(hx + 1, ey + 7, SKIN[1])
    r.fixed(hx + 2, ey + 5, SKIN[3]); r.fixed(hx + 2, ey + 6, SKIN[2]); r.fixed(hx + 3, ey + 6, SKIN[3])   # its shadow on the cheek
    return face


def spectacles(r, hx, ey, P):
    """round brass spectacles; the lenses warm what is behind them a touch"""
    for sx in (-1, 1):
        cx = hx + sx * 4.5                                                     # centre of a pixel column (x + 0.5)
        for y in range(ey - 4, ey + 5):
            for x in range(int(cx) - 4, int(cx) + 5):
                d = math.hypot(x + 0.5 - cx, y + 0.5 - (ey + 0.5))
                e = r.buf.get((x, y))
                if d <= 2.6 and e is not None and e[3] is not None:
                    c = mix(e[3], TINT, 0.13)
                    if x + 0.5 < cx and y < ey: c = mix(c, (255, 248, 226), 0.08)
                    e[3] = c
                elif 2.6 < d <= 3.55:
                    a = math.atan2(y + 0.5 - (ey + 0.5), x + 0.5 - cx)
                    col = GOLD[4] if -2.5 < a < -1.0 else (GOLD[1] if 0.3 < a < 2.5 else GOLD[2])
                    r.fixed(x, y, col)
        gx, gy = int(cx) - 1, ey - 1
        if P.get('glint'):
            for (x, y, c) in ((gx - 1, gy + 2, (238, 226, 198)), (gx, gy + 1, (255, 250, 232)), (gx + 1, gy, (255, 250, 232)),
                              (gx + 2, gy - 1, (238, 226, 198)), (gx + 1, gy + 1, (226, 206, 166))):
                r.fixed(x, y, c)
            r.fixed(int(cx) - 2, ey - 3, GOLD[6])
        else:
            r.fixed(gx, gy, mix(r.buf[(gx, gy)][3] or TINT, (255, 246, 222), 0.45))
            r.fixed(int(cx) - 2, ey - 3, GOLD[5])
        r.fixed(int(cx) + sx * 4, ey - 1, GOLD[2])                             # the hinge; the temple runs back into the hair
        r.fixed(int(cx) + sx * 5, ey - 1, GOLD[1])
    r.fixed(hx - 1, ey - 1, GOLD[4]); r.fixed(hx, ey - 1, GOLD[2])             # the bridge over the nose


def brows(r, hx, ey, P):
    """bushy white brows overhanging the rims; up on "hm" and when he studies the pawn"""
    by = ey - 3 - (1 if (P.get('brow') or P.get('hm')) else 0)
    for sx in (-1, 1):
        bx = int(math.floor(hx + sx * 4.5 - 0.5))
        for k in range(-2, 4):
            x = bx + k * sx
            droop = 1 if k >= 3 else 0
            r.fixed(x, by + droop, HAIR[4] if k > 0 else HAIR[5])
            if -2 <= k <= 2: r.fixed(x, by - 1 + droop, HAIR[7] if k < 1 else HAIR[6])
        r.fixed(bx + 3 * sx, by - 2, HAIR[6])                                   # strays curling up
        r.fixed(bx + 4 * sx, by - 1, HAIR[5])
        r.fixed(bx - 2 * sx, by - 2, HAIR[6])


def fringe(r, hx, ey):
    """the ragged horseshoe of white hair round the back of the head, wild over the ears"""
    for sx in (-1, 1):
        for (dx, dy, rx, ry, jag, lift) in ((9.6, -9.6, 2.4, 2.0, 0.3, 0.12), (11.8, -7.2, 2.7, 2.8, 0.35, 0.06),
                                            (13.0, -3.6, 2.6, 3.2, 0.38, 0.0), (13.4, -0.4, 2.2, 2.6, 0.4, -0.04),
                                            (12.2, 4.2, 2.0, 2.4, 0.3, -0.1), (14.6, -5.6, 1.5, 1.3, 0.5, 0.05)):
            r.ellipsoid(hx + sx * dx, ey + dy, rx, ry, M['hair'], jag=jag, lift=lift, group='fringe%d' % sx)


def beard(r, hx, ey, P):
    hm = P.get('hm', 0)
    top = ey + 18
    def clip(x, y):
        dx = abs(x + 0.5 - hx)
        if dx > 13.6 - max(0.0, y - top) * 0.44: return False                 # it tapers onto the chest
        if dx >= 10.2: return y >= ey - 1                                      # sideburns into the fringe
        return y >= ey + 7.6 - max(0.0, dx - 3.2) * 0.8                        # the cheek line falls to the moustache
    def strands(x, y, u, w):
        v = -0.18 if (x * 5 + int(3 * math.sin(y * 0.3))) % 7 == 0 and w > -0.3 else 0
        return v - (0.05 if w > 0.8 else 0) - (0.08 if abs(u) > 0.8 else 0)
    r.ellipsoid(hx, ey + 15.0, 13.8, 21.0, M['hair'], group='beard', clip=clip, vfun=strands, jag=0.07, flat=0.6)
    for (dx, ln) in ((-4, 2), (-1, 3), (2, 2), (5, 1)):                         # wisps at its point
        x = hx + dx
        yb = max((y for y in range(ey, ey + 40) if group_at(r, x, y) == 'beard'), default=None)
        if yb is None: continue
        for k in range(1, ln + 1): r.fixed(x + (k // 2) * (1 if dx > 0 else -1) * 0, yb + k, HAIR[4 - min(k, 2)])
    # the moustache: a heavy walrus, parted under the nose, a dark line under it
    d = 1 if hm else 0
    pts = [(hx - 2.2, ey + 7.6), (hx + 2.2, ey + 7.6), (hx + 5.2, ey + 6.4), (hx + 7.8, ey + 8.0), (hx + 9.2, ey + 12.4 - d),
           (hx + 6.6, ey + 11.8 + d), (hx + 3.0, ey + 11.0 + d), (hx, ey + 10.6 + d), (hx - 3.0, ey + 11.0 + d), (hx - 6.6, ey + 11.8 + d),
           (hx - 9.2, ey + 12.4 - d), (hx - 7.8, ey + 8.0), (hx - 5.2, ey + 6.4)]
    r.poly(pts, M['stache'], lift=0.16, round_=0.8, tilt=-0.3, group='stache',
           vfun=lambda x, y: (-0.22 if x in (hx - 1, hx) and y < ey + 9 else 0) + (-0.12 if (x * 3 + y) % 5 == 0 else 0))
    my = ey + 11 + d
    for x in range(hx - 9, hx + 9):                                            # the shadow under the moustache
        ys = [y for y in range(ey + 6, ey + 16) if group_at(r, x, y) == 'stache']
        if ys and group_at(r, x, max(ys) + 1) == 'beard':
            r.darken(x, max(ys) + 1, 0.3); r.darken(x, max(ys) + 2, 0.12)
    if hm:                                                                     # "hm": the lips push out under it
        for x in range(hx - 2, hx + 2): r.fixed(x, my + 1, INKC)
        r.fixed(hx - 1, my + 2, ROSE[4]); r.fixed(hx, my + 2, ROSE[3])
    else:
        r.fixed(hx - 2, my + 1, mix(INKC, HAIR[3], 0.4)); r.fixed(hx - 1, my + 1, INKC); r.fixed(hx, my + 1, INKC)
        r.fixed(hx + 1, my + 1, mix(INKC, HAIR[3], 0.4))
        r.fixed(hx - 1, my + 2, ROSE[3]); r.fixed(hx, my + 2, ROSE[2])


def board(r, cx, by):
    """a small wooden game board held level at the hips, seen a little from above; by = the top surface's middle row"""
    top = [(cx - 12.5, by - 4), (cx + 12.5, by - 4), (cx + 14.5, by + 2), (cx - 14.5, by + 2)]
    def field(x, y):
        rel = y - (by - 4)                                                     # 0..5 back to front
        xl, xr = cx - 11.0 - rel * 0.33, cx + 11.0 + rel * 0.33
        if rel < 1 or rel > 4 or x < xl or x >= xr: return 0.2                 # the frame, lighter wood
        return -0.42 if ((int((x - cx + 30) // 3) + (rel - 1) // 2) % 2) else 0.0
    r.poly(top, M['wood'], round_=0.3, tilt=-0.9, group='board', vfun=field)
    r.poly([(cx - 14.5, by + 2), (cx + 14.5, by + 2), (cx + 14.5, by + 4), (cx - 14.5, by + 4)], M['wood'], lift=-0.24, round_=0.5,
           group='board', vfun=lambda x, y: -0.1 if y == by + 4 else 0)
    for (dx, dy, col) in ((-8, 0, 'ivory'), (-4, -2, 'dark'), (5, 1, 'ivory'), (8, -2, 'red'), (1, 0, 'dark')):
        x, y = cx + dx, by + dy
        hi, lo = {'ivory': ((218, 206, 178), (146, 132, 106)), 'dark': ((90, 70, 56), (38, 28, 22)), 'red': (RED[5], RED[2])}[col]
        r.fixed(x, y - 2, hi); r.fixed(x + 1, y - 2, lo)
        r.fixed(x, y - 1, hi); r.fixed(x + 1, y - 1, lo)
        r.fixed(x - 1, y, hi); r.fixed(x, y, hi); r.fixed(x + 1, y, lo)
        r.darken(x + 2, y, 0.2)


def ortolan(P, four=False):
    W = 128
    cx = W // 2
    r = Rig(W, 160)
    bt, bh = P['bt'], P['bh']
    U = lambda y: y - bt if y < 97 else y
    ey = 29 - bh
    # legs and old brogues: a short, planted stance
    for sx in (-1, 1):
        hip, foot = (cx + sx * 6.0, 104), (cx + sx * 8.5, 149)
        knee = ((hip[0] + foot[0]) / 2 + sx * 0.4, (hip[1] + foot[1]) / 2)
        r.tube(hip, knee, 7.2, 6.0, M['trou'], group='leg%d' % sx, folds=lambda u, sd: -0.22 if abs(sd) < 0.1 and u > 0.3 else 0)
        r.tube(knee, foot, 6.0, 5.2, M['trou'], group='leg%d' % sx,
               folds=lambda u, sd, sx=sx: (-0.2 if u > 0.78 and abs(sd + sx * 0.3) < 0.12 else 0) + (0.08 if u > 0.86 else 0))
        r.ellipsoid(foot[0] + sx * 1.8, 152.6, 7.6, 3.6, M['shoe'], group='shoe%d' % sx)
        r.ellipsoid(foot[0] + sx * 0.8, 150.3, 4.9, 2.3, M['shoe'], lift=0.1, group='shoe%d' % sx)
        r.fixed(foot[0] + sx * 1.8 - 3, 152, SHOE[6]); r.fixed(foot[0] + sx * 1.8 - 2, 152, SHOE[5])   # a shine on the toe cap
    r.poly([(cx - 13, 96), (cx + 13, 96), (cx + 13.5, 110), (cx + 2, 116), (cx, 112), (cx - 2, 116), (cx - 13.5, 110)], M['trou'],
           group='pelvis', vfun=lambda x, y: -0.18 if x in (cx - 1, cx) and y > 104 else 0)
    # the waistcoat over a round belly: horn buttons, two welt pockets, a brass watch chain
    vest = [(cx - 10, U(51)), (cx + 10, U(51)), (cx + 14, U(67)), (cx + 16.5, U(84)), (cx + 16, 97), (cx + 14, 106), (cx + 1, 101.5),
            (cx - 1, 101.5), (cx - 14, 106), (cx - 16, 97), (cx - 16.5, U(84)), (cx - 14, U(67))]
    r.poly(vest, M['vest'], round_=0.9, tilt=0.15, group='vest',
           vfun=lambda x, y: (-0.22 if x == cx and y > U(56) else 0) + (0.1 if x == cx - 1 and y > U(56) else 0)
           + (-0.1 if y > 94 else 0))
    for y in (64, 72, 80, 88, 96):
        yy = U(y); r.fixed(cx, yy, (124, 100, 70)); r.fixed(cx, yy + 1, (54, 40, 28)); r.fixed(cx - 1, yy, (86, 68, 46))
    for sx in (-1, 1):
        for x in range(cx + sx * 7, cx + sx * 13, sx): r.fixed(x, U(87), VEST[0]); r.darken(x, U(88), -0.12)
    for i in range(11):                                                         # the watch chain sags to the left pocket
        t = i / 10
        x, y = cx - 1 - 9 * t, U(81) + 6 * t + 2.8 * math.sin(math.pi * t)
        r.fixed(x, y, GOLD[5] if i % 2 else GOLD[3])
    # the coat: a standing collar behind the beard, two long panels open over the waistcoat, broad lapels
    r.ellipsoid(cx, U(52), 14.5, 5.0, M['coat'], lift=-0.1, group='collar')
    def panel_v(sx):
        folds = [(cx + sx * 16.5, 97, 0.10), (cx + sx * 21.5, 104, 0.15), (cx + sx * 13.5, 114, 0.05)]
        def v(x, y):
            out = 0.0
            for (fx, fy, slant) in folds:
                if y < fy: continue
                px = fx + sx * (y - fy) * slant
                d = (x + 0.5 - px) * sx
                if -0.5 <= d < 0.5: out -= 0.3
                elif -1.5 <= d < -0.5: out += 0.12
            if 124 <= y < 133: out -= (y - 124) * 0.018                         # street dirt creeping up the hem
            if y >= 133: out += 0.1                                             # its edge is worn pale
            if y >= 135: out -= 0.22
            for (sx_, sy, sr) in ((-18.5, 121, 2.2), (20.5, 92, 1.8), (-21.0, 78, 1.6)):   # old stains
                if (x + 0.5 - (cx + sx_)) ** 2 + ((y - sy) * 1.3) ** 2 < sr * sr: out -= 0.14
            return out
        return v
    for sx in (-1, 1):
        sag = 1.2 if sx > 0 else 0                                              # the pocket full of forms drags that side
        pts = [(cx + sx * 9, U(49)), (cx + sx * 20, U(53)), (cx + sx * 22.5, U(62)), (cx + sx * 23, 92), (cx + sx * 24.5, 116),
               (cx + sx * 26.5, 135 + sag), (cx + sx * 18, 137 + sag), (cx + sx * 10.5, 137.5 + sag * 0.6), (cx + sx * 10.5, 114),
               (cx + sx * 12, 95), (cx + sx * 13.2, U(79)), (cx + sx * 9.6, U(53))]
        r.poly(pts, M['coat'], round_=0.75, group='coat%d' % sx, vfun=panel_v(sx))
        lap = [(cx + sx * 9.2, U(50)), (cx + sx * 15, U(53.5)), (cx + sx * 14, U(56.5)), (cx + sx * 18.5, U(60)), (cx + sx * 13.3, U(79.5)),
               (cx + sx * 10.8, U(64))]
        r.poly(lap, M['coat'], lift=0.13, round_=0.5, group='lapel%d' % sx)
        seam(r, 'lapel%d' % sx, 0.2)
    # permit forms sticking out of the left pocket (viewer's right), behind the flap (ortolan4's lower arm is there)
    for k, (dx, top, tilt) in enumerate(() if four else ((16.0, 100.0, -0.15), (18.2, 101.6, 0.12), (20.0, 100.4, 0.3))):
        x0 = cx + dx
        r.poly([(x0, top), (x0 + 4, top + tilt * 4), (x0 + 4.2, 109), (x0 + 0.2, 109)], M['paper'], lift=0.08 - k * 0.12, round_=0.3,
               group='paper%d' % k, vfun=lambda x, y, top=top: -0.14 if (y - int(top)) % 2 == 0 and y > top + 1 else 0)
    if not four: r.fixed(cx + 21, 101, RED[3]); r.fixed(cx + 22, 101, RED[2]); r.fixed(cx + 21, 102, RED[2])   # a red stamp
    for sx in (-1, 1):                                                          # the hip-pocket flaps
        x0 = cx + sx * 13.5
        r.poly([(x0, 107), (x0 + sx * 9.6, 106.5), (x0 + sx * 9.8, 110.5), (x0, 111)], M['coat'], lift=0.1, round_=0.4, group='flap%d' % sx)
        seam(r, 'flap%d' % sx, 0.28)
    # the right arm (viewer's left) hangs
    shL = (cx - 19.5, U(58))
    if four:                                                                    # ortolan4: it grips his lapel, the elbow
        wrL = (cx - 16.0, U(71))                                                # out and down at his side
        sleeve(r, shL, (cx - 24.0, U(82)), wrL, 'armL')
        hand_lapel(r, (cx - 13.2, U(69)), -1, M['hand'], 'handL')
    else:
        wrL = (cx - 23.5, 104)
        elL = ((shL[0] + wrL[0]) / 2 - 1.6, (shL[1] + wrL[1]) / 2)              # the elbow hangs by the body
        sleeve(r, shL, elL, wrL, 'armL')
        hand_hang(r, (wrL[0] + 0.3, wrL[1] + 0.5), -1, M['hand'], 'handL')
    # the extra pair (ortolan4): shirtsleeves from under the waistcoat, bare forearms, the board at the hips
    if four:
        by = 115 - P.get('board', 0)
        under_vest = lambda x, y: not (y < U(98) and group_at(r, x, y) == 'vest')   # the roots go in under the waistcoat
        for sx in (-1, 1):
            root, elbow = (cx + sx * 11.0, U(92)), (cx + sx * 16.2, 103.0)
            handc = (cx + sx * 15.4, by - 1.0)
            ec = (root[0] + (elbow[0] - root[0]) * 0.72, root[1] + (elbow[1] - root[1]) * 0.72)   # rolled up above the elbow
            r.tube(root, ec, 3.0, 2.8, M['shirt'], group='lsl%d' % sx, clip=under_vest,
                   folds=lambda u, sd: -0.22 if 0.45 < u < 0.53 else 0)
            r.tube(elbow, handc, 2.6, 2.2, M['newskin'], group='lfa%d' % sx)
            r.ellipsoid(elbow[0], elbow[1] - 0.5, 2.6, 2.4, M['newskin'], group='lfa%d' % sx)   # the elbow, bare
            r.tube(ec, (ec[0] + (elbow[0] - ec[0]) * 0.8, ec[1] + (elbow[1] - ec[1]) * 0.8), 3.4, 3.3, M['shirt'], lift=0.12,
                   group='lcuff%d' % sx, folds=lambda u, sd: -0.25 if 0.4 < u < 0.6 else 0)
            seam(r, 'lsl%d' % sx, 0.18); seam(r, 'lcuff%d' % sx, 0.2)
            r.ellipsoid(handc[0] + sx * 0.5, handc[1] + 2.0, 2.1, 2.7, M['newhand'], group='lh%d' % sx)   # the heel of the hand
        board(r, cx, by)
        for sx in (-1, 1):                                                       # the thumbs lie on the board
            up = 2 if (P.get('hm') and sx < 0) else 0
            r.tube((cx + sx * 15.6, by - 0.5 - up * 0.4), (cx + sx * 12.3, by - 0.8 - up), 1.15, 0.95, M['newhand'], lift=0.08,
                   group='lthumb%d' % sx)
            seam(r, 'lthumb%d' % sx, 0.2)
            for k in range(2): r.fixed(cx + sx * (13.8 - k * 1.4), by + 4, NEWSK[3 - k])         # fingertips under the edge
    # the head: the fringe, the face, spectacles, brows, the beard
    hx = cx
    head(r, hx, ey, P)
    spectacles(r, hx, ey, P)
    brows(r, hx, ey, P)
    fringe(r, hx, ey)
    beard(r, hx, ey, P)
    # the left arm (viewer's right): the pawn at his chest, raised to the eyes to study it
    pw = P.get('pawn', 0)
    shR = (cx + 19.5, U(58))
    handR = [(cx + 12, U(80)), (cx + 13, U(70)), (cx + 13.5, U(58))][pw]
    elR = [(cx + 22.5, U(83)), (cx + 23.5, U(80)), (cx + 24, U(75))][pw]        # the elbow stays down at his side
    wrR = (handR[0] + 2.9, handR[1] + (0.4 if pw < 2 else 1.6))
    sleeve(r, shR, elR, wrR, 'armR')
    hand_hold(r, handR, 1, M['hand'], 'handR', turn=(pw == 2))
    im = r.render()
    px = im.load()                                                              # fixed pixels on the silhouette got the
    for y in range(im.height):                                                  # renderer's neutral ink: make it warm
        for x in range(im.width):
            if px[x, y] == (18, 14, 12, 255): px[x, y] = WARM_INK + (255,)
    return im


def sheet(frames, path):
    w, h = frames[0].size
    s = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, im in enumerate(frames): s.paste(im, (i * w, 0))
    s.save(path)


if __name__ == '__main__':
    for name, four in (('ortolan', False), ('ortolan4', True)):
        os.makedirs(f'{OUT}/{name}', exist_ok=True)
        frames = [ortolan(p, four) for p in POSE]
        for i, im in enumerate(frames): im.save(f'{OUT}/{name}/{i}.png')
        sheet(frames, f'{OUT}/{name}.png')
    ALL = ([INK] + COAT + VEST + SHIRT + TROU + SHOE + SKIN + NEWSK + ROSE + HAIR + STACH + GOLD + WOOD + RED + PAPER
           + [INKC, PUPIL, EYEW, TINT, WARM_INK])
    seen, rows = set(), []
    for c in ALL:
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/ortolan.gpl', 'w').write('GIMP Palette\nName: ortolan\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT)
