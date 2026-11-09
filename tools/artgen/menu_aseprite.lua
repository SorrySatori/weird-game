-- Builds the menu kit's Aseprite sources from the generator output (menu_ui.py + menu_logo.py).
-- aseprite -b --script-param dir=<gen out> --script-param out=assets/aseprite --script-param pal=<menu.gpl> [--script-param only=ledger] --script menu_aseprite.lua
-- only=ledger builds just the journal / quest-log / inventory pieces (tabs, cards, rail, chevron, sockets, coin, ledger
-- panel) and leaves the rest.
-- Draw touch-ups into the "UPRAVY" layer of each file; menu_export.lua merges it in.
local d, o, pal = app.params["dir"], app.params["out"], app.params["pal"]

local function build(name, w, h, frames, tags, duration)
  local s = Sprite(w, h, ColorMode.RGB)
  local base = s.layers[1]; base.name = "kresba"
  for i, file in ipairs(frames) do
    if i > 1 then s:newEmptyFrame() end
    s:newCel(base, i, Image{ fromFile = file }, Point(0, 0))
    s.frames[i].duration = duration or 0.11
  end
  for _, t in ipairs(tags or {}) do
    local tag = s:newTag(t[2], t[3]); tag.name = t[1]
  end
  local up = s:newLayer(); up.name = "UPRAVY"
  s:loadPalette(pal)
  app.activeLayer = up
  s:saveAs(o .. "/" .. name .. ".aseprite")
  s:close()
end

local function seq(dir, n)
  local t = {}
  for i = 0, n - 1 do t[#t + 1] = d .. "/menu/" .. dir .. "/" .. i .. ".png" end
  return t
end

-- the journal / quest log (ui/LedgerPanel.js)
build("UI_MenuTab_68x20", 68, 20, seq("menu_tab", 3), { { "klid", 1, 1 }, { "najeti", 2, 2 }, { "vybrana", 3, 3 } }, 0.5)
build("UI_MenuCard_24x24", 24, 24, seq("menu_card", 2), { { "klid", 1, 1 }, { "rozsvicena", 2, 2 } }, 0.5)
build("UI_MenuRail_10x32", 10, 32, seq("menu_rail", 1))
build("UI_MenuChevron_8x8", 8, 8, seq("menu_chevron", 4), { { "zavreno", 1, 2 }, { "otevreno", 3, 4 } }, 0.5)
-- the inventory (systems/inventory/InventorySystem.js)
build("UI_MenuItemSlot_40x40", 40, 40, seq("menu_islot", 4), { { "prazdna", 1, 1 }, { "predmet", 2, 2 }, { "najeti", 3, 3 }, { "vybrana", 4, 4 } }, 0.5)
build("UI_MenuCoin_12x12", 12, 12, seq("menu_coin", 1))
do
  local img = Image{ fromFile = d .. "/menu_panel_ledger.png" }
  build("UI_MenuPanel_ledger", img.width, img.height, { d .. "/menu_panel_ledger.png" })
end
if app.params["only"] == "ledger" then print("ok") return end

-- 3 variants x (0 idle, 1-8 hover loop, 9 pressed, 10 disabled)
build("UI_MenuButtons_192x48", 192, 48, seq("menu_button", 33),
      { { "myceny", 1, 11 }, { "chorose", 12, 22 }, { "muchomurka", 23, 33 } })
-- 0 idle, 1 hover, 2 pressed, 3 selected; empty slot / slot with a save
build("UI_MenuSlots_228x26", 228, 26, seq("menu_slot", 8), { { "volny", 1, 4 }, { "obsazeny", 5, 8 } }, 0.5)
build("UI_MenuSmall_20x20", 20, 20, seq("menu_small", 9), { { "vlevo", 1, 3 }, { "vpravo", 4, 6 }, { "zavrit", 7, 9 } }, 0.5)
build("UI_MenuLogo_344x100", 344, 100, seq("menu_logo", 8), { { "logo", 1, 8 } }, 0.2)
build("UI_MenuSlider_136x16", 136, 16, seq("menu_slider", 2), { { "trubice", 1, 1 }, { "zamereno", 2, 2 } }, 0.5)
build("UI_MenuSliderFill_136x16", 136, 16, seq("menu_slider_fill", 1))
build("UI_MenuKnob_16x16", 16, 16, seq("menu_knob", 8), { { "kolecko", 1, 4 }, { "rozsvicene", 5, 8 } }, 0.15)
build("UI_MenuToggle_40x20", 40, 20, seq("menu_toggle", 4), { { "vypnuto", 1, 2 }, { "zapnuto", 3, 4 } }, 0.5)
for _, k in ipairs({ "pause", "slots", "lang", "settings" }) do
  local img = Image{ fromFile = d .. "/menu_panel_" .. k .. ".png" }
  build("UI_MenuPanel_" .. k, img.width, img.height, { d .. "/menu_panel_" .. k .. ".png" })
end
print("ok")
