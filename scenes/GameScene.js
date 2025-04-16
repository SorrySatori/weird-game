class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' });
        this.dialogVisible = false;
    }

    preload() {
        // Load the game assets
        this.load.image('cityBackground', 'assets/images/city.png');
        this.load.image('ground', 'assets/images/ground.png');
        this.load.spritesheet('priest', 'assets/images/priest.png', {
            frameWidth: 64,
            frameHeight: 64
        });
        this.load.spritesheet('stranger', 'assets/images/mysterious-stranger.png', {
            frameWidth: 64,
            frameHeight: 64
        });

        // Load sound assets
        this.load.audio('backgroundMusic', 'assets/sounds/background-music.wav');
        this.load.audio('clickSound', 'assets/sounds/click.wav');

        // Handle load errors
        this.load.on('loaderror', (fileObj) => {
            console.log('Error loading asset:', fileObj.key);
        });
    }

    create() {
        try {
            // Add the city background
            const bg = this.add.image(400, 300, 'cityBackground');
            bg.setDisplaySize(800, 600);

            // Add ground/street platform
            const ground = this.add.tileSprite(400, 550, 800, 100, 'ground');
            ground.setDisplaySize(800, 100);

            // Create an invisible rectangle that covers the entire game area
            const gameArea = this.add.rectangle(0, 0, 800, 600, 0x000000, 0);
            gameArea.setOrigin(0, 0);
            gameArea.setInteractive();

            // Start background music
            this.backgroundMusic = this.sound.add('backgroundMusic', { loop: true });
            this.backgroundMusic.play();

            // Add click sound
            this.clickSound = this.sound.add('clickSound');

            // Create the Fungus Priest character
            this.priest = this.add.sprite(100, 470, 'priest');
            this.priest.setScale(2);

            // Create the Mysterious Stranger NPC
            this.stranger = this.add.sprite(600, 470, 'stranger');
            this.stranger.setScale(2);
            this.stranger.setInteractive({ useHandCursor: true });

            // Create NPC idle animation
            this.anims.create({
                key: 'stranger-idle',
                frames: this.anims.generateFrameNumbers('stranger', { start: 0, end: 3 }),
                frameRate: 4,
                repeat: -1
            });
            this.stranger.play('stranger-idle');

            // Create dialog box
            this.dialogBox = this.add.container(400, 300);
            this.dialogBox.setDepth(1000);

            // Dialog background
            const dialogBg = this.add.rectangle(0, 0, 600, 200, 0x0a2712, 0.9);
            dialogBg.setStrokeStyle(2, 0x7fff8e);

            // Dialog text
            this.dialogText = this.add.text(-280, -80, '', {
                fontSize: '24px',
                fill: '#7fff8e',
                wordWrap: { width: 560 }
            });

            // Continue button
            const continueButton = this.add.text(200, 60, 'Continue', {
                fontSize: '20px',
                fill: '#7fff8e',
                backgroundColor: '#0a271266',
                padding: { x: 10, y: 5 }
            });
            continueButton.setInteractive({ useHandCursor: true });

            continueButton.on('pointerover', () => {
                continueButton.setStyle({ fill: '#b3ffcc' });
            });

            continueButton.on('pointerout', () => {
                continueButton.setStyle({ fill: '#7fff8e' });
            });

            continueButton.on('pointerdown', () => {
                this.clickSound.play();
                this.hideDialog();
            });

            // Add elements to dialog container
            this.dialogBox.add([dialogBg, this.dialogText, continueButton]);
            this.dialogBox.visible = false;

            // Dialog content
            this.dialogLines = [
                "Greetings, seeker of truth. I am but a whisper in this strange city.",
                "The patterns you see... they are not what they seem. The fungal gods watch from beyond.",
                "Perhaps our paths will cross again, when the spores align..."
            ];
            this.currentLine = 0;

            // Add click handler for NPC
            this.stranger.on('pointerdown', () => {
                if (!this.dialogVisible) {
                    this.clickSound.play();
                    this.showDialog();
                }
            });

            // Create walking animation
            this.anims.create({
                key: 'walk',
                frames: this.anims.generateFrameNumbers('priest', { start: 0, end: 3 }),
                frameRate: 8,
                repeat: -1
            });

            // Create idle animation
            this.anims.create({
                key: 'idle',
                frames: this.anims.generateFrameNumbers('priest', { start: 0, end: 0 }),
                frameRate: 1,
                repeat: 0
            });

            // Set initial animation
            this.priest.play('idle');

            // Add click/tap handler for movement
            this.input.on('pointerdown', (pointer) => {
                if (!this.dialogVisible && pointer.y < 500) { // Only move if no dialog and clicked above ground
                    const targetX = pointer.x;
                    const direction = targetX < this.priest.x ? -1 : 1;

                    // Play click sound
                    this.clickSound.play();

                    // Flip sprite based on direction
                    this.priest.setScale(2 * direction, 2);

                    // Play walking animation
                    this.priest.play('walk');

                    // Move the priest
                    this.tweens.add({
                        targets: this.priest,
                        x: targetX,
                        duration: Math.abs(targetX - this.priest.x) * 5,
                        ease: 'Linear',
                        onComplete: () => {
                            this.priest.play('idle');
                        }
                    });
                }
            });

            // Add menu button
            const menuButton = this.add.text(50, 50, 'Menu', {
                fontSize: '24px',
                fill: '#7fff8e',
                backgroundColor: '#0a271266',
                padding: { x: 15, y: 10 },
                stroke: '#0a2712',
                strokeThickness: 2
            });
            menuButton.setInteractive({ useHandCursor: true });

            menuButton.on('pointerover', () => {
                menuButton.setStyle({ 
                    fill: '#b3ffcc',
                    backgroundColor: '#0a271299'
                });
                menuButton.setScale(1.1);
            });

            menuButton.on('pointerout', () => {
                menuButton.setStyle({ 
                    fill: '#7fff8e',
                    backgroundColor: '#0a271266'
                });
                menuButton.setScale(1);
            });

            menuButton.on('pointerdown', () => {
                this.clickSound.play();
                this.backgroundMusic.stop();
                this.scene.start('MainScene');
            });

            // Add custom cursor if available
            try {
                this.input.setDefaultCursor('none');
                this.cursor = this.add.image(0, 0, 'cursor');
                this.cursor.setScale(0.008);
                this.cursor.setAlpha(0.8);
                this.input.on('pointermove', (pointer) => {
                    this.cursor.setPosition(pointer.x, pointer.y);
                });
            } catch (e) {
                console.log('Custom cursor not available');
            }
        } catch (error) {
            console.error('Error in create():', error);
        }
    }

    showDialog() {
        this.dialogVisible = true;
        this.dialogBox.visible = true;
        this.dialogText.setText(this.dialogLines[this.currentLine]);
        this.currentLine = (this.currentLine + 1) % this.dialogLines.length;
    }

    hideDialog() {
        this.dialogVisible = false;
        this.dialogBox.visible = false;
    }

    update() {
        // Game loop updates will go here
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.GameScene = GameScene;
}
