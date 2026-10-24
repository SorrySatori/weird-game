"""Feral Toast -- the Screaming Cork Club band as animated pixel-art sprites (scale 1, feet on the canvas bottom).
Each sheet: frames 0-3 idle (breath, blink), 4-11 playing (8 frames, two per beat of feral-toast.mp3, ~177 BPM).
  telka   128x176  lead guitar: olive tentacle-faced punk, studded leather jacket, ripped denim, combat boots,
                   a creature-faced guitar; strums and headbangs, the tentacles swing
  bass_xl 144x192  Bass Player XL: a tall worn steel robot (pauldrons, pistons, cables, an "XL" stencil, a visor),
                   sunburst bass held properly -- fretting hand under the neck; mechanical knee-bob, plucking
  karlis  176x176  Fluffy Karlis: a shaggy bear in a patched leather vest and a band tee behind a full kit;
                   a groove that ends on a crash (the cymbal wobbles into the loop, he roars)
  mira    144x176  Mira Dron: a deep hood with glowing eyes, a knitted fringed scarf, long pale fingers on an eldritch
                   synth (keys, knobs, patch cables, running lights, a swirl screen, a horned skull), tentacles beside it
Drawn with rig.py (volumes -> tone buffer -> cast shadows, contact lines, material texture, dither, warm outline);
the arms are posed by two-bone IK onto the instrument, so the hands always land on strings, frets, drums and keys.
python3 feral_toast.py <outdir> [ids]  ->  <id>.png sheets + <id>/<n>.png frames + club.gpl"""
import sys, os, math
from PIL import Image
from common import FONT
from symbionts import curve
from rig import Rig, norm
from pal_club import *

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'

def lerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

def ik(S, H, L1, L2, side):
    """elbow for shoulder S and hand H; side = which way the elbow points ('down', 'up', 'left', 'right')"""
    dx, dy = H[0] - S[0], H[1] - S[1]
    d0 = math.hypot(dx, dy) or 1e-6
    ux, uy = dx / d0, dy / d0
    d = min(d0, L1 + L2 - 0.01)
    a = (L1 * L1 - L2 * L2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, L1 * L1 - a * a))
    e1 = (S[0] + ux * a - uy * h, S[1] + uy * a + ux * h)
    e2 = (S[0] + ux * a + uy * h, S[1] + uy * a - ux * h)
    key = side if callable(side) else {'down': lambda e: e[1], 'up': lambda e: -e[1], 'left': lambda e: -e[0], 'right': lambda e: e[0]}[side]
    return max((e1, e2), key=key)

def worm(r, pts, r0, r1, mat, group, cups=None, lift=0.0):
    """a tapered, curving limb (tentacles) as a chain of tubes of one group"""
    n = len(pts) - 1
    for i in range(n):
        r.tube(pts[i], pts[i + 1], r0 + (r1 - r0) * i / n, r0 + (r1 - r0) * (i + 1) / n, mat, lift=lift, group=group)
    if cups:
        for i in range(2, n, 2):
            r.fixed(pts[i][0] + cups[0], pts[i][1] + cups[1], cups[2])

def creases(lo, k=-0.2, every=3):
    return lambda t, side: k if t > lo and int(t * 40 + side * 2) % every == 0 else 0

def text(r, s, x, y, color):
    cx = x
    for ch in s:
        rows = FONT[ch]
        for j, row in enumerate(rows):
            for i, bit in enumerate(row):
                if bit == '1': r.fixed(cx + i, y + j, color)
        cx += len(rows[0]) + 1

class Inst:
    """a guitar / bass in its own frame: u along the neck (towards the headstock), v across it (+v = below the neck)"""
    def __init__(s, O, ang):
        s.O, s.U, s.ang = O, (math.cos(ang), math.sin(ang)), ang
        s.V = (-s.U[1], s.U[0])
    def P(s, u, v):
        return (s.O[0] + s.U[0] * u + s.V[0] * v, s.O[1] + s.U[1] * u + s.V[1] * v)
    def local(s, x, y):
        px, py = x + 0.5 - s.O[0], y + 0.5 - s.O[1]
        return px * s.U[0] + py * s.U[1], px * s.V[0] + py * s.V[1]

