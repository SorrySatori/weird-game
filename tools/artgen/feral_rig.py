"""Feral Toast -- the Screaming Cork Club band (ScreamingCorkClubScene; the ScraperAmbra cutscene shows frames 4-11)
drawn for real with the character renderer (rig.py, the Edgar quality bar). Supersedes feral_px.py (the old AI pictures
box-filtered and animated) and the first rig version feral_toast.py (whose ik/lerp/worm helpers other generators still
import, so that file stays). The designs follow the old pictures in tools/artgen/ref/feral_*.png -- read, not traced:
  telka    the tentacle-faced guitarist: an olive octopoid head (seven crown tentacles with curled tips, big yellow eyes,
           a beard of hanging tentacles), a worn black leather jacket with studs, shoulder spikes and a rust patch, black
           jeans ripped at the knee (green hide shows), combat boots; a guitar whose body is a fanged creature's head
  bass_xl  Bass Player XL: a heavy, worn slate-steel robot -- a domed helmet with a black visor and two square yellow
           eyes, pauldrons, a plated chest, ribbed joints, knee caps, big feet; a cream P-bass with a black guard
  karlis   Fluffy Karlis: a heavy brown bear seated behind his kit -- a long muzzle with a broad dark nose, brow ridges
           over small deep-set eyes, small round ears set back, a thick neck into sloped shoulders, a barrel body, shaggy
           top-lit fur, big paws round the sticks (idle: the right paw holds a stick up, ready, as in the old picture) --
           in an old leather vest over a black band tee; a crash on a boom stand, two toms, a hi-hat with its pedal and
           a kick drum whose worn head carries the band's sign -- a fanged slice of toast
  mira     Mira Dron: a deep green hood (a black void with two yellow eyes), a fringed sand-coloured scarf, long pale
           green fingers on an eldritch synth -- a mossy stone console with glowing runes, a medallion with a horned
           golden skull on its front, vines curling up at its sides (one ends in a bud)
Sheets like before (the scene and the demo only swap PNGs): 12 frames of 128x192 (karlis 144x192), soles on row 189;
  0-3   idle: 0 rest, 1 breath in, 2 looking about (held), 3 blink
  4-11  playing = 4 beats of feral-toast.mp3 (~177 BPM) x 2 frames (the down-beat frame 4/6/8/10, then the after-beat):
        knees give on every beat, headbangs on 1 and 3, the picking hand strums down/up; Karlis: the raised stick drops
        onto the crash on 1 (it wobbles), kick on 1 and 3, the left paw on the hi-hat on 2 and 4 (it closes), toms on 3
        and 4 (the paw winds up again); Mira: the hands alternate on the keys, light runs through the runes, the
        skull's eyes flash on 1 and 3, the vines sway.
Instrument rules (the user's): the fretting hand wraps the neck from BEHIND (palm under the neck, the thumb tip over
its top edge, the fingers curl onto the fretboard from below), the elbow hangs down, the neck is steep (~42 deg) and
the hand sits near the headstock; the picking hand strums over the strings.
python3 feral_rig.py <outdir> [ids]  ->  <id>.png sheets + <id>/<n>.png frames + feral_toast.gpl"""
import sys, os, math
from PIL import Image, ImageDraw
from common import ramp, INK, make_noise, h32
import rig
from rig import Rig, Mat, norm
from feral_toast import ik, lerp, Inst
from symbionts import curve
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
W, H, SOLE = 128, 192, 189
R = ramp
nA, nB, nC = make_noise(3, 911, 200, 220), make_noise(6, 912, 200, 220), make_noise(11, 913, 200, 220)


def mix(a, b, t): return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


# ---------------------------------------------------------------------------------------------------- textures
rig.TEX['hide'] = lambda x, y: ((nA(x * 1.3, y * 1.3) - 0.5) * 0.16 + (nB(x, y) - 0.5) * 0.14
                                - (0.13 if h32(x, y, 71) % 19 == 0 else 0))                   # mottled, pitted
rig.TEX['oldleather'] = lambda x, y: ((nA(x * 1.4, y * 1.4) - 0.5) * 0.10 + (nB(x * 0.9, y * 0.9) - 0.5) * 0.16
                                      + (nC(x + 30, y) - 0.5) * 0.14 + (0.06 if h32(x, y, 72) % 31 == 0 else 0))
rig.TEX['blackjeans'] = lambda x, y: ((nA(x * 1.6, y * 1.6) - 0.5) * 0.08 - (0.05 if (x - y) % 3 == 0 else 0)
                                      + (nC(x * 0.6, y * 0.6 + 50) - 0.5) * 0.18)            # faded patches
rig.TEX['grime'] = lambda x, y: ((nA(x * 1.2, y * 1.2) - 0.5) * 0.08 + (nC(x * 0.8 + 70, y * 0.8) - 0.5) * 0.22
                                 + (-0.08 if h32(x, y, 73) % 13 == 0 else 0))                # worn steel, smudged
