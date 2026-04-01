import SaveSystem from '../systems/SaveSystem.js';
import LanguageSystem from '../systems/LanguageSystem.js';

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

            const i18n = LanguageSystem.getInstance();

            const title = this.add.text(400, 170, 'Upper Morkezela:', {
                fontSize: '72px',
                fill: '#7fff8e',
                fontFamily: 'Arial',
                stroke: '#0a2712',
                strokeThickness: 8,
                shadow: { color: '#2fff91', blur: 10, stroke: true, fill: true }
            })

            const subTitle = this.add.text(400, 250, 'A Weird Game', {
                fontSize: '72px',
                fill: '#7fff8e',
                fontFamily: 'Arial',
                stroke: '#0a2712',
                strokeThickness: 8,
                shadow: { color: '#2fff91', blur: 10, stroke: true, fill: true }
            })


            title.setOrigin(0.5)
            subTitle.setOrigin(0.5)

            // Create button background
            const buttonBg = this.add.rectangle(400, 400, 200, 60, 0x0a2712, 0.4);
            buttonBg.setStrokeStyle(2, 0x7fff8e);
            buttonBg.setInteractive({ useHandCursor: true });;

            // Add start game text
            const startText = this.add.text(400, 400, i18n.t('ui.menu.startGame'), {
                fontSize: '32px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            });
            startText.setOrigin(0.5);

            // Add Load Game button with matching style
            const loadGameBg = this.add.rectangle(400, 480, 200, 60, 0x0a2712, 0.4);
            loadGameBg.setStrokeStyle(2, 0x7fff8e);
            loadGameBg.setInteractive({ useHandCursor: true });

            const loadGameText = this.add.text(400, 480, i18n.t('ui.menu.loadGame'), {
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

            // Add Language button
            this.langSystem = LanguageSystem.getInstance();
            const currentLang = this.langSystem.supportedLanguages.find(
                l => l.code === this.langSystem.getLanguage()
            );

            const langBg = this.add.rectangle(400, 540, 200, 50, 0x0a2712, 0.4);
            langBg.setStrokeStyle(2, 0x7fff8e);
            langBg.setInteractive({ useHandCursor: true });

            this.langText = this.add.text(400, 540, currentLang ? currentLang.name : 'Language', {
                fontSize: '24px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            });
            this.langText.setOrigin(0.5);

            addHoverEffects(langBg, this.langText);

            langBg.on('pointerdown', () => {
                this.clickSound.play();
                this.showLanguageModal(addHoverEffects);
            });

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
     * Show the language selection modal
     */
    showLanguageModal(addHoverEffects) {
        if (this.langModal) return;

        const cx = this.cameras.main.width / 2;
        const cy = this.cameras.main.height / 2;
        const langs = this.langSystem.supportedLanguages;
        const currentCode = this.langSystem.getLanguage();

        this.langModal = this.add.container(0, 0);
        this.langModal.setDepth(2000);

        // Dim overlay
        const overlay = this.add.rectangle(cx, cy, 800, 600, 0x000000, 0.7);
        overlay.setInteractive(); // blocks clicks to elements beneath
        this.langModal.add(overlay);

        // Panel
        const panelH = 60 + langs.length * 60 + 60;
        const panel = this.add.rectangle(cx, cy, 320, panelH, 0x0a2712, 0.95);
        panel.setStrokeStyle(2, 0x7fff8e);
        this.langModal.add(panel);

        // Title
        const title = this.add.text(cx, cy - panelH / 2 + 30, this.langSystem.t('ui.menu.language'), {
            fontSize: '28px',
            fill: '#7fff8e',
            fontFamily: 'Arial'
        });
        title.setOrigin(0.5);
        this.langModal.add(title);

        // Language options
        langs.forEach((lang, idx) => {
            const y = cy - panelH / 2 + 80 + idx * 60;
            const isActive = lang.code === currentCode;

            const optBg = this.add.rectangle(cx, y, 260, 44, 0x0a2712, isActive ? 0.8 : 0.4);
            optBg.setStrokeStyle(isActive ? 2 : 1, isActive ? 0x2fff91 : 0x7fff8e);
            optBg.setInteractive({ useHandCursor: true });

            const optText = this.add.text(cx, y, lang.name, {
                fontSize: '24px',
                fill: isActive ? '#2fff91' : '#7fff8e',
                fontFamily: 'Arial',
                fontStyle: isActive ? 'bold' : ''
            });
            optText.setOrigin(0.5);

            if (!isActive) {
                addHoverEffects(optBg, optText);
            }

            optBg.on('pointerdown', () => {
                if (lang.code === currentCode) {
                    // Close modal when clicking already-active language
                    this.clickSound.play();
                    this.langModal.destroy();
                    this.langModal = null;
                    return;
                }
                this.clickSound.play();
                this.langSystem.setLanguage(lang.code);
                if (this.sceneMusic) this.sceneMusic.stop();
                this.scene.restart();
            });

            this.langModal.add([optBg, optText]);
        });

        // Close on overlay click
        overlay.on('pointerdown', () => {
            this.clickSound.play();
            this.langModal.destroy();
            this.langModal = null;
        });
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
            550,
            0x0a2712,
            0.9
        );
        panelBg.setStrokeStyle(2, 0x7fff8e);
        this.loadMenuContainer.add(panelBg);
        
        // Add title
        const title = this.add.text(
            this.cameras.main.width / 2,
            this.cameras.main.height / 2 - 230,
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
        this.saveSlotContainer = this.add.container(this.cameras.main.width / 2, this.cameras.main.height / 2);
        this.loadMenuContainer.add(this.saveSlotContainer);
        
        // Add back button
        const backButton = this.createButton(
            this.cameras.main.width / 2,
            this.cameras.main.height / 2 + 230,
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
        console.log('Populating load menu');
        // Clear existing save slots
        this.saveSlotContainer.removeAll(true);
        
        // Debug: Check localStorage directly
        console.log('Checking localStorage directly:');
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('weird-game-save-')) {
                console.log(`Found save in localStorage: ${key}`);
            }
        }
        
        // Get save files
        const saveFilesResult = window.gameAPI ? window.gameAPI.listSaveFiles() : { success: false, files: [] };
        console.log('Save files result:', saveFilesResult);
        
        if (!saveFilesResult.success || !saveFilesResult.files || saveFilesResult.files.length === 0) {
            // No save files found - clear any existing content first
            this.saveSlotContainer.removeAll(true);
            
            const noSavesText = this.add.text(0, 0, 'No save files found', {
                fontSize: '24px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            });
            noSavesText.setOrigin(0.5);
            this.saveSlotContainer.add(noSavesText);
            return;
        }
        
        // Debug: Log the files we found
        console.log(`Found ${saveFilesResult.files.length} save files to display`);
        saveFilesResult.files.forEach((file, index) => {
            console.log(`Save file ${index}: ${file.name}, date: ${file.displayDate}`);
        });
        
        // Add save slots
        let yPos = -190;
        
        // Clear all existing content to prevent duplicates
        this.saveSlotContainer.removeAll(true);
        
        // Limit to 6 save slots to match in-game save menu
        const filesToShow = saveFilesResult.files.slice(0, 6);
        
        // Double check we have files to show
        if (filesToShow.length === 0) {
            const noSavesText = this.add.text(0, 0, 'No save files found', {
                fontSize: '24px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            });
            noSavesText.setOrigin(0.5);
            this.saveSlotContainer.add(noSavesText);
            return;
        }
        
        filesToShow.forEach(saveFile => {
            console.log('Processing save file:', saveFile);
            // Create container for this save slot
            const slotContainer = this.add.container(0, yPos);
            
            // Create background
            const slotBg = this.add.rectangle(0, 0, 300, 60, 0x000000, 0.6);
            slotBg.setStrokeStyle(1, 0x7fff8e);
            slotBg.setInteractive({ useHandCursor: true });
            
            // Add subtle fungal decoration
            const decoration = this.add.graphics();
            decoration.fillStyle(0x7fff8e, 0.2);
            decoration.fillCircle(-150, 0, 5);
            decoration.fillCircle(-140, -20, 3);
            decoration.fillCircle(-160, 15, 4);
            slotContainer.add(decoration);
            
            // Format date
            let dateString = 'Unknown date';
            if (saveFile.displayDate) {
                dateString = saveFile.displayDate;
            } else if (saveFile.date) {
                try {
                    const date = new Date(saveFile.date);
                    dateString = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
                } catch (e) {
                    console.error('Error formatting date:', e);
                }
            }
            
            // Add text - simplified for main menu
            const slotText = this.add.text(-120, -10, `${saveFile.name}`, {
                fontSize: '20px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            });
            
            const dateText = this.add.text(-120, 15, dateString, {
                fontSize: '14px',
                fill: '#5c9b6b',
                fontFamily: 'Arial'
            });
            
            // Add scene info if available (simplified)
            if (saveFile.scene && saveFile.scene !== 'Unknown') {
                const sceneText = this.add.text(80, 0, saveFile.scene, {
                    fontSize: '16px',
                    fill: '#7fff8e',
                    fontFamily: 'Arial'
                });
                slotContainer.add(sceneText);
            }
            
            // Add error indicator if there was an error parsing the save
            if (saveFile.error) {
                const errorText = this.add.text(80, 0, '⚠️ Error', {
                    fontSize: '16px',
                    fill: '#ff0000',
                    fontFamily: 'Arial'
                });
                slotContainer.add(errorText);
            }
            
            // Add all elements to container
            slotContainer.add([slotBg, slotText, dateText]);
            
            // Add hover effect
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
            yPos += 65; // Move down for the next slot
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
