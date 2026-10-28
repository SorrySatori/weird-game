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

BONE = (232, 226, 207)
SPORE = (127, 255, 142)    # the game's UI green
GROWTH = (163, 234, 163)
DECAY = (214, 128, 72)

# id -> list of lines; each line: (text, size, colour, tracking em, y centre)
TITLES = {
    'hymnar': [("Deep beneath the earth, the mycelium carries a cry for help.", 44, BONE, 0.02, 1015)],
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

# Small studio logo on the end card.
LOGOS = {'cta': (os.path.join(REPO, 'assets', 'images', 'ui', 'TempurraLogo.png'), 170, 850)}


def tracked_width(font, text, tracking):
    return sum(font.getlength(ch) for ch in text) + tracking * font.size * (len(text) - 1)


def draw_line(layer, text, size, colour, tracking, cy):
    font = ImageFont.truetype(FONT, size)
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
    if tid in LOGOS:
        path, size, cy = LOGOS[tid]
        logo = Image.open(path).convert('RGBA').resize((size, size), Image.LANCZOS)
        out.alpha_composite(logo, ((W - size) // 2, cy - size // 2))
    out.save(os.path.join(OUT, f'{tid}.png'))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for tid, lines in TITLES.items():
        render(tid, lines)
        print('title', tid)
