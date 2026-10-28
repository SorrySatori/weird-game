import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import { preloadGDProps, applyGDBackground, placeGDProps } from '../utils/GDProps.js';
import JournalSystem from '../systems/JournalSystem.js';
import { GANG_QUEST_IDS, gangQuestStatus, recordSpyFragment } from '../utils/GangOfLamps.js';

export default class Shed521Scene extends GameScene {
    constructor() {
        super({ key: 'Shed521Scene' });
        this.isTransitioning = false;
        this.visitedDialogs = new Set();
        this._dialogTextCache = {}; // Cache for dynamic dialog text
        this.journalSystem = JournalSystem.getInstance();
    }

    get dialogContent() {
        // Get base content
        const inventory = this.registry.get('inventory');
        console.log('inventory', inventory);
        
        // Check if player made a promise to the clerk
        const quest = this.questSystem.getQuest('rust_reclamation');
        // Check if any update has the promise_made key
        const promiseMade = quest && quest.updates && quest.updates.some(update => update.key === 'promise_made');
        const hasLivingCore = !!inventory?.items?.some(item => item.id === 'living-core');
        const hasFindRustQuest = (this.questSystem && this.questSystem.getQuest('find_rust_choir') && !this.questSystem.getQuest('find_rust_choir').isComplete && !this.questSystem.getQuest('find_rust_choir').updates.some(update => update.key === 'talk_to_ravla'));
        // Gang of Lamps: Don's spy quest — buy a whisper out of Gnur.
        const canSpyGnur = gangQuestStatus(this, GANG_QUEST_IDS.don) === 'active' && !this.hasJournalEntry('gang_spy_gnur');
        // Ulvarex (Mirage Weave) can make Gnur see a Rust superior instead of a stranger — a
        // deception route that gets a deeper whisper for free, and sours the balance toward decay.
        const canSpyGnurUlvarex = canSpyGnur && !!this.symbiontSystem?.hasSymbiont('ulvarex-borrowed-horizon');

        const content = {
            ...super.dialogContent,
            speaker: 'Gnur',
            start: {
                moodNpc: 'gnur',
                textKey: 'default',
                text: "Another stray wanderin' down the veins of Shed 521...\nWhat're you lookin' for, outsider? Body upgrade? New lungs? Or just bad ideas?\nHe chuckles, voice crackling like a broken choir.\nSay your need. Maybe ol' Gnur's got a whisper to sell.",
                options: [
                    { text: "Who are you exactly?", key: 'who_are_you_exactly', next: "background" },
                    // Add the option to confront Gnur about lying if player made the promise
                    ...(promiseMade ? [{ text: "About that living core... you lied to me.", key: 'about_that_living_core_you_lied_to_me', next: "confront_about_lie" }] : []),
                    ...(hasFindRustQuest ? [{ text: "I'm looking for a way to reach the Rust Choir headquarters in the Scraper. Can you help me?", key: 'im_looking_for_the_way_how_to_reach_the_rust_choir', next: "rustDomain" }] : []),
                    ...(canSpyGnur ? [{ text: "You said you sell whispers. What's the Rust Choir not saying out loud?", key: 'gnur_spy_probe', next: "gnur_spy_secret" }] : []),
                    ...(canSpyGnurUlvarex ? [{ text: "[Ulvarex · Mirage Weave] (Let him see a Rust superior, and demand the whole truth.)", key: 'gnur_spy_ulvarex', next: "gnur_spy_ulvarex_read" }] : []),
                ],
                onTrigger: () => {
                    // Add journal entry about meeting Gnur
                    if (!this.hasJournalEntry('gnur_meeting')) {
                        this.addJournalEntry(
                            'gnur_meeting',
                            'Gnur',
                            'In the guts of Shed 521, I encountered Gnur, a figure whose voice crackles "like a broken choir." He seems to be a dealer in body modifications and other questionable services. There\'s something unsettling about him.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Gnur', faction: 'Rust Choir', location: 'Shed 521' }
                        );
                    }
                }
            },
            gnur_spy_ulvarex_read: {
                text: "Ulvarex pours light across your outline and *bends* it — and Gnur's forge-eyes go wide with recognition at a superior who was never there. \"Ah — didn't hear you come down, boss, forgive me—\" He stands straighter, eager to please the phantom. \"The mole? Yeah, yeah, still singing sweet. Their little archivist in the Lumen Directorate feeds Brukk which districts the pretty people are about to write off, so we know which machines'll be goin' cheap. And there's talk of a *second* pair of ears inside, higher up, but I ain't been told a name.\" He blinks as the mirage frays. \"...Wait. Who—\" Too late; you have it.",
                options: [
                    { text: "(Let the mirage dissolve.)", key: 'gnur_spy_ulvarex_close', next: "start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(0, 5);
                    this.notifyShift('lie_like_face', 'decay');
                    recordSpyFragment(this, 'gnur', "Rust Choir Secret: the Directorate Mole", "Wearing Ulvarex's mirage of a Rust superior, I made Gnur spill freely: the Choir has a mole inside the Lumen Directorate — an archivist tipping Brukk which districts the Directorate will write off, so the Choir claims the machines cheap. Gnur hinted at a *second*, higher-placed pair of hands inside too, though he had no name.");
                }
            },
            gnur_spy_secret: {
                text: "Gnur's crackle drops to a conspirator's murmur. \"A whisper, eh? For you, cheap — I'm feelin' generous.\" He leans close, oil-breath and static. \"The Choir's got someone *inside* the Lumen Directorate. One of their prim little archivists sings for us on the quiet — feeds Brukk which districts the Directorate's about to write off, so we know which machines'll be going cheap. The pretty people think they're pruning the city. They're just tellin' us where to dig.\" He straightens, grin crackling. \"That whisper's worth more'n you paid. Don't say Gnur never gave you nothin'.\"",
                options: [
                    { text: "Worth every bit. (Remember this.)", key: 'gnur_spy_secret_close', next: "start" }
                ],
                onTrigger: () => {
                    recordSpyFragment(this, 'gnur', "Rust Choir Secret: Gnur", "Gnur sold me a whisper: the Rust Choir has a mole inside the Lumen Directorate — an archivist who tips Brukk off about which districts the Directorate is about to write off, so the Choir knows which machines will soon be going cheap. The Directorate thinks it's pruning the city; it's really telling the Choir where to dig.");
                }
            },
            background: {
                text: "Used to keep the machines running in the old days. Now I'm with the Rust Choir. We sing to the machines to keep them awake... or lull them to make them sleep. Depends on the situation.",
                options: [
                    { text: "Tell me about the Rust Choir", key: 'tell_me_about_the_rust_choir', next: "rustChoir" },
                    { text: "Ask something else", key: 'back_to_other_topics', next: "start" }
                ],
                onTrigger: () => {
                    this.addJournalFact('gnur_meeting', 'rust_choir', "He used to keep the machines running in the old days; now he is with the Rust Choir. That suggests a deeper involvement with the city's hidden infrastructures and technologies than his shabby appearance would suggest.");
                    this.addJournalFact('rust_choir_faction', 'machines', "Gnur says they sing to the machines — to keep some awake and lull others to sleep, depending on the situation.");
                }
            },
            rustChoir: {
                text: "We celebrate entropy, collapse as transformation. After all, all things lead to chaos. We like to trade in secrets, especially old tech. If you are interested to know more, visit the old Scraper and talk to Brukk's people.",
                options: [
                    { text: "Who is Brukk?", key: 'who_is_brukk', next: "brukk" },
                    { text: "Ask something else", key: 'back_to_other_topics', next: "start" }
                ],
                onTrigger: () => {
                    this.addJournalFact('rust_choir_faction', 'entropy', "They celebrate entropy — collapse as transformation — and like to trade in secrets, above all old tech. Brukk's people can be found in the old Scraper.");
                }
            },
            brukk: {
                text: "Brukk is our leader... He is the keeper of the old tech, the one who can help you find what you're looking for. That's all I can tell you.",
                options: [
                    { text: "Ask something else", key: 'back_to_other_topics', next: "start" }
                ],
                onTrigger: () => {
                    this.addJournalFact('rust_choir_faction', 'brukk', "Their leader is Brukk, the keeper of the old tech.");
                }
            },
            bishop: {
                text: "Ahhh, the shrouded one... yeah, she came down here, glimmer-eyed and restless. Wanted a lens — an optic from the old dream rigs, pre-war make. Only the Choir still digs those up. But info ain't free, friend.",
                options: [
                    { text: "What do you want?", key: 'what_do_you_want', next: "rustReclamation" },
                    { text: "I can help you recover some old tech", key: 'i_can_help_you_recover_old_tech_carefully', next: "recoverTech" },
                    { text: 'Tell me what I want to know... or else.', key: 'tell_me_what_i_want_to_know_or_else', next: 'threat'},
                    { text: "Ask something else", key: 'back_to_other_topics', next: "start" }
                ]
            },
            threat: {
                text: "Heh... brave words. But here mate, threats are like throwing toilet paper at iron walls. (His voice lowers dangerously.) You want answers? You bring me something of value. You bring me a piece of metal that sings. Or you'll leave empty-handed.",
                options: [
                    { text: "Ok, tell me more", key: 'ok_tell_me_more', next: "recoverTech" },
                    { text: "Ask something else", key: 'back_to_other_topics', next: "start" }
                ]
            },
            rustReclamation: {
                text: "Actually, there is something you can do for me. As a favor, I can tell you more about where I saw the bishop lately.",
                options: [
                    { text: "Ok, tell me more", key: 'ok_tell_me_more', next: "recoverTech" },
                    { text: "Ask something else", key: 'back_to_other_topics', next: "start" }
                ]
            },
            recoverTech: {
                text: "Well, that's another story. Somewhere at Shed 521 there's an abandoned office, leading to unused tunnels. There's a derelict core I need.\n Find it, and maybe I'll find my memory about your Bishop friend.",
                options: [
                    { text: "Ask something else", key: 'back_to_other_topics', next: "start" }
                ]
            },
            complete_quest: {
                text: "Ah... the living core. (His eyes glimmer with an unsettling light as he takes the artifact.) Yes, this will sing beautifully in our choir.\n\nAs promised, about your Bishop... She got her lens. Paid with a Vestigel — an experimental coin, worth ten of those lenses, and she knew it. Didn't haggle. Don't have it anymore, before you ask. She was quite interested in Dr. Elphi's work. Last I heard, she made her way to Scraper 1140 to meet with the good doctor herself. Seemed... urgent.",
                options: [
                    { text: "Thank you for the information", key: 'thank_you_for_the_information', next: "complete_quest_end" }
                ],
            },
            complete_quest_end: {
                text: "(Gnur returns to his work, humming a strange metallic tune.)",
                options: [
                    { text: "Leave", key: 'leave', next: "end" }
                ],
                // onTrigger, not onShow: a state with onShow is never rendered (its text and "Leave" never appeared)
                onTrigger: () => {
                    // Only complete the quest if we haven't already
                    const quest = this.questSystem.getQuest('rust_reclamation');
                    if (quest && !quest.isComplete) {
                        // Remove living-core from inventory
                        this.removeItemFromInventory('living-core');

                        this.modifyGrowthDecay(0, 1);
                        
                        // Complete rust_reclamation quest
                        this.questSystem.updateQuest('rust_reclamation', 'I have given Gnur the living core. He seems satisfied.', 'core_delivered');
                        this.questSystem.completeQuest('rust_reclamation');
                        
                        // Update find_bishop quest with new information
                        this.questSystem.updateQuest('find_bishop', 'The Bishop bought a pre-war lens from Gnur and paid with a Vestigel — then headed to Scraper 1140 to meet Dr. Elphi.', 'bishop_location_scraper');
                    }
                }
            },
            end: {
                text: "Come back if you need anything... unusual.",
                options: [],
                onShow: () => {
                    this.hideDialog();
                }
            },
            // New dialog branch for confronting Gnur about lying
            confront_about_lie: {
                text: "(Gnur's expression darkens) What lies you talkin' about, mate? I need that core. Ain't no lie in that.",
                options: [
                    { text: "The clerk told me it's crucial for the Shed's energy maintenance. I won't help you sabotage it.", key: 'the_clerk_told_me_its_crucial_for_the_sheds_energy', next: "refuse_quest" },
                    // Only a hand-over if the core is actually in the pack — otherwise complete_quest_end
                    // logged "I have given Gnur the living core" and his Bishop tip without any delivery.
                    { text: "Never mind, I'll still get it for you.", key: 'never_mind_ill_still_get_it_for_you', next: hasLivingCore ? "complete_quest" : "end" }
                ],
                onTrigger: () => {
                    this.addJournalFact('rust_choir_faction', 'any_means', "Their methods are questionable: Gnur still wants the living core, even though the clerk says Shed 521 depends on it. The Choir seems willing to get old tech by any means necessary.");
                }
            },
            refuse_quest: {
                text: "(Gnur's eyes narrow to slits, a metallic growl escaping his throat)\n\nSo you've been talkin' to the paper-pushers, eh? Should've known better than to trust an outsider. Get out of my sight before I decide your lungs would make a fine addition to my collection.",
                options: [
                    { text: "Leave", key: 'leave', next: "end" }
                ],
                onTrigger: () => {
                    // Only fail the quest if we haven't already completed it
                    const quest = this.questSystem.getQuest('rust_reclamation');
                    if (quest && !quest.isComplete) {
                        this.showNotification(this.t('notifications.questFailed'));
                        this.modifyGrowthDecay(5, 0); // Reward growth for making the ethical choice
                        
                        // Update and complete the quest (marking it as failed in the description)
                        this.questSystem.updateQuest('rust_reclamation', 'I refused to help Gnur steal the living core after learning its importance. He was not happy about it.', 'quest_refused');
                        this.questSystem.completeQuest('rust_reclamation'); // Using completeQuest as there's no failQuest method
                    }
                    if (this.registry.get('factionSystem')) {
                        this.modifyFactionReputation('RustChoir', -10);
                        this.modifyFactionReputation('PithReclaimers', 10);
                    }
                }
            },
            rustDomain: {
                text: "Heh, the Rust Choir's domain ain't easy to reach. First you need to pass a test. Make yourself useful to us. Tell me, why do you want to find the Rust Choir headquarters?",
                options: [
                    { text: "I seek knowledge about old technologies and machines.", key: 'i_seek_knowledge_about_old_technologies_and_machin', next: "rustDomainKnowledge" },
                    { text: "I need to speak to Brukk. It's important.", key: 'i_need_to_speak_to_brukk_its_important', next: "rustDomainBrukk" },
                    { text: "I wish to join you. I was... always a big fan of rust and machines.", key: 'i_wish_to_join_you_i_was_always_a_big_fan_of_rust_', next: "rustDomainJoin" },
                    { text: "Ask something else", key: 'back_to_other_topics', next: "start" }
                ]
            },
            rustDomainKnowledge: {
                text: "Knowledge, eh? Well, knowledge is power, and power is rust. Very well, talk to Ravla, cause she's the one who decides who can meet with Brukk. You can usually find her in the Screaming Cork tavern.",
                options: [
                    { text: "Ask something else", key: 'back_to_other_topics', next: "start" }
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('find_rust_choir', 'Gnur mentioned that to reach the Rust Choir headquarters, I need to speak with Ravla at the Screaming Cork tavern first.', 'talk_to_ravla');
                }
                },
            rustDomainBrukk: {
                text: "Important, huh? Brukk values urgency. Talk to Ravla in Screaming Cork tavern first, she will have a little test prepared for you. Once you've done that, she'll arrange a meeting with Brukk. I mean, probably. If she likes you.",
                options: [
                    { text: "Ask something else", key: 'back_to_other_topics', next: "start" }
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('find_rust_choir', 'Gnur mentioned that to reach the Rust Choir headquarters, I need to speak with Ravla at the Screaming Cork tavern first.', 'talk_to_ravla');
                }
            },
            rustDomainJoin: {
                text: "A fan of rust and machines, are you? Well, we do appreciate enthusiasm. Prove your dedication by completing a task for us first. Talk to Ravla in the Screaming Cork tavern. She'll have a little initiation test for you. Pass that, and maybe you'll find yourself among us.",
                options: [
                    { text: "Ask something else", key: 'back_to_other_topics', next: "start" }
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('find_rust_choir', 'Gnur mentioned that to reach the Rust Choir headquarters, I need to speak with Ravla at the Screaming Cork tavern first.', 'talk_to_ravla');
                }
            }
        };

        // Check if find_bishop quest exists
        if (this.questSystem.getQuest('find_bishop') && !this.visitedDialogs.has('bishop')) {
            // Add bishop dialog option to start options if quest exists
            content.start.options.splice(1, 0, { text: "I'm looking for the Bishop. Have you seen her?", key: 'im_looking_for_the_bishop_have_you_seen_her', next: "bishop" });
        }

        // Add quest completion option if player has the quest and the living-core
        if (this.questSystem.getQuest('rust_reclamation') &&
            inventory.items.some(item => item.id ==='living-core')) {
            content.start.options.splice(1, 0, { text: "I have the living core you wanted", key: 'i_have_the_living_core_you_wanted', next: "complete_quest" });
        }

        // Filter background options if rustChoir has been visited
        if (this.visitedDialogs.has('rustChoir')) {
            content.background.options = [
                { text: "Ask something else", key: 'back_to_other_topics', next: "start" }
            ];
        }

        // Update start text if recoverTech has been visited
        if (this.visitedDialogs.has('recoverTech') && !inventory.items.some(item => item.id ==='living-core')) {
            content.start.textKey = 'waiting';
            content.start.text = "Just bring me the living core, then I will talk more";
            content.start.options = promiseMade ? [{ text: "About that living core... you lied to me.", key: 'about_that_living_core_you_lied_to_me', next: "confront_about_lie" }] : [];
        }

        return content;
    }

