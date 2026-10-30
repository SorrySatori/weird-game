"""Menu kit -- the main menu, the ESC menu and their save / load / language panels, drawn as a mechano-fungal machine:
dark green enamel plaques in riveted, verdigrised bronze; an iron gear on the left; mycelium, mushrooms, a vine and
moss creeping over the metal. Shown at 2x (utils/menuKit.js).

  menu_button.png   176x32, one row per decoration variant (mycena trio / bracket fungi / fly-agaric):
                    0 idle, 1-8 hover loop (the gear turns 90 deg, a glow pulse runs down the mycelium, the caps glow,
                    the leaves lift), 9 pressed (sunk 1px, everything lit), 10 disabled (dry, grey)
  menu_slot.png     228x26, save / load rows: 0 idle, 1 hover, 2 pressed, 3 selected -- x2 (empty / used porthole)
  menu_small.png    20x20: arrow left x3, arrow right x3, close x3 (idle / hover / pressed)
  menu_panel_<k>.png + menu_panel_<k>_glow.png   the panels pause / slots / lang (frame, corner gears, fungi, title
                    plate) + their ADD glow; sizes in PANELS (mirrored by MENU_PANELS in utils/menuKit.js)
  menu_slider.png   136x16 glass tube (0 idle, 1 focused) + menu_slider_fill.png (the glowing liquid at 100 %, cropped)
  menu_knob.png     16x16 gear knob: 0-3 turns it 90 deg (it rolls along the tube), 4-7 lit
  menu_toggle.png   40x20 lever: 0 off, 1 off focused, 2 on, 3 on focused
  menu_spore.png    3x3 spore for the click puff

python3 menu_ui.py <outdir>  ->  the sheets above + menu/<sheet>/<n>.png frames (for Aseprite) + menu.gpl"""
import sys, os, math, random
from PIL import Image
from common import INK, band, make_noise
from symbionts import Spr, curve, lit, norm
from pal_menu import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
nA, nB, nC = make_noise(5, 701, 600, 400), make_noise(2, 702, 600, 400), make_noise(9, 703, 600, 400)
L2 = (-0.6, -0.8)                                              # light from the top left (2D)

def tone(k, v, x, y): return col(k, band(v, x, y))

def rr_sdf(px, py, x0, y0, x1, y1, r):
    """signed distance to a rounded rectangle (negative inside)"""
    cx, cy, hx, hy = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 - r, (y1 - y0) / 2 - r
    qx, qy = abs(px - cx) - hx, abs(py - cy) - hy
    return math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0) - r

def rr_normal(px, py, box, r):
    e = 0.5
    gx = rr_sdf(px + e, py, *box, r) - rr_sdf(px - e, py, *box, r)
    gy = rr_sdf(px, py + e, *box, r) - rr_sdf(px, py - e, *box, r)
    l = math.hypot(gx, gy) or 1
    return gx / l, gy / l

def darker(c, k=ENAMEL):
    """the same pixel in shadow: the nearest-darker step of its ramp (or the enamel's)"""
    for ramp_ in (ENAMEL, BRONZE, SEA, IRON, RUST, LEAF, MOSS, CAP, MADDER, BONE, GLOW, AMANITA, CORD, PARCH, CAV):
        if c in ramp_:
            i = ramp_.index(c)
            return ramp_[max(0, i - 2)]
    return k[0]

def lumi(c): return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

# --- the plaque -------------------------------------------------------------------------------------------------------
def plaque(s, box, r, pressed=False, hover=False, frame_w=2, rivets=(), enamel_lift=0.0, seed=0, inlay=False, vignette=0.0):
    """bronze frame (outline + bevel) around a recessed enamel field; returns the enamel test"""
    x0, y0, x1, y1 = box
    for y in range(int(y0) - 1, int(y1) + 2):
        for x in range(int(x0) - 1, int(x1) + 2):
            px, py = x + 0.5, y + 0.5
            d = rr_sdf(px, py, *box, r)
            if d > 0: continue
            depth = -d
            if depth < 1:
                s.put(x, y, BRONZE[0], 'frame'); continue
            if depth < 1 + frame_w:
                nx, ny = rr_normal(px, py, box, r)
                face = nx * L2[0] + ny * L2[1]                 # +1 = facing the light
                if pressed: face = -face * 0.6
                v = 3.0 + 1.9 * face + (nB(x + seed, y) - 0.5) * 1.2 + (0.5 if depth < 2 and face > 0 else 0)
                c = col(BRONZE, min(5.6, band(v, x, y)))
                if nA(x * 1.7 + seed, y * 1.7) + (nB(x * 2, y * 2 + seed) - 0.5) * 0.3 > 0.56:   # verdigris
                    c = tone(SEA, (v - 1.2) * 0.6, x, y)
                s.put(x, y, c, 'frame'); continue
            # recessed enamel: the frame shades its top / left inner edge, the bottom / right catches a little light
            nx, ny = rr_normal(px, py, box, r)
            inner = depth - 1 - frame_w
            v = 2.5 + enamel_lift + (1 - (py - y0) / (y1 - y0)) * 0.7 + (nB(x * 1.3 + seed, y * 1.3) - 0.5) * 0.9
            if pressed: v -= 0.8
            if vignette: v -= vignette * max(0.0, 1 - inner / 18) ** 2
            if inner < 1:
                face = nx * L2[0] + ny * L2[1]
                v += -1.6 if face > 0.2 else (0.9 if face < -0.2 else 0)
                if hover: s.put(x, y, GLOW[0] if face <= 0.2 else ENAMEL[1], 'enamel'); continue
            if inlay and 2 <= inner < 3:                           # an engraved bronze line around the field
                s.put(x, y, BRONZE[2] if not hover else BRONZE[3], 'inlay'); continue
            if nC(x * 2.2 + seed, y * 3) > 0.71 and (x + 2 * y) % 5 == 0:   # craquelure
                v -= 0.9
            s.put(x, y, tone(ENAMEL, v, x, y), 'enamel')
    for rx, ry in rivets:
        rivet(s, rx, ry)

