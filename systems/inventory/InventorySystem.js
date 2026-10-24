import LanguageSystem from '../LanguageSystem.js';
import { isRecording, isRecordingPlaying, toggleRecording } from '../../utils/Recordings.js';
import { createHudButton } from '../../utils/hudButton.js';

/**
 * Inventory System
 * Manages the player's inventory, including UI and item interactions
 */
const L = () => LanguageSystem.getInstance();

// Grid layout: 6×3 slots per page, pages flip with the arrows or the mouse wheel.
const SLOT_SIZE = 80;
const SLOT_PAD = 20;
const GRID_COLS = 6;
const GRID_ROWS = 3;
const PAGE_SIZE = GRID_COLS * GRID_ROWS;
const GRID_W = GRID_COLS * SLOT_SIZE + (GRID_COLS - 1) * SLOT_PAD;
const GRID_H = GRID_ROWS * SLOT_SIZE + (GRID_ROWS - 1) * SLOT_PAD;
const GRID_CENTER_Y = -70;
const PANEL_W = 700;
const PANEL_H = 560;
const DESC_H = 110;

// Display order: lower group sorts first. Untyped items keep their pickup order in the middle,
// so the inventory is unlimited but quest-critical things stay on the first page.
const TYPE_ORDER = { key_item: 0, tool: 1, drug: 2, consumable: 2, recording: 4, decoration: 5 };
const DEFAULT_TYPE_ORDER = 3;

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
        this.pager = null;
        this.currentPage = 0;
        this._onWheel = null;
    }

    /**
     * Initialize the inventory system
     */
    init() {
        // Initialize inventory data if not already present
        if (!this.scene.registry.get('inventory')) {
            this.scene.registry.set('inventory', { items: [] });
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
        const { container } = createHudButton(this.scene, 'inventory', L().t('ui.inventory.button'), () => {
            if (this.scene.clickSound) {
                this.scene.clickSound.play();
            }
            this.toggleInventory();
        });
        this.inventoryButton = container;
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
        this.inventoryPanel = this.scene.add.container(this.scene.scale.width / 2, 300);
        this.inventoryPanel.setDepth(1000); // Above most elements
        this.inventoryPanel.setVisible(false);
        
        // Inventory background
        const invBg = this.scene.add.rectangle(0, 0, PANEL_W, PANEL_H, 0x0a2712, 0.9);
        invBg.setStrokeStyle(2, 0x7fff8e);
        this.inventoryPanel.add(invBg);
        
        // Inventory title
        const title = this.scene.add.text(0, -PANEL_H / 2 + 30, L().t('ui.inventory.panelTitle'), {
            fontSize: '28px',
            fill: '#7fff8e',
            fontStyle: 'bold'
        });
        title.setOrigin(0.5);
        this.inventoryPanel.add(title);
        
        // Add money indicator if money system exists
        this.addMoneyIndicator();
        
        // Close button
        const closeBtn = this.scene.add.container(PANEL_W / 2 - 30, -PANEL_H / 2 + 30);
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
        this.slotsContainer = this.scene.add.container(0, GRID_CENTER_Y);
        this.inventoryPanel.add(this.slotsContainer);
        
        // Create one page of slots. Each slot is reused across pages: updateInventoryDisplay()
        // sets slot.item / slot.itemIndex (the REAL index into inventory.items) for the current page.
        this.inventorySlots = [];
        const startX = -GRID_W / 2 + SLOT_SIZE / 2;
        const startY = -GRID_H / 2 + SLOT_SIZE / 2;
        
        for (let row = 0; row < GRID_ROWS; row++) {
            for (let col = 0; col < GRID_COLS; col++) {
                const x = startX + col * (SLOT_SIZE + SLOT_PAD);
                const y = startY + row * (SLOT_SIZE + SLOT_PAD);
                
                // Create slot background
                const slotBg = this.scene.add.rectangle(0, 0, SLOT_SIZE, SLOT_SIZE, 0x0f2315, 1);
                slotBg.setStrokeStyle(2, 0x7fff8e, 0.5);
                
                // Create slot container
                const slot = this.scene.add.container(x, y);
                slot.add(slotBg);
                slot.slotIndex = row * GRID_COLS + col;
                slot.item = null;
                slot.itemIndex = -1;
                
                // Make slot interactive
                slotBg.setInteractive({ useHandCursor: true });
                
                // Show item description on hover
                slotBg.on('pointerover', () => {
                    if (slot.item) {
                        this.showItemDescription(slot.item);
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
        
        // Item description strip below the grid (fixed place, so it never leaves the panel)
        const descY = GRID_CENTER_Y + GRID_H / 2 + 65;
        this.itemDescription = this.scene.add.container(0, descY);
        this.inventoryPanel.add(this.itemDescription);
        
        const descBg = this.scene.add.rectangle(0, 0, GRID_W + 40, DESC_H, 0x0a2712, 0.8);
        descBg.setStrokeStyle(1, 0x7fff8e, 0.5);
        this.itemDescription.add(descBg);
        
        // Item name text
        this.itemNameText = this.scene.add.text(0, -DESC_H / 2 + 16, '', {
            fontSize: '18px',
            fill: '#7fff8e',
            fontStyle: 'bold',
            align: 'center'
        });
        this.itemNameText.setOrigin(0.5);
        this.itemDescription.add(this.itemNameText);
        
        // Item description text
        this.itemDescText = this.scene.add.text(0, -DESC_H / 2 + 32, '', {
            fontSize: '14px',
            fill: '#7fff8e',
            wordWrap: { width: GRID_W },
            align: 'center'
        });
        this.itemDescText.setOrigin(0.5, 0);
        this.itemDescription.add(this.itemDescText);
        
        // Pager (hidden while everything fits on one page)
        this.createPager(descY + DESC_H / 2 + 22);
        
        // Empty inventory message
        this.emptyText = this.scene.add.text(0, GRID_CENTER_Y, L().t('ui.inventory.emptyItems'), {
            fontSize: '20px',
            fill: '#7fff8e',
            fontStyle: 'italic'
        });
        this.emptyText.setOrigin(0.5);
        this.inventoryPanel.add(this.emptyText);
        
        // Mouse wheel flips pages while the panel is open
        this._onWheel = (pointer, over, dx, dy) => {
            if (!this.inventoryVisible || this._activeUsePopup) return;
            if (dy > 0) this.changePage(1);
            else if (dy < 0) this.changePage(-1);
        };
        this.scene.input.on('wheel', this._onWheel);
        
        // Flip a PLAY/STOP label back when an ampule finishes on its own
        this._onRecordingEnded = () => { if (this.inventoryVisible) this.updateInventoryDisplay(); };
        this.scene.events.on('recordingEnded', this._onRecordingEnded);
    }

    /**
     * Create the page navigation row: [<]  1 / 3  [>]
     * @param {number} y - Panel-local y position
     */
    createPager(y) {
        this.pager = this.scene.add.container(0, y);
        this.pager.setVisible(false);
        this.inventoryPanel.add(this.pager);
        
        const makeArrow = (x, label, delta) => {
            const btn = this.scene.add.text(x, 0, label, {
                fontSize: '22px',
                fill: '#7fff8e',
                backgroundColor: 'rgba(15, 35, 21, 0.9)',
                padding: { x: 12, y: 4 }
            });
            btn.setOrigin(0.5);
            btn.setInteractive({ useHandCursor: true });
            btn.on('pointerover', () => { if (btn.alpha === 1) btn.setStyle({ fill: '#b3ffcc' }); });
            btn.on('pointerout', () => btn.setStyle({ fill: '#7fff8e' }));
            btn.on('pointerdown', () => this.changePage(delta));
            this.pager.add(btn);
            return btn;
        };
        
        this.pagerPrev = makeArrow(-70, '<', -1);
        this.pagerNext = makeArrow(70, '>', 1);
        this.pagerLabel = this.scene.add.text(0, 0, '', {
            fontSize: '16px',
            fill: '#7fff8e'
        });
        this.pagerLabel.setOrigin(0.5);
        this.pager.add(this.pagerLabel);
    }

    /**
     * Number of pages needed for the current inventory (always ≥ 1)
     */
    pageCount() {
        const items = this.scene.registry.get('inventory')?.items || [];
        return Math.max(1, Math.ceil(items.length / PAGE_SIZE));
    }

    /**
     * Flip pages by delta (clamped); redraws the grid
     * @param {number} delta - +1 / -1
     */
    changePage(delta) {
        const next = Phaser.Math.Clamp(this.currentPage + delta, 0, this.pageCount() - 1);
        if (next === this.currentPage) return;
        this.currentPage = next;
        if (this.scene.clickSound) {
            this.scene.clickSound.play();
        }
        this.updateInventoryDisplay();
    }

    /**
     * Refresh the pager row for the given page count
     * @param {number} totalPages
     */
    updatePager(totalPages) {
        if (!this.pager) return;
        this.pager.setVisible(totalPages > 1);
        this.pagerLabel.setText(`${this.currentPage + 1} / ${totalPages}`);
        this.pagerPrev.setAlpha(this.currentPage > 0 ? 1 : 0.35);
        this.pagerNext.setAlpha(this.currentPage < totalPages - 1 ? 1 : 0.35);
    }

    /**
     * Items in display order, each paired with its REAL index into inventory.items
     * (stable: same-group items keep pickup order).
     * @param {object[]} items
     * @returns {{item: object, index: number}[]}
     */
    getDisplayOrder(items) {
        return items
            .map((item, index) => ({ item, index, group: TYPE_ORDER[item.type] ?? DEFAULT_TYPE_ORDER }))
            .sort((a, b) => a.group - b.group || a.index - b.index);
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
        
        // Position money indicator at the bottom of inventory panel
        moneyContainer.setPosition(0, PANEL_H / 2 - 28);
        
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
        const items = inventory?.items || [];
        
        // Clear all slots
        this.inventorySlots.forEach(slot => {
            slot.item = null;
            slot.itemIndex = -1;
            // Remove all item sprites from the slot
            slot.each(child => {
                if (child.type !== 'Rectangle') { // Don't remove the background
                    child.destroy();
                }
            }, this);
        });
        this.hideItemDescription();
        
        // Check if inventory is empty
        if (items.length === 0) {
            this.currentPage = 0;
            this.emptyText.setVisible(true);
            this.updatePager(1);
            return;
        }
        
        // Hide empty message
        this.emptyText.setVisible(false);
        
        // Pick the current page of the (type-sorted) view
        const view = this.getDisplayOrder(items);
        const totalPages = Math.max(1, Math.ceil(view.length / PAGE_SIZE));
        this.currentPage = Phaser.Math.Clamp(this.currentPage, 0, totalPages - 1);
        const pageItems = view.slice(this.currentPage * PAGE_SIZE, (this.currentPage + 1) * PAGE_SIZE);
        
        // Add items to slots
        pageItems.forEach(({ item, index }, slotIdx) => {
            {
                const slot = this.inventorySlots[slotIdx];
                slot.item = item;
                slot.itemIndex = index;
                
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
                    if (item.tint) itemSprite.setTint(item.tint);
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
                    // Add use indicator (recordings: PLAY / STOP)
                    const labelKey = isRecording(item)
                        ? (isRecordingPlaying(item.id) ? 'ui.inventory.stop' : 'ui.inventory.play')
                        : 'ui.inventory.use';
                    const useIndicator = this.scene.add.text(25, 25, L().t(labelKey), {
                        fontSize: '12px',
                        fill: '#7fff8e',
                        backgroundColor: 'rgba(10, 39, 18, 0.7)',
                        padding: { x: 3, y: 2 }
                    });
                    useIndicator.setOrigin(1, 1);
                    slot.add(useIndicator);
                    
                    // Make item sprite interactive for usable items. It sits on top of the slot
                    // background and takes the pointer, so it must show the tooltip itself.
                    itemSprite.setInteractive({ useHandCursor: true });
                    itemSprite.on('pointerover', () => this.showItemDescription(item));
                    itemSprite.on('pointerout', () => this.hideItemDescription());
                    itemSprite.on('pointerdown', () => {
                        if (isRecording(item)) {
                            this.useItem(index); // ampules toggle playback directly, no confirm popup
                        } else {
                            this.showUseItemPopup(index, item, slot);
                        }
                    });
                }
            }
        }, this);
        
        this.updatePager(totalPages);
    }
    
    /**
     * Show item description in the strip below the grid
     * @param {object} item - The item to show description for
     */
    showItemDescription(item) {
        if (!this.itemNameText) return;
        this.itemNameText.setText(L().itemName(item));
        this.itemDescText.setFontSize(14).setText(L().itemDescription(item));
        // Long lore texts step down a size so they stay inside the strip
        if (this.itemDescText.height > DESC_H - 36) this.itemDescText.setFontSize(12);
    }

    /**
     * Clear the description strip
     */
    hideItemDescription() {
        if (!this.itemNameText) return;
        this.itemNameText.setText('');
        this.itemDescText.setText('');
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
            
            // Check if this is a drug item (Oltrac variants, or anything flagged isDrug)
            const isDrug = item.isDrug === true || (item.id && (
                item.id === 'grayOltrac' ||
                item.id === 'violetOltrac' ||
                item.id === 'amberOltrac'
            ));
            
            // Sound ampules: toggle playback, keep the panel open
            if (isRecording(item)) {
                const result = toggleRecording(this.scene, item);
                if (result === 'missing' && this.scene.showNotification) {
                    this.scene.showNotification(L().t('notifications.ampuleSilent'));
                }
                this.updateInventoryDisplay();
                return;
            }
            
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
        
        const existingItem = inventory.items.find(invItem => invItem.id === item.id);
        
        if (existingItem) {
            // If item is stackable, increase quantity
            if (item.stackable) {
                existingItem.quantity = (existingItem.quantity || 1) + (item.quantity || 1);
                
                // Update registry
                this.scene.registry.set('inventory', inventory);
                
                // Show notification
                if (this.scene.showNotification) {
                    this.scene.showNotification(L().t('notifications.addedToInventoryQty', { qty: item.quantity || 1, item: L().itemName(item) }));
                }
                
                // Play pickup sound
                if (this.scene.itemPickupSound) {
                    this.scene.itemPickupSound.play();
                }
                
                // Update display
                if (this.inventoryVisible) {
                    this.updateInventoryDisplay();
                }
                
                return true;
            } else {

                return false;
            }
        }
        
        // No capacity limit: the panel pages through everything the player carries.
        
        // Initialize quantity for new items
        if (!item.quantity) {
            item.quantity = 1;
        }
        
        // Add item to inventory
        inventory.items.push(item);
        
        // Update registry
        this.scene.registry.set('inventory', inventory);
        
        // Show notification if available
        if (this.scene.showNotification) {
            this.scene.showNotification(L().t('notifications.addedToInventory', { item: L().itemName(item) }));
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
     * All carried items (used by the shop's Sell tab)
     * @returns {object[]}
     */
    getItems() {
        return this.scene.registry.get('inventory')?.items || [];
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
        this.pager = null;
        this.itemNameText = null;
        this.itemDescText = null;
        if (this._onWheel && this.scene.input) {
            this.scene.input.off('wheel', this._onWheel);
            this._onWheel = null;
        }
        if (this._onRecordingEnded && this.scene.events) {
            this.scene.events.off('recordingEnded', this._onRecordingEnded);
            this._onRecordingEnded = null;
        }
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
        return this.scene.registry.get('inventory') || { items: [] };
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
        const itemName = this.scene.add.text(0, -40, L().itemName(item), {
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
