# artgen — procedural pixel-art background generators

Python 3 + Pillow. Each `*_bg.py` renders a native 1067×600 background (overcast day, one-point perspective,
vanishing point (533, 296), focal length 300, camera height 12 world units — the player is ≈6.4 units tall,
feet on y 534). `pal_day.py` is the shared palette (exported as the Aseprite palette `crossroad-overcast.gpl`, a copy is
kept here; install it with `cp crossroad-overcast.gpl ~/.config/aseprite/palettes/`); `common.py` has noise, banding, the 3×5 pixel font.

```
python3 crossroad_bg.py <outdir>       # -> <outdir>/bg.png
python3 crossroad_corpse.py <outdir>   # -> corpse_0..2.png + crossroad_corpse.png (3-frame sheet 240×440)
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
