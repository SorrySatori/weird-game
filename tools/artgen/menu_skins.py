"""The main menu's TRIAL skins (2026-11-24): the band layout of ui/mainMenuBand.js dressed four more ways, the art drawn
here (PIL only), the life (glows, blinks, sparks, sway) added in ui/menuThemes/<skin>.js.

  python3 tools/artgen/menu_skins.py [skin ...]          # -> assets/images/ui/menu/skins/<skin>/*.png
  python3 tools/artgen/menu_skins.py --preview [skin ...]  # + out/menu_skins/<skin>_preview.png (a mock of the menu)

Skins:
  rust     corrugated rusty sheet, rivets, wires, weeds through the rust holes; scrap plates with caged lamps;
           the title stencilled on a rusty sign (Saira Stencil One / Saira Condensed)
  biomech  bone and blackened metal: ribbed tubes, a spine for the rule, red lymph in glass veins; the entries as
           ribbed pods; the title cast in Grenze Gotisch on a biomechanical cartouche (Grenze)
  jungle   a crumbling concrete wall: cracks, rebar, a drainpipe, ivy, moss and glowing mycelium; cracked slabs for
           the entries; the title as old shop-sign letters (Bungee) on a broken lintel, ivy over it (Rubik)
  crazy    a living machine: veined membrane stitched with wire, eyes, teeth along the rule; the title a ransom
           note of letters in nine fonts, its O an eye (Rubik Beastly)

Every texture is drawn at the game's 1x (the band is 219 px wide in the main menu, 320 in the pause menu, the panels
470): bands and panels at their widest, the plates as nine-slice sources (corners fixed, the middle stretched).
"""
import json, math, os, random, sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'assets', 'images', 'ui', 'menu', 'skins')
FONTS = os.path.join(ROOT, 'assets', 'fonts')
TOOL_FONTS = os.path.join(ROOT, 'tools', 'artgen', 'fonts')       # title-only faces, not shipped with the game
H = 600
BAND_W, BAND_WIDE, PANEL_W = 220, 320, 470
PLATE_W, PLATE_H = 200, 46                                     # nine-slice source of an entry
TITLE_W, TITLE_H = 520, 150


def font(name, px, wght=None):
    path = os.path.join(FONTS, name) if os.path.exists(os.path.join(FONTS, name)) else os.path.join(TOOL_FONTS, name)
    f = ImageFont.truetype(path, px)
    if wght:
        f.set_variation_by_axes(wght if isinstance(wght, (list, tuple)) else [wght])
    return f


# --- texture kit ------------------------------------------------------------------------------------------------------
def noise(w, h, cell, seed, octaves=4, keep=0.5):
    """fractal value noise (L, stretched to 0..255): `cell` px for the coarsest octave, each next one half that"""
    rnd = random.Random(seed)
    acc, total, amp = None, 0.0, 1.0
    for o in range(octaves):
        c = max(1, round(cell / 2 ** o))
        gw, gh = w // c + 4, h // c + 4
        small = Image.new('L', (gw, gh))
        small.putdata([rnd.randrange(256) for _ in range(gw * gh)])
        layer = small.resize((gw * c, gh * c), Image.BICUBIC).crop((c, c, c + w, c + h))
        acc = layer if acc is None else Image.blend(acc, layer, amp / (total + amp))
        total += amp
        amp *= keep
    lo, hi = acc.getextrema()
    return acc.point(lambda v: round((v - lo) * 255 / max(1, hi - lo)))


def gmap(L, stops):
    """a gradient map: L 0..255 through colour stops [(0..1, (r, g, b)), ...] -> RGB"""
    luts = [[], [], []]
    for i in range(256):
        t = i / 255
        for k in range(len(stops) - 1):
            if stops[k][0] <= t <= stops[k + 1][0]:
                a, b = stops[k], stops[k + 1]
                u = (t - a[0]) / max(1e-6, b[0] - a[0])
                break
        else:
            a = b = stops[0] if t < stops[0][0] else stops[-1]
            u = 0
        for ch in range(3):
            luts[ch].append(round(a[1][ch] + (b[1][ch] - a[1][ch]) * u))
    return Image.merge('RGB', [L.point(luts[ch]) for ch in range(3)])


def curve(L, f):
    return L.point([max(0, min(255, round(255 * f(i / 255)))) for i in range(256)])


def threshold(L, t, soft=12):
    """a mask: 255 above t, a soft edge `soft` wide"""
    return L.point(lambda v: max(0, min(255, round((v - t + soft) * 255 / (2 * soft)))))


def relief(height, k=1.0, blur=1.2):
    """lighting from the top-left off a height map: L, 128 = flat"""
    hgt = height.filter(ImageFilter.GaussianBlur(blur)) if blur else height
    a = ImageChops.offset(hgt, 1, 1)
    b = ImageChops.offset(hgt, -1, -1)
    return ImageChops.subtract(b, a, scale=1.0 / k, offset=128)


def lit(img, shade):
    """overlay a 128-centred shade map onto img"""
    rgb = img.convert('RGB')
    return ImageChops.overlay(rgb, Image.merge('RGB', (shade, shade, shade)))


def mul(img, L):
    return ImageChops.multiply(img.convert('RGB'), Image.merge('RGB', (L, L, L)))


def solid(size, colour):
    return Image.new('RGB', size, colour)


def paste_mask(base, top, mask):
    out = base.copy()
    out.paste(top, (0, 0), mask)
    return out


def vgrad(w, h, stops):
    """an L vertical gradient, stops [(0..1, value)]"""
    col = Image.new('L', (1, h))
    vals = []
    for y in range(h):
        t = y / max(1, h - 1)
        for k in range(len(stops) - 1):
            if stops[k][0] <= t <= stops[k + 1][0]:
                u = (t - stops[k][0]) / max(1e-6, stops[k + 1][0] - stops[k][0])
                vals.append(round(stops[k][1] + (stops[k + 1][1] - stops[k][1]) * u))
                break
        else:
            vals.append(stops[-1][1])
    col.putdata(vals)
    return col.resize((w, h))


def hgrad(w, h, f):
    row = Image.new('L', (w, 1))
    row.putdata([max(0, min(255, round(255 * f(x / max(1, w - 1))))) for x in range(w)])
    return row.resize((w, h))


def glow(mask, colour, radius, strength=1.0):
    """an RGBA glow from a mask"""
    m = mask.filter(ImageFilter.GaussianBlur(radius))
    if strength != 1:
        m = m.point(lambda v: min(255, round(v * strength)))
    g = Image.new('RGBA', mask.size, colour + (0,))
    g.putalpha(m)
    return g


def rgba(img, alpha=None):
    out = img.convert('RGBA')
    if alpha is not None:
        out.putalpha(alpha)
    return out


PANEL_DIM = 150                                                # panels carry rows of text: their art darker


