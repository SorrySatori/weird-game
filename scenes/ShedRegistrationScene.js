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
    
    // Safe version of modifyGrowthDecay that doesn't rely on the UI indicator
    safeModifyGrowthDecay(growthChange, decayChange) {
        // Get the growth/decay system from registry
        this.modifyGrowthDecay(growthChange, decayChange);
    }

    preload() {
        super.preload();
        this.load.image('registration-bg', 'assets/images/backgrounds/ShedRegistrationZone.png');
        this.load.image('door', 'assets/images/ui/door.png');
        this.load.image('clerk2', 'assets/images/characters/clerk2.png');
        this.load.image('vowelSeller', 'assets/images/characters/vowelSeller.png');
        this.load.image('hollowWoman', 'assets/images/characters/hollowWoman.png');
        this.load.image('sleeplessMime', 'assets/images/characters/mime.png');

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
        this.sleeplessMime = this.add.sprite(-150, 0, 'sleeplessMime')
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
        this.seniorClerk = this.add.sprite(300, 350, 'clerk2')
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
            
            // Make sure all NPC sprites are completely hidden
            // Hide Sleepless Mime completely if still visible
            if (this.sleeplessMime && this.sleeplessMime.visible) {
                this.sleeplessMime.setVisible(false);
                if (this.sleeplessMimeGlow) {
                    this.sleeplessMimeGlow.setVisible(false);
                }
            }
            
            // Hide Vowel Seller completely if still visible
            if (this.vowelSeller && this.vowelSeller.visible) {
                this.vowelSeller.setVisible(false);
                if (this.vowelSellerAsh) {
                    this.vowelSellerAsh.setVisible(false);
                }
            }
            
            // Hide Hollow Woman completely if still visible
            if (this.hollowWoman && this.hollowWoman.visible) {
                this.hollowWoman.setVisible(false);
                if (this.hollowWomanSeams) {
                    this.hollowWomanSeams.setVisible(false);
                }
            }
            
            // Delay before showing Senior Clerk
            this.time.delayedCall(2000, () => {
                // Create the Senior Clerk if it doesn't exist yet
                if (!this.seniorClerk) {
                    this.seniorClerk = this.add.sprite(400, 400, 'clerk2')
                        .setScale(0.5)
                        .setAlpha(0);
                    this.seniorClerk.setInteractive({ useHandCursor: true });
                    this.seniorClerk.on('pointerdown', () => {
                        if (this.dialogState === 'end' || !this.dialogState) {
                            this.showDialog('seniorClerk_start');
                        }
                    });
                }
                
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
        let questUpdates = [];
        const questSystem = this.registry.get('questSystem');
        if (questSystem && questSystem.getQuest('ortolan_arms')) {
            questUpdates = questSystem.getQuest('ortolan_arms')?.updates;
            console.log('updates', questUpdates)
        }
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
                onTrigger: () => {
                    this.dreamQueueChoices.sleeplessMime = 'memory';
                    this.safeModifyGrowthDecay(2, 0);
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
                onTrigger: () => {
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
                onTrigger: () => {
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
                onTrigger: () => {
                    this.dreamQueueChoices.vowelSeller = 'vowel';
                    this.safeModifyGrowthDecay(0, 1);
                    this.showNotification('Decay +1: A minor memory fades');
                    this.showNotification('Effect: Some characters may recognize your true name');
                    this.npcsInteractedWith.add('vowelSeller');
                }
            },
            vowelSeller_spores: {
                text: "(Their eyes widen slightly.)\n\n'The fungal tongue... I see. Then perhaps you might appreciate this instead.'\n\n(They hand you a small card with nothing written on it.)\n\n'A silent sentence. Use it when words fail you at the clerk's desk.'",
                options: [
                    { text: "I accept this gift.", next: "vowelSeller_end" }
                ],
                onTrigger: () => {
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
                }
            },
            vowelSeller_end: {
                text: "(The Vowel Seller nods and dissolves into a cloud of ash, their vials tinkling softly as they disappear.)",
                options: [
                    { text: "Continue waiting", next: "end" }
                ],
                onTrigger: () => {
                    // Fade out the Vowel Seller
                    this.tweens.add({
                        targets: [this.vowelSeller, this.vowelSellerAsh],
                        alpha: 0,
                        duration: 1500,
                        onComplete: () => {
                            this.vowelSeller.setVisible(false);
                            this.vowelSellerAsh.setVisible(false);
                            this.checkAllNPCsInteracted();
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
                onTrigger: () => {
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
                onTrigger: () => {
                    this.dreamQueueChoices.hollowWoman = 'empathy';
                    this.safeModifyGrowthDecay(3, 0);
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
                onTrigger: () => {
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
                ],
                onTrigger: () => {
                    // Ensure dialog stays open when transitioning to the next state
                    this.time.delayedCall(100, () => {
                        // Make sure we're still in this dialog state before proceeding
                        if (this.dialogState === 'seniorClerk_processing') {
                            // Keep the dialog active but ready for the next state
                            this.dialogActive = true;
                        }
                    });
                }
            },
            seniorClerk_proceed: {
                text: "(The Senior Clerk adjusts their spectacles and reviews your file.)\n\n'Now, let's begin the registration process. Based on your queue interactions, I see several possible paths forward.'",
                options: [
                    { text: "I'm ready to proceed.", next: "registration_start" }
                ],
                onTrigger: () => {
                    // Clean up any existing UI elements first
                    if (this.registrationDoor) {
                        this.registrationDoor.destroy();
                        this.registrationDoor = null;
                    }
                    if (this.doorGlow) {
                        this.doorGlow.destroy();
                        this.doorGlow = null;
                    }
                    if (this.registrationDesk) {
                        this.registrationDesk.destroy();
                        this.registrationDesk = null;
                    }
                    if (this.papers) {
                        this.papers.destroy();
                        this.papers = null;
                    }
                    if (this.deskGlow) {
                        this.deskGlow.destroy();
                        this.deskGlow = null;
                    }
                    
                    // Create the registration desk with papers
                    this.registrationDesk = this.add.image(600, 400, 'door')
                        .setDisplaySize(150, 100)
                        .setAlpha(0.7)
                        .setTint(0x8B4513);
                    
                    // Add papers on desk
                    this.papers = this.add.graphics();
                    this.papers.fillStyle(0xFFFFFF, 0.9);
                    this.papers.fillRect(550, 380, 80, 30);
                    this.papers.fillRect(590, 370, 70, 40);
                    
                    // Add glow effect
                    this.deskGlow = this.add.graphics();
                    this.deskGlow.fillStyle(0x7fff8e, 0.2);
                    this.deskGlow.fillCircle(600, 400, 80);
                }
            },
            registration_start: {
                text: "'Before we proceed, I need to know the purpose of your registration. What brings you to Shed13 today?'",
                options: [
                    { text: "I'm here for general registration.", next: "registration_general" },
                    { text: "I'd rather not say.", next: "registration_evasive" },
                    ...(questUpdates.some(update => update.key === 'artisan_form_clue') ? [{ text: "I need an Artisan's Exemption Form.", next: "registration_artisan" }] : []),
                    ...(questUpdates.some(update => update.key === 'deformity_form_clue') ? [{ text: "I need an Inherited Deformity Form.", next: "registration_deformity" }] : []),
                    ...(questUpdates.some(update => update.key === 'nonverbal_gesture_clue') ? [{ text: "(Make a nonverbal gesture)", next: "registration_nonverbal" }] : []),
                ],
            },
            registration_artisan: {
                text: "'Ah, the Artisan's Exemption Form. A rare request.'",
                options: [
                    { text: "It's for Ortolan, a board game designer.", next: "registration_artisan_ortolan" },
                    { text: "I need it for personal reasons.", next: "registration_artisan_personal" }
                ]
            },
            registration_artisan_ortolan: {
                text: "(The clerk's eyebrows raise slightly.)\n\n'Ortolan? The multi-limbed game designer? Interesting...'\n\n(They shuffle through papers and produce a complex form with intricate patterns.)\n\n'This form requires creative verification. Please demonstrate artistic merit.'",
                options: [
                    { text: "I can demonstrate my creativity.", next: "registration_creative_challenge" },
                    { text: "Perhaps another form would be better.", next: "registration_reconsider" }
                ]
            },
            registration_artisan_personal: {
                text: "'Personal reasons are insufficient for this form. It requires documented creative output.'",
                options: [
                    { text: "I can demonstrate my creativity.", next: "registration_creative_challenge" },
                    { text: "Perhaps another form would be better.", next: "registration_reconsider" }
                ]
            },
            registration_creative_challenge: {
                text: "'Very well. Please complete this pattern.'",
                options: [
                    ...(this.dreamQueueChoices.sleeplessMime === 'rulebook' ? [{ text: "(Show the rulebook fragment)", next: "registration_success_artisan" }] : []),
                    ...(this.dreamQueueChoices.hollowWoman === 'narrative' ? [{ text: "(Recite the bureaucratic incantation)", next: "registration_success_artisan" }] : []),
                    ...(this.dreamQueueChoices.vowelSeller === 'silence' ? [{ text: "(Draw a fungal pattern)", next: "registration_success_artisan" }] : []),
                    { text: "I can't do this.", next: "registration_failure" }
                ],
            },
            registration_deformity: {
                text: "'The Inherited Deformity Form? That's a sensitive document.'",
                options: [
                    { text: "It's for a friend with multiple arms.", next: "registration_deformity_friend" },
                    { text: "I need to understand the classification system.", next: "registration_deformity_system" }
                ]
            },
            registration_deformity_friend: {
                text: "'Multiple arms? Interesting. The form requires proof of beneficial mutation versus detrimental deformity.'",
                options: [
                    ...(this.dreamQueueChoices.hollowWoman === 'narrative' ? [{ text: "(Recite the bureaucratic incantation to bypass the clause)", next: "registration_success_deformity" }] : []),
                    ...(this.dreamQueueChoices.hollowWoman === 'empathy' ? [{ text: "(Offer a symbolic gesture of shared experience)", next: "registration_success_deformity" }] : []),
                    ...(this.dreamQueueChoices.sleeplessMime === 'rulebook' ? [{ text: "(Show the rulebook fragment)", next: "registration_success_deformity" }] : []),
                    { text: "I don't have proof.", next: "registration_failure" }
                ],
            },
            registration_deformity_system: {
                text: "'The classification system is complex. It requires specialized knowledge.'",
                options: [
                    { text: "I have some experience with bureaucracy.", next: "registration_bureaucracy_challenge" },
                    { text: "Perhaps I should try a different approach.", next: "registration_reconsider" }
                ]
            },
            registration_bureaucracy_challenge: {
                text: "'Demonstrate your understanding of Form Section 7-B.'",
                options: [
                    ...(this.dreamQueueChoices.hollowWoman === 'narrative' ? [{ text: "Section 7-B relates to the Inherited Deformity clause, which can be bypassed with proper documentation.", next: "registration_success_deformity" }] : []),
                    ...(this.dreamQueueChoices.vowelSeller === 'vowel' ? [{ text: "Section 7-B covers beneficial mutations.", next: "registration_partial_success" }] : []),
                    { text: "I'm not familiar with Section 7-B.", next: "registration_failure" }
                ],
            },
            registration_nonverbal: {
                text: "(The clerk watches your gesture with interest.)\n\n'Ah, nonverbal communication. A rare approach in bureaucracy.'",
                options: [
                    ...(this.dreamQueueChoices.sleeplessMime === 'memory' || this.dreamQueueChoices.sleeplessMime === 'rulebook' ? [{ text: "(Mime a complex game being played)", next: "registration_success_nonverbal" }] : []),
                    ...(this.dreamQueueChoices.vowelSeller === 'silence' ? [{ text: "(Present the Silent Sentence card)", next: "registration_success_nonverbal" }] : []),
                    { text: "I can't do this.", next: "registration_failure" }
                ],
            },
            registration_general: {
                text: "'General registration requires specific purpose. Shed13 doesn't accept visitors without purpose.'",
                options: [
                    { text: "I'm interested in the fungal research.", next: "registration_fungal" },
                    { text: "I'm here on behalf of someone else.", next: "registration_proxy" },
                    { text: "Perhaps I should be more specific.", next: "registration_reconsider" }
                ]
            },
            registration_fungal: {
                text: "'Fungal research access requires specialized clearance and growth/decay balance verification.'",
                options: [
                    ...(this.dreamQueueChoices.hollowWoman === 'empathy' ? [{ text: "I can help you recover old tech carefully", next: "registration_success_fungal" }] : []),
                    ...(this.dreamQueueChoices.sleeplessMime === 'memory' || this.dreamQueueChoices.sleeplessMime === 'rulebook' ? [{ text: "I can help you recover old tech carefully", next: "registration_success_fungal" }] : []),
                    { text: "I don't have qualifications yet.", next: "registration_failure" }
                ],
            },
            registration_proxy: {
                text: "'Proxy registration requires authorization from the principal party.'",
                options: [
                    ...(this.dreamQueueChoices.vowelSeller === 'vowel' ? [{ text: "(Speak the principal's true name with the vowel you purchased)", next: "registration_success_proxy" }] : []),
                    { text: "I don't have authorization.", next: "registration_failure" }
                ],

            },
            registration_evasive: {
                text: "(The clerk's expression hardens.)\n\n'Evasiveness is noted in your file. This complicates the process.'",
                options: [
                    { text: "I apologize. Let me be more specific.", next: "registration_reconsider" },
                    { text: "I have my reasons for discretion.", next: "registration_discretion" }
                ]
            },
            registration_discretion: {
                text: "'Discretion requires additional verification.'",
                options: [
                    ...(this.dreamQueueChoices.vowelSeller === 'silence' ? [{ text: "(Present the Silent Sentence card)", next: "registration_partial_success" }] : []),
                    { text: "I understand the need for verification.", next: "registration_failure" },
                    { text: "I refuse further verification.", next: "registration_failure" }
                ],
            },
            registration_reconsider: {
                text: "'Very well. Let's start again.'",
                options: [
                    { text: "Continue", next: "registration_start" }
                ]
            },
            registration_success_artisan: {
                text: "(The clerk stamps the Artisan's Exemption Form with a flourish.)\n\n'Approved. The form grants creative exemption from standard limb restrictions. Ortolan will be pleased.'",
                options: [
                    { text: "Thank you.", next: "registration_complete_success" }
                ],
                onTrigger: () => {
                    // Add form to inventory
                    this.addItemToInventory({
                        id: 'artisan-exemption-form',
                        name: "Artisan's Exemption Form",
                        description: "Official form granting exemption from standard limb restrictions for creative purposes. Approved for Ortolan.",
                        stackable: false
                    });
                    this.showNotification('Received: Artisan\'s Exemption Form');
                    
                    // Update quest
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && questSystem.getQuest('ortolan_arms')) {
                        questSystem.updateQuest(
                            'ortolan_arms', 
                            'I successfully obtained the Artisan\'s Exemption Form for Ortolan. This should help with the bureaucratic hurdles for additional arms.',
                            'form_obtained'
                        );
                        this.showNotification('Quest updated: Ortolan Arms Investigation');
                    }
                    
                    // Increase Growth
                    this.safeModifyGrowthDecay(3, 0);
                    this.showNotification('Growth +3: Creative bureaucracy mastered');
                }
            },
            registration_success_deformity: {
                text: "(The clerk stamps the Inherited Deformity Form with precision.)\n\n'Approved. This form acknowledges beneficial mutation status for multiple limbs. A rare classification.'",
                options: [
                    { text: "Thank you.", next: "registration_complete_success" }
                ],
                onTrigger: () => {
                    // Add form to inventory
                    this.addItemToInventory({
                        id: 'deformity-form',
                        name: "Inherited Deformity Form",
                        description: "Official form classifying multiple limbs as beneficial mutations rather than deformities. Approved for use.",
                        stackable: false
                    });
                    this.showNotification('Received: Inherited Deformity Form');
                    
                    // Update quest
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && questSystem.getQuest('ortolan_arms')) {
                        questSystem.updateQuest(
                            'ortolan_arms', 
                            'I successfully obtained the Inherited Deformity Form. This should help Ortolan with the bureaucratic hurdles for additional arms.',
                            'form_obtained'
                        );
                        this.showNotification('Quest updated: Ortolan Arms Investigation');
                    }
                    
                    // Increase Growth
                    this.safeModifyGrowthDecay(3, 0);
                    this.showNotification('Growth +3: Bureaucratic mastery achieved');
                }
            },
            registration_success_nonverbal: {
                text: "(The clerk nods with unexpected understanding.)\n\n'Your nonverbal application is... approved. This special dispensation allows for limb modification without standard documentation.'",
                options: [
                    { text: "(Nod gratefully)", next: "registration_complete_success" }
                ],
                onTrigger: () => {
                    // Add dispensation to inventory
                    this.addItemToInventory({
                        id: 'special-dispensation',
                        name: "Special Dispensation",
                        description: "A rare document allowing limb modification without standard paperwork. Obtained through nonverbal means.",
                        stackable: false
                    });
                    this.showNotification('Received: Special Dispensation');
                    
                    // Update quest
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && questSystem.getQuest('ortolan_arms')) {
                        questSystem.updateQuest(
                            'ortolan_arms', 
                            'I successfully obtained a Special Dispensation through nonverbal means. This should help Ortolan bypass the bureaucracy for additional arms.',
                            'form_obtained'
                        );
                        this.showNotification('Quest updated: Ortolan Arms Investigation');
                    }
                    
                    // Increase Growth
                    this.safeModifyGrowthDecay(4, 0);
                    this.showNotification('Growth +4: Transcended verbal bureaucracy');
                }
            },
            registration_success_fungal: {
                text: "(The clerk stamps a form with a fungal seal.)\n\n'Approved for fungal research access. Level 2 clearance granted. The mycologists will be notified of your arrival.'",
                options: [
                    { text: "Thank you.", next: "registration_complete_success" }
                ],
                onTrigger: () => {
                    // Add clearance to inventory
                    this.addItemToInventory({
                        id: 'fungal-clearance',
                        name: "Fungal Research Clearance",
                        description: "Level 2 clearance for accessing fungal research areas in Shed13. A valuable credential.",
                        stackable: false
                    });
                    this.showNotification('Received: Fungal Research Clearance');
                    
                    // Increase Growth
                    this.safeModifyGrowthDecay(2, 0);
                    this.showNotification('Growth +2: Scientific recognition');
                }
            },
            registration_success_proxy: {
                text: "(The clerk's eyes widen slightly.)\n\n'The true name... I see. Proxy authorization granted. This document allows you to act on behalf of the named individual.'",
                options: [
                    { text: "Thank you.", next: "registration_complete_success" }
                ],
                onTrigger: () => {
                    // Add proxy form to inventory
                    this.addItemToInventory({
                        id: 'proxy-authorization',
                        name: "Proxy Authorization",
                        description: "Official document allowing you to act on behalf of another individual in Shed13 bureaucratic matters.",
                        stackable: false
                    });
                    this.showNotification('Received: Proxy Authorization');
                    
                    // Increase Growth
                    this.safeModifyGrowthDecay(2, 0);
                    this.showNotification('Growth +2: Identity flexibility');
                }
            },
            registration_partial_success: {
                text: "(The clerk hesitates, then stamps a form with a provisional mark.)\n\n'Partially approved. This temporary permit grants limited access. Full approval requires additional documentation in the future.'",
                options: [
                    { text: "I understand.", next: "registration_complete_partial" }
                ],
                onTrigger: () => {
                    // Add temporary permit to inventory
                    this.addItemToInventory({
                        id: 'temporary-permit',
                        name: "Temporary Permit",
                        description: "A provisional document granting limited access. Not fully approved, but better than nothing.",
                        stackable: false
                    });
                    this.showNotification('Received: Temporary Permit');
                    
                    // Update quest if relevant
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && questSystem.getQuest('ortolan_arms')) {
                        questSystem.updateQuest(
                            'ortolan_arms', 
                            'I obtained a Temporary Permit that might help Ortolan, but it\'s not fully approved. I may need to find another solution.',
                            'partial_progress'
                        );
                        this.showNotification('Quest updated: Ortolan Arms Investigation');
                    }
                    
                    // Balanced Growth/Decay
                    this.safeModifyGrowthDecay(1, 1);
                    this.showNotification('Growth +1, Decay +1: Bureaucratic compromise');
                }
            },
            registration_failure: {
                text: "(The clerk stamps 'REJECTED' on the form with finality.)\n\n'Your application is denied. Insufficient qualification, documentation, or purpose. You may reapply after a standard waiting period of 47 days.'",
                options: [
                    { text: "I see...", next: "registration_complete_failure" }
                ],
                onTrigger: () => {
                    // Increase Decay
                    this.safeModifyGrowthDecay(0, 3);
                    this.showNotification('Decay +3: Bureaucratic rejection');
                    
                    // Update quest if relevant
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && questSystem.getQuest('ortolan_arms')) {
                        questSystem.updateQuest(
                            'ortolan_arms', 
                            'My registration attempt failed. I\'ll need to find another way to help Ortolan with the arm situation.',
                            'failed_attempt'
                        );
                        this.showNotification('Quest updated: Ortolan Arms Investigation');
                    }
                }
            },
            registration_complete_success: {
                text: "(The Senior Clerk gestures to a door that wasn't there before, glowing with a soft green light.)\n\n'Your registration is complete. You may proceed through the green door to finalize your documentation.'",
                options: [
                    { text: "Enter the door", next: "seniorClerk_end" }
                ],
                onTrigger: () => {
                    // Clean up any existing UI elements first
                    if (this.registrationDesk) {
                        this.registrationDesk.destroy();
                        this.registrationDesk = null;
                    }
                    if (this.papers) {
                        this.papers.destroy();
                        this.papers = null;
                    }
                    if (this.deskGlow) {
                        this.deskGlow.destroy();
                        this.deskGlow = null;
                    }
                    if (this.registrationDoor) {
                        this.registrationDoor.destroy();
                        this.registrationDoor = null;
                    }
                    if (this.doorGlow) {
                        this.doorGlow.destroy();
                        this.doorGlow = null;
                    }
                    
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
            registration_complete_partial: {
                text: "(The Senior Clerk gestures to a door that wasn't there before, glowing with a muted yellow-green light.)\n\n'Your provisional registration is recorded. You may proceed, but expect additional scrutiny in sensitive areas.'",
                options: [
                    { text: "Enter the door", next: "seniorClerk_end" }
                ],
                onTrigger: () => {
                    // Clean up any existing UI elements first
                    if (this.registrationDesk) {
                        this.registrationDesk.destroy();
                        this.registrationDesk = null;
                    }
                    if (this.papers) {
                        this.papers.destroy();
                        this.papers = null;
                    }
                    if (this.deskGlow) {
                        this.deskGlow.destroy();
                        this.deskGlow = null;
                    }
                    if (this.registrationDoor) {
                        this.registrationDoor.destroy();
                        this.registrationDoor = null;
                    }
                    if (this.doorGlow) {
                        this.doorGlow.destroy();
                        this.doorGlow = null;
                    }
                    
                    // Create the new door with yellow-green glow
                    this.registrationDoor = this.add.image(600, 400, 'door')
                        .setDisplaySize(100, 150)
                        .setInteractive({ useHandCursor: true });
                    
                    // Add glow effect
                    this.doorGlow = this.add.graphics();
                    this.doorGlow.fillStyle(0xaaff4d, 0.3); // Yellow-green
                    this.doorGlow.fillCircle(600, 400, 80);
                    
                    // Make the door interactive
                    this.registrationDoor.on('pointerdown', () => {
                        this.hideDialog();
                        this.proceedToRegistrationOffice();
                    });
                }
            },
            registration_complete_failure: {
                text: "(The Senior Clerk gestures to a door that wasn't there before, glowing with a dull red light.)\n\n'You may exit through this door. Your rejection has been recorded. Better luck in 47 days.'",
                options: [
                    { text: "Enter the door", next: "seniorClerk_end" }
                ],
                onTrigger: () => {
                    // Clean up any existing UI elements first
                    if (this.registrationDesk) {
                        this.registrationDesk.destroy();
                        this.registrationDesk = null;
                    }
                    if (this.papers) {
                        this.papers.destroy();
                        this.papers = null;
                    }
                    if (this.deskGlow) {
                        this.deskGlow.destroy();
                        this.deskGlow = null;
                    }
                    if (this.registrationDoor) {
                        this.registrationDoor.destroy();
                        this.registrationDoor = null;
                    }
                    if (this.doorGlow) {
                        this.doorGlow.destroy();
                        this.doorGlow = null;
                    }
                    
                    // Create the new door with red glow
                    this.registrationDoor = this.add.image(600, 400, 'door')
                        .setDisplaySize(100, 150)
                        .setInteractive({ useHandCursor: true });
                    
                    // Add glow effect
                    this.doorGlow = this.add.graphics();
                    this.doorGlow.fillStyle(0xff4d4d, 0.3); // Red
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
                onTrigger: () => {
                    this.hideDialog();
                }
            },
            end: {
                text: "",
                options: [],
                onTrigger: () => {
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
    
    // Helper method to dynamically set dialog options
    setDialogOptions(dialogKey, options) {
        // Find the dialog in the current dialog content
        const dialogContent = this.dialogContent;
        
        if (dialogContent[dialogKey]) {
            // Update the options for this dialog
            dialogContent[dialogKey].options = options;
            
            // If dialog is currently showing, refresh it
            if (this.dialogState === dialogKey && this.dialogBox && this.dialogBox.visible) {
                // Hide current dialog and show it again with updated options
                this.hideDialog();
                this.showDialog(dialogKey);
            }
        }
    }
}
