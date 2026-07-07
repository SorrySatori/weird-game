import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

/**
 * GodgraveyardScene — the graveyard of dead gods beneath the Townhall.
 *
 * Two states:
 *  - No access → the sealed gate (GodgraveyardGate.png), a locked message, exit only.
 *  - Access (journal `godgraveyard_access_granted` or the permit item) → the open graveyard
 *    (Godgraveyard.png) with Phor Calesta present. The player clicks graves; Phor narrates each
 *    dead god and each grave yields a candidate password (a name/epitaph) recorded to the journal
 *    as `grave_<slug>`. Exactly one epitaph is the true passphrase to the sealed Scraper cellar
 *    ("I FOLD", grave of Laimig Cel Who Lost the Game — the homage Ortolan & Elphi chose).
 */
export default class GodgraveyardScene extends GameScene {
    constructor() {
        super({ key: 'GodgraveyardScene' });
        this.isTransitioning = false;
    }

    hasGraveyardAccess() {
        return !!(this.hasJournalEntry('godgraveyard_access_granted') || this.hasItem('godgraveyard-access-permit'));
    }

    // The dead gods. `correct: true` marks the true cellar passphrase.
    graves() {
        return [
            {
                slug: 'laimig', x: 100, name: 'Laimig Cel, Who Lost the Game', epitaph: 'I FOLD', correct: true,
                lore: "\"Laimig Cel — a god of wagers and games, who bet against a rival deity and lost everything, even Their own name. The epitaph is Their last move: 'I FOLD.'\"\n\nPhor lowers her voice. \"Odd thing — a divinographer before me swore two game-makers used to leave offerings at this stone. A dreamwright and her partner. They were... taken with the god who knew when to lose.\""
            },
            {
                slug: 'sisyla', x: 225, name: 'Sisyla, the Unwaking', epitaph: 'SLEEP HAS NO DOOR',
                lore: "\"Sisyla drew Their faithful into a sleep so deep that waking became heresy. When Sisyla died, the dreams did not — they just had no one left to dream them. The stone reads: 'SLEEP HAS NO DOOR.'\""
            },
            {
                slug: 'vhorn', x: 350, name: 'Vhorn the Tally-Keeper', epitaph: 'COUNT ME OUT',
                lore: "\"Vhorn counted everything — debts, sins, grains of ash. They died when a follower proved the numbers never balanced. Bitter little god. The epitaph is a joke at Their own expense: 'COUNT ME OUT.'\""
            },
            {
                slug: 'liln', x: 475, name: 'Liln of Small Mercies', epitaph: 'BE KIND, THEN LEAVE',
                lore: "\"Liln asked so little — a kind word, a shared crust — that no empire ever bothered to worship Them, and so They faded. The gentlest grave here. 'BE KIND, THEN LEAVE.' As good a rule as any.\""
            },
            {
                slug: 'lietus', x: 600, name: 'Lietus Kika, of Temporal Confusion', epitaph: 'IT WAS ONLY YESTERDAY',
                lore: "\"Lietus Kika — god of temporal confusion, prayed to by those forever certain they did a thing only recently, when years have quietly slid by. This stone can't even agree how long it's stood here.\" Phor frowns at her own notes. \"I could swear I catalogued it last week. My handwriting says eleven years ago. The epitaph, without a shred of irony: 'IT WAS ONLY YESTERDAY.'\""
            },
            {
                slug: 'hvetrdjaana', x: 725, name: 'Hvétrdjaana', epitaph: '(unreadable)',
                lore: "\"Hvétrdjaana — goddess of the urbzunids and the krobulovits.\" Phor sounds the words carefully. \"What those were, no one alive can say. Beasts? Peoples? Ideas? Her worshippers died out so long ago the names are just noises now. And look — the inscription's in a script even I can't read. A goddess of the utterly forgotten... forgotten utterly. There's nothing here to take away but the sadness of it.\""
            }
        ];
    }

