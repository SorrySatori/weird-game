-- Exports the symbiont HUD art from the Aseprite sources into the game (hand touch-ups in the "UPRAVY" layers included).
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/ui --script tools/artgen/symbionts_export.lua
local src, dst = app.params["src"], app.params["dst"]

-- flatten the named layers of one frame
local function flat(spr, frame, layers)
  local want = {}
  for _, name in ipairs(layers) do want[name] = true end
  for _, l in ipairs(spr.layers) do l.isVisible = want[l.name] == true end
  local img = Image(spr.width, spr.height, ColorMode.RGB)
  img:drawSprite(spr, frame)
  return img
end

-- symbionts.png: 4 frames per row, one row per tag (symbiont), in frame order
local s = app.open(src .. "/UI_Symbionts_32x32.aseprite")
local sheet = Image(32 * 4, 32 * math.ceil(#s.frames / 4), ColorMode.RGB)
for i = 1, #s.frames do
  sheet:drawImage(flat(s, i, { "symbionti", "symbionti UPRAVY" }), Point(((i - 1) % 4) * 32, ((i - 1) // 4) * 32))
end
sheet:saveAs(dst .. "/symbionts.png")
s:close()

-- symbiont_pods.png: open pod / its lip (open pod cut by the mask) / sealed pod / cord end / glow
local p = app.open(src .. "/UI_SymbiontPods_48x58.aseprite")
local POD = { "lusk", "lusk UPRAVY" }
local open = flat(p, 1, POD)
local mask = flat(p, 1, { "maska retu (pred symbiontem)" })
local lip = Image(p.width, p.height, ColorMode.RGB)
for y = 0, p.height - 1 do
  for x = 0, p.width - 1 do
    if app.pixelColor.rgbaA(mask:getPixel(x, y)) > 0 then lip:drawPixel(x, y, open:getPixel(x, y)) end
  end
end
local out = Image(p.width * 5, p.height, ColorMode.RGB)
for i, img in ipairs({ open, lip, flat(p, 2, POD), flat(p, 3, POD), flat(p, 4, { "zare (ADD)" }) }) do
  out:drawImage(img, Point((i - 1) * p.width, 0))
end
out:saveAs(dst .. "/symbiont_pods.png")
p:close()
print("ok")
