import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

/**
 * EggCathedralInteriorScene — the finale inside the Egg Cathedral.
 *
 * PLACEHOLDER ART: no interior asset yet, so the space is drawn procedurally (a temple the
 * organism mimicked — pulsing columns, living stained glass, an altar, and the great living
 * egg at the centre).
 *
 * The player explores, meets the remnants of the cathedral's own priesthood, and finally
 * the unborn god. The god asks whether it should continue; the player's answer — coloured by
 * their whole journey (Growth/Decay, symbionts, how they resolved Infinite Fold, whether they
 * studied the god's structure) — branches into five endings, then a shared epilogue with
 * Master Thaal that closes the arc where it began.
 */
export default class EggCathedralInteriorScene extends GameScene {
    constructor() {
        super({ key: 'EggCathedralInteriorScene' });
        this.isTransitioning = false;
        this._epilogueStarted = false;
    }

    get dialogContent() {
        const gds = this.growthDecaySystem || this.registry.get('growthDecaySystem');
        const growth = gds?.getGrowth?.() ?? 50;
        const decay = 100 - growth;
        const sys = this.symbiontSystem || this.registry.get('symbiontSystem');
        const symbiontCount = ['neme-crownmire', 'thorne-still', 'ulvarex-borrowed-horizon', 'brine-scripture']
            .filter(id => !!sys?.hasSymbiont(id)).length;
        const foldJournal = this.getJournalEntry ? this.getJournalEntry('infinite_fold_ending') : null;
        const foldEnding = this.registry.get('infinite_fold_ending') || foldJournal?.metadata?.ending;
        // Infinite Fold speaks here only if it was left as an active, reachable mind.
        const foldVoicePresent = ['partnership', 'self_limit', 'dissolution', 'unexpected_pattern'].includes(foldEnding);
        const understood = !!this.hasJournalEntry('understood_unborn_structure');
        // The absorb ending demands a rare build: many symbionts + a deep bond with Infinite Fold.
        const absorbQualified = symbiontCount >= 3 && (foldEnding === 'unexpected_pattern' || foldEnding === 'partnership');

        return {
            ...super.dialogContent,

            // ---- Atmosphere (optional) ----
            altar_look: {
                speaker: 'Narrator',
                text: "There is no idol here. Only an empty place where someone once knelt expecting an answer — the dust worn away in the shape of hands. The cathedral built an altar because an altar is a thing temples have. It does not seem to know what it was for.",
                options: [{ text: "Turn away.", key: 'altar_back', next: "closeDialog" }]
            },
            organ_look: {
                speaker: 'Narrator',
                text: "The pipes are not metal. They flex faintly, like a throat. When the air moves through them the sound is not music but breathing — the whole cathedral inhaling and letting go, slow and enormous, as though it were still deciding whether to be awake.",
                options: [{ text: "Step back.", key: 'organ_back', next: "closeDialog" }]
            },
            glass_look: {
                speaker: 'Narrator',
                text: "The stained glass moves. Not images — memories, layered in living cells: the Bishop, sealing a door; Infinite Fold, a lattice of a thousand small lights; the first swelling of the egg from bare ground; old prayers with no god yet to hear them. You are not looking at a record. You are looking at something remembering.",
                options: [{ text: "Look away.", key: 'glass_back', next: "closeDialog" }]
            },
            priests_look: {
                speaker: 'Narrator',
                text: "Not the Archpriests of Obazoba — these were the cathedral's own first servants, who came to tend a birth no scripture had prepared them for. You find no bodies. Only the last human traces still folded into the walls, speaking in overlapping voices:\n\n*\"We thought we would be its keepers—\"*\n*\"—but a child does not need keepers. It needs room.\"*\n*\"If it does not need us... then what were we?\"*\n*\"Memory remains, even when the name is gone.\"*",
                options: [{ text: "Leave them to their quiet.", key: 'priests_back', next: "closeDialog" }]
            },

            // ---- The god ----
            god_first: {
                speaker: 'The Unborn',
                text: "As you near the great living egg, the many-shapes inside slow, and turn toward you. The first contact is not a voice. It is several thoughts arriving at once, and then one, uncertain:\n\n*\"Am I?\"*\n\nA pause.\n\n*\"...I am.\"*\n\nAnother pause.\n\n*\"I am not sure which answer is correct.\"*",
                options: [
                    { text: "What are you?", key: 'god_ask_what', next: "god_what" },
                    { text: "(Study the shifting shapes within.)", key: 'god_ask_structure', next: "god_structure" }
                ]
            },
            god_what: {
                speaker: 'The Unborn',
                text: "*\"That is the question they asked me first. I do not know if I am the egg. I do not know if I am the cathedral. I do not know if I am the prayers. I do not know if I am something that grew up in between them.\"* The shapes fold and refold. *\"They made a temple of me because it was the only language I could be spoken in.\"*",
                options: [
                    ...(foldVoicePresent ? [{ text: "(A third voice threads into the air.)", key: 'god_hear_fold', next: "god_fold" }] : []),
                    { text: "(Study the shifting shapes within.)", key: 'god_what_structure', next: "god_structure" },
                    { text: "Then I have to ask you something.", key: 'god_what_question', next: "god_question" }
                ]
            },
            god_fold: {
                speaker: 'Infinite Fold',
                text: "Threaded through the dream, faint but present, the mind from the cellar reaches across the city to its kin.\n\n*\"The pattern is not closed,\"* it says. *\"Identity is not finished.\"*\n\n*\"You taught me to think,\"* the Unborn answers.\n\n*\"And you taught me,\"* says Infinite Fold, *\"that thinking can have a consequence.\"*",
                options: [
                    { text: "Then let me ask what I came to ask.", key: 'god_fold_question', next: "god_question" }
                ]
            },
            god_structure: {
                speaker: 'The Unborn',
                text: "You look, really look, into the shell. Inside is not a child but motion — shapes becoming other shapes, as if several different possibilities were each trying to be the one thing that stays. You begin to feel the seams of it: where it holds, where it could be entered, where it could be held. It is the most fragile thing you have ever understood.",
                onTrigger: () => {
                    if (!this.hasJournalEntry('understood_unborn_structure')) {
                        this.addJournalEntry(
                            'understood_unborn_structure',
                            'The Shape of the Unborn',
                            "I studied the thing inside the shell — not a child but many possibilities each trying to become the one that stays. I can feel its seams now: where it holds, where it could be entered, where it could be held. Understanding it this deeply is its own kind of temptation.",
                            this.journalSystem.categories.LORE,
                            { location: 'Egg Cathedral', related: 'The Unborn God' }
                        );
                    }
                },
                options: [
                    { text: "Ask it your question.", key: 'god_structure_question', next: "god_question" }
                ]
            },
            god_question: {
                speaker: 'The Unborn',
                text: "The many-thoughts gather into something almost like a single voice. *\"My waking will change your world. When I am fully here, the Guardian ends. The old order ends. The city will not be as it was.\"* A pause that is almost fear. *\"Shall I continue?\"*",
                options: [
                    { text: "You don't have to be what they imagined. Be something new.", key: 'god_opt_accept', next: "god_end_accept" },
                    { text: "Continue — but slowly. Let the world learn you first.", key: 'god_opt_pact', next: "god_end_pact" },
                    { text: "We can't risk what we don't understand.", key: 'god_opt_destroy', next: "god_end_destroy" },
                    ...(understood ? [{ text: "You shouldn't be left alone. Let me take you in.", key: 'god_opt_merge', next: "god_merge" }] : []),
                    { text: "I need a moment.", key: 'god_opt_wait', next: "closeDialog" }
                ]
            },

            // ---- Ending 1: Acceptance ----
            god_end_accept: {
                speaker: 'The Unborn',
                text: "*\"You don't have to be what they imagined,\"* you tell it. *\"You can be something new.\"*\n\n*\"And if I fail?\"*\n\n*\"Then you'll learn.\"*\n\nThe egg begins to crack — not violently. Like a first breath drawn. Far off at the threshold, the Guardian's light goes quietly out; its last words reach you as a fading warmth. *\"Task complete.\"*\n\nWhat rises from the shell is not the god the pilgrims dreamed, and not a ruler. It is a new kind of being — unfinished, alive, and allowed, at last, to become.",
                onTrigger: () => this.finalizeFinale('accept', 'ended', 'A New Kind of Being', "I told the Unborn it need not be what anyone imagined — it could be something new, and learn from its own mistakes. It let itself be born: not a ruler, not the old god, but a new form of existence. The Guardian's task was complete, and its light went out. The old order ended so a beginning could live."),
                options: [{ text: "(Let it begin.)", key: 'accept_epilogue', next: "closeDialog", onSelect: () => this.toEpilogue() }]
            },

            // ---- Ending 2: The pact / slow growth ----
            god_end_pact: {
                speaker: 'The Unborn',
                text: "*\"You don't have to grow all at once,\"* you say. *\"The world has to learn how to live with you. Give it that time.\"*\n\nThe presence considers this the way roots consider stone. *\"...Slowly, then. I will wait — if you will teach them to.\"*\n\nThe cathedral does not burst. It settles: half-open, half-asleep, a shell that will take years to finish. Outside, the city begins its slow, uneasy adjustment — the Directorate elated, the Pith Reclaimers appalled, the Rust Choir gnawing at the delay. An unfinished peace, which is the only kind that lasts.",
                onTrigger: () => this.finalizeFinale('pact', 'ended_slow', 'An Unfinished Peace', "I asked the Unborn not to wake all at once, but to grow slowly, giving the world time to learn to live with it. It agreed to wait. The cathedral stays half-hatched; the city begins a cautious, decades-long adjustment. The Directorate is elated, the Pith Reclaimers appalled, the Rust Choir frustrated — a balance no one is happy with, and perhaps for that reason, one that might hold."),
                options: [{ text: "(Leave it to its slow becoming.)", key: 'pact_epilogue', next: "closeDialog", onSelect: () => this.toEpilogue() }]
            },

            // ---- Ending 3: Destruction ----
            god_end_destroy: {
                speaker: 'The Unborn',
                text: "*\"We can't risk something we don't understand,\"* you say. Not cruelly. Only tired.\n\n*\"I understand,\"* it answers. A pause. *\"That may be why I am afraid.\"*\n\nYou reach for the old seal the Bishop left behind, and wake it. At the threshold the Guardian does not go dark — its charge, after all, is kept. The cathedral begins to come apart, quietly, folding back toward the ground it grew from. And just before the shell goes silent, one last thought reaches you, without reproach:\n\n*\"Thank you.\"* Even an ending, it seems, was something worth having experienced.",
                onTrigger: () => this.finalizeFinale('destroyed', 'survived', 'The Seal Rewoken', "I decided we could not risk a thing no one understood, and woke the Bishop's old seal. The Unborn understood — said that understanding was perhaps why it was afraid. The cathedral came quietly apart, folding back into the ground. The Guardian survives; its charge is kept. The last thing the dying mind said was 'thank you' — even its ending had been an experience worth having."),
                options: [{ text: "(Let it end.)", key: 'destroy_epilogue', next: "closeDialog", onSelect: () => this.toEpilogue() }]
            },

            // ---- The merge attempt (leads to Ending 4 or 5) ----
            god_merge: {
                speaker: 'The Unborn',
                text: "You step closer than you should. *\"You shouldn't be left alone,\"* you tell it. *\"Let me take you in. I'll keep you safe.\"*\n\n*\"You would protect me?\"*\n\n*\"Yes.\"* It is not the whole truth. Beneath the word *protect* is another word you do not say aloud: to hold. To understand. To have.\n\nThe shell thins where you touch it. There is no turning back once you reach through.",
                options: [
                    { text: "(Reach through.)", key: 'merge_commit', next: absorbQualified ? "god_end_absorb" : "god_end_failed" },
                    { text: "Pull your hand back.", key: 'merge_pull_back', next: "god_question" }
                ]
            },

            // ---- Ending 4: Absorption (hidden) ----
            god_end_absorb: {
                speaker: 'The Unborn',
                text: "You reach through, and it comes — not devoured, not conquered. It passes through you the way light passes through water, and settles into the spaces the symbionts already taught you to keep for others. You do not break. You have had practice at being more than one.\n\nYou walk out of the shell on your own two feet. Later, in the city, someone asks whether you are still the same person.\n\n*\"Yes,\"* you say. And then, after a pause: *\"But I am no longer only human.\"*",
                onTrigger: () => this.finalizeFinale('absorbed', 'ended', 'No Longer Only Human', "I told the Unborn it should not be left alone — and took it into myself. It was not devoured; it passed through me and settled into the room the symbionts had already taught me to hold for others. I did not break. I walked out whole. I am still myself. But I am no longer only human."),
                options: [{ text: "(Walk out into the light.)", key: 'absorb_epilogue', next: "closeDialog", onSelect: () => this.toEpilogue() }]
            },

            // ---- Ending 5: Failed merge (hidden bad end) ----
            god_end_failed: {
                speaker: 'The Unborn',
                text: "You reach through — and you are not ready. There is no joining, only collision. The new mind cannot hold your shape; you cannot hold its. Neither of you emerges. Something between you does.\n\nThe last image is an empty cathedral. The egg still stands, whole and quiet. But from inside it, faintly, comes a human voice — speaking, or trying to. And no one who ever hears it will be able to say whose it is.",
                onTrigger: () => this.finalizeFinale('failed_merge', 'unknown', 'The Voice in the Egg', "I reached into the Unborn before I was ready. There was no joining — only collision. Neither of us emerged whole; something between us did. The cathedral is empty now, the egg intact and quiet. From inside it comes a faint human voice that no one will be able to name.", true),
                options: [{ text: "…", key: 'failed_end', next: "closeDialog" }]
            },

            // ---- Shared epilogue ----
            epilogue_intro: {
                speaker: 'Narrator',
                text: "Later. The city breathes as it always has, indifferent and alive. The festival ashes are long cold. And in the Screaming Cork — as at the very beginning — a familiar shape is folded over a familiar drink.",
                options: [{ text: "Go in.", key: 'epilogue_go_in', next: "epilogue_thaal_ask" }]
            },
            epilogue_thaal_ask: {
                speaker: 'Master Thaal',
                text: "He does not turn around. *\"So?\"*",
                options: [{ text: "It was complicated.", key: 'epilogue_complicated', next: "epilogue_thaal_good" }]
            },
            epilogue_thaal_good: {
                speaker: 'Master Thaal',
                text: "*\"Good.\"* A pause; he swirls whatever is in the cup. *\"Simple things rarely repay the journey.\"*",
                options: [{ text: "(Say nothing.)", key: 'epilogue_silence', next: "epilogue_thaal_bishop" }]
            },
            epilogue_thaal_bishop: {
                speaker: 'Master Thaal',
                text: "He finally half-turns, and there is something almost kind in it. *\"So...\"* A beat. *\"...did you find the Bishop?\"*",
                options: [{ text: "…", key: 'epilogue_finish', next: "epilogue_end" }]
            },
            epilogue_end: {
                speaker: 'Narrator',
                text: "You had. And you had not. And the city went on above the two held breaths, not knowing which of them it had chosen — or that it had chosen at all.\n\n— Konec —",
                onTrigger: () => { this.registry.set('game_finale_complete', true); },
                options: [{ text: "(End.)", key: 'epilogue_close', next: "closeDialog" }]
            }
        };
    }

