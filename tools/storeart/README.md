# Steam store + library artwork

`store_art.py` composes the key art (default: the main menu painting `assets/images/backgrounds/background.png`) with the
pixel-art logo (`tools/artgen/menu_logo.py`, store variant with "A WEIRD GAME") into every Steamworks format.

```sh
python3 tools/storeart/store_art.py                        # → tools/storeart/out/ (git-ignored) + _contact_sheet.png
python3 tools/storeart/store_art.py --art path/to/painting.png   # a new key art, same compositions
```

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
| `community_icon_184x184.jpg` | Community icon | |

Rules (partner.steamgames.com/doc/store/assets, checked 2026-10-30): capsules hold the art and the game's title only —
no quotes, scores, "demo" / "wishlist" / sale text (time-limited text goes into Artwork Overrides). Screenshots come
from `tools/trailer/capture.sh --screenshots`.

Where each crop looks (`fx`, `fy` in `crop_cover`) and where the logo sits (`put_logo`) is set per format in `build()`;
a new painting usually needs only those numbers changed.
