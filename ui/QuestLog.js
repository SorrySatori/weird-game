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

        // Track mouse wheel for scrolling
        this.scene.input.on('wheel', (pointer, gameObjects, deltaX, deltaY, deltaZ) => {
            if (this.questPanel.visible && this.questContent) {
                const scrollSpeed = 0.5;
                const newY = Phaser.Math.Clamp(
                    this.questContent.y - deltaY * scrollSpeed,
                    -this.contentHeight + 400, // Allow scrolling up to content height minus visible area
                    0 // Don't scroll past the top
                );
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
        // Create container for the quest log
        this.questPanel = this.scene.add.container(400, 300);
        this.questPanel.setDepth(200);
        this.questPanel.setScrollFactor(0);
        this.questPanel.visible = false;
        
        // Create background
        const bg = this.scene.add.graphics();
        bg.fillStyle(0x0a2712, 0.95);
        bg.fillRect(-200, -250, 400, 500);
        bg.lineStyle(2, 0x7fff8e);
        bg.strokeRect(-200, -250, 400, 500);
        
        // Create tab buttons
        const activeTabStyle = { font: 'bold 20px Arial', fill: '#7fff8e' };
        const inactiveTabStyle = { font: '20px Arial', fill: '#5c9b6b' };
        
        this.activeTab = 'active';
        
        // Create tab backgrounds
        const tabBg = this.scene.add.graphics();
        tabBg.fillStyle(0x0a2712);
        tabBg.fillRect(-200, -250, 190, 35); // Active tab background
        tabBg.fillStyle(0x081d0d);
        tabBg.fillRect(0, -250, 190, 35); // Finished tab background
        
        this.activeTabButton = this.scene.add.text(-180, -240, 'Active Quests', activeTabStyle);
        this.finishedTabButton = this.scene.add.text(20, -240, 'Finished Quests', inactiveTabStyle);
        
        this.activeTabButton.setInteractive({ useHandCursor: true });
        this.finishedTabButton.setInteractive({ useHandCursor: true });
        
        this.activeTabButton.on('pointerdown', () => {
            if (this.activeTab !== 'active') {
                this.activeTab = 'active';
                this.activeTabButton.setStyle(activeTabStyle);
                this.finishedTabButton.setStyle(inactiveTabStyle);
                tabBg.clear();
                tabBg.fillStyle(0x0a2712);
                tabBg.fillRect(-200, -250, 190, 35);
                tabBg.fillStyle(0x081d0d);
                tabBg.fillRect(0, -250, 190, 35);
                this.updateQuestDisplay();
            }
        });
        
        this.finishedTabButton.on('pointerdown', () => {
            if (this.activeTab !== 'finished') {
                this.activeTab = 'finished';
                this.finishedTabButton.setStyle(activeTabStyle);
                this.activeTabButton.setStyle(inactiveTabStyle);
                tabBg.clear();
                tabBg.fillStyle(0x081d0d);
                tabBg.fillRect(-200, -250, 190, 35);
                tabBg.fillStyle(0x0a2712);
                tabBg.fillRect(0, -250, 190, 35);
                this.updateQuestDisplay();
            }
        });
        
        // Add title below tabs
        const title = this.scene.add.text(0, -200, 'Quest Log', {
            font: '24px Arial',
            fill: '#7fff8e',
            align: 'center'
        });
        title.setOrigin(0.5);
        
        // Create mask for scrollable content
        const maskGraphics = this.scene.add.graphics();
        maskGraphics.fillStyle(0xffffff);
        maskGraphics.fillRect(200, 50, 360, 400); // Mask dimensions
        maskGraphics.setVisible(false); // Hide the mask graphics while keeping the mask effect
        
        // Create quest content container
        this.questContent = this.scene.add.container(0, -180);
        const mask = maskGraphics.createGeometryMask();
        this.questContent.setMask(mask);
        
        // Add all elements to panel
        this.questPanel.add([bg, tabBg, this.activeTabButton, this.finishedTabButton, title, this.questContent]);
        
        // Add close button
        const closeButton = this.scene.add.text(170, -240, 'X', {
            font: '20px Arial',
            fill: '#7fff8e'
        });
        closeButton.setInteractive({ useHandCursor: true });
        closeButton.on('pointerdown', () => {
            this.hideQuestLog();
        });
        this.questPanel.add(closeButton);
    }

    createQuestEntry(quest, yOffset) {
        const container = this.scene.add.container(-180, yOffset);
        const isExpanded = this.expandedQuests.has(quest.title);

        // Create header with toggle button
        const toggleButton = this.scene.add.text(-20, 0, isExpanded ? '▼' : '▶', {
            font: 'bold 16px Arial',
            fill: '#7fff8e'
        });

        // Quest title (header)
        const title = this.scene.add.text(0, 0, quest.title, {
            font: 'bold 20px Arial',
            fill: quest.isComplete ? '#00ff00' : '#7fff8e',
            wordWrap: { width: 340 }
        });

        // Make header interactive
        const headerZone = this.scene.add.zone(-20, 0, 380, 30);
        headerZone.setOrigin(0);
        headerZone.setInteractive({ useHandCursor: true });
        headerZone.on('pointerdown', () => {
            this.toggleQuestExpansion(quest.title);
        });

        container.add([toggleButton, title, headerZone]);
        let height = 40;

        // Add description and updates if expanded
        if (isExpanded) {
            const desc = this.scene.add.text(0, 35, quest.description, {
                font: '16px Arial',
                fill: '#7fff8e',
                wordWrap: { width: 340 },
                lineSpacing: 5
            });
            container.add(desc);
            height += desc.height + 15;

            // Add updates
            let updateY = height;
            quest.updates.forEach(update => {
                const updateText = this.scene.add.text(20, updateY, '• ' + update.text, {
                    font: '14px Arial',
                    fill: '#5c9b6b',
                    wordWrap: { width: 320 },
                    lineSpacing: 5
                });
                container.add(updateText);
                updateY += updateText.height + 10;
            });
            height = updateY;
        }

        this.questContent.add(container);
        return height;
    }

    updateQuestDisplay() {
        // Clear existing content
        this.questContent.removeAll(true);
        
        // Get all quests
        const quests = this.questSystem.getAllQuests();
        
        let yOffset = 0;
        quests.forEach(quest => {
            // Only show quests based on the active tab
            if ((this.activeTab === 'active' && !quest.isComplete) || 
                (this.activeTab === 'finished' && quest.isComplete)) {
                const height = this.createQuestEntry(quest, yOffset);
                yOffset += height + 20; // Add spacing between quests
            }
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
        this.updateQuestDisplay();
    }

    hideQuestLog() {
        this.questPanel.visible = false;
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
