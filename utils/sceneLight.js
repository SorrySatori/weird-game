/**
 * The scene's light on its characters: every character sprite (utils/characterSheets.js, the protagonist included)
 * takes the colour and the colourfulness of the light where it stands, measured from the scene's background
 * (tools/artgen/scene_light.py -> utils/sceneLightTable.js: [colour, saturation]). Grey-green and a little faded under
 * the overcast sky, warm and full in a lamp-lit tavern, darker in dark places: the characters stop looking pasted on.
 *
 * One colour matrix per sprite (a WebGL preFX): first the saturation, then the colour, so the light's own hue isn't
 * faded with the sprite. Without WebGL it falls back to a plain tint (colour only).
 *
 * Applied on the first frame a sprite is drawn, not when it is made, so the scene's own touches come first: a sprite
 * the scene tinted itself (the protagonist's green glow) and the dialog portraits are left alone.
 * Scenes missing from the table are left as they are.
 */
import { isCharacterSprite } from './characterSheets.js';
import { SCENE_LIGHT } from './sceneLightTable.js';

/** saturation s (0 grey .. 1 as drawn) then the colour: rows of a 4x5 colour matrix (Phaser.Display.ColorMatrix) */
function lightMatrix(tint, s) {
    const x = (1 + 2 * s) / 3, y = (1 - s) / 3;          // Phaser's saturate(v) with v = s - 1
    const [r, g, b] = [(tint >> 16) & 255, (tint >> 8) & 255, tint & 255].map(c => c / 255);
    return [
        r * x, r * y, r * y, 0, 0,
        g * y, g * x, g * y, 0, 0,
        b * y, b * y, b * x, 0, 0,
        0, 0, 0, 1, 0,
    ];
}

export function applySceneLight(scene) {
    const light = SCENE_LIGHT[scene.sys.settings.key];
    if (!light) return;
    const [tint, sat] = light;
    const matrix = lightMatrix(tint, sat);
    const pending = new Set();
    const added = obj => { if (isCharacterSprite(obj)) pending.add(obj); };
    const lightUp = () => {
        if (!pending.size) return;
        for (const obj of pending) {
            if (!obj.active || obj.isTinted || obj.blendMode !== Phaser.BlendModes.NORMAL) continue;  // the scene's own colour
            if (obj.scrollFactorX !== 1 || (obj.parentContainer?.depth ?? 0) >= 100) continue;       // UI: dialog portraits
            const fx = obj.preFX?.addColorMatrix();
            if (fx) fx.set(matrix); else obj.setTint(tint);
        }
        pending.clear();
    };
    scene.events.on('addedtoscene', added);
    scene.events.on('prerender', lightUp);
    scene.events.once('shutdown', () => { scene.events.off('addedtoscene', added); scene.events.off('prerender', lightUp); });
}
