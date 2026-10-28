-- Builds the Aseprite source of the generated inventory icons: one 60x60 frame per icon, each frame tagged with the
-- item id (the export names the PNGs by the tags), a generated layer + an empty UPRAVY layer for hand edits.
-- aseprite -b --script-param dir=<outdir of item_icons.py> --script-param out=assets/aseprite --script tools/artgen/item_icons_aseprite.lua
-- OVERWRITES assets/aseprite/UI_ItemIcons_60x60.aseprite (incl. its UPRAVY layer).
local d, o = app.params["dir"], app.params["out"]
local ids = {}
for line in io.lines(d .. "/icons.txt") do if line ~= "" then ids[#ids + 1] = line end end
local s = Sprite(60, 60, ColorMode.RGB)
local base = s.layers[1]; base.name = "IKONY (Claude)"
local up = s:newLayer(); up.name = "UPRAVY - kresli sem"
for i, id in ipairs(ids) do
  if i > 1 then s:newEmptyFrame() end
  s:newCel(base, i, Image{ fromFile = d .. "/" .. id .. ".png" }, Point(0, 0))
  local t = s:newTag(i, i); t.name = id
end
app.activeLayer = up
s:saveAs(o .. "/UI_ItemIcons_60x60.aseprite")
s:close()
print("ok " .. #ids)
