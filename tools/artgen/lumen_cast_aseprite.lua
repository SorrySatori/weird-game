-- Builds the Aseprite sources of the Lumen Directorate cast (Verrik, the Angle Corrector, Seldo) from lumen_cast.py.
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<lumen_cast.gpl> --script lumen_cast_aseprite.lua
-- OVERWRITES assets/aseprite/Lumen_verrik.aseprite, Lumen_angle_corrector.aseprite, Lumen_seldo.aseprite (incl. their
-- UPRAVY layers). Draw touch-ups into the "UPRAVY" layer; lumen_cast_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
for _, c in ipairs({
    { "verrik", "ceka (dech, tykadlo, kridla se zachveji x2, ostri srpu se zablyskne x2, vydech; lucerna blika)", "Lumen_verrik" },
    { "angle_corrector", "ceka (0-3 klid = ctvrtiny otoceni prstenu; 4 nadech, 5 hledi se rozzari, 6 prilba se nakloni, 7 vydech + prst)", "Lumen_angle_corrector" },
    { "seldo", "ceka (dech, papir zasusti, rucicka tiknutim + lampicka, naklon hlavy, povoleni se zachveje, mrk, vydech)", "Lumen_seldo" } }) do
  local id, tagname, file = c[1], c[2], c[3]
  local s = Sprite(128, 192, ColorMode.RGB)
  local base = s.layers[1]; base.name = id
  for i = 1, 8 do
    if i > 1 then s:newEmptyFrame() end
    s:newCel(base, i, Image{ fromFile = d .. "/" .. id .. "/" .. (i - 1) .. ".png" }, Point(0, 0))
    s.frames[i].duration = 0.2
  end
  local tag = s:newTag(1, 8); tag.name = tagname
  local up = s:newLayer(); up.name = id .. " UPRAVY"
  s:loadPalette(pal)
  app.activeLayer = up
  s:saveAs(o .. "/" .. file .. ".aseprite")
  s:close()
end
print("ok")
