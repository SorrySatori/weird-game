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
        // tools/artgen/backyard_bg.py: native 1067×600, overcast day -- the old transit yard under the pipes
        this.load.image('scraperBackyardBg', 'assets/images/backgrounds/ScraperBackyard.png');
    }

    create() {
        super.create();

        const bg = this.add.image(400, 300, 'scraperBackyardBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        // the yard paints its own ground: no generic floor strip
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }

        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);

        // Back from the bus: he climbs out of the pit on the right; otherwise he stands by the Scraper's back door
        if (this.priest && this.enteredFrom === 'AbandonedBusScene') {
            this.priest.x = 890;
            this.priest.setScale(-1, 1);
            if (this.priestGlow) { this.priestGlow.x = this.priest.x; this.priestGlow.setScale(-1.05, 1.05); }
        }

        // The Scraper's back door in its rear wall on the left: back into the lobby (lit whole on hover)
        const backDoor = this.transitionManager.createDoorZone({ points: [[92, 363], [165, 352], [165, 472], [92, 508]] }, {
            target: 'ScraperInteriorScene', walkX: 110, walkY: 470, direction: 'left',
            label: () => this.t('ui.hotspots.returnInside')
        });
        // the arrow keys leave by the same door at the left edge (GameScene.registerEdgeExit)
        this.registerEdgeExit('left', () => this.leaveByEdge('left', 'ScraperInteriorScene'), backDoor);

        // The bus, sunk to its upper deck: the pit dug down to its front door on the right is the way in
        this.transitionManager.createDoorZone({ points: [[724, 462], [915, 462], [1000, 518], [748, 518]] }, {
            target: 'AbandonedBusScene', walkX: 880, walkY: 470, direction: 'down',
            label: () => this.t('ui.hotspots.abandonedBus')
        });

        // Add journal entry about the backyard if not already added
        if (this.journalSystem && !this.journalSystem.hasEntry('scraper_backyard')) {
            this.addJournalEntry(
                'scraper_backyard',
                'Scraper Backyard',
                'Behind the Scraper building lies an overgrown yard filled with the remnants of the old world. Most notable is an abandoned bus, its metal frame now serving as a trellis for strange fungal growths. There\'s something ominous about it, as if it holds undiscovered secrets.',
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
