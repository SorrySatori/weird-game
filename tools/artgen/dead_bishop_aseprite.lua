-- Builds the Aseprite source of the dead Bishop (AbandonedBusScene) from dead_bishop.py.
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script dead_bishop_aseprite.lua
-- OVERWRITES assets/aseprite/Bus_dead_bishop.aseprite (incl. its UPRAVY layer).
-- Draw touch-ups into the "UPRAVY" layer; dead_bishop_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local s = Sprite(192, 88, ColorMode.RGB)
local base = s.layers[1]; base.name = "dead_bishop"
for i = 1, 5 do
  if i > 1 then s:newEmptyFrame() end
  s:newCel(base, i, Image{ fromFile = d .. "/dead_bishop/" .. (i - 1) .. ".png" }, Point(0, 0))
  s.frames[i].duration = 0.33
end
local tag = s:newTag(1, 4); tag.name = "pulz (porost na hrudi, blikani displeje helmy)"
local tag2 = s:newTag(5, 5); tag2.name = "portret (hlava a ramena na stred)"
local up = s:newLayer(); up.name = "dead_bishop UPRAVY"
s:loadPalette(pal)
app.activeLayer = up
s:saveAs(o .. "/Bus_dead_bishop.aseprite")
s:close()
print("ok")
