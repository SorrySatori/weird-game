-- Swaps the generated base image of one layer in an existing background source, keeping every other layer (UPRAVY too).
-- aseprite -b --script-param f=assets/aseprite/<file>.aseprite --script-param layer="<layer name>" --script-param img=<png> --script tools/artgen/bg_update.lua
local s = app.open(app.params["f"])
local name, img = app.params["layer"], Image{ fromFile = app.params["img"] }
for _, l in ipairs(s.layers) do
  if l.name == name then
    local c = l:cel(1)
    if c then c.image = img; c.position = Point(0, 0) else s:newCel(l, 1, img, Point(0, 0)) end
  end
end
s:saveAs(app.params["f"])
s:close()
print("ok " .. name)
