"""Guide layer for the Crossroad Aseprite template: every hotspot the scene code creates, in canvas (1067x600) coords."""
import sys
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1]
W, H = 1067, 600
KX = W / 800
g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
try: F = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf', 11)
except Exception: F = ImageFont.load_default()
def box(x, y, w, h, col, label, space800=True):
    if space800: x, w = round(x * KX), round(w * KX)
    d.rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], outline=col)
    d.rectangle([x - w / 2, y - h / 2 - 14, x - w / 2 + 6 * len(label) + 4, y - h / 2], fill=(40, 40, 40, 220))
    d.text((x - w / 2 + 2, y - h / 2 - 13), label, fill=col, font=F)
box(100, 400, 120, 200, (90, 220, 255), 'EXIT -> Shed 521')
box(400, 572, 150, 56, (90, 220, 255), 'EXIT -> Egg Cathedral (cesta k divakovi)')
box(650, 400, 100, 200, (90, 220, 255), 'EXIT -> Voxmarket')
box(409, 400, 52, 120, (90, 220, 255), 'EXIT -> Scraper (cesta k obzoru)')
box(400, 196, 230, 110, (255, 210, 60), 'POZOROVANI: rozcestnik')
box(408, 140, 130, 150, (120, 255, 140), 'SKYSHIP zona (po zasazeni spor)', space800=False)
# corpse sprite footprint (240x440, anchor bottom-centre at 533,496) + its clickable figure
d.rectangle([408 - 120, 496 - 440, 408 + 120, 496], outline=(255, 120, 200))
d.text((408 - 118, 496 - 440 + 2), 'MRTVOLA sprite 240x440 (kotva dole uprostred 408,496)', fill=(255, 120, 200), font=F)
d.rectangle([408 - 120 + 56, 496 - 440 + 136, 408 - 120 + 184, 496 - 1], outline=(255, 60, 160))
d.text((408 - 120 + 58, 496 - 440 + 138), 'klikaci oblast', fill=(255, 60, 160), font=F)
for x in range(0, W, 8): d.line([(x, 534), (x + 4, 534)], fill=(255, 80, 80))
d.text((4, 536), 'cara nohou y534 (hrac 128px)', fill=(255, 80, 80), font=F)
for x in range(0, W, 8): d.line([(x, 296), (x + 4, 296)], fill=(200, 200, 90))
d.text((4, 284), 'horizont / ubezny bod (533,296)', fill=(200, 200, 90), font=F)
g.save(f'{OUT}/guides.png')
