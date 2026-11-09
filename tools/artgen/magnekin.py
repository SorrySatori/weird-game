"""Magnekin of the Town Square (TownSquareScene; after his filing, the Tribunal's Room in PithReclaimersRoomScene) and
his collapsed remains, redrawn with the character renderer (rig.py, the Edgar quality bar) after the old AI images
magnekin.png / magnekin_broken.png (removed; in git history before the full-game redraw).

He is a collective of micro-cities built on the lodestone shards of the Crownmire shrine, holding a man's shape by
magnetism: a lanky figure packed from dark lumpy lodestone pebbles and magnetic scrap -- blue-black, iron-grey, a few
rust-brown plates -- every pebble lit by its own light and wedged into its neighbours, with tiny warm windows burning in
some of them (the cities). Thin blue-grey cables loop round the chest, the hips and the limbs; a wire hoop arcs over
the head from behind; the round lumpy head wears a crude borrowed face (two pale glowing eyes in dark rings, a slit of
a mouth); seven small winged satellites -- moth-like nodes with one pale eye each -- hang round him on their tethers.

  magnekin         128x192, facing the viewer, soles on row 189; an 8-frame calm idle:
                   0 rest   1 the satellites drift, the windows flicker   2 the eyes blink
                   3 a shoulder pebble lifts off   4 it hangs a pixel out   5 it snaps back with a faint blue spark
                   6 the eyes brighten, iron filings lift from a sleeve   7 settle (the satellites come round)
  magnekin_broken  128x64, the heap he collapses into, ground on row 61; 4 frames:
                   0 still   1 a faint blue spark arcs between two pebbles   2 a pebble twitches   3 a fallen
                   satellite's wing twitches, a window flickers on again
python3 magnekin.py <outdir>  ->  magnekin.png + magnekin/<n>.png, magnekin_broken.png + magnekin_broken/<n>.png,
                                  magnekin.gpl"""
import sys, os, math, random
from PIL import Image
from common import ramp, INK, h32
import rig
from rig import Rig, Mat
from feral_toast import lerp

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
W, H = 128, 192
FLOOR = 189
R = ramp
LODE  = R('#08080a #0e0f12 #141519 #1b1c21 #222429 #2a2c31 #33353a #3d3f43 #484a4d #545656')   # blue-black lodestone
IRONG = R('#0d0e10 #15171a #1e2125 #272b30 #31363c #3b4148 #464d55 #525a62 #5f6871')                  # iron-grey scrap
RUSTC = R('#110906 #1b0e09 #27140d #341b11 #422316 #512b1b #613522 #714029 #824c32')                  # rust plates
WIRE  = [(30, 40, 52), (46, 62, 80), (66, 88, 110), (94, 122, 146), (128, 156, 176)]
WING  = [(52, 54, 64), (78, 80, 94), (108, 108, 122), (140, 138, 152), (170, 166, 178)]
EYEW  = (222, 232, 226)
EYEG  = (128, 172, 172)
DARK  = (10, 10, 14)
WINDOW = [(92, 60, 28), (156, 106, 44), (214, 160, 76), (250, 212, 128)]
SPARK = [(60, 96, 156), (120, 170, 226), (200, 230, 255)]
WARMOUT = (22, 18, 20)                                                     # a dark, slightly warm outline (never black)

rig.TEX['lode'] = lambda x, y: (rig.nM(x * 1.6, y * 1.6) - 0.5) * 0.12 + (0.05 if h32(x, y, 77) % 23 == 0 else 0) - (0.06 if h32(x, y, 78) % 17 == 0 else 0)
def mat(rmp, amb=0.16, spec=0.25): return Mat(rmp, 'lode', amb, spec, outline=WARMOUT)
MATS = {'lode': mat(LODE), 'iron': mat(IRONG, 0.18, 0.35), 'rust': mat(RUSTC, 0.2, 0.1)}


