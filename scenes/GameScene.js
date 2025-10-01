import GrowthDecaySystem from '../systems/GrowthDecaySystem.js';
import GrowthDecayIndicator from '../ui/GrowthDecayIndicator.js';
import QuestSystem from '../systems/QuestSystem.js';
import QuestLog from '../ui/QuestLog.js';
import FactionReputation from '../systems/FactionReputation.js';
import SymbiontSystem from '../systems/SymbiontSystem.js';
import SporeSystem from '../systems/SporeSystem.js';
import SporeBar from '../ui/SporeBar.js';
import PlayerMovementSystem from '../systems/player/PlayerMovementSystem.js';
import InventorySystem from '../systems/inventory/InventorySystem.js';
import MoneySystem from '../systems/inventory/MoneySystem.js';
import JournalSystem from '../systems/JournalSystem.js';
import JournalUI from '../ui/JournalUI.js';
import EffectsSystem from '../systems/EffectsSystem.js';

export default class GameScene extends Phaser.Scene {
    constructor(config = { key: 'GameScene' }) {
        super(config);
        this.dialogVisible = false;
        this.dialogState = 'main';
        this.dialogOptionsY = 0; // Track options position
        this.isTransitioning = false; // Flag to prevent multiple transitions
        this.symbiontContainer = null;
        this.symbiontSlots = [];
        this.symbiontIcons = new Map();
        
        // Systems will be initialized in init()
        this.playerMovementSystem = null;
        this.inventorySystem = null;
        this.moneySystem = null;
        this.journalSystem = null;
        this.journalUI = null;
        this.effectsSystem = null;
    }

    init() {
        // Reset transition flag when scene starts
        this.isTransitioning = false;
        
        // Initialize the player movement system
        this.playerMovementSystem = new PlayerMovementSystem(this);
        
        // Initialize the inventory system
        this.inventorySystem = new InventorySystem(this);
    }

