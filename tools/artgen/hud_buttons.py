"""HUD buttons -- drawn objects instead of the generic mushroom buttons. 48x48, 2 frames each: closed / open (hover).
  0-1 inventory -- a leather satchel with a fly-agaric toggle; on hover the flap lifts and a vial and a scroll peek out
  2-3 map       -- a parchment map folded in three (coast, route, X); on hover it lies unfolded and the X glows
  4-5 journal   -- a moss-green leather book, bronze corners, mushroom emblem; on hover it lies open
  6-7 quests    -- a task note pinned by a bronze tack, one item ticked, a red seal; on hover the corner lifts, ticks glow
  8   badge     -- the red wax "!" seal for unread journal / quest updates
python3 hud_buttons.py <outdir>  ->  hud_buttons.png (9 frames of 48x48) + hud/<n>.png (for Aseprite) + hud.gpl"""
import sys, os, math
from PIL import Image
from common import INK, band, h32, make_noise
from symbionts import Spr, curve, lit, norm
from pal_hud import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
nA, nB = make_noise(4, 82, 80, 80), make_noise(2, 81, 80, 80)

def tone(k, v, x, y): return col(k, band(v, x, y))

def area(s, box, inside, shade, part='x'):
    x0, y0, x1, y1 = box
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if inside(x, y):
                c = shade(x, y)
                if c: s.put(x, y, c, part)

def rrect(x0, y0, x1, y1, rt, rb):
    """inside-test of a rectangle with rounded top / bottom corners (pixel centres)"""
    def inside(x, y):
        px, py = x + 0.5, y + 0.5
        if not (x0 <= px <= x1 and y0 <= py <= y1): return False
        r = rt if py < (y0 + y1) / 2 else rb
        cx, cy = min(max(px, x0 + r), x1 - r), min(max(py, y0 + r), y1 - r)
        return (px - cx) ** 2 + (py - cy) ** 2 <= r * r
    return inside

def quad(p0, p1, p2):
    return lambda t: ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                      (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])

