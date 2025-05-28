/**
 * Shop System for the game
 * Handles item purchases, selling, and shop UI
 */
export default class ShopSystem {
    /**
     * Create a new shop system
     * @param {Phaser.Scene} scene - The scene this system belongs to
     * @param {Object} options - Configuration options
     * @param {string} options.shopName - Name of the shop
     * @param {Array} options.inventory - Array of items available in the shop
     * @param {Object} options.position - Position of the shop UI
     * @param {number} options.position.x - X position
     * @param {number} options.position.y - Y position
     * @param {number} options.buyMultiplier - Price multiplier when buying (default: 1.0)
     * @param {number} options.sellMultiplier - Price multiplier when selling (default: 0.5)
     */
    constructor(scene, options = {}) {
        this.scene = scene;
        
        // Set default options
        const defaultOptions = {
            shopName: 'Shop',
            inventory: [],
            position: {
                x: 400,
                y: 300
            },
            buyMultiplier: 1.0,
            sellMultiplier: 0.5,
            width: 600,
            height: 400
        };
        
        // Merge default options with provided options
        this.options = { ...defaultOptions, ...options };
        
        // Initialize shop inventory
        this.inventory = this.options.inventory;
        
        // Create UI elements
        this.container = null;
        this.isOpen = false;
        this.selectedItem = null;
        this.itemButtons = [];
        this.currentTab = 'buy';
        
        // Create the shop UI
        this.createShopUI();
        
        console.log(`Shop system initialized: ${this.options.shopName}`);
    }
    
    /**
     * Create the shop UI
     * @private
     */
    createShopUI() {
        // Create main container for the shop
        this.container = this.scene.add.container(this.options.position.x, this.options.position.y);
        this.container.setDepth(100);
        this.container.setVisible(false);
        
        // Add background
        const bg = this.scene.add.rectangle(
            0, 
            0, 
            this.options.width, 
            this.options.height, 
            0x000000, 
            0.9
        );
        bg.setStrokeStyle(2, 0xFFD700);
        this.container.add(bg);
        
        // Add shop title
        const title = this.scene.add.text(
            0, 
            -this.options.height/2 + 25, 
            this.options.shopName, 
            {
                fontFamily: 'Arial',
                fontSize: '24px',
                color: '#FFD700',
                fontStyle: 'bold'
            }
        );
        title.setOrigin(0.5);
        this.container.add(title);
        
        // Add close button
        const closeButton = this.scene.add.text(
            this.options.width/2 - 30, 
            -this.options.height/2 + 25, 
            'X', 
            {
                fontFamily: 'Arial',
                fontSize: '24px',
                color: '#FF0000',
                fontStyle: 'bold'
            }
        );
        closeButton.setOrigin(0.5);
        closeButton.setInteractive({ useHandCursor: true });
        closeButton.on('pointerdown', () => this.close());
        this.container.add(closeButton);
        
        // Add tabs for buy/sell
        this.createTabs();
        
        // Add item list container
        this.itemListContainer = this.scene.add.container(0, 0);
        this.container.add(this.itemListContainer);
        
        // Add item details container
        this.itemDetailsContainer = this.scene.add.container(
            this.options.width/4, 
            0
        );
        this.container.add(this.itemDetailsContainer);
        
        // Add player money display
        this.moneyText = this.scene.add.text(
            -this.options.width/2 + 20, 
            -this.options.height/2 + 25, 
            `Gold: ${this.scene.getMoney()}`, 
            {
                fontFamily: 'Arial',
                fontSize: '18px',
                color: '#FFD700'
            }
        );
        this.container.add(this.moneyText);
        
        // Create the initial item list
        this.showItemList();
    }
    
