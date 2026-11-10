-- Builds the Aseprite source of the hand-drawn fast-travel map (1067x600, shown 1:1 by MapUI).
-- aseprite -b --script-param dir=<outdir of handmap.py> --script-param out=assets/aseprite [--script-param color=1] \
--         --script tools/artgen/map_aseprite.lua
-- color=1 builds the felt-tip coloured version (UI_Map_barevna_1067x600.aseprite, BARVY layer in Multiply mode;
-- needs `handmap.py --color`), else the black-and-white one (UI_Map_1067x600.aseprite). OVERWRITES it, UPRAVY included.
local d, o, col = app.params["dir"], app.params["out"], app.params["color"] == "1"
local s = Sprite(1067, 600, ColorMode.RGB)
local function add(layer, name, file)
  layer.name = name
  s:newCel(layer, 1, Image{ fromFile = d .. "/layers/" .. file .. ".png" }, Point(0, 0))
  return layer
end
add(s.layers[1], "PAPIR (Claude)", "papir")
if col then add(s:newLayer(), "BARVY - fixy (Claude)", "barvy").blendMode = BlendMode.MULTIPLY end
add(s:newLayer(), "SKICA (tvoje kresba)", "skica")
add(s:newLayer(), "DOKRESLENO (Claude)", "dokresleno")
local up = s:newLayer(); up.name = "UPRAVY - kresli sem"
app.activeLayer = up
s:saveAs(o .. (col and "/UI_Map_barevna_1067x600.aseprite" or "/UI_Map_1067x600.aseprite"))
s:close()
print("ok")
