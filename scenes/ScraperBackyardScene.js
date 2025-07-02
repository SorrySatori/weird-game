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
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set background
        const bg = this.add.image(400, 300, 'scraperBackyardBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Position the priest in the scene
        if (this.priest) {
            this.priest.x = 200;
            this.priest.y = 470;
            this.priest.setOrigin(0.5, 1);
            this.priest.play('idle');
            
            // Update priest's glow position
            if (this.priestGlow) {
                this.priestGlow.x = this.priest.x;
                this.priestGlow.y = this.priest.y;
            }
        }

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
            if (this.isTransitioning) return;
            this.isTransitioning = true;
            
            // Move priest to exit
            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: 50,
                y: 470,
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('ScraperInteriorScene');
                    });
                }
            });
        });
        
        // Add abandoned bus
        this.abandonedBus = this.add.image(600, 350, 'abandonedBus');
        this.abandonedBus.setScale(0.8);
        this.abandonedBus.setDepth(5);
        this.abandonedBus.setInteractive({ useHandCursor: true });
        
        // Add bus hover hint
        const busText = this.add.text(600, 280, "Abandoned Bus", {
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
            // Check if pointer is near the bus
            if (Math.abs(pointer.x - 600) < 100 && Math.abs(pointer.y - 350) < 100) {
                busText.setAlpha(1);
            } else {
                busText.setAlpha(0);
            }
        });
        
        // Add bus click handler
        this.abandonedBus.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;
            
            // Move priest to bus
            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: 500,
                y: 470,
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('AbandonedBusScene');
                    });
                }
            });
        });
        
        // Add glow effect to the bus
        const busGlow = this.add.graphics();
        busGlow.fillStyle(0x7fff8e, 0.2);
        busGlow.fillCircle(600, 350, 60);
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
            this.journalSystem.addEntry({
                id: 'scraper_backyard',
                title: 'Scraper Backyard',
                content: 'Behind the Scraper building lies an overgrown yard filled with the remnants of the old world. Most notable is an abandoned bus, its metal frame now serving as a trellis for strange fungal growths. There\'s something ominous about it, as if it holds secrets from the time of the Great Fruiting.',
                category: 'locations',
                metadata: { location: 'Scraper Backyard' }
            });
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
