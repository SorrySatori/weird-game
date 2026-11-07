/**
 * Money System for the game
 * Handles currency management, transactions, and UI display.
 *
 * The amount lives in the game registry ('money'): it carries from scene to scene, a save stores it
 * (SaveSystem.PERSISTED_REGISTRY_KEYS + saveData.money) and a new game clears it, so every new game starts with
 * STARTING_MONEY. (It used to live in localStorage, which outlived games and sessions: a new game started with
 * whatever the last one had left.)
 */
export const STARTING_MONEY = 50;
const LEGACY_STORAGE_KEY = 'playerMoney';

export default class MoneySystem {
    /** Localized money notification via the scene's t(); falls back to the plain string. */
    _msg(key, amount, fallback) {
        if (typeof this.scene?.t !== 'function') return fallback;
        const text = this.scene.t(`notifications.${key}`, { amount });
        return text === `notifications.${key}` ? fallback : text;
    }

    /**
     * Create a new money system
     * @param {Phaser.Scene} scene - The scene this system belongs to
     * @param {Object} options - Configuration options
     * @param {number} options.initialAmount - Starting money amount (default: 0)
     * @param {string} options.currencyName - Name of the currency (default: 'dinar')
     * @param {boolean} options.showUI - Whether to show the UI (default: true)
     * @param {Object} options.position - Position of the UI
     * @param {number} options.position.x - X position (default: 700)
     * @param {number} options.position.y - Y position (default: 50)
     */
    constructor(scene, options = {}) {
        this.scene = scene;
        
        // Set default options
        const defaultOptions = {
            initialAmount: 0,
            currencyName: 'dinar',
            showUI: true,
            position: {
                x: 700,
                y: 50
            },
        };
        
        // Merge default options with provided options
        this.options = { ...defaultOptions, ...options };
        
        // The game's current amount, or (a new game) the starting amount. (`??`, not `||`: 0 is an amount -- a broke
        // player used to get the starting money back on the next scene.)
        try { window.localStorage?.removeItem(LEGACY_STORAGE_KEY); } catch (e) { /* the old store, no longer used */ }
        this.amount = this.loadMoney() ?? this.options.initialAmount;
        
        // Create UI if enabled
        if (this.options.showUI) {
            this.createUI();
        }
        
        // Register this system with the scene for updates
        if (scene.sys && scene.sys.updateList) {
            scene.sys.updateList.add(this);
        }
        
        // Save initial state
        this.saveMoney();
        
        console.log(`Money system initialized with ${this.amount} ${this.options.currencyName}`);
    }
    
    /**
     * Create the money UI
     * @private
     */
    createUI() {
        // Create container for money display - position will be set by the inventory system
        this.container = this.scene.add.container(0, 0);
        this.container.setDepth(100); // Always on top
        this.container.setVisible(false); // Hide by default, inventory system will show it
        
        // Add background
        this.background = this.scene.add.rectangle(0, 0, 120, 40, 0x0f2315, 1);
        this.background.setStrokeStyle(2, 0x7fff8e, 0.5);
        this.container.add(this.background);
        
        // Add coin icon
        this.coinIcon = this.scene.add.text(-40, 0, '💰', { 
            fontSize: '24px'
        });
        this.coinIcon.setOrigin(0.5);
        this.container.add(this.coinIcon);
        
        // Add text display
        this.moneyText = this.scene.add.text(10, 0, `${this.amount}`, {
            fontFamily: 'Arial',
            fontSize: '18px',
            color: '#7fff8e',
            fontStyle: 'bold'
        });
        this.moneyText.setOrigin(0, 0.5);
        this.container.add(this.moneyText);
        
        // Update the display
        this.updateUI();
    }
    
    /**
     * Update the money UI
     * @private
     */
    updateUI() {
        if (!this.moneyText) return;
        
        // Update text
        this.moneyText.setText(`${this.amount}`);
        
        // Animate when money changes
        this.scene.tweens.add({
            targets: this.container,
            scaleX: 1.2,
            scaleY: 1.2,
            duration: 100,
            yoyo: true,
            ease: 'Sine.easeInOut'
        });
    }
    
    /**
     * Get the UI container for positioning by other systems
     * @returns {Phaser.GameObjects.Container} The money UI container
     */
    getUIContainer() {
        return this.container;
    }
    
    /**
     * Add money to the player's wallet
     * @param {number} amount - Amount to add
     * @param {boolean} showNotification - Whether to show a notification
     * @returns {number} New total amount
     */
    add(amount, showNotification = true) {
        if (amount <= 0) {
            console.warn('Cannot add negative or zero amount. Use subtract() instead.');
            return this.amount;
        }
        
        // Add the amount
        this.amount += amount;
        
        // Update UI
        this.updateUI();
        
        // Show notification if enabled
        if (showNotification && this.scene.showNotification) {
            this.scene.showNotification(this._msg('moneyGain', amount, `+${amount} ${this.options.currencyName}`));
        }
        
        // Save the new amount
        this.saveMoney();
        this.syncRegistryMoney();
        
        return this.amount;
    }
    
