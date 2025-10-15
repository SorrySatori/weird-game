/**
 * GameMenu.js - In-game menu system triggered by ESC key
 */
export default class GameMenu {
    /**
     * @param {Phaser.Scene} scene - The scene this menu belongs to
     */
    constructor(scene) {
        this.scene = scene;
        this.visible = false;
        this.container = null;
        this.saveSystem = null;
        this.saveSlot = 'save1';
        
        // Sound effects
        this.hoverSound = scene.sound.add('hoverSound');
        this.clickSound = scene.sound.add('clickSound');
        
        // Create the menu
        this.create();
        
        // Set up ESC key handling
        this.setupKeyboardControls();
    }
    
    /**
     * Set up keyboard controls for the menu
     */
    setupKeyboardControls() {
        // Remove any existing key bindings to avoid duplicates
        if (this.escKey) {
            this.escKey.removeAllListeners();
        }
        
        // Add ESC key listener
        this.escKey = this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.ESC);
        
        // Use a simple flag-based approach instead of direct event binding
        this.scene.events.on('update', () => {
            if (Phaser.Input.Keyboard.JustDown(this.escKey)) {
                if (this.visible) {
                    this.hideMenu();
                } else {
                    this.showMenu();
                }
            }
        });
    }
    
    /**
     * Create the menu elements
     */
    create() {
        // Create a container for all menu elements
        this.container = this.scene.add.container(0, 0);
        this.container.setDepth(1000); // Ensure it's above everything else
        
        // Add a semi-transparent background
        const bg = this.scene.add.rectangle(
            this.scene.cameras.main.width / 2,
            this.scene.cameras.main.height / 2,
            this.scene.cameras.main.width,
            this.scene.cameras.main.height,
            0x000000,
            0.7
        );
        bg.setInteractive(); // Make background clickable to prevent click-through
        this.container.add(bg);
        
        // Add menu title
        const title = this.scene.add.text(
            this.scene.cameras.main.width / 2,
            100,
            'GAME MENU',
            {
                fontSize: '48px',
                fill: '#7fff8e',
                fontFamily: 'Arial',
                stroke: '#0a2712',
                strokeThickness: 6
            }
        );
        title.setOrigin(0.5);
        this.container.add(title);
        
        // Add close button (X)
        const closeButton = this.scene.add.text(
            this.scene.cameras.main.width - 50,
            50,
            'X',
            {
                fontSize: '32px',
                fill: '#7fff8e',
                fontFamily: 'Arial',
                stroke: '#0a2712',
                strokeThickness: 4
            }
        );
        closeButton.setOrigin(0.5);
        closeButton.setInteractive({ useHandCursor: true });
        
        // Add hover effects
        closeButton.on('pointerover', () => {
            closeButton.setStyle({ fill: '#2fff91' });
            this.hoverSound.play();
        });
        
        closeButton.on('pointerout', () => {
            closeButton.setStyle({ fill: '#7fff8e' });
        });
        
        // Add click handler
        closeButton.on('pointerdown', () => {
            this.clickSound.play();
            this.hideMenu();
        });
        
        this.container.add(closeButton);
        
        // Add menu options
        const buttonStyle = {
            fontSize: '32px',
            fill: '#7fff8e',
            fontFamily: 'Arial'
        };
        
        const buttonY = 200;
        const buttonSpacing = 80;
        
        // Resume Game button
        const resumeButton = this.createButton(
            this.scene.cameras.main.width / 2,
            buttonY,
            'Resume Game',
            buttonStyle,
            () => this.hideMenu()
        );
        this.container.add(resumeButton);
        
        // Save Game button
        const saveButton = this.createButton(
            this.scene.cameras.main.width / 2,
            buttonY + buttonSpacing,
            'Save Game',
            buttonStyle,
            () => this.showSaveMenu()
        );
        this.container.add(saveButton);
        
        // Load Game button
        const loadButton = this.createButton(
            this.scene.cameras.main.width / 2,
            buttonY + buttonSpacing * 2,
            'Load Game',
            buttonStyle,
            () => this.showLoadMenu()
        );
        this.container.add(loadButton);
        
        // Exit to Main Menu button
        const exitButton = this.createButton(
            this.scene.cameras.main.width / 2,
            buttonY + buttonSpacing * 3,
            'Exit to Main Menu',
            buttonStyle,
            () => {
                this.clickSound.play();
                this.scene.scene.start('MainScene');
            }
        );
        this.container.add(exitButton);
        
        // Create save/load submenus (initially hidden)
        this.createSaveMenu();
        this.createLoadMenu();
        
        // Hide the menu initially
        this.container.setVisible(false);
    }
    
    /**
     * Create a button with hover effects
     */
    createButton(x, y, text, style, callback) {
        const container = this.scene.add.container(x, y);
        
        // Button background
        const bg = this.scene.add.rectangle(0, 0, 300, 60, 0x0a2712, 0.4);
        bg.setStrokeStyle(2, 0x7fff8e);
        container.add(bg);
        
        // Button text
        const buttonText = this.scene.add.text(0, 0, text, style);
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
     * Create the save game submenu
     */
    createSaveMenu() {
        this.saveMenuContainer = this.scene.add.container(0, 0);
        this.saveMenuContainer.setDepth(1001);
        this.container.add(this.saveMenuContainer);
        
        // Add a panel background
        const panelBg = this.scene.add.rectangle(
            this.scene.cameras.main.width / 2,
            this.scene.cameras.main.height / 2,
            500,
            400,
            0x0a2712,
            0.9
        );
        panelBg.setStrokeStyle(2, 0x7fff8e);
        this.saveMenuContainer.add(panelBg);
        
        // Add title
        const title = this.scene.add.text(
            this.scene.cameras.main.width / 2,
            this.scene.cameras.main.height / 2 - 160,
            'SAVE GAME',
            {
                fontSize: '32px',
                fill: '#7fff8e',
                fontFamily: 'Arial',
                stroke: '#0a2712',
                strokeThickness: 4
            }
        );
        title.setOrigin(0.5);
        this.saveMenuContainer.add(title);
        
        // Add save slot input field background
        const inputBg = this.scene.add.rectangle(
            this.scene.cameras.main.width / 2,
            this.scene.cameras.main.height / 2 - 80,
            400,
            50,
            0x000000,
            0.6
        );
        inputBg.setStrokeStyle(1, 0x7fff8e);
        this.saveMenuContainer.add(inputBg);
        
        // Add save slot input label
        const inputLabel = this.scene.add.text(
            this.scene.cameras.main.width / 2 - 190,
            this.scene.cameras.main.height / 2 - 80,
            'Save Name:',
            {
                fontSize: '24px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            }
        );
        inputLabel.setOrigin(0, 0.5);
        this.saveMenuContainer.add(inputLabel);
        
        // Create save name text display
        this.saveNameText = this.scene.add.text(
            this.scene.cameras.main.width / 2,
            this.scene.cameras.main.height / 2 - 80,
            this.saveSlot || 'save1',
            {
                fontSize: '24px',
                fill: '#7fff8e',
                fontFamily: 'Arial',
                align: 'center'
            }
        );
        this.saveNameText.setOrigin(0.5);
        this.saveMenuContainer.add(this.saveNameText);
        
        // Add name cycling buttons
        const prevButton = this.scene.add.text(
            this.scene.cameras.main.width / 2 - 100,
            this.scene.cameras.main.height / 2 - 80,
            '◀',
            {
                fontSize: '28px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            }
        );
        prevButton.setOrigin(0.5);
        prevButton.setInteractive({ useHandCursor: true });
        this.saveMenuContainer.add(prevButton);
        
        const nextButton = this.scene.add.text(
            this.scene.cameras.main.width / 2 + 100,
            this.scene.cameras.main.height / 2 - 80,
            '▶',
            {
                fontSize: '28px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            }
        );
        nextButton.setOrigin(0.5);
        nextButton.setInteractive({ useHandCursor: true });
        this.saveMenuContainer.add(nextButton);
        
        // Add button hover effects
        prevButton.on('pointerover', () => {
            prevButton.setStyle({ fill: '#2fff91' });
            this.hoverSound.play();
        });
        prevButton.on('pointerout', () => {
            prevButton.setStyle({ fill: '#7fff8e' });
        });
        
        nextButton.on('pointerover', () => {
            nextButton.setStyle({ fill: '#2fff91' });
            this.hoverSound.play();
        });
        nextButton.on('pointerout', () => {
            nextButton.setStyle({ fill: '#7fff8e' });
        });
        
        // Add button click handlers
        let saveIndex = 1;
        
        prevButton.on('pointerdown', () => {
            this.clickSound.play();
            saveIndex = Math.max(1, saveIndex - 1);
            this.saveSlot = `save${saveIndex}`;
            this.saveNameText.setText(this.saveSlot);
        });
        
        nextButton.on('pointerdown', () => {
            this.clickSound.play();
            saveIndex += 1;
            this.saveSlot = `save${saveIndex}`;
            this.saveNameText.setText(this.saveSlot);
        });
        
        // Add save button
        const saveButton = this.createButton(
            this.scene.cameras.main.width / 2,
            this.scene.cameras.main.height / 2,
            'Save',
            {
                fontSize: '28px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            },
            () => this.saveGame()
        );
        this.saveMenuContainer.add(saveButton);
        
        // Add back button
        const backButton = this.createButton(
            this.scene.cameras.main.width / 2,
            this.scene.cameras.main.height / 2 + 80,
            'Back',
            {
                fontSize: '28px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            },
            () => {
                this.saveMenuContainer.setVisible(false);
                this.saveNameInput.style.display = 'none';
            }
        );
        this.saveMenuContainer.add(backButton);
        
        // Hide the save menu initially
        this.saveMenuContainer.setVisible(false);
    }
    
    /**
     * Create the load game submenu
     */
    createLoadMenu() {
        this.loadMenuContainer = this.scene.add.container(0, 0);
        this.loadMenuContainer.setDepth(1001);
        this.container.add(this.loadMenuContainer);
        
        // Add a panel background
        const panelBg = this.scene.add.rectangle(
            this.scene.cameras.main.width / 2,
            this.scene.cameras.main.height / 2,
            500,
            400,
            0x0a2712,
            0.9
        );
        panelBg.setStrokeStyle(2, 0x7fff8e);
        this.loadMenuContainer.add(panelBg);
        
        // Add title
        const title = this.scene.add.text(
            this.scene.cameras.main.width / 2,
            this.scene.cameras.main.height / 2 - 160,
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
        this.saveSlotContainer = this.scene.add.container(0, 0);
        this.loadMenuContainer.add(this.saveSlotContainer);
        
        // Add back button
        const backButton = this.createButton(
            this.scene.cameras.main.width / 2,
            this.scene.cameras.main.height / 2 + 160,
            'Back',
            {
                fontSize: '28px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            },
            () => {
                this.loadMenuContainer.setVisible(false);
            }
        );
        this.loadMenuContainer.add(backButton);
        
        // Add "No Save Files" text (will be hidden if saves exist)
        this.noSavesText = this.scene.add.text(
            this.scene.cameras.main.width / 2,
            this.scene.cameras.main.height / 2,
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
    }
    
    /**
     * Show the save menu
     */
    showSaveMenu() {
        // Show the save menu container
        this.saveMenuContainer.setVisible(true);
        
        // Reset save index to 1 if not set
        if (!this.saveSlot) {
            this.saveSlot = 'save1';
        }
        
        // Update the save name text
        if (this.saveNameText) {
            this.saveNameText.setText(this.saveSlot);
        }
    }
    
    /**
     * Show the load menu
     */
    showLoadMenu() {
        // Initialize save system if needed
        if (!this.saveSystem) {
            // Lazy-load the SaveSystem
            import('../systems/SaveSystem.js').then(module => {
                const SaveSystem = module.default;
                this.saveSystem = new SaveSystem(this.scene);
                this.populateLoadMenu();
            });
        } else {
            this.populateLoadMenu();
        }
        
        // Show the load menu
        this.loadMenuContainer.setVisible(true);
    }
    
    /**
     * Populate the load menu with save files
     */
    populateLoadMenu() {
        // Clear previous save slots
        this.saveSlotContainer.removeAll(true);
        
        // Check if gameAPI is available
        if (!window.gameAPI) {
            console.error('Game API not available');
            this.noSavesText.setText('Save system not available');
            this.noSavesText.setVisible(true);
            return;
        }
        
        const saveFiles = this.saveSystem.listSaveFiles();
        
        if (!saveFiles || saveFiles.length === 0) {
            this.noSavesText.setVisible(true);
            return;
        }
        
        this.noSavesText.setVisible(false);
        
        // Sort save files by date (newest first)
        saveFiles.sort((a, b) => new Date(b.date) - new Date(a.date));
        
        // Add save slots
        const slotY = this.scene.cameras.main.height / 2 - 80;
        const slotSpacing = 60;
        
        saveFiles.forEach((saveFile, index) => {
            if (index >= 5) return; // Limit to 5 save slots
            
            const date = new Date(saveFile.date);
            const formattedDate = `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
            
            // Create slot container
            const slotContainer = this.scene.add.container(
                this.scene.cameras.main.width / 2,
                slotY + index * slotSpacing
            );
            
            // Add slot background
            const slotBg = this.scene.add.rectangle(0, 0, 450, 50, 0x000000, 0.6);
            slotBg.setStrokeStyle(1, 0x7fff8e);
            slotBg.setInteractive({ useHandCursor: true });
            slotContainer.add(slotBg);
            
            // Add slot text
            const slotText = this.scene.add.text(
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
            const dateText = this.scene.add.text(
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
     * Toggle menu visibility
     * Note: We're not using this method directly anymore, but keeping it for compatibility
     */
    toggleMenu() {
        console.log('toggleMenu called');
        if (this.visible) {
            this.hideMenu();
        } else {
            this.showMenu();
        }
    }
    
    /**
     * Show the menu
     */
    showMenu() {
        // Don't show menu if dialog is visible
        if (this.scene.dialogVisible) return;
        
        console.log('Showing game menu');
        this.visible = true;
        
        if (this.container) {
            this.container.setVisible(true);
        }
        
        // Don't pause the scene as it can cause issues
        // Instead, we'll just show the menu overlay
    }
    
    /**
     * Hide the menu
     */
    hideMenu() {
        console.log('Hiding game menu');
        this.visible = false;
        
        if (this.container) {
            this.container.setVisible(false);
        }
        
        if (this.saveMenuContainer) {
            this.saveMenuContainer.setVisible(false);
        }
        
        if (this.loadMenuContainer) {
            this.loadMenuContainer.setVisible(false);
        }
    }
    
    /**
     * Save the current game
     */
    async saveGame() {
        // Get the save name from the text display
        const saveName = this.saveSlot || 'save1';
        
        // Check if gameAPI is available
        if (!window.gameAPI) {
            console.error('Game API not available');
            this.scene.showNotification('Save system not available', 0xff0000);
            return;
        }
        
        // Lazy-load the SaveSystem if not already loaded
        if (!this.saveSystem) {
            const module = await import('../systems/SaveSystem.js');
            const SaveSystem = module.default;
            this.saveSystem = new SaveSystem(this.scene);
        }
        
        // Save the game
        const result = await this.saveSystem.saveGame(saveName);
        
        // Show notification
        if (result.success) {
            this.scene.showNotification(`Game saved as "${saveName}"`, 0x00ff00);
        } else {
            this.scene.showNotification(`Failed to save game: ${result.message}`, 0xff0000);
        }
        
        // Hide the save menu
        this.saveMenuContainer.setVisible(false);
    }
    
    /**
     * Load a saved game
     */
    async loadGame(slotName) {
        // Check if gameAPI is available
        if (!window.gameAPI) {
            console.error('Game API not available');
            this.scene.showNotification('Save system not available', 0xff0000);
            return;
        }
        
        // Lazy-load the SaveSystem if not already loaded
        if (!this.saveSystem) {
            const module = await import('../systems/SaveSystem.js');
            const SaveSystem = module.default;
            this.saveSystem = new SaveSystem(this.scene);
        }
        
        // Load the game
        const result = await this.saveSystem.loadGame(slotName);
        
        // Show notification
        if (result.success) {
            this.scene.showNotification(`Game loaded from "${slotName}"`, 0x00ff00);
            // Hide the menu
            this.hideMenu();
        } else {
            this.scene.showNotification(`Failed to load game: ${result.message}`, 0xff0000);
        }
    }
    
    /**
     * Clean up resources
     */
    destroy() {
        // Remove ESC key listener
        if (this.escKey) {
            this.escKey.removeAllListeners();
        }
        
        // Destroy container and all children
        if (this.container) {
            this.container.destroy(true);
        }
    }
    
    /**
     * Update the menu (called every frame)
     */
    update() {
        // Nothing to update every frame
    }
}
