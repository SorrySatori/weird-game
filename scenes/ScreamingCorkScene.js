import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class ScreamingCorkScene extends GameScene {
    constructor() {
        super({ key: 'ScreamingCorkScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        return {
            ...super.dialogContent, // Include parent dialog content for symbiont dialogs
            
            // Edgar Eskola dialog
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
                    { text: "Goodbye.", next: "closeDialog" }
                ]
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
                text: "I’ve tried everything. Janitor. Clerk. Meat assembler. Imaginator. But I’ve never been anything truly mine. I think… I want to write a book. But I don’t know what it’s about yet.",
                options: [
                    { text: "I can help you write the book", next: "edgar_book" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_book: {
                text: "You would... do that for me? Thank you. I don't know what it's about yet. But I'm open to suggestions.",
                options: [
                    { text: "I will come back when I have an idea", next: "edgar_start" }
                ],
                onTrigger: () => {
                    this.questSystem.addQuest(
                        'edgar_book',
                        'Help Edgar to write a book',
                        'Edgar Eskola mentioned he wants to write a book. I should help him.'
                    );
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
                    { text: "I need it for an important purpose.", next: "edgar_vestigel_need" },
                    { text: "May I have it?", next: "edgar_vestigel_request" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_vestigel_need: {
                text: "Important purpose, you say? Well, I don't really *need* it, but I kinda like it. Maybe you could do something for me in exchange?",
                options: [
                    { text: "I could help you write your book", next: "edgar_vestigel_book" },
                    { text: "Back to other topics", next: "edgar_start" }
                ]
            },
            edgar_vestigel_book: {
                text: "You could help me to write a book. I've been struggling to find a voice, a story worth telling. If you could truly help me...",
                options: [
                    { text: "I promise to help you write your book", next: "edgar_vestigel_book_offer" }
                ]
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
                    ...(this.questSystem.getQuest('edgar_book') ? [
                        { text: "I could help with your book, as we discussed earlier.", next: "edgar_vestigel_book_help" }
                    ] : [
                        { text: "Maybe I could help you with something.", next: "edgar_vestigel_offer" }
                    ]),
                    { text: "Back to other topics", next: "edgar_start" }
                ]
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
                }
            },
            edgar_vestigel_book_help: {
                text: "Yes, you did offer to help with my book. A fair exchange - your help for the vestigel. I've been collecting ideas but haven't made much progress.",
                options: [
                    { text: "I'll make sure your book becomes a reality.", next: "edgar_vestigel_thanks" }
                ]
            },
            edgar_vestigel_thanks: {
                text: "Remember your promise. I look forward to seeing what we can create together. A book that truly captures the essence of... well, that's what we need to discover.",
                options: [
                    { text: "Back to other topics", next: "edgar_start" }
                ],
                onTrigger: () => {
                    this.showNotification('Growth increased');
                    this.modifyGrowthDecay(1, 0);
                    this.questSystem.updateQuest('the_three_vestigels', 'Edgar Eskola would trade the Vestigel for your help with his book.', 'edgar_book_trade');
                }
            }
        };
    }

    preload() {
        super.preload();
        this.load.image('screamingCorkBg', 'assets/images/backgrounds/ScreamingCork.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        this.load.image('edgarEskola', 'assets/images/characters/EdgarEskola.png');
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
