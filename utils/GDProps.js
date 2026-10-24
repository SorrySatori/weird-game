/**
 * GDProps — Growth/Decay scenery props shared by scenes.
 *
 * The world reacts to the Growth/Decay balance (GameScene.getGDTendency(): growthDominant ≥ 65,
 * decayDominant ≥ 65, else balanced). Besides the global colour wash (applyGDAmbience) a scene can
 *   1. swap its background for `<baseKey>_growth` / `<baseKey>_decay` art if that texture exists
 *      (missing files are tolerated — the loader just warns), and
 *   2. scatter a few props: small transparent sprites from assets/images/props/, placed in canvas
 *      coordinates. Props stand behind the player (depth 4 by default; the player is 20) and should
 *      keep their feet at y ≤ ~520 so the walk line (y 534) passes in front of them.
 *
 * Usage in a scene:
 *   preload():  preloadGDProps(this);  this.load.image('FooBg_growth', …); this.load.image('FooBg_decay', …);
 *   create():   applyGDBackground(this, bg, 'FooBg');
 *               placeGDProps(this, { growth: [{ prop: 'bush', x: 240, y: 492 }], decay: [{ prop: 'fire', x: 700, y: 500 }] });
 */

export const GD_PROPS = {
    bush:      { file: 'prop_bush_flowering.png' },
    vine:      { file: 'prop_vine_clump.png', origin: [0.5, 0] },      // hangs: anchor top-centre
    mushrooms: { file: 'prop_mushroom_cluster.png' },
    trash:     { file: 'prop_trash_pile.png' },
    crate:     { file: 'prop_crate_broken.png' },
    rubble:    { file: 'prop_rubble.png' },
    fire:      { file: 'prop_barrel_fire.png', frames: { frameWidth: 64, frameHeight: 112 }, anim: { key: 'gdprop_fire_burn', frameRate: 8 } }
};
const texKey = (name) => 'gdprop_' + name;

/** Queue every prop texture. Safe to call from any scene's preload(); Phaser ignores already-loaded keys. */
export function preloadGDProps(scene) {
    for (const [name, def] of Object.entries(GD_PROPS)) {
        const key = texKey(name);
        if (scene.textures.exists(key)) continue;
        const path = 'assets/images/props/' + def.file;
        if (def.frames) scene.load.spritesheet(key, path, def.frames);
        else scene.load.image(key, path);
    }
}

/**
 * Swap the background for its Growth/Decay variant when that art exists. Returns the texture key in use.
 * No tint fallback: the ambience wash already colours balanced-vs-tilted scenes; props carry the rest.
 */
export function applyGDBackground(scene, bg, baseKey) {
    const tendency = scene.getGDTendency ? scene.getGDTendency() : 'balanced';
    if (tendency === 'balanced' || !bg) return baseKey;
    const altKey = baseKey + (tendency === 'growthDominant' ? '_growth' : '_decay');
    if (!scene.textures.exists(altKey)) return baseKey;
    bg.setTexture(altKey);
    if (scene.fitBackground) scene.fitBackground(bg);
    return altKey;
}

/**
 * Place the props for the current tendency. `placements` = { growth: [...], decay: [...] } where each entry is
 * { prop, x, y, depth?, scale?, flipX? }. Returns the created sprites (empty when balanced or art is missing).
 */
export function placeGDProps(scene, placements) {
    const tendency = scene.getGDTendency ? scene.getGDTendency() : 'balanced';
    if (tendency === 'balanced') return [];
    return placeProps(scene, (tendency === 'growthDominant' ? placements.growth : placements.decay) || []);
}

/** Place props regardless of the tendency (scenery that is always there, e.g. a burning barrel). Same entry shape. */
export function placeProps(scene, list) {
    const made = [];
    for (const p of list) {
        const def = GD_PROPS[p.prop];
        const key = texKey(p.prop);
        if (!def || !scene.textures.exists(key)) continue;
        const sprite = scene.add.sprite(p.x, p.y, key)
            .setOrigin(...(def.origin || [0.5, 1]))
            .setDepth(p.depth ?? 4)
            .setScale(p.scale ?? 1)
            .setFlipX(!!p.flipX);
        if (def.anim) {
            if (!scene.anims.exists(def.anim.key)) {
                scene.anims.create({ key: def.anim.key, frames: scene.anims.generateFrameNumbers(key, { start: 0, end: 5 }), frameRate: def.anim.frameRate, repeat: -1 });
            }
            sprite.play(def.anim.key);
        }
        if (p.prop === 'fire') made.push(addFireGlow(scene, p.x, p.y, (p.depth ?? 4) - 1));
        made.push(sprite);
    }
    return made;
}

/** Warm, flickering light a burning barrel throws on the ground and nearby walls (additive, below the prop). */
function addFireGlow(scene, x, y, depth) {
    const glow = scene.add.graphics().setDepth(depth).setBlendMode(Phaser.BlendModes.ADD);
    for (let i = 4; i >= 1; i--) {
        glow.fillStyle(0xd9ad52, 0.05);
        glow.fillEllipse(x, y - 60, 40 * i, 44 * i);   // around the flames
        glow.fillEllipse(x, y - 4, 50 * i, 14 * i);    // spill on the ground
    }
    scene.tweens.add({ targets: glow, alpha: { from: 0.55, to: 1 }, duration: 260, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    return glow;
}
