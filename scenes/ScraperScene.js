import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class ScraperScene extends GameScene {
    constructor() {
        super({ key: 'ScraperScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        return {
            ...super.dialogContent, // Include parent dialog content for symbiont dialogs
            // Add ScraperScene specific dialogs here if needed
        };
    }

    preload() {
        super.preload();
        this.load.image('scraperBg', 'assets/images/backgrounds/Scraper1140.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set scraper background
        const bg = this.add.image(400, 300, 'scraperBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Add invisible clickable exit area at the left side
        this.exitArea = this.add.image(50, 470, 'exitArea')
            .setDisplaySize(40, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);
        
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

        // Exit area click handler
        this.exitArea.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);

            this.tweens.add({
                targets: priest,
                x: 50,
                y: 470,
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('CrossroadScene');
                    });
                }
            });
        });
        
        // Create exit to ScreamingCorkScene at the right edge
        this.transitionManager.createTransitionZone(
            750, // x position
            470, // y position
            80, // width
            200, // height
            'right', // direction
            'BurningBearStreetScene', // target scene
            750, // walk to x
            470 // walk to y
        );
    }

    update() {
        super.update();
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.ScraperScene = ScraperScene;
}
