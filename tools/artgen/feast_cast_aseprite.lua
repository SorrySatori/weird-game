-- Builds the Aseprite sources of the Cardinal Feast cast from feast_cast.py (one file per character).
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script feast_cast_aseprite.lua
-- Draw touch-ups into the "<id> UPRAVY" layer; feast_cast_export.lua merges it in (then rebuild the tokens, see README).
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local CAST = {
  { id = "emils", w = 128, h = 176, n = 24, tags = { { 1, 8, "cte (ceka)" }, { 9, 16, "pripiji (ceka)" }, { 17, 24, "vita (ceka)" } } },
  { id = "pim", w = 128, h = 128, n = 8, tags = { { 1, 8, "ceka (dech, mrk, pohled, prst na brade, ocas, polkne)" } } },
  { id = "vesper", w = 128, h = 176, n = 8, tags = { { 1, 8, "ceka (dech, plamen, mrk, pohled, kadidla)" } } },
  { id = "marigold", w = 128, h = 160, n = 8, tags = { { 1, 8, "ceka (michani v hrnci, para, mrk)" } } },
  { id = "cornelius", w = 128, h = 160, n = 8, tags = { { 1, 8, "ceka (dech, monokl, mrk, poharek, mesec)" } } },
  { id = "wren", w = 128, h = 144, n = 8, tags = { { 1, 8, "ceka (dech, mrk, pise, pohled)" } } },
  { id = "gallow", w = 128, h = 176, n = 8, tags = { { 1, 8, "ceka (dech, sekacek, mrk, zamraceni, klobasy)" } } },
}
for _, c in ipairs(CAST) do
  local s = Sprite(c.w, c.h, ColorMode.RGB)
  local base = s.layers[1]; base.name = c.id
  for i = 1, c.n do
    if i > 1 then s:newEmptyFrame() end
    s:newCel(base, i, Image{ fromFile = d .. "/" .. c.id .. "/" .. (i - 1) .. ".png" }, Point(0, 0))
    s.frames[i].duration = 0.2
  end
  for _, t in ipairs(c.tags) do local tag = s:newTag(t[1], t[2]); tag.name = t[3] end
  local up = s:newLayer(); up.name = c.id .. " UPRAVY"
  s:loadPalette(pal)
  app.activeLayer = up
  s:saveAs(o .. "/Feast_" .. c.id .. ".aseprite")
  s:close()
end
print("ok")
