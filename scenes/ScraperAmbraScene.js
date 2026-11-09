import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import LanguageSystem from '../systems/LanguageSystem.js';
import { isDemoClosed, sayDemoClosed, showDemoEnd } from '../utils/demo.js';

export default class ScraperAmbraScene extends GameScene {
    constructor() {
        super({ key: 'ScraperAmbraScene' });
        this.isTransitioning = false; // Add flag to track transition state
    }

    preload() {
        super.preload();
        this.load.image('scraperAmbraBg', 'assets/images/backgrounds/ScraperAmbra.png');
        this.load.spritesheet('drElphiIdle', 'assets/images/characters/elphi_idle.png', { frameWidth: 128, frameHeight: 160 });

        // Make sure sounds are loaded
        if (!this.sound.get('click')) {
            this.load.audio('click', 'assets/sounds/click.mp3');
        }
    }

    create() {
        this.demoEndPending = false;
        // Call parent create first to initialize mechanics
        super.create();
        this.playSceneMusic('dr_elphi_theme');

        // Set background (native 1067×600: tools/artgen/ambra_bg.py — the loft studio on floor 177-Quiet)
        const bg = this.add.image(this.scale.width / 2, 300, 'scraperAmbraBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        // The background paints the studio floor; drop the generic ground strip
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Add fade-in effect
        this.cameras.main.fadeIn(1200, 0, 0, 0);

        // Position the priest on the walk line (feet on y 534), just left of the rug
        this.priest.x = 430;
        this.priest.y = 470;
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }
        
        // Create exit back to Scraper Interior
        this.transitionManager.createTransitionZone(
            400, // x position
            550, // y position
            200, // width
            50, // height
            'down', // direction
            'ScraperInteriorScene', // target scene
            400, // walk to x
            300, // walk to y
            'Back to Elevator' // the exit's own hover label (a second hint here doubled it)
        );
        
        // Add ambient elements
        this.createAmbientElements();
        
        // Add Dr. Elphi Quarn NPC
        this.createDrElphi();
        
        // Update the find_bishop quest if it exists and is not complete
        const questSystem = this.registry.get('questSystem');
        const findBishopQuest = questSystem?.getQuest('find_bishop');
        if (findBishopQuest && !findBishopQuest.isComplete) {
            questSystem.updateQuest('find_bishop', 'I\'ve reached Dr. Elphi\'s studio on floor 177-Quiet. Now I need to find clues about the Bishop.', 'reached_elphi_studio');
        }
        // Getting up here is what level_177_access was about -- done on arrival, not when Elphi is spoken to
        const accessQuest = questSystem?.getQuest('level_177_access');
        if (accessQuest && !accessQuest.isComplete) {
            questSystem.updateQuest('level_177_access', "The Lift-Mother took me up. I'm on floor 177-Quiet.", 'arrived');
            questSystem.completeQuest('level_177_access');
        }
        
        // Show a welcome notification
        this.time.delayedCall(1000, () => {
            this.showNotification(this.t('scraperAmbra.arrival'), 0x7fff8e);
        });
    }
    
