"""The dead Bishop in the abandoned bus (AbandonedBusScene), redrawn with the character renderer (rig.py, the Edgar
bar) after her old AI picture (DeadBishop.png): the Obazoba's Bishop slumped on the bus floor, her shoulders and
head fallen back against the bench, legs out along the aisle. Everything the examination dialog names is on her:

  * ceremonial robes, deep moss green with an ochre-gold yoke, hem and cuffs -- stained with pale fungal growth
  * her face pale and serene, eyes shut, a bruise at the temple under the helmet's strap
  * the homemade dream helmet still strapped on: a hammered tin cap, rivets, a tangle of wires curling up out of it
    (the old picture's "crown"), the visor pushed up with its one old lens in a brass ring, a tiny screen at the
    temple flickering its error
  * the portable dream device clutched in her hand, the Cardinal Feast cartridge in it, its cable up to the helmet
  * papers sticking out of her wide sleeve, a worn notebook on the floor by her hip, a small cloth bag of
    Sulkberries by her other hand, half of them spilled
  * Neme in her chest: a faint green glow under the robe

192x88 frames, bottom = the floor line (y 85); 4 frames, no breathing -- only the growth's faint green pulse and the
helmet screen's flicker:  0 dim, screen on  1 brighter  2 brightest, screen off  3 easing, screen on; frame 4 is not
in the animation: her head and shoulders centred, for the dialog's bust portrait
    python3 dead_bishop.py <outdir>  ->  dead_bishop.png (5-frame sheet) + dead_bishop/<n>.png + dead_bishop.gpl
"""
import sys, os, math
from PIL import Image
from common import ramp, make_noise, h32
from rig import Rig, Mat
from feral_toast import ik
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
W, H = 192, 88
R = ramp
ROBE  = R('#0d130e #132017 #1a291d #213324 #293e2c #324a35 #3d5840 #4a674c')
GOLD  = R('#2a1e0c #46331a #644a20 #82632a #a07c36 #bb9548 #d2ae60')
STAIN = R('#2a2d22 #383c2d #4a4f3b #5d634b #737a5d')          # the pale growth in the cloth
SKIN  = R('#2e2b28 #423d38 #57514a #6d665d #847c70 #9a9283 #ada697 #bfb9ab')   # pale, bloodless
BRUISE = [(64, 52, 70), (82, 66, 86), (98, 82, 98)]
TIN   = R('#101010 #181816 #21201d #2b2a26 #36342f #423f38 #504c43 #5f5a4f')
COPPER = R('#2a140c #462212 #6a3418 #8c4a22')
LEATH = R('#140d09 #20150e #2d1d13 #3b2619 #4a3120')
CLOTH = R('#2a2416 #3d3520 #52482c #685c39 #7e7046')          # the berry bag, sackcloth
BERRY = [(52, 16, 30), (84, 26, 44), (118, 40, 60), (150, 70, 84)]
PAPER = R('#5c5a4e #767364 #8f8b7a #a7a28f')
DEV   = R('#101211 #191c1a #232724 #2e332f #3a403b')
SCREEN_ON = [(150, 40, 30), (214, 92, 48)]                     # the error, red-amber
LENS  = [(70, 86, 80), (104, 124, 114), (150, 168, 154), (210, 220, 200)]
MYC   = [(20, 58, 34), (31, 90, 50), (63, 143, 90), (127, 255, 142), (200, 255, 208)]
INK = (8, 9, 8)
RIM = (178, 192, 182)                                        # the overcast light from the roof hole

M = {'robe': Mat(ROBE, 'wool', 0.22), 'gold': Mat(GOLD, 'metal', 0.26, 0.6), 'skin': Mat(SKIN, 'skin', 0.34, 0.1),
     'tin': Mat(TIN, 'metal', 0.24, 0.9), 'leath': Mat(LEATH, 'leather', 0.22, 0.3), 'cloth': Mat(CLOTH, 'fabric', 0.24),
     'dev': Mat(DEV, 'plain', 0.24, 0.6), 'paper': Mat(PAPER, 'plain', 0.4), 'shoe': Mat(LEATH, 'leather', 0.2, 0.4),
     'copper': Mat(COPPER, 'metal', 0.3, 0.7)}
nS = make_noise(3, 211, W, H); nL = make_noise(7, 212, W, H)

PULSE = [0.0, 0.5, 1.0, 0.45]
SCREEN = [1, 1, 0, 1]


