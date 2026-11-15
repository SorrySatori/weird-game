-- Builds the Aseprite source of Gnur (Shed 521) from the generator output (gnur.py).
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script gnur_aseprite.lua
-- Draw touch-ups into the "UPRAVY" layer; gnur_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local s = Sprite(128, 128, ColorMode.RGB)
local base = s.layers[1]; base.name = "gnur"
for i = 1, 12 do
  if i > 1 then s:newEmptyFrame() end
  s:newCel(base, i, Image{ fromFile = d .. "/gnur/" .. (i - 1) .. ".png" }, Point(0, 0))
  s.frames[i].duration = i <= 4 and 0.4 or 0.07
end
for _, t in ipairs({ { "ceka", 1, 4 }, { "chuze", 5, 12 } }) do local tag = s:newTag(t[2], t[3]); tag.name = t[1] end
local up = s:newLayer(); up.name = "gnur UPRAVY"
s:loadPalette(pal)
app.activeLayer = up
s:saveAs(o .. "/Shed_gnur.aseprite")
s:close()
print("ok")
