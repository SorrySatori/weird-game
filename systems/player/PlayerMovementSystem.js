/**
 * PlayerMovementSystem.js
 * Handles player character movement, animations, and related functionality
 */
/** how close to the screen edge the arrow keys let the priest walk (his body stays in the picture) */
const EDGE_MARGIN = 28;
/** walking toward an edge this close to it takes the exit on that side (the physics world bounds may stop him earlier) */
const EDGE_EXIT_BAND = 72;

export default class PlayerMovementSystem {
    /**
     * @param {Phaser.Scene} scene - The scene this system belongs to
     */
    constructor(scene) {
        this.scene = scene;
        this.priest = null;
        this.priestGlow = null;
        this.speed = 4;
        // Multiplier applied to walk speed (arrow-key step + click-to-move tween). Drug/status
        // effects (e.g. the Wimlick stimulant) raise this; reset to 1 when the effect wears off.
        this.speedMultiplier = 1;
        this.movementState = {
            left: false,
            right: false,
            up: false,
            down: false
        };
        this.isMoving = false;
        this.isTweenMoving = false; // true while a click-to-move tween is running
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
        // The ESC menu is open: its arrows / Enter drive the menu, not the priest
        return !!this.scene.gameMenu?.visible;
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
        
        this.priest.setScale(direction, 1);
        if (this.priestGlow) {
            this.priestGlow.setScale(1.05 * direction, 1.05);
            this.priestGlow.x = this.priest.x;
        }
        
        // Stop any existing tweens
        this.scene.tweens.killTweensOf(this.priest);
        if (this.priestGlow) {
            this.scene.tweens.killTweensOf(this.priestGlow);
        }
        
        // Play walk animation (flag it so update() doesn't cancel it back to idle each frame)
        this.isTweenMoving = true;
        this.priest.play('walk', true); // Force restart the animation

        // Create new tween
        this.scene.tweens.add({
            targets: this.priestGlow ? [this.priest, this.priestGlow] : [this.priest],
            x: targetX,
            duration: Math.abs(targetX - this.priest.x) * 5 / (this.speedMultiplier || 1),
            ease: 'Linear',
            onComplete: () => {
                this.isTweenMoving = false;
                this.priest.play('idle', true); // Force restart the animation
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
        const leaving = this.scene.isTransitioning;            // an exit is walking him out: keys don't steer

        const step = this.speed * (this.speedMultiplier || 1);
        if (leaving) {
            // nothing
        } else if (this.movementState.left) {
            this.priest.x -= step;
            this.priest.setScale(-1, 1);
            this.priestGlow.setScale(-1.05, 1.05);
            moved = true;
        }
        else if (this.movementState.right) {
            this.priest.x += step;
            this.priest.setScale(1, 1);
            this.priestGlow.setScale(1.05, 1.05);
            moved = true;
        }

        // The screen edges: the arrows stop him there -- or, where an exit lies on that side, he leaves by it
        if (moved) {
            const W = this.scene.scale.width;
            this.priest.x = Phaser.Math.Clamp(this.priest.x, EDGE_MARGIN, W - EDGE_MARGIN);
            const side = this.movementState.left && this.priest.x <= EDGE_EXIT_BAND ? 'left'
                : this.movementState.right && this.priest.x >= W - EDGE_EXIT_BAND ? 'right' : null;
            if (side && this.scene.takeEdgeExit?.(side, this.priest.y)) {
                this.movementState.left = false;
                this.movementState.right = false;
                moved = false;
            }
        }

        // Update animations
        if (moved) {
            if (!this.priest.anims.isPlaying || this.priest.anims.currentAnim.key !== 'walk') {
                this.priest.play('walk');
            }
        } else if (!this.isTweenMoving && this.priest.anims.currentAnim && this.priest.anims.currentAnim.key === 'walk') {
            this.priest.play('idle');
        }

        // Update visual effects
        if (this.priestGlow && this.priest) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
            // Some scenes anchor the priest at the feet (setOrigin(0.5, 1)); the glow is a second
            // sprite of the same texture, so it must share the origin or it renders half a body
            // lower as a ghostly silhouette. Keep them in sync here, centrally.
            if (this.priestGlow.originX !== this.priest.originX || this.priestGlow.originY !== this.priest.originY) {
                this.priestGlow.setOrigin(this.priest.originX, this.priest.originY);
            }
            // ...and the same pose, or a still idle silhouette ghosts behind the walking legs
            if (this.priestGlow.frame.name !== this.priest.frame.name) this.priestGlow.setFrame(this.priest.frame.name);
        }
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
