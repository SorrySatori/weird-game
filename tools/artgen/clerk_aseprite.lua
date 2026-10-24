-- Builds the Aseprite source of the Applications clerk from clerk.py.
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script clerk_aseprite.lua
-- Draw touch-ups into the "UPRAVY" layer; clerk_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local s = Sprite(128, 176, ColorMode.RGB)
local base = s.layers[1]; base.name = "clerk"
for i = 1, 8 do
  if i > 1 then s:newEmptyFrame() end
  s:newCel(base, i, Image{ fromFile = d .. "/clerk/" .. (i - 1) .. ".png" }, Point(0, 0))
  s.frames[i].duration = 0.25
end
local tag = s:newTag(1, 8); tag.name = "ceka (dech, bryle, list, pero)"
local up = s:newLayer(); up.name = "clerk UPRAVY"
s:loadPalette(pal)
app.activeLayer = up
s:saveAs(o .. "/Shed_clerk_applications.aseprite")
s:close()
print("ok")
