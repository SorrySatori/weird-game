import LanguageSystem from '../systems/LanguageSystem.js';

let SPOREBAR_ID = 1;
export default class SporeBar {

    constructor(scene, x, y) {
        this.id = SPOREBAR_ID++;
        this.lang = LanguageSystem.getInstance();
        this.scene = scene;
        
        // Create container for the spore bar
        this.container = scene.add.container(x, y);
        
        // Create the background bar
        this.background = scene.add.rectangle(0, 0, 150, 20, 0x222222, 0.8);
        this.background.setOrigin(0, 0);
        this.background.setStrokeStyle(1, 0x7fff8e);
        
        // Create the fill bar (starts at 100%)
        this.fillBar = scene.add.rectangle(2, 2, 146, 16, 0x7fff8e, 0.7);
        this.fillBar.setOrigin(0, 0);
        
        // Create label
        this.label = scene.add.text(75, 24, this.lang.t('sporeBar.label'), {
            fontSize: '14px',
            fill: '#7fff8e',
            align: 'center'
        });
        this.label.setOrigin(0.5, 0);
        
        // Create value text
        this.valueText = scene.add.text(75, 10, '100%', {
            fontSize: '12px',
            fill: '#ffffff',
            align: 'center'
        });
        this.valueText.setOrigin(0.5, 0.5);
        
        // Add everything to the container
        this.container.add([this.background, this.fillBar, this.label, this.valueText]);
        
        // Set high depth to ensure it's always visible
        this.container.setDepth(1000);
        
        // Make the bar interactive for showing more details
        this.background.setInteractive({ useHandCursor: true });
        
        // Create tooltip (initially hidden)
        this.createTooltip();
        this.hideTooltip();
        
        // Add hover handlers
        this.background.on('pointerover', () => {
            this.showTooltip();
        });
        
        this.background.on('pointerout', () => {
            this.hideTooltip();
        });
        
        // Subscribe to system updates
        if (scene.sporeSystem) {
            this.boundUpdateDisplay = this.updateDisplay.bind(this);
            scene.sporeSystem.subscribe(this.boundUpdateDisplay);
            // Immediately sync UI to current spore level
            this.updateDisplay(scene.sporeSystem.getSporeLevel(), scene.sporeSystem.getMaxSpores());
        }

    }
    
    createTooltip() {
        // Create semi-transparent background for tooltip
        this.tooltipBg = this.scene.add.rectangle(0, 30, 200, 80, 0x000000, 0.8);
        this.tooltipBg.setOrigin(0, 0);
        this.tooltipBg.setStrokeStyle(1, 0x7fff8e);
        
        // Create text for displaying tooltip
        this.tooltipText = this.scene.add.text(10, 40, 
            this.lang.t('sporeBar.tooltipTitle') + '\n' +
            this.lang.t('sporeBar.tooltipDesc') + '\n' +
            this.lang.t('sporeBar.tooltipCurrent', { current: 0, max: 0 }), {
            fontSize: '12px',
            fill: '#ffffff',
            align: 'left',
            wordWrap: { width: 180 }
        });
        
        // Add to container
        this.container.add([this.tooltipBg, this.tooltipText]);
    }
    
    showTooltip() {
        // Update tooltip text with current values
        if (this.scene.sporeSystem) {
            const current = this.scene.sporeSystem.getSporeLevel();
            const max = this.scene.sporeSystem.getMaxSpores();
            const tooltipContent = this.lang.t('sporeBar.tooltipTitle') + '\n' +
                this.lang.t('sporeBar.tooltipDesc') + '\n' +
                this.lang.t('sporeBar.tooltipCurrent', { current, max });
            this.tooltipText.setText(tooltipContent);
        }
        
        this.tooltipBg.setVisible(true);
        this.tooltipText.setVisible(true);
    }
    
    hideTooltip() {
        this.tooltipBg.setVisible(false);
        this.tooltipText.setVisible(false);
    }
    
    updateDisplay(currentSpores, maxSpores = 100) {
        // Defensive: If UI elements are destroyed, do nothing
        if (!this.fillBar || !this.valueText) return;
        
        // Update the fill bar width based on spore level
        const maxWidth = 146;
        const fillWidth = Math.max(0, (currentSpores / maxSpores) * maxWidth);
        this.fillBar.width = fillWidth;
        
        // Update the text
        const percentage = Math.round((currentSpores / maxSpores) * 100);
        this.valueText.setText(`${Math.round(currentSpores)}/${maxSpores}`);
        
        // Change color based on percentage
        if (percentage < 25) {
            this.fillBar.fillColor = 0xff3333; // Red when low
        } else if (percentage < 50) {
            this.fillBar.fillColor = 0xffaa33; // Orange when medium
        } else {
            this.fillBar.fillColor = 0x7fff8e; // Green when high
        }
    }
    
    cleanup() {
        // Unsubscribe from system updates
        const system = this.scene.sporeSystem;
        if (system && this.boundUpdateDisplay) {
            system.unsubscribe(this.boundUpdateDisplay);
        }
        
        // Destroy all UI elements
        if (this.container) {
            this.container.destroy();
        }
        // Null UI refs to help GC and avoid zombie calls
        this.fillBar = null;
        this.valueText = null;
        this.background = null;
        this.label = null;
        this.tooltipBg = null;
        this.tooltipText = null;
        this.container = null;
    }
}
