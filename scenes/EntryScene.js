import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';

export default class EntryScene extends GameScene {
    constructor() {
        super({ key: 'EntryScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    get dialogContent() {
        return {
            ...super.dialogContent, // Include parent dialog content for symbiont dialogs
            main: {
                text: "Ah, my apprentice, there you are! *sigh* I've been waiting for you. Listen carefully, for I have an important task that requires... well, someone of your particular talents.",
                options: [
                    { text: "What task, Master?", next: 'task' },
                    { text: "Why can't you do it yourself?", next: 'whyNot' }
                ],
                onTrigger: () => {
                    this.addJournalEntry(
                        'obazoba_cult',
                        'Obazoba Cult',
                        'The Obazoba Cult is a cult of fungal worshippers that worships the Obazoba, a fungal deity that is said to be the source of all life and rot. The cult is known for modifying their bodies to grow fungal spores. The cultists are partially human and partially mushrooms. You are, of course, a fungal apprentice of this cult. Congratulations!',
                        this.journalSystem.categories.LORE,
                        { location: 'Obazoba Cult' }
                    );
                    // Add journal entry about skyship seen above the city
                    if (!this.hasJournalEntry('upper_morkezela')) {
                        this.addJournalEntry(
                            'upper_morkezela',
                            'Upper Morkezela',
                            'They call it a city, but Upper Morkezela was never fully alive. It grew like a misunderstanding — a mistake made permanent by concrete, ritual, and time. The streets curve inward. And no one knows who is in charge, there are several factions fighting for control. "In Morkezela, your second shadow watches the first. Neither trusts you." — Anonymous graffito, scratched into the side of a forgotten monorail',
                            this.journalSystem.categories.PLACES,
                            { location: 'Upper Morkezela skyline' }
                        );
                    }
                    
                    // Add journal entry about being an apprentice
                    if (!this.hasJournalEntry('fungal_apprentice')) {
                        this.addJournalEntry(
                            'fungal_apprentice',
                            'Fungal Apprentice',
                            'As the newest apprentice to Fungal Master Thaal, I have much to learn about the spores, the city, and the strange ways of the fungal clergy. My master is... eccentric, to say the least. He seems to have a habit of assigning me tasks he finds beneath his station.',
                            this.journalSystem.categories.PEOPLE,
                            { relationship: 'Player character' }
                        );
                    }
                    
                    // Add journal entry about the fungal master
                    if (this.journalSystem && !this.hasJournalEntry('fungal_master')) {
                        this.addJournalEntry(
                            'fungal_master',
                            'Fungal Master Thaal',
                            'The eccentric Fungal Master Thaal is known for his vast knowledge of spores and his equally vast disinterest in doing any actual work. He prefers to delegate tasks to his apprentices while he engages in "important spiritual communion" at the local tavern.',
                            this.journalSystem.categories.PEOPLE,
                            { relationship: 'Master' }
                        );
                    }
                    
                    // Start the find_bishop quest
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && !questSystem.getQuest('find_bishop')) {
                        questSystem.addQuest(
                            'find_bishop',
                            'Find the Bishop',
                            'The Fungal Master has tasked me with finding the Bishop at the Egg Cathedral. She might know about the distress call received from the city via the myceliar network. I need to speak with her to learn more.'
                        );
                    }
                    
                    // Listen for dialog closed event to make the master walk away
                    this.events.once('dialog-closed', this.masterWalkAway.bind(this));
                }
            },
            task: {
                text: "You must find the Bishop at the Egg Cathedral. She might knows about the distress call we have received from this city via myceliar network. The Bishop should be present at the Egg Cathedral.",
                options: [
                    { text: "Wait, do you mean the task you have been given by the Spore Council? The only reason we are here? Why can't we go see the Bishop together?", next: 'whyNot' },
                    { text: "Tell me more about the city first", next: 'city' },
                ]
            },
            whyNot: {
                text: "*adjusts robe importantly* I am far too busy with... important research. Yes! Research into advanced mycological phenomena that your novice mind couldn't possibly comprehend. Besides, I have a... prior engagement at the Fermented Cap tavern. The Bishop specifically requested someone of your... particular level of experience.",
                options: [
                    { text: "You're just avoiding work, aren't you?", next: 'avoiding' },
                    { text: "What should I tell the Bishop when I find him?", next: 'tellBishop' },
                    { text: "Tell me more about the city first", next: 'city' }
                ]
            },
            avoiding: {
                text: "*huffs indignantly* How dare you! I am conducting vital... spiritual communion with the fermented spirits. It's a sacred ritual that requires my full attention and several mugs of mushroom ale. Now, off you go! The Bishop awaits, and this is excellent training for you. Consider yourself fortunate!",
                options: [
                    { text: "What should I tell the Bishop when I find him?", next: 'tellBishop' },
                    { text: "Tell me more about the city first", next: 'city' },
                    { text: "Master, I have heard that Upper Morkezela is called the Dead gods city. Could you tell me more?", next: 'gods' }
                ]
            },
            tellBishop: {
                text: "Tell her you're my apprentice, sent to assist with the spore disturbance investigation. She'll know what to do. And remember to represent the fungal clergy with dignity! No embarrassing me this time. Now, was there anything else you needed to know before you go?",
                options: [
                    { text: "Tell me more about the city", next: 'city' },
                    { text: "Who are the gods?", next: 'gods' },
                    { text: "I'll be on my way", next: 'farewell' }
                ]
            },
            farewell: {
                text: "Excellent! The Egg Cathedral is just to the east. And if anyone asks, tell them I'm engaged in VERY important spiritual communion that cannot be disturbed. Now off you go, apprentice! Glory to the Great Fruiting!",
                options: [
                    { text: "Glory to the Great Fruiting...", next: 'close' }
                ]
            },
            close: {
                text: "*waves dismissively while eyeing the path to the tavern*",
                options: []
            },
            city: {
                text: "Upper Morkezela... it breathes with ancient spores. The buildings grow like mushrooms in the dark, their patterns shifting when no one watches. Some say the entire city is a graveyard of forgotten gods from many spheres. Each time people cease to believe in some god, the grows. The dying gods bring streets, building and forgotten culture with them. They don't want to be alone in the void, afterlife or whatever there is for them after they die, you know. ",
                options: [
                    { text: "Ask about the gods", next: 'gods' },
                    { text: "Do you have any advice for me?", next: 'advice' },
                    { text: "Tell me more about city locations.", next: 'locations' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            advice: {
                text: "Remember, all your actions have consequences. Some of them will cause the city to grow, some will cause it to rot and decay. Your action can change the city and its future. They can change how the city will look and how its inhabitants will live and react to you.",
                options: [
                    { text: "Ask about the gods", next: 'gods' },
                    { text: "Tell me more about city locations.", next: 'locations' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            gods: {
                text: "You know, or you should know, that there is only one real god. Obozoba, the Ur-mushroom, the one who created the world and all life and death in it. The other gods are just illusions... but yeah, this is a city where gods are going to die. See, not all gods live forever.",
                options: [
                    { text: "Ask about the city", next: 'city' },
                    { text: "Where can I learn more about the gods?", next: 'priests' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            priests: {
                text: "Go to the Egg Catedral and talk to some of the priests there. They are always happy to chat. I mean, talk to the our priest or the Bistop. Don't talk to the other god's priests. I mean, the false gods' priests. The false priests. Ehm. You get me.",
                options: [
                    { text: "Could you tell me more about the Egg Catedral?", next: 'eggCatedral' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            eggCatedral: {
                text: "The Egg Cathedral is, well, a huge catedral that is hatching from gigantic egg. A massive, shell-grown structure inhabited by fungal clergy, flickering with bio-luminescent scripture... They don't know which to which religion the cathedral belongs. So all major churches send their priest just to be sure. They wait for the signs they hope for, but the cathedral is still hatching...",
                options: [
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            locations: {
                text: "The city has many locations, but the most significant ones are the Yolk Sea, Shed 512, Scraper 1140, Voxmarket, and the Stomach Clock. Which one interests you?",
                options: [
                    { text: "Shed 512", next: 'shed512' },
                    { text: "Yolk Sea", next: 'yolkSea' },
                    { text: "Scraper 1140", next: 'scraper1140' },
                    { text: "Voxmarket", next: 'voxmarket' },
                    { text: "Stomach Clock", next: 'stomachClock' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            shed512: {
                text: "Shed 512, also known as the Bureau of Shapes. A twisted bureaucracy in an old shipping yard turned into an ever-expanding cubicle labyrinth. People come here to register their current form or apply for bodily adjustments. You can find it right next to the Voxmarket",
                options: [
                    { text: "What is the Egg Cathedral?", next: 'eggCatedral' },
                    { text: "What is the Yolk Sea?", next: 'yolkSea' },
                    { text: "What is the Scraper 1140", next: 'scraper1140' },
                    { text: "What is the Voxmarket?", next: 'voxmarket' },
                    { text: "What is the Stomach Clock?", next: 'stomachClock' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            yolkSea: {
                text: "The Yolk Sea is a glowing, sentient ocean of living yolk. Boats float like seeds, and whispers rise from its depths.",
                options: [
                    { text: "What is the Shed 512?", next: 'shed512' },
                    { text: "What is the Scraper 1140", next: 'scraper1140' },
                    { text: "What is the Voxmarket?", next: 'voxmarket' },
                    { text: "What is the Stomach Clock?", next: 'stomachClock' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            scraper1140: {
                text: "It's a crooked skyscraper retrofitted into a vertical slum. Each floor houses a different caste, age, or species. I'm afraid I don't know much about it, but I would be careful around this place",
                options: [
                    { text: "What is the Shed 512?", next: 'shed512' },
                    { text: "What is the Scraper 1140", next: 'scraper1140' },
                    { text: "What is the Stomach Clock?", next: 'stomachClock' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            voxmarket: {
                text: "The Voxmarket is a bustling marketplace... audio bazaar where recorded voices, sounds, and thoughts are sold. Stalls display silent conversation loops. You can buy the sound of someone’s first heartbreak or a scream from before fire existed. I have heard that also black market thrives here.",
                options: [
                    { text: "What is the Shed 512?", next: 'shed512' },
                    { text: "What is the Scraper 1140", next: 'scraper1140' },
                    { text: "What is the Stomach Clock?", next: 'stomachClock' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            },
            stomachClock: {
                text: "The Stomach Clock is a biomechanical chamber shaped like a digestive clock. Time runs in loops; bile is sacred. You can see it at the townhall",
                options: [
                    { text: "What is the Shed 512?", next: 'shed512' },
                    { text: "What is the Scraper 1140", next: 'scraper1140' },
                    { text: "What is the Voxmarket?", next: 'voxmarket' },
                    { text: "Return to previous topic", next: 'main' }
                ]
            }
        };
    }

    preload() {
        super.preload();
        // Load any EntryScene-specific assets here
        this.load.image('desolateUrban', 'assets/images/backgrounds/Desolate Urban Landscape.png');
        // Load fungal master sprite as a regular image since it's not a spritesheet
        this.load.image('fungal_master', 'assets/images/characters/fungal_master.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Create the parallax layers
        this.createParallaxLayers();
        
        // Create city background after parallax layers
        this.createCityBackground();
        
        // Create fungal master after mechanics are initialized
        this.createFungalMaster();
        
        // Create transition zone to EggCatedralScene at the right edge
        this.transitionManager.createTransitionZone(
            780, // x position
            470, // y position
            40,  // width
            200, // height
            'right', // direction
            'EggCatedralScene', // target scene
            100, // walk to x in target scene
            470  // walk to y in target scene
        );
        
        // Start background music
        this.playSceneMusic('backgroundMusic');

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
        
        // Set up the apprentice entrance sequence
        this.setupApprenticeEntrance();
    }

    createCityBackground() {
        // Add the city background
        const bg = this.add.image(400, 300, 'cityBackground');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-2); // Set lower depth for background
    }

    createParallaxLayers() {
        const layer1X = 470;
        const layer2X = layer1X + 800;

        // Create two copies of the foreground for infinite scrolling
        this.foreground1 = this.add.image(layer1X, 220, 'desolateUrban');
        this.foreground2 = this.add.image(layer2X, 220, 'desolateUrban');

        // Set up both layers
        [this.foreground1, this.foreground2].forEach(fg => {
            fg.setDisplaySize(800, 600);
            fg.setDepth(0);
            fg.setBlendMode(Phaser.BlendModes.MULTIPLY);
        });

        // Flip the second layer horizontally
        this.foreground2.setScale(-1, 1);
        
        // Store initial positions using the same constants
        this.foreground1.initialX = layer1X;
        this.foreground2.initialX = layer2X;
        if (this.priest) {
            this.priest.initialX = this.priest.x;
        }
    }

    createFungalMaster() {
        // Add the fungal master character
        this.master = this.add.image(600, 470, 'fungal_master');
        
        // Scale down the master image as it's a large image
        this.master.setScale(0.15);  // Adjust scale to fit the scene
        this.master.setInteractive({ useHandCursor: true });
        
        // Add a green glow effect for the fungal appearance
        const masterGlowFX = this.add.image(600, 470, 'fungal_master');
        masterGlowFX.setScale(0.155);  // Slightly larger than the character
        masterGlowFX.setTint(0x00FF00);  // Green glow
        masterGlowFX.setAlpha(0.3);  // Transparent glow
        masterGlowFX.setBlendMode(Phaser.BlendModes.ADD);  // Additive blending for glow effect
        this.masterGlow = masterGlowFX;
        
        // Add pulsating effect to the glow
        this.tweens.add({
            targets: this.masterGlow,
            alpha: 0.5,
            duration: 1500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Add subtle breathing animation to the master
        this.tweens.add({
            targets: this.master,
            scaleX: this.master.scaleX * 1.02,
            scaleY: this.master.scaleY * 1.02,
            duration: 2000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Add click handler for NPC
        this.master.on('pointerdown', () => {
            if (!this.dialogVisible) {
                this.clickSound.play();
                this.showDialog('main');
            }
        });
    }

    update() {
        super.update();

        // Update parallax based on character movement
        if (this.priest && this.foreground1 && this.foreground2 && !this.dialogVisible) {
            // Calculate how far the character has moved from their initial position
            const characterOffset = this.priest.x - this.priest.initialX;
            
            // Apply inverse parallax effect (move foreground in opposite direction)
            const parallaxSpeed = 0.3;
            
            // Update both foreground positions
            this.foreground1.x = this.foreground1.initialX - (characterOffset * parallaxSpeed);
            this.foreground2.x = this.foreground2.initialX - (characterOffset * parallaxSpeed);
            
            // Keep vertical positions fixed
            this.foreground1.y = 220;
            this.foreground2.y = 220;

            // Check if we need to reset positions
            const screenWidth = 800;
            const resetThreshold = screenWidth / 2;

            // If first image moves too far left, move it to the right
            if (this.foreground1.x < -resetThreshold) {
                this.foreground1.x += screenWidth;
                this.foreground1.initialX += screenWidth;
            }
            // If second image moves too far left, move it to the right
            if (this.foreground2.x < -resetThreshold) {
                this.foreground2.x += screenWidth;
                this.foreground2.initialX += screenWidth;
            }
            // If first image moves too far right, move it to the left
            if (this.foreground1.x > screenWidth * 1.5) {
                this.foreground1.x -= screenWidth;
                this.foreground1.initialX -= screenWidth;
            }
            // If second image moves too far right, move it to the left
            if (this.foreground2.x > screenWidth * 1.5) {
                this.foreground2.x -= screenWidth;
                this.foreground2.initialX -= screenWidth;
            }
        }
        
        // Update master glow position if it exists
        if (this.master && this.masterGlow) {
            this.masterGlow.x = this.master.x;
            this.masterGlow.y = this.master.y;
        }
        
        // Update priestGlow position if it exists to follow the apprentice
        if (this.priest && this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // No need to check for edge transitions as SceneTransitionManager handles this
    }
    
    /**
     * Set up the apprentice entrance sequence
     */
    setupApprenticeEntrance() {
        // Temporarily disable player controls
        if (this.playerMovementSystem) {
            this.playerMovementSystem.disableControls();
        }
        
        // Position the apprentice off-screen to the left
        if (this.priest) {
            this.priest.x = -50;
            this.priest.initialX = -50;
            
            // Rename the priest to apprentice for clarity
            this.apprentice = this.priest;
            
            // Play walking animation
            this.apprentice.play('walk');
            
            // Create a tween to move the apprentice into the scene
            this.tweens.add({
                targets: this.apprentice,
                x: 200,
                duration: 3000,
                ease: 'Linear',
                onComplete: () => {
                    // Stop walking animation
                    this.apprentice.play('idle');
                    
                    // Show dialog after a short delay
                    this.time.delayedCall(500, () => {
                        this.showDialog('main');
                    });
                    
                    // Re-enable controls after dialog closes
                    this.events.once('dialog-closed', () => {
                        if (this.playerMovementSystem) {
                            this.playerMovementSystem.enableControls();
                        }
                    });
                }
            });
            
            // Make the glow follow the apprentice
            if (this.priestGlow) {
                this.priestGlow.x = this.apprentice.x;
                this.priestGlow.y = this.apprentice.y;
            }
        }
    }
    
    /**
     * Override hideDialog to emit the dialog-closed event
     */
    hideDialog() {
        // Call the parent method first
        super.hideDialog();
        
        // Emit the dialog-closed event
        this.events.emit('dialog-closed');
    }
    
    /**
     * Make the fungal master walk away after dialog closes
     */
    masterWalkAway() {
        if (this.master && this.masterGlow) {
            // Create a tween to make the master walk to the right and disappear
            this.tweens.add({
                targets: [this.master, this.masterGlow],
                x: 900, // Walk off the right side of the screen
                duration: 5000,
                ease: 'Linear',
                onComplete: () => {
                    // Remove the master and glow when they're off-screen
                    this.master.destroy();
                    this.masterGlow.destroy();
                    
                    // Add a notification that the master has left
                    if (this.showNotification) {
                        this.showNotification('The Fungal Master has departed for the tavern...');
                    }
                }
            });
        }
    }
}