def rivet(s, x, y):
    for dx, dy, c in ((0, 0, BRONZE[7]), (1, 0, BRONZE[5]), (0, 1, BRONZE[4]), (1, 1, BRONZE[2]),
                      (2, 1, BRONZE[1]), (1, 2, BRONZE[1]), (-1, 0, BRONZE[3]), (0, -1, BRONZE[3])):
        if s.part.get((x + dx, y + dy)) in ('frame', 'enamel'): s.put(x + dx, y + dy, c, 'rivet')

# --- the gear ---------------------------------------------------------------------------------------------------------
def gear(s, cx, cy, ang, rb=9.5, teeth_h=2.6, n=8, spokes=4, dry=False, seed=0):
    """an iron gear with 4 spokes, rust and moss attached to the gear (they turn with it), brass hub"""
    R = rb + teeth_h + 1
    mine, holes = {}, []
    for y in range(int(cy - R) - 1, int(cy + R) + 2):
        for x in range(int(cx - R) - 1, int(cx + R) + 2):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            rr = math.hypot(dx, dy)
            th = math.atan2(dy, dx) - ang
            ph = abs(((th * n / (2 * math.pi)) % 1) - 0.5)        # 0 = between teeth, 0.5 = tooth centre
            ph = 0.5 - ph
            outer = rb + teeth_h * max(0.0, min(1.0, (0.30 - ph) / 0.08))
            if rr > outer: continue
            # gear-local coordinates for the textures (rust, moss turn with the gear)
            lx = cx + math.cos(-ang) * dx - math.sin(-ang) * dy
            ly = cy + math.sin(-ang) * dx + math.cos(-ang) * dy
            a4 = (th * spokes / (2 * math.pi)) % 1
            spoke = a4 < 0.13 or a4 > 0.87
            if rb * 0.38 < rr < rb - 2.6 and not spoke:
                holes.append((x, y)); continue
            hub = rb * 0.29
            if rr < hub:                                          # brass hub + axle
                v = 3.5 + 3.0 * lit((dx / hub, dy / hub, math.sqrt(max(0.1, 1 - (rr / hub) ** 2))))
                c = BRONZE[1] if rr < 1.0 else tone(BRONZE, v, x, y)
                mine[(x, y)] = c; continue
            nx, ny = dx / (rr or 1), dy / (rr or 1)
            face = nx * L2[0] + ny * L2[1]
            v = 3.3 + (nB(lx * 1.6 + seed, ly * 1.6) - 0.5) * 0.7
            if outer - rr < 1.4: v += 2.4 * face                  # the rim's bevel
            elif rb - 2.6 <= rr < rb - 1.6: v -= 1.2 * face       # sunk ring
            elif rr < rb * 0.38 + 0.8: v -= 0.8
            c = tone(IRON, v, x, y)
            if nA(lx * 2.3 + 40 + seed, ly * 2.3) > 0.67:
                c = tone(RUST, v * 0.75, x, y)
            if nC(lx * 3 + seed, ly * 3) > 0.72 and rr > rb - 3:
                c = tone(LEAF, 1.5 + 2 * max(0, face) + nB(lx * 4, ly * 4), x, y)
            if dry: c = greyed(c, 0.0)
            mine[(x, y)] = c
    for (x, y) in holes:                                          # see-through: the plaque behind, in shadow
        if (x, y) in s.px: s.put(x, y, ENAMEL[0] if s.part.get((x, y)) == 'enamel' else darker(s.px[(x, y)]), 'hole')
    edge = {}
    for (x, y) in mine:                                           # outline on air, a cast shadow on the plaque
        for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1)):
            q = (x + ddx, y + ddy)
            if q in mine or q in holes: continue
            if q in s.px:
                if (ddx, ddy) in ((1, 0), (0, 1), (1, 1)): edge[q] = darker(s.px[q])
            elif (ddx, ddy) != (1, 1):
                edge[q] = INK
    for q, c in edge.items(): s.put(q[0], q[1], c, 'gearedge')
    for (x, y), c in mine.items(): s.put(x, y, c, 'gear')

# --- organic growth ---------------------------------------------------------------------------------------------------
ORGANIC = ('cap', 'stem', 'gill', 'leaf', 'vine', 'sporo')

