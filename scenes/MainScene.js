import SaveSystem from '../systems/SaveSystem.js';

export default class MainScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MainScene' });
        console.log('MainScene constructor called');
        this.saveSystem = null;
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
            buttonBg.setInteractive({ useHandCursor: true });;

            // Add start game text
            const startText = this.add.text(400, 400, 'Start Game', {
                fontSize: '32px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            });
            startText.setOrigin(0.5);

            // Add Load Game button with matching style
            const loadGameBg = this.add.rectangle(400, 480, 200, 60, 0x0a2712, 0.4);
            loadGameBg.setStrokeStyle(2, 0x7fff8e);
            loadGameBg.setInteractive({ useHandCursor: true });

            const loadGameText = this.add.text(400, 480, 'Load Game', {
                fontSize: '32px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            });
            loadGameText.setOrigin(0.5);

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
            addHoverEffects(loadGameBg, loadGameText);

            // Add click handlers
            buttonBg.on('pointerdown', () => {
                this.clickSound.play();
                this.cameras.main.fadeOut(1000, 0, 0, 0);
                this.cameras.main.once('camerafadeoutcomplete', () => {
                    this.scene.start('IntroScene');
                    // this.scene.start('EntryScene');

                });
            });
            
            loadGameBg.on('pointerdown', () => {
                this.clickSound.play();
                this.showLoadMenu();
            });

            if (!this.backgroundMusic) {
                this.backgroundMusic = this.sound.add('mainMenuMusic', { loop: true });
            }
            this.sceneMusic = this.sound.add('mainMenuMusic', { loop: true });
            this.sceneMusic.play();
            
            // Initialize save system
            this.saveSystem = new SaveSystem(this);

            // Add F11 key handler for fullscreen
            this.input.keyboard.on('keydown-F11', (event) => {
                event.preventDefault();
                if (!document.fullscreenElement) {
                    this.scale.startFullscreen();
                    // Force resize after fullscreen
                    setTimeout(() => {
                        this.scale.resize(window.innerWidth, window.innerHeight);
                    }, 100);
                } else if (document.exitFullscreen) {
                    document.exitFullscreen();
                    // Force resize after exiting fullscreen
                    setTimeout(() => {
                        this.scale.resize(window.innerWidth, window.innerHeight);
                    }, 100);
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
        if (this.loadMenuVisible && this.saveNameInput) {
            // Update input position if the canvas size changes
            const gameCanvas = this.sys.game.canvas;
            const scale = this.scale.displayScale.x;
            const x = gameCanvas.offsetLeft + (this.cameras.main.width / 2 + 20) * scale;
            const y = gameCanvas.offsetTop + (this.cameras.main.height / 2 - 80) * scale;
            
            this.saveNameInput.style.left = `${x}px`;
            this.saveNameInput.style.top = `${y}px`;
        }
    }
    
    /**
     * Show the load game menu
     */
    showLoadMenu() {
        // Initialize save system if needed
        if (!this.saveSystem) {
            this.saveSystem = new SaveSystem(this);
        }
        
        // Create load menu container if it doesn't exist
        if (!this.loadMenuContainer) {
            this.createLoadMenu();
        }
        
        // Show the load menu
        this.loadMenuContainer.setVisible(true);
        this.loadMenuVisible = true;
        
        // Populate with save files
        this.populateLoadMenu();
    }
    
    /**
     * Create the load game menu
     */
    createLoadMenu() {
        this.loadMenuContainer = this.add.container(0, 0);
        this.loadMenuContainer.setDepth(1000);
        
        // Add a semi-transparent background
        const bg = this.add.rectangle(
            this.cameras.main.width / 2,
            this.cameras.main.height / 2,
            this.cameras.main.width,
            this.cameras.main.height,
            0x000000,
            0.7
        );
        this.loadMenuContainer.add(bg);
        
        // Add a panel background
        const panelBg = this.add.rectangle(
            this.cameras.main.width / 2,
            this.cameras.main.height / 2,
            500,
            400,
            0x0a2712,
            0.9
        );
        panelBg.setStrokeStyle(2, 0x7fff8e);
        this.loadMenuContainer.add(panelBg);
        
        // Add title
        const title = this.add.text(
            this.cameras.main.width / 2,
            this.cameras.main.height / 2 - 160,
            'LOAD GAME',
            {
                fontSize: '32px',
                fill: '#7fff8e',
                fontFamily: 'Arial',
                stroke: '#0a2712',
                strokeThickness: 4
            }
        );
        title.setOrigin(0.5);
        this.loadMenuContainer.add(title);
        
        // Add save slots container
        this.saveSlotContainer = this.add.container(0, 0);
        this.loadMenuContainer.add(this.saveSlotContainer);
        
        // Add back button
        const backButton = this.createButton(
            this.cameras.main.width / 2,
            this.cameras.main.height / 2 + 160,
            'Back',
            {
                fontSize: '28px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            },
            () => {
                this.loadMenuContainer.setVisible(false);
                this.loadMenuVisible = false;
            }
        );
        this.loadMenuContainer.add(backButton);
        
        // Add "No Save Files" text (will be hidden if saves exist)
        this.noSavesText = this.add.text(
            this.cameras.main.width / 2,
            this.cameras.main.height / 2,
            'No save files found',
            {
                fontSize: '24px',
                fill: '#7fff8e',
                fontFamily: 'Arial',
                align: 'center'
            }
        );
        this.noSavesText.setOrigin(0.5);
        this.loadMenuContainer.add(this.noSavesText);
        
        // Hide the load menu initially
        this.loadMenuContainer.setVisible(false);
        this.loadMenuVisible = false;
    }
    
    /**
     * Create a button with hover effects
     */
    createButton(x, y, text, style, callback) {
        const container = this.add.container(x, y);
        
        // Button background
        const bg = this.add.rectangle(0, 0, 300, 60, 0x0a2712, 0.4);
        bg.setStrokeStyle(2, 0x7fff8e);
        container.add(bg);
        
        // Button text
        const buttonText = this.add.text(0, 0, text, style);
        buttonText.setOrigin(0.5);
        container.add(buttonText);
        
        // Make interactive
        bg.setInteractive({ useHandCursor: true });
        
        // Add hover effects
        bg.on('pointerover', () => {
            bg.setFillStyle(0x0a2712, 0.6);
            buttonText.setStyle({ ...style, fill: '#2fff91' });
            this.hoverSound.play();
        });
        
        bg.on('pointerout', () => {
            bg.setFillStyle(0x0a2712, 0.4);
            buttonText.setStyle({ ...style, fill: '#7fff8e' });
        });
        
        // Add click handler
        bg.on('pointerdown', () => {
            this.clickSound.play();
            if (callback) callback();
        });
        
        return container;
    }
    
    /**
     * Populate the load menu with save files
     */
    populateLoadMenu() {
        // Clear previous save slots
        this.saveSlotContainer.removeAll(true);
        
        const saveFiles = this.saveSystem.listSaveFiles();
        
        if (saveFiles.length === 0) {
            this.noSavesText.setVisible(true);
            return;
        }
        
        this.noSavesText.setVisible(false);
        
        // Sort save files by date (newest first)
        saveFiles.sort((a, b) => new Date(b.date) - new Date(a.date));
        
        // Add save slots
        const slotY = this.cameras.main.height / 2 - 80;
        const slotSpacing = 60;
        
        saveFiles.forEach((saveFile, index) => {
            if (index >= 5) return; // Limit to 5 save slots
            
            const date = new Date(saveFile.date);
            const formattedDate = `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
            
            // Create slot container
            const slotContainer = this.add.container(
                this.cameras.main.width / 2,
                slotY + index * slotSpacing
            );
            
            // Add slot background
            const slotBg = this.add.rectangle(0, 0, 450, 50, 0x000000, 0.6);
            slotBg.setStrokeStyle(1, 0x7fff8e);
            slotBg.setInteractive({ useHandCursor: true });
            slotContainer.add(slotBg);
            
            // Add slot text
            const slotText = this.add.text(
                -210,
                0,
                `${saveFile.name}`,
                {
                    fontSize: '22px',
                    fill: '#7fff8e',
                    fontFamily: 'Arial'
                }
            );
            slotText.setOrigin(0, 0.5);
            slotContainer.add(slotText);
            
            // Add date text
            const dateText = this.add.text(
                210,
                0,
                formattedDate,
                {
                    fontSize: '16px',
                    fill: '#7fff8e',
                    fontFamily: 'Arial'
                }
            );
            dateText.setOrigin(1, 0.5);
            slotContainer.add(dateText);
            
            // Add hover effects
            slotBg.on('pointerover', () => {
                slotBg.setFillStyle(0x0a2712, 0.8);
                slotText.setStyle({ fontSize: '22px', fill: '#2fff91', fontFamily: 'Arial' });
                dateText.setStyle({ fontSize: '16px', fill: '#2fff91', fontFamily: 'Arial' });
                this.hoverSound.play();
            });
            
            slotBg.on('pointerout', () => {
                slotBg.setFillStyle(0x000000, 0.6);
                slotText.setStyle({ fontSize: '22px', fill: '#7fff8e', fontFamily: 'Arial' });
                dateText.setStyle({ fontSize: '16px', fill: '#7fff8e', fontFamily: 'Arial' });
            });
            
            // Add click handler
            slotBg.on('pointerdown', () => {
                this.clickSound.play();
                this.loadGame(saveFile.name);
            });
            
            this.saveSlotContainer.add(slotContainer);
        });
    }
    
    /**
     * Load a saved game
     */
    async loadGame(slotName) {
        try {
            console.log('Loading game from slot:', slotName);
            
            // Use the game API to load the game
            const result = window.gameAPI ? window.gameAPI.loadGame(slotName) : { success: false, error: 'Game API not available' };
            
            if (result.success) {
                const saveData = result.data;
                console.log('Save data loaded:', saveData);
                
                // Store save data in registry for access by other scenes
                this.registry.set('savedData', saveData);
                
                // Store individual system data in registry
                if (saveData.quests) this.registry.set('savedQuests', saveData.quests);
                if (saveData.journal) this.registry.set('savedJournal', saveData.journal);
                if (saveData.symbionts) this.registry.set('savedSymbionts', saveData.symbionts);
                if (saveData.factions) this.registry.set('savedFactions', saveData.factions);
                if (saveData.effects) this.registry.set('savedEffects', saveData.effects);
                if (saveData.spores) this.registry.set('savedSpores', saveData.spores);
                if (saveData.money) this.registry.set('savedMoney', saveData.money);
                if (saveData.inventory) this.registry.set('inventory', saveData.inventory);
                if (saveData.growthDecay) this.registry.set('growthDecayBalance', saveData.growthDecay);
                if (saveData.usedDialogOptions) this.registry.set('usedDialogOptions', new Map(saveData.usedDialogOptions));
                
                // Start the saved scene
                const targetScene = saveData.currentScene || 'GameScene';
                
                this.cameras.main.fadeOut(1000, 0, 0, 0);
                this.cameras.main.once('camerafadeoutcomplete', () => {
                    // Stop music
                    if (this.sceneMusic) {
                        this.sceneMusic.stop();
                    }
                    
                    // Start the scene with loaded data
                    this.scene.start(targetScene, { 
                        loadedPosition: saveData.player.position,
                        loadedSave: true // Flag to indicate this is a loaded save
                    });
                });
                
                // Show notification
                if (this.showNotification) {
                    this.showNotification('Loading game...', 0x00ff00);
                }
            } else {
                console.error('Failed to load game:', result.error);
                if (this.showNotification) {
                    this.showNotification('Failed to load game: ' + result.error, 0xff0000);
                }
            }
        } catch (error) {
            console.error('Error loading game:', error);
            if (this.showNotification) {
                this.showNotification('Error loading game: ' + error.message, 0xff0000);
            }
        }
    }
}
