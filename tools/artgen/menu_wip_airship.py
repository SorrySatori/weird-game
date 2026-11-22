"""Cut the green airship out of the darkened menu painting (menu_wip_darken.py) so the main menu can fly it.

in:  paper.png (the photo warped + scaled, menu_wip_warp.py), dark_full.png (menu_wip_darken.py), the band's crop x0 x1 bottom
out: band.png (the 1067x600 band with the airship's spot filled with smoke), ship.png (the airship, RGBA, band scale)
     and its position in the band (the centre) on stdout.
The coordinates are for the 2026-11-19 photo.
"""
import sys
from PIL import Image, ImageFilter, ImageChops, ImageMath, ImageDraw

paper_p, dark_p, out_band, out_ship = sys.argv[1:5]
x0, x1, bottom = (int(v) for v in sys.argv[5:8])
paper = Image.open(paper_p).convert('RGB')
dark = Image.open(dark_p).convert('RGB')
W, H = dark.size
BOX = (1196, 220, 1394, 350)          # the airship with its drips; the ochre smoke column starts at ~1362


def L(expr, **ims):
    return ImageMath.lambda_eval(lambda e: e['convert'](expr(e), 'L'), **ims)


# 1. the airship's mask, from the photo's colours: green/teal (balloon, drips) + the warm gondola, closed over the
#    lattice lines; then its dark outline (only right next to it, the smoke has dark streaks too)
h, s, v = paper.convert('HSV').split()
# (PIL's hue runs 0-255: green ~85, teal ~120; the gondola's red-brown and orange lights < 36, only inside its hull,
# the ochre smoke column right of the ship is warm too)
gondola = Image.new('L', (W, H), 0)
ImageDraw.Draw(gondola).ellipse((1240, 282, 1344, 340), fill=255)
green = L(lambda e: ((e['h'] > 60) & (e['h'] < 140) & (e['s'] > 45)) * 255, h=h, s=s)
warm = L(lambda e: ((e['h'] < 36) & (e['s'] > 80)) * 255, h=h, s=s)
col = ImageChops.lighter(green, ImageChops.multiply(warm, gondola))
box = Image.new('L', (W, H), 0)
ImageDraw.Draw(box).rectangle(BOX, fill=255)
col = ImageChops.multiply(col, box)
closed = col.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
near = closed.filter(ImageFilter.MaxFilter(7))
outline = ImageChops.multiply(near, v.point(lambda t: 255 if t < 95 else 0))
mask = ImageChops.lighter(closed, outline)
# the balloon and the gondola are solid (lattice cells, window rows): fill what the mask encloses there
hull = Image.new('L', (W, H), 0)
ImageDraw.Draw(hull).ellipse((1214, 232, 1372, 296), fill=255)                  # the balloon
ImageDraw.Draw(hull).ellipse((1246, 286, 1338, 334), fill=255)                  # the gondola
hull = ImageChops.multiply(hull, mask.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9)))
mask = ImageChops.lighter(mask, hull)
alpha = mask.filter(ImageFilter.GaussianBlur(0.7))

# 2. the smoke where it was = the surrounding smoke's tone (normalised convolution; the townhall's green domes just
#    below don't count) + the grain and streaks of the smoke mirrored from just above the hole (per pixel column, so
#    it meets the top edge; the ochre column under the tail carries on)
hole = mask.filter(ImageFilter.MaxFilter(9))
# the whole envelope, also the smoke between the ropes and drips (it's tinted by them)
ImageDraw.Draw(hole).polygon([(1218, 286), (1352, 286), (1348, 354), (1232, 354)], fill=255)
hp, dp = hole.load(), dark.load()
mir = dark.copy()
mp = mir.load()
for x in range(BOX[0] - 6, min(W, BOX[2] + 6)):
    y = BOX[1] - 12
    while y < BOX[3] + 12:
        if not hp[x, y]:
            y += 1
            continue
        ya = y
        while hp[x, y]:
            y += 1
        for yy in range(ya, y):
            sy = ya - 1 - (yy - ya)
            mp[x, yy] = dp[x, sy] if sy >= 0 and not hp[x, sy] else dp[x, ya - 1]
