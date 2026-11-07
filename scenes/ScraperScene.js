import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';

export default class ScraperScene extends GameScene {
    constructor() {
        super({ key: 'ScraperScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    preload() {
        super.preload();
        this.preloadMusic('streetSong');
        this.load.image('scraperBg', 'assets/images/backgrounds/Scraper1140.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Native 1067×600 (tools/artgen/scraper_bg.py): the old picture re-pixelled, plus a wet rooftop to walk on
        const bg = this.add.image(400, 300, 'scraperBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        // The background paints its own roof and duckboards; the generic ground strip would cover it.
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }
        this.playSceneMusic('streetSong', { resume: true });

        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
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
        
        // Add entrance to the Scraper building interior: the "1140" gate of the footbridge, centre of the background
        const gateX = this.scale.width / 2;
        const scraperEntrance = this.add.image(gateX, 470, 'exitArea')
            .setDisplaySize(100, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        scraperEntrance.setDepth(5);
        
        // Add a hint about the scraper entrance
        const scraperHint = this.add.text(gateX, 355, this.t('ui.hotspots.enterScraper'), {
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
            if (Math.abs(pointer.x - gateX) < 50 && Math.abs(pointer.y - 470) < 100) {
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
                    "Scraper 1140: a crooked skyscraper towering over the city. It used to be an office tower; now every floor lives a life of its own, and nobody seems quite sure how many floors there are.",
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
                x: gateX,
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

        // The stair-house door at the left (down to the Crossroad): a standard exit -- the arrow, its label on hover,
        // and the arrow keys take it at the screen edge (it used to be a bare invisible hotspot with none of that)
        this.transitionManager.createTransitionZone(
            50, // x position (800-space)
            470, // y position
            80, // width
            200, // height
            'left', // direction
            'CrossroadScene', // target scene
            50, // walk to x
            470 // walk to y
        );

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

        // Examine: the tower & its "SCRAPER 1140" sign (upper-center, clear of the gate below).
        // Comment deepens once you've been inside.
        this.createObservable(447, 160, 200, 170, () => {
            if (this.hasJournalEntry('scraper_building')) return this.t('observe.scraper.been_inside');
            return this.t('observe.scraper.default');
        }, { hint: this.t('observe.scraper.hint') });
    }

    update() {
        super.update();
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.ScraperScene = ScraperScene;
}
