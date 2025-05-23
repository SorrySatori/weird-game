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
    }

    create() {
        super.create();

        // Set crossroad background based on growth state
        const hasGrowth = this.registry.get('crossroadGrowth') || false;
        const bgKey = hasGrowth ? 'crossroadBg_growth' : 'crossroadBg';
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

        if (!hasGrowth) {
            this.corpse = this.add.image(400, 300, 'door');
            this.corpse.setDisplaySize(120, 200);
            this.corpse.setAlpha(0.01);
            this.corpse.setInteractive({ useHandCursor: true });
            this.corpse.on('pointerdown', () => this.showCorpseDialog());
        }

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);

        // Scene transitions setup...
        this.setupSceneTransitions();

        // Load persisted symbiont system
        this.symbiontSystem = this.registry.get('symbiontSystem');
    }

    setupSceneTransitions() {
        // Shed13 entrance click logic
        this.marketEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: 100,
                y: 470,
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('Shed13Scene');
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
            ...super.dialogContent,  // Include parent dialog content
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
