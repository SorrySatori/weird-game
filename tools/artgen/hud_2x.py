"""The HUD buttons on the game's 2x pixel grid: the 48x48 frames of hud_buttons.py halved to 24x24 art pixels (shapes
and colours of the approved drawing kept by grid2x.rep_down), then the detail halving loses is drawn again by hand,
one art pixel = 2x2 screen pixels: the map's route, peaks and X, the open journal's lines, the quest note's
checkboxes and lines, the badge's "!". Saved pre-scaled (48x48 frames), so utils/hudButton.js is unchanged.

  python3 tools/artgen/hud_2x.py      (reads the 1x original via grid2x.master: tools/artgen/masters_1x/...)
"""
import os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from grid2x import REPO, master, rep_down, up

PATH = os.path.join(REPO, 'assets/images/ui/hud_buttons.png')
F = 48

INK = (84, 60, 44)           # the paper's brown ink
RED, RED_DARK = (196, 52, 46), (128, 30, 30)
GLOW = (246, 168, 118)       # the X glowing on the open map
GREEN, GREEN_LIT = (60, 140, 90), (150, 240, 140)
WHITE = (244, 236, 214)


def px(img, pts, col):
    p = img.load()
    for x, y in pts:
        p[x, y] = col + (255,)


def dashes(y, x0, x1, gaps=()):
    return [(x, y) for x in range(x0, x1 + 1) if x not in gaps]


def clear(img, x0, y0, x1, y1):
    """Flatten a paper area to its own commonest colour: the halved 1 px lines leave stray dots."""
    p = img.load()
    cols = [p[x, y] for y in range(y0, y1 + 1) for x in range(x0, x1 + 1) if p[x, y][3]]
    paper = max(set(cols), key=cols.count)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if p[x, y][3]: p[x, y] = paper
    return paper[:3]


INK_SOFT = (128, 98, 70)     # text lines read lighter than drawn marks


def map_closed(f):
    clear(f, 9, 6, 14, 17); clear(f, 16, 6, 19, 17)
    px(f, [(10, 16), (12, 15), (14, 14)], RED_DARK)                       # the route over the folded panels
    px(f, [(16, 13)], RED)
    px(f, [(17, 10), (19, 10), (18, 11), (17, 12), (19, 12)], RED)         # X
    px(f, [(15, 8), (16, 7), (17, 8), (18, 7), (19, 8)], INK)              # two peaks


def map_open(f):
    clear(f, 9, 5, 21, 19)
    px(f, [(15, y) for y in range(5, 20)], (238, 226, 196))                # the fold, lighter
    px(f, [(10, 17), (12, 16), (14, 15), (16, 13)], RED)
    px(f, [(17, 10), (19, 10), (17, 12), (19, 12)], RED)
    px(f, [(18, 11)], GLOW)
    px(f, [(16, 8), (17, 7), (18, 8), (19, 7), (20, 8)], INK)


def journal_open(f):
    clear(f, 2, 6, 10, 19); clear(f, 14, 6, 21, 19)
    for y, gaps in ((8, (6,)), (11, (5,)), (14, (8,)), (17, ())):
        px(f, dashes(y, 3, 9 if y != 17 else 6, gaps), INK_SOFT)           # the left page's lines
    px(f, [(17, 7), (18, 7), (19, 7), (16, 8), (20, 8), (18, 9), (18, 10)], INK)   # a little mushroom sketch
    for y in (13, 16):
        px(f, dashes(y, 15, 20, (17,) if y == 13 else ()), INK_SOFT)


def quests(f, lit):
    clear(f, 6, 6, 18, 16)
    px(f, dashes(7, 10, 15), INK)                                          # the note's heading
    for y in (9, 13):
        box = [(7, y), (8, y), (9, y), (7, y + 1), (9, y + 1), (7, y + 2), (8, y + 2), (9, y + 2)]
        px(f, box, INK)
        px(f, dashes(y + 1, 11, 17, (14,)), INK_SOFT)
    px(f, dashes(17, 11, 14 if lit else 16), INK_SOFT)                     # a last line (the corner lifts on hover)
    px(f, [(8, 10), (9, 9), (10, 8)], GREEN_LIT if lit else GREEN)         # the first one ticked


def badge(f):
    a = f.getchannel('A')
    x0, y0, x1, y1 = a.getbbox()
    cx = (x0 + x1 - 1) // 2
    top = y0 + 2                                                           # below the rim: bar, gap, dot
    px(f, [(cx, top), (cx, top + 1)], WHITE)
    px(f, [(cx, top + 3)], WHITE)


DETAIL = {2: map_closed, 3: map_open, 5: journal_open, 6: lambda f: quests(f, False), 7: lambda f: quests(f, True), 8: badge}

if __name__ == '__main__':
    src = master(PATH).convert('RGBA')
    out = Image.new('RGBA', src.size, (0, 0, 0, 0))
    for i in range(src.width // F):
        low = rep_down(src.crop((i * F, 0, i * F + F, F)))
        if i in DETAIL: DETAIL[i](low)
        out.paste(up(low, (F, F)), (i * F, 0))
    out.save(PATH)
    print('hud_buttons.png on the 2x grid')