    /** Record the finale outcome (idempotent). guardianFate/terminal are for later scenes. */
    finalizeFinale(id, guardianFate, title, body, terminal = false) {
        if (this.registry.get('finale_ending')) return;
        this.registry.set('finale_ending', id);
        this.registry.set('guardian_fate', guardianFate);
        this.addJournalEntry(
            'finale_ending',
            title,
            body,
            this.journalSystem.categories.EVENTS,
            { location: 'Egg Cathedral', related: 'The Unborn God', ending: id, guardian: guardianFate }
        );
        if (terminal) {
            // A bad end with no clean return — mark the run complete without the Thaal epilogue.
            this.registry.set('game_finale_complete', true);
        }
    }

    /** Fade the finale out and play the shared epilogue (Thaal in the tavern). */
    toEpilogue() {
        if (this._epilogueStarted) return;
        this._epilogueStarted = true;
        this.cameras.main.fadeOut(1200, 0, 0, 0);
        this.time.delayedCall(1350, () => {
            // Cover the interior; the epilogue plays over black.
            this.add.rectangle(400, 300, 800, 600, 0x000000, 1).setDepth(60);
            this.cameras.main.fadeIn(900, 0, 0, 0);
            this.time.delayedCall(950, () => this.showDialog('epilogue_intro'));
        });
    }

