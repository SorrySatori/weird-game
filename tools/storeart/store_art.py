"""Steam store + library artwork: the key art (default: the main menu painting) composed with the pixel-art logo
(tools/artgen/menu_logo.py, store variant with "A WEIRD GAME") into every format Steamworks asks for.

  python3 tools/storeart/store_art.py [--art path/to/key_art.png] [--out tools/storeart/out] [--demo]

--demo: the demo app's set (-> out/demo/): every capsule, the library capsule and the library logo carry a riveted
bronze "DEMO" plaque under the name (Steam: a demo's capsules / library assets must show it's a demo); the hero and the
page background stay text-free.

Sizes and rules (partner.steamgames.com/doc/store/assets, .../libraryassets, checked 2026-10-30):
  store:   header 920x430, small 462x174 (logo nearly fills it), main 1232x706, vertical 748x896,
           page background 1438x810 (ambient, no text)
  library: capsule 600x900, header 920x430, hero 3840x1240 (NO text; keep the subject inside the centred 860x380
           safe area -- Steam crops the rest when the window resizes), logo PNG with transparency, 1280 wide and/or 720 tall
  community icon 184x184
  Capsules: the art + the game's title only -- no quotes, review scores, "demo" / "wishlist" / sale text
  (except the demo app's own capsules, which must say "demo").
The logo is pixel art: upscaled nearest-neighbour to the next whole multiple, then averaged down to the exact size."""
import sys, os, math, argparse
from PIL import Image, ImageFilter, ImageEnhance, ImageChops

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'artgen'))
sys.argv, _argv = sys.argv[:1], sys.argv[1:]                      # menu_logo reads argv[1] as its out dir
import menu_logo                                                    # noqa: E402
from menu_ui import glow_image                                      # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--art', default=os.path.join(ROOT, 'assets', 'images', 'backgrounds', 'background.png'))
ap.add_argument('--out', default=None)
ap.add_argument('--demo', action='store_true', help="the demo app's set: a DEMO plaque under the name")
args = ap.parse_args(_argv)
args.out = args.out or os.path.join(ROOT, 'tools', 'storeart', 'out', *(['demo'] if args.demo else []))
os.makedirs(args.out, exist_ok=True)

GLOW = (127, 255, 142)

# --- the logo ---------------------------------------------------------------------------------------------------------
def make_logos():
    s, mask = menu_logo.logo(0, subtitle=True)
    full = s.image()
    glow = glow_image(menu_logo.LW, menu_logo.LH, mask, radius=2.6, gain=1.4)
    box = full.getbbox()
    store = (full.crop(box), glow.crop(box))
    # the small capsule: the name only (cut above the subtitle) -- it has to read at 120x45
    sub_top = min(y for (x, y), p in s.part.items() if p == 'letter' and y > 60) - 1
    short_box = (box[0], box[1], box[2], sub_top)
    short = (full.crop(short_box), glow.crop(short_box))
    return store, short

def scale_pixels(im, width):
    """pixel art to an exact width: nearest-neighbour to a whole multiple at least that big, then area-averaged down"""
    k = max(1, math.ceil(width / im.width))
    big = im.resize((im.width * k, im.height * k), Image.NEAREST)
    h = round(im.height * width / im.width)
    return big if big.width == width else big.resize((width, h), Image.BOX)

