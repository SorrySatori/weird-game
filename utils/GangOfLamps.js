// The Gang of Lamps — shared helpers for the disguised talking street-lamp questline.
// These live outside GameScene to keep the base class lean; each takes the scene explicitly.

export const LAMP_IDS = ['don', 'torchere', 'chandelier', 'sconce'];

/** True once the Lumen Directorate has hunted down and destroyed the Gang (terminal). */
export function gangLampsDestroyed(scene) {
    return !!scene.hasJournalEntry('gang_lamps_destroyed');
}

/** Create a clickable disguised street-lamp NPC with a soft flicker. Opens `dialogKey` on click. */
export function createStreetLamp(scene, textureKey, x, y, scale, dialogKey, depth = 6) {
    // If the Gang has been destroyed, no lamp appears anywhere ever again.
    if (gangLampsDestroyed(scene)) return null;
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

// ============================================================================
// L2 — the four quests (unlocked once all lamps are connected) → the Vestigel
// ============================================================================

/** The four L2 quest ids, one per lamp. */
export const GANG_QUEST_IDS = {
    don: 'gang_don_spy',            // Ears on the Rust Choir (spy)
    torchere: 'gang_torchere_smuggle', // A Run Past the Customs (smuggle)
    chandelier: 'gang_chandelier_eavesdrop', // A Choice Morsel (eavesdrop)
    sconce: 'gang_sconce_recover',  // Recover What Was Filed
};

/** 'none' (not started), 'active' (in progress), or 'done' (complete). */
export function gangQuestStatus(scene, questId) {
    const q = scene.questSystem?.getQuest(questId);
    if (!q) return 'none';
    return q.isComplete ? 'done' : 'active';
}

/** True once every one of the four L2 quests is complete. */
export function allGangQuestsComplete(scene) {
    return Object.values(GANG_QUEST_IDS).every(id => scene.questSystem?.getQuest(id)?.isComplete);
}

/** Whether Don has already handed over the Vestigel reward. */
export function gangRewardClaimed(scene) {
    return !!scene.hasJournalEntry('gang_vestigel_reward');
}

/** The Rust-Choir spy fragments the player has gathered so far (0–3). */
export function spyFragmentCount(scene) {
    return ['brukk', 'gnur', 'ravla'].filter(k => scene.hasJournalEntry('gang_spy_' + k)).length;
}

/**
 * Record one Rust-Choir secret fragment for Don's spy quest. Call from the
 * relevant Rust member's dialog. Idempotent per member.
 */
export function recordSpyFragment(scene, memberKey, title, secret) {
    const flag = 'gang_spy_' + memberKey;
    if (scene.hasJournalEntry(flag)) return;
    scene.addJournalEntry(
        flag,
        title,
        secret,
        scene.journalSystem.categories.LORE,
        { group: 'Gang of Lamps', related: "Ears on the Rust Choir" }
    );
    const n = spyFragmentCount(scene);
    if (scene.questSystem?.getQuest(GANG_QUEST_IDS.don)) {
        scene.questSystem.updateQuest(GANG_QUEST_IDS.don, `I've prised ${n === 1 ? 'a secret' : n + ' secrets'} out of the Rust Choir. I should take what I have to Don and see if it's enough.`, flag);
    }
    scene.showNotification('Rust Choir secret learned', 0xb87333);
}

// --- Betrayal / alternate-completion state -------------------------------------------------

/** True if the player fed any lamp false intel or diverted the contraband instead of playing straight. */
export function gangDeceived(scene) {
    return ['gang_spy_betrayed', 'gang_eavesdrop_betrayed', 'gang_smuggle_kept', 'gang_smuggle_gave_rust', 'gang_smuggle_gave_pith']
        .some(f => scene.hasJournalEntry(f));
}

/** Don's spy quest is reportable once 2 real secrets are gathered OR the player betrayed the lamps for false intel. */
export function spyReportable(scene) {
    return spyFragmentCount(scene) >= 2 || !!scene.hasJournalEntry('gang_spy_betrayed');
}

/** Chandelier's eavesdrop is reportable once heard honestly OR via betrayal (false gossip). */
export function eavesdropReportable(scene) {
    return !!scene.hasJournalEntry('gang_eavesdrop_heard') || !!scene.hasJournalEntry('gang_eavesdrop_betrayed');
}

/** Torchère's run is reportable once dropped honestly OR diverted (fenced / given to Rust / given to Pith). */
export function smuggleReportable(scene) {
    return ['gang_smuggle_delivered', 'gang_smuggle_kept', 'gang_smuggle_gave_rust', 'gang_smuggle_gave_pith']
        .some(f => scene.hasJournalEntry(f));
}

/**
 * Terminal betrayal: the Lumen Directorate traces the contraband to the Gang and destroys
 * every lamp. Ends the questline for good (no Vestigel). Faction rep / G-D handled by caller.
 */
export function destroyGangLamps(scene) {
    if (gangLampsDestroyed(scene)) return;
    scene.addJournalEntry(
        'gang_lamps_destroyed',
        'The Gang Is Gone',
        "I handed the Directorate the contraband and told them where it came from. They did not hesitate. By nightfall every one of the Gang of Lamps — Don Girandole, Chandelier, Torchère, the little Sconce — had been quietly pulled from its post and unmade, their circuit gone dark for good. The Directorate is grateful. The city is a little quieter. Whatever the Don had been keeping for me, it went dark with him.",
        scene.journalSystem.categories.EVENTS,
        { group: 'Gang of Lamps' }
    );
    if (scene.questSystem?.getQuest('gang_of_lamps') && !scene.questSystem.getQuest('gang_of_lamps').isComplete) {
        scene.questSystem.updateQuest('gang_of_lamps', 'The Gang of Lamps was destroyed by the Lumen Directorate. There is no one left to reconnect, and no reward to collect.', 'gang_lamps_destroyed');
    }
    scene.showNotification('The Gang of Lamps is destroyed', 0x8B0000);
}

/** Grant the Gang of Lamps reward: a real Vestigel (the second of the legendary three). */
export function grantGangVestigel(scene) {
    if (gangRewardClaimed(scene)) return;
    const deceived = gangDeceived(scene);
    // stackable so the reward always lands even if the player still carries the
    // Eskola vestigel (a non-stackable add would silently fail on a duplicate id).
    scene.addItemToInventory({
        id: 'vestigel',
        name: 'Vestigel',
        description: 'A coin-like object that seems faintly alive. One of only three known to exist — this one the Gang of Lamps had squirreled away in a gutter for years.',
        texture: 'vestigel',
        icon: 'vestigel',
        stackable: true,
    });
    scene.addJournalEntry(
        'gang_vestigel_reward',
        'The Lamps\' Vestigel',
        (deceived
            ? "Don Girandole made good on his promise and gave me a Vestigel — one of the three legendary alive-coins, kept hidden in a gutter for years. He called me the truest friend the family ever had. He does not know that some of what I brought his family was a lie, sold or bought from the very people they asked me to watch. The coin is warm in my hand and I cannot quite meet the little light of him. Kloor Venn has been hunting one of these."
            : "With all four of his family reconnected and their errands run honestly, Don Girandole made good on his promise: he gave me a Vestigel the Gang had kept hidden in a gutter for years — one of the three legendary alive-coins. Kloor Venn has been hunting one of these."),
        scene.journalSystem.categories.EVENTS,
        { group: 'Gang of Lamps', related: 'The Three Vestigels' }
    );
    if (scene.questSystem?.getQuest('gang_of_lamps') && !scene.questSystem.getQuest('gang_of_lamps').isComplete) {
        scene.questSystem.completeQuest('gang_of_lamps');
    }
    scene.showNotification('Received: Vestigel', 0xffcc66);
}
