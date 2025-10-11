/**
 * JournalUI.js
 * User interface for displaying journal entries with a fungal theme
 */
class JournalUI {
    constructor(scene) {
        this.scene = scene;
        this.visible = false;
        this.currentCategory = null;
        this.journalSystem = this.scene.journalSystem;
        
        // Create UI container
        this.container = this.scene.add.container(400, 300);
        this.container.setDepth(1000);
        this.container.visible = false;
        
        this.createUI();
        
        // Register ESC key to close journal
        this.escKey = this.scene.input.keyboard.addKey('ESC');
        this.escKey.on('down', () => {
            if (this.visible) {
                this.toggle();
            }
        });
        
        // Register J key as shortcut to open journal
        this.jKey = this.scene.input.keyboard.addKey('J');
        this.jKey.on('down', () => {
            this.toggle();
        });
    }
    
    createUI() {
        // Background panel
        this.background = this.scene.add.graphics();
        this.background.fillStyle(0x0a1a12, 0.95); // Dark green background
        this.background.fillRect(-400, -300, 800, 600);
        this.background.lineStyle(2, 0x2a623d); // Border color matching fungal theme
        this.background.strokeRect(-400, -300, 800, 600);
        this.container.add(this.background);
        
        // Title
        this.title = this.scene.add.text(0, -260, "JOURNAL", {
            fontSize: '32px',
            fontFamily: 'Georgia',
            color: '#7fff8e',
            align: 'center'
        }).setOrigin(0.5);
        this.container.add(this.title);
        
        // Decorative fungal elements
        this.addFungalDecoration(-380, -280, 30, 0x2a623d); // Top left
        this.addFungalDecoration(380, -280, 30, 0x2a623d); // Top right
        this.addFungalDecoration(-380, 280, 30, 0x2a623d); // Bottom left
        this.addFungalDecoration(380, 280, 30, 0x2a623d); // Bottom right
        
        // Close button
        this.closeButton = this.scene.add.text(380, -280, "X", {
            fontSize: '24px',
            fontFamily: 'Georgia',
            color: '#7fff8e'
        }).setOrigin(0.5).setInteractive({ useHandCursor: true });
        
        this.closeButton.on('pointerover', () => {
            this.closeButton.setColor('#ffffff');
        });
        
        this.closeButton.on('pointerout', () => {
            this.closeButton.setColor('#7fff8e');
        });
        
        this.closeButton.on('pointerdown', () => {
            this.toggle();
        });
        
        this.container.add(this.closeButton);
        
        // Category tabs
        this.createCategoryTabs();
        
        // Content area
        this.contentMask = this.scene.add.graphics();
        this.contentMask.fillRect(-360, -200, 1280, 720);
        this.contentMaskObj = new Phaser.Display.Masks.GeometryMask(this.scene, this.contentMask);
        
        this.contentContainer = this.scene.add.container(-360, -200);
        this.contentContainer.setMask(this.contentMaskObj);
        this.container.add(this.contentContainer);
        
        // Scrolling controls
        this.scrollUpButton = this.createScrollButton(-25, -210, 'up');
        this.scrollDownButton = this.createScrollButton(-25, 240, 'down');
        
        // Enable scrolling with mouse wheel
        this.scene.input.on('wheel', (pointer, gameObjects, deltaX, deltaY, deltaZ) => {
            if (this.visible) {
                const scrollSpeed = 20;
                if (deltaY > 0) {
                    this.scroll(scrollSpeed);
                } else if (deltaY < 0) {
                    this.scroll(-scrollSpeed);
                }
            }
        });
    }
    
