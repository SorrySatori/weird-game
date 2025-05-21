import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class ScreamingCorkScene extends GameScene {
    constructor() {
        super({ key: 'ScreamingCorkScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        return {
            ...super.dialogContent, // Include parent dialog content for symbiont dialogs
            // Add ScreamingCorkScene specific dialogs here if needed
        };
    }

    preload() {
        super.preload();
        this.load.image('screamingCorkBg', 'assets/images/ScreamingCork.png');
        this.load.image('arrow', 'assets/images/arrow.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set background
        const bg = this.add.image(400, 300, 'screamingCorkBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Position the priest at the right side when entering from ScraperScene
        this.priest.x = 700;
        this.priest.y = 470;
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
        
        // Create exit to ScraperScene at the left edge
        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            80, // width
            200, // height
            'left', // direction
            'ScraperScene', // target scene
            50, // walk to x
            470 // walk to y
        );
        
        // Create entrance to the tavern interior (centered on the tavern door)
        this.transitionManager.createTransitionZone(
            400, // x position - centered on the door
            470, // y position
            100, // width
            200, // height
            'up', // direction
            'ScreamingCorkInteriorScene', // target scene
            100, // walk to x - position inside the tavern
            470 // walk to y
        );
        
        // Add a hint about the tavern entrance
        const doorHint = this.add.text(400, 380, 'Enter Tavern', {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        doorHint.setOrigin(0.5);
        doorHint.setAlpha(0);
        doorHint.setDepth(10);
        
        // Show hint when hovering near the door
        this.input.on('pointermove', (pointer) => {
            // Check if pointer is near the door area
            if (Math.abs(pointer.x - 400) < 50 && Math.abs(pointer.y - 470) < 100) {
                doorHint.setAlpha(1);
            } else {
                doorHint.setAlpha(0);
            }
        });
    }

    update() {
        super.update();
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.ScreamingCorkScene = ScreamingCorkScene;
}
