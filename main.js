const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    scene: [MainScene, GameScene, EggCatedralScene],
    backgroundColor: '#2d2d2d',
    pixelArt: true,
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH
    }
};

const game = new Phaser.Game(config);
