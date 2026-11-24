# Main-menu design trials

## 2026-11-23: full-screen designs

The six full-screen main-menu designs tried over Marti's painting before the Brutal band won, kept for reference
(they are not loaded by the game; `tools/` is left out of the build).

- `menuDesigns_trial_backup.js`: was `ui/menuDesigns.js`. Every design is one `build*()` function:
  - `buildGlass` (line 473) **Vitráž**: stained glass after the Egg Cathedral (violet title plate, glass panes in
    amber / teal / rose / violet, lead lines), title in UnifrakturMaguntia, labels in Cinzel; `GLASS`, `LEAD` and
    `glassPane()` (Voronoi glass cells) just above it.
  - `buildGlow` (line 280) **Bioluminiscence**: neon cyan + magenta glow on deep indigo, no panels; title in Monoton,
    labels in Comfortaa.
  - the others: `buildPaper` (Ateliér), `buildCabaret` (Kabaret), `buildSlab` (Brutal), `buildOffice` (Úřad), and
    the band layouts that led to today's menu (`buildBandSide`, `buildBandBottom`).
- `MainScene_trial_backup.js`: was `scenes/MainScene.js` at the time (the L key cycled the designs, `paintingLayout`
  placed the painting per design).

The fonts were in `assets/fonts/trial/`. Cinzel, UnifrakturMaguntia (Vitráž), Monoton and Comfortaa
(Bioluminiscence) are now in `assets/fonts/`: the band menu's trial themes use them (`ui/mainMenuBand.js`). All OFL, from
github.com/google/fonts (the current files cover Czech diacritics). The other trial fonts (Caveat, Permanent Marker,
Abril Fatface, Cormorant Garamond, Black Ops One, Courier Prime) are on Google Fonts under the same names.

To run a design again: copy the file back to `ui/menuDesigns.js`, the fonts back to `assets/fonts/trial/`, and take
the design hook-up from `MainScene_trial_backup.js` (preloadMenuDesigns, buildMenuDesign, the L key).

## 2026-11-24: the band's looks, and the pick

Picked: **jungle** (Městská džungle) with the entries alone in the middle of the painting. The other eight looks
and the band layout are still in the code, only switched off for players, so any of them comes back in a second:

- `looks_2026-11-24_band.jpg`, `looks_2026-11-24_center.jpg`: all nine looks, band layout / entries in the middle.
- `store_art_themes_2026-11-24.jpg`: the Steam capsules with the title in Brutal, Vitráž, Bioluminiscence, jungle.

| id | name | where |
|---|---|---|
| `brutal` | Brutal (acid yellow on black) | `ui/mainMenuBand.js` THEMES |
| `vitraz` | Vitráž (Egg Cathedral glass) | `ui/mainMenuBand.js` THEMES |
| `glow` | Bioluminiscence (neon) | `ui/mainMenuBand.js` THEMES |
| `rust` | Rez (rusty sheet, caged lamps) | `ui/menuSkins.js` + `tools/artgen/menu_skins.py` |
| `biomech` | Biomechanika (bone, heartbeat pods) | `ui/menuSkins.js` + `tools/artgen/menu_skins.py` |
| `jungle` | Městská džungle: **the menu** | `ui/menuSkins.js` + `tools/artgen/menu_skins.py` |
| `crazy` | Totálně crazy (flesh, eyes, teeth) | `ui/menuSkins.js` + `tools/artgen/menu_skins.py` |
| `tripe` | Boltcovitka (Auricularia mesenterica) | `ui/menuSkins.js` + `tools/artgen/menu_skins.py` |
| `panelak` | Panelák (luxfery, steel lattice, neon) | `ui/menuSkins.js` + `tools/artgen/menu_skins.py` |

To look at one again:

- **In the game**: run it from the sources (`npm run electron`, or a browser). On the title screen **L** cycles the
  looks and **C** switches the layout (band on the left / entries in the middle). The choice is kept in the settings
  (`menuTrialTheme`, `menuTrialLayout` in localStorage `gameSettings`); cycle back to jungle + middle, or delete the two
  keys, to see the real menu again. The packaged game ignores both and has no L / C (`menuTrials()` in
  `ui/mainMenuBand.js`, `devBuild` from `preload.js`).
- **Stills**: `./tools/trailer/capture.sh --screenshots --only menu_panelak,menu_panelak_center --lang cs` (ids
  `menu_<id>`, `_center`, `_center_settings`, `_settings`, `_pause`) into `tools/trailer/out/stills/`.
- **The art** of a skin: `python3 tools/artgen/menu_skins.py <id> [--preview]`.
- **Steam art** in a look: `python3 tools/storeart/store_art.py --theme brutal|vitraz|glow [--demo]` (→ `out/<theme>/`;
  jungle is the default → `out/`).

To make another look THE menu: `MENU_LOOK` in `ui/mainMenuBand.js` (theme + layout).