def thread_walk(rnd, start, heading, length, bounds, wiggle=0.35, branch=0.06, depth=0, dist0=0):
    """mycelium: a wandering 1px thread with branches; returns [(x, y, dist)]"""
    out, (x, y), h = [], start, heading
    for i in range(length):
        h += rnd.uniform(-wiggle, wiggle)
        x += math.cos(h); y += math.sin(h)
        bx0, by0, bx1, by1 = bounds
        if y < by0: y = by0; h = -h
        if y > by1: y = by1; h = -h
        if not (bx0 <= x <= bx1): break
        out.append((int(x), int(y), dist0 + i))
        if depth < 2 and rnd.random() < branch:
            out += thread_walk(rnd, (x, y), h + rnd.choice((-1, 1)) * rnd.uniform(0.5, 1.1),
                               int(length * rnd.uniform(0.2, 0.45)), bounds, wiggle, branch * 0.5, depth + 1, dist0 + i)
    return out

def draw_threads(s, pts, glow_phase=None, dry=False, total=60, mask=None):
    """raised pale strands with a dark underside; hover: green, a bright pulse travelling away from the fungi"""
    own = {(x, y) for x, y, d in pts}
    skip = ('gear', 'gearedge', 'rivet') + ORGANIC
    for (x, y, d) in pts:
        if s.part.get((x, y)) in skip: continue
        if dry: c = BONE[2]
        elif glow_phase is None: c = BONE[4] if d % 5 else BONE[5]
        else:
            k = ((d / total) - glow_phase) % 1.0
            c = GLOW[5] if k < 0.07 else GLOW[4] if k < 0.16 else GLOW[3] if k < 0.4 else GLOW[2]
            if mask is not None and k < 0.4: mask.add((x, y))
        s.put(x, y, c, 'thread')

LEAF_UP = ['....oo.',
           '..oohho',
           '.ohhmdo',
           '.ohmmdo',
           'ovmmdo.',
           'ov.oo..']
LEAF_PERK = ['...oo..',
             '..ohho.',
             '..ohmdo',
             '.ohmmdo',
             '.ovmdo.',
             'ov.oo..']
LEAF_TONE = {'o': 0, 'd': 2, 'v': 3, 'm': 4, 'h': 5}

def leaf(s, x, y, up, perk, dry, flip=False):
    pat = LEAF_PERK if perk else LEAF_UP
    rows = pat if up else pat[::-1]
    if flip: rows = [r[::-1] for r in rows]; x -= len(rows[0]) - 1
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == '.': continue
            yy = y - len(rows) + 1 + r if up else y + r
            k = LEAF[LEAF_TONE[ch] + (1 if perk and ch in 'mh' else 0)]
            s.put(x + c, yy, greyed(k) if dry else k, 'leaf')

def vine(s, path, leaves, perk=False, dry=False, curl=None):
    """a 2px stem along path(t), ivy leaves [(t, up)], an optional tendril curl at the end"""
    pts = curve(path, 120)
    for (x, y) in pts:
        s.put(x, y, LEAF[2] if not dry else BONE[2], 'vine')
    for (x, y) in pts:
        s.put(x, y - 1, LEAF[4] if not dry else BONE[3], 'vine')
    if curl:
        cx, cy, r0 = curl
        for i in range(26):
            a = i * 0.42; r = r0 * (1 - i / 30)
            s.put(cx + math.cos(a) * r, cy + math.sin(a) * r, LEAF[3] if not dry else BONE[2], 'vine')
    for lv in leaves:
        t, up = lv[0], lv[1]
        x, y = path(t)
        leaf(s, int(x), int(y) - (1 if up else -1), up, perk, dry, flip=len(lv) > 2 and lv[2])

def cushion(s, cx, cy, rx, ry, seed, dry=False, sporo=0):
    """a cushion of moss sitting on the metal, with a few sporophyte stalks"""
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            u, w = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            d = u * u + w * w + (nB(x * 3 + seed, y * 3) - 0.5) * 0.5
            if d > 1 or (y + 0.5 > cy + ry * 0.4 and d > 0.6): continue
            v = 1.0 + 4.5 * lit((u, w, math.sqrt(max(0.05, 1 - min(1, u * u + w * w))))) + (nB(x * 4, y * 4 + seed) - 0.5) * 1.5
            k = tone(MOSS, v, x, y)
            s.put(x, y, greyed(k) if dry else k, 'moss')
    rnd = random.Random(seed)
    for _ in range(sporo):
        x = int(cx + rnd.uniform(-rx * 0.7, rx * 0.7)); h = rnd.randint(2, 4); y0 = int(cy - ry * 0.6)
        for i in range(h): s.put(x, y0 - i, CAP[3] if not dry else BONE[2], 'sporo')
        s.put(x, y0 - h, CAP[6] if not dry else BONE[3], 'sporo')

