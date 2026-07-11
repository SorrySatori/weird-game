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
            }
        };
    }

    preload() {
        super.preload();
        // Reuse the abandoned-office interior for the archival reading room.
        this.load.image('pith-room-bg', 'assets/images/backgrounds/ShedAbandonedOffice.png');
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
