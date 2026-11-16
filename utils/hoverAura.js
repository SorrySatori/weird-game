/**
 * The hover aura: a soft green glow round a character the pointer is over (a WebGL preFX glow; scaling the sprite
 * would smear the pixel art). Every character gets it:
 *
 *  - automatically, any interactive sprite whose texture is a character sheet (loaded from assets/images/characters/):
 *    GameScene.preload calls autoHoverAura (utils/characterSheets.js knows the sheets), no scene code needed;
 *  - explicitly, with addHoverAura, where the thing hovered isn't the character sprite itself (a container or a zone
 *    round it, a whole band) or the glow has its own colour (Don Girandole's lamp light). Those are left alone by the
 *    automatic one.
 *
 * No aura while a dialog is open (a character behind the dialog would light up).
 */
import { isCharacterSprite } from './characterSheets.js';

export const AURA_COLOR = 0x7fff8e;

const glow = (sprite, color) => sprite.preFX?.addGlow(color, 2, 0, false, 0.1, 8);

/** `target` (a sprite, container or zone) lights `sprites` (default: itself) while the pointer is over it. */
export function addHoverAura(target, sprites = [target], color = AURA_COLOR) {
    target.__hoverAura = true;
    let lit = [];
    const off = () => { lit.forEach(([s, fx]) => s.preFX?.remove(fx)); lit = []; };
    const on = () => {
        if (lit.length || target.scene?.dialogVisible) return;
        lit = sprites.filter(s => s.active).map(s => [s, glow(s, color)]).filter(([, fx]) => fx);
    };
    target.on('pointerover', on);
    target.on('pointerout', off);
    target.once('destroy', off);
    return { on, off };
}

/** Lights any interactive character sprite the pointer goes over (unless addHoverAura already handles it). */
export function autoHoverAura(scene) {
    const lit = new Map();
    const over = (pointer, obj) => {
        if (obj.__hoverAura || !isCharacterSprite(obj) || lit.has(obj) || scene.dialogVisible) return;
        const fx = glow(obj, AURA_COLOR);
        if (fx) { lit.set(obj, fx); obj.once('destroy', () => lit.delete(obj)); }
    };
    const out = (pointer, obj) => {
        const fx = lit.get(obj);
        if (fx) { obj.preFX?.remove(fx); lit.delete(obj); }
    };
    scene.input.on('gameobjectover', over);
    scene.input.on('gameobjectout', out);
    scene.events.once('shutdown', () => {
        scene.input.off('gameobjectover', over);
        scene.input.off('gameobjectout', out);
        lit.clear();
    });
}