def mycena(s, bx, by, h, w, lean, glow=False, dry=False, mask=None):
    """a bell-capped mushroom standing on (bx, by): radial grooves, a translucent rim and gills that glow"""
    sw = 2 if w >= 8 else 1
    for i in range(h):
        x = bx + lean * i / max(1, h)
        s.put(x, by - i, BONE[6] if not dry else BONE[3], 'stem')
        if sw == 2: s.put(x + 1, by - i, BONE[4] if not dry else BONE[2], 'stem')
    tx = bx + lean + (0.5 if sw == 2 else 0)
    ch = max(3, (w + 1) // 2)
    top = by - h - ch
    for t in range(ch):
        hw = w / 2 * (0.32 + 0.68 * ((t + 1) / ch) ** 0.75)
        y = top + t
        for x in range(int(tx - hw), int(tx + hw) + 1):
            u = (x + 0.5 - tx) / hw
            if abs(u) > 1: continue
            n = norm((u * 0.9, -0.7 + 0.9 * t / ch, math.sqrt(max(0.05, 1 - u * u))))
            v = 1.0 + 5.2 * lit(n) - (0.7 if (x - int(tx)) % 2 == 0 and t > 0 else 0)
            c = tone(CAP, v, x, y)
            if t == ch - 1:                                        # the rim: translucent, it glows first
                c = (GLOW[3] if abs(u) > 0.55 else GLOW[2]) if glow else CAP[2] if abs(u) > 0.6 else CAP[4]
                if glow and mask is not None: mask.add((x, y))
            elif t == 0 and abs(u) < 0.5 and not glow: c = CAP[7]
            s.put(x, y, greyed(c) if dry else c, 'cap')
    gy = top + ch                                                  # gills under the rim
    hw = w / 2 - 1.2
    for x in range(int(tx - hw), int(tx + hw) + 1):
        if s.part.get((x, gy)) == 'stem': continue
        c = (GLOW[4] if glow else BONE[3]) if not dry else BONE[1]
        s.put(x, gy, c, 'gill')
        if glow and mask is not None: mask.add((x, gy))

def bracket(s, x, y, w, h, glow=False, dry=False, mask=None):
    """a shelf fungus growing out of the right edge: zoned half-ellipse, pale growing margin, pores beneath"""
    for yy in range(y - h, y + 1):
        for xx in range(x, x + w + 1):
            u, v_ = (xx + 0.5 - x) / w, (y + 0.5 - (yy + 0.5)) / h
            d = math.sqrt(u * u + v_ * v_)
            if d > 1 or u < 0: continue
            zone = int(d * 5)
            k = [CAP[3], CAP[5], CAP[2], CAP[6], BONE[6]][min(4, zone)]
            if v_ > 0.55 and zone < 4: k = CAP[min(7, CAP.index(k) + 1)]
            if yy == y: k = BONE[4]                                # pore surface
            if glow and (zone == 4 or yy == y):
                k = GLOW[4] if yy == y else GLOW[3]
                if mask is not None: mask.add((xx, yy))
            s.put(xx, yy, greyed(k) if dry else k, 'cap')

def agaric(s, bx, by, h, w, glow=False, dry=False, mask=None):
    """a weathered fly-agaric in the same muted key as the other fungi: a low madder-brown dome, the striated cap
    shaded like the mycenas, a few dirty cream veil flakes, gills that glow"""
    for i in range(h):
        s.put(bx, by - i, BONE[5] if not dry else BONE[3], 'stem'); s.put(bx + 1, by - i, BONE[3] if not dry else BONE[2], 'stem')
    if h >= 4:
        ry_ = by - int(h * 0.6)
        for x in range(bx - 1, bx + 3): s.put(x, ry_, BONE[4] if not dry else BONE[2], 'stem')
    cy = by - h; cx = bx + 1
    rx, ry = w / 2, max(2.5, w / 3.3)
    for y in range(int(cy - ry) - 1, cy + 1):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 1):
            u, v_ = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            if u * u + v_ * v_ > 1: continue
            n = (u * 0.9, v_ * 0.9, math.sqrt(max(0.05, 1 - u * u - v_ * v_)))
            v = 0.9 + 4.6 * lit(n) - (0.6 if (x - int(cx)) % 2 == 0 and v_ > -0.5 else 0)
            c = tone(MADDER, v, x, y)
            if y == cy and not glow: c = MADDER[1]
            s.put(x, y, greyed(c) if dry else c, 'cap')
    for wx, wy in ((-2, -2), (1, -3), (2, -2), (-3, -1)):            # veil flakes: few, small, dull
        if abs(wx) < rx - 1 and s.part.get((cx + wx, cy + wy)) == 'cap':
            s.put(cx + wx, cy + wy, (BONE[4] if (wx + wy) % 2 else BONE[3]) if not dry else BONE[2], 'cap')
    for x in range(int(cx - rx) + 1, int(cx + rx)):
        if s.part.get((x, cy + 1)) == 'stem': continue
        s.put(x, cy + 1, (GLOW[3] if glow else BONE[3]) if not dry else BONE[1], 'gill')
        if glow and mask is not None: mask.add((x, cy + 1))

def outline_parts(s, parts, c=INK):
    """a dark contour around the organic parts where they meet air or metal"""
    add = {}
    for (x, y), p in s.part.items():
        if p not in parts: continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if s.part.get(q) in parts or s.part.get(q) == 'thread': continue
            if not (0 <= q[0] < s.w and 0 <= q[1] < s.h): continue
            add[q] = c if q not in s.px else darker(s.px[q])
    for q, cc in add.items(): s.put(q[0], q[1], cc, 'organicedge')

