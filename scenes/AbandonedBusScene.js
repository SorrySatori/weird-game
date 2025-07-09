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
        this.load.image('deadBishop', 'assets/images/characters/DeadBishop.png');
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
                    if (!this.dialogVisible) {
                        this.dialogState = 'dead_bishop_start';
                        this.showDialog(this.dialogState);
                    }

                    // Get quest system
                    const questSystem = this.registry.get('questSystem');

                    // Complete the find_bishop quest if active
                    if (questSystem && questSystem.getQuest('find_bishop') && !questSystem.getQuest('find_bishop').isComplete) {
                        questSystem.completeQuest('find_bishop');

                        // Add a new quest to investigate the bishop's death
                        questSystem.addQuest(
                            'who_killed_bishop',
                            'Who Killed the Bishop?',
                            'I found the Bishop dead in an abandoned bus behind the Scraper building. His body shows barely any signs of violence. I should investigate who might be responsible for her death.'
                        );
                    }
                }
            });
        });

        // Add journal entry about the abandoned bus interior if not already added
        if (this.journalSystem && !this.journalSystem.hasEntry('abandoned_bus_interior')) {
            this.addJournalEntry(
                'abandoned_bus_interior',
                'Abandoned Bus Interior',
                'The inside of the bus is a strange mix of decay and new growth. The seats have been consumed by fungus, and strange bioluminescent patches provide an eerie green light. In the back of the bus lies the body of who appears to be the Bishop I was searching for, partially consumed by fungal growth.',
                this.journalSystem.categories.PLACES
            );
        }

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
    }

    get dialogContent() {
        const parentContent = super.dialogContent;

        const busContent = {
            dead_bishop_start: {
                text: "The body before you is clearly that of a religious figure - an Obazoba Bishop in ceremonial robes stained with fungal growth. Her face is serene but pale, with subtle bruising visible at her temples. Nearby, you spot a portable dream device, a worn notebook and a dream interface helmet (still attached) and a small bag of what appears to be berries. In her sleeve you spot some papers.",
                options: [
                    { text: "Examine the bruising", next: "dead_bishop_bruising" },
                    { text: "Check the dream device", next: "dead_bishop_cartridge" },
                    { text: "Examine the helmet", next: "dead_bishop_helmet" },
                    { text: "Look at the notebook", next: "dead_bishop_notebook" },
                    { text: "Read the notes", next: "dead_bishop_memo" },
                    { text: "Inspect the berries", next: "dead_bishop_berries" },
                    { text: "Step back", next: "closeDialog" }
                ],
                onTrigger: () => {
                    // Add journal entry about finding the Bishop if not already added
                    if (this.journalSystem && !this.journalSystem.hasEntry('found_dead_bishop')) {
                        this.addJournalEntry(
                            'found_dead_bishop',
                            'The Bishop\'s Fate',
                            'I found the Bishop in an abandoned bus behind the Scraper building. Her body shows no obvious signs of violence, but there\'s bruising at her temples near the neural interface points. A dream device with a cartridge labeled "The Cardinal Feast" was found nearby, along with her journal and other personal effects. This doesn\'t appear to be a natural death.',
                            this.journalSystem.categories.EVENTS
                        );
                    }
                }
            },
            dead_bishop_bruising: {
                text: "A closer examination reveals subtle bruising beneath where neural interface straps would be placed. The markings are consistent with neural overstimulation - possibly dream-burnout or data surge trauma. There's no sign of external violence, but something clearly overwhelmed her neural pathways.",
                options: [
                    { text: "Check the dream device", next: "dead_bishop_cartridge" },
                    { text: "Look at the notebook", next: "dead_bishop_notebook" },
                    { text: "Read the notes", next: "dead_bishop_memo" },
                    { text: "Examine the helmet", next: "dead_bishop_helmet" },
                    { text: "Inspect the berries", next: "dead_bishop_berries" },
                    { text: "Step back", next: "closeDialog" }
                ],
                onTrigger: () => {
                    // Add journal entry about the bruising if not already added
                    if (this.journalSystem && !this.journalSystem.hasEntry('bishop_bruising')) {
                        this.addJournalEntry(
                            'bishop_bruising',
                            'Neural Trauma',
                            'The Bishop\'s body shows signs of neural trauma - bruising at the temples where dream interface devices connect. This suggests she died while connected to a dream device, possibly from neural overstimulation or some kind of data surge. The death appears to be dream-related rather than physical violence.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Bishop', related: 'Dream Technology' }
                        );
                    }
                    this.questSystem.updateQuest(
                        'who_killed_bishop',
                        'I have examined the Bishop\'s body and found bruises at the temples where dream interface devices connect. This suggests she died while connected to a dream device, possibly from neural overstimulation or some kind of data surge. The death appears to be dream-related rather than physical violence.',
                        'dead_bishop_bruising'
                    );
                }
            },
            dead_bishop_cartridge: {
                text: "You examine the portable dream device clutched in the Bishop's hand. A cartridge labeled 'The Cardinal Feast' is inserted, but appears corrupted. The device's small screen displays an error message: \"Runtime loop detected. Initiated failsafe: NULL SCENE.\" Whatever experience this cartridge contained, it seems to have catastrophically failed during use.",
                options: [
                    { text: "Examine the bruising", next: "dead_bishop_bruising" },
                    { text: "Look at the notebook", next: "dead_bishop_notebook" },
                    { text: "Read the notes", next: "dead_bishop_memo" },
                    { text: "Examine the helmet", next: "dead_bishop_helmet" },
                    { text: "Inspect the berries", next: "dead_bishop_berries" },
                    { text: "Step back", next: "closeDialog" }
                ],
                onTrigger: () => {
                    // Add journal entry about the dream cartridge if not already added
                    if (this.journalSystem && !this.journalSystem.hasEntry('bishop_cartridge')) {
                        this.addJournalEntry(
                            'bishop_cartridge',
                            'The Cardinal Feast',
                            'The Bishop was using a dream cartridge called "The Cardinal Feast" when she died. The device shows an error about a runtime loop and something called a "NULL SCENE" failsafe. This suggests a catastrophic failure in the dream program that may have caused neural feedback severe enough to be fatal.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Bishop', related: 'Dream Technology' }
                        );
                    }
                    this.questSystem.updateQuest(
                        'who_killed_bishop',
                        'Before she died, the Bishop was apparently playing a game called "The Cardinal Feast".',
                        'dead_bishop_cartridge'
                    );
                    const dreamCartridge = {
                        id: 'dream_cartridge',
                        name: 'The Cardinal Feast',
                        description: 'A portable dream device with a cartridge labeled "The Cardinal Feast". I hope it is at least a good game when it was the last one poor Bishop played.',
                        icon: 'dream_cartridge',
                        usable: true,
                        consumable: false,
                        value: 0
                    };
                    this.addItemToInventory(dreamCartridge);
                }
            },
            dead_bishop_helmet: {
                text: "You examine the dream interface helmet attached to the Bishop's body. It's a portable device with a small screen and a neural interface port. The helmet is slightly warm to the touch, suggesting it was recently in use. Maybe she was inside a dream program — but someone intentionally erased the session data? Unfortunately, it's clear that the helmet is not functional and the neural interface port is damaged.",
                options: [
                    { text: "Examine the bruising", next: "dead_bishop_bruising" },
                    { text: "Check the dream device", next: "dead_bishop_cartridge" },
                    { text: "Read the memo note", next: "dead_bishop_memo" },
                    { text: "Inspect the berries", next: "dead_bishop_berries" },
                    { text: "Step back", next: "closeDialog" }
                ],
                onTrigger: () => {
                    if (this.journalSystem && !this.journalSystem.hasEntry('bishop_helmet')) {
                        this.addJournalEntry(
                            'bishop_helmet',
                            'Dream Interface Helmet',
                            'The Bishop was wearing a portable dream interface helmet when she died. The device shows an error about a runtime loop and something called a "NULL SCENE" failsafe. This suggests a catastrophic failure in the dream program that may have caused neural feedback severe enough to be fatal.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Bishop', related: 'Dream Technology' }
                        );
                    }
                    this.questSystem.updateQuest(
                        'who_killed_bishop',
                        'Before she died, the Bishop was apparently using a portable dream interface helmet.',
                        'dead_bishop_helmet'
                    )
                }
            },
            dead_bishop_notebook: {
                text: "You carefully open the Bishop's notebook. A small leather-bound notebook. Most pages are torn out or never used. Only one entry remains, hastily scribbled: “The city no longer hears me. Perhaps the dreams will.”",
                options: [
                    { text: "Examine the bruising", next: "dead_bishop_bruising" },
                    { text: "Check the dream device", next: "dead_bishop_cartridge" },
                    { text: "Read the memo note", next: "dead_bishop_memo" },
                    { text: "Examine the helmet", next: "dead_bishop_helmet" },
                    { text: "Inspect the berries", next: "dead_bishop_berries" },
                    { text: "Step back", next: "closeDialog" }
                ],
                onTrigger: () => {
                    // Add journal entry about the Bishop's journal if not already added
                    if (this.journalSystem && !this.journalSystem.hasEntry('bishop_journal')) {
                        this.addJournalEntry(
                            'bishop_journal',
                            'The Bishop\'s Journal',
                            'The Bishop\'s journal contains a disturbing note: "The city no longer hears me. Perhaps the dreams will."',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Bishop', related: 'Identity' }
                        );
                    }
                    this.questSystem.updateQuest(
                        'who_killed_bishop',
                        'Before she died, the Bishop was apparently writing in her journal. Most pages are torn out or never used. Only one entry remains, hastily scribbled: “The city no longer hears me. Perhaps the dreams will.”',
                        'dead_bishop_journal'
                    )
                }
            },
            dead_bishop_memo: {
                text: "You find a crumpled note in the Bishop's sleeve. It's written in her handwriting and stamped 'TOWNHALL PERSONAL LOG – FOR INTERNAL USE ONLY'. The fragment reads: \"I walked into the confessional, but she was already there. Looked like me. But didn't breathe. Didn't blink. And it finished my sentence.\" The rest of the note is torn away.",
                options: [
                    { text: "Examine the bruising", next: "dead_bishop_bruising" },
                    { text: "Check the dream device", next: "dead_bishop_cartridge" },
                    { text: "Examine the helmet", next: "dead_bishop_helmet" },
                    { text: "Look at the notebook", next: "dead_bishop_notebook" },
                    { text: "Inspect the berries", next: "dead_bishop_berries" },
                    { text: "Step back", next: "closeDialog" }
                ],
                onTrigger: () => {
                    // Add journal entry about the memo if not already added
                    if (this.journalSystem && !this.journalSystem.hasEntry('bishop_memo')) {
                        this.addJournalEntry(
                            'bishop_memo',
                            'Townhall Memo',
                            'A memo from the Bishop describes a disturbing encounter with what sounds like a doppelgänger of herself. The note was officially logged at the Townhall, suggesting she reported this incident. The encounter with something that "looked like me" but "didn\'t breathe" suggests either a hallucination or something more sinister.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Bishop', related: 'Doppelgänger' }
                        );
                    }
                    this.questSystem.updateQuest(
                        'who_killed_bishop',
                        'I have found a strange note written with the Bishop\'s hand and stamped "TOWNHALL PERSONAL LOG – FOR INTERNAL USE ONLY". The fragment reads: \"I walked into the confessional, but she was already there. Looked like me. But didn\'t breathe. Didn\'t blink. And it finished my sentence.\"',
                        'dead_bishop_notebook'
                    );
                }
            },
            dead_bishop_berries: {
                text: "A small bag of spiced Sulkberries sits nearby, half-eaten. The sour, pungent berries are still fresh, suggesting the Bishop was here recently and possibly consuming them to calm her nerves before using the dream device. Sulkberries are known for their mild calming effect.",
                options: [
                    { text: "Examine the bruising", next: "dead_bishop_bruising" },
                    { text: "Check the dream device", next: "dead_bishop_cartridge" },
                    { text: "Examine the helmet", next: "dead_bishop_helmet" },
                    { text: "Look at the notebook", next: "dead_bishop_notebook" },
                    { text: "Read the memo note", next: "dead_bishop_memo" },
                    { text: "Step back", next: "closeDialog" }
                ],
                onTrigger: () => {
                    // Add journal entry about the berries if not already added
                    if (this.journalSystem && !this.journalSystem.hasEntry('bishop_berries')) {
                        this.addJournalEntry(
                            'bishop_berries',
                            'Spiced Sulkberries',
                            'The Bishop had been eating Sulkberries shortly before her death. These berries are commonly used to calm the mind. Their freshness suggests she died very recently, making this a fresh scene rather than an old death.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Bishop', related: 'Timeline' }
                        );
                    }
                    this.questSystem.updateQuest(
                        'who_killed_bishop',
                        'Before she died, the Bishop was apparently eating Sulkberries. These berries are commonly used to calm the mind. Their freshness suggests she died very recently, making this a fresh scene rather than an old death.',
                        'dead_bishop_berries'
                    )
                }
            },
        };

        return { ...parentContent, ...busContent };
    }

    update() {
        super.update();
    }
}
