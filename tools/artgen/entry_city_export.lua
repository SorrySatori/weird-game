-- Exports the city view source into the game at 1:1: every layer except the "neexportovat" ones (UPRAVY included).
-- aseprite -b --script-param f=assets/aseprite/EntryCity_1067x600.aseprite \
--         --script-param out=assets/images/backgrounds/EntryCity.png --script tools/artgen/entry_city_export.lua
local s = app.open(app.params["f"])
for _, l in ipairs(s.layers) do l.isVisible = not string.find(l.name, "neexportovat", 1, true) end
local img = Image(s.width, s.height, ColorMode.RGB)
img:drawSprite(s, 1)
img:saveAs(app.params["out"])
s:close()
print("ok")
