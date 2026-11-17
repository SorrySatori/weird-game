import LanguageSystem from '../systems/LanguageSystem.js';
import { drawPixelFrame, UI_FONT, UI_SMALL } from '../utils/pixelFrame.js';

export default class GrowthDecayIndicator {
    constructor(scene, x, y) {
        this.scene = scene;
        this.lang = LanguageSystem.getInstance();
        
        // Create container for the indicator
        this.container = scene.add.container(x, y);
        
        // The medallion (native 100×100 pixel art, scale 1): its field splits between growth and decay
        this.indicator = scene.add.image(0, 0, 'growthDecay', 5);
        this.indicator.setOrigin(0, 0);
        
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
        
        // Initialize with current values to maintain visual state across scenes
        this.updateDisplay(system.getGrowth(), system.getDecay());
    }
    
    createPopupMenu() {
        // A pixel plate (utils/pixelFrame.js) with the values in the UI font
        this.menuBg = this.scene.add.graphics();
        drawPixelFrame(this.menuBg, 110, 4, 132, 44);
        
        // Create text for displaying values
        this.menuText = this.scene.add.text(122, 12, '', {
            fontFamily: UI_FONT,
            fontSize: UI_SMALL,
            fill: '#c8e6d0',
            align: 'left',
            lineSpacing: 4
        });
        
        this.updateMenuText();
    }
    
    updateMenuText() {
        const system = this.scene.growthDecaySystem;
        this.menuText.setText(
            this.lang.t('ui.growthLabel', { value: system.getGrowth() }) + '\n' + this.lang.t('ui.decayLabel', { value: system.getDecay() })
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
        // The green share of the field follows growth (decay = 100 - growth): frame k = growth 10·k %
        this.indicator.setFrame(Phaser.Math.Clamp(Math.round(growth / 10), 0, 10));
        
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
