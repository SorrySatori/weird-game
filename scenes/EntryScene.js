class EntryScene extends GameScene {
    constructor() {
        super({ key: 'EntryScene' });
    }

    preload() {
        super.preload();
        // Load any EntryScene-specific assets here
    }

    create() {
        this.createCityBackground();
        this.initSceneMechanics();
        this.createStranger();
        
        // Start background music
        this.playSceneMusic('backgroundMusic');
    }

    createCityBackground() {
        // Add the city background
        const bg = this.add.image(400, 300, 'cityBackground');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
    }

    createStranger() {
        // Add the mysterious stranger character
        this.stranger = this.add.sprite(600, 470, 'stranger');
        this.stranger.setScale(2);
        this.stranger.setInteractive({ useHandCursor: true });
        
        // Handle cursor visibility for stranger
        this.input.on('gameobjectover', (pointer, gameObject) => {
            if (gameObject === this.stranger) {
                this.cursor.setAlpha(0);
            }
        });
        
        this.input.on('gameobjectout', (pointer, gameObject) => {
            if (gameObject === this.stranger) {
                this.cursor.setAlpha(0.8);
            }
        });
        
        // Create NPC idle animation
        this.anims.create({
            key: 'stranger-idle',
            frames: this.anims.generateFrameNumbers('stranger', { start: 0, end: 3 }),
            frameRate: 4,
            repeat: -1
        });
        
        this.stranger.play('stranger-idle');
        
        // Add click handler for NPC
        this.stranger.on('pointerdown', () => {
            if (!this.dialogVisible) {
                this.clickSound.play();
                this.showDialog('main');
            }
        });
    }

    update() {
        super.update();
        
        // Check if priest reaches right edge (adjusted threshold)
        if (this.priest && this.priest.x >= 750 && !this.isTransitioning) {
            this.isTransitioning = true;
            this.cameras.main.fadeOut(800, 0, 0, 0);
            this.cameras.main.once('camerafadeoutcomplete', () => {
                this.scene.start('EggCatedralScene');
                this.isTransitioning = false;
            });
        }
    }

    // Override dialogContent to provide EntryScene-specific dialog
    get dialogContent() {
        return {
            main: {
                text: "Greetings, seeker of truth. I am but a whisper in this strange city, messenger of the fungal gods",
                options: [
                    { text: "Tell me more about the city", next: 'city' },
                    { text: "Who are the fungal gods?", next: 'gods' }
                ]
            },
            city: {
                text: "This city... it breathes with ancient spores. The buildings grow like mushrooms in the dark, their patterns shifting when no one watches. Some say the entire city is one vast mycelial network, connecting all who dwell here in ways we cannot comprehend.",
                options: [
                    { text: "Ask about the gods", next: 'gods' },
                    { text: "Tell me more about city locations.", next: 'locations' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            gods: {
                text: "The fungal gods... they exist between reality and dream, like the thin membrane between cap and stem. They whisper through the spores we breathe, guiding us toward enlightenment... or perhaps madness. The distinction matters little in their realm.",
                options: [
                    { text: "Ask about the city", next: 'city' },
                    { text: "Where can I learn more about the fungal gods?", next: 'priests' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            priests: {
                text: "Go to the Egg Catedral and talk to some of the priests there. They are always happy to chat.",
                options: [
                    { text: "What is the Egg Catedral?", next: 'eggCatedral' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            eggCatedral: {
                text: "The Egg Cathedral is, well, a huge catedral that is hatching from gigantic egg. A massive, shell-grown structure inhabited by fungal clergy, flickering with bio-luminescent scripture...",
                options: [
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            locations: {
                text: "The city has many locations, but the most significant ones are the Candlepit of Saint Hesh, the Yolk Sea, Midwives' Ossuary, Sporewind Graves, and the Stomach Clock. Which one interests you?",
                options: [
                    { text: "Candlepit of Saint Hesh", next: 'candlepit' },
                    { text: "Yolk Sea", next: 'yolkSea' },
                    { text: "Midwives' Ossuary", next: 'midwivesOssuary' },
                    { text: "Sporewind Graves", next: 'sporewindGraves' },
                    { text: "Stomach Clock", next: 'stomachClock' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            candlepit: {
                text: "The Candlepit of Saint Hesh is a Circular wax catacomb with memory-melting rituals and speaking wounds. It is located beneath the Egg Cathedral.",
                options: [
                    { text: "What is the Egg Cathedral?", next: 'eggCatedral' },
                    { text: "What is the Yolk Sea?", next: 'yolkSea' },
                    { text: "What is the Midwives' Ossuary?", next: 'midwivesOssuary' },
                    { text: "What is the Sporewind Graves?", next: 'sporewindGraves' },
                    { text: "What is the Stomach Clock?", next: 'stomachClock' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            yolkSea: {
                text: "The Yolk Sea is a glowing, sentient ocean of living yolk. Boats float like seeds, and whispers rise from its depths.",
                options: [
                    { text: "What is the Candlepit of Saint Hesh?", next: 'candlepit' },
                    { text: "What is the Midwives' Ossuary?", next: 'midwivesOssuary' },
                    { text: "What is the Sporewind Graves?", next: 'sporewindGraves' },
                    { text: "What is the Stomach Clock?", next: 'stomachClock' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            midwivesOssuary: {
                text: "The Midwives' Ossuary is a Pelvis-shaped crypt filled with midwife husks who sew memory threads into your bones.",
                options: [
                    { text: "What is the Yolk Sea?", next: 'yolkSea' },
                    { text: "What is the Sporewind Graves?", next: 'sporewindGraves' },
                    { text: "What is the Stomach Clock?", next: 'stomachClock' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            sporewindGraves: {
                text: "The Sporewind Graves is a foggy fungal plains with drifting memory apparitions.",
                options: [
                    { text: "What is the Yolk Sea?", next: 'yolkSea' },
                    { text: "What is the Midwives' Ossuary?", next: 'midwivesOssuary' },
                    { text: "What is the Stomach Clock?", next: 'stomachClock' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            stomachClock: {
                text: "The Stomach Clock is a biomechanical chamber shaped like a digestive clock. Time runs in loops; bile is sacred. You can see it at the townhall",
                options: [
                    { text: "What is the Yolk Sea?", next: 'yolkSea' },
                    { text: "What is the Midwives' Ossuary?", next: 'midwivesOssuary' },
                    { text: "What is the Sporewind Graves?", next: 'sporewindGraves' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            }
        };
    }
}

if (typeof window !== 'undefined') {
    window.EntryScene = EntryScene;
}
