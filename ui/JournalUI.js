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
        
        // Special handling for Factions category
        if (this.currentCategory === 'Factions') {
            this.displayFactions();
            return;
        }
        
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
    
    displayFactions() {
        const padding = 10;
        let yOffset = 20;
        
        // Section title for reputation
        const reputationTitle = this.scene.add.text(360, yOffset, 
            'FACTION STANDING', {
            fontSize: '22px',
            fontFamily: 'Georgia',
            color: '#7fff8e',
            fontStyle: 'bold'
        }).setOrigin(0.5, 0);
        this.contentContainer.add(reputationTitle);
        yOffset += reputationTitle.height + padding * 2;
        
        // Get faction reputation system from scene registry
        const factionSystem = this.scene.registry.get('factionSystem');
        
        if (!factionSystem) {
            const noSystemText = this.scene.add.text(360, yOffset, 
                'Faction system not available.', {
                fontSize: '18px',
                fontFamily: 'Georgia',
                color: '#7fff8e',
                wordWrap: { width: 700 }
            }).setOrigin(0.5, 0);
            
            this.contentContainer.add(noSystemText);
            yOffset += noSystemText.height + padding * 2;
        } else {
            // Get all factions
            const factions = factionSystem.factions;
            const discoveredFactions = Object.keys(factions).filter(key => {
                // Only show factions that have been discovered
                return factions[key].discovered || factions[key].reputation !== 0;
            });
            
            if (discoveredFactions.length === 0) {
                const noFactionsText = this.scene.add.text(360, yOffset, 
                    'No factions discovered yet.', {
                    fontSize: '16px',
                    fontFamily: 'Georgia',
                    color: '#aaaaaa',
                    wordWrap: { width: 700 },
                    align: 'center'
                }).setOrigin(0.5, 0);
                
                this.contentContainer.add(noFactionsText);
                yOffset += noFactionsText.height + padding * 2;
            } else {
                // Display each discovered faction
                discoveredFactions.forEach(factionKey => {
                    const faction = factions[factionKey];
                    const reputation = faction.reputation;
                    
                    // Create faction entry box
                    const entryBox = this.scene.add.graphics();
                    entryBox.fillStyle(0x1a3b23, 0.8);
                    entryBox.lineStyle(2, faction.color || 0x2a623d);
                    
                    this.contentContainer.add(entryBox);
                    
                    // Faction name
                    const nameText = this.scene.add.text(padding, yOffset + padding, 
                        faction.name, {
                        fontSize: '24px',
                        fontFamily: 'Georgia',
                        color: '#7fff8e',
                        fontStyle: 'bold'
                    });
                    this.contentContainer.add(nameText);
                    
                    // Reputation bar background
                    const barWidth = 400;
                    const barHeight = 20;
                    const barX = padding;
                    const barY = yOffset + nameText.height + padding * 2;
                    
                    const barBg = this.scene.add.graphics();
                    barBg.fillStyle(0x0a1a12, 1);
                    barBg.fillRect(barX, barY, barWidth, barHeight);
                    barBg.lineStyle(1, 0x2a623d);
                    barBg.strokeRect(barX, barY, barWidth, barHeight);
                    this.contentContainer.add(barBg);
                    
                    // Reputation bar fill
                    const maxRep = 100; // Maximum reputation value
                    const minRep = -100; // Minimum reputation value
                    const normalizedRep = Math.max(minRep, Math.min(maxRep, reputation));
                    const fillWidth = (Math.abs(normalizedRep) / maxRep) * (barWidth / 2);
                    
                    const barFill = this.scene.add.graphics();
                    if (normalizedRep >= 0) {
                        // Positive reputation - green bar from center to right
                        barFill.fillStyle(0x7fff8e, 0.8);
                        barFill.fillRect(barX + barWidth / 2, barY, fillWidth, barHeight);
                    } else {
                        // Negative reputation - red bar from center to left
                        barFill.fillStyle(0xff4444, 0.8);
                        barFill.fillRect(barX + barWidth / 2 - fillWidth, barY, fillWidth, barHeight);
                    }
                    this.contentContainer.add(barFill);
                    
                    // Reputation value text
                    const repText = this.scene.add.text(barX + barWidth + padding, barY + barHeight / 2, 
                        `${reputation >= 0 ? '+' : ''}${reputation}`, {
                        fontSize: '18px',
                        fontFamily: 'Georgia',
                        color: reputation >= 0 ? '#7fff8e' : '#ff4444',
                        fontStyle: 'bold'
                    }).setOrigin(0, 0.5);
                    this.contentContainer.add(repText);
                    
                    // Reputation status text
                    let statusText = '';
                    if (reputation >= 75) statusText = 'Revered';
                    else if (reputation >= 50) statusText = 'Honored';
                    else if (reputation >= 25) statusText = 'Friendly';
                    else if (reputation >= 10) statusText = 'Liked';
                    else if (reputation > -10) statusText = 'Neutral';
                    else if (reputation > -25) statusText = 'Disliked';
                    else if (reputation > -50) statusText = 'Unfriendly';
                    else if (reputation > -75) statusText = 'Hostile';
                    else statusText = 'Hated';
                    
                    const statusLabel = this.scene.add.text(padding, barY + barHeight + padding, 
                        `Status: ${statusText}`, {
                        fontSize: '16px',
                        fontFamily: 'Georgia',
                        color: '#ffffff',
                        fontStyle: 'italic'
                    });
                    this.contentContainer.add(statusLabel);
                    
                    // Faction description
                    const descText = this.scene.add.text(padding, barY + barHeight + statusLabel.height + padding * 2, 
                        faction.description || 'A mysterious faction.', {
                        fontSize: '14px',
                        fontFamily: 'Georgia',
                        color: '#aaaaaa',
                        wordWrap: { width: 700 },
                        lineSpacing: 4
                    });
                    this.contentContainer.add(descText);
                    
                    // Calculate entry height
                    const entryHeight = nameText.height + barHeight + statusLabel.height + descText.height + padding * 7;
                    entryBox.fillRoundedRect(0, yOffset, 720, entryHeight, 10);
                    entryBox.strokeRoundedRect(0, yOffset, 720, entryHeight, 10);
                    
                    // Add glowing spots
                    this.addGlowingSpots(entryBox, 0, yOffset, 720, entryHeight);
                    
                    // Update yOffset for next faction
                    yOffset += entryHeight + padding * 2;
                });
            }
        }
        
        // Add separator line
        const separator = this.scene.add.graphics();
        separator.lineStyle(2, 0x2a623d);
        separator.lineBetween(50, yOffset, 670, yOffset);
        this.contentContainer.add(separator);
        yOffset += padding * 3;
        
        // Section title for journal entries
        const journalTitle = this.scene.add.text(360, yOffset, 
            'FACTION RECORDS', {
            fontSize: '22px',
            fontFamily: 'Georgia',
            color: '#7fff8e',
            fontStyle: 'bold'
        }).setOrigin(0.5, 0);
        this.contentContainer.add(journalTitle);
        yOffset += journalTitle.height + padding * 2;
        
        // Get journal entries for Factions category
        const entries = this.journalSystem.getEntriesByCategory('Factions');
        
        if (entries.length === 0) {
            const noEntriesText = this.scene.add.text(360, yOffset, 
                'No faction records yet.', {
                fontSize: '16px',
                fontFamily: 'Georgia',
                color: '#aaaaaa',
                wordWrap: { width: 700 },
                align: 'center'
            }).setOrigin(0.5, 0);
            
            this.contentContainer.add(noEntriesText);
            yOffset += noEntriesText.height + padding;
        } else {
            // Sort entries by timestamp (newest first)
            entries.sort((a, b) => b.timestamp - a.timestamp);
            
            entries.forEach(entry => {
                // Entry container with fungal styling
                const entryBox = this.scene.add.graphics();
                entryBox.fillStyle(0x1a3b23, 0.8);
                entryBox.lineStyle(1, 0x2a623d);
                
                this.contentContainer.add(entryBox);
                
                // Title
                const titleText = this.scene.add.text(padding, yOffset + padding, 
                    entry.title, {
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
                    wordWrap: { width: 680 - padding * 2 },
                    lineSpacing: 5
                });
                this.contentContainer.add(contentText);
                
                // Calculate entry height
                const entryHeight = titleText.height + contentText.height + padding * 4;
                entryBox.fillRoundedRect(0, yOffset, 720, entryHeight, 10);
                entryBox.strokeRoundedRect(0, yOffset, 720, entryHeight, 10);
                
                // Add glowing spots
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
