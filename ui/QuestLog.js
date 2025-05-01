export default class QuestLog {
    constructor(scene, x = 750, y = 50) {
        this.scene = scene;
        this.questSystem = scene.registry.get('questSystem');
        
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
        
        // Add title
        const title = this.scene.add.text(0, -220, 'Quest Log', {
            font: '24px Arial',
            fill: '#7fff8e',
            align: 'center'
        });
        title.setOrigin(0.5);
        
        // Create quest content container
        this.questContent = this.scene.add.container(0, -180);
        
        // Add all elements to panel
        this.questPanel.add([bg, title, this.questContent]);
        
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

    updateQuestDisplay() {
        // Clear existing content
        this.questContent.removeAll(true);
        
        // Get all quests
        const quests = this.questSystem.getAllQuests();
        
        let yOffset = 0;
        quests.forEach(quest => {
            // Quest title
            const title = this.scene.add.text(-180, yOffset, quest.title, {
                font: '18px Arial',
                fill: quest.isComplete ? '#00ff00' : '#7fff8e',
                wordWrap: { width: 360 }
            });
            
            // Quest description
            const desc = this.scene.add.text(-180, yOffset + 25, quest.description, {
                font: '14px Arial',
                fill: '#7fff8e',
                wordWrap: { width: 360 }
            });
            
            this.questContent.add([title, desc]);
            
            // Add updates if any
            let updateOffset = yOffset + 50;
            quest.updates.forEach(update => {
                const updateText = this.scene.add.text(-160, updateOffset, '• ' + update.text, {
                    font: '12px Arial',
                    fill: '#5c9b6b',
                    wordWrap: { width: 340 }
                });
                this.questContent.add(updateText);
                updateOffset += 20;
            });
            
            yOffset = updateOffset + 20;
        });
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
