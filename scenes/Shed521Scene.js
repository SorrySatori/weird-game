import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
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
                text: this._dialogTextCache.start || "Another stray wanderin' down the veins of Shed521...\nWhat're you lookin' for, outsider? Body upgrade? New lungs? Or just bad ideas?\nHe chuckles, voice crackling like a broken choir.\nSay your need. Maybe ol' Gnur's got a whisper to sell.",
                options: [
                    { text: "Who are you exactly?", key: 'who_are_you_exactly', next: "background" },
                    // Add the option to confront Gnur about lying if player made the promise
                    ...(promiseMade ? [{ text: "About that living core... you lied to me.", key: 'about_that_living_core_you_lied_to_me', next: "confront_about_lie" }] : []),
                    ...(hasFindRustQuest ? [{ text: "I'm looking for the way how to reach the Rust Choir headquarters in the Scraper. Can you help me?", key: 'im_looking_for_the_way_how_to_reach_the_rust_choir', next: "rustDomain" }] : []),
                    ...(canSpyGnur ? [{ text: "You said you sell whispers. What's the Rust Choir not saying out loud?", key: 'gnur_spy_probe', next: "gnur_spy_secret" }] : []),
                    ...(canSpyGnurUlvarex ? [{ text: "[Ulvarex · Mirage Weave] (Let him see a Rust superior, and demand the whole truth.)", key: 'gnur_spy_ulvarex', next: "gnur_spy_ulvarex_read" }] : []),
                ],
                onTrigger: () => {
                    // Add journal entry about meeting Gnur
                    if (!this.hasJournalEntry('gnur_meeting')) {
                        this.addJournalEntry(
                            'gnur_meeting',
                            'Gnur of the Rust Choir',
                            'In the guts of Shed 521, I encountered Gnur, a figure whose voice crackles "like a broken choir." He seems to be a dealer in body modifications and other questionable services. There\'s something unsettling about him - his connection to the mysterious Rust Choir suggests a deeper involvement with the city\'s hidden infrastructures and technologies than his shabby appearance would suggest.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Gnur', faction: 'Rust Choir', location: 'Shed 521' }
                        );
                    }
                }
            },
            gnur_spy_ulvarex_read: {
                text: "Ulvarex pours light across your outline and *bends* it — and Gnur's forge-eyes go wide with recognition at a superior who was never there. \"Ah — didn't hear you come down, boss, forgive me—\" He stands straighter, eager to please the phantom. \"The mole? Yeah, yeah, still singing sweet. Their little archivist in the Lumen Directorate feeds Brukk which districts the pretty people are about to write off, so we know which machines'll be goin' cheap. And there's talk of a *second* pair of hands inside, higher up, but I ain't been told a name.\" He blinks as the mirage frays. \"...Wait. Who—\" Too late; you have it.",
                options: [
                    { text: "(Let the mirage dissolve.)", key: 'gnur_spy_ulvarex_close', next: "start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(0, 5);
                    this.showNotification('You wore a lie like a face. The world sours toward Decay.', 0x8B0000);
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
                text: "Used to keep the machines running in the old days. Now I'm with the Rust Choir. We sing the old machines awake... or lull the new flesh to sleep. Depends who's buying.",
                options: [
                    { text: "Tell me about the Rust Choir", key: 'tell_me_about_the_rust_choir', next: "rustChoir" },
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "start" }
                ]
            },
            rustChoir: {
                text: "We celebrate entropy, collapse as transformation, we... worship 'final songs'. We like to trade in secrets, especially old tech. If you are interested to know more, visit the old Scraper and talk to Brukk's people.",
                options: [
                    { text: "Who is Brukk?", key: 'who_is_brukk', next: "brukk" },
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "start" }
                ]
            },
            brukk: {
                text: "Brukk is our leader if we had any... He is the keeper of the old tech, the one who can help you find what you're looking for. That's all I can tell you.",
                options: [
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "start" }
                ]
            },
            bishop: {
                text: "Ahhh, the shrouded one... yeah, she passed through, glimmer-eyed and restless. But info ain't free, friend.",
                options: [
                    { text: "What do you want?", key: 'what_do_you_want', next: "rustReclamation" },
                    { text: "I can help you recover old tech carefully", key: 'i_can_help_you_recover_old_tech_carefully', next: "recoverTech" },
                    { text: 'Tell me what I want to know... or else.', key: 'tell_me_what_i_want_to_know_or_else', next: 'threat'},
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "start" }
                ]
            },
            threat: {
                text: "Heh... brave words from soft lungs. But here, threats are like throwing paper at iron walls. (His voice lowers dangerously.) You want answers? You bring me value. You bring me rust that sings. Or you'll leave here empty, maybe even emptier.",
                options: [
                    { text: "Ok, tell me more", key: 'ok_tell_me_more', next: "recoverTech" },
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "start" }
                ]
            },
            rustReclamation: {
                text: "Actually, there is something you can do for me. As a favor, I can tell you more about where I saw the bishop lately.",
                options: [
                    { text: "Ok, tell me more", key: 'ok_tell_me_more', next: "recoverTech" },
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "start" }
                ]
            },
            recoverTech: {
                text: "Now that is a tune I can hum to. Somewhere at Shed 521 there's an abandoned office, leading to unused tunnels. There's a derelict core I need pulled out — still breathing, barely.\n Find it, and maybe I'll find my memory about your Bishop friend.",
                options: [
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "start" }
                ]
            },
            complete_quest: {
                text: "Ah... the living core. (His eyes glimmer with an unsettling light as he takes the artifact.) Yes, this will sing beautifully in our choir.\n\nAs promised, about your Bishop... She was quite interested in Dr. Elphi's work. Last I heard, she made her way to Scraper 1140 to meet with the good doctor herself. Seemed... urgent.",
                options: [
                    { text: "Thank you for the information", key: 'thank_you_for_the_information', next: "complete_quest_end" }
                ],
            },
            complete_quest_end: {
                text: "(Gnur returns to his work, humming a strange metallic tune.)",
                options: [
                    { text: "Leave", key: 'leave', next: "end" }
                ],
                onShow: () => {
                    // Only complete the quest if we haven't already
                    const quest = this.questSystem.getQuest('rust_reclamation');
                    if (quest && !quest.isComplete) {
                        // Remove living-core from inventory
                        this.removeItemFromInventory('living-core');

                        this.showNotification('Quest completed: Rust Reclamation');
                        this.modifyGrowthDecay(0, 1);
                        
                        // Complete rust_reclamation quest
                        this.questSystem.updateQuest('rust_reclamation', 'I have given Gnur the living core. He seems satisfied.', 'core_delivered');
                        this.questSystem.completeQuest('rust_reclamation');
                        
                        // Update find_bishop quest with new information
                        this.questSystem.updateQuest('find_bishop', 'The Bishop was last seen heading to Scraper 1140 to meet with Dr. Elphi.', 'bishop_location_scraper');
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
                text: "(Gnur's expression darkens) What lies you talkin' about, outsider? I need that core. Ain't no lie in that.",
                options: [
                    { text: "The clerk told me it's crucial for the Shed's energy maintenance. I won't help you sabotage it.", key: 'the_clerk_told_me_its_crucial_for_the_sheds_energy', next: "refuse_quest" },
                    { text: "Never mind, I'll still get it for you.", key: 'never_mind_ill_still_get_it_for_you', next: "complete_quest" }
                ]
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
                        this.showNotification('Quest failed: Rust Reclamation');
                        this.modifyGrowthDecay(5, 0); // Reward growth for making the ethical choice
                        
                        // Update and complete the quest (marking it as failed in the description)
                        this.questSystem.updateQuest('rust_reclamation', 'I refused to help Gnur steal the living core after learning its importance. He was not happy about it.', 'quest_refused');
                        this.questSystem.completeQuest('rust_reclamation'); // Using completeQuest as there's no failQuest method
                    }
                    const factionSystem = this.registry.get('factionSystem');
                    if (factionSystem) {
                        factionSystem.modifyReputation('RustChoir', -10);
                        factionSystem.modifyReputation('PithReclaimers', +10);
                        this.showNotification('Rust Choir Reputation -10');
                        this.showNotification('Pith Reclaimers Reputation +10');
                    }
                }
            },
            rustDomain: {
                text: "Heh, the Rust Choir's domain ain't easy to reach. First you need to pass a test. Make yourself useful to us. Tell me, why do you want to find the Rust Choir headquarters?",
                options: [
                    { text: "I seek knowledge about old technologies and machines.", key: 'i_seek_knowledge_about_old_technologies_and_machin', next: "rustDomainKnowledge" },
                    { text: "I need to speak to Brukk. It's important.", key: 'i_need_to_speak_to_brukk_its_important', next: "rustDomainBrukk" },
                    { text: "I wish to join you. I was... always a big fan of rust and machines.", key: 'i_wish_to_join_you_i_was_always_a_big_fan_of_rust_', next: "rustDomainJoin" },
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "start" }
                ]
            },
            rustDomainKnowledge: {
                text: "Knowledge, eh? Well, knowledge is power, and power is rust. Very well, talk to Ravla, cause she's the one who decides who can meet with Brukk. You can usually find her in the Creaming Cork tavern.",
                options: [
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "start" }
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('find_rust_choir', 'Gnur mentioned that to reach the Rust Choir headquarters, I need to speak with Ravla at the Screaming Cork tavern first.', 'talk_to_ravla');
                }
                },
            rustDomainBrukk: {
                text: "Important, huh? Brukk values urgency. Talk to Ravla in Screaming Cork tavern first, she will have a little test prepared for you. Once you've done that, she'll arrange a meeting with Brukk. I mean, probably. If she likes you.",
                options: [
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "start" }
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('find_rust_choir', 'Gnur mentioned that to reach the Rust Choir headquarters, I need to speak with Ravla at the Screaming Cork tavern first.', 'talk_to_ravla');
                }
            },
            rustDomainJoin: {
                text: "A fan of rust and machines, are you? Well, we do appreciate enthusiasm. Prove your dedication by completing a task for us first. Talk to Ravla in the Screaming Cork tavern. She'll have a little initiation test for you. Pass that, and maybe you'll find yourself among us.",
                options: [
                    { text: "Back to other topics", key: 'back_to_other_topics', next: "start" }
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('find_rust_choir', 'Gnur mentioned that to reach the Rust Choir headquarters, I need to speak with Ravla at the Screaming Cork tavern first.', 'talk_to_ravla');
                }
            }
        };

        // Check if find_bishop quest exists
        if (this.questSystem.getQuest('find_bishop') && !this.visitedDialogs.has('bishop')) {
            // Add bishop dialog option to start options if quest exists
            content.start.options.splice(1, 0, { 
                text: "I'm looking for the Bishop. Have you seen her?", 
                next: "bishop" 
            });
        }

        // Add quest completion option if player has the quest and the living-core
        if (this.questSystem.getQuest('rust_reclamation') &&
            inventory.items.some(item => item.id ==='living-core')) {
            content.start.options.splice(1, 0, {
                text: "I have the living core you wanted",
                next: "complete_quest"
            });
        }

        // Filter background options if rustChoir has been visited
        if (this.visitedDialogs.has('rustChoir')) {
            content.background.options = [
                { text: "Back to other topics", next: "start" }
            ];
        }

        // Update start text if recoverTech has been visited
        if (this.visitedDialogs.has('recoverTech') && !inventory.items.some(item => item.id ==='living-core')) {
            content.start.text = "Just bring me the living core, then I will talk more";
            content.start.options = promiseMade ? [{ text: "About that living core... you lied to me.", next: "confront_about_lie" }] : [];
        }

        return content;
    }

    showDialog(dialogKey) {
        // Handle faction reputation changes
        if (dialogKey === 'rustChoir' || dialogKey === 'brukk' || dialogKey === 'complete_quest') {
            const factionSystem = this.registry.get('factionSystem');
            if (factionSystem) {
                factionSystem.modifyReputation('RustChoir', 10);
                this.showNotification('Rust Choir Reputation +10');
                if (!this.hasJournalEntry('rust_choir_faction')) {
                    this.addJournalEntry(
                        'rust_choir_faction',
                        'The Rust Choir - Machines and Memory',
                        'The Rust Choir appears to be a faction with an interest in old technology and machinery. They "sing the old machines awake" according to rumor, and seem to value the preservation and control of ancient tech. Their methods are questionable, as they appear willing to obtain technological artifacts through any means necessary.',
                        this.journalSystem.categories.FACTIONS,
                        { faction: 'Rust Choir', location: 'Shed521' }
                    );
                }
            }
        }

        // Handle quest updates
        const questSystem = this.registry.get('questSystem');
        if (questSystem) {
            if (dialogKey === 'bishop' && questSystem.quests.has('find_bishop')) {
                questSystem.updateQuest('find_bishop', "The Bishop was seen at Scraper 1140, making an unusual trade involving a 'game lens'. Gnur might know more, but he wants something in return.", 'bishop_clue_gnur');
                this.showNotification('Quest updated: Find the Bishop');
            } else if (dialogKey === 'recoverTech') {
                questSystem.addQuest(
                    'rust_reclamation',
                    'Rust Reclamation',
                    "Gnur needs help recovering a 'living core' from Shed 521's unused tunnels, located somewhere behind the abandoned office."
                );
                this.showNotification('Quest added: Rust Reclamation');
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
        const bg = this.add.image(400, 300, 'Shed521Bg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
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
        this.gnur.setDepth(1); // Ensure it's above background
        this.addGroundShadow(400, 470 + this.gnur.displayHeight * 0.42, this.gnur.displayWidth * 0.55, this.gnur.displayHeight * 0.12);
        this.gnur.setInteractive({ useHandCursor: true });

        // Create transition to Shed521FloorsScene at the elevator
        this.transitionManager = new SceneTransitionManager(this);
        
        this.transitionManager.createTransitionZone(
            200, // x position
            400, // y position
            120, // width
            200, // height
            'right', // direction
            'Shed521FloorsScene', // target scene
            100, // walk to x
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

    preload() {
        super.preload();
        this.load.image('Shed521Bg', 'assets/images/backgrounds/Shed521.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
        this.load.image('mysteriousSpore', 'assets/images/items/spore.png');
        // Load Gnur sprite
        this.load.image('gnur', './assets/images/characters/Gnur.png');
    }

    update() {
        super.update();
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.Shed521Scene = Shed521Scene;
}
