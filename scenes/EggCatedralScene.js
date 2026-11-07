import { notePlace } from '../utils/places.js';
import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class EggCatedralScene extends GameScene {
    constructor() {
        super({ key: 'EggCatedralScene' });
        this.isTransitioning = false; // Add flag to track transition state
    }

    preload() {
        super.preload();
        this.load.image('eggCatedralBg', 'assets/images/backgrounds/egg-catedral.png');
        this.load.image('door', 'assets/images/ui/door.png'); // Placeholder transparent image for clickable door
        this.load.audio('cathedralSoundtrack', 'assets/sounds/cathedral.mp3'); // shared with CathedralEntrance
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        notePlace(this, 'place_egg_cathedral');   // the journal's Places tab, on the first visit
        
        // Set egg cathedral background
        const bg = this.add.image(400, 300, 'eggCatedralBg');
        this.fitBackground(bg);
        bg.setDepth(-1);

        // The redrawn background (1067×600) paints its own meadow and path, so drop the generic floor strip.
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Cathedral soundtrack — continues seamlessly into/out of CathedralEntrance
        this.playSceneMusic('cathedralSoundtrack', { resume: true });
        
        // Create transition zones using SceneTransitionManager
        
        // Cathedral entrance door transition — the small glowing door at the top of the steps,
        // far away in the middle of the picture. The priest walks up the path on the ground line.
        this.transitionManager.createTransitionZone(
            400, // x position (800-space; remapped to the canvas centre)
            390, // y position
            26,  // width
            50,  // height
            'up', // direction
            'CathedralEntrance', // target scene
            400, // walk to x
            470, // walk to y (stay on the ground line in front of the steps)
            'Cathedral Interior' // destination name
        );
        
        // Right border transition to CrossroadScene
        this.transitionManager.createTransitionZone(
            780, // x position
            470, // y position
            40,  // width
            200, // height
            'right', // direction
            'CrossroadScene', // target scene
            100, // walk to x
            470, // walk to y
            'Crossroads' // destination name
        );

        // Examine: the whole Egg Cathedral, anchored to its towers and spires. The bubble auto-flips
        // below it (tail up) so it clears the top HUD. Clear of the entrance-door transition (y≈365-415).
        this.createObservable(400, 145, 150, 210, () => this.t('observe.egg_cathedral_approach.default'),
            { hint: this.t('observe.egg_cathedral_approach.hint'), overObject: true });
        
        // Left transition removed - no going back to EntryScene
        // The Fungal Master has left and the apprentice's journey continues forward
    }
    

    update() {
        // Call parent update for all standard mechanics
        super.update();
        
        // No need for manual transition checks anymore as SceneTransitionManager handles this
    }

    shutdown() {
        // Restore background music when leaving the scene
        this.restoreBackgroundMusic();
        super.shutdown();
    }
}
