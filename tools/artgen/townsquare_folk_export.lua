-- Exports the Town Square folk sheets from their Aseprite sources into the game (touch-ups in "UPRAVY" included).
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters --script tools/artgen/townsquare_folk_export.lua
--   -> busker_idle.png (8 idle + 1 portrait frame x 176x144), magnekin_idle.png (8 x 128x192), magnekin_broken_idle.png (4 x 128x64)
local src, dst = app.params["src"], app.params["dst"]
for _, c in ipairs({ { "TownSquare_busker", "busker", "busker_idle" },
                     { "TownSquare_magnekin", "magnekin", "magnekin_idle" },
                     { "TownSquare_magnekin_broken", "magnekin_broken", "magnekin_broken_idle" } }) do
  local file, id, out = c[1], c[2], c[3]
  local s = app.open(src .. "/" .. file .. ".aseprite")
  for _, l in ipairs(s.layers) do l.isVisible = (l.name == id or l.name == id .. " UPRAVY") end
  local sheet = Image(s.width * #s.frames, s.height, ColorMode.RGB)
  for i = 1, #s.frames do
    local img = Image(s.width, s.height, ColorMode.RGB)
    img:drawSprite(s, i)
    sheet:drawImage(img, Point((i - 1) * s.width, 0))
  end
  sheet:saveAs(dst .. "/" .. out .. ".png")
  s:close()
end
print("ok")
