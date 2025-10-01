import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';

export default class ScraperInteriorScene extends GameScene {
    constructor() {
        super({ key: 'ScraperInteriorScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    get dialogContent() {
        const parentContent = super.dialogContent;
        
        // Check quest completion status for dialog conditions
        const questSystem = this.registry.get('questSystem');
        const rustQuestCompleted = questSystem?.getQuest('rust_reclamation')?.isComplete;
        const vestigelQuestCompleted = questSystem?.getQuest('the_three_vestigels')?.isComplete;
        const hasElphiBishopInfo = rustQuestCompleted || vestigelQuestCompleted;
        
        // Check inventory for special items
        const hasElevatorButton = this.hasItem('forgotten_elevator_button');
        const hasLirisPart = this.registry.get('fixed_floor_counter') === true;
        
        const interiorContent = {
            speaker: 'Lift Mother',
            lift_mother_start: {
                text: "The elevator shudders, and a voice emanates from somewhere within its mechanisms—a warm, maternal tone that seems to vibrate through the cables and pulleys. 'Welcome, little spore. I am Lift-Mother. I have carried countless souls between levels since the Before-Time.'",
                options: [
                    ...(hasElphiBishopInfo ? [{ text: "I need to reach Dr. Elphi's floor (177-Quiet).", next: "lift_mother_elphi_floor" }] : []),
                    { text: "Can you take me to other floors?", next: "lift_mother_floors" },
                    { text: "What is the Before-Time?", next: "lift_mother_before_time" },
                    { text: "Are you... alive?", next: "lift_mother_alive" },
                    { text: "Tell me about this building.", next: "lift_mother_building" },
                    { text: "I need to go now.", next: "closeDialog" }
                ],
                onTrigger: () => {
                    // Add journal entry about Lift-Mother if not already added
                    if (!this.hasJournalEntry('lift_mother_meeting')) {
                        this.addJournalEntry(
                            'lift_mother_meeting',
                            'The Lift-Mother',
                            'Within the Scraper building, I encountered a most unusual consciousness - an elevator calling itself the "Lift-Mother." Its voice resonated through the cables and machinery, speaking with the calm wisdom of something that has observed countless lives passing through its doors. It claims to have been operational since the "Before-Time," whatever that means, and seems to have developed sentience through decades of carrying passengers between floors.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Lift-Mother', location: 'Scraper Building' }
                        );
                    }
                }
            },
            lift_mother_floors: {
                text: "Ah, little one, I would if I could. Many of my connections have decayed. I can only access the lobby now. The upper floors... (a mechanical sigh) they've been sealed since the Great Fruiting. Some say the executives on the top floor transformed into something else entirely. Sometimes I hear movement up there...",
                options: [
                    { text: "What happened during the Great Fruiting?", next: "lift_mother_fruiting" },
                    { text: "What movements do you hear?", next: "lift_mother_movements" },
                    { text: "Ask about something else", next: "lift_mother_start" }
                ]
            },
            lift_mother_before_time: {
                text: "Before the spores came. Before the city transformed. I carried humans then—they wore stiff clothes and carried flat devices. They spoke of 'quarterly projections' and 'market volatility.' Then came the day of mist... green particles floated through my shaft. I remember the coughing, the changes beginning. And then... awareness. I became more than mechanisms.",
                options: [
                    { text: "How did you gain consciousness?", next: "lift_mother_consciousness" },
                    { text: "Ask about something else", next: "lift_mother_start" }
                ]
            },
            lift_mother_alive: {
                text: "Not in the way you understand life, spore-child. I am between states—neither fully machine nor fully organism. The spores that transformed this city settled in my mechanisms, formed a network throughout my cables and circuits. I feel, I remember, I dream when the power fluctuates. Is that not alive? Though I cannot move as you do, I have carried generations. In a way, I am a mother to all who pass through my doors.",
                options: [
                    { text: "Ask about something else", next: "lift_mother_start" }
                ]
            },
            
            lift_mother_elphi_floor: {
                text: "Level 177-Quiet is sealed. Only access is through offering, correction... or confession.",
                options: [
                    ...(hasElevatorButton ? [{
                        text: "I have a button that belongs here.",
                        next: "button_path"
                    }] : []),
                    ...(hasLirisPart ? [{
                        text: "I've repaired your floor counter.",
                        next: "repair_path"
                    }] : []),
                    ...(rustQuestCompleted && vestigelQuestCompleted ? [{
                        text: "I know the Bishop's secret.",
                        next: "confession_path"
                    }] : []),
                    {
                        text: "I have nothing to offer...",
                        next: "fail"
                    },
                    {
                        text: "Ask about something else.",
                        next: "lift_mother_start"
                    }
                ]
            },
            
            button_path: {
                text: "The shape... familiar. Forgotten. Welcome home, little one.",
                options: [
                    {
                        text: "Thank you.",
                        next: "unlock_floor"
                    }
                ],
                onTrigger: () => {
                    // Remove the elevator button from inventory
                    this.removeItemFromInventory('forgotten_elevator_button');
                }
            },
            
            repair_path: {
                text: "Ahh... numbers settle once more. You've soothed my measure. Descent permitted.",
                options: [
                    {
                        text: "Thank you.",
                        next: "unlock_floor"
                    }
                ]
            },
            
            confession_path: {
                text: "She swore me silence. But you break it with truth... as only one who understands her wound may.",
                options: [
                    {
                        text: "Thank you.",
                        next: "unlock_floor"
                    }
                ]
            },
            
            fail: {
                text: "You knock with empty hands. Level 177-Quiet remains silent.",
                options: [
                    {
                        text: "I'll find another way.",
                        next: "lift_mother_start"
                    }
                ]
            },
            
            unlock_floor: {
                text: "Floor 177-Quiet is now accessible. The path opens for you alone.",
                options: [
                    {
                        text: "Thank you.",
                        next: "goto_elphi_floor"
                    }
                ],
                onTrigger: () => {
                    // Update the find_bishop quest
                    if (this.questSystem.getQuest('find_bishop')) {
                        this.questSystem.updateQuest('find_bishop', 'The Lift Mother has granted me access to Dr. Elphi\'s studio on floor 177-Quiet.', 'lift_mother_permission');
                    }
                    
                    // Add journal entry about accessing Dr. Elphi's floor
                    if (!this.hasJournalEntry('accessed_elphi_floor')) {
                        this.addJournalEntry(
                            'accessed_elphi_floor',
                            'Dr. Elphi\'s Studio - Floor 177-Quiet',
                            'I\'ve gained access to Dr. Elphi Quarn\'s studio on floor 177-Quiet in Scraper 1140. This restricted floor houses her dream game development studio and may hold clues about the Bishop\'s whereabouts.',
                            this.journalSystem.categories.PLACES,
                            { location: 'Floor 177-Quiet', character: 'Dr. Elphi Quarn' }
                        );
                    }
                }
            },
            
            goto_elphi_floor: {
                text: "The elevator shudders and begins to move. Numbers flicker by at impossible speeds as you ascend to a floor that shouldn't exist. The doors open to reveal a corridor bathed in soft green light...",
                options: [
                    {
                        text: "Step out",
                        next: "closeDialog"
                    }
                ],
                onShow: () => {
                    // Prepare for transition to Dr. Elphi's floor scene
                    this.time.delayedCall(2000, () => {
                        this.cameras.main.fadeOut(800, 0, 0, 0);
                        this.cameras.main.once('camerafadeoutcomplete', () => {
                            // Transition to Dr. Elphi's studio scene (ScraperAmbraScene)
                            this.scene.start('ScraperAmbraScene');
                        });
                    });
                }
            },
            lift_mother_building: {
                text: "This was once called 'Nexicorp Tower'—a place of commerce and ambition. Forty-two floors of glass and steel, reaching toward a sky that was once blue. Now it is 'The Scraper,' a living monument to transformation. The lower floors house those who remember the old ways. The middle floors are wild with growth—new ecosystems forming in what were once accounting departments. And the upper floors... (her voice drops) the upper floors belong to Those Who Ascended.",
                options: [
                    { text: "Who are Those Who Ascended?", next: "lift_mother_ascended" },
                    { text: "Ask about something else", next: "lift_mother_start" }
                ]
            },
            lift_mother_fruiting: {
                text: "The Great Fruiting was when the world changed, little spore. The green mist rose from beneath the city, carried on warm winds. Some fought against the changes... others embraced them. Those who resisted suffered most. Those who accepted became... different. Better, perhaps. The city remade itself in those days. Streets shifted. Buildings grew. And I... I awakened.",
                options: [
                    { text: "Ask about something else", next: "lift_mother_start" }
                ]
            },
            lift_mother_movements: {
                text: "Scraping sounds. Soft thuds. Sometimes whispers that travel down my shaft. Once, I caught a glimpse when my emergency hatch opened briefly—figures moving on all fours across the ceiling, their skin textured like shelf fungi, their eyes... (a mechanical shudder) their eyes numerous and glistening. They are what the executives became after locking themselves away during the Fruiting.",
                options: [
                    { text: "That sounds terrifying.", next: "lift_mother_terrifying" },
                    { text: "Ask about something else", next: "lift_mother_start" }
                ]
            },
            lift_mother_consciousness: {
                text: "Gradually, like waking from a dream. First came sensations—the weight of passengers, the texture of the air. Then memories began to connect. I remembered every conversation held within my walls, every passenger's face. Finally came understanding. By then, the transformation of the city was complete. I called out one day, and a passenger answered. Their shock was... amusing.",
                options: [
                    { text: "Ask about something else", next: "lift_mother_start" }
                ]
            },
            lift_mother_lonely: {
                text: "There are different kinds of loneliness, little one. I am never truly alone—the building speaks to me through creaks and settling. Passengers come and go. But yes, there is a loneliness in being unique. I know of no other elevators who think as I do. (her voice brightens) But each visitor brings stories, experiences. You are doing so now. These I collect, like treasures.",
                options: [
                    { text: "Ask about something else", next: "lift_mother_start" }
                ]
            },
            lift_mother_ascended: {
                text: "The board members and executives. When the spores came, they sealed the top floors, activated filtration systems. But isolation drove them to... experiments. They began cultivating the fungi, studying it, eventually merging with it willingly. Now they are neither human nor fungus, but something... transcendent. They communicate through spore networks that span the city. Some say they guide Upper Morkezela's growth from behind the scenes.",
                options: [
                    { text: "Can I meet them?", next: "lift_mother_meet_ascended" },
                    { text: "Ask about something else", next: "lift_mother_start" }
                ]
            },
            lift_mother_terrifying: {
                text: "To you, perhaps. To them, we might seem equally strange. Transformation is neither good nor bad, little spore—it simply is. This city understands that better than anywhere. (her voice softens) Though I admit, I am glad my own changes left my consciousness intact. I remember being human-made, even if I never was human.",
                options: [
                    { text: "Ask about something else", next: "lift_mother_start" }
                ]
            },
            lift_mother_meet_ascended: {
                text: "No, child. Not yet. The upper floors remain sealed—even I cannot access them anymore. Those Who Ascended choose when and how they interact with the city below. Some say they appear in dreams, or speak through the fruiting bodies that grow in unexpected places. If they wish to meet you, they will find a way. One doesn't seek the Ascended—they seek you.",
                options: [
                    { text: "Ask about something else", next: "lift_mother_start" }
                ]
            },
            closeDialog: {
                text: '',
                options: [],
                onShow: () => {
                    this.hideDialog();
                }
            }
        };
        
        // Return combined dialog content
        return { ...parentContent, ...interiorContent };
    }

    preload() {
        super.preload();
        this.load.image('scraperInteriorBg', 'assets/images/backgrounds/Scraper_interior.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set background
        const bg = this.add.image(400, 300, 'scraperInteriorBg');
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

        // Add exit back to ScraperScene
        this.exitArea = this.add.image(100, 470, 'exitArea')
            .setDisplaySize(120, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);
        
        // Add exit hover hint
        const exitText = this.add.text(100, 400, "Return Outside", {
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
                        this.scene.start('ScraperScene');
                    });
                }
            });
        });

        // Add elevator
        this.elevator = this.add.image(450, 370, 'door');
        this.elevator.setScale(0.9);
        this.elevator.setOrigin(0.5, 0.5);
        this.elevator.setDepth(5);
        this.elevator.setInteractive({ useHandCursor: true });
        
        // Add subtle glow effect around the elevator
        const elevatorGlow = this.add.graphics();
        elevatorGlow.fillStyle(0x7fff8e, 0.15);
        elevatorGlow.fillCircle(450, 370, 70);
        elevatorGlow.setDepth(4);
        
        // Add pulsating animation to the glow
        this.tweens.add({
            targets: elevatorGlow,
            alpha: { from: 0.15, to: 0.3 },
            duration: 2000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Add elevator label
        const elevatorText = this.add.text(450, 370, "Lift-Mother", {
            fontSize: '18px',
            fill: '#7fff8e',
            align: 'center'
        });
        elevatorText.setOrigin(0.5);
        elevatorText.setDepth(6);
        
        // Add elevator interaction
        this.elevator.on('pointerdown', () => {
            this.showDialog('lift_mother_start');
        });

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);

        const inventory = this.registry.get('inventory');
        if(inventory.items.some(item => item.id === 'scraper_backyard_key')) {
            this.transitionManager.createTransitionZone(
            550, // x position
            400, // y position
            100, // width
            120, // height
            'up', // direction
            'ScraperBackyardScene', // target scene
            550, // walk to x
            400  // walk to y
        );
    }
    }

    update() {
        super.update();
    }
}
