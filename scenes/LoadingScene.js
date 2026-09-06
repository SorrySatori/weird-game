import { ITEM_ICONS } from '../utils/itemIcons.js';

export default class LoadingScene extends Phaser.Scene {
    constructor() {
        super({ key: 'LoadingScene' });
    }

    preload() {
        // Load the Tempurra logo
        this.load.image('tempurraLogo', 'assets/images/ui/TempurraLogo.png');

        // Load other essential assets needed for MainScene
        this.load.image('background', 'assets/images/backgrounds/background.png');
        this.load.audio('hoverSound', 'assets/sounds/hover.wav');
        this.load.audio('clickSound', 'assets/sounds/click.mp3');

        // Central item-icon registry. Loaded once here so every icon is available game-wide
        // (inventory in any scene, after a save load). An icon not yet drawn simply fails to
        // load and the item falls back to its lettered-circle placeholder — so we quietly
        // ignore load errors for these optional textures.
        const iconKeys = new Set(ITEM_ICONS.map(i => i.key));
        this.load.on('loaderror', (file) => { if (file && iconKeys.has(file.key)) { /* optional icon missing — placeholder is used */ } });
        ITEM_ICONS.forEach(({ key, path }) => this.load.image(key, path));
        
        // Create loading text
        const loadingText = this.add.text(this.scale.width / 2, 400, 'Loading...', {
            fontSize: '24px',
            fill: '#7fff8e',
            fontFamily: 'Arial'
        });
        loadingText.setOrigin(0.5);
        
        // Add loading progress bar
        const progressBar = this.add.graphics();
        const progressBox = this.add.graphics();
        const cx = this.scale.width / 2; // centre the bar on the (now 1067-wide) canvas
        progressBox.fillStyle(0x0a2712, 0.8);
        progressBox.fillRect(cx - 160, 430, 320, 30);

        // Register loading progress events
        this.load.on('progress', (value) => {
            progressBar.clear();
            progressBar.fillStyle(0x7fff8e, 1);
            progressBar.fillRect(cx - 150, 440, 300 * value, 10);
        });
    }

    create() {
        // Create a dark background
        this.add.rectangle(this.scale.width / 2, this.scale.height / 2, this.scale.width, this.scale.height, 0x000000).setOrigin(0.5);
        
        // Add the Tempurra logo
        const logo = this.add.image(this.scale.width / 2, 300, 'tempurraLogo');
        logo.setScale(0.4);
        
        // Add a subtle glow effect around the logo
        const glow = this.add.graphics();
        glow.fillStyle(0x7fff8e, 0.2);
        glow.fillCircle(400, 300, 150);
        glow.setDepth(-1);
        
        // Add pulsating animation to the glow
        this.tweens.add({
            targets: glow,
            alpha: { from: 0.2, to: 0.4 },
            duration: 1500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Add a subtle scale animation to the logo
        this.tweens.add({
            targets: logo,
            scale: { from: 0.4, to: 0.42 },
            duration: 1200,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Display for a few seconds then transition to MainScene
        this.time.delayedCall(3000, () => {
            this.cameras.main.fadeOut(1000, 0, 0, 0);
            this.cameras.main.once('camerafadeoutcomplete', () => {
                this.scene.start('MainScene');
            });
        });
    }
}
