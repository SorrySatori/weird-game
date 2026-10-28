-- Exports the fast-travel map into the game: all art layers (UPRAVY included) merged at the native 400x300 --
-- the game runs with pixelArt: true, so MapUI's 2x display keeps hard pixels. Run after hand edits in Aseprite:
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/ui --script tools/artgen/map_export.lua
local src, dst = app.params["src"], app.params["dst"]
local s = app.open(src .. "/UI_Map_400x300.aseprite")
for _, l in ipairs(s.layers) do l.isVisible = not string.find(l.name, "neexportovat", 1, true) end
local img = Image(s.width, s.height, ColorMode.RGB)
img:drawSprite(s, 1)
img:saveAs(dst .. "/map.png")
s:close()
print("ok")
