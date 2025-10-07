import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';

export default class ScreamingCorkScene extends GameScene {
    constructor() {
        super({ key: 'ScreamingCorkScene' });

        // Get instance of the journal system
        this.journalSystem = JournalSystem.getInstance();
        this.isTransitioning = false;

        // Initialize book properties
        this.bookTopics = [];
        this.bookTone = '';
        this.bookGenre = '';
        this.bookProtagonist = '';
        this.bookSetting = '';
        this.maxTopics = 3; // Maximum number of inspirational topics
    }

    // Helper method to check if player has journal entry related to specific experiences
    hasJournalExperience(entryId) {
        return this.journalSystem.getEntry(entryId);
    }
    
    // Helper method for compatibility with dialog system
    hasJournalEntry(entryId) {
        return this.journalSystem.getEntry(entryId);
    }

    // Helper method to get available inspirational topics based on journal entries
    getAvailableTopics() {
        const topics = [];
        // Get already selected topic IDs for filtering
        const selectedTopicIds = this.bookTopics ? this.bookTopics.map(topic => topic.id) : [];

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

    // Helper method to format the book title based on selections
    generateBookTitle() {
        // Generate different title formats based on genre
        let title = '';

        switch (this.bookGenre) {
            case 'fungal_techno':
                if (this.bookTone === 'tragic') {
                    title = `The Last ${this.bookProtagonist.split(' ')[0]} of ${this.bookSetting.split(' ').slice(0, 2).join(' ')}`;
                } else if (this.bookTone === 'metaphysical') {
                    title = `${this.bookSetting.split(' ')[0]} Recursions`;
                } else if (this.bookTone === 'romantic') {
                    title = `Love Among the ${this.bookSetting.split(' ').slice(-2).join(' ')}`;
                } else if (this.bookTone === 'existential') {
                    title = `The ${this.bookProtagonist.split(' ')[0]}'s Dilemma`;
                } else if (this.bookTone === 'political') {
                    title = `Revolution in the ${this.bookSetting.split(' ').slice(-1)[0]}`;
                } else { // comical
                    title = `The Ridiculous Adventures of a ${this.bookProtagonist.split(' ')[0]} in ${this.bookSetting.split(' ').slice(0, 2).join(' ')}`;
                }
                break;

            case 'postmodern':
                if (this.bookTone === 'existential' || this.bookTone === 'metaphysical') {
                    title = `${this.bookSetting.split(' ')[0]}, ${this.bookSetting.split(' ')[1]}, ${this.bookProtagonist.split(' ')[0]}`;
                } 
                if (this.bookTone === 'tragic') {
                    title = `The Making of ${this.bookProtagonist.split(' ')[0]} from ${this.bookSetting.split(' ').slice(0, 2).join(' ')}`;
                }
                else {
                    title = `The ${this.bookProtagonist.split(' ')[0]} Variations`;
                }
                break;

            case 'urban_fantasy':
                if (this.bookTone === 'political') { title = `The ${this.bookProtagonist.split(' ')[0]} of ${this.bookSetting.split(' ')[0]} Street`;
                } 
                else if (this.bookTone === 'metaphysical') {
                    title = `The Tale of ${this.bookProtagonist}'travels to ${this.bookSetting.split(' ')[0]}`;
                }
                
                else {
                    title = `The ${this.bookProtagonist.split(' ')[0]} of ${this.bookSetting.split(' ').slice(0, 2).join(' ')}`;
                }
                break;

            case 'funny_animals':
                if(this.bookTone === 'political') title = `${this.bookProtagonist.split(' ')[0]}'s Guide to ${this.bookTone.charAt(0).toUpperCase() + this.bookTone.slice(1)} Living`;
                else if (this.bookTone === 'existential') title = `The ${this.bookProtagonist.split(' ')[0]} Who Thought Too Much`;
                else if (this.bookTone === 'tragic') title = `The Sad Tale of ${this.bookProtagonist.split(' ')[0]} who Wished to be a Zookeeper`;
                else title = `Crazy Cats in ${this.bookSetting.split(' ')[0]}`;
                break;

            case 'detective':
                if(this.bookTone === 'metaphysical') title = `The ${this.bookSetting.split(' ')[0]} ${this.bookSetting.split(' ')[1] || ''} Mystery`;
                if(this.bookTone === 'tragic') title = `The Sad ${this.bookProtagonist.split(' ')[0]} Case`;
                if(this.bookTone === 'comical') title = `The Hilarious ${this.bookProtagonist.split(' ')[0]} and the ${this.bookSetting.split(' ')[0]} ${this.bookSetting.split(' ')[1] || ''} Murder`;
                else title = `The Case of the ${this.bookSetting.split(' ')[0]} ${this.bookSetting.split(' ')[1] || ''}`;
                break;

            case 'weird_fiction':
                if(this.bookTone === 'comical') title = `Making fun of ${this.bookProtagonist.split(' ')[0]} Dreams of ${this.bookSetting.split(' ')[0]}`;
                if(this.bookTone === 'tragic') title = `The ${this.bookProtagonist.split(' ')[0]} Who Cried Fungi`;
                if(this.bookTone === 'existential') title = `The ${this.bookProtagonist.split(' ')[0]} and the ${this.bookSetting.split(' ')[0]} Paradox`;
                else title = `The ${this.bookProtagonist.split(' ')[0]} in the ${this.bookSetting.split(' ')[0]} Labyrinth`;
                break;
        }

        return title;
    }

    get dialogContent() {
        return {
            ...super.dialogContent, // Include parent dialog content for symbiont dialogs

            // Edgar Eskola dialog
            speaker: 'Edgar Eskola',
            edgar_start: {
        
                text: "The ursine creature shifts uncomfortably. He glances at you with a mix of wariness and curiosity.",
                options: [
                    { text: "Hello there.", next: "edgar_greeting" },
                    { text: "What are you doing here?", next: "edgar_purpose" },
                    { text: "Tell me about yourself.", next: "edgar_background" },
                    { text: "What do you know about the Burning Bear Festival?", next: "edgar_festival" },
                    // Dynamically add vestigel option if player has the quest
                    ...(this.questSystem.getQuest('the_three_vestigels') ? [
                        { text: "I'm looking for a vestigel, I heard you might have one.", next: "edgar_vestigel" }
                    ] : []),
                    // Only show book topics option if quest is active but not completed
                    ...(this.registry.get('questSystem')?.getQuest('edgar_book') && 
                       this.registry.get('questSystem')?.getQuest('edgar_book').status !== 'completed' ? [
                        { text: "Let's start with some inspirational topics", next: "edgar_book_topics" }
                    ] : []),
                    { text: "Goodbye.", next: "closeDialog" }
                ],
                onTrigger: () => {
                    // Add journal entry about meeting Edgar Eskola
                    if (!this.hasJournalExperience('edgar_eskola_meeting')) {
                        this.addJournalEntry(
                            'edgar_eskola_meeting',
                            'Edgar Eskola - The Mišutkenn of Screaming Cork',
                            'I met Edgar Eskola, a mišutkenn patron at the Screaming Cork tavern. He seems uncomfortable around humans, which is understandable given the history of prejudice against his kind in Upper Morkezela. Despite his bearish appearance, there\'s a softness to him - an intellectual quality that suggests he\'s more than the city\'s stereotypes would imply.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Edgar Eskola', location: 'Screaming Cork' }
                        );
                    }
                }
            },
            edgar_greeting: {
        
                text: "Mmm. Hello," + "Not often people choose to speak with me. Most avoid mišutkenn if they can help it.",
                options: [
                    { text: "Why is that?", next: "edgar_prejudice" },
                    { text: "What are mišutkenn?", next: "edgar_what" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_what: {
        
                text: "Mišutkenn are... well, we're not exactly human. Or anything else, for that matter. We're... different.",
                options: [
                    { text: "Back to other topics", next: "edgar_start" }
                ],
                onTrigger: () => {
                    this.showNotification('Growth increased');
                    this.modifyGrowthDecay(1, 0);
                }
            },
            edgar_prejudice: {
                text: "History. Superstition. Fear of what's different. Take your pick. The founders of this city drove my ancestors from the Remaper Hills. Now we're just... tolerated. At best.",
                options: [
                    { text: "That's unfortunate.", next: "edgar_unfortunate" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_unfortunate: {
        
                text: "That's one way to put it. But I've learned to live with it. Mostly.",
                options: [
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_purpose: {
                text: "Waiting. Watching. Avoiding the preparations for that cursed festival. The Screaming Cork is one of the few places that doesn't go all-in on the bear burning nonsense.",
                options: [
                    { text: "You don't like the festival?", next: "edgar_festival" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_background: {
        
                text: "Not much to tell. I've had more jobs than I can count. Janitor at 1140 Scraper, professional imaginator, clerk, art model, airship mechanic, meat packer... None of them stuck. Not entirely my fault, though.",
                options: [
                    { text: "Professional imaginator?", next: "edgar_imaginator" },
                    { text: "Why didn't they work out?", next: "edgar_jobs" },
                    { text: "What would you like to do?", next: "edgar_dream_job" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_dream_job: {
        
                text: "I've tried everything. Janitor. Clerk. Meat assembler. Imaginator. But I've never been anything truly mine. I think… I want to write a book. But I don't know what it's about yet.",
                options: [
                    ...(!this.questSystem.getQuest('edgar_book') ? [
                        { text: "I can help you write the book", next: "edgar_book" }
                    ] : []),
                    { text: "Back to other topics", next: "edgar_start" }
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
                    { text: "Let's start with some inspirational topics", next: "edgar_book_topics" },
                    { text: "I will come back when I have an idea", next: "edgar_start" }
                ],
                onTrigger: () => {
                    if (!this.questSystem.getQuest('edgar_book')) {
                        this.questSystem.addQuest(
                            'edgar_book',
                            'Help Edgar to write a book',
                            'Edgar Eskola mentioned he wants to write a book. I should help him.'
                        );

                        // Add journal entry about agreeing to help with the book
                        this.addJournalEntry(
                            'edgar_book_quest_start',
                            'A Promise to a Writer',
                            'I offered to help Edgar Eskola write his book. He seems genuinely touched by the gesture, though neither of us have a clear idea of what the book should be about yet. My experiences in this strange city might provide inspiration for his story.',
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

            // Topic selection dialog - lets player choose inspirational topics
            edgar_book_topics: {
                text: "What inspires you about this city? What experiences might make a good story? I've been stuck in the same routines for so long, I need fresh perspectives.",
                options: this.getAvailableTopics().map(function(topic) {
                    return {
                        text: topic.text,
                        next: "edgar_book_topic_selected",
                        onSelect: function() {
                            this.bookTopics.push(topic);
                        }
                    };
                }),
                onTrigger: () => {
                    console.log('edgar_book_topics', this.bookTopics);
                }
            },

            // Topic selected dialog - adds the selected topic and returns to topic selection
            edgar_book_topic_selected: {
                text: "That's a fascinating topic! It gives me some interesting ideas to work with.",
                // Instead of spreading conditionally in the declaration, we'll set this in a function
                options: function() {
                    const options = [
                        { text: "Let's continue", next: "edgar_book_topics" }
                    ];
                    
                    if (this.bookTopics && this.bookTopics.length >= 3) {
                        options.push({ text: "I think I have enough topics", next: "edgar_book_tone" });
                    }
                    
                    return options;
                },
                onTrigger: () => {
                    // Add the selected topic to our list
                    if (this.currentTopic) {
                        this.bookTopics.push(this.currentTopic);

                        // Add journal entry about suggesting this topic
                        this.addJournalEntry(
                            `edgar_book_topic_${this.currentTopic.id}`,
                            `Book Inspiration: ${this.currentTopic.text}`,
                            `I suggested ${this.currentTopic.text} as inspiration for Edgar's book. ${this.currentTopic.description}. Edgar seemed intrigued by the concept and jotted down some notes.`,
                            this.journalSystem.categories.EVENTS,
                            {
                                character: 'Edgar Eskola',
                                location: 'Screaming Cork',
                                quest: 'edgar_book'
                            }
                        );

                        this.currentTopic = null;
                    }
                }
            },

            // Tone selection dialog - choose emotional tone for the book
            edgar_book_tone: {
        
                text: "Now that we have some topics to work with, what tone should the book have? I'm thinking about the emotional feel of it.",
                options: [
                    { text: "Tragic - a tale of sorrow and loss", next: "edgar_book_tone_selected", onSelect: function() { this.bookTone = 'tragic'; } },
                    { text: "Metaphysical - exploring consciousness", next: "edgar_book_tone_selected", onSelect: function() { this.bookTone = 'metaphysical'; } },
                    { text: "Romantic - focusing on connections", next: "edgar_book_tone_selected", onSelect: function() { this.bookTone = 'romantic'; } },
                    { text: "Existential - pondering meaning and mortality", next: "edgar_book_tone_selected", onSelect: function() { this.bookTone = 'existential'; } },
                    { text: "Political - examining power dynamics", next: "edgar_book_tone_selected", onSelect: function() { this.bookTone = 'political'; } },
                    { text: "Comical - finding humor in the strange", next: "edgar_book_tone_selected", onSelect: function() { this.bookTone = 'comical'; } }
                ]
            },

            // Tone selected dialog
            edgar_book_tone_selected: {
                text: "That's a great tone choice! It will give the book a distinct emotional flavor that should resonate with readers.",
                options: [
                    { text: "Now let's choose a genre for the book", next: "edgar_book_genre" }
                ],
                onTrigger: () => {
                    // Add journal entry about the tone selection
                    let toneDescription;
                    switch (this.bookTone) {
                        case 'tragic': toneDescription = 'a somber exploration of loss and sorrow'; break;
                        case 'metaphysical': toneDescription = 'a deep dive into questions of consciousness and reality'; break;
                        case 'romantic': toneDescription = 'a story focused on connection and love'; break;
                        case 'existential': toneDescription = 'a meditation on meaning and mortality'; break;
                        case 'political': toneDescription = 'an examination of power structures and their effects'; break;
                        case 'comical': toneDescription = 'a humorous look at the absurdities of life'; break;
                        default: toneDescription = 'an emotional journey'; break;
                    }

                    this.addJournalEntry(
                        `edgar_book_tone_${this.bookTone}`,
                        `Book Tone: ${this.bookTone.charAt(0).toUpperCase() + this.bookTone.slice(1)}`,
                        `I suggested that Edgar's book should have a ${this.bookTone} tone - ${toneDescription}. He seemed to embrace the idea, considering how it would fit with the inspirations we discussed.`,
                        this.journalSystem.categories.EVENTS,
                        {
                            character: 'Edgar Eskola',
                            location: 'Screaming Cork',
                            quest: 'edgar_book'
                        }
                    );
                }
            },

            // Genre selection dialog - choose genre for the book
            edgar_book_genre: {
        
                text: "The tone is set, but what genre should this story be? I've been exploring some experimental options.",
                options: [
                    { text: "Fungal techno-thriller", next: "edgar_book_genre_selected", onSelect: function() { this.bookGenre = 'fungal_techno'; } },
                    { text: "Postmodern novel", next: "edgar_book_genre_selected", onSelect: function() { this.bookGenre = 'postmodern'; } },
                    { text: "Urban fantasy", next: "edgar_book_genre_selected", onSelect: function() { this.bookGenre = 'urban_fantasy'; } },
                    { text: "Funny animals with depression", next: "edgar_book_genre_selected", onSelect: function() { this.bookGenre = 'funny_animals'; } },
                    { text: "Detective novel", next: "edgar_book_genre_selected", onSelect: function() { this.bookGenre = 'detective'; } },
                    { text: "Dreamy weird fiction", next: "edgar_book_genre_selected", onSelect: function() { this.bookGenre = 'weird_fiction'; } }
                ]
            },

            // Genre selected dialog
            edgar_book_genre_selected: {
                text: "That genre is perfect! It captures exactly the kind of story that would work in this strange city.",
                options: [
                    { text: "Let's decide on the main protagonist", next: "edgar_book_protagonist" }
                ],
                onTrigger: () => {
                    // Add journal entry about the genre selection
                    let genreDescription;
                    switch (this.bookGenre) {
                        case 'fungal_techno': genreDescription = 'combining biotechnology with horror elements'; break;
                        case 'postmodern': genreDescription = 'breaking conventional narrative rules'; break;
                        case 'urban_fantasy': genreDescription = 'bringing magical elements into the city setting'; break;
                        case 'funny_animals': genreDescription = 'using anthropomorphic characters to explore deeper emotions'; break;
                        case 'detective': genreDescription = 'following clues to unravel mysteries'; break;
                        case 'weird_fiction': genreDescription = 'blurring the lines between reality and dreams'; break;
                        default: genreDescription = 'a compelling literary style'; break;
                    }

                    this.addJournalEntry(
                        `edgar_book_genre_${this.bookGenre}`,
                        `Book Genre: ${this.bookGenre.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}`,
                        `I suggested that Edgar write a ${this.bookGenre.replace('_', ' ')} - ${genreDescription}. Edgar seemed to see the potential in using this genre to express his experiences in Upper Morkezela.`,
                        this.journalSystem.categories.EVENTS,
                        {
                            character: 'Edgar Eskola',
                            location: 'Screaming Cork',
                            quest: 'edgar_book'
                        }
                    );
                }
            },

            // Protagonist selection dialog
            edgar_book_protagonist: {
        
                text: "Who should the main character be? What kind of protagonist would fit this story?",
                options: [
                    { text: "A disoriented tourist", next: "edgar_book_protagonist_selected", onSelect: function() { this.bookProtagonist = 'disoriented tourist'; } },
                    { text: "A renegade fungal scientist", next: "edgar_book_protagonist_selected", onSelect: function() { this.bookProtagonist = 'bad scientist'; } },
                    { text: "A mišutkenn seeking identity", next: "edgar_book_protagonist_selected", onSelect: function() { this.bookProtagonist = 'mišutkenn'; } },
                    { text: "An amnesiac with strange abilities", next: "edgar_book_protagonist_selected", onSelect: function() { this.bookProtagonist = 'strange amnesiac'; } },
                    { text: "A sentient fungal colony", next: "edgar_book_protagonist_selected", onSelect: function() { this.bookProtagonist = 'fungal colony'; } },
                    { text: "A dream detective", next: "edgar_book_protagonist_selected", onSelect: function() { this.bookProtagonist = 'dream detective'; } },
                ]
            },

            // Protagonist selected dialog
            edgar_book_protagonist_selected: {
                text: "That's a fascinating protagonist choice! I can already imagine how they would navigate through the story and engage with readers.",
                options: [
                    { text: "Finally, let's choose a setting", next: "edgar_book_setting" }
                ],
                onTrigger: () => {
                    // Add journal entry about the protagonist selection
                    let protagonistDescription;
                    switch (this.bookProtagonist) {
                        case 'tourist': protagonistDescription = 'experiencing the strange city with fresh, confused eyes'; break;
                        case 'scientist': protagonistDescription = 'delving into the mysteries of the city\'s fungal biology'; break;
                        case 'misutkenn': protagonistDescription = 'searching for identity and belonging between worlds'; break;
                        case 'amnesiac': protagonistDescription = 'uncovering their past while wielding unusual abilities'; break;
                        case 'fungal_colony': protagonistDescription = 'a collective consciousness experiencing individuality'; break;
                        case 'detective': protagonistDescription = 'solving mysteries by entering people\'s dreams'; break;
                        default: protagonistDescription = 'navigating the complexities of Upper Morkezela'; break;
                    }

                    this.addJournalEntry(
                        `edgar_book_protagonist_${this.bookProtagonist}`,
                        `Book Protagonist: ${this.bookProtagonist.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}`,
                        `I suggested that the main character of Edgar's book should be a ${this.bookProtagonist.replace('_', ' ')} - ${protagonistDescription}. Edgar seemed excited about developing this character for his story.`,
                        this.journalSystem.categories.EVENTS,
                        {
                            character: 'Edgar Eskola',
                            location: 'Screaming Cork',
                            quest: 'edgar_book'
                        }
                    );
                }
            },

            // Setting selection dialog
            edgar_book_setting: {
                text: "And finally, where should this story take place? What's the setting?",
                options: [
                    { text: "The Scraper's shifting floors", next: "edgar_book_setting_selected", onSelect: function() { this.bookSetting = 'scraper'; } },
                    { text: "A murderous magical school", next: "edgar_book_setting_selected", onSelect: function() { this.bookSetting = 'magical_school'; } },
                    { text: "A giant immortal mammal, swimming in the ocean", next: "edgar_book_setting_selected", onSelect: function() { this.bookSetting = 'immortal_mammal'; } },
                    { text: "The fungal wilds", next: "edgar_book_setting_selected", onSelect: function() { this.bookSetting = 'fungal_wilds'; } },
                    { text: "A skyship above the clouds", next: "edgar_book_setting_selected", onSelect: function() { this.bookSetting = 'skyship'; } },
                    { text: "The subterranean markets", next: "edgar_book_setting_selected", onSelect: function() { this.bookSetting = 'markets'; } }
                ]
            },

            // Setting selected dialog
            edgar_book_setting_selected: {
                text: "What an evocative setting! It creates the perfect atmosphere and provides so many narrative possibilities.",
                options: [
                    { text: "Let's see what book we've created", next: "edgar_book_completion" }
                ],
                onTrigger: () => {
                    // Add journal entry about the setting selection
                    let settingDescription;
                    switch (this.bookSetting) {
                        case 'scraper': settingDescription = 'a mysterious building with floors that rearrange themselves'; break;
                        case 'magical_school': settingDescription = 'the magical school, where kids are dying every year under suspicious circumstances, except the main protagonist, of course'; break;
                        case 'immortal_mammal': settingDescription = 'an enormous creature without a name, swimming eternally in the depths'; break;
                        case 'fungal_wilds': settingDescription = 'the untamed areas where fungal growths take their most primordial forms'; break;
                        case 'skyship': settingDescription = 'a vessel drifting above the clouds, isolated yet connected to the city below'; break;
                        case 'markets': settingDescription = 'the underground commercial spaces where anything can be traded'; break;
                        default: settingDescription = 'a compelling environment for the story'; break;
                    }

                    this.addJournalEntry(
                        `edgar_book_setting_${this.bookSetting}`,
                        `Book Setting: ${this.bookSetting.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}`,
                        `I suggested that Edgar's book should be set in ${this.bookSetting.replace('_', ' ')} - ${settingDescription}. Edgar seemed inspired by this location and how it would interact with the story's other elements.`,
                        this.journalSystem.categories.EVENTS,
                        {
                            character: 'Edgar Eskola',
                            location: 'Screaming Cork',
                            quest: 'edgar_book'
                        }
                    );
                }
            },

            // Final book completion dialog
            edgar_book_completion: {
                // Use a placeholder - the actual title will be replaced in the onTrigger function
                text: `"${this.generateBookTitle()}"... This is perfect! It combines all the elements into something cohesive yet surprising. I can see the whole narrative taking shape already. It will be about ${this.bookProtagonist} and the genre will be ${this.bookGenre}, I like that. Nice touch with the overall ${this.bookTone} book tone. The setting is ${this.bookSetting}, very original. I think we have an ultimate hit in our hands! Thank you, my friend. You've helped me find my voice as a writer. I'll start working on it right away. When it's published, you'll get the first copy, I promise.`,
                options: [
                    { text: "I look forward to reading it", next: "edgar_book_farewell" },
                    { text: "Make sure to credit me as co-author", next: "edgar_book_farewell" }
                ],
                onTrigger: () => {
                    // Generate book title
                    const bookTitle = this.generateBookTitle();
                    
                    // // Replace the dialog text in the game's dialog object
                    // this.dialogContent.edgar_book_completion.text = 
                    //     `"${bookTitle}"... This is perfect! It combines all the elements into something cohesive yet surprising. I can see the whole narrative taking shape already. Thank you, my friend. You've helped me find my voice as a writer. I'll start working on it right away. When it's published, you'll get the first copy, I promise.`;
                    
                    // Update the visible dialog text if it exists
                    // if (this.dialogText) {
                    //     this.dialogText.setText(this.dialogContent.edgar_book_completion.text);
                    // }

                    // Complete the quest
                    this.questSystem.updateQuest('edgar_book', 'You have helped Edgar Eskola develop his book concept. He is very grateful to you.', 'completed');
                    this.questSystem.completeQuest('edgar_book');

                    // Add journal entry about the completed book
                    let topicsText = '';
                    if (this.bookTopics.length > 0) {
                        topicsText = 'Drawing inspiration from ' +
                            this.bookTopics.map(t => t.text.toLowerCase()).join(', ') +
                            ', ';
                    }

                    this.addJournalEntry(
                        'edgar_book_completed',
                        `Edgar's Book: "${bookTitle}"`,
                        `I helped Edgar Eskola develop his book concept. ${topicsText}we created a ${this.bookTone} ${this.bookGenre.replace('_', ' ')} 
                        featuring a ${this.bookProtagonist.replace('_', ' ')} in ${this.bookSetting.replace('_', ' ')}. 
                        Edgar titled it "${bookTitle}" and seemed genuinely inspired to begin writing. 
                        He promised me the first copy when it's published.`,
                        this.journalSystem.categories.EVENTS,
                        {
                            character: 'Edgar Eskola',
                            location: 'Screaming Cork',
                            quest: 'edgar_book',
                            quest_status: 'completed'
                        }
                    );
                    
                    // Check if the player has the vestigel quest and was promised the vestigel
                    if (this.questSystem.getQuest('the_three_vestigels')) {
                        // Next dialog will give the vestigel
                        this.dialogContent.edgar_book_farewell.text = "I should get to work now. The ideas are flowing, and I don't want to lose them. Oh, and as promised, here's the vestigel. It's of more use to you than to me. Thank you again for your help. Feel free to check in on my progress sometime.";
                    }
                }
            },

            // Final farewell after completing the book quest
            edgar_book_farewell: {
        
                text: "I should get to work now. The ideas are flowing, and I don't want to lose them. Thank you again for your help. Feel free to check in on my progress sometime.",
                options: [
                    { text: "Good luck, Edgar", next: "edgar_start" }
                ],
                onTrigger: () => {
                    
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
                }
            },

            edgar_imaginator: {
        
                text: "I dreamed up locations and characters for Dr. Elphi Quarn's games. Turns out my imagination was too... wild. Too erratic, they said. My dreams were 'unusable.' Their loss.",
                options: [
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_jobs: {
        
                text: "Bad timing, mostly. The Scraper took the Rusty Choir and stopped being an official part of the city - no need for a janitor then. The other jobs... well, being a mišutkenn doesn't help with job security in this city.",
                options: [
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_festival: {
        
                text: "The Burning Bear Festival? A cruel reminder of an ancient 'victory' over my kind. They stuff bear skins with things they want to be rid of, then burn them at midnight. Some fill them with pests, bad habits, vices... others with rivals, if the rumors are true.",
                options: [
                    { text: "That sounds disturbing.", next: "edgar_disturbing" },
                    { text: "It's just tradition, isn't it?", next: "edgar_tradition" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_disturbing: {
                text: "It is. Imagine being surrounded by burning effigies that look like your ancestors. The city lights up with fires of different colors and smells, while I hide away, waiting for it to end.",
                options: [
                    { text: "I'm sorry to hear that.", next: "edgar_sympathy" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_tradition: {
        
                text: "Tradition? Traditions can be cruel. Just because something has been done for generations doesn't make it right. But few in this city would agree with me.",
                options: [
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_sympathy: {
        
                text: "Your sympathy is... unexpected. But appreciated. Perhaps not everyone in this city is as thoughtless as I've come to believe.",
                options: [
                    { text: "Back to other topics", next: "edgar_start" }
                ],
                onTrigger: () => {
                    this.showNotification('Growth increased');
                    this.modifyGrowthDecay(1, 0);
                }
            },

            // New vestigel dialog path
            edgar_vestigel: {
        
                text: "A vestigel? Yes... I do have one. It's a peculiar object, a small small, but apparently valuable token. It was hidden inside a plush toy. See, I rather bought it from a street vendor, when I saw it. Otherwise somebody would use it for that cursed festival. The vendor didn't know about the Vestigel, but she surprisingly refused to take it back, when I offered it to her. She said something about a professional honor, hmm...",
                options: [
                    // Use ternary to determine next dialog based on book quest completion status
                    { text: "I need it for an important purpose.", next: this.questSystem.getQuest('edgar_book')?.status === 'completed' ? "edgar_vestigel_give_completed" : "edgar_vestigel_need" },
                    { text: "May I have it?", next: this.questSystem.getQuest('edgar_book')?.status === 'completed' ? "edgar_vestigel_give_completed" : "edgar_vestigel_request" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_vestigel_need: {
        
                text: "Important purpose, you say? Well, I don't really *need* it, but I kinda like it. Maybe you could do something for me in exchange?",
                options: [
                    { text: "What do you need?", next: "edgar_vestigel_convince" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_vestigel_book_offer: {
                text: "You would do that for me? In exchange for the vestigel... Very well. Here, take it. It's of more use to you than to me, it seems. And I look forward to our literary collaboration.",
                options: [
                    { text: "Thank you. I'll help you create something wonderful.", next: "edgar_vestigel_thanks" }
                ],
                onTrigger: () => {
                    this.questSystem.addQuest(
                        'edgar_book',
                        'Help Edgar to write a book',
                        'Edgar Eskola mentioned he wants to write a book. I should help him.'
                    );

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
                    this.questSystem.updateQuest('the_three_vestigels', 'Received a vestigel from Edgar in exchange for helping with his book.', 'edgar_vestigel_acquired');

                    // Growth increase
                    this.showNotification('Growth increased');
                    this.modifyGrowthDecay(1, 0);

                    // Add journal entry about receiving the vestigel
                    this.addJournalEntry(
                        'edgar_vestigel_received',
                        'The Writer\'s Token',
                        'Today I acquired one of the three vestigels from Edgar Eskola at the Screaming Cork. He gave it to me in exchange for my promise to help him write his book. The vestigel had been hidden inside a plush toy that Edgar had bought from a street vendor. He mentioned that the vendor refused to take it back when offered, citing "professional honor." The vestigel itself is small but intricately carved, clearly valuable to someone who knows its purpose.',
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
            },
            edgar_vestigel_request: {
        
                text: "Just like that? You know that's a valuable trinket. I wouldn't give it away without good reason.",
                options: [
                    { text: "What would convince you to part with it?", next: "edgar_vestigel_convince" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_vestigel_convince: {
        
                text: "Hmm...",
                options: [
                    // Determine which option to show based on book quest status
                    ...(this.questSystem.getQuest('edgar_book')?.status === 'completed' ? [
                        { text: "I already helped you write your book.", next: "edgar_vestigel_give_completed" }
                    ] : this.questSystem.getQuest('edgar_book') ? [
                        { text: "I could help with your book, as we discussed earlier.", next: "edgar_vestigel_book_help" }
                    ] : [
                        { text: "Maybe I could help you with something.", next: "edgar_vestigel_offer" }
                    ]),
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_vestigel_book_help: {
                text: "Ah yes, the book. I've been thinking more about it since we talked. If you're serious about helping me with it, I could part with the vestigel. It seems like a fair exchange.",
                options: [
                    { text: "I'll definitely help you write something meaningful.", next: "edgar_vestigel_book_offer" }
                ],
                onTrigger: () => {
                    // Add journal entry about this decision point
                    this.addJournalEntry(
                        'edgar_book_vestigel_path',
                        'Literary Exchange',
                        'Edgar seems more enthusiastic about his book than holding onto the vestigel. This is the perfect opportunity to obtain one of the three vestigels I need while also helping him fulfill his dream of becoming a writer.',
                        this.journalSystem.categories.THOUGHTS,
                        {
                            character: 'Edgar Eskola',
                            location: 'Screaming Cork',
                            quests: ['the_three_vestigels', 'edgar_book']
                        }
                    );
                }
            },
            edgar_vestigel_offer: {
                text: "Hmm... maybe you could help me with something. Do you know something about literature? I would like to become... a writer. But I don't know where to start. You would help me with that? I've been struggling to find a voice, a story worth telling. If you could truly help me...",
                options: [
                    { text: "I'll do my best.", next: "edgar_vestigel_thanks" }
                ],
                onTrigger: () => {
                    this.questSystem.addQuest(
                        'edgar_book',
                        'Help Edgar to write a book',
                        'Edgar Eskola mentioned he wants to write a book. I should help him.'
                    );

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
                text: "Yes, you did offer to help with my book. A fair exchange - your help for the vestigel. I've been collecting ideas but haven't made much progress.",
                options: [
                    { text: "I'll make sure your book becomes a reality.", next: "edgar_vestigel_thanks" }
                ]
            },
            
            // New dialog for when player asks for vestigel after book is completed
            edgar_vestigel_give_completed: {
        
                text: "Oh, you're interested in the vestigel? After all your help with my book, I'd be happy to give it to you. It's of more use to you than to me. Here, take it with my gratitude.",
                options: [
                    { text: "Thank you, Edgar.", next: "edgar_start" }
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
                    { text: "Back to other topics", next: "edgar_start" }
                ],
                onTrigger: () => {
                    this.showNotification('Growth increased');
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
            }
        };
    }

    preload() {
        super.preload();
        this.load.image('screamingCorkBg', 'assets/images/backgrounds/ScreamingCork.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        this.load.image('edgarEskola', 'assets/images/characters/EdgarEskola.png');
        this.load.image('vestigel', 'assets/images/items/vestigel.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();

        // Set background
        const bg = this.add.image(400, 300, 'screamingCorkBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

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
        const doorHint = this.add.text(400, 380, 'Enter Tavern', {
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
            if (Math.abs(pointer.x - 400) < 50 && Math.abs(pointer.y - 470) < 100) {
                doorHint.setAlpha(1);
            } else {
                doorHint.setAlpha(0);
            }
        });

        // Add Edgar Eskola NPC
        this.createEdgarEskola();
    }

    update() {
        super.update();
    }

    createEdgarEskola() {
        // Create Edgar Eskola NPC
        this.edgar = this.add.image(200, 510, 'edgarEskola'); // Further increased Y to lower position more
        this.edgar.setScale(0.125); // Set appropriate scale
        this.edgar.setOrigin(0.5, 1.0); // Set origin to bottom center to align with ground
        this.edgar.setDepth(5);
        this.edgar.setInteractive({ useHandCursor: true });

        // Add dialog interaction
        this.edgar.on('pointerdown', () => {
            if (this.dialogVisible) return;
            this.showDialog('edgar_start');
        });

        // Add subtle wobble effect
        this.addWobbleEffect(this.edgar, 200, 510); // Update wobble position to match new Y
    }

    addWobbleEffect(sprite, baseX, baseY) {
        // Create a very subtle wobble effect
        this.tweens.add({
            targets: sprite,
            y: { from: baseY - 1, to: baseY + 1 },
            ease: 'Sine.easeInOut',
            duration: 1500,
            yoyo: true,
            repeat: -1
        });

        // Add a very slight rotation wobble
        this.tweens.add({
            targets: sprite,
            angle: { from: -1, to: 1 },
            ease: 'Sine.easeInOut',
            duration: 2000,
            yoyo: true,
            repeat: -1,
            delay: 5000 // Offset from the y-wobble for more natural movement
        });
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.ScreamingCorkScene = ScreamingCorkScene;
}