def greyed(c, lift=0.0):
    """disabled look: the colour's luminance on the iron ramp"""
    l = lumi(c) / 255
    return IRON[max(0, min(len(IRON) - 1, int(l * 9 + lift * 8)))]

def glow_image(w, h, mask, radius=2.2, gain=1.7):
    """soft white halo around the lit pixels (tinted + faded in by the game, ADD blend)"""
    from PIL import ImageFilter
    im = Image.new('L', (w, h), 0); p = im.load()
    for (x, y) in mask:
        if 0 <= x < w and 0 <= y < h: p[x, y] = 255
    im = im.filter(ImageFilter.GaussianBlur(radius)).point(lambda a: min(255, int(a * gain)))
    out = Image.new('RGBA', (w, h), (255, 255, 255, 0)); out.putalpha(im)
    return out

# --- the main menu button ---------------------------------------------------------------------------------------------
BW, BH = 192, 48
BOX = (18, 15, 181, 39)
BUTTON_GLOW = {}

def button(variant, f):
    """f: 0 idle, 1-8 hover, 9 pressed, 10 disabled"""
    hover, pressed, dry = 1 <= f <= 8, f == 9, f == 10
    lit_ = hover or pressed
    k = f - 1 if hover else 0
    off = 1 if pressed else 0
    s = Spr(BW, BH)
    mask = set()
    x0, y0, x1, y1 = BOX
    y0o, y1o = y0 + off, y1 + off
    seed = variant * 37
    rivets = [(x0 + 36, y0o + 1), (x1 - 44, y0o + 1), (x0 + 36, y1o - 2), (x1 - 5, y1o - 2)]
    plaque(s, (x0, y0o, x1, y1o), 3, pressed=pressed, hover=lit_, frame_w=3, rivets=rivets, seed=seed, inlay=True)
    rnd = random.Random(100 + variant)
    ox = {0: x1 - 17, 1: x1 - 4, 2: x1 - 22}[variant]
    pts = thread_walk(rnd, (ox, y0o + 1), math.pi, 64, (x0 + 44, y0o, x1, y0o + 5), wiggle=0.38, branch=0.07)
    pts += thread_walk(rnd, (ox + 3, y0o + 2), math.pi * 0.6, 18, (x1 - 44, y0o + 2, x1 + 1, y1o - 3), wiggle=0.3)
    # moss cushions + the ivy along the bottom-left edge, coming from behind the gear
    for cx, rx, ry, sp in ((x0 + 22, 6, 3, 2), (x0 + 47, 4, 2.5, 1), (x0 + 70, 3, 2, 0), (x1 - 30, 4, 2, 1)):
        cushion(s, cx, y1o - 1, rx, ry, seed + cx, dry, sporo=sp)
    perk = lit_
    vine(s, lambda t: (x0 + 12 + 70 * t, y1o - 0.5 + 1.6 * math.sin(t * 6.5 + variant)),
         [(0.18, False), (0.34, True), (0.55, False), (0.72, True), (0.88, False)], perk=perk, dry=dry,
         curl=(x0 + 86, y1o - 3.5, 2.6))
    phase = 0.5 if pressed else (k / 8 if hover else None)
    draw_threads(s, pts, phase, dry, total=64, mask=mask)
    # the fungi at the right end
    if variant == 0:
        for bx, h, w, lean in ((x1 - 26, 5, 7, -1), (x1 - 16, 8, 11, 1), (x1 - 6, 3, 6, 1)):
            mycena(s, bx, y0o + 1, h, w, lean, lit_, dry, mask)
    elif variant == 1:
        for yy, w, h in ((y0o + 7, 8, 4), (y0o + 14, 10, 5), (y0o + 21, 7, 4)):
            bracket(s, x1 - 1, yy, w, h, lit_, dry, mask)
        mycena(s, x1 - 30, y0o + 1, 4, 7, -1, lit_, dry, mask)
    else:
        agaric(s, x1 - 22, y0o + 1, 5, 11, lit_, dry, mask)
        mycena(s, x1 - 11, y0o + 1, 5, 6, 1, lit_, dry, mask)
        agaric(s, x1 - 33, y0o + 1, 2, 5, lit_, dry, mask)
    outline_parts(s, ORGANIC)
    # the gear (turns 90 deg over the 8 hover frames -- its 4 spokes make the loop seamless)
    gear(s, 18, 27 + off, k * math.pi / 16 if hover else 0, rb=11.5, teeth_h=3.2, dry=dry, seed=seed)
    if dry:
        for q, c in list(s.px.items()):
            if s.part[q] in ('frame', 'enamel', 'rivet', 'thread', 'threadshadow', 'inlay'): s.px[q] = greyed(c, 0.05)
    if f == 1: BUTTON_GLOW[variant] = glow_image(BW, BH, mask)
    return s

# --- save / load rows -------------------------------------------------------------------------------------------------
SW, SH = 228, 26
SBOX = (2, 2, 225, 23)

