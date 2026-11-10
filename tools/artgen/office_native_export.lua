-- Exports the abandoned office background into the game after hand edits in Aseprite: every layer except the reference
-- ones ("neexportovat"), UPRAVY included, flattened at 1067x600 -> assets/images/backgrounds/ShedAbandonedOffice.png.
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/backgrounds --script tools/artgen/office_native_export.lua
local src, dst = app.params["src"], app.params["dst"]
local s = app.open(src .. "/ShedAbandonedOffice_1067x600.aseprite")
for _, l in ipairs(s.layers) do l.isVisible = not string.find(l.name, "neexportovat", 1, true) end
local img = Image(s.width, s.height, ColorMode.RGB)
img:drawSprite(s, 1)
img:saveAs(dst .. "/ShedAbandonedOffice.png")
s:close()
print("ok")
