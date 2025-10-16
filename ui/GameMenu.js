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
        if (this.f5Key) {
            this.f5Key.removeAllListeners();
        }
        if (this.f9Key) {
            this.f9Key.removeAllListeners();
        }
        
        // Add ESC key listener for menu toggle
        this.escKey = this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.ESC);
        
        // Add F5 key listener for quick save
        this.f5Key = this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.F5);
        
        // Add F9 key listener for quick load
        this.f9Key = this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.F9);
        
        // Use a simple flag-based approach instead of direct event binding
        this.scene.events.on('update', () => {
            // Toggle menu with ESC
            if (Phaser.Input.Keyboard.JustDown(this.escKey)) {
                if (this.visible) {
                    this.hideMenu();
                } else {
                    this.showMenu();
                }
            }
            
            // Quick save with F5
            if (Phaser.Input.Keyboard.JustDown(this.f5Key)) {
                this.quickSave();
            }
            
            // Quick load with F9
            if (Phaser.Input.Keyboard.JustDown(this.f9Key)) {
                this.quickLoad();
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
        
        // Add keyboard shortcut help text
        const helpText = this.scene.add.text(
            this.scene.cameras.main.width / 2,
            550,
            'Keyboard Shortcuts: F5 = Quick Save | F9 = Quick Load | ESC = Menu',
            {
                fontSize: '16px',
                fill: '#5c9b6b',
                fontFamily: 'Arial',
                align: 'center'
            }
        );
        helpText.setOrigin(0.5);
        this.container.add(helpText);
        
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
     * Create the save game submenu with 6 save slots
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
            this.scene.cameras.main.height / 2 - 170,
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
        
        // Add save and back buttons at the top
        const buttonStyle = {
            fontSize: '24px',
            fill: '#7fff8e',
            fontFamily: 'Arial'
        };
        
        // Add save button (top left)
        const saveButton = this.createButton(
            this.scene.cameras.main.width / 2,
            this.scene.cameras.main.height / 2 - 120,
            'Save',
            buttonStyle,
            () => this.saveGame()
        );
        this.saveMenuContainer.add(saveButton);
        
        // Create container for save slots
        this.saveSlotContainer = this.scene.add.container(0, 0);
        this.saveMenuContainer.add(this.saveSlotContainer);
        
        // Create navigation arrows for save slots
        const prevPageButton = this.scene.add.text(
            this.scene.cameras.main.width / 2 - 200,
            this.scene.cameras.main.height / 2,
            '◀',
            {
                fontSize: '32px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            }
        );
        prevPageButton.setOrigin(0.5);
        prevPageButton.setInteractive({ useHandCursor: true });
        this.saveMenuContainer.add(prevPageButton);
        
        const nextPageButton = this.scene.add.text(
            this.scene.cameras.main.width / 2 + 200,
            this.scene.cameras.main.height / 2,
            '▶',
            {
                fontSize: '32px',
                fill: '#7fff8e',
                fontFamily: 'Arial'
            }
        );
        nextPageButton.setOrigin(0.5);
        nextPageButton.setInteractive({ useHandCursor: true });
        this.saveMenuContainer.add(nextPageButton);
        
        // Add hover effects for navigation buttons
        prevPageButton.on('pointerover', () => {
            prevPageButton.setStyle({ fill: '#2fff91' });
            this.hoverSound.play();
        });
        prevPageButton.on('pointerout', () => {
            prevPageButton.setStyle({ fill: '#7fff8e' });
        });
        
        nextPageButton.on('pointerover', () => {
            nextPageButton.setStyle({ fill: '#2fff91' });
            this.hoverSound.play();
        });
        nextPageButton.on('pointerout', () => {
            nextPageButton.setStyle({ fill: '#7fff8e' });
        });
        
        // Initialize save slot variables
        this.currentSavePage = 0;
        this.slotsPerPage = 6;
        this.saveSlots = [];
        
        // Create 6 save slots
        for (let i = 0; i < this.slotsPerPage; i++) {
            this.createSaveSlot(i);
        }
        
        // Add click handlers for navigation buttons
        prevPageButton.on('pointerdown', () => {
            this.clickSound.play();
            if (this.currentSavePage > 0) {
                this.currentSavePage--;
                this.updateSaveSlots();
            }
        });
        
        nextPageButton.on('pointerdown', () => {
            this.clickSound.play();
            this.currentSavePage++;
            this.updateSaveSlots();
        });
        
        // Hide the save menu initially
        this.saveMenuContainer.setVisible(false);
    }
    
    /**
     * Create a single save slot
     * @param {number} index - Index of the slot (0-5)
     */
    createSaveSlot(index) {
        // Calculate position (3 columns, 2 rows)
        const col = index % 3;
        const row = Math.floor(index / 3);
        
        const x = this.scene.cameras.main.width / 2 + (col - 1) * 140;
        const y = this.scene.cameras.main.height / 2 - 40 + row * 80;
        
        // Create slot container
        const slotContainer = this.scene.add.container(x, y);
        
        // Add slot background
        const slotBg = this.scene.add.rectangle(0, 0, 120, 60, 0x000000, 0.6);
        slotBg.setStrokeStyle(1, 0x7fff8e);
        slotContainer.add(slotBg);
        
        // Add slot text
        const slotText = this.scene.add.text(
            0,
            0,
            `save${index + 1}`,
            {
                fontSize: '18px',
                fill: '#7fff8e',
                fontFamily: 'Arial',
                align: 'center'
            }
        );
        slotText.setOrigin(0.5);
        slotContainer.add(slotText);
        
        // Make slot interactive
        slotBg.setInteractive({ useHandCursor: true });
        
        // Add hover effects
        slotBg.on('pointerover', () => {
            slotBg.setFillStyle(0x0a2712, 0.8);
            slotText.setStyle({ fontSize: '18px', fill: '#2fff91', fontFamily: 'Arial' });
            this.hoverSound.play();
        });
        
        slotBg.on('pointerout', () => {
            slotBg.setFillStyle(0x000000, 0.6);
            slotText.setStyle({ fontSize: '18px', fill: '#7fff8e', fontFamily: 'Arial' });
        });
        
        // Add click handler
        slotBg.on('pointerdown', () => {
            this.clickSound.play();
            
            // Select this slot
            this.selectSaveSlot(index);
        });
        
        // Store slot components
        this.saveSlots.push({
            container: slotContainer,
            background: slotBg,
            text: slotText,
            index: index,
            selected: false
        });
        
        // Add to save slot container
        this.saveSlotContainer.add(slotContainer);
    }
    
    /**
     * Select a save slot
     * @param {number} index - Index of the slot to select
     */
    selectSaveSlot(index) {
        // Deselect all slots
        this.saveSlots.forEach(slot => {
            slot.selected = false;
            slot.background.setStrokeStyle(1, 0x7fff8e);
        });
        
        // Select the clicked slot
        const slot = this.saveSlots[index];
        slot.selected = true;
        slot.background.setStrokeStyle(2, 0xffffff);
        
        // Update save slot name
        const slotNumber = this.currentSavePage * this.slotsPerPage + index + 1;
        this.saveSlot = `save${slotNumber}`;
    }
    
    /**
     * Update save slots based on current page
     */
    updateSaveSlots() {
        // Update slot texts
        this.saveSlots.forEach((slot, i) => {
            const slotNumber = this.currentSavePage * this.slotsPerPage + i + 1;
            slot.text.setText(`save${slotNumber}`);
            
            // Reset selection
            slot.selected = false;
            slot.background.setStrokeStyle(1, 0x7fff8e);
        });
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
        
        // Reset save page to 0
        this.currentSavePage = 0;
        
        // Update save slots
        this.updateSaveSlots();
        
        // Reset save slot if not set
        if (!this.saveSlot) {
            this.saveSlot = 'save1';
        }
        
        // Try to select the current save slot
        const slotNumber = parseInt(this.saveSlot.replace('save', ''), 10);
        if (!isNaN(slotNumber)) {
            const page = Math.floor((slotNumber - 1) / this.slotsPerPage);
            const index = (slotNumber - 1) % this.slotsPerPage;
            
            if (page === this.currentSavePage && index >= 0 && index < this.saveSlots.length) {
                this.selectSaveSlot(index);
            }
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
        
        // Hide the input field
        if (this.saveNameInput) {
            this.saveNameInput.style.display = 'none';
        }
    }
    
    /**
     * Quick save the current game (F5 key)
     */
    async quickSave() {
        console.log('Quick save triggered');
        
        // Don't save if dialog is visible or menu is open
        if (this.scene.dialogVisible || this.visible) {
            return;
        }
        
        // Use quicksave slot
        const saveName = 'quicksave';
        
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
        
        // Get current date/time for display
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        
        // Show saving notification
        this.scene.showNotification(`Saving game...`, 0x7fff8e);
        
        // Save the game
        const result = await this.saveSystem.saveGame(saveName);
        
        // Show notification
        if (result.success) {
            // Play a success sound
            if (this.scene.sound.get('clickSound')) {
                this.scene.sound.play('clickSound');
            }
            this.scene.showNotification(`Game saved at ${timeString}`, 0x00ff00);
        } else {
            this.scene.showNotification(`Failed to save game: ${result.message}`, 0xff0000);
        }
    }
    
    /**
     * Save the current game
     */
    async saveGame() {
        // Get the save name from the selected slot
        const saveName = this.saveSlot || 'save1';
        
        // Check if a slot is selected
        let slotSelected = false;
        for (const slot of this.saveSlots) {
            if (slot.selected) {
                slotSelected = true;
                break;
            }
        }
        
        // If no slot is selected, show a notification
        if (!slotSelected) {
            this.scene.showNotification('Please select a save slot', 0xff9900);
            return;
        }
        
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
            this.scene.showNotification(`Game saved as "${saveName}"`);
        } else {
            this.scene.showNotification(`Failed to save game: ${result.message}`, 0xff0000);
        }
        
        // Hide the save menu
        this.saveMenuContainer.setVisible(false);
    }
    
    /**
     * Quick load the most recent quicksave (F9 key)
     */
    async quickLoad() {
        console.log('Quick load triggered');
        
        // Don't load if dialog is visible
        if (this.scene.dialogVisible) {
            return;
        }
        
        // Use quicksave slot
        const saveName = 'quicksave';
        
        // Check if gameAPI is available
        if (!window.gameAPI) {
            console.error('Game API not available');
            this.scene.showNotification('Load system not available', 0xff0000);
            return;
        }
        
        // Check if quicksave exists
        const saveFiles = window.gameAPI.listSaveFiles();
        const quicksaveExists = saveFiles.success && saveFiles.files.some(file => file.name === 'quicksave');
        
        if (!quicksaveExists) {
            this.scene.showNotification('No quicksave found', 0xff9900);
            return;
        }
        
        // Lazy-load the SaveSystem if not already loaded
        if (!this.saveSystem) {
            const module = await import('../systems/SaveSystem.js');
            const SaveSystem = module.default;
            this.saveSystem = new SaveSystem(this.scene);
        }
        
        // Show loading notification
        this.scene.showNotification(`Loading quicksave...`, 0x7fff8e);
        
        // Load the game
        const result = await this.saveSystem.loadGame(saveName);
        
        // Show notification
        if (result.success) {
            // Play a success sound
            if (this.scene.sound.get('clickSound')) {
                this.scene.sound.play('clickSound');
            }
            this.scene.showNotification(`Game loaded successfully`, 0x00ff00);
            
            // Hide the menu if it's open
            if (this.visible) {
                this.hideMenu();
            }
        } else {
            this.scene.showNotification(`Failed to load game: ${result.message}`, 0xff0000);
        }
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
            this.scene.showNotification(`Game loaded from "${slotName}"`);
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
