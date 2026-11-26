"""Steam store + library artwork: Marti's main-menu painting (the key art) at night with the main menu's title, drawn
as the game's menu has it (--theme below; the jungle lintel by default), in every format Steamworks asks for.

  python3 tools/storeart/store_art.py [--theme jungle|brutal|vitraz|glow] [--art key_art.png] [--out dir] [--demo]

--theme: the main menu's look the title takes (ui/mainMenuBand.js themes):
       jungle (default, -> out/; the game's menu since 2026-11-24): the title on a crumbling concrete lintel with ivy
       and glowing mycelium (tools/artgen/menu_skins.py jungle_title, Bungee + Rubik), DEMO on a concrete plate hung on
       rusty wires, the icon a concrete gear with ivy and glowing mushrooms. The looks tried before it (see
       tools/menu_trials/README.md): brutal (-> out/brutal/: acid Space Grotesk / white Bebas Neue), vitraz
       (-> out/vitraz/: the title on a violet stained-glass plate, Morkezela in blackletter, Cinzel) or glow
       (-> out/glow/: neon MORKEZELA in Monoton, Comfortaa, on an indigo shade). The crops are the same; the title,
       the DEMO tag and the icons change.

--art: default tools/storeart/painting_scan.jpg = the scan of the finished painting (2026-11-26, A4 at 600 dpi, raw
       and portrait): flattened here by tools/artgen/menu_painting.py from_scan at 3920 x 2772 (2x the menu's
       1960 x 1386, so the 3840 px hero is sharp; not registered: the crops and POOLS are fractions). Any other image
       (e.g. key_art.jpg = the phone photo of 2026-11-23, still the menu band's reference) is used as it is.
--demo: the demo app's set (-> out/demo/): every capsule, the library capsule/header and the library logo carry an
       acid DEMO tag on the subtitle line (Steam: a demo's capsules / library assets must show it's a demo); the hero
       and the page background stay text-free.

Sizes and rules (partner.steamgames.com/doc/store/assets, .../libraryassets, checked 2026-10-30):
  store:   header 920x430, small 462x174 (the name nearly fills it), main 1232x706, vertical 748x896,
           page background 1438x810 (ambient, no text)
  library: capsule 600x900, header 920x430, hero 3840x1240 (NO text; keep the subject inside the centred 860x380
           safe area: Steam crops the rest when the window resizes), logo PNG with transparency, 1280 wide and/or 720 tall
  community icon 184x184, client (shortcut) icon .ico
  Capsules: the art + the game's title only: no quotes, review scores, "demo" / "wishlist" / sale text
  (except the demo app's own capsules, which must say "demo").
Each crop is a box in fractions of the painting (`crop`), so a scan at another resolution keeps the compositions.
soundtrack/build.py imports this module for the album cover (title(), put_title(), crop(), grade())."""
import argparse, math, os, random
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FONTS = os.path.join(ROOT, 'assets', 'fonts')
KEY_ART = os.path.join(ROOT, 'tools', 'storeart', 'painting_scan.jpg')
SUBTITLE = 'A WEIRD GAME'

ACID = (230, 255, 46, 255)          # ui/mainMenuBand.js ACID
WHITE = (255, 255, 255, 255)
GREY = (216, 216, 216, 255)         # the subtitle (#d8d8d8)
BLACK = (0, 0, 0, 255)
SS = 4                              # everything is drawn 4x and averaged down
THEMES = ['brutal', 'vitraz', 'glow', 'jungle']
THEME = 'jungle'                    # main() sets it from --theme; put_title() and icon() draw in it (OST cover too)

# The title's proportions in the menu's units (u): MORKEZELA is 262 u wide (createTopTitle TW). Measured off the
# 1920x1080 menu screenshot (tools/trailer/out/screenshots/25_main_menu.png): UPPER's caps end 9.5 u above
# MORKEZELA's, the rule's middle is 14.7 u under MORKEZELA's baseline, the subtitle's caps are centred on the rule.
TW = 262
UPPER_PX, UPPER_SPACING = 13, 9
SUB_PX, SUB_SPACING, SUB_X = 11, 4, 40
RULE_W, RULE_H = 30, 4
UPPER_GAP, RULE_DROP = 9.5, 14.7


def font(name, px, bold=False):
    f = ImageFont.truetype(os.path.join(FONTS, name), max(1, round(px)))
    if bold:
        f.set_variation_by_name('Bold')
    return f


def cap_height(f, ch='M'):
    return -f.getbbox(ch, anchor='ls')[1]


def spaced(draw, x, baseline, text, f, spacing, fill):
    """text drawn a letter at a time with `spacing` after each (Phaser's letterSpacing does the same)"""
    for ch in text:
        draw.text((x, baseline), ch, font=f, fill=fill, anchor='ls')
        x += f.getlength(ch) + spacing
    return x


def gear_mask(size, cx, cy, ro, teeth=10, hole=0.46, angle=0.0):
    """mainMenuBand.js gear(): trapezoid teeth round a disc, a hole in the middle; as an L mask"""
    m = Image.new('L', size, 0)
    d = ImageDraw.Draw(m)
    ri, step, pts = ro * 0.83, 2 * math.pi / teeth, []
    for i in range(teeth):
        a = i * step + math.radians(angle)
        for r, t in ((ri, -0.5), (ri, -0.24), (ro, -0.13), (ro, 0.13), (ri, 0.24)):
            pts.append((cx + math.cos(a + t * step) * r, cy + math.sin(a + t * step) * r))
    d.polygon(pts, fill=255)
    h = ro * hole
    d.ellipse((cx - h, cy - h, cx + h, cy + h), fill=0)
    return m


