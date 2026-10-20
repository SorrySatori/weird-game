"""Growth/Decay props — small transparent pixel-art sprites placed by code (utils/GDProps.js), reusable across scenes.
Anchor: bottom-centre (the vine clump: top-centre). The burning barrel is a 6-frame sheet."""
import sys, math, random
from PIL import Image
from pal_day import *
OUT = sys.argv[1]
nA, nB = make_noise(9, 7, 256, 256), make_noise(4, 8, 256, 256)

def canvas(w, h): return {}, {}
def ell_pts(cx, cy, rx, ry):
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            nx, ny = (x - cx) / rx, (y - cy) / ry; d = nx * nx + ny * ny
            if d <= 1: yield x, y, nx, ny, d
def finish(PIX, PART, w, h, soft=(), shadow=True, extra=None):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); p = img.load()
    if shadow:
        for y in range(h - 6, h):
            for x in range(w):
                d = ((x - w / 2) / (w * 0.45)) ** 2 + ((y - h + 3) / 4.0) ** 2
                if d < 1 and (x, y) not in PIX and (x + y) % 2 == 0: p[x, y] = (7, 10, 9, 130 if d < 0.6 else 70)
    if extra:
        for (x, y), c in extra.items():
            if 0 <= x < w and 0 <= y < h: p[x, y] = c
    for (x, y), c in PIX.items():
        if 0 <= x < w and 0 <= y < h: p[x, y] = c + (255,)
    for (x, y) in list(PIX):
        a = PART.get((x, y))
        for nx_, ny_ in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx_, ny_) not in PIX:
                if 0 <= x < w and 0 <= y < h: p[x, y] = INK + (255,)
                break
            b = PART.get((nx_, ny_))
            if a != b and frozenset((a, b)) not in soft and (nx_, ny_) > (x, y):
                p[nx_, ny_] = INK + (255,)
    return img

# ------------------------------------------------------------------ growth: flowering bush
def bush(seed=1):
    random.seed(seed); W_, H_ = 96, 72; PIX, PART = canvas(W_, H_)
    blobs = [(48, 46, 34, 22), (28, 50, 20, 16), (70, 48, 22, 18), (44, 32, 22, 16), (62, 34, 18, 14), (34, 38, 16, 12)]
    for (cx, cy, rx, ry) in blobs:
        for x, y, nx, ny, d in ell_pts(cx, cy, rx, ry):
            lam = max(0.0, -ny * 0.7 + math.sqrt(max(0, 1 - d)) * 0.6 - nx * 0.15)
            v = 0.8 + 4.2 * lam + (nB(x, y) - 0.5) * 1.6
            if h32(x, y, seed) % 5 == 0: v -= 1.2                                 # leaf shadows
            PIX[(x, y)] = LEAF[max(0, min(5, int(v)))]; PART[(x, y)] = 'leaf'
    for _ in range(26):                                                            # blossoms on the lit side/top
        x, y = random.randint(14, 82), random.randint(18, 56)
        if (x, y) in PIX and nB(x * 2, y * 2) > 0.45:
            c = FLOWER[random.choice((0, 1, 2, 3, 3))]
            for (dx, dy) in ((0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1)):
                if (x + dx, y + dy) in PIX: PIX[(x + dx, y + dy)] = c if (dx, dy) in ((0, 0), (1, 0), (0, 1), (1, 1)) else FLOWER[4]
            PART[(x, y)] = 'leaf'
    for y in range(60, 70):                                                        # stems at the base
        for x in (40, 41, 52, 53, 47):
            PIX[(x, y)] = WOOD[2] if x % 2 else WOOD[1]; PART[(x, y)] = 'leaf'
    return finish(PIX, PART, W_, H_)

# ------------------------------------------------------------------ growth: hanging vine clump (anchor TOP-centre)
def vine():
    random.seed(4); W_, H_ = 64, 96; PIX, PART = canvas(W_, H_)
    for k in range(9):
        x = 6 + k * 6.4 + random.uniform(-2, 2); y = 0.0; ang = math.radians(270 + random.uniform(-12, 12)); n = random.randint(40, 90)
        for i in range(n):
            ang += random.uniform(-0.25, 0.25); ang = max(math.radians(235), min(math.radians(305), ang))
            x += math.cos(ang); y -= math.sin(ang); xi, yi = int(x), int(y)
            if not (0 <= xi < W_ and 0 <= yi < H_): break
            PIX[(xi, yi)] = LEAF[1 if i % 3 else 0]; PART[(xi, yi)] = 'v'
            if i % 7 == 3:
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        if dx * dx + dy * dy <= 4 and 0 <= xi + dx < W_ and 0 <= yi + dy < H_:
                            PIX[(xi + dx, yi + dy)] = LEAF[3 if dy < 0 else 2 if dy == 0 else 1]; PART[(xi + dx, yi + dy)] = 'v'
                if random.random() < 0.18: PIX[(xi, yi - 1)] = FLOWER[3]; PIX[(xi + 1, yi - 1)] = FLOWER[4]
    for x in range(0, W_):                                                         # the mat it hangs from
        for y in range(0, 5):
            if h32(x, y, 3) % 4: PIX[(x, y)] = LEAF[2 if y < 2 else 1]; PART[(x, y)] = 'v'
    return finish(PIX, PART, W_, H_, shadow=False)

