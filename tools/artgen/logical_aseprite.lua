-- Builds an Aseprite source for a background kept at its logical size (356x200, the game shows it 3x):
-- the given art layers (bottom to top), an empty UPRAVY layer, the hidden scale figures + guides from <dir> (if there).
-- aseprite -b --script-param dir=<outdir> --script-param "layers=a.png|LAYER A;b.png|LAYER B" \
--         --script-param out=assets/aseprite/<Name>_356x200.aseprite --script-param pal=<gpl> --script tools/artgen/logical_aseprite.lua
-- OVERWRITES the target (incl. its UPRAVY layer); to refresh one generated layer use bg_update.lua.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local s = Sprite(356, 200, ColorMode.RGB)
local first = true
for entry in string.gmatch(app.params["layers"], "[^;]+") do
  local file, name = string.match(entry, "([^|]+)|(.+)")
  local l = first and s.layers[1] or s:newLayer()
  l.name = name; first = false
  s:newCel(l, 1, Image{ fromFile = d .. "/" .. file }, Point(0, 0))
end
local up = s:newLayer(); up.name = "UPRAVY - kresli sem"
if app.fs.isFile(d .. "/chars.png") then                -- cut-scene pictures have no figures / guides
  local ch = s:newLayer(); ch.name = "POSTAVY meritko (neexportovat)"
  s:newCel(ch, 1, Image{ fromFile = d .. "/chars.png" }, Point(0, 0)); ch.isVisible = false; ch.isEditable = false
end
if app.fs.isFile(d .. "/guides.png") then
  local g = s:newLayer(); g.name = "VODITKA (neexportovat)"
  s:newCel(g, 1, Image{ fromFile = d .. "/guides.png" }, Point(0, 0)); g.isVisible = false; g.isEditable = false
end
s:loadPalette(pal)
app.activeLayer = up
s:saveAs(o)
s:close()
print("ok")
