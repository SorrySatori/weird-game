"""The main menu's background from Marti's painting (straightened by menu_painting.py), and the bits that move on it.

usage: menu_painting_band.py painting.png out_dir x0 x1 top bottom width [ref.png]
ref: an earlier, sharper photo of the painting laid onto the same pixels (menu_painting.py ... ref): the shapes (the
airship's mask, the clock's hands, the Scraper's windows, the cathedral's light) are found on it, because a darker
repaint photographed softer has no clean thresholds; the colours always come from painting.png.
out_dir gets:
  band.png        the painting's x0..x1 / top..bottom scaled to `width` px wide (the whole painting at 1012: as large as
                  the full-screen menus showed it); the airship's spot is sky, the clock face has no hands. MainScene
                  places and scales it per menu layout (a side band shows it whole at 600 px high).
  airship.png     the green airship (it flies), cut out of the painting
  idle_weight.png where Edgar (R) and Ortolan (G) are, soft-edged: MainScene's shader breathes and sways them whole
  scraper_window_*, cathedral_*
                  the painting redrawn a little (a window on/off, the cathedral's light in another colour): opaque
                  patches of the band, only where it differs
  clock_*.png     the town hall clock's hands (they turn about the pivot)
  layers.json     where everything goes, in band.png's pixels, + the list of files (MainScene.createPaintingLife)
All the layers are resampled exactly like the band (PIL resize with a box), so at rest they sit on it pixel for pixel.
The coordinates are for the 2026-11-23 photo of the finished painting.
"""
import json
import math
import os
import sys
from PIL import Image, ImageFilter, ImageChops, ImageMath, ImageDraw

src_p, out_dir = sys.argv[1:3]
x0, x1, top, bottom, width = (int(v) for v in sys.argv[3:8])
paint = Image.open(src_p).convert('RGB')
W, H = paint.size
geo = Image.open(sys.argv[8]).convert('RGB') if len(sys.argv) > 8 else paint      # where the shapes are found
assert geo.size == paint.size, 'ref must be the same size as the painting'
BOX = (1682, 318, 1930, 490)          # the airship with its fins and drips
SCRAPER_RIGHT = 1660                  # the Scraper's right edge, left of the ship
POLE = (1666, 378, 1684, 600)         # the thin dark pole left of the gondola
GRAIN = (1690, 226, 1862, 316)        # the light sky just above the ship: its pencil grain fills the hole
# the ochre smoke column right of the ship: it runs on behind the tail fins
OCHRE_UNDER_TAIL = [(1866, 318), (1942, 318), (1944, 442), (1896, 442)]


def L(expr, **ims):
    return ImageMath.lambda_eval(lambda e: e['convert'](expr(e), 'L'), **ims)


# 1. the airship's mask from its colours: green/teal (balloon, fins, drips) + the warm gondola, closed over the
#    lattice lines; then its dark outline (only right next to it). PIL's hue runs 0-255: green ~85, teal ~120.
h, s, v = geo.convert('HSV').split()
gondola = Image.new('L', (W, H), 0)
ImageDraw.Draw(gondola).ellipse((1730, 406, 1886, 470), fill=255)
green = L(lambda e: ((e['h'] > 60) & (e['h'] < 150) & (e['s'] > 60)) * 255, h=h, s=s)
warm = L(lambda e: ((e['h'] < 36) & (e['s'] > 70)) * 255, h=h, s=s)
col = ImageChops.lighter(green, ImageChops.multiply(warm, gondola))
box = Image.new('L', (W, H), 0)
ImageDraw.Draw(box).rectangle(BOX, fill=255)
col = ImageChops.multiply(col, box)
closed = col.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
near = closed.filter(ImageFilter.MaxFilter(7))
outline = ImageChops.multiply(near, v.point(lambda t: 255 if t < 100 else 0))
mask = ImageChops.lighter(closed, outline)
# the balloon and the gondola are solid: fill what the mask encloses there
hull = Image.new('L', (W, H), 0)
ImageDraw.Draw(hull).ellipse((1688, 327, 1910, 408), fill=255)                  # the balloon
ImageDraw.Draw(hull).ellipse((1735, 410, 1882, 466), fill=255)                  # the gondola
hull = ImageChops.multiply(hull, mask.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9)))
mask = ImageChops.lighter(mask, hull)
alpha = mask.filter(ImageFilter.GaussianBlur(0.7))

