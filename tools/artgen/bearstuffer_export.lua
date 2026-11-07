-- Exports the bear stuffer (with its UPRAVY touch-ups) as the game's sheet.
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters/streetfolk --script tools/artgen/bearstuffer_export.lua
local src, dst = app.params["src"], app.params["dst"]
local s = app.open(src .. "/Street_bear_stuffer.aseprite")
for _, l in ipairs(s.layers) do l.isVisible = true end
local n = #s.frames
local sheet = Image(s.width * n, s.height, ColorMode.RGB)
for i = 1, n do
  local img = Image(s.width, s.height, ColorMode.RGB)
  img:drawSprite(s, i)
  sheet:drawImage(img, Point((i - 1) * s.width, 0))
end
sheet:saveAs(dst .. "/bear_stuffer.png")
s:close()
print("ok")
