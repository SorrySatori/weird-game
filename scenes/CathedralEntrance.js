import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class CathedralEntrance extends GameScene {
    constructor() {
        super({ key: 'CathedralEntrance' });
        this.isTransitioning = false; // Add flag to track transition state
        
        // Store temple guard dialog content in a separate property
        this._templeGuardDialogContent = {
            speaker: 'Temple Guard',
            templeGuardGreeting: {
        text: "Halt. The yolk sleeps uneasily today. Entry to the Egg Cathedral is… temporarily restricted.",
                options: [
                    { text: "When will it open?", key: 'when_will_it_open', next: "templeGuardWhen" },
                    { text: "Why is it closed?", key: 'why_is_it_closed', next: "templeGuardWhy" },
                    { text: "Who are you?", key: 'who_are_you', next: "templeGuardWho" },
                    { text: "I need to speak with someone inside", key: 'i_need_to_speak_with_someone_inside', next: "speakWithSomeoneInside" },
                    { text: "I'm a master Thaal's apprentice. Surely I may pass.", key: 'im_a_master_thaals_apprentice_surely_i_may_pass', next: "iAmFungalApprentice" }
                ]
            },
            templeGuardAskSomethingElse: {
        text: "Is there anything else I can help you with?",
                options: [
                    { text: "When will it open?", key: 'when_will_it_open', next: "templeGuardWhen" },
                    { text: "Why is it closed?", key: 'why_is_it_closed', next: "templeGuardWhy" },
                    { text: "Who are you?", key: 'who_are_you', next: "templeGuardWho" },
                    { text: "I need to speak with someone inside", key: 'i_need_to_speak_with_someone_inside', next: "speakWithSomeoneInside" },
                    { text: "I'm a master Thaal's apprentice. Surely I may pass.", key: 'im_a_master_thaals_apprentice_surely_i_may_pass', next: "iAmFungalApprentice" }
                ]
            },
            iAmFungalApprentice: {
        text: "(Tilts head) Even rot-born clergy must heed the pulses. The Cathedral breathes its own rhythm. You must attune.",
                options: [
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardWhen: {
        text: "I have no idea. When the great Council say so. It could be days, it could be centuries. We stand guard until the Awakening.",
                options: [
                    { text: "The Awakening?", key: 'the_awakening', next: "templeGuardAwakening" },
                    { text: "Where can I find the Bishop?", key: 'where_can_i_find_the_bishop', next: "bishop_info" },
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardGreeting" }
                ]
            },
            templeGuardAwakening: {
        text: "The Awakening is the moment when's the cathedral fully grown. Hatched. We stand guard until the Awakening.",
                options: [
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardGreeting" }
                ]
            },
            speakWithSomeoneInside: {
                text: "No summons have been issued. No minds may enter without resonance. Wait. Or seek for your Bishop. She's one of the Council, I am sure you know.",
                options: [
                    { text: "I'm a master Thaal's apprentice. Surely I may pass.", key: 'im_a_master_thaals_apprentice_surely_i_may_pass', next: "iAmFungalApprentice" },
                    { text: "Where can I find the Bishop?", key: 'where_can_i_find_the_bishop', next: "bishop_info" },
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" }
                ]
            },
            bishop_info: {
        text: "Probably at the Voxmarket, or around Shed 521. She dwells where the walls still echo with initiation. Look for the door that doesn’t open—until it does",
                options: [
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" },
                    { text: "What is the Voxmarket?", key: 'what_is_the_voxmarket', next: "templeGuardVoxmarket"},
                    {text: "What is the Shed 521?", key: 'what_is_the_shed_521', next: "templeGuardShed521"},
                ]
            },
            templeGuardVoxmarket: {
                text: "It's an audio bazaar near Shed 521 where recorded voices, sounds, and thoughts are sold. Stalls display silent conversation loops. You can buy the sound of someone’s first heartbreak or a scream from before fire existed.",
                options: [
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" },
                    { text: "What is the Shed 521?", key: 'what_is_the_shed_521', next: "templeGuardShed521" },
                ]
            },
            templeGuardShed521: {
                text: "It's also known as the Bureau of Shapes. A twisted bureaucracy in an old shipping yard turned into an ever-expanding cubicle labyrinth. People come here to register their current form or apply for bodily adjustments. You can find it right next to the Voxmarket",
                options: [
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" },
                    { text: "Where can I find the Bishop?", key: 'where_can_i_find_the_bishop', next: "bishop_info" },
                ]
            },
            templeGuardWhy: {
        text: "It is the order of the cathedral council. However, I have heard that it was mainly your bishop, meaning the bishop of Obazoba church, who declared the emergency. That must be enough for you to know.",
                options: [
                    { text: "I need to speak with someone inside", key: 'i_need_to_speak_with_someone_inside', next: "speakWithSomeoneInside" },
                    { text: "Where can I find the Bishop?", key: 'where_can_i_find_the_bishop', next: "bishop_info" },
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardWho: {
        text: "I am a Sentinel of the Veil, sworn to protect the sacred Egg Cathedral from contamination. My eyes have witnessed a thousand years of spore patterns.",
                options: [
                    { text: "How long have you been here?", key: 'how_long_have_you_been_here', next: "templeGuardTime" },
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardFruiting: {
        text: "When the cathedral's fully hatched from its egg, something miraculous will happen. The walls will burst, spreading our consciousness across the stars... Or somqething like that. You know, nobody really knows, but I imagine it will be something truly magnificent.",
                options: [
                    { text: "That sounds apocalyptic", key: 'that_sounds_apocalyptic', next: "templeGuardApocalypse" },
                    { text: "That sounds fascinating", key: 'that_sounds_fascinating', next: "templeGuardFascinating" },
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardTime: {
                text: "I have stood at this post since the Third Sporulation. My flesh has long since been replaced by plants. My consciousness is connected to the city. I think my left foot is made from rodent.",
                options: [
                    { text: "That's... familiar", key: 'thats_familiar', next: "templeGuardDisturbing" },
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardFascinating: {
                text: "Fascinating, isn't it? That's why all major faiths have their people here. No one wants to miss the chance that it will be their god to whom the cathedral will be devoted.",
                options: [
                    { text: "I see", key: 'i_see', next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardApocalypse: {
                text: "Apocalypse? No. Transformation. The cathedral will become something truly new, some say that it will become a birthplace of a new god. Nobody really know, that's why all churches have their representatives present. It's all very interesting, see.",
                options: [
                    { text: "I see", key: 'i_see', next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardDisturbing: {
                text: "Glad you see it that way. I have gained immortality and purpose. My consciousness spans the mycelial network. I am never alone.",
                options: [
                    { text: "Fascinating", key: 'fascinating', next: "templeGuardAskSomethingElse" }
                ]
            }
        };
    }

    preload() {
        super.preload();
        this.load.image('cathedralEntranceBg', 'assets/images/backgrounds/CathedralEntrance.png');
        this.load.image('exitArea', 'assets/images/ui/door.png'); // Reusing door image for exit area
        this.load.image('guard', 'assets/images/characters/guard.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set cathedral entrance background
        const bg = this.add.image(400, 300, 'cathedralEntranceBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Position the priest at the bottom center when entering this scene
        this.priest.x = 200;
        this.priest.y = 470; // Position on the ground
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }
        
        // Create transition zone for exit to EggCatedralScene
        this.transitionManager.createTransitionZone(
            400, // x position
            550, // y position
            200, // width
            40,  // height
            'down', // direction
            'EggCatedralScene', // target scene
            400, // walk to x
            550, // walk to y
            'Cathedral Exterior' // destination name
        );
        
        // Remove the NPC if it exists
        if (this.stranger) {
            this.stranger.destroy();
        }
        
        // Add temple guard at the cathedral door
        this.createTempleGuard();
        
        // Make sure sounds are loaded
        if (!this.clickSound) {
            this.clickSound = this.sound.add('click');
        }
        if (!this.dialogMurmur) {
            this.dialogMurmur = this.sound.add('dialogMurmur');
        }
    }
    
    // Override the dialogContent getter from GameScene
    get dialogContent() {
        // Combine parent dialog content with our temple guard dialog
        const parentContent = super.dialogContent || {};
        return {
            ...parentContent,
            ...this._templeGuardDialogContent
        };
    }
    
    createTempleGuard() {
        // Create a container for the temple guard
        this.templeGuard = this.add.container(380, 450);
        this.templeGuard.setDepth(5);
        
        // Create the guard using the sprite image
        const guardSprite = this.add.sprite(0, 0, 'guard');
        guardSprite.setScale(0.2); // Match the scale of the apprentice figure
        
        // Apply a green tint to match the fungal theme
        guardSprite.setTint(0x7fff8e);
        
        // Create a container for the head for independent movement
        const headContainer = this.add.container(0, -50);
        
        // Add glowing eyes effect
        const leftEye = this.add.graphics();
        leftEye.fillStyle(0x7fff8e, 1);
        leftEye.fillCircle(-10, 0, 3);
        
        const rightEye = this.add.graphics();
        rightEye.fillStyle(0x7fff8e, 1);
        rightEye.fillCircle(10, 0, 3);
        
        // Add pulsating effect to eyes
        this.tweens.add({
            targets: [leftEye, rightEye],
            alpha: { from: 1, to: 0.5 },
            duration: 1200,
            yoyo: true,
            repeat: -1
        });
        
        // Add eyes to head container
        headContainer.add([leftEye, rightEye]);
        
        // Add staff with glowing orb
        const guardStaff = this.add.graphics();
        guardStaff.lineStyle(4, 0x7fff8e, 1);
        guardStaff.beginPath();
        guardStaff.moveTo(40, -80);
        guardStaff.lineTo(40, 60);
        guardStaff.closePath();
        guardStaff.strokePath();
        
        // Add staff orb
        const staffOrb = this.add.graphics();
        staffOrb.fillStyle(0x7fff8e, 0.8);
        staffOrb.fillCircle(40, -70, 8);
        
        // Add pulsating effect to the orb
        this.tweens.add({
            targets: staffOrb,
            alpha: { from: 0.8, to: 0.4 },
            duration: 1500,
            yoyo: true,
            repeat: -1
        });
        
        // Add all elements to the container
        this.templeGuard.add([
            guardSprite,
            headContainer,
            guardStaff,
            staffOrb
        ]);
        
        // Add a subtle pulsating glow effect around the guard
        this.guardGlow = this.add.graphics();
        this.guardGlow.fillStyle(0x7fff8e, 0.2);
        this.guardGlow.fillCircle(380, 450, 50);
        this.guardGlow.setDepth(4);
        
        // Animate the glow
        this.tweens.add({
            targets: this.guardGlow,
            alpha: { from: 0.2, to: 0.1 },
            duration: 1500,
            yoyo: true,
            repeat: -1
        });
        
        // Add subtle swaying movement to the guard
        this.tweens.add({
            targets: this.templeGuard,
            angle: { from: -1, to: 1 },
            duration: 2500,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });
        
        // Add subtle breathing movement
        this.tweens.add({
            targets: this.templeGuard,
            scaleY: { from: 1, to: 1.02 },
            y: { from: 450, to: 449 },
            duration: 1800,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });
        
        // Add occasional head movement
        this.time.addEvent({
            delay: 5000,
            callback: () => {
                // Random head movement
                const lookDirection = Phaser.Math.Between(0, 2);
                let targetX = 0;
                
                if (lookDirection === 0) targetX = -3; // Look left
                else if (lookDirection === 1) targetX = 3; // Look right
                
                this.tweens.add({
                    targets: headContainer,
                    x: targetX,
                    duration: 1000,
                    ease: 'Power1',
                    yoyo: true,
                    hold: 1500
                });
            },
            callbackScope: this,
            loop: true
        });
        
        // Add occasional staff movement
        this.time.addEvent({
            delay: 8000,
            callback: () => {
                // Subtle staff adjustment
                this.tweens.add({
                    targets: [guardStaff, staffOrb],
                    x: { from: 0, to: 2 },
                    duration: 800,
                    ease: 'Bounce.easeOut',
                    yoyo: true
                });
            },
            callbackScope: this,
            loop: true
        });
        
        // Make guard interactive - create a hit area
        const hitArea = new Phaser.Geom.Rectangle(-40, -100, 80, 160);
        this.templeGuard.setInteractive(hitArea, Phaser.Geom.Rectangle.Contains);
        
        // Add hover effect
        this.templeGuard.on('pointerover', () => {
            this.templeGuard.setScale(1.05);
            document.body.style.cursor = 'pointer';
            
            // Alert animation when hovered
            this.tweens.add({
                targets: headContainer,
                y: -3,
                duration: 300,
                ease: 'Power1',
                yoyo: true
            });
        });
        
        this.templeGuard.on('pointerout', () => {
            this.templeGuard.setScale(1);
            document.body.style.cursor = 'default';
            
            // Reset head position
            this.tweens.add({
                targets: headContainer,
                y: 0,
                duration: 300,
                ease: 'Power1'
            });
        });
        
        // Show dialog on click
        this.templeGuard.on('pointerdown', () => {
            if (this.clickSound) {
                this.clickSound.play();
            }
            
            // Alert animation when clicked
            this.tweens.add({
                targets: this.templeGuard,
                y: { from: 450, to: 445 },
                duration: 100,
                ease: 'Power1',
                yoyo: true
            });
            
            this.showDialog('templeGuardGreeting');
        });
    }

    update() {
        // Call parent update for all standard mechanics
        super.update();
        
        // No need for manual transition checks as SceneTransitionManager handles this
    }
    
    shutdown() {
        // Call parent shutdown to stop audio
        super.shutdown();
        
        // Additional cleanup specific to CathedralEntrance
        if (this.templeGuard) {
            this.templeGuard.destroy();
            this.templeGuard = null;
        }
    }
    
    showDialog(dialogKey) {
        // Handle Growth/Decay changes
        if (dialogKey === 'templeGuardFascinating') {
            this.modifyGrowthDecay(1, 0);
            if (this._templeGuardDialogContent.templeGuardFruiting) {
                this._templeGuardDialogContent.templeGuardFruiting.options = 
                    this._templeGuardDialogContent.templeGuardFruiting.options.filter(
                        option => option.next !== 'templeGuardFascinating' && 
                                 option.next !== 'templeGuardApocalypse'
                    );
            }
        } else if (dialogKey === 'templeGuardApocalypse') {
            this.modifyGrowthDecay(0, 1);
            if (this._templeGuardDialogContent.templeGuardFruiting) {
                this._templeGuardDialogContent.templeGuardFruiting.options = 
                    this._templeGuardDialogContent.templeGuardFruiting.options.filter(
                        option => option.next !== 'templeGuardFascinating' && 
                                 option.next !== 'templeGuardApocalypse'
                    );
            }
        }

        // Handle quest updates
        if (dialogKey === 'bishop_info' && !this.questSystem.getQuest('find_bishop')) {
            this.questSystem.addQuest(
                'find_bishop',
                'Find the Bishop',
                'The temple guard mentioned that the Bishop might help me gain access to the cathedral. I should seek her out.'
            );
            this.showNotification('Quest updated: Find the Bishop');
        } else if (dialogKey === 'templeGuardVoxmarket' && this.questSystem.getQuest('find_bishop')) {
            this.questSystem.updateQuest(
                'find_bishop',
                'The Voxmarket is an audio bazaar where recorded voices and sounds are traded. The Bishop might be found there.'
            );
            this.showNotification('Quest updated: Find the Bishop');
        } else if (dialogKey === 'templeGuardShed521' && this.questSystem.getQuest('find_bishop')) {
            this.questSystem.updateQuest(
                'find_bishop',
                'Shed 521, also known as the Bureau of Shapes, is a bureaucratic maze where people register their forms. The Bishop is known to visit this place.'
            );
            this.showNotification('Quest updated: Find the Bishop');
        }

        // Show the dialog content
        super.showDialog(dialogKey);
    }
}
