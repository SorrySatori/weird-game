import LanguageSystem from '../LanguageSystem.js';
import { itemValue, isSellable } from '../../utils/itemValues.js';
import { itemIcon, openPaperScreen, closePaperScreen, refreshPaperScreen } from '../../ui/paperKit.js';
import { panelSet } from '../../ui/panelStyle.js';
import { SHOP_SCREENS } from '../../ui/panels/shopScreens.js';
import { playMenuSound } from '../../utils/menuKit.js';

/**
 * Shop System: a stall's stock, buying and selling, and its screen.
 *
 * The screen is ui/paperKit.js's gridScreen, in the style chosen in the Settings (as the inventory): a curiosity
 * cabinet with price tags on the compartments, or the merchant's wares on a green cloth with tags tied on. Buy / Sell
 * are tabs; the chosen piece's card / note shows its price and the Buy / Sell button (a price you can't pay is red),
 * your dinar at its foot. Hover previews a piece, a click picks it; arrows move the pick, Enter / Space buys or sells
 * it, Tab switches Buy / Sell, PgUp / PgDn turn pages.
 */
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

        this.isOpen = false;
        this.currentTab = 'buy';
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

    // ------------------------------------------------------------------ the screen
    /** the shop's screen in the panel set's look (ui/panels/shopScreens.js: a market stall, or a mail-order catalogue) */
    buildScreen(overlay) {
        return SHOP_SCREENS[panelSet()](overlay, this.screenCtx(overlay));
    }

    /** everything a shop screen reads and does (see ui/panels/shopScreens.js for the contract) */
    screenCtx(overlay) {
        const lang = LanguageSystem.getInstance();
        const iconKey = (it) => this.scene.inventorySystem?.iconKey?.(it)
            ?? ([it.texture, it.id].find(k => k && overlay.textures.exists(k)) || null);
        const label = (k) => this.t(`shop.${k}`, {}, k === 'buy' ? 'Buy' : 'Sell');
        return {
            scene: overlay, W: overlay.scale.width, H: overlay.scale.height, lang: lang.getLanguage(),
            t: (key, params = {}, fallback = '') => this.t(key, params, fallback),
            title: this.title(), shopKey: this.options.shopKey || null,
            tabs: [{ key: 'buy', label: label('buy') }, { key: 'sell', label: label('sell') }],
            tab: () => this.currentTab,
            setTab: (key) => { this.currentTab = key; },
            items: () => this.listedItems(),
            name: (it) => this.itemName(it),
            desc: (it) => this.itemDescription(it),
            kind: (it) => { const k = `ui.inventory.types.${it.type}`, v = it.type ? lang.t(k) : ''; return v && v !== k ? v : ''; },
            qty: (it) => it.quantity || 1,
            price: (it) => this.priceOf(it),
            canAfford: (it) => this.canAfford(this.priceOf(it)),
            actLabel: () => label(this.currentTab),
            act: (it) => { const p = this.priceOf(it); if (this.currentTab === 'buy') this.buyItem(it, p); else this.sellItem(it, p); },
            money: () => this.scene.getMoney?.() ?? 0,
            iconKey,
            icon: (it, x, y, k = 1) => itemIcon(overlay, iconKey(it), it, this.itemName(it), x, y, k),
            empty: () => (this.currentTab === 'buy' ? this.t('shop.noItems', {}, 'No items available') : this.t('shop.nothingToSell', {}, "You have nothing we'd buy.")),
            strings: {
                forSale: this.t('shop.forSale', {}, 'Items for Sale'), yourItems: this.t('shop.yourItems', {}, 'Your Items'),
                price: (price) => this.t('shop.price', { price }, `Price: ${price} dinar`),
                balance: (amount) => this.t('shop.balance', { amount }, `Dinar: ${amount}`),
                hint: this.t('ui.inventory.selectHint', {}, 'Point at an item, or click it to pick it.')
            },
            sound: (key, vol = 1) => playMenuSound(overlay, key, vol),
            close: () => this.close()
        };
    }

    /** redraw the open screen */
    refresh() { refreshPaperScreen(this); }

    // ------------------------------------------------------------------ trading
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
        this.refresh();
    }

    /** the dinar at the card's foot (scenes call this every frame while the shop is open) */
    updateMoneyDisplay() {
        refreshPaperScreen(this, 'footer');
    }

    // ------------------------------------------------------------------ open / close
    open() {
        if (this.isOpen) return;
        this.isOpen = true;
        this.currentTab = 'buy';
        openPaperScreen(this);
    }

    close() {
        if (!this.isOpen) return;
        this.isOpen = false;
        closePaperScreen(this);
    }

    /** paperKit: another panel took the screen over */
    paperClosed() { this.isOpen = false; }

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
        closePaperScreen(this);
        this.isOpen = false;
    }

    destroy() {
        this.shutdown();
    }
}
