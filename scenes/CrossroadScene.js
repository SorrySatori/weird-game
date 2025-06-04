import GameScene from './GameScene.js';

export default class CrossroadScene extends GameScene {
    constructor() {
        super({ key: 'CrossroadScene' });
        this.isTransitioning = false;
        // Use the persisted symbiont system
        this.symbiontSystem = null; // Will be set in create from registry
    }

    preload() {
        super.preload();
        this.load.image('crossroadBg', 'assets/images/crossroad.png');
        this.load.image('crossroadBg_growth', 'assets/images/crossroad_growth.png');
        this.load.image('door', 'assets/images/door.png');
        this.load.image('skyship', 'assets/images/skyship.png');
    }

    create() {
        super.create();

        // Check if growth has happened
        this.hasGrowth = this.registry.get('crossroadGrowth') || false;
        const bgKey = this.hasGrowth ? 'crossroadBg_growth' : 'crossroadBg';
        this.background = this.add.image(400, 300, bgKey);
        this.background.setDisplaySize(800, 600);
        this.background.setDepth(-1);

        // Create symbiont UI
        this.createSymbiontUI();

        // Add invisible clickable area for Shed13 entrance
        this.marketEntrance = this.add.image(100, 400, 'door')
            .setDisplaySize(120, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.marketEntrance.setDepth(10);

        // Add invisible clickable area for VoxMarket entrance
        this.voxMarketEntrance = this.add.image(650, 400, 'door')
            .setDisplaySize(100, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.voxMarketEntrance.setDepth(10);

        // Add invisible clickable area for Scraper entrance
        this.scraperEntrance = this.add.image(400, 400, 'door')
            .setDisplaySize(100, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.scraperEntrance.setDepth(10);

        // Add invisible clickable area at the right border for EntryScene
        this.scraperSceneEntrance = this.add.image(750, 470, 'door')
            .setDisplaySize(40, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.scraperSceneEntrance.setDepth(10);

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

        // Scene transitions setup...
        this.setupSceneTransitions();

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
        // Setup the transition for the skyship area if it exists
        if (this.hasGrowth && this.skyshipTransition) {
            this.setupSkyshipTransition();
        }
        
        // Setup the transition for the market entrance
        this.marketEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;
            
            // Get priest position
            const priestX = this.priest.x;
            const priestY = this.priest.y;
            
            // Calculate distance to transition point
            const distance = Phaser.Math.Distance.Between(
                priestX, priestY,
                this.marketEntrance.x, this.marketEntrance.y
            );
            
            // Calculate duration based on distance (faster for closer distances)
            const duration = Math.min(Math.max(distance * 5, 500), 2000);
            
            // Move priest to the transition point
            this.priest.play('walk');
            this.tweens.add({
                targets: this.priest,
                x: this.marketEntrance.x,
                y: this.marketEntrance.y,
                duration: duration,
                ease: 'Linear',
                onComplete: () => {
                    this.priest.play('idle');
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('VoxMarket');
                    });
                }
            });
        });
        
        // Setup the transition for the cathedral entrance
        this.cathedralEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;
            
            // Get priest position
            const priestX = this.priest.x;
            const priestY = this.priest.y;
            
            // Calculate distance to transition point
            const distance = Phaser.Math.Distance.Between(
                priestX, priestY,
                this.cathedralEntrance.x, this.cathedralEntrance.y
            );
            
            // Calculate duration based on distance (faster for closer distances)
            const duration = Math.min(Math.max(distance * 5, 500), 2000);
            
            // Move priest to the transition point
            this.priest.play('walk');
            this.tweens.killTweensOf(this.priest);
            
            this.tweens.add({
                targets: this.priest,
                x: this.cathedralEntrance.x,
                y: this.cathedralEntrance.y,
                duration: duration,
                ease: 'Linear',
                onComplete: () => {
                    this.priest.play('idle');
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('EggCatedralScene');
                        this.isTransitioning = false;
                    });
                }
            });
        });

        // VoxMarket entrance click logic
        this.voxMarketEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: 650,
                y: 470,
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('VoxMarket');
                    });
                }
            });
        });

        // ScraperScene entrance click logic
        this.scraperSceneEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: 750,
                y: 470,
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('ScraperScene');
                    });
                }
            });
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
            corpseMain: {
                text: 'You find a strange corpse. Its flesh seems to pulse with an otherworldly energy. What do you do?',
                options: [
                    {
                        text: 'Plant spores in it',
                        next: 'plantSpores'
                    },
                    {
                        text: 'Cut it open',
                        next: 'acceptSymbiont'
                    },
                    {
                        text: 'Leave it alone',
                        next: 'closeDialog'
                    }
                ]
            },
            plantSpores: {
                text: 'You carefully plant spores in the corpse. They immediately take root, spreading a network of luminescent mycelium through the dead flesh. This area will never be the same.',
                options: [
                    {
                        text: 'Continue',
                        next: 'closeDialogAndGrow'
                    }
                ]
            },
            acceptSymbiont: {
                text: 'As you cut into the corpse, you find something extraordinary - a symbiotic entity that calls itself Thorne-Still. It offers to merge with you, granting you the power to perceive and manipulate the threads of reality itself.',
                options: [
                    {
                        text: 'Accept Thorne-Still as your symbiont',
                        next: 'acceptSymbiontConfirm'
                    },
                    {
                        text: 'Decline',
                        next: 'closeDialog'
                    }
                ]
            },
            acceptSymbiontConfirm: {
                text: 'Thorne-Still merges with your being. You feel its calm presence in your mind, and with it comes the ability to perceive the threads of reality itself. You can now use Suture-Reality to temporarily repair glitched environments.',
                options: [
                    {
                        text: 'Continue',
                        next: 'closeDialogAndAcceptSymbiont'
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
            closeDialogAndAcceptSymbiont: {
                text: '',
                options: [],
                onShow: () => {
                    // Increase Decay by 2
                    this.modifyGrowthDecay(0, 2);
                    
                    const success = this.symbiontSystem.addSymbiont('thorne-still', {
                        name: 'Thorne-Still',
                        power: 0,
                        ability: 'Suture-Reality'
                    });

                    if (success) {
                        // Show notification about gaining the symbiont
                        this.showNotification('Gained Symbiont: Thorne-Still');
                        
                        // Add symbiont icon
                        this.addSymbiontIcon('thorne-still', {
                            name: 'Thorne-Still',
                            power: 0,
                            ability: 'Suture-Reality'
                        });
                }
                this.hideDialog();
            }
        }
    };
}
    
    showCorpseDialog() {
        this.showDialog('corpseMain');
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
        
        this.skyshipTransition.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;
            
            // Get priest position
            const priestX = this.priest.x;
            const priestY = this.priest.y;
            
            // Calculate distance to transition point
            const distance = Phaser.Math.Distance.Between(
                priestX, priestY,
                this.skyshipTransition.x, this.skyshipTransition.y
            );
            
            // Calculate duration based on distance (faster for closer distances)
            const duration = Math.min(Math.max(distance * 5, 500), 2000);
            
            // Move priest to the transition point
            this.priest.play('walk');
            this.tweens.add({
                targets: this.priest,
                x: this.skyshipTransition.x,
                y: 470,
                duration: duration,
                ease: 'Linear',
                onComplete: () => {
                    this.priest.play('idle');
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
