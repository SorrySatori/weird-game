-- Exports a logical-size (356x200) background source into the game: every layer except the "neexportovat" ones
-- (UPRAVY included), blown up 3x with hard pixels, 1068x600 cropped to the 1067x600 canvas.
-- aseprite -b --script-param f=assets/aseprite/<Name>_356x200.aseprite --script-param out=assets/images/backgrounds/<Name>.png --script tools/artgen/logical_export.lua
local s = app.open(app.params["f"])
for _, l in ipairs(s.layers) do l.isVisible = not string.find(l.name, "neexportovat", 1, true) end
local img = Image(s.width, s.height, ColorMode.RGB)
img:drawSprite(s, 1)
local out = Image(1067, 600, ColorMode.RGB)
for y = 0, 599 do
  for x = 0, 1066 do out:drawPixel(x, y, img:getPixel(x // 3, y // 3)) end
end
out:saveAs(app.params["out"])
s:close()
print("ok")
