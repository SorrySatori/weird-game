"""Voxmarket NPCs as pixel-art sprites (rig.py renderer, the Feral Toast / Edgar quality bar), scale 1, feet on the bottom.
  kloor      128x160  Kloor Venn: a hunched sewer rat in a ragged olive hood, cloak and scarf, a belt of pouches and
                      Oltrac vials, a bare ringed tail; frames 0-3 idle (breath, sniff, blink), 4-11 walk (facing right)
  zerren     176x160  Zerren: hooded, a pale stitched doll-face, behind a counter draped in red with a gold fringe; an
                      orange plush bear, a green plush octopus and a rack of sound-ampules; 0-3 idle (breath, lifts an
                      ampule to the light, tilts the head)
  hesh_vell  208x176  Hesh and Vell: withered bark-skinned twin auctioneers in tattered robes with gold trim, antler-twig
                      hoods, glowing eyes, each with a raised gavel; 0-7 idle -- Vell repeats Hesh's gavel two frames late
python3 voxmarket_chars.py <outdir> [ids]  ->  <id>.png sheets + <id>/<n>.png + vox_chars.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK, h32
from symbionts import curve
from rig import Rig, Mat, norm
from feral_toast import ik, worm, creases, lerp
from pal_club import BRASS, STEEL, BONE2, EYE, VEIN

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
def R(s): return ramp(s)
RATFUR = R('#140d0a #20150f #2d1e15 #3b281c #4b3324 #5d402d #714f38 #865f44 #9a7155')
RATPINK = R('#3a1f1c #55302a #72433a #8e584c #a86e60 #c08878')
CLOAK = R('#121209 #1b1b0e #262514 #33311b #403d22 #4f4a2a #605934 #726a40')
LEATH = R('#120c09 #1c140e #281c14 #35261b #433123 #523d2c')
HOOD = R('#141a0e #1e2614 #29331b #354223 #43522c #536436 #657841 #78894e')
MASK = R('#3a312a #54483d #6e6050 #8a7a66 #a4937c #bcab90 #d0c0a2')
CLOTH = R('#2e0f0c #4a1912 #6a2418 #8c3322 #ab4a30 #c66a48 #d8845e')
TABLE = R('#1c120b #2a1b10 #3a2616 #4c331d #5f4126 #745232 #8a6440')
BEAR = R('#2e170a #4a2610 #6a3818 #8c4c22 #ad642f #c98042 #dc9a5a')
OCTO = R('#10200e #1a3216 #26461f #345c2a #457238 #5a8a48 #72a25a')
BARK = R('#140e09 #20160e #2d2014 #3c2b1b #4c3824 #5e472f #72583b #886b48')
ROBEB = R('#120c08 #1c130c #281b11 #352417 #432e1d #523924 #63452d #76563a')
WOODS = R('#2a1c10 #4a3420 #7a5a38 #a88458 #d0b080')
AMPS = [R('#0e2a2c #1d5a5a #3a9a92 #8ae0d4'), R('#24123a #4a2a6e #7a52a8 #b894e0'), R('#3a2408 #7a5414 #c49030 #f0d27a'), R('#3a0e0c #7a2218 #b8432e #e8806a')]

M = {
    'fur': Mat(RATFUR, 'fur', 0.2), 'pink': Mat(RATPINK, 'skin', 0.24, 0.2), 'cloak': Mat(CLOAK, 'wool', 0.18), 'leath': Mat(LEATH, 'leather', 0.18, 0.4),
    'hood': Mat(HOOD, 'wool', 0.18), 'mask': Mat(MASK, 'skin', 0.28, 0.25), 'cloth': Mat(CLOTH, 'fabric', 0.2), 'table': Mat(TABLE, 'wood', 0.2, 0.3),
    'bear': Mat(BEAR, 'fur', 0.24), 'octo': Mat(OCTO, 'wool', 0.24), 'bark': Mat(BARK, 'fur', 0.16), 'robe': Mat(ROBEB, 'wool', 0.16),
    'brass': Mat(BRASS, 'metal', 0.2, 0.6), 'wood': Mat(WOODS, 'wood', 0.25, 0.3), 'steel': Mat(STEEL, 'metal', 0.18, 0.5),
}

# ------------------------------------------------------------------------------------------------------------- Kloor
def kloor(P):
    r = Rig(128, 160)
    ph, bob, walk = P['ph'], P['bob'], P['walk']
    hip = (56, 108 + bob)
    # tail: from the rump, sweeping down behind, curling at the tip
    sw = math.sin(ph) * 3 if walk else math.sin(P['ph']) * 1.2
    tail = curve(lambda t: (44 - 26 * t + sw * t, 112 + 38 * t * t - 6 * math.sin(t * 3.0) * t + (6 * (t - 0.8) ** 2 * 10 if t > 0.8 else 0)), 22)
    worm(r, tail, 3.2, 1.0, M['pink'], 'tail')
    for i in range(3, len(tail) - 2, 3): r.darken(tail[i][0], tail[i][1], 0.25)
    def leg(sgn, phase, far):
        s = math.sin(phase) * 9 if walk else 0.0
        lift = max(0.0, math.cos(phase)) * 5 if walk else 0.0
        h = (hip[0] + (3 if far else -2), hip[1] + 2)
        knee = (h[0] + 7 + s * 0.45, h[1] + 14 - lift * 0.4)
        ankle = (h[0] - 1 + s, 147 - lift)
        toe = (ankle[0] + 13, 156 - lift * 0.6)
        g = 'legF' if far else 'legN'; lf = -0.18 if far else 0.0
        r.tube(h, knee, 7.4, 5.6, M['fur'], lift=lf, group=g)
        r.tube(knee, ankle, 4.8, 3.4, M['fur'], lift=lf, group=g)
        r.tube(ankle, toe, 3.4, 2.2, M['fur'], lift=lf, group=g)
        for k in range(3): r.fixed(toe[0] + 1, toe[1] - 1 + k, RATPINK[3])
        for k in (0.35, 0.6): p = lerp(knee, ankle, k); r.fixed(p[0] - 1, p[1], LEATH[2]); r.fixed(p[0], p[1], LEATH[2]); r.fixed(p[0] + 1, p[1], LEATH[3])   # cloth wraps
    leg(1, ph + math.pi, True)
    # far arm, behind the body
    shF = (58, 74 + bob)
    handF = (62 - math.sin(ph) * 6, 104 + bob) if walk else (74, 92 + bob)
    E = ik(shF, handF, 15, 15, 'left')
    r.tube(shF, E, 4.4, 3.8, M['cloak'], lift=-0.2, group='armF'); r.tube(E, handF, 3.0, 2.4, M['fur'], lift=-0.2, group='armF')
    r.ellipsoid(handF[0], handF[1], 2.8, 2.6, M['fur'], lift=-0.15, group='armF')
    # the hunched body in the cloak, a ragged hem
    r.ellipsoid(58, 92 + bob, 19, 27, M['cloak'], rot=0.42, group='body')
    hem = [(44, 100 + bob), (76, 104 + bob)]
    pts = [(44, 98 + bob)]
    for k in range(10):
        x = 40 + k * 4.4; pts.append((x + 2, 130 + bob + (5 if k % 2 else -1) + (h32(k, 3) % 3)))
    pts += [(80, 104 + bob), (74, 96 + bob)]
    r.poly(pts, M['cloak'], group='body', vfun=lambda x, y: -0.16 if (x * 2 + y) % 9 == 0 else 0)
    r.tube((44, 100 + bob), (78, 104 + bob), 2.6, 2.6, M['leath'], group='belt')                     # belt, pouches, vials
    r.ellipsoid(50, 106 + bob, 4.2, 3.6, M['leath'], group='pouch')
    r.ellipsoid(70, 108 + bob, 3.4, 3.0, M['leath'], group='pouch')
    for (vx, c) in ((58, AMPS[1]), (62, AMPS[2]), (65, STEEL)):
        for k in range(5): r.fixed(vx, 104 + bob + k, c[2] if k < 4 else c[1])
        r.fixed(vx, 103 + bob, LEATH[4])
    leg(-1, ph, False)
    # scarf + hood behind the head
    r.poly([(64, 62 + bob), (82, 66 + bob), (80, 76 + bob), (62, 74 + bob)], M['cloak'], lift=0.08, group='scarf')
    r.tube((66, 72 + bob), (60, 90 + bob + (2 * math.sin(ph) if walk else 0)), 2.8, 2.2, M['cloak'], lift=0.05, group='scarf')
    hx, hy = 82, 58 + bob + P['hd']
    r.poly([(58, 74 + bob), (60, 50 + bob), (68, 38 + bob), (80, 36 + bob), (86, 44 + bob), (78, 66 + bob)], M['cloak'], lift=-0.05, group='hood')
    # the head: skull, a long snout, pink nose, buck teeth, whiskers
    r.ellipsoid(hx, hy, 12.5, 11, M['fur'], group='head')
    sn = P['sniff']
    r.tube((hx + 5, hy + 2), (hx + 23, hy + 8 - sn), 7.4, 2.8, M['fur'], group='head')
    r.ellipsoid(hx + 23, hy + 8 - sn, 2.2, 2.0, M['pink'], group='nose')
    for (x, y) in ((hx + 19, hy + 12 - sn), (hx + 20, hy + 12 - sn), (hx + 19, hy + 13 - sn), (hx + 20, hy + 13 - sn)): r.fixed(x, y, (214, 188, 110))
    for k in range(hx + 9, hx + 20): r.fixed(k, hy + 11 - sn + (1 if k > hx + 15 else 0), RATFUR[1])
    for (a, ln) in ((-0.35, 13), (-0.1, 14), (0.18, 12)):
        for j in range(ln):
            if (j + (P['ph'] > 0)) % 4 == 3: continue
            r.fixed(hx + 21 + j * math.cos(a), hy + 7 - sn + j * math.sin(a), BONE2[4] if j < 6 else BONE2[2])
    r.poly([(hx - 14, hy + 2), (hx - 13, hy - 7), (hx - 6, hy - 12), (hx + 3, hy - 12), (hx + 6, hy - 8), (hx - 2, hy - 4), (hx - 8, hy + 6)],
           M['cloak'], lift=0.06, group='hoodbrim', vfun=lambda x, y: -0.15 if (x + y) % 6 == 0 else 0)          # the hood over the crown
    for ex, grp in ((hx - 7, 'earF'), (hx - 1, 'earN')):                                            # ears through slits in the hood
        r.ellipsoid(ex, hy - 13, 5.6, 7.0, M['fur'], lift=(-0.15 if grp == 'earF' else 0), group=grp)
        r.ellipsoid(ex + 0.5, hy - 12.5, 3.0, 4.4, M['pink'], lift=-0.1, group=grp)
    if P['blink']:
        r.fixed(hx + 6, hy - 1, RATFUR[1]); r.fixed(hx + 7, hy - 1, RATFUR[1])
    else:
        r.fixed(hx + 6, hy - 2, INK); r.fixed(hx + 7, hy - 2, INK); r.fixed(hx + 6, hy - 1, INK); r.fixed(hx + 7, hy - 1, EYE[2]); r.fixed(hx + 7, hy - 2, EYE[1])
    for k in range(4): r.fixed(hx + 4 + k, hy - 4 - (k == 1 or k == 2), RATFUR[1])                     # a scowling brow
    # near arm, in front: a hand holding an Oltrac vial (idle) or swinging (walk)
    shN = (68, 78 + bob)
    handN = (70 + math.sin(ph) * 7, 110 + bob) if walk else (84, 96 + bob)
    E = ik(shN, handN, 17, 16, 'left')
    r.tube(shN, E, 5.6, 4.8, M['cloak'], folds=creases(0.8), group='armN'); r.tube(E, handN, 3.6, 2.8, M['fur'], group='armN')
    r.ellipsoid(handN[0], handN[1], 3.6, 3.2, M['fur'], group='handN')
    for k in range(3): r.fixed(handN[0] + 2 + (k == 1), handN[1] - 1 + k, BONE2[3])                  # claws
    if not walk:
        for k in range(6): r.fixed(handN[0] + 1, handN[1] - 7 + k, AMPS[1][2] if k < 5 else AMPS[1][1])
        r.fixed(handN[0] + 1, handN[1] - 8, LEATH[4]); r.fixed(handN[0] + 1, handN[1] - 6, AMPS[1][3])
    return r.render()

KLOOR_IDLE = [dict(ph=0.0, bob=0, walk=False, hd=0, sniff=0, blink=False), dict(ph=0.5, bob=1, walk=False, hd=0, sniff=0, blink=False),
              dict(ph=1.0, bob=1, walk=False, hd=-1, sniff=1, blink=False), dict(ph=0.0, bob=0, walk=False, hd=0, sniff=0, blink=True)]
KLOOR_WALK = [dict(ph=i * math.pi / 4, bob=(1 if i % 4 in (1, 2) else 0), walk=True, hd=(1 if i % 4 == 2 else 0), sniff=0, blink=False) for i in range(8)]

# ------------------------------------------------------------------------------------------------------------ Zerren
def zerren(P):
    r = Rig(176, 160)
    br, lift_amp, tilt = P['br'], P['amp'], P['tilt']
    # Zerren behind the counter: cloak shoulders, the hood, a stitched doll-face
    r.poly([(60, 74 - br), (116, 74 - br), (130, 112), (46, 112)], M['hood'], group='cloak', vfun=lambda x, y: -0.15 if (x - 88 + y // 5) % 8 == 0 else 0)
    hx, hy = 88 + tilt, 46 - br
    r.ellipsoid(hx, hy, 24, 27, M['hood'], group='hood')
    r.poly([(hx - 18, hy - 14), (hx, hy - 30), (hx + 18, hy - 14)], M['hood'], group='hood')
    r.ellipsoid(hx, hy + 3, 15, 18, M['hood'], lift=-0.55, group='hoodin')
    r.ellipsoid(hx, hy + 4, 12, 14.5, M['mask'], group='face')
    for ex in (hx - 5, hx + 5):                                                                     # stitched eyes
        for d in (-1, 0, 1): r.fixed(ex + d, hy + 1 + d, INK); r.fixed(ex + d, hy + 1 - d, INK)
    for x in range(hx - 6, hx + 7):                                                                 # a stitched smile
        y = hy + 11 + (1 if abs(x - hx) > 4 else 0)
        r.fixed(x, y, (42, 28, 22))
        if (x - hx) % 2 == 0: r.fixed(x, y - 1, (42, 28, 22)); r.fixed(x, y + 1, (42, 28, 22))
    for cx_ in (hx - 8, hx + 8): r.darken(cx_, hy + 8, -0.1)
    # the counter: a tabletop, red cloth with a gold fringe, legs at the sides
    for lx in (28, 146): r.tube((lx, 108), (lx, 157), 3.4, 3.0, M['table'], group='leg%d' % lx)
    r.poly([(18, 102), (158, 102), (160, 110), (16, 110)], M['table'], lift=0.15, round_=0.3, group='top')
    r.poly([(36, 108), (140, 108), (142, 150), (34, 150)], M['cloth'], group='cloth',
           vfun=lambda x, y: (0.18 if 40 < x < 136 and 114 < y < 144 and (x in (44, 132) or y in (118, 140)) else 0) - (0.15 if (x * 3) % 17 == 0 else 0))
    for x in range(34, 143): r.fixed(x, 150 + (x % 2), BRASS[5] if x % 3 else BRASS[3])
    # the plush bear (left) and the plush octopus (right)
    r.ellipsoid(48, 92, 11, 11, M['bear'], group='bear')
    r.ellipsoid(48, 74, 9, 8.5, M['bear'], group='bear')
    for ex in (41, 55): r.ellipsoid(ex, 66, 3.4, 3.4, M['bear'], group='bear')
    r.ellipsoid(48, 77, 4.2, 3.2, M['bear'], lift=0.2, group='bear')
    for ex in (45, 51): r.fixed(ex, 72, INK); r.fixed(ex, 73, INK)
    r.fixed(48, 76, INK)
    for k in range(5): r.fixed(48, 86 + k, BEAR[2])                                                # the seam (where the Vestigel was)
    r.ellipsoid(132, 82, 10, 9, M['octo'], group='octo')
    for k in range(5):
        a = -0.3 + k * 0.4
        worm(r, curve(lambda t: (124 + k * 4 + math.sin(t * 4 + k) * 2, 88 + 16 * t), 6), 2.4, 1.2, M['octo'], 'octo')
    for ex in (128, 136): r.fixed(ex, 81, INK); r.fixed(ex, 82, INK)
    # a rack of sound-ampules
    r.poly([(98, 94), (122, 94), (122, 102), (98, 102)], M['table'], round_=0.4, group='rack')
    for i in range(4):
        ax = 101 + i * 6
        c = AMPS[i]
        for k in range(9): r.fixed(ax, 89 + k, c[2] if k < 8 else c[1]); r.fixed(ax + 1, 89 + k, c[1] if k < 8 else c[0])
        r.fixed(ax, 88, STEEL[6]); r.fixed(ax, 91, c[3])
    # hands on the counter; the right one sometimes lifts an ampule to the light
    for (hx_, hy_, grp) in ((72, 102, 'handL'), (104 if not lift_amp else 108, 102 if not lift_amp else 80, 'handR')):
        sh = (hx_ - 8 if hx_ < 88 else hx_ + 8, 80 - br)
        E = ik(sh, (hx_, hy_), 14, 14, 'left' if hx_ < 88 else 'right')
        r.tube(sh, E, 6.4, 5.6, M['hood'], group=grp); r.tube(E, (hx_, hy_ - 2), 5.6, 5.0, M['hood'], group=grp)
        r.ellipsoid(hx_, hy_, 4.6, 3.6, M['mask'], group=grp + 'h')
        for k in range(3): r.fixed(hx_ - 2 + k * 2, hy_ + 2, MASK[2])
    if lift_amp:
        c = AMPS[0]
        for k in range(9): r.fixed(108, 68 + k, c[2] if k < 8 else c[1]); r.fixed(109, 68 + k, c[1])
        r.fixed(108, 67, STEEL[6]); r.fixed(108, 70, c[3]); r.fixed(110, 66, c[3])
    return r.render()

ZERREN_IDLE = [dict(br=0, amp=False, tilt=0), dict(br=1, amp=False, tilt=0), dict(br=1, amp=True, tilt=1), dict(br=0, amp=False, tilt=-1)]

# ------------------------------------------------------------------------------------------------------- Hesh & Vell
GAVEL = [0, 2, 5, 7, 5, 2, 0, -3]                    # the raise-and-strike; Vell runs two frames late
TILT = [0, 0, 1, 1, 0, 0, -1, -1]

def twin(r, cx, outer, f, tag):
    g, tl = GAVEL[f], TILT[f]
    folds = lambda x, y: -0.2 if (x - cx + y // 7) % 7 == 0 else (0.1 if (x - cx + y // 7) % 7 == 1 else 0)
    # the dark under-robe, then an open outer robe whose edges are trimmed in gold
    r.poly([(cx - 10, 66), (cx + 10, 66), (cx + 14, 166), (cx - 14, 166)], M['robe'], lift=-0.35, group='under' + tag, vfun=folds)
    for sgn in (-1, 1):
        pts = [(cx + sgn * 6, 64), (cx + sgn * 15, 64), (cx + sgn * 24, 122)]
        for k in range(6):
            x = cx + sgn * (25 - k * 3.4)
            pts.append((x, 166 + (4 if k % 2 else 0) + h32(k, cx, sgn) % 3))
        pts.append((cx + sgn * 8, 168)); pts.append((cx + sgn * 5, 100))
        r.poly(pts, M['robe'], group='robe' + tag + str(sgn), vfun=folds)
        for y in range(66, 168):                                                    # the gilded edge of the opening
            t = (y - 66) / 102
            ex = cx + sgn * (6 - (1 if y < 100 else 0) * 1 + (3 if y > 100 else 0) * t)
            r.fixed(ex, y, BRASS[5] if y % 4 else BRASS[3])
            if y % 12 == 0: r.fixed(ex + sgn, y, BRASS[6])
    for k in range(14):                                                             # mycelium wisps fraying from the hem
        x = cx - 25 + k * 3.8
        for j in range(2 + h32(k, cx, 2) % 3): r.fixed(x + (j % 2), 168 + (3 if k % 2 else 0) + j, BONE2[5] if j < 2 else BONE2[3])
    for y in range(78, 84): r.fixed(cx - 3, y, BARK[2]); r.fixed(cx + 3, y, BARK[2])               # bark ribs in the open collar
    r.ellipsoid(cx, 72, 3.4, 3.0, M['brass'], group='clasp' + tag)
    # hood with antler twigs, gold-trimmed rim, a dark opening, a withered face, glowing eyes
    hx = cx + tl
    r.poly([(cx - 15, 68), (hx - 13, 34), (hx - 6, 20), (hx, 14), (hx + 6, 20), (hx + 13, 34), (cx + 15, 68)], M['robe'], lift=0.06, group='hood' + tag)
    for sgn in (-1, 1):
        base = (hx + sgn * 7, 22)
        tw = curve(lambda t: (base[0] + sgn * 9 * t, base[1] - 12 * t + 3 * t * t), 6)
        worm(r, tw, 2.2, 0.8, M['bark'], 'twig' + tag)
        b2 = tw[3]
        worm(r, curve(lambda t: (b2[0] + sgn * 2 * t, b2[1] - 6 * t), 4), 1.4, 0.7, M['bark'], 'twig' + tag)
    r.ellipsoid(hx, 44, 9.5, 12.5, M['brass'], lift=-0.1, group='rim' + tag)
    r.ellipsoid(hx, 44, 8.5, 11.5, M['robe'], lift=-0.75, group='void' + tag)
    r.ellipsoid(hx, 48, 6.5, 8.0, M['bark'], lift=-0.3, group='face' + tag)
    for ex in (hx - 4, hx + 3):
        glow = EYE[3] if f == 7 else EYE[2]
        r.fixed(ex, 42, glow); r.fixed(ex + 1, 42, EYE[2]); r.fixed(ex, 43, EYE[1]); r.fixed(ex + 1, 43, EYE[1])
    for x in range(hx - 3, hx + 4): r.fixed(x, 53, BARK[0])
    # the inner hand holds the auction ledger against the chest
    lx = cx - outer * 7
    r.poly([(lx - 6, 92), (lx + 6, 92), (lx + 6, 106), (lx - 6, 106)], M['robe'], lift=0.2, round_=0.3, group='ledger' + tag)
    for y in range(94, 105, 2): r.fixed(lx - 4 + (outer > 0) * 0, y, BONE2[4]); r.fixed(lx - 3, y, BONE2[3])
    r.ellipsoid(lx + outer * 6, 99, 3.0, 3.4, M['bark'], group='ihand' + tag)
    # the outer arm raised with a gavel, in a wide tattered sleeve
    sh = (cx + outer * 13, 72)
    hand = (cx + outer * 26, 44 - g)
    E = ik(sh, hand, 17, 16, 'down')
    r.tube(sh, E, 6.8, 6.2, M['robe'], group='sleeve' + tag)
    r.tube(E, (hand[0] - outer * 2, hand[1] + 7), 6.2, 8.0, M['robe'], group='sleeve' + tag)
    for k in range(4):                                                              # rags hanging from the sleeve
        p = lerp(E, (hand[0] - outer * 2, hand[1] + 7), 0.6 + k * 0.1)
        r.stroke([(p[0] + outer * 3, p[1] + 3 + j) for j in range(4 + k % 2)], 1.4, M['robe'], v=0.3, group='sleeve' + tag)
    r.ellipsoid(hand[0], hand[1], 3.4, 3.2, M['bark'], group='hand' + tag)
    top = (hand[0] + outer * 2, hand[1] - 15)
    r.stroke(curve(lambda t: lerp(hand, top, t), 16), 2.4, M['wood'], v=0.55, group='gavel' + tag)
    r.tube((top[0] - 6, top[1] - 1), (top[0] + 6, top[1] + 1), 4.2, 4.2, M['wood'], group='gavel' + tag)
    for dx in (-4, 4): r.fixed(top[0] + dx, top[1], BRASS[6]); r.fixed(top[0] + dx, top[1] + 1, BRASS[4]); r.fixed(top[0] + dx, top[1] - 1, BRASS[4])

def hesh_vell(f):
    r = Rig(208, 176)
    twin(r, 60, -1, f, 'H')                          # Hesh, the left one
    twin(r, 148, 1, (f - 2) % 8, 'V')                # Vell, half a beat behind
    return r.render()

CAST = {'kloor': (kloor, KLOOR_IDLE + KLOOR_WALK), 'zerren': (zerren, ZERREN_IDLE), 'hesh_vell': (hesh_vell, list(range(8)))}
ALL = [INK] + RATFUR + RATPINK + CLOAK + LEATH + HOOD + MASK + CLOTH + TABLE + BEAR + OCTO + BARK + ROBEB + WOODS + BRASS + STEEL + BONE2 + EYE + [c for a in AMPS for c in a]

if __name__ == '__main__':
    only = sys.argv[2].split(',') if len(sys.argv) > 2 else list(CAST)
    for cid in only:
        fn, poses = CAST[cid]
        os.makedirs(f'{OUT}/{cid}', exist_ok=True)
        frames = [fn(p) for p in poses]
        w, h = frames[0].size
        sheet = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
        for i, im in enumerate(frames):
            im.save(f'{OUT}/{cid}/{i}.png'); sheet.paste(im, (i * w, 0))
        sheet.save(f'{OUT}/{cid}.png')
    seen, rows = set(), []
    for c in ALL:
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/vox_chars.gpl', 'w').write('GIMP Palette\nName: vox_chars\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT)