# ------------------------------------------------------------------ growth: mushroom cluster
def mushrooms():
    W_, H_ = 64, 48; PIX, PART = canvas(W_, H_)
    for (cx, base, h, rx, ry, pid) in ((16, 46, 18, 12, 7, 'a'), (32, 46, 26, 15, 9, 'b'), (48, 46, 14, 10, 6, 'c'), (26, 46, 10, 7, 4, 'd')):
        for y in range(base - h, base + 1):                                        # stem
            for x in range(cx - 3, cx + 4):
                PIX[(x, y)] = STONE[7 if x < cx else 6 if x == cx else 5]; PART[(x, y)] = pid
        cy = base - h
        for x, y, nx, ny, d in ell_pts(cx, cy, rx, ry):
            if y > cy + 1 and abs(nx) < 0.45: continue                             # gills notch under the cap
            lam = max(0.0, -ny * 0.75 + math.sqrt(max(0, 1 - d)) * 0.5)
            v = 1.0 + 4.0 * lam + (nB(x * 2, y * 2) - 0.5) * 0.8
            if h32(x, y, 9) % 11 == 0: v -= 1.4
            PIX[(x, y)] = CAP[max(0, min(5, int(v)))] if y <= cy + 1 else CAP[0]; PART[(x, y)] = pid + 'c'
    return finish(PIX, PART, W_, H_, soft={frozenset(('ac', 'a')), frozenset(('bc', 'b')), frozenset(('cc', 'c')), frozenset(('dc', 'd'))})

# ------------------------------------------------------------------ decay: trash pile
def trash():
    random.seed(8); W_, H_ = 96, 56; PIX, PART = canvas(W_, H_)
    for (cx, cy, rx, ry, col) in ((30, 44, 22, 11, STONE), (62, 42, 24, 13, STONE), (46, 30, 16, 9, STONE)):   # bin bags
        for x, y, nx, ny, d in ell_pts(cx, cy, rx, ry):
            v = 1.0 + 2.2 * max(0.0, -ny * 0.7 + math.sqrt(max(0, 1 - d)) * 0.6) + (nB(x, y) - 0.5) * 0.8
            PIX[(x, y)] = col[max(0, min(9, int(v)))]; PART[(x, y)] = 'bag%d' % cx
    bits = [(STONE[8], 'paper'), (STONE[7], 'paper'), (METAL[3], 'can'), (METAL[4], 'can'), (RED[3], 'rag'), (GLOW[1], 'bottle'), (SKY[4], 'glass'), (WARM[4], 'card')]
    for _ in range(34):                                                            # loose litter
        x, y = random.randint(6, 90), random.randint(26, 54); c, k = random.choice(bits); w = random.randint(2, 6); h = random.randint(1, 3)
        for dx in range(w):
            for dy in range(h):
                PIX[(x + dx, y + dy)] = c if (dx + dy) % 3 else tuple(max(0, q - 40) for q in c); PART[(x + dx, y + dy)] = k + str(x)
    return finish(PIX, PART, W_, H_, soft={frozenset(p) for p in [('bag30', 'bag62'), ('bag30', 'bag46'), ('bag62', 'bag46')]})

# ------------------------------------------------------------------ decay: broken crate
def crate():
    W_, H_ = 72, 56; PIX, PART = canvas(W_, H_)
    for y in range(18, 54):                                                        # body planks (front face), broken top-right corner missing
        for x in range(8, 64):
            if x > 46 and y < 30 and (x - 46) > (30 - y) * 1.3: continue
            pl = (y - 18) // 7; i = 3 + (h32(pl, 1) % 2)
            if (y - 18) % 7 == 0: i = 1
            if x in (8, 9, 62, 63) or 34 <= x <= 35: i = 2
            PIX[(x, y)] = WOOD[i]; PART[(x, y)] = 'c'
    for (x0, y0, x1, y1) in ((44, 20, 70, 4), (48, 26, 66, 14), (10, 16, 2, 8)):   # splintered boards sticking out
        n = int(math.hypot(x1 - x0, y1 - y0))
        for i in range(n + 1):
            x, y = int(x0 + (x1 - x0) * i / n), int(y0 + (y1 - y0) * i / n)
            for dy in (0, 1, 2): PIX[(x, y + dy)] = WOOD[4 if dy == 0 else 2]; PART[(x, y + dy)] = 's%d' % x0
    for (x, y) in ((20, 38), (21, 38), (28, 46), (52, 40), (53, 40), (14, 50)): PIX[(x, y)] = STONE[2]       # nails
    return finish(PIX, PART, W_, H_)

