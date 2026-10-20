local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local spr = Sprite(1067, 600, ColorMode.RGB)
local base = spr.layers[1]; base.name = "SHED 521 pozadi (Claude)"
spr:newCel(base, 1, Image{ fromFile = d .. "/bg.png" }, Point(0, 0))
local paint = spr:newLayer(); paint.name = "UPRAVY - kresli sem"
local ch = spr:newLayer(); ch.name = "POSTAVY meritko (neexportovat)"
spr:newCel(ch, 1, Image{ fromFile = d .. "/chars.png" }, Point(0, 0)); ch.isVisible = false; ch.isEditable = false
local g = spr:newLayer(); g.name = "VODITKA (neexportovat)"
spr:newCel(g, 1, Image{ fromFile = d .. "/guides.png" }, Point(0, 0)); g.isVisible = false; g.isEditable = false
spr:loadPalette(pal)
app.activeLayer = paint
spr:saveAs(o .. "/Shed521_1067x600.aseprite")
print("ok")
