import ScalingManager from '../utils/ScalingManager.js';

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
        this.load.audio('hoverSound', 'assets/sounds/hover.wav');
        this.load.audio('clickSound', 'assets/sounds/click.mp3');
        this.load.audio('mainMenuMusic', 'assets/sounds/upper-morkezela.mp3');


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

            // Add hover and click sounds
            this.hoverSound = this.sound.add('hoverSound');
            this.clickSound = this.sound.add('clickSound');

            // Add title text
            const title = this.add.text(400, 150, 'Weird Game', {
                fontSize: '72px',
                fill: '#7fff8e',
                fontFamily: 'Arial',
                stroke: '#0a2712',
                strokeThickness: 8,
                shadow: { color: '#2fff91', blur: 10, stroke: true, fill: true }
            });
            title.setOrigin(0.5);

            // Create start game button
            const startBg = this.add.rectangle(400, 350, 200, 60, 0x0a2712, 0.4);
            startBg.setStrokeStyle(2, 0x7fff8e);
            startBg.setInteractive({ useHandCursor: true });
            startBg.setDepth(1);
            
            const startText = this.add.text(400, 350, 'Start Game', {
                fontSize: '32px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            });
            startText.setOrigin(0.5);
            
            // Add hover effects
            startBg.on('pointerover', () => {
                startBg.setFillStyle(0x0a2712, 0.6);
                startText.setStyle({ fill: '#2fff91' });
                this.hoverSound.play();
            });
            
            startBg.on('pointerout', () => {
                startBg.setFillStyle(0x0a2712, 0.4);
                startText.setStyle({ fill: '#7fff8e' });
            });
            
            // Add click handler
            startBg.on('pointerdown', () => {
                this.clickSound.play();
                this.cameras.main.fadeOut(1000, 0, 0, 0);
                this.cameras.main.once('camerafadeoutcomplete', () => {
                    this.scene.start('IntroScene');
                });
            });

            // Create fullscreen button
            const fullscreenBg = this.add.rectangle(400, 430, 200, 60, 0x0a2712, 0.4);
            fullscreenBg.setStrokeStyle(2, 0x7fff8e);
            fullscreenBg.setInteractive({ useHandCursor: true });
            fullscreenBg.setDepth(1);
            
            const fullscreenText = this.add.text(400, 430, 'Fullscreen', {
                fontSize: '32px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            });
            fullscreenText.setOrigin(0.5);
            
            // Add hover effects
            fullscreenBg.on('pointerover', () => {
                fullscreenBg.setFillStyle(0x0a2712, 0.6);
                fullscreenText.setStyle({ fill: '#2fff91' });
                this.hoverSound.play();
            });
            
            fullscreenBg.on('pointerout', () => {
                fullscreenBg.setFillStyle(0x0a2712, 0.4);
                fullscreenText.setStyle({ fill: '#7fff8e' });
            });
            
            // Add click handler
            fullscreenBg.on('pointerdown', () => {
                this.clickSound.play();
                this.toggleFullscreen();
            });

            // Add global click handler for debugging
            this.input.on('pointerdown', (pointer) => {
                console.log('Click detected at:', pointer.x, pointer.y);
            });

            if (!this.backgroundMusic) {
                this.backgroundMusic = this.sound.add('mainMenuMusic', { loop: true });
            }
            this.sceneMusic = this.sound.add('mainMenuMusic', { loop: true });
            this.sceneMusic.play();

            // Add F11 key handler for fullscreen
            this.input.keyboard.on('keydown-F11', (event) => {
                event.preventDefault();
                this.toggleFullscreen();
            });
            
            // Add F key handler for fullscreen (common in web games)
            this.input.keyboard.on('keydown-F', (event) => {
                this.toggleFullscreen();
            });


            // Add global click handler to debug
            this.input.on('pointerdown', (pointer) => {
                console.log('Click detected at:', pointer.x, pointer.y);
            });

        } catch (error) {
            console.error('Error in create():', error);
        }
    }

    toggleFullscreen() {
        // Cross-browser fullscreen handling
        const container = document.getElementById('game-container');
        
        if (!document.fullscreenElement && 
            !document.mozFullScreenElement && 
            !document.webkitFullscreenElement && 
            !document.msFullscreenElement) {
            
            // Enter fullscreen
            if (container.requestFullscreen) {
                container.requestFullscreen();
            } else if (container.msRequestFullscreen) {
                container.msRequestFullscreen();
            } else if (container.mozRequestFullScreen) {
                container.mozRequestFullScreen();
            } else if (container.webkitRequestFullscreen) {
                container.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
            }
            
            // Force resize after fullscreen
            setTimeout(() => {
                this.scale.resize(window.innerWidth, window.innerHeight);
                console.log('Entered fullscreen mode, resizing to:', window.innerWidth, window.innerHeight);
            }, 100);
        } else {
            // Exit fullscreen
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            }
            
            // Force resize after exiting fullscreen
            setTimeout(() => {
                this.scale.resize(window.innerWidth, window.innerHeight);
                console.log('Exited fullscreen mode, resizing to:', window.innerWidth, window.innerHeight);
            }, 100);
        }
    }
    
    update() {
        // Game loop updates will go here
    }
}
