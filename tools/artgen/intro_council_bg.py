"""The Council chamber of the Highest Humenium Council (intro), native 1067x600.

A rotunda hewn deep under the Obazoba: a curved masonry wall with the carved Ur-mushroom relief, the god's roots
breaking in from above, hanging mycelium threads with luminous droplets, niches with glowing fungi, fan-backed seats
carved like bracket fungi. The round table is a slab of petrified bracket fungus (growth rings) holding a sunken pool
of liquid mycelium -- the room's main light (faces are lit from below), with tallow candles as warm accents.

python3 intro_council_bg.py <outdir>  ->  council_bg.png, council_table.png (transparent layer drawn over the back
row's chairs, under the archpriests), council_glow.png (only the luminous pixels; the scene pulses it with ADD),
council.json (seat anchors, candle flames, pool) for the scene."""
import sys, math, random, json
from PIL import Image
from pal_under import *
from intro_layout import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
CX, HY = VP
img = Image.new('RGB', (W, H), INK); P = img.load()
tab = Image.new('RGBA', (W, H), (0, 0, 0, 0)); T = tab.load()
glw = Image.new('RGBA', (W, H), (0, 0, 0, 0)); GL = glw.load()
nA, nB, nC = make_noise(48, 21, W, H), make_noise(14, 22, W, H), make_noise(4, 23, W, H)
nD = make_noise(26, 24, W, H)

def put(x, y, c, glow=False, layer=None):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H:
        (layer or P)[x, y] = c if layer is None else c + (255,)
        if glow: GL[x, y] = c + (255,)

def k_of(x):                       # the rotunda wall bows toward the camera at the sides
    u = (x - CX) / 533.0
    return 1 + 0.55 * u * u

def wy(x, y0):                     # a wall feature at height y0 (seen at the centre) -> screen y at column x
    return HY + (y0 - HY) * k_of(x)

def y0_of(x, y):
    return HY + (y - HY) / k_of(x)

def pool_light(x, y):
    d = math.hypot(x - POOL['cx'], (y - POOL['cy']) * 1.8)
    return max(0.0, 1 - d / 600) ** 1.5

WALL_BASE = 436                    # floor line (centre-equivalent); hidden behind the table in the middle

# ------------------------------------------------------------------ 1. the masonry wall
ROW = 26
for y in range(H):
    for x in range(W):
        y0 = y0_of(x, y)
        if y0 > WALL_BASE:
            continue
        r = math.floor((y0 - WALL_BASE) / ROW)
        fy = (y0 - WALL_BASE) / ROW - r
        bw = 58 + (h32(r, 3) % 4) * 9
        off = h32(r, 5) % bw
        c = (x + off) // bw
        lx = (x + off) % bw
        py = fy * ROW * k_of(x)                      # screen px from the top of the block
        hgt = ROW * k_of(x)
        o = (h32(r, c, 7) % 1000) / 1000 - 0.5
        bcx, bcy = x - lx + bw / 2, wy(x, WALL_BASE + (r + 0.5) * ROW)
        L = pool_light(bcx, bcy)
        v = 2.6 + o * 1.3 + L * 4.4 + (nB(x, y) - 0.5) * 0.9 + (nC(x, y) - 0.5) * 0.5
        v -= max(0.0, (210 - y0) / 210) * 1.3                    # the upper wall sinks into darkness
        v -= ((x - CX) / 533.0) ** 2 * 1.2
        if py < 1.6 or lx < 2: v = 0.6 + L * 1.5                   # mortar joint
        elif py < 3: v -= 0.7                                      # top edge in shadow (light comes from below)
        elif py > hgt - 3: v += 0.8                                # bottom edge catches the pool light
        elif lx < 4: v -= 0.4
        if (h32(r, c, 9) % 7 == 0) and abs(lx - bw * 0.6 + py * 0.7) < 0.8 and py > 4: v -= 1.4   # cracks
        ramp_k = 'g' if L > 0.42 else 'R'
        P[x, y] = col(ramp_k, band(v, x, y))

