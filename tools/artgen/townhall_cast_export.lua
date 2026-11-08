-- Exports the Townhall cast sheets from the Aseprite sources into the game (touch-ups in "UPRAVY" included).
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters/townhall --script tools/artgen/townhall_cast_export.lua
local src, dst = app.params["src"], app.params["dst"]
for _, id in ipairs({ "phor", "clerk", "eater", "seraphel", "poet" }) do
  local s = app.open(src .. "/Townhall_" .. id .. ".aseprite")
  for _, l in ipairs(s.layers) do l.isVisible = (l.name == id or l.name == id .. " UPRAVY") end
  local sheet = Image(s.width * #s.frames, s.height, ColorMode.RGB)
  for i = 1, #s.frames do
    local img = Image(s.width, s.height, ColorMode.RGB)
    img:drawSprite(s, i)
    sheet:drawImage(img, Point((i - 1) * s.width, 0))
  end
  sheet:saveAs(dst .. "/" .. id .. ".png")
  s:close()
end
print("ok")
