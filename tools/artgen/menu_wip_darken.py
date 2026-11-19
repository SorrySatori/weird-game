"""Marti's unfinished menu painting (phone photo, already warped to the paper by menu_wip_warp.py and scaled to 1411 px wide):
   paint the white paper dark, keep the drawing. All coordinates (egg, Ortolan, clock, sketch, right block) are for the
   2026-11-19 photo; re-measure them for a new one. Usage: menu_wip_darken.py paper.png full.png band.png x0 x1 bottom

1. even out the photo's lighting: the paper's own colour around each spot (a blur of the paper pixels only), so the
   page reads white everywhere and the drawing keeps its real colours
2. ink = how far a pixel is from white in its weakest channel (colour pencil counts, paper doesn't)
3. the drawing as REGIONS, not pixels: ink closed into solid shapes, so a pencil-shaded balustrade stays whole instead
   of its paper grain turning into black specks; only along a shape's edge do paper-light pixels go dark (no white rim)
4. the egg's inside is drawn paper (the shell): kept, found by flood fill inside its outline
5. the drawing is dimmed a little (the user: tone the light down, also around the characters)
"""
import sys
from PIL import Image, ImageFilter, ImageChops, ImageMath, ImageDraw

src, out_full, out_band = sys.argv[1], sys.argv[2], sys.argv[3]
im = Image.open(src).convert('RGB')
W, H = im.size


def divide(a, b, gain=1.0):
    return Image.merge('RGB', [
        ImageMath.lambda_eval(lambda e: e['convert'](e['float'](e['a']) * 255.0 * gain / (e['float'](e['b']) + 1.0), 'L'), a=x, b=y)
        for x, y in zip(a.split(), b.split())])


def ink_of(flat):
    r, g, b = flat.split()
    return ImageChops.invert(ImageChops.darker(ImageChops.darker(r, g), b))


def ramp(t0, t1):
    def f(v):
        x = min(1.0, max(0.0, (v - t0) / (t1 - t0)))
        return int(255 * x * x * (3 - 2 * x))
    return [f(v) for v in range(256)]


