-- Builds the Aseprite source of the Growth/Decay medallion (HUD) from gd_medallion.py.
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script gd_medallion_aseprite.lua
-- Frame k = growth 10*k %. Draw touch-ups into the "UPRAVY" layer; gd_medallion_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local s = Sprite(100, 100, ColorMode.RGB)
local base = s.layers[1]; base.name = "medailon"
for i = 1, 11 do
  if i > 1 then s:newEmptyFrame() end
  s:newCel(base, i, Image{ fromFile = d .. "/gd/" .. (i - 1) .. ".png" }, Point(0, 0))
  s.frames[i].duration = 0.3
end
local tag = s:newTag(1, 11); tag.name = "rust 0-100 %"
local up = s:newLayer(); up.name = "medailon UPRAVY"
s:loadPalette(pal)
app.activeLayer = up
s:saveAs(o .. "/UI_GrowthDecay_100.aseprite")
s:close()
print("ok")
