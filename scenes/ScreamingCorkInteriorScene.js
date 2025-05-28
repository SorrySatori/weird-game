import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import ShopSystem from '../systems/items/ShopSystem.js';

export default class ScreamingCorkInteriorScene extends GameScene {
    constructor() {
        super({ key: 'ScreamingCorkInteriorScene' });
        this.isTransitioning = false;
        this.shopSystem = null;
    }

    get dialogContent() {
        return {
            ...super.dialogContent, // Include parent dialog content for symbiont dialogs
            
            // Ravla dialog - the forger
            ravla_start: {
                text: "Ravla looks up from her work, eyes sharp and calculating. \"Need something? I'm busy, so make it quick.\"",
                options: [
                    { text: "Who are you?", next: "ravla_who" },
                    { text: "What do you do here?", next: "ravla_job" },
                    { text: "Nevermind", next: "closeDialog" }
                ]
            },
            ravla_who: {
                text: "Name's Ravla. I'm an... artist of sorts. Been at the Cork for years now. It's quiet, keeps the authorities at a distance.",
                options: [
                    { text: "Back", next: "ravla_start" }
                ]
            },
            ravla_job: {
                text: "I provide services for those who need certain... paperwork adjusted. Nothing illegal, of course. Just creative interpretations of bureaucratic necessities.",
                options: [
                    { text: "I need some documents...", next: "ravla_documents" },
                    { text: "Back", next: "ravla_start" }
                ]
            },
            ravla_documents: {
                text: "Hmm. What kind of documents are we talking about? I don't work for free, and I don't work for just anyone.",
                options: [
                    { text: "Just curious", next: "ravla_curious" },
                    { text: "I need help with Shed 13 paperwork", next: "ravla_shed13" },
                    ...(this.registry.get('questSystem')?.getQuest('ortolan_arms')?.updates.some(update => update.key === 'forge_documents_suggestion') ? [
                        { text: "I need help with Ortolan's paperwork", next: "ravla_ortolan" }
                    ] : [])
                ]
            },
            ravla_curious: {
                text: "Curiosity is expensive in this city. Come back when you have real business.",
                options: [
                    { text: "Back", next: "ravla_start" }
                ]
            },
            ravla_shed13: {
                text: "Shed 13? Those bureaucrats are the worst. Their forms change weekly, and the security features are a nightmare. It'll cost you.",
                options: [
                    { text: "How much?", next: "ravla_cost" },
                    { text: "Back", next: "ravla_start" }
                ]
            },
            ravla_cost: {
                text: "For Shed 13? 500 credits minimum. Plus whatever materials I need to source. Come back when you have the money.",
                options: [
                    { text: "I'll think about it", next: "ravla_start" }
                ]
            },
            ravla_ortolan: {
                text: "Artisan's Exemption Form? For Ortolan? Interesting. Those forms have special seals that are hard to duplicate. But... I might be able to help.",
                options: [
                    { text: "What would you need?", next: "ravla_ortolan_need" },
                    { text: "Back", next: "ravla_start" }
                ]
            },
            ravla_ortolan_need: {
                text: "I'd need to see an original first. Even an expired one. And it won't be cheap - 300 credits. But I can make it perfect. No one would know the difference.",
                options: [
                    { text: "I'll find an original", next: "ravla_ortolan_agree" },
                    { text: "That's too expensive", next: "ravla_start" }
                ]
            },
            ravla_ortolan_agree: {
                text: "Good. Find me an original, bring the credits, and I'll have it ready in no time. Just don't tell anyone where you got it.",
                options: [
                    { text: "Deal", next: "closeDialog" }
                ],
                onTrigger: () => {
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem) {
                        questSystem.updateQuest('ortolan_arms', 'Ravla at the Screaming Cork can forge the Artisan\'s Exemption Form for Ortolan, but she needs to see an original first and wants 300 credits for the job.', 'ravla_forger_agreement');
                        this.showNotification('Quest updated: Ortolan Arms Investigation');
                    }
                }
            },
            
            // Heliodor dialog
            heliodor_start: {
                text: "Heliodor nods politely. \"Welcome to the Screaming Cork. First time? The name's a bit misleading - it's actually quite peaceful most nights.\"",
                options: [
                    { text: "Who are you?", next: "heliodor_who" },
                    { text: "Tell me about this place", next: "heliodor_place" },
                    { text: "Heard any rumors lately?", next: "heliodor_rumors" },
                    {
                      text: "Do you have anything for sale?",
                      next: 'openShop'
                    },
                    { text: "Goodbye", next: "closeDialog" }
                ]
            },
            heliodor_who: {
                text: "We are Heliodor. We keep an eye on things here, make sure everyone behaves.",
                options: [
                    { text: "Back", next: "heliodor_start" }
                ]
            },
            heliodor_place: {
                text: "The Screaming Cork's been here longer than most of the city. Owner claims it was the first building erected after the Collapse. Doubt that's true, but it's certainly old. Good place to disappear for a while.",
                options: [
                    { text: "Back", next: "heliodor_start" }
                ]
            },
            heliodor_rumors: {
                text: "Hmm. Word is the Rust Choir minions are getting more aggressive with their territory. And there's something strange happening at the Cathedral.",
                options: [
                    { text: "Anything else?", next: "heliodor_more_rumors" },
                    { text: "Back", next: "heliodor_start" }
                ]
            },
            heliodor_more_rumors: {
                text: "Well, if you're interested in less savory information... that woman in the corner, Ravla? She's the best document forger in the district. Just don't tell her I told you.",
                options: [
                    { text: "Thanks for the tip", next: "heliodor_start" }
                ],
                onTrigger: () => {
                    // Add a hint about Ravla to any relevant quests
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem) {
                        const quest = questSystem.getQuest('ortolan_arms');
                        if (quest && !quest.updates.some(update => update.key === 'ravla_forger_hint')) {
                            questSystem.updateQuest('ortolan_arms', 'Heliodor at the Screaming Cork mentioned that Ravla is a skilled document forger. She might be able to help with the Ortolan situation.', 'ravla_forger_hint');
                            this.showNotification('Quest updated: Ortolan Arms Investigation');
                        }
                    }
                }
            },
            openShop: {
                text: "Take your time browsing. Quality goods at fair prices!",
                options: [
                    {
                        text: "[Open Shop Interface]",
                        next: 'shopInterface'
                    },
                    {
                        text: "Actually, nevermind.",
                        next: 'closeDialog'
                    }
                ]
            },
            shopInterface: {
                text: "",
                options: [],
                onShow: () => {
                    this.hideDialog();
                    if (this.shopSystem) {
                        this.shopSystem.open();
                    }
                }
            },
            heliodorMerchandise: {
                text: "I have connections with traders from all over. Some items come from distant lands, others from local craftsmen. I pride myself on offering only the finest goods.",
                options: [
                    {
                        text: "Show me what you have for sale.",
                        next: 'openShop'
                    },
                    {
                        text: "I'll come back later.",
                        next: 'closeDialog'
                    }
                ]
            },
        };
    }

    preload() {
        super.preload();
        this.load.image('screamingCorkInteriorBg', 'assets/images/ScreamingCorkInterior.png');
        this.load.image('arrow', 'assets/images/arrow.png');
        
        // Load NPC sprites as static images first to ensure they exist
        this.load.image('ravla_static', 'assets/images/ravla.png');
        this.load.image('heliodor_static', 'assets/images/heliodor.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set background
        const bg = this.add.image(400, 300, 'screamingCorkInteriorBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Position the priest at the entrance
        this.priest.x = 100;
        this.priest.y = 470;
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
        
        // Create exit back to ScreamingCorkScene at the left edge
        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            80, // width
            200, // height
            'left', // direction
            'ScreamingCorkScene', // target scene
            50, // walk to x
            470 // walk to y
        );
        
        // Create NPCs
        this.createNPCs();
    }
    
    createNPCs() {
        // Create Ravla NPC (the forger) using static image
        this.ravla = this.add.image(700, 470, 'ravla_static');
        this.ravla.setScale(0.125); // Further reduced scale to make sprite more proportional
        this.ravla.setDepth(5);
        this.ravla.setInteractive({ useHandCursor: true });
        
        // Create Heliodor NPC using static image
        this.heliodor = this.add.image(300, 470, 'heliodor_static');
        this.heliodor.setScale(0.125); // Further reduced scale to make sprite more proportional
        this.heliodor.setDepth(5);
        this.heliodor.setInteractive({ useHandCursor: true });
        
        // Initialize shop system
        this.initShopSystem();
        
        // Add dialog interactions
        this.ravla.on('pointerdown', () => {
            if (this.dialogVisible) return;
            this.showDialog('ravla_start');
        });
        
        this.heliodor.on('pointerdown', () => {
            if (this.dialogVisible) return;
            this.showDialog('heliodor_start');
        });
        
        // Add simple movement for NPCs
        this.addNPCMovement();
    }
    
    // We're using static images instead of animations for now
    createNPCAnimations() {
        // No animations needed as we're using static images
    }
    
    addNPCMovement() {
        // Ravla subtle wobble animation
        this.addWobbleEffect(this.ravla, 600, 450);
        
        // Heliodor subtle wobble animation
        this.addWobbleEffect(this.heliodor, 400, 430);
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

    update() {
        super.update();
        
        // Update money display if needed
        if (this.shopSystem && this.shopSystem.isOpen) {
            this.shopSystem.updateMoneyDisplay();
        }
    }
    
    /**
     * Initialize the shop system with inventory
     */
    initShopSystem() {
        // Sample shop inventory
        const shopInventory = [
            {
                id: 'pliers',
                name: 'Pliers',
                description: 'A pair of pliers. Useful for repairing or extracting.',
                price: 25,
                type: 'tool',
            },

        ];
        
        // Create shop system
        this.shopSystem = new ShopSystem(this, {
            shopName: 'Screaming Cork Shop',
            inventory: shopInventory,
            position: {
                x: 400,
                y: 300
            },
            buyMultiplier: 1.0,
            sellMultiplier: 0.5
        });
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.ScreamingCorkInteriorScene = ScreamingCorkInteriorScene;
}
