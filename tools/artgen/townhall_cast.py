"""The Townhall cast, redrawn with the character renderer (rig.py, the Edgar quality bar) after their old AI pictures
(phor.png, townhall_clerk.png, complaint_eater.png, councilor_seraphel_dune.png, poet.png -- now only references for who
they are). Scale 1, origin bottom-centre, soles on the frame's bottom rows; 8 calm idle frames each (the scenes sequence
them with holds).

  phor      128x160, soles on y 156 -- Phor Calesta, divinographer (TownhallScene, right of the stair; GodgraveyardScene):
            a Craybara (crayfish + capybara) -- an unmistakable capybara's head in near-profile: a big blunt box with a
            flat top, a deep square muzzle with the nostrils high on its top corner, a small placid half-lidded eye set
            high and far back, small round ears, coarse reddish-brown fur, the dark morrillo gland of a grown male on
            the snout -- carried low and forward on a short thick neck inside a round diving-helmet glass dome (his home
            water lapping round the neck under the chin, a bronze neck ring),
            a brown leather fedora on the dome, a pleated ruff, a long moss-green coat with short
            sleeves, a belt with a brass buckle and a leather satchel; huge orange crayfish forearms and claws (the near
            one raised, open), one booted foot and one bare crayfish foot, a segmented tail behind. Turned to the
            viewer's left.
            0 rest  1 inhale  2 blink  3-5 a bubble rises from under his chin through the dome water and breaks (4: the
            raised claw opens wider, 5: it snips shut)  6 the tail tip flicks, the hanging claw twitches  7 exhale
  clerk     128x160, soles on y 156 -- the Townhall clerk (TownhallInteriorScene): a short, scruffy, tired bureaucrat --
            wild brown hair under a battered pillbox hat with a lit candle stuck on it (wax running down the hat), round
            brass-rimmed spectacles, a stubbled scowl, a grubby shirt and cravat, a brown waistcoat with a watch chain,
            a frayed frock coat; a black quill in his right hand, a sheaf of papers in his left. The flame flickers in
            every frame.
            0 rest  1 rest, the flame in another shape (alternate 0/1 so it keeps flickering through holds)  2 inhale
            3 blink  4-5 he looks down at the papers (two flame shapes)  6 he scratches a note (the quill on the
            sheaf)  7 the flame gutters, a thread of smoke
  eater     128x144, soles on y 141 -- the Complaint Eater (TownhallInteriorScene): a bloated, squatting toad-thing of
            mottled ochre skin with violet bruises, part plumbing -- a row of brass goggle-eyes on the brow, a smoking
            brass chimney-pipe on its head, coiled brass hoses over the shoulder and round the hip, brass joint-rings,
            a shirt collar and a red tie on the throat; one hand stuffs a complaint form into its wide mouth; clawed
            toad feet on a litter of paper.
            Play 0..7 in order (the smoke rises through the loop, the jaw chews twice):
            0 rest  1 jaw down  2 bite  3 swallow (the throat bulges)  4 the goggle lenses whirr brighter
            5 jaw down + a puff from the chimney  6 bite + the belly heaves  7 rest
  seraphel  128x192, soles on y 189 -- Councilor Seraphel Dune (TownhallInteriorScene): tall and gaunt, a pale bird-skull
            face with a long beak and dark sockets, long whisker-filaments, a tall fan-shaped headdress with a gilt
            spine and a jewel, a high teal collar, long dark layered robes with gilt pinstripes, hanging seal-tags on
            cords, a pale inner stole, long bony fingers steepled at the chest, bony bird feet with talons.
            0 rest  1 inhale  2 the whiskers drift  3 the fingertips tap  4 the head tilts  5 the seals sway  6 a
            pale glint in the sockets  7 exhale
  poet      128x144, soles on y 141 -- the Mad Poet (TownhallInteriorScene, on the reading dais; ScraperAmbra cutscene):
            wild dark hair, a ragged beard, bloodshot eyes, a red scarf, a tattered purple frock coat over a red
            waistcoat, a revolver raised beside his head (a wisp from the muzzle), an open book of poems at his chest.
            DRAWN ~15% SMALLER than the others (figure ~124 px instead of ~146) because he stands on the dais at depth
            ~17.6 (feet y 482), not on the walk line at depth 15 -- at scale 1 he reads the same real height.
            0 rest  1 inhale  2 a twitchy blink  3 the gun hand trembles  4-5 he declaims (head back, mouth open)
            6 he turns a page  7 exhale
python3 townhall_cast.py <outdir> [phor|clerk|eater|seraphel|poet ...]
  -> <id>.png (8-frame sheets) + <id>/<n>.png + townhall_cast.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK, h32
import rig
from rig import Rig, Mat, norm
from feral_toast import ik, lerp
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
R = ramp
WARM_INK = (34, 22, 17)

# ------------------------------------------------------------------------------------------------------- textures
rig.TEX['tweed'] = lambda x, y: ((rig.nF(x * 1.7, y * 1.7) - 0.5) * 0.10 + (rig.nM(x * 1.1, y * 1.1) - 0.5) * 0.16
                                 + (rig.nL(x * 0.7 + 40, y * 0.7) - 0.5) * 0.24 + (0.025 if (x + 2 * y) % 3 == 0 else -0.01))
rig.TEX['worn'] = lambda x, y: ((rig.nF(x * 1.7, y * 1.7) - 0.5) * 0.12 + (rig.nM(x * 1.1, y * 1.1) - 0.5) * 0.18
                                + (rig.nL(x * 0.7 + 40, y * 0.7) - 0.5) * 0.30 + (0.03 if (x + 2 * y) % 3 == 0 else -0.012)
                                - (0.12 if rig.nL(x * 2.3 + 90, y * 2.3) > 0.78 else 0))
rig.TEX['pelt'] = lambda x, y: ((rig.nF(x * 1.1, y * 0.45) - 0.5) * 0.22 + (rig.nM(x * 0.9, y * 0.9) - 0.5) * 0.10)
rig.TEX['shell'] = lambda x, y: ((rig.nM(x * 1.3, y * 1.3) - 0.5) * 0.14 + (rig.nF(x * 2.0, y * 2.0) - 0.5) * 0.06
                                 + (0.10 if h32(x, y, 77) % 23 == 0 else 0))                     # pitted, tubercled
rig.TEX['wart'] = lambda x, y: ((rig.nM(x * 1.6, y * 1.6) - 0.5) * 0.18 + (rig.nF(x * 1.8, y * 1.8) - 0.5) * 0.08
                                + (0.14 if h32(x // 2, y // 2, 31) % 9 == 0 else 0))
rig.TEX['felt'] = lambda x, y: (rig.nM(x * 1.6, y * 1.6) - 0.5) * 0.12 + (rig.nF(x * 2.2, y * 2.2) - 0.5) * 0.06
rig.TEX['silk'] = lambda x, y: (rig.nF(x * 0.6, y * 2.4) - 0.5) * 0.10 + (rig.nL(x, y + 17) - 0.5) * 0.06
rig.TEX['hair'] = lambda x, y: ((rig.nF(x * 1.3 + 2.0 * math.sin(y * 0.23), y * 0.25) - 0.5) * 0.40
                                + (rig.nM(x * 0.8, y * 0.8) - 0.5) * 0.08)
rig.TEX['bone'] = lambda x, y: (rig.nM(x * 1.2, y * 1.2) - 0.5) * 0.10 + (rig.nF(x * 0.5, y * 1.8) - 0.5) * 0.08


def mat(rmp, tex, amb, spec=0.0): return Mat(rmp, tex, amb, spec, outline=WARM_INK)


def mix(a, b, t): return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def group_at(r, x, y):
    e = r.buf.get((int(x), int(y)))
    return r.groups[e[2]] if e else None


def color_at(r, x, y):
    e = r.buf.get((int(x), int(y)))
    return e


def arc(p0, a0, k, L, n=6):
    """points along a curve from p0, heading a0 (radians, screen space), turning k radians per pixel, length L"""
    pts, a, (x, y), st = [p0], a0, p0, L / n
    for _ in range(n):
        a += k * st; x += math.cos(a) * st; y += math.sin(a) * st
        pts.append((x, y))
    return pts


def chain(r, pts, r0, r1, m, g, lift=0.0, folds=None):
    n = len(pts) - 1
    for i in range(n):
        r.tube(pts[i], pts[i + 1], r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n, m, lift=lift, group=g, folds=folds)


def warm_ink(im):
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y] == (18, 14, 12, 255): px[x, y] = WARM_INK + (255,)
    return im


def sheet(frames, path):
    w, h = frames[0].size
    s = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, im in enumerate(frames): s.paste(im, (i * w, 0))
    s.save(path)


# ================================================================================================= PHOR CALESTA
FUR    = R('#1a0d07 #28140b #371c10 #472515 #582f1a #693920 #7a4427 #8a4f2e #995b36 #a6683f')
MUZ    = R('#2a170e #3b2214 #4e2e1b #613b22 #73482a #845533 #93623c #a17046')
SHELLC = R('#1e0a05 #2e1007 #40170a #52200d #642a10 #763414 #883f18 #994b1d #a85823 #b6672d')
GCOAT  = R('#0e0e09 #15160f #1c1e14 #24271a #2d3020 #363927 #40422e #4a4c36 #55563f #626149')
GTROU  = R('#0e0d09 #15130d #1c1a12 #242117 #2d291d #363123 #403a2a')
RUFF   = R('#2c2214 #41341f #57472c #6d5a3a #826d4a #95805a #a6916a #b4a07a')
LEATH  = R('#150b06 #20110a #2c180e #392013 #472818 #55311e #643a24 #73442b #814f33')
BRONZE = R('#16120b #251d10 #372b16 #4a3a1d #5d4a25 #70592f #826a3b #937b4a')
VERD   = (72, 104, 84)
WATER  = (58, 104, 98)
GLASS  = (196, 222, 214)
PUPIL  = (16, 10, 8)

rig.TEX['coarse'] = lambda x, y: ((rig.nF(x * 1.6, y * 0.7) - 0.5) * 0.13 + (rig.nM(x * 0.9, y * 0.9) - 0.5) * 0.06)   # short bristly fur
MP = {'fur': mat(FUR, 'coarse', 0.2, 0.05), 'muzzle': mat(MUZ, 'coarse', 0.22, 0.05), 'shell': mat(SHELLC, 'shell', 0.2, 0.55), 'coat': mat(GCOAT, 'worn', 0.17),
      'trou': mat(GTROU, 'fabric', 0.18), 'ruff': mat(RUFF, 'fabric', 0.28), 'leather': mat(LEATH, 'leather', 0.2, 0.3),
      'hat': mat(LEATH, 'felt', 0.2, 0.08), 'brass': mat(BRONZE, 'metal', 0.24, 0.8), 'boot': mat(LEATH[:-2], 'leather', 0.18, 0.5)}

PHOR_POSE = [dict(bt=0), dict(bt=1), dict(bt=0, blink=1), dict(bt=0, bubble=1), dict(bt=0, bubble=2, snip=1),
             dict(bt=0, bubble=3, snip=-1), dict(bt=0, flick=1), dict(bt=1)]


def spikes(r, pts, side, m, g, every=2, ln=2.6, start=1):
    """little thorns along the outer edge of a carapace segment chain; side = +1/-1 normal direction"""
    for i in range(start, len(pts) - 1, every):
        (x0, y0), (x1, y1) = pts[i - 1], pts[i + 1]
        dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L * side, dx / L * side
        bx, by = pts[i]
        rr = 2.6
        r.poly([(bx + nx * rr - dx / L * 1.6, by + ny * rr - dy / L * 1.6), (bx + nx * (rr + ln) + dx / L * 1.2, by + ny * (rr + ln) + dy / L * 1.2),
                (bx + nx * rr + dx / L * 1.8, by + ny * rr + dy / L * 1.8)], m, lift=0.1, round_=0.4, group=g)


def crab_claw(r, wrist, ang, g, palm=(10.0, 7.5), fl=16.0, open_=0.5, fr=(4.2, 3.6), curl=1.0):
    """a crayfish chela from the wrist: the swollen palm along `ang`, the fixed finger (below) and the hinged one (above)
    curving toward each other; open_ = half the gap angle at the hinge"""
    m = MP['shell']
    ca, sa = math.cos(ang), math.sin(ang)
    pc = (wrist[0] + ca * palm[0] * 0.85, wrist[1] + sa * palm[0] * 0.85)
    def pv(x, y, u, w):
        v = -0.16 if w > 0.5 else 0
        if -0.55 < w < -0.15 and -0.5 < u < 0.6: v += 0.08                        # the lit ridge along the palm
        if abs(u - 0.15) < 0.05: v -= 0.1                                        # a growth line
        return v
    r.ellipsoid(pc[0], pc[1], palm[0], palm[1], m, rot=ang, group=g, vfun=pv)
    hinge = (pc[0] + ca * palm[0] * 0.78, pc[1] + sa * palm[0] * 0.78)
    fingers = []
    for side, rr in ((-1, fr[0]), (1, fr[1])):                                   # side +1 = the (-sin, cos) side
        a, turn, n = ang + side * open_, -side * (open_ * 2.0 + 0.45) * curl, 8
        wsum = sum(0.3 + (i + 0.5) / n for i in range(n))
        base = (hinge[0] - sa * side * palm[1] * 0.42, hinge[1] + ca * side * palm[1] * 0.42)
        pts, (x, y) = [base], base
        for i in range(n):                                                        # straight at the root, hooked at the tip
            a += turn * (0.3 + (i + 0.5) / n) / wsum
            x += math.cos(a) * fl / n; y += math.sin(a) * fl / n
            pts.append((x, y))
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            r.tube(pts[i], pts[i + 1], rr * (1 - t0 ** 1.3 * 0.82), rr * (1 - t1 ** 1.3 * 0.82), m, lift=0.03 if side < 0 else -0.05,
                   group=g + 'f%d' % side, folds=lambda u, sd, s=side: (0.1 if sd * s < -0.3 else 0))
        seam(r, g + 'f%d' % side, 0.26)
        fingers.append(pts)
        for i in (1, 2, 3, 4):                                                    # pale teeth on the inner edge
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy) or 1
            nx, ny = dy / L * side, -dx / L * side
            q = rr * (1 - i / n * 0.8)
            r.fixed(x0 + nx * q * 0.95, y0 + ny * q * 0.95, (176, 140, 98) if i % 2 else SHELLC[8])
        r.fixed(pts[-1][0], pts[-1][1], SHELLC[1])                                # dark tips
    for i in range(7):                                                            # tubercles on the palm's top
        t = (h32(i, 9) % 100) / 100 * 1.4 - 0.7
        d = (h32(i, 3) % 60) / 10 - 3
        r.fixed(pc[0] + ca * d * 1.4 + sa * t * palm[1] * 0.8, pc[1] + sa * d * 1.4 - ca * t * palm[1] * 0.8 - 1, SHELLC[9] if i % 2 else SHELLC[7])
    return fingers


def carapace_arm(r, a, b, ra, rb, g, outer=1, segs=4):
    """a segmented crayfish forearm a -> b with thorns on the outer side"""
    pts = [lerp(a, b, t / segs) for t in range(segs + 1)]
    for i in range(segs):
        r.tube(pts[i], pts[i + 1], ra + (rb - ra) * i / segs + 0.5, ra + (rb - ra) * (i + 1) / segs, MP['shell'], group=g,
               folds=lambda u, sd: (-0.32 if u > 0.88 else 0) + (0.12 if u < 0.3 and sd * outer < -0.2 else 0) - (0.1 if sd * outer > 0.6 else 0))
    spikes(r, [lerp(a, b, t / 8) for t in range(9)], outer, MP['shell'], g + 'sp', every=2, ln=2.4)
    return pts


def bell_sleeve(r, sh, end, r0, r1, g, lift=0.0, m=None):
    """a wide, three-quarter coat sleeve flaring from the shoulder to a ragged cuff: long creases, a bend crease"""
    m = m or MP['coat']
    def folds(u, sd):
        v = 0.0
        if u > 0.25 and (abs(sd - 0.35) < 0.09 or abs(sd + 0.2) < 0.08): v -= 0.26          # long drapes
        if u > 0.25 and (abs(sd - 0.5) < 0.1 or abs(sd + 0.05) < 0.08): v += 0.08
        if 0.56 < u < 0.62 and abs(sd) < 0.7: v -= 0.2                                   # the bend
        if sd < -0.55: v += 0.1
        return v
    r.ellipsoid(sh[0], sh[1] + 1.5, r0 + 0.6, r0, m, lift=lift, group=g)               # the shoulder's cap under the cloth
    r.tube(sh, end, r0, r1, m, lift=lift, group=g, folds=folds)
    seam(r, g, 0.24)
    dx, dy = end[0] - sh[0], end[1] - sh[1]; L_ = math.hypot(dx, dy) or 1
    nx, ny = -dy / L_, dx / L_
    for k in range(-4, 5):                                                              # the cuff frays
        t = k / 4.4
        x, y = end[0] + nx * r1 * t + dx / L_ * (r1 * 0.15), end[1] + ny * r1 * t + dy / L_ * (r1 * 0.15)
        if h32(k, int(sh[0])) % 3: r.fixed(x + dx / L_, y + dy / L_, GCOAT[1])
        r.darken(x, y, 0.18)


def boxy(r, cx, cy, rx, ry, p, m, lift=0.0, group=None, vfun=None, rot=0.0, zk=1.2):
    """a superellipsoid (|u|^p + |w|^p <= 1): a rounded box -- flat faces, softly rounded edges and corners"""
    oid = r.new(group)
    c, s = math.cos(rot), math.sin(rot)
    R = max(rx, ry) * 1.1 + 2
    for y in range(int(cy - R), int(cy + R) + 1):
        for x in range(int(cx - R), int(cx + R) + 1):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            u, w = (dx * c + dy * s) / rx, (-dx * s + dy * c) / ry
            f = abs(u) ** p + abs(w) ** p
            if f > 1: continue
            z = (1 - f) ** (1 / p)
            gu, gw = math.copysign(abs(u) ** (p - 1), u), math.copysign(abs(w) ** (p - 1), w)
            n = norm((gu * c - gw * s, gu * s + gw * c, z * zk))
            v = r.shade(m, n, lift) + (vfun(x, y, u, w) if vfun else 0)
            r.put(x, y, m, v, oid)
    return oid


def phor_head(r, hx, hy, P):
    """a capybara's head in near-profile, facing the viewer's left (hx, hy = the head's middle): one big blunt box --
    a flat top running almost level from the ears to the nose, a deep, square, heavy muzzle (a touch lighter) squared
    off at the front, the nostrils high on its top corner, the small mouth low at its front; the heavy cheek under a
    small round eye set high and far back, small round ears high on the skull, coarse short reddish-brown fur; calm and
    half-lidded. It sits inside the dome with clear glass round it, so its silhouette reads against the glass."""
    blink = P.get('blink')
    fur = MP['fur']
    coarse = lambda x, y, u, w: (-0.08 if h32(x, y >> 1, 61) % 11 == 0 else 0) + (0.05 if h32(x, y, 62) % 13 == 0 else 0)
    top = hy - 7.0                                                                       # the flat top line
    # the short, thick neck: as wide as the back half of the head, rising out of the collar ring (clipped at the ring
    # so it never spills over the ruff) straight into the back and underside of the skull -- solid fur, no glass between
    neck_v = lambda u, sd: (-0.14 if sd > 0.55 else 0) + (0.06 if sd < -0.5 else 0) + (-0.1 if (int(u * 14) + int(sd * 3)) % 4 == 0 else 0)
    r.tube((hx + 4.5, hy + 1.5), (hx + 2.5, hy + 17.5), 7.8, 8.4, fur, group='pneck', folds=neck_v, clip=lambda x, y: y <= hy + 16.5)
    r.ellipsoid(hx + 0.5, hy + 6.8, 6.4, 4.2, fur, lift=-0.05, group='pneck')                        # the throat under the jaw
    r.ellipsoid(hx + 9.0, top + 0.6, 1.9, 1.9, fur, lift=-0.24, group='pearF')                       # the far ear
    boxy(r, hx + 1.0, hy - 0.5, 10.6, 6.5, 3.4, fur, lift=0.05, group='pskull', rot=-0.03,
         vfun=lambda x, y, u, w: coarse(x, y, u, w) + (0.05 if w < -0.55 else 0) - (0.1 if u > 0.72 else 0) - max(0.0, w - 0.2) * 0.2)
    boxy(r, hx - 7.4, hy + 1.0, 5.7, 7.6, 5.0, MP['muzzle'], lift=0.1, group='psnout', rot=-0.03,
         vfun=lambda x, y, u, w: coarse(x, y, u, w) * 0.7 - max(0.0, w - 0.35) * 0.3 + (0.05 if w < -0.6 else 0))   # deep and square
    r.ellipsoid(hx + 1.5, hy + 3.6, 6.6, 3.7, fur, lift=-0.06, group='pjaw', vfun=coarse)            # the heavy cheek
    # the near ear: small and round, high at the back of the skull, dark inside
    ax, ay = hx + 6.6, top + 0.4
    r.ellipsoid(ax, ay, 2.5, 2.3, fur, lift=0.04, group='pear')
    for (x, y, c) in ((ax - 0.5, ay + 0.5, FUR[1]), (ax + 0.5, ay + 0.5, FUR[2]), (ax - 0.5, ay - 0.5, FUR[3]), (ax - 1.5, ay - 1.5, FUR[8])):
        r.fixed(x, y, c)
    fx = hx - 13.1                                                                      # the muzzle's blunt front
    # the nostrils: dark slits high on the top corner of the muzzle (the far one a dot), the nose's top lit
    for (dx, dy, c) in ((0.6, -5.5, FUR[0]), (0.6, -6.5, FUR[0]), (1.6, -6.8, FUR[0]), (2.6, -7.0, FUR[1]), (1.6, -5.8, FUR[2]),
                        (4.6, -7.2, FUR[1]), (5.4, -7.2, FUR[2])):
        r.fixed(fx + dx, hy + dy, c)
    # the morrillo: the dark, bare scent gland a grown male capybara carries on top of his snout
    for (dx, c) in ((7.6, FUR[1]), (8.6, FUR[0]), (9.6, FUR[0]), (10.6, FUR[1]), (11.6, FUR[2])):
        r.fixed(fx + dx, top + 0.2 + (dx - 7.6) * 0.03, c)
    for (dx, c) in ((8.6, FUR[2]), (9.6, FUR[3]), (10.6, FUR[2])):
        r.fixed(fx + dx, top + 1.2, c)
    r.fixed(fx + 9.6, top - 0.6, FUR[4])
    r.fixed(fx + 2.6, hy - 7.6, MUZ[7]); r.fixed(fx + 0.6, hy - 7.4, MUZ[6])
    # the cleft lip down the blunt front, the small mouth low on it, the crease of the chin
    for k in range(4): r.fixed(fx + 0.6, hy - 4.5 + k, MUZ[2] if k < 3 else MUZ[1])
    for dx in range(0, 4): r.fixed(fx + 0.6 + dx, hy + 4.5 + (1 if dx > 1 else 0), MUZ[0])
    r.fixed(fx + 1.6, hy + 5.5, MUZ[5])
    for dx in range(4, 10): r.fixed(fx + dx, hy + 8.0, MUZ[1])
    for (dx, dy) in ((3, -3), (5, -2), (4, -0.5), (6, -0.5)): r.fixed(fx + dx, hy + dy, MUZ[3])   # whisker pores
    for k in range(3): r.fixed(fx - 0.4 - k, hy - 1 + k * 0.6, (52, 36, 26))                     # a sparse whisker
    for k in range(9):                                                                  # the long lip line: from the mouth
        x, y = fx + 2 + k * 1.1, hy + 5.2 - k * 0.45                                    # corner back under the cheek
        r.darken(x, y, 0.16); r.darken(x, y + 1, -0.06)
    # the eye: small, round, set high and far back; the heavy lid half down -- placid
    ex, ey = int(hx + 1), int(hy - 4)
    if blink:
        for dx in range(-1, 2): r.fixed(ex + dx, ey + 1, FUR[1])
        r.fixed(ex, ey, FUR[5])
    else:
        for dx in range(-1, 2): r.fixed(ex + dx, ey, FUR[1])                                      # the lid's lash line
        r.fixed(ex - 1, ey + 1, (196, 184, 162)); r.fixed(ex, ey + 1, PUPIL); r.fixed(ex + 1, ey + 1, (30, 18, 12))
        r.fixed(ex, ey + 2, (36, 22, 15))
    r.fixed(ex - 1, ey + 2, FUR[6]); r.fixed(ex - 1, ey + 3, FUR[7]); r.fixed(ex, ey + 3, FUR[7]); r.fixed(ex + 1, ey + 2, FUR[3])
    r.fixed(ex - 1, ey - 1, FUR[8]); r.fixed(ex, ey - 1, FUR[8]); r.fixed(ex + 1, ey - 1, FUR[7])   # the brow ridge
    # coarse fur catching the light along the flat top
    for x in range(int(hx - 13), int(hx + 9), 2):
        if h32(x, 3) % 3: r.fixed(x, int(top + 0.8 + (x - hx) * 0.03), FUR[9] if x < hx else FUR[8])


def phor(P):
    W, H, FL = 128, 160, 156
    r = Rig(W, H)
    bt = P['bt']
    U = lambda y: y - bt                                       # the upper body breathes
    fl = P.get('flick', 0)
    # ------------------------------------------------------------------------------------- the tail (behind everything)
    tl = arc((90, 124), 0.35, 0.03, 22, 6)
    tl += arc(tl[-1], 0.35 + 0.03 * 22, -0.2 - 0.12 * fl, 8 + fl, 3)[1:]
    n = len(tl) - 1
    for i in range(n):
        r.tube(tl[i], tl[i + 1], 6.4 - i * 0.55, 6.4 - (i + 1) * 0.55, MP['shell'], lift=-0.16, group='tail',
               folds=lambda u, sd: (-0.3 if u > 0.85 else 0) + (0.12 if sd < -0.4 else 0))
    for i in range(1, n):
        x, y = tl[i]
        r.fixed(x - 1, y - 4.2 + i * 0.35, SHELLC[7]); r.fixed(x, y - 4.2 + i * 0.35, SHELLC[6])
    tp = tl[-1]
    for (dx, dy) in ((1, -2), (2, -1), (2, 0), (1, 1), (2, 2)):                    # a fan of tail-plates at the tip
        r.fixed(tp[0] + dx, tp[1] + dy, SHELLC[5] if dy < 1 else SHELLC[3])
    # ------------------------------------------------------------------------------------- legs: a wide, crouched stance
    near_hip, near_knee, near_ank = (56, 110), (44, 127), (40, 146)
    far_hip, far_knee, far_ank = (78, 112), (87, 130), (92, 146)
    r.tube(far_hip, far_knee, 8.4, 7.2, MP['trou'], lift=-0.08, group='legF',
           folds=lambda u, sd: (-0.24 if abs(sd - 0.2) < 0.1 and u > 0.3 else 0))
    r.tube(far_knee, far_ank, 7.2, 5.4, MP['trou'], lift=-0.08, group='legF',
           folds=lambda u, sd: (-0.24 if (0.55 < u < 0.61 or 0.8 < u < 0.85) and abs(sd) < 0.8 else 0) + (0.08 if u > 0.9 else 0))
    for x in range(int(far_ank[0] - 5), int(far_ank[0] + 6)):                         # the ragged trouser end
        if h32(x, 4) % 3: r.darken(x, far_ank[1] + 3, 0.2)
    r.ellipsoid(far_ank[0], far_ank[1] + 4, 5.0, 4.0, MP['shell'], group='footF')                 # the ankle joint
    for k, (a, ln, rr) in enumerate(((math.pi * 0.97, 8.0, 3.0), (math.pi * 0.72, 6.0, 2.8), (math.pi * 0.12, 6.5, 2.6))):
        base = (far_ank[0] + math.cos(a) * 3, far_ank[1] + 6.5)
        pts = arc(base, a, 0.05 if k == 0 else -0.05, ln, 4)
        pts = [(x, min(y, FL - 1.6)) for (x, y) in pts]
        chain(r, pts, rr, 0.7, MP['shell'], 'toeF%d' % k, lift=0.02 - 0.06 * (k == 1))
        seam(r, 'toeF%d' % k, 0.22)
    seam(r, 'footF', 0.2)
    r.tube(near_hip, near_knee, 8.8, 7.6, MP['trou'], group='legN',
           folds=lambda u, sd: (-0.24 if abs(sd + 0.15) < 0.1 and u > 0.25 else 0) + (0.1 if sd < -0.5 else 0))
    r.tube(near_knee, near_ank, 7.6, 6.0, MP['trou'], group='legN',
           folds=lambda u, sd: (-0.26 if (0.5 < u < 0.56 or 0.72 < u < 0.77) and abs(sd) < 0.8 else 0) + (0.1 if sd < -0.5 else 0))
    r.ellipsoid(near_knee[0] - 0.5, near_knee[1], 7.4, 6.4, MP['trou'], lift=0.1, group='legN')
    seam(r, 'legN', 0.2)
    bx = near_ank[0]
    r.tube((near_ank[0] + 0.5, near_ank[1] - 4), (near_ank[0], FL - 5), 6.4, 6.2, MP['boot'], group='bootN',
           folds=lambda u, sd: (-0.24 if 0.12 < u < 0.22 else 0) + (0.1 if sd < -0.5 else 0))
    r.poly([(bx - 14.5, FL - 6.5), (bx - 4, FL - 9.5), (bx + 6.5, FL - 8.5), (bx + 7.5, FL - 1.0), (bx + 6.5, FL), (bx - 15.5, FL),
            (bx - 16.5, FL - 3.0)], MP['boot'], round_=0.6, tilt=-0.5, group='bootN',
           vfun=lambda x, y: (0.2 if y <= FL - 7 else 0) - (0.26 if y >= FL - 1 else 0))
    for x in range(int(bx - 16), int(bx + 7)): r.fixed(x, FL, LEATH[0])
    for (dx, c) in ((-13, LEATH[8]), (-12, LEATH[7]), (-11, LEATH[6])): r.fixed(bx + dx, FL - 6, c)   # the scuffed toe cap
    r.fixed(bx - 14, FL - 5, LEATH[6])
    for k in range(3): r.fixed(bx - 3 + k * 2, FL - 9 + (k % 2), LEATH[2])                             # lacing
    # ------------------------------------------------------------------------------------- the coat
    def coat_v(x, y):
        v = 0.0
        for (fx, fy, sl) in ((49, 102, -0.30), (57, 108, -0.12), (82, 102, 0.22), (90, 110, 0.38), (72, 112, 0.05)):
            if y < fy: continue
            px = fx + (y - fy) * sl
            d = x + 0.5 - px
            if -0.5 <= d < 0.5: v -= 0.3
            elif 0.5 <= d < 1.5: v += 0.12
        if y > 124: v -= (y - 124) * 0.018                                        # the hem dark with damp and graveyard dirt
        if U(74) < y < U(95): v += 0.10 * max(0.0, 1 - abs(x - 60) / 13) - (0.12 if y < U(78) and 52 < x < 76 else 0)   # chest; under the ruff
        if U(80) < y < U(95) and (x - 70 + (y - U(80)) * 0.5) % 9 == 0: v -= 0.18           # pulls toward the belt
        v -= max(0, x - 78) * 0.009
        if rig.nM(x * 1.3 + 50, y * 1.3) > 0.68: v -= 0.1                             # blotchy wear, damp patches
        for (sx_, sy, sr) in ((86, 120, 2.2), (60, 90, 1.8), (48, 128, 2.0)):        # old stains
            if (x - sx_) ** 2 + ((y - sy) * 1.3) ** 2 < sr * sr: v -= 0.12
        return v
    coat = [(46, U(72)), (64, U(68)), (84, U(70)), (95, U(78)), (97, U(96)), (98, 110), (102, 124), (104, 136), (92, 139), (78, 136),
            (66, 139), (60, 133), (52, 128), (42, 127), (40, 112), (40, U(96)), (40, U(82))]
    r.poly(coat, MP['coat'], round_=0.85, group='coat', vfun=coat_v)
    for (x, y) in ((44, 128), (50, 129), (70, 139), (84, 138), (96, 139), (101, 137)):                 # a frayed hem
        r.fixed(x, y, GCOAT[1]); r.fixed(x + 1, y + 1, GCOAT[2])
    for y in range(110, 138):                                                     # the split at the front
        x = 64 + (y - 110) * 0.05
        r.darken(x, y, 0.32); r.darken(x + 1, y, -0.12)
    # belt + bronze buckle + the satchel on the hip
    belt = [(40, U(96)), (97, U(97)), (97.5, U(101.5)), (40.5, U(100.5))]
    r.poly(belt, MP['leather'], round_=0.9, group='belt', vfun=lambda x, y: (-0.12 if y >= U(100) else 0) + (0.1 if y <= U(96) else 0))
    bkx, bky = 56, U(95)
    for dx in range(0, 7):
        for dy in range(0, 6):
            if dx in (0, 6) or dy in (0, 5):
                r.fixed(bkx + dx, bky + dy, BRONZE[7] if (dx < 3 and dy < 2) else (BRONZE[3] if dy > 3 or dx > 4 else BRONZE[5]))
    r.fixed(bkx + 3, bky + 2, BRONZE[2]); r.fixed(bkx + 3, bky + 3, BRONZE[2]); r.fixed(bkx + 4, bky + 2, LEATH[1])
    r.tube((84, U(101)), (85, U(106)), 1.1, 1.1, MP['leather'], group='strap')
    r.ellipsoid(86, U(112), 8.2, 7.0, MP['leather'], group='satchel',
                vfun=lambda x, y, u, w: (-0.16 if w > 0.5 else 0) + (-0.16 if (x * 2 + y) % 9 == 0 else 0))
    r.poly([(78, U(105)), (94, U(105.5)), (93, U(111)), (86, U(113)), (79, U(111))], MP['leather'], lift=0.14, round_=0.6, group='flap',
           vfun=lambda x, y: -0.14 if y >= U(111) else 0)
    seam(r, 'flap', 0.28)
    r.fixed(86, U(112), BRONZE[7]); r.fixed(86, U(113), BRONZE[3])
    for (x, y) in ((80, U(106)), (83, U(106)), (88, U(106)), (91, U(106))): r.fixed(x, y, LEATH[2])   # the flap's stitching
    # ------------------------------------------------------------------------------------- the far arm: the claw hangs at his side
    shF = (88, U(75))
    elF = (97, U(96))
    wrF = (101, U(108))
    carapace_arm(r, lerp(shF, elF, 0.7), wrF, 5.4, 5.0, 'armF', outer=-1, segs=3)
    bell_sleeve(r, shF, lerp(shF, elF, 0.9), 6.8, 9.0, 'slvF', lift=-0.04)
    twitch = 0.16 if fl else 0.0
    crab_claw(r, wrF, math.pi * 0.6 + twitch, 'clawF', palm=(10.5, 7.8), fl=15.0, open_=0.5, fr=(3.9, 3.5))
    # ------------------------------------------------------------------------------------- the ruff, the neck ring, the head
    r.ellipsoid(63, U(70), 17.0, 6.0, MP['ruff'], group='ruff',
                vfun=lambda x, y, u, w: (-0.3 if (x * 2 + int(abs(w) * 3)) % 5 == 0 else 0) + (0.08 if w < -0.3 else 0))
    for k in range(11):                                                           # the pleats' scalloped lower edge
        x = 47.5 + k * 3.2
        r.fixed(x, U(75) + (1 if k % 2 else 0) - (1 if k in (0, 10) else 0), RUFF[1])
    hx, hy = 61, U(50.5)                                                       # low and forward on the neck
    phor_head(r, hx, hy, P)
    r.ellipsoid(59, U(66), 15.5, 3.6, MP['brass'], group='ring',
                vfun=lambda x, y, u, w: (-0.28 if w > 0.3 else 0) + (0.16 if w < -0.4 else 0))
    for k in range(8):                                                            # rivets on the neck ring
        x = 46.5 + k * 3.6
        r.fixed(x, U(66), BRONZE[7] if k < 4 else BRONZE[5]); r.fixed(x, U(67), BRONZE[2])
    for (x, y) in ((50, U(68)), (51, U(68)), (63, U(68)), (70, U(68))): r.fixed(x, y, VERD)           # verdigris
    # ------------------------------------------------------------------------------------- the fedora on the dome
    DCX, DCY, DR = 58.5, U(50.0), 16.6
    hbx, hby = 59.0, U(34.5)
    r.ellipsoid(hbx + 0.5, hby, 20.5, 3.8, MP['hat'], lift=-0.06, group='brim',
                vfun=lambda x, y, u, w: (0.12 if w < -0.3 else -0.14 if w > 0.5 else 0) + (-0.18 if abs(u) > 0.9 else 0))
    crown = [(hbx - 11.0, hby - 0.5), (hbx - 10.5, hby - 7), (hbx - 8.5, hby - 12.0), (hbx - 3, hby - 13.6), (hbx + 3, hby - 14.0),
             (hbx + 8.0, hby - 12.5), (hbx + 10.6, hby - 7.5), (hbx + 11.3, hby - 0.5)]
    r.poly(crown, MP['hat'], round_=0.9, group='crown',
           vfun=lambda x, y: (-0.28 if abs(x + 0.5 - hbx) < 1.0 and y < hby - 7 else 0) + (-0.06 if y < hby - 10 else 0)
           + (0.08 if x < hbx - 4 and y < hby - 6 else 0))
    r.poly([(hbx - 11.1, hby - 4.4), (hbx + 11.4, hby - 4.4), (hbx + 11.4, hby - 1.2), (hbx - 11.1, hby - 1.2)],
           mat(R('#0f0907 #1a110c #261a13 #33241a #40301f'), 'fabric', 0.22), round_=0.9, group='band')
    r.poly([(hbx - 19.5, hby + 0.8), (hbx + 20, hby + 0.8), (hbx + 16, hby + 3.6), (hbx - 15, hby + 3.6)], MP['hat'], lift=0.06,
           round_=0.6, tilt=-0.5, group='brimF', vfun=lambda x, y: -0.16 if y >= hby + 3 else 0.04)
    for x in range(int(hbx - 15), int(hbx + 16)):
        if h32(x, 11) % 5 == 0: r.darken(x, hby + 2, 0.12)
    r.fixed(hbx + 6, hby - 3, (120, 112, 86)); r.fixed(hbx + 7, hby - 4, (96, 90, 70))                  # a dry feather-stub in the band
    # ------------------------------------------------------------------------------------- the near arm: the claw raised, open
    shN = (50, U(76))
    elN = (46, U(99))                                                             # the elbow hangs at his side
    wrN = (33, U(92))
    r.ellipsoid(elN[0], elN[1] - 0.5, 5.8, 5.4, MP['shell'], group='armN')         # the elbow joint, carapace
    carapace_arm(r, elN, wrN, 5.6, 5.0, 'armN', outer=1, segs=3)
    bell_sleeve(r, shN, lerp(shN, elN, 0.8), 7.0, 9.4, 'slvN', lift=0.1)
    seam(r, 'slvN', 0.3)
    for y in range(int(shN[1]) - 4, int(elN[1]) - 2):                             # the sleeve's lit outer edge
        xs = [x for x in range(20, 70) if group_at(r, x, y) == 'slvN']
        if xs: r.darken(min(xs), y, -0.16); r.darken(min(xs) + 1, y, -0.08)
    sn = P.get('snip', 0)
    op = 0.85 + (0.16 if sn > 0 else -0.45 if sn < 0 else 0.0)
    crab_claw(r, wrN, math.pi * 1.06, 'clawN', palm=(11.0, 8.4), fl=17.0, open_=op, fr=(4.6, 4.0), curl=0.9)
    seam(r, 'armN', 0.2)
    # ------------------------------------------------------------------------------------- render, then the glass dome
    inside = {}
    for y in range(int(DCY - DR) - 1, int(DCY + DR) + 2):
        for x in range(int(DCX - DR) - 1, int(DCX + DR) + 2):
            d = math.hypot(x + 0.5 - DCX, (y + 0.5 - DCY) * 1.02)
            if d <= DR: inside[(x, y)] = d
    over = {'brim', 'brimF', 'crown', 'band', 'ring', 'ruff', 'clawN', 'clawNf-1', 'clawNf1', 'armN', 'armNsp', 'slvN'}
    behind = {(x, y) for (x, y) in inside if group_at(r, x, y) in over}
    im = warm_ink(r.render())
    px = im.load()
    wl = int(U(60))                                                               # the water line: laps round his neck
    for (x, y), d in inside.items():
        if (x, y) in behind or not (0 <= x < W and 0 <= y < H): continue
        c = px[x, y]
        e = d / DR
        under = y > wl
        if c[3] == 0:                                                              # empty glass (the street shows through)
            if under: px[x, y] = mix(WATER, (34, 62, 60), e * 0.7) + (int(110 + 80 * e),)
            else: px[x, y] = mix(GLASS, (120, 150, 146), e) + (int(24 + 96 * e ** 3),)
        else:                                                                      # the head behind the glass
            col = c[:3]
            col = mix(col, WATER, 0.28) if under else mix(col, GLASS, 0.05)
            px[x, y] = col + (255,)
    for x in range(int(DCX - DR), int(DCX + DR) + 1):                              # the meniscus
        if (x, wl) in inside and (x, wl) not in behind:
            c = px[x, wl]
            px[x, wl] = mix(c[:3], (170, 208, 198), 0.5) + (max(c[3], 180),)
    if P.get('bubble'):                                                            # a bubble from under his chin rises
        bx_, by_ = {1: (53.0, U(65)), 2: (53.5, U(62)), 3: (53.5, wl)}[P['bubble']]
        dots = ((0, -1, (214, 236, 228)), (-1, 0, (150, 190, 184)), (1, 0, (110, 150, 146)), (0, 1, (110, 150, 146)), (0, 0, (176, 214, 204)))
        if P['bubble'] == 3: dots = ((-1, 0, (206, 230, 222)), (1, 0, (206, 230, 222)), (0, -1, (226, 242, 236)))   # it breaks
        for (dx, dy, c) in dots:
            x, y = int(bx_ + dx), int(by_ + dy)
            if (x, y) in inside and (x, y) not in behind: px[x, y] = c + (235,)
    for (x, y), d in inside.items():                                               # the rim: dark round the edge, lit top-left
        if (x, y) in behind: continue
        if d > DR - 1.0:
            a = math.atan2(y + 0.5 - DCY, x + 0.5 - DCX)
            lit = -2.6 < a < -1.2
            px[x, y] = ((150, 176, 168) if lit else (46, 58, 54)) + (235 if lit else 255,)
    for (x, y), d in inside.items():
        if (x, y) in behind: continue
        a = math.atan2(y + 0.5 - DCY, x + 0.5 - DCX)
        if DR - 3.4 < d <= DR - 1.7 and -2.6 < a < -1.8: px[x, y] = (236, 244, 236, 235)          # the sky's window
        elif DR - 3.0 < d <= DR - 2.0 and 0.25 < a < 0.95: px[x, y] = (146, 192, 182, 210)        # a reflection low right
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))                                      # 4 px right: the raised claw clears the edge
    out.paste(im.crop((0, 0, W - 4, H)), (4, 0))
    return out


# ================================================================================================ SHARED: PEOPLE
GOLD   = R('#2a1c09 #463210 #6a4e1a #8e6c25 #b08a35 #cfab52 #e8cc84')
PAPER  = R('#4c4636 #665f4b #807862 #998f77 #ada48a #beb59b #ccc4ab')
FLAME  = [(110, 44, 14), (176, 86, 26), (226, 146, 50), (248, 198, 98), (255, 236, 176), (255, 250, 228)]
EYEW   = (200, 188, 168)
INKC   = (44, 28, 22)


def face(r, hx, ey, SK, rx=9.4, ry=11.5, turn=-1, jaw=0.5, sockets=0.14, lightx=0.0):
    """a hand-pixelled face (the Ortolan method: clean shading bands that read at 1x). (hx, ey) = the face's axis and the
    eye row; turn = -1: turned a little to the viewer's left (the far cheek shows more, the features shift)"""
    L = rig.norm((-0.5 + lightx, -0.65, 0.6))
    cy = ey - 1.5
    pix = {}
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(hx - rx) - 2, int(hx + rx) + 2):
            u, w = (x + 0.5 - hx) / rx, (y + 0.5 - cy) / ry
            if w > 0.25: u /= max(0.4, 1 - (w - 0.25) * jaw)
            d = u * u + w * w
            if d > 1: continue
            uu = u - turn * 0.2
            n = (uu * 0.9, w * 0.9, math.sqrt(max(0.05, 1 - min(1, uu * uu + w * w) * 0.82)))
            v = 0.16 + 0.84 * max(0.0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2])
            dx, dy = x + 0.5 - (hx + turn), y - ey
            for sx in (-1, 1):
                if abs(dx - sx * 4.2) <= 3.0 and -2 <= dy <= 1: v -= sockets if dy < 0 else sockets * 0.4
            if abs(dx) >= 7 and -6 <= dy <= -1: v -= 0.06
            pix[(x, y)] = v
    oid = r.new('face')
    n = len(SK)
    for (x, y), v in pix.items():
        r.fixed(x, y, SK[max(1, min(n - 1, 1 + int(v * (n - 1.6))))], oid)
    return pix


