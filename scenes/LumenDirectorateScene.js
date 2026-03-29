import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class LumenDirectorateScene extends GameScene {
    constructor() {
        super({ key: 'LumenDirectorateScene' });
        this.isTransitioning = false;
    }

    preload() {
        super.preload();
        this.load.image('lumenDirectorateBg', 'assets/images/backgrounds/LumenDirectorate.png');
    }

    create() {
        super.create();
        this.playSceneMusic('genericMusic');

        const bg = this.add.image(400, 300, 'lumenDirectorateBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        this.transitionManager = new SceneTransitionManager(this);

        // Back to Town Square (right side)
        this.transitionManager.createTransitionZone(
            750,
            300,
            80,
            400,
            'right',
            'TownSquareScene',
            100,
            300,
        );

        // Enter the Lumen Directorate interior
        this.transitionManager.createTransitionZone(
            400,
            250,
            150,
            80,
            'up',
            'LumenDirectorateInteriorScene',
            400,
            450,
        );

        // Position the priest
        this.priest.x = 400;
        this.priest.y = 450;

        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        this.cameras.main.fadeIn(800, 0, 0, 0);

        // Show arrival notification
        this.time.delayedCall(500, () => {
            this.showNotification('Lumen Directorate Headquarters', 0x556B2F);
        });
    }

    update() {
        super.update();
    }
}

if (typeof window !== 'undefined') {
    window.LumenDirectorateScene = LumenDirectorateScene;
}

export { LumenDirectorateScene };
