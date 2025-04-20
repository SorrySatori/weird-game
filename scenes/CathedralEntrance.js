class CathedralEntrance extends GameScene {
    constructor() {
        super({ key: 'CathedralEntrance' });
        this.isTransitioning = false; // Add flag to track transition state
    }

    preload() {
        super.preload();
        this.load.image('cathedralEntranceBg', 'assets/images/CathedralEntrance.png');
        this.load.image('exitArea', 'assets/images/door.png'); // Reusing door image for exit area
    }

    create() {
        // Call parent create but skip city background creation
        this.createCityBackground = () => {}; // Temporarily override to do nothing
        super.create(); // This will call all the mechanics setup but with empty city background
        this.createCityBackground = GameScene.prototype.createCityBackground; // Restore original function
        
        // Set cathedral entrance background
        const bg = this.add.image(400, 300, 'cathedralEntranceBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Add invisible clickable exit area at the bottom of the screen
        this.exitArea = this.add.image(400, 550, 'exitArea')
            .setDisplaySize(800, 50)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);
        
        // Position the priest at the bottom center when entering this scene
        this.priest.x = 400;
        this.priest.y = 470; // Position on the ground
        
        // Update priest's staff position
        this.updateStaffPosition(1);
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }
        
        // Exit area click logic
        this.exitArea.on('pointerdown', () => {
            // Move priest to exit area, then fade out
            const priest = this.priest;
            priest.play('walk');
            
            // Stop any existing tweens on the priest
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: 400,
                y: 550,
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('EggCatedralScene');
                    });
                }
            });
        });
        
        // Remove the NPC if it exists
        if (this.stranger) {
            this.stranger.destroy();
        }
    }

    update() {
        // Call parent update for all standard mechanics
        super.update();
        
        // Check if player is in exit area and not already transitioning
        if (this.priest && this.priest.y > 525 && !this.isTransitioning) {
            this.isTransitioning = true; // Set flag to prevent multiple transitions
            
            // Stop any player movement
            this.priest.play('idle');
            
            this.cameras.main.fadeOut(800, 0, 0, 0);
            this.cameras.main.once('camerafadeoutcomplete', () => {
                this.scene.start('EggCatedralScene');
            });
        }
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.CathedralEntrance = CathedralEntrance;
}
