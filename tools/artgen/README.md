# artgen — procedural pixel-art background generators

Python 3 + Pillow. Each `*_bg.py` renders a native 1067×600 background (overcast day, one-point perspective,
vanishing point (533, 296), focal length 300, camera height 12 world units — the player is ≈6.4 units tall,
feet on y 534). `pal_day.py` is the shared palette (exported as the Aseprite palette `crossroad-overcast.gpl`, a copy is
kept here; install it with `cp crossroad-overcast.gpl ~/.config/aseprite/palettes/`); `common.py` has noise, banding, the 3×5 pixel font.

```
python3 crossroad_bg.py <outdir>       # -> <outdir>/bg.png
python3 crossroad_corpse.py <outdir>   # -> corpse_0..2.png + crossroad_corpse.png (3-frame sheet 240×500)
python3 shed521_bg.py <outdir> [base|growth|decay]   # -> bg.png / bg_growth.png / bg_decay.png (Growth/Decay variants)
python3 burningbear_bg.py <outdir> [base|growth|decay]   # -> bg*.png + bears.json + fire_<variant>.png/.json (animated fire atlas,
                                                       #    frames trimmed to the 1067x600 canvas -> assets/images/props/bbs_fire_*)
python3 props.py <outdir>              # -> prop_*.png Growth/Decay scenery props (assets/images/props/, placed by utils/GDProps.js)
python3 <scene>_guides.py <outdir>     # hotspot guide layer for the Aseprite template
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite \
        --script-param pal=~/.config/aseprite/palettes/crossroad-overcast.gpl --script <scene>_aseprite.lua
```
`chars.png` is the character-scale overlay layer used in the templates. Regenerate from here rather than
hand-editing the PNGs; hand touch-ups go into the "UPRAVY" layer of the `.aseprite` files.

