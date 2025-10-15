import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';

export default class ScraperScene extends GameScene {
    constructor() {
        super({ key: 'ScraperScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    get dialogContent() {
        return {
            ...super.dialogContent, // Include parent dialog content for symbiont dialogs
            // Add ScraperScene specific dialogs here if needed
        };
    }

    preload() {
        super.preload();
        this.load.image('scraperBg', 'assets/images/backgrounds/Scraper1140.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set scraper background
        const bg = this.add.image(400, 300, 'scraperBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        this.playSceneMusic('genericMusic');

        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Add invisible clickable exit area at the left side
        this.exitArea = this.add.image(50, 470, 'exitArea')
            .setDisplaySize(40, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);
        
        // Position the priest at the right side when entering
        this.priest.x = 700;
        this.priest.y = 470;
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
        
        // Add entrance to the Scraper building interior
        const scraperEntrance = this.add.image(400, 470, 'exitArea')
            .setDisplaySize(100, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        scraperEntrance.setDepth(5);
        
        // Add a hint about the scraper entrance
        const scraperHint = this.add.text(400, 380, 'Enter Scraper', {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        scraperHint.setOrigin(0.5);
        scraperHint.setAlpha(0);
        scraperHint.setDepth(10);
        
        // Show hint when hovering near the entrance
        this.input.on('pointermove', (pointer) => {
            // Check if pointer is near the scraper entrance
            if (Math.abs(pointer.x - 400) < 50 && Math.abs(pointer.y - 470) < 100) {
                scraperHint.setAlpha(1);
            } else {
                scraperHint.setAlpha(0);
            }
        });
        
        // Add scraper entrance click handler
        scraperEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;
            
            // Add journal entry about the Scraper
            if (!this.hasJournalEntry('scraper_building')) {
                this.addJournalEntry(
                    'scraper_building',
                    'The Scraper',
                    'The imposing structure known as "The Scraper" rises above the surrounding buildings. Once a corporate headquarters called Nexicorp Tower, it now stands as a living monument to transformation. Its lower floors house those who remember the old ways, while the middle floors have become wild ecosystems. No one knows how many floors it has. Elevators refuse to count them. Tenants report missing levels, duplicate floors, and entire wings dedicated to unrecognized languages or species. Most assume the building self-generates new strata in response to emotional entropy.',
                    this.journalSystem.categories.PLACES,
                    { location: 'The Scraper, Upper Morkezela' }
                );
            }
            
            // Move priest to scraper entrance
            const priest = this.priest;
            if (!priest) {
                // If priest doesn't exist, just transition immediately
                this.cameras.main.fadeOut(800, 0, 0, 0);
                this.cameras.main.once('camerafadeoutcomplete', () => {
                    this.scene.start('ScraperInteriorScene');
                    this.isTransitioning = false;
                });
                return;
            }
            
            // Create a variable to track if the tween completed
            let tweenCompleted = false;
            
            // Play walk animation
            priest.play('walk');
            
            // Kill any existing tweens
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: 400,
                y: 470,
                duration: 1000,
                onComplete: () => {
                    tweenCompleted = true;
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('ScraperInteriorScene');
                        this.isTransitioning = false; // Reset transition flag
                    });
                }
            });
            
            // Add a safety timeout in case the tween doesn't complete
            this.time.delayedCall(2000, () => {
                if (!tweenCompleted) {
                    console.log('Scraper entrance transition timed out, forcing transition');
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('ScraperInteriorScene');
                        this.isTransitioning = false;
                    });
                }
            });
        });

        // Exit area click handler
        this.exitArea.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            if (!priest) {
                // If priest doesn't exist, just transition immediately
                this.cameras.main.fadeOut(800, 0, 0, 0);
                this.cameras.main.once('camerafadeoutcomplete', () => {
                    this.scene.start('CrossroadScene');
                    this.isTransitioning = false;
                });
                return;
            }
            
            // Create a variable to track if the tween completed
            let tweenCompleted = false;
            
            // Play walk animation
            priest.play('walk');
            
            // Kill any existing tweens
            this.tweens.killTweensOf(priest);

            this.tweens.add({
                targets: priest,
                x: 50,
                y: 470,
                duration: 1000,
                onComplete: () => {
                    tweenCompleted = true;
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('CrossroadScene');
                        this.isTransitioning = false;
                    });
                }
            });
            
            // Add a safety timeout in case the tween doesn't complete
            this.time.delayedCall(2000, () => {
                if (!tweenCompleted) {
                    console.log('Exit transition timed out, forcing transition');
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('CrossroadScene');
                        this.isTransitioning = false;
                    });
                }
            });
        });
        
        // Create exit to ScreamingCorkScene at the right edge
        this.transitionManager.createTransitionZone(
            750, // x position
            470, // y position
            80, // width
            200, // height
            'right', // direction
            'BurningBearStreetScene', // target scene
            750, // walk to x
            470 // walk to y
        );
    }

    update() {
        super.update();
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.ScraperScene = ScraperScene;
}