def round_specs(r, cxs, ey, rim, hi, lo, tint, rad=3.3, glint=False):
    """round wire spectacles: the lenses tint what is behind them, a lit arc and a shadowed arc on each rim"""
    for cx in cxs:
        for y in range(int(ey - rad) - 2, int(ey + rad) + 3):
            for x in range(int(cx - rad) - 2, int(cx + rad) + 3):
                d = math.hypot(x + 0.5 - cx, y + 0.5 - (ey + 0.5))
                e = r.buf.get((x, y))
                if d <= rad - 0.5 and e is not None and e[3] is not None:
                    c = mix(e[3], tint, 0.18)
                    if x + 0.5 < cx and y < ey: c = mix(c, (255, 248, 226), 0.1)
                    e[3] = c
                elif rad - 0.5 < d <= rad + 0.45:
                    a = math.atan2(y + 0.5 - (ey + 0.5), x + 0.5 - cx)
                    r.fixed(x, y, hi if -2.6 < a < -1.0 else (lo if 0.3 < a < 2.6 else rim))
        gx, gy = int(cx) - 1, ey - 1
        r.fixed(gx, gy, (255, 246, 222) if glint else mix(r.buf[(gx, gy)][3] or tint, (255, 246, 222), 0.45))
        if glint: r.fixed(gx + 1, gy + 1, (236, 222, 190)); r.fixed(gx - 1, gy + 2, (220, 206, 176))


