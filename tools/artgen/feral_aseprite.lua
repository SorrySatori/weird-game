-- Builds the Aseprite sources of the Feral Toast band from the generator output (feral_px.py; earlier feral_toast.py).
-- The frame size is taken from the frames themselves.
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script feral_aseprite.lua
-- One file per member; tags "ceka" (idle, 4 frames) and "hraje" (playing, 8 frames = 4 beats at 177 BPM).
-- Draw touch-ups into the "UPRAVY" layer; feral_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
for _, id in ipairs({ "telka", "bass_xl", "karlis", "mira" }) do
  local first = Image{ fromFile = d .. "/" .. id .. "/0.png" }
  local s = Sprite(first.width, first.height, ColorMode.RGB)
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
