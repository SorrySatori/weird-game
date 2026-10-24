-- Builds the Aseprite sources of the Voxmarket NPCs from the generator output (voxmarket_chars.py).
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script voxchars_aseprite.lua
-- Draw touch-ups into the "UPRAVY" layer; voxchars_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local CAST = {
  { "kloor", 128, 160, 12, { { "ceka", 1, 4 }, { "chuze", 5, 12 } } },
  { "zerren", 176, 160, 4, { { "ceka", 1, 4 } } },
  { "hesh_vell", 208, 176, 8, { { "ceka (Vell o 2 snimky pozdeji)", 1, 8 } } },
}
for _, m in ipairs(CAST) do
  local id, w, h, n, tags = m[1], m[2], m[3], m[4], m[5]
  local s = Sprite(w, h, ColorMode.RGB)
  local base = s.layers[1]; base.name = id
  for i = 1, n do
    if i > 1 then s:newEmptyFrame() end
    s:newCel(base, i, Image{ fromFile = d .. "/" .. id .. "/" .. (i - 1) .. ".png" }, Point(0, 0))
    s.frames[i].duration = 0.2
  end
  for _, t in ipairs(tags) do local tag = s:newTag(t[2], t[3]); tag.name = t[1] end
  local up = s:newLayer(); up.name = id .. " UPRAVY"
  s:loadPalette(pal)
  app.activeLayer = up
  s:saveAs(o .. "/Vox_" .. id .. ".aseprite")
  s:close()
end
print("ok")