    /**
     * Subtract money from the player's wallet
     * @param {number} amount - Amount to subtract
     * @param {boolean} showNotification - Whether to show a notification
     * @returns {boolean} Whether the transaction was successful
     */
    subtract(amount, showNotification = true) {
        if (amount <= 0) {
            console.warn('Cannot subtract negative or zero amount. Use add() instead.');
            return false;
        }
        
        // Check if player has enough money
        if (this.amount < amount) {
            // Show notification if enabled
            if (showNotification && this.scene.showNotification) {
                this.scene.showNotification(this._msg('notEnoughMoney', amount, `Not enough ${this.options.currencyName}!`), 'error');
            }
            return false;
        }
        
        // Subtract the amount
        this.amount -= amount;
        
        // Update UI
        this.updateUI();
        
        // Show notification if enabled
        if (showNotification && this.scene.showNotification) {
            this.scene.showNotification(this._msg('moneyLoss', amount, `-${amount} ${this.options.currencyName}`));
        }
        
        // Save the new amount
        this.saveMoney();
        this.syncRegistryMoney();
        
        return true;
    }
    
    /**
     * Check if the player has enough money
     * @param {number} amount - Amount to check
     * @returns {boolean} Whether the player has enough money
     */
    hasEnough(amount) {
        return this.amount >= amount;
    }
    
    /**
     * Set the money amount directly
     * @param {number} amount - New amount
     * @param {boolean} showNotification - Whether to show a notification
     */
    set(amount, showNotification = false) {
        if (amount < 0) {
            console.warn('Cannot set negative amount.');
            return;
        }
        
        const difference = amount - this.amount;
        this.amount = amount;
        
        // Update UI
        this.updateUI();
        
        // Show notification if enabled
        if (showNotification && this.scene.showNotification) {
            if (difference > 0) {
                this.scene.showNotification(this._msg('moneyGain', difference, `+${difference} ${this.options.currencyName}`));
            } else if (difference < 0) {
                this.scene.showNotification(this._msg('moneyLoss', -difference, `${difference} ${this.options.currencyName}`));
            }
        }
        
        // Save the new amount
        this.saveMoney();
        this.syncRegistryMoney();
    }
    
    /**
     * Get the current money amount
     * @returns {number} Current money amount
     */
    get() {
        return this.amount;
    }
    
    /**
     * Store the amount in the game registry ('money')
     * @private
     */
    saveMoney() {
        this.scene?.registry?.set('money', this.amount);
    }

    /**
     * Keep loaded-save registry money in sync across scene transitions.
     * GameScene reapplies registry savedMoney on each scene create.
     * @private
     */
    syncRegistryMoney() {
        if (this.scene?.registry?.has('savedMoney')) {
            this.scene.registry.set('savedMoney', {
                amount: this.amount,
                currencyName: this.options.currencyName
            });
        }
    }
    
    /**
     * The game's current amount from the registry
     * @private
     * @returns {number|null} Loaded money amount or null if not found
     */
    loadMoney() {
        const v = this.scene?.registry?.get('money');
        return Number.isFinite(v) ? v : null;
    }
    
    /**
     * Forget the game's amount (the next MoneySystem starts with initialAmount)
     * @private
     */
    clearSavedMoney() {
        this.scene?.registry?.remove('money');
    }
    
    /**
     * Reset the money amount to the initial value
     * @param {boolean} showNotification - Whether to show a notification
     */
    reset(showNotification = false) {
        this.set(this.options.initialAmount, showNotification);
    }
    
    /**
     * Show or hide the money UI
     * @param {boolean} visible - Whether the UI should be visible
     */
    setVisible(visible) {
        if (this.container) {
            this.container.setVisible(visible);
        }
    }
    
    /**
     * Update method called by the scene
     */
    update() {
        // Nothing to update every frame currently
    }
    
    /**
     * Clean up resources when the scene is shut down
     */
    shutdown() {
        // Save the current amount
        this.saveMoney();
        
        // Remove from update list
        if (this.scene.sys && this.scene.sys.updateList) {
            this.scene.sys.updateList.remove(this);
        }
        
        // Destroy UI elements
        if (this.container) {
            this.container.destroy();
            this.container = null;
        }
    }
    
    /**
     * Destroy this system
     */
    destroy() {
        this.shutdown();
    }
    
    /**
     * Set the amount directly (used when loading saved games)
     * @param {number} amount - The amount to set
     */
    setAmount(amount) {
        if (amount < 0) {
            console.warn('Cannot set negative amount.');
            return;
        }
        
        this.amount = amount;
        
        // Update UI if it exists
        if (this.moneyText) {
            this.updateUI();
        }

        this.saveMoney();
        this.syncRegistryMoney();
    }
    
    /**
     * Get the currency name
     * @returns {string} The currency name
     */
    getCurrencyName() {
        return this.options.currencyName;
    }
}
