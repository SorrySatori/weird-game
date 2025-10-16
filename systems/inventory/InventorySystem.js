/**
 * Inventory System
 * Manages the player's inventory, including UI and item interactions
 */
export default class InventorySystem {
    constructor(scene) {
        this.scene = scene;
        this.inventoryVisible = false;
        this.inventoryButton = null;
        this.inventoryPanel = null;
        this.slotsContainer = null;
        this.inventorySlots = [];
        this.itemDescription = null;
        this.emptyText = null;
    }

    /**
     * Initialize the inventory system
     */
    init() {
        // Initialize inventory data if not already present
        if (!this.scene.registry.get('inventory')) {
            this.scene.registry.set('inventory', {
                items: [],
                maxItems: 12 // Maximum number of items in inventory
            });
        }

        // Create inventory button (mushroom shape)
        this.createInventoryButton();
        
        // Initialize inventory panel (hidden by default)
        this.createInventoryPanel();
        
        // Set up keyboard shortcut
        this.setupKeyboardShortcut();
    }

    /**
     * Create the inventory button
     */
    createInventoryButton() {
        this.inventoryButton = this.scene.add.container(60, 540);
        this.inventoryButton.setDepth(100);
        
        // Create mushroom cap (circle)
        const mushroomCap = this.scene.add.circle(0, -5, 20, 0x7fff8e);
        
        // Create mushroom stem (rectangle)
        const mushroomStem = this.scene.add.rectangle(0, 10, 10, 15, 0x7fff8e);
        
        // Add spots to mushroom cap
        const spots = this.scene.add.container(0, -5);
        const spot1 = this.scene.add.circle(-8, -5, 3, 0x0a2712);
        const spot2 = this.scene.add.circle(5, 0, 4, 0x0a2712);
        const spot3 = this.scene.add.circle(0, 8, 2, 0x0a2712);
        spots.add([spot1, spot2, spot3]);
        
        // Add "Inventory" text
        const invText = this.scene.add.text(0, 15, 'Inventory', {
            fontSize: '12px',
            fill: '#7fff8e'
        });
        invText.setOrigin(0.5);
        
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
            if (this.scene.clickSound) {
                this.scene.clickSound.play();
            }
            this.toggleInventory();
        });
    }

    /**
     * Set up keyboard shortcut for inventory
     */
    setupKeyboardShortcut() {
        // Toggle inventory with 'I' key
        this.scene.input.keyboard.on('keydown-I', () => {
            if (!this.scene.dialogVisible) {
                this.toggleInventory();
            }
        });
    }

    /**
     * Create the inventory panel
     */
    createInventoryPanel() {
        // Create inventory panel container
        this.inventoryPanel = this.scene.add.container(400, 300);
        this.inventoryPanel.setDepth(1000); // Above most elements
        this.inventoryPanel.setVisible(false);
        
        // Inventory background - make it significantly larger to accommodate money indicator
        const invBg = this.scene.add.rectangle(0, 0, 500, 520, 0x0a2712, 0.9);
        invBg.setStrokeStyle(2, 0x7fff8e);
        this.inventoryPanel.add(invBg);
        
        // Inventory title
        const title = this.scene.add.text(0, -120, 'INVENTORY', {
            fontSize: '28px',
            fill: '#7fff8e',
            fontStyle: 'bold'
        });
        title.setOrigin(0.5);
        this.inventoryPanel.add(title);
        
        // Add money indicator if money system exists
        this.addMoneyIndicator();
        
        // Close button
        const closeBtn = this.scene.add.container(230, -240);
        const closeBg = this.scene.add.rectangle(0, 0, 40, 40, 0x0a2712, 0.6);
        closeBg.setStrokeStyle(1, 0x7fff8e);
        closeBg.setInteractive({ useHandCursor: true });
        const closeText = this.scene.add.text(0, 0, 'X', {
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
            if (this.scene.clickSound) {
                this.scene.clickSound.play();
            }
            this.toggleInventory(false);
        });
        
        // Create inventory slots container - centered in the panel
        this.slotsContainer = this.scene.add.container(0, 0);
        this.inventoryPanel.add(this.slotsContainer);
        
        // Create inventory slots (4x3 grid)
        this.inventorySlots = [];
        const slotSize = 80;
        const padding = 20;
        const gridWidth = 4;
        const gridHeight = 3;
        
        // Calculate total grid width and height
        const totalGridWidth = gridWidth * slotSize + (gridWidth - 1) * padding;
        const totalGridHeight = gridHeight * slotSize + (gridHeight - 1) * padding;
        
        // Calculate starting position to center the grid
        const startX = -totalGridWidth / 2 + slotSize / 2;
        const startY = -totalGridHeight / 2 + slotSize / 2;
        
        for (let row = 0; row < gridHeight; row++) {
            for (let col = 0; col < gridWidth; col++) {
                const x = startX + col * (slotSize + padding);
                const y = startY + row * (slotSize + padding);
                
                // Create slot background
                const slotBg = this.scene.add.rectangle(0, 0, slotSize, slotSize, 0x0f2315, 1);
                slotBg.setStrokeStyle(2, 0x7fff8e, 0.5);
                
                // Create slot container
                const slot = this.scene.add.container(x, y);
                slot.add(slotBg);
                
                // Add slot index
                const slotIndex = row * 4 + col;
                slot.slotIndex = slotIndex;
                
                // Make slot interactive
                slotBg.setInteractive({ useHandCursor: true });
                
                // Show item description on hover
                slotBg.on('pointerover', () => {
                    const inventory = this.scene.registry.get('inventory');
                    if (inventory.items[slotIndex]) {
                        this.showItemDescription(inventory.items[slotIndex], x, y);
                    }
                });
                
                // Hide description when not hovering
                slotBg.on('pointerout', () => {
                    this.hideItemDescription();
                });
                
                // Add slot to container
                this.slotsContainer.add(slot);
                this.inventorySlots.push(slot);
            }
        }
        
        // Create item description container
        this.itemDescription = this.scene.add.container(0, 0);
        this.itemDescription.setVisible(false);
        this.inventoryPanel.add(this.itemDescription);
        
        // Item description background
        const descBg = this.scene.add.rectangle(0, 0, 200, 100, 0x0a2712, 0.8);
        descBg.setStrokeStyle(1, 0x7fff8e);
        this.itemDescription.add(descBg);
        
        // Item name text
        this.itemNameText = this.scene.add.text(0, -30, '', {
            fontSize: '18px',
            fill: '#7fff8e',
            fontStyle: 'bold',
            align: 'center'
        });
        this.itemNameText.setOrigin(0.5);
        this.itemDescription.add(this.itemNameText);
        
        // Item description text
        this.itemDescText = this.scene.add.text(0, 5, '', {
            fontSize: '14px',
            fill: '#7fff8e',
            wordWrap: { width: 180 },
            align: 'center'
        });
        this.itemDescText.setOrigin(0.5, 0);
        this.itemDescription.add(this.itemDescText);
        
        // Empty inventory message
        this.emptyText = this.scene.add.text(0, 0, 'Your inventory is empty', {
            fontSize: '20px',
            fill: '#7fff8e',
            fontStyle: 'italic'
        });
        this.emptyText.setOrigin(0.5);
        this.inventoryPanel.add(this.emptyText);
    }

    /**
     * Add money indicator to inventory panel
     */
    addMoneyIndicator() {
        // Check if money system exists
        if (!this.scene.moneySystem) return;
        
        // Get money UI container
        const moneyContainer = this.scene.moneySystem.getUIContainer();
        if (!moneyContainer) return;
        
        // Position money indicator at the bottom of inventory panel - with plenty of space
        moneyContainer.setPosition(0, 240);
        
        // Add to inventory panel
        this.inventoryPanel.add(moneyContainer);
        
        // Make it visible when inventory is open
        moneyContainer.setVisible(true);
    }

    /**
     * Toggle inventory visibility
     * @param {boolean} forceState - Optional state to force
     */
    toggleInventory(forceState) {
        // Set visibility based on forceState or toggle current state
        this.inventoryVisible = forceState !== undefined ? forceState : !this.inventoryVisible;
        
        // Update inventory panel visibility
        if (this.inventoryPanel) {
            this.inventoryPanel.setVisible(this.inventoryVisible);
        }
        
        // Update inventory display if visible
        if (this.inventoryVisible) {
            this.updateInventoryDisplay();
        }
        
        // Notify scene that inventory visibility changed
        if (this.scene.events) {
            this.scene.events.emit('inventoryVisibilityChanged', this.inventoryVisible);
        }
    }

    /**
     * Update inventory display
     */
    updateInventoryDisplay() {
        // Get current inventory
        const inventory = this.scene.registry.get('inventory');
        
        // Clear all slots
        this.inventorySlots.forEach(slot => {
            // Remove all item sprites from the slot
            slot.each(child => {
                if (child.type !== 'Rectangle') { // Don't remove the background
                    child.destroy();
                }
            }, this);
        });
        
        // Check if inventory is empty
        if (!inventory.items || inventory.items.length === 0) {
            this.emptyText.setVisible(true);
            return;
        }
        
        // Hide empty message
        this.emptyText.setVisible(false);
        
        // Add items to slots
        inventory.items.forEach((item, index) => {
            if (index < this.inventorySlots.length) {
                const slot = this.inventorySlots[index];
                
                // Create item sprite or placeholder
                let itemSprite;
                
                // Try different properties as texture keys
                const possibleTextureKeys = [
                    item.texture,                // Explicit texture property
                    item.id,                     // Item ID
                    item.name.toLowerCase().replace(/\s+/g, '_'),  // Lowercase name with underscores
                    item.name                    // Item name as is
                ];
                
                // Find the first valid texture key
                const textureKey = possibleTextureKeys.find(key => 
                    key && this.scene.textures.exists(key)
                );
                
                if (textureKey) {
                    // Use the found texture
                    itemSprite = this.scene.add.image(0, 0, textureKey);
                    itemSprite.setDisplaySize(60, 60);
                } else {
                    // Create a colored circle as placeholder if no texture found
                    itemSprite = this.scene.add.circle(0, 0, 25, 0x7fff8e, 0.8);
                    
                    // Add first letter of item name
                    const itemInitial = this.scene.add.text(0, 0, item.name.charAt(0), {
                        fontSize: '24px',
                        fill: '#0a2712',
                        fontStyle: 'bold'
                    });
                    itemInitial.setOrigin(0.5);
                    slot.add(itemInitial);
                    
                    // Log missing texture for debugging
                    console.warn(`No texture found for item: ${item.name} (${item.id}). Tried: ${possibleTextureKeys.filter(Boolean).join(', ')}`);
                }
                
                // Add item sprite to slot
                slot.add(itemSprite);
                
                // Make item usable if it has a use function
                if (item.usable) {
                    // Add use indicator
                    const useIndicator = this.scene.add.text(25, 25, 'USE', {
                        fontSize: '12px',
                        fill: '#7fff8e',
                        backgroundColor: 'rgba(10, 39, 18, 0.7)',
                        padding: { x: 3, y: 2 }
                    });
                    useIndicator.setOrigin(1, 1);
                    slot.add(useIndicator);
                    
                    // Make item sprite interactive for usable items
                    itemSprite.setInteractive({ useHandCursor: true });
                    itemSprite.on('pointerdown', () => {
                        this.showUseItemPopup(index, item, slot);
                    });
                }
            }
        }, this);
    }
    
    /**
     * Show item description
     * @param {object} item - The item to show description for
     * @param {number} x - X position of the slot
     * @param {number} y - Y position of the slot
     */
    showItemDescription(item, x, y) {
        // Update description text
        this.itemNameText.setText(item.name);
        this.itemDescText.setText(item.description || 'No description available');
        
        // Position description box
        this.itemDescription.setPosition(x, y + 100);
        this.itemDescription.setVisible(true);
    }

    /**
     * Hide item description
     */
    hideItemDescription() {
        this.itemDescription.setVisible(false);
    }

    /**
     * Use an item from inventory
     * @param {number} index - Index of the item to use
     */
    useItem(index) {
        const inventory = this.scene.registry.get('inventory');
        const item = inventory.items[index];
        
        if (item && item.usable) {
            // Play use sound if available
            if (this.scene.itemUseSound) {
                this.scene.itemUseSound.play();
            }
            
            // Check if this is a drug item (Oltrac)
            const isDrug = item.id && (
                item.id === 'grayOltrac' || 
                item.id === 'violetOltrac' || 
                item.id === 'amberOltrac'
            );
            
            // Apply drug effects if applicable
            if (isDrug && this.scene.effectsSystem) {
                console.log(`Using drug item: ${item.name}`);
                this.scene.effectsSystem.applyDrugEffect(item);
                
                // Close the inventory when using a drug
                this.toggleInventory(false);
            }
            
            // Emit event that item was used
            this.scene.events.emit('itemUsed', item, index);
            
            // If item is consumable, remove it from inventory
            if (item.consumable) {
                this.removeItemFromInventory(index);
            }
            
            // Update inventory display
            this.updateInventoryDisplay();
        }
    }

    /**
     * Add an item to inventory
     * @param {object} item - The item to add
     * @returns {boolean} - Whether the item was added successfully
     */
    addItemToInventory(item) {
        const inventory = this.scene.registry.get('inventory');
        
        // Check if inventory is full
        if (inventory.items.length >= inventory.maxItems) {
            // Show notification if available
            if (this.scene.showNotification) {
                this.scene.showNotification('Inventory is full!', 0xff0000);
            }
            return false;
        }
        
        // Add item to inventory
        inventory.items.push(item);
        
        // Update registry
        this.scene.registry.set('inventory', inventory);
        
        // Show notification if available
        if (this.scene.showNotification) {
            this.scene.showNotification(`Added to inventory: ${item.name}`);
        }
        
        // Play pickup sound if available
        if (this.scene.itemPickupSound) {
            this.scene.itemPickupSound.play();
        }
        
        // Update inventory display if visible
        if (this.inventoryVisible) {
            this.updateInventoryDisplay();
        }
        
        return true;
    }

    /**
     * Remove an item from inventory
     * @param {number|string} itemIdOrIndex - The item ID or index to remove
     * @returns {object|null} - The removed item or null if not found
     */
    removeItemFromInventory(itemIdOrIndex) {
        const inventory = this.scene.registry.get('inventory');
        let index = itemIdOrIndex;
        
        // If itemIdOrIndex is a string, find the item by ID
        if (typeof itemIdOrIndex === 'string') {
            index = inventory.items.findIndex(item => item.id === itemIdOrIndex);
        }
        
        // Check if item exists
        if (index < 0 || index >= inventory.items.length) {
            return null;
        }
        
        // Remove item from inventory
        const removedItem = inventory.items.splice(index, 1)[0];
        
        // Update registry
        this.scene.registry.set('inventory', inventory);
        
        // Update inventory display if visible
        if (this.inventoryVisible) {
            this.updateInventoryDisplay();
        }
        
        return removedItem;
    }

    /**
     * Check if inventory has a specific item
     * @param {string} itemId - The item ID to check for
     * @returns {boolean} - Whether the item is in inventory
     */
    hasItem(itemId) {
        const inventory = this.scene.registry.get('inventory');
        return inventory.items.some(item => item.id === itemId);
    }

    /**
     * Get an item from inventory by ID
     * @param {string} itemId - The item ID to get
     * @returns {object|null} - The item or null if not found
     */
    getItem(itemId) {
        const inventory = this.scene.registry.get('inventory');
        return inventory.items.find(item => item.id === itemId) || null;
    }

    /**
     * Clean up resources
     */
    cleanup() {
        if (this.inventoryButton) {
            this.inventoryButton.destroy();
            this.inventoryButton = null;
        }
        
        if (this.inventoryPanel) {
            this.inventoryPanel.destroy();
            this.inventoryPanel = null;
        }
        
        this.inventorySlots = [];
        this.slotsContainer = null;
        if (this._activeUsePopup) {
            this._activeUsePopup.destroy(true);
            this._activeUsePopup = null;
        }
    }
    
    /**
     * Get all inventory items for serialization
     * @returns {Object} Inventory data for saving
     */
    getInventoryData() {
        return this.scene.registry.get('inventory') || {
            items: [],
            maxItems: 12
        };
    }
    
    /**
     * Load inventory data from a save file
     * @param {Object} inventoryData - Inventory data from save file
     */
    loadInventoryData(inventoryData) {
        if (!inventoryData) return;
        
        // Update registry with saved inventory data
        this.scene.registry.set('inventory', inventoryData);
        
        // Update inventory display if visible
        if (this.inventoryVisible) {
            this.updateInventoryDisplay();
        }
    }

    /**
     * Show a popup menu for using an item
     * @param {number} index - Index of the item
     * @param {object} item - The item object
     * @param {Phaser.GameObjects.Container} slot - The slot container
     */
    showUseItemPopup(index, item, slot) {
        console.log('showUseItemPopup called for', item.name, 'at index', index);
        
        // Prevent multiple popups
        if (this._activeUsePopup) {
            console.log('Destroying existing popup');
            this._activeUsePopup.destroy(true);
            this._activeUsePopup = null;
        }

        // Create a centered popup directly on the camera/screen
        // Get the camera center coordinates
        const centerX = this.scene.cameras.main.width / 2;
        const centerY = this.scene.cameras.main.height / 2;
        console.log('Creating popup at center:', centerX, centerY);
        
        // Create a popup container that's fixed to the camera
        const popup = this.scene.add.container(centerX, centerY);
        popup.setDepth(9999); // Extremely high depth to ensure it's on top
        
        // Create a semi-transparent overlay for the entire screen
        const overlay = this.scene.add.rectangle(
            0, 0,
            this.scene.cameras.main.width * 2,
            this.scene.cameras.main.height * 2,
            0x000000, 0.5
        );
        overlay.setOrigin(0.5);
        popup.add(overlay);
        
        // Create a visible popup background
        const bg = this.scene.add.rectangle(0, 0, 200, 120, 0x0a2712, 0.95);
        bg.setStrokeStyle(4, 0x7fff8e, 1); // Thicker, more visible border
        popup.add(bg);
        
        // Add item name at the top
        const itemName = this.scene.add.text(0, -40, item.name, {
            fontSize: '20px',
            fill: '#7fff8e',
            fontStyle: 'bold',
            align: 'center'
        });
        itemName.setOrigin(0.5);
        popup.add(itemName);
        
        // Use button
        const useBtn = this.scene.add.text(-50, 10, 'Use', {
            fontSize: '22px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(10, 39, 18, 0.8)',
            padding: { x: 15, y: 8 },
            align: 'center'
        });
        useBtn.setOrigin(0.5);
        useBtn.setInteractive({ useHandCursor: true });
        popup.add(useBtn);

        // Cancel button
        const cancelBtn = this.scene.add.text(50, 10, 'Cancel', {
            fontSize: '22px',
            fill: '#ff8888',
            backgroundColor: 'rgba(39, 10, 18, 0.8)',
            padding: { x: 15, y: 8 },
            align: 'center'
        });
        cancelBtn.setOrigin(0.5);
        cancelBtn.setInteractive({ useHandCursor: true });
        popup.add(cancelBtn);

        // Button logic
        useBtn.on('pointerdown', () => {
            this.useItem(index);
            popup.destroy(true);
            this._activeUsePopup = null;
        });
        cancelBtn.on('pointerdown', () => {
            popup.destroy(true);
            this._activeUsePopup = null;
        });

        // Store reference for cleanup
        this._activeUsePopup = popup;

        // Optionally close popup if overlay is clicked
        overlay.setInteractive();
        overlay.on('pointerdown', () => {
            if (this._activeUsePopup) {
                this._activeUsePopup.destroy(true);
                this._activeUsePopup = null;
            }
        });
    }
}