def flame_px(px, W, H, bx, by, k):
    """a small candle flame drawn straight onto the image (no outline): base (bx, by), shape k 0..4 (4 = guttering)"""
    shapes = [
        ["..1..", ".121.", ".232.", "12421", "13531", ".242.", "..1.."],
        ["...1.", "..12.", ".232.", ".243.", "13531", ".242.", "..1.."],
        [".1...", ".21..", ".232.", "1243.", "13531", ".242.", "..1.."],
        ["..1..", "..2..", ".131.", ".242.", "13431", ".242.", "..1.."],
        [".....", ".....", "...1.", "..21.", ".1321", ".242.", "..1.."],
    ]
    rows = shapes[k]
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == '.': continue
            x, y = bx - 2 + i, by - len(rows) + 1 + j
            if 0 <= x < W and 0 <= y < H: px[x, y] = FLAME[int(ch)] + (255,)


def warm_light(px, W, H, lx, ly, rad, gain):
    """warms whatever is near a flame"""
    for y in range(max(0, int(ly - rad)), min(H, int(ly + rad) + 1)):
        for x in range(max(0, int(lx - rad)), min(W, int(lx + rad) + 1)):
            c = px[x, y]
            if c[3] < 255: continue
            d = math.hypot(x - lx, (y - ly) * 1.1) / rad
            if d >= 1: continue
            t = gain * (1 - d) ** 1.6
            px[x, y] = mix(c[:3], (255, 196, 110), t) + (255,)


def boot(r, ank, FL, d, m, g, ramp_):
    """a worn boot: the shaft from the ankle, the foot pointing d (-1 viewer-left / +1 right)"""
    bx = ank[0]
    r.tube((ank[0], ank[1] - 3), (ank[0], FL - 5), 5.6, 5.4, m, group=g, folds=lambda u, sd: (-0.24 if 0.15 < u < 0.25 else 0) + (0.1 if sd < -0.5 else 0))
    r.poly([(bx - d * 6.5, FL - 8.5), (bx + d * 3.5, FL - 9), (bx + d * 9.5, FL - 5.5), (bx + d * 11.5, FL - 2), (bx + d * 10.5, FL), (bx - d * 7, FL)],
           m, round_=0.6, tilt=-0.5, group=g, vfun=lambda x, y: (0.2 if y <= FL - 7 else 0) - (0.26 if y >= FL - 1 else 0))
    for x in range(int(min(bx - d * 7, bx + d * 11)), int(max(bx - d * 7, bx + d * 11)) + 1): r.fixed(x, FL, ramp_[0])
    r.fixed(bx + d * 8, FL - 5, ramp_[-1]); r.fixed(bx + d * 9, FL - 4, ramp_[-2])
    seam(r, g, 0.2)


def ragged(x0, x1, y, depth, seed, step=2.0):
    """a ragged hem line from x0 to x1 (polygon points along the bottom, left to right)"""
    pts, x = [], x0
    while x <= x1:
        k = h32(int(x * 3), seed) % 7
        pts.append((x, y + (depth if k == 0 else depth * 0.5 if k < 3 else 0) + (h32(int(x), seed + 1) % 3) * 0.4))
        x += step
    return pts


# ============================================================================================= THE TOWNHALL CLERK
CSKIN  = R('#3a2218 #553222 #6e432e #86563b #9c694a #b07c5a #c08f6c #cda07e #d8b291')
CHAIR  = R('#160f0a #22170f #2f2015 #3d2a1b #4b3421 #5a3e28 #6a4930 #7a5539')
CHAT   = R('#0d0a08 #15100c #1e1711 #281f17 #33281e #3e3125 #4a3a2c')
WAX    = R('#4e4030 #6e5e44 #8e7e5e #ab9b78 #c6b792 #dbcfaa #e9e0c2')
CSHIRT = R('#2e2a20 #464031 #5f5743 #776e56 #8d8369 #a0967b #b1a78c')
CVEST  = R('#130b07 #1d110a #28180f #332015 #3f281a #4b3020 #573927 #634330')
CCOAT  = R('#120c08 #1b120c #251911 #302117 #3b291d #473124 #533a2a #604431 #6c4e39 #785840')
CTROU  = R('#0e0c0a #161310 #1e1a16 #27221c #302a23 #3a332a #443c31')
QUILL  = R('#0b0b0d #141417 #1d1d21 #27272c #323238 #3e3e45 #4c4c54 #5c5c64')

