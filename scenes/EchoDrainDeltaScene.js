import GameScene from './GameScene.js'
import SceneTransitionManager from '../utils/SceneTransitionManager.js'

export default class EchoDrainDeltaScene extends GameScene {
    constructor() {
        super({ key: 'EchoDrainDeltaScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        return {
            ...super.dialogContent,
        };
    }

    preload() {
        super.preload();

        this.load.image('echoDrainDeltaBg', 'assets/images/backgrounds/EchoDrainDelta.png');
        this.load.image('metal_scrap', 'assets/images/items/metal_scrap.png');
    }

    create() {
        super.create();

        const bg = this.add.image(400, 300, 'echoDrainDeltaBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        this.transitionManager = new SceneTransitionManager(this);

        // Transition back to Harbor (left side)
        this.transitionManager.createTransitionZone(
            0,
            300,
            80,
            400,
            'left',
            'HarborScene',
            750,
            300,
        );

        // Create metal scrap collectible
        this.createMetalScrapCollectible();

        this.cameras.main.fadeIn(800, 0, 0, 0);
    }

    createMetalScrapCollectible() {
        // Check if metal scrap has already been collected
        if (this.registry.get('delta_metal_scrap_collected')) {
            return;
        }

        const metalScrap = this.add.sprite(500, 450, 'metal_scrap');
        metalScrap.setScale(0.05);
        metalScrap.setDepth(10);
        metalScrap.setInteractive({ useHandCursor: true });

        // Add glow effect
        const scrapGlow = this.add.graphics();
        scrapGlow.fillStyle(0xc0c0c0, 0.2);
        scrapGlow.fillCircle(500, 350, 30);
        scrapGlow.setDepth(9);

        // Pulsing animation
        this.tweens.add({
            targets: scrapGlow,
            alpha: { from: 0.2, to: 0.05 },
            duration: 1500,
            yoyo: true,
            repeat: -1
        });

        // Hover effect
        metalScrap.on('pointerover', () => {
            metalScrap.setScale(0.07);
        });

        metalScrap.on('pointerout', () => {
            metalScrap.setScale(0.05);
        });

        // Collect item
        metalScrap.on('pointerdown', () => {
            if (this.clickSound) {
                this.clickSound.play();
            }

            // Add to inventory
            const added = this.addItemToInventory({
                id: 'metal_scrap',
                name: 'Metal Scrap',
                description: 'Rusty metal fragments found in the delta.',
                image: 'metal_scrap',
                stackable: true
            });

            if (added) {
                // Mark as collected
                this.registry.set('delta_metal_scrap_collected', true);

                // Fade out and destroy
                this.tweens.add({
                    targets: [metalScrap, scrapGlow],
                    alpha: 0,
                    scale: 0,
                    duration: 300,
                    onComplete: () => {
                        metalScrap.destroy();
                        scrapGlow.destroy();
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
    window.EchoDrainDeltaScene = EchoDrainDeltaScene;
}

export { EchoDrainDeltaScene };
