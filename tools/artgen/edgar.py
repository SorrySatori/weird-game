"""Edgar Eskola, the mišutkenn of the Screaming Cork (ScreamingCorkScene) -- the old portrait-sized art
(assets/images/characters/EdgarEskola.png, 1024x1536 painted at ~16 px per "pixel", shown at 0.125) brought down to
its native grid so it reads exactly as before, then animated in place. Nothing is re-drawn from scratch: the user
wants the bear to stay as he is; the frames only move parts of the original pixels.
128x192 frames, soles on y 189; an 8-frame idle:
  0 rest            1 breath in (head, shoulders and the bag rise a pixel)     2 blink
  3 the right ear twitches                       4-5 the bag sways right / left on its neck
  6 he lowers his head a little (a grumble)      7 head down, eyes shut (a sigh)
The eye glints of the source were transparent holes (the background showed through); they are glints now.
python3 edgar.py <outdir>  ->  edgar.png (8-frame sheet) + edgar/<n>.png + edgar.gpl"""
import sys, os
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../assets/images/characters/EdgarEskola.png')
W, H, DROP = 128, 192, 7                        # the source's soles sit on y 182 -> moved down to 189
GLINT = (204, 190, 158, 255)
EYES = [(50, 36, 58, 41), (65, 36, 73, 42)]     # boxes (x0, y0, x1, y1) around the eyes, source grid
EAR = (75, 19, 89, 33)                          # the right (viewer's right) ear
BAG_X = 38                                      # columns left of this are the bag, its paw and the cuff
HEAD = (38, 0, 93, 54)                          # the head, down to the collar

def base():
    im = Image.open(SRC).convert('RGBA')
    sm = im.convert('RGBa').reduce(8).convert('RGBA')                       # premultiplied box filter: no halo
    sm.putalpha(sm.getchannel('A').point(lambda v: 255 if v >= 140 else 0))
    p = sm.load()
    seen, todo = set(), [(x, y) for x in range(W) for y in (0, H - 1)] + [(x, y) for y in range(H) for x in (0, W - 1)]
    while todo:                                                              # the outside: transparent, reached from the edge
        x, y = todo.pop()
        if (x, y) in seen or not (0 <= x < W and 0 <= y < H) or p[x, y][3]: continue
        seen.add((x, y)); todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    for y in range(H):
        for x in range(W):
            if p[x, y][3] or (x, y) in seen: continue
            if any(x0 <= x <= x1 and y0 <= y <= y1 for (x0, y0, x1, y1) in EYES): p[x, y] = GLINT
            else:                                                            # any other pinhole: the mean of its neighbours
                nb = [p[x + dx, y + dy] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if p[x + dx, y + dy][3]]
                p[x, y] = tuple(sum(c[i] for c in nb) // len(nb) for i in range(3)) + (255,)
    return sm

def lum(c): return (c[0] * 3 + c[1] * 4 + c[2]) / 8

def frame(src, breath=0, blink=False, ear=0, sway=0, nod=0):
    s = src.load()
    out = src.copy(); o = out.load()
    if breath:                                                              # everything above the cut rises, the row at the cut stretches
        for x in range(W):
            cut = 130 if x < BAG_X else 104
            for y in range(cut):
                o[x, y] = s[x, y + 1] if y + 1 < cut else s[x, y]
    if nod:                                                                 # the head sinks onto the collar
        x0, y0, x1, y1 = HEAD
        cur = out.copy(); c = cur.load()
        for x in range(x0, x1):
            for y in range(y1, y0, -1):
                if c[x, y - 1][3]: o[x, y] = c[x, y - 1]
                elif y < y1: o[x, y] = c[x, y - 1]
            o[x, y0] = (0, 0, 0, 0)
    if blink:                                                               # the glints go out, the lid line darkens
        cur = out.copy(); c = cur.load()
        dy = 1 if nod else 0
        for (x0, y0, x1, y1) in EYES:
            box = [(x, y) for x in range(x0, x1 + 1) for y in range(y0 + dy, y1 + 1 + dy)]
            dark = min((c[x, y] for (x, y) in box if c[x, y][3]), key=lum)
            for (x, y) in box:
                if c[x, y][:3] == GLINT[:3]:
                    o[x, y] = dark
                    up = c[x, y - 1]
                    o[x, y - 1] = tuple(int(v * 0.7) for v in up[:3]) + (255,)
    if ear:                                                                 # the ear flicks up a pixel
        cur = out.copy(); c = cur.load()
        x0, y0, x1, y1 = EAR
        for x in range(x0, x1 + 1):
            for y in range(y0 - 1, y1):
                src_px = c[x, y + 1]
                if src_px[3] or y >= y0: o[x, y] = src_px
    if sway:                                                                # the bag's body swings on its knotted neck
        cur = out.copy(); c = cur.load()
        for y in range(115, 132):                                           # below the paw only
            k = sway
            for x in range(0, BAG_X):
                xs = x - k
                o[x, y] = c[xs, y] if 0 <= xs < BAG_X else (c[x, y] if xs >= BAG_X else (0, 0, 0, 0))
    moved = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    moved.paste(out.crop((0, 0, W, H - DROP)), (0, DROP))
    return moved

POSES = [dict(), dict(breath=1), dict(blink=True), dict(ear=1),
         dict(sway=1), dict(sway=-1), dict(nod=1), dict(nod=1, blink=True)]

if __name__ == '__main__':
    src = base()
    frames = [frame(src, **p) for p in POSES]
    os.makedirs(f'{OUT}/edgar', exist_ok=True)
    sheet = Image.new('RGBA', (W * len(frames), H), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        im.save(f'{OUT}/edgar/{i}.png'); sheet.paste(im, (i * W, 0))
    sheet.save(f'{OUT}/edgar.png')
    # an Aseprite palette of the colours actually used, sorted by brightness
    cols = sorted({px[:3] for im in frames for px in im.getdata() if px[3]}, key=lum)
    pal = Image.new('RGB', (len(cols), 1)); pal.putdata(cols)
    pal = pal.quantize(64, method=Image.Quantize.MEDIANCUT).getpalette()[:64 * 3]
    rows = sorted({tuple(pal[i:i + 3]) for i in range(0, len(pal), 3)}, key=lum)
    open(f'{OUT}/edgar.gpl', 'w').write('GIMP Palette\nName: edgar\nColumns: 8\n#\n' +
                                       '\n'.join('%3d %3d %3d\t#%02x%02x%02x' % (c + c) for c in rows) + '\n')
    print('ok', OUT, len(cols), 'colours')
