import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';

export default class CrossroadScene extends GameScene {
    constructor() {
        super({ key: 'CrossroadScene' });
        this.isTransitioning = false;
        // Use the persisted symbiont system
        this.symbiontSystem = null; // Will be set in create from registry
        this.journalSystem = JournalSystem.getInstance();
    }

    preload() {
        super.preload();
        this.load.image('crossroadBg', 'assets/images/backgrounds/crossroad.png');
        this.load.image('crossroadBg_growth', 'assets/images/backgrounds/crossroad_growth.png');
        this.load.image('door', 'assets/images/ui/door.png');
        this.load.image('skyship', 'assets/images/backgrounds/skyship.png');
    }

    create() {
        super.create();

        // Check if growth has happened
        this.hasGrowth = this.registry.get('crossroadGrowth') || false;
        
        // Initialize the journal system
        this.journalSystem = JournalSystem.getInstance();
        
        const bgKey = this.hasGrowth ? 'crossroadBg_growth' : 'crossroadBg';
        this.background = this.add.image(400, 300, bgKey);
        this.background.setDisplaySize(800, 600);
        this.background.setDepth(-1);
        this.playSceneMusic('genericMusic');

        // Create symbiont UI
        this.createSymbiontUI();
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);

        if (!this.hasGrowth) {
            this.corpse = this.add.image(400, 300, 'door');
            this.corpse.setDisplaySize(120, 200);
            this.corpse.setAlpha(0.01);
            this.corpse.setInteractive({ useHandCursor: true });
            this.corpse.on('pointerdown', () => this.showCorpseDialog());
        } else {
            // Add skyship transition area when growth is present
            this.skyshipTransition = this.add.image(400, 200, 'door')
                .setDisplaySize(100, 150)
                .setAlpha(0.01)
                .setInteractive({ useHandCursor: true });
            this.skyshipTransition.setDepth(10);
            
            // Add a subtle glow effect to hint at the interactive area
            const skyshipGlow = this.add.graphics();
            skyshipGlow.fillStyle(0x7fff8e, 0.2);
            skyshipGlow.fillCircle(400, 200, 50);
            skyshipGlow.setDepth(9);
            
            // Add pulsating animation to the glow
            this.tweens.add({
                targets: skyshipGlow,
                alpha: { from: 0.2, to: 0.4 },
                duration: 1500,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
        }

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);

        // Setup scene transitions using the transition manager
        this.setupSceneTransitions();
        
        // Setup skyship transition separately
        this.setupSkyshipTransition();

        // Load persisted symbiont system
        this.symbiontSystem = this.registry.get('symbiontSystem');
        
        // Add registry change listener to update the scene when growth state changes
        this.registry.events.on('changedata', this.handleRegistryChange, this);
        
        // For testing: manually trigger the registry change handler if growth is already true
        if (this.hasGrowth) {
            this.handleRegistryChange(this.registry, 'crossroadGrowth', true);
        }
        
        // Clean up event listener when scene is shut down
        this.events.on('shutdown', () => {
            this.registry.events.off('changedata', this.handleRegistryChange, this);
        });
    }

    setupSceneTransitions() {
        // Create transition zone for Shed521 entrance
        this.transitionManager.createTransitionZone(
            100, // x position
            400, // y position
            120, // width
            200, // height
            'left', // direction
            'Shed521Scene', // target scene
            100, // walk to x
            400 // walk to y
        );
        
        // Create transition zone for Cathedral entrance
        this.transitionManager.createTransitionZone(
            200, // x position
            500, // y position
            100, // width
            200, // height
            'left', // direction
            'EggCatedralScene', // target scene
            200, // walk to x
            500 // walk to y
        );
        
        // Create transition zone for VoxMarket entrance
        this.transitionManager.createTransitionZone(
            650, // x position
            400, // y position
            100, // width
            200, // height
            'right', // direction
            'VoxMarket', // target scene
            650, // walk to x
            470 // walk to y
        );
        
        // Create transition zone for ScraperScene entrance
        this.transitionManager.createTransitionZone(
            750, // x position
            470, // y position
            40, // width
            200, // height
            'right', // direction
            'ScraperScene', // target scene
            750, // walk to x
            470 // walk to y
        );
        
        // Setup the transition for the skyship area if it exists
        if (this.hasGrowth && this.skyshipTransition) {
            this.setupSkyshipTransition();
        }
    }

