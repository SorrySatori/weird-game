-- Builds a fresh Aseprite source for a generated 1067x600 background: the base layer + an empty UPRAVY layer.
-- aseprite -b --script-param img=<png> --script-param out=assets/aseprite/<Name>_1067x600.aseprite --script-param "layer=<NAME> pozadi (Claude)" --script tools/artgen/bg_source.lua
local s = Sprite(1067, 600, ColorMode.RGB)
local base = s.layers[1]; base.name = app.params["layer"]
s:newCel(base, 1, Image{ fromFile = app.params["img"] }, Point(0, 0))
local up = s:newLayer(); up.name = "UPRAVY - kresli sem"
app.activeLayer = up
s:saveAs(app.params["out"])
s:close()
print("ok")