# ------------------------------------------------------------------ 2. the carved Obazoba relief (smooth panel)
RCX, RCY, RRX, RRY = CX, 150, 128, 86                 # cap dome centre (screen, centre column = no curvature)
PANEL = (CX - 196, 22, CX + 196, 330)                  # pointed-arch panel
def in_panel(x, y):
    x0, y0_, x1, y1 = PANEL
    if not (x0 <= x <= x1 and y <= y1): return False
    # pointed arch: two circles
    rr = (x1 - x0) * 0.82
    a = math.hypot(x - (x0 + rr), y - (y0_ + rr * 0.7))
    b = math.hypot(x - (x1 - rr), y - (y0_ + rr * 0.7))
    return y >= y0_ + rr * 0.7 or (a <= rr and b <= rr)

def relief_h(x, y):
    """height field of the relief (0 = panel surface)"""
    h = 0.0
    # cap dome (upper half ellipse) with a thick rim
    if y <= RCY + 6:
        u = (x - RCX) / RRX
        prof = RCY - RRY * (1 - abs(u) ** 2.6) ** 0.55 - 7 * math.exp(-(u / 0.16) ** 2)   # dome + umbo
        if abs(u) <= 1 and y >= prof:
            d = min(1.0, u * u + ((y - RCY) / max(1, RCY - prof + 0.01)) ** 2)
            h = max(h, 0.5 + 0.9 * math.sqrt(max(0.0, 1 - d)) + (0.25 if y > RCY - 6 else 0))
    # gills: a dark crescent under the cap
    if RCY < y <= RCY + 14:
        u = (x - RCX) / RRX
        if abs(u) < 1 - (y - RCY) / 16.0:
            h = max(h, 0.2 + 0.25 * (abs(math.sin(math.atan2(y - RCY - 40, x - RCX) * 40)) > 0.5))
    # a slender stalk, swelling into a bulb at the foot
    if RCY + 8 < y <= PANEL[3]:
        t = (y - RCY) / (PANEL[3] - RCY)
        sw = 17 + 6 * t + 22 * math.exp(-((t - 0.95) / 0.12) ** 2)
        if abs(x - RCX) <= sw:
            h = max(h, 0.4 + 0.6 * math.sqrt(1 - ((x - RCX) / sw) ** 2))
    # sun-rays above the cap
    if y < RCY:
        ang = math.atan2(y - RCY, x - RCX)
        dist = math.hypot((x - RCX) / RRX, (y - RCY) / RRY)
        if 1.08 < dist < 1.85 and -math.pi < ang < 0:
            k = (ang + math.pi) / math.pi * 12
            if abs(k - round(k)) < 0.10 + 0.04 / dist and 0 < round(k) < 12: h = max(h, 0.3)
    # roots at the foot of the stalk spreading over the panel
    if y > PANEL[3] - 60:
        t = (y - (PANEL[3] - 60)) / 60.0
        for s, a in ((-1, 0.9), (1, 0.9), (-1, 2.2), (1, 2.2)):
            rx_ = RCX + s * (30 + a * 40 * t * t * 1.8)
            if abs(x - rx_) < 5 - t * 2: h = max(h, 0.35)
    return h

for y in range(0, PANEL[3] + 1):
    for x in range(PANEL[0], PANEL[2] + 1):
        if not in_panel(x, y): continue
        h = relief_h(x, y)
        hu, hd = relief_h(x, y - 1), relief_h(x, y + 1)
        hl, hr = relief_h(x - 1, y), relief_h(x + 1, y)
        L = pool_light(x, y)
        v = 1.4 + L * 2.0 + (nB(x, y) - 0.5) * 0.5 - max(0.0, (120 - y) / 120) * 0.6
        if h > 0:
            v += 0.6 + (hu - hd) * 7.0 + (hl - hr) * 1.5 + h * 0.8  # lit from below: down-facing slopes brighten
            if h - hd > 0.25: v += 1.2                              # lower edges catch light
            P[x, y] = col('C', band(max(0.6, min(4.6, v - 0.5)), x, y))
        else:
            if hd - h > 0.25: v -= 1.0                              # shadow above a raised edge (light from below)
            if hu - h > 0.25: v += 0.6
            P[x, y] = col('R', band(max(0.4, v + 0.6), x, y))
    # panel frame