    setupSkyshipTransition() {
        // Create transition zone for Skyship using the transition manager
        this.transitionManager.createTransitionZone(
            400, // x position
            200, // y position
            100, // width
            150, // height
            'up', // direction
            'SkyshipScene', // target scene
            400, // walk to x
            200 // walk to y
        );
        
        // Add a subtle glow effect to hint at the interactive area
        const skyshipGlow = this.add.graphics();
        skyshipGlow.fillStyle(0x7fff8e, 0.2);
        skyshipGlow.fillCircle(400, 200, 50);
        skyshipGlow.setDepth(9);
        
        // Add pulsating animation to the glow
        this.tweens.add({
            targets: skyshipGlow,
            alpha: { from: 0.2, to: 0.4 },
            duration: 1500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
    }

    createSymbiontUI() {
        const startX = 60;
        const startY = 480;
        const spacing = 40;
        const slotSize = 30;

        // Create container for slots
        this.symbiontContainer = this.add.container(0, 0);
        this.symbiontContainer.setDepth(100);
        this.symbiontContainer.setScrollFactor(0);

        this.symbiontSlots = [];
        this.symbiontIcons = new Map();

        for (let i = 0; i < this.symbiontSystem.maxSlots; i++) {
            // Create slot background
            const slot = this.add.rectangle(startX + (i * spacing), startY, slotSize, slotSize, 0x1a3b23)
                .setStrokeStyle(1, 0x7fff8e)
                .setDepth(100)
                .setAlpha(i < this.symbiontSystem.unlockedSlots ? 1 : 0.3);

            this.symbiontSlots.push(slot);
            this.symbiontContainer.add(slot);

            if (i >= this.symbiontSystem.unlockedSlots) {
                const lockText = this.add.text(slot.x, slot.y, '', {
                    fontSize: '16px',
                    color: '#7fff8e'
                }).setOrigin(0.5).setDepth(101);
                this.symbiontContainer.add(lockText);
            }
        }

        // Restore any existing symbionts
        if (this.symbiontSystem) {
            this.symbiontSystem.symbionts.forEach((data, id) => {
                this.addSymbiontIcon(id, data);
            });
        }
    }

    get dialogContent() {
        return {
            ...super.dialogContent,
            speaker: 'Giant Corpse',
            corpseMain: {
                text: `You find a strange, gigantic corpse. Its flesh seems to pulse with an otherworldly energy. It is clear that it's been here for a while, but surprisingly, it doesn't smell at all. What do you do?`,
                options: [
                    {
                        text: 'Plant spores in it',
                        key: 'plant_spores_in_it',
                        next: 'plantSpores'
                    },
                    {
                        text: 'Cut it open',
                        key: 'cut_it_open',
                        next: 'acceptSymbiont'
                    },
                    {
                        text: 'Leave it alone',
                        key: 'leave_it_alone',
                        next: 'closeDialog'
                    }
                ]
            },
            corpseExhausted: {
                text: `There is nothing more you can do with the old corpse. Its purpose has been fulfilled.`,
                options: [
                    {
                        text: 'Leave it alone',
                        key: 'leave_it_alone',
                        next: 'closeDialog'
                    }
                ]
            },
            corpseReconsider: {
                text: `You approach the strange corpse again. From within, you hear a familiar voice: "Changed your mind, baby? I'm still here waiting for you."`,
                options: [
                    {
                        text: 'Accept Thorne-Still as your symbiont',
                        key: 'accept_thornestill_as_your_symbiont',
                        next: 'acceptSymbiontConfirm'
                    },
                    {
                        text: 'Plant spores in it instead',
                        key: 'plant_spores_in_it_instead',
                        next: 'plantSpores'
                    },
                    {
                        text: 'Leave it alone',
                        key: 'leave_it_alone',
                        next: 'closeDialog'
                    }
                ]
            },
            plantSpores: {
                text: 'You carefully plant spores in the corpse. They immediately take root, spreading a network of luminescent mycelium through the dead flesh. This area will never be the same.',
                options: [
                    {
                        text: 'Continue',
                        key: 'continue',
                        next: 'closeDialogAndGrow'
                    }
                ]
            },
            acceptSymbiont: {
                text: `As you cut into the corpse's head, you find something extraordinary - a symbiotic entity that calls itself Thorne-Still. "Hey there, baby, I'm Thorne-Still. How can I help you today?" whispers in strange voice. "Maybe we can share a road for some time? What do you say? That fungus of yours looks comfortably enough for me."`,
                options: [
                    {
                        text: 'Accept Thorne-Still as your symbiont',
                        key: 'accept_thornestill_as_your_symbiont',
                        next: 'acceptSymbiontConfirm'
                    },
                    {
                        text: 'Decline',
                        key: 'decline',
                        next: 'declineSymbiont'
                    }
                ],
                onTrigger: () => {
                    // Mark that the symbiont has been offered
                    this.addJournalEntry(
                        'symbiont_thorne_still_offered',
                        'Encountered Thorne-Still',
                        'In the strange corpse at the crossroads, I found a symbiotic entity calling itself Thorne-Still. It offered to merge with me.',
                        this.journalSystem.categories.EVENTS
                    );
                }
            },
            acceptSymbiontConfirm: {
                text: 'Thorne-Still merges with your being. It literally crawls into your stomach. You feel its calm presence in your mind, and with it comes the ability to perceive the threads of reality itself. You can now use Brain Rot ability to make others confused, forgetful, or vulnerable to suggestion.',
                options: [
                    {
                        text: 'Continue',
                        key: 'continue',
                        next: 'closeDialogAndAcceptSymbiont'
                    }
                ]
            },
            declineSymbiont: {
                text:  `"Your lost, baby", whispers the symbiont. "But don't worry, I'll be here if you need me. "`,
                options: [
                    {
                        text: 'Continue',
                        key: 'continue',
                        next: 'closeDialogAndDeclineSymbiont'
                    }
                ]
            },
            closeDialog: {
                text: '',
                options: [],
                onShow: () => {
                    this.hideDialog();
                }
            },
            closeDialogAndGrow: {
                text: '',
                options: [],
                onTrigger: () => {
                    // Decrease spores by 10 (adjust as desired)
                    this.modifySpores(-10);

                    // Increase Growth by 2
                    this.modifyGrowthDecay(2, 0);
                    
                    // Add journal entry for planting spores
                    this.addJournalEntry(
                        'crossroad_corpse_spores_planted',
                        'Planted Spores in Crossroad Corpse',
                        'I planted spores in the strange corpse at the crossroads. The mycelium quickly spread through the dead flesh, transforming the area with luminescent growth. This has opened up a new path to what appears to be a skyship above.',
                        this.journalSystem.categories.EVENTS
                    );
                    
                    // Set the growth state and update background
                    this.registry.set('crossroadGrowth', true);
                    this.background.setTexture('crossroadBg_growth');
                    
                    // Remove the corpse
                    if (this.corpse) {
                        this.corpse.destroy();
                        this.corpse = null;
                    }
                    
                    // Directly create the skyship transition area
                    if (!this.skyshipTransition) {
                        // Add skyship transition area
                        this.skyshipTransition = this.add.image(400, 200, 'door')
                            .setDisplaySize(100, 150)
                            .setAlpha(0.01)
                            .setInteractive({ useHandCursor: true });
                        this.skyshipTransition.setDepth(10);
                        
                        // Add a subtle glow effect to hint at the interactive area
                        const skyshipGlow = this.add.graphics();
                        skyshipGlow.fillStyle(0x7fff8e, 0.2);
                        skyshipGlow.fillCircle(400, 200, 50);
                        skyshipGlow.setDepth(9);
                        
                        // Add pulsating animation to the glow
                        this.tweens.add({
                            targets: skyshipGlow,
                            alpha: { from: 0.2, to: 0.4 },
                            duration: 1500,
                            yoyo: true,
                            repeat: -1,
                            ease: 'Sine.easeInOut'
                        });
                        
                        // Setup the transition for the skyship area
                        this.setupSkyshipTransition();
                        
                        // Show a notification about the new area
                        this.showNotification("Some strange plant grows from the corpse. You also notice something above it...");
                    }
                    
                    this.hideDialog();
                }
            },
            closeDialogAndDeclineSymbiont: {
                text: '',
                options: [],
                onShow: () => {
                    // Mark that the symbiont has been declined using journal entry
                    this.addJournalEntry(
                        'symbiont_thorne_still_declined',
                        'Declined Thorne-Still',
                        'I declined the offer from the symbiotic entity Thorne-Still. It seemed disappointed but said it would wait for me if I changed my mind.',
                        this.journalSystem.categories.EVENTS
                    );
                    this.hideDialog();
                }
            },
            closeDialogAndAcceptSymbiont: {
                text: '',
                options: [],
                onShow: () => {
                    // Increase Decay by 2
                    this.modifyGrowthDecay(0, 2);
                    
                    // Mark that the symbiont has been accepted using journal entry
                    this.addJournalEntry(
                        'symbiont_thorne_still_accepted',
                        'Accepted Thorne-Still',
                        'I accepted the symbiotic entity Thorne-Still. It merged with me, crawling into my stomach. I can now use its Brain Rot ability to confuse and manipulate others.',
                        this.journalSystem.categories.EVENTS
                    );
                    
                    const success = this.symbiontSystem.addSymbiont('thorne-still', {
                        name: 'Thorne-Still',
                        power: 0,
                        ability: 'Brain Rot'
                    });

                    if (success) {
                        // Show notification about gaining the symbiont
                        this.showNotification('Gained Symbiont: Thorne-Still');
                        
                        // Add symbiont icon
                        this.addSymbiontIcon('thorne-still', {
                            name: 'Thorne-Still',
                            power: 0,
                            ability: 'Brain Rot'
                        });
                    }
                    this.hideDialog();
                }
            }
        }
    }
    
    showCorpseDialog() {
        // Determine which dialog to show based on journal entries
        if (this.hasJournalEntry('symbiont_thorne_still_accepted') || this.hasJournalEntry('symbiont_thorne_still_offered')) {
            // If symbiont was accepted or offered without explicit decline
            this.showDialog('corpseExhausted');
        } else if (this.hasGrowth) {
            // If growth was chosen
            this.showDialog('corpseExhausted');
        } else if (this.hasJournalEntry('symbiont_thorne_still_declined')) {
            // If symbiont was declined but not accepted yet
            this.showDialog('corpseReconsider');
        } else {
            // First interaction
            this.showDialog('corpseMain');
        }
    }
    
    startSkyshipAnimation() {
        // Create a camera zoom effect to simulate looking up
        const originalZoom = this.cameras.main.zoom;
        
        // Create the skyship image above the scene - make it cover the full screen
        const skyship = this.add.image(400, -100, 'skyship');
        // // Calculate scale to ensure full screen coverage
        // const scaleX = this.cameras.main.width / skyship.width * 1.2; // 20% larger than needed
        // const scaleY = this.cameras.main.height / skyship.height * 1.2;
        // const scale = Math.max(scaleX, scaleY); // Use the larger scale to ensure full coverage
        // skyship.setScale(scale);
        skyship.setScale(0.8);
        skyship.setAlpha(0);
        skyship.setDepth(10000);
        
        // Create a text message
        const messageBox = this.add.rectangle(400, 300, 600, 100, 0x0a2712, 0.9);
        messageBox.setStrokeStyle(2, 0x7fff8e);
        messageBox.setDepth(101);
        messageBox.setAlpha(0);
        
        const messageText = this.add.text(400, 300, "Looks like there is a skyship above the city...", {
            fontSize: '18px',
            fill: '#7fff8e',
            align: 'center',
            wordWrap: { width: 580 }
        });
        messageText.setOrigin(0.5);
        messageText.setDepth(10200);
        messageText.setAlpha(0);
        
        // Use sequential tweens instead of timeline
        // Step 1: First zoom out slightly to prepare for looking up
        this.tweens.add({
            targets: this.cameras.main,
            zoom: originalZoom * 0.9,
            duration: 1000,
            ease: 'Sine.easeInOut',
            onComplete: () => {
                // Add journal entry about skyship seen above the city
                if (!this.hasJournalEntry('skyship_sighting')) {
                    this.addJournalEntry(
                        'skyship_sighting',
                        'Strange Vessel in the Emerald Sky',
                        'A massive skyship hovers above Upper Morkezela, its hull gleaming with an unnatural light. The locals say it appeared a month ago and hasn\'t moved since. Some believe it to be a vessel of the fungal gods, others whisper of more terrestrial origins. Its purpose remains unknown, but its presence has changed the city\'s atmosphere, both literally and figuratively - spores seem to drift from its direction when the wind is right.',
                        this.journalSystem.categories.EVENTS,
                        { location: 'Upper Morkezela skyline' }
                    );
                }
                // Step 2: Then zoom in and pan up to simulate looking up
                this.tweens.add({
                    targets: this.cameras.main,
                    zoom: originalZoom * 1.2,
                    scrollY: -150,
                    duration: 2000,
                    ease: 'Sine.easeInOut',
                    onComplete: () => {
                        // Step 3: Fade in the skyship
                        this.tweens.add({
                            targets: skyship,
                            y: 100,
                            alpha: 1,
                            duration: 2000,
                            ease: 'Sine.easeOut',
                            onComplete: () => {
                                // Step 4: Show the message after the skyship appears
                                this.tweens.add({
                                    targets: [messageBox, messageText],
                                    alpha: 1,
                                    duration: 1000,
                                    ease: 'Sine.easeInOut',
                                    onComplete: () => {
                                        // Step 5: Wait a moment and then transition to the SkyshipBoardScene
                                        this.time.delayedCall(3000, () => {
                                            // Fade out to transition to the new scene
                                            this.cameras.main.fadeOut(1000, 0, 0, 0);
                                            this.cameras.main.once('camerafadeoutcomplete', () => {
                                                // Reset camera settings before changing scenes
                                                this.cameras.main.zoom = originalZoom;
                                                this.cameras.main.scrollX = 0;
                                                this.cameras.main.scrollY = 0;
                                                
                                                // Start the SkyshipBoardScene
                                                this.scene.start('SkyshipBoardScene');
                                                this.isTransitioning = false;
                                            });
                                        });
                                    }
                                });
                            }
                        });
                    }
                });
            }
        });
    }

    // Handle registry changes, particularly for crossroadGrowth
    handleRegistryChange(parent, key, data) {
        // If the crossroadGrowth registry key changes, update the scene
        if (key === 'crossroadGrowth' && data === true && !this.hasGrowth) {
            // Update our local tracking variable
            this.hasGrowth = true;
            
            // Update the background
            if (this.background) {
                this.background.setTexture('crossroadBg_growth');
            }
            // Remove corpse if it exists
            if (this.corpse) {
                this.corpse.destroy();
                this.corpse = null;
            }
            
            // Add skyship transition area if it doesn't exist yet
            if (!this.skyshipTransition) {
                // Add skyship transition area
                this.skyshipTransition = this.add.image(400, 200, 'door')
                    .setDisplaySize(100, 150)
                    .setAlpha(0.01)
                    .setInteractive({ useHandCursor: true });
                this.skyshipTransition.setDepth(10);
                
                // Add a subtle glow effect to hint at the interactive area
                const skyshipGlow = this.add.graphics();
                skyshipGlow.fillStyle(0x7fff8e, 0.2);
                skyshipGlow.fillCircle(400, 200, 50);
                skyshipGlow.setDepth(9);
                
                // Add pulsating animation to the glow
                this.tweens.add({
                    targets: skyshipGlow,
                    alpha: { from: 0.2, to: 0.4 },
                    duration: 1500,
                    yoyo: true,
                    repeat: -1,
                    ease: 'Sine.easeInOut'
                });
                
                // Setup the transition for the skyship area
                this.setupSkyshipTransition();
            }
        }
    }
    
    // Setup the transition for the skyship area
    setupSkyshipTransition() {
        if (!this.skyshipTransition) return;
        
        console.log('Setting up skyship transition');
        
        this.skyshipTransition.on('pointerdown', () => {
            console.log('Skyship transition clicked');
            if (this.isTransitioning) return;
            this.isTransitioning = true;
            
            // Get priest position
            const priest = this.priest;
            if (!priest) {
                // If priest doesn't exist, just start the animation immediately
                console.log('No priest found, starting skyship animation directly');
                this.startSkyshipAnimation();
                return;
            }
            
            // Calculate distance to transition point
            const distance = Phaser.Math.Distance.Between(
                priest.x, priest.y,
                this.skyshipTransition.x, this.skyshipTransition.y
            );
            
            // Calculate duration based on distance (faster for closer distances)
            const duration = Math.min(Math.max(distance * 5, 500), 2000);
            
            // Create a variable to track if the tween completed
            let tweenCompleted = false;
            
            // Move priest to the transition point
            priest.play('walk');
            
            // Kill any existing tweens
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: this.skyshipTransition.x,
                y: 470,
                duration: duration,
                ease: 'Linear',
                onComplete: () => {
                    tweenCompleted = true;
                    priest.play('idle');
                    this.startSkyshipAnimation();
                }
            });
            
            // Add a safety timeout in case the tween doesn't complete
            this.time.delayedCall(2000, () => {
                if (!tweenCompleted) {
                    console.log('Skyship transition tween timed out, forcing transition');
                    if (priest.anims && priest.anims.exists('idle')) {
                        priest.play('idle');
                    }
                    this.startSkyshipAnimation();
                }
            });
        });
    }
    
    update() {
        super.update();

        // Check if player is at the right edge of the screen
        if (this.priest && this.priest.x > 780 && !this.isTransitioning) {
            this.isTransitioning = true;
            this.priest.play('idle');
            this.cameras.main.fadeOut(800, 0, 0, 0);
            this.cameras.main.once('camerafadeoutcomplete', () => {
                this.scene.start('VoxMarket');
                this.isTransitioning = false; // Reset transition flag
            });
        }

        if (this.priest && this.priest.x < 80 && !this.isTransitioning) {
            this.isTransitioning = true;
            this.priest.play('idle');
            this.cameras.main.fadeOut(800, 0, 0, 0);
            this.cameras.main.once('camerafadeoutcomplete', () => {
                this.scene.start('EggCatedralScene');
                this.isTransitioning = false; // Reset transition flag
            });
        }

        // Check Growth/Decay effects on symbionts
        if (this.symbiontSystem) {
            const growth = this.registry.values.growth || 0;
            const decay = this.registry.values.decay || 0;
            const effect = this.symbiontSystem.checkDecayGrowthEffects(decay, growth);
            
            if (effect) {
                if (effect.type === 'leave') {
                    this.showNotification(effect.message, 0xff0000);
                }
            }
        }
    }
}
