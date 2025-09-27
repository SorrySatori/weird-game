import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class Shed521FloorsScene extends GameScene {
    constructor() {
        super({ key: 'Shed521FloorsScene' });
        this.isTransitioning = false; // Add flag to track transition state
        this.currentFloor = 1; // Track current floor: 1, 2, or 3
    }

    preload() {
        super.preload();
        this.load.image('floors', 'assets/images/backgrounds/Shed521_floors.png');
        this.load.image('door', 'assets/images/ui/door.png'); // Placeholder transparent image for clickable door
        this.load.image('arrow', 'assets/images/ui/arrow.png'); // Arrow for transition hover effects
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
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
        
        // Create transition zones for each area using SceneTransitionManager
        
        // First Floor Transitions
        
        // Welcome Office (First Floor - Left)
        this.welcomeZone = this.transitionManager.createTransitionZone(
            110, // x position
            450, // y position
            120, // width
            100, // height
            'left', // direction
            'Shed521GateScene', // target scene
            50, // walk to x
            520 // walk to y
        );
        
        // Exit to Shed521Scene (First Floor - Center)
        this.exitZone = this.transitionManager.createTransitionZone(
            450, // x position
            450, // y position
            100, // width
            100, // height
            'down', // direction
            'Shed521Scene', // target scene
            450, // walk to x
            450, // walk to y
            'Exit'
        );
        
        // Stairs to Second Floor (First Floor - Right)
        this.secondFloorZone = this.transitionManager.createTransitionZone(
            650, // x position
            450, // y position
            100, // width
            100, // height
            'up', // direction
            'Shed521FloorsScene', // target scene - same scene, different floor
            650, // walk to x
            450, // walk to y - second floor level,
            'To Second Floor'
        );
        
        // Second Floor Transitions
        
        // Assessment Office (Second Floor - Left)
        this.assessmentZone = this.transitionManager.createTransitionZone(
            200, // x position
            340, // y position
            80, // width
            80, // height
            'left', // direction
            'ShedAbandonedOfficeScene', // target scene
            150, // walk to x
            340 // walk to y
        );
        
        // Stairs to First Floor (Second Floor - Center)
        this.secondToFirstZone = this.transitionManager.createTransitionZone(
            400, // x position
            340, // y position
            80, // width
            80, // height
            'down', // direction
            'Shed521FloorsScene', // target scene - same scene, different floor
            400, // walk to x
            520, // walk to y - first floor level
            'Stairs to First Floor'
        );
        
        // Stairs to Third Floor (Second Floor - Right)
        this.thirdFloorZone = this.transitionManager.createTransitionZone(
            690, // x position
            250, // y position
            80, // width
            80, // height
            'up', // direction
            'Shed521FloorsScene', // target scene - same scene, different floor
            690, // walk to x
            250, // walk to y - third floor level
            'Stairs to Third Floor'
        );
        
        // Third Floor Transitions
        
        // Registration Office (Third Floor - Left)
        this.registrationZone = this.transitionManager.createTransitionZone(
            150, // x position
            120, // y position
            80, // width
            80, // height
            'left', // direction
            'ShedRegistrationScene', // target scene
            100, // walk to x
            120 // walk to y
        );
        
        // Applications Office (Third Floor - Center)
        this.applicationsZone = this.transitionManager.createTransitionZone(
            400, // x position
            120, // y position
            80, // width
            80, // height
            'up', // direction
            'ShedApplicationsScene', // target scene
            400, // walk to x
            120 // walk to y
        );
        
        // Stairs to Second Floor (Third Floor - Right)
        this.thirdToSecondZone = this.transitionManager.createTransitionZone(
            690, // x position
            120, // y position
            80, // width
            80, // height
            'down', // direction
            'Shed521FloorsScene', // target scene - same scene, different floor
            690, // walk to x
            120 // walk to y - second floor level
        );

        // Helper to update entrance availability based on current floor
        this.updateEntranceAvailability = (currentFloor) => {
            // Disable all transition zones first
            const allZones = [
                this.welcomeZone, this.exitZone, this.secondFloorZone,
                this.assessmentZone, this.secondToFirstZone, this.thirdFloorZone,
                this.thirdToSecondZone, this.registrationZone, this.applicationsZone
            ];
            
            allZones.forEach(zone => {
                if (zone && zone.input) {
                    zone.input.enabled = false;
                }
            });

            // Enable zones based on current floor
            switch (currentFloor) {
                case 1: // First floor
                    [this.welcomeZone, this.exitZone, this.secondFloorZone].forEach(zone => {
                        if (zone && zone.input) {
                            zone.input.enabled = true;
                        }
                    });
                    break;
                case 2: // Second floor
                    [this.assessmentZone, this.secondToFirstZone, this.thirdFloorZone].forEach(zone => {
                        if (zone && zone.input) {
                            zone.input.enabled = true;
                        }
                    });
                    break;
                case 3: // Third floor
                    [this.registrationZone, this.applicationsZone, this.thirdToSecondZone].forEach(zone => {
                        if (zone && zone.input) {
                            zone.input.enabled = true;
                        }
                    });
                    break;
            }
        };

        // Initialize with first floor entrances active
        this.updateEntranceAvailability(1);

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

        // Add custom transition handling for same-scene floor changes and external scene transitions
        
        // 1. FLOOR TRANSITIONS (same scene, different floors)
        
        // First to Second Floor
        this.secondFloorZone.off('pointerdown');
        this.secondFloorZone.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;
            
            const priest = this.priest;
            this.tweens.killTweensOf(priest);
            
            // First make the priest walk to the transition area
            const walkToX = this.secondFloorZone.x;
            
            // Play walking animation and move to transition area horizontally
            priest.play('walk');
            
            // Calculate walk duration based on horizontal distance only
            const distance = Math.abs(priest.x - walkToX);
            const walkDuration = distance * 4; // 4ms per pixel
            
            this.tweens.add({
                targets: priest,
                x: walkToX,
                // Keep the same Y position
                duration: walkDuration,
                ease: 'Linear',
                onComplete: () => {
                    // After reaching the transition area, teleport to second floor
                    priest.play('idle');
                    this.cameras.main.flash(300, 127, 255, 142); // Green flash effect
                    
                    // Short delay before teleporting
                    this.time.delayedCall(200, () => {
                        priest.x = 650;
                        priest.y = 340; // Second floor level
                        
                        this.currentFloor = 2;
                        this.updateEntranceAvailability(this.currentFloor);
                        
                        // Short delay before allowing new interactions
                        this.time.delayedCall(400, () => {
                            this.isTransitioning = false;
                        });
                    });
                }
            });
        });
        
        // Second to First Floor
        this.secondToFirstZone.off('pointerdown');
        this.secondToFirstZone.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;
            
            const priest = this.priest;
            this.tweens.killTweensOf(priest);
            
            // First make the priest walk to the transition area
            const walkToX = this.secondToFirstZone.x;
            
            // Play walking animation and move to transition area horizontally
            priest.play('walk');
            
            // Calculate walk duration based on horizontal distance only
            const distance = Math.abs(priest.x - walkToX);
            const walkDuration = distance * 4; // 4ms per pixel
            
            this.tweens.add({
                targets: priest,
                x: walkToX,
                // Keep the same Y position
                duration: walkDuration,
                ease: 'Linear',
                onComplete: () => {
                    // After reaching the transition area, teleport to first floor
                    priest.play('idle');
                    this.cameras.main.flash(300, 127, 255, 142); // Green flash effect
                    
                    // Short delay before teleporting
                    this.time.delayedCall(200, () => {
                        priest.x = 400;
                        priest.y = 520; // First floor level
                        
                        this.currentFloor = 1;
                        this.updateEntranceAvailability(this.currentFloor);
                        
                        // Short delay before allowing new interactions
                        this.time.delayedCall(400, () => {
                            this.isTransitioning = false;
                        });
                    });
                }
            });
        });
        
        // Second to Third Floor
        this.thirdFloorZone.off('pointerdown');
        this.thirdFloorZone.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;
            
            const priest = this.priest;
            this.tweens.killTweensOf(priest);
            
            // First make the priest walk to the transition area
            const walkToX = this.thirdFloorZone.x;
            
            // Play walking animation and move to transition area horizontally
            priest.play('walk');
            
            // Calculate walk duration based on horizontal distance only
            const distance = Math.abs(priest.x - walkToX);
            const walkDuration = distance * 4; // 4ms per pixel
            
            this.tweens.add({
                targets: priest,
                x: walkToX,
                // Keep the same Y position
                duration: walkDuration,
                ease: 'Linear',
                onComplete: () => {
                    // After reaching the transition area, teleport to third floor
                    priest.play('idle');
                    this.cameras.main.flash(300, 127, 255, 142); // Green flash effect
                    
                    // Short delay before teleporting
                    this.time.delayedCall(200, () => {
                        priest.x = 690;
                        priest.y = 180; // Third floor level
                        
                        this.currentFloor = 3;
                        this.updateEntranceAvailability(this.currentFloor);
                        
                        // Short delay before allowing new interactions
                        this.time.delayedCall(400, () => {
                            this.isTransitioning = false;
                        });
                    });
                }
            });
        });
        
        // Third to Second Floor
        this.thirdToSecondZone.off('pointerdown');
        this.thirdToSecondZone.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;
            
            const priest = this.priest;
            this.tweens.killTweensOf(priest);
            
            // First make the priest walk to the transition area
            const walkToX = this.thirdToSecondZone.x;
            
            // Play walking animation and move to transition area horizontally
            priest.play('walk');
            
            // Calculate walk duration based on horizontal distance only
            const distance = Math.abs(priest.x - walkToX);
            const walkDuration = distance * 4; // 4ms per pixel
            
            this.tweens.add({
                targets: priest,
                x: walkToX,
                // Keep the same Y position
                duration: walkDuration,
                ease: 'Linear',
                onComplete: () => {
                    // After reaching the transition area, teleport to second floor
                    priest.play('idle');
                    this.cameras.main.flash(300, 127, 255, 142); // Green flash effect
                    
                    // Short delay before teleporting
                    this.time.delayedCall(200, () => {
                        priest.x = 690;
                        priest.y = 340; // Second floor level
                        
                        this.currentFloor = 2;
                        this.updateEntranceAvailability(this.currentFloor);
                        
                        // Short delay before allowing new interactions
                        this.time.delayedCall(400, () => {
                            this.isTransitioning = false;
                        });
                    });
                }
            });
        });
        
        // 2. SCENE TRANSITIONS (to other scenes)
        
        // Assessment Office (Second Floor)
        this.assessmentZone.off('pointerdown');
        this.assessmentZone.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;
            
            // Fade out and transition to Assessment scene
            this.cameras.main.fadeOut(800, 0, 0, 0);
            this.cameras.main.once('camerafadeoutcomplete', () => {
                this.scene.start('ShedAbandonedOfficeScene');
                this.isTransitioning = false;
            });
        });
        
        // Registration Office (Third Floor)
        this.registrationZone.off('pointerdown');
        this.registrationZone.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;
            
            // Fade out and transition to Registration scene
            this.cameras.main.fadeOut(800, 0, 0, 0);
            this.cameras.main.once('camerafadeoutcomplete', () => {
                this.scene.start('ShedRegistrationScene');
                this.isTransitioning = false;
            });
        });
        
        // Applications Office (Third Floor)
        this.applicationsZone.off('pointerdown');
        this.applicationsZone.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;
            
            // Fade out and transition to Applications scene
            this.cameras.main.fadeOut(800, 0, 0, 0);
            this.cameras.main.once('camerafadeoutcomplete', () => {
                this.scene.start('ShedApplicationsScene');
                this.isTransitioning = false;
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
