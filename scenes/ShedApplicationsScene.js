import GameScene from './GameScene.js';

export default class ShedApplicationsScene extends GameScene {
    constructor() {
        super({ key: 'ShedApplicationsScene' });
        this.isTransitioning = false;
    }

    preload() {
        super.preload();
        this.load.image('applications-bg', 'assets/images/ShedApplications.png');
        this.load.image('door', 'assets/images/door.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set initial priest position
        if (this.priest) {
            this.priest.x = 650;  // Match entrance position from Shed13FloorsScene
            this.priest.y = 520;  // Ground level
            this.priest.setOrigin(0.5, 1);
            this.priest.play('idle');
        }

        // Set background
        const bg = this.add.image(400, 300, 'applications-bg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Add exit back to Shed13FloorsScene
        this.exitToShed = this.add.image(650, 520, 'door')
            .setDisplaySize(100, 100)
            .setAlpha(0.01)
            .setInteractive();

        this.exitArea = this.add.image(50, 470, 'exitArea')
            .setDisplaySize(50, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);

        // Set up pointer events
        this.exitToShed.on('pointerover', () => {
            if (!this.isTransitioning) {
                this.setCursor('pointer');
            }
        });

        this.exitToShed.on('pointerout', () => {
            if (!this.isTransitioning) {
                this.setCursor('default');
            }
        });

        this.exitToShed.on('pointerdown', () => {
            if (!this.isTransitioning) {
                this.isTransitioning = true;
                this.transitionToScene('Shed13FloorsScene', () => {
                    // Set position in Shed13FloorsScene near the applications entrance
                    return { x: 650, y: 450 };
                });
            }
        });

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
                        this.scene.start('Shed13FloorsScene');
                        this.isTransitioning = false; // Reset transition flag
                    });
                }
            });
        });
    }
    

    update() {
        super.update();
    }
}