MC = {'skin': mat(CSKIN, 'skin', 0.28, 0.12), 'hair': mat(CHAIR, 'hair', 0.24, 0.05), 'hat': mat(CHAT, 'felt', 0.2, 0.06),
      'wax': mat(WAX, 'plain', 0.4, 0.3), 'shirt': mat(CSHIRT, 'fabric', 0.24), 'vest': mat(CVEST, 'fabric', 0.2, 0.08),
      'coat': mat(CCOAT, 'worn', 0.17), 'trou': mat(CTROU, 'fabric', 0.18), 'boot': mat(LEATH[:-2], 'leather', 0.18, 0.5),
      'paper': mat(PAPER, 'plain', 0.42), 'quill': mat(QUILL, 'silk', 0.26, 0.2), 'gold': mat(GOLD, 'metal', 0.26, 0.8)}

CLERK_POSE = [dict(fl=0), dict(fl=3), dict(bt=1, fl=1), dict(blink=1, fl=2), dict(look=1, fl=0), dict(look=1, fl=3),
              dict(look=1, write=1, fl=1), dict(fl=4)]


def hair_strands(r, hx, ey, m, ramp_, seed=1, spread=1.0, n=9, top=-9.0, bottom=6.0, reach=(13.0, 15.0), ln=(4.0, 8.0)):
    """wild, unwashed hair: tapered locks springing outward from both sides of the head, curling at the ends"""
    for sx in (-1, 1):
        for i in range(n):
            t = i / (n - 1)
            y0 = ey + top + (bottom - top) * t
            x0 = hx + sx * (reach[0] - 2.0 + 2.0 * math.sin(t * math.pi))
            a0 = math.atan2(-0.9 + t * 1.9 + (h32(i, seed, sx) % 7 - 3) * 0.12, sx * 1.0)
            L = ln[0] + (h32(i, seed + 1, sx) % 100) / 100 * (ln[1] - ln[0]) * spread
            k = sx * (0.10 if h32(i, seed + 2) % 2 else -0.08)
            pts = arc((x0, y0), a0, k, L, 4)
            g = 'lock%d_%d' % (sx, i)
            chain(r, pts, 1.7, 0.45, m, g, lift=0.1 - t * 0.25)
            seam(r, g, 0.16)
            ex, ey_ = pts[-1]
            r.fixed(ex, ey_, ramp_[1])


def hand_pinch(r, c, sx, m, g, ramp_):
    """a hand seen from the back pinching something (a quill, a page corner) between thumb and curled fingers"""
    x, y = c
    r.ellipsoid(x, y, 3.3, 3.4, m, group=g)
    for k in range(3):
        r.tube((x - sx * 0.5, y - 1.4 + k * 1.7), (x - sx * 3.2, y - 0.8 + k * 1.8), 1.05, 0.95, m, lift=0.03, group=g + 'f%d' % k)
        seam(r, g + 'f%d' % k, 0.16)
    r.tube((x + sx * 1.2, y - 2.4), (x - sx * 2.0, y - 3.4), 1.15, 0.95, m, lift=0.1, group=g + 't')
    seam(r, g + 't', 0.2)
    r.fixed(x + sx * 1.5, y + 1, ramp_[3])


