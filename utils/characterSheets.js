/**
 * Which textures are character sheets: the ones loaded from assets/images/characters/. Used by the hover aura
 * (utils/hoverAura.js) and the scene light (utils/sceneLight.js).
 */
const CHARACTER_KEYS = new Set();   // module-wide: a sheet loaded on an earlier visit stays in the texture manager

/** Called first in GameScene.preload, so the scene's own sheets (and the protagonist's) are seen loading. */
export function trackCharacterSheets(loader) {
    if (loader.__characterSheets) return;   // the loader outlives scene restarts
    loader.__characterSheets = true;
    loader.on('load', file => {
        if (/assets\/images\/characters\//.test(file.url)) CHARACTER_KEYS.add(file.key);
    });
}

export const isCharacterSprite = obj => obj?.type === 'Sprite' && CHARACTER_KEYS.has(obj.texture?.key);
