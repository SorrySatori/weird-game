export default class MainScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MainScene' });
        console.log('MainScene constructor called');
    }

    preload() {
        console.log('MainScene preload started');
        // Load images
        this.load.image('background', 'assets/images/backgrounds/background.png');
        
        // Load sound assets
        this.load.audio('backgroundMusic', 'assets/sounds/background-music.wav');
        this.load.audio('hoverSound', 'assets/sounds/hover.wav');
        this.load.audio('clickSound', 'assets/sounds/click.mp3');

        // Handle load errors
        this.load.on('loaderror', (fileObj) => {
            console.log('Error loading asset:', fileObj.key);
        });
    }

    create() {
        console.log('MainScene create started');
        try {
            // Create an invisible rectangle that covers the entire game area
            const gameArea = this.add.rectangle(0, 0, 800, 600, 0x000000, 0);
            gameArea.setOrigin(0, 0);
            gameArea.setInteractive();

            // Add background
            const bg = this.add.image(400, 300, 'background');
            bg.setDisplaySize(800, 600);

            // Start background music
            this.backgroundMusic = this.sound.add('backgroundMusic', { loop: true });
            this.backgroundMusic.play();

            // Add hover and click sounds
            this.hoverSound = this.sound.add('hoverSound');
            this.clickSound = this.sound.add('clickSound');

            // Add title text
            const title = this.add.text(400, 200, 'Weird Game', {
                fontSize: '72px',
                fill: '#7fff8e',
                fontFamily: 'Arial',
                stroke: '#0a2712',
                strokeThickness: 8,
                shadow: { color: '#2fff91', blur: 10, stroke: true, fill: true }
            });
            title.setOrigin(0.5);

            // Create button background
            const buttonBg = this.add.rectangle(400, 400, 200, 60, 0x0a2712, 0.4);
            buttonBg.setStrokeStyle(2, 0x7fff8e);
            buttonBg.setInteractive();
            buttonBg.setDepth(1);
            // Add start game text
            const startText = this.add.text(400, 400, 'Start Game', {
                fontSize: '32px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            });
            startText.setOrigin(0.5);

            // Add fullscreen button with matching style
            const fullscreenBg = this.add.rectangle(400, 480, 200, 60, 0x0a2712, 0.4);
            fullscreenBg.setStrokeStyle(2, 0x7fff8e);
            fullscreenBg.setInteractive({ useHandCursor: true });

            const fullscreenText = this.add.text(400, 480, 'Fullscreen', {
                fontSize: '32px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            });
            fullscreenText.setOrigin(0.5);

            // Add hover effects for both buttons
            const addHoverEffects = (bg, text) => {
                bg.on('pointerover', () => {
                    bg.setFillStyle(0x0a2712, 0.6);
                    text.setStyle({ fill: '#2fff91' });
                    this.hoverSound.play();
                });

                bg.on('pointerout', () => {
                    bg.setFillStyle(0x0a2712, 0.4);
                    text.setStyle({ fill: '#7fff8e' });
                });
            };

            addHoverEffects(buttonBg, startText);
            addHoverEffects(fullscreenBg, fullscreenText);

            // Add click handlers
            buttonBg.on('pointerdown', () => {
                this.clickSound.play();
                this.cameras.main.fadeOut(1000, 0, 0, 0);
                this.cameras.main.once('camerafadeoutcomplete', () => {
                    this.scene.start('EntryScene');
                });
            });

            fullscreenBg.on('pointerdown', () => {
                this.clickSound.play();
                if (!document.fullscreenElement) {
                    this.scale.startFullscreen();
                } else if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            });

            // Add F11 key handler for fullscreen
            this.input.keyboard.on('keydown-F11', (event) => {
                event.preventDefault();
                if (!document.fullscreenElement) {
                    this.scale.startFullscreen();
                } else if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            });


            // Add global click handler to debug
            this.input.on('pointerdown', (pointer) => {
                console.log('Click detected at:', pointer.x, pointer.y);
            });

        } catch (error) {
            console.error('Error in create():', error);
        }
    }

    update() {
        // Game loop updates will go here
    }
}
