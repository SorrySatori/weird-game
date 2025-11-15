import GameScene from './GameScene.js'
import SceneTransitionManager from '../utils/SceneTransitionManager.js'

export default class TownSquareScene extends GameScene {
    constructor() {
        super({ key: 'TownSquareScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        return {
            ...super.dialogContent,
            ...this._magnekinDialogContent,
            ...this._buskerDialogContent
        };
    }

    preload() {
        super.preload();

        this.load.image('townSquareBg', 'assets/images/backgrounds/TownSquare.png');
        this.load.image('magnekin', 'assets/images/characters/magnekin.png');
        this.load.image('busker', 'assets/images/characters/busker.png');
    }

    create() {
        super.create();
        this.playSceneMusic('busker_theme');

        const bg = this.add.image(400, 300, 'townSquareBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        this.transitionManager = new SceneTransitionManager(this);

        this.transitionManager.createTransitionZone(
            720,
            300,
            80,
            400,
            'right',
            'TownhallScene',
            50,
            300,
        );

        this.createMagnekin();
        this.createBusker();

        this.cameras.main.fadeIn(800, 0, 0, 0);
    }

    createMagnekin() {
        this._magnekinDialogContent = {
            speaker: 'Magnekin',

            magnekin_start: {
                text: "Hello, who are you? I am... hmm, Magnekin, an average real citizen of this city. ",
                options: [
                    { text: "Hi, I am an aprentice of master Thaal from Obazoba church.", next: "magnekin_greeting" },
                    { text: "Hello there, I'm an Obazoba cult adept.", next: "magnekin_sense" },
                    { text: "What do you mean, *real citizen*?", next: "magnekin_suspicious" },
                    { text: "Hello, my name is Lord Murmurspine, I am en envoy from the Lagerlandia. Do you have a moment to talk about our lord and saviour, Maltimus Hopsalot?", next: "magnekin_hopsalot" },
                    ...(this.registry.get('symbiontSystem')?.hasSymbiont('neme-crownmire') ? [
                        { text: "Use Neme's power to detect lies and pretense.", next: "magnekin_neme_power" }
                    ] : []),
                ]
            },

            magnekin_greeting: {
                text: "It's a pleasure to meet you. Life in the city is... complicated, to say the least. But we manage, as every proper real and tottaly existing citizen. So, what brings you to this part of town?",
                options: [
                    { text: "I came here with my master to search for an origin of a distress signal. Did you seen any distress signal lately? Or anything unusual?", next: "magnekin_signal" },
                    { text: "Why do you keep saying *real*? You know, that sounds a bit suspicious.", next: "magnekin_suspicious" },
                    { text: "I am looking for my master. Have you ever heard about a place called Fermented Cap?", next: "magnekin_fermented_cap" },
                    ...(this.registry.get('symbiontSystem')?.hasSymbiont('neme-crownmire') ? [
                        { text: "Use Neme's power to detect lies and pretense.", next: "magnekin_neme_power" }
                    ] : []),
                    ...(this.questSystem.getQuest('rust_feast') ? [{
                        text: 'You know, I see your body is made of metal. You must know a lot... hm, about metal. Do you know where I can find some metal scraps?',
                        next: 'magenekin_metal_scraps'
                    }] : []),
                ]
            },

            magnekin_sense: {
                text: "An Obazoba cult adept, you say? Hmm, I must admit, I have heard some rumors about your kind. They say you folks have some... interesting beliefs. Could you tell me more about them?",
                options: [
                    { text: "Obazoba teaches that all minds are connected through hidden mycelium.", next: "obazoba_mycelium" },
                    { text: "Technically, it's not a cult. It’s a philosophy. A moist one, but still.", next: "obazoba_philosophy" },
                    { text: "Everything you heard is true and even weirder.", next: "obazoba_weirder" },
                    { text: "Maybe later.", next: "magnekin_main" }]
            },
            magnekin_main: {
                text: "So, do you have any other questions for me, fellow citizen?",
                options: [
                    { text: "I came here with my master to search for an origin of a distress signal. Did you seen any distress signal lately? Or anything unusual?", next: "magnekin_signal" },
                    { text: "Why do you keep saying *real*? You know, that sounds a bit suspicious.", next: "magnekin_suspicious" },
                    { text: "I am looking for my master. Have you ever heard about a pub called Fermented Cap?", next: "magnekin_fermented_cap" },
                    ...(this.registry.get('symbiontSystem')?.hasSymbiont('neme-crownmire') ? [
                        { text: "Use Neme's power to detect lies and pretense.", next: "magnekin_neme_power" }
                    ] : []),
                    ...(this.questSystem.getQuest('rust_feast') ? [{
                        text: 'You know, I see your body is made of metal. You must know a lot... hm, about metal. Do you know where I can find some metal scraps?',
                        next: 'magenekin_metal_scraps'
                    }] : []),
                ]
            },
            magnekin_suspicious: {
                text: "Well... what do you mean, suspicious? I am just a simple citizen trying to get by in this city. I am as real as they come. One person which exists in this world. Just like you. Ehm... what about the weather and taxes, huh?",
                options: [
                    { text: "Sorry, but there is something off about you.", next: "magnekin_off" },
                    { text: "Cut the act. Who are you really?", next: "magnekin_what_are_you" },
                    { text: "Come on. Nobody talks like that. Just tell me what you are.", next: "magnekin_what_are_you" },
                    ...(this.registry.get('symbiontSystem')?.hasSymbiont('neme-crownmire') ? [
                        { text: "Use Neme's power to detect lies and pretense.", next: "magnekin_neme_power" }
                    ] : []),
                    { text: "Alright then, keep your secrets.", next: "magnekin_main" }
                ]
            },
            magnekin_hopsalot: {
                text: "Ah, Lagerlandia! Yes, I've heard of it. A land of endless hops and barley, if I'm not mistaken. As for Maltimus Hopsalot, well, I can't say I've had the pleasure of meeting him personally. But I've heard he's quite the character. Always ready with a pint and a hearty laugh. So, what brings you here on his behalf?",
                options: [
                    { text: "Maltimus Hopsalot is a beer god, everybody knows that. Hm, I think there's something wrong with you... or suspicious.", next: "magnekin_suspicious" },
                    { text: "Maltimus wants you to contribute for the Endless Feast", next: "magnekin_contribution" },
                    ...(this.registry.get('symbiontSystem')?.hasSymbiont('neme-crownmire') ? [
                        { text: "Use Neme's power to detect lies and pretense.", next: "magnekin_neme_power" }
                    ] : []),
                    { text: "Maltimus Hopsalot wants you to join the faith!.", next: "magnekin_join_faith" },
                    { text: "Actually, I have other question.", next: "magnekin_main" }
                ]
            },
            magnekin_neme_power: {
                hidecloseOption: true,
                text: "As you focus Neme's power on Magnekin, you sense a strange aura around him. It's a mix of deception and hidden intentions. You get the feeling that Magnekin is not being entirely truthful with you. First, he's a liar. Second, he's not a one being, he's an enormous collective of tiny creatures.",
                options: [
                    { text: "Confront Magnekin about your discovery.", next: "magnekin_what_are_you" },
                ]
            },
            magnekin_signal: {
                text: "Distress signal, you say? Hmm, I haven't seen anything like that recently. But I've heard rumours that merchants at the Voxmarket have some good distress signals on sale right now.",
                options: [
                    { text: "What the hell arou you talking about?", next: "magnekin_wtf" },
                    { text: "Thanks... I guees. I have some other questions.", next: "magnekin_main" },
                    ...(this.registry.get('symbiontSystem')?.hasSymbiont('neme-crownmire') ? [
                        { text: "Use Neme's power to detect lies and pretense.", next: "magnekin_neme_power" }
                    ] : []),
                ]
            },
            magnekin_fermented_cap: {
                text: "Fermented Cap, you say? Yes, I've heard of that place. It's a famous museum of old things here in the city center.",
                options: [
                    { text: "What are you talking about? It's not a museum, it's a pub.", next: "magnekin_main" },
                    { text: "Museum of old things? Nobody talks like that, what's wrong with you?", next: "magnekin_wtf" },
                    ...(this.registry.get('symbiontSystem')?.hasSymbiont('neme-crownmire') ? [
                        { text: "Use Neme's power to detect lies and pretense.", next: "magnekin_neme_power" }
                    ] : []),
                    { text: "Err... Thanks... I guees. I have some other questions.", next: "magnekin_main" },
                ]
            },
            magenekin_metal_scraps: {
                text: "Ah, metal scraps! Yes, I know a place where you can find some. Go to Echo Drain delta place, there are plenty of metal scraps lying around. ",
                options: [
                    { text: "Thanks for the info. Can I ask for something else?", next: "magnekin_main" },
                    ...(this.registry.get('symbiontSystem')?.hasSymbiont('neme-crownmire') ? [
                        { text: "Use Neme's power to detect lies and pretense.", next: "magnekin_neme_power" }
                    ] : []),
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('rust_feast', 'A strange creature that identifies itself as Magnekin told me that some metal scraps could be found at Echo Drain delta.', 'magnekin_tip');
                }

            },
            obazoba_mycelium: {
                text: "Ah, the mycelium network! It's fascinating how interconnected everything is. Through the mycelium, we can share thoughts, emotions, and even memories. It's like a living web that binds us all together. In a way, it's a reminder that we're never truly alone. Could you tell me more?",
                options: [
                    { text: "Would you prefer the official doctrine or the fun version?", next: "obazoba_more" },
                    { text: "Let me tell you about the Ur-mushroom.", next: "obazoba_ur_mushroom" },
                    { text: "I’m just the apprentice", next: "obazoba_apprentice" },
                    { text: "Maybe later.", next: "magnekin_main" }
                ]
            },
            obazoba_philosophy: {
                text: "A philosophy, you say? Moisture is the sign that the Ur-Mushroom is near, you say? Interesting, could you tell me more?",
                options: [
                    { text: "Moisture is life breathing", next: "obazoba_moisture" },
                    { text: "Would you prefer the official doctrine or the fun version?", next: "obazoba_more" },
                    { text: "Let me tell you about the Ur-mushroom.", next: "obazoba_ur_mushroom" },
                    { text: "I’m just the apprentice", next: "obazoba_apprentice" },
                    { text: "Maybe later.", next: "magnekin_main" }
                ]
            },
            obazoba_weirder: {
                text: "Hah, I thought that you are goint to say that. So, what else can you tell me about your beliefs? Anything particularly weird?",
                options: [
                    { text: "Would you prefer the official doctrine or the fun version?", next: "obazoba_more" },
                    { text: "Let me tell you about the Ur-mushroom.", next: "obazoba_ur_mushroom" },
                    { text: "Mushrooms can create their own weather.", next: "obazoba_weather" },
                    { text: "I’m just the apprentice", next: "obazoba_apprentice" },
                    { text: "Maybe later.", next: "magnekin_main" }
                ]
            },
            magnekin_contribution: {
                text: "Ah, the Endless Feast! A noble cause indeed. Contributing to the feast is a way to honor Maltimus Hopsalot and ensure that his blessings continue to flow. Here's 10 dinars, good man.",
                options: [
                    { text: "Thank you. Anything else I should know?", next: "magnekin_main" },
                    ...(this.registry.get('symbiontSystem')?.hasSymbiont('neme-crownmire') ? [
                        { text: "Use Neme's power to detect lies and pretense.", next: "magnekin_neme_power" }
                    ] : []),
                ],
                onTrigger: () => {
                    this.moneySystem.add(10);
                }
            },
            magnekin_join_faith: {
                hidecloseOption: true,
                text: "Join the faith of Maltimus Hopsalot? Of course, it will be my honor to do so! May the endless hops guide my path.",
                options: [
                    { text: "Glad to hear that. Let's proceed with the holy ceremony... I mean, with the foamy ceremony", next: "magnekin_hopsalot_ceremony" },
                ],
            },
            magnekin_hopsalot_ceremony: {
                hidecloseOption: true,
                text: "You start the ceremony to convert Magnekin to the faith of Maltimus Hopsalot. Starting with the sacred words: *Intent flows as foam does — upward, outward, and occasionally sideways*",
                options: [
                    { text: "Continue the ceremony", next: "magnekin_hopsalot_ceremony_continue" },
                ],
            },
            magnekin_hopsalot_ceremony_continue: {
                hidecloseOption: true,
                text: "The novice must then carry the mug—still full—to a small altar shaped like a keg. But you dont have a mug with you. Luckily, Magnekin produces one from his body. Just like that, he grabs some metal and forms a decent mug. The ceremony can continue",
                options: [
                    { text: "Complete the ceremony", next: "magnekin_hopsalot_ceremony_complete" },
                ],
            },
            magnekin_hopsalot_ceremony_complete: {
                hidecloseOption: true,
                text: "Magnekin raises the mug to his lips and drinks deeply, savoring the bitter taste of the sacred brew. As he finishes the last drop, he feels a warm glow spreading through his body. He is now a devoted follower of Maltimus Hopsalot. You scream the sacred chant: *HOP! HOP! HOPSA-LOOOOT!FOAM AND FIZZZ, NEVER STOP!*",
                options: [
                    { text: "Welcome to the faith of Maltimus Hopsalot!", next: "magnekin_hopsalot_completed" },
                ],
                onTrigger: () => {
                    this.addJournalEntry(
                        'magnekin_hopsalot_conversion',
                        'Maltimus Hopsalot Conversion',
                        'Seriously, what just happened? I have converted Magnekin to the faith of Maltimus Hopsalot. I need to write down that I totally made up Lagerlandia and Maltimus Hopsalot on the spot. Yet this creature believed me. Unbelievable. I have my own cult now.',
                        this.journalSystem.categories.EVENT,
                    );
                    this.addJournalEntry(
                        'magnekin_hopsalot_church',
                        'Maltimus Hopsalot Church',
                        'Lagerlandia is a mythical land where beer flows like rivers and the skies rain hops. Its patron deity, Maltimus Hopsalot, is revered as the god of beer, brewing, and merriment. Followers of Maltimus Hopsalot believe that by partaking in the sacred brew, they can achieve enlightenment and eternal joy. The church of Maltimus Hopsalot is known for its lively festivals, communal feasts, and the legendary Endless Feast, where devotees gather to celebrate the divine gift of beer. Or something like that. I just made it up, but it sounds convincing enough.',
                        this.journalSystem.categories.LORE,
                    );
                }
            },
            magnekin_off: {
                hidecloseOption: true,
                text: "Off? What do you mean, off? Ahh damn it... it's not very convincing, is it? Look, I just want to get by in this city without drawing too much attention. You know how it is. People can be... judgmental. What gave me away?",
                options: [
                    { text: "Everything about you is weird.", next: "magnekin_everything" },
                    { text: "You keep talking about being a 'real citizen'.", next: "magnekin_everything" },
                    { text: "I will tell you. But first, who are you really?", next: "magnekin_everything" },
                ]
            },
            magnekin_what_are_you: {
                hidecloseOption: true,
                text: "Alright, you got me. I'm not exactly what you'd call a 'real citizen'. I'm actually a collective of tiny cities that work together to mimic a humanoid form. We call ourselves Magnekin. You know, we use power of magnets to hold together. It's a long story. We were just curious about life in the city of the big creatures. It's fascinating experiment, really. But I'm afraid we are not very convincing at blending in.",
                options: [
                    { text: "Fascinating. Are you really cities? How's that possible?", next: "magnekin_cities" },
                    { text: "What's your origin story", next: "magnekin_origin" },
                    { text: "I can help you to blend in.", next: "magnekin_blend" },
                ],
                onTrigger: () => {
                    this.addJournalEntry(
                        'magnekin_reveal',
                        'Magnekin',
                        'I have discovered that creature called Magnekin is not a single being, but a collective of tiny cities that work together to mimic a humanoid form. They use magnetic forces to hold themselves together. I wonder if this town could get any more strange than it already is.',
                        this.journalSystem.categories.PEOPLE,
                    );
                }
            },
            magnekin_cities:{
                text: "Yes, there is a whole civilization living inside me. Each part of my body is actually a micro-city, inhabited by beings who have built their homes and lives around magnetic lodestones. We work together to create this humanoid form, allowing us to explore the world of larger creatures like you. It's a delicate balance, but we've managed to make it work. It's quite an experience, seeing the world from this perspective.",
                options: [
                    { text: "Incredible. I can help you to blend in, if you want.", next: "magnekin_origin" },
                    { text: "Interesting. But you seem fragile and from valuable resources (try to destroy Magnekin).", next: "magnekin_destroy" },
                    { text: "It was nice to meet you, but I have other questions.", next: "magnekin_main" },
                ]
            },
            magnekin_origin: {
                text: "Well, it's a bit complicated. Our historians teach that in the Crownmire, there was once a cult that worshiped ancient magnetic spirits. When their shrine collapsed after unknown disaster, its lodestone heart shattered into millions of shards—each shard becoming a cornerstone for a micro-city’s consciousness. Our civilization only recenlty discovered that there is another world beyond, at entirely different scale. We are still learning how to interact with you.",
            options: [
                { text: "Incredible. I can help you to blend in, if you want.", next: "magnekin_origin" },
                { text: "Interesting. But you seem fragile and from valuable resources (try to destroy Magnekin).", next: "magnekin_destroy" },
                { text: "It was nice to meet you, but I have other questions.", next: "magnekin_main" },
            ]
            },
            magnekin_hopsalot_completed: {
                text: "Thank you, my friend! I feel... different now. Like a new purpose has awakened within me. I am honored to be a follower of Maltimus Hopsalot. May the endless hops guide my path!",
                options: [
                    { text: "Glad to hear that. Anything else I should know?", next: "magnekin_main" },
                    ...(this.registry.get('symbiontSystem')?.hasSymbiont('neme-crownmire') ? [
                        { text: "Use Neme's power to detect lies and pretense.", next: "magnekin_neme_power" }
                    ] : []),
                ],
                onTrigger: () => {
                    this.modifySpores(10);
                }
            },

        };

        this.magnekin = this.add.container(250, 300);
        this.magnekin.setDepth(-1);

        const magnekinSprite = this.add.sprite(0, 0, 'magnekin');
        magnekinSprite.setScale(0.2);

        magnekinSprite.setTint(0xc0c0c0);

        this.magnekin.add(magnekinSprite);

        this.magnekinGlow = this.add.graphics();
        this.magnekinGlow.fillStyle(0x8888ff, 0.15);
        this.magnekinGlow.fillCircle(250, 350, 45);
        this.magnekinGlow.setDepth(4);

        this.tweens.add({
            targets: this.magnekinGlow,
            alpha: { from: 0.15, to: 0.05 },
            duration: 2000,
            yoyo: true,
            repeat: -1
        });

        this.tweens.add({
            targets: this.magnekin,
            y: { from: 350, to: 345 },
            duration: 2500,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });

        const hitArea = new Phaser.Geom.Rectangle(-40, -90, 80, 140);
        this.magnekin.setInteractive(hitArea, Phaser.Geom.Rectangle.Contains);

        this.magnekin.on('pointerover', () => {
            this.magnekin.setScale(1.05);
            document.body.style.cursor = 'pointer';
        });

        this.magnekin.on('pointerout', () => {
            this.magnekin.setScale(1);
            document.body.style.cursor = 'default';
        });

        this.magnekin.on('pointerdown', () => {
            if (this.clickSound) {
                this.clickSound.play();
            }

            this.tweens.add({
                targets: this.magnekin,
                y: { from: this.magnekin.y, to: this.magnekin.y - 5 },
                duration: 100,
                ease: 'Power1',
                yoyo: true
            });

            this.showDialog('magnekin_start');
        });
    }

    createBusker() {
        this._buskerDialogContent = {
            speaker: 'Busker',

            busker_greeting: {
                text: "Hey there! Care to hear a tune? I play the songs of the old world—melodies that remember when the sky was blue and the air was clean.",
                options: [
                    { text: "What kind of songs do you play?", next: "busker_songs" },
                    { text: "Where did you learn these songs?", next: "busker_learn" },
                    { text: "Maybe later.", next: null }
                ]
            },

            busker_songs: {
                text: "Ballads of lost cities, lullabies from forgotten cultures, work songs from trades that no longer exist. Each one is a memory preserved in melody. Music is the only time machine we have left.",
                options: [
                    { text: "That's beautiful.", next: "busker_greeting" },
                    { text: "Maybe later.", next: null }
                ]
            },

            busker_learn: {
                text: "From the elders, mostly. They taught me before they passed on. Now I'm one of the few who remembers. Sometimes I wonder if anyone really listens, or if I'm just singing to the stones.",
                options: [
                    { text: "I'm listening.", next: "busker_thanks" },
                    { text: "Maybe later.", next: null }
                ]
            },

            busker_thanks: {
                text: "Thank you, friend. That means more than you know. As long as someone listens, the songs live on. And as long as the songs live, so do the memories.",
                options: [
                    { text: "Tell me more.", next: "busker_greeting" },
                    { text: "Farewell.", next: null }
                ]
            }
        };

        this.busker = this.add.container(550, 380);
        this.busker.setDepth(-1);

        const buskerSprite = this.add.sprite(0, 0, 'busker');
        buskerSprite.setScale(0.2);

        buskerSprite.setTint(0xffcc88);

        this.busker.add(buskerSprite);

        this.buskerGlow = this.add.graphics();
        this.buskerGlow.fillStyle(0xffaa44, 0.15);
        this.buskerGlow.fillCircle(550, 380, 45);
        this.buskerGlow.setDepth(4);

        this.tweens.add({
            targets: this.buskerGlow,
            alpha: { from: 0.15, to: 0.05 },
            duration: 1800,
            yoyo: true,
            repeat: -1
        });

        this.tweens.add({
            targets: this.busker,
            angle: { from: -2, to: 2 },
            duration: 3000,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });

        const hitArea = new Phaser.Geom.Rectangle(-40, -90, 80, 140);
        this.busker.setInteractive(hitArea, Phaser.Geom.Rectangle.Contains);

        this.busker.on('pointerover', () => {
            this.busker.setScale(1.05);
            document.body.style.cursor = 'pointer';
        });

        this.busker.on('pointerout', () => {
            this.busker.setScale(1);
            document.body.style.cursor = 'default';
        });

        this.busker.on('pointerdown', () => {
            if (this.clickSound) {
                this.clickSound.play();
            }

            this.tweens.add({
                targets: this.busker,
                y: { from: this.busker.y, to: this.busker.y - 5 },
                duration: 100,
                ease: 'Power1',
                yoyo: true
            });

            this.showDialog('busker_greeting');
        });
    }

    shutdown() {
        super.shutdown();
    }

    update() {
        super.update();
    }
}

if (typeof window !== 'undefined') {
    window.TownSquareScene = TownSquareScene;
}

export { TownSquareScene };
