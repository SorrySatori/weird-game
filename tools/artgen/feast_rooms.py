"""The rooms of The Cardinal Feast (CardinalFeastScene), painted as native 1067x600 pixel art for the mini-game's
top-down / three-quarter view (the north wall stands up as a face, the floor is seen from above, side and south walls
are their stone caps). Sized for the half-size cast tokens (feast_cast.py, ~40-50 px wide, ~70-80 px tall).

  nave       the cathedral nave on a Sunday: flagstones, a red runner up the aisle, eight pews, the pulpit, the
             confession booth on the west wall, lancet windows, the north doorway to the Long Hall, candle stands
  hall       the Long Hall: chequered flags, a fireplace in the north wall, the long table (cloth, red runner, plates,
             goblets, candelabra, bread, a covered dish), the empty seat of honour at its east head, the kitchen door in
             the west wall, the way back to the nave in the south wall
  hall_dark  the same hall with every candle snuffed and the fire out -- the Infinite Fold; a faceless figure sits in
             the seat of honour, the table is set for one

Every room also writes its gameplay layout (walkable bounds, colliders = the full drawn footprint of each object, so a
token can never stand "inside" a drawn prop, doors, interaction spots, guest positions, candle flames for the animated
flame sprites) to feast_rooms.json -- the scene reads that file, so art and gameplay cannot drift apart.
python3 feast_rooms.py <outdir>  ->  nave.png hall.png hall_dark.png flame.png (4 frames of 8x12) feast_rooms.json feast_rooms.gpl"""
import sys, os, math, json
from PIL import Image
from common import ramp, make_noise, h32

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
W, H = 1067, 600
R = ramp
CX = W // 2
FLOOR = (64, 118, 1003, 548)                  # x0, y0, x1, y1 of the floor seen from above
WALL_TOP = 20                                 # the north wall's cap starts here; its face runs down to FLOOR y0

STONE  = R('#120f0c #1b1712 #251f18 #2f281f #3a3126 #463b2e #534537 #615141 #705e4c #806b57 #8f7a64')
STONE2 = R('#110e0b #1a1511 #241d17 #2e251d #3a2f25 #46392d #534436 #614f40 #6f5b4a')
WALLS  = R('#0c0c0d #131416 #1b1c1f #242629 #2e3033 #393b3e #45474a #525456 #616263')
OAK    = R('#0c0805 #140d08 #1d130b #27190f #312013 #3c2818 #48301d #553923 #62432a')
LINEN  = R('#2a2722 #3a362f #4b463c #5d574b #6f695a #827b6a #958d7b #a69f8c')
RUG    = R('#130606 #1e0908 #2a0d0b #37120e #451812 #531e16 #61251b')
GOLD   = R('#2e200a #4e3812 #74561c #9a7628 #bc963a #d8b658')
IRON   = R('#0e0e0e #171716 #21211f #2c2c29 #383834 #46453f #55534c')
GLASS  = [(26, 34, 58), (36, 48, 78), (70, 30, 38), (98, 44, 46), (96, 78, 34), (40, 66, 48), (58, 70, 92)]
WAX    = R('#5a5240 #7a705a #9a9078 #b8ae94 #cfc6ac')
FIRE   = [(90, 30, 12), (150, 60, 20), (210, 110, 40), (240, 170, 80), (255, 226, 160)]
PEWTER = R('#2a2a28 #3c3c38 #50504a #66655e #7c7a72 #92908a')
FOOD   = [(70, 38, 22), (98, 56, 30), (126, 78, 40), (150, 102, 56), (96, 40, 30), (120, 56, 40), (84, 92, 48)]
INK = (14, 10, 8)
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
nF, nM, nL = make_noise(3, 401, W + 8, H + 8), make_noise(9, 402, W + 8, H + 8), make_noise(31, 403, W + 8, H + 8)


class Canvas:
    """colour buffer + an 'emissive' mask (flames, fire, glass) that the lighting pass leaves alone"""
    def __init__(self):
        self.c = [(6, 5, 4)] * (W * H)
        self.emit = bytearray(W * H)

    def put(self, x, y, col, emit=0):
        x, y = int(x), int(y)
        if 0 <= x < W and 0 <= y < H:
            self.c[y * W + x] = col
            self.emit[y * W + x] = emit

    def get(self, x, y): return self.c[int(y) * W + int(x)]

    def shade(self, x, y, k):
        """darken (k < 1) / lighten (k > 1) a pixel in place"""
        x, y = int(x), int(y)
        if 0 <= x < W and 0 <= y < H and not self.emit[y * W + x]:
            c = self.c[y * W + x]
            self.c[y * W + x] = (min(255, int(c[0] * k)), min(255, int(c[1] * k)), min(255, int(c[2] * k)))

    def tone(self, x, y, rp, v):
        """a ramp colour for tone v (0..1), ordered-dithered"""
        i = v * (len(rp) - 1) + (BAYER[y % 4][x % 4] / 16 - 0.47) * 0.9
        self.put(x, y, rp[max(0, min(len(rp) - 1, int(round(i))))])

    def rect(self, x0, y0, x1, y1, rp, vf):
        for y in range(int(y0), int(y1)):
            for x in range(int(x0), int(x1)):
                self.tone(x, y, rp, vf(x, y))

    def outline(self, x0, y0, x1, y1, col=INK):
        for x in range(int(x0), int(x1)): self.put(x, y0, col); self.put(x, y1 - 1, col)
        for y in range(int(y0), int(y1)): self.put(x0, y, col); self.put(x1 - 1, y, col)

    def ao(self, x0, y0, x1, y1, r=7, k=0.5):
        """contact shadow on the floor around an object's footprint"""
        for y in range(int(y0 - r), int(y1 + r)):
            for x in range(int(x0 - r), int(x1 + r)):
                if x0 <= x < x1 and y0 <= y < y1: continue
                dx = max(x0 - x, 0, x - (x1 - 1)); dy = max(y0 - y, 0, y - (y1 - 1))
                d = math.hypot(dx, dy)
                if d < r: self.shade(x, y, 1 - k * (1 - d / r) ** 1.6)