    /**
     * Create tabs for buy/sell modes
     * @private
     */
    createTabs() {
        const tabY = -this.options.height/2 + 70;
        const tabWidth = 100;
        const tabHeight = 40;
        const tabSpacing = 10;
        
        // Buy tab
        this.buyTab = this.scene.add.container(-tabWidth - tabSpacing/2, tabY);
        const buyBg = this.scene.add.rectangle(0, 0, tabWidth, tabHeight, 0x333333, 0.9);
        buyBg.setStrokeStyle(2, 0xFFD700);
        this.buyTab.add(buyBg);
        
        const buyText = this.scene.add.text(0, 0, 'Buy', {
            fontFamily: 'Arial',
            fontSize: '18px',
            color: '#FFFFFF'
        });
        buyText.setOrigin(0.5);
        this.buyTab.add(buyText);
        
        this.buyTab.setInteractive(new Phaser.Geom.Rectangle(-tabWidth/2, -tabHeight/2, tabWidth, tabHeight), Phaser.Geom.Rectangle.Contains);
        this.buyTab.on('pointerdown', () => this.setTab('buy'));
        
        // Sell tab
        this.sellTab = this.scene.add.container(tabSpacing/2, tabY);
        const sellBg = this.scene.add.rectangle(0, 0, tabWidth, tabHeight, 0x333333, 0.9);
        sellBg.setStrokeStyle(2, 0x888888);
        this.sellTab.add(sellBg);
        
        const sellText = this.scene.add.text(0, 0, 'Sell', {
            fontFamily: 'Arial',
            fontSize: '18px',
            color: '#FFFFFF'
        });
        sellText.setOrigin(0.5);
        this.sellTab.add(sellText);
        
        this.sellTab.setInteractive(new Phaser.Geom.Rectangle(-tabWidth/2, -tabHeight/2, tabWidth, tabHeight), Phaser.Geom.Rectangle.Contains);
        this.sellTab.on('pointerdown', () => this.setTab('sell'));
        
        this.container.add([this.buyTab, this.sellTab]);
    }
    
    /**
     * Switch between buy and sell tabs
     * @param {string} tab - Tab to switch to ('buy' or 'sell')
     */
    setTab(tab) {
        if (tab === this.currentTab) return;
        
        this.currentTab = tab;
        
        // Update tab appearance
        if (tab === 'buy') {
            this.buyTab.getAt(0).setStrokeStyle(2, 0xFFD700);
            this.sellTab.getAt(0).setStrokeStyle(2, 0x888888);
        } else {
            this.buyTab.getAt(0).setStrokeStyle(2, 0x888888);
            this.sellTab.getAt(0).setStrokeStyle(2, 0xFFD700);
        }
        
        // Update item list
        this.showItemList();
        
        // Clear item details
        this.clearItemDetails();
    }
    
    /**
     * Show the list of items based on current tab
     * @private
     */
    showItemList() {
        // Clear existing items
        this.itemListContainer.removeAll(true);
        this.itemButtons = [];
        
        // Create list background
        const listBg = this.scene.add.rectangle(
            -this.options.width/4, 
            0, 
            this.options.width/2 - 20, 
            this.options.height - 120, 
            0x222222, 
            0.8
        );
        this.itemListContainer.add(listBg);
        
        // Get items based on current tab
        const items = this.currentTab === 'buy' 
            ? this.inventory 
            : this.scene.inventorySystem.getItems();
        
        // Create item list title
        const listTitle = this.scene.add.text(
            -this.options.width/4, 
            -this.options.height/2 + 100, 
            this.currentTab === 'buy' ? 'Items for Sale' : 'Your Items', 
            {
                fontFamily: 'Arial',
                fontSize: '18px',
                color: '#FFFFFF',
                fontStyle: 'bold'
            }
        );
        listTitle.setOrigin(0.5);
        this.itemListContainer.add(listTitle);
        
        // Create scrollable item list
        const startY = -this.options.height/2 + 140;
        const itemHeight = 50;
        const itemWidth = this.options.width/2 - 40;
        
        items.forEach((item, index) => {
            // Skip items without a price in buy mode
            if (this.currentTab === 'buy' && !item.price) return;
            
            const y = startY + index * (itemHeight + 10);
            
            // Skip if item would be outside the visible area
            if (y > this.options.height/2 - 20) return;
            
            // Create item button
            const itemButton = this.scene.add.container(-this.options.width/4, y);
            
            // Button background
            const buttonBg = this.scene.add.rectangle(
                0, 
                0, 
                itemWidth, 
                itemHeight, 
                0x333333, 
                0.8
            );
            buttonBg.setStrokeStyle(1, 0x888888);
            itemButton.add(buttonBg);
            
            // Item name
            const nameText = this.scene.add.text(
                -itemWidth/2 + 10, 
                -10, 
                item.name, 
                {
                    fontFamily: 'Arial',
                    fontSize: '16px',
                    color: '#FFFFFF'
                }
            );
            itemButton.add(nameText);
            
            // Item price
            const price = this.currentTab === 'buy' 
                ? Math.round(item.price * this.options.buyMultiplier) 
                : Math.round((item.price || 0) * this.options.sellMultiplier);
            
            const priceText = this.scene.add.text(
                -itemWidth/2 + 10, 
                10, 
                `Price: ${price} gold`, 
                {
                    fontFamily: 'Arial',
                    fontSize: '14px',
                    color: '#FFD700'
                }
            );
            itemButton.add(priceText);
            
            // Make button interactive
            itemButton.setInteractive(new Phaser.Geom.Rectangle(-itemWidth/2, -itemHeight/2, itemWidth, itemHeight), Phaser.Geom.Rectangle.Contains);
            itemButton.on('pointerdown', () => this.selectItem(item, price));
            itemButton.on('pointerover', () => {
                buttonBg.setStrokeStyle(2, 0xFFD700);
            });
            itemButton.on('pointerout', () => {
                buttonBg.setStrokeStyle(1, 0x888888);
            });
            
            // Add to container and button list
            this.itemListContainer.add(itemButton);
            this.itemButtons.push(itemButton);
        });
        
        // Show "No items" message if list is empty
        if (items.length === 0 || (this.currentTab === 'buy' && this.itemButtons.length === 0)) {
            const noItemsText = this.scene.add.text(
                -this.options.width/4, 
                0, 
                'No items available', 
                {
                    fontFamily: 'Arial',
                    fontSize: '16px',
                    color: '#888888'
                }
            );
            noItemsText.setOrigin(0.5);
            this.itemListContainer.add(noItemsText);
        }
    }
    
