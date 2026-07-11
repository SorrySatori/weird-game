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
        const hasOsswine = !!sys?.hasSymbiont('osswine');
        const foldJournal = this.getJournalEntry ? this.getJournalEntry('infinite_fold_ending') : null;
        const foldEnding = this.registry.get('infinite_fold_ending') || foldJournal?.metadata?.ending;
        // Infinite Fold speaks here only if it was left as an active, reachable mind.
        const foldVoicePresent = ['partnership', 'self_limit', 'dissolution', 'unexpected_pattern'].includes(foldEnding);
        const understood = !!this.hasJournalEntry('understood_unborn_structure');
        const readJournal = !!this.hasJournalEntry('bishop_journal_read');
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
                options: [{ text: "Look away.", key: 'glass_back', next: "closeDialog" }],
                onTrigger: () => {
                    if (!this.hasJournalEntry('green_mist_emergence')) {
                        this.addJournalEntry(
                            'green_mist_emergence',
                            'The Green Mist / The Emergence',
                            "The living glass remembers the day it began. A green mist rolled through the city, and then a vast egg pushed up through the ground — through layer upon layer of dead gods and forgotten faith. Many took it for the end of the world. Instead the streets shifted, the buildings grew, and the city remade itself around the swelling shell. That was the Emergence, and the egg has been becoming the Egg Cathedral ever since.",
                            this.journalSystem.categories.LORE,
                            { location: 'Egg Cathedral', related: 'The Unborn God' }
                        );
                    }
                }
            },
            priests_look: {
                speaker: 'Narrator',
                text: "Not the Archpriests of Obazoba — these were the cathedral's own first servants, who came to tend a birth no scripture had prepared them for. You find no bodies. Only the last human traces still folded into the walls, speaking in overlapping voices:\n\n*\"We thought we would be its keepers—\"*\n*\"—but a child does not need keepers. It needs room.\"*\n*\"If it does not need us... then what were we?\"*\n*\"Memory remains, even when the name is gone.\"*",
                options: [
                    ...(hasOsswine ? [{ text: '[Grave-Sense] Read how the servants ended.', key: 'grave_sense_servants', next: "servants_grave_sense" }] : []),
                    { text: "Leave them to their quiet.", key: 'priests_back', next: "closeDialog" }
                ]
            },
            // Osswine reads the servants' end — a willing dissolution into the growing god.
            servants_grave_sense: {
                speaker: 'Osswine',
                text: "Osswine stirs sluggishly — here, at the swollen heart of so much new life, it can barely wake, a mourner half-drowned in a birth. But it finds them: the faint folded traces in the walls, and it reads. *\"...These did not die. I keep reaching for the ending and there is none — only a handing-over. They came to tend a birth, understood they were not needed for it, and rather than leave, they let go. Unwound themselves, thread by thread, into the thing they were tending. Willing. Glad, even.\"*\n\nA soft, envious settling. *\"Each one's last intent was the same — not survival, but donation. To be the first material the new one was made from. There is no grief to read here, priest. That is the strangest death I have ever failed to find. They did not stop. They became someone else's beginning.\"*",
                onTrigger: () => {
                    if (!this.hasJournalEntry('grave_sense_servants')) {
                        this.addJournalEntry(
                            'grave_sense_servants',
                            "Grave-Sense: The Servants' End",
                            "Through Osswine I read the end of the cathedral's first servants — and Osswine, which reads endings, could find none. They did not die: they handed themselves over. Having come to tend the birth and understood they were not needed for it, they chose not to leave but to let go, unwinding thread by thread into the thing they tended. Willingly, even gladly. Each one's last intent was the same — not survival but donation, to be the first material the new one was made from. Osswine, which reads only endings, called it the strangest death it ever failed to find: they did not stop, they became someone else's beginning.",
                            this.journalSystem.categories.LORE,
                            { location: 'Egg Cathedral', via: 'osswine' }
                        );
                    }
                },
                options: [
                    { text: "Leave them to their quiet.", key: 'grave_sense_servants_back', next: "closeDialog" }
                ]
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
                    ...(readJournal ? [{ text: "She wrote of you. In her journal.", key: 'god_what_bishop', next: "god_bishop" }] : []),
                    { text: "(Study the shifting shapes within.)", key: 'god_what_structure', next: "god_structure" },
                    { text: "Then I have to ask you something.", key: 'god_what_question', next: "god_question" }
                ]
            },

            // Unlocked only if the player found and read the Bishop's journal in the study.
            god_bishop: {
                speaker: 'The Unborn',
                text: "*\"She wrote of me,\"* it says — not a question. *\"She feared me.\"*\n\nYou say yes.\n\n*\"But she stayed.\"*\n\nYes.\n\nA long, folding silence. *\"...Why?\"*",
                options: [
                    { text: "Because fear wasn't her last thought. It was responsibility.", key: 'god_bishop_answer', next: "god_bishop_reply" }
                ]
            },
            god_bishop_reply: {
                speaker: 'The Unborn',
                text: "The many-shapes go very still, as if holding something too large to move. *\"Responsibility,\"* it repeats, tasting the word. *\"She was afraid, and she stayed anyway, and she gave it that name. Then perhaps that is a thing I could learn to be — if I am given the chance to.\"*\n\nIt turns back to you, and the question it asked before is waiting, changed now.",
                onTrigger: () => { this.registry.set('bishop_arc_closed', true); },
                options: [
                    { text: "(Return to its question.)", key: 'god_bishop_to_question', next: "god_question" }
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
                hideCloseOption: true,
                text: "The many-thoughts gather into something almost like a single voice. *\"My waking will change your world. When I am fully here, the Guardian ends. The old order ends. The city will not be as it was.\"* A pause that is almost fear. *\"Shall I continue?\"*",
                options: [
                    { text: "You don't have to be what they imagined. Be something new.", key: 'god_opt_accept', next: "god_end_accept" },
                    { text: "Continue — but slowly. Let the world learn you first.", key: 'god_opt_pact', next: "god_end_pact" },
                    { text: "We can't risk what we don't understand.", key: 'god_opt_destroy', next: "god_end_destroy" },
                    ...(understood ? [{ text: "You shouldn't be left alone. Let me take you in.", key: 'god_opt_merge', next: "god_merge" }] : [])
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
                hideCloseOption: true,
                options: [{ text: "…", key: 'failed_end', next: "closeDialog", onSelect: () => this.rollCredits() }]
            },

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

    /** Roll the end credits (the real game-over). */
    rollCredits() {
        if (this._creditsStarted) return;
        this._creditsStarted = true;
        this.registry.set('game_finale_complete', true);
        this.cameras.main.fadeOut(1400, 0, 0, 0);
        this.time.delayedCall(1500, () => {
            this.scene.start('CreditsScene', { ending: this.registry.get('finale_ending') || null });
        });
    }

    /** Fade the finale out and hand off to the epilogue, which plays in the Screaming Cork. */
    toEpilogue() {
        if (this._epilogueStarted) return;
        this._epilogueStarted = true;
        this.registry.set('epilogue_mode', true);
        this.cameras.main.fadeOut(1400, 0, 0, 0);
        this.time.delayedCall(1500, () => this.scene.start('ScreamingCorkInteriorScene'));
    }

    preload() {
        super.preload();
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        this.load.image('cathedralHeartBg', 'assets/images/backgrounds/CathedralHeart.png');
    }

    create() {
        super.create();
        this.playSceneMusic('cathedralTheme');

        // The heart of the cathedral — where the player meets the Unborn.
        const bg = this.add.image(400, 300, 'cathedralHeartBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        this.transitionManager = new SceneTransitionManager(this);
        this.transitionManager.createTransitionZone(
            400, 565, 200, 46, 'down', 'EggCathedralStudyScene', 400, 470, 'Back to the Study'
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
                "I stepped inside the Egg Cathedral. It made a temple of itself — pulsing columns, breathing pipes, glass that remembers. At its heart waits the Unborn: many possibilities trying to become one. This is where it ends.",
                this.journalSystem.categories.PLACES,
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
