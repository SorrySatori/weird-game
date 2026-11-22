import LanguageSystem from '../LanguageSystem.js';
import { itemValue, isSellable } from '../../utils/itemValues.js';
import { createMenuPanel, addPanelClose, createMenuIconButton, playMenuSound, MENU_COLORS, MENU_FONT } from '../../utils/menuKit.js';

/**
 * Shop System: a stall's stock, buying and selling, and its panel.
 *
 * The panel is the menu kit's 'ledger' frame (as the journal, the quest log and the inventory): the shop's name on the
 * title plate, Buy / Sell tab plaques, a grid of bronze item sockets with each piece's icon and price under it (pages
 * flip with the round arrows, the mouse wheel or PgUp / PgDn), the chosen piece's card on the right (big icon, name,
 * kind, description, the price, the Buy / Sell plaque) and your dinar underneath. Hover previews a piece, a click picks
 * it; arrows move the pick, Enter / Space buys or sells it, Tab switches Buy / Sell.
 */
const S = 2;                                   // pixel-art scale of the kit
const COLS = 6;
const ROWS = 3;
const PAGE_SIZE = COLS * ROWS;
const SLOT = 80;                               // menu_islot 40×40 at 2×
const SLOT_GAP = 8;
const ROW_PITCH = SLOT + 32;                   // a socket + its price line
const GRID = { left: -432, top: -168 };        // relative to the panel centre
const GRID_W = COLS * SLOT + (COLS - 1) * SLOT_GAP;
const GRID_CX = GRID.left + GRID_W / 2;
const ICON = 60;                               // item icons are drawn 60×60 (utils/itemIcons.js)
const TAB_Y = -201;                            // as the ledger's tabs (ui/LedgerPanel.js)
const CARD = { x: 112, y: -204, w: 320, h: 416 };
const CARD_CX = CARD.x + CARD.w / 2;
const FOOT_Y = 190;                            // the pager + money row
const POOR = '#e0806a';                        // a price you can't pay
const TEXT = {
    name: { fontFamily: MENU_FONT, fontSize: '20px', fontStyle: 'bold', color: MENU_COLORS.title, stroke: MENU_COLORS.stroke, strokeThickness: 3, align: 'center' },
    kind: { fontFamily: MENU_FONT, fontSize: '14px', fontStyle: 'italic', color: MENU_COLORS.dim, align: 'center' },
    body: { fontFamily: MENU_FONT, fontSize: '15px', color: MENU_COLORS.text, lineSpacing: 4 },
    small: { fontFamily: MENU_FONT, fontSize: '15px', color: MENU_COLORS.text, stroke: MENU_COLORS.stroke, strokeThickness: 4 },
    price: { fontFamily: MENU_FONT, fontSize: '14px', color: MENU_COLORS.title, stroke: MENU_COLORS.stroke, strokeThickness: 3 },
};

export default class ShopSystem {
    /**
     * @param {Phaser.Scene} scene - The scene this system belongs to
     * @param {Object} options
     * @param {string} options.shopName - Name of the shop (English fallback; options.shopKey → shop.names.<key>)
     * @param {Array} options.inventory - Items for sale
     * @param {number} options.buyMultiplier - Price multiplier when buying (default 1.0)
     * @param {number} options.sellMultiplier - Price multiplier when selling (default 0.5)
     * @param {Function} [options.onBuy] - called with the item after a purchase went through
     * (options.position / width / height are accepted for old callers; the panel is always centred.)
     */
    constructor(scene, options = {}) {
        this.scene = scene;
        this.options = { shopName: 'Shop', inventory: [], buyMultiplier: 1.0, sellMultiplier: 0.5, ...options };

        // One-off items the player already bought from this shop are gone for good (registry `shopSoldOut`,
        // persisted in saves); stackable goods restock.
        this.inventory = this.options.inventory.filter(item => !this.isSoldOut(item.id));

        this.container = null;
        this.isOpen = false;
        this.currentTab = 'buy';
        this.page = 0;
        this.selectedItem = null;
        this.hoverItem = null;
        this.slots = [];

        this.createShopUI();
    }

