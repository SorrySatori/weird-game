-- Builds the Aseprite source of the Senior Clerk (registration yard) from senior_clerk.py.
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script senior_clerk_aseprite.lua
-- Draw touch-ups into the "UPRAVY" layer; senior_clerk_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local s = Sprite(128, 192, ColorMode.RGB)
local base = s.layers[1]; base.name = "senior clerk"
for i = 1, 8 do
  if i > 1 then s:newEmptyFrame() end
  s:newCel(base, i, Image{ fromFile = d .. "/senior_clerk/" .. (i - 1) .. ".png" }, Point(0, 0))
  s.frames[i].duration = 0.25
end
local tag = s:newTag(1, 8); tag.name = "ceka (dech, mrk, odfrknuti, jazyk, pohled, kniha)"
local up = s:newLayer(); up.name = "senior clerk UPRAVY"
s:loadPalette(pal)
app.activeLayer = up
s:saveAs(o .. "/Shed_senior_clerk.aseprite")
s:close()
print("ok")
