class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' });
        this.dialogVisible = false;
        this.dialogState = 'main';
        this.dialogOptionsY = 0; // Track options position
    }

    preload() {
        // Load the game assets
        this.load.image('cityBackground', 'assets/images/city.png');
        this.load.image('ground', 'assets/images/ground.png');
        this.load.image('cursor', 'assets/images/cursor.png');
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

            // Start background music
            this.backgroundMusic = this.sound.add('backgroundMusic', { loop: true });
            this.backgroundMusic.play();

            // Add click sound
            this.clickSound = this.sound.add('clickSound');

            // Set up custom cursor for non-interactive areas
            this.cursor = this.add.image(0, 0, 'cursor');
            this.cursor.setScale(0.008);
            this.cursor.setAlpha(0.8);
            this.cursor.setDepth(1000);
            
            this.input.on('pointermove', (pointer) => {
                this.cursor.setPosition(pointer.x, pointer.y);
            });

            // Create the Fungus Priest character
            this.priest = this.add.sprite(100, 470, 'priest');
            this.priest.setScale(2);

            // Create the Mysterious Stranger NPC
            this.stranger = this.add.sprite(600, 470, 'stranger');
            this.stranger.setScale(2);
            this.stranger.setInteractive({ useHandCursor: true });
            
            // Handle cursor visibility
            this.input.on('gameobjectover', (pointer, gameObject) => {
                if (gameObject.input.useHandCursor) {
                    this.cursor.setAlpha(0);
                }
            });
            
            this.input.on('gameobjectout', (pointer, gameObject) => {
                if (gameObject.input.useHandCursor) {
                    this.cursor.setAlpha(0.8);
                }
            });

            // Create NPC idle animation
            this.anims.create({
                key: 'stranger-idle',
                frames: this.anims.generateFrameNumbers('stranger', { start: 0, end: 3 }),
                frameRate: 4,
                repeat: -1
            });
            this.stranger.play('stranger-idle');

            // Add click handler for NPC
            this.stranger.on('pointerdown', () => {
                if (!this.dialogVisible) {
                    this.clickSound.play();
                    this.showDialog('main');
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
                if (!this.dialogVisible && pointer.y < 500) {
                    const targetX = pointer.x;
                    const direction = targetX < this.priest.x ? -1 : 1;
                    this.clickSound.play();
                    this.priest.setScale(2 * direction, 2);
                    this.priest.play('walk');

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

            // Add menu button with our established style
            const menuButtonBg = this.add.rectangle(50, 50, 100, 40, 0x0a2712, 0.4);
            menuButtonBg.setStrokeStyle(2, 0x7fff8e);
            menuButtonBg.setInteractive({ useHandCursor: true });
            menuButtonBg.setDepth(1);

            const menuText = this.add.text(50, 50, 'Menu', {
                fontSize: '24px',
                fill: '#7fff8e'
            });
            menuText.setOrigin(0.5);
            menuText.setDepth(2);

            menuButtonBg.on('pointerover', () => {
                menuButtonBg.setFillStyle(0x0a2712, 0.6);
                menuText.setStyle({ fill: '#b3ffcc' });
                menuButtonBg.setScale(1.1);
                menuText.setScale(1.1);
            });

            menuButtonBg.on('pointerout', () => {
                menuButtonBg.setFillStyle(0x0a2712, 0.4);
                menuText.setStyle({ fill: '#7fff8e' });
                menuButtonBg.setScale(1);
                menuText.setScale(1);
            });

            menuButtonBg.on('pointerdown', () => {
                this.clickSound.play();
                this.backgroundMusic.stop();
                this.scene.start('MainScene');
            });

        } catch (error) {
            console.error('Error in create():', error);
        }
    }

    createDialogOption(text, y, callback) {
        const optionBg = this.add.rectangle(0, y, 560, 40, 0x0a2712, 0.4);
        optionBg.setStrokeStyle(1, 0x7fff8e);
        optionBg.setInteractive({ useHandCursor: true });

        const optionText = this.add.text(0, y, text, {
            fontSize: '20px',
            fill: '#7fff8e'
        });
        optionText.setOrigin(0.5);

        optionBg.on('pointerover', () => {
            optionBg.setFillStyle(0x0a2712, 0.6);
            optionText.setStyle({ fill: '#b3ffcc' });
        });

        optionBg.on('pointerout', () => {
            optionBg.setFillStyle(0x0a2712, 0.4);
            optionText.setStyle({ fill: '#7fff8e' });
        });

        optionBg.on('pointerdown', () => {
            this.clickSound.play();
            
            // Disable interaction to prevent multiple clicks
            optionBg.disableInteractive();
            
            // Hide clicked option with fade out
            this.tweens.add({
                targets: [optionBg, optionText],
                alpha: 0,
                duration: 200,
                ease: 'Power2'
            });
            
            // Move dialog options down with animation
            this.tweens.add({
                targets: this.dialogOptions,
                y: 200,
                duration: 300,
                ease: 'Power2',
                onComplete: () => {
                    this.dialogOptionsY = 200; // Update tracked position
                    callback();
                }
            });
        });

        return [optionBg, optionText];
    }

    showDialog(state) {
        // Destroy previous dialog if it exists
        if (this.dialogBox) {
            this.dialogBox.destroy();
        }

        this.dialogVisible = true;
        this.dialogState = state;
        const content = this.dialogContent[state];
        
        // Create new dialog box
        this.dialogBox = this.add.container(400, 300);
        this.dialogBox.setDepth(1000);
        
        // Dialog background
        const dialogBg = this.add.rectangle(0, 0, 600, 300, 0x0a2712, 0.9);
        dialogBg.setStrokeStyle(2, 0x7fff8e);
        this.dialogBox.add(dialogBg);

        // Dialog text
        this.dialogText = this.add.text(-280, -120, content.text, {
            fontSize: '24px',
            fill: '#7fff8e',
            wordWrap: { width: 560 },
            lineSpacing: 6
        });
        this.dialogBox.add(this.dialogText);

        // Create new dialog options container
        this.dialogOptions = this.add.container(0, this.dialogOptionsY);
        this.dialogBox.add(this.dialogOptions);
        
        // Create dialog options with increased spacing
        content.options.forEach((option, index) => {
            const y = index * 60;
            const elements = this.createDialogOption(option.text, y, () => {
                this.showDialog(option.next);
            });
            this.dialogOptions.add(elements);
        });
        
        // Add close option at the bottom with proper spacing
        const closeElements = this.createDialogOption('Close', content.options.length * 60, () => {
            this.dialogOptionsY = 0;
            this.hideDialog();
        });
        this.dialogOptions.add(closeElements);
    }

    hideDialog() {
        this.dialogVisible = false;
        if (this.dialogBox) {
            this.dialogBox.destroy();
            this.dialogBox = null;
        }
    }

    get dialogContent() {
        return {
            main: {
                text: "Greetings, seeker of truth. I am but a whisper in this strange city.",
                options: [
                    { text: "Tell me more about the city", next: 'city' },
                    { text: "Who are the fungal gods?", next: 'gods' }
                ]
            },
            city: {
                text: "This city... it breathes with ancient spores. The buildings grow like mushrooms in the dark, their patterns shifting when no one watches. Some say the entire city is one vast mycelial network, connecting all who dwell here in ways we cannot comprehend.",
                options: [
                    { text: "Ask about the gods", next: 'gods' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            gods: {
                text: "The fungal gods... they exist between reality and dream, like the thin membrane between cap and stem. They whisper through the spores we breathe, guiding us toward enlightenment... or perhaps madness. The distinction matters little in their realm.",
                options: [
                    { text: "Ask about the city", next: 'city' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            }
        };
    }

    update() {
        // Game loop updates will go here
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.GameScene = GameScene;
}