class Body:
    """collects the pebbles of the figure, then draws them back to front"""
    def __init__(s, seed):
        s.peb = []; s.rnd = random.Random(seed); s.windows = []
    def add(s, cx, cy, rx, ry, rot, lift, kind, depth, tag=''):
        s.peb.append(dict(cx=cx, cy=cy, rx=rx, ry=ry, rot=rot, lift=lift, kind=kind, depth=depth, tag=tag))
    def kind(s, rust=0.12, iron=0.25):
        u = s.rnd.random()
        return 'rust' if u < rust else 'iron' if u < rust + iron else 'lode'
    def capsule(s, a, b, ra, rb, layer, rust=0.1, iron=0.25, step=0.62, tag=''):
        """a limb a->b packed with pebbles: the middle ones nearer the viewer, the light from the left"""
        ax, ay = a; bx, by = b; L = math.hypot(bx - ax, by - ay) or 1
        ux, uy = (bx - ax) / L, (by - ay) / L; px, py = -uy, ux
        t = 0.0
        while t <= 1.0001:
            rad = ra + (rb - ra) * t
            cx, cy = ax + (bx - ax) * t, ay + (by - ay) * t
            k = 1 if rad < 2.6 else 2 if rad < 4.2 else 3
            for j in range(k):
                off = ((j - (k - 1) / 2) * rad * (0.95 if k == 2 else 0.68)) + s.rnd.uniform(-0.35, 0.35)
                sd = off / max(rad, 1e-6)
                prx = rad * s.rnd.uniform(0.55, 0.78); pry = prx * s.rnd.uniform(0.75, 1.15)
                s.add(cx + px * off + ux * s.rnd.uniform(-0.6, 0.6), cy + py * off + uy * s.rnd.uniform(-0.6, 0.6),
                      prx, pry, s.rnd.uniform(0, math.pi), -0.26 * sd * (1 if px > 0 else -1) + s.rnd.uniform(-0.05, 0.05),
                      s.kind(rust, iron), layer + (1 - abs(sd)) * 0.5 + s.rnd.uniform(0, 0.08), tag)
            t += max(0.04, step * (ra + rb) / 2 / L * 0.85)
    def blob(s, cx, cy, rx, ry, layer, spacing=4.6, prad=(2.8, 4.2), rust=0.1, iron=0.25, light=(-0.6, -0.8), tag='', clip=None):
        """a rounded mass (the head, the chest) packed with pebbles on a jittered grid; nearer in the middle"""
        y = cy - ry
        row = 0
        while y <= cy + ry:
            x = cx - rx + (spacing / 2 if row % 2 else 0)
            while x <= cx + rx:
                jx, jy = x + s.rnd.uniform(-1.2, 1.2), y + s.rnd.uniform(-1.2, 1.2)
                u, w = (jx - cx) / rx, (jy - cy) / ry
                d = u * u + w * w
                if d <= 1.0 and (clip is None or clip(jx, jy)):
                    pr = s.rnd.uniform(*prad) * (1 - 0.25 * d)
                    nz = math.sqrt(max(0.0, 1 - d))
                    lift = 0.32 * (u * light[0] + w * light[1]) * 0.5 - 0.18 * d + s.rnd.uniform(-0.06, 0.06)
                    s.add(jx, jy, pr, pr * s.rnd.uniform(0.75, 1.1), s.rnd.uniform(0, math.pi), lift, s.kind(rust, iron), layer + nz * 0.6 + s.rnd.uniform(0, 0.06), tag)
                x += spacing
            y += spacing * 0.86; row += 1
    def draw(s, r, jitter=None):
        for i, p in enumerate(sorted(s.peb, key=lambda p: p['depth'])):
            cx, cy = p['cx'], p['cy']
            if jitter and p['tag'] in jitter: cx += jitter[p['tag']][0]; cy += jitter[p['tag']][1]
            r.ellipsoid(cx, cy, p['rx'], p['ry'], MATS[p['kind']], rot=p['rot'], lift=p['lift'], jag=0.28, flat=0.6, group='p%d' % i,
                        vfun=(lambda x, y, u, w: (-0.12 if abs(u + w) < 0.12 else 0)) if p['rx'] > 3.4 else None)   # a fracture line in the big ones
            if p['kind'] != 'rust' and p['rx'] > 2.6 and h32(int(cx * 7), int(cy * 7), 5) % 5 == 0:
                s.windows.append((cx + (h32(int(cx), int(cy), 6) % 3) - 1, cy + (h32(int(cx), int(cy), 7) % 3) - 1, h32(i, 31) % 4))


