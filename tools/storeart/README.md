# Steam store + library artwork

`store_art.py` composes the key art (Marti's main-menu painting, `tools/storeart/key_art.jpg`) at night with the main
menu's title as the game has it since 2026-11-24 (Městská džungle): MORKEZELA in peeling Bungee letters on a crumbling
concrete lintel, a mint UPPER, ivy over the top edge, glowing mycelium in the cracks (tools/artgen/menu_skins.py
`jungle_title(k)`, drawn at each format's size).

```sh
python3 tools/storeart/store_art.py                        # → tools/storeart/out/ (git-ignored) + _contact_sheet.png
python3 tools/storeart/store_art.py --art path/to/scan.png  # a new key art (a scan), same compositions
python3 tools/storeart/store_art.py --demo                 # the demo app's set → tools/storeart/out/demo/
python3 tools/storeart/store_art.py --theme brutal [--demo]  # an earlier menu look → out/brutal/ (+ demo/)
python3 tools/storeart/store_art.py --theme vitraz [--demo]  # → out/vitraz/ (+ demo/)
python3 tools/storeart/store_art.py --theme glow [--demo]    # → out/glow/ (+ demo/)
python3 tools/storeart/store_art.py --day                  # the painting at its own brightness (no night grade)
```

**Night grade** (default since 2026-11-24; the bare white paper read too bright): `night()` dims the whole painting
before the crops (gamma, the bright grey paper sunk into indigo, a cool tint, colour pushed back up) and keeps the
day's light in a few soft pools (`POOLS`, fractions of the painting: the Egg Cathedral's shell, the green haze, the
clock spider, the bear, Edgar) with a faint halo; `vignette()` darkens each format's edges after its crop. `--day`
turns both off.

`--theme` draws the title, the DEMO tag and the icons in one of the main menu's looks (`ui/mainMenuBand.js`; the ones
tried on 2026-11-24 are kept, tools/menu_trials/README.md): **jungle** (the default = the game's menu), **brutal**
(UPPER in acid Space Grotesk, MORKEZELA in white Bebas Neue with a gear for the O, the acid rule + A WEIRD GAME; DEMO
an acid tag on the subtitle line; the icon a white gear with acid mushrooms), **vitraz** (the title on a violet
stained-glass plate, Morkezela in UnifrakturMaguntia, Cinzel; DEMO on an amber pane; the gear in gold on a round
window) or **glow** (neon MORKEZELA in Monoton with a cyan glow, Comfortaa, indigo shades; DEMO in a magenta neon
frame; the gear as a neon outline) or **jungle** (Městská džungle: the menu's concrete lintel with the peeling
sign letters, ivy and glowing mycelium, drawn big by tools/artgen/menu_skins.py `jungle_title(k)`; DEMO on a concrete
plate under it; the icon a concrete gear with ivy and glowing mushrooms). The crops, the hero and the page background
are the same in all of them.
`out/_themes_compare.png` puts the four side by side.

`key_art.jpg` is the painting flattened from the phone photo of 2026-11-23 (`tools/artgen/menu_painting.py photo.jpg
painting.png`, 1960×1386). The hero (3840 wide) is upscaled from it; a scan would make it sharper (flatten it the same
way, save it over `key_art.jpg`, check the crops). Crops are boxes in fractions of the painting (`crop` in `build()`),
so another resolution keeps the compositions. The portrait capsules and the soundtrack cover add black above the
painting (`extend_top`) so the title sits clear of the cathedral's spire.

`--demo` puts a **DEMO** sign (jungle: a concrete plate hung on rusty wires under the lintel) on every capsule, the library capsule/header and the library
logo (a demo's capsules and library assets have to show it's a demo); the hero and the page background stay
text-free. Upload them to the demo app (5564540), not to the full game. The previous set (AI painting + pixel logo,
2026-10-30) is kept in `out/_old_2026-10-30/`.

| File | Steamworks slot | Notes |
|---|---|---|
| `header_capsule_920x430.png` | Store → Header Capsule | also `library_header_920x430.png` (Library → Header) |
| `small_capsule_462x174.png` | Store → Small Capsule | name only (no subtitle) so it reads at 120×45 |
| `main_capsule_1232x706.png` | Store → Main Capsule | |
| `vertical_capsule_748x896.png` | Store → Vertical Capsule | |
| `page_background_1438x810.png` | Store → Page Background | ambient, no text |
| `library_capsule_600x900.png` | Library → Capsule | |
| `library_hero_3840x1240.png` | Library → Hero | no text allowed; keep the subject in the centred 860×380 safe area |
| `library_logo_1280.png` | Library → Logo | transparent PNG; place it in the Steamworks preview tool |
| `community_icon_184x184.jpg` | Community icon | the title's gear, white on black, acid mushrooms |
| `shortcut_icon.ico` | Client icon (shortcut) | the same on a rounded black tile, 16–256 px |

Rules (partner.steamgames.com/doc/store/assets, checked 2026-10-30): capsules hold the art and the game's title only —
no quotes, scores, "demo" / "wishlist" / sale text (time-limited text goes into Artwork Overrides). Screenshots come
from `tools/trailer/capture.sh --screenshots`.

Where each crop looks (`crop`) and where the title sits (`put_title`) is set per format in `build()`;
a new painting usually needs only those numbers changed. `tools/soundtrack/build.py` uses the same pieces for the
album cover (ORIGINAL SOUNDTRACK on the subtitle line).
