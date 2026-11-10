"""The first view of Upper Morkezela (EntryScene), native 1067x600: an overlook above the city, overcast stormy DAY.

Replaces the re-pixelled AI vista (entry_bg.py + city_ref.jpg, shown 3x). Same composition, redrawn at 1 px on the
shared camera (raster3d: VP (533, 296), F 300, eye 12 units, the walk line y 534 = depth 15):
  * the sky: a heavy storm ceiling (light-marched fbm cloud masses, lit top edges, dark bellies), thin dark strata
    over the horizon, and the city's sickly green glow along the horizon lighting the low clouds from below;
  * the city far below the overlook (its ground at Y -200): ~950 buildings -- a skyline of slender towers out to
    z 5500, a carpet of low roofs sampled evenly in screen rows, dark ruins framing the far left; tenement blocks with
    window grids (a weave once too far for windows), art-deco setbacks, ruins with stepped broken tops and bare
    girders, the temples the dying gods brought along (gothic spires, onion domes, ziggurats, pagodas), lattice
    masts, trees gone wild on the roofs -- vines hanging off everything, the bases sinking into a green mist, all of
    it fading into the glow with distance;
  * the Egg Cathedral on the left, as it stands now (EggCatedralScene, the map), rising out of the earth (the Egg
    Emergence): the giant egg split down the middle, its two halves parted with jagged broken rims (a lit lip, the
    shell's thick wall, the yellowed membrane inside), cracked, wrapped in vines and ivy grown into the cracks, both
    halves sunk into a great mound of heaved earth (turf, bushes and small trees on its crest, scarps showing the
    soil strata and the torn street with roots hanging out, scree and blocks down its flanks, plates of the old
    road crust tilted up round the shells, two houses at its foot tilted and half swallowed, a leaning street lamp),
    contact shadows where shell meets ground; between the halves the gothic cathedral stands on the mound's saddle
    (twin towers with slate spires and finials, outer towers, the gable and rose window, lancets lit warm, the lit
    arched door) with a stone stair down to the city;
  * Scraper 1140 in the middle (z 420), the landmark the player walks to next, after ScraperScene's tower
    (scraper_native_bg.py: FACER / TOWR / CREAM ramps): the dark weathered concrete slab with floor ledges and soot
    runs, the faded SCRAPER 1140 lettering, near-black service shafts stepped on its left (plant rooms, a tank,
    aerials, amber portholes, a gantry), a riser with a clad pipe on its right, the cornice and finned crown with
    finials, one small amber window low, and a tall antenna mast that keeps the old needle silhouette (tip y 40);
  * places the player will visit, small and unlabelled: Voxmarket's three zeppelin hangars (stucco gables with a
    glowing radial arch, blue-grey and rust-patched barrel roofs), Shed 521's top-heavy timber tower with its pipe,
    plume, annex, fence and heating pipes, the Lumen Directorate's pale twin spires and glasshouse in its gardens, the
    Townhall's clock and copper dome, and on the far right the harbour (quays, four cranes) with the sea on the
    horizon, the Echo Drain's derricks crowned with brass gramophone horns out in the water, Redmass Island, boats;
  * city life: chimney stacks with smoke and steam plumes leaning in the wind, cables and skybridges strung between
    tall towers, banners on facades, lit windows, a rail viaduct with a train across the middle distance, faint
    hills on the horizon, god rays falling through the cloud break onto the city beyond the Scraper, four flocks;
  * skyships of the Verdigrace's kind: a detailed near one (netted, mossy gasbag with glowing spots, ribbed fins,
    a planked hull with lit ports, rail, cabin, rigging, a pennant, vines trailing) and three far ones;
  * the overlook (raster3d + paintpass): wet flagstones with puddles mirroring the sky, a carved stone balustrade
    (a fillet, a groove and dentils on the coping, a moulded plinth, sunk panels with rosettes on the piers), a
    tall lidded amphora (cracked, chipped, mossy) on the first pier, an urn with ivy on the second, a broken stretch (fallen coping,
    rubble), ivy and moss, a lantern on a pier, the signpost with a painted egg pointing right (to the Cathedral; the
    exit), weeds along the plinth and in the joints, fallen ivy leaves.

    python3 entry_city_bg.py <outdir> [backdrop]   # -> entry_city.png (= assets/images/backgrounds/EntryCity.png), backdrop.png
                                                   #    (sky + city only; `backdrop` stops there), chars.png + guides.png (the
                                                   #    Aseprite reference layers), entry_city.gpl (96 colours), fixed.json
Fixed points (canvas, also written to fixed.json): Master Thaal (600, 530); walk line y 534 (on the flags, in front of
the plinth foot y 516); the exit = the right edge (800-space zone x 780); the signpost post at x 911 (foot y 527), its
board x 900..1010, y 402..437 pointing right; the coping's top y 444..459; the broken stretch x 420..507; the lantern
(748, 412); the egg's halves x ~138..406 round (272, 282), top y 144, sunk into the mound (x 80..466, crest ~y 362);
the cathedral door x 265..279, y 355..386, its stair down to y 462;
Scraper 1140's slab x 528..572 (top y 124), shafts from x 490, its mast x 549 with the tip at y 40.
The far city has its own z-buffer (a second Raster) and its own aerial perspective; only the overlook goes through
paintpass. Render ~30 s, deterministic. SKY_OX / SKY_OY (env) shift the cloud noise to try other skies.
"""
import sys, os, math, random, json
from PIL import Image, ImageDraw
from common import h32, make_noise, band, ramp
from pal_day import STONE, WOOD, WARM, GLOW, METAL, LEAF as LEAFR, INK, MYC
from shedkit import wn, tone, mix, RUSTY
from raster3d import Raster, proj, W, H, CX, HY, F, CAMH

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
HERE_ = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)
INF = 9e9

def clamp(v, a=0.0, b=1.0): return a if v < a else b if v > b else v
def X_at(sx, Z): return (sx - CX) * Z / F
def Y_at(sy, Z): return CAMH - (sy - HY) * Z / F

# ---------------------------------------------------------------------------------------------------- palette
CLOUD = ramp('#232d2c #283432 #2e3a37 #34413d #3b4843 #43504a #4b5851 #546159 #5d6a61 #677369 #717c71 #7c867a '
             '#889183 #959d8e #a3aa9a #b2b8a8')
GLOWR = ramp('#5a6a44 #667848 #73874c #809550 #8da256 #9aae5e #a8b96a #b7c47a')
SHELL = ramp('#3b4036 #4a5043 #5a6151 #6b7261 #7d8471 #8f9682 #a1a793 #b3b8a4 #c4c8b5 #d3d6c5')
VINE = ramp('#16240f #1e3214 #284219 #33541e #3f6824 #4d7c2c #5d9035 #70a240')
CSTONE = ramp('#141a19 #1b2220 #222a28 #2a3330 #323c38 #3b4641 #45504a #505b54 #5b665e')     # the city's stone, cool
CWARM = ramp('#21180f #2e2116 #3c2b1c #4a3624 #5a432e #6b523a')                             # brick, rust, timber
CPALE = ramp('#3a3d33 #4a4d41 #5b5f50 #6d7160 #808471')                                     # stucco, limestone
GOLDD = ramp('#3e3520 #564927 #6f5f30 #88763b')                                             # tarnished domes
COPPER = ramp('#1f3a33 #2b4d43 #386053 #477464')                                           # verdigris roofs
OCHRE = ramp('#2a1f0e #403016 #5a4420 #74592b #8e6f38 #a5854a')
YG = -200.0                                                                                 # the city's ground

# ---------------------------------------------------------------------------------------------------- 1. the sky
NS = [make_noise(c, 40 + i, 2800, 1800) for i, c in enumerate((180, 90, 45, 22, 11, 5))]
NW = [make_noise(120, 60, 2800, 1800), make_noise(120, 61, 2800, 1800), make_noise(40, 62, 2800, 1800), make_noise(40, 63, 2800, 1800)]
AMP = (0.40, 0.26, 0.16, 0.10, 0.055, 0.025)
rnd = random.Random(3)
COV = [[0.0] * W for _ in range(H)]
def _cov_blob(cx, cy, rx, ry, w):
    for y in range(max(0, int(cy - ry * 2.2)), min(H, int(cy + ry * 2.2) + 1)):
        row = COV[y]; dy = ((y + 0.5 - cy) / ry) ** 2
        for x in range(max(0, int(cx - rx * 2.2)), min(W, int(cx + rx * 2.2) + 1)):
            e = ((x + 0.5 - cx) / rx) ** 2 + dy
            if e < 4.8: row[x] += w * math.exp(-e * 1.4)
SKY_OX, SKY_OY = int(os.environ.get('SKY_OX', 300)), int(os.environ.get('SKY_OY', 900))
for (cx, cy, rx, ry, w) in ((60, 40, 260, 110, 0.55), (300, 90, 230, 90, 0.6), (560, -20, 200, 70, 0.3), (850, 50, 240, 100, 0.55),
                            (1080, 80, 220, 110, 0.55), (600, 120, 150, 80, -0.5), (240, 170, 140, 40, 0.3), (120, 175, 190, 40, 0.35), (380, 200, 150, 30, 0.3), (900, 185, 200, 40, 0.35),
                            (650, 232, 120, 22, 0.25), (200, 255, 260, 16, 0.25), (800, 262, 280, 14, 0.25), (520, 270, 220, 12, 0.2)):
    _cov_blob(cx, cy, rx, ry, w)

def _fbm(x, y):
    wx = x + (NW[0](x, y * 2) - 0.5) * 70 + (NW[2](x, y * 2) - 0.5) * 18
    wy = y + (NW[1](x, y * 2) - 0.5) * 30 + (NW[3](x, y * 2) - 0.5) * 8
    sx, sy = wx * 0.62, wy * 1.15
    s = 0.0
    for n, a in zip(NS, AMP): s += n(sx, sy) * a
    return s

def cloud_d(x, y):
    xi = max(0, min(W - 1, int(x))); yi = max(0, min(H - 1, int(y)))
    return _fbm(x + SKY_OX, y + SKY_OY) - 0.62 + COV[yi][xi] * 0.55

def strata(x, y):
    """low dark cloud strips over the horizon, silhouetted against the glow"""
    if y < 200 or y > 312: return 0.0
    wx = x + (NW[2](x, y * 3) - 0.5) * 40
    f = NS[1](wx * 0.35, y * 2.6) * 0.5 + NS[2](wx * 0.4, y * 2.4) * 0.3 + NS[3](wx * 0.6, y * 2.0) * 0.14 + NS[4](wx, y * 1.5) * 0.06
    env = math.exp(-((y - 262) / 30.0) ** 2)
    return (f - 0.58) * 3.0 + env * 0.55 - 0.45

def glow_k(x, y):
    """the city's green glow on the horizon (peaks just above the far skyline)"""
    gx = 0.75 + 0.35 * NS[0](x * 1.1 + 900, 40) + 0.25 * math.exp(-((x - 600) / 220.0) ** 2)
    return (math.exp(-((y - 318) / 26.0) ** 2) * 0.82 + math.exp(-((y - 300) / 80.0) ** 2) * 0.26) * gx

def sky_px(x, y):
    t = clamp(y / HY)
    d = cloud_d(x, y)
    clear = 9.2 + 4.6 * t ** 1.5 + (NS[0](x * 0.7, y * 1.5) - 0.5) * 1.0
    if d <= 0:
        v = clear + max(-1.5, d * 5)
    else:
        occ = 0.0
        for k, st in enumerate((2, 5, 10, 18, 28)):
            occ += max(0.0, cloud_d(x - st * 0.4, y - st)) * (1.0 - k * 0.12)
        body = clamp(d * 4)
        v = clear - 1.6 - body * 2.8 - occ * 5.0 * (1.15 - 0.5 * t)
        v += (1 - clamp(occ * 7)) * clamp(d * 14) * 3.4                       # fresh top edges catch the light
        if cloud_d(x + 1, y + 3) <= 0: v -= 0.8                                # a crisp darker belly line
    st_ = strata(x, y)
    if st_ > 0:
        v = min(v, clear - 3.4 - clamp(st_ * 3) * 1.6 + (2.6 if strata(x, y - 2) <= 0 else 0))
    v += (NS[5](x * 1.3, y * 2.2) - 0.5) * 0.7 + (NS[4](x * 0.9, y * 2.0) - 0.5) * 0.4             # brush grain, breaks the contours
    v = clamp(v, 0.0, len(CLOUD) - 1.01)
    c = CLOUD[band(v, x, y)]
    gk = glow_k(x, y)
    if st_ > 0: gk *= 0.35 + 1.4 * (strata(x, y + 3) <= 0) * clamp((y - 230) / 40.0)       # bellies lit green
    elif d > 0: gk *= 0.6 + 0.9 * clamp((y - 170) / 120.0) * clamp(d * 5)
    if gk > 0.07:
        gc = GLOWR[min(len(GLOWR) - 1, max(0, band(gk * 8.5 - 1.0, x, y)))]
        c = mix(c, gc, clamp(gk * 1.05))
    return c

def haze_at(y):
    """the cloudless air colour at row y -- what far things fade into (the glow near the horizon)"""
    t = clamp(y / HY)
    c = CLOUD[int(clamp(9.2 + 4.6 * t ** 1.5 - 0.6, 0, len(CLOUD) - 1.01))]
    c2 = CLOUD[min(len(CLOUD) - 1, int(clamp(9.2 + 4.6 * t ** 1.5 - 0.6, 0, len(CLOUD) - 1.01)) + 1)]
    f = (9.2 + 4.6 * t ** 1.5 - 0.6) % 1
    c = tuple(c[i] + (c2[i] - c[i]) * f for i in range(3))
    gk = math.exp(-((y - 318) / 26.0) ** 2) * 0.82 + math.exp(-((y - 300) / 80.0) ** 2) * 0.26
    if y > 318: gk = max(gk, 0.82 - (y - 318) * 0.004)                       # below the glow line: the lit mist
    gk *= 0.9
    gc = GLOWR[min(len(GLOWR) - 1, max(0, int(gk * 8.5 - 1.0)))]
    return tuple(int(c[i] + (gc[i] - c[i]) * clamp(gk * 1.05)) for i in range(3))
HAZE_ROW = [haze_at(y) for y in range(H)]
MIST = (116, 144, 82)

print('sky...')
SKYB = [[sky_px(x, y) for x in range(W)] for y in range(H)]
# distant hills on the horizon, lost in the haze, darker against the glow (the sea takes the right of the horizon)
for x in range(W):
    ridge = 283 - 16 * NS[1](x * 0.9 + 77, 30) - 9 * NS[2](x * 1.2, 40) - 4 * NS[3](x * 1.5, 50) + 7 * clamp((x - 760) / 120.0) ** 1.5
    for y in range(max(0, int(ridge)), 306):
        k = 0.42 * clamp((y - ridge) / 3.0 + 0.4) * (1 - clamp((y - 294) / 14.0))
        SKYB[y][x] = mix(SKYB[y][x], mix(HAZE_ROW[y], (50, 66, 60), 0.55), k + (0.1 if y - ridge < 1.2 else 0))
if os.environ.get('SKY_ONLY'):
    im_ = Image.new('RGB', (W, H)); ip_ = im_.load()
    for y in range(H):
        for x in range(W): ip_[x, y] = SKYB[y][x]
    im_.save(os.path.join(OUT, 'sky_%d_%d.png' % (SKY_OX, SKY_OY))); sys.exit(0)

# ---------------------------------------------------------------------------------------------------- 2. the city below
# its own z-buffer (raster3d's quads) but its own shading and aerial perspective: no paintpass, no ink outlines far off
city = Raster()
FOGK = {}                                             # obj -> how much aerial haze it takes (1 = all)

def cbox(x0, x1, y0, y1, z0, z1, front, side, top=None, obj=None):
    """raster3d.Raster.box with cut shaders (None = no pixel: broken tops, holes)"""
    obj = obj or city.obj()
    city.quad((x0, y0, z0), (x1, y0, z0), (x0, y1, z0), front, obj, cut=True, cls='front')
    if x1 < 0: city.quad((x1, y0, z0), (x1, y0, z1), (x1, y1, z0), side, obj, cut=True, cls='side')
    elif x0 > 0: city.quad((x0, y0, z0), (x0, y0, z1), (x0, y1, z0), side, obj, cut=True, cls='side')
    if top is not None and y1 < CAMH: city.quad((x0, y1, z0), (x1, y1, z0), (x0, y1, z1), top, obj, cut=True, cls='top')
    return obj

def vine_hang(u, Y, Ytop, seed, dens=0.5, maxlen=40.0, z=300.0):
    """strands hanging from a roofline / ledge at Ytop: 0 = none, else 1 + how far down the strand (0..1)"""
    w = max(1.3, 1.1 * z / F)                                     # a strand is at least a pixel wide
    k = math.floor(u / w)
    if h32(k, seed, 71) % 3: return 0
    cl = wn(1, u * 0.06 + seed * 3.1, 7.0 + seed)
    if cl < 1 - dens * 0.8: return 0
    ln = maxlen * (0.25 + 0.75 * ((h32(k, seed, 72) % 100) / 100.0)) * (cl - (1 - dens * 0.8)) / (dens * 0.8 + 1e-6)
    dv = Ytop - Y
    if dv < 0 or dv > ln: return 0
    return 1 + dv / max(1.0, ln)

def wall_sh(b, face):
    """a building face: weathered material, a grid of windows when they are big enough to read, vines hanging from the
    roofline, a stepped broken top for ruins"""
    mat, seed = b['mat'], b['seed']
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = X if face == 'front' else Z
        prof = b.get('prof')
        if prof is not None and Y > prof(u): return None
        ppu = F / z
        v = b['v0'] + (0.0 if face == 'front' else -1.0) + (wn(0, u * 0.09 + seed, Y * 0.06) - 0.5) * 0.7 + 0.9 * clamp((Y - YG) / 420.0)
        v -= 0.8 * clamp((YG + 30 - Y) / 30)                        # damp, sooty foot
        c = None
        fl, bay = b['fl'], b['bay']
        hy = Y - YG
        fi = math.floor(hy / fl); fv = hy / fl - fi
        bi = math.floor((u - b['u0']) / bay); fu = (u - b['u0']) / bay - bi
        ytop = prof(u) if prof is not None else b['y1']
        style = b.get('style', 'grid')
        if ppu * fl > 2.4 and fi >= 1 and Y < ytop - fl * 0.4 and style != 'blank':
            ww = b['ww'] if style != 'ribbon' else 0.9
            if abs(fu - 0.5) < ww / 2 and ((0.32 < fv < 0.8) if not b.get('strip') else (0.12 < fv < 0.97)):
                k = h32(bi, fi, seed, 1 if face == 'front' else 2)
                if k % 1000 < b['lit'] * 10:
                    c = GLOW[1] if (k >> 4) % 3 else MYC[2]                            # a dim lit window
                elif k % 7 == 0 or (prof is not None and Y > ytop - fl * 2.2 and k % 3 == 0):
                    c = CSTONE[0]                                                       # a hole, a broken pane
                else:
                    c = tone(CSTONE, b['v0'] - 1.2 + fv * 1.2 - (0.8 if face != 'front' else 0) + (k % 3) * 0.3 + 0.9 * clamp((Y - YG) / 420.0), x, y)   # glass: the sky in it
            elif ppu * fl > 6 and fv < 0.07: v -= 0.7                                   # floor line
            elif ppu * fl > 6 and abs(fu - 0.5) < ww / 2 + 0.06 and 0.26 < fv < 0.32: v += 0.8    # a sill
        if style == 'blank' and ppu * fl > 4 and (fv < 0.06 or fu < 0.05): v -= 0.6                  # precast panel joints
        if prof is not None and ppu * fl > 3 and ytop - fl * 0.25 < Y: v += 1.0                     # the broken edge, lit
        if ppu * fl <= 2.4 and style != 'blank':                                                     # too far for windows: bays and floors as a weave
            v += (0.35 if bi % 2 else -0.15) - (0.5 if fi % 2 and (x + y) % 2 else 0)
        if face == 'front' and u - b['u0'] < 1.3 * z / F: v += 0.9                                    # the lit left arris
        elif prof is None and b['y1'] - Y < 1.2 * z / F: v += 0.8                                     # the parapet, lit from the sky
        if c is None: c = tone(mat, v, x, y)
        if b.get('banner') and face == 'front' and ppu * fl > 2.6 and bi == 1 + h32(seed, 92) % 3 and ytop - fl * 3.2 < Y < ytop - fl * 0.6 and abs(fu - 0.5) < 0.3:
            c = tone([RUSTY, OCHRE, COPPER][h32(seed, 93) % 3], 3.0 + (1.0 if fu < 0.45 else 0) - (ytop - Y) / fl * 0.3, x, y)   # a banner
        hv = vine_hang(u, Y, ytop, seed, b['vines'], b['vlen'], z)
        if hv:
            c = tone(VINE, 4.6 - (hv - 1) * 2.4 - (1.0 if face != 'front' else 0) + (h32(int(u * 3), int(Y * 0.7)) % 3) * 0.4, x, y)
        return c
    return sh

