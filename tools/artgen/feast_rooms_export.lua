-- Exports the Cardinal Feast rooms from their Aseprite sources into the game (touch-ups in "UPRAVY" included).
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/backgrounds/feast --script tools/artgen/feast_rooms_export.lua
local src, dst = app.params["src"], app.params["dst"]
for _, id in ipairs({ "nave", "hall", "hall_dark" }) do
  local s = app.open(src .. "/Feast_" .. id .. "_1067x600.aseprite")
  local img = Image(s.width, s.height, ColorMode.RGB)
  img:drawSprite(s, 1)
  img:saveAs(dst .. "/" .. id .. ".png")
  s:close()
end
print("ok")