    // ---- i18n helpers: everything shown to the player goes through the scene's t(); the English
    // strings on the items / options stay as fallbacks so a missing key never blanks the UI.
    t(key, params = {}, fallback = '') {
        if (typeof this.scene?.t !== 'function') return fallback;
        const v = this.scene.t(key, params);
        return (v === key || v === undefined || typeof v !== 'string') ? fallback : v;
    }
    title() { return this.options.shopKey ? this.t(`shop.names.${this.options.shopKey}`, {}, this.options.shopName) : this.options.shopName; }

    // ---- one-off stock -------------------------------------------------------------------------
    // Shops sell unique pieces: a bought item leaves the stall and stays gone across scene visits and
    // save/load. Opt out per item with `stackable: true` (consumables like Oltrac) or `restock: true`.
    stockKey() { return this.options.shopKey || this.options.shopName; }
    isOneOff(item) { return !item.stackable && item.restock !== true; }
    soldOutIds() {
        const all = this.scene.registry.get('shopSoldOut') || {};
        return all[this.stockKey()] || [];
    }
    isSoldOut(itemId) { return this.soldOutIds().includes(itemId); }
    setSoldOut(itemId, soldOut) {
        const all = { ...(this.scene.registry.get('shopSoldOut') || {}) };
        const ids = new Set(all[this.stockKey()] || []);
        if (soldOut) ids.add(itemId); else ids.delete(itemId);
        all[this.stockKey()] = Array.from(ids);
        this.scene.registry.set('shopSoldOut', all);
    }
    itemName(item) { return LanguageSystem.getInstance().itemName(item); }
    itemDescription(item) { return LanguageSystem.getInstance().itemDescription(item) || this.t('shop.noDescription', {}, 'No description available.'); }

    // ---- what the current tab lists, and at what price ------------------------------------------
    /** buy: the priced stock; sell: what a shop will take (worth something, not a quest item -- utils/itemValues.js) */
    listedItems() {
        return this.currentTab === 'buy'
            ? this.inventory.filter(item => item.price)
            : (this.scene.inventorySystem?.getItems() || []).filter(isSellable);
    }
    priceOf(item) {
        return this.currentTab === 'buy'
            ? Math.round(item.price * this.options.buyMultiplier)
            : Math.max(1, Math.round(itemValue(item) * this.options.sellMultiplier));
    }
    canAfford(price) { return this.currentTab === 'sell' || this.scene.hasEnoughMoney?.(price) !== false; }
    pageCount() { return Math.max(1, Math.ceil(this.listedItems().length / PAGE_SIZE)); }

    /** the icon (or a lettered enamel disc) the inventory would show for this item */
    makeIcon(item, x, y, size) {
        const inv = this.scene.inventorySystem;
        if (inv?.makeIcon) return inv.makeIcon(item, x, y, size);
        return [this.scene.add.text(x, y, (this.itemName(item) || '?').charAt(0), { ...TEXT.name, fontSize: `${Math.round(size * 0.4)}px` }).setOrigin(0.5)];
    }