# --- inventory: the satchel -------------------------------------------------------------------------------------------
def satchel(f):
    s = Spr(48, 48)
    strap = curve(quad((10, 20), (24, -5), (38, 20)), 60)
    s.stroke(strap, lambda t: 3.2, lambda t, x, y: LEATHER[2], 'strap')
    s.stroke([(x - 0.6, y - 0.9) for x, y in strap], lambda t: 1.0, lambda t, x, y: LEATHER[4], 'strap')
    def leather(x, y, lift=0.0, cx=24, half=17):
        u = max(-1, min(1, (x + 0.5 - cx) / half)); w = (y + 0.5 - 30) / 13
        n = norm((u * 0.85, w * 0.4, math.sqrt(max(0.05, 1 - u * u * 0.7))))
        return 1.0 + lift + 5.0 * lit(n) + (nB(x * 1.3, y * 1.3) - 0.5) * 0.9
    body = rrect(7, 18, 41, 43, 3, 6)
    mouth_y, mouth_ry = 19.5, 2.6
    def mouth_low(x):
        u = (x + 0.5 - 24) / 15.5
        return mouth_y + mouth_ry * math.sqrt(1 - u * u) if abs(u) < 1 else mouth_y
    if f == 0:
        area(s, (6, 17, 42, 44), body, lambda x, y: tone(LEATHER, leather(x, y) - (0.8 if y >= 41 else 0), x, y), 'body')
        def flap_bottom(x):
            u = (x + 0.5 - 24) / 17.5
            return 29 + 5 * math.sqrt(max(0.0, 1 - u * u))
        flap = lambda x, y: y + 0.5 <= flap_bottom(x) and rrect(6.5, 15.5, 41.5, 40, 3, 3)(x, y)
        area(s, (6, 15, 42, 36), flap, lambda x, y: tone(LEATHER, leather(x, y, 0.6) + (0.8 if y == 16 else 0), x, y), 'flap')
        for x in range(8, 41):                       # the flap's shadow on the bag
            yb = int(flap_bottom(x)) + 1
            if s.part.get((x, yb)) == 'body': s.put(x, yb, LEATHER[1], 'body')
        for y in range(19, 33):                      # stitching along the flap
            if y % 2 == 0:
                for x in (9, 38):
                    if s.part.get((x, y)) == 'flap' and y + 2.5 < flap_bottom(x): s.put(x, y, LEATHER[6], 'stitch')
        for x in range(10, 38, 2):
            s.put(x, int(flap_bottom(x)) - 2, LEATHER[6], 'stitch')
        for x in range(22, 27): s.put(x, 35, LEATHER[2], 'loop'); s.put(x, 36, LEATHER[3], 'loop')
        for y in range(33, 38): s.put(24, y, BONE[5], 'toggle'); s.put(25, y, BONE[4], 'toggle')
        s.blob(24.5, 33, 4.0, 2.4, lambda x, y, n: tone(AMANITA, 0.6 + 3.4 * lit(n), x, y), 'toggle')
        for x, y in ((22, 32), (25, 32), (27, 33)): s.put(x, y, BONE[7], 'toggle')
    else:
        def flap_top(x):
            u = (x + 0.5 - 24) / 17
            return 19 - (9 + 5 * math.sqrt(max(0.0, 1 - u * u)))
        area(s, (7, 3, 41, 19), lambda x, y: 7 <= x <= 40 and y + 0.5 >= flap_top(x),
             lambda x, y: tone(LEATHER, leather(x, y, -0.4) - 1.2 + (1.2 if y + 0.5 < flap_top(x) + 1.5 else 0), x, y), 'flap')
        for x in range(10, 38, 2):                                  # the flap's stitching, now upside down
            s.put(x, int(flap_top(x)) + 2, LEATHER[6], 'stitch')
        for x in range(22, 27): s.put(x, int(flap_top(24)) + 1, AMANITA[2], 'toggle')   # the toggle, seen edge-on
        area(s, (8, 16, 40, 23), lambda x, y: abs(x + 0.5 - 24) < 15.5 and abs(y + 0.5 - mouth_y) <= mouth_ry * math.sqrt(max(0, 1 - ((x + 0.5 - 24) / 15.5) ** 2)),
             lambda x, y: VEIN[1] if (abs(x + 0.5 - 24) < 6 and y + 0.5 > mouth_y) else CAV[1], 'inside')
        roll = curve(lambda t: (14 + 3.5 * t, 21 - 10 * t), 20)          # a rolled scroll
        s.stroke(roll, lambda t: 3.6, lambda t, x, y: PARCH[5] if x < 16 + 3.5 * (21 - y) / 10 else PARCH[3], 'scroll')
        s.put(17, 10, INKL[1], 'scroll'); s.put(18, 11, PARCH[2], 'scroll')
        area(s, (27, 11, 32, 21), lambda x, y: 27 <= x <= 31 and 12 <= y <= 21,                       # a glowing vial
             lambda x, y: VEIN[3] if x == 28 and y < 19 else VEIN[2] if y > 15 else VEIN[0], 'vial')
        for x in range(27, 32): s.put(x, 11, BRONZE[3], 'vial'); s.put(x, 10, BRONZE[4], 'vial')
        s.put(29, 9, BRONZE[5], 'vial')
        area(s, (6, 17, 42, 44), lambda x, y: body(x, y) and y + 0.5 > mouth_low(x),
             lambda x, y: tone(LEATHER, leather(x, y) - (0.8 if y >= 41 else 0), x, y), 'body')
        for x in range(9, 40):
            s.put(x, int(mouth_low(x)) + 1, LEATHER[6], 'body')
    s.outline()
    return s

# --- map --------------------------------------------------------------------------------------------------------------
def coast(y): return 15 + 2.5 * math.sin(y * 0.45)
ROUTE_PTS = curve(quad((17, 33), (24, 37), (34, 23)), 40)

def map_content(x, y, dark, glow):
    """what is printed on the map at (x, y): (ramp, index) or None"""
    d = 1 if dark else 0
    if abs(x + 0.5 - coast(y)) < 0.6: return INKL, 1
    if x + 0.5 < coast(y): return SEA, (3 if (x * 2 + y * 3) % 9 == 0 else 2) - d
    for i, (px, py) in enumerate(ROUTE_PTS):
        if i % 4 < 2 and int(px) == x and int(py) == y: return ROUTE, 1 - d
    if (x, y) in ((34, 21), (36, 21), (35, 22), (34, 23), (36, 23)): return ROUTE, (3 if glow else 2) - d
    for cx, cy in ((32, 13), (37, 16), (28, 16)):
        if (x, y) in ((cx, cy), (cx - 1, cy + 1), (cx + 1, cy + 1), (cx - 2, cy + 2), (cx + 2, cy + 2)): return INKL, 1
    if (x, y) == (10, 12): return ROUTE, 1
    if (x, y) in ((10, 13), (9, 14), (11, 14), (10, 15)): return INKL, 2
    return None

