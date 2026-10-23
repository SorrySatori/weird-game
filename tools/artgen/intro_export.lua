-- Exports the intro art from the Aseprite sources into the game (hand touch-ups in the "UPRAVY" layers included).
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/intro --script intro_export.lua
local src, dst = app.params["src"], app.params["dst"]

-- flatten the named layers of one file into one PNG per output
local function exportLayers(file, outputs)
  local spr = app.open(src .. "/" .. file)
  for _, o in ipairs(outputs) do
    local want = {}
    for _, n in ipairs(o.layers) do want[n] = true end
    for _, l in ipairs(spr.layers) do l.isVisible = want[l.name] == true end
    spr:saveCopyAs(dst .. "/" .. o.out)
  end
  spr:close()
end

exportLayers("Intro_Hymnar_1067x1000.aseprite", {
  { out = "hymnar.png", layers = { "hymnar", "hymnar UPRAVY" } },
  { out = "hymnar_gills.png", layers = { "lupeny zare (ADD)" } },
  { out = "hymnar_glow.png", layers = { "zily zare (ADD)" } },
})
exportLayers("Intro_CouncilChamber_1067x600.aseprite", {
  { out = "council_bg.png", layers = { "pozadi", "pozadi UPRAVY" } },
  { out = "council_glow.png", layers = { "zare (ADD)" } },
  { out = "council_table.png", layers = { "stul", "stul UPRAVY" } },
})

-- character sheets: all frames side by side (back row 8 = idle 0-3 + talk 4-7, elders 4 = idle)
for _, name in ipairs({ "varhun", "tynri", "rhull", "elder_l", "elder_r" }) do
  local spr = app.open(src .. "/Intro_Council_" .. name .. ".aseprite")
  app.command.ExportSpriteSheet{
    ui = false, askOverwrite = false, type = SpriteSheetType.HORIZONTAL,
    textureFilename = dst .. "/council_" .. name .. ".png", dataFilename = "",
    trim = false, shapePadding = 0, borderPadding = 0, innerPadding = 0,
  }
  spr:close()
end
print("ok")
