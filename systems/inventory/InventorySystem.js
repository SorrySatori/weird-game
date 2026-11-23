import LanguageSystem from '../LanguageSystem.js';
import { isRecording, isRecordingPlaying, toggleRecording } from '../../utils/Recordings.js';
import { createHudButton } from '../../utils/hudButton.js';
import { MENU_COLORS, MENU_FONT } from '../../utils/menuKit.js';
import { gridScreen, itemIcon, openPaperScreen, closePaperScreen, refreshPaperScreen } from '../../ui/paperKit.js';

/**
 * Inventory System
 * The player's items (registry 'inventory'), using them, and the inventory screen (ui/paperKit.js gridScreen, in the
 * style chosen in the Settings: a curiosity cabinet, or the bag tipped out on a desk). The HUD satchel or I open it;
 * I, ESC (GameMenu) or its cross close it.
 */
const L = () => LanguageSystem.getInstance();

// Display order: lower group sorts first. Untyped items keep their pickup order in the middle,
// so the inventory is unlimited but quest-critical things stay on the first page.
const TYPE_ORDER = { key_item: 0, tool: 1, drug: 2, consumable: 2, recording: 4, decoration: 5 };
const DEFAULT_TYPE_ORDER = 3;

export default class InventorySystem {
    constructor(scene) {
        this.scene = scene;
        this.inventoryVisible = false;
        this.inventoryButton = null;
        this.designOpen = false;
    }

    /**
     * Initialize the inventory system
     */
    init() {
        if (!this.scene.registry.get('inventory')) {
            this.scene.registry.set('inventory', { items: [] });
        }
        this.createInventoryButton();
        this.setupKeyboardShortcut();
        this._onRecordingEnded = () => this.updateInventoryDisplay();       // a Play label flips back to Stop
        this.scene.events.on('recordingEnded', this._onRecordingEnded);
        this.scene.events.once('shutdown', () => this.cleanup());
    }

    /** the satchel on the HUD */
    createInventoryButton() {
        const { container } = createHudButton(this.scene, 'inventory', L().t('ui.inventory.button'), () => {
            if (this.scene.clickSound) {
                this.scene.clickSound.play();
            }
            this.toggleInventory();
        });
        this.inventoryButton = container;
    }

    /** I toggles (the open screen's own keys live in ui/paperKit.js) */
    setupKeyboardShortcut() {
        this._onI = () => {
            if (!this.scene.dialogVisible) this.toggleInventory();
        };
        this.scene.input.keyboard.on('keydown-I', this._onI);
    }

    /** the texture an item shows: item.texture, its id, or its name (utils/itemIcons.js); null = lettered placeholder */
    iconKey(item) {
        return [item.texture, item.id, item.name?.toLowerCase().replace(/\s+/g, '_'), item.name]
            .find(key => key && this.scene.textures.exists(key)) || null;
    }

