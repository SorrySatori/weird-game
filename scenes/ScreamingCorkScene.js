import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import LanguageSystem from '../systems/LanguageSystem.js';
import JournalSystem from '../systems/JournalSystem.js';
import { composeBook, edgarReaction, newBookSeed, bookRoles, render } from '../utils/EdgarBook.js';

export default class ScreamingCorkScene extends GameScene {
    constructor() {
        super({ key: 'ScreamingCorkScene' });

        // Get instance of the journal system
        this.journalSystem = JournalSystem.getInstance();
        this.isTransitioning = false;

        // Edgar's book: the draft (seed + picks) lives in the registry ('edgarBookDraft'), see bookDraft
        this.currentTopic = null;
    }

    // Helper method to check if player has journal entry related to specific experiences
    hasJournalExperience(entryId) {
        return this.journalSystem.getEntry(entryId);
    }
    
    // Helper method for compatibility with dialog system
    hasJournalEntry(entryId) {
        return this.journalSystem.getEntry(entryId);
    }

    /** Edgar's book in progress (registry + saves): { seed, topics[], tone, genre, protagonist, setting }. */
    get bookDraft() {
        return this.registry.get('edgarBookDraft') || { seed: 0, topics: [] };
    }

    setBookPick(kind, value) {
        this.registry.set('edgarBookDraft', { ...this.bookDraft, [kind]: value });
    }

    /** Open the book quest with a fresh seeded draft (no-op if it's already running). Returns true if new. */
    startEdgarBook() {
        if (this.questSystem.getQuest('edgar_book')) return false;
        // its own seed: the same picks write a different book next playthrough
        this.registry.set('edgarBookDraft', { seed: newBookSeed(), topics: [] });
        this.questSystem.addQuest(
            'edgar_book',
            'Help Edgar to write a book',
            'Edgar Eskola mentioned he wants to write a book. I should help him.'
        );
        return true;
    }

    /** The draft the finished book was made from (kept in the journal), or the one in progress. */
    get bookDraftUsed() {
        return this.getJournalEntry('edgar_book_completed')?.metadata?.book_draft || this.bookDraft;
    }

    /** The finished book in `lang` (utils/EdgarBook.js); reviews only from people the player has met. */
    composeEdgarBook(lang) {
        return composeBook(this.bookDraftUsed, lang, id => !!this.hasJournalEntry(id));
    }

    // Helper method to get available inspirational topics based on journal entries
    getAvailableTopics() {
        const topics = [];
        // Get already selected topic IDs for filtering
        const selectedTopicIds = this.bookDraft.topics || [];

        // Check for various journal entries that could serve as inspiration
        if (this.hasJournalExperience('scraper_sighting') && !selectedTopicIds.includes('scraper_building')) {
            topics.push({
                id: 'scraper_building',
                text: "The mysterious Scraper building",
                description: "A building that seems to shift and change, with floors that rearrange themselves"
            });
        }

        if (this.hasJournalExperience('lift_mother_meeting') && !selectedTopicIds.includes('lift_mother')) {
            topics.push({
                id: 'lift_mother',
                text: "The sentient elevator Lift-Mother",
                description: "An ancient, conscious elevator that remembers the city's history"
            });
        }

        if (this.hasJournalExperience('ortolan_meeting') && !selectedTopicIds.includes('ortolan')) {
            topics.push({
                id: 'ortolan',
                text: "Ortolan, the board game designer",
                description: "A character who creates complex games and seeks more arms for playtesting"
            });
        }

        if (this.hasJournalExperience('dream_queue') && !selectedTopicIds.includes('dream_queue')) {
            topics.push({
                id: 'dream_queue',
                text: "The Dream Queue",
                description: "A mysterious place where people's dreams are processed and stored"
            });
        }

        if (this.hasJournalExperience('spore_infection') && !selectedTopicIds.includes('spore_infection')) {
            topics.push({
                id: 'spore_infection',
                text: "The fungal spore infection",
                description: "The strange spores that infect people and change them"
            });
        }

        if (this.hasJournalExperience('vestigel_quest') && !selectedTopicIds.includes('vestigels')) {
            topics.push({
                id: 'vestigels',
                text: "The mysterious vestigels",
                description: "Ancient artifacts with unknown powers that you're collecting"
            });
        }

        if (this.hasJournalExperience('kloor_venn_meeting') && !selectedTopicIds.includes('kloor_venn')) {
            topics.push({
                id: 'kloor_venn',
                text: "The enigmatic Kloor Venn",
                description: "A character who speaks in riddles and seems to exist in multiple places at once"
            });
        }

        if (this.hasJournalExperience('skyship_sighting') && !selectedTopicIds.includes('skyships')) {
            topics.push({
                id: 'skyships',
                text: "The skyships above the city",
                description: "Massive vessels that drift through the clouds for reasons unknown"
            });
        }

        if (this.hasJournalExperience('rust_choir') && !selectedTopicIds.includes('rust_choir')) {
            topics.push({
                id: 'rust_choir',
                text: "The mysterious Rust Choir",
                description: "A faction that communicates through the vibrations of rusting metal"
            });
        }

        if (this.hasJournalExperience('burning_bear_festival') && !selectedTopicIds.includes('burning_bear')) {
            topics.push({
                id: 'burning_bear',
                text: "The Burning Bear Festival",
                description: "A controversial festival with deep meaning for Edgar"
            });
        }

        if (this.hasJournalExperience('board_games_war') && !selectedTopicIds.includes('board_games_war')) {
            topics.push({
                id: 'board_games_war',
                text: "The Board Game Wars",
                description: "An ancient conflict where Ludarchs — game designers who could rewrite reality — destroyed entire cities as pawns in their games"
            });
        }

        if (this.hasJournalExperience('noise_god_insight') && !selectedTopicIds.includes('noise_god')) {
            topics.push({
                id: 'noise_god',
                text: "The Noise God",
                description: "A forgotten deity that came to die in Upper Morkezela, whose presence still pulses through broken amplifiers and magnetic dust"
            });
        }

        if (this.hasJournalExperience('magnekin_reveal') && !selectedTopicIds.includes('magnekin')) {
            topics.push({
                id: 'magnekin',
                text: "Magnekin — A Civilization in One Body",
                description: "A collective of tiny cities held together by magnetic forces, disguised as a single humanoid citizen"
            });
        }

        if (this.hasJournalExperience('phor_calesta') && !selectedTopicIds.includes('god_graveyard')) {
            topics.push({
                id: 'god_graveyard',
                text: "The God Graveyard beneath the city",
                description: "Layers of fossilized dead gods lying beneath Upper Morkezela, their prayers turned to strata and halos crystallized into mineral deposits"
            });
        }

        // Always provide some default topics even if the player hasn't journaled much
        if (topics.length < 2) {
            // Only add default topics if they haven't been selected yet
            if (!selectedTopicIds.includes('city_mystery')) {
                topics.push({
                    id: 'city_mystery',
                    text: "The mysteries of Upper Morkezela",
                    description: "The strange city with its fungal growth and unusual inhabitants"
                });
            }

            if (!selectedTopicIds.includes('misutken_life')) {
                topics.push({
                    id: 'misutken_life',
                    text: "Life as a mišutkenn in the city",
                    description: "The challenges and perspectives of being different in Upper Morkezela"
                });
            }
        }

        return topics;
    }

