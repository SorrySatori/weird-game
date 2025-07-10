/**
 * PlayerMovementSystem.js
 * Handles player character movement, animations, and related functionality
 */
export default class PlayerMovementSystem {
    /**
     * @param {Phaser.Scene} scene - The scene this system belongs to
     */
    constructor(scene) {
        this.scene = scene;
        this.priest = null;
        this.priestGlow = null;
        this.speed = 4;
        this.movementState = {
            left: false,
            right: false,
            up: false,
            down: false
        };
        this.isMoving = false;
        this.dialogVisible = false;
        this.controlsDisabled = false;
    }

    /**
     * Initialize the player movement system
     * @param {Phaser.GameObjects.Sprite} priest - The player character sprite
     * @param {Phaser.GameObjects.Sprite} priestGlow - The glow effect for the player character
     */
    init(priest, priestGlow) {
        this.priest = priest;
        this.priestGlow = priestGlow;
        this.setupKeyboardControls();
        this.setupMouseControls();
    }

    /**
     * Set up keyboard controls for player movement
     */
    setupKeyboardControls() {
        // Set up keyboard input
        this.scene.input.keyboard.on('keydown-LEFT', () => {
            if (!this.dialogVisible && !this.isInteractingWithUI()) {
                this.movementState.left = true;
            }
        });
        this.scene.input.keyboard.on('keyup-LEFT', () => {
            this.movementState.left = false;
        });

        this.scene.input.keyboard.on('keydown-RIGHT', () => {
            if (!this.dialogVisible && !this.isInteractingWithUI()) {
                this.movementState.right = true;
            }
        });
        this.scene.input.keyboard.on('keyup-RIGHT', () => {
            this.movementState.right = false;
        });

        this.scene.input.keyboard.on('keydown-UP', () => {
            if (!this.dialogVisible && !this.isInteractingWithUI()) {
                this.movementState.up = true;
            }
        });
        this.scene.input.keyboard.on('keyup-UP', () => {
            this.movementState.up = false;
        });

        this.scene.input.keyboard.on('keydown-DOWN', () => {
            if (!this.dialogVisible && !this.isInteractingWithUI()) {
                this.movementState.down = true;
            }
        });
        this.scene.input.keyboard.on('keyup-DOWN', () => {
            this.movementState.down = false;
        });
    }

    /**
     * Set up mouse controls for player movement
     */
    setupMouseControls() {
        // Add click/tap handler for movement
        this.scene.input.on('pointerdown', (pointer) => {
            if (!this.dialogVisible && pointer.y < 500 && !this.isInteractingWithUI()) {
                const targetX = pointer.x;
                this.movePriestTo(targetX);
            }
        });
    }

    /**
     * Check if the player is interacting with UI elements
     * @returns {boolean} True if interacting with UI, false otherwise
     */
    isInteractingWithUI() {
        // This is a placeholder - the actual implementation would check if the player
        // is clicking on UI elements, which would require access to the UI elements
        return false;
    }

    /**
     * Move the priest character to a specific x position
     * @param {number} targetX - The target x position
     */
    movePriestTo(targetX) {
        if (!this.priest || this.dialogVisible) return;
        
        const direction = targetX < this.priest.x ? -1 : 1;
        
        // Play click sound if available
        if (this.scene.clickSound) {
            this.scene.clickSound.play();
        }
        
        this.priest.setScale(2 * direction, 2);
        this.priestGlow.setScale(2.1 * direction, 2.1);
        this.priestGlow.x = this.priest.x;
        this.priest.play('walk');
        
        this.scene.tweens.add({
            targets: [this.priest, this.priestGlow],
            x: targetX,
            duration: Math.abs(targetX - this.priest.x) * 5,
            ease: 'Linear',
            onComplete: () => {
                this.priest.play('idle');
            }
        });
    }

    /**
     * Disable player controls for cutscenes or dialog sequences
     */
    disableControls() {
        // Reset all movement states
        this.movementState.left = false;
        this.movementState.right = false;
        this.movementState.up = false;
        this.movementState.down = false;
        
        // Set a flag that controls are disabled
        this.controlsDisabled = true;
    }
    
    /**
     * Enable player controls after cutscenes or dialog sequences
     */
    enableControls() {
        this.controlsDisabled = false;
    }

    /**
     * Update method to be called in the scene's update loop
     */
    update() {
        if (!this.priest || this.dialogVisible || this.controlsDisabled) return;
        
        let moved = false;

        if (this.movementState.left) {
            this.priest.x -= this.speed;
            this.priest.setScale(-2, 2);
            this.priestGlow.setScale(-2.1, 2.1);
            moved = true;
        } 
        else if (this.movementState.right) {
            this.priest.x += this.speed;
            this.priest.setScale(2, 2);
            this.priestGlow.setScale(2.1, 2.1);
            moved = true;
        }

        // Update animations
        if (moved) {
            if (!this.priest.anims.isPlaying || this.priest.anims.currentAnim.key !== 'walk') {
                this.priest.play('walk');
            }
        } else if (this.priest.anims.currentAnim && this.priest.anims.currentAnim.key === 'walk') {
            this.priest.play('idle');
        }

        // Update visual effects
        this.priestGlow.x = this.priest.x;
        this.priestGlow.y = this.priest.y;
    }

    /**
     * Set the dialog visibility state
     * @param {boolean} visible - Whether dialog is visible
     */
    setDialogVisible(visible) {
        this.dialogVisible = visible;
    }

    /**
     * Clean up resources when the system is no longer needed
     */
    cleanup() {
        // Remove event listeners
        this.scene.input.keyboard.off('keydown-LEFT');
        this.scene.input.keyboard.off('keyup-LEFT');
        this.scene.input.keyboard.off('keydown-RIGHT');
        this.scene.input.keyboard.off('keyup-RIGHT');
        this.scene.input.keyboard.off('keydown-UP');
        this.scene.input.keyboard.off('keyup-UP');
        this.scene.input.keyboard.off('keydown-DOWN');
        this.scene.input.keyboard.off('keyup-DOWN');
        
        // Clear references
        this.priest = null;
        this.priestGlow = null;
        this.scene = null;
    }
}
