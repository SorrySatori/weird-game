"""The main menu's title: "UPPER MORKEZELA" cast in weathered bronze (URW Bookman Demi, pixel-snapped and re-shaded),
the O of MORKEZELA is an iron gear that turns; mushrooms grow on the letters, mycelium drapes over them and pulses.
Shown at 2x by MainScene (utils/menuKit.js).

  menu_logo.png       8 frames of 344x100 (the gear turns 60 deg = one spoke period over the loop, the pulse runs along
                      the mycelium) -- the anim loops seamlessly
  menu_logo_glow.png  soft white halo of the glowing parts (ADD, tinted + breathing in the game)
  menu_logo_store.png (+_glow)  one still frame with 'A WEIRD GAME' under the name, for the Steam art (tools/storeart)

python3 menu_logo.py <outdir>  ->  menu_logo.png, menu_logo_glow.png, menu/menu_logo/<n>.png"""
import sys, os, math, random
from PIL import Image, ImageDraw, ImageFont
from common import INK, band, make_noise
from menu_ui import (Spr, BRONZE, SEA, ENAMEL, MOSS, GLOW, L2, tone, col, gear, mycena, agaric, cushion, vine,
                     thread_walk, draw_threads, outline_parts, glow_image, rivet, ORGANIC)

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
FONT = '/usr/share/fonts/gsfonts/URWBookman-Demi.otf'
LW, LH = 344, 100
FRAMES = 8
nA, nB = make_noise(6, 811, 400, 200), make_noise(2, 812, 400, 200)

def glyph_mask(text, size, x, y, spacing=0):
    """pixel-snapped glyphs: {(x, y)} + per-letter boxes"""
    font = ImageFont.truetype(FONT, size)
    im = Image.new('L', (LW, LH), 0); d = ImageDraw.Draw(im); d.fontmode = '1'
    boxes, cx = [], x
    for ch in text:
        d.text((cx, y), ch, font=font, fill=255)
        bb = font.getbbox(ch)
        boxes.append((ch, int(cx + bb[0]), int(y + bb[1]), int(cx + bb[2]), int(y + bb[3])))
        cx += font.getlength(ch) + spacing
    p = im.load()
    return {(i, j) for j in range(LH) for i in range(LW) if p[i, j]}, boxes

def text_width(text, size, spacing=0):
    font = ImageFont.truetype(FONT, size)
    return sum(font.getlength(c) for c in text) + spacing * (len(text) - 1)

