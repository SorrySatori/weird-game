export default class QuestLog {
    constructor(scene, x = 750, y = 50) {
        this.scene = scene;
        this.questSystem = scene.registry.get('questSystem');
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
                // Simple scrolling with reasonable limits
                const scrollSpeed = 0.5;
                const maxScroll = -this.contentHeight + 400;
                
                // Apply scroll with clamping
                const newY = Phaser.Math.Clamp(
                    this.questContent.y - deltaY * scrollSpeed,
                    maxScroll < -200 ? maxScroll : -200, // Don't scroll past bottom
                    -200 // Don't scroll past top
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
        const label = this.scene.add.text(0, 20, 'Quests', {
            font: '12px Arial',
            fill: '#7fff8e',
            align: 'center'
        });
        label.setOrigin(0.5);
        
        // Add all elements to container
        this.buttonContainer.add([buttonBg, spot1, spot2, label]);
        
        // Make button interactive
        this.buttonContainer.setSize(40, 60);
        this.buttonContainer.setInteractive({ useHandCursor: true });
        this.buttonContainer.on('pointerdown', () => {
            this.toggleQuestLog();
        });
    }

    createQuestPanel() {
        this.questPanel = this.scene.add.container(400, 300);
        this.questPanel.setDepth(200);
        this.questPanel.setScrollFactor(0);
        this.questPanel.visible = false;
        
        const bg = this.scene.add.graphics();
        bg.fillStyle(0x1a1a0e, 0.95); // Dark sepia background
        bg.fillRect(-300, -300, 600, 600); // Larger panel for more content
        
        // Add decorative border
        bg.lineStyle(4, 0x3d3d28); // Dark border
        bg.strokeRect(-300, -300, 600, 600);
        
        // Inner border with aged look
        bg.lineStyle(1, 0x5c5c3d);
        bg.strokeRect(-290, -290, 580, 580);
        
        // Add decorative corners
        this.addDecorativeCorner(bg, -300, -300, 0); // Top left
        this.addDecorativeCorner(bg, 300, -300, Math.PI/2); // Top right
        this.addDecorativeCorner(bg, 300, 300, Math.PI); // Bottom right
        this.addDecorativeCorner(bg, -300, 300, Math.PI*3/2); // Bottom left
        
        // Create tab buttons with parchment style
        const activeTabStyle = { 
            font: 'bold 22px Georgia', 
            fill: '#e6d2a8', // Light parchment color
            stroke: '#000000',
            strokeThickness: 2
        };
        const inactiveTabStyle = { 
            font: '20px Georgia', 
            fill: '#a89f81', // Darker parchment color
            stroke: '#000000',
            strokeThickness: 1
        };
        
        this.activeTab = 'active';
        
        const tabBg = this.scene.add.graphics();
        tabBg.fillStyle(0x2a2a1c); // Dark tab background
        tabBg.fillRect(-300, -300, 290, 45); // Active tab background
        tabBg.fillStyle(0x1a1a0e); // Darker for inactive
        tabBg.fillRect(0, -300, 290, 45); // Finished tab background
        
        this.addParchmentTexture(tabBg, -300, -300, 290, 45, 0.1);
        this.addParchmentTexture(tabBg, 0, -300, 290, 45, 0.1);
        
        this.activeTabButton = this.scene.add.text(-270, -287, 'ACTIVE QUESTS', activeTabStyle);
        this.finishedTabButton = this.scene.add.text(30, -287, 'COMPLETED QUESTS', inactiveTabStyle);
        
        this.activeTabButton.setInteractive({ useHandCursor: true });
        this.finishedTabButton.setInteractive({ useHandCursor: true });
        
        this.activeTabButton.on('pointerdown', () => {
            if (this.activeTab !== 'active') {
                this.activeTab = 'active';
                this.activeTabButton.setStyle(activeTabStyle);
                this.finishedTabButton.setStyle(inactiveTabStyle);
                tabBg.clear();
                tabBg.fillStyle(0x2a2a1c);
                tabBg.fillRect(-300, -300, 290, 45);
                tabBg.fillStyle(0x1a1a0e);
                tabBg.fillRect(0, -300, 290, 45);
                this.addParchmentTexture(tabBg, -300, -300, 290, 45, 0.1);
                this.addParchmentTexture(tabBg, 0, -300, 290, 45, 0.1);
                this.updateQuestDisplay();
            }
        });
        
        this.finishedTabButton.on('pointerdown', () => {
            if (this.activeTab !== 'finished') {
                this.activeTab = 'finished';
                this.finishedTabButton.setStyle(activeTabStyle);
                this.activeTabButton.setStyle(inactiveTabStyle);
                tabBg.clear();
                tabBg.fillStyle(0x1a1a0e);
                tabBg.fillRect(-300, -300, 290, 45);
                tabBg.fillStyle(0x2a2a1c);
                tabBg.fillRect(0, -300, 290, 45);
                this.addParchmentTexture(tabBg, -300, -300, 290, 45, 0.1);
                this.addParchmentTexture(tabBg, 0, -300, 290, 45, 0.1);
                this.updateQuestDisplay();
            }
        });
        
        // Add decorative divider below tabs
        const divider = this.scene.add.graphics();
        divider.lineStyle(2, 0x3d3d28);
        divider.lineBetween(-290, -250, 290, -250);
        
        // Create quest content container with a simple approach
        this.questContent = this.scene.add.container(0, 0);
        
        // Add all elements to panel
        this.questPanel.add([bg, tabBg, divider, this.activeTabButton, this.finishedTabButton, this.questContent]);
        
        // Add close button with Planescape style
        const closeButton = this.scene.add.text(280, -290, 'X', {
            font: 'bold 24px Georgia',
            fill: '#e6d2a8',
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
        graphics.lineStyle(2, 0x3d3d28);
        graphics.beginPath();
        graphics.moveTo(0, 20);
        graphics.lineTo(0, 0);
        graphics.lineTo(20, 0);
        graphics.stroke();
        
        // Add small flourish
        graphics.lineStyle(1, 0x5c5c3d);
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
        // Simple approach to ensure text is visible
        const container = this.scene.add.container(0, yOffset);
        const isExpanded = this.expandedQuests.has(quest.title);
        
        // Create background
        const entryBg = this.scene.add.graphics();
        entryBg.fillStyle(0x23231a, 0.4);
        entryBg.fillRect(-250, 0, 500, isExpanded ? 200 : 50);
        entryBg.lineStyle(1, 0x3d3d28, 0.5);
        entryBg.strokeRect(-250, 0, 500, isExpanded ? 200 : 50);
        container.add(entryBg);
        
        // Add toggle indicator
        const toggleButton = this.scene.add.text(-230, 15, isExpanded ? '▼' : '►', {
            font: 'bold 18px Georgia',
            fill: quest.isComplete ? '#daa520' : '#c8b273',
            stroke: '#000000',
            strokeThickness: 1
        });
        
        // Add quest title
        const title = this.scene.add.text(-200, 15, quest.title, {
            font: 'bold 22px Georgia',
            fill: quest.isComplete ? '#daa520' : '#e6d2a8',
            stroke: '#000000',
            strokeThickness: 2,
            wordWrap: { width: 400 }
        });
        
        // Make clickable
        const headerZone = this.scene.add.zone(-250, 0, 500, 50);
        headerZone.setOrigin(0);
        headerZone.setInteractive({ useHandCursor: true });
        headerZone.on('pointerdown', () => {
            this.toggleQuestExpansion(quest.title);
        });
        
        // Add hover effect
        headerZone.on('pointerover', () => {
            entryBg.clear();
            entryBg.fillStyle(0x2a2a20, 0.6);
            entryBg.fillRect(-250, 0, 500, isExpanded ? entryHeight : 50);
            entryBg.lineStyle(1, 0x5c5c3d, 0.7);
            entryBg.strokeRect(-250, 0, 500, isExpanded ? entryHeight : 50);
        });
        
        headerZone.on('pointerout', () => {
            entryBg.clear();
            entryBg.fillStyle(0x23231a, 0.4);
            entryBg.fillRect(-250, 0, 500, isExpanded ? entryHeight : 50);
            entryBg.lineStyle(1, 0x3d3d28, 0.5);
            entryBg.strokeRect(-250, 0, 500, isExpanded ? entryHeight : 50);
        });
        
        container.add([toggleButton, title, headerZone]);
        let contentY = 60;
        let entryHeight = 50;
        
        // Add description and updates if expanded
        if (isExpanded) {
            // Add description
            const desc = this.scene.add.text(-230, contentY, quest.description, {
                font: '18px Georgia',
                fill: '#c8b273',
                wordWrap: { width: 460 },
                lineSpacing: 8
            });
            container.add(desc);
            contentY += desc.height + 20;
            
            // Add updates if any
            if (quest.updates && quest.updates.length > 0) {
                // Add header
                const updatesHeader = this.scene.add.text(-230, contentY, 'Progress:', {
                    font: 'italic 18px Georgia',
                    fill: '#daa520',
                    stroke: '#000000',
                    strokeThickness: 1
                });
                container.add(updatesHeader);
                contentY += 30;
                
                // Add each update
                quest.updates.forEach(update => {
                    // Add bullet
                    const bullet = this.scene.add.graphics();
                    bullet.fillStyle(0xc8b273, 0.8);
                    bullet.fillCircle(-220, contentY + 8, 4);
                    container.add(bullet);
                    
                    // Add update text
                    const updateText = this.scene.add.text(-205, contentY, update.text, {
                        font: '16px Georgia',
                        fill: '#a89f81',
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
            entryBg.fillStyle(0x23231a, 0.4);
            entryBg.fillRect(-250, 0, 500, entryHeight);
            entryBg.lineStyle(1, 0x3d3d28, 0.5);
            entryBg.strokeRect(-250, 0, 500, entryHeight);
        }
        
        this.questContent.add(container);
        return entryHeight + 15;
    }

    updateQuestDisplay() {
        // Reset position
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
                'You have no active quests.' : 
                'You have not completed any quests yet.', 
                {
                    font: 'italic 20px Georgia',
                    fill: '#a89f81',
                    align: 'center'
                }
            );
            noQuestsText.setOrigin(0.5);
            this.questContent.add(noQuestsText);
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

    toggleQuestExpansion(questTitle) {
        if (this.expandedQuests.has(questTitle)) {
            this.expandedQuests.delete(questTitle);
        } else {
            this.expandedQuests.add(questTitle);
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
