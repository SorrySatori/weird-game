class EggCatedralScene extends GameScene {
    constructor() {
        super({ key: 'EggCatedralScene' });
    }

    preload() {
        super.preload();
        this.load.image('eggCatedralBg', 'assets/images/egg-catedral.png');
    }

    create() {
        // Set egg cathedral background
        const bg = this.add.image(400, 300, 'eggCatedralBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        // Use all mechanics from GameScene except city background
        this.initSceneMechanics();
    }
}

if (typeof window !== 'undefined') {
    window.EggCatedralScene = EggCatedralScene;
}