def map_(f):
    s = Spr(48, 48)
    if f == 0:
        panels = [(6, 18, 9, 11, 39, 37, False), (18, 30, 11, 9, 37, 39, True), (30, 42, 9, 11, 39, 37, False)]
        for x0, x1, t0, t1, b0, b1, dark in panels:
            for x in range(x0, x1):
                t = (x + 0.5 - x0) / (x1 - x0)
                top, bot = t0 + (t1 - t0) * t, b0 + (b1 - b0) * t
                for y in range(int(top), int(bot) + 1):
                    if not (top <= y + 0.5 <= bot): continue
                    edge = y + 0.5 - top < 1 or bot - (y + 0.5) < 1 or x in (6, 41)
                    v = (3.6 if dark else 5.1) + (nB(x * 1.4, y * 1.4) - 0.5) * 0.6 - (0.8 if edge else 0)
                    c = map_content(x, y, dark, False)
                    s.put(x, y, col(c[0], c[1]) if c else tone(PARCH, v, x, y), 'map')
        for y in range(10, 39):
            if s.has(18, y): s.put(18, y, PARCH[2], 'map')
            if s.has(30, y): s.put(30, y, PARCH[7], 'map')
    else:
        for x in range(4, 45):
            top, bot = 8 + round(0.8 * math.sin(x * 0.3)), 40 + round(0.8 * math.sin(x * 0.3 + 1))
            for y in range(top, bot + 1):
                if x + y < 4 + 8 + 5: continue                   # dog-eared corner, drawn below
                edge = y in (top, bot) or x in (4, 44)
                v = 5.2 + (nB(x * 1.4, y * 1.4) - 0.5) * 0.6 - (0.8 if edge else 0)
                if x in (17, 31): v -= 0.9
                elif x in (18, 32): v += 0.5
                c = map_content(x, y, False, True)
                s.put(x, y, col(c[0], c[1]) if c else tone(PARCH, v, x, y), 'map')
        for x in range(4, 13):                                    # the folded-back corner
            for y in range(8, 17):
                if 4 + 8 + 5 - 4 <= x + y < 4 + 8 + 5: s.put(x, y, PARCH[3] if x + y < 16 else PARCH[6], 'corner')
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)): s.put(35 + dx, 22 + dy, ROUTE[3], 'map')
        s.put(35, 22, (255, 236, 200), 'map')
    s.outline()
    if f == 1:
        for x, y in ((35, 18), (39, 22), (31, 22), (35, 26)): s.put(x, y, ROUTE[3], 'spark')
    return s

