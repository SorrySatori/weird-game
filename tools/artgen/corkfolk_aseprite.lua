-- Builds the Aseprite sources of the Screaming Cork's people (Heliodor, Ravla) from corkfolk.py.
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script corkfolk_aseprite.lua
-- Draw touch-ups into the "UPRAVY" layer; corkfolk_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
for _, c in ipairs({ { "heliodor", 128, 192, "ceka (dech, zare, mrk, oci, listi, kapka)" }, { "ravla", 128, 128, "ceka (dech, bryle, hlava, ruce, chapadlo)" } }) do
  local id, w, h, tagname = c[1], c[2], c[3], c[4]
  local s = Sprite(w, h, ColorMode.RGB)
  local base = s.layers[1]; base.name = id
  for i = 1, 8 do
    if i > 1 then s:newEmptyFrame() end
    s:newCel(base, i, Image{ fromFile = d .. "/" .. id .. "/" .. (i - 1) .. ".png" }, Point(0, 0))
    s.frames[i].duration = 0.25
  end
  local tag = s:newTag(1, 8); tag.name = tagname
  local up = s:newLayer(); up.name = id .. " UPRAVY"
  s:loadPalette(pal)
  app.activeLayer = up
  s:saveAs(o .. "/Cork_" .. id .. ".aseprite")
  s:close()
end
print("ok")
