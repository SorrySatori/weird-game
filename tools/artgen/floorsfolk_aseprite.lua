-- Builds the Aseprite sources of the people on the Floors of Shed 521 from floorsfolk.py (frame hold times included).
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script floorsfolk_aseprite.lua
-- Draw touch-ups into the "UPRAVY" layer; floorsfolk_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
for _, id in ipairs({ "welcome_clerk", "dozer", "queue0", "queue1", "queue2", "queue3" }) do
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
  local tag = s:newTag(1, #holds); tag.name = "idle"
  local up = s:newLayer(); up.name = id .. " UPRAVY"
  s:loadPalette(pal)
  app.activeLayer = up
  s:saveAs(o .. "/ShedFloors_" .. id .. ".aseprite")
  s:close()
end
print("ok")
