import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class ScraperAmbraScene extends GameScene {
    constructor() {
        super({ key: 'ScraperAmbraScene' });
        this.isTransitioning = false; // Add flag to track transition state
    }

    preload() {
        super.preload();
        this.load.image('scraperAmbraBg', 'assets/images/backgrounds/ScraperAmbra.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set background
        const bg = this.add.image(400, 300, 'scraperAmbraBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Add fade-in effect
        this.cameras.main.fadeIn(1200, 0, 0, 0);
        
        // Position the priest at the center when entering this scene
        this.priest.x = 400;
        this.priest.y = 450; // Position on the ground
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }
        
        // Create exit back to Scraper Interior
        this.transitionManager.createTransitionZone(
            400, // x position
            550, // y position
            200, // width
            50, // height
            'down', // direction
            'ScraperInteriorScene', // target scene
            400, // walk to x
            300 // walk to y
        );
        
        // Add a hint about the exit
        const exitHint = this.add.text(400, 520, 'Back to Elevator', {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        exitHint.setOrigin(0.5);
        exitHint.setAlpha(0);
        exitHint.setDepth(10);
        
        // Show hint when hovering near the exit
        this.input.on('pointermove', (pointer) => {
            // Check if pointer is near the exit area
            if (Math.abs(pointer.x - 400) < 100 && Math.abs(pointer.y - 550) < 50) {
                exitHint.setAlpha(1);
            } else {
                exitHint.setAlpha(0);
            }
        });
        
        // Add ambient elements
        this.createAmbientElements();
        
        // Update the find_bishop quest if it exists and is not complete
        const questSystem = this.registry.get('questSystem');
        const findBishopQuest = questSystem?.getQuest('find_bishop');
        if (findBishopQuest && !findBishopQuest.isComplete) {
            questSystem.updateQuest('find_bishop', 'I\'ve reached Dr. Elphi\'s studio on floor 177-Quiet. Now I need to find clues about the Bishop.', 'reached_elphi_studio');
        }
        
        // Show a welcome notification
        this.time.delayedCall(1000, () => {
            this.showNotification('Floor 177-Quiet: Dr. Elphi\'s Studio', 0x7fff8e);
        });
    }
    
    /**
     * Create ambient elements for the scene
     */
    createAmbientElements() {
        // Add some floating spores/particles
        for (let i = 0; i < 30; i++) {
            const x = Math.random() * 800;
            const y = Math.random() * 400 + 100;
            const size = Math.random() * 3 + 1;
            
            const particle = this.add.circle(x, y, size, 0x7fff8e, 0.4);
            particle.setDepth(3);
            
            // Add floating movement
            this.tweens.add({
                targets: particle,
                x: x + (Math.random() * 100 - 50),
                y: y + (Math.random() * 60 - 30),
                alpha: { from: 0.4, to: 0.1 },
                duration: 3000 + Math.random() * 2000,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
        }
        
        // Add a subtle green glow effect to the scene
        const ambientGlow = this.add.graphics();
        ambientGlow.fillStyle(0x7fff8e, 0.05);
        ambientGlow.fillRect(0, 0, 800, 600);
        ambientGlow.setDepth(2);
        
        // Add pulsating effect to the glow
        this.tweens.add({
            targets: ambientGlow,
            alpha: { from: 0.05, to: 0.1 },
            duration: 4000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
    }
    
    get dialogContent() {
        return {
            ...super.dialogContent, // Include parent dialog content
            
            // Add scene-specific dialog content here
            elphi_studio_intro: {
                text: "Dr. Elphi's studio is eerily quiet. Workstations with glowing screens line the walls, each displaying fragments of code and strange designs. The air feels charged with creative energy, but there's no sign of Dr. Elphi herself.",
                options: [
                    { text: "Continue exploring", next: "closeDialog" }
                ]
            }
        };
    }
    
    shutdown() {
        // Clean up resources
        super.shutdown();
    }
    
    update() {
        // Call parent update for all standard mechanics
        super.update();
    }
}
