-- Exports the Applications clerk sheet from the Aseprite source into the game (touch-ups in "UPRAVY" included).
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters --script tools/artgen/clerk_export.lua
local src, dst = app.params["src"], app.params["dst"]
local s = app.open(src .. "/Shed_clerk_applications.aseprite")
for _, l in ipairs(s.layers) do l.isVisible = (l.name == "clerk" or l.name == "clerk UPRAVY") end
local sheet = Image(s.width * #s.frames, s.height, ColorMode.RGB)
for i = 1, #s.frames do
  local img = Image(s.width, s.height, ColorMode.RGB)
  img:drawSprite(s, i)
  sheet:drawImage(img, Point((i - 1) * s.width, 0))
end
sheet:saveAs(dst .. "/clerk_applications.png")
s:close()
print("ok")
