"""Dr. Elphi Quarn brought down from her old portrait-sized art to its own grid (like edgar.py / corkfolk.py: box filter,
nothing re-drawn) and animated in place by moving / relighting her own pixels. (Ortolan used to live here too; he is now
redrawn by ortolan.py -- this script no longer touches his sheets or Aseprite sources.)
  elphi     128x160 (from DrElphi.png, /11), soles on y 156; 8 frames:
            0 rest  1 breath (the hologram bobs)  2 the goggles glint  3 the hologram pulses  4 it drifts up, sparks shift
            5 the coat's specks twinkle  6 she taps the device in her hand  7 a strand of hair stirs
python3 ortolan_elphi.py <outdir>  ->  elphi.png (sheet) + elphi/<n>.png + ortolan_elphi.gpl"""
import sys, os
from PIL import Image
from corkfolk import pixelize, rise, shift_box, scale_c, CHARS, lum

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'


def place(im, W, H, dx, dy):
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); out.alpha_composite(im, (dx, dy)); return out


def pick(im, box, pred):
    p = im.load(); x0, y0, x1, y1 = box
    return [(x, y) for y in range(y0, y1) for x in range(x0, x1) if p[x, y][3] and pred(p[x, y])]


def cyan(c): return c[1] > 150 and c[2] > 150 and c[0] < 140


# ---------------------------------------------------------------------------------------------------- Dr. Elphi
def elphi():
    src = pixelize(f'{CHARS}/DrElphi.png', 11)                                                   # 94x140, soles on y 139
    p = src.load()
    HOLO = (70, 30, 92, 70)
    holo = pick(src, HOLO, lambda c: c[3] > 0)
    goggles = pick(src, (36, 14, 64, 26), cyan)
    specks = [pt for pt in pick(src, (8, 36, 72, 126), cyan) if not (HOLO[0] <= pt[0] < HOLO[2] and pt[1] < HOLO[3])]
    def without_holo(im):
        out = im.copy(); o = out.load()
        for pt in holo: o[pt] = (0, 0, 0, 0)
        return out
    def holo_at(im, dy, k=1.0, sparks=0):
        out = without_holo(im); o = out.load()
        for (x, y) in holo:
            c = src.getpixel((x, y))
            if 0 <= y + dy < im.height: o[x, y + dy] = scale_c(c, k) if k != 1.0 else c
        for i in range(sparks):                                                                  # a few sparks thrown up
            sx, sy = HOLO[0] + 4 + (i * 5) % 14, HOLO[1] + 2 - (i % 2) * 2 + dy
            if 0 <= sy < im.height and not out.getpixel((sx, sy))[3]: o[sx, sy] = (150, 255, 236, 255)
        return out
    def glint(im):
        out = im.copy(); o = out.load()
        for (x, y) in goggles:
            if (x - 38) - (y - 15) in (0, 1) or (x - 52) - (y - 15) == 0: o[x, y] = (210, 255, 248, 255)
        return out
    def twinkle(im):
        out = im.copy(); o = out.load()
        for i, pt in enumerate(specks):
            c = src.getpixel(pt)
            o[pt] = (min(255, c[0] + 60), 255, 255, 255) if i % 3 == 0 else scale_c(c, 0.8)
        return out
    def hair_stir(im):                                                                           # outer locks lean a pixel
        out = im.copy(); o = out.load(); q = im.load()
        for y in range(10, 38):
            for x in range(22, 34):
                c = q[x, y]
                if c[3] and c[0] > c[2] + 40 and c[0] > 90 and x - 1 >= 0 and not q[x - 1, y][3]: o[x - 1, y] = c
        return out
    base_breath = rise(src, 74, (8, 70))
    F = [src, holo_at(base_breath, -1), glint(src), holo_at(src, 0, 1.25, 3), holo_at(src, -2, 1.1, 2),
         twinkle(src), shift_box(src, (72, 72, 88, 88), 0, 1), hair_stir(src)]
    return [place(f, 128, 160, 17, 17) for f in F]


if __name__ == '__main__':
    allc = set()
    for name, frames in (('elphi', elphi()),):
        w, h = frames[0].size
        os.makedirs(f'{OUT}/{name}', exist_ok=True)
        sheet = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
        for i, im in enumerate(frames):
            im.save(f'{OUT}/{name}/{i}.png'); sheet.paste(im, (i * w, 0))
            allc |= {im.getpixel((x, y))[:3] for y in range(h) for x in range(w) if im.getpixel((x, y))[3]}
        sheet.save(f'{OUT}/{name}.png')
    cols = sorted(allc, key=lum)
    pal = Image.new('RGB', (len(cols), 1)); pal.putdata(cols)
    pal = pal.quantize(128, method=Image.Quantize.MEDIANCUT).getpalette()[:128 * 3]
    rows = sorted({tuple(pal[i:i + 3]) for i in range(0, len(pal), 3)}, key=lum)
    open(f'{OUT}/ortolan_elphi.gpl', 'w').write('GIMP Palette\nName: ortolan_elphi\nColumns: 8\n#\n' +
                                               '\n'.join('%3d %3d %3d\t#%02x%02x%02x' % (c + c) for c in rows) + '\n')
    print('ok', OUT)
