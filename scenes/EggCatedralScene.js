class EggCatedralScene extends GameScene {
    constructor() {
        super({ key: 'EggCatedralScene' });
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
                        // Optionally: start a new scene or show dialog
                        this.scene.start('GameScene');
                    });
                }
            });
        });
    }
}

if (typeof window !== 'undefined') {
    window.EggCatedralScene = EggCatedralScene;
}
