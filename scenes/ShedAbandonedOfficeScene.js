import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class ShedAbandonedOfficeScene extends GameScene {
    constructor() {
        super({ key: 'ShedAbandonedOfficeScene' });
        this.isTransitioning = false;
    }

    preload() {
        super.preload();
        this.load.image('office-bg', 'assets/images/backgrounds/ShedAbandonedOffice.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set background
        const bg = this.add.image(400, 300, 'office-bg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Set initial priest position
        if (this.priest) {
            this.priest.x = 250;  // Match entrance position from Shed521FloorsScene
            this.priest.y = 520;  // Ground level
            this.priest.setOrigin(0.5, 1);
            this.priest.play('idle');
        }
        this.transitionManager = new SceneTransitionManager(this);

        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            50, // width
            200, // height
            'left', // direction
            'Shed521FloorsScene',
            700, // walk to x
            470, // walk to y
            'Back to the stairs' 
        )

        this.transitionManager.createTransitionZone(
            750, // x position
            470, // y position
            50, // width
            200, // height
            'right', // direction
            'ShedHallScene',
            100, // walk to x
            470, // walk to y
            'To the Hall' 
        )
    }

    update() {
        super.update();
    }
}
