"""The Sentinel of the Veil, the guard at the Egg Cathedral's door (CathedralEntrance, texture key `guard`), redrawn with
the character renderer (rig.py, the Edgar quality bar), loosely after the author's hand-drawn guardian1.png: a tall
sentinel in worn plate (big rounded pauldrons, a ridged breastplate, faulds, knee cops) over a plum surcoat skirt and a
plum cape; the head a deep black cowl with nothing in it but two amber eye-slits and a brass speaking grille; a
halberd planted beside his right foot; a round verdigris shield with iron cross-bands and a boss on his left arm.
Contrapposto: the weight on his left leg, the torso a little turned, the head turned toward the player.
128x176 frames, soles on y 172; an 8-frame idle:
  0 rest  1 inhale  2 inhale held, the eyes flare  3 exhale, a draught stirs the cape  4 the head tilts
  5 tilted, the cape swings back  6 the eyes dim (a slow blink)  7 settling
python3 guardian.py <outdir>  ->  guardian.png (8-frame strip) + guardian/<n>.png + guardian.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK, h32
from rig import Rig, Mat
from feral_toast import ik, lerp
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
STEEL = ramp('#121318 #1c1e24 #282b32 #353941 #444951 #555b63 #686e76 #7e848a #979ca0 #b6b9ba')
MAIL  = ramp('#0e0f12 #17191d #22252a #2e3238 #3b4047 #4a5058')
PLUM  = ramp('#160810 #240d1b #341328 #461a36 #582245 #6a2c54 #7c3864 #8e4674')
HOOD  = ramp('#060508 #0b0a0e #121015 #19161d #211d26 #2a2530')
VERD  = ramp('#16241f #1f332c #2a4439 #365648 #436858 #527a69 #648c7a #7aa08e #94b6a4')
BRASS = ramp('#2a1d0c #46321a #6a4c22 #8e682e #b0883e #cca656 #e2c47a')
LEATH = ramp('#140c08 #22150d #321f13 #43291a #553522 #67412b #7a4f35')
WOOD  = ramp('#160d07 #24160c #342012 #452b18 #57371f')
EYE   = [(96, 46, 10), (178, 96, 22), (236, 156, 44), (255, 204, 96), (255, 236, 178)]
M = {'steel': Mat(STEEL, 'metal', 0.22, 0.9), 'mail': Mat(MAIL, 'metal', 0.2, 0.5), 'plum': Mat(PLUM, 'wool', 0.2),
     'hood': Mat(HOOD, 'wool', 0.26), 'verd': Mat(VERD, 'metal', 0.22, 0.5), 'brass': Mat(BRASS, 'metal', 0.24, 0.8),
     'leath': Mat(LEATH, 'leather', 0.2, 0.4), 'wood': Mat(WOOD, 'wood', 0.22)}

POSE = [dict(b=0, eye=1, tilt=0, cape=0), dict(b=1, eye=1, tilt=0, cape=0), dict(b=1, eye=2, tilt=0, cape=0),
        dict(b=0, eye=1, tilt=0, cape=1), dict(b=0, eye=1, tilt=1, cape=1), dict(b=0, eye=1, tilt=1, cape=2),
        dict(b=1, eye=0, tilt=0, cape=1), dict(b=0, eye=1, tilt=0, cape=0)]


def plate(r, cx, cy, rx, ry, rot=0.0, lift=0.0, group=None, lames=0, lame_dir=1):
    """a rounded armour plate; lames = dark lines of overlapping plates across it"""
    def vf(x, y, u, w):
        if lames and w * lame_dir > -0.6:
            k = (w * lame_dir + 0.6) * lames / 1.6
            if abs(k - round(k)) < 0.12 and round(k) > 0: return -0.45
        return 0
    return r.ellipsoid(cx, cy, rx, ry, M['steel'], rot=rot, lift=lift, group=group, vfun=vf)


def guardian(P):
    r = Rig(128, 176)
    b, tilt, cs = P['b'], P['tilt'], P['cape']
    sway = [0, 3, -2][cs]
    # ---- the cape behind everything: from the shoulders, flaring to the calves, its hem rippling with the draught
    hem = [(100 + sway, 158), (92 + sway * 0.8, 164 + (cs == 1)), (80 + sway * 0.5, 160), (66, 165 - (cs == 2)), (52, 161),
           (38 + sway * 0.4, 166), (28 + sway * 0.6, 160)]
    r.poly([(44, 56 - b), (84, 56 - b), (97 + sway * 0.4, 112)] + hem + [(30 + sway * 0.3, 112)], M['plum'], lift=-0.3, group='cape',
           vfun=lambda x, y: -0.32 if (x * 2 + y // 4 + sway) % 13 == 0 and y > 96 else 0)
    # ---- legs, contrapposto: the weight on his left leg (viewer's right, straight), the right leg loose, the knee forward
    for (hip, foot, g, side, lf) in (((72, 104), (73, 171), 'legL', 'left', -0.04), ((56, 107), (45, 171), 'legR', 'right', 0.0)):
        knee = ik(hip, foot, 33, 33, side)
        if g == 'legR': knee = (knee[0] - 1, knee[1] + 1)
        r.tube(hip, knee, 6.6, 5.6, M['mail'], lift=lf, group=g)
        r.tube(knee, (foot[0], foot[1] - 6), 5.4, 4.6, M['leath'], lift=lf, group=g + 'b',
               folds=lambda t, s: 0.28 if t < 0.1 else (-0.2 if 0.46 < t < 0.52 else 0))              # boot cuff, a strap
        toe = -3 if g == 'legR' else 1
        r.ellipsoid(foot[0] + toe, foot[1] - 3, 7.6, 3.6, M['leath'], lift=lf, group=g + 'f')
        for k in range(8): r.fixed(foot[0] - 6 + k * 1.6 + toe, foot[1] - 0.2, LEATH[0])
        plate(r, knee[0], knee[1] + 1, 6.0, 5.0, lift=0.12 + lf, group=g + 'k')                          # the knee cop
        r.fixed(knee[0] - 1, knee[1], STEEL[9]); r.fixed(knee[0], knee[1] + 3, BRASS[4])
    # ---- the surcoat skirt: heavy folds, the hem higher over the weight leg's hip
    def skirt_v(x, y):
        v = 0.0
        for fx in (47, 53, 59, 70, 76, 82):
            d = x + 0.5 - (fx + (y - 100) * (fx - 64) / 60)
            if abs(d) < 0.7: v -= 0.3
            elif 0.7 <= d < 2.0: v += 0.1
        if abs(x - 64.5 - (y - 100) * -0.08) < 0.8 and y > 106: v -= 0.7                            # the front split
        return v
    r.poly([(47, 99), (81, 99), (88, 118), (91, 138), (80, 141), (66, 138), (52, 144), (38, 141), (40, 118)],
           M['plum'], group='skirt', vfun=skirt_v)
    # ---- the cuirass: a broad chest tapering to the waist, a ridge a little left of centre (the torso is turned)
    ridge = 62
    def chest_v(x, y):
        v = 0.0
        if abs(x - ridge) < 0.8: v += 0.4
        elif 0.8 <= x - ridge < 2.2: v -= 0.2
        if y > 84: v -= (y - 84) * 0.03
        return v
    r.poly([(45, 57 - b), (83, 57 - b), (87, 68 - b), (84, 82), (78, 93), (64, 96), (51, 93), (44, 82), (42, 68 - b)],
           M['steel'], lift=0.0, round_=0.95, group='chest', vfun=chest_v)
    for k, y0 in enumerate((92, 97)):                                                                  # faulds
        r.poly([(49 - k * 2, y0), (80 + k * 2, y0), (82 + k * 2, y0 + 5), (47 - k * 2, y0 + 5)], M['steel'], lift=-0.06 - k * 0.06,
               round_=0.95, group='fauld%d' % k)
    r.poly([(46, 101), (83, 101), (83, 105), (46, 105)], M['leath'], group='belt')                       # the belt
    for (x, y, c) in ((63, 102, BRASS[6]), (64, 102, BRASS[5]), (63, 103, BRASS[4]), (64, 103, BRASS[3]), (65, 103, BRASS[2]), (65, 102, BRASS[4])):
        r.fixed(x, y, c)
    for (dx, dy) in ((0, -2), (-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 2)):   # the Cathedral's egg badge
        r.fixed(71 + dx, 70 + dy - b, BRASS[6] if dx + dy < 0 else (BRASS[4] if dx + dy < 2 else BRASS[2]))
    plate(r, 64, 55 - b, 13, 5, lift=0.04, group='gorget')
    # ---- the shield arm (his left, viewer's right): pauldron, the arm bent, the forearm behind the shield
    shL = (85, 62 - b)
    elL = (93, 86)
    r.tube(shL, elL, 5.6, 5.0, M['mail'], group='armL')
    plate(r, 86, 62 - b, 10.5, 8.5, rot=0.35, lift=0.0, group='pauldL', lames=3)
    # ---- the shield: big, round, verdigris bronze, iron cross-bands, a boss; held a little turned, in front of the hip
    sx, sy, srx, sry = 92, 104 - b * 0.5, 19.5, 23.0
    sid = r.ellipsoid(sx, sy, srx, sry, M['verd'], rot=-0.1, flat=0.5, group='shield')
    for y in range(int(sy - sry) - 2, int(sy + sry) + 3):                                             # bands and rim in iron / brass
        for x in range(int(sx - srx) - 2, int(sx + srx) + 3):
            e = r.buf.get((x, y))
            if not e or e[2] != sid: continue
            u, w = (x + 0.5 - sx) / srx, (y + 0.5 - sy) / sry
            d = math.hypot(u, w)
            if d > 0.88: e[0] = M['brass']; e[1] += 0.1
            elif abs(u + w * 0.1) < 0.1 or abs(w - u * 0.1) < 0.085: e[0] = M['steel']; e[1] -= 0.15
            elif h32(x, y, 77) % 9 == 0: e[1] -= 0.25                                                 # pitting in the patina
    for (u, w) in ((-0.45, 0.0), (0.45, 0.0), (0.0, -0.45), (0.0, 0.45), (-0.74, 0.0), (0.74, 0.0), (0.0, -0.74), (0.0, 0.74)):
        r.fixed(sx + u * srx, sy + w * sry, BRASS[6]); r.fixed(sx + u * srx + 1, sy + w * sry + 1, BRASS[1])   # rivets
    r.ellipsoid(sx - 0.5, sy - 0.5, 4.6, 4.8, M['steel'], lift=0.2, group='boss')
    r.fixed(sx - 2, sy - 3, STEEL[9]); r.fixed(sx - 1, sy - 3, STEEL[8])
    for (dx, dy) in ((7, 9), (8, 10), (9, 10), (-9, 12), (-8, 13)): r.darken(sx + dx, sy + dy, 0.4)       # old dents
    # ---- the head: a deep black cowl, a void, two amber slits, a brass grille; turned toward the player
    hx, hy = 60 - tilt * 2, 33 - b + tilt
    rot = -0.16 * tilt
    r.ellipsoid(64, 50 - b, 16.5, 7, M['hood'], group='cowl')                                           # the cowl over the gorget
    r.poly([(hx + 8, hy - 11), (hx + 16, hy + 1), (hx + 19, hy + 16), (hx + 10, hy + 19)], M['hood'], lift=-0.12, group='hood')
    r.ellipsoid(hx, hy, 13.0, 15.0, M['hood'], rot=rot, group='hood',
                vfun=lambda x, y, u, w: -0.25 if abs(math.atan2(w, u + 0.4) * 3 % 1 - 0.5) < 0.05 and u > -0.2 else 0)
    r.poly([(hx - 9 - tilt, hy - 12), (hx + 1 - tilt * 2, hy - 18), (hx + 10, hy - 13), (hx + 4, hy - 11)], M['hood'], lift=0.14, group='hoodtop')
    fx, fy = hx - 2, hy + 2
    for y in range(int(fy - 12), int(fy + 13)):                                                       # the face: a void
        for x in range(int(fx - 10), int(fx + 11)):
            dx, dy = x + 0.5 - fx, y + 0.5 - fy
            dx, dy = dx * math.cos(rot) + dy * math.sin(rot), -dx * math.sin(rot) + dy * math.cos(rot)
            d = (dx / 8.4) ** 2 + (dy / 10.5) ** 2
            if d <= 1: r.fixed(x, y, (4, 3, 5) if d < 0.72 else (10, 9, 12))
    lvl = P['eye']
    eyes = ((fx - 6, fy - 3, 4), (fx + 2, fy - 3 - tilt, 3))                                          # the far slit shorter, higher on a tilt
    for (ex, ey, w_) in eyes:
        for k in range(w_):
            core = [EYE[1], EYE[3], EYE[4]][lvl]
            edge_ = [EYE[0], EYE[2], EYE[3]][lvl]
            r.fixed(ex + k, ey + (1 if tilt and k == 0 and ex < fx else 0), core if 0 < k < w_ - 1 else edge_)
            if lvl: r.fixed(ex + k, ey + 1 + (1 if tilt and k == 0 and ex < fx else 0), EYE[0])
            if lvl == 2: r.fixed(ex + k, ey - 1, EYE[1])
    gx, gy = fx - 1 - tilt, fy + 5 + tilt                                                             # the speaking grille
    for dy in range(4):
        for dx in range(-3, 4):
            if (dx / 3.5) ** 2 + ((dy - 1.5) / 2.2) ** 2 > 1: continue
            edge = abs(dx) == 3 or dy in (0, 3)
            r.fixed(gx + dx, gy + dy, BRASS[5] if edge and dy == 0 else (BRASS[2] if edge else ((5, 4, 6) if dx % 2 == 0 else BRASS[3])))
    for k in range(13):                                                                               # the cowl's rim round the face
        a = -2.9 + k * 0.42
        r.fixed(fx + math.cos(a + rot) * 9.6, fy + math.sin(a + rot) * 11.8, HOOD[4] if k % 3 else HOOD[5])
    # ---- the halberd: a long shaft planted by his right foot, leaning a little out
    shaft_x = lambda y: 32 + (171 - y) * 0.03
    r.tube((shaft_x(171), 171), (shaft_x(14), 14), 1.7, 1.5, M['wood'], group='shaft')
    for y in (150, 152):
        r.fixed(shaft_x(y), y, BRASS[5]); r.fixed(shaft_x(y) + 1, y, BRASS[3])
    r.tube((shaft_x(171), 171), (shaft_x(165), 165), 1.9, 1.7, M['steel'], group='butt')               # the iron butt-cap
    # its head: langets down the shaft, a crescent axe blade (viewer's left), a back hook, a top spike
    hx_, top = shaft_x(16), 16
    r.tube((hx_, top + 8), (shaft_x(top + 30), top + 30), 2.0, 1.8, M['steel'], group='langet')
    blade = [(hx_ - 1, top + 1), (hx_ - 7, top - 2), (hx_ - 12, top - 3), (hx_ - 15, top + 3), (hx_ - 16.5, top + 10),
             (hx_ - 15, top + 17), (hx_ - 11, top + 21), (hx_ - 7, top + 18), (hx_ - 1, top + 14)]
    def blade_v(x, y):
        # flat steel: darker toward the shaft, a bevel line, a bright honed edge on the convex side
        d_edge = min(math.hypot(x + 0.5 - bx, y + 0.5 - by) for (bx, by) in blade[1:8])
        v = -0.35 if x > hx_ - 6 else 0.0
        if d_edge < 1.6: v += 0.9
        elif d_edge < 3.2: v -= 0.25
        return v
    r.poly(blade, M['steel'], lift=-0.05, round_=0.12, tilt=-0.2, group='blade', vfun=blade_v)
    for (x, y) in ((hx_ - 4, top + 4), (hx_ - 4, top + 11)): r.fixed(x, y, BRASS[5])                 # its rivets
    r.poly([(hx_ + 1, top + 5), (hx_ + 6, top + 3), (hx_ + 10, top - 2), (hx_ + 9, top + 4), (hx_ + 1, top + 10)], M['steel'], lift=0.05,
           round_=0.4, group='hook')
    r.poly([(hx_ - 1.6, top + 3), (hx_ - 0.4, top - 16), (hx_ + 0.6, top - 16), (hx_ + 1.6, top + 3)], M['steel'], lift=0.2, round_=0.8, group='spike')
    # ---- the halberd arm (his right, viewer's left) in front: the gauntlet closed round the shaft at the belt
    shR = (43, 62 - b)
    hand = (shaft_x(100) + 1, 100)
    elR = ik(shR, hand, 21, 21, 'left')                                                               # the elbow hangs out and down
    r.tube(shR, elR, 5.8, 5.2, M['mail'], group='armR')
    plate(r, elR[0], elR[1], 4.8, 4.4, lift=0.12, group='couter')
    r.tube(elR, (hand[0] + 1, hand[1] - 3), 5.0, 4.6, M['steel'], group='vambrace', folds=lambda t, s: -0.45 if 0.48 < t < 0.54 else 0)
    plate(r, 42, 62 - b, 11.5, 9.0, rot=-0.3, lift=0.08, group='pauldR', lames=3)
    r.ellipsoid(hand[0] + 0.6, hand[1] + 1.2, 4.6, 4.2, M['steel'], group='gauntlet')
    for k in range(4): r.fixed(hand[0] - 3 + k * 2, hand[1] + 3, STEEL[1]); r.fixed(hand[0] - 3 + k * 2, hand[1] + 2, STEEL[6])   # the fingers' lames
    for y in (hand[1] - 5, hand[1] + 6):                                                              # the shaft above and below the fist
        r.fixed(shaft_x(y), y, WOOD[3])
    seam(r, 'armR', 0.25); seam(r, 'pauldR', 0.22); seam(r, 'pauldL', 0.22); seam(r, 'gauntlet', 0.2); seam(r, 'shield', 0.25)
    seam(r, 'hoodtop', 0.12); seam(r, 'skirt', 0.15); seam(r, 'vambrace', 0.15)
    im = r.render()
    # the eyes' faint light on the void and the cowl round them (a glow, not a volume)
    if P['eye'] > 0:
        p = im.load()
        for (ex, ey, w_) in eyes:
            cx_ = ex + w_ / 2 - 0.5
            for y in range(int(ey - 3), int(ey + 4)):
                for x in range(int(cx_ - 5), int(cx_ + 6)):
                    c = p[x, y]
                    if c[3] == 0 or c[:3] in EYE: continue
                    d = math.hypot((x - cx_) / 1.8, y - ey)
                    k = max(0.0, 1 - d / 3.4) * (0.3 if P['eye'] == 1 else 0.55)
                    if k > 0.05: p[x, y] = tuple(int(c[i] + (EYE[1][i] - c[i]) * k) for i in range(3)) + (255,)
    return im


if __name__ == '__main__':
    os.makedirs(f'{OUT}/guardian', exist_ok=True)
    frames = [guardian(p) for p in POSE]
    sheet = Image.new('RGBA', (128 * len(frames), 176), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        im.save(f'{OUT}/guardian/{i}.png'); sheet.paste(im, (i * 128, 0))
    sheet.save(f'{OUT}/guardian.png')
    ALL = [INK] + STEEL + MAIL + PLUM + HOOD + VERD + BRASS + LEATH + WOOD + EYE
    seen, rows = set(), []
    for c in ALL:
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/guardian.gpl', 'w').write('GIMP Palette\nName: guardian\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT)
