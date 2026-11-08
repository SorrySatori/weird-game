-- Builds the Aseprite sources of the Town Square folk from busker.py and magnekin.py.
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite \
--          --script-param palb=<busker.gpl> --script-param palm=<magnekin.gpl> --script tools/artgen/townsquare_folk_aseprite.lua
-- OVERWRITES assets/aseprite/TownSquare_busker.aseprite, TownSquare_magnekin.aseprite, TownSquare_magnekin_broken.aseprite
-- (incl. their UPRAVY layers). Draw touch-ups into the "UPRAVY" layers; townsquare_folk_export.lua merges them in.
local d, o = app.params["dir"], app.params["out"]
for _, c in ipairs({
    { "busker", 176, 144, 9, 1 / 6, "hraje (dolu, zpet, nahoru, zpet; druhy akord; buben dupe)", "TownSquare_busker", app.params["palb"], 8 },
    { "magnekin", 128, 192, 8, 0.2, "ceka (druzice, okna, mrk, oblazek odskoci, jiskra, oci, pilinky)", "TownSquare_magnekin", app.params["palm"] },
    { "magnekin_broken", 128, 64, 4, 0.25, "hromada (klid, jiskra, oblazek, kridlo + okno)", "TownSquare_magnekin_broken", app.params["palm"] } }) do
  local id, w, h, n, dur, tagname, file, pal = c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8]
  local s = Sprite(w, h, ColorMode.RGB)
  local base = s.layers[1]; base.name = id
  for i = 1, n do
    if i > 1 then s:newEmptyFrame() end
    s:newCel(base, i, Image{ fromFile = d .. "/" .. id .. "/" .. (i - 1) .. ".png" }, Point(0, 0))
    s.frames[i].duration = dur
  end
  local last = c[9] or n                                                    -- the busker's 9th frame is his dialog portrait
  local tag = s:newTag(1, last); tag.name = tagname
  if last < n then local pt = s:newTag(last + 1, n); pt.name = "portret (dialog)" end
  local up = s:newLayer(); up.name = id .. " UPRAVY"
  s:loadPalette(pal)
  app.activeLayer = up
  s:saveAs(o .. "/" .. file .. ".aseprite")
  s:close()
end
print("ok")
