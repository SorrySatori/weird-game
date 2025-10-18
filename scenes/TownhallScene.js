import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class TownhallScene extends GameScene {
    constructor() {
        super({ key: 'TownhallScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        return {
            ...super.dialogContent, // Include parent dialog content for symbiont dialogs
            // Add TownhallScene specific dialogs here if needed
        };
    }

    preload() {
        super.preload();
        this.load.image('townhallBg', 'assets/images/backgrounds/townhall.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set townhall background
        const bg = this.add.image(400, 300, 'townhallBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            80, // width
            200, // height
            'left', // direction
            'BurningBearStreetScene', // target scene
            750, // walk to x
            470 // walk to y
        );

        // Position the priest at the bottom center when entering
        this.priest.x = 400;
        this.priest.y = 470;
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        this.cameras.main.fadeIn(800, 0, 0, 0);
    }

    update() {
        super.update();
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.TownhallScene = TownhallScene;
}

export { TownhallScene };
