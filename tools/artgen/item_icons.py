"""Inventory icons for the demo items that still showed the lettered-circle placeholder.

60x60, transparent, shown 1:1 (pixelArt) -- the same look as the hand-drawn townhall key / Oltrac jars / cartridge:
clean shapes, light from the top left, a 1 px dark outline. One function per icon; families share helpers
(official forms = paper + header + stamp, Ortolan's game pieces = polished wood / bone / obsidian).

    python3 item_icons.py <outdir>     # -> <outdir>/<id>.png per icon, icons.txt (frame order), sheet.png (4x preview)

The ids are the inventory item ids (utils/itemIcons.js resolves an icon by item id).
"""
import math, os, sys
from PIL import Image

S = 60
def hx(s): s = s.lstrip('#'); return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)
def ramp(s): return [hx(c) for c in s.split()]
def pick(r, i): return r[max(0, min(len(r) - 1, int(round(i))))]
def mix(a, b, t): return tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(3)) + (255,)
def h32(*a):
    h = 2166136261
    for v in a:
        h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return h

INK    = hx('#17130f')
PAPER  = ramp('#5d5546 #8c826c #b8ad93 #d8cfb5 #eee6cf')
SEPIA  = ramp('#4a3a24 #6e5636 #937650 #b89a6c #d4bb8c')
TEXT   = hx('#6a6254')
STEEL  = ramp('#2a2f36 #46505b #6b7884 #9aa6b0 #ccd5db')
BRASS  = ramp('#3d2a10 #6b4a1a #9a6e28 #c69a3e #e8c66a')
WOOD   = ramp('#2e1a0e #4e2e18 #74472a #9a6640 #bf8b5c')
GRIP   = ramp('#3a1414 #5e2220 #85362e #a8503f')
BONE   = ramp('#4c4638 #7d7560 #ada48a #d6cdb1 #f0e9d2')
GLASS  = ramp('#22343a #3a565c #5d8288 #9cc0c0 #d6efe8')
SLIME  = ramp('#1f2a14 #34461e #4f6428 #6f8436 #93a64a')
TOAD   = ramp('#1c2414 #2f3d1f #4b5c2c #6f7f3a #98a556')
RUST   = ramp('#2a130c #4d2412 #77391a #a35528 #c87a3c')
ROT    = ramp('#3a3418 #5e5424 #8a7c34 #b8a64c #dccd78')
OBSID  = ramp('#0e0b14 #1c1626 #2d2440 #463a60')
VIOL   = ramp('#3a1450 #6a2a8a #a050c8 #e0a0ff')
GREEN  = ramp('#12301c #1f5a32 #3f8f5a #7fff8e #c8ffd0')
TEAL   = ramp('#123034 #1d4a4e #2c6a6c #44908c #6cb8ac')
RED    = ramp('#3a0e10 #6a1a1e #9a2a2a #c84a3c')
STAMP_G, STAMP_V, STAMP_B, STAMP_R = hx('#3f7a4c'), hx('#6a4a8a'), hx('#3a5a8a'), hx('#9a2a2a')


