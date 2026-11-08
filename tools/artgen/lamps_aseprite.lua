-- Builds the Aseprite sources of the Gang of Lamps from lamps.py.
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite \
--          --script-param pal=$HOME/.config/aseprite/palettes/lamps.gpl --script tools/artgen/lamps_aseprite.lua
-- OVERWRITES assets/aseprite/Lamps_{sconce,chandelier,torchere,don}.aseprite (incl. their UPRAVY layers).
-- Draw touch-ups into the "UPRAVY" layers; lamps_export.lua merges them in.
-- Lamps_don is at LOGICAL size (45x56): the game shows it at scale 3 to match Scraper1140.png's 3x pixels.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
for _, c in ipairs({
    { "sconce", 128, 176, "ceka (plamen kouka ke dverim, ukrcne se, mosazna lampa zarachta)" },
    { "chandelier", 128, 216, "ceka (odlesk obehne krystaly, koule se rozhlizi, privesek se houpe)" },
    { "torchere", 128, 200, "ceka (vitr polozi plamen, otoci se na tebe a vzplane, jiskry)" },
    { "don", 45, 56, "ceka (plamen se otoci k hraci, doutnik zezhne, kour stoupa)" } }) do
  local id, w, h, tagname = c[1], c[2], c[3], c[4]
  local s = Sprite(w, h, ColorMode.RGB)
  local base = s.layers[1]; base.name = id
  for i = 1, 8 do
    if i > 1 then s:newEmptyFrame() end
    s:newCel(base, i, Image{ fromFile = d .. "/" .. id .. "/" .. (i - 1) .. ".png" }, Point(0, 0))
    s.frames[i].duration = 1 / 6
  end
  local tag = s:newTag(1, 8); tag.name = tagname
  local up = s:newLayer(); up.name = id .. " UPRAVY"
  if pal then s:loadPalette(pal) end
  app.activeLayer = up
  s:saveAs(o .. "/Lamps_" .. id .. ".aseprite")
  s:close()
end
print("ok")
