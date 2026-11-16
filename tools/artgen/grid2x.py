"""Snap art onto the game's 2x pixel grid (one art pixel = 2x2 screen pixels; the world is 533x300 shown x2).

The picture keeps its size, so no scene code changes: every 2x2 block becomes one colour, the block's own colour
closest to its mean (no new colours, edges stay crisp). Sprite edges keep their darkest pixel, so the 1 px outlines
survive. The 1x master is kept in tools/artgen/masters_1x/ (same relative path)
on the first run and whenever the asset is found off the grid (a fresh 1x export); otherwise runs start from it, so
re-running is safe.

  python3 tools/artgen/grid2x.py bg assets/images/backgrounds/crossroad.png [--signs crossroad]
  python3 tools/artgen/grid2x.py bg assets/images/backgrounds/Shed521_floors.png --text floors_bg   (textspec.py)
  python3 tools/artgen/grid2x.py bgs        every background, with its lettering (BGS) and the ink pass
  python3 tools/artgen/grid2x.py sheet assets/images/characters/priest.png --frame 128x128
"""
import argparse, collections, json, os, shutil, sys
from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MASTERS = os.path.join(HERE, 'masters_1x')
K = 2
OUTLINE = (24, 20, 22, 255)
sys.path.insert(0, HERE)
from common import text_width, draw_text   # the backgrounds' own 3x5 sign font


def rep_down(img, k=K):
    """k x k blocks -> one pixel: the block's own colour closest to its mean. RGBA: a block is opaque when >= 40 % of
    it is (its colour from the opaque pixels only); an edge block with less keeps its darkest opaque pixel, so the
    sprites' own 1 px outlines and thin parts (a tail, a cable) survive as one art pixel instead of vanishing."""
    img = img.convert('RGBA')
    w, h = (img.width + k - 1) // k, (img.height + k - 1) // k
    pad = Image.new('RGBA', (w * k, h * k), (0, 0, 0, 0)); pad.paste(img, (0, 0))
    src, out = pad.load(), Image.new('RGBA', (w, h), (0, 0, 0, 0))
    dst = out.load()
    for by in range(h):
        for bx in range(w):
            px = [src[bx * k + i, by * k + j] for j in range(k) for i in range(k)]
            if any(0 < p[3] < 255 for p in px):
                # soft alpha (glows, shadows, soft edges): the block keeps its mean alpha, coloured by its most opaque
                # pixel nearest to the alpha-weighted mean colour
                vis = [p for p in px if p[3]]; wsum = sum(p[3] for p in vis)
                mr, mg, mb = (sum(p[c] * p[3] for p in vis) / wsum for c in range(3))
                best = min(vis, key=lambda p: (p[0] - mr) ** 2 + (p[1] - mg) ** 2 + (p[2] - mb) ** 2 - p[3])
                dst[bx, by] = best[:3] + (round(wsum / (k * k)),); continue
            op = [p for p in px if p[3] > 127]
            if not op: continue
            if len(op) < 0.4 * k * k:
                dk = min(op, key=lambda p: p[0] + p[1] + p[2]); dst[bx, by] = dk[:3] + (255,); continue
            mr, mg, mb = (sum(p[c] for p in op) / len(op) for c in range(3))
            best = min(op, key=lambda p: (p[0] - mr) ** 2 + (p[1] - mg) ** 2 + (p[2] - mb) ** 2)
            dst[bx, by] = best[:3] + (255,)
    return out


