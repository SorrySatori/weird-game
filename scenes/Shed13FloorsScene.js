import GameScene from './GameScene.js';

export default class Shed13FloorsScene extends GameScene {
    constructor() {
        super({ key: 'Shed13FloorsScene' });
        this.isTransitioning = false; // Add flag to track transition state
        this.currentFloor = 1; // Track current floor: 1, 2, or 3
    }

    preload() {
        super.preload();
        this.load.image('floors', 'assets/images/backgrounds/Shed13_floors.png');
        this.load.image('door', 'assets/images/ui/door.png'); // Placeholder transparent image for clickable door
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set initial priest position to first floor
        if (this.priest) {
            this.priest.x = 400;  // Center of the scene
            this.priest.y = 520;  // Adjusted ground level (first floor)
            this.priest.setOrigin(0.5, 1);  // Ensure origin is at feet
            this.priest.play('idle');
        }

        // Set crossroad background
        const bg = this.add.image(400, 300, 'floors');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Add invisible clickable area for Shed13 entrance
        this.welcomeEntrance = this.add.image(110, 450, 'door')
            .setDisplaySize(120, 100)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });

        this.secondFloorEntrance = this.add.image(650, 450, 'door')
            .setDisplaySize(100, 100)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });

        this.exitEntrance = this.add.image(450, 450, 'door')
            .setDisplaySize(100, 100)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });

        // --- Hidden entrance to third floor ---
        this.thirdFloorEntrance = this.add.image(690, 250, 'door')
            .setDisplaySize(80, 80)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });

        // --- Entrance back to first floor ---
        this.secondToFirstEntrance = this.add.image(400, 340, 'door')
            .setDisplaySize(80, 80)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });

        this.assessmentEntrance = this.add.image(200, 340, 'door')
            .setDisplaySize(80, 80)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });

        // --- Entrance back to second floor ---
        this.thirdToSecondEntrance = this.add.image(690, 120, 'door')
            .setDisplaySize(80, 80)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });

            this.registrationEntrance = this.add.image(150, 120, 'door')
            .setDisplaySize(80, 80)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });

            this.applicationsEntrance = this.add.image(400, 120, 'door')
            .setDisplaySize(80, 80)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });

        // Set up pointer events for all entrances
        const entrances = [
            this.welcomeEntrance,
            this.secondFloorEntrance,
            this.exitEntrance,
            this.thirdFloorEntrance,
            this.secondToFirstEntrance,
            this.thirdToSecondEntrance,
            this.assessmentEntrance,
            this.registrationEntrance,
            this.applicationsEntrance
        ];

        entrances.forEach(entrance => {
            entrance.on('pointerover', () => {
                if (entrance.input.enabled) {
                }
            });
            entrance.on('pointerout', () => {
            });
        });

        // Helper to update entrance availability based on current floor
        this.updateEntranceAvailability = (currentFloor) => {
            // Disable all entrances first
            [this.welcomeEntrance, this.exitEntrance, this.secondFloorEntrance, this.assessmentEntrance,
             this.thirdFloorEntrance, this.secondToFirstEntrance, this.thirdToSecondEntrance].forEach(entrance => {
                if (entrance) {
                    entrance.disableInteractive();
                    entrance.setAlpha(0);
                }
            });

            // Enable only entrances for current floor
            switch(currentFloor) {
                case 1:
                    this.welcomeEntrance.setInteractive({ useHandCursor: true }).setAlpha(0.01);
                    this.exitEntrance.setInteractive({ useHandCursor: true }).setAlpha(0.01);
                    this.secondFloorEntrance.setInteractive({ useHandCursor: true }).setAlpha(0.01);
                    break;
                case 2:
                    this.secondToFirstEntrance.setInteractive({ useHandCursor: true }).setAlpha(0.01);
                    this.thirdFloorEntrance.setInteractive({ useHandCursor: true }).setAlpha(0.01);
                    this.assessmentEntrance.setInteractive({ useHandCursor: true }).setAlpha(0.01);
                    break;
                case 3:
                    this.thirdToSecondEntrance.setInteractive({ useHandCursor: true }).setAlpha(0.01);
                    break;
            }
        };

        // Initial entrance setup
        this.updateEntranceAvailability(1);

        this.thirdFloorEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            // First move to the entrance
            this.tweens.add({
                targets: priest,
                x: 690,
                y: 340, // Second floor height
                duration: 800,
                onComplete: () => {
                    // Then teleport to third floor after a delay
                    this.time.delayedCall(200, () => {
                        priest.y = this.getThirdFloorY(690);
                        this.cameras.main.flash(300, 127, 255, 142);
                        priest.play('idle');
                        this.updateEntranceAvailability(3);
                        this.time.delayedCall(400, () => {
                            this.isTransitioning = false;
                        });
                    });
                }
            });
        });

        this.secondToFirstEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            // First move to the entrance
            this.tweens.add({
                targets: priest,
                x: 400,
                y: 340, // Second floor height
                duration: 800,
                onComplete: () => {
                    // Then teleport to first floor after a delay
                    this.time.delayedCall(200, () => {
                        priest.y = 520;
                        this.cameras.main.flash(300, 127, 255, 142);
                        priest.play('idle');
                        this.updateEntranceAvailability(1);
                        this.time.delayedCall(400, () => {
                            this.isTransitioning = false;
                        });
                    });
                }
            });
        });

        this.assessmentEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            // First move to the entrance
            this.tweens.add({
                targets: priest,
                x: 200,
                y: 340, // Second floor height
                duration: 800,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('ShedAbandonedOfficeScene');
                        this.isTransitioning = false;
                    });
                }
            });
        });

        this.registrationEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            // First move to the entrance
            this.tweens.add({
                targets: priest,
                x: 690,
                y: this.getThirdFloorY(690),
                duration: 800,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('ShedRegistrationScene');
                        this.isTransitioning = false;
                    });
                }
            });
        });

        this.applicationsEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            // First move to the entrance
            this.tweens.add({
                targets: priest,
                x: 690,
                y: this.getThirdFloorY(690),
                duration: 800,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('ShedApplicationsScene');
                        this.isTransitioning = false;
                    });
                }
            });
        });

        this.thirdToSecondEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            // First move to the entrance
            this.tweens.add({
                targets: priest,
                x: 690,
                y: this.getThirdFloorY(690),
                duration: 800,
                onComplete: () => {
                    // Then teleport to second floor after a delay
                    this.time.delayedCall(200, () => {
                        priest.x = 400;
                        priest.y = 340;
                        this.cameras.main.flash(300, 127, 255, 142);
                        priest.play('idle');
                        this.updateEntranceAvailability(2);
                        this.time.delayedCall(400, () => {
                            this.isTransitioning = false;
                        });
                    });
                }
            });
        });

        // Second floor entrance click logic
        this.secondFloorEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            // First move to the entrance
            this.tweens.add({
                targets: priest,
                x: 650,
                y: 520,
                duration: 800,
                onComplete: () => {
                    // Then teleport to second floor after a delay
                    this.time.delayedCall(200, () => {
                        priest.x = 400;
                        priest.y = 340;
                        this.cameras.main.flash(300, 127, 255, 142);
                        priest.play('idle');
                        this.updateEntranceAvailability(2);
                        this.time.delayedCall(400, () => {
                            this.isTransitioning = false;
                        });
                    });
                }
            });
        });

        // Draw walkable straight line (platform) on second floor
        this.secondFloorPlatform = this.add.graphics();
        // Use background-matching color and subtle opacity
        this.secondFloorPlatform.fillStyle(0x1a2420, 0.7); // Match dark greenish-gray, slightly transparent
        this.secondFloorPlatform.fillRect(0, 340, 800, 8); // x, y, width, height
        this.secondFloorPlatform.setDepth(2);

        // Optionally, add physics body for collision (if priest uses arcade physics)
        if (this.physics && this.priest && this.physics.add) {
            this.physics.add.existing(this.secondFloorPlatform, true);
            this.physics.add.collider(this.priest, this.secondFloorPlatform);
        }

        // Ensure priest's anchor is at the feet (center-bottom)
        if (this.priest && this.priest.setOrigin) {
            this.priest.setOrigin(0.5, 1);
        }

        // Exit entrance click logic
        this.exitEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: 100,
                y: 520, // Ground level
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('Shed13Scene');
                    });
                }
            });
        });

        // Welcome entrance click logic
        this.welcomeEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: 650,
                y: 520, // Ground level
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('Shed13GateScene');
                    });
                }
            });
        });
    }
    

    // Helper: returns y for the third floor surface at given x
    getThirdFloorY(x) {
        console.log('x:', x);
        // Left segment: flat
        if (x < 100) {
            // Move priest to first floor (ground level)
            const priest = this.priest;
            this.tweens.killTweensOf(priest);

            priest.x = 400;
            priest.y = 340;
            priest.play('idle');
            this.cameras.main.flash(300, 127, 255, 142);
            this.time.delayedCall(400, () => {
                this.isTransitioning = false;
            });
            return 250;
        } 
        else if (x < 350) {
            return 185;
        } 
        // Step up: vertical
        else if (x < 400) {
            return 180 - ((x - 540) / 20) * 24;
        }
        // Right segment: flat
        return 156;
    }

    update() {
        super.update();
        
        // Check if player is at the right edge of the screen
        if (this.priest && this.priest.x > 780 && !this.isTransitioning) {
            this.isTransitioning = true;
            this.priest.play('idle');
            this.cameras.main.fadeOut(800, 0, 0, 0);
            this.cameras.main.once('camerafadeoutcomplete', () => {
                this.scene.start('VoxMarket');
                this.isTransitioning = false; // Reset transition flag
            });
        }

        // --- Only adjust priest y to third floor surface when actually on third floor ---
        if (
            this.priest &&
            this.priest.x >= 0 && this.priest.x <= 800 &&
            this.priest.y >= 140 && this.priest.y <= 200 // Only when near third floor
        ) {
            const targetY = this.getThirdFloorY(this.priest.x);
            if (Math.abs(this.priest.y - targetY) < 40) {
                this.priest.y = targetY;
            }
        }
    }
}

// If you ever set priest.x to a third floor position at scene start or elsewhere,
// also set priest.y = this.getThirdFloorY(priest.x);
