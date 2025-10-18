import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';

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
        
        const content = {
            ...super.dialogContent,
            speaker: 'Gruk',
            start: {
                text: this._dialogTextCache.start || "Another stray wanderin' down the veins of Shed521...\nWhat're you lookin' for, outsider? Body upgrade? New lungs? Or just bad ideas?\nHe chuckles, voice crackling like a broken choir.\nSay your need. Maybe ol' Gnur's got a whisper to sell.",
                options: [
                    { text: "Who are you exactly?", next: "background" },
                    // Add the option to confront Gnur about lying if player made the promise
                    ...(promiseMade ? [{ text: "About that living core... you lied to me.", next: "confront_about_lie" }] : []),
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
            background: {
                text: "Used to keep the machines running in the old days. Now I'm with the Rust Choir. We sing the old machines awake... or lull the new flesh to sleep. Depends who's buying.",
                options: [
                    { text: "Tell me about the Rust Choir", next: "rustChoir" },
                    { text: "Back to other topics", next: "start" }
                ]
            },
            rustChoir: {
                text: "We celebrate entropy, collapse as transformation, we... worship 'final songs'. We like to trade in secrets, especially old tech. If you are interested to know more, visit the old Scraper and talk to Brukk's people.",
                options: [
                    { text: "Who is Brukk?", next: "brukk" },
                    { text: "Back to other topics", next: "start" }
                ]
            },
            brukk: {
                text: "Brukk is our leader if we had any... He is the keeper of the old tech, the one who can help you find what you're looking for. That's all I can tell you.",
                options: [
                    { text: "Back to other topics", next: "start" }
                ]
            },
            bishop: {
                text: "Ahhh, the shrouded one... yeah, she passed through, glimmer-eyed and restless. But info ain't free, friend.",
                options: [
                    { text: "What do you want?", next: "rustReclamation" },
                    { text: "I can help you recover old tech carefully", next: "recoverTech" },
                    { text: 'Tell me what I want to know... or else.', next: 'threat'},
                    { text: "Back to other topics", next: "start" }
                ]
            },
            threat: {
                text: "Heh... brave words from soft lungs. But here, threats are like throwing paper at iron walls. (His voice lowers dangerously.) You want answers? You bring me value. You bring me rust that sings. Or you'll leave here empty, maybe even emptier.",
                options: [
                    { text: "Ok, tell me more", next: "recoverTech" },
                    { text: "Back to other topics", next: "start" }
                ]
            },
            rustReclamation: {
                text: "Actually, there is something you can do for me. As a favor, I can tell you more about where I saw the bishop lately.",
                options: [
                    { text: "Ok, tell me more", next: "recoverTech" },
                    { text: "Back to other topics", next: "start" }
                ]
            },
            recoverTech: {
                text: "Now that is a tune I can hum to. Somewhere at Shed 521 there's an abandoned office, leading to unused tunnels. There's a derelict core I need pulled out — still breathing, barely.\n Find it, and maybe I'll find my memory about your Bishop friend.",
                options: [
                    { text: "Back to other topics", next: "start" }
                ]
            },
            complete_quest: {
                text: "Ah... the living core. (His eyes glimmer with an unsettling light as he takes the artifact.) Yes, this will sing beautifully in our choir.\n\nAs promised, about your Bishop... She was quite interested in Dr. Elphi's work. Last I heard, she made her way to Scraper 1140 to meet with the good doctor herself. Seemed... urgent.",
                options: [
                    { text: "Thank you for the information", next: "complete_quest_end" }
                ],
            },
            complete_quest_end: {
                text: "(Gnur returns to his work, humming a strange metallic tune.)",
                options: [
                    { text: "Leave", next: "end" }
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
                    { text: "The clerk told me it's crucial for the Shed's energy maintenance. I won't help you sabotage it.", next: "refuse_quest" },
                    { text: "Never mind, I'll still get it for you.", next: "complete_quest" }
                ]
            },
            refuse_quest: {
                text: "(Gnur's eyes narrow to slits, a metallic growl escaping his throat)\n\nSo you've been talkin' to the paper-pushers, eh? Should've known better than to trust an outsider. Get out of my sight before I decide your lungs would make a fine addition to my collection.",
                options: [
                    { text: "Leave", next: "end" }
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
            }
        }

        // Handle quest updates
        const questSystem = this.registry.get('questSystem');
        if (questSystem) {
            if (dialogKey === 'bishop' && questSystem.quests.has('find_bishop')) {
                questSystem.updateQuest('find_bishop', "The Bishop was seen at Scraper 1140, making an unusual trade involving a 'game lens'. Gnur might know more, but he wants something in return.", 'bishop_clue_gnur');
                this.showNotification('Quest updated: Find the Bishop of Threshold');
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

        // Add Gnur NPC with proper size
        this.gnur = this.add.sprite(400, 470, 'gnur');
        this.gnur.setDisplaySize(80, 80); // Set a fixed size
        this.gnur.setDepth(1); // Ensure it's above background
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
