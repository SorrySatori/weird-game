import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';

export default class AbandonedBusScene extends GameScene {
    constructor() {
        super({ key: 'AbandonedBusScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    preload() {
        super.preload();
        this.load.image('abandonedBusInteriorBg', 'assets/images/backgrounds/AbandonedBus.png');
        this.load.image('deadBishop', 'assets/images/characters/dead_bishop.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
        this.load.image('door', 'assets/images/ui/door.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set background
        const bg = this.add.image(400, 300, 'abandonedBusInteriorBg');
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

        // Add exit back to ScraperBackyardScene
        this.exitArea = this.add.image(100, 470, 'exitArea')
            .setDisplaySize(120, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);
        
        // Add exit hover hint
        const exitText = this.add.text(100, 400, "Exit Bus", {
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
            
            // Check if pointer is near the dead bishop
            if (Math.abs(pointer.x - 500) < 100 && Math.abs(pointer.y - 400) < 100) {
                bishopText.setAlpha(1);
            } else {
                bishopText.setAlpha(0);
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
                        this.scene.start('ScraperBackyardScene');
                    });
                }
            });
        });
        
        // Create a container for the DeadBishop to improve hit area
        this.deadBishopContainer = this.add.container(500, 400);
        this.deadBishopContainer.setSize(200, 200);
        this.deadBishopContainer.setInteractive({ useHandCursor: true });
        
        // Add the DeadBishop sprite to the container
        this.deadBishop = this.add.sprite(0, 0, 'deadBishop');
        this.deadBishop.setScale(0.15);
        this.deadBishopContainer.add(this.deadBishop);
        
        // Add name tag for the DeadBishop
        const bishopName = this.add.text(0, 60, "Dead Bishop", {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        bishopName.setOrigin(0.5);
        this.deadBishopContainer.add(bishopName);
        
        // Add hover hint for the DeadBishop
        const bishopText = this.add.text(500, 320, "Investigate Body", {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        bishopText.setOrigin(0.5);
        bishopText.setAlpha(0);
        bishopText.setDepth(10);
        
        // Add glow effect to the DeadBishop
        const bishopGlow = this.add.graphics();
        bishopGlow.fillStyle(0x7fff8e, 0.2);
        bishopGlow.fillCircle(500, 400, 60);
        bishopGlow.setDepth(4);
        
        // Add pulsating animation to the glow
        this.tweens.add({
            targets: bishopGlow,
            alpha: { from: 0.15, to: 0.3 },
            duration: 2000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Add DeadBishop click handler
        this.deadBishopContainer.on('pointerdown', () => {
            if (this.isTransitioning) return;
            
            // Move priest closer to the DeadBishop
            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: 400,
                y: 470,
                duration: 800,
                onComplete: () => {
                    priest.play('idle');
                    
                    // Start dialog with the DeadBishop
                    this.startDialog('dead_bishop_start');
                    
                    // Get quest system
                    const questSystem = this.registry.get('questSystem');
                    
                    // Complete the find_bishop quest if active
                    if (questSystem && questSystem.getQuest('find_bishop') && !questSystem.getQuest('find_bishop').isComplete) {
                        questSystem.completeQuest('find_bishop');
                        
                        // Add a new quest to investigate the bishop's death
                        questSystem.addQuest(
                            'who_killed_bishop',
                            'Who Killed the Bishop?',
                            'I found the Bishop dead in an abandoned bus behind the Scraper building. His body shows signs of fungal infection, but there are also signs of violence. I should investigate who might be responsible for his death.'
                        );
                    }
                }
            });
        });

        // Add journal entry about the abandoned bus interior if not already added
        if (this.journalSystem && !this.journalSystem.hasEntry('abandoned_bus_interior')) {
            this.journalSystem.addEntry({
                id: 'abandoned_bus_interior',
                title: 'Abandoned Bus Interior',
                content: 'The inside of the bus is a strange mix of decay and new growth. The seats have been consumed by fungus, and strange bioluminescent patches provide an eerie green light. In the back of the bus lies the body of who appears to be the Bishop I was searching for, partially consumed by fungal growth.',
                category: 'locations',
                metadata: { location: 'Abandoned Bus Interior' }
            });
        }

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
    }

    get dialogContent() {
        const parentContent = super.dialogContent;
        
        const busContent = {
            dead_bishop_start: {
                text: "The body before you is clearly that of a religious figure - robes now stained with both blood and fungal growth. The Bishop's face is partially consumed by a strange moss that seems to pulse with faint light. His hands are clutched around a small journal, and there appears to be a wound in his chest that doesn't look accidental.",
                options: [
                    { text: "Examine the wound", next: "dead_bishop_wound" },
                    { text: "Look at the journal", next: "dead_bishop_journal" },
                    { text: "Investigate the fungal growth", next: "dead_bishop_fungus" },
                    { text: "Step back", next: "closeDialog" }
                ],
                onTrigger: () => {
                    // Add journal entry about finding the Bishop if not already added
                    if (this.journalSystem && !this.journalSystem.hasEntry('found_dead_bishop')) {
                        this.journalSystem.addEntry({
                            id: 'found_dead_bishop',
                            title: 'The Bishop\'s Fate',
                            content: 'I finally found the Bishop, but not as I had hoped. His body lies in an abandoned bus behind the Scraper building, partially consumed by fungus. There\'s evidence of violence - a wound to his chest that suggests he was killed before the fungus began to consume him. His journal may contain clues about what happened.',
                            category: 'quests',
                            metadata: { character: 'Bishop', location: 'Abandoned Bus' }
                        });
                    }
                }
            },
            dead_bishop_wound: {
                text: "The wound is a clean puncture, likely from a blade of some kind. It pierced directly through the heart with surgical precision. Whoever did this knew exactly where to strike. Strangely, there's very little blood - as if the fungus quickly sealed the wound after it was inflicted. The edges of the wound show signs of the same moss that covers parts of his face.",
                options: [
                    { text: "Look at the journal", next: "dead_bishop_journal" },
                    { text: "Investigate the fungal growth", next: "dead_bishop_fungus" },
                    { text: "Step back", next: "closeDialog" }
                ]
            },
            dead_bishop_journal: {
                text: "You carefully pry the journal from the Bishop's stiff fingers. The most recent entry reads: \"Dr. Elphi's experiments have gone too far. The symbiosis she describes is not natural - it's a perversion of the Great Fruiting's purpose. I've seen what happens in her lab... those poor subjects. I must inform the Council, though I fear she suspects my discovery. If anything happens to me, look to her first.\"",
                options: [
                    { text: "Examine the wound", next: "dead_bishop_wound" },
                    { text: "Investigate the fungal growth", next: "dead_bishop_fungus" },
                    { text: "Step back", next: "closeDialog" }
                ],
                onTrigger: () => {
                    // Add journal entry about the Bishop's journal if not already added
                    if (this.journalSystem && !this.journalSystem.hasEntry('bishop_journal')) {
                        this.journalSystem.addEntry({
                            id: 'bishop_journal',
                            title: 'The Bishop\'s Journal',
                            content: 'The Bishop\'s final journal entry suggests that Dr. Elphi was conducting dangerous experiments that he discovered. He was planning to report her to "the Council" but feared she knew about his discovery. The entry explicitly states that if anything happened to him, Dr. Elphi should be the first suspect.',
                            category: 'clues',
                            metadata: { character: 'Bishop', related: 'Dr. Elphi' }
                        });
                    }
                }
            },
            dead_bishop_fungus: {
                text: "The fungal growth on the Bishop's body is unlike anything you've seen before. It pulses with a faint bioluminescence and seems to be spreading in a controlled pattern, not randomly as natural decomposition would. There's something almost deliberate about it, as if it's not consuming the body but... transforming it. You notice small nodules forming that resemble the early stages of fruiting bodies.",
                options: [
                    { text: "Examine the wound", next: "dead_bishop_wound" },
                    { text: "Look at the journal", next: "dead_bishop_journal" },
                    { text: "Step back", next: "closeDialog" }
                ],
                onTrigger: () => {
                    // Add journal entry about the unusual fungus if not already added
                    if (this.journalSystem && !this.journalSystem.hasEntry('bishop_fungus')) {
                        this.journalSystem.addEntry({
                            id: 'bishop_fungus',
                            title: 'Unusual Fungal Growth',
                            content: 'The fungus growing on the Bishop\'s body appears to be a controlled, possibly engineered strain. It doesn\'t seem to be decomposing the body in a natural way, but rather transforming it systematically. This matches with Dr. Elphi\'s research into fungal symbiosis mentioned in the Bishop\'s journal.',
                            category: 'clues',
                            metadata: { related: 'Fungal Research' }
                        });
                    }
                }
            }
        };
        
        return { ...parentContent, ...busContent };
    }

    update() {
        super.update();
    }
}
