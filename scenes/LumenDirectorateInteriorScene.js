import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class LumenDirectorateInteriorScene extends GameScene {
    constructor() {
        super({ key: 'LumenDirectorateInteriorScene' });
        this.isTransitioning = false;
    }

    preload() {
        super.preload();
        this.load.image('lumenInteriorBg', 'assets/images/backgrounds/LumenDirectorateInterior.png');
    }

    create() {
        super.create();
        this.playSceneMusic('genericMusic');

        const bg = this.add.image(400, 300, 'lumenInteriorBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        this.transitionManager = new SceneTransitionManager(this);

        // Exit back to Lumen Directorate exterior
        this.transitionManager.createTransitionZone(
            400,
            550,
            200,
            50,
            'down',
            'LumenDirectorateScene',
            400,
            350,
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
            this.showNotification('Lumen Directorate — Interior', 0x556B2F);
        });

        // NPC will be added later when assets are provided
    }

    update() {
        super.update();
    }
}

if (typeof window !== 'undefined') {
    window.LumenDirectorateInteriorScene = LumenDirectorateInteriorScene;
}

export { LumenDirectorateInteriorScene };
