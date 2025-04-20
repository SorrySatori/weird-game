class GameScene extends Phaser.Scene {
    constructor(config = { key: 'GameScene' }) {
        super(config);
        this.dialogVisible = false;
        this.dialogState = 'main';
        this.dialogOptionsY = 0; // Track options position
        this.isTransitioning = false; // Flag to prevent multiple transitions
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
        this.load.image('fungalPriestAvatar', 'assets/images/fungal-priest.png');

        // Load sound assets
        this.load.audio('backgroundMusic', 'assets/sounds/background-music.wav');
        this.load.audio('clickSound', 'assets/sounds/click.wav');
        this.load.audio('dialogMurmur', 'assets/sounds/dialog-murmur.wav');

        // Handle load errors
        this.load.on('loaderror', (fileObj) => {
            console.log('Error loading asset:', fileObj.key);
        });
    }

    create() {
        this.createCityBackground();
        this.initSceneMechanics();
    }

    createCityBackground() {
        // Add the city background
        const bg = this.add.image(400, 300, 'cityBackground');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
    }

    initSceneMechanics() {
        try {
            // Add ground/street platform
            const ground = this.add.tileSprite(400, 550, 800, 100, 'ground');
            ground.setDisplaySize(800, 100);

            // Start background music
            this.backgroundMusic = this.sound.add('backgroundMusic', { loop: true });
            this.backgroundMusic.play();

            // Add click sound
            this.clickSound = this.sound.add('clickSound');
            
            // Add dialog murmur sound
            this.dialogMurmur = this.sound.add('dialogMurmur');

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
            
            // Apply a darker brown fungal tint
            this.priest.setTint(0x8B4513);  // Darker brown for more fungal look
            
            // Create a simpler staff for the priest
            this.staff = this.add.graphics();
            this.staff.lineStyle(3, 0x8B4513, 1); // Thinner brown staff stick
            this.staff.lineBetween(0, 0, 0, -50); // Slightly shorter staff
            
            // Add a glowing orb at the top of the staff
            this.staffOrb = this.add.circle(0, -55, 6, 0x00FF00, 0.8);
            this.staffOrb.setBlendMode(Phaser.BlendModes.ADD);
            
            // Remove the separate arms and hands graphics
            if (this.lowerArm) this.lowerArm.destroy();
            if (this.upperArm) this.upperArm.destroy();
            if (this.priestHand) this.priestHand.destroy();
            if (this.priestHandUpper) this.priestHandUpper.destroy();
            
            // Add pulsating effect to the staff orb
            this.tweens.add({
                targets: this.staffOrb,
                alpha: 0.4,
                duration: 1000,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
            
            // Position the staff relative to the priest
            this.updateStaffPosition(1); // 1 = facing right
            
            // Add a green glow effect for the fungal appearance
            const glowFX = this.add.sprite(100, 470, 'priest');
            glowFX.setScale(2.1);  // Slightly larger than the character
            glowFX.setTint(0x00FF00);  // Green glow
            glowFX.setAlpha(0.2);  // Transparent glow
            glowFX.setBlendMode(Phaser.BlendModes.ADD);  // Additive blending for glow effect
            
            // Make the glow follow the priest
            this.priestGlow = glowFX;
            
            // Add pulsating effect to the glow
            this.tweens.add({
                targets: this.priestGlow,
                alpha: 0.3,
                duration: 1500,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
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
            
            // Only add the Stranger if not EggCatedralScene
            if (!this.isEggCatedral()) {
                this.stranger = this.add.sprite(600, 470, 'stranger');
                this.stranger.setScale(2);
                this.stranger.setInteractive({ useHandCursor: true });
                // Handle cursor visibility for stranger
                this.input.on('gameobjectover', (pointer, gameObject) => {
                    if (gameObject === this.stranger) {
                        this.cursor.setAlpha(0);
                    }
                });
                this.input.on('gameobjectout', (pointer, gameObject) => {
                    if (gameObject === this.stranger) {
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
            }

            // Add click/tap handler for movement
            this.input.on('pointerdown', (pointer) => {
                if (!this.dialogVisible && pointer.y < 500) {
                    const targetX = pointer.x;
                    const direction = targetX < this.priest.x ? -1 : 1;
                    this.clickSound.play();
                    this.priest.setScale(2 * direction, 2);
                    this.priestGlow.setScale(2.1 * direction, 2.1);  // Flip the glow too
                    this.priestGlow.x = this.priest.x;  // Keep glow aligned with priest
                    this.updateStaffPosition(direction); // Update staff position
                    this.priest.play('walk');
                    
                    this.tweens.add({
                        targets: [this.priest, this.priestGlow],  // Move both priest and glow
                        x: targetX,
                        duration: Math.abs(targetX - this.priest.x) * 5,
                        ease: 'Linear',
                        onUpdate: () => {
                            // Update staff position as priest moves
                            const direction = targetX < this.priest.x ? -1 : 1;
                            this.updateStaffPosition(direction);
                        },
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

            // Avatar sprite for dialog (hidden by default)
            this.avatar = this.add.image(-250, 0, 'fungalPriestAvatar');
            this.avatar.setDisplaySize(128, 128);
            this.avatar.setVisible(false);
            // Move avatar to top right corner
            this.avatar.setPosition(800 - 64, 64); // Assuming 800x600 game size
            // Ensure avatar is above background but below dialog box
            this.avatar.setDepth(999);

        } catch (error) {
            console.error('Error in create():', error);
        }
    }

    // Helper to determine if this is EggCatedralScene
    isEggCatedral() {
        return this.scene && this.scene.key === 'EggCatedralScene';
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
            this.dialogMurmur.play();
            
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
                    // Play dialog murmur sound before showing next dialog
                    this.dialogMurmur.play({
                        volume: 0.8,
                        rate: 0.8
                    });
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
        if (this.textMaskGraphics) {
            this.textMaskGraphics.destroy();
        }
        if (this.avatar) {
            this.avatar.setVisible(true);
            // Keep avatar at top right
            this.avatar.setPosition(800 - 64, 64);
        }

        this.dialogVisible = true;
        this.dialogState = state;
        const content = this.dialogContent[state];
        
        // Create new dialog box
        this.dialogBox = this.add.container(400, 300);
        this.dialogBox.setDepth(1000);
        
        // Dialog background
        const dialogBg = this.add.rectangle(0, 0, 600, 400, 0x0a2712, 0.9);
        dialogBg.setStrokeStyle(2, 0x7fff8e);
        this.dialogBox.add(dialogBg);

        // Add 'X' close button
        const closeBtn = this.add.container(280, -180);
        const closeBg = this.add.rectangle(0, 0, 40, 40, 0x0a2712, 0.6);
        closeBg.setStrokeStyle(1, 0x7fff8e);
        const closeText = this.add.text(0, 0, 'X', {
            fontSize: '24px',
            fill: '#7fff8e'
        });
        closeText.setOrigin(0.5);
        closeBtn.add([closeBg, closeText]);
        this.dialogBox.add(closeBtn);

        // Make close button interactive
        closeBg.setInteractive({ useHandCursor: true });
        closeBg.on('pointerover', () => {
            closeBg.setFillStyle(0x0a2712, 0.8);
            closeText.setStyle({ fill: '#b3ffcc' });
        });
        closeBg.on('pointerout', () => {
            closeBg.setFillStyle(0x0a2712, 0.6);
            closeText.setStyle({ fill: '#7fff8e' });
        });
        closeBg.on('pointerdown', () => {
            this.clickSound.play();
            this.hideDialog();
        });

        // Create a separate container for text area with fixed height
        const textContainer = this.add.container(0, -120);
        this.dialogBox.add(textContainer);
        
        // Create background for text area
        const textBgHeight = 120;
        const textBg = this.add.rectangle(0, 0, 560, textBgHeight, 0x0a2712, 0.8);
        textBg.setStrokeStyle(1, 0x7fff8e);
        textContainer.add(textBg);
        
        // Create mask for scrollable text
        this.textMaskGraphics = this.add.graphics();
        this.textMaskGraphics.fillStyle(0xffffff);
        this.textMaskGraphics.fillRect(400 - 270, 300 - 180, 540, textBgHeight - 10);
        
        // Create text with proper wrapping
        this.dialogText = this.add.text(0, -(textBgHeight/2) + 10, content.text, {
            fontSize: '22px',
            fill: '#7fff8e',
            wordWrap: { width: 520 },
            lineSpacing: 6,
            align: 'center'
        });
        this.dialogText.setOrigin(0.5, 0);
        textContainer.add(this.dialogText);
        
        // Set up text scrolling if needed
        const textHeight = this.dialogText.height;
        const textAreaHeight = textBgHeight - 20; // Account for padding
        
        if (textHeight > textAreaHeight) {
            // Text needs scrolling
            this.dialogText.setMask(new Phaser.Display.Masks.GeometryMask(this, this.textMaskGraphics));
            
            // Add scroll indicators
            const upArrow = this.add.text(-260, -(textBgHeight/2) + 5, '▲', {
                fontSize: '18px',
                fill: '#7fff8e'
            });
            upArrow.setOrigin(0.5);
            textContainer.add(upArrow);
            
            const downArrow = this.add.text(-260, (textBgHeight/2) - 5, '▼', {
                fontSize: '18px',
                fill: '#7fff8e'
            });
            downArrow.setOrigin(0.5);
            textContainer.add(downArrow);
            
            // Make arrows interactive
            upArrow.setInteractive({ useHandCursor: true });
            upArrow.on('pointerover', () => upArrow.setStyle({ fill: '#b3ffcc' }));
            upArrow.on('pointerout', () => upArrow.setStyle({ fill: '#7fff8e' }));
            upArrow.on('pointerdown', () => {
                this.clickSound.play();
                if (this.dialogText.y < -(textBgHeight/2) + 10) {
                    this.dialogText.y += 20;
                    if (this.dialogText.y > -(textBgHeight/2) + 10) {
                        this.dialogText.y = -(textBgHeight/2) + 10;
                    }
                }
            });
            
            downArrow.setInteractive({ useHandCursor: true });
            downArrow.on('pointerover', () => downArrow.setStyle({ fill: '#b3ffcc' }));
            downArrow.on('pointerout', () => downArrow.setStyle({ fill: '#7fff8e' }));
            downArrow.on('pointerdown', () => {
                this.clickSound.play();
                const minY = -(textBgHeight/2) + 10 - (textHeight - textAreaHeight);
                if (this.dialogText.y > minY) {
                    this.dialogText.y -= 20;
                    if (this.dialogText.y < minY) {
                        this.dialogText.y = minY;
                    }
                }
            });
            
            // Add mouse wheel support
            this.input.on('wheel', (pointer, gameObjects, deltaX, deltaY, deltaZ) => {
                if (this.dialogVisible && pointer.y < 300) {
                    const scrollAmount = deltaY > 0 ? -20 : 20;
                    const newY = this.dialogText.y + scrollAmount;
                    const minY = -(textBgHeight/2) + 10 - (textHeight - textAreaHeight);
                    
                    if (newY <= -(textBgHeight/2) + 10 && newY >= minY) {
                        this.dialogText.y = newY;
                    } else if (newY > -(textBgHeight/2) + 10) {
                        this.dialogText.y = -(textBgHeight/2) + 10;
                    } else if (newY < minY) {
                        this.dialogText.y = minY;
                    }
                }
            });
        }
        
        // Create options container - positioned well below the text area
        const optionsContainer = this.add.container(0, 0);
        this.dialogBox.add(optionsContainer);
        
        // Create dialog options container
        this.dialogOptions = this.add.container(0, 0);
        optionsContainer.add(this.dialogOptions);
        
        // Create dialog options
        const visibleOptionsCount = 4; // Maximum number of visible options
        const optionHeight = 60;
        
        // Calculate total options including "Close"
        const totalOptions = content.options.length + 1;
        
        // Determine if we need pagination
        const needsPagination = totalOptions > visibleOptionsCount;
        
        // Track current page
        this.currentOptionPage = 0;
        const totalPages = Math.ceil(totalOptions / visibleOptionsCount);
        
        // Function to show options for current page
        const showOptionsForPage = (page) => {
            // Clear existing options
            this.dialogOptions.removeAll(true);
            
            // Calculate start and end indices for current page
            const startIdx = page * visibleOptionsCount;
            const endIdx = Math.min(startIdx + visibleOptionsCount, content.options.length);
            
            // Add options for current page
            for (let i = startIdx; i < endIdx; i++) {
                const option = content.options[i];
                const y = (i - startIdx) * optionHeight;
                
                const elements = this.createDialogOption(option.text, y, () => {
                    this.showDialog(option.next);
                });
                this.dialogOptions.add(elements);
            }
            
            // Add close option if it fits on this page
            if (endIdx === content.options.length && (endIdx - startIdx) < visibleOptionsCount) {
                const y = (endIdx - startIdx) * optionHeight;
                const closeElements = this.createDialogOption('Close', y, () => {
                    this.hideDialog();
                });
                this.dialogOptions.add(closeElements);
            }
            
            // Add pagination controls if needed
            if (needsPagination) {
                // Add page indicator
                const pageText = this.add.text(0, visibleOptionsCount * optionHeight + 20, 
                    `Page ${page + 1}/${totalPages}`, {
                    fontSize: '18px',
                    fill: '#7fff8e'
                });
                pageText.setOrigin(0.5, 0);
                this.dialogOptions.add(pageText);
                
                // Previous page button
                if (page > 0) {
                    const prevBtn = this.add.container(-100, visibleOptionsCount * optionHeight + 20);
                    const prevBg = this.add.rectangle(0, 0, 80, 30, 0x0a2712, 0.6);
                    prevBg.setStrokeStyle(1, 0x7fff8e);
                    const prevText = this.add.text(0, 0, '< Prev', {
                        fontSize: '18px',
                        fill: '#7fff8e'
                    });
                    prevText.setOrigin(0.5);
                    prevBtn.add([prevBg, prevText]);
                    this.dialogOptions.add(prevBtn);
                    
                    prevBg.setInteractive({ useHandCursor: true });
                    prevBg.on('pointerover', () => {
                        prevBg.setFillStyle(0x0a2712, 0.8);
                        prevText.setStyle({ fill: '#b3ffcc' });
                    });
                    prevBg.on('pointerout', () => {
                        prevBg.setFillStyle(0x0a2712, 0.6);
                        prevText.setStyle({ fill: '#7fff8e' });
                    });
                    prevBg.on('pointerdown', () => {
                        this.clickSound.play();
                        this.currentOptionPage--;
                        showOptionsForPage(this.currentOptionPage);
                    });
                }
                
                // Next page button
                if (page < totalPages - 1) {
                    const nextBtn = this.add.container(100, visibleOptionsCount * optionHeight + 20);
                    const nextBg = this.add.rectangle(0, 0, 80, 30, 0x0a2712, 0.6);
                    nextBg.setStrokeStyle(1, 0x7fff8e);
                    const nextText = this.add.text(0, 0, 'Next >', {
                        fontSize: '18px',
                        fill: '#7fff8e'
                    });
                    nextText.setOrigin(0.5);
                    nextBtn.add([nextBg, nextText]);
                    this.dialogOptions.add(nextBtn);
                    
                    nextBg.setInteractive({ useHandCursor: true });
                    nextBg.on('pointerover', () => {
                        nextBg.setFillStyle(0x0a2712, 0.8);
                        nextText.setStyle({ fill: '#b3ffcc' });
                    });
                    nextBg.on('pointerout', () => {
                        nextBg.setFillStyle(0x0a2712, 0.6);
                        nextText.setStyle({ fill: '#7fff8e' });
                    });
                    nextBg.on('pointerdown', () => {
                        this.clickSound.play();
                        this.currentOptionPage++;
                        showOptionsForPage(this.currentOptionPage);
                    });
                }
            }
        };
        
        // Show options for the first page
        showOptionsForPage(0);
    }

    hideDialog() {
        if (this.dialogBox) {
            this.dialogBox.destroy();
            this.dialogBox = null;
        }
        if (this.textMaskGraphics) {
            this.textMaskGraphics.destroy();
            this.textMaskGraphics = null;
        }
        this.dialogVisible = false;
        // Hide avatar on dialog close
        if (this.avatar) {
            this.avatar.setVisible(false);
        }
    }

    get dialogContent() {
        return {
            main: {
                text: "Greetings, seeker of truth. I am but a whisper in this strange city, messenger of the fungal gods",
                options: [
                    { text: "Tell me more about the city", next: 'city' },
                    { text: "Who are the fungal gods?", next: 'gods' }
                ]
            },
            city: {
                text: "This city... it breathes with ancient spores. The buildings grow like mushrooms in the dark, their patterns shifting when no one watches. Some say the entire city is one vast mycelial network, connecting all who dwell here in ways we cannot comprehend.",
                options: [
                    { text: "Ask about the gods", next: 'gods' },
                    { text: "Tell me more about city locations.", next: 'locations' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            gods: {
                text: "The fungal gods... they exist between reality and dream, like the thin membrane between cap and stem. They whisper through the spores we breathe, guiding us toward enlightenment... or perhaps madness. The distinction matters little in their realm.",
                options: [
                    { text: "Ask about the city", next: 'city' },
                    { text: "Where can I learn more about the fungal gods?", next: 'priests' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            priests: {
                text: "Go to the Egg Catedral and talk to some of the priests there. They are always happy to chat.",
                options: [
                    { text: "What is the Egg Catedral?", next: 'eggCatedral' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            eggCatedral: {
                text: "The Egg Cathedral is, well, a huge catedral that is hatching from gigantic egg. A massive, shell-grown structure inhabited by fungal clergy, flickering with bio-luminescent scripture...",
                options: [
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            locations: {
                text: "The city has many locations, but the most significant ones are the Candlepit of Saint Hesh, the Yolk Sea, Midwives’ Ossuary, Sporewind Graves, and the Stomach Clock. Which one interests you?",
                options: [
                    { text: "Candlepit of Saint Hesh", next: 'candlepit' },
                    { text: "Yolk Sea", next: 'yolkSea' },
                    { text: "Midwives’ Ossuary", next: 'midwivesOssuary' },
                    { text: "Sporewind Graves", next: 'sporewindGraves' },
                    { text: "Stomach Clock", next: 'stomachClock' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            candlepit: {
                text: "The Candlepit of Saint Hesh is a Circular wax catacomb with memory-melting rituals and speaking wounds. It is located beneath the Egg Cathedral.",
                options: [
                    { text: 'What is the Egg Cathedral?', next: 'eggCatedral' },
                    { text: 'What is the Yolk Sea?', next: 'yolkSea' },
                    { text: 'What is the Midwives’ Ossuary?', next: 'midwivesOssuary' },
                    { text: 'What is the Sporewind Graves?', next: 'sporewindGraves' },
                    { text: 'What is the Stomach Clock?', next: 'stomachClock' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            yolkSea: {
                text: "The Yolk Sea is a glowing, sentient ocean of living yolk. Boats float like seeds, and whispers rise from its depths.",
                options: [
                    { text: 'What is the Candlepit of Saint Hesh?', next: 'candlepit' },
                    { text: 'What is the Midwives’ Ossuary?', next: 'midwivesOssuary' },
                    { text: 'What is the Sporewind Graves?', next: 'sporewindGraves' },
                    { text: 'What is the Stomach Clock?', next: 'stomachClock' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            midwivesOssuary: {
                text: "The Midwives’ Ossuary is a Pelvis-shaped crypt filled with midwife husks who sew memory threads into your bones.",
                options: [
                    { text: 'What is the Yolk Sea?', next: 'yolkSea' },
                    { text: 'What is the Sporewind Graves?', next: 'sporewindGraves' },
                    { text: 'What is the Stomach Clock?', next: 'stomachClock' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            sporewindGraves: {
                text: "The Sporewind Graves is a foggy fungal plains with drifting memory apparitions.",
                options: [
                    { text: 'What is the Yolk Sea?', next: 'yolkSea' },
                    { text: 'What is the Midwives’ Ossuary?', next: 'midwivesOssuary' },
                    { text: 'What is the Stomach Clock?', next: 'stomachClock' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            stomachClock: {
                text: "The Stomach Clock is a biomechanical chamber shaped like a digestive clock. Time runs in loops; bile is sacred. You can see it at the townhall",
                options: [
                    { text: 'What is the Yolk Sea?', next: 'yolkSea' },
                    { text: 'What is the Midwives’ Ossuary?', next: 'midwivesOssuary' },
                    { text: 'What is the Sporewind Graves?', next: 'sporewindGraves' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            }
        };
    }

    updateStaffPosition(direction) {
        // Position staff based on direction priest is facing
        const offsetX = direction > 0 ? 15 : -15; // Staff closer to body
        
        // Position the staff
        this.staff.x = this.priest.x + offsetX;
        this.staff.y = this.priest.y - 10;
        this.staffOrb.x = this.staff.x;
        this.staffOrb.y = this.staff.y - 55; // Adjusted for shorter staff
    }

    update() {
        // Game loop updates will go here
        
        // Only handle scene transitions in the main GameScene, not in scenes that extend it
        if (this.scene.key === 'GameScene') {
            // Check if priest reaches right edge (adjusted threshold)
            if (this.priest && this.priest.x >= 750 && !this.isTransitioning) {
                this.isTransitioning = true;
                this.cameras.main.fadeOut(800, 0, 0, 0);
                this.cameras.main.once('camerafadeoutcomplete', () => {
                    this.scene.start('EggCatedralScene');
                    this.isTransitioning = false;
                });
            }
        }
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.GameScene = GameScene;
}
