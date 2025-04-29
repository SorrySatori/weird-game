import GameScene from './GameScene.js';

export default class Shed13Scene extends GameScene {
    constructor() {
        super({ key: 'Shed13Scene' });
        this.isTransitioning = false;
        this.visitedDialogs = new Set();
        
        // Store all dialog content in a separate property
        this._dialogContent = {
            start: {
                text: "Another stray wanderin' down the veins of Shed13...\nWhat're you lookin' for, outsider? Body upgrade? New lungs? Or just bad ideas?\nHe chuckles, voice crackling like a broken choir.\nSay your need. Maybe ol' Gnur's got a whisper to sell.",
                options: [
                    { text: "Who are you exactly?", next: "background" },
                    { text: "I'm looking for the Bishop. Have you seen her?", next: "bishop" },
                    { text: "Goodbye", next: "end" }
                ]
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
                text: "Heh... brave words from soft lungs. But here,  threats are like throwing paper at iron walls. (His voice lowers dangerously.) You want answers? You bring me value. You bring me rust that sings. Or you'll leave here empty, maybe even emptier.",
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
                text: "Now that is a tune I can hum to.Shed13's 3rd Sublevel got swallowed when the fold pressure rose.There's a derelict core I need pulled out — still breathing, barely.\n(He hands you a jagged scrap map.) Find it, and maybe I'll find my memory about your Bishop friend.",
                options: [
                    { text: "Back to other topics", next: "start" }
                ]
            },
            end: {
                text: "Come back if you need anything... unusual.",
                options: []
            }
        };
    }

    get dialogContent() {
        // Filter dialog options based on visited states and quest status
        const questSystem = this.registry.get('questSystem');
        const hasFindBishopQuest = questSystem?.quests?.has('find_bishop');

        // Filter options based on conditions
        const content = JSON.parse(JSON.stringify(this._dialogContent)); // Deep clone
        
        // Modify start options
        content.start.options = this.visitedDialogs.has('recoverTech') ?
            []
            :
            [
                { text: "Who are you exactly?", next: "background" },
                ...(hasFindBishopQuest ? [{ text: "I'm looking for the Bishop. Have you seen her?", next: "bishop" }] : []),
                { text: "Goodbye", next: "end" }
            ]

        // Filter background optionqs
        if (this.visitedDialogs.has('rustChoir')) {
            content.background.options = [
                { text: "Back to other topics", next: "start" }
            ];
        }

        return content;
    }

    showDialog(dialogKey) {
        // Handle faction reputation changes
        if (dialogKey === 'rustChoir' || dialogKey === 'brukk') {
            this.modifyFactionReputation('RustChoir', 10);
        }

        // Handle quest updates
        const questSystem = this.registry.get('questSystem');
        if (questSystem) {
            if (dialogKey === 'bishop' && questSystem.quests.has('find_bishop')) {
                questSystem.updateQuest('find_bishop', "The Bishop was seen at Scraper 1140, making an unusual trade involving a 'game lens'. Gnur might know more, but he wants something in return.");
                this.showNotification('Quest Updated: Find Bishop');
            } else if (dialogKey === 'recoverTech') {
                this.questSystem.addQuest(
                    'rust_reclamation',
                    'Rust Reclamation',
                    "Gnur needs help recovering a 'living core' from Shed13's 3rd Sublevel. The area was swallowed by fold pressure, making this a dangerous but potentially rewarding task.",
                );
                this.showNotification('New Quest: Rust Reclamation');
                this.modifyGrowthDecay(1, 0);
            }
        }

        // Track visited dialogs
        this.visitedDialogs.add(dialogKey);

        if (this.visitedDialogs.has('recoverTech'))
            this._dialogContent.start.text = "Just bring me the living core, then I will talk more"

        // Show the dialog content
        super.showDialog(dialogKey);
    }

    preload() {
        super.preload();
        this.load.image('shed13Bg', 'assets/images/Shed13.png');
        this.load.image('exitArea', 'assets/images/door.png');
        this.load.image('mysteriousSpore', 'assets/images/spore.png');
        // Load Gnur sprite
        this.load.image('gnur', './assets/images/Gnur.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set shed13 background
        const bg = this.add.image(400, 300, 'shed13Bg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Add Gnur NPC with proper size
        this.gnur = this.add.sprite(400, 470, 'gnur');
        this.gnur.setDisplaySize(80, 80); // Set a fixed size
        this.gnur.setDepth(1); // Ensure it's above background
        this.gnur.setInteractive({ useHandCursor: true });
        
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
        
        // Add interaction with Gnur
        this.gnur.on('pointerdown', () => {
            if (!this.dialogVisible) {
                this.dialogState = 'start';
                this.showDialog(this.dialogState);
            }
        });
        
        // Handle cursor visibility for Gnur
        this.gnur.on('pointerover', () => {
            this.cursor.setAlpha(0);
        });
        
        this.gnur.on('pointerout', () => {
            this.cursor.setAlpha(0.8);
        });

        // Add a collectable spore
        const spore = this.add.image(300, 450, 'mysteriousSpore');
        spore.setScale(0.5);
        // Add a subtle glow effect
        spore.preFX.addGlow(0x7fff8e, 4, 0, false, 0.5, 16);
        
        // Make the spore collectable with description
        this.makeItemCollectable({
            id: 'mysterious_spore',
            name: 'Mysterious Spore',
            description: 'A peculiar spore found in Shed13. It pulses with an otherworldly energy.',
            spriteKey: 'mysteriousSpore',
            stackable: true
        }, spore);
        
        // Add invisible clickable exit area at the right side
        this.exitArea = this.add.image(750, 470, 'exitArea')
            .setDisplaySize(40, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);
        
        // Position the priest at the left side when entering
        this.priest.x = 100;
        this.priest.y = 470;
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // Exit area click handler
        this.exitArea.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            priest.play('walk');
            this.tweens.killTweensOf(priest);

            this.tweens.add({
                targets: priest,
                x: 750,
                y: 470,
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('CrossroadScene');
                    });
                }
            });
        });
    }

    update() {
        super.update();
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.Shed13Scene = Shed13Scene;
}
