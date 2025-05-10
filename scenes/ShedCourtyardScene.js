import GameScene from './GameScene.js';

export default class ShedCourtyardScene extends GameScene {
    constructor() {
        super({ key: 'ShedCourtyard' });  // This key must match what we use in transitions
        this.isTransitioning = false;
    }

    preload() {
        super.preload();
        this.load.image('courtyard-bg', 'assets/images/ShedMutationCourtyard.png');
        this.load.image('door', 'assets/images/door.png');
        this.load.image('exitArea', 'assets/images/exitArea.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set background
        const bg = this.add.image(400, 300, 'courtyard-bg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Set initial priest position
        if (this.priest) {
            this.priest.x = 50;
            this.priest.y = 470;  // Match the ground level from other scenes
            this.priest.setOrigin(0.5, 1);
            this.priest.play('idle');
        }

        // Add invisible clickable exit area at the left of the screen
        this.exitArea = this.add.image(50, 470, 'exitArea')
            .setDisplaySize(50, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);
        
        // Exit area click logic
        this.exitArea.on('pointerdown', () => {
            if (!this.isTransitioning && this.priest && this.priest.x < 100) {
                this.isTransitioning = true;

                const priest = this.priest;
                priest.play('walk');
                
                // Stop any existing tweens on the priest
                this.tweens.killTweensOf(priest);
                
                this.tweens.add({
                    targets: priest,
                    x: 20,
                    y: priest.y,
                    duration: 1000,
                    onComplete: () => {
                        this.cameras.main.fadeOut(800, 0, 0, 0);
                        this.cameras.main.once('camerafadeoutcomplete', () => {
                            this.scene.start('Shed13GateScene');
                            this.isTransitioning = false;
                        });
                    }
                });
            }
        });
    }

    update() {
        super.update();
        
        // Handle cursor through the exitArea's useHandCursor property
        if (this.priest && this.priest.x < 100) {
            this.exitArea.input.cursor = 'pointer';
        } else {
            this.exitArea.input.cursor = 'default';
        }
    }
}