def roof_sh(b):
    """a flat roof seen from above: tar and gravel gone green, a raised parapet edge, puddles"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        if s < 0.04 or s > 0.96 or t < 0.06: return tone(b['mat'], b['v0'] + 0.8, x, y)
        g = wn(2, X * 0.12 + b['seed'], Z * 0.12) + (wn(3, X * 0.6, Z * 0.6) - 0.5) * 0.35
        if g > 0.62 - min(0.5, b['vines']) * 0.3: return tone(VINE, 1.4 + (g - 0.5) * 3 + (wn(3, X * 0.8, Z * 0.8) - 0.5) * 2.6, x, y)
        return tone(CSTONE, 2.4 + (wn(3, X * 0.3, Z * 0.3) - 0.5) * 1.6 + (0.6 if wn(1, X * 0.9, Z * 0.9) > 0.7 else 0), x, y)
    return sh

def flat(c): return lambda x, y, s, t, z, wp: c
def tone_sh(r, v): return lambda x, y, s, t, z, wp: tone(r, v, x, y)

def tri_sh(r, v0, lean=0.0):
    """a vertical triangle (a spire, a gable) lit on its left facet"""
    def sh(x, y, s, t, z, wp):
        half = 0.5 * (1 - t)
        if abs(s - 0.5 - lean * t) > half: return None
        d = (s - 0.5 - lean * t) / max(1e-6, half)
        return tone(r, v0 + (1.2 if d < -0.05 else -0.6) + (wn(0, wp[0] * 0.3, wp[1] * 0.3) - 0.5) * 0.6, x, y)
    return sh

def dome_sh(r, v0, onion=False):
    """a dome / an onion dome as a camera-facing silhouette, lit from the upper left"""
    def prof(t):
        if onion:
            if t < 0.62: return 0.5 * (0.78 + 0.22 * math.sin(t / 0.62 * math.pi * 0.85))
            return 0.5 * max(0.0, (1 - (t - 0.62) / 0.38)) ** 1.6
        return 0.5 * math.sqrt(max(0.0, 1 - t * t))
    def sh(x, y, s, t, z, wp):
        hw = prof(t)
        if abs(s - 0.5) > hw or hw <= 0: return None
        u = (s - 0.5) / hw
        v = v0 + 1.6 * (-u) * 0.9 + 1.0 * (0.5 - abs(u)) + t * 0.8
        if abs(u) > 0.86: v -= 0.8
        if onion and ((u + 1) * 4) % 1 < 0.14: v -= 0.7                                 # ribs
        return tone(r, v, x, y)
    return sh

def mast(X, Z, y0, y1, w0, seed):
    """a lattice mast: four tapering legs, X braces, a platform, its top light"""
    legs = []
    for (dx, dz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        legs.append(((X + dx * w0, y0, Z + dz * w0), (X + dx * w0 * 0.15, y1, Z + dz * w0 * 0.15)))
    sh = flat(CSTONE[1])
    for (a, b) in legs[:2] + legs[2:3]:
        city.line3(a, b, sh, w=0.9, cls='front')
    n = 7
    for i in range(n):
        ta, tb = i / n, (i + 1) / n
        def lp(L, tt): return tuple(L[0][j] + (L[1][j] - L[0][j]) * tt for j in range(3))
        city.line3(lp(legs[0], ta), lp(legs[1], tb), sh, w=0.6, cls='front')
        city.line3(lp(legs[1], ta), lp(legs[0], tb), sh, w=0.6, cls='front')
        city.line3(lp(legs[0], tb), lp(legs[1], tb), sh, w=0.6, cls='front')
    city.line3((X, y1, Z), (X, y1 + (y1 - y0) * 0.12, Z), sh, w=0.6, cls='front')

# ---- the buildings
def building(X, Z, w, d, h, kind, seed, protect=None, near=False):
    x0, x1 = X - w / 2, X + w / 2
    y1 = YG + h
    if protect is not None:                                                   # keep the egg / the needle clear
        for (px0, px1, py, pz) in protect:
            sx0, sx1 = CX + F * x0 / Z, CX + F * x1 / Z
            if Z < pz and sx1 > px0 and sx0 < px1:
                ymax = Y_at(py, Z)
                if y1 > ymax: y1 = ymax
                if kind not in ('block', 'ruin'): kind = 'block'                       # no spires or tiers poking up in front
        if y1 < YG + 12: return
        h = y1 - YG
    mat = [CSTONE, CSTONE, CSTONE, CPALE, CSTONE, CWARM, CSTONE, CPALE, CSTONE, CSTONE, CSTONE][h32(seed, 3) % 11]
    if kind == 'block' and 450 < Z < 2600 and h32(seed, 90) % 6 == 0 and y1 < 0:              # a chimney with a plume
        CHIMNEYS.append((X - w * 0.25, y1, Z, seed))
    if kind in ('tower', 'block') and 700 < Z < 2600 and h > 230: TOPS.append((X, y1, Z, w))
    b = dict(mat=mat, seed=seed, v0=2.4 + (h32(seed, 4) % 5) * 0.3, fl=10.5, bay=7.0 + (h32(seed, 5) % 4) * 1.5,
             ww=0.4 + (h32(seed, 6) % 3) * 0.08, lit=[1, 2, 3, 4, 6][h32(seed, 7) % 5], u0=x0, y1=y1,
             vines=0.25 + (h32(seed, 8) % 6) * 0.12, vlen=10 + (h32(seed, 9) % 5) * 9, prof=None, banner=h32(seed, 91) % 5 == 0,
             style=['grid', 'grid', 'grid', 'ribbon', 'blank', 'grid'][h32(seed, 10) % 6])
    if b['style'] == 'blank' and mat is CPALE: b['mat'] = CSTONE
    if Z < 750 and mat is not CSTONE: b['mat'] = CSTONE; b['v0'] -= 0.3
    if near: b['mat'] = CSTONE; b['v0'] -= 0.6; b['vines'] = min(1.0, b['vines'] + 0.35); b['vlen'] += 20
    if kind == 'ruin':
        st = b['bay'] * 0.8
        def prof(u, y1=y1, st=st, seed=seed, fl=b['fl']):
            k = math.floor(u / st)
            return y1 - fl * ((h32(k, seed, 11) % 5) * 0.9 + (h32(k, seed, 12) % 3) * 0.3)
        b['prof'] = prof
        b['vines'] = min(1.0, b['vines'] + 0.3)
    obj = city.obj()
    FOGK[obj] = 1.0
    top = roof_sh(b) if kind != 'ruin' else None
    if kind == 'tower':                                                        # art-deco setbacks
        tiers = 2 + h32(seed, 13) % 2
        yy, ww_, dd = YG, w, d
        for i in range(tiers):
            yt = YG + h * (0.62, 0.84, 1.0)[i] if tiers == 3 else YG + h * (0.75, 1.0)[i]
            bb = dict(b, u0=X - ww_ / 2, y1=yt)
            cbox(X - ww_ / 2, X + ww_ / 2, yy, yt, Z + (d - dd) / 2, Z + (d + dd) / 2, wall_sh(bb, 'front'), wall_sh(bb, 'side'), roof_sh(bb), obj=obj)
            yy = yt; ww_ *= 0.68; dd *= 0.68
        city.line3((X, yy, Z + d / 2), (X, yy + h * 0.14, Z + d / 2), flat(CSTONE[1]), w=0.8, cls='front')
        return
    cbox(x0, x1, YG, y1, Z, Z + d, wall_sh(b, 'front'), wall_sh(b, 'side'), top, obj=obj)
    if kind == 'ruin':                                                         # bare girders out of the break
        for k in range(1 + h32(seed, 14) % 3):
            gx = x0 + w * (0.2 + 0.6 * ((h32(seed, 15 + k) % 100) / 100))
            gt = y1 + 4 + h32(seed, 18 + k) % 14
            city.line3((gx, y1 - 14, Z - 0.2), (gx + (h32(seed, 21 + k) % 7 - 3), gt, Z - 0.2), flat(CWARM[1]), w=0.9, cls='front')
    elif kind == 'spire':                                                      # a church: a tower, a needle spire, pinnacles
        tw = w * 0.42; tx = x0 + w * (0.25 if h32(seed, 16) % 2 else 0.75)
        th = y1 + h * 0.45
        bb = dict(b, mat=CSTONE, u0=tx - tw / 2, y1=th, vlen=b['vlen'] * 0.6)
        cbox(tx - tw / 2, tx + tw / 2, y1 - 1, th, Z - 0.5, Z + tw - 0.5, wall_sh(bb, 'front'), wall_sh(bb, 'side'), obj=obj)
        sh_h = min(h * 0.6, tw * (2.4 + (h32(seed, 17) % 4) * 0.5))
        city.quad((tx - tw / 2 - 0.5, th, Z + tw / 2 - 0.5), (tx + tw / 2 + 0.5, th, Z + tw / 2 - 0.5), (tx - tw / 2 - 0.5, th + sh_h, Z + tw / 2 - 0.5),
                  tri_sh(COPPER if h32(seed, 19) % 2 else CSTONE, 2.4), obj, cut=True, cls='front')
        for px in (tx - tw / 2, tx + tw / 2):
            city.quad((px - 1.2, th, Z - 0.6), (px + 1.2, th, Z - 0.6), (px - 1.2, th + sh_h * 0.25, Z - 0.6), tri_sh(CSTONE, 2.6), obj, cut=True, cls='front')
        city.quad((x0, y1, Z + d * 0.3), (x1, y1, Z + d * 0.3), (x0, y1 + w * 0.35, Z + d * 0.3), tri_sh(CWARM, 2.2), obj, cut=True, cls='front')   # the nave roof
    elif kind in ('dome', 'onion'):
        dw = w * (0.7 if kind == 'dome' else 0.55)
        dh = dw * (0.55 if kind == 'dome' else 1.25)
        dr = h32(seed, 23) % 3
        rr = [GOLDD, COPPER, CPALE][dr] if Z > 750 else COPPER
        city.quad((X - dw / 2, y1, Z + d * 0.4), (X + dw / 2, y1, Z + d * 0.4), (X - dw / 2, y1 + dh, Z + d * 0.4), dome_sh(rr, 2.2, kind == 'onion'), obj, cut=True, cls='front')
        if kind == 'onion': city.line3((X, y1 + dh, Z + d * 0.4), (X, y1 + dh + dw * 0.3, Z + d * 0.4), flat(rr[1]), w=0.6, cls='front')
    elif kind == 'zigg':                                                       # a stepped temple
        yy, ww_ = y1, w
        for i in range(4):
            ww_ *= 0.74
            bb = dict(b, mat=CPALE, u0=X - ww_ / 2, y1=yy + h * 0.12, lit=0, vines=0.7)
            cbox(X - ww_ / 2, X + ww_ / 2, yy, yy + h * 0.12, Z + (w - ww_) / 2, Z + (w + ww_) / 2, wall_sh(bb, 'front'), wall_sh(bb, 'side'), roof_sh(bb), obj=obj)
            yy += h * 0.12
    elif kind == 'pagoda':                                                     # tiers with wide eaves
        yy, ww_ = y1, w * 0.6
        for i in range(4):
            city.quad((X - ww_ * 0.75, yy + 1.5, Z - 1), (X + ww_ * 0.75, yy + 1.5, Z - 1), (X - ww_ * 0.75, yy + 4.0, Z - 1), tri_sh(CWARM, 1.8), obj, cut=True, cls='front')
            bb = dict(b, mat=CWARM, u0=X - ww_ / 2, y1=yy + 9, lit=6)
            cbox(X - ww_ / 2, X + ww_ / 2, yy, yy + 9, Z, Z + ww_, wall_sh(bb, 'front'), wall_sh(bb, 'side'), obj=obj)
            yy += 9; ww_ *= 0.8
    if kind in ('block', 'ruin') and y1 < -60 and h32(seed, 26) % 3 == 0:     # trees gone wild on the roof
        for k in range(1 + h32(seed, 27) % 4):
            tx = x0 + w * ((h32(seed, 28 + k) % 100) / 100.0); tz = Z + d * ((h32(seed, 32 + k) % 100) / 100.0)
            r_ = 3.0 + (h32(seed, 36 + k) % 5)
            ty = (prof(tx) if kind == 'ruin' else y1) + r_ * 0.7
            city.disc(tx, ty, tz, r_, lambda x, y, s_, t_, z, wp: (tone(VINE, 3.6 - t_ * 2.2 - s_ * 0.8 + (wn(3, x * 0.7, y * 0.7) - 0.5) * 2.2, x, y)
                                                                  if s_ * s_ + t_ * t_ < 0.8 + 0.3 * wn(1, x * 0.9, y * 0.9) else None), obj, cls='front')
    if kind == 'block' and h32(seed, 25) % 3 == 0 and y1 < CAMH:               # rooftop clutter: a water tank, an aerial
        tx = x0 + w * 0.3
        cbox(tx - 2.5, tx + 2.5, y1 + 3, y1 + 9, Z + 3, Z + 8, tone_sh(CWARM, 2.4), tone_sh(CWARM, 1.4), tone_sh(CWARM, 3.0), obj=obj)
        for lx in (tx - 2, tx + 2): city.line3((lx, y1, Z + 3), (lx, y1 + 3, Z + 3), flat(CSTONE[1]), w=0.5, cls='front')
        city.line3((x1 - 3, y1, Z + 4), (x1 - 3, y1 + 18, Z + 4), flat(CSTONE[1]), w=0.5, cls='front')

EGG_SX, EGG_SY, EGG_A, EGG_B, EGG_Z = 272, 282, 138, 90, 330.0
NEEDLE_SX, NEEDLE_Z = 549, 420.0                       # Scraper 1140's mast
PROTECT = [(EGG_SX - 196, EGG_SX + 196, 440, EGG_Z), (482, 594, 392, NEEDLE_Z),
           (405, 492, 362, 950), (598, 658, 352, 1150), (658, 800, 394, 650), (800, 890, 414, 560), (880, 1067, 352, 1450)]
MISTK = {}                                            # obj -> how much of the low mist it takes (1 = all)
def coast_z(sx):
    """the coastline on the right: beyond this depth the city gives way to the sea (screen column sx)"""
    return 4600 - (sx - 850) * 17.5 if sx > 850 else 1e9
CHIMNEYS, TOPS = [], []
TALL = ['block'] * 30 + ['tower'] * 26 + ['ruin'] * 22 + ['mast'] * 6 + ['spire'] * 4 + ['onion'] * 2
LOW = ['block'] * 40 + ['ruin'] * 30 + ['spire'] * 8 + ['dome'] * 5 + ['onion'] * 4 + ['zigg'] * 3 + ['pagoda'] * 3
crng = random.Random(1140)
def place(Z, sx, w, d, h, kind, seed, near=False):
    if Z > coast_z(sx) - 40 or Z > coast_z(sx + w * F / Z * 0.5) - 40: return     # the sea
    if sx > 850 and Z > 700: h = min(h, 40 + Z * 0.02); kind = 'block' if kind in ('tower', 'mast', 'spire', 'onion') else kind   # the low harbour district
    X = X_at(sx, Z)
    if kind == 'mast':
        sxl, sxr = CX + F * (X - 6) / Z, CX + F * (X + 6) / Z
        if any(Z < pz and sxr > px0 and sxl < px1 for (px0, px1, py, pz) in PROTECT): return
        obj = city.obj(); FOGK[obj] = 1.0
        mast(X, Z, YG, YG + h, w * 0.1, seed)
        return
    building(X, Z, w, d, h, kind, seed, PROTECT, near)
print('city...')
# the skyline: slender towers, far and hazy (the farther, the more of them)
for i in range(330):
    Z = 700 + (crng.random() ** 0.7) * 4800
    sx = crng.uniform(-90, W + 90)
    w = crng.uniform(24, 70) * (0.7 + Z / 9000)
    h = crng.uniform(140, 560) * (0.55 + 0.6 * crng.random() ** 2)
    place(Z, sx, w, w * crng.uniform(0.7, 1.3), h, crng.choice(TALL), 10000 + i)
# the carpet of low roofs, ruins and temples between them (sampled evenly in screen rows, so it fills the view)
for i in range(620):
    yb = crng.uniform(304, 540)
    Z = F * (CAMH - YG) / (yb - HY)
    if Z < 300: continue
    sx = crng.uniform(-60, W + 60)
    w = crng.uniform(16, 46)
    h = crng.uniform(14, 80) * (0.6 + 0.8 * crng.random() ** 2)
    place(Z, sx, w, w * crng.uniform(0.7, 1.5), h, crng.choice(LOW), 20000 + i)
# near ruins framing the view at the sides, dark and overgrown
for i in range(14):
    Z = crng.uniform(300, 520)
    sx = crng.choice((crng.uniform(-60, 125), crng.uniform(905, W + 60)))
    w = crng.uniform(24, 50)
    h_ = crng.uniform(90, 230); kind_ = crng.choice(('ruin', 'ruin', 'block', 'tower'))
    if sx > 60: continue                                  # keep the harbour side open, frame only the far left
    place(Z, sx, w, w * crng.uniform(0.8, 1.3), h_ * 0.6, kind_, 30000 + i, near=True)
# the ground of the city, lost in the mist
city.quad((-9000, YG, 250), (9000, YG, 250), (-9000, YG, 7000), lambda x, y, s, t, z, wp: tone(CSTONE, 3.0 + wn(2, wp[0] * 0.05, wp[2] * 0.05) * 2, x, y), cls='top')

def sq(sx0, sx1, sy0, sy1, Z, sh, obj, cls='front'):
    """a vertical quad given in screen pixels at depth Z (sy0 bottom, sy1 top); its shader may work in screen pixels"""
    X0, X1 = X_at(sx0, Z), X_at(sx1, Z); Y0, Y1 = Y_at(sy0, Z), Y_at(sy1, Z)
    city.quad((X0, Y0, Z), (X1, Y0, Z), (X0, Y1, Z), sh, obj, cut=True, cls=cls)

# ---- Scraper 1140 in the middle (z 420): the dark weathered concrete monolith of ScraperScene (scraper_native_bg.py)
#      seen from afar -- the lettered slab with floor ledges and soot runs, the near-black service shafts stepped on its
#      left with plant rooms, a tank and aerials, a riser on its right, the cornice and finned crown with finials, and a
#      tall antenna mast that keeps the old needle silhouette; one small amber window low; the letters a faint smudge.
# ramps copied from scraper_native_bg.py (FACER = the lettered face, TOWR = the shafts, CREAM = the letters' paint)
FACER = ramp('#0f1614 #131b18 #17201d #1b2622 #1f2b27 #24312c #293832 #2e3e37 #33453d #394c43 #3f5349 #465a50 #4e6257')
TOWR = ramp('#101413 #151a19 #1a201e #1f2723 #252e29 #2b362f #313e35 #37463b #3d4e42 #445648 #4c5e4f #556756 #5e7060')
CREAM = ramp('#4a4c3d #5f604b #78785b #92916b #a7a57a #b8b588 #c7c396 #d4d0a4')
AMBER = ramp('#3a2414 #5a3418 #82481e #a95f26 #cb7c31 #e29b43 #f0b961 #f8d48a #ffeabf')
SCR_Z = 420.0
SL0, SL1, SLT = 528, 572, 128                       # the slab: x from, x to, its top (the cornice above it)
SCR_WIN = (547, 549, 392, 395)                      # the one lit window
SCR_LIGHTS = ((514, 258), (521, 331), (497, 342), (502, 381), (577, 222))
from common import FONT
SCR_TXT = {}
def _scr_letters():
    for (word, y0) in (('SCRAPER', SLT + 8), ('1140', SLT + 15)):
        wd = sum(len(FONT[ch][0]) + 1 for ch in word) - 1
        x0 = (SL0 + SL1) // 2 - wd // 2 + 1
        for ch in word:
            for r, row in enumerate(FONT[ch]):
                for k, bit in enumerate(row):
                    if bit == '1': SCR_TXT[(x0 + k, y0 + r)] = 1
            x0 += len(FONT[ch][0]) + 1
_scr_letters()

def scr_soot(x, y, top, every, seed):
    """a run of soot hanging from the ledge above (0..1), per pixel column, in clusters"""
    kb = (y - top) // every
    hs = h32(x, kb, seed, 77)
    if hs % 3 or wn(2, x * 0.4 + seed, kb * 3.1) < 0.4: return 0.0
    d = (y - top) - kb * every
    L = 2 + (hs >> 6) % 7
    return (1 - d / L) if 1 <= d < L else 0.0

def scr_slab(x, y, s, t, z, wp):
    pu, pv = (x - SL0) // 5, (y - SLT) // 4
    hp = h32(pu, pv, 51)
    val = 6.6 + ((hp % 7) - 3) * 0.14 - (0.8 if hp % 17 == 0 else 0) + (0.7 if hp % 31 == 5 else 0)
    val += (wn(0, x * 0.25, y * 0.1) - 0.5) * 1.6 + (wn(1, x * 1.3, y * 1.3) - 0.5) * 0.8
    val -= 2.0 * max(0.0, wn(3, x * 0.5, y * 0.2) - 0.55) * 2.5                       # dark weather blotches
    val += 0.6 * clamp((330 - y) / 200.0)                                               # the sky lights the upper face
    ly = (y - SLT) % 8
    if ly == 0 and y > SLT + 22: val += 2.0                                             # a floor ledge, lit
    elif ly == 1 and y > SLT + 22: val -= 1.4                                           # its underside
    val -= 2.2 * scr_soot(x, y, SLT, 8, 3)
    if y < SLT + 6: val -= 1.8 * clamp((wn(2, x * 0.6, 1) - 0.2) * 3)                  # soot under the cornice
    if x == SL0: val += 1.6                                                             # the left arris catches the sky
    elif x <= SL0 + 2: val -= 1.0                                                       # in the shafts' shadow
    if x >= SL1 - 1: val -= 1.4
    if h32(x // 2, y // 3, 52) % 97 == 0: val -= 2.0                                    # a vent slot
    c = tone(FACER, val, x, y)
    if (x, y) in SCR_TXT and wn(3, x * 1.7 + 40, y * 1.7) < 0.8:                       # the letters, faded, peeling
        c = mix(c, tone(CREAM, 4.0 + (wn(1, x * 2, y * 2) - 0.5) * 2, x, y), 0.55)
    elif (x, y - 1) in SCR_TXT and h32(x, 53) % 3 == 0: c = mix(c, CREAM[1], 0.3)      # paint washed down under them
    if SCR_WIN[0] <= x <= SCR_WIN[1] and SCR_WIN[2] <= y <= SCR_WIN[3]:
        return AMBER[6] if (x + y) % 2 else AMBER[5]
    d = math.hypot(max(SCR_WIN[0] - x, 0, x - SCR_WIN[1]), max(SCR_WIN[2] - y, 0, y - SCR_WIN[3]) * 0.8)
    if d < 7: c = tuple(min(255, int(c[i] + (105, 52, 14)[i] * 0.5 * math.exp(-d / 2.5))) for i in range(3))
    return c

def scr_mass(seed, every=6):
    """the service shafts: near-black, channelled (pipes lit on their left), ledges, a few amber portholes"""
    def sh(x, y, s, t, z, wp):
        if (x, y) in SCR_LIGHTS: return AMBER[5]
        val = 1.8 + (wn(0, x * 0.2 + seed, y * 0.08) - 0.5) * 1.6 + (wn(2, x * 1.4, y * 1.4) - 0.5) * 0.7
        g = (x + seed) // 3; fu = (x + seed) % 3
        kind = h32(g, seed, 5) % 5
        if kind == 0: val += 1.1 if fu == 0 else (-0.6 if fu == 2 else 0.2)              # a pipe
        elif kind == 1: val -= 0.8                                                       # a recess
        if (y - 40) % every == 0: val += 1.4
        elif (y - 40) % every == 1: val -= 0.9
        val -= 1.6 * scr_soot(x, y, 40, every, seed)
        return tone(TOWR, val, x, y)
    return sh

def scr_flat(v0, dv=0.6):
    return lambda x, y, s, t, z, wp: tone(TOWR, v0 + (wn(1, x * 0.5, y * 0.5) - 0.5) * dv * 2, x, y)

def spike(cx, y0, y1, w, Z, v0, obj):
    """a finial / pinnacle: tapering from w px at y0 up to a point at y1, lit on its left"""
    def sh(x, y, s, t, z, wp):
        half = max(0.5, w / 2 * (1 - t) ** 0.7)
        if abs(x + 0.5 - cx) > half: return None
        return tone(TOWR, v0 + (1.2 if x + 0.5 < cx else 0), x, y)
    sq(cx - w / 2 - 0.5, cx + w / 2 + 0.5, y0, y1, Z, sh, obj)

def aerial(cx, y0, y1, Z, obj, bars=10):
    sq(cx, cx + 1.01, y0, y1, Z, scr_flat(1.4, 0.3), obj)
    k = 1
    while y0 - k * bars > y1 + 3:
        hw = max(1, 3 - k // 2)
        sq(cx - hw, cx + hw + 1.01, y0 - k * bars + 1, y0 - k * bars, Z, scr_flat(2.0, 0.3), obj)
        k += 1

def scraper():
    obj = city.obj(); FOGK[obj] = 0.55
    Z = SCR_Z
    sq(SL0, SL1, 480, SLT, Z, scr_slab, obj)                                                    # the lettered slab
    sq(SL0 - 2, SL1 + 2, SLT, SLT - 4, Z - 1, lambda x, y, s, t, z, wp: tone(TOWR, 6.0 if y == SLT - 4 else (1.2 if y == SLT - 1 else 4.2), x, y), obj)   # cornice
    def crown(x, y, s, t, z, wp):
        val = 3.2 + (wn(1, x * 0.3, y * 0.2) - 0.5) * 1.2
        if (x - 531) % 4 == 0: val += 1.3                                                    # tall fins
        elif (x - 531) % 4 == 1: val -= 0.9
        return tone(TOWR, val, x, y)
    sq(531, 568, SLT - 4, 104, Z + 1, crown, obj)
    sq(530, 538, 104, 96, Z, scr_mass(41, 4), obj)                                            # plant rooms on the crown
    sq(559, 567, 104, 100, Z, scr_mass(43, 4), obj)
    for (cx, top, w) in ((530.5, 84, 3), (536, 92, 2), (563, 80, 3), (567.5, 90, 2)):         # finials
        spike(cx, 104, top, w, Z - 0.5, 2.0, obj)
    # the antenna mast: the old needle's silhouette
    sq(548, 550.01, 104, 70, Z + 0.5, scr_flat(1.6, 0.3), obj)
    sq(548.5, 549.51, 70, 40, Z + 0.5, scr_flat(1.6, 0.3), obj)
    for (yy, hw) in ((96, 4), (86, 3), (76, 2), (62, 1)):
        sq(549 - hw, 550 + hw, yy + 1, yy, Z + 0.5, scr_flat(2.2, 0.3), obj)
    city.disc(X_at(549.5, Z), Y_at(40.5, Z), Z, 0.7, lambda x, y, s, t, z, wp: AMBER[4], cls='emit')    # its light
    # the shafts on the left, stepped, with their roof clutter
    sq(508, SL0, 480, 214, Z - 2, scr_mass(3), obj)
    sq(490, 508, 480, 296, Z - 3, scr_mass(9), obj)
    sq(489, 509, 297, 295, Z - 3.5, scr_flat(3.8), obj)                                         # parapet lips
    sq(507, 529, 215, 213, Z - 2.5, scr_flat(3.8), obj)
    sq(492, 503, 296, 287, Z - 2.5, scr_mass(31, 4), obj)                                     # a plant room
    def tank(x, y, s, t, z, wp):
        n = (x + 0.5 - 506) / 2.5
        if abs(n) > 1: return None
        return tone(TOWR, 2.8 - n * 1.6 + (1.0 if y % 3 == 0 else 0), x, y)
    sq(503, 509, 296, 286, Z - 3.2, tank, obj)
    aerial(494, 287, 262, Z - 3.2, obj, 8); aerial(500, 287, 274, Z - 3.2, obj, 7)
    spike(490.5, 296, 279, 2, Z - 3.6, 1.6, obj)
    sq(516, 526, 214, 205, Z - 2.2, scr_mass(17, 4), obj)
    aerial(512, 214, 184, Z - 2.4, obj, 9)
    # the riser on the right, a clad pipe up it, a gantry off it
    sq(SL1, 581, 480, 176, Z - 1, scr_mass(23), obj)
    sq(576, 578.01, 480, 182, Z - 1.3, lambda x, y, s, t, z, wp: tone(TOWR, 3.4 if x == 576 else 1.6, x, y), obj)
    sq(581, 590, 251, 249, Z - 1.5, scr_flat(2.6), obj)
    for gx in (583, 586, 589): sq(gx, gx + 1.01, 249, 245, Z - 1.5, scr_flat(1.8), obj)
    sq(482, 490, 331, 329, Z - 3.5, scr_flat(2.6), obj)                                         # a gantry off the shafts
    for gx in (482, 485, 488): sq(gx, gx + 1.01, 329, 325, Z - 3.5, scr_flat(1.8), obj)
scraper()

# ---- the Egg Cathedral on the left: as it stands now (EggCatedralScene, the map) -- the giant egg split in two, the
#      halves parted with jagged broken rims, ivy over the shells and grown into their cracks, the gothic cathedral
#      standing between them (twin spires with finials, smaller outer towers, a rose window, a lit door)
CB = 386                                             # where the cathedral stands: the saddle of the mound between the shells
# ---- the ground the egg broke out of: a great mound of heaved earth, the shells sunk into it (the Egg Emergence)
MOUND = (80, 466)                                    # its foot, left and right (screen x)
SOIL = ramp('#1a140e #241b12 #2f2417 #3b2e1d #4a3a25 #5b4830 #6d583b')
def _g(x, c, w): return math.exp(-((x - c) / w) ** 2)
def mound_top(x):
    """the mound's top edge (screen y) at column x: heaped up against both shells (higher on the left), a saddle
    under the cathedral, slumped terraces and lumps down its flanks"""
    if x < MOUND[0] or x > MOUND[1]: return 999.0
    t = (x - 272) / ((MOUND[1] - MOUND[0]) / 2)
    y = 452 - 86 * max(0.0, 1 - abs(t) ** 1.25)
    y -= 32 * _g(x, 190, 38) + 26 * _g(x, 354, 34) + 6 * _g(x, 118, 12) + 5 * _g(x, 428, 10)
    y += 5 * _g(x, 140, 7) + 4 * _g(x, 404, 6)                                    # slumped terraces
    w = clamp(1 - (abs(x - 272) - 30) / 12.0)
    y = y * (1 - w) + CB * w                                                      # the saddle the cathedral stands on
    y += (wn(1, x * 0.21, 7.0) - 0.5) * 6 * (1 - w) + (wn(3, x * 0.8, 2.0) - 0.5) * 2.5 * (1 - w)
    return y

EGGC = {}
EGG_SH, EGG_LEAN = 31, 0.05                          # how far each half has moved out, how much it leans away at the top
def egg():
    obj = city.obj(); FOGK[obj] = 0.42
    cx, cy, A, B = EGG_SX, EGG_SY, EGG_A, EGG_B
    L = (-0.42, 0.74, 0.52); ll = math.sqrt(sum(c * c for c in L)); L = tuple(c / ll for c in L)
    def half_w(dy):
        v = -dy / A
        if abs(v) >= 1: return 0.0
        return B * math.sqrt(1 - v * v) * (1 - 0.13 * v)
    erng = random.Random(330)
    # the break: one jagged line down the middle of the egg, the two halves' rims are its two sides
    jr = random.Random(34)
    JP = []; yy, off = -A - 6.0, 0.0
    while yy < A + 12:                                         # irregular teeth: long and short runs, big and small
        JP.append((yy, off))
        yy += jr.choice((3, 4, 5, 6, 8, 10, 13, 16))
        off = max(-11.0, min(11.0, off * 0.35 + jr.choice((-1, 1)) * jr.uniform(1.5, 8.5)))
    def jx(dy):
        for (a_, b_) in zip(JP, JP[1:]):
            if a_[0] <= dy < b_[0]:
                t = (dy - a_[0]) / (b_[0] - a_[0])
                return a_[1] + (b_[1] - a_[1]) * t
        return 0.0
    def inside(px, py, side):
        if abs(px) >= half_w(py) - 0.5: return False
        return px < jx(py) - 1.5 if side < 0 else px > jx(py) + 1.5
    # cracks running in from the broken rims and up from the foot; the main ones with vines grown into them
    CR = {}
    def walk(x0, y0, ang, n, depth, vine, side):
        x, y = x0, y0
        for i in range(n):
            ang += erng.uniform(-0.5, 0.5)
            nx, ny = x + math.cos(ang) * 2.6, y + math.sin(ang) * 2.6
            for k in range(4):
                px, py = x + (nx - x) * k / 4, y + (ny - y) * k / 4
                if not inside(px, py, side): return
                ix, iy = int(round(px)), int(round(py))
                if vine and i < n * 0.8:
                    CR[(ix, iy)] = 3
                    for (ox, oy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        if CR.get((ix + ox, iy + oy)) != 3: CR[(ix + ox, iy + oy)] = 1
                else:
                    if CR.get((ix, iy)) != 3: CR[(ix, iy)] = 1
                    CR.setdefault((ix + 1, iy + 1), 2)
            x, y = nx, ny
            if depth < 2 and i in (n // 3, (2 * n) // 3) and erng.random() < 0.65:
                walk(x, y, ang + erng.choice((-1, 1)) * erng.uniform(0.6, 1.1), int(n * 0.55), depth + 1, vine and depth == 0, side)
    for k in range(26):
        side = -1 if k % 2 else 1
        dy = erng.uniform(-0.85, 0.85) * A
        walk(jx(dy) + side * 2.5, dy, (math.pi if side < 0 else 0.0) + erng.uniform(-0.8, 0.8), erng.randint(8, 22), 0, k % 3 == 0, side)
    for k in range(10):
        side = -1 if k % 2 else 1
        u = erng.uniform(0.15, 0.9) * side
        dy = A * 0.9
        walk(u * half_w(dy), dy - 1, -math.pi / 2 + erng.uniform(-0.6, 0.6), erng.randint(10, 22), 0, k % 2 == 0, side)
    # vines wrapping the shells, out of the hedges at the foot, round the back and out again
    VN = {}
    for k in range(14):
        lon0 = erng.uniform(-math.pi, math.pi)
        twist = erng.choice((-1, 1)) * erng.uniform(0.7, 1.9)
        vtop = erng.uniform(-0.1, 0.9)
        v = -0.92; i = 0
        while v < vtop:
            lon = lon0 + twist * (v + 1) + 0.18 * math.sin(v * 9 + k)
            if math.cos(lon) > 0.08:
                dy = -v * A; hw = half_w(dy); dx = hw * math.sin(lon)
                w = 3.8 * (1 - (v + 0.92) / (vtop + 0.92)) + 1.3
                for ox in range(-3, 4):
                    if abs(ox) <= w / 2:
                        key = (int(round(dx + ox)), int(round(dy)))
                        VN[key] = max(VN.get(key, -9), 1.4 if ox < 0 else (-0.9 if ox >= w / 2 - 1 else 0.3))
                if i % 9 == 0:
                    s_ = 1 if (i // 9) % 2 else -1
                    for (lx, ly, sh) in ((s_ * (w / 2 + 1), 0, 1.0), (s_ * (w / 2 + 2), -1, 2.2), (s_ * (w / 2 + 2), 0, 0.6), (s_ * (w / 2 + 3), -1, 1.6)):
                        VN[(int(round(dx + lx)), int(round(dy + ly)))] = sh
            v += 0.5 / A; i += 1
    reach = int(B + EGG_SH + EGG_LEAN * 2 * A + 4)
    for y in range(int(cy - A) - 1, int(cy + A) + 2):
        dy = y + 0.5 - cy
        shift = EGG_SH + EGG_LEAN * (cy + A - y)
        for x in range(int(cx - reach), int(cx + reach) + 1):
            dx = x + 0.5 - cx
            for side in (-1, 1):
                dxo = dx - side * shift                                         # where this pixel was on the whole egg
                e = (dxo - jx(dy)) * (-side)                                    # how far from the break, inward = negative
                if e > 0: continue
                hw = half_w(dy)
                if hw <= 0 or abs(dxo) >= hw: continue
                v = -dy / A; cv = math.sqrt(max(0.0, 1 - v * v)) * (1 - 0.13 * v)
                u = dxo / hw
                su = math.sqrt(max(0.0, 1 - u * u))
                n = (u * cv, v, su * cv); nl = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1; n = (n[0] / nl, n[1] / nl, n[2] / nl)
                lon, lat = math.asin(clamp(u, -1, 1)), math.asin(clamp(v, -1, 1))
                diff = max(0.0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2])
                val = 1.4 + 6.8 * (0.62 * diff + 0.38 * (0.5 + 0.5 * n[1]))
                val += (wn(0, lon * 9 + 50, lat * 9) - 0.5) * 1.3 + (wn(1, lon * 30, lat * 30) - 0.5) * 0.5
                gd = mound_top(x) - y                                                    # how high above the ground here
                if gd < -1: continue                                                     # sunk into the mound
                val -= 2.6 * clamp(1 - gd / 12.0) + 0.8 * clamp((-v - 0.45) / 0.5)        # contact shadow, the foot in shade
                ix, iy = int(round(dxo)), int(round(dy))
                c = None
                cr = CR.get((ix, iy))
                if cr == 1: c = tone(SHELL, val - 3.0, x, y)
                elif cr == 2: c = tone(SHELL, val + 0.9, x, y)
                elif cr == 3: c = tone(VINE, 3.4 + (val - 5) * 0.35 + (1.0 if h32(x, y, 47) % 3 == 0 else 0), x, y)
                iv = wn(2, lon * 7 + 3, lat * 5) + 0.9 * clamp((-v - 0.05) / 0.5) - 0.25 * abs(u) + 0.5 * clamp(1 - gd / 45.0)
                if iv > 0.95:                                                            # a skin of ivy over the lower shell
                    lv = 2.2 + (1.4 if n[0] < -0.1 else 0) + (wn(3, x * 0.8, y * 0.8) - 0.5) * 2.4 + (val - 5) * 0.25
                    if h32(x, y, 46) % 5 == 0: lv += 1.2
                    c = tone(VINE, lv - (1.0 if iv < 1.0 else 0), x, y)
                vn = VN.get((ix, iy))
                if vn is not None:
                    c = tone(VINE, 2.0 + vn + (val - 5) * 0.3 - clamp((-v - 0.2) / 0.5) * 0.8, x, y)
                if e > -1.4: c = tone(SHELL, 8.8 - (0.0 if side < 0 else 1.4), x, y)        # the broken lip, catching the light
                elif e > -6.5:                                                           # the shell's thick wall, then the dark inside
                    q = (e + 6.5) / 5.1
                    c = tone(SHELL, 2.2 + q * 3.0 + (0.7 if side < 0 else 0) + (wn(1, x * 0.9, y * 0.9) - 0.5) * 0.8, x, y)
                    if q < 0.25: c = mix(c, (60, 52, 40), 0.35)                          # the membrane inside, yellowed
                if c is None: c = tone(SHELL, val, x, y)
                rk = (1 - n[2]) ** 2.5 * clamp(0.75 - n[1])
                if rk > 0.08 and e < -6.5: c = mix(c, GLOWR[4], clamp(rk * 0.9))       # the city's glow on the outer rim
                EGGC[(x, y)] = c
                city.put(x, y, 298 - n[2] * 8, lambda x_, y_, a, b, z, wp: EGGC[(x_, y_)], obj, 0, 0,
                         (X_at(x + 0.5, EGG_Z), Y_at(y + 0.5, EGG_Z), EGG_Z), n, 'egg')
egg()

CATH_Z = 312.0
def gothic_sh(seed, lit=0.0, wins=True):
    """a tower shaft: coursed stone, lit on the left, lancet slits (some warm), ivy up from the foot"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        v = 3.4 + (1.4 if s < 0.3 else -0.5 if s > 0.75 else 0.3) + (wn(0, X * 0.4, Y * 0.4) - 0.5) * 0.8
        if s < 0.06 or s > 0.94: v -= 0.8
        if (Y * 0.5) % 1 < 0.12: v -= 0.4                                                      # courses
        c = tone(CSTONE, v, x, y)
        if wins:
            fv = (t * 5) % 1; fi = int(t * 5)
            if 0.4 < s < 0.6 and 0.2 < fv < 0.8 and fi >= 1:
                c = GLOW[1] if h32(seed, fi, 41) % 100 < lit * 100 else CSTONE[0]
                if fv > 0.72 and abs(s - 0.5) > 0.06: c = tone(CSTONE, v, x, y)               # the pointed head
        g = wn(2, X * 0.3 + seed, Y * 0.12) + 0.6 * clamp(0.5 - t) - 0.25
        if g > 0.5:
            c = tone(VINE, 2.4 + (1.0 if s < 0.4 else 0) + (wn(3, X * 1.6, Y * 1.6) - 0.5) * 2.4 - (0.8 if g < 0.54 else 0), x, y)
        return c
    return sh

