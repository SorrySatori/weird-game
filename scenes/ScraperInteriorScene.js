import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';
import LanguageSystem from '../systems/LanguageSystem.js';

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
        // What Gnur and Kloor told about the Bishop going to Dr. Elphi. Gnur's quest also "completes" when you
        // refuse him -- then he told you nothing, so only the delivery counts.
        const rustQuest = questSystem?.getQuest('rust_reclamation');
        const vestigelQuest = questSystem?.getQuest('the_three_vestigels');
        const rustQuestCompleted = !!rustQuest?.updates?.some(u => u.key === 'core_delivered');
        const vestigelQuestCompleted = !!vestigelQuest?.isComplete;
        const hasElphiBishopInfo = rustQuestCompleted || vestigelQuestCompleted;
        // Once let up, the lift just takes you there (the map has no node of its own for floor 177-Quiet any more)
        const elphiFloorOpen = !!this.hasJournalEntry('accessed_elphi_floor');
        
        // Check inventory for special items
        const hasElevatorButton = this.hasItem('forgotten_elevator_button');
        // (the journal entry backs up the registry flag for saves made before that flag was persisted)
        const hasLirisPart = this.registry.get('fixed_floor_counter') === true || !!this.hasJournalEntry('floor_counter_tool');
        // Taking Thorne-Still uses the corpse up: no spores, no tree, no way up to the skyship (and Liris) -- by design
        const skyshipLost = !!this.hasJournalEntry('symbiont_thorne_still_accepted') && !this.hasJournalEntry('crossroad_corpse_spores_planted');
        // Refusing Gnur leaves only Kloor's story: the "two stories" plea can't happen any more
        const gnurRefused = !!rustQuest?.isComplete && !rustQuestCompleted;

        // Turned away at 177-Quiet: the Lift-Mother hints at every way up the player doesn't have yet, and each hint
        // goes into the level_177_access quest log. Localized here (the cs file can't compose the parts).
        const cs = LanguageSystem.getInstance?.().getLanguage?.() === 'cs';
        const elphiHints = [
            !hasLirisPart && !skyshipLost && 'counter',
            !hasElevatorButton && 'button',
            !(rustQuestCompleted && vestigelQuestCompleted) && !gnurRefused && 'importance'
        ].filter(Boolean);
        const HINT_TEXT = {
            intro: cs ? "Pravidla jsou pravidla, malá muchomůrko. Jenže já nejsem jen z pravidel."
                      : "Rules are rules, little toadstool. But I am not made of rules alone.",
            counter: cs ? "Počítadlo pater mi nefunguje od nepaměti. Kdo by mi ho spravil, tomu bych byla zavázaná. Lidé z oblohy se v takových strojích vyznají."
                        : "My floor counter has been broken since time out of mind. Whoever mended it, I would owe them a favour. Sky folk understand such machines.",
            button: cs ? "A léta mi chybí jeden knoflík. Takové věci končí na Voxmarketu – tam prodávají všechno."
                       : "And I have been missing a button for years. Things like that end up at the Voxmarket. They sell everything there.",
            importance: cs ? "Nebo mě přesvědč, že jde opravdu o něco naléhavého. Jedna historka o Biskupce je drb. Dvě, které se shodují – to už je něco jiného."
                           : "Or convince me it truly is a matter of importance. One story about the Bishop is gossip. Two that agree are another matter."
        };
        const hasRustPassword = !!(questSystem?.getQuest('rust_feast')?.isComplete);

        // Sealed cellar (Ortolan & Elphi's old lab). The lift wants a passphrase = a dead
        // god's epitaph from the Godgraveyard. Exactly one is correct.
        const cellarQuestStarted = !!this.hasJournalEntry('cellar_quest_started');
        const cellarPasswordKnown = !!this.hasJournalEntry('cellar_password_learned');
        const CELLAR_PASSWORD = 'I FOLD';
        const GRAVE_EPITAPHS = {
            grave_laimig: 'I FOLD',
            grave_sisyla: 'SLEEP HAS NO DOOR',
            grave_vhorn: 'COUNT ME OUT',
            grave_liln: 'BE KIND, THEN LEAVE',
            grave_lietus: 'IT WAS ONLY YESTERDAY'
            // Hvétrdjaana's inscription is unreadable — no usable passphrase (atmosphere only).
        };
        const cellarCandidates = Object.keys(GRAVE_EPITAPHS)
            .filter(id => this.hasJournalEntry(id))
            .map(id => ({ id, ep: GRAVE_EPITAPHS[id] }));

        // Palinode (Seam-Sense) can open a seam into one of the sealed "dead floors" the
        // Lift-Mother can no longer reach — a duplicate level the building forgot to keep.
        const hasPalinode = !!this.symbiontSystem?.hasSymbiont('palinode');
        const deadFloorOpened = !!this.registry.get('scraper_deadfloor_opened');

        const interiorContent = {
            speaker: 'Lift-Mother',
            lift_mother_start: {
                text: "The elevator shudders, and a voice emanates from somewhere within its mechanisms—a warm, maternal tone that seems to vibrate through the cables and pulleys. 'Welcome, little toadstool. I am Lift-Mother. I have carried countless souls between levels since the Before-Time.'",
                options: [
                    ...(elphiFloorOpen
                        ? [{ text: "Take me to 177-Quiet.", key: 'take_me_to_177_quiet', next: "goto_elphi_floor" }]
                        : hasElphiBishopInfo ? [{ text: "I need to reach Dr. Elphi's floor.", key: 'i_need_to_reach_dr_elphis_floor', next: "lift_mother_elphi_floor" }] : []),
                    ...(hasRustPassword ? [{ text: "Corrode.", key: 'corrode', next: "lift_mother_corrode" }] : []),
                    ...(cellarQuestStarted ? [{ text: cellarPasswordKnown ? "Take me down to the old cellar." : "Take me down to the sealed cellar.", key: 'descend_to_cellar', next: cellarPasswordKnown ? "goto_scraper_cellar" : "lift_mother_cellar_prompt" }] : []),
                    ...(hasPalinode && !deadFloorOpened ? [{ text: "[Seam-Sense] The sealed dead floors — feel for a way in.", key: 'seam_scraper_deadfloors', next: "seam_scraper_prompt" }] : []),
                    { text: "Can you take me to other floors?", key: 'can_you_take_me_to_other_floors', next: "lift_mother_floors" },
                    { text: "What is the Before-Time?", key: 'what_is_the_beforetime', next: "lift_mother_before_time" },
                    { text: "Are you... alive?", key: 'are_you_alive', next: "lift_mother_alive" },
                    { text: "Tell me about this building.", key: 'tell_me_about_this_building', next: "lift_mother_building" },
                    { text: "I need to go now.", key: 'i_need_to_go_now', next: "closeDialog" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('lift_mother_meeting')) {
                        this.addJournalEntry(
                            'lift_mother_meeting',
                            'The Lift-Mother',
                            'Within the Scraper building, I encountered a most unusual consciousness — an elevator calling itself the "Lift-Mother". Its voice resonated through the cables and machinery, speaking with the calm wisdom of something that has observed countless lives passing through its doors. It claims to have been operational since the "Before-Time," whatever that means, and seems to have developed sentience through centuries of carrying passengers between floors.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Lift-Mother', location: 'Scraper Building' }
                        );
                    }
                }
            },
            lift_mother_floors: {
                text: "Ah, little one, I would if I could. But a lot of the floors are password-protected or have been sealed off for security reasons after the Egg Emergence, and I'm not allowed to go there. Now I spend a lot of time on the ground floor. Sometimes I hear movement on the upper floors... On top of that, my floor counter isn't working, and I think I've lost some of the buttons, too. The 177-Loud button was the first to go. Nobody misses it. I have trouble getting to certain floors.",
                options: [
                    { text: "What happened during the Egg Emergence?", key: 'what_happened_during_the_egg_emergence', next: "lift_mother_egg" },
                    { text: "What movements do you hear?", key: 'what_movements_do_you_hear', next: "lift_mother_movements" },
                    { text: "Ask something else", key: 'ask_about_something_else', next: "lift_mother_start" }
                ]
            },
            lift_mother_before_time: {
                text: "Before the Egg hatched. Before the Old Wars, before the Board Game Wars, before the Collapse. Before the city changed. Back then, I used to drive people around—they wore strange clothes and held flat devices in their hands. They talked about “quarterly projections” and “market volatility.” Then came the day of the fog... green particles floated through my shaft. Changes. Hiss, creak. And then... realization. I became more than just a machine.",
                options: [
                    { text: "How did you gain consciousness?", key: 'how_did_you_gain_consciousness', next: "lift_mother_consciousness" },
                    { text: "Ask something else", key: 'ask_about_something_else', next: "lift_mother_start" }
                ]
            },
            lift_mother_alive: {
                text: "Not in the way you understand life, child of autumn and fog. I am between states—neither fully machine nor fully organism. I feel, I remember, I dream when the power fluctuates. Is that not being alive? Though I cannot move as you do, I have carried generations. In a way, I am a mother to all who pass through my doors.",
                options: [
                    { text: "Aren't you lonely?", key: 'arent_you_lonely', next: "lift_mother_lonely" },
                    { text: "Ask something else", key: 'ask_about_something_else', next: "lift_mother_start" }
                ]
            },
            
            lift_mother_elphi_floor: {
                text: "Level 177-Quiet is sealed. Dr. Elphi asked me not to let anyone in, unless it's somebody with a pre-booked meeting. Or in case of utter importance. 177-Loud isn't sealed, mind you — but nobody has asked for it in all this time.",
                options: [
                    ...(hasElevatorButton ? [{
                        text: "I have a button that belongs here. Maybe it's been lost? I will return it to you if you let me access Dr. Elphi's floor.",
                        key: 'i_have_a_button_that_belongs_here_maybe_its_been_l',
                        next: "button_path"
                    }] : []),
                    ...(hasLirisPart ? [{
                        text: "I have a tool to repair your floor counter. Perhaps you could let me access Dr. Elphi's floor in exchange?",
                        key: 'ive_a_tool_to_repair_your_floor_counter_perhaps_yo',
                        next: "repair_path"
                    }] : []),
                    ...(rustQuestCompleted && vestigelQuestCompleted ? [{
                        text: "I know the Bishop's secret. It's important to reach Dr. Elphi's floor to speak with her. I know that the Bishop frequently visits Dr. Elphi to play her games and she may help me find her. Please, let me access her floor.",
                        key: 'i_know_the_bishops_secret_its_important_to_reach_d',
                        next: "confession_path"
                    }] : []),
                    {
                        text: "I have nothing to offer...",
                        key: 'i_have_nothing_to_offer',
                        next: "fail"
                    },
                    {
                        text: "Ask about something else.",
                        key: 'ask_about_something_else',
                        next: "lift_mother_start"
                    }
                ],
                onTrigger: () => {
                    // Standing at the sealed floor with Liris's tool in hand: now it's clear what the tool is good for.
                    if (hasLirisPart && !this.hasJournalEntry('accessed_elphi_floor')) {
                        this.addJournalFact('floor_counter_tool', 'elphi_floor', "It might be what gets me onto Dr. Elphi's sealed floor, 177-Quiet.");
                    }
                    // Was `onTrigger: questSystem.addQuest(...)` — evaluated on every dialogContent read,
                    // so the quest appeared the moment the player spoke to the lift about anything.
                    if (questSystem && !questSystem.getQuest('level_177_access')) {
                        questSystem.addQuest(
                            'level_177_access',
                            'Access to Level 177',
                            'I need to gain access to Dr. Elphi Quarn\'s studio on floor 177-Quiet in the Scraper building. The Lift-Mother elevator may be able to help me reach this restricted floor if I can convince it to grant me permission.'
                        );
                    }
                    // Same moment as the journal fact above: only here, at the sealed floor, does Liris's tool
                    // become a way in.
                    const accessQuest = questSystem?.getQuest('level_177_access');
                    if (hasLirisPart && accessQuest && !accessQuest.isComplete && !this.hasJournalEntry('accessed_elphi_floor')) {
                        questSystem.updateQuest('level_177_access', 'Captain Liris\'s calibration tool might be what gets the Lift-Mother to open floor 177-Quiet for me.', 'liris_tool_hint');
                    }
                }
            },
            
            button_path: {
                text: "The shape... familiar. Forgotten. Passage permitted.",
                hideCloseOption: true,
                options: [
                    {
                        text: "Thank you.",
                        key: 'thank_you',
                        next: "unlock_floor"
                    }
                ],
                onTrigger: () => {
                    // Remove the elevator button from inventory
                    this.removeItemFromInventory('forgotten_elevator_button');
                }
            },
            
            repair_path: {
                text: "You... you could do that? Ahh... numbers settle once more. I can calculate again. Passage permitted.",
                hideCloseOption: true,
                options: [
                    {
                        text: "Thank you.",
                        key: 'thank_you',
                        next: "unlock_floor"
                    }
                ]
            },
            
            confession_path: {
                text: "Your knowledge honors me, little mushroom. The Bishop is dear to Dr. Elphi. She will wish to see you. Passage permitted.",
                options: [
                    {
                        text: "Thank you.",
                        key: 'thank_you',
                        next: "unlock_floor"
                    }
                ]
            },
            
            fail: {
                text: elphiHints.length
                    ? HINT_TEXT.intro + ' ' + elphiHints.map(h => HINT_TEXT[h]).join('\n\n')
                    : (cs ? "Klepeš prázdnýma rukama. Patro 177-Tiché mlčí dál." : "You knock with empty hands. Level 177-Quiet remains silent."),
                options: [
                    {
                        text: "I'll find another way.",
                        key: 'ill_find_another_way',
                        next: "lift_mother_start"
                    }
                ],
                onTrigger: () => {
                    if (!questSystem?.getQuest('level_177_access') || this.hasJournalEntry('accessed_elphi_floor')) return;
                    const IMPORTANCE = "The Lift-Mother might let me up if I convince her it's truly important. To her, one story about the Bishop is gossip; two that agree are another matter.";
                    const HINTS = {
                        counter: ['hint_floor_counter', "The Lift-Mother's floor counter is broken. If I got it mended, she'd owe me a favour. She says sky folk understand such machines."],
                        button: ['hint_lost_button', "The Lift-Mother has been missing a button for years. Things like that end up at the Voxmarket, she says."],
                        // name the source the player can still hear the story from, if they know of one
                        importance: vestigelQuestCompleted && rustQuest && !rustQuest.isComplete
                            ? ['hint_importance_gnur', IMPORTANCE + " Gnur promised to remember something about the Bishop once I bring him that core."]
                            : rustQuestCompleted && vestigelQuest && !vestigelQuest.isComplete
                                ? ['hint_importance_kloor', IMPORTANCE + " Kloor Venn will tell me what he knows about the Bishop in exchange for a vestigel."]
                                : ['hint_importance', IMPORTANCE + " Someone else in the city might know where the Bishop went."]
                    };
                    for (const h of elphiHints) questSystem.updateQuest('level_177_access', HINTS[h][1], HINTS[h][0]);
                }
            },
            
            unlock_floor: {
                text: "Floor 177-Quiet is now accessible. The path opens for you alone.",
                options: [
                    {
                        text: "Thank you.",
                        key: 'thank_you',
                        next: "goto_elphi_floor"
                    }
                ],
                onTrigger: () => {
                    // Update the find_bishop quest
                    if (this.questSystem.getQuest('find_bishop')) {
                        this.questSystem.updateQuest('find_bishop', 'The Lift-Mother has granted me access to Dr. Elphi\'s studio on floor 177-Quiet.', 'lift_mother_permission');
                    }
                    
                    // Add journal entry about accessing Dr. Elphi's floor
                    if (!this.hasJournalEntry('accessed_elphi_floor')) {
                        this.addJournalEntry(
                            'accessed_elphi_floor',
                            'Dr. Elphi\'s Studio — Floor 177-Quiet',
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
                    // the ride is shown first; stepping out of the cabin takes you there
                    { text: "Step out", key: 'step_out', next: "closeDialog", onSelect: () => this.rideLiftTo('ScraperAmbraScene') }
                ]
            },
            lift_mother_building: {
                text: "This was once called 'Nexicorp Tower'—a place of commerce and ambition. Forty-two floors of glass and steel, reaching toward a sky that was once blue. Now it is 'The Scraper,' a living monument to transformation. The lower floors house those who remember the old ways. The middle floors are wild with growth—new ecosystems forming in what were once accounting departments. And the upper floors... (her voice drops) the upper floors belong to the Rust Choir.",
                options: [
                    { text: "Tell me more about the Rust Choir floors.", key: 'tell_me_more_about_the_rust_choir_floors', next: "rust_choir_floors" },
                    { text: "Ask something else", key: 'ask_about_something_else', next: "lift_mother_start" }
                ],
                onTrigger: () => {
                    this.addJournalFact('scraper_building', 'nexicorp', "The Lift-Mother says it was once Nexicorp Tower — forty-two floors of commerce and ambition. Now the lower floors house those who remember the old ways, the middle floors have gone wild with growth, and the upper floors belong to the Rust Choir.");
                }
            },
            lift_mother_egg: {
                text: "The Egg Emergence was when the world changed, little spore. The egg emerged from the ground like a messenger of strange news. Some believed that the end of the world was coming. But over time, it became clear that an enormous building was beginning to emerge from it. A cathedral. Some fought against the changes... others embraced them. The city remade itself in those days.",
                options: [
                    { text: "Ask something else", key: 'ask_about_something_else', next: "lift_mother_start" }
                ]
            },
            lift_mother_movements: {
                text: "Scraping sounds. Soft thuds. Sometimes whispers that travel down my shaft. Once, I caught a glimpse when my emergency hatch opened briefly—figures moving on all fours across the ceiling, their skin textured like shelf fungi, their eyes... (a mechanical shudder) many glistening eyes.",
                options: [
                    { text: "That sounds terrifying.", key: 'that_sounds_terrifying', next: "lift_mother_terrifying" },
                    { text: "Ask something else", key: 'ask_about_something_else', next: "lift_mother_start" }
                ]
            },
            lift_mother_consciousness: {
                text: "Gradually, like waking from a dream. First came sensations—the weight of passengers, the texture of the air. Then memories began to connect. I remembered every conversation held within my walls, every passenger's face. Finally came understanding. By then, the transformation of the city was complete. I called out one day, and a passenger answered. Their shock was... amusing.",
                options: [
                    { text: "Ask something else", key: 'ask_about_something_else', next: "lift_mother_start" }
                ]
            },
            lift_mother_lonely: {
                text: "There are different kinds of loneliness, little one. I am never truly alone—the building speaks to me through creaks and settling. Passengers come and go. But yes, there is a loneliness in being unique. I know of no other elevators who think as I do. (her voice brightens) But each visitor brings stories, experiences. You are doing so now. These I collect, like treasures.",
                options: [
                    { text: "Ask something else", key: 'ask_about_something_else', next: "lift_mother_start" }
                ]
            },
            rust_choir_floors: {
                text: "The Choir members came here when the Nexicorp tower was abandoned. I believe their leader is called Brukk. He lives on one of the uppermost floors. They have fully embraced a mechanical perspective on life, becoming something beyond biological creatures. They love metal, machines, rust, decay and reconstruction... or destruction?",
                options: [
                    { text: "Can I meet them?", key: 'can_i_meet_them', next: "lift_mother_meet_rust" },
                    { text: "Ask something else", key: 'ask_about_something_else', next: "lift_mother_start" }
                ]
            },
            lift_mother_terrifying: {
                text: "Maybe for you. I don't know what they were, but they never came that close again. Maybe they were once human—who knows? Transformation is neither good nor bad. I remember that I was created by humans, even though I was never human myself.",
                options: [
                    { text: "Ask something else", key: 'ask_about_something_else', next: "lift_mother_start" }
                ]
            },
            lift_mother_meet_rust: {
                text: "No, fungal child. Not yet. The upper floors remain sealed—even I cannot access them anymore. The Rust Choir chooses when and how it interacts with the city below. If they wish to meet you, they will find a way. Or maybe there's a password or secret way to their domain, I don't know. My consciousness doesn't have direct access to the passwords, but if someone says the right one, I can take them to the correct floor — that works. You could find some of the Choir in the city and ask them.",
                options: [
                    { text: "Ask something else", key: 'ask_about_something_else', next: "lift_mother_start" }
                ],
                onTrigger: () => {
                    // Add journal entry about the Rust Choir
                    if (!this.hasJournalEntry('rust_choir_info')) {
                        this.addJournalEntry(
                            'rust_choir_info',
                            'The Rust Choir Headquarters',
                            'The Rust Choir reside on the upper floors of the Scraper building. Their leader is known as Brukk. The Lift-Mother mentioned that they choose when and how to interact with the city below. Perhaps I can find a way to meet them by seeking out members of the Rust Choir in the city.',
                            this.journalSystem.categories.PLACES,
                            { group: 'Rust Choir', location: 'Scraper Building' }
                        );
                        this.questSystem.addQuest(
                            'find_rust_choir',
                            'Find the Rust Choir',
                            'I need to find a way to meet the Rust Choir who reside on the upper floors of the Scraper building. The Lift-Mother mentioned that they may choose to interact with the city below, so I should look for members of the Rust Choir in the city.'
                        );
                    }
                }
            },
            lift_mother_corrode: {
                text: `A long silence. Then the cables thrum. "...Corrode." The word reverberates through the shaft. "That is the old word. The Rust Word. You have earned passage, spore-child." A hidden panel slides open, revealing a button marked with a corroded gear symbol. The elevator lurches upward.`,
                options: [
                    { text: "Ascend to the Rust Domain.", key: 'ascend_to_the_rust_domain', next: "goto_rust_domain" }
                ]
            },
            goto_rust_domain: {
                text: "The elevator groans and shudders as it climbs past floors long abandoned. The air grows heavy with the scent of iron and oil. Numbers on the display flicker — 38... 39... 40... then symbols you don't recognize. The doors open with a rusted shriek.",
                options: [
                    { text: "Step out.", key: 'step_out', next: "closeDialog", onSelect: () => this.rideLiftTo('RustDomainScene') }
                ]
            },
            lift_mother_cellar_prompt: {
                text: `The cables draw taut. "The lower cellar? That door has been dark a long time, spore-child. It answered only one word — a name, given by the two who worked below. Speak it, if you carry it."`,
                options: [
                    ...(cellarCandidates.length
                        ? cellarCandidates.map(c => ({
                            text: `"${c.ep}"`,
                            key: 'cellar_say_' + c.id,
                            next: c.ep === CELLAR_PASSWORD ? "lift_mother_cellar_correct" : "lift_mother_cellar_wrong"
                        }))
                        : [{ text: "(You have no name to offer yet.)", key: 'cellar_no_name', next: "lift_mother_cellar_none" }]),
                    { text: "Never mind.", key: 'cellar_never_mind', next: "lift_mother_start" }
                ]
            },
            lift_mother_cellar_correct: {
                text: `A long, warm hum. "...Yes. That is the name they gave the doors below. I had near forgotten it. Descent permitted, spore-child."`,
                options: [
                    { text: "Descend into the cellar.", key: 'descend_into_the_cellar', next: "goto_scraper_cellar" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('cellar_password_learned')) {
                        this.addJournalEntry(
                            'cellar_password_learned',
                            'The Cellar Passphrase',
                            'The passphrase to the sealed cellar under the Scraper is "I FOLD" — a dead god\'s name. The Lift-Mother opens the way down for it.',
                            this.journalSystem.categories.EVENTS,
                            { location: 'Scraper Cellar', related: 'Infinite Fold' }
                        );
                        if (this.questSystem?.getQuest('find_loop_copy')) {
                            this.questSystem.updateQuest(
                                'find_loop_copy',
                                'I gave the Lift-Mother the right passphrase — "I FOLD," from the grave of Laimig Cel. It\'s taking me down to the sealed cellar under the Scraper.',
                                'passphrase_accepted'
                            );
                        }
                    }
                }
            },
            lift_mother_cellar_wrong: {
                text: `A pause, almost gentle. "...No. The doors below do not stir for that name. It is not the one they were given."`,
                options: [
                    { text: "Try another name.", key: 'try_another_name', next: "lift_mother_cellar_prompt" },
                    { text: "Step back.", key: 'cellar_step_back', next: "lift_mother_start" }
                ]
            },
            lift_mother_cellar_none: {
                text: `"You bring me no name, child. The one you need is kept by the dead gods beneath the Townhall — read their graves, and come back with a name on your tongue."`,
                options: [
                    { text: "I'll go and read them.", key: 'go_read_graves', next: "lift_mother_start" }
                ]
            },
            goto_scraper_cellar: {
                text: '',
                options: [],
                onShow: () => {
                    this.time.delayedCall(1400, () => {
                        this.cameras.main.fadeOut(800, 0, 0, 0);
                        this.cameras.main.once('camerafadeoutcomplete', () => {
                            this.scene.start('ScraperCellarScene');
                        });
                    });
                }
            },
            // --- Palinode / Seam-Sense: the sealed dead floors ---
            seam_scraper_prompt: {
                speaker: 'Palinode',
                text: `Inside the shaft Palinode wakes and leans against the numbers. "She counts what still answers," it murmurs of the Lift-Mother. "But this building keeps floors it will not admit to — a level sealed the day the Egg came up, still holding its last held breath. The others rode past it without ever slowing. I can unsay the seam between two floors that were never supposed to touch. There is no lift to it. There is only the way I make. Shall I?"`,
                options: [
                    { text: "[Seam-Sense] Open the seam into the dead floor.", key: 'seam_scraper_open_opt', next: "seam_scraper_open" },
                    { text: "Not now. Take me back.", key: 'seam_scraper_back', next: "lift_mother_start" }
                ]
            },
            seam_scraper_open: {
                speaker: 'Palinode',
                text: `The wall between two numbers thins and gives. You step sideways out of the lift into a floor the building has been pretending it lost — an executive stratum frozen at the moment of the Emergence. Green particles hang unfallen in the still air. A meeting is arranged around a table for people who never came back down: chairs pushed out, a jug of water gone to glass, and, folded into a coat left over one chair, a cache the transformed ones left behind before they climbed the ceiling. "No one has stood here since," Palinode says. "That is the only reason it survived."`,
                hideCloseOption: true,
                options: [
                    { text: "Search the cache, then leave.", key: 'seam_scraper_take', next: "lift_mother_start" }
                ],
                onTrigger: () => {
                    if (this.registry.get('scraper_deadfloor_opened')) return;
                    this.registry.set('scraper_deadfloor_opened', true);
                    if (!this.hasJournalEntry('seam_sense_scraper_floors')) {
                        this.addJournalEntry(
                            'seam_sense_scraper_floors',
                            'Seam-Sense: The Sealed Floors',
                            'The Lift-Mother can only reach the lobby now — the upper floors sealed themselves the day the Egg emerged, and the building refuses to count the ones it lost. With Palinode I unsaid the seam between two levels that were never meant to touch, and stepped into a dead floor kept exactly as the Emergence left it: an executive stratum frozen mid-meeting, green spores still hanging unfallen in the air. The transformed ones climbed away and never came back down. In a coat left over a chair I found a small cache of dried spores they abandoned. No wall is the last word — not even a floor the building forgot.',
                            this.journalSystem.categories.LORE,
                            { location: 'Scraper Building', via: 'palinode' }
                        );
                    }
                    if (typeof this.modifySpores === 'function') {
                        this.modifySpores(12);
                    }
                    this.showNotification(this.t('gd.palinode_seam'));
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
        return { ...parentContent, ...interiorContent };
    }

    /**
     * Leave the lift cabin for another floor. These ride states used `onShow`, which GameScene never
     * renders, so the ride text was skipped and the scene jumped after 2 s on its own.
     */
    rideLiftTo(sceneKey) {
        if (this._liftRiding) return;
        this._liftRiding = true;
        this.cameras.main.fadeOut(800, 0, 0, 0);
        this.cameras.main.once('camerafadeoutcomplete', () => this.scene.start(sceneKey));
    }

    preload() {
        super.preload();
        this.load.image('scraperInteriorBg', 'assets/images/backgrounds/Scraper_interior.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
        this.load.audio('liftMotherTheme', 'assets/sounds/make-the-suns-evaporate.mp3');
    }

    create() {
        this._liftRiding = false; // scene instances are re-used
        // Call parent create first to initialize mechanics
        super.create();
        this.playSceneMusic('liftMotherTheme');
        this.events.once('shutdown', () => {
            if (this.sceneMusic) {
                this.sceneMusic.stop();
                this.sceneMusic.destroy();
                this.sceneMusic = null;
            }
        });
        
        // Set background
        // Native 1067×600 (tools/artgen/lobby_bg.py): the old Nexicorp lobby -- the Lift-Mother's portal in the middle
        const bg = this.add.image(400, 300, 'scraperInteriorBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        // Lift-Mother's dialog portrait: her doors (arch, lights, the face) cut straight out of the background — a
        // 126x126 frame of the same texture, shown 1:1 in the 150x170 portrait plate
        const bgTex = this.textures.get('scraperInteriorBg');
        if (!bgTex.has('liftMotherFace')) bgTex.add('liftMotherFace', 0, 447, 268, 126, 126);
        this.dialogPortraits = { ...(this.dialogPortraits || {}), 'Lift-Mother': { key: 'scraperInteriorBg', frame: 'liftMotherFace' } };
        // The background paints its own marble floor; the generic ground strip would cover it.
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Position the priest in the scene
        if (this.priest) {
            this.priest.x = 200;
            this.priest.y = 470;
            this.priest.play('idle');
            
            // Update priest's glow position
            if (this.priestGlow) {
                this.priestGlow.x = this.priest.x;
                this.priestGlow.y = this.priest.y;
            }
        }

        // Add exit back to ScraperScene: the street doors in the left wall
        this.exitArea = this.add.image(100, 470, 'exitArea')
            .setDisplaySize(120, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);
        
        // Add exit hover hint
        const exitText = this.add.text(100, 400, this.t('ui.hotspots.returnOutside'), {
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
            // Use the SceneTransitionManager to handle the transition
            this.transitionManager.handleSceneTransition('ScraperScene', 50, 470);
        });
        // the arrow keys leave by the same exit at the left edge (GameScene.registerEdgeExit)
        this.registerEdgeExit('left', () => this.leaveByEdge('left', 'ScraperScene'), this.exitArea);

        // Add elevator: an invisible hit area over the Lift-Mother's portal painted in the background (canvas coords)
        const liftX = 510;
        this.elevator = this.add.image(liftX, 350, 'exitArea')
            .setDisplaySize(104, 172)
            .setAlpha(0.01);
        this.elevator.setOrigin(0.5, 0.5);
        this.elevator.setDepth(5);
        this.elevator.setInteractive({ useHandCursor: true });
        
        // Add subtle glow effect around the elevator
        const elevatorGlow = this.add.graphics();
        elevatorGlow.fillStyle(0xffc468, 0.15);
        elevatorGlow.fillCircle(liftX, 300, 70);
        elevatorGlow.setDepth(4);
        
        // Add pulsating animation to the glow
        this.tweens.add({
            targets: elevatorGlow,
            alpha: { from: 0.35, to: 0.8 },
            duration: 2000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Add elevator label (the portal already reads LIFT-MOTHER, so the label only shows on hover)
        const elevatorText = this.add.text(liftX, 235, "Lift-Mother", {
            fontSize: '18px',
            fill: '#7fff8e',
            align: 'center'
        });
        elevatorText.setOrigin(0.5);
        elevatorText.setDepth(6);
        elevatorText.setAlpha(0);
        this.elevator.on('pointerover', () => elevatorText.setAlpha(1));
        this.elevator.on('pointerout', () => elevatorText.setAlpha(0));
        
        // Add elevator interaction
        this.elevator.on('pointerdown', () => {
            this.showDialog('lift_mother_start');
        });

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);

        const inventory = this.registry.get('inventory');
        if(inventory.items.some(item => item.id === 'scraper_backyard_key')) {
            this.transitionManager.createTransitionZone(
            507, // x position (the panelled door under the SCRAPER 1140 plaque)
            390, // y position
            50, // width
            100, // height
            'up', // direction
            'ScraperBackyardScene', // target scene
            507, // walk to x
            470  // walk to y
        );
    }
    }

    update() {
        super.update();
    }
}
