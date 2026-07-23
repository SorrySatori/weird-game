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
export const ITEM_ICONS = [
    // --- Keys (first hand-drawn batch) ---
    { key: 'townhall-key',         path: 'assets/images/items/townhall-key.png' },
    { key: 'scraper_backyard_key', path: 'assets/images/items/scraper_backyard_key.png' },

    // --- Other placeholder items awaiting art — uncomment as each is drawn ---
    // { key: 'chrono-slurry-toadlet',   path: 'assets/images/items/chrono-slurry-toadlet.png' },
    // { key: 'godgraveyard-access-permit', path: 'assets/images/items/godgraveyard-access-permit.png' },
    // { key: 'forged-arms-permission',  path: 'assets/images/items/forged-arms-permission.png' },
    // { key: 'grayOltrac',              path: 'assets/images/items/grayOltrac.png' },
    // { key: 'violetOltrac',            path: 'assets/images/items/violetOltrac.png' },
    // { key: 'amberOltrac',             path: 'assets/images/items/amberOltrac.png' },
    // NOTE: 'dream_cartridge' has only an icon: field (ignored by the resolver) — after drawing,
    //       also give that item a texture:'dream_cartridge' field so it resolves.
    // { key: 'dream_cartridge',         path: 'assets/images/items/dream_cartridge.png' },
    // NOTE: 'corrosive_cultivar' has only an image: field (ignored) — same fix (add texture:).
    // { key: 'corrosive_cultivar',      path: 'assets/images/items/corrosive_cultivar.png' },
];