class Icon:
    def __init__(self):
        self.px = {}
    def put(self, x, y, c):
        if c is not None and 0 <= x < S and 0 <= y < S:
            self.px[(int(x), int(y))] = c
    def get(self, x, y): return self.px.get((int(x), int(y)))
    def rect(self, x0, y0, x1, y1, f):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): self.put(x, y, f(x, y) if callable(f) else f)
    def ell(self, cx, cy, rx, ry, f):
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - rx - 1), int(cx + rx + 2)):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0: self.put(x, y, f(x, y) if callable(f) else f)
    def poly(self, pts, f):
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            for i in range(len(pts)):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
                if (y0 <= y + 0.5 < y1) or (y1 <= y + 0.5 < y0):
                    xs.append(x0 + (y + 0.5 - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(int(math.ceil(a - 0.5)), int(math.floor(b - 0.5)) + 1):
                    self.put(x, y, f(x, y) if callable(f) else f)
    def line(self, x0, y0, x1, y1, c, w=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n + 1):
            t = i / max(1, n); x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t
            for dy in range(w):
                for dx in range(w): self.put(round(x) + dx, round(y) + dy, c(x, y) if callable(c) else c)
    def outline(self, col=INK):
        add = []
        for (x, y) in list(self.px):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + dx, y + dy) not in self.px: add.append((x + dx, y + dy))
        for p in add: self.put(*p, col)
    def glow(self, col, r=3, a=0.35):
        """a soft halo around what is drawn so far -- translucent rings fading out, added UNDER it"""
        halo = {}
        for (x, y) in self.px:
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    q = (x + dx, y + dy)
                    if q in self.px or not (0 <= q[0] < S and 0 <= q[1] < S): continue
                    d = math.hypot(dx, dy)
                    if d <= r: halo[q] = max(halo.get(q, 0), 1 - (d - 1) / r)
        for q, t in halo.items():
            self.px[q] = col[:3] + (int(255 * a * min(1, t)),)
    def image(self):
        im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        for (x, y), c in self.px.items(): im.putpixel((x, y), c)
        return im


def lit(r, x, y, x0, y0, x1, y1, base=2.5, k=1.6):
    """shade a box: brighter toward the top-left, darker toward the bottom-right"""
    u = (x - x0) / max(1, x1 - x0); v = (y - y0) / max(1, y1 - y0)
    return pick(r, base + k * (0.5 - (u + v) / 2) * 2)


# ---------------------------------------------------------------------------------------------- paper family

def paper(ic, x0, y0, x1, y1, r=PAPER, dog=True):
    """a sheet seen flat, its right and bottom edges in shade, a dog-eared top-right corner"""
    def f(x, y):
        v = 3.4 - 0.9 * (x - x0) / (x1 - x0) - 0.6 * (y - y0) / (y1 - y0)
        if x == x1 or y == y1: v -= 1.2
        if h32(x, y, 3) % 11 == 0: v -= 0.5                     # fibre
        return pick(r, v)
    ic.rect(x0, y0, x1, y1, f)
    if dog:
        for d in range(5):
            for e in range(5 - d):
                ic.px.pop((x1 - d, y0 + e), None)
        for d in range(5):
            ic.put(x1 - 4 + d, y0 + d, pick(r, 1));
            for e in range(d): ic.put(x1 - 4 + e, y0 + d, pick(r, 2 + (e == d - 1)))

def text_lines(ic, x0, x1, ys, col=TEXT, seed=0, ragged=True):
    for i, y in enumerate(ys):
        end = x1 - (h32(seed, i) % 6 if ragged else 0)
        x = x0
        while x < end:
            w = 2 + h32(seed, i, x) % 5
            for k in range(min(w, end - x)): ic.put(x + k, y, col)
            x += w + 1

def stamp(ic, cx, cy, r, col, seed=0, smudge=0.0, cross=False):
    """a round rubber stamp: ring + inner mark, inked unevenly over the paper"""
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            d = math.hypot(x - cx, y - cy)
            ring = r - 1.3 <= d <= r
            inner = d <= r - 3 and (abs(y - cy) <= 1 if not cross else (abs((x - cx) - (y - cy)) <= 0 or abs((x - cx) + (y - cy)) <= 0))
            if (ring or inner) and h32(x, y, seed) % 7 > (1 + smudge * 4):
                base = ic.get(x, y) or PAPER[3]
                ic.put(x, y, mix(base, col, 0.8))
    for i in range(int(smudge * 9)):                               # a forger's smeared ink
        x, y = cx + r - 1 + h32(i, seed) % 4, cy - 1 + h32(seed, i) % 5
        base = ic.get(x, y)
        if base: ic.put(x, y, mix(base, col, 0.5))

def arms_glyph(ic, x, y, col, arms=4):
    """a tiny figure with extra arms -- the Shed's pictogram for limb paperwork"""
    ic.put(x, y, col); ic.put(x, y + 1, col); ic.put(x, y + 2, col); ic.put(x, y + 3, col)
    ic.put(x - 1, y + 4, col); ic.put(x + 1, y + 4, col)
    for k in range(arms // 2):
        yy = y + 1 + k
        ic.put(x - 1, yy, col); ic.put(x - 2, yy - 1 + k, col)
        ic.put(x + 1, yy, col); ic.put(x + 2, yy - 1 + k, col)

def form(ic, header, stamp_col, seed, smudge=0.0, arms=4, extra=None):
    paper(ic, 13, 6, 46, 53)
    ic.rect(16, 9, 40, 12, lambda x, y: mix(PAPER[3], header, 0.85 if y < 12 else 0.6))   # header band
    for x in range(18, 38, 3): ic.put(x, 10, mix(header, PAPER[4], 0.6))                 # its title
    arms_glyph(ic, 20, 16, TEXT, arms)
    text_lines(ic, 25, 42, [17, 19, 21], seed=seed)
    text_lines(ic, 17, 42, [26, 28, 30, 32, 34, 36], seed=seed + 1)
    for x in range(17, 30): ic.put(x, 46, TEXT)                                           # signature line
    for i, x in enumerate(range(18, 28)): ic.put(x, 44 + (1 if i % 3 == 1 else 0) - (1 if i % 4 == 2 else 0), hx('#2c3a5a'))
    if extra: extra(ic)
    stamp(ic, 37, 44, 6, stamp_col, seed, smudge)
    ic.outline()


def artisan_exemption_form(ic):
    form(ic, STAMP_G, STAMP_G, 11)

def deformity_form(ic):
    form(ic, STAMP_V, STAMP_V, 12, arms=6)

def special_dispensation(ic):
    # a heavier document: ribbon down the side and a red wax seal instead of a rubber stamp
    paper(ic, 13, 6, 46, 53, dog=False)
    ic.rect(16, 9, 43, 12, lambda x, y: mix(PAPER[3], hx('#8a6a2a'), 0.75))
    for x in range(19, 41, 2): ic.put(x, 10, BRASS[4])
    text_lines(ic, 17, 43, [17, 19, 21, 23, 27, 29, 31, 33], seed=13)
    ic.rect(19, 36, 25, 52, lambda x, y: pick(RED, 2.6 - (x - 19) / 4))                     # ribbon
    ic.poly([(19, 52), (25, 52), (25, 57), (22, 54), (19, 57)], lambda x, y: pick(RED, 1.8))
    ic.ell(22, 40, 6, 6, lambda x, y: pick(RED, 3.4 - (x - 18 + y - 36) / 7))               # wax seal
    for a in range(10):
        t = a * math.pi / 5; ic.put(round(22 + 6.4 * math.cos(t)), round(40 + 6.4 * math.sin(t)), pick(RED, 2))
    ic.ell(22, 40, 3, 3, lambda x, y: pick(RED, 1.6))
    ic.put(21, 39, pick(RED, 3)); ic.put(23, 41, pick(RED, 0))
    for x in range(30, 43): ic.put(x, 46, TEXT)
    ic.outline()

def temporary_permit(ic):
    # a small yellow slip with a perforated stub and a faded, half-inked stamp
    Y = ramp('#6a5a26 #9a8638 #c8b052 #e6d27a #f4e6a4')
    paper(ic, 9, 16, 50, 43, r=Y, dog=False)
    for y in range(17, 43, 2): ic.px.pop((9, y), None); ic.put(18, y, pick(Y, 1))        # perforation + stub edge
    ic.rect(11, 19, 16, 40, lambda x, y: pick(Y, 3.2 - (y - 19) / 30))
    for y in range(21, 39, 4): ic.put(13, y, pick(Y, 0)); ic.put(14, y, pick(Y, 0))       # stub number
    for x in range(22, 46, 2): ic.put(x, 20, pick(Y, 0))                                  # TEMPORARY
    text_lines(ic, 22, 47, [25, 28, 31], col=pick(Y, 0), seed=14)
    stamp(ic, 40, 36, 5, mix(STAMP_B, Y[3], 0.35), 14, smudge=0.4)
    for (x, y) in ((24, 37), (27, 37)): ic.ell(x, y, 1.2, 1.2, None); ic.px.pop((x, y), None)   # punched holes
    ic.outline()

def forged_arms_permission(ic):
    # the artisan form again -- but the stamp is crooked and smeared and an ink blot gives it away
    def blot(ic):
        ic.ell(41, 27, 2.5, 2, hx('#2a2c3a')); ic.put(44, 29, hx('#2a2c3a')); ic.put(43, 30, hx('#2a2c3a'))
    form(ic, mix(STAMP_G, hx('#8a8a3a'), 0.5), mix(STAMP_G, hx('#5a6a2a'), 0.5), 15, smudge=0.8, extra=blot)

def rulebook_fragment(ic):
    # a torn sepia page: a little board diagram with arrows (memory exchange), a ragged bottom edge
    paper(ic, 11, 8, 48, 50, r=SEPIA, dog=False)
    for x in range(11, 49):                                                               # tear it
        cut = 44 + (h32(x, 21) % 5) + (2 if x % 7 < 2 else 0)
        for y in range(cut, 51): ic.px.pop((x, y), None)
        ic.put(x, cut - 1, pick(SEPIA, 4))
    for x in range(14, 46): ic.put(x, 11, pick(SEPIA, 1))                                 # chapter rule
    text_lines(ic, 14, 45, [14, 16], col=pick(SEPIA, 1), seed=21)
    for (cx, cy) in ((19, 26), (39, 26), (29, 35)):                                       # three spaces...
        ic.ell(cx, cy, 3.2, 3.2, pick(SEPIA, 4))
        for a in range(12):
            t = a * math.pi / 6; ic.put(round(cx + 3.6 * math.cos(t)), round(cy + 3.6 * math.sin(t)), pick(SEPIA, 1))
    for (a, b) in (((23, 25), (35, 25)), ((37, 30), (32, 34)), ((26, 34), (21, 30))):    # ...memories handed round
        ic.line(a[0], a[1], b[0], b[1], pick(SEPIA, 0))
    ic.put(34, 24, pick(SEPIA, 0)); ic.put(34, 26, pick(SEPIA, 0))
    text_lines(ic, 14, 45, [41], col=pick(SEPIA, 1), seed=22)
    ic.outline()

def silent_sentence(ic):
    # a blank card that still means something: empty, but a faint shimmer crosses it
    C = ramp('#7a7468 #a8a090 #cfc8b4 #ece6d4 #fbf8ee')
    ic.rect(12, 14, 47, 45, lambda x, y: pick(C, 3.6 - (x - 12) / 40 - (y - 14) / 45 + (0.6 if x == 12 or y == 14 else 0) - (1.6 if x == 47 or y == 45 else 0)))
    for (x, y) in ((12, 14), (47, 14), (12, 45), (47, 45)): ic.px.pop((x, y), None)     # rounded corners
    for i in range(26):                                                                   # the meaning, almost visible
        x = 16 + i; y = 33 - round(5 * math.sin(i / 4.0))
        if h32(i, 31) % 3: ic.put(x, y, mix(ic.get(x, y) or C[3], hx('#7fc8b4'), 0.7))
        if i % 3 == 0: ic.put(x, y - 3, mix(ic.get(x, y - 3) or C[3], hx('#b8a0e0'), 0.6))
        if i % 4 == 1: ic.put(x, y + 3, mix(ic.get(x, y + 3) or C[3], hx('#e0c890'), 0.55))
    for (x, y) in ((18, 20), (19, 20), (18, 21), (41, 38), (42, 38), (42, 39)):        # the quote marks, unprinted
        ic.put(x, y, mix(C[3], C[1], 0.45))
    ic.outline()
    ic.glow(hx('#bfe8dc'), r=2, a=0.22)


# ---------------------------------------------------------------------------------------------- objects

def pliers(ic):
    # closed steel jaws up right, a riveted pivot, two handles spreading down left with red rubber grips
    px_, py_ = 31, 28
    ic.poly([(px_ - 2, py_ - 1), (px_ + 1, py_ + 2), (47, 13), (45, 11)], lambda x, y: lit(STEEL, x, y, 29, 11, 47, 30, 3.1))   # upper jaw
    ic.poly([(px_ - 1, py_ + 2), (px_ + 2, py_ + 4), (49, 15), (47, 13)], lambda x, y: lit(STEEL, x, y, 30, 13, 49, 32, 2.2))   # lower jaw
    for i in range(7): ic.put(44 - i * 2, 13 + i * 2, pick(STEEL, 0))                          # the bite line
    for (ex, ey, v) in ((9, 44, 3.0), (21, 56, 2.2)):                                          # handles
        dx, dy = ex - px_, ey - py_; n = math.hypot(dx, dy); ox, oy = -dy / n * 2.2, dx / n * 2.2
        ic.poly([(px_ + ox, py_ + oy), (px_ - ox, py_ - oy), (ex - ox, ey - oy), (ex + ox, ey + oy)],
                lambda x, y, v=v: pick(STEEL, v - 0.6))
        gx, gy = px_ + dx * 0.38, py_ + dy * 0.38                                              # the grip, lower 60 %
        ic.poly([(gx + ox * 1.4, gy + oy * 1.4), (gx - ox * 1.4, gy - oy * 1.4), (ex - ox * 1.4, ey - oy * 1.4), (ex + ox * 1.4, ey + oy * 1.4)],
                lambda x, y, v=v: pick(GRIP, v - 0.4 + (0.8 if (x + y) % 5 == 0 else 0)))
    ic.ell(px_, py_ + 1, 3.6, 3.6, lambda x, y: pick(STEEL, 3.6 - (x - px_ + 3 + y - py_ + 2) / 4))   # pivot
    ic.put(px_, py_ + 1, pick(STEEL, 1)); ic.put(px_ - 1, py_, pick(STEEL, 4))
    ic.outline()

def forgotten_elevator_button(ic):
    # a round brass bezel on a square plate, an ivory button with a strange engraved glyph, faint green glow
    ic.rect(12, 12, 47, 47, lambda x, y: lit(BRASS, x, y, 12, 12, 47, 47, 2.0, 1.4))
    for (x, y) in ((15, 15), (44, 15), (15, 44), (44, 44)):                                   # screws
        ic.put(x, y, pick(BRASS, 4)); ic.put(x + 1, y, pick(BRASS, 1)); ic.put(x, y + 1, pick(BRASS, 1))
    ic.ell(30, 30, 13, 13, lambda x, y: pick(BRASS, 3.6 - (x - 18 + y - 18) / 14))           # bezel
    ic.ell(30, 30, 10, 10, lambda x, y: pick(BRASS, 0.8 + (x - 20 + y - 20) / 20))           # its inner lip
    ic.ell(30, 30, 9, 9, lambda x, y: pick(BONE, 4.2 - math.hypot(x - 26, y - 26) / 5))     # the button
    G, G2 = hx('#1f5a32'), hx('#3f8f5a')                                                   # faintly lit green
    for (x, y) in ((30, 24), (29, 25), (31, 25), (28, 27), (32, 27), (30, 27), (30, 28), (27, 30), (33, 30),
                   (30, 31), (28, 33), (29, 34), (31, 34), (32, 33), (30, 36)):              # the glyph: no number
        ic.put(x, y, G2 if (x + y) % 3 else G)
    for (x, y) in ((24, 22), (23, 24), (36, 37)): ic.put(x, y, pick(BONE, 4))               # shine
    ic.outline()

def market_map(ic):
    # a folded paper map of the hangar market: three panels, paths, a little hangar arch, a red X
    panels = [(8, 13, 22, 47, 3.3), (22, 11, 37, 45, 2.6), (37, 13, 52, 47, 3.1)]
    for i, (x0, y0, x1, y1, v) in enumerate(panels):
        ic.poly([(x0, y0 if i != 1 else y0), (x1, y0 if i == 0 else y1 - 34), (x1, y1 if i == 0 else y1), (x0, y1 if i != 1 else y1 + 2)],
                lambda x, y, v=v, x0=x0: pick(PAPER, v - (x - x0) / 30 + (0.4 if h32(x, y) % 13 == 0 else 0)))
    for x in (22, 37):
        for y in range(11, 48):
            if ic.get(x, y): ic.put(x, y, pick(PAPER, 1))                                     # folds
    P = hx('#6a5a3e')
    for (a, b) in (((11, 40), (19, 30)), ((19, 30), (30, 34)), ((30, 34), (41, 24)), ((41, 24), (48, 30))):
        ic.line(a[0], a[1], b[0], b[1], P)
    for i in range(7):                                                                        # the hangar's arch
        t = math.pi * i / 6; ic.put(round(43 + 4 * math.cos(t)), round(21 - 3 * math.sin(t)), hx('#4a5a6a'))
    W = hx('#3a6a8a')
    for y in range(36, 46): ic.put(26 + (y % 3 == 0), y, W)                                  # the drain
    for d in range(-2, 3): ic.put(31 + d, 20 + d, RED[2]); ic.put(31 + d, 20 - d, RED[2])   # X
    ic.outline()

def game_prototype(ic):
    # Ortolan's prototype "Sects & Stakes": a box in 3/4 whose lid shows a cat idol with a golden halo and a ring of
    # hooded cultists; a cat meeple (the winning strategy) and a robed cultist pawn stand on top
    BOX = ramp('#2a1014 #4a1c22 #6e2c30 #944040')
    LID = ramp('#1a1024 #2c1a3c #44285a #5e3a7a')
    CAT = ramp('#141218 #2a2630 #45404c')
    ic.poly([(9, 29), (28, 39), (28, 51), (9, 41)], lambda x, y: pick(BOX, 2.8 - (y - 29) / 24))          # left side
    ic.poly([(28, 39), (51, 27), (51, 39), (28, 51)], lambda x, y: pick(BOX, 1.4 - (x - 28) / 50))         # right side
    ic.poly([(9, 27), (30, 16), (51, 25), (28, 37)], lambda x, y: pick(LID, 2.6 - (x - 9) / 60))           # the lid
    for i in range(22): ic.put(10 + i, 27 - i // 2, pick(BRASS, 3)); ic.put(29 + i, 36 - (i * 11) // 22, pick(BRASS, 1))   # gilt edges
    for i in range(23): ic.put(9 + i, 28 + (i * 10) // 22, pick(LID, 3.4)); ic.put(28 + i, 38 - (i * 12) // 23, pick(BOX, 0.4))   # lid lip
    cx, cy = 30, 26                                                                                        # the cat idol...
    for a_ in range(20):                                                                                   # ...its halo
        t = a_ * math.pi / 10; ic.put(round(cx + 5.5 * math.cos(t)), round(cy - 1 + 3.2 * math.sin(t)), pick(BRASS, 4 if math.sin(t) < 0 else 3))
    ic.ell(cx, cy, 2.6, 2.2, lambda x, y: pick(CAT, 1.6))
    ic.put(cx - 2, cy - 3, pick(CAT, 1)); ic.put(cx + 2, cy - 3, pick(CAT, 1))                          # ears
    ic.put(cx - 1, cy - 1, hx('#e0c040')); ic.put(cx + 1, cy - 1, hx('#e0c040'))                         # eyes
    for (px, py) in ((19, 27), (23, 31), (37, 30), (41, 25), (25, 22), (35, 21)):                          # hooded cultists
        ic.put(px, py, RED[3]); ic.put(px, py + 1, RED[2])
    # a robed cultist pawn on the left, a cat meeple on the right
    ic.poly([(14, 25), (17, 25), (18, 28), (13, 28)], lambda x, y: pick(RED, 3 - (x - 13) / 4))
    ic.ell(15.5, 23, 1.6, 1.6, lambda x, y: pick(RED, 3.4)); ic.put(15, 23, pick(RED, 1))
    ic.rect(42, 15, 46, 20, lambda x, y: pick(CAT, 2 - (x - 42) / 4))
    ic.put(42, 14, pick(CAT, 2)); ic.put(46, 14, pick(CAT, 1)); ic.put(43, 16, hx('#e0c040')); ic.put(45, 16, hx('#e0c040'))
    ic.line(47, 19, 49, 16, pick(CAT, 1))                                                                  # its tail
    ic.rect(14, 41, 22, 45, lambda x, y: pick(PAPER, 3.6))                                                 # label
    for x in range(15, 22, 2): ic.put(x, 43, TEXT)
    ic.outline()

def black_cactus_card(ic):
    # the Black Cactus from Absolutely Profane Life: Normality -- a black-bordered card in a collector's toploader:
    # a black saguaro against a violet dusk in the art box, a title bar, a rules box, a rarity gem
    BLK = ramp('#0c0c0e #1a1a1e #2a2a30')
    FRM = ramp('#4a3a28 #7a6440 #a88c5a #cdb382')
    SKY = ramp('#1a1030 #34205a #5a3a86 #8a5aa8 #c08ab8')
    x0, y0, x1, y1 = 15, 7, 45, 52
    ic.rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2, lambda x, y: hx('#9aa6a8')[:3] + (110,))            # the toploader
    ic.rect(x0, y0, x1, y1, lambda x, y: pick(BLK, 1.2 - (x - x0 + y - y0) / 80))                # black border
    ic.rect(x0 + 2, y0 + 2, x1 - 2, y1 - 2, lambda x, y: pick(FRM, 2.4 - (y - y0) / 50))         # inner frame
    ic.rect(x0 + 3, y0 + 3, x1 - 3, y0 + 6, lambda x, y: pick(FRM, 3.4))                         # title bar
    for x in range(x0 + 4, x0 + 20, 2): ic.put(x, y0 + 5, BLK[0])                                 # BLACK CACTUS
    ic.ell(x1 - 6, y0 + 5, 1.4, 1.4, hx('#2a6a3a'))                                              # its cost
    ic.rect(x0 + 3, y0 + 8, x1 - 3, y0 + 26, lambda x, y: pick(SKY, 4.2 - (y - y0 - 8) / 4.5))   # the art: dusk
    for (sx, sy) in ((x0 + 6, y0 + 11), (x1 - 7, y0 + 10), (x0 + 12, y0 + 9)): ic.put(sx, sy, hx('#e8d8f0'))
    ic.rect(x0 + 3, y0 + 24, x1 - 3, y0 + 26, lambda x, y: pick(BLK, 2))                          # dark ground
    cx = (x0 + x1) // 2
    ic.rect(cx - 1, y0 + 12, cx + 1, y0 + 25, BLK[0])                                             # the saguaro
    ic.rect(cx - 6, y0 + 16, cx - 4, y0 + 21, BLK[0]); ic.rect(cx - 6, y0 + 20, cx - 1, y0 + 21, BLK[0])
    ic.rect(cx + 4, y0 + 14, cx + 6, y0 + 19, BLK[0]); ic.rect(cx + 1, y0 + 18, cx + 6, y0 + 19, BLK[0])
    for (px, py) in ((cx - 1, y0 + 12), (cx - 6, y0 + 16), (cx + 4, y0 + 14)): ic.put(px + 1, py, SKY[4])   # rim light
    ic.put(cx, y0 + 11, hx('#c84a8a'))                                                            # one flower
    ic.rect(x0 + 3, y0 + 28, x1 - 3, y0 + 29, lambda x, y: pick(FRM, 3.6))                       # type line
    ic.rect(x0 + 3, y0 + 31, x1 - 3, y1 - 5, lambda x, y: pick(PAPER, 3.4))                       # rules box
    text_lines(ic, x0 + 5, x1 - 5, [y0 + 33, y0 + 35, y0 + 37, y0 + 40], col=TEXT, seed=61)
    ic.put(cx, y1 - 3, hx('#e0a030')); ic.put(cx - 1, y1 - 3, hx('#a06a20'))                     # rarity gem
    for i in range(9):                                                                            # toploader shine
        for (x, y) in ((x0 + 1 + i, y0 + 9 - i), (x0 + 1 + i, y0 + 12 - i)):
            ic.put(x, y, mix(ic.get(x, y) or BLK[1], hx('#ffffff'), 0.35))
    ic.outline()

def probability_die(ic):
    # a bone d6 in 3/4 -- the top face shows seven pips, which a die shouldn't
    top = [(30, 12), (47, 20), (30, 28), (13, 20)]
    ic.poly(top, lambda x, y: pick(BONE, 4.2 - (y - 12) / 30))
    ic.poly([(13, 20), (30, 28), (30, 48), (13, 39)], lambda x, y: pick(BONE, 3.2 - (y - 20) / 40))
    ic.poly([(30, 28), (47, 20), (47, 39), (30, 48)], lambda x, y: pick(BONE, 2.0 - (x - 30) / 40))
    D = hx('#2a2420')
    for (x, y) in ((24, 18), (30, 15), (36, 18), (30, 20), (24, 22), (36, 22), (30, 25)):  # seven
        ic.put(x, y, D); ic.put(x + 1, y, D)
    for (x, y) in ((18, 28), (25, 38)): ic.ell(x, y, 1.3, 1.3, D)                            # two
    for (x, y) in ((35, 31), (39, 35), (43, 31), (35, 40), (43, 39)): ic.ell(x, y, 1.1, 1.1, hx('#4a3a5a'))  # five, faintly violet
    ic.outline()
    ic.glow(VIOL[2], r=2, a=0.25)

def hopsalot_figurine(ic):
    # a collector's box with a window: Maxim Hopsalot, patron of Lagerlandia -- hop-cone crown, foam beard, a raised
    # tankard -- and beside it the empty plastic rings of the six-pack Ortolan drank
    BOXC = ramp('#1a1e3a #2a3060 #3c4688 #5662b0')
    HOP = ramp('#1f3a14 #35601f #548a2c #7fb444')
    TUN = ramp('#3a2a10 #6a4a1a #9a7028 #c89a40')
    SKN = ramp('#5a3a2a #8a5a40 #b88060 #dca888')
    FOAM = ramp('#8a8878 #c8c4b0 #f0ece0')
    ic.poly([(9, 8), (12, 5), (40, 5), (37, 8)], lambda x, y: pick(BOXC, 3))                     # box top
    ic.poly([(37, 8), (40, 5), (40, 49), (37, 52)], lambda x, y: pick(BOXC, 0.6))                # box side
    ic.rect(9, 8, 37, 52, lambda x, y: pick(BOXC, 2.2 - (x - 9) / 40))                           # box front
    ic.rect(10, 9, 36, 14, lambda x, y: pick(BRASS, 3.4 - (y - 9) / 6))                          # gold header
    for x in range(13, 34, 2): ic.put(x, 11, pick(BRASS, 1) if x % 4 else RED[2])              # the brand
    ic.rect(12, 17, 34, 48, lambda x, y: pick(BOXC, 0.4))                                        # the window's inside
    # Maxim Hopsalot on his plinth
    ic.rect(17, 45, 29, 47, lambda x, y: pick(STEEL, 2.6 - (x - 17) / 10))
    ic.ell(23, 38, 6.5, 7, lambda x, y: pick(TUN, 3.4 - (x - 17) / 7 - (y - 31) / 14))         # round body
    ic.rect(18, 37, 28, 38, pick(TUN, 0.8))                                                      # belt
    ic.put(23, 37, pick(BRASS, 4)); ic.put(23, 38, pick(BRASS, 3))
    ic.ell(23, 27, 3.6, 3.6, lambda x, y: pick(SKN, 3.2 - (x - 20) / 5))                        # head
    ic.put(22, 26, INK); ic.put(25, 26, INK)                                                     # merry eyes
    ic.ell(23, 30.5, 3.6, 2.6, lambda x, y: pick(FOAM, 2.4 - (x - 20) / 6))                     # a beard like foam
    for (hx_, hy_) in ((20, 22), (23, 21), (26, 22)):                                            # crown of hop cones
        ic.ell(hx_, hy_, 1.4, 1.9, lambda x, y: pick(HOP, 3 - (y - 20) / 2))
        ic.put(hx_, hy_ - 2, pick(HOP, 1))
    ic.rect(29, 28, 32, 33, lambda x, y: pick(BRASS, 3.2 - (x - 29) / 3))                       # the tankard
    ic.rect(29, 27, 32, 27, pick(FOAM, 2)); ic.put(30, 26, pick(FOAM, 2))
    ic.put(33, 30, pick(BRASS, 1)); ic.put(33, 31, pick(BRASS, 1))
    ic.line(28, 33, 29, 31, pick(SKN, 2))                                                        # his raised arm
    for i in range(5):                                                                           # plastic shine, in the corner
        for (x, y) in ((13 + i, 22 - i), (13 + i, 25 - i)): ic.put(x, y, mix(ic.get(x, y) or BOXC[1], GLASS[4], 0.5))
    ic.outline()
    # the empty six-pack rings, lying next to the box
    rings = {}
    for r_ in range(2):
        for c_ in range(3):
            cx, cy = 44 + c_ * 6 - r_ * 3, 47 + r_ * 5
            for y in range(cy - 3, cy + 4):
                for x in range(cx - 4, cx + 5):
                    d = ((x - cx) / 3.3) ** 2 + ((y - cy) / 2.3) ** 2
                    if 0.45 <= d <= 1.0: rings[(x, y)] = hx('#d4d8d2') if y <= cy else hx('#8e968e')
    for p, c in rings.items():
        if p not in ic.px or ic.px[p] == INK: ic.put(*p, c)
    for (x, y) in list(rings):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in rings and q not in ic.px: ic.put(*q, INK)

def fate_altering_piece(ic):
    # an obsidian spire piece with one eye; it gives off an unsettling violet-red light
    ic.ell(30, 50, 10, 3.2, lambda x, y: pick(OBSID, 2.4 - (x - 30) / 10))
    ic.poly([(22, 49), (38, 49), (34, 42), (26, 42)], lambda x, y: pick(OBSID, 3 - (x - 22) / 8))
    ic.poly([(26, 42), (34, 42), (31, 10), (29, 10)], lambda x, y: pick(OBSID, 3.4 - (x - 26) / 3))
    ic.ell(30, 38, 6, 1.6, lambda x, y: pick(OBSID, 3 - (x - 24) / 6))                         # collar
    ic.ell(30, 10, 2.6, 2.6, lambda x, y: pick(OBSID, 3.6 - (x - 28 + y - 8) / 3))              # orb on top
    ic.ell(30, 26, 3.4, 2.2, hx('#d8c0e0'))                                                 # the eye
    ic.ell(30, 26, 1.4, 1.6, hx('#c8202a')); ic.put(30, 26, INK)
    for y in range(12, 40, 4): ic.put(28, y, pick(OBSID, 3))
    ic.outline()
    ic.glow(hx('#b0306a'), r=3, a=0.4)

def chrono_slurry_toadlet(ic):
    # a brass carrier jar: glass cylinder, murky slurry, the toadlet's big eyes staring out
    ic.rect(17, 18, 43, 50, lambda x, y: pick(GLASS, 2.6 - abs(x - 24) / 12))               # glass
    ic.rect(18, 34, 42, 49, lambda x, y: mix(pick(SLIME, 2.4 - (y - 34) / 16), GLASS[2], 0.2))   # slurry
    for i in range(8): ic.put(20 + h32(i, 41) % 21, 35 + h32(i, 42) % 13, pick(SLIME, 4))     # bubbles
    ic.ell(30, 34, 8, 6, lambda x, y: pick(TOAD, 3.6 - (x - 22) / 8 - (y - 28) / 10))        # the toadlet
    for ex in (25, 35):
        ic.ell(ex, 29, 3, 3, lambda x, y, ex=ex: pick(TOAD, 3.4 - (x - ex + 3) / 4))
        ic.ell(ex, 29, 1.8, 1.8, hx('#d8b030')); ic.put(ex, 29, INK); ic.put(ex, 30, INK)
    for x in range(26, 35): ic.put(x, 36, pick(TOAD, 1))                                      # its mouth
    for x in (20, 21):
        for y in range(19, 33): ic.put(x, y, mix(ic.get(x, y), GLASS[4], 0.6))               # glass shine
    ic.rect(15, 13, 45, 17, lambda x, y: lit(BRASS, x, y, 15, 13, 45, 17, 2.6, 1.2))         # lid
    ic.rect(15, 50, 45, 53, lambda x, y: lit(BRASS, x, y, 15, 50, 45, 53, 2.2, 1.2))         # base
    for i in range(9):                                                                        # carrying handle
        t = math.pi * i / 8; ic.put(round(30 + 9 * math.cos(t)), round(12 - 6 * math.sin(t)), pick(BRASS, 3 if i < 4 else 2))
    for x in (16, 44):
        for y in range(18, 50, 8): ic.put(x, y, pick(BRASS, 3))                               # rivets
    ic.outline()

def corrosive_cultivar(ic):
    # a rusted tin eaten from the inside by the bred rot: pale ochre fronds and spore caps spilling over the rim
    ic.rect(18, 32, 42, 52, lambda x, y: pick(RUST, 3.4 - (x - 18) / 10 + (0.6 if h32(x, y, 51) % 5 == 0 else 0)))
    ic.ell(30, 32, 12, 3, lambda x, y: pick(RUST, 1.2))                                      # the opening
    for (x, y) in ((24, 44), (25, 45), (35, 40), (36, 41), (36, 42)):                         # holes eaten through
        ic.px.pop((x, y), None)
    for y in range(36, 52):
        for x in (22, 31, 38):
            if h32(x, y, 52) % 3 == 0: ic.put(x, y, pick(ROT, 2))                              # rot veins on the tin
    for (bx, by, ex, ey) in ((26, 31, 20, 16), (30, 31, 31, 11), (34, 31, 41, 17), (28, 31, 24, 22), (33, 31, 37, 24)):
        ic.line(bx, by, ex, ey, lambda x, y: pick(ROT, 3.2 - (y - 10) / 30))
        ic.line(bx + 1, by, ex + 1, ey, lambda x, y: pick(ROT, 2.2 - (y - 10) / 30))
        ic.ell(ex, ey, 2.4, 2, lambda x, y, ex=ex, ey=ey: pick(RUST, 4.4 - (x - ex + y - ey + 4) / 3))   # spore caps
        ic.put(ex - 1, ey - 1, pick(ROT, 4))
    for (x, y) in ((19, 53), (20, 54), (41, 53)): ic.put(x, y, pick(RUST, 2))                # drips
    ic.outline()


ICONS = [
    ('pliers', pliers),
    ('forgotten_elevator_button', forgotten_elevator_button),
    ('market_map', market_map),
    ('artisan-exemption-form', artisan_exemption_form),
    ('deformity-form', deformity_form),
    ('special-dispensation', special_dispensation),
    ('temporary-permit', temporary_permit),
    ('forged-arms-permission', forged_arms_permission),
    ('rulebook-fragment', rulebook_fragment),
    ('silent-sentence', silent_sentence),
    ('game-prototype', game_prototype),
    ('black-cactus-card', black_cactus_card),
    ('probability-die', probability_die),
    ('hopsalot-figurine', hopsalot_figurine),
    ('fate-altering-piece', fate_altering_piece),
    ('chrono-slurry-toadlet', chrono_slurry_toadlet),
    ('corrosive_cultivar', corrosive_cultivar),
]

def main(out):
    os.makedirs(out, exist_ok=True)
    cols = 6
    sheet = Image.new('RGBA', (cols * 64, ((len(ICONS) + cols - 1) // cols) * 64), (24, 40, 30, 255))
    for i, (iid, fn) in enumerate(ICONS):
        ic = Icon(); fn(ic)
        im = ic.image(); im.save(os.path.join(out, f'{iid}.png'))
        sheet.alpha_composite(im, ((i % cols) * 64 + 2, (i // cols) * 64 + 2))
    with open(os.path.join(out, 'icons.txt'), 'w') as fh: fh.write('\n'.join(i for i, _ in ICONS) + '\n')
    sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(os.path.join(out, 'sheet.png'))
    print('ok', len(ICONS), out)

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '/tmp/item_icons')
