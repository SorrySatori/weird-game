-- Builds the Aseprite source of the native Scraper 1140 background (scraper_native_bg.py), 1067x600, 1 px = 1 px in the game.
-- aseprite -b --script-param dir=<outdir of scraper_native_bg.py> --script-param out=assets/aseprite \
--         --script-param pal=$HOME/.config/aseprite/palettes/scraper_native.gpl --script tools/artgen/scraper_native_aseprite.lua
-- OVERWRITES assets/aseprite/Scraper1140_1067x600.aseprite (incl. its UPRAVY layer) -- to refresh only the generated layer
-- of an existing source use bg_update.lua with layer "SCRAPER 1140 pozadi (Claude)".
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local spr = Sprite(1067, 600, ColorMode.RGB)
local base = spr.layers[1]; base.name = "SCRAPER 1140 pozadi (Claude)"
spr:newCel(base, 1, Image{ fromFile = d .. "/scraper.png" }, Point(0, 0))
local paint = spr:newLayer(); paint.name = "UPRAVY - kresli sem"
local ch = spr:newLayer(); ch.name = "POSTAVY meritko (neexportovat)"
spr:newCel(ch, 1, Image{ fromFile = d .. "/chars.png" }, Point(0, 0)); ch.isVisible = false; ch.isEditable = false
local g = spr:newLayer(); g.name = "VODITKA (neexportovat)"
spr:newCel(g, 1, Image{ fromFile = d .. "/guides.png" }, Point(0, 0)); g.isVisible = false; g.isEditable = false
if pal and pal ~= "" then spr:loadPalette(pal) end
app.activeLayer = paint
spr:saveAs(o .. "/Scraper1140_1067x600.aseprite")
spr:close()
print("ok")
