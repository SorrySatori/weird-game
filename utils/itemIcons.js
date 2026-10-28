/**
 * Central registry of hand-drawn item ICON textures.
 *
 * Loaded once in LoadingScene.preload() (see scenes/LoadingScene.js), so every listed texture is
 * available game-wide — the inventory resolver (systems/inventory/InventorySystem.js) picks it up
 * in any scene and after loading a save, not just in the scene where the item was obtained.
 *
 * HOW TO ADD AN ICON:
 *   1. Draw it in Piskel at 60x60 (the game runs pixelArt:true and shows icons 1:1 → pixel-perfect).
 *      Export PNG with a transparent background.
 *   2. Save as assets/images/items/<key>.png where <key> matches the item's `id` (or its `texture`
 *      field). The resolver checks item.texture / item.id / name — NOT item.icon or item.image.
 *   3. Add a line below. Done — no per-scene load calls needed.
 *
 * A key whose file does not exist yet degrades gracefully to the lettered-circle placeholder
 * (LoadingScene suppresses the load error), so it is safe to list an icon before it is drawn.
 */
// NOTE: every item below resolves by its `id` (the resolver checks item.texture, then item.id,
// then the name). So the texture key MUST equal the item's id, and the file is <id>.png. No item
// definition needs editing — dream_cartridge (icon: field) and corrosive_cultivar (image: field)
// both still resolve because their id matches the key here.
export const ITEM_ICONS = [
    // --- Keys (done) ---
    { key: 'townhall-key',            path: 'assets/images/items/townhall-key.png' },
    { key: 'scraper_backyard_key',    path: 'assets/images/items/scraper_backyard_key.png' },

    // --- Current batch (active — drop the PNGs in and they show) ---
    { key: 'grayOltrac',              path: 'assets/images/items/grayOltrac.png' },     // Oltrac drug — gray (draw once, recolour ×3)
    { key: 'violetOltrac',            path: 'assets/images/items/violetOltrac.png' },   // Oltrac drug — violet
    { key: 'amberOltrac',             path: 'assets/images/items/amberOltrac.png' },    // Oltrac drug — amber (rarest)
    { key: 'dream_cartridge',         path: 'assets/images/items/dream_cartridge.png' },// "The Cardinal Feast" cartridge (the Bishop's last game)
    { key: 'ampule',                  path: 'assets/images/items/ampule.png' },         // sealed glass ampule — Zerren's sound recordings (shared icon, tinted per item)

    // --- Demo items, generated pixel art (tools/artgen/item_icons.py -> assets/aseprite/UI_ItemIcons_60x60.aseprite) ---
    { key: 'pliers',                    path: 'assets/images/items/pliers.png' },                    // for the Living Core
    { key: 'forgotten_elevator_button', path: 'assets/images/items/forgotten_elevator_button.png' }, // Zerren -> Lift-Mother
    { key: 'market_map',                path: 'assets/images/items/market_map.png' },
    // Ortolan's "extra arms" paperwork (forms = one visual family) ...
    { key: 'artisan-exemption-form',    path: 'assets/images/items/artisan-exemption-form.png' },
    { key: 'deformity-form',            path: 'assets/images/items/deformity-form.png' },
    { key: 'special-dispensation',      path: 'assets/images/items/special-dispensation.png' },
    { key: 'temporary-permit',          path: 'assets/images/items/temporary-permit.png' },
    { key: 'forged-arms-permission',    path: 'assets/images/items/forged-arms-permission.png' },
    { key: 'rulebook-fragment',         path: 'assets/images/items/rulebook-fragment.png' },
    { key: 'silent-sentence',           path: 'assets/images/items/silent-sentence.png' },
    // ... and his gifts for it (game pieces = another)
    { key: 'game-prototype',            path: 'assets/images/items/game-prototype.png' },
    { key: 'black-cactus-card',         path: 'assets/images/items/black-cactus-card.png' },        // once worth millions
    { key: 'probability-die',           path: 'assets/images/items/probability-die.png' },
    { key: 'hopsalot-figurine',         path: 'assets/images/items/hopsalot-figurine.png' },        // Maxim Hopsalot, sans six-pack
    { key: 'fate-altering-piece',       path: 'assets/images/items/fate-altering-piece.png' },
    // faction errands
    { key: 'chrono-slurry-toadlet',     path: 'assets/images/items/chrono-slurry-toadlet.png' },     // prophetic toad in a brass jar
    { key: 'corrosive_cultivar',        path: 'assets/images/items/corrosive_cultivar.png' },        // rot-plant that eats metal

    // --- Older art some scenes loaded only for themselves: registered here so the icon also shows after loading
    //     a save in another scene ---
    { key: 'vestigel',                  path: 'assets/images/items/vestigel.png' },
    { key: 'rust_feast',                path: 'assets/images/items/rust_feast.png' },
    { key: 'living-core',               path: 'assets/images/characters/living-core.png' },
    { key: 'oil',                       path: 'assets/images/items/oil.png' },
    { key: 'metal_scrap',               path: 'assets/images/items/metal_scrap.png' },
    { key: 'redmass',                   path: 'assets/images/items/redmass.png' },

    // --- Still placeholders (outside the demo) — uncomment each as you draw it ---
    // { key: 'godgraveyard-access-permit',path: 'assets/images/items/godgraveyard-access-permit.png' },
    // { key: 'filed_dossier',             path: 'assets/images/items/filed_dossier.png' },
    // { key: 'wimlick',                   path: 'assets/images/items/wimlick.png' },
];
