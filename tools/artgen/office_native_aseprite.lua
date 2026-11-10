-- Builds the Aseprite source of the abandoned office in Shed 521 (ShedAbandonedOfficeScene), native 1067x600: the
-- generated background, an empty UPRAVY layer to paint on, and two hidden reference layers (the priest for scale; the
-- hotspots, Palinode's bricked opening, the walk line, the horizon and the HUD buttons).
-- aseprite -b --script-param dir=<outdir of office_native_bg.py> --script-param out=assets/aseprite \
--         --script-param pal=$HOME/.config/aseprite/palettes/office-native.gpl --script tools/artgen/office_native_aseprite.lua
-- OVERWRITES assets/aseprite/ShedAbandonedOffice_1067x600.aseprite (incl. its UPRAVY layer) -- to refresh only the
-- generated layer of an existing source use bg_update.lua with layer="KANCELAR pozadi (Claude)".
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local spr = Sprite(1067, 600, ColorMode.RGB)
local base = spr.layers[1]; base.name = "KANCELAR pozadi (Claude)"
spr:newCel(base, 1, Image{ fromFile = d .. "/office.png" }, Point(0, 0))
local paint = spr:newLayer(); paint.name = "UPRAVY - kresli sem"
local ch = spr:newLayer(); ch.name = "POSTAVY meritko (neexportovat)"
spr:newCel(ch, 1, Image{ fromFile = d .. "/chars.png" }, Point(0, 0)); ch.isVisible = false; ch.isEditable = false
local g = spr:newLayer(); g.name = "VODITKA (neexportovat)"
spr:newCel(g, 1, Image{ fromFile = d .. "/guides.png" }, Point(0, 0)); g.isVisible = false; g.isEditable = false
spr:loadPalette(pal)
app.activeLayer = paint
spr:saveAs(o .. "/ShedAbandonedOffice_1067x600.aseprite")
spr:close()
print("ok")
