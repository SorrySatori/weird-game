import GameScene from './GameScene.js'
import SceneTransitionManager from '../utils/SceneTransitionManager.js'

export default class HarborScene extends GameScene {
    constructor() {
        super({ key: 'HarborScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        return {
            ...super.dialogContent,
        };
    }

    preload() {
        super.preload();

        this.load.image('harborBg', 'assets/images/backgrounds/Harbor.png');
        this.load.image('oil', 'assets/images/items/oil.png');
    }

    create() {
        super.create();

        const bg = this.add.image(400, 300, 'harborBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        this.transitionManager = new SceneTransitionManager(this);

        // Transition back to TownSquare (left side)
        this.transitionManager.createTransitionZone(
            0,
            300,
            80,
            400,
            'left',
            'TownSquareScene',
            750,
            300,
        );

        // Transition to EchoDrainDelta (right side)
        this.transitionManager.createTransitionZone(
            720,
            300,
            80,
            400,
            'right',
            'EchoDrainDeltaScene',
            50,
            300,
        );

        // Create oil collectible
        this.createOilCollectible();

        this.cameras.main.fadeIn(800, 0, 0, 0);
    }

    createOilCollectible() {
        // Check if oil has already been collected
        if (this.registry.get('harbor_oil_collected')) {
            return;
        }

        const oil = this.add.sprite(300, 470, 'oil');
        oil.setScale(0.075);
        oil.setDepth(10);
        oil.setInteractive({ useHandCursor: true });

        // Add glow effect
        const oilGlow = this.add.graphics();
        oilGlow.fillStyle(0xffaa00, 0.2);
        oilGlow.fillCircle(300, 400, 30);
        oilGlow.setDepth(9);

        // Pulsing animation
        this.tweens.add({
            targets: oilGlow,
            alpha: { from: 0.2, to: 0.05 },
            duration: 1500,
            yoyo: true,
            repeat: -1
        });

        // Floating animation
        this.tweens.add({
            targets: oil,
            y: { from: 470, to: 480 },
            duration: 2000,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });

        // Hover effect
        oil.on('pointerover', () => {
            oil.setScale(0.08);
        });

        oil.on('pointerout', () => {
            oil.setScale(0.075);
        });

        // Collect item
        oil.on('pointerdown', () => {
            if (this.clickSound) {
                this.clickSound.play();
            }

            // Add to inventory
            const added = this.addItemToInventory({
                id: 'oil',
                name: 'Oil',
                description: 'Viscous oil found at the harbor.',
                image: 'oil',
                stackable: true
            });

            if (added) {
                // Mark as collected
                this.registry.set('harbor_oil_collected', true);

                // Fade out and destroy
                this.tweens.add({
                    targets: [oil, oilGlow],
                    alpha: 0,
                    scale: 0,
                    duration: 300,
                    onComplete: () => {
                        oil.destroy();
                        oilGlow.destroy();
                    }
                });
            }
        });
    }

    shutdown() {
        super.shutdown();
    }

    update() {
        super.update();
    }
}

if (typeof window !== 'undefined') {
    window.HarborScene = HarborScene;
}

export { HarborScene };