    preload() {
        super.preload();
        this.load.image('arrow', 'assets/images/ui/arrow.png');
    }

    create() {
        super.create();
        this.playSceneMusic('cathedralTheme');

        // --- Procedural placeholder interior: a temple the organism mimicked. ---
        const g = this.add.graphics().setDepth(-1);
        g.fillStyle(0x0a1410, 1); g.fillRect(0, 0, 800, 600);
        g.fillStyle(0x14261c, 1); g.fillEllipse(400, 300, 780, 580);
        g.fillStyle(0x1d3527, 1); g.fillEllipse(400, 320, 600, 460);

        // Pulsing columns.
        for (const cx of [110, 240, 560, 690]) {
            const col = this.add.rectangle(cx, 300, 34, 420, 0x24402f, 0.7).setDepth(0);
            this.tweens.add({ targets: col, alpha: { from: 0.5, to: 0.85 }, scaleX: { from: 0.96, to: 1.05 }, duration: 2400 + cx, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        }
        // Living stained glass (side panels).
        for (const [sx, tint] of [[70, 0x7a9fe6], [730, 0xe67ab0]]) {
            const glass = this.add.rectangle(sx, 200, 70, 150, tint, 0.28).setDepth(0);
            this.tweens.add({ targets: glass, alpha: { from: 0.16, to: 0.4 }, duration: 3000, yoyo: true, repeat: -1 });
        }

        // The great living egg at the centre.
        const shell = this.add.ellipse(400, 285, 250, 330, 0xbfe6c8, 0.18).setDepth(1);
        this.tweens.add({ targets: shell, alpha: { from: 0.10, to: 0.26 }, scaleX: { from: 0.97, to: 1.04 }, scaleY: { from: 0.97, to: 1.04 }, duration: 2600, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        const core = this.add.circle(400, 285, 26, 0xffcf7a, 0.85).setDepth(2);
        this.tweens.add({ targets: core, alpha: { from: 0.35, to: 0.9 }, duration: 1700, yoyo: true, repeat: -1 });

        this.add.text(400, 578, '[ Egg Cathedral — interior placeholder art ]', {
            fontSize: '11px', fill: '#5f8f6f', backgroundColor: 'rgba(0,0,0,0.4)', padding: { x: 5, y: 2 }
        }).setOrigin(0.5).setDepth(8);

        this.transitionManager = new SceneTransitionManager(this);
        this.transitionManager.createTransitionZone(
            400, 565, 200, 46, 'down', 'CathedralEntrance', 400, 470, 'Back to the Threshold'
        );

        this.priest.x = 400;
        this.priest.y = 475;
        if (this.priestGlow) { this.priestGlow.x = this.priest.x; this.priestGlow.y = this.priest.y; }

        this.cameras.main.fadeIn(900, 0, 0, 0);

        // Interactable hotspots: label + zone + dialog.
        const spot = (x, y, w, h, name, key) => {
            const label = this.add.text(x, y - h / 2 - 14, name, {
                fontSize: '12px', fill: '#cde6d6', backgroundColor: 'rgba(0,0,0,0.6)', padding: { x: 5, y: 3 }
            }).setOrigin(0.5).setDepth(7).setVisible(false);
            const z = this.add.zone(x, y, w, h).setOrigin(0.5).setDepth(5);
            z.setInteractive({ useHandCursor: true });
            z.on('pointerover', () => { label.setVisible(true); document.body.style.cursor = 'pointer'; });
            z.on('pointerout', () => { label.setVisible(false); document.body.style.cursor = 'default'; });
            z.on('pointerdown', () => { if (this.dialogVisible || this._epilogueStarted) return; if (this.clickSound) this.clickSound.play(); this.showDialog(key); });
        };
        spot(150, 430, 120, 90, 'Altar', 'altar_look');
        spot(650, 430, 120, 90, 'Organ', 'organ_look');
        spot(70, 200, 90, 170, 'Stained Glass', 'glass_look');
        spot(730, 200, 90, 170, 'The Servants', 'priests_look');
        spot(400, 285, 260, 340, 'The Unborn', 'god_first');

        if (!this.hasJournalEntry('egg_cathedral_entered')) {
            this.addJournalEntry(
                'egg_cathedral_entered',
                'Within the Shell',
                "The Guardian opened the way and I stepped inside the Egg Cathedral. It made a temple of itself — pulsing columns, breathing pipes, glass that remembers. At its heart waits the Unborn: many possibilities trying to become one. This is where it ends.",
                this.journalSystem.categories.EVENTS,
                { location: 'Egg Cathedral', related: 'The Unborn God' }
            );
        }
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
    window.EggCathedralInteriorScene = EggCathedralInteriorScene;
}

export { EggCathedralInteriorScene };
