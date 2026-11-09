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
 *
 * Art: both backgrounds are native 1067×600 (tools/artgen/gyard_gate_bg.py, gyard_bg.py). Each grave is carved for its
 * god, and its hit polygon (canvas coords, printed by gyard_bg.py into gyard.json) follows the stone in the picture.
 * Osswine's pale growth in the ossuary niche is its own sprite (gyard_osswine.png), gone once it has bonded.
 */

// Canvas-space hit polygons of the graves in Godgraveyard.png (gyard_bg.py → gyard.json, simplified), where the unread
// glint sits on each stone, and the zone depth (nearer stones win where two outlines overlap).
const GRAVE_SPOTS = {
    laimig: { depth: 0.79, mark: [236, 186], poly: [[267, 152], [295, 161], [319, 175], [322, 210], [341, 218], [314, 447], [288, 472], [221, 483], [145, 494], [122, 470], [128, 423], [145, 325], [155, 232], [162, 206], [179, 181], [204, 162], [235, 153]] },
    sisyla: { depth: 0.74, mark: [352, 150], poly: [[349, 109], [398, 142], [412, 167], [415, 235], [420, 440], [362, 445], [300, 450], [290, 275], [287, 158], [300, 134]] },
    vhorn: { depth: 0.72, mark: [678, 228], poly: [[671, 196], [690, 199], [707, 211], [716, 236], [722, 319], [729, 434], [686, 435], [646, 425], [637, 293], [638, 277], [646, 274], [633, 239], [638, 216], [652, 202]] },
    liln: { depth: 0.81, mark: [767, 445], poly: [[769, 427], [793, 441], [797, 462], [791, 500], [763, 495], [737, 490], [738, 453], [745, 434]] },
    lietus: { depth: 0.70, mark: [818, 322], poly: [[823, 303], [841, 304], [871, 321], [880, 350], [869, 370], [856, 381], [840, 389], [812, 390], [781, 379], [766, 363], [763, 350], [767, 331], [776, 319], [805, 305]] },
    hvetrdjaana: { depth: 0.794, mark: [960, 318], poly: [[941, 287], [1008, 303], [1044, 327], [1061, 355], [1068, 390], [1085, 429], [1089, 463], [1099, 494], [1080, 506], [987, 488], [908, 473], [888, 457], [883, 416], [867, 354], [869, 345], [884, 341], [891, 335], [878, 312], [887, 302], [902, 294]] },
};
// The ossuary niche on the far left (the little gabled shrine full of skulls) and Osswine's growth sprite in it.
const OSSUARY = { poly: [[18, 337], [138, 337], [138, 507], [18, 507]], glint: [78, 380], sprite: [14, 394] };

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
                lore: "\"Laimig Cel — a god of wagers and games, who bet against a rival deity and lost everything, even Their own name. The epitaph is Their last move: 'I FOLD.'\"\n\nPhor lowers his voice. \"Odd thing — a divinographer before me swore two game-makers used to leave offerings at this stone. A dreamwright and her partner. They were... taken with the god who knew when to lose.\""
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
                lore: "\"Lietus Kika — god of temporal confusion, prayed to by those forever certain they did a thing only recently, when years have quietly slid by. This stone can't even agree how long it's stood here.\" Phor frowns at his own notes. \"I could swear I catalogued it last week. My handwriting says eleven years ago. The epitaph, without a shred of irony: 'IT WAS ONLY YESTERDAY.'\""
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
                    if (g.correct) this.addJournalFact('cellar_password_learned', 'laimig', "It is the epitaph of Laimig Cel, the god who lost the game.");
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
        this.clearOsswineNiche();
        if (!this.hasJournalEntry('osswine_bonded')) {
            this.addJournalEntry(
                'osswine_bonded',
                'Bonded: Osswine',
                'Among the god-graves I took on Osswine, the "late mourner" — a decay symbiont that reads the dead and the decayed through its Grave-Sense: how a thing died, its last intent, what it once was. It is the mirror of Neme (who reads the living) and goes dormant where Growth runs high.',
                this.journalSystem.categories.PEOPLE,
                { location: 'Godgraveyard', symbiont: 'osswine' }
            );
        }
        this.showNotification(this.t('notifications.symbiontGained', { name: 'Osswine' }));
    }

    /** The ossuary niche where Osswine waits (the pale growth on the skulls) — only until it has bonded. */
    createOsswineNiche() {
        this._osswineNiche = null;
        if (this.symbiontSystem?.hasSymbiont('osswine')) return;
        const growth = this.add.image(OSSUARY.sprite[0], OSSUARY.sprite[1], 'gyardOsswine').setOrigin(0, 0).setDepth(3);
        const [gx, gy] = OSSUARY.glint;
        const glint = this.add.text(gx, gy, '✦', { fontSize: '15px', fill: '#cdd7c0' }).setOrigin(0.5).setDepth(7).setAlpha(0.5);
        const glintTween = this.tweens.add({ targets: glint, alpha: { from: 0.3, to: 0.85 }, y: gy - 6, duration: 1500, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        const xs = OSSUARY.poly.map(p => p[0]), ys = OSSUARY.poly.map(p => p[1]);
        const bx = Math.min(...xs), by = Math.min(...ys), bw = Math.max(...xs) - bx, bh = Math.max(...ys) - by;
        const label = this.add.text(bx + bw / 2, by - 14, 'OSSUARY NICHE', {
            fontSize: '12px', fill: '#cdd7c0', backgroundColor: 'rgba(0,0,0,0.6)', padding: { x: 5, y: 3 }
        }).setOrigin(0.5).setDepth(8).setVisible(false);
        const zone = this.add.zone(bx, by, bw, bh).setOrigin(0, 0).setDepth(0.824);
        zone.setInteractive({
            hitArea: new Phaser.Geom.Polygon(OSSUARY.poly.map(([x, y]) => [x - bx, y - by]).flat()),
            hitAreaCallback: Phaser.Geom.Polygon.Contains, useHandCursor: true
        });
        zone.on('pointerover', () => { label.setVisible(true); document.body.style.cursor = 'pointer'; });
        zone.on('pointerout', () => { label.setVisible(false); document.body.style.cursor = 'default'; });
        zone.on('pointerdown', () => { if (this.dialogVisible) return; if (this.clickSound) this.clickSound.play(); this.showDialog('osswine_offer'); });
        this._osswineNiche = { growth, glint, glintTween, label, zone };
    }

    /** Osswine has left the niche (bonded): its growth fades from the skulls, the niche is plain scenery again. */
    clearOsswineNiche() {
        const n = this._osswineNiche;
        if (!n) return;
        this._osswineNiche = null;
        n.glintTween?.stop();
        [n.glint, n.label, n.zone].forEach(o => o?.destroy());
        document.body.style.cursor = 'default';
        if (n.growth?.scene) this.tweens.add({ targets: n.growth, alpha: 0, duration: 1200, onComplete: () => n.growth.destroy() });
    }

    preload() {
        super.preload();
        this.load.image('godgraveyardBg', 'assets/images/backgrounds/Godgraveyard.png');
        this.load.image('godgraveyardGateBg', 'assets/images/backgrounds/GodgraveyardGate.png');
        this.load.image('gyardOsswine', 'assets/images/props/gyard_osswine.png');
        this.load.spritesheet('phorIdle', 'assets/images/characters/townhall/phor.png', { frameWidth: 128, frameHeight: 160 });
        this.load.image('arrow', 'assets/images/ui/arrow.png');
    }

    create() {
        super.create();
        this.playSceneMusic('cathedralTheme');

        const access = this.hasGraveyardAccess();

        const bg = this.add.image(400, 300, access ? 'godgraveyardBg' : 'godgraveyardGateBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        // Both pictures paint their own ground (the cobbled lane / the field); drop the generic strip
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }
        // The gate "speaks" in the sealed-gate dialog: show the gate itself on the plate (EN + CZ speaker name)
        this.dialogPortraits = { ...(this.dialogPortraits || {}), 'Godgraveyard Gate': 'godgraveyardGateBg', 'Brána Bohohřbitova': 'godgraveyardGateBg' };

        this.transitionManager = new SceneTransitionManager(this);

        // Exit back up to the Town Square: the near edge of the picture (the lane / the path behind the viewer).
        this.transitionManager.createTransitionZone(
            400, 560, 200, 60, 'up', 'TownSquareScene', 400, 500, 'Town Square'
        );

        // Feet on the walk line (y 534): on the cobbled lane before the gate / left of the path in the field
        this.priest.x = access ? 400 : 470;
        this.priest.y = 470;
        if (this.priestGlow) { this.priestGlow.x = this.priest.x; this.priestGlow.y = this.priest.y; }

        // Examine: the great half-buried god's face (only once inside the open graveyard).
        // Osswine grave-senses a literal dead god; Phor's divinography reframes what you see.
        if (access) {
            // the face in the mud with its broken halo, between Sisyla's and Vhorn's stones (canvas x ~425..620)
            this.createObservable(392, 318, 146, 170, () => {
                if (this.symbiontSystem?.osswineCanRead && this.symbiontSystem.osswineCanRead()) return this.t('observe.godgraveyard.osswine');
                if (this.hasJournalEntry('phor_calesta')) return this.t('observe.godgraveyard.knows');
                return this.t('observe.godgraveyard.default');
            }, { hint: this.t('observe.godgraveyard.hint'), depth: 0.6 });
        } else {
            // Locked gate: a quick examine aside (distinct from the formal gate_sealed dialog) -- the chained leaves
            this.createObservable(400, 345, 150, 190, () => {
                if (this.hasJournalEntry('phor_calesta') || this.questSystem?.getQuest('excavation_permit')) return this.t('observe.godgraveyard_gate.knows');
                return this.t('observe.godgraveyard_gate.default');
            }, { hint: this.t('observe.godgraveyard_gate.hint') });
        }

        this.cameras.main.fadeIn(700, 0, 0, 0);

        if (!access) {
            // Sealed gate: a single interactable that explains, plus a first-visit journal note.
            this.time.delayedCall(700, () => this.showDialog('gate_sealed'));
            if (!this.hasJournalEntry('godgraveyard_gate_seen')) {
                this.addJournalEntry(
                    'godgraveyard_gate_seen',
                    'The Sealed Godgraveyard',
                    'I found the gate to the Godgraveyard, sealed with the Townhall\'s wax. I need the Townhall\'s permission — and Phor Calesta to guide me — to get inside.',
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
                'Phor Calesta took me down into the Godgraveyard beneath the Townhall — layer upon layer of fossilized dead gods. He says their gravestones tell only the truth. I can read individual graves for their names and epitaphs.',
                this.journalSystem.categories.PLACES,
                { location: 'Godgraveyard', character: 'Phor Calesta' }
            );
        }
        this.time.delayedCall(900, () => { if (!this.dialogVisible) this.showDialog('phor_graveyard_start'); });
    }

    createPhor() {
        // On the walk line at the right edge of the flagstone path, in front of the fallen face (clear of the grave
        // outlines except the very foot of Vhorn's stone). Soles on frame row 156 -> sprite y = FEET + 3.
        const PX = 600, FEET = 528;
        // 'phor_idle' is global: keep the frame list in sync with TownhallScene.
        if (!this.anims.exists('phor_idle')) {
            this.anims.create({
                key: 'phor_idle',
                frames: this.anims.generateFrameNumbers('phorIdle', { frames: [0, 0, 0, 1, 1, 7, 0, 0, 2, 0, 0, 0, 3, 4, 5, 0, 0, 0, 1, 1, 7, 0, 0, 6, 6, 0, 0, 0] }),
                frameRate: 5, repeat: -1
            });
        }
        const p = this.add.sprite(PX, FEET + 3, 'phorIdle', 0).setOrigin(0.5, 1).setDepth(6);
        p.play('phor_idle');
        this.addGroundShadow(PX + 4, FEET - 2, 70, 12);
        p.setInteractive({ hitArea: new Phaser.Geom.Rectangle(6, 18, 112, 140), hitAreaCallback: Phaser.Geom.Rectangle.Contains, useHandCursor: true });
        this.dialogPortraits = { ...(this.dialogPortraits || {}), 'Phor Calesta': { key: 'phorIdle', frame: 0, zoom: 2, top: 18 } };
        this.add.text(PX, FEET - 146, 'PHOR CALESTA', {
            fontSize: '13px', fill: '#c9e8ff', backgroundColor: 'rgba(0,0,0,0.5)', padding: { x: 4, y: 2 }
        }).setOrigin(0.5).setDepth(6);
        let hoverFx = null;
        p.on('pointerover', () => { if (!hoverFx) hoverFx = p.preFX?.addGlow(0x7fff8e, 2, 0, false, 0.1, 8); });
        p.on('pointerout', () => { if (hoverFx) { p.preFX?.remove(hoverFx); hoverFx = null; } });
        p.on('pointerdown', () => { if (this.dialogVisible) return; if (this.clickSound) this.clickSound.play(); this.showDialog('phor_graveyard_start'); });
    }

    createGraves() {
        // Invisible clickable zones shaped like the painted tombstones (GRAVE_SPOTS, canvas coords) — no HUD markers.
        // The player discovers them by hovering (name label + hand cursor), like NPCs.
        this.graves().forEach(g => {
            const spot = GRAVE_SPOTS[g.slug];
            const xs = spot.poly.map(p => p[0]), ys = spot.poly.map(p => p[1]);
            const bx = Math.min(...xs), by = Math.min(...ys), bw = Math.max(...xs) - bx, bh = Math.max(...ys) - by;
            const cx = Math.min(this.scale.width - 90, Math.max(90, bx + bw / 2));
            const zone = this.add.zone(bx, by, bw, bh).setOrigin(0, 0).setDepth(spot.depth);
            zone.setInteractive({
                hitArea: new Phaser.Geom.Polygon(spot.poly.map(([x, y]) => [x - bx, y - by]).flat()),
                hitAreaCallback: Phaser.Geom.Polygon.Contains, useHandCursor: true
            });
            const label = this.add.text(cx, Math.max(100, by - 16), g.name.toUpperCase(), {
                fontSize: '12px', fill: '#e8dcc0', backgroundColor: 'rgba(0,0,0,0.6)', padding: { x: 5, y: 3 },
                align: 'center', wordWrap: { width: 170 }
            }).setOrigin(0.5).setDepth(8).setVisible(false);

            // Discreet "unread" indicator — a soft golden glint on the stone that
            // gently breathes and bobs; it vanishes once the grave has been read.
            let indicator = null, indicatorTween = null;
            if (!this.hasJournalEntry('grave_' + g.slug)) {
                const [mx, my] = spot.mark;
                indicator = this.add.text(mx, my, '✦', { fontSize: '15px', fill: '#e6c069' }).setOrigin(0.5).setDepth(7).setAlpha(0.5);
                indicatorTween = this.tweens.add({ targets: indicator, alpha: { from: 0.35, to: 0.9 }, y: my - 6, duration: 1400, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
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
