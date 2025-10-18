import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class BurningBearStreetScene extends GameScene {
    constructor() {
        super({ key: 'BurningBearStreetScene' });
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
        this.load.image('burningBearStreetBg', 'assets/images/backgrounds/BurningBearStreet.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set scraper background
        const bg = this.add.image(400, 300, 'burningBearStreetBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        
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

        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            80, // width
            200, // height
            'left', // direction
            'ScraperScene', // target scene
            750, // walk to x
            470 // walk to y
        );

        this.transitionManager.createTransitionZone(
            400, // x position
            470, // y position
            80, // width
            200, // height
            'up', // direction
            'TownhallScene', // target scene
            750, // walk to x
            470 // walk to y
        );
        
        this.transitionManager.createTransitionZone(
            750, // x position
            470, // y position
            80, // width
            200, // height
            'right', // direction
            'ScreamingCorkScene', // target scene
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
    window.BurningBearStreetScene = BurningBearStreetScene;
}