# --- journal ----------------------------------------------------------------------------------------------------------
def journal(f):
    s = Spr(48, 48)
    if f == 0:
        area(s, (12, 8, 40, 44), lambda x, y: (37 <= x <= 40 and 8 <= y <= 43) or (12 <= x <= 40 and 42 <= y <= 44),
             lambda x, y: PARCH[4] if x == 40 or y == 44 else PARCH[6] if y % 2 else PARCH[5], 'pages')
        def spine(x, y):
            u = (x + 0.5 - 9.5) / 2.5
            v = 1.2 + 3.6 * lit((u, 0, math.sqrt(max(0.0, 1 - u * u))))
            if y in (12, 20, 28, 36): v += 1.5
            if y in (13, 21, 29, 37): v -= 1.2
            return tone(MOSS, v, x, y)
        area(s, (8, 6, 11, 44), lambda x, y: 8 <= x <= 11 and 6 <= y <= 44, spine, 'spine')
        def cover(x, y):
            v = 4.4 - (x - 11) * 0.05 + (nB(x * 1.3, y * 1.3) - 0.5) * 0.7
            on = (x in (14, 34) and 9 <= y <= 39) or (y in (9, 39) and 14 <= x <= 34)
            if on: return MOSS[1]
            if (x in (15, 35) and 10 <= y <= 40) or (y in (10, 40) and 15 <= x <= 35): v += 1.1
            return tone(MOSS, v, x, y)
        area(s, (12, 6, 37, 42), lambda x, y: 12 <= x <= 37 and 6 <= y <= 42, cover, 'cover')
        for cy, sg in ((6, 1), (42, -1)):                         # bronze corners
            area(s, (32, 4, 37, 44), lambda x, y: (37 - x) + sg * (y - cy) <= 5 and 32 <= x <= 37 and (cy <= y <= cy + 5 if sg > 0 else cy - 5 <= y <= cy),
                 lambda x, y: tone(BRONZE, 5.2 - ((37 - x) + abs(y - cy)) * 0.4, x, y), 'bronze')
            s.put(35, cy + 2 * sg, BRONZE[7], 'bronze')
        for y in range(15, 33):                                    # the emblem: a bronze ring with a mushroom
            for x in range(16, 33):
                dx, dy = x + 0.5 - 24.5, y + 0.5 - 24
                d = math.hypot(dx, dy)
                if 5.8 <= d <= 7.3: s.put(x, y, tone(BRONZE, 4.6 - 1.4 * (dx + dy) / d, x, y), 'emblem')
        for y in range(20, 24):
            for x in range(20, 30):
                if ((x + 0.5 - 24.5) / 4.2) ** 2 + ((y + 0.5 - 23.5) / 3.2) ** 2 <= 1:
                    s.put(x, y, BRONZE[6] if y < 22 else BRONZE[5], 'emblem')
        for y in range(24, 28): s.put(24, y, BRONZE[5], 'emblem'); s.put(25, y, BRONZE[4], 'emblem')
        for y in range(43, 47):
            for x in (29, 30, 31): s.put(x, y, WAX[2] if x == 29 else WAX[1], 'ribbon')
        s.put(29, 47, WAX[1], 'ribbon'); s.put(31, 47, WAX[1], 'ribbon')
    else:
        area(s, (3, 10, 45, 42), rrect(3, 11, 45, 42, 2, 2), lambda x, y: tone(MOSS, 2.6 + (nB(x, y) - 0.5) * 0.6, x, y), 'cover')
        def dip(x): g = abs(x + 0.5 - 24.5); return 2 if g < 2 else 1 if g < 5 else 0
        for x in range(5, 44):
            top, bot = 12 + dip(x) - (1 if 9 < abs(x + 0.5 - 24.5) < 16 else 0), 39 - (1 if abs(x + 0.5 - 24.5) < 3 else 0)
            for y in range(top, bot + 1):
                g = abs(x + 0.5 - 24.5)
                v = 6.2 - 1.8 * max(0.0, 1 - g / 6) - (0.6 if g > 17.5 else 0) + (nB(x * 1.2, y * 1.2) - 0.5) * 0.4
                s.put(x, y, tone(PARCH, v, x, y), 'page')
        for y in range(13, 40):
            if s.has(24, y): s.put(24, y, PARCH[2], 'page')
            if s.has(25, y): s.put(25, y, PARCH[3], 'page')
        for x in range(5, 44): s.put(x, 40, PARCH[4], 'edge'); s.put(x, 41, PARCH[3] if x % 2 else PARCH[4], 'edge')
        for ry in range(15, 36, 3):                                 # lines of handwriting
            for x0, x1 in ((8, 22), (28, 41)):
                if x0 == 28 and ry < 27: continue
                x = x0
                while x < x1:
                    h = h32(x, ry, 7); run = 2 + h % 4
                    for k in range(run):
                        if x + k <= x1: s.put(x + k, ry, INKL[2], 'ink')
                    x += run + 1 + (h >> 5) % 2
        for t in range(9):                                          # a sketch of a mushroom on the right page
            a = math.pi * (1 - t / 8)
            s.put(34.5 + 5 * math.cos(a), 21 - 3.5 * math.sin(a), INKL[1], 'ink')
        for x in range(30, 40): s.put(x, 21, INKL[1], 'ink')
        for y in range(22, 26): s.put(33, y, INKL[1], 'ink'); s.put(36, y, INKL[1], 'ink')
        for x, y in ((32, 18), (36, 19)): s.put(x, y, INKL[2], 'ink')
        s.stroke(curve(lambda t: (26 + 2 * t, 11 + 33 * t), 40), lambda t: 2.0, lambda t, x, y: WAX[2] if t < 0.85 else WAX[1], 'ribbon')
    s.outline()
    return s

