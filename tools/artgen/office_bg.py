"""The abandoned office behind Shed 521 (ShedAbandonedOfficeScene) -- the old AI picture kept as it is, re-pixelled.

The user wanted the room and especially the graffito BETTER DECAY THAN CHANGE kept 1:1, so nothing is redrawn:
`office_ref.png` (the original, 1536x1024, irregular ~4.6-5 px blocks) is resampled onto 356 logical columns (cell
4.31 px, the most common colour of each cell's middle -> crisp letters and edges) on a palette with own ramps for the
graffito's maroon paint, the exposed brick, the window light and the moss; the frame keeps logical rows 13..213 (the
rotten ceiling loses its top, the floor its last strip). Shown 3x in the game like Scraper 1140.

    python3 office_bg.py <outdir>   # -> office_356.png (logical), office.png (1067x600 =
                                    #    assets/images/backgrounds/ShedAbandonedOffice.png), chars.png, guides.png, office.gpl
"""
import os, sys
from PIL import Image, ImageDraw
from repix import LW, LH, K, family_palette, resample_mode, to_canvas, write_gpl

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, 'office_ref.png')
R0 = 13                                   # first logical row of the frame (keeps the graffito clear of the HUD buttons, top right)

FAMILIES = [
    ('paint', lambda h, s, v, c: (h < 0.07 or h > 0.95) and s > 0.35 and v < 0.32, 10),     # the graffito
    ('brick', lambda h, s, v, c: 0.02 <= h <= 0.10 and s > 0.40 and 0.22 <= v <= 0.65, 8),
    ('light', lambda h, s, v, c: v > 0.48 and 0.07 <= h <= 0.18 and s > 0.28, 8),           # windows, lamp-lit spots
    ('moss', lambda h, s, v, c: 0.17 <= h <= 0.45 and s > 0.25 and v > 0.12, 8),
]


def overlays():
    ch = Image.open(os.path.join(HERE, 'chars.png')).convert('RGBA').resize((LW, LH), Image.NEAREST)
    g = Image.new('RGBA', (LW, LH), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    def zone(cx, cy, w, h, col):
        d.rectangle([(cx - w / 2) / K, (cy - h / 2) / K, (cx + w / 2) / K - 1, (cy + h / 2) / K - 1], outline=col)
    kx = 1067 / 800
    zone(50 * kx, 470, 50 * kx, 200, (255, 200, 80, 255))        # back to the stairs (left edge)
    zone(352 * kx, 205, 78 * kx, 156, (127, 255, 142, 255))      # to the Hall (the back doorway)
    d.line([(0, 178), (LW, 178)], fill=(255, 80, 80, 255))
    return ch, g


def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    src = Image.open(REF).convert('RGB')
    pal = family_palette(src, FAMILIES, 34)
    full = resample_mode(src, pal)
    logical = full.crop((0, R0, LW, R0 + LH))
    logical.save(os.path.join(out, 'office_356.png'))
    to_canvas(logical).save(os.path.join(out, 'office.png'))
    ch, g = overlays(); ch.save(os.path.join(out, 'chars.png')); g.save(os.path.join(out, 'guides.png'))
    write_gpl(os.path.join(out, 'office.gpl'), 'shed-abandoned-office', pal)
    print('palette', len(pal), 'colours; logical rows', full.size[1])


if __name__ == '__main__':
    main()
