-- Exports the protagonist sheet from the Aseprite source into the game (touch-ups in "UPRAVY" included).
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters --script tools/artgen/hero_export.lua
local src, dst = app.params["src"], app.params["dst"]
local s = app.open(src .. "/Hero_priest_128.aseprite")
for _, l in ipairs(s.layers) do l.isVisible = (l.name == "priest" or l.name == "priest UPRAVY") end
local sheet = Image(s.width * #s.frames, s.height, ColorMode.RGB)
for i = 1, #s.frames do
  local img = Image(s.width, s.height, ColorMode.RGB)
  img:drawSprite(s, i)
  sheet:drawImage(img, Point((i - 1) * s.width, 0))
end
sheet:saveAs(dst .. "/priest.png")
s:close()
print("ok")