    showDialog(dialogKey) {
        // Handle faction reputation changes
        // First visit only — re-opening "Who is Brukk?" used to farm +10 reputation every time.
        if ((dialogKey === 'rustChoir' || dialogKey === 'brukk' || dialogKey === 'complete_quest') && !this.visitedDialogs.has(dialogKey)) {
            const factionSystem = this.registry.get('factionSystem');
            if (factionSystem) {
                this.modifyFactionReputation('RustChoir', 10);
                if (!this.hasJournalEntry('rust_choir_faction')) {
                    this.addJournalEntry(
                        'rust_choir_faction',
                        'The Rust Choir',
                        'The Rust Choir is one of the factions that hold sway in Upper Morkezela.',
                        this.journalSystem.categories.FACTIONS,
                        { faction: 'Rust Choir', location: 'Shed 521' }
                    );
                }
            }
        }

        // Handle quest updates
        const questSystem = this.registry.get('questSystem');
        if (questSystem) {
            if (dialogKey === 'bishop' && questSystem.quests.has('find_bishop')) {
                questSystem.updateQuest('find_bishop', "Gnur says the Bishop came down to Shed 521 for a lens from the old pre-war dream rigs — Rust Choir stock. He wants something in return before he says more.", 'bishop_clue_gnur');
            } else if (dialogKey === 'recoverTech' && !questSystem.getQuest('rust_reclamation')) {
                questSystem.addQuest(
                    'rust_reclamation',
                    'Rust Reclamation',
                    "Gnur needs help recovering a 'living core' from Shed 521's unused tunnels, located somewhere behind the abandoned office."
                );
                this.modifyGrowthDecay(1, 0);
            }
        }

        // Track visited dialogs
        this.visitedDialogs.add(dialogKey);

        // Show the dialog content
        super.showDialog(dialogKey);
    }