# --- quests: the pinned task note -------------------------------------------------------------------------------------
def quests(f):
    s = Spr(48, 48)
    curl = 7 if f == 0 else 11
    R, B = 38, 43
    def left(y): return 10 + (1 if h32(y, 1) % 3 == 0 else 0)
    def right(y): return R - (1 if h32(y, 2) % 3 == 0 else 0)
    def bottom(x): return B - (1 if h32(x, 3) % 3 == 0 else 0)
    def paper(x, y):
        v = 5.4 + (nB(x * 1.4, y * 1.4) - 0.5) * 0.7 - (0.7 if x == left(y) or x == right(y) or y == bottom(x) or y == 8 else 0)
        return tone(PARCH, v, x, y)
    area(s, (9, 8, 39, 44), lambda x, y: left(y) <= x <= right(y) and 8 <= y <= bottom(x) and (R - x) + (B - y) > curl, paper, 'note')
    for x in range(16, 33):                                         # heading
        if x % 5 != 0: s.put(x, 14, INKL[1], 'ink')
    tick = VEIN[3] if f == 1 else VEIN[2]
    for i, y0 in enumerate((18, 25, 32)):
        for k in range(5):
            for x, y in ((13 + k, y0), (13 + k, y0 + 4), (13, y0 + k), (17, y0 + k)): s.put(x, y, INKL[1], 'ink')
        x = 20
        while x < 35 - i * 3:
            h = h32(x, y0, 9); run = 2 + h % 4
            for k in range(run):
                if x + k < 35 - i * 3: s.put(x + k, y0 + 2, INKL[2], 'ink')
            x += run + 1
        if i == 0:
            for x, y in ((13, y0 + 1), (14, y0 + 2), (15, y0 + 3), (16, y0 + 2), (17, y0 + 1), (18, y0), (19, y0 - 1)):
                s.put(x, y, tick, 'tick')
            if f == 1:
                for x, y in ((12, y0 + 1), (20, y0 - 2), (15, y0 + 4)): s.put(x, y, VEIN[2], 'tick')
    c = R + B - curl                                                # the curled corner: its back, folded over the front
    for y in range(B - curl, B + 1):
        for x in range(R - curl, R + 1):
            if (R - x) + (B - y) <= curl:
                fx, fy = c - y, c - x
                on_fold = (R - fx) + (B - fy) == curl
                s.put(fx, fy, PARCH[6] if on_fold else PARCH[3] if (fx + fy) % 3 else PARCH[4], 'curl')
    s.blob(24.5, 9.5, 2.7, 2.7, lambda x, y, n: tone(BRONZE, 2.4 + 4.4 * lit(n) + (0.8 if f == 1 else 0), x, y), 'pin')
    for x, y in ((26, 12), (27, 11)): s.put(x, y, PARCH[2], 'shadow')
    for y in range(44, 47): s.put(14, y, WAX[1], 'seal'); s.put(17, y + (1 if y == 46 else 0), WAX[1], 'seal')
    def wax(x, y, n):
        d = math.hypot(x + 0.5 - 15.5, y + 0.5 - 40)
        return WAX[1] if 1.4 < d < 2.2 else tone(WAX, 0.8 + 3.0 * lit(n), x, y)
    s.blob(15.5, 40, 3.4, 3.2, wax, 'seal')
    s.outline()
    return s

# --- the notification badge ------------------------------------------------------------------------------------------
def badge(f=0):
    s = Spr(48, 48)
    for y in range(16, 33):
        for x in range(16, 33):
            dx, dy = x + 0.5 - 24, y + 0.5 - 24
            d = math.hypot(dx, dy)
            if d < 6.4 + 0.35 * math.sin(7 * math.atan2(dy, dx) + 1):
                n = (dx / 7, dy / 7, math.sqrt(max(0.0, 1 - (d / 7) ** 2)))
                s.put(x, y, tone(WAX, 0.9 + 3.0 * lit(n), x, y), 'wax')
    for y in range(20, 26): s.put(23, y, BONE[7], 'mark'); s.put(24, y, BONE[6], 'mark')
    for y in (27, 28): s.put(23, y, BONE[7], 'mark'); s.put(24, y, BONE[6], 'mark')
    s.outline()
    return s

FRAMES = [lambda: satchel(0), lambda: satchel(1), lambda: map_(0), lambda: map_(1),
          lambda: journal(0), lambda: journal(1), lambda: quests(0), lambda: quests(1), badge]

if __name__ == '__main__':
    os.makedirs(f'{OUT}/hud', exist_ok=True)
    sheet = Image.new('RGBA', (48 * len(FRAMES), 48), (0, 0, 0, 0))
    for i, fn in enumerate(FRAMES):
        im = fn().image()
        im.save(f'{OUT}/hud/{i}.png'); sheet.paste(im, (i * 48, 0))
    sheet.save(f'{OUT}/hud_buttons.png')
    write_gpl(f'{OUT}/hud.gpl')
    print('ok', OUT)
