-- Exports the Cardinal Feast cast sheets from the Aseprite sources into the game (touch-ups in "UPRAVY" included).
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters/feast --script tools/artgen/feast_cast_export.lua
-- then rebuild the half-size tokens: python3 tools/artgen/feast_cast.py --tokens assets/images/characters/feast
local src, dst = app.params["src"], app.params["dst"]
for _, id in ipairs({ "emils", "pim", "vesper", "marigold", "cornelius", "wren", "gallow" }) do
  local s = app.open(src .. "/Feast_" .. id .. ".aseprite")
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
