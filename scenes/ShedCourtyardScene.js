import GameScene from './GameScene.js';
import QuestSystem from '../systems/QuestSystem.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';

export default class ShedCourtyardScene extends GameScene {
    constructor() {
        super({ key: 'ShedCourtyard' });
        this.isTransitioning = false;
        this._ortolan = null;
        this.journalSystem = JournalSystem.getInstance();
        this._ortholanDialogContent = {
            speaker: 'Ortholan',

            main: {
        
                text: "Ah, another visitor to this bureaucratic nightmare... *sigh* I've been here for days trying to get approval for an extra pair of arms. Do you know how hard it is to design complex board games with just two hands?",
                options: [
                    { text: "Why do you need extra arms?", next: "explain_need" },
                    { text: "Board games? What do you mean?", next: "board_games" },
                    { text: "Who are you?", next: "who_are_you" },
                    { text: "Good luck with that!", next: "goodbye" }
                ]
            },
            explain_need: {
        
                text: "Have you ever tried to playtest a complex strategy game by yourself? Moving pieces, managing resources, tracking multiple player states... It's a nightmare! With four arms, I could revolutionize solo playtesting. But the paperwork here... it's endless!",
                options: [
                    { text: "I could help you with the application process.", next: "start_quest" },
                    { text: "Sounds complicated. Good luck!", next: "goodbye" }
                ]
            },
            board_games: {
        
                text: "You did heard about a thing called a board game, didn't you? Well, I'm a best damn board game designer in this forsaken place. My games are not like the simple things for children you probably know, they provide a unique gameplay experience. With four arms, I can handle complex interactions and manage multiple player states more effectively. But the bureaucracy... it's a nightmare!",
                options: [
                    { text: "I could help you with the application process.", next: "start_quest" },
                    { text: "Who are you?", next: "who_are_you" },
                    { text: "Sounds complicated. Good luck!", next: "goodbye" }
                ]
            },
            who_are_you: {
        
                text: "I'm Ortolan Šmelc, a board game designer. I once served as a 'worldwright' during the era of table-top divination wars. My creations are literally microcosmic games—wooden boards sprouting tiny sentient pieces, enacting dramas and politics. You might heard from some calling me conservative, merely because I reject illusion-tech and mindplay, they are usualy morally unstable. Players are gods, but rules are sacred. ",
                options: [
                    { text: "Why do you need extra arms?", next: "explain_need" },
                    { text: "Table top divination wars? What do you mean?", next: "divination_wars" },
                    { text: "Sounds complicated. Good luck!", next: "goodbye" }
                ]
            },
            divination_wars: {
        
                text: "Ah, yes... terrible times. Maybe you should ask a historian about that. Or I can tell you more, but first I need to get out of this bureaucratic nightmare.",
                options: [
                    { text: "I could help you with the application process.", next: "start_quest" },
                    { text: "Sounds complicated. Good luck!", next: "goodbye" }
                ]
            },
            start_quest: {
                text: "Really? Oh, that would be wonderful! The main issue is getting through to the right department. They keep sending me between floors, and every clerk seems to need a different form. If you could help me track down the right paperwork and get it to the correct office, I'd be eternally grateful!",
                options: [
                    { text: "I'll see what I can do.", next: "accept_quest" }
                ],
                onTrigger: () => {
                    const questSystem = QuestSystem.getInstance();
                    if (!questSystem.getQuest('ortolan_arms')) {
                        questSystem.addQuest(
                            'ortolan_arms',
                            'Extra Arms for Ortolan',
                            'Help Ortolan, the board game designer, navigate the Shed\'s bureaucracy to get approval for an extra pair of arms.'
                        );
                        this.showNotification('Quest added: Extra Arms for Ortolan');
                    }
                }
            },
            accept_quest: {
                text: "Thank you! With your help, I'm sure we can navigate this bureaucratic maze. Come back when you have any progress to report!",
                options: [
                    { text: "I'll do my best.", next: "goodbye" }
                ]
            },
            quest_active: {
                text: "Still stuck in bureaucratic limbo... But I'm hopeful with your help we can get through this maze of paperwork!",
                options: [
                    { text: "I'll keep working on it.", next: "goodbye" },
                    { text: "See you later.", next: "goodbye" }
                ]
            },
            // Form submission dialogs
            give_artisan_form: {
        
                text: "An Artisan's Exemption Form?! This is perfect! Creative exemption from standard limb restrictions... exactly what I need! This form recognizes my work as a legitimate art form deserving of special consideration. You've saved me months of bureaucratic wrangling!",
                options: [
                    { text: "Happy to help.", next: "complete_quest_artisan" }
                ],
                onTrigger: () => {
                    // Remove the form from inventory
                    this.removeItemFromInventory('artisan-exemption-form');
                }
            },
            give_deformity_form: {
                text: "An Inherited Deformity Form? Hmm, not exactly how I'd describe my need for extra arms, but... it's approved! 'Beneficial mutation status' - I suppose that works. The classification is a bit insulting, but the result is what matters. Thank you for your help!",
                options: [
                    { text: "It's what I could get.", next: "complete_quest_deformity" }
                ],
                onTrigger: () => {
                    // Remove the form from inventory
                    this.removeItemFromInventory('deformity-form');
                }
            },
            give_special_dispensation: {
        
                text: "A Special Dispensation! How did you manage this? These are incredibly rare! Limb modification without standard documentation... this is even better than I hoped for! You must have impressed someone important. This will save me so much trouble!",
                options: [
                    { text: "Sometimes actions speak louder than words.", next: "complete_quest_dispensation" }
                ],
                onTrigger: () => {
                    // Remove the form from inventory
                    this.removeItemFromInventory('special-dispensation');
                }
            },
            give_temporary_permit: {
                text: "A Temporary Permit? Well... it's better than nothing, I suppose. Limited access is still access. I'll need to find a more permanent solution eventually, but this will at least let me start the process. Thank you for your efforts.",
                options: [
                    { text: "Sorry it's not better.", next: "complete_quest_temporary" }
                ],
                onTrigger: () => {
                    // Remove the form from inventory
                    this.removeItemFromInventory('temporary-permit');
                }
            },
            give_proxy_authorization: {
        
                text: "A Proxy Authorization? Interesting approach... This allows you to act on my behalf in bureaucratic matters. Not exactly what I was looking for, but potentially very useful. I could send you to handle future paperwork for me! Clever solution.",
                options: [
                    { text: "I can continue to help if needed.", next: "complete_quest_proxy" }
                ],
                onTrigger: () => {
                    // Remove the form from inventory
                    this.removeItemFromInventory('proxy-authorization');
                }
            },
            give_fungal_clearance: {
        
                text: "Fungal Research Clearance? I'm not sure how this helps with my extra arms situation... but wait, this might actually work! The mycologists have been experimenting with limb grafting. With this clearance, I could approach them directly about a fungal-based solution. Unconventional, but promising!",
                options: [
                    { text: "Sometimes you need to think outside the box.", next: "complete_quest_fungal" }
                ],
                onTrigger: () => {
                    // Remove the form from inventory
                    this.removeItemFromInventory('fungal-clearance');
                }
            },
            // Quest completion dialogs with rewards
            complete_quest_artisan: {
                text: "You've done me an incredible service! This form is exactly what I needed. As a token of my gratitude, please accept this prototype of my latest game. It's still in development, but the core mechanics are solid. The pieces respond to your thoughts - just be careful what you wish for!",
                options: [
                    { text: "Thank you, I'll treasure it.", next: "quest_completed" }
                ],
                onTrigger: () => {
                    this.completeQuest('ortolan_arms', 'artisan');
                    // Add game prototype to inventory
                    this.addItemToInventory({
                        id: 'game-prototype',
                        name: "Ortolan's Game Prototype",
                        description: "A prototype board game with semi-sentient pieces that respond to your thoughts. The rules seem to shift when you're not looking.",
                        stackable: false
                    });
                    this.showNotification('Received: Ortolan\'s Game Prototype');
                    // Growth reward
                    this.safeModifyGrowthDecay(5, 0);
                    this.showNotification('Growth +5: Mastered bureaucratic creativity');
                }
            },
            complete_quest_deformity: {
        
                text: "Well, it's not exactly how I'd describe myself, but it gets the job done! Thank you for your help. Here, take this special die I crafted. It has... unusual properties. Sometimes it shows numbers that don't exist, and occasionally predicts future rolls. Use it wisely.",
                options: [
                    { text: "Thank you for this gift.", next: "quest_completed" }
                ],
                onTrigger: () => {
                    this.completeQuest('ortolan_arms', 'deformity');
                    // Add special die to inventory
                    this.addItemToInventory({
                        id: 'probability-die',
                        name: "Probability-Bending Die",
                        description: "A strange die crafted by Ortolan that occasionally shows impossible numbers and seems to predict future rolls.",
                        stackable: false
                    });
                    this.showNotification('Received: Probability-Bending Die');
                    // Growth reward
                    this.safeModifyGrowthDecay(4, 0);
                    this.showNotification('Growth +4: Embraced beneficial mutation');
                }
            },
            complete_quest_dispensation: {
                text: "This is remarkable! A special dispensation is rare indeed. You've saved me months, possibly years of bureaucratic struggle. Please, take this game piece I've been working on. It's a special 'worldwright' piece that can alter the rules of any game it's placed in. Very useful for creative thinking.",
                options: [
                    { text: "It's beautiful, thank you.", next: "quest_completed" }
                ],
                onTrigger: () => {
                    this.completeQuest('ortolan_arms', 'dispensation');
                    // Add worldwright piece to inventory
                    this.addItemToInventory({
                        id: 'worldwright-piece',
                        name: "Worldwright Game Piece",
                        description: "A special game piece crafted by Ortolan that can alter the rules of any game it's placed in. It seems to glow faintly with possibility.",
                        stackable: false
                    });
                    this.showNotification('Received: Worldwright Game Piece');
                    // Growth reward
                    this.safeModifyGrowthDecay(6, 0);
                    this.showNotification('Growth +6: Transcended bureaucratic limitations');
                }
            },
            complete_quest_temporary: {
        
                text: "It's not ideal, but it's a start! I appreciate your efforts. Here, take this token - it's not much, but it might bring you a bit of luck. It's made from a special wood that seems to influence probability slightly in games of chance.",
                options: [
                    { text: "Thank you for the token.", next: "quest_completed" }
                ],
                onTrigger: () => {
                    this.completeQuest('ortolan_arms', 'temporary');
                    // Add luck token to inventory
                    this.addItemToInventory({
                        id: 'luck-token',
                        name: "Minor Luck Token",
                        description: "A simple wooden token crafted by Ortolan that seems to slightly influence probability in games of chance.",
                        stackable: true,
                        count: 3
                    });
                    this.showNotification('Received: 3 Minor Luck Tokens');
                    // Growth reward
                    this.safeModifyGrowthDecay(3, 0);
                    this.showNotification('Growth +3: Found temporary solutions');
                }
            },
            complete_quest_proxy: {
                text: "What an interesting solution! This could be very useful for future bureaucratic matters. As thanks, please take this strategy guide I wrote. It contains insights into game design that few understand, and might help you navigate complex systems - bureaucratic or otherwise.",
                options: [
                    { text: "I'll study it carefully.", next: "quest_completed" }
                ],
                onTrigger: () => {
                    this.completeQuest('ortolan_arms', 'proxy');
                    // Add strategy guide to inventory
                    this.addItemToInventory({
                        id: 'strategy-guide',
                        name: "Ortolan's Strategy Guide",
                        description: "A comprehensive guide to game design and strategy written by Ortolan. It contains insights that seem applicable to many complex systems.",
                        stackable: false
                    });
                    this.showNotification('Received: Ortolan\'s Strategy Guide');
                    // Growth reward
                    this.safeModifyGrowthDecay(4, 0);
                    this.showNotification('Growth +4: Mastered proxy representation');
                }
            },
            give_forged_permission: {
        
                text: "Is this... wait, this is a forgery! But... it's actually quite impressive. The seal looks authentic, the watermarks are perfect, and the signature... well, it's better than the real thing. Where did you get this?",
                options: [
                    { text: "From a specialist in the Screaming Cork.", next: "forged_reaction" },
                    { text: "I'd rather not say.", next: "forged_reaction" }
                ],
                onTrigger: () => {
                    // Remove the forged document from inventory
                    this.removeItemFromInventory('forged-arms-permission');
                }
            },
            forged_reaction: {
                text: "Well, I suppose I shouldn't look a gift horse in the mouth. This will certainly do the trick - the bureaucrats barely look at these forms anyway. They just check for the right seals and stamps. Though using a forgery does feel... morally questionable.",
                options: [
                    { text: "It's for a good cause.", next: "complete_quest_forged" },
                    { text: "Sorry about that.", next: "complete_quest_forged" }
                ]
            },
            complete_quest_forged: {
        
                text: "I suppose you're right. The bureaucracy here is absurd anyway. With this document, I can finally get the procedure approved! Thank you for your... creative solution. Here, take this special game piece I've been working on. It might bring you some luck in your endeavors.",
                options: [
                    { text: "Thank you for the gift.", next: "quest_completed" }
                ],
                onTrigger: () => {
                    // Complete quest with 'forged' completion type
                    this.completeQuest('ortolan_arms', 'forged');
                    
                    // Increase Decay due to using forged documents
                    this.safeModifyGrowthDecay(0, 15);
                    this.showNotification('Decay +15: Used forged documents');
                    
                    // Add special game piece to inventory
                    this.addItemToInventory({
                        id: 'fate-altering-piece',
                        name: "Fate-Altering Game Piece",
                        description: "A special game piece crafted by Ortolan that seems to subtly influence probability and fate when carried. It glows with a faint, unsettling light.",
                        stackable: false
                    });
                    this.showNotification('Received: Fate-Altering Game Piece');
                }
            },
            complete_quest_fungal: {
        
                text: "What an unexpected solution! The mycologists might be able to help me grow additional arms through fungal grafting. It's not what I had in mind, but I'm intrigued by the possibility. Here, take this special spore sample. It responds to creative thought - plant it somewhere and see what grows!",
                options: [
                    { text: "Thank you for this unusual gift.", next: "quest_completed" }
                ],
                onTrigger: () => {
                    this.completeQuest('ortolan_arms', 'fungal');
                    // Add creative spores to inventory
                    this.addItemToInventory({
                        id: 'creative-spores',
                        name: "Creative Thought Spores",
                        description: "A sample of unusual spores that respond to creative thought. When planted, they grow into structures that reflect the planter's imagination.",
                        stackable: true,
                        count: 5
                    });
                    this.showNotification('Received: Creative Thought Spores');
                    // Growth reward
                    this.safeModifyGrowthDecay(5, 0);
                    this.showNotification('Growth +5: Embraced fungal innovation');
                }
            },
            quest_completed: {
                text: "Thanks to you, I can finally pursue my vision for more complex game design! With these extra arms, my games will reach new heights of complexity and engagement. If you ever want to playtest something, come find me. I'll make sure you get a copy of my next creation!",
                options: [
                    { text: "I'll look forward to it.", next: "goodbye" },
                    { text: "Tell me more about your games.", next: "games_discussion" }
                ]
            },
            games_discussion: {
        
                text: "My games explore the boundaries between player and piece, between rules and reality. Each game is a microcosm with its own physics and logic. With these extra arms, I can now create games with multiple overlapping boards and simultaneous action! Imagine playing on three levels at once, with pieces that exist in multiple states...",
                options: [
                    { text: "Sounds fascinating.", next: "goodbye" }
                ]
            },
            goodbye: {
                text: "Don't get lost...",
                options: [],
                onTrigger: () => {
                    this.hideDialog();
                }
            }
        };
    }

