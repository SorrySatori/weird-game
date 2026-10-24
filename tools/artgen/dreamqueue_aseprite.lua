-- Builds the Aseprite sources of the dream queue (Sleepless Mime, Vowel Seller, Hollow Woman) from dreamqueue.py.
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script dreamqueue_aseprite.lua
-- Draw touch-ups into the "UPRAVY" layer; dreamqueue_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
for _, id in ipairs({ "mime", "vowel_seller", "hollow_woman" }) do
  local s = Sprite(128, 160, ColorMode.RGB)
  local base = s.layers[1]; base.name = id
  for i = 1, 6 do
    if i > 1 then s:newEmptyFrame() end
    s:newCel(base, i, Image{ fromFile = d .. "/" .. id .. "/" .. (i - 1) .. ".png" }, Point(0, 0))
    s.frames[i].duration = 0.22
  end
  local tag = s:newTag(1, 6); tag.name = "ceka"
  local up = s:newLayer(); up.name = id .. " UPRAVY"
  s:loadPalette(pal)
  app.activeLayer = up
  s:saveAs(o .. "/DreamQueue_" .. id .. ".aseprite")
  s:close()
end
print("ok")
