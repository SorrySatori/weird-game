-- aseprite -b --script asm.lua --script-param dir=<scratch> --script-param out=<repo/assets/aseprite> --script-param pal=<gpl>
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]

-- 1. the background template
local spr = Sprite(1067, 600, ColorMode.RGB)
local base = spr.layers[1]; base.name = "KRIZOVATKA pozadi (Claude)"
spr:newCel(base, 1, Image{ fromFile = d .. "/bg.png" }, Point(0, 0))
local paint = spr:newLayer(); paint.name = "UPRAVY - kresli sem"
local corpse = spr:newLayer(); corpse.name = "MRTVOLA nahled (zvlastni sprite, neexportovat)"
spr:newCel(corpse, 1, Image{ fromFile = d .. "/corpse_0.png" }, Point(408 - 120, 496 - 440)); corpse.isEditable = false
local ch = spr:newLayer(); ch.name = "POSTAVY meritko (neexportovat)"
spr:newCel(ch, 1, Image{ fromFile = d .. "/chars.png" }, Point(0, 0)); ch.isVisible = false; ch.isEditable = false
local g = spr:newLayer(); g.name = "VODITKA (neexportovat)"
spr:newCel(g, 1, Image{ fromFile = d .. "/guides.png" }, Point(0, 0)); g.isVisible = false; g.isEditable = false
spr:loadPalette(pal)
app.activeLayer = paint
spr:saveAs(o .. "/Crossroad_1067x600.aseprite")

-- 2. the corpse: one sprite, three frames, tagged
local c = Sprite(240, 440, ColorMode.RGB)
local cl = c.layers[1]; cl.name = "MRTVOLA (Claude)"
c:newCel(cl, 1, Image{ fromFile = d .. "/corpse_0.png" }, Point(0, 0))
c:newFrame(); c:newCel(cl, 2, Image{ fromFile = d .. "/corpse_1.png" }, Point(0, 0))
c:newFrame(); c:newCel(cl, 3, Image{ fromFile = d .. "/corpse_2.png" }, Point(0, 0))
local cp = c:newLayer(); cp.name = "UPRAVY - kresli sem"
local t1 = c:newTag(1, 1); t1.name = "0 netknuta"
local t2 = c:newTag(2, 2); t2.name = "1 rozriznuta hlava"
local t3 = c:newTag(3, 3); t3.name = "2 prorostla (strom)"
c:loadPalette(pal)
app.activeLayer = cp
c:saveAs(o .. "/Crossroad_corpse_240x440x3.aseprite")
print("ok")