    /**
     * Create ambient elements for the scene
     */
    createAmbientElements() {
        // Add some floating spores/particles
        for (let i = 0; i < 30; i++) {
            const x = Math.random() * this.scale.width;
            const y = Math.random() * 400 + 100;
            const size = Math.random() * 3 + 1;
            
            const particle = this.add.circle(x, y, size, 0x7fff8e, 0.4);
            particle.setDepth(3);
            
            // Add floating movement
            this.tweens.add({
                targets: particle,
                x: x + (Math.random() * 100 - 50),
                y: y + (Math.random() * 60 - 30),
                alpha: { from: 0.4, to: 0.1 },
                duration: 3000 + Math.random() * 2000,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
        }
        
        // Add a subtle green glow effect to the scene
        const ambientGlow = this.add.graphics();
        ambientGlow.fillStyle(0x7fff8e, 0.05);
        ambientGlow.fillRect(0, 0, this.scale.width, this.scale.height);
        ambientGlow.setDepth(2);
        
        // Add pulsating effect to the glow
        this.tweens.add({
            targets: ambientGlow,
            alpha: { from: 0.05, to: 0.1 },
            duration: 4000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
    }
    
    /** The demo's main line ends with this talk: the end card follows once the dialog closes (any way it closes). */
    hideDialog() {
        super.hideDialog();
        if (!this.demoEndPending) return;
        this.demoEndPending = false;
        showDemoEnd(this);
    }

    /** Elphi's backyard key + the quest pointer (both exit lines; idempotent). */
    giveBackyardLead() {
        this.demoEndPending = true;
        // Key only once (re-opening the exit used to push a duplicate), and make sure the quest points
        // to the backyard even when the player got here via "Never mind" without the Bishop/anomaly branch.
        if (!this.hasItem('scraper_backyard_key')) {
            this.addItemToInventory({
                id: 'scraper_backyard_key',
                name: "Backyard Key",
                description: "A key to the Scraper 1140 backyard. It seems to glow faintly.",
                stackable: false
            });
        }
        const questSystem = this.registry.get('questSystem');
        const findBishopQuest = questSystem?.getQuest('find_bishop');
        if (findBishopQuest && !findBishopQuest.isComplete && !findBishopQuest.updates.some(u => u.key === 'check_shard_backyard')) {
            questSystem.updateQuest('find_bishop', 'Dr. Elphi pointed me to the Scraper backyard. I should look for the Bishop there.', 'check_shard_backyard');
        }
    }

    get dialogContent() {
        // She has already told about the Bishop and handed over the backyard key: the first-visit openers
        // ("I'm looking for the Bishop", the anomaly, "stop guessing") would only loop back to that talk.
        const backyardLead = !!this.questSystem?.getQuest('find_bishop')?.updates?.some(u => u.key === 'check_shard_backyard')
            || !!this.hasItem('scraper_backyard_key');

        return {
            ...super.dialogContent,
            speaker: 'Dr. Elphi',

            
            // Dr. Elphi Quarn dialog tree
            dr_elphi_start: {
                // textKey lets the CZ file pick the matching variant (the old lookup matched on the EN text itself).
                textKey: backyardLead ? 'lead_given' : 'default',
                text: backyardLead
                    ? "Back already? The backyard hasn't gone anywhere. Or did you come to stare at my helmets?"
                    : "Hm. You're not scheduled. Not tagged either. Let me guess: someone wants a neural tuning, a performance consultation, or you've come to warn me about 'metaphysical leakage' again.",
                options: [
                    ...(!backyardLead ? [
                        { text: "I'm looking for someone. The Bishop.", key: 'im_looking_for_someone_the_bishop', next: "dr_elphi_bishop_path" },
                        { text: "I was sent to investigate an anomaly. Might be connected to this place.", key: 'i_was_sent_to_investigate_an_anomaly_might_be_conn', next: "dr_elphi_anomaly_path" },
                        { text: "I heard you design dream-based games.", key: 'i_heard_you_design_dreambased_games', next: "dr_elphi_games_path" },
                        { text: "I'll explain if you stop guessing.", key: 'ill_explain_if_you_stop_testing_me', next: "dr_elphi_testing_path" }
                    ] : [
                        { text: "I heard you design dream-based games.", key: 'i_heard_you_design_dreambased_games', next: "dr_elphi_games_path" }
                    ]),
                    // small talk, any time
                    { text: "What are you working on now?", key: 'what_are_you_working_on_now', next: "dr_elphi_work_skyship" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('met_dr_elphi')) {
                        this.addJournalEntry(
                            'met_dr_elphi',
                            'Dr. Elphi Quarn',
                            "Dr. Elphi Quarn works alone on floor 177-Quiet of the Scraper, in a studio called ARB Ambra, where she makes dream games. Smart, cautious, and outspoken.",
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Dr. Elphi Quarn', location: 'ARB Ambra' }
                        );
                    }
                    // Trigger any animations or effects when dialog starts
                    if (this.drElphi) {
                        this.tweens.add({
                            targets: this.drElphi,
                            y: this.drElphi.y - 10,
                            duration: 300,
                            yoyo: true,
                            ease: 'Sine.easeOut'
                        });
                    }
                }
            },
            
            dr_elphi_bishop_path: {
                text: "The Bishop? Well, you're late. She came here. Often, actually. Always for simulations. Never politics.\n\nShe preferred narrative-based games. Immersive fictions, drift environments. The Cardinal Feast was a favorite.\n\nLast I saw her? Three digestions ago, maybe four. She ended her session, said she might stay outside awhile. She had a key to the backyard.\n\nI didn't think much of it. She seemed… distracted. More than usual.",
                options: [
                    { text: "What's in the backyard?", key: 'whats_in_the_backyard', next: "dr_elphi_backyard_info" },
                    { text: "Did she say where she was going?", key: 'did_she_say_where_she_was_going', next: "dr_elphi_bishop_destination" },
                    { text: "I'll go look for her there.", key: 'ill_go_look_for_her_there', next: "dr_elphi_exit" }
                ],
                onTrigger: () => {
                    this.addJournalFact('met_dr_elphi', 'bishop_visits', "The Bishop came to her often, always to play, never for politics.");
                    // Update the find_bishop quest to direct to the Scraper backyard
                    // (route-neutral: the same key is also written by dr_elphi_exit, which "Never mind" reaches without this state)
                    const questSystem = this.registry.get('questSystem');
                    const findBishopQuest = questSystem?.getQuest('find_bishop');
                    if (findBishopQuest && !findBishopQuest.isComplete) {
                        questSystem.updateQuest('find_bishop', 'Dr. Elphi pointed me to the Scraper backyard. I should look for the Bishop there.', 'check_shard_backyard');
                    }
                }
            },
            
            dr_elphi_anomaly_path: {
                text: "If this is some kind of anomaly, I have nothing to do with it. All test environments are well secured. In the worst-case scenario, it won't disrupt anything around it.",
                options: [
                    { text: "I'm looking for the Bishop.", key: 'im_looking_for_the_bishop', next: "dr_elphi_bishop_path" },
                    { text: "The Bishop came here to play.", key: 'the_bishop_came_here_to_play', next: "dr_elphi_bishop_path" }
                ]
            },
            
            dr_elphi_games_path: {
                text: "I make them. Dream architecture. Neurofiction. Post-sensory architecture.\n\nYou're standing in ARB Ambra. And no, the initials don't stand for anything. They just sound better that way.\n\nWhat did you hear exactly?",
                options: backyardLead
                    ? [{ text: "Ask something else.", key: 'ask_something_else_games', next: "dr_elphi_start" }]
                    : [
                        { text: "The Bishop came here to play.", key: 'the_bishop_came_here_to_play', next: "dr_elphi_bishop_path" },
                        { text: "Something went wrong. I'm following the trace.", key: 'something_went_wrong_im_following_the_trace', next: "dr_elphi_anomaly_path" },
                        { text: "Never mind.", key: 'never_mind', next: "dr_elphi_exit_brief" }
                    ],
                onTrigger: () => {
                    this.addJournalFact('met_dr_elphi', 'dreams', "She designs dreams: neurofiction, dream architecture.");
                }
            },
            
            dr_elphi_testing_path: {
                text: "Guessing and experimenting is how I stay alive. Most visitors lie. Some of them don't even know it.\\n\\nBut fine. Speak clearly. What do you want?",
                options: [
                    { text: "I'm looking for the Bishop.", key: 'im_looking_for_the_bishop', next: "dr_elphi_bishop_path" },
                    { text: "There's been a signal anomaly. A distress call.", key: 'theres_been_a_signal_anomaly', next: "dr_elphi_anomaly_path" }
                ]
            },
            
            dr_elphi_work_skyship: {
                text: "*She rubs her temples.* A skyship. A colossal one, for a new game. I split my imaginators into teams: some do the interiors, some the ship itself and how it flies, some the people on board, their dialogs and quests. Simple. Nothing goes according to the brief.\n\nDolores Políčková has the main design concept. A retro-futurist airship: brass, glass, elegance. And every time she dreams it, there's a giant hen in it. She can't get rid of it. It's in every draft.",
                options: [
                    { text: "A giant hen?", key: 'a_giant_hen', next: "dr_elphi_work_captain" }
                ]
            },
            dr_elphi_work_captain: {
                text: "That's the least of it. Zachariáš Cvak had the captain almost finished. Captain Mervyn, dialogs and all. Then Mervyn got stuck in a loop and started rambling about some conspiracy of cabbages. Cvak keeps cleaning up his dialogs and steering him back on course. The cabbages keep coming back. And conspiring.",
                options: [
                    { text: "And the interiors?", key: 'and_the_interiors', next: "dr_elphi_work_mox" }
                ]
            },
            dr_elphi_work_mox: {
                text: "Some of them are Mox Igrixee's. Mox only fully exists in this dimension in odd weeks. Exactly the psychedelic energy I promised the journalists. Unfortunately, Mox recently discovered chocolate. Now it keeps breaking through into the dream: bulkheads, fittings, furniture. Some of it even takes the shape of living creatures.\n\nToday a pack of chocolate cats ran across the deck and started playing with the cabbages, and the captain crashed into the hen. *She sighs.* So I called it a day.",
                options: [
                    { text: "Good luck with the hen.", key: 'good_luck_with_the_hen', next: "dr_elphi_start" }
                ],
                onTrigger: () => {
                    this.addJournalFact('met_dr_elphi', 'skyship_game', "She's building a colossal skyship for a new game, but her imaginators keep dreaming in a giant hen, conspiring cabbages and chocolate cats.");
                }
            },

            dr_elphi_bishop_destination: {
                text: "No. She never does. The Bishop moves in patterns only she understands. But she always returns to the Cathedral eventually.\\n\\nThis time, though, I have a feeling that something has changed. She was... going out to the yard often, as if something there had caught her attention. When I asked her about it, she sounded evasive.",
                options: [
                    { text: "What was she avoiding?", key: 'what_was_she_avoiding', next: "dr_elphi_bishop_concerns" },
                    { text: "I'll go look for her there.", key: 'ill_go_look_for_her_there', next: "dr_elphi_exit" },
                    { text: "What's in the backyard?", key: 'whats_in_the_backyard', next: "dr_elphi_backyard_info" }
                ]
            },
            
            dr_elphi_bishop_concerns: {
                text: "She wouldn't say directly. Something about 'resonance patterns' and 'harmonic disturbances.' Cathedral business, I assumed.\n\nBut she spent more time in the simulations than usual. Almost like she was hiding. Or preparing for something.",
                options: [
                    { text: "I should check the backyard.", key: 'i_should_check_the_backyard', next: "dr_elphi_exit" },
                    { text: "Tell me about this backyard.", key: 'tell_me_about_this_backyard', next: "dr_elphi_backyard_info" }
                ]
            },
            
            dr_elphi_backyard_info: {
                text: "It's an old transit yard. Abandoned decades ago when the new lines were built. Now it's mostly overgrown with that peculiar moss.\n\nThe Bishop seemed fascinated by it. Said it had 'mnemonic properties.' Whatever that means. You know, your folk and their cryptic terminology...",
                options: [
                    { text: "I'll go investigate.", key: 'ill_go_investigate', next: "dr_elphi_exit" },
                    { text: "Is it dangerous?", key: 'is_it_dangerous', next: "dr_elphi_backyard_danger" }
                ]
            },
            
            dr_elphi_backyard_danger: {
                text: "Not conventionally. But nothing around is truly safe, is it?\n\nJust don't fall asleep there. Apparently, people have dreams that are way too intense there.",
                options: [
                    { text: "I'll be careful.", key: 'ill_be_careful', next: "dr_elphi_exit" }
                ]
            },
            
            dr_elphi_exit: {
                text: "I'm not hiding anything. If something happened to her, I didn't see it.\n\nBut you might.\n\nCome back if you find something. Here, take my key to the backyard.",
                options: [
                    { text: "I'll check the backyard.", key: 'ill_check_the_backyard', next: "closeDialog" },
                    { text: "Thanks for the information.", key: 'thanks_for_the_information', next: "closeDialog" }
                ],
                onTrigger: () => this.giveBackyardLead()
            },
            // "Never mind" before she ever talked about the Bishop: no "if something happened to her"
            dr_elphi_exit_brief: {
                text: "Suit yourself. If you're going to poke around anyway, poke around somewhere useful: the backyard. Here, take my key.\n\nCome back if you find something.",
                options: [
                    { text: "I'll check the backyard.", key: 'ill_check_the_backyard', next: "closeDialog" },
                    { text: "Thanks.", key: 'thanks_brief', next: "closeDialog" }
                ],
                onTrigger: () => this.giveBackyardLead()
            },

        };
    }

    /**
     * Creates the Dr. Elphi Quarn NPC with animations and interactions
     */
    createDrElphi() {
        // She stands on the floor in front of her desk (world (12, 0, 17) in ambra_bg.py), feet anchored
        // tools/artgen/elphi.py (rig.py redraw): 8 idle frames of 128×160 at scale 1 (soles on y 510)
        if (!this.anims.exists('elphi_idle')) {
            // breath (the hologram bobs), the goggles glint (a blink), the hologram pulses and drifts, she glances at it,
            // a tap on the device in her hand (the glyph answers), a lock of hair stirs
            this.anims.create({ key: 'elphi_idle', frames: this.anims.generateFrameNumbers('drElphiIdle', { frames: [0, 0, 1, 1, 0, 0, 3, 3, 4, 4, 0, 0, 2, 0, 0, 1, 1, 0, 5, 5, 0, 0, 6, 0, 6, 0, 0, 3, 4, 4, 0, 7, 7, 0, 0, 0] }), frameRate: 4, repeat: -1 });
        }
        this._elphiHoverFx = null; // the scene instance is reused
        this.drElphi = this.add.sprite(745, 514, 'drElphiIdle', 0);
        this.drElphi.setOrigin(0.5, 1);
        this.drElphi.setDepth(6);
        this.drElphi.play('elphi_idle');
        this.addGroundShadow(this.drElphi.x, this.drElphi.y - 7, 52, 14);
        // dialog portrait: a 2x bust of the idle sheet (the speaker is 'Dr. Elphi' in both languages)
        const elphiBust = { key: 'drElphiIdle', frame: 0, zoom: 2, top: 10 };
        this.dialogPortraits = { ...(this.dialogPortraits || {}), 'Dr. Elphi': elphiBust, 'Dr. Elphi Quarn': elphiBust };
        const midY = this.drElphi.y - this.drElphi.displayHeight / 2;

        // Add name tag above her head
        const nameTag = this.add.text(this.drElphi.x, this.drElphi.y - 4 - 144 - 12, 'Dr. Elphi Quarn', {   // over her curls (the figure is 144 px)
            fontSize: '14px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 5, y: 2 }
        });
        nameTag.setOrigin(0.5);
        nameTag.setDepth(5);
        
        // (her idle is the frame animation above -- no glow disc, bobbing or tilting tweens on the pixel art)
        
        // Create a much larger hit area for better clickability
        // Using a container to expand the interactive area
        const drElphiContainer = this.add.container(this.drElphi.x, midY);
        
        // Create a transparent rectangle for the hit area
        const hitAreaGraphic = this.add.graphics();
        hitAreaGraphic.fillStyle(0xffffff, 0.0); // Completely transparent
        hitAreaGraphic.fillRect(-60, -80, 120, 160); // Much larger hit area
        
        // Add the hit area to the container
        drElphiContainer.add(hitAreaGraphic);
        
        // Make the container interactive
        drElphiContainer.setSize(120, 160);
        drElphiContainer.setInteractive();
        
        // Hover effect
        drElphiContainer.on('pointerover', () => {
            // a soft green outline glow instead of scaling (scaling smears the pixel art); WebGL only, harmless otherwise
            if (!this._elphiHoverFx) this._elphiHoverFx = this.drElphi.preFX?.addGlow(0x7fff8e, 2, 0, false, 0.1, 8);
            nameTag.setFontSize('16px');
            document.body.style.cursor = 'pointer';
        });
        
        drElphiContainer.on('pointerout', () => {
            if (this._elphiHoverFx) { this.drElphi.preFX?.remove(this._elphiHoverFx); this._elphiHoverFx = null; }
            nameTag.setFontSize('14px');
            document.body.style.cursor = 'default';
        });
        
        // Click to start dialog
        drElphiContainer.on('pointerdown', () => {
            console.log('Dr. Elphi clicked!'); // Debug log
            
            // Play a sound effect if available
            if (this.sound.get('click')) {
                this.sound.play('click', { volume: 0.5 });
            }
            
            // Show dialog
            this.showDialog('dr_elphi_start');
        });
        
        // Add a notification to indicate Dr. Elphi is present
        this.time.delayedCall(1500, () => {
            this.showNotification(this.t('scraperAmbra.elphiPresent'));
        });
    }

    shutdown() {
        // Clean up resources
        this.restoreBackgroundMusic();
        this.sceneMusic = null;
        super.shutdown();
    }
    
    update() {
        // Call parent update for all standard mechanics
        super.update();
    }
}