    get dialogContent() {
        const states = {
            ...super.dialogContent,
            speaker: 'Phor Calesta',

            gate_sealed: {
                speaker: 'Godgraveyard Gate',
                text: "A vast iron gate, sealed with the Townhall's wax and older, greener locks. It will not open for you — not yet. Somewhere below, fossilized gods keep their silence.\n\n(You need the Townhall's leave to come down here — and Phor Calesta to guide you.)",
                options: [
                    { text: "Head back up.", key: 'head_back_up', next: "closeDialog" }
                ]
            },

            phor_graveyard_start: {
                speaker: 'Phor Calesta',
                text: "Phor Calesta stands among the leaning stones, notebook in hand, practically glowing. \"You did it — they let us down. Look at them all: gods from a hundred dead spheres, brought here to fossilize so they wouldn't be alone.\"\n\n\"Read the stones. Gods lie to their followers, but their corpses tell only truth. Ask me about any of them.\"",
                options: [
                    { text: "I will. (read the graves)", key: 'read_the_graves', next: "closeDialog" }
                ]
            }
        };

        // One dialog state per grave (Phor narrates; records the candidate).
        this.graves().forEach(g => {
            states['grave_' + g.slug] = {
                speaker: 'Phor Calesta',
                text: `You brush moss from the stone. Phor reads over your shoulder:\n\n${g.lore}`,
                options: [
                    { text: "Note it down.", key: 'note_it_down_' + g.slug, next: "closeDialog" }
                ],
                onTrigger: () => {
                    const id = 'grave_' + g.slug;
                    if (!this.hasJournalEntry(id)) {
                        this.addJournalEntry(
                            id,
                            `Grave: ${g.name}`,
                            `${g.name}. Epitaph: "${g.epitaph}". ${g.lore.replace(/"/g, '')}`,
                            this.journalSystem.categories.LORE,
                            { location: 'Godgraveyard', character: 'Phor Calesta', epitaph: g.epitaph }
                        );
                    }
                }
            };
        });

        return states;
    }

