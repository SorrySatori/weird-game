import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';

/**
 * The Tribunal's Room — a hidden reading room beneath the Townhall, unlocked by joining the
 * Ink Tribunal. Home base: a "Tribunal's Cache" that pays out a share for every soul the
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
                `The Ink Tribunal set aside a share for filing ${e.name} into the record.`,
                this.journalSystem.categories.EVENTS,
                { group: 'Ink Tribunal' }
            );
            gold += 40; spores += 15;
        }
        if (this.moneySystem) this.moneySystem.add(gold);
        if (this.modifySpores) this.modifySpores(spores);
        this.showNotification(`Reclaimed share: +${gold} dinar, +${spores} spores`, 0xffdf7a);
    }

    get dialogContent() {
        const pending = this._pendingCache();
        return {
            ...super.dialogContent,
            pith_cache: {
                speaker: 'Narrator',
                textKey: pending.length ? 'pith_cache_full' : 'pith_cache_empty',
                text: pending.length
                    ? `The glass orb on its pedestal clouds at your touch, then clears — and there, suspended within it, is the Tribunal's share set aside for every soul you have filed into the record.`
                    : `The orb hangs clear and empty. A whisper moves through it in a clerk's precise voice: "Balance disbursed. Bring us more of the unaccounted."`,
                options: pending.length
                    ? [{ text: "Take the Tribunal's share.", key: 'take_pith_cache', next: "closeDialog", onSelect: () => this._collectCache() }]
                    : [{ text: "Step away from the orb.", key: 'close_pith_cache', next: "closeDialog" }],
                onTrigger: () => {
                    this.addJournalFact('pith_room_entered', 'orb', "The orb holds the Tribunal's share for every soul I bring into the fold.");
                }
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
                text: `"The Tribunal does not ask us to be less strange. Only to be written down. We can live with being written down." A pause. "The cities inside me have started a small archive of their own. We are learning the local custom: keep everything, throw away nothing."`,
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
        this.load.image('pith-room-bg', 'assets/images/backgrounds/ReclaimersRoom.png');
        // Recruited souls that now reside here.
        this.load.spritesheet('magnekinIdle', 'assets/images/characters/magnekin_idle.png', { frameWidth: 128, frameHeight: 192 }); // tools/artgen/magnekin.py
        this.load.spritesheet('heirAquariumIdle', 'assets/images/characters/voxmarket/heir_aquarium.png', { frameWidth: 128, frameHeight: 176 }); // tools/artgen/voxmarket_guests.py
    }

    create() {
        super.create();
        this.playSceneMusic('genericMusic');

        if (this.ground) { this.ground.destroy(); this.ground = null; }

        // The Tribunal's vaulted archive cellar, native 1067×600 with its own floor (tools/artgen/tribunal_bg.py)
        const bg = this.add.image(this.scale.width / 2, 300, 'pith-room-bg');
        this.fitBackground(bg);
        bg.setDepth(-1);

        this.transitionManager = new SceneTransitionManager(this);
        this.transitionManager.createTransitionZone(
            400, 560, 180, 80, 'down', 'TownhallInteriorScene', 400, 500, 'Back to the Townhall'
        );

        if (this.priest) {
            this.priest.x = 650;
            this.priest.y = 470; // feet on the walk line (y 534)
        }
        if (this.priestGlow) { this.priestGlow.x = this.priest.x; this.priestGlow.y = this.priest.y; }

        // the cache: the glass orb on its bronze pedestal in the middle of the court circle (orb y ~368-420, plinth foot ~482)
        const stash = this.add.zone(this.scale.width / 2, 425, 72, 118).setInteractive({ useHandCursor: true });
        stash.setDepth(5);
        stash.on('pointerover', () => { document.body.style.cursor = 'pointer'; });
        stash.on('pointerout', () => { document.body.style.cursor = 'default'; });
        stash.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog('pith_cache');
        });

        // Souls the player has filed into the Tribunal now reside here — on the near floor either side of the court
        // circle (feet y 523): Magnekin by the writing desk, the Heir between the eggshell vitrine and the docket trolley.
        if (this.hasJournalEntry('pith_recruit_magnekin')) {
            // Magnekin: 8 idle frames of 128×192 at scale 1, origin bottom. 'magnekin_idle' is global: keep this frame list
            // in sync with TownSquareScene.
            if (!this.anims.exists('magnekin_idle')) {
                this.anims.create({ key: 'magnekin_idle', frames: this.anims.generateFrameNumbers('magnekinIdle', { frames: [0, 0, 1, 1, 2, 3, 3, 4, 4, 5, 6, 6, 7, 7] }), frameRate: 5, repeat: -1 });
            }
            const mag = this.add.sprite(300, 525, 'magnekinIdle', 0).setOrigin(0.5, 1).setDepth(6);
            mag.play('magnekin_idle');
            this.addGroundShadow(300, 521, 60, 12);
            mag.setInteractive({ hitArea: new Phaser.Geom.Rectangle(30, 8, 68, 183), hitAreaCallback: Phaser.Geom.Rectangle.Contains, useHandCursor: true });
            const magBust = { key: 'magnekinIdle', frame: 0, zoom: 2, top: 8 };
            this.dialogPortraits = { ...(this.dialogPortraits || {}), 'Magnekin': magBust };
            let magHoverFx = null;
            mag.on('pointerover', () => { if (!magHoverFx) magHoverFx = mag.preFX?.addGlow(0x9fb8ff, 2, 0, false, 0.1, 8); });
            mag.on('pointerout', () => { if (magHoverFx) { mag.preFX?.remove(magHoverFx); magHoverFx = null; } });
            mag.on('pointerdown', () => {
                if (this.dialogVisible) return;
                if (this.clickSound) this.clickSound.play();
                this.showDialog('magnekin_room_start');
            });
        }
        if (this.hasJournalEntry('pith_recruit_heir')) {
            // the Heir: 8 idle frames of 128×176 at scale 1, origin bottom. 'heir_idle' is global: keep this frame list in
            // sync with VoxmarketHallScene + HarborScene.
            if (!this.anims.exists('heir_idle')) {
                this.anims.create({ key: 'heir_idle', frames: this.anims.generateFrameNumbers('heirAquariumIdle', { frames: [0, 0, 1, 1, 7, 0, 0, 2, 0, 0, 0, 3, 3, 0, 4, 4, 0, 0, 5, 5, 5, 0, 1, 1, 7, 0, 0, 6, 6, 0, 0] }), frameRate: 5, repeat: -1 });
            }
            const heir = this.add.sprite(775, 525, 'heirAquariumIdle', 0).setOrigin(0.5, 1).setDepth(6);
            heir.play('heir_idle');
            this.addGroundShadow(775, 521, 50, 11);
            heir.setInteractive({ hitArea: new Phaser.Geom.Rectangle(35, 11, 58, 163), hitAreaCallback: Phaser.Geom.Rectangle.Contains, useHandCursor: true });
            const heirBust = { key: 'heirAquariumIdle', frame: 0, zoom: 2, top: 9 };
            this.dialogPortraits = { ...(this.dialogPortraits || {}), 'Heir to the Yellow Aquarium': heirBust, 'Dědic Žlutého akvária': heirBust };
            let heirHoverFx = null;
            heir.on('pointerover', () => { if (!heirHoverFx) heirHoverFx = heir.preFX?.addGlow(0x7fff8e, 2, 0, false, 0.1, 8); });
            heir.on('pointerout', () => { if (heirHoverFx) { heir.preFX?.remove(heirHoverFx); heirHoverFx = null; } });
            heir.on('pointerdown', () => {
                if (this.dialogVisible) return;
                if (this.clickSound) this.clickSound.play();
                this.showDialog('heir_room_start');
            });
        }

        if (!this.hasJournalEntry('pith_room_entered')) {
            this.addJournalEntry(
                'pith_room_entered',
                "The Tribunal's Room",
                'A hidden reading room beneath the Townhall, off every official record — which, for the Ink Tribunal, is the only privacy that survives. Shelved files climb the walls; a clouded glass orb stands on a pedestal.',
                this.journalSystem.categories.PLACES,
                { location: "The Tribunal's Room" }
            );
        }

        this.cameras.main.fadeIn(800, 0, 0, 0);
    }
}