## Intro (the Hymnar + the Council chamber)
Underground palette `pal_under.py` (Aseprite: `intro-underground.gpl`, copy to `~/.config/aseprite/palettes/`).
`intro_layout.py` is the shared seat/table geometry (the back-row sprites are cut exactly at the table's far edge).
```
python3 intro_hymnar.py <outdir>         # -> hymnar.png 1067x1000 (+ _gills / _glow ADD layers, hymnar.json signal path + lanterns)
python3 intro_council_bg.py <outdir>     # -> council_bg.png, council_table.png, council_glow.png, council.json (seats, candles)
python3 intro_council_chars.py <outdir>  # -> council_<id>.png sheets + <id>/<n>.png frames, council_preview.png
# build the Aseprite sources (OVERWRITES assets/aseprite/Intro_*.aseprite, incl. their UPRAVY layers):
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite \
        --script-param pal=$HOME/.config/aseprite/palettes/intro-underground.gpl --script tools/artgen/intro_aseprite.lua
# export into the game (merges the UPRAVY layers) -- run this after hand edits in Aseprite:
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/intro --script tools/artgen/intro_export.lua >/dev/null
cp <outdir>/hymnar.json <outdir>/council.json assets/images/intro/
```
Sheets: Varhun / Tynri / Rhull 8 frames of 128x176 (idle 0 rest / 1 inhale / 2 blink / 3 eye-glow, talk 4-7 = mouth only);
elder_l / elder_r 4 frames of 200x350 (0 rest / 1 inhale / 2 head sinks or bulb glows / 3 blink; elder_r is flipped in the scene).
The scene keeps the figures still and only now and then shows an idle frame (IntroScene.idleLife) -- no fidgeting.

## Symbiont HUD (the "rosary" under the G/D medallion + the symbionts in it)
Palette `pal_symb.py` (Aseprite: `symbionts.gpl`, copy to `~/.config/aseprite/palettes/`).
```
python3 symbionts.py <outdir>        # -> symbionts.png (4 idle frames x 1 row per symbiont, 32x32) + symbiont_pods.png (5 x 48x58)
# build the Aseprite sources (OVERWRITES assets/aseprite/UI_Symbiont*.aseprite, incl. their UPRAVY layers):
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite \
        --script-param pal=$HOME/.config/aseprite/palettes/symbionts.gpl --script tools/artgen/symbionts_aseprite.lua
# export into the game (merges the UPRAVY layers) -- run this after hand edits in Aseprite:
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/ui --script tools/artgen/symbionts_export.lua
```
`UI_Symbionts_32x32.aseprite`: one tag per symbiont, frames 0 rest / 1 breath / 2 blink-or-glint / 3 accent; row order =
`SYMBIONT_ROWS` in `scenes/GameScene.js` (the last row, `generic`, is the fallback for a symbiont without art -- a new
symbiont = a new tag before `generic` + its id in `SYMBIONT_ROWS`). `UI_SymbiontPods_48x58.aseprite`: frames open pod /
sealed pod / cord end / glow (white, ADD, tinted per symbiont in the game); the hidden layer `maska retu` marks the pixels
of the open pod drawn IN FRONT of the symbiont (its lower lip). Pods stack every 58 px, the cord is continuous across them.

## HUD buttons (inventory satchel, map, journal, quest note + the unread badge)
Palette `pal_hud.py` (Aseprite: `hud.gpl`, copy to `~/.config/aseprite/palettes/`); shares the wax / vein / bone ramps
with the symbiont HUD.
```
python3 hud_buttons.py <outdir>      # -> hud_buttons.png (9 frames of 48x48) + hud/<n>.png
# build the Aseprite source (OVERWRITES assets/aseprite/UI_HudButtons_48x48.aseprite, incl. its UPRAVY layer):
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite \
        --script-param pal=$HOME/.config/aseprite/palettes/hud.gpl --script tools/artgen/hud_aseprite.lua
# export into the game -- run this after hand edits in Aseprite:
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/ui --script tools/artgen/hud_export.lua
```
Tags `inventar` / `mapa` / `denik` / `ukoly`: frame 1 closed, frame 2 the "open" hover state; `odznak` = the badge.
The game side is `utils/hudButton.js` (positions, hover frame swap, labels, badge).

## Feral Toast (the band in the Screaming Cork Club)
**Current sheets come from `feral_px.py`** (2026-10-25): like `edgar.py`, the original `feral_guitarist / bassplayer /
drummer / synth.png` box-filtered to their native grid (8×; Kārlis 7× — seated behind the kit he read small) and
animated by moving / relighting their own pixels: idle 0-3 (rest, breath, eyes, a small move), playing 4-11 = 4 beats,
2 frames per beat (knees give, headbangs on 1 and 3, strums; Kārlis' stick drops onto the crash which wobbles, the kick
thumps on 1 and 3, hi-hat on 2 and 4; Mira's hands alternate, runes shimmer, the skull's eyes flash, tendrils sway).
Frames 128×192 (Kārlis 144×192), soles on y 189; the scene's BAND `y` is the feet line (sprite at y + 2).
```
python3 feral_px.py <outdir>         # -> telka.png bass_xl.png karlis.png mira.png + <id>/<n>.png + feral_px.gpl
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite --script-param pal=$HOME/.config/aseprite/palettes/feral_px.gpl --script tools/artgen/feral_aseprite.lua
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters/feral_toast --script tools/artgen/feral_export.lua
```
The rig-drawn version below (`feral_toast.py`) is superseded but kept.

Palette + materials `pal_club.py` (Aseprite: `club.gpl`), renderer `rig.py`: volumes go into a tone buffer, then get cast
shadows, contact lines, material texture (denim, leather, fur, wool, metal), a 4×4 dither and a warm outline. Each member
is a small rig (two-bone IK onto the instrument; fretting hands sit UNDER the neck), so every frame is re-posed, not tweened.
```
python3 feral_toast.py <outdir>      # -> telka.png bass_xl.png karlis.png mira.png (12 frames each) + <id>/<n>.png
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite \
        --script-param pal=$HOME/.config/aseprite/palettes/club.gpl --script tools/artgen/feral_aseprite.lua
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters/feral_toast --script tools/artgen/feral_export.lua
```
`FeralToast_<id>.aseprite`: tag `ceka` = idle (frames 1-4), `hraje` = playing (5-12, two frames per beat of
feral-toast.mp3 ≈ 177 BPM). Sizes: telka 128×176, bass_xl 144×192, karlis 176×176 (with the kit), mira 144×176 (with the synth).
The old AI images `feral_*.png` stay — ScraperAmbraScene's cutscene still uses them.

## Voxmarket (the market inside the zeppelin hangar: main hall, Zerren's lane, the auction bay)
Same camera as the Crossroad, but the shell is RAY-CAST (a barrel vault with lattice trusses, side walls with steel
windows, a skylight band, the radial-glazed gable; or a flat gallery deck for the lane) and everything else is planar
quads with per-pixel depth (`quad()`, `box()`, `disc()`, `line3()`), shaded by small per-object shader functions.
```
python3 voxmarket_bg.py <outdir> hall|alley|auction [base|growth|decay]   # -> hall.png, hall_growth.png, ...
```
Game files: hall → `Voxmarket*.png` (VoxMarket), alley → `VoxmarketMarket*.png` (VoxmarketMarketScene),
auction → `VoxmarketHall*.png` (VoxmarketHallScene); the scenes swap variants with `applyGDBackground`.
Fixed points the art respects: the auction portal (arch in the right hangar wall at z 25, canvas x ≈ 915, exit zone 686 in 800-space),
Zerren's niche (his counter sprite at canvas 200, feet 517), the auction stage top at y ≈ 431 (the twins stand on it).
Rule: nothing low nearer than z ≈ 16 (the walk line y 534 must stay in front of all counters).

## Voxmarket NPCs (Kloor Venn, Zerren, Hesh & Vell)
Same renderer as Feral Toast (`rig.py`). `python3 voxmarket_chars.py <outdir>` → `kloor.png` (128×160: 0-3 idle,
4-11 walk, faces right), `zerren.png` (176×160, 4 idle, the counter is part of the sprite), `hesh_vell.png` (208×176,
8 idle frames; Vell repeats Hesh's gavel two frames late). Then
```
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite --script-param pal=$HOME/.config/aseprite/palettes/vox_chars.gpl --script tools/artgen/voxchars_aseprite.lua
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters/voxmarket --script tools/artgen/voxchars_export.lua
```
Sources `assets/aseprite/Vox_<id>.aseprite` (tags ceka / chuze, UPRAVY layer). In the scenes all three keep their old
texture keys (`kloor`, `zerren`, `heshAndVell`), shown at scale 1 with a bottom-centre origin on their feet.

## The protagonist (the Obazoba apprentice, texture key `priest`)
Same renderer (`rig.py`). `python3 hero.py <outdir>` → `priest.png` (12 frames of 128×128, faces right, soles on y 125:
0-3 idle, 4-11 an 8-frame walk) + `hero.gpl`. Then
```
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite --script-param pal=$HOME/.config/aseprite/palettes/hero.gpl --script tools/artgen/hero_aseprite.lua
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters --script tools/artgen/hero_export.lua
```
Source `assets/aseprite/Hero_priest_128.aseprite` (tags ceka / chuze, UPRAVY layer). The game shows it at scale 1
(`GameScene`: anims `idle` = frames 0,0,1,2,2,1,0,0,0,3,0,0 at 4 fps, `walk` = 4-11 at 14 fps; `PlayerMovementSystem`
flips with `setScale(±1, 1)`); the green additive `priestGlow` copy follows the priest's frame and origin.

## Painterly finish (`paintpass.py`) — grime, wear, light
Shared by `crossroad_bg.py`, `shed521_bg.py`, `burningbear_bg.py` (via the `face_engine()` adapter) and
`voxmarket_bg.py` (its own buffers + a normal buffer `NB`); every generator calls it on the shaded colours right before
its outline pass, so re-running a generator re-applies it. Everything is computed in world/surface coordinates: ground
contact shadow around wall/prop bases, a depth-based AO in recesses, shadows under anything that overhangs, rain-wash
streaks under ledges/sills, a damp foot of each wall (moss in Growth, soot in Decay), plaster falling off to brick
(`peel=`), cracks (`crack=`), chipped edges, warm light spilling from emissive pixels (lit windows, lamps, doorways)
plus bloom, cool-tinted shadows and a faint colour drift / brush grain. Strength knobs: `light_gain`, `grime_gain`, `bloom`.
To push a new render into an existing Aseprite source without touching its UPRAVY layer:
```
aseprite -b --script-param f=assets/aseprite/<file>.aseprite --script-param "layer=<base layer name>" --script-param img=<png> --script tools/artgen/bg_update.lua
```

## Interiors on the shared rasteriser (`raster3d.py`)
`raster3d.Raster` = quads / boxes / discs / 3D lines with per-pixel depth, world position, normal and a paintpass class
per object (`cls='ground'|'wall'|'ceil'|'prop'|'emit'`); `quad(..., cut=True)` and discs treat a shader's `None` as
transparent; `render(ink, fog, post=, overlay=, **paintpass knobs)` shades, runs `paintpass`, draws depth outlines
(`overlay` draws crisp lettering after the painterly pass). Same camera as every background.
```
python3 ambra_bg.py <outdir>     # -> ambra.png = assets/images/backgrounds/ScraperAmbra.png (Dr. Elphi's studio, ScraperAmbraScene)
aseprite -b --script-param img=<png> --script-param out=assets/aseprite/<Name>_1067x600.aseprite --script-param "layer=<NAME> pozadi (Claude)" --script tools/artgen/bg_source.lua   # first build of a source
```
ARB Ambra fixed points: Elphi stands at canvas (745, 510) (feet, origin bottom, scale 0.08) in front of her desk; the
exit to the elevator is the bottom edge (behind the camera); the walk line is y 534.

## Egg Cathedral entrance (CathedralEntrance)
The user's composition (`cathedral_ref.png`, painted 2026-10-18) rebuilt on `raster3d` through a long lens (`raster3d.F`
patched to 1200, the facade at ~70 units) so it stays frontal like the drawing: coursed ashlar (`masonry()`: merged
block lengths, sunk joints, lit arrises, dirty / replaced blocks), the portal's stepped orders + hood mould as one arch
family (`arch_w()` = a radial coordinate across the orders), round sandstone towers with slate spires (`cylinder()` /
`cone()` built from facets), rubble aisles, grey buttresses, the eggshell halves. The stained glass, the tympanum's glow
pattern and the shell's silhouette and holes are read from `cathedral_ref.png`, so the user's art stays as drawn.
```
python3 cathedral_bg.py <outdir>     # -> cathedral.png = assets/images/backgrounds/CathedralEntrance.png
```
Source `assets/aseprite/CathedralEntrance_1067x600.aseprite` (UPRAVY layer). Fixed points: the guard on the second
step (feet y 508, centred), the walk line y 534, the glowing tympanum y ~240-312 (the examine hotspot).

## Shed 521 grounds (gate, mutation courtyard, registration yard)
`shedkit.py` = the shared kit on `raster3d`: the overcast sky, world-space materials in the Crossroad palette
(`planks`, `corrugated`, `steel`, `concrete`, `setts`, `windows_sh`), queue stanchions, and people drawn with the
character renderer (`applicant_img` / `applicant`: hooded applicants, some with a mushroom cap, coral knobs or a gas
mask; standing or seated; front, back or profile), `mushroom_img` / `mushroom` (giant mushrooms -- not used: no
mushrooms without a reason in the world) and `statue` (mossy stone applicants on plinths). Drawn figures go into the scene as depth-sized sprites (`Raster.sprite`).
```
python3 gate_bg.py <outdir>          # -> gate.png         = assets/images/backgrounds/Shed521_gate.png (Shed521GateScene)
python3 courtyard_bg.py <outdir>     # -> courtyard.png    = ShedMutationCourtyard.png (ShedCourtyardScene)
python3 registration_bg.py <outdir>  # -> registration.png = ShedRegistrationZone.png (ShedRegistrationScene)
python3 floors_bg.py <outdir>        # -> floors.png       = Shed521_floors.png (Shed521FloorsScene): a cut-away of the bureau's
                                     #    three floors through a long lens (raster3d.F patched to 3000), floor lines y 520/340/180
```
Kit extras: `facade()` (tenement walls: glass with the sky in it, lit / shuttered / boarded / broken / curtained windows,
sills, grime runs, drainpipes) + `balconies()`; `mutant_img` / `bizarre_statue` (approved mutations in stone: six arms,
three heads, tentacles, antlers, a snail shell with a claw, a head of eyes, stilts); `Raster.render(mirror=...)` makes
wet ground reflect the scene (a screen-space march up the column from the eye mirrored under the floor). The burning
barrel at the gate is the animated GD prop placed unconditionally with `placeProps()` (utils/GDProps.js).
Sources `assets/aseprite/{Shed521_gate,ShedMutationCourtyard,ShedRegistrationZone,Shed521_floors}_1067x600.aseprite` (UPRAVY layer).
Fixed points: the Floors door on the gate's near right (exit right); Ortolan at canvas (600, 526) in the courtyard;
the dream queue around canvas x 363..703 (feet y 522) and the Senior Clerk at (533, 522) in the registration yard.

## The people on the Floors (Shed521FloorsScene)
The Floors background has no people baked in (only empty benches); the WELCOME clerk, a dozer on the ground-floor bench
and the four-strong queue at APPLICATIONS are animated sprites: `applicant_img` with its pose knobs (`bob`, `lean`,
`nod`, `face='front'`, `hands`, `papers`/`page`, `stamp`; all zero = the still figure the other backgrounds use).
`floorsfolk.py` imports `floors_bg.py`'s geometry (that one renders only when run as a script) and cuts out of every
frame whatever is nearer in its depth buffer -- the counter, the bench seat, the top floor's slab edge and railing.
```
python3 floorsfolk.py <outdir>       # -> <id>.png sheets (128 wide; welcome_clerk 8 frames, dozer 7 × 128×80, queue0..3 6 each)
                                     #    + <id>/<n>.png + <id>/durations.txt + floorsfolk.gpl; prints anchors, heights, holds
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite --script-param pal=$HOME/.config/aseprite/palettes/floorsfolk.gpl --script tools/artgen/floorsfolk_aseprite.lua
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters/shedfloors --script tools/artgen/floorsfolk_export.lua
```
Sources `assets/aseprite/ShedFloors_<id>.aseprite` (tag idle, frame hold times, UPRAVY layer). The scene's
`FLOORS_FOLK` table holds the printed anchors / heights / holds; `utils/AmbientNpc.js` plays them (frames repeated in
100 ms ticks: Phaser 3.88 ignores per-frame durations) and a click shows a line from `lang/<code>/ambient.js`.

## The dream queue (Sleepless Mime, Vowel Seller, Hollow Woman — ShedRegistrationScene)
Same renderer as the protagonist (`rig.py`). `python3 dreamqueue.py <outdir>` → `mime.png`, `vowel_seller.png`,
`hollow_woman.png` (6 idle frames of 128×160 each, facing the viewer, feet on y 156) + `dreamqueue.gpl`. Then
```
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite --script-param pal=$HOME/.config/aseprite/palettes/dreamqueue.gpl --script tools/artgen/dreamqueue_aseprite.lua
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters/dreamqueue --script tools/artgen/dreamqueue_export.lua
```
Sources `assets/aseprite/DreamQueue_<id>.aseprite` (tag ceka, UPRAVY layer). The scene keeps the texture keys
`sleeplessMime` / `vowelSeller` / `hollowWoman`, shows them at scale 1 (anims dq_mime / dq_vowel / dq_hollow) and uses
2× busts from the sheets as dialog portraits (`dialogPortraits` `{ key, frame, zoom, top }`, EN + CZ speaker names).

## Applications office + its clerk (ShedApplicationsScene)
```
python3 applications_bg.py <outdir>  # -> applications.png = ShedApplications.png (the Bureau's paperwork office: drop ceiling,
                                     #    cubicles with green-screen terminals, filing cabinets, pneumatic-tube post, the clerk's desk)
python3 clerk.py <outdir>            # -> clerk.png (8 idle frames of 128×176: breath, glasses pushed up, a page leafed, pen taps) + clerk.gpl
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite --script-param pal=$HOME/.config/aseprite/palettes/clerk.gpl --script tools/artgen/clerk_aseprite.lua
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters --script tools/artgen/clerk_export.lua
```
Sources `assets/aseprite/ShedApplications_1067x600.aseprite`, `assets/aseprite/Shed_clerk_applications.aseprite` (UPRAVY layers).
The clerk stands at canvas (250, 526) (origin bottom) in front of his desk; the doors to the Floors are on the left wall
and the right wall near the front (exits at x ≈ 67 and 867). Portrait = a 2× bust (`dialogPortraits`, EN + CZ name).

## The Senior Clerk (ShedRegistrationScene)
Same renderer (`rig.py`), redrawn after the old `clerk2.png`: a reptilian bureaucrat (scaly skull, a comb of spines webbed
with a rust membrane, slit-pupilled amber eyes, flat snout, clawed fingers — deliberately *not* a frog, no crown) in a
charcoal suit, a rubber stamp at his chest and a ledger at his side.
```
python3 senior_clerk.py <outdir>     # -> senior_clerk.png (8 idle frames of 128×192, facing the viewer, soles on y 189) + senior_clerk.gpl
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite --script-param pal=$HOME/.config/aseprite/palettes/senior_clerk.gpl --script tools/artgen/senior_clerk_aseprite.lua
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters --script tools/artgen/senior_clerk_export.lua
```
Source `assets/aseprite/Shed_senior_clerk.aseprite` (tag ceka, UPRAVY layer). Frames: 0 rest / 1 inhale + crest lifts /
2 blink / 3 a disdainful sniff / 4 tongue flick / 5 a glance left at the newcomer / 6-7 the ledger lifted and knocked square.
The scene loads it as `seniorClerk` (anim `senior_clerk_idle`, 4 fps), origin bottom at (533, 524); portrait = a 2× bust.
The old `clerk2.png` is unused.

## Edgar Eskola (ScreamingCorkScene)
Not redrawn from scratch — the bear must stay as he was. `edgar.py` box-filters the old `EdgarEskola.png` (1024×1536,
painted at ~16 px per "pixel", shown at 0.125) down to its native 128×192 grid and animates it by moving parts of
those pixels (the source's transparent eye glints are filled in as glints).
```
python3 edgar.py <outdir>            # -> edgar.png (8 idle frames of 128×192, soles on y 189) + edgar.gpl
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite --script-param pal=$HOME/.config/aseprite/palettes/edgar.gpl --script tools/artgen/edgar_aseprite.lua
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters --script tools/artgen/edgar_export.lua
```
Source `assets/aseprite/Edgar_eskola.aseprite` (tag ceka, UPRAVY layer). Frames: 0 rest / 1 breath / 2 blink /
3 ear twitch / 4-5 the bag sways / 6 head lowered / 7 head lowered, eyes shut. The scene keeps the key `edgarEskola`
(anim `edgar_idle`, 4 fps) at (300, 525), origin bottom; portrait = a 2× bust. `EdgarEskola.png` stays as the source.

## The Screaming Cork from the street (ScreamingCorkScene)
```
python3 cork_bg.py <outdir>          # -> cork.png = assets/images/backgrounds/ScreamingCork.png
```
On `raster3d` + `shedkit`, after the old art: the timber tavern seen close across the pavement — the main block
(name board painted with a TTF mask, DejaVu Serif Condensed Bold, peeling; falls back to the 3×5 font), the older
clapboard tower on the left with a dark archway through it (the exit left), the forward-stepping wing on the right with
the arched side door, U-bent vent pipes, red-lit cellar windows (the club), and the pub sign: a carved screaming cork
with a corkscrew in it. Source `assets/aseprite/ScreamingCork_1067x600.aseprite` (UPRAVY layer).
Fixed points: door centred on x 533 (sill y ~485); name board x 362..704, y 183..299 (the observable); archway
x 15..103; Edgar at (300, 525); the walk line y 534 runs along the pavement.

## Scraper 1140 (ScraperScene) — the old picture, re-pixelled, plus a rooftop
Not redrawn from scratch — the user loves the old AI picture. `scraper_bg.py` reads it from `scraper1140_ref.png`
(the original 1536×1024, kept here as the source): it is a 384×256 picture blown up 4×, so every 4×4 block is sampled
back to one logical pixel (block centres, x blocks start at 4g+1), the frame is cut to **356×200** (grid x 14..370,
y 0..200) and locked to one palette (k-means: 40 greens + 8 warm window tones + 4 sign creams + 3 foreground extras);
the two figures on the old walkway are painted out by exemplar inpainting from the haze around them. The foreground is
new and drawn at the same logical size: a wet tar roof with a duckboard walk and puddles that mirror the scene (the
centre one holds the tower's lit window; the mirrored ray sees the parapet / railing first, then the far plate), a
parapet with the railing and its sagging chain, the stair-house on the left with a caged lamp over its door, roof
clutter and an antenna mast cabled into the tower, a turbine vent and two drums, a clad heating pipe across the near
left, and a gate with a suspension footbridge whose hung lamps fade into the fog (no number plate on the gate —
the user had it removed: the tower already says 1140). Own eye level (the old
walkway's): horizon row 150 = canvas 450, the player's feet at row 178 = canvas 534 stand at depth 15; units: the
player is 6.4 tall, the eye 4.2. The game shows it 3× (356 × 3 = 1068, cropped to 1067×600).
```
python3 scraper_bg.py <outdir> [reuse]   # -> plate.png bridge.png fg.png (356x200 layers), scraper.png (1067x600),
                                         #    chars.png + guides.png overlays, scraper.gpl; reuse = keep <outdir>/plate_raw.png
cp <outdir>/scraper.gpl ~/.config/aseprite/palettes/scraper.gpl
# build the Aseprite source (OVERWRITES assets/aseprite/Scraper1140_356x200.aseprite, incl. its UPRAVY layer):
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite \
        --script-param pal=$HOME/.config/aseprite/palettes/scraper.gpl --script tools/artgen/scraper_aseprite.lua
# export into the game (merges UPRAVY, 3x hard pixels) -- run this after hand edits in Aseprite:
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/backgrounds --script tools/artgen/scraper_export.lua
```
Source `assets/aseprite/Scraper1140_356x200.aseprite` — edit it at the logical size, one Aseprite pixel = 3×3 in the
game. Layers: `ORIGINAL precisteny`, `LAVKA + BRANA` (gate, footbridge, its lamps), `POPREDI`, `UPRAVY - kresli sem`,
hidden `POSTAVY meritko` + `VODITKA` (hit zones, walk line) — the export skips the two `neexportovat` layers.
Fixed points (canvas): the gate centred on x 533 (pylons 497..568, top y ~378) = "Enter Scraper"; the stair-house
door x 21..77 (sill y ~525) = the exit left to the Crossroad; the sign x ~510..690, y ~90..205 (the observable);
Don Girandole on the pipe-tower platform at the right edge (deck y ~378, sprite centre (1018, 301)).

## Inside the Screaming Cork (ScreamingCorkInteriorScene): the taproom, Heliodor, Ravla
```
python3 corkin_bg.py <outdir>        # -> corkin.png = ScreamingCorkInterior.png, counter.png = ScreamingCorkInterior_counter.png
python3 corkfolk.py <outdir>         # -> heliodor.png (8 × 128×192), ravla.png (8 × 128×128) + corkfolk.gpl
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite --script-param pal=$HOME/.config/aseprite/palettes/corkfolk.gpl --script tools/artgen/corkfolk_aseprite.lua
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters --script tools/artgen/corkfolk_export.lua   # -> <id>_idle.png
```
The taproom on `raster3d`: a tall timber hall, a stuffed cephalopod over the back bar (drawn with `rig.py`, pasted with
`Raster.sprite`), the name in red neon (TTF mask, DejaVu Sans Condensed Bold), bottle shelves before a clouded mirror,
the counter in front, the street door in the left wall (exit left, x ~28..122), the club doorway at the back right
(stairs down in red light, x ~817..882, y ~321..425) with a Feral Toast bill, lanterns, round tables, Ravla's desk and
candle in the right corner. `counter.png` = every pixel nearer than Heliodor (z 17.3) inside his sprite's box; the
scene draws it at depth 5.5 over him (depth 5). Heliodor at (533, 492) before the curtained doorway between the
back-bar cabinets, Ravla at (960, 524), both origin bottom.
`corkfolk.py` treats the people like `edgar.py`: the old `heliodor.png` / `ravla.png` box-filtered 8× to their native
grid and animated by moving / relighting their own pixels (the old PNGs stay as the sources). Sources
`assets/aseprite/Cork_heliodor.aseprite`, `Cork_ravla.aseprite`, `ScreamingCorkInterior_1067x600.aseprite` (UPRAVY layers).

## The club under the Screaming Cork (ScreamingCorkClubScene)
```
python3 club_bg.py <outdir>          # -> club.png = assets/images/backgrounds/ScreamingCorkClub.png
```
A brick cellar under a shallow barrel vault (`vault_y()`, strips on `raster3d`), brick ribs at z 21 / 25, the plank
stage wall to wall (front edge z 16.6, 1.8 high) for the Feral Toast sprites (feet y 470 / 452, x shares in the scene's
BAND), the painted cloth banner (TTF mask, DejaVu Sans Condensed Bold), a ring of salvaged speaker cones over it (the
Noise God's altar, a few breathing green), three industrial lamps whose shades end at y 118 over x 272 / 515 / 787
(the scene's light cones start there), amp stacks, a backstage door in the left wall, a gig bill.
Source `assets/aseprite/ScreamingCorkClub_1067x600.aseprite` (UPRAVY layer).

## Re-pixelled AI backgrounds kept as they are (`repix.py`): the abandoned office, the first view of the city
For old pictures the user wants kept (like Scraper 1140) but whose block grid is irregular (~4.5-6 px): `repix.py`
resamples the whole source width onto **356 logical columns** (square cells), each cell taking the MOST COMMON colour of
its middle (crisp letters and edges, no blended seams) on a palette built per colour family (`family_palette`: small but
important families keep their own ramps), then the frame is a 200-row cut shown 3x like Scraper 1140.
```
python3 office_bg.py <outdir>   # ShedAbandonedOffice: office_ref.png kept 1:1 (the graffito BETTER DECAY THAN CHANGE has its
                                #   own maroon paint ramp), rows 13..213 so the graffito clears the HUD buttons -> office_356.png
python3 entry_bg.py <outdir>    # EntryScene: city_ref.jpg (rows 0..200: storm sky, the egg, the Scraper's needle) + a new
                                #   overlook in front (wet flagstones, a stone balustrade with a broken stretch, ivy, a signpost
                                #   with a painted egg pointing right to the Cathedral) -> plate.png + fg.png
# generic logical-size sources (356x200, UPRAVY + hidden figures/guides) and their 3x export:
aseprite -b --script-param dir=<outdir> --script-param "layers=a.png|LAYER A;b.png|LAYER B" --script-param out=assets/aseprite/<Name>_356x200.aseprite \
        --script-param pal=$HOME/.config/aseprite/palettes/<pal>.gpl --script tools/artgen/logical_aseprite.lua
aseprite -b --script-param f=assets/aseprite/<Name>_356x200.aseprite --script-param out=assets/images/backgrounds/<Name>.png --script tools/artgen/logical_export.lua
```
Sources: `ShedAbandonedOffice_356x200.aseprite` (layer `ORIGINAL precisteny`), `EntryCity_356x200.aseprite` (`ORIGINAL precisteny`
+ `POPREDI`). The city is now `assets/images/backgrounds/EntryCity.png` (GameScene's `cityBackground`, ScraperAmbra's
dream panels `cs_city`); `city.jpg` is no longer loaded. Palettes `office.gpl`, `entry.gpl` (copies here).
Fixed points: office -- the back doorway (canvas x 417..521, y 127..281) = "To the Hall", the left edge = back to the
stairs, the bare-brick patch by the graffito wall (662, 212) = Palinode's bricked tunnel; city -- Master Thaal at
(600, 530), the overlook's walk line y 534, the exit at the right edge (the signpost at x ~911 points to it).

## The Hall under Shed 521 (ShedHallScene) and the Scraper's lobby (ScraperInteriorScene) — raster3d interiors
```
python3 hall_bg.py <outdir>    # -> hall.png  = ShedHall.png: a low service hall, the old corridor now the tunnel off into the
                               #    dark (stencilled 521 over it), the Living Core's iron socket fused into the back wall with
                               #    roots of living metal over the wall and floor (veins glowing), the steel door back (exit sign)
python3 lobby_bg.py <outdir>   # -> lobby.png = Scraper_interior.png: the Nexicorp art-deco lobby -- the Lift-Mother's arched
                               #    bronze portal (a mask with closed eyes, an arc of amber lamps, LIFT-MOTHER), the SCRAPER 1140
                               #    plaque + the backyard door, the stair up, the street doors (daylight), a concierge desk
aseprite -b --script-param img=<png> --script-param out=assets/aseprite/<Name>_1067x600.aseprite --script-param "layer=<NAME> pozadi (Claude)" --script tools/artgen/bg_source.lua
```
Sources `ShedHall_1067x600.aseprite`, `Scraper_interior_1067x600.aseprite` (UPRAVY layer). Fixed points: hall -- the Core
sprite at (683, 376) in its socket, the door back to the office x 71..162; lobby -- the lift portal x 459..561, y 263..434
(hit area centred (510, 350)), the backyard door x 648..706 (zone 800-space (507, 390)), the street doors x 33..169.

## The skyship Verdigrace: the look-up cut (skyship.png) and its deck (SkyshipBoardScene)
```
python3 skyship_bg.py <outdir>   # -> skyship_356.png + skyship.png: skyship_ref.png (portrait) re-pixelled onto 190 columns,
                                 #    rows 22..222, centred in a 356x200 frame whose sides are new sky carrying on the source's
                                 #    own sky row by row (colour smoothed down the rows, cloud banks lower down); stars removed
python3 board_bg.py <outdir>     # -> board.png = skyship_board.png (raster3d): the gondola deck under the bladder's netted,
                                 #    spore-lit underside; the bulwark with living-wood balusters curving to the fiddlehead stem
                                 #    (lantern), the rope ladder by the bow, the grown dial-board, the cabin, stanchions with pods;
                                 #    beyond the rail the emerald overcast, a cloud sea, the city far below (the Scraper, the Egg)
aseprite -b --script-param dir=<outdir> --script-param "layers=skyship_356.png|LOD + OBLOHA (Claude)" --script-param out=assets/aseprite/Skyship_356x200.aseprite \
        --script-param pal=$HOME/.config/aseprite/palettes/skyship.gpl --script tools/artgen/logical_aseprite.lua
aseprite -b --script-param f=assets/aseprite/Skyship_356x200.aseprite --script-param out=assets/images/backgrounds/skyship.png --script tools/artgen/logical_export.lua
aseprite -b --script-param img=<outdir>/board.png --script-param out=assets/aseprite/SkyshipBoard_1067x600.aseprite --script-param "layer=PALUBA pozadi (Claude)" --script tools/artgen/bg_source.lua
```
The cut (CrossroadScene.startSkyshipAnimation) pins the picture to the screen (scrollFactor 0) and scales it by
1/camera.zoom when it fades in, so it lands pixel-exact on the zoomed camera; the message box sits under the ship.
`paintpass.paint(sheen_gain=...)` (default 1.0) was added for the deck: its damp-patch sheen read as spilt paint on the
planks. Deck fixed points: the rope ladder x ~118 (exit zone 40..160), the dial-board's lens (533, 403) (observable
800-space (400, 420, 80, 110)), Captain Liris at (700, 466) scale 0.1 (feet on the walk line), the cabin from x 826.

## Captain Liris (SkyshipBoardScene) — redrawn; Ortolan + Dr. Elphi — their old art animated
```
python3 liris.py <outdir>          # -> liris.png (8 idle frames of 128x160, soles on y 156) + liris.gpl -- rig.py: a teal hood, a brass
                                   #    monocle with an amber lens, a brick-red scarf, a long brown coat, olive tunic, spyglass, boots;
                                   #    0 rest 1 inhale 2 blink 3 the lens clicks 4-5 a gust (scarf + hem) 6 a hand to the monocle 7 settle
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite --script-param pal=$HOME/.config/aseprite/palettes/liris.gpl --script tools/artgen/liris_aseprite.lua
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters --script tools/artgen/liris_export.lua   # -> liris_idle.png
python3 ortolan_elphi.py <outdir>  # like corkfolk.py (box filter onto the source's own grid, the old pixels moved/relit):
                                   #    ortolan 128x160 (Ortolan.png /8), ortolan4 144x160 (ortolan4.png /6, same height), elphi 128x160
                                   #    (DrElphi.png /11, the soft white halo dropped, the hologram kept and animated); 8 frames each
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite --script-param pal=$HOME/.config/aseprite/palettes/ortolan_elphi.gpl --script tools/artgen/ortolan_elphi_aseprite.lua
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters --script tools/artgen/ortolan_elphi_export.lua   # -> ortolan_idle.png ortolan4_idle.png elphi_idle.png
```
Sources `Sky_liris.aseprite`, `Ortolan_idle.aseprite`, `Ortolan4_idle.aseprite`, `Elphi_idle.aseprite` (tag ceka, UPRAVY layer).
In the scenes: new texture keys `captainLiris` (sheet), `ortolanIdle` / `ortolan4Idle`, `drElphiIdle` (the old `drElphi` image
stays loaded for ScraperAmbra's cutscene panels); all at scale 1, origin bottom, anims `liris_idle`, `ortolan_idle`,
`ortolan4_idle`, `elphi_idle` (4 fps, frames repeated for timing); hover = a preFX glow, never scaling; the old bobbing /
tilting tweens and green glow discs are gone. Liris has a 2x bust portrait (EN "Captain Liris" + CZ "Kapitánka Liris").

## Fast-travel map (ui/MapUI.js, texture `mapBg`)
`map_bg.py` draws the map at a native 400×300 (MapUI shows it 2× with hard pixels — the game runs with `pixelArt: true`).
Node `x,y` in MapUI (800×600 panel, centre 0,0) is pixel `((x + 400) / 2, (y + 300) / 2)` here: each landmark stands
`LIFT[k]` px above its node so MapUI's circle marks its doorstep, the label zone under every node stays free of filler,
and the roads (`ROADS`) mirror `MapUI.connections` — MapUI draws no straight lines over the art. One node per place:
rooms and floors inside it (Dr. Elphi's studio + the Rust Domain in the Scraper, the whole Shed 521 compound, …) are in
the location's `inside` list in MapUI, have no landmark of their own and show "you are here" on the building. Places
the player hasn't visited get no marker and no label (the building is still drawn). **Moving a node = change it in both
`N` here and `locations` in MapUI.js.** Palette `map.gpl` (a copy is kept here; install with
`cp map.gpl ~/.config/aseprite/palettes/`).
```
python3 map_bg.py <outdir>       # -> map.png, map.gpl, layers/<name>.png, map_preview.png (4x)
# build the Aseprite source (OVERWRITES assets/aseprite/UI_Map_400x300.aseprite, incl. its UPRAVY layer):
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite \
        --script-param pal=$HOME/.config/aseprite/palettes/map.gpl --script tools/artgen/map_aseprite.lua
# export into the game (merges UPRAVY, skips the hidden guides) -- run this after hand edits in Aseprite:
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/ui --script tools/artgen/map_export.lua
```
Layers: ground, water, roads, shadows, forests + town, landmarks, lights, **UPRAVY - kresli sem** (under the vignette, so
hand edits get the same edge shading), vignette (translucent black), frame; `VODITKA … (neexportovat)` is hidden: red
rings = MapUI node circles, cyan boxes = their labels, yellow lines = title band / legend band.

## Inventory icons (the demo items that had the lettered-circle placeholder)
`item_icons.py` draws 60×60 icons (transparent, shown 1:1) in the look of the hand-drawn key / Oltrac jars / cartridge:
light from the top left, a 1 px dark outline; families share helpers (official forms = paper + header + stamp, Ortolan's
gifts = game pieces). File name = item id; `utils/itemIcons.js` registers them (LoadingScene loads them game-wide).
```
python3 item_icons.py <outdir>       # -> <id>.png per icon, icons.txt (frame order), sheet.png (4x preview)
# build the Aseprite source (OVERWRITES assets/aseprite/UI_ItemIcons_60x60.aseprite, incl. its UPRAVY layer):
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite --script tools/artgen/item_icons_aseprite.lua
# export into the game (merges UPRAVY; one PNG per frame tag = item id) -- run this after hand edits in Aseprite:
aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/items --script tools/artgen/item_icons_export.lua
```
A new icon = a function + a line in `ICONS`, then a line in `utils/itemIcons.js`.
