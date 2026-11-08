-- Builds the Aseprite sources of the Voxmarket auction guests from the generator output (voxmarket_guests.py).
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script voxguests_aseprite.lua
-- (OVERWRITES assets/aseprite/Vox_<id>.aseprite incl. their UPRAVY layers.) Draw touch-ups into the "UPRAVY" layer;
-- voxguests_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local CAST = {
  { "sister_calyx", 128, 176, 8 },
  { "heartbroker_lune", 128, 192, 8 },
  { "silence", 128, 128, 8 },
  { "heir_aquarium", 128, 176, 8 },
}
for _, m in ipairs(CAST) do
  local id, w, h, n = m[1], m[2], m[3], m[4]
  local s = Sprite(w, h, ColorMode.RGB)
  local base = s.layers[1]; base.name = id
  for i = 1, n do
    if i > 1 then s:newEmptyFrame() end
    s:newCel(base, i, Image{ fromFile = d .. "/" .. id .. "/" .. (i - 1) .. ".png" }, Point(0, 0))
    s.frames[i].duration = 0.2
  end
  local tag = s:newTag(1, n); tag.name = "ceka"
  local up = s:newLayer(); up.name = id .. " UPRAVY"
  s:loadPalette(pal)
  app.activeLayer = up
  s:saveAs(o .. "/Vox_" .. id .. ".aseprite")
  s:close()
end
print("ok")