# ---- floors -------------------------------------------------------------------------------------------------------------
def stone_px(cv, xx, yy, rp, xa, ya, xb, yb, base, tint_, crack, chip):
    """one pixel of a flag spanning [xa, xb) x [ya, yb): a dirty joint, chipped corners, a lit upper arris, a crack"""
    ex, ey = min(xx - xa, xb - 1 - xx), min(yy - ya, yb - 1 - yy)
    corner = min(xx - xa, xb - 1 - xx) + min(yy - ya, yb - 1 - yy)
    v = base + (nF(xx * 1.4, yy * 1.4) - 0.5) * 0.1 + (nM(xx * 0.7, yy * 0.7) - 0.5) * 0.12
    if ex == 0 or ey == 0 or corner < 2 + chip:
        v = 0.17 + (nF(xx * 2, yy * 2) - 0.5) * 0.08
    elif yy - ya == 1 or xx - xa == 1: v += 0.05
    elif yb - 1 - yy == 1 or xb - 1 - xx == 1: v -= 0.05
    if crack and ex > 2 and ey > 2 and abs((xx - xa) * 0.6 - (yy - ya) - 2 + 2 * math.sin(xx * 0.5)) < 0.5: v -= 0.2
    cv.tone(xx, yy, rp, v)
    if tint_ and ex > 0 and ey > 0:
        c = cv.get(xx, yy)
        cv.c[yy * W + xx] = (min(255, c[0] + 3 * tint_), c[1], max(0, c[2] - 3 * tint_))


def flags_random(cv, x0, y0, x1, y1, rp, cell=30, seed=0):
    """flagstones packed on a grid with no running joints: cells merge into 1x1, 2x1, 1x2 and 2x2 stones"""
    cols, rows = (x1 - x0 + cell - 1) // cell, (y1 - y0 + cell - 1) // cell
    taken = set()
    for j in range(rows):
        for i in range(cols):
            if (i, j) in taken: continue
            hh = h32(i, j, seed)
            opts = [(1, 1)] * 4 + [(2, 1)] * 3 + [(1, 2)] * 2 + [(2, 2)] * 2 + [(3, 2)]
            sw, sh = opts[hh % len(opts)]
            while sw > 1 and any((i + a, j + b) in taken or i + a >= cols for a in range(sw) for b in range(sh)): sw -= 1
            while sh > 1 and any((i + a, j + b) in taken or j + b >= rows for a in range(sw) for b in range(sh)): sh -= 1
            for a in range(sw):
                for b in range(sh): taken.add((i + a, j + b))
            xa, ya = x0 + i * cell, y0 + j * cell
            xb, yb = min(x1, xa + sw * cell), min(y1, ya + sh * cell)
            base = 0.44 + ((hh >> 4) % 100) / 100 * 0.2
            tint_ = ((hh >> 12) % 3) - 1
            for yy in range(ya, yb):
                for xx in range(xa, xb):
                    stone_px(cv, xx, yy, rp, xa, ya, xb, yb, base, tint_, (hh >> 16) % 6 == 0, (hh >> 20) % 3)


