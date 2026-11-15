"""A light restyle pass over the author's hand-drawn Master Thaal (idle + walk), so he sits
with the rest of the cast (the rig.py look: muted earthy ramps, form shading from the top left, material texture, warm
dark outlines instead of pure black). Nothing is redrawn: every pixel keeps its place, so the shapes, the faces and the
animation stay exactly the user's. Per pixel:
  * its material comes from the original colour (per-sprite rules: robe / cap / cream / wood / steel / plum / jade ...)
  * its tone = the original shade (its rank inside that material, so the user's own shading and folds stay) mixed with
    form light (a height field from the distance to the silhouette and to the drawn lines, lit from the top left),
    a little material texture, and a contact shadow under each material boundary
  * pure-black outer outlines become a warm dark of the material they wrap; black lines inside become a soft dark of
    the material; thick black areas touching the outside (the guardian's hood) become shaded black cloth; black areas
    enclosed by the figure (the faces under the hoods) stay voids; small glowing bits (eyes, the gem, the mouth grille)
    keep their colours
(The guardian went through it once too, then was redrawn for real: guardian.py; guardian_material stays for reference.)
Inputs (the user's originals) live in tools/artgen/ref/handmade_*.png.
python3 handmade_restyle.py <outdir>  ->  master_thaal.png, master_thaal_walk.png (same sheet layouts)"""
import sys, os, math, colorsys
from collections import deque
from PIL import Image
from common import ramp, make_noise, h32

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ref')
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
nF, nM = make_noise(2, 611, 420, 420), make_noise(5, 612, 420, 420)
L = (-0.55, -0.7, 0.45); _l = math.sqrt(sum(c * c for c in L)); L = tuple(c / _l for c in L)

R = {
    'robe':  ramp('#1e0e06 #321808 #4a240c #623210 #7c4116 #96521e #ac6428 #c07834 #d08e46'),   # Thaal's orange robe, muted
    'cap':   ramp('#2a1006 #46190a #66260e #883514 #a8461a #c25a22 #d6722e #e48e44 #eeac6a'),   # the mushroom cap
    'cream': ramp('#3a3026 #5a4c3c #7a6a56 #9a8a72 #b8aa90 #d2c6ac #e6dcc4 #f2ead8'),
    'wood':  ramp('#140c07 #20140c #2e1d12 #3d2718 #4e321f #603e27 #724b30 #86593a'),
    'skin':  ramp('#3a2014 #5a3420 #7a4a2e #9a6440 #b47c54 #c8946a'),
    'steel': ramp('#16161a #222327 #303237 #404348 #52565b #666a6e #7c8084 #94979a #aeb0b0 #c8c8c4'),
    'plum':  ramp('#1a0812 #2a0d1e #3c132b #501a3a #64234a #782e5a #8c3c6a #a04e7a'),
    'jade':  ramp('#1a2620 #26362e #34483e #435a4f #546e61 #668274 #7a9686 #90a998 #a8bcac'),
    'pink':  ramp('#3a1420 #5a2030 #7e3044 #a0465a #ba6476 #d08494'),
    'cloth': ramp('#060405 #0b0809 #120e10 #1a1518 #241e22 #2e2730'),                          # black cloth (the hood)
}
TEX = {'robe': 'fabric', 'cap': 'plain', 'cream': 'plain', 'wood': 'wood', 'skin': 'plain', 'steel': 'metal',
       'plum': 'fabric', 'jade': 'metal', 'pink': 'plain', 'cloth': 'fabric'}
def tex(kind, x, y):
    if kind == 'fabric': return (nF(x * 1.6, y * 1.6) - 0.5) * 0.10 + (0.025 if (x + y) % 2 else -0.025)
    if kind == 'wood': return (nF(x * 0.35, y * 2.2) - 0.5) * 0.12
    if kind == 'metal': return (nM(x * 0.8, y * 0.8) - 0.5) * 0.06 + (0.05 if h32(x, y >> 2, 5) % 41 == 0 else 0)
    return (nF(x, y) - 0.5) * 0.05

