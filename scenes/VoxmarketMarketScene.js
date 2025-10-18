import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';
import ShopSystem from '../systems/items/ShopSystem.js';

export default class VoxmarketMarketScene extends GameScene {
    constructor() {
        super({ key: 'VoxmarketMarketScene' });
        this.isTransitioning = false; // Add flag to track transition state
        this.journalSystem = JournalSystem.getInstance();
    }
    
    /**
     * Check if the player has learned about Bishop's connection to Dr. Elphi
     * through completing either the rust_reclamation or the_three_vestigels quests
     */
    hasElphiBishopInfo() {
        const questSystem = this.registry.get('questSystem');
        const rustQuestCompleted = questSystem?.getQuest('rust_reclamation')?.isComplete;
        const vestigelQuestCompleted = questSystem?.getQuest('the_three_vestigels')?.isComplete;
        return rustQuestCompleted || vestigelQuestCompleted;
    }

    get dialogContent() {
        return {
            ...super.dialogContent,
            speaker: 'Zerren',
            // Zerren dialog
            zerren_start: {
                text: "A woman with vibrant clothing and a small stall of trinkets notices your approach. 'Welcome to my little corner of Voxmarket. I'm Zerren. Looking for anything special today?'",
                options: [
                    { text: "Who are you?", next: "zerren_who" },
                    { text: "What do you sell?", next: "zerren_selling" },
                    ...(this.registry.get('questSystem')?.getQuest('the_three_vestigels') ? [
                        { text: "About the Vestigel you had...", next: "zerren_vestigel_inquiry" }
                    ] : []),
                ]
            },
            
            zerren_who: {
                text: "'I'm Zerren, a collector and seller of curiosities from across the realms. Been trading here in Voxmarket for years now. You'll find all sorts of interesting trinkets at my stall that you won't see anywhere else.'",
                options: [
                    { text: "What kind of trinkets?", next: "zerren_selling" },
                    { text: "Back", next: "zerren_start" }
                ]
            },
            
            zerren_selling: {
                text: "'I specialize in rare oddities and collectibles. Decorative items mostly, but sometimes I get my hands on things with... unusual properties.' She gestures to her collection of strange figurines, crystals, and small mechanical devices.",
                options: [
                    { text: "Interesting collection", next: "zerren_collection" },
                    { text: "Show me what you have for sale", next: "zerren_shop" },
                    { text: "Back", next: "zerren_start" }
                ]
            },
            
            zerren_shop: {
                text: "'Of course! Take a look at my current inventory. I'm always getting new items in, so check back regularly.'" + (this.hasElphiBishopInfo() ? " She lowers her voice. 'I recently acquired something special - an old elevator button with unusual markings. Might be of interest if you're exploring the taller structures around here.'" : ""),
                options: [], // Empty options array is required
                onShow: () => {
                    // Close the dialog first
                    this.hideDialog();
                    
                    // Open the shop after a short delay
                    this.time.delayedCall(300, () => {
                        if (this.shopSystem) {
                            this.shopSystem.open();
                        }
                    });
                }
            },
            
            zerren_collection: {
        speaker: 'Unknown',
                text: "'Thank you! I take pride in finding unique items. Had a lovely plush toy recently that was quite popular - sold it just last week. Strange little thing, but charming in its own way.'",
                options: [
                    { text: "Tell me more about that toy", next: "zerren_plush_toy" },
                    { text: "Back", next: "zerren_start" }
                ]
            },
            
            zerren_plush_toy: {
                text: "'It was an odd little thing - looked like a cross between a stuffed animal and some kind of abstract sculpture. Got it from a traveler passing through.'",
                options: [
                    { text: "Who bought it?", next: "zerren_buyer_inquiry" },
                    { text: "Back", next: "zerren_start" }
                ]
            },
            
            zerren_vestigel_inquiry: {
                text: "Zerren looks confused. 'Vestigel? How do you... how do you know about it? It was the worst deal I made in my life.'",
                options: [
                    { text: "Kloor told me about it.", next: "zerren_kloor_inquiry" },
                    { text: "I can't tell you, it doesn't matter.", next: "zerren_refuse_inquiry" },
                    { text: "Back", next: "zerren_start" }
                ]
            },
            
            zerren_kloor_inquiry: {
                text: "I see. That bastard wants it for himself, doesn't he? I don't know what he plans to do with it, but it's not good. Listen, I didn't know that it contained hidden Vestigel, I thought it was just a peculiar stuffed toy. The buyer discovered the secret later, but it was too late.",
                options: [
                    { text: "Who did you sell it to?", next: "zerren_buyer_inquiry" },
                    { text: "Back", next: "zerren_start" }
                ],
                onTrigger: () => {
                    const factionSystem = this.registry.get('factionSystem');
                    if (factionSystem) {
                        factionSystem.modifyReputation('RustChoir', +10);
                        factionSystem.modifyReputation('PithReclaimers', -10);
                        this.showNotification('Rust Choir Reputation +10');
                        this.showNotification('Pith Reclaimers Reputation -10');
                        
                        // Add journal entry for Rust Choir if not already added
                        if (!this.hasJournalEntry('rust_choir_faction')) {
                            this.addJournalEntry(
                                'rust_choir_faction',
                                'The Rust Choir - Machines and Memory',
                                'The Rust Choir appears to be a faction with an interest in old technology and machinery. They "sing the old machines awake" according to rumor, and seem to value the preservation and control of ancient tech. Their methods are questionable, as they appear willing to obtain technological artifacts through any means necessary. They have visible presence in Voxmarket and seem particularly interested in the living cores of buildings.',
                                this.journalSystem.categories.LORE,
                                { faction: 'Rust Choir', location: 'Voxmarket' }
                            );
                        }
                    }
                }
            },
            
            zerren_refuse_inquiry: {
                text: "Hmm... allright, be mysterious. I bet it's one of my competitors here at the market, so I will find out anyway. Listen, I didn't know that it contained hidden Vestigel, I thought it was just a peculiar stuffed toy. The buyer discovered the secret later, but it was too late.",
                options: [
                    { text: "Who did you sell it to?", next: "zerren_buyer_inquiry" },
                    { text: "Back", next: "zerren_start" }
                ],
                onTrigger: () => {
                    const factionSystem = this.registry.get('factionSystem');
                    if (factionSystem) {
                        factionSystem.modifyReputation('RustChoir', -10);
                        factionSystem.modifyReputation('PithReclaimers', +10);
                        this.showNotification('Rust Choir Reputation -10');
                        this.showNotification('Pith Reclaimers Reputation +10');
                        
                        // Add journal entry for Pith Reclaimers if not already added
                        if (!this.hasJournalEntry('pith_reclaimers_faction')) {
                            this.addJournalEntry(
                                'pith_reclaimers_faction',
                                'The Pith Reclaimers - Keepers of Balance',
                                'The Pith Reclaimers appear to be a faction concerned with maintaining balance and preventing technological overreach. They stand in opposition to the Rust Choir, believing some ancient technologies should remain dormant. They seem particularly protective of the "living cores" that power the buildings of the city, viewing them as entities to be respected rather than exploited.',
                                this.journalSystem.categories.LORE,
                                { faction: 'Pith Reclaimers', location: 'Voxmarket' }
                            );
                        }
                    }
                }
            },
            
            zerren_buyer_inquiry: {
                text: "Zerren suddenly becomes guarded. 'I... I don't typically disclose information about my customers. It's a matter of professional discretion, you understand.' She glances away nervously.",
                options: [
                    { text: "Offer 50 dinar as incentive", next: "zerren_bribe_attempt" },
                    { text: "Try to persuade her", next: "zerren_persuade_attempt" },
                    ...(this.registry.get('symbiontSystem')?.hasSymbiont('thorne-still') ? [
                        { text: "Use Thorne-still's Brain Rot power", next: "zerren_thorne_still_power" }
                    ] : []),
                    ...(this.registry.get('reputationSystem')?.getFactionReputation('sporemind_accord') >= 50 ? [
                        { text: "Appeal to Sporemind Accord relationship", next: "zerren_sporemind_appeal" }
                    ] : []),
                    { text: "Back", next: "zerren_start" }
                ]
            },
            
            zerren_bribe_attempt: {
                text: "You offer Zerren 50 dinar for the information.",
                options: [
                    { text: "Confirm", next: "zerren_bribe_success" },
                    { text: "Back", next: "zerren_buyer_inquiry" }
                ],
                onTrigger: (option) => {
                    if (option && option.text === "Confirm") {
                        if (this.hasEnoughMoney(50)) {
                            this.subtractMoney(50);
                            this.showNotification("-50 dinar");
                            return "zerren_bribe_success";
                        } else {
                            return "zerren_not_enough_money";
                        }
                    }
                }
            },
            
            zerren_not_enough_money: {
                text: "'That's a generous offer, but...' Zerren eyes your coin purse. 'It seems you don't actually have that much to spare.'",
                options: [
                    { text: "Try something else", next: "zerren_buyer_inquiry" }
                ]
            },
            
            zerren_bribe_success: {
                text: "Zerren quickly pockets the gold coins. 'Well, for this kind of compensation, I suppose I can make an exception.' She leans in closer. 'It was Edgar Eskola who bought the toy. Eccentric collector, lives in the upper district. Always looking for strange artifacts.'",
                options: [
                    { text: "Thank you for the information", next: "zerren_quest_update" }
                ],
                onTrigger: () => {
                    // Update the quest
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && questSystem.getQuest('the_three_vestigels')) {
                        questSystem.updateQuest('the_three_vestigels', "Zerren revealed that Edgar Eskola purchased the plush toy containing a Vestigel. He can be found usually somewhere around the Screaming Cork tavern.", 'found_eskola_lead');
                        this.showNotification("Quest updated: The Three Vestigels");
                    }
                },
            },
            zerren_persuade_attempt: {
                text: "'This is really important. The Vestigel inside that toy could be dangerous in the wrong hands. I need to find it for the safety of everyone in Upper Morkezela.' Zerren looks uncertain, weighing your words carefully.",
                options: [
                    { text: "Continue persuading", next: "zerren_persuade_roll" }
                ],
                onTrigger: () => {
                    // Simulate a persuasion check based on charisma or similar stat
                    const roll = Math.random() * 20;
                    
                    if (roll > 15) {
                        return "zerren_persuade_success";
                    } else {
                        return "zerren_persuade_fail";
                    }
                }
            },
            
            zerren_persuade_success: {
                text: "Zerren sighs, relenting. 'I suppose if it's that important... The buyer was Edgar Eskola. He's a collector of oddities with deep pockets. Has a place in the upper district. Very private person, though. Be careful how you approach him.'",
                options: [
                    { text: "Thank you for understanding", next: "zerren_quest_update" }
                ],
                onTrigger: () => {
                    // Update the quest
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && questSystem.getQuest('the_three_vestigels')) {
                        questSystem.updateQuest('the_three_vestigels', "Zerren revealed that Edgar Eskola purchased the plush toy containing a Vestigel. He can be found usually somewhere around the Screaming Cork tavern.", 'found_eskola_lead');
                        this.showNotification("Quest updated: The Three Vestigels");
                    }
                }
            },
            
