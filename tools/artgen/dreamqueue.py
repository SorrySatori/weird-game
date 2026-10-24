"""The dream queue of the Shed 521 registration yard (ShedRegistrationScene), drawn with the character renderer
(rig.py, the Edgar quality bar) to match how the dialogs describe them. 128x160 frames, facing the viewer, feet on
y 156, idle loops of 6 frames:
  mime          the Sleepless Mime: a hooded, stooped figure in a long coat over a striped mime shirt, a rusting
                riveted faceplate with eye slits, white gloves -- it pantomimes a box (a die) in the air
  vowel_seller  the Vowel Seller: a tall, gaunt, ash-covered man in a long open coat lined with tiny vials, each
                with a glowing letter in fluid; he holds up a vial with a pulsing A, ash flakes drift off him
  hollow_woman  the Hollow Woman: a pale, faded woman with empty eyes and stitched seams, long lank hair, her left
                arm ends at the elbow, neatly stitched; she sways, waiting forever
python3 dreamqueue.py <outdir>  ->  <id>.png (6-frame sheet) + <id>/<n>.png + dreamqueue.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK, h32
from rig import Rig, Mat
from feral_toast import ik, lerp

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
R = ramp
COAT  = R('#0e1014 #171a20 #21252d #2c313b #383e4a #464d5a #565e6c #687080')
TROU  = R('#0a0a0b #131315 #1d1d20 #28282c')
RUSTP = R('#24120a #3a1d10 #552a16 #6f381d #8a4a26 #a35e33 #b9764a')
GLOVE = R('#5e5c56 #7e7c74 #9c9a90 #b8b6aa #d2d0c4 #e8e6da')
ASH   = R('#1c1c1b #2a2a28 #3a3a37 #4b4b47 #5e5e59 #74746e #8c8c85 #a6a69e')
ASHSK = R('#2e2c28 #45423b #5d5950 #767166 #8f8a7d #a8a294')
LINING= R('#1a0e12 #28161c #381f27 #4a2a33')
DRESS = R('#16190f #20241a #2b3123 #373f2d #444e38 #536045 #637153')
PALE  = R('#3c3e36 #565a4e #727668 #8f9384 #aaae9e #c2c5b4')
HAIR  = R('#0c0c0a #151512 #1f1f1a #2a2a23')
STITCH = (28, 22, 18)
VIALS = [(255, 214, 110), (120, 232, 255), (255, 120, 190), (160, 255, 150), (255, 160, 90)]
RUSTP_M = Mat(R('#2a140b #43200f #5e2e17 #7a3f20 #985330 #b56c45 #cf8c62'), 'metal', 0.24, 0.3)
M = {'coat': Mat(COAT, 'wool', 0.2), 'trou': Mat(TROU, 'fabric', 0.18), 'plate': Mat(RUSTP, 'metal', 0.22, 0.6),
     'glove': Mat(GLOVE, 'fabric', 0.3), 'ash': Mat(ASH, 'wool', 0.22), 'ashsk': Mat(ASHSK, 'skin', 0.24, 0.1),
     'lining': Mat(LINING, 'fabric', 0.2), 'dress': Mat(DRESS, 'wool', 0.22), 'pale': Mat(PALE, 'skin', 0.28, 0.15),
     'hair': Mat(HAIR, 'fur', 0.2)}

from hero import seam

def crease(x, y, cx, every, y0):
    """long vertical folds fanning out from the centre line below y0: a dark fold line, a lit edge beside it"""
    if y < y0: return 0.0
    u = (x - cx) * (1 - 0.25 * min(1.0, (y - y0) / 80)) / every
    d = u - math.floor(u)
    return -0.32 if d < 0.14 else (0.12 if d < 0.3 else 0.0)

def glove(r, hand, palm_up=False, g='glove'):
    """a white glove, palm flat as on an invisible wall, fingers together"""
    r.ellipsoid(hand[0], hand[1], 3.3, 3.7, M['glove'], group=g)
    for k in range(4):
        fx = hand[0] - 2.1 + k * 1.4
        tip = (fx, hand[1] - 6.0 + abs(k - 1.5) * 0.6) if not palm_up else (fx + 5.0, hand[1] - 0.8)
        r.tube((fx, hand[1] - 1.5), tip, 0.8, 0.7, M['glove'], group=g)
    r.tube((hand[0] - 3.2, hand[1] + 0.5), (hand[0] - 4.6, hand[1] - 2.5), 0.9, 0.8, M['glove'], group=g)   # the thumb

def mime(f):
    """stooped from sleeplessness, a theatrical coat over the striped shirt, the rusting faceplate pushed forward"""
    r = Rig(128, 160)
    sway = [0, 1, 1, 0, -1, 0][f]
    for sx in (-1, 1):                                                                            # thin legs, slightly bent
        knee = (64 + sx * 5, 128)
        r.tube((64 + sx * 5, 104), knee, 4.6, 4.0, M['trou'], group='leg%d' % sx)
        r.tube(knee, (64 + sx * 6, 149), 4.0, 3.4, M['trou'], group='leg%d' % sx)
        r.ellipsoid(64 + sx * 8, 152.5, 7.0, 3.0, Mat(TROU, 'leather', 0.18, 0.7), group='shoe%d' % sx)
    S = sway
    coat = [(58 + S, 52), (72 + S, 52), (82 + S, 58), (84 + S, 68), (82, 100), (87, 132), (78, 134), (66, 130), (54, 134), (43, 132), (48, 100), (46 + S, 68), (48 + S, 58)]
    r.poly(coat, Mat(COAT, 'fabric', 0.2), group='coat',
           vfun=lambda x, y: crease(x, y, 64, 7.5, 66))
    r.poly([(60 + S, 56), (70 + S, 56), (70, 98), (60, 98)], Mat(GLOVE, 'fabric', 0.2), group='shirt',
           vfun=lambda x, y: 0.55 if (y // 4) % 2 else -0.5)
    r.poly([(58 + S, 54), (62 + S, 56), (61, 98), (56, 100)], M['coat'], lift=0.12, group='lapelL')
    r.poly([(68 + S, 56), (72 + S, 54), (75, 100), (70, 98)], M['coat'], lift=0.12, group='lapelR')
    hx, hy = 66 + S, 40                                                                            # the head pushed forward
    r.poly([(hx - 14, hy + 4), (hx + 12, hy + 4), (hx + 15, hy + 16), (hx - 17, hy + 16)], M['coat'], group='drape')
    r.ellipsoid(hx - 1, hy - 1, 13.5, 15, M['coat'], group='hood')
    r.ellipsoid(hx, hy + 1, 9.6, 11.4, M['coat'], lift=-0.7, group='hoodin')
    STP = Mat(R('#1e2224 #2e3437 #40484b #545d60 #6b7577 #869091 #a4adab'), 'metal', 0.24, 0.8)
    rust = lambda x, y: h32(x // 2, y // 2, 61) % 7 < 3 or (y > hy + 4 and h32(x, 62) % 3 == 0)          # rust eating the steel
    r.ellipsoid(hx + 0.5, hy + 1.5, 7.6, 9.4, STP, group='plate',
                vfun=lambda x, y, u, w: (0.2 if u * u + w * w > 0.8 else 0))
    pl = r.groups
    for (x_, y_), e in list(r.buf.items()):
        if e[0] is STP and rust(x_, y_): e[0] = RUSTP_M
    for (dx, dy) in ((-5, -6), (5, -6), (-6, 4), (6, 4), (0, -8)): r.fixed(hx + 0.5 + dx, hy + 1.5 + dy, (200, 206, 200))   # rivets
    blink = f == 4
    for ex in (-3.2, 3.6):                                                                          # eye slits, sleepless eyes
        for k in range(-2, 3): r.fixed(hx + ex + k, hy, (12, 8, 6))
        r.fixed(hx + ex + 0.5, hy, (12, 8, 6) if blink else (232, 226, 196))
        r.fixed(hx + ex, hy + 2, (60, 34, 24)); r.fixed(hx + ex + 1, hy + 2, (60, 34, 24))          # the shadow under them
    r.fixed(hx - 3, hy + 3, (20, 16, 14)); r.fixed(hx - 3, hy + 4, (20, 16, 14))                       # a painted tear
    for k in range(-3, 4): r.fixed(hx + 0.5 + k, hy + 6 + (abs(k) == 3) - (k == 0), (36, 20, 14))     # a painted smile
    POSES = [((48, 84), (82, 84), False, False), ((48, 84), (82, 84), False, False), ((53, 70), (77, 70), True, True),
             ((48, 86), (65, 70), False, True), ((50, 92), (80, 92), False, False), ((48, 84), (82, 84), False, False)]
    hl, hr_, upl, upr = POSES[f]
    for (sh, hand, up, sx) in (((49 + S, 60), hl, upl, -1), ((81 + S, 60), hr_, upr, 1)):
        wrist = (hand[0], hand[1] + 3)
        el = ik(sh, wrist, 17, 16, lambda e, sx=sx: e[1] * 0.5 + e[0] * sx)
        r.tube(sh, el, 4.3, 3.9, M['coat'], group='arm%d' % sx, folds=lambda t, sd: -0.25 if t > 0.85 else 0)
        r.tube(el, wrist, 3.9, 3.5, M['coat'], group='arm%d' % sx)
        glove(r, hand, palm_up=up, g='glove%d' % sx)
        seam(r, 'arm%d' % sx, 0.28)
    seam(r, 'plate', 0.3)
    return r.render()

def vowel_seller(f):
    """tall and gaunt, ash-grey from head to foot, his open coat lined with vials of glowing letters"""
    r = Rig(128, 160)
    for sx in (-1, 1):
        r.tube((64 + sx * 4, 100), (64 + sx * 5, 149), 3.6, 3.0, M['trou'], group='leg%d' % sx)
        r.ellipsoid(64 + sx * 7, 152.5, 6.0, 2.8, Mat(TROU, 'leather', 0.18, 0.5), group='shoe%d' % sx)
    coat = [(56, 44), (72, 44), (79, 48), (81, 58), (80, 92), (88, 146), (40, 146), (48, 92), (47, 58), (49, 48)]
    r.poly(coat, Mat(ASH, 'fabric', 0.22), group='coat',
           vfun=lambda x, y: crease(x, y, 64, 8.0, 60) + (0.25 if h32(x // 2, y // 3, 4) % 23 == 0 else 0))
    r.poly([(58, 48), (70, 48), (71, 100), (57, 100)], Mat(R('#1e1e1b #2a2a26 #383833 #474741 #57574f'), 'fabric', 0.2), group='waistcoat',
           vfun=lambda x, y: -0.5 if x == 64 else 0)
    for k in range(4): r.fixed(63, 56 + k * 10, ASH[6])                                            # waistcoat buttons
    for side, x0 in ((-1, 49), (1, 72)):                                                           # the open coat's lining with vial loops
        pts = [(x0, 54), (x0 + 7, 54), (x0 + 7 + side * 4, 140), (x0 + side * 4, 140)]
        r.poly(pts, M['lining'], lift=-0.1, group='lining%d' % side)
        for row in range(7):
            for col in range(2):
                vx, vy = int(x0 + 2 + col * 3 + side * row * 0.5), 60 + row * 11
                c = VIALS[h32(row, col, side) % len(VIALS)]
                lit = (f + row * 2 + col) % 4 != 0
                r.fixed(vx, vy - 2, (110, 90, 70))                                                   # the cork
                r.fixed(vx, vy - 1, (170, 186, 184))
                r.fixed(vx, vy, c if lit else tuple(v // 2 for v in c)); r.fixed(vx, vy + 1, c if lit else tuple(v // 3 for v in c))
                r.fixed(vx, vy + 2, (150, 166, 164))
        r.poly([(x0 + (0 if side < 0 else 6), 46), (x0 + (6 if side < 0 else 0), 46), (x0 + 3 + side * 4, 82)], M['ash'], lift=0.15, group='lapel%d' % side)
    hx, hy = 64, 24                                                                                # the gaunt, ash-grey head
    r.ellipsoid(hx, hy + 11, 4.0, 5.0, M['ashsk'], group='neck')
    r.ellipsoid(hx, hy, 7.6, 11, M['ashsk'], group='head',
                vfun=lambda x, y, u, w: (0.3 if h32(x, y, 3) % 6 == 0 else 0) + (-0.35 if abs(u) > 0.55 and w > 0.05 else 0) + (-0.3 if h32(x // 2, y, 8) % 17 == 0 else 0))
    for ex in (-3.2, 3.2):
        r.ellipsoid(hx + ex, hy - 1, 2.4, 2.2, M['ashsk'], lift=-0.7, group='socket')
        r.fixed(hx + ex, hy - 1, (216, 210, 180))
    r.fixed(hx - 1, hy + 7, ASHSK[0]); r.fixed(hx, hy + 7, ASHSK[1]); r.fixed(hx + 1, hy + 7, ASHSK[0])
    r.ellipsoid(hx, hy + 3, 1.2, 2.2, M['ashsk'], lift=0.1, group='nose')
    sh, hand = (50, 50), (38, 30 + [0, -1, -1, 0, 1, 0][f])                                        # the raised hand, the vial
    el = ik(sh, hand, 16, 16, lambda e: e[1] - e[0] * 0.6)
    r.tube(sh, el, 4.0, 3.6, M['ash'], group='armL'); r.tube(el, (hand[0], hand[1] + 3), 3.6, 3.2, M['ash'], group='armL')
    r.ellipsoid(hand[0], hand[1] + 1, 2.8, 3.2, M['ashsk'], group='handL')
    seam(r, 'armL', 0.3)
    sh2, hand2 = (78, 50), (84, 94)
    el2 = ik(sh2, hand2, 23, 22, lambda e: e[0])
    r.tube(sh2, el2, 4.0, 3.6, M['ash'], group='armR'); r.tube(el2, hand2, 3.6, 3.2, M['ash'], group='armR')
    r.ellipsoid(hand2[0], hand2[1] + 2, 2.8, 3.4, M['ashsk'], group='handR')
    seam(r, 'armR', 0.28)
    img = r.render()
    px = img.load()
    vx, vy = hand[0], hand[1] - 10
    pulse = [0, 1, 2, 1, 0, 1][f]
    if pulse:                                                                                    # the vial's glow
        for dy in range(-9, 10):
            for dx in range(-7, 8):
                d = math.hypot(dx, dy * 0.8)
                if 4.5 < d < 4.5 + pulse * 2 and (dx + dy) % 2 == 0 and px[vx + dx, vy + dy][3] == 0:
                    px[vx + dx, vy + dy] = (200, 190, 110, 255) if d < 6 else (150, 140, 80, 255)
    for y in range(vy - 5, vy + 7):
        for x in range(vx - 2, vx + 3):
            edge = x in (vx - 2, vx + 2) or y in (vy - 5, vy + 6)
            px[x, y] = (156, 176, 174, 255) if edge else (36, 66 + pulse * 22, 58 + pulse * 18, 255)
    for (dx, dy) in ((0, -2), (-1, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (1, 1), (-1, 2), (1, 2)):   # the A
        px[vx + dx, vy + dy] = [(220, 210, 110), (255, 238, 150), (255, 255, 215)][pulse] + (255,)
    for k in (-1, 0, 1): px[vx + k, vy - 6] = (110, 84, 58, 255)                                    # the cork
    for k in range(16):                                                                          # ash drifting off him
        x0 = 44 + h32(k, 1) % 44; y0 = 16 + h32(k, 2) % 60
        y = (y0 + f * 4 + k * 3) % 150; x = x0 + int(math.sin((y + k) * 0.2) * 2)
        if 0 <= x < 128 and 0 <= y < 160:
            px[x, y] = (156, 156, 150, 255) if k % 3 else (196, 196, 188, 255)
    return img

def hollow_woman(f):
    """thin and faded, leaning a little, hair hanging lank around a pale stitched face with empty eyes"""
    r = Rig(128, 160)
    lean = 3
    sway = [0, 1, 2, 1, 0, -1][f]
    bob = [0, 0, 1, 1, 0, 0][f]
    hem = []
    for k in range(12):
        x = 86 + sway - k * 4.4
        hem.append((x, 152 + (3 if k % 2 else 0) + (h32(k, f // 2) % 2)))
    dress = [(57 + lean, 50 + bob), (71 + lean, 50 + bob), (78 + lean, 56 + bob), (77, 86), (80, 120), hem[0]] + hem[1:] + [(40 + sway, 150), (47, 120), (51, 86), (50 + lean, 56 + bob)]
    r.poly(dress, M['dress'], group='dress', vfun=lambda x, y: crease(x - sway * (y - 80) / 70, y, 64, 6.5, 80) + (-0.3 if y > 140 else 0))
    for (sx_, sy_, ln) in ((54, 74, 6), (66, 104, 8), (58, 128, 7), (72, 90, 5)):                     # stitched mends on the dress
        for j in range(ln): r.fixed(sx_ + j, sy_ + (j % 2), STITCH)
    sh, hand = (53 + lean, 56 + bob), (46 + sway * 0.5, 104 + bob)                                   # the right arm hangs, long fingers
    el = ik(sh, hand, 25, 24, lambda e: -e[0])
    r.tube(sh, el, 3.8, 3.2, M['dress'], group='armL'); r.tube(el, hand, 2.8, 2.2, M['pale'], group='armL')
    for k in range(4): r.tube((hand[0] - 1.5 + k * 1.1, hand[1]), (hand[0] - 2.0 + k * 1.2, hand[1] + 7 + (k % 2)), 0.7, 0.55, M['pale'], group='fingers')
    seam(r, 'armL', 0.3)
    st, el2 = (75 + lean, 56 + bob), (79 + lean, 72 + bob)                                           # the left ends at the elbow
    r.tube(st, el2, 4.0, 3.8, M['dress'], group='armR')
    r.ellipsoid(el2[0] + 0.5, el2[1] + 3.0, 3.0, 2.4, M['pale'], group='stump')
    for k in range(-1, 3):                                                                           # sewn shut, a neat row of stitches
        r.fixed(el2[0] - 1 + k * 1.5, el2[1] + 3, STITCH); r.fixed(el2[0] - 1 + k * 1.5, el2[1] + 2, (90, 80, 70)); r.fixed(el2[0] - 1 + k * 1.5, el2[1] + 4, (90, 80, 70))
    for k in range(5): r.fixed(el2[0] - 3 + k * 1.5, el2[1] - 0.5 + (k % 2), DRESS[0])                # the sleeve's frayed cuff
    seam(r, 'armR', 0.28)
    hx, hy = 64 + lean + 1, 30 + bob                                                                  # the head
    r.poly([(hx - 10, hy - 8), (hx + 10, hy - 8), (hx + 12 + sway * 0.6, hy + 36), (hx + 7, hy + 40), (hx - 7, hy + 40), (hx - 12 + sway * 0.6, hy + 34)], M['hair'], group='hairback')
    r.ellipsoid(hx, hy + 11, 3.2, 4.4, M['pale'], group='neck')
    r.ellipsoid(hx, hy, 7.4, 10.2, M['pale'], group='face',
                vfun=lambda x, y, u, w: -0.25 if abs(u) > 0.65 else 0)
    for ex in (-3.0, 3.2):
        r.ellipsoid(hx + ex, hy - 0.5, 2.3, 2.8, M['pale'], lift=-1.2, group='socket')               # empty eyes
    for k in (-1, 0, 1): r.fixed(hx + k, hy + 6, PALE[0])
    r.ellipsoid(hx + 0.3, hy + 2.6, 1.0, 1.8, M['pale'], lift=0.08, group='nose')
    for j in range(-9, 11):                                                                          # the seam: hairline to chin
        x = hx - 3 + j * 0.12; y = hy + j
        r.fixed(x, y, STITCH)
        if j % 3 == 0: r.fixed(x - 1, y - 1, STITCH); r.fixed(x + 1, y + 1, STITCH)
    for k in range(-3, 4):
        r.fixed(hx + k, hy + 11, STITCH)
        if k % 2 == 0: r.fixed(hx + k, hy + 10, STITCH)
    r.poly([(hx - 9, hy - 10), (hx + 9, hy - 10), (hx + 8, hy - 5), (hx + 2, hy - 8), (hx - 1, hy - 8), (hx - 8, hy - 4)], M['hair'], group='fringe')
    for k in range(3):                                                                               # lank strands framing the face
        for sx in (-1, 1):
            x0 = hx + sx * (8 + k * 2)
            r.stroke([(x0 + (j / 20) * (sway * 0.7 + sx), hy - 6 + j) for j in range(26 + k * 6)], 1.8, M['hair'], v=0.32, group='strand%d%d' % (k, sx))
    return r.render()

CAST = {'mime': mime, 'vowel_seller': vowel_seller, 'hollow_woman': hollow_woman}
if __name__ == '__main__':
    for name, fn in CAST.items():
        os.makedirs(f'{OUT}/{name}', exist_ok=True)
        frames = [fn(i) for i in range(6)]
        sheet = Image.new('RGBA', (128 * 6, 160), (0, 0, 0, 0))
        for i, im in enumerate(frames):
            im.save(f'{OUT}/{name}/{i}.png'); sheet.paste(im, (i * 128, 0))
        sheet.save(f'{OUT}/{name}.png')
    ALL = [INK] + COAT + TROU + RUSTP + GLOVE + ASH + ASHSK + LINING + DRESS + PALE + HAIR + [STITCH] + VIALS
    seen, rows = set(), []
    for c in ALL:
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/dreamqueue.gpl', 'w').write('GIMP Palette\nName: dreamqueue\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT)