    /**
     * Select an item to show details
     * @param {Object} item - The item to select
     * @param {number} price - The calculated price of the item
     * @private
     */
    selectItem(item, price) {
        this.selectedItem = item;
        this.selectedPrice = price;
        
        // Clear existing details
        this.clearItemDetails();
        
        // Create details background
        const detailsBg = this.scene.add.rectangle(
            0, 
            0, 
            this.options.width/2 - 20, 
            this.options.height - 120, 
            0x222222, 
            0.8
        );
        this.itemDetailsContainer.add(detailsBg);
        
        // Item name
        const nameText = this.scene.add.text(
            0, 
            -this.options.height/2 + 140, 
            item.name, 
            {
                fontFamily: 'Arial',
                fontSize: '20px',
                color: '#FFFFFF',
                fontStyle: 'bold'
            }
        );
        nameText.setOrigin(0.5);
        this.itemDetailsContainer.add(nameText);
        
        // Item description
        const descText = this.scene.add.text(
            0, 
            -this.options.height/2 + 180, 
            item.description || 'No description available.', 
            {
                fontFamily: 'Arial',
                fontSize: '16px',
                color: '#CCCCCC',
                wordWrap: { width: this.options.width/2 - 60 },
                align: 'center'
            }
        );
        descText.setOrigin(0.5, 0);
        this.itemDetailsContainer.add(descText);
        
        // Item price
        const priceText = this.scene.add.text(
            0, 
            -this.options.height/2 + 250, 
            `Price: ${price} gold`, 
            {
                fontFamily: 'Arial',
                fontSize: '18px',
                color: '#FFD700'
            }
        );
        priceText.setOrigin(0.5);
        this.itemDetailsContainer.add(priceText);
        
        // Action button (buy or sell)
        const actionText = this.currentTab === 'buy' ? 'Buy Item' : 'Sell Item';
        const actionButton = this.scene.add.container(0, this.options.height/2 - 80);
        
        const buttonBg = this.scene.add.rectangle(
            0, 
            0, 
            200, 
            50, 
            0x444444, 
            0.9
        );
        buttonBg.setStrokeStyle(2, 0xFFD700);
        actionButton.add(buttonBg);
        
        const buttonText = this.scene.add.text(
            0, 
            0, 
            actionText, 
            {
                fontFamily: 'Arial',
                fontSize: '18px',
                color: '#FFFFFF'
            }
        );
        buttonText.setOrigin(0.5);
        actionButton.add(buttonText);
        
        actionButton.setInteractive(new Phaser.Geom.Rectangle(-100, -25, 200, 50), Phaser.Geom.Rectangle.Contains);
        actionButton.on('pointerdown', () => {
            if (this.currentTab === 'buy') {
                this.buyItem(item, price);
            } else {
                this.sellItem(item, price);
            }
        });
        actionButton.on('pointerover', () => {
            buttonBg.setFillStyle(0x666666, 0.9);
        });
        actionButton.on('pointerout', () => {
            buttonBg.setFillStyle(0x444444, 0.9);
        });
        
        this.itemDetailsContainer.add(actionButton);
    }
    
