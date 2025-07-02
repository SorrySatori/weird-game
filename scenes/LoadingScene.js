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
        
        // Create loading text
        const loadingText = this.add.text(400, 400, 'Loading...', {
            fontSize: '24px',
            fill: '#7fff8e',
            fontFamily: 'Arial'
        });
        loadingText.setOrigin(0.5);
        
        // Add loading progress bar
        const progressBar = this.add.graphics();
        const progressBox = this.add.graphics();
        progressBox.fillStyle(0x0a2712, 0.8);
        progressBox.fillRect(240, 430, 320, 30);
        
        // Register loading progress events
        this.load.on('progress', (value) => {
            progressBar.clear();
            progressBar.fillStyle(0x7fff8e, 1);
            progressBar.fillRect(250, 440, 300 * value, 10);
        });
    }

    create() {
        // Create a dark background
        this.add.rectangle(400, 300, 800, 600, 0x000000).setOrigin(0.5);
        
        // Add the Tempurra logo
        const logo = this.add.image(400, 300, 'tempurraLogo');
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
