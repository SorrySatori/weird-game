"""Feral Toast (ScreamingCorkClubScene) from their original art -- the old feral_guitarist / feral_bassplayer /
feral_drummer / feral_synth.png (1024x1536) brought down to their native grid like edgar.py (box filter, nothing
re-drawn) and animated by moving parts of their own pixels. Replaces the rig-drawn feral_toast.py sheets, same layout:
128x192 frames (Karlis 144x192: he is taken at 7x, seated behind his kit he would read small), soles on y 189; 0-3 idle (rest, breath, eyes, a small move), 4-11 playing = 4 beats of feral-toast.mp3
(~177 BPM), two frames per beat: the down-beat frame (4, 6, 8, 10) and the frame after it.
  telka    the tentacle-faced guitarist: knees give on the beat, a headbang on 1 and 3, the picking hand strums
  bass_xl  the robot on bass: the same, his visor flashes on the bar's start
  karlis   the bear on drums: the raised stick comes down on the crash (it wobbles), the kick thumps on 1 and 3,
           the low hand on the hi-hat on 2 and 4
  mira     the hooded synth player: hands alternate on the keys, light runs through the runes, the skull's eyes flash
           on the bar's start, the tendrils sway
python3 feral_px.py <outdir>  ->  <id>.png (12-frame sheets) + <id>/<n>.png + feral_px.gpl"""
import sys, os, math
from PIL import Image
from corkfolk import pixelize, lum

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
CHARS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../assets/images/characters')
W, H, SOLE = 128, 192, 189

# ---------------------------------------------------------------------------------------------------- pixel moves
def move(im, rect, dx, dy, pred=None, clear=True):
    """move the opaque pixels of rect (and pred(x, y)) by (dx, dy); what they leave becomes transparent (clear)
    or keeps the old pixels"""
    x0, y0, x1, y1 = rect
    W, H = im.size
    s = im.copy(); p = s.load(); out = im.copy(); o = out.load()
    pts = [(x, y) for y in range(max(0, y0), min(H, y1)) for x in range(max(0, x0), min(W, x1)) if p[x, y][3] and (pred is None or pred(x, y))]
    if clear:
        for pt in pts: o[pt] = (0, 0, 0, 0)
    for (x, y) in pts:
        if 0 <= x + dx < W and 0 <= y + dy < H: o[x + dx, y + dy] = p[x, y]
    return out

def rotate(im, rect, pivot, deg, pred=None):
    """turn the opaque pixels of rect (and pred) about pivot by deg (screen clockwise > 0), nearest neighbour"""
    x0, y0, x1, y1 = rect
    W, H = im.size
    s = im.copy(); p = s.load(); out = im.copy(); o = out.load()
    src = {(x, y) for y in range(y0, y1) for x in range(x0, x1) if 0 <= x < W and 0 <= y < H and p[x, y][3] and (pred is None or pred(x, y))}
    for pt in src: o[pt] = (0, 0, 0, 0)
    a = math.radians(deg); c, sn = math.cos(a), math.sin(a)
    px, py = pivot
    R = int(max(math.hypot(x - px, y - py) for (x, y) in src)) + 2 if src else 0
    for y in range(py - R, py + R + 1):
        for x in range(px - R, px + R + 1):
            if not (0 <= x < W and 0 <= y < H): continue
            ux, uy = x - px, y - py                                                   # inverse rotation
            sx, sy = round(px + ux * c + uy * sn), round(py - ux * sn + uy * c)
            if (sx, sy) in src: o[x, y] = p[sx, sy]
    return out

def bob(im, cut, dy):
    """everything above row cut moves by dy (down > 0: the knees give; up < 0: a breath); the rows at the cut
    are squeezed / stretched"""
    W, H = im.size
    p = im.load(); out = im.copy(); o = out.load()
    for x in range(W):
        col = [p[x, y] for y in range(H)]
        if dy > 0:
            for y in range(cut + dy - 1, -1, -1):
                o[x, y] = col[y - dy] if y - dy >= 0 else (0, 0, 0, 0)
        else:
            for y in range(0, cut):
                o[x, y] = col[y - dy] if y - dy < cut else col[y]
    return out

def recolor(im, rect, pred, fn):
    p = im.load(); out = im.copy(); o = out.load()
    x0, y0, x1, y1 = rect
    for y in range(y0, y1):
        for x in range(x0, x1):
            if p[x, y][3] and pred(p[x, y], x, y): o[x, y] = fn(p[x, y], x, y)
    return out

