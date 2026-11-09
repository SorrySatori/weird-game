import { notePlace } from '../utils/places.js';
import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import { preloadGDProps, placeProps } from '../utils/GDProps.js';

export default class Shed521GateScene extends GameScene {
    constructor() {
        super({ key: 'Shed521GateScene' });
        this.isTransitioning = false; // Add flag to track transition state
    }

    preload() {
        super.preload();
        this.preloadMusic('shedLoop');
        this.load.image('Shed521GateBg', 'assets/images/backgrounds/Shed521_gate.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        this.load.image('gateBarrier', 'assets/images/props/gate_barrier.png');
        preloadGDProps(this); // the burning barrel by the lamp
        // Audio is already loaded in GameScene's preload
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        notePlace(this, 'place_shed_521');   // the journal's Places tab, on the first visit
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Play market theme
        this.playSceneMusic('shedLoop', { resume: true });
        
        // The gate yard (native 1067×600: tools/artgen/gate_bg.py — the queue for mutation forms, the Floors door on the right)
        const bg = this.add.image(this.scale.width / 2, 300, 'Shed521GateBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        
        // The background paints the yard's setts; drop the generic ground strip
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }
        
        // A barrel fire by the lamp post (animated, with its warm glow)
        placeProps(this, [{ prop: 'fire', x: 716, y: 500 }]);

        this.createGateBarrier();

        // Position the priest at the right side when entering this scene
        this.priest.x = 750;
        this.priest.y = 470; // Position on the ground
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }
        
        // Create transition zones using SceneTransitionManager
        
        // Exit to Floors Scene (right side of the screen)
        this.floorsZone = this.transitionManager.createTransitionZone(
            750, // x position
            470, // y position
            50,  // width
            200, // height
            'right', // direction
            'Shed521FloorsScene', // target scene
            750, // walk to x
            470, // walk to y
            'Back to the Main Building' // clearer than the Floors' location name
        );
        
        // Exit to Courtyard Scene (left side of the screen)
        this.courtyardZone = this.transitionManager.createTransitionZone(
            50,  // x position
            470, // y position
            50,  // width
            200, // height
            'left', // direction
            'ShedCourtyard', // target scene
            50,  // walk to x
            470  // walk to y
        );
        
        // Remove the NPC if it exists
        if (this.stranger) {
            this.stranger.destroy();
        }
    }

    /**
     * The boom barrier shut across the gate (tools/artgen/gate_bg.py renders it as its own sprite, placed pixel-exact
     * on the background) -- it tells the player the street beyond is closed. A click gets one line from the clerk in
     * the forms kiosk: a speech bubble, no dialog, the way the people inside the Shed talk (utils/AmbientNpc.js).
     */
    createGateBarrier() {
        const barrier = this.add.image(474, 377, 'gateBarrier').setOrigin(0, 0).setDepth(0);
        // the arm is only a few pixels thick: its whole frame is the hotspot, with a strip of air above it
        barrier.setInteractive({
            hitArea: new Phaser.Geom.Rectangle(0, -8, barrier.width, barrier.height + 8),
            hitAreaCallback: Phaser.Geom.Rectangle.Contains,
            useHandCursor: true,
        });

        const name = this.add.text(barrier.x + barrier.width / 2, barrier.y - 18, this.t('ambient.gate_barrier.name'), {
            fontSize: '13px', fill: '#7fff8e', backgroundColor: 'rgba(0,0,0,0.5)', padding: { x: 5, y: 2 }
        }).setOrigin(0.5).setDepth(100).setAlpha(0);
        barrier.on('pointerover', () => name.setAlpha(1));
        barrier.on('pointerout', () => name.setAlpha(0));

        const kiosk = { x: 456, y: 337 };   // the roof of the forms kiosk left of the gate (its hatch is behind the queue's last head)
        let next = 0;
        let bubble = null;
        barrier.on('pointerdown', (pointer, localX, localY, event) => {
            event.stopPropagation(); // the priest stays put
            if (this.dialogVisible || bubble?.active) return;
            const lines = this.t('ambient.gate_barrier.lines');
            if (!Array.isArray(lines) || !lines.length) return;
            name.setAlpha(0);
            bubble = this.showSpeechBubble(kiosk, lines[next++ % lines.length], { duration: 3800, offsetY: 0 });
        });
    }

    shutdown() {
        // Restore background music when leaving the scene
        this.restoreBackgroundMusic();
        super.shutdown();
    }

    update() {
        // Call parent update for all standard mechanics
        super.update();
    }
    
    shutdown() {
        this.restoreBackgroundMusic();
        super.shutdown();
    }
}