    // ------------------------------------------------------------------ the panel
    createShopUI() {
        const sc = this.scene;
        const panel = createMenuPanel(sc, 'ledger', sc.scale.width / 2, 300, this.title());
        // the shop's name on the title plate (150 native px): shrink a long one until it fits
        for (let size = 17; panel.title.width > 286 && size > 12; size--) panel.title.setFontSize(size);
        this.container = panel.container.setDepth(1003).setScrollFactor(0, 0, true).setVisible(false);
        addPanelClose(sc, panel, () => this.close());
        const add = (o) => { this.container.add(o); return o; };

        // Buy / Sell plaques over the grid
        this.tabs = ['buy', 'sell'].map((tab, i) => {
            const x = GRID_CX + (i ? 74 : -74);
            const img = add(sc.add.image(x, TAB_Y, 'menuTab', 0).setScale(S).setInteractive({ useHandCursor: true }));
            img.input.hitArea.setTo(1, 1, 66, 18);
            const text = add(sc.add.text(x, TAB_Y, this.t(`shop.${tab}`, {}, tab === 'buy' ? 'Buy' : 'Sell'), {
                fontFamily: MENU_FONT, fontSize: '16px', color: MENU_COLORS.text, stroke: MENU_COLORS.stroke, strokeThickness: 3,
            }).setOrigin(0.5));
            const t = { tab, img, text, hover: false };
            img.on('pointerover', () => { t.hover = true; this.drawTabs(); playMenuSound(sc, 'hoverSound', 0.5); });
            img.on('pointerout', () => { t.hover = false; this.drawTabs(); });
            img.on('pointerdown', (pointer, lx, ly, event) => {
                event?.stopPropagation();
                if (this.currentTab === tab) return;
                playMenuSound(sc, 'clickSound');
                this.setTab(tab);
            });
            return t;
        });

        // the sockets: one page, re-filled per page
        this.slots = [];
        for (let row = 0; row < ROWS; row++) {
            for (let col = 0; col < COLS; col++) {
                const x = GRID.left + SLOT / 2 + col * (SLOT + SLOT_GAP);
                const y = GRID.top + SLOT / 2 + row * ROW_PITCH;
                const bg = add(sc.add.image(x, y, 'menuItemSlot', 0).setScale(S).setInteractive({ useHandCursor: true }));
                bg.input.hitArea.setTo(1, 1, 38, 38);
                const slot = { bg, x, y, item: null, parts: [], hover: false };
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
                this.slots.push(slot);
            }
        }
        this.emptyText = add(sc.add.text(GRID_CX, GRID.top + ROW_PITCH * 1.2, '', {
            ...TEXT.body, fontSize: '18px', fontStyle: 'italic', color: MENU_COLORS.dim, align: 'center', wordWrap: { width: GRID_W - 60 },
        }).setOrigin(0.5));

        // the chosen piece's card
        add(sc.add.nineslice(CARD.x, CARD.y, 'menuCard', 0, CARD.w / S, CARD.h / S, 7, 7, 7, 7).setOrigin(0, 0).setScale(S));
        this.detailSocket = add(sc.add.image(CARD_CX, CARD.y + 92, 'menuItemSlot', 1).setScale(4));
        this.detailName = add(sc.add.text(CARD_CX, CARD.y + 184, '', { ...TEXT.name, wordWrap: { width: CARD.w - 36 } }).setOrigin(0.5, 0));
        this.detailKind = add(sc.add.text(CARD_CX, 0, '', TEXT.kind).setOrigin(0.5, 0));
        this.detailDesc = add(sc.add.text(CARD.x + 18, 0, '', { ...TEXT.body, wordWrap: { width: CARD.w - 36 } }));
        this.detailHint = add(sc.add.text(CARD_CX, CARD.y + 184, this.t('ui.inventory.selectHint', {}, 'Point at an item, or click it to pick it.'), {
            ...TEXT.kind, fontSize: '15px', wordWrap: { width: CARD.w - 40 },
        }).setOrigin(0.5, 0));
        const priceY = CARD.y + CARD.h - 74;
        this.detailCoin = add(sc.add.image(CARD_CX, priceY, 'menuCoin').setScale(S));
        this.detailPrice = add(sc.add.text(CARD_CX, priceY, '', { ...TEXT.small, fontSize: '20px', color: MENU_COLORS.title }).setOrigin(0, 0.5));
        this.createActionButton(add);

        // the pager + the money
        this.pagerPrev = add(createMenuIconButton(sc, GRID_CX - 74, FOOT_Y, 'left', () => this.changePage(-1)));
        this.pagerNext = add(createMenuIconButton(sc, GRID_CX + 74, FOOT_Y, 'right', () => this.changePage(1)));
        this.pagerLabel = add(sc.add.text(GRID_CX, FOOT_Y, '', TEXT.small).setOrigin(0.5));
        add(sc.add.image(GRID.left + 14, FOOT_Y, 'menuCoin').setScale(S));
        this.moneyText = add(sc.add.text(GRID.left + 34, FOOT_Y, '', { ...TEXT.small, fontSize: '17px', color: MENU_COLORS.title }).setOrigin(0, 0.5));

        // the mouse wheel flips pages; keys move the pick, buy / sell, switch tabs (only while open)
        this._onWheel = (pointer, over, dx, dy) => {
            if (!this.isOpen) return;
            if (dy > 0) this.changePage(1); else if (dy < 0) this.changePage(-1);
        };
        sc.input.on('wheel', this._onWheel);
        this._onKey = (event) => this.handleKey(event);
        sc.input.keyboard?.on('keydown', this._onKey);
        sc.events.once('shutdown', () => this.shutdown());

        this.drawTabs();
        this.refresh();
    }

