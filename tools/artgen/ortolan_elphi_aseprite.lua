-- Builds the Aseprite sources of Ortolan (both looks) and Dr. Elphi from ortolan_elphi.py.
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script ortolan_elphi_aseprite.lua
-- Draw touch-ups into the "UPRAVY" layer; ortolan_elphi_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
for _, c in ipairs({ { "ortolan", 128, 160, "ceka (dech, mrk, bryle, hm, ruka, kyvnuti)", "Ortolan_idle" },
                     { "ortolan4", 144, 160, "ceka (dech, mrk, bryle, hm, horni ruce, kyvnuti)", "Ortolan4_idle" },
                     { "elphi", 128, 160, "ceka (dech, bryle, hologram, plast, tuknuti, vlasy)", "Elphi_idle" } }) do
  local id, w, h, tagname, file = c[1], c[2], c[3], c[4], c[5]
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
  s:saveAs(o .. "/" .. file .. ".aseprite")
  s:close()
end
print("ok")