# 2. the sky where it was: the surrounding sky's tone (normalised convolution, without the ochre column, the
#    Scraper and the pole left of the ship), blended top to bottom + the pencil grain of the sky
#    just above it, tiled
hole = mask.filter(ImageFilter.MaxFilter(9))
# the whole envelope, also the sky between the ropes and drips (it's tinted by them)
ImageDraw.Draw(hole).polygon([(1704, 400), (1888, 400), (1880, 490), (1724, 490)], fill=255)
dh, ds, dv = geo.convert('HSV').split()
ochre = L(lambda e: ((e['h'] >= 18) & (e['h'] <= 50) & (e['s'] > 60) & (e['v'] > 100)) * 255, h=dh, s=ds, v=dv)
other = ochre.filter(ImageFilter.MaxFilter(5))
ImageDraw.Draw(other).rectangle((0, 0, SCRAPER_RIGHT, H), fill=255)
ImageDraw.Draw(other).rectangle(POLE, fill=255)


def normconv(img, known):
    out = None
    for r in (64, 32, 16, 8, 4):
        num = Image.merge('RGB', [ImageChops.multiply(c, known).filter(ImageFilter.GaussianBlur(r)) for c in img.split()])
        den = known.filter(ImageFilter.GaussianBlur(r))
        est = Image.merge('RGB', [L(lambda e: e['float'](e['n']) * 255.0 / (e['float'](e['d']) + 0.5), n=c, d=den)
                                  for c in num.split()])
        out = est if out is None else Image.composite(est, out, den.point(lambda t: max(0, min(255, (t - 50) * 4))))
    return out


near = normconv(paint, ImageChops.multiply(ImageChops.invert(hole), ImageChops.invert(other)))
# the tone runs from the sky above the hole to the sky below it, column by column (the sky is lighter above the
# ship and smudged darker below; a round blend made one flat grey blot), smoothed sideways (column by column it
# drew vertical streaks) and mixed with the round blend
tone = near.copy()
hp_, np_, tp = hole.load(), near.load(), tone.load()
for x in range(BOX[0] - 8, min(W, BOX[2] + 8)):
    ys = [y for y in range(BOX[1] - 12, BOX[3] + 12) if hp_[x, y]]
    if not ys:
        continue
    ya, yb = ys[0] - 3, ys[-1] + 3
    ca, cb = np_[x, ya], np_[x, yb]
    for y in range(ya + 1, yb):
        f = (y - ya) / (yb - ya)
        tp[x, y] = tuple(round(a + f * (b - a)) for a, b in zip(ca, cb))
