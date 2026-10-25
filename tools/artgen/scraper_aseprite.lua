-- Builds the Aseprite source of the Scraper 1140 background at its logical size (356x200; the game shows it 3x).
-- aseprite -b --script-param dir=<outdir of scraper_bg.py> --script-param out=assets/aseprite \
--         --script-param pal=$HOME/.config/aseprite/palettes/scraper.gpl --script tools/artgen/scraper_aseprite.lua
-- OVERWRITES assets/aseprite/Scraper1140_356x200.aseprite (incl. its UPRAVY layer) -- to refresh one generated layer
-- of an existing source use bg_update.lua instead.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local s = Sprite(356, 200, ColorMode.RGB)
local plate = s.layers[1]; plate.name = "ORIGINAL precisteny (Claude)"
s:newCel(plate, 1, Image{ fromFile = d .. "/plate.png" }, Point(0, 0))
local br = s:newLayer(); br.name = "LAVKA + BRANA (Claude)"
s:newCel(br, 1, Image{ fromFile = d .. "/bridge.png" }, Point(0, 0))
local fg = s:newLayer(); fg.name = "POPREDI (Claude)"
s:newCel(fg, 1, Image{ fromFile = d .. "/fg.png" }, Point(0, 0))
local up = s:newLayer(); up.name = "UPRAVY - kresli sem"
local ch = s:newLayer(); ch.name = "POSTAVY meritko (neexportovat)"
s:newCel(ch, 1, Image{ fromFile = d .. "/chars.png" }, Point(0, 0)); ch.isVisible = false; ch.isEditable = false
local g = s:newLayer(); g.name = "VODITKA (neexportovat)"
s:newCel(g, 1, Image{ fromFile = d .. "/guides.png" }, Point(0, 0)); g.isVisible = false; g.isEditable = false
s:loadPalette(pal)
s.gridBounds = Rectangle(0, 0, 8, 8)
app.activeLayer = up
s:saveAs(o .. "/Scraper1140_356x200.aseprite")
s:close()
print("ok")
