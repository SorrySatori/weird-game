"""The people of the Floors of Shed 521 (Shed521FloorsScene) as animated sprites instead of figures baked into the
background (floors_bg.py draws only empty benches now). Drawn with shedkit.applicant_img -- the same applicants as the
rest of the bureau -- at the size the floors' long lens gives them; 128 px wide frames, feet (or the seat) on the
bottom row, shown at scale 1 with origin bottom-centre.
  welcome_clerk  the gas-masked clerk behind the WELCOME counter, stamping forms
  dozer          an applicant dozing on the ground-floor bench: the head sinks, then jerks up
  queue0..3      the queue at APPLICATIONS on the top floor, facing the door (left): one leans towards the door,
                 one leafs through his papers, one sways, the last one now and then glances at the viewer
Whatever of the floors stands in front of a figure (the counter, the bench seat, the top floor's slab edge and
railing) is cut out of its frames using the background's depth buffer, so the sprite sits behind it as the baked
figures did. Each frame has a hold time (ms); the scene repeats frames to hold them (Phaser ignores per-frame durations).
python3 floorsfolk.py <outdir>  ->  <id>.png (sheet) + <id>/<n>.png + <id>/durations.txt + floorsfolk.gpl,
prints each figure's canvas anchor (the sprite's x, y with origin bottom-centre) and height (top) for the scene"""
import sys, os
from PIL import Image
import floors_bg                                      # the floors' geometry and camera (it only renders as a script)
from floors_bg import F, FLOORS, ZW, cx, W0
from shedkit import applicant_img, proj

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
ZB = floors_bg.rs.ZB                                  # the depth of the nearest surface per canvas pixel

QUEUE_SHIFT = 1.2                                     # the queue stands a step further from the door than it used to,
                                                      # clear of the APPLICATIONS door hotspot
# id: (X, Y0, Z, standing height h, base kwargs, frames [(pose kwargs, hold ms)])
CAST = {
    'welcome_clerk': (W0 + 5.6, 0.0, ZW - 1.0, 6.4, dict(seed=590, kind='mask', view='front', papers=False, stamp=True), [
        (dict(hands=((23, 45), (57, 39))), 1100),
        (dict(hands=((23, 45), (57, 39)), bob=0.9), 900),
        (dict(hands=((23, 45), (57, 30)), bob=0.4), 200),
        (dict(hands=((23, 45), (58, 23)), bob=-0.4), 300),
        (dict(hands=((23, 45), (57, 39)), bob=1.0), 160),
        (dict(hands=((23, 45), (57, 39)), bob=0.4), 700),
        (dict(hands=((27, 45), (57, 39)), lean=0.9), 600),
        (dict(hands=((23, 45), (57, 39)), bob=0.9), 900)]),
    'dozer': (cx(370) - 1.2, 0.9, ZW - 1.0, 6.4, dict(seed=503, kind='coral', view='front', seated=True), [
        (dict(), 1200), (dict(bob=0.8, nod=1.0), 1000), (dict(bob=1.0, nod=2.2), 1000), (dict(bob=1.2, nod=3.4), 1200),
        (dict(bob=1.2, nod=4.4), 1800), (dict(bob=-0.6, nod=-0.8), 300), (dict(bob=0.3), 1500)]),
    'queue0': (cx(533) + 2.2 + QUEUE_SHIFT, FLOORS[2], ZW - 1.2, 6.2, dict(seed=540, view='left'), [
        (dict(), 900), (dict(lean=0.8, bob=0.5), 700), (dict(lean=1.6, bob=0.9), 1100), (dict(lean=0.8, bob=0.5), 700),
        (dict(), 800), (dict(lean=-0.8), 1000)]),
    'queue1': (cx(533) + 3.9 + QUEUE_SHIFT, FLOORS[2], ZW - 1.7, 6.2, dict(seed=541, view='left', papers=True), [
        (dict(), 1000), (dict(page=(0.0, 0.0, 2.0)), 200), (dict(page=(0.0, 0.0, 4.0), bob=0.5), 240),
        (dict(page=(0.6, -0.8, 1.5), bob=0.9), 240), (dict(bob=0.5), 1000), (dict(), 1200)]),
    'queue2': (cx(533) + 5.5 + QUEUE_SHIFT, FLOORS[2], ZW - 1.2, 6.2, dict(seed=542, view='left'), [
        (dict(), 1000), (dict(bob=0.6, lean=-0.4), 1000), (dict(bob=1.0, lean=-0.9), 1000), (dict(bob=0.6, lean=-1.2), 1000),
        (dict(bob=0.3, lean=-0.6), 1000), (dict(), 1000)]),
    'queue3': (cx(533) + 7.2 + QUEUE_SHIFT, FLOORS[2], ZW - 1.7, 6.2, dict(seed=543, view='left'), [
        (dict(), 1000), (dict(bob=0.6), 1000), (dict(bob=1.0), 1000), (dict(bob=0.6), 1000),
        (dict(face='front', bob=0.3), 1700), (dict(bob=0.3), 800)]),
}
FW = 128

if __name__ == '__main__':
    pal = set()
    for name, (X, Y0, Z, h, base, frames) in CAST.items():
        seated = base.get('seated', False)
        hpx = F * h * (0.72 if seated else 1.0) / Z
        imgs = [applicant_img(hpx=hpx, **base, **pose) for pose, _ in frames]
        bottom = max(im.getbbox()[3] for im in imgs)                                         # the feet / seat row (+1)
        FH = 128 if not seated else 80
        (sx, sy) = proj(X, Y0, Z)
        feet = int(round(sy))                                                                # canvas row of the feet
        os.makedirs(f'{OUT}/{name}', exist_ok=True)
        sheet = Image.new('RGBA', (FW * len(imgs), FH), (0, 0, 0, 0))
        x0, y0 = int(round(sx)) - FW // 2, feet + 1 - FH                                    # the frame's top-left on the canvas
        for i, im in enumerate(imgs):
            fr = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
            fr.paste(im, ((FW - im.size[0]) // 2, FH - bottom), im)
            px = fr.load()
            for y in range(FH):                                                              # behind whatever is nearer
                for x in range(FW):
                    z = ZB[y0 + y][x0 + x] if 0 <= y0 + y < len(ZB) and 0 <= x0 + x < len(ZB[0]) else None
                    if px[x, y][3] and z is not None and z < Z - 0.05: px[x, y] = (0, 0, 0, 0)
            fr.save(f'{OUT}/{name}/{i}.png'); sheet.paste(fr, (i * FW, 0))
            pal.update(c[:3] for _, c in fr.getcolors(1 << 16) if c[3])
        sheet.save(f'{OUT}/{name}.png')
        open(f'{OUT}/{name}/durations.txt', 'w').write(' '.join(str(d) for _, d in frames) + '\n')
        top = FH - min(Image.open(f'{OUT}/{name}/{i}.png').getbbox()[1] for i in range(len(imgs)))
        print(f'{name:14s} {FW}x{FH} x{len(imgs)}  anchor x {int(round(sx))} y {feet + 1}  top {top}  holds {[d for _, d in frames]}')
    rows = ['%3d %3d %3d\t#%02x%02x%02x' % (c + c) for c in sorted(pal)]
    open(f'{OUT}/floorsfolk.gpl', 'w').write('GIMP Palette\nName: floorsfolk\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    print('ok', OUT, len(rows), 'colours')
