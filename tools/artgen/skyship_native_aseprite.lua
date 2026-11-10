-- Builds the Aseprite source of the skyship look-up cut (CrossroadScene, skyship.png) from a skyship_native_bg.py render:
-- the generated picture, an empty UPRAVY layer for hand edits, and a hidden guide layer with the cut's message box.
-- aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite --script-param pal=$HOME/.config/aseprite/palettes/skyship_native.gpl --script tools/artgen/skyship_native_aseprite.lua
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local spr = Sprite(1067, 600, ColorMode.RGB)
local base = spr.layers[1]; base.name = "LOD pohled zdola (Claude)"
spr:newCel(base, 1, Image{ fromFile = d .. "/skyship.png" }, Point(0, 0))
local paint = spr:newLayer(); paint.name = "UPRAVY - kresli sem"
local g = spr:newLayer(); g.name = "VODITKA box se zpravou (neexportovat)"
spr:newCel(g, 1, Image{ fromFile = d .. "/guides.png" }, Point(0, 0)); g.isVisible = false; g.isEditable = false
spr:loadPalette(pal)
app.activeLayer = paint
spr:saveAs(o .. "/Skyship_1067x600.aseprite")
print("ok")
