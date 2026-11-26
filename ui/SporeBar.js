import LanguageSystem from '../systems/LanguageSystem.js';
import { drawPixelFrame, UI_FONT, UI_SMALL } from '../utils/pixelFrame.js';

let SPOREBAR_ID = 1;
// A glass ampule lying in a weathered bronze cradle, the spore fluid inside (tools/artgen/spore_bar.py): moss-mint while
// there are plenty, ochre when they run low, rust when they're nearly gone. Same palette as the G/D medallion.
const W = 160, H = 24;
const FILL = { x: 10, y: 6, w: 140, h: 12 };       // the tube's inside
const STATES = [                                    // [from %, fill row, the meniscus' colour]
    [50, 0, 0x9ad0a0], [25, 1, 0xb8a25c], [0, 2, 0xb06a3a],
];
export default class SporeBar {

    constructor(scene, x, y) {
        this.id = SPOREBAR_ID++;
        this.lang = LanguageSystem.getInstance();
        this.scene = scene;
        
        // Create container for the spore bar
        this.container = scene.add.container(x, y);
        
        // The cradle and the empty tube, the fluid (cropped to the level), its edge, the glass's shine over it;
        // `background` is only the hover area
        this.frame = scene.add.image(0, 0, 'sporeBarFrame').setOrigin(0, 0);
        this.background = scene.add.rectangle(0, 0, W, H, 0x000000, 0).setOrigin(0, 0);
        this.fillBar = scene.add.sprite(FILL.x, FILL.y, 'sporeBarFill', 0).setOrigin(0, 0);
        this.meniscus = scene.add.rectangle(FILL.x, FILL.y, 1, FILL.h, STATES[0][2], 0.55).setOrigin(0, 0);
        this.glass = scene.add.image(0, 0, 'sporeBarGlass').setOrigin(0, 0);

        // The label under it, the value on the glass
        this.label = scene.add.text(W / 2, H + 4, this.lang.t('sporeBar.label'), {
            fontFamily: UI_FONT,
            fontSize: UI_SMALL,
            fill: '#c2cfb0',
            align: 'center'
        });
        this.label.setOrigin(0.5, 0);
        this.valueText = scene.add.text(W / 2, H / 2, '100%', {
            fontFamily: UI_FONT,
            fontSize: UI_SMALL,
            fill: '#f2f0e4',
            stroke: '#0a0f0c',
            strokeThickness: 3,
            align: 'center'
        });
        this.valueText.setOrigin(0.5, 0.5);

        // Add everything to the container
        this.container.add([this.frame, this.background, this.fillBar, this.meniscus, this.glass, this.label, this.valueText]);
        
        // Set high depth to ensure it's always visible
        this.container.setDepth(1000).setScrollFactor(0);   // pinned to the screen like the rest of the HUD
        
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
        // The tooltip's plate (utils/pixelFrame.js)
        this.tooltipBg = this.scene.add.graphics();
        drawPixelFrame(this.tooltipBg, 0, 44, 200, 80);   // below the SPORES label
        
        // Create text for displaying tooltip
        this.tooltipText = this.scene.add.text(10, 52, 
            this.lang.t('sporeBar.tooltipTitle') + '\n' +
            this.lang.t('sporeBar.tooltipDesc') + '\n' +
            this.lang.t('sporeBar.tooltipCurrent', { current: 0, max: 0 }), {
            fontFamily: UI_FONT,
            fontSize: UI_SMALL,
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
        
        // The fluid up to the level (whole pixels), its colour by how much is left, a lighter edge where it ends
        const ratio = Math.max(0, Math.min(1, currentSpores / maxSpores));
        const w = Math.round(ratio * FILL.w);
        const [, row, edge] = STATES.find(([from]) => ratio * 100 >= from) || STATES[STATES.length - 1];
        this.fillBar.setFrame(row).setCrop(0, 0, w, FILL.h);
        this.meniscus.setFillStyle(edge, 0.55).setPosition(FILL.x + w - 1, FILL.y).setVisible(w > 1 && w < FILL.w);

        this.valueText.setText(`${Math.round(currentSpores)}/${maxSpores}`);
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
        this.meniscus = null;
        this.valueText = null;
        this.background = null;
        this.label = null;
        this.tooltipBg = null;
        this.tooltipText = null;
        this.container = null;
    }
}
