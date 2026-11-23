import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

const WALK_Y = 534 - 64;   // the priest's centre (128 px, origin 0.5) with his feet on the floor line y 534

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
        
        // Native 1067×600 on the shared camera (tools/artgen/office_native_bg.py): the old room redrawn, the graffito
        // BETTER DECAY THAN CHANGE sprayed anew; Palinode's bricked opening on the graffito wall stays at canvas (662, 212)
        const bg = this.add.image(400, 300, 'office-bg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        // The background paints its own floor; the generic ground strip would cover it.
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }

        // The redrawn room uses the shared camera, so the priest is his usual size again (no setPriestScale)
        if (this.priest) {
            this.priest.x = 250;  // Match entrance position from Shed521FloorsScene
            this.priest.y = WALK_Y;
            this.priest.play('idle');
        }
        this.transitionManager = new SceneTransitionManager(this);

        // the whole left edge of the room: the stairwell door is just out of frame (its warm light falls on the floor)
        this.transitionManager.createEdgeExit('left', {
            target: 'Shed521FloorsScene', walkX: 67, walkY: WALK_Y, label: 'Back to the stairs', width: 140, top: 330
        });

        // The doorway in the back wall (canvas x 437..502 with its frame, y 293..416): the stair down to the Hall, lit
        // green from below; the threshold is in too
        this.transitionManager.createDoorZone({ rect: [437, 293, 65, 123] }, {
            target: 'ShedHallScene', walkX: 469, walkY: WALK_Y, label: 'To the Hall'
        });

        // The graffiti BETTER DECAY THAN CHANGE (canvas x 700..975, y 135..345, so its hover label clears the HUD; clear of Palinode's arch at x 639..685)
        this.createObservable(628, 240, 206, 210, () => {
            const lean = this.getGDTendency ? this.getGDTendency() : 'balanced';
            if (lean === 'decayDominant') return this.t('observe.office_graffiti.decay');
            if (lean === 'growthDominant') return this.t('observe.office_graffiti.growth');
            return this.t('observe.office_graffiti.default');
        }, { hint: this.t('observe.office_graffiti.hint'), bubble: { maxWidth: 300 } });
    }

    update() {
        super.update();
    }
}