def k(c, f): return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (c[3],)
def yellow(c, x, y): return c[0] > 150 and c[1] > 110 and c[2] < 110 and c[0] > c[2] + 70
def bright_green(c, x, y): return c[1] > 120 and c[1] > c[0] + 30 and c[1] > c[2] + 50
def sway(im, rect, amp, top_heavy=True):
    """rows of rect shift sideways, most at its top (or bottom), the opaque pixels only"""
    x0, y0, x1, y1 = rect
    out = im
    for y in range(y0, y1):
        u = (y1 - y) / (y1 - y0) if top_heavy else (y - y0) / (y1 - y0)
        d = round(amp * u ** 1.3)
        if d: out = move(out, (x0, y, x1, y + 1), d, 0)
    return out

# ---------------------------------------------------------------------------------------------------- the band
def telka():
    s = pixelize(f'{CHARS}/feral_guitarist.png', 8)
    HEAD, PICK, KNEE = (26, 0, 94, 64), (46, 96, 66, 114), 132
    eyes = lambda f: recolor(s if f is None else f, HEAD, yellow, lambda c, x, y: k(c, 0.35))
    idle = [s, bob(s, 120, -1), eyes(None), sway(s, (26, 0, 94, 30), 1)]
    play = []
    for b in range(4):
        f = bob(s, KNEE, 1)
        f = move(f, (HEAD[0], HEAD[1], HEAD[2], HEAD[3] + 1), 0, 2 if b in (0, 2) else 1)    # headbang on 1 and 3
        f = move(f, PICK, 0, 2, clear=False)                                              # the strum: down
        f = sway(f, (26, 0, 94, 30), 1 if b % 2 else -1)
        play.append(f)
        g = move(s, PICK, 0, -1, clear=False)                                             # and back up
        g = sway(g, (26, 0, 94, 30), 1 if b % 2 else -1)
        play.append(g)
    return idle + play

def bass_xl():
    s = pixelize(f'{CHARS}/feral_bassplayer.png', 8)
    HEAD, PICK, KNEE = (40, 8, 76, 48), (28, 82, 50, 100), 130
    idle = [s, bob(s, 118, -1), recolor(s, HEAD, yellow, lambda c, x, y: k(c, 0.45)), move(s, HEAD, 1, 0)]
    play = []
    for b in range(4):
        f = bob(s, KNEE, 1)
        f = move(f, (HEAD[0], HEAD[1], HEAD[2], HEAD[3] + 1), 0, 2 if b in (0, 2) else 1)
        f = move(f, PICK, 0, 2, clear=False)
        if b == 0: f = recolor(f, (40, 10, 76, 52), yellow, lambda c, x, y: (255, 236, 150, 255))   # the visor flares
        play.append(f)
        play.append(move(s, PICK, 0, -1, clear=False))
    return idle + play

def karlis():
    s = pixelize(f'{CHARS}/feral_drummer.png', 7)                                     # 7x: seated behind his kit he'd read small
    q = lambda *v: tuple(round(c * 8 / 7) for c in v)                                    # coordinates measured on the 8x grid
    W, H = s.size
    p = s.load()
    for y in range(160, H):                                                          # drop the pale dust patch under the kit
        for x in range(W):                                                           # (the kick drum's head stays)
            c = p[x, y]
            in_head = ((x - 48) / 20.5) ** 2 + ((y - 169) / 26.0) ** 2 < 1
            if c[3] and lum(c) > 96 and max(c[:3]) - min(c[:3]) < 45 and not in_head: p[x, y] = (0, 0, 0, 0)
    HEAD, KNEE = q(50, 18, 94, 62), q(120)[0]
    STICK = q(4, 26, 46, 64)
    A50, A42, A31, A60 = q(50, 42, 31, 60)
    arm = lambda x, y: (y < A50 and x < A42) or (x < A31 and y < A60)                   # fist + stick, not the crash's rim
    CRASH = q(0, 66, 46, 94)
    LOW = q(80, 78, 116, 98)
    KICK = q(20, 124, 64, 172)
    sp = s.load()
    brass = lambda x, y: x < q(40)[0] and lum(sp[x, y]) > 60                                    # the crash itself, not the arm over it
    def stroke(im, down, tilt):
        """the raised fist and stick drop by `down` and the stick's tip dips by `tilt` degrees about the fist"""
        f = move(im, STICK, -1 if down > 2 else 0, down, arm)
        return rotate(f, (0, q(26)[0] + down, q(50)[0], q(64)[0] + down), (q(17)[0], q(56)[0] + down), tilt,
                      lambda x, y: (y < A50 + down and x < A42) or (x < q(30)[0] and y < A60 + down))
    idle = [s, bob(s, q(110)[0], -1), move(s, HEAD, 1, 0), stroke(s, 1, 4)]
    play = []
    for b in range(4):
        f = stroke(s, 5, 14)                                                                # the stick comes down on the crash
        f = move(f, CRASH, 0, 1, pred=brass)                                                # the crash wobbles
        f = move(f, HEAD, 0, 1)
        if b in (0, 2): f = recolor(f, KICK, lambda c, x, y: lum(c) > 80, lambda c, x, y: k(c, 1.18))   # the kick
        else: f = move(f, LOW, 0, 2, clear=False)                                           # the hi-hat on 2 and 4
        play.append(f)
        g = move(s, LOW, 0, -1, clear=False)
        play.append(g)
    return [f.crop((0, 0, 144, H)) for f in idle + play]                               # 144 wide: the kit's left edge to the hi-hat