def save(img, skin, name):
    if name == 'panel':
        img = mul(img, Image.new('L', img.size, PANEL_DIM if skin != 'tripe' else 105))
    elif name == 'panel_myc':
        img = Image.merge('RGBA', img.split()[:3] + (img.getchannel('A').point(lambda v: v // 2),))
    d = os.path.join(OUT, skin)
    os.makedirs(d, exist_ok=True)
    img.save(os.path.join(d, name + '.png'), optimize=True)
    return img


# --- drawn bits -------------------------------------------------------------------------------------------------------
def leaf(d, x, y, ang, size, fill, outline=None):
    """a pointed leaf from (x, y) along `ang`"""
    ca, sa = math.cos(ang), math.sin(ang)
    pts = []
    for t in [i / 8 for i in range(9)]:
        wdt = math.sin(math.pi * t) * size * 0.38
        pts.append((x + ca * t * size - sa * wdt, y + sa * t * size + ca * wdt))
    for t in [i / 8 for i in range(8, -1, -1)]:
        wdt = math.sin(math.pi * t) * size * 0.38
        pts.append((x + ca * t * size + sa * wdt, y + sa * t * size - ca * wdt))
    d.polygon(pts, fill=fill, outline=outline)


def vine(d, rnd, x, y, ang, length, step=3, width=2, colour=(46, 70, 30), leaves=(52, 88, 36), leaf_every=9,
         leaf_size=7, curl=0.08, bounds=None):
    """a wandering stem with leaves; returns its points"""
    pts = [(x, y)]
    turn = 0.0
    for i in range(int(length / step)):
        turn = turn * 0.85 + (rnd.random() - 0.5) * curl
        ang += turn
        x += math.cos(ang) * step
        y += math.sin(ang) * step
        if bounds:
            x = max(bounds[0], min(bounds[2], x))
            y = max(bounds[1], min(bounds[3], y))
        pts.append((x, y))
    d.line(pts, fill=colour, width=width, joint='curve')
    for i in range(leaf_every // 2, len(pts), leaf_every):
        px, py = pts[i]
        side = 1 if (i // leaf_every) % 2 else -1
        a = ang + side * (0.9 + rnd.random() * 0.5)
        if i + 1 < len(pts):
            a = math.atan2(pts[i + 1][1] - py, pts[i + 1][0] - px) + side * (0.9 + rnd.random() * 0.5)
        shade = tuple(max(0, min(255, c + rnd.randint(-14, 14))) for c in leaves)
        leaf(d, px, py, a, leaf_size * (0.7 + rnd.random() * 0.6), shade)
    return pts


def grass(d, rnd, x, y, n, height, colours):
    """a tuft of grass blades from (x, y)"""
    for _ in range(n):
        h = height * (0.5 + rnd.random() * 0.7)
        lean = (rnd.random() - 0.5) * 1.1
        bx = x + (rnd.random() - 0.5) * 8
        tip = (bx + lean * h * 0.6, y - h)
        mid = (bx + lean * h * 0.2, y - h * 0.5)
        col = colours[rnd.randrange(len(colours))]
        d.polygon([(bx - 1.4, y), mid, tip, (mid[0] + 1.2, mid[1]), (bx + 1.4, y)], fill=col)


def rivet(img, x, y, r, base, hi, lo):
    d = ImageDraw.Draw(img)
    d.ellipse([x - r - 1, y - r - 0.5, x + r + 1, y + r + 1.5], fill=lo)        # shadow
    d.ellipse([x - r, y - r, x + r, y + r], fill=base)
    d.ellipse([x - r * 0.6, y - r * 0.7, x + r * 0.1, y - r * 0.05], fill=hi)


def streaks(size, sources, rnd, length=(30, 90), colour=(120, 52, 20)):
    """rust run down from points: RGBA"""
    w, h = size
    m = Image.new('L', size, 0)
    d = ImageDraw.Draw(m)
    for (x, y) in sources:
        for _ in range(2):
            L = rnd.uniform(*length)
            xx = x + rnd.uniform(-2, 2)
            for k in range(int(L)):
                a = round(150 * (1 - k / L) ** 1.4)
                d.point((xx + math.sin(k * 0.15) * 0.6, y + k), fill=a)
                d.point((xx + 1, y + k), fill=a // 2)
    m = m.filter(ImageFilter.GaussianBlur(0.7))
    out = Image.new('RGBA', size, colour + (0,))
    out.putalpha(m)
    return out


def text_mask(size, xy, text, f, anchor='mm', spacing=0, stroke=0):
    m = Image.new('L', size, 0)
    d = ImageDraw.Draw(m)
    if spacing:
        widths = [d.textlength(ch, font=f) for ch in text]
        total = sum(widths) + spacing * (len(text) - 1)
        x = xy[0] - total / 2 if anchor[0] == 'm' else xy[0]
        for ch, cw in zip(text, widths):
            d.text((x, xy[1]), ch, font=f, fill=255, anchor='l' + anchor[1], stroke_width=stroke, stroke_fill=255)
            x += cw + spacing
    else:
        d.text(xy, text, font=f, fill=255, anchor=anchor, stroke_width=stroke, stroke_fill=255)
    return m


# =====================================================================================================================
# RUST
RUST_DARK, RUST, RUST_HOT = (38, 24, 18), (84, 46, 28), (122, 64, 34)
STEEL = [(0, (22, 22, 24)), (0.5, (44, 42, 42)), (1, (70, 66, 62))]
SODIUM = (255, 150, 56)


def rust_sheet(w, h, seed, paint=(44, 64, 60), seams=(), rust_amt=0.5, corrugate=20, holes=0):
    """a corrugated rusty steel sheet: old paint flaking off it, rust blooming through, rivet seams, rust runs"""
    rnd = random.Random(seed)
    base = gmap(noise(w, h, 60, seed), STEEL)
    # old paint over the steel, chipped off where the noise is low
    chip = threshold(noise(w, h, 26, seed + 1, 5, 0.6), 110, 6)
    painted = mul(solid((w, h), paint), curve(noise(w, h, 8, seed + 2, 3), lambda t: 0.75 + 0.35 * t))
    img = paste_mask(base, painted, chip)
    # rust: coarse blooms + fine pitting, more of it toward the foot and along the seams
    rn = noise(w, h, 40, seed + 3, 5, 0.55)
    foot = vgrad(w, h, [(0, 0), (0.6, 40), (1, 110)])
    seam_band = Image.new('L', (w, h), 0)
    sd = ImageDraw.Draw(seam_band)
    for sy in seams:
        sd.rectangle([0, sy - 16, w, sy + 22], fill=70)
    seam_band = seam_band.filter(ImageFilter.GaussianBlur(10))
    rmask = ImageChops.add(ImageChops.add(rn, foot), seam_band)
    rmask = threshold(rmask, round(255 * (1 - rust_amt)), 30)
    rust_col = gmap(noise(w, h, 14, seed + 4, 4), [(0, RUST_DARK), (0.55, RUST), (1, RUST_HOT)])
    img = paste_mask(img, rust_col, rmask)
    # corrugation: vertical ridges lit from the left
    if corrugate:
        ridges = hgrad(w, h, lambda t: 0.5 + 0.13 * math.sin(2 * math.pi * t * w / corrugate))
        img = lit(img, ridges)
    # the surface: pits and dents
    img = lit(img, relief(noise(w, h, 6, seed + 5, 3), 0.7, 0.8))
    # rust runs from the seams
    d = ImageDraw.Draw(img)
    srcs = []
    for sy in seams:
        # the overlap: a shadow under the upper sheet's edge, a lit lip above it
        d.rectangle([0, sy, w, sy + 3], fill=(10, 8, 8))
        d.line([(0, sy - 1), (w, sy - 1)], fill=(96, 80, 66))
        for rx in range(10, w, 26):
            rivet(img, rx + rnd.randint(-1, 1), sy - 7, 3, (70, 58, 50), (128, 108, 90), (14, 10, 8))
            srcs.append((rx, sy - 4))
    img = Image.alpha_composite(img.convert('RGBA'), streaks((w, h), srcs, rnd)).convert('RGB')
    # holes rusted through
    hole_pts = []
    for _ in range(holes):
        hx, hy = rnd.randint(20, w - 40), rnd.randint(60, h - 80)
        r = rnd.randint(6, 12)
        m = Image.new('L', (w, h), 0)
        md = ImageDraw.Draw(m)
        pts = [(hx + math.cos(a) * r * rnd.uniform(0.6, 1.3), hy + math.sin(a) * r * rnd.uniform(0.5, 1.1))
               for a in [i * math.pi / 7 for i in range(14)]]
        md.polygon(pts, fill=255)
        edge = m.filter(ImageFilter.MaxFilter(5))
        img.paste(RUST_HOT, (0, 0), ImageChops.subtract(edge, m).point(lambda v: v * 0.8))
        img.paste((6, 5, 6), (0, 0), m)
        hole_pts.append((hx, hy, r))
    return img, hole_pts


def rust_band(w, h, seed, panel=False):
    img, holes = rust_sheet(w, h, seed, paint=(46, 60, 56) if not panel else (52, 48, 46),
                            seams=(196, 404) if not panel else (150, 450), rust_amt=0.42, holes=2 if not panel else 3)
    rnd = random.Random(seed + 9)
    # dark: the band is a backdrop; darkest toward the garden at its foot
    img = mul(img, vgrad(w, h, [(0, 170), (0.5, 150), (1, 80)]))
    img = mul(img, hgrad(w, h, lambda t: 0.72 + 0.28 * math.sin(math.pi * min(1, t * 1.15)) ** 0.5))
    over = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    # two sagging cables across, bindweed twisting along one of them
    for k, (y0, sag) in enumerate([(78, 22), (338, 30)] if not panel else [(60, 26)]):
        pts = [(x, y0 + sag * math.sin(math.pi * x / w) + 4 * math.sin(x * 0.02 + k)) for x in range(-4, w + 5, 3)]
        d.line([(x, y + 2) for x, y in pts], fill=(0, 0, 0, 120), width=3)
        d.line(pts, fill=(18, 16, 16, 255), width=3)
        d.line([(x, y - 1) for x, y in pts], fill=(70, 64, 58, 255), width=1)
        if k == 0:
            # the vine winds round the cable
            for x in range(0, w, 2):
                y = pts[min(len(pts) - 1, x // 3)][1] + 3.5 * math.sin(x * 0.18)
                d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(40, 64, 28, 255))
                if x % 14 == 0:
                    leaf(d, x, y, -math.pi / 2 + rnd.uniform(-0.8, 0.8), rnd.uniform(5, 8),
                         (54 + rnd.randint(-8, 8), 86 + rnd.randint(-10, 10), 34, 255))
    # weeds through the holes and along the foot
    for hx, hy, r in holes:
        grass(d, rnd, hx, hy + r * 0.3, 7, 26, [(58, 82, 34, 255), (74, 96, 40, 255), (46, 66, 28, 255)])
    for x in range(-6, w + 6, 9):
        grass(d, rnd, x, h - 2, 3, 18 + rnd.random() * 22, [(46, 64, 28, 255), (62, 84, 36, 255), (78, 92, 44, 255)])
    # a thistle and a dock leaf at the foot
    tx = w * 0.42
    d.line([(tx, h), (tx + 3, h - 70)], fill=(56, 70, 36, 255), width=2)
    for k in range(4):
        leaf(d, tx + 1, h - 18 - k * 13, -math.pi / 2 + (1 if k % 2 else -1) * 1.1, 13, (62, 80, 40, 255))
    d.ellipse([tx - 3, h - 80, tx + 9, h - 68], fill=(70, 78, 44, 255))
    d.pieslice([tx - 3, h - 90, tx + 9, h - 72], 200, 340, fill=(150, 70, 130, 255))
    over = over.filter(ImageFilter.GaussianBlur(0.35))
    out = Image.alpha_composite(img.convert('RGBA'), over)
    return out.convert('RGB')


def rust_pipe(h, seed, w=18):
    """the rule: a rusty pipe with flanges, bindweed climbing it"""
    rnd = random.Random(seed)
    core = 10
    x0 = (w - core) // 2
    cyl = hgrad(core, h, lambda t: 0.18 + 0.75 * math.sin(math.pi * (0.12 + 0.88 * t)) ** 2 * (1 - 0.55 * t))
    metal = gmap(noise(core, h, 20, seed, 4), [(0, RUST_DARK), (0.5, (98, 46, 22)), (1, (150, 74, 32))])
    metal = mul(metal, cyl.point(lambda v: min(255, v + 40)))
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    img.paste(metal, (x0, 0))
    d = ImageDraw.Draw(img)
    for fy in range(70, h, 150):
        fl = hgrad(w, 9, lambda t: 0.2 + 0.7 * math.sin(math.pi * (0.1 + 0.9 * t)) ** 2 * (1 - 0.5 * t))
        fm = mul(gmap(noise(w, 9, 6, seed + fy, 2), [(0, (60, 30, 18)), (1, (140, 70, 32))]), fl.point(lambda v: min(255, v + 50)))
        img.paste(fm, (0, fy))
        for bx in (2, w - 4):
            d.ellipse([bx, fy + 2, bx + 3, fy + 5], fill=(30, 18, 12, 255))
    # bindweed spiralling up from the foot
    for y in range(h - 1, int(h * 0.35), -2):
        x = w / 2 + (w / 2 - 2) * math.sin(y * 0.09)
        front = math.cos(y * 0.09) > 0
        col = (52, 84, 34, 255) if front else (30, 48, 22, 255)
        d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=col)
        if y % 16 == 0:
            leaf(d, x, y, math.pi + (0.5 if x > w / 2 else -0.5) + rnd.uniform(-0.3, 0.3), 7, (58, 92, 36, 255))
    return img


def rust_plate(seed, paint):
    """an entry: a scrap steel plate, four bolts, a bevelled edge"""
    w, h = PLATE_W, PLATE_H
    img, _ = rust_sheet(w, h, seed, paint=paint, seams=(), rust_amt=0.38, corrugate=0)
    img = mul(img, vgrad(w, h, [(0, 215), (1, 150)]))
    # bevel: lighter top-left edge, dark bottom-right
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=(14, 10, 8))
    d.line([(1, 1), (w - 2, 1)], fill=(150, 130, 110))
    d.line([(1, 1), (1, h - 2)], fill=(120, 104, 90))
    d.line([(2, h - 2), (w - 2, h - 2)], fill=(20, 14, 10))
    for bx, by in [(7, 7), (w - 8, 7), (7, h - 8), (w - 8, h - 8)]:
        rivet(img, bx, by, 2.6, (80, 66, 56), (150, 130, 110), (10, 8, 6))
    # a corner bent and rusted off (bottom-right), cut by alpha
    a = Image.new('L', (w, h), 255)
    ImageDraw.Draw(a).polygon([(w, h - 9), (w, h), (w - 13, h)], fill=0)
    return rgba(img, a)


def rust_lamp(on):
    """the caged lamp at an entry's end: off (dark glass) or on (sodium)"""
    s = 22
    img = Image.new('RGBA', (s, s + 6), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([s / 2 - 3, 0, s / 2 + 3, 5], fill=(40, 30, 24, 255))
    cx, cy, r = s / 2, 6 + 8, 7
    if on:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 196, 110, 255))
        d.ellipse([cx - 3, cy - 4, cx + 2, cy + 1], fill=(255, 244, 214, 255))
    else:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(58, 46, 34, 255))
        d.ellipse([cx - 4, cy - 4, cx - 1, cy - 1], fill=(108, 92, 70, 255))
    for k in range(-2, 3):                                     # the cage
        x = cx + k * 3.4
        d.line([(x, cy - r - 1), (x + k * 0.4, cy + r + 1)], fill=(34, 26, 20, 255), width=1)
    d.arc([cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1], 0, 360, fill=(34, 26, 20, 255))
    d.line([(cx - r, cy), (cx + r, cy)], fill=(34, 26, 20, 255))
    return img


def rust_title():
    """UPPER MORKEZELA stencilled on a rusty sign, overspray and runs, weeds over its corner"""
    w, h = TITLE_W, TITLE_H
    pw, ph, px, py = 470, 112, 25, 14
    plate, _ = rust_sheet(pw, ph, 77, paint=(30, 38, 38), seams=(), rust_amt=0.34, corrugate=0)
    plate = mul(plate, vgrad(pw, ph, [(0, 190), (1, 140)]))
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    # a soft dark shade behind the sign
    sh = Image.new('L', (w, h), 0)
    ImageDraw.Draw(sh).rounded_rectangle([px + 6, py + 10, px + pw + 8, py + ph + 14], 8, fill=200)
    img = Image.alpha_composite(img, glow(sh, (0, 0, 0), 9))
    shape = Image.new('L', (pw, ph), 255)
    sd = ImageDraw.Draw(shape)
    sd.polygon([(pw, ph - 18), (pw, ph), (pw - 26, ph)], fill=0)        # a corner rusted off
    sd.polygon([(0, 0), (14, 0), (0, 10)], fill=0)
    img.paste(rgba(plate, shape), (px, py), shape)
    d = ImageDraw.Draw(img)
    d.rectangle([px, py, px + pw - 1, py + ph - 1], outline=(12, 9, 8, 255))
    for bx, by in [(px + 9, py + 9), (px + pw - 10, py + 9), (px + 9, py + ph - 10), (px + pw - 40, py + ph - 10)]:
        rivet(img, bx, by, 3.2, (84, 70, 58), (150, 130, 110), (10, 8, 6))
    # the stencilled letters: the paint mask, its overspray and a few runs
    f = font('SairaStencilOne.ttf', 70)
    m = text_mask((w, h), (w / 2, py + 64), 'MORKEZELA', f)
    fu = font('SairaStencilOne.ttf', 17)
    mu = text_mask((w, h), (w / 2, py + 20), 'UPPER', fu, spacing=12)
    rnd = random.Random(5)
    runs = Image.new('L', (w, h), 0)
    rd = ImageDraw.Draw(runs)
    bb = m.getbbox()
    for _ in range(11):
        x = rnd.randint(bb[0] + 4, bb[2] - 4)
        col = [m.getpixel((x, y)) for y in range(bb[1], bb[3])]
        if not any(col):
            continue
        yb = bb[1] + max(i for i, v in enumerate(col) if v)
        rd.line([(x, yb), (x, yb + rnd.randint(4, 16))], fill=220, width=2)
        rd.ellipse([x - 1.5, yb + 12, x + 1.5, yb + 16], fill=0)
    paint_m = ImageChops.lighter(m, runs.filter(ImageFilter.GaussianBlur(0.4)))
    wear = threshold(noise(w, h, 5, 8, 3), 70, 30)                     # the paint worn thin in places
    paint_m = ImageChops.multiply(paint_m, wear)
    spray = m.filter(ImageFilter.GaussianBlur(3.5)).point(lambda v: v * 0.35)
    speck = ImageChops.multiply(m.filter(ImageFilter.MaxFilter(9)), threshold(noise(w, h, 2, 9, 1), 215, 4)).point(lambda v: v * 0.6)
    bone = (226, 214, 186)
    img = Image.alpha_composite(img, glow(spray, bone, 0, 1))
    img = Image.alpha_composite(img, glow(speck, bone, 0, 1))
    tex = mul(solid((w, h), bone), curve(noise(w, h, 4, 3, 2), lambda t: 0.82 + 0.2 * t))
    img.paste(tex, (0, 0), paint_m)
    um = mu
    img.paste(SODIUM, (0, 0), um)
    img = Image.alpha_composite(img, glow(mu, SODIUM, 2.5, 0.35))
    # the subtitle stamped on a riveted strip below the sign
    fs = font('SairaCondensed-Bold.ttf', 15)
    stw = 170
    strip, _ = rust_sheet(stw, 22, 31, paint=(26, 24, 24), seams=(), rust_amt=0.3, corrugate=0)
    sx, sy = (w - stw) // 2, py + ph - 4
    img.paste(strip, (sx, sy))
    d = ImageDraw.Draw(img)
    d.rectangle([sx, sy, sx + stw - 1, sy + 21], outline=(10, 8, 8, 255))
    for bx in (sx + 6, sx + stw - 7):
        rivet(img, bx, sy + 11, 2.2, (80, 66, 56), (140, 120, 100), (10, 8, 6))
    d = ImageDraw.Draw(img)
    st = text_mask((w, h), (w / 2, sy + 11), 'A WEIRD GAME', fs, spacing=4)
    img.paste((210, 200, 182), (0, 0), st)
    # weeds and bindweed over the bottom-left corner and up the side
    rnd = random.Random(12)
    over = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    vine(od, rnd, px + 2, py + ph + 4, -1.2, 120, width=2, colour=(40, 62, 28, 255), leaves=(56, 90, 36), leaf_every=7,
         leaf_size=9, curl=0.1)
    vine(od, rnd, px + pw - 2, py + ph + 2, -2.0, 70, width=2, colour=(40, 62, 28, 255), leaves=(60, 94, 38), leaf_every=6,
         leaf_size=8, curl=0.12)
    for x in range(px - 6, px + 60, 7):
        grass(od, rnd, x, py + ph + 10, 3, 24, [(52, 76, 32, 255), (70, 92, 40, 255)])
    img = Image.alpha_composite(img, over)
    return img


def build_rust():
    s = 'rust'
    save(rust_band(BAND_W, H, 101), s, 'band')
    save(rust_band(BAND_WIDE, H, 102), s, 'band_wide')
    save(rust_band(PANEL_W, H, 202, panel=True), s, 'panel')
    save(rust_pipe(H, 303), s, 'rule')
    for i, paint in enumerate([(52, 70, 58), (92, 44, 36), (54, 58, 66), (78, 70, 50), (60, 52, 62)]):
        save(rust_plate(400 + i, paint), s, f'plate{i}')
    save(rust_lamp(False), s, 'lamp_off')
    save(rust_lamp(True), s, 'lamp_on')
    save(rust_title(), s, 'title')


# =====================================================================================================================
# BIOMECH
BONE = [(0, (5, 5, 6)), (0.3, (20, 19, 19)), (0.55, (50, 47, 43)), (0.8, (112, 104, 90)), (1, (200, 190, 164))]
LYMPH = (232, 54, 79)


def tube_profile(u):
    return math.sqrt(max(0.0, 1 - (2 * u - 1) ** 2))


def raise_px(px, x, y, v):
    if v > px[x, y]:
        px[x, y] = min(255, int(v))


def bio_height(w, h, seed, tubes=(), ribs=(), knobs=()):
    """a sculpted height map: a low membrane, vertical ribbed tubes (x, width, rib period, lift), horizontal bony ribs
    (y, thickness, bow) between them, vertebra knobs (x, y, r)"""
    hm = noise(w, h, 22, seed, 4).point(lambda v: round(v * 0.3))
    px = hm.load()
    for (x0, tw, rib, lift) in tubes:
        for x in range(max(0, int(x0)), min(w, int(x0 + tw))):
            prof = tube_profile((x - x0) / tw)
            for y in range(h):
                r = 0.8 + 0.2 * abs(math.sin(math.pi * y / rib)) ** 0.6 if rib else 1.0
                raise_px(px, x, y, lift + 150 * prof * r)
    for (y0, th, bow) in ribs:
        for x in range(w):
            yc = y0 + bow * math.sin(math.pi * x / w)
            for y in range(max(0, int(yc - th)), min(h, int(yc + th) + 1)):
                prof = tube_profile((y - (yc - th)) / (2 * th))
                raise_px(px, x, y, 40 + 120 * prof)
    for (kx, ky, r) in knobs:
        for x in range(max(0, int(kx - r)), min(w, int(kx + r) + 1)):
            for y in range(max(0, int(ky - r)), min(h, int(ky + r) + 1)):
                dd = ((x - kx) ** 2 + ((y - ky) * 1.2) ** 2) / (r * r)
                if dd < 1:
                    raise_px(px, x, y, 90 + 150 * math.sqrt(1 - dd))
    return hm


def bio_colour(hm, k=2.6, gloss=0.55, base=BONE):
    col = gmap(hm, base)
    sh = relief(hm, k, 1.0)
    col = lit(col, sh)
    spec = threshold(sh, 196, 18).point(lambda v: round(v * gloss))
    col.paste((236, 230, 214), (0, 0), spec)
    return col


def hose(px, w, h, pts, r, rib=6, lift=30):
    """a ribbed hose along a polyline: discs stamped along it, ribbed by the distance travelled"""
    dist = 0.0
    for i, (x, y) in enumerate(pts):
        if i:
            dist += math.hypot(x - pts[i - 1][0], y - pts[i - 1][1])
        ribk = 0.78 + 0.22 * abs(math.sin(math.pi * dist / rib)) ** 0.6
        for xx in range(max(0, int(x - r)), min(w, int(x + r) + 1)):
            for yy in range(max(0, int(y - r)), min(h, int(y + r) + 1)):
                dd = ((xx - x) ** 2 + (yy - y) ** 2) / (r * r)
                if dd < 1:
                    raise_px(px, xx, yy, lift + 160 * math.sqrt(1 - dd) * ribk)


def snake(rnd, x, y, ang, n, step=2.0, wobble=0.05):
    pts, turn = [], 0.0
    for _ in range(n):
        turn = turn * 0.9 + (rnd.random() - 0.5) * wobble
        ang += turn
        x += math.cos(ang) * step
        y += math.sin(ang) * step
        pts.append((x, y))
    return pts


def bio_band(w, h, seed, panel=False):
    rnd = random.Random(seed)
    tubes = [(6, 22, 6, 24), (w * 0.6, 14, 5, 12), (w - 40, 24, 7, 30)]
    if w > 260:
        tubes.append((w * 0.35, 12, 5, 8))
    ribs = [(y, 4 + rnd.random() * 2, rnd.uniform(-18, 18)) for y in range(70, h, 112)]
    knobs = [(17, y, 6.5) for y in range(14, h, 21)] + [(w - 28, y, 8) for y in range(30, h, 34)]
    hm = bio_height(w, h, seed, tubes, ribs, knobs)
    px = hm.load()
    for k in range(3 if w < 260 else 5):                     # hoses snaking down across the band
        pts = snake(rnd, rnd.uniform(0.2, 0.8) * w, -10, math.pi / 2 + rnd.uniform(-0.5, 0.5), 340, 2.0, 0.06)
        hose(px, w, h, pts, 5 + rnd.random() * 3, 5, 36)
    img = bio_colour(hm)
    # veins in the recesses: dark, a few of them still red
    over = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    for _ in range(int(w * h / 12000)):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        a = rnd.uniform(0, math.pi * 2)
        pts = [(x, y)]
        for _ in range(40):
            a += rnd.uniform(-0.35, 0.35)
            x += math.cos(a) * 3
            y += math.sin(a) * 3
            pts.append((x, y))
        d.line(pts, fill=(90, 10, 20, 180) if rnd.random() < 0.6 else (20, 4, 6, 200), width=1 + (rnd.random() < 0.3))
    img = Image.alpha_composite(img.convert('RGBA'), over.filter(ImageFilter.GaussianBlur(0.4))).convert('RGB')
    img = mul(img, vgrad(w, h, [(0, 215), (0.55, 190), (1, 80)]))
    return img


def bio_spine(h, seed, w=32):
    """the rule: vertebrae stacked down a glass vein of red lymph"""
    rnd = random.Random(seed)
    hm = Image.new('L', (w, h), 0)
    px = hm.load()
    cx = w / 2 + 2
    for y0 in range(-6, h + 20, 23):
        bw = 10 + rnd.uniform(-0.6, 0.6)
        for x in range(w):
            for y in range(max(0, y0 - 11), min(h, y0 + 12)):
                dx, dy = (x - cx) / bw, (y - y0) / 9
                dd = dx * dx + dy * dy
                if dd < 1:
                    raise_px(px, x, y, 80 + 170 * math.sqrt(1 - dd))
                wing = ((x - cx) / (w / 2)) ** 2 + ((y - y0 + 3) / 3.2) ** 2      # the transverse processes
                if wing < 1:
                    raise_px(px, x, y, 60 + 110 * math.sqrt(1 - wing))
    col = bio_colour(hm, 2.2, 0.6)
    a = hm.point(lambda v: 255 if v > 30 else 0).filter(ImageFilter.GaussianBlur(0.5))
    img = rgba(col, a)
    # the lymph vein on its left
    d = ImageDraw.Draw(img)
    d.rectangle([1, 0, 4, h], fill=(40, 6, 10, 255))
    d.line([(2, 0), (2, h)], fill=(150, 26, 40, 255))
    d.line([(3, 0), (3, h)], fill=(96, 14, 24, 255))
    return img


def bio_pod(seed):
    """an entry: a ribbed pod, its middle a dark recess for the label; + the recess as a glow mask"""
    w, h = PLATE_W, PLATE_H
    hm = Image.new('L', (w, h), 0)
    px = hm.load()
    nz = noise(w, h, 10, seed, 3).load()
    end = 30
    for x in range(w):
        for y in range(h):
            # the pill: round ends
            ex = min(x, w - 1 - x)
            if ex < h / 2:
                dx = (h / 2 - ex) / (h / 2)
                dy = (y - h / 2) / (h / 2)
                if dx * dx + dy * dy > 1:
                    continue
            v = 60 + 150 * tube_profile((y + 0.5) / h)
            if ex < end:                                      # ribbed ends
                v *= 0.78 + 0.22 * abs(math.sin(math.pi * ex / 5)) ** 0.7
            elif 9 <= y <= h - 10:                            # the recess
                v = 40 + nz[x, y] * 0.08
            px[x, y] = max(1, min(255, int(v)))
    a = hm.point(lambda v: 255 if v > 0 else 0)
    col = bio_colour(hm, 2.4, 0.5)
    win = Image.new('L', (w, h), 0)
    ImageDraw.Draw(win).rounded_rectangle([end, 9, w - 1 - end, h - 10], 6, fill=255)
    col = paste_mask(col, mul(col, Image.new('L', (w, h), 120)), win)
    glow_m = win.filter(ImageFilter.GaussianBlur(3))
    return rgba(col, a), Image.merge('RGBA', (Image.new('L', (w, h), 255),) * 3 + (glow_m,))


def bio_title():
    w, h = TITLE_W, TITLE_H
    cw, ch, cx0, cy0 = 480, 108, 20, 10
    hm = Image.new('L', (cw, ch), 0)
    px = hm.load()
    # the cartouche: a ribbed frame round a recess, two tubes plugged into its ends
    for x in range(cw):
        for y in range(ch):
            ex, ey = min(x, cw - 1 - x), min(y, ch - 1 - y)
            e = min(ex / 1.0, ey * 1.0)
            if ex < 40 and ey < 40:
                # the rounded corners
                r = 40 - math.hypot(40 - ex, 40 - ey)
                if r < 0:
                    continue
                e = r
            if e < 12:
                prof = tube_profile(e / 12 * 0.5 + 0.25)
                rib = 0.8 + 0.2 * abs(math.sin(math.pi * (x + y) / 6)) ** 0.6
                px[x, y] = int(70 + 160 * prof * rib)
            else:
                px[x, y] = 28
    hm = ImageChops.lighter(hm, noise(cw, ch, 14, 3, 3).point(lambda v: round(v * 0.18)))
    a = hm.point(lambda v: 255 if v > 0 else 0)
    # knobs on top
    for k in range(-2, 3):
        kx, ky, r = cw / 2 + k * 26, 6, 7 - abs(k)
        for x in range(int(kx - r), int(kx + r) + 1):
            for y in range(0, int(ky + r) + 1):
                dd = ((x - kx) ** 2 + (y - ky) ** 2) / (r * r)
                if dd < 1:
                    raise_px(px, x, y, 120 + 120 * math.sqrt(1 - dd))
    col = bio_colour(hm, 2.6, 0.5)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sh = Image.new('L', (w, h), 0)
    ImageDraw.Draw(sh).rounded_rectangle([cx0 + 4, cy0 + 8, cx0 + cw + 4, cy0 + ch + 12], 30, fill=210)
    img = Image.alpha_composite(img, glow(sh, (0, 0, 0), 10))
    img.paste(col, (cx0, cy0), a)
    # tubes from both sides into the frame
    for side in (0, 1):
        tw, th = 26, 20
        thm = Image.new('L', (tw, th))
        thm.putdata([int(50 + 170 * tube_profile((y + 0.5) / th) * (0.78 + 0.22 * abs(math.sin(math.pi * x / 5)) ** 0.6))
                     for y in range(th) for x in range(tw)])
        tc = bio_colour(thm, 2.4, 0.5)
        img.paste(tc, (0 if side == 0 else w - tw, cy0 + ch // 2 - th // 2))
    # the letters: cast bone-metal in Grenze Gotisch, a red lymph glow behind them
    f = font('GrenzeGotisch.ttf', 66, 700)
    m = text_mask((w, h), (w / 2, cy0 + 62), 'Morkezela', f)
    img = Image.alpha_composite(img, glow(m.filter(ImageFilter.MaxFilter(5)), LYMPH, 8, 1.4))
    lhm = m.filter(ImageFilter.GaussianBlur(1.6))
    lhm = ImageChops.lighter(lhm, m.point(lambda v: v * 0.55))
    lcol = lit(gmap(lhm, [(0, (40, 36, 32)), (0.6, (150, 140, 118)), (1, (226, 216, 188))]), relief(lhm, 3.0, 0.8))
    rim = m.filter(ImageFilter.MaxFilter(3))
    img.paste((14, 10, 10), (0, 0), rim)
    img.paste(lcol, (0, 0), m)
    fu = font('Grenze.ttf', 15, 700)
    mu = text_mask((w, h), (w / 2, cy0 + 22), 'UPPER', fu, spacing=10)
    img.paste((214, 202, 176), (0, 0), mu)
    # the subtitle on a ribbed bar under the cartouche
    fs = font('Grenze.ttf', 13, 700)
    bw, bh = 164, 20
    bhm = Image.new('L', (bw, bh))
    bhm.putdata([int(40 + 130 * tube_profile((y + 0.5) / bh)) for y in range(bh) for x in range(bw)])
    bc = bio_colour(bhm, 2.0, 0.4)
    bc = mul(bc, Image.new('L', (bw, bh), 170))
    bm = Image.new('L', (bw, bh), 0)
    ImageDraw.Draw(bm).rounded_rectangle([0, 0, bw - 1, bh - 1], 9, fill=255)
    sx, sy = (w - bw) // 2, cy0 + ch - 6
    img.paste(bc, (sx, sy), bm)
    st = text_mask((w, h), (w / 2, sy + bh / 2), 'A WEIRD GAME', fs, spacing=4)
    img.paste((222, 196, 176), (0, 0), st)
    return img


def build_biomech():
    s = 'biomech'
    save(bio_band(BAND_W, H, 111), s, 'band')
    save(bio_band(BAND_WIDE, H, 112), s, 'band_wide')
    save(bio_band(PANEL_W, H, 222, panel=True), s, 'panel')
    save(bio_spine(H, 333), s, 'rule')
    for i in range(5):
        pod, g = bio_pod(500 + i)
        save(pod, s, f'plate{i}')
        if i == 0:
            save(g, s, 'plate_glow')
    save(bio_title(), s, 'title')


# =====================================================================================================================
# JUNGLE
CONCRETE = [(0, (26, 28, 27)), (0.5, (56, 58, 55)), (1, (90, 91, 86))]
MINT = (150, 255, 196)
IVY = [(24, 44, 24), (32, 60, 30), (42, 74, 36), (56, 90, 44)]


def crack_path(rnd, x, y, ang, n, step=2.5):
    pts, turn = [(x, y)], 0.0
    for _ in range(n):
        turn = turn * 0.6 + (rnd.random() - 0.5) * 0.9
        ang += turn * 0.5
        x += math.cos(ang) * step
        y += math.sin(ang) * step
        pts.append((x, y))
    return pts


def concrete(w, h, seed, cracks=5, spall=True, moss=0.5, k=1.0):
    """a weathered concrete wall: aggregate, water stains, pitting, cracks (returned: their paths), a spalled patch
    with rusty rebar, moss; k = px per menu px (the store art draws it bigger)"""
    rnd = random.Random(seed)
    K = lambda v: max(1, round(v * k))
    img = gmap(noise(w, h, K(50), seed, 5, 0.55), CONCRETE)
    # aggregate: little light and dark stones
    for t, col in [(232, (110, 108, 100)), (236, (18, 18, 18))]:
        m = threshold(noise(w, h, K(2), seed + t, 1), t, 3)
        img.paste(col, (0, 0), m.point(lambda v: v * 0.6))
    # water stains running down from the top
    st = noise(w, max(2, h // 10), K(5), seed + 3, 3).resize((w, h), Image.BICUBIC)
    st = ImageChops.multiply(st, vgrad(w, h, [(0, 255), (0.7, 140), (1, 60)]))
    img = mul(img, curve(st, lambda t: 1 - 0.45 * max(0, t - 0.35)))
    img = lit(img, relief(noise(w, h, K(5), seed + 4, 3), 0.9, 0.7 * k))
    d = ImageDraw.Draw(img)
    paths = []
    for _ in range(cracks):
        pts = crack_path(rnd, rnd.uniform(0, w), rnd.uniform(-10 * k, h * 0.6), math.pi / 2 + rnd.uniform(-0.8, 0.8), rnd.randint(40, 110), 2.5 * k)
        d.line([(x + k, y + k) for x, y in pts], fill=(98, 98, 92), width=K(1))
        d.line(pts, fill=(8, 8, 8), width=K(2))
        paths.append(pts)
        if rnd.random() < 0.6:                              # a branch
            j = rnd.randrange(len(pts))
            br = crack_path(rnd, *pts[j], rnd.uniform(0, math.pi), rnd.randint(10, 40), 2.5 * k)
            d.line(br, fill=(10, 10, 10), width=K(1))
            paths.append(br)
    if spall:
        sx, sy, sw, sh = rnd.uniform(0.15, 0.5) * w, rnd.uniform(0.35, 0.6) * h, rnd.uniform(50, 80), rnd.uniform(26, 40)
        m = Image.new('L', (w, h), 0)
        pts = [(sx + sw / 2 + math.cos(a) * sw / 2 * rnd.uniform(0.7, 1.1), sy + sh / 2 + math.sin(a) * sh / 2 * rnd.uniform(0.6, 1.1))
               for a in [i * math.pi / 8 for i in range(16)]]
        ImageDraw.Draw(m).polygon(pts, fill=255)
        img.paste(mul(img, Image.new('L', (w, h), 120)), (0, 0), m)
        d = ImageDraw.Draw(img)
        for ry in (sy + sh * 0.35, sy + sh * 0.7):          # rebar
            d.line([(sx + 2, ry + 2), (sx + sw - 2, ry + 2)], fill=(10, 8, 6), width=3)
            d.line([(sx, ry), (sx + sw, ry)], fill=(96, 48, 26), width=3)
            for rx in range(int(sx), int(sx + sw), 4):
                d.point((rx, ry - 1), fill=(140, 70, 36))
        edge = ImageChops.subtract(m.filter(ImageFilter.MaxFilter(3)), m)
        img.paste((104, 104, 98), (0, 0), ImageChops.offset(edge, 0, 1))
    # moss: patches toward the foot and along the cracks
    mm = noise(w, h, K(30), seed + 7, 4)
    cr = Image.new('L', (w, h), 0)
    cd = ImageDraw.Draw(cr)
    for pts in paths:
        cd.line(pts, fill=150, width=K(7))
    cr = cr.filter(ImageFilter.GaussianBlur(4 * k))
    mm = ImageChops.add(ImageChops.add(mm, vgrad(w, h, [(0, 0), (0.6, 30), (1, 120)])), cr)
    mmask = threshold(mm, round(255 * (1 - moss * 0.6)), 24)
    mcol = gmap(noise(w, h, K(3), seed + 8, 3), [(0, (22, 36, 16)), (0.6, (48, 72, 30)), (1, (78, 100, 44))])
    img = paste_mask(img, mcol, mmask)
    return img, paths


def ivy_leaf(d, x, y, s, ang, col, k=1.0):
    """an ivy leaf: three pointed lobes"""
    ca, sa = math.cos(ang), math.sin(ang)
    P = lambda u, v: (x + (u * ca - v * sa) * s, y + (u * sa + v * ca) * s)
    d.polygon([P(0, 0), P(0.35, -0.55), P(0.55, -0.35), P(1.0, 0), P(0.55, 0.35), P(0.35, 0.55)], fill=col)
    if s >= 12:                                   # big enough to show it: one half lit, the veins paler
        lite = tuple(min(255, c + 22) for c in col[:3]) + (255,)
        d.polygon([P(0, 0), P(0.35, -0.55), P(0.55, -0.35), P(1.0, 0)], fill=lite)
        vein = tuple(min(255, c + 40) for c in col[:3]) + (255,)
        for vx, vy in ((0.55, -0.35), (0.55, 0.35)):
            d.line([P(0.2, 0), P(vx, vy)], fill=vein, width=max(1, round(k * 0.7)))
    d.line([P(0, 0), P(0.85, 0)], fill=tuple(max(0, c - 14) for c in col[:3]) + (255,), width=max(1, round(k)))


def ivy_curtain(over, rnd, w, top, n, depth, x_range=None, k=1.0):
    """ivy hanging down from the top edge"""
    d = ImageDraw.Draw(over)
    for _ in range(n):
        x = rnd.uniform(*(x_range or (0, w)))
        pts = snake(rnd, x, top - 4 * k, math.pi / 2 + rnd.uniform(-0.25, 0.25), int(rnd.uniform(0.3, 1) * depth / 2), 2.0 * k, 0.08)
        d.line(pts, fill=(34, 40, 22, 255), width=max(1, round(k)))
        for i in range(0, len(pts), 3):
            px_, py_ = pts[i]
            col = IVY[rnd.randrange(len(IVY))] + (255,)
            ivy_leaf(d, px_ + rnd.uniform(-2, 2) * k, py_, rnd.uniform(6, 10) * k, rnd.uniform(0, math.pi * 2), col, k)


def fern(d, rnd, x, y, length, ang, col):
    pts = []
    for i in range(int(length / 2)):
        t = i / (length / 2)
        a = ang + 0.9 * t * t
        x += math.cos(a) * 2
        y += math.sin(a) * 2
        pts.append((x, y, a, t))
    d.line([(p[0], p[1]) for p in pts], fill=col, width=1)
    for i, (px_, py_, a, t) in enumerate(pts):
        if i % 2:
            continue
        L = 9 * math.sin(math.pi * min(1, t * 1.1 + 0.05)) + 1
        for side in (-1, 1):
            b = a + side * 1.2
            d.line([(px_, py_), (px_ + math.cos(b) * L, py_ + math.sin(b) * L)], fill=col, width=2)


def mycelium(w, h, rnd, starts, n=60, k=1.0):
    """glowing threads creeping from points (cracks): an L mask"""
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)

    def thread(x, y, a, length, depth):
        pts = [(x, y)]
        turn = 0.0
        for _ in range(int(length / 2)):
            turn = turn * 0.8 + (rnd.random() - 0.5) * 0.3
            a += turn
            x += math.cos(a) * 2 * k
            y += math.sin(a) * 2 * k
            pts.append((x, y))
            if depth < 2 and rnd.random() < 0.04:
                thread(x, y, a + rnd.choice((-0.8, 0.8)), length * 0.5, depth + 1)
        d.line(pts, fill=255, width=max(1, round(k)))
        d.ellipse([x - k, y - k, x + k, y + k], fill=255)

    for _ in range(n):
        x, y = rnd.choice(starts)
        thread(x, y, rnd.uniform(0, math.pi * 2), rnd.uniform(14, 50), 0)
    return m


def colonies(w, h, rnd, centres, k=1.0, size=(8, 20)):
    """mycelium as mould colonies: soft cottony patches, each many faint curling hyphae spreading from its middle,
    summed so they build up into fuzz (dense in the middle, wispy at the rim): an L mask. Reads as something
    growing, not as a spark or a bolt."""
    m = Image.new('L', (w, h), 0)
    for cx, cy, *_ in centres:
        R = rnd.uniform(*size) * k
        t = Image.new('L', (w, h), 0)
        d = ImageDraw.Draw(t)
        for _ in range(int(R / k * 2.2)):
            a = rnd.uniform(0, 2 * math.pi)
            r0 = rnd.uniform(0, R * 0.3)
            x, y = cx + math.cos(a) * r0, cy + math.sin(a) * r0
            turn, v = 0.0, rnd.randint(40, 85)
            steps = int(rnd.uniform(0.5, 1.0) * R / (1.2 * k))
            for i in range(steps):
                turn = turn * 0.75 + (rnd.random() - 0.5) * 0.8
                a += turn * 0.5
                nx, ny = x + math.cos(a) * 1.2 * k, y + math.sin(a) * 1.2 * k
                d.line([(x, y), (nx, ny)], fill=round(v * (1 - i / steps) ** 0.6), width=max(1, round(0.7 * k)))
                x, y = nx, ny
        core = Image.new('L', (w, h), 0)                    # the felted middle
        ImageDraw.Draw(core).ellipse([cx - R * 0.35, cy - R * 0.3, cx + R * 0.35, cy + R * 0.3], fill=70)
        m = ImageChops.add(m, ImageChops.add(t, core.filter(ImageFilter.GaussianBlur(R * 0.25))))
    return m


def along_cracks(paths, dx=0, dy=0, every=2):
    """points along the cracks (x, y, the crack's direction there): where colonies() can take hold"""
    out = []
    for pts in paths:
        for i in range(0, len(pts) - 1, every):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            out.append((x0 + dx, y0 + dy, math.atan2(y1 - y0, x1 - x0)))
    return out


def panel_edges(w, h, side=20, foot=64, fade=26):
    """an L mask: the panel's left and right edges and its foot (the rows of text keep clear of the glow)"""
    c = lambda v: max(0.0, min(1.0, v))
    sides = hgrad(w, h, lambda t: max(c((side + fade - t * w) / fade), c((t * w - (w - side - fade)) / fade)))
    return ImageChops.lighter(sides, vgrad(w, h, [(0, 0), ((h - foot - fade) / h, 0), ((h - foot) / h, 255), (1, 255)]))


def jungle_band(w, h, seed, panel=False):
    rnd = random.Random(seed)
    img, paths = concrete(w, h, seed, cracks=6 if not panel else 8, moss=0.4)
    img = mul(img, vgrad(w, h, [(0, 190), (0.5, 175), (1, 80)]))
    starts = [p for pts in paths for p in pts[::4]]
    if panel:                                                 # tufts along the edges and the foot only
        edges = panel_edges(w, h)
        seeds = [(rnd.uniform(0, 12), rnd.uniform(20, h)) for _ in range(9)] + [(w - rnd.uniform(0, 12), rnd.uniform(20, h)) for _ in range(9)]
        seeds += [(rnd.uniform(0, w), h - rnd.uniform(0, 40)) for _ in range(10)]
        myc = ImageChops.multiply(colonies(w, h, rnd, seeds, size=(7, 15)), edges)
    else:
        myc = mycelium(w, h, rnd, starts, 70)
    over = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ivy_curtain(over, rnd, w, 0, 26 if not panel else 40, 260)
    d = ImageDraw.Draw(over)
    for x in range(-10, w + 10, 16):                          # ferns and grass at the foot
        fern(d, rnd, x + rnd.uniform(-4, 4), h + 2, rnd.uniform(40, 80), -math.pi / 2 + rnd.uniform(-0.9, 0.3),
             (40 + rnd.randint(-8, 8), 70 + rnd.randint(-10, 10), 34, 255))
        grass(d, rnd, x, h, 2, 22, [(46, 70, 30, 255), (60, 86, 36, 255)])
    # the threads dimly in the band itself (JS lays the same mask on top, glowing, breathing)
    img = Image.alpha_composite(img.convert('RGBA'), glow(myc, MINT, 2.0, 0.8))
    img.paste(MINT, (0, 0), myc.point(lambda v: v * 0.3))
    img = Image.alpha_composite(img, over.filter(ImageFilter.GaussianBlur(0.3)))
    return img.convert('RGB'), myc


def jungle_pipe(h, seed, w=20):
    """the rule: a verdigris drainpipe, its joints, ivy on it"""
    rnd = random.Random(seed)
    core = 12
    x0 = (w - core) // 2
    cyl = hgrad(core, h, lambda t: 0.2 + 0.75 * math.sin(math.pi * (0.1 + 0.9 * t)) ** 2 * (1 - 0.5 * t))
    metal = gmap(noise(core, h, 16, seed, 4), [(0, (24, 46, 40)), (0.5, (58, 104, 88)), (1, (110, 156, 128))])
    metal = mul(metal, cyl.point(lambda v: min(255, v + 40)))
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    img.paste(metal, (x0, 0))
    d = ImageDraw.Draw(img)
    for jy in range(40, h, 120):
        jm = mul(gmap(noise(w - 4, 8, 5, seed + jy, 2), [(0, (30, 56, 48)), (1, (110, 150, 120))]),
                 hgrad(w - 4, 8, lambda t: 0.3 + 0.7 * math.sin(math.pi * (0.1 + 0.9 * t)) ** 2))
        img.paste(jm, (2, jy))
        d.line([(2, jy + 8), (w - 3, jy + 8)], fill=(8, 14, 12, 255))
    for y in range(0, int(h * 0.55), 3):                     # ivy down from the top
        x = w / 2 + (w / 2 - 3) * math.sin(y * 0.05 + 1)
        if rnd.random() < 0.55:
            ivy_leaf(d, x, y, rnd.uniform(6, 9), rnd.uniform(0, math.pi * 2), IVY[rnd.randrange(len(IVY))] + (255,))
    return img


def jungle_slab(seed):
    """an entry: a cracked concrete slab, its corners chipped, moss on its top; + its mycelium as a glow mask"""
    w, h = PLATE_W, PLATE_H
    rnd = random.Random(seed)
    img, paths = concrete(w, h, seed, cracks=2, spall=False, moss=0.25)
    img = lit(img, vgrad(w, h, [(0, 190), (1, 120)]))
    d = ImageDraw.Draw(img)
    d.line([(0, 0), (w - 1, 0)], fill=(116, 116, 108))
    d.line([(0, h - 1), (w - 1, h - 1)], fill=(12, 12, 12))
    a = Image.new('L', (w, h), 255)
    ad = ImageDraw.Draw(a)
    for cx, cy in [(0, 0), (w, 0), (0, h), (w, h)]:           # chipped corners
        r = rnd.uniform(3, 8)
        ad.polygon([(cx, cy), (cx + (r if cx == 0 else -r), cy), (cx, cy + (r if cy == 0 else -r))], fill=0)
    # moss along the top edge
    mt = threshold(noise(w, 10, 6, seed + 1, 3), 120, 30)
    mt = ImageChops.multiply(mt, vgrad(w, 10, [(0, 255), (1, 0)]))
    img.paste((54, 80, 34), (0, 0), mt)
    starts = [p for pts in paths for p in pts[::3]] or [(w / 2, h / 2)]
    myc = mycelium(w, h, rnd, starts + [(rnd.uniform(0, w), rnd.uniform(0, h)) for _ in range(6)], 22)
    return rgba(img, a), Image.merge('RGBA', (Image.new('L', (w, h), 255),) * 3 + (ImageChops.multiply(myc, a),))


def jungle_ivy_end(seed, w=84, h=PLATE_H + 18):
    """ivy grown over the left end of an entry's slab (a disabled entry: nobody has been this way); mirror it for the
    right end. The slab sits centred in it, 9 px of room above and below for the leaves that spill over."""
    rnd = random.Random(seed)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(7):                                        # stems creeping in from the end, thinning out
        y0 = rnd.uniform(6, h - 6)
        pts = snake(rnd, rnd.uniform(-4, 4), y0, rnd.uniform(-0.5, 0.5), rnd.randint(14, 34), 2.0, 0.14)
        d.line(pts, fill=(30, 36, 20, 255), width=1)
        for i, (x, y) in enumerate(pts):
            if i % 2 == 0 and rnd.random() < 1.1 - x / w:       # dense at the end, sparse further in
                ivy_leaf(d, x + rnd.uniform(-2, 2), y + rnd.uniform(-2, 2), rnd.uniform(6, 10), rnd.uniform(0, math.pi * 2),
                         IVY[rnd.randrange(len(IVY))] + (255,))
    sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))                # a soft shadow under the leaves, on the slab
    sh.putalpha(img.getchannel('A').filter(ImageFilter.GaussianBlur(2)).point(lambda v: v * 0.6))
    return Image.alpha_composite(ImageChops.offset(sh, 1, 2), img)


def jungle_title(k=1.0, subtitle='A WEIRD GAME', demo=False, live=False):
    """MORKEZELA as old shop-sign letters (Bungee) painted on a broken concrete lintel, peeling; UPPER glowing mint;
    mycelium in fuzzy tufts along the cracks, ivy over the top; the subtitle stencilled on its foot. k = px per menu
    px (the menu draws it at 1, the store art bigger); demo: a small concrete plate with DEMO hanging under it.
    live (the menu): the mycelium baked in dimly, returned as a mask too (img, myc) for the menu to make it breathe."""
    K = lambda v: max(1, round(v * k))
    below = 46 if demo else 0
    w, h = round(TITLE_W * k), round((TITLE_H + below) * k)
    lw, lh, lx, ly = K(470), K(104), K(25), K(20)
    rnd = random.Random(21)
    slab, paths = concrete(lw, lh, 61, cracks=4, spall=False, moss=0.4, k=k)
    slab = mul(slab, vgrad(lw, lh, [(0, 175), (1, 120)]))
    a = Image.new('L', (lw, lh), 255)
    ad = ImageDraw.Draw(a)
    ad.polygon([(lw, lh - 30 * k), (lw, lh), (lw - 40 * k, lh)], fill=0)    # a broken corner, rebar out of it
    ad.polygon([(0, 0), (22 * k, 0), (0, 14 * k)], fill=0)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sh = Image.new('L', (w, h), 0)
    ImageDraw.Draw(sh).rectangle([lx + 6 * k, ly + 10 * k, lx + lw + 6 * k, ly + lh + 12 * k], fill=200)
    img = Image.alpha_composite(img, glow(sh, (0, 0, 0), 10 * k))
    img.paste(slab, (lx, ly), a)
    d = ImageDraw.Draw(img)
    for j in range(2):
        d.line([(lx + lw - (30 - j * 10) * k, ly + lh - 6 * k), (lx + lw - (8 - j * 14) * k, ly + lh + 10 * k)], fill=(96, 48, 26, 255), width=K(3))
    # the letters: old sign paint, peeling
    f = font('Bungee.ttf', K(58))
    m = text_mask((w, h), (w / 2, ly + 62 * k), 'MORKEZELA', f)
    peel = threshold(noise(w, h, K(7), 23, 4), 64, 20)
    paint_m = ImageChops.multiply(m, peel)
    img.paste((12, 14, 12), (0, 0), ImageChops.offset(m, K(2), K(3)).point(lambda v: v * 0.6))
    img.paste((70, 72, 66), (0, 0), m)                                     # where the paint is gone: the bare concrete
    tex = mul(solid((w, h), (222, 214, 186)), curve(noise(w, h, K(3), 5, 2), lambda t: 0.84 + 0.18 * t))
    img.paste(tex, (0, 0), paint_m)
    fu = font('Rubik.ttf', K(15), 700)
    mu = text_mask((w, h), (w / 2, ly + 22 * k), 'UPPER', fu, spacing=11 * k)
    img.paste(MINT, (0, 0), mu)
    img = Image.alpha_composite(img, glow(mu, MINT, 3 * k, 0.5))
    # mycelium in fuzzy tufts along the lintel's cracks, faint over the letters
    seeds = along_cracks(paths, lx, ly, 3)
    myc = colonies(w, h, rnd, [seeds[rnd.randrange(len(seeds))] for _ in range(16)], k)
    on_slab = Image.new('L', (w, h), 0)                                     # (the threads stay on the concrete)
    on_slab.paste(a, (lx, ly))
    myc = ImageChops.multiply(myc, on_slab.filter(ImageFilter.MinFilter(2 * K(2) + 1)))
    myc = ImageChops.multiply(myc, ImageChops.invert(m.filter(ImageFilter.MaxFilter(2 * K(2) + 1)).point(lambda v: v * 0.75)))
    img = Image.alpha_composite(img, glow(myc, MINT, 5 * k, 0.9 if live else 1.4))    # a soft bloom round the mat
    img = Image.alpha_composite(img, glow(myc, MINT, 1.5 * k, 0.5 if live else 0.8))
    img.paste((180, 250, 210), (0, 0), myc.point(lambda v: v * (0.25 if live else 0.45)))
    # ivy over the top edge, hanging over the letters at the left and right
    over = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ivy_curtain(over, rnd, w, ly + 2 * k, 7, 70, (lx, lx + 90 * k), k)
    ivy_curtain(over, rnd, w, ly + 2 * k, 6, 60, (lx + lw - 110 * k, lx + lw), k)
    od = ImageDraw.Draw(over)
    for x in range(lx, lx + lw, K(5)):                                      # a fringe of leaves along the top
        if rnd.random() < 0.7:
            ivy_leaf(od, x, ly + rnd.uniform(-4, 3) * k, rnd.uniform(6, 10) * k, rnd.uniform(0, math.pi * 2), IVY[rnd.randrange(4)] + (255,), k)
    img = Image.alpha_composite(img, over)
    # the subtitle stencilled on the slab's foot
    if subtitle:
        fs = font('Rubik.ttf', K(12), 700)
        st = text_mask((w, h), (w / 2, ly + lh - 12 * k), subtitle, fs, spacing=5 * k)
        img.paste((190, 196, 184), (0, 0), st)
    if demo:
        # a small concrete plate hanging on two rusty wires, DEMO glowing mint on it
        pw, ph = K(124), K(36)
        px, py = (w - pw) // 2, ly + lh + K(14)
        plate, _ = concrete(pw, ph, 63, cracks=1, spall=False, moss=0.3, k=k)
        plate = mul(plate, vgrad(pw, ph, [(0, 170), (1, 120)]))
        d = ImageDraw.Draw(img)
        for xx in (px + pw * 0.25, px + pw * 0.75):
            d.line([(xx, ly + lh - 4 * k), (xx, py)], fill=(96, 48, 26, 255), width=K(2))
        sh2 = Image.new('L', (w, h), 0)
        ImageDraw.Draw(sh2).rectangle([px + 3 * k, py + 4 * k, px + pw + 3 * k, py + ph + 4 * k], fill=200)
        img = Image.alpha_composite(img, glow(sh2, (0, 0, 0), 4 * k))
        img.paste(plate, (px, py))
        dm = text_mask((w, h), (w / 2, py + ph / 2 + 1 * k), 'DEMO', font('Bungee.ttf', K(22)), spacing=3 * k)
        img = Image.alpha_composite(img, glow(dm, MINT, 4 * k, 0.9))
        img.paste((210, 255, 228), (0, 0), dm)
    return (img, myc) if live else img


def build_jungle():
    s = 'jungle'
    for name, wd, seed in [('band', BAND_W, 121), ('band_wide', BAND_WIDE, 122), ('panel', PANEL_W, 232)]:
        band, myc = jungle_band(wd, H, seed, panel=name == 'panel')
        save(band, s, name)
        save(Image.merge('RGBA', (Image.new('L', myc.size, 255),) * 3 + (myc,)), s, name + '_myc')
    save(jungle_pipe(H, 343), s, 'rule')
    for i in range(5):
        slab, g = jungle_slab(600 + i)
        save(slab, s, f'plate{i}')
        save(g, s, f'plate{i}_glow')
    save(jungle_ivy_end(701), s, 'ivy_l')
    save(jungle_ivy_end(702).transpose(Image.FLIP_LEFT_RIGHT), s, 'ivy_r')
    title, myc = jungle_title(live=True)
    save(title, s, 'title')
    save(Image.merge('RGBA', (Image.new('L', myc.size, 255),) * 3 + (myc,)), s, 'title_myc')


# =====================================================================================================================
# CRAZY
FLESH = [(0, (20, 4, 16)), (0.4, (70, 18, 48)), (0.75, (150, 52, 92)), (1, (230, 140, 170))]
HOTPINK, ACIDG, CYANC = (255, 63, 164), (200, 255, 0), (80, 240, 255)


def cells(w, h, seed, size=34):
    """F2 - F1 cellular noise (L): bright cell middles, dark seams"""
    rnd = random.Random(seed)
    gw, gh = w // size + 3, h // size + 3
    pts = {(i, j): ((i + rnd.random()) * size, (j + rnd.random()) * size) for i in range(-1, gw) for j in range(-1, gh)}
    img = Image.new('L', (w, h))
    out = []
    for y in range(h):
        j0 = y // size
        for x in range(w):
            i0 = x // size
            f1 = f2 = 1e9
            for i in (i0 - 1, i0, i0 + 1):
                for j in (j0 - 1, j0, j0 + 1):
                    px_, py_ = pts[(i, j)]
                    dd = (px_ - x) ** 2 + (py_ - y) ** 2
                    if dd < f1:
                        f1, f2 = dd, f1
                    elif dd < f2:
                        f2 = dd
            out.append(min(255, int((math.sqrt(f2) - math.sqrt(f1)) * 255 / (size * 0.7))))
    img.putdata(out)
    return img


def suture_patch(img, rnd, x, y, pw, ph, seed):
    """a rusty plate stitched onto the flesh with wire"""
    plate, _ = rust_sheet(pw, ph, seed, paint=(96, 84, 96), rust_amt=0.5, corrugate=0)
    plate = mul(plate, Image.new('L', plate.size, 230))
    m = Image.new('L', (pw, ph), 0)
    pts = [(pw / 2 + math.cos(a) * pw / 2 * rnd.uniform(0.8, 1.0), ph / 2 + math.sin(a) * ph / 2 * rnd.uniform(0.8, 1.0))
           for a in [i * math.pi / 6 for i in range(12)]]
    ImageDraw.Draw(m).polygon(pts, fill=255)
    img.paste(plate, (int(x), int(y)), m)
    d = ImageDraw.Draw(img)
    for i, (px_, py_) in enumerate(pts):
        cx, cy = x + px_, y + py_
        nx, ny = (px_ - pw / 2), (py_ - ph / 2)
        L = math.hypot(nx, ny) or 1
        nx, ny = nx / L * 3.5, ny / L * 3.5
        tx, ty = -ny, nx
        d.line([(cx - nx + tx * 0.5, cy - ny + ty * 0.5), (cx + nx - tx * 0.5, cy + ny - ty * 0.5)], fill=(18, 16, 20), width=2)
        d.line([(cx - nx - tx * 0.5, cy - ny - ty * 0.5), (cx + nx + tx * 0.5, cy + ny + ty * 0.5)], fill=(150, 146, 140), width=1)
    rivet(img, x + pw / 2, y + ph / 2, 3, (90, 80, 76), (170, 160, 150), (10, 8, 8))


def crazy_band(w, h, seed, panel=False):
    rnd = random.Random(seed)
    hm = cells(w, h, seed, 44).filter(ImageFilter.GaussianBlur(2))
    hm = ImageChops.lighter(hm.point(lambda v: round(v * 0.85)), noise(w, h, 8, seed, 3).point(lambda v: round(v * 0.3)))
    col = gmap(hm, FLESH)
    sh = relief(hm, 1.5, 1.6)
    col = lit(col, sh)
    col.paste((255, 214, 226), (0, 0), threshold(sh, 200, 16).point(lambda v: v * 0.45))        # wet
    # veins
    over = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    for _ in range(int(w * h / 5000)):
        pts = snake(rnd, rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(0, 6.3), 60, 2.5, 0.45)
        d.line(pts, fill=(190, 24, 64, 170) if rnd.random() < 0.6 else (70, 150, 220, 120), width=1 + (rnd.random() < 0.4))
    col = Image.alpha_composite(col.convert('RGBA'), over.filter(ImageFilter.GaussianBlur(0.5))).convert('RGB')
    # rusty patches stitched on
    for k in range(2 if not panel else 3):
        pw, ph = rnd.randint(58, 80), rnd.randint(38, 56)
        suture_patch(col, rnd, rnd.uniform(4, w - pw - 30), rnd.uniform(40 + k * 220, 160 + k * 220), pw, ph, seed + k)
    col = mul(col, vgrad(w, h, [(0, 170), (0.6, 150), (1, 80)]))
    # eye sockets: dark puckered rims where JS puts the eyes
    eyes = []
    for _ in range(4 if not panel else 6):
        for _ in range(50):
            ex, ey, r = rnd.uniform(18, w - 40), rnd.uniform(20, h - 60), rnd.uniform(7, 13)
            if all(math.hypot(ex - a, ey - b) > r + c + 26 for a, b, c in eyes) and not (100 < ey < 360 and ex < w - 40 and w < 400 and rnd.random() < 0.8):
                eyes.append((ex, ey, r))
                break
    m = Image.new('L', (w, h), 0)
    md = ImageDraw.Draw(m)
    for ex, ey, r in eyes:
        md.ellipse([ex - r * 1.6, ey - r * 1.25, ex + r * 1.6, ey + r * 1.25], fill=255)
    col = paste_mask(col, mul(col, Image.new('L', (w, h), 60)), m.filter(ImageFilter.GaussianBlur(3)))
    return col, [dict(x=round(x, 1), y=round(y, 1), r=round(r, 1)) for x, y, r in eyes]


def crazy_teeth(h, seed, w=30):
    """the rule: a gum down the band's edge, uneven teeth biting into the painting (a gold one, a steel one)"""
    rnd = random.Random(seed)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    gum = mul(gmap(noise(12, h, 6, seed, 3), [(0, (90, 16, 40)), (1, (170, 50, 80))]),
              hgrad(12, h, lambda t: 0.5 + 0.5 * math.sin(math.pi * t)))
    img.paste(gum, (0, 0))
    d = ImageDraw.Draw(img)
    y = 2
    while y < h:
        th = rnd.uniform(10, 16)
        L = rnd.uniform(9, w - 11)
        kind = rnd.random()
        fill = (226, 214, 180) if kind < 0.86 else (232, 184, 70) if kind < 0.93 else (176, 184, 192)
        shade = tuple(max(0, c - 70) for c in fill)
        d.polygon([(9, y), (10 + L, y + th * 0.55), (9, y + th)], fill=shade + (255,))
        d.polygon([(9, y + 1), (8 + L, y + th * 0.5), (9, y + th * 0.75)], fill=fill + (255,))
        d.line([(10, y + 2), (6 + L * 0.7, y + th * 0.42)], fill=(255, 250, 236, 255))
        y += th + rnd.uniform(-1, 2)
    d.line([(10, 0), (10, h)], fill=(120, 24, 52, 255), width=2)
    return img


def crazy_eye(r=20):
    """an eyeball (sclera, red veins) and its iris (acid green, a gear for a pupil): two sprites"""
    s = r * 2 + 4
    ball = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    m = Image.new('L', (s, s), 0)
    ImageDraw.Draw(m).ellipse([2, 2, s - 2, s - 2], fill=255)
    sc = hgrad(s, s, lambda t: 1).convert('RGB')
    shade = Image.radial_gradient('L').resize((s, s)).point(lambda v: 255 - round(v * 0.55))
    sc = mul(solid((s, s), (236, 228, 214)), ImageChops.offset(shade, -3, -3))
    bd = ImageDraw.Draw(sc)
    rnd = random.Random(4)
    for _ in range(9):
        a = rnd.uniform(0, 6.3)
        pts = snake(rnd, s / 2 + math.cos(a) * r, s / 2 + math.sin(a) * r, a + math.pi, 7, 1.6, 0.8)
        bd.line(pts, fill=(196, 60, 70), width=1)
    ball.paste(sc, (0, 0), m)
    ir = round(r * 0.55)
    si = ir * 2 + 2
    iris = Image.new('RGBA', (si, si), (0, 0, 0, 0))
    idr = ImageDraw.Draw(iris)
    idr.ellipse([1, 1, si - 1, si - 1], fill=(40, 70, 10, 255))
    idr.ellipse([2, 2, si - 2, si - 2], fill=ACIDG + (255,))
    for k in range(18):
        a = k * math.pi / 9
        idr.line([(si / 2 + math.cos(a) * ir * 0.45, si / 2 + math.sin(a) * ir * 0.45), (si / 2 + math.cos(a) * ir * 0.95, si / 2 + math.sin(a) * ir * 0.95)],
                 fill=(120, 170, 0, 255))
    pr = ir * 0.48
    pts = []
    for k in range(16):                                            # the pupil: a little gear
        a = k * math.pi / 8
        rr = pr if k % 2 == 0 else pr * 0.72
        pts.append((si / 2 + math.cos(a) * rr, si / 2 + math.sin(a) * rr))
    idr.polygon(pts, fill=(8, 4, 8, 255))
    idr.ellipse([si / 2 - ir * 0.55, si / 2 - ir * 0.6, si / 2 - ir * 0.2, si / 2 - ir * 0.25], fill=(255, 255, 255, 230))
    return ball, iris


def crazy_tag(seed, colour):
    """an entry: a torn cardboard tag, a hole at the top for its string"""
    w, h = PLATE_W, PLATE_H
    rnd = random.Random(seed)
    img = mul(solid((w, h), colour), curve(noise(w, h, 4, seed, 3), lambda t: 0.8 + 0.25 * t))
    img = lit(img, relief(noise(w, h, 3, seed + 1, 2), 0.6, 0.6))
    a = Image.new('L', (w, h), 0)
    pts = [(x, rnd.uniform(0, 3)) for x in range(0, w + 1, 6)] + [(w - rnd.uniform(0, 3), y) for y in range(0, h + 1, 6)] + \
          [(x, h - rnd.uniform(0, 3)) for x in range(w, -1, -6)] + [(rnd.uniform(0, 3), y) for y in range(h, -1, -6)]
    ImageDraw.Draw(a).polygon(pts, fill=255)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=tuple(max(0, c - 70) for c in colour))
    return rgba(img, a)


RANSOM = [  # (letter, font, size, scrap colour, ink colour, rotation)
    ('M', 'BebasNeue.ttf', 74, (230, 255, 40), (10, 10, 10), -6),
    ('O', None, 0, None, None, 0),
    ('R', 'UnifrakturMaguntia.ttf', 64, (30, 22, 40), (255, 90, 180), 5),
    ('K', 'SairaStencilOne.ttf', 62, (150, 70, 34), (236, 226, 200), -3),
    ('E', 'Monoton.ttf', 52, (14, 10, 34), (90, 240, 255), 7),
    ('Z', 'RubikBeastly.ttf', 64, (240, 230, 214), (190, 20, 70), -8),
    ('E', 'GrenzeGotisch.ttf', 66, (60, 120, 70), (240, 236, 210), 4),
    ('L', 'BungeeShade.ttf', 58, (255, 100, 170), (20, 10, 20), -4),
    ('A', 'RubikMicrobe.ttf', 64, (20, 20, 20), (200, 255, 0), 6),
]


def ransom_letter(ch, fname, px, scrap, ink, rot, seed, wght=None):
    f = font(fname, px, wght)
    probe = ImageDraw.Draw(Image.new('L', (4, 4)))
    bb = probe.textbbox((0, 0), ch, font=f, anchor='mm')
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pw, ph = tw + 22, th + 20
    rnd = random.Random(seed)
    img = Image.new('RGBA', (pw + 20, ph + 20), (0, 0, 0, 0))
    a = Image.new('L', img.size, 0)
    pts = [(10 + x, 10 + rnd.uniform(-2, 3)) for x in range(0, pw + 1, 5)] + [(10 + pw + rnd.uniform(-3, 2), 10 + y) for y in range(0, ph + 1, 5)] + \
          [(10 + x, 10 + ph + rnd.uniform(-3, 2)) for x in range(pw, -1, -5)] + [(10 + rnd.uniform(-2, 3), 10 + y) for y in range(ph, -1, -5)]
    ImageDraw.Draw(a).polygon(pts, fill=255)
    paper = mul(solid(img.size, scrap), curve(noise(img.width, img.height, 3, seed, 2), lambda t: 0.82 + 0.24 * t))
    sh = Image.new('L', img.size, 0)
    sh.paste(a.point(lambda v: v * 0.7), (3, 4))
    img = Image.alpha_composite(img, glow(sh, (0, 0, 0), 2))
    img.paste(paper, (0, 0), a)
    d = ImageDraw.Draw(img)
    d.text((img.width / 2, img.height / 2), ch, font=f, fill=ink + (255,), anchor='mm')
    return img.rotate(rot, Image.BICUBIC, expand=True)


def crazy_title():
    """the title in pieces: a ransom-note letter per file (JS wobbles them), the O an eye; UPPER and the subtitle"""
    s = 'crazy'
    layout = []
    x = 0
    for i, (ch, fname, px, scrap, ink, rot) in enumerate(RANSOM):
        if ch == 'O':
            layout.append(dict(eye=True, x=x + 36, w=72))
            x += 76
            continue
        img = ransom_letter(ch, fname, px, scrap, ink, rot, 700 + i, 700 if 'Grenze' in fname else None)
        save(img, s, f'title_{i}')
        layout.append(dict(file=f'title_{i}', x=x + img.width / 2, w=img.width, h=img.height))
        x += img.width - 16
    total = x + 16
    for L in layout:
        L['x'] = round(L['x'] - total / 2, 1)
    up = Image.new('RGBA', (220, 40), (0, 0, 0, 0))
    ux = 6
    for k, (ch, fname, col, scrap) in enumerate([('U', 'RubikBeastly.ttf', (20, 10, 20), (90, 240, 255)), ('P', 'BebasNeue.ttf', (240, 236, 210), (120, 30, 60)),
                                                 ('P', 'UnifrakturMaguntia.ttf', (20, 10, 20), (230, 255, 40)), ('E', 'Monoton.ttf', (255, 90, 180), (14, 10, 34)),
                                                 ('R', 'SairaStencilOne.ttf', (236, 226, 200), (150, 70, 34))]):
        li = ransom_letter(ch, fname, 22, scrap, col, (-1) ** k * 7, 800 + k)
        up.alpha_composite(li, (ux, (40 - li.height) // 2))
        ux += li.width - 8
    save(up.crop((0, 0, ux + 10, 40)), s, 'title_upper')
    sub = Image.new('RGBA', (300, 50), (0, 0, 0, 0))
    m = text_mask(sub.size, (150, 22), 'a weird game', font('RubikWetPaint.ttf', 26), spacing=2)
    sub = Image.alpha_composite(sub, glow(m, ACIDG, 3, 0.6))
    sub.paste(ACIDG, (0, 0), m)
    save(sub.crop(sub.getbbox()), s, 'title_sub')
    return dict(letters=layout, width=round(total))


def build_crazy():
    s = 'crazy'
    meta = {}
    for name, wd, seed in [('band', BAND_W, 131), ('band_wide', BAND_WIDE, 132), ('panel', PANEL_W, 242)]:
        band, eyes = crazy_band(wd, H, seed, panel=name == 'panel')
        save(band, s, name)
        meta[name] = eyes
    save(crazy_teeth(H, 353), s, 'rule')
    ball, iris = crazy_eye(20)
    save(ball, s, 'eye_ball')
    save(iris, s, 'eye_iris')
    big_ball, big_iris = crazy_eye(34)
    save(big_ball, s, 'eye_big_ball')
    save(big_iris, s, 'eye_big_iris')
    for i, c in enumerate([(200, 230, 60), (240, 120, 170), (226, 214, 186), (90, 200, 220), (180, 140, 240)]):
        save(crazy_tag(900 + i, c), s, f'plate{i}')
    meta['title'] = crazy_title()
    with open(os.path.join(OUT, s, 'layout.json'), 'w') as fh:
        json.dump(meta, fh, indent=1)


# =====================================================================================================================
# TRIPE: the tripe fungus (Auricularia mesenterica): rubbery lobes, their insides wrinkled into meandering ridges,
# glossy, the margins pale and hairy
TRIPE = [(0, (22, 12, 18)), (0.3, (56, 32, 40)), (0.55, (96, 58, 60)), (0.78, (150, 92, 80)), (0.92, (196, 130, 106)), (1, (232, 180, 158))]
LOBE = [(0, (60, 38, 44)), (0.45, (120, 80, 78)), (0.8, (172, 124, 110)), (1, (214, 176, 160))]
FUZZ = (206, 196, 200)
SALMON = (240, 160, 128)


def meanders(w, h, seed, scale=16, warp=12, sharp=2.4, stretch=1.0):
    """brain-like meandering ridges: the iso-line of a warped noise, sharpened (L)"""
    pad = int(warp) + 2
    bw, bh = w + 2 * pad, h + 2 * pad
    base = noise(bw, max(4, int(bh / stretch)), scale, seed, 3, 0.45).resize((bw, bh), Image.BICUBIC)
    wa, wb = noise(w, h, scale * 3, seed + 1, 2), noise(w, h, scale * 3, seed + 2, 2)
    bp, ap, cp = base.load(), wa.load(), wb.load()
    out = []
    for y in range(h):
        for x in range(w):
            v = bp[int(x + pad + (ap[x, y] - 128) / 128 * warp), int(y + pad + (cp[x, y] - 128) / 128 * warp)] / 255
            out.append(int(255 * max(0.0, 1 - abs(2 * v - 1)) ** sharp))
    m = Image.new('L', (w, h))
    m.putdata(out)
    return m


def wet(col, hm, k=2.2, gloss=0.6, blur=1.1):
    sh = relief(hm, k, blur)
    out = lit(col, sh)
    spec = threshold(sh, 192, 16).point(lambda v: round(v * gloss))
    out.paste((250, 236, 232), (0, 0), spec)
    return out, spec


def fuzz_rim(img, mask, rnd, width=4, hair=0.5):
    """the pale hairy margin round a mask (on an RGBA img)"""
    ring = ImageChops.subtract(mask, mask.filter(ImageFilter.MinFilter(width * 2 + 1)))
    pale = Image.new('RGBA', img.size, FUZZ + (0,))
    pale.putalpha(ring.filter(ImageFilter.GaussianBlur(1)).point(lambda v: round(v * 0.85)))
    img.alpha_composite(pale)
    # hairs: specks just outside the edge
    outer = ImageChops.subtract(mask.filter(ImageFilter.MaxFilter(5)), mask)
    sp = ImageChops.multiply(outer, threshold(noise(img.width, img.height, 1, rnd.randrange(9999), 1), 150, 30))
    hairs = Image.new('RGBA', img.size, (226, 220, 222, 0))
    hairs.putalpha(sp.point(lambda v: round(v * hair)))
    img.alpha_composite(hairs)
    return img


def lobe(w, h, seed, tone=LOBE, ridged=0.35):
    """one ear-shaped lobe (RGBA): a wavy rim, a dome with fine radial wrinkles, a pale hairy margin"""
    rnd = random.Random(seed)
    m = Image.new('L', (w, h), 0)
    ph = [rnd.uniform(0, 6.3) for _ in range(3)]
    pts = []
    for k in range(72):
        a = k * math.pi * 2 / 72
        r = 1 + 0.07 * math.sin(5 * a + ph[0]) + 0.04 * math.sin(9 * a + ph[1]) + 0.03 * math.sin(13 * a + ph[2])
        pts.append((w / 2 + math.cos(a) * (w / 2 - 6) * r * 0.95, h / 2 + math.sin(a) * (h / 2 - 6) * r * 0.95))
    ImageDraw.Draw(m).polygon(pts, fill=255)
    dome = m.filter(ImageFilter.GaussianBlur(min(w, h) / 5))
    rid = meanders(w, h, seed, scale=max(6, min(w, h) // 5), warp=5, sharp=2.0, stretch=1.6)
    hm = Image.blend(dome, ImageChops.multiply(rid, dome), ridged)
    col, _ = wet(gmap(hm, tone), hm, 2.0, 0.55)
    img = rgba(col, m)
    return fuzz_rim(img, m, rnd, 3, 0.6)


def tripe_surface(w, h, seed, dark=1.0):
    hm = meanders(w, h, seed, scale=15, warp=12, sharp=2.2, stretch=1.8)
    hm = ImageChops.lighter(hm, noise(w, h, 40, seed + 5, 3).point(lambda v: round(v * 0.35)))
    col, spec = wet(gmap(hm, TRIPE), hm, 2.4, 0.5)
    return col, hm, spec


def tripe_band(w, h, seed, panel=False):
    rnd = random.Random(seed)
    col, hm, spec = tripe_surface(w, h, seed)
    img = col.convert('RGBA')
    # lobes: a crown of them at the top, a few down the band, overlapping
    spots = [(rnd.uniform(-20, w + 20), rnd.uniform(-30, 30), rnd.uniform(70, 110), rnd.uniform(50, 80)) for _ in range(int(w / 40) + 2)]
    spots += [(rnd.uniform(0, w), y + rnd.uniform(-20, 20), rnd.uniform(50, 80), rnd.uniform(34, 56)) for y in range(140, h - 140, 120)]
    for k, (x, y, lw, lh) in enumerate(spots):
        lb = lobe(int(lw), int(lh), seed * 10 + k)
        sh = Image.new('L', img.size, 0)
        sh.paste(lb.getchannel('A'), (int(x - lw / 2) + 3, int(y - lh / 2) + 5))
        img.alpha_composite(glow(sh, (0, 0, 0), 4, 0.8))
        img.alpha_composite(lb, (int(x - lw / 2), int(y - lh / 2)))
    img = mul(img, vgrad(w, h, [(0, 180), (0.55, 140), (1, 56)]))
    img = mul(img, hgrad(w, h, lambda t: 0.8 + 0.2 * math.sin(math.pi * min(1, t * 1.1)) ** 0.5))
    return img


def tripe_rule(h, seed, w=28):
    """the rule: the fungus' margin down the band's edge, scalloped and hairy"""
    rnd = random.Random(seed)
    m = Image.new('L', (w, h), 0)
    px = m.load()
    ph = [rnd.uniform(0, 6.3) for _ in range(3)]
    for y in range(h):
        edge = 15 + 4 * math.sin(y * 0.11 + ph[0]) + 2.5 * math.sin(y * 0.29 + ph[1]) + 1.5 * math.sin(y * 0.53 + ph[2])
        for x in range(w):
            if x < edge:
                px[x, y] = 255
    dome = hgrad(w, h, lambda t: 1 - t).point(lambda v: v)
    rid = meanders(w, h, seed, scale=7, warp=4, sharp=2.0, stretch=0.5)
    hm = ImageChops.multiply(Image.blend(dome, rid, 0.5), m)
    col, _ = wet(gmap(hm, LOBE), hm, 2.0, 0.5)
    img = rgba(col, m)
    return fuzz_rim(img, m, rnd, 2, 0.45)


def tripe_plate(seed):
    """an entry: a flattened lobe, its middle wrinkled; + its wet sheen as a glow mask"""
    w, h = PLATE_W, PLATE_H
    rnd = random.Random(seed)
    m = Image.new('L', (w, h), 0)
    pts = [(x, 4 + 2.2 * math.sin(x * 0.11 + seed) + rnd.uniform(-0.6, 0.6)) for x in range(8, w - 7, 4)]
    pts += [(w - 4 - 2 * math.sin(y * 0.3 + seed), y) for y in range(8, h - 7, 4)]
    pts += [(x, h - 4 - 2.2 * math.sin(x * 0.13 + seed * 2)) for x in range(w - 8, 7, -4)]
    pts += [(4 + 2 * math.sin(y * 0.3 + seed * 3), y) for y in range(h - 8, 7, -4)]
    ImageDraw.Draw(m).polygon(pts, fill=255)
    m = m.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 128 else 0)
    dome = m.filter(ImageFilter.GaussianBlur(7))
    rid = meanders(w, h, seed, scale=9, warp=6, sharp=2.0, stretch=0.6)
    hm = Image.blend(dome, ImageChops.multiply(rid, dome), 0.3)
    col, spec = wet(gmap(hm, [(0, (118, 104, 118)), (0.5, (164, 152, 166)), (0.85, (204, 196, 208)), (1, (232, 228, 236))]), hm, 1.6, 0.6)
    img = rgba(col, m)
    img = fuzz_rim(img, m, rnd, 2, 0.5)
    sheen = ImageChops.multiply(spec.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1)), m)
    return img, Image.merge('RGBA', (Image.new('L', (w, h), 255),) * 3 + (sheen,))


def tripe_title():
    """MORKEZELA grown out of the fungus: soft Fraunces letters, wrinkled and wet inside, a hairy pale rim"""
    w, h = TITLE_W, TITLE_H
    rnd = random.Random(44)
    f = font('Fraunces.ttf', 76, [144, 900, 100, 1])
    m = text_mask((w, h), (w / 2, 76), 'Morkezela', f)
    m = m.filter(ImageFilter.GaussianBlur(1.4)).point(lambda v: 255 if v > 110 else 0)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sh = Image.new('L', (w, h), 0)
    sh.paste(m.filter(ImageFilter.MaxFilter(9)), (3, 6))
    img = Image.alpha_composite(img, glow(sh, (6, 2, 4), 6, 1.2))
    dome = m.filter(ImageFilter.GaussianBlur(4))
    rid = meanders(w, h, 45, scale=7, warp=5, sharp=1.8, stretch=1.4)
    hm = Image.blend(dome, ImageChops.multiply(rid, dome), 0.5)
    col, spec = wet(gmap(hm, [(0, (50, 28, 34)), (0.45, (128, 80, 74)), (0.8, (190, 130, 108)), (1, (236, 192, 170))]), hm, 2.6, 0.7)
    img.paste(col, (0, 0), m)
    img = fuzz_rim(img, m, rnd, 1, 0.35)
    fu = font('Fraunces.ttf', 19, [72, 900, 100, 0])
    mu = text_mask((w, h), (w / 2, 22), 'UPPER', fu, spacing=13)
    img.alpha_composite(glow(mu.filter(ImageFilter.MaxFilter(7)), (8, 3, 6), 4, 1.4))
    img.paste((248, 238, 234), (0, 0), mu)
    fs = font('Fraunces.ttf', 14, [72, 600, 100, 0])
    st = text_mask((w, h), (w / 2, 128), 'A WEIRD GAME', fs, spacing=5)
    img.alpha_composite(glow(st.filter(ImageFilter.MaxFilter(5)), (8, 4, 6), 3, 1.0))
    img.paste((220, 200, 196), (0, 0), st)
    # the wet sheen alone (JS makes it glisten) and where drops can fall from (the letters' lowest points)
    sheen = Image.merge('RGBA', (Image.new('L', (w, h), 255),) * 3 + (ImageChops.multiply(spec.filter(ImageFilter.GaussianBlur(0.8)), m),))
    drips = []
    px = m.load()
    for x in range(0, w, 3):
        ys = [y for y in range(h - 1, 0, -1) if px[x, y]]
        if ys and ys[0] > 90:
            drips.append((x, ys[0]))
    drips = [drips[i] for i in sorted(rnd.sample(range(len(drips)), min(10, len(drips))))]
    return img, sheen, drips


def build_tripe():
    s = 'tripe'
    save(tripe_band(BAND_W, H, 141), s, 'band')
    save(tripe_band(BAND_WIDE, H, 142), s, 'band_wide')
    save(tripe_band(PANEL_W, H, 252, panel=True), s, 'panel')
    save(tripe_rule(H, 363), s, 'rule')
    for i in range(5):
        p, g = tripe_plate(1000 + i)
        save(p, s, f'plate{i}')
        save(g, s, f'plate{i}_glow')
    t, sheen, drips = tripe_title()
    save(t, s, 'title')
    save(sheen, s, 'title_sheen')
    with open(os.path.join(OUT, s, 'layout.json'), 'w') as fh:
        json.dump({'drips': drips}, fh)


# =====================================================================================================================
# PANELAK: a post-Soviet prefab tower at dusk, grimy porous concrete, its windows lit one by one; steel lattice like
# a radio telescope's; the entries glass blocks (luxfery) in steel frames, a stairwell light behind them; the name in
# rooftop letters with red neon (one broken), UPPER in cold white neon, the subtitle on a backlit shop sign
SLAB = [(0, (40, 41, 42)), (0.5, (60, 60, 60)), (1, (80, 79, 76))]
AMBER = (255, 204, 102)
NEON = (255, 74, 58)


def lattice(d, x0, y0, x1, y1, col, hi, vertical=True, step=20, chord=3):
    """a steel lattice girder in the box: two chords, struts and zigzag diagonals"""
    if vertical:
        for x in (x0, x1 - chord):
            d.rectangle([x, y0, x + chord - 1, y1], fill=col)
            d.line([(x, y0), (x, y1)], fill=hi)
        y, k = y0, 0
        while y < y1:
            d.line([(x0 + chord, y), (x1 - chord, y)], fill=col, width=2)
            a, b = ((x0 + chord, y), (x1 - chord, min(y1, y + step))) if k % 2 == 0 else ((x1 - chord, y), (x0 + chord, min(y1, y + step)))
            d.line([a, b], fill=col, width=2)
            y += step
            k += 1
    else:
        for y in (y0, y1 - chord):
            d.rectangle([x0, y, x1, y + chord - 1], fill=col)
            d.line([(x0, y), (x1, y)], fill=hi)
        x, k = x0, 0
        while x < x1:
            d.line([(x, y0 + chord), (x, y1 - chord)], fill=col, width=2)
            a, b = ((x, y0 + chord), (min(x1, x + step), y1 - chord)) if k % 2 == 0 else ((x, y1 - chord), (min(x1, x + step), y0 + chord))
            d.line([a, b], fill=col, width=2)
            x += step
            k += 1


def porous(w, h, seed, tone=SLAB):
    """prefab concrete up close: mottled, rough, full of pores (dark holes lit on their lower rim)"""
    img = gmap(noise(w, h, 48, seed, 5, 0.55), tone)
    img = mul(img, curve(noise(w, h, 70, seed + 4, 3), lambda t: 0.7 + 0.38 * t))          # dirty patches
    img = lit(img, relief(noise(w, h, 2, seed + 3, 2), 0.45, 0.6))
    pores = ImageChops.lighter(threshold(noise(w, h, 1, seed + 1, 1), 238, 4), threshold(noise(w, h, 2, seed + 2, 1), 246, 4))
    img.paste((16, 16, 16), (0, 0), pores.point(lambda v: v * 0.7))
    rim = ImageChops.subtract(ImageChops.offset(pores, 0, 1), pores)
    img.paste((104, 104, 100), (0, 0), rim.point(lambda v: v * 0.3))
    return img


def smudge(img, box, colour, alpha, blur):
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).ellipse(box, fill=round(255 * alpha))
    img.paste(colour, (0, 0), m.filter(ImageFilter.GaussianBlur(blur)))


def panelak_facade(w, h, seed, roof=True):
    """the tower's face, grimy: porous panels with tarred joints, patched, soot over the windows, rust and water runs,
    salt bloom; windows in old wood or new white plastic, a boarded one; faded coloured loggia parapets; aerials on
    the roof, a tag at its foot in the fog. Returns the image, the windows (for JS to light), the aviation light."""
    rnd = random.Random(seed)
    img = porous(w, h, seed)
    d = ImageDraw.Draw(img)
    FH, top = 46, 44 if roof else 0
    cols = max(3, round(w / 70))
    cw = w / cols
    loggia = rnd.randrange(cols)
    windows, runs_dark, runs_rust, runs_salt = [], [], [], []
    # patch repairs: lighter, smoother rectangles
    for _ in range(3):
        px, py, pw, ph = rnd.uniform(0, w - 40), rnd.uniform(top + 20, h - 80), rnd.uniform(20, 46), rnd.uniform(10, 26)
        patch = mul(gmap(noise(int(pw), int(ph), 8, rnd.randrange(999), 2), [(0, (70, 70, 68)), (1, (100, 100, 96))]), Image.new('L', (int(pw), int(ph)), 210))
        img.paste(patch, (int(px), int(py)))
    d = ImageDraw.Draw(img)
    for y in range(top, h, FH):                          # tarred joints
        d.line([(0, y), (w, y)], fill=(10, 10, 10), width=3)
        d.line([(0, y + 3), (w, y + 3)], fill=(78, 78, 76))
        runs_salt += [(x, y + 3) for x in range(rnd.randint(0, 40), w, rnd.randint(40, 90))]
    for c in range(1, cols):
        x = round(c * cw)
        d.line([(x, top), (x, h)], fill=(12, 12, 12), width=3)
    for fl, y in enumerate(range(top, h - 20, FH)):
        for c in range(cols):
            cx = (c + 0.5) * cw
            if c == loggia:
                d.rectangle([cx - cw / 2 + 4, y + 4, cx + cw / 2 - 4, y + FH - 2], fill=(8, 8, 9))
                win = (round(cx - 10), y + 8, 20, 22)
                windows.append(win)
                d.rectangle([win[0], win[1], win[0] + win[2], win[1] + win[3]], outline=(64, 54, 42), fill=(16, 18, 24))
                # a faded coloured parapet, corrugated, rusting at its foot
                pw = int(cw - 6)
                tint = rnd.choice([(150, 118, 60), (128, 62, 46), (72, 90, 108), (110, 112, 70)])
                par = mul(solid((pw, 16), tint), hgrad(pw, 16, lambda t: 0.75 + 0.15 * math.sin(t * pw * 0.9)))
                par = mul(par, curve(noise(pw, 16, 4, seed + fl * 7 + c, 2), lambda t: 0.55 + 0.45 * t))
                img.paste(par, (round(cx - cw / 2 + 3), y + FH - 18))
                d = ImageDraw.Draw(img)
                d.line([(cx - cw / 2 + 3, y + FH - 18), (cx + cw / 2 - 3, y + FH - 18)], fill=(30, 26, 22), width=2)
                runs_rust += [(cx - cw / 2 + 6 + k * 9, y + FH - 2) for k in range(int(cw / 9) - 1)]
                if rnd.random() < 0.35:                  # laundry
                    for k in range(3):
                        lx = cx - cw / 2 + 10 + k * 9
                        d.rectangle([lx, y + 10, lx + 6, y + 20], fill=rnd.choice([(120, 54, 54), (60, 76, 110), (160, 150, 124)]))
                if rnd.random() < 0.2:                   # a dish
                    d.ellipse([cx + cw / 2 - 20, y + FH - 32, cx + cw / 2 - 8, y + FH - 18], fill=(120, 120, 116))
                continue
            win = (round(cx - 11), y + 10, 22, 26)
            windows.append(win)
            x0, y0, ww, wh = win
            kind = rnd.random()
            frame = (146, 146, 140) if kind < 0.4 else (74, 52, 36) if kind < 0.85 else (52, 54, 56)
            d.rectangle([x0 - 2, y0 - 2, x0 + ww + 2, y0 + wh + 2], fill=frame)
            if kind > 0.97:                              # boarded up
                d.rectangle([x0, y0, x0 + ww, y0 + wh], fill=(98, 80, 58))
                d.line([(x0, y0 + 8), (x0 + ww, y0 + 8)], fill=(60, 48, 34))
                d.line([(x0, y0 + 17), (x0 + ww, y0 + 17)], fill=(60, 48, 34))
            else:
                glass = mul(solid((ww, wh), (26, 30, 40)), vgrad(ww, wh, [(0, 255), (1, 110)]))
                if rnd.random() < 0.5:                   # a curtain, dim
                    glass = mul(glass, hgrad(ww, wh, lambda t: 1 + 0 * t).point(lambda v: v))
                    cur = mul(solid((ww, wh), rnd.choice([(70, 60, 50), (60, 54, 66), (80, 70, 44)])), hgrad(ww, wh, lambda t: 0.75 + 0.25 * abs(math.sin(t * 9))))
                    glass = Image.blend(glass, cur, 0.35)
                img.paste(glass, (x0, y0))
                d = ImageDraw.Draw(img)
                d.line([(x0 + ww // 2, y0), (x0 + ww // 2, y0 + wh)], fill=frame)
                d.line([(x0, y0 + 9), (x0 + ww, y0 + 9)], fill=frame)
            d.line([(x0 - 3, y0 + wh + 3), (x0 + ww + 3, y0 + wh + 3)], fill=(96, 96, 92), width=2)    # the sill
            runs_dark += [(x0 + rnd.uniform(0, ww), y0 + wh + 4) for _ in range(3)]
            # the dark wedge every sill leaves on the wall below it
            wedge = Image.new('L', img.size, 0)
            spread = rnd.uniform(2, 8)
            ImageDraw.Draw(wedge).polygon([(x0 - 2, y0 + wh + 4), (x0 + ww + 2, y0 + wh + 4), (x0 + ww + spread, y0 + wh + rnd.uniform(22, 40)),
                                           (x0 - spread, y0 + wh + rnd.uniform(22, 40))], fill=round(255 * rnd.uniform(0.3, 0.6)))
            img.paste((14, 13, 12), (0, 0), wedge.filter(ImageFilter.GaussianBlur(4)))
            d = ImageDraw.Draw(img)
            # soot from the kitchen over the window
            if rnd.random() < 0.45:
                smudge(img, [x0 - 6, y0 - 22, x0 + ww + 6, y0 + 4], (8, 8, 8), 0.55, 6)
                d = ImageDraw.Draw(img)
            if rnd.random() < 0.3:                       # an AC box, rusting
                ax = x0 + rnd.choice([-6, ww - 8])
                d.rectangle([ax, y0 + wh + 6, ax + 14, y0 + wh + 13], fill=(140, 140, 134))
                for gx in range(ax + 2, ax + 13, 2):
                    d.line([(gx, y0 + wh + 7), (gx, y0 + wh + 12)], fill=(84, 84, 80))
                runs_rust.append((ax + 7, y0 + wh + 13))
    img = img.convert('RGBA')
    img.alpha_composite(streaks((w, h), runs_dark, rnd, (30, 120), (6, 6, 6)))
    img.alpha_composite(streaks((w, h), runs_rust, rnd, (16, 60), (96, 46, 22)))
    salt = streaks((w, h), runs_salt, rnd, (8, 30), (190, 188, 176))
    salt.putalpha(salt.getchannel('A').point(lambda v: v // 2))
    img.alpha_composite(salt)
    img = img.convert('RGB')
    av = None
    if roof:
        sky = mul(solid((w, top), (34, 38, 50)), vgrad(w, top, [(0, 150), (1, 255)]))
        img.paste(sky, (0, 0))
        d = ImageDraw.Draw(img)
        d.rectangle([0, top - 6, w, top], fill=(30, 30, 32))
        d.line([(0, top - 6), (w, top - 6)], fill=(80, 80, 80))
        smudge(img, [-20, top - 4, w + 20, top + 50], (6, 6, 6), 0.6, 10)          # the roof's edge, black with soot
        d = ImageDraw.Draw(img)
        for k in range(cols + 1):
            ax = rnd.uniform(10, w - 10)
            ah = rnd.uniform(16, 34)
            d.line([(ax, top - 6), (ax + rnd.uniform(-2, 2), top - 6 - ah)], fill=(12, 12, 14))
            for j in range(3):
                yy = top - 6 - ah + 3 + j * 5
                L = 10 - j * 2
                d.line([(ax - L, yy + rnd.uniform(-1, 1)), (ax + L, yy)], fill=(12, 12, 14))
        mx = w * 0.18
        d.line([(mx, top - 6), (mx, 4)], fill=(12, 12, 14), width=2)
        av = (round(mx), 4)
    # a tag low on the wall, half in the fog
    d = ImageDraw.Draw(img)
    gx, gy = rnd.uniform(10, w * 0.5), h - rnd.uniform(70, 100)
    pts = snake(rnd, gx, gy, -0.2, 40, 2.2, 1.4)
    d.line(pts, fill=(150, 84, 120), width=2)
    pts = snake(rnd, gx + 10, gy + 6, 0.1, 30, 2.0, 1.6)
    d.line(pts, fill=(170, 170, 160), width=1)
    img = mul(img, vgrad(w, h, [(0, 205), (0.6, 180), (1, 125)]))
    fog = ImageChops.multiply(noise(w, h, 40, seed + 9, 3), vgrad(w, h, [(0, 0), (0.62, 0), (0.85, 150), (1, 230)]))
    img = Image.alpha_composite(img.convert('RGBA'), glow(fog, (86, 90, 100), 6, 0.9)).convert('RGB')
    return img, windows, av


def lit_window(kind):
    """a lit window: warm light behind curtains (0, 1) or the blue of a TV (2)"""
    ww, wh = 22, 26
    base = {0: (255, 200, 110), 1: (240, 150, 80), 2: (92, 120, 196)}[kind]
    img = mul(solid((ww, wh), base), vgrad(ww, wh, [(0, 255), (1, 190)]))
    d = ImageDraw.Draw(img)
    if kind < 2:
        for x in range(0, ww, 3):
            d.line([(x, 0), (x, wh)], fill=tuple(round(c * 0.82) for c in base))
        d.rectangle([0, 0, ww, 3], fill=tuple(round(c * 0.6) for c in base))
        if kind == 0:                                     # a plant on the sill
            d.ellipse([3, wh - 9, 10, wh - 2], fill=(40, 56, 30))
    else:
        d.rectangle([4, 12, 14, 20], fill=(200, 220, 255))
    d.line([(ww // 2, 0), (ww // 2, wh)], fill=(60, 50, 40))
    d.line([(0, 9), (ww, 9)], fill=(60, 50, 40))
    return img.convert('RGBA')


def panelak_truss(h, seed, w=24):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lattice(d, 0, 0, w, h, (60, 62, 66, 255), (120, 122, 124, 255), True, 22, 4)
    rmask = ImageChops.multiply(img.getchannel('A'), threshold(noise(w, h, 18, seed, 3), 130, 40))
    rust_c = Image.new('RGBA', (w, h), (104, 50, 26, 255))
    rust_c.putalpha(rmask.point(lambda v: round(v * 0.85)))
    img.alpha_composite(rust_c)
    for y in range(11, h, 44):
        d.rectangle([0, y - 4, w - 1, y + 4], fill=(74, 76, 80, 255))
        for x in (4, w // 2, w - 5):
            d.ellipse([x - 1.5, y - 1.5, x + 1.5, y + 1.5], fill=(10, 10, 12, 255))
    return img


# --- the entries: glass blocks (luxfery) in a steel frame -------------------------------------------------------------
LUX = 20


def lux_block(lit):
    """one glass block with its mortar (a tile): rippled thick glass, greenish; lit = a stairwell tube behind it"""
    s = LUX
    if lit:
        base, ripple, edge, mortar = (164, 186, 160), (226, 238, 210), (100, 122, 104), (40, 40, 38)
    else:
        base, ripple, edge, mortar = (30, 40, 40), (58, 74, 72), (16, 22, 22), (70, 70, 68)
    img = Image.new('RGB', (s, s), mortar)
    g = Image.new('RGB', (s - 2, s - 2), base)
    gp = g.load()
    n = s - 2
    for y in range(n):
        for x in range(n):
            # the thick glass: darker toward its rim, rippled in rings round the middle
            ex = min(x, y, n - 1 - x, n - 1 - y) / (n / 2)
            rr = math.hypot(x - n / 2 + 0.5, (y - n / 2 + 0.5) * 1.15)
            wave = 0.5 + 0.5 * math.sin(rr * 1.35 + math.sin(x * 0.7) * 0.6)
            k = min(1, ex * 2.2)
            c = [edge[i] + (base[i] - edge[i]) * k for i in range(3)]
            c = [c[i] + (ripple[i] - c[i]) * wave * 0.55 * k for i in range(3)]
            gp[x, y] = tuple(int(v) for v in c)
    d = ImageDraw.Draw(g)
    d.line([(2, 2), (6, 2)], fill=(ripple if not lit else (250, 252, 240)))
    img.paste(g, (1, 1))
    return img.convert('RGBA')


def girder_tile():
    """the frame's chords: a steel angle with rivets (a tile 12 x 6)"""
    img = Image.new('RGBA', (12, 6), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 11, 5], fill=(58, 60, 64, 255))
    d.line([(0, 0), (11, 0)], fill=(128, 130, 132, 255))
    d.line([(0, 5), (11, 5)], fill=(18, 18, 20, 255))
    d.ellipse([4, 2, 7, 5], fill=(90, 92, 94, 255))
    d.point((5, 2), fill=(150, 152, 150, 255))
    rm = threshold(noise(12, 6, 3, 41, 2), 150, 30)
    img.paste((104, 50, 26), (0, 0), ImageChops.multiply(rm, img.getchannel('A')).point(lambda v: v // 2))
    return img


def lattice_post(h=48, w=10):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lattice(d, 0, 0, w, h, (58, 60, 64, 255), (124, 126, 128, 255), True, 10, 2)
    rm = threshold(noise(w, h, 6, 42, 2), 140, 30)
    img.paste((104, 50, 26), (0, 0), ImageChops.multiply(rm, img.getchannel('A')).point(lambda v: v // 2))
    return img


def stair_switch(on):
    """the stairwell light's push-switch, its little orange window glowing"""
    img = Image.new('RGBA', (12, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, 11, 15], 2, fill=(176, 166, 136, 255))
    d.line([(1, 1), (10, 1)], fill=(214, 206, 180, 255))
    d.rounded_rectangle([2, 3, 9, 12], 1, fill=(150, 140, 112, 255) if not on else (126, 118, 94, 255))
    d.rectangle([4, 5, 7, 7], fill=(255, 158, 50, 255) if on else (130, 66, 24, 255))
    return img


def panelak_title():
    """MORKEZELA as rooftop letters on a lattice girder: grimy sheet-metal faces, red neon tubes (lit in a separate
    layer, one letter's apart: it flickers); UPPER in cold white neon on its own small girder; the subtitle on a
    backlit shop sign hanging under the big one; a dish at the end"""
    w, h = TITLE_W, TITLE_H
    rnd = random.Random(77)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    f = font('RussoOne.ttf', 62)
    word = 'MORKEZELA'
    probe = ImageDraw.Draw(Image.new('L', (4, 4)))
    widths = [probe.textlength(ch, font=f) for ch in word]
    gap = 6
    total = sum(widths) + gap * (len(word) - 1)
    x = (w - total) / 2
    base_y = 92
    masks = []
    for ch, cw in zip(word, widths):
        m = Image.new('L', (w, h), 0)
        ImageDraw.Draw(m).text((x, base_y), ch, font=f, fill=255, anchor='ls')
        masks.append(m)
        x += cw + gap
    allm = Image.new('L', (w, h), 0)
    for m in masks:
        allm = ImageChops.lighter(allm, m)
    d = ImageDraw.Draw(img)
    gx0, gx1 = (w - total) / 2 - 18, (w + total) / 2 + 18
    for px in range(int(gx0) + 10, int(gx1), 46):
        d.line([(px, 40), (px, base_y + 4)], fill=(36, 36, 40, 255), width=3)
    lattice(d, gx0, base_y + 2, gx1, base_y + 22, (56, 58, 62, 255), (110, 112, 114, 255), False, 18, 3)
    side = Image.new('RGBA', (w, h), (20, 20, 22, 0))
    side.putalpha(ImageChops.offset(allm, 3, 3))
    img.alpha_composite(side)
    face = gmap(noise(w, h, 6, 78, 3), [(0, (104, 98, 88)), (1, (176, 170, 156))])
    face = mul(face, curve(noise(w, h, 18, 79, 3), lambda t: 0.6 + 0.45 * t))
    face = Image.alpha_composite(face.convert('RGBA'), streaks((w, h), [(rnd.uniform(0, w), rnd.uniform(36, 70)) for _ in range(46)], rnd, (10, 34), (88, 44, 22))).convert('RGB')
    img.paste(face, (0, 0), allm)
    tube = ImageChops.subtract(allm.filter(ImageFilter.MinFilter(5)), allm.filter(ImageFilter.MinFilter(9)))
    img.paste((92, 30, 28), (0, 0), tube)
    broken = 5
    tube_ok = Image.new('L', (w, h), 0)
    for k, m in enumerate(masks):
        if k != broken:
            tube_ok = ImageChops.lighter(tube_ok, ImageChops.multiply(tube, m))
    tube_k = ImageChops.multiply(tube, masks[broken])

    def neon_layer(tm, colour, core):
        layer = glow(tm.filter(ImageFilter.MaxFilter(3)), colour, 5, 1.6)
        layer.alpha_composite(glow(tm, core, 0.6, 1.4))
        return layer
    # UPPER: thin tube letters on a small girder of its own, up on the left
    fu = font('Jost.ttf', 24, 300)
    ux, uy = int(gx0) + 6, 26
    um = Image.new('L', (w, h), 0)
    ImageDraw.Draw(um).text((ux, uy), 'UPPER', font=fu, fill=255, anchor='lm', stroke_width=0)
    ubb = um.getbbox()
    d = ImageDraw.Draw(img)
    lattice(d, ubb[0] - 6, ubb[3] + 3, ubb[2] + 6, ubb[3] + 11, (56, 58, 62, 255), (110, 112, 114, 255), False, 8, 2)
    for px in (ubb[0] + 4, ubb[2] - 4):
        d.line([(px, ubb[3] + 11), (px, 46)], fill=(36, 36, 40, 255), width=2)
    img.paste((150, 160, 170), (0, 0), um)                                    # the tubes, unlit
    upper_neon = neon_layer(um, (150, 220, 255), (236, 250, 255))
    # the subtitle: a backlit shop sign in a steel box, hanging under the girder
    fs = font('Jost.ttf', 13, 700)
    bw, bh = 150, 22
    px2, py2 = (w - bw) // 2, base_y + 30
    for xx in (px2 + 24, px2 + bw - 24):
        d.line([(xx, base_y + 22), (xx, py2)], fill=(30, 30, 32, 255))
    d.rectangle([px2, py2, px2 + bw, py2 + bh], fill=(40, 42, 46, 255))
    panel = mul(solid((bw - 6, bh - 6), (236, 230, 208)), curve(noise(bw - 6, bh - 6, 4, 5, 2), lambda t: 0.85 + 0.15 * t))
    panel = mul(panel, hgrad(bw - 6, bh - 6, lambda t: 0.88 + 0.12 * math.sin(math.pi * t)))
    img.paste(panel, (px2 + 3, py2 + 3))
    st = text_mask((w, h), (w / 2, py2 + bh / 2 + 1), 'A WEIRD GAME', fs, spacing=3)
    img.paste((150, 30, 26), (0, 0), st)
    box = Image.new('L', (w, h), 0)
    ImageDraw.Draw(box).rectangle([px2 + 3, py2 + 3, px2 + bw - 3, py2 + bh - 3], fill=255)
    box_glow = glow(box, (255, 244, 214), 7, 0.9)
    dx, dy = int(gx1) + 2, base_y - 10
    d = ImageDraw.Draw(img)
    d.pieslice([dx - 4, dy - 26, dx + 30, dy + 8], 120, 300, fill=(80, 82, 86, 255))
    d.line([(dx + 6, dy - 9), (dx + 22, dy - 22)], fill=(36, 36, 40, 255), width=2)
    d.line([(dx + 10, dy + 2), (dx + 10, base_y + 22)], fill=(36, 36, 40, 255), width=3)
    meta = {'aviation': [round(gx1) + 12, base_y - 34]}
    return (img, neon_layer(tube_ok, NEON, (255, 180, 170)), neon_layer(tube_k, NEON, (255, 180, 170)), upper_neon, box_glow, meta)


def build_panelak():
    s = 'panelak'
    meta = {}
    for name, wd, seed in [('band', BAND_W, 151), ('band_wide', BAND_WIDE, 152), ('panel', PANEL_W, 262)]:
        img, wins, av = panelak_facade(wd, H, seed, roof=True)
        save(img, s, name)
        meta[name] = {'windows': wins, 'aviation': av}
    save(panelak_truss(H, 373), s, 'rule')
    for k in range(3):
        save(lit_window(k), s, f'win{k}')
    save(lux_block(False), s, 'lux')
    save(lux_block(True), s, 'lux_lit')
    save(girder_tile(), s, 'girder')
    save(lattice_post(), s, 'post')
    save(stair_switch(False), s, 'switch')
    save(stair_switch(True), s, 'switch_on')
    t, neon, neon_k, neon_up, box_glow, tm = panelak_title()
    for name, im in [('title', t), ('title_neon', neon), ('title_neon_broken', neon_k), ('title_neon_upper', neon_up), ('title_box_glow', box_glow)]:
        save(im, s, name)
    meta['title'] = tm
    with open(os.path.join(OUT, s, 'layout.json'), 'w') as fh:
        json.dump(meta, fh)



SKINS = {'rust': build_rust, 'biomech': build_biomech, 'jungle': build_jungle, 'crazy': build_crazy,
         'tripe': build_tripe, 'panelak': build_panelak}


# --- preview ------------------------------------------------------------------------------------------------------------
LABELS = ['Nová hra', 'Načíst hru', 'Nastavení', 'Ukončit hru']
PREVIEW_FONT = {'rust': ('SairaCondensed-Bold.ttf', 21, None, (232, 220, 196), (255, 176, 87)),
                'biomech': ('Grenze.ttf', 20, 700, (222, 212, 190), (255, 120, 136)),
                'jungle': ('Rubik.ttf', 18, 600, (226, 228, 214), (170, 255, 206)),
                'crazy': ('RubikBeastly.ttf', 21, None, (30, 14, 30), (255, 40, 150)),
                'tripe': ('Fraunces.ttf', 19, [24, 700, 100, 0], (46, 22, 34), (150, 50, 40)),
                'panelak': ('Jost.ttf', 18, 600, (240, 232, 210), (255, 226, 150))}


def nine(img, w, h, l=16, r=16, t=12, b=12):
    """a nine-slice stretch of img to w x h"""
    W, Hh = img.size
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    xs = [(0, l, 0, l), (l, W - r, l, w - r), (W - r, W, w - r, w)]
    ys = [(0, t, 0, t), (t, Hh - b, t, h - b), (Hh - b, Hh, h - b, h)]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            piece = img.crop((sx0, sy0, sx1, sy1)).resize((max(1, dx1 - dx0), max(1, dy1 - dy0)), Image.BILINEAR)
            out.paste(piece, (dx0, dy0))
    return out


def eye_at(scr, d, pre, x, y, k):
    ball = Image.open(os.path.join(d, f'eye_{pre}ball.png')).convert('RGBA')
    iris = Image.open(os.path.join(d, f'eye_{pre}iris.png')).convert('RGBA')
    if k != 1:
        ball = ball.resize((max(1, round(ball.width * k)), max(1, round(ball.height * k))), Image.LANCZOS)
        iris = iris.resize((max(1, round(iris.width * k)), max(1, round(iris.height * k))), Image.LANCZOS)
    scr.alpha_composite(ball, (round(x - ball.width / 2), round(y - ball.height / 2)))
    scr.alpha_composite(iris, (round(x - iris.width / 2 + 3 * k), round(y - iris.height / 2 + 2 * k)))


PREVIEW_GLOW = {'biomech': LYMPH, 'jungle': MINT, 'tripe': (255, 230, 222), 'panelak': AMBER}


def preview(skin):
    W, Hh = 1067, 600
    band_w = 219
    RX = band_w - 4
    scr = Image.new('RGBA', (W, Hh), (0, 0, 0, 255))
    paint = Image.open(os.path.join(ROOT, 'assets/images/backgrounds/menu_painting/band.png')).convert('RGBA')
    k = Hh / paint.height
    paint = paint.resize((round(paint.width * k), Hh), Image.LANCZOS)
    scr.paste(paint, (W - paint.width, 0))
    d = os.path.join(OUT, skin)
    band = Image.open(os.path.join(d, 'band.png')).convert('RGBA').crop((0, 0, RX, Hh))
    scr.paste(band, (0, 0))
    rule = Image.open(os.path.join(d, 'rule.png')).convert('RGBA')
    scr.alpha_composite(rule, (RX + 2 - rule.width // 2, 0))
    fname, px, wght, col, col_on = PREVIEW_FONT[skin]
    f = font(fname, px, wght)
    for i, lab in enumerate(LABELS if skin != 'panelak' else []):     # (panelak's entries are built in JS from tiles)
        y = 120 + i * 58 + 23
        pl = nine(Image.open(os.path.join(d, f'plate{i}.png')).convert('RGBA'), RX - 22, 46)
        scr.alpha_composite(pl, (11, y - 23))
        on = i == 0
        gf = next((g for g in (f'plate{i}_glow.png', 'plate_glow.png') if os.path.exists(os.path.join(d, g))), None)
        if on and gf:
            gl = nine(Image.open(os.path.join(d, gf)).convert('RGBA'), RX - 22, 46)
            tint = Image.new('RGBA', gl.size, PREVIEW_GLOW[skin] + (0,))
            tint.putalpha(gl.getchannel('A').point(lambda v: v * 0.8))
            scr.alpha_composite(tint, (11, y - 23))
        dr = ImageDraw.Draw(scr)
        upper = skin in ('rust', 'panelak')
        dr.text((11 + (RX - 22) / 2 - (8 if skin == 'rust' else 0), y), lab.upper() if upper else lab, font=f,
                fill=col_on if on else col, anchor='mm', stroke_width=0 if skin in ('crazy', 'tripe') else 2, stroke_fill=(10, 8, 8))
        if skin == 'rust':
            lamp = Image.open(os.path.join(d, 'lamp_on.png' if on else 'lamp_off.png')).convert('RGBA')
            if on:
                g = Image.new('L', (W, Hh), 0)
                ImageDraw.Draw(g).ellipse([RX - 60, y - 40, RX + 10, y + 20], fill=120)
                scr = Image.alpha_composite(scr, glow(g, SODIUM, 14))
            scr.alpha_composite(lamp, (RX - 34, y - 26))
    tx = round(219 + 457 * k)
    if skin == 'crazy':
        lay = json.load(open(os.path.join(d, 'layout.json')))
        for e in lay['band']:
            if e['x'] < RX - 10:
                eye_at(scr, d, '', e['x'], e['y'], e['r'] / 20)
        up = Image.open(os.path.join(d, 'title_upper.png')).convert('RGBA')
        scr.alpha_composite(up, (tx - up.width // 2 - 120, 6))
        for L in lay['title']['letters']:
            if L.get('eye'):
                eye_at(scr, d, 'big_', tx + L['x'], 70, 1.0)
                continue
            im = Image.open(os.path.join(d, L['file'] + '.png')).convert('RGBA')
            scr.alpha_composite(im, (round(tx + L['x'] - im.width / 2), 70 - im.height // 2))
        sub = Image.open(os.path.join(d, 'title_sub.png')).convert('RGBA')
        scr.alpha_composite(sub, (tx - sub.width // 2 + 90, 116))
    else:
        title = Image.open(os.path.join(d, 'title.png')).convert('RGBA')
        scr.alpha_composite(title, (tx - title.width // 2, 6))
    if skin == 'panelak':
        lay = json.load(open(os.path.join(d, 'layout.json')))
        rnd = random.Random(3)
        for (x, y, ww, wh) in lay['band']['windows']:
            if x + ww < RX and rnd.random() < 0.35:
                scr.alpha_composite(Image.open(os.path.join(d, f'win{rnd.randrange(3)}.png')).convert('RGBA').crop((0, 0, ww, wh)), (x, y))
        for n in ('title_neon', 'title_neon_broken', 'title_neon_upper', 'title_box_glow'):
            nl = Image.open(os.path.join(d, n + '.png')).convert('RGBA')
            scr.alpha_composite(nl, (tx - nl.width // 2, 6))
    if skin == 'tripe':
        sh = Image.open(os.path.join(d, 'title_sheen.png')).convert('RGBA')
        scr.alpha_composite(sh, (tx - sh.width // 2, 6))
    if os.path.exists(os.path.join(d, 'band_myc.png')):
        myc = Image.open(os.path.join(d, 'band_myc.png')).getchannel('A').crop((0, 0, RX, Hh))
        mm = Image.new('L', (W, Hh), 0)
        mm.paste(myc, (0, 0))
        scr = Image.alpha_composite(scr, glow(mm, MINT, 2, 0.8))
    os.makedirs(os.path.join(ROOT, 'out', 'menu_skins'), exist_ok=True)
    p = os.path.join(ROOT, 'out', 'menu_skins', f'{skin}_preview.png')
    scr.convert('RGB').save(p)
    return p


if __name__ == '__main__':
    args = sys.argv[1:]
    prev = '--preview' in args
    names = [a for a in args if not a.startswith('--')] or list(SKINS)
    for n in names:
        SKINS[n]()
        print(n, 'ok', preview(n) if prev else '')
