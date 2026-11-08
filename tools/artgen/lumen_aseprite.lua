-- Builds the Aseprite sources of the Lumen Directorate backgrounds from a lumen_bg.py / lumen_int_bg.py output dir:
--   assets/aseprite/LumenDirectorate_1067x600.aseprite          base + hidden GROWTH / DECAY variant layers + the
--                                                                surplus bloom (growth only, its own layer) + UPRAVY
--   assets/aseprite/LumenDirectorateInterior_1067x600.aseprite  base + UPRAVY
-- aseprite -b --script-param dir=<outdir> --script-param out=assets/aseprite --script tools/artgen/lumen_aseprite.lua
-- (OVERWRITES both files, incl. their UPRAVY layers.)
local dir, out = app.params["dir"], app.params["out"]

local function layer(s, name, file, visible, x, y)
    local l = s:newLayer(); l.name = name
    s:newCel(l, 1, Image{ fromFile = dir .. "/" .. file }, Point(x or 0, y or 0))
    l.isVisible = visible
    return l
end

-- the exterior with its Growth/Decay variants
local s = Sprite(1067, 600, ColorMode.RGB)
local base = s.layers[1]; base.name = "LUMEN pozadi (Claude)"
s:newCel(base, 1, Image{ fromFile = dir .. "/lumen.png" }, Point(0, 0))
layer(s, "GROWTH varianta (export -> _growth.png)", "lumen_growth.png", false)
layer(s, "DECAY varianta (export -> _decay.png)", "lumen_decay.png", false)
-- the harvestable bloom: a separate sprite in the game (props/lumen_surplus_bloom.png at canvas 879,427)
layer(s, "GROWTH nadbytecny kvet (props/lumen_surplus_bloom.png @879,427)", "surplus_bloom.png", false, 879, 427)
local up = s:newLayer(); up.name = "UPRAVY - kresli sem"
app.activeLayer = up
s:saveAs(out .. "/LumenDirectorate_1067x600.aseprite")
s:close()

-- the great hall
local t = Sprite(1067, 600, ColorMode.RGB)
local b2 = t.layers[1]; b2.name = "LUMEN SAL pozadi (Claude)"
t:newCel(b2, 1, Image{ fromFile = dir .. "/lumen_int.png" }, Point(0, 0))
local up2 = t:newLayer(); up2.name = "UPRAVY - kresli sem"
app.activeLayer = up2
t:saveAs(out .. "/LumenDirectorateInterior_1067x600.aseprite")
t:close()
print("ok")