def tiles_checker(cv, x0, y0, x1, y1, rp, cell=32, seed=0):
    """square flags laid as a chequer of two stones (the hall), worn and unevenly set"""
    for j in range((y1 - y0 + cell - 1) // cell):
        for i in range((x1 - x0 + cell - 1) // cell):
            hh = h32(i, j, seed)
            xa, ya = x0 + i * cell, y0 + j * cell
            xb, yb = min(x1, xa + cell), min(y1, ya + cell)
            base = (0.6 if (i + j) % 2 else 0.36) + ((hh >> 4) % 100) / 100 * 0.1
            for yy in range(ya, yb):
                for xx in range(xa, xb):
                    stone_px(cv, xx, yy, rp, xa, ya, xb, yb, base, 0, (hh >> 16) % 7 == 0, (hh >> 20) % 3)


def scatter(cv, x0, y0, x1, y1, n, seed, kind='rush'):
    """floor litter: rush stalks (the hall), wax drips + crumbs; deterministic"""
    for k in range(n):
        x = x0 + h32(k, seed, 1) % (x1 - x0); y = y0 + h32(k, seed, 2) % (y1 - y0)
        if kind == 'rush':
            a = (h32(k, seed, 3) % 180) / 180 * math.pi; ln = 3 + h32(k, seed, 4) % 5
            for t in range(ln): cv.put(x + math.cos(a) * t, y + math.sin(a) * t * 0.6, (96, 84, 52) if t % 2 else (74, 64, 40))
        else:
            cv.put(x, y, WAX[2]); cv.put(x + 1, y, WAX[1])


def runner(cv, x0, y0, x1, y1):
    """a long red runner with a gold-ish border, worn pale along its middle, frayed at the end"""
    for y in range(int(y0), int(y1)):
        for x in range(int(x0), int(x1)):
            ex = min(x - x0, x1 - 1 - x)
            v = 0.5 + (nF(x * 2, y * 0.6) - 0.5) * 0.18 + (0.04 if (x + y) % 2 else -0.02)
            if 3 <= ex <= 4: cv.put(x, y, GOLD[2] if (y // 2) % 3 else GOLD[3]); continue
            if ex < 3: v -= 0.12
            v += 0.12 * max(0.0, 1 - abs(x - (x0 + x1) / 2) / ((x1 - x0) * 0.22)) * (nM(x, y * 0.3) > 0.45)   # trodden pale
            if y > y1 - 3 and (x * 7) % 3: continue
            cv.tone(x, y, RUG, v)
    cv.ao(x0, y0, x1, y1, r=3, k=0.25)


# ---- walls --------------------------------------------------------------------------------------------------------------
def north_wall(cv, openings=(), windows=(), banners=()):
    """the north wall: a cap seen from above, then the coursed ashlar face down to the floor, a plinth, soot over the
    windows, damp at the foot"""
    x0, x1 = 0, W
    face0, face1 = WALL_TOP + 10, FLOOR[1]
    for y in range(WALL_TOP, face0):                                                  # the cap
        for x in range(x0, x1):
            v = 0.62 + (nF(x * 1.5, y * 3) - 0.5) * 0.12 - (0.2 if y == face0 - 1 else 0) + (0.08 if y == WALL_TOP else 0)
            if (x + h32(y, 3) % 20) % 41 == 0: v -= 0.25
            cv.tone(x, y, WALLS, v)
    course = 13
    for y in range(face0, face1):
        r_ = (y - face0) // course
        off = (r_ % 2) * 23
        for x in range(x0, x1):
            bx = (x + off) // 46
            ey = (y - face0) % course
            ex = (x + off) % 46
            v = 0.4 + (h32(bx, r_, 9) % 100) / 100 * 0.16 + (nF(x * 1.2, y * 1.2) - 0.5) * 0.12 + (nM(x * 0.6, y) - 0.5) * 0.1
            if ey == 0 or ex == 0: v -= 0.3
            elif ey == 1: v += 0.06
            if y > face1 - 12: v -= 0.12 + (0.1 if y > face1 - 4 else 0)                 # the plinth + damp foot
            if y == face1 - 12: v += 0.1
            v -= 0.16 * max(0.0, 1 - (y - face0) / 14)                                       # the cap's shadow on the face
            cv.tone(x, y, WALLS, v)
    for (wx, ww) in windows: lancet(cv, wx, face0 + 10, ww, face1 - face0 - 30)
    for (bx, bw) in banners: banner(cv, bx, face0 + 6, bw, 50)
    for (ox, ow, glow) in openings: doorway(cv, ox, ow, face0 + 18, face1, glow)


def lancet(cv, cx, top, w, h):
    """a pointed lancet of dim stained glass in a stone reveal, soot streaking up from it"""
    hw = w / 2
    def inside(x, y, m=0.0):
        if y < top + hw:                                                              # the pointed head
            dy = top + hw - y
            return abs(x + 0.5 - cx) <= hw - m - dy * 0.9 and dy <= hw * 1.1
        return abs(x + 0.5 - cx) <= hw - m and y <= top + h
    for y in range(int(top - 3), int(top + h + 3)):
        for x in range(int(cx - hw - 3), int(cx + hw + 4)):
            if inside(x, y, -2.5) and not inside(x, y):
                cv.tone(x, y, WALLS, 0.55 if x < cx else 0.3)                             # the reveal
            elif inside(x, y):
                lead = (y - top) % 9 == 0 or (x - int(cx)) % 6 == 0
                if lead: cv.put(x, y, (16, 14, 14), 1); continue
                cell = h32((x - int(cx)) // 6, (y - top) // 9, int(cx))
                g = GLASS[cell % len(GLASS)]
                f = 0.75 + (nF(x * 2, y * 2) - 0.5) * 0.3 - 0.25 * (y - top) / h
                cv.put(x, y, (int(g[0] * f), int(g[1] * f), int(g[2] * f)), 1)
    for y in range(int(top - 26), int(top - 2)):                                       # soot above it
        for x in range(int(cx - hw), int(cx + hw)):
            if nF(x * 3, y * 0.5) > 0.45: cv.shade(x, y, 0.88)


def banner(cv, cx, top, w, h):
    """a hanging cloth banner: red, a gold cross, a pointed foot"""
    for y in range(top, top + h + 6):
        for x in range(int(cx - w / 2), int(cx + w / 2)):
            if y > top + h and abs(x + 0.5 - cx) > (top + h + 6 - y) * w / 12: continue
            v = 0.5 + (0.18 if x < cx - w / 4 else -0.1 if x > cx + w / 4 else 0.04) + (nF(x * 2, y) - 0.5) * 0.12
            cv.tone(x, y, RUG, v)
    for y in range(top + 10, top + 34): cv.put(cx - 1, y, GOLD[4]); cv.put(cx, y, GOLD[2])
    for x in range(int(cx - 7), int(cx + 7)): cv.put(x, top + 17, GOLD[4]); cv.put(x, top + 18, GOLD[2])
    for x in range(int(cx - w / 2 - 2), int(cx + w / 2 + 2)): cv.put(x, top - 1, IRON[4]); cv.put(x, top, IRON[2])


def doorway(cv, cx, w, top, bottom, glow):
    """an arched opening in the north wall with warm light (or darkness) beyond, a worn threshold"""
    hw = w / 2
    for y in range(int(top - 4), bottom):
        for x in range(int(cx - hw - 4), int(cx + hw + 4)):
            dy = top + hw - y
            r_out = hw + 4
            inside = abs(x + 0.5 - cx) <= hw and (dy <= 0 or math.hypot(x + 0.5 - cx, dy) <= hw)
            rim = abs(x + 0.5 - cx) <= r_out and (dy <= 0 or math.hypot(x + 0.5 - cx, dy) <= r_out)
            if inside:
                t = (y - top) / max(1, bottom - top)
                if glow: cv.put(x, y, (int(70 + 60 * t), int(40 + 36 * t), int(18 + 12 * t)), 1)
                else: cv.put(x, y, (8, 7, 6))
            elif rim:
                cv.tone(x, y, WALLS, 0.6 if x < cx else 0.34)


def side_walls(cv):
    """the west / east / south walls are seen from above as stone caps; a thin dark inner edge"""
    for y in range(WALL_TOP, H):
        for x in list(range(0, FLOOR[0])) + list(range(FLOOR[2], W)):
            v = 0.5 + (nF(x * 1.4, y * 1.4) - 0.5) * 0.14 + (nM(x, y) - 0.5) * 0.1
            if (y + (x // 32) * 11) % 32 == 0: v -= 0.25
            d = min(abs(x - FLOOR[0] + 1), abs(x - FLOOR[2]))
            if d < 3: v -= 0.3 - d * 0.08
            cv.tone(x, y, WALLS, v)
    for y in range(FLOOR[3], H):
        for x in range(FLOOR[0], FLOOR[2]):
            v = 0.5 + (nF(x * 1.4, y * 1.4) - 0.5) * 0.14 - (0.3 if y < FLOOR[3] + 3 else 0)
            if (x + (y // 32) * 13) % 40 == 0: v -= 0.25
            cv.tone(x, y, WALLS, v)
    for y in range(FLOOR[1], FLOOR[3]):                                               # damp + AO along the walls
        for x in range(FLOOR[0], FLOOR[2]):
            d = min(x - FLOOR[0], FLOOR[2] - 1 - x, (y - FLOOR[1]) * 1.4, (FLOOR[3] - 1 - y) * 1.6)
            if d < 18: cv.shade(x, y, 0.6 + 0.4 * (d / 18) ** 0.7)


def side_door(cv, side, y0, y1, glow):
    """an opening in a side wall's cap: a step and light (or dark) beyond"""
    xa, xb = (0, FLOOR[0]) if side < 0 else (FLOOR[2], W)
    for y in range(y0, y1):
        for x in range(xa, xb):
            t = abs(x - (FLOOR[0] if side < 0 else FLOOR[2])) / (xb - xa)
            if y in (y0, y1 - 1): cv.tone(x, y, WALLS, 0.25); continue
            cv.put(x, y, (int(110 - 60 * t), int(64 - 36 * t), int(28 - 16 * t)) if glow else (10, 9, 8), 1 if glow else 0)


def south_gap(cv, cx, w, glow=False):
    """the way down to the nave in the south wall's cap: steps falling into the dark"""
    for y in range(FLOOR[3], H):
        for x in range(int(cx - w / 2), int(cx + w / 2)):
            k = (y - FLOOR[3]) // 7
            v = 0.42 - k * 0.07 + (0.12 if (y - FLOOR[3]) % 7 == 0 else 0) + (nF(x * 2, y) - 0.5) * 0.08
            cv.tone(x, y, STONE, max(0.0, v))
    for y in range(FLOOR[3], H):
        cv.put(cx - w / 2 - 1, y, INK); cv.put(cx + w / 2, y, INK)


# ---- furniture (3/4 boxes: the top face drawn h px higher than the footprint, the front face below it) -------------------
def box3(cv, x0, y0, w, d, h, top_rp, front_rp, top_v=0.62, front_v=0.32, grain=True, outline=True):
    """footprint (x0, y0, w, d) on the floor, height h: the top face at (x0, y0 - h), the front face down to y0 + d"""
    cv.ao(x0, y0 + d - 2, x0 + w, y0 + d + 2, r=6, k=0.55)
    for y in range(int(y0 - h), int(y0 + d - h)):
        for x in range(int(x0), int(x0 + w)):
            v = top_v + ((nF(x * 0.4, y * 2.5) - 0.5) * 0.16 if grain else (nF(x, y) - 0.5) * 0.1)
            if y == int(y0 - h): v += 0.12
            if x == int(x0): v += 0.06
            cv.tone(x, y, top_rp, v)
    for y in range(int(y0 + d - h), int(y0 + d)):
        for x in range(int(x0), int(x0 + w)):
            v = front_v + (nF(x * 0.4, y * 2.5) - 0.5) * 0.14 - 0.12 * (y - (y0 + d - h)) / max(1, h)
            cv.tone(x, y, front_rp, v)
    if outline: cv.outline(int(x0) - 1, int(y0 - h) - 1, int(x0 + w) + 1, int(y0 + d) + 1)


def pew(cv, x0, y0, w):
    """a pew facing north, seen from behind (the camera is south): the seat's lit top beyond, the backrest's cap and
    its panelled back toward us, carved ends standing proud; footprint y0..y0+18, drawn up to y0-10"""
    cv.ao(x0, y0 + 16, x0 + w, y0 + 20, r=7, k=0.6)
    for y in range(y0 - 10, y0 - 2):                                                  # the seat, beyond the back
        for x in range(x0 + 3, x0 + w - 3):
            cv.tone(x, y, OAK, 0.62 + (nF(x * 0.3, y * 3) - 0.5) * 0.16 + (0.08 if y == y0 - 10 else 0))
    for y in range(y0 - 2, y0 + 1):                                                   # the backrest's cap
        for x in range(x0 + 2, x0 + w - 2):
            cv.tone(x, y, OAK, 0.82 if y == y0 - 2 else 0.6)
    for y in range(y0 + 1, y0 + 17):                                                  # its back, panelled
        for x in range(x0 + 2, x0 + w - 2):
            v = 0.38 + (nF(x * 0.3, y * 3) - 0.5) * 0.14 - (y - y0) * 0.008
            px_ = (x - x0 - 2) % 40
            if px_ in (0, 1): v += 0.12 if px_ == 0 else -0.14                          # panel stiles
            if y in (y0 + 3, y0 + 14): v -= 0.12
            cv.tone(x, y, OAK, v)
    for ex in (x0, x0 + w - 4):                                                       # the carved ends
        for y in range(y0 - 12, y0 + 18):
            for x in range(ex, ex + 4):
                v = 0.5 + (0.2 if x == ex else -0.1 if x == ex + 3 else 0) + (0.14 if y < y0 - 9 else 0)
                cv.tone(x, y, OAK, v)
        cv.put(ex + 1, y0 - 13, OAK[7]); cv.put(ex + 2, y0 - 13, OAK[6])
    cv.outline(x0 - 1, y0 - 14, x0 + w + 1, y0 + 18)
    for k in range(int(w // 34)):                                                     # hymnals left on the seat
        if h32(int(x0), k, 5) % 3 == 0:
            bx = x0 + 12 + k * 34
            cv.rect(bx, y0 - 9, bx + 8, y0 - 4, LEATHER_R, lambda x, y: 0.55 if y < y0 - 7 else 0.35)


LEATHER_R = R('#1c0c0a #2c1410 #3e1d16 #52281e #663428')


def candle_stand(cv, x, base, hgt, flames, n=1):
    """an iron floor candle stand: a foot, a shaft, a drip pan, n candles; their flame points go to `flames`"""
    cv.ao(x - 5, base - 2, x + 6, base + 1, r=5, k=0.5)
    for dx in range(-4, 5): cv.put(x + dx, base, IRON[3 if dx < 0 else 1]); cv.put(x + dx, base - 1, IRON[4])
    for y in range(base - hgt, base): cv.put(x, y, IRON[4]); cv.put(x + 1, y, IRON[2])
    for dx in range(-4, 6): cv.put(x + dx, base - hgt, IRON[5]); cv.put(x + dx, base - hgt + 1, IRON[2])
    for k in range(n):
        cx = x + (k - (n - 1) / 2) * 5
        candle(cv, cx, base - hgt - 1, 7 + (k % 2) * 2, flames)
    for k in range(3):                                                                # wax drips on the floor
        cv.put(x + 3 - k * 3, base + 2 + k % 2, WAX[2])


def candle(cv, x, y, h, flames, lit=True):
    """a wax candle standing on (x, y); records its flame for the animated sprite"""
    for yy in range(int(y - h), int(y + 1)):
        cv.put(x, yy, WAX[3]); cv.put(x + 1, yy, WAX[1])
    cv.put(x, y - h, WAX[4])
    if lit:
        cv.put(x, y - h - 1, FIRE[4], 1); cv.put(x, y - h - 2, FIRE[3], 1); cv.put(x + 1, y - h - 1, FIRE[2], 1); cv.put(x, y - h - 3, FIRE[2], 1)
        flames.append([int(x), int(y - h - 1)])
    else:
        cv.put(x, y - h - 1, (30, 26, 22)); cv.put(x, y - h - 2, (52, 48, 44))


def pulpit(cv, x0, y0, flames):
    """a wooden pulpit raised on a step: a lectern with an open book, a carved front with a gold cross"""
    box3(cv, x0 - 4, y0 + 34, 84, 10, 6, STONE, STONE, top_v=0.6, front_v=0.35, grain=False)   # the step
    box3(cv, x0, y0, 76, 34, 30, OAK, OAK, top_v=0.58, front_v=0.38)
    for y in range(y0 + 10, y0 + 30): cv.put(x0 + 37, y, GOLD[4]); cv.put(x0 + 38, y, GOLD[2])
    for x in range(x0 + 31, x0 + 45): cv.put(x, y0 + 16, GOLD[4]); cv.put(x, y0 + 17, GOLD[2])
    for y in range(y0 - 26, y0 - 18):                                                 # the open book on the lectern
        for x in range(x0 + 26, x0 + 50):
            cv.put(x, y, LINEN[6] if x != x0 + 38 else LINEN[3])
            if (y - y0) % 2 == 0 and x not in (x0 + 26, x0 + 49, x0 + 38, x0 + 37) and h32(x, y) % 5: cv.put(x, y, LINEN[3])
    candle(cv, x0 + 6, y0 - 26, 6, flames); candle(cv, x0 + 68, y0 - 26, 6, flames)


def booth(cv, x0, y0, w, d, h):
    """the confession booth against the west wall: a tall dark box, a curtained door, a little grille"""
    box3(cv, x0, y0, w, d, h, OAK, OAK, top_v=0.5, front_v=0.3)
    fy0, fy1 = int(y0 + d - h), int(y0 + d)
    for y in range(fy0 + 8, fy1 - 4):                                                 # the curtain
        for x in range(x0 + 10, x0 + w - 10):
            v = 0.42 + 0.14 * math.sin((x - x0) * 0.9) + (nF(x, y) - 0.5) * 0.1
            cv.tone(x, y, RUG, v)
    for y in range(fy0 + 14, fy0 + 26):                                               # the grille
        for x in range(x0 + w - 8, x0 + w - 3):
            cv.put(x, y, IRON[1] if (x + y) % 2 else IRON[4])
    for x in range(x0 + 2, x0 + w - 2): cv.put(x, fy0 + 4, GOLD[2])


# ---- the hall's table ---------------------------------------------------------------------------------------------------
def table(cv, x0, y0, w, d, seats_n, seats_s, flames, dark=False):
    """the long feast table: oak under a linen cloth (pressed folds, a few wine stains) hanging over its front edge, a
    red runner, a place at every seat, bread, jugs, fruit, the candelabra and the covered dish; `dark` = the Infinite
    Fold: one place set at the head, every candle out"""
    h = 14
    cv.ao(x0, y0 + d - 4, x0 + w, y0 + d + 4, r=9, k=0.6)
    ty0, ty1 = y0 - h, y0 + d - h
    for y in range(int(ty0), int(ty1)):                                               # the cloth on top
        for x in range(int(x0), int(x0 + w)):
            v = 0.46 + (nF(x * 0.5, y * 0.5) - 0.5) * 0.06 - 0.06 * ((y - ty0) / (ty1 - ty0))
            fx = (x - x0) % 48
            if fx == 0: v -= 0.1
            elif fx == 1: v += 0.05
            if y == int(ty0): v += 0.1
            cv.tone(x, y, LINEN, v)
    for k in range(9):                                                                # wine stains
        sx_, sy_ = x0 + 20 + h32(k, 31) % (w - 40), ty0 + 6 + h32(k, 32) % (d - 12)
        for yy in range(int(sy_) - 2, int(sy_) + 3):
            for xx in range(int(sx_) - 3, int(sx_) + 4):
                if (xx - sx_) ** 2 / 9 + (yy - sy_) ** 2 / 4 < 1 and h32(xx, yy, k) % 3: cv.shade(xx, yy, 0.82)
    for y in range(int(ty1), int(ty1 + 10)):                                          # the cloth hanging over the front
        for x in range(int(x0), int(x0 + w)):
            v = 0.4 + 0.12 * math.sin((x - x0) * 0.32) - (y - ty1) * 0.025 + (nF(x, y) - 0.5) * 0.06
            cv.tone(x, y, LINEN, v)
        if y == int(ty1 + 9):
            for x in range(int(x0), int(x0 + w)): cv.put(x, y, LINEN[1] if (x // 7) % 2 else LINEN[2])
    for y in range(int(ty1 + 10), int(y0 + d)):                                       # the oak below the cloth, legs
        for x in range(int(x0) + 4, int(x0 + w) - 4):
            leg = (x - x0) % 120 < 8
            cv.tone(x, y, OAK, (0.34 if leg else 0.18) + (nF(x * 0.3, y * 3) - 0.5) * 0.1)
    cv.outline(int(x0) - 1, int(ty0) - 1, int(x0 + w) + 1, int(y0 + d) + 1)
    my = int((ty0 + ty1) / 2)
    for y in range(my - 10, my + 10):                                                 # the runner, gold-edged
        for x in range(int(x0 + 4), int(x0 + w - 4)):
            ey = min(y - (my - 10), my + 9 - y)
            if ey == 2: cv.put(x, y, GOLD[2] if x % 3 else GOLD[3]); continue
            cv.tone(x, y, RUG, 0.5 + (nF(x * 2, y) - 0.5) * 0.1 - (0.15 if ey < 2 else 0))
    if not dark:
        for sx in seats_n: place(cv, sx, ty0 + 14, flip=False)
        for sx in seats_s: place(cv, sx, ty1 - 13, flip=True)
        for (bx, by) in ((x0 + 66, my - 2), (x0 + w - 70, my + 1), (x0 + w * 0.37, my + 2), (x0 + w * 0.63, my - 1)):
            bread(cv, bx, by)
        for (jx, jy) in ((x0 + 110, my - 15), (x0 + w - 120, my + 20)): jug(cv, jx, jy)
        fruit(cv, x0 + w * 0.3, my + 16); fruit(cv, x0 + w * 0.7, my - 16)
        cloche(cv, x0 + w / 2, my + 3)
        for fx in (x0 + w * 0.2, x0 + w * 0.5 - 46, x0 + w * 0.5 + 46, x0 + w * 0.8):
            candelabrum(cv, fx, my + 5, flames, lit=True)
    else:
        place(cv, x0 + w - 24, my - 18, flip=False)
        for fx in (x0 + w * 0.2, x0 + w * 0.5, x0 + w * 0.8): candelabrum(cv, fx, my + 5, flames, lit=False)


def jug(cv, cx, cy):
    """a stoneware wine jug"""
    cx, cy = int(cx), int(cy)
    for y in range(cy - 9, cy + 1):
        for x in range(cx - 4, cx + 5):
            r_ = 4.2 - (2.2 if y < cy - 6 else 0)
            if abs(x + 0.5 - cx) <= r_: cv.tone(x, y, STONE, 0.75 if x < cx - 1 else 0.5 if x < cx + 2 else 0.3)
    cv.put(cx + 4, cy - 6, STONE[3]); cv.put(cx + 5, cy - 5, STONE[3]); cv.put(cx + 5, cy - 4, STONE[2])
    for x in range(cx - 2, cx + 2): cv.put(x, cy - 10, (60, 16, 20))


def fruit(cv, cx, cy):
    """a wooden bowl of marsh fruit"""
    cx, cy = int(cx), int(cy)
    for y in range(cy - 3, cy + 4):
        for x in range(cx - 9, cx + 10):
            if ((x - cx) / 9.4) ** 2 + ((y - cy) / 3.8) ** 2 <= 1: cv.tone(x, y, OAK, 0.45 if y > cy else 0.62)
    for (dx, dy, c) in ((-5, -3, (110, 40, 36)), (-1, -4, (126, 102, 40)), (3, -3, (88, 104, 52)), (6, -2, (110, 40, 36)), (1, -2, (140, 116, 52))):
        for (ex, ey) in ((0, 0), (1, 0), (0, 1), (1, 1), (-1, 0)): cv.put(cx + dx + ex, cy + dy + ey, c if ey == 0 else tuple(int(v * 0.7) for v in c))
        cv.put(cx + dx, cy + dy, tuple(min(255, v + 50) for v in c))


def place(cv, cx, cy, flip=False):
    """a place setting: a pewter plate with something on it, a goblet, a knife"""
    cx, cy = int(round(cx)), int(round(cy))
    for y in range(cy - 7, cy + 8):
        for x in range(cx - 11, cx + 12):
            d = ((x + 0.5 - cx) / 11.2) ** 2 + ((y + 0.5 - cy) / 7.2) ** 2
            if d <= 1:
                v = 0.6 - (0.3 if d > 0.78 else 0) + (0.14 if x < cx and y < cy else 0)
                cv.tone(x, y, PEWTER, v)
                if d < 0.32: cv.put(x, y, FOOD[(h32(cx, x, y) % 3) + (0 if h32(cx, 7) % 2 else 4)])
    gx, gy = cx + (15 if not flip else -15), cy - (3 if not flip else -3)
    for y in range(gy - 7, gy + 1):
        for x in range(gx - 2, gx + 3): cv.put(x, y, GOLD[4] if x < gx else GOLD[2] if x == gx else GOLD[1])
    for x in range(gx - 1, gx + 2): cv.put(x, gy - 7, (110, 26, 30))
    for x in range(gx - 2, gx + 3): cv.put(x, gy + 2, GOLD[2])
    cv.put(gx, gy + 1, GOLD[3])
    kx = cx - (15 if not flip else -15)
    for y in range(cy - 5, cy + 5): cv.put(kx, y, PEWTER[5] if y < cy + 1 else OAK[5])


def bread(cv, cx, cy):
    cx, cy = int(round(cx)), int(round(cy))
    for y in range(int(cy - 3), int(cy + 4)):
        for x in range(int(cx - 6), int(cx + 7)):
            d = ((x + 0.5 - cx) / 6.4) ** 2 + ((y + 0.5 - cy) / 3.6) ** 2
            if d <= 1: cv.put(x, y, FOOD[3] if y < cy - 1 and x < cx + 2 else FOOD[2] if d < 0.7 else FOOD[1])
    for k in range(3): cv.put(cx - 3 + k * 3, cy - 1, FOOD[1])


def cloche(cv, cx, cy):
    """the covered dish nobody asks about: a silver dome on a platter"""
    cx, cy = int(round(cx)), int(round(cy))
    for y in range(int(cy - 3), int(cy + 5)):
        for x in range(int(cx - 17), int(cx + 18)):
            if ((x + 0.5 - cx) / 17) ** 2 + ((y + 0.5 - cy - 1) / 4) ** 2 <= 1: cv.tone(x, y, PEWTER, 0.4)
    for y in range(int(cy - 16), int(cy + 2)):
        for x in range(int(cx - 13), int(cx + 14)):
            d = ((x + 0.5 - cx) / 13) ** 2 + ((y + 0.5 - cy) / 16) ** 2
            if d <= 1 and y <= cy:
                v = 0.5 + 0.4 * (1 - d) * (1 if x < cx - 2 else 0.4) - (0.2 if d > 0.85 else 0)
                cv.tone(x, y, PEWTER, v)
    for (x, y) in ((cx - 5, cy - 11), (cx - 4, cy - 12), (cx - 6, cy - 9)): cv.put(x, y, (220, 218, 206))
    cv.put(cx, cy - 17, PEWTER[5]); cv.put(cx, cy - 16, PEWTER[3]); cv.put(cx - 1, cy - 16, PEWTER[4]); cv.put(cx + 1, cy - 16, PEWTER[2])


def candelabrum(cv, cx, base, flames, lit=True):
    """a three-branched gold candelabrum standing on the cloth"""
    cx, base = int(round(cx)), int(round(base))
    for dx in range(-3, 4): cv.put(cx + dx, base, GOLD[1]); cv.put(cx + dx, base - 1, GOLD[3])
    for y in range(base - 12, base - 1): cv.put(cx, y, GOLD[4]); cv.put(cx + 1, y, GOLD[2])
    for dx in range(-6, 8): cv.put(cx + dx, base - 12, GOLD[4]); cv.put(cx + dx, base - 11, GOLD[1])
    for dx in (-6, 0, 6):
        for y in range(base - 15, base - 11): cv.put(cx + dx, y, GOLD[3])
        candle(cv, cx + dx, base - 15, 6, flames, lit=lit)


def fireplace(cv, cx, w, lit, flames_fire):
    """a stone fireplace set into the north wall: a mantel, the hearth opening, a fire (or cold ash), a hearth stone"""
    face0, face1 = WALL_TOP + 10, FLOOR[1]
    top = face0 + 14
    hw = w / 2
    for y in range(top, face1 + 8):
        for x in range(int(cx - hw), int(cx + hw)):
            ex = min(x - (cx - hw), cx + hw - 1 - x)
            if y < top + 8:
                v = 0.66 + (0.12 if y == top else 0) - (0.3 if y == top + 7 else 0)
                cv.tone(x, y, STONE, v + (nF(x, y) - 0.5) * 0.1); continue
            if ex < 10 and y < face1:
                cv.tone(x, y, STONE, 0.55 - (0.15 if ex > 7 else 0) + (nF(x, y) - 0.5) * 0.1); continue
            if y >= face1:
                cv.tone(x, y, STONE, 0.5 - (y - face1) * 0.02 + (nF(x * 2, y * 2) - 0.5) * 0.1); continue
            t = (y - top - 8) / max(1, face1 - top - 8)
            if lit:
                fl = nF(x * 0.9, y * 0.5 + 3)
                k = int(max(0, min(4, (t * 3.2 + fl * 1.6 - 1.2) * (1.2 - abs(x - cx) / hw))))
                cv.put(x, y, FIRE[k] if t > 0.35 else (int(30 + 40 * t), int(14 + 16 * t), 8), 1 if t > 0.35 else 0)
            else:
                cv.put(x, y, (14, 12, 11) if t < 0.85 else (40, 38, 36) if (x + y) % 3 else (24, 22, 20))
    if lit: flames_fire.append([int(cx), int(face1 - 6)])


def honour_chair(cv, cx, cy, dark=False):
    """the empty seat of honour at the east head of the table, turned toward it: a broad carved oak chair with a red
    velvet seat, gilded arms and a tall back crowned with a gold finial; in the Infinite Fold something faceless sits
    in it"""
    cv.ao(cx - 18, cy + 18, cx + 22, cy + 30, r=8, k=0.6)
    for y in range(cy - 62, cy + 30):                                                 # the tall back, on the east side
        for x in range(cx + 8, cx + 22):
            if y < cy - 54 and abs(x + 0.5 - (cx + 15)) > (y - (cy - 62)) * 0.9 + 1: continue
            v = 0.5 + (0.2 if x == cx + 8 else -0.12 if x > cx + 19 else 0) + (nF(x * 0.4, y * 2) - 0.5) * 0.12
            if (y - cy) % 18 == 0: v -= 0.14
            cv.tone(x, y, OAK, v)
        if cy - 46 < y < cy + 2:
            for x in range(cx + 11, cx + 19): cv.tone(x, y, RUG, 0.48 + (0.08 if x < cx + 14 else 0))
    for y in range(cy - 4, cy + 22):                                                  # the seat, its velvet cushion
        for x in range(cx - 16, cx + 9):
            v = 0.62 if y < cy + 14 else 0.32
            cv.tone(x, y, RUG if y < cy + 14 else OAK, v + (nF(x, y) - 0.5) * 0.08 + (0.1 if y == cy - 4 else 0))
    for (yy, x0_, x1_) in ((cy - 6, cx - 18, cx + 9), (cy + 16, cx - 18, cx + 9)):     # the gilded arms
        for x in range(x0_, x1_): cv.put(x, yy, GOLD[4]); cv.put(x, yy + 1, GOLD[2])
    for y in range(cy + 22, cy + 30):
        for x in (cx - 16, cx - 15, cx + 6, cx + 7): cv.put(x, y, OAK[3])
    cv.outline(cx - 19, cy - 7, cx + 10, cy + 23)
    for (x, y, c) in ((cx + 15, cy - 64, GOLD[5]), (cx + 14, cy - 63, GOLD[4]), (cx + 16, cy - 63, GOLD[3]), (cx + 15, cy - 62, GOLD[3])):
        cv.put(x, y, c)
    if dark:                                                                          # the presence: seated, no face
        for y in range(cy - 44, cy + 16):
            for x in range(cx - 14, cx + 12):
                hy = cy - 34
                head = ((x + 0.5 - cx) / 8) ** 2 + ((y + 0.5 - hy) / 10) ** 2 <= 1
                body = y > hy + 6 and abs(x + 0.5 - cx) < 9 + (y - hy) * 0.14
                if head or body: cv.put(x, y, (2, 2, 3), 1)


def west_hatch(cv, y0, y1):
    """the kitchen door in the west wall: warm light and a worn step"""
    side_door(cv, -1, y0, y1, glow=True)
    for y in range(y0 + 1, y1 - 1):
        for x in range(FLOOR[0], FLOOR[0] + 10):
            cv.shade(x, y, 1.18 - (x - FLOOR[0]) * 0.015)


# ---- light --------------------------------------------------------------------------------------------------------------
def lighting(cv, lights, ambient, warm=(1.0, 0.74, 0.46)):
    """ambient * colour + warm point lights (falloff), computed on a 4 px grid and bilinearly spread; emissive pixels
    keep their colour; then a faint warm bloom around the flames"""
    gs = 4
    gw, gh = W // gs + 2, H // gs + 2
    grid = []
    for gy in range(gh):
        row = []
        for gx in range(gw):
            x, y = gx * gs, gy * gs
            r_, g_, b_ = ambient
            for (lx, ly, rad, inten) in lights:
                d2 = ((x - lx) ** 2 + ((y - ly) * 1.25) ** 2) / (rad * rad)
                f = inten / (1 + d2 * 3.0) * max(0.0, 1 - d2 * 0.18)
                r_ += f * warm[0]; g_ += f * warm[1]; b_ += f * warm[2]
            row.append((r_, g_, b_))
        grid.append(row)
    out = []
    for y in range(H):
        gy, fy = y // gs, (y % gs) / gs
        for x in range(W):
            i = y * W + x
            c = cv.c[i]
            if cv.emit[i]: out.append(c); continue
            gx, fx = x // gs, (x % gs) / gs
            a, b, cc, d = grid[gy][gx], grid[gy][gx + 1], grid[gy + 1][gx], grid[gy + 1][gx + 1]
            l = [a[k] * (1 - fx) * (1 - fy) + b[k] * fx * (1 - fy) + cc[k] * (1 - fx) * fy + d[k] * fx * fy for k in range(3)]
            n = (nL(x * 1.1, y * 1.1) - 0.5) * 0.06                                    # a painterly drift
            out.append(tuple(max(0, min(255, int(c[k] * (l[k] + n)))) for k in range(3)))
    cv.c = out


def finish(cv, path):
    im = Image.new('RGB', (W, H))
    im.putdata(cv.c)
    im.save(path)
    return im


# ======================================================================================================================
def nave():
    cv, flames, L = Canvas(), [], {}
    north_wall(cv, openings=[(CX, 64, True)], windows=[(150, 26), (270, 26), (796, 26), (916, 26)],
               banners=[(390, 30), (676, 30)])
    side_walls(cv)
    flags_random(cv, FLOOR[0], FLOOR[1], FLOOR[2], FLOOR[3], STONE, cell=30, seed=3)
    scatter(cv, FLOOR[0] + 6, FLOOR[1] + 6, FLOOR[2] - 6, FLOOR[3] - 6, 90, 12, 'wax')
    for y in range(FLOOR[1], FLOOR[3]):                                               # worn path up the aisle
        for x in range(CX - 60, CX + 60):
            if nM(x * 0.8, y * 0.4) > 0.5: cv.shade(x, y, 1.05)
    runner(cv, CX - 36, FLOOR[1] + 4, CX + 36, FLOOR[3] - 2)
    colliders = []
    for row_y in (236, 302, 368, 434):
        for (x0, w) in ((214, 240), (612, 240)):
            pew(cv, x0, row_y, w)
            colliders.append({'x': x0 - 2, 'y': row_y - 14, 'w': w + 4, 'h': 36})
    px, py = 300, 140
    pulpit(cv, px, py, flames)
    colliders.append({'x': px - 6, 'y': py - 32, 'w': 88, 'h': 82})
    bx, by, bw, bd, bh = 84, 386, 80, 66, 60
    booth(cv, bx, by, bw, bd, bh)
    colliders.append({'x': bx - 4, 'y': by - bh - 2, 'w': bw + 8, 'h': bd + bh + 6})
    for x in (CX - 64, CX + 64): candle_stand(cv, x, 130, 26, flames, n=3)
    for y in (190, 270, 350, 470):
        candle_stand(cv, 74, y, 22, flames); candle_stand(cv, 992, y, 22, flames)
    lights = [(f[0], f[1], 95, 0.62) for f in flames] + [(CX, FLOOR[1] - 10, 170, 0.9)]
    lighting(cv, lights, (0.46, 0.43, 0.44))
    L = {
        'bg': 'feast_nave', 'title': 'The Nave — Sunday',
        'bounds': {'x0': FLOOR[0] + 6, 'y0': FLOOR[1] + 8, 'x1': FLOOR[2] - 6, 'y1': FLOOR[3] - 8},
        'colliders': colliders,
        'doors': [{'id': 'north', 'x': CX - 28, 'y': FLOOR[1] - 4, 'w': 56, 'h': 44, 'to': 'hall', 'spawn': {'x': CX, 'y': 500},
                   'label': 'to the Long Hall ▲', 'lx': CX, 'ly': 104}],
        'interacts': {'pulpit': {'x': px + 38, 'y': py + 62, 'hit': {'x': px - 4, 'y': py - 32, 'w': 84, 'h': 82}, 'label': '✝ Pulpit'},
                      'booth': {'x': bx + bw + 24, 'y': by + 16, 'hit': {'x': bx, 'y': by - bh, 'w': bw, 'h': bd + bh}, 'label': '⌂ Confession'}},
        'npcs': {'pim': [470, 340]},
        'spawn': {'x': CX, 'y': 486},
        'flames': flames
    }
    return cv, L


def hall(dark=False):
    cv, flames, fire = Canvas(), [], []
    north_wall(cv, windows=[(130, 24), (236, 24), (830, 24), (936, 24)], banners=[(372, 30), (694, 30)])
    fireplace(cv, CX, 112, not dark, fire)
    side_walls(cv)
    tiles_checker(cv, FLOOR[0], FLOOR[1], FLOOR[2], FLOOR[3], STONE2, cell=32, seed=7)
    scatter(cv, FLOOR[0] + 6, FLOOR[1] + 6, FLOOR[2] - 6, FLOOR[3] - 6, 260, 11, 'rush')
    west_hatch(cv, 252, 332) if not dark else side_door(cv, -1, 252, 332, glow=False)
    south_gap(cv, CX, 60)
    tx, ty, tw, td = 293, 216, 480, 178
    north = [345, 445, 641, 735]
    south = [419, 528, 641]
    table(cv, tx, ty, tw, td, north if not dark else [], south if not dark else [], flames, dark=dark)
    honour_chair(cv, tx + tw + 30, 290, dark=dark)
    colliders = [{'x': tx - 4, 'y': ty - 18, 'w': tw + 8, 'h': td + 14},
                 {'x': tx + tw + 12, 'y': 222, 'w': 40, 'h': 100}, {'x': tx + tw + 62, 'y': 200, 'w': 16, 'h': 36}]
    if not dark:
        candle_stand(cv, tx + tw + 70, 232, 28, flames, n=3)                          # a light by the seat of honour
        for y in (180, 300, 430):
            candle_stand(cv, 74, y, 22, flames); candle_stand(cv, 992, y, 22, flames)
        for x in (CX - 96, CX + 96): candle_stand(cv, x, 126, 24, flames, n=3)
        lights = [(f[0], f[1], 80, 0.42) for f in flames] + [(f[0], f[1] + 20, 260, 1.5) for f in fire] + [(40, 292, 150, 0.8)]
        lighting(cv, lights, (0.42, 0.39, 0.4))
    else:
        for y in (180, 300, 430):
            candle_stand_dark(cv, 74, y); candle_stand_dark(cv, 992, y)
        candle_stand_dark(cv, tx + tw + 70, 232, 28, 3)
        lighting(cv, [], (0.2, 0.2, 0.27), warm=(0.6, 0.6, 0.8))
        for i, c in enumerate(cv.c):                                                     # drained of warmth
            g = (c[0] * 30 + c[1] * 59 + c[2] * 11) // 100
            cv.c[i] = ((c[0] + g * 2) // 3, (c[1] + g * 2) // 3, min(255, (c[2] + g * 2) // 3 + 4))
    L = {
        'bg': 'feast_hall' if not dark else 'feast_hall_dark', 'title': 'The Long Hall',
        'bounds': {'x0': FLOOR[0] + 6, 'y0': FLOOR[1] + 8, 'x1': FLOOR[2] - 6, 'y1': FLOOR[3] - 8},
        'colliders': colliders,
        'doors': [{'id': 'south', 'x': CX - 28, 'y': FLOOR[3] - 30, 'w': 56, 'h': 34, 'to': 'nave', 'spawn': {'x': CX, 'y': 236},
                   'label': '▼ back to the Nave', 'lx': CX, 'ly': 566}],
        'interacts': {'guesthonor': {'x': tx + tw + 84, 'y': 300, 'hit': {'x': tx + tw + 12, 'y': 222, 'w': 44, 'h': 100},
                                     'label': '☥ Name the guest of honour'}},
        'npcs': {'cornelius': [north[0], 190], 'wren': [north[1], 190], 'vesper': [543, 170], 'otho': [north[2], 190], 'foyle': [north[3], 190],
                 'twins': [south[0], 432], 'marigold': [south[2], 432], 'quill': [tx + tw + 84, 392], 'gallow': [116, 296]},
        'spawn': {'x': CX, 'y': 500},
        'flames': flames, 'fire': fire
    }
    return cv, L


def candle_stand_dark(cv, x, base, hgt=22, n=1):
    fl = []
    candle_stand(cv, x, base, hgt, fl, n=n)
    for (fx, fy) in fl:
        for dy in range(0, 4): cv.put(fx, fy - dy, (34, 30, 26) if dy < 2 else (60, 58, 56))


def flame_sheet():
    """4 frames of 8x12: a small candle flame flickering (the scene places one on every lit wick, ADD blend not needed)"""
    im = Image.new('RGBA', (32, 12), (0, 0, 0, 0)); p = im.load()
    shapes = [(0, 5), (1, 6), (-1, 5), (0, 4)]
    for f, (lean, hgt) in enumerate(shapes):
        for k in range(hgt):
            t = k / max(1, hgt - 1)
            x = f * 8 + 4 + (lean if t > 0.5 else 0)
            y = 11 - k
            c = FIRE[4] if t < 0.3 else FIRE[3] if t < 0.6 else FIRE[2]
            p[x, y] = c + (255,)
            if t < 0.5:
                p[x - 1, y] = FIRE[2] + (200,)
                p[x + 1, y] = FIRE[1] + (170,)
    return im


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    layout = {'w': W, 'h': H}
    cv, layout['nave'] = nave(); finish(cv, f'{OUT}/nave.png'); print('nave')
    cv, layout['hall'] = hall(); finish(cv, f'{OUT}/hall.png'); print('hall')
    cv, dl = hall(dark=True); finish(cv, f'{OUT}/hall_dark.png'); print('hall_dark')
    flame_sheet().save(f'{OUT}/flame.png')
    json.dump(layout, open(f'{OUT}/feast_rooms.json', 'w'), ensure_ascii=False, indent=1)
    ALL = STONE + STONE2 + WALLS + OAK + LINEN + RUG + GOLD + IRON + WAX + PEWTER + GLASS + FIRE + FOOD + [INK]
    seen, rows = set(), []
    for c in ALL:
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(f'{OUT}/feast_rooms.gpl', 'w').write('GIMP Palette\nName: feast_rooms\nColumns: 16\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT)