def slot(f, used):
    """f: 0 idle, 1 hover, 2 pressed, 3 selected; the porthole on the left glows when the slot holds a save"""
    hover, pressed, sel = f == 1, f == 2, f == 3
    off = 1 if pressed else 0
    s = Spr(SW, SH)
    x0, y0, x1, y1 = SBOX
    plaque(s, (x0, y0 + off, x1, y1 + off), 3, pressed=pressed, hover=hover or sel, frame_w=3, seed=77,
           rivets=[(x1 - 8, y0 + 1 + off), (x1 - 8, y1 - 2 + off)], enamel_lift=0.9 if sel else 0.4 if hover else 0)
    if hover or sel:                                               # hovered / selected row: the bronze catches light
        for q, c in list(s.px.items()):
            if s.part[q] == 'frame' and c != BRONZE[0]:
                s.px[q] = BRONZE[min(7, BRONZE.index(c) + (2 if sel else 1))] if c in BRONZE else SEA[min(3, SEA.index(c) + 1)] if c in SEA else c
    # porthole
    cx, cy = 14, 12.5 + off
    for y in range(0, SH):
        for x in range(2, 28):
            r = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if r > 8.2: continue
            if r > 6.6:
                face = ((x + 0.5 - cx) * L2[0] + (y + 0.5 - cy) * L2[1]) / r
                s.put(x, y, tone(BRONZE, 4 + 2.2 * face, x, y) if r < 7.6 else BRONZE[0], 'port')
            else:
                if used:
                    g = 1 - r / 6.6
                    v = 0.6 + g * (3.6 if (hover or sel or pressed) else 2.6) + (nB(x * 3, y * 3) - 0.5)
                    c = tone(GLOW, v, x, y)
                else:
                    c = tone(ENAMEL, 1.2 + (nB(x * 3, y * 3)) * 1.2, x, y)
                if (x + 0.5 - cx) < -2 and (y + 0.5 - cy) < -2 and r > 3.5 and r < 5: c = BONE[6] if used else ENAMEL[5]
                s.put(x, y, c, 'port')
    if used:                                                       # a few threads growing from the porthole
        rnd = random.Random(5)
        pts = thread_walk(rnd, (22, y0 + 2 + off), 0, 30, (22, y0 + 1 + off, 90, y0 + 3 + off), 0.4, 0.1)
        draw_threads(s, pts, 0.3 if (hover or sel or pressed) else None, total=30)
    cushion(s, x1 - 22, y1 - 1 + off, 5, 2, 31, sporo=1)
    outline_parts(s, ORGANIC + ("moss",))
    return s

# --- small round buttons: arrows + close ------------------------------------------------------------------------------
def small(kind, f):
    hover, pressed = f == 1, f == 2
    off = 1 if pressed else 0
    s = Spr(20, 20)
    cx, cy = 9.5, 9.5 + off
    for y in range(20):
        for x in range(20):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            r = math.hypot(dx, dy)
            if r > 8.6: continue
            if r > 7.7: s.put(x, y, BRONZE[0], 'frame'); continue
            face = (dx * L2[0] + dy * L2[1]) / (r or 1)
            if pressed: face = -face * 0.6
            if r > 5.6:
                c = tone(BRONZE, 3.8 + 2.4 * face + (nB(x * 2, y * 2) - 0.5), x, y)
                if nA(x * 3 + 9, y * 3) > 0.66: c = tone(SEA, 1.4 + face, x, y)
            else:
                c = tone(ENAMEL, 2.4 - (1.2 * face if r > 4.6 else 0) - (0.8 if pressed else 0), x, y)
            s.put(x, y, c, 'body')
    lit_c, dark_c = (GLOW[4], GLOW[2]) if (hover or pressed) else (BONE[6], BONE[3])
    if kind in ('left', 'right'):
        for c in range(5):                                         # a solid arrowhead, base -> tip
            x = 7 + c if kind == 'right' else 12 - c
            for y in range(int(cy) - (4 - c), int(cy) + (4 - c) + 1):
                s.put(x, y, lit_c if y < cy - 0.5 else dark_c, 'glyph')
    else:
        for i in range(-3, 4):                                     # X
            s.put(cx - 0.5 + i, cy - 0.5 + i, lit_c, 'glyph'); s.put(cx + 0.5 + i, cy - 0.5 + i, dark_c, 'glyph')
            s.put(cx - 0.5 + i, cy - 0.5 - i, lit_c, 'glyph'); s.put(cx + 0.5 + i, cy - 0.5 - i, dark_c, 'glyph')
    return s

# --- settings controls: slider (glass tube + glowing liquid + a gear knob that rolls), lever toggle ------------------
TW, TH = 136, 16
GLASS = (4, 5, 131, 10)                                            # the tube's inside; menuKit.js SLIDER mirrors it