# ------------------------------------------------------------------ decay: rubble
def rubble():
    random.seed(5); W_, H_ = 96, 40; PIX, PART = canvas(W_, H_)
    for _ in range(40):
        x, y = random.randint(4, 88), random.randint(14, 36); w, h = random.randint(4, 9), random.randint(3, 5)
        brick = random.random() < 0.5
        for dx in range(w):
            for dy in range(h):
                c = (WARM[2 + (dy == 0)] if brick else STONE[4 + (dy == 0) + (dx == 0)])
                PIX[(x + dx, y + dy)] = c; PART[(x + dx, y + dy)] = 'r%d' % (x * 100 + y)
    return finish(PIX, PART, W_, H_)

# ------------------------------------------------------------------ decay: burning barrel (6 frames, 64x112)
def barrel_fire():
    FW_, FH_ = 64, 112; frames = []
    for k in range(6):
        PIX, PART = canvas(FW_, FH_); glow = {}
        for y in range(64, 110):                                                   # the rusty drum
            for x in range(14, 51):
                nx = (x - 32) / 18.0
                v = 2.2 - 1.9 * nx * nx + (nB(x, y) - 0.5) * 0.5
                c = METAL[max(0, min(6, int(v)))]
                if y in (66, 67, 86, 87, 106, 107): c = METAL[max(0, min(6, int(v) + 1))]            # ribs
                if nA(x * 1.6, y * 1.6) > 0.56: c = WARM[max(0, min(5, int(1.6 - nx * 1.2)))]       # rust
                if y < 70: c = GLOW[1] if (x + y + k) % 3 else WARM[3]                              # rim lit by the fire
                if 70 <= y < 80 and abs(nx) < 0.35 and (x + y) % 2: c = GLOW[0]                     # glow through a burnt hole
                PIX[(x, y)] = c; PART[(x, y)] = 'drum'
        for x in range(12, 53):                                                    # top rim ellipse
            for y in (62, 63):
                if (x - 32) ** 2 / 400 <= 1: PIX[(x, y)] = METAL[5 if y == 62 else 3]; PART[(x, y)] = 'drum'
        for y in range(4, 66):                                                     # flames: teardrop mask + animated noise
            for x in range(8, 57):
                t = (66 - y) / 62.0; hw = 17 * (1 - t) ** 0.6 + 2
                nx = (x - 32) / hw
                if abs(nx) > 1: continue
                n = nA(x * 1.5 + k * 9, y * 1.1 - k * 13) * 0.65 + nB(x * 1.5, y * 1.3 - k * 9) * 0.35
                thr = 0.28 + 0.5 * t + 0.25 * nx * nx
                if n < thr: continue
                strength = (n - thr) / max(0.05, 1 - thr)
                c = GLOW[4] if strength > 0.55 and t < 0.55 else GLOW[3] if strength > 0.3 else GLOW[2] if t < 0.5 else GLOW[1] if t < 0.8 else RED[4]
                if t < 0.2 and strength < 0.25: c = RED[4]
                PIX[(x, y)] = c; PART[(x, y)] = 'fire'
        random.seed(100 + k)
        for _ in range(9):                                                         # embers
            x, y = random.randint(16, 48), random.randint(0, 40)
            if (x, y) not in PIX: glow[(x, y)] = GLOW[3] + (220,)
        img = finish(PIX, PART, FW_, FH_, soft={frozenset(('fire', 'drum'))}, extra=glow)
        p = img.load()
        for (x, y) in PIX:                                                         # flames have no ink outline
            if PART[(x, y)] == 'fire' and p[x, y][:3] == INK: p[x, y] = GLOW[1] + (255,)
        frames.append(img)
    sheet = Image.new('RGBA', (FW_ * 6, FH_), (0, 0, 0, 0))
    for i, f in enumerate(frames): sheet.paste(f, (i * FW_, 0))
    return sheet

bush().save(f'{OUT}/prop_bush_flowering.png'); vine().save(f'{OUT}/prop_vine_clump.png'); mushrooms().save(f'{OUT}/prop_mushroom_cluster.png')
trash().save(f'{OUT}/prop_trash_pile.png'); crate().save(f'{OUT}/prop_crate_broken.png'); rubble().save(f'{OUT}/prop_rubble.png')
barrel_fire().save(f'{OUT}/prop_barrel_fire.png')
print('props done')
