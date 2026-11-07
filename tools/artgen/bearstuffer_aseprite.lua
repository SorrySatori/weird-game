-- Builds the Aseprite source of the bear stuffer on Burning Bear Street from bearstuffer.py (frame hold times included).
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<bearstuffer.gpl> --script bearstuffer_aseprite.lua
-- Draw touch-ups into the "UPRAVY" layer; bearstuffer_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local id = "bear_stuffer"
local holds = {}
for v in io.open(d .. "/" .. id .. "/durations.txt"):read("*l"):gmatch("%d+") do holds[#holds + 1] = tonumber(v) end
local first = Image{ fromFile = d .. "/" .. id .. "/0.png" }
local s = Sprite(first.width, first.height, ColorMode.RGB)
local base = s.layers[1]; base.name = id
for i = 1, #holds do
  if i > 1 then s:newEmptyFrame() end
  s:newCel(base, i, Image{ fromFile = d .. "/" .. id .. "/" .. (i - 1) .. ".png" }, Point(0, 0))
  s.frames[i].duration = holds[i] / 1000
end
local tag = s:newTag(1, #holds); tag.name = "vycpavani"
local up = s:newLayer(); up.name = id .. " UPRAVY"
s:loadPalette(pal)
app.activeLayer = up
s:saveAs(o .. "/Street_" .. id .. ".aseprite")
s:close()
print("ok")
