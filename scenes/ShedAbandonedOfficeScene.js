import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

const WALK_Y = 534 - 64 * 2;   // the 2× priest's centre with his feet on the floor line

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

        // The room is the old picture shown 3× and drawn close up: at his usual 128 px the priest was a child next to the
        // desks, so here he is twice as big (integer: crisp pixels), feet on the same line (y 534)
        if (this.priest) {
            this.setPriestScale(2);
            this.priest.x = 250;  // Match entrance position from Shed521FloorsScene
            this.priest.y = WALK_Y;
            this.priest.play('idle');
        }
        this.transitionManager = new SceneTransitionManager(this);

        // the whole left edge of the room, as tall as the (2×) priest standing there
        this.transitionManager.createTransitionZone(
            50, // x position
            380, // y position
            50, // width
            380, // height
            'left', // direction
            'Shed521FloorsScene',
            50, // walk to x
            WALK_Y, // walk to y
            'Back to the stairs' 
        )

        // The doorway in the back wall leads on to the Hall: from its lintel down past the desks to the floor, so it is
        // as easy to hit as the room's other exit (there is nothing else to click here)
        this.transitionManager.createTransitionZone(
            352, // x position
            280, // y position
            78, // width
            306, // height
            'up', // direction
            'ShedHallScene',
            352, // walk to x
            WALK_Y, // walk to y
            'To the Hall'
        )
    }

    update() {
        super.update();
    }
}
