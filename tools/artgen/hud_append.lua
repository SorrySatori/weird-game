-- Adds the frames the generator has but the HUD buttons' Aseprite source doesn't yet, keeping every touch-up
-- ("ikony UPRAVY") of the existing frames. Then export with hud_export.lua.
-- aseprite -b --script-param dir=<gen out> --script-param src=assets/aseprite --script tools/artgen/hud_append.lua
local d, src = app.params["dir"], app.params["src"]
local TAGS = { { "inventar", 1, 2 }, { "mapa", 3, 4 }, { "denik", 5, 6 }, { "ukoly", 7, 8 }, { "odznak", 9, 9 }, { "napoveda", 10, 11 } }
local s = app.open(src .. "/UI_HudButtons_48x48.aseprite")
local base
for _, l in ipairs(s.layers) do if l.name == "ikony" then base = l end end
local i = #s.frames + 1
while app.fs.isFile(d .. "/hud/" .. (i - 1) .. ".png") do
  s:newEmptyFrame()
  s:newCel(base, i, Image{ fromFile = d .. "/hud/" .. (i - 1) .. ".png" }, Point(0, 0))
  s.frames[i].duration = 0.6
  i = i + 1
end
local have = {}
for _, t in ipairs(s.tags) do have[t.name] = true end
for _, t in ipairs(TAGS) do
  if not have[t[1]] and t[3] <= #s.frames then local tag = s:newTag(t[2], t[3]); tag.name = t[1] end
end
s:saveAs(src .. "/UI_HudButtons_48x48.aseprite")
s:close()
print("ok " .. (i - 1) .. " frames")
