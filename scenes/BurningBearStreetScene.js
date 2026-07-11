import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class BurningBearStreetScene extends GameScene {
    constructor() {
        super({ key: 'BurningBearStreetScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        // Day-2 dialog is kept in its own getter so this scene doesn't accumulate
        // day-branching spaghetti. See day2DialogContent().
        return {
            ...super.dialogContent, // symbiont dialogs etc.
            ...(this.isDay2() ? this.day2DialogContent : {})
        };
    }

    // === Day 2 ===
    get day2DialogContent() {
        // Ortolan relocates here on Day 2. How much he helps depends on whether the
        // player helped him win his extra pair of arms on Day 1 (the ortolan_arms quest).
        const helped = !!this.questSystem?.getQuest('ortolan_arms')?.isComplete;
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
                        { text: "Right. The Scraper cellar.", key: 'right_scraper_cellar', next: "closeDialog" }
                    ]
                    : [
                        ...(this.hasJournalEntry('met_infinite_fold') ? [{ text: "[Before entering the cathedral] You built the old systems. What am I walking into?", key: 'perspective_ortolan_open', next: "ortolan_bb_perspective" }] : []),
                        { text: "Infinite Fold. Elphi says it's running again.", key: 'the_infinite_loop_running', next: "ortolan_bb_loop" },
                        { text: "Never mind.", key: 'never_mind_bb', next: "closeDialog" }
                    ]
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
                    if (!this.hasJournalEntry('perspective_ortolan')) {
                        this.addJournalEntry(
                            'perspective_ortolan',
                            "Ortolan's Perspective: A Flawed Make",
                            "Before entering the Egg Cathedral I asked Ortolan, a maker, what I was walking into. He gave me a builder's read of it: \"Something can be beautiful and still be badly designed\" — a thing can sing and still be broken at its root, the flaw baked into the beauty rather than opposed to it. He says the presence hatching in the cathedral is an older make than anything he built, but it was still *made*, and everything made has seams. The machinery ringing the cathedral is old-order work — pre-war regulators and dampers meant to hold the site steady, most of it now failing quietly. The one part still honestly running is the Sentinel of the Veil at the door: the last working mechanism of the old order, a guard-system wired into the city's mycelial network, still faithfully executing an instruction whose authors are all dead. Ortolan warns that a mechanism doesn't stop being dangerous just because it's obsolete — it stops being *understood*.",
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
                ]
            },

            ortolan_bb_sentinel: {
                speaker: 'Ortolan',
                text: `"The Sentinel of the Veil." He says the name the way you'd name a machine you respect and don't quite trust. "That one's the last of them — the last mechanism of the old order still honestly running. Flesh turned to plant, mind spliced into the city's mycelial net; a guard-system, really, dressed as a guardian. Someone gave it a single instruction a very long time ago — *keep the veil shut* — and every author of that instruction is dead now, and it is still executing it. Faithfully. Without appeal.\n\nThat's what makes it dangerous, and it's the same fault as the thing in the cellar: a made thing carrying out a purpose past the death of everyone who could have told it to stop. It won't reason. It won't relent. It only knows the rule it was given. If you mean to pass it, don't argue with the man — there's no man left to argue with. Work the rule."`,
                options: [
                    { text: "How do the surrounding systems tie in?", key: 'ortolan_bb_sentinel_machinery', next: "ortolan_bb_mechanisms" },
                    { text: "Ask something else.", key: 'ortolan_bb_sentinel_back', next: "ortolan_bb_perspective" },
                    { text: "Enough. Thank you, Ortolan.", key: 'ortolan_bb_sentinel_close', next: "closeDialog" }
                ]
            },

            ortolan_bb_loop: {
                speaker: 'Ortolan',
                text: `"Infinite Fold." He says it flatly — more annoyed than afraid. "An old experiment. Elphi and I built it together, years back: she shaped the dream, I shaped the game underneath. We never finished it. The city's rulers got nervous — called it dangerous, *unpredictable* — and shut the whole project down.\n\nThen Elphi and I fell out over who'd keep the keys to the games afterward. Haven't spoken since." He shrugs. "It was a game. That's all it ever was."`,
                options: [
                    { text: "Elphi thinks it killed the Bishop.", key: 'elphi_thinks_it_killed', next: "ortolan_bb_danger" },
                    { text: "Is there still a copy of it anywhere?", key: 'still_a_copy_anywhere', next: "ortolan_bb_copy" }
                ]
            },

            ortolan_bb_danger: {
                speaker: 'Ortolan',
                text: `He actually laughs. "Killed her? Elphi always did flinch at her own shadow. A game does not reach out of a helmet and stop a heart. If the Bishop died with it running, look to the hardware — or to whatever hand tampered with the cartridge — not to my rules.\n\nInfinite Fold is temperamental. Not murderous." A flicker of doubt crosses him, quickly buried. "...Unfinished, granted. But not *that.*"`,
                options: [
                    { text: "Then where could a copy be?", key: 'where_could_a_copy_be', next: "ortolan_bb_copy" },
                    { text: "I hope you're right.", key: 'i_hope_youre_right', next: "closeDialog" }
                ]
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
                        const base = 'Ortolan — now on Burning Bear Street — told me Infinite Fold was an unfinished experimental game he built with Dr. Elphi years ago. The city\'s rulers shut the project down as dangerous and unpredictable; Ortolan and Elphi then fell out over control of the games and haven\'t spoken since. He dismisses the idea that it could have killed the Bishop, blaming tampered hardware, and believes a master build is still sealed in the cellar under the Scraper — their old laboratory and workshop.';
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
                            this.questSystem.updateQuest(
                                'who_killed_bishop',
                                'Ortolan (now on Burning Bear Street) says Infinite Fold was an unfinished game he built with Dr. Elphi, shut down by the city\'s rulers as too dangerous. A master build is likely still sealed in the cellar under the Scraper — their old lab.' + (helped ? ' He also told me what it was truly built to do: ask whether a thought could arise with no single author.' : ' He wouldn\'t say more.') + ' I should search the Scraper cellar.',
                                'ortolan_infinite_loop_revealed'
                            );
                        }
                    }
                    // Start the cellar hunt: the elevator needs a dead god's name as its passphrase.
                    if (!this.hasJournalEntry('cellar_quest_started')) {
                        this.addJournalEntry(
                            'cellar_quest_started',
                            'The Sealed Cellar',
                            'A master copy of Infinite Fold sits in the sealed cellar under the Scraper — Ortolan and Dr. Elphi\'s old lab. Ortolan no longer has the key, but the elevator\'s passphrase is a dead god\'s true name, remembered only on its gravestone in the Godgraveyard beneath the Townhall. I should read the graves there (Phor Calesta can guide me) and find the right name — or lean on a faction I belong to.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Ortolan', related: 'Infinite Fold', location: 'Scraper Cellar' }
                        );
                        if (this.questSystem && !this.questSystem.getQuest('find_loop_copy')) {
                            this.questSystem.addQuest(
                                'find_loop_copy',
                                'The Sealed Cellar',
                                'Get into the sealed cellar under the Scraper, where a master copy of Infinite Fold waits. The elevator (Lift-Mother) needs a passphrase — a dead god\'s name from the graves in the Godgraveyard beneath the Townhall (read them with Phor Calesta), or ask a faction you belong to.'
                            );
                        }
                    }
                }
            }
        };
    }

    preload() {
        super.preload();
        this.load.image('burningBearStreetBg', 'assets/images/backgrounds/BurningBearStreet.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        this.load.image('ortolan', 'assets/images/characters/Ortolan.png');
        this.load.image('ortolan4', 'assets/images/characters/ortolan4.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set scraper background
        const bg = this.add.image(400, 300, 'burningBearStreetBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
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
            750, // walk to x
            470 // walk to y
        );

        this.transitionManager.createTransitionZone(
            400, // x position
            470, // y position
            80, // width
            200, // height
            'up', // direction
            'TownhallScene', // target scene
            750, // walk to x
            470 // walk to y
        );
        
        this.transitionManager.createTransitionZone(
            750, // x position
            470, // y position
            80, // width
            200, // height
            'right', // direction
            'ScreamingCorkScene', // target scene
            750, // walk to x
            470 // walk to y
        );

        if (this.isDay2()) this.setupDay2();
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
        const x = 250, groundY = 500;
        // If the player won him his extra pair of arms on Day 1, he now sports all four.
        const armsHelped = !!this.questSystem?.getQuest('ortolan_arms')?.isComplete;
        this.ortolan = this.add.sprite(x, groundY, armsHelped ? 'ortolan4' : 'ortolan').setOrigin(0.5, 1).setScale(0.15).setDepth(6);
        this.ortolan.setInteractive({ useHandCursor: true });

        const label = this.add.text(x, groundY - this.ortolan.displayHeight - 6, 'ORTOLAN', {
            fontSize: '14px', fill: '#ffdf7a', backgroundColor: 'rgba(0,0,0,0.5)', padding: { x: 5, y: 2 }
        }).setOrigin(0.5).setDepth(6);

        this.ortolan.on('pointerover', () => { this.ortolan.setScale(0.158); document.body.style.cursor = 'pointer'; });
        this.ortolan.on('pointerout', () => { this.ortolan.setScale(0.15); document.body.style.cursor = 'default'; });
        this.ortolan.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog('ortolan_bb_start');
        });

        if (!this.hasJournalEntry('ortolan_bb_meeting')) {
            this.addJournalEntry(
                'ortolan_bb_meeting',
                'Ortolan on Burning Bear Street',
                'Dr. Elphi pointed me to Ortolan about Infinite Fold. He has moved from the Shed to Burning Bear Street, buried as ever in permit paperwork.',
                this.journalSystem.categories.PEOPLE,
                { character: 'Ortolan', location: 'Burning Bear Street' }
            );
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