    /**
     * Clear the item details panel
     * @private
     */
    clearItemDetails() {
        this.itemDetailsContainer.removeAll(true);
        this.selectedItem = null;
    }
    
    /**
     * Buy an item from the shop
     * @param {Object} item - The item to buy
     * @param {number} price - The price of the item
     * @private
     */
    buyItem(item, price) {
        // Check if player has enough money
        if (!this.scene.hasEnoughMoney(price)) {
            this.scene.showNotification('Not enough gold!', 'error');
            return;
        }
        
        // Subtract money
        this.scene.subtractMoney(price);
        
        // Add item to inventory
        this.scene.addItemToInventory({...item});
        
        // Show notification
        this.scene.showNotification(`Purchased: ${item.name}`);
        
        // Update money display
        this.updateMoneyDisplay();
        
        // Refresh item list if in sell tab
        if (this.currentTab === 'sell') {
            this.showItemList();
        }
        
        // Clear item details
        this.clearItemDetails();
    }
    
    /**
     * Sell an item to the shop
     * @param {Object} item - The item to sell
     * @param {number} price - The price of the item
     * @private
     */
    sellItem(item, price) {
        // Remove item from inventory
        if (!this.scene.removeItemFromInventory(item.id)) {
            this.scene.showNotification('Failed to sell item', 'error');
            return;
        }
        
        // Add money
        this.scene.addMoney(price);
        
        // Show notification
        this.scene.showNotification(`Sold: ${item.name}`, '', `+${price} gold`);
        
        // Update money display
        this.updateMoneyDisplay();
        
        // Refresh item list
        this.showItemList();
        
        // Clear item details
        this.clearItemDetails();
    }
    
    /**
     * Update the money display
     * @private
     */
    updateMoneyDisplay() {
        if (this.moneyText) {
            this.moneyText.setText(`Gold: ${this.scene.getMoney()}`);
        }
    }
    
    /**
     * Open the shop
     */
    open() {
        if (this.isOpen) return;
        
        this.isOpen = true;
        this.container.setVisible(true);
        
        // Update money display
        this.updateMoneyDisplay();
        
        // Refresh item list
        this.showItemList();
        
        // Clear item details
        this.clearItemDetails();
        
        // Add animation
        this.scene.tweens.add({
            targets: this.container,
            scale: { from: 0.8, to: 1 },
            alpha: { from: 0, to: 1 },
            duration: 200,
            ease: 'Power2'
        });
    }
    
    /**
     * Close the shop
     */
    close() {
        if (!this.isOpen) return;
        
        // Add animation
        this.scene.tweens.add({
            targets: this.container,
            scale: { from: 1, to: 0.8 },
            alpha: { from: 1, to: 0 },
            duration: 200,
            ease: 'Power2',
            onComplete: () => {
                this.isOpen = false;
                this.container.setVisible(false);
            }
        });
    }
    
    /**
     * Toggle the shop open/closed
     */
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    /**
     * Add an item to the shop inventory
     * @param {Object} item - The item to add
     */
    addItem(item) {
        if (!item.price) {
            console.warn('Item added to shop has no price:', item.name);
        }
        
        this.inventory.push(item);
        
        // Refresh item list if shop is open and in buy tab
        if (this.isOpen && this.currentTab === 'buy') {
            this.showItemList();
        }
    }
    
    /**
     * Remove an item from the shop inventory
     * @param {string} itemId - The ID of the item to remove
     * @returns {boolean} Whether the item was successfully removed
     */
    removeItem(itemId) {
        const index = this.inventory.findIndex(item => item.id === itemId);
        
        if (index === -1) return false;
        
        this.inventory.splice(index, 1);
        
        // Refresh item list if shop is open and in buy tab
        if (this.isOpen && this.currentTab === 'buy') {
            this.showItemList();
        }
        
        return true;
    }
    
    /**
     * Set the shop inventory
     * @param {Array} items - The new inventory
     */
    setInventory(items) {
        this.inventory = items;
        
        // Refresh item list if shop is open and in buy tab
        if (this.isOpen && this.currentTab === 'buy') {
            this.showItemList();
        }
    }
    
    /**
     * Clean up resources when the scene is shut down
     */
    shutdown() {
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
}
