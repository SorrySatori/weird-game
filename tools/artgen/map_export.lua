-- Exports the hand-drawn fast-travel map into the game: all layers (UPRAVY included) merged at 1067x600.
-- Run after hand edits in Aseprite:
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/ui [--script-param color=1] \
--         --script tools/artgen/map_export.lua
-- color=1 exports the coloured version (UI_Map_barevna_1067x600.aseprite -> map_color.png).
local src, dst, col = app.params["src"], app.params["dst"], app.params["color"] == "1"
local s = app.open(src .. (col and "/UI_Map_barevna_1067x600.aseprite" or "/UI_Map_1067x600.aseprite"))
for _, l in ipairs(s.layers) do l.isVisible = not string.find(l.name, "neexportovat", 1, true) end
local img = Image(s.width, s.height, ColorMode.RGB)
img:drawSprite(s, 1)
img:saveAs(dst .. (col and "/map_color.png" or "/map.png"))
s:close()
print("ok")