    /** an item's icon (or a lettered enamel disc) at x, y, size px (the shop's grid uses it too); returns the game objects */
    makeIcon(item, x, y, size) {
        const sc = this.scene, key = this.iconKey(item);
        if (key) {
            const img = sc.add.image(x, y, key).setDisplaySize(size, size);
            if (item.tint) img.setTint(item.tint);
            return [img];
        }
        console.warn(`No texture found for item: ${item.name} (${item.id})`);
        return [
            sc.add.circle(x, y, size * 0.4, 0x16251b, 1).setStrokeStyle(2, 0x9a7b3a),
            sc.add.text(x, y, (L().itemName(item) || '?').charAt(0), {
                fontFamily: MENU_FONT, fontSize: `${Math.round(size * 0.4)}px`, fontStyle: 'bold', color: MENU_COLORS.title,
                stroke: MENU_COLORS.stroke, strokeThickness: 3
            }).setOrigin(0.5),
        ];
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

    // ------------------------------------------------------------------ open / close / redraw
    /**
     * Toggle inventory visibility
     * @param {boolean} forceState - Optional state to force
     */
    toggleInventory(forceState) {
        this.inventoryVisible = forceState !== undefined ? forceState : !this.inventoryVisible;
        if (this.inventoryVisible) this.openScreen(); else this.closeScreen();
        if (this.scene.events) {
            this.scene.events.emit('inventoryVisibilityChanged', this.inventoryVisible);
        }
    }

    /** the inventory screen (ui/paperKit.js) */
    openScreen() {
        openPaperScreen(this);
        this.designOpen = true;
    }

    closeScreen() {
        if (!this.designOpen) return;
        this.designOpen = false;
        closePaperScreen(this);
    }

    /** paperKit: another panel took the screen over */
    paperClosed() {
        this.designOpen = false;
        this.inventoryVisible = false;
        this.scene.events?.emit('inventoryVisibilityChanged', false);
    }

    close() { this.toggleInventory(false); }

    /** paperKit: what the screen shows and does */
    buildScreen(overlay, style) {
        const lang = L();
        const all = () => this.scene.registry.get('inventory')?.items || [];
        const t = (key, fallback, params) => { const v = lang.t(key, params); return v === key ? fallback : v; };
        return gridScreen(overlay, style, {
            title: lang.t('ui.inventory.panelTitle'),
            cardHead: t('ui.inventory.catalogue', 'CATALOGUE'),
            empty: lang.t('ui.inventory.emptyItems'),
            hint: lang.t('ui.inventory.selectHint'),
            bag: true, bagMore: t('ui.inventory.tipOutMore', 'tip out more'),
            items: () => this.getDisplayOrder(all()).map(v => v.item),
            name: (it) => lang.itemName(it),
            qty: (it) => it.quantity || 1,
            icon: (it, x, y, k) => itemIcon(overlay, this.iconKey(it), it, lang.itemName(it), x, y, k),
            mark: (it) => (it.usable ? (isRecording(it) && isRecordingPlaying(it.id) ? 'playing' : 'usable') : null),
            detail: (it) => {
                const kindKey = `ui.inventory.types.${it.type}`, kind = it.type ? lang.t(kindKey) : '';
                const label = isRecording(it) ? (isRecordingPlaying(it.id) ? 'ui.inventory.stopItem' : 'ui.inventory.playItem') : 'ui.inventory.useItem';
                return {
                    name: lang.itemName(it), kind: kind && kind !== kindKey ? kind : '', desc: lang.itemDescription(it),
                    button: it.usable ? { label: lang.t(label), act: () => { const i = all().indexOf(it); if (i >= 0) this.useItem(i); } } : null
                };
            },
            footer: () => (this.scene.moneySystem ? t('shop.balance', `${this.scene.moneySystem.amount ?? 0}`, { amount: this.scene.moneySystem.amount ?? 0 }) : '')
        });
    }

    /** redraw the open screen (items added, used up, an ampule stopped) */
    updateInventoryDisplay() {
        refreshPaperScreen(this);
    }

    // ------------------------------------------------------------------ data
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
     * Use up ONE of an item: a stack loses one, a single item is removed (removeItemFromInventory takes the whole stack)
     * @param {string} itemId
     * @returns {boolean} whether there was one to take
     */
    consumeOne(itemId) {
        const inventory = this.scene.registry.get('inventory');
        const item = inventory?.items.find(i => i.id === itemId);
        if (!item) return false;
        if ((item.quantity || 1) > 1) {
            item.quantity -= 1;
            this.scene.registry.set('inventory', inventory);
            if (this.inventoryVisible) this.updateInventoryDisplay();
            return true;
        }
        return !!this.removeItemFromInventory(itemId);
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
     * Clean up resources (also on the scene's shutdown: scene instances are re-used)
     */
    cleanup() {
        this.closeScreen();
        this.inventoryVisible = false;
        if (this.inventoryButton) {
            this.inventoryButton.destroy();
            this.inventoryButton = null;
        }
        if (this._onI && this.scene.input?.keyboard) {
            this.scene.input.keyboard.off('keydown-I', this._onI);
            this._onI = null;
        }
        if (this._onRecordingEnded) {
            this.scene.events?.off('recordingEnded', this._onRecordingEnded);
            this._onRecordingEnded = null;
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
}
