import GameScene from './GameScene.js';

export default class Shed13Scene extends GameScene {
    constructor() {
        super({ key: 'Shed13Scene' });
        this.isTransitioning = false;
    }

    preload() {
        super.preload();
        this.load.image('shed13Bg', 'assets/images/Shed13.png');
        this.load.image('exitArea', 'assets/images/door.png');
        this.load.image('mysteriousSpore', 'assets/images/spore.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set shed13 background
        const bg = this.add.image(400, 300, 'shed13Bg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Add a collectable spore
        const spore = this.add.image(300, 450, 'mysteriousSpore');
        spore.setScale(0.5);
        // Add a subtle glow effect
        spore.preFX.addGlow(0x7fff8e, 4, 0, false, 0.5, 16);
        
        // Make the spore collectable with description
        this.makeItemCollectable({
            id: 'mysterious_spore',
            name: 'Mysterious Spore',
            description: 'A peculiar spore found in Shed13. It pulses with an otherworldly energy.',
            spriteKey: 'mysteriousSpore',
            stackable: true
        }, spore);
        
        // Add invisible clickable exit area at the right side
        this.exitArea = this.add.image(750, 470, 'exitArea')
            .setDisplaySize(40, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);
        
        // Position the priest at the left side when entering
        this.priest.x = 100;
        this.priest.y = 470;
        
        // Update priest's staff position (facing right)
        this.updateStaffPosition(1);
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // Exit area click handler
        this.exitArea.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);

            this.tweens.add({
                targets: priest,
                x: 750,
                y: 470,
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('CrossroadScene');
                    });
                }
            });
        });
    }

    update() {
        super.update();
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.Shed13Scene = Shed13Scene;
}
