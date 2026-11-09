/**
 * What things are worth when the player sells them (a shop pays value × its sellMultiplier). An item bought in a shop
 * carries its own `price`; curiosities that were given rather than bought are valued here by id -- so the copies already
 * sitting in older saves are worth something too. Quest items are never for sale: selling one could block the story.
 */
export const ITEM_VALUES = {
    // Ortolan's thank-you curiosities (utils/OrtolanArms.js)
    'game-prototype': 40, 'black-cactus-card': 60, 'legged-shark-statuette': 30, 'hopsalot-figurine': 30, 'apocalypse-cop-figure': 34,
    // keepsakes from the dream queue in the Registration (ShedRegistrationScene)
    'silent-sentence': 24, 'rulebook-fragment': 20,
};

/** the main and side quests need these -- a shop won't take them */
export const UNSELLABLE = new Set([
    'vestigel', 'living-core', 'scraper_backyard_key', 'forgotten_elevator_button',
    'artisan-exemption-form', 'deformity-form', 'special-dispensation', 'temporary-permit', 'forged-arms-permission',
]);

export const itemValue = (item) => item?.price || ITEM_VALUES[item?.id] || 0;
export const isSellable = (item) => !!item && !UNSELLABLE.has(item.id) && item.type !== 'key_item' && itemValue(item) > 0;
