import LanguageSystem from '../systems/LanguageSystem.js';

export default class QuestLog {
    constructor(scene, x = 750, y = 50) {
        this.scene = scene;
        this.questSystem = scene.registry.get('questSystem');
        this.lang = LanguageSystem.getInstance();
        this.expandedQuests = new Set();
        
        // Create quest log button
        this.createQuestButton(x, y);
        
        // Create quest log panel (initially hidden)
        this.createQuestPanel();
        
        // Subscribe to quest updates
        this.questSystem.subscribe(this.updateQuestDisplay.bind(this));
        
        // Add keyboard shortcut
        this.scene.input.keyboard.on('keydown-Q', () => {
            this.toggleQuestLog();
        });

        // Simple mouse wheel scrolling
        this.scene.input.on('wheel', (pointer, gameObjects, deltaX, deltaY, deltaZ) => {
            if (this.questPanel.visible && this.questContent) {
                // Calculate scroll bounds
                const visibleHeight = 430; // Height of the visible area (mask height)
                const contentHeight = this.contentHeight || 0;
                const minY = -200; // Top position
                const maxY = contentHeight > visibleHeight ? -(contentHeight - visibleHeight + 200) : -200;
                
                // Apply scroll with clamping
                const scrollSpeed = 0.8;
                const newY = Phaser.Math.Clamp(
                    this.questContent.y - deltaY * scrollSpeed,
                    maxY, // Don't scroll past bottom
                    minY  // Don't scroll past top
                );
                
                // Set new position directly
                this.questContent.setY(newY);
            }
        });
    }