def outline(spr, col=OUTLINE):
    """One-pixel outline round the silhouette (4-neighbourhood), at the sprite's own (low-res) grid."""
    s, o = spr.load(), spr.copy()
    d = o.load()
    for y in range(spr.height):
        for x in range(spr.width):
            if s[x, y][3]: continue
            if any(0 <= x + dx < spr.width and 0 <= y + dy < spr.height and s[x + dx, y + dy][3]
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                d[x, y] = col
    return o


def up(low, size, k=K):
    return low.resize((low.width * k, low.height * k), Image.NEAREST).crop((0, 0) + size)


# ---- lettering: a halved 3x5 font is mush, so the signs are drawn again with one-art-pixel letters

def _mode(cols): return collections.Counter(cols).most_common(1)[0][0]


def _sign_colours(orig, txt, cx, ty, sc):
    pts = set(); w = text_width(txt, sc); draw_text(lambda x, y: pts.add((x, y)), txt, cx - w // 2, ty, sc)
    o = orig.load(); x0 = cx - w // 2
    fg = _mode([o[x, y][:3] for x, y in pts])
    bg = _mode([o[x, y][:3] for x in range(x0 - 2, x0 + w + 2) for y in range(ty - 2, ty + 5 * sc + 2) if (x, y) not in pts])
    return fg, bg


def signs_crossroad(low, orig):
    """crossroad_bg.py's SIGNS (two plates at 3 px letters, four signpost arms at 2 px): crossroad_signs.json."""
    G = json.load(open(os.path.join(HERE, 'crossroad_signs.json')))
    d, P = ImageDraw.Draw(low), low.load()
    put = lambda c: (lambda x, y: P.__setitem__((x, y), c + (255,)))
    for txt, cx, ty, sc in G['signs'][:2]:
        fg, bg = _sign_colours(orig, txt, cx, ty, sc)
        wo = text_width(txt, sc)
        d.rectangle([(cx - wo // 2) // K - 1, ty // K - 1, (cx + wo - wo // 2) // K + 1, (ty + 5 * sc) // K + 1], fill=bg)
        w = text_width(txt, 1); x0, y0 = round(cx / K) - w // 2, round((ty + 2.5 * sc) / K - 2.5)
        draw_text(put(fg), txt, x0, y0, 1)
    pxl = round(G['POST_X'] / K); post = low.crop((pxl - 2, 0, pxl + 3, low.height))
    for (txt, sgn, ay), (_, cx, ty, sc) in zip(G['arms'], G['signs'][2:]):
        fg, bg = _sign_colours(orig, txt, cx, ty, sc)
        a, w = round(ay / K), text_width(txt, 1)
        hh, L = 5, w + 12                                            # the arm of crossroad_bg.py, halved
        if sgn < 0: pts = [(pxl, a - hh), (pxl - L + hh, a - hh), (pxl - L, a), (pxl - L + hh, a + hh), (pxl, a + hh)]; tx = pxl - L + hh + 1
        else: pts = [(pxl, a - hh), (pxl + L - hh, a - hh), (pxl + L, a), (pxl + L - hh, a + hh), (pxl, a + hh)]; tx = pxl + 4
        d.polygon(pts, fill=bg, outline=tuple(int(c * 0.55) for c in bg))
        draw_text(put(fg), txt, tx, a - 2, 1)
    low.paste(post, (pxl - 2, 0))                                    # the post stays in front of its arms


def signs_spec(low, orig, spec):
    """Lettering recorded by textspec.py ([text, x, y, scale] per draw_text call): cleared and drawn again at half the
    scale (a 3x font becomes 1x, smaller; a 1x one stays 1x, bigger), centred where it was, in its own colours."""
    d, P = ImageDraw.Draw(low), low.load()
    for txt, x, y, sc in json.load(open(os.path.join(HERE, 'textspecs', spec + '.json'))):
        w = text_width(txt, sc)
        fg, bg = _sign_colours(orig, txt, x + w // 2, y, sc)
        d.rectangle([x // K, y // K, (x + w - 1) // K, (y + 5 * sc - 1) // K], fill=bg)
        s2 = max(1, sc // K); w2 = text_width(txt, s2)
        draw_text(lambda px, py: P.__setitem__((px, py), fg + (255,)), txt,
                  round((x + w / 2) / K - w2 / 2), round((y + 2.5 * sc) / K - 2.5 * s2), s2)


def signs_entrycity(low, orig):
    """The overlook's signpost: its arrow shaft is 2 px on odd rows (419-420), so halving drops it; one art pixel."""
    ImageDraw.Draw(low).line([(932 // K, 419 // K + 1), (987 // K, 419 // K + 1)], fill=(200, 200, 172, 255))


SIGNS = {'crossroad': signs_crossroad, 'entrycity': signs_entrycity}


def ink_pass(low, T=28, k=0.8, shade=0.25, max_luma=75):
    """Ink contours on the art grid (after Primordia's drawn line): where a pixel is darker than a 4-neighbour by more
    than T, it is the shadow side of an edge and goes most of the way to its own colour at `shade`, a one-art-pixel
    line. Only mid and dark tones take ink (a lit surface's texture would turn to blotches), and a lone inked pixel is
    dropped (texture grain, not a line). The generators' own 1 px depth outlines don't survive halving; this replaces
    them with lines the 2x grid can hold."""
    lum = lambda p: 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]
    s = low.load(); W, H = low.size; mark = set()
    for y in range(H):
        for x in range(W):
            if not s[x, y][3]: continue
            lp = lum(s[x, y])
            if lp > max_luma: continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                X, Y = x + dx, y + dy
                if 0 <= X < W and 0 <= Y < H and s[X, Y][3] and lum(s[X, Y]) - lp > T:
                    mark.add((x, y)); break
    for x, y in mark:
        if any((x + i, y + j) in mark for i in (-1, 0, 1) for j in (-1, 0, 1) if i or j):
            p = s[x, y]; s[x, y] = tuple(int(p[c] * (1 - k + shade * k)) for c in range(3)) + (p[3],)


def on_grid(img, k=K):
    """True when the picture is (nearly) all k x k blocks already, i.e. made by this script."""
    im = img.convert('RGBA'); w, h = im.width // k * k, im.height // k * k
    im = im.crop((0, 0, w, h))
    back = im.resize((w // k, h // k), Image.NEAREST).resize((w, h), Image.NEAREST)
    diff = ImageChops.difference(im, back).convert('L').point(lambda v: 255 if v > 8 else 0)
    return diff.histogram()[255] < 0.01 * w * h


def master(path, block=K):
    """The 1x original, kept in masters_1x. The first run copies it there; so does any later run that finds a picture
    off the grid in place of the converted one (a fresh export from a generator or Aseprite), so a re-run never
    converts a stale original over new work."""
    rel = os.path.relpath(os.path.abspath(path), REPO)
    m = os.path.join(MASTERS, rel)
    if not os.path.exists(m) or not on_grid(Image.open(path), block):
        os.makedirs(os.path.dirname(m), exist_ok=True); shutil.copy2(path, m)
    return Image.open(m)


def do_bg(path, signs=None, text=None, ink=False):
    orig = master(path).convert('RGBA')
    low = rep_down(orig)
    if signs: SIGNS[signs](low, orig)
    if text: signs_spec(low, orig, text)
    if ink: ink_pass(low)
    keep_alpha = orig.getchannel('A').getextrema()[0] < 255          # an overlay (a counter in front of the bg)
    up(low, orig.size).convert('RGBA' if keep_alpha else 'RGB').save(path)


def do_sheet(path, fw, fh, add_outline=False, block=K, out_path=None):
    """block = texture pixels per art pixel: 2 for art shown at scale 1, 4 for art the game shows at 0.5.
    out_path: write a converted copy there and leave the original in place (item icons: utils/itemIcons.js)."""
    orig = (Image.open(path) if out_path else master(path, block)).convert('RGBA')   # --out: the original stays put
    out = Image.new('RGBA', orig.size, (0, 0, 0, 0))
    for y in range(0, orig.height, fh):
        for x in range(0, orig.width, fw):
            low = rep_down(orig.crop((x, y, x + fw, y + fh)), block)
            if add_outline: low = outline(low)
            out.paste(up(low, (fw, fh), block), (x, y))
    if out_path: os.makedirs(os.path.dirname(out_path), exist_ok=True)
    out.save(out_path or path)


def do_atlas(path, json_path):
    """A Phaser atlas (Aseprite JSON): every frame on its own, so odd-width frames don't share blocks."""
    orig = master(path).convert('RGBA')
    frames = json.load(open(json_path))['frames']
    out = Image.new('RGBA', orig.size, (0, 0, 0, 0))
    for f in (frames.values() if isinstance(frames, dict) else frames):
        x, y, w, h = (f['frame'][c] for c in ('x', 'y', 'w', 'h'))
        out.paste(up(rep_down(orig.crop((x, y, x + w, y + h))), (w, h)), (x, y))
    out.save(path)


# every background of the game on the grid, with its lettering and ink: `grid2x.py bgs` re-runs them all
BGS = {
    'crossroad.png': {'signs': 'crossroad'}, 'EntryCity.png': {'signs': 'entrycity'},
    'Shed521_floors.png': {'text': 'floors_bg'}, 'Shed521_gate.png': {'text': 'gate_bg'},
    'ShedApplications.png': {'text': 'applications_bg'}, 'ScraperAmbra.png': {'text': 'ambra_bg'},
    'ShedMutationCourtyard.png': {'text': 'courtyard_bg'}, 'Shed521.png': {'text': 'shed521_bg'},
    'Shed521_growth.png': {'text': 'shed521_bg'}, 'Shed521_decay.png': {'text': 'shed521_bg'},
}
NOT_BGS = {'background.png', 'crossroad_corpse.png'}   # an unused old picture; the corpse is a sheet


def do_bgs():
    d = os.path.join(REPO, 'assets/images/backgrounds')
    for name in sorted(os.listdir(d)):
        if not name.endswith('.png') or name in NOT_BGS: continue
        opt = BGS.get(name, {})
        do_bg(os.path.join(d, name), opt.get('signs'), opt.get('text'), ink=True)
        print('  ', name)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('kind', choices=['bg', 'sheet', 'atlas', 'bgs'])
    ap.add_argument('path', nargs='?')
    ap.add_argument('--signs', choices=sorted(SIGNS))
    ap.add_argument('--text', help='a textspecs/<name>.json recorded by textspec.py (bg)')
    ap.add_argument('--ink', action='store_true', help='ink contours on the art grid (bg)')
    ap.add_argument('--frame', help='WxH of one frame (sheet)')
    ap.add_argument('--json', help='the atlas JSON (atlas)')
    ap.add_argument('--out', help='write the converted copy here, keep the original (sheet)')
    ap.add_argument('--block', type=int, default=K, help='texture px per art px (sheet): 4 for art shown at 0.5')
    ap.add_argument('--outline', action='store_true', help='add a dark ring round the silhouette (sheet)')
    a = ap.parse_args()
    if a.kind == 'bgs': do_bgs()
    elif a.kind == 'bg': do_bg(a.path, a.signs, a.text, a.ink)
    elif a.kind == 'atlas': do_atlas(a.path, a.json)
    else:
        fw, fh = map(int, a.frame.split('x'))
        do_sheet(a.path, fw, fh, a.outline, a.block, a.out)
    print('2x grid:', a.path or 'all backgrounds')
