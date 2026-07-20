// The Gang of Lamps — shared helpers for the disguised talking street-lamp questline.
// These live outside GameScene to keep the base class lean; each takes the scene explicitly.

export const LAMP_IDS = ['don', 'torchere', 'chandelier', 'sconce'];

/** Create a clickable disguised street-lamp NPC with a soft flicker. Opens `dialogKey` on click. */
export function createStreetLamp(scene, textureKey, x, y, scale, dialogKey, depth = 6) {
    const lamp = scene.add.image(x, y, textureKey).setScale(scale).setDepth(depth);
    lamp.setInteractive({ useHandCursor: true });
    lamp.on('pointerover', () => { document.body.style.cursor = 'pointer'; });
    lamp.on('pointerout', () => { document.body.style.cursor = 'default'; });
    lamp.on('pointerdown', () => {
        if (scene.dialogVisible) return;
        if (scene.clickSound) scene.clickSound.play();
        scene.showDialog(dialogKey);
    });
    scene.tweens.add({ targets: lamp, alpha: { from: 0.9, to: 1 }, duration: 1500 + Math.random() * 900, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    return lamp;
}

/** How many of the four lamps the player has found so far. */
export function lampsFoundCount(scene) {
    return LAMP_IDS.filter(id => scene.hasJournalEntry('met_lamp_' + id)).length;
}

/** Record a first meeting with a lamp; starts/advances the Gang of Lamps quest. */
export function meetLamp(scene, id, name) {
    const flag = 'met_lamp_' + id;
    if (scene.hasJournalEntry(flag)) return;
    scene.addJournalEntry(
        flag,
        name,
        `I found ${name} — one of the Gang of Lamps, a sentient street-lamp that cannot move and relies on me to carry word to the others.`,
        scene.journalSystem.categories.PEOPLE,
        { group: 'Gang of Lamps', character: name }
    );
    if (scene.questSystem && !scene.questSystem.getQuest('gang_of_lamps')) {
        scene.questSystem.addQuest('gang_of_lamps', 'The Gang of Lamps', "A talking street-lamp let me in on a secret: a scattered gang of sentient lamps, unable to move and out of contact with one another. Find all four — Don Girandole, Torchère, Chandelier, and Sconce — so they can speak through me.");
    }
    const n = lampsFoundCount(scene);
    if (scene.questSystem?.getQuest('gang_of_lamps')) {
        if (n >= 4) {
            scene.questSystem.updateQuest('gang_of_lamps', 'All four lamps are found and back in contact through me. Now they have work for me.', 'all_lamps_found');
        } else {
            scene.questSystem.updateQuest('gang_of_lamps', `I've found ${n} of the 4 lamps.`, flag);
        }
    }
    scene.showNotification(`Found a lamp: ${name}`, 0xffcc66);
}
