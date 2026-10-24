-- Builds the symbiont HUD's Aseprite sources from the generator output (symbionts.py).
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script symbionts_aseprite.lua
-- Layers ending in "UPRAVY" are for hand touch-ups; symbionts_export.lua merges them in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local IDS = { "thorne-still", "neme-crownmire", "ulvarex-borrowed-horizon", "brine-scripture", "osswine", "palinode", "generic" }

-- 1. the symbionts: 32x32, one tag of 4 idle frames per symbiont (0 rest / 1 breath / 2 blink-glint / 3 accent)
local s = Sprite(32, 32, ColorMode.RGB)
local base = s.layers[1]; base.name = "symbionti"
local n = 0
for _, id in ipairs(IDS) do
  for f = 0, 3 do
    n = n + 1
    if n > 1 then s:newEmptyFrame() end
    s:newCel(base, n, Image{ fromFile = d .. "/symb/" .. id .. "/" .. f .. ".png" }, Point(0, 0))
    s.frames[n].duration = 0.25
  end
  local tag = s:newTag(n - 3, n); tag.name = id
end
local up = s:newLayer(); up.name = "symbionti UPRAVY"
s:loadPalette(pal)
app.activeLayer = up
s:saveAs(o .. "/UI_Symbionts_32x32.aseprite")
s:close()

-- 2. the pods of the "rosary": frame 1 open pod, 2 sealed pod, 3 end of the cord, 4 glow (ADD, tinted per symbiont).
--    The hidden "maska retu" marks which pixels of the open pod sit IN FRONT of the symbiont (the lower lip).
local p = Sprite(48, 58, ColorMode.RGB)
local pod = p.layers[1]; pod.name = "lusk"
for _ = 2, 4 do p:newEmptyFrame() end
p:newCel(pod, 1, Image{ fromFile = d .. "/pod/open.png" }, Point(0, 0))
p:newCel(pod, 2, Image{ fromFile = d .. "/pod/sealed.png" }, Point(0, 0))
p:newCel(pod, 3, Image{ fromFile = d .. "/pod/end.png" }, Point(0, 0))
local podUp = p:newLayer(); podUp.name = "lusk UPRAVY"
local mask = p:newLayer(); mask.name = "maska retu (pred symbiontem)"
p:newCel(mask, 1, Image{ fromFile = d .. "/pod/lip.png" }, Point(0, 0)); mask.isVisible = false
local prev = p:newLayer(); prev.name = "nahled symbiontu (neexportovat)"
p:newCel(prev, 1, Image{ fromFile = d .. "/symb/neme-crownmire/0.png" }, Point(8, 15))
prev.isVisible = false; prev.isEditable = false
local glow = p:newLayer(); glow.name = "zare (ADD)"
p:newCel(glow, 4, Image{ fromFile = d .. "/pod/glow.png" }, Point(0, 0))
for i, name in ipairs({ "otevreny", "zapeceteny", "konec snury", "zare" }) do
  local tag = p:newTag(i, i); tag.name = name
end
p:loadPalette(pal)
app.activeLayer = podUp
p:saveAs(o .. "/UI_SymbiontPods_48x58.aseprite")
p:close()
print("ok")
