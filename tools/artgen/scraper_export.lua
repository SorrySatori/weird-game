-- Exports the Scraper 1140 background into the game: the four art layers (UPRAVY included) blown up 3x with hard
-- pixels, 1068x600 cropped to the 1067x600 canvas. Run after hand edits in Aseprite:
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/backgrounds --script tools/artgen/scraper_export.lua
local src, dst = app.params["src"], app.params["dst"]
local s = app.open(src .. "/Scraper1140_356x200.aseprite")
for _, l in ipairs(s.layers) do l.isVisible = not string.find(l.name, "neexportovat", 1, true) end
local img = Image(s.width, s.height, ColorMode.RGB)
img:drawSprite(s, 1)
local out = Image(1067, 600, ColorMode.RGB)
for y = 0, 599 do
  for x = 0, 1066 do out:drawPixel(x, y, img:getPixel(x // 3, y // 3)) end
end
out:saveAs(dst .. "/Scraper1140.png")
s:close()
print("ok")
