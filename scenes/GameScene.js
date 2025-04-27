import GrowthDecaySystem from '../systems/GrowthDecaySystem.js';
import GrowthDecayIndicator from '../ui/GrowthDecayIndicator.js';
import QuestSystem from '../systems/QuestSystem.js';
import QuestLog from '../ui/QuestLog.js';

export default class GameScene extends Phaser.Scene {
    constructor(config = { key: 'GameScene' }) {
        super(config);
        this.dialogVisible = false;
        this.dialogState = 'main';
        this.dialogOptionsY = 0; // Track options position
        this.isTransitioning = false; // Flag to prevent multiple transitions
        this.cursors = null; // Initialize cursors reference
    }

    init() {
        // Reset transition flag when scene starts
        this.isTransitioning = false;
    }

    preload() {
        // Load the game assets
        this.load.image('cityBackground', 'assets/images/city.jpg');
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
        this.load.audio('cathedralTheme', 'assets/sounds/cathedral-theme.wav');
        this.load.audio('marketTheme', 'assets/sounds/market-theme.wav');
        this.load.audio('clickSound', 'assets/sounds/click.mp3');
        this.load.audio('dialogMurmur', 'assets/sounds/dialog-murmur.wav');

        // Load Growth/Decay indicator image
        this.load.image('growthDecay', 'assets/images/growthDecay.jpg');

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
        
        // Initialize scene mechanics
        this.initSceneMechanics();

        // Initialize movement state
        this.movementState = {
            left: false,
            right: false
        };

        // Set up keyboard listeners
        this.input.keyboard.on('keydown-LEFT', () => {
            console.log('Left key down');
            this.movementState.left = true;
        });

        this.input.keyboard.on('keyup-LEFT', () => {
            console.log('Left key up');
            this.movementState.left = false;
        });

        this.input.keyboard.on('keydown-RIGHT', () => {
            console.log('Right key down');
            this.movementState.right = true;
        });

        this.input.keyboard.on('keyup-RIGHT', () => {
            console.log('Right key up');
            this.movementState.right = false;
        });

        this.input.keyboard.on('keydown-A', () => {
            console.log('A key down');
            this.movementState.left = true;
        });

        this.input.keyboard.on('keyup-A', () => {
            console.log('A key up');
            this.movementState.left = false;
        });

        this.input.keyboard.on('keydown-D', () => {
            console.log('D key down');
            this.movementState.right = true;
        });

        this.input.keyboard.on('keyup-D', () => {
            console.log('D key up');
            this.movementState.right = false;
        });

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
    }

