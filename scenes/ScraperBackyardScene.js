import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';

export default class ScraperBackyardScene extends GameScene {
    constructor() {
        super({ key: 'ScraperBackyardScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    preload() {
        super.preload();
        this.load.image('scraperBackyardBg', 'assets/images/backgrounds/ScraperBackyard.png');
        this.load.image('abandonedBus', 'assets/images/objects/abandoned_bus.png');
        this.load.image('exitArea', 'assets/images/ui/arrow.png');
        this.load.image('door', 'assets/images/ui/door.png');
    }

    create() {
        super.create();
        
        const bg = this.add.image(400, 300, 'scraperBackyardBg');
        bg.setDisplaySize(800, 750); 
        bg.setPosition(400, 180);
        bg.setDepth(-1);
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this); 

        // Add exit back to ScraperInteriorScene
        this.exitArea = this.add.image(100, 470, 'exitArea')
            .setDisplaySize(120, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);
        
        // Add exit hover hint
        const exitText = this.add.text(100, 400, "Return Inside", {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        exitText.setOrigin(0.5);
        exitText.setAlpha(0);
        exitText.setDepth(10);
        
        // Show hint when hovering near the exit
        this.input.on('pointermove', (pointer) => {
            // Check if pointer is near the exit area
            if (Math.abs(pointer.x - 100) < 60 && Math.abs(pointer.y - 470) < 100) {
                exitText.setAlpha(1);
            } else {
                exitText.setAlpha(0);
            }
        });
        
        // Add exit click handler
        this.exitArea.on('pointerdown', () => {
            // Use the SceneTransitionManager to handle the transition
            if (!this.transitionManager) {
                this.transitionManager = new SceneTransitionManager(this);
            }
            this.transitionManager.handleSceneTransition('ScraperInteriorScene', 50, 470);
        });
        
        // Add abandoned bus - adjusted position for the zoomed out background
        this.abandonedBus = this.add.image(400, 420, 'door');
        this.abandonedBus.setScale(1.0); // Increased scale for better visibility
        this.abandonedBus.setDepth(5);
        this.abandonedBus.setInteractive({ useHandCursor: true });
        
        // Add bus hover hint - adjusted position
        const busText = this.add.text(400, 350, "Abandoned Bus", {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        busText.setOrigin(0.5);
        busText.setAlpha(0);
        busText.setDepth(10);
        
        // Show hint when hovering near the bus
        this.input.on('pointermove', (pointer) => {
            // Check if pointer is near the bus - adjusted hit area for new position
            if (Math.abs(pointer.x - 400) < 100 && Math.abs(pointer.y - 420) < 100) {
                busText.setAlpha(1);
            } else {
                busText.setAlpha(0);
            }
        });
        
        // Add bus click handler
        this.abandonedBus.on('pointerdown', () => {
            // Use the SceneTransitionManager to handle the transition
            if (!this.transitionManager) {
                this.transitionManager = new SceneTransitionManager(this);
            }
            this.transitionManager.handleSceneTransition('AbandonedBusScene', 350, 500);
        });
        
        // Add glow effect directly onto the bus
        const busGlow = this.add.graphics();
        busGlow.fillStyle(0x7fff8e, 0.25);
        // Create an elliptical glow that covers the bus shape
        busGlow.fillEllipse(400, 420, 120, 70); // Shaped to match the bus dimensions
        busGlow.setDepth(4);
        
        // Add pulsating animation to the glow
        this.tweens.add({
            targets: busGlow,
            alpha: { from: 0.15, to: 0.3 },
            duration: 2000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Add journal entry about the backyard if not already added
        if (this.journalSystem && !this.journalSystem.hasEntry('scraper_backyard')) {
            this.addJournalEntry(
                'scraper_backyard',
                'Scraper Backyard',
                'Behind the Scraper building lies an overgrown yard filled with the remnants of the old world. Most notable is an abandoned bus, its metal frame now serving as a trellis for strange fungal growths. There\'s something ominous about it, as if it holds secrets from the time of the Great Fruiting.',
                this.journalSystem.categories.PLACES,
                { location: 'Scraper Backyard' }
            );
        }

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
    }

    get dialogContent() {
        const parentContent = super.dialogContent;
        
        const backyardContent = {
            // No specific dialog for this scene yet
        };
        
        return { ...parentContent, ...backyardContent };
    }

    update() {
        super.update();
    }
}
