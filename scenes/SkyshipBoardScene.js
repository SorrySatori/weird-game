import GameScene from './GameScene.js';

export default class SkyshipBoardScene extends GameScene {
    constructor() {
        super({ key: 'SkyshipBoardScene' });
        this.isTransitioning = false;
    }

    preload() {
        super.preload();
        this.load.image('skyshipBoardBg', 'assets/images/skyship_board.png');
        this.load.image('exitArea', 'assets/images/door.png');
    }

    create() {
        super.create();

        // Set skyship board background
        this.background = this.add.image(400, 300, 'skyshipBoardBg');
        this.background.setDisplaySize(800, 600);
        this.background.setDepth(-1);

        // Create symbiont UI
        this.createSymbiontUI();

        // Add exit area to go back to CrossroadScene
        this.exitArea = this.add.image(100, 500, 'exitArea')
            .setDisplaySize(120, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);

        // Add a subtle glow effect to hint at the exit area
        const exitGlow = this.add.graphics();
        exitGlow.fillStyle(0x7fff8e, 0.2);
        exitGlow.fillCircle(100, 500, 50);
        exitGlow.setDepth(9);
        
        // Add pulsating animation to the glow
        this.tweens.add({
            targets: exitGlow,
            alpha: { from: 0.2, to: 0.4 },
            duration: 1500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Add a text hint for the exit
        const exitText = this.add.text(100, 550, "Return to city", {
            fontSize: '16px',
            fill: '#7fff8e',
            align: 'center'
        });
        exitText.setOrigin(0.5);
        exitText.setDepth(10);

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);

        // Setup scene transitions
        this.setupSceneTransitions();
    }

    setupSceneTransitions() {
        // Exit to CrossroadScene
        this.exitArea.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: 100,
                y: 500,
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('CrossroadScene');
                    });
                }
            });
        });
    }

    dialogContent() {
        return {
            main: {
                text: 'You find yourself on the deck of a skyship. The air is thin up here, and you can see the fungal city sprawled below.',
                options: [
                    {
                        text: 'Look around',
                        next: 'lookAround'
                    },
                    {
                        text: 'Close',
                        next: 'closeDialog'
                    }
                ]
            },
            lookAround: {
                text: 'The skyship appears to be a transport vessel. Various fungal growths line the edges of the deck, seemingly serving as both decoration and structural support. The ship sways gently in the wind.',
                options: [
                    {
                        text: 'Back',
                        next: 'main'
                    }
                ]
            },
            closeDialog: {
                text: '',
                options: [],
                onShow: () => {
                    this.hideDialog();
                }
            }
        };
    }

    update() {
        super.update();

        // Check Growth/Decay effects on symbionts if applicable
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