    update() {
        // Handle keyboard movement
        if (this.priest && !this.dialogVisible) {
            const speed = 4;
            let moved = false;

            if (this.movementState.left) {
                this.priest.x -= speed;
                this.priest.setScale(-2, 2);
                this.priestGlow.setScale(-2.1, 2.1);
                this.updateStaffPosition(-1);
                moved = true;
            } 
            else if (this.movementState.right) {
                this.priest.x += speed;
                this.priest.setScale(2, 2);
                this.priestGlow.setScale(2.1, 2.1);
                this.updateStaffPosition(1);
                moved = true;
            }

            // Update animations
            if (moved) {
                if (!this.priest.anims.isPlaying || this.priest.anims.currentAnim.key !== 'walk') {
                    this.priest.play('walk');
                }
            } else if (this.priest.anims.currentAnim && this.priest.anims.currentAnim.key === 'walk') {
                this.priest.play('idle');
            }

            // Update visual effects
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // Call super.update() if it exists
        if (typeof super.update === 'function') {
            super.update();
        }
    }

    initSystems() {
        // Initialize Growth/Decay system
        this.growthDecaySystem = GrowthDecaySystem.getInstance();
        this.growthDecayIndicator = new GrowthDecayIndicator(this, 20, 20);

        // Initialize Quest system
        this.questSystem = QuestSystem.getInstance();
        this.questSystem.setScene(this);
        // Position quest log button at the same Y level as inventory (550)
        this.questLog = new QuestLog(this, 700, 550);
    }

    initSceneMechanics() {
        try {
            // Add ground/street platform
            const ground = this.add.tileSprite(400, 550, 800, 100, 'ground');
            ground.setDepth(1);

            // Initialize inventory system
            this.initInventory();

            // Initialize music system
            this.initMusicSystem();

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
            
            // Enable physics for the priest
            this.physics.world.enable(this.priest);
            this.priest.body.setCollideWorldBounds(true);
            
            // Create a simpler staff for the priest
            this.staff = this.add.graphics();
            this.staff.lineStyle(3, 0x8B4513, 1); // Thinner brown staff stick
            this.staff.lineBetween(0, 0, 0, -50); // Slightly shorter staff
            
            // Add a glowing orb at the top of the staff
            this.staffOrb = this.add.circle(0, -55, 6, 0x00FF00, 0.8);
            this.staffOrb.setBlendMode(Phaser.BlendModes.ADD);
            
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

            // Add click/tap handler for movement
            this.input.on('pointerdown', (pointer) => {
                if (!this.dialogVisible && pointer.y < 500) {
                    const targetX = pointer.x;
                    this.movePriestTo(targetX);
                }
            });

            // Add keyboard controls
        } catch (error) {
            console.error('Error in initSceneMechanics():', error);
        }
    }

    movePriestTo(targetX) {
        if (!this.priest || this.dialogVisible) return;
        
        const direction = targetX < this.priest.x ? -1 : 1;
        this.clickSound.play();
        this.priest.setScale(2 * direction, 2);
        this.priestGlow.setScale(2.1 * direction, 2.1);
        this.priestGlow.x = this.priest.x;
        this.updateStaffPosition(direction);
        this.priest.play('walk');
        
        this.tweens.add({
            targets: [this.priest, this.priestGlow],
            x: targetX,
            duration: Math.abs(targetX - this.priest.x) * 5,
            ease: 'Linear',
            onUpdate: () => {
                const direction = targetX < this.priest.x ? -1 : 1;
                this.updateStaffPosition(direction);
            },
            onComplete: () => {
                this.priest.play('idle');
            }
        });
    }

    isEggCatedral() {
        return this.scene && this.scene.key === 'EggCatedralScene';
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
            document.body.style.cursor = 'pointer';
            this.cursor.setAlpha(0); // Hide custom cursor on button
        });
        
        this.inventoryButton.on('pointerout', () => {
            this.inventoryButton.setScale(1);
            document.body.style.cursor = 'default';
            this.cursor.setAlpha(0.8); // Show custom cursor again
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
        const closeText = this.add.text(0, 0, 'X', {
            fontSize: '24px',
            fill: '#7fff8e'
        });
        closeText.setOrigin(0.5);
        closeBtn.add([closeBg, closeText]);
        this.inventoryPanel.add(closeBtn);
        
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
                    this.cursor.setAlpha(0); // Hide custom cursor on slot
                    
                    // Show item description if there's an item
                    const inventory = this.registry.get('inventory');
                    if (inventory.items[slotIndex]) {
                        this.showItemDescription(inventory.items[slotIndex], x, y);
                    }
                });
                slotBg.on('pointerout', () => {
                    slotBg.setStrokeStyle(2, 0x7fff8e, 0.5);
                    this.cursor.setAlpha(0.8); // Show custom cursor again
                    
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
            align: 'center',
            wordWrap: { width: 180 }
        });
        this.descriptionText.setOrigin(0.5);
        this.itemDescription.add(this.descriptionText);
        