dh, ds, dv = dark.convert('HSV').split()
domes = L(lambda e: ((e['h'] > 60) & (e['h'] < 150) & (e['s'] > 45) & (e['v'] > 70)) * 255, h=dh, s=ds, v=dv)
ochre = L(lambda e: ((e['h'] >= 20) & (e['h'] <= 50) & (e['s'] > 70) & (e['v'] > 110)) * 255, h=dh, s=ds, v=dv)
ochre_wide = ochre.filter(ImageFilter.MaxFilter(5))


def normconv(known):
    out = None
    for r in (48, 24, 12, 6):
        num = Image.merge('RGB', [ImageChops.multiply(c, known).filter(ImageFilter.GaussianBlur(r)) for c in dark.split()])
        den = known.filter(ImageFilter.GaussianBlur(r))
        est = Image.merge('RGB', [L(lambda e: e['float'](e['n']) * 255.0 / (e['float'](e['d']) + 0.5), n=c, d=den)
                                  for c in num.split()])
        out = est if out is None else Image.composite(est, out, den.point(lambda t: max(0, min(255, (t - 50) * 4))))
    return out


# the grey smoke: its tone from the grey around, its grain from the mirror (none where the mirror hit ochre)
nothole = ImageChops.invert(hole)
tone = normconv(ImageChops.multiply(ImageChops.multiply(nothole, ImageChops.invert(domes)), ImageChops.invert(ochre_wide)))
# (the grain: the smoke ~130 px up, shifted 25 px left or right, whichever isn't the scraper or the ochre there; a
# mirror drew arcs)
def grain(dx):
    src = ImageChops.offset(dark, dx, 130)
    soft = src.filter(ImageFilter.GaussianBlur(9))
    so = src.convert('HSV').split()
    odd = L(lambda e: ((e['h'] >= 20) & (e['h'] <= 50) & (e['s'] > 70) & (e['v'] > 110)) * 255, h=so[0], s=so[1], v=so[2])
    ok = ImageChops.invert(odd.filter(ImageFilter.MaxFilter(9)))
    if dx > 0:   # this source reaches into the scraper left of the hole
        clear = Image.new('L', (W, H), 0)
        ImageDraw.Draw(clear).rectangle((1211 + dx, 0, W, H), fill=255)
        ok = ImageChops.multiply(ok, clear)
    return ImageChops.subtract(src, soft), ImageChops.subtract(soft, src), ok


up = Image.new('RGB', (W, H)); down = Image.new('RGB', (W, H)); done = Image.new('L', (W, H), 0)
for dx in (25, -25, 60):
    u, d, ok = grain(dx)
    use = ImageChops.multiply(ok, ImageChops.invert(done))
    up, down = Image.composite(u, up, use), Image.composite(d, down, use)
    done = ImageChops.lighter(done, ok)
grey = ImageChops.subtract(ImageChops.add(tone, up), down)
# the ochre column under the tail (its edges measured just above and below the ship): the column mirrored from above
col = Image.new('L', (W, H), 0)
ImageDraw.Draw(col).polygon([(1355, 225), (1393, 225), (1386, 358), (1349, 358)], fill=255)
fill = Image.composite(mir, grey, col.filter(ImageFilter.GaussianBlur(1.5)))
feather = hole.filter(ImageFilter.GaussianBlur(3))
bg = Image.composite(fill, dark, feather)

# 3. the band and the airship at band scale (premultiplied, so its rim doesn't drag the smoke along)
w = x1 - x0
h_ = round(w * 600 / 1067)
k = 1067 / w
bg.crop((x0, bottom - h_, x1, bottom)).resize((1067, 600), Image.LANCZOS).save(out_band)
ship = dark.convert('RGBA')
ship.putalpha(alpha)
bb = alpha.point(lambda t: 255 if t > 8 else 0).getbbox()
bb = (bb[0] - 2, bb[1] - 2, bb[2] + 2, bb[3] + 2)
sw, sh = round((bb[2] - bb[0]) * k), round((bb[3] - bb[1]) * k)
ship.crop(bb).convert('RGBa').resize((sw, sh), Image.LANCZOS).convert('RGBA').save(out_ship)
cx = ((bb[0] + bb[2]) / 2 - x0) * k
cy = ((bb[1] + bb[3]) / 2 - (bottom - h_)) * k
print(f'ship {sw}x{sh} centre in band: {cx:.1f}, {cy:.1f}')