def hsv(c): h, s, v = colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255); return h * 360, s, v
def lum(c): return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

def thaal_material(c):
    h, s, v = hsv(c)
    if s < 0.1: return 'cream' if v > 0.85 else 'steel'
    if 250 <= h < 290: return None                       # the purple gem: keep
    if h >= 290 or h < 8: return 'pink'                  # the cap's spots
    if 45 <= h < 70: return None                         # yellow glints: keep
    if 8 <= h < 45:
        if s < 0.66 and v < 0.4: return 'wood'           # the staff, the hands
        if v > 0.93 and s > 0.55: return 'cap'
        return 'robe'
    return 'steel'

def guardian_material(c):
    h, s, v = hsv(c)
    if s < 0.1: return 'steel'
    if 290 <= h < 345: return 'plum'
    if 80 <= h < 170: return 'jade'
    if 8 <= h < 45:
        if v > 0.75: return 'skin'                       # (lit bits outside the hood; inside it they are kept as a glow)
        return 'wood'
    return 'steel'

def restyle_frame(im, material_of):
    W_, H_ = im.size
    src = im.load()
    out = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); p = out.load()
    alpha = lambda x, y: 0 <= x < W_ and 0 <= y < H_ and src[x, y][3] > 0
    black = lambda x, y: alpha(x, y) and max(src[x, y][:3]) < 20
    # thickness of black: 1 = a line, more = a filled black area
    blk = {(x, y) for y in range(H_) for x in range(W_) if black(x, y)}
    thick = {}
    for (x, y) in blk:
        thick[(x, y)] = 2 if all(((x + dx, y + dy) in blk) for dx in (-1, 0, 1) for dy in (-1, 0, 1)) else 1
    # grow thick areas by one pixel so their edge pixels belong to them too
    area = set(k for k, t in thick.items() if t == 2)
    area |= {(x + dx, y + dy) for (x, y) in list(area) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (x + dx, y + dy) in blk}
    # black areas: touching the outside -> cloth; enclosed -> a void (a face under a hood)
    comp, seen = {}, set()
    for s0 in area:
        if s0 in seen: continue
        q, members, outside = deque([s0]), [], False
        seen.add(s0)
        while q:
            x, y = q.popleft(); members.append((x, y))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if not alpha(*n): outside = True
                elif n in area and n not in seen: seen.add(n); q.append(n)
        big = len(members) > 60
        for m in members: comp[m] = 'cloth' if (outside and big) else 'void'
    # materials of the coloured pixels
    mat = {}
    for y in range(H_):
        for x in range(W_):
            if alpha(x, y) and (x, y) not in blk: mat[(x, y)] = material_of(src[x, y][:3])
    # glowing bits: small non-black pixels sitting mostly in a void / the hood -> keep their colour
    keep = set()
    for (x, y), m in mat.items():
        nb = sum(1 for dx in (-1, 0, 1) for dy in (-1, 0, 1) if comp.get((x + dx, y + dy)) in ('void', 'cloth'))
        if m is None or nb >= 3: keep.add((x, y))
    # height fields for form light: distance to the outside only (soft cloth), and to the outside + the drawn lines
    # (hard parts: armour plates, the staff); cloth taking the lines too would come out quilted
    def distance(with_lines):
        dist, q = {}, deque()
        for y in range(H_):
            for x in range(W_):
                if not alpha(x, y): continue
                edge = any(not alpha(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                line = with_lines and (x, y) in blk and (x, y) not in area
                if edge or line: dist[(x, y)] = 0; q.append((x, y))
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if alpha(*n) and n not in dist and dist[(x, y)] < 12: dist[n] = dist[(x, y)] + 1; q.append(n)
        return dist
    D_SIL, D_LINE = distance(False), distance(True)
    HARD = ('steel', 'wood', 'jade', 'skin')
    def hgt(x, y, m):
        if m in HARD: d = min(D_LINE.get((x, y), 9), 9) / 9; return 6 * math.sqrt(max(0.0, 1 - (1 - d) ** 2))
        d = min(D_SIL.get((x, y), 12), 12) / 12; dl = min(D_LINE.get((x, y), 9), 9) / 9
        return 7 * math.sqrt(max(0.0, 1 - (1 - d) ** 2)) + 1.2 * dl
    # the original shade of each pixel, ranked inside its material (so the user's own shading is kept)
    lums = {}
    for (x, y), m in mat.items():
        if m: lums.setdefault(m, []).append(lum(src[x, y]))
    rng = {m: (min(v), max(v)) for m, v in lums.items()}
    def tone_of(x, y, m, base_l):
        hx = (hgt(x + 1, y, m) - hgt(x - 1, y, m)) / 2; hy = (hgt(x, y + 1, m) - hgt(x, y - 1, m)) / 2
        n = (-hx, -hy, 1.0); nl = math.sqrt(n[0] ** 2 + n[1] ** 2 + 1); n = (n[0] / nl, n[1] / nl, 1 / nl)
        light = max(0.0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2])
        t = 0.6 * base_l + 0.4 * (light * 1.25 - 0.1) + tex(TEX[m], x, y)
        if m == 'steel': t += 0.12 + 0.35 * max(0.0, light - 0.8) * 5 * 0.2                 # polished metal: brighter, a sheen
        # a contact shadow just below / right of another material (layers of cloth, the cap's brim, the pauldrons)
        for dx, dy in ((0, -1), (-1, 0), (0, -2)):
            o = mat.get((x + dx, y + dy), comp.get((x + dx, y + dy)))
            if o is not None and o != m and (x + dx, y + dy) not in blk: t -= 0.08; break
        return t
    def put_tone(x, y, m, t):
        r = R[m]
        i = t * (len(r) - 1) + (BAYER[y % 4][x % 4] / 16 - 0.47) * 0.85
        p[x, y] = r[max(0, min(len(r) - 1, int(round(i))))] + (255,)
    for y in range(H_):
        for x in range(W_):
            if not alpha(x, y): continue
            if (x, y) in keep and (x, y) not in blk: p[x, y] = src[x, y]; continue
            if (x, y) in mat:
                m = mat[(x, y)]
                lo, hi = rng[m]
                base_l = (lum(src[x, y]) - lo) / max(1.0, hi - lo)
                put_tone(x, y, m, tone_of(x, y, m, 0.15 + 0.8 * base_l)); continue
            kind = comp.get((x, y))
            if kind == 'cloth':
                put_tone(x, y, 'cloth', tone_of(x, y, 'cloth', 0.35)); continue
            if kind == 'void':
                p[x, y] = R['cloth'][0 if (x * 7 + y * 3) % 11 else 1] + (255,); continue
            # a black line: outside edge -> a warm dark of the material it wraps; inside -> a soft dark of the material
            nbm = [mat.get((x + dx, y + dy)) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))]
            nbm = [m for m in nbm if m]
            outer = any(not alpha(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            m = max(set(nbm), key=nbm.count) if nbm else ('cloth' if any(comp.get((x + dx, y + dy)) for dx in (-1, 0, 1) for dy in (-1, 0, 1)) else None)
            if m is None: p[x, y] = (22, 16, 12, 255); continue
            if outer: p[x, y] = tuple(int(c * 0.55) for c in R[m][0]) + (255,)
            else: p[x, y] = R[m][1 if m != 'cloth' else 0] + (255,)
    return out

def restyle_sheet(name, fw, fh, material_of):
    sheet = Image.open(os.path.join(REF, 'handmade_' + name + '.png')).convert('RGBA')
    out = Image.new('RGBA', sheet.size, (0, 0, 0, 0))
    for fy in range(sheet.height // fh):
        for fx in range(sheet.width // fw):
            cell = sheet.crop((fx * fw, fy * fh, fx * fw + fw, fy * fh + fh))
            if cell.getbbox() is None: continue
            out.paste(restyle_frame(cell, material_of), (fx * fw, fy * fh))
    out.save(os.path.join(OUT, name + '.png'))

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    restyle_sheet('master_thaal', 128, 128, thaal_material)
    restyle_sheet('master_thaal_walk', 128, 128, thaal_material)
    print('ok', OUT)
