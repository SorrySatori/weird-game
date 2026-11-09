-- Exports Dr. Elphi's idle sheet from its Aseprite source (UPRAVY included) -> assets/images/characters/elphi_idle.png.
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters --script tools/artgen/elphi_export.lua
local src, dst = app.params["src"], app.params["dst"]
local id, file = "elphi", "Elphi_idle"
local s = app.open(src .. "/" .. file .. ".aseprite")
for _, l in ipairs(s.layers) do l.isVisible = (l.name == id or l.name == id .. " UPRAVY") end
local sheet = Image(s.width * #s.frames, s.height, ColorMode.RGB)
for i = 1, #s.frames do
  local img = Image(s.width, s.height, ColorMode.RGB)
  img:drawSprite(s, i)
  sheet:drawImage(img, Point((i - 1) * s.width, 0))
end
sheet:saveAs(dst .. "/" .. id .. "_idle.png")
s:close()
print("ok")
