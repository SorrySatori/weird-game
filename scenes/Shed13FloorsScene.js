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
        this.welcomeEntrance = this.add.image(110, 400, 'door')
            .setDisplaySize(120, 200)  // Made even wider to better match the large door
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.welcomeEntrance.setDepth(10);

        // Add invisible clickable area for VoxMarket entrance
        // this.exitEntrance = this.add.image(650, 400, 'door')
        //     .setDisplaySize(100, 200)
        //     .setAlpha(0.01)
        //     .setInteractive({ useHandCursor: true });
        // this.exitEntrance.setDepth(10);

        this.exitEntrance = this.add.image(450, 400, 'door')
        .setDisplaySize(100, 200)
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
