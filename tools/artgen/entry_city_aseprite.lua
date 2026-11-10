-- Builds the Aseprite source of the first view of the city (EntryScene) from an entry_city_bg.py render:
-- the generated background, an empty UPRAVY layer for hand touch-ups, and the hidden scale / guide layers.
-- aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite \
--         --script-param pal=$HOME/.config/aseprite/palettes/entry_city.gpl --script tools/artgen/entry_city_aseprite.lua
-- (OVERWRITES assets/aseprite/EntryCity_1067x600.aseprite incl. its UPRAVY layer; to swap only the base image of an
--  existing source use bg_update.lua with layer="MESTO pozadi (Claude)")
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local spr = Sprite(1067, 600, ColorMode.RGB)
local base = spr.layers[1]; base.name = "MESTO pozadi (Claude)"
spr:newCel(base, 1, Image{ fromFile = d .. "/entry_city.png" }, Point(0, 0))
local paint = spr:newLayer(); paint.name = "UPRAVY - kresli sem"
local ch = spr:newLayer(); ch.name = "POSTAVY meritko (neexportovat)"
spr:newCel(ch, 1, Image{ fromFile = d .. "/chars.png" }, Point(0, 0)); ch.isVisible = false; ch.isEditable = false
local g = spr:newLayer(); g.name = "VODITKA (neexportovat)"
spr:newCel(g, 1, Image{ fromFile = d .. "/guides.png" }, Point(0, 0)); g.isVisible = false; g.isEditable = false
if pal and pal ~= "" then spr:loadPalette(pal) end
app.activeLayer = paint
spr:saveAs(o .. "/EntryCity_1067x600.aseprite")
print("ok")
