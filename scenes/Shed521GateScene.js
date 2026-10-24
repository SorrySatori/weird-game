import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class Shed521GateScene extends GameScene {
    constructor() {
        super({ key: 'Shed521GateScene' });
        this.isTransitioning = false; // Add flag to track transition state
    }

    preload() {
        super.preload();
        this.load.image('Shed521GateBg', 'assets/images/backgrounds/Shed521_gate.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        // Audio is already loaded in GameScene's preload
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Play market theme
        this.playSceneMusic('marketTheme');
        
        // The gate yard (native 1067×600: tools/artgen/gate_bg.py — the queue for mutation forms, the Floors door on the right)
        const bg = this.add.image(this.scale.width / 2, 300, 'Shed521GateBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        
        // The background paints the yard's setts; drop the generic ground strip
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }
        
        // Position the priest at the right side when entering this scene
        this.priest.x = 750;
        this.priest.y = 470; // Position on the ground
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }
        
        // Create transition zones using SceneTransitionManager
        
        // Exit to Floors Scene (right side of the screen)
        this.floorsZone = this.transitionManager.createTransitionZone(
            750, // x position
            470, // y position
            50,  // width
            200, // height
            'right', // direction
            'Shed521FloorsScene', // target scene
            750, // walk to x
            470  // walk to y
        );
        
        // Exit to Courtyard Scene (left side of the screen)
        this.courtyardZone = this.transitionManager.createTransitionZone(
            50,  // x position
            470, // y position
            50,  // width
            200, // height
            'left', // direction
            'ShedCourtyard', // target scene
            50,  // walk to x
            470  // walk to y
        );
        
        // Remove the NPC if it exists
        if (this.stranger) {
            this.stranger.destroy();
        }
    }

    shutdown() {
        // Restore background music when leaving the scene
        this.restoreBackgroundMusic();
        super.shutdown();
    }

    update() {
        // Call parent update for all standard mechanics
        super.update();
    }
    
    shutdown() {
        this.restoreBackgroundMusic();
        super.shutdown();
    }
}
