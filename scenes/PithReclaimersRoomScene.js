import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';

/**
 * The Reclaimers' Room — a hidden reading room beneath the Townhall, unlocked by joining the
 * Pith Reclaimers. Home base: a "Reclaimed Cache" that pays out a share for every soul the
 * player has filed into the record (the recruit-scaling perk). Reachable only via a
 * membership-gated transition from TownhallInteriorScene.
 */
export default class PithReclaimersRoomScene extends GameScene {
    constructor() {
        super({ key: 'PithReclaimersRoomScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    // Souls the player can be paid a share for (guarded by save-persisted journal entries).
    _cacheEntries() {
        return [
            { rec: 'pith_recruit_magnekin', got: 'pith_cache_magnekin', name: 'Magnekin' },
            { rec: 'pith_recruit_heir', got: 'pith_cache_heir', name: 'the Heir' },
        ];
    }
    _pendingCache() {
        return this._cacheEntries().filter(e => this.hasJournalEntry(e.rec) && !this.hasJournalEntry(e.got));
    }
    _collectCache() {
        const pending = this._pendingCache();
        if (!pending.length) return;
        let gold = 0, spores = 0;
        for (const e of pending) {
            this.addJournalEntry(
                e.got,
                'Reclaimed Share',
                `The Pith Reclaimers set aside a share for filing ${e.name} into the record.`,
                this.journalSystem.categories.EVENTS,
                { group: 'Pith Reclaimers' }
            );
            gold += 40; spores += 15;
        }
        if (this.moneySystem) this.moneySystem.add(gold);
        if (this.modifySpores) this.modifySpores(spores);
        this.showNotification(`Reclaimed share: +${gold} gold, +${spores} spores`, 0xffdf7a);
    }

    get dialogContent() {
        const pending = this._pendingCache();
        return {
            ...super.dialogContent,
            pith_cache: {
                speaker: 'Narrator',
                textKey: pending.length ? 'pith_cache_full' : 'pith_cache_empty',
                text: pending.length
                    ? `A squat iron filing-cabinet in the corner bears the Reclaimers' seal. A drawer slides open at your touch — inside, neatly labelled, is a share set aside for every soul you have filed into the record.`
                    : `The Reclaimers' filing-cabinet stands open and empty. Its ledger notes, in a clerk's precise hand: "Balance disbursed. Bring us more of the unaccounted."`,
                options: pending.length
                    ? [{ text: "Take the Reclaimers' share.", key: 'take_pith_cache', next: "closeDialog", onSelect: () => this._collectCache() }]
                    : [{ text: "Close the drawer.", key: 'close_pith_cache', next: "closeDialog" }]
            },

            // --- Filed souls, now residing in the room ---
            magnekin_room_start: {
                speaker: 'Magnekin',
                text: `Magnekin stands among the shelves, borrowed face at ease. "A collection of cities. Now, officially, one citizen — filed, stamped, cross-referenced." A thousand tiny windows glow warm. "It is strange. We spent so long pretending to belong, and a single form made it... true. Thank you, friend. We are accounted for."`,
                options: [
                    { text: "You seem at home here.", key: 'magnekin_room_home', next: "magnekin_room_home" },
                    { text: "Take care, Magnekin.", key: 'magnekin_room_bye', next: "closeDialog" },
                ]
            },
            magnekin_room_home: {
                speaker: 'Magnekin',
                text: `"The Reclaimers do not ask us to be less strange. Only to be written down. We can live with being written down." A pause. "The cities inside me have started a small archive of their own. We are learning the local custom: keep everything, throw away nothing."`,
                options: [{ text: "Fitting.", key: 'magnekin_room_fitting', next: "magnekin_room_start" }]
            },
            heir_room_start: {
                speaker: 'Heir to the Yellow Aquarium',
                text: `The Heir stands very still among the files, embryos drifting in slow, contented spirals. "Recorded," they say, and the word moves through the floorboards. "Continued. The register keeps us the way the Yellow Aquarium keeps its living things — because we can still change." Their yellow light is steady now. "We are remembered forward. It is enough."`,
                options: [
                    { text: "No more haunting the auctions, then?", key: 'heir_room_auctions', next: "heir_room_auctions" },
                    { text: "Rest well.", key: 'heir_room_bye', next: "closeDialog" },
                ]
            },
            heir_room_auctions: {
                speaker: 'Heir to the Yellow Aquarium',
                text: `"The lots still call. But a collector who is themselves collected need not chase the tide." A ripple of embryos. "We visit. We do not drift. There is a difference, now that there is a shelf with our name on it."`,
                options: [{ text: "There is.", key: 'heir_room_diff', next: "heir_room_start" }]
            }
        };
    }

    preload() {
        super.preload();
        // Reuse the abandoned-office interior for the archival reading room.
        this.load.image('pith-room-bg', 'assets/images/backgrounds/ShedAbandonedOffice.png');
        // Recruited souls that now reside here.
        this.load.image('magnekin', 'assets/images/characters/magnekin.png');
        this.load.image('heirToAquarium', 'assets/images/characters/heirToAquarium.png');
    }

    // A filed soul lives in the room; clicking them opens their settled dialog.
    createRecruitNpc(recruitFlag, textureKey, x, y, scale, tint, dialogState) {
        if (!this.hasJournalEntry(recruitFlag)) return;
        const npc = this.add.image(x, y, textureKey);
        npc.setScale(scale);
        if (tint !== null) npc.setTint(tint);
        npc.setDepth(5);
        npc.setInteractive({ useHandCursor: true });
        npc.on('pointerover', () => { document.body.style.cursor = 'pointer'; });
        npc.on('pointerout', () => { document.body.style.cursor = 'default'; });
        npc.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog(dialogState);
        });
        return npc;
    }

    create() {
        super.create();
        this.playSceneMusic('genericMusic');

        const bg = this.add.image(400, 300, 'pith-room-bg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        bg.setTint(0xd9c98f); // warm archival cast, to distinguish it from the Shed office

        this.transitionManager = new SceneTransitionManager(this);
        this.transitionManager.createTransitionZone(
            400, 560, 180, 80, 'down', 'TownhallInteriorScene', 400, 500, 'Back to the Townhall'
        );

        if (this.priest) {
            this.priest.x = 700;
            this.priest.y = 480;
        }
        if (this.priestGlow) { this.priestGlow.x = this.priest.x; this.priestGlow.y = this.priest.y; }

        // The Reclaimed Cache — pays out per soul filed.
        const cache = this.add.rectangle(180, 430, 70, 90, 0x6b5b2f, 1).setStrokeStyle(2, 0xffdf7a);
        cache.setDepth(5);
        cache.setInteractive({ useHandCursor: true });
        cache.on('pointerover', () => { document.body.style.cursor = 'pointer'; });
        cache.on('pointerout', () => { document.body.style.cursor = 'default'; });
        cache.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog('pith_cache');
        });

        // Souls the player has filed into the Pith now reside here instead of their old haunts.
        this.createRecruitNpc('pith_recruit_magnekin', 'magnekin', 330, 440, 0.18, 0xc0c0c0, 'magnekin_room_start');
        this.createRecruitNpc('pith_recruit_heir', 'heirToAquarium', 500, 450, 0.11, null, 'heir_room_start');

        if (!this.hasJournalEntry('pith_room_entered')) {
            this.addJournalEntry(
                'pith_room_entered',
                "The Reclaimers' Room",
                'A hidden reading room beneath the Townhall, off every official record — which, for the Pith Reclaimers, is the only privacy that survives. Shelved files climb the walls; a sealed filing-cabinet holds the Reclaimers\' share for every soul I bring into the fold.',
                this.journalSystem.categories.PLACES,
                { location: "The Reclaimers' Room" }
            );
        }

        this.cameras.main.fadeIn(800, 0, 0, 0);
    }
}