    preload() {
        // Load the game assets
        this.load.image('cityBackground', 'assets/images/backgrounds/city.jpg');
        this.load.image('ground', 'assets/images/ui/ground.png');
        this.load.image('cursor', 'assets/images/ui/cursor.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        this.load.image('journalIcon', 'assets/images/ui/journal.png'); // Journal icon
        this.load.spritesheet('priest', 'assets/images/characters/priest.png', {
            frameWidth: 64,
            frameHeight: 64
        });
        this.load.spritesheet('stranger', 'assets/images/characters/mysterious-stranger.png', {
            frameWidth: 64,
            frameHeight: 64
        });
        this.load.image('fungalPriestAvatar', 'assets/images/characters/fungal-priest.png');

        // Load sound assets
        this.load.audio('backgroundMusic', 'assets/sounds/infinite_fold.mp3');
        this.load.audio('cathedralTheme', 'assets/sounds/cathedral-theme.wav');
        this.load.audio('marketTheme', 'assets/sounds/market-theme.wav');
        this.load.audio('clickSound', 'assets/sounds/click.mp3');
        this.load.audio('dialogMurmur', 'assets/sounds/dialog-murmur.wav');
        this.load.audio('genericMusic', 'assets/sounds/background-music.wav');


        // Load Growth/Decay indicator image
        this.load.image('growthDecay', 'assets/images/ui/growthDecay.jpg');

        // Handle load errors
        this.load.on('loaderror', (fileObj) => {
            console.log('Error loading asset:', fileObj.key);
        });
    }

    create() {
        // Create background if needed
        if (typeof this.createCityBackground === 'function') {
            this.createCityBackground();
        }
        
        // Initialize systems
        this.initSystems();
        
        // Add keyboard binding for journal (J key)
        this.input.keyboard.on('keydown-J', () => {
            if (this.journalUI) {
                this.journalUI.toggle();
            }
        });
        
        // Create symbiont UI
        this.createSymbiontUI();
        
        // Initialize scene mechanics
        this.initSceneMechanics();

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
    }

    update() {
        // Update player movement if system is initialized
        if (this.playerMovementSystem) {
            this.playerMovementSystem.update();
        }

        // Call super.update() if it exists
        if (typeof super.update === 'function') {
            super.update();
        }
    }

    initSystems() {
        // Initialize Journal System
        this.journalSystem = JournalSystem.getInstance();
        this.journalSystem.setScene(this);
        
        // Create Journal UI
        this.journalUI = new JournalUI(this);
        
        // Initialize Money System
        this.moneySystem = new MoneySystem(this, {
            initialAmount: 25, // Start with 25 gold
            currencyName: 'gold',
            position: {
                x: 700,
                y: 50
            }
        });
        
        // Initialize Growth/Decay system
        if (!this.registry.get('growthDecaySystem')) {
            const growthDecaySystem = new GrowthDecaySystem();
            this.registry.set('growthDecaySystem', growthDecaySystem);
            
            growthDecaySystem.on('growthChanged', (amount) => {
                const message = amount > 0 ? 'Growth increased!' : 'Growth decreased!';
                this.showNotification(message, amount > 0 ? 0x00ff00 : 0xff0000);
            });
            
            growthDecaySystem.on('decayChanged', (amount) => {
                const message = amount > 0 ? 'Decay increased!' : 'Decay decreased!';
                this.showNotification(message, amount > 0 ? 0x8b4513 : 0x00ff00);
            });
        }
        this.growthDecaySystem = this.registry.get('growthDecaySystem');
        this.growthDecayIndicator = new GrowthDecayIndicator(this);

        // Initialize Symbiont system
        if (!this.registry.get('symbiontSystem')) {
            this.registry.set('symbiontSystem', new SymbiontSystem(this));
        }
        this.symbiontSystem = this.registry.get('symbiontSystem');

        if (this.symbiontSystem.symbionts.size > 0) {
            const message = this.symbiontSystem.getRandomMessage('thorne-still');
            if (message) {
                this.showNotification(message, '', '', 10000);
            }
        }

        // Initialize Quest system if not already initialized
        if (!this.registry.get('questSystem')) {
            const questSystem = new QuestSystem();
            questSystem.setScene(this);
            this.registry.set('questSystem', questSystem);
            
            // Add quest system event handlers
            questSystem.on('questAdded', (questId, title) => {
                this.showNotification(`New Quest: ${title}`);
            });
            
            questSystem.on('questUpdated', (questId, title) => {
                this.showNotification(`Quest Updated: ${title}`);
            });
            
            questSystem.on('questCompleted', (questId, title) => {
                this.showNotification(`Quest Completed: ${title}`);
            });
        }
        this.questSystem = this.registry.get('questSystem');
        this.questLog = new QuestLog(this);

        // Initialize Faction system if not already initialized
        if (!this.registry.get('factionSystem')) {
            const factionSystem = new FactionReputation();
            this.registry.set('factionSystem', factionSystem);
            
            // Add faction system event handlers
            factionSystem.on('reputationChanged', (faction, oldValue, newValue) => {
                const change = newValue - oldValue;
                const sign = change > 0 ? '+' : '';
                this.showNotification(`${faction} Reputation: ${sign}${change}`, 0x7fff8e);
            });
        }
        this.factionSystem = this.registry.get('factionSystem');
        
        // Initialize Spore system
        if (!this.registry.get('sporeSystem')) {
            const sporeSystem = SporeSystem.getInstance(this);
            this.registry.set('sporeSystem', sporeSystem);
        } else {
            // Update scene reference in existing instance
            SporeSystem.getInstance(this);
        }
        this.sporeSystem = this.registry.get('sporeSystem');
        
        // Create Spore Bar UI, cleaning up any old one first
        if (this.sporeBar) {
            this.sporeBar.cleanup();
        }
        
        // Initialize Effects System for drug effects and visual effects
        this.effectsSystem = new EffectsSystem(this);
        this.effectsSystem.init();
        this.sporeBar = new SporeBar(this, 325, 10);
    }

    createSymbiontUI() {
        const startX = 60;
        const startY = 480;
        const spacing = 40;
        const slotSize = 30;

        // Create container for slots
        this.symbiontContainer = this.add.container(0, 0);
        this.symbiontContainer.setDepth(100);
        this.symbiontContainer.setScrollFactor(0); // Make it persist across scenes

        this.symbiontSlots = [];
        this.symbiontIcons = new Map();

        for (let i = 0; i < this.symbiontSystem.maxSlots; i++) {
            // Create slot background
            const slot = this.add.rectangle(startX + (i * spacing), startY, slotSize, slotSize, 0x1a3b23)
                .setStrokeStyle(1, 0x7fff8e)
                .setDepth(100)
                .setAlpha(i < this.symbiontSystem.unlockedSlots ? 1 : 0.3);

            this.symbiontSlots.push(slot);
            this.symbiontContainer.add(slot);

            if (i >= this.symbiontSystem.unlockedSlots) {
                const lockText = this.add.text(slot.x, slot.y, '', {
                    fontSize: '16px',
                    color: '#7fff8e'
                }).setOrigin(0.5).setDepth(101);
                this.symbiontContainer.add(lockText);
            }
        }

        // Restore any existing symbionts
        if (this.symbiontSystem) {
            this.symbiontSystem.symbionts.forEach((data, id) => {
                this.addSymbiontIcon(id, data);
            });
        }
    }

    addSymbiontIcon(id, data) {
        // Get symbiont system from registry
        const symbiontSystem = this.registry.get('symbiontSystem');
        if (!symbiontSystem) {
            console.error('SymbiontSystem not found in registry');
            return;
        }
        
        const slot = symbiontSystem.symbionts.size - 1;
        const x = 60 + (slot * 40);
        const y = 480;
        
        // Create glowing circle for symbiont
        const symbiontIcon = this.add.circle(x, y, 12, 0x7fff8e)
            .setDepth(102)
            .setInteractive({ useHandCursor: true });
        
        // Add pulsing animation
        this.tweens.add({
            targets: symbiontIcon,
            scale: 1.2,
            alpha: 0.8,
            duration: 1000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Add hover tooltip
        symbiontIcon.on('pointerover', () => {
            const tooltipBg = this.add.rectangle(x, y - 40, 200, 60, 0x0a2712, 0.9)
                .setStrokeStyle(1, 0x7fff8e);
            const tooltipText = this.add.text(x, y - 40, 
                `${data.name}\nPower: ${data.power}\nAbility: ${data.ability}`, {
                fontSize: '12px',
                color: '#7fff8e',
                align: 'left'
            }).setOrigin(0.5);
            
            this.activeTooltip = this.add.container(0, 0, [tooltipBg, tooltipText])
                .setDepth(103);
        });

        symbiontIcon.on('pointerout', () => {
            if (this.activeTooltip) {
                this.activeTooltip.destroy();
                this.activeTooltip = null;
            }
        });

        symbiontIcon.on('pointerdown', () => {
            // Get the symbiont-specific dialog from SymbiontSystem
            this.showSymbiontDialog(id);
        });

        this.symbiontContainer.add(symbiontIcon);
        this.symbiontIcons.set(id, symbiontIcon);
    }

    /**
     * Show dialog for a specific symbiont
     * @param {string} symbiontId - The ID of the symbiont to show dialog for
     * @param {string} dialogKey - Optional specific dialog section to show (defaults to 'main')
     */
    showSymbiontDialog(symbiontId, dialogKey = 'main') {
        // Get the symbiont system
        const symbiontSystem = this.registry.get('symbiontSystem');
        if (!symbiontSystem) {
            console.error('SymbiontSystem not found in registry');
            return;
        }
        
        // Get dialog content for this symbiont
        const dialogContent = symbiontSystem.getSymbiontDialogContent(symbiontId, dialogKey);
        if (!dialogContent) {
            console.error(`No dialog content found for symbiont ${symbiontId} and key ${dialogKey}`);
            return;
        }
        
        // Create a dynamic dialog state
        const dynamicDialogState = {
            speaker: dialogContent.speaker || symbiontSystem.getSymbiontName(symbiontId) || 'Person',
            text: dialogContent.text,
            options: dialogContent.options.map(option => {
                if (option.next === 'closeDialog') {
                    // Keep closeDialog as is
                    return option;
                } else {
                    // For other options, create a custom handler
                    return {
                        text: option.text,
                        onSelect: () => {
                            // Show the next dialog section for this symbiont
                            this.showSymbiontDialog(symbiontId, option.next);
                        }
                    };
                }
            })
        };
        
        // Show the dynamic dialog
        this.showDialog(dynamicDialogState);
    }
    
    initSceneMechanics() {
        try {
            // Keyboard shortcuts are now handled by their respective systems

            // Add ground/street platform
            const ground = this.add.tileSprite(400, 550, 800, 100, 'ground');
            ground.setDepth(1);

            // Initialize inventory system
            if (this.inventorySystem) {
                this.inventorySystem.init();
            }

            // Initialize music system
            this.initMusicSystem();

            // Add click sound
            this.clickSound = this.sound.add('clickSound');
            
            // Add dialog murmur sound
            this.dialogMurmur = this.sound.add('dialogMurmur');

            // Create the Fungal Apprentice character (using the same priest sprite)
            this.priest = this.add.sprite(100, 470, 'priest');
            this.priest.setScale(2);
            // Also create an apprentice reference for clarity
            this.apprentice = this.priest;
            
            // Enable physics for the priest
            this.physics.world.enable(this.priest);
            this.priest.body.setCollideWorldBounds(true);
            
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
                duration: 1000,
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

            // Initialize the player movement system with the priest character
            if (this.playerMovementSystem) {
                this.playerMovementSystem.init(this.priest, this.priestGlow);
                // Update dialog visibility state
                this.playerMovementSystem.setDialogVisible(this.dialogVisible);
            }
            
            // Create journal button container at top right corner (aligned with Quest button)
            const journalBtnContainer = this.add.container(690, 50);
            journalBtnContainer.setDepth(100);
            
            // Create mushroom-shaped button background for journal
            const journalBtnBg = this.add.graphics();
            journalBtnBg.fillStyle(0x2a623d); // Dark green cap
            journalBtnBg.fillCircle(0, -10, 20);
            journalBtnBg.fillStyle(0x1a3b23); // Darker green stem
            journalBtnBg.fillRect(-10, -10, 20, 25);
            
            // Add glowing spots to journal button
            const journalSpot1 = this.add.circle(-5, -15, 3, 0x7fff8e);
            const journalSpot2 = this.add.circle(5, -20, 2, 0x7fff8e);
            journalSpot1.setAlpha(0.7);
            journalSpot2.setAlpha(0.7);
            
            // Add a small book/scroll icon to the center of the mushroom
            const journalIcon = this.add.graphics();
            journalIcon.fillStyle(0x7fff8e, 0.9); // Glowing green
            journalIcon.fillRect(-8, -15, 16, 12); // Book/scroll shape
            journalIcon.lineStyle(1, 0x1a3b23); // Dark green lines
            journalIcon.lineBetween(-8, -15, 8, -15); // Top line
            journalIcon.lineBetween(-8, -11, 8, -11); // Middle line
            journalIcon.lineBetween(-8, -7, 8, -7); // Bottom line
            
            // Add all elements to container
            journalBtnContainer.add([journalBtnBg, journalSpot1, journalSpot2, journalIcon]);
            
            // Add journal label under button
            const journalLabel = this.add.text(0, 25, 'JOURNAL', {
                fontSize: '12px',
                fontFamily: 'Georgia',
                color: '#7fff8e',
                align: 'left'
            }).setOrigin(0.5);
            journalBtnContainer.add(journalLabel);
            
            // Make button interactive
            journalBtnContainer.setSize(40, 60);
            journalBtnContainer.setInteractive({ useHandCursor: true });
            
            // No pulsating effect as requested
            
            journalBtnContainer.on('pointerdown', () => {
                if (this.clickSound) this.clickSound.play();
                this.journalUI.toggle();
            });
        } catch (error) {
            console.error('Error in initSceneMechanics():', error);
        }
    }

    movePriestTo(targetX) {
        // Delegate to the player movement system
        if (this.playerMovementSystem) {
            this.playerMovementSystem.movePriestTo(targetX);
        }
    }

    initInventory() {
        // Initialize inventory data
        if (!this.registry.get('inventory')) {
            this.registry.set('inventory', {
                items: [],
                maxItems: 12 // Maximum number of items in inventory
            });
        }
        
        // Create inventory button (mushroom shape)
        this.inventoryButton = this.add.container(60, 540);
        this.inventoryButton.setDepth(100);
        
        // Mushroom cap
        const mushroomCap = this.add.graphics();
        mushroomCap.fillStyle(0x2a623d, 1); // Dark green
        mushroomCap.fillEllipse(0, -5, 20, 15);
        mushroomCap.lineStyle(2, 0x7fff8e, 0.7); // Green glow outline
        mushroomCap.strokeEllipse(0, -5, 20, 15);
        
        // Mushroom stem
        const mushroomStem = this.add.graphics();
        mushroomStem.fillStyle(0x1a3b23, 1); // Darker green
        mushroomStem.fillRect(-5, -5, 10, 15);
        
        // Mushroom spots
        const spots = this.add.graphics();
        spots.fillStyle(0x7fff8e, 0.7); // Glowing green spots
        spots.fillCircle(-8, -8, 2);
        spots.fillCircle(5, -3, 3);
        spots.fillCircle(0, -10, 2);
        
        // Text label
        const invText = this.add.text(0, 15, 'Inventory', {
            fontSize: '14px',
            fill: '#7fff8e'
        });
        invText.setOrigin(0.5);
        
        // Add all elements to the button container
        this.inventoryButton.add([mushroomCap, mushroomStem, spots, invText]);
        
        // Make button interactive
        this.inventoryButton.setInteractive(new Phaser.Geom.Rectangle(-25, -20, 50, 50), Phaser.Geom.Rectangle.Contains);
        
        // Add hover effects
        this.inventoryButton.on('pointerover', () => {
            this.inventoryButton.setScale(1.1);
        });
        
        this.inventoryButton.on('pointerout', () => {
            this.inventoryButton.setScale(1);
        });
        
        // Open inventory on click
        this.inventoryButton.on('pointerdown', () => {
            if (this.clickSound) {
                this.clickSound.play();
            }
            this.toggleInventory();
        });
        
        // Add keyboard shortcut ('I' key)
        this.input.keyboard.on('keydown-I', () => {
            this.toggleInventory();
        });
        
        // Initialize inventory panel (hidden by default)
        this.inventoryVisible = false;
        this.createInventoryPanel();
    }
    
    createInventoryPanel() {
        // Create inventory panel container
        this.inventoryPanel = this.add.container(400, 300);
        this.inventoryPanel.setDepth(1000); // Above most elements
        this.inventoryPanel.setVisible(false);
        
        // Inventory background
        const invBg = this.add.rectangle(0, 0, 500, 400, 0x0a2712, 0.9);
        invBg.setStrokeStyle(2, 0x7fff8e);
        this.inventoryPanel.add(invBg);
        
        // Inventory title
        const title = this.add.text(0, -170, 'SPORE COLLECTION', {
            fontSize: '28px',
            fill: '#7fff8e',
            fontStyle: 'bold'
        });
        title.setOrigin(0.5);
        this.inventoryPanel.add(title);
        
        // Close button
        const closeBtn = this.add.container(230, -170);
        const closeBg = this.add.rectangle(0, 0, 40, 40, 0x0a2712, 0.6);
        closeBg.setStrokeStyle(1, 0x7fff8e);
        closeBg.setInteractive({ useHandCursor: true });
        const closeText = this.add.text(0, 0, 'X', {
            fontSize: '24px',
            fill: '#7fff8e'
        });
        closeText.setOrigin(0.5);
        closeBtn.add([closeBg, closeText]);
        this.inventoryPanel.add(closeBtn);
        
        // Make close button interactive
        closeBg.on('pointerover', () => {
            closeBg.setFillStyle(0x0a2712, 0.8);
            closeText.setStyle({ fill: '#b3ffcc' });
        });
        closeBg.on('pointerout', () => {
            closeBg.setFillStyle(0x0a2712, 0.6);
            closeText.setStyle({ fill: '#7fff8e' });
        });
        closeBg.on('pointerdown', () => {
            if (this.clickSound) {
                this.clickSound.play();
            }
            this.toggleInventory(false);
        });
        
        // Create inventory slots container
        this.slotsContainer = this.add.container(0, 0);
        this.inventoryPanel.add(this.slotsContainer);
        
        // Create inventory slots (4x3 grid)
        this.inventorySlots = [];
        const slotSize = 80;
        const padding = 10;
        const startX = -180;
        const startY = -100;
        
        for (let row = 0; row < 3; row++) {
            for (let col = 0; col < 4; col++) {
                const x = startX + col * (slotSize + padding);
                const y = startY + row * (slotSize + padding);
                
                // Create slot background
                const slotBg = this.add.rectangle(x, y, slotSize, slotSize, 0x0f2315, 1);
                slotBg.setStrokeStyle(2, 0x7fff8e, 0.5);
                
                // Create slot container
                const slot = this.add.container(x, y);
                slot.add(slotBg);
                
                // Add slot index
                const slotIndex = row * 4 + col;
                slot.slotIndex = slotIndex;
                
                // Make slot interactive
                slotBg.setInteractive({ useHandCursor: true });
                slotBg.on('pointerover', () => {
                    slotBg.setStrokeStyle(2, 0x7fff8e, 1);
                    
                    // Show item description if there's an item
                    const inventory = this.registry.get('inventory');
                    if (inventory.items[slotIndex]) {
                        this.showItemDescription(inventory.items[slotIndex], x, y);
                    }
                });
                slotBg.on('pointerout', () => {
                    slotBg.setStrokeStyle(2, 0x7fff8e, 0.5);
                    
                    // Hide description
                    if (this.itemDescription) {
                        this.itemDescription.setVisible(false);
                    }
                });
                
                this.slotsContainer.add(slot);
                this.inventorySlots.push(slot);
            }
        }
        
        // Create item description container (hidden initially)
        this.itemDescription = this.add.container(0, 0);
        this.itemDescription.setVisible(false);
        this.inventoryPanel.add(this.itemDescription);
        
        // Description background
        const descBg = this.add.rectangle(0, 0, 200, 80, 0x0a2712, 0.9);
        descBg.setStrokeStyle(1, 0x7fff8e);
        this.itemDescription.add(descBg);
        
        // Description text
        this.descriptionText = this.add.text(0, 0, '', {
            fontSize: '16px',
            fill: '#7fff8e',
            align: 'left',
            wordWrap: { width: 180 }
        });
        this.descriptionText.setOrigin(0.5);
        this.itemDescription.add(this.descriptionText);
        
        // Empty inventory message
        this.emptyText = this.add.text(0, 0, 'Your spore collection is empty.\nGather spores as you explore.', {
            fontSize: '18px',
            fill: '#7fff8e',
            align: 'left'
        });
        this.emptyText.setOrigin(0.5);
        this.inventoryPanel.add(this.emptyText);
    }
    
    showItemDescription(item, slotX, slotY) {
        // Position description near the slot but not overlapping
        this.itemDescription.setPosition(slotX + 100, slotY);
        
        // Update description text
        this.descriptionText.setText(item.description || item.name);
        
        // Show description
        this.itemDescription.setVisible(true);
    }
    
    toggleInventory(forceState) {
        // If forceState is provided, set to that state, otherwise toggle
        this.inventoryVisible = forceState !== undefined ? forceState : !this.inventoryVisible;
        
        // Update inventory panel visibility, only if it exists
        if (this.inventoryPanel) {
            this.inventoryPanel.setVisible(this.inventoryVisible);
        }
        
        if (this.inventoryVisible) {
            // Update inventory display
            this.updateInventoryDisplay();
        }
    }
    
    updateInventoryDisplay() {
        // Get current inventory
        const inventory = this.registry.get('inventory');
        
        if (!this.inventorySlots || !this.emptyText) return;
        
        // Clear all slots
        this.inventorySlots.forEach(slot => {
            // Remove any item sprites but keep the background
            while (slot.list.length > 1) {
                slot.remove(slot.list[slot.list.length - 1], true);
            }
        });
        
        // Show/hide empty message
        this.emptyText.setVisible(inventory.items.length === 0);
        
        // Add items to slots
        inventory.items.forEach((item, index) => {
            if (index < this.inventorySlots.length) {
                const slot = this.inventorySlots[index];
                
                // Create item visual
                if (item.spriteKey) {
                    // If item has a sprite, use it
                    const itemSprite = this.add.image(0, 0, item.spriteKey);
                    itemSprite.setDisplaySize(40, 40); // Smaller and fits inside slot
                    itemSprite.setOrigin(0.5, 0.5);
                    itemSprite.setPosition(0, 0);
                    slot.add(itemSprite);
                } else {
                    // Otherwise create a colored circle with the first letter
                    const itemCircle = this.add.graphics();
                    itemCircle.fillStyle(item.color || 0x7fff8e, 1);
                    itemCircle.fillCircle(0, 0, 24);
                    slot.add(itemCircle);
                    
                    const itemText = this.add.text(0, 0, item.name.charAt(0).toUpperCase(), {
                        fontSize: '20px',
                        fill: '#0a2712'
                    });
                    itemText.setOrigin(0.5);
                    slot.add(itemText);
                }
                
                // Add item count if stackable
                if (item.count && item.count > 1) {
                    const countText = this.add.text(16, 16, `x${item.count}`, {
                        fontSize: '14px',
                        fill: '#7fff8e',
                        stroke: '#0a2712',
                        strokeThickness: 4
                    });
                    countText.setOrigin(0.5);
                    slot.add(countText);
                }
            }
        });
    }
    
    // Method to add an item to inventory
    addItemToInventory(item) {
        // Delegate to inventory system
        if (this.inventorySystem) {
            return this.inventorySystem.addItemToInventory(item);
        }
        return false;
    }

    removeItemFromInventory(itemId) {
        // Delegate to inventory system
        if (this.inventorySystem) {
            return this.inventorySystem.removeItemFromInventory(itemId);
        }
        return false;
    }
    
    hasItem(itemId) {
        // Delegate to inventory system
        if (this.inventorySystem) {
            return this.inventorySystem.hasItem(itemId);
        }
        return false;
    }

    showNotification(title, subtitle = '', amount = '', duration = 500) {
        // Determine notification type and settings based on content
        const notificationConfig = this.getNotificationConfig(title, subtitle);
        
        // Create notification container at the appropriate position
        const notification = this.add.container(400, notificationConfig.yPosition);
        notification.setDepth(2000);
        notification.setScrollFactor(0);

        // Format the message in a single line
        let message = title;
        if (subtitle) {
            if (typeof subtitle === 'string' && subtitle.toLowerCase().includes('quest')) {
                message = subtitle; // For quests, just show the quest name
            } else {
                message += ' ' + subtitle;
            }
        }
        if (amount !== '') {
            message += ' ' + amount;
        }
                
        // Create the text with proper wrapping for long messages
        const padding = 20;
        const maxWidth = 500; // Maximum width for the text box
        
        // Add type icon if available
        let iconText = null;
        if (notificationConfig.icon) {
            iconText = this.add.text(-maxWidth/2 + padding, -10, notificationConfig.icon, {
                fontSize: '16px',
                fill: notificationConfig.textColor
            });
            iconText.setOrigin(0, 0.5);
        }
        
        // Add type label if available
        let typeLabel = null;
        if (notificationConfig.label) {
            typeLabel = this.add.text(-maxWidth/2 + padding + 25, -10, notificationConfig.label, {
                fontSize: '12px',
                fill: notificationConfig.textColor,
                fontStyle: 'bold'
            });
            typeLabel.setOrigin(0, 0.5);
        }
        
        // Main message text
        const textConfig = {
            fontSize: '16px',
            fill: '#ffffff', // White text for better readability
            align: 'left',
            wordWrap: { width: maxWidth - (padding * 2) } // Enable word wrapping
        };
        
        const text = this.add.text(0, 10, message, textConfig);
        text.setOrigin(0.5);

        const boxWidth = Math.max(text.width + (padding * 2), 200);
        const boxHeight = Math.max(text.height + (padding * 2) + 20, 60);
        
        const box = this.add.graphics();
        // Dark background with semi-transparency
        box.fillStyle(0x0a2712, 0.9);
        box.fillRect(-boxWidth/2, -boxHeight/2, boxWidth, boxHeight);
        
        // Border with notification-specific color
        box.lineStyle(2, notificationConfig.borderColor);
        box.strokeRect(-boxWidth/2, -boxHeight/2, boxWidth, boxHeight);
        
        // Add subtle fungal pattern (dots) with notification color
        for (let i = 0; i < 5; i++) {
            const dotX = Phaser.Math.Between(-boxWidth/2 + 10, boxWidth/2 - 10);
            const dotY = Phaser.Math.Between(-boxHeight/2 + 10, boxHeight/2 - 10);
            const dotSize = Phaser.Math.Between(2, 4);
            box.fillStyle(notificationConfig.borderColor, 0.3);
            box.fillCircle(dotX, dotY, dotSize);
        }

        // Add elements to notification container
        notification.add(box);
        if (iconText) notification.add(iconText);
        if (typeLabel) notification.add(typeLabel);
        notification.add(text);
        
        // Add a subtle glow effect
        const glow = this.add.graphics();
        glow.fillStyle(notificationConfig.borderColor, 0.2);
        glow.fillCircle(0, 0, 40);
        notification.addAt(glow, 0); // Add behind other elements
        
        // Add pulsating animation to the glow
        this.tweens.add({
            targets: glow,
            alpha: { from: 0.2, to: 0.1 },
            scale: { from: 1, to: 1.2 },
            duration: 1500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Animate notification entry
        this.tweens.add({
            targets: notification,
            y: notificationConfig.yPosition - 20,
            alpha: { from: 0, to: 1 },
            duration,
            ease: 'Back.easeOut', // Bouncy effect
            onComplete: () => {
                // Hold for a longer time before fading out
                const baseDisplayTime = 4000; // Increased base display time from 2000ms to 4000ms
                const displayTime = Math.max(baseDisplayTime, message.length * 100); // Doubled the per-character time
                
                this.time.delayedCall(displayTime, () => {
                    this.tweens.add({
                        targets: notification,
                        y: notificationConfig.yPosition - 40,
                        alpha: 0,
                        duration,
                        ease: 'Power2',
                        onComplete: () => {
                            notification.destroy();
                        }
                    });
                });
            }
        });
        
        return notification;
    }
    
    /**
     * Determine notification configuration based on content
     * @private
     * @param {string} title - The notification title
     * @param {string|number} subtitle - The notification subtitle or color
     * @returns {Object} Configuration object with colors, position, etc.
     */
    getNotificationConfig(title, subtitle) {
        const lowerTitle = title.toLowerCase();
        const lowerSubtitle = typeof subtitle === 'string' ? subtitle.toLowerCase() : '';
        
        // Quest notifications
        if (lowerTitle.includes('quest') || 
            lowerSubtitle.includes('quest') ||
            lowerTitle.includes('completed')) {
            return {
                borderColor: 0xffd700, // Gold
                textColor: '#ffd700',
                yPosition: 80,
                icon: '🔍',
                label: 'QUEST'
            };
        }
        
        // Journal notifications
        if (lowerTitle.includes('journal') || 
            title === 'Journal Updated' ||
            lowerTitle.includes('added to journal')) {
            return {
                borderColor: 0x7fff8e, // Bright green
                textColor: '#7fff8e',
                yPosition: 140,
                icon: '📖',
                label: 'JOURNAL'
            };
        }
        
        // Growth/Decay notifications
        if (lowerTitle.includes('growth') || 
            lowerTitle.includes('decay') || 
            lowerTitle.includes('spore') ||
            lowerTitle.includes('experiencing effects')) {
            return {
                borderColor: 0x9370db, // Purple
                textColor: '#9370db',
                yPosition: 200,
                icon: '🍄',
            };
        }
        
        // Reputation notifications
        if (lowerTitle.includes('reputation') ||
            lowerSubtitle.includes('reputation')) {
            return {
                borderColor: 0x4169e1, // Royal blue
                textColor: '#4169e1',
                yPosition: 260,
                icon: '⭐',
                label: 'REPUTATION'
            };
        }
        
        // Error notifications
        if (subtitle === 'error' || 
            lowerTitle.includes('failed') || 
            lowerTitle.includes('not enough') ||
            lowerTitle.includes('cannot')) {
            return {
                borderColor: 0xff6347, // Tomato red
                textColor: '#ff6347',
                yPosition: 320,
                icon: '❗',
                label: 'NOTICE'
            };
        }
        
        // Default notifications
        return {
            borderColor: 0x7fff8e, // Default green
            textColor: '#ffffff',
            yPosition: 380,
            icon: '•',
            label: ''
        };
    }

    transitionToScene(newScene) {
        if (this.isTransitioning) return;
        this.isTransitioning = true;
        
        // Stop any player movement and set to idle
        if (this.priest) {
            this.priest.play('idle');
        }
        
        // Fade out
        this.cameras.main.fadeOut(800, 0, 0, 0);
        this.cameras.main.once('camerafadeoutcomplete', () => {
            // Stop ALL audio
            this.sound.stopAll();
            
            // Start new scene
            this.scene.start(newScene);
        });
    }

    initMusicSystem() {
        // Initialize background music if not already done
        if (!this.backgroundMusic) {
            this.backgroundMusic = this.sound.add('backgroundMusic', { loop: true });
        }
        
        // Initialize scene-specific music
        this.sceneMusic = null;
    }

    playSceneMusic(key) {
        // Stop ALL audio currently playing in the game
        this.sound.stopAll();
        
        // Play new scene music
        if (key) {
            this.sceneMusic = this.sound.add(key, { loop: true });
            this.sceneMusic.play();
        }
    }

    restoreBackgroundMusic() {
        // Stop ALL audio currently playing in the game
        this.sound.stopAll();
        
        // Create and play background music
        this.backgroundMusic = this.sound.add('backgroundMusic', { loop: true });
        this.backgroundMusic.play();
    }
    
    // Modify spore level by given amount
    modifySpores(amount) {
        if (!this.sporeSystem) return false;
        return this.sporeSystem.modifySpores(amount);
    }
    
    // Get current spore level
    getSporeLevel() {
        if(!this.sporeSystem) return 0;
        return this.sporeSystem.getSporeLevel();
    }
    
    // Money system helper methods
    
    /**
     * Add money to the player's wallet
     * @param {number} amount - Amount to add
     * @param {boolean} showNotification - Whether to show a notification
     * @returns {number} New total amount
     */
    addMoney(amount, showNotification = true) {
        if (!this.moneySystem) return 0;
        return this.moneySystem.add(amount, showNotification);
    }
    
    /**
     * Subtract money from the player's wallet
     * @param {number} amount - Amount to subtract
     * @param {boolean} showNotification - Whether to show a notification
     * @returns {boolean} Whether the transaction was successful
     */
    subtractMoney(amount, showNotification = true) {
        if (!this.moneySystem) return false;
        return this.moneySystem.subtract(amount, showNotification);
    }
    
    /**
     * Check if the player has enough money
     * @param {number} amount - Amount to check
     * @returns {boolean} Whether the player has enough money
     */
    hasEnoughMoney(amount) {
        if (!this.moneySystem) return false;
        return this.moneySystem.hasEnough(amount);
    }

    /**
     * Get the current money amount
     * @returns {number} Current money amount
     */
    getMoney() {
        if (!this.moneySystem) return 0;
        return this.moneySystem.get();
    }
    
    /**
     * Add a journal entry about an important event
     * @param {string} id - Unique identifier for the entry
     * @param {string} title - Title of the journal entry
     * @param {string} content - Main content of the journal entry
     * @param {string} category - Category from JournalSystem.categories
     * @param {Object} metadata - Additional metadata (optional)
     * @returns {boolean} - Whether the entry was added successfully
     */
    addJournalEntry(id, title, content, category, metadata = {}) {
        if (!this.journalSystem) return false;
        
        const result = this.journalSystem.addEntry(id, title, content, category, metadata);
        
        // Show notification if entry was added successfully
        if (result) {
            this.showNotification('Journal Updated', title);
        }
        
        return result;
    }
    
    /**
     * Check if a journal entry exists
     * @param {string} id - Entry identifier to check
     * @returns {boolean} - Whether the entry exists
     */
    hasJournalEntry(id) {
        if (!this.journalSystem) return false;
        return this.journalSystem.getEntry(id);
    }
    
    /**
     * Get a specific journal entry
     * @param {string} id - Entry identifier
     * @returns {Object|null} - The journal entry or null if not found
     */
    getJournalEntry(id) {
        if (!this.journalSystem) return null;
        return this.journalSystem.getEntry(id);
    }

    shutdown() {
        // Clean up all audio
        this.sound.stopAll();
        
        // Clean up character and effects
        if (this.priest) {
            this.priest.destroy();
            this.priest = null;
        }
        if (this.priestGlow) {
            this.priestGlow.destroy();
            this.priestGlow = null;
        }
        
        // Clean up dialog system
        if (this.dialogBox) {
            this.dialogBox.destroy();
            this.dialogBox = null;
        }
        if (this.dialogText) {
            this.dialogText.destroy();
            this.dialogText = null;
        }
        this.dialogOptions.forEach(option => option.destroy());
        this.dialogOptions = [];
        this.dialogVisible = false;
        this.dialogCallback = null;

        // Remove all event listeners
        this.input.removeAllListeners();
        
        // Clean up Growth/Decay indicator if it exists
        if (this.growthDecayIndicator) {
            // Call its cleanup method if it exists
            if (typeof this.growthDecayIndicator.cleanup === 'function') {
                this.growthDecayIndicator.cleanup();
            }
            this.growthDecayIndicator = null;
        }

        // Clean up spore system
        if (this.sporeSystem) {
            this.sporeSystem.cleanup();
        }
        
        // Clean up spore bar
        if (this.sporeBar) {
            this.sporeBar.cleanup();
            this.sporeBar = null;
        }
        
        // Clean up effects system
        if (this.effectsSystem) {
            this.effectsSystem.cleanup();
            this.effectsSystem = null;
        }

        // Call parent shutdown
        super.shutdown();

    // Defensive: also clean up spore bar on scene destroy
    this.events.on('shutdown', () => {
        if (this.sporeBar) this.sporeBar.cleanup();
    });
    this.events.on('destroy', () => {
        if (this.sporeBar) this.sporeBar.cleanup();
    });
    }

    update() {
        // Base implementation for game loop updates
        // Child scenes should override this method for scene-specific behavior
    }

    shutdown() {
        // Stop any playing scene music
        if (this.sceneMusic && this.sceneMusic.isPlaying) {
            this.sceneMusic.stop();
            this.sceneMusic.destroy();
            this.sceneMusic = null;
        }
        
        // Stop background music if playing
        if (this.backgroundMusic && this.backgroundMusic.isPlaying) {
            this.backgroundMusic.stop();
            this.backgroundMusic.destroy();
            this.backgroundMusic = null;
        }
        
        // Clean up player movement system
        if (this.playerMovementSystem) {
            this.playerMovementSystem.cleanup();
            this.playerMovementSystem = null;
        }
        
        // Clean up inventory system
        if (this.inventorySystem) {
            this.inventorySystem.cleanup();
            this.inventorySystem = null;
        }
    }

    // Helper method for other scenes to modify Growth/Decay balance
    modifyGrowthDecay(growthChange, decayChange) {
        if (this.growthDecaySystem) {
            this.growthDecaySystem.modifyBalance(growthChange, decayChange);
        }
    }

    modifyFactionReputation(faction, amount) {
        const factionSystem = this.registry.get('factionSystem');
        const result = factionSystem.modifyReputation(faction, amount);
        if (result) {
            const sign = amount > 0 ? '+' : '';
            this.showNotification(
                `${result.faction} Reputation ${sign}${amount}`,
                result.amount > 0 ? 0xb87333 : 0x8B0000
            );
        }
    }

    // Dialog option creation
    createDialogOption(text, y, callback) {
        // Create text first to calculate its height
        const optionText = this.add.text(-250, y, `• ${text}`, {
            fontSize: '20px',
            fill: '#7fff8e',
            wordWrap: { width: 540 },
            align: 'left'
        });
        optionText.setOrigin(0, 0.5); // Left align text with vertical center
        
        // Calculate dynamic height based on text content with padding
        const textHeight = optionText.height;
        // Ensure enough height for the text plus padding (10px on top and bottom)
        const optionHeight = textHeight + 10; // Just a bit of padding for Fallout style // Minimum 40px height with 20px padding
        
        // Create background with dynamic height
        const optionBg = this.add.rectangle(0, y, 560, optionHeight, 0x0a2712, 0);
        optionBg.setInteractive({ useHandCursor: true });
        
        // Return the actual height used for proper spacing in the caller
        optionBg.actualHeight = optionHeight;

        optionBg.on('pointerover', () => {
            // No background change for Fallout style
            optionText.setStyle({ fill: "#ffffff" }); // Bright white on hover
        });

        optionBg.on('pointerout', () => {
            // No background change for Fallout style
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
        }
        
        this.dialogVisible = true;
        
        // Update dialog visibility in player movement system
        if (this.playerMovementSystem) {
            this.playerMovementSystem.setDialogVisible(true);
        }
        
        // Handle both direct content objects and state keys
        let content;
        if (typeof state === 'object') {
            // Direct content object passed (from showSymbiontDialog)
            content = state;
        } else {
            // State key passed, look up in dialogContent
            this.dialogState = state;
            content = this.dialogContent[state];
            content.speaker = this.dialogContent?.speaker
            // Check if we need to inherit speaker from parent dialog group
            if (!content.speaker && state.includes('_')) {
                // Try to find a parent dialog with a speaker defined
                const dialogGroup = state.split('_')[0];
                const groupDialog = this.dialogContent[dialogGroup];
                
                if (groupDialog && groupDialog.speaker) {
                    content.speaker = groupDialog.speaker;
                } else {
                    // Try to infer speaker from dialog key
                    const speakerMap = {
                        'temple': 'Temple Guard',
                        'guard': 'Guard',
                        'merchant': 'Merchant',
                        'edgar': 'Edgar',
                        'ortholan': 'Ortholan',
                        'registrar': 'Registrar',
                        'clerk': 'Clerk',
                        'scientist': 'Scientist',
                        'stranger': 'Stranger',
                        'citizen': 'Citizen',
                        'npc': 'Citizen',
                        'bishop': 'Bishop',
                        'thaal': 'Fungal Master Thaal'
                    };
                    
                    // Check if any key in speakerMap is part of the dialog state
                    for (const [key, name] of Object.entries(speakerMap)) {
                        if (state.toLowerCase().includes(key)) {
                            content.speaker = name;
                            break;
                        }
                    }
                }
            }
        }
        
        // Check if content is valid
        if (!content) {
            console.error('Dialog content not found for state:', state);
            return;
        }
        
        // Check if this state has an onTrigger handler (runs without closing dialog)
        if (content.onTrigger) {
            content.onTrigger.call(this); // Bind the correct 'this' context
        }
        
        // Check if this state has an onShow handler (closes dialog)
        if (content.onShow) {
            content.onShow();
            return; // Don't show dialog if onShow is defined
        }
        
        // Create new dialog box
        this.dialogBox = this.add.container(400, 300);
        this.dialogBox.setDepth(1000);
        
        // We'll set the dialog background size after calculating content height
        // Initial size - increased height to fit more content
        const dialogBg = this.add.rectangle(0, 0, 600, 500, 0x0a2712, 0.9);
        dialogBg.setStrokeStyle(2, 0x7fff8e);
        this.dialogBox.add(dialogBg);

        // Add 'X' close button
        const closeBtn = this.add.container(280, -230);
        const closeBg = this.add.rectangle(0, 0, 40, 40, 0x0a2712, 0.6);
        closeBg.setStrokeStyle(1, 0x7fff8e);
        closeBg.setInteractive({ useHandCursor: true });
        const closeText = this.add.text(0, 0, 'X', {
            fontSize: '24px',
            fill: '#7fff8e'
        });
        closeText.setOrigin(0.5);
        closeBtn.add([closeBg, closeText]);
        this.dialogBox.add(closeBtn);

        // Make close button interactive
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
        const textContainer = this.add.container(0, -140);
        this.dialogBox.add(textContainer);
        
        // Store text container position for reference when positioning options
        const textContainerY = -140;
        
        // Create background for text area
        const textBgHeight = 180; // Increased height for more text
        const textBg = this.add.rectangle(0, 0, 560, textBgHeight, 0x0a2712, 0.8);
        textBg.setStrokeStyle(1, 0x7fff8e);
        textContainer.add(textBg);
        
        // Create mask for scrollable text
        this.textMaskGraphics = this.add.graphics();
        this.textMaskGraphics.fillStyle(0xffffff);
        this.textMaskGraphics.fillRect(400 - 270, 300 - 220, 540, textBgHeight - 10);
        
        // Create text with proper wrapping
        // Add speaker name if provided
        let speakerName = content.speaker;
        
        // If still no speaker name, try to infer from the current scene or context
        if (!speakerName) {
            // Try to get scene name or current NPC name
            const sceneName = this.scene.key.replace('Scene', '');
            if (sceneName.includes('Cathedral')) {
                speakerName = 'Temple Guard';
            } else if (sceneName.includes('Voxmarket')) {
                speakerName = 'Merchant';
            } else if (sceneName.includes('Scraper')) {
                speakerName = 'Resident';
            } else if (sceneName.includes('Shed')) {
                speakerName = 'Shed Staff';
            } else {
                speakerName = 'Citizen';
            }
        }
        
        const speakerText = this.add.text(-260, -(textBgHeight/2) + 10, speakerName + ':', {
            fontSize: '22px',
            fontStyle: 'bold',
            fill: '#ffff00', // Yellow color for speaker name
            align: 'left'
        });
        speakerText.setOrigin(0, 0);
        textContainer.add(speakerText);

        this.dialogText = this.add.text(-260, -(textBgHeight/2) + 40, content.text, {
            fontSize: '22px',
            fill: '#7fff8e',
            wordWrap: { width: 520 },
            lineSpacing: 6,
            align: 'left'
        });
        this.dialogText.setOrigin(0, 0); // Left align text
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
        
        // Create options container - positioned below the text area
        // Position it with appropriate spacing (reduced from previous value)
        const optionsContainer = this.add.container(0, textContainerY + textBgHeight + 20); // Text area position + height + spacing
        this.dialogBox.add(optionsContainer);
        
        // Create dialog options container
        this.dialogOptions = this.add.container(0, 0);
        optionsContainer.add(this.dialogOptions);
        
        // Create dialog options
        const visibleOptionsCount = 4; // Maximum number of visible options
        // We'll use dynamic heights for options based on content
        
        // Calculate total options including "Close"
        // Handle options that are functions
        if (typeof content.options === 'function') {
            content.options = content.options.call(this);
        }
        
        // Make sure content.options exists and is an array
        if (!content.options || !Array.isArray(content.options)) {
            content.options = [];
        }
        
        const totalOptions = content.options.length + 1; // +1 for Close button
        
        // Calculate total pages needed
        const totalPages = Math.ceil(totalOptions / visibleOptionsCount);
        
        // Determine if we need pagination - we need at least 2 pages
        const needsPagination = totalPages > 1;
        
        // Track current page
        this.currentOptionPage = 0;
        
        // Debug pagination info
        console.log(`Dialog pagination: ${totalOptions} options, ${visibleOptionsCount} visible, ${totalPages} pages, needs pagination: ${needsPagination}`);
        
        // Function to show options for current page
        const showOptionsForPage = (page) => {
            // Clear existing options
            this.dialogOptions.removeAll(true);
            
            // Calculate start and end indices for current page
            const startIdx = page * visibleOptionsCount;
            const endIdx = Math.min(startIdx + visibleOptionsCount, content.options.length);
            
            // Add options for current page with dynamic spacing
            let currentY = 0; // Track the current Y position
            
            for (let i = startIdx; i < endIdx; i++) {
                const option = content.options[i];
                
                // Create the dialog option at the current Y position
                const elements = this.createDialogOption(option.text, currentY, () => {
            // Call onSelect if it exists
            if (option.onSelect) {
                option.onSelect.call(this); // Bind the correct 'this' context
            }
            
            // Check if there's an onTrigger function that returns a dialog ID
            if (content.onTrigger) {
                const nextDialog = content.onTrigger.call(this, option); // Bind the correct 'this' context
                if (nextDialog) {
                    // If onTrigger returns a dialog ID, use that instead of option.next
                    this.showDialog(nextDialog);
                    return;
                }
            }
            
            // Otherwise use the option's next value
            if (option.next) {
                this.showDialog(option.next);
            }
        });
                this.dialogOptions.add(elements);
                
                // Increment Y position by the actual height of this option plus spacing
                const spacing = 8; // Reduced spacing for Fallout style
                currentY += elements[0].actualHeight + spacing;
            }
            
            // Add close option if it fits on this page
            if (endIdx === content.options.length && (endIdx - startIdx) < visibleOptionsCount) {
                const closeElements = this.createDialogOption('Close', currentY, () => {
                    this.hideDialog();
                });
                this.dialogOptions.add(closeElements);
                
                // Update currentY for consistent spacing after Close button
                const spacing = 15; // Same spacing as between other options
                currentY += closeElements[0].actualHeight + spacing;
            }
            
            // Add pagination controls if needed
            if (needsPagination) {
                // Create pagination container
                const paginationContainer = this.add.container(0, currentY + 20);
                this.dialogOptions.add(paginationContainer);
                
                // Add page indicator text
                const pageText = this.add.text(-15, 0, 
                    `Page ${page + 1}/${totalPages}`, {
                    fontSize: '18px',
                    fill: '#7fff8e'
                });
                pageText.setOrigin(0.5);
                paginationContainer.add(pageText);
                
                // Add navigation arrows based on current page
                if (page < totalPages - 1) {
                    // Add right arrow for next page
                    const rightArrow = this.add.text(pageText.width/2 + 15, 0, '▶', {
                        fontSize: '18px',
                        fill: '#7fff8e'
                    });
                    rightArrow.setOrigin(0.5);
                    rightArrow.setInteractive({ useHandCursor: true });
                    paginationContainer.add(rightArrow);
                    
                    // Add hover and click effects
                    rightArrow.on('pointerover', () => rightArrow.setStyle({ fill: '#b3ffcc' }));
                    rightArrow.on('pointerout', () => rightArrow.setStyle({ fill: '#7fff8e' }));
                    rightArrow.on('pointerdown', () => {
                        this.clickSound.play();
                        this.currentOptionPage++;
                        showOptionsForPage(this.currentOptionPage);
                    });
                }
                
                if (page > 0) {
                    // Add left arrow for previous page
                    const leftArrow = this.add.text(-pageText.width/2 - 30, 0, '◀', {
                        fontSize: '18px',
                        fill: '#7fff8e'
                    });
                    leftArrow.setOrigin(0.5);
                    leftArrow.setInteractive({ useHandCursor: true });
                    paginationContainer.add(leftArrow);
                    
                    // Add hover and click effects
                    leftArrow.on('pointerover', () => leftArrow.setStyle({ fill: '#b3ffcc' }));
                    leftArrow.on('pointerout', () => leftArrow.setStyle({ fill: '#7fff8e' }));
                    leftArrow.on('pointerdown', () => {
                        this.clickSound.play();
                        this.currentOptionPage--;
                        showOptionsForPage(this.currentOptionPage);
                    });
                }
                
                // Update currentY to include pagination controls
                currentY += 50;
            }
            
            // Resize dialog background based on content height
            if (this.dialogBg) {
                // Calculate total height needed: text area (120px) + spacing (20px) + options area (currentY) + bottom padding (30px)
                const totalHeight = 120 + 20 + currentY + 30;
                // Set minimum height to 500px to match initial height
                const newHeight = Math.max(500, totalHeight);
                this.dialogBg.height = newHeight;
                
                // Center the dialog box vertically based on new height
                this.dialogBox.y = 300;
                
                // No need to reposition options container as it's already positioned relative to text area
            }
        };
        
        // Show options for the first page
        showOptionsForPage(0);
        
        // Store reference to dialog background for resizing
        this.dialogBg = dialogBg;
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
        
        // Update dialog visibility in player movement system
        if (this.playerMovementSystem) {
            this.playerMovementSystem.setDialogVisible(false);
        }
        
        // Hide avatar on dialog close
        if (this.avatar) {
            this.avatar.setVisible(false);
        }
    }

    get dialogContent() {
        return {
            ...super.dialogContent,
            // Symbiont dialogs are now dynamically generated
            // See showSymbiontDialog method
            
            closeDialog: {
                text: '',
                options: [],
                onShow: () => {
                    this.hideDialog();
                }
            }
        };
    }

    makeItemCollectable(item, sprite) {
        // Make the item sprite interactive
        sprite.setInteractive({ useHandCursor: true });

        // Create item description container if it doesn't exist
        if (!this.worldItemDescription) {
            this.worldItemDescription = this.add.container(0, 0);
            this.worldItemDescription.setDepth(1000);
            this.worldItemDescription.setVisible(false);

            // Description background
            const descBg = this.add.rectangle(0, 0, 200, 80, 0x0a2712, 0.9);
            descBg.setStrokeStyle(1, 0x7fff8e);
            this.worldItemDescription.add(descBg);

            // Description text
            this.worldDescriptionText = this.add.text(0, 0, '', {
                fontSize: '16px',
                fill: '#7fff8e',
                align: 'left',
                wordWrap: { width: 180 }
            });
            this.worldDescriptionText.setOrigin(0.5);
            this.worldItemDescription.add(this.worldDescriptionText);
        }

        // Show description on hover
        sprite.on('pointerover', () => {
            this.worldDescriptionText.setText(item.description || item.name);
            
            // Position tooltip above the item
            const tooltipX = sprite.x;
            const tooltipY = sprite.y - sprite.displayHeight/2 - 50;
            this.worldItemDescription.setPosition(tooltipX, tooltipY);
            this.worldItemDescription.setVisible(true);
        });

        // Hide description when not hovering
        sprite.on('pointerout', () => {
            this.worldItemDescription.setVisible(false);
        });

        // Add item to inventory on click
        sprite.on('pointerdown', () => {
            if (this.clickSound) this.clickSound.play();
            if (this.addItemToInventory(item)) {
                // Successfully added to inventory
                this.showNotification(`Added to inventory: ${item.name}`);
                sprite.destroy(); // Remove from world
                this.worldItemDescription.setVisible(false);
            }
        });
    }


}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.GameScene = GameScene;
}