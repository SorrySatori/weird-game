import LanguageSystem from '../LanguageSystem.js';
import { isRecording, isRecordingPlaying, toggleRecording } from '../../utils/Recordings.js';
import { createHudButton } from '../../utils/hudButton.js';
import { createMenuPanel, addPanelClose, createMenuIconButton, playMenuSound, MENU_COLORS, MENU_FONT } from '../../utils/menuKit.js';

/**
 * Inventory System
 * Manages the player's inventory, including UI and item interactions.
 *
 * The panel is the menu kit's 'ledger' frame (as the journal and the quest log): a 6×4 grid of bronze item sockets on
 * the left (pages flip with the round arrows, the mouse wheel or PgUp / PgDn), the chosen item's card on the right
 * (big icon, name, kind, description, and its Use / Play button), the money underneath. Hover previews an item, a
 * click selects it; arrows move the selection, Enter / Space uses it.
 */
const L = () => LanguageSystem.getInstance();

const S = 2;                                   // pixel-art scale of the kit
const GRID_COLS = 6;
const GRID_ROWS = 4;
const PAGE_SIZE = GRID_COLS * GRID_ROWS;
const SLOT = 80;                               // menu_islot 40×40 at 2×
const SLOT_GAP = 8;
const GRID = { left: -432, top: -204 };        // relative to the panel centre
const GRID_W = GRID_COLS * SLOT + (GRID_COLS - 1) * SLOT_GAP;
const GRID_H = GRID_ROWS * SLOT + (GRID_ROWS - 1) * SLOT_GAP;
const ICON = 60;                               // item icons are drawn 60×60 (utils/itemIcons.js)
const CARD = { x: 112, y: -204, w: 320, h: 416 };
const CARD_CX = CARD.x + CARD.w / 2;
const FOOT_Y = GRID.top + GRID_H + 40;         // the pager + money row
const TEXT = {
    name: { fontFamily: MENU_FONT, fontSize: '20px', fontStyle: 'bold', color: MENU_COLORS.title, stroke: MENU_COLORS.stroke, strokeThickness: 3, align: 'center' },
    kind: { fontFamily: MENU_FONT, fontSize: '14px', fontStyle: 'italic', color: MENU_COLORS.dim, align: 'center' },
    body: { fontFamily: MENU_FONT, fontSize: '15px', color: MENU_COLORS.text, lineSpacing: 4 },
    small: { fontFamily: MENU_FONT, fontSize: '15px', color: MENU_COLORS.text, stroke: MENU_COLORS.stroke, strokeThickness: 4 },
};

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
        this.inventorySlots = [];
        this.currentPage = 0;
        this.selectedItem = null;              // the item object (indices shift when something is removed)
        this.hoverItem = null;
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
        this.createInventoryButton();
        this.createInventoryPanel();
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
     * Keys: I toggles; while open, arrows move the selection, Enter / Space uses it, PgUp / PgDn flip pages
     */
    setupKeyboardShortcut() {
        this.scene.input.keyboard.on('keydown-I', () => {
            if (!this.scene.dialogVisible) {
                this.toggleInventory();
            }
        });
        this._onKey = (event) => this.handleKey(event);
        this.scene.input.keyboard.on('keydown', this._onKey);
    }

    // ------------------------------------------------------------------ the panel
    createInventoryPanel() {
        const sc = this.scene;
        const panel = createMenuPanel(sc, 'ledger', sc.scale.width / 2, 300, L().t('ui.inventory.panelTitle'));
        this.inventoryPanel = panel.container.setDepth(1000).setScrollFactor(0, 0, true).setVisible(false);
        addPanelClose(sc, panel, () => this.toggleInventory(false));
        const add = (o) => { this.inventoryPanel.add(o); return o; };

        // the sockets: one page, re-filled per page (slot.item / slot.itemIndex = the REAL index into inventory.items)
        this.inventorySlots = [];
        for (let row = 0; row < GRID_ROWS; row++) {
            for (let col = 0; col < GRID_COLS; col++) {
                const x = GRID.left + SLOT / 2 + col * (SLOT + SLOT_GAP);
                const y = GRID.top + SLOT / 2 + row * (SLOT + SLOT_GAP);
                const bg = add(sc.add.image(x, y, 'menuItemSlot', 0).setScale(S).setInteractive({ useHandCursor: true }));
                bg.input.hitArea.setTo(1, 1, 38, 38);
                const slot = { bg, x, y, slotIndex: row * GRID_COLS + col, item: null, itemIndex: -1, parts: [], hover: false };
                bg.on('pointerover', () => {
                    slot.hover = true; this.drawSlot(slot);
                    if (slot.item) { this.hoverItem = slot.item; this.showDetails(); playMenuSound(sc, 'hoverSound', 0.35); }
                });
                bg.on('pointerout', () => {
                    slot.hover = false; this.drawSlot(slot);
                    if (this.hoverItem === slot.item) { this.hoverItem = null; this.showDetails(); }
                });
                bg.on('pointerdown', (pointer, lx, ly, event) => {
                    event?.stopPropagation();
                    if (!slot.item) return;
                    playMenuSound(sc, 'clickSound');
                    this.select(slot.item);
                });
                this.inventorySlots.push(slot);
            }
        }
        this.emptyText = add(sc.add.text(GRID.left + GRID_W / 2, GRID.top + GRID_H / 2, L().t('ui.inventory.emptyItems'), {
            ...TEXT.body, fontSize: '18px', fontStyle: 'italic', color: MENU_COLORS.dim,
        }).setOrigin(0.5));

        // the chosen item's card
        add(sc.add.nineslice(CARD.x, CARD.y, 'menuCard', 0, CARD.w / S, CARD.h / S, 7, 7, 7, 7).setOrigin(0, 0).setScale(S));
        this.detailSocket = add(sc.add.image(CARD_CX, CARD.y + 92, 'menuItemSlot', 1).setScale(4));
        this.detailQty = add(sc.add.text(CARD_CX + 62, CARD.y + 150, '', TEXT.small).setOrigin(1, 1));
        this.detailName = add(sc.add.text(CARD_CX, CARD.y + 184, '', { ...TEXT.name, wordWrap: { width: CARD.w - 36 } }).setOrigin(0.5, 0));
        this.detailKind = add(sc.add.text(CARD_CX, 0, '', TEXT.kind).setOrigin(0.5, 0));
        this.detailDesc = add(sc.add.text(CARD.x + 18, 0, '', { ...TEXT.body, wordWrap: { width: CARD.w - 36 } }));
        this.detailHint = add(sc.add.text(CARD_CX, CARD.y + 184, L().t('ui.inventory.selectHint'), {
            ...TEXT.kind, fontSize: '15px', wordWrap: { width: CARD.w - 40 },
        }).setOrigin(0.5, 0));
        this.createUseButton(add);

        // the pager + the money
        this.pagerPrev = add(createMenuIconButton(sc, GRID.left + GRID_W / 2 - 74, FOOT_Y, 'left', () => this.changePage(-1)));
        this.pagerNext = add(createMenuIconButton(sc, GRID.left + GRID_W / 2 + 74, FOOT_Y, 'right', () => this.changePage(1)));
        this.pagerLabel = add(sc.add.text(GRID.left + GRID_W / 2, FOOT_Y, '', TEXT.small).setOrigin(0.5));
        this.coin = add(sc.add.image(GRID.left + 14, FOOT_Y, 'menuCoin').setScale(S));
        this.moneyText = add(sc.add.text(GRID.left + 34, FOOT_Y, '', { ...TEXT.small, fontSize: '17px', color: MENU_COLORS.title }).setOrigin(0, 0.5));

        // the mouse wheel flips pages while the panel is open
        this._onWheel = (pointer, over, dx, dy) => {
            if (!this.inventoryVisible) return;
            if (dy > 0) this.changePage(1);
            else if (dy < 0) this.changePage(-1);
        };
        sc.input.on('wheel', this._onWheel);

        // flip a Play / Stop label back when an ampule finishes on its own
        this._onRecordingEnded = () => { if (this.inventoryVisible) this.updateInventoryDisplay(); };
        sc.events.on('recordingEnded', this._onRecordingEnded);
        sc.events.once('shutdown', () => this.cleanup());
        this.showDetails();
    }

    /** the Use / Play / Stop button on the item card: a tab plaque (idle / hover / pressed) */
    createUseButton(add) {
        const sc = this.scene, y = CARD.y + CARD.h - 34;
        const img = add(sc.add.image(CARD_CX, y, 'menuTab', 0).setScale(S).setInteractive({ useHandCursor: true }));
        img.input.hitArea.setTo(1, 1, 66, 18);
        const text = add(sc.add.text(CARD_CX, y + 1, '', { ...TEXT.small, fontSize: '16px', strokeThickness: 3 }).setOrigin(0.5));
        img.on('pointerover', () => { img.setFrame(1); text.setColor(MENU_COLORS.textHover); playMenuSound(sc, 'hoverSound', 0.5); });
        img.on('pointerout', () => { img.setFrame(0); text.setColor(MENU_COLORS.text); });
        img.on('pointerdown', (pointer, lx, ly, event) => {
            event?.stopPropagation();
            img.setFrame(2); text.y = y - 1;
            playMenuSound(sc, 'clickSound');
            sc.time.delayedCall(110, () => {
                if (!img.active) return;
                img.setFrame(1); text.y = y + 1;
                this.useSelected();
            });
        });
        this.useButton = { img, text };
    }

    drawSlot(slot) {
        const selected = slot.item && slot.item === this.selectedItem;
        slot.bg.setFrame(selected ? 3 : slot.hover && slot.item ? 2 : slot.item ? 1 : 0);
    }

    /** the texture an item shows: item.texture, its id, or its name (utils/itemIcons.js); null = lettered placeholder */
    iconKey(item) {
        return [item.texture, item.id, item.name?.toLowerCase().replace(/\s+/g, '_'), item.name]
            .find(key => key && this.scene.textures.exists(key)) || null;
    }

    /** an item's icon (or a lettered enamel disc) at x, y; returns the game objects */
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
            sc.add.text(x, y, (L().itemName(item) || '?').charAt(0), { ...TEXT.name, fontSize: `${Math.round(size * 0.4)}px` }).setOrigin(0.5),
        ];
    }

    // ------------------------------------------------------------------ paging
    pageCount() {
        const items = this.scene.registry.get('inventory')?.items || [];
        return Math.max(1, Math.ceil(items.length / PAGE_SIZE));
    }

    changePage(delta) {
        const next = Phaser.Math.Clamp(this.currentPage + delta, 0, this.pageCount() - 1);
        if (next === this.currentPage) return;
        this.currentPage = next;
        playMenuSound(this.scene, 'clickSound');
        this.updateInventoryDisplay();
    }

    updatePager(totalPages) {
        const many = totalPages > 1;
        this.pagerLabel.setVisible(many).setText(`${this.currentPage + 1} / ${totalPages}`);
        this.pagerPrev.setVisible(many).setAlpha(this.currentPage > 0 ? 1 : 0.35);
        this.pagerNext.setVisible(many).setAlpha(this.currentPage < totalPages - 1 ? 1 : 0.35);
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
        if (this.inventoryPanel) {
            this.inventoryPanel.setVisible(this.inventoryVisible);
        }
        if (this.inventoryVisible) {
            this.hoverItem = null;
            this.updateInventoryDisplay();
        }
        if (this.scene.events) {
            this.scene.events.emit('inventoryVisibilityChanged', this.inventoryVisible);
        }
    }

    updateInventoryDisplay() {
        if (!this.inventoryPanel) return;
        const items = this.scene.registry.get('inventory')?.items || [];
        if (this.selectedItem && !items.includes(this.selectedItem)) this.selectedItem = null;   // used up / sold

        for (const slot of this.inventorySlots) {
            slot.parts.forEach(p => p.destroy());
            slot.parts = [];
            slot.item = null;
            slot.itemIndex = -1;
        }
        this.emptyText.setVisible(items.length === 0);

        const view = this.getDisplayOrder(items);
        const totalPages = Math.max(1, Math.ceil(view.length / PAGE_SIZE));
        this.currentPage = Phaser.Math.Clamp(this.currentPage, 0, totalPages - 1);
        view.slice(this.currentPage * PAGE_SIZE, (this.currentPage + 1) * PAGE_SIZE).forEach(({ item, index }, i) => {
            const slot = this.inventorySlots[i];
            slot.item = item;
            slot.itemIndex = index;
            const parts = this.makeIcon(item, slot.x, slot.y, ICON);
            if ((item.quantity || 1) > 1) {
                parts.push(this.scene.add.text(slot.x + 34, slot.y + 34, `×${item.quantity}`, { ...TEXT.small, fontSize: '14px' }).setOrigin(1, 1));
            }
            if (item.usable) {                                        // a glowing spore: it can be used / played
                const playing = isRecording(item) && isRecordingPlaying(item.id);
                const dot = this.scene.add.image(slot.x - 28, slot.y + 28, 'menuSpore').setScale(S).setTint(playing ? 0xf0fff2 : 0x7fff8e);
                if (playing) this.scene.tweens.add({ targets: dot, alpha: 0.3, duration: 500, yoyo: true, repeat: -1 });
                parts.push(dot);
            }
            parts.forEach(p => this.inventoryPanel.add(p));
            slot.parts = parts;
        });
        this.inventorySlots.forEach(slot => this.drawSlot(slot));
        this.updatePager(totalPages);
        this.moneyText.setText(`${this.scene.moneySystem?.amount ?? 0}`);
        this.coin.setVisible(!!this.scene.moneySystem);
        this.moneyText.setVisible(!!this.scene.moneySystem);
        this.showDetails();
    }

    select(item) {
        this.selectedItem = item;
        this.inventorySlots.forEach(slot => this.drawSlot(slot));
        this.showDetails();
    }

    /** the card shows the hovered item, else the selected one, else a hint */
    showDetails() {
        if (!this.detailName) return;
        const item = this.hoverItem || this.selectedItem;
        this.detailIconParts?.forEach(p => p.destroy());
        this.detailIconParts = null;
        this.detailSocket.setFrame(item ? 1 : 0);
        this.detailHint.setVisible(!item);
        for (const t of [this.detailName, this.detailKind, this.detailDesc, this.detailQty]) t.setText('');
        this.useButton.img.setVisible(false);
        this.useButton.text.setVisible(false);
        if (!item) return;

        const parts = this.makeIcon(item, CARD_CX, CARD.y + 92, ICON * 2);
        parts.forEach(p => this.inventoryPanel.add(p));
        this.detailIconParts = parts;
        this.inventoryPanel.bringToTop(this.detailQty);
        if ((item.quantity || 1) > 1) this.detailQty.setText(`×${item.quantity}`);

        this.detailName.setText(L().itemName(item));
        let y = this.detailName.y + this.detailName.height + 2;
        const kindKey = `ui.inventory.types.${item.type}`, kind = item.type ? L().t(kindKey) : '';
        this.detailKind.setText(kind && kind !== kindKey ? kind : '').setY(y);
        if (this.detailKind.text) y += this.detailKind.height;
        const bottom = CARD.y + CARD.h - (item.usable ? 62 : 16);
        this.detailDesc.setY(y + 10).setFontSize(15).setText(L().itemDescription(item) || '');
        if (this.detailDesc.y + this.detailDesc.height > bottom) this.detailDesc.setFontSize(13);   // long lore texts step down

        if (item.usable) {
            const label = isRecording(item)
                ? (isRecordingPlaying(item.id) ? 'ui.inventory.stopItem' : 'ui.inventory.playItem')
                : 'ui.inventory.useItem';
            this.useButton.text.setText(L().t(label)).setVisible(true);
            this.useButton.img.setVisible(true).setFrame(0);
        }
    }

    /** use (or play / stop) the selected item */
    useSelected() {
        const item = this.selectedItem;
        if (!item?.usable) return;
        const index = (this.scene.registry.get('inventory')?.items || []).indexOf(item);
        if (index >= 0) this.useItem(index);
    }

    /** arrows move the selection over the whole (paged) list, Enter / Space use it, PgUp / PgDn flip pages */
    handleKey(event) {
        if (!this.inventoryVisible || this.scene.dialogVisible) return;
        const items = this.scene.registry.get('inventory')?.items || [];
        const view = this.getDisplayOrder(items).map(v => v.item);
        let i = view.indexOf(this.selectedItem);
        const move = { ArrowRight: 1, KeyD: 1, ArrowLeft: -1, KeyA: -1, ArrowDown: GRID_COLS, KeyS: GRID_COLS, ArrowUp: -GRID_COLS, KeyW: -GRID_COLS }[event.code];
        if (move !== undefined && view.length) {
            i = i < 0 ? this.currentPage * PAGE_SIZE : Phaser.Math.Clamp(i + move, 0, view.length - 1);
            this.hoverItem = null;
            this.currentPage = Math.floor(i / PAGE_SIZE);
            this.selectedItem = view[i];
            playMenuSound(this.scene, 'hoverSound', 0.4);
            this.updateInventoryDisplay();
        } else if (event.code === 'Enter' || event.code === 'NumpadEnter' || event.code === 'Space') {
            this.useSelected();
        } else if (event.code === 'PageDown') this.changePage(1);
        else if (event.code === 'PageUp') this.changePage(-1);
    }

    // ------------------------------------------------------------------ data (unchanged by the redesign)
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
        if (this.inventoryButton) {
            this.inventoryButton.destroy();
            this.inventoryButton = null;
        }
        if (this.inventoryPanel) {
            this.inventoryPanel.destroy();
            this.inventoryPanel = null;
        }
        this.inventorySlots = [];
        this.detailName = null;
        this.detailIconParts = null;
        if (this._onWheel && this.scene.input) {
            this.scene.input.off('wheel', this._onWheel);
            this._onWheel = null;
        }
        if (this._onKey && this.scene.input?.keyboard) {
            this.scene.input.keyboard.off('keydown', this._onKey);
            this._onKey = null;
        }
        if (this._onRecordingEnded && this.scene.events) {
            this.scene.events.off('recordingEnded', this._onRecordingEnded);
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