def instrument(r, g, bodies, cuts, neck0, neck_len, head_len, body_mat, face=None, head_mat='maple', strings=4,
               pickups=((2, 5), (10, 13)), guard=None):
    end = neck0 + neck_len
    corners = [g.P(u, v) for u in (-34, end + head_len + 2) for v in (-20, 20)]
    x0, x1 = int(min(p[0] for p in corners)), int(max(p[0] for p in corners)) + 1
    y0, y1 = int(min(p[1] for p in corners)), int(max(p[1] for p in corners)) + 1
    ob, on = r.new('guitar'), r.new('guitar')
    for y in range(max(0, y0), min(r.h, y1)):
        for x in range(max(0, x0), min(r.w, x1)):
            u, v = g.local(x, y)
            best = None
            for (cu, cv, ru, rv) in bodies:
                d = ((u - cu) / ru) ** 2 + ((v - cv) / rv) ** 2
                if d <= 1 and (best is None or d < best[0]): best = (d, (u - cu) / ru, (v - cv) / rv)
            if best and not any((u - cu) ** 2 + (v - cv) ** 2 <= cr * cr for (cu, cv, cr) in cuts):
                d, nu, nv = best
                e = max(0.0, d - 0.72) / 0.28 * 1.6                      # a flat top with a rounded bevel at the rim
                n = norm(((g.U[0] * nu + g.V[0] * nv) * e, (g.U[1] * nu + g.V[1] * nv) * e, 1.0))
                val = r.shade(M[body_mat], n) - (0.1 if d > 0.93 else 0)
                f = face(u, v, d) if face else None
                if isinstance(f, tuple): r.put(x, y, None, 0, ob, f); continue
                if guard and guard(u, v, d): r.put(x, y, None, 0, ob, BONE2[4] if v < 6 else BONE2[3]); continue
                if any(a <= u <= b for (a, b) in pickups) and abs(v) <= 3.4:
                    pole = any(abs(u - (a + b) / 2) < 0.6 for (a, b) in pickups)
                    r.put(x, y, None, 0, ob, STEEL[6] if pole and int(v + 9) % 2 == 0 else TEE[1]); continue
                if -9.5 <= u <= -7.5 and abs(v) <= 4: r.put(x, y, None, 0, ob, STEEL[6] if u > -8.5 else STEEL[3]); continue
                r.put(x, y, M[body_mat], val + (f or 0), ob)
            elif neck0 <= u <= end and abs(v) <= 2.7:
                if abs(v) <= 2.1:
                    n = norm((g.V[0] * v * 0.3, g.V[1] * v * 0.3, 1.0))
                    fret = (end - u) % 5.6 < 0.75
                    dot = int((end - u) // 5.6) in (2, 4, 6, 8) and abs(v) < 0.6 and 2.2 < (end - u) % 5.6 < 3.4
                    if fret: r.put(x, y, None, 0, on, STEEL[7])
                    elif dot: r.put(x, y, None, 0, on, BONE2[5])
                    else: r.put(x, y, M['board'], r.shade(M['board'], n), on)
                else: r.put(x, y, M[head_mat], r.shade(M[head_mat], (0, -0.3 if v < 0 else 0.3, 0.95)), on)
            elif end < u <= end + head_len and abs(v) <= 3.6 - (u - end) * 0.1:
                r.put(x, y, M[head_mat], r.shade(M[head_mat], (0, -0.2, 0.98)) - (0.12 if abs(v) > 2.6 else 0), on)
    for u in range(int(end) + 2, int(end + head_len), 3):                 # tuning pegs
        for sv in (-4.4, 4.4):
            p = g.P(u, sv); r.fixed(p[0], p[1], STEEL[8], on)
    for k in range(strings):                                               # strings
        sv = -1.5 + 3.0 * k / max(1, strings - 1)
        u = -8.0
        while u < end:
            p = g.P(u, sv)
            if (int(p[0]), int(p[1])) in r.buf: r.fixed(p[0], p[1], STEEL[7] if k % 2 else STEEL[6], on)
            u += 1.0

def fretting_arm(r, g, S, u, L1, L2, mat, r0, r1, r2, group, joint=False):
    """The neck hand wraps the neck from BEHIND: the arm and the palm are drawn before the instrument (the palm sits
    under the neck, the thumb tip peeks over its top edge); fret_fingers() then curls the fingers onto the fretboard."""
    H = g.P(u, 5.0)
    E = ik(S, H, L1, L2, 'down')                                     # the elbow hangs by the side, the forearm rises to the neck
    r.tube(S, E, r0, r1, M[mat], folds=None if joint else creases(0.8), group=group)
    if joint: r.ellipsoid(E[0], E[1], r1 + 0.3, r1 + 0.3, M[mat], lift=-0.15, group=group + 'j')
    r.tube(E, H, r1, r2, M[mat], folds=None if joint else creases(0.85), group=group + '2')
    palm = g.P(u, 5.2)
    r.ellipsoid(palm[0], palm[1], 4.6, 3.6, M[mat], rot=g.ang, group=group + 'h')
    thumb = g.P(u + 1.5, -3.4)
    r.ellipsoid(thumb[0], thumb[1], 1.9, 1.6, M[mat], group=group + 'h')

def fret_fingers(r, g, u, mat, group):
    """three fingers from the neck's lower edge curled onto the fretboard, pressing the strings"""
    for k in (-2.4, 0.0, 2.4):
        r.tube(g.P(u + k, 3.4), g.P(u + k - 0.4, -1.0), 1.6, 1.25, M[mat], lift=0.08, group=group)

def pick_hand(r, pos, mat, group, pick=True):
    r.ellipsoid(pos[0], pos[1], 4.6, 3.9, M[mat], group=group)
    for dx in (-2, 0, 2): r.darken(pos[0] + dx, pos[1] + 2, 0.15)
    if pick: r.fixed(pos[0] + 3, pos[1] + 3, BONE2[5])

# ------------------------------------------------------------------------------------------------------------- Telka
def _tp(bob, hd, strum, fret, knee, lean, ph, blink=False): return dict(bob=bob, hd=hd, strum=strum, fret=fret, knee=knee, lean=lean, ph=ph, blink=blink)
TELKA_IDLE = [_tp(0, 0, 0, 0.2, 0, 0, 0.0), _tp(1, 0, 0, 0.2, 0, 0, 0.5), _tp(1, 0, 0, 0.2, 0, 1, 1.0), _tp(0, 0, 0, 0.2, 0, 0, 1.5, True)]
TELKA_PLAY = [_tp(b, h, st, fr, k, ln, i * math.pi / 4) for i, (b, h, st, fr, k, ln) in enumerate(
    [(0, 0, -4, 0.0, 0, 0), (1, 2, 4, 0.0, 1, 1), (2, 4, -4, 0.35, 2, 1), (1, 2, 4, 0.35, 1, 0),
     (0, 0, -4, 0.7, 0, 0), (1, 2, 4, 0.7, 1, -1), (2, 4, -4, 0.35, 2, -1), (1, 2, 4, 0.35, 1, 0)])]

def creature_face(u, v, d):
    for (eu, ev) in ((0.5, -8.5), (9.0, -8.0)):
        q = (u - eu) ** 2 + (v - ev) ** 2
        if q <= 1.0: return INK
        if q <= 5.0: return EYE[2] if v < ev else EYE[1]
        if q <= 7.5 and v < ev: return GUIT[1]                            # heavy lids
    if 8.2 <= v <= 10.5 and -16 <= u <= 4:
        return BONE2[5] if int(u) % 2 == 0 and v < 9.6 else GUIT[0]       # fangs
    if (int(u), int(v)) in ((-6, -2), (-4, -2)): return GUIT[0]           # nostrils
    if d < 0.9 and int(u * 1.3 + v * 0.7) % 7 == 0 and int(v) % 3 == 0: return -0.12   # scales
    return None

def telka(P):
    r = Rig(128, 176)
    bob, hd, lean = P['bob'], P['hd'], P['lean']
    hx, hy = 63 + lean, 33 + bob + hd
    top = 52 + bob
    for i, a in enumerate((-162, -140, -117, -94, -71, -48, -26)):            # crown tentacles, swinging
        ang = math.radians(a); L = 10 + (3, 6, 8, 9, 8, 6, 3)[i]; sw = math.sin(P['ph'] + i * 0.9) * 2.4
        pts = curve(lambda t: (hx + math.cos(ang) * (8 + L * t) + sw * t * t, hy - 3 + math.sin(ang) * (10 + L * t) + 2.5 * t * t), 10)
        worm(r, pts, 3.0, 1.0, M['skin'], 'tent')
    hipL, hipR = (55, 104 + bob), (71, 104 + bob)
    kL, kR = (48 - P['knee'], 135 + bob // 2), (77 + P['knee'], 135 + bob // 2)
    for hip, kn, an, grp in ((hipL, kL, (43, 158), 'legL'), (hipR, kR, (82, 158), 'legR')):
        r.tube(hip, kn, 8.4, 6.8, M['denim'], folds=creases(0.82), group=grp)
        r.tube(kn, an, 6.8, 5.4, M['denim'], folds=creases(0.72, -0.16), group=grp)
    r.ellipsoid(kL[0] + 1, kL[1] + 1, 3.4, 2.2, M['skin'], lift=-0.12, group='legL')       # ripped knee
    for dx in (-3, -1, 1, 3): r.fixed(kL[0] + 1 + dx, kL[1] - 1, DENIM[6])
    for an, sgn, grp in (((43, 158), -1, 'bootL'), ((82, 158), 1, 'bootR')):
        r.tube((an[0], an[1] - 4), (an[0], 165), 6.6, 7.0, M['jacket'], group=grp)
        r.ellipsoid(an[0] + sgn * 3, 167.5, 9.5, 5.2, M['jacket'], group=grp)
        for x in range(an[0] + sgn * 3 - 10, an[0] + sgn * 3 + 10): r.fixed(x, 172, (26, 21, 19))
        for y in range(an[1] - 3, 164, 2): r.fixed(an[0] - 1, y, JACKET[6]); r.fixed(an[0] + 1, y, JACKET[6])
    r.ellipsoid(63, 104 + bob, 16, 7.5, M['denim'], group='hips')
    r.tube((46, 99 + bob), (80, 99 + bob), 2.4, 2.4, M['jacket'], group='belt')
    for x in range(61, 66): r.fixed(x, 98 + bob, BRASS[6]); r.fixed(x, 100 + bob, BRASS[4])
    for x in (50, 55, 71, 76): r.fixed(x, 99 + bob, BRASS[7])
    r.poly([(50, top + 2), (76, top + 2), (78, 100 + bob), (48, 100 + bob)], M['tee'], group='tee')
    for (x, y) in ((61, 76), (62, 75), (63, 75), (64, 75), (65, 75), (66, 76), (61, 77), (66, 77), (62, 78), (65, 78), (63, 80), (64, 80)):
        r.fixed(x, y + bob, SKIN_T[6])                                                  # a scrawled sigil on the tee
    jfold = lambda x, y: -0.16 if (x * 2 + y) % 11 == 0 else 0
    r.poly([(37, top + 6), (52, top + 1), (56, top + 12), (54, 106 + bob), (40, 108 + bob), (35, top + 30)], M['jacket'], group='jacket', vfun=jfold)
    r.poly([(74, top + 1), (89, top + 6), (91, top + 30), (86, 108 + bob), (72, 106 + bob), (70, top + 12)], M['jacket'], group='jacket', vfun=jfold)
    r.poly([(52, top + 1), (58, top + 2), (55, top + 22)], M['jacket'], lift=0.14, group='lapel')
    r.poly([(68, top + 2), (74, top + 1), (71, top + 22)], M['jacket'], lift=0.14, group='lapel')
    for y in range(top + 24, 104 + bob, 2): r.fixed(55, y, JACKET[6]); r.fixed(71, y, JACKET[6])     # zips
    for sx in (42, 85):
        r.ellipsoid(sx, top + 7, 9.5, 7, M['jacket'], group='pad' + str(sx))
        for k in range(5): r.fixed(sx - 6 + k * 3, top + 4 + (k % 2), BRASS[7])
    r.tube((hx, top - 6), (hx, top + 3), 5.4, 6.4, M['skin'], group='head')
    r.ellipsoid(hx, hy, 13.5, 15.5, M['skin'], group='head')
    r.ellipsoid(hx, hy - 1.5, 11.5, 3.6, M['skin'], lift=0.1, group='head')
    for ex in (hx - 5, hx + 5):
        r.ellipsoid(ex, hy + 1.5, 3.4, 2.6, M['skin'], lift=-0.35, group='head')
        if P['blink']:
            for x in range(ex - 2, ex + 3): r.fixed(x, hy + 2, SKIN_T[1])
        else:
            for x in range(ex - 2, ex + 2):
                for y in (hy + 1, hy + 2): r.fixed(x, y, EYE[2] if y == hy + 1 else EYE[1])
            r.fixed(ex - 2, hy + 1, EYE[3]); r.fixed(ex, hy + 1, INK); r.fixed(ex, hy + 2, INK)
    for i in range(7):                                                           # the tentacle beard
        x0 = hx - 8.5 + i * 2.8; L = 14 + (2, 6, 9, 11, 9, 6, 2)[i]; sw = math.sin(P['ph'] + i * 0.8) * 2.0
        pts = curve(lambda t: (x0 + sw * t + (i - 3) * 1.4 * t, hy + 8 + L * t + (1.5 * math.sin(t * 6 + i) if t > 0.8 else 0)), 10)
        worm(r, pts, 2.8, 1.0, M['skin'], 'beard', cups=(1, 0, SKIN_T[7]))
    g = Inst((57, 108 + bob), math.radians(-40))
    r.stroke(curve(lambda t: lerp(g.P(24, -12), (87, top + 6), t), 30), 3.4, M['jacket'], v=0.32, group='strap')
    uf = 52 + 9 * P['fret']                                          # near the headstock, where the chords are
    fretting_arm(r, g, (86, top + 8), uf, 27, 24, 'jacket', 6.6, 5.8, 4.6, 'armF')
    for k in range(3):                                                # the green hand under the leather cuff
        p = g.P(uf + k - 1, 5.2); r.ellipsoid(p[0], p[1], 3.2, 2.8, M['skin'], group='armFh')
    instrument(r, g, [(-6, 0, 19, 15.5), (12, -1, 12, 11.5)], [(21, 9, 7)], 21, 47, 11, 'guitar', face=creature_face, head_mat='guitar')
    fret_fingers(r, g, uf, 'skin', 'handF')
    S, H = (40, top + 8), g.P(6, -1.5 + P['strum'])
    E = ik(S, H, 27, 26, 'left')
    r.tube(S, E, 6.6, 5.8, M['jacket'], folds=creases(0.8), group='armS'); r.tube(E, H, 5.8, 4.8, M['jacket'], folds=creases(0.85), group='armS')
    pick_hand(r, H, 'skin', 'handS')
    return r.render()

# ----------------------------------------------------------------------------------------------------------- Bass XL
XL_IDLE = [dict(bob=0, hd=0, hdx=0, pluck=0, fret=0.2, eye=2), dict(bob=0, hd=0, hdx=1, pluck=0, fret=0.2, eye=2),
           dict(bob=1, hd=0, hdx=1, pluck=0, fret=0.2, eye=0), dict(bob=0, hd=0, hdx=0, pluck=0, fret=0.2, eye=2)]
XL_PLAY = [dict(bob=b, hd=h, hdx=0, pluck=p, fret=f, eye=e) for (b, h, p, f, e) in
           [(0, 0, -3, 0.0, 3), (2, 2, 3, 0.0, 2), (0, 0, -3, 0.0, 3), (2, 2, 3, 0.0, 2),
            (0, 0, -3, 0.6, 3), (2, 2, 3, 0.6, 2), (0, 0, -3, 0.3, 3), (2, 2, 3, 0.3, 2)]]

def bass_xl(P):
    r = Rig(144, 192); C = 72
    bob = P['bob']; top = 48 + bob
    st = M['steel']
    for sgn, grp in ((-1, 'L'), (1, 'R')):
        hip, kn, an = (C + sgn * 9, 116 + bob), (C + sgn * (11 + bob // 2), 148 + bob // 2), (C + sgn * 11, 176)
        r.tube(hip, kn, 6.8, 5.8, st, group='thigh' + grp)
        r.tube((kn[0] - sgn * 3, kn[1] + 3), (an[0] - sgn * 3, an[1] - 5), 1.7, 1.7, st, lift=-0.3, group='piston' + grp)
        r.tube(kn, an, 5.8, 4.6, st, group='shin' + grp)
        r.poly([(kn[0] - 4, kn[1] + 5), (kn[0] + 4, kn[1] + 5), (an[0] + 3, an[1] - 7), (an[0] - 3, an[1] - 7)], st, lift=0.14, round_=0.6, group='guard' + grp)
        r.ellipsoid(kn[0], kn[1], 5.8, 5.2, st, lift=-0.1, group='knee' + grp)
        r.ellipsoid(an[0], an[1], 4.4, 3.6, st, lift=-0.2, group='ankle' + grp)
        r.ellipsoid(an[0] + sgn * 2, 184, 10.5, 5.6, st, flat=0.8, group='foot' + grp)
        for x in range(an[0] + sgn * 2 - 10, an[0] + sgn * 2 + 11): r.fixed(x, 189, (24, 26, 30))
    r.poly([(C - 14, 104 + bob), (C + 14, 104 + bob), (C + 12, 118 + bob), (C - 12, 118 + bob)], st, round_=0.8, group='pelvis')
    r.stroke(curve(lambda t: (C - 7 + 2 * math.sin(t * 3), 84 + bob + 21 * t), 20), 2.0, color=CABLES[0], group='cable')
    r.stroke(curve(lambda t: (C + 7 - 2 * math.sin(t * 3), 84 + bob + 21 * t), 20), 2.0, color=CABLES[1], group='cable')
    for k in range(5): r.ellipsoid(C, 88 + bob + k * 4, 5.2, 2.6, st, lift=-0.18, group='spine')
    r.poly([(C - 17, top + 2), (C + 17, top + 2), (C + 21, top + 12), (C + 16, 86 + bob), (C - 16, 86 + bob), (C - 21, top + 12)], st, round_=0.95, lift=0.05, group='chest')
    r.ellipsoid(C - 10, top + 27, 4.5, 3.2, M['rust'], flat=0.3, group='chest')
    for x in range(C - 18, C + 19): r.darken(x, top + 19, 0.3)
    for y in range(top + 20, 86 + bob): r.darken(C, y, 0.25)
    for (x, y) in ((C - 15, top + 6), (C + 15, top + 6), (C - 15, top + 17), (C + 15, top + 17), (C - 3, top + 22), (C + 3, top + 22), (C - 13, top + 33), (C + 13, top + 33)):
        r.fixed(x, y, STEEL[9])
    for i in range(4):
        for x in range(C + 4, C + 15): r.fixed(x, top + 25 + i * 2, STEEL[0] if x % 3 else STEEL[3])
    text(r, 'XL', C + 5, top + 8, BONE2[4])
    for sx, grp in ((C - 21, 'pL'), (C + 21, 'pR')):
        r.ellipsoid(sx, top + 7, 9, 8, st, lift=0.08, group=grp)
        for k in range(4): r.fixed(sx - 5 + k * 3, top + 2 + (k % 2), STEEL[9])
    hx, hy = C + P['hdx'], 26 + bob + P['hd']
    r.tube((C, top - 12), (C, top + 2), 3.4, 3.8, st, lift=-0.3, group='neck')
    r.stroke(curve(lambda t: (C + 4 + math.sin(t * 4), top - 10 + 12 * t), 10), 1.4, color=CABLES[2], group='neck')
    r.ellipsoid(hx, hy, 12, 13, st, lift=0.08, group='head')
    r.poly([(hx - 8, hy + 6), (hx + 8, hy + 6), (hx + 6, hy + 14), (hx - 6, hy + 14)], st, lift=-0.06, group='head')
    for y in range(hy + 8, hy + 13, 2):
        for x in range(hx - 4, hx + 5): r.darken(x, y, 0.3)                        # speaker grille mouth
    r.ellipsoid(hx, hy, 10.5, 11.5, st, lift=-0.62, group='head', clip=lambda x, y: hy - 3 <= y <= hy + 2)   # visor glass
    for x in range(hx - 7, hx + 3): r.fixed(x, hy - 3, STEEL[8])
    if P['eye']:
        for ex in (hx - 5, hx + 3):
            r.fixed(ex, hy - 1, EYE[P['eye']]); r.fixed(ex + 1, hy - 1, EYE[P['eye']])
            r.fixed(ex, hy, EYE[max(0, P['eye'] - 2)]); r.fixed(ex + 1, hy, EYE[max(0, P['eye'] - 2)])
    for ex in (hx - 12, hx + 12): r.ellipsoid(ex, hy + 1, 2.8, 3.2, st, lift=-0.05, group='head')
    r.tube((hx + 8, hy - 9), (hx + 11, hy - 18), 1.1, 0.8, st, group='head')
    r.fixed(hx + 11, hy - 19, CABLES[0])
    g = Inst((C - 4, 112 + bob), math.radians(-40))
    r.stroke(curve(lambda t: lerp(g.P(25, -12), (C + 21, top + 6), t), 30), 3.4, M['jacket'], v=0.3, group='strap')
    guard = lambda u, v, d: -10 <= u <= 15 and 3.8 <= v <= 10.5 and d < 0.82
    burst = lambda u, v, d: 0.28 - 0.62 * d
    uf = 50 + 12 * P['fret']
    fretting_arm(r, g, (C + 21, top + 9), uf, 31, 28, 'steel', 5.6, 4.8, 4.2, 'armF', joint=True)
    instrument(r, g, [(-7, 0, 19, 15.5), (13, -1, 12, 11.5)], [(21, 9, 7)], 22, 52, 11, 'burst', face=burst, guard=guard, pickups=((3, 6), (11, 14)))
    fret_fingers(r, g, uf, 'steel', 'handF')
    S, H = (C - 21, top + 9), g.P(8, -1.5 + P['pluck'])
    E = ik(S, H, 27, 26, 'left')
    r.tube(S, E, 5.6, 4.8, st, group='armP'); r.ellipsoid(E[0], E[1], 5, 5, st, lift=-0.15, group='armPj'); r.tube(E, H, 4.8, 4.2, st, group='armP2')
    pick_hand(r, H, 'steel', 'handP', pick=False)
    for k in (-1.5, 1.5): r.tube(g.P(8 + k, -1.5 + P['pluck'] + 2), g.P(8 + k, -3 + P['pluck']), 1.2, 1.1, st, group='handP')
    return r.render()

# ------------------------------------------------------------------------------------------------------ Fluffy Karlis
HH, SN, T1, T2, FL, CR = (24, 96), (46, 118), (72, 103), (104, 101), (132, 121), (138, 75)
def hit(tip, side): return (tip, (tip[0] + 12 * side, tip[1] - 15))
def up(hand, side): return ((hand[0] - 13 * side, hand[1] - 11), hand)
KARLIS_IDLE = [dict(L=((52, 117), (64, 105)), R=((122, 119), (110, 106)), bob=b, hd=0, wob=0, mouth=False, blink=bl, ear=e, hh=2)
               for (b, bl, e) in ((0, False, 0), (1, False, 0), (1, False, 1), (0, True, 0))]
KARLIS_PLAY = [dict(L=L, R=R, bob=b, hd=h, wob=w, mouth=m, blink=False, ear=0, hh=hh) for (L, R, b, h, w, m, hh) in [
    (hit(HH, 1), up((114, 80), -1), 0, 0, 2, False, 2), (up((40, 82), 1), hit(T2, -1), 0, 1, 3, False, 2),
    (hit(SN, 1), up((116, 82), -1), 1, 2, 0, False, 2), (up((40, 84), 1), hit(FL, -1), 1, 1, 0, False, 4),
    (hit(HH, 1), up((114, 80), -1), 0, 0, 0, False, 2), (up((42, 82), 1), hit(T1, -1), 0, 1, 0, False, 2),
    (hit(SN, 1), hit(FL, -1), 1, 2, 0, False, 2), (up((44, 60), 1), hit(CR, -1), 1, 3, 1, True, 2)]]

def cymbal(r, cx, cy, rx, ry, group):
    rings = lambda x, y, u, w: (-0.09 if int(math.hypot(u, w) * 8) % 2 else 0.04)
    r.ellipsoid(cx, cy, rx, max(ry, 1.0), M['cymbal'], flat=0.35, group=group, vfun=rings)
    r.ellipsoid(cx, cy - max(ry, 1.0) * 0.3, 3.2, 1.4, M['cymbal'], lift=0.15, group=group)

def drum_top(r, cx, cy, rx, ry, group):
    r.ellipsoid(cx, cy, rx, ry, M['heads'], flat=0.2, group=group)
    for k in range(int(rx * 3)):                                           # the hoop
        a = k / (rx * 3) * 2 * math.pi
        r.fixed(cx + rx * math.cos(a), cy + ry * math.sin(a), STEEL[8] if math.sin(a) < 0 else STEEL[6])

def shell(r, cx, top, rx, h, mat, group, lugs=3):
    r.poly([(cx - rx, top), (cx + rx, top), (cx + rx, top + h), (cx - rx, top + h)], M[mat], round_=0.97, group=group)
    for k in range(lugs):
        lx = cx - rx * 0.7 + k * rx * 1.4 / max(1, lugs - 1)
        for y in range(top + 2, top + min(h, 7)): r.fixed(lx, y, STEEL[8] if y % 2 else STEEL[6])

def karlis(P):
    r = Rig(176, 176)
    bob, hy = P['bob'], P['hd'] + P['bob']
    st = M['steel']
    for (x0, y0) in ((147, 80), (24, 100)):                                          # cymbal stands
        r.stroke([(x0, y) for y in range(y0, 173)], 2.2, st, v=0.55, group='stand')
        for dx in (-10, 10): r.stroke(curve(lambda t: (x0 + dx * t, 158 + 15 * t), 12), 1.6, st, v=0.4, group='stand')
        r.ellipsoid(x0, 157, 2.2, 2.2, st, group='stand')
    r.ellipsoid(88, 92 + bob, 35, 36, M['fur'], jag=0.1, group='body')
    r.poly([(76, 60 + bob), (100, 60 + bob), (99, 124), (77, 124)], M['tee'], group='tee')
    for side in (-1, 1):
        r.poly([(88 + side * 12, 58 + bob), (88 + side * 29, 66 + bob), (88 + side * 28, 124), (88 + side * 12, 124)], M['vest'], group='vest' + str(side))
        for y in range(62 + bob, 120, 4): r.fixed(88 + side * 13, y, BRASS[6])
    for (x, y, c) in ((63, 80, LACQ[5]), (64, 80, LACQ[5]), (65, 80, LACQ[5]), (63, 81, LACQ[4]), (64, 81, LACQ[4]), (65, 81, LACQ[4]),
                      (110, 88, CONSOLE[6]), (111, 88, CONSOLE[6]), (112, 88, CONSOLE[6]), (110, 89, CONSOLE[5]), (111, 89, CONSOLE[5]), (112, 89, CONSOLE[5])):
        r.fixed(x, y + bob, c)                                                        # patches on the vest
    toast = lambda x, y: (81 <= x <= 95 and 81 <= y <= 94) or ((x - 84.5) ** 2 + (y - 81) ** 2 <= 12) or ((x - 91.5) ** 2 + (y - 81) ** 2 <= 12)
    for y in range(76, 96):
        for x in range(79, 98):
            if toast(x, y):
                edge = not all(toast(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                r.fixed(x, y + bob, BONE2[2] if edge else BONE2[4])
    for (x, y) in ((85, 85), (91, 85), (86, 90), (90, 90)): r.fixed(x, y + bob, TEE[1])
    ear = P['ear']
    for ex, grp in ((71 - ear, 'earL'), (105, 'earR')):
        r.ellipsoid(ex, 24 + hy, 5.2, 4.8, M['fur'], jag=0.12, group=grp)
        r.ellipsoid(ex, 25 + hy, 2.6, 2.4, M['muzzle'], lift=-0.2, group=grp)
    r.ellipsoid(88, 34 + hy, 17.5, 14, M['fur'], jag=0.1, group='head')                    # skull
    r.ellipsoid(88, 45 + hy, 19, 11, M['fur'], jag=0.14, group='head')                     # heavy jowls
    r.ellipsoid(88, 41 + hy, 5.4, 7, M['muzzle'], lift=0.02, group='snout')                # bridge of the snout
    r.ellipsoid(88, 49 + hy, 9.5, 6.4, M['muzzle'], group='snout')
    r.ellipsoid(88, 44.5 + hy, 4.4, 3.0, M['nose'], group='nose')
    r.fixed(86, 45 + hy, VEST[0]); r.fixed(90, 45 + hy, VEST[0])
    r.ellipsoid(88, 31 + hy, 13, 3.4, M['fur'], lift=0.1, jag=0.1, group='brow')         # brow ridge
    for ex in (81, 95):
        r.ellipsoid(ex, 35 + hy, 3.2, 2.2, M['fur'], lift=-0.4, group='head')
        if P['blink']:
            for x in (ex - 1, ex, ex + 1): r.fixed(x, 35 + hy, FUR[1])
        else:
            r.fixed(ex - 1, 35 + hy, VEST[0]); r.fixed(ex, 35 + hy, VEST[0]); r.fixed(ex, 36 + hy, VEST[1]); r.fixed(ex - 1, 35 + hy, BONE2[3])
    if P['mouth']:
        r.ellipsoid(88, 54 + hy, 5.6, 3.6, M['lacq'], lift=-0.55, group='mouth')
        for x in (85, 91): r.fixed(x, 52 + hy, BONE2[5]); r.fixed(x, 53 + hy, BONE2[4])
    else:
        for x in range(84, 93): r.fixed(x, 53 + hy + (1 if x in (84, 92) else 0), MUZZLE[0])
    for dx in (-8, 8): r.stroke(curve(lambda t: (46 + dx * t, 128 + 45 * t), 14), 1.6, st, v=0.4, group='stand')
    shell(r, 46, 118, 12, 10, 'steel', 'snare', lugs=4); drum_top(r, 46, 118, 12, 3.6, 'snare')
    for cx, cy in ((72, 103), (104, 101)):
        shell(r, cx, cy, 10.5, 13, 'lacq', 'tom%d' % cx); drum_top(r, cx, cy, 10.5, 3.6, 'tom%d' % cx)
    for dx in (-13, 13): r.stroke(curve(lambda t: (132 + dx + dx * 0.15 * t, 148 + 25 * t), 14), 1.6, st, v=0.4, group='stand')
    shell(r, 132, 121, 14, 27, 'lacq', 'floor', lugs=4); drum_top(r, 132, 121, 14, 4.5, 'floor')
    r.ellipsoid(88, 145, 29.5, 29.5, M['lacq'], flat=0.55, group='kickhoop')
    r.ellipsoid(88, 145, 26.5, 26.5, M['heads'], flat=0.22, group='kick')
    for k in range(12):
        a = k / 12 * 2 * math.pi
        r.fixed(88 + 28 * math.cos(a), 145 + 28 * math.sin(a), STEEL[8])
    big = lambda x, y: (78 <= x <= 98 and 139 <= y <= 157) or ((x - 83) ** 2 + (y - 139) ** 2 <= 30) or ((x - 93) ** 2 + (y - 139) ** 2 <= 30)
    for y in range(130, 160):
        for x in range(75, 101):
            if big(x, y):
                d2 = sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)) if not big(x + dx, y + dy))
                r.fixed(x, y, MUZZLE[1] if d2 >= 3 else MUZZLE[3] if d2 else (BURST[6] if (x + y) % 5 else BURST[5]))
    for (x, y) in ((82, 143), (83, 144), (84, 145), (94, 143), (93, 144), (92, 145), (82, 146), (93, 146)): r.fixed(x, y, INK)
    for x in range(83, 94): r.fixed(x, 151, MUZZLE[0])
    for (x, y) in ((84, 152), (85, 152), (85, 153), (91, 152), (92, 152), (91, 153)): r.fixed(x, y, BONE2[5])
    gap = P['hh']
    cymbal(r, 24, 98 - gap, 13, 2.4, 'hihat'); cymbal(r, 24, 99, 13, 2.2, 'hihat2')
    tilt = (0, 3.5, 2.0, 1.0)[P['wob']]
    cymbal(r, 147, 76 - tilt * 0.4, 17, 3.6 + tilt, 'crash')
    for (tip, hand), sh, side in ((P['L'], (63, 68 + bob), 'left'), (P['R'], (113, 68 + bob), 'right')):
        E = ik(sh, hand, 23, 22, side)
        r.tube(sh, E, 8.6, 7.6, M['fur'], jag=0.08, group='arm' + side)
        r.tube(E, hand, 7.6, 6.4, M['fur'], jag=0.08, group='arm' + side)
        dxs, dys = tip[0] - hand[0], tip[1] - hand[1]; L = math.hypot(dxs, dys) or 1
        r.stroke(curve(lambda t: (hand[0] - dxs / L * 4 + (dxs + dxs / L * 4) * t, hand[1] - dys / L * 4 + (dys + dys / L * 4) * t), 30), 2.4, M['maple'], v=0.6, group='stick' + side)
        r.fixed(tip[0], tip[1], MAPLE[5])
        r.ellipsoid(hand[0], hand[1], 6.2, 5.6, M['fur'], lift=-0.05, jag=0.05, group='paw' + side)
        for k in (-2, 0, 2): r.fixed(hand[0] + k, hand[1] + 5, BONE2[4])
    return r.render()

# ----------------------------------------------------------------------------------------------------------- Mira Dron
MIRA_IDLE = [dict(hl=(54, 98), hr=(90, 98), hx=0, hd=0, led=i // 2, blink=(i == 3), vine=i * 0.4) for i in range(4)]
MIRA_PLAY = [dict(hl=(lx, 97 + (i % 2)), hr=(rx, 98 - (i % 2)), hx=sx, hd=i % 2, led=i, blink=False, vine=i * math.pi / 4)
             for i, (lx, rx, sx) in enumerate([(44, 92, 0), (52, 86, 1), (58, 98, 1), (50, 104, 0), (44, 94, 0), (50, 88, -1), (56, 100, -1), (48, 96, 0)])]

def mira(P):
    r = Rig(144, 176)
    for x0, sgn in ((15, -1), (129, 1)):                                          # tentacles curling up beside the synth
        sw = math.sin(P['vine']) * 1.8
        pts = curve(lambda t: (x0 + sgn * (6 * math.sin(t * 2.6) + sw * t * t) + (sgn * 4 * math.cos(t * 8) * (t - 0.6) if t > 0.6 else 0),
                               172 - 74 * t), 16)
        worm(r, pts, 6.0, 1.4, M['console'], 'tentacle' + str(sgn), cups=(-sgn, 0, SKIN_T[6]), lift=0.08)
    hx, hd = P['hx'], P['hd']
    folds = lambda x, y: -0.14 if (x - 72 + y // 6) % 7 == 0 else 0
    r.poly([(46, 64), (98, 64), (114, 106), (30, 106)], M['robe'], group='robe', vfun=folds)
    hood = [(52, 68), (48, 42), (57, 22), (72 + hx, 7 + hd), (88 + hx, 22), (96, 42), (92, 68)]
    r.poly(hood, M['robe'], lift=0.04, group='hood', vfun=lambda x, y: -0.15 if (x * 3 - y) % 13 == 0 and y > 24 else 0)
    r.ellipsoid(72 + hx, 44 + hd, 11.5, 13.5, M['robe'], lift=-0.85, group='void')
    if not P['blink']:
        for ex in (67 + hx, 76 + hx):
            r.fixed(ex, 42 + hd, EYE[3]); r.fixed(ex + 1, 42 + hd, EYE[2]); r.fixed(ex, 43 + hd, EYE[2]); r.fixed(ex + 1, 43 + hd, EYE[1])
            for (dx, dy) in ((-1, 0), (2, 1), (0, 2), (1, -1)): r.fixed(ex + dx, 42 + hd + dy, ROBE[3])
    r.poly([(42, 57), (102, 57), (108, 72), (36, 72)], M['scarf'], group='scarf')
    for x in range(38, 107, 2):
        L = 3 + (x * 7) % 3
        r.stroke([(x + 0.5, 72 + k) for k in range(L)], 1.2, M['scarf'], v=0.45 - 0.05 * (x % 3), group='fringe')
    r.poly([(22, 90), (122, 90), (128, 104), (16, 104)], M['console'], lift=0.14, round_=0.3, tilt=-0.5, group='top')
    for x in range(24, 121):                                                    # keybed
        k = (x - 24) % 4
        r.fixed(x, 101, SCARF[7] if k else SCARF[2]); r.fixed(x, 102, SCARF[6] if k else SCARF[2])
        if (x - 24) % 8 in (2, 3): r.fixed(x, 100, CONSOLE[0]); r.fixed(x, 99, CONSOLE[1])
    for i in range(12):
        lx = 28 + i * 8; on = (i + P['led']) % 4 == 0
        r.fixed(lx, 93, VEIN[3] if on else VEIN[0]); r.fixed(lx + 1, 93, VEIN[2] if on else VEIN[0])
    for i, kx in enumerate((30, 38, 106, 114)):
        r.ellipsoid(kx, 96.5, 2.2, 1.6, M['brass'], group='knob%d' % i)
        r.fixed(kx + (1 if (i + P['led']) % 2 else -1), 96, BRASS[7])
    for y in range(93, 99):
        for x in range(60, 85):
            u, w = (x + 0.5 - 72) / 12, (y + 0.5 - 96) / 3
            if u * u + w * w <= 1:
                a = math.atan2(w, u) + P['led'] * 0.6
                r.fixed(x, y, VEIN[3] if int((a + math.hypot(u, w) * 6) * 2) % 3 == 0 else VEIN[1])
    for (a, b, c) in (((40, 96), (50, 93), CABLES[0]), ((92, 96), (100, 92), CABLES[1]), ((44, 97), (98, 97), CABLES[2])):
        mid = ((a[0] + b[0]) / 2, max(a[1], b[1]) + 3)
        r.stroke(curve(lambda t: ((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * mid[0] + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * mid[1] + t * t * b[1]), 30), 1.2, color=c, group='cable')
    carve = lambda x, y: -0.22 if x in (24, 120) or y in (112, 166) or ((x - 72) ** 2 / 900 + (y - 139) ** 2 / 500 > 1 and (x + y) % 9 == 0 and 26 < x < 118 and 114 < y < 164) else 0
    r.poly([(16, 104), (128, 104), (128, 173), (16, 173)], M['console'], round_=0.35, group='front', vfun=carve)
    for (rx, ry) in ((20, 108), (124, 108), (20, 169), (124, 169)): r.fixed(rx, ry, BRASS[7])
    r.ellipsoid(72, 141, 8.5, 9.5, M['brass'], group='skull')
    for sgn in (-1, 1):
        worm(r, curve(lambda t: (72 + sgn * (6 + 13 * t), 136 - 15 * t * t), 8), 3.0, 0.9, M['brass'], 'horn%d' % sgn)
        for dx in (0, 1):
            for dy in (0, 1): r.fixed(72 + sgn * 3 + dx - (1 if sgn < 0 else 0), 139 + dy, CONSOLE[0])
    r.fixed(72, 143, CONSOLE[0]); r.fixed(72, 144, CONSOLE[0])
    for x in range(67, 78, 2): r.fixed(x, 147, CONSOLE[0]); r.fixed(x + 1, 147, BRASS[5])
    for (hand, sh, side) in ((P['hl'], (52, 68), 'left'), (P['hr'], (92, 68), 'right')):
        wrist = (hand[0], hand[1] - 5)
        E = ik(sh, wrist, 19, 16, side)
        r.tube(sh, E, 7.0, 6.2, M['robe'], folds=creases(0.8), group='sleeve' + side)
        r.tube(E, wrist, 6.2, 7.6, M['robe'], folds=creases(0.6), group='sleeve' + side)
        r.ellipsoid(hand[0], hand[1] - 3, 3.6, 2.6, M['hands'], group='hand' + side)
        for k in (-2, 0, 2): r.tube((hand[0] + k, hand[1] - 2), (hand[0] + k * 1.2, hand[1] + 1), 1.0, 0.9, M['hands'], group='hand' + side)
    return r.render()

CAST = {'telka': (telka, TELKA_IDLE, TELKA_PLAY), 'bass_xl': (bass_xl, XL_IDLE, XL_PLAY),
        'karlis': (karlis, KARLIS_IDLE, KARLIS_PLAY), 'mira': (mira, MIRA_IDLE, MIRA_PLAY)}

if __name__ == '__main__':
    only = sys.argv[2].split(',') if len(sys.argv) > 2 else list(CAST)
    for cid in only:
        fn, idle, play = CAST[cid]
        os.makedirs(f'{OUT}/{cid}', exist_ok=True)
        frames = [fn(p) for p in idle + play]
        w, h = frames[0].size
        sheet = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
        for i, im in enumerate(frames):
            im.save(f'{OUT}/{cid}/{i}.png'); sheet.paste(im, (i * w, 0))
        sheet.save(f'{OUT}/{cid}.png')
    write_gpl(f'{OUT}/club.gpl')
    print('ok', OUT)
