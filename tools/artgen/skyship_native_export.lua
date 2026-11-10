-- Exports the skyship look-up cut into the game, 1:1: every layer except the "neexportovat" ones (UPRAVY included).
-- Run after hand edits in Aseprite:
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/backgrounds --script tools/artgen/skyship_native_export.lua
local src, dst = app.params["src"], app.params["dst"]
local s = app.open(src .. "/Skyship_1067x600.aseprite")
for _, l in ipairs(s.layers) do l.isVisible = not string.find(l.name, "neexportovat", 1, true) end
local img = Image(s.width, s.height, ColorMode.RGB)
img:drawSprite(s, 1)
img:saveAs(dst .. "/skyship.png")
s:close()
print("ok")
