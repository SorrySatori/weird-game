"""Renders the trailer's text as transparent 1920×1080 PNGs (out/titles/<id>.png) for build.mjs to overlay.

    python3 tools/trailer/titles.py

Text and styles live in TITLES below; edit.js refers to them by id.
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, 'out', 'titles')
W, H = 1920, 1080

FONT = '/usr/share/fonts/gsfonts/P052-Roman.otf'  # one face for every line of the trailer
NOIR_FONT = os.path.join(HERE, 'fonts', 'SpecialElite-Regular.ttf')   # the noir cut: a typewriter, all capitals (Apache 2.0)

BONE = (232, 226, 207)
SPORE = (127, 255, 142)    # the game's UI green
GROWTH = (163, 234, 163)
DECAY = (214, 128, 72)

# id -> list of lines; each line: (text, size, colour, tracking em, y centre)
TITLES = {
    'agarida': [("Deep beneath the earth, the mycelium carries a cry for help.", 44, BONE, 0.02, 1015)],
    'city': [("A city built on the bones of dead gods", 48, BONE, 0.02, 1015)],
    'gods': [("THE GODS ARE DEAD.", 76, BONE, 0.18, 540)],
    'paperwork': [("THE PAPERWORK IS NOT.", 76, BONE, 0.18, 540)],
    'grow': [("GROW", 120, GROWTH, 0.22, 520)],
    'decay': [("OR DECAY", 120, DECAY, 0.22, 520)],
    'logo': [
        ("UPPER MORKEZELA", 124, BONE, 0.16, 500),
        ("A WEIRD GAME", 34, SPORE, 0.5, 610),
    ],
    'cta': [
        ("FREE DEMO", 84, BONE, 0.2, 380),
        ("COMING SOON", 40, SPORE, 0.45, 485),
        ("Wishlist on Steam", 46, BONE, 0.04, 620),
    ],
}


def tip(label, *lines):
    """A "10 tips" card: the small green label, then one or two lines of the tip."""
    if len(lines) == 1:
        return [(label, 40, SPORE, 0.5, 450), (lines[0], 66, BONE, 0.12, 560)]
    return [(label, 40, SPORE, 0.5, 400), (lines[0], 66, BONE, 0.12, 510), (lines[1], 66, BONE, 0.12, 605)]


# The gameplay trailer: ten tips for visiting Upper Morkezela (the idea of the 2025 YouTube trailer).
TITLES.update({
    'dream': [("I had a strange dream that I became a mushroom…", 46, BONE, 0.02, 1015)],
    'tips_title': [
        ("10 TIPS FOR VISITING", 44, SPORE, 0.4, 610),
        ("UPPER MORKEZELA", 112, BONE, 0.16, 710),
    ],
    'tip1': tip("TIP 1", "MAKE SOME FRIENDS"),
    'tip2': tip("TIP 2", "DON'T TAKE DRUGS", "FROM STRANGERS"),
    'tip3': tip("TIP 3", "OR DO… YOU KNOW,", "IF YOU WANNA HAVE SOME FUN"),
    'tip4': tip("TIP 4", "WRITE IN YOUR JOURNAL", "REGULARLY"),
    'tip5': tip("TIP 5", "GO SEE SOME SIGHTS"),
    'tip6': tip("TIP 6", "DON'T TOUCH", "EVERYTHING YOU SEE"),
    'tip7': tip("TIP 7", "DON'T USE BRAIN ROT", "ON PEOPLE YOU LIKE"),
    'tip8': tip("TIP 8", "BE NICE TO LOCALS"),
    'tip9': tip("TIP 9", "USE PUBLIC TRANSPORT.", "IT'S CHEAP AND EFFECTIVE"),
    'tip10': tip("TIP 10", "DON'T POKE THE BEAR"),
    'bonus': tip("BONUS TIP", "DON'T EXPECT", "ANYTHING NORMAL"),
    'joke': [
        ("…or, you know, when it's ready.", 46, BONE, 0.02, 500),
        ("I'm not a machine.", 46, BONE, 0.02, 580),
    ],
})

BACKDROP = set()   # ids drawn with a soft dark pad behind the text (the noir captions)

# Small studio logo on the end card.
LOGOS = {'cta': (os.path.join(REPO, 'assets', 'images', 'ui', 'TempurraLogo.png'), 170, 850)}


def tracked_width(font, text, tracking):
    return sum(font.getlength(ch) for ch in text) + tracking * font.size * (len(text) - 1)


def draw_line(layer, text, size, colour, tracking, cy, face=FONT):
    font = ImageFont.truetype(face, size)
    d = ImageDraw.Draw(layer)
    x = (W - tracked_width(font, text, tracking)) / 2
    ascent, descent = font.getmetrics()
    y = cy - (ascent + descent) / 2
    for ch in text:
        d.text((x, y), ch, font=font, fill=colour + (255,))
        x += font.getlength(ch) + tracking * size


def render(tid, lines):
    text = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for line in lines:
        draw_line(text, *line)
    # soft dark halo so the text reads over bright pixel art; a faint coloured glow on top
    alpha = text.getchannel('A')
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    shadow.putalpha(alpha.filter(ImageFilter.GaussianBlur(10)).point(lambda a: min(255, int(a * 1.6))))
    glow_colour = lines[0][2]
    glow = Image.new('RGBA', (W, H), glow_colour + (0,))
    glow.putalpha(alpha.filter(ImageFilter.GaussianBlur(18)).point(lambda a: int(a * 0.35)))
    out = Image.alpha_composite(Image.alpha_composite(shadow, glow), text)
    if tid in BACKDROP:
        # subtitles over busy pictures (the painting): a soft dark pad behind the lines
        x0, y0, x1, y1 = alpha.getbbox()
        pad = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(pad).rounded_rectangle((x0 - 46, y0 - 22, x1 + 46, y1 + 24), radius=26, fill=(0, 0, 0, 120))
        out = Image.alpha_composite(pad.filter(ImageFilter.GaussianBlur(20)), out)
    if tid in LOGOS:
        path, size, cy = LOGOS[tid]
        logo = Image.open(path).convert('RGBA').resize((size, size), Image.LANCZOS)
        out.alpha_composite(logo, ((W - size) // 2, cy - size // 2))
    out.save(os.path.join(OUT, f'{tid}.png'))


# The noir release cut (edit.js 'noir' / 'noir_cs'): the apprentice's narration from noir.json, in both languages,
# as subtitles at the bottom → nr_<lang>_<caption id>.png, the logo nr_logo, the end card nr_<lang>_cta.png. Every line
# of this cut is in the typewriter face, in capitals (the user's choice).
import json
from itertools import combinations
NOIR = json.load(open(os.path.join(HERE, 'noir.json'), encoding='utf-8'))
CAP_SIZE, CAP_TRACK, CAP_MAX, CAP_LH = 40, 0.0, 1600, 54


def caption(text):
    """In capitals, on as few balanced lines as fit (up to three); a one-letter word (Czech V, K, S, Z, A, I…) never
    ends a line; a no-break space in noir.json keeps "Shed 521" or "Feral Toast" together."""
    text = text.upper()
    font = ImageFont.truetype(NOIR_FONT, CAP_SIZE)
    width = lambda s: tracked_width(font, s, CAP_TRACK)
    words = text.split(' ')
    ok = [k for k in range(1, len(words)) if len(words[k - 1]) > 1]
    best = [text]
    for n in (1, 2, 3):
        cands = [()] if n == 1 else list(combinations(ok, n - 1))
        if not cands: continue
        split = lambda ks: [' '.join(words[a:b]) for a, b in zip((0,) + ks, ks + (len(words),))]
        lines = min((split(ks) for ks in cands), key=lambda ls: max(width(l) for l in ls))
        best = lines
        if max(width(l) for l in lines) <= CAP_MAX: break
    n = len(best)
    return [(l, CAP_SIZE, BONE, CAP_TRACK, 1022 - (n - 1 - i) * CAP_LH, NOIR_FONT) for i, l in enumerate(best)]


TITLES['nr_logo'] = [("UPPER MORKEZELA", 112, BONE, 0.06, 500, NOIR_FONT), ("A WEIRD GAME", 34, SPORE, 0.3, 612, NOIR_FONT)]
for lang in ('en', 'cs'):
    for cid, texts in NOIR['captions'].items():
        TITLES[f'nr_{lang}_{cid}'] = caption(texts[lang])
        BACKDROP.add(f'nr_{lang}_{cid}')
    big, small = NOIR['cards']['cta'][lang]
    TITLES[f'nr_{lang}_cta'] = [(big.upper(), 80, BONE, 0.12, 420, NOIR_FONT), (small.upper(), 38, SPORE, 0.2, 525, NOIR_FONT)]
    LOGOS[f'nr_{lang}_cta'] = (os.path.join(REPO, 'assets', 'images', 'ui', 'TempurraLogo.png'), 170, 760)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for tid, lines in TITLES.items():
        render(tid, lines)
        print('title', tid)