def put_logo(canvas, logo, cx, cy, width, glow_strength=0.55, shadow=0.6):
    """logo centred on (cx, cy) with a soft dark halo behind it (legibility) and its green bioluminescence"""
    art, glow = logo
    lg = scale_pixels(art, width)
    gl = glow.resize(lg.size, Image.BILINEAR)
    x, y = round(cx - lg.width / 2), round(cy - lg.height / 2)
    # dark halo from the logo's own shape
    pad = width // 12
    a = Image.new('L', (lg.width + 2 * pad, lg.height + 2 * pad), 0)
    a.paste(lg.getchannel('A'), (pad, pad))
    a = a.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(max(8, width // 28)))
    halo = Image.new('RGBA', a.size, (0, 0, 0, 0)); halo.putalpha(a.point(lambda v: int(v * shadow)))
    canvas.alpha_composite(halo, (x - pad, y - pad + max(2, width // 160)))
    # bioluminescence, added
    g = Image.new('RGB', lg.size, GLOW)
    ga = gl.getchannel('A').point(lambda v: int(v * glow_strength))
    region = canvas.crop((x, y, x + lg.width, y + lg.height)).convert('RGB')
    lit = ImageChops.add(region, Image.composite(g, Image.new('RGB', lg.size, (0, 0, 0)), ga))
    canvas.paste(lit, (x, y))
    canvas.alpha_composite(lg, (x, y))
    return y + lg.height

def demo_badge():
    """the demo plaque, native pixels: 'DEMO' cast in bronze (the logo's letters) on a riveted dark-enamel plate"""
    from menu_ui import Spr, BRONZE, ENAMEL, tone, rivet
    from common import INK
    size, sp = 15, 3
    mask, _ = menu_logo.glyph_mask('DEMO', size, 0, 0, sp)
    x0, y0 = min(x for x, _ in mask), min(y for _, y in mask)
    tw, th = max(x for x, _ in mask) - x0 + 1, max(y for _, y in mask) - y0 + 1
    padx, pady = 14, 6
    W, H = tw + 2 * padx, th + 2 * pady + 2                         # +2: the letters' drop shadow
    s = Spr(W, H)
    for y in range(H):
        for x in range(W):
            e = min(x, y, W - 1 - x, H - 1 - y)
            if (x in (0, W - 1)) and (y in (0, H - 1)): continue        # rounded corners
            if e == 0: s.put(x, y, INK, 'contour'); continue
            if e <= 2:                                                  # bronze rim, lit from the top left
                lit_ = 1 if (y <= 2 or x <= 2) and not (y >= H - 3 or x >= W - 3) else -1
                s.put(x, y, tone(BRONZE, 3.6 + 1.6 * lit_ - 0.6 * (e - 1), x, y), 'frame'); continue
            s.put(x, y, tone(ENAMEL, 2.6 - 1.4 * (y - 3) / (H - 6), x, y), 'enamel')
    for rx in (6, W - 7):
        rivet(s, rx, H // 2 - 1)
    letters = {(x - x0 + padx, y - y0 + pady) for x, y in mask}
    menu_logo.cast_bronze(s, letters, pady, th, seed=31)
    from menu_ui import glow_image
    return s.image(), glow_image(W, H, letters, radius=2.0, gain=1.2)

def put_badge(canvas, badge, cx, top, width):
    """the DEMO plaque centred under the name (its top at `top`)"""
    h = round(badge[0].height * width / badge[0].width)
    put_logo(canvas, badge, cx, top + h / 2, width, glow_strength=0.35, shadow=0.5)

def community_icon():
    """46x46 native: dark enamel, a verdigrised bronze ring, the iron gear, fungi on top (shown at 4x)"""
    from menu_ui import Spr, gear, mycena, outline_parts, ORGANIC, BRONZE, ENAMEL, SEA, tone, L2, nA
    s = Spr(46, 46)
    c, cy, R = 23.0, 25.0, 20.0
    for y in range(46):
        for x in range(46):
            r = math.hypot(x + 0.5 - c, y + 0.5 - cy)
            if r > R: continue
            if r > R - 1: s.put(x, y, BRONZE[0], 'frame'); continue
            if r > R - 4:
                face = ((x + 0.5 - c) * L2[0] + (y + 0.5 - cy) * L2[1]) / r
                col_ = tone(BRONZE, 3.3 + 2.2 * face, x, y)
                if nA(x * 3 + 40, y * 3) > 0.6: col_ = tone(SEA, 1.6 + face, x, y)
                s.put(x, y, col_, 'frame'); continue
            s.put(x, y, tone(ENAMEL, 1.2 + (1 - r / (R - 4)) * 2.2, x, y), 'enamel')
    gear(s, c, cy + 1, 0.2, rb=10.5, teeth_h=3.0, n=12, spokes=6, seed=7)
    mycena(s, 16, cy - R + 3, 1, 7, -1, True)
    mycena(s, 24, cy - R + 1, 2, 9, 1, True)
    mycena(s, 31, cy - R + 3, 1, 5, 1, True)
    outline_parts(s, ORGANIC)
    return s.image()


# --- the art ----------------------------------------------------------------------------------------------------------
ART = Image.open(args.art).convert('RGB')

def crop_cover(w, h, fx=0.5, fy=0.5, zoom=1.0):
    """the largest crop of the art with the target's aspect (/zoom), centred on (fx, fy), resized to w x h"""
    aw, ah = ART.size
    r = w / h
    cw, ch = (aw, aw / r) if aw / ah < r else (ah * r, ah)
    cw, ch = cw / zoom, ch / zoom
    x0 = min(max(0, fx * aw - cw / 2), aw - cw)
    y0 = min(max(0, fy * ah - ch / 2), ah - ch)
    img = ART.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((w, h), Image.LANCZOS)
    return img.convert('RGBA')

def shade(img, top=0.0, bottom=0.0, centre=None, strength=0.6):
    """darken for the logo: a vertical gradient (top / bottom = alpha at the edges) and / or an ellipse around centre"""
    w, h = img.size
    m = Image.new('L', (w, h), 0); p = m.load()
    for y in range(h):
        t = y / (h - 1)
        v = top * max(0.0, 1 - t / 0.55) ** 1.5 + bottom * max(0.0, (t - 0.55) / 0.45) ** 1.5
        for x in range(w):
            vv = v
            if centre:
                cx, cy, rx, ry = centre
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                vv = max(vv, strength * max(0.0, 1 - d))
            p[x, y] = int(min(1, vv) * 255)
    dark = Image.new('RGBA', (w, h), (6, 8, 5, 0)); dark.putalpha(m)
    img.alpha_composite(dark)
    return img

def grade(img, contrast=1.15, colour=1.1, bright=1.12):
    rgb = img.convert('RGB')
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Color(rgb).enhance(colour)
    rgb = ImageEnhance.Brightness(rgb).enhance(bright)
    return rgb.convert('RGBA')

def save(img, name):
    path = os.path.join(args.out, name)
    img.convert('RGB').save(path, optimize=True)
    return path

# --- the formats ------------------------------------------------------------------------------------------------------
def build():
    store, short = make_logos()
    badge = demo_badge() if args.demo else None
    out = {}

    def titled(img, logo, cx, cy, width, badge_w, gap, **kw):
        """the name, and in the demo set the DEMO plaque under it"""
        if badge: cy -= (badge[0].height * badge_w / badge[0].width + gap) / 2   # keep the pair centred
        bottom = put_logo(img, logo, cx, cy, width, **kw)
        if badge: put_badge(img, badge, cx, bottom + gap, badge_w)

    # header capsule (store + library header): the egg cathedral and the spire under the name
    img = grade(crop_cover(920, 430, 0.45, 0.42))
    img = shade(img, top=0.75, bottom=0.25)
    titled(img, store, 460, 150 + (40 if badge else 0), 640, 210, 10)
    out['header_capsule_920x430.png'] = img
    out['library_header_920x430.png'] = img
    # small capsule: the name nearly fills it (the demo: a bit smaller, the plaque under it)
    img = grade(crop_cover(462, 174, 0.45, 0.30, zoom=1.15), bright=0.8)
    img = shade(img, top=0.5, bottom=0.5, centre=(231, 87, 260, 110), strength=0.55)
    titled(img, short, 231, 89, 360 if badge else 430, 150, 6, glow_strength=0.45)
    out['small_capsule_462x174.png'] = img
    # main capsule
    img = grade(crop_cover(1232, 706, 0.45, 0.45))
    img = shade(img, top=0.8, bottom=0.3)
    titled(img, store, 616, 205 + (45 if badge else 0), 820, 260, 14)
    out['main_capsule_1232x706.png'] = img
    # vertical capsule + library capsule: portrait around the cathedral door, the name on top
    img = grade(crop_cover(748, 896, 0.36, 0.5))
    img = shade(img, top=0.85, bottom=0.35)
    titled(img, store, 374, 170 + (40 if badge else 0), 680, 230, 12)
    out['vertical_capsule_748x896.png'] = img
    img = grade(crop_cover(600, 900, 0.36, 0.5))
    img = shade(img, top=0.85, bottom=0.35)
    titled(img, store, 300, 165 + (40 if badge else 0), 552, 200, 12)
    out['library_capsule_600x900.png'] = img
    # library hero: no text; the cathedral's lit door stays in the centred safe area
    img = grade(crop_cover(3840, 1240, 0.5, 0.56), contrast=1.05)
    img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=60, threshold=2))
    out['library_hero_3840x1240.png'] = img
    # page background: ambient, dark, soft
    img = crop_cover(1438, 810, 0.5, 0.5).filter(ImageFilter.GaussianBlur(3))
    img = grade(img, contrast=0.9, colour=0.7, bright=0.55)
    out['page_background_1438x810.png'] = img
    for name, im in out.items():
        save(im, name)
    # library logo: transparent, 1280 wide, with its halo + glow baked in so it reads over any hero
    lg = scale_pixels(store[0], 1180)
    bg_ = scale_pixels(badge[0], 360) if badge else None
    logo = Image.new('RGBA', (1280, lg.height + 60 + (bg_.height + 30 if badge else 0)), (0, 0, 0, 0))
    a = lg.getchannel('A').filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(14))
    halo = Image.new('RGBA', lg.size, (0, 0, 0, 0)); halo.putalpha(a.point(lambda v: int(v * 0.7)))
    gl = store[1].resize(lg.size, Image.BILINEAR)
    glow = Image.new('RGBA', lg.size, GLOW + (0,)); glow.putalpha(gl.getchannel('A').point(lambda v: int(v * 0.5)))
    for layer, dy in ((halo, 36), (glow, 30), (lg, 30)):
        logo.alpha_composite(layer, (50, dy))
    if badge:                                                       # the plaque under the name, same halo + glow
        by, bx = 30 + lg.height + 24, (1280 - bg_.width) // 2
        a = bg_.getchannel('A').filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(12))
        halo = Image.new('RGBA', bg_.size, (0, 0, 0, 0)); halo.putalpha(a.point(lambda v: int(v * 0.6)))
        glow = Image.new('RGBA', bg_.size, GLOW + (0,))
        glow.putalpha(badge[1].resize(bg_.size, Image.BILINEAR).getchannel('A').point(lambda v: int(v * 0.35)))
        for layer, dy in ((halo, 6), (glow, 0), (bg_, 0)):
            logo.alpha_composite(layer, (bx, by + dy))
    logo.save(os.path.join(args.out, 'library_logo_1280.png'), optimize=True)
    out['library_logo_1280.png'] = logo
    # community icon: the logo's gear in a bronze porthole, two glowing mycenas growing on the rim
    icon = scale_pixels(community_icon(), 184).convert('RGB')
    save(icon, 'community_icon_184x184.jpg')
    out['community_icon_184x184.jpg'] = icon
    # shortcut (client) icon: the same porthole as a Windows .ico, transparent outside the ring, 16..256 px
    ico = scale_pixels(community_icon(), 256)
    ico.save(os.path.join(args.out, 'shortcut_icon.ico'),
             sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    return out

def contact_sheet(out):
    sheet = Image.new('RGB', (1900, 1560), (27, 40, 56))           # Steam's page blue
    places = {
        'main_capsule_1232x706.png': (20, 20, 0.75), 'header_capsule_920x430.png': (960, 20, 0.95),
        'small_capsule_462x174.png': (960, 450, 1.0), 'vertical_capsule_748x896.png': (20, 560, 0.62),
        'library_capsule_600x900.png': (500, 560, 0.62), 'library_hero_3840x1240.png': (900, 660, 0.25),
        'page_background_1438x810.png': (900, 990, 0.35), 'library_logo_1280.png': (1420, 990, 0.35),
        'community_icon_184x184.jpg': (1450, 450, 1.0),
    }
    for name, (x, y, k) in places.items():
        im = out[name]
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        if im.mode == 'RGBA':
            bg = Image.new('RGBA', im.size, (60, 60, 60, 255)); bg.alpha_composite(im); im = bg
        sheet.paste(im.convert('RGB'), (x, y))
    sheet.save(os.path.join(args.out, '_contact_sheet.png'))

if __name__ == '__main__':
    o = build()
    contact_sheet(o)
    print('\n'.join(sorted(o)))
