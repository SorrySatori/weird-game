"""Gnur, the Rust Choir's money man in Shed 521, redrawn at native resolution (rig.py renderer, the Edgar quality bar)
after his old AI sheet (Gnur2.png, 582x982 frames squashed to 80x80 in the scene). The look is kept: a moss-green hooded
robe, a ragged ochre mantle over the shoulders, no face in the hood but darkness and two yellow eyes. Drawn into it:
a stooped old machinist (he "kept the machines running in the old days"); the eyes are two little amber lamps; where a
mouth would be, a corroded brass speaker grille (his voice "crackles like a broken transistor radio") with a copper lead into the
collar; the near arm hangs as the protagonist's does, a bell sleeve under the mantle, the hand at his belt an iron prosthesis (he
deals in body upgrades), the far hand is bandaged; a leather tool roll
on the back hip; trade goods on cords at the belt (a pre-war lens -- he sold the Bishop hers -- and a brass cog);
rust soaked into the hem, a sewn patch. 128x128 frames, facing right, soles on y 125 (the protagonist's format):
  0-3   idle: 0 rest  1 a breath (the shoulders rise)  2 the eye-lamps flicker down  3 the grille crackles (a spark)
        and the iron fingers curl
  4-11  walk: an 8-frame stooped shuffle; the robe swings with the legs, the trinkets swing on their cords
python3 gnur.py <outdir>  ->  gnur.png (12 frames) + gnur/<n>.png + gnur.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK, h32, make_noise
from rig import Rig, Mat, nF
from feral_toast import ik, lerp
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
ROBE  = ramp('#0e140f #151d16 #1c271e #243226 #2d3e2f #374b38 #425843 #4f664f #5d745b')
STAIN = ramp('#150f0a #20160e #2c1f12 #382817 #45321c #513c22 #5e4629 #6a5030 #765a37')   # rust soaked into the same wool
MANT  = ramp('#211a10 #322717 #45361f #594627 #6d5732 #82693e #967b4c #aa8e5c #bca06d')
GRIME = ramp('#1c150d #2a2013 #3a2c1a #4a3821 #5a4529 #6a5232 #7a5f3b #8a6c45 #9a7a50')    # the mantle, oil-dark
VOID  = ramp('#040605 #080b09 #0d110e #131814')
BRASS = ramp('#24190b #3d2c12 #5c441c #7c5e28 #9c7a36 #bb9748 #d6b462')
COPP  = ramp('#2a130b #4a2414 #6e381f #92502c #b06a3c #c9874f')
VERD  = [(40, 70, 58), (62, 104, 86), (96, 140, 116)]
IRON  = ramp('#121314 #1d1f21 #2a2d30 #3a3e42 #4d5257 #63696e #7d8388')
WRAP  = ramp('#141110 #1e1915 #2a231d #382e26 #463a30 #57493c #6a5a4b #7e6d5c')
LEATH = ramp('#170f0a #23170f #312015 #402a1b #4f3422 #5f3f2a #6f4b33')
CORD  = ramp('#241a10 #3b2c1a #574227 #735a36')
WOOD  = ramp('#24150c #3a2314 #55341d #6e4527')
EYE   = [(92, 54, 8), (176, 116, 18), (240, 186, 40), (255, 226, 110), (255, 246, 200)]
GLASS = [(28, 38, 36), (52, 74, 66), (96, 128, 112), (170, 196, 176), (236, 244, 230)]

def burlap(x, y):                                                      # coarse sackcloth: weave + slubs
    return (nF(x * 1.8, y * 1.8) - 0.5) * 0.12 + (0.05 if x % 2 == 0 and y % 2 == 0 else (-0.04 if (x + y) % 2 else 0))

M = {'robe': Mat(ROBE, 'wool', 0.18), 'mant': Mat(MANT, 'fabric', 0.2), 'void': Mat(VOID, 'plain', 0.1),
     'iron': Mat(IRON, 'metal', 0.22, 0.7), 'brass': Mat(BRASS, 'metal', 0.24, 0.8), 'copp': Mat(COPP, 'metal', 0.22, 0.7),
     'wrap': Mat(WRAP, 'fabric', 0.22), 'leath': Mat(LEATH, 'leather', 0.2, 0.4), 'wood': Mat(WOOD, 'wood', 0.22)}
M['mant'].tex = burlap
nRust, nBlot = make_noise(4, 311, 160, 160), make_noise(7, 312, 160, 160)
ROBE_I = {c: i for i, c in enumerate(ROBE)}
MANT_I = {c: i for i, c in enumerate(MANT)}


def cog(r, cx, cy):
    """a 7x7 brass cog with a hole"""
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            d = math.hypot(dx, dy)
            tooth = (abs(dx) == 3 and dy == 0) or (abs(dy) == 3 and dx == 0) or (abs(dx) == 2 and abs(dy) == 2)
            if d < 1: r.fixed(cx + dx, cy + dy, VOID[1])
            elif d < 2.5 or tooth: r.fixed(cx + dx, cy + dy, BRASS[5] if dx + dy < -1 else (BRASS[3] if dx + dy < 2 else BRASS[1]))


def lens(r, cx, cy, glint):
    """the pre-war lens: a glass disc in a brass bezel"""
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            d = math.hypot(dx, dy)
            if d > 3.3: continue
            if d > 2.4: c = BRASS[5] if dx + dy < 0 else BRASS[2]
            else: c = GLASS[3] if dx + dy < -1 else (GLASS[2] if dx + dy < 1 else GLASS[1])
            r.fixed(cx + dx, cy + dy, c)
    r.fixed(cx - 1, cy - 1, GLASS[4] if glint else GLASS[3])


def gnur(P):
    r = Rig(128, 128)
    ph, walk, bob = P['ph'], P['walk'], P['bob']
    L = 1 if walk else 0                                               # the stoop leans a little further into the walk
    H = 85 + bob                                                       # the waist (the belt)
    br = P['breath']                                                   # the shoulders and the hood rise on the breath
    feet = {}

    def leg(phase, far):
        if walk:
            foot = (63 + math.sin(phase) * 11, 125 - max(0.0, math.cos(phase)) * 3)
        else:
            foot = (57 if far else 67, 125)
        hip = (58 if far else 63, H + 6)
        knee = ik(hip, foot, 18, 19, 'right')                          # knees forward, bent: a shuffle
        g = 'legF' if far else 'legN'; lf = -0.24 if far else 0.0
        r.tube(hip, knee, 5.6, 4.6, M['wrap'], lift=lf - 0.2, group=g)
        ank = (foot[0], foot[1] - 4)
        r.tube(knee, ank, 4.6, 4.2, M['wrap'], lift=lf, group=g,
               folds=lambda t, s: -0.24 if int(t * 7) % 2 == 0 and t > 0.25 else 0.04)                     # rag bindings
        r.ellipsoid(foot[0] + 3, foot[1] - 2.5, 6.4, 3.4, M['wrap'], lift=lf - 0.08, group=g,
                    vfun=lambda x, y, u, w: -0.2 if (x + y) % 4 == 0 else 0)
        for k in range(6): r.fixed(foot[0] - 3 + k * 1.8, foot[1] - 0.2, WRAP[0])                          # the sole
        feet[far] = foot

    def bandaged(hand, u, lift, g):
        r.ellipsoid(hand[0] + u[0] * 3, hand[1] + u[1] * 3, 3.0, 3.4, M['wrap'], lift=lift + 0.1, group=g + 'h',
                    vfun=lambda x, y, uu, w: -0.22 if (y - x) % 3 == 0 else 0)

    def iron_hand(hand, u, curl, lift, g):
        wx, wy = hand[0] + u[0] * 1.5, hand[1] + u[1] * 1.5
        r.tube((wx - u[0] * 1.2, wy - u[1] * 1.2), (wx + u[0] * 0.8, wy + u[1] * 0.8), 2.6, 2.6, M['brass'], lift=lift, group=g + 'w')   # the brass wrist collar
        px, py = hand[0] + u[0] * 4.5, hand[1] + u[1] * 4.5
        r.ellipsoid(px, py, 3.4, 3.0, M['iron'], lift=lift + 0.05, group=g + 'h')                       # the back-of-hand plate
        for k in range(4):                                                                              # four jointed fingers
            bx, by = px - 1.4 + k * 1.6, py + 1.8
            ln = 5.0 - (k == 0) * 0.6 - (k == 3) * 1.0
            if curl:
                mid = (bx + 1.4, by + ln * 0.5); tip = (bx + 0.2, by + ln * 0.75)
            else:
                mid = (bx + 0.6 + k * 0.2, by + ln * 0.55); tip = (bx + 1.4 + k * 0.3, by + ln)
            r.tube((bx, by), mid, 1.05, 0.95, M['iron'], lift=lift + 0.1, group=g + 'f%d' % k)
            r.tube(mid, tip, 0.95, 0.8, M['iron'], lift=lift + 0.1, group=g + 'f%d' % k)
            r.fixed(mid[0], mid[1], BRASS[5] if k % 2 else BRASS[4])                                     # a brass knuckle pin
        r.tube((px - 3.0, py - 1.0), (px - 3.8, py + 2.8), 1.1, 0.9, M['iron'], lift=lift, group=g + 't')  # the thumb
        r.fixed(px, py - 1, IRON[6]); r.fixed(px + 1, py - 1, IRON[5])

    def peek_hand(hand, u, curl, lift, g):
        """only the iron fingertips show under the cuff (and a glint of the brass wrist)"""
        nx, ny = -u[1], u[0]
        for k in (-1, 0, 1):
            bx, by = hand[0] + u[0] * 1.2 + nx * k * 1.5, hand[1] + u[1] * 1.2 + ny * k * 1.5
            ln = (1.4 if curl else 2.8) - (abs(k) * 0.5)
            r.tube((bx, by), (bx + u[0] * ln + (0.6 if curl else 0), by + u[1] * ln), 0.85, 0.75, M['iron'], lift=lift + 0.15, group=g + 'f%d' % k)
        r.fixed(hand[0] - nx * 2.2, hand[1] - ny * 2.2, BRASS[5])

    def drape_sleeve(sh, hand, lift, g, curl, l1, l2):
        """a wide, flowing bell sleeve that hangs past the hand: the arm is only guessed at under the cloth, the iron
        fingertips just show in the shadow under its ragged hem"""
        e = ik(sh, hand, l1, l2, 'left')
        d = math.hypot(hand[0] - e[0], hand[1] - e[1]) or 1
        u = ((hand[0] - e[0]) / d, (hand[1] - e[1]) / d)
        hem = (hand[0] + u[0] * 3, hand[1] + u[1] * 3)
        r.tube(sh, e, 5.6, 6.0, M['robe'], lift=lift, group=g,
               folds=lambda t, s_: -0.26 if abs(s_ - 0.35) < 0.09 else 0)
        r.tube(e, hem, 6.0, 9.2, M['robe'], lift=lift, group=g, jag=0.05,
               folds=lambda t, s_: -0.3 if (abs(s_ + 0.4) < 0.08 or abs(s_ - 0.25) < 0.08) and t > 0.15 else (0.12 if abs(s_ + 0.1) < 0.1 else 0))
        r.ellipsoid(hem[0], hem[1], 2.2, 7.4, M['robe'], rot=math.atan2(u[1], u[0]), lift=lift - 0.55, group=g + 'in')   # the dark opening
        nx, ny = -u[1], u[0]
        for k in (-1, 0, 1):                                            # the fingertips, just peeking out
            bx, by = hem[0] - u[0] * 0.5 + nx * k * 1.6, hem[1] - u[1] * 0.5 + ny * k * 1.6
            ln = (1.0 if curl else 2.0) - abs(k) * 0.4
            r.tube((bx, by), (bx + u[0] * ln + (0.5 if curl else 0), by + u[1] * ln), 0.85, 0.75, M['iron'], lift=lift + 0.15, group=g + 'f%d' % k)
        r.fixed(hem[0] - nx * 2.6, hem[1] - ny * 2.6 - u[1], BRASS[5])                                         # a glint of the brass wrist

    def hero_sleeve(sh, hand, lift, g, curl):
        """the protagonist's arm (hero.py): a bell sleeve, the elbow hanging back, the hand out of the cuff -- here an iron one"""
        e = ik(sh, hand, 17, 16, 'left')
        r.tube(sh, e, 5.4, 5.2, M['robe'], lift=lift, group=g)
        r.tube(e, hand, 5.0, 6.6, M['robe'], lift=lift, group=g,
               folds=lambda t, s_: -0.22 if t < 0.12 and s_ > 0 else (0.1 if t > 0.9 else 0))
        d = math.hypot(hand[0] - e[0], hand[1] - e[1]) or 1
        u = ((hand[0] - e[0]) / d, (hand[1] - e[1]) / d)
        r.ellipsoid(hand[0] + u[0] * 3, hand[1] + u[1] * 3, 3.0, 3.2 if not curl else 2.7, M['iron'], lift=lift + 0.1, group=g + 'h')
        r.fixed(hand[0] + u[0] * 3 - 1, hand[1] + u[1] * 3 - 1, IRON[6])                                       # a glint on the knuckles
        r.fixed(hand[0] + u[0] * 2 + 1.5, hand[1] + u[1] * 2, BRASS[5])                                         # the brass wrist joint
        r.ellipsoid(hand[0] + u[0] * 1, hand[1] + u[1] * 1, 4.0, 4.0, M['robe'], lift=lift - 0.35, group=g,
                    clip=lambda x, y: (x - hand[0]) * u[0] + (y - hand[1]) * u[1] < 0.5)                        # the cuff's dark inside

    def sleeve(sh, hand, lift, g, kind, curl=False, l1=14, l2=13):
        e = ik(sh, hand, l1, l2, 'left')                               # elbows hang back
        r.tube(sh, e, 4.4, 4.0, M['robe'], lift=lift, group=g)
        r.tube(e, hand, 4.0, 5.4, M['robe'], lift=lift, group=g,      # a wide sleeve, a crease at the elbow
               folds=lambda t, s: -0.24 if t < 0.14 and s > 0 else (0.1 if t > 0.88 else 0))
        d = math.hypot(hand[0] - e[0], hand[1] - e[1]) or 1
        u = ((hand[0] - e[0]) / d, (hand[1] - e[1]) / d)
        if kind == 'iron': iron_hand(hand, u, curl, lift, g)
        elif kind == 'peek': peek_hand(hand, u, curl, lift, g)
        else: bandaged(hand, u, lift, g)
        r.ellipsoid(hand[0] + u[0] * 1, hand[1] + u[1] * 1, 3.4, 3.4, M['robe'], lift=lift - 0.35, group=g,
                    clip=lambda x, y: (x - hand[0]) * u[0] + (y - hand[1]) * u[1] < 0.5)                  # the cuff's dark inside

    sw = math.sin(ph) if walk else 0.0
    leg(ph + math.pi, True)
    # the far arm, behind the body: hangs, the bandaged hand swings a little against the far leg
    sleeve((60 + L, 58 + bob), (60 + L + sw * 6, 86 + bob - max(0.0, sw) * 2), -0.26, 'armF', 'wrap')
    # the tool roll on the back hip: rolled leather, a strap, a screwdriver's wooden handle and a copper pipe poking out
    tb = bob + (1 if walk and math.cos(ph * 2) < -0.3 else 0)
    r.tube((42 + L, H - 8 + tb), (40 + L, H - 13 + tb), 1.1, 1.1, M['iron'], group='tools')                  # a spanner's shank
    for (dx, dy) in ((-2, -1), (-1, -1), (1, -1), (2, -1), (-2, 0), (2, 0)): r.fixed(40 + L + dx, H - 14 + tb + dy, IRON[4] if dy < 0 else IRON[2])
    r.tube((46 + L, H - 8 + tb), (46 + L, H - 13 + tb), 1.5, 1.4, M['wood'], group='tools')                   # a screwdriver's handle
    r.ellipsoid(43 + L, H + 1 + tb, 6.4, 9.6, M['leath'], group='roll',
                vfun=lambda x, y, u, w: -0.24 if abs(w + 0.1) < 0.08 or abs(w - 0.5) < 0.08 else 0)        # the rolled layers
    for k in range(-8, 9): r.fixed(43 + L + (k > 4), H + 1 + tb + k, LEATH[1])
    leg(ph, False)

    # the robe: one piece from the hump to the hem, flaring; it swings with the legs
    fx = max(86 + L, max(f[0] for f in feet.values()) + 6)
    bx = min(46 + L, min(f[0] for f in feet.values()) - 6)
    hem = 115 + bob
    gap = abs(sw) * 4 if walk else 0
    mid = (feet[True][0] + feet[False][0]) / 2
    pts = [(52 + L, 46 + bob), (66 + L, 42 + bob), (80 + L, 50 + bob), (85 + L, 62 + bob), (86 + L, 76 + bob), (85 + L, H + 2), (fx, hem - 2)]
    n = 13
    for k in range(1, n):
        x = fx - (fx - bx) * k / n
        lift_ = gap * max(0.0, 1 - abs(x - mid) / 8)
        pts.append((x, hem + (2.5 if k % 2 else 0) + h32(k, int(ph * 7), 3) % 2 - lift_))
    pts += [(bx, hem - 3), (44 + L, H + 2), (43 + L, 66 + bob), (46 + L, 54 + bob)]

    def robe_v(x, y):
        v = 0.0
        if y > H + 2:                                                  # folds fanning from the belt to the hem
            t = (y - H - 2) / max(1, hem - H - 2)
            for wx, hx_ in ((52, 0.12), (59, 0.36), (66, 0.6), (74, 0.82), (80, 0.95)):
                fxk = (wx + L) + ((bx + (fx - bx) * hx_) - (wx + L)) * t
                if abs(x + 0.5 - fxk) < 0.7: v -= 0.24
                elif 0.7 <= x + 0.5 - fxk < 2.0: v += 0.08
        elif y < 70 + bob and x < 54 + L: v += 0.06                   # the hump catches the light
        elif (x + y // 3) % 9 == 0 and y > 60 + bob: v -= 0.14
        if h32(x // 2, (y - bob) // 2, 11) % 47 == 0: v += 0.14        # threadbare spots
        return v
    r.poly(pts, M['robe'], group='robe', vfun=robe_v)
    # a sewn patch on the skirt's back
    qx, qy = 50 + L, 98 + bob
    r.poly([(qx, qy), (qx + 8, qy - 1), (qx + 8, qy + 7), (qx + 1, qy + 8)], Mat(ROBE, 'fabric', 0.26), lift=0.1, group='patch')
    for k in range(0, 9, 2):
        r.fixed(qx + k, qy - (k > 4), CORD[2]); r.fixed(qx + 1 + k * 0.8, qy + 8 - (k > 5), CORD[2])
        r.fixed(qx + (k > 4) * 8, qy + k * 0.9, CORD[1])
    # the rope belt, slanting with the stoop; the trinkets on cords
    r.tube((44 + L, H + 3), (85 + L, H + 1), 1.6, 1.6, Mat(CORD, 'fabric', 0.24), group='belt')
    for k in range(5): r.fixed(48 + L + (k % 2) * 0.7, H + 4 + k, CORD[3 if k % 2 else 2])               # the knot's tails

    # the near arm: the protagonist's bell sleeve, its shoulder under the mantle, so only the forearm and the iron hand show
    hero_sleeve((70 + L, 56 + bob - br), (72 + L - sw * 6, 84 + bob - max(0.0, -sw) * 3), 0.06, 'armN', P['curl'])
    # the trinkets hang at the front of the belt, over the sleeve
    s1, s2 = (math.sin(ph + 0.6) * 2.2 if walk else 0), (math.sin(ph + 1.2) * 1.8 if walk else 0)
    for k in range(9): r.fixed(80 + L + s1 * k / 9, H + 2 + k, CORD[1])
    lens(r, 80 + L + s1, H + 14, P['glint'])
    for k in range(6): r.fixed(74 + L + s2 * k / 6, H + 2 + k, CORD[1])
    cog(r, 74 + L + s2, H + 11)
    for k in range(4): r.fixed(69 + L, H + 3 + k, CORD[1])                                              # a paper tag
    for dy in range(4):
        for dx in range(3): r.fixed(68 + L + dx, H + 7 + dy, (178, 166, 132) if (dx + dy) % 3 else (150, 138, 108))

    # the mantle: ragged sackcloth round the shoulders, open under the chin
    m = bob - br
    mp = [(46 + L, 50 + m), (54 + L, 42 + m), (68 + L, 39 + m), (82 + L, 45 + m), (88 + L, 54 + m), (89 + L, 63 + m)]
    teeth = [(89, 63), (86, 67), (83, 64), (79, 69), (75, 65), (71, 70), (66, 66), (62, 70), (57, 66), (53, 69), (49, 64), (45, 66)]
    mp += [(x + L, y + m + (h32(x, 9) % 2)) for (x, y) in teeth]
    mp += [(42 + L, 58 + m)]

    def mant_v(x, y):
        v = 0.0
        if (x * 2 + y) % 11 == 0 and y > 48 + m: v -= 0.16            # sackcloth folds hanging off the shoulder
        if y < 47 + m and x > 70 + L: v -= 0.12                        # the hood's shadow on the collar
        return v
    r.poly(mp, M['mant'], round_=0.75, tilt=-0.15, group='mant', vfun=mant_v)
    # the tool roll's strap over the mantle, from the near shoulder to the back hip
    for k in range(30):
        t = k / 29
        x0, y0 = 76 + L - t * 30, 48 + m + t * (H - 10 - 48 - m + tb - bob + bob)
        r.fixed(x0, y0, LEATH[2] if k % 6 else LEATH[1]); r.fixed(x0, y0 + 1, LEATH[3])

    # the head: a deep hood with a drooping tail, darkness inside, two lamp-eyes, a speaker grille
    hx, hy = 73 + L, 36 + bob - br
    r.ellipsoid(hx - 3, hy + 14, 12, 5.2, M['robe'], group='cowl')
    r.poly([(hx - 11, hy - 5), (hx - 5, hy - 7), (hx - 9, hy + 10), (hx - 17, hy + 20), (hx - 18, hy + 9)], M['robe'], lift=-0.06, group='hood')
    r.ellipsoid(hx - 1, hy, 13.4, 14.4, M['robe'], lift=0.04, group='hood',
                vfun=lambda x, y, u, w: -0.2 if abs(math.atan2(w, u + 0.5) * 3 % 1 - 0.5) < 0.05 and u < 0.2 else 0)
    r.ellipsoid(hx + 4.5, hy + 2, 9.2, 10.8, M['void'], group='hoodin',
                vfun=lambda x, y, u, w: -0.3 if w < -0.3 else 0)
    for k in range(13):                                                                                 # the hood's worn rim
        a = -2.7 + k * 0.2
        r.fixed(hx + 4.5 + math.cos(a) * 10.2, hy + 2 + math.sin(a) * 11.8, ROBE[7 if k % 4 else 6])
    r.poly([(hx - 10, hy - 10), (hx + 2, hy - 15), (hx + 11, hy - 10), (hx + 13, hy - 6), (hx + 3, hy - 9)], M['robe'], lift=0.14, group='hoodtop')
    # the eye-lamps: a near and a far one, a faint glow on the dark round them
    fl = P['flick']
    for (ex, ey, far) in ((hx + 5, hy - 1, False), (hx + 10, hy - 1, True)):
        if fl:
            core, hi, halo = EYE[1], EYE[2], None
        else:
            core, hi, halo = EYE[2] if not far else EYE[1], EYE[4] if not far else EYE[3], EYE[0]
        if halo:
            for (dx, dy) in ((-1, 0), (2, 0), (0, -1), (1, -1), (0, 2), (1, 2)):
                if not (far and dx == 2): r.fixed(ex + dx, ey + dy, halo)
        r.fixed(ex, ey, hi); r.fixed(ex + 1, ey, core); r.fixed(ex, ey + 1, core)
        r.fixed(ex + 1, ey + 1, EYE[1] if not fl else EYE[0])
    # the speaker grille where a mouth would be: a brass oval, verdigris at the bottom, holes in a mesh
    gx, gy = hx + 7, hy + 7
    lit = P['crack']
    for dy in range(-2, 3):
        for dx in range(-3, 4):
            if (dx / 3.1) ** 2 + (dy / 2.2) ** 2 > 1: continue
            edge = (dx / 2.1) ** 2 + (dy / 1.3) ** 2 > 1
            if edge: c = VERD[1] if dy > 0 and dx < 1 else (BRASS[5] if dy < 0 else BRASS[3])
            elif (dx + dy) % 2 == 0: c = EYE[2] if lit and (dx, dy) in ((0, 0), (-1, 1), (1, -1)) else VOID[0]
            else: c = BRASS[2] if dy >= 0 else BRASS[4]
            r.fixed(gx + dx, gy + dy, c)
    r.fixed(gx - 2, gy + 2, VERD[0]); r.fixed(gx + 2, gy + 2, VERD[2])
    if lit:                                                                                             # the crackle: a spark
        for (dx, dy, c) in ((5, -2, EYE[4]), (6, -3, EYE[3]), (5, 1, EYE[3]), (7, 0, EYE[2])): r.fixed(gx + dx, gy + dy, c)

    # the near arm in front: the iron hand held forward, a dealer's fidget; it swings against the near leg
    seam(r, 'armN', 0.14); seam(r, 'hoodtop', 0.12); seam(r, 'mant', 0.16); seam(r, 'patch', 0.1)
    im = r.render()

    # rust and oil soaked into the cloth: robe pixels near the hem and in blotches go rust-brown, the mantle gets grime
    p = im.load()
    for y in range(128):
        for x in range(128):
            c = p[x, y][:3]
            if p[x, y][3] == 0: continue
            if c in ROBE_I:
                i = ROBE_I[c]
                depth = (y - (hem - 11)) / 11 + (nRust(x - L, y) - 0.5) * 0.9
                drip = y > H + 3 and h32((x - L) // 2, 77) % 17 == 0 and y < H + 6 + h32((x - L) // 2, 78) % 9 - ((x - L) % 2) * 3
                if depth > 0.45 or drip: p[x, y] = STAIN[i] + (255,)
            elif c in MANT_I:
                i = MANT_I[c]
                if nBlot(x * 1.3 - L, y * 1.3 - bob + 40) > 0.8 or (y > 63 + m and nRust(x, y) > 0.6): p[x, y] = GRIME[i] + (255,)
    return im


IDLE = [dict(ph=0.0, walk=False, bob=0, breath=0, flick=False, crack=False, curl=False, glint=False),
        dict(ph=0.0, walk=False, bob=0, breath=1, flick=False, crack=False, curl=False, glint=True),
        dict(ph=0.0, walk=False, bob=0, breath=0, flick=True, crack=False, curl=False, glint=False),
        dict(ph=0.0, walk=False, bob=0, breath=0, flick=False, crack=True, curl=True, glint=False)]
# the body is lowest just after each contact and highest on the passing pose
WALK = [dict(ph=i * math.pi / 4, walk=True, bob=int(round(1.6 * abs(math.sin(i * math.pi / 4 - 0.5)))), breath=0,
             flick=False, crack=False, curl=False, glint=(i % 4 == 1)) for i in range(8)]

if __name__ == '__main__':
    os.makedirs(f'{OUT}/gnur', exist_ok=True)
    frames = [gnur(p) for p in IDLE + WALK]
    sheet = Image.new('RGBA', (128 * len(frames), 128), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        im.save(f'{OUT}/gnur/{i}.png'); sheet.paste(im, (i * 128, 0))
    sheet.save(f'{OUT}/gnur.png')
    ALL = [INK] + ROBE + STAIN + MANT + GRIME + VOID + BRASS + COPP + VERD + IRON + WRAP + LEATH + CORD + WOOD + EYE + GLASS
    seen, rows = set(), []
    for c in ALL:
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/gnur.gpl', 'w').write('GIMP Palette\nName: gnur\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT)
