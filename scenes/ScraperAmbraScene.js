import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class ScraperAmbraScene extends GameScene {
    constructor() {
        super({ key: 'ScraperAmbraScene' });
        this.isTransitioning = false; // Add flag to track transition state
    }

    preload() {
        super.preload();
        this.load.image('scraperAmbraBg', 'assets/images/backgrounds/ScraperAmbra.png');
        this.load.image('drElphi', 'assets/images/characters/DrElphi.png');
        
        // Make sure sounds are loaded
        if (!this.sound.get('click')) {
            this.load.audio('click', 'assets/audio/click.mp3');
        }
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        this.playSceneMusic('dr_elphi_theme');

        // Set background
        const bg = this.add.image(400, 300, 'scraperAmbraBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Add fade-in effect
        this.cameras.main.fadeIn(1200, 0, 0, 0);
        
        // Position the priest at the center when entering this scene
        this.priest.x = 400;
        this.priest.y = 450; // Position on the ground
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }
        
        // Create exit back to Scraper Interior
        this.transitionManager.createTransitionZone(
            400, // x position
            550, // y position
            200, // width
            50, // height
            'down', // direction
            'ScraperInteriorScene', // target scene
            400, // walk to x
            300 // walk to y
        );
        
        // Add a hint about the exit
        const exitHint = this.add.text(400, 520, 'Back to Elevator', {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        exitHint.setOrigin(0.5);
        exitHint.setAlpha(0);
        exitHint.setDepth(10);
        
        // Show hint when hovering near the exit
        this.input.on('pointermove', (pointer) => {
            // Check if pointer is near the exit area
            if (Math.abs(pointer.x - 400) < 100 && Math.abs(pointer.y - 550) < 50) {
                exitHint.setAlpha(1);
            } else {
                exitHint.setAlpha(0);
            }
        });
        
        // Add ambient elements
        this.createAmbientElements();
        
        // Add Dr. Elphi Quarn NPC
        this.createDrElphi();
        
        // Update the find_bishop quest if it exists and is not complete
        const questSystem = this.registry.get('questSystem');
        const findBishopQuest = questSystem?.getQuest('find_bishop');
        if (findBishopQuest && !findBishopQuest.isComplete) {
            questSystem.updateQuest('find_bishop', 'I\'ve reached Dr. Elphi\'s studio on floor 177-Quiet. Now I need to find clues about the Bishop.', 'reached_elphi_studio');
        }
        
        // Show a welcome notification
        this.time.delayedCall(1000, () => {
            this.showNotification('Floor 177-Quiet: Dr. Elphi\'s Studio', 0x7fff8e);
        });
    }
    
    /**
     * Create ambient elements for the scene
     */
    createAmbientElements() {
        // Add some floating spores/particles
        for (let i = 0; i < 30; i++) {
            const x = Math.random() * 800;
            const y = Math.random() * 400 + 100;
            const size = Math.random() * 3 + 1;
            
            const particle = this.add.circle(x, y, size, 0x7fff8e, 0.4);
            particle.setDepth(3);
            
            // Add floating movement
            this.tweens.add({
                targets: particle,
                x: x + (Math.random() * 100 - 50),
                y: y + (Math.random() * 60 - 30),
                alpha: { from: 0.4, to: 0.1 },
                duration: 3000 + Math.random() * 2000,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
        }
        
        // Add a subtle green glow effect to the scene
        const ambientGlow = this.add.graphics();
        ambientGlow.fillStyle(0x7fff8e, 0.05);
        ambientGlow.fillRect(0, 0, 800, 600);
        ambientGlow.setDepth(2);
        
        // Add pulsating effect to the glow
        this.tweens.add({
            targets: ambientGlow,
            alpha: { from: 0.05, to: 0.1 },
            duration: 4000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
    }
    
    get dialogContent() {
        const bishopDead = !!this.questSystem?.getQuest('who_killed_bishop');
        const hasBruising = !!this.hasJournalEntry('bishop_bruising');
        const hasCartridge = !!this.hasJournalEntry('bishop_cartridge');
        const hasHelmet = !!this.hasJournalEntry('bishop_helmet');
        const hasJournal = !!this.hasJournalEntry('bishop_journal');
        const hasMemo = !!this.hasJournalEntry('bishop_memo');
        const hasBerries = !!this.hasJournalEntry('bishop_berries');
        const hasDissection = !!this.hasJournalEntry('bishop_dissection');
        const discussedBruising = !!this.hasJournalEntry('elphi_bruising_analysis');
        const discussedCartridge = !!this.hasJournalEntry('elphi_cartridge_analysis');
        const discussedHelmet = !!this.hasJournalEntry('elphi_helmet_analysis');
        const discussedMemo = !!this.hasJournalEntry('elphi_memo_analysis');
        const discussedJournal = !!this.hasJournalEntry('elphi_journal_analysis');
        const discussedDissection = !!this.hasJournalEntry('elphi_dissection_analysis');
        const discussedBerries = !!this.hasJournalEntry('elphi_berries_analysis');
        const allCluesDiscussed = (!hasBruising || discussedBruising) && (!hasCartridge || discussedCartridge) && (!hasHelmet || discussedHelmet) && (!hasMemo || discussedMemo) && (!hasJournal || discussedJournal) && (!hasDissection || discussedDissection) && (!hasBerries || discussedBerries) && (hasBruising || hasCartridge || hasHelmet || hasMemo || hasJournal || hasDissection || hasBerries);
        const readyForDay2 = !!this.hasJournalEntry('elphi_ready_for_day2');

        return {
            ...super.dialogContent,
            speaker: 'Dr. Elphi',
            
            elphi_studio_intro: {
                text: "Dr. Elphi's studio is eerily quiet. Workstations with glowing screens line the walls, each displaying fragments of code and strange designs. The air feels charged with creative energy, but there's no sign of Dr. Elphi herself.",
                options: [
                    { text: "Continue exploring", next: "closeDialog" }
                ]
            },
            
            // Dr. Elphi Quarn dialog tree
            dr_elphi_start: {
                text: bishopDead
                    ? "You're back. I can see it on your face. Something happened to her, didn't it?"
                    : "Hm. You're not scheduled. Not tagged either. Let me guess — someone wants a neural tuning, a performance consultation, or you've come to warn me about 'metaphysical leakage' again.",
                options: [
                    ...(!bishopDead ? [
                        { text: "I'm looking for someone. The Bishop.", next: "dr_elphi_bishop_path" },
                        { text: "I was sent to investigate an anomaly. Might be connected to this place.", next: "dr_elphi_anomaly_path" },
                        { text: "I heard you design dream-based games.", next: "dr_elphi_games_path" },
                        { text: "I'll explain if you stop testing me.", next: "dr_elphi_testing_path" }
                    ] : []),
                    ...(bishopDead ? [
                        { text: "The Bishop is dead. I found her body in the backyard.", next: "dr_elphi_bishop_dead" }
                    ] : []),
                    ...(bishopDead && (hasBruising || hasCartridge || hasHelmet || hasMemo || hasJournal || hasDissection) ? [
                        { text: "I need your expertise. I found some clues.", next: "dr_elphi_clues_hub" }
                    ] : []),
                ],
                onTrigger: () => {
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && questSystem.getQuest('level_177_access') && !questSystem.getQuest('level_177_access').isComplete) {
                        questSystem.completeQuest('level_177_access');
                    }
                    // Trigger any animations or effects when dialog starts
                    if (this.drElphi) {
                        this.tweens.add({
                            targets: this.drElphi,
                            y: this.drElphi.y - 10,
                            duration: 300,
                            yoyo: true,
                            ease: 'Sine.easeOut'
                        });
                    }
                }
            },
            
            dr_elphi_bishop_path: {
                text: "The Bishop? Well, you're late. She came here. Often, actually. Always for simulations. Never politics.\n\nShe liked the softer ones. Immersive fictions, drift environments. The Cardinal Feast was a favorite.\n\nLast I saw her? Three days ago, maybe four. She ended her session, said she might stay outside awhile. She had a key to the backyard.\n\nI didn't think much of it. She seemed… distracted. More than usual.",
                options: [
                    { text: "What's in the backyard?", next: "dr_elphi_backyard_info" },
                    { text: "Did she say where she was going?", next: "dr_elphi_bishop_destination" },
                    { text: "I'll go look for her there.", next: "dr_elphi_exit" }
                ],
                onTrigger: () => {
                    // Update the find_bishop quest to direct to Shard backyard
                    const questSystem = this.registry.get('questSystem');
                    const findBishopQuest = questSystem?.getQuest('find_bishop');
                    if (findBishopQuest && !findBishopQuest.isComplete) {
                        questSystem.updateQuest('find_bishop', 'Dr. Elphi mentioned the Bishop was last seen in the Shard backyard. I should check there next.', 'check_shard_backyard');
                    }
                }
            },
            
            dr_elphi_anomaly_path: {
                text: "If there's an anomaly, it isn't from me. All test environments are sandboxed. At worst, they collapse privately.\n\nUnless you mean her. The Bishop ran a few sessions recently. She didn't say what she was avoiding, but something had her on edge.\n\nShe had a habit of sitting out back after play — the old transit yard. She hasn't come in days.\n\nHere.",
                options: [
                    { text: "What was she avoiding?", next: "dr_elphi_bishop_concerns" },
                    { text: "What's in the backyard?", next: "dr_elphi_backyard_info" },
                    { text: "I'll investigate the backyard.", next: "dr_elphi_exit" }
                ],
                onTrigger: () => {
                    // Update the find_bishop quest to direct to Shard backyard
                    const questSystem = this.registry.get('questSystem');
                    const findBishopQuest = questSystem?.getQuest('find_bishop');
                    if (findBishopQuest && !findBishopQuest.isComplete) {
                        questSystem.updateQuest('find_bishop', 'Dr. Elphi mentioned the Bishop was last seen in the Shard backyard. I should check there next.', 'check_shard_backyard');
                    }
                }
            },
            
            dr_elphi_games_path: {
                text: "I make them. Dream architecture. Neurofiction. Post-sensory architecture.\n\nYou're standing in ARB Ambra — and no, the initials don't stand for anything. They just sound better that way.\n\nWhat did you hear exactly?",
                options: [
                    { text: "The Bishop came here to play.", next: "dr_elphi_bishop_path" },
                    { text: "Something went wrong. I'm following the trace.", next: "dr_elphi_anomaly_path" },
                    { text: "Never mind.", next: "dr_elphi_exit" }
                ]
            },
            
            dr_elphi_testing_path: {
                text: "Testing is how I stay alive. Most visitors lie. Some of them don't even know it.\n\nBut fine. Speak clearly. This floor costs me processing cycles.",
                options: [
                    { text: "I'm looking for the Bishop.", next: "dr_elphi_bishop_path" },
                    { text: "There's been a signal anomaly.", next: "dr_elphi_anomaly_path" }
                ]
            },
            
            dr_elphi_bishop_destination: {
                text: "No. She never does. The Bishop moves in patterns only she understands. But she always returns to the Cathedral eventually.\n\nThis time feels different though. She was... preoccupied with something in the old transit yard. Said the moss there was 'singing' to her. Typical Cathedral mysticism.",
                options: [
                    { text: "I'll go look for her there.", next: "dr_elphi_exit" },
                    { text: "What's in the backyard?", next: "dr_elphi_backyard_info" }
                ]
            },
            
            dr_elphi_bishop_concerns: {
                text: "She wouldn't say directly. Something about 'resonance patterns' and 'harmonic disturbances.' Cathedral business, I assumed.\n\nBut she spent more time in the simulations than usual. Almost like she was hiding. Or preparing for something.",
                options: [
                    { text: "I should check the backyard.", next: "dr_elphi_exit" },
                    { text: "Tell me about this backyard.", next: "dr_elphi_backyard_info" }
                ]
            },
            
            dr_elphi_backyard_info: {
                text: "It's an old transit yard. Abandoned decades ago when the new lines were built. Now it's mostly overgrown with that peculiar moss.\n\nThe Bishop seemed fascinated by it. Said it had 'mnemonic properties.' Whatever that means. Cathedral folk and their cryptic terminology...",
                options: [
                    { text: "I'll go investigate.", next: "dr_elphi_exit" },
                    { text: "Is it dangerous?", next: "dr_elphi_backyard_danger" }
                ]
            },
            
            dr_elphi_backyard_danger: {
                text: "Not conventionally. But nothing around is truly safe, is it? The moss remembers things. Sometimes it... shares those memories. Unpredictably.\n\nJust don't fall asleep out there. The dreams can be... intense.",
                options: [
                    { text: "I'll be careful.", next: "dr_elphi_exit" }
                ]
            },
            
            dr_elphi_exit: {
                text: "I'm not hiding anything. If something happened to her, I didn't see it.\n\nBut you might.\n\nCome back if you find something. Here, take my key to the backyard.",
                options: [
                    { text: "I'll check the backyard.", next: "closeDialog" },
                    { text: "Thanks for the information.", next: "closeDialog" }
                ],
                onTrigger: () => {
                    this.addItemToInventory({
                        id: 'scraper_backyard_key',
                        name: "Backyard Key",
                        description: "A key to the Scraper 1140 backyard. It seems to glow faintly with possibility.",
                        stackable: false
                    });
                    // Show a notification about the updated quest
                    this.time.delayedCall(500, () => {
                        this.showNotification('Quest Updated: Find the Bishop', 0x7fff8e);
                    });
                }
            },

            // === Post-Bishop-death dialog tree ===

            dr_elphi_bishop_dead: {
                text: `Dead. *She stops typing. Her hands hover motionless over the console.* Dead how? Where? In the backyard? I gave her that key myself.\n\nI assumed she was meditating. She did that sometimes — sat among the moss for hours. I didn't check.\n\nI should have checked.`,
                options: [
                    { text: "She was inside an abandoned bus.", next: "dr_elphi_dead_bus" },
                    { text: "It doesn't look like natural causes.", next: "dr_elphi_dead_unnatural" },
                    ...(hasBruising || hasCartridge || hasHelmet || hasMemo || hasJournal || hasDissection ? [
                        { text: "I found clues. I could use your expertise.", next: "dr_elphi_clues_hub" }
                    ] : []),
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('elphi_told_bishop_dead')) {
                        this.addJournalEntry(
                            'elphi_told_bishop_dead',
                            'Dr. Elphi Learns of the Bishop\'s Death',
                            'I told Dr. Elphi that the Bishop is dead. She seemed genuinely shaken — she had given the Bishop a key to the backyard and assumed she was meditating out there. She hadn\'t checked on her.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn', location: 'Scraper Ambra' }
                        );
                    }
                }
            },

            dr_elphi_dead_bus: {
                text: `The old transit bus? She went there sometimes. Said it was "outside the signal." Whatever she meant by that.\n\nShe was afraid of being observed. Not by people — by something else. She never elaborated.`,
                options: [
                    { text: "Observed by what?", next: "dr_elphi_dead_observed" },
                    ...(hasBruising || hasCartridge || hasMemo ? [
                        { text: "I found evidence that might explain what happened.", next: "dr_elphi_clues_hub" }
                    ] : []),
                ]
            },

            dr_elphi_dead_unnatural: {
                text: `Not natural. *She exhales slowly.* No. I wouldn't expect it to be. She'd been paranoid for weeks. Kept running the same game over and over — The Cardinal Feast. An RPG about a lizard cardinal. Harmless, really. Popular title.\n\nBut she played it obsessively. Said she needed to "find someone inside." I told her it's just a game — there's nobody to find in there.\n\nShe didn't agree.`,
                options: [
                    { text: "What is The Cardinal Feast exactly?", next: "dr_elphi_cardinal_feast_explained" },
                    ...(hasBruising || hasCartridge || hasMemo ? [
                        { text: "I found some clues at the scene.", next: "dr_elphi_clues_hub" }
                    ] : []),
                ]
            },

            dr_elphi_dead_observed: {
                text: `She never said directly. But after sessions, she'd sometimes whisper about "the reflection" — something she glimpsed inside The Cardinal Feast that recognized her back.\n\nI assumed it was dream bleed. Neural residue. Common side effect of deep immersion.\n\nBut she was insistent it was real.`,
                options: [
                    { text: "That matches something I found.", next: "dr_elphi_clues_hub" },
                    { text: "What is The Cardinal Feast?", next: "dr_elphi_cardinal_feast_explained" },
                ]
            },

            dr_elphi_cardinal_feast_explained: {
                text: `The Cardinal Feast? It's an RPG — a fantasy game. You play as a lizard cardinal who's a cannibal. He needs to lure more lizard folk to his feasts so he can eat them. It's dark humor, but it's just a game. One of our more popular titles, actually.\n\nThere's nothing dangerous about it. No hidden layers, no experimental code. Just a standard neurofiction rendered through the dream helmet.\n\nBut the Bishop played it over and over. Dozens of sessions. She kept saying she saw something between the scenes — someone watching her from inside the game. I checked the code myself. There's nothing there.`,
                options: [
                    ...(hasCartridge ? [
                        { text: "I found the dream cartridge. It showed some kind of error.", next: "dr_elphi_clues_cartridge" }
                    ] : []),
                    { text: "Could the dream program have killed her?", next: "dr_elphi_dream_kill" },
                    { text: "Back to the clues.", next: "dr_elphi_clues_hub" },
                ]
            },

            dr_elphi_dream_kill: {
                text: `In theory? No. The helmets have failsafes. Neural load limiters, session timeouts, emergency disconnects.\n\nBut if someone modified the cartridge — removed the limiters, injected a feedback loop — then yes. A sufficiently corrupted dream could overwhelm the neural pathways. Death by recursive experience.\n\nIt would look exactly like what you described. No wounds. Just... stopped.`,
                options: [
                    { text: "Who could modify a cartridge like that?", next: "dr_elphi_who_modified" },
                    { text: "Back to the clues.", next: "dr_elphi_clues_hub" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('elphi_dream_kill_theory')) {
                        this.questSystem.updateQuest('who_killed_bishop', 'Dr. Elphi confirmed that a corrupted dream cartridge could cause death by neural overload — "death by recursive experience." The failsafes would have to be deliberately removed. Someone tampered with The Cardinal Feast.', 'elphi_dream_kill');
                        this.addJournalEntry(
                            'elphi_dream_kill_theory',
                            'Death by Recursive Experience',
                            'Dr. Elphi explained that dream helmets have neural failsafes, but a deliberately corrupted cartridge — with limiters removed and a feedback loop injected — could cause fatal neural overload. She called it "death by recursive experience." This means the Bishop\'s death was likely murder, not accident.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn' }
                        );
                    }
                }
            },

            dr_elphi_who_modified: {
                text: `Me, obviously. I designed the system. But I didn't.\n\nAnyone with access to the dream architecture could do it. That means someone at ARB Ambra — a former employee, maybe. Or someone who stole the schematics.\n\nDream technology is my invention. The Townhall doesn't keep records of how it works — they barely understand it. But the Bishop had that Townhall memo on her. That paper might be the real lead. Someone at the Townhall knew something about what was happening to her.`,
                options: [
                    { text: "The Townhall memo — the one about the doppelgänger.", next: "dr_elphi_clues_memo" },
                    { text: "Back to the clues.", next: "dr_elphi_clues_hub" },
                ]
            },

            // === Clues discussion hub ===

            dr_elphi_clues_hub: {
                text: `Show me what you've found. I may not be an investigator, but I know dream technology better than anyone in this city.`,
                options: [
                    ...(hasBruising && !discussedBruising ? [
                        { text: "There was bruising at her temples.", next: "dr_elphi_clues_bruising" }
                    ] : []),
                    ...(hasCartridge && !discussedCartridge ? [
                        { text: "She had a dream cartridge — The Cardinal Feast.", next: "dr_elphi_clues_cartridge" }
                    ] : []),
                    ...(hasHelmet && !discussedHelmet ? [
                        { text: "There was a damaged dream helmet.", next: "dr_elphi_clues_helmet" }
                    ] : []),
                    ...(hasMemo && !discussedMemo ? [
                        { text: "I found a strange note about a doppelgänger.", next: "dr_elphi_clues_memo" }
                    ] : []),
                    ...(hasJournal && !discussedJournal ? [
                        { text: "Her journal said: 'The city no longer hears me.'", next: "dr_elphi_clues_journal" }
                    ] : []),
                    ...(hasDissection && !discussedDissection ? [
                        { text: "There was a strange fungal growth inside her body.", next: "dr_elphi_clues_dissection" }
                    ] : []),
                    ...(hasBerries && !discussedBerries ? [
                        { text: "There was a bag of Sulkberries near her body.", next: "dr_elphi_clues_berries" }
                    ] : []),
                    { text: "That's all I have for now.", next: "dr_elphi_clues_done" },
                ]
            },

            dr_elphi_clues_bruising: {
                text: `Bruising at the neural interface points. *She leans forward, studying an invisible pattern in the air.* That's consistent with a feedback surge — the kind you'd get from a dream session without limiters.\n\nNormal helmets cap neural throughput at safe levels. The bruising means something pushed past those limits. Violently.\n\nThis wasn't an accident. Someone removed the safety protocols from her device.`,
                options: [
                    { text: "Could she have done it herself?", next: "dr_elphi_bruising_self" },
                    { text: "Back to other clues.", next: "dr_elphi_clues_hub" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('elphi_bruising_analysis')) {
                        this.questSystem.updateQuest('who_killed_bishop', 'Dr. Elphi confirmed the bruising indicates a feedback surge from a dream session without safety limiters. Someone deliberately removed the safety protocols.', 'elphi_bruising');
                        this.addJournalEntry(
                            'elphi_bruising_analysis',
                            'Dr. Elphi\'s Analysis: Neural Bruising',
                            'Dr. Elphi confirmed that the bruising at the Bishop\'s temples is consistent with a neural feedback surge from a dream session without limiters. Normal helmets cap throughput at safe levels — the bruising means something pushed past those limits violently. According to Elphi, this could not have been an accident.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn' }
                        );
                    }
                }
            },

            dr_elphi_bruising_self: {
                text: `Possible, but unlikely. Removing limiters requires technical knowledge and specific tools. The Bishop was a mystic, not an engineer.\n\nAnd why would she? She was afraid, not suicidal. She was searching for answers, not an exit.`,
                options: [
                    { text: "Back to other clues.", next: "dr_elphi_clues_hub" },
                ]
            },

            dr_elphi_clues_cartridge: {
                text: `*Her eyes widen.* You have the actual cartridge? Let me see.\n\n*She examines it carefully.* The Cardinal Feast — the lizard cannibal RPG. Nothing wrong with the game itself. It's one of our standard titles.\n\n*She plugs it into a diagnostic port.* But the session data... "Runtime loop detected. NULL SCENE." That's the last failsafe. It means something went catastrophically wrong during her final session. The game itself is fine, but whatever happened while she was playing it was not.\n\nI might be able to fix the cartridge and replay her last scene. See exactly where she was in the game when everything went wrong. But it would take time — the data core is damaged.`,
                options: [
                    { text: "How long would it take to fix?", next: "dr_elphi_cartridge_fix_time" },
                    { text: "Who had access to modify this?", next: "dr_elphi_who_modified" },
                    { text: "Back to other clues.", next: "dr_elphi_clues_hub" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('elphi_cartridge_analysis')) {
                        this.questSystem.updateQuest('who_killed_bishop', 'Dr. Elphi confirmed The Cardinal Feast is a normal game — the lizard cannibal RPG. But the session data shows a catastrophic failure during the Bishop\'s final session. Elphi might be able to fix the cartridge and replay the last scene.', 'elphi_cartridge');
                        this.addJournalEntry(
                            'elphi_cartridge_analysis',
                            'Dr. Elphi\'s Analysis: The Cardinal Feast',
                            'Dr. Elphi examined The Cardinal Feast cartridge. The game itself is a standard RPG — nothing suspicious. But the session data shows a catastrophic failure: "Runtime loop detected. NULL SCENE." Something went terribly wrong during the Bishop\'s final session. Elphi offered to fix the damaged data core and replay the Bishop\'s last scene, but it will take time.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn' }
                        );
                    }
                }
            },

            dr_elphi_cartridge_fix_time: {
                text: `Give me until tomorrow. The data core took heavy damage from the loop, but I designed this architecture — I know how to reconstruct corrupted session frames.\n\nI'll need to isolate the last scene the Bishop entered before the crash. If something unusual was happening in the game at that point, I'll find it.\n\nBut first — show me everything else you've found. I want the full picture before I start digging into the dream data.`,
                options: [
                    { text: "Back to other clues.", next: "dr_elphi_clues_hub" },
                ]
            },

            dr_elphi_clues_helmet: {
                text: `The neural interface port was damaged, you say? That's significant. If the port was burned out, it means the signal load exceeded anything the hardware was rated for.\n\nThe helmet was probably the murder weapon — or at least the delivery mechanism. Whoever tampered with the cartridge knew the helmet would channel the feedback directly into her brain.\n\nPortable helmets don't have as many safeguards as my studio beds. She was vulnerable out there alone.`,
                options: [
                    { text: "She had a portable device? Not your studio equipment?", next: "dr_elphi_helmet_portable" },
                    { text: "Back to other clues.", next: "dr_elphi_clues_hub" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('elphi_helmet_analysis')) {
                        this.questSystem.updateQuest('who_killed_bishop', 'Dr. Elphi says the damaged helmet port confirms the signal load was beyond hardware limits. The portable helmet — with fewer safeguards than studio equipment — was the delivery mechanism for the fatal neural feedback.', 'elphi_helmet');
                        this.addJournalEntry(
                            'elphi_helmet_analysis',
                            'Dr. Elphi\'s Analysis: Dream Helmet',
                            'Dr. Elphi confirmed that the damaged neural interface port means the signal load exceeded hardware limits. The portable dream helmet has fewer safeguards than the studio beds, making it the ideal delivery mechanism. The Bishop was specifically vulnerable because she chose to use the portable device alone in the backyard, away from the studio\'s safety systems.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn' }
                        );
                    }
                }
            },

            dr_elphi_helmet_portable: {
                text: `She had her own. Brought it months ago — said she needed to practice outside the studio. I thought it was odd, but the Bishop was always odd.\n\nI offered her supervised sessions instead. She refused. Said the studio "had too many ears."\n\nWhoever killed her knew she'd be using the portable device. Alone. Outside signal range. This was planned.`,
                options: [
                    { text: "Back to other clues.", next: "dr_elphi_clues_hub" },
                ]
            },

            dr_elphi_clues_memo: {
                text: `*She reads the note carefully, then goes very still.*\n\n"Looked like me. Didn't breathe. Didn't blink. And it finished my sentence."\n\n*Long pause.* I have no idea what this is. And I don't say that often. This isn't dream bleed, it's not neural residue, it's not any side effect I've ever documented or theorized.\n\nSomeone — or something — that looked exactly like the Bishop was walking around this city. And based on this memo, the Bishop was scared enough to formally report it.`,
                options: [
                    { text: "This was stamped as a Townhall log.", next: "dr_elphi_memo_townhall" },
                    { text: "Could dream technology cause something like this?", next: "dr_elphi_memo_not_dreams" },
                    { text: "Back to other clues.", next: "dr_elphi_clues_hub" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('elphi_memo_analysis')) {
                        this.questSystem.updateQuest('who_killed_bishop', 'Dr. Elphi couldn\'t explain the doppelgänger from the Bishop\'s memo. It\'s not any known side effect of dream technology. The Bishop formally reported the encounter at the Townhall.', 'elphi_memo');
                        this.addJournalEntry(
                            'elphi_memo_analysis',
                            'Dr. Elphi\'s Analysis: The Doppelgänger',
                            'Dr. Elphi was genuinely unsettled by the Bishop\'s doppelgänger report. She confirmed this is not a known side effect of dream technology — not dream bleed, not neural residue. Something that looked exactly like the Bishop was walking around Upper Morkezela, and the Bishop was frightened enough to formally log the encounter at the Townhall.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn' }
                        );
                    }
                }
            },

            dr_elphi_memo_not_dreams: {
                text: `No. I've built every dream system in this city. I know what they can and can't do. Dreams stay in dreams. They don't walk out of a helmet and start impersonating people.\n\nWhatever the Bishop saw, it wasn't caused by my technology. Which means there's something happening in this city that I don't understand. And that worries me more than the murder itself.`,
                options: [
                    { text: "This was stamped as a Townhall log.", next: "dr_elphi_memo_townhall" },
                    { text: "Back to other clues.", next: "dr_elphi_clues_hub" },
                ]
            },

            dr_elphi_memo_townhall: {
                text: `The Townhall stamps personal logs for bureaucratic purposes — incident reports, mental health audits, formal complaints. It means the Bishop went through official channels with this. She was taking it seriously.\n\nIf it's in the Townhall system, the archive clerk would have a copy. That might tell us when exactly this doppelgänger appeared — and whether anyone else filed a similar report.`,
                options: [
                    { text: "Back to other clues.", next: "dr_elphi_clues_hub" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('elphi_townhall_log')) {
                        this.questSystem.updateQuest('who_killed_bishop', 'The Bishop\'s doppelgänger encounter was formally logged at the Townhall. The archive clerk might have a copy — and records of whether anyone else reported something similar.', 'elphi_townhall_log');
                        this.addJournalEntry(
                            'elphi_townhall_log',
                            'Townhall Records of the Doppelgänger',
                            'The Bishop formally reported the doppelgänger encounter at the Townhall as an official personal log. The archive clerk should have a copy with timestamps that could reveal when this started — and whether anyone else in Upper Morkezela has reported seeing their own double.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn' }
                        );
                    }
                }
            },

            dr_elphi_clues_journal: {
                text: `"The city no longer hears me. Perhaps the dreams will."\n\n*She's quiet for a long moment.* That sounds like disconnection from the myceliar network. The Bishop was a high-level Obazoba cleric — she would have been connected to the network at all times.\n\nIf she lost that connection... she would have been desperate. Isolated. The dreams were her last resort for communication.`,
                options: [
                    { text: "Why would she lose the connection?", next: "dr_elphi_journal_network" },
                    { text: "Back to other clues.", next: "dr_elphi_clues_hub" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('elphi_journal_analysis')) {
                        this.questSystem.updateQuest('who_killed_bishop', 'Dr. Elphi interpreted the Bishop\'s journal entry as evidence she had been disconnected from the myceliar network — a devastating loss for an Obazoba cleric. She turned to dreams as her last resort.', 'elphi_journal');
                        this.addJournalEntry(
                            'elphi_journal_analysis',
                            'Dr. Elphi\'s Analysis: The Bishop\'s Journal',
                            'Dr. Elphi interpreted the Bishop\'s journal entry — "The city no longer hears me. Perhaps the dreams will." — as evidence of disconnection from the myceliar network. For a high-level Obazoba cleric, losing that connection would be catastrophic, leaving her isolated and desperate. The dreams became her last means of reaching out.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn' }
                        );
                    }
                }
            },

            dr_elphi_journal_network: {
                text: `Interference, damage, or deliberate severance. The myceliar network isn't just mystical — it has physical nodes throughout Upper Morkezela. If someone disrupted her personal node, she'd be cut off.\n\nThe Cathedral would know about network disruptions. And the Spore Council — they monitor the network's health. If her connection was deliberately severed, someone very powerful wanted her silenced.`,
                options: [
                    { text: "Back to other clues.", next: "dr_elphi_clues_hub" },
                ]
            },

            dr_elphi_clues_dissection: {
                text: `A fungal growth integrated with her nervous system? *She stops, staring.* That's not a natural infection. The Obazoba cultivate internal spore colonies — it's part of their theology — but what you're describing sounds like a symbiont.\n\nIf the Bishop had been carrying a symbiont, and if the recursive dream disrupted the symbiotic bond... the feedback wouldn't just have destroyed her mind. It would have destabilized the symbiont as well.\n\nThis changes things. The killer might not have targeted just the Bishop. They might have been trying to kill — or capture — whatever was living inside her.`,
                options: [
                    { text: "The symbiont called itself Neme of the Crownmire.", next: "dr_elphi_dissection_neme" },
                    { text: "Back to other clues.", next: "dr_elphi_clues_hub" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('elphi_dissection_analysis')) {
                        this.questSystem.updateQuest('who_killed_bishop', 'Dr. Elphi believes the fungal growth inside the Bishop was a symbiont. The killer may have been targeting the symbiont itself, not just the Bishop.', 'elphi_dissection');
                        this.addJournalEntry(
                            'elphi_dissection_analysis',
                            'Dr. Elphi\'s Analysis: The Fungal Growth',
                            'Dr. Elphi identified the fungal growth in the Bishop\'s body as a symbiont — more than a natural infection. If the recursive dream disrupted the symbiotic bond, the feedback would have destabilized both the Bishop and the symbiont. Elphi raised a disturbing possibility: the killer might not have been targeting the Bishop at all, but whatever was living inside her.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn' }
                        );
                    }
                }
            },

            dr_elphi_dissection_neme: {
                text: `Neme of the Crownmire. *She whispers the name like a prayer.* I've heard of it. Old stories from the Obazoba elders — a photosensitive symbiont that grants the ability to sense deception.\n\nIf someone knew the Bishop carried Neme... that symbiont is invaluable. Worth killing for, to certain factions.\n\nThe Spore Council would want it preserved. Others might want it destroyed — or weaponized.`,
                options: [
                    { text: "Back to other clues.", next: "dr_elphi_clues_hub" },
                ]
            },

            dr_elphi_clues_berries: {
                text: `Sulkberries? *She picks up the bag and examines them.* Spiced, too. These are fresh — whoever prepared them did it recently.\n\nSulkberries have a mild calming effect. People use them before dream sessions to lower neural resistance. Makes the immersion deeper. I sometimes recommend them to anxious first-timers.\n\nBut here's the thing — spiced Sulkberries like these aren't common. They're a Lumen Directorate specialty. The Directorate cultivates them and sells them through their own channels.`,
                options: [
                    { text: "The Lumen Directorate? Could they be connected to this?", next: "dr_elphi_berries_lumen" },
                    { text: "Back to other clues.", next: "dr_elphi_clues_hub" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('elphi_berries_analysis')) {
                        this.questSystem.updateQuest('who_killed_bishop', 'Dr. Elphi identified the Sulkberries as a spiced variety — a Lumen Directorate specialty. The Bishop was using them to deepen her dream immersion. The Directorate might know who she was buying from.', 'elphi_berries');
                        this.addJournalEntry(
                            'elphi_berries_analysis',
                            'Dr. Elphi\'s Analysis: Spiced Sulkberries',
                            'Dr. Elphi confirmed the Sulkberries found near the Bishop are a spiced variety used to deepen dream immersion by lowering neural resistance. These particular spiced Sulkberries are a Lumen Directorate specialty — they cultivate and sell them through their own channels. The Directorate might know who supplied the Bishop.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn' }
                        );
                    }
                }
            },

            dr_elphi_berries_lumen: {
                text: `Not necessarily connected to the murder. But the Lumen Directorate knows everything that happens in this city. They claim they won the Board Games War, they claim they saved everyone, and they act like Upper Morkezela is their personal project.\n\nIf the Bishop was buying spiced Sulkberries from them, they'd know. They keep records of everything — who buys what, who visits whom. It's all about "transparency," they say.\n\nMore importantly — the Directorate has interests in the Egg Cathedral. They've been watching it closely, waiting for the hatching. If the Bishop sealed the Cathedral, the Directorate would have noticed. And they would have opinions about it.\n\nSpeak to them. They might know more about the Bishop's last weeks than anyone. And if they don't — they'll know who does.`,
                options: [
                    { text: "Where can I find the Lumen Directorate?", next: "dr_elphi_lumen_where" },
                    { text: "Back to other clues.", next: "dr_elphi_clues_hub" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('elphi_lumen_lead')) {
                        this.questSystem.updateQuest('who_killed_bishop', 'Dr. Elphi suggested speaking with the Lumen Directorate. They sell the spiced Sulkberries the Bishop was using, they keep detailed records of transactions, and they have a strong interest in the Egg Cathedral. They might know more about the Bishop\'s final weeks.', 'elphi_lumen_lead');
                        this.addJournalEntry(
                            'elphi_lumen_lead',
                            'Investigation Lead: The Lumen Directorate',
                            'Dr. Elphi pointed me toward the Lumen Directorate. They cultivate and sell the spiced Sulkberries found near the Bishop — they would have records of who bought them. More importantly, the Directorate has been closely monitoring the Egg Cathedral and would have noticed the Bishop\'s emergency closure. As the unofficial rulers of Upper Morkezela, they may know more about the Bishop\'s activities than anyone else.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn' }
                        );
                    }
                }
            },

            dr_elphi_lumen_where: {
                text: `Their headquarters is near the main square — quite a building, you can't miss it. They like making an impression.\n\nAsk for whoever handles "cultivation oversight" or "Cathedral liaison." That's who would know about the Sulkberries and the Bishop's dealings with them.\n\nBut be careful how you approach them. The Directorate doesn't like surprises. And they definitely don't like being accused of anything. Go in with questions, not accusations.`,
                options: [
                    { text: "Back to other clues.", next: "dr_elphi_clues_hub" },
                ]
            },

            dr_elphi_clues_done: {
                text: allCluesDiscussed
                    ? `I think we've covered everything you found. This was no accident. Someone with knowledge of dream technology did this.\n\nTwo leads stand out. The Townhall — the Bishop formally reported that doppelgänger. Someone processed that report and someone might have followed up. And the Lumen Directorate — they supplied the Sulkberries, they monitor the Cathedral, and they know everything that moves in this city.\n\nAnd I'll work on the cartridge tonight. If you come back tomorrow, I should have the Bishop's last dream scene reconstructed. We'll see exactly what she saw before she died.`
                    : `Bring me more when you find it. The Bishop didn't deserve whatever happened to her.\n\nI'll be here. Working. Trying not to think about the fact that she died using my technology.`,
                options: [
                    ...(!allCluesDiscussed ? [
                        { text: "I'll keep investigating.", next: "closeDialog" },
                    ] : []),
                    ...(allCluesDiscussed && !readyForDay2 ? [
                        { text: "I'll investigate the Townhall and come back tomorrow.", next: "dr_elphi_end_day1" },
                    ] : []),
                    ...(readyForDay2 ? [
                        { text: "I'll be back.", next: "closeDialog" },
                    ] : []),
                ]
            },

            dr_elphi_end_day1: {
                text: `Good. Two things to follow up on.\n\nFirst — the Townhall. The Bishop's doppelgänger report was officially stamped. Find out who processed it, who read it, and whether anyone followed up. Or buried it.\n\nSecond — the Lumen Directorate. They supplied the Sulkberries and they've been watching the Cathedral like hawks. If the Bishop was doing anything unusual, they'd know.\n\nI'll have the cartridge ready by tomorrow. Come find me when you're ready to see what the Bishop saw.\n\nBe careful out there. Whoever did this is still in this city.`,
                options: [
                    { text: "Until tomorrow, Dr. Elphi.", next: "closeDialog" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('elphi_ready_for_day2')) {
                        this.questSystem.updateQuest('who_killed_bishop', 'I\'ve discussed all the clues with Dr. Elphi. She\'s working on fixing The Cardinal Feast cartridge to replay the Bishop\'s last dream scene — should be ready by tomorrow. Meanwhile, I should investigate two leads: the Townhall (doppelgänger report) and the Lumen Directorate (Sulkberries and Cathedral intel).', 'elphi_day1_complete');
                        this.addJournalEntry(
                            'elphi_ready_for_day2',
                            'Day 1 Complete: The Investigation Begins',
                            'I\'ve shared all my findings with Dr. Elphi Quarn. She confirmed the Bishop\'s death is connected to dream technology, but the doppelgänger remains unexplained — it\'s not any known side effect. Two leads to follow: 1) The Townhall, where the Bishop formally reported the doppelgänger encounter. 2) The Lumen Directorate, who supplied the Bishop\'s spiced Sulkberries and have been closely monitoring the Egg Cathedral. Elphi is working overnight to fix the corrupted Cardinal Feast cartridge. I should return to her tomorrow.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn' }
                        );
                    }
                }
            }
        };
    }
    
    /**
     * Creates the Dr. Elphi Quarn NPC with animations and interactions
     */
    createDrElphi() {
        // Create Dr. Elphi sprite at a more visible position
        this.drElphi = this.add.sprite(600, 350, 'drElphi');
        
        // Set scale to match the priest character (priest is at scale 2.0)
        this.drElphi.setScale(0.1); // Reduced scale to match priest proportions
        this.drElphi.setDepth(5);
        
        // Log to console for debugging
        console.log('Creating Dr. Elphi at position:', this.drElphi.x, this.drElphi.y);
        
        // Add name tag
        const nameTag = this.add.text(this.drElphi.x, this.drElphi.y + 30, 'Dr. Elphi Quarn', {
            fontSize: '14px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 5, y: 2 }
        });
        nameTag.setOrigin(0.5);
        nameTag.setDepth(5);
        
        // Add a subtle glow effect
        const glow = this.add.graphics();
        glow.fillStyle(0x7fff8e, 0.15);
        glow.fillCircle(this.drElphi.x, this.drElphi.y, 40);
        glow.setDepth(4);
        
        // Add pulsating effect to the glow
        this.tweens.add({
            targets: glow,
            alpha: { from: 0.15, to: 0.25 },
            duration: 2000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Add subtle movement animations
        this.tweens.add({
            targets: this.drElphi,
            y: this.drElphi.y - 5,
            duration: 2500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Random head movements
        this.time.addEvent({
            delay: 3000,
            callback: () => {
                // Random slight rotation
                const randomAngle = (Math.random() * 6) - 3;
                this.tweens.add({
                    targets: this.drElphi,
                    angle: randomAngle,
                    duration: 1000,
                    ease: 'Sine.easeInOut',
                    yoyo: true
                });
            },
            callbackScope: this,
            loop: true
        });
        
        // Create a much larger hit area for better clickability
        // Using a container to expand the interactive area
        const drElphiContainer = this.add.container(this.drElphi.x, this.drElphi.y);
        
        // Create a transparent rectangle for the hit area
        const hitAreaGraphic = this.add.graphics();
        hitAreaGraphic.fillStyle(0xffffff, 0.0); // Completely transparent
        hitAreaGraphic.fillRect(-60, -80, 120, 160); // Much larger hit area
        
        // Add the hit area to the container
        drElphiContainer.add(hitAreaGraphic);
        
        // Make the container interactive
        drElphiContainer.setSize(120, 160);
        drElphiContainer.setInteractive();
        
        // Hover effect
        drElphiContainer.on('pointerover', () => {
            this.drElphi.setScale(0.11); // Slightly larger on hover
            nameTag.setFontSize('16px');
            document.body.style.cursor = 'pointer';
        });
        
        drElphiContainer.on('pointerout', () => {
            this.drElphi.setScale(0.1); // Back to normal size
            nameTag.setFontSize('14px');
            document.body.style.cursor = 'default';
        });
        
        // Click to start dialog
        drElphiContainer.on('pointerdown', () => {
            console.log('Dr. Elphi clicked!'); // Debug log
            
            // Play a sound effect if available
            if (this.sound.get('click')) {
                this.sound.play('click', { volume: 0.5 });
            }
            
            // Show dialog
            this.showDialog('dr_elphi_start');
        });
        
        // Add a notification to indicate Dr. Elphi is present
        this.time.delayedCall(1500, () => {
            this.showNotification('Dr. Elphi is working at her console');
        });
    }
    
    shutdown() {
        // Clean up resources
        this.restoreBackgroundMusic();
        this.sceneMusic = null;
        super.shutdown();
    }
    
    update() {
        // Call parent update for all standard mechanics
        super.update();
    }
}
