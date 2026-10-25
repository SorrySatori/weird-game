-- Builds the Aseprite source of Edgar Eskola (Screaming Cork) from edgar.py.
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script edgar_aseprite.lua
-- Draw touch-ups into the "UPRAVY" layer; edgar_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local s = Sprite(128, 192, ColorMode.RGB)
local base = s.layers[1]; base.name = "edgar"
for i = 1, 8 do
  if i > 1 then s:newEmptyFrame() end
  s:newCel(base, i, Image{ fromFile = d .. "/edgar/" .. (i - 1) .. ".png" }, Point(0, 0))
  s.frames[i].duration = 0.2
end
local tag = s:newTag(1, 8); tag.name = "ceka (dech, mrk, ucho, pytlik, hlava)"
local up = s:newLayer(); up.name = "edgar UPRAVY"
s:loadPalette(pal)
app.activeLayer = up
s:saveAs(o .. "/Edgar_eskola.aseprite")
s:close()
print("ok")
