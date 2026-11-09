"""The Lumen Directorate cast, redrawn with the character renderer (rig.py, the Edgar quality bar) after their old AI
pictures (gardener.png / AngleCorrector.png / seldo.png -- now only references for who they are):

  verrik           128x192, soles on y 189 -- Verrik the gardener (LumenDirectorateScene, in front of the left bed):
                   a big crouching insect -- brown chitin, a segmented abdomen, veined translucent wings folded back,
                   large glowing green compound eyes, a beaked face under a cap of moss, twig-like antennae, a mantle of
                   moss with asters, daisies and seed heads over the shoulders, moss rags at the waist, a brass lantern
                   of glow-moss at the hip; both hands on a long pole pruner whose curved sickle blade hangs with moss.
                   0 rest  1 inhale  2 an antenna twitches  3-4 the wings shiver  5-6 the sickle's edge glints
                   7 exhale (the lantern flickers all along)
  verrik_decay     the same 8 frames in Decay (LumenDirectorateScene swaps to it when getGDTendency() is decayDominant):
                   the mantle brown-grey and patchy, the blooms wilted, seed heads blown, the glow-moss dimmer, the
                   sickle dull with rust specks, the wings tattered, the upper body 2 px more stooped, the antennae
                   drooping; dead leaves lie at his feet and two are shaken off the mantle in frames 3-6 (the Decay
                   anim plays 3-4-5-6 in order so they fall; 5-6 keep only a dull gleam on the blade)
  angle_corrector  128x192, soles on y 189 -- the Angle Corrector (LumenDirectorateInteriorScene, right near column):
                   a tall figure in plate of pale limestone enamel, worn and gilt-trimmed like the Directorate's own
                   facade: a lancet helm with a lit visor slit, the tracery of a lancet window and the Lumen sun on the
                   breastplate, pauldrons swept up into spires, slate mail at the joints, ivy trained in right angles up
                   the breastplate, a gilt ring floating over the helm marked like a goniometer. 3/4 turned to the
                   viewer's left, the weight on the far leg; the near gauntlet rests on the head of a tall brass
                   T-square planted beside him, the far arm hangs close.
                   The ring turns a quarter notch per frame with period 4 (frames k and k+4 show it at the same angle),
                   so any run 0-1-2-3 or 4-5-6-7 (or a mix keeping the k -> k+1 mod 4 order) keeps it turning:
                   0-3 rest  4 inhale  5 the visor brightens as it measures you  6 the helm tips one degree
                   7 exhale, a finger lifts off the T-square and settles.
  seldo            128x192, soles on y 189 -- Seldo Thrice-Corrected (LumenDirectorateInteriorScene, left near column):
                   a slender figure folded from pale green official forms (ruled lines, tiny print, three red
                   corrections: brow, belly, forearm), a head folded like a paper bird's (a crest swept back, two slit
                   eyes lit from inside), a folded sash held by a brass paperclip, a jacket whose tails are accordion
                   pleats; 3/4 to the viewer's right, weight on the far leg; the near hand holds a folded, sealed permit
                   up beside him; behind the head a brass protractor arc with a needle and a little lamp.
                   0 rest  1 inhale  2 the facets rustle  3 the needle ticks + lamp bright  4 the head tilts
                   5 the permit flutters  6 a slit-eyed "blink" (the eye folds shut)  7 exhale

python3 lumen_cast.py <outdir> [verrik|angle_corrector|seldo ...]
  -> <id>.png (8-frame sheets) + <id>/<n>.png + lumen_cast.gpl"""
import sys, os, math
from PIL import Image
from common import ramp, INK, h32
import rig
from rig import Rig, Mat, norm
from feral_toast import ik
from hero import seam

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
R = ramp

# ---- palettes (muted; the Lumen gold and limestone, no candy) ---------------------------------------------------------
CHITIN = R('#100a08 #180f0b #21150f #2a1a12 #331f16 #3d251a #482b1e #533223 #5f3a29 #6c4330 #7a4e38 #895a42')
CHBELL = R('#1c140d #281d13 #362719 #453220 #553e28 #654b31 #76593b')               # paler belly plates
MOSS   = R('#121409 #1a1d0d #232811 #2d3316 #383f1b #444b21 #515828 #5f6530 #6e733a #7e8245 #8f9152')
MOSSDK = R('#0e0f08 #16180c #1f2210 #292c15 #33361a #3e401f')
ASTER  = R('#2e1f2e #43304a #5a4262 #725779 #8a6d8e #9f84a0')
CREAM  = R('#6e6852 #8a8468 #a6a084 #c0ba9c #d6d0b2')
OCHRE  = R('#3e2c10 #5a4218 #765a24 #927232 #ac8a44')
WOOD   = R('#170e08 #24160c #321f11 #412916 #50341c #5f3f23 #6f4b2b #805835')
STEEL  = R('#15171a #1f2226 #2a2e33 #363b41 #434950 #525960 #636a71 #777e84 #8e9498 #a9adaf #c6c9c8')
GOLD   = R('#2a1c09 #463210 #6a4e1a #8e6c25 #b08a35 #cfab52 #e8cc84')
BRASS  = R('#1e150b #2e2110 #3f2e16 #513c1d #634a25 #75592f #87693b #977a4a #a68b5c')
EYEG   = R('#161d0b #202b0f #2c3a13 #394a18 #475b1e #566d25 #677f2f #7a913c #8fa44e #a8b968 #c3cf8e')     # the compound eyes
GLOWG  = R('#2e3c14 #45561c #5e7026 #7a8a36 #98a64c #b8c272 #d4daa0')                        # glow-moss in the lantern
DEAD   = R('#13110e #1c1915 #26221c #302b23 #3b342a #463e32 #51483a #5c5243 #685d4d #746958 #807563')  # dead moss (Decay)
DEADDK = R('#0f0d0b #171411 #1f1b17 #28231d #312b23 #3a3329')
WILT   = R('#2e2228 #463540 #5f4a55 #75606a #8a767c #9c8a8c')                            # wilted asters, faded
WCREAM = R('#4a4234 #625844 #7a6e56 #92856a #a69a7e')                                    # wilted daisies, browned
LEAF   = R('#2e1c0e #452a14 #5e3a1b #774c26 #8c5e32 #a0703e')                            # dead leaves
WINGM  = (186, 196, 168)                                                             # wing membrane (translucent)
WINGV  = (74, 58, 34)                                                                # wing veins
WARM_INK = (34, 22, 14)

LIME   = R('#181815 #22221e #2d2c27 #393731 #45433b #524f46 #605c51 #6e695d #7c7769 #8a8476 #989283 #a7a090 #b5ae9d #c3bcaa')  # enamel
SLATE  = R('#101317 #171b21 #1f242b #282e36 #323942 #3d454f #49525c')
SAGE   = R('#161b14 #20271d #2b3427 #364131 #424f3c #4f5d48 #5d6b55')                # the tabard
IVY    = R('#0f1a0c #172812 #213818 #2c481f #385a27 #456b30')
VISOR  = R('#3c2a0c #6a4c16 #a07a28 #d4ac4a #f4dc8c #fff4cc')

PAPER  = R('#1a1f17 #252b21 #31382c #3e4637 #4c5544 #5b6552 #6b7561 #7c8671 #8e9782 #a0a893 #b2b9a5 #c4c9b7 #d4d8c8')
PINK   = R('#3c1c16 #5a2a20 #78392a #8e4636')                                         # the red correction ink
PRINT  = (86, 96, 80)                                                                 # faint printed rules / type

def _tex():
    nF, nM, nL = rig.nF, rig.nM, rig.nL
    rig.TEX['chitin'] = lambda x, y: ((nM(x * 1.3, y * 1.3) - 0.5) * 0.12 + (nF(x * 2.6, y * 0.55) - 0.5) * 0.20
                                      + (0.07 if h32(x, y, 77) % 23 == 0 else 0) - (0.06 if h32(x, y, 78) % 17 == 0 else 0))
    rig.TEX['moss'] = lambda x, y: ((nF(x * 2.2, y * 2.2) - 0.5) * 0.34 + (nM(x * 1.1, y * 1.1) - 0.5) * 0.14
                                    + (0.1 if h32(x, y, 31) % 7 == 0 else 0) - (0.1 if h32(x, y, 32) % 9 == 0 else 0))
    rig.TEX['bark'] = lambda x, y: (nF(x * 2.4, y * 0.4) - 0.5) * 0.16 + (nM(x, y) - 0.5) * 0.06
    rig.TEX['enamel'] = lambda x, y: ((nL(x * 0.9, y * 0.9) - 0.5) * 0.12 + (nM(x * 1.3, y * 1.3) - 0.5) * 0.08
                                      + (nF(x * 1.5, y * 1.5) - 0.5) * 0.05 - (0.08 if h32(x, y, 13) % 41 == 0 else 0))
    rig.TEX['paper'] = lambda x, y: ((nF(x * 2.0, y * 2.0) - 0.5) * 0.05 + (nF(x * 0.3, y * 3.0) - 0.5) * 0.05
                                     + (0.03 if h32(x, y, 5) % 11 == 0 else 0))


_tex()
M = {'chitin': Mat(CHITIN, 'chitin', 0.18, 0.6), 'belly': Mat(CHBELL, 'chitin', 0.24, 0.2),
     'moss': Mat(MOSS, 'moss', 0.22), 'mossdk': Mat(MOSSDK, 'moss', 0.25), 'wood': Mat(WOOD, 'bark', 0.24, 0.15),
     'steel': Mat(STEEL, 'metal', 0.2, 0.9), 'gold': Mat(GOLD, 'metal', 0.24, 0.8), 'brass': Mat(BRASS, 'metal', 0.22, 0.7), 'eye': Mat(EYEG, 'plain', 0.3, 0.6),
     'glow': Mat(GLOWG, 'plain', 0.6), 'dead': Mat(DEAD, 'moss', 0.2), 'deaddk': Mat(DEADDK, 'moss', 0.22), 'lime': Mat(LIME, 'enamel', 0.18, 0.4), 'slate': Mat(SLATE, 'leather', 0.2, 0.3),
     'sage': Mat(SAGE, 'wool', 0.22), 'ivy': Mat(IVY, 'plain', 0.26, 0.2), 'paper': Mat(PAPER, 'paper', 0.3, 0.05)}


def mix(a, b, t): return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def group_at(r, x, y):
    e = r.buf.get((int(x), int(y)))
    return r.groups[e[2]] if e else None


def facet(r, pts, mat, n, group=None, lift=0.0, vfun=None, clip=None):
    """a flat polygon with ONE normal (a plane of plate or paper): the facets of a solid read as separate planes"""
    oid = r.new(group)
    v0 = r.shade(mat, norm(n), lift)
    ys = [p[1] for p in pts]
    for y in range(int(math.floor(min(ys))), int(math.ceil(max(ys))) + 1):
        yc, xs = y + 0.5, []
        for i in range(len(pts)):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
            if (y0 <= yc < y1) or (y1 <= yc < y0): xs.append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(int(math.ceil(xs[i] - 0.5)), int(math.floor(xs[i + 1] - 0.5)) + 1):
                if clip and not clip(x, y): continue
                r.put(x, y, mat, v0 + (vfun(x, y) if vfun else 0), oid)
    return oid


