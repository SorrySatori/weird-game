"""Talking mouths: overlay sheets that open a character's mouth while they speak in a dialogue (utils/talk.js).

For each character in CHARS: the closed mouth's line in frame 0 of its idle sheet (x, y, width) and how many rows of
the jaw below it move down. Every idle frame is matched against frame 0 around the mouth (the head bobs with the
breath), and two states are drawn from that frame's own pixels: half open (the jaw 1 px down) and open (2 px), the gap
filled with the mouth's dark inside (the open one with its lower corners rounded off).

Output: assets/images/characters/talk/<sheet>.png, the idle sheet's frame size, 2 rows (half, open) x its frames. Only
the changed pixels are opaque, so the overlay laid exactly over the playing sprite shows the mouth and nothing else.
Being under assets/images/characters/ it takes the scene's light like the sprite it covers (utils/sceneLight.js).

    python3 tools/artgen/talk_mouths.py [--preview out.png]

Left out on purpose: faces without a mouth to open (Thaal's dark hood, the Guardian's grille, Gnur's speaker grille,
Hesh and Vell, the lamp Don, Lift-Mother the lift itself).
"""
import os, sys
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
DIR = os.path.join(ROOT, 'assets', 'images', 'characters')
OUT = os.path.join(DIR, 'talk')

# sheet (under characters/): frame w, h, (mouth x, y, width) in frame 0, jaw rows that move[, the inside's colour]
CHARS = {
    'edgar_eskola':        (128, 192, (53, 60, 9), 5, (78, 32, 32, 255)),   # dark fur: a red maw, or it doesn't show
    'heliodor_idle':       (128, 192, (62, 53, 5), 5),
    'ortolan_idle':        (128, 160, (60, 40, 8), 3),
    'elphi_idle':          (128, 160, (55, 41, 7), 4),
    'liris_idle':          (128, 160, (63, 42, 3), 3),
    'ravla_idle':          (128, 144, (58, 60, 5), 3),
    'senior_clerk':        (128, 192, (60, 47, 9), 6),
    'clerk_applications':  (128, 176, (62, 51, 5), 4),
    'voxmarket/zerren':    (176, 160, (80, 58, 16), 3),
    'voxmarket/kloor':     (128, 160, (98, 64, 6), 2),
}


def frames_of(sheet, fw, fh):
    cols, rows = sheet.width // fw, sheet.height // fh
    return [sheet.crop((c * fw, r * fh, c * fw + fw, r * fh + fh)) for r in range(rows) for c in range(cols)]


def track(f0, f, mx, my, w, reach=4):
    """the shift of frame f against frame 0 around the mouth (the face above it: nose, eyes)"""
    a, b = f0.load(), f.load()
    box = [(x, y) for y in range(my - 10, my + 4) for x in range(mx - 8, mx + w + 8)
           if 0 <= x < f0.width and 0 <= y < f0.height and a[x, y][3] > 0]
    best = (1 << 62, 0, 0)
    for dy in range(-reach, reach + 1):
        for dx in range(-reach, reach + 1):
            s = 0
            for (x, y) in box:
                X, Y = x + dx, y + dy
                p = b[X, Y] if 0 <= X < f.width and 0 <= Y < f.height else (0, 0, 0, 0)
                q = a[x, y]
                s += abs(p[0] - q[0]) + abs(p[1] - q[1]) + abs(p[2] - q[2]) + abs(p[3] - q[3])
            if s < best[0] or (s == best[0] and abs(dx) + abs(dy) < abs(best[1]) + abs(best[2])):
                best = (s, dx, dy)
    return best[1], best[2]


def inner_of(f, mx, my, w):
    """the mouth's dark inside: the darkest pixel of the closed line, darker still, a little warm"""
    px = f.load()
    line = [px[x, my] for x in range(mx, mx + w) if px[x, my][3] > 0] or [(60, 40, 40, 255)]
    r, g, b, _ = min(line, key=lambda c: c[0] + c[1] + c[2])
    return (max(14, int(r * 0.45) + 8), max(8, int(g * 0.35)), max(8, int(b * 0.35)), 255)


def mouth(f, mx, my, w, jaw, k, inner=None):
    """frame f with the mouth k px open, as an overlay (only the changed pixels opaque)"""
    src = f.load()
    out = Image.new('RGBA', f.size, (0, 0, 0, 0))
    o = out.load()
    inner = inner or inner_of(f, mx, my, w)
    H = f.height
    for x in range(mx - 1, mx + w + 1):
        if not 0 <= x < f.width: continue
        inside = mx <= x < mx + w
        for i in range(jaw):                                   # the jaw drops k px
            y = my + 1 + i
            if y + k < H and src[x, y][3] > 0: o[x, y + k] = src[x, y]
        for j in range(k):                                     # and opens the gap
            y = my + 1 + j
            if y >= H: continue
            corner = k == 2 and j == k - 1 and x in (mx, mx + w - 1) and w > 3
            if inside and not corner: o[x, y] = inner
            elif src[x, my + 1][3] > 0: o[x, y] = src[x, my + 1]   # the corners / cheeks stretch over the gap
    return out


def build(name, fw, fh, spec, jaw, inner=None):
    sheet = Image.open(os.path.join(DIR, name + '.png')).convert('RGBA')
    frames = frames_of(sheet, fw, fh)
    mx, my, w = spec
    out = Image.new('RGBA', (fw * len(frames), fh * 2), (0, 0, 0, 0))
    shifts = []
    for i, f in enumerate(frames):
        dx, dy = track(frames[0], f, mx, my, w) if i else (0, 0)
        shifts.append((dx, dy))
        for k in (1, 2):
            out.alpha_composite(mouth(f, mx + dx, my + dy, w, jaw, k, inner), (i * fw, (k - 1) * fh))
    path = os.path.join(OUT, name.split('/')[-1] + '.png')
    out.save(path)
    return frames, shifts, path


def preview(results, path, s=5):
    """frame 0 of each: closed / half / open, around the mouth"""
    tiles = []
    for name, (frames, fw, fh, spec, jaw, outp) in results.items():
        mx, my, w = spec
        ov = Image.open(outp)
        box = (mx - 12, my - 14, mx + w + 12, my + 12)
        row = []
        for k in (0, 1, 2):
            f = frames[0].copy()
            if k: f.alpha_composite(ov.crop((0, (k - 1) * fh, fw, k * fh)))
            c = f.crop(box)
            bg = Image.new('RGBA', c.size, (90, 90, 100, 255)); bg.alpha_composite(c)
            row.append(bg.resize((c.width * s, c.height * s), Image.NEAREST))
        t = Image.new('RGBA', (sum(r.width for r in row) + 20, row[0].height), (30, 30, 36, 255))
        x = 0
        for r in row: t.paste(r, (x, 0)); x += r.width + 10
        tiles.append(t)
    W = max(t.width for t in tiles)
    sheet = Image.new('RGBA', (W, sum(t.height + 8 for t in tiles)), (20, 20, 24, 255))
    y = 0
    for t in tiles: sheet.paste(t, (0, y)); y += t.height + 8
    sheet.save(path)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    results = {}
    for name, (fw, fh, spec, jaw, *inner) in CHARS.items():
        frames, shifts, outp = build(name, fw, fh, spec, jaw, inner[0] if inner else None)
        results[name] = (frames, fw, fh, spec, jaw, outp)
        print(name, len(frames), 'frames, head shifts', shifts)
    if '--preview' in sys.argv:
        preview(results, sys.argv[sys.argv.index('--preview') + 1])
