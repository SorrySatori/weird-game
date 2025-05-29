import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class VoxmarketHallScene extends GameScene {
    constructor() {
        super({ key: 'VoxmarketHallScene' });
        this.isTransitioning = false; // Add flag to track transition state
    }

    get dialogContent() {
        return {
            ...super.dialogContent, // Include parent dialog content for symbiont dialogs
            // Add VoxmarketHall specific dialogs here if needed
        };
    }

    preload() {
        super.preload();
        this.load.image('voxmarketHallBg', 'assets/images/VoxmarketHall.png');
        this.load.image('arrow', 'assets/images/door.png'); // Arrow for transition zones
        // Audio is already loaded in GameScene's preload
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Play market theme
        this.playSceneMusic('marketTheme');
        
        // Set voxmarket hall background
        const bg = this.add.image(400, 300, 'voxmarketHallBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Create a custom ground for the hall scene
        this.createHallGround();
        
        // Completely hide the original ground
        if (this.ground) {
            this.ground.destroy(); // Destroy instead of just hiding
        }
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Position the priest at the left when entering this scene
        this.priest.x = 100;
        this.priest.y = 470; // Position on the ground
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }
        
        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
        
        // Create exit to VoxMarket at the left edge
        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            50, // width
            200, // height
            'left', // direction
            'VoxMarket', // target scene
            100, // walk to x
            470 // walk to y
        );
        
        // Add a hint about the exit
        const exitHint = this.add.text(100, 420, 'Back to Main Market', {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        exitHint.setOrigin(0.5);
        exitHint.setAlpha(0);
        exitHint.setDepth(10);
        
        // Show hint when hovering near the exit
        this.input.on('pointermove', (pointer) => {
            // Check if pointer is near the exit area
            if (Math.abs(pointer.x - 50) < 50 && Math.abs(pointer.y - 470) < 100) {
                exitHint.setAlpha(1);
            } else {
                exitHint.setAlpha(0);
            }
        });
        
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
    
    // Create a custom ground for the hall scene that matches the aesthetic
    createHallGround() {
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
        
        // Fill with dark reddish-brown base color to match hall floor
        groundGraphics.fillStyle(0x2a1a18, 1);
        groundGraphics.fillRect(0, groundY, groundWidth, groundHeight);
        
        // Add some texture with lines
        groundGraphics.lineStyle(1, 0x3c2824, 0.3);
        
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
        
        // Add subtle glowing particles to match the hall atmosphere
        for (let i = 0; i < 30; i++) {
            const x = Math.random() * groundWidth;
            const y = groundY + Math.random() * (groundHeight - 10);
            const size = Math.random() * 2 + 1;
            
            const particle = this.add.circle(x, y, size, 0xcc6644, 0.2);
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
