-- Exports the inventory icons into the game: every tagged frame (UPRAVY merged) -> <dst>/<tag name>.png, 60x60.
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/items --script tools/artgen/item_icons_export.lua
local src, dst = app.params["src"], app.params["dst"]
local s = app.open(src .. "/UI_ItemIcons_60x60.aseprite")
for _, l in ipairs(s.layers) do l.isVisible = not string.find(l.name, "neexportovat", 1, true) end
for _, t in ipairs(s.tags) do
  local img = Image(s.width, s.height, ColorMode.RGB)
  img:drawSprite(s, t.fromFrame.frameNumber)
  img:saveAs(dst .. "/" .. t.name .. ".png")
end
print("ok " .. #s.tags)
s:close()
