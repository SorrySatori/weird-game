import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class ScraperAmbraScene extends GameScene {
    constructor() {
        super({ key: 'ScraperAmbraScene' });
        this.isTransitioning = false; // Add flag to track transition state
    }

    preload() {
        super.preload();
        this.load.image('scraperAmbraBg', 'assets/images/backgrounds/ScraperAmbra.png');
        this.load.image('drElphi', 'assets/images/characters/DrElphi.png');
        
        // Make sure sounds are loaded
        if (!this.sound.get('click')) {
            this.load.audio('click', 'assets/audio/click.mp3');
        }
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        this.playSceneMusic('dr_elphi_theme');

        // Set background
        const bg = this.add.image(400, 300, 'scraperAmbraBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Add fade-in effect
        this.cameras.main.fadeIn(1200, 0, 0, 0);
        
        // Position the priest at the center when entering this scene
        this.priest.x = 400;
        this.priest.y = 450; // Position on the ground
        
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
            300 // walk to y
        );
        
        // Add a hint about the exit
        const exitHint = this.add.text(400, 520, 'Back to Elevator', {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        exitHint.setOrigin(0.5);
        exitHint.setAlpha(0);
        exitHint.setDepth(10);
        
        // Show hint when hovering near the exit
        this.input.on('pointermove', (pointer) => {
            // Check if pointer is near the exit area
            if (Math.abs(pointer.x - 400) < 100 && Math.abs(pointer.y - 550) < 50) {
                exitHint.setAlpha(1);
            } else {
                exitHint.setAlpha(0);
            }
        });
        
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
        
        // Show a welcome notification
        this.time.delayedCall(1000, () => {
            this.showNotification('Floor 177-Quiet: Dr. Elphi\'s Studio', 0x7fff8e);
        });
    }
    
    /**
     * Create ambient elements for the scene
     */
    createAmbientElements() {
        // Add some floating spores/particles
        for (let i = 0; i < 30; i++) {
            const x = Math.random() * 800;
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
        ambientGlow.fillRect(0, 0, 800, 600);
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
    
    get dialogContent() {
        return {
            ...super.dialogContent,
            speaker: 'Dr. Elphi',
            
            elphi_studio_intro: {
                text: "Dr. Elphi's studio is eerily quiet. Workstations with glowing screens line the walls, each displaying fragments of code and strange designs. The air feels charged with creative energy, but there's no sign of Dr. Elphi herself.",
                options: [
                    { text: "Continue exploring", next: "closeDialog" }
                ]
            },
            
            // Dr. Elphi Quarn dialog tree
            dr_elphi_start: {
                text: "Hm. You're not scheduled. Not tagged either. Let me guess — someone wants a neural tuning, a performance consultation, or you've come to warn me about 'metaphysical leakage' again.",
                options: [
                    { text: "I'm looking for someone. The Bishop.", next: "dr_elphi_bishop_path" },
                    { text: "I was sent to investigate an anomaly. Might be connected to this place.", next: "dr_elphi_anomaly_path" },
                    { text: "I heard you design dream-based games.", next: "dr_elphi_games_path" },
                    { text: "I'll explain if you stop testing me.", next: "dr_elphi_testing_path" }
                ],
                onTrigger: () => {
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && questSystem.getQuest('level_177_access') && !questSystem.getQuest('level_177_access').isComplete) {
                        questSystem.completeQuest('level_177_access');
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
                text: "The Bishop? Well, you're late. She came here. Often, actually. Always for simulations. Never politics.\n\nShe liked the softer ones. Immersive fictions, drift environments. The Cardinal Feast was a favorite.\n\nLast I saw her? Three days ago, maybe four. She ended her session, said she might stay outside awhile. She had a key to the backyard.\n\nI didn't think much of it. She seemed… distracted. More than usual.",
                options: [
                    { text: "What's in the backyard?", next: "dr_elphi_backyard_info" },
                    { text: "Did she say where she was going?", next: "dr_elphi_bishop_destination" },
                    { text: "I'll go look for her there.", next: "dr_elphi_exit" }
                ],
                onTrigger: () => {
                    // Update the find_bishop quest to direct to Shard backyard
                    const questSystem = this.registry.get('questSystem');
                    const findBishopQuest = questSystem?.getQuest('find_bishop');
                    if (findBishopQuest && !findBishopQuest.isComplete) {
                        questSystem.updateQuest('find_bishop', 'Dr. Elphi mentioned the Bishop was last seen in the Shard backyard. I should check there next.', 'check_shard_backyard');
                    }
                }
            },
            
            dr_elphi_anomaly_path: {
                text: "If there's an anomaly, it isn't from me. All test environments are sandboxed. At worst, they collapse privately.\n\nUnless you mean her. The Bishop ran a few sessions recently. She didn't say what she was avoiding, but something had her on edge.\n\nShe had a habit of sitting out back after play — the old transit yard. She hasn't come in days.\n\nHere.",
                options: [
                    { text: "What was she avoiding?", next: "dr_elphi_bishop_concerns" },
                    { text: "What's in the backyard?", next: "dr_elphi_backyard_info" },
                    { text: "I'll investigate the backyard.", next: "dr_elphi_exit" }
                ],
                onTrigger: () => {
                    // Update the find_bishop quest to direct to Shard backyard
                    const questSystem = this.registry.get('questSystem');
                    const findBishopQuest = questSystem?.getQuest('find_bishop');
                    if (findBishopQuest && !findBishopQuest.isComplete) {
                        questSystem.updateQuest('find_bishop', 'Dr. Elphi mentioned the Bishop was last seen in the Shard backyard. I should check there next.', 'check_shard_backyard');
                    }
                }
            },
            
            dr_elphi_games_path: {
                text: "I make them. Dream architecture. Neurofiction. Post-sensory architecture.\n\nYou're standing in ARB Ambra — and no, the initials don't stand for anything. They just sound better that way.\n\nWhat did you hear exactly?",
                options: [
                    { text: "The Bishop came here to play.", next: "dr_elphi_bishop_path" },
                    { text: "Something went wrong. I'm following the trace.", next: "dr_elphi_anomaly_path" },
                    { text: "Never mind.", next: "dr_elphi_exit" }
                ]
            },
            
            dr_elphi_testing_path: {
                text: "Testing is how I stay alive. Most visitors lie. Some of them don't even know it.\n\nBut fine. Speak clearly. This floor costs me processing cycles.",
                options: [
                    { text: "I'm looking for the Bishop.", next: "dr_elphi_bishop_path" },
                    { text: "There's been a signal anomaly.", next: "dr_elphi_anomaly_path" }
                ]
            },
            
            dr_elphi_bishop_destination: {
                text: "No. She never does. The Bishop moves in patterns only she understands. But she always returns to the Cathedral eventually.\n\nThis time feels different though. She was... preoccupied with something in the old transit yard. Said the moss there was 'singing' to her. Typical Cathedral mysticism.",
                options: [
                    { text: "I'll go look for her there.", next: "dr_elphi_exit" },
                    { text: "What's in the backyard?", next: "dr_elphi_backyard_info" }
                ]
            },
            
            dr_elphi_bishop_concerns: {
                text: "She wouldn't say directly. Something about 'resonance patterns' and 'harmonic disturbances.' Cathedral business, I assumed.\n\nBut she spent more time in the simulations than usual. Almost like she was hiding. Or preparing for something.",
                options: [
                    { text: "I should check the backyard.", next: "dr_elphi_exit" },
                    { text: "Tell me about this backyard.", next: "dr_elphi_backyard_info" }
                ]
            },
            
            dr_elphi_backyard_info: {
                text: "It's an old transit yard. Abandoned decades ago when the new lines were built. Now it's mostly overgrown with that peculiar moss.\n\nThe Bishop seemed fascinated by it. Said it had 'mnemonic properties.' Whatever that means. Cathedral folk and their cryptic terminology...",
                options: [
                    { text: "I'll go investigate.", next: "dr_elphi_exit" },
                    { text: "Is it dangerous?", next: "dr_elphi_backyard_danger" }
                ]
            },
            
            dr_elphi_backyard_danger: {
                text: "Not conventionally. But nothing around is truly safe, is it? The moss remembers things. Sometimes it... shares those memories. Unpredictably.\n\nJust don't fall asleep out there. The dreams can be... intense.",
                options: [
                    { text: "I'll be careful.", next: "dr_elphi_exit" }
                ]
            },
            
            dr_elphi_exit: {
                text: "I'm not hiding anything. If something happened to her, I didn't see it.\n\nBut you might.\n\nCome back if you find something. Here, take my key to the backyard.",
                options: [
                    { text: "I'll check the backyard.", next: "closeDialog" },
                    { text: "Thanks for the information.", next: "closeDialog" }
                ],
                onTrigger: () => {
                    this.addItemToInventory({
                        id: 'scraper_backyard_key',
                        name: "Backyard Key",
                        description: "A key to the Scraper 1140 backyard. It seems to glow faintly with possibility.",
                        stackable: false
                    });
                    // Show a notification about the updated quest
                    this.time.delayedCall(500, () => {
                        this.showNotification('Quest Updated: Find the Bishop', 0x7fff8e);
                    });
                }
            }
        };
    }
    
    /**
     * Creates the Dr. Elphi Quarn NPC with animations and interactions
     */
    createDrElphi() {
        // Create Dr. Elphi sprite at a more visible position
        this.drElphi = this.add.sprite(600, 350, 'drElphi');
        
        // Set scale to match the priest character (priest is at scale 2.0)
        this.drElphi.setScale(0.1); // Reduced scale to match priest proportions
        this.drElphi.setDepth(5);
        
        // Log to console for debugging
        console.log('Creating Dr. Elphi at position:', this.drElphi.x, this.drElphi.y);
        
        // Add name tag
        const nameTag = this.add.text(this.drElphi.x, this.drElphi.y + 30, 'Dr. Elphi Quarn', {
            fontSize: '14px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 5, y: 2 }
        });
        nameTag.setOrigin(0.5);
        nameTag.setDepth(5);
        
        // Add a subtle glow effect
        const glow = this.add.graphics();
        glow.fillStyle(0x7fff8e, 0.15);
        glow.fillCircle(this.drElphi.x, this.drElphi.y, 40);
        glow.setDepth(4);
        
        // Add pulsating effect to the glow
        this.tweens.add({
            targets: glow,
            alpha: { from: 0.15, to: 0.25 },
            duration: 2000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Add subtle movement animations
        this.tweens.add({
            targets: this.drElphi,
            y: this.drElphi.y - 5,
            duration: 2500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Random head movements
        this.time.addEvent({
            delay: 3000,
            callback: () => {
                // Random slight rotation
                const randomAngle = (Math.random() * 6) - 3;
                this.tweens.add({
                    targets: this.drElphi,
                    angle: randomAngle,
                    duration: 1000,
                    ease: 'Sine.easeInOut',
                    yoyo: true
                });
            },
            callbackScope: this,
            loop: true
        });
        
        // Create a much larger hit area for better clickability
        // Using a container to expand the interactive area
        const drElphiContainer = this.add.container(this.drElphi.x, this.drElphi.y);
        
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
            this.drElphi.setScale(0.11); // Slightly larger on hover
            nameTag.setFontSize('16px');
            document.body.style.cursor = 'pointer';
        });
        
        drElphiContainer.on('pointerout', () => {
            this.drElphi.setScale(0.1); // Back to normal size
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
            this.showNotification('Dr. Elphi is working at her console');
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
