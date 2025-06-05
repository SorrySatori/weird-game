import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class CathedralEntrance extends GameScene {
    constructor() {
        super({ key: 'CathedralEntrance' });
        this.isTransitioning = false; // Add flag to track transition state
        
        // Store temple guard dialog content in a separate property
        this._templeGuardDialogContent = {
            templeGuardGreeting: {
                text: "Halt. The yolk sleeps uneasily today. Entry to the Egg Cathedral is… temporarily restricted.",
                options: [
                    { text: "When will it open?", next: "templeGuardWhen" },
                    { text: "Why is it closed?", next: "templeGuardWhy" },
                    { text: "Who are you?", next: "templeGuardWho" },
                    { text: "I need to speak with someone inside", next: "speakWithSomeoneInside" },
                    { text: "I'm a Fungal Priest. Surely I may pass.", next: "iAmFungalPriest" }
                ]
            },
            templeGuardAskSomethingElse: {
                text: "Is there anything else I can help you with?",
                options: [
                    { text: "When will it open?", next: "templeGuardWhen" },
                    { text: "Why is it closed?", next: "templeGuardWhy" },
                    { text: "Who are you?", next: "templeGuardWho" },
                    { text: "I need to speak with someone inside", next: "speakWithSomeoneInside" },
                    { text: "I'm a Fungal Priest. Surely I may pass.", next: "iAmFungalPriest" }
                ]
            },
            iAmFungalPriest: {
                text: "(Tilts head) Even rot-born clergy must heed the pulses. The Cathedral breathes its own rhythm. You must attune.",
                options: [
                    { text: "Ask something else", next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardWhen: {
                text: "Time has little meaning to the Mycelial Consciousness. When the great bishop says so or until the Great Fruiting. It could be days, it could be centuries. We stand guard until the Great Fruiting.",
                options: [
                    { text: "The Great Fruiting?", next: "templeGuardFruiting" },
                    { text: "Where can I find the Bishop?", next: "bishopOfThreshold" },
                    { text: "Ask something else", next: "templeGuardGreeting" }
                ]
            },
            speakWithSomeoneInside: {
                text: "No summons have been issued. No minds may enter without resonance. Wait. Or seek the Bishop of Threshold.",
                options: [
                    { text: "I'm a Fungal Priest. Surely I may pass.", next: "iAmFungalPriest" },
                    { text: "Where can I find the Bishop of Threshold?", next: "bishopOfThreshold" },
                    { text: "Ask something else", next: "templeGuardAskSomethingElse" }
                ]
            },
            bishopOfThreshold: {
                text: "Probably at the Voxmarket, or around Shed 13. She dwells where the walls still echo with initiation. Look for the door that doesn’t open—until it does",
                options: [
                    { text: "Ask something else", next: "templeGuardAskSomethingElse" },
                    { text: "What is the Voxmarket?", next: "templeGuardVoxmarket"},
                    {text: "What is the Shed 13?", next: "templeGuardShed13"},
                ]
            },
            templeGuardVoxmarket: {
                text: "It's an audio bazaar near Shed 13 where recorded voices, sounds, and thoughts are sold. Stalls display silent conversation loops. You can buy the sound of someone’s first heartbreak or a scream from before fire existed.",
                options: [
                    { text: "Ask something else", next: "templeGuardAskSomethingElse" },
                    { text: "What is the Shed 13?", next: "templeGuardShed13" },
                ]
            },
            templeGuardShed13: {
                text: "It's also known as the Bureau of Shapes. A twisted bureaucracy in an old shipping yard turned into an ever-expanding cubicle labyrinth. People come here to register their current form or apply for bodily adjustments. You can find it right next to the Voxmarket",
                options: [
                    { text: "Ask something else", next: "templeGuardAskSomethingElse" },
                    { text: "Where can I find the Bishop?", next: "bishopOfThreshold" },
                ]
            },
            templeGuardWhy: {
                text: "It is the order of the bishop and the cathedral council. That must be enough for you to know.",
                options: [
                    { text: "I need to speak with someone inside", next: "speakWithSomeoneInside" },
                    { text: "Where can I find the Bishop?", next: "bishopOfThreshold" },
                    { text: "Ask something else", next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardWho: {
                text: "I am a Sentinel of the Veil, sworn to protect the sacred mycelia from contamination. My eyes have witnessed a thousand years of spore patterns.",
                options: [
                    { text: "How long have you been here?", next: "templeGuardTime" },
                    { text: "Ask something else", next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardFruiting: {
                text: "When the cathedral's inner chambers completely fill with spores, the Great Fruiting will begin. The walls will burst, spreading our consciousness across the stars.",
                options: [
                    { text: "That sounds apocalyptic", next: "templeGuardApocalypse" },
                    { text: "That sounds fascinating", next: "templeGuardFascinating" },
                    { text: "Ask something else", next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardTime: {
                text: "I have stood at this post since the Third Sporulation. My flesh has long since been replaced by hyphae, my blood by mycelial fluids. I am as much fungus as guard now.",
                options: [
                    { text: "That's... familiar", next: "templeGuardDisturbing" },
                    { text: "Ask something else", next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardFascinating: {
                text: "Fascinating, isn't it? The city will become a vast fruiting body, sending spores to colonize new worlds. It is our destiny.",
                options: [
                    { text: "I see", next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardApocalypse: {
                text: "Apocalypse? No. Transformation. The city will become a vast fruiting body, sending spores to colonize new worlds. It is our destiny.",
                options: [
                    { text: "I see", next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardDisturbing: {
                text: "Glad you see it that way. I have gained immortality and purpose. My consciousness spans the mycelial network. I am never alone.",
                options: [
                    { text: "Fascinating", next: "templeGuardAskSomethingElse" }
                ]
            }
        };
    }

    preload() {
        super.preload();
        this.load.image('cathedralEntranceBg', 'assets/images/backgrounds/CathedralEntrance.png');
        this.load.image('exitArea', 'assets/images/ui/door.png'); // Reusing door image for exit area
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
            550  // walk to y
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
        
        // Create the guard's body using graphics
        const guardBody = this.add.graphics();
        
        // Guard's robe (dark green)
        guardBody.fillStyle(0x1a3b23, 1);
        guardBody.fillRect(-20, -60, 40, 120);
        
        // Guard's hood (darker green)
        guardBody.fillStyle(0x0f2315, 1);
        guardBody.fillTriangle(-20, -60, 20, -60, 0, -90);
        
        // Guard's face (shadowed)
        guardBody.fillStyle(0x000000, 0.8);
        guardBody.fillEllipse(0, -50, 15, 20);
        
        // Guard's glowing eyes
        const leftEye = this.add.graphics();
        leftEye.fillStyle(0x7fff8e, 1);
        leftEye.fillCircle(-6, -50, 3);
        
        const rightEye = this.add.graphics();
        rightEye.fillStyle(0x7fff8e, 1);
        rightEye.fillCircle(6, -50, 3);
        
        // Add pulsating effect to eyes
        this.tweens.add({
            targets: [leftEye, rightEye],
            alpha: { from: 1, to: 0.5 },
            duration: 1200,
            yoyo: true,
            repeat: -1
        });
        
        // Create the guard's staff
        const guardStaff = this.add.graphics();
        guardStaff.lineStyle(4, 0x7fff8e, 1);
        guardStaff.beginPath();
        guardStaff.moveTo(30, -80);
        guardStaff.lineTo(30, 60);
        guardStaff.closePath();
        guardStaff.strokePath();
        
        // Add a spearhead
        const spearhead = this.add.graphics();
        spearhead.fillStyle(0x7fff8e, 1);
        spearhead.beginPath();
        spearhead.moveTo(30, -80);
        spearhead.lineTo(40, -100);
        spearhead.lineTo(20, -100);
        spearhead.closePath();
        spearhead.fillPath();
        
        // Add decorative elements to the staff
        const staffOrb = this.add.graphics();
        staffOrb.fillStyle(0x7fff8e, 0.8);
        staffOrb.fillCircle(30, -70, 8);
        
        // Add pulsating effect to the orb
        this.tweens.add({
            targets: staffOrb,
            alpha: { from: 0.8, to: 0.4 },
            duration: 1500,
            yoyo: true,
            repeat: -1
        });
        
        // Add shoulder armor (fungal caps)
        const leftShoulder = this.add.graphics();
        leftShoulder.fillStyle(0x2a623d, 1);
        leftShoulder.fillEllipse(-25, -40, 15, 10);
        leftShoulder.lineStyle(2, 0x7fff8e, 0.5);
        leftShoulder.strokeEllipse(-25, -40, 15, 10);
        
        const rightShoulder = this.add.graphics();
        rightShoulder.fillStyle(0x2a623d, 1);
        rightShoulder.fillEllipse(25, -40, 15, 10);
        rightShoulder.lineStyle(2, 0x7fff8e, 0.5);
        rightShoulder.strokeEllipse(25, -40, 15, 10);
        
        // Add belt with fungal patterns
        const guardBelt = this.add.graphics();
        guardBelt.fillStyle(0x0f2315, 1);
        guardBelt.fillRect(-20, 0, 40, 10);
        guardBelt.lineStyle(2, 0x7fff8e, 0.7);
        
        // Add belt patterns
        for (let i = -15; i <= 15; i += 10) {
            guardBelt.strokeCircle(i, 5, 3);
        }
        
        // Create a container for the head and eyes for independent movement
        const headContainer = this.add.container(0, 0);
        headContainer.add([leftEye, rightEye]);
        
        // Add all elements to the container
        this.templeGuard.add([
            guardBody, 
            headContainer,
            guardStaff, 
            spearhead, 
            staffOrb, 
            leftShoulder, 
            rightShoulder, 
            guardBelt
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
                    targets: [guardStaff, spearhead, staffOrb],
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
        if (dialogKey === 'bishopOfThreshold' && !this.questSystem.getQuest('find_bishop')) {
            this.questSystem.addQuest(
                'find_bishop',
                'Find the Bishop of Threshold',
                'The temple guard mentioned that the Bishop of Threshold might help me gain access to the cathedral. I should seek her out.'
            );
            this.showNotification('Quest updated: Find the Bishop of Threshold');
        } else if (dialogKey === 'templeGuardVoxmarket' && this.questSystem.getQuest('find_bishop')) {
            this.questSystem.updateQuest(
                'find_bishop',
                'The Voxmarket is an audio bazaar where recorded voices and sounds are traded. The Bishop might be found there.'
            );
            this.showNotification('Quest updated: Find the Bishop of Threshold');
        } else if (dialogKey === 'templeGuardShed13' && this.questSystem.getQuest('find_bishop')) {
            this.questSystem.updateQuest(
                'find_bishop',
                'Shed 13, also known as the Bureau of Shapes, is a bureaucratic maze where people register their forms. The Bishop is known to visit this place.'
            );
            this.showNotification('Quest updated: Find the Bishop of Threshold');
        }

        // Show the dialog content
        super.showDialog(dialogKey);
    }
}