    get dialogContent() {
        return this._ortholanDialogContent;
    }

    preload() {
        super.preload();
        this.load.image('courtyard-bg', 'assets/images/backgrounds/ShedMutationCourtyard.png');
        this.load.image('door', 'assets/images/ui/door.png');
        this.load.image('exitArea', 'assets/images/ui/exitArea.png');
        this.load.image('ortolan', 'assets/images/characters/Ortolan.png');
        this.load.image('particle', 'assets/images/effects/particle.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
    }

    create() {
        super.create();
        
        const bg = this.add.image(400, 300, 'courtyard-bg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        if (this.priest) {
            this.priest.x = 50;
            this.priest.y = 470;
            this.priest.setOrigin(0.5, 1);
            this.priest.play('idle');
        }

        // Add Ortolan
        this._ortolan = this.add.sprite(600, 520, 'ortolan');
        this._ortolan.setOrigin(0.5, 1);
        this._ortolan.setScale(0.15);
        this._ortolan.setInteractive({ useHandCursor: true });
        this._ortolan.on('pointerdown', () => {
            // Add journal entry when first meeting Ortolan
            if (!this.hasJournalEntry('ortolan_meeting')) {
                this.addJournalEntry(
                    'ortolan_meeting',
                    'Ortolan - The Board Game Designer',
                    'I met Ortolan, a board game developer. Ortolan designs complex board games and seeks approval for additional arms to better pursue this passion. The being seems both frustrated by and resigned to the city\'s labyrinthine processes, yet maintains a charming persistence in the face of absurd regulations.',
                    this.journalSystem.categories.PEOPLE,
                    { character: 'Ortolan', location: 'Shed 521 Courtyard' }
                );
            }
            this.showOrtholanDialog();
        });

        // Add idle animation for Ortolan
        this.tweens.add({
            targets: this._ortolan,
            y: this._ortolan.y - 3,
            duration: 2000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Random head movements
        this.time.addEvent({
            delay: 5000,
            callback: () => {
                if (Math.random() > 0.5) {
                    this.tweens.add({
                        targets: this._ortolan,
                        angle: Phaser.Math.Between(-5, 5),
                        duration: 1000,
                        ease: 'Sine.easeInOut',
                        yoyo: true
                    });
                }
            },
            loop: true
        });

        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Create exit to Shed521GateScene at the left edge
        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            50, // width
            200, // height
            'left', // direction
            'Shed521GateScene', // target scene
            20, // walk to x
            470 // walk to y
        );

        // Exit area cursor handling is now managed by SceneTransitionManager
    }
    
    // Helper method to remove an item from inventory
    removeItemFromInventory(itemId) {
        const inventory = this.registry.get('inventory');
        if (!inventory || !inventory.items) return;
        
        const itemIndex = inventory.items.findIndex(item => item.id === itemId);
        if (itemIndex !== -1) {
            // Remove the item
            inventory.items.splice(itemIndex, 1);
            // Update the registry
            this.registry.set('inventory', inventory);
        }
    }
    
    // Helper method to add an item to inventory
    addItemToInventory(item) {
        const inventory = this.registry.get('inventory');
        if (!inventory) return;
        
        // Check if item is stackable and already exists
        if (item.stackable) {
            const existingItem = inventory.items.find(i => i.id === item.id);
            if (existingItem) {
                existingItem.count = (existingItem.count || 1) + (item.count || 1);
                this.registry.set('inventory', inventory);
                return;
            }
        }
        
        // Add new item if there's space
        if (inventory.items.length < inventory.maxItems) {
            inventory.items.push(item);
            this.registry.set('inventory', inventory);
        } else {
            this.showNotification('Inventory is full!');
        }
    }
    
    // Safe version of modifyGrowthDecay that doesn't rely on the UI indicator
    safeModifyGrowthDecay(growthChange, decayChange) {
        // Get the growth/decay system from registry
        const growthDecaySystem = this.registry.get('growthDecaySystem');
        if (growthDecaySystem) {
            // Directly modify the system without relying on UI updates
            growthDecaySystem.modifyBalance(growthChange, decayChange);
        }
    }
    
    // Helper method to complete the quest
    completeQuest(questId, completionType) {
        const questSystem = QuestSystem.getInstance();
        if (!questSystem) return;
        
        const quest = questSystem.getQuest(questId);
        if (!quest) return;
        
        // Update quest status to completed
        questSystem.updateQuest(
            questId,
            `You successfully helped Ortolan obtain approval for extra arms through a ${completionType} form. He can now pursue his board game design with greater efficiency.`,
            'completed'
        );
        questSystem.completeQuest(questId);
        // Show notification
        this.showNotification('Quest completed: Extra Arms for Ortolan');
        
        // Visual celebration effect
        this.createCompletionEffect();
    }
    
    // Create a visual celebration effect for quest completion
    createCompletionEffect() {
        // Create particles for celebration
        const particles = this.add.particles('particle', {
            x: this._ortolan.x,
            y: this._ortolan.y - 50,
            speed: { min: 50, max: 100 },
            angle: { min: 0, max: 360 },
            scale: { start: 0.5, end: 0 },
            lifespan: 1000,
            blendMode: 'ADD',
            frequency: 50,
            quantity: 10,
            tint: [0x7fff8e, 0xffffff]
        });
        
        // Stop emitting after 1 second
        this.time.delayedCall(1000, () => {
            particles.destroy();
        });
    }

    showOrtholanDialog() {
        const questSystem = QuestSystem.getInstance();
        const ortholanQuest = questSystem.getQuest('ortolan_arms');
        const inventory = this.registry.get('inventory');

        if (!ortholanQuest) {
            // Quest not started yet
            this.showDialog('main');
            return;
        }

        // Check if the quest is already completed
        if (ortholanQuest.status === 'completed') {
            this.showDialog('quest_completed');
            return;
        }

        // Check if player has any of the forms in their inventory
        const hasArtisanForm = inventory?.items.some(item => item.id === 'artisan-exemption-form');
        const hasDeformityForm = inventory?.items.some(item => item.id === 'deformity-form');
        const hasSpecialDispensation = inventory?.items.some(item => item.id === 'special-dispensation');
        const hasTemporaryPermit = inventory?.items.some(item => item.id === 'temporary-permit');
        const hasProxyAuthorization = inventory?.items.some(item => item.id === 'proxy-authorization');
        const hasFungalClearance = inventory?.items.some(item => item.id === 'fungal-clearance');

        // Update dialog options based on forms in inventory
        const dialogOptions = [
            { text: "I'll keep working on it.", next: "goodbye" },
            { text: "See you later.", next: "goodbye" }
        ];

        // Check for forged document from Ravla
        const hasForgedPermission = inventory?.items.some(item => item.id === 'forged-arms-permission');
        
        if (hasForgedPermission) {
            dialogOptions.unshift({ text: "I have a forged Multiple Arms Permission for you.", next: "give_forged_permission" });
        }
        if (hasArtisanForm) {
            dialogOptions.unshift({ text: "I have an Artisan's Exemption Form for you.", next: "give_artisan_form" });
        }
        if (hasDeformityForm) {
            dialogOptions.unshift({ text: "I have an Inherited Deformity Form for you.", next: "give_deformity_form" });
        }
        if (hasSpecialDispensation) {
            dialogOptions.unshift({ text: "I have a Special Dispensation for you.", next: "give_special_dispensation" });
        }
        if (hasTemporaryPermit) {
            dialogOptions.unshift({ text: "I have a Temporary Permit for you.", next: "give_temporary_permit" });
        }
        if (hasProxyAuthorization) {
            dialogOptions.unshift({ text: "I have a Proxy Authorization for you.", next: "give_proxy_authorization" });
        }
        if (hasFungalClearance) {
            dialogOptions.unshift({ text: "I have a Fungal Research Clearance for you.", next: "give_fungal_clearance" });
        }

        // Set the dialog options
        this._ortholanDialogContent.quest_active.options = dialogOptions;
        
        // Show the dialog
        this.showDialog('quest_active');
    }
}
