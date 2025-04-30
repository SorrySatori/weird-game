import GameScene from './GameScene.js';

export default class Shed13FloorsScene extends GameScene {
    constructor() {
        super({ key: 'Shed13FloorsScene' });
        this.isTransitioning = false; // Add flag to track transition state
    }

    preload() {
        super.preload();
        this.load.image('floors', 'assets/images/Shed13_floors.png');
        this.load.image('door', 'assets/images/door.png'); // Placeholder transparent image for clickable door
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set crossroad background
        const bg = this.add.image(400, 300, 'floors');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Add invisible clickable area for Shed13 entrance
        this.welcomeEntrance = this.add.image(110, 450, 'door')
            .setDisplaySize(120, 100)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.welcomeEntrance.setDepth(10);

        this.secondFloorEntrance = this.add.image(650, 450, 'door')
            .setDisplaySize(100, 100)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.secondFloorEntrance.setDepth(10);

        this.exitEntrance = this.add.image(450, 450, 'door')
        .setDisplaySize(100, 100)
        .setAlpha(0.01)
        .setInteractive({ useHandCursor: true });
    this.exitEntrance.setDepth(10);

        
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
                y: 470, // Ground level
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('CrossroadScene');
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
                y: 470, // Ground level
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('Shed13GateScene');
                    });
                }
            });
        });

        // Second floor entrance click logic
        this.secondFloorEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            this.tweens.killTweensOf(priest);
            // Instantly move priest to second floor
            priest.x = 400; // Center of the platform
            priest.y = 280; // Second floor height
            priest.play('idle');

            // Optionally, you can add a small fade/flash effect for teleportation
            this.cameras.main.flash(300, 127, 255, 142);

            // Allow further transitions after a short delay
            this.time.delayedCall(400, () => {
                this.isTransitioning = false;
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
    }
}
