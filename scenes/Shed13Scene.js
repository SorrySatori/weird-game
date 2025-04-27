import GameScene from './GameScene.js';

export default class Shed13Scene extends GameScene {
    constructor() {
        super({ key: 'Shed13Scene' });
        this.isTransitioning = false;
        this.visitedDialogs = new Set();
    }

    get dialogContent() {
        return {
            start: {
                text: "Another stray wanderin' down the veins of Shed13...\nWhat're you lookin' for, outsider? Body upgrade? New lungs? Or just bad ideas?\nHe chuckles, voice crackling like a broken choir.\nSay your need. Maybe ol' Gnur's got a whisper to sell.",
                options: [
                    { text: "Who are you exactly?", next: "background" },
                    { text: "I'm looking for the Bishop of Threshold. Have you seen her?", next: "bishop" },
                    { text: "Goodbye", next: "end" }
                ]
            },
            background: {
                text: "Used to keep the machines running in the old days. Now I'm with the Rust Choir. We sing the old machines awake... or lull the new flesh to sleep. Depends who's buying.",
                options: [
                    ...(this.visitedDialogs.has('rustChoir') ? [] : [{ text: "Tell me about the Rust Choir", next: "rustChoir" }]),
                    { text: "Back to other topics", next: "start" }
                ]
            },
            rustChoir: {
                text: "We celebrate entropy, collapse as transformation, we... worship 'final songs'. We like to trade in secrets, especially old tech. If you are interested to know more, visit the old Scraper and talk to Brukk's people.",
                options: [
                    ...(this.visitedDialogs.has('brukk') ? [] : [{ text: "Who is Brukk?", next: "brukk" }]),
                    { text: "Back to other topics", next: "start" }
                ],
                onVisit: () => {
                    this.visitedDialogs.add('rustChoir');
                    this.modifyFactionReputation('RustChoir', 10);
                }
            },
            brukk: {
                text: "Brukk is our leader if we had any... He is the keeper of the old tech, the one who can help you find what you're looking for. That's all I can tell you.",
                options: [
                    { text: "Back to other topics", next: "start" }
                ],
                onVisit: () => {
                    this.visitedDialogs.add('brukk');
                    this.modifyFactionReputation('RustChoir', 10);
                }
            },
            bishop: {
                text: "Ahhh, the shrouded one... yeah, she passed through, glimmer-eyed and restless. But info ain't free, friend.",
                options: [
                    { text: "What do you want?", next: "rustReclamation" },
                    ...(this.visitedDialogs.has('threat') ? [] : [{ text: "Give me the answer. Right now... or else.", next: "threat" }]),
                    ...(this.visitedDialogs.has('recoverTech') ? [] : [{ text: "I can help you recover tech carefully.", next: "recoverTech" }]),
                    { text: "Back to other topics", next: "start" }
                ]
            },
            threat: {
                text: "Heh... brave words from soft lungs.\nBut here, threats are like throwing paper at iron walls.\n(His voice lowers dangerously.)\nYou want answers? You bring me value. You bring me rust that sings.\nOr you'll leave here empty, maybe even emptier.",
                options: [
                    { text: "What do you want?", next: "rustReclamation" },
                    { text: "Back to other topics", next: "start" }
                ],
                onVisit: () => {
                    this.visitedDialogs.add('threat');
                    this.modifyGrowthDecay(0, 1);
                }
            },
            recoverTech: {
                text: "Now that is a tune I can hum to.\nShed13's 3rd Sublevel got swallowed when the fold pressure rose.*\nThere's a derelict core I need pulled out — still breathing, barely.\n(He hands you a jagged scrap map.)\nFind it, and maybe I'll find my memory about your Bishop friend.",
                options: [
                    ...(this.visitedDialogs.has('rustReclamation') ? [] : [{ text: "Tell me about the Rust Reclamation", next: "rustReclamation" }]),
                    { text: "Back to other topics", next: "start" }
                ],
                onVisit: () => {
                    if (!this.visitedDialogs.has('recoverTech')) {
                        this.visitedDialogs.add('recoverTech');
                        this.visitedDialogs.add('threat'); // Remove threat option
                        this.modifyGrowthDecay(1, 0);
                    }
                }
            },
            rustReclamation: {
                text: "Actually, there is something you can do for me. As a favor, I can tell you more about where I saw the bishop lately.",
                options: [
                    { text: "Ok, tell me more", next: "recoverTech" },
                    { text: "Back to other topics", next: "start" }
                ],
                onVisit: () => {
                    this.visitedDialogs.add('rustReclamation');
                }
            },
            end: {
                text: "Come back if you need anything... unusual.",
                options: []
            }
        };
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
        
        // Update priest's staff position (facing right)
        this.updateStaffPosition(1);
        
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

    showDialog(state) {
        const dialogState = this.dialogContent[state];
        if (dialogState.onVisit) {
            dialogState.onVisit();
        }
        super.showDialog(state);
    }

    update() {
        super.update();
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.Shed13Scene = Shed13Scene;
}
