import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class ShedAbandonedOfficeScene extends GameScene {
    constructor() {
        super({ key: 'ShedAbandonedOfficeScene' });
        this.isTransitioning = false;
    }

    preload() {
        super.preload();
        this.preloadMusic('shedLoop');
        this.load.image('office-bg', 'assets/images/backgrounds/ShedAbandonedOffice.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        this.playSceneMusic('shedLoop', { resume: true });
        
        // Native 1067×600 (tools/artgen/office_bg.py): the old picture re-pixelled, the graffito kept 1:1
        const bg = this.add.image(400, 300, 'office-bg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        // The background paints its own floor; the generic ground strip would cover it.
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }

        // Set initial priest position (on the walk line, feet at y 534 like every scene)
        if (this.priest) {
            this.priest.x = 250;  // Match entrance position from Shed521FloorsScene
            this.priest.y = 470;
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
            50, // walk to x
            470, // walk to y
            'Back to the stairs' 
        )

        // The doorway in the back wall leads on to the Hall
        this.transitionManager.createTransitionZone(
            352, // x position
            205, // y position
            78, // width
            156, // height
            'up', // direction
            'ShedHallScene',
            352, // walk to x
            470, // walk to y
            'To the Hall'
        )
    }

    update() {
        super.update();
    }
}
