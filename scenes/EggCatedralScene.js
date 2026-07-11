import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class EggCatedralScene extends GameScene {
    constructor() {
        super({ key: 'EggCatedralScene' });
        this.isTransitioning = false; // Add flag to track transition state
    }

    preload() {
        super.preload();
        this.load.image('eggCatedralBg', 'assets/images/backgrounds/egg-catedral.png');
        this.load.image('door', 'assets/images/ui/door.png'); // Placeholder transparent image for clickable door
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set egg cathedral background
        const bg = this.add.image(400, 300, 'eggCatedralBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Start cathedral theme
        this.playSceneMusic('cathedralTheme');
        
        // Create transition zones using SceneTransitionManager
        
        // Cathedral entrance door transition
        this.transitionManager.createTransitionZone(
            450, // x position
            300, // y position
            100, // width
            120, // height
            'up', // direction
            'CathedralEntrance', // target scene
            450, // walk to x
            340, // walk to y (slightly below door center)
            'Cathedral Interior' // destination name
        );
        
        // Right border transition to CrossroadScene
        this.transitionManager.createTransitionZone(
            780, // x position
            470, // y position
            40,  // width
            200, // height
            'right', // direction
            'CrossroadScene', // target scene
            100, // walk to x
            470, // walk to y
            'Crossroads' // destination name
        );
        
        // Left transition removed - no going back to EntryScene
        // The Fungal Master has left and the apprentice's journey continues forward

        // A secret way in: an unsealed gap in the shell that bypasses the Guardian and drops
        // straight into the Bishop's study. Two ways to find it:
        //   1. Edgar reveals it (journal 'edgar_cathedral_path').
        //   2. Palinode's Seam-Sense feels the seam directly, without ever needing Edgar.
        const hasEdgarPath = !!this.hasJournalEntry('edgar_cathedral_path');
        const hasPalinode = !!this.symbiontSystem?.hasSymbiont('palinode');
        if (hasEdgarPath || hasPalinode) {
            const gx = 90, gy = 330;
            const gap = this.add.ellipse(gx, gy, 46, 90, 0x0a1410, 0.85).setDepth(0);
            // Palinode's shimmer runs a cooler seam-green; Edgar's stays the familiar spore-green.
            const glowColor = (hasPalinode && !hasEdgarPath) ? 0xbfe6c8 : 0x7fff8e;
            const glow = this.add.circle(gx, gy, 7, glowColor, 0.8).setDepth(1);
            this.tweens.add({ targets: glow, alpha: { from: 0.25, to: 0.8 }, duration: 1600, yoyo: true, repeat: -1 });

            // When it is Palinode — not Edgar — who finds the gap, record the Seam-Sense discovery.
            if (hasPalinode && !hasEdgarPath && !this.hasJournalEntry('seam_sense_cathedral_gap')) {
                this.addJournalEntry(
                    'seam_sense_cathedral_gap',
                    'Seam-Sense: The Unsealed Cathedral',
                    'Palinode stirred before the shell of the Egg Cathedral and refused to believe the wall. Where the Guardian keeps every honest door, the unsaying found the one the shell forgot to keep shut — a seam in the stone, a gap wearing the shape of a wall. I never needed Edgar\'s directions. No wall is the last word. It drops straight into the Bishop\'s study.',
                    this.journalSystem.categories.EVENTS,
                    { location: 'Egg Cathedral', via: 'palinode' }
                );
            }

            const label = hasEdgarPath ? "Edgar's Gap" : "A Seam in the Shell";
            this.transitionManager.createTransitionZone(
                gx, gy, 70, 120,
                'left',
                'EggCathedralStudyScene',
                gx + 10, gy,
                label
            );
        }
    }
    

    update() {
        // Call parent update for all standard mechanics
        super.update();
        
        // No need for manual transition checks anymore as SceneTransitionManager handles this
    }

    shutdown() {
        // Restore background music when leaving the scene
        this.restoreBackgroundMusic();
        super.shutdown();
    }
}