    /** the Buy / Sell plaque on the card (idle / hover / pressed); dimmed when you can't pay */
    createActionButton(add) {
        const sc = this.scene, y = CARD.y + CARD.h - 34;
        const img = add(sc.add.image(CARD_CX, y, 'menuTab', 0).setScale(S).setInteractive({ useHandCursor: true }));
        img.input.hitArea.setTo(1, 1, 66, 18);
        const text = add(sc.add.text(CARD_CX, y + 1, '', { ...TEXT.small, fontSize: '16px', strokeThickness: 3 }).setOrigin(0.5));
        const btn = { img, text, enabled: true };
        img.on('pointerover', () => { img.setFrame(1); text.setColor(btn.enabled ? MENU_COLORS.textHover : MENU_COLORS.textDisabled); playMenuSound(sc, 'hoverSound', 0.5); });
        img.on('pointerout', () => { img.setFrame(0); text.setColor(btn.enabled ? MENU_COLORS.text : MENU_COLORS.textDisabled); });
        img.on('pointerdown', (pointer, lx, ly, event) => {
            event?.stopPropagation();
            img.setFrame(2); text.y = y - 1;
            playMenuSound(sc, 'clickSound');
            sc.time.delayedCall(110, () => {
                if (!img.active) return;
                img.setFrame(1); text.y = y + 1;
                this.actOnSelected();
            });
        });
        this.actionButton = btn;
    }

    drawTabs() {
        this.tabs?.forEach(t => {
            const sel = t.tab === this.currentTab;
            t.img.setFrame(sel ? 2 : t.hover ? 1 : 0);
            t.text.y = TAB_Y + (sel ? -1 : 1);
            t.text.setColor(sel || t.hover ? MENU_COLORS.textHover : MENU_COLORS.text);
            t.text.setShadow(0, 0, '#7fff8e', sel ? 6 : 0, false, true);
        });
    }

    drawSlot(slot) {
        const selected = slot.item && slot.item === this.selectedItem;
        slot.bg.setFrame(selected ? 3 : slot.hover && slot.item ? 2 : slot.item ? 1 : 0);
    }

