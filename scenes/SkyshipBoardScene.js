import GameScene from './GameScene.js';
import JournalSystem from '../systems/JournalSystem.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
export default class SkyshipBoardScene extends GameScene {
    constructor() {
        super({ key: 'SkyshipBoardScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    preload() {
        super.preload();
        this.load.image('skyshipBoardBg', 'assets/images/backgrounds/skyship_board.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
        this.load.image('captainLiris', 'assets/images/characters/captain_liris.png');
    }

    create() {
        super.create();

        // Set skyship board background
        this.background = this.add.image(400, 300, 'skyshipBoardBg');
        this.background.setDisplaySize(800, 600);
        this.background.setDepth(-1);

        // Create symbiont UI
        this.createSymbiontUI();

        // Add exit area to go back to CrossroadScene
        this.exitArea = this.add.image(100, 500, 'exitArea')
            .setDisplaySize(120, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);

        // Add a subtle glow effect to hint at the exit area
        const exitGlow = this.add.graphics();
        exitGlow.fillStyle(0x7fff8e, 0.2);
        exitGlow.fillCircle(100, 500, 50);
        exitGlow.setDepth(9);
        
        // Add pulsating animation to the glow
        this.tweens.add({
            targets: exitGlow,
            alpha: { from: 0.2, to: 0.4 },
            duration: 1500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Add a text hint for the exit
        const exitText = this.add.text(100, 550, "Return to city", {
            fontSize: '16px',
            fill: '#7fff8e',
            align: 'center'
        });
        exitText.setOrigin(0.5);
        exitText.setDepth(10);

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);

        // Setup scene transitions
        this.setupSceneTransitions();
        
        // Add Captain Liris
        this.createCaptainLiris();
    }

    createCaptainLiris() {
        // Create Captain Liris NPC
        this.captainLiris = this.add.image(600, 300, 'captainLiris');
        this.captainLiris.setScale(0.2);
        this.captainLiris.setDepth(5);
        this.captainLiris.setInteractive({ useHandCursor: true });
        
        // Add a subtle glow effect around the captain
        const captainGlow = this.add.graphics();
        captainGlow.fillStyle(0x7fff8e, 0.15);
        captainGlow.fillCircle(600, 300, 40);
        captainGlow.setDepth(4);
        
        // Add pulsating animation to the glow
        this.tweens.add({
            targets: captainGlow,
            alpha: { from: 0.15, to: 0.3 },
            duration: 2000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Add hover effect
        this.captainLiris.on('pointerover', () => {
            this.tweens.add({
                targets: this.captainLiris,
                scaleX: 0.22,
                scaleY: 0.22,
                duration: 300,
                ease: 'Sine.easeOut'
            });
        });
        
        this.captainLiris.on('pointerout', () => {
            this.tweens.add({
                targets: this.captainLiris,
                scaleX: 0.2,
                scaleY: 0.2,
                duration: 300,
                ease: 'Sine.easeOut'
            });
        });
        
        // Add click interaction to show dialog
        this.captainLiris.on('pointerdown', () => {
            this.showDialog('captainMain');
        });
        
        // Add a name tag below the captain
        const captainText = this.add.text(600, 360, "Captain Liris", {
            fontSize: '18px',
            fill: '#7fff8e',
            align: 'center'
        });
        captainText.setOrigin(0.5);
        captainText.setDepth(6);
    }
    
    setupSceneTransitions() {
        // Initialize the scene transition manager if it doesn't exist
        if (!this.transitionManager) {
            this.transitionManager = new SceneTransitionManager(this);
        }
        
        // Exit to CrossroadScene
        this.exitArea.on('pointerdown', () => {
            // Use the SceneTransitionManager to handle the transition
            this.transitionManager.handleSceneTransition('CrossroadScene', 100, 500);
        });
    }

    get dialogContent() {
        // Combine parent dialog content with this scene's content
        const parentContent = super.dialogContent || {};
        
        // Define this scene's dialog content
        const skyshipContent = {
            speaker: 'Captain Liris',
            main: {
                text: 'You find yourself on the deck of a skyship. The air is thin up here, and you can see the fungal city sprawled below.',
                options: [
                    {
                        text: 'Look around',
                        next: 'lookAround'
                    },
                ]
            },
            lookAround: {
                text: 'The skyship appears to be a transport vessel. Various fungal growths line the edges of the deck, seemingly serving as both decoration and structural support. The ship sways gently in the wind.',
                options: [
                    {
                        text: 'Other topics',
                        next: 'main'
                    }
                ]
            },
            captainMain: {
                text: "Ah, a visitor! Welcome aboard the Verdigrace. I'm Captain Liris, navigator of the aerial currents and keeper of this fine vessel. What brings you to my ship?",
                options: [
                    {
                        text: 'How does this ship fly?',
                        next: 'captainTechnology'
                    },
                    {
                        text: 'Where are you headed?',
                        next: 'captainDestination'
                    },
                    {
                        text: 'Tell me about yourself.',
                        next: 'captainAbout'
                    },
                    {
                        text: 'Is flying dangerous?',
                        next: 'captainDanger'
                    },
                    {
                        text: 'What cargo do you carry?',
                        next: 'captainCargo'
                    },
                    ...(this.hasJournalEntry('lift_mother_meeting') ? [{
                        text: 'I need help with an elevator system.',
                        next: 'captainElevator'
                    }] : []),
                ],
                onTrigger: () => {
                    // Add journal entry for meeting Captain Liris if not already added
                    if (!this.hasJournalEntry('captain_liris_meeting')) {
                        this.addJournalEntry(
                            'captain_liris_meeting',
                            'Captain Liris of the Verdigrace',
                            'Aboard the skyship, I met Captain Liris, an imposing figure in an ornate uniform who commands the vessel known as the Verdigrace. The ship travels the aerial trade routes between various settlements and research outposts, carrying rare spores, mycelia, and information.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Captain Liris', location: 'Verdigrace Skyship' }
                        );
                    }
                }
            },
            captainAbout: {
                text: "I'm Captain Liris, master of this vessel, as I said. I'm on a mission for the Lumen Directorate, as usual.",
                options: [
                    {
                        text: 'What is the Lumen Directorate?',
                        next: 'captainAccord'
                    },
                    {
                        text: 'Other topics',
                        next: 'captainMain'
                    }
                ]
            },
            captainAccord: {
                text: "The Lumen Directorate is a powerful organization, you know? We strive for the fusion of mind and flora. We are keepers and protectors of everything that grows. We are the guardians of life.",
                options: [
                    {
                        text: 'Other topics',
                        next: 'captainMain'
                    },
                    {
                        text: "What is you mission?",
                        next: "captainMission"
                    },
                    {
                        text: "Does Lumen Directorate have some enemies?",
                        next: "captainEnemies"
                    }
                ],
                onTrigger: () => {
                    const factionSystem = this.registry.get('factionSystem');
                    if (factionSystem) {
                        factionSystem.modifyReputation('LumenDirectorate', +10);
                        this.showNotification('Lumen Directorate Reputation +10');
                    }
                }
            },
            captainMission: {
                text: "We are on a mission to search and gather rare specimens for the Lumen Directorate. But we are still waiting for more specs, so we don't mind that little ladder of yours.",
                options: [
                    {
                        text: 'Other topics',
                        next: 'captainMain'
                    }
                ]
            },
            captainEnemies: {
                text: "Sure, we have some enemies, as everybody. Especially that Rust Choir scum, but that's hardly surprising.", 
                options: [
                    {
                        text: 'Other topics',
                        next: 'captainMain'
                    }
                ],
                onTrigger: () => {
                    const factionSystem = this.registry.get('factionSystem');
                    if (factionSystem) {
                        factionSystem.modifyReputation('LumenDirectorate', +10);
                        this.showNotification('Lumen Directorate Reputation +10');
                        if (!this.hasJournalEntry('lumen_directorate_faction')) {
                            this.addJournalEntry(
                                'lumen_directorate_faction',
                                'LUMEN DIRECTORATE',
                                'The Lumen Directorate is a powerful faction dedicated to the fusion of mind and flora. They are keepers and protectors of everything that grows, acting as guardians of life itself. Their members often undertake missions to gather rare specimens and promote symbiotic growth.',
                                this.journalSystem.categories.FACTIONS,
                                { faction: 'Lumen Directorate', location: 'Voxmarket' }
                            );
                        }
                    }
                }
            },
            captainTechnology: {
                text: "Fascinating, isn't it? The ship's hull is infused with a special strain of buoyant spores. They create microscopic gas pockets that give us lift. The mycelial sails catch the wind currents, and the rudder fungi respond to my commands through a symbiotic bond. I've been connected to this ship for over twenty cycles now.",
                options: [
                    {
                        text: 'That sounds dangerous.',
                        next: 'captainDanger'
                    },
                    {
                        text: 'Ask something else',
                        next: 'captainMain'
                    }
                ]
            },
            
            captainAloft: {
                text: "Fascinating, isn't it? The ship's hull is infused with a special strain of buoyant spores. They create microscopic gas pockets that give us lift. The mycelial sails catch the wind currents, and the rudder fungi respond to my commands through a symbiotic bond. I've been connected to this ship for over twenty cycles now.",
                options: [
                    {
                        text: 'That sounds dangerous.',
                        next: 'captainDanger'
                    },
                    {
                        text: 'Ask something else',
                        next: 'captainMain'
                    }
                ]
            },
            captainDanger: {
                text: "Ha! Life without risk is no life at all. Yes, there are dangers—storm spores that could envelop us, predatory flying mycelia that hunt in the upper reaches, not to mention the constant balance between Growth and Decay that keeps us from either dissolving into spores or becoming a rigid, dead mass. But the freedom of the skies... that's worth any risk.",
                options: [
                    {
                        text: 'Other topics',
                        next: 'captainMain'
                    }
                ]
            },
            captainDestination: {
                text: "We follow the great spore currents that circle above the continent. Next stop is the Hanging Gardens of Mycora, where we'll trade city goods for rare cultivation specimens. After that, perhaps the floating research outposts of the Eastern Canopy. The winds decide our ultimate path.",
                options: [
                    {
                        text: 'Could I travel with you?',
                        next: 'captainTravel'
                    },
                    {
                        text: 'Ask something else',
                        next: 'captainMain'
                    }
                ]
            },
            captainTravel: {
                text: "Perhaps someday, friend. But not on this journey. The ship has... chosen its crew already. I can sense it's not ready to bond with you yet. Return when you've proven your worth. The Verdigrace is particularly picky about who it accepts. If you really mean it, visit Lumen Directorate headqurarters in the city and ask about joining the crew. They might have some tasks for you to prove your dedication.",
                options: [
                    {   text: 'Where can I find the Lumen Directorate headquarters?',
                        next: 'captainDirectorate'
                    },
                    {
                        text: 'Other topics',
                        next: 'captainMain'
                    }
                ]
            },
                captainDirectorate: {
                text: "The Lumen Directorate headquarters is located in the heart of the city, near the main square. It's quite a building, you can't miss it.",
                options: [
                    {
                        text: 'Thank you! I have some other questions.',
                        next: 'captainMain'
                    }
                ],
                onTrigger: () => {
                    const factionSystem = this.registry.get('factionSystem');
                    if (factionSystem) {
                        factionSystem.modifyReputation('LumenDirectorate', +5);
                        this.showNotification('Lumen Directorate Reputation +5');
                    }
                     if (!this.questSystem.getQuest('find_lumen_directorate')) {
                        this.questSystem.addQuest('find_lumen_directorate', 'Nothing Hidden. Nothing Lost', 'Captain Liris gave me directions to the Lumen Directorate headquarters. I should visit them to learn more about their work and see if I can join their crew.')
                    }
                }
            },
            captainCargo: {
                text: "Primarily rare spores and mycelia that can't be cultivated in the city. Specialized symbiont strains, crystallized growth enzymes, decay-resistant building materials. We also carry messages between the scattered aerial colonies and research stations. Information is perhaps our most valuable cargo—knowledge that would never reach the ground otherwise.",
                options: [
                    {
                        text: 'Do you have anything to trade?',
                        next: 'captainTrade'
                    },
                    {
                        text: 'Ask something else',
                        next: 'captainMain'
                    }
                ]
            },
            captainTrade: {
                text: "Not at the moment, I'm afraid. We've just begun our journey and haven't collected our specialized goods yet. Return after we've made our first circuit—perhaps in a few cycles—and I might have something unique for an intrepid explorer like yourself. Keep an eye on the skies for our return.",
                options: [
                    {
                        text: 'Other topics',
                        next: 'captainMain'
                    }
                ]
            },
            
            captainElevator: {
                text: "An elevator system, you say? Ah, you must be referring to one of those ancient vertical transport mechanisms in the city's towers. Those old systems are fascinating—a blend of mechanical engineering and early symbiotic technology. What seems to be the issue?",
                options: [
                    {
                        text: 'The floor counter is broken.',
                        next: 'captainFloorCounter'
                    },
                    {
                        text: 'Never mind, ask something else.',
                        next: 'captainMain'
                    }
                ]
            },
            
            captainFloorCounter: {
                text: "A floor counter malfunction? That's a common issue with the lift systems. The numeric displays were designed to handle the simple tasks as going up and down, but the engineers did not count with sentient elevators. I happen to have developed a specialized calibration tool for just such problems during my time maintaining the aerial dock lifts.",
                options: [
                    {
                        text: 'Could I borrow this tool?',
                        next: 'captainGivesTool'
                    },
                    {
                        text: 'How does it work?',
                        next: 'captainToolExplanation'
                    }
                ]
            },
            
            captainToolExplanation: {
                text: "It's a symbiotic interface that bridges old electronic systems with the newly developed lift's intelligent mind. The tool contains a specialized strain of communication micro drones that can translate between digital signals and brain-like impulses. You simply attach it to the counter's maintenance port, and it reestablishes the connection between the mechanical components and the building's new nervous system.",
                options: [
                    {
                        text: 'Could I borrow this tool?',
                        next: 'captainGivesTool'
                    },
                    {
                        text: 'Ask something else',
                        next: 'captainMain'
                    }
                ]
            },
            
            captainGivesTool: {
                text: "Of course you can! I always carry spares—you never know when you'll need to repair something mid-flight. Here, take this calibration module. It's simple to use: just attach it to the maintenance panel of the elevator system, and it will automatically recalibrate the floor counter. The drones inside will do all the work.",
                options: [
                    {
                        text: 'Thank you!',
                        next: 'closeDialog'
                    }
                ],
                onTrigger: () => {
                    // Set registry flag for fixed floor counter
                    this.registry.set('fixed_floor_counter', true);
                    
                    // Add journal entry about the floor counter repair tool
                    if (!this.hasJournalEntry('floor_counter_tool')) {
                        this.addJournalEntry(
                            'floor_counter_tool',
                            'Elevator Calibration Tool',
                            'Captain Liris provided me with a specialized calibration tool to repair the broken floor counter in the Lift Mother\'s system. This symbiotic interface bridges old electronic systems with new mycelial networks, allowing me to access restricted floors like Dr. Elphi\'s studio on level 177-Quiet.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Captain Liris', location: 'Skyship' }
                        );
                    }
                    
                    // Update the find_bishop quest if active
                    if (this.questSystem.getQuest('find_bishop')) {
                        this.questSystem.updateQuest('find_bishop', 'Captain Liris gave me a calibration tool to repair the Lift Mother\'s floor counter, which should allow me to access Dr. Elphi\'s studio.', 'got_floor_counter_tool');
                    }
                    
                    // Show notification
                    this.showNotification('Obtained: Elevator Calibration Tool', '', '', 5000);
                }
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
        return { ...parentContent, ...skyshipContent };
    }

    update() {
        super.update();

        // Check Growth/Decay effects on symbionts if applicable
        if (this.symbiontSystem) {
            const growth = this.registry.values.growth || 0;
            const decay = this.registry.values.decay || 0;
            const effect = this.symbiontSystem.checkDecayGrowthEffects(decay, growth);
            
            if (effect) {
                if (effect.type === 'leave') {
                    this.showNotification(effect.message, 0xff0000);
                }
            }
        }
    }
}
