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
        this.load.image('exitArea', 'assets/images/ui/door.png'); // Reusing door image for exit area
        // Audio is already loaded in GameScene's preload
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Play market theme
        this.playSceneMusic('marketTheme');
        
        // Set vox market background
        const bg = this.add.image(400, 200, 'Shed521GateBg');
        bg.setDisplaySize(800, 750); // Further increased height to fully cover the ground
        bg.setDepth(-1);
        
        // Create a custom ground for the market scene
        this.createMarketGround();
        
        // Completely hide the original ground
        if (this.ground) {
            this.ground.destroy(); // Destroy instead of just hiding
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
    
    // Create a custom ground for the market scene that matches the aesthetic
    createMarketGround() {
        // Remove the original ground if it exists
        if (this.ground) {
            this.ground.destroy();
        }
        
        // Create a graphics object for the ground
        const groundGraphics = this.add.graphics();
        
        // Set the ground dimensions
        const groundWidth = 800;
        const groundHeight = 160;
        const groundY = 500;
        
        // Fill with dark greenish-gray base color to match market floor
        groundGraphics.fillStyle(0x1a2420, 1);
        groundGraphics.fillRect(0, groundY, groundWidth, groundHeight);
        
        // Add some texture with lines
        groundGraphics.lineStyle(1, 0x283c32, 0.3);
        
        // Horizontal lines for floor boards
        for (let i = 0; i < 10; i++) {
            const y = groundY + Math.random() * groundHeight;
            groundGraphics.beginPath();
            groundGraphics.moveTo(0, y);
            groundGraphics.lineTo(groundWidth, y);
            groundGraphics.closePath();
            groundGraphics.strokePath();
        }
        
        // Vertical lines for texture
        for (let i = 0; i < 20; i++) {
            const x = Math.random() * groundWidth;
            groundGraphics.beginPath();
            groundGraphics.moveTo(x, groundY);
            groundGraphics.lineTo(x, groundY + groundHeight);
            groundGraphics.closePath();
            groundGraphics.strokePath();
        }
        
        // Add green glowing particles to match the market atmosphere
        for (let i = 0; i < 50; i++) {
            const x = Math.random() * groundWidth;
            const y = groundY + Math.random() * (groundHeight - 10);
            const size = Math.random() * 3 + 1;
            
            const particle = this.add.circle(x, y, size, 0x32ff64, 0.3);
            particle.setDepth(1);
            
            // Add pulsating effect to some particles
            if (Math.random() > 0.7) {
                this.tweens.add({
                    targets: particle,
                    alpha: 0.1,
                    duration: 1500 + Math.random() * 1000,
                    yoyo: true,
                    repeat: -1,
                    ease: 'Sine.easeInOut'
                });
            }
        }
        
        // Set the ground depth
        groundGraphics.setDepth(0);
    }
}