    /** fill the sockets with the current page, then the card, the pager and the money */
    refresh() {
        const items = this.listedItems();
        const pages = Math.max(1, Math.ceil(items.length / PAGE_SIZE));
        this.page = Phaser.Math.Clamp(this.page, 0, pages - 1);
        if (this.selectedItem && !items.includes(this.selectedItem)) this.selectedItem = null;
        if (this.hoverItem && !items.includes(this.hoverItem)) this.hoverItem = null;
        const view = items.slice(this.page * PAGE_SIZE, (this.page + 1) * PAGE_SIZE);
        this.slots.forEach((slot, i) => {
            slot.parts.forEach(p => p.destroy());
            slot.parts = [];
            slot.item = view[i] || null;
            if (slot.item) {
                const item = slot.item, price = this.priceOf(item);
                slot.parts.push(...this.makeIcon(item, slot.x, slot.y, ICON));
                if ((item.quantity || 1) > 1) {
                    slot.parts.push(this.scene.add.text(slot.x + 34, slot.y + 34, `×${item.quantity}`, { ...TEXT.small, fontSize: '13px' }).setOrigin(1, 1));
                }
                const txt = this.scene.add.text(0, slot.y + SLOT / 2 + 12, `${price}`, { ...TEXT.price, color: this.canAfford(price) ? MENU_COLORS.title : POOR }).setOrigin(0, 0.5);
                const coin = this.scene.add.image(0, slot.y + SLOT / 2 + 12, 'menuCoin');
                const w = coin.width + 4 + txt.width;                                  // coin + number, centred under the socket
                coin.setX(slot.x - w / 2 + coin.width / 2); txt.setX(slot.x - w / 2 + coin.width + 4);
                slot.parts.push(coin, txt);
                slot.parts.forEach(p => this.container.add(p));
            }
            this.drawSlot(slot);
        });
        this.slots.forEach(slot => slot.bg.setAlpha(items.length ? 1 : 0.35));          // an empty list: the message reads over dim sockets
        this.emptyText.setVisible(!items.length).setText(this.currentTab === 'buy'
            ? this.t('shop.noItems', {}, 'No items available')
            : this.t('shop.nothingToSell', {}, "You have nothing we'd buy."));
        const many = pages > 1;
        this.pagerLabel.setVisible(many).setText(`${this.page + 1} / ${pages}`);
        this.pagerPrev.setVisible(many).setAlpha(this.page > 0 ? 1 : 0.35);
        this.pagerNext.setVisible(many).setAlpha(this.page < pages - 1 ? 1 : 0.35);
        this.updateMoneyDisplay();
        this.showDetails();
    }

    select(item) {
        this.selectedItem = item;
        this.slots.forEach(slot => this.drawSlot(slot));
        this.showDetails();
    }

    /** the card shows the hovered piece, else the picked one, else a hint */
    showDetails() {
        if (!this.detailName) return;
        const item = this.hoverItem || this.selectedItem;
        this.detailIconParts?.forEach(p => p.destroy());
        this.detailIconParts = null;
        this.detailSocket.setFrame(item ? 1 : 0);
        this.detailHint.setVisible(!item);
        for (const t of [this.detailName, this.detailKind, this.detailDesc, this.detailPrice]) t.setText('');
        this.detailCoin.setVisible(!!item);
        this.actionButton.img.setVisible(!!item);
        this.actionButton.text.setVisible(!!item);
        if (!item) return;

        const parts = this.makeIcon(item, CARD_CX, CARD.y + 92, ICON * 2);
        parts.forEach(p => this.container.add(p));
        this.detailIconParts = parts;

        const L = LanguageSystem.getInstance();
        this.detailName.setText(this.itemName(item));
        let y = this.detailName.y + this.detailName.height + 2;
        const kindKey = `ui.inventory.types.${item.type}`, kind = item.type ? L.t(kindKey) : '';
        this.detailKind.setText(kind && kind !== kindKey ? kind : '').setY(y);
        if (this.detailKind.text) y += this.detailKind.height;
        const bottom = CARD.y + CARD.h - 96;
        this.detailDesc.setY(y + 10).setFontSize(15).setText(this.itemDescription(item));
        if (this.detailDesc.y + this.detailDesc.height > bottom) this.detailDesc.setFontSize(13);   // long lore texts step down

        // the price: a coin and the sum, centred; red when you can't pay
        const price = this.priceOf(item), ok = this.canAfford(price);
        this.detailPrice.setText(`${price}`).setColor(ok ? MENU_COLORS.title : POOR);
        const w = 24 + 8 + this.detailPrice.width;
        this.detailCoin.setX(CARD_CX - w / 2 + 12);
        this.detailPrice.setX(CARD_CX - w / 2 + 32);

        const btn = this.actionButton;
        btn.enabled = ok;
        btn.text.setText(this.t(`shop.${this.currentTab}`, {}, this.currentTab === 'buy' ? 'Buy' : 'Sell'))
            .setColor(ok ? MENU_COLORS.text : MENU_COLORS.textDisabled);
        btn.img.setFrame(0);
    }