            zerren_persuade_fail: {
                text: "Zerren shakes her head firmly. 'I'm sorry, but I can't break my customers' trust. Perhaps there's another way you could find this information?'",
                options: [
                    { text: "Try something else", next: "zerren_buyer_inquiry" }
                ]
            },
            
            zerren_thorne_still_power: {
                text: "You feel Thorne-still's presence intensify as the symbiont's power flows through you. Reality seems to waver around Zerren as the Brain Rot ability takes effect. Her eyes glaze slightly as she stumbles into a daze.",
                options: [
                    { text: "Who bought the plush toy?", next: "zerren_thorne_still_success" }
                ],
                onTrigger: () => {
                    const sporeSystem = this.registry.get('sporeSystem');
                    const currentSpores = sporeSystem.getSporeLevel();
                    
                    if (currentSpores < 10) {
                        this.showDialog('zerren_not_enough_spores');
                        return;
                    }
                    
                    sporeSystem.modifySpores(-10);
                }
            },
            
            zerren_not_enough_spores: {
                text: "Zerren shakes her head firmly. 'I'm sorry, but I can't break my customers' trust. Perhaps there's another way you could find this information?'",
                options: [
                    { text: "Try something else", next: "zerren_buyer_inquiry" }
                ]
            },
            
            zerren_thorne_still_success: {
                text: "Zerren speaks in a distant voice, as if reciting a fact from memory rather than revealing a secret. 'Urggh... Edgar Eskola purchased the plush toy. Grrrr... He lives in the upper district of Voxmarket. Collector of strange artifacts. Grrrr... ' She blinks, momentarily confused about what just happened.",
                options: [
                    { text: "Thank you for your help. Maybe take some rest, you dont' look well.", next: "zerren_quest_update" }
                ],
                onTrigger: () => {
                    // Update the quest
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && questSystem.getQuest('the_three_vestigels')) {
                        questSystem.updateQuest('the_three_vestigels', "Zerren revealed that Edgar Eskola purchased the plush toy containing a Vestigel. He can be found usually somewhere around the Screaming Cork tavern.", 'found_eskola_lead');
                        this.showNotification("Quest updated: The Three Vestigels");
                    }
                    this.modifyGrowthDecay(0, 10);
                    this.showNotification("Decay + 10");
                }
            },
            
            zerren_sporemind_appeal: {
                text: "'As an ally of the Sporemind Accord, I'm tracking down these Vestigels on their behalf. They consider this a matter of great importance to the balance of power in the region.'",
                options: [
                    { text: "Continue", next: "zerren_sporemind_success" }
                ]
            },
            
            zerren_sporemind_success: {
                text: "Zerren's eyes widen with recognition. 'Oh! You're with the Accord? Why didn't you say so?' She looks more at ease. 'The buyer was Edgar Eskola. He's a collector in the upper district. Quite wealthy and very interested in artifacts from beyond the Threshold.'",
                options: [
                    { text: "The Accord appreciates your cooperation", next: "zerren_quest_update" }
                ]
            },
            
            zerren_quest_update: {
                text: "'I hope you find what you're looking for. And please... if you see Edgar, don't mention I sent you. He values his privacy.' Zerren returns to arranging her merchandise, occasionally glancing in your direction.",
                options: [
                    { text: "Leave", next: "closeDialog" }
                ],
                onTrigger: () => {
                    // Update the quest
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && questSystem.getQuest('the_three_vestigels')) {
                        questSystem.updateQuest('the_three_vestigels', "Zerren revealed that Edgar Eskola purchased the plush toy containing a Vestigel. He can be found usually somewhere around the Screaming Cork tavern.", 'found_eskola_lead');
                        this.showNotification("Quest updated: The Three Vestigels");
                    }
                }
            }
        };
    }


    preload() {
        super.preload();
        this.load.image('voxmarketMarketBg', 'assets/images/backgrounds/VoxmarketMarket.png');
        this.load.image('arrow', 'assets/images/ui/door.png'); // Arrow for transition zones
        this.load.image('zerren', 'assets/images/characters/Zerren.png'); // Zerren NPC image
        // Audio is already loaded in GameScene's preload
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Play market theme
        this.playSceneMusic('marketTheme');
        
        // Set voxmarket market background
        const bg = this.add.image(400, 300, 'voxmarketMarketBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Create a custom ground for the market scene
        this.createMarketGround();
        
        // Completely hide the original ground
        if (this.ground) {
            this.ground.destroy(); // Destroy instead of just hiding
        }
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Position the priest at the center when entering this scene
        this.priest.x = 400;
        this.priest.y = 470; // Position on the ground
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }
        
        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
        
        // Create exit to VoxMarket at the bottom of the screen
        this.transitionManager.createTransitionZone(
            400, // x position
            550, // y position
            200, // width
            50, // height
            'down', // direction
            'VoxMarket', // target scene
            400, // walk to x
            520 // walk to y
        );
        
        // Add a hint about the exit
        const exitHint = this.add.text(400, 520, 'Back to Main Market', {
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
        
        // Remove the NPC if it exists
        if (this.stranger) {
            this.stranger.destroy();
        }
        
        // Create Zerren NPC
        this.zerren = this.add.sprite(200, 440, 'zerren');
        this.zerren.setScale(0.15);
        this.zerren.setDepth(5);
        this.zerren.setInteractive({ useHandCursor: true });
        
        // Add dialog interaction
        this.zerren.on('pointerdown', () => {
            if (this.dialogVisible) return;
            this.showDialog('zerren_start');
        });
        
        // Add a name tag above Zerren
        const zerrenTag = this.add.text(200, 420, 'Zerren', {
            fontSize: '14px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 5, y: 2 }
        });
        zerrenTag.setOrigin(0.5);
        zerrenTag.setDepth(6);
        
        // Initialize shop system for Zerren
        this.initShopSystem();
    }

    shutdown() {
        // Restore background music when leaving the scene
        this.restoreBackgroundMusic();
        
        // Clean up shop system
        if (this.shopSystem) {
            this.shopSystem.shutdown();
        }
        
        super.shutdown();
    }

    update() {
        // Call parent update for all standard mechanics
        super.update();
    }
    
    /**
     * Initialize the shop system with Zerren's inventory
     */
    initShopSystem() {
        // Check if player has completed quests to unlock special items
        const hasElphiBishopInfo = this.hasElphiBishopInfo();
        const questSystem = this.registry.get('questSystem');
        const findBishopActive = questSystem?.getQuest('find_bishop')?.isComplete;
        
        // Basic shop inventory
        const shopInventory = [
            {
                id: 'trinket_box',
                name: 'Ornate Trinket Box',
                description: 'A small decorative box with intricate fungal patterns.',
                price: 30,
                type: 'decoration',
            },
            {
                id: 'crystal_vial',
                name: 'Luminescent Crystal Vial',
                description: 'A vial containing glowing crystal fragments. Makes for pleasant ambient lighting.',
                price: 45,
                type: 'decoration',
            },
            {
                id: 'market_map',
                name: 'Voxmarket Map',
                description: 'A detailed map of Voxmarket and surrounding areas.',
                price: 15,
                type: 'tool',
            },
        ];
        
        // Add the Forgotten Elevator Button if player has learned about Bishop's connection to Dr. Elphi
        if (hasElphiBishopInfo) {
            shopInventory.push({
                id: 'forgotten_elevator_button',
                name: 'Forgotten Elevator Button',
                description: 'An old elevator button with strange markings. It seems to be for a floor that doesn\'t officially exist.',
                price: 75,
                type: 'key_item',
            });
        }
        
        // Create shop system
        this.shopSystem = new ShopSystem(this, {
            shopName: 'Zerren\'s Curios',
            inventory: shopInventory,
            position: {
                x: 400,
                y: 300
            },
            buyMultiplier: 1.0,
            sellMultiplier: 0.5
        });
        
        // Add journal entry about the Forgotten Elevator Button if it's available and find_bishop quest is active
        if (hasElphiBishopInfo && findBishopActive && !this.hasJournalEntry('forgotten_elevator_button_available')) {
            this.addJournalEntry(
                'forgotten_elevator_button_available',
                'Mysterious Button at Zerren\'s Shop',
                'Zerren has added a strange item to her inventory - a "Forgotten Elevator Button" with unusual markings. It appears to be for accessing a floor that doesn\'t officially exist. This might be useful for reaching Dr. Elphi\'s studio that the Bishop mentioned.',
                this.journalSystem.categories.ITEMS,
                { location: 'Voxmarket', character: 'Zerren' }
            );
            
            // Update the find_bishop quest
            questSystem.updateQuest('find_bishop', 'I found a Forgotten Elevator Button at Zerren\'s shop that might help me access Dr. Elphi\'s floor.', 'found_elevator_button');
            
            // Show a notification
            this.showNotification('New item available: Forgotten Elevator Button', 0x7fff8e);
        }
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

    shutdown() {
        this.restoreBackgroundMusic();
        super.shutdown();
    }
}
