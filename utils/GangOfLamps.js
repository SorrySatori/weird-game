// The Gang of Lamps — shared helpers for the disguised talking street-lamp questline.
// These live outside GameScene to keep the base class lean; each takes the scene explicitly.

import { countForm } from '../systems/LanguageSystem.js';

export const LAMP_IDS = ['don', 'torchere', 'chandelier', 'sconce'];

/** True once the Lumen Directorate has hunted down and destroyed the Gang (terminal). */
export function gangLampsDestroyed(scene) {
    return !!scene.hasJournalEntry('gang_lamps_destroyed');
}

/**
 * The lamps' art (tools/artgen/lamps.py -> assets/images/characters/lamps/<file>.png, Aseprite Lamps_<file>):
 * 8-frame idle sheets, origin bottom-centre, shown at scale 1 -- Don at 3, because he is drawn on the 3x pixel grid of
 * Scraper1140.png. `order` = the idle's frame sequence (holds included), `hit` = the clickable box in frame pixels
 * [x, y, w, h], `bust` = the dialog portrait, keyed by the EN and CZ speaker names, `shadow` = [w, h] of the contact
 * shadow on the ground (none for Don, who stands on a platform in the picture).
 */
export const LAMP_ART = {
    // the near-twin of the townhall's painted lamp; the flame darts to the door, ducks, the brass lamp rattles
    lamp_sconce: { file: 'sconce', fw: 128, fh: 176, scale: 1, fps: 6, names: ['Sconce'],
        order: [0, 0, 0, 1, 0, 0, 2, 3, 3, 3, 3, 4, 0, 0, 0, 1, 0, 5, 5, 0, 0, 0, 6, 6, 7, 0, 0, 0],
        hit: [44, 2, 44, 174], bust: { frame: 3, zoom: 3, top: 4 }, shadow: [30, 7] },
    // the glint runs round the lustres once per loop, the globe's hot spot looks about, a pendant swings
    lamp_chandelier: { file: 'chandelier', fw: 128, fh: 216, scale: 1, fps: 5, names: ['Chandelier'],
        order: [0, 1, 2, 3, 4, 5, 6, 7],
        hit: [32, 6, 64, 210], bust: { frame: 0, zoom: 2, top: 8 }, shadow: [34, 9] },
    // the sea wind lays the flame over; it rounds on you and flares, spits sparks
    lamp_torchere: { file: 'torchere', fw: 128, fh: 200, scale: 1, fps: 6, names: ['Torchère'],
        order: [0, 1, 2, 0, 1, 5, 6, 7, 0, 1, 2, 3, 3, 4, 4, 5, 6, 7],
        hit: [44, 0, 44, 200], bust: { frame: 3, zoom: 2, top: 0 }, shadow: [32, 10] },
    // the head-lamp's flame turns to look, the cigar hand lifts, the ember breathes, smoke curls up
    lamp_don: { file: 'don', fw: 45, fh: 56, scale: 3, fps: 5, names: ['Don Girandole'],
        order: [0, 1, 1, 0, 0, 2, 3, 3, 3, 3, 4, 4, 5, 0, 0, 1, 0, 6, 6, 7, 0, 0],
        hit: [0, 2, 45, 48], bust: { frame: 3, zoom: 4, top: 1 } },     // the foot left out: the right-edge exit is below
};

/** Queue a lamp's sheet in a scene's preload(). */
export function preloadStreetLamp(scene, textureKey) {
    const a = LAMP_ART[textureKey];
    scene.load.spritesheet(textureKey, `assets/images/characters/lamps/${a.file}.png`, { frameWidth: a.fw, frameHeight: a.fh });
}

/**
 * Create a clickable disguised street-lamp NPC: its animated sheet with the feet (the base's front edge) at canvas
 * (x, y), a soft glow on hover, its bust as the dialog portrait. Opens `dialogKey` on click.
 */