def line_px(x0, y0, x1, y1):
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    return [(int(round(x0 + (x1 - x0) * i / max(1, n - 1))), int(round(y0 + (y1 - y0) * i / max(1, n - 1)))) for i in range(n)]


def stage_light(r, y0, k):
    """the light falls from above: everything below y0 gets gradually darker (weight, and the floor's shadow)"""
    for (x, y), e in r.buf.items():
        if e[0] is not None and y > y0: e[1] -= (y - y0) * k


def warm_ink(im):
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y] == (18, 14, 12, 255): px[x, y] = WARM_INK + (255,)
    return im


# ======================================================================================================================
#  VERRIK
# ======================================================================================================================
VPOSE = [dict(b=0), dict(b=1), dict(b=0, ant=1), dict(b=0, wing=1), dict(b=1, wing=2), dict(b=1, glint=1, look=1),
         dict(b=0, glint=2, look=1), dict(b=0)]
LANTERN = [0, 1, 2, 1, 0, 2, 1, 0]                                                   # its flicker, per frame


def wing_layer(W, H, root, ang, L, wid, side, sheen=0.0, ghost=None, tatter=0):
    """a veined, translucent insect wing (RGBA) from `root` along angle `ang` (radians, screen space), length L,
    max width wid; side = +1/-1 picks which edge is the straight leading edge (the costa)"""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); p = im.load()
    ca, sa = math.cos(ang), math.sin(ang)
    nx, ny = -sa * side, ca * side                                                   # toward the leading edge
    def lead(t): return wid * 0.22 * math.sin(math.pi * min(1, t)) ** 0.7 + 0.8
    def trail(t): return wid * 0.78 * math.sin(math.pi * min(1.0, t * 0.96 + 0.02)) ** 0.55
    R_ = L + wid + 4
    x0, x1 = int(root[0] - R_), int(root[0] + R_)
    y0, y1 = int(root[1] - R_), int(root[1] + R_)
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            dx, dy = x + 0.5 - root[0], y + 0.5 - root[1]
            u = dx * ca + dy * sa
            v = dx * nx + dy * ny
            if u < 0 or u > L: continue
            t = u / L
            le, tr = lead(t), trail(t)
            if tatter and t > 0.5:                                                         # a ragged, torn trailing edge
                tr *= 0.72 + 0.28 * (h32(int(t * 26), tatter, 3) % 100) / 100
            if not (-tr <= v <= le): continue
            # the membrane: pale, cool, more opaque toward the root and along the costa, a faint warm sheen
            a = 64 + 50 * (1 - t) + (22 if v > le - 3 else 0)
            col = WINGM
            s = math.exp(-((t - 0.45 - sheen * 0.15) ** 2) / 0.02) * math.exp(-((v + tr * 0.25) ** 2) / 30)
            col = mix(col, (230, 226, 196), 0.5 * s); a += 40 * s
            col = mix(col, (150, 170, 150), max(0, (t - 0.6)) * 0.6)                  # cooler toward the tip
            # veins: the costa, three long veins fanning from the root, cross-veins making cells
            f = (v + tr) / max(0.1, le + tr)                                           # 0 trailing .. 1 leading edge
            vein = False
            if le - v < 1.0 or (v + tr) < 0.9: vein = True                             # the rim
            for fv, t0 in ((0.72, 0.0), (0.46, 0.08), (0.2, 0.22)):
                if t > t0 and abs(f - fv - 0.05 * math.sin(t * 7)) * (le + tr) < 0.55: vein = True
            for tc in (0.28, 0.5, 0.66, 0.8, 0.9):
                cs = tc + 0.03 * math.sin(f * 9 + tc * 20)
                if abs(t - cs) * L < 0.5 and f > 0.12: vein = True
            if vein:
                p[x, y] = WINGV + (205,)
            else:
                p[x, y] = col + (int(min(170, a)),)
    if ghost:                                                                          # a faint after-image while it shivers
        g = wing_layer(W, H, root, ghost, L, wid, side, tatter=tatter)
        gp = g.load()
        for y in range(H):
            for x in range(W):
                if p[x, y][3] == 0 and gp[x, y][3]:
                    c = gp[x, y]; p[x, y] = c[:3] + (c[3] // 4,)
    return im


def verrik_hand(r, c, g, back=False):
    """a chitin fist round the pole: the back of the hand, three fingers wrapped across it toward the viewer's left,
    a hooked claw at the knuckles"""
    x, y = c
    r.ellipsoid(x + 1.5, y, 3.4, 3.3, M['chitin'], group=g)
    for k in range(3):
        r.tube((x + 2.6, y - 2.0 + k * 1.9), (x - 2.4, y - 1.6 + k * 2.0), 1.15, 1.0, M['chitin'], lift=0.05, group=g + 'f%d' % k)
        seam(r, g + 'f%d' % k, 0.2)
        r.fixed(x - 3.2, y - 1.4 + k * 2.0, CHITIN[1])
    r.tube((x + 2.0, y - 3.0), (x - 1.6, y - 4.4), 1.2, 0.9, M['chitin'], lift=0.1, group=g + 't')   # the thumb over the top
    seam(r, g + 't', 0.2)


def flower(r, x, y, kind, tilt=0):
    """a tiny bloom pinned into the moss: aster (mauve), daisy (cream), seed head (ochre)"""
    x, y = int(x), int(y)
    if kind == 'big':
        for (dx, dy, k) in ((-2, 0, 3), (2, 0, 1), (0, -2, 4), (0, 2, 1), (-1, -1, 4), (1, 1, 2), (-1, 1, 2), (1, -1, 3),
                            (-2, -1, 3), (2, 1, 0), (-1, -2, 4), (1, 2, 1), (-2, 1, 2), (2, -1, 2), (1, -2, 3), (-1, 2, 1)):
            r.fixed(x + dx, y + dy, ASTER[k + 1])
        r.fixed(x, y, OCHRE[4]); r.fixed(x - 1, y, OCHRE[3]); r.fixed(x + 1, y, OCHRE[2]); r.fixed(x, y + 1, OCHRE[1])
        r.fixed(x, y - 1, OCHRE[3])
    elif kind == 'aster':
        for (dx, dy, k) in ((-1, 0, 3), (1, 0, 2), (0, -1, 4), (0, 1, 1), (-1, -1, 4), (1, 1, 1), (-1, 1, 2), (1, -1, 3)):
            r.fixed(x + dx, y + dy, ASTER[k + 1])
        r.fixed(x, y, OCHRE[3]); r.fixed(x + 1, y + 1, ASTER[0])
    elif kind == 'daisy':
        for (dx, dy, k) in ((-1, 0, 3), (1, 0, 1), (0, -1, 3), (0, 1, 1), (-1, -1, 2), (1, 1, 0), (-1, 1, 1), (1, -1, 2)):
            r.fixed(x + dx, y + dy, CREAM[k])
        r.fixed(x, y, OCHRE[4]); r.fixed(x + 1, y + 1, MOSS[2])
    elif kind == 'small':
        r.fixed(x, y, ASTER[4]); r.fixed(x + 1, y, ASTER[2]); r.fixed(x, y + 1, ASTER[1])
    else:
        r.fixed(x, y, OCHRE[4]); r.fixed(x + 1, y, OCHRE[2]); r.fixed(x, y - 1, OCHRE[3]); r.fixed(x + 1, y - 1, OCHRE[1])
        r.fixed(x, y + 1, MOSS[2])


def wilted(r, x, y, kind):
    """the same blooms gone over (Decay): heads drooping on bent stalks, petals hanging, seed heads blown to a stub"""
    x, y = int(x), int(y)
    if kind in ('big', 'aster', 'small'):
        r.fixed(x, y - 1, DEAD[5])                                                     # the stalk, bent over
        if kind == 'small':
            r.fixed(x + 1, y, WILT[3]); r.fixed(x + 1, y + 1, WILT[1]); return
        pet = ((-1, 1, 4), (1, 1, 3), (0, 2, 3), (-1, 2, 2), (1, 2, 2), (-1, 3, 1), (1, 3, 1)) + \
              (((-2, 1, 4), (2, 1, 2), (0, 3, 2), (-2, 2, 3), (2, 2, 1), (-2, 3, 1), (0, 4, 1)) if kind == 'big' else ())
        for (dx, dy, k) in pet: r.fixed(x + dx, y + dy, WILT[k])                      # petals hanging off a nodding head
        r.fixed(x, y, OCHRE[2]); r.fixed(x - 1, y, OCHRE[3]); r.fixed(x, y + 1, OCHRE[1])
        r.fixed(x - 1, y - 2, DEAD[7])
    elif kind == 'daisy':
        r.fixed(x, y - 1, DEAD[6]); r.fixed(x - 1, y - 2, DEAD[7])
        for (dx, dy, k) in ((-1, 1, 4), (1, 1, 2), (0, 2, 3), (-1, 2, 2), (1, 2, 1), (0, 3, 1)): r.fixed(x + dx, y + dy, WCREAM[k])
        r.fixed(x, y, OCHRE[2]); r.fixed(x - 1, y, OCHRE[3])
    else:
        r.fixed(x, y, OCHRE[1]); r.fixed(x, y - 1, OCHRE[0])                           # blown: a bare stub


# dead leaves shaken off the mantle while the wings shiver (frames 3-6 play in order in the Decay anim) and those that
# already lie at his feet; (x, y, tumble) per frame, None = not in that frame
LEAF_FALL = [{3: (31, 104, 0), 4: (28, 126, 1), 5: (25, 154, 0), 6: (23, 185, 2)},
             {3: (97, 108, 1), 4: (100, 132, 0), 5: (103, 160, 1), 6: (105, 186, 2)}]
LEAF_GROUND = [(22, 187), (106, 188), (72, 188), (47, 188)]


def leaf_px(im, x, y, tumble, k=0):
    """a dead leaf, 3 px: flat, edge-on or lying"""
    p = im.load()
    shape = {0: ((0, 0, 4), (1, 0, 3), (-1, 0, 5), (0, 1, 2), (1, 1, 1)), 1: ((0, 0, 4), (0, 1, 3), (0, -1, 5), (1, 0, 2), (1, 1, 1)),
             2: ((0, 0, 4), (1, 0, 3), (-1, 0, 5), (2, 0, 2), (0, -1, 3))}[tumble]
    for (dx, dy, c) in shape:
        if 0 <= x + dx < im.width and 0 <= y + dy < im.height: p[x + dx, y + dy] = LEAF[max(0, c - k)] + (255,)


def plates(n, hi=0.2, lo=-0.36, edge=0.12):
    """tube folds for overlapping chitin plates: each plate's rim catches the light, then it darkens toward where it
    tucks under the next one"""
    def f(u, sd):
        s = (u * n) % 1.0
        if s > 1 - edge: return lo
        rim = 0.14 if s < 0.08 else 0
        return rim + hi * (0.5 - s) + (0.06 if sd < -0.35 else 0) - (0.1 if sd > 0.6 else 0)
    return f


def verrik_leg(r, hip, knee, ankle, foot_dir, g, near):
    """an insect leg: a plated thigh, a knobbed knee, a spined shin, a three-jointed foot with two claws"""
    r.tube(hip, knee, 9.4 if near else 8.8, 5.4, M['chitin'], group=g, folds=plates(3),
           bulge=lambda t: 2.0 * math.sin(math.pi * min(1, t * 1.4)))
    r.ellipsoid(knee[0], knee[1], 5.4, 4.8, M['chitin'], lift=0.12, group=g + 'k',
                vfun=lambda x, y, u, w: (-0.24 if w > 0.55 else 0) + (0.12 if -0.6 < w < -0.2 and u < 0 else 0))
    r.tube(knee, ankle, 4.0, 2.7, M['chitin'], group=g + 's', folds=plates(2, 0.16, -0.3, 0.1))
    seam(r, g + 'k', 0.18)
    dx, dy = ankle[0] - knee[0], ankle[1] - knee[1]; L = math.hypot(dx, dy)
    side = -1 if near else 1                                                           # spines on the outer edge of the shin
    for k in (0.28, 0.5, 0.72):
        sx, sy = knee[0] + dx * k, knee[1] + dy * k
        rr = 4.0 + (2.7 - 4.0) * k
        r.fixed(sx + side * (rr + 0.4), sy, CHITIN[3]); r.fixed(sx + side * (rr + 1.4), sy - 1, CHITIN[2])
    fx, fy = ankle
    pts = [(fx, fy)]
    for k in range(3):
        fx += foot_dir * (3.6 - k * 0.4); fy += (3.6, 2.2, 1.6)[k]
        pts.append((fx, fy))
    for i in range(3):
        r.tube(pts[i], pts[i + 1], 3.0 - i * 0.5, 2.5 - i * 0.5, M['chitin'], lift=0.04, group=g + 'f')
    cx, cy = pts[-1]
    for k, (ox, oy) in enumerate(((1, -1), (2, 0), (2, 1), (3, 1))):
        r.fixed(cx + foot_dir * ox, cy + oy, CHITIN[3 if k < 2 else 1])
    r.fixed(cx - foot_dir * 2, cy + 1, CHITIN[2]); r.fixed(cx - foot_dir * 3, cy + 1, CHITIN[1])   # the back claw


def shaggy_pts(pts, top, bot, seed, step=2.6):
    """subdivide a polygon's outline and push every other vertex outward: tufts along the top, long hanging strands
    along the bottom (amp by which way the edge faces)"""
    cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
    out, n = [], len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        L = math.hypot(x1 - x0, y1 - y0); k = max(1, int(L / step))
        nx, ny = (y1 - y0) / (L or 1), -(x1 - x0) / (L or 1)
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        if (mx + nx - cx) ** 2 + (my + ny - cy) ** 2 < (mx - cx) ** 2 + (my - cy) ** 2: nx, ny = -nx, -ny
        amp = bot if ny > 0.45 else top
        for j in range(k):
            t = j / k
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            if j % 2:
                a = amp * (0.35 + 0.65 * (h32(int(x * 7), int(y * 7), seed) % 100) / 100)
                x, y = x + nx * a, y + ny * a + (a * 0.5 if ny > 0.45 else 0)
            out.append((x, y))
    return out


def shag(r, pts, mat, g, top=2.0, bot=5.0, seed=1, lift=0.0, ytop=None, tilt=0.0):
    yt = ytop if ytop is not None else min(p[1] for p in pts)
    def v(x, y):
        k = (x + int(2.5 * rig.nF(x * 0.7, y * 0.35 + seed * 9)))                   # strands wander
        strand = -0.18 if h32(k, y // 9, seed) % 6 == 0 else (0.07 if h32(k, y // 7, seed + 1) % 5 == 0 else 0)
        return strand - (y - yt) * 0.008
    return r.poly(shaggy_pts(pts, top, bot, seed), mat, lift=lift, round_=0.85, tilt=tilt, group=g, vfun=v)


def verrik(P, fi, decay=False):
    """decay=True: the Decay look -- the mantle gone brown-grey and patchy, the blooms wilted, the seed heads blown, dead
    leaves falling (frames 3-6) and lying at his feet, the glow-moss dimmer, the sickle dull, the wings tattered, the
    upper body stooped two pixels lower, the head pushed forward, the antennae drooping"""
    W, H = 128, 192
    b = P.get('b', 0)
    st = 2 if decay else 0
    U = lambda y: y - b + st                                                          # the upper body rises on a breath
    MOSSM, MOSSDKM = (M['dead'], M['deaddk']) if decay else (M['moss'], M['mossdk'])
    bloom = wilted if decay else flower
    # ---- the abdomen, behind and below (its own layer: the near wing folds over it): fat, ringed with tergites,
    # pointing back and down to the left
    ra = Rig(W, H)
    def ab_rings(x, y, u, w):
        s = ((u + 1.2) * 2.6) % 1.0
        return (-0.34 if s > 0.85 else 0.16 * (1 - s)) + (0.1 if w < -0.4 else -0.08 * max(0, w))
    ra.ellipsoid(36, 138, 17, 12.5, M['chitin'], rot=-0.7, group='abdomen', vfun=ab_rings, flat=0.9)
    ra.ellipsoid(22, 154, 7.0, 6.0, M['chitin'], rot=-0.8, group='abtip', lift=-0.06, vfun=ab_rings)
    ra.ellipsoid(16, 161, 3.4, 2.6, M['chitin'], rot=-0.8, group='abtip2', lift=-0.1)
    seam(ra, 'abtip', 0.2); seam(ra, 'abtip2', 0.2)
    abdomen = ra.render()
    r = Rig(W, H)
    S0, S1 = (56, 189), (106, 36)                                                      # the pole, butt to top
    sl = lambda y: S0[0] + (S0[1] - y) * (S1[0] - S0[0]) / (S0[1] - S1[1])
    # ---- legs, deep in a crouch: the far one, the thorax, the near one
    verrik_leg(r, (75, 130), (94, 148), (90, 177), 1, 'legF', False)
    r.ellipsoid(63, U(109), 17.5, 20, M['chitin'], group='torso', flat=0.85)
    r.ellipsoid(64, U(117), 11.0, 11, M['belly'], group='belly', clip=lambda x, y: y > U(106),
                vfun=lambda x, y, u, w: (-0.28 if (y - U(106)) % 5 == 4 else 0.04 * ((y - U(106)) % 5)))
    verrik_leg(r, (51, 130), (33, 149), (38, 178), -1, 'legN', True)
    # ---- moss rags hanging from the belt over the thighs
    top = 122
    for k, (x0, w, ln, dr) in enumerate(((37, 7, 22, -4), (43, 8, 30, -3), (50, 7, 34, -1), (56, 7, 26, 0), (62, 6, 31, 0),
                                         (68, 7, 27, 1), (74, 8, 24, 2), (81, 6, 19, 3))):
        pts = [(x0, top), (x0 + w, top), (x0 + w + dr * 0.5, top + ln * 0.7), (x0 + w * 0.75 + dr, top + ln),
               (x0 + w * 0.5 + dr, top + ln - 4), (x0 + w * 0.25 + dr, top + ln - 1), (x0 + dr * 0.6, top + ln * 0.72)]
        r.poly(pts, MOSSM if k % 2 else MOSSDKM, round_=0.6, lift=-0.04 - (k % 3) * 0.05, group='rag%d' % k,
               vfun=lambda x, y: (-0.2 if h32(x, y // 6, 9) % 5 == 0 else 0) - (y - top) * 0.006)
        seam(r, 'rag%d' % k, 0.16)
    r.tube((37, 123), (83, 124), 1.9, 1.9, M['wood'], group='belt', lift=-0.16,
           folds=lambda u, sd: -0.22 if (u * 13 + sd * 1.5) % 1.0 < 0.22 else 0.0)               # a twisted root belt
    # ---- the lantern of glow-moss on a short chain at the near hip
    lx, ly = 22, 128
    for k in range(10): r.fixed(38 - k * 1.6, 124 + k * 0.35, GOLD[2] if k % 2 else GOLD[0])
    glow = LANTERN[fi]
    dim = 2 if decay else 0                                                            # the glow-moss is starving
    r.ellipsoid(lx, ly + 7, 4.2, 5.8, M['glow'], lift=glow * 0.08 - dim * 0.14, group='lantglass', flat=0.6)
    for k in range(-1, 2): r.fixed(lx + k, ly + 9, GLOWG[max(0, min(6, 4 + glow - abs(k) - dim))])
    r.fixed(lx, ly + 7, GLOWG[max(0, min(6, 3 + glow - dim))]); r.fixed(lx - 1, ly + 10, GLOWG[max(0, 3 - dim)])
    r.poly([(lx - 3, ly - 1), (lx + 3, ly - 1), (lx + 4.5, ly + 2), (lx - 4.5, ly + 2)], M['gold'], round_=0.8, group='lant')
    r.ellipsoid(lx, ly - 2, 1.4, 1.1, M['gold'], group='lant')
    for xb in (lx - 4, lx - 1, lx + 2):
        for y in range(ly + 2, ly + 13):
            if group_at(r, xb, y) == 'lantglass': r.fixed(xb, y, GOLD[1] if xb > lx else GOLD[3])
    r.poly([(lx - 4.5, ly + 12.5), (lx + 4.5, ly + 12.5), (lx + 3, ly + 15), (lx - 3, ly + 15)], M['gold'], round_=0.8, group='lantb')
    # ---- the upper arms hang under the mantle (the forearms come after it)
    shF, elF = (86, U(88)), (93, U(106))
    r.tube(shF, elF, 6.0, 5.0, M['chitin'], group='armF', folds=plates(2))
    shN = (40, U(90))
    haN = (sl(118) + 0.5, 118)
    elN = ik(shN, haN, 20, 27, lambda e: e[1] - e[0] * 0.8)                           # the elbow hangs out at the side
    r.tube(shN, elN, 6.2, 5.0, M['chitin'], group='armN', folds=plates(2))
    r.ellipsoid(elN[0], elN[1], 4.8, 4.4, M['chitin'], group='armN')
    # ---- the mantle's back: a shaggy hump of moss rising behind the head (the shoulders are hunched)
    hump = [(27, 94), (30, 82), (37, 71), (46, 62), (56, 57), (64, 56), (72, 57), (82, 62), (91, 71), (98, 82), (101, 94), (64, 98)]
    shag(r, [(x, U(y)) for (x, y) in hump], MOSSM, 'hump', top=2.6, bot=3.0, seed=3, lift=-0.16)
    # ---- the head: chitin under a cap of moss, two big faceted eyes under stern brow plates, a heavy hooked beak
    hx, hy = 64 + (1 if decay else 0), U(65)
    r.ellipsoid(hx, hy, 12.5, 11, M['chitin'], group='head', flat=0.9, vfun=lambda x, y, u, w: -0.12 if u < -0.65 else 0)
    shag(r, [(hx - 13, hy - 4), (hx - 10, hy - 11), (hx - 2, hy - 14), (hx + 6, hy - 13), (hx + 12, hy - 8), (hx + 11, hy - 6),
             (hx + 2, hy - 8), (hx - 6, hy - 7), (hx - 11, hy + 2)], MOSSM, 'cap', top=2.0, bot=2.2, seed=5, lift=0.06)
    r.poly([(hx - 1.5, hy - 6), (hx + 4.5, hy - 6), (hx + 6.0, hy + 5), (hx + 4.5, hy + 8), (hx + 0, hy + 8), (hx - 2, hy + 4)],
           M['chitin'], lift=0.14, round_=0.8, group='frons', vfun=lambda x, y: -0.18 if x == hx + 1 and y > hy - 4 else 0)
    look = P.get('look', 0)
    EYES = ((hx - 6.4, hy + 0.5, 5.6, 6.6, -0.4, 'eyeN'), (hx + 9.4, hy - 0.2, 3.8, 6.2, 0.35, 'eyeF'))
    for (ex, ey, erx, ery, rot, g) in EYES:
        def facets(x, y, u, w):
            lat = -0.12 if (x + (y // 2)) % 2 == 0 and y % 2 == 0 else 0.0
            return lat + (0.16 if w < -0.4 else 0) - (0.16 if w > 0.45 else 0)
        r.ellipsoid(ex, ey, erx, ery, M['eye'], rot=rot, group=g, vfun=facets, flat=0.8)
        seam(r, g, 0.3)
        gx, gy = int(ex - erx * 0.3) + look, int(ey - ery * 0.35)
        r.fixed(gx, gy, (206, 214, 178)); r.fixed(gx + 1, gy, (170, 184, 136)); r.fixed(gx, gy + 1, (156, 172, 120))
        ps = (int(ex + 0.5 + look * 0.6), int(ey + 1.5))                               # the dark pseudopupil
        r.fixed(ps[0], ps[1], EYEG[1]); r.fixed(ps[0] + 1, ps[1], EYEG[2]); r.fixed(ps[0], ps[1] + 1, EYEG[2])
    for (x, y), e in list(r.buf.items()):                                             # the glow spills on the chitin
        if e[0] is M['chitin']:
            for (ex, ey, erx, ery, rot, g) in EYES:
                d = math.hypot(x + 0.5 - ex, (y + 0.5 - ey) * 0.85)
                if erx + 1.0 < d < erx + 3.2 and abs(y - hy) < 12: e[1] += 0.07
    for (pts, g) in (([(hx - 13.5, hy - 7.5), (hx - 6, hy - 9), (hx + 1.5, hy - 4.8), (hx + 1, hy - 2.6), (hx - 6, hy - 5.2), (hx - 12.5, hy - 4.2)], 'browN'),
                     ([(hx + 4.5, hy - 5.2), (hx + 9.5, hy - 8.6), (hx + 13.5, hy - 7.2), (hx + 13, hy - 4.6), (hx + 9.5, hy - 5.6), (hx + 5, hy - 3.0)], 'browF')):
        r.poly(pts, M['chitin'], lift=0.16, round_=0.5, tilt=-0.5, group=g)
        seam(r, g, 0.3)
    r.tube((hx + 2.5, hy + 2), (hx + 6.0, hy + 11), 4.0, 2.4, M['chitin'], lift=0.12, group='beak',
           folds=lambda u, sd: (0.2 if -0.6 < sd < -0.15 else 0) - (0.2 if sd > 0.55 else 0))
    r.tube((hx + 6.0, hy + 11), (hx + 5.5, hy + 15), 2.4, 0.8, M['chitin'], lift=0.05, group='beak')
    r.fixed(hx + 5, hy + 15, CHITIN[1]); r.fixed(hx + 4, hy + 14, CHITIN[2])
    for x in range(int(hx + 3), int(hx + 8)): r.darken(x, hy + 12, 0.18)
    for (mx, sx) in ((hx - 0.5, -1), (hx + 9.5, 1)):
        r.tube((mx, hy + 7), (mx + sx * 1.2, hy + 12), 1.7, 0.8, M['chitin'], lift=-0.04, group='mand%d' % sx)
        seam(r, 'mand%d' % sx, 0.22)
    seam(r, 'beak', 0.28)
    # the antennae: jointed twigs curving out and back, a bud and a side-twig each; the near one twitches
    ant = P.get('ant', 0)
    for (base, pts, tw) in (((hx - 2, hy - 11), [(-1, -6), (-4, -12), (-9, -18), (-15, -22), (-21, -24), (-25, -23)], 2),
                            ((hx + 4, hy - 12), [(2, -6), (6, -12), (11, -17), (17, -20), (22, -20), (25, -18)], 2)):
        q = [(base[0] + dx, base[1] + dy + (i * 0.7 if decay else 0)) for i, (dx, dy) in enumerate(pts)]   # they droop in Decay
        if ant and base[0] < hx:
            q[-1] = (q[-1][0] + 1, q[-1][1] - 3); q[-2] = (q[-2][0], q[-2][1] - 1)
        prev = base
        for i, pt in enumerate(q):
            r.tube(prev, pt, 1.3 - i * 0.09, 1.1 - i * 0.09, M['chitin'], lift=0.1, group='ant')
            prev = pt
        for pt in q[1:-1]: r.fixed(pt[0], pt[1], CHITIN[7])
        a, c = q[tw], q[tw + 1]
        r.tube(a, (a[0] + (c[0] - a[0]) * 0.2, a[1] - 5), 0.8, 0.6, M['chitin'], group='ant')
        bud = DEAD if decay else MOSS
        r.fixed(q[-1][0], q[-1][1], bud[7]); r.fixed(q[-1][0] + (1 if base[0] > hx else -1), q[-1][1], bud[5])
    # ---- the mantle's front: a shaggy drape over both shoulders and the chest, a V under the beak, a fringe below
    drape = [(25, 96), (28, 85), (35, 77), (45, 74), (53, 78), (60, 84), (64, 86), (69, 84), (75, 77), (84, 74), (94, 77),
             (101, 85), (103, 96), (97, 103), (86, 107), (74, 110), (64, 112), (54, 110), (42, 106), (31, 102)]
    shag(r, [(x, U(y)) for (x, y) in drape], MOSSM, 'mantle', top=2.2, bot=5.5 if not decay else 4.0, seed=7, ytop=U(74), lift=-0.06)
    for (x, y), e in list(r.buf.items()):
        if r.groups.get(e[2]) not in ('mantle', 'hump', 'cap'): continue
        hsh = h32(x // 3, y // 3, 41) % 7
        if decay:                                                                      # patchy: matted bald patches, a
            n = rig.nM(x * 1.6 + 40, y * 1.6)                                          # few tufts still sickly green
            if n < 0.3: e[0] = M['deaddk']; e[1] -= 0.06 + (0.3 - n) * 0.6
            elif n > 0.74 and r.groups.get(e[2]) != 'cap': e[0] = M['moss']; e[1] -= 0.16
            elif hsh == 1: e[1] += 0.06
            if h32(x, y, 43) % 37 == 0: r.fixed(x, y, OCHRE[1] if h32(x, y, 44) % 2 else DEAD[8])
            continue
        if hsh == 0: e[1] -= 0.12
        elif hsh == 1: e[1] += 0.07
        if h32(x, y, 43) % 41 == 0: r.fixed(x, y, OCHRE[3] if h32(x, y, 44) % 2 else CREAM[1])   # lichen, dry stalks
    for x in range(30, 100):                                                           # a dark crease where the drape lies on
        ys = [y for y in range(U(70), U(92)) if group_at(r, x, y) == 'mantle']         # the hump
        if ys and group_at(r, x, min(ys) - 1) == 'hump': r.darken(x, min(ys) - 1, 0.22)
    for (x, y, k) in ((36, 82, 'big'), (43, 78, 'aster'), (31, 89, 'big'), (39, 90, 'small'), (46, 85, 'small'),
                      (52, 93, 'daisy'), (58, 101, 'seed'), (78, 82, 'daisy'), (88, 80, 'aster'), (94, 88, 'small'),
                      (72, 99, 'aster'), (44, 98, 'seed'), (84, 93, 'daisy'), (64, 94, 'daisy'), (98, 85, 'seed'),
                      (27, 95, 'small'), (36, 72, 'aster'), (88, 68, 'daisy'), (52, 62, 'small'), (79, 62, 'seed')):
        bloom(r, x, U(y), k)
    for (x, y, k) in ((hx - 9, hy - 11, 'aster'), (hx - 2, hy - 14, 'daisy'), (hx + 5, hy - 13, 'small'), (hx - 13, hy - 4, 'seed')):
        bloom(r, x, y, k)
    # ---- the pole pruner: a crooked pole planted by the near foot, a curved sickle at its top
    knots = (0.22, 0.47, 0.71)
    r.tube(S0, S1, 2.0, 1.7, M['wood'], group='pole',
           folds=lambda u, sd: (0.16 if sd < -0.35 else 0) - (0.3 if any(abs(u - k) < 0.012 for k in knots) else 0))
    for k in knots:
        y = S0[1] + (S1[1] - S0[1]) * k; x = sl(y)
        r.ellipsoid(x, y, 2.6, 1.7, M['wood'], group='pole')
    r.tube((S1[0] - 0.8, S1[1] + 7), (S1[0], S1[1] + 1), 2.5, 2.5, M['gold'], group='ferrule',
           folds=lambda u, sd: -0.25 if 0.45 < u < 0.55 else 0)
    bcx, bcy, br = 113.0, 46.0, 10.5
    blade = {}
    for y in range(26, 64):
        for x in range(96, 128):
            d = math.hypot(x + 0.5 - bcx, y + 0.5 - bcy)
            a = math.atan2(y + 0.5 - bcy, x + 0.5 - bcx)
            if not (-2.75 <= a <= 0.95): continue
            t = (a + 2.75) / 3.7
            th = 3.8 * (1 - t) ** 0.8 + 0.6
            if br - 0.4 <= d <= br + th: blade[(x, y)] = (d - br) / th
    oid = r.new('blade')
    for (x, y), s in blade.items():
        r.put(x, y, M['steel'], 0.3 + (0.34 if s < 0.25 else 0) - s * 0.14 - (0.14 if decay else 0), oid)
        if decay and h32(x, y, 61) % 11 == 0 and s > 0.3: r.fixed(x, y, (96, 58, 32))   # specks of rust on a dulled blade
    glint = P.get('glint', 0)
    if glint and decay:                                                                # only a dull gleam now
        a = -2.0 if glint == 1 else -0.35
        gx, gy = bcx + math.cos(a) * (br + 0.3), bcy + math.sin(a) * (br + 0.3)
        r.fixed(gx, gy, STEEL[8]); r.fixed(gx + 1, gy, STEEL[6]); r.fixed(gx, gy + 1, STEEL[6])
    elif glint:
        a = -2.0 if glint == 1 else -0.35
        gx, gy = bcx + math.cos(a) * (br + 0.3), bcy + math.sin(a) * (br + 0.3)
        for (dx, dy, c) in ((0, 0, (250, 248, 232)), (1, 0, (210, 212, 202)), (-1, 0, (210, 212, 202)), (0, 1, (210, 212, 202)),
                            (0, -1, (210, 212, 202)), (2, 0, STEEL[8]), (-2, 0, STEEL[8]), (0, -2, STEEL[8]), (0, 2, STEEL[8])):
            r.fixed(gx + dx, gy + dy, c)
    for (x0, ln) in ((104, 7), (108, 4), (114, 9), (119, 5)):                          # moss hanging off the blade's back
        ys = [y for y in range(24, 64) if (x0, y) in blade]
        if not ys: continue
        t0 = min(ys)
        for k in range(ln):
            r.fixed(x0 + (1 if k > 5 else 0), t0 - 1 + k, (DEAD if decay else MOSS)[6 - min(5, k // 2)] if k else (DEAD if decay else MOSS)[7])
    # ---- the far forearm and hand, up the pole beside the shoulder
    haF = (sl(U(84)) + 0.5, U(84))
    r.tube(elF, (haF[0] + 1.5, haF[1] + 3), 5.0, 3.8, M['chitin'], group='foreF', folds=plates(2))
    r.tube((elF[0] - 0.4, elF[1] - 3), (haF[0] + 1.2, haF[1] + 9), 4.4, 4.0, MOSSM, group='cuffF', jag=0.2)
    seam(r, 'cuffF', 0.18)
    verrik_hand(r, haF, 'handF')
    # ---- the near forearm comes across the belly to the pole
    r.tube(elN, (haN[0] - 3, haN[1]), 4.8, 3.6, M['chitin'], group='foreN', folds=plates(2))
    r.tube((elN[0] + 3, elN[1] + 0.8), (elN[0] + 12, elN[1] + 3.2), 4.2, 4.0, MOSSM, group='cuffN', jag=0.25)
    seam(r, 'cuffN', 0.2); seam(r, 'foreN', 0.2)
    verrik_hand(r, haN, 'handN')
    seam(r, 'armN', 0.22)
    stage_light(r, 110, 0.004)
    body = r.render()
    # ---- the wings, behind everything (translucent); the near one folds over the abdomen
    wing = P.get('wing', 0)
    dn = [0.0, -0.07, 0.04][wing]
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    wN = wing_layer(W, H, (46, U(82)), math.radians(121) + dn, 80, 22, -1, sheen=wing * 0.5,
                    ghost=(math.radians(121) if wing == 1 else None), tatter=7 if decay else 0)
    wF = wing_layer(W, H, (84, U(84)), math.radians(63) - dn * 0.8, 78, 19, 1, sheen=wing * 0.5,
                    ghost=(math.radians(63) if wing == 1 else None), tatter=11 if decay else 0)
    lay = Image.alpha_composite(lay, wF)
    lay = Image.alpha_composite(lay, abdomen)
    lay = Image.alpha_composite(lay, wN)
    out = Image.alpha_composite(lay, body)
    if decay:                                                                          # dead leaves: lying, and falling
        for i, (x, y) in enumerate(LEAF_GROUND): leaf_px(out, x, y, 2, k=1 + i % 2)
        for path in LEAF_FALL:
            if fi in path:
                x, y, tb = path[fi]
                leaf_px(out, x, y, tb)
    return warm_ink(out)


# ======================================================================================================================
#  THE ANGLE CORRECTOR
# ======================================================================================================================
APOSE = [dict(b=0), dict(b=0), dict(b=0), dict(b=0), dict(b=1), dict(b=1, vis=2), dict(b=1, vis=1, tilt=1), dict(b=0, tap=1)]


def wear(y0, y1, seed=1, grime=0.16):
    """a plate's wear: darker toward its lower edge (grime settles), a few fine scratches and pits"""
    def v(x, y):
        t = (y - y0) / max(1.0, (y1 - y0))
        out = -grime * max(0.0, t - 0.45) * 1.8
        hh = h32(x, y, seed)
        if hh % 61 == 0: out -= 0.2                                                     # a pit
        if (x + y * 2) % 9 == 0 and h32(x // 3, y // 3, seed + 7) % 9 == 0: out -= 0.16  # a short scratch
        if hh % 47 == 1: out += 0.1
        return out
    return v


def pplate(r, pts, mat, g, round_=0.8, tilt=0.0, lift=0.0, seed=1, grime=0.16, extra=None):
    ys = [p[1] for p in pts]
    w = wear(min(ys), max(ys), seed, grime)
    return r.poly(pts, mat, lift=lift, round_=round_, tilt=tilt, group=g,
                  vfun=(lambda x, y: w(x, y) + extra(x, y)) if extra else w)


def gilt_line(r, pts, k=4, under=True):
    """an engraved gilt line along a run of points, with a dark cut under it"""
    for i in range(len(pts) - 1):
        for (x, y) in line_px(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]):
            r.fixed(x, y, GOLD[k] if (x + y) % 4 else GOLD[k - 1])
            if under: r.darken(x, y + 1, 0.14)


def angle_corrector(P, fi):
    """3/4 turned to the viewer's left (toward the hall's middle; he stands by the right column), the weight on the far
    leg (that hip up, that shoulder down), the near leg free and bent; the near gauntlet rests on the head of a tall
    brass T-square planted beside him like a staff, the far arm hangs close to his side"""
    W, H = 128, 192
    r = Rig(W, H)
    b = P.get('b', 0)
    U = lambda y: y - b
    fl = 57.5                                                                          # the body's front line (sternum)
    # ---- the far arm first: it hangs close behind the far side, the gauntlet relaxed by the thigh
    shF, elF, haF = (45, U(78)), (42, U(99)), (44.5, U(117))
    r.tube(shF, elF, 4.6, 4.2, M['slate'], group='armmailF')
    r.tube((shF[0] - 0.5, U(84)), (elF[0], elF[1] - 2), 5.0, 4.6, M['lime'], group='rereF',
           folds=lambda u, sd: (-0.24 if (u * 3) % 1 > 0.88 else 0) - (0.16 if sd > 0.3 else 0))
    r.tube(elF, haF, 4.5, 3.8, M['lime'], group='vambF', folds=lambda u, sd: (0.1 if sd < -0.4 else 0) - (0.14 if sd > 0.4 else 0))
    pplate(r, [(elF[0] - 4.5, elF[1] - 4), (elF[0] + 3, elF[1] - 4), (elF[0] + 3.5, elF[1] + 3), (elF[0] - 2, elF[1] + 5),
               (elF[0] - 6.5, elF[1] + 1)], M['lime'], 'couterF', round_=0.6, tilt=-0.3, lift=0.0, seed=17)
    r.tube((haF[0] + 0.3, haF[1] - 2), (haF[0], haF[1] + 0.5), 4.0, 3.8, M['gold'], lift=-0.16, group='cuffF')
    pplate(r, [(haF[0] - 3.5, haF[1]), (haF[0] + 3.5, haF[1]), (haF[0] + 3, haF[1] + 6), (haF[0] - 3, haF[1] + 6)], M['lime'], 'handF',
           round_=0.8, seed=31)
    for k in range(3):
        r.tube((haF[0] - 2.2 + k * 2.1, haF[1] + 5.5), (haF[0] - 2.4 + k * 2.1, haF[1] + 10 - k * 0.6), 1.15, 1.0, M['lime'], group='fingF%d' % k,
               folds=lambda u, sd: -0.2 if 0.45 < u < 0.58 else 0)
        seam(r, 'fingF%d' % k, 0.2)
    seam(r, 'couterF', 0.26); seam(r, 'vambF', 0.2)
    # ---- the legs: the far one straight under the weight, the near one free, the knee bent forward
    LEGS = (('F', (51.5, 118), (52.5, 122), (52, 147), (52, 150), (52, 154), (51.5, 180), (51.5, 180), -1, 6.6),
            ('N', (71.5, 121), (72, 124), (77, 147), (77.8, 150.5), (78, 155), (80.5, 181), (81, 181), -1, 7.2))
    for (k, mail, c0, c1, kc, g0, g1, ft, toe, rr) in LEGS:
        g = 'leg' + k
        r.tube(mail, (g1[0], 184), 5.2, 4.4, M['slate'], group=g + 'mail')
        r.tube(c0, c1, rr, rr - 1.0, M['lime'], group=g + 'c', folds=lambda u, sd: (-0.2 if u > 0.86 else 0) - (0.08 if sd > 0.5 else 0))
        r.tube(g0, g1, 5.4, 4.4, M['lime'], group=g + 'g',
               folds=lambda u, sd: (0.16 if -0.4 < sd < -0.12 else 0) - (0.2 if sd > 0.08 else 0) - (0.12 if u > 0.8 else 0))
        kx, ky = kc
        pplate(r, [(kx - 6, ky - 2), (kx - 0.5, ky - 5.5), (kx + 5.5, ky - 2), (kx + 4.5, ky + 2), (kx - 0.5, ky + 6.5), (kx - 5.5, ky + 2)],
               M['lime'], g + 'k', round_=0.8, tilt=-0.2, lift=0.06, seed=5)
        r.fixed(kx - 1, ky, GOLD[5]); r.fixed(kx, ky, GOLD[3]); r.fixed(kx - 1, ky + 1, GOLD[2])
        tx = ft[0]
        pplate(r, [(tx - 4.5, 179), (tx + 5, 179), (tx + 5.5, 186), (tx + 4, 189), (tx - 6, 189), (tx - 10.5, 188.5), (tx - 6, 184)],
               M['lime'], g + 's', round_=0.7, tilt=-0.6, lift=-0.04, seed=7)
        for y in (182, 185): r.darken(tx - 2, y, 0.12); r.darken(tx + 2, y, 0.12)
        seam(r, g + 'k', 0.24); seam(r, g + 's', 0.22); seam(r, g + 'c', 0.16)
    # ---- the tabard: sage cloth from the waist, swinging a little after the free knee; a gilt hem
    tab = [(fl - 6, U(104)), (fl + 7, U(104)), (fl + 9.5, 164), (fl + 4, 166), (fl - 4.5, 165.5)]
    r.poly(tab, M['sage'], round_=0.5, group='tabard',
           vfun=lambda x, y: (-0.22 if (x - int(fl)) in (-3, 4) and y > 122 else 0) + (0.08 if (x - int(fl)) in (-2, 5) and y > 122 else 0)
           - (0.1 if y > 158 else 0))
    for x in range(int(fl - 4), int(fl + 9)):
        yy = 165 + (0 if x < fl + 4 else -1)
        r.fixed(x, yy, GOLD[3] if x % 2 else GOLD[2]); r.fixed(x, yy - 1, GOLD[1])
    # ---- the faulds: three hoops of plate below the waist, sloping down to the free hip; tassets over the thighs
    for k, y in enumerate((104, 110, 116)):
        w0, w1 = 15 + k * 1.5, 16.5 + k * 1.5
        pts = [(fl - w0 * 0.75, U(y) - 0.5), (fl + w0 * 1.15, U(y) + 1), (fl + w1 * 1.15, U(y) + 8.5), (fl - w1 * 0.75, U(y) + 7)]
        pplate(r, pts, M['lime'], 'fauld%d' % k, round_=0.9, tilt=-0.15, seed=11 + k, grime=0.3)
        seam(r, 'fauld%d' % k, 0.26)
    for (tx, w, sk, top) in ((47, 5.5, -1, 121.5), (72, 8, 1.5, 124)):
        pplate(r, [(tx - w, top), (tx + w, top), (tx + w + sk, top + 15.5), (tx - w + sk, top + 16)], M['lime'], 'tasset%d' % tx,
               round_=0.8, seed=13, grime=0.3)
        seam(r, 'tasset%d' % tx, 0.26)
        gilt_line(r, [(tx - w + sk, top + 15.5), (tx + w + sk, top + 15)], k=3)
    # ---- the cuirass: the near side broad, the far side foreshortened, the ridge on the front line; the tracery of a
    # lancet window, the Lumen sun in its head
    chest = [(47, U(63)), (75, U(62)), (82.5, U(70)), (82, U(86)), (76, U(104)), (45.5, U(104)), (41.5, U(86)), (42.5, U(71))]
    pplate(r, chest, M['lime'], 'cuirass', round_=0.9, tilt=-0.1, seed=19, grime=0.22)
    for y in range(U(64), U(104)):
        r.darken(fl - 1, y, -0.18); r.darken(fl, y, 0.1)
    for y in range(U(64), U(104)):                                                     # the far side turns away: darker
        for x in range(40, int(fl) - 6): r.darken(x, y, 0.06)
    arch = [(fl - 6.5, U(100)), (fl - 6.5, U(84)), (fl - 5.5, U(79)), (fl - 3, U(74)), (fl + 0.5, U(71)), (fl + 5, U(74)),
            (fl + 8.5, U(79)), (fl + 9.5, U(84)), (fl + 9.5, U(100))]
    gilt_line(r, arch, k=4)
    gilt_line(r, [(fl - 6.5, U(100)), (fl + 9.5, U(100))], k=3)
    gilt_line(r, [(fl + 1.5, U(88)), (fl + 1.5, U(99))], k=4, under=False)
    for (x0, x1) in ((fl - 6.5, fl + 1.5), (fl + 1.5, fl + 9.5)):
        gilt_line(r, [(x0, U(89)), ((x0 + x1) / 2, U(85)), (x1, U(89))], k=3, under=False)
    sy, sx0 = U(79), fl + 1
    for (dx, dy, c) in ((0, 0, GOLD[6]), (-1, 0, GOLD[5]), (0, -1, GOLD[5]), (-1, -1, GOLD[6]), (1, 0, GOLD[3]), (0, 1, GOLD[3]),
                        (-1, 1, GOLD[4]), (1, -1, GOLD[4]), (1, 1, GOLD[2]), (-3, -1, GOLD[3]), (2, -1, GOLD[2]),
                        (-1, -3, GOLD[4]), (-1, 2, GOLD[2]), (-3, 1, GOLD[2]), (2, 1, GOLD[1])):
        r.fixed(sx0 + dx, sy + dy, c)
    gilt_line(r, [(45.5, U(103)), (76, U(103))], k=4)
    # ---- the near upper arm, under the pauldron
    tap = P.get('tap', 0)
    tqx, tqy = 96.0, U(92)                                                             # the T-square's head (its joint)
    shN, elN = (82, U(78)), (87, U(99))
    haN = (tqx - 1.5, tqy - 3)
    r.tube(shN, elN, 4.6, 4.4, M['slate'], group='armmailN')
    r.tube((shN[0] + 0.5, U(82)), (elN[0], elN[1] - 3), 5.4, 4.8, M['lime'], group='rereN',
           folds=lambda u, sd: (-0.24 if (u * 3) % 1 > 0.88 else 0) - (0.12 if u > 0.7 else 0))
    # ---- the gorget and the pauldrons (the far one lower: his weight is on that side), three lames, the top one swept
    # up into a spire at the outer corner
    pplate(r, [(49, U(57)), (70, U(57)), (73.5, U(64)), (46, U(64.5))], M['lime'], 'gorget', round_=0.9, seed=23,
           extra=lambda x, y: -0.16 if (y - U(57)) % 3 == 2 else 0)
    seam(r, 'gorget', 0.24)
    for (sx, inner0, outer0, drop) in ((-1, 50, 33.5, 2), (1, 70, 93, 0)):
        for k in (2, 1, 0):
            y0 = U(66) + k * 6.5 + drop
            inner, outer = inner0 + sx * k * 1.5, outer0 - sx * k * 1.2
            pts = [(inner, y0 + 1), (outer - sx * 3, y0), (outer, y0 + 3), (outer, y0 + 9.5), (inner + sx * 2, y0 + 10.5)]
            if k == 0:
                pts = [(inner, y0 + 1), (outer - sx * 7, y0 - 1), (outer + sx * 1, y0 - 5), (outer + sx * 1, y0 + 9.5), (inner + sx * 2, y0 + 11)]
            pplate(r, pts, M['lime'], 'paul%d_%d' % (sx, k), round_=0.75, tilt=-0.35, lift=0.0 - k * 0.04 - (0.06 if sx < 0 else 0),
                   seed=29 + k, grime=0.26)
            seam(r, 'paul%d_%d' % (sx, k), 0.3)
            gilt_line(r, [pts[-2], pts[-1]], k=4 if sx < 0 else 3)
    # ---- the ivy, trained in right angles up the near side of the breastplate
    path = [(77, U(110)), (77, U(97)), (71, U(97)), (71, U(88)), (76, U(88)), (76, U(79)), (72, U(79)), (72, U(72))]
    pix = []
    for i in range(len(path) - 1): pix += line_px(path[i][0], path[i][1], path[i + 1][0], path[i + 1][1])[(1 if i else 0):]
    for (x, y) in pix: r.fixed(x, y, IVY[1]); r.darken(x + 1, y + 1, 0.12)
    for i, (x, y) in enumerate(pix):
        if i % 4 != 2: continue
        nxt = pix[min(i + 1, len(pix) - 1)]
        horiz = nxt[1] == y
        side = 1 if (i // 4) % 2 else -1
        ox, oy = (0, side * 2) if horiz else (side * 2, 0)
        lx, ly = x + ox, y + oy
        for (dx_, dy_, k) in ((0, 0, 4), (-1, 0, 3), (1, 0, 2), (0, -1, 5), (0, 1, 1), (-1, -1, 4), (1, 1, 0)):
            r.fixed(lx + dx_, ly + dy_, IVY[k])
    # ---- the near forearm: the elbow close at his side, the forearm forward to the T-square's head
    wr = (haN[0] - 1, haN[1] + 4)
    r.tube(elN, wr, 4.8, 4.0, M['lime'], group='vambN', folds=lambda u, sd: (0.12 if -0.6 < sd < -0.2 else 0) - (0.12 if sd > 0.5 else 0))
    pplate(r, [(elN[0] - 3, elN[1] - 5), (elN[0] + 4, elN[1] - 5), (elN[0] + 7.5, elN[1] + 2), (elN[0] + 1, elN[1] + 5.5),
               (elN[0] - 3.5, elN[1] + 2)], M['lime'], 'couterN', round_=0.6, tilt=-0.3, lift=0.08, seed=17)
    r.fixed(elN[0] + 1, elN[1], GOLD[4])
    seam(r, 'vambN', 0.22); seam(r, 'couterN', 0.26)
    # ---- the T-square: a tall brass rule planted beside him, leaning a touch; its head a crossbar under his hand
    foot = (99.5, 188)
    dx, dy = tqx - foot[0], tqy - foot[1]; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    blade = [(tqx + nx * 2.4, tqy + ny * 2.4), (tqx - nx * 2.4, tqy - ny * 2.4), (foot[0] - nx * 1.9, foot[1] - ny * 1.9), (foot[0] + nx * 1.9, foot[1] + ny * 1.9)]
    r.poly(blade, M['brass'], round_=0.6, lift=0.0, group='rule',
           vfun=lambda x, y: -0.1 if h32(x, y, 3) % 13 == 0 else 0)
    for k in range(4, int(L) - 2, 3):                                                  # graduations along its edge
        px_, py_ = tqx - ux * k, tqy - uy * k
        ln = 3 if k % 15 == 4 else 2
        for j in range(ln): r.fixed(px_ + nx * (1.5 - j), py_ + ny * (1.5 - j), BRASS[0])
    head = [(tqx - 12, tqy - 3.5), (tqx + 10, tqy - 4.2), (tqx + 10, tqy + 1.8), (tqx - 12, tqy + 2.4)]
    r.poly(head, M['brass'], round_=0.3, tilt=-0.7, lift=0.06, group='tqhead',
           vfun=lambda x, y: (0.2 if y < tqy - 2.5 else 0) - (0.24 if y > tqy + 0.8 else 0))
    for x in (tqx - 10, tqx + 8): r.fixed(x, tqy - 1, BRASS[1]); r.fixed(x, tqy, BRASS[0]); r.fixed(x - 1, tqy - 1, BRASS[6])
    seam(r, 'tqhead', 0.28); seam(r, 'rule', 0.2)
    # the gauntlet laid over the head, fingers curled round its far edge
    x, y = haN
    r.tube((wr[0] + 1, wr[1]), (wr[0] - 0.4, wr[1] - 1.6), 4.3, 4.1, M['gold'], lift=-0.12, group='cuffN')
    pplate(r, [(x - 4.5, y - 3), (x + 4, y - 3.5), (x + 5, y + 1.5), (x - 4.5, y + 2)], M['lime'], 'handN', round_=0.7, tilt=-0.5, seed=31)
    r.fixed(x - 1, y - 1, GOLD[4]); r.fixed(x, y - 1, GOLD[2])
    for k in range(4):
        fx = x - 3.8 + k * 2.4
        up = -2 if (tap and k == 0) else 0
        r.tube((fx, y + 1.5 + up), (fx - 0.3, y + 5.0 + up), 1.25, 1.1, M['lime'], group='fingN%d' % k,
               folds=lambda u, sd: -0.22 if 0.45 < u < 0.58 else 0)
        seam(r, 'fingN%d' % k, 0.2)
    # ---- the helm: a lancet like the Directorate's windows, turned to the viewer's left: the faceplate and its lit
    # visor slit sit left of the helm's middle; a gilt crest
    hx, hy = 59.0, U(46)
    tilt = P.get('tilt', 0)
    helm = [(hx - 1, hy - 17), (hx + 5, hy - 12.5), (hx + 10, hy - 4.5), (hx + 11, hy + 4), (hx + 10, hy + 11), (hx + 6, hy + 14.5),
            (hx - 6.5, hy + 14.5), (hx - 9.5, hy + 11), (hx - 10.5, hy + 4), (hx - 9.5, hy - 5), (hx - 5.5, hy - 13)]
    pplate(r, helm, M['lime'], 'helm', round_=0.95, tilt=-0.2, seed=37, grime=0.12)
    fx = hx - 3.0
    face = [(fx - 5, hy - 4), (fx + 7.5, hy - 4.5), (fx + 8, hy + 6), (fx + 5, hy + 12), (fx - 3, hy + 12), (fx - 5.5, hy + 6)]
    pplate(r, face, M['lime'], 'face', round_=0.45, tilt=0.0, lift=0.06, seed=41, grime=0.1)
    seam(r, 'face', 0.32)
    for y in range(int(hy - 3), int(hy + 11)): r.darken(fx + 7, y, 0.12)              # the faceplate's turned edge
    vis = P.get('vis', 0)
    for x in range(int(fx - 4), int(fx + 7)):
        y = hy + 1 + (1 if (tilt and x < fx - 0) else 0)
        k = 1 + vis + (1 if abs(x + 0.5 - (fx + 1)) < 3 else 0)
        r.fixed(x, y, VISOR[min(5, k)]); r.fixed(x, y - 1, LIME[0]); r.darken(x, y + 1, 0.2)
    gilt_line(r, [(hx - 1.5, hy - 16), (fx + 1, hy - 5)], k=5, under=False)
    for k in range(3):
        for dx in (-2, 3): r.fixed(fx + dx, hy + 5 + k * 2, LIME[1])
    stage_light(r, 96, 0.004)
    im = r.render()
    # ---- the gilt ring over the helm, turning; graduations like a goniometer
    ring = Image.new('RGBA', (W, H), (0, 0, 0, 0)); p = ring.load()
    rcx, rcy, rx, ry = 58.5, U(24) + 0.0, 18.5, 4.4
    phase = (fi % 4) / 4.0                                                             # frames k and k+4 share the ring's angle
    for i in range(900):
        a = i / 900 * 2 * math.pi
        x, y = rcx + rx * math.cos(a), rcy + ry * math.sin(a)
        front = math.sin(a) > 0
        c = (GOLD[6] if math.cos(a) < -0.5 else GOLD[5]) if front else GOLD[3]
        p[int(x), int(y)] = c + (255,)
    for k in range(16):
        a = (k + phase) / 16 * 2 * math.pi
        front = math.sin(a) > 0
        x2, y2 = rcx + (rx + 1.5) * math.cos(a), rcy + (ry + 1.5) * math.sin(a)
        col = (GOLD[6] if math.cos(a) < -0.3 else GOLD[5]) if front else GOLD[2]     # all alike: the loop is seamless
        p[int(x2), int(y2)] = col + (255,)
    out = Image.alpha_composite(ring, im)
    return warm_ink(out)


# ======================================================================================================================
#  SELDO THRICE-CORRECTED
# ======================================================================================================================
SPOSE = [dict(b=0), dict(b=1), dict(b=1, rustle=1), dict(b=0, tick=1), dict(b=0, tick=1, tilt=1), dict(b=0, flut=1),
         dict(b=1, blink=1), dict(b=0)]
NS = (-0.75, -0.2, 0.62)                                                               # a side facet turned to the light
NFR = (0.28, -0.12, 0.95)                                                              # a front facet, a little away
NSH = (0.8, -0.1, 0.58)                                                                # a facet turned away (shade)


def paper_v(rules=False, print_=False, seed=1, y0=0):
    """a facet's printed matter: faint ruled lines, rows of tiny type"""
    def v(x, y):
        out = 0.0
        if rules and (y - y0) % 4 == 3: out -= 0.07
        if print_ and (y - y0) % 4 == 1 and h32(x // 2, y, seed) % 3 and h32(x, y, seed + 1) % 4: out -= 0.11
        return out
    return v


def ink_marks(r, marks):
    for (x, y, c) in marks: r.fixed(x, y, c)


def seldo(P, fi):
    W, H = 128, 192
    r = Rig(W, H)
    b = P.get('b', 0)
    U = lambda y: y - b
    rus = P.get('rustle', 0)
    # ---- the far arm hangs at his side, half behind the coat
    shF, elF, haF = (79, U(69)), (83, U(92)), (82, U(113))
    for (a0, a1, w0, w1, g) in ((shF, elF, 3.6, 3.2, 'uarmF'), (elF, haF, 3.2, 2.6, 'farmF')):
        dx, dy = a1[0] - a0[0], a1[1] - a0[1]; L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
        facet(r, [(a0[0] - nx * w0, a0[1] - ny * w0), (a0[0], a0[1]), (a1[0], a1[1]), (a1[0] - nx * w1, a1[1] - ny * w1)], M['paper'], NFR, group=g,
              lift=-0.06)
        facet(r, [(a0[0], a0[1]), (a0[0] + nx * w0, a0[1] + ny * w0), (a1[0] + nx * w1, a1[1] + ny * w1), (a1[0], a1[1])], M['paper'], NSH, group=g,
              lift=-0.06)
        seam(r, g, 0.18)
    facet(r, [(haF[0] - 2.5, haF[1]), (haF[0] + 2.5, haF[1]), (haF[0] + 3, haF[1] + 6), (haF[0] + 1, haF[1] + 9), (haF[0] - 2, haF[1] + 7)],
          M['paper'], NSH, group='handF', lift=0.02)
    # ---- the legs: long folded prisms; the weight on the far one, the near one free, its knee bent forward
    LEGS = (('F', (68, 119), (69, 152), (67, 182), 1), ('N', (58, 120), (51, 151), (55, 182), 0))
    for (k, hip, knee, ank, far) in LEGS:
        for (a0, a1, w0, w1, part) in ((hip, knee, 4.8, 3.5, 't'), (knee, ank, 3.4, 2.6, 's')):
            g = 'leg' + k + part
            dx, dy = a1[0] - a0[0], a1[1] - a0[1]; L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
            facet(r, [(a0[0] - nx * w0, a0[1] - ny * w0), (a0[0], a0[1]), (a1[0], a1[1]), (a1[0] - nx * w1, a1[1] - ny * w1)], M['paper'],
                  NS if not far else NFR, group=g, lift=-0.04 * far, vfun=paper_v(rules=(part == 't'), y0=1))
            facet(r, [(a0[0], a0[1]), (a0[0] + nx * w0, a0[1] + ny * w0), (a1[0] + nx * w1, a1[1] + ny * w1), (a1[0], a1[1])], M['paper'],
                  NSH if far else NFR, group=g, lift=-0.04 * far)
            for (x, y) in line_px(a0[0], a0[1], a1[0], a1[1])[1:-1]: r.darken(x, y, -0.1)     # the fold catches the light
            seam(r, g, 0.2)
        # the shoe: a folded point toward the viewer's right
        ax, ay = ank
        facet(r, [(ax - 3, ay - 1), (ax + 3, ay - 1), (ax + 11, 188.5), (ax + 1, 189), (ax - 3.5, 189)], M['paper'], (0.1, -0.85, 0.5),
              group='shoe' + k, lift=-0.04)
        facet(r, [(ax - 3.5, 187.5), (ax + 11, 188.5), (ax + 10, 189.6), (ax - 3.5, 189.6)], M['paper'], NSH, group='shoe' + k, lift=-0.1)
        seam(r, 'shoe' + k, 0.24)
    # a red correction on the near thigh: a struck line, a caret
    ink_marks(r, [(50, 132, PINK[2]), (51, 131, PINK[2]), (52, 131, PINK[3]), (53, 130, PINK[2]), (54, 130, PINK[1]),
                  (51, 134, PINK[1]), (52, 133, PINK[2]), (53, 134, PINK[1])])
    # ---- the coat-tail: paper flaps folded out below the waist, alternately lit and shaded
    n = 8                                                                              # accordion pleats, folded alternately
    for i in range(n):                                                                 # toward and away from the light
        t0, t1 = i / n, (i + 1) / n
        wx0, wx1 = 53 + 20 * t0, 53 + 20 * t1
        hx0, hx1 = 44 + 41 * t0, 44 + 41 * t1
        lift_ = (1 if (rus and i % 2 == 0) else 0)
        hy0 = 124 + 6 * math.sin(math.pi * t0) - (2 if i % 2 == 0 else 0) - lift_
        hy1 = 124 + 6 * math.sin(math.pi * t1) - (2 if i % 2 else 0) - (1 if (rus and i % 2) else 0)
        nn = (-0.55, -0.15, 0.82) if i % 2 == 0 else (0.5, -0.05, 0.86)
        facet(r, [(wx0, U(102)), (wx1, U(102)), (hx1, hy1), (hx0, hy0)], M['paper'], nn, group='tail%d' % i,
              vfun=paper_v(rules=(i % 3 == 1), y0=103 + i), lift=0.04 - 0.012 * i)
        if i % 2 == 0:
            for (x, y) in line_px(wx1, U(103), hx1, hy1 - 1): r.darken(x, y, -0.1)    # the ridge between two pleats
    for i in range(n): seam(r, 'tail%d' % i, 0.08)
    # a faded round stamp on a flap
    for a in range(0, 360, 30):
        x, y = 68 + 3.2 * math.cos(math.radians(a)), 119 + 3.0 * math.sin(math.radians(a))
        r.darken(x, y, 0.1)
    # ---- the torso: a folded jacket -- the lit side panel, the front, the waist pinched
    side = [(41, U(64)), (57, U(63)), (58, U(102)), (53, U(103)), (49, U(88)), (44, U(72))]
    front = [(57, U(63)), (84, U(65)), (81, U(74)), (76, U(88)), (73, U(103)), (58, U(102))]
    facet(r, side, M['paper'], NS, group='torsoS', vfun=paper_v(print_=True, seed=3, y0=U(63)))
    facet(r, front, M['paper'], NFR, group='torsoF', vfun=paper_v(rules=True, print_=True, seed=5, y0=U(63)))
    for (x, y) in line_px(57, U(64), 58, U(101)): r.darken(x, y, -0.14)
    for (x, y) in line_px(64, U(86), 72, U(100)): r.darken(x, y, 0.1); r.darken(x + 1, y, -0.08)   # a fold across the belly
    seam(r, 'torsoF', 0.14)
    # the first correction: a red strike-through on the jacket's front, a word written over it
    ink_marks(r, [(x, U(93), PINK[2]) for x in range(67, 75)] + [(69, U(91), PINK[1]), (70, U(90), PINK[2]), (71, U(91), PINK[1]),
                                                               (72, U(90), PINK[2]), (73, U(91), PINK[1])])
    # ---- the collar: two big folded lapels, standing up round the neck
    facet(r, [(48, U(60)), (58, U(62)), (59, U(76)), (50, U(70))], M['paper'], (-0.5, -0.5, 0.7), group='lapelS', lift=0.04)
    facet(r, [(58, U(62)), (78, U(61)), (70, U(72)), (59, U(76))], M['paper'], (0.2, -0.55, 0.8), group='lapelF', lift=0.02)
    seam(r, 'lapelS', 0.2); seam(r, 'lapelF', 0.2)
    # ---- the sash: a folded band from the far shoulder down across the chest to the near hip, two-tone along its fold
    s0, s1 = (81, U(66)), (52, U(100))
    dx, dy = s1[0] - s0[0], s1[1] - s0[1]; L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    wv = 1 if rus else 0
    facet(r, [(s0[0] + nx * 3.5, s0[1] + ny * 3.5), (s0[0], s0[1]), (s1[0], s1[1]), (s1[0] + nx * 3.5, s1[1] + ny * 3.5 + wv)], M['paper'],
          (-0.2, -0.75, 0.6), group='sash', lift=0.08)
    facet(r, [(s0[0], s0[1]), (s0[0] - nx * 3.5, s0[1] - ny * 3.5), (s1[0] - nx * 3.5, s1[1] - ny * 3.5 + wv), (s1[0], s1[1])], M['paper'],
          (0.15, 0.2, 0.96), group='sash', lift=-0.04)
    seam(r, 'sash', 0.24)
    for i in range(0, int(L), 7):                                                       # its printed border dashes
        x, y = s0[0] + dx * i / L - nx * 2, s0[1] + dy * i / L - ny * 2
        r.darken(x, y, 0.1)
    # the brass paperclip at the shoulder
    cx_, cy_ = 78, U(63)
    for (x, y, c) in ((cx_, cy_, BRASS[6]), (cx_, cy_ + 1, BRASS[5]), (cx_, cy_ + 2, BRASS[5]), (cx_, cy_ + 3, BRASS[4]), (cx_ + 1, cy_ + 4, BRASS[3]),
                      (cx_ + 2, cy_ + 3, BRASS[3]), (cx_ + 2, cy_ + 2, BRASS[4]), (cx_ + 2, cy_ + 1, BRASS[5]), (cx_ + 1, cy_, BRASS[6]),
                      (cx_ + 2, cy_ - 1, BRASS[7]), (cx_ + 3, cy_, BRASS[5]), (cx_ + 3, cy_ + 1, BRASS[4])):
        r.fixed(x, y, c)
    # ---- the near arm: the elbow down at his side, the forearm up -- he holds a folded permit up beside him between two
    # fingers, the way one shows a card that settles an argument
    shN, elN, haN = (44, U(68)), (40, U(90)), (32, U(72))
    for (a0, a1, w0, w1, g) in ((shN, elN, 3.8, 3.3, 'uarmN'), (elN, haN, 3.2, 2.5, 'farmN')):
        dx, dy = a1[0] - a0[0], a1[1] - a0[1]; L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
        facet(r, [(a0[0] - nx * w0, a0[1] - ny * w0), (a0[0], a0[1]), (a1[0], a1[1]), (a1[0] - nx * w1, a1[1] - ny * w1)], M['paper'],
              NS if g == 'uarmN' else (0.4, 0.2, 0.9), group=g, lift=0.04)
        facet(r, [(a0[0], a0[1]), (a0[0] + nx * w0, a0[1] + ny * w0), (a1[0] + nx * w1, a1[1] + ny * w1), (a1[0], a1[1])], M['paper'],
              NFR if g == 'uarmN' else (-0.7, -0.2, 0.68), group=g, lift=0.04)
        for (x, y) in line_px(a0[0], a0[1], a1[0], a1[1])[1:-1]: r.darken(x, y, -0.1)
        seam(r, g, 0.24)
    # the third correction: a red tick on the forearm
    ink_marks(r, [(35, U(82), PINK[2]), (36, U(83), PINK[3]), (37, U(82), PINK[2]), (38, U(81), PINK[2]), (39, U(80), PINK[1])])
    hx_, hy_ = haN
    facet(r, [(hx_ - 2.5, hy_ + 2), (hx_ + 2.5, hy_ + 2.5), (hx_ + 3, hy_ - 2), (hx_ - 1, hy_ - 3.5)], M['paper'], (-0.4, -0.3, 0.86),
          group='handN', lift=0.08)
    flut = P.get('flut', 0)
    card = Mat(CREAM, 'paper', 0.3)
    pp = [(hx_ - 4, hy_ - 15), (hx_ + 4, hy_ - 16 + flut), (hx_ + 4.5, hy_ - 4 + flut), (hx_ - 3, hy_ - 3)]
    facet(r, pp, card, (0.2, -0.3, 0.93), group='permit', lift=-0.02)
    fold = [(hx_ - 4, hy_ - 15), (hx_ - 3, hy_ - 3), (hx_ - 7, hy_ - 5), (hx_ - 8, hy_ - 14)]          # folded once: the back leaf
    facet(r, fold, card, (-0.7, -0.3, 0.65), group='permit', lift=0.12)
    for k in range(4): r.fixed(hx_ - 2 + k * 1.5, hy_ - 13 + k * 0.1 + (flut if k > 2 else 0), CREAM[1])   # lines of type
    for k in range(3): r.fixed(hx_ - 2 + k * 1.5, hy_ - 11 + k * 0.1 + (flut if k > 1 else 0), CREAM[1])
    for k in range(4): r.fixed(hx_ - 2 + k * 1.5, hy_ - 9 + k * 0.1 + (flut if k > 2 else 0), CREAM[1])
    for (x, y, c) in ((hx_ + 1, hy_ - 6 + flut, PINK[2]), (hx_ + 2, hy_ - 6 + flut, PINK[3]), (hx_ + 1, hy_ - 5 + flut, PINK[1]),
                      (hx_ + 2, hy_ - 5 + flut, PINK[2])):
        r.fixed(x, y, c)                                                                # a small red seal on it
    seam(r, 'permit', 0.26)
    for k in range(2):                                                                  # the thumb and a finger pinching it
        r.tube((hx_ - 0.5 + k * 1.8, hy_ - 1.5), (hx_ - 0.5 + k * 1.8, hy_ - 5), 0.95, 0.85, M['paper'], lift=0.12, group='pinch%d' % k)
        seam(r, 'pinch%d' % k, 0.22)
    seam(r, 'handN', 0.22)
    # ---- the neck and the head: folded like a paper bird's -- a crest swept up and back, a narrow face turned to the
    # viewer's right, four planes meeting in one fold point
    tilt = P.get('tilt', 0)
    hb = U(58)
    facet(r, [(58, hb + 5), (65, hb + 5), (64.5, hb - 2), (58.5, hb - 2)], M['paper'], NFR, group='neck', lift=-0.14)
    A = (39 + tilt, U(38) + tilt)                                                      # the crest's tip, swept back
    B = (75 + tilt, U(43) + tilt * 0.5)                                                # the brow's front corner
    C = (71 + tilt * 0.5, U(59))                                                       # the chin
    D = (52, U(57))                                                                    # the nape
    F = (62 + tilt * 0.6, U(46) + tilt * 0.3)                                          # the fold point
    facet(r, [A, F, D], M['paper'], (-0.4, 0.1, 0.9), group='headS', lift=-0.02)       # the side, under the crest
    facet(r, [A, B, F], M['paper'], (-0.3, -0.85, 0.45), group='headT', lift=0.0)      # the top plane, catching the light
    facet(r, [F, B, C], M['paper'], (0.1, -0.15, 0.98), group='headF', lift=0.12, vfun=paper_v(print_=True, seed=9, y0=U(44)))
    facet(r, [D, F, C], M['paper'], (-0.1, 0.65, 0.75), group='headJ', lift=0.0)      # the jaw plane, under
    for (p0, p1, dv) in ((A, F, -0.18), (F, B, -0.12), (F, C, 0.12), (F, D, -0.06)):
        for (x, y) in line_px(p0[0], p0[1], p1[0], p1[1])[1:-1]: r.darken(x, y, dv)    # the folds: ridges lit, valleys dark
    for g in ('headS', 'headT', 'headF', 'headJ'): seam(r, g, 0.1)
    # the face: two narrow slit eyes with a light behind them, a small fold of a mouth
    blink = P.get('blink', 0)
    ey = U(48) + (1 if tilt else 0)
    for (ex, w) in ((65 + tilt, 3), (70 + tilt, 3)):
        for x in range(ex, ex + w):
            if blink:
                r.fixed(x, ey, PAPER[4])
            else:
                r.fixed(x, ey, PAPER[1]); r.fixed(x, ey - 1, PAPER[3])
        if not blink: r.fixed(ex + 1, ey, (228, 206, 140)); r.fixed(ex + 2, ey, (176, 150, 92))
    mx = 68 + tilt
    r.fixed(mx, ey + 6, PAPER[2]); r.fixed(mx + 1, ey + 6, PAPER[2]); r.fixed(mx + 2, ey + 5, PAPER[3])   # a thin, knowing mouth
    # the second correction: a red caret and a stroke on the brow, as if the face itself had been edited
    ink_marks(r, [(66 + tilt, ey - 3, PINK[2]), (67 + tilt, ey - 4, PINK[3]), (68 + tilt, ey - 3, PINK[2]),
                  (70 + tilt, ey - 4, PINK[1]), (71 + tilt, ey - 4, PINK[2]), (72 + tilt, ey - 4, PINK[1])])
    stage_light(r, 100, 0.0035)
    body = r.render()
    # ---- the protractor arc behind the head: a brass half-ring with graduations, its base line, the needle, the lamp
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); p = lay.load()
    acx, acy, ar = 60.0, U(46) + 0.0, 28.0
    for i in range(600):
        a = math.pi + i / 599 * math.pi
        x, y = acx + ar * math.cos(a), acy + ar * math.sin(a)
        p[int(x), int(y)] = (BRASS[6] if math.cos(a) < 0 else BRASS[4]) + (235,)
    for k in range(19):                                                                 # every 10 degrees, longer every 30
        a = math.pi + k / 18 * math.pi
        ln = 4 if k % 3 == 0 else 2
        for j in range(1, ln + 1):
            x, y = acx + (ar - j) * math.cos(a), acy + (ar - j) * math.sin(a)
            p[int(x), int(y)] = BRASS[5 if k % 3 == 0 else 3] + (220,)
    for x in range(int(acx - ar), int(acx + ar + 5)):                                   # the base line, dashed
        if x % 3 != 2: p[x, int(acy)] = BRASS[3] + (200,)
    na = math.radians(-58 - (10 if P.get('tick') else 0))
    for t in range(0, int(ar - 3)):
        x, y = acx + t * math.cos(na), acy + t * math.sin(na)
        p[int(x), int(y)] = BRASS[5] + (210,)
    lx, ly = int(acx + ar + 6), int(acy)
    bright = 1 if P.get('tick') else 0
    for y in range(ly - 4, ly + 5):                                                     # the lamp's glow
        for x in range(lx - 4, lx + 6):
            d = math.hypot(x - lx - 0.5, y - ly)
            if d < 4.5 and p[x, y][3] == 0: p[x, y] = (240, 214, 140, int((60 + 30 * bright) * (1 - d / 4.5)))
    for (dx, dy, c) in ((0, 0, (255, 240, 196)), (1, 0, (244, 214, 140)), (0, 1, (232, 196, 120)), (1, 1, (204, 164, 92))):
        p[lx + dx, ly + dy - 1] = (c if bright else mix(c, BRASS[6], 0.3)) + (255,)
    out = Image.alpha_composite(lay, body)
    return warm_ink(out)


# ======================================================================================================================
#  sheets, palette, CLI
# ======================================================================================================================
CAST = {'verrik': (verrik, VPOSE, 128, 192), 'verrik_decay': (lambda P, fi: verrik(P, fi, decay=True), VPOSE, 128, 192), 'angle_corrector': (angle_corrector, APOSE, 128, 192),
        'seldo': (seldo, SPOSE, 128, 192)}


def sheet(frames, path):
    w, h = frames[0].size
    s = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, im in enumerate(frames): s.paste(im, (i * w, 0))
    s.save(path)


def write_gpl(path):
    ALL = ([INK, WARM_INK, WINGM, WINGV, PRINT] + CHITIN + CHBELL + MOSS + MOSSDK + ASTER + CREAM + OCHRE + WOOD + STEEL + GOLD
           + EYEG + GLOWG + DEAD + DEADDK + WILT + WCREAM + LEAF + LIME + SLATE + SAGE + IVY + VISOR + PAPER + PINK)
    seen, rows = set(), []
    for c in ALL:
        if c not in seen: seen.add(c); rows.append('%3d %3d %3d\t#%02x%02x%02x' % (c + c))
    open(path, 'w').write('GIMP Palette\nName: lumen_cast\nColumns: 8\n#\n' + '\n'.join(rows) + '\n')


if __name__ == '__main__':
    which = sys.argv[2:] or list(CAST)
    for name in which:
        fn, poses, w, h = CAST[name]
        os.makedirs(f'{OUT}/{name}', exist_ok=True)
        frames = [fn(p, i) for i, p in enumerate(poses)]
        for i, im in enumerate(frames): im.save(f'{OUT}/{name}/{i}.png')
        sheet(frames, f'{OUT}/{name}.png')
    write_gpl(f'{OUT}/lumen_cast.gpl')
    print('ok', OUT)
