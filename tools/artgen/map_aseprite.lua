-- Builds the Aseprite source of the fast-travel map at its logical size (400x300; MapUI shows it 2x).
-- aseprite -b --script-param dir=<outdir of map_bg.py> --script-param out=assets/aseprite \
--         --script-param pal=$HOME/.config/aseprite/palettes/map.gpl --script tools/artgen/map_aseprite.lua
-- OVERWRITES assets/aseprite/UI_Map_400x300.aseprite (incl. its UPRAVY layer) -- to refresh one generated layer
-- of an existing source use bg_update.lua instead.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local s = Sprite(400, 300, ColorMode.RGB)
local function add(layer, name, file)
  layer.name = name
  s:newCel(layer, 1, Image{ fromFile = d .. "/layers/" .. file .. ".png" }, Point(0, 0))
  return layer
end
add(s.layers[1], "ZEME (Claude)", "zeme")
add(s:newLayer(), "VODA (Claude)", "voda")
add(s:newLayer(), "CESTY (Claude)", "cesty")
add(s:newLayer(), "STINY (Claude)", "stiny")
add(s:newLayer(), "LESY + MESTO (Claude)", "mesto")
add(s:newLayer(), "MISTA (Claude)", "mista")
add(s:newLayer(), "SVETLA (Claude)", "svetla")
local up = s:newLayer(); up.name = "UPRAVY - kresli sem"
add(s:newLayer(), "VINETA (Claude)", "vineta")
add(s:newLayer(), "RAMECEK (Claude)", "ramecek")
local g = add(s:newLayer(), "VODITKA uzly+popisky (neexportovat)", "voditka")
g.isVisible = false; g.isEditable = false
if pal and pal ~= "" then s:loadPalette(pal) end
s.gridBounds = Rectangle(0, 0, 8, 8)
app.activeLayer = up
s:saveAs(o .. "/UI_Map_400x300.aseprite")
s:close()
print("ok")
