import GameScene from './GameScene.js';

export default class ShedHallScene extends GameScene {
    constructor() {
        super({ key: 'ShedHallScene' });  
        this.isTransitioning = false;
    }

    preload() {
        super.preload();
        this.load.image('hall-bg', 'assets/images/ShedHall.png');
        this.load.image('exitArea', 'assets/images/exitArea.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set background
        const bg = this.add.image(400, 300, 'hall-bg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Set initial priest position if coming from abandoned office
        if (this.priest) {
            this.priest.x = 50;  
            this.priest.y = 470;  
            this.priest.setOrigin(0.5, 1);
            this.priest.play('idle');
        }

        // Add left exit area for returning to abandoned office
        this.leftExit = this.add.image(50, 470, 'exitArea')
            .setDisplaySize(50, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true })
            .setDepth(10);

        // Left exit click logic
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
                            this.scene.start('ShedAbandonedOfficeScene');
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
