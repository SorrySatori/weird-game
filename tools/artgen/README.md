# artgen — procedural pixel-art background generators

Python 3 + Pillow. Each `*_bg.py` renders a native 1067×600 background (overcast day, one-point perspective,
vanishing point (533, 296), focal length 300, camera height 12 world units — the player is ≈6.4 units tall,
feet on y 534). `pal_day.py` is the shared palette (exported as the Aseprite palette `crossroad-overcast.gpl`, a copy is
kept here; install it with `cp crossroad-overcast.gpl ~/.config/aseprite/palettes/`); `common.py` has noise, banding, the 3×5 pixel font.

```
python3 crossroad_bg.py <outdir>       # -> <outdir>/bg.png
python3 crossroad_corpse.py <outdir>   # -> corpse_0..2.png + crossroad_corpse.png (3-frame sheet 240×440)
python3 shed521_bg.py <outdir> [base|growth|decay]   # -> bg.png / bg_growth.png / bg_decay.png (Growth/Decay variants)
python3 props.py <outdir>              # -> prop_*.png Growth/Decay scenery props (assets/images/props/, placed by utils/GDProps.js)
python3 <scene>_guides.py <outdir>     # hotspot guide layer for the Aseprite template
aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite \
        --script-param pal=~/.config/aseprite/palettes/crossroad-overcast.gpl --script <scene>_aseprite.lua
```
`chars.png` is the character-scale overlay layer used in the templates. Regenerate from here rather than
hand-editing the PNGs; hand touch-ups go into the "UPRAVY" layer of the `.aseprite` files.
