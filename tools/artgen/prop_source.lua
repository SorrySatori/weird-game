-- Builds an Aseprite source for a generated prop sprite (any size): one layer per image + an empty UPRAVY layer.
-- aseprite -b --script-param "imgs=<png>|<layer name>;<png>|<layer name>" --script-param out=assets/aseprite/<Name>.aseprite --script tools/artgen/prop_source.lua
local specs = {}
for part in string.gmatch(app.params["imgs"], "[^;]+") do
  local path, name = part:match("([^|]+)|(.+)")
  specs[#specs + 1] = { path = path, name = name }
end
local first = Image{ fromFile = specs[1].path }
local s = Sprite(first.width, first.height, ColorMode.RGB)
for i, sp in ipairs(specs) do
  local layer = (i == 1) and s.layers[1] or s:newLayer()
  layer.name = sp.name
  s:newCel(layer, 1, (i == 1) and first or Image{ fromFile = sp.path }, Point(0, 0))
end
local up = s:newLayer(); up.name = "UPRAVY - kresli sem"
app.activeLayer = up
s:saveAs(app.params["out"])
s:close()
print("ok")