def bezier(p0, p1, p2, n=24):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (i / n for i in range(n + 1))]


def cable(r, pts, lit=3, shadow=True, behind=None):
    """a thin cable: 1 px, lit on its upper side, a soft shadow pixel under it on whatever it lies over"""
    seen = set()
    for (x, y) in pts:
        k = (int(math.floor(x)), int(math.floor(y)))
        if k in seen: continue
        seen.add(k)
        if behind and behind(k[0], k[1]): continue
        r.fixed(k[0], k[1], WIRE[lit] if (k[0] + k[1]) % 3 else WIRE[lit - 1])
        if shadow: r.darken(k[0], k[1] + 1, 0.22)


def satellite(r, x, y, flap, gid, eye=True):
    """a tiny winged node: a dark lumpy body with one pale eye, four thin veined wings in an X (they beat: flap 0/1)"""
    x, y = int(round(x)), int(round(y))
    lift_ = 1 if flap else 0
    for sx in (-1, 1):
        for (dx, dy, c) in ((2, -2, 2), (3, -3, 3), (4, -3 + lift_, 3), (4, -4 + lift_ * 2, 4), (5, -4 + lift_ * 2, 3), (3, -2, 1),
                            (2, 2, 2), (3, 3, 2), (4, 3, 1), (3, 2, 1)):
            r.fixed(x + sx * dx + (1 if sx > 0 else 0), y + dy, WING[c])
    r.ellipsoid(x + 0.5, y + 0.5, 2.3, 2.0, MATS['lode'], lift=0.12, jag=0.2, group=gid)
    if eye:
        r.fixed(x, y, EYEW); r.fixed(x + 1, y, (176, 196, 190)); r.fixed(x, y + 1, (150, 168, 164))
    else:
        r.fixed(x, y, LODE[3])


SATS = [  # (anchor on the body, rest position, phase)
    ((50, 60), (22, 50), 0.0), ((80, 58), (106, 47), 1.1), ((41, 90), (14, 92), 2.3), ((88, 92), (113, 86), 3.0),
    ((40, 120), (20, 128), 4.2), ((57, 160), (32, 164), 5.0), ((72, 166), (101, 170), 0.6)]

POSE = [dict(f=0, bob=0, blink=0, peb=(0, 0), spark=0, glow=0, filings=0),
        dict(f=1, bob=1, blink=0, peb=(0, 0), spark=0, glow=0, filings=0),
        dict(f=2, bob=1, blink=1, peb=(0, 0), spark=0, glow=0, filings=0),
        dict(f=3, bob=0, blink=0, peb=(-2, -2), spark=0, glow=0, filings=0),
        dict(f=4, bob=0, blink=0, peb=(-3, -2), spark=0, glow=0, filings=0),
        dict(f=5, bob=0, blink=0, peb=(0, 0), spark=1, glow=0, filings=0),
        dict(f=6, bob=1, blink=0, peb=(0, 0), spark=0, glow=1, filings=1),
        dict(f=7, bob=0, blink=0, peb=(0, 0), spark=0, glow=0, filings=0)]


