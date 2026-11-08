"""Writes the Aseprite palette for the two Townhall backgrounds (townhall.gpl): the 96 colours that best cover both
renders (median cut over the pair), sorted by hue family and lightness.
    python3 townhall_palette.py <townhall.png> <townhall_interior.png> <out.gpl>"""
import sys, colorsys
from PIL import Image
a, b = (Image.open(p).convert('RGB') for p in sys.argv[1:3])
both = Image.new('RGB', (a.width, a.height + b.height)); both.paste(a, (0, 0)); both.paste(b, (0, a.height))
q = both.quantize(colors=96, method=Image.Quantize.MEDIANCUT)
pal = q.getpalette()[:96 * 3]
cols = sorted({tuple(pal[i:i + 3]) for i in range(0, len(pal), 3)},
              key=lambda c: (round(colorsys.rgb_to_hsv(*(v / 255 for v in c))[0] * 8) % 8, sum(c)))
out = ['GIMP Palette', 'Name: Townhall', 'Columns: 12', '#'] + ['%3d %3d %3d\tTownhall %d' % (c + (i + 1,)) for i, c in enumerate(cols)]
open(sys.argv[3], 'w').write('\n'.join(out) + '\n')
print(len(cols), 'colours ->', sys.argv[3])
