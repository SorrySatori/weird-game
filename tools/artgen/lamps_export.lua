-- Exports the Gang of Lamps sheets from their Aseprite sources into the game (touch-ups in "UPRAVY" included).
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters/lamps \
--          [--script-param only=don] --script tools/artgen/lamps_export.lua
--   -> sconce.png (8 x 128x176), chandelier.png (8 x 128x216), torchere.png (8 x 128x200), don.png (8 x 136x168),
--      all shown at scale 1; `only` (comma-separated ids) limits it to those lamps
local src, dst, only = app.params["src"], app.params["dst"], app.params["only"]
local want = nil
if only and only ~= "" then
  want = {}
  for id in string.gmatch(only, "[^,]+") do want[id] = true end
end
for _, id in ipairs({ "sconce", "chandelier", "torchere", "don" }) do
  if not want or want[id] then
    local s = app.open(src .. "/Lamps_" .. id .. ".aseprite")
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
end
print("ok")
