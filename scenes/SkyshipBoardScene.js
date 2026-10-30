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
        this.preloadMusic('flightGuitar');
        this.load.image('skyshipBoardBg', 'assets/images/backgrounds/skyship_board.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
        this.load.spritesheet('captainLiris', 'assets/images/characters/liris_idle.png', { frameWidth: 128, frameHeight: 160 });
    }

    create() {
        super.create();
        this.playSceneMusic('flightGuitar');

        // Set skyship board background
        // Native 1067×600 (tools/artgen/board_bg.py): the gondola deck under the moss-netted bladder
        this.background = this.add.image(400, 300, 'skyshipBoardBg');
        this.fitBackground(this.background);
        this.background.setDepth(-1);
        // The background paints its own deck; the generic ground strip would cover it.
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }

        // Add exit area to go back to CrossroadScene: the rope ladder hooked over the rail by the bow
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
        const exitText = this.add.text(100, 550, this.t('ui.hints.returnToCity'), {
            fontSize: '16px',
            fill: '#7fff8e',
            align: 'center'
        });
        exitText.setOrigin(0.5);
        exitText.setDepth(10);

        // Examine: the dial-board itself (the grown instrument with the green lens, centre back). Knows-tier once
        // the floor-counter's taken.
        this.createObservable(400, 420, 80, 110, () => {
            if (this.hasJournalEntry('floor_counter_tool')) return this.t('observe.skyship_board.knows');
            return this.t('observe.skyship_board.default');
        }, { hint: this.t('observe.skyship_board.hint') });

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);

        // Setup scene transitions
        this.setupSceneTransitions();
        
        // Add Captain Liris
        this.createCaptainLiris();
    }

    createCaptainLiris() {
        // Captain Liris (tools/artgen/liris.py): 8 idle frames of 128×160 at scale 1, soles on the deck walk line
        this._lirisHoverFx = null;  // the scene instance is reused: drop a glow left on the previous run's sprite
        const lx = 700, feet = 533;
        if (!this.anims.exists('liris_idle')) {
            // breath, a blink, the monocle's lens clicking round, a gust through the scarf and coat, a touch to the monocle
            this.anims.create({
                key: 'liris_idle',
                frames: this.anims.generateFrameNumbers('captainLiris', { frames: [0, 0, 1, 1, 0, 0, 2, 0, 0, 1, 1, 0, 3, 3, 0, 0, 4, 5, 5, 4, 0, 1, 1, 0, 0, 6, 6, 6, 7, 0, 0, 0] }),
                frameRate: 4,
                repeat: -1
            });
        }
        this.captainLiris = this.add.sprite(lx, feet, 'captainLiris', 0).setOrigin(0.5, 1).setDepth(6);
        this.captainLiris.play('liris_idle');
        this.addGroundShadow(lx, feet - 4, 40, 10);
        this.captainLiris.setInteractive({ useHandCursor: true });
        // bust portrait for her dialogs (EN + CZ speaker names)
        const bust = { key: 'captainLiris', frame: 0, zoom: 2, top: 10 };
        this.dialogPortraits = { ...(this.dialogPortraits || {}), 'Captain Liris': bust, 'Kapitánka Liris': bust };

        // Hover: a soft glow round her (pixel art isn't scaled)
        this.captainLiris.on('pointerover', () => {
            if (!this._lirisHoverFx) this._lirisHoverFx = this.captainLiris.preFX?.addGlow(0x7fff8e, 2, 0, false, 0.1, 8);
        });
        this.captainLiris.on('pointerout', () => {
            if (this._lirisHoverFx) { this.captainLiris.preFX?.remove(this._lirisHoverFx); this._lirisHoverFx = null; }
        });
        
        // Add click interaction to show dialog
        this.captainLiris.on('pointerdown', () => {
            this.showDialog('captainMain');
        });
        
        // Add a name tag below the captain
        const captainText = this.add.text(lx, 548, this.t('ui.hotspots.captainLiris'), {
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

    /** Run a side effect only the first time its key is seen in this scene instance. */
    once(key, fn) {
        this._rewarded = this._rewarded || new Set();
        if (this._rewarded.has(key)) return;
        this._rewarded.add(key);
        fn();
    }

    get dialogContent() {
        // Combine parent dialog content with this scene's content
        const parentContent = super.dialogContent || {};
        
        // Define this scene's dialog content
        const skyshipContent = {
            speaker: 'Captain Liris',
            main: {
                speaker: 'Narrator',
                text: 'You find yourself on the deck of a skyship. The air is thin up here, and you can see the city sprawled below.',
                options: [
                    {
                        text: 'Look around',
                        key: 'look_around',
                        next: 'lookAround'
                    },
                ]
            },
            lookAround: {
                speaker: 'Narrator',
                text: 'The skyship appears to be a transport vessel. Various strange plants line the edges of the deck, seemingly serving as both decoration and structural support. The ship sways gently in the wind.',
                options: [
                    {
                        text: 'Ask something else',
                        key: 'other_topics',
                        next: 'main'
                    }
                ]
            },
            captainMain: {
                moodNpc: 'liris',
                text: "Ah, a visitor! Welcome aboard the Verdigrace. I'm Captain Liris, navigator of the aerial currents and keeper of this fine vessel. What brings you to my ship?",
                options: [
                    {
                        text: 'How does this ship fly?',
                        key: 'how_does_this_ship_fly',
                        next: 'captainTechnology'
                    },
                    {
                        text: 'Where are you headed?',
                        key: 'where_are_you_headed',
                        next: 'captainDestination'
                    },
                    {
                        text: 'Tell me about yourself.',
                        key: 'tell_me_about_yourself',
                        next: 'captainAbout'
                    },
                    {
                        text: 'Is flying dangerous?',
                        key: 'is_flying_dangerous',
                        next: 'captainDanger'
                    },
                    {
                        text: 'What cargo do you carry?',
                        key: 'what_cargo_do_you_carry',
                        next: 'captainCargo'
                    },
                    ...(this.hasJournalEntry('lift_mother_meeting') ? [{
                        text: 'I need help with an elevator system.',
                        key: 'i_need_help_with_an_elevator_system',
                        next: 'captainElevator'
                    }] : []),
                    ...(this.hasJournalEntry('met_infinite_fold') ? [{
                        text: "[Before entering the cathedral] You watch that egg from up here. Tell me what you see.",
                        key: 'before_entering_liris',
                        next: 'lirisPerspective'
                    }] : []),
                ],
                onTrigger: () => {
                    // Add journal entry for meeting Captain Liris if not already added
                    if (!this.hasJournalEntry('captain_liris_meeting')) {
                        this.addJournalEntry(
                            'captain_liris_meeting',
                            'Captain Liris of the Verdigrace',
                            'Aboard the skyship, I met Captain Liris, an imposing figure in an ornate uniform who commands the vessel known as the Verdigrace.',
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
                        key: 'what_is_the_lumen_directorate',
                        next: 'captainAccord'
                    },
                    {
                        text: 'Ask something else',
                        key: 'other_topics',
                        next: 'captainMain'
                    }
                ]
            },
            captainAccord: {
                text: "The Lumen Directorate is a powerful organization, you know? We strive for the fusion of mind and flora. We are keepers and protectors of everything that grows. We are the guardians of life.",
                options: [
                    {
                        text: 'Ask something else',
                        key: 'other_topics',
                        next: 'captainMain'
                    },
                    {
                        text: "What is your mission?",
                        key: 'what_is_you_mission',
                        next: "captainMission"
                    },
                    {
                        text: "Does the Lumen Directorate have enemies?",
                        key: 'does_lumen_directorate_have_some_enemies',
                        next: "captainEnemies"
                    }
                ],
                onTrigger: () => this.once('captainAccord', () => this.modifyFactionReputation('LumenDirectorate', 10))
            },
            captainMission: {
                text: "We are on a mission to search and gather rare specimens for the Lumen Directorate. But we are still waiting for more specs, so we don't mind that little ladder of yours.",
                options: [
                    {
                        text: 'Ask something else',
                        key: 'other_topics',
                        next: 'captainMain'
                    }
                ],
                onTrigger: () => {
                    this.addJournalFact('lumen_directorate_faction', 'specimens', "Their people go on missions to gather rare specimens — Captain Liris is on one now.");
                }
            },
            captainEnemies: {
                text: "Sure, we have some enemies, as everybody. Especially that Rust Choir scum, but that's hardly surprising.", 
                options: [
                    {
                        text: 'Ask something else',
                        key: 'other_topics',
                        next: 'captainMain'
                    }
                ],
                onTrigger: () => {
                    this.once('captainEnemies', () => this.modifyFactionReputation('LumenDirectorate', 10));
                    if (!this.hasJournalEntry('lumen_directorate_faction')) {
                        this.addJournalEntry(
                            'lumen_directorate_faction',
                            'The Lumen Directorate',
                            'The Lumen Directorate is a powerful faction dedicated to the fusion of mind and flora. They are keepers and protectors of everything that grows, acting as guardians of life itself.',
                            this.journalSystem.categories.FACTIONS,
                            { faction: 'Lumen Directorate', location: 'Skyship' }
                        );
                    }
                }
            },
            captainTechnology: {
                text: "Fascinating, isn't it? The ship's hull is infused with a special strain of buoyant plants. They create microscopic gas pockets that give us lift. The organic sails catch the wind currents, and the rudder fungi respond to my commands through a symbiotic bond. I've been connected to this ship for over twenty cycles now.",
                options: [
                    {
                        text: 'That sounds dangerous.',
                        key: 'that_sounds_dangerous',
                        next: 'captainDanger'
                    },
                    {
                        text: 'Ask something else',
                        key: 'ask_something_else',
                        next: 'captainMain'
                    }
                ]
            },
            
            captainDanger: {
                text: "Ha! Life without risk is no life at all. Yes, there are dangers here—storm trees that could swallow us whole, predatory flying blackberries that hunt in the heights, and other horrors. But the freedom of the skies... that's worth any risk.",
                options: [
                    {
                        text: 'Ask something else',
                        key: 'other_topics',
                        next: 'captainMain'
                    }
                ]
            },
            captainDestination: {
                text: "We are monitoring the regular dandelion clouds circling over the continent. Next stop is the Hanging Gardens of Mycora, where we'll trade goods for rare cultivation specimens. After that, perhaps the floating research outposts of the Eastern Canopy. The winds decide our ultimate path.",
                options: [
                    {
                        text: 'Could I travel with you?',
                        key: 'could_i_travel_with_you',
                        next: 'captainTravel'
                    },
                    {
                        text: 'Ask something else',
                        key: 'ask_something_else',
                        next: 'captainMain'
                    }
                ],
                onTrigger: () => {
                    this.addJournalFact('captain_liris_meeting', 'routes', "The ship travels the aerial trade routes between far-flung settlements and research outposts, wherever the winds allow.");
                }
            },
            captainTravel: {
                text: "Perhaps someday, friend. But not on this journey. The ship has... chosen its crew already. I can sense it's not ready to bond with you yet. Return when you've proven your worth. The Verdigrace is particularly picky about who it accepts. If you really mean it, visit the Lumen Directorate headquarters in the city and ask about joining the crew. They might have some tasks for you to prove your dedication.",
                options: [
                    {   text: 'Where can I find the Lumen Directorate headquarters?',
                        key: 'where_can_i_find_the_lumen_directorate_headquarter',
                        next: 'captainDirectorate'
                    },
                    {
                        text: 'Ask something else',
                        key: 'other_topics',
                        next: 'captainMain'
                    }
                ]
            },
            captainDirectorate: {
                text: "The Lumen Directorate headquarters is located in the heart of the city, near the main square. It's quite a building, you can't miss it.",
                options: [
                    {
                        text: 'Thank you! I have some other questions.',
                        key: 'thank_you_i_have_some_other_questions',
                        next: 'captainMain'
                    }
                ],
                onTrigger: () => {
                    this.once('captainDirectorate', () => this.modifyFactionReputation('LumenDirectorate', 5));
                    if (!this.questSystem.getQuest('find_lumen_directorate')) {
                        this.questSystem.addQuest('find_lumen_directorate', 'Nothing Hidden. Nothing Lost', "I'd like to join the Lumen Directorate. I should learn more about their work and find out what it takes to become one of them.");
                    }
                    // the description is shared with Verrik's route; Liris's directions are their own update
                    this.questSystem.updateQuest('find_lumen_directorate', "Captain Liris gave me directions to the Lumen Directorate headquarters, near the main square. Joining them might earn me a place on the Verdigrace's crew.", 'liris_directions');
                }
            },
            captainCargo: {
                text: "Primarily rare spores and mycelia that can't be cultivated in the city. Specialized symbiont strains, crystallized growth enzymes, decay-resistant building materials. We also carry messages between the scattered aerial colonies and research stations. Information is perhaps our most valuable cargo—knowledge that would never reach the ground otherwise.",
                options: [
                    {
                        text: 'Do you have anything to trade?',
                        key: 'do_you_have_anything_to_trade',
                        next: 'captainTrade'
                    },
                    {
                        text: 'Ask something else',
                        key: 'ask_something_else',
                        next: 'captainMain'
                    }
                ],
                onTrigger: () => {
                    this.addJournalFact('captain_liris_meeting', 'cargo', "It carries rare spores, mycelia and symbiont strains — and information, which she calls its most valuable cargo.");
                }
            },
            captainTrade: {
                text: "Not at the moment, I'm afraid. We've just begun our journey and haven't collected any goods yet. Return after we've made our first circuit—perhaps in a few cycles—and I might have something unique for an intrepid explorer like yourself. Keep an eye on the skies for our return.",
                options: [
                    {
                        text: 'Ask something else',
                        key: 'other_topics',
                        next: 'captainMain'
                    }
                ]
            },
            
            captainElevator: {
                text: "An elevator system, you say? Ah, you must be referring to one of those ancient vertical transport mechanisms in the city's towers. Those old systems are fascinating—a blend of mechanical engineering and early symbiotic technology. What seems to be the issue?",
                options: [
                    {
                        text: 'The floor counter is broken.',
                        key: 'the_floor_counter_is_broken',
                        next: 'captainFloorCounter'
                    },
                    {
                        text: 'Never mind, ask something else.',
                        key: 'never_mind_ask_something_else',
                        next: 'captainMain'
                    }
                ]
            },
            
            captainFloorCounter: {
                text: "A floor counter malfunction? That's a common issue with the lift systems. The numeric displays were designed to handle simple tasks like going up and down, but the engineers didn't reckon with sentient elevators. I happen to have developed a specialized calibration tool for just such problems during my time maintaining the aerial dock lifts.",
                options: [
                    {
                        text: 'Could I borrow this tool?',
                        key: 'could_i_borrow_this_tool',
                        next: 'captainGivesTool'
                    },
                    {
                        text: 'How does it work?',
                        key: 'how_does_it_work',
                        next: 'captainToolExplanation'
                    }
                ]
            },
            
            captainToolExplanation: {
                text: "It's a symbiotic interface that bridges old electronic systems with the newly developed lift's intelligent mind. The tool contains a specialized strain of communication micro drones that can translate between digital signals and brain-like impulses. You simply attach it to the counter's maintenance port, and it reestablishes the connection between the mechanical components and the building's new nervous system.",
                options: [
                    {
                        text: 'Could I borrow this tool?',
                        key: 'could_i_borrow_this_tool',
                        next: 'captainGivesTool'
                    },
                    {
                        text: 'Ask something else',
                        key: 'ask_something_else',
                        next: 'captainMain'
                    }
                ],
                onTrigger: () => {
                    this.addJournalFact('floor_counter_tool', 'how_it_works', "It's a symbiotic interface: micro-drones that translate between the old electronics and the lift's new, living mind.");
                }
            },
            
            captainGivesTool: {
                text: "Of course you can! I always carry spares—you never know when you'll need to repair something mid-flight. Here, take this calibration module. It's simple to use: just attach it to the maintenance panel of the elevator system, and it will automatically recalibrate the floor counter. The drones inside will do all the work.",
                options: [
                    {
                        text: 'Thank you!',
                        key: 'thank_you',
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
                            'Captain Liris provided me with a specialized calibration tool to repair the broken floor counter in the Lift-Mother\'s system. With the counter fixed, the lift might reach floors it can\'t get to now.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Captain Liris', location: 'Skyship' }
                        );
                    }
                    
                    // Update the find_bishop quest if active. Nothing here ties the counter to Dr. Elphi's
                    // floor yet — that link is logged at the lift (ScraperInteriorScene, 'liris_tool_hint').
                    if (this.questSystem.getQuest('find_bishop')) {
                        this.questSystem.updateQuest('find_bishop', 'Captain Liris gave me a calibration tool to repair the Lift-Mother\'s floor counter. With the counter fixed, the lift might reach floors it can\'t get to now.', 'got_floor_counter_tool');
                    }
                    
                    // Show notification
                    this.showNotification(this.t('skyship.toolObtained'), '', '', 5000);
                }
            },
            lirisPerspective: {
                onTrigger: () => {
                    this.addJournalFact('skyship_sighting', 'anchored', "Captain Liris says she has been anchored over the Crossroads for about a month, and the ship hasn't moved since.");
                },
                text: "So you're going in. I won't ask what for — that's your business. But I've been anchored over this Crossroads a month now, and I keep the ship's eye on that cathedral because it's the most interesting thing on the continent. You want the truth? It isn't static. It never was. The old survey charts I inherited put the shell three spans shorter and the eastern buttress where there's now open air. The Verdigrace logs it every watch. That thing is growing while everyone below stands around arguing whose god it belongs to.",
                options: [
                    {
                        text: 'Show me the records.',
                        key: 'show_me_the_records',
                        next: 'lirisRecords'
                    },
                    {
                        text: 'What happens when I come back out?',
                        key: 'what_happens_when_i_come_back_out',
                        next: 'lirisReturn'
                    },
                    {
                        text: 'Ask something else',
                        key: 'other_topics',
                        next: 'captainMain'
                    }
                ]
            },
            lirisRecords: {
                text: "Here — the current chart against the last Directorate survey. The outline's changed by more than weather could explain. The scripture-light patterns drift, then settle into new shapes, always more ordered than the last. Structural mass keeps climbing, watch after watch. I've charted storms, migrations, whole colonies dissolving into spore — I know what a thing looks like when it's dying, and I know what a thing looks like when it's building toward something. That cathedral is building. Slowly, patiently, toward a shape it hasn't shown us yet.",
                options: [
                    {
                        text: 'What happens when I come back out?',
                        key: 'what_happens_when_i_come_back_out',
                        next: 'lirisReturn'
                    },
                    {
                        text: 'Ask something else',
                        key: 'other_topics',
                        next: 'captainMain'
                    }
                ],
                onTrigger: () => {
                    this.addJournalFact('perspective_liris', 'records', "Her records show more than growth: the scripture-light drifts and settles into ever more ordered patterns, and the structural mass keeps climbing. Whatever is inside, it is building toward a shape no one has seen yet.");
                }
            },
            lirisReturn: {
                text: "One more thing, and then I'll leave you to it. I don't know what you found in there. But I know someone should be outside when you come back out. So here's my offer: when you're done behind the Veil, signal from the cathedral steps and the Verdigrace will drop a line. A lift out — a way home, wherever home is for you now. Whatever that egg becomes, you won't have to walk away from it alone.",
                options: [
                    {
                        text: 'Thank you, Captain.',
                        key: 'thank_you_captain',
                        next: 'closeDialog'
                    },
                    {
                        text: 'Ask something else',
                        key: 'other_topics',
                        next: 'captainMain'
                    }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('perspective_liris')) {
                        this.addJournalEntry(
                            'perspective_liris',
                            'Liris — A Watcher from Above',
                            "Before I entered the Egg Cathedral, Captain Liris told me what the Verdigrace has seen from the sky. The cathedral is not static — her survey charts show the shell growing, watch after watch. She offered a lift out when I am done: signal from the steps and the Verdigrace will drop a line. \"I don't know what you found in there. But I know someone should be outside when you come back out.\"",
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Captain Liris', location: 'Verdigrace Skyship' }
                        );
                    }
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
