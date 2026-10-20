"""Shared palette + helpers for the Crossroad art (same night palette family as the Egg Cathedral exterior)."""
import math, random

def hx(s): return (int(s[1:3], 16), int(s[3:5], 16), int(s[5:7], 16))
def ramp(s): return [hx(c) for c in s.split()]

NIGHT  = ramp('#0a0c07 #11140c #181c11 #202616 #29301c #333b22 #3f4829 #4c5631 #5c663b #6f7a48')
SHELL  = ramp('#1f2118 #2c2f22 #3b3e2d #4c5039 #5f6347 #747856 #8b8e68 #a3a57c #bcbd93 #d4d4ae')
STONE  = ramp('#0e100c #161912 #1f231a #292e22 #34392b #414736 #4f5642 #616852 #767d65 #8e957b')
WARM   = ramp('#1a1310 #2a1f19 #3a2c24 #4a3d34 #66574a #857463 #a5937d #c7b69c #ddd3c4')
GLOW   = ramp('#c97a2a #e09a3a #f0bd5a #f8dc8a #fff2c8')
WOOD   = ramp('#2e1a10 #4a2a17 #6b3f22 #8c5a33')
JEWEL  = ramp('#6e1420 #b02a35 #142a5c #2f5fb3 #7fb2e6 #1f4a2a #4f9a4a #5a2a7a')
SCRIPT = ramp('#3f8f5a #7fff8e')
MYC    = ramp('#143a22 #1f5a32 #3f8f5a #7fff8e #c8ffd0 #f0fff2')   # mycelium / bioluminescence
FLESH  = ramp('#1c1d16 #2a2b21 #3a3c2e #4e503d #646650 #7c7e64 #96977a #adad8e #c2c2a5')  # dead demigod skin (grey-green)
INK = hx('#050604')
RAMPS = {'N': NIGHT, 'S': SHELL, 'T': STONE, 'W': WARM, 'M': MYC, 'F': FLESH, 'G': GLOW, 'J': JEWEL, 'D': WOOD}

def lum(c): return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
TO_WARM = {k: [min(range(len(WARM)), key=lambda j: abs(lum(WARM[j]) - lum(c))) for c in RAMPS[k]] for k in 'NSTF'}

def h32(*a):
    h = 2166136261
    for v in a: h = ((h ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return h

def make_noise(cell, seed, W, H):
    rnd = random.Random(seed); gw, gh = W // cell + 3, H // cell + 3
    g = [[rnd.random() for _ in range(gw)] for _ in range(gh)]
    def n(x, y):
        fx, fy = x / cell, y / cell; ix, iy = int(fx), int(fy); tx, ty = fx - ix, fy - iy
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        ix0, ix1, iy0, iy1 = ix % gw, (ix + 1) % gw, iy % gh, (iy + 1) % gh
        a = g[iy0][ix0] * (1 - tx) + g[iy0][ix1] * tx; b = g[iy1][ix0] * (1 - tx) + g[iy1][ix1] * tx
        return a * (1 - ty) + b * ty
    return n

def band(v, x, y):
    """quantise a continuous ramp position into clean bands with a thin dithered seam"""
    f = math.floor(v); t = v - f
    return f + (1 if t > 0.62 else 0 if t < 0.38 else (x + y) % 2)

# 3x5 pixel font (M is 5 wide)
FONT = {
    'A': ['010', '101', '111', '101', '101'], 'C': ['011', '100', '100', '100', '011'],
    'D': ['110', '101', '101', '101', '110'], 'E': ['111', '100', '110', '100', '111'],
    'H': ['101', '101', '111', '101', '101'], 'K': ['101', '101', '110', '101', '101'],
    'L': ['100', '100', '100', '100', '111'], 'M': ['10001', '11011', '10101', '10001', '10001'],
    'O': ['111', '101', '101', '101', '111'], 'P': ['110', '101', '110', '100', '100'],
    'R': ['110', '101', '110', '101', '101'], 'S': ['011', '100', '010', '001', '110'],
    'T': ['111', '010', '010', '010', '010'], 'V': ['101', '101', '101', '101', '010'],
    'X': ['101', '101', '010', '101', '101'], 'G': ['011', '100', '101', '101', '011'],
    'I': ['111', '010', '010', '010', '111'], 'N': ['101', '111', '111', '101', '101'],
    'U': ['101', '101', '101', '101', '111'], 'B': ['110', '101', '110', '101', '110'],
    '1': ['010', '110', '010', '010', '111'], '2': ['110', '001', '010', '100', '111'],
    '5': ['111', '100', '110', '001', '110'], '0': ['111', '101', '101', '101', '111'],
    '4': ['101', '101', '111', '001', '001'], ' ': ['0', '0', '0', '0', '0'],
}
def text_width(s, sc):
    return sum(len(FONT[ch][0]) * sc + sc for ch in s) - sc
def draw_text(put, s, x, y, sc):
    """put(x, y) per pixel; returns width"""
    cx = x
    for ch in s:
        rows = FONT[ch]
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == '1':
                    for dy in range(sc):
                        for dx in range(sc): put(cx + c * sc + dx, y + r * sc + dy)
        cx += len(rows[0]) * sc + sc
    return cx - x - sc