for y in range(0, PANEL[3] + 1):
    for x in range(PANEL[0] - 4, PANEL[2] + 5):
        inside = in_panel(x, y)
        near = any(in_panel(x + dx, y + dy) != inside for dx, dy in ((4, 0), (-4, 0), (0, 4), (0, -4)))
        if near and not inside:
            P[x, y] = col('R', 1 + (1 if (x + y) % 5 == 0 else 0))
        elif near and inside and not any(in_panel(x + dx, y + dy) != inside for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))):
            pass

# ------------------------------------------------------------------ 3. glowing mycelium veins (relief outline + wall)
rnd = random.Random(77)
def vein(x, y, ang, length, w=1, bright=5, branch=0.04, depth=0, stop_y=None):
    for i in range(length):
        x += math.cos(ang); y += math.sin(ang)
        ang += (rnd.random() - 0.5) * 0.35
        if stop_y is not None and y > stop_y: return
        v = bright - (1 if i > length * 0.7 else 0)
        for k in range(w):
            put(x + k, y, col('M', v), glow=True)
        if rnd.random() < 0.035: put(x, y, col('M', bright + 2), glow=True); put(x + 1, y, col('M', bright + 1), glow=True)
        if depth < 2 and rnd.random() < branch * 0.35:
            vein(x, y, ang + rnd.choice((-0.8, 0.8)), int(length * 0.45), 1, max(3, bright - 1), branch, depth + 1, stop_y)

