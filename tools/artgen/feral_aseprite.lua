-- Builds the Aseprite sources of the Feral Toast band from the generator output (feral_toast.py).
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script feral_aseprite.lua
-- One file per member; tags "ceka" (idle, 4 frames) and "hraje" (playing, 8 frames = 4 beats at 177 BPM).
-- Draw touch-ups into the "UPRAVY" layer; feral_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local CAST = { { "telka", 128, 176 }, { "bass_xl", 144, 192 }, { "karlis", 176, 176 }, { "mira", 144, 176 } }

for _, m in ipairs(CAST) do
  local id, w, h = m[1], m[2], m[3]
  local s = Sprite(w, h, ColorMode.RGB)
  local base = s.layers[1]; base.name = id
  for i = 1, 12 do
    if i > 1 then s:newEmptyFrame() end
    s:newCel(base, i, Image{ fromFile = d .. "/" .. id .. "/" .. (i - 1) .. ".png" }, Point(0, 0))
    s.frames[i].duration = i <= 4 and 0.4 or 0.17
  end
  local idle = s:newTag(1, 4); idle.name = "ceka"
  local play = s:newTag(5, 12); play.name = "hraje"
  local up = s:newLayer(); up.name = id .. " UPRAVY"
  s:loadPalette(pal)
  app.activeLayer = up
  s:saveAs(o .. "/FeralToast_" .. id .. ".aseprite")
  s:close()
end
print("ok")