def title(width, subtitle=SUBTITLE, upper_scale=1.0, demo=False, angle=10):
    """the menu's title block, MORKEZELA `width` px wide, as RGBA (transparent around it, a margin of 8 u)"""
    u = width / TW * SS
    b100 = ImageFont.truetype(os.path.join(FONTS, 'BebasNeue.ttf'), 100)
    wM, wR, cap = b100.getlength('M'), b100.getlength('RKEZELA'), cap_height(b100)
    wO = cap * 1.08                                  # the gear's slot (gearTitle)
    k = TW * u / (wM + wO + wR)
    big = font('BebasNeue.ttf', 100 * k)
    cap_h = cap_height(big)
    up = font('SpaceGrotesk.ttf', UPPER_PX * u * upper_scale, bold=True)
    sub = font('SpaceGrotesk.ttf', SUB_PX * u, bold=True)
    pad = 8 * u
    y_upper = pad + cap_height(up, 'U')              # baselines, from the top
    y_mork = y_upper + UPPER_GAP * u + cap_h
    y_rule = y_mork + RULE_DROP * u
    tag = None
    if demo:                                         # an acid tag, DEMO in black, at the subtitle line's right end
        tf = font('BebasNeue.ttf', 23 * u)
        tw, th = tf.getlength('DEMO'), cap_height(tf, 'D')
        tag = (tf, tw + 12 * u, th + 9 * u)
    bottom = y_rule + max(RULE_H / 2 * u, cap_height(sub) / 2, tag[2] / 2 if tag else 0) + pad
    img = Image.new('RGBA', (math.ceil(TW * u + 2 * pad), math.ceil(bottom)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0 = pad
    spaced(d, x0, y_upper, 'UPPER', up, UPPER_SPACING * u * upper_scale, ACID)
    d.text((x0, y_mork), 'M', font=big, fill=WHITE, anchor='ls')
    d.text((x0 + (wM + wO) * k, y_mork), 'RKEZELA', font=big, fill=WHITE, anchor='ls')
    g = gear_mask(img.size, x0 + (wM + wO / 2) * k, y_mork - cap_h / 2, cap_h / 2, angle=angle)
    img.paste(Image.new('RGBA', img.size, WHITE), (0, 0), g)
    if subtitle:
        d.rectangle((x0, y_rule - RULE_H / 2 * u, x0 + RULE_W * u, y_rule + RULE_H / 2 * u), fill=ACID)
        spaced(d, x0 + SUB_X * u, y_rule + cap_height(sub, 'A') / 2, subtitle, sub, SUB_SPACING * u, GREY)
    if tag:
        tf, w_, h_ = tag
        x1 = x0 + TW * u
        d.rectangle((x1 - w_, y_rule - h_ / 2, x1, y_rule + h_ / 2), fill=ACID)
        d.text((x1 - w_ / 2, y_rule + cap_height(tf, 'D') / 2), 'DEMO', font=tf, fill=BLACK, anchor='ms')
    return img.resize((round(img.width / SS), round(img.height / SS)), Image.LANCZOS)


def soft_rect(w, h, alpha, colour=(0, 0, 0)):
    """createTopTitle's shade: black (or `colour`), its edges fading out (smoothstep over the outer third)"""
    def ramp(n):
        return [min(1.0, min(t, 1 - t) / 0.34) for t in ((i + 0.5) / n for i in range(n))]
    rx, ry = ramp(w), ramp(h)
    rx = [v * v * (3 - 2 * v) for v in rx]
    ry = [v * v * (3 - 2 * v) for v in ry]
    a = Image.new('L', (w, h))
    a.putdata([round(255 * alpha * vy * vx) for vy in ry for vx in rx])
    out = Image.new('RGBA', (w, h), tuple(colour) + (255,))
    out.putalpha(a)
    return out


def titled(width, shade=0.8, **kw):
    """the theme's title on its shade as one RGBA image centred on the title; `width` is Brutal's MORKEZELA width
    (the other themes scale theirs to a similar footprint); shade 0 = the title alone, cropped to it"""
    if THEME == 'vitraz':
        return glass_title(width * 1.12, shade=shade, **kw)
    if THEME == 'glow':
        return neon_title(width * 1.05, shade=shade, **kw)
    if THEME == 'jungle':
        return jungle_store_title(width * 1.1, shade=shade, **kw)
    t = title(width, **kw)
    if not shade:
        return t
    u = width / TW
    s = soft_rect(round(t.width + 94 * u), round(t.height + 86 * u), shade)   # the menu's: 424 x ~190 u round 262 u
    s.alpha_composite(t, (round((s.width - t.width) / 2), round((s.height - t.height) / 2)))
    return s


def put_title(canvas, cx, cy, width, shade=0.8, **kw):
    """the theme's title centred on (cx, cy) on its shade"""
    t = titled(width, shade, **kw)
    canvas.alpha_composite(t, (round(cx - t.width / 2), round(cy - t.height / 2)))
    return t


# --- Vitráž: stained glass (ui/mainMenuBand.js glassTitle / glassPane) -------------------------------------------------
LEAD = (23, 18, 31, 255)
GLASS = {
    'violet': [(107, 58, 160), (83, 44, 140), (128, 76, 178), (70, 40, 120)],
    'amber': [(240, 178, 60), (222, 150, 40), (250, 200, 90), (210, 130, 30)],
    'teal': [(42, 140, 140), (30, 118, 128), (60, 160, 150), (24, 100, 112)],
    'rose': [(201, 79, 124), (180, 60, 104), (220, 100, 140), (160, 50, 90)],
}
GLASS_GLOW = {'amber': (255, 198, 90), 'teal': (111, 230, 218), 'rose': (255, 143, 184), 'violet': (195, 155, 255)}


def pointed(w, h, tip, inset=4):
    """the menu's pointed pane outline (a stretched hexagon), in its own px"""
    return [(inset, h / 2), (tip, inset), (w - tip, inset), (w - inset, h / 2), (w - tip, h - inset), (tip, h - inset)]


def clip_half(poly, mx, my, nx, ny):
    """the part of a polygon on the side of the line through (mx, my) away from the normal (nx, ny)"""
    out = []
    for i, (ax, ay) in enumerate(poly):
        bx, by = poly[(i + 1) % len(poly)]
        da, db = (ax - mx) * nx + (ay - my) * ny, (bx - mx) * nx + (by - my) * ny
        if da <= 0:
            out.append((ax, ay))
        if (da <= 0) != (db <= 0):
            t = da / (da - db)
            out.append((ax + t * (bx - ax), ay + t * (by - ay)))
    return out


def voronoi(w, h, seeds, ay=1.4):
    """the cells (polygons) of the seeds in a w x h box, distance with y weighted by ay (glassPane's 1.4)"""
    cells = []
    for i, (px, py) in enumerate(seeds):
        poly = [(0, 0), (w, 0), (w, h * ay), (0, h * ay)]
        for j, (qx, qy) in enumerate(seeds):
            if i != j and poly:
                poly = clip_half(poly, (px + qx) / 2, (py + qy) * ay / 2, qx - px, (qy - py) * ay)
        cells.append([(x, y / ay) for x, y in poly])
    return cells


def glass(W, H, shape, palette, seed, n, k, light=0.28, lead=7):
    """glassPane in PIL: W x H px, `shape` a polygon in menu px (k px each) filled with n glass cells, lead seams
    2 menu px wide, light through the middle, `lead` menu px of lead round the edge"""
    w, h = W * SS, H * SS
    r = random.Random(seed)
    seeds = [(r.random() * w, r.random() * h) for _ in range(n)]
    looks = [(r.choice(palette), 0.85 + r.random() * 0.3) for _ in range(n)]
    img = Image.new('RGBA', (w, h), LEAD)
    d = ImageDraw.Draw(img)
    cells = voronoi(w, h, seeds)
    for (col, b), cell in zip(looks, cells):
        if len(cell) > 2:
            d.polygon(cell, fill=tuple(min(255, round(c * b)) for c in col) + (255,))
    seam = max(1, round(2 * k * SS))
    for cell in cells:
        if len(cell) > 2:
            d.line(cell + [cell[0]], fill=LEAD, width=seam, joint='curve')
    # the streaks in the glass (glassPane's sin(x * 0.07 + y * 0.11)), and the light through the middle
    sw, sh = max(2, round(W / k)), max(2, round(H / k))
    streak = Image.new('L', (sw, sh))
    streak.putdata([round(235 + 20 * math.sin(x * 0.07 + y * 0.11)) for y in range(sh) for x in range(sw)])
    rgb = ImageChops.multiply(img.convert('RGB'), streak.resize((w, h), Image.BILINEAR).convert('RGB'))
    R = max(w, h) * 0.6
    g = Image.new('L', (64, 64))
    g.putdata([round(255 * light * max(0.0, 1 - math.hypot(x - 31.5, y - 31.5) / 32)) for y in range(64) for x in range(64)])
    lit = Image.new('L', (w, h), 0)
    lit.paste(g.resize((round(2 * R), round(2 * R)), Image.BILINEAR), (round(w / 2 - R), round(h * 0.35 - R)))
    rgb = Image.composite(Image.new('RGB', (w, h), (255, 255, 230)), rgb, lit)
    pts = [(x * k * SS, y * k * SS) for x, y in shape]
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out.paste(rgb, (0, 0), mask)
    if lead:
        ImageDraw.Draw(out).line(pts + [pts[0]], fill=LEAD, width=max(1, round(lead * k * SS)), joint='curve')
    return out.resize((W, H), Image.LANCZOS)


def text_w(f, text, spacing=0):
    return sum(f.getlength(ch) + spacing for ch in text) - spacing


def centred(d, cx, cy, text, f, fill, spacing=0, **kw):
    """text centred on (cx, cy) (the middle of the ascender/descender like a centred Phaser text), letter-spaced"""
    if not spacing:
        d.text((cx, cy), text, font=f, fill=fill, anchor='mm', **kw)
        return
    x = cx - text_w(f, text, spacing) / 2
    for ch in text:
        d.text((x, cy), ch, font=f, fill=fill, anchor='lm', **kw)
        x += f.getlength(ch) + spacing


def glass_title(width, subtitle=SUBTITLE, demo=False, shade=0.8, **_):
    """glassTitle: the violet glass plate (`width` px wide), U P P E R + Morkezela in gold blackletter on it, the
    subtitle on a lead strip across its foot, a soft shadow; demo: an amber pane with DEMO under it"""
    PW, PH, M = 452, 104, 56                               # the menu's plate, and a margin for the shadow
    k = width / PW
    below = (16 if subtitle else 0) + (44 if demo else 0)
    lift = 44 if demo else 0                               # the same room above: the plate stays put, DEMO hangs below
    W, H = round((PW + 2 * M) * k), round((PH + 2 * M + below + lift) * k)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ox, oy = M, M + lift
    if shade:
        s = soft_rect(round((PW + 90) * k), round((PH + 70 + below) * k), min(1.0, 0.75 * shade / 0.8))
        img.alpha_composite(s, (round((ox + PW / 2) * k - s.width / 2), round((oy + PH / 2 + 6 + below / 2) * k - s.height / 2)))
    img.alpha_composite(glass(round(PW * k), round(PH * k), pointed(PW, PH, 34), GLASS['violet'], 11, 40, k, lead=6),
                        (round(ox * k), round(oy * k)))
    d = ImageDraw.Draw(img)
    cx = (ox + PW / 2) * k
    centred(d, cx, (oy + 20) * k, 'U P P E R', font('Cinzel.ttf', 13 * k, bold=True), '#fbeec8',
            stroke_width=max(1, round(2 * k)), stroke_fill=LEAD)
    centred(d, cx, (oy + 58) * k, 'Morkezela', font('UnifrakturMaguntia.ttf', 54 * k), '#ffcf5a',
            stroke_width=max(1, round(3.5 * k)), stroke_fill=LEAD)
    if subtitle:
        sf = font('Cinzel.ttf', 10 * k, bold=True)
        sy = (oy + PH + 4) * k
        sw = text_w(sf, subtitle, 2 * k) + 34 * k
        d.rectangle((cx - sw / 2, sy - 10 * k, cx + sw / 2, sy + 10 * k), fill=LEAD)
        centred(d, cx, sy, subtitle, sf, '#e8d9ff', spacing=2 * k)
    if demo:
        tf = font('Cinzel.ttf', 16 * k, bold=True)
        dw, dh = text_w(tf, 'DEMO', 2 * k) + 50 * k, 32 * k
        dy = (oy + PH + (16 if subtitle else 0) + 24) * k
        pane = glass(round(dw), round(dh), pointed(dw / k, dh / k, 14), GLASS['amber'], 5, 6, k, lead=4)
        img.alpha_composite(pane, (round(cx - dw / 2), round(dy - dh / 2)))
        centred(d, cx, dy, 'DEMO', tf, '#fff6dc', spacing=2 * k, stroke_width=max(1, round(2 * k)), stroke_fill=LEAD)
    return img if shade else img.crop(img.getbbox())


# --- Bioluminiscence: neon (ui/mainMenuBand.js neonTitle) ----------------------------------------------------------------
CYAN, MAGENTA, NEON_VIOLET, NIGHT = (94, 242, 255), (255, 79, 216), (157, 123, 255), (7, 4, 26)


def glow_layer(img, mask, colour, strength, dist):
    """preFX addGlow, roughly: the mask blurred near and far, in `colour`, over img"""
    near = mask.filter(ImageFilter.GaussianBlur(dist * 0.35)).point(lambda v: min(255, round(v * 0.55 * strength)))
    far = mask.filter(ImageFilter.GaussianBlur(dist)).point(lambda v: min(255, round(v * 0.45 * strength)))
    g = Image.new('RGBA', img.size, colour + (0,))
    g.putalpha(ImageChops.add(near, far))
    img.alpha_composite(g)


def neon_text(img, cx, cy, text, f, fill, colour, strength, dist, spacing=0):
    m = Image.new('L', img.size, 0)
    centred(ImageDraw.Draw(m), cx, cy, text, f, 255, spacing=spacing)
    glow_layer(img, m, colour, strength, dist)
    t = Image.new('RGBA', img.size, fill)
    t.putalpha(m)
    img.alpha_composite(t)


def neon_title(width, subtitle=SUBTITLE, demo=False, shade=0.8, **_):
    """neonTitle: U P P E R in magenta, MORKEZELA (`width` px) a near-white Monoton tube in a cyan glow, the subtitle
    in lower case, on two indigo shades; demo: DEMO in a magenta neon frame under it"""
    w56 = ImageFont.truetype(os.path.join(FONTS, 'Monoton.ttf'), 56).getlength('MORKEZELA')
    k = width / w56
    tw = w56 + 32                                          # Phaser's text width (16 px padding a side)
    below = 46 if demo else 0
    W, H = round((tw + 170) * k), round((230 + 2 * below) * k)   # (as much room above as DEMO takes below)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    cx, top = W / 2, (115 - 60 + below) * k                 # the big shade (210 high) centred 60 below the top
    if shade:
        a = shade / 0.8
        for sw, sh, al in ((tw + 150, 210 + below, 0.9), (tw + 30, 120 + below, 0.75)):
            s = soft_rect(round(sw * k), round(sh * k), min(1.0, al * a), NIGHT)
            img.alpha_composite(s, (round(cx - s.width / 2), round(top + (60 + below / 2) * k - s.height / 2)))
    neon_text(img, cx, top + 12 * k, 'U P P E R', font('Comfortaa.ttf', 13 * k, bold=True), (255, 143, 230, 255), MAGENTA, 2.5, 7 * k)
    neon_text(img, cx, top + 56 * k, 'MORKEZELA', font('Monoton.ttf', 56 * k), (226, 253, 255, 255), CYAN, 2.8, 9 * k)
    if subtitle:
        d = ImageDraw.Draw(img)
        centred(d, cx, top + 104 * k, subtitle.lower(), font('Comfortaa.ttf', 13 * k, bold=True), '#d8ceff', spacing=4 * k)
    if demo:
        tf = font('Comfortaa.ttf', 15 * k, bold=True)
        dy = top + (104 + 36) * k if subtitle else top + 110 * k
        bw, bh = text_w(tf, 'DEMO', 3 * k) + 30 * k, 28 * k
        m = Image.new('L', img.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((cx - bw / 2, dy - bh / 2, cx + bw / 2, dy + bh / 2), radius=8 * k, outline=255, width=max(1, round(2 * k)))
        glow_layer(img, m, MAGENTA, 3, 6 * k)
        frame = Image.new('RGBA', img.size, (255, 190, 240, 255))
        frame.putalpha(m)
        img.alpha_composite(frame)
        neon_text(img, cx, dy, 'DEMO', tf, (255, 220, 248, 255), MAGENTA, 2.5, 6 * k, spacing=3 * k)
    return img if shade else img.crop(img.getbbox())


# --- the art ----------------------------------------------------------------------------------------------------------
def load_art(path=KEY_ART):
    img = Image.open(path).convert('RGB')
    if os.path.basename(path).startswith('painting_scan'):        # the raw scan: flattened first
        import sys
        sys.path.insert(0, os.path.join(ROOT, 'tools', 'artgen'))
        import menu_painting
        img = menu_painting.from_scan(img, scale=2)
    return img


def extend_top(art, frac, fade=0.12):
    """the painting with `frac` of its height of black added above it, its top edge (`fade` of the height) fading
    into it: room for the title above the cathedral's spire in the portrait formats (the painting's top is dark
    smoke, so the seam doesn't show)"""
    aw, ah = art.size
    e, n = round(ah * frac), max(1, round(ah * fade))
    out = Image.new('RGB', (aw, ah + e), (0, 0, 0))
    a = Image.new('L', (1, ah), 255)
    a.putdata([round(255 * min(1.0, y / n) ** 1.5) for y in range(ah)])
    out.paste(art, (0, e), a.resize((aw, ah)))
    return out


def crop(art, w, h, x0=0.0, y0=0.0, x1=1.0):
    """the w:h box from x0 to x1 (fractions of the painting's width), its top at y0 (a fraction of the height; pulled
    up if the box would run off the bottom), resized to w x h"""
    aw, ah = art.size
    cw = (x1 - x0) * aw
    ch = cw * h / w
    if ch > ah:                                     # too tall: the full height, the width centred on the box
        ch, cx = ah, (x0 + x1) / 2 * aw
        cw = ch * w / h
        x0 = max(0, min(aw - cw, cx - cw / 2)) / aw
    top = min(y0 * ah, ah - ch)
    box = (x0 * aw, top, x0 * aw + cw, top + ch)
    return art.resize((w, h), Image.LANCZOS, box=box).convert('RGBA')


def grade(img, contrast=1.06, colour=1.05, bright=1.0):
    rgb = img.convert('RGB')
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Color(rgb).enhance(colour)
    rgb = ImageEnhance.Brightness(rgb).enhance(bright)
    return rgb.convert('RGBA')


def top_shade(img, depth=0.45, alpha=0.55):
    """a dark gradient from the top edge down to `depth` of the height (the title sits in the smoke up there)"""
    w, h = img.size
    n = max(1, round(h * depth))
    a = Image.new('L', (1, h), 0)
    a.putdata([round(255 * alpha * max(0.0, 1 - y / n) ** 1.6) for y in range(h)])
    dark = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    dark.putalpha(a.resize((w, h)))
    img.alpha_composite(dark)
    return img


# --- night: the painting dimmed (the paper reads too bright on a dark store page), a few things still lit ----------
AT_NIGHT = True
POOLS = [  # light that stays: (cx, cy, rx, ry) as fractions of the painting's width / height, strength
    (0.17, 0.40, 0.17, 0.30, 1.0),      # the Egg Cathedral's shell
    (0.55, 0.30, 0.16, 0.16, 0.55),     # the green haze over the cemetery
    (0.92, 0.50, 0.07, 0.10, 0.7),      # the clock spider
    (0.16, 0.82, 0.07, 0.14, 0.45),     # the bear
    (0.89, 0.80, 0.06, 0.15, 0.45)]     # Edgar


def pools(size):
    """the POOLS as one soft L mask"""
    w, h = size
    m = Image.new('L', size, 0)
    for cx, cy, rx, ry, k in POOLS:
        pw, ph = round(2 * rx * w), round(2 * ry * h)
        g = Image.radial_gradient('L').resize((pw, ph), Image.BILINEAR)
        g = g.point(lambda x, k=k: round(255 * k * (1 - min(1, x / 255)) ** 1.5))
        layer = Image.new('L', size, 0)
        layer.paste(g, (round(cx * w - pw / 2), round(cy * h - ph / 2)))
        m = ImageChops.add(m, layer)
    return m.filter(ImageFilter.GaussianBlur(w / 80))


def night(art, gamma=1.85, paper=0.75, tint=(168, 166, 214), sat=1.3, light=0.78, halo=0.2):
    """the whole painting at night: mids down (gamma), the bare paper (bright + grey) sunk furthest into indigo, a
    cool tint, the colour pushed back up; the POOLS keep the day's light, with a faint halo so they read as lit"""
    rgb = art.convert('RGB')
    d = rgb.point([round(255 * (i / 255) ** gamma) for i in range(256)] * 3)
    _, s, v = d.convert('HSV').split()
    m = ImageChops.multiply(v, ImageChops.invert(s)).point(lambda x: round(255 * paper * (x / 255) ** 1.2))
    d = Image.composite(ImageChops.multiply(d, Image.new('RGB', d.size, (64, 56, 98))), d, m)
    d = ImageChops.multiply(d, Image.new('RGB', d.size, tint))
    d = ImageEnhance.Color(d).enhance(sat)
    p = pools(rgb.size)
    out = Image.composite(rgb, d, p.point(lambda x: round(x * light)))
    glow = ImageChops.multiply(Image.merge('RGB', (p, p, p)), Image.new('RGB', d.size, (120, 110, 150)))
    return Image.blend(out, ImageChops.screen(out, glow.filter(ImageFilter.GaussianBlur(art.width / 40))), halo)


def vignette(img, k=0.5):
    """darker edges and corners (per format, so after the crop); a no-op by day"""
    if not AT_NIGHT:
        return img
    g = Image.radial_gradient('L').resize(img.size, Image.BILINEAR)
    f = g.point(lambda x: round(255 * (1 - k * min(1, x / 255) ** 2.4)))
    return ImageChops.multiply(img.convert('RGB'), Image.merge('RGB', (f, f, f))).convert('RGBA')


# --- the icons ----------------------------------------------------------------------------------------------------------
SHROOMS = [  # mainMenuBand.js SHROOMS: (w, h, polygon in fractions) a mycena bell, a round cap, a flat cap
    (14, 24, 'bell'), (16, 18, 'round'), (20, 14, 'flat')]


def shroom(d, kind, fx, fy, k, fill):
    """one flat mushroom silhouette, its stem's foot at (fx, fy), k px per menu px"""
    w, h, form = SHROOMS[kind]
    x0, y0 = fx - w * k / 2, fy - h * k

    def P(x, y):
        return (x0 + x * k, y0 + y * k)
    stem = {'bell': (1.5, 0.4), 'round': (2, 0.45), 'flat': (2, 0.35)}[form]
    d.rectangle((*P(w / 2 - stem[0], h * stem[1]), *P(w / 2 + stem[0], h)), fill=fill)
    if form == 'bell':        # quadratic curve from (1, .46h) through control (w/2, -.12h) to (w-1, .46h)
        pts = [P(1 + (w - 2) * t, (1 - t) ** 2 * h * 0.46 + 2 * (1 - t) * t * -h * 0.12 + t * t * h * 0.46)
               for t in (i / 24 for i in range(25))]
    elif form == 'round':     # the top half of an ellipse
        pts = [P(w / 2 + math.cos(a) * (w / 2 - 1), h * 0.45 - math.sin(a) * h * 0.38)
               for a in (math.pi * i / 24 for i in range(25))]
    else:
        pts = [P(1 + (w - 2) * t, (1 - t) ** 2 * h * 0.42 + 2 * (1 - t) * t * -h * 0.05 + t * t * h * 0.42)
               for t in (i / 24 for i in range(25))] + [P(w - 3, h * 0.5), P(3, h * 0.5)]
    d.polygon(pts, fill=fill)


def icon(size, rounded=False):
    """the community / client icon in the theme"""
    return {'vitraz': icon_vitraz, 'glow': icon_glow, 'jungle': icon_jungle}.get(THEME, icon_brutal)(size, rounded)


def gear_points(cx, cy, ro, teeth=10, angle=0.0):
    ri, step, pts = ro * 0.83, 2 * math.pi / teeth, []
    for i in range(teeth):
        a = i * step + math.radians(angle)
        for r, t in ((ri, -0.5), (ri, -0.24), (ro, -0.13), (ro, 0.13), (ri, 0.24)):
            pts.append((cx + math.cos(a + t * step) * r, cy + math.sin(a + t * step) * r))
    return pts


def icon_tile(S, rounded, fill):
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if rounded:
        d.rounded_rectangle((0, 0, S - 1, S - 1), radius=S * 0.16, fill=fill)
    else:
        d.rectangle((0, 0, S, S), fill=fill)
    return img, d


def icon_vitraz(size, rounded=False):
    """a round stained-glass window in lead, the title's gear in gold on it, glass-coloured mushrooms on its rim"""
    img, d = icon_tile(size, rounded, LEAD)
    cx, cy, R = size * 0.5, size * 0.58, size * 0.34
    k = size / 184
    ring = [(R + math.cos(a) * R * 0.96, R + math.sin(a) * R * 0.96) for a in (2 * math.pi * i / 72 for i in range(72))]
    pal = GLASS['violet'] * 3 + GLASS['teal'] + GLASS['rose'][:2]
    roundel = glass(round(2 * R), round(2 * R), [(x / k, y / k) for x, y in ring], pal, 21, 26, k, light=0.3, lead=5)
    img.alpha_composite(roundel, (round(cx - R), round(cy - R)))
    S = size * SS
    big = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(big)
    pts = gear_points(cx * SS, cy * SS, R * 0.55 * SS)
    bd.line(pts + [pts[0]], fill=LEAD, width=round(4 * k * SS), joint='curve')
    bd.polygon(pts, fill=(226, 180, 72, 255))
    h = R * 0.55 * 0.46 * SS
    bd.ellipse((cx * SS - h, cy * SS - h, cx * SS + h, cy * SS + h), fill=LEAD)
    for (kind, a, scale), hue in zip(((1, -112, 1.8), (0, -82, 2.2), (2, -52, 1.7)), ('amber', 'teal', 'rose')):
        r = math.radians(a)
        shroom(bd, kind, (cx + math.cos(r) * R * 0.94) * SS, (cy + math.sin(r) * R * 0.94 + 1.5 * k) * SS, k * SS * scale,
               GLASS_GLOW[hue] + (255,))
    img.alpha_composite(big.resize((size, size), Image.LANCZOS))
    return img


def icon_glow(size, rounded=False):
    """the title's gear as a cyan neon outline on deep indigo, neon mushrooms growing off its rim"""
    img, d = icon_tile(size, rounded, (13, 8, 38, 255))
    cx, cy, ro = size * 0.5, size * 0.6, size * 0.3
    k = size / 184
    S = size * SS
    m = Image.new('L', (S, S), 0)
    md = ImageDraw.Draw(m)
    pts = gear_points(cx * SS, cy * SS, ro * SS)
    md.line(pts + [pts[0]], fill=255, width=round(3.2 * k * SS), joint='curve')
    h = ro * 0.46 * SS
    md.ellipse((cx * SS - h, cy * SS - h, cx * SS + h, cy * SS + h), outline=255, width=round(3.2 * k * SS))
    m = m.resize((size, size), Image.LANCZOS)
    glow_layer(img, m, CYAN, 3, 6 * k)
    core = Image.new('RGBA', (size, size), (210, 252, 255, 255))
    core.putalpha(m)
    img.alpha_composite(core)
    for (kind, a, scale), col in zip(((1, -112, 2.0), (0, -82, 2.6), (2, -52, 1.9)), (CYAN, MAGENTA, NEON_VIOLET)):
        r = math.radians(a)
        sm = Image.new('L', (S, S), 0)
        shroom(ImageDraw.Draw(sm), kind, (cx + math.cos(r) * ro * 0.95) * SS, (cy + math.sin(r) * ro * 0.95 - 1 * k) * SS,
               k * SS * scale, 255)
        sm = sm.resize((size, size), Image.LANCZOS)
        glow_layer(img, sm, col, 2.5, 5 * k)
        c = Image.new('RGBA', (size, size), tuple(min(255, v + 90) for v in col) + (255,))
        c.putalpha(sm)
        img.alpha_composite(c)
    return img


def icon_brutal(size, rounded=False):
    """the title's gear, white on black, three acid mushrooms growing off its rim"""
    S = size * SS
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if rounded:
        d.rounded_rectangle((0, 0, S - 1, S - 1), radius=S * 0.16, fill=BLACK)
    else:
        d.rectangle((0, 0, S, S), fill=BLACK)
    cx, cy, ro = S * 0.5, S * 0.6, S * 0.3
    # a soft acid glow where the mushrooms grow (the menu's clump glows too)
    glow = Image.new('L', img.size, 0)
    gx, gy = cx + S * 0.06, cy - ro - S * 0.06
    ImageDraw.Draw(glow).ellipse((gx - S * 0.26, gy - S * 0.2, gx + S * 0.26, gy + S * 0.2), fill=90)
    glow = glow.filter(ImageFilter.GaussianBlur(S * 0.07))
    img.paste(Image.new('RGBA', img.size, ACID), (0, 0), glow)
    img.paste(Image.new('RGBA', img.size, WHITE), (0, 0), gear_mask(img.size, cx, cy, ro, angle=0))
    k = S / 184
    for kind, a, scale in ((1, -112, 2.0), (0, -82, 2.6), (2, -52, 1.9)):       # the stems' feet on the rim
        r = math.radians(a)
        shroom(d, kind, cx + math.cos(r) * ro * 0.86, cy + math.sin(r) * ro * 0.86 + 1.5 * k, k * scale, ACID)
    return img.resize((size, size), Image.LANCZOS)


# --- Městská džungle: the menu's title (tools/artgen/menu_skins.py jungle_title) drawn big ---------------------------
def skins():
    import sys
    sys.path.insert(0, os.path.join(ROOT, 'tools', 'artgen'))
    import menu_skins
    return menu_skins


def jungle_store_title(width, subtitle=SUBTITLE, demo=False, shade=0.8, **_):
    """the concrete lintel (`width` px wide) with the peeling sign letters, ivy and glowing mycelium; demo: a concrete
    plate with DEMO hanging under it (the same room added above, so the lintel stays where it was)"""
    ms = skins()
    k = width / 470
    t = ms.jungle_title(k, subtitle=subtitle, demo=demo)
    if demo:
        pad = Image.new('RGBA', (t.width, t.height + round(46 * k)), (0, 0, 0, 0))
        pad.alpha_composite(t, (0, round(46 * k)))
        t = pad
    if not shade:
        return t.crop(t.getbbox())
    s = soft_rect(round(t.width + 60 * k), round(t.height + 40 * k), min(1.0, shade * 0.95))
    s.alpha_composite(t, (round((s.width - t.width) / 2), round((s.height - t.height) / 2)))
    return s


def icon_jungle(size, rounded=False):
    """the title's gear cast in weathered concrete on a dark concrete tile, ivy over it, mould colonies glowing on its
    cracks (as the menu's slabs: thin threads read as sparks), three little glowing mushrooms on its rim"""
    ms = skins()
    S = size * SS
    k = S / 184 * 0.55
    rnd = random.Random(9)
    bg, bg_paths = ms.concrete(S, S, 71, cracks=3, spall=False, moss=0.45, k=k)
    bg = ms.mul(bg, Image.new('L', (S, S), 120)).convert('RGBA')
    cx, cy, ro = S * 0.5, S * 0.6, S * 0.3
    gm = gear_mask((S, S), cx, cy, ro, angle=8)
    sh = Image.new('L', (S, S), 0)
    sh.paste(gm, (round(S * 0.02), round(S * 0.03)))
    bg.alpha_composite(ms.glow(sh, (0, 0, 0), S * 0.02, 1.2))
    face, paths = ms.concrete(S, S, 72, cracks=4, spall=False, moss=0.35, k=k)
    face = ms.lit(face, ms.relief(gm, 3.0, S * 0.006))
    bg.paste(face, (0, 0), gm)
    on = lambda p: gm.getpixel((int(min(S - 1, max(0, p[0]))), int(min(S - 1, max(0, p[1]))))) > 0
    seeds = [p for p in ms.along_cracks(paths, every=4) if on(p)]
    # (the face has few cracks: the rest take hold on the rim, more of them on the shady lower left)
    while len(seeds) < 40:
        a, r = rnd.uniform(0.3, 2.9) + (rnd.random() < 0.6) * 1.2, rnd.uniform(0.62, 0.95) * ro
        p = (cx + math.cos(a) * r, cy + math.sin(a) * r)
        if on(p):
            seeds.append(p)
    myc = ms.colonies(S, S, rnd, [seeds[rnd.randrange(len(seeds))] for _ in range(14)], k * 1.6, size=(9, 17))
    myc = myc.filter(ImageFilter.GaussianBlur(S * 0.002)).point(lambda v: min(255, v * 1.4))
    myc = ImageChops.multiply(myc, gm.filter(ImageFilter.MinFilter(5)))
    bg.alpha_composite(ms.glow(myc, ms.MINT, S * 0.012, 1.6))
    bg.paste((200, 255, 222), (0, 0), myc.point(lambda v: v * 0.7))
    over = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    ms.ivy_curtain(over, rnd, S, 0, 9, S * 0.55 / (k * 1.6), (0, S * 0.45), k * 1.6)
    bg.alpha_composite(over)
    # the glow where the mushrooms grow, and the mushrooms
    g = Image.new('L', (S, S), 0)
    gx, gy = cx + S * 0.06, cy - ro - S * 0.06
    ImageDraw.Draw(g).ellipse((gx - S * 0.24, gy - S * 0.18, gx + S * 0.24, gy + S * 0.18), fill=110)
    bg.paste(Image.new('RGBA', (S, S), ms.MINT + (255,)), (0, 0), g.filter(ImageFilter.GaussianBlur(S * 0.07)))
    d = ImageDraw.Draw(bg)
    kk = S / 184
    for kind, a, scale, col in ((1, -112, 2.0, (150, 255, 196)), (0, -82, 2.6, (232, 255, 240)), (2, -52, 1.9, (95, 214, 160))):
        r = math.radians(a)
        shroom(d, kind, cx + math.cos(r) * ro * 0.86, cy + math.sin(r) * ro * 0.86 + 1.5 * kk, kk * scale, col)
    if rounded:
        m = Image.new('L', (S, S), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, S - 1, S - 1), radius=S * 0.16, fill=255)
        bg.putalpha(m)
    return bg.resize((size, size), Image.LANCZOS)


# --- the formats ------------------------------------------------------------------------------------------------------
def build(art, demo):
    out = {}
    kw = dict(demo=demo)
    art = night(art) if AT_NIGHT else art
    # header capsule (store + library header): the skyline, the title in the smoke between the spire and the Scraper
    # (x from 70 to 1870 of 1960: the airship whole, the cut just above Edgar's ears and Ortolan's hair)
    img = top_shade(vignette(grade(crop(art, 920, 430, 0.036, 0.0, 0.954))), 0.5, 0.35)
    put_title(img, 470, 112, 470, **kw)
    out['header_capsule_920x430.png'] = out['library_header_920x430.png'] = img
    # small capsule: the name nearly fills it, no subtitle (a demo keeps the line for its tag)
    img = top_shade(vignette(grade(crop(art, 462, 174, 0.12, 0.02, 0.88), bright=0.85), 0.3), 1.0, 0.45)
    # (vitraz / glow hang the DEMO tag under the title: smaller and higher there, so the tag stays inside)
    hang = demo and THEME != 'brutal'
    put_title(img, 231, 66 if hang else 87, 290 if hang else 330 if demo else 372, shade=0.75,
              subtitle=SUBTITLE if demo else None, upper_scale=1.5, **kw)
    out['small_capsule_462x174.png'] = img
    # main capsule: the whole skyline and the two at the balustrade
    img = top_shade(vignette(grade(crop(art, 1232, 706, 0.0, 0.0, 1.0))), 0.5, 0.35)
    put_title(img, 632, 158, 600, **kw)
    out['main_capsule_1232x706.png'] = img
    # vertical capsule + library capsule: portrait, the Egg Cathedral and Edgar, the title in the smoke on top
    # (the painting is too short for both the title and the spire: black above it, the title in the dark;
    # the full height, so Edgar keeps his feet)
    tall = extend_top(art, 0.14)
    img = top_shade(vignette(grade(crop(tall, 748, 896, 0.0, 0.0, 0.69))), 0.35, 0.3)
    put_title(img, 374, 112, 540, **kw)
    out['vertical_capsule_748x896.png'] = img
    img = top_shade(vignette(grade(crop(tall, 600, 900, 0.0, 0.0, 0.55))), 0.35, 0.3)
    put_title(img, 300, 106, 480, **kw)
    out['library_capsule_600x900.png'] = img
    # library hero: no text; from the spire's tip down to the cathedral's door, the cemetery in the centred safe area
    img = vignette(grade(crop(art, 3840, 1240, 0.0, 0.135, 1.0)), 0.3)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=50, threshold=2))
    out['library_hero_3840x1240.png'] = img
    # page background: ambient, dark, soft
    img = grade(crop(art, 1438, 810, 0.0, 0.1, 1.0).filter(ImageFilter.GaussianBlur(3)), 0.9, 0.7, 0.7 if AT_NIGHT else 0.45)
    out['page_background_1438x810.png'] = img
    # library logo: transparent, 1280 wide, the soft shade baked in so it reads over any part of the hero
    t = titled(1060, 0, **kw)
    logo = Image.new('RGBA', (1280, min(720, t.height + 120)), (0, 0, 0, 0))
    put_title(logo, 640, logo.height / 2, 1060, shade=0.6, **kw)
    out['library_logo_1280.png'] = logo
    out['community_icon_184x184.jpg'] = icon(184)
    return out