def depth_field(mask, cap=5):
    """distance (4-neighbour) from the outside, capped"""
    dist = {}
    frontier = [q for q in mask if any((q[0] + dx, q[1] + dy) not in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for q in frontier: dist[q] = 1
    k = 1
    while frontier and k < cap:
        nxt = []
        for (x, y) in frontier:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q in mask and q not in dist: dist[q] = k + 1; nxt.append(q)
        frontier, k = nxt, k + 1
    for q in mask: dist.setdefault(q, cap)
    return dist

def cast_bronze(s, mask, top, cap_h, seed=0):
    """bevelled cast letters: lit top-left edges, a darker interior towards the bottom, verdigris running down"""
    dist = depth_field(mask)
    shadow = {(x + dx, y + 2) for (x, y) in mask for dx in (1, 2)} - mask
    for q in shadow: s.put(q[0], q[1], ENAMEL[0], 'shadow')
    for (x, y) in mask:
        d = dist[(x, y)]
        gx = dist.get((x + 1, y), 0) - dist.get((x - 1, y), 0)
        gy = dist.get((x, y + 1), 0) - dist.get((x, y - 1), 0)
        gl = math.hypot(gx, gy) or 1
        face = (-gx / gl) * L2[0] + (-gy / gl) * L2[1]          # outward normal vs the light
        h = (y - top) / cap_h
        if d == 1: v = 3.4 + 2.6 * face
        elif d == 2: v = 3.5 + 1.3 * face
        else: v = 3.9 - 1.0 * h + (nB(x * 1.4 + seed, y * 1.4) - 0.5) * 1.0
        c = col(BRONZE, min(6.4, band(v, x, y)))
        if nA(x * 3.2 + seed, y * 0.3) + h * 0.2 > 0.76:      # verdigris streaks running down
            c = tone(SEA, (v - 1.0) * 0.62, x, y)
        s.put(x, y, c, 'letter')
    for (x, y) in list(mask | shadow):                          # contour
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in mask and q not in shadow and q not in s.px: s.put(q[0], q[1], INK, 'contour')

def top_of(mask, x):
    ys = [y for (xx, y) in mask if xx == x]
    return min(ys) if ys else None

def logo(f, subtitle=False):
    """subtitle: the store variant -- 'A WEIRD GAME' under the name (part of the Steam title), the ivy left out"""
    s = Spr(LW, LH)
    glow_mask = set()
    # UPPER -- small, letter-spaced, between two riveted bronze rods ending in little gears
    up_size, up_sp = 17, 4
    uw = text_width('UPPER', up_size, up_sp)
    ux = (LW - uw) / 2
    umask, _ = glyph_mask('UPPER', up_size, ux, 4, up_sp)
    cast_bronze(s, umask, 8, 12, seed=3)
    uy = 15
    for x0, x1 in ((60, int(ux) - 8), (int(ux + uw) + 8, LW - 60)):
        for x in range(x0, x1 + 1):
            s.put(x, uy, BRONZE[0], 'rod'); s.put(x, uy + 1, BRONZE[5], 'rod'); s.put(x, uy + 2, BRONZE[3], 'rod')
            s.put(x, uy + 3, BRONZE[0], 'rod')
        for x in range(x0 + 6, x1 - 4, 10): rivet(s, x, uy + 1)
    gear(s, 55, uy + 1.5, 0.2, rb=4.5, teeth_h=2.0, n=6, spokes=3, seed=1)
    gear(s, LW - 56, uy + 1.5, 0.5, rb=4.5, teeth_h=2.0, n=6, spokes=3, seed=2)
    # MORKEZELA, the O left out for the gear
    size = 44
    word = 'MORKEZELA'
    ww = text_width(word, size)
    wx = (LW - ww) / 2
    wy = 30 - ImageFont.truetype(FONT, size).getbbox('M')[1]
    mask, boxes = glyph_mask(word, size, wx, wy)
    _, ox0, oy0, ox1, oy1 = boxes[1]
    omask, _ = glyph_mask('O', size, boxes[1][1] - ImageFont.truetype(FONT, size).getbbox('O')[0], wy)
    mask -= omask
    top = min(y for _, y in mask); cap_h = max(y for _, y in mask) - top
    cast_bronze(s, mask, top, cap_h, seed=11)
    ocx, ocy = (ox0 + ox1) / 2, (oy0 + oy1) / 2
    orad = min(ox1 - ox0, oy1 - oy0) / 2
    s.gear_centre = (ocx, ocy, orad)                            # tools/storeart crops the community icon here
    # the gear turns 60 deg over the loop: 12 teeth, 6 spokes -> seamless
    gear(s, ocx, ocy, f * (math.pi / 3) / FRAMES, rb=orad - 3.0, teeth_h=3.0, n=12, spokes=6, seed=7)
    # growth: mushrooms on M, K and L, moss at the feet of the letters, ivy hanging from the first E
    lx = {ch + str(i): b for i, (ch, *b) in enumerate(boxes)}
    m = lx['M0']; k = lx['K3']; l = lx['L7']; e = lx['E4']; a = lx['A8']
    rnd = random.Random(4)
    pts = thread_walk(rnd, (m[0] + 12, top + 1), 0, 120, (m[0] + 4, top - 1, a[2] - 6, top + 3), wiggle=0.35, branch=0.05)
    phase = f / FRAMES
    for cxm, rx, sp in ((m[0] + 6, 5, 1), (k[2] - 4, 4, 1), (l[0] + 9, 6, 2), (a[2] - 6, 4, 0)):
        cushion(s, cxm, top + cap_h - 1, rx, 2.2, cxm, sporo=sp)
    if subtitle:
        sub, sub_size, sub_sp = 'A WEIRD GAME', 15, 3
        sw = text_width(sub, sub_size, sub_sp)
        smask, _ = glyph_mask(sub, sub_size, (LW - sw) / 2, top + cap_h + 6, sub_sp)
        cast_bronze(s, smask, min(y for _, y in smask), 10, seed=23)
    else:
        vine(s, lambda t: (e[0] + 6 + 2 * math.sin(t * 5), top + cap_h - 2 + 22 * t),
             [(0.25, True), (0.5, True, True), (0.78, True)], curl=(e[0] + 7, top + cap_h + 21, 2.2))
    draw_threads(s, [(x, y, d) for (x, y, d) in pts if s.part.get((x, y)) in ('letter', 'contour')], phase, total=120, mask=glow_mask)
    for bx, h, w, lean in ((m[0] + 5, 5, 7, -1), (m[0] + 13, 9, 11, 1), (m[0] + 21, 3, 6, 2)):
        mycena(s, bx, (top_of(mask, bx) or top) - 1, h, w, lean, True, False, glow_mask)
    apex = (a[0] + a[2]) // 2
    agaric(s, apex - 1, (top_of(mask, apex) or top) - 1, 4, 10, True, False, glow_mask)
    for bx, h, w, lean in ((a[2] - 3, 3, 6, 1), (l[0] + 3, 4, 6, -1)):
        mycena(s, bx, (top_of(mask, bx) or top + 8) - 1, h, w, lean, True, False, glow_mask)
    outline_parts(s, ORGANIC + ('moss',))
    return s, glow_mask

if __name__ == '__main__':
    d = os.path.join(OUT, 'menu', 'menu_logo'); os.makedirs(d, exist_ok=True)
    sheet = Image.new('RGBA', (LW * FRAMES, LH), (0, 0, 0, 0))
    gm = set()
    for f in range(FRAMES):
        s, g = logo(f)
        gm |= g if f == 0 else set()
        im = s.image(); im.save(os.path.join(d, '%d.png' % f))
        sheet.alpha_composite(im, (f * LW, 0))
    sheet.save(os.path.join(OUT, 'menu_logo.png'))
    glow_image(LW, LH, gm, radius=2.6, gain=1.4).save(os.path.join(OUT, 'menu_logo_glow.png'))
    s, g = logo(0, subtitle=True)                                  # the store / library variant (tools/storeart)
    s.image().save(os.path.join(OUT, 'menu_logo_store.png'))
    glow_image(LW, LH, g, radius=2.6, gain=1.4).save(os.path.join(OUT, 'menu_logo_store_glow.png'))
    print('ok')