export function createStreetLamp(scene, textureKey, x, y, dialogKey, depth = 6) {
    // If the Gang has been destroyed, no lamp appears anywhere ever again.
    if (gangLampsDestroyed(scene)) return null;
    const a = LAMP_ART[textureKey];
    const animKey = textureKey + '_idle';
    if (!scene.anims.exists(animKey)) {
        scene.anims.create({ key: animKey, frames: scene.anims.generateFrameNumbers(textureKey, { frames: a.order }), frameRate: a.fps, repeat: -1 });
    }
    const lamp = scene.add.sprite(x, y, textureKey, 0).setOrigin(0.5, 1).setScale(a.scale).setDepth(depth);
    lamp.play({ key: animKey, startFrame: Math.floor(Math.random() * a.order.length) });
    if (a.shadow) scene.addGroundShadow(x, y - 3, a.shadow[0], a.shadow[1]);
    const [hx, hy, hw, hh] = a.hit;
    lamp.setInteractive({ hitArea: new Phaser.Geom.Rectangle(hx, hy, hw, hh), hitAreaCallback: Phaser.Geom.Rectangle.Contains, useHandCursor: true });
    // Hover: a soft warm glow (pixel art isn't scaled); the scene instance is reused, so the glow lives on the sprite.
    let hoverFx = null;
    lamp.on('pointerover', () => { if (!hoverFx) hoverFx = lamp.preFX?.addGlow(0xffd27a, 2, 0, false, 0.1, Math.max(3, Math.round(8 / a.scale))); });
    lamp.on('pointerout', () => { if (hoverFx) { lamp.preFX?.remove(hoverFx); hoverFx = null; } });
    lamp.on('pointerdown', () => {
        if (scene.dialogVisible) return;
        if (scene.clickSound) scene.clickSound.play();
        scene.showDialog(dialogKey);
    });
    const bust = { key: textureKey, ...a.bust };
    scene.dialogPortraits = { ...(scene.dialogPortraits || {}) };
    for (const n of a.names) scene.dialogPortraits[n] = bust;
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
    // The first lamp only says it's one of a scattered gang; how many there are and who they are comes
    // from a lamp's rundown (learnLampFamily), so neither the names nor the count go in up front.
    if (scene.questSystem && !scene.questSystem.getQuest('gang_of_lamps')) {
        scene.questSystem.addQuest('gang_of_lamps', 'The Gang of Lamps', "A talking street-lamp let me in on a secret: it belongs to a scattered gang of sentient lamps, unable to move and out of contact with one another. I should find the others so they can speak through me.");
    }
    const n = lampsFoundCount(scene);
    const quest = scene.questSystem?.getQuest('gang_of_lamps');
    if (quest) {
        if (n >= 4) {
            scene.questSystem.updateQuest('gang_of_lamps', 'All four lamps are found and back in contact through me.', 'all_lamps_found');
        } else {
            const familyKnown = quest.updates.some(u => u.key === 'lamp_family_known');
            // The flag stays per-lamp; textKey + n let the quest log translate the count line.
            const textKey = familyKnown ? 'lamps_found_of_four' : 'lamps_found_' + countForm(n);
            scene.questSystem.updateQuest('gang_of_lamps',
                familyKnown ? `I've found ${n} of the 4 lamps.` : (n === 1 ? 'One lamp found so far.' : `${n} lamps found so far.`),
                flag, { textKey, n });
        }
    }
    scene.showNotification(`Found a lamp: ${name}`, 0xffcc66);
}

/**
 * A lamp has just told the player who the four are and where they stand (its "family" rundown,
 * or a return-visit reminder). Call from that state's onTrigger. Idempotent; no-op once all are found.
 */
export function learnLampFamily(scene) {
    const quest = scene.questSystem?.getQuest('gang_of_lamps');
    if (!quest || quest.isComplete || lampsFoundCount(scene) >= 4) return;
    scene.questSystem.updateQuest('gang_of_lamps', 'There are four lamps in all: the Don, up on the high walkway under Scraper 1140; Chandelier, on a post in the town square; Sconce, by the house of stamps; and Torchère, down by the water where the cargo comes in.', 'lamp_family_known');
}

/**
 * A reconnected lamp has just said there'll be work soon (its "connected" greeting). Call from that
 * state's onTrigger. Idempotent; only before any of the four L2 jobs has been taken.
 */
export function lampsHaveWork(scene) {
    const quest = scene.questSystem?.getQuest('gang_of_lamps');
    if (!quest || quest.isComplete || gangLampsDestroyed(scene) || lampsFoundCount(scene) < 4) return;
    if (Object.values(GANG_QUEST_IDS).some(id => scene.questSystem.getQuest(id))) return;
    scene.questSystem.updateQuest('gang_of_lamps', "The lamps say they'll have work for me soon. I should check back with them.", 'lamps_have_work');
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
        scene.questSystem.updateQuest(GANG_QUEST_IDS.don, `I've prised ${n === 1 ? 'a secret' : n + ' secrets'} out of the Rust Choir. I should take what I have to Don and see if it's enough.`, flag,
            { textKey: 'spy_secrets_' + countForm(n), n });
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
    // Only worth noting if Kloor has actually told me he's after one. Added before the entry so it
    // lands silently with it (no second "Journal updated").
    if (scene.questSystem?.getQuest('the_three_vestigels')) {
        scene.addJournalFact('gang_vestigel_reward', 'kloor', 'Kloor Venn has been hunting one of these.');
    }
    scene.addJournalEntry(
        'gang_vestigel_reward',
        'The Lamps\' Vestigel',
        (deceived
            ? "Don Girandole made good on his promise and gave me a Vestigel — one of the three legendary alive-coins, kept hidden in a gutter for years. He called me the truest friend the family ever had. He does not know that some of what I brought his family was a lie, sold or bought from the very people they asked me to watch. The coin is warm in my hand and I cannot quite meet the little light of him."
            : "With all four of his family reconnected and their errands run honestly, Don Girandole made good on his promise: he gave me a Vestigel the Gang had kept hidden in a gutter for years — one of the three legendary alive-coins."),
        scene.journalSystem.categories.EVENTS,
        { group: 'Gang of Lamps', related: 'The Three Vestigels' }
    );
    if (scene.questSystem?.getQuest('gang_of_lamps') && !scene.questSystem.getQuest('gang_of_lamps').isComplete) {
        scene.questSystem.completeQuest('gang_of_lamps');
    }
    scene.showNotification('Received: Vestigel', 0xffcc66);
}
