export default class GrowthDecayIndicator {
    constructor(scene, x, y) {
        this.scene = scene;
        
        // Create container for the indicator
        this.container = scene.add.container(x, y);
        
        // Load and add the image
        this.indicator = scene.add.image(0, 0, 'growthDecay');
        this.indicator.setOrigin(0, 0);
        this.indicator.setDisplaySize(100, 100); // Reasonable size for corner display
        
        // Make it interactive
        this.indicator.setInteractive({ useHandCursor: true });
        
        // Create the popup menu (initially hidden)
        this.createPopupMenu();
        
        // Add everything to the container
        this.container.add([this.indicator, this.menuBg, this.menuText]);
        
        // Set high depth to ensure it's always visible
        this.container.setDepth(1000);
        
        // Initially hide the menu
        this.hideMenu();
        
        // Add hover handlers
        this.indicator.on('pointerover', () => {
            this.showMenu();
        });
        
        this.indicator.on('pointerout', () => {
            this.hideMenu();
        });
        
        // Subscribe to system updates
        const system = scene.growthDecaySystem;
        system.subscribe(this.updateDisplay.bind(this));
    }
    
    createPopupMenu() {
        // Create semi-transparent background for menu
        this.menuBg = this.scene.add.rectangle(110, 0, 150, 80, 0x000000, 0.8);
        this.menuBg.setOrigin(0, 0);
        
        // Create text for displaying values
        this.menuText = this.scene.add.text(120, 10, '', {
            fontSize: '16px',
            fill: '#ffffff',
            align: 'left'
        });
        
        this.updateMenuText();
    }
    
    updateMenuText() {
        const system = this.scene.growthDecaySystem;
        this.menuText.setText(
            `Growth: ${system.getGrowth()}%\nDecay: ${system.getDecay()}%`
        );
    }
    
    toggleMenu() {
        if (this.menuBg.visible) {
            this.hideMenu();
        } else {
            this.showMenu();
        }
    }
    
    showMenu() {
        this.updateMenuText();
        this.menuBg.setVisible(true);
        this.menuText.setVisible(true);
    }
    
    hideMenu() {
        this.menuBg.setVisible(false);
        this.menuText.setVisible(false);
    }
    
    updateDisplay(growth, decay) {
        // Update the indicator's tint based on the balance
        // More growth = greener, more decay = browner
        const greenTint = Math.floor((growth / 100) * 255);
        const brownTint = Math.floor((decay / 100) * 255);
        this.indicator.setTint(
            Phaser.Display.Color.GetColor(
                brownTint,
                greenTint,
                0
            )
        );
        
        // Update menu text if visible
        if (this.menuBg.visible) {
            this.updateMenuText();
        }
    }
    
    cleanup() {
        // Unsubscribe from system updates
        const system = this.scene.growthDecaySystem;
        if (system) {
            system.unsubscribe(this.updateDisplay.bind(this));
        }
        
        // Destroy all UI elements
        if (this.container) {
            this.container.destroy();
            this.container = null;
        }
        if (this.indicator) {
            this.indicator.destroy();
            this.indicator = null;
        }
        if (this.menuBg) {
            this.menuBg.destroy();
            this.menuBg = null;
        }
        if (this.menuText) {
            this.menuText.destroy();
            this.menuText = null;
        }
    }
}
