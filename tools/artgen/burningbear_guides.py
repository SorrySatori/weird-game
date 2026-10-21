import sys
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1]; W, H = 1067, 600; KX = W / 800
g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
try: F = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf', 11)
except Exception: F = ImageFont.load_default()
def box(x, y, w, h, col, label, canvas=False):
    if not canvas: x, w = round(x * KX), round(w * KX)
    d.rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], outline=col)
    d.rectangle([x - w / 2, y - h / 2 - 14, x - w / 2 + 6 * len(label) + 4, y - h / 2], fill=(40, 40, 40, 220))
    d.text((x - w / 2 + 2, y - h / 2 - 13), label, fill=col, font=F)
box(50, 470, 80, 200, (90, 220, 255), 'EXIT <- Scraper (pruchod)')
box(400, 375, 90, 110, (90, 220, 255), 'EXIT ^ Radnice')
box(750, 470, 80, 200, (90, 220, 255), 'EXIT -> Screaming Cork')
box(610, 545, 46, 22, (255, 210, 60), 'mriz (Torchere)', canvas=True)
box(533, 470, 60, 30, (255, 160, 60), 'ohniste', canvas=True)
d.rectangle([250 - 30, 525 - 150, 250 + 30, 525], outline=(255, 120, 200)); d.text((222, 360), 'ORTOLAN (den 2)', fill=(255, 120, 200), font=F)
for x in range(0, W, 8): d.line([(x, 534), (x + 4, 534)], fill=(255, 80, 80))
d.text((4, 536), 'cara nohou y534 (hrac 128px)', fill=(255, 80, 80), font=F)
for x in range(0, W, 8): d.line([(x, 296), (x + 4, 296)], fill=(200, 200, 90))
d.text((4, 284), 'horizont / ubezny bod (533,296)', fill=(200, 200, 90), font=F)
g.save(f'{OUT}/guides.png')
