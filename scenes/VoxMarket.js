import GameScene from './GameScene.js';

export default class VoxMarket extends GameScene {
    constructor() {
        super({ key: 'VoxMarket' });
        this.isTransitioning = false; // Add flag to track transition state
    }

    get dialogContent() {
        return {
            ...super.dialogContent, // Include parent dialog content for symbiont dialogs
            // Add VoxMarket specific dialogs here if needed
        };
    }

    preload() {
        super.preload();
        this.load.image('voxMarketBg', 'assets/images/Voxmarket.png');
        this.load.image('exitArea', 'assets/images/door.png'); // Reusing door image for exit area
        // Audio is already loaded in GameScene's preload
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Play market theme
        this.playSceneMusic('marketTheme');
        
        // Set vox market background
        const bg = this.add.image(400, 200, 'voxMarketBg');
        bg.setDisplaySize(800, 750); // Further increased height to fully cover the ground
        bg.setDepth(-1);
        
        // Create a custom ground for the market scene
        this.createMarketGround();
        
        // Completely hide the original ground
        if (this.ground) {
            this.ground.destroy(); // Destroy instead of just hiding
        }
        
        // Add invisible clickable exit area at the left of the screen
        this.exitArea = this.add.image(50, 470, 'exitArea')
            .setDisplaySize(50, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);
        
        // Position the priest at the right side when entering this scene
        this.priest.x = 750;
        this.priest.y = 470; // Position on the ground
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }
        
        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
        
        // Exit area click logic
        this.exitArea.on('pointerdown', () => {
            // Move priest to exit area, then fade out
            const priest = this.priest;
            priest.play('walk');
            
            // Stop any existing tweens on the priest
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: 50,
                y: 470,
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('CrossroadScene');
                        this.isTransitioning = false; // Reset transition flag
                    });
                }
            });
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
        
        // Check if player is in exit area and not already transitioning
        if (this.priest && this.priest.x < 80 && !this.isTransitioning) {
            this.transitionToScene('CrossroadScene');
        }
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
