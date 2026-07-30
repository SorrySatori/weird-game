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

    // --- Remaining inventory placeholders — uncomment each as you draw it ---
    // Story / quest items:
    // { key: 'chrono-slurry-toadlet',     path: 'assets/images/items/chrono-slurry-toadlet.png' },   // prophetic toad in a brass jar
    // { key: 'corrosive_cultivar',        path: 'assets/images/items/corrosive_cultivar.png' },       // rot-plant that eats metal
    // { key: 'godgraveyard-access-permit',path: 'assets/images/items/godgraveyard-access-permit.png' },
    // { key: 'forged-arms-permission',    path: 'assets/images/items/forged-arms-permission.png' },
    // Ortolan "extra arms" quest chain (forms = one visual family; game pieces = another):
    // { key: 'game-prototype',            path: 'assets/images/items/game-prototype.png' },
    // { key: 'probability-die',           path: 'assets/images/items/probability-die.png' },
    // { key: 'worldwright-piece',         path: 'assets/images/items/worldwright-piece.png' },
    // { key: 'luck-token',                path: 'assets/images/items/luck-token.png' },
    // { key: 'strategy-guide',            path: 'assets/images/items/strategy-guide.png' },
    // { key: 'fate-altering-piece',       path: 'assets/images/items/fate-altering-piece.png' },
    // { key: 'creative-spores',           path: 'assets/images/items/creative-spores.png' },
    // { key: 'rulebook-fragment',         path: 'assets/images/items/rulebook-fragment.png' },
    // { key: 'silent-sentence',           path: 'assets/images/items/silent-sentence.png' },
    // { key: 'artisan-exemption-form',    path: 'assets/images/items/artisan-exemption-form.png' },
    // { key: 'deformity-form',            path: 'assets/images/items/deformity-form.png' },
    // { key: 'special-dispensation',      path: 'assets/images/items/special-dispensation.png' },
    // { key: 'temporary-permit',          path: 'assets/images/items/temporary-permit.png' },
    // Voxmarket shop stock:
    // { key: 'trinket_box',               path: 'assets/images/items/trinket_box.png' },
    // { key: 'crystal_vial',              path: 'assets/images/items/crystal_vial.png' },
    // { key: 'market_map',                path: 'assets/images/items/market_map.png' },
    // { key: 'forgotten_elevator_button', path: 'assets/images/items/forgotten_elevator_button.png' },
];