    preload() {
        super.preload();
        this.load.image('godgraveyardBg', 'assets/images/backgrounds/Godgraveyard.png');
        this.load.image('godgraveyardGateBg', 'assets/images/backgrounds/GodgraveyardGate.png');
        this.load.image('phor', 'assets/images/characters/phor.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
    }

    create() {
        super.create();
        this.playSceneMusic('cathedralTheme');

        const access = this.hasGraveyardAccess();

        const bg = this.add.image(400, 300, access ? 'godgraveyardBg' : 'godgraveyardGateBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        this.transitionManager = new SceneTransitionManager(this);

        // Exit back up to the Town Square.
        this.transitionManager.createTransitionZone(
            400, 560, 200, 60, 'up', 'TownSquareScene', 500, 500, 'Town Square'
        );

        this.priest.x = 400;
        this.priest.y = 500;
        if (this.priestGlow) { this.priestGlow.x = this.priest.x; this.priestGlow.y = this.priest.y; }

        this.cameras.main.fadeIn(700, 0, 0, 0);

        if (!access) {
            // Sealed gate: a single interactable that explains, plus a first-visit journal note.
            this.time.delayedCall(700, () => this.showDialog('gate_sealed'));
            if (!this.hasJournalEntry('godgraveyard_gate_seen')) {
                this.addJournalEntry(
                    'godgraveyard_gate_seen',
                    'The Sealed Godgraveyard',
                    'I found the gate to the Godgraveyard beneath the Townhall, but it is sealed. I need the Townhall\'s permission — and Phor Calesta, the divinographer, to get inside.',
                    this.journalSystem.categories.PLACES,
                    { location: 'Godgraveyard' }
                );
            }
            return;
        }

        // Open graveyard: Phor + clickable graves.
        this.createPhor();
        this.createGraves();

        if (!this.hasJournalEntry('godgraveyard_entered')) {
            this.addJournalEntry(
                'godgraveyard_entered',
                'Into the Godgraveyard',
                'Phor Calesta took me down into the Godgraveyard beneath the Townhall — layer upon layer of fossilized dead gods. She says their gravestones tell only the truth. I can read individual graves for their names and epitaphs.',
                this.journalSystem.categories.PLACES,
                { location: 'Godgraveyard', character: 'Phor Calesta' }
            );
        }
        this.time.delayedCall(900, () => { if (!this.dialogVisible) this.showDialog('phor_graveyard_start'); });
    }

    createPhor() {
        const p = this.add.sprite(400, 470, 'phor').setOrigin(0.5, 1).setScale(0.14).setDepth(6);
        p.setInteractive({ useHandCursor: true });
        const label = this.add.text(400, 470 - p.displayHeight - 6, 'PHOR CALESTA', {
            fontSize: '13px', fill: '#c9e8ff', backgroundColor: 'rgba(0,0,0,0.5)', padding: { x: 4, y: 2 }
        }).setOrigin(0.5).setDepth(6);
        p.on('pointerover', () => { p.setScale(0.148); document.body.style.cursor = 'pointer'; });
        p.on('pointerout', () => { p.setScale(0.14); document.body.style.cursor = 'default'; });
        p.on('pointerdown', () => { if (this.dialogVisible) return; if (this.clickSound) this.clickSound.play(); this.showDialog('phor_graveyard_start'); });
    }

    createGraves() {
        // Invisible clickable zones over the painted tombstones — no HUD markers.
        // The player discovers them by hovering (name label + hand cursor), like NPCs.
        const LAYOUT = { laimig: 100, sisyla: 235, vhorn: 395, liln: 505, lietus: 615, hvetrdjaana: 730 };
        const ZW = 110, ZH = 300, CY = 250;
        this.graves().forEach(g => {
            const cx = LAYOUT[g.slug] || g.x;
            const zone = this.add.zone(cx - ZW / 2, CY - ZH / 2, ZW, ZH).setOrigin(0, 0);
            zone.setInteractive({ hitArea: new Phaser.Geom.Rectangle(0, 0, ZW, ZH), hitAreaCallback: Phaser.Geom.Rectangle.Contains, useHandCursor: true });
            const label = this.add.text(cx, 120, g.name.toUpperCase(), {
                fontSize: '12px', fill: '#e8dcc0', backgroundColor: 'rgba(0,0,0,0.6)', padding: { x: 5, y: 3 },
                align: 'center', wordWrap: { width: 170 }
            }).setOrigin(0.5).setDepth(8).setVisible(false);

            // Discreet "unread" indicator — a soft golden glint above the stone that
            // gently breathes and bobs; it vanishes once the grave has been read.
            let indicator = null, indicatorTween = null;
            if (!this.hasJournalEntry('grave_' + g.slug)) {
                indicator = this.add.text(cx, 168, '✦', { fontSize: '15px', fill: '#e6c069' }).setOrigin(0.5).setDepth(7).setAlpha(0.5);
                indicatorTween = this.tweens.add({ targets: indicator, alpha: { from: 0.35, to: 0.9 }, y: 162, duration: 1400, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
            }

            zone.on('pointerover', () => { label.setVisible(true); document.body.style.cursor = 'pointer'; });
            zone.on('pointerout', () => { label.setVisible(false); document.body.style.cursor = 'default'; });
            zone.on('pointerdown', () => {
                if (this.dialogVisible) return;
                if (this.clickSound) this.clickSound.play();
                this.showDialog('grave_' + g.slug);
                // Reading the grave clears its indicator.
                if (indicatorTween) { indicatorTween.stop(); indicatorTween = null; }
                if (indicator) { indicator.destroy(); indicator = null; }
            });
        });
    }

    update() {
        super.update();
    }

    shutdown() {
        this.restoreBackgroundMusic();
        super.shutdown();
    }
}

if (typeof window !== 'undefined') {
    window.GodgraveyardScene = GodgraveyardScene;
}

export { GodgraveyardScene };
