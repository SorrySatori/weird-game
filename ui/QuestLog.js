export default class QuestLog {
    constructor(scene, x, y) {
        this.scene = scene;
        this.questSystem = scene.questSystem;
        
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
        
        // Set depth
        this.buttonContainer.setDepth(100);
    }

    createQuestPanel() {
        // Create container for the panel
        this.panel = this.scene.add.container(400, 300);
        this.panel.setDepth(1000);
        this.panel.visible = false;
        
        // Create semi-transparent background
        const bg = this.scene.add.graphics();
        bg.fillStyle(0x000000, 0.9);
        bg.fillRect(-300, -200, 600, 400);
        bg.lineStyle(2, 0x2a623d);
        bg.strokeRect(-300, -200, 600, 400);
        
        // Add title
        const title = this.scene.add.text(0, -180, 'QUEST LOG', {
            font: 'bold 24px Arial',
            fill: '#7fff8e',
            align: 'center'
        });
        title.setOrigin(0.5);
        
        // Add close button
        const closeBtn = this.scene.add.text(270, -190, 'X', {
            font: 'bold 20px Arial',
            fill: '#7fff8e'
        });
        closeBtn.setInteractive({ useHandCursor: true });
        closeBtn.on('pointerdown', () => {
            this.hideQuestLog();
        });
        
        // Create quest content container
        this.questContent = this.scene.add.container(0, 0);
        
        // Add all elements to panel
        this.panel.add([bg, title, closeBtn, this.questContent]);
    }

    updateQuestDisplay() {
        // Clear existing content
        this.questContent.removeAll();
        
        const quests = this.questSystem.getAllQuests();
        let yOffset = -140;
        
        quests.forEach(quest => {
            // Add quest title
            const title = this.scene.add.text(-280, yOffset, quest.title, {
                font: 'bold 16px Arial',
                fill: quest.isComplete ? '#888888' : '#7fff8e'
            });
            
            // Add quest description
            const description = this.scene.add.text(-280, yOffset + 25, quest.description, {
                font: '14px Arial',
                fill: '#ffffff',
                wordWrap: { width: 540 },
                lineSpacing: 5
            });
            
            // Add updates
            let updateOffset = yOffset + description.height + 35;
            quest.updates.forEach(update => {
                const updateText = this.scene.add.text(-260, updateOffset, '• ' + update.text, {
                    font: '12px Arial',
                    fill: '#aaaaaa',
                    wordWrap: { width: 520 },
                    lineSpacing: 5
                });
                this.questContent.add(updateText);
                updateOffset += updateText.height + 10;
            });
            
            this.questContent.add([title, description]);
            yOffset = updateOffset + 20;
        });
    }

    toggleQuestLog() {
        if (this.panel.visible) {
            this.hideQuestLog();
        } else {
            this.showQuestLog();
        }
    }

    showQuestLog() {
        this.panel.visible = true;
        this.updateQuestDisplay();
    }

    hideQuestLog() {
        this.panel.visible = false;
    }

    cleanup() {
        this.questSystem.unsubscribe(this.updateQuestDisplay.bind(this));
        if (this.buttonContainer) {
            this.buttonContainer.destroy();
        }
        if (this.panel) {
            this.panel.destroy();
        }
    }
}
