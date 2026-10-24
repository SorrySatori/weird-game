"""The protagonist -- the Obazoba apprentice -- redrawn at native resolution (rig.py renderer, the Edgar quality bar).
128x128 frames, facing right, soles on y 125 (the old 64x64 sprite was shown at scale 2, so the size on screen and the
feet line stay the same; the game now shows it at scale 1).
  0-3   idle: breath, the amulet's glow, a blink
  4-11  walk: an 8-frame cycle; the robe swings with the striding legs, the bell sleeves swing against the legs
        (elbows back), the pack and the tin mug on it bounce a little
Look kept from the old sprite: a travel-worn dark-brown hooded robe, a big leather pack with a bedroll, a green glowing
myceliar amulet on the chest, a rope belt with a pouch, a young pale face in the hood. Mud on the hem, a sewn patch.
python3 hero.py <outdir>  ->  priest.png (12 frames) + priest/<n>.png + hero.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK, h32, make_noise
from rig import Rig, Mat
from feral_toast import ik, lerp
from pal_symb import VEIN

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
ROBE = ramp('#120d0a #1c1510 #271d16 #33271d #403126 #4e3c2f #5e4939 #705745')
PACK = ramp('#1e120a #2e1c10 #422816 #58361e #6e4628 #865a34 #9e6e42')
SKIN = ramp('#3a2a24 #5a4034 #7a5846 #9a725a #b88c70 #d0a688 #e2bea0')
HAIR = ramp('#120e0c #1e1814 #2c241e #3a3028')
BOOT = ramp('#100c0a #1a1410 #261e18 #342a22 #44382e')
ROPE = ramp('#2a2014 #45361f #66512e #87703f #a48a52')
ROLL = ramp('#1e2420 #2c3630 #3e4a40 #566252 #707a66')
TIN  = ramp('#1c1c1e #2e2e32 #4a4a4e #6c6c70 #9a9a9c')
GLOW = [(40, 74, 46), (60, 122, 74)]                                   # the amulet's light on the robe
M = {'robe': Mat(ROBE, 'wool', 0.18), 'pack': Mat(PACK, 'leather', 0.18, 0.4), 'skin': Mat(SKIN, 'skin', 0.26, 0.2),
     'hair': Mat(HAIR, 'fur', 0.2), 'boot': Mat(BOOT, 'leather', 0.18, 0.5), 'rope': Mat(ROPE, 'fabric', 0.24),
     'roll': Mat(ROLL, 'wool', 0.22), 'tin': Mat(TIN, 'metal', 0.2, 0.6), 'legs': Mat(HAIR, 'fabric', 0.2)}
nMud = make_noise(3, 211, 160, 160)

def seam(r, group, dv):
    """a dark seam on whatever lies behind a volume of `group` (separates same-coloured cloth, e.g. a sleeve on the robe)"""
    hit = set()
    for (x, y), e in r.buf.items():
        if e[0] is None or r.groups[e[2]] != group: continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = r.buf.get((x + dx, y + dy))
            if q and q[0] is not None and q[2] < e[2] and r.groups[q[2]] != group: hit.add((x + dx, y + dy))
    for k in hit: r.buf[k][1] -= dv

def hero(P):
    r = Rig(128, 128)
    ph, walk, bob = P['ph'], P['walk'], P['bob']
    L = 2 if walk else 0                                               # the upper body leans into the walk
    H = 83 + bob                                                       # the waist
    feet = {}
    def leg(phase, far):
        if walk:
            foot = (60 + math.sin(phase) * 16, 125 - max(0.0, math.cos(phase)) * 5)
        else:
            foot = (55 if far else 64, 125)
        hip = (57 if far else 61, H + 4)
        knee = ik(hip, foot, 22, 21, 'right')                          # knees point forward
        g = 'legF' if far else 'legN'; lf = -0.22 if far else 0.0
        r.tube(hip, knee, 6.0, 5.0, M['legs'], lift=lf, group=g)
        ank = (foot[0], foot[1] - 4)
        r.tube(knee, lerp(knee, ank, 0.45), 4.6, 4.4, M['legs'], lift=lf, group=g)
        r.tube(lerp(knee, ank, 0.4), ank, 4.8, 4.4, M['boot'], lift=lf, group=g)
        r.ellipsoid(foot[0] + 3, foot[1] - 2.5, 6.6, 3.4, M['boot'], lift=lf, group=g)
        for k in range(6): r.fixed(foot[0] - 3 + k * 1.8, foot[1] - 0.2, BOOT[0])             # the sole
        feet[far] = foot
        return knee
    def sleeve(sh, hand, lift, g):
        e = ik(sh, hand, 17, 16, 'left')                               # elbows hang back
        r.tube(sh, e, 5.4, 5.2, M['robe'], lift=lift, group=g)
        r.tube(e, hand, 5.0, 6.6, M['robe'], lift=lift, group=g,      # a bell sleeve, a crease at the elbow
               folds=lambda t, s: -0.22 if t < 0.12 and s > 0 else (0.1 if t > 0.9 else 0))
        d = math.hypot(hand[0] - e[0], hand[1] - e[1]) or 1
        u = ((hand[0] - e[0]) / d, (hand[1] - e[1]) / d)
        r.ellipsoid(hand[0] + u[0] * 3, hand[1] + u[1] * 3, 3.0, 3.2, M['skin'], lift=lift, group=g + 'h')
        r.ellipsoid(hand[0] + u[0] * 1, hand[1] + u[1] * 1, 4.0, 4.0, M['robe'], lift=lift - 0.35, group=g,
                    clip=lambda x, y: (x - hand[0]) * u[0] + (y - hand[1]) * u[1] < 0.5)       # the cuff's dark inside

    leg(ph + math.pi, True)
    # the far arm swings opposite the far leg, behind the body
    sw = math.sin(ph) if walk else 0.0
    sleeve((59 + L, 47 + bob), (58 + L + sw * 10, 80 + bob - max(0.0, sw) * 3), -0.24, 'armF')
    # the pack: leather sack, flap, buckles, a bedroll on top, a tin mug hanging off the bottom
    pb = bob + (1 if walk and math.cos(ph * 2) < -0.3 else 0)
    r.ellipsoid(43 + L, 61 + pb, 12, 17.5, M['pack'], group='pack',
                vfun=lambda x, y, u, w: -0.2 if abs(u + 0.15) < 0.07 and w > -0.3 else 0)    # the seam
    r.poly([(33 + L, 51 + pb), (52 + L, 49 + pb), (54 + L, 61 + pb), (44 + L, 64 + pb), (33 + L, 63 + pb)], M['pack'], lift=0.12, round_=0.6, group='flap',
           vfun=lambda x, y: -0.25 if y == int(63 + pb) - 1 or (h32(x, y, 7) % 23 == 0) else 0)
    for bx in (38 + L, 47 + L):
        for k in range(5): r.fixed(bx, 61 + pb + k, PACK[1])                                   # straps
        r.fixed(bx - 1, 64 + pb, ROPE[4]); r.fixed(bx, 64 + pb, ROPE[4]); r.fixed(bx + 1, 64 + pb, ROPE[3]); r.fixed(bx, 65 + pb, ROPE[1])
    r.tube((33 + L, 40 + pb), (55 + L, 40 + pb), 5.6, 5.6, M['roll'], group='roll')
    r.ellipsoid(33 + L, 40 + pb, 3.2, 5.6, M['roll'], lift=-0.1, group='rollend',
                vfun=lambda x, y, u, w: -0.3 if abs(math.hypot(u, w) - 0.55) < 0.14 else 0)
    for sx in (39 + L, 50 + L):
        for k in range(-5, 6): r.fixed(sx, 40 + pb + k, PACK[1])
    mx = 34 + L + (1 if walk and sw > 0.5 else -1 if walk and sw < -0.5 else 0); my = 80 + pb
    for k in range(4): r.fixed(36 + L + (mx - 34 - L) * k / 4, 74 + pb + k, ROPE[1])
    r.tube((mx, my), (mx, my + 3), 3.4, 3.2, M['tin'], group='mug')
    r.ellipsoid(mx, my - 0.5, 3.4, 1.1, M['tin'], lift=-0.35, group='mug')
    for (dx, dy) in ((-4, 0), (-5, 1), (-5, 2), (-4, 3)): r.fixed(mx + dx, my + dy, TIN[1])  # the handle

    leg(ph, False)
    # the robe, one piece from the collar to the hem, flaring; it swings with the striding legs
    fx = max(79 + L, max(f[0] for f in feet.values()) + 7)
    bx = min(46 + L, min(f[0] for f in feet.values()) - 7)
    hem = 116 + bob
    gap = abs(sw) * 5 if walk else 0                                   # how far the hem lifts between the legs
    mid = (feet[True][0] + feet[False][0]) / 2
    pts = [(53 + L, 43 + bob), (70 + L, 42 + bob), (77 + L, 52 + bob), (78 + L, 68 + bob), (77 + L, H + 1), (fx, hem - 2)]
    n = 11
    for k in range(1, n):
        x = fx - (fx - bx) * k / n
        lift_ = gap * max(0.0, 1 - abs(x - mid) / 8)
        pts.append((x, hem + (2.5 if k % 2 else 0) + h32(k, int(ph * 7), 3) % 2 - lift_))
    pts += [(bx, hem - 3), (47 + L, H + 1), (48 + L, 58 + bob)]
    def robe_v(x, y):
        v = 0.0
        if y > H + 2:                                                  # folds fanning from the belt to the hem
            t = (y - H - 2) / max(1, hem - H - 2)
            for wx, hx in ((52, 0.15), (58, 0.4), (64, 0.62), (70, 0.85)):
                fxk = (wx + L) + ((bx + (fx - bx) * hx) - (wx + L)) * t
                if abs(x + 0.5 - fxk) < 0.7: v -= 0.24
                elif 0.7 <= x + 0.5 - fxk < 2.0: v += 0.08
            m = (y - (hem - 8)) / 8                                    # mud soaked up into the hem
            if m > 0: v -= m * 0.34 + (nMud(x, y) - 0.5) * 0.3
        elif (x + y // 3) % 9 == 0 and y > 52 + bob: v -= 0.14         # the chest's soft folds
        if h32(x // 2, (y - bob) // 2, 11) % 53 == 0: v += 0.14         # threadbare spots
        return v
    r.poly(pts, M['robe'], group='robe', vfun=robe_v)
    # a sewn patch on the skirt
    px, py = 58 + L, 97 + bob
    r.poly([(px, py), (px + 7, py - 1), (px + 8, py + 6), (px + 1, py + 7)], Mat(ROBE, 'fabric', 0.24), lift=0.06, group='patch')
    for k in range(0, 8, 2):
        r.fixed(px + k, py - (k > 3), ROPE[1]); r.fixed(px + 1 + k * 0.9, py + 7 - (k > 5), ROPE[1])
    # the pack's strap over the shoulder, the rope belt, the pouch
    for k in range(26):
        t = k / 25
        r.fixed(57 + L + t * 9, 44 + bob + t * 37, PACK[2] if k % 5 else PACK[1]); r.fixed(58 + L + t * 9, 44 + bob + t * 37, PACK[3])
    r.tube((47 + L, H + 2), (78 + L, H + 2), 1.7, 1.7, M['rope'], group='belt')
    r.ellipsoid(71 + L, H + 9, 4.4, 5.0, M['pack'], group='pouch', vfun=lambda x, y, u, w: -0.3 if w < -0.45 else 0)
    for k in range(6): r.fixed(76 + L + (k % 2) * 0.7, H + 3 + k, ROPE[3 if k % 2 else 2])     # the knot's tails
    # the myceliar amulet on a cord -- a knot of green light
    for k in range(10): r.fixed(70 + L + k * 0.4, 44 + bob + k, ROPE[1])
    ax, ay = 74 + L, 58 + bob
    if P['glow']:
        for dy in range(-6, 7):
            for dx in range(-5, 6):
                d = math.hypot(dx * 1.2, dy)
                if 3.6 < d < 5.6 and (dx + dy) % 2 == 0: r.fixed(ax + dx, ay + dy, GLOW[0])
                elif 3.0 < d <= 3.6: r.fixed(ax + dx, ay + dy, GLOW[1])
    for dy in range(-3, 4):                                            # a 5x7 knot, lit from the top left
        w = 2 - (abs(dy) + 1) // 2
        for dx in range(-w, w + 1):
            r.fixed(ax + dx, ay + dy, VEIN[0] if abs(dx) == w and w else (VEIN[2] if dx + dy < 0 else VEIN[1]))
    r.fixed(ax, ay - 1, VEIN[3]); r.fixed(ax - 1, ay, VEIN[3])
    if P['glow']: r.fixed(ax, ay, (210, 255, 220)); r.fixed(ax, ay - 2, VEIN[3])
    # the head: a deep hood with a tail hanging down the back, a young pale face, a dark fringe, the hood's worn rim
    hx, hy = 69 + L + (1 if walk else 0), 23 + bob
    r.ellipsoid(hx - 4, hy + 17, 12, 5.5, M['robe'], group='cowl')
    r.poly([(hx - 12, hy - 4), (hx - 6, hy - 6), (hx - 9, hy + 12), (hx - 16, hy + 20), (hx - 15, hy + 8)], M['robe'], lift=-0.06, group='hood')
    r.ellipsoid(hx - 2, hy, 12.5, 14.5, M['robe'], lift=0.04, group='hood',
                vfun=lambda x, y, u, w: -0.2 if abs(math.atan2(w, u + 0.5) * 3 % 1 - 0.5) < 0.05 and u < 0.2 else 0)
    r.ellipsoid(hx + 4, hy + 2, 8.6, 10.6, M['robe'], lift=-0.62, group='hoodin')
    r.ellipsoid(hx + 5.5, hy + 3.5, 6.0, 7.8, M['skin'], group='face',
                vfun=lambda x, y, u, w: -0.24 if w < -0.5 else (-0.12 if u < -0.55 else 0))         # brow + cheek under the hood
    r.ellipsoid(hx + 11.2, hy + 3.2, 1.2, 1.5, M['skin'], lift=0.1, group='face')               # the nose
    r.poly([(hx + 1, hy - 6), (hx + 9, hy - 6), (hx + 11, hy - 2), (hx + 9, hy - 2), (hx + 8, hy), (hx + 6, hy - 2), (hx + 4, hy + 1), (hx + 1, hy + 4)],
           M['hair'], group='hair')                                                              # a fringe falling to the brow
    if P['blink']:
        r.fixed(hx + 8, hy + 2, SKIN[2]); r.fixed(hx + 9, hy + 2, SKIN[2])
    else:
        r.fixed(hx + 8, hy + 1, HAIR[0]); r.fixed(hx + 9, hy + 1, HAIR[1]); r.fixed(hx + 8, hy + 2, HAIR[0]); r.fixed(hx + 9, hy + 2, (226, 222, 210))
    r.fixed(hx + 9, hy + 7, SKIN[2])                                                             # the mouth
    for k in range(12):                                                                          # the hood's rim
        a = -2.6 + k * 0.2
        r.fixed(hx + 4 + math.cos(a) * 9.6, hy + 2 + math.sin(a) * 11.6, ROBE[6 if k % 4 else 5])
    r.poly([(hx - 9, hy - 10), (hx + 3, hy - 14), (hx + 11, hy - 9), (hx + 12, hy - 5), (hx + 3, hy - 8)], M['robe'], lift=0.14, group='hoodtop')
    # the near arm in front, swinging against the near leg
    sleeve((66 + L, 50 + bob), (68 + L - sw * 11, 81 + bob - max(0.0, -sw) * 3), 0.06, 'armN')
    seam(r, 'armN', 0.28); seam(r, 'hoodtop', 0.12); seam(r, 'pouch', 0.15)
    return r.render()

IDLE = [dict(ph=0.0, walk=False, bob=0, blink=False, glow=False), dict(ph=0.0, walk=False, bob=1, blink=False, glow=True),
        dict(ph=0.0, walk=False, bob=1, blink=False, glow=False), dict(ph=0.0, walk=False, bob=0, blink=True, glow=False)]
# the body is lowest just after each contact (legs spread) and highest on the passing pose
WALK = [dict(ph=i * math.pi / 4, walk=True, bob=int(round(2 * abs(math.sin(i * math.pi / 4 - 0.5)))), blink=False, glow=(i % 4 == 0)) for i in range(8)]

if __name__ == '__main__':
    os.makedirs(f'{OUT}/priest', exist_ok=True)
    frames = [hero(p) for p in IDLE + WALK]
    sheet = Image.new('RGBA', (128 * len(frames), 128), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        im.save(f'{OUT}/priest/{i}.png'); sheet.paste(im, (i * 128, 0))
    sheet.save(f'{OUT}/priest.png')
    ALL = [INK] + ROBE + PACK + SKIN + HAIR + BOOT + ROPE + ROLL + TIN + VEIN + GLOW
    seen, rows = set(), []
    for c in ALL:
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/hero.gpl', 'w').write('GIMP Palette\nName: hero\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT)
