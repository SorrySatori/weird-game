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
import SaveSystem from '../systems/SaveSystem.js';
import GameMenu from '../ui/GameMenu.js';
import MapUI from '../ui/MapUI.js';
import LanguageSystem from '../systems/LanguageSystem.js';
import { renderDialogLayout } from '../utils/dialogLayouts.js';
import { runEquipmentTutorial } from '../utils/equipmentTutorial.js';

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
        
        // Track used dialog options
        this.usedDialogOptions = new Map();
        
        // Systems will be initialized in init()
        this.playerMovementSystem = null;
        this.inventorySystem = null;
        this.moneySystem = null;
        this.journalSystem = null;
        this.journalUI = null;
        this.effectsSystem = null;
        this.saveSystem = null;
        this.gameMenu = null;
        this.mapUI = null;
    }

    init(data) {
        console.log('GameScene init with data:', data);
        
        // Reset transition flag when scene starts
        this.isTransitioning = false;
        
        // Initialize the player movement system
        this.playerMovementSystem = new PlayerMovementSystem(this);
        
        // Initialize the inventory system
        this.inventorySystem = new InventorySystem(this);
        
        // Load used dialog options from registry if available
        if (this.registry.has('usedDialogOptions')) {
            this.usedDialogOptions = new Map(this.registry.get('usedDialogOptions'));
        } else {
            this.usedDialogOptions = new Map();
        }
        
        // Initialize the save system
        this.saveSystem = new SaveSystem(this);
        
        // Store loaded position if provided (from save game)
        this.loadedPosition = data?.loadedPosition || null;
        
        // Flag to track if this is a loaded save
        this.isLoadedSave = data?.loadedSave || false;
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
        this.load.audio('dr_elphi_theme', 'assets/sounds/dr_elphi.mp3');
        this.load.audio('busker_theme', 'assets/sounds/busker.wav');



        // Load Growth/Decay indicator image
        this.load.image('growthDecay', 'assets/images/ui/growthDecay.jpg');

        // Fast-travel map background
        this.load.image('mapBg', 'assets/images/ui/map.png');

        // Handle load errors
        this.load.on('loaderror', (fileObj) => {
            console.log('Error loading asset:', fileObj.key);
        });
    }

    create() {
        console.log('GameScene create');
        
        // Reset dialog state for clean scene entry
        this.dialogVisible = false;
        this.dialogBox = null;
        
        // Create background if needed
        if (typeof this.createCityBackground === 'function') {
            this.createCityBackground();
        }
        
        // Initialize systems
        this.initSystems();
        
        // NOTE: the J-key toggle lives in JournalUI (alongside ESC). Do NOT bind keydown-J here as
        // well — two handlers on a single press toggled the journal twice, so it never opened.

        
        // Create symbiont UI
        this.createSymbiontUI();
        
        // Initialize scene mechanics
        this.initSceneMechanics();
        
        // Create the fast travel map (M key)
        this.mapUI = new MapUI(this);
        this.input.keyboard.on('keydown-M', () => {
            if (this.mapUI && !this.dialogVisible) {
                this.mapUI.toggle();
            }
        });

        // Create the game menu (ESC key menu)
        this.gameMenu = new GameMenu(this);

        // Growth/Decay world ambience (colour cast + motes; balanced = nothing).
        this.applyGDAmbience();

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
        
        // If we have a loaded position from a save game, set player position
        if (this.loadedPosition && this.player) {
            console.log('Setting player position from loaded save:', this.loadedPosition);
            this.player.setPosition(this.loadedPosition.x, this.loadedPosition.y);
        }
    }

    update() {
        // Update player movement if system is initialized
        if (this.playerMovementSystem) {
            this.playerMovementSystem.update();
        }

        // Keep the player's ground shadow under its feet.
        if (this.priestShadow && this.priest) {
            this.priestShadow.x = this.priest.x;
            this.priestShadow.y = this.priest.y + 58;
            this.priestShadow.setVisible(this.priest.visible);
        }

        // Update game menu if it exists
        if (this.gameMenu) {
            this.gameMenu.update();
        }

        // Symbiont ambient messages
        if (this.symbiontSystem && this.symbiontSystem.symbionts.size > 0 && !this.dialogVisible) {
            for (const [id] of this.symbiontSystem.symbionts) {
                const message = this.symbiontSystem.getRandomMessage(id);
                if (message) {
                    this.showNotification(message, '', '', 4000);
                    break; // Only one message per frame
                }
            }
        }

        // Call super.update() if it exists
        if (typeof super.update === 'function') {
            super.update();
        }
    }

    initSystems() {
        console.log('Initializing game systems');
        
        // Initialize Journal System
        this.journalSystem = JournalSystem.getInstance();
        this.journalSystem.setScene(this);
        
        // Add journal system event handlers
        this.journalSystem.on('entryAdded', (id, title) => {
            // Show notification indicator on journal button
            this.registry.set('hasUnreadJournalEntries', true);
            if (this.journalNotificationIndicator) {
                this.journalNotificationIndicator.setVisible(true);
            }
        });
        
        this.journalSystem.on('entryUpdated', (id, title) => {
            // Show notification indicator on journal button
            this.registry.set('hasUnreadJournalEntries', true);
            if (this.journalNotificationIndicator) {
                this.journalNotificationIndicator.setVisible(true);
            }
        });
        
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
        this.symbiontSystem.scene = this; // Update scene reference for new scene

        // Initialize Quest system if not already initialized
        if (!this.registry.get('questSystem')) {
            const questSystem = new QuestSystem();
            questSystem.setScene(this);
            this.registry.set('questSystem', questSystem);
            
            // Add quest system event handlers
            questSystem.on('questAdded', (questId, title) => {
                this.showNotification('New quest');
                // Show notification indicator on quest log button
                this.registry.set('hasUnreadQuestUpdates', true);
                if (this.questLog && this.questLog.questNotificationIndicator) {
                    this.questLog.questNotificationIndicator.setVisible(true);
                }
            });
            
            questSystem.on('questUpdated', (questId, title) => {
                this.showNotification('Quest updated');
                // Show notification indicator on quest log button
                this.registry.set('hasUnreadQuestUpdates', true);
                if (this.questLog && this.questLog.questNotificationIndicator) {
                    this.questLog.questNotificationIndicator.setVisible(true);
                }
            });
            
            questSystem.on('questCompleted', (questId, title) => {
                this.showNotification('Quest completed!');
                this.modifySpores(5);
                // Show notification indicator on quest log button
                this.registry.set('hasUnreadQuestUpdates', true);
                if (this.questLog && this.questLog.questNotificationIndicator) {
                    this.questLog.questNotificationIndicator.setVisible(true);
                }
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
        
        // Load saved data if this is a loaded save
        this.loadSavedData();
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
        
        // Find the correct slot index for this symbiont
        let slot = 0;
        for (const [symId] of symbiontSystem.symbionts) {
            if (symId === id) break;
            slot++;
        }
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
            speaker: dialogContent?.speaker || symbiontSystem.getSymbiontName(symbiontId) || 'Person',
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
            this.ground = ground; // stored so scenes can remove/replace the generic floor strip

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
            this.priest.setDepth(20); // the player renders in front of the ground, NPCs, and props
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
            glowFX.setDepth(19); // just behind the player
            
            // Make the glow follow the priest
            this.priestGlow = glowFX;

            // Soft ground shadow that tracks the player (kept under its feet in update()).
            this.priestShadow = this.addGroundShadow(this.priest.x, this.priest.y + 58, 66, 16);
            
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

            // Create map button container (left of journal)
            const mapBtnContainer = this.add.container(630, 50);
            mapBtnContainer.setDepth(100);

            const mapBtnBg = this.add.graphics();
            mapBtnBg.fillStyle(0x2a623d);
            mapBtnBg.fillCircle(0, -10, 20);
            mapBtnBg.fillStyle(0x1a3b23);
            mapBtnBg.fillRect(-10, -10, 20, 25);

            const mapSpot1 = this.add.circle(-5, -15, 3, 0x7fff8e);
            const mapSpot2 = this.add.circle(5, -20, 2, 0x7fff8e);
            mapSpot1.setAlpha(0.7);
            mapSpot2.setAlpha(0.7);

            // Compass-like icon for map
            const mapIcon = this.add.graphics();
            mapIcon.lineStyle(1.5, 0x7fff8e, 0.9);
            mapIcon.strokeCircle(0, -10, 8);
            mapIcon.fillStyle(0x7fff8e, 0.9);
            mapIcon.fillTriangle(0, -18, -3, -8, 3, -8); // North arrow

            const mapLabel = this.add.text(0, 25, 'MAP', {
                fontSize: '12px',
                fontFamily: 'Georgia',
                color: '#7fff8e',
                align: 'center'
            }).setOrigin(0.5);

            mapBtnContainer.add([mapBtnBg, mapSpot1, mapSpot2, mapIcon, mapLabel]);
            mapBtnContainer.setSize(40, 60);
            mapBtnContainer.setInteractive({ useHandCursor: true });
            mapBtnContainer.on('pointerover', () => {
                mapBtnContainer.setScale(1.1);
            });
            mapBtnContainer.on('pointerout', () => {
                mapBtnContainer.setScale(1);
            });
            mapBtnContainer.on('pointerdown', () => {
                if (this.clickSound) this.clickSound.play();
                if (this.mapUI && !this.dialogVisible) {
                    this.mapUI.toggle();
                }
            });
            
            // Create notification indicator (red exclamation mark)
            this.journalNotificationIndicator = this.add.container(18, -22);
            this.journalNotificationIndicator.setDepth(101);
            
            const indicatorBg = this.add.circle(0, 0, 8, 0xff0000);
            const indicatorText = this.add.text(0, 0, '!', {
                fontSize: '14px',
                fontFamily: 'Arial',
                color: '#ffffff',
                fontStyle: 'bold'
            }).setOrigin(0.5);
            
            this.journalNotificationIndicator.add([indicatorBg, indicatorText]);
            journalBtnContainer.add(this.journalNotificationIndicator);
            
            // Hide indicator initially
            this.journalNotificationIndicator.setVisible(false);
            
            // Check if there are unread journal entries
            if (this.registry.get('hasUnreadJournalEntries')) {
                this.journalNotificationIndicator.setVisible(true);
            }
            
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
            
            journalBtnContainer.on('pointerover', () => {
                journalBtnContainer.setScale(1.1);
            });
            journalBtnContainer.on('pointerout', () => {
                journalBtnContainer.setScale(1);
            });
            
            journalBtnContainer.on('pointerdown', () => {
                if (this.clickSound) this.clickSound.play();
                this.journalUI.toggle();
                // Hide notification indicator when journal is opened
                this.journalNotificationIndicator.setVisible(false);
                this.registry.set('hasUnreadJournalEntries', false);
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

    /**
     * Show a comic-style speech bubble above a target (a sprite/container with numeric x/y,
     * or a plain {x, y}). The bubble follows the target while alive.
     * Reusable across scenes for monologues/asides over characters or objects.
     * @param {object} target - object with numeric .x/.y
     * @param {string} message - the line to speak
     * @param {object} [opts] - { duration=3200, maxWidth=220, offsetY=78, depth=900,
     *   persistent=false } — persistent bubbles skip the timed fade and stay until the player
     *   dismisses them (an ✕ button, or a click anywhere outside the bubble).
     * @returns {Phaser.GameObjects.Container|null}
     */
    showSpeechBubble(target, message, opts = {}) {
        if (!target || typeof target.x !== 'number' || !this.add || !this.cameras?.main) return null;
        const duration = opts.duration ?? 3200;
        const maxWidth = opts.maxWidth ?? 220;
        const offsetY = opts.offsetY ?? 78;
        const depth = opts.depth ?? 900;

        const container = this.add.container(target.x, target.y - offsetY).setDepth(depth);

        const text = this.add.text(0, 0, message, {
            fontSize: '13px', fontStyle: 'bold', fill: '#1b1b1b',
            align: 'center', wordWrap: { width: maxWidth }
        }).setOrigin(0.5, 1);

        const padX = 12, padY = 8, tailH = 10, radius = 8;
        const w = text.width + padX * 2;
        const h = text.height + padY * 2;
        const bx = -w / 2;

        // Bubble sits above the target by default; but if there isn't room above without hitting
        // the top HUD (the spores bar), flip it BELOW the target with the tail pointing up.
        const topSafe = 82;
        const flip = ((target.y - offsetY) - (h + tailH)) < topSafe;
        const byTop = flip ? tailH : -(h + tailH); // body top, container-local

        const bubble = this.add.graphics();
        bubble.fillStyle(0xf5f2e6, 0.96);
        bubble.fillRoundedRect(bx, byTop, w, h, radius);
        if (flip) bubble.fillTriangle(-8, tailH, 8, tailH, 0, 0);   // tail points up (bubble below)
        else bubble.fillTriangle(-8, -tailH, 8, -tailH, 0, 0);      // tail points down (bubble above)
        bubble.lineStyle(2, 0x1b1b1b, 0.9);
        bubble.strokeRoundedRect(bx, byTop, w, h, radius);
        bubble.beginPath();
        if (flip) { bubble.moveTo(-8, tailH); bubble.lineTo(0, 0); bubble.lineTo(8, tailH); }
        else { bubble.moveTo(-8, -tailH); bubble.lineTo(0, 0); bubble.lineTo(8, -tailH); }
        bubble.strokePath();

        text.setPosition(0, byTop + h - padY); // sit inside the bubble body (origin 0.5,1)
        container.add([bubble, text]);
        container.setAlpha(0);
        this.tweens.add({ targets: container, alpha: 1, duration: 150, ease: 'Sine.easeOut' });

        const minY = h + tailH + 6;          // non-flipped: keep body top on-screen
        const maxY = 600 - 6 - (h + tailH);  // flipped: keep body bottom on-screen
        const follow = () => {
            if (!container.active) return;
            container.x = target.x;
            container.y = flip ? Math.min(maxY, target.y) : Math.max(minY, target.y - offsetY);
        };
        this.events.on('update', follow);

        let overlay = null;
        const cleanup = () => {
            this.events.off('update', follow);
            this.events.off('shutdown', cleanup);
            if (overlay && overlay.active) overlay.destroy();
            if (container.active) container.destroy();
        };
        const close = () => {
            if (!container.active) return;
            if (overlay) overlay.disableInteractive();
            this.tweens.add({ targets: container, alpha: 0, duration: 200, onComplete: cleanup });
        };

        if (opts.persistent) {
            // Persistent bubble: stays until dismissed with the ✕ or a click anywhere outside it.
            const bodyZone = this.add.zone(0, byTop + h / 2, w, h).setInteractive(); // absorb clicks on the body
            const closeX = this.add.text(w / 2 - 12, byTop + 11, '✕', {
                fontSize: '13px', fontStyle: 'bold', fill: '#7a1010',
                backgroundColor: '#e7e0cc', padding: { x: 4, y: 1 }
            }).setOrigin(0.5).setInteractive({ useHandCursor: true });
            closeX.on('pointerover', () => { document.body.style.cursor = 'pointer'; });
            closeX.on('pointerout', () => { document.body.style.cursor = 'default'; });
            closeX.on('pointerdown', () => close());
            container.add([bodyZone, closeX]);
            // Full-screen catcher just below the bubble; a click outside dismisses it. This frame's
            // pointerdown has already been dispatched, so the opening click won't self-close it.
            overlay = this.add.zone(400, 300, 1600, 1200).setScrollFactor(0).setDepth(depth - 1).setInteractive();
            overlay.on('pointerdown', () => close());
        } else {
            this.time.delayedCall(duration, () => close());
        }
        this.events.once('shutdown', cleanup);
        return container;
    }

    /** Convenience: translate a key via the shared LanguageSystem (current language). */
    t(key) {
        return LanguageSystem.getInstance().t(key);
    }

    /**
     * Make a location/object examinable. Clicking the (invisible) zone makes the protagonist
     * comment in their own words via a speech bubble. `resolve` returns the line to say — the
     * scene author computes it from context (what the player knows / has seen / was told), so
     * the same object reads differently over the course of the game. Reusable across scenes.
     * @param {number} x @param {number} y @param {number} width @param {number} height
     * @param {(function():string)|string} resolve - the comment (or a fn returning it by context)
     * @param {object} [opts] - { hint, depth=2, overObject=false, bubble:{duration,maxWidth,offsetY} }
     * @returns {Phaser.GameObjects.Zone|null}
     */
    createObservable(x, y, width, height, resolve, opts = {}) {
        if (!this.add) return null;
        const zone = this.add.zone(x, y, width, height).setInteractive({ useHandCursor: true });
        zone.setDepth(opts.depth ?? 2);

        let hint = null;
        if (opts.hint) {
            hint = this.add.text(x, y - height / 2 - 14, opts.hint, {
                fontSize: '13px', fill: '#7fff8e', backgroundColor: 'rgba(0,0,0,0.5)', padding: { x: 5, y: 2 }
            }).setOrigin(0.5).setDepth(100).setAlpha(0);
        }
        zone.on('pointerover', () => { if (hint) hint.setAlpha(1); document.body.style.cursor = 'pointer'; });
        zone.on('pointerout', () => { if (hint) hint.setAlpha(0); document.body.style.cursor = 'default'; });
        zone.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            const line = (typeof resolve === 'function') ? resolve() : resolve;
            if (!line) return;
            // Bubble over the protagonist (they're the one speaking); or over the object if asked.
            const target = opts.overObject ? { x, y: y - height / 2 } : (this.priest || { x, y });
            // Examine asides are persistent + closable (read at leisure); callers may override.
            this.showSpeechBubble(target, line, { persistent: true, ...(opts.bubble || {}) });
        });
        return zone;
    }

    showNotification(title, subtitle = '', amount = '', duration = 400) {
        // Determine notification type and settings based on content
        const notificationConfig = this.getNotificationConfig(title, subtitle);

        // For symbiont messages, use dedicated bottom display
        if (notificationConfig.isSymbiont) {
            this.showSymbiontMessage(title);
            return;
        }

        // Build short message
        let message = title;
        if (amount !== '') message += ' ' + amount;

        // Guard: if this scene's camera isn't active, skip rendering
        if (!this.cameras || !this.cameras.main) return;

        // Small corner notification — top-right
        const gameWidth = this.cameras.main.width;
        const xPos = gameWidth - 20;
        const yPos = notificationConfig.yPosition;

        const notification = this.add.container(xPos, yPos);
        notification.setDepth(2000);
        notification.setScrollFactor(0);

        // Icon + short text on one line
        const displayText = notificationConfig.icon ? `${notificationConfig.icon} ${message}` : message;

        const text = this.add.text(0, 0, displayText, {
            fontSize: '13px',
            fill: notificationConfig.textColor || '#ffffff',
            fontStyle: 'bold',
        });
        text.setOrigin(1, 0.5); // Right-aligned

        const padding = 8;
        const boxWidth = text.width + padding * 2;
        const boxHeight = text.height + padding * 2;

        const box = this.add.graphics();
        box.fillStyle(0x0a2712, 0.85);
        box.fillRoundedRect(-boxWidth, -boxHeight / 2, boxWidth, boxHeight, 4);
        box.lineStyle(1, notificationConfig.borderColor, 0.7);
        box.strokeRoundedRect(-boxWidth, -boxHeight / 2, boxWidth, boxHeight, 4);

        notification.add(box);
        notification.add(text);

        // Slide in from right, hold, slide out
        notification.x = xPos + boxWidth;
        notification.alpha = 0;

        this.tweens.add({
            targets: notification,
            x: xPos,
            alpha: 1,
            duration,
            ease: 'Power2',
            onComplete: () => {
                const holdTime = Math.max(2500, message.length * 60);
                this.time.delayedCall(holdTime, () => {
                    this.tweens.add({
                        targets: notification,
                        x: xPos + boxWidth,
                        alpha: 0,
                        duration: 400,
                        ease: 'Power2',
                        onComplete: () => notification.destroy()
                    });
                });
            }
        });

        return notification;
    }

    /**
     * Display symbiont ambient message at the very bottom of the screen
     */
    showSymbiontMessage(message) {
        // Guard: if this scene's camera isn't active, skip
        if (!this.cameras || !this.cameras.main) return;

        // Destroy previous symbiont message if still visible
        if (this._symbiontMsg) {
            this._symbiontMsg.destroy();
            this._symbiontMsg = null;
        }

        const gameWidth = this.cameras.main.width;
        const gameHeight = this.cameras.main.height;
        const yPos = gameHeight - 30;

        const container = this.add.container(gameWidth / 2, yPos);
        container.setDepth(1999);
        container.setScrollFactor(0);
        this._symbiontMsg = container;

        const text = this.add.text(0, 0, `🧬 ${message}`, {
            fontSize: '13px',
            fill: '#66ccaa',
            align: 'center',
            wordWrap: { width: gameWidth - 120 }
        });
        text.setOrigin(0.5);

        const padding = 8;
        const boxWidth = Math.min(text.width + padding * 2, gameWidth - 80);
        const boxHeight = text.height + padding * 2;

        const box = this.add.graphics();
        box.fillStyle(0x0a2712, 0.8);
        box.fillRoundedRect(-boxWidth / 2, -boxHeight / 2, boxWidth, boxHeight, 4);
        box.lineStyle(1, 0x66ccaa, 0.5);
        box.strokeRoundedRect(-boxWidth / 2, -boxHeight / 2, boxWidth, boxHeight, 4);

        container.add(box);
        container.add(text);

        // Fade in, hold, fade out
        container.alpha = 0;
        this.tweens.add({
            targets: container,
            alpha: 1,
            duration: 600,
            ease: 'Power1',
            onComplete: () => {
                const holdTime = Math.max(4000, message.length * 80);
                this.time.delayedCall(holdTime, () => {
                    this.tweens.add({
                        targets: container,
                        alpha: 0,
                        duration: 800,
                        ease: 'Power1',
                        onComplete: () => {
                            container.destroy();
                            if (this._symbiontMsg === container) {
                                this._symbiontMsg = null;
                            }
                        }
                    });
                });
            }
        });
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
        
        // Symbiont ambient messages — routed to bottom display
        if (lowerTitle.includes('thorne-still:') ||
            lowerTitle.includes('ulvarex:') ||
            lowerTitle.includes('neme') ||
            lowerTitle.includes('symbiont')) {
            return { isSymbiont: true };
        }

        // Quest notifications
        if (lowerTitle.includes('quest') || lowerTitle.includes('completed')) {
            return {
                borderColor: 0xffd700,
                textColor: '#ffd700',
                yPosition: 60,
                icon: '🔍',
            };
        }
        
        // Journal notifications
        if (lowerTitle.includes('journal')) {
            return {
                borderColor: 0x7fff8e,
                textColor: '#7fff8e',
                yPosition: 90,
                icon: '📖',
            };
        }
        
        // Growth/Decay notifications
        if (lowerTitle.includes('growth') || 
            lowerTitle.includes('decay') || 
            lowerTitle.includes('spore') ||
            lowerTitle.includes('experiencing effects')) {
            return {
                borderColor: 0x9370db,
                textColor: '#9370db',
                yPosition: 120,
                icon: '🍄',
            };
        }
        
        // Reputation notifications
        if (lowerTitle.includes('reputation')) {
            return {
                borderColor: 0x4169e1,
                textColor: '#4169e1',
                yPosition: 150,
                icon: '⭐',
            };
        }
        
        // Error notifications
        if (lowerTitle.includes('failed') || 
            lowerTitle.includes('not enough') ||
            lowerTitle.includes('cannot')) {
            return {
                borderColor: 0xff6347,
                textColor: '#ff6347',
                yPosition: 180,
                icon: '❗',
            };
        }
        
        // Default
        return {
            borderColor: 0x7fff8e,
            textColor: '#ffffff',
            yPosition: 60,
            icon: '',
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
            this.showNotification('Journal updated');
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
     * Which in-game day are we on. Day 2 begins once the player has slept at the
     * end of Day 1 (persisted via the journal, so it survives save/load).
     * Scenes should gate Day-2 content behind this rather than duplicating scenes.
     * @returns {boolean}
     */
    isDay2() {
        return !!this.hasJournalEntry('day1_complete_slept');
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
        if (this.dialogOptions) {
            if (typeof this.dialogOptions.destroy === 'function') {
                this.dialogOptions.destroy();
            } else if (Array.isArray(this.dialogOptions)) {
                this.dialogOptions.forEach(option => option.destroy());
            }
        }
        this.dialogOptions = null;
        this.dialogVisible = false;
        this.dialogCallback = null;

        // Remove all event listeners
        this.input.removeAllListeners();
        
        // Clean up Growth/Decay indicator if it exists
        if (this.growthDecayIndicator) {
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

        // Call parent shutdown
        super.shutdown();
    }

    // Helper method for other scenes to modify Growth/Decay balance
    modifyGrowthDecay(growthChange, decayChange) {
        if (!this.growthDecaySystem) return;
        const beforeDecay = this.growthDecaySystem.getDecay();
        const beforeGrowth = this.growthDecaySystem.getGrowth();
        this.growthDecaySystem.modifyBalance(growthChange, decayChange);
        const afterDecay = this.growthDecaySystem.getDecay();
        const afterGrowth = this.growthDecaySystem.getGrowth();

        // Announce when the balance crosses a symbiont's silence threshold (>70), so the player
        // understands why a read ability just switched off/on. Only fires if they host it.
        const sym = this.symbiontSystem || this.registry.get('symbiontSystem');
        if (sym && sym.hasSymbiont) {
            const i18n = LanguageSystem.getInstance();
            if (sym.hasSymbiont('neme-crownmire')) {
                if (beforeDecay <= 70 && afterDecay > 70) this.showNotification?.(i18n.t('notifications.nemeSilenced'), 0x8B0000);
                else if (beforeDecay > 70 && afterDecay <= 70) this.showNotification?.(i18n.t('notifications.nemeRecovered'), 0x4caf50);
            }
            if (sym.hasSymbiont('osswine')) {
                if (beforeGrowth <= 70 && afterGrowth > 70) this.showNotification?.(i18n.t('notifications.osswineSilenced'), 0x4caf50);
                else if (beforeGrowth > 70 && afterGrowth <= 70) this.showNotification?.(i18n.t('notifications.osswineRecovered'), 0x8B0000);
            }
        }
    }

    /**
     * Apply a one-time Growth/Decay nudge tied to a narrative choice. Re-selecting the same
     * option (re-opening a dialog, walking the hub twice) will NOT stack the effect — the
     * choice is remembered by a save-persisted registry flag. Use this for every Day-2
     * stance write so the accumulated balance stays honest.
     * @param {string} key   unique id for the choice (e.g. 'elphi_blame')
     * @param {number} growthChange
     * @param {number} decayChange
     * @returns {boolean} true if it applied this call, false if already spent
     */
    gdChoiceOnce(key, growthChange = 0, decayChange = 0) {
        const flag = 'gd_choice_' + key;
        if (this.registry.get(flag)) return false;
        this.registry.set(flag, true);
        this.modifyGrowthDecay(growthChange, decayChange);
        return true;
    }

    /**
     * Current Growth/Decay tendency for NPC mood reactions.
     * Only 'pronounced' balances react — a near-even split stays quiet.
     * @returns {'growthDominant'|'decayDominant'|'balanced'}
     */
    getGDTendency() {
        const g = this.growthDecaySystem?.getGrowth() ?? 50;
        if (g >= 65) return 'growthDominant';
        if ((100 - g) >= 65) return 'decayDominant';
        return 'balanced';
    }

    /**
     * Localized reactive "mood aside" for an NPC who reacts to the player's Growth/Decay by
     * their nature. Returns '' when the balance is not pronounced, or when no line exists for
     * this npc/tendency. NPCs opt in by tagging their greeting state with `moodNpc: '<key>'`;
     * showDialog() prepends the (already-localized) result after translation.
     * @param {string} npcKey
     * @returns {string}
     */
    moodAside(npcKey) {
        const tendency = this.getGDTendency();
        if (tendency === 'balanced') return '';
        const key = `mood.${npcKey}.${tendency}`;
        const line = LanguageSystem.getInstance().t(key);
        return line === key ? '' : line; // t() returns the key path when missing
    }

    /** True once inducted into the Lumen Directorate. Save-persisted (journal-backed). */
    isLumenMember() {
        return !!this.hasJournalEntry('lumen_directorate_joined');
    }

    /** Idempotently record the Pith Reclaimers as a discovered faction — the gate for joining them. */
    learnPithReclaimers() {
        if (!this.hasJournalEntry || this.hasJournalEntry('pith_reclaimers_faction')) return;
        this.addJournalEntry(
            'pith_reclaimers_faction',
            'The Pith Reclaimers - Keepers of Balance',
            'The Pith Reclaimers appear to be a faction concerned with maintaining balance and preventing technological overreach. They stand in opposition to the Rust Choir, believing some ancient technologies should remain dormant. They run the city\'s administrative apparatus from the Townhall.',
            this.journalSystem.categories.FACTIONS,
            { faction: 'Pith Reclaimers' }
        );
    }

    /**
     * Growth/Decay ambience: washes the environment (not the characters) in a colour cast and
     * drifting motes reflecting the current balance. Renders above the background but below
     * characters (depth 0.5), so "the world changes, not the player." Balanced = untouched.
     * Applied automatically to every gameplay scene from create().
     */
    applyGDAmbience() {
        if (this._gdAmbience) { this._gdAmbience.destroy(); this._gdAmbience = null; }
        const tendency = this.getGDTendency ? this.getGDTendency() : 'balanced';
        if (tendency === 'balanced') return;

        const growth = tendency === 'growthDominant';
        const washColor = growth ? 0x7fdf5a : 0x9c5a28; // green bloom vs rust/sepia
        const washAlpha = growth ? 0.12 : 0.16;
        const moteColor = growth ? 0xcdeeb0 : 0xb08a5a;

        const layer = this.add.container(0, 0);
        layer.setDepth(0.5);
        layer.setScrollFactor(0);
        this._gdAmbience = layer;

        // Colour cast over the scenery.
        layer.add(this.add.rectangle(400, 300, 800, 600, washColor, washAlpha));

        // Drifting motes — spores rising (growth) / ash settling (decay).
        for (let i = 0; i < 16; i++) {
            const x = Math.random() * 800;
            const y = Math.random() * 600;
            const mote = this.add.circle(x, y, 1 + Math.random() * 2.5, moteColor, 0.5);
            layer.add(mote);
            const drift = growth ? -(40 + Math.random() * 60) : (30 + Math.random() * 50);
            this.tweens.add({
                targets: mote,
                y: y + drift,
                alpha: { from: 0.15, to: 0.6 },
                duration: 4000 + Math.random() * 4000,
                delay: Math.random() * 3000,
                ease: 'Sine.easeInOut',
                yoyo: true,
                repeat: -1
            });
        }
    }

    /**
     * Soft elliptical ground shadow (a drawn decal — no asset). Sits on the ground beneath
     * characters. Returns the ellipse; reposition it each frame if its owner moves.
     */
    addGroundShadow(x, y, width = 60, height = 16) {
        const shadow = this.add.ellipse(x, y, width, height, 0x000000, 0.35);
        shadow.setDepth(2);
        return shadow;
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
    
    /**
     * Load saved data from registry
     */
    loadSavedData() {
        console.log('Loading saved data from registry');
        
        // Only proceed if this is a loaded save
        if (!this.isLoadedSave) {
            console.log('Not a loaded save, skipping data loading');
            return;
        }
        
        // Load quest data
        if (this.registry.has('savedQuests') && this.questSystem) {
            console.log('Loading saved quests');
            const questData = this.registry.get('savedQuests');
            this.questSystem.loadFromData(questData);
        }
        
        // Load journal data
        if (this.registry.has('savedJournal') && this.journalSystem) {
            console.log('Loading saved journal');
            const journalData = this.registry.get('savedJournal');
            this.journalSystem.loadFromData(journalData);
        }
        
        // Load symbiont data
        if (this.registry.has('savedSymbionts') && this.symbiontSystem) {
            console.log('Loading saved symbionts');
            const symbiontData = this.registry.get('savedSymbionts');
            this.symbiontSystem.loadFromData(symbiontData);
            
            // Rebuild symbiont UI
            this.createSymbiontUI();
        }
        
        // Load faction data
        if (this.registry.has('savedFactions') && this.factionSystem) {
            console.log('Loading saved factions');
            const factionData = this.registry.get('savedFactions');
            this.factionSystem.setReputations(factionData);
        }
        
        // Load effects data
        if (this.registry.has('savedEffects') && this.effectsSystem) {
            console.log('Loading saved effects');
            const effectsData = this.registry.get('savedEffects');
            this.effectsSystem.loadEffects(effectsData);
        }
        
        // Load spore data
        if (this.registry.has('savedSpores') && this.sporeSystem) {
            console.log('Loading saved spores');
            const sporeData = this.registry.get('savedSpores');
            this.sporeSystem.setSporeLevel(sporeData.currentSpores);
            this.sporeSystem.setMaxSpores(sporeData.maxSpores);
            
            // Update spore bar
            if (this.sporeBar) {
                this.sporeBar.updateDisplay(
                    sporeData.currentSpores,
                    sporeData.maxSpores
                );
            }
        }
        
        // Load money data
        if (this.registry.has('savedMoney') && this.moneySystem) {
            console.log('Loading saved money');
            const moneyData = this.registry.get('savedMoney');
            this.moneySystem.setAmount(moneyData.amount);
        }

        // Load growth/decay balance (both load paths stash it under 'growthDecayBalance').
        // Without this the freshly-created GrowthDecaySystem stays at its default 50/50.
        if (this.registry.has('growthDecayBalance') && this.growthDecaySystem) {
            this.growthDecaySystem.loadFromData(this.registry.get('growthDecayBalance'));
        }

        // Show notification
        this.showNotification('Game data loaded successfully');
    }

    // Dialog option creation

    showDialog(state) {
        // Destroy previous dialog if it exists
        if (this.dialogBox) {
            this.dialogBox.destroy();
            this.dialogBox = null;
        }
        if (this.textMaskGraphics) {
            this.textMaskGraphics.destroy();
            this.textMaskGraphics = null;
        }
        this.clearDialogLayoutArtifacts();
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
            // The scene's top-level `speaker` is a DEFAULT, not an override: only apply it
            // when the state doesn't declare its own speaker (otherwise a scene with a
            // primary NPC would mislabel every other NPC's dialog, e.g. a lamp shown as "Busker").
            if (content && !content.speaker && this.dialogContent?.speaker) {
                content.speaker = this.dialogContent.speaker;
            }
            // Check if we need to inherit speaker from parent dialog group
            if (!content?.speaker && state.includes('_')) {
                // Try to find a parent dialog with a speaker defined
                const dialogGroup = state.split('_')[0];
                const groupDialog = this.dialogContent[dialogGroup];
                
                if (groupDialog && groupDialog?.speaker) {
                    content.speaker = groupDialog.speaker;
                } else {
                    // Try to infer speaker from dialog key
                    const speakerMap = {
                        'temple': 'Temple Guard',
                        'guard': 'Guard',
                        'merchant': 'Merchant',
                        'edgar': 'Edgar',
                        'ortolan': 'Ortolan',
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
            this.hideDialog();
            return;
        }

        // Apply i18n translation if not English
        if (typeof state === 'string') {
            const langSys = LanguageSystem.getInstance();
            content = langSys.translateDialog(this.scene.key, state, content);
        }

        // Growth/Decay mood aside — a state tagged with `moodNpc` gets a reactive line prepended
        // when the player's balance is pronounced. Applied AFTER translation (so the localized line
        // survives Czech text replacement); clone content first so we never mutate the cached tree.
        if (content && content.moodNpc && typeof content.text === 'string') {
            const aside = this.moodAside(content.moodNpc);
            if (aside) content = { ...content, text: `${aside}\n\n${content.text}` };
        }

        // Check if this state has an onTrigger handler (runs without closing dialog)
        if (content.onTrigger) {
            content.onTrigger.call(this); // Bind the correct 'this' context
        }
        
        // If onTrigger called hideDialog(), don't continue rendering
        if (!this.dialogVisible) {
            return;
        }
        
        // Check if this state has an onShow handler (closes dialog)
        if (content.onShow) {
            content.onShow();
            return; // Don't show dialog if onShow is defined
        }

        // Present the dialog via the finalized layout (utils/dialogLayouts.js).
        renderDialogLayout(this, this._buildDialogModel(state, content));
    }

    /** Clean up scroll masks + wheel handlers created by non-classic dialog layouts. */
    clearDialogLayoutArtifacts() {
        if (this._dialogMasks) { this._dialogMasks.forEach(m => m.destroy()); this._dialogMasks = null; }
        if (this._dialogWheel) { this._dialogWheel.forEach(h => this.input.off('wheel', h)); this._dialogWheel = null; }
    }

    /**
     * Normalize the current dialog state into a layout-agnostic model for the presenter layer.
     * The option `activate()` carries the EXACT same navigation logic as the classic renderer
     * (mark used → onSelect → onTrigger-return → next), so only presentation differs.
     */
    _buildDialogModel(state, content) {
        const stateKey = typeof state === 'string' ? state : (this.dialogState || 'dialog');
        let opts = content.options;
        if (typeof opts === 'function') opts = opts.call(this);
        if (!Array.isArray(opts)) opts = [];

        const options = opts.map(option => ({
            label: option.text,
            used: this.usedDialogOptions.has(this.createDialogOptionKey(stateKey, option.text)),
            isClose: false,
            activate: () => {
                this.markDialogOptionAsUsed(this.createDialogOptionKey(stateKey, option.text));
                if (option.onSelect) option.onSelect.call(this);
                if (content.onTrigger) {
                    const nextDialog = content.onTrigger.call(this, option);
                    if (nextDialog) { this.showDialog(nextDialog); return; }
                }
                if (option.next) this.showDialog(option.next);
            },
        }));

        if (!content.hideCloseOption) {
            options.push({
                label: LanguageSystem.getInstance().t('ui.dialog.close'),
                used: false, isClose: true,
                activate: () => this.hideDialog(),
            });
        }

        return { speaker: content.speaker || null, text: content.text || '', options };
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
        this.clearDialogLayoutArtifacts();
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

    /**
     * Optional, meta-narrative tutorial offered by Master Thaal in the intro.
     * Implementation lives in utils/equipmentTutorial.js — this just runs it against this scene.
     */
    startEquipmentTutorial() {
        runEquipmentTutorial(this);
    }

    get dialogContent() {
        return {
            ...super.dialogContent,
            
            closeDialog: {
                text: '',
                options: [],
                onShow: () => {
                    this.hideDialog();
                }
            }
        };
    }
    
    // Create a unique key for dialog options to track usage
    createDialogOptionKey(dialogState, optionText) {
        return `${dialogState}:${optionText}`;
    }
    
    // Mark a dialog option as used
    markDialogOptionAsUsed(optionKey) {
        this.usedDialogOptions.set(optionKey, true);
        
        // Save to registry for persistence between scenes
        this.registry.set('usedDialogOptions', Array.from(this.usedDialogOptions.entries()));
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