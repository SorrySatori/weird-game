-- Builds the Aseprite source of the the Sentinel (Cathedral guard) from guardian.py.
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script guardian_aseprite.lua
-- Draw touch-ups into the "UPRAVY" layer; guardian_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local s = Sprite(128, 176, ColorMode.RGB)
local base = s.layers[1]; base.name = "guardian"
for i = 1, 8 do
  if i > 1 then s:newEmptyFrame() end
  s:newCel(base, i, Image{ fromFile = d .. "/guardian/" .. (i - 1) .. ".png" }, Point(0, 0))
  s.frames[i].duration = 0.2
end
local tag = s:newTag(1, 8); tag.name = "ceka (dech, oci, plast, naklon hlavy)"
local up = s:newLayer(); up.name = "guardian UPRAVY"
s:loadPalette(pal)
app.activeLayer = up
s:saveAs(o .. "/Cathedral_guardian.aseprite")
s:close()
print("ok")
