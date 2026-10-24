-- Builds the HUD buttons' Aseprite source from the generator output (hud_buttons.py).
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script hud_aseprite.lua
-- Draw touch-ups into "ikony UPRAVY"; hud_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]
local TAGS = { { "inventar", 1, 2 }, { "mapa", 3, 4 }, { "denik", 5, 6 }, { "ukoly", 7, 8 }, { "odznak", 9, 9 } }

local s = Sprite(48, 48, ColorMode.RGB)
local base = s.layers[1]; base.name = "ikony"
for i = 1, 9 do
  if i > 1 then s:newEmptyFrame() end
  s:newCel(base, i, Image{ fromFile = d .. "/hud/" .. (i - 1) .. ".png" }, Point(0, 0))
  s.frames[i].duration = 0.6
end
for _, t in ipairs(TAGS) do
  local tag = s:newTag(t[2], t[3]); tag.name = t[1]
end
local up = s:newLayer(); up.name = "ikony UPRAVY"
s:loadPalette(pal)
app.activeLayer = up
s:saveAs(o .. "/UI_HudButtons_48x48.aseprite")
s:close()
print("ok")