# 1. lighting: a rough guess (the brightest paper nearby), then the paper's own colour (blur of paper pixels only)
small = im.resize((W // 16, H // 16), Image.BOX).filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(4))
light0 = small.resize((W, H), Image.BICUBIC)
paper = ink_of(divide(im, light0)).point(lambda v: 255 if v < 22 else 0)
q = 4
ps = paper.resize((W // q, H // q), Image.BOX)
num = ImageChops.multiply(im.resize((W // q, H // q), Image.BOX), Image.merge('RGB', [ps] * 3)).filter(ImageFilter.GaussianBlur(10))
den = ps.filter(ImageFilter.GaussianBlur(10))
fine = divide(num, Image.merge('RGB', [den] * 3))
# far from any paper (inside the smoke) the paper colour comes from much further out
num2 = ImageChops.multiply(im.resize((W // q, H // q), Image.BOX), Image.merge('RGB', [ps] * 3)).filter(ImageFilter.GaussianBlur(45))
den2 = ps.filter(ImageFilter.GaussianBlur(45))
coarse = divide(num2, Image.merge('RGB', [den2] * 3))
light = Image.composite(fine, coarse, den.point(lambda v: min(255, v * 4)))
light = light.filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BICUBIC)
flat = divide(im, light, gain=1.0)

# 2.-3. ink and the alpha: a grey-level closing of the ink map fills the paper grain inside a pencil-shaded area (so it
# doesn't turn into black specks) without growing the drawing past its edges (a blur did: white rims everywhere)
ink = ink_of(flat).filter(ImageFilter.GaussianBlur(1.0))
closed = ink.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
alpha = closed.point(ramp(14, 64)).filter(ImageFilter.GaussianBlur(0.8))

# Ortolan's white hair and beard: light strokes count as drawing there
head = Image.new('L', (W, H), 0)
ImageDraw.Draw(head).ellipse((1224, 596, 1314, 750), fill=255)
alpha = ImageChops.lighter(alpha, ImageChops.multiply(head.filter(ImageFilter.GaussianBlur(3)), ink.point(ramp(6, 26))))

# the unfinished pencil sketch in the middle (a frame, not painted yet): its graphite is not drawing
SKETCH = (818, 440, 1012, 680)
sk = Image.new('L', (W, H), 0)
ImageDraw.Draw(sk).rectangle(SKETCH, fill=255)
r_, g_, b_ = flat.split()
sat = ImageMath.lambda_eval(lambda e: e['convert'](((e['g'] > e['r'] + 15) & (e['g'] > e['b'] + 15)) * 255, 'L'), r=r_, g=g_, b=b_)
keep = ImageChops.lighter(ImageChops.invert(sk.filter(ImageFilter.GaussianBlur(4))), sat)
alpha = ImageChops.multiply(alpha, keep)
ink = ImageChops.multiply(ink, keep)

# 4. the egg: flood the paper inside its outline from a grid of seeds (an ellipse a bit outside the shell stops leaks)
EGG = (80, 226, 406, 590)
barrier = ink.point(lambda v: 255 if v > 40 else 0)
ImageDraw.Draw(barrier).ellipse(EGG, outline=255, width=4)
cx, cy, rx, ry = (EGG[0] + EGG[2]) / 2, (EGG[1] + EGG[3]) / 2, (EGG[2] - EGG[0]) / 2, (EGG[3] - EGG[1]) / 2
for y in range(EGG[1], EGG[3], 6):
    for x in range(EGG[0], EGG[2], 6):
        if ((x - cx) / (rx * 0.9)) ** 2 + ((y - cy) / (ry * 0.9)) ** 2 < 1 and barrier.getpixel((x, y)) == 0:
            ImageDraw.floodfill(barrier, (x, y), 128)
egg = barrier.point(lambda v: 255 if v == 128 else 0).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(1.5))
inner = Image.new('L', (W, H), 0)
ImageDraw.Draw(inner).ellipse((cx - rx * 0.97, cy - ry * 0.97, cx + rx * 0.97, cy + ry * 0.97), fill=255)
alpha = ImageChops.lighter(alpha, ImageChops.lighter(egg, inner)).filter(ImageFilter.GaussianBlur(0.6))

# 4b. paper the drawing encloses (the light smoke on the right, the townhall's stone, the clock face, Ortolan's
# beard) is drawing too: only paper reachable from the open sky / the balustrade's gaps turns dark. The flood runs on
# eroded paper so it can't slip into the smoke through hairline gaps.
paper_m = alpha.point(lambda v: 255 if v < 128 else 0)
fl = paper_m.filter(ImageFilter.MinFilter(7))
seeds = [(x, y) for y in range(330, 700, 20) for x in range(560, 860, 20)]
seeds += [(x, y) for y in (812, 828, 844) for x in range(0, W, 3)]
for sxy in seeds:
    if fl.getpixel(sxy) == 255:
        ImageDraw.floodfill(fl, sxy, 128)
reached = fl.point(lambda v: 255 if v == 128 else 0).filter(ImageFilter.MaxFilter(9))
sky = ImageChops.multiply(reached, paper_m)
holes = ImageChops.subtract(paper_m, sky).point(lambda v: 255 if v > 127 else 0)
# ...but only the narrow ones (paper grain, light streaks in the smoke): an enclosed paper AREA (a courtyard of the
# drawing, the ground by the stairs) is still empty paper, so it goes dark too
# (an opening: where a 15 px square fits; thin parts attached to an area stay drawing, e.g. the stairs' steps)
big = ImageChops.multiply(holes.filter(ImageFilter.MinFilter(15)).filter(ImageFilter.MaxFilter(17)), holes)
holes = ImageChops.subtract(holes, big)
# grown over their own rim (else the drawing's soft edge darkens a ring around each filled hole), never into the open
bgp = ImageChops.lighter(sky, big).point(lambda v: 255 if v > 127 else 0)
holes = ImageChops.multiply(holes.filter(ImageFilter.MaxFilter(5)), ImageChops.invert(bgp)).filter(ImageFilter.GaussianBlur(0.8))
alpha = ImageChops.lighter(alpha, holes)
# the right block (smoke, the townhall, Ortolan) is drawn edge to edge
blk = Image.new('L', (W, H), 0)
ImageDraw.Draw(blk).polygon([(1138, 0), (W, 0), (W, 690), (1150, 690), (1150, 330)], fill=255)
alpha = ImageChops.lighter(alpha, blk.filter(ImageFilter.GaussianBlur(2)))
# Ortolan's white hair + beard and the clock's face: drawn white, and they stay light (not dimmed like the graphite)
whites = Image.new('L', (W, H), 0)
ImageDraw.Draw(whites).ellipse((1226, 598, 1312, 748), fill=255)
ImageDraw.Draw(whites).ellipse((1268, 468, 1322, 522), fill=255)
whites = whites.filter(ImageFilter.GaussianBlur(2))
alpha = ImageChops.lighter(alpha, whites)

# 5. the drawing a little dimmer; the black with a trace of the paper's grain
dim = flat.point(lambda v: int(255 * (v / 255) ** 1.12 * 0.86))
bright = dim                                    # the egg keeps more of its light: the menu's focal point
# the greys (graphite: the smoke, the stone, the egg's paper) dimmer than the colours, so they sit in the dark
h_, s_, v_ = dim.convert('HSV').split()
v_ = ImageMath.lambda_eval(lambda e: e['convert'](e['float'](e['v']) * (0.6 + 0.4 * e['min'](e['float'](e['s']) / 110.0, 1.0)), 'L'), v=v_, s=s_)
dim = Image.merge('HSV', (h_, s_, v_)).convert('RGB')
dim = Image.composite(bright, dim, ImageChops.lighter(ImageChops.lighter(egg, inner).point(lambda v: v * 6 // 10),
                                                      whites.point(lambda v: v * 85 // 100)))
grain = flat.convert('L').point(lambda v: max(0, min(255, int(9 + (v - 225) * 0.10))))
grain = Image.composite(Image.new('L', (W, H), 9), grain, sk.filter(ImageFilter.GaussianBlur(4)))   # no ghost of the sketch
dark = Image.merge('RGB', [grain, grain.point(lambda v: max(0, v - 1)), grain.point(lambda v: v + 4)])
# along the edges the paper's light is taken out of the colour (as if the white were transparent), so no pale rim
res = Image.composite(ImageChops.subtract(dim, Image.merge('RGB', [ImageChops.invert(alpha)] * 3)), dark, alpha)
res.save(out_full)

# the menu's 16:9 band (bottom-anchored: the characters' feet stay in)
x0, x1, bottom = int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
w = x1 - x0
h = round(w * 600 / 1067)
res.crop((x0, bottom - h, x1, bottom)).resize((1067, 600), Image.LANCZOS).save(out_band)
print('ok', W, H)
