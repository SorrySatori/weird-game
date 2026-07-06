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
                    ? [{ text: "Right. The Scraper cellar.", key: 'right_scraper_cellar', next: "closeDialog" }]
                    : [
                        { text: "The Infinite Loop. Elphi says it's running again.", key: 'the_infinite_loop_running', next: "ortolan_bb_loop" },
                        { text: "Never mind.", key: 'never_mind_bb', next: "closeDialog" }
                    ]
            },

            ortolan_bb_loop: {
                speaker: 'Ortolan',
                text: `"The Infinite Loop." He says it flatly — more annoyed than afraid. "An old experiment. Elphi and I built it together, years back: she shaped the dream, I shaped the game underneath. We never finished it. The city's rulers got nervous — called it dangerous, *unpredictable* — and shut the whole project down.\n\nThen Elphi and I fell out over who'd keep the keys to the games afterward. Haven't spoken since." He shrugs. "It was a game. That's all it ever was."`,
                options: [
                    { text: "Elphi thinks it killed the Bishop.", key: 'elphi_thinks_it_killed', next: "ortolan_bb_danger" },
                    { text: "Is there still a copy of it anywhere?", key: 'still_a_copy_anywhere', next: "ortolan_bb_copy" }
                ]
            },

            ortolan_bb_danger: {
                speaker: 'Ortolan',
                text: `He actually laughs. "Killed her? Elphi always did flinch at her own shadow. A game does not reach out of a helmet and stop a heart. If the Bishop died with it running, look to the hardware — or to whatever hand tampered with the cartridge — not to my rules.\n\nThe Loop is temperamental. Not murderous." A flicker of doubt crosses him, quickly buried. "...Unfinished, granted. But not *that.*"`,
                options: [
                    { text: "Then where could a copy be?", key: 'where_could_a_copy_be', next: "ortolan_bb_copy" },
                    { text: "I hope you're right.", key: 'i_hope_youre_right', next: "closeDialog" }
                ]
            },

            ortolan_bb_copy: {
                speaker: 'Ortolan',
                textKey: helped ? 'helped' : 'cold',
                text: helped
                    ? `"A copy?" He sets the ledger down and goes still — all four hands quiet. "The master build. It'll still be in the cellar under the Scraper, where our old lab and workshop were. Sealed, filed, and forgotten, like everything the rulers are afraid of.\n\nAnd since you did me a good turn — listen closely. If that thing truly has someone caught inside, you don't smash your way out. Every board I ever built hides a *losing move* — one choice the game pretends isn't there, that lets the piece decide to leave. Elphi's seamless walls buried it, but my rules are still underneath. Find the losing move, and you can pull someone out. Remember that."`
                    : `"A copy." He picks at a permit form, unhurried. "There'll be an old build in the cellar under the Scraper. That's where the lab was. Beyond that — you're on your own. I've paperwork of my own to fight, and you weren't much help with mine." He turns back to his forms.`,
                options: [
                    { text: "Thank you, Ortolan.", key: 'thanks_ortolan_bb', next: "closeDialog" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('ortolan_infinite_loop')) {
                        const base = 'Ortolan — now on Burning Bear Street — told me the Infinite Loop was an unfinished experimental game he built with Dr. Elphi years ago. The city\'s rulers shut the project down as dangerous and unpredictable; Ortolan and Elphi then fell out over control of the games and haven\'t spoken since. He dismisses the idea that it could have killed the Bishop, blaming tampered hardware, and believes a master build is still sealed in the cellar under the Scraper — their old laboratory and workshop.';
                        this.addJournalEntry(
                            'ortolan_infinite_loop',
                            'Ortolan and the Infinite Loop',
                            base + (helped
                                ? ' Because I helped him win his extra arms, he shared how to free a trapped mind: every board he built hides a "losing move" — one choice the game hides that lets a trapped piece choose to leave. I\'ll need that if I ever enter the Loop.'
                                : ' He was curt — because I never helped him with his arms permit, he withheld anything beyond the location.'),
                            this.journalSystem.categories.EVENTS,
                            { character: 'Ortolan', location: 'Burning Bear Street', related: 'The Infinite Loop' }
                        );
                        // Prep for a future confrontation with the Loop — only if he trusted the player.
                        if (helped && !this.hasJournalEntry('ortolan_losing_move')) {
                            this.addJournalEntry(
                                'ortolan_losing_move',
                                'The Losing Move',
                                'Ortolan revealed that every board he designed — including the Infinite Loop — hides a "losing move": one choice the game conceals that lets a trapped mind decide to leave. To pull someone out of the Loop, I must find and make that losing move rather than trying to force an escape.',
                                this.journalSystem.categories.LORE,
                                { character: 'Ortolan', related: 'The Infinite Loop' }
                            );
                        }
                        if (this.questSystem?.getQuest('who_killed_bishop')) {
                            this.questSystem.updateQuest(
                                'who_killed_bishop',
                                'Ortolan (now on Burning Bear Street) says the Infinite Loop was an unfinished game he built with Dr. Elphi, shut down by the city\'s rulers as too dangerous. A master build is likely still sealed in the cellar under the Scraper — their old lab.' + (helped ? ' He also told me how to free a trapped mind: find the game\'s hidden "losing move."' : ' He wouldn\'t say more.') + ' I should search the Scraper cellar.',
                                'ortolan_infinite_loop_revealed'
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
        // Once Dr. Elphi has sent the player about the Infinite Loop, Ortolan has
        // relocated here from Shed 521.
        if (this.hasJournalEntry('infinite_loop_ortolan_lead')) {
            this.createOrtolan();
        }
    }

    createOrtolan() {
        const x = 250, groundY = 500;
        this.ortolan = this.add.sprite(x, groundY, 'ortolan').setOrigin(0.5, 1).setScale(0.15).setDepth(6);
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
                'Dr. Elphi pointed me to Ortolan about the Infinite Loop. He has moved from the Shed to Burning Bear Street, buried as ever in permit paperwork.',
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