def magnekin(P):
    r = Rig(W, H)
    f, bob = P['f'], P['bob']
    cx = 64
    b = Body(1140)
    # legs: long, a little apart; big knee pebbles; elongated feet turned out
    for sx in (-1, 1):                                                       # his weight on the far leg, the near knee easy
        hip, knee, ank = ((cx - 7.5, 110), (cx - 8.5, 147), (cx - 11.5, 181)) if sx < 0 else ((cx + 7.5, 107), (cx + 10.0, 145), (cx + 10.5, 180))
        b.capsule(hip, knee, 6.4, 4.6, 0.0, tag='thigh')
        b.add(knee[0] + sx * 0.5, knee[1] - 1, 4.4, 3.8, 0.4, 0.14, 'iron', 1.2)                            # the knee
        b.capsule((knee[0], knee[1] + 3), ank, 4.4, 2.9, 0.0, tag='shin')
        b.capsule((ank[0], ank[1] + 2), (ank[0] + sx * 7, FLOOR - 2.2), 3.6, 2.8, 0.2, iron=0.5, tag='foot')
    # pelvis, belly, chest: a tapered column of pebbles (chest broad, a narrow waist)
    b.blob(cx, 104, 12.5, 8.0, 0.6, spacing=4.6, prad=(3.0, 4.2))
    b.blob(cx, 88, 9.0, 9.5, 0.8, spacing=3.8, prad=(2.2, 3.0), rust=0.08, iron=0.4)
    b.blob(cx + 0.5, 69 + bob, 17.0, 14.0, 1.0, spacing=5.8, prad=(3.8, 5.6), rust=0.24,
           clip=lambda x, y: y > 55 + bob + abs(x - cx) * 0.18)
    b.capsule((cx, 47 + bob), (cx, 57 + bob), 3.2, 4.0, 0.9, iron=0.6)                                       # the neck
    for sx in (-1, 1):                                                                                     # shoulder caps
        b.add(cx + sx * 15.5, 58 + bob, 5.4, 4.6, 0.3 * sx, 0.06 if sx < 0 else -0.08, 'rust' if sx < 0 else 'lode', 1.9,
              tag='shoulderL' if sx < 0 else 'shoulderR')
    # arms: hanging a little away from the body, the elbows by the waist, big hands with long fingers
    for sx in (-1, 1):
        sh, el, wr = ((cx - 18, 62 + bob), (cx - 24.5, 92), (cx - 22.5, 118)) if sx < 0 else ((cx + 18, 61 + bob), (cx + 23.0, 93), (cx + 26.0, 120))
        b.capsule(sh, el, 4.6, 3.4, 2.0, tag='upper%d' % sx)
        b.add(el[0], el[1], 3.4, 3.0, 0.0, 0.06, 'iron', 2.6)                                              # the elbow
        b.capsule(el, wr, 3.6, 2.6, 2.2, tag='fore%d' % sx)
        b.blob(wr[0] + sx * 0.5, wr[1] + 5, 4.6, 5.2, 2.8, spacing=3.4, prad=(1.8, 2.6), iron=0.3)           # the palm
        for k in range(4):                                                                                 # fingers
            fx = wr[0] + sx * 0.5 - 3.6 + k * 2.4
            b.capsule((fx, wr[1] + 8.5), (fx + sx * 0.6 - 0.3 * (k - 1.5), wr[1] + 16 - abs(k - 1.5) * 1.4), 1.6, 1.2, 3.0, iron=0.4, step=0.9)
        b.capsule((wr[0] - sx * 3.6, wr[1] + 3), (wr[0] - sx * 5.0, wr[1] + 9), 1.7, 1.3, 3.1, step=0.9)       # the thumb
    # the wire hoop over the head, behind it
    hx, hy = cx + 1, 31 + bob
    hoop = [(hx + 15.5 * math.cos(a), hy - 5 + 15.0 * math.sin(a)) for a in [math.pi * (0.92 + i / 60 * 1.12) for i in range(61)]]
    for (x, y) in hoop:
        r.stroke([(x, y)], 2.2, MATS['iron'], v=0.5 if x < hx else 0.3, group='hoop')
    for (x, y) in hoop[::3]: r.darken(x + 0.6, y - 0.6, -0.15)
    # the head: a lumpy ball
    hb = Body(77)
    for k in range(16):                                                      # a ring of pebbles rounds the skull off
        a = k / 16 * 2 * math.pi
        hb.add(hx + math.cos(a) * 10.2, hy + math.sin(a) * 10.6, 2.8, 2.5, a, 0.2 * (-math.cos(a) - math.sin(a)) * 0.5 - 0.1,
               hb.kind(0.2, 0.25), 3.5)
    hb.blob(hx, hy, 10.5, 11.0, 4.0, spacing=3.8, prad=(2.4, 3.4), rust=0.12, iron=0.25)
    jit = {'shoulderL': P['peb']}
    b.draw(r, jitter=jit)
    hb.draw(r)
    # the borrowed face: two rust plates for cheeks, eyes in dark rings, a slit of a mouth
    r.ellipsoid(hx - 6.0, hy + 4.8, 2.8, 2.0, MATS['rust'], lift=0.04, group='cheek')                     # one rust plate of a cheek
    for dx in range(-8, 9): r.darken(hx + dx, hy - 5 + (abs(dx) > 5), 0.25)                              # the brow's shadow
    r.ellipsoid(hx, hy + 2.5, 1.8, 2.8, MATS['iron'], lift=0.12, group='nose')
    eyes = []
    for sx in (-1, 1):
        ex, ey = hx + sx * 5.0, hy - 1.0
        for yy in range(int(ey) - 3, int(ey) + 4):
            for xx in range(int(ex) - 3, int(ex) + 4):
                d = math.hypot(xx + 0.5 - ex, yy + 0.5 - ey)
                if d <= 3.2: r.fixed(xx, yy, DARK)                                     # the socket ring
        eyes.append((ex, ey))
    for (ex, ey) in eyes:
        for yy in range(int(ey) - 2, int(ey) + 3):
            for xx in range(int(ex) - 2, int(ex) + 3):
                d = math.hypot(xx + 0.5 - ex, yy + 0.5 - ey)
                if d <= 2.0:
                    if P['blink']: r.fixed(xx, yy, LODE[4] if yy < ey else LODE[6])      # a lid of iron slides over
                    else: r.fixed(xx, yy, EYEW if d < 1.4 or yy < ey else EYEG)
        if not P['blink']: r.fixed(ex - 0.5, ey - 0.5, DARK)                           # the pupil
    for dx in range(-3, 3): r.fixed(hx + dx, hy + 7, DARK)                              # the mouth: a slit between pebbles
    r.fixed(hx - 4, hy + 6, LODE[2]); r.fixed(hx + 3, hy + 6, LODE[2])
    # cables looping round him (in front), and the tethers out to the satellites
    loops = [((cx - 17, 63 + bob), (cx - 2, 88), (cx + 15, 97)),           # shoulder across the chest to the far hip
             ((cx + 16, 66 + bob), (cx + 6, 74), (cx - 12, 81)),
             ((cx - 12, 101), (cx, 118), (cx + 12, 104)),                  # sagging round the hips
             ((cx - 9, 128), (cx + 3, 150), (cx + 11, 138)),               # a loop between the legs
             ((cx - 22, 82), (cx - 30, 98), (cx - 24, 106)),               # round the near elbow
             ((cx + 24, 100), (cx + 31, 110), (cx + 25, 114))]
    for (a, m, c) in loops:
        cable(r, bezier(a, m, c, 40))
    sats = []
    for i, (anc, rest, ph) in enumerate(SATS):
        a = ph + f * math.pi / 4
        sx_, sy_ = rest[0] + 1.6 * math.cos(a), rest[1] + 1.2 * math.sin(a * 1.3)
        if anc[1] < 70: anc = (anc[0], anc[1] + bob)
        mid = ((anc[0] + sx_) / 2, max(anc[1], sy_) + 6)                     # the tether sags
        cable(r, bezier(anc, mid, (sx_, sy_ + 2), 30), lit=2, shadow=False)
        sats.append((sx_, sy_, (f + i) % 2))
    for i, (x, y, fl) in enumerate(sats): satellite(r, x, y, fl, 'sat%d' % i)
    # tiny lit windows in the pebbles (the cities), flickering
    for (x, y, k) in b.windows + hb.windows:
        if abs(x - hx) < 9 and abs(y - hy) < 9: continue                     # not on the face
        on = h32(int(x * 3), int(y * 3), f // 2 + 9) % 5 != 0
        if not on: continue
        e = r.buf.get((int(x), int(y)))
        if e is None or (e[0] is None and e[3] in (EYEW, EYEG, DARK)): continue
        r.fixed(x, y, WINDOW[(k + f) % 3])
        if k == 0 and (int(x) + 1, int(y)) in r.buf: r.fixed(x + 1, y, WINDOW[0])
    # a glow round the eyes when they brighten; iron filings lifting from a sleeve; the spark
    if P['glow']:
        for (ex, ey) in eyes:
            for (dx, dy) in ((-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, -2), (-2, 2), (2, 2)):
                e = r.buf.get((int(ex + dx), int(ey + dy)))
                if e: r.fixed(ex + dx, ey + dy, (70, 104, 108))
    if P['filings']:
        for (dx, dy) in ((-27, 96), (-30, 100), (-28, 103), (-32, 95), (27, 104), (30, 99)):
            r.fixed(cx + dx, dy, LODE[6] if (dx + dy) % 2 else LODE[3])
    if P['spark']:
        a0, a1 = (cx - 17, 59), (cx - 9, 63)
        pts = [lerp(a0, a1, t / 7) for t in range(8)]
        for i, (x, y) in enumerate(pts):
            yy = y + (1 if i % 2 else -1) * (i not in (0, 7))
            r.fixed(x, yy, SPARK[2]); r.fixed(x, yy - 1, SPARK[1]); r.fixed(x + 1, yy + 1, SPARK[0])
    im = r.render(shadow=0.15, contact=0.16)
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y] == (18, 14, 12, 255): px[x, y] = WARMOUT + (255,)
    return im


