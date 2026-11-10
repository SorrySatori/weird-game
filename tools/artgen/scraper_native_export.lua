-- Exports the native Scraper 1140 background into the game: every layer except the "neexportovat" ones (UPRAVY
-- included) merged at 1067x600. Run after hand edits in Aseprite:
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/backgrounds --script tools/artgen/scraper_native_export.lua
local src, dst = app.params["src"], app.params["dst"]
local s = app.open(src .. "/Scraper1140_1067x600.aseprite")
for _, l in ipairs(s.layers) do l.isVisible = not string.find(l.name, "neexportovat", 1, true) end
local img = Image(s.width, s.height, ColorMode.RGB)
img:drawSprite(s, 1)
img:saveAs(dst .. "/Scraper1140.png")
s:close()
print("ok")
