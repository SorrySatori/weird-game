import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';

export default class RustDomainScene extends GameScene {
    constructor() {
        super({ key: 'RustDomainScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    get dialogContent() {
        return {
            ...super.dialogContent,
            speaker: 'Narrator',

            machines_destroyed: {
                text: `The machines shudder and grind. One by one, their rhythmic hum falters — replaced by a grinding, choking rasp. Sparks spit from corroded joints. A deep vibration runs through the floor, then stops. Silence. The Rust Feast you delivered was hollow. The illusion of redmass dissolved inside their guts, leaving nothing but oil and metal scraps. The machines tried to feed on something that wasn't there. Now they are still.`,
                options: [
                    { text: "What have I done...", next: "machines_destroyed_aftermath" }
                ]
            },
            machines_destroyed_aftermath: {
                text: `Ulvarex stirs inside you, uneasy. "The weave held. It always holds. But machines... they don't dream. They don't believe. They just consume." A long pause. "The illusion fed their trust, not their hunger." Around you, the Rust Choir domain is quiet for the first time. The machines that once hummed with life are dark and still. Rust is already forming on surfaces that were polished moments ago.`,
                options: [
                    { text: "The Rust Choir will know what I've done.", next: "closeDialog" }
                ],
                onTrigger: () => {
                    this.modifyFactionReputation('RustChoir', -20);
                    this.addJournalEntry(
                        'rust_choir_machines_destroyed',
                        'The Machines Fall Silent',
                        'The illusory redmass I used in the Rust Feast has destroyed the Rust Choir machines. They tried to feed on the Mirage Weave and found nothing — the illusion dissolved inside them. The machines are dead. The Rust Choir will not forgive this.',
                        this.journalSystem.categories.EVENTS
                    );
                }
            },
        };
    }

    preload() {
        super.preload();
        this.load.image('rustDomainBg', 'assets/images/backgrounds/RustDomain.png');
    }

    create() {
        super.create();

        // Set background
        const bg = this.add.image(400, 300, 'rustDomainBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);

        // Add fade-in effect
        this.cameras.main.fadeIn(1200, 0, 0, 0);

        // Position the priest
        this.priest.x = 400;
        this.priest.y = 470;

        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // Create exit back to Scraper Interior (elevator)
        this.transitionManager.createTransitionZone(
            400, // x position
            560, // y position
            200, // width
            50,  // height
            'down',
            'ScraperInteriorScene',
            450, // walk to x (near elevator)
            370  // walk to y
        );

        const exitHint = this.add.text(400, 575, 'Back to Elevator', {
            fontSize: '14px',
            fill: '#c87533',
            backgroundColor: '#1a0a00',
            padding: { x: 8, y: 4 }
        });
        exitHint.setOrigin(0.5);
        exitHint.setDepth(10);
        exitHint.setAlpha(0.7);

        // Complete find_rust_choir quest on arrival
        if (this.questSystem) {
            const findQuest = this.questSystem.getQuest('find_rust_choir');
            if (findQuest && !findQuest.isComplete) {
                this.questSystem.completeQuest('find_rust_choir');
                this.showNotification('Quest completed: Find the Rust Choir');
            }
        }

        // Journal entry on first visit
        if (!this.hasJournalEntry('rust_domain_arrival')) {
            this.addJournalEntry(
                'rust_domain_arrival',
                'The Rust Domain',
                'I have reached the upper floors of the Scraper — the domain of the Rust Choir. The air is thick with the smell of oil and oxidized metal. Machines hum and click in the walls, some of them alive in ways that defy explanation. This is where Brukk resides.',
                this.journalSystem.categories.PLACES
            );
        }

        // Illusion feast consequences — machines are destroyed
        if (this.registry.get('rust_feast_illusory') && !this.hasJournalEntry('rust_choir_machines_destroyed')) {
            this.time.delayedCall(1500, () => {
                this.showDialog('machines_destroyed');
            });
        }
    }

    update() {
        super.update();
    }
}

if (typeof window !== 'undefined') {
    window.RustDomainScene = RustDomainScene;
}
