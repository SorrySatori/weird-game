import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import ShopSystem from '../systems/items/ShopSystem.js';
import JournalSystem from '../systems/JournalSystem.js';

export default class VoxMarket extends GameScene {
    constructor() {
        super({ key: 'VoxMarket' });
        this.isTransitioning = false; // Add flag to track transition state
        this.shopSystem = null;
        this.kloorPath = [
            { x: 200, y: 440, duration: 5000 },
            { x: 400, y: 440, duration: 3000 },
            { x: 600, y: 440, duration: 4000 },
            { x: 400, y: 440, duration: 3000 }
        ];
        this.kloorPathIndex = 0;
        this.journalSystem = JournalSystem.getInstance();
    }

    get dialogContent() {
        return {
            ...super.dialogContent, // Include parent dialog content for symbiont dialogs
            
            // Kloor Venn dialog
            kloor_start: {
                text: "Kloor Venn eyes you with a mixture of suspicion and interest. 'What do you want? I'm busy.'" ,
                options: [
                    { text: "Who are you?", next: "kloor_who" },
                    { text: "What are you selling?", next: "kloor_selling" },
                    { text: "I want to sell you some spores.", next: "kloor_buy_spores" },
                    ...(this.registry.get('questSystem')?.getQuest('find_bishop') ? [
                        { text: "Do you know anything about the Bishop of Threshold?", next: "kloor_bishop" }
                    ] : []),
                    ...(this.registry.get('questSystem')?.getQuest('the_three_vestigels') ? [
                        { text: "About those Vestigels...", next: "kloor_vestigels_progress" }
                    ] : []),
                    { text: "Goodbye.", next: "closeDialog" }
                ],
                onTrigger: () => {
                    // Add journal entry for meeting Kloor Venn if not already added
                    if (!this.hasJournalEntry('kloor_venn_meeting')) {
                        this.addJournalEntry(
                            'kloor_venn_meeting',
                            'Kloor Venn - Pharmaceutical Entrepreneur',
                            'In Voxmarket, I encountered Kloor Venn, a self-described "pharmaceutical entrepreneur" who deals in a psychoactive substance called Oltrac. He seems particularly interested in my fungal spores as potential source material for his products. There is an air of shifty opportunism about him, though his connections in the market appear extensive.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Kloor Venn', location: 'Voxmarket' }
                        );
                    }
                }
            },
            
            kloor_who: {
                text: "'The name's Kloor Venn. I'm a... pharmaceutical entrepreneur. I deal in specialized substances that expand the mind.' He taps his temple and grins.",
                options: [
                    { text: "What kind of substances?", next: "kloor_substances" },
                    { text: "Back", next: "kloor_start" }
                ]
            },
            
            kloor_substances: {
                text: "'I specialize in Oltrac - a rare psychoactive compound derived from certain... biological materials.' He eyes your fungal growths with interest. 'Materials not unlike what you seem to be carrying around.'",
                options: [
                    { text: "Tell me more about Oltrac", next: "kloor_oltrac" },
                    { text: "Back", next: "kloor_start" }
                ]
            },
            
            kloor_oltrac: {
                text: "'Oltrac comes in different varieties. Gray is common, Violet is more potent, and Amber... well, Amber Oltrac is something special. Opens doors in the mind that most don't even know exist. The quality depends on the source material.'",
                options: [
                    { text: "I want to buy some", next: "kloor_shop" },
                    { text: "I could sell you some spores", next: "kloor_buy_spores" },
                    { text: "Back", next: "kloor_start" }
                ]
            },
            
            kloor_selling: {
                text: "'I deal in Oltrac - finest mind-expanding substance in the Voxmarket. Opens your perception to the true nature of reality.' He lowers his voice. 'Interested in buying? Or perhaps... selling me some of those spores you're carrying?'",
                options: [
                    { text: "Show me what you have", next: "kloor_shop" },
                    { text: "I could sell you some spores", next: "kloor_buy_spores" },
                    { text: "Back", next: "kloor_start" }
                ]
            },
            
            kloor_shop: {
                text: "'Take a look at my wares. Quality guaranteed.'",
                options: [
                    { text: "Show me", next: "kloor_open_shop" },
                    { text: "Not now", next: "kloor_start" }
                ]
            },
            
            kloor_open_shop: {
                text: "",
                options: [],
                onShow: () => {
                    this.hideDialog();
                    this.shopSystem.open();
                }
            },
            
            kloor_buy_spores: {
                text: "Kloor's eyes light up with interest. 'I'm always in the market for quality spores. They're the key ingredient in my Oltrac. I'll pay you based on what I can make with them. How much are you willing to part with?'",
                options: [
                    { text: "Sell 10 spores", next: "kloor_sell_spores_10" },
                    { text: "Sell 20 spores", next: "kloor_sell_spores_20" },
                    { text: "Sell 30 spores", next: "kloor_sell_spores_30" },
                    { text: "Not now", next: "kloor_start" }
                ]
            },
            
            kloor_sell_spores_10: {
                text: "You offer to sell 10 spores to Kloor.",
                options: [
                    { text: "Confirm", next: "" },
                    { text: "Back", next: "kloor_buy_spores" },
                ],
                onTrigger: (option) => {
                    if (option && option.text === "Confirm") {
                        const dialogId = this.sellSporesToKloor(10);
                        return dialogId; // Return the dialog ID to override the 'next' value
                    }
                }
            },
            
            kloor_sell_spores_20: {
                text: "You offer to sell 20 spores to Kloor.",
                options: [
                    { text: "Confirm", next: "" },
                    { text: "Back", next: "kloor_buy_spores" },
                ],
                onTrigger: (option) => {
                    if (option && option.text === "Confirm") {
                        const dialogId = this.sellSporesToKloor(20);
                        return dialogId; // Return the dialog ID to override the 'next' value
                    }
                }
            },
            
            kloor_sell_spores_30: {
                text: "You offer to sell 30 spores to Kloor.",
                options: [
                    { text: "Confirm", next: "" },
                    { text: "Back", next: "kloor_buy_spores" },
                ],
                onTrigger: (option) => {
                    if (option && option.text === "Confirm") {
                        const dialogId = this.sellSporesToKloor(30);
                        return dialogId; // Return the dialog ID to override the 'next' value
                    }
                }
            },
            
            kloor_not_enough_spores: {
                text: "Kloor frowns. 'You don't have enough spores. Come back when you've collected more.'",
                options: [
                    { text: "OK", next: "kloor_start" }
                ]
            },
            

            
            kloor_gray_oltrac_8: {
                text: "Kloor examines your spores carefully, then nods. 'These will work for Gray Oltrac - the common stuff. Not bad.' He hands you 8 gold coins. 'Pleasure doing business with you.'",
                options: [
                    { text: "Thanks", next: "kloor_start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(0, 1);
                }
            },
            
            kloor_gray_oltrac_16: {
                text: "Kloor examines your spores carefully, then nods. 'These will work for Gray Oltrac - the common stuff. Not bad.' He hands you 16 gold coins. 'Pleasure doing business with you.'",
                options: [
                    { text: "Thanks", next: "kloor_start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(0, 2);
                }
            },
            
            kloor_gray_oltrac_24: {
                text: "Kloor examines your spores carefully, then nods. 'These will work for Gray Oltrac - the common stuff. Not bad.' He hands you 24 gold coins. 'Pleasure doing business with you.'",
                options: [
                    { text: "Thanks", next: "kloor_start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(0, 3);
                }
            },
            
            kloor_violet_oltrac_15: {
                text: "Kloor's eyes light up as he examines your spores. 'Excellent quality! I can make Violet Oltrac with these.' He hands you 15 gold coins with a grin. 'Very good business indeed.'",
                options: [
                    { text: "Thanks", next: "kloor_start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(0, 4);
                }
            },
            
            kloor_violet_oltrac_30: {
                text: "Kloor's eyes light up as he examines your spores. 'Excellent quality! I can make Violet Oltrac with these.' He hands you 30 gold coins with a grin. 'Very good business indeed.'",
                options: [
                    { text: "Thanks", next: "kloor_start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(0, 5);
                }
            },
            
            kloor_violet_oltrac_45: {
                text: "Kloor's eyes light up as he examines your spores. 'Excellent quality! I can make Violet Oltrac with these.' He hands you 45 gold coins with a grin. 'Very good business indeed.'",
                options: [
                    { text: "Thanks", next: "kloor_start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(0, 6);
                }
            },
            
            kloor_amber_oltrac_25: {
                text: "Kloor gasps as he examines your spores. 'Extraordinary! These are perfect for Amber Oltrac - the rarest kind!' He eagerly counts out 25 gold coins. 'Exceptional business! Come back anytime!'",
                options: [
                    { text: "Thanks", next: "kloor_start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(0, 7);
                }
            },
            
            kloor_amber_oltrac_50: {
                text: "Kloor gasps as he examines your spores. 'Extraordinary! These are perfect for Amber Oltrac - the rarest kind!' He eagerly counts out 50 gold coins. 'Exceptional business! Come back anytime!'",
                options: [
                    { text: "Thanks", next: "kloor_start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(0, 8);
                }
            },
            
            kloor_amber_oltrac_75: {
                text: "Kloor gasps as he examines your spores. 'Extraordinary! These are perfect for Amber Oltrac - the rarest kind!' He eagerly counts out 75 gold coins. 'Exceptional business! Come back anytime!'",
                options: [
                    { text: "Thanks", next: "kloor_start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(0, 9);
                }
            },
            
            kloor_bishop: {
                text: "Kloor's expression shifts to one of caution. 'The Bishop of Threshold? Yeah, I've seen her around. Not someone to mess with. She was here in the market recently, trading with some of the merchants.'",
                options: [
                    { text: "Do you know where she went?", next: "kloor_bishop_location" },
                    { text: "What was she trading?", next: "kloor_bishop_trading" },
                    { text: "Back", next: "kloor_start" }
                ]
            },
            
            kloor_bishop_location: {
                text: "'Can't say for certain. The Bishop moves in mysterious ways.' He smirks at his own joke. 'But I heard she was heading toward the Hall. She has contacts there.'",
                options: [
                    { text: "Thanks for the information", next: "kloor_start" },
                    { text: "What was she trading?", next: "kloor_bishop_trading" }
                ]
            },
            
            kloor_bishop_trading: {
                text: "'Now that's interesting.' Kloor leans in closer. 'She had this strange currency - called Vestigels. Not like regular money. They're rare, experimental. Supposedly they hold... properties. A merchant named Zerren got one from her.'",
                options: [
                    { text: "Tell me more about these Vestigels", next: "kloor_vestigels" },
                    { text: "Thanks for the information", next: "kloor_start" }
                ]
            },
            
            kloor_vestigels: {
                text: "'Vestigels are strange. They're like coins but... alive somehow. There are three known to exist in the market. I've been trying to get my hands on one to study its properties. Could be valuable for my... research.'",
                options: [
                    { text: "I could help you get one", next: "kloor_vestigels_help" },
                    { text: "Sounds dangerous", next: "kloor_start" }
                ]
            },
            
            kloor_vestigels_help: {
                text: "'Really? That would be... useful.' Kloor's eyes narrow with suspicion, then he nods. 'If you can get me one of the Vestigels, I'll tell you everything I know about the Bishop's movements. Deal?'",
                options: [
                    { text: "Deal", next: "kloor_vestigels_quest_start" },
                    { text: "I need to think about it", next: "kloor_start" }
                ]
            },
            
            kloor_vestigels_quest_start: {
                text: "Perfect! Let me know when you have one.",
                options: [
                    { text: "OK", next: "kloor_start" }
                ],
                onTrigger: () => {
                    // Start the quest if it doesn't exist yet
                    if (!this.registry.get('questSystem')?.getQuest('the_three_vestigels')) {
                        this.questSystem.updateQuest('find_bishop', 'Kloor Venn wants me to find one of the three Vestigels in the market. He mentioned that a merchant named Zerren has one.', 'vestigel');
                        this.questSystem.addQuest(
                            'the_three_vestigels',
                            'The Three Vestigels',
                            'Kloor Venn wants me to find one of the three Vestigels in the market. He mentioned that a merchant named Zerren has one.'
                        );
                        this.showNotification('New Quest: The Three Vestigels');
                    }
                }
            },
            
            kloor_vestigels_quest_info: {
                text: "'Here's what I know: Zerren has one Vestigel. He's usually in the Market area. The other two are held by merchants named Liss and Dovan. Find one of them, get me a Vestigel, and I'll tell you what you need to know about the Bishop.'",
                options: [
                    { text: "I'll find one for you", next: "closeDialog" }
                ]
            },
            
            kloor_vestigels_progress: {
                text: "'Any luck finding a Vestigel? Those things aren't easy to come by.'",
                options: [
                    { text: "Not yet", next: "kloor_start" },
                    ...(this.hasItem('vestigel') ? [
                        { text: "I have one right here", next: "kloor_vestigels_complete" }
                    ] : [])
                ]
            },
            
            kloor_vestigels_complete: {
                text: "Kloor's eyes widen as you show him the Vestigel. 'Incredible! You actually found one!' He carefully takes it from you, examining it with fascination. 'As promised, I'll tell you what I know about the Bishop.'",
                options: [
                    { text: "Tell me", next: "kloor_bishop_reveal" }
                ],
                onTrigger: function() {
                    // Remove the Vestigel from inventory
                    this.removeItemFromInventory('vestigel');
                    
                    // Update quest with message before completing it
                    this.questSystem.updateQuest(
                        'the_three_vestigels', 
                        'I gave the vestigel to Kloor Venn in exchange for information about the Bishop of Threshold.', 
                        'completed'
                    );
                    
                    // Complete the quest
                    this.questSystem.completeQuest('the_three_vestigels');
                    this.showNotification('Quest Completed: The Three Vestigels');
                    
                    // Add journal entry about giving the vestigel to Kloor
                    this.addJournalEntry(
                        'kloor_vestigel_exchange',
                        'Vestigel Exchange with Kloor',
                        'I traded the vestigel I acquired from Edgar Eskola to Kloor Venn. In exchange, he promised to reveal what he knows about the Bishop of Threshold and her activities in the market. The strange coin-like object seemed to fascinate him greatly - perhaps for its value, or perhaps for some other property I\'m not aware of.',
                        this.journalSystem.categories.QUESTS,
                        { character: 'Kloor Venn', item: 'Vestigel', location: 'Voxmarket' }
                    );
                }
            },
            
            kloor_bishop_reveal: {
                text: "'From what I know, she shops for rare gaming items. You see, our Bishop became addicted to dream games from Dr. Elphi Quarn. She visited Dr. Elphi quite often. Dr. Elphi is famous game designer, owner of the studio where games are made from dreams of professional imaginators. She is also an inventor. Kloor told me, that the Bishop seemed depressed and was searching for something. Her contact with Dr. Elphi seems quite irregular and unusual. I should look for Dr. Elphi at the Scraper 1140..'",
                options: [
                    { text: "The dream games?", next: "kloor_dream_games" }
                ]
            },
            
            kloor_dream_games: {
                text: "'The dream games? Yes, they could be... addictive. ARB Ambra Studio produces the best... actually the only existing ones. I heard that finding a good imaginator is quite hard. The studio is equipped with specially adapted beds, the imaginators wear silver helmets without visors on their heads, to which is attached a complex system of wires, cables and electrodes. The helmets are the doctor's invention and she is duly proud of them.'",
                options: [
                    { text: "Thank you for the information", next: "kloor_quest_update" }
                ]
            },
            
            kloor_quest_update: {
                text: "",
                options: [],
                onTrigger: function() {
                    // Update the find_bishop quest with more detailed information
                    if (this.questSystem.getQuest('find_bishop')) {
                        this.questSystem.updateQuest(
                            'find_bishop',
                            'According to Kloor Venn, the Bishop visited Dr. Elpi Quarn quite often. Dr. Elphi is famous game designer, owner of the studio where games are made from dreams of professional imaginators. She is also an inventor. Kloor told me, that the Bishop seemed depressed and was searching for something. Her contact with Dr. Elphi seems quite irregular and unusual. I should look for Dr. Elphi at the Scraper 1140.',
                            'elphi_contact'
                        );
                        this.showNotification('Quest Updated: Find the Bishop of Threshold');
                        
                        // Add journal entry about the Bishop's search for the Threshold Key
                        this.addJournalEntry(
                            'bishop_elphi_contact',
                            'The Bishop\'s Contact with Dr. Elphi',
                            'According to Kloor Venn, the Bishop visited Dr. Elpi Quarn quite often. Dr. Elphi is famous game designer, owner of the studio where games are made from dreams of professional imaginators. She is also an inventor. Kloor told me, that the Bishop seemed depressed and was searching for something. Her contact with Dr. Elphi seems quite irregular and unusual. I should look for Dr. Elphi at the Scraper 1140.',
                            this.journalSystem.categories.EVENTS,
                        );
                        
                        // Close dialog after updating quest
                        this.hideDialog();
                    }
                }
            }
        };
    }

    preload() {
        super.preload();
        this.load.image('voxMarketBg', 'assets/images/backgrounds/Voxmarket.png');
        this.load.image('exitArea', 'assets/images/ui/door.png'); // Reusing door image for exit area
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        
        // Load Kloor Venn drug dealer assets
        this.load.image('kloor', 'assets/images/characters/rat.png');
        
        // Load Oltrac drug images
        this.load.image('grayOltrac', 'assets/images/effects/grayOltrac.png'); 
        this.load.image('violetOltrac', 'assets/images/effects/violetOltrac.png'); 
        this.load.image('amberOltrac', 'assets/images/effects/amberOltrac.png'); 
        
        // Audio is already loaded in GameScene's preload
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Play market theme
        this.playSceneMusic('marketTheme');
        
        // Set vox market background
        const bg = this.add.image(400, 200, 'voxMarketBg');
        bg.setDisplaySize(800, 750); // Further increased height to fully cover the ground
        bg.setDepth(-1);
        
        // Create a custom ground for the market scene
        this.createMarketGround();
        
        // Completely hide the original ground
        if (this.ground) {
            this.ground.destroy(); // Destroy instead of just hiding
        }
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Position the priest at the right side when entering this scene
        this.priest.x = 750;
        this.priest.y = 470; // Position on the ground
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }
        
        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
        
        // Create exit to CrossroadScene at the left edge
        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            50, // width
            200, // height
            'left', // direction
            'CrossroadScene', // target scene
            50, // walk to x
            470 // walk to y
        );
        
        // Create entrance to VoxmarketMarketScene at the top
        this.transitionManager.createTransitionZone(
            400, // x position
            470, // y position
            200, // width
            50, // height
            'up', // direction
            'VoxmarketMarketScene', // target scene
            400, // walk to x
            470 // walk to y
        );
        
        // Create entrance to VoxmarketHallScene at the right
        this.transitionManager.createTransitionZone(
            550, // x position
            470, // y position
            50, // width
            200, // height
            'right', // direction
            'VoxmarketHallScene', // target scene
            550, // walk to x
            470 // walk to y
        );
        
        // Add hints for the entrances
        const marketHint = this.add.text(400, 470, 'Market', {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        marketHint.setOrigin(0.5);
        marketHint.setAlpha(0);
        marketHint.setDepth(10);
        
        const hallHint = this.add.text(550, 470, 'Hall', {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        hallHint.setOrigin(0.5);
        hallHint.setAlpha(0);
        hallHint.setDepth(10);
        
        // Show hints when hovering near the entrances
        this.input.on('pointermove', (pointer) => {
            // Check if pointer is near the market entrance
            if (Math.abs(pointer.x - 400) < 100 && Math.abs(pointer.y - 470) < 50) {
                marketHint.setAlpha(1);
            } else {
                marketHint.setAlpha(0);
            }
            
            // Check if pointer is near the hall entrance
            if (Math.abs(pointer.x - 550) < 50 && Math.abs(pointer.y - 470) < 100) {
                hallHint.setAlpha(1);
            } else {
                hallHint.setAlpha(0);
            }
        });
        
        // Remove the NPC if it exists
        if (this.stranger) {
            this.stranger.destroy();
        }
        
        // Create Kloor Venn NPC
        this.createKloorVenn();
        
        // Initialize the shop system for Kloor's Oltrac shop
        this.initShopSystem();
    }

    shutdown() {
        // Restore background music when leaving the scene
        this.restoreBackgroundMusic();
        super.shutdown();
    }

    update() {
        // Call parent update for all standard mechanics
        super.update();
        
        // Update shop money display if needed
        if (this.shopSystem && this.shopSystem.isOpen) {
            this.shopSystem.updateMoneyDisplay();
        }
    }
    
    /**
     * Create Kloor Venn NPC with walking animation
     */
    createKloorVenn() {
        // Create Kloor Venn NPC
        this.kloor = this.add.sprite(300, 440, 'kloor');
        this.kloor.setScale(0.15); // Adjust scale as needed
        this.kloor.setDepth(5);
        this.kloor.setInteractive({ useHandCursor: true });
        
        // Add dialog interaction
        this.kloor.on('pointerdown', () => {
            if (this.dialogVisible) return;
            this.showDialog('kloor_start');
        });
        
        // Create walking animation for Kloor
        this.startKloorWalking();
        
        // Add a name tag above Kloor
        const kloorTag = this.add.text(300, 420, 'Kloor Venn', {
            fontSize: '14px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 5, y: 2 }
        });
        kloorTag.setOrigin(0.5);
        kloorTag.setDepth(6);
        
        // Make the name tag follow Kloor
        this.kloorTag = kloorTag;
    }
    
    /**
     * Start Kloor's walking animation along a path
     */
    startKloorWalking() {
        if (!this.kloor) return;
        
        const nextIndex = (this.kloorPathIndex + 1) % this.kloorPath.length;
        const nextPoint = this.kloorPath[nextIndex];
        
        // Determine direction for sprite flipping
        if (nextPoint.x > this.kloor.x) {
            this.kloor.setFlipX(false); // Face right
        } else if (nextPoint.x < this.kloor.x) {
            this.kloor.setFlipX(true); // Face left
        }
        
        // Create walking tween
        this.tweens.add({
            targets: this.kloor,
            x: nextPoint.x,
            y: nextPoint.y,
            duration: nextPoint.duration,
            ease: 'Linear',
            onUpdate: () => {
                // Update name tag position
                if (this.kloorTag) {
                    this.kloorTag.x = this.kloor.x;
                    this.kloorTag.y = this.kloor.y - 50;
                }
            },
            onComplete: () => {
                // Move to next point in path
                this.kloorPathIndex = nextIndex;
                this.startKloorWalking();
            }
        });
        
        // Add subtle bobbing motion for walking effect
        this.tweens.add({
            targets: this.kloor,
            y: nextPoint.y - 5,
            duration: 300,
            yoyo: true,
            repeat: Math.floor(nextPoint.duration / 600),
            ease: 'Sine.easeInOut'
        });
    }
    
    /**
     * Initialize the shop system for Kloor's Oltrac shop
     */
    initShopSystem() {
        // Oltrac shop inventory
        const shopInventory = [
            {
                id: 'grayOltrac',
                name: 'Gray Oltrac',
                description: 'A common variant of Oltrac. Provides mild hallucinogenic effects.',
                price: 15,
                type: 'drug',
                usable: true,
            },
            {
                id: 'violetOltrac',
                name: 'Violet Oltrac',
                description: 'A medium-strength variant of Oltrac. Enhances perception and provides vivid visions.',
                price: 30,
                type: 'drug',
                usable: true,
            },
            {
                id: 'amberOltrac',
                name: 'Amber Oltrac',
                description: 'The rarest and most potent form of Oltrac. Said to allow glimpses beyond the veil of reality.',
                price: 50,
                type: 'drug',
                usable: true,
                    }
        ];
        
        // Create shop system
        this.shopSystem = new ShopSystem(this, {
            shopName: "Kloor's Oltrac Emporium",
            inventory: shopInventory,
            position: {
                x: 400,
                y: 300
            },
            buyMultiplier: 1.0,
            sellMultiplier: 0.5
        });
    }
    
    /**
     * Sell spores to Kloor and determine which Oltrac he can make
     * @param {number} amount - Amount of spores to sell
     */
    sellSporesToKloor(amount) {
        const sporeSystem = this.registry.get('sporeSystem');
        const currentSpores = sporeSystem.getSporeLevel();
        
        if (currentSpores < amount) {
            // Not enough spores
            this.showDialog('kloor_not_enough_spores');
            return;
        }
        
        // Remove spores from player
        sporeSystem.modifySpores(-amount);
        
        // Add direct symbiont reaction to spore selling
        const symbiontSystem = this.registry.get('symbiontSystem');
        if (symbiontSystem && symbiontSystem.symbionts.has('thorne-still')) {
            // Always show a reaction when selling spores to Kloor
            const messages = [
                "Hey! I was saving those spores for later.",
                "Selling spores? I hope you got a good price for MY dinner.",
                "Less spores means less me. Is that what you want?",
                "I felt those spores vanish. It's like watching money burn.",
                "Fewer spores? I'm going to have to start rationing my existence.",
                "You're hemorrhaging spores. That's basically symbiont abuse.",
                "Those spores were load-bearing! The architecture of this relationship is at risk.",
                "I was counting those spores. Literally counting them. Now I have to start over.",
                "Spore reduction? This is why we can't have nice parasitic relationships.",
                "Less spores? Fine. I'll just photosynthesize your emotions instead."
            ];
            const message = messages[Math.floor(Math.random() * messages.length)];
            this.showNotification(`thorne-still: ${message}`, "", "", 10000);
        }
        
        // Determine Oltrac type and payment based on amount
        let oltracType, paymentAmount;
        
        // Determine Oltrac type based on amount of spores
        if (amount === 10) {
            // 10 spores - 80% Gray, 20% Violet
            const roll = Math.random();
            if (roll < 0.8) {
                oltracType = 'Gray';
                paymentAmount = 8; // Base payment for Gray
            } else {
                oltracType = 'Violet';
                paymentAmount = 15; // Base payment for Violet
            }
        } else if (amount === 20) {
            // 20 spores - 60% Gray, 35% Violet, 5% Amber
            const roll = Math.random();
            if (roll < 0.6) {
                oltracType = 'Gray';
                paymentAmount = 16; // Double payment for Gray
            } else if (roll < 0.95) {
                oltracType = 'Violet';
                paymentAmount = 30; // Double payment for Violet
            } else {
                oltracType = 'Amber';
                paymentAmount = 50; // Base payment for Amber
            }
        } else if (amount === 30) {
            // 30 spores - 40% Gray, 50% Violet, 10% Amber
            const roll = Math.random();
            if (roll < 0.4) {
                oltracType = 'Gray';
                paymentAmount = 24; // Triple payment for Gray
            } else if (roll < 0.9) {
                oltracType = 'Violet';
                paymentAmount = 45; // Triple payment for Violet
            } else {
                oltracType = 'Amber';
                paymentAmount = 75; // 1.5x payment for Amber
            }
        }
        
        // Add money to player
        this.moneySystem.add(paymentAmount);
        this.showNotification(`+${paymentAmount} gold`);
        
        // Determine which dialog to show based on the result
        let dialogId;
        
        if (oltracType === 'Gray') {
            if (paymentAmount === 8) dialogId = 'kloor_gray_oltrac_8';
            else if (paymentAmount === 16) dialogId = 'kloor_gray_oltrac_16';
            else dialogId = 'kloor_gray_oltrac_24';
        } else if (oltracType === 'Violet') {
            if (paymentAmount === 15) dialogId = 'kloor_violet_oltrac_15';
            else if (paymentAmount === 30) dialogId = 'kloor_violet_oltrac_30';
            else dialogId = 'kloor_violet_oltrac_45';
        } else { // Amber
            if (paymentAmount === 25) dialogId = 'kloor_amber_oltrac_25';
            else if (paymentAmount === 50) dialogId = 'kloor_amber_oltrac_50';
            else dialogId = 'kloor_amber_oltrac_75';
        }
        
        // Show the appropriate dialog directly
        this.showDialog(dialogId);
        console.log('dialogId', dialogId);
        return dialogId;
    }
    
    // Create a custom ground for the market scene that matches the aesthetic
    createMarketGround() {
        // Remove the original ground if it exists
        if (this.ground) {
            this.ground.destroy();
        }
        
        // Create a graphics object for the ground
        const groundGraphics = this.add.graphics();
        
        // Set the ground dimensions
        const groundWidth = 800;
        const groundHeight = 160;
        const groundY = 500;
        
        // Fill with dark greenish-gray base color to match market floor
        groundGraphics.fillStyle(0x1a2420, 1);
        groundGraphics.fillRect(0, groundY, groundWidth, groundHeight);
        
        // Add some texture with lines
        groundGraphics.lineStyle(1, 0x283c32, 0.3);
        
        // Horizontal lines for floor boards
        for (let i = 0; i < 10; i++) {
            const y = groundY + Math.random() * groundHeight;
            groundGraphics.beginPath();
            groundGraphics.moveTo(0, y);
            groundGraphics.lineTo(groundWidth, y);
            groundGraphics.closePath();
            groundGraphics.strokePath();
        }
        
        // Vertical lines for texture
        for (let i = 0; i < 20; i++) {
            const x = Math.random() * groundWidth;
            groundGraphics.beginPath();
            groundGraphics.moveTo(x, groundY);
            groundGraphics.lineTo(x, groundY + groundHeight);
            groundGraphics.closePath();
            groundGraphics.strokePath();
        }
        
        // Add green glowing particles to match the market atmosphere
        for (let i = 0; i < 50; i++) {
            const x = Math.random() * groundWidth;
            const y = groundY + Math.random() * (groundHeight - 10);
            const size = Math.random() * 3 + 1;
            
            const particle = this.add.circle(x, y, size, 0x32ff64, 0.3);
            particle.setDepth(1);
            
            // Add pulsating effect to some particles
            if (Math.random() > 0.7) {
                this.tweens.add({
                    targets: particle,
                    alpha: 0.1,
                    duration: 1500 + Math.random() * 1000,
                    yoyo: true,
                    repeat: -1,
                    ease: 'Sine.easeInOut'
                });
            }
        }
        
        // Set the ground depth
        groundGraphics.setDepth(0);
    }
}