def slate_spire(seed):
    """a slate spire: lit facet left, shaded right, slate courses, a crocket line on the arris"""
    def sh(x, y, s, t, z, wp):
        half = 0.5 * (1 - t)
        if abs(s - 0.5) > half: return None
        d = (s - 0.5) / max(1e-6, half)
        v = 2.2 + (1.4 if d < -0.05 else -0.4) + (wn(0, wp[0] * 0.5, wp[1] * 0.5) - 0.5) * 0.6
        if (t * 14) % 1 < 0.12: v -= 0.5
        if abs(d) > 0.82 and int(t * 22) % 2 == 0: v += 1.0                                   # crockets on the edges
        return tone(CSTONE, v, x, y)
    return sh

def cathedral():
    """between the parted shells, on the heaved ground: twin towers with tall slate spires and finials, two smaller
    outer towers, the nave front with a gable and a rose window, lancets lit warm, the arched door glowing; buttress
    arches"""
    obj = city.obj(); FOGK[obj] = 0.45
    Z = CATH_Z
    cx = EGG_SX
    sq(cx - 36, cx + 36, CB + 8, CB - 92, Z + 3, gothic_sh(55, 0.3), obj)                               # the nave front
    for (x0, w, shaft, tip, seed) in ((cx - 41, 10, CB - 118, CB - 156, 1), (cx + 31, 10, CB - 116, CB - 152, 2)):   # outer towers
        sq(x0, x0 + w, CB + 8, shaft, Z + 1, gothic_sh(seed, 0.4), obj)
        sq(x0 - 1, x0 + w + 1, shaft, tip, Z + 0.8, slate_spire(seed), obj)
    for (x0, w, shaft, tip, seed) in ((cx - 27, 16, CB - 186, CB - 246, 3), (cx + 11, 16, CB - 184, CB - 242, 4)):   # the twin towers
        sq(x0, x0 + w, CB + 8, shaft, Z, gothic_sh(seed, 0.28), obj)
        sq(x0 - 1, x0 + w + 1, shaft, tip, Z - 0.3, slate_spire(seed), obj)
        for px in (x0, x0 + w):                                                                         # pinnacles at the corners
            sq(px - 1.5, px + 1.5, shaft + 1, shaft - 11, Z - 0.6, tri_sh(CSTONE, 3.2), obj)
        fx = x0 + w / 2                                                                                 # the finial: a knob, a cross
        sq(fx - 0.5, fx + 0.51, tip + 1, tip - 7, Z - 0.8, lambda x, y, s, t, z, wp: CSTONE[6], obj)
        sq(fx - 2, fx + 2.01, tip - 4, tip - 5, Z - 0.8, lambda x, y, s, t, z, wp: CSTONE[6], obj)
        city.disc(X_at(fx, Z), Y_at(tip + 1, Z), Z - 0.9, 0.9, lambda x, y, s, t, z, wp: CSTONE[5], obj)
    def gable(x, y, s, t, z, wp):                                                                       # the gable, the rose window
        half = 0.5 * (1 - t * 0.85)
        if abs(s - 0.5) > half: return None
        rx, ry = cx, CB - 116
        dr = math.hypot(x + 0.5 - rx, y + 0.5 - ry) / 8.0
        if dr < 1:
            if dr > 0.8: return CSTONE[5]
            a = math.atan2(y + 0.5 - ry, x + 0.5 - rx)
            if dr < 0.22: return CSTONE[4]
            if (a * 8 / math.pi) % 1 < 0.25: return CSTONE[3]                                          # tracery
            return [RUSTY[3], (70, 52, 96), RUSTY[2], (54, 70, 110)][int((a + math.pi) / (math.pi / 4)) % 4]
        return gothic_sh(77, 0.0, wins=False)(x, y, s, t, z, wp)
    sq(cx - 11, cx + 11, CB - 90, CB - 146, Z + 0.5, gable, obj)
    def door(x, y, s, t, z, wp):                                                                        # the arched door, lit
        dxp = abs(x + 0.5 - cx)
        top = CB - 29 + (dxp / 6.0) ** 2 * 7
        if y + 0.5 < top: return None
        if y + 0.5 < top + 1.2 or dxp > 5.2: return CSTONE[5]
        return GLOW[3] if (dxp < 2 and y > CB - 17) else GLOW[2]
    sq(cx - 7, cx + 7, CB, CB - 31, Z - 0.5, door, obj, cls='emit')
    for (a, b_, h_) in ((cx - 36, cx - 27, CB - 88), (cx + 36, cx + 27, CB - 86)):                      # buttress arches
        P0 = (X_at(a, Z - 1), Y_at(h_ + 10, Z - 1), Z - 1); P1 = (X_at(b_, Z - 1), Y_at(h_ - 8, Z - 1), Z - 1)
        city.line3(P0, P1, flat(CSTONE[3]), w=1.6, sag=-4.0, cls='front')
