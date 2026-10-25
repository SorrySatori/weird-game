-- Exports the Ortolan / Ortolan (four arms) / Dr. Elphi idle sheets from the Aseprite sources (UPRAVY included).
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/characters --script tools/artgen/ortolan_elphi_export.lua
local src, dst = app.params["src"], app.params["dst"]
for _, c in ipairs({ { "ortolan", "Ortolan_idle" }, { "ortolan4", "Ortolan4_idle" }, { "elphi", "Elphi_idle" } }) do
  local id, file = c[1], c[2]
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
end
print("ok")
