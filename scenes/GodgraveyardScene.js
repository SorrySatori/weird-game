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
        const hasBrine = !!this.symbiontSystem?.hasSymbiont('brine-scripture');
        const hasOsswine = !!this.symbiontSystem?.hasSymbiont('osswine');
        const hasFreeSlot = !!this.symbiontSystem && this.symbiontSystem.symbionts.size < this.symbiontSystem.unlockedSlots;
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
            const graveOptions = [
                { text: "Note it down.", key: 'note_it_down_' + g.slug, next: "closeDialog" }
            ];
            // Only Hvétrdjaana's stone is unreadable — Brine can taste the salt where the letters wore away.
            if (g.slug === 'hvetrdjaana' && hasBrine) {
                graveOptions.unshift({ text: '[Salt Recall] Read the letters the stone forgot.', key: 'salt_recall_hvetrdjaana', next: 'hvetrdjaana_salt_recall' });
            }
            // Osswine can read the exact moment the tally-keeper's counting broke.
            if (g.slug === 'vhorn' && hasOsswine) {
                graveOptions.unshift({ text: '[Grave-Sense] Read how Vhorn died.', key: 'grave_sense_vhorn', next: 'vhorn_grave_sense' });
            }
            states['grave_' + g.slug] = {
                speaker: 'Phor Calesta',
                text: `You brush moss from the stone. Phor reads over your shoulder:\n\n${g.lore}`,
                options: graveOptions,
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

        // Brine Scripture reads the salt of the one grave no living hand can — Hvétrdjaana's.
        states['hvetrdjaana_salt_recall'] = {
            speaker: 'Brine Scripture',
            text: `Brine Scripture stirs against the unreadable stone and tastes the mineral ghost of letters that wore away centuries before Phor was born. *"...The salt still holds their shape, the way a dry bed holds the river that left it. Hvétrdjaana. The urbzunids and the krobulovits prayed to her when they wished to be unremembered — she was the keeper of merciful forgetting, who lifted the weight of names off the dead, the shamed, the simply tired. They loved her for the mercy of it."*\n\nThe residue shifts, reluctant. *"And that was her undoing. A goddess of forgetting cannot ask to be remembered — it would betray the whole of her. So when her peoples faded, she chose to fade with them, and let her own name rot from her own stone. Not lost, priest. Given away. The last thing she ever forgot was herself."*`,
            onTrigger: () => {
                if (!this.hasJournalEntry('salt_recall_hvetrdjaana')) {
                    this.addJournalEntry(
                        'salt_recall_hvetrdjaana',
                        'Salt Recall: The Unreadable Grave',
                        'Through Brine Scripture I read the salt of Hvétrdjaana\'s grave — the one stone even Phor cannot decipher, its script worn to nothing. Brine tasted the ghost-shape of the vanished letters and recovered her: goddess of the urbzunids and the krobulovits, keeper of merciful forgetting, who lifted the weight of names off the dead and the shamed. When her peoples faded she chose to fade with them and let her own name rot from her stone — not lost, but given away. A goddess of the forgotten who forgot herself last of all.',
                        this.journalSystem.categories.LORE,
                        { location: 'Godgraveyard', via: 'brine-scripture' }
                    );
                }
            },
            options: [
                { text: 'Step back.', key: 'salt_recall_hvetrdjaana_back', next: 'closeDialog' }
            ]
        };

        // Osswine reads the death of the tally-keeper — the instant the sums broke.
        states['vhorn_grave_sense'] = {
            speaker: 'Osswine',
            text: `Osswine leans into the tally-keeper's fossilised bone and reads the exact instant the counting stopped. *"...Here. A follower knelt where you kneel now and set down a proof — clean, patient, undeniable — that the numbers had never once balanced. Not since the first tally he ever made. Vhorn saw it. And in the seeing the whole of him came apart, because a god who is only a ledger cannot survive a single unaccountable coin."*\n\nThe residue stills, like a column of figures refusing to add. *"His last intent was not rage. It was to recount — to run the sum one more time, certain the error lay in the follower and not the world. He died mid-addition, reaching for a total that would never arrive. The last thing in him was a number with no number after it."*`,
            onTrigger: () => {
                if (!this.hasJournalEntry('grave_sense_vhorn')) {
                    this.addJournalEntry(
                        'grave_sense_vhorn',
                        'Grave-Sense: How Vhorn Died',
                        'Through Osswine I read the death of Vhorn the Tally-Keeper. A follower knelt at the grave and laid down an undeniable proof that Vhorn\'s numbers had never once balanced — not since the first tally. In the seeing, the god came apart, for a god who is only a ledger cannot survive a single unaccountable coin. His last intent was not rage but to recount, to run the sum one more time, certain the error lay with the follower and not the world. He died mid-addition, reaching for a total that never arrived — his final thought a number with no number after it.',
                        this.journalSystem.categories.LORE,
                        { location: 'Godgraveyard', via: 'osswine' }
                    );
                }
            },
            options: [
                { text: 'Step back.', key: 'grave_sense_vhorn_back', next: 'closeDialog' }
            ]
        };

        // --- Osswine, the late mourner: a decay symbiont bonded among the god-graves. ---
        states['osswine_offer'] = {
            speaker: 'Osswine',
            text: `In a niche of stacked skulls at the graveyard's edge, something pale and dry unfurls — not a plant, not quite. It has waited among the dead so long it has half become them. A voice like grave-dust settles at the back of your skull:\n\n"You walk among the ended and do not flinch. Rare. I am Osswine — the late mourner. The living have Neme and her kind to read their breathing lies. No one reads the dead. I would. Carry me, and what has stopped will speak to you: how it died, what it meant, what it was before it went quiet."`,
            options: [
                ...(hasFreeSlot
                    ? [{ text: "Bond with it. (take Osswine)", key: 'osswine_bond', next: 'osswine_accept' }]
                    : [{ text: "I have no room to carry it.", key: 'osswine_no_room', next: 'osswine_no_slot' }]),
                { text: "What are you, exactly?", key: 'osswine_what', next: 'osswine_about' },
                { text: "Leave it among the bones.", key: 'osswine_leave', next: 'closeDialog' }
            ]
        };
        states['osswine_about'] = {
            speaker: 'Osswine',
            text: `"I am what settles into a thing once its purpose leaves — the reader of endings. I wake where the city rots and sleep where it blooms; too much life and I go dumb. Fitting, for a mourner. Neme keeps the living pulse; I keep the last echo. Between us, little would stay hidden."`,
            options: [
                { text: "Back.", key: 'osswine_about_back', next: 'osswine_offer' }
            ]
        };
        states['osswine_no_slot'] = {
            speaker: 'Osswine',
            text: `The pale growth stills. "You are already full — another rider crowds your marrow. Make room and come back. The shape-clerks at the Shed will register a vessel, or the rust-folk will weld you one. The dead are patient. It is our one virtue."`,
            options: [
                { text: "I'll come back.", key: 'osswine_no_slot_back', next: 'closeDialog' }
            ]
        };
        states['osswine_accept'] = {
            speaker: 'Osswine',
            text: `You reach into the niche. Cold filaments thread up your wrist and settle, dry and patient, along your bones. The graveyard seems to lean a little closer.\n\n"Good. Now — bring me what has ended, and I will tell you how."`,
            onTrigger: () => this.bondOsswine(),
            options: [
                { text: "Understood.", key: 'osswine_accept_ok', next: 'closeDialog' }
            ]
        };

        return states;
    }

    /** Bond the Osswine symbiont (Grave-Sense). Mirrors the other acquisition flows. */
    bondOsswine() {
        if (this.symbiontSystem?.hasSymbiont('osswine')) return;
        const data = { name: 'Osswine', power: 0, ability: 'Grave-Sense', phrases: this.symbiontSystem.getSymbiontPhrases('osswine') };
        const success = this.symbiontSystem?.addSymbiont('osswine', data);
        if (!success) { this.showNotification('No free symbiont slot!'); return; }
        if (this.addSymbiontIcon) this.addSymbiontIcon('osswine', data);
        if (!this.hasJournalEntry('osswine_bonded')) {
            this.addJournalEntry(
                'osswine_bonded',
                'Bonded: Osswine',
                'Among the god-graves I took on Osswine, the "late mourner" — a decay symbiont that reads the dead and the decayed through its Grave-Sense: how a thing died, its last intent, what it once was. It is the mirror of Neme (who reads the living) and goes dormant where Growth runs high.',
                this.journalSystem.categories.PEOPLE,
                { location: 'Godgraveyard', symbiont: 'osswine' }
            );
        }
        this.showNotification('Gained Symbiont: Osswine');
    }

    /** The ossuary niche where Osswine waits — only until it has bonded. */
    createOsswineNiche() {
        if (this.symbiontSystem?.hasSymbiont('osswine')) return;
        const cx = 60, cy = 300;
        const glint = this.add.text(cx, cy - 40, '✦', { fontSize: '15px', fill: '#cdd7c0' }).setOrigin(0.5).setDepth(7).setAlpha(0.5);
        this.tweens.add({ targets: glint, alpha: { from: 0.3, to: 0.85 }, y: cy - 46, duration: 1500, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        const label = this.add.text(cx, cy - 72, 'OSSUARY NICHE', {
            fontSize: '12px', fill: '#cdd7c0', backgroundColor: 'rgba(0,0,0,0.6)', padding: { x: 5, y: 3 }
        }).setOrigin(0.5).setDepth(8).setVisible(false);
        const zone = this.add.zone(cx - 45, cy - 90, 90, 180).setOrigin(0, 0);
        zone.setInteractive({ hitArea: new Phaser.Geom.Rectangle(0, 0, 90, 180), hitAreaCallback: Phaser.Geom.Rectangle.Contains, useHandCursor: true });
        zone.on('pointerover', () => { label.setVisible(true); document.body.style.cursor = 'pointer'; });
        zone.on('pointerout', () => { label.setVisible(false); document.body.style.cursor = 'default'; });
        zone.on('pointerdown', () => { if (this.dialogVisible) return; if (this.clickSound) this.clickSound.play(); this.showDialog('osswine_offer'); });
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

        // Open graveyard: Phor + clickable graves + the ossuary niche (Osswine).
        this.createPhor();
        this.createGraves();
        this.createOsswineNiche();

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