cathedral()

MOUNDC = {}
def mound():
    """turf and moss on the crest with bushes and small trees rooted in it, cut scarps showing the soil strata and
    the torn street (asphalt, setts, a kerb) with roots hanging out of them, rubble and scree down the slopes, paving
    slabs and kerbstones heaved up on end, two houses at its foot tilted and half swallowed, a leaning street lamp,
    the cathedral's stair down to the city"""
    obj = city.obj(); FOGK[obj] = 0.35
    mr = random.Random(521)
    def put(x, y, c, z=284.0):
        if 0 <= x < W and 0 <= y < H:
            MOUNDC[(x, y)] = c
            city.put(x, y, z, lambda x_, y_, a, b, zz, wp: MOUNDC[(x_, y_)], obj, 0, 0,
                     (X_at(x + 0.5, 300.0), Y_at(y + 0.5, 300.0), 300.0), None, 'egg')
    # the houses at its foot, tilted by the heave (drawn first: the rubble swallows their lower part)
    for (bx, by, w, h, ang, seed) in ((104, 456, 30, 42, -0.26, 1), (440, 458, 28, 38, 0.22, 2), (146, 462, 18, 24, -0.12, 3)):
        ca, sa = math.cos(ang), math.sin(ang)
        for y in range(int(by - h - w), int(by + 4)):
            for x in range(int(bx - w - h * 0.5), int(bx + w + h * 0.5)):
                dx, dy = x + 0.5 - bx, y + 0.5 - by
                lu, lv = dx * ca + dy * sa, -dx * sa + dy * ca                       # into the house's own frame
                if not (-w / 2 <= lu <= w / 2 and -h <= lv <= 0): continue
                fu, fv = (lu + w / 2), (-lv)
                v = 3.6 + (wn(0, fu * 0.3 + seed * 9, fv * 0.3) - 0.5) * 1.2 - (1.0 if fu > w - 6 else 0)
                c = tone(CPALE if seed != 2 else CWARM, v, x, y)
                if fv > h - 3: c = tone(CSTONE, 2.0, x, y)                                          # the cornice
                elif 4 < fu < w - 3 and (fu % 6) < 3 and 4 < (fv % 7) < 6.5 and fv < h - 5:
                    c = CSTONE[0] if h32(int(fu // 6), int(fv // 7), seed) % 4 else GLOW[0]           # windows, one lamp left on
                put(x, y, c, 286.0)
    # the mound itself: heaped scree and soil shaded as one big form (lit on its left flank), a few cut scarps near the
    # crest showing the strata and the torn street, moss creeping down, larger blocks lying about
    for x in range(MOUND[0], MOUND[1] + 1):
        top = mound_top(x)
        slope = (mound_top(x + 3) - mound_top(x - 3)) / 6.0                              # >0 = falling to the right
        scarp = clamp((wn(2, x * 0.06 + 13, 4.0) - 0.56) * 5) * clamp(1 - abs(x - 272) / 150)
        turf = 2 + int(3 * wn(1, x * 0.5, 9.0))
        sdepth = int(5 + 9 * scarp)
        for y in range(int(top), 464):
            d = y - top
            lit = clamp(-slope * 1.2 + 0.5) * 1.4 - d * 0.035                            # left flank faces the light
            if d < turf:                                                                     # turf on the crest
                c = tone(VINE, 2.8 - d * 0.6 + lit * 0.6 + (wn(3, x * 0.9, y * 0.9) - 0.5) * 1.8 + (0.9 if d < 1 else 0), x, y)
            elif scarp > 0.25 and d < turf + sdepth:                                       # a scarp: the strata
                q = d - turf + 1.2 * math.sin(x * 0.11 + 2) + (wn(0, x * 0.3, 5.0) - 0.5) * 2
                band_ = int(q // 2.5) % 5
                v = 2.4 + lit * 0.5
                c = [tone(SOIL, v + 0.6, x, y), tone(OCHRE, v + 0.2, x, y), tone(CSTONE, v + 1.6, x, y),
                     CSTONE[1] if (x + int(q)) % 3 else CSTONE[3], tone(SOIL, v - 0.4, x, y)][band_]
                if q < 0.8: c = tone(SOIL, 1.2, x, y)                                       # the overhang's shadow
            else:
                f1 = wn(1, x * 0.12, y * 0.16); f2 = wn(0, x * 0.5, y * 0.5)
                v = 2.2 + lit + (f1 - 0.5) * 1.6 + (f2 - 0.5) * 0.9
                c = tone(SOIL if f1 > 0.52 else CSTONE, v, x, y)
                if h32(x, y, 62) % 11 == 0: c = tone(CPALE, v + 1.4, x, y)                     # grit catching the light
                elif h32(x, y, 63) % 23 == 0: c = tone(CWARM, v + 0.6, x, y)                  # brick crumbs
                if wn(3, x * 0.16 + 40, y * 0.22) > 0.62 - 0.35 * clamp((top + 22 - y) / 22):
                    c = tone(VINE, 1.8 + lit * 0.6 + (wn(1, x * 1.2, y * 1.2) - 0.5) * 2.2, x, y)   # moss creeping down
            c = mix(c, (8, 10, 9), 0.4 * clamp((y - 432) / 30.0))                              # its foot in the gloom
            put(x, y, c)
        if scarp > 0.35 and h32(x, 63) % 4 == 0:                                         # roots hanging out of the scarps
            ln = 3 + h32(x, 64) % 9; rx = x
            for i in range(ln):
                rx += (h32(x, i, 65) % 3) - 1
                put(rx, int(top + turf + i), SOIL[0] if i % 3 else SOIL[2], 283.5)
    # blocks of broken street and foundations lying on the slopes: lit tops, dark undersides, a shadow below
    for k in range(34):
        x0 = mr.uniform(MOUND[0] + 6, MOUND[1] - 6)
        if abs(x0 - 272) < 26: continue
        y0 = mr.uniform(mound_top(x0) + 6, 452)
        rw, rh = mr.uniform(2.5, 6.5), mr.uniform(1.6, 3.5)
        pal = CPALE if k % 3 == 0 else CSTONE
        for y in range(int(y0 - rh - 1), int(y0 + rh + 3)):
            for x in range(int(x0 - rw - 1), int(x0 + rw + 2)):
                e = ((x + 0.5 - x0) / rw) ** 2 + ((y + 0.5 - y0) / rh) ** 2 + (wn(0, x * 0.9 + k, y * 0.9) - 0.5) * 0.5
                if e < 1:
                    v = 4.2 - (y + 0.5 - y0) / rh * 1.4 - (x + 0.5 - x0) / rw * 0.5
                    put(x, y, mix(tone(pal, v, x, y), (8, 10, 9), 0.4 * clamp((y - 432) / 30.0)), 283.6)
                elif e < 1.6 and y > y0 + rh * 0.4:
                    MOUNDC[(x, y)] = mix(MOUNDC.get((x, y), SOIL[1]), (8, 10, 9), 0.4)          # its shadow on the slope
    # contact shadow along the shells' foot (the crest meets the shell there)
    # paving slabs and kerbstones heaved up on end, sticking out of the crest
    for k in range(16):
        x0 = mr.uniform(MOUND[0] + 8, MOUND[1] - 8)
        if abs(x0 - 272) < 34: continue
        y0 = mound_top(x0) + mr.uniform(-1, 4)
        ang = mr.choice((-1, 1)) * mr.uniform(0.35, 1.25)
        L_, T_ = mr.uniform(7, 16), mr.uniform(2.5, 4.5)
        ca, sa = math.cos(ang), math.sin(ang)
        for y in range(int(y0 - L_ - 2), int(y0 + 4)):
            for x in range(int(x0 - L_), int(x0 + L_) + 1):
                dx, dy = x + 0.5 - x0, y + 0.5 - y0
                lu, lv = dx * ca + dy * sa, -dx * sa + dy * ca
                if not (0 <= -lv <= L_ and -T_ / 2 <= lu <= T_ / 2): continue
                if y > mound_top(x) + 3: continue
                edge = lu > T_ / 2 - 1.2
                c = tone(CPALE if k % 3 else CSTONE, (5.0 if not edge else 2.4) - (-lv) / L_ * 0.8 + (wn(0, x, y) - 0.5), x, y)
                if (-lv) < 1.5: c = tone(SOIL, 2.0, x, y)
                put(x, y, c, 283.0)
    # big plates of the old ground's crust (asphalt, paving) broken and tilted outward round the shells' foot
    for (x0, L_, T_, ang) in ((150, 26, 6, -0.62), (178, 30, 6, -0.45), (214, 22, 5, -0.3), (334, 22, 5, 0.32), (366, 30, 6, 0.5), (402, 24, 5, 0.7)):
        y0 = mound_top(x0) + 3
        ca, sa = math.cos(ang), math.sin(ang)
        for y in range(int(y0 - L_ - 3), int(y0 + 6)):
            for x in range(int(x0 - L_ - 3), int(x0 + L_ + 4)):
                dx, dy = x + 0.5 - x0, y + 0.5 - y0
                lu, lv = dx * ca + dy * sa, -dx * sa + dy * ca                         # lv up the plate, lu across it
                if not (0 <= -lv <= L_ and -T_ / 2 <= lu <= T_ / 2): continue
                if -lv > L_ - 2.5 + 2.5 * wn(0, lu * 0.8 + x0, 1.0): continue          # a broken top edge
                face = lu < -T_ / 2 + 1.6 if ang > 0 else lu > T_ / 2 - 1.6           # the edge turned to us: its section
                if face: c = tone(SOIL if (-lv) % 4 < 2 else CSTONE, 2.0, x, y)
                else:
                    c = tone(CSTONE if x0 % 2 else CPALE, 4.6 - (-lv) / L_ * 1.2 + (wn(1, x * 0.8, y * 0.8) - 0.5) * 1.0, x, y)
                    if h32(int(-lv) // 5, int(x0), 69) % 4 == 0 and abs(lu) < 0.6: c = tone(CPALE, 6.2, x, y)   # a painted road line
                    if wn(3, x * 0.5, y * 0.5) > 0.66: c = tone(VINE, 2.4, x, y)
                put(x, y, c, 282.9)
            # its shadow on the slope below
    # small trees and bushes rooted on the crest
    for k in range(13):
        x0 = mr.uniform(MOUND[0] + 6, MOUND[1] - 6)
        if abs(x0 - 272) < 40: continue
        y0 = mound_top(x0) + 1
        tree = k % 2 == 0
        lean = mr.uniform(-0.35, 0.35)
        th = mr.uniform(8, 16) if tree else 0
        for i in range(int(th)):
            put(int(x0 + lean * i), int(y0 - i), SOIL[1] if i % 4 else SOIL[3], 282.5)
        cxr, cyr = x0 + lean * th, y0 - th - (2 if tree else 0)
        r = mr.uniform(4.5, 8) if tree else mr.uniform(2.5, 4.5)
        for y in range(int(cyr - r - 2), int(cyr + r + 2)):
            for x in range(int(cxr - r - 2), int(cxr + r + 2)):
                dd = math.hypot((x + 0.5 - cxr) / r, (y + 0.5 - cyr) / (r * 0.85)) + (wn(3, x * 0.9 + k, y * 0.9) - 0.5) * 0.5
                if dd > 1: continue
                lit = (cxr - x) * 0.35 + (cyr - y) * 0.45
                c = tone(VINE, 2.8 + lit * 0.5 / max(1, r * 0.25) - dd * 1.2 + (h32(x, y, 66) % 4 == 0) * 1.0, x, y)
                put(x, y, c, 282.0)
    # a street lamp left leaning where the street tore
    for i in range(30):
        put(int(414 + i * 0.33), int(440 - i), CSTONE[1], 282.8)
    put(424, 409, CSTONE[2], 282.7); put(425, 409, CSTONE[1], 282.7); put(424, 410, GLOW[0], 282.7)
    # the cathedral's stair down the mound: worn treads, dark risers, low walls either side, moss in the corners
    cx = EGG_SX
    for y in range(CB, 462):
        half = 9 + (y - CB) * 0.22
        step = (y - CB) % 4
        for x in range(int(cx - half - 3), int(cx + half + 4)):
            dx = x + 0.5 - cx
            if abs(dx) > half + 2.5: continue
            if abs(dx) > half:                                                        # the side walls
                c = tone(CSTONE, 4.4 if abs(dx) < half + 1.2 else 2.6, x, y)
            else:
                c = tone(CPALE, 4.6 if step == 0 else (2.2 if step == 3 else 3.2), x, y)
                if step == 0 and h32(x, y, 67) % 6 == 0: c = tone(CPALE, 3.0, x, y)      # chipped treads
                if abs(dx) > half - 2 and wn(3, x * 0.8, y * 0.8) > 0.5: c = tone(VINE, 2.4, x, y)
                g = math.exp(-((y - CB) / 9.0)) * clamp(1 - abs(dx) / 9.0)
                if g > 0.05: c = mix(c, GLOW[2], g * 0.35)                               # the door's light on the top treads
            c = mix(c, (8, 10, 9), 0.35 * clamp((y - 440) / 24.0))
            put(x, y, c, 283.2)
mound()

# ---- places the player will visit, small but recognisable (consistent with their own scenes and the map); unlabelled
def sxz(sx, Z): return X_at(sx, Z)
def base_y(Z): return HY + F * (CAMH - YG) / Z          # where the city's ground lies at depth Z (screen y)
METALR = ramp('#2a3a3c #35494b #41585a #4e6769 #5c7677 #6f8b89 #86a19e')
LIME = ramp('#3e3f33 #514f40 #66634f #7c7860 #938e73 #aaa487 #c0b99b')
BRASS = ramp('#3a2c14 #5a4420 #7e612c #a2803a #c09c4e')

def voxmarket():
    """Voxmarket: three zeppelin hangars side by side, pale stucco gable ends with a radial glazed arch glowing warm,
    long barrel roofs of blue-grey sheet metal (one patched with rusty sheets) running back toward the vanishing point"""
    obj = city.obj(); FOGK[obj] = 0.75
    Z0 = 650.0
    for (sx, length, roof, seed) in ((686, 320, METALR, 1), (727, 280, RUSTY, 2), (768, 360, METALR, 3)):
        X = sxz(sx, Z0); R = 17.5 * Z0 / F; y0 = YG + 7
        N_ = 14
        for i in range(N_):                                                        # the barrel roof, strip by strip
            a0, a1 = math.pi * i / N_, math.pi * (i + 1) / N_
            P0 = (X + R * math.cos(a0), y0 + R * math.sin(a0), Z0); P1 = (X + R * math.cos(a1), y0 + R * math.sin(a1), Z0)
            P3 = (P0[0], P0[1], Z0 + length)
            lit = 0.5 + 0.5 * math.sin((a0 + a1) / 2) - 0.25 * math.cos((a0 + a1) / 2)
            def rsh(x, y, s, t, z, wp, lit=lit, roof=roof, seed=seed):
                v = 1.6 + lit * 3.2 + (wn(1, wp[2] * 0.08 + seed, wp[0] * 0.1) - 0.5) * 1.0
                if (wp[2] / 9.0) % 1 < 0.14: v -= 0.9                              # the ribs over the vault
                r_ = roof
                if roof is METALR and wn(2, wp[2] * 0.05 + seed * 3, wp[0] * 0.05) > 0.66: r_ = RUSTY
                return tone(r_, v, x, y)
            city.quad(P0, P1, P3, rsh, obj, cls='top')
        for side in (-1, 1):                                                       # the low side walls under the vault
            city.quad((X + side * R, YG, Z0), (X + side * R, YG, Z0 + length), (X + side * R, y0, Z0),
                      lambda x, y, s, t, z, wp: tone(LIME, 2.6 + (1.0 if int(wp[2] / 14) % 2 else 0), x, y), obj, cls='side')
        def gable(x, y, s, t, z, wp, X=X, R=R, y0=y0):
            dx, dy = wp[0] - X, wp[1] - y0
            rr = math.hypot(dx, dy)
            if dy > 0 and rr > R * 1.04: return None
            if abs(dx) > R * 1.04: return None
            if dy > 0 and rr > R * 0.95: return tone(LIME, 5.6, x, y)             # the impost cornice round the arch
            if dy > 0 and rr < R * 0.72:                                           # the radial glazed arch, lit warm
                ang = math.atan2(dy, dx)
                if rr > R * 0.66 or (ang * 9 / math.pi) % 1 < 0.16: return tone(LIME, 4.2, x, y)
                return GLOW[1] if h32(int(ang * 9), int(rr), 3) % 4 else GLOW[2]
            if dy <= 0 and abs(dx) < R * 0.3: return CSTONE[1] if dy < -1.2 else tone(LIME, 4.0, x, y)   # the doorway
            return tone(LIME, 4.6 + (wn(0, wp[0] * 0.3, wp[1] * 0.3) - 0.5) * 1.2 - (0.8 if abs(dx) > R * 0.85 else 0), x, y)
        city.quad((X - R * 1.05, YG, Z0 - 0.5), (X + R * 1.05, YG, Z0 - 0.5), (X - R * 1.05, y0 + R * 1.05, Z0 - 0.5), gable, obj, cut=True, cls='front')

def shed521():
    """Shed 521: the top-heavy timber tower, storeys overhanging upward, X braces, the pale sign plate, a cupola and a
    mast, the big rusty pipe up its flank with a plume, the low annex, the chain-link fence, district-heating pipes"""
    obj = city.obj(); FOGK[obj] = 0.45; MISTK[obj] = 0.5
    Z = 560.0; by = base_y(Z)
    def wood(x, y, s, t, z, wp, v0=3.4):
        v = v0 + (wn(0, x * 0.7, y * 0.2) - 0.5) * 1.4 - (0.8 if x % 3 == 0 else 0)
        return tone(WOOD, v, x, y)
    def storey(x0, x1, y_b, y_t, braces=True, z_=Z):
        def sh(x, y, s, t, z, wp):
            c = wood(x, y, s, t, z, wp)
            if braces and (abs((x - x0) - (y_b - y) * (x1 - x0) / (y_b - y_t)) < 0.9 or abs((x1 - x) - (y_b - y) * (x1 - x0) / (y_b - y_t)) < 0.9):
                c = tone(WOOD, 1.4, x, y)
            if y == int(y_t) or y == int(y_t) + 1: c = tone(WOOD, 5.2 if y == int(y_t) else 1.2, x, y)
            return c
        sq(x0, x1, y_b, y_t, z_, sh, obj)
    cx = 838
    storey(cx - 13, cx + 13, by, by - 16, False)
    sq(cx - 6, cx + 6, by, by - 11, Z - 0.3, lambda x, y, s, t, z, wp: tone(WOOD, 0.8 + (0.6 if x % 3 == 0 else 0), x, y), obj)   # the gate
    storey(cx - 16, cx + 16, by - 16, by - 30, z_=Z - 1)
    storey(cx - 18, cx + 18, by - 30, by - 45, False, z_=Z - 2)
    sq(cx - 12, cx + 12, by - 34, by - 40, Z - 2.3, lambda x, y, s, t, z, wp: tone(LIME, 2.8 + (0.8 if h32(x, y, 9) % 3 == 0 else 0), x, y), obj)   # the sign plate
    storey(cx - 9, cx + 9, by - 45, by - 54, False, z_=Z - 1)                    # the cupola
    sq(cx - 11, cx + 11, by - 54, by - 56, Z - 1.2, lambda x, y, s, t, z, wp: tone(WOOD, 4.0, x, y), obj)
    sq(cx + 4, cx + 5.01, by - 56, by - 74, Z - 1, lambda x, y, s, t, z, wp: tone(WOOD, 1.6, x, y), obj)                   # the mast
    sq(cx + 19, cx + 22, by, by - 50, Z - 2.5, lambda x, y, s, t, z, wp: tone(RUSTY, 3.4 - (x - cx - 19) * 0.8 + (wn(1, y * 0.4, x) - 0.5) * 2, x, y), obj)   # the pipe
    storey(cx + 22, cx + 44, by, by - 10, False, z_=Z + 2)                       # the annex, a lit window
    sq(cx + 30, cx + 34, by - 4, by - 7, Z + 1.8, lambda x, y, s, t, z, wp: GLOW[1], obj, cls='emit')
    for k in range(2):                                                           # district-heating pipes on trestles
        yy = by - 9 - k * 3
        sq(cx - 70, cx - 13, yy + 2, yy, Z - 3 - k, lambda x, y, s, t, z, wp: tone(METALR, 4.8 if y % 2 else 3.4, x, y) if h32(x // 4, 7) % 5 else tone(RUSTY, 3.0, x, y), obj)
    for tx in range(int(cx - 66), int(cx - 13), 9): sq(tx, tx + 1.01, by, by - 9, Z - 3.5, lambda x, y, s, t, z, wp: CSTONE[2], obj)
    def fence(x, y, s, t, z, wp):
        if (x + y) % 3 == 0 or (x - y) % 3 == 0 or y == int(by - 6): return tone(CSTONE, 3.0, x, y)
        return None
    sq(cx - 44, cx + 50, by + 1, by - 6, Z - 6, fence, obj)
    PLUMES.append((cx + 20.5, by - 50, Z, 1.3, 'steam'))

def lumen():
    """the Lumen Directorate: a pale limestone house with pointed windows and twin spires, green copper at their tips,
    its glasshouse alongside, gardens and trees at its foot (the growers' turf)"""
    obj = city.obj(); FOGK[obj] = 0.8
    Z = 950.0; by = int(base_y(Z)); cx = 446
    def lime(x, y, s, t, z, wp):
        v = 4.4 + (wn(0, x * 0.4, y * 0.4) - 0.5) * 1.0 - (0.9 if y % 4 == 0 else 0) * 0.5
        if (x - cx) % 6 in (2, 3) and (by - y) % 12 in range(3, 9): v = 1.4 if h32(x // 6, (by - y) // 12, 5) % 7 else 0
        return tone(LIME, v, x, y) if v > 0 else GLOW[1]
    sq(cx - 22, cx + 22, by, by - 40, Z, lime, obj)
    sq(cx - 24, cx + 24, by - 40, by - 43, Z - 0.5, lambda x, y, s, t, z, wp: tone(LIME, 5.4 if y == int(by - 43) else 3.0, x, y), obj)
    for tx in (cx - 18, cx + 10):
        sq(tx, tx + 8, by - 30, by - 62, Z - 1, lime, obj)
        sq(tx - 0.5, tx + 8.5, by - 62, by - 92, Z - 1.2, lambda x, y, s, t, z, wp: (tone(COPPER if t > 0.55 else LIME, (3.4 if s < 0.5 else 2.0) + (1 if t > 0.55 else 0), x, y) if abs(s - 0.5) <= 0.5 * (1 - t) else None), obj)
    sq(cx - 6, cx + 6, by - 43, by - 58, Z - 0.6, tri_sh(LIME, 3.6), obj)                          # the gable between
    def glass(x, y, s, t, z, wp):
        dx = (x + 0.5 - (cx + 36)) / 12.0; dy = (by - y) / 14.0
        if dx * dx + max(0.0, dy - 0.3) ** 2 / 0.5 > 1: return None
        if x % 3 == 0 or y % 3 == 0: return tone(CSTONE, 4.4, x, y)
        return tone(METALR, 5.2 - dy * 1.6 + (0.8 if dx < -0.2 else 0), x, y)                    # glass with the sky in it
    sq(cx + 23, cx + 49, by, by - 22, Z + 1, glass, obj)
    for k in range(10):                                                                          # the gardens' trees
        tx = cx - 34 + k * 8 + (h32(k, 71) % 5); r_ = 3 + h32(k, 72) % 3
        city.disc(sxz(tx, Z - 6), YG + r_ * Z / F * 1.2, Z - 6, r_ * Z / F,
                  lambda x, y, s_, t_, z, wp, k=k: tone(VINE if k % 4 else LEAFR, 3.8 - s_ * 1.2 - t_ * 1.4, x, y), obj, cls='front')

def townhall():
    """the Townhall: a long civic front, a drum with the Stomach Clock's pale face, a green copper dome and lantern"""
    obj = city.obj(); FOGK[obj] = 0.85
    Z = 1150.0; by = int(base_y(Z)); cx = 628
    def front(x, y, s, t, z, wp):
        v = 3.6 + (wn(0, x * 0.4, y * 0.4) - 0.5) * 0.8
        if (x - cx) % 4 == 0 and (by - y) % 7 in (2, 3, 4): v = 1.4
        if y == int(by - 22): v = 5.0
        return tone(CPALE, v, x, y)
    sq(cx - 26, cx + 26, by, by - 22, Z, front, obj)
    sq(cx - 9, cx + 9, by - 22, by - 34, Z - 1, front, obj)
    def clock(x, y, s, t, z, wp):
        d = math.hypot(x + 0.5 - cx, y + 0.5 - (by - 28))
        if d > 4.2: return None
        return BRASS[3] if d > 3.3 else ((80, 60, 50) if (abs(x + 0.5 - cx) < 0.6 and y < by - 28) or (abs(y + 0.5 - (by - 28)) < 0.6 and x > cx) else (196, 186, 160))
    sq(cx - 5, cx + 5, by - 23, by - 33, Z - 1.5, clock, obj)
    def dome(x, y, s, t, z, wp):
        dx = (x + 0.5 - cx) / 11.0; dy = (by - 34 - (y + 0.5)) / 11.0
        if dx * dx + dy * dy > 1 or dy < 0: return None
        return tone(COPPER, 2.4 - dx * 1.4 + dy * 0.8 + (-0.6 if (dx * 5) % 1 < 0.2 else 0), x, y)
    sq(cx - 11, cx + 11, by - 34, by - 46, Z - 1, dome, obj)
    sq(cx - 1.5, cx + 1.5, by - 45, by - 51, Z - 1.2, lambda x, y, s, t, z, wp: tone(COPPER, 3.0, x, y), obj)
    sq(cx - 0.5, cx + 0.51, by - 51, by - 56, Z - 1.2, lambda x, y, s, t, z, wp: CSTONE[2], obj)
    for tx in (cx - 26, cx + 22):
        sq(tx, tx + 4, by - 22, by - 30, Z - 0.5, front, obj)

def harbour():
    """the sea on the far right horizon, the harbour's quays and cranes at the waterline, the Echo Drain's derricks
    with their brass gramophone horns out in the water, Redmass Island a red hump on the horizon, a few boats"""
    obj = city.obj(); FOGK[obj] = 0.45
    def sea(x, y, s, t, z, wp):
        sx = CX + F * wp[0] / wp[2]
        if wp[2] < coast_z(sx): return None
        ym = max(0, int(2 * HY - y - 4))
        c = mix(mix(HAZE_ROW[ym], SKYB[ym][x], 0.5), (34, 50, 50), 0.55)
        hz_ = clamp(1 - (y - HY) / 9.0)
        c = mix(c, GLOWR[5], 0.55 * hz_)                                                       # the glow mirrored at the horizon
        if (y + int(wn(1, wp[0] * 0.01, 3) * 3)) % 3 == 0 and h32(x // 5, y, 81) % 3: c = mix(c, (40, 54, 50), 0.35)   # swell
        if h32(x, y, 82) % 37 == 0: c = mix(c, (210, 220, 170), 0.6)                           # glints of the glow
        return c
    city.quad((-2000, YG + 0.5, 900), (400000, YG + 0.5, 900), (-2000, YG + 0.5, 40000), sea, obj, cut=True, cls='sea')
    MISTK[obj] = 0.0
    # quays and warehouses along the waterline, cranes over them
    for k in range(9):
        sx = 880 + k * 22 + (h32(k, 83) % 9)
        Zq = coast_z(sx) - 60
        if Zq < 900: continue
        bx = sxz(sx, Zq)
        w_ = 22 * Zq / F * 0.06 + 14
        b = dict(mat=CSTONE if k % 2 else CWARM, seed=600 + k, v0=3.0, fl=10.5, bay=8.0, ww=0.4, lit=3, u0=bx - w_, y1=YG + 18 + (k % 3) * 8,
                 vines=0.1, vlen=6, prof=None, style='grid')
        cbox(bx - w_, bx + w_, YG, b['y1'], Zq, Zq + 40, wall_sh(b, 'front'), wall_sh(b, 'side'), roof_sh(b), obj=obj)
    for (sx, h_, jib, side) in ((912, 170, 100, 1), (955, 180, 110, -1), (996, 175, 115, 1), (1040, 160, 95, -1)):
        Zc = coast_z(sx) - 90
        X = sxz(sx, Zc)
        top = YG + h_
        city.line3((X - 4, YG, Zc), (X - 1, top, Zc), flat(CSTONE[2]), w=1.6, cls='front')
        city.line3((X + 4, YG, Zc), (X + 1, top, Zc), flat(CSTONE[2]), w=1.6, cls='front')
        for k in range(5):
            ya, yb = YG + h_ * k / 5, YG + h_ * (k + 1) / 5
            city.line3((X - 3.5 + k * 0.5, ya, Zc), (X + 3.5 - k * 0.5, yb, Zc), flat(CSTONE[2]), w=0.9, cls='front')
        city.line3((X, top, Zc), (X + side * jib, top - 8, Zc), flat(CSTONE[2]), w=1.6, cls='front')            # the jib
        city.line3((X - side * 18, top, Zc), (X, top + 22, Zc), flat(CSTONE[2]), w=1.0, cls='front')
        city.line3((X, top + 22, Zc), (X + side * jib, top - 8, Zc), flat(CSTONE[1]), w=0.6, cls='front')       # its stay
        city.line3((X + side * jib * 0.8, top - 7, Zc), (X + side * jib * 0.8, top - 60, Zc), flat(CSTONE[1]), w=0.5, cls='front')   # the hook's line
        city.box(X - side * 22 - 7, X - side * 22 + 7, top - 6, top + 4, Zc, Zc + 10, tone_sh(CSTONE, 2.4), tone_sh(CSTONE, 1.6), obj=obj, cls='front')  # counterweight
    # the Echo Drain: derricks out in the water, each crowned with a brass gramophone horn
    for (sx, Zd, h_, fl_) in ((968, 3300, 250, 1), (1012, 2450, 215, -1)):
        X = sxz(sx, Zd)
        for dx_ in (-9, 9):
            city.line3((X + dx_, YG, Zd), (X, YG + h_, Zd), flat(CSTONE[2]), w=3.0, cls='front')
        for k in range(1, 5):
            yk = YG + h_ * k / 5; hw = 9 * (1 - k / 5)
            city.line3((X - hw, yk, Zd), (X + hw, yk, Zd), flat(CSTONE[2]), w=2.0, cls='front')
        hx_, hy_ = X, YG + h_
        def horn(x, y, s, t, z, wp, fl_=fl_):
            u = s if fl_ > 0 else 1 - s                                           # 0 at the throat, 1 at the bell
            r = 0.12 + 0.88 * u ** 2.2
            if abs(t - 0.5) > r / 2: return None
            return tone(BRASS, 1.6 + u * 2.6 + (1.0 if t < 0.5 else 0), x, y)
        city.quad((hx_ - (0 if fl_ > 0 else 95), hy_ - 40, Zd - 5), (hx_ + (95 if fl_ > 0 else 0), hy_ - 40, Zd - 5), (hx_ - (0 if fl_ > 0 else 95), hy_ + 45, Zd - 5), horn, obj, cut=True, cls='front')
    def island(x, y, s, t, z, wp):
        if abs(s - 0.5) * 2 > 1 - t ** 1.5: return None
        return tone(RUSTY, 2.4 + (1.0 if s < 0.45 else 0) + t, x, y)
    Zi = 7500.0
    city.quad((sxz(1026, Zi), YG, Zi), (sxz(1062, Zi), YG, Zi), (sxz(1026, Zi), YG + 160, Zi), island, obj, cut=True, cls='front')
    for (sx, Zb) in ((925, 4300), (1046, 1700), (985, 5600)):                    # boats
        X = sxz(sx, Zb)
        city.box(X - 8, X + 8, YG, YG + 5, Zb, Zb + 20, tone_sh(CSTONE, 1.4), tone_sh(CSTONE, 1.0), tone_sh(CWARM, 2.4), obj=obj, cls='front')

PLUMES = []
voxmarket(); shed521(); lumen(); townhall(); harbour()

# ---- city life: chimney stacks (their plumes are drawn over the backdrop), cables and skybridges strung between the
#      tall towers, a rail viaduct across the middle distance with a train on it
def city_life():
    obj = city.obj(); FOGK[obj] = 1.0
    used = []
    for (X, y1, Z, seed) in CHIMNEYS:
        sx = CX + F * X / Z
        if any(abs(sx - u) < 34 for u in used) or 480 < sx < 600: continue
        used.append(sx)
        cbox(X - 1.6, X + 1.6, y1, y1 + 9, Z + 2, Z + 5, tone_sh(CWARM, 2.6), tone_sh(CWARM, 1.6), obj=obj)
        PLUMES.append((sx, HY + F * (CAMH - y1 - 9) / Z, Z, 0.7 + 0.9 * min(1.0, 900 / Z), 'smoke' if seed % 3 == 0 else 'steam'))
        if len(used) >= 12: break
    tops = sorted(TOPS, key=lambda t: CX + F * t[0] / t[2])
    n = 0
    for (a, b) in zip(tops, tops[1:]):
        sa, sb = CX + F * a[0] / a[2], CX + F * b[0] / b[2]
        if not (8 < sb - sa < 75) or max(a[2], b[2]) / min(a[2], b[2]) > 1.35: continue
        if any(lo < (sa + sb) / 2 < hi for (lo, hi) in ((140, 410), (480, 600))): continue
        ya, yb_ = min(a[1], b[1]) - 14, min(a[1], b[1]) - 30
        city.line3((a[0] + a[3] / 2, ya, a[2]), (b[0] - b[3] / 2, yb_, b[2]), flat(CSTONE[1]), w=0.9, sag=14.0, cls='front')
        if n % 3 == 1:                                                                  # a skybridge
            yy = min(a[1], b[1]) * 0.55 + YG * 0.45
            city.quad((a[0] + a[3] / 2, yy, a[2]), (b[0] - b[3] / 2, yy, b[2]), (a[0] + a[3] / 2, yy + 5, a[2]),
                      lambda x, y, s, t, z, wp: tone(CSTONE, 3.6 if t > 0.7 else 2.2, x, y) if (x % 4 or t > 0.7) else GLOW[0], obj, cls='front')
        n += 1
        if n >= 14: break
    # the viaduct: from behind Voxmarket off toward the harbour, arches into the mist, a train of three cars on it
    A_, B_ = (X_at(668, 760), 760.0), (X_at(960, 1120), 1120.0)
    YD = -96.0
    L_ = math.hypot(B_[0] - A_[0], B_[1] - A_[1])
    def arches(x, y, s, t, z, wp):
        d = s * L_; span = 26.0
        k = math.floor(d / span); fu = d / span - k
        Y = wp[1]
        if Y > YD - 3.5:                                                                # the deck's fascia
            return tone(CSTONE, 4.4 if Y > YD - 1.2 else 2.6, x, y)
        if abs(fu - 0.5) < 0.38:
            ay = YD - 3.5 - span * 0.42 * math.sqrt(max(0.0, 1 - ((fu - 0.5) / 0.38) ** 2))
            if Y < ay: return None
        hv = vine_hang(d, Y, YD - 3.5, 77, 0.6, 30, z)
        if hv: return tone(VINE, 3.6 - (hv - 1) * 2, x, y)
        return tone(CPALE, 3.0 + (1.0 if fu < 0.12 else 0) + (wn(0, d * 0.2, Y * 0.2) - 0.5) * 0.9, x, y)
    city.quad((A_[0], YG, A_[1]), (B_[0], YG, B_[1]), (A_[0], YD, A_[1]), arches, obj, cut=True, cls='front')
    city.quad((A_[0], YD, A_[1]), (B_[0], YD, B_[1]), (A_[0], YD, A_[1] + 6), lambda x, y, s, t, z, wp: tone(CSTONE, 3.4 if (s * L_ / 3) % 1 > 0.25 else 2.0, x, y), obj, cls='top')
    for k in range(3):                                                                  # the train
        s0, s1 = 0.30 + k * 0.045, 0.30 + k * 0.045 + 0.04
        Pa = (A_[0] + (B_[0] - A_[0]) * s0, A_[1] + (B_[1] - A_[1]) * s0); Pb = (A_[0] + (B_[0] - A_[0]) * s1, A_[1] + (B_[1] - A_[1]) * s1)
        city.quad((Pa[0], YD, Pa[1] - 0.5), (Pb[0], YD, Pb[1] - 0.5), (Pa[0], YD + 7, Pa[1] - 0.5),
                  lambda x, y, s, t, z, wp: (GLOW[1] if 0.35 < t < 0.65 and (s * 6) % 1 < 0.5 else tone(COPPER, 1.6 + t * 1.8, x, y)), obj, cls='front')
city_life()


# ---------------------------------------------------------------------------------------------------- 3. the backdrop
def aerial(c, z, y, Y, obj, X=0.0):
    """distance haze toward the air colour of the row (the green glow near the horizon) + a low green mist the city
    stands in"""
    k = FOGK.get(obj, 1.0)
    f = 0.86 * (1 - math.exp(-max(0.0, z - 150) / 2200.0)) * k
    m = clamp((-100 - Y) / 95.0) ** 1.1 * clamp((z - 180) / 420.0) * (0.55 + 0.45 * k) * MISTK.get(obj, 1.0)
    m *= 0.7 + 0.6 * wn(2, X * 0.004 + 40, z * 0.004)
    hz = HAZE_ROW[y]
    c = tuple(c[i] + (hz[i] - c[i]) * f for i in range(3))
    mc = mix(hz, MIST, 0.55)
    return tuple(int(c[i] + (mc[i] - c[i]) * min(1.0, m) * 0.9) for i in range(3))

print('backdrop...')
BD = [[None] * W for _ in range(H)]
BZ = [[INF] * W for _ in range(H)]
for y in range(H):
    for x in range(W):
        g = city.G[y][x]
        if g is None: BD[y][x] = SKYB[y][x]; continue
        shader, obj, a, b, wp, cl = g
        z = city.ZB[y][x]
        c = shader(x, y, a, b, z, wp)
        if c is None: BD[y][x] = SKYB[y][x]; continue
        Yw = wp[1] if wp is not None else CAMH - (y + 0.5 - HY) * z / F
        Xw = wp[0] if wp is not None else (x + 0.5 - CX) * z / F
        if cl != 'emit': c = aerial(c, z, y, Yw, obj, Xw)
        BD[y][x] = c; BZ[y][x] = z
# silhouettes: the sky catches the top edge of near things; a faint dark line where a nearer building cuts a farther one
OUT_BD = [row[:] for row in BD]
for y in range(1, H - 1):
    for x in range(1, W - 1):
        z = BZ[y][x]
        if z >= INF: continue
        za = BZ[y - 1][x]
        if za > z * 1.25 and z < 3000:
            OUT_BD[y][x] = mix(BD[y][x], HAZE_ROW[y], 0.28 * clamp((3000 - z) / 2000))
        for (nx_, ny_) in ((x + 1, y), (x - 1, y), (x, y + 1)):
            zn = BZ[ny_][nx_]
            if zn < z * 0.8 and zn < 1200:
                OUT_BD[y][x] = mix(OUT_BD[y][x], (14, 20, 18), 0.2 * clamp((1200 - zn) / 800)); break
BD = OUT_BD

# ---- god rays: daylight breaking through the cloud break and falling across the city beyond the Scraper (only on the
#      air and on what lies farther off than the tower; the green glow keeps rising from the mist under them)
RAY_SRC = (735.0, -190.0)
BEAMS = [(575, 0.020, 0.11), (655, 0.030, 0.15), (792, 0.017, 0.10), (888, 0.034, 0.16), (985, 0.022, 0.10)]
BEAMS = [(math.atan2(tx - RAY_SRC[0], 330 - RAY_SRC[1]), hw, st) for (tx, hw, st) in BEAMS]
_rn = make_noise(7, 77, 1400, 1400)
for y in range(105, 456):
    fin = clamp((y - 105) / 110.0)
    for x in range(W):
        z = BZ[y][x]
        if z < 760: continue
        ang = math.atan2(x - RAY_SRC[0], y - RAY_SRC[1])
        k = 0.0
        for (ac, hw, st) in BEAMS:
            e = abs(ang - ac) / hw
            if e < 1: k += st * (1 - e * e)
        if k <= 0: continue
        k *= fin * (0.65 + 0.7 * _rn(ang * 1500 + 700, 9.0))
        if z < INF: k *= 1.6                                                     # where a beam lands, the city is sunlit
        BD[y][x] = mix(BD[y][x], (216, 222, 188), clamp(k))

# ---- smoke and steam plumes from the chimneys (and Shed 521's pipe), leaning away in the wind
for (sx, sy, Z, sc, kind) in PLUMES:
    Hh = int(40 * sc) + 8
    dens = {}
    for i in range(Hh):
        t = i / Hh
        cxp = sx + i * (0.35 + 1.3 * t) + 2.0 * math.sin(i * 0.2 + sx)
        cyp = sy - i * (1 - 0.35 * t)
        r = (1.0 + 10.0 * t ** 0.7) * sc
        for yy in range(int(cyp - r), int(cyp + r) + 1):
            for xx in range(int(cxp - r), int(cxp + r) + 1):
                d = math.hypot(xx + 0.5 - cxp, yy + 0.5 - cyp) / r
                if d < 1:
                    v = (1 - d) * (1 - t) ** 0.9
                    if v > dens.get((xx, yy), (0, 0))[0]: dens[(xx, yy)] = (v, yy + 0.5 - cyp)
    fz = 0.86 * (1 - math.exp(-max(0.0, Z - 150) / 2200.0))
    for (xx, yy), (dv, oy) in dens.items():
        if not (0 <= xx < W and 0 <= yy < H) or BZ[yy][xx] < Z: continue
        n = wn(3, xx * 0.35 + sx, yy * 0.35)
        a = clamp(dv * (0.4 + 1.0 * n) * 1.2) * (0.62 if kind == 'steam' else 0.5)
        base = (204, 208, 192) if kind == 'steam' else (64, 66, 58)
        lit = -oy * (6 if kind == 'steam' else 4)                                 # lit on top, shaded below
        c = tuple(max(0, min(255, int(base[i] + lit))) for i in range(3))
        BD[yy][xx] = mix(BD[yy][xx], mix(c, HAZE_ROW[yy], fz), a)

# ---- skyships (the Verdigrace's kind: a finned gasbag netted with vines, a hull slung under it) and birds
def skyship(cx, cy, L, flip=False, fade=0.4, seed=0):
    """L = length of the gasbag in pixels: a fat-nosed gasbag tapering to finned tail, netted, shaded from above,
    a boat hull slung under it on ropes; drawn straight into the backdrop and hazed by `fade`"""
    hb = L * 0.2
    hull_y, hull_h = cy + hb * 1.75, max(2.0, L * 0.075)
    def r_of(u):
        if u >= 1 or u <= -1.02: return 0.0
        r = math.sqrt(max(0.0, 1 - u * u))
        if u < 0: r *= 1 - 0.38 * (-u) ** 1.5
        return r
    for y in range(int(cy - hb * 2.2), int(hull_y + hull_h + 2)):
        for x in range(int(cx - L * 0.6), int(cx + L * 0.6) + 1):
            u = (x + 0.5 - cx) / (L / 2) * (-1 if flip else 1)          # +1 = the nose
            v = (y + 0.5 - cy) / hb
            c = None
            r = r_of(u)
            if abs(v) < r:
                nv = v / r
                val = 3.0 - nv * 1.7 - (0.6 if u < -0.4 else 0) + (0.5 if -0.2 < u < 0.6 and nv < -0.3 else 0)
                if L > 40 and (((u * 5.5 + nv * 1.3) % 1 < 0.09) or ((u * 5.5 - nv * 1.3) % 1 < 0.09)): val -= 0.9    # the vine netting
                c = tone(VINE if h32(int(u * 7), int(nv * 3), seed) % 5 == 0 else CSTONE, val, x, y)
                if abs(nv) > 0.86: c = CSTONE[1]
            elif -1.1 < u < -0.62:                                                                    # the tail fins
                fu = (-0.62 - u) / 0.48
                top = -r_of(u) - fu * 1.15; bot = r_of(u) + fu * 0.75
                if top < v < -r_of(u) + 0.1 or r_of(u) - 0.1 < v < bot:
                    if abs(v) > 0.2 or fu > 0.6: c = tone(CSTONE, 1.6 + (0.9 if v < 0 else 0) - fu * 0.6, x, y)
            if c is None:                                                                             # the hull
                hv = (y + 0.5 - hull_y) / hull_h
                if 0 <= hv <= 1:
                    wu = 0.42 - 0.16 * hv
                    if abs(u - 0.05) < wu + (0.08 if hv < 0.35 else 0) * (1 if u > 0.4 else 0):
                        c = tone(CWARM, 2.4 - hv * 1.6, x, y)
                        if hv < 0.25: c = CWARM[3]
                        if L > 50 and 0.35 < hv < 0.6 and int((u + 1) * 9) % 3 == 0 and h32(int(u * 20), seed) % 2: c = GLOW[1]   # lit ports
            if c is None and cy + hb * 0.75 < y < hull_y and any(abs(u - q) < 0.6 / L * 2 for q in (-0.28, -0.05, 0.18, 0.4)):
                c = CSTONE[1]                                                                         # the ropes
            if c is None and L > 50 and hull_y - L * 0.16 < y < hull_y and abs(u - 0.02) < 1.0 / L * 2:
                c = CWARM[0]                                                                          # a mast
            if c is not None and 0 <= x < W and 0 <= y < H: BD[y][x] = mix(c, HAZE_ROW[y], fade)

def skyship_near(cx, cy, L, flip=False, fade=0.18, seed=7):
    """a nearer skyship of the Verdigrace's kind, in detail: the fish-like gasbag under a net of vines with mossy
    patches and glowing green spots, ragged ribbed fins at the tail, a planked hull with a rail, a cabin, lit ports
    and vines trailing from its keel, rigging, a mast with a pennant"""
    hb = L * 0.21
    hull_y, hull_h = cy + hb * 1.95, L * 0.11
    def r_of(u):
        if u >= 1 or u <= -1.02: return 0.0
        r = math.sqrt(max(0.0, 1 - u * u))
        if u < 0: r *= 1 - 0.4 * (-u) ** 1.5
        return r
    sr = random.Random(seed)
    spots = [(sr.uniform(-0.6, 0.8), sr.uniform(-0.7, 0.6), sr.uniform(1.3, 2.4)) for _ in range(8)]
    ropes = (-0.42, -0.2, 0.02, 0.24, 0.44)
    out = {}
    for y in range(int(cy - hb * 2.6), int(hull_y + hull_h + 14)):
        for x in range(int(cx - L * 0.66), int(cx + L * 0.66) + 1):
            u = (x + 0.5 - cx) / (L / 2) * (-1 if flip else 1)
            v = (y + 0.5 - cy) / hb
            c = None
            r = r_of(u)
            if abs(v) < r:                                                                  # the gasbag
                nv = v / r
                val = 3.6 - nv * 2.0 - (0.6 if u < -0.45 else 0) + (0.6 if -0.2 < u < 0.6 and nv < -0.35 else 0)
                na = (u * 6.2 + nv * 1.6 + 0.12 * math.sin(u * 13 + seed)) % 1
                nb = (u * 6.2 - nv * 1.6 + 0.12 * math.sin(nv * 9 + seed)) % 1
                pal = CSTONE
                c = tone(CSTONE, val, x, y)
                if wn(2, u * 3 + seed, nv * 2) > 0.62 and nv < 0.2: c = mix(c, tone(VINE, val - 0.6, x, y), 0.6)   # moss on its back
                if na < 0.07 or nb < 0.07: c = tone(VINE, 1.6 + (0.8 if nv < 0 else 0), x, y)    # the vine net
                if na < 0.07 and nb < 0.07: c = VINE[3]
                for (su, sv, srad) in spots:                                                # glowing spots
                    d = math.hypot((u - su) * L / 2, (nv - sv) * hb)
                    if d < srad: c = MYC[3] if d < srad * 0.5 else MYC[2]
                if abs(nv) > 0.9: c = tone(CSTONE, 1.0, x, y)
            elif -1.2 < u < -0.52:                                                          # ragged ribbed fins
                fu = (-0.52 - u) / 0.68
                rag = (wn(1, u * 40 + seed, 3.0) - 0.5) * 0.25
                dors = 1.45 * math.sin(math.pi * min(1.0, fu * 1.15)) ** 0.8 + rag
                vent = 0.75 * math.sin(math.pi * min(1.0, fu * 1.3)) ** 0.9 + rag * 0.6
                rr = r_of(max(u, -1.0))
                if -rr - dors < v < -rr + 0.15 or rr - 0.15 < v < rr + vent:
                    rib = ((u * 16 - v * 0.6) % 1) < 0.16
                    c = mix(tone(CSTONE if not rib else VINE, 2.4 + (0.7 if v < 0 else 0) - fu * 0.6 - (0.7 if rib else 0), x, y), HAZE_ROW[y], 0.0 if rib else 0.3)
            if c is None:                                                                   # the hull
                hv = (y + 0.5 - hull_y) / hull_h
                if 0 <= hv <= 1:
                    up = max(0.0, (abs(u) - 0.32) / 0.2) ** 2 * 0.9                          # upturned bow and stern
                    wu = 0.5 - 0.2 * hv
                    if abs(u) < wu and hv > -up + up:
                        c = tone(CWARM, 3.0 - hv * 1.8 - (0.7 if int(hv * hull_h) % 3 == 0 else 0), x, y)
                        if hv < 0.15: c = CWARM[4]
                        if 0.35 < hv < 0.6 and int((u + 1) * 14) % 2 == 0 and abs(u) < 0.36: c = GLOW[2] if h32(int(u * 30), seed) % 3 else CWARM[1]
                hv2 = (y + 0.5 - hull_y) / hull_h
                if c is None and -0.55 < hv2 < 0 and 0.32 < abs(u) < 0.52 and abs(u) - 0.32 > -hv2 * 0.3:   # the raised ends
                    c = tone(CWARM, 3.2, x, y)
                if c is None and -0.3 < hv2 < -0.05 and abs(u) < 0.5 and (int((u + 1) * 30) % 3 == 0 or hv2 > -0.12):
                    c = CWARM[1]                                                            # the rail
                if c is None and -0.75 < hv2 < 0 and -0.3 < u * (-1 if flip else 1) * (-1) < -0.12:
                    c = tone(CWARM, 2.2, x, y)                                             # a cabin aft
                if c is None and hv2 > 1 and hv2 < 1 + 1.4 * ((h32(int((u + 1) * 40), seed, 3) % 100) / 100.0) and h32(int((u + 1) * 40), seed, 4) % 3 == 0 and abs(u) < 0.42:
                    c = tone(VINE, 2.4 - (hv2 - 1) * 1.6, x, y)                             # vines trailing from the keel
            if c is None and cy + hb * 0.85 < y < hull_y and any(abs(u - q - (y - cy) * 0.0008) < 0.55 / L * 2 for q in ropes):
                c = CSTONE[1]                                                               # rigging
            if c is None and hull_y - L * 0.2 < y < hull_y and abs(u - 0.08) < 0.7 / L * 2:
                c = CWARM[0]                                                                # the mast
            if c is None and hull_y - L * 0.2 < y < hull_y - L * 0.2 + 4:
                pu = (u - 0.08) * (-1 if flip else 1) * L / 2
                if 0 < -pu < 9 - (y - (hull_y - L * 0.2)) * 1.6: c = RUSTY[3]               # its pennant, streaming aft
            if c is not None: out[(x, y)] = c
    for (x, y), c in out.items():                                                           # a dark rim against the sky
        if not (0 <= x < W and 0 <= y < H): continue
        edge = any((x + a, y + b) not in out for (a, b) in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        BD[y][x] = mix(mix(c, CSTONE[0], 0.4) if edge else c, HAZE_ROW[y], fade)

skyship(752, 262, 38, flip=False, fade=0.5, seed=1)
skyship(398, 232, 18, flip=True, fade=0.62, seed=3)
skyship(985, 246, 26, flip=True, fade=0.55, seed=4)
skyship_near(872, 166, 118, flip=True, fade=0.16, seed=7)
# flocks of birds: a big loose one over the egg, a smaller one far off, a few near
for (fx, fy, n, big, sx_, sy_, seed) in ((432, 168, 15, 1, 70, 26, 1), (800, 236, 10, 0, 44, 12, 2), (292, 118, 6, 1, 26, 10, 3), (668, 150, 5, 1, 22, 8, 4)):
    fr = random.Random(seed)
    for i in range(n):
        bx = int(fx + fr.uniform(-sx_, sx_)); by = int(fy + fr.uniform(-sy_, sy_) + abs(bx - fx) * 0.25)
        col = mix(CSTONE[1], HAZE_ROW[by], 0.15 if big else 0.4)
        flap = fr.random() < 0.5
        pts = ((-2, -1), (-1, 0), (0, 1 if flap else 0), (1, 0), (2, -1)) if big else ((-1, 0), (0, 1), (1, 0))
        for (ox, oy) in pts:
            if 0 <= bx + ox < W and 0 <= by + oy < H: BD[by + oy][bx + ox] = col

img = Image.new('RGB', (W, H)); ip = img.load()
for y in range(H):
    for x in range(W): ip[x, y] = BD[y][x]
img.save(os.path.join(OUT, 'backdrop.png'))
print('backdrop saved')
if len(sys.argv) > 2 and sys.argv[2] == 'backdrop': sys.exit(0)

# ---------------------------------------------------------------------------------------------------- 4. the overlook
rs = Raster()
ZF, ZK = 16.4, 17.6                                  # the balustrade's plinth: front, back
YP, YC0, YC1 = 0.75, 2.75, 3.2                       # plinth top, coping bottom, coping top
BREAK = (-6.2, -1.4)                                 # the broken stretch (X)
PIERS = [-23.8, -10.4, 12.2, 27.3]
LANTERN_X = 12.2
SIGN_X, SIGN_Z = X_at(911, 15.6), 15.6

rs.quad((-3000, 1600, 500), (3000, 1600, 500), (-3000, -1600, 500), lambda x, y, s, t, z, wp: BD[y][x], cls='sky')

def slab(X, Z):
    """which flagstone (X, Z) lies on: (col, row, fx, fz, hash, width, depth)"""
    rw = 1.7
    row = math.floor(Z / rw); off = (row % 2) * 1.35 + (h32(row, 3) % 5) * 0.21
    cw = 2.5 + (h32(row, 4) % 3) * 0.25
    col = math.floor((X + off) / cw)
    return col, row, (X + off) / cw - col, Z / rw - row, h32(col, row, 5), cw, rw

def puddle(X, Z):
    """rain standing in the worn hollows of some slabs: 1 inside, a thin band below 0.5 = the wet rim"""
    if Z > ZF - 0.35: return 0.0
    col, row, fx, fz, k, cw, rw = slab(X, Z)
    if k % 4 != 1: return 0.0
    cx_, cz_ = 0.35 + (k % 7) * 0.05, 0.4 + ((k >> 4) % 5) * 0.05
    r = 0.24 + ((k >> 8) % 4) * 0.05
    d = math.hypot((fx - cx_) * cw, (fz - cz_) * rw * 1.4) / (r * cw) + (wn(3, X * 2.2, Z * 2.2) - 0.5) * 0.6 + (wn(1, X * 5, Z * 5) - 0.5) * 0.15
    return clamp((1.0 - d) * 12 + 0.5)

def flags(x, y, s, t, z, wp):
    """big worn flagstones in running bond: dark joints with moss in them, per-slab tone, dished and cracked slabs,
    damp toward the balustrade"""
    X, _, Z = wp
    col, row, fx, fz, k, cw, rw = slab(X, Z)
    jx = 1.15 * z / F / cw; jz = 1.15 * z * z / (F * CAMH) / rw
    if fx < jx or fz < jz:                                                         # the joints, moss in some
        m = wn(1, X * 1.7, Z * 1.7) + (wn(3, X * 4.0, Z * 4.0) - 0.5) * 0.3
        c = tone(LEAFR, 0.6 + (m - 0.6) * 4, x, y) if m > 0.6 else STONE[1]
        return c
    v = 4.9 + ((k % 7) - 3) * 0.25 + (wn(0, X * 1.3, Z * 1.3) - 0.5) * 0.6 + (0.5 if k % 13 == 4 else 0)
    v -= 0.9 * (1 - min(fx, 1 - fx) * 2) ** 6 * 0.0
    v -= 0.55 * math.exp(-((fx - 0.5) ** 2 + (fz - 0.5) ** 2) * 6) * (k % 4 == 1)          # worn hollow in the middle
    if k % 5 == 0 and abs((fx - 0.2) * 0.7 - (fz - 0.3)) < 0.022 + jz * 0.4: v -= 1.4       # a crack across the slab
    if k % 11 == 3 and fx > 0.55 and fz > 0.6: v -= 0.9                                    # a chipped corner
    edge = min(fx, 1 - fx, fz, 1 - fz)
    if edge < 0.06: v -= 0.5                                                                # worn, rounded edges
    c = tone(STONE, v, x, y)
    mo = wn(1, X * 0.45 + 20, Z * 0.9) + 0.35 * clamp((Z - 15.4) / 1.0) + 0.25 * clamp((13.0 - Z) / 1.2)
    if mo > 0.86 and edge < 0.03 + (mo - 0.86) * 0.5:                                     # moss creeping in from the joints
        c = tone(LEAFR, 0.8 + (wn(3, X * 3, Z * 3) - 0.5) * 2, x, y)
    return c
rs.quad((-80, 0, 3), (80, 0, 3), (-80, 0, ZF), flags, cls='ground')

def stone_blocks(v0, blen=2.4, seed=0, course=None, moss=0.0):
    """dressed stone in blocks: joints, per-block tone, chipped arrises, lichen, moss at the foot"""
    def sh(x, y, s, t, z, wp):
        X, Y, Z = wp
        u = X
        if course:
            r = math.floor((Y - course[0]) / course[1]); off = (r % 2) * blen * 0.5
        else:
            r = 0; off = 0
        bi = math.floor((u + off + seed * 0.37) / blen); fu = (u + off + seed * 0.37) / blen - bi
        k = h32(bi, r, seed, 51)
        v = v0 + ((k % 5) - 2) * 0.25 + (wn(0, u * 1.1 + seed, Y * 1.1) - 0.5) * 0.9
        if fu < 1.1 * z / F / blen: v -= 1.5                                                # the joint
        elif fu < 2.2 * z / F / blen: v += 0.4                                               # its lit arris
        if course and ((Y - course[0]) / course[1]) % 1 < 1.0 * z / F / course[1]: v -= 1.3
        c = tone(STONE, v, x, y)
        if wn(3, u * 0.7 + seed, Y * 0.9) > 0.7 - moss: c = tone(LEAFR, 1.2 + (wn(1, u * 3, Y * 3) - 0.5) * 2.4, x, y)   # lichen, moss
        return c
    return sh

def coping_top(x, y, s, t, z, wp):
    """the coping's top: worn smooth, lighter (the sky on it), cushions of moss, a wet sheen"""
    X, Y, Z = wp
    bi = math.floor(X / 2.6); fu = X / 2.6 - bi
    v = 6.0 + ((h32(bi, 52) % 5) - 2) * 0.3 + (wn(0, X * 1.5, Z * 1.5) - 0.5) * 0.9
    if fu < 1.1 * z / F / 2.6: v -= 2.0
    c = tone(STONE, v, x, y)
    m = wn(2, X * 0.5 + 31, 3.0) + (wn(3, X * 2.5, Z * 2.5) - 0.5) * 0.3
    if m > 0.6: c = tone(LEAFR, 1.6 + (m - 0.6) * 6 + (wn(1, X * 4, Z * 4) - 0.5) * 2, x, y)
    return c

def baluster_sh(x, y, s, t, z, wp):
    """a turned baluster: square foot and head, a neck, a fat belly; lit from the left"""
    if t < 0.1 or t > 0.9: r = 0.5
    elif t < 0.16 or 0.8 < t < 0.9: r = 0.3
    else:
        tt = (t - 0.16) / 0.64
        r = 0.24 + 0.24 * math.sin(math.pi * min(1.0, tt * 1.25)) ** 1.2 if tt < 0.8 else 0.22 + (tt - 0.8) * 0.3
    u = (s - 0.5) * 2 / r if r > 0 else 9
    if abs(u) > 1: return None
    v = 4.6 - u * 1.6 - abs(u) ** 4 * 1.2 + (wn(0, wp[0] * 2, wp[1] * 2) - 0.5) * 0.8
    if t < 0.1 or t > 0.9: v += 0.3
    c = tone(STONE, v, x, y)
    if wn(3, wp[0] * 1.4, wp[1] * 1.1) > 0.74: c = tone(LEAFR, 1.0 + (1 - u) * 0.6, x, y)
    return c


def carve_coping(c, x, y, t, wp):
    """the coping's carved front: a lit fillet along the top, a sunk groove under it, dentils along the bottom"""
    k = 0.0
    if t > 0.86: k = 0.12
    elif 0.66 < t < 0.76: k = -0.28
    elif t < 0.3: k = 0.1 if (wp[0] * 3.2) % 1 < 0.5 else -0.18
    return tuple(max(0, min(255, int(v * (1 + k)))) for v in c)

def pier_panel(sh, PX):
    """a pier's front with a sunk panel (a lit lower sill, a shadowed upper edge) and a worn carved rosette"""
    def f(x, y, s, t, z, wp):
        c = sh(x, y, s, t, z, wp)
        u, v = (wp[0] - PX) / 0.95, (wp[1] - 1.9) / 1.4
        if abs(u) < 0.62 and abs(v) < 0.85:
            k = -0.22
            if v > 0.78: k = -0.42                                                        # the overhang's shadow
            elif v < -0.78 or u < -0.55: k = 0.1                                          # lit lower and left edges
            d = math.hypot(u / 0.62, (v - 0.1) / 0.62)
            if d < 0.55:                                                                  # the rosette
                a = math.atan2(v - 0.1, u)
                k = 0.12 if (a * 4 / math.pi) % 1 < 0.55 and d > 0.18 else (-0.3 if d > 0.48 else 0.0)
                if d < 0.16: k = 0.2
            c = tuple(max(0, min(255, int(q * (1 + k)))) for q in c)
        return c
    return f

def plinth_moulding(sh):
    def f(x, y, s, t, z, wp):
        c = sh(x, y, s, t, z, wp)
        k = 0.14 if t > 0.78 else (-0.25 if 0.68 < t <= 0.78 else 0.0)
        return tuple(max(0, min(255, int(q * (1 + k)))) for q in c)
    return f

broken = lambda X: BREAK[0] < X < BREAK[1]
near_pier = lambda X: any(abs(X - p) < 1.5 for p in PIERS)
# the plinth (whole, but its top chipped in the break)
rs.box(-60, 60, 0, YP, ZF, ZK, plinth_moulding(stone_blocks(3.4, 2.4, 1, moss=0.05)), stone_blocks(3.0, 2.4, 2),
       top=lambda x, y, s, t, z, wp: tone(STONE, 4.6 + (wn(0, wp[0] * 2, wp[2] * 2) - 0.5), x, y), cls='wall')
# balusters
bx = -40.0
while bx < 40:
    if not near_pier(bx) and not broken(bx):
        rs.quad((bx - 0.32, YP, (ZF + ZK) / 2), (bx + 0.32, YP, (ZF + ZK) / 2), (bx - 0.32, YC0, (ZF + ZK) / 2), baluster_sh, cut=True, cls='prop')
    elif broken(bx) and h32(int(bx * 10), 53) % 3 == 0:                                # a stump left standing
        rs.quad((bx - 0.32, YP, (ZF + ZK) / 2), (bx + 0.32, YP, (ZF + ZK) / 2), (bx - 0.32, YP + 0.7, (ZF + ZK) / 2),
                lambda x, y, s, t, z, wp: (baluster_sh(x, y, s, t * 0.36, z, wp) if t < 0.85 + 0.15 * math.sin(s * 9) else None), cut=True, cls='prop')
    bx += 1.0
# the coping: whole runs, ragged ends at the break
for (a, b_) in ((-60, BREAK[0] + 0.35), (BREAK[1] - 0.2, 60)):
    def cfront(x, y, s, t, z, wp, a=a, b_=b_):
        X = wp[0]
        if X < BREAK[1] and X > BREAK[0] - 0.4 and a < -50:                             # the broken end, left
            if t > 0.25 + 0.6 * ((h32(int(wp[1] * 20), 54) % 7) / 7.0) and X > BREAK[0] + 0.05: return None
        if X > BREAK[0] and X < BREAK[1] + 0.3 and a > -50:
            if t > 0.3 + 0.5 * ((h32(int(wp[1] * 20), 55) % 7) / 7.0) and X < BREAK[1] - 0.05: return None
        c = stone_blocks(3.9, 2.6, 3)(x, y, s, t, z, wp)
        return carve_coping(c, x, y, t, wp)
    rs.quad((a, YC0, ZF - 0.22), (b_, YC0, ZF - 0.22), (a, YC1, ZF - 0.22), cfront, cut=True, cls='wall')
    ta, tb = (a, min(b_, BREAK[0] + 0.05)) if a < -50 else (max(a, BREAK[1] - 0.05), b_)
    rs.quad((ta, YC1, ZF - 0.22), (tb, YC1, ZF - 0.22), (ta, YC1, ZK + 0.22), coping_top, cls='wall')
# piers with caps; a stone ball on two of them, the lantern on another
for k, PX in enumerate(PIERS):
    rs.box(PX - 0.95, PX + 0.95, 0, 3.75, ZF - 0.3, ZK + 0.3, pier_panel(stone_blocks(3.6, 0.95, 10 + k, course=(0.0, 0.62), moss=0.06), PX),
           stone_blocks(2.8, 0.95, 20 + k, course=(0.0, 0.62)), cls='wall')
    rs.box(PX - 1.12, PX + 1.12, 3.75, 4.15, ZF - 0.48, ZK + 0.48, stone_blocks(4.2, 3.0, 30 + k), lambda x, y, s, t, z, wp: STONE[3],
           top=coping_top, cls='wall')
    if k == 2 and False:
        rs.disc(PX, 4.75, (ZF + ZK) / 2, 0.55, lambda x, y, s, t, z, wp: tone(STONE, 5.0 - s * 1.6 - t * 1.6 + (wn(3, x * 0.6, y * 0.6) - 0.5) * 1.4, x, y), cls='prop')
        rs.box(PX - 0.35, PX + 0.35, 4.15, 4.3, (ZF + ZK) / 2 - 0.35, (ZF + ZK) / 2 + 0.35, lambda x, y, s, t, z, wp: STONE[3], lambda x, y, s, t, z, wp: STONE[2], cls='prop')
# the lantern: an iron post on the pier cap, a glazed box glowing warm, a little roof
LZ = (ZF + ZK) / 2
rs.line3((LANTERN_X, 4.15, LZ), (LANTERN_X, 5.0, LZ), lambda x, y, s, t, z, wp: METAL[1], w=0.16)
iron = lambda x, y, s, t, z, wp: METAL[0] if (s < 0.14 or s > 0.86 or t < 0.08 or t > 0.92 or abs(s - 0.5) < 0.05) else GLOW[2 + (abs(s - 0.5) < 0.25 and 0.25 < t < 0.75)]
rs.quad((LANTERN_X - 0.3, 5.0, LZ - 0.3), (LANTERN_X + 0.3, 5.0, LZ - 0.3), (LANTERN_X - 0.3, 5.85, LZ - 0.3), iron, cls='emit')
rs.quad((LANTERN_X - 0.3, 5.0, LZ - 0.3), (LANTERN_X - 0.3, 5.0, LZ + 0.3), (LANTERN_X - 0.3, 5.85, LZ - 0.3), iron, cls='emit')
rs.quad((LANTERN_X - 0.42, 5.85, LZ - 0.42), (LANTERN_X + 0.42, 5.85, LZ - 0.42), (LANTERN_X - 0.42, 6.35, LZ - 0.42), tri_sh(STONE[0:1] * 2 + [METAL[1], METAL[2], METAL[3]], 2.0), cut=True, cls='prop')
rs.line3((LANTERN_X, 6.3, LZ - 0.4), (LANTERN_X, 6.6, LZ - 0.4), lambda x, y, s, t, z, wp: METAL[1], w=0.08)
# a tall lidded amphora on the first pier, on a small plinth: a cracked, chipped rim, two loop handles, moss
SZp = (ZF + ZK) / 2
rs.box(PIERS[0] - 0.62, PIERS[0] + 0.62, 4.15, 4.55, SZp - 0.5, SZp + 0.5, stone_blocks(4.4, 9.0, 41), lambda x, y, s, t, z, wp: STONE[2],
       top=lambda x, y, s, t, z, wp: STONE[5], cls='prop')
def amphora(x, y, s, t, z, wp):
    xn = (s - 0.5) * 2
    if t < 0.06: r = 0.5                                                                 # the foot
    elif t < 0.12: r = 0.28                                                              # the stem
    elif t < 0.78: r = 0.26 + 0.52 * math.sin(math.pi * (t - 0.12) / 0.66) ** 0.7       # the tall body
    elif t < 0.86: r = 0.26                                                              # the neck
    elif t < 0.9: r = 0.4                                                                # the rim
    elif t < 0.97: r = 0.34 - (t - 0.9) / 0.07 * 0.22                                    # the lid
    else: r = 0.1                                                                        # its knob
    hd = ((abs(xn) - 0.5) / 0.09) ** 2 + ((t - 0.77) / 0.07) ** 2                       # the loop handles
    if abs(xn) > r:
        if 0.35 < hd < 1.0 and abs(xn) > 0.3: return tone(STONE, 3.6 - xn * 1.2, x, y)
        return None
    if 0.86 < t < 0.92 and xn > 0.18 and xn < 0.18 + (0.92 - t) * 6: return None        # a chip out of the rim
    u = xn / r
    v = 5.0 - u * 1.6 - abs(u) ** 3 * 1.3 + (wn(0, wp[0] * 3, wp[1] * 3) - 0.5) * 0.9
    if t < 0.06 or 0.86 < t < 0.9: v += 0.5
    if 0.9 <= t < 0.91 or 0.12 <= t < 0.13: v -= 1.4                                    # the lid's and the stem's seams
    if 0.4 < t < 0.44 or 0.6 < t < 0.62: v -= 0.7                                        # incised bands
    if abs(xn - 0.12 - (0.86 - t) * 0.9 - 0.05 * math.sin(t * 60)) < 0.035 and 0.5 < t < 0.88: v -= 2.0   # the crack down from the rim
    c = tone(STONE, v, x, y)
    m = wn(3, wp[0] * 2.2, wp[1] * 2.2) + 0.35 * clamp((0.3 - t) / 0.3) + 0.3 * (t > 0.9) - 0.15 * u
    if m > 0.72: c = tone(LEAFR, 1.6 - u * 0.5 + (m - 0.72) * 3, x, y)                   # moss on the lid and the foot
    return c
rs.quad((PIERS[0] - 0.7, 4.55, SZp - 0.1), (PIERS[0] + 0.7, 4.55, SZp - 0.1), (PIERS[0] - 0.7, 6.65, SZp - 0.1), amphora, cut=True, cls='prop')
# an urn on the second pier, ivy tumbling out of it
def urn(x, y, s, t, z, wp):
    if t < 0.1: r = 0.42
    elif t < 0.2: r = 0.2
    elif t < 0.82: r = 0.24 + 0.24 * math.sin(math.pi * (t - 0.2) / 0.62) ** 0.8
    elif t < 0.9: r = 0.3
    else: r = 0.46
    u = (s - 0.5) * 2 / r
    if abs(u) > 1: return None
    v = 4.8 - u * 1.5 - abs(u) ** 3 * 1.2 + (0.6 if t > 0.9 or t < 0.1 else 0) + (wn(0, wp[0] * 3, wp[1] * 3) - 0.5) * 0.9
    if 0.5 < t < 0.6: v -= 0.6                                                           # a carved band
    c = tone(STONE, v, x, y)
    if wn(3, wp[0] * 2.4, wp[1] * 2.4) > 0.7: c = tone(LEAFR, 1.4 - u * 0.5, x, y)       # lichen
    return c
rs.quad((PIERS[1] - 0.6, 4.15, SZp), (PIERS[1] + 0.6, 4.15, SZp), (PIERS[1] - 0.6, 5.75, SZp), urn, cut=True, cls='prop')
# the fallen coping and rubble in front of the break
def obox(cx, cz, w, d, h, yaw, y0, front, side, top):
    """a box turned by `yaw` about the vertical, standing on y0: its three faces toward the camera"""
    ca, sa = math.cos(yaw), math.sin(yaw)
    def P(u, v, yy): return (cx + u * ca - v * sa, yy, cz + u * sa + v * ca)
    o = rs.obj()
    rs.quad(P(-w / 2, -d / 2, y0), P(w / 2, -d / 2, y0), P(-w / 2, -d / 2, y0 + h), front, o, cls='prop')
    rs.quad(P(-w / 2, -d / 2, y0 + h), P(w / 2, -d / 2, y0 + h), P(-w / 2, d / 2, y0 + h), top, o, cls='prop')
    sx_ = w / 2 if cx + (w / 2) * ca < 0 else -w / 2
    rs.quad(P(sx_, -d / 2, y0), P(sx_, d / 2, y0), P(sx_, -d / 2, y0 + h), side, o, cls='prop')
rs_top = lambda x, y, s, t, z, wp: tone(STONE, 6.6 + (wn(0, wp[0] * 2, wp[2] * 2) - 0.5) * 1.0 - (0.8 if s < 0.04 or s > 0.96 else 0), x, y)
obox(-4.3, 15.55, 2.6, 1.55, 0.45, 0.16, 0.0, stone_blocks(4.8, 9.0, 61), stone_blocks(3.6, 9.0, 62), rs_top)    # a fallen coping stone
for (rx, rz, sz, yaw) in ((-2.2, 15.9, 0.42, -0.5), (-1.5, 15.2, 0.26, 0.7), (-6.4, 15.8, 0.34, 0.3), (-3.2, 14.9, 0.2, 1.1), (-5.6, 14.7, 0.16, 0.2)):
    obox(rx, rz, sz * 1.7, sz * 1.3, sz, yaw, 0.0, stone_blocks(4.6, 9.0, 63), stone_blocks(3.4, 9.0, 64), rs_top)

# ivy: strands of leaves hanging over the coping and down the balusters, draped over its top edge; two piers
# swallowed by it. Each leaf is a small disc (lit upper left), jittered, so it never reads as a grid.
irng = random.Random(77)
def leaf_sh(var):
    def sh(x, y, a, b, z, wp):
        if a * a + (b * 1.15) ** 2 > 1 or (a > 0.55 and b > 0.55): return None
        v = 2.7 + var - (a + b) * 0.9 - (0.9 if a * a + b * b > 0.7 else 0)
        return tone(LEAFR, v, x, y)
    return sh
def ivy(X0, X1, ytop, zf, seed, dens=0.55, maxlen=2.6, top_depth=0.7):
    X = X0
    while X < X1:
        cl = wn(1, X * 0.32 + seed * 7.0, 11.0 + seed)
        if cl > 1 - dens:
            ln = maxlen * ((cl - (1 - dens)) / dens) * (0.35 + 0.65 * irng.random())
            Y = ytop + 0.04; j = 0
            for kk in range(int(top_depth / 0.16 * (0.5 + cl))):                    # over the top edge
                rs.disc(X + irng.uniform(-0.06, 0.06), ytop + 0.05, zf + 0.12 + kk * 0.16 + irng.uniform(0, 0.08),
                        irng.uniform(0.1, 0.15), leaf_sh(irng.uniform(-0.3, 0.9)), cls='prop')
            while ytop - Y < ln:
                side = 0.05 if j % 2 else -0.05
                rs.disc(X + side + irng.uniform(-0.04, 0.04), Y, zf - irng.uniform(0.0, 0.08),
                        irng.uniform(0.09, 0.14) * (1 - 0.3 * (ytop - Y) / max(0.4, ln)), leaf_sh(irng.uniform(-0.6, 0.7) - 0.6 * (ytop - Y) / max(0.4, ln)), cls='prop')
                Y -= irng.uniform(0.1, 0.17); j += 1
        X += irng.uniform(0.09, 0.16)
for (a, b_, seed, dens, ml) in ((-31, -24.7, 1, 0.6, 2.4), (-22.9, -18.0, 2, 0.5, 1.6), (-16.5, -11.3, 3, 0.62, 2.6),
                                (-9.5, BREAK[0] + 0.3, 4, 0.7, 2.7), (BREAK[1] - 0.1, 3.0, 5, 0.45, 1.4), (6.5, 11.3, 6, 0.55, 2.2),
                                (13.1, 18.5, 7, 0.4, 1.3), (22.0, 26.4, 8, 0.66, 2.7), (28.2, 34, 9, 0.6, 2.5)):
    ivy(a, b_, YC1, ZF - 0.3, seed, dens, ml)
for (PX, seed) in ((PIERS[3], 12),):                                                  # a pier swallowed by ivy
    ivy(PX - 1.2, PX + 1.2, 4.2, ZF - 0.55, seed, 0.9, 4.0, 1.4)
ivy(PIERS[1] - 0.5, PIERS[1] - 0.1, 5.72, SZp - 0.45, 13, 0.7, 1.1, 0.0)      # spilling out of the urn
ivy(PIERS[0] - 1.15, PIERS[0] - 0.2, 4.1, ZF - 0.55, 14, 0.8, 2.2, 0.6)       # a little up the amphora's pier

# the signpost: a crooked post, a board with an arrow end, the Cathedral painted on it (in post(), weathered)
SX, SZ = SIGN_X, SIGN_Z
post_wood = lambda x, y, s, t, z, wp: tone(WOOD, 3.4 + (1.0 if s < 0.35 else -0.6 if s > 0.7 else 0) + (wn(0, wp[0] * 6, wp[1] * 0.8) - 0.5) * 1.6 - 1.2 * max(0.0, 1 - wp[1] / 1.2), x, y)
rs.quad((SX - 0.2, 0, SZ), (SX + 0.2, 0, SZ), (SX - 0.2 + 0.25, 7.0, SZ), post_wood, cls='prop')
rs.quad((SX + 0.2, 0, SZ), (SX + 0.2, 0, SZ + 0.4), (SX + 0.2 + 0.25, 7.0, SZ), lambda x, y, s, t, z, wp: tone(WOOD, 1.6, x, y), cls='prop')
BRD = (SX - 0.85, SX + 3.9, 4.75, 6.55, SZ - 0.22)                                     # x0, x1 (body), y0, y1, z
TIP = 0.9
def board(x, y, s, t, z, wp):
    X, Y, Z = wp
    L_ = BRD[1] - BRD[0]
    if X > BRD[1]:
        if abs(Y - (BRD[2] + BRD[3]) / 2) > (BRD[3] - BRD[2]) / 2 * (1 - (X - BRD[1]) / TIP): return None
    plank = math.floor((Y - BRD[2]) / ((BRD[3] - BRD[2]) / 2))
    v = 3.0 + plank * 0.5 + (wn(0, X * 0.9, Y * 9) - 0.5) * 1.4 + (0.6 if (Y - BRD[2]) % ((BRD[3] - BRD[2]) / 2) > 0.62 else 0)
    if abs((Y - BRD[2]) - (BRD[3] - BRD[2]) / 2) < 1.0 * z / F: v -= 1.6                 # the seam between the two planks
    edge = min(X - BRD[0], Y - BRD[2], BRD[3] - Y)
    if edge < 1.2 * z / F: v -= 1.2
    return tone(WOOD, v, x, y)
rs.quad((BRD[0], BRD[2], BRD[4]), (BRD[1] + TIP, BRD[2], BRD[4]), (BRD[0], BRD[3], BRD[4]), board, cut=True, cls='prop')
SIGN_GLYPH = ['       ####       ', '      ######      ', '     ########     ', '     ########     ', '    ##########    ',
              '    ##########    ', '    ##########    ', ' #  ##########  # ', ' #  ##########  # ', '### ########## ###',
              '###  ########  ###', '###   ######   ###', '###            ###', '######  ##  ######', '######  ##  ######',
              '##################', '##################']

def post_fx(col, cls):
    """2D touches before the painterly pass: the sign's paint, weeds in the joints and along the plinth"""
    p0 = proj(BRD[0], BRD[3], BRD[4]); p1 = proj(BRD[1] + TIP, BRD[2], BRD[4])
    bx0, by0, bx1, by1 = int(p0[0]), int(p0[1]), int(p1[0]), int(p1[1])
    paint = (196, 192, 170)
    gx, gy = bx0 + 7, by0 + (by1 - by0 - len(SIGN_GLYPH)) // 2
    for r, row in enumerate(SIGN_GLYPH):
        for k, ch in enumerate(row):
            if ch == '#' and h32(k, r, 91) % 11:
                col[gy + r][gx + k] = paint if h32(k // 2, r // 2, 92) % 6 else (150, 146, 128)   # worn paint
    ay = gy + 8
    ax0, ax1 = gx + 26, bx1 - 22
    for x in range(ax0, ax1 + 1):
        for dy in (0, 1):
            if h32(x, dy, 93) % 9: col[ay + dy][x] = paint
    for d in range(1, 6):
        for dy in (0, 1):
            col[ay - d + dy][ax1 - d] = paint; col[ay + d + dy - 1][ax1 - d] = paint
    # wet flags: puddles mirror the balustrade / signpost above them and, past those, the pale overcast (lighter than
    # the wet stone, as rain water is on a grey day); a faint sheen on the damp stone by the balustrade
    for y in range(HY + 1, H):
        for x in range(W):
            g = rs.G[y][x]
            if g is None or g[5] != 'ground' or g[4] is None: continue
            X, _, Z = g[4]
            p_ = puddle(X, Z)
            k = 0.82 if p_ > 0.5 else 0.1 + 0.14 * clamp((Z - 12.0) / 4.4)
            if 0.0 < p_ <= 0.5:                                                               # the wet lip
                if puddle(X, Z + 0.06) > 0.5: col[y][x] = mix(col[y][x], (22, 28, 26), 0.3)
                k = 0.4
            hit = None; t = 1.02
            while t < 3.2:
                Zt = Z * t; Yw = CAMH * (t - 1); yy = int(HY + F * (CAMH - Yw) / Zt)
                if yy < 0: break
                if yy < y and rs.ZB[yy][x] <= Zt + 0.6: hit = col[yy][x]; break
                t += max(0.01, 0.5 / Z)
            if hit is None:
                rip = int((wn(3, X * 2.5, Z * 7) - 0.5) * 4)
                hit = mix(BD[max(0, int(HY - (y - HY) * 0.32) + rip)][min(W - 1, max(0, x + rip))], HAZE_ROW[236], 0.55)
            col[y][x] = mix(col[y][x], mix(hit, (0, 0, 0), 0.06), k)
    # fallen leaves from the ivy: a scatter, thicker under the ivy and along the plinth
    lr = random.Random(9)
    LEAFC = [(92, 84, 46), (110, 96, 52), (76, 82, 44), (64, 70, 40), (124, 104, 58)]
    for k in range(260):
        X = lr.uniform(-30, 30); Z = ZF - 0.1 - lr.random() ** 2.2 * 4.2
        if lr.random() > 0.35 + 0.65 * wn(1, X * 0.32 + 7.0, 11.0): continue
        px_, py_ = proj(X, 0, Z); px_, py_ = int(px_), int(py_)
        c = LEAFC[lr.randrange(len(LEAFC))]
        for (ox, oy) in ((0, 0), (1, 0)) if lr.random() < 0.6 else ((0, 0), (1, 0), (1, -1)):
            if 0 <= px_ + ox < W and 0 <= py_ + oy < H and cls[py_ + oy][px_ + ox] == 'ground':
                col[py_ + oy][px_ + ox] = c
    # weeds: thin blades in tufts along the plinth foot and in some joints
    wr = random.Random(5)
    for k in range(70):
        X = wr.uniform(-30, 30)
        Z = ZF - 0.08 if k < 45 else wr.uniform(12.6, 16.0)
        if k >= 45 and wn(1, X * 0.8, Z * 0.8) < 0.5: continue
        bx_, by_ = proj(X, 0, Z)
        bx_, by_ = int(bx_), int(by_)
        n = 2 + wr.randint(0, 4)
        for b in range(n):
            hgt = wr.randint(3, 9) * (1.3 if k < 45 else 0.8)
            lean = wr.uniform(-0.45, 0.45)
            for i in range(int(hgt)):
                xx, yy = int(bx_ + b * 1.3 - n * 0.6 + lean * i), by_ - i
                if 0 <= xx < W and 0 <= yy < H and cls[yy][xx] in ('ground', 'wall', 'prop'):
                    col[yy][xx] = LEAFR[min(5, 1 + (i * 3) // max(1, int(hgt)) + (b % 2))]

print('foreground...')
img = rs.render(INK, fog=lambda z: 0.0 if z < 100 else 0.0, post=post_fx,
                light_gain=1.7, grime_gain=1.2, bloom=0.3, stain_gain=1.1, damp_gain=0.7)
img.save(os.path.join(OUT, 'entry_city.png'))
print('saved', os.path.join(OUT, 'entry_city.png'))

# ---------------------------------------------------------------------------------------------------- 5. extras
def fixed_points():
    sb0 = proj(BRD[0], BRD[3], BRD[4]); sb1 = proj(BRD[1] + TIP, BRD[2], BRD[4])
    return {
        'thaal_feet': [600, 530], 'walk_line_y': 534,
        'exit_zone_800space': [780, 470, 40, 200],
        'signpost': {'post_x': round(proj(SX, 0, SZ)[0]), 'post_foot_y': round(proj(SX, 0, SZ)[1]),
                     'board': [round(sb0[0]), round(sb0[1]), round(sb1[0]), round(sb1[1])]},
        'coping_top_y': [round(proj(0, YC1, ZK + 0.22)[1]), round(proj(0, YC1, ZF - 0.22)[1])],
        'plinth_foot_y': round(proj(0, 0, ZF)[1]),
        'break_x': [round(proj(BREAK[0], YC1, ZF)[0]), round(proj(BREAK[1], YC1, ZF)[0])],
        'lantern': [round(proj(LANTERN_X, 5.4, LZ)[0]), round(proj(LANTERN_X, 5.4, LZ)[1])],
        'egg_cathedral': {'cx': EGG_SX, 'cy': EGG_SY, 'halves_x': [EGG_SX - EGG_B - EGG_SH - int(EGG_LEAN * 2 * EGG_A), EGG_SX + EGG_B + EGG_SH + int(EGG_LEAN * 2 * EGG_A)],
                          'top_y': EGG_SY - EGG_A, 'door': [EGG_SX - 7, CB - 31, EGG_SX + 7, CB], 'mound_x': list(MOUND), 'stair_foot_y': 462},
        'landmarks': {'lumen': [424, 492], 'townhall': [602, 654], 'voxmarket': [668, 788], 'shed521': [790, 882], 'sea_from_x': 870},
        'scraper_1140': {'slab_x': [SL0, SL1], 'slab_top_y': SLT - 4, 'mast_x': NEEDLE_SX, 'tip_y': 40, 'lit_window': list(SCR_WIN)},
    }

def guides(fp):
    """the Aseprite reference layer: exits, Thaal, the walk line, the horizon, the HUD zones (not exported)"""
    from PIL import ImageFont
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    try: fnt = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf', 11)
    except Exception: fnt = ImageFont.load_default()
    kx = W / 800
    def box(x0, y0, x1, y1, col, label):
        d.rectangle([x0, y0, x1, y1], outline=col)
        d.rectangle([x0, y0 - 14, x0 + 6 * len(label) + 4, y0], fill=(40, 40, 40, 220))
        d.text((x0 + 2, y0 - 13), label, fill=col, font=fnt)
    ex, ey, ew, eh = fp['exit_zone_800space']
    box(round((ex - ew / 2) * kx), ey - eh // 2, min(W - 1, round((ex + ew / 2) * kx)), ey + eh // 2, (90, 220, 255), 'EXIT -> Egg Cathedral')
    box(600 - 40, 530 - 128, 600 + 40, 530, (127, 255, 142), 'MISTR THAAL')
    b = fp['signpost']['board']
    box(b[0], b[1], b[2], b[3], (255, 210, 60), 'ROZCESTNIK')
    for (x0, y0, x1, y1, lab) in ((873, 4, 1057, 90, 'HUD tlacitka'), (0, 0, 110, 300, 'HUD ruzenec'), (20, 505, 100, 585, 'HUD inventar'),
                                  (325, 8, 475, 52, 'HUD spory')):
        box(x0, max(14, y0), x1, y1, (255, 120, 200), lab)
    for x in range(0, W, 8): d.line([(x, 534), (x + 4, 534)], fill=(255, 80, 80))
    d.text((4, 536), 'cara nohou y534 (hrac 128px)', fill=(255, 80, 80), font=fnt)
    for x in range(0, W, 8): d.line([(x, 296), (x + 4, 296)], fill=(200, 200, 90))
    d.text((4, 284), 'horizont / ubezny bod (533,296)', fill=(200, 200, 90), font=fnt)
    return g

def write_palette(img, path, n=96):
    """the Aseprite palette: the render's own colours, median cut, sorted dark to light"""
    q = img.quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:n * 3]
    cols = sorted({tuple(pal[i:i + 3]) for i in range(0, len(pal), 3)}, key=lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2])
    out = ['GIMP Palette', 'Name: Entry City', 'Columns: 12', '#']
    for c in cols: out.append('%3d %3d %3d\tEntry' % c)
    open(path, 'w').write('\n'.join(out) + '\n')
    return len(cols)

fp = fixed_points()
json.dump(fp, open(os.path.join(OUT, 'fixed.json'), 'w'), indent=1)
guides(fp).save(os.path.join(OUT, 'guides.png'))
Image.open(os.path.join(HERE_, 'chars.png')).save(os.path.join(OUT, 'chars.png'))
print('palette', write_palette(img, os.path.join(OUT, 'entry_city.gpl')), 'colours; fixed points', json.dumps(fp))