def mira():
    s = pixelize(f'{CHARS}/feral_synth.png', 8)
    HEAD, KNEE = (44, 6, 90, 60), 96
    HL, HR = (38, 86, 60, 104), (62, 86, 88, 104)
    RUNES = (16, 96, 112, 120)
    SKULL = (34, 128, 66, 160)
    def runes(f, phase):
        return recolor(f, RUNES, bright_green, lambda c, x, y: k(c, 1.35) if ((x + phase * 12) // 12) % 4 == 0 else k(c, 0.9))
    idle = [s, bob(s, 90, -1), recolor(s, HEAD, yellow, lambda c, x, y: k(c, 0.3)), runes(s, 2)]
    play = []
    for b in range(4):
        f = bob(s, KNEE, 1)
        f = move(f, HEAD, 0, 1)
        f = move(f, HL if b % 2 == 0 else HR, 0, 2, clear=False)                            # a hand presses the keys
        f = runes(f, b * 2)
        f = sway(f, (4, 56, 34, 128), 1 if b % 2 else -1)
        f = sway(f, (100, 66, 126, 128), -1 if b % 2 else 1)
        if b == 0: f = recolor(f, SKULL, yellow, lambda c, x, y: (255, 230, 120, 255))
        play.append(f)
        g = runes(s, b * 2 + 1)
        g = sway(g, (4, 56, 34, 128), 1 if b % 2 else -1)
        play.append(g)
    return idle + play

if __name__ == '__main__':
    allc = set()
    for name, fn in (('telka', telka), ('bass_xl', bass_xl), ('karlis', karlis), ('mira', mira)):
        frames = fn()
        fw = frames[0].width
        d = SOLE - (frames[0].getbbox()[3] - 1)                                            # soles onto y 189
        os.makedirs(f'{OUT}/{name}', exist_ok=True)
        sheet = Image.new('RGBA', (fw * len(frames), H), (0, 0, 0, 0))
        for i, im in enumerate(frames):
            m = Image.new('RGBA', (fw, H), (0, 0, 0, 0)); m.paste(im, (0, d))
            m.save(f'{OUT}/{name}/{i}.png'); sheet.paste(m, (i * fw, 0))
            allc |= {px[:3] for px in m.getdata() if px[3]}
        sheet.save(f'{OUT}/{name}.png')
        print(name, len(frames), 'frames, dropped', d)
    cols = sorted(allc, key=lum)
    pal = Image.new('RGB', (len(cols), 1)); pal.putdata(cols)
    pal = pal.quantize(128, method=Image.Quantize.MEDIANCUT).getpalette()[:128 * 3]
    rows = sorted({tuple(pal[i:i + 3]) for i in range(0, len(pal), 3)}, key=lum)
    open(f'{OUT}/feral_px.gpl', 'w').write('GIMP Palette\nName: feral_px\nColumns: 8\n#\n' +
                                         '\n'.join('%3d %3d %3d\t#%02x%02x%02x' % (c + c) for c in rows) + '\n')
