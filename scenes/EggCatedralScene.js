import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class EggCatedralScene extends GameScene {
    constructor() {
        super({ key: 'EggCatedralScene' });
        this.isTransitioning = false; // Add flag to track transition state
    }

    preload() {
        super.preload();
        this.load.image('eggCatedralBg', 'assets/images/egg-catedral.png');
        this.load.image('door', 'assets/images/door.png'); // Placeholder transparent image for clickable door
        this.load.image('box', 'assets/images/box.png'); // Load the box asset
        // Audio is already loaded in GameScene's preload
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
            340  // walk to y (slightly below door center)
        );
        
        // Right border transition to CrossroadScene
        this.transitionManager.createTransitionZone(
            780, // x position
            470, // y position
            40,  // width
            200, // height
            'right', // direction
            'CrossroadScene', // target scene
            780, // walk to x
            470  // walk to y
        );
        
        // Left border transition to EntryScene
        this.transitionManager.createTransitionZone(
            50,  // x position
            470, // y position
            40,  // width
            200, // height
            'left', // direction
            'EntryScene', // target scene
            50,  // walk to x
            470  // walk to y
        );
        
        // Add box on the ground (visible, clickable)
        this.box = this.add.image(300, 520, 'box');
        this.box.setDisplaySize(48, 48);
        this.box.setDepth(5);
        this.box.setInteractive({ useHandCursor: true });
        this.box.on('pointerdown', () => {
            // Add box to inventory if not already present
            const boxItem = {
                id: 'box',
                name: 'Wooden Box',
                description: 'A mysterious wooden box. What could be inside?',
                spriteKey: 'box',
                stackable: false
            };
            if (this.addItemToInventory) {
                const inventory = this.registry.get('inventory');
                const alreadyInInventory = inventory.items.some(item => item.id === 'box');
                if (!alreadyInInventory) {
                    this.addItemToInventory(boxItem);
                    // Hide box from scene after picking up
                    this.box.setVisible(false);
                }
            }
        });

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
