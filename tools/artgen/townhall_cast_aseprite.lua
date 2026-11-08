-- Builds the Aseprite sources of the Townhall cast from the generator output (townhall_cast.py).
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script townhall_cast_aseprite.lua
-- (OVERWRITES assets/aseprite/Townhall_<id>.aseprite incl. their UPRAVY layers.) Draw touch-ups into the "UPRAVY" layer;
-- townhall_cast_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local only = app.params["only"]
local CAST = {
  { "phor", 128, 160, 8 },
  { "clerk", 128, 160, 8 },
  { "eater", 128, 144, 8 },
  { "seraphel", 128, 192, 8 },
  { "poet", 128, 144, 8 },
}
for _, m in ipairs(CAST) do
  local id, w, h, n = m[1], m[2], m[3], m[4]
  if only == nil or only == "" or string.find("," .. only .. ",", "," .. id .. ",", 1, true) then
    local s = Sprite(w, h, ColorMode.RGB)
    local base = s.layers[1]; base.name = id
    for i = 1, n do
      if i > 1 then s:newEmptyFrame() end
      s:newCel(base, i, Image{ fromFile = d .. "/" .. id .. "/" .. (i - 1) .. ".png" }, Point(0, 0))
      s.frames[i].duration = 0.2
    end
    local tag = s:newTag(1, n); tag.name = "ceka"
    local up = s:newLayer(); up.name = id .. " UPRAVY"
    s:loadPalette(pal)
    app.activeLayer = up
    s:saveAs(o .. "/Townhall_" .. id .. ".aseprite")
    s:close()
  end
end
print("ok")
