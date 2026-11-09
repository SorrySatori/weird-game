-- Builds the Aseprite source of Edgar Eskola (Screaming Cork) from edgar_rig.py (the drawn redraw; edgar.py is the
-- superseded box-filtered derivation of the old AI picture).
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gen out>/edgar_rig.gpl --script tools/artgen/edgar_rig_aseprite.lua
-- Draw touch-ups into the "edgar UPRAVY" layer; edgar_rig_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local s = Sprite(128, 192, ColorMode.RGB)
local base = s.layers[1]; base.name = "edgar"
for i = 1, 8 do
  if i > 1 then s:newEmptyFrame() end
  s:newCel(base, i, Image{ fromFile = d .. "/edgar/" .. (i - 1) .. ".png" }, Point(0, 0))
  s.frames[i].duration = 0.25
end
local tag = s:newTag(1, 8); tag.name = "ceka (dech, mrk, ucho, pytel, hlava dolu, povzdech)"
local up = s:newLayer(); up.name = "edgar UPRAVY"
s:loadPalette(pal)
app.activeLayer = up
s:saveAs(o .. "/Edgar_eskola.aseprite")
s:close()
print("ok")
