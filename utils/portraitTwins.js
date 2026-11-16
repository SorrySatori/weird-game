/**
 * Dialog busts from the 1x original sheets.
 *
 * The world sprites sit on the game's 2x pixel grid (tools/artgen/grid2x.py: one art pixel = 2x2 screen pixels). A bust
 * is a sheet frame at zoom 2 (dialogPortraits `{ key, frame, zoom: 2, top }`), which on a 2x sheet would give 4x
 * pixels. So for these sheets the 1x original (assets/images/characters/1x/, same relative path) is loaded alongside
 * as `<key>@1x`, and utils/dialogLayouts.js draws the bust from it: still 2x pixels on screen, with today's detail.
 */
const TWINS = new Set([
    'liris_idle.png', 'elphi_idle.png', 'clerk_applications.png', 'guardian.png', 'edgar_eskola.png', 'lamps/don.png',
    'heliodor_idle.png', 'ravla_idle.png', 'gnur.png', 'ortolan_idle.png', 'feral_toast/telka.png',
    'dreamqueue/mime.png', 'dreamqueue/vowel_seller.png', 'dreamqueue/hollow_woman.png', 'senior_clerk.png',
]);
const DIR = 'assets/images/characters/';

export const twinKey = key => `${key}@1x`;

/** Called first in GameScene.preload: a sheet from the list also loads its 1x twin under twinKey(key). */
export function loadPortraitTwins(loader) {
    if (loader.__portraitTwins) return;   // the loader outlives scene restarts
    loader.__portraitTwins = true;
    const sheet = loader.spritesheet.bind(loader);
    loader.spritesheet = (key, url, config, ...rest) => {
        const out = sheet(key, url, config, ...rest);
        const rel = typeof url === 'string' ? url.replace(/^\.\//, '') : '';
        if (rel.startsWith(DIR) && TWINS.has(rel.slice(DIR.length))) sheet(twinKey(key), DIR + '1x/' + rel.slice(DIR.length), config);
        return out;
    };
}
