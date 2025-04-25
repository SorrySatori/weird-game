import GameScene from './GameScene.js';

export default class CrossroadScene extends GameScene {
    constructor() {
        super({ key: 'CrossroadScene' });
        this.isTransitioning = false; // Add flag to track transition state
    }

    preload() {
        super.preload();
        this.load.image('crossroadBg', 'assets/images/crossroad.png');
        this.load.image('door', 'assets/images/door.png'); // Placeholder transparent image for clickable door
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set crossroad background
        const bg = this.add.image(400, 300, 'crossroadBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Add invisible clickable area for Shed13 entrance
        this.marketEntrance = this.add.image(100, 400, 'door')
            .setDisplaySize(120, 200)  // Made even wider to better match the large door
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.marketEntrance.setDepth(10);

        // Add invisible clickable area for VoxMarket entrance
        this.voxMarketEntrance = this.add.image(650, 400, 'door')
            .setDisplaySize(100, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.voxMarketEntrance.setDepth(10);

        // Add invisible clickable area for Scraper entrance
        this.scraperEntrance = this.add.image(400, 400, 'door')
            .setDisplaySize(100, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.scraperEntrance.setDepth(10);

        // Add invisible clickable area at the right border for EntryScene
        this.scraperSceneEntrance = this.add.image(750, 470, 'door')
            .setDisplaySize(40, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.scraperSceneEntrance.setDepth(10);
        
        // Shed13 entrance click logic
        this.marketEntrance.on('pointerdown', () => {
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
                        this.scene.start('Shed13Scene');
                    });
                }
            });
        });

        // VoxMarket entrance click logic
        this.voxMarketEntrance.on('pointerdown', () => {
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
                        this.scene.start('VoxMarket');
                    });
                }
            });
        });

        // ScraperScene entrance click logic
        this.scraperSceneEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: 750,
                y: 470, // Ground level
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('ScraperScene');
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
