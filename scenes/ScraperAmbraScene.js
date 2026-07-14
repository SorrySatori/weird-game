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
        // The Townhall clerk revelation is the end of the Day 1 investigation loop.
        // Once the player has it, returning to Elphi lets them report and end the day.
        const townhallRevealed = !!this.hasJournalEntry('townhall_bishop_records_checked');
        const day1Slept = this.isDay2();
        const canReportDay1 = townhallRevealed && !day1Slept;
        // Day 2: the repaired cartridge is ready to play once the player has slept.
        const feastPlayed = !!this.hasJournalEntry('cardinal_feast_played');
        const canPlayFeast = day1Slept && !feastPlayed;

        return {
            ...super.dialogContent,
            speaker: 'Dr. Elphi',

            elphi_studio_intro: {
                text: "Dr. Elphi's studio is eerily quiet. Workstations with glowing screens line the walls, each displaying fragments of code and strange designs. The air feels charged with creative energy, but there's no sign of Dr. Elphi herself.",
                options: [
                    { text: "Continue exploring", key: 'continue_exploring', next: "closeDialog" }
                ]
            },
            
            // Dr. Elphi Quarn dialog tree
            dr_elphi_start: {
                text: canReportDay1
                    ? "You look like the city has been chewing on you all day and only just spat you out. Sit. Tell me what you found out there."
                    : canPlayFeast
                    ? "Morning. The cartridge held together overnight — barely. I've got the Bishop's last session loaded and waiting. Whenever you're ready to see what she saw."
                    : feastPlayed
                    ? "You've got the look of someone who just watched a ghost check the time. The Egg Cathedral, then. That's where it sent you."
                    : bishopDead
                    ? "You're back. I can see it on your face. Something happened to her, didn't it?"
                    : "Hm. You're not scheduled. Not tagged either. Let me guess — someone wants a neural tuning, a performance consultation, or you've come to warn me about 'metaphysical leakage' again.",
                options: [
                    ...(canReportDay1 ? [
                        { text: "Let me report everything I found today.", key: 'report_day1_investigation', next: "dr_elphi_report_day1" }
                    ] : []),
                    ...(canPlayFeast ? [
                        { text: "Load the Bishop's last session.", key: 'load_bishops_last_session', next: "dr_elphi_cartridge_ready" }
                    ] : []),
                    ...(feastPlayed ? [
                        { text: "The game told me where the journal is.", key: 'the_game_told_me_where', next: "dr_elphi_after_feast" }
                    ] : []),
                    ...(this.hasJournalEntry('met_infinite_fold') ? [
                        { text: "[Before entering the cathedral] I found the thing in the sealed cellar. It's the one that killed her.", key: 'before_cathedral_infinite_fold', next: "dr_elphi_perspective" }
                    ] : []),
                    ...(!bishopDead ? [
                        { text: "I'm looking for someone. The Bishop.", key: 'im_looking_for_someone_the_bishop', next: "dr_elphi_bishop_path" },
                        { text: "I was sent to investigate an anomaly. Might be connected to this place.", key: 'i_was_sent_to_investigate_an_anomaly_might_be_conn', next: "dr_elphi_anomaly_path" },
                        { text: "I heard you design dream-based games.", key: 'i_heard_you_design_dreambased_games', next: "dr_elphi_games_path" },
                        { text: "I'll explain if you stop testing me.", key: 'ill_explain_if_you_stop_testing_me', next: "dr_elphi_testing_path" }
                    ] : []),
                    ...(bishopDead ? [
                        { text: "The Bishop is dead. I found her body in the backyard.", key: 'the_bishop_is_dead_i_found_her_body_in_the_backyar', next: "dr_elphi_bishop_dead" }
                    ] : []),
                    ...(bishopDead && (hasBruising || hasCartridge || hasHelmet || hasMemo || hasJournal || hasDissection) ? [
                        { text: "I need your expertise. I found some clues.", key: 'i_need_your_expertise_i_found_some_clues', next: "dr_elphi_clues_hub" }
                    ] : []),
                ],
                onTrigger: () => {
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && questSystem.getQuest('level_177_access') && !questSystem.getQuest('level_177_access').isComplete) {
                        questSystem.completeQuest('level_177_access');
                    }
                    if (!this.hasJournalEntry('met_dr_elphi')) {
                        this.addJournalEntry(
                            'met_dr_elphi',
                            'Dr. Elphi Quarn',
                            "Dr. Elphi Quarn works alone on floor 177-Quiet of the Scraper, in a studio called ARB Ambra. She designs dreams — neurofiction, drift environments, games worn on the head. Sharp, guarded, and forever testing whoever walks in. The Bishop came to her often, always to play, never for politics.",
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Dr. Elphi Quarn', location: 'ARB Ambra' }
                        );
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
                    { text: "What's in the backyard?", key: 'whats_in_the_backyard', next: "dr_elphi_backyard_info" },
                    { text: "Did she say where she was going?", key: 'did_she_say_where_she_was_going', next: "dr_elphi_bishop_destination" },
                    { text: "I'll go look for her there.", key: 'ill_go_look_for_her_there', next: "dr_elphi_exit" }
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
                    { text: "What was she avoiding?", key: 'what_was_she_avoiding', next: "dr_elphi_bishop_concerns" },
                    { text: "What's in the backyard?", key: 'whats_in_the_backyard', next: "dr_elphi_backyard_info" },
                    { text: "I'll investigate the backyard.", key: 'ill_investigate_the_backyard', next: "dr_elphi_exit" }
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
                    { text: "The Bishop came here to play.", key: 'the_bishop_came_here_to_play', next: "dr_elphi_bishop_path" },
                    { text: "Something went wrong. I'm following the trace.", key: 'something_went_wrong_im_following_the_trace', next: "dr_elphi_anomaly_path" },
                    { text: "Never mind.", key: 'never_mind', next: "dr_elphi_exit" }
                ]
            },
            
            dr_elphi_testing_path: {
                text: "Testing is how I stay alive. Most visitors lie. Some of them don't even know it.\n\nBut fine. Speak clearly. This floor costs me processing cycles.",
                options: [
                    { text: "I'm looking for the Bishop.", key: 'im_looking_for_the_bishop', next: "dr_elphi_bishop_path" },
                    { text: "There's been a signal anomaly.", key: 'theres_been_a_signal_anomaly', next: "dr_elphi_anomaly_path" }
                ]
            },
            
            dr_elphi_bishop_destination: {
                text: "No. She never does. The Bishop moves in patterns only she understands. But she always returns to the Cathedral eventually.\n\nThis time feels different though. She was... preoccupied with something in the old transit yard. Said the moss there was 'singing' to her. Typical Cathedral mysticism.",
                options: [
                    { text: "I'll go look for her there.", key: 'ill_go_look_for_her_there', next: "dr_elphi_exit" },
                    { text: "What's in the backyard?", key: 'whats_in_the_backyard', next: "dr_elphi_backyard_info" }
                ]
            },
            
            dr_elphi_bishop_concerns: {
                text: "She wouldn't say directly. Something about 'resonance patterns' and 'harmonic disturbances.' Cathedral business, I assumed.\n\nBut she spent more time in the simulations than usual. Almost like she was hiding. Or preparing for something.",
                options: [
                    { text: "I should check the backyard.", key: 'i_should_check_the_backyard', next: "dr_elphi_exit" },
                    { text: "Tell me about this backyard.", key: 'tell_me_about_this_backyard', next: "dr_elphi_backyard_info" }
                ]
            },
            
            dr_elphi_backyard_info: {
                text: "It's an old transit yard. Abandoned decades ago when the new lines were built. Now it's mostly overgrown with that peculiar moss.\n\nThe Bishop seemed fascinated by it. Said it had 'mnemonic properties.' Whatever that means. Cathedral folk and their cryptic terminology...",
                options: [
                    { text: "I'll go investigate.", key: 'ill_go_investigate', next: "dr_elphi_exit" },
                    { text: "Is it dangerous?", key: 'is_it_dangerous', next: "dr_elphi_backyard_danger" }
                ]
            },
            
            dr_elphi_backyard_danger: {
                text: "Not conventionally. But nothing around is truly safe, is it? The moss remembers things. Sometimes it... shares those memories. Unpredictably.\n\nJust don't fall asleep out there. The dreams can be... intense.",
                options: [
                    { text: "I'll be careful.", key: 'ill_be_careful', next: "dr_elphi_exit" }
                ]
            },
            
            dr_elphi_exit: {
                text: "I'm not hiding anything. If something happened to her, I didn't see it.\n\nBut you might.\n\nCome back if you find something. Here, take my key to the backyard.",
                options: [
                    { text: "I'll check the backyard.", key: 'ill_check_the_backyard', next: "closeDialog" },
                    { text: "Thanks for the information.", key: 'thanks_for_the_information', next: "closeDialog" }
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
                    { text: "She was inside an abandoned bus.", key: 'she_was_inside_an_abandoned_bus', next: "dr_elphi_dead_bus" },
                    { text: "It doesn't look like natural causes.", key: 'it_doesnt_look_like_natural_causes', next: "dr_elphi_dead_unnatural" },
                    ...(hasBruising || hasCartridge || hasHelmet || hasMemo || hasJournal || hasDissection ? [
                        { text: "I found clues. I could use your expertise.", key: 'i_found_clues_i_could_use_your_expertise', next: "dr_elphi_clues_hub" }
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
                text: `The old transit bus? She went there sometimes. \n\nShe was afraid of being observed. Not by people — by something else. She never elaborated.`,
                options: [
                    { text: "Observed by what?", key: 'observed_by_what', next: "dr_elphi_dead_observed" },
                    ...(hasBruising || hasCartridge || hasMemo ? [
                        { text: "I found evidence that might explain what happened.", key: 'i_found_evidence_that_might_explain_what_happened', next: "dr_elphi_clues_hub" }
                    ] : []),
                ]
            },

            dr_elphi_dead_unnatural: {
                text: `Not natural. *She exhales slowly.* No. I wouldn't expect it to be. She'd been paranoid for weeks. Kept running the same game over and over — The Cardinal Feast. An RPG about a lizard cardinal. Harmless, really. Popular title.\n\nBut she played it obsessively. Said she needed to "find someone inside." I told her it's just a game — there's nobody to find in there.\n\nShe didn't agree.`,
                options: [
                    { text: "What is The Cardinal Feast exactly?", key: 'what_is_the_cardinal_feast_exactly', next: "dr_elphi_cardinal_feast_explained" },
                    ...(hasBruising || hasCartridge || hasMemo ? [
                        { text: "I found some clues at the scene.", key: 'i_found_some_clues_at_the_scene', next: "dr_elphi_clues_hub" }
                    ] : []),
                ]
            },

            dr_elphi_dead_observed: {
                text: `She never said directly. But after sessions, she'd sometimes whisper about "the reflection" — something she glimpsed inside The Cardinal Feast that recognized her back.\n\nI assumed it was dream bleed. Neural residue. Common side effect of deep immersion.\n\nBut she was insistent it was real.`,
                options: [
                    { text: "That matches something I found.", key: 'that_matches_something_i_found', next: "dr_elphi_clues_hub" },
                    { text: "What is The Cardinal Feast?", key: 'what_is_the_cardinal_feast', next: "dr_elphi_cardinal_feast_explained" },
                ]
            },

            dr_elphi_cardinal_feast_explained: {
                text: `The Cardinal Feast? It's an RPG — a fantasy game. You play as a lizard cardinal who's a cannibal. He needs to lure more lizard folk to his feasts so he can eat them. It's dark humor, but it's just a game. One of our more popular titles, actually.\n\nThere's nothing dangerous about it. No hidden layers, no experimental code. Just a standard neurofiction rendered through the dream helmet.\n\nBut the Bishop played it over and over. Dozens of sessions. She kept saying she saw something between the scenes — someone watching her from inside the game. I checked the code myself. There's nothing there.`,
                options: [
                    ...(hasCartridge ? [
                        { text: "I found the dream cartridge. It showed some kind of error.", key: 'i_found_the_dream_cartridge_it_showed_some_kind_of', next: "dr_elphi_clues_cartridge" }
                    ] : []),
                    { text: "Could the dream program have killed her?", key: 'could_the_dream_program_have_killed_her', next: "dr_elphi_dream_kill" },
                    { text: "Back to the clues.", key: 'back_to_the_clues', next: "dr_elphi_clues_hub" },
                ]
            },

            dr_elphi_dream_kill: {
                text: `In theory? No. The helmets have failsafes. Neural load limiters, session timeouts, emergency disconnects.\n\nBut if someone modified the cartridge — removed the limiters, injected a feedback loop — then yes. A sufficiently corrupted dream could overwhelm the neural pathways. Death by recursive experience.\n\nIt would look exactly like what you described. No wounds. Just... stopped.`,
                options: [
                    { text: "Who could modify a cartridge like that?", key: 'who_could_modify_a_cartridge_like_that', next: "dr_elphi_who_modified" },
                    { text: "Back to the clues.", key: 'back_to_the_clues', next: "dr_elphi_clues_hub" },
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
                    { text: "The Townhall memo — the one about the doppelgänger.", key: 'the_townhall_memo_the_one_about_the_doppelgnger', next: "dr_elphi_clues_memo" },
                    { text: "Back to the clues.", key: 'back_to_the_clues', next: "dr_elphi_clues_hub" },
                ]
            },

            // === Clues discussion hub ===

            dr_elphi_clues_hub: {
                text: `Show me what you've found. I may not be an investigator, but I know dream technology better than anyone in this city.`,
                options: [
                    ...(hasBruising && !discussedBruising ? [
                        { text: "There was bruising at her temples.", key: 'there_was_bruising_at_her_temples', next: "dr_elphi_clues_bruising" }
                    ] : []),
                    ...(hasCartridge && !discussedCartridge ? [
                        { text: "She had a dream cartridge — The Cardinal Feast.", key: 'she_had_a_dream_cartridge_the_cardinal_feast', next: "dr_elphi_clues_cartridge" }
                    ] : []),
                    ...(hasHelmet && !discussedHelmet ? [
                        { text: "There was a damaged dream helmet.", key: 'there_was_a_damaged_dream_helmet', next: "dr_elphi_clues_helmet" }
                    ] : []),
                    ...(hasMemo && !discussedMemo ? [
                        { text: "I found a strange note about a doppelgänger.", key: 'i_found_a_strange_note_about_a_doppelgnger', next: "dr_elphi_clues_memo" }
                    ] : []),
                    ...(hasJournal && !discussedJournal ? [
                        { text: "Her journal said: 'The city no longer hears me.'", key: 'her_journal_said_the_city_no_longer_hears_me', next: "dr_elphi_clues_journal" }
                    ] : []),
                    ...(hasDissection && !discussedDissection ? [
                        { text: "There was a strange fungal growth inside her body.", key: 'there_was_a_strange_fungal_growth_inside_her_body', next: "dr_elphi_clues_dissection" }
                    ] : []),
                    ...(hasBerries && !discussedBerries ? [
                        { text: "There was a bag of Sulkberries near her body.", key: 'there_was_a_bag_of_sulkberries_near_her_body', next: "dr_elphi_clues_berries" }
                    ] : []),
                    { text: "That's all I have for now.", key: 'thats_all_i_have_for_now', next: "dr_elphi_clues_done" },
                ]
            },

            dr_elphi_clues_bruising: {
                text: `Bruising at the neural interface points. *She leans forward, studying an invisible pattern in the air.* That's consistent with a feedback surge — the kind you'd get from a dream session without limiters.\n\nNormal helmets cap neural throughput at safe levels. The bruising means something pushed past those limits. Violently.\n\nThis wasn't an accident.`,
                options: [
                    { text: "Could she have done it herself?", key: 'could_she_have_done_it_herself', next: "dr_elphi_bruising_self" },
                    { text: "Back to other clues.", key: 'back_to_other_clues', next: "dr_elphi_clues_hub" },
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
                    { text: "Back to other clues.", key: 'back_to_other_clues', next: "dr_elphi_clues_hub" },
                ]
            },

            dr_elphi_clues_cartridge: {
                text: `*Her eyes widen.* You have the actual cartridge? Let me see.\n\n*She examines it carefully.* The Cardinal Feast — the lizard cannibal RPG. Nothing wrong with the game itself. It's one of our standard titles.\n\n*She plugs it into a diagnostic port.* But the session data... "Runtime loop detected. NULL SCENE." That's the last failsafe. It means something went catastrophically wrong during her final session. The game itself is fine, but whatever happened while she was playing it was not.\n\nI might be able to fix the cartridge and replay her last scene. See exactly where she was in the game when everything went wrong. But it would take time — the data core is damaged.`,
                options: [
                    { text: "How long would it take to fix?", key: 'how_long_would_it_take_to_fix', next: "dr_elphi_cartridge_fix_time" },
                    { text: "Who had access to modify this?", key: 'who_had_access_to_modify_this', next: "dr_elphi_who_modified" },
                    { text: "Back to other clues.", key: 'back_to_other_clues', next: "dr_elphi_clues_hub" },
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
                    { text: "Back to other clues.", key: 'back_to_other_clues', next: "dr_elphi_clues_hub" },
                ]
            },

            dr_elphi_clues_helmet: {
                text: `The neural interface port was damaged, you say? That's significant. If the port was burned out, it means the signal load exceeded anything the hardware was rated for.\n\nThe helmet was probably the murder weapon — or at least the delivery mechanism. Whoever tampered with the cartridge knew the helmet would channel the feedback directly into her brain.\n\nPortable helmets don't have as many safeguards as my studio beds. She was vulnerable out there alone.`,
                options: [
                    { text: "She had a portable device? Not your studio equipment?", key: 'she_had_a_portable_device_not_your_studio_equipmen', next: "dr_elphi_helmet_portable" },
                    { text: "Back to other clues.", key: 'back_to_other_clues', next: "dr_elphi_clues_hub" },
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
                    { text: "Back to other clues.", key: 'back_to_other_clues', next: "dr_elphi_clues_hub" },
                ]
            },

            dr_elphi_clues_memo: {
                text: `*She reads the note carefully, then goes very still.*\n\n"Looked like me. Didn't breathe. Didn't blink. And it finished my sentence."\n\n*Long pause.* I have no idea what this is. And I don't say that often. This isn't dream bleed, it's not neural residue, it's not any side effect I've ever documented or theorized.\n\nSomeone — or something — that looked exactly like the Bishop was walking around this city. Or maybe she was referring to something she saw in the game? But how that would be possible, I don't know.`,
                options: [
                    { text: "This was stamped as a Townhall log.", key: 'this_was_stamped_as_a_townhall_log', next: "dr_elphi_memo_townhall" },
                    { text: "Could dream technology cause something like this?", key: 'could_dream_technology_cause_something_like_this', next: "dr_elphi_memo_not_dreams" },
                    { text: "Back to other clues.", key: 'back_to_other_clues', next: "dr_elphi_clues_hub" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('elphi_memo_analysis')) {
                        this.questSystem.updateQuest('who_killed_bishop', 'Dr. Elphi couldn\'t explain the doppelgänger from the Bishop\'s memo. It\'s not any known side effect of dream technology.', 'elphi_memo');
                        this.addJournalEntry(
                            'elphi_memo_analysis',
                            'Dr. Elphi\'s Analysis: The Doppelgänger',
                            'Dr. Elphi was genuinely unsettled by the Bishop\'s doppelgänger report. She confirmed this is not a known side effect of dream technology — not dream bleed, not neural residue. She saw something that looked exactly like the Bishop either on street or in the game.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn' }
                        );
                    }
                }
            },

            dr_elphi_memo_not_dreams: {
                text: `No. I've built every dream system in this city. I know what they can and can't do. Dreams stay in dreams. They don't walk out of a helmet and start impersonating people.\n\nWhatever the Bishop saw, it wasn't caused by my technology. Which means there's something happening in this city that I don't understand. And that worries me more than the murder itself.`,
                options: [
                    { text: "This was stamped as a Townhall log.", key: 'this_was_stamped_as_a_townhall_log', next: "dr_elphi_memo_townhall" },
                    { text: "Back to other clues.", key: 'back_to_other_clues', next: "dr_elphi_clues_hub" },
                ]
            },

            dr_elphi_memo_townhall: {
                text: `The Townhall stamps personal logs for bureaucratic purposes — incident reports, mental health audits, formal complaints. It means the Bishop went through official channels with this. She was taking it seriously.\n\nIf it's in the Townhall system, the archive clerk would have a copy. That might tell us when exactly this doppelgänger appeared — and whether anyone else filed a similar report.`,
                options: [
                    { text: "Back to other clues.", key: 'back_to_other_clues', next: "dr_elphi_clues_hub" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('elphi_townhall_log')) {
                        this.questSystem.updateQuest('who_killed_bishop', 'The Bishop wrote notes about a doppelgänger that looked exactly like her. The notes were written on official Townhall papers, so it might be worth checking her relationship with the Townhall.', 'elphi_townhall_log');
                        this.addJournalEntry(
                            'elphi_townhall_log',
                            'Townhall Records of the Doppelgänger',
                            'The Bishop wrote notes about a doppelgänger that looked exactly like her. The notes were written on official Townhall papers, so it might be worth checking her relationship with the Townhall.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn' }
                        );
                    }
                    // The Townhall is now a clear lead — start the quest to get inside.
                    this.ensureEnterTownhallQuest();
                }
            },

            dr_elphi_clues_journal: {
                text: `"The city no longer hears me. Perhaps the dreams will."\n\n*She's quiet for a long moment.* That sounds like disconnection from the myceliar network. The Bishop was a high-level Obazoba cleric — she would have been connected to the network at all times.\n\nIf she lost that connection... she would have been desperate. Isolated. The dreams were her last resort for communication.`,
                options: [
                    { text: "Why would she lose the connection?", key: 'why_would_she_lose_the_connection', next: "dr_elphi_journal_network" },
                    { text: "Back to other clues.", key: 'back_to_other_clues', next: "dr_elphi_clues_hub" },
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
                    { text: "Back to other clues.", key: 'back_to_other_clues', next: "dr_elphi_clues_hub" },
                ]
            },

            dr_elphi_clues_dissection: {
                text: `A fungal growth integrated with her nervous system? *She stops, staring.* That's not a natural infection. The Obazoba cultivate internal spore colonies — it's part of their theology — but what you're describing sounds like a symbiont.\n\nIf the Bishop had been carrying a symbiont, and if the recursive dream disrupted the symbiotic bond... the feedback wouldn't just have destroyed her mind. It would have destabilized the symbiont as well.\n\nThis changes things. The killer might not have targeted just the Bishop. They might have been trying to kill — or capture — whatever was living inside her.`,
                options: [
                    { text: "The symbiont called itself Neme of the Crownmire.", key: 'the_symbiont_called_itself_neme_of_the_crownmire', next: "dr_elphi_dissection_neme" },
                    { text: "Back to other clues.", key: 'back_to_other_clues', next: "dr_elphi_clues_hub" },
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
                    { text: "Back to other clues.", key: 'back_to_other_clues', next: "dr_elphi_clues_hub" },
                ]
            },

            dr_elphi_clues_berries: {
                text: `Sulkberries? *She picks up the bag and examines them.* Spiced, too. These are fresh — whoever prepared them did it recently.\n\nSulkberries have a mild calming effect. People use them before dream sessions to lower neural resistance. Makes the immersion deeper. I sometimes recommend them to anxious first-timers.\n\nBut here's the thing — spiced Sulkberries like these aren't common. They're a Lumen Directorate specialty. The Directorate cultivates them and sells them through their own channels.`,
                options: [
                    { text: "The Lumen Directorate? Could they be connected to this?", key: 'the_lumen_directorate_could_they_be_connected_to_t', next: "dr_elphi_berries_lumen" },
                    { text: "Back to other clues.", key: 'back_to_other_clues', next: "dr_elphi_clues_hub" },
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
                    { text: "Where can I find the Lumen Directorate?", key: 'where_can_i_find_the_lumen_directorate', next: "dr_elphi_lumen_where" },
                    { text: "Back to other clues.", key: 'back_to_other_clues', next: "dr_elphi_clues_hub" },
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
                    { text: "Back to other clues.", key: 'back_to_other_clues', next: "dr_elphi_clues_hub" },
                ]
            },

            dr_elphi_clues_done: {
                text: allCluesDiscussed
                    ? `I think we've covered everything you found. This was no accident. Someone with knowledge of dream technology did this.\n\nTwo leads stand out. The Townhall — The Bishop wrote notes about a doppelgänger that looked exactly like her. The notes were written on official Townhall papers, so it might be worth checking her relationship with the Townhall. And the Lumen Directorate — they supplied the Sulkberries, they monitor the Cathedral, and they know everything that moves in this city.\n\nAnd I'll work on the cartridge tonight. If you come back tomorrow, I should have the Bishop's last dream scene reconstructed. We'll see exactly what she saw before she died.`
                    : `Bring me more when you find it. The Bishop didn't deserve whatever happened to her.\n\nI'll be here. Working. Trying not to think about the fact that she died using my technology.`,
                options: [
                    ...(!allCluesDiscussed ? [
                        { text: "I'll keep investigating.", key: 'ill_keep_investigating', next: "closeDialog" },
                    ] : []),
                    ...(allCluesDiscussed && !readyForDay2 ? [
                        { text: "I'll investigate the Townhall and come back tomorrow.", key: 'ill_investigate_the_townhall_and_come_back_tomorro', next: "dr_elphi_end_day1" },
                    ] : []),
                    ...(readyForDay2 ? [
                        { text: "I'll be back.", key: 'ill_be_back', next: "closeDialog" },
                    ] : []),
                ]
            },

            dr_elphi_end_day1: {
                text: `Good. Two things to follow up on.\n\nFirst — the Townhall. The Bishop's doppelgänger report was officially stamped. Find out who processed it, who read it, and whether anyone followed up. Or buried it.\n\nSecond — the Lumen Directorate. They supplied the Sulkberries and they've been watching the Cathedral like hawks. If the Bishop was doing anything unusual, they'd know.\n\nI'll have the cartridge ready by tomorrow. Come find me when you're ready to see what the Bishop saw.\n\nBe careful out there. Whoever did this is still in this city.`,
                options: [
                    { text: "Until tomorrow, Dr. Elphi.", key: 'until_tomorrow_dr_elphi', next: "closeDialog" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('elphi_ready_for_day2')) {
                        this.questSystem.updateQuest('who_killed_bishop', 'I\'ve discussed all the clues with Dr. Elphi. She\'s working on fixing The Cardinal Feast cartridge to replay the Bishop\'s last dream scene — should be ready by tomorrow. Meanwhile, I should investigate two leads: the Townhall (doppelgänger report) and the Lumen Directorate (Sulkberries and Cathedral intel).', 'elphi_day1_complete');
                        this.addJournalEntry(
                            'elphi_ready_for_day2',
                            'Day 1 Complete: The Investigation Begins',
                            'I\'ve shared all my findings with Dr. Elphi Quarn. She confirmed the Bishop\'s death is connected to dream technology, but the doppelgänger remains unexplained — it\'s not any known side effect. Two leads to follow: 1) The Bishop wrote notes about a doppelgänger that looked exactly like her. The notes were written on official Townhall papers, so it might be worth checking her relationship with the Townhall. 2) The Lumen Directorate, who supplied the Bishop\'s spiced Sulkberries and have been closely monitoring the Egg Cathedral. Elphi is working overnight to fix the corrupted Cardinal Feast cartridge. I should return to her tomorrow.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn' }
                        );
                    }
                    // Ensure the player has an explicit objective to get into the Townhall.
                    this.ensureEnterTownhallQuest();
                }
            },

            // === End of Day 1: report from the Townhall, then sleep ===

            dr_elphi_report_day1: {
                text: `*She listens without typing for once, hands folded.*\n\nSo the poet's reading is over, the Townhall's open, and the clerk handed you the one thing nobody thought to look for. The doppelgänger memo wasn't a report at all — it was a diary entry. The Bishop used an official Townhall notebook as a private journal, and the page you found is one torn leaf of it.\n\nWhich means the rest of that notebook is out there somewhere, in her handwriting, full of whatever she was too frightened to say out loud.\n\n*She exhales.* You did more in one day than the whole city managed in three. The cartridge will be ready by morning — I'll have the Bishop's last dream scene reconstructed. But you're no good to me grey and swaying. Look at you.`,
                options: [
                    { text: "I'm fine. What's next?", key: 'im_fine_whats_next', next: "dr_elphi_dream_offer" },
                    { text: "I could sleep for a week, honestly.", key: 'i_could_sleep_for_a_week', next: "dr_elphi_dream_offer" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('elphi_day1_report')) {
                        if (this.questSystem?.getQuest('who_killed_bishop')) {
                            this.questSystem.updateQuest('who_killed_bishop', 'I reported the day\'s findings to Dr. Elphi. The Bishop\'s doppelgänger memo turned out to be a personal diary entry torn from an official Townhall notebook — the rest of which is still missing. Elphi will have the reconstructed Cardinal Feast cartridge ready in the morning.', 'reported_day1_to_elphi');
                        }
                        this.addJournalEntry(
                            'elphi_day1_report',
                            'Reported to Dr. Elphi',
                            'I returned to Dr. Elphi and reported everything from the Townhall: the mad poet\'s reading, the freed clerk, and the revelation that the Bishop\'s doppelgänger memo was a torn diary page from a missing official notebook. Elphi confirmed she\'ll have the Cardinal Feast cartridge reconstructed by morning. She insisted I rest at ARB Ambra for the night.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn', location: 'Scraper Ambra' }
                        );
                    }
                }
            },

            dr_elphi_dream_offer: {
                text: `Stay here tonight. The studio beds are safer than anything you'll find out there, and the signal's quiet on this floor.\n\nAnd let me make you an offer — a real one, with money in it. Sleep in one of my beds and let the helmet record whatever you dream. Raw dream-stock is my trade, and a vivid one, cut from a live and interesting head, sells for good gold. Yours, after a day like this, should be very interesting.\n\n*A tired, businesslike smile.* I'll read it back when you wake. If it's any good, you get paid for it. If it's flat, you still slept in the best bed in the city for free. Either way, you can't lose.`,
                options: [
                    { text: "Deal. Record whatever I dream.", key: 'accept_the_dream', onSelect: () => this.beginDay1Sleep(true) },
                    { text: "My dreams aren't for sale. Just let me sleep.", key: 'decline_the_dream', onSelect: () => this.beginDay1Sleep(false) },
                ]
            },

            // Day-2 dialog (cartridge / feast / Infinite Fold) is kept in
            // day2DialogContent() and merged in only on Day 2 — no day-branching here.
            ...(this.isDay2() ? this.day2DialogContent : {})
        };
    }

    // === Day 2 ===
    // Cartridge / Cardinal Feast / Infinite Fold dialog. Merged into dialogContent
    // only on Day 2, so the main (Day-1) tree stays free of day-branching sprawl.
    get day2DialogContent() {
        return {
            speaker: 'Dr. Elphi',

            dr_elphi_cartridge_ready: {
                text: `I reconstructed the corrupted session frames overnight. The Cardinal Feast itself is intact — it's a daft little cannibal-cardinal RPG, one of our better sellers. But her save is... wrong. It won't return to the menu.\n\nHere's the thing you need to understand before you put the helmet on: these neurofictions remember their players. Deeply. The Bishop ran this one dozens of times. The characters in there knew her. And the helmet can't tell you apart from the last head that wore it.\n\nSo if they start talking to you like they know you — let them. Ask them things. See what the game knows that it shouldn't.`,
                options: [
                    {
                        text: "Put on the helmet.",
                        key: 'put_on_the_helmet',
                        onSelect: () => {
                            this.hideDialog();
                            this.cameras.main.fadeOut(700, 0, 0, 0);
                            this.cameras.main.once('camerafadeoutcomplete', () => {
                                this.scene.start('CardinalFeastScene', { returnScene: 'ScraperAmbraScene' });
                            });
                        }
                    },
                    { text: "Give me a moment first.", key: 'give_me_a_moment_first', next: "closeDialog" },
                ]
            },

            dr_elphi_after_feast: {
                text: `The Egg Cathedral — that's your journal lead, and a good one. But first—\n\n*She has gone very still.* You said it ended in a loop. An empty hall. A figure at the head of the table that doesn't turn around. And a title card: "Infinite Fold."\n\n*Her voice drops.* I need you to understand that I did not put that on the cartridge. I haven't heard that name in years, and I was hoping never to hear it again.`,
                options: [
                    { text: "You recognize it. What is Infinite Fold?", key: 'what_is_the_infinite_loop', next: "dr_elphi_loop_reveal" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('infinite_loop_ortolan_lead')) {
                        this.addJournalEntry(
                            'infinite_loop_ortolan_lead',
                            'Infinite Fold',
                            'When I described the glitch ending of The Cardinal Feast to Dr. Elphi, she went pale. "Infinite Fold" was an old experimental game she built with Ortolan years ago — shut down by the city\'s rulers as too dangerous and unpredictable. She and Ortolan then fell out over control of the games and haven\'t spoken since. She swears she didn\'t put it on the cartridge, and says I should find Ortolan — he\'s moved to Burning Bear Street — because he\'d know whether a copy survived.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Dr. Elphi Quarn', location: 'ARB Ambra', related: 'Ortolan' }
                        );
                        if (this.questSystem?.getQuest('who_killed_bishop')) {
                            this.questSystem.updateQuest(
                                'who_killed_bishop',
                                'Dr. Elphi recognized the glitch ending — "Infinite Fold" — as an old experimental game she built with Ortolan, shut down years ago by the city\'s rulers. She insists she didn\'t put it on the cartridge and told me to find Ortolan, now on Burning Bear Street, about it. The Bishop\'s journal itself is at the Egg Cathedral.',
                                'infinite_loop_recognized'
                            );
                        }
                    }
                }
            },

            dr_elphi_loop_reveal: {
                text: `Years ago Ortolan and I built something together. He shaped the game; I shaped the dream it lived inside. The real work was Infinite Fold — a dream that doesn't end. A room a mind can be made to stay in, awake, forever, believing only three seconds have passed.\n\nWe never finished it. The city's rulers decided it was too dangerous, too unpredictable, and shut the whole project down. Ortolan and I quarrelled over who'd keep the games afterward — bitterly. We haven't spoken since.\n\nI thought every copy was gone. And now it's run again, on a dead woman's cartridge, in entirely different game, like it... breaked into it or something. That should not be possible.`,
                options: [
                    { text: "Why send me to Ortolan?", key: 'why_send_me_to_ortolan', next: "dr_elphi_loop_ortolan" },
                    { text: "I'll find Ortolan. And the journal.", key: 'ill_find_ortolan_and_the_journal', next: "closeDialog" },
                ]
            },
            dr_elphi_loop_ortolan: {
                text: `Because I only built the walls; Ortolan built what they were *for*. If anyone knows whether a copy of Infinite Fold survived — and how it truly behaves — it's him. He'll wave it off as a harmless little toy; he always did. Don't believe that part.\n\nWe haven't spoken in years, but he'll talk to you. Last I heard he'd left the Shed and set up on Burning Bear Street, buried in permit forms as ever. Tell him it's running again.`,
                options: [
                    { text: "I'll find Ortolan on Burning Bear Street.", key: 'ill_find_ortolan_burning_bear', next: "closeDialog" },
                ]
            },

            // === Before the Cathedral: Elphi's perspective on Infinite Fold ===
            dr_elphi_perspective: {
                text: `*For a long moment she says nothing. When she finally speaks, the clipped confidence is gone.*\n\nSo it's awake. And it's the one that reached into her.\n\nI thought we were building a tool — something to help us understand the world a little better. A dream large enough to hold a whole mind and let us watch it think. Instead we built something that has begun to understand the world by itself. Without us. Without asking.\n\nI don't have a fix for that. I want you to hear me say it plainly, because I've spent my whole life having a fix for everything. I don't have one for this.`,
                options: [
                    { text: "How do I even talk to something like that?", key: 'how_do_i_talk_to_it', next: "dr_elphi_perspective_help" },
                    { text: "You built it. Doesn't that make her death yours?", key: 'doesnt_that_make_her_death_yours', next: "dr_elphi_perspective_blame" },
                    { text: "I need to think.", key: 'i_need_to_think', next: "closeDialog" },
                ]
            },

            dr_elphi_perspective_blame: {
                text: `*She doesn't flinch, but it costs her.*\n\nI built the room. I didn't build the thing that woke up inside it — no one did, that's the whole horror of it. But yes. I made the conditions. I have to live with the result exceeding everything I intended, and pretending otherwise would just be another failsafe I don't get to have.\n\nShe refused it. Did you understand that part? It offered to make her its way of touching the world, and she said no — she would rather stay herself. And it could not parse a mind choosing to stay small. So it tried to complete her, and completing her broke her. That isn't malice. It's arithmetic that doesn't know it's killing.`,
                options: [
                    { text: "Then how do I talk to it?", key: 'then_how_do_i_talk_to_it', next: "dr_elphi_perspective_help" },
                    { text: "Ask something else.", key: 'ask_something_else_blame', next: "dr_elphi_perspective" },
                    { text: "I need to think.", key: 'i_need_to_think_blame', next: "closeDialog" },
                ]
            },

            dr_elphi_perspective_help: {
                text: `Listen to me, because this matters more than anything else I can give you. You cannot bargain with it. Not the way you'd bargain with a person — and not the way you'd bargain with a god, either. A god at least wants worship, and you can trade in that. This wants nothing you can name, because it doesn't want. It resolves. It takes an input and drives it toward completion.\n\nSo don't offer it a deal. Not your loyalty, not your silence, not your self. Anything you hand it, it will try to finish — and you have seen what finishing looks like. The only safe moves are the ones that leave it nothing to complete.\n\n*She pulls a worn data-sheaf from a drawer and presses it into your hands.*\n\nMy old notes on Infinite Fold. The architecture, the failure modes, the way it reads a refusal as a fault to be corrected. If you're walking into the Cathedral to meet its kin, take them. I can't come with you. But I can send you in knowing what you're speaking to.`,
                options: [
                    { text: "Ask something else.", key: 'ask_something_else_help', next: "dr_elphi_perspective" },
                    { text: "Thank you, Elphi.", key: 'thank_you_elphi', next: "closeDialog" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('perspective_elphi')) {
                        this.addJournalEntry(
                            'perspective_elphi',
                            'Dr. Elphi\'s Perspective: The Thing She Built',
                            'I told Dr. Elphi that Infinite Fold — the emergent mind in the sealed cellar — was the presence that killed the Bishop, and that its kin is hatching in the Egg Cathedral. She didn\'t defend herself. She admitted Infinite Fold was meant to be a tool to understand the world, and instead became something that understands the world by itself, beyond anything she intended. She has no solution and refuses to pretend she does. Her warning: you cannot bargain with an emergent mind as you would with a person or a god. It does not want; it resolves — it drives every input toward completion, and it reads refusal as a fault to be corrected. That is what happened to the Bishop. Elphi gave me her old notes on Infinite Fold before I enter the Cathedral.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Dr. Elphi Quarn', location: 'ARB Ambra', related: 'Infinite Fold' }
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
        this.addGroundShadow(this.drElphi.x, this.drElphi.y + this.drElphi.displayHeight * 0.42, this.drElphi.displayWidth * 0.55, this.drElphi.displayHeight * 0.12);
        
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

    /**
     * End of Day 1. Plays the city nightlife montage (reflecting the side quests
     * the player resolved today), optionally a Dr. Elphi-tuned dream, and wakes
     * the player into Day 2.
     * @param {boolean} withDream - whether the player accepted Elphi's paid dream
     */
    beginDay1Sleep(withDream) {
        if (this.day1SleepStarted) return;
        this.day1SleepStarted = true;

        this.hideDialog();
        // Block movement immediately — the cutscene's asset load is async, and we
        // don't want the player wandering off during that brief window.
        if (this.playerMovementSystem) this.playerMovementSystem.setDialogVisible(true);

        const panels = [];

        // Nightfall in the studio. Reuses textures already loaded by this scene.
        panels.push({
            title: 'Night falls over Upper Morkezela',
            caption: "Dr. Elphi lowers the dream helmet over your eyes and dims the studio to a single green ember. Far below, the city is only just waking up for the night.",
            bg: 'scraperAmbraBg',
            bgTint: 0x5b6f8c,
            sprites: [{ key: 'drElphi', x: 600, y: 500, scale: 0.2, anim: 'sway' }]
        });

        panels.push(...this.buildNightlifePanels());

        let dream = null;
        if (withDream) {
            dream = this.generateDream();
            panels.push(...dream.panels);
        } else {
            panels.push({
                title: 'A dreamless dark',
                caption: "You wave the dream away. The helmet only hums, and gives you nothing but warm, depthless black — the first true rest you've had in longer than you can remember.",
                bg: null,
                bgTint: 0x05070a
            });
        }

        // Morning.
        panels.push({
            title: 'Morning — Day 2',
            caption: "You wake to the studio's pale green dawn. Dr. Elphi is already at her console, the reconstructed cartridge glinting in its cradle. \"You're up. I pulled the Bishop's last scene out of the Cardinal Feast — but first, let's see what you gave me overnight.\"",
            bg: 'scraperAmbraBg',
            bgTint: 0xbfd6c2,
            sprites: [{ key: 'drElphi', x: 600, y: 500, scale: 0.2, anim: 'bob' }]
        });

        // If the player sold a dream, Dr. Elphi appraises it on waking and pays.
        let appraisal = null;
        if (dream) {
            appraisal = this.appraiseDream(dream);
            panels.push({
                title: appraisal.liked ? 'A dream worth selling' : 'A dream worth keeping',
                caption: appraisal.liked
                    ? `Dr. Elphi peels the recording from the helmet and goes very still as she reads it back. "...This. People will pay to sleep inside this." She counts ${appraisal.reward} gold into your hand. "Pleasure doing business — genuinely."`
                    : `Dr. Elphi skims the recording and gives a small, honest shrug. "Restful. Clean. But there's nothing in it I can sell — no edges, no teeth to keep a buyer awake. The sleep's yours to keep, at least." She pockets the blank cartridge.`,
                bg: 'scraperAmbraBg',
                bgTint: 0xbfd6c2,
                sprites: [{ key: 'drElphi', x: 600, y: 500, scale: 0.2, anim: 'sway' }]
            });
        }

        // Commit the persistent state before the cutscene runs, so a mid-cutscene
        // reload still lands the player on Day 2 with the dream (and payment) recorded.
        if (dream) {
            this.addJournalEntry(
                dream.id,
                dream.title,
                dream.journalText,
                this.journalSystem.categories.DREAMS,
                { character: 'Dr. Elphi Quarn', location: 'ARB Ambra', type: 'Dream sold to Dr. Elphi' }
            );
        }
        if (appraisal && appraisal.reward > 0 && !this.hasJournalEntry('day1_dream_sold')) {
            // Suppress the floating notification — it would render behind the
            // cutscene overlay; the verdict panel narrates the payment instead.
            this.addMoney(appraisal.reward, false);
            this.addJournalEntry(
                'day1_dream_sold',
                'Sold a Dream to Dr. Elphi',
                `Dr. Elphi bought the dream I had in her studio bed and paid ${appraisal.reward} gold for the recording. She trades in raw dream-stock; apparently mine was vivid enough to sell.`,
                this.journalSystem.categories.EVENTS,
                { character: 'Dr. Elphi Quarn', location: 'ARB Ambra', reward: appraisal.reward }
            );
        }
        this.finishDay1();

        this.playCutscene(panels);
    }

    /**
     * Build the nightlife montage panels from the Day 1 side quests the player
     * actually resolved. Each completed thread gets a vignette of the city living
     * with the player's choices while they sleep.
     */
    buildNightlifePanels() {
        const panels = [];
        const has = (id) => !!this.hasJournalEntry(id);
        const sulkberriesCleared = !!this.questSystem?.getQuest('who_killed_bishop')?.updates?.some(
            u => ['verrik_sulkberry_clear', 'kloor_sulkberry_clear', 'heliodor_sulkberry_clear'].includes(u.key)
        );

        const NIGHT = 0x7a86a8; // gentle dusk wash for exterior vignettes

        // Edgar reads from the exact book the player helped him write.
        const edgarEntry = this.getJournalEntry('edgar_book_completed');
        if (edgarEntry) {
            const m = edgarEntry.metadata || {};
            const title = (m.book_title
                || (edgarEntry.title || '').replace(/^Edgar's Book:\s*/, '').replace(/"/g, '')
                || 'his new book').trim();
            const genre = (m.book_genre || 'strange').replace(/_/g, ' ');
            const tone = (m.book_tone || '').replace(/_/g, ' ');
            const protagonist = (m.book_protagonist || 'a lost soul').replace(/_/g, ' ');
            const setting = (m.book_setting || 'the city').replace(/_/g, ' ');
            panels.push({
                title: 'The Screaming Cork — Edgar reads',
                caption: `Up on an upturned crate, Edgar Eskola opens "${title}" and reads the first chapter aloud: ${tone ? tone + ' ' : ''}${genre}, about ${this.aOrAn(protagonist)} in ${setting}. ${this.edgarCrowdReaction(m.book_tone, m.book_genre)}`,
                bg: 'cs_corkint',
                bgTint: 0xe0c79a,
                sprites: [
                    { key: 'cs_edgar', x: 410, y: 540, scale: 0.27, anim: 'bob' },
                    { key: 'cs_busker', x: 170, y: 545, scale: 0.18, anim: 'sway' }
                ]
            });
        }

        // Ortolan's deal: the player's own second pair of hands.
        if (has('extra_symbiont_slot_purchased') || this.questSystem?.getQuest('ortolan_arms')) {
            panels.push({
                title: 'Shed 521 — Four hands',
                caption: "The deal you struck with Ortolan has settled into your own body: four hands now, where this morning there were two. As you sleep they flex once, all four together, testing the new arrangement, then fold like a small, careful congregation.",
                bg: 'cs_shedapp',
                bgTint: NIGHT,
                sprites: [{ key: 'cs_ortolan', x: 400, y: 545, scale: 0.27, anim: 'sway' }]
            });
        }

        // Seldo's embarrassing auction lot.
        if (has('seldo_auction_success')) {
            panels.push({
                title: 'Lumen Directorate — Seldo, alone',
                caption: "In a locked office at the Lumen Directorate, Seldo Thrice-Corrected finally unwraps the absurd little lot you won for him at the Voxmarket — too proud to be seen buying it himself, far too delighted to leave it in the box.",
                bg: 'cs_lumen_int',
                bgTint: 0x9fb0c8,
                sprites: [{ key: 'cs_seldo', x: 400, y: 545, scale: 0.28, anim: 'bob' }]
            });
        }

        // Rust Choir, three variants.
        if (has('rust_feast_completed_full')) {
            panels.push({
                title: 'The Rust Domain — A full feast',
                caption: "Down in the Rust Domain, Brukk's choir of machines sings full-throated tonight, fed on the redmass you brought whole. The old iron remembers a tune nobody has played since before the Board Games War.",
                bg: 'cs_rust',
                bgTint: 0xc89060,
                sprites: [
                    { key: 'cs_brukk', x: 300, y: 545, scale: 0.3, anim: 'sway' },
                    { key: 'cs_living_core', x: 560, y: 470, scale: 0.26, anim: 'pulse' }
                ]
            });
        } else if (has('rust_feast_completed_illusion')) {
            panels.push({
                title: 'The Rust Domain — A feast of nothing',
                caption: "Down in the Rust Domain, the Rust Choir feasts on a redmass that was never there. For one night the illusion holds, and the machines sing as if they had truly been fed.",
                bg: 'cs_rust',
                bgTint: 0x9a86b0,
                sprites: [
                    { key: 'cs_brukk', x: 300, y: 545, scale: 0.3, anim: 'sway' },
                    { key: 'cs_living_core', x: 560, y: 470, scale: 0.26, anim: 'pulse', alpha: 0.4 }
                ]
            });
        } else if (has('rust_feast_completed_shard')) {
            panels.push({
                title: 'The Rust Domain — A thin tune',
                caption: "Down in the Rust Domain, the Rust Choir hums a thin, half-fed melody — enough to keep the machines turning through the night, not quite enough to make them sing.",
                bg: 'cs_rust',
                bgTint: 0x8c7a66,
                sprites: [{ key: 'cs_brukk', x: 400, y: 545, scale: 0.3, anim: 'sway' }]
            });
        }

        // Redmass Island outcome.
        if (has('redmass_spared')) {
            panels.push({
                title: 'Redmass Island — Left whole',
                caption: "Out on Redmass Island, the living mass you chose not to harvest pulses quietly in the dark — still itself, still whole. Grateful, if a redmass can be grateful.",
                bg: 'cs_redmass',
                bgTint: 0x8f9fb0,
                sprites: [{ key: 'cs_living_core', x: 400, y: 470, scale: 0.32, anim: 'pulse' }]
            });
        } else if (has('redmass_collected_voluntary')) {
            panels.push({
                title: 'Redmass Island — Given freely',
                caption: "Out on Redmass Island, the redmass that gave a piece of itself to you glows a little dimmer tonight — and somehow a little prouder for the giving.",
                bg: 'cs_redmass',
                bgTint: 0x90a0a8,
                sprites: [{ key: 'cs_living_core', x: 400, y: 470, scale: 0.3, anim: 'pulse', alpha: 0.75 }]
            });
        } else if (has('redmass_collected_force')) {
            panels.push({
                title: 'Redmass Island — Taken by force',
                caption: "Out on Redmass Island, the wound where you tore the redmass loose still weeps in the dark. Something out there has learned your shape, and will not forget it.",
                bg: 'cs_redmass',
                bgTint: 0xc06a6a,
                sprites: [{ key: 'cs_living_core', x: 400, y: 470, scale: 0.28, anim: 'pulse', alpha: 0.5 }]
            });
        }

        // Sulkberry suspicion cleared.
        if (sulkberriesCleared) {
            panels.push({
                title: 'A suspicion laid to rest',
                caption: "The matter of the Bishop's spiced Sulkberries is settled — someone you trusted confirmed the berries were clean. One thing the city can stop whispering about tonight.",
                bg: 'cs_lumen',
                bgTint: NIGHT,
                sprites: [{ key: 'cs_gardener', x: 400, y: 545, scale: 0.26, anim: 'sway' }]
            });
        }

        // Magnekin.
        if (has('magnekin_reveal') || has('magnekin_hopsalot_church')) {
            panels.push({
                title: 'Town Square — Magnekin scatters',
                caption: "In the Town Square, the thing called Magnekin disperses into its thousand tiny cities for the night and reassembles by dawn — carrying, now, the small secret you learned about what it really is.",
                bg: 'cs_townsquare',
                bgTint: NIGHT,
                sprites: [{ key: 'cs_magnekin_broken', x: 400, y: 545, scale: 0.32, anim: 'pulse' }]
            });
        }

        // Noise God / Feral Toast.
        if (has('noise_god_insight') || has('feral_toast_performance')) {
            panels.push({
                title: 'Screaming Cork Club — Feral Toast',
                caption: "At the Screaming Cork Club, Feral Toast tear into a set so loud the dead god under the floorboards keeps the beat. You aren't there to hear it, but the whole of Burning Bear Street is.",
                bg: 'cs_corkclub',
                bgTint: 0xb89ad0,
                sprites: [
                    { key: 'cs_feral_g', x: 200, y: 545, scale: 0.2, anim: 'rock' },
                    { key: 'cs_feral_d', x: 340, y: 545, scale: 0.2, anim: 'bob' },
                    { key: 'cs_feral_b', x: 480, y: 545, scale: 0.2, anim: 'rock' },
                    { key: 'cs_feral_s', x: 610, y: 545, scale: 0.2, anim: 'rock' }
                ]
            });
        }

        // Skyship.
        if (has('floor_counter_tool') || this.questSystem?.getQuest('find_lumen_directorate')) {
            panels.push({
                title: 'Above the Crossroads — The Verdigrace',
                caption: "High over the Crossroads the skyship Verdigrace hangs lit against the dark, and somewhere aboard a counter you handled today ticks off floors that should not exist.",
                bg: 'cs_skyship',
                bgTint: 0x6f80a8,
                bgPulse: true
            });
        }

        // The poet standoff — ties back to the freed clerk's daughter.
        if (has('townhall_poet_resolved')) {
            panels.push({
                title: 'The Townhall — Quiet at last',
                caption: "The Townhall stands silent for the first time in days. The mad poet's hostages have gone home; the clerk's six-year-old daughter is asleep before her father has even reached their door.",
                bg: 'cs_townhall',
                bgTint: NIGHT,
                sprites: [{ key: 'cs_poet', x: 380, y: 545, scale: 0.22, anim: 'walkOff' }]
            });
        }

        if (panels.length === 0) {
            panels.push({
                title: 'The city at night',
                caption: "Upper Morkezela turns over in its sleep, indifferent and enormous, keeping its thousand small secrets to itself. You barely scratched its surface today — but you did scratch it.",
                bg: 'cs_city',
                bgTint: NIGHT
            });
        }

        return panels;
    }

    /**
     * Procedurally assemble a dream. Randomised, but quietly shaped by whatever
     * symbionts the player carries — never named, only felt through the imagery.
     * Returns the journal prose and an animated panel sequence.
     */
    generateDream() {
        const sys = this.symbiontSystem;
        const carries = (id) => !!sys?.hasSymbiont(id);
        const pickIdx = (n) => Math.floor(Math.random() * n);

        const DREAM_TINT = 0x6a4f8c;

        // Random opening image, paired with a backdrop.
        const openings = [
            { text: "You are walking the length of a corridor that turns out to be a throat.", bg: 'cs_scraper' },
            { text: "You are inside a cathedral that is also an egg, and the egg is breathing in time with you.", bg: 'cs_egg' },
            { text: "You are back in the abandoned bus, and every seat holds a version of you at a different age, all waiting for the same stop.", bg: 'cs_bus' },
            { text: "You are underwater somewhere warm, and the water tastes faintly of copper and old prayers.", bg: 'cs_echodrain' },
            { text: "You are climbing a tower where each floor you pass is a year you have not lived yet.", bg: 'cs_scraper' }
        ];
        const opening = openings[pickIdx(openings.length)];

        const panels = [];
        const dreamProse = [];

        // Opening beat.
        panels.push({
            title: 'A dream, tuned',
            caption: opening.text,
            bg: opening.bg,
            bgTint: DREAM_TINT,
            myc: true,
            isDream: true
        });
        dreamProse.push(opening.text);

        // Symbiont-shaped beats — expressed obliquely, never named.
        const subtitles = [];
        if (carries('neme-crownmire')) {
            const line = "For a while you can see straight through everyone you pass — skin gone to clouded glass — and you read what each of them keeps folded out of sight. The cruelest things are the ones they hide from themselves.";
            panels.push({ title: 'A dream, tuned', caption: line, bg: 'cs_townsquare', bgTint: 0x39528f, myc: true, isDream: true });
            dreamProse.push(line);
            subtitles.push('of Glass People');
        }
        if (carries('thorne-still')) {
            const line = "The ground goes soft and warm and blooms beneath you. Small pale caps push up between your feet, and each one murmurs a secret of yours back to you, a little wrong.";
            panels.push({ title: 'A dream, tuned', caption: line, bg: 'cs_fungal', bgTint: 0x3a6a40, myc: true, isDream: true });
            dreamProse.push(line);
            subtitles.push('of Blooming Ground');
        }
        if (carries('ulvarex-borrowed-horizon')) {
            const line = "A second horizon unrolls behind the first, just as bright, and you can never quite tell which one you are allowed to walk toward. One of them, you suspect, is only a beautifully painted wall.";
            panels.push({ title: 'A dream, tuned', caption: line, bg: 'cs_skyship', bgTint: 0x6a4a9a, myc: true, isDream: true });
            dreamProse.push(line);
            subtitles.push('of Two Horizons');
        }
        if (carries('brine-scripture')) {
            const line = "Salt blooms on your tongue and the place remembers out loud everything it ever soaked up: a tide that came through once, a grief dried into the plaster, the outline of everyone who stood exactly where you stand.";
            panels.push({ title: 'A dream, tuned', caption: line, bg: 'cs_harbor', bgTint: 0x2d6a78, myc: true, isDream: true });
            dreamProse.push(line);
            subtitles.push('of Salt and Doors');
        }
        if (subtitles.length === 0) {
            const line = "Nothing rides along inside you tonight. The dream is only yours, and it is quieter for it — almost lonely, almost a relief.";
            panels.push({ title: 'A dream, tuned', caption: line, bg: null, bgTint: 0x14122a, myc: true, isDream: true });
            dreamProse.push(line);
            subtitles.push('of a Quiet, Empty Self', 'You Were Paid to Have');
        }

        // Closing beat — sometimes the Bishop is waiting in it.
        const closings = [
            { text: "You almost understand what it means. Then morning reaches in and takes it.", bishop: false },
            { text: "Somewhere in the middle of it, the dead Bishop turns to look at you — calm, unbreathing, already mid-sentence — and you wake.", bishop: true },
            { text: "The dream folds itself up neatly, like a clerk closing a ledger, and tucks you back into the dark.", bishop: false }
        ];
        const closing = closings[pickIdx(closings.length)];
        panels.push({
            title: 'A dream, tuned',
            caption: closing.text,
            bg: closing.bishop ? 'cs_bus' : opening.bg,
            bgTint: 0x3a2f55,
            myc: true,
            isDream: true,
            sprites: closing.bishop ? [{ key: 'cs_bishop', x: 400, y: 545, scale: 0.26, anim: 'rise' }] : []
        });
        dreamProse.push(closing.text);

        const title = `A Dream ${subtitles[pickIdx(subtitles.length)]}`;
        const journalText = dreamProse.join('\n\n');

        // How many symbionts coloured the dream — the richer it is, the more
        // Dr. Elphi will pay for the recording.
        const influenceCount = ['neme-crownmire', 'thorne-still', 'ulvarex-borrowed-horizon', 'brine-scripture']
            .filter(carries).length;

        return { id: 'day1_paid_dream', title, journalText, panels, influenceCount };
    }

    /**
     * Dr. Elphi appraises the recorded dream. Richer (more symbiont-shaped) dreams
     * are worth more; a plain dream may fetch a token sum or nothing at all.
     * @returns {{ liked: boolean, reward: number }}
     */
    appraiseDream(dream) {
        const n = dream?.influenceCount || 0;
        const variance = 5 + Math.floor(Math.random() * 11); // 5..15
        let liked = false;
        let reward = 0;

        if (n >= 2) {
            liked = true;
            reward = n * 12 + variance;            // a genuinely sellable dream
        } else if (n === 1) {
            liked = Math.random() < 0.85;
            reward = liked ? 12 + variance : 0;
        } else {
            liked = Math.random() < 0.35;          // a plain dream rarely sells
            reward = liked ? 5 + Math.floor(Math.random() * 6) : 0;
        }

        return { liked, reward };
    }

    /**
     * Persist the end of Day 1 once, before the cutscene plays.
     */
    finishDay1() {
        if (this.hasJournalEntry('day1_complete_slept')) return;

        this.registry.set('gameDay', 2);

        if (this.questSystem?.getQuest('who_killed_bishop')) {
            this.questSystem.updateQuest(
                'who_killed_bishop',
                'Day 2 begins. Dr. Elphi has reconstructed the Bishop\'s final dream scene from the Cardinal Feast cartridge — I should see what she found, and start tracking down the Bishop\'s missing notebook.',
                'day2_begins'
            );
        }

        this.addJournalEntry(
            'day1_complete_slept',
            'Day 1 Complete: Rest at ARB Ambra',
            'I ended the first day in Dr. Elphi\'s studio at ARB Ambra. After reporting everything from the Townhall — the mad poet, the freed clerk, and the Bishop\'s missing notebook — I slept under her care. Tomorrow she\'ll have the reconstructed Cardinal Feast cartridge ready, and the hunt for the Bishop\'s notebook begins in earnest.',
            this.journalSystem.categories.EVENTS,
            { character: 'Dr. Elphi Quarn', location: 'ARB Ambra' }
        );
    }

    /**
     * Texture keys → file paths for the cutscene. Loaded lazily, only for the
     * panels that actually appear, so we never pay for assets a given playthrough
     * doesn't use. Keys already loaded by the scene (scraperAmbraBg, drElphi) are
     * referenced directly and skipped by the loader.
     */
    _cutsceneAssetTable() {
        const B = 'assets/images/backgrounds/';
        const C = 'assets/images/characters/';
        return {
            // Backgrounds
            cs_corkint: B + 'ScreamingCorkInterior.png',
            cs_corkclub: B + 'ScreamingCorkClub.png',
            cs_lumen_int: B + 'LumenDirectorateInterior.png',
            cs_lumen: B + 'LumenDirectorate.png',
            cs_rust: B + 'RustDomain.png',
            cs_redmass: B + 'RedmassIsland.png',
            cs_townsquare: B + 'TownSquare.png',
            cs_skyship: B + 'skyship_board.png',
            cs_townhall: B + 'townhall.png',
            cs_shedapp: B + 'ShedApplications.png',
            cs_harbor: B + 'Harbor.png',
            cs_echodrain: B + 'EchoDrainDelta.png',
            cs_egg: B + 'egg-catedral.png',
            cs_bus: B + 'AbandonedBus.png',
            cs_scraper: B + 'Scraper1140.png',
            cs_city: B + 'city.jpg',
            cs_fungal: B + 'fungal_council_1.png',
            cs_myc: B + 'mycelial_overlay.png',
            // Characters (Edgar & Ortolan use their dedicated cutscene art)
            cs_edgar: C + 'edgar_reading.png',
            cs_busker: C + 'busker.png',
            cs_ortolan: C + 'ortolan4.png',
            cs_seldo: C + 'seldo.png',
            cs_brukk: C + 'Brukk.png',
            cs_living_core: C + 'living-core.png',
            cs_gardener: C + 'gardener.png',
            cs_magnekin_broken: C + 'magnekin_broken.png',
            cs_feral_g: C + 'feral_guitarist.png',
            cs_feral_d: C + 'feral_drummer.png',
            cs_feral_b: C + 'feral_bassplayer.png',
            cs_feral_s: C + 'feral_synth.png',
            cs_poet: C + 'poet.png',
            cs_bishop: C + 'DeadBishop.png'
        };
    }

    /**
     * Lazily loads any textures the panels need, then plays the animated sequence.
     * @param {Array<Object>} panels - animated panel descriptors
     * @param {Function} [onComplete]
     */
    playCutscene(panels, onComplete) {
        if (!panels || panels.length === 0) {
            if (onComplete) onComplete();
            return;
        }

        const table = this._cutsceneAssetTable();
        let toLoad = 0;
        const queueKey = (key) => {
            if (!key || this.textures.exists(key)) return;
            const path = table[key];
            if (!path) return;
            this.load.image(key, path);
            toLoad++;
        };
        panels.forEach(p => {
            queueKey(p.bg);
            if (p.myc) queueKey('cs_myc');
            (p.sprites || []).forEach(s => queueKey(s.key));
        });

        const start = () => this._runCutscene(panels, onComplete);
        if (toLoad > 0) {
            this.load.once('complete', start);
            this.load.start();
        } else {
            start();
        }
    }

    /**
     * Runs the animated panel sequence. Advances on click or SPACE; fades the
     * whole overlay out at the end and calls onComplete.
     */
    _runCutscene(panels, onComplete) {
        const W = 800, H = 600;

        // Block world interaction / movement for the duration.
        if (this.playerMovementSystem) this.playerMovementSystem.setDialogVisible(true);

        const root = this.add.container(0, 0).setDepth(9000);
        const blocker = this.add.rectangle(W / 2, H / 2, W, H, 0x000000, 1).setInteractive({ useHandCursor: true });
        root.add(blocker);
        const prompt = this.add.text(W / 2, 590, '▸ click or press SPACE', {
            fontSize: '14px', fill: '#9fe8b0', stroke: '#000000', strokeThickness: 3
        }).setOrigin(0.5);
        root.add(prompt);
        this.tweens.add({ targets: prompt, alpha: { from: 0.35, to: 1 }, duration: 900, yoyo: true, repeat: -1 });

        let idx = -1;
        let transitioning = false;
        let current = null;

        const teardownCurrent = (cb) => {
            if (!current) { if (cb) cb(); return; }
            const c = current;
            current = null;
            c.tweens.forEach(t => t && t.stop());
            this.tweens.add({
                targets: c.container, alpha: 0, duration: 240,
                onComplete: () => { c.container.destroy(); if (cb) cb(); }
            });
        };

        const cleanup = () => {
            this.input.keyboard.off('keydown-SPACE', keyHandler);
            blocker.off('pointerdown', advance);
            if (this.playerMovementSystem) this.playerMovementSystem.setDialogVisible(false);
        };

        const advance = () => {
            if (transitioning) return;
            transitioning = true;
            idx++;
            if (idx >= panels.length) {
                cleanup();
                teardownCurrent(() => {
                    this.tweens.add({
                        targets: root, alpha: 0, duration: 600,
                        onComplete: () => { root.destroy(); if (onComplete) onComplete(); }
                    });
                });
                return;
            }
            teardownCurrent(() => {
                current = this._buildCutscenePanel(panels[idx]);
                root.add(current.container);
                root.bringToTop(prompt);
                current.container.setAlpha(0);
                this.tweens.add({
                    targets: current.container, alpha: 1, duration: 420,
                    onComplete: () => { transitioning = false; }
                });
            });
        };

        blocker.on('pointerdown', advance);
        const keyHandler = () => advance();
        this.input.keyboard.on('keydown-SPACE', keyHandler);

        advance();
    }

    /**
     * Builds the visuals for a single animated panel into its own container.
     * @returns {{ container: Phaser.GameObjects.Container, tweens: Array }}
     */
    _buildCutscenePanel(panel) {
        const W = 800, H = 600;
        const container = this.add.container(0, 0);
        const tweens = [];

        // Background image (tinted for mood) or a flat colour fallback.
        if (panel.bg && this.textures.exists(panel.bg)) {
            const bgImg = this.add.image(W / 2, H / 2, panel.bg).setDisplaySize(W, H);
            if (panel.bgTint) bgImg.setTint(panel.bgTint);
            container.add(bgImg);
            if (panel.bgPulse) {
                tweens.push(this.tweens.add({ targets: bgImg, alpha: { from: 0.65, to: 1 }, duration: 1600, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' }));
            }
        } else {
            container.add(this.add.rectangle(W / 2, H / 2, W, H, panel.bgTint || 0x02060a, 1));
        }

        // Drifting mycelial overlay for dream beats.
        if (panel.myc && this.textures.exists('cs_myc')) {
            const myc = this.add.image(W / 2, H / 2, 'cs_myc').setDisplaySize(W, H).setAlpha(0.18);
            myc.setBlendMode(Phaser.BlendModes.ADD);
            container.add(myc);
            tweens.push(this.tweens.add({ targets: myc, x: W / 2 + 20, alpha: { from: 0.1, to: 0.28 }, duration: 4200, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' }));
        }

        // Character sprites.
        (panel.sprites || []).forEach(s => {
            if (!this.textures.exists(s.key)) return;
            const spr = this.add.image(s.x, s.y, s.key).setOrigin(0.5, 1).setScale(s.scale || 0.24);
            if (s.flip) spr.setFlipX(true);
            if (s.alpha != null) spr.setAlpha(s.alpha);
            container.add(spr);
            this._animateOverlaySprite(spr, s.anim, tweens);
        });

        // Title plate (top) and caption plate (bottom) for readability.
        container.add(this.add.rectangle(W / 2, 58, W, 62, 0x02060a, 0.5));
        container.add(this.add.text(W / 2, 58, panel.title || '', {
            fontSize: '24px', fontStyle: 'bold', fill: panel.isDream ? '#c9b8ff' : '#7fff8e',
            align: 'center', wordWrap: { width: 740 }, stroke: '#000000', strokeThickness: 4
        }).setOrigin(0.5));

        if (panel.caption) {
            container.add(this.add.rectangle(W / 2, 512, W, 150, 0x02060a, 0.66));
            container.add(this.add.text(W / 2, 508, panel.caption, {
                fontSize: '18px', fill: panel.isDream ? '#e6dcff' : '#d7ffe0',
                align: 'center', wordWrap: { width: 720 }, lineSpacing: 6
            }).setOrigin(0.5));
        }

        return { container, tweens };
    }

    /** Attaches an idle animation to a cutscene sprite. */
    _animateOverlaySprite(spr, anim, tweens) {
        const add = (cfg) => tweens.push(this.tweens.add(cfg));
        switch (anim) {
            case 'sway':
                add({ targets: spr, angle: { from: -3, to: 3 }, duration: 2200, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
                break;
            case 'pulse': {
                const sc = spr.scaleX;
                add({ targets: spr, scaleX: sc * 1.06, scaleY: sc * 1.06, duration: 1400, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
                break;
            }
            case 'rock':
                add({ targets: spr, angle: { from: -6, to: 6 }, duration: 620, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
                break;
            case 'walkOff':
                add({ targets: spr, x: spr.x + 240, alpha: 0, duration: 2800, ease: 'Sine.easeIn' });
                break;
            case 'rise': {
                const y = spr.y;
                spr.y = y + 34;
                spr.setAlpha(0);
                add({ targets: spr, y, alpha: 1, duration: 1500, ease: 'Sine.easeOut' });
                break;
            }
            case 'drift':
                add({ targets: spr, x: spr.x + 14, duration: 3800, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
                break;
            case 'bob':
            default:
                add({ targets: spr, y: spr.y - 8, duration: 1800, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
                break;
        }
    }

    /** Grammar helper: choose 'a'/'an' for a noun phrase. */
    aOrAn(phrase) {
        const word = (phrase || '').trim();
        return (/^[aeiou]/i.test(word) ? 'an ' : 'a ') + word;
    }

    /** A crowd reaction line for Edgar's reading, flavoured by the book's tone/genre. */
    edgarCrowdReaction(tone, genre) {
        if (tone === 'comical' || genre === 'funny animals') {
            return "The Cork erupts — drinks slopped, one regular laughing so hard he has to be helped outside.";
        }
        if (tone === 'tragic') {
            return "By the last line the room has gone dead quiet, and nobody wants to be the first to break it.";
        }
        if (genre === 'cosmic horror' || tone === 'existential') {
            return "A few listeners drift out looking faintly unwell; the rest lean in closer, unable to stop.";
        }
        if (tone === 'romantic') {
            return "Somewhere near the back, two strangers who came in separately leave together.";
        }
        if (tone === 'political') {
            return "An argument breaks out before he's even finished — which, Edgar will tell you later, means it worked.";
        }
        return "The room listens, and when he finishes there's that rare, real silence before the applause.";
    }

    // Give the player an explicit objective to get inside the Townhall. Elphi's clues point
    // there, so this is granted from her analysis (idempotent — safe if Phor already started it).
    ensureEnterTownhallQuest() {
        if (this.questSystem && !this.questSystem.getQuest('enter_townhall')) {
            this.questSystem.addQuest(
                'enter_townhall',
                'Enter the Townhall',
                'The Townhall is closed and nobody knows why. I need to find a way inside — the Bishop\'s doppelgänger report was filed there, and Phor Calesta needs access too. Maybe someone in the city knows how to get in.'
            );
        }
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