def slider_track(focus):
    s = Spr(TW, TH)
    plaque(s, (0, 1, TW - 1, TH - 2), 6, frame_w=3, seed=91, hover=False)
    gx0, gy0, gx1, gy1 = GLASS
    for y in range(gy0, gy1 + 1):
        for x in range(gx0, gx1 + 1):
            if s.part.get((x, y)) != 'enamel': continue
            c = ENAMEL[1] if y > gy0 else ENAMEL[3]
            if y == gy0 + 1 and (x // 3) % 5 != 0: c = ENAMEL[4]       # the glass's reflection
            s.put(x, y, c, 'glass')
    for i in range(1, 4):                                          # quarter notches under the tube
        x = gx0 + (gx1 - gx0) * i // 4
        s.put(x, gy1 + 2, BRONZE[1], 'notch')
    if focus:
        for q, c in list(s.px.items()):
            if s.part[q] == 'frame' and c in BRONZE and c != BRONZE[0]: s.px[q] = BRONZE[min(7, BRONZE.index(c) + 1)]
            elif s.part[q] == 'frame' and c in SEA: s.px[q] = SEA[min(3, SEA.index(c) + 1)]
    return s

def slider_fill():
    """the liquid at 100 %; the game crops it to the value"""
    s = Spr(TW, TH)
    gx0, gy0, gx1, gy1 = GLASS
    rnd = random.Random(12)
    for y in range(gy0 + 1, gy1 + 1):
        for x in range(gx0, gx1 + 1):
            k = 2 if y == gy0 + 1 else 1 if y < gy1 else 0
            if y == gy0 + 1 and (x + y) % 7 == 0: k = 3
            s.put(x, y, GLOW[k], 'fill')
    for _ in range(14):                                            # bubbles
        x, y = rnd.randint(gx0 + 2, gx1 - 2), rnd.randint(gy0 + 2, gy1 - 1)
        s.put(x, y, GLOW[4], 'fill')
    return s

def knob(f):
    """a little iron gear riding the tube: frames 0-3 turn it 90 deg (it rolls as it moves), 4-7 the same lit"""
    s = Spr(16, 16)
    lit_ = f >= 4
    gear(s, 8, 8, (f % 4) * math.pi / 8, rb=5.0, teeth_h=1.9, n=8, spokes=4, seed=4)
    if lit_:
        for q, c in list(s.px.items()):
            if c == INK: s.px[q] = GLOW[2]
            elif s.part[q] == 'gear' and c in BRONZE: s.px[q] = GLOW[4]
    return s

def toggle(f):
    """a lever in a bronze slot: 0 off, 1 off focused, 2 on, 3 on focused; when on, the groove fills with light"""
    on, focus = f >= 2, f % 2 == 1
    s = Spr(40, 20)
    plaque(s, (0, 1, 39, 18), 5, frame_w=3, seed=17)
    if focus:
        for q, c in list(s.px.items()):
            if s.part[q] == 'frame' and c in BRONZE and c != BRONZE[0]: s.px[q] = BRONZE[min(7, BRONZE.index(c) + 1)]
    bx = 27 if on else 12
    for x in range(8, 32):                                         # the groove
        s.put(x, 9, ENAMEL[0], 'groove'); s.put(x, 10, ENAMEL[0], 'groove'); s.put(x, 11, ENAMEL[3], 'groove')
        if on and x < bx:
            s.put(x, 9, GLOW[2], 'groove'); s.put(x, 10, GLOW[3] if x % 4 else GLOW[4], 'groove')
    s.blob(bx + 0.5, 10, 4.6, 4.6, lambda x, y, n: tone(BRONZE, 1.2 + 5.4 * lit(n), x, y), 'lever')
    for x in range(bx - 4, bx + 6):                                # the ball's shadow on the plate
        if s.part.get((x, 15)) in ('enamel', 'frame'): s.put(x, 15, darker(s.px[(x, 15)]), 'shadow')
    outline_parts(s, ('lever',))
    return s

# --- panels -----------------------------------------------------------------------------------------------------------
# key: (w, h, title plate w) in native px; utils/menuKit.js MENU_PANELS mirrors these (shown 2x, MARGIN around)
PANELS = {'pause': (224, 196, 128), 'slots': (256, 210, 136), 'lang': (224, 108, 112), 'settings': (256, 140, 136)}
MARGIN = 18

def panel(key):
    """riveted bronze frame with corner plates around dark enamel, a title plate, an iron gear behind the top-left
    corner, fungi + glowing mycelium top-right, shelf fungi on the right side, ivy up the left side, moss below"""
    w, h, tw = PANELS[key]
    W, H, M = w + 2 * MARGIN, h + 2 * MARGIN, MARGIN
    s = Spr(W, H); mask = set()
    x0, y0, x1, y1 = M, M, M + w - 1, M + h - 1
    cx = (x0 + x1) // 2
    gear(s, x0 + 4, y0 + 4, 0.25, rb=16, teeth_h=3.8, seed=5)              # behind the corners; the plates are their axles
    gear(s, x1 - 4, y1 - 4, 0.1, rb=10, teeth_h=3.0, seed=9)
    rv = [(x, y0 + 3) for x in range(x0 + 22, x1 - 18, 16) if abs(x - cx) > tw / 2 + 6] + \
         [(x, y1 - 4) for x in range(x0 + 22, x1 - 18, 16)] + \
         [(x0 + 3, y) for y in range(y0 + 24, y1 - 18, 16)] + [(x1 - 4, y) for y in range(y0 + 24, y1 - 18, 16)]
    plaque(s, (x0, y0, x1, y1), 5, frame_w=6, rivets=rv, seed=11, inlay=True, enamel_lift=-0.6, vignette=1.2)
    for bx, by in ((x0 - 3, y0 - 3), (x1 - 11, y0 - 3), (x0 - 3, y1 - 11), (x1 - 11, y1 - 11)):   # corner plates
        plaque(s, (bx, by, bx + 14, by + 14), 3, frame_w=8, seed=bx + by)
        rivet(s, bx + 6, by + 6)
    plaque(s, (cx - tw // 2, y0 - 8, cx + tw // 2, y0 + 12), 3, frame_w=3, seed=21, inlay=True,         # title plate
           rivets=[(cx - tw // 2 + 4, y0 + 1), (cx + tw // 2 - 5, y0 + 1)])
    rnd = random.Random(len(key) * 7 + w)
    # mycelium from the fungi top-right: along the top frame and down the right side
    ox = x1 - 22
    pts = thread_walk(rnd, (ox, y0 + 1), math.pi, 70, (cx + tw // 2 + 4, y0 - 1, x1, y0 + 4), wiggle=0.4, branch=0.08)
    pts += thread_walk(rnd, (x1 - 2, y0 + 12), math.pi / 2, 90, (x1 - 5, y0 + 10, x1, y1 - 12), wiggle=0.35, branch=0.06)
    for cxm, rx, ry, sp in ((x0 + 26, 7, 3, 2), (x0 + 52, 4, 2.5, 1), (cx + 10, 5, 2.5, 1), (x1 - 36, 6, 3, 2)):
        cushion(s, cxm, y1 - 1, rx, ry, cxm, sporo=sp)
    hang = random.Random(3)
    for _ in range(9):                                                     # moss strands under the bottom edge
        x = hang.randint(x0 + 14, x1 - 14)
        for i in range(hang.randint(2, 5)):
            s.put(x + (i // 3), y1 + 1 + i, MOSS[4 - min(3, i)], 'moss')
    vine(s, lambda t: (x0 + 1.5 + 1.8 * math.sin(t * 9), y1 + 4 - (h * 0.62) * t),
         [(0.1, True, True), (0.24, True), (0.38, True, True), (0.52, True), (0.66, True, True), (0.8, True), (0.93, True, True)],
         curl=(x0 + 4, y1 + 4 - h * 0.62 - 3, 2.6))
    draw_threads(s, pts, 0.0, total=90, mask=mask)
    for bx, hh, ww, lean in ((x1 - 30, 6, 7, -1), (x1 - 20, 10, 11, 1), (x1 - 10, 4, 6, 2)):
        mycena(s, bx, y0 - 1, hh, ww, lean, True, False, mask)
    for yy, ww, hh in ((y1 - 58, 8, 4), (y1 - 50, 11, 5), (y1 - 41, 7, 4)):
        bracket(s, x1 + 1, yy, ww, hh, True, False, mask)
    outline_parts(s, ORGANIC + ('moss',))
    return s, glow_image(W, H, mask, radius=2.6, gain=1.5)

def save_sheet(name, frames, cols=None):
    cols = cols or len(frames)
    w, h = frames[0].w, frames[0].h
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new('RGBA', (w * cols, h * rows), (0, 0, 0, 0))
    d = os.path.join(OUT, 'menu', name); os.makedirs(d, exist_ok=True)
    for i, fr in enumerate(frames):
        im = fr.image(); im.save(os.path.join(d, '%d.png' % i))
        sheet.alpha_composite(im, ((i % cols) * w, (i // cols) * h))
    sheet.save(os.path.join(OUT, name + '.png'))
    return sheet

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    save_sheet('menu_button', [button(v, f) for v in range(3) for f in range(11)], cols=11)
    g = Image.new('RGBA', (BW * 3, BH), (0, 0, 0, 0))
    for v in range(3): g.alpha_composite(BUTTON_GLOW[v], (v * BW, 0))
    g.save(os.path.join(OUT, 'menu_button_glow.png'))
    save_sheet('menu_slot', [slot(f, used) for used in (False, True) for f in range(4)], cols=4)
    save_sheet('menu_small', [small(k, f) for k in ('left', 'right', 'close') for f in range(3)], cols=9)
    save_sheet('menu_slider', [slider_track(False), slider_track(True)], cols=2)
    save_sheet('menu_slider_fill', [slider_fill()])
    save_sheet('menu_knob', [knob(f) for f in range(8)], cols=8)
    save_sheet('menu_toggle', [toggle(f) for f in range(4)], cols=4)
    for k in PANELS:
        sp, gl = panel(k)
        sp.image().save(os.path.join(OUT, 'menu_panel_%s.png' % k)); gl.save(os.path.join(OUT, 'menu_panel_%s_glow.png' % k))
    spore = Image.new('RGBA', (3, 3), (0, 0, 0, 0))
    for (x, y), c in {(1, 0): GLOW[4], (0, 1): GLOW[3], (1, 1): GLOW[5], (2, 1): GLOW[3], (1, 2): GLOW[2]}.items():
        spore.putpixel((x, y), c + (255,))
    spore.save(os.path.join(OUT, 'menu_spore.png'))
    write_gpl(os.path.join(OUT, 'menu.gpl'))
    print('ok')
