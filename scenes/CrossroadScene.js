import GameScene from './GameScene.js';
import SymbiontSystem from '../systems/SymbiontSystem.js';

export default class CrossroadScene extends GameScene {
    constructor() {
        super({ key: 'CrossroadScene' });
        this.isTransitioning = false;
        this.symbiontSystem = new SymbiontSystem(this);
    }

    preload() {
        super.preload();
        this.load.image('crossroadBg', 'assets/images/crossroad.png');
        this.load.image('door', 'assets/images/door.png');
    }

    create() {
        super.create();
        
        // Set crossroad background
        const bg = this.add.image(400, 300, 'crossroadBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        // Add invisible clickable area for Shed13 entrance
        this.marketEntrance = this.add.image(100, 400, 'door')
            .setDisplaySize(120, 200)  // Made even wider to better match the large door
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

        // Add corpse clickable area
        this.corpseInteraction = this.add.rectangle(400, 300, 100, 150, 0x000000, 0)
            .setInteractive({ useHandCursor: true });
        this.corpseInteraction.setDepth(10);
        
        this.corpseInteraction.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.showCorpseDialog();
        });

        // Add symbiont slots to inventory
        this.createSymbiontSlots();

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
                y: 470, // Ground level
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
                y: 470, // Ground level
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
                y: 470, // Ground level
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

    createSymbiontSlots() {
        const startX = 60;
        const startY = 480;
        const spacing = 40;
        const slotSize = 30;

        for (let i = 0; i < this.symbiontSystem.maxSlots; i++) {
            // Create slot background
            const slot = this.add.rectangle(startX + (i * spacing), startY, slotSize, slotSize, 0x1a3b23)
                .setStrokeStyle(1, 0x7fff8e)
                .setDepth(100)
                .setAlpha(i < this.symbiontSystem.unlockedSlots ? 1 : 0.3);

            if (i >= this.symbiontSystem.unlockedSlots) {
                this.add.text(slot.x, slot.y, '', {
                    fontSize: '16px',
                    color: '#7fff8e'
                }).setOrigin(0.5).setDepth(101);
            }
        }
    }

    get dialogContent() {
        // Get parent dialog content first
        const parentContent = super.dialogContent || {};
        
        // Return combined dialog content
        return {
            ...parentContent,
            corpseMain: {
                text: 'Before you lies a massive, rotting corpse of an unknown creature, grotesquely impaled on the crossroad sign. Its flesh seems to pulse with an otherworldly energy, despite its obvious state of decay.',
                options: [
                    {
                        text: 'Plant spores in it',
                        next: 'corpseSpores'
                    },
                    {
                        text: 'Cut it open and look inside',
                        next: 'corpseCut'
                    },
                    {
                        text: 'Leave it alone',
                        next: 'closeDialog'
                    }
                ]
            },
            corpseSpores: {
                text: 'You plant the spores in the decaying flesh. Almost immediately, you can see them taking root, spreading through the dead tissue. A massive fungal growth begins to sprout, reaching towards the sky...',
                options: [
                    {
                        text: 'Continue',
                        next: 'closeDialogAndGrow'
                    }
                ]
            },
            corpseCut: {
                text: 'As you cut into the corpse, you discover something extraordinary - a creature dwelling within! It\'s Thorne-Still, a parasitic entity that has made this corpse its temporary home. It speaks to you telepathically...',
                options: [
                    {
                        text: 'Accept Thorne-Still as your symbiont',
                        next: 'acceptSymbiont'
                    },
                    {
                        text: 'Decline',
                        next: 'closeDialog'
                    }
                ]
            },
            acceptSymbiont: {
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
                onShow: () => {
                    // Increase Growth by 2
                    this.modifyGrowthDecay(2, 0);
                    this.hideDialog();
                    // TODO: Implement secret area access
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
                        this.showNotification('Gained Symbiont: Thorne-Still', 0x7fff8e);
                        
                        // Add symbiont icon using a circle instead of an image
                        const slot = this.symbiontSystem.symbionts.size - 1;
                        const x = 60 + (slot * 40);
                        const y = 480;
                        
                        // Create glowing circle for symbiont
                        const symbiontIcon = this.add.circle(x, y, 12, 0x7fff8e)
                            .setDepth(102);
                        
                        // Add pulsing animation
                        this.tweens.add({
                            targets: symbiontIcon,
                            scale: 1.2,
                            alpha: 0.8,
                            duration: 1000,
                            yoyo: true,
                            repeat: -1,
                            ease: 'Sine.easeInOut'
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

        // Random symbiont messages
        if (this.symbiontSystem && Math.random() < 0.001) { // 0.1% chance per frame
            const message = this.symbiontSystem.getRandomMessage('thorne-still');
            if (message) {
                this.showNotification(message, 0x7fff8e);
            }
        }
    }
}