    createQuestButton(x, y) {
        // Create container for the button
        this.buttonContainer = this.scene.add.container(x, y);
        this.buttonContainer.setDepth(100);
        this.buttonContainer.setScrollFactor(0);
        
        // Create mushroom-shaped button background
        const buttonBg = this.scene.add.graphics();
        buttonBg.fillStyle(0x2a623d); // Dark green cap
        buttonBg.fillCircle(0, -10, 20);
        buttonBg.fillStyle(0x1a3b23); // Darker green stem
        buttonBg.fillRect(-10, -10, 20, 25);
        
        // Add glowing spots
        const spot1 = this.scene.add.circle(-5, -15, 3, 0x7fff8e);
        const spot2 = this.scene.add.circle(5, -20, 2, 0x7fff8e);
        spot1.setAlpha(0.7);
        spot2.setAlpha(0.7);
        
        // Add text label
        const label = this.scene.add.text(0, 20, this.lang.t('ui.hud.quests'), {
            font: '12px Arial',
            fill: '#7fff8e',
            align: 'center'
        });
        label.setOrigin(0.5);
        
        // Add all button elements to container first
        this.buttonContainer.add([buttonBg, spot1, spot2, label]);
        
        // Create notification indicator (red exclamation mark) - add LAST so it appears on top
        this.questNotificationIndicator = this.scene.add.container(18, -22);
        this.questNotificationIndicator.setDepth(101);
        
        const indicatorBg = this.scene.add.circle(0, 0, 8, 0xff0000);
        const indicatorText = this.scene.add.text(0, 0, '!', {
            fontSize: '14px',
            fontFamily: 'Arial',
            color: '#ffffff',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        
        this.questNotificationIndicator.add([indicatorBg, indicatorText]);
        // Add indicator AFTER all other elements so it renders on top
        this.buttonContainer.add(this.questNotificationIndicator);
        
        // Hide indicator initially
        this.questNotificationIndicator.setVisible(false);
        
        // Check if there are unread quest updates
        if (this.scene.registry.get('hasUnreadQuestUpdates')) {
            this.questNotificationIndicator.setVisible(true);
        }
        
        // Make button interactive
        this.buttonContainer.setSize(40, 60);
        this.buttonContainer.setInteractive({ useHandCursor: true });
        this.buttonContainer.on('pointerover', () => {
            this.buttonContainer.setScale(1.1);
        });
        this.buttonContainer.on('pointerout', () => {
            this.buttonContainer.setScale(1);
        });
        this.buttonContainer.on('pointerdown', () => {
            this.toggleQuestLog();
        });
    }

    createQuestPanel() {
        this.questPanel = this.scene.add.container(400, 280);
        this.questPanel.setDepth(1000); // Increased to display over Spore bar
        this.questPanel.setScrollFactor(0);
        this.questPanel.visible = false;
        
        const bg = this.scene.add.graphics();
        bg.fillStyle(0x0a2712, 0.95); // Dark green background to match game style
        bg.fillRect(-300, -250, 600, 500); // Reduced height from 600 to 500
        
        // Add decorative border
        bg.lineStyle(4, 0x1a3b23); // Dark green border
        bg.strokeRect(-300, -250, 600, 500);
        
        // Inner border
        bg.lineStyle(1, 0x2a623d);
        bg.strokeRect(-290, -240, 580, 480);
        
        // Add decorative corners
        this.addDecorativeCorner(bg, -300, -250, 0); // Top left
        this.addDecorativeCorner(bg, 300, -250, Math.PI/2); // Top right
        this.addDecorativeCorner(bg, 300, 250, Math.PI); // Bottom right
        this.addDecorativeCorner(bg, -300, 250, Math.PI*3/2); // Bottom left
        
        // Create tab buttons with green style
        const activeTabStyle = { 
            font: 'bold 22px Georgia', 
            fill: '#7fff8e', // Light green color
            stroke: '#000000',
            strokeThickness: 2
        };
        const inactiveTabStyle = { 
            font: '20px Georgia', 
            fill: '#5c9b6b', // Darker green color
            stroke: '#000000',
            strokeThickness: 1
        };
        
        this.activeTab = 'active';
        
        const tabBg = this.scene.add.graphics();
        tabBg.fillStyle(0x1a3b23); // Dark green tab background
        tabBg.fillRect(-300, -250, 290, 45); // Active tab background
        tabBg.fillStyle(0x0a2712); // Darker green for inactive
        tabBg.fillRect(0, -250, 290, 45); // Finished tab background
        
        this.addParchmentTexture(tabBg, -300, -250, 290, 45, 0.1);
        this.addParchmentTexture(tabBg, 0, -250, 290, 45, 0.1);
        
        this.activeTabButton = this.scene.add.text(-270, -237, this.lang.t('ui.hud.activeQuests'), activeTabStyle);
        this.finishedTabButton = this.scene.add.text(30, -237, this.lang.t('ui.hud.completedQuests'), inactiveTabStyle);
        
        this.activeTabButton.setInteractive({ useHandCursor: true });
        this.finishedTabButton.setInteractive({ useHandCursor: true });
        
        this.activeTabButton.on('pointerdown', () => {
            if (this.activeTab !== 'active') {
                this.activeTab = 'active';
                this.activeTabButton.setStyle(activeTabStyle);
                this.finishedTabButton.setStyle(inactiveTabStyle);
                tabBg.clear();
                tabBg.fillStyle(0x1a3b23);
                tabBg.fillRect(-300, -250, 290, 45);
                tabBg.fillStyle(0x0a2712);
                tabBg.fillRect(0, -250, 290, 45);
                this.addParchmentTexture(tabBg, -300, -250, 290, 45, 0.1);
                this.addParchmentTexture(tabBg, 0, -250, 290, 45, 0.1);
                this.updateQuestDisplay();
            }
        });
        
        this.finishedTabButton.on('pointerdown', () => {
            if (this.activeTab !== 'finished') {
                this.activeTab = 'finished';
                this.finishedTabButton.setStyle(activeTabStyle);
                this.activeTabButton.setStyle(inactiveTabStyle);
                tabBg.clear();
                tabBg.fillStyle(0x0a2712);
                tabBg.fillRect(-300, -250, 290, 45);
                tabBg.fillStyle(0x1a3b23);
                tabBg.fillRect(0, -250, 290, 45);
                this.addParchmentTexture(tabBg, -300, -250, 290, 45, 0.1);
                this.addParchmentTexture(tabBg, 0, -250, 290, 45, 0.1);
                this.updateQuestDisplay();
            }
        });
        
        const divider = this.scene.add.graphics();
        divider.lineStyle(2, 0x1a3b23);
        divider.lineBetween(-290, -200, 290, -200);
        
        // Create mask for scrollable content to prevent text leaking
        // Position mask in world coordinates (questPanel is at 400, 280)
        const maskGraphics = this.scene.add.graphics();
        maskGraphics.fillStyle(0xffffff);
        maskGraphics.fillRect(120, 90, 560, 430); // World coordinates: 400-280=120, 280-190=90
        maskGraphics.setVisible(false); // Hide the mask graphics
        
        // Create quest content container with mask
        this.questContent = this.scene.add.container(0, -200);
        const mask = maskGraphics.createGeometryMask();
        this.questContent.setMask(mask);
        
        // Add all elements to panel
        this.questPanel.add([bg, tabBg, divider, this.activeTabButton, this.finishedTabButton, this.questContent]);
        
        // Add close button with green style
        const closeButton = this.scene.add.text(280, -240, 'X', {
            font: 'bold 24px Georgia',
            fill: '#7fff8e',
            stroke: '#000000',
            strokeThickness: 2
        });
        closeButton.setInteractive({ useHandCursor: true });
        closeButton.on('pointerdown', () => {
            this.hideQuestLog();
        });
        this.questPanel.add(closeButton);
    }
    
    // Helper method to add decorative corners
    addDecorativeCorner(graphics, x, y, rotation) {
        graphics.save();
        graphics.translateCanvas(x, y);
        graphics.rotateCanvas(rotation);
        
        // Draw corner decoration
        graphics.lineStyle(2, 0x1a3b23);
        graphics.beginPath();
        graphics.moveTo(0, 20);
        graphics.lineTo(0, 0);
        graphics.lineTo(20, 0);
        graphics.stroke();
        
        // Add small flourish
        graphics.lineStyle(1, 0x2a623d);
        graphics.beginPath();
        graphics.moveTo(5, 15);
        graphics.lineTo(15, 5);
        graphics.stroke();
        
        graphics.restore();
    }
    
    // Helper method to add parchment-like texture
    addParchmentTexture(graphics, x, y, width, height, intensity) {
        // Add subtle noise/grain to simulate parchment texture
        graphics.fillStyle(0xffffff, intensity);
        
        // Create random dots/specks
        for (let i = 0; i < width * height / 100; i++) {
            const dotX = x + Math.random() * width;
            const dotY = y + Math.random() * height;
            const size = Math.random() * 2 + 0.5;
            graphics.fillCircle(dotX, dotY, size);
        }
    }

    createQuestEntry(quest, yOffset) {
        // Resolve translated quest content
        const tKey = `quests.${quest.id}`;
        const tTitle = this.lang.t(`${tKey}.title`);
        const tDesc = this.lang.t(`${tKey}.description`);
        const displayTitle = tTitle === `${tKey}.title` ? quest.title : tTitle;
        const displayDesc = tDesc === `${tKey}.description` ? quest.description : tDesc;

        // Simple approach to ensure text is visible
        const container = this.scene.add.container(0, yOffset);
        const isExpanded = this.expandedQuests.has(quest.id);
        
        // Create background
        const entryBg = this.scene.add.graphics();
        entryBg.fillStyle(0x0f2415, 0.4);
        entryBg.fillRect(-250, 0, 500, isExpanded ? 200 : 50);
        entryBg.lineStyle(1, 0x1a3b23, 0.5);
        entryBg.strokeRect(-250, 0, 500, isExpanded ? 200 : 50);
        container.add(entryBg);
        
        // Add toggle indicator
        const toggleButton = this.scene.add.text(-230, 15, isExpanded ? '▼' : '►', {
            font: 'bold 18px Georgia',
            fill: quest.isComplete ? '#00ff00' : '#7fff8e',
            stroke: '#000000',
            strokeThickness: 1
        });
        
        // Add quest title
        const title = this.scene.add.text(-200, 15, displayTitle, {
            font: 'bold 22px Georgia',
            fill: quest.isComplete ? '#00ff00' : '#7fff8e',
            stroke: '#000000',
            strokeThickness: 2,
            wordWrap: { width: 400 }
        });
        
        // Make clickable
        const headerZone = this.scene.add.zone(-250, 0, 500, 50);
        headerZone.setOrigin(0);
        headerZone.setInteractive({ useHandCursor: true });
        headerZone.on('pointerdown', () => {
            this.toggleQuestExpansion(quest.id);
        });
        
        // Add hover effect
        headerZone.on('pointerover', () => {
            entryBg.clear();
            entryBg.fillStyle(0x1a3b23, 0.6);
            entryBg.fillRect(-250, 0, 500, isExpanded ? entryHeight : 50);
            entryBg.lineStyle(1, 0x2a623d, 0.7);
            entryBg.strokeRect(-250, 0, 500, isExpanded ? entryHeight : 50);
        });
        
        headerZone.on('pointerout', () => {
            entryBg.clear();
            entryBg.fillStyle(0x0f2415, 0.4);
            entryBg.fillRect(-250, 0, 500, isExpanded ? entryHeight : 50);
            entryBg.lineStyle(1, 0x1a3b23, 0.5);
            entryBg.strokeRect(-250, 0, 500, isExpanded ? entryHeight : 50);
        });
        
        container.add([toggleButton, title, headerZone]);
        let contentY = 60;
        let entryHeight = 50;
        
        // Add description and updates if expanded
        if (isExpanded) {
            // Add description
            const desc = this.scene.add.text(-230, contentY, displayDesc, {
                font: '18px Georgia',
                fill: '#7fff8e',
                wordWrap: { width: 460 },
                lineSpacing: 8
            });
            container.add(desc);
            contentY += desc.height + 20;
            
            // Add updates if any
            if (quest.updates && quest.updates.length > 0) {
                // Add header
                const updatesHeader = this.scene.add.text(-230, contentY, this.lang.t('ui.hud.questProgress'), {
                    font: 'italic 18px Georgia',
                    fill: '#00ff00',
                    stroke: '#000000',
                    strokeThickness: 1
                });
                container.add(updatesHeader);
                contentY += 30;
                
                // Add each update
                quest.updates.forEach(update => {
                    // Resolve translated update text via the update key
                    let displayUpdate = update.text;
                    if (update.key) {
                        const uKey = `${tKey}.updates.${update.key}`;
                        const tUpdate = this.lang.t(uKey);
                        if (tUpdate !== uKey) displayUpdate = tUpdate;
                    }

                    // Add bullet
                    const bullet = this.scene.add.graphics();
                    bullet.fillStyle(0x7fff8e, 0.8);
                    bullet.fillCircle(-220, contentY + 8, 4);
                    container.add(bullet);
                    
                    // Add update text
                    const updateText = this.scene.add.text(-205, contentY, displayUpdate, {
                        font: '16px Georgia',
                        fill: '#5c9b6b',
                        wordWrap: { width: 420 },
                        lineSpacing: 6
                    });
                    container.add(updateText);
                    contentY += updateText.height + 15;
                });
            }
            
            // Update height
            entryHeight = contentY + 10;
            
            // Update background
            entryBg.clear();
            entryBg.fillStyle(0x0f2415, 0.4);
            entryBg.fillRect(-250, 0, 500, entryHeight);
            entryBg.lineStyle(1, 0x1a3b23, 0.5);
            entryBg.strokeRect(-250, 0, 500, entryHeight);
        }
        
        this.questContent.add(container);
        return entryHeight + 15;
    }

    updateQuestDisplay() {
        // Reset position to top
        this.questContent.y = -200;
        
        // Clear existing content
        this.questContent.removeAll(true);
        
        // Get all quests
        const quests = this.questSystem.getAllQuests();
        
        // Filter quests based on active tab
        const filteredQuests = quests.filter(quest => 
            (this.activeTab === 'active' && !quest.isComplete) || 
            (this.activeTab === 'finished' && quest.isComplete)
        );
        
        // Show message if no quests in current tab
        if (filteredQuests.length === 0) {
            const noQuestsText = this.scene.add.text(0, 0, 
                this.activeTab === 'active' ? 
                this.lang.t('ui.hud.noActiveQuests') : 
                this.lang.t('ui.hud.noCompletedQuests'), 
                {
                    font: 'italic 20px Georgia',
                    fill: '#5c9b6b',
                    align: 'center'
                }
            );
            noQuestsText.setOrigin(0.5);
            this.questContent.add(noQuestsText);
            this.contentHeight = 50; // Minimal height for empty state
            return;
        }
        
        // Add quests to the content container
        let yOffset = 0;
        filteredQuests.forEach(quest => {
            const height = this.createQuestEntry(quest, yOffset);
            yOffset += height;
        });

        // Store total content height for scrolling calculations
        this.contentHeight = yOffset;
    }

    toggleQuestExpansion(questId) {
        if (this.expandedQuests.has(questId)) {
            this.expandedQuests.delete(questId);
        } else {
            this.expandedQuests.add(questId);
        }
        this.updateQuestDisplay();
    }

    toggleQuestLog() {
        if (this.questPanel.visible) {
            this.hideQuestLog();
        } else {
            this.showQuestLog();
        }
    }

    showQuestLog() {
        this.questPanel.visible = true;
        this.scene.registry.set('questLogVisible', true);
        this.updateQuestDisplay();
        // Hide notification indicator when quest log is opened
        if (this.questNotificationIndicator) {
            this.questNotificationIndicator.setVisible(false);
            this.scene.registry.set('hasUnreadQuestUpdates', false);
        }
    }

    hideQuestLog() {
        this.questPanel.visible = false;
        this.scene.registry.set('questLogVisible', false);
    }

    cleanup() {
        this.questSystem.unsubscribe(this.updateQuestDisplay.bind(this));
        if (this.buttonContainer) {
            this.buttonContainer.destroy();
        }
        if (this.questPanel) {
            this.questPanel.destroy();
        }
    }
}
