-- Builds the Aseprite source of the Captain Liris (skyship deck) from liris.py.
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script liris_aseprite.lua
-- Draw touch-ups into the "UPRAVY" layer; liris_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local s = Sprite(128, 160, ColorMode.RGB)
local base = s.layers[1]; base.name = "liris"
for i = 1, 8 do
  if i > 1 then s:newEmptyFrame() end
  s:newCel(base, i, Image{ fromFile = d .. "/liris/" .. (i - 1) .. ".png" }, Point(0, 0))
  s.frames[i].duration = 0.25
end
local tag = s:newTag(1, 8); tag.name = "ceka (dech, mrk, monokl, vitr, ruka k monoklu)"
local up = s:newLayer(); up.name = "liris UPRAVY"
s:loadPalette(pal)
app.activeLayer = up
s:saveAs(o .. "/Sky_liris.aseprite")
s:close()
print("ok")
