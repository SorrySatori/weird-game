class EggCatedralScene extends GameScene {
    constructor() {
        super({ key: 'EggCatedralScene' });
        this.isTransitioning = false; // Add flag to track transition state
    }

    preload() {
        super.preload();
        this.load.image('eggCatedralBg', 'assets/images/egg-catedral.png');
        this.load.image('door', 'assets/images/door.png'); // Placeholder transparent image for clickable door
    }

    create() {
        // Set egg cathedral background
        const bg = this.add.image(400, 300, 'eggCatedralBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Add invisible clickable door at entrance (adjust position/size as needed)
        this.door = this.add.image(450, 300, 'door').setDisplaySize(100, 120).setAlpha(0.01).setInteractive({ useHandCursor: true });
        this.door.setDepth(10);
        
        // Add invisible clickable area at the right border for VoxMarket
        this.marketEntrance = this.add.image(780, 470, 'door')
            .setDisplaySize(40, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.marketEntrance.setDepth(10);
        
        // Use all mechanics from GameScene except city background
        this.initSceneMechanics();
        
        // Door click logic
        this.door.on('pointerdown', () => {
            // Move priest to door, then fade out
            const priest = this.priest;
            priest.play('walk');
            this.tweens.add({
                targets: priest,
                x: this.door.x,
                y: this.door.y + 40, // Move slightly below door center
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        // Direct to the Cathedral Entrance scene instead of GameScene
                        this.scene.start('CathedralEntrance');
                    });
                }
            });
        });
        
        // Market entrance click logic
        this.marketEntrance.on('pointerdown', () => {
            // Move priest to market entrance, then fade out
            const priest = this.priest;
            priest.play('walk');
            
            // Kill any existing tweens
            this.tweens.killTweensOf(priest);
            
            // Set transition flag
            this.isTransitioning = true;
            
            this.tweens.add({
                targets: priest,
                x: 780,
                y: 470, // Ground level
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('VoxMarket');
                        this.isTransitioning = false; // Reset transition flag
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

if (typeof window !== 'undefined') {
    window.EggCatedralScene = EggCatedralScene;
}