    create() {
        super.create();


        // Set up scene background and elements
        const bg = this.add.image(400, 300, 'Shed521Bg'); // native 1067×600 (redrawn: the tower, fence, yard)
        this.fitBackground(bg);
        bg.setDepth(-1);
        this.applyShedGDState(bg);
        // The background paints its own rutted track; the generic ground strip would cover it.
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }
        this.playSceneMusic('genericMusic');

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);

        // Examine: the rust-choked pipes/guts of the Shed (upper-centre, clear of Gnur below).
        this.createObservable(400, 195, 240, 150, () => {
            if (this.hasJournalEntry('rust_choir_joined')) return this.t('observe.shed_pipes.member');
            return this.t('observe.shed_pipes.default');
        }, { hint: this.t('observe.shed_pipes.hint') });

        // Add Gnur NPC with proper size
        this.gnur = this.add.sprite(400, 470, 'gnur');
        this.gnur.setDisplaySize(80, 80); // Set a fixed size
        this.gnur.setDepth(6); // standing-NPC layer: in front of the G/D props (4) and the ground, behind the player (20)
        this.gnurShadow = this.addGroundShadow(400, 470 + this.gnur.displayHeight * 0.42, this.gnur.displayWidth * 0.55, this.gnur.displayHeight * 0.12);
        this.gnur.setInteractive({ useHandCursor: true });

        // Looping walk-cycle animation (anims are global — create once).
        if (!this.anims.exists('gnur_walk')) {
            this.anims.create({
                key: 'gnur_walk',
                frames: this.anims.generateFrameNumbers('gnur', { start: 0, end: 5 }),
                frameRate: 8,
                repeat: -1
            });
        }
        this.gnur.play('gnur_walk');

        // Create transition to Shed521FloorsScene at the elevator
        this.transitionManager = new SceneTransitionManager(this);
        
        this.transitionManager.createTransitionZone(
            291, // x position (800-space; remapped onto the tower's gate in the redrawn background)
            400, // y position
            100, // width
            200, // height
            'right', // direction
            'Shed521FloorsScene', // target scene
            291, // walk to x
            470  // walk to y
        );
        
        // Add walking animation to Gnur
        this.tweens.add({
            targets: this.gnur,
            x: this.gnur.x + 200, // Walk 200 pixels to the right
            duration: 3000,
            ease: 'Linear',
            yoyo: true, // Makes it go back and forth
            repeat: -1, // Infinite repeat
            onYoyo: () => {
                this.gnur.setFlipX(true); // Flip sprite when walking left
            },
            onRepeat: () => {
                this.gnur.setFlipX(false); // Reset flip when walking right
            }
        });
        
        // Add subtle bobbing animation for walking
        this.tweens.add({
            targets: this.gnur,
            y: this.gnur.y - 5, // Small up and down movement
            duration: 500,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });
        
        // Handle Gnur interactivity
        this.gnur.setInteractive({ useHandCursor: true });
        
        // Add interaction with Gnur
        this.gnur.on('pointerdown', () => {
            if (!this.dialogVisible) {
                this.dialogState = 'start';  // Set initial dialog state
                this.showDialog(this.dialogState);
            }
        });
        
        // Position the priest at the left side when entering
        this.priest.x = 100;
        this.priest.y = 470;
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }
        
        // Create exit to CrossroadScene at the right edge
        this.transitionManager.createTransitionZone(
            750, // x position
            470, // y position
            40,  // width
            200, // height
            'right', // direction
            'CrossroadScene', // target scene
            700, // walk to x
            470  // walk to y
        );
    }

    /**
     * Growth/Decay state of the yard. Growth: the tower greens over (alt art) + a flowering bush, mushrooms and a
     * vine on the gate. Decay: more rust, missing planks, a sagging fence (alt art) + litter, a broken crate and a
     * burning barrel. Balanced: nothing beyond the global ambience wash. The Rust Choir wants this building, so
     * decay is "their" look here.
     */
    applyShedGDState(bg) {
        applyGDBackground(this, bg, 'Shed521Bg');
        placeGDProps(this, {
            growth: [
                { prop: 'bush', x: 236, y: 496 },
                { prop: 'bush', x: 884, y: 490, flipX: true, scale: 0.8 },
                { prop: 'mushrooms', x: 690, y: 502 },
                { prop: 'vine', x: 404, y: 332 }          // hangs off the gate lintel
            ],
            decay: [
                { prop: 'fire', x: 704, y: 500 },
                { prop: 'trash', x: 252, y: 498 },
                { prop: 'crate', x: 868, y: 494 },
                { prop: 'rubble', x: 470, y: 506 }
            ]
        });
    }

    preload() {
        super.preload();
        this.load.image('Shed521Bg', 'assets/images/backgrounds/Shed521.png');
        // Growth/Decay variants of the yard (same generator, other parameters) + the shared G/D props.
        this.load.image('Shed521Bg_growth', 'assets/images/backgrounds/Shed521_growth.png');
        this.load.image('Shed521Bg_decay', 'assets/images/backgrounds/Shed521_decay.png');
        preloadGDProps(this);
        this.load.image('exitArea', 'assets/images/ui/door.png');
        // Load Gnur sprite
        // Gnur2 = Gnur as a 6-frame walk-cycle spritesheet (3×2 grid, 582×982 per frame).
        this.load.spritesheet('gnur', './assets/images/characters/Gnur2.png', { frameWidth: 582, frameHeight: 982 });
    }

    update() {
        super.update();
        if (this.gnurShadow && this.gnur) this.gnurShadow.x = this.gnur.x; // the shadow walks with him (the bob stays off the ground)
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.Shed521Scene = Shed521Scene;
}