    get dialogContent() {
        // QuestSystem tracks completion as `isComplete` (there is no `status` field).
        const bookDone = !!this.questSystem.getQuest('edgar_book')?.isComplete;
        const onceFlags = this.registry.get('onceFlags') || [];
        const farewellDone = onceFlags.includes('edgar_book_farewell');
        // the city's first reactions only exist once the manuscript has had time to go around (a later visit)
        const reviewsHeard = onceFlags.includes('edgar_book_reviews');
        // Finishing the book while the Vestigel hunt is open hands the token over in the farewell.
        // Computed here (the getter runs at show time) — assigning into `this.dialogContent.x.text`
        // from an onTrigger is lost, because every getter call builds a fresh object.
        const farewellGivesVestigel = !farewellDone && !!this.questSystem.getQuest('the_three_vestigels') && !this.hasItem('vestigel');
        const cs = LanguageSystem.getInstance?.().getLanguage?.() === 'cs';
        const lang = cs ? 'cs' : 'en';
        // Edgar's book (utils/EdgarBook.js): reactions read the draft, the payoff states the finished book.
        const draft = this.bookDraft;
        // (books finished before the generator have no stored draft: no excerpts to re-read for them)
        const used = this.bookDraftUsed;
        const book = (used.tone && used.genre && used.protagonist && used.setting) ? this.composeEdgarBook(lang) : null;
        const bookCast = book ? bookRoles(this.bookDraftUsed) : null;

        return {
            ...super.dialogContent, // Include parent dialog content for symbiont dialogs

            // Edgar Eskola dialog
            speaker: 'Edgar Eskola',
            edgar_start: {
        
                text: "The ursine creature shifts uncomfortably. He glances at you with a mix of wariness and curiosity.",
                options: [
                    { text: "Hello there.", key: 'hello_there', next: "edgar_greeting" },
                    { text: "What are you doing here?", key: 'what_are_you_doing_here', next: "edgar_purpose" },
                    { text: "Tell me about yourself.", key: 'tell_me_about_yourself', next: "edgar_background" },
                    { text: "What do you know about the Burning Bear Festival?", key: 'what_do_you_know_about_the_burning_bear_festival', next: "edgar_festival" },
                    // Dynamically add vestigel option if player has the quest
                    ...(this.questSystem.getQuest('the_three_vestigels') ? [
                        { text: "I'm looking for a vestigel, I heard you might have one.", key: 'im_looking_for_a_vestigel_i_heard_you_might_have_o', next: "edgar_vestigel" }
                    ] : []),
                    // Only show book topics option if quest is active but not completed
                    ...(this.questSystem.getQuest('edgar_book') && !this.questSystem.getQuest('edgar_book').isComplete ? [
                        { text: "Let's start with some inspirational topics.", key: 'lets_start_with_some_inspirational_topics', next: "edgar_book_topics" }
                    ] : []),
                    ...(bookDone && book && farewellDone && !reviewsHeard ? [
                        { text: "So, how's the novel?", key: 'how_is_the_novel', next: "edgar_book_news" }
                    ] : []),
                    ...(bookDone && book ? [
                        { text: "Read me something from your book.", key: 'read_me_from_your_book', next: "edgar_book_reread" }
                    ] : []),
                    // Before the finale: Edgar's overlooked-places perspective on the Egg Cathedral
                    ...(this.hasJournalEntry('met_infinite_fold') ? [
                        { text: "[Before entering the cathedral] You've worked everywhere in this city. Is there a way into the Egg Cathedral nobody talks about?", key: 'edgar_cathedral_ask', next: "edgar_cathedral_way" }
                    ] : []),
                ],
                onTrigger: () => {
                    // Add journal entry about meeting Edgar Eskola
                    if (!this.hasJournalExperience('edgar_eskola_meeting')) {
                        this.addJournalEntry(
                            'edgar_eskola_meeting',
                            'Edgar Eskola of the Screaming Cork',
                            'I met Edgar Eskola, a bear-like patron at the Screaming Cork.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Edgar Eskola', location: 'Screaming Cork' }
                        );
                    }
                }
            },
            edgar_greeting: {
        
                text: "Mmm. Hello. Not often people choose to speak with me. Most avoid mišutkenn if they can help it.",
                options: [
                    { text: "Why is that?", key: 'why_is_that', next: "edgar_prejudice" },
                    { text: "What are mišutkenn?", key: 'what_are_miutkenn', next: "edgar_what" },
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ],
                onTrigger: () => {
                    this.addJournalFact('edgar_eskola_meeting', 'misutkenn', "He is a mišutkenn — and, he says, most people avoid his kind if they can help it.");
                }
            },
            edgar_what: {
        
                text: "Mišutkenn are... well, we're not exactly human. We're... different.",
                options: [
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(1, 0); // the G/D system announces the change itself
                }
            },
            edgar_prejudice: {
                text: "History. Superstition. Fear of what's different. Take your pick. The founders of this city drove my ancestors from the Remaper Hills. Now we're just... tolerated. At best.",
                options: [
                    { text: "That's unfortunate.", key: 'thats_unfortunate', next: "edgar_unfortunate" },
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ],
                onTrigger: () => {
                    this.addJournalFact('edgar_eskola_meeting', 'exiled', "The city's founders drove his ancestors from the Remaper Hills; his kind are tolerated here, at best.");
                }
            },
            edgar_unfortunate: {
        
                text: "That's one way to put it. But I've learned to live with it. Mostly.",
                options: [
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_purpose: {
                text: "Waiting. Watching. Avoiding the preparations for that cursed festival. The Screaming Cork is one of the few places that doesn't go all-in on the bear burning nonsense.",
                options: [
                    { text: "You don't like the festival?", key: 'you_dont_like_the_festival', next: "edgar_festival" },
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_background: {
        
                text: "Not much to tell. I've had more jobs than I can count. Janitor at 1140 Scraper, professional imaginator, clerk, art model, airship mechanic, meat packer... None of them stuck. Not entirely my fault, though.",
                options: [
                    { text: "Professional imaginator?", key: 'professional_imaginator', next: "edgar_imaginator" },
                    { text: "Why didn't they work out?", key: 'why_didnt_they_work_out', next: "edgar_jobs" },
                    { text: "What would you like to do?", key: 'what_would_you_like_to_do', next: "edgar_dream_job" },
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_dream_job: {
        
                text: "I've tried everything. Janitor. Clerk. Meat assembler. Imaginator. But I've never been anything truly mine. I think… I want to write a book. But I don't know what it's about yet.",
                options: [
                    ...(!this.questSystem.getQuest('edgar_book') ? [
                        { text: "I can help you write the book", key: 'i_can_help_you_write_the_book', next: "edgar_book" }
                    ] : []),
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ],
                onTrigger: () => {
                    // Add journal entry about Edgar's aspiration
                    if (!this.hasJournalExperience('edgar_aspiration')) {
                        this.addJournalEntry(
                            'edgar_aspiration',
                            'Edgar\'s Literary Aspirations',
                            'Edgar Eskola, the bearish mišutkenn from the Screaming Cork, expressed his desire to write a book. Despite having worked many jobs in the city, he feels he hasn\'t found his true calling. Writing could be his chance to create something truly his own.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Edgar Eskola', location: 'Screaming Cork' }
                        );
                    }
                }
            },
            edgar_book: {
                text: "You would... do that for me? Thank you. I don't know what it's about yet. But I'm open to suggestions.",
                options: [
                    { text: "Let's start with some inspirational topics", key: 'lets_start_with_some_inspirational_topics', next: "edgar_book_topics" },
                    { text: "I will come back when I have an idea", key: 'i_will_come_back_when_i_have_an_idea', next: "edgar_start" }
                ],
                onTrigger: () => {
                    if (this.startEdgarBook()) {
                        // Add journal entry about agreeing to help with the book
                        this.addJournalEntry(
                            'edgar_book_quest_start',
                            'A Promise to a Writer',
                            'I offered to help Edgar Eskola write his book. He seems genuinely touched by the gesture, though neither of us have a clear idea of what the book should be about yet. My experiences in this strange city might provide some inspiration.',
                            this.journalSystem.categories.EVENTS,
                            {
                                character: 'Edgar Eskola',
                                location: 'Screaming Cork',
                                quest: 'edgar_book'
                            }
                        );
                    }
                }
            },

            // Topic selection: the player's own experiences walk into the book as side characters
            edgar_book_topics: {
                text: "What inspires you about this city? What experiences might make a good story? I've been stuck in the same routines for so long, I need fresh perspectives.",
                // `key: topic.id` lets the cs file translate the labels; the pick is parked in `currentTopic`
                options: this.getAvailableTopics().map(topic => ({
                    text: topic.text,
                    key: topic.id,
                    next: "edgar_book_topic_selected",
                    onSelect: () => { this.currentTopic = topic; }
                })),
            },

            edgar_book_topic_selected: {
                // Edgar already sees the topic as a character (utils/EdgarBook.js CAMEOS)
                text: (this.currentTopic && edgarReaction('topic', draft, lang, this.currentTopic.id))
                    || (cs ? "To je fascinující téma! Hned mě napadá pár zajímavých věcí." : "That's a fascinating topic! It gives me some interesting ideas to work with."),
                // A function: resolved after onTrigger has recorded the pick. Up to three topics, fewer if
                // the player has no more experiences to offer (that used to leave the quest stuck).
                options: function() {
                    const enough = this.bookDraft.topics.length >= 3 || this.getAvailableTopics().length === 0;
                    return [enough
                        ? { text: "I think we have enough topics", key: 'i_think_we_have_enough_topics', next: "edgar_book_tone" }
                        : { text: "Let's continue", key: 'lets_continue', next: "edgar_book_topics" }];
                },
                hideCloseOption: true,
                onTrigger: () => {
                    const topic = this.currentTopic;
                    if (topic && !this.bookDraft.topics.includes(topic.id)) {
                        this.setBookPick('topics', [...this.bookDraft.topics, topic.id]);
                    }
                    this.currentTopic = null;
                }
            },

            edgar_book_tone: {
                text: "Now that we have some topics to work with, what tone should the book have? I'm thinking about the emotional feel of it.",
                hideCloseOption: true,
                options: [
                    { text: "Tragic — a tale of sorrow and loss", key: 'tragic_a_tale_of_sorrow_and_loss', next: "edgar_book_tone_selected", onSelect: () => this.setBookPick('tone', 'tragic') },
                    { text: "Metaphysical — exploring nature of reality", key: 'metaphysical_exploring_consciousness', next: "edgar_book_tone_selected", onSelect: () => this.setBookPick('tone', 'metaphysical') },
                    { text: "Romantic — focusing on connections", key: 'romantic_focusing_on_connections', next: "edgar_book_tone_selected", onSelect: () => this.setBookPick('tone', 'romantic') },
                    { text: "Existential — pondering meaning of life and mortality", key: 'existential_pondering_meaning_and_mortality', next: "edgar_book_tone_selected", onSelect: () => this.setBookPick('tone', 'existential') },
                    { text: "Political — examining power dynamics", key: 'political_examining_power_dynamics', next: "edgar_book_tone_selected", onSelect: () => this.setBookPick('tone', 'political') },
                    { text: "Comical — finding humor in the strange", key: 'comical_finding_humor_in_the_strange', next: "edgar_book_tone_selected", onSelect: () => this.setBookPick('tone', 'comical') }
                ]
            },
            edgar_book_tone_selected: {
                hideCloseOption: true,
                text: edgarReaction('tone', draft, lang) || "That's a wonderful choice!",
                options: [
                    { text: "Now let's choose a genre for the book", key: 'now_lets_choose_a_genre_for_the_book', next: "edgar_book_genre" }
                ]
            },

            edgar_book_genre: {
                hideCloseOption: true,
                text: "The tone is set, but what genre should this story be? I've been exploring some experimental options.",
                options: [
                    { text: "Fungal techno-thriller", key: 'fungal_technothriller', next: "edgar_book_genre_selected", onSelect: () => this.setBookPick('genre', 'fungal techno') },
                    { text: "Postmodern novel", key: 'postmodern_novel', next: "edgar_book_genre_selected", onSelect: () => this.setBookPick('genre', 'postmodern') },
                    { text: "Urban fantasy", key: 'urban_fantasy', next: "edgar_book_genre_selected", onSelect: () => this.setBookPick('genre', 'urban fantasy') },
                    { text: "Funny animals with depression", key: 'funny_animals_with_depression', next: "edgar_book_genre_selected", onSelect: () => this.setBookPick('genre', 'funny animals') },
                    { text: "Detective novel", key: 'detective_novel', next: "edgar_book_genre_selected", onSelect: () => this.setBookPick('genre', 'detective') },
                    { text: "Dreamy weird fiction", key: 'dreamy_weird_fiction', next: "edgar_book_genre_selected", onSelect: () => this.setBookPick('genre', 'weird fiction') },
                    { text: "Mythic war epic", key: 'mythic_war_epic', next: "edgar_book_genre_selected", onSelect: () => this.setBookPick('genre', 'mythic war epic') },
                    { text: "Cosmic horror", key: 'cosmic_horror', next: "edgar_book_genre_selected", onSelect: () => this.setBookPick('genre', 'cosmic horror') }
                ]
            },
            edgar_book_genre_selected: {
                hideCloseOption: true,
                // the genre bends the cast: Edgar names the villain that tone + genre call for
                text: edgarReaction('genre', draft, lang) || "Perfect genre!",
                options: [
                    { text: "Let's decide on the main protagonist", key: 'lets_decide_on_the_main_protagonist', next: "edgar_book_protagonist" }
                ]
            },

            edgar_book_protagonist: {
                hideCloseOption: true,
                text: "Who should the main character be? What kind of protagonist would fit this story?",
                options: [
                    { text: "A disoriented tourist", key: 'a_disoriented_tourist', next: "edgar_book_protagonist_selected", onSelect: () => this.setBookPick('protagonist', 'disoriented tourist') },
                    { text: "A renegade fungal scientist", key: 'a_renegade_fungal_scientist', next: "edgar_book_protagonist_selected", onSelect: () => this.setBookPick('protagonist', 'bad scientist') },
                    { text: "A mišutkenn seeking identity", key: 'a_miutkenn_seeking_identity', next: "edgar_book_protagonist_selected", onSelect: () => this.setBookPick('protagonist', 'mišutkenn') },
                    { text: "An amnesiac with strange abilities", key: 'an_amnesiac_with_strange_abilities', next: "edgar_book_protagonist_selected", onSelect: () => this.setBookPick('protagonist', 'strange amnesiac') },
                    { text: "A sentient fungal colony", key: 'a_sentient_fungal_colony', next: "edgar_book_protagonist_selected", onSelect: () => this.setBookPick('protagonist', 'fungal colony') },
                    { text: "A dream detective", key: 'a_dream_detective', next: "edgar_book_protagonist_selected", onSelect: () => this.setBookPick('protagonist', 'dream detective') },
                    { text: "A rogue Ludarch", key: 'a_rogue_ludarch', next: "edgar_book_protagonist_selected", onSelect: () => this.setBookPick('protagonist', 'rogue Ludarch') },
                    { text: "A living collective pretending to be one person", key: 'a_living_collective_pretending_to_be_one_person', next: "edgar_book_protagonist_selected", onSelect: () => this.setBookPick('protagonist', 'living collective') },
                ]
            },
            edgar_book_protagonist_selected: {
                hideCloseOption: true,
                text: edgarReaction('protagonist', draft, lang) || "A fascinating choice!",
                options: [
                    { text: "Finally, let's choose a setting", key: 'finally_lets_choose_a_setting', next: "edgar_book_setting" }
                ]
            },

            edgar_book_setting: {
                hideCloseOption: true,
                text: "And finally, where should this story take place? What's the setting?",
                options: [
                    { text: "The Scraper's shifting floors", key: 'the_scrapers_shifting_floors', next: "edgar_book_setting_selected", onSelect: () => this.setBookPick('setting', 'scraper') },
                    { text: "A murderous magical school", key: 'a_murderous_magical_school', next: "edgar_book_setting_selected", onSelect: () => this.setBookPick('setting', 'magical school') },
                    { text: "A giant immortal mammal, swimming in the ocean", key: 'a_giant_immortal_mammal_swimming_in_the_ocean', next: "edgar_book_setting_selected", onSelect: () => this.setBookPick('setting', 'immortal mammal') },
                    { text: "The fungal wilds", key: 'the_fungal_wilds', next: "edgar_book_setting_selected", onSelect: () => this.setBookPick('setting', 'fungal wilds') },
                    { text: "A skyship above the clouds", key: 'a_skyship_above_the_clouds', next: "edgar_book_setting_selected", onSelect: () => this.setBookPick('setting', 'skyship') },
                    { text: "The subterranean markets", key: 'the_subterranean_markets', next: "edgar_book_setting_selected", onSelect: () => this.setBookPick('setting', 'markets') },
                    { text: "A war-torn board game that became real", key: 'a_wartorn_board_game_that_became_real', next: "edgar_book_setting_selected", onSelect: () => this.setBookPick('setting', 'living board game') },
                    { text: "The graveyard of dead gods", key: 'the_graveyard_of_dead_gods', next: "edgar_book_setting_selected", onSelect: () => this.setBookPick('setting', 'god graveyard') }
                ]
            },
            edgar_book_setting_selected: {
                hideCloseOption: true,
                text: edgarReaction('setting', draft, lang) || "What an excellent setting!",
                options: [
                    { text: "Let's see what book we've created", key: 'lets_see_what_book_weve_created', next: "edgar_book_completion" }
                ]
            },

            // The finished book: title + back cover, then excerpts and reviews. All built from the
            // seeded draft and localized here — the cs file only translates the options.
            edgar_book_completion: {
                hideCloseOption: !farewellDone,
                text: book ? (cs
                    ? `*Edgar se dlouze zahledí do prázdna a pak plácne tlapou do stolu.* Mám to.\n\n„${book.fullTitle}“\n\n${book.blurb}`
                    : `*Edgar stares into the middle distance for a long moment, then slaps a paw on the table.* I have it.\n\n"${book.fullTitle}"\n\n${book.blurb}`) : '',
                options: [
                    { text: "Read me the opening.", key: 'read_the_opening', next: "edgar_book_excerpt_opening" },
                    { text: "Make sure to credit me as co-author", key: 'make_sure_to_credit_me_as_coauthor', next: "edgar_book_coauthor" }
                ],
                onTrigger: () => {
                    if (this.questSystem.getQuest('edgar_book')?.isComplete) return;
                    const en = this.composeEdgarBook('en');
                    const czech = this.composeEdgarBook('cs');
                    const shown = cs ? czech : en;
                    this.questSystem.updateQuest('edgar_book', "I helped Edgar Eskola come up with his book. He's already writing.", 'completed');
                    this.questSystem.completeQuest('edgar_book');
                    // Built at runtime from the picks, so localized here (lang/*/journal.js can't template).
                    this.addJournalEntry(
                        'edgar_book_completed',
                        cs ? `Edgarova kniha: „${shown.title}“` : `Edgar's Book: "${shown.title}"`,
                        cs
                            ? `Pomohl jsem Edgaru Eskolovi vymyslet knihu „${shown.fullTitle}“. ${shown.blurb}`
                            : `I helped Edgar Eskola come up with his book, "${shown.fullTitle}". ${shown.blurb}`,
                        this.journalSystem.categories.EVENTS,
                        {
                            character: 'Edgar Eskola',
                            location: 'Screaming Cork',
                            quest: 'edgar_book',
                            quest_status: 'completed',
                            // The exact book, so later scenes (the Day-1 nightlife cutscene, re-reading)
                            // rebuild the same text: utils/EdgarBook.js composeBook(book_draft, lang).
                            book_draft: { ...this.bookDraft },
                            book_title: en.title,        // EN — the nightlife cutscene captions are English
                            book_title_cs: czech.title,
                            book_genre: this.bookDraft.genre,
                            book_tone: this.bookDraft.tone,
                            book_protagonist: this.bookDraft.protagonist,
                            book_setting: this.bookDraft.setting
                        }
                    );
                }
            },
            edgar_book_coauthor: {
                hideCloseOption: !farewellDone,
                text: bookCast ? render(cs
                    ? '*Udělá si poznámku.* „Spoluautor.“ Dobře. Budete v poděkování, hned za {K.i}.'
                    : '*He makes a note.* "Co-author." Right. You’ll be in the acknowledgements, right after {K}.', bookCast, lang) : '',
                options: [
                    { text: "Read me the opening.", key: 'read_the_opening', next: "edgar_book_excerpt_opening" }
                ]
            },
            edgar_book_excerpt_opening: {
                hideCloseOption: !farewellDone,
                text: book ? `${cs ? '*Odkašle si.*' : '*He clears his throat.*'}\n\n${book.excerpts.opening}` : '',
                options: [
                    { text: "And then?", key: 'and_then', next: "edgar_book_excerpt_middle" }
                ]
            },
            edgar_book_excerpt_middle: {
                hideCloseOption: !farewellDone,
                text: book ? `${cs ? '*Listuje stránkami, které ještě neexistují.*' : '*He leafs through pages that don’t exist yet.*'}\n\n${book.excerpts.middle}` : '',
                options: [
                    { text: "How does it end?", key: 'how_does_it_end', next: "edgar_book_excerpt_ending" }
                ]
            },
            edgar_book_excerpt_ending: {
                hideCloseOption: !farewellDone,
                // the author's thank-you (third topic) is part of the book, so it closes the reading
                text: book ? `${cs ? '*Ztiší hlas.*' : '*He lowers his voice.*'}\n\n${book.excerpts.ending}${book.thanks ? '\n\n' + book.thanks : ''}` : '',
                options: farewellDone
                    ? [{ text: "Thanks, Edgar.", key: 'thanks_edgar_book', next: "edgar_start" }]
                    : [{ text: "I look forward to reading it", key: 'i_look_forward_to_reading_it', next: "edgar_book_farewell" }]
            },
            // A later visit: the manuscript has been going around the city, the first reactions are in
            edgar_book_news: {
                text: book ? `${cs
                    ? '*Edgarovi cuknou uši něčím nebezpečně blízkým hrdosti.* Koluje to. Půjčil jsem rukopis jednomu člověku a teď ho má přečtený půlka města – na přeskáčku a s fleky od kávy. Už mám první reakce:'
                    : '*Edgar\'s ears twitch with something dangerously close to pride.* It\'s going around. I lent the manuscript to one person, and now half the city has read it — out of order, with coffee stains. The first reactions are in:'}\n\n${book.critics.join('\n')}` : '',
                options: [
                    { text: "Congratulations, Edgar.", key: 'congratulations_edgar', next: "edgar_start" },
                    { text: "Read me something from it again.", key: 'read_me_from_your_book', next: "edgar_book_reread" }
                ],
                onTrigger: () => { this.onceEver('edgar_book_reviews', () => {}); }
            },
            // Later visits: any part of the finished book again
            edgar_book_reread: {
                text: book ? (cs
                    ? `„${book.fullTitle}“ *Edgar se tváří nesmírně spokojeně.* Kterou část?`
                    : `"${book.fullTitle}" *Edgar looks enormously pleased with himself.* Which part?`) : '',
                options: [
                    { text: "The opening.", key: 'read_opening_again', next: "edgar_book_excerpt_opening" },
                    { text: "The middle.", key: 'read_middle_again', next: "edgar_book_excerpt_middle" },
                    { text: "The ending.", key: 'read_ending_again', next: "edgar_book_excerpt_ending" },
                    ...(reviewsHeard ? [{ text: "What are people saying about it?", key: 'read_reviews_again', next: "edgar_book_news" }] : []),
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },

            edgar_book_farewell: {
                textKey: farewellGivesVestigel ? 'vestigel' : 'plain',
                text: farewellGivesVestigel
                    ? "I should get to work now. The ideas are flowing, and I don't want to lose them. Oh, and as promised, here's the vestigel. It's of more use to you than to me. Thank you again for your help. Feel free to check in on my progress sometime."
                    : "I should get to work now. The ideas are flowing, and I don't want to lose them. Thank you again for your help. Feel free to check in on my progress sometime.",
                options: [
                    { text: "Good luck, Edgar", key: 'good_luck_edgar', next: "closeDialog" }
                ],
                onTrigger: () => {
                    // once: re-reading the book later must not hand out another vestigel
                    this.onceEver('edgar_book_farewell', () => {
                        
                        // Check if the player has the vestigel quest and doesn't already have the vestigel
                        if (this.questSystem.getQuest('the_three_vestigels') && !this.hasItem('vestigel')) {
                            
                            // Create the vestigel item
                            const vestigelItem = {
                                id: 'vestigel',
                                name: 'Writer\'s Vestigel',
                                description: 'A small, intricately carved token that Edgar found hidden inside a plush toy. It seems to have some mysterious significance.',
                                icon: 'vestigel',
                                usable: false,
                                consumable: false,
                                value: 0
                            };
                            
                            // Add the vestigel to inventory
                            this.addItemToInventory(vestigelItem);
                            
                            // Update quest progress
                            this.questSystem.updateQuest('the_three_vestigels', 'Received a vestigel from Edgar Eskola in exchange for helping with his book.', 'edgar_vestigel_acquired');
                            
                            // Add journal entry about receiving the vestigel
                            this.addJournalEntry(
                                'edgar_vestigel_received',
                                'The Writer\'s Token',
                                'Today I acquired one of the three vestigels from Edgar Eskola at the Screaming Cork. He gave it to me in exchange for my help with writing his book. The vestigel had been hidden inside a plush toy that Edgar had bought from a street vendor. He mentioned that the vendor refused to take it back when offered, citing "professional honor." The vestigel itself is small but intricately carved, clearly valuable to someone who knows its purpose.',
                                this.journalSystem.categories.EVENTS,
                                {
                                    character: 'Edgar Eskola',
                                    location: 'Screaming Cork',
                                    item: 'Vestigel',
                                    quest: 'the_three_vestigels',
                                    importance: 'high'
                                }
                            );
                        }
                    });
                }
            },

            edgar_imaginator: {
        
                text: "I dreamed up locations and characters for Dr. Elphi Quarn's games. Turns out my imagination was too... wild. Too erratic, they said. My dreams were 'unusable.' Their loss.",
                options: [
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_jobs: {
        
                text: "Bad timing, mostly. The Scraper took the Rust Choir and stopped being an official part of the city — no need for a janitor then. The other jobs... Well, being a mišutkenn doesn't help with job security in this city.",
                options: [
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_festival: {
        
                text: "The Burning Bear Festival? A cruel reminder of an ancient 'victory' over my kind. They stuff bear skins with things they want to be rid of, then burn them at midnight. Some fill them with pests, bad habits, vices... others with rivals, if the rumors are true.",
                options: [
                    { text: "That sounds disturbing.", key: 'that_sounds_disturbing', next: "edgar_disturbing" },
                    { text: "It's just tradition, isn't it?", key: 'its_just_tradition_isnt_it', next: "edgar_tradition" },
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_disturbing: {
                text: "It is. Imagine being surrounded by burning effigies that look like your ancestors. The city lights up with fires of different colors and smells, while I hide away, waiting for it to end.",
                options: [
                    { text: "I'm sorry to hear that.", key: 'im_sorry_to_hear_that', next: "edgar_sympathy" },
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_tradition: {
        
                text: "Tradition? Traditions can be cruel. Just because something has been done for generations doesn't make it right. But few in this city would agree with me.",
                options: [
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_sympathy: {
        
                text: "Your sympathy is... unexpected. But appreciated. Perhaps not everyone in this city is as thoughtless as I've come to believe.",
                options: [
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(1, 0); // the G/D system announces the change itself
                }
            },

            // New vestigel dialog path
            edgar_vestigel: {
        
                text: "A vestigel? Yes... I do have one. It's a peculiar object, a small, but apparently valuable token. It was hidden inside a plush toy. See, I rather bought it from a street vendor, when I saw it. Otherwise somebody would use it for that cursed festival. The vendor didn't know about the Vestigel, but she surprisingly refused to take it back, when I offered it to her. She said something about a professional honor, hmm...",
                options: [
                    // Use ternary to determine next dialog based on book quest completion status
                    { text: "I need it for an important purpose.", key: 'i_need_it_for_an_important_purpose', next: bookDone ? "edgar_vestigel_give_completed" : "edgar_vestigel_need" },
                    { text: "May I have it?", key: 'may_i_have_it', next: bookDone ? "edgar_vestigel_give_completed" : "edgar_vestigel_request" },
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_vestigel_need: {
        
                text: "Important purpose, you say? Well, I don't really *need* it, but I kinda like it. Maybe you could do something for me in exchange?",
                options: [
                    { text: "What do you need?", key: 'what_do_you_need', next: "edgar_vestigel_convince" },
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_vestigel_request: {
        
                text: "Just like that? You know that's a valuable trinket. I wouldn't give it away without good reason.",
                options: [
                    { text: "What would convince you to part with it?", key: 'what_would_convince_you_to_part_with_it', next: "edgar_vestigel_convince" },
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_vestigel_convince: {
        
                text: "Hmm...",
                options: [
                    // Determine which option to show based on book quest status
                    ...(bookDone ? [
                        { text: "I already helped you write your book.", key: 'i_already_helped_you_write_your_book', next: "edgar_vestigel_give_completed" }
                    ] : this.questSystem.getQuest('edgar_book') ? [
                        { text: "I could help with your book, as we discussed earlier.", key: 'i_could_help_with_your_book_as_we_discussed_earlie', next: "edgar_vestigel_book_help" }
                    ] : [
                        { text: "Maybe I could help you with something.", key: 'maybe_i_could_help_you_with_something', next: "edgar_vestigel_offer" }
                    ]),
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_vestigel_offer: {
                text: "Hmm... maybe you could help me with something. Do you know something about literature? I would like to become... a writer. But I don't know where to start. Would you help me with that? I've been struggling to find a voice, a story worth telling. If you could truly help me...",
                options: [
                    { text: "I'll do my best.", key: 'ill_do_my_best', next: "edgar_vestigel_thanks" }
                ],
                onTrigger: () => {
                    this.startEdgarBook();

                    // Add journal entry about the vestigel negotiation
                    this.addJournalEntry(
                        'edgar_vestigel_negotiation',
                        'A Deal with Edgar',
                        'Edgar Eskola agreed to trade his vestigel in exchange for help with writing his book. The vestigel seems valuable to him, but his desire to become an author is stronger. This arrangement could benefit us both - he gets his book, and I get the vestigel I need.',
                        this.journalSystem.categories.EVENTS,
                        {
                            character: 'Edgar Eskola',
                            location: 'Screaming Cork',
                            item: 'Vestigel',
                            quest: 'the_three_vestigels'
                        }
                    );
                }
            },
            edgar_vestigel_book_help: {
                text: "Yes, you did offer to help with my book. A fair exchange — your help for the vestigel. I've been collecting ideas but haven't made much progress.",
                options: [
                    { text: "I'll make sure your book becomes a reality.", key: 'ill_make_sure_your_book_becomes_a_reality', next: "edgar_vestigel_thanks" }
                ]
            },
            
            // New dialog for when player asks for vestigel after book is completed
            edgar_vestigel_give_completed: {
        
                text: "Oh, you're interested in the vestigel? After all your help with my book, I'd be happy to give it to you. It's of more use to you than to me. Here, take it with my gratitude.",
                options: [
                    { text: "Thank you, Edgar.", key: 'thank_you_edgar', next: "edgar_start" }
                ],
                onTrigger: () => {
                    // Only give vestigel if player doesn't already have it
                    if (!this.hasItem('vestigel')) {
                        // Create the vestigel item
                        const vestigelItem = {
                            id: 'vestigel',
                            name: 'Writer\'s Vestigel',
                            description: 'A small, intricately carved token that Edgar found hidden inside a plush toy. It seems to have some mysterious significance.',
                            icon: 'vestigel',
                            usable: false,
                            consumable: false,
                            value: 0
                        };
                        
                        // Add the vestigel to inventory
                        this.addItemToInventory(vestigelItem);
                        
                        // Update quest progress
                        this.questSystem.updateQuest('the_three_vestigels', 'Received a vestigel from Edgar Eskola after helping with his book.', 'edgar_vestigel_acquired');
                        
                        // Add journal entry about receiving the vestigel
                        this.addJournalEntry(
                            'edgar_vestigel_received_after_book',
                            'The Writer\'s Token',
                            'Today I acquired one of the three vestigels from Edgar Eskola at the Screaming Cork. He gave it to me as thanks for helping him write his book. The vestigel had been hidden inside a plush toy that Edgar had bought from a street vendor. He mentioned that the vendor refused to take it back when offered, citing "professional honor." The vestigel itself is small but intricately carved, clearly valuable to someone who knows its purpose.',
                            this.journalSystem.categories.EVENTS,
                            {
                                character: 'Edgar Eskola',
                                location: 'Screaming Cork',
                                item: 'Vestigel',
                                quest: 'the_three_vestigels',
                                importance: 'high'
                            }
                        );
                    }
                }
            },
            edgar_vestigel_thanks: {
        
                text: "Remember your promise. I look forward to seeing what we can create together. A book that truly captures the essence of... well, that's what we need to discover.",
                options: [
                    ...(this.questSystem.getQuest('edgar_book') && !this.questSystem.getQuest('edgar_book').isComplete ? [
                        { text: "Let's start right away, with some inspirational topics.", key: 'lets_start_right_away', next: "edgar_book_topics" }
                    ] : []),
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(1, 0);

                    // Only update the quest state if we haven't already received the vestigel
                    if (!this.hasItem('vestigel')) {
                        this.questSystem.updateQuest('the_three_vestigels', 'Edgar Eskola would trade the Vestigel for your help with his book.', 'edgar_book_trade');
                        
                        // Add journal entry about Edgar's agreement
                        this.addJournalEntry(
                            'edgar_vestigel_agreement',
                            'The Vestigel Bargain',
                            'Edgar agreed to give me his vestigel once I help him write his book. He seems particularly excited about the prospect of becoming an author. The way his eyes lit up when discussing the project suggests this means more to him than just a simple trade - it represents a chance to leave his mark on the city that has so often marginalized him.',
                            this.journalSystem.categories.EVENTS,
                            {
                                character: 'Edgar Eskola',
                                location: 'Screaming Cork',
                                item: 'Vestigel',
                                quests: ['the_three_vestigels', 'edgar_book'],
                                importance: 'high'
                            }
                        );
                    }
                }
            },

            // Before the finale: Edgar's secret way into the Egg Cathedral
            edgar_cathedral_way: {
                text: "The ursine creature goes very still — the way animals do when they hear something potentially dangerous. \"The Egg Cathedral… Yes. I've thought about that place more than most have.\" He lowers his voice. \"I swept its corridors. Oiled its lift-cages. Carried out its ash. Nobody watches the one who carries out the ash. And I learned a thing the priests never did: everyone was using the main entrance. The great doors. The Sentinel. I always looked for the hidden places. Some nights, the walls breathe.\"",
                options: [
                    { text: "The walls breathe?", key: 'the_walls_breathe', next: "edgar_cathedral_breathe" },
                    { text: "Then show me the way in.", key: 'then_show_me_the_way_in', next: "edgar_cathedral_path" },
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ]
            },
            edgar_cathedral_breathe: {
                text: "\"They're breathing. In and out, slowly, as if something were sleeping there. Everyone thinks the cathedral's cellars are just a dead, empty space where nothing exists. But I don't think they're dead. There's something down there. Honestly, I stopped working there because I got scared. I have no idea if those corridors have changed in any way since then — you'll have to see for yourself.\"",
                options: [
                    { text: "So there is a way in.", key: 'so_there_is_a_way_in', next: "edgar_cathedral_path" },
                    { text: "Ask something else", key: 'back_to_other_topics', next: "edgar_start" }
                ],
                onTrigger: () => {
                    this.addJournalFact('edgar_cathedral_path', 'cellars', "He says the cellars everyone takes for dead space are not dead: something is down there. He stopped working there because it frightened him, and he doesn't know how the corridors have changed since.");
                }
            },
            edgar_cathedral_path: {
                text: "\"There is. On the north side, where the cathedral wall meets the dead gods strata, there is a spot where the ground is constantly shifting, creating a narrow passage. A gap the width of a bear's shoulders, if you don't mind the smell of the underneath. You'd better go right away. Whatever's waking in there won't leave a gap open for long.\" He hesitates, one great paw flat on the table. \"Be careful. I've always thought of myself as someone who notices things that no one else notices. I wouldn't want to be the last person to see you alive.\"",
                options: [
                    { text: "Thank you, Edgar.", key: 'thank_you_edgar_cathedral', next: "edgar_start" },
                    { text: "I should go.", key: 'i_should_go', next: "closeDialog" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('edgar_cathedral_path')) {
                        this.addJournalEntry(
                            'edgar_cathedral_path',
                            'Edgar\'s Secret Way',
                            'Edgar Eskola — who spent years as a janitor in the Egg Cathedral, sweeping its corridors and carrying out its ash — told me of a way inside that ignores the great doors and the Sentinel entirely. On the north side, where the cathedral wall meets the dead-god strata, the ground is constantly shifting and has opened a narrow passage — a gap the width of a bear\'s shoulders. Some nights, he says, the walls breathe. "Everyone was using the main entrance," he said. "I always looked for the hidden places."',
                            this.journalSystem.categories.PLACES,
                            { character: 'Edgar Eskola', location: 'Egg Cathedral' }
                        );
                    }
                }
            }
        };
    }

    preload() {
        super.preload();
        this.load.image('screamingCorkBg', 'assets/images/backgrounds/ScreamingCork.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        // Edgar: an 8-frame idle sheet, 128×192 (tools/artgen/edgar.py from the old EdgarEskola.png, Aseprite Edgar_eskola)
        this.load.spritesheet('edgarEskola', 'assets/images/characters/edgar_eskola.png', { frameWidth: 128, frameHeight: 192 });
        this.load.image('vestigel', 'assets/images/items/vestigel.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();

        // Set background
        const bg = this.add.image(400, 300, 'screamingCorkBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        // The background paints its own pavement; drop the generic ground strip
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }

        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);

        // Position the priest at the right side when entering from ScraperScene
        this.priest.x = 700;
        this.priest.y = 470;

        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);

        // Create exit to ScraperScene at the left edge
        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            80, // width
            200, // height
            'left', // direction
            'BurningBearStreetScene', // target scene
            50, // walk to x
            470 // walk to y
        );

        // Create entrance to the tavern interior (centered on the tavern door)
        this.transitionManager.createTransitionZone(
            400, // x position - centered on the door
            470, // y position
            100, // width
            200, // height
            'up', // direction
            'ScreamingCorkInteriorScene', // target scene
            100, // walk to x - position inside the tavern
            470 // walk to y
        );

        // Add a hint about the tavern entrance
        const doorX = this.scale.width / 2;
        const doorHint = this.add.text(doorX, 380, this.t('ui.hints.enterTavern'), {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        doorHint.setOrigin(0.5);
        doorHint.setAlpha(0);
        doorHint.setDepth(10);

        // Show hint when hovering near the door
        this.input.on('pointermove', (pointer) => {
            // Check if pointer is near the door area
            if (Math.abs(pointer.x - doorX) < 50 && Math.abs(pointer.y - 470) < 100) {
                doorHint.setAlpha(1);
            } else {
                doorHint.setAlpha(0);
            }
        });

        // Add Edgar Eskola NPC
        this.createEdgarEskola();

        // Examine: the tavern & the beat under its floorboards (sign/building, upper-center).
        this.createObservable(400, 235, 260, 130, () => {
            if (this.hasJournalEntry('noise_god_insight') || this.hasJournalEntry('feral_toast_performance')) return this.t('observe.screaming_cork.knows_noise');
            return this.t('observe.screaming_cork.default');
        }, { hint: this.t('observe.screaming_cork.hint') });
    }

    update() {
        super.update();
    }

    createEdgarEskola() {
        // Edgar stands on the pavement left of the door, in front of the bench; soles 3 px above the frame's bottom
        this.edgar = this.add.sprite(300, 525, 'edgarEskola', 0);
        this.edgar.setOrigin(0.5, 1);
        this.edgar.setDepth(6);
        this.addGroundShadow(300, 520, 70, 14);
        if (!this.anims.exists('edgar_idle')) {
            // breath, a blink, an ear twitch, the bag swaying, a grumble with the head down -- slow
            this.anims.create({
                key: 'edgar_idle',
                frames: this.anims.generateFrameNumbers('edgarEskola', { frames: [0, 0, 1, 1, 0, 0, 2, 0, 0, 1, 1, 0, 3, 0, 0, 4, 0, 5, 0, 0, 1, 1, 0, 0, 6, 7, 7, 6, 0, 0, 1, 1, 0, 2, 0, 0] }),
                frameRate: 4,
                repeat: -1
            });
        }
        this.edgar.play('edgar_idle');
        this.dialogPortraits = { ...(this.dialogPortraits || {}),
            'Edgar Eskola': { key: 'edgarEskola', frame: 0, zoom: 2, top: 24 } };
        this.edgar.setInteractive({ useHandCursor: true });

        // Add dialog interaction
        this.edgar.on('pointerdown', () => {
            if (this.dialogVisible) return;
            this.showDialog('edgar_start');
        });
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.ScreamingCorkScene = ScreamingCorkScene;
}
