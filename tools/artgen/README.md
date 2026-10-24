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

## Shed 521 grounds (gate, mutation courtyard, registration yard)
`shedkit.py` = the shared kit on `raster3d`: the overcast sky, world-space materials in the Crossroad palette
(`planks`, `corrugated`, `steel`, `concrete`, `setts`, `windows_sh`), queue stanchions, and people drawn with the
character renderer (`applicant_img` / `applicant`: hooded applicants, some with a mushroom cap, coral knobs or a gas
mask; standing or seated; front, back or profile), `mushroom_img` / `mushroom` (giant mushrooms) and `statue` (mossy
stone applicants on plinths). Drawn figures go into the scene as depth-sized sprites (`Raster.sprite`).
```
python3 gate_bg.py <outdir>          # -> gate.png         = assets/images/backgrounds/Shed521_gate.png (Shed521GateScene)
python3 courtyard_bg.py <outdir>     # -> courtyard.png    = ShedMutationCourtyard.png (ShedCourtyardScene)
python3 registration_bg.py <outdir>  # -> registration.png = ShedRegistrationZone.png (ShedRegistrationScene)
```
Sources `assets/aseprite/{Shed521_gate,ShedMutationCourtyard,ShedRegistrationZone}_1067x600.aseprite` (UPRAVY layer).
Fixed points: the Floors door on the gate's near right (exit right); Ortolan at canvas (600, 526) in the courtyard;
the dream queue around canvas x 363..703 (feet y 522) and the Senior Clerk at (533, 522) in the registration yard.
