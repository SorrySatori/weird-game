-- Exports the menu kit from the Aseprite sources into the game (touch-ups in "UPRAVY" included).
-- aseprite -b --script-param src=assets/aseprite --script-param dst=assets/images/ui/menu [--script-param only=ledger] --script tools/artgen/menu_export.lua
-- The ADD glow sheets (menu_button_glow, menu_panel_*_glow, menu_logo_glow) and menu_spore come straight from the generator.
local src, dst = app.params["src"], app.params["dst"]

local function export(name, png, cols)
  local s = app.open(src .. "/" .. name .. ".aseprite")
  for _, l in ipairs(s.layers) do l.isVisible = (l.name == "kresba" or l.name == "UPRAVY") end
  local n = #s.frames
  cols = cols or n
  local rows = math.ceil(n / cols)
  local sheet = Image(s.width * cols, s.height * rows, ColorMode.RGB)
  for i = 1, n do
    local img = Image(s.width, s.height, ColorMode.RGB)
    img:drawSprite(s, i)
    sheet:drawImage(img, Point(((i - 1) % cols) * s.width, math.floor((i - 1) / cols) * s.height))
  end
  sheet:saveAs(dst .. "/" .. png .. ".png")
  s:close()
end

export("UI_MenuTab_68x20", "menu_tab", 3)
export("UI_MenuCard_24x24", "menu_card", 2)
export("UI_MenuRail_10x32", "menu_rail", 1)
export("UI_MenuChevron_8x8", "menu_chevron", 4)
export("UI_MenuItemSlot_40x40", "menu_islot", 4)
export("UI_MenuCoin_12x12", "menu_coin", 1)
export("UI_MenuPanel_ledger", "menu_panel_ledger")
if app.params["only"] == "ledger" then print("ok") return end

export("UI_MenuButtons_192x48", "menu_button", 11)
export("UI_MenuSlots_228x26", "menu_slot", 4)
export("UI_MenuSmall_20x20", "menu_small", 9)
export("UI_MenuLogo_344x100", "menu_logo", 8)
export("UI_MenuSlider_136x16", "menu_slider", 2)
export("UI_MenuSliderFill_136x16", "menu_slider_fill", 1)
export("UI_MenuKnob_16x16", "menu_knob", 8)
export("UI_MenuToggle_40x20", "menu_toggle", 4)
for _, k in ipairs({ "pause", "slots", "lang", "settings" }) do export("UI_MenuPanel_" .. k, "menu_panel_" .. k) end
print("ok")
