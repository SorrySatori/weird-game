import GameScene from './GameScene.js';

export default class ShedAbandonedOfficeScene extends GameScene {
    constructor() {
        super({ key: 'ShedAbandonedOfficeScene' });
        this.isTransitioning = false;
    }

    preload() {
        super.preload();
        this.load.image('office-bg', 'assets/images/backgrounds/ShedAbandonedOffice.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set background
        const bg = this.add.image(400, 300, 'office-bg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Set initial priest position
        if (this.priest) {
            this.priest.x = 250;  // Match entrance position from Shed521FloorsScene
            this.priest.y = 520;  // Ground level
            this.priest.setOrigin(0.5, 1);
            this.priest.play('idle');
        }

        // Add left exit area (back to Shed521FloorsScene)
        this.leftExit = this.add.image(50, 470, 'exitArea')
            .setDisplaySize(50, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true })
            .setDepth(10);

        // Add right exit area (to ShedHallScene)
        this.rightExit = this.add.image(750, 470, 'exitArea')
            .setDisplaySize(50, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true })
            .setDepth(10);

        // Left exit click logic (back to Shed521FloorsScene)
        this.leftExit.on('pointerdown', () => {
            if (!this.isTransitioning) {
                this.isTransitioning = true;
                const priest = this.priest;
                priest.play('walk');
                
                this.tweens.add({
                    targets: priest,
                    x: 50,
                    y: 470,
                    duration: 1000,
                    onComplete: () => {
                        this.cameras.main.fadeOut(800, 0, 0, 0);
                        this.cameras.main.once('camerafadeoutcomplete', () => {
                            this.scene.start('Shed521FloorsScene');
                            this.isTransitioning = false;
                        });
                    }
                });
            }
        });

        // Right exit click logic (to ShedHallScene)
        this.rightExit.on('pointerdown', () => {
            if (!this.isTransitioning) {
                this.isTransitioning = true;
                const priest = this.priest;
                priest.play('walk');
                
                this.tweens.add({
                    targets: priest,
                    x: 750,
                    y: 470,
                    duration: 1000,
                    onComplete: () => {
                        this.cameras.main.fadeOut(800, 0, 0, 0);
                        this.cameras.main.once('camerafadeoutcomplete', () => {
                            this.scene.start('ShedHallScene');
                            this.isTransitioning = false;
                        });
                    }
                });
            }
        });
    }

    update() {
        super.update();
    }
}