    addFungalDecoration(x, y, size, color) {
        const decoration = this.scene.add.graphics();
        decoration.fillStyle(color, 1);
        decoration.fillCircle(x, y, size);
        
        // Add glowing spots
        decoration.fillStyle(0x7fff8e, 0.7); // Glowing green
        decoration.fillCircle(x + size * 0.3, y - size * 0.2, size * 0.2);
        decoration.fillCircle(x - size * 0.25, y + size * 0.3, size * 0.15);
        
        this.container.add(decoration);
        
        // Add pulsating animation
        this.scene.tweens.add({
            targets: decoration,
            alpha: { from: 0.9, to: 1 },
            duration: 1500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
    }
    
    createCategoryTabs() {
        const categories = this.journalSystem.categories;
        const categoryKeys = Object.values(categories);
        
        this.categoryTabs = [];
        this.categoryButtons = [];
        
        const tabWidth = 120;
        const startX = -360 + tabWidth / 2;
        
        categoryKeys.forEach((category, index) => {
            const x = startX + index * tabWidth;
            
            // Tab background
            const tab = this.scene.add.graphics();
            tab.fillStyle(0x1a3b23, 1); // Dark green background
            tab.fillRect(x - tabWidth/2 + 5, -220, tabWidth - 10, 40);
            tab.lineStyle(2, 0x2a623d); // Border
            tab.strokeRect(x - tabWidth/2 + 5, -220, tabWidth - 10, 40);
            
            this.container.add(tab);
            this.categoryTabs.push(tab);
            
            // Tab text
            const tabButton = this.scene.add.text(x, -200, category, {
                fontSize: '18px',
                fontFamily: 'Georgia',
                color: '#7fff8e',
                align: 'center'
            }).setOrigin(0.5).setInteractive({ useHandCursor: true });
            
            tabButton.on('pointerover', () => {
                tabButton.setColor('#ffffff');
            });
            
            tabButton.on('pointerout', () => {
                tabButton.setColor('#7fff8e');
            });
            
            tabButton.on('pointerdown', () => {
                this.selectCategory(category);
            });
            
            this.container.add(tabButton);
            this.categoryButtons.push(tabButton);
        });
    }
    
    createScrollButton(x, y, direction) {
        const arrowSymbol = direction === 'up' ? '▲' : '▼';
        
        const button = this.scene.add.text(x, y, arrowSymbol, {
            fontSize: '24px',
            fontFamily: 'Georgia',
            color: '#7fff8e'
        }).setOrigin(0.5).setInteractive({ useHandCursor: true });
        
        button.on('pointerover', () => {
            button.setColor('#ffffff');
        });
        
        button.on('pointerout', () => {
            button.setColor('#7fff8e');
        });
        
        button.on('pointerdown', () => {
            const scrollAmount = direction === 'up' ? -50 : 50;
            this.scroll(scrollAmount);
        });
        
        this.container.add(button);
        return button;
    }
    
    scroll(amount) {
        if (this.contentContainer.list.length > 0) {
            const minY = 200 - this.contentContainer.height;
            const newY = Phaser.Math.Clamp(
                this.contentContainer.y + amount,
                minY,
                -200
            );
            
            if (newY !== this.contentContainer.y) {
                this.contentContainer.y = newY;
            }
        }
    }
    
    selectCategory(category) {
        this.currentCategory = category;
        this.refreshContent();
        
        // Update tab appearance
        const categoryKeys = Object.values(this.journalSystem.categories);
        categoryKeys.forEach((cat, index) => {
            if (cat === category) {
                this.categoryTabs[index].fillStyle(0x2a623d, 1); // Highlight selected tab
                this.categoryTabs[index].fillRect(this.categoryButtons[index].x - 60 + 5, -220, 110, 40);
                this.categoryTabs[index].lineStyle(2, 0x7fff8e);
                this.categoryTabs[index].strokeRect(this.categoryButtons[index].x - 60 + 5, -220, 110, 40);
            } else {
                this.categoryTabs[index].fillStyle(0x1a3b23, 1); // Normal tab
                this.categoryTabs[index].fillRect(this.categoryButtons[index].x - 60 + 5, -220, 110, 40);
                this.categoryTabs[index].lineStyle(2, 0x2a623d); 
                this.categoryTabs[index].strokeRect(this.categoryButtons[index].x - 60 + 5, -220, 110, 40);
            }
        });
    }
    
    refreshContent() {
        // Clear previous content
        this.contentContainer.removeAll(true);
        this.contentContainer.y = -200; // Reset scroll position
        
        let entries;
        if (this.currentCategory) {
            entries = this.journalSystem.getEntriesByCategory(this.currentCategory);
        } else {
            entries = this.journalSystem.getAllEntries();
        }
        
        // Sort entries by timestamp (newest first)
        entries.sort((a, b) => b.timestamp - a.timestamp);
        
        let yOffset = 20;
        const padding = 10;
        
        if (entries.length === 0) {
            const noEntriesText = this.scene.add.text(360, yOffset, 
                `No entries in ${this.currentCategory || "journal"} yet.`, {
                fontSize: '18px',
                fontFamily: 'Georgia',
                color: '#7fff8e',
                wordWrap: { width: 700 }
            }).setOrigin(0.5, 0);
            
            this.contentContainer.add(noEntriesText);
            yOffset += noEntriesText.height + padding;
        } else {
            entries.forEach(entry => {
                // Entry container with fungal styling
                const entryBox = this.scene.add.graphics();
                entryBox.fillStyle(0x1a3b23, 0.8); // Entry background
                entryBox.fillRoundedRect(0, yOffset, 720, 0, 10); // Height will be determined later
                entryBox.lineStyle(1, 0x2a623d); // Border color
                
                this.contentContainer.add(entryBox);
                                
                // Title with date
                const titleText = this.scene.add.text(padding, yOffset + padding, 
                    `${entry.title}`, {
                    fontSize: '20px',
                    fontFamily: 'Georgia',
                    color: '#7fff8e',
                    fontStyle: 'bold'
                });
                
                this.contentContainer.add(titleText);
                
                // Content text
                const contentText = this.scene.add.text(padding, yOffset + titleText.height + padding * 2, 
                    entry.content, {
                    fontSize: '16px',
                    fontFamily: 'Georgia',
                    color: '#ffffff',
                    wordWrap: { width: 680 - padding * 2 }, // Reduced width to prevent overflow
                    lineSpacing: 5
                });
                
                this.contentContainer.add(contentText);
                
                // Update entry box height based on content
                const entryHeight = titleText.height + contentText.height + padding * 4;
                entryBox.fillRoundedRect(0, yOffset, 720, entryHeight, 10);
                entryBox.strokeRoundedRect(0, yOffset, 720, entryHeight, 10);
                
                // Add glowing spots to entry
                this.addGlowingSpots(entryBox, 0, yOffset, 720, entryHeight);
                
                // Update yOffset for next entry
                yOffset += entryHeight + padding * 2;
            });
        }
        
        // Update content container height
        this.contentContainer.height = yOffset;
    }
    
    addGlowingSpots(graphics, x, y, width, height) {
        graphics.fillStyle(0x7fff8e, 0.3); // Glowing green
        
        // Add random glowing spots
        const numSpots = Math.floor(Math.random() * 3) + 2;
        for (let i = 0; i < numSpots; i++) {
            const spotX = x + Math.random() * (width - 20) + 10;
            const spotY = y + Math.random() * (height - 20) + 10;
            const spotSize = Math.random() * 5 + 2;
            graphics.fillCircle(spotX, spotY, spotSize);
        }
    }
    
    toggle() {
        this.visible = !this.visible;
        this.container.visible = this.visible;
        
        if (this.visible) {
            // Select default category if none selected
            if (!this.currentCategory) {
                this.selectCategory(Object.values(this.journalSystem.categories)[0]);
            } else {
                this.refreshContent();
            }
            
            // Hide custom cursor when journal is open
            if (this.scene.customCursor) {
                this.scene.customCursor.visible = false;
            }
        } else {
            // Show custom cursor when journal is closed
            if (this.scene.customCursor) {
                this.scene.customCursor.visible = true;
            }
        }
    }
}

export default JournalUI;