    /** buy or sell the picked piece (an unaffordable one explains itself) */
    actOnSelected() {
        const item = this.selectedItem || this.hoverItem;
        if (!item) return;
        const price = this.priceOf(item);
        if (this.currentTab === 'buy') this.buyItem(item, price); else this.sellItem(item, price);
    }

    /**
     * Switch between the buy and sell tabs
     * @param {string} tab - 'buy' or 'sell'
     */
    setTab(tab) {
        if (tab === this.currentTab) return;
        this.currentTab = tab;
        this.page = 0;
        this.selectedItem = null;
        this.hoverItem = null;
        this.drawTabs();
        this.refresh();
    }

    changePage(delta) {
        const next = Phaser.Math.Clamp(this.page + delta, 0, this.pageCount() - 1);
        if (next === this.page) return;
        this.page = next;
        this.hoverItem = null;
        playMenuSound(this.scene, 'clickSound');
        this.refresh();
    }

    /** arrows move the pick over the whole (paged) list, Enter / Space act on it, PgUp / PgDn flip pages, Tab switches */
    handleKey(event) {
        if (!this.isOpen || this.scene.dialogVisible || this.scene.gameMenu?.visible) return;
        if (event.code === 'Tab') {
            event.preventDefault?.();
            playMenuSound(this.scene, 'clickSound');
            this.setTab(this.currentTab === 'buy' ? 'sell' : 'buy');
            return;
        }
        const items = this.listedItems();
        const move = { ArrowRight: 1, KeyD: 1, ArrowLeft: -1, KeyA: -1, ArrowDown: COLS, KeyS: COLS, ArrowUp: -COLS, KeyW: -COLS }[event.code];
        if (move !== undefined && items.length) {
            let i = items.indexOf(this.selectedItem);
            i = i < 0 ? this.page * PAGE_SIZE : Phaser.Math.Clamp(i + move, 0, items.length - 1);
            this.hoverItem = null;
            this.page = Math.floor(i / PAGE_SIZE);
            this.selectedItem = items[i];
            playMenuSound(this.scene, 'hoverSound', 0.4);
            this.refresh();
        } else if (event.code === 'Enter' || event.code === 'NumpadEnter' || event.code === 'Space') {
            this.actOnSelected();
        } else if (event.code === 'PageDown') this.changePage(1);
        else if (event.code === 'PageUp') this.changePage(-1);
    }

    // ------------------------------------------------------------------ trading (unchanged by the redesign)
    /**
     * Buy an item from the shop
     * @param {Object} item - The item to buy
     * @param {number} price - The price of the item
     */
    buyItem(item, price) {
        // Check if player has enough money
        if (!this.scene.hasEnoughMoney(price)) {
            this.scene.showNotification(this.t('notifications.notEnoughMoney', {}, 'Not enough dinar!'), 'error');
            return;
        }

        // A non-stackable item can only be carried once — don't take the money for a duplicate
        if (!item.stackable && typeof this.scene.hasItem === 'function' && this.scene.hasItem(item.id)) {
            this.scene.showNotification(this.t('notifications.alreadyOwned', {}, 'You already have one of those.'), 'error');
            return;
        }

        this.scene.subtractMoney(price);
        this.scene.addItemToInventory({ ...item });

        // A unique piece leaves the stall for good
        if (this.isOneOff(item)) {
            this.setSoldOut(item.id, true);
            this.inventory = this.inventory.filter(i => i.id !== item.id);
        }

        this.scene.showNotification(this.t('notifications.purchased', { item: this.itemName(item) }, `Purchased: ${this.itemName(item)}`));
        this.options.onBuy?.(item);
        if (this.selectedItem === item && this.isOneOff(item)) this.selectedItem = null;
        if (this.hoverItem === item && this.isOneOff(item)) this.hoverItem = null;
        this.refresh();
    }

