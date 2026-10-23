-- Builds the intro's Aseprite sources from the generator output.
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<gpl> --script intro_aseprite.lua
-- Layer names ending in "UPRAVY" are for hand touch-ups; intro_export.lua merges each into the image above it.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]

local function layer(spr, name, file, opts)
  local l = spr:newLayer(); l.name = name
  if file then spr:newCel(l, 1, Image{ fromFile = d .. "/" .. file }, Point((opts and opts.x) or 0, (opts and opts.y) or 0)) end
  if opts and opts.hidden then l.isVisible = false end
  if opts and opts.locked then l.isEditable = false end
  return l
end

-- 1. the Hymnar (Obazoba's sacred mushroom), 1067x1000 (the scene pans down it)
local s = Sprite(1067, 1000, ColorMode.RGB)
s.layers[1].name = "hymnar"
s:newCel(s.layers[1], 1, Image{ fromFile = d .. "/hymnar.png" }, Point(0, 0))
local paint = layer(s, "hymnar UPRAVY")
layer(s, "lupeny zare (ADD)", "hymnar_gills.png", { hidden = true })
layer(s, "zily zare (ADD)", "hymnar_glow.png", { hidden = true })
s:loadPalette(pal)
app.activeLayer = paint
s:saveAs(o .. "/Intro_Hymnar_1067x1000.aseprite")
s:close()

-- 2. the Council chamber, 1067x600: background, glow, the table (its own layer: drawn over the seats, under the
--    archpriests), and a locked preview of where the characters sit
local c = Sprite(1067, 600, ColorMode.RGB)
c.layers[1].name = "pozadi"
c:newCel(c.layers[1], 1, Image{ fromFile = d .. "/council_bg.png" }, Point(0, 0))
local cpaint = layer(c, "pozadi UPRAVY")
layer(c, "zare (ADD)", "council_glow.png", { hidden = true })
layer(c, "stul", "council_table.png")
layer(c, "stul UPRAVY")
layer(c, "POSTAVY nahled (neexportovat)", "council_preview.png", { locked = true })
c:loadPalette(pal)
app.activeLayer = cpaint
c:saveAs(o .. "/Intro_CouncilChamber_1067x600.aseprite")
c:close()

-- 3. the council members: one file each, frames tagged idle / talk
local function character(name, fw, fh, n, tags)
  local spr = Sprite(fw, fh, ColorMode.RGB)
  local base = spr.layers[1]; base.name = name
  for i = 1, n do
    if i > 1 then spr:newEmptyFrame() end
    spr:newCel(base, i, Image{ fromFile = d .. "/" .. name .. "/" .. (i - 1) .. ".png" }, Point(0, 0))
  end
  local up = spr:newLayer(); up.name = name .. " UPRAVY"
  for _, t in ipairs(tags) do
    local tag = spr:newTag(t[2], t[3]); tag.name = t[1]
  end
  spr:loadPalette(pal)
  app.activeLayer = up
  spr:saveAs(o .. "/Intro_Council_" .. name .. ".aseprite")
  spr:close()
end
for _, name in ipairs({ "varhun", "tynri", "rhull" }) do
  character(name, 128, 176, 8, { { "idle", 1, 4 }, { "talk", 5, 8 } })
end
character("elder_l", 200, 350, 4, { { "idle", 1, 4 } })
character("elder_r", 200, 350, 4, { { "idle", 1, 4 } })
print("ok")
