"""The drifting mycelium overlay of the dream / cutscene panels (ScraperAmbraScene, texture cs_myc), 1067x600.
Shown with ADD blending at alpha ~0.1-0.28 over the panel picture, so black = no effect and only the threads glow.
Hyphae grow from a few spore points by a persistent random walk, fork now and then, thin out and fade with age;
where two strands cross a small knot (a node of the network) lights up. Pure pixel art: 1-px strands, no blur, a
one-pixel dim halo next to the brighter strands, a 5-step teal-to-pale-green ramp.

    python3 mycelium_overlay.py <outdir>   ->  mycelial_overlay.png"""
import sys, os, math, random
from PIL import Image

W, H = 1067, 600
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
RAMP = [(0, 0, 0), (10, 30, 26), (22, 58, 46), (44, 96, 70), (86, 150, 104), (150, 206, 150), (210, 240, 196)]

rnd = random.Random(521)
lvl = [[0] * W for _ in range(H)]                 # brightness level 0..6 per pixel

def plot(x, y, v):
    if 0 <= x < W and 0 <= y < H and lvl[y][x] < v: lvl[y][x] = v

strands = []
SPORES = [(-3, 0.18), (-3, 0.72), (W + 3, 0.3), (W + 3, 0.85), (0.22, -3), (0.7, H + 3), (0.5, -3), (0.38, H + 3)]
for i, (sx, sy) in enumerate(SPORES):              # spore points round the edges, so the middle of the panel stays calm
    x = sx if sx < 0 or sx > W else sx * W
    y = sy if sy < 0 or sy > H else sy * H
    a0 = math.atan2(H / 2 - y, W / 2 - x)
    for k in range(3 if i < 4 else 2):
        strands.append([x, y, a0 + rnd.uniform(-1.0, 1.0), 5.0 if i < 4 else 4.0, rnd.randint(200, 380)])

while strands:
    x, y, a, v, life = strands.pop()
    age = 0
    while age < life:
        a += rnd.gauss(0, 0.16)
        x += math.cos(a); y += math.sin(a); age += 1
        if not (-5 < x < W + 5 and -5 < y < H + 5): break
        fade = 1 - age / life
        lv = max(1, int(round(v * (0.45 + 0.55 * fade))))
        ix, iy = int(x), int(y)
        if lvl[iy % H][ix % W] >= 3 and age > 8 and rnd.random() < 0.5:     # a crossing: light a knot
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1): plot(ix + dx, iy + dy, min(6, lv + (2 if dx == dy == 0 else 1)))
        plot(ix, iy, lv)
        if lv >= 3:                                                          # the dim halo of a bright strand
            nx, ny = -math.sin(a), math.cos(a)
            plot(int(x + nx), int(y + ny), lv - 2); plot(int(x - nx), int(y - ny), lv - 2)
        if rnd.random() < 0.012 and v > 2.2:                                 # a fork
            strands.append([x, y, a + rnd.choice((-1, 1)) * rnd.uniform(0.5, 1.1), v - 0.8, int((life - age) * rnd.uniform(0.5, 0.9))])

img = Image.new('RGB', (W, H)); px = img.load()
for y in range(H):
    for x in range(W): px[x, y] = RAMP[lvl[y][x]]
os.makedirs(OUT, exist_ok=True)
img.save(os.path.join(OUT, 'mycelial_overlay.png'))
print('mycelial_overlay.png', W, H)
