import GameScene from './GameScene.js';

export default class ShedRegistrationScene extends GameScene {
    constructor() {
        super({ key: 'ShedRegistrationScene' });
        this.isTransitioning = false;
        this.dreamQueueStarted = false;
        this.npcsInteractedWith = new Set();
        this.dreamQueueChoices = {
            sleeplessMime: null,
            vowelSeller: null,
            hollowWoman: null
        };
    }

    preload() {
        super.preload();
        this.load.image('registration-bg', 'assets/images/ShedRegistrationZone.png');
        this.load.image('door', 'assets/images/door.png');
        this.load.image('clerk', 'assets/images/clerk.png');
        this.load.image('clerk2', 'assets/images/clerk2.png');
        this.load.image('vowelSeller', 'assets/images/vowelSeller.png');
        this.load.image('hollowWoman', 'assets/images/hollowWoman.png');

    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set initial priest position
        if (this.priest) {
            this.priest.x = 110;  // Match entrance position from Shed13FloorsScene
            this.priest.y = 520;  // Ground level
            this.priest.setOrigin(0.5, 1);
            this.priest.play('idle');
        }

        // Set background
        const bg = this.add.image(400, 300, 'registration-bg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Add exit back to Shed13FloorsScene
        this.exitToShed = this.add.image(110, 520, 'door')
            .setDisplaySize(100, 100)
            .setAlpha(0.01)
            .setInteractive();

        // Set up pointer events
        this.exitToShed.on('pointerover', () => {
            if (!this.isTransitioning) {
                this.setCursor('pointer');
            }
        });

        // Create an invisible exit area using a rectangle instead of an image
        this.exitArea = this.add.rectangle(50, 470, 50, 200, 0xffffff)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);
        
        // Create NPCs but keep them invisible until needed
        this.createDreamQueueNPCs();
        
        // Start the dream queue sequence after a short delay
        this.time.delayedCall(1000, () => {
            this.startDreamQueue();
        });

        this.exitToShed.on('pointerout', () => {
            if (!this.isTransitioning) {
                this.setCursor('default');
            }
        });

        this.exitToShed.on('pointerdown', () => {
            if (!this.isTransitioning) {
                this.isTransitioning = true;
                this.transitionToScene('Shed13FloorsScene', () => {
                    // Set position in Shed13FloorsScene near the welcome entrance
                    return { x: 110, y: 450 };
                });
            }
        });

        this.exitArea.on('pointerdown', () => {
            // Move priest to exit area, then fade out
            const priest = this.priest;
            priest.play('walk');
            
            // Stop any existing tweens on the priest
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: 50,
                y: 470,
                duration: 1000,
                onComplete: () => {
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('Shed13FloorsScene');
                        this.isTransitioning = false; // Reset transition flag
                    });
                }
            });
        });
    }

    update() {
        super.update();
    }
    
    createDreamQueueNPCs() {
        // Create a container for the queue
        this.queueContainer = this.add.container(400, 450);
        
        // 1. Sleepless Mime (using clerk.png for now) - first in queue
        this.sleeplessMime = this.add.sprite(-150, 0, 'clerk')
            .setScale(0.4)
            .setVisible(false)
            .setInteractive({ useHandCursor: true });
            
        // Add a subtle glow effect
        this.sleeplessMimeGlow = this.add.graphics();
        this.sleeplessMimeGlow.fillStyle(0x7fff8e, 0.2);
        this.sleeplessMimeGlow.fillCircle(-150, 0, 50);
        this.sleeplessMimeGlow.setVisible(false);
        
        // Add to queue container
        this.queueContainer.add(this.sleeplessMime);
        this.queueContainer.add(this.sleeplessMimeGlow);
        
        // Set up interaction
        this.sleeplessMime.on('pointerdown', () => {
            if (!this.isTransitioning) {
                this.showDialog('sleeplessMime_start');
            }
        });
        
        // 2. Vowel Seller - second in queue
        this.vowelSeller = this.add.sprite(0, 0, 'vowelSeller')
            .setScale(0.4)
            .setVisible(false)
            .setInteractive({ useHandCursor: true });
            
        // Add ash particle effect (static version to avoid errors)
        this.vowelSellerAsh = this.add.graphics();
        this.vowelSellerAsh.fillStyle(0xcccccc, 0.3);
        this.vowelSellerAsh.fillCircle(0, 0, 40);
        this.vowelSellerAsh.setVisible(false);
        
        // Add to queue container
        this.queueContainer.add(this.vowelSeller);
        this.queueContainer.add(this.vowelSellerAsh);
        
        // Set up interaction
        this.vowelSeller.on('pointerdown', () => {
            if (!this.isTransitioning) {
                this.showDialog('vowelSeller_start');
            }
        });
        
        // 3. Hollow Woman (using clerk2.png for now) - third in queue
        this.hollowWoman = this.add.sprite(150, 0, 'hollowWoman')
            .setScale(0.4)
            .setVisible(false)
            .setInteractive({ useHandCursor: true });
            
        // Add stitched seams effect
        this.hollowWomanSeams = this.add.graphics();
        this.hollowWomanSeams.lineStyle(1, 0x7fff8e, 0.7);
        this.hollowWomanSeams.strokeRect(150 - 20, 0 - 40, 40, 80);
        this.hollowWomanSeams.setVisible(false);
        
        // Add to queue container
        this.queueContainer.add(this.hollowWoman);
        this.queueContainer.add(this.hollowWomanSeams);
        
        // Set up interaction
        this.hollowWoman.on('pointerdown', () => {
            if (!this.isTransitioning) {
                this.showDialog('hollowWoman_start');
            }
        });
        
        // 4. Senior Clerk (will appear after all others are interacted with)
        this.seniorClerk = this.add.sprite(300, 350, 'clerk')
            .setScale(0.5)
            .setAlpha(0)
            .setInteractive({ useHandCursor: true });
            
        // Set up interaction
        this.seniorClerk.on('pointerdown', () => {
            if (!this.isTransitioning && this.seniorClerk.alpha > 0.9) {
                this.showDialog('seniorClerk_start');
            }
        });
    }
    
    startDreamQueue() {
        if (this.dreamQueueStarted) return;
        this.dreamQueueStarted = true;
        
        // Fade in the NPCs one by one with a delay
        
        // 1. Sleepless Mime
        this.sleeplessMime.setVisible(true);
        this.sleeplessMimeGlow.setVisible(true);
        this.sleeplessMime.alpha = 0;
        this.sleeplessMimeGlow.alpha = 0;
        
        this.tweens.add({
            targets: [this.sleeplessMime, this.sleeplessMimeGlow],
            alpha: 1,
            duration: 1500,
            delay: 500,
            ease: 'Power2'
        });
        
        // 2. Vowel Seller
        this.vowelSeller.setVisible(true);
        this.vowelSellerAsh.setVisible(true);
        this.vowelSeller.alpha = 0;
        this.vowelSellerAsh.alpha = 0;
        
        this.tweens.add({
            targets: [this.vowelSeller, this.vowelSellerAsh],
            alpha: 1,
            duration: 1500,
            delay: 1500,
            ease: 'Power2'
        });
        
        // 3. Hollow Woman
        this.hollowWoman.setVisible(true);
        this.hollowWomanSeams.setVisible(true);
        this.hollowWoman.alpha = 0;
        this.hollowWomanSeams.alpha = 0;
        
        this.tweens.add({
            targets: [this.hollowWoman, this.hollowWomanSeams],
            alpha: 1,
            duration: 1500,
            delay: 2500,
            ease: 'Power2',
            onComplete: () => {
                this.showNotification('The dream queue awaits...');
            }
        });
    }
    
    checkAllNPCsInteracted() {
        // Check if player has interacted with all three NPCs
        if (this.npcsInteractedWith.size >= 3) {
            // Show notification
            this.showNotification('All queue inhabitants have faded away');
            
            // Delay before showing Senior Clerk
            this.time.delayedCall(2000, () => {
                // Fade in the Senior Clerk
                this.tweens.add({
                    targets: this.seniorClerk,
                    alpha: 1,
                    y: 300,
                    duration: 1500,
                    ease: 'Power2',
                    onComplete: () => {
                        this.showNotification('The Senior Clerk has arrived');
                        this.time.delayedCall(1000, () => {
                            this.showDialog('seniorClerk_start');
                        });
                    }
                });
            });
        }
    }
    
    get dialogContent() {
        return {
            ...super.dialogContent,
            // 1. Sleepless Mime Dialog
            sleeplessMime_start: {
                text: "(The Sleepless Mime watches you intently. Their rusting faceplate catches the dim light. They silently mimic your posture, then make a gesture with their hands - forming a cube shape, like a die. They pantomime you holding it.)",
                options: [
                    { text: "I used to play.", next: "sleeplessMime_memory" },
                    { text: "Is that for Ortolan?", next: "sleeplessMime_ortolan" }
                ]
            },
            sleeplessMime_memory: {
                text: "(The Mime nods enthusiastically. Their hands begin to weave a pattern in the air, conjuring phantom game pieces. For a moment, you feel yourself slipping into a memory...)",
                options: [
                    { text: "Remember...", next: "sleeplessMime_memory_scene" }
                ]
            },
            sleeplessMime_memory_scene: {
                text: "(You recall a childhood game. Dice made of bone, cards painted with symbols that shifted when no one was looking. The rules changed each time, but somehow you always knew how to play. The memory fades, but leaves a warm glow in your mind.)",
                options: [
                    { text: "Thank you for reminding me.", next: "sleeplessMime_end" }
                ],
                onShow: () => {
                    this.dreamQueueChoices.sleeplessMime = 'memory';
                    this.modifyGrowthDecay(2, 0);
                    this.showNotification('Growth +2: A cherished memory returns');
                    this.npcsInteractedWith.add('sleeplessMime');
                    this.checkAllNPCsInteracted();
                }
            },
            sleeplessMime_ortolan: {
                text: "(The Mime nods vigorously. They reach into their pocket and produce a tattered fragment of paper. They press it into your hand - it appears to be a page from Ortolan's unfinished rulebook.)",
                options: [
                    { text: "Read the fragment", next: "sleeplessMime_rulebook" }
                ]
            },
            sleeplessMime_rulebook: {
                text: "'...and when the third eye opens on the die, all players must exchange one memory with the player to their left. If memories cannot be verified by a Witness, the exchange is considered void, and both players gain a Doubt token...'",
                options: [
                    { text: "This will be useful. Thank you.", next: "sleeplessMime_end" }
                ],
                onShow: () => {
                    this.dreamQueueChoices.sleeplessMime = 'rulebook';
                    // Add rulebook fragment to inventory
                    this.addItemToInventory({
                        id: 'rulebook-fragment',
                        name: 'Rulebook Fragment',
                        description: 'A torn page from Ortolan\'s unfinished game rulebook. It describes memory exchange mechanics.',
                        stackable: false
                    });
                    this.showNotification('Received: Rulebook Fragment');
                    this.npcsInteractedWith.add('sleeplessMime');
                    this.checkAllNPCsInteracted();
                }
            },
            sleeplessMime_end: {
                text: "(The Mime bows deeply, then fades away into the dreamlike atmosphere of the queue.)",
                options: [
                    { text: "Continue waiting", next: "end" }
                ],
                onShow: () => {
                    // Fade out the Mime
                    this.tweens.add({
                        targets: [this.sleeplessMime, this.sleeplessMimeGlow],
                        alpha: 0,
                        duration: 1500,
                        onComplete: () => {
                            this.sleeplessMime.setVisible(false);
                            this.sleeplessMimeGlow.setVisible(false);
                        }
                    });
                }
            },
            
            // 2. Vowel Seller Dialog
            vowelSeller_start: {
                text: "(The ash-covered figure turns to you, tiny glass vials clinking in their coat pockets. Each contains a glowing letter, suspended in fluid.)\n\n'I sell vowels. If you want your name to matter, you'll need one.'\n\nThey hold up a vial with a pulsing 'A' inside.",
                options: [
                    { text: "I'll buy one.", next: "vowelSeller_buy" },
                    { text: "Keep your vowels. I speak in spores.", next: "vowelSeller_spores" }
                ]
            },
            vowelSeller_buy: {
                text: "'A wise choice. The price is a minor memory. Something small... perhaps the taste of your first meal in this city?'\n\n(They uncork the vial, and the vowel floats up, hovering before entering your mouth. You feel a strange resonance, as if your name has become more complete.)",
                options: [
                    { text: "Thank you.", next: "vowelSeller_end" }
                ],
                onShow: () => {
                    this.dreamQueueChoices.vowelSeller = 'vowel';
                    this.modifyGrowthDecay(0, 1);
                    this.showNotification('Decay +1: A minor memory fades');
                    this.showNotification('Effect: Some characters may recognize your true name');
                    this.npcsInteractedWith.add('vowelSeller');
                    this.checkAllNPCsInteracted();
                }
            },
            vowelSeller_spores: {
                text: "(Their eyes widen slightly.)\n\n'The fungal tongue... I see. Then perhaps you might appreciate this instead.'\n\n(They hand you a small card with nothing written on it.)\n\n'A silent sentence. Use it when words fail you at the clerk's desk.'",
                options: [
                    { text: "I accept this gift.", next: "vowelSeller_end" }
                ],
                onShow: () => {
                    this.dreamQueueChoices.vowelSeller = 'silence';
                    // Add silent sentence to inventory
                    this.addItemToInventory({
                        id: 'silent-sentence',
                        name: 'Silent Sentence',
                        description: 'A blank card that somehow contains meaning. It might be useful when words fail.',
                        stackable: false
                    });
                    this.showNotification('Received: Silent Sentence');
                    this.npcsInteractedWith.add('vowelSeller');
                    this.checkAllNPCsInteracted();
                }
            },
            vowelSeller_end: {
                text: "(The Vowel Seller nods and dissolves into a cloud of ash, their vials tinkling softly as they disappear.)",
                options: [
                    { text: "Continue waiting", next: "end" }
                ],
                onShow: () => {
                    // Fade out the Vowel Seller
                    this.tweens.add({
                        targets: [this.vowelSeller, this.vowelSellerAsh],
                        alpha: 0,
                        duration: 1500,
                        onComplete: () => {
                            this.vowelSeller.setVisible(false);
                            this.vowelSellerAsh.setVisible(false);
                        }
                    });
                }
            },
            
            // 3. Hollow Woman Dialog
            hollowWoman_start: {
                text: "(The woman with empty eyes and stitched seams leans slightly on your shoulder. Her voice is barely audible.)\n\n'It's always the same. The longer I wait... the fewer limbs I have.'\n\n(You notice her left arm ends at the elbow, the edges neatly stitched.)",
                options: [
                    { text: "Do you remember your hands?", next: "hollowWoman_hands" },
                    { text: "You can have one of mine.", next: "hollowWoman_offer" }
                ]
            },
            hollowWoman_hands: {
                text: "'Sometimes... in dreams. They were good at filling out forms. Section 7-B was my specialty.'\n\n(She whispers a strange bureaucratic incantation in your ear.)\n\n'Remember that when you speak to the clerk. It's the only way to bypass the Inherited Deformity clause.'",
                options: [
                    { text: "I'll remember. Thank you.", next: "hollowWoman_end" }
                ],
                onShow: () => {
                    this.dreamQueueChoices.hollowWoman = 'narrative';
                    // Update quest if it exists
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && questSystem.getQuest('ortolan_arms')) {
                        questSystem.updateQuest(
                            'ortolan_arms', 
                            'The Hollow Woman in the registration queue taught me a bureaucratic incantation to bypass the Inherited Deformity clause. This might help with Ortolan\'s paperwork.',
                            'bureaucratic_incantation'
                        );
                        this.showNotification('Quest updated: Ortolan Arms Investigation');
                    }
                    this.npcsInteractedWith.add('hollowWoman');
                    this.checkAllNPCsInteracted();
                }
            },
            hollowWoman_offer: {
                text: "(Her empty eyes widen slightly.)\n\n'A symbolic gift... I haven't received one in cycles.'\n\n(She touches your hand, and for a moment you feel a strange connection, as if something flows between you.)",
                options: [
                    { text: "You're welcome.", next: "hollowWoman_end" }
                ],
                onShow: () => {
                    this.dreamQueueChoices.hollowWoman = 'empathy';
                    this.modifyGrowthDecay(3, 0);
                    this.showNotification('Growth +3: Symbolic empathy strengthens you');
                    this.npcsInteractedWith.add('hollowWoman');
                    this.checkAllNPCsInteracted();
                }
            },
            hollowWoman_end: {
                text: "(The Hollow Woman steps back, a faint smile on her stitched face. She unravels thread by thread until nothing remains but the memory of her presence.)",
                options: [
                    { text: "Continue waiting", next: "end" }
                ],
                onShow: () => {
                    // Fade out the Hollow Woman
                    this.tweens.add({
                        targets: [this.hollowWoman, this.hollowWomanSeams],
                        alpha: 0,
                        duration: 1500,
                        onComplete: () => {
                            this.hollowWoman.setVisible(false);
                            this.hollowWomanSeams.setVisible(false);
                        }
                    });
                }
            },
            
            // 4. Senior Clerk Dialog
            seniorClerk_start: {
                text: "(The Senior Clerk materializes at the front of the queue, adjusting a stack of papers with mechanical precision. Their voice has a metallic quality.)\n\n'Queue segment F-7 has been processed. Your presence has been noted and your interactions catalogued.'\n\n(They consult a clipboard.)\n\n'State your business.'",
                options: [
                    { text: "I need to register for...", next: "seniorClerk_register" },
                    { text: "What happened to those people I was talking to?", next: "seniorClerk_people" }
                ]
            },
            seniorClerk_register: {
                text: "'Registration requires Form 27-B/6, submitted in triplicate with appropriate growth/decay balance certification.'\n\n(They look at you expectantly, then sigh.)\n\n'But I see you've been... influenced by the queue inhabitants. Very well. I'll expedite your processing.'",
                options: [
                    { text: "Thank you.", next: "seniorClerk_processing" }
                ]
            },
            seniorClerk_people: {
                text: "(The Clerk's expression remains unchanged.)\n\n'People? There were no people. Only manifestations of the queue itself. Echoes of those who waited too long. You've absorbed their essence now - their stories are part of your processing.'\n\n(They tap their clipboard.)\n\n'Quite irregular, but we'll proceed.'",
                options: [
                    { text: "I see...", next: "seniorClerk_processing" }
                ]
            },
            seniorClerk_processing: {
                text: "'Based on your queue interactions, your application has been...'\n\n(They stamp a form with a flourish.)\n\n'...approved. You may proceed to the Registration Office proper. The Registrar will see you now.'",
                options: [
                    { text: "Proceed to the Registration Office", next: "seniorClerk_proceed" }
                ]
            },
            seniorClerk_proceed: {
                text: "(The Senior Clerk gestures to a door that wasn't there before, glowing with a soft green light.)\n\n'Remember what you've learned here. The queue is never just a queue in Shed13.'",
                options: [
                    { text: "Enter the door", next: "seniorClerk_end" }
                ],
                onShow: () => {
                    // Create the new door
                    this.registrationDoor = this.add.image(600, 400, 'door')
                        .setDisplaySize(100, 150)
                        .setInteractive({ useHandCursor: true });
                    
                    // Add glow effect
                    this.doorGlow = this.add.graphics();
                    this.doorGlow.fillStyle(0x7fff8e, 0.3);
                    this.doorGlow.fillCircle(600, 400, 80);
                    
                    // Make the door interactive
                    this.registrationDoor.on('pointerdown', () => {
                        this.hideDialog();
                        this.proceedToRegistrationOffice();
                    });
                }
            },
            seniorClerk_end: {
                text: "(The Senior Clerk returns to their paperwork, seemingly forgetting your existence.)",
                options: [
                    { text: "Approach the glowing door", next: "end" }
                ],
                onShow: () => {
                    this.hideDialog();
                }
            }
        };
    }
    
    proceedToRegistrationOffice() {
        // Save the player's choices for use in the next scene
        this.registry.set('dreamQueueChoices', this.dreamQueueChoices);
        
        // Transition effect
        this.isTransitioning = true;
        this.cameras.main.fadeOut(1000, 0, 0, 0);
        this.cameras.main.once('camerafadeoutcomplete', () => {
            // Logic for what happens next would go here
            // For now, we'll just go back to the Shed13FloorsScene
            this.scene.start('Shed13FloorsScene');
            this.isTransitioning = false;
        });
    }
}
