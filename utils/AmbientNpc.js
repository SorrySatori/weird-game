// Ambient people — animated figures that live in a scene without being characters you talk to.
// A click makes them say one line in a speech bubble (no dialog); they cycle through their lines
// (lang/<code>/ambient.js: ambient.<id>.lines) and the hover shows their name (ambient.<id>.name).
// Sprites are drawn at on-screen size (scale 1), feet-anchored, below the player (depth 6).

const TICK = 100; // ms per animation step: a frame is held for whole ticks (Phaser 3.88 ignores per-frame durations)

/**
 * @param {Phaser.Scene} scene - a GameScene (needs t() and showSpeechBubble())
 * @param {object} cfg - { id, key=id, x, y, holds, top, depth=6 }
 *   id: the lang key under ambient.*; key: the spritesheet texture; x, y: the feet (origin bottom-centre);
 *   holds: how long each frame stays (ms); top: the figure's height in px (where the bubble and the name go)
 * @returns {Phaser.GameObjects.Sprite}
 */
export function createAmbientNpc(scene, { id, key = id, x, y, holds, top, depth = 6 }) {
    const anim = `ambient_${key}`;
    if (!scene.anims.exists(anim)) {
        const frames = holds.flatMap((ms, frame) => Array.from({ length: Math.max(1, Math.round(ms / TICK)) }, () => ({ key, frame })));
        scene.anims.create({ key: anim, frames, frameRate: 1000 / TICK, repeat: -1 });
    }
    const npc = scene.add.sprite(x, y, key, 0).setOrigin(0.5, 1).setDepth(depth);
    npc.play(anim);
    npc.anims.setProgress(Math.random()); // out of step with each other
    npc.setInteractive({ pixelPerfect: true, useHandCursor: true });

    const headY = y - top;
    const name = scene.add.text(x, headY - 12, scene.t(`ambient.${id}.name`), {
        fontSize: '13px', fill: '#7fff8e', backgroundColor: 'rgba(0,0,0,0.5)', padding: { x: 5, y: 2 }
    }).setOrigin(0.5).setDepth(100).setAlpha(0);
    npc.on('pointerover', () => name.setAlpha(1));
    npc.on('pointerout', () => name.setAlpha(0));

    let next = 0;
    let bubble = null;
    npc.on('pointerdown', () => {
        if (scene.dialogVisible || bubble?.active) return; // let the current line finish
        const lines = scene.t(`ambient.${id}.lines`);
        if (!Array.isArray(lines) || !lines.length) return;
        name.setAlpha(0);
        // anchored at the feet: over the head, or (no room under the HUD, the top floor) below the feet, never over the body
        bubble = scene.showSpeechBubble({ x, y }, lines[next++ % lines.length], { duration: 3800, offsetY: top + 4 });
    });
    return npc;
}