# trace the cap outline just outside the dome
for t in range(0, 181, 1):
    a = math.radians(180 + t)
    x = RCX + (RRX + 5) * math.cos(a); y = RCY + (RRY + 5) * math.sin(a)
    if (t // 9) % 3 != 2: put(x, y, col('M', 4 + (t % 13 == 0) * 2), glow=True)
# threads down from the stalk foot, spreading over the lower wall
for i in range(9):
    sx = RCX + (i - 4) * 9
    vein(sx, PANEL[3] - 4, math.pi / 2 + (i - 4) * 0.22, 160, 1, 4, 0.05, stop_y=WALL_BASE)
# a few wild threads across the wall
for (sx, sy, a, n) in ((140, 60, 1.2, 220), (930, 70, 1.9, 220), (300, 30, 1.4, 160), (770, 40, 1.7, 160)):
    vein(sx, sy, a, n, 1, 3, 0.06, stop_y=WALL_BASE)

# ------------------------------------------------------------------ 4. niches with luminous fungi
NICHES = [(262, 150), (804, 150), (112, 118), (955, 118)]
glow_points = []
for (nx, ny0) in NICHES:
    ny = wy(nx, ny0)
    w2, hh = 22, 46
    for y in range(int(ny - hh), int(ny + 10)):
        for x in range(nx - w2 - 3, nx + w2 + 4):
            dx = abs(x - nx)
            top = ny - hh + (w2 - math.sqrt(max(0, w2 * w2 - dx * dx))) if dx <= w2 else None
            if top is not None and y >= top and y <= ny:
                depth = (y - top) / (ny - top + 1)
                v = 0.5 + depth * 2.2 + (1 - dx / w2) * 0.8 + (nC(x, y) - 0.5) * 0.4
                put(x, y, col('g', band(v, x, y)))
            elif dx <= w2 + 3 and (top is None or y >= ny - hh - 3):
                t2 = ny - hh + (w2 + 3 - math.sqrt(max(0, (w2 + 3) ** 2 - dx * dx)))
                if y >= t2 and y <= ny + 3:
                    put(x, y, col('C', 3 if y > ny else 2))                     # carved frame
    # a sill
    for x in range(nx - w2 - 6, nx + w2 + 7):
        for y in range(int(ny), int(ny + 5)):
            put(x, y, col('C', 4 if y == int(ny) else 2))
    # cluster of small glowing mushrooms on the sill
    r2 = random.Random(nx)
    for m in range(6):
        mx = nx + r2.randint(-w2 + 4, w2 - 4); mh = r2.randint(5, 14); cw = r2.randint(3, 6)
        for yy in range(int(ny) - mh, int(ny)):
            put(mx, yy, col('M', 5), glow=True)
        for yy in range(-2, 1):
            for xx in range(-cw + abs(yy), cw - abs(yy) + 1):
                put(mx + xx, int(ny) - mh + yy, col('M', 7 if yy == -2 else 6), glow=True)
        put(mx, int(ny) - mh - 2, col('M', 8), glow=True)
    glow_points.append(dict(x=nx, y=int(ny - 8), r=34))

# ------------------------------------------------------------------ 5. roots of the god breaking in from above
def root(x0, length, amp, ph, w0, lean):
    pts = []
    for i in range(length):
        y = i - 6
        x = x0 + amp * math.sin(i / 37 + ph) + lean * i
        w = w0 * (1 - i / length * 0.75) + 2
        pts.append((x, y, w))
    for (x, y, w) in pts:
        for xx in range(int(x - w), int(x + w) + 1):
            u = (xx - x) / w
            v = 2.2 + 1.6 * math.sqrt(max(0, 1 - u * u)) - 0.5 * u + (nB(xx * 3, y) - 0.5) * 1.6
            if abs(u) > 0.85: v = 0.7
            if (int(y + xx * 0.6) % 11) == 0 and abs(u) < 0.8: v -= 1.0               # twisted fibres
            put(xx, y, col('O', band(v, xx, y)))
    # a mycelium sheath creeping down the root
    for (x, y, w) in pts[::3]:
        if (int(y) // 23) % 2 == 0:
            put(x + w * math.sin(y / 7), y, col('M', 4), glow=True)
    return pts

ROOTS = [(38, 520, 10, 0.4, 26, 0.02), (205, 300, 14, 1.3, 16, 0.05), (868, 300, 14, 2.1, 16, -0.05),
         (1030, 520, 10, 3.0, 26, -0.02), (330, 140, 8, 0.0, 11, 0.12), (742, 140, 8, 1.0, 11, -0.12)]
for rt in ROOTS:
    root(*rt)

# ------------------------------------------------------------------ 6. hanging threads with luminous droplets
for (hx_, end) in ((120, 210), (152, 150), (262, 120), (388, 150), (410, 230), (452, 120), (622, 120), (660, 230),
                   (684, 160), (812, 110), (906, 170), (948, 230), (990, 140)):
    sway = (h32(hx_) % 7 - 3) * 0.6
    for y in range(0, end):
        x = hx_ + sway * math.sin(y / 40)
        put(x, y, col('M', 2 if y < end - 30 else 3), glow=y > end - 30)
    x = hx_ + sway * math.sin(end / 40)
    for (dx, dy, v) in ((0, 0, 8), (-1, 0, 6), (1, 0, 6), (0, 1, 7), (0, -1, 6), (0, 2, 5)):
        put(x + dx, end + dy, col('M', v), glow=True)
    glow_points.append(dict(x=int(x), y=end, r=10))

# ------------------------------------------------------------------ 7. carved fan-backed seats (bracket fungi)
def fan(cx, base_y, rx, ry, lobes, seed, ramp_k='O'):
    for y in range(int(base_y - ry - 6), int(base_y) + 1):
        for x in range(int(cx - rx - 6), int(cx + rx) + 7):
            ang = math.atan2(base_y - y, x - cx)
            if ang < 0: continue
            r = math.hypot((x - cx) / rx, (base_y - y) / ry)
            edge = 1 + 0.045 * math.sin(ang * lobes + seed) + 0.02 * math.sin(ang * lobes * 2.3)
            if r > edge: continue
            dpx = (edge - r) * (rx * abs(math.cos(ang)) + ry * abs(math.sin(ang)))   # px to the margin
            zone = r / edge * 7 + (nD(x * 2, y * 2) - 0.5) * 0.5
            L = pool_light(x, y)
            v = 1.8 + (math.floor(zone) % 2) * 1.1 + L * 2.2 + (nC(x, y) - 0.5) * 0.6
            if abs(zone - round(zone)) < 0.05: v = 0.9                               # dark line between growth zones
            if abs(math.sin(ang * 29 + seed)) < 0.05 and zone > 1: v -= 0.6          # radial fibres
            if dpx < 1.2:
                put(x, y, INK); continue
            if dpx < 4.5:                                                            # pale growing margin
                put(x, y, col('C', 5.6 if dpx > 3 else 4.4)); continue
            put(x, y, col(ramp_k, band(v, x, y)))

fan(CX, 372, 92, 168, 9, 0.7)                                   # Varhun's high seat
fan(SEATS['tynri']['x'], 384, 66, 128, 7, 1.9)
fan(SEATS['rhull']['x'], 384, 66, 128, 7, 2.6)

# ------------------------------------------------------------------ 8. the floor (seen only at the sides and under the table)
for y in range(H):
    for x in range(W):
        if y0_of(x, y) <= WALL_BASE: continue
        z = 891 * 5 / max(1, (y - HY))
        wx = (x - CX) * z / 891
        tx, tz = math.floor(wx / 3.2), math.floor(z / 2.4)
        fx, fz = wx / 3.2 - tx, z / 2.4 - tz
        o = (h32(tx, tz, 3) % 1000) / 1000 - 0.5
        L = pool_light(x, y)
        v = 1.6 + o * 0.9 + L * 2.0 + (nB(x, y) - 0.5) * 0.6
        if fx < 0.05 or fz < 0.07: v = 0.5
        P[x, y] = col('g' if L > 0.5 else 'R', band(v, x, y))
# glowing veins over the floor toward the table foot
for i in range(14):
    a = math.pi / 2 + (i - 6.5) * 0.24
    vein(CX + math.cos(a) * 160, 556, a, 120, 1, 4, 0.03)

# ------------------------------------------------------------------ 9. the table (separate layer)
TCX, TCY, TRX, TRY, SIDE = TABLE['cx'], TABLE['cy'], TABLE['rx'], TABLE['ry'], TABLE['side']
PCX, PCY, PRX, PRY = POOL['cx'], POOL['cy'], POOL['rx'], POOL['ry']
SINK = 7
def tput(x, y, c, glow=False):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H:
        T[x, y] = c + (255,)
        if glow: GL[x, y] = c + (255,)

# pedestal: a thick fibrous stalk under the slab
for y in range(TCY + 40, H):
    t = (y - (TCY + 40)) / (H - TCY - 40)
    hw = 150 - 40 * math.sin(t * math.pi * 0.8) + (30 * t * t)
    for x in range(int(TCX - hw), int(TCX + hw) + 1):
        u = (x - TCX) / hw
        v = 0.6 + 1.6 * math.sqrt(max(0, 1 - u * u)) + (nB(x * 3, y * 0.5) - 0.5) * 1.2 - t * 0.4
        if abs(u) > 0.94: v = 0.3
        tput(x, y, col('O', band(v, x, y)))
# the rim side band (front half only)
for x in range(TCX - TRX, TCX + TRX + 1):
    yf = front_edge_y(x)
    if yf is None: continue
    u = (x - TCX) / TRX
    for y in range(int(yf), int(yf + SIDE * (0.35 + 0.65 * math.sqrt(max(0, 1 - u * u))))):
        dy = y - yf
        v = 1.3 + 1.6 * (1 - abs(u) ** 2) - dy / SIDE * 0.9 + (nB(x, y) - 0.5) * 0.6
        if dy < 2: v = 5.0 - abs(u) * 2.5                                            # lit lip
        elif dy in (6, 7) or int(dy) == SIDE - 8: v -= 1.0                            # carved grooves
        elif 9 < dy < SIDE - 10:
            ph = (x - TCX) / (1.0 + 0.6 * (1 - abs(u)))                               # spore glyphs along the band
            gx = (ph % 22) - 11; gy = dy - (9 + (SIDE - 19) / 2)
            if abs(math.hypot(gx, gy * 1.4) - 4.5) < 0.9: v += 1.3
            if abs(gx) < 0.8 and abs(gy) < 1: v += 1.6
        tput(x, y, col('O' if dy >= 2 else 'C', band(max(0.4, v + (1.0 if dy >= 2 else 0.6)), x, y)))
    tput(x, int(yf + SIDE * (0.35 + 0.65 * math.sqrt(max(0, 1 - u * u)))), INK)
# the top: a slab of petrified bracket fungus -- dark concentric growth zones, a pale growing margin
def ell_dist(x, y, cx, cy, rx, ry):
    """approx. pixel distance inside an ellipse's edge (positive inside)"""
    dx, dy = x - cx, y - cy
    f = (dx / rx) ** 2 + (dy / ry) ** 2 - 1
    g = 2 * math.hypot(dx / rx ** 2, dy / ry ** 2) or 1e-6
    return -f / g
for y in range(TCY - TRY - 1, TCY + TRY + 2):
    for x in range(TCX - TRX - 1, TCX + TRX + 2):
        d_out = ell_dist(x, y, TCX, TCY, TRX, TRY)
        if d_out < 0: continue
        d_in = -ell_dist(x, y, PCX, PCY, PRX, PRY)
        if d_in < 0: continue
        rn = math.sqrt(((x - TCX) / TRX) ** 2 + ((y - TCY) / TRY) ** 2)
        L = pool_light(x, y)
        zone = rn * 9 + (nD(x * 1.5, y * 3) - 0.5) * 0.7
        v = 2.0 + (math.floor(zone) % 2) * 0.9 + L * 2.2 + (nC(x, y) - 0.5) * 0.7
        if abs(zone - round(zone)) < 0.04: v -= 0.9
        if d_out < 1.2: tput(x, y, INK); continue
        if d_out < 5.5:                                                               # pale margin, lit on the near side
            tput(x, y, col('C', (6.2 if y > TCY else 4.6) - (1.0 if d_out < 2.4 else 0))); continue
        if d_in < 7:                                                                  # inner lip, lit by the pool
            tput(x, y, col('M', 1.2 + (7 - d_in) * 0.35 + (0.5 if y < PCY else 0)), glow=d_in < 2.5); continue
        tput(x, y, col('O', band(v + 1.0, x, y)))
# the pool: far inner wall + liquid mycelium
for y in range(PCY - PRY - 1, PCY + PRY + SINK + 2):
    for x in range(PCX - PRX - 1, PCX + PRX + 2):
        rp = ((x - PCX) / PRX) ** 2 + ((y - PCY) / PRY) ** 2
        if rp >= 1: continue
        rl = ((x - PCX) / (PRX - 2)) ** 2 + ((y - PCY - SINK) / (PRY - 1)) ** 2
        if rl >= 1:                                                                   # the far inner wall, lit green
            v = 2.0 + (y - (PCY - PRY)) / SINK * 2.5 + (nC(x, y) - 0.5) * 0.6
            tput(x, y, col('g', band(v, x, y)), glow=False)
            continue
        swirl = nA(x * 1.6 + 26 * math.sin(y / 7.0), y * 4.0)
        s = abs((swirl * 7) % 1 - 0.5)
        v = 3.0 + 2.8 * (1 - rl) + swirl * 1.2 + (1.3 if s < 0.035 else 0) + (nC(x, y) - 0.5) * 0.4
        if rl > 0.9: v -= 0.8
        tput(x, y, col('M', band(v, x, y)), glow=True)
    # lip highlight along the front inner edge
for x in range(PCX - PRX, PCX + PRX + 1):
    u = (x - PCX) / PRX
    if abs(u) >= 1: continue
    y = PCY + PRY * math.sqrt(1 - u * u)
    tput(x, y, col('M', 6 if abs(u) < 0.8 else 5), glow=True)
    tput(x, y + 1, col('C', 6))
# motes floating on the pool
r3 = random.Random(5)
for i in range(26):
    a = r3.random() * math.tau; rr = math.sqrt(r3.random()) * 0.85
    x, y = PCX + math.cos(a) * PRX * rr, PCY + SINK + math.sin(a) * PRY * rr * 0.9
    tput(x, y, col('M', 9), glow=True)

# tallow candles on the ring (front + ends; the back of the ring is where the archpriests rest their hands)
CANDLES = [(232, 452, 16), (318, 497, 12), (420, 508, 9), (646, 508, 11), (752, 497, 14), (834, 452, 18), (858, 438, 8)]
flames = []
for (cx_, cy_, hh) in CANDLES:
    for y in range(cy_ - hh, cy_ + 1):
        for x in range(cx_ - 3, cx_ + 4):
            u = (x - cx_) / 3.5
            v = 5.0 + 2.2 * (1 - u * u) - 1.2 * u - (1.6 if y >= cy_ - 1 else 0)
            if abs(u) > 0.95: v = 2.5
            tput(x, y, col('C', v))
    for (dx, dy) in ((2, 2), (2, 3), (2, 4), (-2, 3), (-2, 4), (-2, 5), (-2, 6)):                  # wax drips
        tput(cx_ + dx, cy_ - hh + dy, col('C', 8))
    for x in range(cx_ - 5, cx_ + 6): tput(x, cy_ + 1, col('C', 3 if abs(x - cx_) > 3 else 5))  # puddle of wax
    tput(cx_, cy_ - hh - 1, INK); tput(cx_, cy_ - hh - 2, INK)                                    # wick
    for (dx, dy, v) in ((0, -3, 7), (0, -4, 7), (0, -5, 6), (0, -6, 5), (-1, -3, 5), (1, -3, 5), (-1, -4, 5),
                        (1, -4, 4), (0, -7, 4), (0, -2, 6)):
        tput(cx_ + dx, cy_ - hh + dy, col('G', v), glow=True)
    flames.append(dict(x=cx_, y=cy_ - hh - 5))
# little glowing mushrooms sprouting at the table's edge
for (mx, my) in ((262, 420), (270, 424), (800, 420), (806, 416), (600, 512), (606, 514)):
    for yy in range(my - 5, my + 1): tput(mx, yy, col('M', 5), glow=True)
    for xx in range(-2, 3): tput(mx + xx, my - 6, col('M', 7), glow=True)
    tput(mx, my - 7, col('M', 8), glow=True)

# the glow layer keeps only what is actually visible (not veins hidden behind the seats or under the table)
for y in range(H):
    for x in range(W):
        g = GL[x, y]
        if g[3] == 0: continue
        t = T[x, y]
        vis = t[:3] if t[3] else P[x, y]
        if tuple(vis) != tuple(g[:3]): GL[x, y] = (0, 0, 0, 0)
img.save(f'{OUT}/council_bg.png')
tab.save(f'{OUT}/council_table.png')
glw.save(f'{OUT}/council_glow.png')
seats = {k: dict(zip(('x', 'y'), seat_anchor(k))) for k in SEATS}
json.dump(dict(seats=seats, candles=flames, glows=glow_points,
               pool=dict(x=PCX, y=PCY + SINK, rx=PRX, ry=PRY)), open(f'{OUT}/council.json', 'w'), indent=1)
print('ok', OUT)