def _bearfur(x, y):
    """shaggy fur: clumps (lit tops, dark partings between them) and hanging strands"""
    c = nB(x * 0.9 + 1.4 * math.sin(y * 0.35), y * 0.55)                                  # clumps
    v = (c - 0.5) * 0.26
    if 0.48 < c < 0.52: v -= 0.16                                                          # a parting between clumps
    v += (nA(x * 1.1 + 2.0 * math.sin(y * 0.4), y * 0.3) - 0.5) * 0.16                      # strands
    k = (x * 7 + (y // 3) * 13) % 11
    return v + (-0.12 if k == 0 else 0.08 if k == 5 else 0) + (nC(x, y) - 0.5) * 0.08
rig.TEX['bearfur'] = _bearfur
rig.TEX['knit'] = lambda x, y: ((nA(x * 2.0, y * 2.0) - 0.5) * 0.10 + (0.05 if (x // 2 + y) % 2 else -0.04)
                                + (nC(x, y + 20) - 0.5) * 0.12)
rig.TEX['stone'] = lambda x, y: ((nA(x * 1.5, y * 1.5) - 0.5) * 0.14 + (nB(x * 1.1 + 9, y * 1.1) - 0.5) * 0.16
                                 + (nC(x, y) - 0.5) * 0.14 + (-0.1 if h32(x, y, 74) % 17 == 0 else 0))
rig.TEX['worn'] = lambda x, y: (nA(x * 1.4, y * 1.4) - 0.5) * 0.12 + (nC(x * 0.7, y * 0.7 + 10) - 0.5) * 0.2

# ---------------------------------------------------------------------------------------------------- palette
HIDE   = R('#121709 #1b220e #252e13 #303b18 #3c491d #495823 #57672a #677832 #79893c #8c9a48 #a2ad5c')  # Telka
JACK   = R('#080807 #0d0e0b #131410 #191b15 #20221b #282a21 #313329 #3b3d32 #46493c #545748')                # old black leather
JEANS  = R('#0a0909 #100f0e #161514 #1d1b1a #252221 #2d2a28 #363230 #403b38')
BOOTS  = R('#070606 #0c0a0a #12100f #191615 #201c1a #282320 #312b27 #3c342f')
TEE    = R('#0e0e0f #151516 #1d1d1f #262628 #303033')
GUIT   = R('#0e1209 #151b0c #1d2510 #263015 #303c1a #3b481f #475625 #55652c #657534 #788640')
FANG   = R('#4a4330 #6a6045 #8a7f5d #a99d77 #c3b891 #d6cdaa')
EYERED = R('#2a0906 #48120b #6b1f12 #8e301b #ab4526 #c25f36')
NECKW  = R('#1e1009 #2d180d #3e2212 #512d18 #643a1f #784828 #8b5832 #9d6a3f')
BOARDW = R('#120a07 #1b100b #24160f #2d1c13')
STEEL  = R('#15171a #212429 #2e3238 #3d4249 #4e545b #61676e #767c82 #8d9297 #a7abaf #c3c6c8')
RUSTP  = R('#26100a #3b1a0f #522415 #6a301b #7f3d22 #924b2b')                                     # the rust patch
EYEY   = R('#3f3608 #6e5f12 #a08c22 #c9b23a #e2cd5c #f1e38e')                                     # Telka's eyes
EYE_OPEN = [' sssss ',
            'slhhyls',
            'lhgyyyd',
            'lhyppyd',
            'oyyppdo',
            'odyppdo',
            ' ooddo ',
            '  sss  ']
EYE_BLINK = [' sssss ',
             'sllllls',
             'lLLLLLl',
             'lLLLLLl',
             'oKKKKKo',
             'odLLLdo',
             ' ooooo ',
             '  sss  ']
EYEC = {'l': HIDE[1], 'o': HIDE[1], 'h': EYEY[5], 'g': (252, 246, 210), 'y': EYEY[4], 'd': EYEY[2], 'p': (12, 10, 4),
        'L': HIDE[5], 'K': HIDE[0], ' ': None}
WARMOUT = (22, 16, 12)
GREENOUT = (14, 18, 8)

def mat(rmp, tex, amb, spec=0.0, out=WARMOUT): return Mat(rmp, tex, amb, spec, outline=out)
M = {'hide': mat(HIDE, 'hide', 0.2, 0.25, GREENOUT), 'jack': mat(JACK, 'oldleather', 0.2, 0.55), 'jeans': mat(JEANS, 'blackjeans', 0.2),
     'boots': mat(BOOTS, 'oldleather', 0.2, 0.6), 'tee': mat(TEE, 'knit', 0.2), 'guit': mat(GUIT, 'hide', 0.2, 0.45, GREENOUT),
     'fang': mat(FANG, 'plain', 0.3, 0.3), 'neckw': mat(NECKW, 'wood', 0.25, 0.3), 'board': mat(BOARDW, 'wood', 0.3),
     'steel': mat(STEEL, 'metal', 0.2, 0.8), 'rustp': mat(RUSTP, 'knit', 0.22)}


# ---------------------------------------------------------------------------------------------------- helpers
def tentacle(r, pts, r0, r1, mat, group, lift=0.0, suck=None):
    """a tapering tentacle along pts; suck = colour of the suckers dotted along its underside"""
    n = len(pts) - 1
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        r.tube(a, b, r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n, mat, lift=lift, group=group)
    if suck:
        for i in range(2, n - 1, 3):
            (ax, ay), (bx, by) = pts[i], pts[i + 1]
            dx, dy = bx - ax, by - ay; L = math.hypot(dx, dy) or 1
            rr = r0 + (r1 - r0) * i / n
            if rr < 1.3: continue
            r.fixed(ax - dy / L * rr * 0.6, ay + dx / L * rr * 0.6, suck)


def hook(x0, y0, ang, L, curl, sway=0.0, n=14):
    """points of a limb that leaves (x0, y0) at angle ang and rolls its tip over by `curl` radians"""
    pts, x, y, a = [], x0, y0, ang
    step = L / n
    for i in range(n + 1):
        pts.append((x, y))
        t = i / n
        a += (curl * 5 * t ** 4 / n) + sway / n
        x += math.cos(a) * step; y += math.sin(a) * step
    return pts


def poly_mask(pts, ox=0, oy=0):
    """the pixels inside a polygon"""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, y0 = int(min(xs)) - 1, int(min(ys)) - 1
    w, h = int(max(xs)) - x0 + 3, int(max(ys)) - y0 + 3
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in pts], fill=255)
    px = m.load()
    return {(x + x0, y + y0) for y in range(h) for x in range(w) if px[x, y]}


def path_mask(path, radii, step=0.35):
    """a limb / strand as a union of discs along a polyline with a radius per vertex"""
    S = set()
    for i in range(len(path) - 1):
        (ax, ay), (bx, by) = path[i], path[i + 1]
        L = math.hypot(bx - ax, by - ay); n = max(1, int(L / step))
        for k in range(n + 1):
            t = k / n
            x, y, rr = ax + (bx - ax) * t, ay + (by - ay) * t, radii[i] + (radii[i + 1] - radii[i]) * t
            for yy in range(int(y - rr) - 1, int(y + rr) + 2):
                for xx in range(int(x - rr) - 1, int(x + rr) + 2):
                    if (xx + 0.5 - x) ** 2 + (yy + 0.5 - y) ** 2 <= rr * rr: S.add((xx, yy))
    return S


def ellipse_mask(cx, cy, rx, ry, rot=0.0):
    c, s = math.cos(rot), math.sin(rot); R = max(rx, ry) + 1
    out = set()
    for y in range(int(cy - R) - 1, int(cy + R) + 2):
        for x in range(int(cx - R) - 1, int(cx + R) + 2):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            u, w = (dx * c + dy * s) / rx, (-dx * s + dy * c) / ry
            if u * u + w * w <= 1: out.add((x, y))
    return out


def region(r, mask, mat, D=5.0, bulge=1.0, lift=0.0, group=None, vfun=None, tilt=(0.0, 0.0), clip=None):
    """shade an arbitrary pixel set as a soft volume: a rounded rim D px wide around a flatter middle (the normal comes
    from the distance to the region's edge), so cloth and flesh get believable form without tube rings"""
    mask = {p for p in mask if 0 <= p[0] < r.w and 0 <= p[1] < r.h and (clip is None or clip(*p))}
    if not mask: return None
    oid = r.new(group)
    INF = 1e9
    xs, ys = [p[0] for p in mask], [p[1] for p in mask]
    x0, x1, y0, y1 = min(xs) - 1, max(xs) + 1, min(ys) - 1, max(ys) + 1
    d = {}
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d[(x, y)] = INF if (x, y) in mask else 0.0
    for y in range(y0 + 1, y1 + 1):                                                    # two-pass chamfer distance
        for x in range(x0 + 1, x1 + 1):
            if d[(x, y)]:
                d[(x, y)] = min(d[(x, y)], d[(x - 1, y)] + 1, d[(x, y - 1)] + 1, d[(x - 1, y - 1)] + 1.414,
                                d.get((x + 1, y - 1), 0) + 1.414)
    for y in range(y1 - 1, y0 - 1, -1):
        for x in range(x1 - 1, x0 - 1, -1):
            if d[(x, y)]:
                d[(x, y)] = min(d[(x, y)], d[(x + 1, y)] + 1, d[(x, y + 1)] + 1, d[(x + 1, y + 1)] + 1.414,
                                d.get((x - 1, y + 1), 0) + 1.414)
    for (x, y) in mask:
        gx = d.get((x + 1, y), 0) - d.get((x - 1, y), 0)
        gy = d.get((x, y + 1), 0) - d.get((x, y - 1), 0)
        gl = math.hypot(gx, gy) or 1.0
        t = min(d[(x, y)] - 0.5, D) / D
        s = max(0.0, min(0.97, (1 - t) * bulge))
        n = norm((-gx / gl * s + tilt[0], -gy / gl * s + tilt[1], math.sqrt(1 - s * s)))
        v = r.shade(mat, n, lift) + (vfun(x, y) if vfun else 0)
        r.put(x, y, mat, v, oid)
    return oid


def fold(r, pts, group=None, dark=0.26, light=0.12, step=0.5):
    """a cloth fold along a polyline: a dark crease with a lit ridge on its upper-left side"""
    done = set()
    for i in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        L = math.hypot(bx - ax, by - ay); n = max(1, int(L / step))
        nx, ny = -(by - ay) / (L or 1), (bx - ax) / (L or 1)
        if nx * -0.6 + ny * -0.8 < 0: nx, ny = -nx, -ny                                  # (nx, ny) toward the light
        for k in range(n + 1):
            t = k / n
            x, y = ax + (bx - ax) * t, ay + (by - ay) * t
            taper = math.sin(math.pi * (i + t) / (len(pts) - 1)) ** 0.6
            for (px, py, dv) in ((x, y, dark * taper), (x + nx * 1.1, y + ny * 1.1, -light * taper)):
                q = (int(px), int(py))
                if q in done: continue
                e = r.buf.get(q)
                if e and e[0] is not None and (group is None or r.groups[e[2]] == group):
                    e[1] -= dv; done.add(q)


def recolor_outline(im, old, new):
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y] == old + (255,): px[x, y] = new + (255,)
    return im


# ============================================================================================================ Telka
def _tp(**k):
    d = dict(bob=0, hd=0, hx=0, strum=0, fret=0, knee=0, ph=0.0, fling=0.0, blink=False, look=0, breath=0)
    d.update(k); return d

TELKA_IDLE = [_tp(), _tp(breath=1, ph=0.8), _tp(breath=1, ph=1.6, look=1, hx=1), _tp(ph=2.4, blink=True)]
TELKA_PLAY = [  # beat 1: headbang down, knees give, strum down / up ... beat 3 the same, the chord changes on 3
    _tp(bob=2, hd=4, strum=4, knee=2, ph=3.0, fling=-1.0), _tp(bob=1, hd=1, strum=-3, knee=1, ph=3.6, fling=0.8),
    _tp(bob=1, hd=0, strum=4, knee=1, ph=4.2, fling=0.3), _tp(bob=0, hd=0, strum=-3, knee=0, ph=4.8, fling=0.0),
    _tp(bob=2, hd=4, strum=4, knee=2, ph=5.4, fling=-1.0, fret=1), _tp(bob=1, hd=1, strum=-3, knee=1, ph=6.0, fling=0.8, fret=1),
    _tp(bob=1, hd=0, strum=4, knee=1, ph=6.6, fling=0.3, fret=1), _tp(bob=0, hd=0, strum=-3, knee=0, ph=7.2, fling=0.0)]


def boot(r, ax, sx, group, sole=SOLE):
    """a heavy laced combat boot; ax = the ankle's x, sx = the way the toe points"""
    m = M['boots']
    shaft = poly_mask([(ax - 6, sole - 17), (ax + 6, sole - 17), (ax + 6.5 + sx * 1, sole - 6), (ax - 6.5 + sx * 1, sole - 6)])
    foot = poly_mask([(ax - sx * 7, sole - 9), (ax + sx * 6, sole - 9), (ax + sx * 12, sole - 6), (ax + sx * 14.5, sole - 3),
                      (ax + sx * 14, sole - 1), (ax - sx * 7.5, sole - 1)])
    region(r, shaft | foot, m, D=4.0, group=group, vfun=lambda x, y: (-0.18 if (y - sole) % 3 == 0 and abs(x - ax) < 6 and y < sole - 9 else 0))
    for x in range(int(ax - 9), int(ax + 16) + 1):                                     # the sole
        xx = ax + (x - ax) * sx
        q = (int(xx), sole - 2)
        if q in r.buf:
            r.fixed(q[0], sole, (26, 22, 20)); r.fixed(q[0], sole - 1, (48, 42, 38) if x % 4 else (36, 31, 28))
    for y in range(sole - 16, sole - 8, 2):                                            # laces up the front
        lx = ax + sx * 3
        r.fixed(lx, y, BOOTS[6]); r.fixed(lx + sx, y, BOOTS[4]); r.fixed(lx - sx, y + 1, BOOTS[0])
    r.fixed(ax + sx * 11, sole - 6, BOOTS[7]); r.fixed(ax + sx * 12, sole - 5, BOOTS[6])   # the toe cap's shine
    fold(r, [(ax - sx * 5, sole - 8), (ax + sx * 2, sole - 7), (ax + sx * 7, sole - 6)], group, 0.2, 0.08)


def telka(P):
    r = Rig(W, H)
    bob, hd, br, kn = P['bob'], P['hd'], P['breath'], P['knee']
    T = lambda y: y + bob - (br if y < 104 else 0)
    # ---------------------------------------------------------------- legs (a wide rocker stance, weight on the left)
    hipL, hipR = (48, 121 + bob), (68, 120 + bob)
    kneeL, kneeR = (36 - kn * 0.6, 147 + bob * 0.8), (83 + kn * 0.6, 143 + bob * 0.8)
    ankL, ankR = (35, 174), (90, 174)
    for hip, knee, ank, g in ((hipL, kneeL, ankL, 'legL'), (hipR, kneeR, ankR, 'legR')):
        region(r, path_mask([hip, knee, ank], [10.0, 7.8, 6.6]), M['jeans'], D=5.0, group=g)
    fold(r, [(kneeL[0] - 6, kneeL[1] - 4), (kneeL[0] - 1, kneeL[1] - 2), (kneeL[0] + 5, kneeL[1] - 5)], 'legL')
    fold(r, [(kneeL[0] - 5, kneeL[1] + 3), (kneeL[0] + 1, kneeL[1] + 4), (kneeL[0] + 6, kneeL[1] + 1)], 'legL', 0.2)
    fold(r, [(hipL[0] - 7, hipL[1] + 10), (hipL[0] - 2, hipL[1] + 15), (hipL[0] + 3, hipL[1] + 13)], 'legL', 0.2)
    fold(r, [(ankL[0] - 6, ankL[1] - 5), (ankL[0], ankL[1] - 3), (ankL[0] + 6, ankL[1] - 5)], 'legL', 0.24)
    fold(r, [(kneeR[0] - 8, kneeR[1] - 8), (kneeR[0] - 3, kneeR[1] - 3), (kneeR[0] - 4, kneeR[1] + 4)], 'legR')
    fold(r, [(kneeR[0] + 1, kneeR[1] + 6), (kneeR[0] + 5, kneeR[1] + 9), (kneeR[0] + 7, kneeR[1] + 6)], 'legR', 0.2)
    fold(r, [(ankR[0] - 6, ankR[1] - 6), (ankR[0], ankR[1] - 3), (ankR[0] + 6, ankR[1] - 6)], 'legR', 0.24)
    kx, ky = int(kneeR[0]) + 1, int(kneeR[1])                                              # the rip: green hide
    rip = {(-2, -2), (-1, -2), (0, -2), (-3, -1), (-2, -1), (-1, -1), (0, -1), (1, -1), (-3, 0), (-2, 0), (-1, 0), (0, 0), (1, 0),
           (2, 0), (-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1), (-1, 2), (0, 2), (1, 2)}
    for (dx, dy) in rip:
        r.fixed(kx + dx, ky + dy, HIDE[6 - (1 if dy > 0 else 0) - (1 if dx > 0 else 0) + (1 if dx + dy < -2 else 0)])
    for (dx, dy) in ((-3, -3), (-1, -3), (1, -2), (3, 1), (2, 3), (0, 3), (-2, 2), (-4, 0)):
        r.fixed(kx + dx, ky + dy, JEANS[7] if dy < 0 else JEANS[6])                        # frayed threads
    boot(r, ankL[0], -1, 'bootL'); boot(r, ankR[0], 1, 'bootR')
    # ---------------------------------------------------------------- the jacket's body (a tee under the open front)
    region(r, poly_mask([(52, T(64)), (74, T(64)), (75, T(122)), (51, T(122))]), M['tee'], D=6, group='tee')
    for (x, y) in ((60, 98), (61, 97), (62, 97), (63, 97), (64, 98), (62, 99), (62, 100), (61, 102), (63, 102)):
        r.fixed(x, T(y), (88, 84, 74))                                                     # a scratchy print on the tee
    jl = region(r, poly_mask([(31, T(75)), (42, T(68)), (54, T(64)), (58, T(66)), (57, T(92)), (56, T(126)), (42, T(128)),
                              (38, T(118)), (36, T(98))]), M['jack'], D=6, group='jackL')
    jr = region(r, poly_mask([(69, T(66)), (73, T(64)), (83, T(67)), (92, T(75)), (90, T(98)), (85, T(118)), (81, T(127)),
                              (69, T(125)), (69, T(92))]), M['jack'], D=6, group='jackR')
    seam(r, 'jackR', 0.18)
    for pts, gname in (([(40, T(86)), (45, T(92)), (51, T(95))], 'jackL'), ([(38, T(103)), (44, T(108)), (52, T(110))], 'jackL'),
                       ([(42, T(119)), (48, T(121)), (55, T(119))], 'jackL'), ([(87, T(87)), (81, T(94)), (74, T(97))], 'jackR'),
                       ([(87, T(104)), (80, T(109)), (73, T(110))], 'jackR'), ([(82, T(120)), (76, T(122)), (70, T(121))], 'jackR')):
        fold(r, pts, gname, 0.24, 0.14)
    region(r, poly_mask([(50, T(63)), (57, T(67)), (59, T(86)), (56, T(99)), (52, T(86))]), M['jack'], D=2.5, lift=0.12, group='lapL')
    region(r, poly_mask([(69, T(67)), (76, T(63)), (74, T(86)), (70, T(99)), (67, T(86))]), M['jack'], D=2.5, lift=0.06, group='lapR')
    seam(r, 'lapL', 0.26); seam(r, 'lapR', 0.26)
    for (x, y) in ((53, 71), (54, 76), (55, 81), (56, 86), (73, 71), (72, 76), (71, 81), (70, 86), (39, 108), (39, 113),
                   (87, 104), (86, 109), (44, 72), (48, 70), (80, 70), (84, 72)):
        r.fixed(x, T(y), STEEL[8]); r.fixed(x + 1, T(y) + 1, STEEL[2]); r.fixed(x, T(y) + 1, STEEL[4])   # studs
    for y in range(int(T(100)), int(T(124)), 2): r.fixed(57, y, STEEL[5]); r.fixed(69, y, STEEL[4])   # open zips
    for (bx, by, c) in ((44, 87, FANG), (48, 97, RUSTP), (79, 89, EYERED), (43, 96, STEEL)):          # pin badges
        y0 = T(by)
        r.fixed(bx, y0, c[-2]); r.fixed(bx + 1, y0, c[-3]); r.fixed(bx, y0 + 1, c[-4]); r.fixed(bx + 1, y0 + 1, c[-5])
        r.darken(bx + 2, y0 + 1, 0.2); r.darken(bx + 1, y0 + 2, 0.2)
    # ---------------------------------------------------------------- the fretting arm (behind the neck)
    g = Inst((45, 130 + bob), math.radians(-43))
    uf = 71 + 4 * P['fret']                                                               # near the headstock
    shR = (86, T(78))
    palm = g.P(uf, 5.4)
    E = ik(shR, palm, 22, 22, 'down')                                                     # the elbow hangs
    wr = g.P(uf - 1.5, 8.5)
    region(r, path_mask([shR, E, wr], [8.0, 6.6, 5.0]), M['jack'], D=5.0, group='armF')
    fold(r, [(E[0] - 5, E[1] - 3), (E[0] - 1, E[1] - 1), (E[0] + 2, E[1] - 4)], 'armF', 0.3, 0.14)
    fold(r, [(shR[0] - 2, shR[1] + 8), (shR[0] + 3, shR[1] + 10)], 'armF', 0.22, 0.1)
    region(r, ellipse_mask(*g.P(uf, 5.4), 4.4, 3.4, g.ang), M['hide'], D=2.5, group='palmF')   # the palm under the neck
    th = g.P(uf + 2.3, -3.4)
    region(r, ellipse_mask(th[0], th[1], 1.9, 1.6), M['hide'], D=1.5, lift=0.1, group='thumbF')   # the thumb tip on top
    # ---------------------------------------------------------------- the head
    hx, hy = 63 + P['hx'], 51 + bob + hd - br
    fl = P['fling']
    # the beard's dark mass first (the gaps between the strands read dark)
    region(r, ellipse_mask(hx, hy + 16, 10.0, 10.0), M['hide'], D=3, lift=-0.6, group='beardback')
    # the beard: separate hanging tentacles, the middle ones longest, the tips curling out
    beard = [(-10.5, 15), (-7.5, 21), (-4.5, 26), (-1.5, 30), (1.5, 30), (4.5, 26), (7.5, 21), (10.5, 15)]
    for i in (0, 7, 1, 6, 2, 5, 3, 4):
        dx, L = beard[i]
        sd = -1 if dx < 0 else 1
        sw = math.sin(P['ph'] * 1.3 + i * 0.9) * 0.3 + fl * 0.12 * sd
        x0, y0 = hx + dx * 0.9, hy + 6 + abs(dx) * 0.15
        pts = hook(x0, y0, math.radians(90 - dx * 1.5), L - fl * 1.5, -sd * 1.3, sway=sw, n=12)
        radii = [2.3 if k < 7 else max(0.7, 2.3 - (k - 6) * 0.3) for k in range(13)]
        region(r, path_mask(pts, radii), M['hide'], D=2.2, lift=0.04 - 0.08 * (i % 2), group='beard%d' % i)
        for k in (4, 7, 10):
            r.fixed(pts[k][0] - 0.8 * sd, pts[k][1], HIDE[8] if k < 9 else HIDE[7])       # suckers catch the light
    # the mantle grows into the crown: the tentacles share the head's shading (one group, no seams)
    crown = [(-166, 20, -1.7, 3.6), (-138, 28, 1.5, 4.0), (-108, 35, -1.3, 4.4), (-80, 33, 1.4, 4.4), (-50, 27, -1.6, 4.0),
             (-18, 19, 1.6, 3.4)]
    for i, (a, L, curl, r0) in enumerate(crown):
        ang = math.radians(a)
        sw = math.sin(P['ph'] + i * 1.1) * 0.3 + fl * 0.35 * math.cos(ang)
        base = (hx + math.cos(ang) * 4.0, hy - 5 + math.sin(ang) * 4.0)
        pts = hook(base[0], base[1], ang, L - fl * 2, curl, sway=sw, n=16)
        radii = [max(0.7, r0 * (1 - k / 16) ** 1.6 + 0.6) for k in range(17)]
        region(r, path_mask(pts, radii), M['hide'], D=2.6, group='head',
               vfun=lambda x, y: -0.05 if (x + y) % 5 == 0 else 0)
    head = ellipse_mask(hx, hy - 6, 9.5, 9.5) | ellipse_mask(hx, hy + 2.0, 15.0, 8.5) | ellipse_mask(hx, hy + 6.5, 11.5, 4.5)
    region(r, head, M['hide'], D=8.0, group='head', vfun=lambda x, y: (-0.07 if (x * 5 + y * 3) % 13 == 0 else 0))
    for sx in (-1, 1):                                                                    # bulging brow ridges
        region(r, ellipse_mask(hx + sx * 7.6, hy - 1.8, 5.8, 2.6, sx * -0.2), M['hide'], D=2.4, lift=0.08, group='brow%d' % sx)
    for sx in (-1, 1):                                                                    # eyes: big, pale yellow, slit pupils
        ex, ey = int(round(hx + sx * 7.6)) - 3, int(round(hy + 2.2)) - 3
        tpl = EYE_BLINK if P['blink'] else EYE_OPEN
        for j, row in enumerate(tpl):
            for i, ch in enumerate(row):
                if ch == ' ': continue
                if ch == 's': r.darken(ex + i, ey + j, 0.3); continue
                if ch == 'p' and P['look']: ch = 'y'
                r.fixed(ex + i, ey + j, EYEC[ch])
        if P['look'] and not P['blink']:
            for j in (2, 3, 4): r.fixed(ex + 4, ey + j, EYEC['p'])
    # ---------------------------------------------------------------- the creature guitar
    guitar_body(r, g, bob, P)
    neck(r, g, 23, 89, 13)
    fret_fingers(r, g, uf)
    # ---------------------------------------------------------------- the picking arm (in front), the spiked shoulder
    shL = (37, T(79))
    hand = g.P(13, -2.0 + P['strum'])
    EL = ik(shL, (hand[0] - 3, hand[1] + 1), 25, 30, 'left')
    region(r, path_mask([shL, EL, (hand[0] - 3.5, hand[1] + 1)], [8.4, 7.0, 5.4]), M['jack'], D=5.0, group='armS')
    fold(r, [(EL[0] + 2, EL[1] - 6), (EL[0] + 4, EL[1] - 1), (EL[0] + 1, EL[1] + 3)], 'armS', 0.3, 0.14)
    fold(r, [(EL[0] + 6, EL[1] + 2), (EL[0] + 9, EL[1] + 5)], 'armS', 0.22, 0.1)
    fold(r, [(shL[0] - 4, shL[1] + 14), (shL[0] + 1, shL[1] + 12)], 'armS', 0.2, 0.1)
    px0, py0 = int(shL[0]) - 8, int(shL[1]) + 2                                          # the rust patch, stitched on
    for y in range(py0, py0 + 9):
        for x in range(px0, px0 + 7):
            e = r.buf.get((x, y))
            if e and r.groups[e[2]] == 'armS':
                edge = x in (px0, px0 + 6) or y in (py0, py0 + 8)
                lit = 1 if x < px0 + 3 and y < py0 + 4 else 0
                c = RUSTP[2 + lit + (1 if h32(x, y, 5) % 5 == 0 else 0)] if not edge else (RUSTP[1] if (x + y) % 2 else RUSTP[4])
                r.fixed(x, y, c)
    for k, (dx, dy, a, L) in enumerate(((-11, 2, -168, 4), (-9, -3, -146, 5), (-5, -6, -124, 6), (-1, -8, -102, 5), (3, -8, -84, 4))):
        bx, by = shL[0] + dx, shL[1] + dy                                                 # conical spikes
        ang = math.radians(a)
        for t in range(L + 1):
            px, py = bx + math.cos(ang) * t, by + math.sin(ang) * t
            r.fixed(px, py, STEEL[7] if t < L - 1 else STEEL[9])
            if t < L - 2: r.fixed(px - math.sin(ang) * 0.9, py + math.cos(ang) * 0.9, STEEL[3])
    pick_hand(r, hand, P)
    im = r.render()
    return recolor_outline(im, (18, 14, 12), WARMOUT)


def guitar_body(r, g, bob, P):
    """the body is a creature's head facing left: two red eyes under a heavy brow, a fanged jaw along the lower edge,
    a red knob-eye on the upper horn, spines; the bridge and pickups sit between them"""
    cx, cy = g.O
    lobe = (cx - 3, cy + 3)                                                              # the head lobe
    horn = (cx + 10, cy - 11)
    scale = lambda x, y, u, w: ((-0.16 if (x * 3 + y * 2) % 9 == 0 and (x + y) % 2 else 0) + (-0.12 if w > 0.6 else 0)
                                + (nB(x * 2, y * 2) - 0.5) * 0.2)
    r.ellipsoid(horn[0], horn[1], 13.5, 9.0, M['guit'], rot=math.radians(-28), group='gbody', vfun=scale, flat=0.8)
    r.ellipsoid(lobe[0], lobe[1], 19.5, 15.5, M['guit'], rot=math.radians(-10), group='gbody', vfun=scale, flat=0.8)
    r.ellipsoid(lobe[0] - 9, lobe[1] - 7, 9.5, 6.0, M['guit'], lift=0.08, group='gbody', vfun=scale)     # the brow
    for (a, b, r0) in (((horn[0] + 10, horn[1] - 2), (horn[0] + 18, horn[1] - 8), 2.8),                  # spines
                       ((lobe[0] - 14, lobe[1] - 11), (lobe[0] - 19, lobe[1] - 18), 2.6),
                       ((lobe[0] - 6, lobe[1] - 13), (lobe[0] - 8, lobe[1] - 19), 2.0),
                       ((lobe[0] + 15, lobe[1] + 8), (lobe[0] + 21, lobe[1] + 11), 2.2)):
        r.tube(a, b, r0, 0.6, M['guit'], group='gbody')
    # the jaw: a wide maw from the snout (left) back to its corner, uneven interlocking fangs
    x0m, x1m = lobe[0] - 19, lobe[0] + 9
    for x in range(int(x0m), int(x1m) + 1):
        t = (x - x0m) / (x1m - x0m)
        top = lobe[1] + 1.0 + t * 4.0 + math.sin(t * 7) * 0.4
        hgt = 7.0 * (1 - t) ** 0.8 + 0.6
        bot = top + hgt
        for y in range(int(top), int(bot) + 1):
            if (x, y) in r.buf: r.fixed(x, y, (16, 10, 6) if y > top + 1 and y < bot - 1 else (40, 24, 14))
        r.darken(x, int(top) - 1, -0.12)                                                 # the lit upper lip
        r.darken(x, int(bot) + 1, 0.22)                                                  # the shadow under the jaw
        if t < 0.9:
            k = h32(int(x), 41) % 5
            if x % 3 == 0:                                                               # upper fangs hang down
                L = int(min(hgt - 1, 2 + k % 3 + (1 if t < 0.4 else 0)))
                for j in range(L): r.fixed(x, int(top) + j, FANG[5 - min(4, j + (1 if j else 0))])
                if L > 2: r.fixed(x + 1, int(top), FANG[2])
            elif x % 3 == 2 and hgt > 3:                                                 # lower fangs point up
                L = int(min(hgt - 2, 2 + k % 2))
                for j in range(L): r.fixed(x, int(bot) - j, FANG[3 - min(2, j)])
    for (ex, ey) in ((lobe[0] - 14, lobe[1] - 5), (lobe[0] - 8, lobe[1] - 6)):           # the creature's eyes
        for (dx, dy, k) in ((0, 0, 4), (1, 0, 3), (0, 1, 3), (1, 1, 2), (-1, 0, 2), (-1, 1, 1), (0, -1, 3), (1, -1, 2), (2, 0, 1), (2, 1, 1)):
            r.fixed(ex + dx, ey + dy, EYERED[k])
        r.fixed(ex, ey - 1, EYERED[5]); r.fixed(ex + 1, ey, (30, 8, 4)); r.fixed(ex + 1, ey + 1, (24, 6, 3))
        for dx in (-2, -1, 0, 1, 2, 3): r.darken(ex + dx, ey - 2, 0.3)                  # under the brow
    kx, ky = horn[0] - 3, horn[1] - 1                                                    # the knob-eye on the horn
    for y in range(ky - 2, ky + 3):
        for x in range(kx - 2, kx + 3):
            d = math.hypot(x - kx, y - ky)
            if d <= 2.4: r.fixed(x, y, EYERED[4] if d < 1.2 else EYERED[2] if d < 2 else EYERED[1])
    r.fixed(kx - 1, ky - 1, EYERED[5]); r.fixed(kx, ky, (36, 10, 6))
    for u in (-5.0, -4.4):                                                               # bridge
        for v in range(-3, 4):
            p = g.P(u, v); r.fixed(p[0], p[1], STEEL[6] if v < 0 else STEEL[4])
    for (u0, u1) in ((4, 7), (12, 15)):                                                  # pickups
        for u in range(u0, u1):
            for v in range(-3, 4):
                p = g.P(u, v); r.fixed(p[0], p[1], (20, 18, 16) if (u != u0 + 1 or v % 2) else STEEL[6])


def neck(r, g, n0, n1, head_len, strings=2, head_mat='neckw', style='claw'):
    """the neck in the instrument's frame: a brown fretboard with darker frets and pale dots, a rough clawed headstock;
    the strings are a faint sheen (they can't be counted at this size)"""
    on = r.new('neck')
    end = n1
    corners = [g.P(u, v) for u in (n0 - 2, end + head_len + 2) for v in (-7, 7)]
    x0, x1 = int(min(p[0] for p in corners)), int(max(p[0] for p in corners)) + 1
    y0, y1 = int(min(p[1] for p in corners)), int(max(p[1] for p in corners)) + 1
    for y in range(max(0, y0), min(r.h, y1)):
        for x in range(max(0, x0), min(r.w, x1)):
            u, v = g.local(x, y)
            if n0 <= u <= end and -2.2 <= v <= 2.9:
                if v <= 1.9:
                    fret = (end - u) % 5.0 < 0.9
                    k = int((end - u) // 5.0)
                    dot = k in (2, 4, 6, 8) and abs(v) < 0.8 and 2.0 < (end - u) % 5.0 < 3.4
                    if dot: r.put(x, y, None, 0, on, FANG[3])
                    else: r.put(x, y, M['board'], (0.42 if fret else 0.6) + (0.12 if v < -1 else 0), on)
                else:
                    r.put(x, y, M['neckw'], 0.25, on)                                     # the neck's shaded underside
            elif end < u <= end + head_len:
                t = (u - end) / head_len
                if style == 'claw':
                    half = 2.8 + t * 1.8 + (1.3 if int(u * 0.8) % 3 == 0 and t > 0.25 else 0)    # a jagged, clawed headstock
                    if -half <= v + t * 0.6 <= half:
                        r.put(x, y, M[head_mat], 0.75 - 0.35 * (v + half) / (2 * half), on)
                else:                                                                     # a Fender-style paddle
                    lo, hi = -2.6 - min(1.0, t * 3) * 2.6 + max(0, t - 0.8) * 6, 2.6 + (0.6 if t < 0.3 else 0) - t * 1.0
                    if lo <= v <= hi:
                        r.put(x, y, M[head_mat], 0.7 - 0.3 * (v - lo) / (hi - lo) - (0.15 if v > hi - 0.9 or v < lo + 0.9 else 0), on)
    if style == 'claw':
        for u in range(int(end) + 3, int(end + head_len), 3):                           # tuning pegs
            for sv in (-5.0, 5.2):
                p = g.P(u, sv); r.fixed(p[0], p[1], STEEL[8] if sv < 0 else STEEL[5])
    for k in range(strings):                                                            # the string sheen
        sv = -0.9 + 1.8 * k / max(1, strings - 1)
        u = -5.0
        while u < end + 1:
            p = g.P(u, sv); q = (int(p[0]), int(p[1]))
            e = r.buf.get(q)
            if e is not None and (u > n0 or r.groups.get(e[2]) in ('gbody', 'bbody', 'guard')):
                c = e[3] if e[3] else None
                if c is None:
                    mt = e[0]; c = mt.ramp[max(0, min(len(mt.ramp) - 1, int(e[1] * (len(mt.ramp) - 1))))]
                r.fixed(q[0], q[1], mix(c, STEEL[8], 0.3 if u > n0 else 0.45), e[2])
            u += 1.0


def fret_fingers(r, g, uf, mat='hide'):
    """four fingers from the neck's lower edge curled onto the fretboard (the tips press the strings)"""
    for i, k in enumerate((-3.6, -1.2, 1.2, 3.6)):
        base, tip = g.P(uf + k, 3.8), g.P(uf + k - 0.5, -0.6 + 0.5 * (i % 2))
        r.tube(base, tip, 1.45, 1.15, M[mat], lift=0.08 - 0.04 * (i % 2), group='ffing%d' % i)
        r.darken(*g.P(uf + k + 0.9, 1.0), 0.15)


def pick_hand(r, h, P):
    """a loose fist over the strings, the knuckles to us, a bone pick between thumb and finger"""
    x, y = h
    r.ellipsoid(x - 1.5, y + 0.5, 4.2, 3.6, M['hide'], group='pickH')
    for k in range(4):
        r.ellipsoid(x - 2.8 + k * 1.7, y + 2.8 + abs(k - 1.5) * 0.3, 1.1, 1.3, M['hide'], lift=0.05 - (k % 2) * 0.06, group='pickH%d' % k)
    r.tube((x + 1.5, y - 1.5), (x + 3.6, y + 0.5), 1.3, 1.0, M['hide'], lift=0.1, group='pickT')
    r.fixed(x + 4, y + 2, FANG[5]); r.fixed(x + 4, y + 3, FANG[3])


# ============================================================================================================ Bass XL
XLS    = R('#060908 #090d0d #0c1212 #0f1717 #131c1c #162121 #1a2727 #1f2d2d #253434 #2b3c3b #324544 #3b4f4e #485d5b #5a706d #748985')
VISOR  = R('#040607 #080c0e #0d1316 #131b1f #1a252a')
CREAM  = R('#2e2418 #433522 #59472d #6e5939 #806a45 #907a52 #9f8960 #ac976e #b8a47d')
GUARD  = R('#0a0a0a #121212 #1b1b1b #262626 #333333')
ROSEW  = R('#120b08 #1a100b #22160f #2b1c13')
RUSTY  = R('#2a160c #46230f #643314 #80441b #995526')
XLEYE  = [(92, 70, 8), (190, 146, 24), (246, 204, 60), (255, 236, 150)]
M.update({'xl': mat(XLS, 'grime', 0.14, 0.9, (8, 10, 11)), 'visor': mat(VISOR, 'plain', 0.3, 1.2, (6, 8, 9)),
          'cream': mat(CREAM, 'worn', 0.24, 0.5), 'guard': mat(GUARD, 'plain', 0.2, 0.9), 'rosew': mat(ROSEW, 'wood', 0.3)})


def _xp(**k):
    d = dict(bob=0, hd=0, hx=0, pluck=0, fret=0, eye=2, breath=0, knee=0)
    d.update(k); return d

XL_IDLE = [_xp(), _xp(breath=1), _xp(breath=1, hx=1, eye=2), _xp(eye=0)]
XL_PLAY = [_xp(bob=2, hd=3, pluck=1, knee=2, eye=3), _xp(bob=1, hd=1, pluck=0, knee=1, eye=2),
           _xp(bob=1, hd=0, pluck=1, knee=1, eye=2), _xp(bob=0, hd=0, pluck=0, eye=2),
           _xp(bob=2, hd=3, pluck=1, knee=2, fret=1, eye=3), _xp(bob=1, hd=1, pluck=0, knee=1, fret=1, eye=2),
           _xp(bob=1, hd=0, pluck=1, knee=1, fret=1, eye=2), _xp(bob=0, hd=0, pluck=0, fret=1, eye=2)]


def panel_line(r, pts, group=None, dv=0.34, hi=0.14):
    """an engraved seam between steel plates: dark line, a lit lip below/right of it"""
    fold(r, pts, group, dv, -hi)


def rivet(r, x, y):
    r.fixed(x, y, XLS[11]); r.fixed(x + 1, y + 1, XLS[2]); r.fixed(x, y + 1, XLS[5])


def rust_streak(r, x, y, L, group=None):
    for k in range(L):
        e = r.buf.get((int(x), int(y) + 1 + k))
        if e and (group is None or r.groups[e[2]] == group):
            r.fixed(int(x), int(y) + 1 + k, RUSTY[3 - min(3, k // 2)] if k < L - 1 else RUSTY[1])


def bass_xl(P):
    r = Rig(W, H)
    bob, hd, br, kn = P['bob'], P['hd'], P['breath'], P['knee']
    st = M['xl']
    T = lambda y: y + bob - (br if y < 96 else 0)
    # ---------------------------------------------------------------- feet and legs (knees give, mechanically)
    for sx, hip, knee, ank, g in ((-1, (51, 119 + bob), (39 - kn * 0.6, 146 + bob * 0.8), (38, 175), 'L'),
                                  (1, (70, 118 + bob), (81 + kn * 0.6, 142 + bob * 0.8), (84, 175), 'R')):
        foot = poly_mask([(ank[0] - 6, 176), (ank[0] + 6, 176), (ank[0] + 6 + sx * 3, 182), (ank[0] + sx * 11, 185),
                          (ank[0] + sx * 11, SOLE + 1), (ank[0] - sx * 7, SOLE + 1), (ank[0] - sx * 7, 181)])
        region(r, foot, st, D=3.5, group='foot' + g)
        panel_line(r, [(ank[0] - sx * 8, 184), (ank[0] + sx * 12, 184)], 'foot' + g, 0.3, 0.1)
        for x in range(int(ank[0] - 13), int(ank[0] + 15)):
            if (x, SOLE) in r.buf: r.fixed(x, SOLE, XLS[1])
        region(r, path_mask([knee, lerp(knee, ank, 0.35), (ank[0], ank[1] + 1)], [6.2, 6.8, 5.0]), st, D=4.5, group='shin' + g)
        panel_line(r, [(knee[0] - 4, knee[1] + 9), (knee[0] + 4, knee[1] + 9)], 'shin' + g, 0.26, 0.1)
        region(r, path_mask([hip, knee], [8.0, 6.2]), st, D=5.0, group='thigh' + g)
        for y in (6, 10, 14):                                                            # the ribbed joint behind the knee
            pass
        region(r, ellipse_mask(knee[0] + sx * 0.5, knee[1] + 0.5, 5.8, 6.2), st, D=4.0, lift=0.06, group='knee' + g)
        rivet(r, int(knee[0]), int(knee[1]) - 1)
        region(r, ellipse_mask(ank[0], ank[1] - 1, 4.4, 3.2), st, D=2.5, lift=-0.08, group='ankle' + g)
    # ---------------------------------------------------------------- pelvis, belly segments, chest
    region(r, poly_mask([(46, T(108)), (76, T(108)), (77, T(118)), (68, T(127)), (54, T(127)), (45, T(118))]), st, D=5,
           group='pelvis')
    for k in range(4):
        y = T(92) + k * 4
        region(r, poly_mask([(52 - k * 0.3, y), (70 + k * 0.3, y), (69, y + 4.5), (53, y + 4.5)]), st, D=2.2, lift=-0.16 - 0.05 * (k % 2),
               group='belly%d' % k)
    chest = poly_mask([(42, T(61)), (52, T(56)), (70, T(56)), (80, T(61)), (79, T(76)), (73, T(90)), (61, T(95)), (49, T(90)), (43, T(77))])
    region(r, chest, st, D=10.0, group='chest')
    panel_line(r, [(44, T(76)), (52, T(79)), (61, T(80)), (70, T(79)), (78, T(76))], 'chest')
    panel_line(r, [(61, T(58)), (61, T(79))], 'chest', 0.24, 0.08)
    panel_line(r, [(50, T(84)), (61, T(88)), (72, T(84))], 'chest', 0.2, 0.08)
    for (x, y) in ((46, 65), (76, 65), (47, 74), (75, 74), (57, 92), (65, 92)): rivet(r, x, int(T(y)))
    rust_streak(r, 47, T(74), 5, 'chest'); rust_streak(r, 57, T(92), 3)
    for (x, y) in ((52, 66), (53, 67), (54, 68), (69, 84), (70, 85)):                     # scratches catch the light
        r.fixed(x, T(y), XLS[10])
    # ---------------------------------------------------------------- the fretting arm (behind the neck)
    g = Inst((40, 126 + bob), math.radians(-40))
    uf = 77 + 5 * P['fret']
    shR = (79, T(66))
    palm = g.P(uf, 5.6)
    E = ik(shR, palm, 21, 21, 'down')
    region(r, path_mask([shR, E], [7.0, 6.0]), st, D=4.0, group='uarmR')
    region(r, path_mask([E, lerp(E, g.P(uf - 1.5, 8.5), 0.4), g.P(uf - 1.5, 8.5)], [6.0, 6.6, 4.8]), st, D=4.0, group='farmR')
    for k in (0.35, 0.6):
        p = lerp(E, g.P(uf - 1.5, 8.5), k)
        panel_line(r, [(p[0] - 4, p[1] + 1), (p[0] + 4, p[1] - 1)], 'farmR', 0.26, 0.08)
    region(r, ellipse_mask(E[0], E[1], 4.8, 4.6), st, D=3, lift=-0.04, group='elbR')
    region(r, ellipse_mask(*g.P(uf, 5.6), 4.6, 3.6, g.ang), st, D=2.5, group='palmR')
    th = g.P(uf + 2.4, -3.6)
    region(r, ellipse_mask(th[0], th[1], 2.0, 1.7), st, D=1.5, lift=0.1, group='thumbR')
    region(r, ellipse_mask(78, T(64), 6.8, 6.6), st, D=5, lift=0.04, group='padR')         # pauldron
    rivet(r, 80, int(T(60)))
    # ---------------------------------------------------------------- the head: a domed helmet, a black visor
    hx, hy = 60 + P['hx'], 38 + bob + hd - br
    region(r, path_mask([(61, T(50)), (61, T(59))], [4.2, 4.6]), st, D=2.5, lift=-0.25, group='neck')
    for k in range(3): panel_line(r, [(57, T(52) + k * 2.5), (65, T(52) + k * 2.5)], 'neck', 0.3, 0.1)
    helm = ellipse_mask(hx, hy - 2, 12.4, 13.6) | poly_mask([(hx - 10, hy), (hx + 11.5, hy), (hx + 9, hy + 14), (hx - 6, hy + 16)])
    region(r, helm, st, D=7.5, group='head')
    region(r, ellipse_mask(hx - 10.5, hy + 3, 3.2, 5.0), st, D=2.5, lift=0.02, group='ear')         # the side plate
    rivet(r, int(hx - 11), int(hy + 2))
    visor = poly_mask([(hx - 7.5, hy - 5), (hx + 9.5, hy - 5), (hx + 9.5, hy + 2), (hx + 6, hy + 3), (hx + 5, hy + 14), (hx + 2, hy + 16),
                       (hx - 3, hy + 14), (hx - 3.5, hy + 3), (hx - 7.5, hy + 2)])
    region(r, visor, M['visor'], D=3.0, group='visor')
    for y in range(int(hy) - 4, int(hy) + 8):                                             # a reflection across the glass
        r.darken(hx + 7 - (y - hy) * 0.3, y, -0.25)
    if P['eye']:
        for ex in (hx - 3, hx + 4):
            c = XLEYE[P['eye']]
            for dx in range(3):
                for dy in range(3):
                    r.fixed(ex + dx, hy - 2 + dy, c if dy < 2 else XLEYE[max(0, P['eye'] - 1)])
            r.fixed(ex, hy - 2, XLEYE[3])
            if P['eye'] >= 3:                                                            # a flare on the bar's start
                r.darken(ex + 1, hy - 4, -0.4); r.darken(ex + 1, hy + 2, -0.3); r.darken(ex - 1, hy - 1, -0.3); r.darken(ex + 3, hy - 1, -0.3)
    else:
        for ex in (hx - 3, hx + 4):
            for dx in range(3): r.fixed(ex + dx, hy, XLEYE[0])
    panel_line(r, [(hx - 9, hy - 9), (hx - 2, hy - 13), (hx + 6, hy - 12)], 'head', 0.22, 0.12)
    for (x, y) in ((hx - 5, hy - 11), (hx - 4, hy - 11), (hx - 6, hy - 10)): r.fixed(x, y, XLS[12])   # the dome's shine
    # ---------------------------------------------------------------- the bass: a worn cream P-bass, black guard
    bass_body(r, g, P)
    neck(r, g, 21, 93, 15, head_mat='cream', style='fender')
    for u in (96, 99.5, 103, 106.5):                                                      # four big tuners along the top
        p = g.P(u, -6.4)
        for (dx, dy, c) in ((0, 0, XLS[11]), (1, 0, XLS[7]), (0, 1, XLS[6]), (1, 1, XLS[3])): r.fixed(p[0] + dx, p[1] + dy, c)
    fret_fingers(r, g, uf, 'xl')
    # ---------------------------------------------------------------- the plucking arm (in front), its pauldron
    shL = (41, T(66))
    hand = g.P(15, -2.5)
    EL = ik(shL, hand, 25, 28, 'left')
    region(r, path_mask([shL, EL], [7.4, 6.2]), st, D=4.0, group='uarmL')
    region(r, path_mask([EL, lerp(EL, hand, 0.4), hand], [6.2, 6.8, 5.0]), st, D=4.0, group='farmL')
    for k in (0.3, 0.55):
        p = lerp(EL, hand, k)
        panel_line(r, [(p[0] - 1, p[1] - 4), (p[0] + 1, p[1] + 4)], 'farmL', 0.26, 0.08)
    region(r, ellipse_mask(EL[0], EL[1], 5.0, 4.8), st, D=3, lift=-0.02, group='elbL')
    rivet(r, int(EL[0]) - 1, int(EL[1]) - 1)
    region(r, ellipse_mask(39, T(64), 8.4, 7.8), st, D=6, lift=0.08, group='padL')
    rivet(r, 33, int(T(59))); rivet(r, 41, int(T(58)))
    for (x, y) in ((31, 60), (32, 59), (33, 58)): r.fixed(x, T(y), XLS[12])              # the pauldron's shine
    rust_streak(r, 41, T(58), 4, 'padL')
    pluck_hand(r, g, hand, P)
    im = r.render()
    return recolor_outline(im, (18, 14, 12), (10, 13, 14))


def bass_body(r, g, P):
    """a Precision-style body in worn cream: the lacquer gone to wood at the edge and under the forearm, a black guard,
    a split pickup with a thumb rest, a chrome bridge"""
    O = g.O
    loc = lambda u, v: g.P(u, v)
    lower = ellipse_mask(*loc(-7, 0.5), 21.5, 17.5, g.ang + 0.15)
    upper = ellipse_mask(*loc(11, -1), 14.0, 12.5, g.ang)
    horn = path_mask([loc(11, -7), loc(19, -12), loc(25, -13)], [6.5, 4.4, 2.6]) | path_mask([loc(11, 8), loc(18, 11), loc(21, 11)], [5.4, 3.8, 2.4])
    waist = path_mask([loc(-5, 17), loc(6, 11)], [4, 3])
    body = (lower | upper | horn) - waist
    wear = lambda x, y: (-0.18 if nB(x * 1.6, y * 1.6) > 0.68 else 0) + (-0.1 if h32(x, y, 31) % 9 == 0 else 0)
    region(r, body, M['cream'], D=3.0, group='bbody', vfun=wear)
    # the guard: from the neck pocket round the upper bout and down past the pickup, under the strings
    gmask = ellipse_mask(*loc(5, 3), 11.0, 7.5, g.ang + 0.35) | path_mask([loc(12, -3), loc(19, -8)], [3.6, 2.2])
    guard = {p for p in body & gmask if all((p[0] + dx, p[1] + dy) in body for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)))}
    guard -= ellipse_mask(*loc(-9, -2), 4.5, 6.5, g.ang)
    region(r, guard, M['guard'], D=1.5, group='guard')
    for (x, y) in guard:                                                                  # its bevelled edge
        if any((x + dx, y + dy) not in guard for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) and (x + y) % 2 == 0:
            r.fixed(x, y, (58, 56, 52) if g.local(x, y)[1] < 0 else (30, 28, 26))
    for (u0, u1, v0, v1) in ((1, 4, -4, 0.5), (4, 7, -0.5, 4)):                          # split pickup
        for u in range(u0, u1):
            for v in range(int(v0), int(v1) + 1):
                p = loc(u, v); r.fixed(p[0], p[1], (14, 12, 10) if (u + v) % 3 else (60, 58, 54))
    for u in range(-12, -9):                                                              # bridge
        for v in range(-4, 5):
            p = loc(u + 0.5, v); r.fixed(p[0], p[1], XLS[11] if u == -12 else XLS[8] if v < 0 else XLS[5])
    for (u, v) in ((-1, -7), (-2, -7), (-3, -7)):                                         # thumb rest
        p = loc(u, v); r.fixed(p[0], p[1], (30, 28, 26))
    for (u, v) in ((-17, 6), (-19, 3), (-15, 9), (-8, 12)):                               # knobs
        p = loc(u, v)
        r.fixed(p[0], p[1], XLS[9]); r.fixed(p[0] + 1, p[1], XLS[5]); r.fixed(p[0], p[1] + 1, XLS[4]); r.fixed(p[0] + 1, p[1] + 1, XLS[2])


def pluck_hand(r, g, hand, P):
    """the steel hand over the strings: the back of the hand to us, two fingers plucking, the thumb anchored on the
    pickup"""
    x, y = hand
    st = M['xl']
    region(r, ellipse_mask(x, y, 4.0, 3.4, g.ang), st, D=2.5, group='handL')
    th = g.P(9, -6.0)
    region(r, path_mask([(x - 1, y + 1), th], [1.8, 1.4]), st, D=1.4, lift=0.08, group='handLt')
    for k, du in enumerate((-1.6, 1.4)):
        up = (P['pluck'] + k) % 2
        a = g.P(15 + du, -1.0)
        b = g.P(15 + du - (0.6 if up else 0), 3.2 - (1.8 if up else 0))
        region(r, path_mask([(a[0], a[1]), b], [1.5, 1.2]), st, D=1.2, lift=0.06 * k, group='handLf%d' % k)


# ============================================================================================================ Karlis
KW = 144
FUR    = R('#0b0705 #100b07 #150f0a #1a130d #1f1710 #251b13 #2b2016 #31251a #382a1e #403023 #4a3829 #574330 #66503a')
MUZ    = R('#1f1912 #29211a #342b21 #3f342a #4b3f33 #574a3d #645647 #716251')
NOSE   = R('#070505 #0e0a09 #171211 #221b19 #332a26 #4a3f3a')
VESTD  = R('#0b0a09 #11100e #171512 #1e1b17 #25211c #2d2822 #363028 #3f382f #4a4137 #554b40')            # old leather vest
TEEB   = R('#0b0b0b #111111 #171717 #1e1e1e #262626 #2f2f2f')
TROUK  = R('#0c0b0a #121110 #191716 #201e1c #282523 #312d2a')
SHELLK = R('#0a0908 #0f0e0c #151311 #1b1916 #221f1b #2a2621 #332d27 #3d362f #48403a')                  # old black lacquer
HEADK  = R('#2b241b #382f24 #463b2e #544838 #615442 #6e604d #7b6c58 #877863 #92836e')                  # old coated heads
CYM    = R('#17120a #221a0e #2e2312 #3a2d17 #47381d #544323 #614e2a #6f5a33 #7d673d #8b7449 #9a8358')
STANDK = R('#121314 #1c1d1f #26282a #323436 #3f4244 #4e5154 #606366 #767a7c')
STICKW = R('#33261a #4a3925 #614c31 #775f3e #8a714d #9b825e')
LOGO   = (150, 142, 124)
M.update({'fur': mat(FUR, 'bearfur', 0.16, 0.05, (12, 8, 5)), 'muz': mat(MUZ, 'bearfur', 0.24, 0.1, (16, 11, 7)),
          'nose': mat(NOSE, 'plain', 0.2, 1.4), 'vestd': mat(VESTD, 'blackjeans', 0.18, 0.2), 'teeb': mat(TEEB, 'knit', 0.2),
          'trouk': mat(TROUK, 'blackjeans', 0.2), 'shellk': mat(SHELLK, 'worn', 0.18, 0.7), 'headk': mat(HEADK, 'worn', 0.26, 0.1),
          'cym': mat(CYM, 'metal', 0.2, 1.0, (18, 13, 6)), 'standk': mat(STANDK, 'metal', 0.22, 0.9), 'stick': mat(STICKW, 'wood', 0.3, 0.4)})


def shag(mask, amount=1, seed=0):
    """make a fur edge: nibble the boundary, let tufts poke out (mostly downward, fur hangs)"""
    m = set(mask)
    for (x, y) in list(mask):
        if any((x + dx, y + dy) not in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            hsh = h32(x, y, seed)
            if hsh % 6 == 0: m.discard((x, y))
            if amount and hsh % 9 == 1 and (x, y + 1) not in mask:
                m.add((x, y + 1))
                if amount > 1 and hsh % 2: m.add((x, y + 2))
    return m


# stick tips and paw positions; R = his right paw (viewer's left), L = his left paw (viewer's right)
K_CRASH, K_TOM1, K_TOM2, K_HH = (17, 83), (41, 108), (82, 111), (114, 95)
def _kp(**k):
    d = dict(R='rest', L='rest', bob=0, hd=0, hx=0, wob=0, kick=0, hh=2, blink=False, look=0, ear=0, roar=False, breath=0)
    d.update(k); return d

KARLIS_IDLE = [_kp(), _kp(breath=1), _kp(breath=1, hx=-1, look=-1, ear=1), _kp(blink=True)]
KARLIS_PLAY = [_kp(R='crash', L='tom2', kick=1, wob=1, hd=1, bob=1), _kp(R='mid', L='up', wob=2, hd=0),
               _kp(R='tom1up', L='hh', hh=0, wob=3, bob=1), _kp(R='tom1up', L='up', hh=2),
               _kp(R='tom1', L='tom2up', kick=1, hd=1, bob=1), _kp(R='mid', L='tom2up', hd=0),
               _kp(R='tom1', L='hh', hh=0, bob=1), _kp(R='up', L='tom2', hd=-1, roar=True)]
# (paw, stick tip) per pose
K_RPOSE = {'rest': ((36, 68), (51, 49)), 'crash': ((36, 80), (18, 86)), 'mid': ((36, 64), (50, 46)), 'up': ((34, 54), (47, 34)),
           'tom1': ((46, 98), (40, 109)), 'tom1up': ((44, 86), (42, 70))}
K_LPOSE = {'rest': ((104, 100), (88, 108)), 'tom2': ((102, 100), (84, 111)), 'tom2up': ((104, 90), (94, 78)),
           'hh': ((108, 98), (118, 95)), 'up': ((108, 86), (116, 72))}
K_SH = {'R': (60, 64), 'L': (116, 62)}                                                    # shoulders (before breath/bob)


def cymbal(r, cx, cy, rx, ry, rot, group, lift=0.0):
    """a cymbal seen from the side-above: a flat bronze disc facing up -- lathe rings, a darker rim, a bell, one sheen"""
    ry = max(1.2, ry)
    oid = r.new(group)
    c, s = math.cos(rot), math.sin(rot)
    for (x, y) in ellipse_mask(cx, cy, rx, ry, rot):
        dx, dy = x + 0.5 - cx, y + 0.5 - cy
        u, w = (dx * c + dy * s) / rx, (-dx * s + dy * c) / ry
        d = math.hypot(u, w)
        v = 0.5 + lift - 0.16 * d - 0.12 * w + (0.06 if int(d * 9) % 2 else -0.04)
        if abs(u + w * 0.4 + 0.25) < 0.12: v += 0.28                                     # the sheen
        if d > 0.86 and w > 0: v -= 0.18                                                # the edge turned away
        r.put(x, y, M['cym'], v, oid)
    for (x, y) in ellipse_mask(cx - s * ry * 0.3, cy - c * ry * 0.3, 3.4, max(1.0, ry * 0.5), rot):
        r.put(x, y, M['cym'], 0.68 + lift - (0.18 if y > cy - ry * 0.3 else 0), oid)     # the bell


def flat_head(r, mask, cx, cy, rx, ry, group, base=0.5, lift=0.0, mottle=0.22):
    """a drum head seen at an angle: a flat, worn, coated skin -- lighter at the back, stick marks in the middle"""
    oid = r.new(group)
    for (x, y) in mask:
        u, w = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
        d = math.hypot(u, w)
        v = base + lift - 0.12 * w - 0.06 * u - (0.12 if d > 0.88 else 0) + (nB(x * 1.7, y * 1.7) - 0.5) * mottle
        if (u + 0.15) ** 2 + (w * 0.8) ** 2 < 0.08 and h32(x, y, 61) % 3 == 0: v -= 0.16   # stick marks
        r.put(x, y, M['headk'], v, oid)
    return oid


def drum(r, cx, top, rx, ry, h, group, lugs=4):
    """a shell (cx, top = the head's middle) seen a little from above: a coated head in a steel hoop, lugs"""
    shell = poly_mask([(cx - rx, top), (cx + rx, top), (cx + rx, top + h), (cx - rx, top + h)]) | ellipse_mask(cx, top + h, rx, ry)
    region(r, shell, M['shellk'], D=4.0, group=group,
           vfun=lambda x, y: (0.14 if abs(x - (cx - rx * 0.45)) < 1.2 else 0) + (-0.12 if y > top + h - 1 else 0))
    for k in range(lugs):
        lx = cx - rx * 0.78 + k * rx * 1.56 / max(1, lugs - 1)
        for y in range(int(top + 3), int(top + min(h, 9))):
            r.fixed(lx, y, STANDK[6] if y % 3 else STANDK[3])
        r.fixed(lx, top + 2, STANDK[7])
    for (y0, w) in ((top + 1, 2), (top + h - 1, 1)):                                    # the hoops: a lit chrome band
        for k in range(w):
            for x in range(int(cx - rx), int(cx + rx) + 1):
                y = int(y0 + k + ry * 0.55 * max(0.0, 1 - ((x + 0.5 - cx) / rx) ** 2) ** 0.5)
                if (x, y) in r.buf: r.fixed(x, y, STANDK[7 - k] if x < cx - rx * 0.3 else STANDK[5 - k] if x < cx + rx * 0.4 else STANDK[3])
    flat_head(r, ellipse_mask(cx, top, rx, ry), cx, top, rx, ry, group + 'h', base=0.55)
    for k in range(int(rx * 3.2)):                                                       # the top hoop
        a = k / (rx * 3.2) * 2 * math.pi
        x, y = cx + rx * math.cos(a), top + ry * math.sin(a)
        r.fixed(x, y, STANDK[7] if math.sin(a) < 0 and math.cos(a) < 0.3 else STANDK[4])


def stand(r, x, top, bottom, group, spread=10, pedal=False):
    r.stroke([(x, y) for y in range(int(top), int(bottom) - 8)], 1.5, M['standk'], v=0.42, group=group)
    for dx in (-spread, -spread * 0.35, spread):
        r.stroke(curve(lambda t: (x + dx * t, bottom - 9 + 9 * t), 12), 1.3, M['standk'], v=0.45, group=group)
    r.fixed(x, bottom - 9, STANDK[7]); r.fixed(x, bottom - 8, STANDK[5])
    for y in range(int(top) + 4, int(bottom) - 10, 9): r.fixed(x, y, STANDK[7]); r.fixed(x + 1, y, STANDK[2])   # wing nuts
    if pedal:
        region(r, poly_mask([(x - 3, bottom - 1), (x + 9, bottom - 4), (x + 10, bottom), (x - 3, bottom + 1)]), M['standk'], D=1.5, group=group + 'p')


def toast_sign(r, cx, cy, P, group):
    """the band's sign painted in dark ink on the kick's worn front head: a slice of toast with angry eyes and a
    fanged grin -- faded, scuffed by years of beater and boots"""
    th = int(P['kick'])
    cy = cy + th * 0.5
    ink = (40, 28, 18)
    def ins(x, y):
        dx, dy = x + 0.5 - cx, y + 0.5 - cy
        if -10.5 <= dx <= 10.5 and -3 <= dy <= 11 - abs(dx) * 0.08: return True
        return (dx + 5) ** 2 + (dy + 3.5) ** 2 <= 36 or (dx - 5) ** 2 + (dy + 3.5) ** 2 <= 36 or (abs(dx) <= 6 and -8 <= dy <= -3)
    S = {(x, y) for y in range(int(cy) - 13, int(cy) + 14) for x in range(int(cx) - 13, int(cx) + 14) if ins(x, y)}
    def paint(x, y, c, k):
        e = r.buf.get((x, y))
        if not e: return
        base = e[3] if e[3] else e[0].ramp[max(0, min(len(e[0].ramp) - 1, int(e[1] * (len(e[0].ramp) - 1))))]
        if nA(x * 2.4, y * 2.4) > 0.7: k *= 0.45                                          # paint worn off
        r.fixed(x, y, mix(base, c, k))
    for (x, y) in S:
        edge = any((x + dx, y + dy) not in S for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        deep = edge or any((x + dx, y + dy) not in S for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)))
        if edge: paint(x, y, (52, 32, 18), 0.8)                                           # the crust
        elif deep: paint(x, y, (110, 70, 36), 0.55)
        else: paint(x, y, (156, 116, 66), 0.4)                                            # golden crumb
    ey = int(cy) - 1
    for sd in (-1, 1):                                                                    # angry eyes: slanted brows
        ex = int(cx) + sd * 4
        for k in range(4): paint(ex - sd * 2 + sd * k, ey - 2 + (k if sd > 0 else 3 - k) // 2 - 1, ink, 0.9)
        paint(ex, ey, ink, 0.9); paint(ex + sd, ey, ink, 0.9); paint(ex, ey + 1, (110, 26, 14), 0.8)
    my = ey + 5
    for x in range(int(cx) - 6, int(cx) + 7):                                             # the grin with fangs
        paint(x, my + (1 if abs(x - cx) > 4 else 0) - (1 if abs(x - cx) > 6 else 0), ink, 0.9)
    for x in (int(cx) - 4, int(cx), int(cx) + 4):
        paint(x, my + 1, (206, 192, 162), 0.7); paint(x, my + 2, (180, 166, 136), 0.45)


def fur_rim(r, groups, dv=0.24):
    """top light on fur: the upper edge of the silhouette (and of every clump against the dark behind it) catches it"""
    hit = []
    for (x, y), e in r.buf.items():
        if e[0] is None or r.groups[e[2]] not in groups: continue
        up, ul = r.buf.get((x, y - 1)), r.buf.get((x - 1, y - 1))
        if up is None or (up[0] is not None and r.groups[up[2]] not in groups and up[2] < e[2]):
            hit.append(((x, y), dv)); hit.append(((x, y + 1), dv * 0.45))
        elif ul is None:
            hit.append(((x, y), dv * 0.6))
    for (q, d) in hit:
        e = r.buf.get(q)
        if e and e[0] is not None: e[1] += d


def karlis(P):
    r = Rig(KW, H)
    bob, br = P['bob'], P['breath']
    T = lambda y: y + bob - br
    # ---------------------------------------------------------------- behind him: the crash's boom stand
    stand(r, 14, 100, SOLE, 'standC', spread=10)
    r.stroke(curve(lambda t: (14 + 12 * t, 100 - 15 * t), 16), 1.6, M['standk'], v=0.55, group='standC')   # the boom
    # ---------------------------------------------------------------- the drum throne under him (its post shows below)
    region(r, ellipse_mask(91, 139, 13, 3.6), M['vestd'], D=2, lift=-0.1, group='throne')
    region(r, path_mask([(91, 141), (91, 176)], [1.6, 1.6]), M['standk'], D=1.2, lift=-0.2, group='throne')
    for dx in (-11, 3, 11):
        r.stroke(curve(lambda t: (91 + dx * t, 175 + 13 * t), 10), 1.3, M['standk'], v=0.35, group='throne')
    # ---------------------------------------------------------------- the mass of him, seated: a thick neck into sloped
    # shoulders, a barrel chest, the belly and lap sinking behind the toms (one fur volume, no seams)
    body = (poly_mask([(76, T(42)), (100, T(40)), (113, T(49)), (122, T(62)), (126, T(80)), (124, T(100)), (116, T(116)), (104, T(124)),
                       (76, T(126)), (60, T(118)), (52, T(100)), (50, T(80)), (54, T(64)), (63, T(51))])
            | ellipse_mask(88, T(104), 33, 20))
    region(r, shag(body, 2, 7), M['fur'], D=15, group='body')
    # the upper arms hang from the shoulders out of the vest's armholes (drawn before the vest)
    for side in ('R', 'L'):
        sh = (K_SH[side][0], T(K_SH[side][1]))
        paw, tip = (K_RPOSE if side == 'R' else K_LPOSE)[P[side]]
        E = elbow(sh, paw, side)
        region(r, shag(path_mask([sh, lerp(sh, E, 0.4), E], [10.0, 9.2, 7.6]), 2, 19 + len(side)), M['fur'], D=7, group='body')
    # the band tee over the barrel chest, the open leather vest over it -- it ends at the waist
    tee = poly_mask([(77, T(52)), (101, T(50)), (110, T(70)), (113, T(98)), (108, T(122)), (70, T(124)), (64, T(98)), (67, T(70))])
    region(r, tee, M['teeb'], D=10, group='tee')
    for (x, y) in logo_pts(88, T(80)): r.fixed(x, y, mix(LOGO, TEEB[3], 0.3 if (x + y) % 3 else 0.05))
    for sd, pts in ((-1, [(76, T(47)), (68, T(52)), (63, T(60)), (61, T(74)), (56, T(84)), (54, T(100)), (58, T(110)), (73, T(112)),
                          (76, T(96)), (78, T(70)), (79, T(56))]),
                    (1, [(101, T(46)), (110, T(51)), (114, T(59)), (115, T(73)), (120, T(84)), (122, T(100)), (118, T(110)), (104, T(112)),
                         (101, T(96)), (99, T(70)), (99, T(55))])):
        g = 'vest%d' % sd
        region(r, poly_mask(pts), M['vestd'], D=7, lift=-0.08, group=g,
               vfun=lambda x, y: (-0.12 if (x * 5 + y * 3) % 17 == 0 else 0) + (0.07 if (x * 3 + y) % 23 == 0 else 0)
               + (nB(x * 1.8 + 30, y * 1.8) - 0.5) * 0.2)
        seam(r, g, 0.22)
        cx0 = 89 + sd * 20                                                                 # chest pocket + flap
        region(r, poly_mask([(cx0 - 5, T(74)), (cx0 + 5, T(74)), (cx0 + 5, T(78)), (cx0, T(80)), (cx0 - 5, T(78))]), M['vestd'],
               D=1.5, lift=0.12, group='flap%d' % sd)
        seam(r, 'flap%d' % sd, 0.26)
        r.fixed(cx0, T(78), STANDK[7])
        fold(r, [(89 + sd * 31, T(88)), (89 + sd * 26, T(96)), (89 + sd * 22, T(106))], g, 0.24, 0.1)
        fold(r, [(89 + sd * 25, T(64)), (89 + sd * 22, T(72))], g, 0.18, 0.08)
        fold(r, [(89 + sd * 14, T(60)), (89 + sd * 13, T(84)), (89 + sd * 13, T(110))], g, -0.12, 0.0)    # the worn front edge
        for k in range(4):                                                                 # studs down the front edge
            y = T(86) + k * 6; x = 89 + sd * (13 + k * 0.2)
            r.fixed(x, y, STANDK[7]); r.fixed(x, y + 1, STANDK[2])
        for y in range(int(T(106)), int(T(113))):                                         # the frayed hem at the waist
            if (y * 3 + sd) % 4 == 0: r.darken(89 + sd * (16 + (y * 7) % 13), y, 0.24)
    collar = [(70, T(50)), (77, T(56)), (88, T(59)), (99, T(56)), (107, T(49))]
    region(r, path_mask(collar, [2.6, 2.8, 2.8, 2.8, 2.6]), M['vestd'], D=2, lift=0.16, group='collar')
    for k, (x, y) in enumerate(collar[1:-1]):
        r.fixed(x - 2, y - 1, STANDK[7]); r.fixed(x + 2, y, STANDK[6])
    for k in range(9):                                                                    # a chain round his neck
        a = math.pi * (0.15 + 0.7 * k / 8)
        r.fixed(89 - 11 * math.cos(a), T(60) + 5 * math.sin(a), CYM[9] if k % 2 else CYM[6])
    # ---------------------------------------------------------------- the head: heavy, low, the long muzzle down to the drums
    hx, hy = 85 + P['hx'], 32 + P['hd'] + bob - br
    ear = P['ear']
    for (ex, ey, s) in ((hx - 13, hy - 14 - ear, 0.92), (hx + 14, hy - 14, 1.0)):           # small round ears, set back
        region(r, shag(ellipse_mask(ex, ey, 4.8 * s, 4.6 * s), 1, 13), M['fur'], D=2.8, lift=0.04, group='ear')
        region(r, ellipse_mask(ex + 0.5 * (1 if ex < hx else -1), ey + 1.0, 2.2 * s, 2.0 * s), M['muz'], D=1.2, lift=-0.5, group='earin')
    skull = (ellipse_mask(hx + 1, hy - 3, 18.0, 13.0) | ellipse_mask(hx, hy + 8, 17.0, 10.0)
             | ellipse_mask(hx + 3, hy + 15, 14.0, 7.5))
    muzzle = poly_mask([(hx - 10, hy + 1), (hx - 2, hy + 2), (hx + 1, hy + 10), (hx - 2, hy + 19), (hx - 9, hy + 23), (hx - 17, hy + 21),
                        (hx - 20, hy + 16), (hx - 17, hy + 8)])
    region(r, shag(skull, 1, 17), M['fur'], D=10, group='head',
           vfun=lambda x, y: (-0.12 if y > hy + 16 and x > hx - 2 else 0) + (-0.08 if y < hy - 8 else 0))
    region(r, muzzle, M['fur'], D=6, lift=0.02, group='head')
    for (x, y) in muzzle:                                                                 # the snout greys toward its tip
        t = max(0.0, min(1.0, ((hx - 1) - x) / 18 + (y - (hy + 6)) / 28))
        e = r.buf.get((x, y))
        if e and e[0] is M['fur'] and (h32(x, y, 91) % 100) / 100 < t * 0.9: e[0] = M['muz']; e[1] -= 0.04
    for (x, y) in path_mask([(hx - 6, hy + 3), (hx - 10, hy + 8), (hx - 14, hy + 12)], [1.6, 1.8, 1.6]):
        e = r.buf.get((x, y))                                                             # the top-lit bridge of the muzzle
        if e and e[0] is not None and h32(x, y, 93) % 3: e[1] += 0.1
    for (bx, sd) in ((hx - 9, -1), (hx + 5, 1)):                                           # brow ridges over each eye
        region(r, ellipse_mask(bx, hy - 3.5, 5.6, 2.0, sd * -0.25), M['fur'], D=1.8, lift=0.12, group='head')
        for dx in range(-4, 4):
            r.darken(bx + dx, hy - 1, 0.28); r.darken(bx + dx, hy, 0.16)                   # the deep socket under it
    nose = ellipse_mask(hx - 14.5, hy + 16.5, 4.6, 3.5, 0.2)
    region(r, nose, M['nose'], D=1.8, lift=-0.3, group='nose')
    for (dx, dy, c) in ((-17, 15, NOSE[5]), (-16, 14, NOSE[4]), (-15, 14, NOSE[3]), (-17, 18, NOSE[0]), (-13, 18, NOSE[0])):
        r.fixed(hx + dx, hy + dy, c)
    if P['roar']:                                                                         # a roar on the fill
        region(r, poly_mask([(hx - 17, hy + 21), (hx - 3, hy + 20), (hx - 3, hy + 26), (hx - 12, hy + 28)]), M['nose'], D=1.5,
               lift=-0.1, group='mouth')
        for (dx, dy) in ((-15, 21), (-5, 20), (-10, 26), (-5, 25)): r.fixed(hx + dx, hy + dy, (196, 182, 154))
    else:
        for (dx, dy) in ((-16, 21), (-14, 22), (-12, 22), (-9, 23), (-6, 22), (-4, 22), (-2, 21)):
            r.fixed(hx + dx, hy + dy, MUZ[0])
    for (ex, ey, far) in ((hx - 9, hy + 1, True), (hx + 5, hy, False)):                   # small, deep-set, squinting
        if P['blink']:
            for dx in (-1, 0, 1): r.fixed(ex + dx, ey, FUR[2])
        else:
            r.fixed(ex - 1, ey, (104, 70, 32)); r.fixed(ex, ey, NOSE[0]); r.fixed(ex + 1, ey, (70, 46, 22))
            r.fixed(ex, ey + 1, NOSE[1]); r.fixed(ex - 1, ey + 1, (60, 40, 20))
            r.fixed(ex - 1 + (1 if P['look'] < 0 else 0), ey, (176, 142, 92))               # the glint
    fur_rim(r, ('body', 'head', 'ear'), 0.3)
    # ---------------------------------------------------------------- his left leg (viewer's right): the thigh comes at us
    # from the throne, the knee shows between tom and hi-hat, the shin goes down to the pedal
    press = 1 if P['hh'] == 0 else 0
    region(r, shag(path_mask([(117, 162), (120, 177)], [5.4, 5.0]), 1, 43), M['fur'], D=3, group='ankle')    # fur above the foot
    region(r, path_mask([(114, T(134)), (116, 150), (118, 163)], [7.4, 6.8, 6.4]), M['trouk'], D=4, group='shin')
    fold(r, [(111, 146), (116, 149), (121, 146)], 'shin', 0.2, 0.1)
    for x in range(110, 126):                                                             # the rolled-up cuff
        for y in (161, 162):
            e = r.buf.get((x, y))
            if e and r.groups[e[2]] == 'shin': e[1] += 0.14 if y == 161 else -0.12
    region(r, ellipse_mask(108, T(124), 13, 8.5, 0.25), M['trouk'], D=6, group='thigh')
    region(r, ellipse_mask(114, T(130), 7.6, 6.6), M['trouk'], D=4, lift=0.06, group='thigh')
    fold(r, [(98, T(121)), (105, T(124)), (111, T(122))], 'thigh', 0.24, 0.12)
    kx, ky = 112, int(T(128))                                                             # the torn knee, fur shows
    for (dx, dy) in ((0, 0), (1, 0), (2, 0), (-1, 1), (0, 1), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (1, 3)):
        r.fixed(kx + dx, ky + dy, FUR[8 + (1 if dy < 2 and dx < 2 else 0)])
    for (dx, dy) in ((-1, -1), (1, -1), (3, -1), (4, 2), (3, 4), (-2, 2)): r.fixed(kx + dx, ky + dy, TROUK[5])
    region(r, shag(ellipse_mask(122, 184 + press * 0.5, 9.5, 4.6, 0.1 + press * 0.08), 1, 5), M['fur'], D=3, group='footR')
    for k in range(4): r.fixed(128 + k * 1.5, 186 + press + (k % 2), MUZ[5])              # claws on the pedal
    fur_rim(r, ('ankle', 'footR'), 0.25)
    stand(r, 121, 100, SOLE, 'standH', spread=12, pedal=True)
    # ---------------------------------------------------------------- the kit in front of him
    tilt = (0.5, 0.95, 0.2, 0.64)[P['wob']]                                                # the crash wobbles after a hit
    cymbal(r, 26, 85 - tilt * 1.5, 22.5, 5.0 + tilt * 4.0, math.radians(-16 + tilt * 6), 'crash')
    gap = P['hh']
    cymbal(r, 121, 99, 18, 3.0, math.radians(-3), 'hhbot'); cymbal(r, 121, 97 - gap, 18, 3.4, math.radians(-3), 'hhtop', lift=0.06)
    stand(r, 38, 132, SOLE - 4, 'standT', spread=9)
    drum(r, 38, 108, 16, 4.6, 23, 'tom1')
    drum(r, 80, 112, 15, 4.2, 20, 'tom2')
    kick(r, 49, 161, P)
    # ---------------------------------------------------------------- forearms, paws and sticks
    for side in ('R', 'L'):
        forearm(r, (K_SH[side][0], T(K_SH[side][1])), (K_RPOSE if side == 'R' else K_LPOSE)[P[side]], side)
    fur_rim(r, ('farmR', 'farmL', 'pawR', 'pawL'), 0.2)
    im = r.render()
    return recolor_outline(im, (18, 14, 12), (12, 8, 5))


def elbow(sh, paw, side):
    """the upper arm hangs from the shoulder close to the body: the elbow down, a little out"""
    return ik(sh, paw, 22, 24, (lambda e: e[0] * 0.15 + e[1]) if side == 'L' else (lambda e: -e[0] * 0.15 + e[1]))


def forearm(r, sh, pose, side):
    """the forearm from the elbow to a big paw gripping the stick (fingers rolled round it, claws showing)"""
    paw, tip = pose
    sd = -1 if side == 'R' else 1
    E = elbow(sh, paw, side)
    region(r, shag(path_mask([E, lerp(E, paw, 0.35), paw], [8.2, 8.8, 6.8]), 2, 23 + sd), M['fur'], D=5, group='farm' + side)
    wr = lerp(E, paw, 0.7)                                                                # a leather wrist band
    dx, dy = paw[0] - E[0], paw[1] - E[1]; L = math.hypot(dx, dy) or 1
    for k in (-1, 0, 1):
        p = (wr[0] + dx / L * k, wr[1] + dy / L * k)
        region(r, path_mask([(p[0] - dy / L * 8, p[1] + dx / L * 8), (p[0] + dy / L * 8, p[1] - dx / L * 8)], [0.9, 0.9]),
               M['vestd'], D=1.0, lift=0.1 if k else 0.2, group='band' + side)
    sx, sy = tip[0] - paw[0], tip[1] - paw[1]; SL = math.hypot(sx, sy) or 1
    ux, uy = sx / SL, sy / SL                                                             # along the stick
    nx, ny = -uy, ux
    butt = (paw[0] - ux * 8, paw[1] - uy * 8)
    region(r, path_mask([butt, tip], [1.3, 1.0]), M['stick'], D=1.0, group='stick' + side)
    r.fixed(tip[0], tip[1], STICKW[5])
    region(r, shag(ellipse_mask(paw[0] - ux * 1.0, paw[1] - uy * 1.0, 7.6, 6.8), 1, 29 + sd), M['fur'], D=4, group='paw' + side)
    for k in range(4):                                                                    # fingers rolled over the stick
        c = (paw[0] + ux * (k - 1.5) * 2.6 + nx * 3.2, paw[1] + uy * (k - 1.5) * 2.6 + ny * 3.2)
        region(r, ellipse_mask(c[0], c[1], 1.9, 1.6), M['fur'], D=1.4, lift=0.06 - 0.06 * (k % 2), group='fing%s%d' % (side, k))
        r.fixed(c[0] + nx * 1.6, c[1] + ny * 1.6, MUZ[5] if k % 2 else MUZ[6])           # claw tips
    th = (paw[0] - nx * 3.0 + ux * 2.0, paw[1] - ny * 3.0 + uy * 2.0)                     # the thumb over the stick
    region(r, ellipse_mask(th[0], th[1], 2.2, 1.8), M['fur'], D=1.4, lift=0.1, group='thumb' + side)


def logo_pts(cx, cy):
    """a scratchy, spiky black-metal style band logo on the tee (unreadable, as they are)"""
    pts = set()
    for k in range(9):
        x = cx - 9 + k * 2.2
        h = 6 + (3 if k in (2, 6) else 0) + (k % 2)
        for j in range(h): pts.add((int(x + (j % 3 == 0) * 0.5), int(cy - h // 2 + j)))
    for x in range(int(cx) - 11, int(cx) + 12):
        if x % 2 == 0: pts.add((x, int(cy) + 1))
    for (dx, dy) in ((-12, -6), (-11, -5), (11, -6), (12, -7), (-1, -8), (0, -9), (1, -8), (-13, 4), (13, 4), (-5, 6), (5, 7)):
        pts.add((int(cx + dx), int(cy + dy)))
    return pts


def kick(r, cx, cy, P):
    th = P['kick']
    for sx in (-1, 1):                                                                    # spurs
        r.stroke(curve(lambda t: (cx + sx * (20 + 8 * t), cy + 12 + 16 * t), 10), 1.6, M['standk'], v=0.5, group='spur')
    region(r, ellipse_mask(cx, cy, 26.5, 26.5), M['shellk'], D=4, group='kickhoop')
    for k in range(14):                                                                   # claws + tension rods
        a = k / 14 * 2 * math.pi + 0.1
        x, y = cx + 26 * math.cos(a), cy + 26 * math.sin(a)
        r.fixed(x, y, STANDK[7] if math.sin(a) < 0.3 else STANDK[4]); r.fixed(x + math.cos(a), y + math.sin(a), STANDK[3])
    head = ellipse_mask(cx, cy + th * 0.4, 23.0, 23.0)
    flat_head(r, head, cx - 6, cy - 8, 30, 30, 'kick', base=0.62, lift=0.07 * th, mottle=0.3)
    for (x, y) in head:                                                                   # the hoop's shadow on it
        if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy - th * 0.4) ** 2 > 20.5 ** 2 and y < cy + 4: r.darken(x, y, 0.16)
    toast_sign(r, cx, cy, P, 'kick')


# ============================================================================================================ Mira
ROBEM  = R('#080d08 #0c130c #111a10 #162115 #1b291a #213120 #283a26 #30442d #394f35 #435a3d #4e6647')
VOID   = R('#030403 #060806 #0a0d09 #0f130d')
SCARFM = R('#2a2416 #3b331f #4e4429 #615534 #74673f #86784b #978a59 #a69a68 #b3a878')
STONE  = R('#060806 #0a0d09 #0e120d #121711 #161c15 #1b2219 #20281e #262f23 #2d3629 #343e30 #3c4737')
VINE   = R('#081008 #0c170b #111f0f #162714 #1c3019 #23391e #2b4324 #344e2b')
FINGER = R('#1d2619 #2a3524 #384530 #47563d #57674b #687a5a #7a8c6a')
SKULLG = R('#2a2110 #3d3116 #52431d #675525 #7b672e #8f7a39 #a28d47 #b29e58')
RUNE   = [(24, 52, 22), (44, 98, 38), (84, 176, 66), (150, 238, 110), (214, 255, 182)]
M.update({'robe': mat(ROBEM, 'knit', 0.18, 0.05, (6, 10, 6)), 'void': mat(VOID, 'plain', 0.6), 'scarf': mat(SCARFM, 'knit', 0.24, 0.0, (20, 16, 10)),
          'stone': mat(STONE, 'stone', 0.18, 0.2, (5, 8, 5)), 'vine': mat(VINE, 'hide', 0.2, 0.2, (5, 9, 5)),
          'finger': mat(FINGER, 'hide', 0.24, 0.15, (10, 14, 8)), 'skull': mat(SKULLG, 'worn', 0.26, 0.6, (24, 18, 8))})


def _mp(**k):
    d = dict(hl=(36, 112), hr=(78, 112), hx=0, hd=0, led=0, blink=False, ph=0.0, eyes=1, breath=0, look=0)
    d.update(k); return d

MIRA_IDLE = [_mp(), _mp(breath=1, ph=0.6, led=1), _mp(breath=1, ph=1.2, hx=-1, look=-1, led=2), _mp(ph=1.8, blink=True, led=3)]
MIRA_PLAY = [_mp(hl=(32, 111), hr=(80, 108), hd=1, led=0, eyes=3, ph=0.0), _mp(hl=(38, 108), hr=(76, 112), led=1, eyes=2, ph=0.8),
             _mp(hl=(44, 111), hr=(84, 108), hx=1, led=2, eyes=1, ph=1.6), _mp(hl=(36, 108), hr=(72, 112), hx=1, led=3, eyes=1, ph=2.4),
             _mp(hl=(30, 111), hr=(82, 108), hd=1, led=4, eyes=3, ph=3.2), _mp(hl=(40, 108), hr=(78, 112), led=5, eyes=2, ph=4.0),
             _mp(hl=(46, 111), hr=(86, 108), hx=-1, led=6, eyes=1, ph=4.8), _mp(hl=(34, 108), hr=(74, 112), hx=-1, led=7, eyes=1, ph=5.6)]


def spline(ctrl, per=6):
    """a Catmull-Rom curve through the control points"""
    P = [ctrl[0]] + list(ctrl) + [ctrl[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(per):
            t = k / per; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(ctrl[-1])
    return out


def vine(r, pts, r0, r1, group, bud=None):
    radii = [max(0.7, r0 + (r1 - r0) * k / (len(pts) - 1)) for k in range(len(pts))]
    region(r, path_mask(pts, radii), M['vine'], D=2.2, group=group)
    for k in range(3, len(pts) - 2, 4):                                                   # small thorns / leaf nubs
        (ax, ay), (bx, by) = pts[k], pts[k + 1]
        L = math.hypot(bx - ax, by - ay) or 1
        side = 1 if k % 8 == 3 else -1
        r.fixed(ax + (by - ay) / L * radii[k] * side * 1.3, ay - (bx - ax) / L * radii[k] * side * 1.3, VINE[6])


def mira(P):
    r = Rig(W, H)
    br, hx, hd = P['breath'], P['hx'], P['hd']
    ph = P['ph']
    T = lambda y: y - br + (3 if y < 96 else 0)                                          # hunched over the console
    # ---------------------------------------------------------------- vines curling up behind the console
    def tendril(ctrl, r0, group, phase=0.0, amp=1.4):
        sw = [(x + math.sin(ph + phase) * amp * (k / (len(ctrl) - 1)) ** 1.5, y) for k, (x, y) in enumerate(ctrl)]
        pts = spline(sw, 6)
        vine(r, pts, r0, 0.8, group)
        return pts
    left = tendril([(16, 186), (11, 166), (19, 148), (11, 130), (15, 110), (21, 94), (18, 84)], 3.8, 'vineL', 0.0)
    bx, by = left[-1]
    region(r, ellipse_mask(bx + 1, by - 5, 6.4, 5.2), M['vine'], D=3.5, lift=0.1, group='bud')
    for (dx, dy) in ((-2, -6), (1, -7), (3, -4), (0, -4), (4, -6), (-1, -2)):            # pale spots on the bud
        r.fixed(bx + 1 + dx, by + dy, mix(VINE[7], RUNE[2], 0.45))
    tendril([(14, 134), (9, 126), (7, 118), (11, 113), (15, 116), (13, 120)], 2.2, 'vineL2', 1.0, 1.0)
    tendril([(101, 186), (108, 166), (100, 148), (109, 128), (114, 108), (108, 94), (112, 84), (117, 86), (116, 91)], 3.8, 'vineR0', 0.5)
    tendril([(98, 178), (111, 160), (119, 142), (115, 126), (119, 118), (123, 121), (121, 126)], 2.8, 'vineR1', 2.0, 1.2)
    tendril([(96, 156), (105, 140), (103, 130), (99, 128), (98, 133)], 2.2, 'vineR2', 3.0, 0.8)
    # ---------------------------------------------------------------- the robe, the scarf, the hood
    region(r, poly_mask([(46, T(68)), (55, T(64)), (73, T(64)), (83, T(68)), (91, T(80)), (96, T(98)), (98, T(116)), (32, T(116)), (34, T(98)), (38, T(80))]),
           M['robe'], D=9, group='robe')
    for pts in (([(40, T(80)), (37, T(96)), (35, T(112))]), ([(90, T(80)), (94, T(96)), (96, T(110))]), ([(52, T(92)), (50, T(108))]),
                ([(78, T(92)), (81, T(108))])):
        fold(r, pts, 'robe', 0.22, 0.1)
    hood = poly_mask([(45, T(68)), (43, T(52)), (45, T(40)), (50 + hx, T(31) + hd), (56 + hx, T(26) + hd), (62 + hx, T(23) + hd),
                      (67 + hx, T(21) + hd), (71 + hx, T(24) + hd), (77, T(33)), (81, T(46)), (83, T(68))])
    region(r, hood, M['robe'], D=7, lift=0.04, group='hood')
    fold(r, [(63 + hx, T(21) + hd), (71, T(32)), (77, T(48)), (79, T(62))], 'hood', 0.24, 0.12)
    fold(r, [(52 + hx, T(30) + hd), (48, T(46)), (49, T(62))], 'hood', 0.18, 0.1)
    void = ellipse_mask(63 + hx, T(47) + hd, 9.5, 12.5) | poly_mask([(54 + hx, T(47) + hd), (72 + hx, T(47) + hd), (71 + hx, T(63)), (55 + hx, T(63))])
    region(r, void, M['void'], D=4, group='void')
    for (x, y) in void:                                                                   # the hood's rim falls into it
        if any((x + dx, y + dy) not in void for dx, dy in ((1, 0), (-1, 0), (0, -1))): r.darken(x, y, -0.25)
    if P['blink']:
        for ex in (58, 66): r.fixed(ex + hx + P['look'], T(48) + hd + 1, (90, 76, 10)); r.fixed(ex + 1 + hx + P['look'], T(48) + hd + 1, (90, 76, 10))
    else:
        for ex in (58, 66):
            x0, y0 = ex + hx + P['look'], T(47) + hd
            r.fixed(x0, y0, (255, 236, 120)); r.fixed(x0 + 1, y0, (236, 204, 60))
            r.fixed(x0, y0 + 1, (226, 192, 48)); r.fixed(x0 + 1, y0 + 1, (176, 140, 30))
            for (dx, dy) in ((-1, 0), (2, 0), (0, -1), (1, 2), (-1, 1), (2, 1)): r.darken(x0 + dx, y0 + dy, -0.35)   # glow
    scarf = poly_mask([(40, T(66)), (50, T(61)), (64, T(64)), (78, T(61)), (88, T(66)), (84, T(72)), (74, T(80)), (67, T(88)), (63, T(93)),
                       (59, T(87)), (52, T(79)), (44, T(72))])
    region(r, scarf, M['scarf'], D=4, group='scarf')
    fold(r, [(46, T(68)), (54, T(75)), (61, T(84))], 'scarf', 0.22, 0.1)
    fold(r, [(82, T(68)), (74, T(75)), (67, T(83))], 'scarf', 0.22, 0.1)
    fold(r, [(56, T(66)), (63, T(70)), (71, T(66))], 'scarf', 0.2, 0.1)
    for (x, y) in list(scarf):                                                            # a ragged fringe
        if (x, y + 1) not in scarf and h32(x, 77) % 3:
            L = 1 + h32(x, 78) % 3
            for k in range(1, L + 1): r.fixed(x, y + k, SCARFM[3 - min(2, k)] if k < L else SCARFM[1])
    # ---------------------------------------------------------------- the console: a mossy stone altar of a synth
    front = poly_mask([(19, 128), (93, 125), (91, 176), (22, 178)])
    def carve(x, y):
        v = -0.12 if y > 164 else 0
        fx = min(x - 22, 90 - x); fy = min(y - 130, 174 - y)
        if 0 <= min(fx, fy) < 1: v += 0.16                                                # the frame's lit lip
        elif 1 <= min(fx, fy) < 2: v -= 0.2                                               # its groove
        elif min(fx, fy) >= 2: v -= 0.08                                                  # the sunk panel
        return v
    region(r, front, M['stone'], D=4, group='front', vfun=carve)
    for (x0, y0) in ((76, 136), (84, 150), (74, 158)):                                    # a carved vine in relief
        for k in range(12):
            t = k / 11
            fold(r, [(x0 + 6 * math.sin(t * 5), y0 + 8 * t - 4), (x0 + 6 * math.sin((t + 0.09) * 5), y0 + 8 * (t + 0.09) - 4)], 'front', 0.18, 0.14)
    side = poly_mask([(93, 123), (101, 118), (100, 171), (91, 176)])
    region(r, side, M['stone'], D=2, lift=-0.18, group='side')
    plinth = poly_mask([(13, 177), (98, 174), (105, 170), (106, 182), (100, SOLE + 1), (13, SOLE + 1)])
    region(r, plinth, M['stone'], D=4, lift=0.04, group='plinth')
    region(r, poly_mask([(12, 120), (104, 116), (103, 124), (96, 128), (16, 131), (11, 126)]), M['stone'], D=2, lift=0.08, group='slabedge')
    top = poly_mask([(21, 101), (95, 98), (104, 116), (12, 120)])
    oid = r.new('top')
    for (x, y) in top:
        v = 0.46 + (y - 100) * 0.006 + (nB(x * 1.6, y * 1.6) - 0.5) * 0.24
        r.put(x, y, M['stone'], v, oid)
    for (x, y) in top:                                                                    # the slab's lit front edge
        if (x, y + 1) not in top: r.darken(x, y, -0.22)
    runes(r, P['led'])
    medallion(r, 52, 151, P)
    for (x, y) in ((22, 132), (88, 130), (24, 172), (88, 170)): r.fixed(x, y, SKULLG[5]); r.fixed(x + 1, y + 1, SKULLG[1])   # corner studs
    # moss on the stone
    for (x, y) in list(front | plinth):
        if nC(x * 1.3 + 40, y * 1.3) > 0.74 and h32(x, y, 81) % 3 and (y > 160 or x < 26 or x > 86):
            r.fixed(x, y, mix(VINE[3 + h32(x, y, 82) % 3], STONE[4], 0.35))
    # ---------------------------------------------------------------- arms: sleeves forward, long pale fingers on the runes
    for (sh, hand, sd) in (((45, T(76)), P['hl'], -1), ((85, T(76)), P['hr'], 1)):
        wr = (hand[0] - sd * 1, hand[1] - 6)
        E = ik(sh, wr, 18, 18, lambda e, sd=sd: e[1] * 1.0 + sd * e[0] * 0.6)
        region(r, path_mask([sh, E, lerp(E, wr, 0.5), wr], [7.6, 6.8, 7.8, 9.6]), M['robe'], D=5, group='sleeve%d' % sd)
        fold(r, [(wr[0] - 6, wr[1] + 1), (wr[0], wr[1] + 3), (wr[0] + 6, wr[1] + 1)], 'sleeve%d' % sd, 0.26, 0.12)   # the cuff's rim
        fold(r, [lerp(E, wr, 0.3), lerp(E, wr, 0.55)], 'sleeve%d' % sd, 0.2, 0.08)
        seam(r, 'sleeve%d' % sd, 0.22)
        region(r, ellipse_mask(hand[0], hand[1] - 3, 4.4, 2.8), M['finger'], D=2, group='hand%d' % sd)
        for k in range(4):                                                                # long fingers splayed onto the slab
            fx = hand[0] - 4.5 + k * 3.0
            region(r, path_mask([(fx, hand[1] - 3), (fx - 0.4 + sd * 0.3, hand[1] + 1.5), (fx - 0.6 + (k - 1.5) * 0.6, hand[1] + 4)],
                                [1.1, 1.0, 0.8]), M['finger'], D=1.0, lift=0.06 * (k % 2), group='fing%d%d' % (sd, k))
        for k in range(4):                                                                # their glow on the runes
            r.darken(hand[0] - 4.5 + k * 3.0, hand[1] + 5, -0.2)
    im = r.render()
    return recolor_outline(im, (18, 14, 12), (6, 10, 6))


RUNES = [((24, 108), 'dots'), ((30, 113), 'bar'), ((42, 104), 'hook'), ((58, 108), 'circle'), ((72, 103), 'dots'), ((76, 110), 'hook'),
         ((86, 105), 'bar'), ((91, 112), 'dots'), ((18, 115), 'bar'), ((40, 112), 'dots'), ((66, 115), 'bar'), ((50, 102), 'dots'),
         ((84, 101), 'hook'), ((30, 104), 'hook'), ((54, 115), 'hook'), ((97, 108), 'dots')]


def runes(r, led):
    """glyphs cut into the slab, glowing green; a wave of light runs across them"""
    for i, ((x, y), kind) in enumerate(RUNES):
        lv = 4 if (i - led) % 5 == 0 else 3 if (i - led) % 5 in (1, 4) else 2
        c, d = RUNE[lv], RUNE[max(0, lv - 2)]
        if kind == 'dots':
            for (dx, dy) in ((0, 0), (2, 0), (1, 1), (4, 1)): r.fixed(x + dx, y + dy, c)
        elif kind == 'bar':
            for dx in range(5): r.fixed(x + dx, y + (dx // 3), c if dx % 2 else d)
        elif kind == 'hook':
            for (dx, dy) in ((0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2)): r.fixed(x + dx, y + dy, c)
        elif kind == 'circle':
            for k in range(26):
                a = k / 26 * 2 * math.pi
                r.fixed(x + 7.5 * math.cos(a), y + 3.6 * math.sin(a), c if k % 4 else d)
            for (dx, dy) in ((-2, 1), (-1, 0), (0, 0), (1, -1), (2, -1), (0, -2), (0, 1)): r.fixed(x + dx, y + dy, c)
        for dy in range(-2, 4):                                                           # the glow spills onto the stone
            for dx in range(-2, 7):
                e = r.buf.get((int(x + dx), int(y + dy)))
                if e and e[0] is not None: e[1] += 0.05 * (lv - 1)


def medallion(r, cx, cy, P):
    """a round recess on the console's front with a horned golden skull; its eyes flash on the downbeats"""
    ring = ellipse_mask(cx, cy, 16.5, 16.5) - ellipse_mask(cx, cy, 14.5, 14.5)
    region(r, ring, M['skull'], D=1.2, lift=-0.1, group='medring')
    region(r, ellipse_mask(cx, cy, 14.5, 14.5), M['stone'], D=5, lift=-0.26, group='medin')
    for sd in (-1, 1):                                                                    # horns: up and out, then in
        pts = curve(lambda t: (cx + sd * (4 + 9 * math.sin(t * 1.7)), cy - 5 - 9 * t + 2 * t * t), 10)
        region(r, path_mask(pts, [2.4 - 1.6 * k / 10 for k in range(11)]), M['skull'], D=1.5, group='horn%d' % sd)
    skull = ellipse_mask(cx, cy - 2, 6.5, 5.5) | poly_mask([(cx - 5, cy), (cx + 5, cy), (cx + 2.5, cy + 10), (cx - 2.5, cy + 10)])
    region(r, skull, M['skull'], D=3, group='skull')
    eye = (220, 200, 70) if P['eyes'] == 1 else (250, 236, 120) if P['eyes'] == 2 else (255, 252, 200)
    for sd in (-1, 1):
        ex = cx + sd * 3 - (1 if sd < 0 else 0)
        r.fixed(ex, cy - 2, SKULLG[0]); r.fixed(ex + 1, cy - 2, SKULLG[0]); r.fixed(ex, cy - 1, eye); r.fixed(ex + 1, cy - 1, SKULLG[0])
        if P['eyes'] == 3:
            for (dx, dy) in ((0, -2), (-1, -1), (2, -1), (0, 0), (1, 0)): r.darken(ex + dx, cy - 1 + dy, -0.4)
    for y in range(int(cy) + 3, int(cy) + 9): r.darken(cx, y, 0.2)                       # the snout's ridge
    r.fixed(cx - 1, cy + 7, SKULLG[0]); r.fixed(cx + 1, cy + 7, SKULLG[0])                 # nostrils


CAST = {'telka': (telka, TELKA_IDLE, TELKA_PLAY), 'bass_xl': (bass_xl, XL_IDLE, XL_PLAY), 'karlis': (karlis, KARLIS_IDLE, KARLIS_PLAY),
        'mira': (mira, MIRA_IDLE, MIRA_PLAY)}


def write_gpl(path):
    """the band's ramps (+ outlines and glows) as an Aseprite palette for touch-ups in the UPRAVY layers"""
    ramps = [HIDE, JACK, JEANS, BOOTS, TEE, GUIT, FANG, EYERED, NECKW, BOARDW, STEEL, RUSTP, EYEY, XLS, VISOR, CREAM, GUARD,
             ROSEW, RUSTY, XLEYE, FUR, MUZ, NOSE, VESTD, TEEB, TROUK, SHELLK, HEADK, CYM, STANDK, STICKW, ROBEM, VOID, SCARFM,
             STONE, VINE, FINGER, SKULLG, RUNE]
    extra = [WARMOUT, GREENOUT, (10, 13, 14), (12, 8, 5), (6, 10, 6), INK, LOGO]
    seen, rows = set(), []
    for c in [c for rmp in ramps for c in rmp] + extra:
        c = tuple(c)
        if c in seen: continue
        seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    with open(path, 'w') as f:
        f.write('GIMP Palette\nName: feral_toast\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')


def sheet(frames, path):
    w, h = frames[0].size
    s = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, im in enumerate(frames): s.paste(im, (i * w, 0))
    s.save(path)


if __name__ == '__main__':
    only = sys.argv[2].split(',') if len(sys.argv) > 2 else list(CAST)
    for cid in only:
        fn, idle, play = CAST[cid]
        os.makedirs(f'{OUT}/{cid}', exist_ok=True)
        frames = [fn(p) for p in idle + play]
        low = max(im.getchannel('A').getbbox()[3] - 1 for im in frames)                  # the outline under the soles
        if low != SOLE:                                                                   # ends on row 189, like before
            frames = [im.transform(im.size, Image.AFFINE, (1, 0, 0, 0, 1, low - SOLE)) for im in frames]
        for i, im in enumerate(frames): im.save(f'{OUT}/{cid}/{i}.png')
        sheet(frames, f'{OUT}/{cid}.png')
    write_gpl(f'{OUT}/feral_toast.gpl')
    print('ok', OUT)
