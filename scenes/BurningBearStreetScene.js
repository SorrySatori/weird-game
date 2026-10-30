import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import { GANG_QUEST_IDS, gangQuestStatus, smuggleReportable } from '../utils/GangOfLamps.js';
import { heldArmsPaperwork, handOverArmsPaperwork } from '../utils/OrtolanArms.js';
import { preloadGDProps, applyGDBackground, placeGDProps } from '../utils/GDProps.js';

// Animated fire (tools/artgen/burningbear_bg.py): 6-frame loops packed in an atlas whose frames are trimmed against the
// full 1067×600 canvas, so a sprite at (0,0) / origin (0,0) lands exactly where that fire sits in the background.
// Frame names '<fire>_<n>': 'pit' (the fire pit, balanced + decay) and 'b0'..'b9' (the burning bears, decay only).
const FIRE_ATLAS = { balanced: 'bbs_fire_base', decayDominant: 'bbs_fire_decay' };

export default class BurningBearStreetScene extends GameScene {
    constructor() {
        super({ key: 'BurningBearStreetScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        // Day-2 dialog is kept in its own getter so this scene doesn't accumulate
        // day-branching spaghetti. See day2DialogContent().
        const hasUlvarex = !!this.symbiontSystem?.hasSymbiont('ulvarex-borrowed-horizon');
        const hasPalinode = !!this.symbiontSystem?.hasSymbiont('palinode');
        return {
            ...super.dialogContent, // symbiont dialogs etc.
            ...(this.isDay2() ? this.day2DialogContent : {}),

            // Gang of Lamps (Torchère's quest): the dead-drop, with method choices.
            smuggle_drop: {
                speaker: 'Priest',
                text: `The grate is rust-welded into the cobbles, and Torchère's parcel sits heavy in your coat — Wimlick, the kind of weight the customs men dream about. The street is quiet. For now.`,
                options: [
                    { text: "Pry the grate up and tuck it in.", key: 'smuggle_plain', next: "closeDialog", onSelect: () => this.deliverSmuggle('plain') },
                    ...(hasUlvarex ? [{ text: "[Ulvarex · Mirage Weave] Shroud the parcel and drop it unseen.", key: 'smuggle_ulvarex', next: "closeDialog", onSelect: () => this.deliverSmuggle('ulvarex') }] : []),
                    ...(hasPalinode ? [{ text: "[Palinode] Unsay the rusted grate so it opens like new.", key: 'smuggle_palinode', next: "closeDialog", onSelect: () => this.deliverSmuggle('palinode') }] : []),
                    { text: "[Betray] Keep it. Tell Torchère the drop was made. (What I do with it is my business.)", key: 'smuggle_keep', next: "closeDialog", onSelect: () => this.keepSmuggle() },
                    { text: "Not here. Not yet.", key: 'smuggle_cancel', next: "closeDialog" },
                ]
            },
        };
    }

    // === Day 2 ===
    get day2DialogContent() {
        // Ortolan relocates here on Day 2. How much he helps depends on whether the
        // player helped him win his extra pair of arms on Day 1 (the ortolan_arms quest).
        const helped = !!this.questSystem?.getQuest('ortolan_arms')?.isComplete;
        // Day-1 paperwork still in the pack: he's here now, not at the Shed, so he takes it here.
        const armsOffer = heldArmsPaperwork(this)
            ? [{ text: "I still have the paperwork for your extra arms.", key: 'ortolan_bb_arms_offer', next: "ortolan_bb_arms" }]
            : [];
        const asked = !!this.hasJournalEntry('ortolan_infinite_loop');

        return {
            speaker: 'Ortolan',

            ortolan_bb_start: {
                speaker: 'Ortolan',
                textKey: asked ? 'asked' : (helped ? 'helped' : 'cold'),
                text: asked
                    ? `He doesn't look up from the ledger balanced across two of his hands. "You again. The cellar under the Scraper — that's where the old build will be, if it's anywhere. Now let me get back to my forms."`
                    : helped
                        ? `"Well — if it isn't the soul who wrangled me a second pair of hands out of that paper-mill." He flexes all four, pleased. "I don't forget a kindness. But you've the look of someone Elphi sent... and she and I haven't traded a civil word in years. What does she want?"`
                        : `He barely glances up from his forms. "You. You watched me drown in permits and strolled on by. And now you turn up wearing Elphi's name like a badge. We haven't spoken in years, she and I. Say your piece and let me work."`,
                options: asked
                    ? [
                        ...(this.hasJournalEntry('met_infinite_fold') ? [{ text: "[Before entering the cathedral] You built the old systems. What am I walking into?", key: 'perspective_ortolan_open', next: "ortolan_bb_perspective" }] : []),
                        ...armsOffer,
                        { text: "Right. The Scraper cellar.", key: 'right_scraper_cellar', next: "closeDialog" }
                    ]
                    : [
                        ...(this.hasJournalEntry('met_infinite_fold') ? [{ text: "[Before entering the cathedral] You built the old systems. What am I walking into?", key: 'perspective_ortolan_open', next: "ortolan_bb_perspective" }] : []),
                        { text: "Infinite Fold. Elphi says it's running again.", key: 'the_infinite_loop_running', next: "ortolan_bb_loop" },
                        ...armsOffer,
                        { text: "Never mind.", key: 'never_mind_bb', next: "closeDialog" }
                    ]
            },

            ortolan_bb_arms: {
                speaker: 'Ortolan',
                text: `*He looks at the papers, then at his four hands, then at you.* "The paperwork for the arms? I got them in the end — the Shed lost my file and approved it by accident. Classic."\n\nHe takes the papers anyway and tucks them into his coat with great tenderness. "Now it's retroactively legal. You've no idea how much better that feels. Here — this was meant for you back at the Shed."`,
                options: [
                    { text: "Thank you, Ortolan.", key: 'ortolan_bb_arms_thanks', next: "ortolan_bb_start" }
                ],
                onTrigger: () => { handOverArmsPaperwork(this); }
            },

            // === Perspective branch (only after meeting Infinite Fold in the cellar) ===
            // Ortolan speaks as a maker: he understands the flaws of his own creations,
            // and reads the cathedral and its old machinery with a practical, technical eye.
            ortolan_bb_perspective: {
                speaker: 'Ortolan',
                text: `He sets down whichever ledger is nearest and, for once, gives you all four hands' worth of attention. "So you've been down to the cellar. I can see it on you — the look of someone who's had a machine talk back.\n\nThen hear a maker's honest word, since Elphi never will: something can be beautiful and still be badly designed. I've built both, sometimes in the same afternoon. A thing can sing and still be broken at the root — the flaw isn't the opposite of the beauty, it's *baked into it*. That thing hatching in the cathedral is no different. It's an older make than anything I ever bolted together, but it was still *made*, and everything made has seams. If you're walking in there, walk in knowing that."`,
                options: [
                    { text: "What surrounds it? The old machinery.", key: 'ortolan_bb_perspective_machinery', next: "ortolan_bb_mechanisms" },
                    { text: "Tell me about the guard at the door.", key: 'ortolan_bb_perspective_guard', next: "ortolan_bb_sentinel" },
                    { text: "I'll keep it in mind.", key: 'ortolan_bb_perspective_close', next: "closeDialog" }
                ],
                onTrigger: () => {
                    // Choosing to understand the make before entering the cathedral leans Growth.
                    this.gdChoiceOnce('day2_ortolan_understand', 3, 0);
                    if (!this.hasJournalEntry('perspective_ortolan')) {
                        this.addJournalEntry(
                            'perspective_ortolan',
                            "Ortolan's Perspective: A Flawed Make",
                            "Before entering the Egg Cathedral I asked Ortolan, a maker, what I was walking into. He gave me a builder's read of it: \"Something can be beautiful and still be badly designed\" — a thing can sing and still be broken at its root, the flaw baked into the beauty rather than opposed to it. He says the presence hatching in the cathedral is an older make than anything he built, but it was still *made*, and everything made has seams.",
                            this.journalSystem.categories.LORE,
                            { character: 'Ortolan', location: 'Egg Cathedral', related: 'Infinite Fold' }
                        );
                    }
                }
            },

            ortolan_bb_mechanisms: {
                speaker: 'Ortolan',
                text: `"The machinery? Old-order work, all of it — pre-war, from before the egg ever broke ground. Regulators, dampers, load-bearing wards; the sort of thing you build to hold a site *steady* while something delicate cooks inside it." He taps a knuckle on the desk in a slow, mechanical rhythm. "Most of it's failing now. Not dramatically — that's the trap. It fails the way old code fails: quietly, in the corners, doing the wrong thing very confidently. The men who tuned it are decades dead, and the site kept growing around their settings like a tree swallowing a fence.\n\nSo don't trust anything in there that hums along like it knows what it's doing. Knowing-what-it's-doing is exactly the failure mode. A well-made thing left running long enough stops being a tool and starts being *weather.*"`,
                options: [
                    { text: "And the guard at the door?", key: 'ortolan_bb_mechanisms_guard', next: "ortolan_bb_sentinel" },
                    { text: "Ask something else.", key: 'ortolan_bb_mechanisms_back', next: "ortolan_bb_perspective" },
                    { text: "Enough. Thank you, Ortolan.", key: 'ortolan_bb_mechanisms_close', next: "closeDialog" }
                ],
                onTrigger: () => {
                    this.addJournalFact('perspective_ortolan', 'machinery', "The machinery ringing the cathedral is old-order work — pre-war regulators and dampers meant to hold the site steady, most of it now failing quietly, doing the wrong thing very confidently. A well-made thing left running long enough, he warns, stops being a tool and starts being weather.");
                }
            },

            ortolan_bb_sentinel: {
                speaker: 'Ortolan',
                text: `"The Sentinel of the Veil." He says the name the way you'd name a machine you respect and don't quite trust. "That one's the last of them — the last mechanism of the old order still honestly running. Flesh turned to plant, mind spliced into the city's mycelial net; a guard-system, really, dressed as a guardian. Someone gave it a single instruction a very long time ago — *keep the veil shut* — and every author of that instruction is dead now, and it is still executing it. Faithfully. Without appeal.\n\nThat's what makes it dangerous, and it's the same fault as the thing in the cellar: a made thing carrying out a purpose past the death of everyone who could have told it to stop. It won't reason. It won't relent. It only knows the rule it was given. If you mean to pass it, don't argue with the man — there's no man left to argue with. Work the rule."`,
                options: [
                    { text: "How do the surrounding systems tie in?", key: 'ortolan_bb_sentinel_machinery', next: "ortolan_bb_mechanisms" },
                    { text: "Ask something else.", key: 'ortolan_bb_sentinel_back', next: "ortolan_bb_perspective" },
                    { text: "Enough. Thank you, Ortolan.", key: 'ortolan_bb_sentinel_close', next: "closeDialog" }
                ],
                onTrigger: () => {
                    this.addJournalFact('perspective_ortolan', 'sentinel', "The Sentinel of the Veil at the door is the last mechanism of the old order still honestly running: a guard-system wired into the city's mycelial network, still faithfully executing an instruction whose authors are all dead. It won't reason or relent — to pass it, don't argue; work the rule.");
                }
            },

            ortolan_bb_loop: {
                speaker: 'Ortolan',
                text: `"Infinite Fold." He says it flatly — more annoyed than afraid. "An old experiment. Elphi and I built it together, years back: she shaped the dream, I shaped the game underneath. We never finished it. The city's rulers got nervous — called it dangerous, *unpredictable* — and shut the whole project down.\n\nThen Elphi and I fell out over who'd keep the keys to the games afterward. Haven't spoken since." He shrugs. "It was a game. That's all it ever was."`,
                options: [
                    // Framing it as a killer to be contained leans Decay; asking after it out of curiosity leans Growth.
                    { text: "Elphi thinks it killed the Bishop.", key: 'elphi_thinks_it_killed', next: "ortolan_bb_danger", onSelect: () => this.gdChoiceOnce('day2_ortolan_frame', 0, 2) },
                    { text: "Is there still a copy of it anywhere?", key: 'still_a_copy_anywhere', next: "ortolan_bb_copy", onSelect: () => this.gdChoiceOnce('day2_ortolan_frame', 2, 0) }
                ]
            },

            ortolan_bb_danger: {
                speaker: 'Ortolan',
                text: `He actually laughs. "Killed her? Elphi always did flinch at her own shadow. A game does not reach out of a helmet and stop a heart. If the Bishop died with it running, look to the hardware — or to whatever hand tampered with the cartridge — not to my rules.\n\nInfinite Fold is temperamental. Not murderous." A flicker of doubt crosses him, quickly buried. "...Unfinished, granted. But not *that.*"`,
                options: [
                    { text: "Then where could a copy be?", key: 'where_could_a_copy_be', next: "ortolan_bb_copy" },
                    { text: "I hope you're right.", key: 'i_hope_youre_right', next: "closeDialog" }
                ],
                onTrigger: () => {
                    // Optional branch: may be heard before the ortolan_infinite_loop entry exists (shows once it does).
                    this.addJournalFact('ortolan_infinite_loop', 'dismisses_murder', "He dismisses the idea that it could have killed the Bishop — a game can't reach out of a helmet and stop a heart, he says; look to the hardware, or to whoever tampered with the cartridge.");
                }
            },

            ortolan_bb_copy: {
                speaker: 'Ortolan',
                textKey: helped ? 'helped' : 'cold',
                text: helped
                    ? `"A copy?" He sets the ledger down and goes still — all four hands quiet. "The master build. It'll still be in the cellar under the Scraper, where our old lab and workshop were. Sealed, filed, and forgotten, like everything the rulers are afraid of.\n\nAnd the cellar's locked — I don't have the key any more, the rulers took it. But the lift's passphrase... we never made one up. We used a dead god's true name — one only its gravestone still remembers. Read the graves in the Godgraveyard beneath the Townhall; a divinographer can guide you. You'll know the one when you see it.\n\nAnd since you did me a good turn — I'll tell you what it was truly for. Infinite Fold, we named it. It was never a game you could win or lose; there was no winning move, and no losing one. It was a question we built a machine to ask: can a thought arise that has no single author? We let a thousand players pour their small choices and dreams into it, and watched whether something new — a way of meaning none of us had written — would grow up out of all of them at once. The rulers pulled the plug precisely because it began to work: it started making sense in ways none of us could account for. So don't ask me what a sealed old build is now. Ask what it was built to become. That question was the whole experiment — and they were frightened enough of the answer to bury it down there."`
                    : `"A copy." He picks at a permit form, unhurried. "There'll be an old build in the cellar under the Scraper, where the lab was. It's sealed, mind — the lift wants a passphrase I've long since forgotten. Something to do with that graveyard beneath the Townhall, if that means anything to you. Beyond that, you're on your own. I've paperwork of my own, and you weren't much help with mine." He turns back to his forms.`,
                options: [
                    { text: "Thank you, Ortolan.", key: 'thanks_ortolan_bb', next: "closeDialog" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('ortolan_infinite_loop')) {
                        const base = 'Ortolan — now on Burning Bear Street — told me Infinite Fold was an unfinished experimental game he built with Dr. Elphi years ago. The city\'s rulers shut the project down as dangerous and unpredictable; Ortolan and Elphi then fell out over control of the games and haven\'t spoken since. He believes an old build is still sealed in the cellar under the Scraper — their old lab.';
                        this.addJournalEntry(
                            'ortolan_infinite_loop',
                            'Ortolan and Infinite Fold',
                            base + (helped
                                ? ' Because I helped him win his extra arms, he told me what Infinite Fold was truly for: not a game to win, but a machine built to ask whether a thought could arise with no single author — a genuinely new way of meaning, grown from a thousand players at once. The rulers buried the project precisely because it began to succeed.'
                                : ' He was curt — because I never helped him with his arms permit, he withheld anything beyond the location.'),
                            this.journalSystem.categories.EVENTS,
                            { character: 'Ortolan', location: 'Burning Bear Street', related: 'Infinite Fold' }
                        );
                        // Prep for a future confrontation with Infinite Fold — only if he trusted the player.
                        if (helped && !this.hasJournalEntry('infinite_fold_purpose')) {
                            this.addJournalEntry(
                                'infinite_fold_purpose',
                                'The Purpose of Infinite Fold',
                                'Ortolan revealed the true aim of Infinite Fold. It was never a game with a winning or losing move. He and Dr. Elphi built it to ask a single question: can a thought arise that has no single author? Thousands of players poured their choices and dreams into it, and the makers watched to see whether a genuinely new way of meaning — one none of them had written — would emerge from all of them at once. The city\'s rulers shut it down because it began to work, producing sense they could no longer account for.',
                                this.journalSystem.categories.LORE,
                                { character: 'Ortolan', related: 'Infinite Fold' }
                            );
                        }
                        if (this.questSystem?.getQuest('who_killed_bishop')) {
                            // Route-neutral base ("master build" is only said by a grateful Ortolan); the
                            // true purpose is only told if the player helped him, so it gets its own update.
                            this.questSystem.updateQuest(
                                'who_killed_bishop',
                                'Ortolan (now on Burning Bear Street) says Infinite Fold was an unfinished game he built with Dr. Elphi, shut down by the city\'s rulers as too dangerous. An old build is probably still sealed in the cellar under the Scraper — their old lab. I should search the Scraper cellar.',
                                'ortolan_infinite_loop_revealed'
                            );
                            if (helped) {
                                this.questSystem.updateQuest(
                                    'who_killed_bishop',
                                    'Ortolan also told me what Infinite Fold was truly built for: not a game to win, but a machine to ask whether a thought could arise with no single author.',
                                    'ortolan_fold_purpose'
                                );
                            }
                        }
                    }
                    // Start the cellar hunt: the elevator needs a dead god's name as its passphrase.
                    if (!this.hasJournalEntry('cellar_quest_started')) {
                        this.addJournalEntry(
                            'cellar_quest_started',
                            'The Sealed Cellar',
                            'An old build of Infinite Fold is sealed in the cellar under the Scraper — Ortolan and Dr. Elphi\'s old lab. The lift down wants a passphrase, and it has something to do with the Godgraveyard beneath the Townhall.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Ortolan', related: 'Infinite Fold', location: 'Scraper Cellar' }
                        );
                        // Only a grateful Ortolan explains the passphrase (the curt one barely names the graveyard).
                        if (helped) {
                            this.addJournalFact('cellar_quest_started', 'passphrase', "Ortolan no longer has the key, but the passphrase is a dead god's true name, remembered only on its gravestone in the Godgraveyard. I should read the graves there and find the right name — a divinographer could guide me.");
                            if (this.hasJournalEntry('phor_calesta')) {
                                this.addJournalFact('cellar_quest_started', 'phor', "Phor Calesta is a divinographer — he could read the graves with me.");
                            }
                        }
                        if (this.questSystem && !this.questSystem.getQuest('find_loop_copy')) {
                            // Route-neutral: the curt Ortolan only says "an old build" and "something to do
                            // with that graveyard". The dead-god detail (and Phor, if met) mirror the journal facts above.
                            this.questSystem.addQuest(
                                'find_loop_copy',
                                'The Sealed Cellar',
                                'Get into the sealed cellar under the Scraper, where Ortolan says an old build of Infinite Fold is kept. The lift down (Lift-Mother) wants a passphrase — something to do with the Godgraveyard beneath the Townhall.'
                            );
                            if (helped) {
                                this.questSystem.updateQuest('find_loop_copy', "Ortolan told me the passphrase is a dead god's true name, remembered only on its gravestone in the Godgraveyard. I should read the graves there — a divinographer could guide me.", 'passphrase_dead_god');
                                if (this.hasJournalEntry('phor_calesta')) {
                                    this.questSystem.updateQuest('find_loop_copy', 'Phor Calesta is a divinographer — he could read the graves with me.', 'phor_can_read_graves');
                                }
                            }
                        }
                    }
                }
            }
        };
    }

    preload() {
        super.preload();
        this.preloadMusic('streetSong');
        this.load.image('burningBearStreetBg', 'assets/images/backgrounds/BurningBearStreet.png');   // native 1067×600 (redrawn)
        this.load.image('burningBearStreetBg_growth', 'assets/images/backgrounds/BurningBearStreet_growth.png');
        this.load.image('burningBearStreetBg_decay', 'assets/images/backgrounds/BurningBearStreet_decay.png');
        preloadGDProps(this);
        this.load.atlas('bbs_fire_base', 'assets/images/props/bbs_fire_base.png', 'assets/images/props/bbs_fire_base.json');
        this.load.atlas('bbs_fire_decay', 'assets/images/props/bbs_fire_decay.png', 'assets/images/props/bbs_fire_decay.json');
        this.load.image('exitArea', 'assets/images/ui/door.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        this.load.spritesheet('ortolanIdle', 'assets/images/characters/ortolan_idle.png', { frameWidth: 128, frameHeight: 160 });
        this.load.spritesheet('ortolan4Idle', 'assets/images/characters/ortolan4_idle.png', { frameWidth: 144, frameHeight: 160 });
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        this.playSceneMusic('streetSong', { resume: true });
        
        // Set scraper background
        const bg = this.add.image(400, 300, 'burningBearStreetBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        this.applyBearStreetGDState(bg);
        // The background paints its own cobbles and pavements; the generic ground strip would cover them.
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        
        // Position the priest at the right side when entering
        this.priest.x = 700;
        this.priest.y = 470;
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);

        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            80, // width
            200, // height
            'left', // direction
            'ScraperScene', // target scene
            60, // walk to x (into the left archway)
            470 // walk to y
        );

        this.transitionManager.createTransitionZone(
            400, // x position (800-space; the far end of the street, toward the Townhall tower)
            375, // y position — above the fire pit, so clicking the pit doesn't leave the scene
            90, // width
            110, // height
            'up', // direction
            'TownhallScene', // target scene
            400, // walk to x
            470 // walk to y
        );
        
        this.transitionManager.createTransitionZone(
            750, // x position
            470, // y position
            80, // width
            200, // height
            'right', // direction
            'ScreamingCorkScene', // target scene
            745, // walk to x (into the right archway)
            470 // walk to y
        );

        this.createSmuggleDeadDrop();

        if (this.isDay2()) this.setupDay2();
    }

    // Gang of Lamps (Torchère's quest): a loose grate on the street the player uses as a
    // dead-drop for the contraband. Only present while the run is active and undelivered.
    // Clicking opens a route-choice dialog (plain / Ulvarex / Palinode).
    createSmuggleDeadDrop() {
        const active = gangQuestStatus(this, GANG_QUEST_IDS.torchere) === 'active';
        // Hide the grate once the run is resolved any way (dropped, kept, or diverted to a
        // faction). `smuggleReportable` covers all of those; still requires the parcel in hand.
        const unresolved = !smuggleReportable(this);
        const hasParcel = this.hasItem('wimlick');
        if (!active || !unresolved || !hasParcel) return;

        const x = 610, y = 545;
        const grate = this.add.rectangle(x, y, 46, 22, 0x0a0d0a, 0.55).setDepth(3);
        grate.setStrokeStyle(2, 0x1c241c, 0.9);
        grate.setInteractive({ useHandCursor: true });
        const hint = this.add.text(x, y - 26, 'Loose grate', {
            fontSize: '13px', fill: '#7fff8e', backgroundColor: 'rgba(0,0,0,0.5)', padding: { x: 5, y: 2 }
        }).setOrigin(0.5).setDepth(10).setAlpha(0);
        grate.on('pointerover', () => { hint.setAlpha(1); document.body.style.cursor = 'pointer'; });
        grate.on('pointerout', () => { hint.setAlpha(0); document.body.style.cursor = 'default'; });
        this._smuggleDropCleanup = () => { grate.disableInteractive(); grate.destroy(); hint.destroy(); this._smuggleDropCleanup = null; };
        grate.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog('smuggle_drop');
        });
    }

    // Complete Torchère's dead-drop. `mode`: 'plain' | 'ulvarex' | 'palinode'. Running narcotics
    // sours the balance toward Decay; wearing Ulvarex's mirage to do it unseen sours it further.
    deliverSmuggle(mode) {
        this.removeItemFromInventory('wimlick');
        if (!this.hasJournalEntry('gang_smuggle_delivered')) {
            this.addJournalEntry('gang_smuggle_delivered', 'The Drop Is Made', "I tucked Torchère's parcel — the Wimlick — into the loose grate on Burning Bear Street. I should report back to the torch by the water.", this.journalSystem.categories.EVENTS, { group: 'Gang of Lamps', related: 'A Run Past the Customs' });
            if (this.questSystem?.getQuest(GANG_QUEST_IDS.torchere)) {
                this.questSystem.updateQuest(GANG_QUEST_IDS.torchere, 'The Wimlick is in the grate. Report back to Torchère at the Harbor.', 'gang_smuggle_delivered');
            }
        }
        if (mode === 'ulvarex') {
            this.modifyGrowthDecay(0, 6);
            this.addMoney(10);
            this.notifyShift('clean_run_lie', 'decay');
        } else {
            this.modifyGrowthDecay(0, 4);
            this.notifyShift('contraband_dropped', 'decay');
        }
        if (this._smuggleDropCleanup) this._smuggleDropCleanup();
    }

    // Betrayal: DON'T make the drop — pocket the Wimlick and lie to Torchère that it's done.
    // The parcel STAYS in the inventory: the player can later sell it to any trader with a
    // buy/sell counter, use it themselves, or (before reporting to Torchère) still reconsider.
    keepSmuggle() {
        if (!this.hasJournalEntry('gang_smuggle_kept')) {
            this.addJournalEntry('gang_smuggle_kept', 'Kept the Contraband', "I never made Torchère's drop. I'm keeping the Wimlick — I can sell it to a trader for coin, try it myself, or just sit on it. Whatever I do, when I see the torch by the water I'll tell him the run went clean.", this.journalSystem.categories.EVENTS, { group: 'Gang of Lamps', related: 'A Run Past the Customs' });
            if (this.questSystem?.getQuest(GANG_QUEST_IDS.torchere)) {
                this.questSystem.updateQuest(GANG_QUEST_IDS.torchere, "I kept Torchère's Wimlick for myself instead of dropping it. I can still report a 'clean drop' to him at the Harbor — and the parcel is mine to sell or use.", 'gang_smuggle_kept');
            }
        }
        this.modifyGrowthDecay(0, 4);
        this.notifyShift('parcel_kept', 'decay');
        if (this._smuggleDropCleanup) this._smuggleDropCleanup();
    }

    // Growth/Decay: alt background (overgrown street / the bears burning) + scenery props.
    // Decay also gets live fire: flickering glow over every burning bear and the bonfire, and rising embers.
    applyBearStreetGDState(bg) {
        applyGDBackground(this, bg, 'burningBearStreetBg');
        placeGDProps(this, {
            growth: [                                             // flowering bushes by the archways (spring, not mould)
                { prop: 'bush', x: 112, y: 514 },
                { prop: 'bush', x: 962, y: 510, flipX: true, scale: 0.85 }
            ],
            decay: [
                { prop: 'trash', x: 168, y: 514 },
                { prop: 'rubble', x: 905, y: 508 },
                { prop: 'crate', x: 300, y: 470, scale: 0.8 }
            ]
        });
        this.addStreetFires(this.getGDTendency());
    }

    // Animated flames from the fire atlas (pit when balanced; pit + every hanging bear on Decay). On Decay each fire
    // also gets a flickering additive glow and rising embers. Growth: the pit is overgrown, no fire.
    addStreetFires(tendency) {
        const key = FIRE_ATLAS[tendency];
        if (!key || !this.textures.exists(key)) return;
        const tex = this.textures.get(key);
        const fires = [...new Set(tex.getFrameNames().map(n => n.replace(/_\d+$/, '')))];
        fires.forEach((name, i) => {
            const animKey = `${key}_${name}`;
            if (!this.anims.exists(animKey)) {
                const frames = tex.getFrameNames().filter(n => n.startsWith(name + '_')).sort((a, b) => parseInt(a.split('_').pop()) - parseInt(b.split('_').pop()));
                this.anims.create({ key: animKey, frames: frames.map(frame => ({ key, frame })), frameRate: 8, repeat: -1 });
            }
            const sprite = this.add.sprite(0, 0, key, `${name}_0`).setOrigin(0, 0).setDepth(0.55);
            sprite.play({ key: animKey, startFrame: i % 6 });
        });
        if (tendency === 'decayDominant') this.addBurningBearFX(tex, fires);
    }

    addBurningBearFX(tex, fireNames) {
        if (!this.textures.exists('bbs_ember')) {
            const g = this.make.graphics({ x: 0, y: 0, add: false });
            g.fillStyle(0xffffff, 1).fillRect(0, 0, 2, 2);
            g.generateTexture('bbs_ember', 2, 2);
            g.destroy();
        }
        // Glow + embers sit on each fire's trimmed box (spriteSourceSize = where the frame lies on the canvas).
        const fires = fireNames.map(name => {
            const fr = tex.get(`${name}_0`);
            const b = fr.customData?.spriteSourceSize || { x: fr.x, y: fr.y, w: fr.width, h: fr.height };
            return { x: b.x + b.w / 2, y: b.y + b.h * 0.6, w: b.w * 0.9, h: b.h * 0.8, top: b.y + b.h * 0.35 };
        });
        fires.forEach((f, i) => {
            const glow = this.add.graphics().setDepth(0.6).setBlendMode(Phaser.BlendModes.ADD);
            for (let k = 3; k >= 1; k--) {
                glow.fillStyle(0xd9ad52, 0.022);
                glow.fillEllipse(f.x, f.y, f.w * (k + 1) / 2, f.h * (k + 1) / 3);
            }
            this.tweens.add({ targets: glow, alpha: { from: 0.5, to: 1 }, duration: 180 + (i % 4) * 70, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
            this.add.particles(f.x, f.top + 6, 'bbs_ember', {
                x: { min: -f.w * 0.3, max: f.w * 0.3 },
                speedY: { min: -70, max: -25 }, speedX: { min: -14, max: 18 },
                lifespan: { min: 900, max: 1800 }, frequency: 120 + (i % 3) * 60, quantity: 1,
                alpha: { start: 1, end: 0 }, scale: { start: 1, end: 0.4 },
                tint: [0xefcb73, 0xd9ad52, 0xa24a37], blendMode: 'ADD'
            }).setDepth(0.7);
        });
    }

    // === Day 2 ===
    // All Day-2 scene content lives here, kept out of create() to avoid day-branching sprawl.
    setupDay2() {
        // Once Dr. Elphi has sent the player about Infinite Fold, Ortolan has
        // relocated here from Shed 521.
        if (this.hasJournalEntry('infinite_loop_ortolan_lead')) {
            this.createOrtolan();
        }
    }

    createOrtolan() {
        const x = 250, groundY = 525;
        // If the player won him his extra pair of arms on Day 1, he now sports all four.
        const armsHelped = !!this.questSystem?.getQuest('ortolan_arms')?.isComplete;
        // tools/artgen/ortolan_elphi.py: 8 idle frames at scale 1, soles on y 156 of the 160 px frame
        const SEQ = [0, 0, 1, 1, 7, 0, 0, 2, 0, 0, 0, 1, 1, 7, 0, 3, 3, 0, 0, 4, 4, 0, 1, 1, 7, 0, 0, 5, 5, 0, 0, 6, 6, 0, 0, 0];
        if (!this.anims.exists('ortolan_idle')) this.anims.create({ key: 'ortolan_idle', frames: this.anims.generateFrameNumbers('ortolanIdle', { frames: SEQ }), frameRate: 4, repeat: -1 });
        if (!this.anims.exists('ortolan4_idle')) this.anims.create({ key: 'ortolan4_idle', frames: this.anims.generateFrameNumbers('ortolan4Idle', { frames: SEQ }), frameRate: 4, repeat: -1 });
        this.ortolan = this.add.sprite(x, groundY + 4, armsHelped ? 'ortolan4Idle' : 'ortolanIdle', 0).setOrigin(0.5, 1).setDepth(6);
        this.ortolan.play(armsHelped ? 'ortolan4_idle' : 'ortolan_idle');
        this._ortolanHoverFx = null;  // the scene instance is reused
        this.addGroundShadow(x, groundY - 1, armsHelped ? 70 : 46, 12);
        this.ortolan.setInteractive({ useHandCursor: true });

        const label = this.add.text(x, groundY - 151 - 10, 'ORTOLAN', {
            fontSize: '14px', fill: '#ffdf7a', backgroundColor: 'rgba(0,0,0,0.5)', padding: { x: 5, y: 2 }
        }).setOrigin(0.5).setDepth(6);

        this.ortolan.on('pointerover', () => {   // a soft glow, not scaling (scaling smears the pixel art)
            if (!this._ortolanHoverFx) this._ortolanHoverFx = this.ortolan.preFX?.addGlow(0xffdf7a, 2, 0, false, 0.1, 8);
            document.body.style.cursor = 'pointer';
        });
        this.ortolan.on('pointerout', () => {
            if (this._ortolanHoverFx) { this.ortolan.preFX?.remove(this._ortolanHoverFx); this._ortolanHoverFx = null; }
            document.body.style.cursor = 'default';
        });
        this.ortolan.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog('ortolan_bb_start');
        });

        if (!this.hasJournalEntry('ortolan_bb_meeting')) {
            this.addJournalEntry(
                'ortolan_bb_meeting',
                'Ortolan on Burning Bear Street',
                'Dr. Elphi pointed me to Ortolan about Infinite Fold. He has moved to Burning Bear Street.',
                this.journalSystem.categories.PEOPLE,
                { character: 'Ortolan', location: 'Burning Bear Street' }
            );
        }
        // Only someone who met him at the Shed on Day 1 knows where he came from.
        if (this.hasJournalEntry('ortolan_meeting') || this.questSystem?.getQuest('ortolan_arms')) {
            this.addJournalFact('ortolan_bb_meeting', 'shed', "He used to keep to the Shed; now he's set up here, buried as ever in permit paperwork.");
        }
    }

    update() {
        super.update();
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.BurningBearStreetScene = BurningBearStreetScene;
}