# --------------------------------------------------------------------------------------------- the collapsed heap
BPOSE = [dict(f=0, spark=0, twitch=0, wing=0, win=0), dict(f=1, spark=1, twitch=0, wing=0, win=0),
         dict(f=2, spark=0, twitch=1, wing=0, win=0), dict(f=3, spark=0, twitch=0, wing=1, win=1)]
BH, BFLOOR = 64, 61


def broken(P):
    r = Rig(W, BH)
    b = Body(521)
    rnd = random.Random(7)
    # a dark oil slick under it
    for y in range(BFLOOR - 3, BFLOOR + 2):
        for x in range(14, 116):
            u, w = (x + 0.5 - 64) / 50.0, (y + 0.5 - (BFLOOR - 1.0)) / 2.4
            if u * u + w * w <= 1 and h32(x, y, 3) % 9: r.fixed(x, y, (16, 16, 20) if (x + y) % 5 else (40, 44, 56))
    # the heap: a low mound, bigger pebbles at the bottom, scattered ones round it
    b.blob(64, BFLOOR - 12, 30.0, 12.0, 0.0, spacing=5.0, prad=(3.2, 4.8), rust=0.3, iron=0.25,
           clip=lambda x, y: y < BFLOOR - 2)
    b.blob(60, BFLOOR - 22, 17.0, 8.0, 1.0, spacing=4.6, prad=(2.8, 4.2), rust=0.3, iron=0.2)
    for i in range(14):
        x = rnd.choice((rnd.uniform(18, 36), rnd.uniform(92, 112)))
        b.add(x, BFLOOR - rnd.uniform(1.5, 3.5), rnd.uniform(1.6, 3.0), rnd.uniform(1.4, 2.4), rnd.uniform(0, 3), rnd.uniform(-0.1, 0.05),
              b.kind(0.35, 0.3), 2.0 + rnd.random() * 0.1, tag='scatter%d' % i)
    b.add(80, BFLOOR - 25, 3.4, 3.0, 0.5, 0.05, 'iron', 2.5, tag='twitch')
    b.draw(r, jitter={'twitch': (1, -2) if P['twitch'] else (0, 0)})
    # the head has rolled onto the heap's left shoulder, the bent hoop still behind it; the eyes dead -- one keeps a flicker
    hx, hy = 41, BFLOOR - 27
    for i in range(22):
        a_ = math.pi * (0.95 + i / 21 * 0.75)
        r.stroke([(hx + 2 + 12.5 * math.cos(a_), hy - 1 + 12.0 * math.sin(a_))], 2.0, MATS['iron'], v=0.45, group='hoop')
    hb = Body(78)
    for k in range(14):
        a_ = k / 14 * 2 * math.pi
        hb.add(hx + math.cos(a_) * 7.4, hy + math.sin(a_) * 7.0, 2.4, 2.2, a_, 0.2 * (-math.cos(a_) - math.sin(a_)) * 0.5 - 0.1, hb.kind(0.2, 0.3), 3.5)
    hb.blob(hx, hy, 7.5, 7.0, 4.0, spacing=3.4, prad=(2.0, 2.8), rust=0.15, iron=0.3)
    hb.draw(r)
    for (ex, lit) in ((hx - 3.5, False), (hx + 3.5, P['win'] == 1)):
        ey = hy - 0.5
        for yy in range(int(ey) - 3, int(ey) + 4):
            for xx in range(int(ex) - 3, int(ex) + 4):
                d = math.hypot(xx + 0.5 - ex, yy + 0.5 - ey)
                if d <= 2.6: r.fixed(xx, yy, DARK)
                if d <= 1.4: r.fixed(xx, yy, (112, 140, 138) if lit else (46, 52, 56))
    for dx in range(-2, 3): r.fixed(hx + dx, hy + 4, DARK)
    # cables spilling out of it, tangled; a fallen satellite or two
    for (a, m, c) in (((40, BFLOOR - 12), (30, BFLOOR - 2), (18, BFLOOR - 5)), ((76, BFLOOR - 18), (96, BFLOOR - 4), (110, BFLOOR - 2)),
                      ((56, BFLOOR - 28), (66, BFLOOR - 40), (74, BFLOOR - 26)), ((62, BFLOOR - 8), (70, BFLOOR + 1), (84, BFLOOR - 6))):
        cable(r, bezier(a, m, c, 40))
    satellite(r, 24, BFLOOR - 6, P['wing'], 'satA', eye=False)
    satellite(r, 102, BFLOOR - 10, 0, 'satB', eye=P['win'] == 1)
    for (x, y, k) in b.windows[:6]:
        if P['win'] and k % 2 == 0: r.fixed(x, y, WINDOW[1])
    if P['spark']:
        pts = [lerp((70, BFLOOR - 20), (84, BFLOOR - 16), t / 9) for t in range(10)]
        for i, (x, y) in enumerate(pts):
            yy = y + (1 if i % 2 else -1) * (i not in (0, 9))
            r.fixed(x, yy, SPARK[2]); r.fixed(x, yy - 1, SPARK[1]); r.fixed(x + 1, yy + 1, SPARK[0])
    im = r.render(shadow=0.15, contact=0.16)
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y] == (18, 14, 12, 255): px[x, y] = WARMOUT + (255,)
    return im


def save_sheet(name, frames):
    os.makedirs(f'{OUT}/{name}', exist_ok=True)
    w, h = frames[0].size
    s = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        im.save(f'{OUT}/{name}/{i}.png'); s.paste(im, (i * w, 0))
    s.save(f'{OUT}/{name}.png')


if __name__ == '__main__':
    fr = [magnekin(p) for p in POSE]
    save_sheet('magnekin', fr)
    br = [broken(p) for p in BPOSE]
    save_sheet('magnekin_broken', br)
    used = set()
    for im in fr + br: used |= {px[:3] for px in im.getdata() if px[3]}
    ALL = [INK, WARMOUT, DARK, EYEW, EYEG] + LODE + IRONG + RUSTC + WIRE + WING + WINDOW + SPARK
    seen, rows = set(), []
    for c in ALL + sorted(used):
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/magnekin.gpl', 'w').write('GIMP Palette\nName: magnekin\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT, len(rows), 'colours')
