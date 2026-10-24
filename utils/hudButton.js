/**
 * HUD buttons (inventory, map, journal, quests): a drawn object that "opens" while hovered (the satchel's flap
 * lifts, the map unfolds, the book opens, the note's corner curls), a localized label below it and the red wax
 * badge for unread updates. Pixel art at scale 1 — hover swaps the frame instead of scaling.
 * Art: tools/artgen/hud_buttons.py → assets/aseprite/UI_HudButtons_48x48.aseprite → hud_export.lua →
 * assets/images/ui/hud_buttons.png (frames: closed / open per button, badge last).
 */
export const HUD_FRAME = { inventory: 0, map: 2, journal: 4, quests: 6, badge: 8 };

/** Where each button sits; the equipment tutorial points its highlight ring at the same spots. */
export function hudButtonPos(scene, icon) {
    const W = scene.scale.width;
    return {
        inventory: { x: 60, y: 540 },
        map: { x: W - 170, y: 50 },
        journal: { x: W - 110, y: 50 },
        quests: { x: W - 50, y: 50 }
    }[icon];
}

/** Centre of the drawn icon (the label hangs below it). */
export function hudIconCentre(scene, icon) {
    const { x, y } = hudButtonPos(scene, icon);
    return { x, y: y - 6 };
}

export function preloadHudButtons(scene) {
    scene.load.spritesheet('hudButtons', 'assets/images/ui/hud_buttons.png', { frameWidth: 48, frameHeight: 48 });
}

/**
 * @returns {{ container: Phaser.GameObjects.Container, badge: Phaser.GameObjects.Image }} the badge starts hidden
 */
export function createHudButton(scene, icon, label, onClick, pos = hudButtonPos(scene, icon)) {
    const frame = HUD_FRAME[icon];
    const container = scene.add.container(pos.x, pos.y).setDepth(100).setScrollFactor(0);
    const img = scene.add.image(0, -6, 'hudButtons', frame);
    const text = scene.add.text(0, 20, label, {
        fontFamily: 'Georgia',
        fontSize: '13px',
        color: '#7fff8e',
        stroke: '#06120a',
        strokeThickness: 3
    }).setOrigin(0.5, 0);
    const badge = scene.add.image(16, -22, 'hudButtons', HUD_FRAME.badge).setVisible(false);
    container.add([img, text, badge]);

    container.setSize(52, 76);
    container.setInteractive({ useHandCursor: true });
    container.on('pointerover', () => {
        img.setFrame(frame + 1);
        text.setColor('#c8ffd0');
    });
    container.on('pointerout', () => {
        img.setFrame(frame);
        text.setColor('#7fff8e');
    });
    container.on('pointerdown', (pointer, localX, localY, event) => {
        event.stopPropagation(); // don't also walk the priest to the HUD
        onClick();
    });
    return { container, badge };
}
