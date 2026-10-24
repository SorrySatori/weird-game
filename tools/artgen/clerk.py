"""The Applications clerk of Shed 521 (ShedApplicationsScene) -- an Ink Tribunal bureaucrat of the Bureau of Shapes,
redrawn with the character renderer (rig.py) after the old sprite: an olive, cephalopod-like head with a crown of
slowly curling tentacles and two big yellow eyes behind round wire glasses, a pink shirt, a red tie, a bottle-green
waistcoat with a name badge, a clipboard in the crook of his arm. 128x176 frames, facing the viewer turned a little to
the right (towards whoever comes in through the door), feet on y 172; an 8-frame idle:
  0-1  breathing, the tentacles curl          2-3  he pushes his glasses up his nose
  4-5  he leafs the clipboard's page          6-7  he taps the clipboard with the pen
python3 clerk.py <outdir>  ->  clerk.png (8-frame sheet) + clerk/<n>.png + clerk.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK, h32
from rig import Rig, Mat
from feral_toast import ik, lerp
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
R = ramp
SKIN  = R('#1e2410 #2c3518 #3c4821 #4d5c2b #5f7036 #738443 #899a54 #a2b06a')
EYE   = R('#4a3a0c #7a6214 #a88a22 #d0ae38 #ecd062')
SHIRT = R('#3a2230 #523042 #6c4056 #86526a #a0687e #b98296')
TIE   = R('#2c0c0c #461212 #621a18 #7e2620 #9a3428')
VEST  = R('#0e1a16 #142420 #1c302a #263e36 #314c43 #3e5c51')
TROU  = R('#101614 #182220 #222e2b #2c3a36 #374741')
SHOE  = R('#0c0b0a #171512 #23201b #302b24')
BOARD = R('#2a180c #432713 #5c381c #774a27 #905d33')
PAPER = R('#8c8878 #aaa694 #c6c2ae #dedac6 #eeead8')
WIRE  = R('#3a3426 #6a5e40 #9a8a5c #c8b47a')
M = {'skin': Mat(SKIN, 'skin', 0.26, 0.35), 'shirt': Mat(SHIRT, 'fabric', 0.24), 'tie': Mat(TIE, 'fabric', 0.24, 0.2),
     'vest': Mat(VEST, 'wool', 0.2), 'trou': Mat(TROU, 'fabric', 0.18), 'shoe': Mat(SHOE, 'leather', 0.2, 0.7),
     'board': Mat(BOARD, 'wood', 0.22, 0.2), 'paper': Mat(PAPER, 'plain', 0.4)}

POSE = [dict(b=0, t=0.0, glasses=0, leaf=0, tap=0), dict(b=1, t=0.6, glasses=0, leaf=0, tap=0),
        dict(b=1, t=1.2, glasses=1, leaf=0, tap=0), dict(b=0, t=1.8, glasses=2, leaf=0, tap=0),
        dict(b=0, t=2.4, glasses=0, leaf=1, tap=0), dict(b=1, t=3.0, glasses=0, leaf=2, tap=0),
        dict(b=1, t=3.6, glasses=0, leaf=0, tap=1), dict(b=0, t=4.2, glasses=0, leaf=0, tap=2)]

def clerk(P):
    r = Rig(128, 176)
    b = P['b']; t = P['t']
    # legs, shoes (a bureaucrat's tidy stance, the near foot a little forward)
    for sx, fz in ((-1, 0), (1, 1)):
        hip = (62 + sx * 6, 112)
        foot = (62 + sx * 8 + fz * 2, 166)
        knee = ik(hip, foot, 28, 27, 'right')
        r.tube(hip, knee, 6.6, 5.6, M['trou'], group='leg%d' % sx, folds=lambda u, sd: -0.25 if abs(sd) < 0.12 and u > 0.1 else 0)
        r.tube(knee, foot, 5.6, 4.8, M['trou'], group='leg%d' % sx, folds=lambda u, sd: -0.25 if abs(sd) < 0.12 else 0)
        r.ellipsoid(foot[0] + 3, 169.5, 8.0, 3.4, M['shoe'], group='shoe%d' % sx)
    # the torso: shirt, waistcoat with buttons, the tie, a name badge
    r.poly([(54, 60 + b), (72, 60 + b), (79, 66 + b), (80, 80), (78, 112), (48, 112), (46, 80), (47, 66 + b)], M['shirt'], group='shirt')
    r.ellipsoid(49, 67 + b, 6.0, 5.0, M['shirt'], group='shoulderL'); r.ellipsoid(78, 67 + b, 6.0, 5.0, M['shirt'], group='shoulderR')
    r.poly([(50, 66 + b), (58, 64 + b), (60, 84), (62, 114), (47, 114), (46, 82)], M['vest'], group='vestL',
           vfun=lambda x, y: -0.3 if (x + y // 2) % 9 == 0 and y > 80 else 0)
    r.poly([(68, 64 + b), (77, 66 + b), (80, 82), (79, 114), (64, 114), (66, 84)], M['vest'], group='vestR',
           vfun=lambda x, y: -0.3 if (x - y // 2) % 9 == 0 and y > 80 else 0)
    r.poly([(60, 64 + b), (66, 64 + b), (65, 70 + b), (61, 70 + b)], M['tie'], group='knot')
    r.poly([(61, 70 + b), (65, 70 + b), (67, 98), (63, 102), (59, 98)], M['tie'], group='tie',
           vfun=lambda x, y: 0.25 if (y // 3) % 3 == 0 else 0)                                         # a striped tie
    for k in range(4): r.fixed(64 + k * 0.6, 84 + k * 7, VEST[5]); r.fixed(65 + k * 0.6, 84 + k * 7, (190, 170, 110))   # buttons
    for x in range(70, 77):
        for y in range(76, 80): r.fixed(x, y, PAPER[4] if 71 <= x <= 75 and y in (77, 78) and (x + y) % 2 else PAPER[2])   # the badge
    r.fixed(71, 77, (40, 40, 60)); r.fixed(73, 78, (40, 40, 60))
    r.tube((46, 113), (81, 113), 1.8, 1.8, Mat(SHOE, 'leather', 0.2, 0.6), group='belt')
    # the far (left) arm: elbow down, the clipboard held in its crook against the chest
    shL = (49, 68 + b)
    leaf = P['leaf']
    handL = (47, 98)
    el = ik(shL, handL, 18, 17, 'down')
    r.tube(shL, el, 4.8, 4.3, M['shirt'], group='armL', folds=lambda u, sd: -0.25 if u > 0.8 and sd > 0 else 0)
    r.tube(el, handL, 4.3, 3.8, M['shirt'], group='armL')
    bx, by = 52, 82 + b
    r.poly([(bx - 6, by), (bx + 14, by - 4), (bx + 17, by + 22), (bx - 3, by + 26)], M['board'], group='board')
    r.poly([(bx - 4, by + 2), (bx + 13, by - 2), (bx + 15, by + 21), (bx - 1, by + 24)], M['paper'], group='paper',
           vfun=lambda x, y: -0.25 if (y - x // 5) % 3 == 0 else 0)                                      # typed lines
    if leaf:                                                                                       # a page lifted, turning
        lift_ = [0, 8, 14][leaf]
        r.poly([(bx - 3, by + 1), (bx + 13, by - 3), (bx + 13 - lift_ * 0.4, by - 3 - lift_), (bx - 3 + lift_ * 0.2, by + 1 - lift_ * 0.9)],
               Mat(PAPER, 'plain', 0.45), group='page')
    for k in range(4): r.fixed(bx + 3 + k, by - 2 - (k > 1), (150, 150, 140))                     # the clip
    r.ellipsoid(handL[0], handL[1] + 1, 3.2, 3.6, M['skin'], group='handL')                         # holding the board's edge
    for k in range(3): r.tube((handL[0] + 1, handL[1] - 1 + k * 2.0), (handL[0] + 5.5, handL[1] - 1.5 + k * 2.2), 1.0, 0.85, M['skin'], group='fingL')
    seam(r, 'armL', 0.25)
    # the head: a bulbous olive mantle, big yellow eyes behind round glasses, a small mouth
    hx, hy = 63, 40 + b
    r.ellipsoid(hx, hy + 14, 7.0, 6.0, M['skin'], group='neck')
    r.ellipsoid(hx, hy, 15.5, 17.0, M['skin'], group='head',
                vfun=lambda x, y, u, w: (0.2 if h32(x // 2, y // 2, 5) % 11 == 0 else 0) + (-0.2 if w > 0.55 else 0))
    for (dx, dy, rr) in ((-9, -8, 2.4), (8, -11, 2.0), (11, 2, 1.6), (-12, 3, 1.8)):              # warts on the mantle
        r.ellipsoid(hx + dx, hy + dy, rr, rr, M['skin'], lift=0.15, group='wart')
    eyes = ((hx - 6.5, hy + 1), (hx + 7.0, hy + 0))
    look = (1.0, 0.3)
    for (ex, ey) in eyes:
        r.ellipsoid(ex, ey, 5.6, 5.8, Mat(EYE, 'plain', 0.4, 0.6), group='eye%d' % int(ex))
        r.ellipsoid(ex + look[0], ey + look[1], 2.6, 2.8, Mat(R('#050505 #101010 #1c1c1a'), 'plain', 0.3), lift=-0.3, group='pupil%d' % int(ex))
        r.fixed(ex - 1.5, ey - 2.5, (255, 248, 210))
    gl = P['glasses']
    gy = [0, -1, -2][gl]                                                                          # pushed up the nose
    for (ex, ey) in eyes:                                                                         # heavy, bored lids
        r.ellipsoid(ex, ey - 3.2, 6.0, 3.0, M['skin'], lift=0.05, group='lid%d' % int(ex),
                    clip=lambda x, y, ey=ey: y < ey - 1.2)
    RIM = (34, 26, 16); HI = (214, 196, 140)
    for (ex, ey) in eyes:
        for k in range(36):
            a = k / 36 * 2 * math.pi
            for rr in (6.6, 7.3):
                r.fixed(ex + math.cos(a) * rr, ey + gy + math.sin(a) * rr, HI if (math.sin(a - 2.4) > 0.75 and rr < 7) else RIM)
    for k in range(4): r.fixed(hx - 1.5 + k, hy + gy - 1 - (k in (1, 2)), RIM)                     # the bridge
    for (x, y) in ((hx - 14, hy + gy), (hx - 15, hy + gy + 1), (hx + 14.5, hy + gy - 1), (hx + 15.5, hy + gy)): r.fixed(x, y, RIM)
    for k in range(-2, 3): r.fixed(hx + 1 + k, hy + 11 + (abs(k) == 2) * -1, SKIN[0])                # a pursed little mouth
    # the tentacles: a crown curling slowly
    BASES = [(-11, -9, 2.3, -1), (-6, -14, 2.6, -1), (0, -16, 2.8, 1), (6, -14, 2.6, 1), (11, -9, 2.3, 1), (-14, -1, 2.0, -1), (14, -1, 2.0, 1)]
    for i, (dx, dy, r0, side) in enumerate(BASES):
        pts = []
        ln = 18 + (h32(i, 3) % 7)
        ang0 = math.atan2(dy, dx * 1.2)
        for j in range(8):
            u = j / 7
            ang = ang0 + side * u * (1.4 + 0.5 * math.sin(t + i * 1.3)) + 0.25 * math.sin(t * 1.3 + i + u * 3)
            if j == 0: x, y = hx + dx, hy + dy
            else: x, y = pts[-1][0] + math.cos(ang) * ln / 7, pts[-1][1] + math.sin(ang) * ln / 7 * 0.9 - (1.4 if u < 0.5 else 0)
            pts.append((x, y))
        n = len(pts) - 1
        for k in range(n):
            r.tube(pts[k], pts[k + 1], r0 * (1 - k / n * 0.75), r0 * (1 - (k + 1) / n * 0.75), M['skin'], group='tent%d' % i,
                   lift=-0.12 if dy > -3 else 0.0)
        for k in range(1, n, 2): r.fixed(pts[k][0] + side * 0.6, pts[k][1] + 1, SKIN[6])               # suckers
    # the near (right) arm: the pen -- at his side, up to the glasses, or tapping the clipboard
    shR = (78, 68 + b)
    if gl: handR = ((hx + 7, hy + 8) if gl == 1 else (hx + 2, hy + 4))
    elif P['tap']: handR = (bx + 12 - P['tap'], by + 10 - P['tap'] * 2)
    else: handR = (82, 106)
    el = ik(shR, handR, 19, 18, lambda e: e[1] * 0.6 + e[0])
    r.tube(shR, el, 5.0, 4.5, M['shirt'], group='armR', folds=lambda u, sd: -0.25 if u > 0.85 and sd < 0 else 0)
    r.tube(el, handR, 4.5, 4.0, M['shirt'], group='armR')
    r.ellipsoid(handR[0], handR[1] + 1, 3.6, 3.4, M['skin'], group='handR')
    if gl:
        r.tube((handR[0] - 1, handR[1] - 1), (handR[0] - 2, handR[1] - 7), 1.0, 0.8, M['skin'], group='fingR')   # one finger on the bridge
    else:
        pen0 = (handR[0] - 1, handR[1] + 2); pen1 = (handR[0] - 6, handR[1] - 6) if P['tap'] else (handR[0] + 1, handR[1] + 9)
        r.tube(pen0, pen1, 0.9, 0.8, Mat(R('#0a0a0a #1a1a1a #2c2c2c #444444'), 'metal', 0.3, 0.8), group='pen')
    seam(r, 'armR', 0.28)
    return r.render()

if __name__ == '__main__':
    os.makedirs(f'{OUT}/clerk', exist_ok=True)
    frames = [clerk(p) for p in POSE]
    sheet = Image.new('RGBA', (128 * len(frames), 176), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        im.save(f'{OUT}/clerk/{i}.png'); sheet.paste(im, (i * 128, 0))
    sheet.save(f'{OUT}/clerk.png')
    ALL = [INK] + SKIN + EYE + SHIRT + TIE + VEST + TROU + SHOE + BOARD + PAPER + WIRE
    seen, rows = set(), []
    for c in ALL:
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/clerk.gpl', 'w').write('GIMP Palette\nName: clerk\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT)
