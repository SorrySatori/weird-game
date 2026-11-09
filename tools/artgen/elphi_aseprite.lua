-- Builds the Aseprite source of Dr. Elphi Quarn from elphi.py (rig.py redraw; replaces the ortolan_elphi.py derivation).
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script elphi_aseprite.lua
-- OVERWRITES assets/aseprite/Elphi_idle.aseprite (incl. its UPRAVY layer).
-- Draw touch-ups into the "UPRAVY" layer; elphi_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local id, file = "elphi", "Elphi_idle"
local s = Sprite(128, 160, ColorMode.RGB)
local base = s.layers[1]; base.name = id
for i = 1, 8 do
  if i > 1 then s:newEmptyFrame() end
  s:newCel(base, i, Image{ fromFile = d .. "/" .. id .. "/" .. (i - 1) .. ".png" }, Point(0, 0))
  s.frames[i].duration = 0.25
end
local tag = s:newTag(1, 8); tag.name = "ceka (dech, bryle + mrk, hologram pulzuje, stoupa, pohled na nej, tuknuti, vlasy)"
local up = s:newLayer(); up.name = id .. " UPRAVY"
s:loadPalette(pal)
app.activeLayer = up
s:saveAs(o .. "/" .. file .. ".aseprite")
s:close()
print("ok")