def save_all(out, folder):
    os.makedirs(folder, exist_ok=True)
    for name, im in out.items():
        path = os.path.join(folder, name)
        if name.endswith('.png') and name.startswith('library_logo'):
            im.save(path, optimize=True)
        else:
            im.convert('RGB').save(path, quality=95, optimize=True)
    # client (shortcut) icon: the same gear on a rounded black tile, 16..256 px
    icon(256, rounded=True).save(os.path.join(folder, 'shortcut_icon.ico'),
                                 sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


def contact_sheet(out, folder):
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
            bg = Image.new('RGBA', im.size, (60, 60, 60, 255))
            bg.alpha_composite(im)
            im = bg
        sheet.paste(im.convert('RGB'), (x, y))
    sheet.save(os.path.join(folder, '_contact_sheet.png'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--art', default=KEY_ART)
    ap.add_argument('--out', default=None)
    ap.add_argument('--demo', action='store_true', help="the demo app's set: a DEMO tag on the subtitle line")
    ap.add_argument('--theme', choices=THEMES, default='jungle', help="the menu look of the title and icons")
    ap.add_argument('--day', action='store_true', help="the painting as it is (no night grade)")
    args = ap.parse_args()
    global THEME, AT_NIGHT
    THEME, AT_NIGHT = args.theme, not args.day
    folder = args.out or os.path.join(ROOT, 'tools', 'storeart', 'out', *([] if THEME == 'jungle' else [THEME]),
                                      *(['demo'] if args.demo else []))
    out = build(load_art(args.art), args.demo)
    save_all(out, folder)
    contact_sheet(out, folder)
    print('\n'.join(sorted(out) + ['shortcut_icon.ico']))


if __name__ == '__main__':
    main()