rb = (BOX[0] - 40, BOX[1] - 20, min(W, BOX[2] + 40), BOX[3] + 20)
rw, rh = rb[2] - rb[0], rb[3] - rb[1]
smooth = tone.copy()
smooth.paste(tone.crop(rb).resize((max(1, rw // 32), rh), Image.BOX).resize((rw, rh), Image.BICUBIC), rb[:2])
tone = Image.composite(Image.blend(smooth, near, 0.4).filter(ImageFilter.GaussianBlur(3)), near, hole)
# the grain: the patch's fine detail (lightness minus a small blur, the same on all three channels, so its washes
# stay out), tiled over the hole like bricks (mirrored tiles drew symmetric blots)
patch = paint.crop(GRAIN).convert('L')
soft = patch.filter(ImageFilter.GaussianBlur(3))
hi, lo = ImageChops.subtract(patch, soft), ImageChops.subtract(soft, patch)
up_l, down_l = Image.new('L', (W, H), 0), Image.new('L', (W, H), 0)
pw, ph = patch.size
for j, y in enumerate(range(BOX[1] - 12, BOX[3] + 12, ph)):
    for x in range(BOX[0] - 12 - (pw // 2) * (j % 2), BOX[2] + 12, pw):
        up_l.paste(hi, (x, y)); down_l.paste(lo, (x, y))
up, down = Image.merge('RGB', [up_l] * 3), Image.merge('RGB', [down_l] * 3)
up, down = (Image.eval(g, lambda t: t * 3 // 4) for g in (up, down))   # the sky round the ship is a little calmer
sky = ImageChops.subtract(ImageChops.add(tone, up), down)

# the ochre column under the tail: mirrored per pixel column from just above the hole
hp, pp = hole.load(), paint.load()
mir = paint.copy()
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
            mp[x, yy] = pp[x, sy] if sy >= 0 and not hp[x, sy] else pp[x, ya - 1]
col = Image.new('L', (W, H), 0)
ImageDraw.Draw(col).polygon(OCHRE_UNDER_TAIL, fill=255)
fill = Image.composite(mir, sky, col.filter(ImageFilter.GaussianBlur(1.5)))
bg = Image.composite(fill, paint, hole.filter(ImageFilter.GaussianBlur(5)))


# 3. the clock on the town hall: its two hands are one dark V from the pivot; lift them off the face
CLOCK_C, CLOCK_R = (1809, 700), 34          # the white face (inside the numerals' outer ends)
PIVOT = (1809.5, 698.0)
MINUTE_TIP, HOUR_TIP = (1784, 718), (1830.5, 724)     # it says about twenty to five
lum, glum = paint.convert('L'), geo.convert('L')        # the painting's lightness / the shapes'
face = Image.new('L', (W, H), 0)
ImageDraw.Draw(face).ellipse((CLOCK_C[0] - CLOCK_R, CLOCK_C[1] - CLOCK_R, CLOCK_C[0] + CLOCK_R, CLOCK_C[1] + CLOCK_R), fill=255)
dark = ImageChops.multiply(glum.point(lambda t: 255 if t < 125 else 0), face)
hands = dark.copy()
ImageDraw.floodfill(hands, (round(PIVOT[0]), round(PIVOT[1]) + 2), 128, thresh=0)       # the V, not the numerals
hands = hands.point(lambda t: 255 if t == 128 else 0)
assert hands.getbbox(), 'the pivot is not on the hands'
hands_wide = ImageChops.multiply(hands.filter(ImageFilter.MaxFilter(5)), face)
face_known = ImageChops.multiply(ImageChops.multiply(face.filter(ImageFilter.MinFilter(5)), ImageChops.invert(hands_wide)),
                                 glum.point(lambda t: 255 if t > 150 else 0))


def normconv_small(img, known, radii=(8, 4, 2)):
    out = None
    for r in radii:
        num = Image.merge('RGB', [ImageChops.multiply(c, known).filter(ImageFilter.GaussianBlur(r)) for c in img.split()])
        den = known.filter(ImageFilter.GaussianBlur(r))
        est = Image.merge('RGB', [L(lambda e: e['float'](e['n']) * 255.0 / (e['float'](e['d']) + 0.5), n=c, d=den)
                                  for c in num.split()])
        out = est if out is None else Image.composite(est, out, den.point(lambda t: max(0, min(255, (t - 50) * 4))))
    return out


bg = Image.composite(normconv_small(bg, face_known), bg, hands_wide.filter(ImageFilter.GaussianBlur(0.8)))
# each hand: its own sector of the V (the hub belongs to both), alpha from how much darker than the face it is
fl = sorted(lum.getpixel((x, y)) for x in range(CLOCK_C[0] - 20, CLOCK_C[0] + 20, 2)
            for y in range(CLOCK_C[1] - 20, CLOCK_C[1] + 20, 2) if face_known.getpixel((x, y)))
face_l = fl[len(fl) // 2]
hand_px = [(x, y) for y in range(CLOCK_C[1] - CLOCK_R, CLOCK_C[1] + CLOCK_R) for x in range(CLOCK_C[0] - CLOCK_R, CLOCK_C[0] + CLOCK_R)
           if hands.getpixel((x, y))]
ls = sorted(lum.getpixel(p) for p in hand_px)
hand_l = ls[len(ls) // 10]
darkest = sorted(hand_px, key=lambda p: lum.getpixel(p))[:max(1, len(hand_px) // 3)]
hand_rgb = tuple(sorted(paint.getpixel(p)[i] for p in darkest)[len(darkest) // 2] for i in range(3))


def angle(p):
    return math.atan2(p[1] - PIVOT[1], p[0] - PIVOT[0])


A_MIN, A_HOUR = angle(MINUTE_TIP), angle(HOUR_TIP)
hand_alpha = {'minute': Image.new('L', (W, H), 0), 'hour': Image.new('L', (W, H), 0)}
hw = hands_wide.load()
for y in range(CLOCK_C[1] - CLOCK_R, CLOCK_C[1] + CLOCK_R):
    for x in range(CLOCK_C[0] - CLOCK_R, CLOCK_C[0] + CLOCK_R):
        if not hw[x, y]:
            continue
        a = max(0.0, min(1.0, (face_l - lum.getpixel((x, y))) / max(1, face_l - hand_l)))
        if a <= 0:
            continue
        r = math.hypot(x - PIVOT[0], y - PIVOT[1])
        t = angle((x, y))
        dm = abs(math.remainder(t - A_MIN, math.tau))
        dh = abs(math.remainder(t - A_HOUR, math.tau))
        for name, mine in (('minute', dm <= dh), ('hour', dh < dm)):
            if mine or r < 5:
                hand_alpha[name].putpixel((x, y), round(a * 255))

# 4. the two characters move whole (MainScene's PaintingIdleFX shader breathes and sways them): where they are, as a
#    soft weight (R = Edgar, G = Ortolan), traced ~3 px outside their ink outline; the sack, boots and the gap
#    between the legs belong to them (the feet barely move, the shader anchors them)
CHARACTERS = {
    'edgar': [(255, 905), (262, 889), (275, 884), (290, 893), (305, 884), (320, 893), (338, 893), (352, 891), (372, 893),
              (387, 905), (384, 925), (380, 960), (372, 990), (392, 1012), (410, 1040), (415, 1100), (414, 1180),
              (413, 1258), (390, 1262), (387, 1275), (388, 1336), (326, 1336), (324, 1275), (300, 1268), (297, 1336),
              (216, 1336), (215, 1305), (232, 1290), (236, 1262), (238, 1185), (198, 1183), (196, 1135), (207, 1112),
              (203, 1080), (207, 1062), (206, 1046), (222, 1046), (238, 1030), (244, 1006), (262, 995), (255, 970),
              (252, 930)],
    'ortolan': [(1745, 852), (1770, 848), (1800, 851), (1815, 868), (1822, 895), (1822, 918), (1815, 950), (1832, 972),
                (1846, 990), (1848, 1050), (1848, 1150), (1848, 1240), (1830, 1248), (1812, 1250), (1806, 1262),
                (1820, 1300), (1820, 1332), (1764, 1333), (1760, 1300), (1752, 1300), (1755, 1322), (1698, 1323),
                (1697, 1290), (1702, 1262), (1683, 1260), (1680, 1200), (1680, 1100), (1682, 1000), (1690, 978),
                (1712, 965), (1720, 950), (1719, 918), (1724, 876)],
}
weights = {}
for name, poly in CHARACTERS.items():
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    weights[name] = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(4))

# 5. the variants: the painting redrawn a little (Scraper windows go on/off, the cathedral's light changes colour);
#    each becomes a patch of the band where it differs
VARIANTS = {}       # name -> (edited painting, the full-res box where it may differ)


def mirror_fill(img, mask, rows):
    """the lowest `rows` pixels of every column of mask, from the pixels just below it (what was behind the bottom)"""
    out = img.copy()
    op, ip, mp_ = out.load(), img.load(), mask.load()
    bx = mask.getbbox()
    for x in range(bx[0], bx[2]):
        ys = [y for y in range(bx[1], bx[3]) if mp_[x, y] > 127]
        if ys:
            for i in range(rows):
                op[x, ys[-1] - i] = ip[x, min(H - 1, ys[-1] + 1 + i)]
    return out


def moved(base, under, mask, dy, rot=0.0, pivot=None):
    """base with the masked part lifted dy px (and turned rot degrees anticlockwise about pivot) over `under`"""
    bx = mask.getbbox()
    m = 12
    box = (bx[0] - m, bx[1] - m, bx[2] + m, bx[3] + m)
    part = base.convert('RGBA').crop(box)
    part.putalpha(mask.crop(box).filter(ImageFilter.GaussianBlur(0.6)))
    c = ((pivot[0] - box[0], pivot[1] - box[1]) if pivot else None)
    part = part.convert('RGBa').rotate(rot, resample=Image.BICUBIC, center=c, translate=(0, -dy)).convert('RGBA')
    out = under.convert('RGBA')
    out.alpha_composite(part, box[:2])
    return out.convert('RGB'), box


def poly_mask(poly):
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    return m


# the Scraper's windows: the lit (orange) ones go dark green like the rest, a few green ones light up; each window's
# inside = what the flood from its middle reaches before the dark frame
LIT = [(1623, 338), (1581, 495), (1602, 720), (1540, 778), (1635, 842)]
DARK = [(1564, 464), (1582, 534), (1613, 526), (1600, 605), (1570, 646), (1572, 762), (1592, 812), (1555, 820), (1605, 852)]


def window(seed, lit=False):
    if lit:
        # a lit window has dark scribbles in its orange: its inside = the orange around the seed, closed over them
        box = (seed[0] - 22, seed[1] - 26, seed[0] + 22, seed[1] + 26)
        hh, ss, vv = (c.crop(box) for c in geo.convert('HSV').split())
        o = L(lambda e: ((e['h'] >= 10) & (e['h'] <= 32) & (e['s'] > 70) & (e['v'] > 130)) * 255, h=hh, s=ss, v=vv)
        o = o.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
        full = Image.new('L', (W, H), 0)
        full.paste(o, box[:2])
        return full
    # the frame: dark (< 75), thickened a pixel so its thin spots don't let the flood out; the inside grows back
    frame = glum.crop((seed[0] - 30, seed[1] - 30, seed[0] + 30, seed[1] + 30)).point(lambda t: 255 if t < 75 else 0)
    m = ImageChops.invert(frame.filter(ImageFilter.MaxFilter(3)))
    ImageDraw.floodfill(m, (30, 30), 128, thresh=0)
    m = m.point(lambda t: 255 if t == 128 else 0).filter(ImageFilter.MaxFilter(3))
    bb = m.getbbox()
    assert bb and bb[2] - bb[0] < 40 and bb[3] - bb[1] < 48, f'window at {seed} leaks: {bb}'
    full = Image.new('L', (W, H), 0)
    full.paste(m, (seed[0] - 30, seed[1] - 30))
    return full


def texture(seed, lit=False):
    m = window(seed, lit)
    bb = m.filter(ImageFilter.MinFilter(3)).getbbox()
    return bg.crop(bb)


lit_tex, dark_tex = texture(LIT[3], True), texture(DARK[5])
windows = []
for lit, seeds in ((True, LIT), (False, DARK)):
    for seed in seeds:
        m = window(seed, lit)
        bb = m.getbbox()
        tex = (dark_tex if lit else lit_tex).resize((bb[2] - bb[0], bb[3] - bb[1]), Image.BICUBIC)
        layer = bg.copy()
        layer.paste(tex, bb[:2])
        soft = m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
        name = f'scraper_window_{len(windows)}'
        VARIANTS[name] = (Image.composite(layer, bg, soft), (bb[0] - 3, bb[1] - 3, bb[2] + 3, bb[3] + 3))
        windows.append({'name': name, 'lit': lit})

# the cathedral's light (its three arched windows and the door) in other colours, to fade to now and then
CATHEDRAL_LIGHTS = [(320, 405, 357, 470), (241, 560, 279, 630), (401, 555, 439, 626), (302, 690, 387, 818)]
ch, cs, cv = geo.convert('HSV').split()
yellow = L(lambda e: ((e['h'] >= 18) & (e['h'] <= 55) & (e['s'] > 20) & (e['v'] > 120)) * 255, h=ch, s=cs, v=cv)
lights = Image.new('L', (W, H), 0)
for b_ in CATHEDRAL_LIGHTS:
    ImageDraw.Draw(lights).rectangle(b_, fill=255)
lights = ImageChops.multiply(lights, yellow).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
LIGHT_HUES = {'violet': 195, 'green': 78, 'rose': 232, 'cyan': 128}     # PIL hue, 0-255
lbox = (min(b_[0] for b_ in CATHEDRAL_LIGHTS) - 4, min(b_[1] for b_ in CATHEDRAL_LIGHTS) - 4,
        max(b_[2] for b_ in CATHEDRAL_LIGHTS) + 4, max(b_[3] for b_ in CATHEDRAL_LIGHTS) + 4)
for name, hue in LIGHT_HUES.items():
    crop = bg.crop(lbox).convert('HSV')
    h0, s0, v0 = crop.split()
    recol = Image.merge('HSV', (h0.point(lambda t: hue), s0.point(lambda t: min(255, int(t * 1.35) + 25)), v0)).convert('RGB')
    layer = bg.copy()
    layer.paste(recol, lbox[:2])
    VARIANTS['cathedral_' + name] = (Image.composite(layer, bg, lights), lbox)

# the graveyard: where a green glow may rise (between the graves, in front of the stone face)
GLOW_SPOTS = [(815, 545), (900, 612), (1015, 598), (1060, 612), (1135, 590), (1200, 585), (1255, 580), (1120, 640)]

# 6. the band and the layers, all resampled the same way (a box resize, so a region equals the band's pixels)
SPIRE_TOP = 180           # painting y just above the cathedral's spire: where the full-screen layout starts
w, h_ = x1 - x0, bottom - top
sx = width / w
bw, bh = width, round(h_ * sx)
ky = bh / h_              # (a hair off sx, so the box never reaches past the painting)
pad = 0
os.makedirs(out_dir, exist_ok=True)


def to_band(x, y):
    return pad + (x - x0) * sx, (y - top) * ky


def region(img, bb):
    """img (painting size) resampled into band rect bb (band px)"""
    a, b, c, d = bb
    return img.resize((c - a, d - b), Image.LANCZOS,
                      box=(x0 + (a - pad) / sx, top + b / ky, x0 + (c - pad) / sx, top + d / ky))


def band_box(full_bb, margin=2):
    p, q = to_band(full_bb[0], full_bb[1]), to_band(full_bb[2], full_bb[3])
    return (max(0, math.floor(p[0]) - margin), max(0, math.floor(p[1]) - margin),
            min(bw, math.ceil(q[0]) + margin), min(bh, math.ceil(q[1]) + margin))


def sprite(rgb, alpha, name):
    rgba = rgb.convert('RGBA')
    rgba.putalpha(alpha)
    bb = band_box(alpha.getbbox())
    out = region(rgba.convert('RGBa'), bb).convert('RGBA')
    out.save(os.path.join(out_dir, name + '.png'))
    return {'x': bb[0], 'y': bb[1], 'w': bb[2] - bb[0], 'h': bb[3] - bb[1]}


region(bg, (0, 0, bw, bh)).save(os.path.join(out_dir, 'band.png'))
layers = {'band': {'w': bw, 'h': bh, 'spireTop': round((SPIRE_TOP - top) * ky)}}

# the airship: flies, so it's a plain sprite; its centre is where it starts
ship = sprite(paint, alpha, 'airship')
layers['airship'] = {'x': ship['x'] + ship['w'] / 2, 'y': ship['y'] + ship['h'] / 2}

# the variants: opaque patches of the band where the redrawn painting differs
for name, (img, full_bb) in VARIANTS.items():
    bb = band_box(full_bb, margin=2)
    new, old = region(img, bb), region(bg, bb)
    diff = ImageChops.difference(new, old).convert('L').point(lambda t: 255 if t > 2 else 0).getbbox()
    assert diff, name + ' changes nothing'
    pb = (bb[0] + diff[0], bb[1] + diff[1], bb[0] + diff[2], bb[1] + diff[3])
    new.crop(diff).save(os.path.join(out_dir, name + '.png'))
    layers[name] = {'x': pb[0], 'y': pb[1]}
layers['scraper_windows'] = windows
layers['cathedral_lights'] = ['cathedral_' + n for n in LIGHT_HUES]
layers['glow_spots'] = [[round(v, 1) for v in to_band(*p)] for p in GLOW_SPOTS]

# the characters' weight map (band size) and what the shader needs to move them: the soles (anchor), how tall they
# are and their middle, in band px
Image.merge('RGB', (region(weights['edgar'], (0, 0, bw, bh)), region(weights['ortolan'], (0, 0, bw, bh)),
                    Image.new('L', (bw, bh), 0))).save(os.path.join(out_dir, 'idle_weight.png'))
layers['idle'] = {}
for name, poly in CHARACTERS.items():
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    (lx, top_y), (rx, foot_y) = to_band(min(xs), min(ys)), to_band(max(xs), max(ys))
    layers['idle'][name] = {'feetY': round(foot_y, 1), 'height': round(foot_y - top_y, 1),
                            'centreX': round((lx + rx) / 2, 1), 'halfWidth': round((rx - lx) / 2, 1)}

# the clock hands: one colour, alpha = darkness; they turn about the pivot
for name, a in hand_alpha.items():
    sp = sprite(Image.new('RGB', (W, H), hand_rgb), a, 'clock_' + name)
    px_, py_ = to_band(*PIVOT)
    sp.update({'pivotX': px_, 'pivotY': py_, 'originX': (px_ - sp['x']) / sp['w'], 'originY': (py_ - sp['y']) / sp['h']})
    layers['clock_' + name] = sp
layers['clock_minute']['angle'] = math.degrees(A_MIN)
layers['clock_hour']['angle'] = math.degrees(A_HOUR)

layers['files'] = sorted(f[:-4] for f in os.listdir(out_dir) if f.endswith('.png') and f != 'band.png')
with open(os.path.join(out_dir, 'layers.json'), 'w') as f:
    json.dump(layers, f, indent=1)
print(json.dumps(layers))
