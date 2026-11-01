-- Builds the Aseprite sources of Ortolan (two arms / four arms) from ortolan.py.
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script ortolan_aseprite.lua
-- OVERWRITES assets/aseprite/Ortolan_idle.aseprite + Ortolan4_idle.aseprite (incl. their UPRAVY layers).
-- Draw touch-ups into the "UPRAVY" layer; ortolan_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
for _, c in ipairs({ { "ortolan", "ceka (dech, mrk, bryle, hm, pesec nahoru, prohlizi si ho, vydech)", "Ortolan_idle" },
                     { "ortolan4", "ceka (dech, mrk, bryle, hm + palec, pesec nahoru, prohlizi si ho, vydech)", "Ortolan4_idle" } }) do
  local id, tagname, file = c[1], c[2], c[3]
  local s = Sprite(128, 160, ColorMode.RGB)
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
  s:saveAs(o .. "/" .. file .. ".aseprite")
  s:close()
end
print("ok")
