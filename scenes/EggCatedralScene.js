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
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set egg cathedral background
        const bg = this.add.image(400, 300, 'eggCatedralBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Start cathedral theme
        this.playSceneMusic('cathedralTheme');
        
        // Create transition zones using SceneTransitionManager
        
        // Cathedral entrance door transition
        this.transitionManager.createTransitionZone(
            450, // x position
            300, // y position
            100, // width
            120, // height
            'up', // direction
            'CathedralEntrance', // target scene
            450, // walk to x
            340, // walk to y (slightly below door center)
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