def cuff(r, a, b, rad, group):
    """the gold band round a wide sleeve's mouth: a thin ring across the sleeve's end"""
    dx, dy = b[0] - a[0], b[1] - a[1]; L_ = math.hypot(dx, dy) or 1
    ux, uy = dx / L_, dy / L_; px_, py_ = -uy, ux
    for k in range(-int(rad * 2), int(rad * 2) + 1):
        t = k / 2.0
        for j, c in ((0, GOLD[4]), (1, GOLD[2]), (-1, GOLD[1])):
            x_, y_ = b[0] - ux * (1.4 + j * 0.9) + px_ * t, b[1] - uy * (1.4 + j * 0.9) + py_ * t
            e = r.buf.get((int(x_), int(y_)))
            if e and r.groups[e[2]] in ('armN', 'armF'): r.fixed(x_, y_, c if abs(t) < rad - 1 else GOLD[1])


def bishop(fr):
    r = Rig(W, H)
    pulse = PULSE[fr]
    fold = lambda k, a, b=0.0: (lambda x, y: (-0.22 if (x * a + y) % k < 1 else (0.1 if (x * a + y) % k < 2 else 0)) + b)
    # ---- the far arm hangs down her back to the floor; papers stick out of its wide sleeve
    shF, elF, hF = (139, 47), (147, 64), (156, 78)
    r.tube(shF, elF, 5.0, 5.4, M['robe'], lift=-0.1, group='armF')
    r.tube(elF, (hF[0] - 2, hF[1] - 3), 5.4, 7.0, M['robe'], lift=-0.05, group='armF', folds=lambda u, sd: -0.2 if (u * 4) % 1 < 0.15 else 0)
    cuff(r, elF, (hF[0] - 2, hF[1] - 3), 6.6, 'cuffF')
    r.poly([(hF[0] - 6, hF[1] - 12), (hF[0] - 1, hF[1] - 15), (hF[0] + 2, hF[1] - 10), (hF[0] - 3, hF[1] - 7)], M['paper'], lift=0.15, group='paperA')
    r.poly([(hF[0] - 3, hF[1] - 11), (hF[0] + 3, hF[1] - 13), (hF[0] + 4, hF[1] - 9), (hF[0] - 1, hF[1] - 7)], M['paper'], lift=0.3, group='paperB')
    for k in range(3): r.fixed(hF[0] - 2 + k * 1.6, hF[1] - 11 + k * 0.2 - k * 0.4, PAPER[0])                 # ink lines
    r.ellipsoid(hF[0] + 2, hF[1] + 1, 3.2, 2.2, M['skin'], group='handF')
    for k in range(3): r.tube((hF[0] + 3 + k * 1.4, hF[1] + 1.5), (hF[0] + 5 + k * 1.1, hF[1] - 0.5), 0.8, 0.7, M['skin'], group='handF')
    # ---- the robe pooled round her on the floor
    r.poly([(60, 85), (84, 80), (112, 81), (140, 78), (150, 84), (150, 86), (58, 86)], M['robe'], lift=-0.18, group='pool', round_=0.3)
    # ---- the legs under the skirt: the knees a little up, the slippers out of the hem
    for (fx, fy, k) in ((47, 79, 0), (52, 82, 1)):
        r.ellipsoid(fx, fy, 4.4, 2.6, M['shoe'], rot=-0.5, lift=0.06 * k, group='foot%d' % k)
    skirt = [(104, 66), (90, 64), (78, 66), (66, 71), (56, 77), (54, 84), (70, 85), (100, 85), (118, 84), (116, 74)]
    r.poly(skirt, M['robe'], group='skirt', round_=0.75, vfun=fold(11, 2, 0.0))
    r.poly([(98, 66), (84, 65), (74, 68), (82, 70), (96, 70)], M['robe'], lift=0.22, group='knee', round_=0.6)   # light on the knees
    for x in range(55, 112):                                                                       # the gold hem
        yy = 84 - (2 if x < 60 else 0)
        r.fixed(x, yy, GOLD[3] if (x // 3) % 2 else GOLD[2]); r.fixed(x, yy + 1, GOLD[1])
    # ---- the torso: slumped back against the bench, three-quarters to us
    torso = [(116, 84), (142, 49), (140, 40), (133, 36), (125, 38), (114, 52), (105, 63), (98, 72), (104, 80)]
    r.poly(torso, M['robe'], group='torso', round_=0.85, vfun=fold(9, -1, 0.0))
    # the gold yoke: a V over the chest from the shoulders, its point at the breastbone
    for (a, b) in (((126, 39), (120, 56)), ((138, 40), (121, 56))):
        n = 16
        for i in range(n + 1):
            t = i / n
            x_, y_ = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            r.fixed(x_ - 1, y_, GOLD[5]); r.fixed(x_, y_, GOLD[3]); r.fixed(x_ + 1, y_, GOLD[1])
    r.fixed(121, 57, GOLD[4]); r.fixed(120, 58, GOLD[2]); r.fixed(122, 58, GOLD[2]); r.fixed(121, 59, GOLD[1])   # a clasp
    # Neme under the robe at the breastbone: a faint green glow, pulsing
    gx, gy = 117, 62
    for y in range(gy - 6, gy + 7):
        for x in range(gx - 7, gx + 8):
            d = math.hypot((x - gx) / 7.0, (y - gy) / 5.0)
            e = r.buf.get((x, y))
            if d > 1 or not e or e[0] is not M['robe']: continue
            k = (1 - d) * (0.3 + 0.7 * pulse)
            if k > 0.5 and (x + y) % 2 == 0: r.fixed(x, y, MYC[2] if k < 0.72 else MYC[3])
            elif k > 0.22 and (x * 3 + y) % 4 == 0: r.fixed(x, y, MYC[1])
            elif k > 0.08: e[1] += 0.1
    # ---- the near arm: across the body to the hand in her lap, which still grips the dream device
    shN, elN, hN = (124, 45), (110, 59), (98, 70)
    r.tube(shN, elN, 5.0, 5.2, M['robe'], lift=0.08, group='armN', folds=lambda u, sd: -0.22 if u > 0.82 and sd > 0 else 0)
    r.tube(elN, (hN[0] + 4, hN[1] - 2), 5.2, 6.6, M['robe'], lift=0.08, group='armN', folds=lambda u, sd: -0.18 if (u * 4) % 1 < 0.15 else 0)
    cuff(r, elN, (hN[0] + 4, hN[1] - 2), 6.4, 'cuffN')
    # the device: a palm-sized box, the cartridge in its top slot (red label), a little dark screen
    r.poly([(88, 66), (97, 64), (99, 71), (90, 73)], M['dev'], lift=0.12, group='device')
    r.poly([(89, 62), (94, 61), (95, 65), (90, 66)], M['dev'], lift=0.32, group='cart')
    for (x, y, c) in ((90, 63, (120, 42, 38)), (91, 63, (152, 60, 46)), (92, 62, (152, 60, 46)), (93, 62, (110, 38, 34))):
        r.fixed(x, y, c)
    for (x, y) in ((91, 68), (92, 68), (93, 67), (94, 67), (92, 69), (93, 69), (94, 68), (95, 68)):
        r.fixed(x, y, (40, 58, 50) if (x + y) % 2 else (50, 72, 60))
    r.ellipsoid(hN[0], hN[1] + 0.5, 3.4, 2.8, M['skin'], group='handN')
    for k in range(3): r.tube((hN[0] - 1, hN[1] + k * 1.3 - 1), (hN[0] - 5, hN[1] + k * 1.5 - 1.5), 0.9, 0.8, M['skin'], group='handN')
    r.tube((hN[0] - 1, hN[1] - 2), (hN[0] - 4, hN[1] - 5), 0.9, 0.8, M['skin'], group='handN')            # the thumb over the top
    # ---- the neck and the head, fallen back against the seat; the helmet still strapped on
    r.tube((131, 38), (133, 33), 3.6, 3.4, M['skin'], lift=-0.1, group='neck')
    hx, hy = 135, 27
    r.ellipsoid(hx, hy, 7.0, 8.2, M['skin'], rot=-0.5, group='head')
    # the face (light from above-left): pale and still, eyes shut, three-quarters to the left and tipped up
    L = (-0.45, -0.75, 0.5)
    for y in range(18, 38):
        for x in range(126, 144):
            e = r.buf.get((x, y))
            if not e or r.groups[e[2]] != 'head': continue
            u, w = (x + 0.5 - (hx - 1.5)) / 6.4, (y + 0.5 - (hy + 1)) / 7.6
            d = min(0.99, u * u + w * w)
            n = (u, w, math.sqrt(1 - d))
            v = 0.32 + 0.68 * max(0.0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2])
            r.fixed(x, y, SKIN[max(1, min(7, 1 + int(v * 6.4)))])
    for (x, y, c) in ((129, 27, SKIN[1]), (130, 27, SKIN[1]), (131, 28, SKIN[2]),          # the near eye, shut: a lid line
                      (134, 26, SKIN[2]), (135, 26, SKIN[1]), (136, 27, SKIN[2]),          # the far eye
                      (129, 25, SKIN[3]), (130, 25, SKIN[4]), (134, 24, SKIN[3]),          # the brow
                      (128, 29, SKIN[6]), (128, 30, SKIN[3]), (129, 31, SKIN[2]),          # the nose, its tip lit
                      (130, 33, SKIN[2]), (131, 33, (74, 54, 54)), (132, 33, SKIN[2]),     # the mouth, closed
                      (131, 35, SKIN[5]), (132, 36, SKIN[3]), (127, 31, SKIN[5])):         # the chin, the cheek
        r.fixed(x, y, c)
    # the helmet: a hammered tin cap over the crown and the back of the skull, a riveted band at the brow
    def capclip(x, y): return (x - hx) * 0.7 + (hy - y) * 1.0 > 0.5
    r.ellipsoid(hx + 1.2, hy - 1.0, 8.6, 8.4, M['tin'], rot=-0.5, group='helmet', clip=capclip,
                vfun=lambda x, y, u, w: (0.18 if h32(x // 2, y // 2, 7) % 5 == 0 else 0) - (0.15 if h32(x, y, 8) % 6 == 0 else 0))
    for (x, y) in ((131, 20), (135, 18), (140, 19), (143, 23)):                                       # rivets on the band
        r.fixed(x, y, TIN[7]); r.fixed(x + 1, y + 1, TIN[1])
    # the visor pushed up off the brow, its one old lens in a brass ring
    r.poly([(124, 21), (130, 15), (133, 17), (128, 24)], M['tin'], lift=0.18, group='visor')
    lx, ly = 127, 19
    for a in range(16):
        t = a / 16 * 2 * math.pi
        r.fixed(lx + math.cos(t) * 2.5, ly + math.sin(t) * 2.5, GOLD[5] if math.sin(t) < 0 else GOLD[2])
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            r.fixed(lx + dx, ly + dy, LENS[2] if dy < 0 else LENS[1])
    r.fixed(lx - 1, ly - 1, LENS[3])
    # the tangle of wires curling up out of the cap (the old picture's crown): thin, dark, one copper, one red
    for (x0, y0, ln, cw, col) in ((134, 18, 8, 1, 0), (138, 17, 10, -1, 1), (141, 19, 7, 1, 2), (143, 22, 8, 1, 3)):
        pts = []; a = -1.75 + (x0 - 138) * 0.1; x_, y_ = x0, y0
        for i in range(ln):
            pts.append((x_, y_)); a += cw * 0.34 * (1 + i / ln)
            x_ += math.cos(a); y_ += math.sin(a)
        c = [(26, 22, 20), (112, 52, 30), (98, 34, 30), (44, 46, 46)][col]
        for (px_, py_) in pts: r.fixed(px_, py_, c)
    # the chin strap; the little screen at the temple flickering its error; the bruise just under it
    for k in range(8): r.fixed(138 - k * 0.45, 29 + k, LEATH[3] if k % 3 else LEATH[2])
    sx, sy = 140, 27
    for (dx, dy) in ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)): r.fixed(sx + dx, sy + dy, DEV[1])
    if SCREEN[fr]: r.fixed(sx, sy, SCREEN_ON[0]); r.fixed(sx + 1, sy, SCREEN_ON[1]); r.fixed(sx + 1, sy + 1, SCREEN_ON[0])
    else: r.fixed(sx + 1, sy, DEV[3])
    for (x, y, k) in ((136, 29, 1), (137, 29, 0), (136, 30, 0), (137, 30, 2), (138, 28, 0)):
        r.fixed(x, y, BRUISE[k])
    # the cable from the helmet's back down her shoulder to the device
    pts = [(143 - i * 0.5, 28 + i * 1.0) for i in range(12)]
    pts += [(137 - i * 2.0, 40 + i * 1.15 + math.sin(i * 0.7) * 1.3) for i in range(21)]
    r.stroke(pts, 1.1, color=(22, 19, 17), group='cable')
    # ---- the notebook on the floor by her hip, the bag of berries by her other hand
    r.poly([(74, 80), (84, 78), (87, 82), (77, 84)], M['leath'], lift=0.1, group='book')
    for x in range(76, 86): r.fixed(x, 83 - (x - 76) * 0.2, PAPER[2] if x % 2 else PAPER[1])
    r.ellipsoid(170, 80, 5.0, 4.6, M['cloth'], group='bag', vfun=lambda x, y, u, w: -0.15 if (x + y) % 4 == 0 else 0)
    r.ellipsoid(170, 75.5, 3.6, 1.6, M['cloth'], lift=-0.3, group='bagmouth')
    for (x, y) in ((169, 75), (171, 75), (170, 74)): r.fixed(x, y, BERRY[1])
    for (x, y, k) in ((176, 83, 2), (178, 84, 1), (175, 85, 1), (179, 82, 2), (174, 84, 0)):
        r.fixed(x, y, BERRY[k])
        if k == 2: r.fixed(x - 1, y - 1, BERRY[3])
    seam(r, 'armN', 0.28); seam(r, 'armF', 0.2); seam(r, 'torso', 0.14); seam(r, 'skirt', 0.1)
    im = r.render()
    # ---- the pale growth: sparse lichen-like patches eating the robe, mostly low where it touches the floor,
    #      and a few tiny pale caps on the shoulder and the hem (hashed in sprite space, fixed across frames)
    px = im.load()
    for y in range(H):
        for x in range(W):
            c = px[x, y]
            if c[3] == 0 or c[:3] not in ROBE: continue
            i = ROBE.index(c[:3])
            s = nS(x * 1.3, y * 1.3) * 0.55 + nL(x * 1.2, y * 1.2) * 0.45 + max(0.0, (y - 72) * 0.012)
            if s > 0.75:
                px[x, y] = STAIN[max(0, min(len(STAIN) - 1, i - 3 + (1 if s > 0.8 else 0)))] + (255,)
                if s > 0.8 and pulse > 0.4 and h32(x, y, 5) % 7 == 0: px[x, y] = MYC[1] + (255,)
    for (x, y) in ((141, 46), (143, 49), (60, 81), (64, 82), (110, 82), (146, 79)):
        px[x, y] = STAIN[4] + (255,); px[x + 1, y] = STAIN[3] + (255,); px[x, y + 1] = STAIN[1] + (255,)
    # rim light: the grey daylight from the roof hole catches her upper edges (robe, sleeves, skin, the helmet)
    src = im.copy(); sp = src.load()
    for y in range(1, H):
        for x in range(W):
            c = sp[x, y]
            if c[3] == 0 or sp[x, y - 1][3] != 0: continue
            for k, (dy, lift) in enumerate(((0, 0.42), (1, 0.2))):
                if y + dy >= H: continue
                cc = sp[x, y + dy]
                if cc[3] == 0 or cc[:3] in BRUISE or cc[:3] in MYC: continue
                px[x, y + dy] = tuple(min(255, int(cc[i] + (RIM[i] - cc[i]) * lift)) for i in range(3)) + (255,)
    # a contact shadow on the floor under her (dithered, semi-transparent), so she sits in the light pool
    for y in range(79, H):
        for x in range(36, W - 4):
            if px[x, y][3] != 0: continue
            d = ((x - 112) / 78.0) ** 2 + ((y - 85.5) / 3.2) ** 2
            if d > 1: continue
            a = int(150 * (1 - d) ** 0.7)
            if (x + y) % 2 and a < 70: continue
            px[x, y] = (10, 11, 9, a)
    return im


if __name__ == '__main__':
    os.makedirs(f'{OUT}/dead_bishop', exist_ok=True)
    frames = [bishop(i) for i in range(4)]
    # frame 4: a bust for the dialog portrait -- her head and shoulders moved to the frame's centre
    bust = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    bust.paste(frames[0].crop((104, 0, 168, 64)), (W // 2 - 32, 6))
    frames.append(bust)
    sheet = Image.new('RGBA', (W * len(frames), H), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        im.save(f'{OUT}/dead_bishop/{i}.png'); sheet.paste(im, (i * W, 0))
    sheet.save(f'{OUT}/dead_bishop.png')
    ALL = [INK] + ROBE + GOLD + STAIN + SKIN + BRUISE + TIN + COPPER + LEATH + CLOTH + BERRY + PAPER + DEV + SCREEN_ON + LENS + MYC
    seen, rows = set(), []
    for c in ALL:
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/dead_bishop.gpl', 'w').write('GIMP Palette\nName: dead_bishop\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT)
