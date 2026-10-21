-- aseprite -b --script-param dir=<dir with bg.png bg_growth.png bg_decay.png guides.png chars.png> --script-param out=assets/aseprite --script-param pal=<gpl> --script burningbear_aseprite.lua
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local spr = Sprite(1067, 600, ColorMode.RGB)
local base = spr.layers[1]; base.name = "BURNING BEAR pozadi (Claude)"
spr:newCel(base, 1, Image{ fromFile = d .. "/bg.png" }, Point(0, 0))
local gr = spr:newLayer(); gr.name = "GROWTH varianta (export -> _growth.png)"
spr:newCel(gr, 1, Image{ fromFile = d .. "/bg_growth.png" }, Point(0, 0)); gr.isVisible = false
local de = spr:newLayer(); de.name = "DECAY varianta - medvedi hori (export -> _decay.png)"
spr:newCel(de, 1, Image{ fromFile = d .. "/bg_decay.png" }, Point(0, 0)); de.isVisible = false
local paint = spr:newLayer(); paint.name = "UPRAVY - kresli sem"
local ch = spr:newLayer(); ch.name = "POSTAVY meritko (neexportovat)"
spr:newCel(ch, 1, Image{ fromFile = d .. "/chars.png" }, Point(0, 0)); ch.isVisible = false; ch.isEditable = false
local g = spr:newLayer(); g.name = "VODITKA (neexportovat)"
spr:newCel(g, 1, Image{ fromFile = d .. "/guides.png" }, Point(0, 0)); g.isVisible = false; g.isEditable = false
spr:loadPalette(pal)
app.activeLayer = paint
spr:saveAs(o .. "/BurningBearStreet_1067x600.aseprite")
print("ok")