    /**
     * Sell an item to the shop
     * @param {Object} item - The item to sell
     * @param {number} price - The price of the item
     */
    sellItem(item, price) {
        if (!this.scene.removeItemFromInventory(item.id)) {
            this.scene.showNotification(this.t('notifications.failedToSell', {}, 'Failed to sell item'), 'error');
            return;
        }

        this.scene.addMoney(price);

        // Selling a one-off piece back to the shop that stocked it puts it back on the stall
        const template = this.options.inventory.find(i => i.id === item.id);
        if (template && this.isOneOff(template) && this.isSoldOut(item.id)) {
            this.setSoldOut(item.id, false);
            if (!this.inventory.some(i => i.id === item.id)) this.inventory.push(template);
        }

        this.scene.showNotification(this.t('notifications.sold', { item: this.itemName(item) }, `Sold: ${this.itemName(item)}`), '', this.t('notifications.moneyGain', { amount: price }, `+${price} dinar`));
        this.selectedItem = null;
        this.hoverItem = null;
        this.refresh();
    }

    /** the dinar under the grid (scenes call this every frame while the shop is open) */
    updateMoneyDisplay() {
        if (this.moneyText?.active) this.moneyText.setText(`${this.scene.getMoney?.() ?? 0}`);
    }

    // ------------------------------------------------------------------ open / close
    open() {
        if (this.isOpen || !this.container) return;
        this.isOpen = true;
        this.selectedItem = null;
        this.hoverItem = null;
        this.container.setVisible(true).setAlpha(0);
        this.refresh();
        this.scene.tweens.add({ targets: this.container, alpha: 1, duration: 160, ease: 'Sine.easeOut' });   // a fade: pixel art isn't scaled
    }

    close() {
        if (!this.isOpen || !this.container) return;
        this.scene.tweens.add({
            targets: this.container, alpha: 0, duration: 140, ease: 'Sine.easeIn',
            onComplete: () => { this.isOpen = false; this.container?.setVisible(false); },
        });
    }

    toggle() {
        if (this.isOpen) this.close(); else this.open();
    }

    // ------------------------------------------------------------------ stock changes
    /** @param {Object} item - The item to add */
    addItem(item) {
        if (!item.price) console.warn('Item added to shop has no price:', item.name);
        this.inventory.push(item);
        if (this.isOpen && this.currentTab === 'buy') this.refresh();
    }

    /**
     * @param {string} itemId - The ID of the item to remove
     * @returns {boolean} Whether the item was removed
     */
    removeItem(itemId) {
        const index = this.inventory.findIndex(item => item.id === itemId);
        if (index === -1) return false;
        this.inventory.splice(index, 1);
        if (this.isOpen && this.currentTab === 'buy') this.refresh();
        return true;
    }

    /** @param {Array} items - The new stock */
    setInventory(items) {
        this.inventory = items;
        if (this.isOpen && this.currentTab === 'buy') this.refresh();
    }

    /** Clean up when the scene shuts down (scene instances are re-used) */
    shutdown() {
        if (this._onWheel) { this.scene.input?.off('wheel', this._onWheel); this._onWheel = null; }
        if (this._onKey) { this.scene.input?.keyboard?.off('keydown', this._onKey); this._onKey = null; }
        if (this.container) {
            this.container.destroy();
            this.container = null;
        }
        this.isOpen = false;
    }

    destroy() {
        this.shutdown();
    }
}