        // Empty inventory message
        this.emptyText = this.add.text(0, 0, 'Your spore collection is empty.\nGather spores as you explore.', {
            fontSize: '18px',
            fill: '#7fff8e',
            align: 'center'
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
        const inventory = this.registry.get('inventory');
        
        // Check if item already exists (for stackable items)
        if (item.stackable) {
            const existingItem = inventory.items.find(i => i.id === item.id);
            if (existingItem) {
                existingItem.count = (existingItem.count || 1) + 1;
                this.registry.set('inventory', inventory);
                return true;
            }
        }
        
        // Check if inventory is full
        if (inventory.items.length >= inventory.maxItems) {
            console.log('Inventory is full!');
            return false;
        }
        
        // Add new item
        inventory.items.push(item);
        this.registry.set('inventory', inventory);
        
        // Show notification
        this.showItemNotification(item);
        
        return true;
    }
    
    showItemNotification(item) {
        // Create notification container
        const notification = this.add.container(400, 100);
        notification.setDepth(2000);
        
        // Notification background
        const notifBg = this.add.rectangle(0, 0, 300, 60, 0x0a2712, 0.9);
        notifBg.setStrokeStyle(2, 0x7fff8e);
        notification.add(notifBg);
        
        // Notification text
        const text = this.add.text(0, 0, `Collected: ${item.name}`, {
            fontSize: '18px',
            fill: '#7fff8e'
        });
        text.setOrigin(0.5);
        notification.add(text);
        
        // Animate notification
        this.tweens.add({
            targets: notification,
            y: 80,
            alpha: { from: 0, to: 1 },
            duration: 500,
            ease: 'Power2',
            onComplete: () => {
                // Hold for a moment then fade out
                this.time.delayedCall(2000, () => {
                    this.tweens.add({
                        targets: notification,
                        y: 60,
                        alpha: 0,
                        duration: 500,
                        ease: 'Power2',
                        onComplete: () => {
                            notification.destroy();
                        }
                    });
                });
            }
        });
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
                align: 'center',
                wordWrap: { width: 180 }
            });
            this.worldDescriptionText.setOrigin(0.5);
            this.worldItemDescription.add(this.worldDescriptionText);
        }

        // Show description on hover
        sprite.on('pointerover', () => {
            this.cursor.setAlpha(0); // Hide custom cursor
            this.worldDescriptionText.setText(item.description || item.name);
            
            // Position tooltip above the item
            const tooltipX = sprite.x;
            const tooltipY = sprite.y - sprite.displayHeight/2 - 50;
            this.worldItemDescription.setPosition(tooltipX, tooltipY);
            this.worldItemDescription.setVisible(true);
        });

        // Hide description when not hovering
        sprite.on('pointerout', () => {
            this.cursor.setAlpha(0.8); // Show custom cursor
            this.worldItemDescription.setVisible(false);
        });

        // Add item to inventory on click
        sprite.on('pointerdown', () => {
            if (this.clickSound) this.clickSound.play();
            if (this.addItemToInventory(item)) {
                // Successfully added to inventory
                this.showItemNotification(item);
                sprite.destroy(); // Remove from world
                this.worldItemDescription.setVisible(false);
            }
        });
    }

    // Dialog option creation
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
                pageText.setOrigin(0.5);
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
        // This is now a base implementation that child scenes should override
        return {};
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
            document.body.style.cursor = 'pointer';
            this.cursor.setAlpha(0); // Hide custom cursor on button
        });
        
        this.inventoryButton.on('pointerout', () => {
            this.inventoryButton.setScale(1);
            document.body.style.cursor = 'default';
            this.cursor.setAlpha(0.8); // Show custom cursor again
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
        const closeText = this.add.text(0, 0, 'X', {
            fontSize: '24px',
            fill: '#7fff8e'
        });
        closeText.setOrigin(0.5);
        closeBtn.add([closeBg, closeText]);
        this.inventoryPanel.add(closeBtn);
        
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
                    this.cursor.setAlpha(0); // Hide custom cursor on slot
                    
                    // Show item description if there's an item
                    const inventory = this.registry.get('inventory');
                    if (inventory.items[slotIndex]) {
                        this.showItemDescription(inventory.items[slotIndex], x, y);
                    }
                });
                slotBg.on('pointerout', () => {
                    slotBg.setStrokeStyle(2, 0x7fff8e, 0.5);
                    this.cursor.setAlpha(0.8); // Show custom cursor again
                    
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
            align: 'center',
            wordWrap: { width: 180 }
        });
        this.descriptionText.setOrigin(0.5);
        this.itemDescription.add(this.descriptionText);
        
        // Empty inventory message
        this.emptyText = this.add.text(0, 0, 'Your spore collection is empty.\nGather spores as you explore.', {
            fontSize: '18px',
            fill: '#7fff8e',
            align: 'center'
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
        const inventory = this.registry.get('inventory');
        
        // Check if item already exists (for stackable items)
        if (item.stackable) {
            const existingItem = inventory.items.find(i => i.id === item.id);
            if (existingItem) {
                existingItem.count = (existingItem.count || 1) + 1;
                this.registry.set('inventory', inventory);
                return true;
            }
        }
        
        // Check if inventory is full
        if (inventory.items.length >= inventory.maxItems) {
            console.log('Inventory is full!');
            return false;
        }
        
        // Add new item
        inventory.items.push(item);
        this.registry.set('inventory', inventory);
        
        // Show notification
        this.showItemNotification(item);
        
        return true;
    }
    
    showItemNotification(item) {
        // Create notification container
        const notification = this.add.container(400, 100);
        notification.setDepth(2000);
        
        // Notification background
        const notifBg = this.add.rectangle(0, 0, 300, 60, 0x0a2712, 0.9);
        notifBg.setStrokeStyle(2, 0x7fff8e);
        notification.add(notifBg);
        
        // Notification text
        const text = this.add.text(0, 0, `Collected: ${item.name}`, {
            fontSize: '18px',
            fill: '#7fff8e'
        });
        text.setOrigin(0.5);
        notification.add(text);
        
        // Animate notification
        this.tweens.add({
            targets: notification,
            y: 80,
            alpha: { from: 0, to: 1 },
            duration: 500,
            ease: 'Power2',
            onComplete: () => {
                // Hold for a moment then fade out
                this.time.delayedCall(2000, () => {
                    this.tweens.add({
                        targets: notification,
                        y: 60,
                        alpha: 0,
                        duration: 500,
                        ease: 'Power2',
                        onComplete: () => {
                            notification.destroy();
                        }
                    });
                });
            }
        });
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
        if (this.staff) {
            this.staff.destroy();
            this.staff = null;
        }
        if (this.staffOrb) {
            this.staffOrb.destroy();
            this.staffOrb = null;
        }
        if (this.cursor) {
            this.cursor.destroy();
            this.cursor = null;
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

        // Call parent shutdown
        super.shutdown();
    }

    // Update the staff position relative to the priest
    updateStaffPosition(direction) {
        if (!this.staff || !this.staffOrb) return;
        
        // Position staff and orb relative to priest
        const offsetX = direction > 0 ? 15 : -15; // Staff on right or left side based on direction
        const offsetY = -20; // Staff slightly above priest's center
        
        this.staff.x = this.priest.x + offsetX;
        this.staff.y = this.priest.y + offsetY;
        
        this.staffOrb.x = this.staff.x;
        this.staffOrb.y = this.staff.y - 55; // Orb at top of staff
        
        // Clear and redraw staff with correct direction
        this.staff.clear();
        this.staff.lineStyle(3, 0x8B4513, 1);
        this.staff.lineBetween(0, 0, 0, -50);
    }

    // Check if the current scene is EggCatedralScene
    isEggCatedral() {
        return this.constructor.name === 'EggCatedralScene';
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
    }

    // Helper method for other scenes to modify Growth/Decay balance
    modifyGrowthDecay(growthChange) {
        this.growthDecaySystem.updateBalance(growthChange);
    }

    showNotification(text, color = 0x00ff00) {
        // Create notification container
        const notification = this.add.container(400, 550);
        notification.setDepth(1000);

        // Create background
        const bg = this.add.graphics();
        bg.fillStyle(0x000000, 0.8);
        bg.fillRoundedRect(-100, -15, 200, 30, 5);
        
        // Create text
        const message = this.add.text(0, 0, text, {
            font: '14px Arial',
            fill: '#' + color.toString(16).padStart(6, '0'),
            align: 'center'
        });
        message.setOrigin(0.5);
        
        // Add to container
        notification.add([bg, message]);
        
        // Animate in
        notification.setAlpha(0);
        notification.y = 570;
        
        this.tweens.add({
            targets: notification,
            y: 550,
            alpha: 1,
            duration: 200,
            ease: 'Power1',
            onComplete: () => {
                // Hold for 2 seconds then fade out
                this.time.delayedCall(2000, () => {
                    this.tweens.add({
                        targets: notification,
                        y: 530,
                        alpha: 0,
                        duration: 200,
                        ease: 'Power1',
                        onComplete: () => {
                            notification.destroy();
                        }
                    });
                });
            }
        });
    }

    modifyGrowthDecay(growthChange, decayChange) {
        const system = this.growthDecaySystem;
        if (system) {
            if (growthChange) {
                system.updateBalance(growthChange);
                const message = growthChange > 0 ? 'Growth increased!' : 'Growth decreased!';
                const color = growthChange > 0 ? 0x00ff00 : 0xff0000;
                this.showNotification(message, color);
            }
            if (decayChange) {
                system.updateBalance(-decayChange); // Negative because decay is opposite of growth
                const message = decayChange > 0 ? 'Decay increased!' : 'Decay decreased!';
                const color = decayChange > 0 ? 0x8b4513 : 0x00ff00;
                this.showNotification(message, color);
            }
        }
    }
}

// ... rest of your code remains the same ...
// Make the scene available globally
if (typeof window !== 'undefined') {
    window.GameScene = GameScene;
}