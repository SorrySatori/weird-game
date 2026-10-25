"""The people inside the Screaming Cork (ScreamingCorkInteriorScene) -- Heliodor the barkeep and Ravla the forger --
brought down from their old portrait-sized art to its native grid (like edgar.py: box filter, nothing re-drawn) and
animated in place by moving / relighting their own pixels.
  heliodor  128x192 (from heliodor.png 1024x1536), soles on y 189; 8 frames:
            0 rest  1 breath  2 the glow of the colony swells  3 one shoulder-eye of the cluster blinks
            4 the head's eyes narrow  5 the leaves on his vine arm rustle  6-7 a drop gathers on the tap and falls
  ravla     128x128 (from ravla.png 1024x1024), soles on y 125; 8 frames:
            0 rest  1 breath  2 the goggles flash  3 she looks down at her work  4-5 her hands fiddle
            6-7 the tentacle behind her sways
python3 corkfolk.py <outdir>  ->  heliodor.png ravla.png (sheets) + <id>/<n>.png + corkfolk.gpl"""
import sys, os
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
CHARS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../assets/images/characters')

def lum(c): return (c[0] * 3 + c[1] * 4 + c[2]) / 8

def pixelize(path, k):
    """premultiplied box filter by k, hard alpha; pinholes inside the figure filled from their neighbours"""
    im = Image.open(path).convert('RGBA')
    sm = im.convert('RGBa').reduce(k).convert('RGBA')
    sm.putalpha(sm.getchannel('A').point(lambda v: 255 if v >= 140 else 0))
    W, H = sm.size; p = sm.load()
    seen, todo = set(), [(x, y) for x in range(W) for y in (0, H - 1)] + [(x, y) for y in range(H) for x in (0, W - 1)]
    while todo:
        x, y = todo.pop()
        if (x, y) in seen or not (0 <= x < W and 0 <= y < H) or p[x, y][3]: continue
        seen.add((x, y)); todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    for y in range(H):
        for x in range(W):
            if p[x, y][3] or (x, y) in seen: continue
            nb = [p[x + dx, y + dy] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if p[x + dx, y + dy][3]]
            p[x, y] = tuple(sum(c[i] for c in nb) // len(nb) for i in range(3)) + (255,)
    return sm

def drop(im, d):
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.paste(im.crop((0, 0, im.width, im.height - d)), (0, d))
    return out

def rise(src, cut, xr=None):
    """breath: everything above row `cut` rises a pixel, the row at the cut stretches"""
    s = src.load(); out = src.copy(); o = out.load()
    for x in range(*(xr or (0, src.width))):
        for y in range(cut):
            o[x, y] = s[x, y + 1] if y + 1 < cut else s[x, y]
    return out

def shift_box(src, box, dx=0, dy=0):
    """move the opaque pixels of a box by (dx, dy); what they uncover keeps the pixels that were under them"""
    x0, y0, x1, y1 = box
    s = src.load(); out = src.copy(); o = out.load()
    for y in range(y0, y1):
        for x in range(x0, x1):
            if s[x, y][3] and 0 <= x + dx < src.width and 0 <= y + dy < src.height: o[x + dx, y + dy] = s[x, y]
    return out

def scale_c(c, k): return tuple(max(0, min(255, int(v * k))) for v in c[:3]) + (c[3],)

# ---------------------------------------------------------------------------------------------------- Heliodor
def glowing(c): return c[3] and c[1] > 120 and c[1] > c[0] + 35 and c[1] > c[2] + 60
def components(im, pred, box):
    """connected groups of pixels matching pred inside box"""
    p = im.load(); x0, y0, x1, y1 = box; seen = set(); groups = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if (x, y) in seen or not pred(p[x, y]): continue
            g, todo = [], [(x, y)]
            while todo:
                q = todo.pop()
                if q in seen or not (x0 <= q[0] < x1 and y0 <= q[1] < y1) or not pred(p[q]): continue
                seen.add(q); g.append(q); todo += [(q[0] + 1, q[1]), (q[0] - 1, q[1]), (q[0], q[1] + 1), (q[0], q[1] - 1)]
            groups.append(g)
    return groups

def heliodor_frames():
    src = pixelize(f'{CHARS}/heliodor.png', 8)
    p = src.load()
    head_eyes = [g for g in components(src, glowing, (60, 30, 82, 44)) if len(g) > 4]
    shoulder = sorted((g for g in components(src, glowing, (24, 34, 44, 56)) if len(g) > 3), key=lambda g: -len(g))
    LEAF = (14, 60, 46, 120)                                                     # the leafy vine arm (viewer's left)
    def glow(im, k):
        out = im.copy(); o = out.load(); q = im.load()
        for y in range(im.height):
            for x in range(im.width):
                if glowing(q[x, y]): o[x, y] = scale_c(q[x, y], k)
        return out
    def blink(im, group):                                                         # the orb closes: its light goes out
        out = im.copy(); o = out.load()
        for pt in group: o[pt] = scale_c(p[pt], 0.42)
        return out
    def narrow(im):                                                               # the head's eyes squint: their upper half goes dark
        out = im.copy(); o = out.load()
        for g in head_eyes:
            ys = [pt[1] for pt in g]; mid = (min(ys) + max(ys)) / 2
            for pt in g:
                if pt[1] < mid: o[pt] = scale_c(p[pt], 0.5)
        return out
    def rustle(im):                                                               # leaves twitch: leaf tips poke out a pixel
        q = im.load(); out = im.copy(); o = out.load()
        x0, y0, x1, y1 = LEAF
        for y in range(y0, y1, 3):
            for x in range(x0, x1):
                c = q[x, y]
                if c[3] and c[1] > c[0] and x >= 1 and not q[x - 1, y][3]: o[x - 1, y] = c
        return out
    spout = max(((x, y) for y in range(80, 100) for x in range(104, 118) if p[x, y][3]), key=lambda q: (q[1], -abs(q[0] - 112)))
    def drip(im, k):                                                              # an amber drop at the tap's spout
        out = im.copy(); o = out.load()
        sx, sy = spout
        AMB = [(214, 160, 70, 255), (240, 196, 110, 255), (150, 98, 40, 255)]
        if k == 1: o[sx, sy + 1] = AMB[0]
        else:
            for (dy, c) in ((4, AMB[1]), (5, AMB[0]), (6, AMB[2])): o[sx, sy + dy] = c
        return out
    F = [src, rise(src, 100), glow(src, 1.25), blink(src, shoulder[0]) if shoulder else src,
         narrow(src), rustle(src), drip(src, 1), drip(src, 2)]
    return [drop(f, 9) for f in F]

# ---------------------------------------------------------------------------------------------------- Ravla
def purple(c): return c[3] and c[2] > 70 and c[2] > c[1] + 35 and c[0] > c[1]
def ravla_frames():
    src = pixelize(f'{CHARS}/ravla.png', 8)
    p = src.load()
    lenses = [(x, y) for y in range(20, 38) for x in range(58, 86) if purple(p[x, y])]
    def flash(im):
        out = im.copy(); o = out.load()
        for pt in lenses:
            c = p[pt]; o[pt] = (min(255, c[0] + 70), min(255, c[1] + 40), min(255, c[2] + 80), 255)
        if lenses: o[min(lenses, key=lambda q: (q[1], q[0]))] = (236, 214, 255, 255)
        return out
    def sway(im, amp):                                                           # the tentacle's free loop leans, more at the top
        q = im.load(); out = im.copy(); o = out.load()
        for y in range(0, 40):
            k = round(amp * (1 - y / 40) ** 1.3)
            if not k: continue
            row = [q[x, y] for x in range(0, 42)]
            for x in range(0, 42):
                xs = x - k
                o[x, y] = row[xs] if 0 <= xs < 42 else (0, 0, 0, 0)
        return out
    F = [src, rise(src, 70, (40, 92)), flash(src), shift_box(src, (44, 4, 88, 44), 0, 1),
         shift_box(src, (48, 74, 80, 98), 1, 0), shift_box(src, (48, 74, 80, 98), -1, 1),
         sway(src, 2), sway(src, -1)]
    return [drop(f, 2) for f in F]

if __name__ == '__main__':
    allc = set()
    for name, frames in (('heliodor', heliodor_frames()), ('ravla', ravla_frames())):
        w, h = frames[0].size
        os.makedirs(f'{OUT}/{name}', exist_ok=True)
        sheet = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
        for i, im in enumerate(frames):
            im.save(f'{OUT}/{name}/{i}.png'); sheet.paste(im, (i * w, 0))
            allc |= {px[:3] for px in im.getdata() if px[3]}
        sheet.save(f'{OUT}/{name}.png')
    cols = sorted(allc, key=lum)
    pal = Image.new('RGB', (len(cols), 1)); pal.putdata(cols)
    pal = pal.quantize(96, method=Image.Quantize.MEDIANCUT).getpalette()[:96 * 3]
    rows = sorted({tuple(pal[i:i + 3]) for i in range(0, len(pal), 3)}, key=lum)
    open(f'{OUT}/corkfolk.gpl', 'w').write('GIMP Palette\nName: corkfolk\nColumns: 8\n#\n' +
                                          '\n'.join('%3d %3d %3d\t#%02x%02x%02x' % (c + c) for c in rows) + '\n')
    print('ok', OUT)