def clerk(P):
    W, H, FL = 128, 160, 156
    r = Rig(W, H)
    bt = P.get('bt', 0)
    U = lambda y: y - bt
    look, write = P.get('look', 0), P.get('write', 0)
    # --------------------------------------------------------------------------- the coat's back and tails (behind the legs)
    back = [(45, U(66)), (83, U(66)), (88, 90), (91, 110)] + list(reversed(ragged(37, 91, 113, 4, 21))) + [(37, 112), (40, 90)]
    r.poly(back, MC['coat'], lift=-0.22, round_=0.6, group='coatback',
           vfun=lambda x, y: (-0.2 if (x - 40) % 7 == 0 and y > 96 else 0) - (y - 96) * 0.008)
    # --------------------------------------------------------------------------- legs: weight on the near leg, the far knee eased
    for hip, knee, ank, d, g, lift in (((71, 98), (78, 120), (81, 145), 1, 'legF', -0.08), ((59, 98), (58, 122), (56, 146), -1, 'legN', 0.0)):
        r.tube(hip, knee, 7.2, 6.2, MC['trou'], lift=lift, group=g,
               folds=lambda u, sd: (-0.24 if abs(sd + 0.1) < 0.1 and u > 0.3 else 0) + (0.1 if sd < -0.5 else 0))
        r.tube(knee, ank, 6.2, 5.6, MC['trou'], lift=lift, group=g,
               folds=lambda u, sd: (-0.26 if (0.62 < u < 0.68 or 0.82 < u < 0.87 or 0.15 < u < 0.2) and abs(sd) < 0.85 else 0)
               + (0.1 if sd < -0.5 else 0))                                          # baggy, concertina'd above the boot
        seam(r, g, 0.2)
        boot(r, ank, FL, d, MC['boot'], g + 'b', LEATH)
    # --------------------------------------------------------------------------- the shirt, the waistcoat, the cravat
    r.poly([(54, U(60)), (74, U(60)), (76, 96), (52, 96)], MC['shirt'], lift=-0.06, group='shirt')
    r.ellipsoid(63.5, U(58), 4.6, 3.4, MC['skin'], lift=-0.2, group='neck')
    for (pts, g) in (([(53, U(64)), (60, U(63)), (64, U(80)), (64.5, 99), (61, 102), (52.5, 97)], 'vestN'),
                     ([(67, U(63)), (75, U(64)), (76.5, 97), (68, 102), (64.5, 99), (64.5, U(80))], 'vestF')):
        r.poly(pts, MC['vest'], round_=0.85, group=g,
               vfun=lambda x, y: (-0.22 if (x * 2 + y) % 11 == 0 and y > U(80) else 0) + (0.06 if y < U(74) else 0))
        seam(r, g, 0.22)
    for y in (U(82), U(87), U(92)):
        r.fixed(64, y, GOLD[4]); r.fixed(65, y, GOLD[2]); r.fixed(64, y + 1, GOLD[1])
    for i in range(10):                                                                  # the watch chain to the far pocket
        t = i / 9
        r.fixed(65 + 8 * t, U(87) + 3 * t + 2.0 * math.sin(math.pi * t), GOLD[5] if i % 2 else GOLD[3])
    for x in range(69, 75): r.fixed(x, U(90), CVEST[0])
    for (pts, g) in (([(57.5, U(59.5)), (63, U(62)), (61, U(65.5)), (56.5, U(63))], 'colN'),
                     ([(69.5, U(59.5)), (64, U(62)), (66, U(65.5)), (70.5, U(63))], 'colF')):
        r.poly(pts, MC['shirt'], lift=0.18, round_=0.4, group=g)
        seam(r, g, 0.2)
    r.ellipsoid(63.5, U(63.5), 2.6, 2.2, MC['shirt'], lift=0.08, group='cravat')         # a limp cravat, gone grey
    r.poly([(61.5, U(65)), (65.5, U(65)), (66.5, U(74)), (63.5, U(76)), (60.5, U(73))], MC['shirt'], lift=0.02, round_=0.7, group='cravat',
           vfun=lambda x, y: -0.16 if (x + y) % 4 == 0 else 0)
    seam(r, 'cravat', 0.22)
    # --------------------------------------------------------------------------- the front of the coat: open, frayed, lapels
    def coat_v(x, y):
        v = (rig.nL(x * 0.9 + 5, y * 0.9) - 0.5) * 0.1
        if y > 96 and (x * 3 + y // 6) % 13 == 0: v -= 0.22                             # drapes
        if y > 106: v -= (y - 106) * 0.015
        for (sx_, sy, sr) in ((44, 104, 2.0), (86, 96, 1.6), (49, 82, 1.5)):             # stains, ink
            if (x - sx_) ** 2 + ((y - sy) * 1.3) ** 2 < sr * sr: v -= 0.13
        return v
    near = [(46, U(65)), (55, U(63)), (58.5, U(76)), (57.5, 97), (55, 117)] + list(reversed(ragged(38, 55, 115, 4, 5))) + [(38, 114), (39, 96), (41, U(78))]
    far = [(73, U(63)), (82, U(65)), (87, U(78)), (89, 96), (91, 114)] + list(reversed(ragged(73, 91, 115, 4, 9))) + [(72.5, 117), (71, 97), (70.5, U(76))]
    r.poly(far, MC['coat'], lift=-0.05, round_=0.8, group='coatF', vfun=coat_v)
    r.poly(near, MC['coat'], round_=0.8, group='coatN', vfun=coat_v)
    seam(r, 'coatF', 0.22); seam(r, 'coatN', 0.22)
    for (pts, g, lf) in (([(53, U(63.5)), (57.5, U(64)), (60, U(77)), (56.5, U(84)), (53.5, U(72))], 'lapN', 0.12),
                         ([(75, U(63.5)), (70.5, U(64)), (68.5, U(77)), (72, U(84)), (75, U(72))], 'lapF', 0.0)):
        r.poly(pts, MC['coat'], lift=lf, round_=0.5, group=g)
        seam(r, g, 0.26)
    for (x0, y0) in ((44, 104), (82, 102)):                                              # torn pocket flaps
        r.poly([(x0, y0), (x0 + 8, y0 - 0.5), (x0 + 8, y0 + 2.5), (x0 + 3, y0 + 3.5), (x0, y0 + 2.5)], MC['coat'], lift=0.1, round_=0.4, group='pk%d' % x0)
        seam(r, 'pk%d' % x0, 0.26)
    # --------------------------------------------------------------------------- the far arm: the sheaf of papers at his chest
    shF, elF = (80, U(67)), (86, U(89))
    hF = (83.5, U(97)) if not (look or write) else (85.5, U(84))
    r.tube(shF, elF, 5.8, 5.2, MC['coat'], lift=-0.04, group='armF',
           folds=lambda u, sd: (-0.26 if 0.82 < u and abs(sd) < 0.6 else 0) + (0.1 if sd < -0.5 else 0))
    r.tube(elF, hF, 5.2, 4.6, MC['coat'], lift=0.02, group='foreF',
           folds=lambda u, sd: -0.22 if 0.35 < u < 0.4 and abs(sd) < 0.7 else 0)
    r.tube(lerp(elF, hF, 0.62), lerp(elF, hF, 0.86), 4.9, 4.9, MC['coat'], lift=0.14, group='cuffF')
    seam(r, 'armF', 0.22); seam(r, 'foreF', 0.22); seam(r, 'cuffF', 0.24)
    tilt = -0.2 if (look or write) else 0.12
    px0, py0 = (hF[0] - 6.0, hF[1] - 13.0) if (look or write) else (hF[0] - 5.0, hF[1] - 12.0)
    for k in range(4):                                                                   # the sheaf: dog-eared, fanned
        a = tilt + (k - 1.5) * 0.08
        ca, sa = math.cos(a), math.sin(a)
        wq, hq = 15.0, 19.0
        ox, oy = px0 + k * 1.1, py0 + k * 0.7
        pts = [(ox, oy), (ox + ca * wq, oy + sa * wq), (ox + ca * wq - sa * hq, oy + sa * wq + ca * hq), (ox - sa * hq, oy + ca * hq)]
        r.poly(pts, MC['paper'], lift=0.04 - k * 0.07, round_=0.3, group='page%d' % k,
               vfun=lambda x, y, k=k, oy=oy: (-0.2 if k == 3 and (y - int(oy)) % 3 == 0 and 2 < y - oy < 17 and (x * 7 + y) % 5 else 0))
        seam(r, 'page%d' % k, 0.2)
    for (x, y) in ((px0 + 3, py0 + 18), (px0 + 4, py0 + 19), (px0 + 18, py0 + 2)):           # a red seal, a torn corner
        r.fixed(x, y, (120, 38, 30))
    hand_pinch(r, (hF[0] - 0.5, hF[1] + 0.5), 1, MC['skin'], 'handF', CSKIN)
    # --------------------------------------------------------------------------- the head
    hx, ey = 61, U(50) + (1 if look else 0)
    turn = -1
    r.ellipsoid(hx + 1, ey - 3, 13.4, 10.5, MC['hair'], lift=-0.18, jag=0.25, group='hairback')
    r.ellipsoid(hx - 10.6, ey + 2, 2.3, 3.6, MC['skin'], group='earN')
    r.ellipsoid(hx + 10.2, ey + 2, 2.1, 3.4, MC['skin'], lift=-0.1, group='earF')
    face(r, hx, ey, CSKIN, rx=10.3, ry=12.6, turn=turn, jaw=0.42)
    fx = hx + turn
    # stubble: a grey-blue dither on the jaw, the upper lip, the chin
    for y in range(ey + 4, ey + 11):
        for x in range(hx - 9, hx + 10):
            e = r.buf.get((x, y))
            if e is None or e[3] is None or group_at(r, x, y) != 'face': continue
            if abs(x - fx) < 3 and y < ey + 6: continue
            if (x + y * 2) % 3 == 0 or (y > ey + 7 and (x + y) % 2 == 0): e[3] = mix(e[3], (70, 62, 60), 0.36)
    # eyes behind the spectacles, small and tired, bags under them
    for sx in (-1, 1):
        ex = int(math.floor(fx + sx * 4.7 - 0.5))
        if P.get('blink'):
            for x in range(ex - 1, ex + 2): r.fixed(x, ey, CSKIN[2]); r.fixed(x, ey - 1, CSKIN[4])
        else:
            for x in range(ex - 1, ex + 2): r.fixed(x, ey, EYEW)
            r.fixed(ex + (1 if look else -1 if sx < 0 else 0), ey, PUPIL)
            if look: r.fixed(ex, ey, mix(EYEW, CSKIN[3], 0.5))
            for x in range(ex - 1, ex + 2): r.fixed(x, ey - 1, CSKIN[1])
        r.fixed(ex - 1, ey + 2, CSKIN[3]); r.fixed(ex, ey + 2, CSKIN[3]); r.fixed(ex + 1, ey + 2, CSKIN[4])
        r.fixed(ex, ey + 3, CSKIN[4])
    # heavy, frowning brows (they knit down toward the nose)
    for sx in (-1, 1):
        bx_ = int(math.floor(fx + sx * 4.7 - 0.5))
        for k in range(-2, 3):
            x = bx_ + k
            inner = (k * sx) < 0
            y = ey - 3 + (1 if inner and abs(k) == 2 else 0)
            r.fixed(x, y, CHAIR[2]); r.fixed(x, y - 1, CHAIR[4] if not inner else CHAIR[3])
    r.fixed(fx, ey - 3, CSKIN[2]); r.fixed(fx, ey - 4, CSKIN[3])                       # the frown's crease
    # the nose: big, a bulb, pointing a little to his left
    nose = {(0, 1): 6, (-1, 1): 4, (0, 2): 6, (-1, 2): 5, (0, 3): 7, (-1, 3): 5, (-2, 4): 5, (-1, 4): 7, (0, 4): 7, (1, 4): 4,
            (-2, 5): 4, (-1, 5): 5, (0, 5): 6, (1, 5): 3}
    for (dx, dy), k in nose.items(): r.fixed(fx + dx, ey + dy, CSKIN[k])
    r.fixed(fx - 2, ey + 6, CSKIN[1]); r.fixed(fx, ey + 6, CSKIN[2]); r.fixed(fx + 1, ey + 6, CSKIN[2]); r.fixed(fx + 2, ey + 5, CSKIN[2])
    # the mouth: turned down, a sour line
    my = ey + 8
    for dx, dy in ((-3, 1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 1)): r.fixed(fx + dx, my + dy, INKC)
    r.fixed(fx - 1, my + 1, CSKIN[5]); r.fixed(fx, my + 1, CSKIN[4])
    round_specs(r, (fx - 4.7, fx + 4.7), ey, (54, 40, 20), GOLD[5], GOLD[1], (210, 190, 140), rad=3.4)
    r.fixed(fx - 1, ey - 1, GOLD[3]); r.fixed(fx, ey - 1, GOLD[3])                     # the bridge
    for (x, y) in ((fx - 8, ey - 1), (fx - 9, ey - 1), (fx + 8, ey - 1), (fx + 9, ey - 1)): r.fixed(x, y, GOLD[2])
    # the hair: a mass under the hat, then wild strands escaping sideways and down over the ears
    for sx in (-1, 1):
        r.ellipsoid(hx + sx * 11.0 + 0.5, ey - 4.0, 4.4, 5.6, MC['hair'], jag=0.18, lift=0.0, group='hair%d' % sx)
        r.ellipsoid(hx + sx * 11.6 + 0.5, ey + 2.0, 3.0, 4.0, MC['hair'], jag=0.2, lift=-0.1, group='hair%d' % sx)
    hair_strands(r, hx, ey, MC['hair'], CHAIR, seed=3)
    for (x, y0, ln) in ((hx - 5, ey - 10, 4), (hx - 2, ey - 10, 3), (hx + 3, ey - 10, 3), (hx + 6, ey - 10, 2)):
        for k in range(ln): r.fixed(x + (k // 2) * (-1 if x < hx else 1), y0 + k, CHAIR[3 + (k == 0)])
    # --------------------------------------------------------------------------- the hat and the candle stuck on it
    by = ey - 12
    r.ellipsoid(hx + 0.5, by, 13.0, 2.6, MC['hat'], lift=-0.04, group='brim',
                vfun=lambda x, y, u, w: (0.12 if w < -0.3 else -0.14 if w > 0.5 else 0) + (-0.16 if abs(u) > 0.88 else 0))
    crown = [(hx - 8.0, by - 0.5), (hx - 7.6, by - 10.5), (hx - 2.0, by - 11.5), (hx + 4.0, by - 10.6), (hx + 7.2, by - 11.2), (hx + 8.6, by - 0.5)]
    r.poly(crown, MC['hat'], round_=0.9, group='crown',
           vfun=lambda x, y: (-0.2 if (x + 0.5 - hx - 2) ** 2 + (y - by + 6) ** 2 < 4 else 0) + (0.08 if x < hx - 3 else 0))   # a dent
    r.poly([(hx - 8.0, by - 3.6), (hx + 8.6, by - 3.6), (hx + 8.6, by - 1.0), (hx - 8.0, by - 1.0)],
           mat(R('#0c0907 #15100c #1f1712 #2a2018'), 'fabric', 0.2), round_=0.9, group='hband')
    ct = by - 11                                                                          # the crown's top
    cx_ = hx - 1
    r.ellipsoid(cx_, ct + 0.2, 4.4, 1.6, MC['wax'], lift=0.1, group='waxpool')             # the puddle it stands in
    r.poly([(cx_ - 2.6, ct - 7.5), (cx_ + 2.4, ct - 8.0), (cx_ + 2.6, ct), (cx_ - 2.8, ct)], MC['wax'], round_=0.9, group='candle',
           vfun=lambda x, y: (0.12 if y < ct - 6 else 0))
    drips = [(cx_ - 4, ct + 1, 4), (cx_ + 3, ct + 1, 6), (cx_ - 7, ct + 2, 3), (cx_ + 6, ct + 1, 2), (cx_ + 1, ct + 1, 9)]
    for (x, y0, ln) in drips:                                                             # wax runs down the crown
        for k in range(ln): r.fixed(x, y0 + k, WAX[5 - min(3, k // 2)] if k < ln - 1 else WAX[4])
        r.fixed(x + 1, y0, WAX[3])
    r.fixed(cx_ - 1, ct - 8, WAX[6]); r.fixed(cx_ + 1, ct - 8, WAX[4])                    # the melted rim
    r.fixed(cx_, ct - 8.6, (30, 22, 16)); r.fixed(cx_, ct - 9.6, (40, 30, 22))           # the wick
    # --------------------------------------------------------------------------- the near arm: the quill
    shN = (47, U(67))
    hN = (48.5, U(78)) if not write else (79, U(86))
    elN = (43.5, U(92)) if not write else (52, U(96))
    r.tube(shN, elN, 6.0, 5.4, MC['coat'], lift=0.06, group='armN',
           folds=lambda u, sd: (-0.26 if 0.8 < u and abs(sd) < 0.6 else 0) + (-0.2 if 0.4 < u < 0.45 and abs(sd) < 0.7 else 0) + (0.12 if sd < -0.5 else 0))
    r.tube(elN, hN, 5.4, 4.6, MC['coat'], lift=0.1, group='foreN',
           folds=lambda u, sd: (-0.24 if (0.3 < u < 0.35) and abs(sd) < 0.7 else 0) + (0.1 if sd < -0.5 else 0))
    r.tube(lerp(elN, hN, 0.62), lerp(elN, hN, 0.86), 5.0, 5.0, MC['coat'], lift=0.2, group='cuffN')
    for k in range(4):                                                                     # a frayed cuff
        c = lerp(elN, hN, 0.88)
        r.fixed(c[0] - 3 + k * 2, c[1] + 2 + (k % 2), CCOAT[1])
    seam(r, 'armN', 0.24); seam(r, 'foreN', 0.24); seam(r, 'cuffN', 0.24)
    # the quill: shaft from the nib below the fist up past his shoulder, a dark feather, the vane split here and there
    nib = (hN[0] + (1 if not write else -1), hN[1] + 5)
    top = (hN[0] - 12, hN[1] - 26) if not write else (hN[0] - 16, hN[1] - 22)
    dxq, dyq = top[0] - nib[0], top[1] - nib[1]; Lq = math.hypot(dxq, dyq)
    for i in range(int(Lq) + 1):
        t = i / Lq
        x, y = nib[0] + dxq * t, nib[1] + dyq * t
        if t > 0.32:
            wv = 3.2 * math.sin(math.pi * min(1.0, (t - 0.32) / 0.68)) ** 0.6
            for k in range(1, int(wv) + 2):
                if k > wv + 0.5: break
                for sd in (-1, 1):
                    gap = (h32(i, sd + 5) % 9 == 0)
                    if gap and k > 1: continue
                    c = QUILL[5 - min(4, k)] if sd < 0 else QUILL[3 - min(2, k // 2)]
                    r.fixed(x + sd * k * 0.85 - (dyq / Lq) * 0, y + sd * k * 0.5, c)
        r.fixed(x, y, (150, 140, 120) if t > 0.15 else (36, 30, 26))
    r.fixed(nib[0], nib[1] + 1, (20, 16, 14))
    hand_pinch(r, hN, -1, MC['skin'], 'handN', CSKIN)
    # --------------------------------------------------------------------------- render, the flame, its light
    im = warm_ink(r.render())
    px = im.load()
    fb = (int(cx_), int(ct - 10))
    flame_px(px, W, H, fb[0], fb[1], P.get('fl', 0))
    warm_light(px, W, H, fb[0], fb[1] - 2, 22, 0.22 if P.get('fl', 0) != 4 else 0.12)
    if P.get('fl', 0) == 4:                                                               # guttering: a thread of smoke
        for k, (dx, dy) in enumerate(((0, -6), (1, -7), (1, -8), (0, -9), (-1, -10), (-1, -11))):
            x, y = fb[0] + dx, fb[1] + dy
            if 0 <= y: px[x, y] = (150, 144, 136, 150 - k * 18)
    else:
        for k, (dx, dy) in enumerate(((0, -8), (1, -9), (1, -10), (0, -11))):
            x, y = fb[0] + dx + (P.get('fl', 0) % 2), fb[1] + dy
            if 0 <= y: px[x, y] = (150, 144, 136, 70 - k * 14)
    return im


# ============================================================================================ THE COMPLAINT EATER
TOAD   = R('#130f08 #1d170c #282010 #342a14 #413419 #4f3f1e #5d4a24 #6b552b #796133 #876d3c #957a46')
BELLY  = R('#2f2918 #3d351f #4c4328 #5b5131 #6a5f3b #796d46 #877a51 #94875c')
BRUISE = R('#291a28 #3a243b #4c2f4d #5d3b5d #6b4769')
BRASSY = R('#150e06 #241808 #37260c #4b3511 #604517 #75561e #896828 #9b7a36 #ac8d4a')
LENS   = [(30, 18, 8), (66, 40, 12), (120, 80, 20), (180, 128, 40), (226, 180, 80), (248, 222, 146)]
MAW    = R('#12070a #200b0e #321016 #45161d #591e24 #6c282c')
TIE    = R('#2c0c0c #461212 #621a18 #7e2620 #9a3428 #ad4532')
TEETH  = [(118, 104, 70), (164, 150, 108), (196, 184, 142)]
SMOKE  = (132, 126, 118)

ME = {'skin': mat(TOAD, 'wart', 0.22, 0.25), 'belly': mat(BELLY, 'wart', 0.26, 0.2), 'brass': mat(BRASSY, 'metal', 0.22, 0.85),
      'maw': mat(MAW, 'plain', 0.3, 0.4), 'tie': mat(TIE, 'fabric', 0.24, 0.15), 'collar': mat(CSHIRT, 'fabric', 0.3),
      'paper': mat(PAPER, 'plain', 0.42), 'hose': mat(BRASSY, 'metal', 0.2, 0.6)}

EATER_POSE = [dict(ph=0), dict(ph=1, jaw=1, bt=1), dict(ph=2, jaw=-1), dict(ph=3, gulp=1), dict(ph=4, lens=1),
              dict(ph=5, jaw=1, puff=1), dict(ph=6, jaw=-1, heave=1, bt=1), dict(ph=7)]


def hose(r, pts, rad, g, lift=0.0, pitch=2.2):
    """a corrugated brass hose along a polyline"""
    n = len(pts) - 1
    run = 0.0
    for i in range(n):
        L = math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
        r0 = run
        r.tube(pts[i], pts[i + 1], rad, rad, ME['hose'], lift=lift, group=g,
               folds=lambda u, sd, r0=r0, L=L: (-0.26 if ((r0 + u * L) % pitch) < pitch * 0.35 else 0.06) + (0.08 if sd < -0.4 else 0))
        run += L


def gauge_ring(r, cx, cy, rad, P, g, lens_on=True):
    """a brass ring set into the flesh (a joint, a goggle): a lit rim, rivets, an amber lens"""
    r.ellipsoid(cx, cy, rad, rad, ME['brass'], group=g,
                vfun=lambda x, y, u, w: (0.12 if (u * u + w * w) > 0.55 and u + w < -0.3 else 0) + (-0.2 if (u * u + w * w) > 0.55 and u + w > 0.6 else 0))
    inner = rad * 0.58
    k = 1 if P.get('lens') else 0
    for y in range(int(cy - inner) - 1, int(cy + inner) + 2):
        for x in range(int(cx - inner) - 1, int(cx + inner) + 2):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / inner
            if d > 1: continue
            if not lens_on: r.fixed(x, y, BRASSY[1] if d > 0.6 else MAW[1]); continue
            li = int((1 - d) * 3.2) + k + (1 if (x + 0.5 < cx and y + 0.5 < cy) else 0)
            r.fixed(x, y, LENS[max(0, min(5, li))])
    r.fixed(cx - inner * 0.4, cy - inner * 0.4, LENS[5] if k else LENS[4])
    for a in range(0, 360, 60):                                                      # rivets
        ax, ay = cx + math.cos(math.radians(a + 15)) * (rad - 0.9), cy + math.sin(math.radians(a + 15)) * (rad - 0.9)
        r.fixed(ax, ay, BRASSY[8] if a < 180 else BRASSY[3])


def crumple(r, pts, g, lift=0.0, lines=True):
    r.poly(pts, ME['paper'], lift=lift, round_=0.35, group=g,
           vfun=lambda x, y: ((-0.22 if (y + x // 4) % 3 == 0 and (x * 5 + y) % 4 else 0) if lines else 0) + (-0.18 if h32(x, y, 3) % 11 == 0 else 0))
    seam(r, g, 0.2)


def eater(P):
    W, H, FL = 128, 144, 141
    r = Rig(W, H)
    bt, ph = P.get('bt', 0), P.get('ph', 0)
    heave = P.get('heave', 0)
    U = lambda y: y - bt
    # --------------------------------------------------------------------------- the litter of complaints it squats on
    for k, (x0, y0, w, h, a) in enumerate(((6, 137, 10, 4, 0.2), (44, 138, 9, 3, -0.25), (78, 137, 10, 4, 0.3), (113, 137, 9, 3, -0.2))):
        ca, sa = math.cos(a), math.sin(a)
        crumple(r, [(x0, y0), (x0 + w * ca, y0 + w * sa), (x0 + w * ca - 1, y0 + w * sa + h), (x0 - 1.5, y0 + h)], 'litter%d' % k, lift=-0.06, lines=False)
    # --------------------------------------------------------------------------- hoses behind: over the right shoulder, the coil on the left
    hose(r, arc((88, U(52)), -0.55, 0.075, 34, 9), 3.0, 'hoseB', lift=-0.08)
    hose(r, [(28, 104), (16, 99), (8, 104), (7, 114), (13, 121), (24, 122)], 2.8, 'coil', lift=-0.06)
    r.ellipsoid(25, 122, 3.4, 3.4, ME['brass'], group='coilend')
    # --------------------------------------------------------------------------- the haunches and the body
    for (cx, cy, rx, ry, g) in ((31, 120, 15.5, 17.0, 'hauN'), (99, 118, 15.0, 18.0, 'hauF')):
        r.ellipsoid(cx, cy, rx, ry, ME['skin'], group=g, lift=-0.04 if g == 'hauF' else 0.0,
                    vfun=lambda x, y, u, w: (-0.16 if w > 0.6 else 0) + (0.1 * (1 if h32(x // 3, y // 3, 8) % 7 == 0 else 0)))
        seam(r, g, 0.12)
    def belly_v(x, y, u, w):
        v = 0.0
        for (bx_, by_, br) in ((44, 112, 4.5), (78, 96, 3.6), (88, 120, 5.0), (56, 126, 3.0), (70, 84, 2.6)):   # bruises
            if (x - bx_) ** 2 + ((y - by_) * 1.2) ** 2 < br * br: v -= 0.1
        if w > 0.72: v -= 0.14
        v -= max(0.0, w - 0.3) * 0.28                                               # dark toward the paving
        return v
    r.ellipsoid(65, U(104) - heave, 37.5 + heave, 30.5 + heave * 0.5, ME['skin'], group='body', vfun=belly_v)
    for i in range(26):                                                              # warts all over the hide
        x = 30 + h32(i, 41) % 72; y = U(80) + h32(i, 42) % 52
        e = r.buf.get((x, y))
        if e and r.groups[e[2]] == 'body' and math.hypot(x - 58, (y - U(112)) * 1.1) > 16:
            r.ellipsoid(x, y, 1.6 + (i % 3) * 0.5, 1.4 + (i % 2) * 0.4, ME['skin'], lift=0.12, group='bwart%d' % i)
    BRUISES = ((44, 112, 5.0), (80, 97, 4.0), (88, 121, 5.5), (56, 127, 3.4), (34, 99, 3.4), (100, 106, 3.0), (24, 116, 3.0))
    skin_px = {k for k, e in r.buf.items() if e[0] is not None and r.groups[e[2]] in ('body', 'belly', 'hauN', 'hauF')}
    # the feet: long splayed toad toes with dark claws, flat on the paving
    for (ax, ay, toes) in ((24, 133, ((math.pi * 0.98, 13), (math.pi * 0.84, 12), (math.pi * 0.70, 10), (math.pi * 0.56, 8))),
                           (104, 132, ((math.pi * 0.02, 13), (math.pi * 0.16, 11), (math.pi * 0.32, 10), (math.pi * 0.48, 8)))):
        r.ellipsoid(ax, ay + 1, 7.0, 4.6, ME['skin'], group='foot%d' % ax)
        for k, (a, ln) in enumerate(toes):
            pts = arc((ax + math.cos(a) * 3, ay + 3), a, 0.0, ln, 4)
            pts = [(x, min(y, FL - 1.4)) for (x, y) in pts]
            chain(r, pts, 2.2, 1.2, ME['skin'], 'toe%d_%d' % (ax, k), lift=0.02)
            seam(r, 'toe%d_%d' % (ax, k), 0.2)
            ex, ey_ = pts[-1]
            dxn = 1 if math.cos(a) > 0 else -1
            for j in range(3): r.fixed(ex + dxn * (1 + j * 0.7), min(FL, ey_ + j * 0.5), (36, 28, 18) if j else (90, 80, 60))
            r.ellipsoid(pts[2][0], pts[2][1] - 0.2, 1.8, 1.4, ME['skin'], lift=0.1, group='knuck%d_%d' % (ax, k))
    # --------------------------------------------------------------------------- joints of brass sunk into the flesh
    hose(r, [(112, U(76)), (113, U(84)), (108, U(90))], 3.0, 'hoseB2', lift=-0.04)
    gauge_ring(r, 104, U(90), 6.4, P, 'ringS')
    gauge_ring(r, 98, 116, 5.0, P, 'ringH')
    gauge_ring(r, 30, 116, 4.2, P, 'ringH2')
    # --------------------------------------------------------------------------- the head: wide, flat, warty, the maw
    jaw = P.get('jaw', 0)
    gulp = P.get('gulp', 0)
    r.ellipsoid(58, U(80) + gulp, 18.0 + gulp * 2, 8.5 + gulp * 2, ME['belly'], lift=-0.02, group='throat',
                vfun=lambda x, y, u, w: -0.2 if (y - U(80)) % 3 == 0 and w > -0.2 else 0)          # the throat folds
    r.ellipsoid(60, U(64), 30.5, 16.5, ME['skin'], group='head',
                vfun=lambda x, y, u, w: (0.08 if w < -0.5 else 0) + (-0.12 if w > 0.6 else 0))
    for (dx, dy, rr) in ((-22, -7, 2.4), (-14, -12, 2.0), (16, -12, 2.2), (25, -6, 2.6), (6, -14, 1.8), (-26, 2, 2.0), (28, 3, 2.2)):
        r.ellipsoid(60 + dx, U(64) + dy, rr, rr * 0.9, ME['skin'], lift=0.14, group='wart%d' % dx)   # warts
    # the maw: a wide crooked slot, open on the chew
    mt = U(68)                                                                       # the upper lip's middle
    mb = mt + 6 + jaw * 3                                                            # the lower lip
    cav = [(34, mt + 1)] + [(34 + i * 4, mt - 1.5 * math.sin(math.pi * i / 11) + (0 if i % 3 else 0.5)) for i in range(1, 11)] + [(80, mt + 2)] + \
          [(80 - i * 4, mb + 2.2 * math.sin(math.pi * i / 11)) for i in range(1, 11)]
    r.poly(cav, ME['maw'], lift=-0.08, round_=0.6, group='maw', vfun=lambda x, y: -0.15 if y > mt + 2 else 0)
    r.poly([(34, mt + 1), (57, mt - 1.6), (80, mt + 2), (78, mt + 3.4), (57, mt + 0.6), (36, mt + 2.6)], ME['skin'], lift=0.16, round_=0.4, group='lipU')
    r.poly([(36, mb - 0.2), (57, mb + 3.0), (78, mb + 0.5), (79, mb + 3.5), (57, mb + 6.0), (35, mb + 3.0)], ME['skin'], lift=0.02, round_=0.5, group='lipL')
    seam(r, 'lipU', 0.2); seam(r, 'lipL', 0.18)
    for i, x in enumerate(range(40, 78, 4)):                                         # crooked teeth, top and bottom
        r.fixed(x, mt + 3, TEETH[1 + (i % 2)]); r.fixed(x + 1, mt + 3, TEETH[0])
        if i % 2: r.fixed(x, mt + 4, TEETH[0])
        r.fixed(x + 2, mb - 0.5, TEETH[1]); r.fixed(x + 2, mb - 1.5, TEETH[0] if i % 3 else TEETH[1])
    # the bureaucratic remains: a shirt collar and a red tie on the throat
    for (pts, g) in (([(49, U(85)), (57, U(86)), (55, U(90)), (48, U(88))], 'colL'), ([(66, U(85)), (58, U(86)), (61, U(90)), (67, U(88))], 'colR')):
        r.poly(pts, ME['collar'], lift=0.16, round_=0.4, group=g)
        seam(r, g, 0.2)
    r.ellipsoid(57.5, U(87.5), 2.4, 2.0, ME['tie'], group='tie')
    r.poly([(56, U(88.5)), (59.5, U(88.5)), (58, U(100) - heave), (54, U(108) - heave), (51, U(104) - heave), (55, U(96))], ME['tie'],
           round_=0.6, group='tie', vfun=lambda x, y: 0.12 if (x + y) % 6 == 0 else 0)
    seam(r, 'tie', 0.22)
    # the brass goggle-eyes in a row on the brow
    for (gx, gy, gr) in ((79.5, U(56), 4.6), (39, U(56.5), 5.4), (51.5, U(52), 6.6), (66.5, U(51.5), 6.6)):
        gauge_ring(r, gx, gy, gr, P, 'eye%d' % gx)
    r.tube((43.5, U(54)), (46, U(53)), 1.0, 1.0, ME['brass'], group='bridge1')
    r.tube((72.5, U(53.0)), (75.5, U(54.5)), 1.0, 1.0, ME['brass'], group='bridge3')
    # the chimney on its head
    cx_ = 72
    r.ellipsoid(cx_, U(47.5), 7.4, 2.6, ME['brass'], group='flange')
    r.tube((cx_, U(47)), (cx_ + 0.5, U(26)), 4.0, 3.6, ME['brass'], group='stack',
           folds=lambda u, sd: (-0.22 if (0.3 < u < 0.35 or 0.62 < u < 0.67) else 0) + (0.14 if (0.36 < u < 0.4 or 0.68 < u < 0.72) and sd < 0 else 0))
    r.ellipsoid(cx_ + 0.5, U(24.5), 6.0, 2.2, ME['brass'], lift=0.08, group='cap')
    r.ellipsoid(cx_ + 0.5, U(24.0), 3.8, 1.1, ME['maw'], lift=-0.3, group='flue')
    for y in (U(43), U(35)):
        for x in (cx_ - 3, cx_ + 3): r.fixed(x, y, BRASSY[8] if x < cx_ else BRASSY[2])
    for (x, y) in ((cx_ - 1, U(40)), (cx_ + 2, U(31)), (cx_ - 2, U(29))): r.fixed(x, y, (60, 34, 20))     # soot and rust
    # --------------------------------------------------------------------------- the far arm resting on its haunch
    r.tube((103, U(94)), (99, U(111)), 5.4, 4.4, ME['skin'], lift=0.02, group='armF', folds=lambda u, sd: -0.18 if 0.45 < u < 0.52 else 0)
    r.ellipsoid(98, U(113), 4.2, 3.4, ME['skin'], group='armF')
    for k in range(4):
        r.tube((96.5 + k * 1.7, U(114)), (94 + k * 2.6, U(119.5)), 1.5, 1.1, ME['skin'], group='fingF%d' % k)
        seam(r, 'fingF%d' % k, 0.18)
    # --------------------------------------------------------------------------- the near arm: a complaint stuffed into the maw
    sh, el = (38, U(88)), (29, U(98))
    hd = (35, U(76)) if jaw >= 0 else (37, U(75))
    r.tube(sh, el, 6.4, 5.6, ME['skin'], group='armN', folds=lambda u, sd: -0.16 if u > 0.85 else 0)
    r.tube(el, hd, 5.6, 4.4, ME['skin'], lift=0.06, group='armN', folds=lambda u, sd: 0.1 if sd < -0.5 else 0)
    seam(r, 'armN', 0.2)
    pin = 46 + (2 if jaw < 0 else 0)
    crumple(r, [(30, U(66)), (pin, mt + 1), (pin + 1, mt + 6 + jaw), (34, U(80)), (27, U(73))], 'complaint', lift=0.06)
    for (x, y) in ((33, U(72)), (36, U(74)), (31, U(75))): r.fixed(x, y, (90, 40, 34))                # a red "URGENT" stamp, smudged
    r.ellipsoid(hd[0], hd[1], 4.2, 3.8, ME['skin'], lift=0.04, group='handN')
    for k in range(4):                                                               # long toad fingers over the page
        r.tube((hd[0] + 1, hd[1] - 2 + k * 1.6), (hd[0] + 7 + (k == 1), hd[1] - 4 + k * 2.2), 1.2, 0.9, ME['skin'], lift=0.08, group='fingN%d' % k)
        seam(r, 'fingN%d' % k, 0.2)
    im = warm_ink(r.render())
    px = im.load()
    hide = {k for k, e in r.buf.items() if e[0] is not None and r.groups[e[2]] in ('body', 'hauN', 'hauF', 'head', 'armN', 'armF', 'throat')}
    for (x, y) in hide:                                                               # toad mottling: dark blotches, pale flecks
        m_ = rig.nM(x * 1.5 + 30, y * 1.5) + (rig.nF(x * 2, y * 2) - 0.5) * 0.3
        if m_ > 0.64: px[x, y] = mix(px[x, y][:3], TOAD[1], min(0.45, (m_ - 0.64) * 2.2)) + (255,)
        elif m_ < 0.2 and h32(x, y, 9) % 3 == 0: px[x, y] = mix(px[x, y][:3], BELLY[7], 0.25) + (255,)
    for (x, y) in skin_px:                                                            # the paler, softer underside
        d = math.hypot((x - 57) / (23 + heave), (y - (U(111) - heave)) / 21.0) + (rig.nM(x * 2.5, y * 2.5) - 0.5) * 0.35
        if d < 1 and r.groups[r.buf[(x, y)][2]] == 'body': px[x, y] = mix(px[x, y][:3], BELLY[6], 0.34 * (1 - d * d)) + (255,)
    for (bx_, by_, br) in BRUISES:                                                    # violet bruises soaked into the hide
        for y in range(int(by_ - br) - 1, int(by_ + br) + 2):
            for x in range(int(bx_ - br) - 1, int(bx_ + br) + 2):
                if (x, y) not in skin_px or r.buf.get((x, y)) is None or r.groups[r.buf[(x, y)][2]] not in ('body', 'belly', 'hauN', 'hauF'): continue
                d = math.hypot(x - bx_, (y - by_) * 1.2) / br + (rig.nF(x * 3, y * 3) - 0.5) * 0.7
                if d < 1: px[x, y] = mix(px[x, y][:3], BRUISE[2], 0.45 * (1 - d) ** 0.5) + (255,)
    # --------------------------------------------------------------------------- smoke from the chimney: puffs rise through the loop
    px = im.load()
    for j in range(3):
        t = ((ph + j * 8 / 3) % 8) / 8
        sx_, sy_ = cx_ + 1 + math.sin(t * 5 + j) * 2.4 + t * 5, U(21) - t * 20
        rad = 1.6 + t * 3.0 + (1.0 if P.get('puff') and j == 0 else 0)
        alpha = int(150 * (1 - t) ** 0.8) + (50 if P.get('puff') and j == 0 else 0)
        for y in range(int(sy_ - rad) - 1, int(sy_ + rad) + 2):
            for x in range(int(sx_ - rad) - 1, int(sx_ + rad) + 2):
                if not (0 <= x < W and 0 <= y < H) or px[x, y][3] == 255: continue
                d = math.hypot(x + 0.5 - sx_, y + 0.5 - sy_) / rad
                if d > 1: continue
                lit = (x + 0.5 < sx_ and y + 0.5 < sy_)
                c = mix(SMOKE, (176, 170, 160), 0.5) if lit else SMOKE
                a = min(200, int(alpha * (1 - d * d * 0.6)))
                if a > px[x, y][3]: px[x, y] = c + (a,)
    return im


# ======================================================================================= COUNCILOR SERAPHEL DUNE
ROBE   = R('#08080a #0d0d10 #121216 #18181c #1e1f23 #25262b #2d2e33 #36373c #404146')
TEALC  = R('#0b1615 #11201e #182c29 #203935 #294742 #33554f #3e635c')
BONE   = R('#28241c #3d382c #534c3e #6a6250 #817864 #978e78 #aaa18b #bcb49e #cbc4af #d8d2bf')
STOLE  = R('#24221d #33302a #433f37 #534e44 #635d51 #726c5f #807a6c')
GILT   = R('#21180a #382a10 #554016 #71571e #8b6e29 #a28538 #b79c4f #c8b06a')
GEM    = [(20, 40, 38), (34, 76, 70), (56, 118, 104), (110, 176, 156)]
WHISK  = (196, 190, 172)

MS = {'robe': mat(ROBE, 'worn', 0.2, 0.2), 'robe2': mat(ROBE, 'worn', 0.18, 0.1), 'teal': mat(TEALC, 'silk', 0.22, 0.3),
      'bone': mat(BONE, 'bone', 0.28, 0.22), 'stole': mat(STOLE, 'fabric', 0.26), 'gilt': mat(GILT, 'metal', 0.26, 0.85),
      'cord': mat(GILT, 'fabric', 0.24, 0.2)}

SERA_POSE = [dict(), dict(bt=1), dict(wh=1), dict(tap=1), dict(tilt=1), dict(sway=1), dict(glint=1), dict(bt=1, wh=-1)]


def gilt_line(r, pts, c_hi, c_lo, step=0.5):
    """a 1-px gilt edging along a polyline, lit where it faces up-left"""
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        L = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for k in range(L + 1):
            t = k / L
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            r.fixed(x, y, c_hi if (x1 - x0) * -1 + (y1 - y0) * 0.3 > 0 or (h32(int(x), int(y)) % 3 == 0) else c_lo)


def seraphel(P):
    W, H, FL = 128, 192, 189
    r = Rig(W, H)
    bt = P.get('bt', 0)
    U = lambda y: y - bt
    tilt = P.get('tilt', 0)
    sway = P.get('sway', 0)
    # turned a quarter to the viewer's left (toward the dais): the robe's opening and the face sit left of the frame's
    # middle, the far (viewer-right) flank shows more; the weight on the near leg, the far knee bent under the cloth
    C = lambda y: 60.5 - (y - 40) * 0.025                                                # the front line, leaning a touch
    # --------------------------------------------------------------------------- the bird feet under the hem
    for (fx, fy, d, g, lift) in ((68.0, FL - 1, 1, 'footF', -0.12), (53.0, FL, -1, 'footN', 0.0)):
        r.tube((fx, 173), (fx + d * 0.5, fy - 3), 2.0, 1.7, MS['bone'], lift=lift, group=g,
               folds=lambda u, sd: -0.22 if int(u * 9) % 2 == 0 and abs(sd) < 0.8 else 0)
        r.ellipsoid(fx + d * 0.5, fy - 2.4, 2.8, 2.1, MS['bone'], lift=lift, group=g)
        toes = ((math.pi * (0.5 + d * 0.44), 8.5), (math.pi * (0.5 + d * 0.27), 10.0), (math.pi * (0.5 + d * 0.06), 7.0)) if d < 0 else \
               ((math.pi * 0.06, 7.5), (math.pi * 0.24, 8.0), (math.pi * 0.5 + 0.3, 6.0))
        for k, (a, ln) in enumerate(toes):
            pts = arc((fx + d * 0.5, fy - 2.0), a, 0.0, ln, 3)
            pts = [(x, min(y, fy - 0.8)) for (x, y) in pts]
            chain(r, pts, 1.4, 0.8, MS['bone'], g + 't%d' % k, lift=lift)
            seam(r, g + 't%d' % k, 0.18)
            ex, ey_ = pts[-1]
            r.fixed(ex + math.cos(a) * 1.2, fy, (30, 26, 20)); r.fixed(ex + math.cos(a) * 0.4, fy - 0.6, (60, 54, 44))
    # --------------------------------------------------------------------------- the mantle (the back layer, longest)
    def robe_v(x, y, base=0.0):
        v = base + (rig.nL(x * 0.8 + 3, y * 0.5) - 0.5) * 0.10
        for fx0, sl in ((44, -0.16), (50, -0.07), (76, 0.06), (84, 0.14), (90, 0.2)):     # long drapes
            px_ = fx0 + (y - 60) * sl + 1.2 * math.sin(y * 0.07 + fx0)
            d = x + 0.5 - px_
            if y > 60 and -0.5 <= d < 0.5: v -= 0.28
            elif y > 60 and 0.5 <= d < 1.6: v += 0.12
        if 112 < y < 146:                                                                # the far knee pushing the cloth out
            k_ = math.exp(-((x - 75) / 3.2) ** 2) * math.sin(math.pi * (y - 112) / 34)
            v += 0.16 * k_
            if 140 < y < 150 and 70 < x < 82: v -= 0.12
        if y > 168: v -= (y - 168) * 0.012
        return v
    mantle = [(47, U(43)), (75, U(42)), (86, U(50)), (91, U(66)), (93, 110), (96, 150), (99, 182), (86, 185), (72, 183), (60, 185),
              (46, 184), (34, 182), (37, 150), (39, 110), (40, U(66)), (41, U(50))]
    r.poly(mantle, MS['robe2'], lift=-0.08, round_=0.8, group='mantle', vfun=robe_v)
    hem = ragged(34, 99, 182, 3, 77, step=3.0)                                            # a tattered, gilt-fringed hem
    for (x, y) in hem:
        for dy in range(int(y) - 182 + 1): r.fixed(x, 182 + dy, ROBE[1])
        if h32(int(x), 4) % 2: r.fixed(x, y + 1, GILT[3])
    # --------------------------------------------------------------------------- the pale stole (only a strip shows, below the hands)
    r.poly([(C(70) - 2, U(70)), (C(70) + 3, U(70)), (C(178) + 4, 179), (C(178) - 3, 180)], MS['stole'], lift=-0.1, round_=0.7, group='stole',
           vfun=lambda x, y: (-0.2 if abs(x + 0.5 - C(y)) < 0.6 and y > 92 else 0) + (-0.1 if y > 160 else 0))
    for y0 in (120, 150):                                                                 # embroidered glyph bands on it
        for x in range(int(C(y0) - 3), int(C(y0) + 5)):
            r.fixed(x, y0, GILT[3] if x % 2 else GILT[1]); r.fixed(x, y0 + 3, GILT[2] if x % 2 == 0 else GILT[1])
            if (x + y0) % 3 == 0: r.fixed(x, y0 + 1.5, GILT[2])
    # the robe's front panels, open over the stole, gilt-edged; the far one is broader (we see his left flank)
    near = [(C(44) - 2, U(44)), (46, U(45)), (41, U(64)), (40, 110), (38, 178), (C(178) - 6, 181), (C(120) - 3.5, 120), (C(70) - 3, U(70))]
    far = [(C(44) + 3, U(44)), (77, U(44)), (88, U(56)), (90, 110), (93, 179), (C(178) + 7, 180), (C(120) + 4.5, 120), (C(70) + 4, U(70))]
    r.poly(far, MS['robe'], lift=-0.06, round_=0.85, group='panelF', vfun=lambda x, y: robe_v(x, y, -0.02))
    r.poly(near, MS['robe'], lift=0.04, round_=0.85, group='panelN', vfun=lambda x, y: robe_v(x, y, 0.04))
    seam(r, 'panelF', 0.16); seam(r, 'panelN', 0.2)
    for sx, pts in ((-1, [(C(70) - 3, U(70)), (C(120) - 3.5, 120), (C(178) - 6, 181)]), (1, [(C(70) + 4, U(70)), (C(120) + 4.5, 120), (C(178) + 7, 180)])):
        gilt_line(r, pts, GILT[6] if sx < 0 else GILT[4], GILT[3] if sx < 0 else GILT[2])
    for (x0, k) in ((46, 0), (73, 2), (82, 3)):                                          # faint gilt pinstripes following the drape
        for y in range(U(60), 178):
            x = x0 + (x0 - 60) * (y - 60) * 0.0018 + 1.0 * math.sin(y * 0.07 + x0)
            e = r.buf.get((int(x), y))
            if e and e[0] is not None and r.groups[e[2]] in ('panelN', 'panelF') and h32(y // 3, k) % 5:
                r.fixed(int(x), y, GILT[1] if (y // 7 + k) % 3 else GILT[2])
    # --------------------------------------------------------------------------- the far sleeve (behind the arm), a long drape
    r.poly([(79, U(48)), (87, U(52)), (92, U(68)), (94, 104), (92, 120), (86, 123), (82, 110), (79, U(80))], MS['robe'], lift=-0.1, round_=0.85,
           group='sleeveF', vfun=lambda x, y: (-0.26 if (x - 85) % 4 == 0 and y > U(72) else 0))
    seam(r, 'sleeveF', 0.2)
    gilt_line(r, [(94, 104), (92, 120), (86, 123)], GILT[4], GILT[2])
    # the forearms come in toward the chest (inner sleeves with teal cuffs)
    hcx = C(70) - 1.0                                                                     # the steeple's axis
    for sx, el, lift in ((1, (80, U(86)), -0.04), (-1, (45, U(88)), 0.1)):
        wr = (hcx + sx * 5.6, U(77))
        r.tube(el, wr, 4.6, 3.6, MS['robe'], lift=lift, group='fore%d' % sx,
               folds=lambda u, sd: (-0.24 if 0.4 < u < 0.46 and abs(sd) < 0.7 else 0) + (0.12 if sd < -0.5 else 0))
        r.tube(lerp(el, wr, 0.7), wr, 4.2, 4.0, MS['teal'], lift=lift + 0.1, group='cuff%d' % sx)
        seam(r, 'fore%d' % sx, 0.24); seam(r, 'cuff%d' % sx, 0.22)
        gilt_line(r, [(wr[0] - sx * 0.5, wr[1] - 3.6), (wr[0] - sx * 0.5, wr[1] + 3.6)], GILT[6], GILT[3])
    # the near sleeve's drape hangs in front, from the shoulder past the elbow
    r.poly([(41, U(48)), (49, U(47)), (50, U(70)), (48, 100), (44, 122), (37, 124), (33, 110), (35, U(66))], MS['robe'], lift=0.08, round_=0.85,
           group='sleeveN', vfun=lambda x, y: (-0.28 if (x - 40) % 4 == 0 and y > U(74) else 0) + (0.08 if x < 38 else 0))
    seam(r, 'sleeveN', 0.26)
    gilt_line(r, [(48, 100), (44, 122), (37, 124), (33, 110)], GILT[6], GILT[3])
    # --------------------------------------------------------------------------- the steepled hands: long bony fingers, tips touching
    tap = P.get('tap', 0)
    for sx in (1, -1):
        hc = (hcx + sx * 4.0, U(75))
        r.ellipsoid(hc[0], hc[1], 2.8, 3.4, MS['bone'], lift=-0.06 if sx > 0 else 0.04, group='palm%d' % sx)
        for k in range(4):
            base = (hc[0] - sx * 0.6 + sx * (k - 1.5) * 0.4, hc[1] - 2.0 + k * 0.6)
            tip = (hcx + sx * (0.6 + tap * (1.2 if k < 2 else 0)), U(64) + k * 1.6)
            mid = ((base[0] + tip[0]) / 2 + sx * 0.9, (base[1] + tip[1]) / 2)
            g = 'fing%d_%d' % (sx, k)
            r.tube(base, mid, 0.95, 0.85, MS['bone'], lift=0.05 - k * 0.04 - (0.06 if sx > 0 else 0), group=g)
            r.tube(mid, tip, 0.85, 0.7, MS['bone'], lift=0.05 - k * 0.04 - (0.06 if sx > 0 else 0), group=g)
            r.fixed(mid[0] + sx * 0.6, mid[1], BONE[7] if sx < 0 else BONE[5])
            seam(r, g, 0.18)
        r.tube((hc[0] - sx * 1.5, hc[1] + 1), (hcx + sx * 1.2, U(71)), 1.0, 0.8, MS['bone'], lift=0.06, group='thumb%d' % sx)
        seam(r, 'thumb%d' % sx, 0.2)
    # --------------------------------------------------------------------------- the seal-tags on gilt cords (mostly on his left flank)
    tags = ((78, U(50), 30, 1, (5, 8)), (84, U(53), 50, 2, (6, 11)), (44, U(51), 24, 3, (5, 7)), (89, U(58), 68, 4, (4, 7)))
    for (tx, ty, ln, i, (tw, th)) in tags:
        dx_ = sway * (1 if i % 2 else -1)
        bot = (tx + dx_, ty + ln)
        for k in range(int(ln)):
            r.fixed(tx + dx_ * k / ln, ty + k, GILT[4] if k % 2 else GILT[2])
        x0, y0 = int(bot[0]) - tw // 2, int(bot[1])
        r.poly([(x0, y0), (x0 + tw, y0), (x0 + tw, y0 + th), (x0, y0 + th)], MS['gilt'], round_=0.4, group='tag%d' % i)
        for yy in range(y0 + 2, y0 + th - 1, 2):
            for xx in range(x0 + 1, x0 + tw - 1):
                if h32(xx, yy, i) % 3: r.fixed(xx, yy, GILT[1])
        r.fixed(x0 + tw // 2, y0 + th, GILT[5]); r.fixed(x0 + tw // 2, y0 + th + 1, GILT[3])
    # --------------------------------------------------------------------------- the high teal collar, the headdress, the skull
    hx = C(22) - 1.5 - tilt
    hy = U(22) + (1 if tilt else 0)
    fan_c = (hx + 1.0, hy - 1)
    fan_oid = r.new('fan')
    for y in range(int(hy - 21), int(hy + 1)):
        for x in range(int(hx - 14), int(hx + 16)):
            u, w = (x + 0.5 - fan_c[0]) / 12.0, (y + 0.5 - fan_c[1]) / 19.5
            if u * u + w * w > 1 or y > hy: continue
            a = math.atan2(x + 0.5 - fan_c[0], -(y + 0.5 - fan_c[1]))
            rib = abs(((a + 2) * 7.5) % 1 - 0.5) < 0.12
            if u * u + w * w > 0.86: r.fixed(x, y, GILT[5] if a < 0 else GILT[3], fan_oid)
            elif rib and (u * u + w * w) > 0.15: r.fixed(x, y, GILT[2] if a < 0 else GILT[1], fan_oid)
            else: r.put(x, y, MS['robe'], 0.32 + (0.12 if u < -0.2 else 0) - max(0, u) * 0.16, fan_oid)
    for y in range(int(hy - 21), int(hy - 2)):
        r.fixed(fan_c[0] - 0.5, y, GILT[6] if y < hy - 10 else GILT[4]); r.fixed(fan_c[0] + 0.5, y, GILT[3])
    for (dx, dy, c) in ((0, -22, GEM[3]), (1, -22, GEM[2]), (0, -21, GEM[2]), (1, -21, GEM[1]), (0, -23, GILT[6]), (1, -23, GILT[5]),
                        (0, -20, GILT[4]), (1, -20, GILT[3]), (-1, -21, GILT[4]), (2, -21, GILT[2])):
        r.fixed(fan_c[0] - 0.5 + dx, hy + dy, c)
    for sx in (-1, 1):                                                                   # two stiff teal wings rising behind the jaw
        cc = C(40)
        pts = [(cc + sx * 4, U(42)), (cc + sx * (14 if sx < 0 else 16), U(44)), (cc + sx * 12, U(32)), (cc + sx * 8.5, U(27)), (cc + sx * 6, U(32))]
        r.poly(pts, MS['teal'], lift=0.04 * -sx, round_=0.7, group='collar%d' % sx,
               vfun=lambda x, y: -0.2 if (x + y) % 4 == 0 and y > U(34) else 0)
        gilt_line(r, [(cc + sx * (14 if sx < 0 else 16), U(44)), (cc + sx * 12, U(32)), (cc + sx * 8.5, U(27))], GILT[6], GILT[3])
    r.ellipsoid(C(42), U(42), 9.0, 3.2, MS['teal'], lift=-0.06, group='collarB')
    r.ellipsoid(hx + 0.5, hy, 7.6, 7.2, MS['bone'], group='skull',
                vfun=lambda x, y, u, w: (-0.12 if w > 0.5 else 0) + (0.06 if u < -0.3 and w < 0 else 0) - max(0, u - 0.3) * 0.2)
    r.ellipsoid(hx - 4.4, hy + 3.5, 2.6, 2.2, MS['bone'], lift=-0.04, group='cheek')
    r.ellipsoid(hx + 5.0, hy + 3.2, 2.0, 2.2, MS['bone'], lift=-0.16, group='cheek2')
    bk = arc((hx - 1.5, hy + 4.0), math.pi * 0.5 + 0.26 + tilt * 0.08, 0.016, 15.5, 6)
    n = len(bk) - 1
    for i in range(n):
        r.tube(bk[i], bk[i + 1], 3.4 * (1 - i / n * 0.82), 3.4 * (1 - (i + 1) / n * 0.82), MS['bone'], lift=0.04, group='beak',
               folds=lambda u, sd: (0.14 if -0.5 < sd < -0.1 else 0) + (-0.18 if sd > 0.5 else 0))
    for i in range(1, n): r.fixed(bk[i][0] - 0.8, bk[i][1], BONE[8 if i < 3 else 7])
    r.fixed(bk[1][0] + 1.4, bk[1][1] + 1, BONE[2]); r.fixed(bk[1][0] + 1.4, bk[1][1] + 2, BONE[2])
    r.fixed(bk[-1][0], bk[-1][1] + 1, BONE[3])
    for sx, ex, sz in ((-1, hx - 3.4, 1), (1, hx + 3.0, 0)):                              # the sockets (the far one narrower)
        cells = [(0, 0), (1, 0), (0, 1), (1, 1), (0, -1)] + ([(-1, 0), (-1, 1), (-1, 2)] if sz else [(1, 2)])
        for (dx, dy) in cells:
            r.fixed(ex + dx, hy + dy, (16, 13, 11) if (dx, dy) != (0, -1) else (34, 28, 22))
        if P.get('glint'): r.fixed(ex, hy, (226, 232, 214)); r.fixed(ex + 1, hy + 1, (120, 130, 116))
        else: r.fixed(ex, hy + 1, (54, 50, 42))
        r.fixed(ex - 1, hy - 2, BONE[8] if sx < 0 else BONE[6]); r.fixed(ex, hy - 2, BONE[8] if sx < 0 else BONE[6])
    for (x, y) in ((hx - 1, hy - 5), (hx + 2, hy - 4), (hx - 4, hy - 4)): r.fixed(x, y, BONE[9])
    r.fixed(hx + 1, hy - 6, BONE[3]); r.fixed(hx + 2, hy - 6, BONE[4])
    # --------------------------------------------------------------------------- render, then the whiskers (thin, pale, no outline)
    im = warm_ink(r.render())
    px = im.load()
    wh = P.get('wh', 0)
    for sx in (-1, 1):
        for k, (y0, ln, bend) in enumerate(((hy + 5, 16, 0.05), (hy + 7, 19, 0.08), (hy + 9, 14, 0.11))):
            pts = arc((hx + sx * 3.4 - 1, y0), math.pi * (0.5 - sx * 0.42) + sx * k * 0.08 - wh * 0.05,
                      -sx * (bend + wh * 0.012), ln * (0.85 if sx > 0 else 1.0), int(ln))
            for i, (x, y) in enumerate(pts[1:]):
                xi, yi = int(x), int(y)
                if not (0 <= xi < W and 0 <= yi < H): continue
                if px[xi, yi][3] == 255 and i < 3: continue
                c = WHISK if i < ln * 0.6 else mix(WHISK, (120, 116, 104), 0.5)
                if px[xi, yi][3] < 255: px[xi, yi] = c + (max(70, 235 - i * 9),)
                else: px[xi, yi] = mix(px[xi, yi][:3], c, 0.6) + (255,)
    return im


# ================================================================================================== THE MAD POET
# Drawn ~15% smaller than the rest of the cast (figure ~124 px instead of ~146): he stands on the reading dais at depth
# ~17.6 (feet y 482) rather than on the walk line at depth 15, so at scale 1 he reads the same real height as the others.
PSKIN  = R('#33201a #4b2e23 #63402f #7a523d #8e644c #a0765c #b0886c #bd997d #c8a88c')
PHAIR  = R('#0e0b09 #17120e #201913 #2a2119 #352a1f #413326 #4d3d2e #5a4836')
PURP   = R('#100b11 #18111a #211723 #2a1d2d #342437 #3e2b41 #48334b #523b55 #5c445f')
SCARF  = R('#260a0a #3a0f0f #511613 #681e18 #7e281e #923325 #a3402d')
PTROU  = R('#0d0e0c #141612 #1c1e19 #24271f #2d3026 #363a2d #404535')
IRON   = R('#0b0b0d #141418 #1e1e23 #29292f #35353c #43434a #53535a')
GRIP   = R('#1c0f08 #2e180c #422312 #572f18')
COVER  = R('#1a0d08 #28140c #371c11 #472516 #572f1c #673922')
EYEP   = (214, 188, 176)

MPo = {'skin': mat(PSKIN, 'skin', 0.28, 0.1), 'hair': mat(PHAIR, 'hair', 0.24, 0.12), 'coat': mat(PURP, 'worn', 0.18, 0.06),
       'scarf': mat(SCARF, 'wool', 0.22), 'vest': mat(SCARF, 'fabric', 0.2, 0.1), 'shirt': mat(CSHIRT, 'fabric', 0.24),
       'trou': mat(PTROU, 'fabric', 0.18), 'boot': mat(LEATH[:-2], 'leather', 0.18, 0.5), 'iron': mat(IRON, 'metal', 0.24, 0.9),
       'grip': mat(GRIP, 'wood', 0.24, 0.3), 'cover': mat(COVER, 'leather', 0.22, 0.3), 'paper': mat(PAPER, 'plain', 0.42)}

POET_POSE = [dict(ph=0), dict(ph=1, bt=1), dict(ph=2, blink=1), dict(ph=3, shake=1), dict(ph=4, declaim=1), dict(ph=5, declaim=2),
             dict(ph=6, page=1), dict(ph=7, bt=1)]


def poet(P):
    W, H, FL = 128, 144, 141
    r = Rig(W, H)
    bt = P.get('bt', 0)
    U = lambda y: y - bt
    dc = P.get('declaim', 0)
    # --------------------------------------------------------------------------- the coat's back and tails
    back = [(47, U(58)), (80, U(58)), (86, 82), (90, 106)] + list(reversed(ragged(36, 91, 112, 5, 13))) + [(37, 108), (41, 82)]
    r.poly(back, MPo['coat'], lift=-0.24, round_=0.6, group='coatback', vfun=lambda x, y: (-0.2 if (x - 40) % 6 == 0 and y > 90 else 0))
    # --------------------------------------------------------------------------- legs: the near leg planted, the far knee out
    for hip, knee, ank, d, g, lift in (((70, 90), (76, 110), (78, 130), 1, 'legF', -0.08), ((58, 90), (55, 111), (54, 131), -1, 'legN', 0.0)):
        r.tube(hip, knee, 6.4, 5.6, MPo['trou'], lift=lift, group=g,
               folds=lambda u, sd: (-0.24 if abs(sd + 0.1) < 0.1 and u > 0.3 else 0) + (0.1 if sd < -0.5 else 0))
        r.tube(knee, ank, 5.6, 5.0, MPo['trou'], lift=lift, group=g,
               folds=lambda u, sd: (-0.26 if (0.55 < u < 0.61 or 0.8 < u < 0.85) and abs(sd) < 0.85 else 0) + (0.1 if sd < -0.5 else 0))
        seam(r, g, 0.2)
        boot(r, (ank[0], ank[1] + 1), FL, d, MPo['boot'], g + 'b', LEATH)
    for (x, y) in ((53, 110), (54, 111), (55, 110), (56, 112), (54, 112)): r.fixed(x, y, PSKIN[3] if (x + y) % 2 else PTROU[0])   # a torn knee
    # --------------------------------------------------------------------------- shirt, red waistcoat, the coat's front
    r.poly([(54, U(56)), (72, U(56)), (74, 90), (52, 90)], MPo['shirt'], lift=-0.1, group='shirt', vfun=lambda x, y: -0.14 if (x + y) % 5 == 0 else 0)
    r.poly([(66, 88), (73, 88), (71, 96), (67, 94)], MPo['shirt'], lift=-0.04, group='shirttail')            # the shirt hanging out
    for (pts, g) in (([(53, U(60)), (60, U(59)), (63, U(74)), (63.5, 90), (60, 92.5), (52.5, 89)], 'vestN'),
                     ([(66, U(59)), (73, U(60)), (75, 89), (67, 92.5), (63.5, 90), (63.5, U(74))], 'vestF')):
        r.poly(pts, MPo['vest'], round_=0.85, group=g, vfun=lambda x, y: (-0.22 if (x * 2 + y) % 9 == 0 else 0) + (-0.1 if y > 84 else 0))
        seam(r, g, 0.22)
    for y in (U(76), U(81)): r.fixed(63, y, GOLD[3]); r.fixed(63, y + 1, GOLD[1])
    def coat_v(x, y):
        v = (rig.nL(x * 0.9 + 5, y * 0.9) - 0.5) * 0.12
        if y > 88 and (x * 3 + y // 6) % 11 == 0: v -= 0.22
        if y > 100: v -= (y - 100) * 0.016
        for (sx_, sy, sr) in ((45, 96, 2.0), (84, 90, 1.8), (50, 76, 1.4)):
            if (x - sx_) ** 2 + ((y - sy) * 1.3) ** 2 < sr * sr: v -= 0.14
        return v
    near = [(46, U(57)), (55, U(56)), (58, U(70)), (57, 90), (55, 112)] + list(reversed(ragged(37, 55, 110, 5, 5))) + [(37, 108), (38, 88), (41, U(70))]
    far = [(72, U(56)), (81, U(57)), (86, U(70)), (88, 90), (91, 108)] + list(reversed(ragged(72, 91, 111, 5, 9))) + [(71.5, 112), (70, 90), (69.5, U(70))]
    r.poly(far, MPo['coat'], lift=-0.04, round_=0.8, group='coatF', vfun=coat_v)
    r.poly(near, MPo['coat'], lift=0.02, round_=0.8, group='coatN', vfun=coat_v)
    seam(r, 'coatF', 0.22); seam(r, 'coatN', 0.22)
    for (pts, g, lf) in (([(52, U(56)), (56.5, U(57)), (59, U(69)), (55.5, U(76)), (52.5, U(65))], 'lapN', 0.12),
                         ([(75, U(56)), (70.5, U(57)), (68.5, U(69)), (72, U(76)), (75, U(65))], 'lapF', 0.0)):
        r.poly(pts, MPo['coat'], lift=lf, round_=0.5, group=g)
        seam(r, g, 0.26)
    # --------------------------------------------------------------------------- the far arm: the open book of poems
    shF, elF = (80, U(60)), (86, U(81))
    page = P.get('page', 0)
    hF = (80, U(76))
    r.tube(shF, elF, 5.2, 4.6, MPo['coat'], lift=-0.04, group='armF',
           folds=lambda u, sd: (-0.26 if 0.8 < u and abs(sd) < 0.6 else 0) + (0.1 if sd < -0.5 else 0))
    r.tube(elF, hF, 4.6, 4.0, MPo['coat'], lift=0.02, group='foreF', folds=lambda u, sd: -0.22 if 0.35 < u < 0.4 and abs(sd) < 0.7 else 0)
    seam(r, 'armF', 0.22); seam(r, 'foreF', 0.22)
    for k in range(4):                                                                     # a frayed cuff
        c = lerp(elF, hF, 0.85)
        r.fixed(c[0] - 2 + k, c[1] + 3 + (k % 2), PURP[1])
    bx, by = 72.0, U(66.5)                                                                # the book's spine, tilted toward us
    ang = -0.32
    ca, sa = math.cos(ang), math.sin(ang)
    P2 = lambda u, v: (bx + ca * u - sa * v, by + sa * u + ca * v)
    r.poly([P2(-13, -1), P2(13, -1), P2(13.5, 9.5), P2(-13.5, 9.5)], MPo['cover'], lift=-0.1, round_=0.4, group='cover')
    for (side, g) in ((-1, 'pageL'), (1, 'pageR')):
        pts = [P2(0, 0), P2(side * 11.5, -1.6), P2(side * 12.2, 8.2), P2(0, 9.0)]
        r.poly(pts if side > 0 else list(reversed(pts)), MPo['paper'], lift=0.06 if side < 0 else -0.02, round_=0.5, tilt=-0.2, group=g,
               vfun=lambda x, y: (-0.24 if (y - int(by)) % 2 == 0 and h32(x, y) % 4 else 0))
        seam(r, g, 0.18)
    for t in range(9): x, y = P2(0, t); r.fixed(x, y, PAPER[1])                             # the gutter
    if page:                                                                               # a page lifting, turning
        r.poly([P2(0.5, 0), P2(7, -5), P2(8, 3), P2(0.5, 8.5)], MPo['paper'], lift=0.18, round_=0.5, group='turn')
        seam(r, 'turn', 0.2)
    for k in range(3):                                                                     # fingers under the cover, the thumb on the page
        x, y = P2(6 + k * 2.2, 10.2)
        r.ellipsoid(x, y, 1.2, 1.0, MPo['skin'], group='bfing%d' % k)
    tx, ty = P2(9, 6)
    r.tube((tx + 3, ty + 3), (tx, ty), 1.2, 1.0, MPo['skin'], lift=0.08, group='bthumb'); seam(r, 'bthumb', 0.2)
    # --------------------------------------------------------------------------- the head: wild hair, a ragged beard, haunted eyes
    hx, ey = 62, U(41) - (1 if dc else 0)
    r.ellipsoid(hx + 1, ey - 5, 13.6, 11.0, MPo['hair'], lift=-0.18, jag=0.3, group='hairback')
    r.ellipsoid(hx - 9.4, ey + 2, 2.1, 3.2, MPo['skin'], group='earN')
    face(r, hx, ey, PSKIN, rx=9.0, ry=11.2, turn=-1, jaw=0.45, sockets=0.2)
    fx = hx - 1
    for sx in (-1, 1):                                                                     # hollow cheeks
        for y in range(ey + 2, ey + 5):
            e = r.buf.get((fx + sx * 6, y))
            if e and e[3] is not None: e[3] = mix(e[3], PSKIN[2], 0.35)
    # the beard: ragged, dark, along the jaw to a point, a moustache
    def bclip(x, y):
        dx = abs(x + 0.5 - fx)
        if dx >= 8.0: return y >= ey + 2
        return y >= ey + 7.4 - max(0.0, dx - 3.0) * 0.7
    r.ellipsoid(fx, ey + 7.5, 9.8, 8.6, MPo['hair'], jag=0.18, group='beard', clip=bclip,
                vfun=lambda x, y, u, w: (-0.16 if (x * 3 + int(2 * math.sin(y * 0.4))) % 5 == 0 else 0) - (0.1 if abs(u) > 0.8 else 0))
    for (dx, ln) in ((-4, 3), (-1, 4), (2, 3), (5, 2)):
        x = fx + dx
        yb = max((y for y in range(ey, ey + 22) if group_at(r, x, y) == 'beard'), default=None)
        if yb is None: continue
        for k in range(1, ln + 1): r.fixed(x + (k // 2) * (1 if dx > 0 else -1), yb + k, PHAIR[3 - min(k, 2)])
    my = ey + 7
    if dc:                                                                                 # declaiming: the mouth open, teeth
        for dx in range(-2, 2):
            r.fixed(fx + dx, my, INKC); r.fixed(fx + dx, my + 1, (60, 20, 18)); r.fixed(fx + dx, my + 2 + (dc > 1), INKC)
        r.fixed(fx - 1, my, (180, 168, 140)); r.fixed(fx, my, (160, 150, 124))
        if dc > 1:
            for dx in range(-2, 2): r.fixed(fx + dx, my + 2, (60, 20, 18))
    else:
        for dx in range(-2, 2): r.fixed(fx + dx, my, INKC)
        r.fixed(fx - 1, my + 1, PSKIN[4])
    for dx in range(-4, 4):                                                                # the moustache over it
        r.fixed(fx + dx, my - 1, PHAIR[2] if abs(dx + 0.5) > 2 else PHAIR[3])
    r.fixed(fx - 4, my, PHAIR[2]); r.fixed(fx + 3, my, PHAIR[2])
    # eyes: wide, bloodshot, red-rimmed, dark bags; the brows high and crooked
    for sx in (-1, 1):
        ex = int(math.floor(fx + sx * 4.2 + 0.5 - 0.5))
        if P.get('blink'):
            for x in range(ex - 1, ex + 2): r.fixed(x, ey, PSKIN[2]); r.fixed(x, ey - 1, PSKIN[3])
        else:
            for x in range(ex - 1, ex + 2): r.fixed(x, ey, EYEP)
            r.fixed(ex + (-1 if not dc else 0), ey - (1 if dc else 0) if False else ey, PUPIL)
            r.fixed(ex + 1, ey, mix(EYEP, (150, 60, 50), 0.5))
            for x in range(ex - 1, ex + 2): r.fixed(x, ey - 1, (110, 46, 38))           # raw red upper lids
        for x in range(ex - 1, ex + 2): r.fixed(x, ey + 1, (120, 56, 46))                 # raw lower rims
        r.fixed(ex - 1, ey + 2, PSKIN[1]); r.fixed(ex, ey + 2, PSKIN[2]); r.fixed(ex + 1, ey + 2, PSKIN[2])   # dark bags
        b0 = ey - 3 - (1 if (P.get('blink') or dc) else 0)
        for k in range(-2, 3):
            r.fixed(ex + k, b0 + (1 if k * sx > 1 else 0) - (1 if sx > 0 and k == 0 else 0), PHAIR[2])
    nose = {(0, 1): 5, (-1, 1): 3, (0, 2): 5, (-1, 2): 4, (0, 3): 6, (-1, 3): 4, (-1, 4): 6, (0, 4): 6, (1, 4): 3}
    for (dx, dy), k in nose.items(): r.fixed(fx + dx, ey + dy, PSKIN[k])
    r.fixed(fx - 2, ey + 5, PSKIN[1]); r.fixed(fx + 1, ey + 5, PSKIN[1]); r.fixed(fx + 2, ey + 4, PSKIN[2])
    # the wild hair: a matted mop over the crown, locks springing out everywhere, a few hanging over the brow
    r.ellipsoid(hx + 0.5, ey - 8.5, 11.0, 7.5, MPo['hair'], jag=0.2, group='haircap',
                clip=lambda x, y: y < ey - 5 + (h32(x, 17) % 4) - (2 if abs(x - fx) > 6 else 0) or abs(x + 0.5 - hx) > 8.6,
                vfun=lambda x, y, u, w: (-0.18 if (x * 3 + int(2 * math.sin(y * 0.5))) % 5 == 0 else 0))
    hair_strands(r, hx, ey - 2, MPo['hair'], PHAIR, seed=7, n=10, top=-12.0, bottom=6.0, reach=(12.0, 14.0), ln=(4.0, 9.0))
    for i in range(6):                                                                     # spikes on the crown
        a = -math.pi / 2 + (i - 2.6) * 0.36 + (h32(i, 5) % 5 - 2) * 0.09
        x0, y0 = hx + 1 + math.cos(a) * 9, ey - 6 + math.sin(a) * 9
        pts = arc((x0, y0), a, 0.06 * (1 if i % 2 else -1), 5 + h32(i, 6) % 4, 3)
        chain(r, pts, 1.6, 0.4, MPo['hair'], 'spike%d' % i, lift=0.12)
        seam(r, 'spike%d' % i, 0.16)
    for (x, y0, ln) in ((fx - 4, ey - 9, 4), (fx - 1, ey - 9, 5), (fx + 3, ey - 9, 3)):     # greasy locks over the forehead
        for k in range(ln): r.fixed(x + (k // 2) * (-1 if x < fx else 0), y0 + k, PHAIR[2 + (k == 0)])
    # the red scarf wound round the neck, one end over the chest
    r.ellipsoid(63.5, U(55.5), 10.0, 3.8, MPo['scarf'], group='scarf', vfun=lambda x, y, u, w: -0.22 if (x + y) % 4 == 0 and abs(w) > 0.3 else 0)
    r.poly([(55, U(56)), (61, U(57)), (59.5, U(72)), (54, U(73)), (53.5, U(64))], MPo['scarf'], lift=0.04, round_=0.7, group='scarfe',
           vfun=lambda x, y: -0.18 if y in (U(62), U(67)) else 0)
    for k in range(4): r.fixed(54 + k * 1.4, U(73) + (k % 2), SCARF[2 + (k % 2)])
    seam(r, 'scarf', 0.2); seam(r, 'scarfe', 0.22)
    # --------------------------------------------------------------------------- the near arm: the revolver raised beside his head
    sh = P.get('shake', 0)
    shN = (47, U(59))
    hN = (33 - sh, U(53) - (1 if dc > 1 else 0) + sh)
    elN = (38, U(79))                                                                      # the elbow hangs down at his side
    r.tube(shN, elN, 5.6, 5.0, MPo['coat'], lift=0.06, group='armN',
           folds=lambda u, sd: (-0.26 if 0.8 < u and abs(sd) < 0.6 else 0) + (0.12 if sd < -0.5 else 0))
    r.tube(elN, hN, 5.0, 4.2, MPo['coat'], lift=0.1, group='foreN',
           folds=lambda u, sd: (-0.24 if (0.3 < u < 0.35 or 0.55 < u < 0.6) and abs(sd) < 0.7 else 0) + (0.12 if sd < -0.5 else 0))
    for k in range(4):
        c = lerp(elN, hN, 0.84)
        r.fixed(c[0] - 2 + k, c[1] + 1 + (k % 2), PURP[1])
    seam(r, 'armN', 0.24); seam(r, 'foreN', 0.24)
    gx, gy = hN[0] + 0.5, hN[1] - 2.0                                                     # the revolver, muzzle up
    r.poly([(gx - 1.4, gy + 2), (gx + 1.6, gy + 1.5), (gx + 2.6, gy + 7), (gx - 0.2, gy + 7.5)], MPo['grip'], round_=0.5, group='grip')
    r.poly([(gx - 2.4, gy - 5), (gx + 2.4, gy - 5), (gx + 2.4, gy + 1.5), (gx - 2.4, gy + 1.5)], MPo['iron'], round_=0.9, group='cyl',
           vfun=lambda x, y: -0.24 if (x - int(gx)) % 2 == 0 else 0.05)
    r.tube((gx - 0.6, gy - 5), (gx - 1.4, gy - 17), 1.2, 1.1, MPo['iron'], lift=0.08, group='barrel')
    r.tube((gx + 1.0, gy - 5), (gx + 0.4, gy - 12), 0.8, 0.7, MPo['iron'], lift=-0.1, group='rod')
    r.fixed(gx - 1.5, gy - 17.5, IRON[6]); r.fixed(gx - 2.0, gy - 18, IRON[1])            # the front sight
    r.tube((gx + 1.6, gy + 1.2), (gx + 3.2, gy - 0.6), 0.8, 0.6, MPo['iron'], group='hammer')
    r.ellipsoid(hN[0], hN[1] + 2.4, 3.2, 3.3, MPo['skin'], lift=0.02, group='fist')
    for k in range(4):
        r.ellipsoid(hN[0] - 2.3 + k * 1.5, hN[1] + 4.6, 0.9, 1.2, MPo['skin'], lift=0.06, group='knk%d' % k)
        seam(r, 'knk%d' % k, 0.18)
    r.tube((hN[0] + 1.5, hN[1] + 1.5), (hN[0] - 1.2, hN[1] + 0.4), 1.0, 0.9, MPo['skin'], lift=0.12, group='gthumb'); seam(r, 'gthumb', 0.2)
    im = warm_ink(r.render())
    px = im.load()
    ph = P.get('ph', 0)                                                                   # a wisp from the muzzle, curling away
    mx, my_ = gx - 1.6, gy - 19
    for i in range(10):
        t = i / 9
        x = mx + math.sin(t * 4.2 + ph * 0.8) * (1 + t * 2.2) + t * 2.0
        y = my_ - i * 1.0
        xi, yi = int(x), int(y)
        if 0 <= xi < W and 0 <= yi < H and px[xi, yi][3] < 255:
            px[xi, yi] = (170, 164, 156, int(150 * (1 - t) ** 0.8))
    return im


# =================================================================================================== registry
CAST = {'phor': (phor, PHOR_POSE), 'clerk': (clerk, CLERK_POSE), 'eater': (eater, EATER_POSE), 'seraphel': (seraphel, SERA_POSE), 'poet': (poet, POET_POSE)}
GPL = ([INK, WARM_INK, PUPIL, WATER, GLASS, VERD, EYEW, INKC] + FUR + MUZ + SHELLC + GCOAT + GTROU + RUFF + LEATH + BRONZE + GOLD + PAPER + FLAME
       + CSKIN + CHAIR + CHAT + WAX + CSHIRT + CVEST + CCOAT + CTROU + QUILL + TOAD + BELLY + BRUISE + BRASSY + LENS + MAW + TIE + TEETH
       + ROBE + TEALC + BONE + STOLE + GILT + GEM + [WHISK] + PSKIN + PHAIR + PURP + SCARF + PTROU + IRON + GRIP + COVER + [EYEP])


def write_gpl(path, frames_by_id, extra=96):
    """the ramps + the most used of the mixed colours (light spill, glass, bruises), capped so the palette stays usable"""
    count = {}
    for frames in frames_by_id.values():
        for im in frames:
            for (r_, g_, b_, a_) in im.getdata():
                if a_ == 255: count[(r_, g_, b_)] = count.get((r_, g_, b_), 0) + 1
    used = sorted(count, key=lambda c: -count[c])[:extra]
    seen, rows = set(), []
    for c in GPL + used:
        c = tuple(c)
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(path, 'w').write('GIMP Palette\nName: townhall_cast\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')
    return len(rows)


if __name__ == '__main__':
    ids = sys.argv[2:] or list(CAST)
    done = {}
    for cid in ids:
        fn, poses = CAST[cid]
        os.makedirs(f'{OUT}/{cid}', exist_ok=True)
        frames = [fn(p) for p in poses]
        for i, im in enumerate(frames): im.save(f'{OUT}/{cid}/{i}.png')
        sheet(frames, f'{OUT}/{cid}.png')
        done[cid] = frames
    n = write_gpl(f'{OUT}/townhall_cast.gpl', done)
    print('ok', OUT, ids, n, 'colours')
