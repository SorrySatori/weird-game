import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class TownhallScene extends GameScene {
    constructor() {
        super({ key: 'TownhallScene' });
        this.isTransitioning = false;
    }
        
        // Store Phor Calesta dialog content
    

        get dialogContent() {
            const questSystem = this.registry.get('questSystem');
            const hasRustFeastQuest = questSystem.getQuest('rust_feast');
            return {
            speaker: 'Phor Calesta',
            phorGreeting: {
                text: "Ah, another pilgrim to the archives of the forgotten divine. I am Phor Calesta, archaeologist of lost theologies. The locals call me 'Godgrave Excavator,' though I prefer the term Divinographer.",
                options: [
                    { text: "What is Divinography?", next: "phorDivinography" },
                    { text: "Where are you from?", next: "phorMurkvale" },
                    { text: "What are you doing here?", next: "phorPurpose" },
                   ...(hasRustFeastQuest && [{ text: "I'm looking for a living rust cluster", next: "phorRustCluster" }]),
                ],
                onTrigger: () => {
                    if (this.journalSystem && !this.journalSystem.hasEntry('phor_calesta')) {
                        this.addJournalEntry(
                            'phor_calesta',
                            'Phor Calesta - Divinographer',
                            'I have meet another strange person. An archaeologist specializing in the study of dead gods and their fossilized remains. He is a Craybara from city of Murkvale. Phor seeks excavation permits to explore the Godgraveyard.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Phor Calesta', related: 'Identity' }
                        );
                    }            
                },
            },
            phorDivinography: {
                text: "Divinography is the study of dead gods as geological phenomena. When a deity dies, their essence doesn't simply vanish—it fossilizes. Ossified prayers become strata. Halos crystallize into mineral deposits. I excavate these divine remains and catalog their properties.",
                options: [
                    { text: "That sounds like grave robbery", next: "phorGraveRobbery" },
                    { text: "Fascinating. What have you found?", next: "phorFindings" },
                    { text: "Ask something else", next: "phorAskSomethingElse" }
                ]
            },
            phorGraveRobbery: {
                text: "(Chuckles wetly) Perhaps. But tell me—is it robbery if the deceased has no heirs? No worshippers? When a god dies and their faithful scatter, their remains become... unclaimed property. I simply ensure they're studied rather than forgotten.",
                options: [
                    { text: "I suppose that's one way to look at it", next: "phorAskSomethingElse" },
                    { text: "What have you found?", next: "phorFindings" }
                ]
            },
            phorFindings: {
                text: "Remarkable things. Godmetal that hums with residual faith. Prayer beads that still whisper devotions in dead languages. Once, I found a halo fragment that projected the last thoughts of its deity—a loop of cosmic despair lasting exactly 47 seconds.",
                options: [
                    { text: "That's disturbing", next: "phorDisturbing" },
                    { text: "Where do you find these things?", next: "phorLocations" },
                    { text: "Ask something else", next: "phorAskSomethingElse" }
                ]
            },
            phorDisturbing: {
                text: "Disturbing? Perhaps. But also illuminating. We learn more from divine death than divine life. Gods lie to their followers. Their corpses tell only truth.",
                options: [
                    { text: "Ask something else", next: "phorAskSomethingElse" }
                ]
            },
            phorLocations: {
                text: "Anywhere pressure and memory intersect. Submerged temples. Collapsed cathedrals. The deeper strata of this very city. Murkvale, my home, is particularly rich—the water pressure there fossilizes divine essence beautifully.",
                options: [
                    { text: "Tell me about Murkvale", next: "phorMurkvale" },
                    { text: "Ask something else", next: "phorAskSomethingElse" }
                ]
            },
            phorMurkvale: {
                text: "I'm from Murkvale. It is a submerged city where my people, the Craybara, evolved. We are amphibious—adapted to crushing depths and social pressures alike. The city's ruins grow like coral, and memory itself fossilizes in the sediment. It's a perfect laboratory for studying divine archaeology.",
                options: [
                    { text: "What brought you here?", next: "phorPurpose" },
                    { text: "Ask something else", next: "phorAskSomethingElse" }
                ]
            },
            phorPurpose: {
                text: "This city sits atop layers of dead faiths. The Egg Cathedral above is merely the latest iteration. Beneath the city lie the bones of many gods who came to die here. I'm here to excavate the lower strata and document what gods died to make room for the current ones. But to do that, I must first survive the bureaucracy. Sadly, the townhall won't let me to excavate at the Godgraveyard level without proper permits. But the damned townhall is closed or what.",
                options: [
                    { text: "That's quite ambitious", next: "phorAmbitious" },
                    { text: "Can I help you to get the permission?", next: "phorPurposeHelp" },
                    { text: "Ask something else", next: "phorAskSomethingElse" }
                ]
            },
            phorPurposeHelp: {
                text: "Hmm. Perhaps you could. If you manage to navigate the townhall bureaucracy and secure excavation permits for the Godgraveyard, I would be forever in your debt.",
                options: [
                    { text: "I'll see what I can do", next: "phorAskSomethingElse" }
                ],
                onTrigger: () => {
                        this.questSystem.addQuest('excavation_permit', 'Divinography', 'I should help Phor Calesta obtain excavation permits for the Godgraveyard of the townhall. First, I need to get inside the townhall somehow.', 'talked_to_phor');
                    }
            },
            phorAmbitious: {
                text: "Ambition is all that survives pressure. In Murkvale, we learned that early. The weak are crushed. The ambitious adapt. I intend to publish the definitive text on divine stratigraphy—assuming I survive the excavation.",
                options: [
                    { text: "Ask something else", next: "phorAskSomethingElse" }
                ]
            },
            phorAskSomethingElse: {
                text: "Yes? What else troubles your curiosity?",
                options: [
                    { text: "What is Divinography?", next: "phorDivinography" },
                    { text: "Tell me about Murkvale", next: "phorMurkvale" },
                    { text: "What are you doing here?", next: "phorPurpose" },
                    { text: "I'm looking for a living rust cluster", next: "phorRustCluster", condition: () => this.questSystem.hasQuest('rust_feast') },
                    { text: "Farewell", next: null }
                ]
            },
            phorRustCluster: {
                text: "Ah! A living rust cluster. Fascinating organisms—part mineral, part fungal, part memory. They grow in places where metal and decay achieve equilibrium. I've documented several colonies in my excavations.",
                options: [
                    { text: "Where can I find one?", next: "phorRustClusterLocation" },
                    { text: "What are they exactly?", next: "phorRustClusterNature" }
                ]
            },
            phorRustClusterLocation: {
                text: "The most accessible colony I've found is in the lower levels of Shed 521—specifically in the maintenance halls. The bureaucrats avoid that area due to 'structural concerns,' which makes it perfect for rust cluster growth. Look for corroded pipes with orange-red crystalline growths.",
                options: [
                    { text: "How do I extract one safely?", next: "phorRustClusterExtraction" },
                    { text: "Thank you for the information", next: "phorRustClusterThanks" }
                ],
                onTrigger: () => {
                        this.questSystem.updateQuest('rust_feast', 'Phor Calesta told me that living rust clusters can be found in the maintenance halls of Shed 521. I should look for corroded pipes with orange-red crystalline growths.', 'learned_rust_cluster_location');
                    }
            },
            phorRustClusterNature: {
                text: "They're symbiotic organisms—fungal mycelium that feeds on oxidizing metal while preserving the structural memory of what the metal once was. In a sense, they're living fossils of decay. Quite poetic, really.",
                options: [
                    { text: "Where can I find one?", next: "phorRustClusterLocation" },
                    { text: "Ask something else", next: "phorAskSomethingElse" }
                ]
            },
            phorRustClusterExtraction: {
                text: "Carefully. They're delicate. Use a blade to separate the cluster from its substrate, but leave some of the host metal attached—they need it to survive. And whatever you do, don't expose them to pure water. It disrupts their oxidation cycle.",
                options: [
                    { text: "Thank you for the advice", next: "phorRustClusterThanks" }
                ]
            },
            phorRustClusterThanks: {
                text: "Of course. If you're successful, do tell me what you're using it for. I'm always interested in how others utilize these divine remnants.",
                options: [
                    { text: "Ask something else", next: "phorAskSomethingElse" },
                    { text: "Farewell", next: null }
                ]
            }
        }
    }


    preload() {
        super.preload();
        this.load.image('townhallBg', 'assets/images/backgrounds/townhall.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        this.load.image('phor', 'assets/images/characters/phor.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set townhall background
        const bg = this.add.image(400, 300, 'townhallBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            80, // width
            200, // height
            'left', // direction
            'BurningBearStreetScene', // target scene
            750, // walk to x
            470 // walk to y
        );

        // Position the priest at the bottom center when entering
        this.priest.x = 400;
        this.priest.y = 470;
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }
        
        // Create Phor Calesta
        this.createPhorCalesta();
        
        // Make sure sounds are loaded
        if (!this.clickSound) {
            this.clickSound = this.sound.add('click');
        }

        this.cameras.main.fadeIn(800, 0, 0, 0);
    }
    
    createPhorCalesta() {
        // Create a container for Phor Calesta
        this.phor = this.add.container(550, 420);
        this.phor.setDepth(5);
        
        // Create the character sprite
        const phorSprite = this.add.sprite(0, 0, 'phor');
        phorSprite.setScale(0.2); // Match the scale of other characters
        
        // Apply a subtle tint to give an amphibious/aquatic feel
        phorSprite.setTint(0x88ccdd);
        
        // Create a container for the head for independent movement
        const headContainer = this.add.container(0, -45);

        // Add all elements to the container
        this.phor.add([
            phorSprite,
            headContainer
        ]);
        
        // Add a subtle pulsating glow effect
        this.phorGlow = this.add.graphics();
        this.phorGlow.fillStyle(0x66ffff, 0.15);
        this.phorGlow.fillCircle(550, 420, 45);
        this.phorGlow.setDepth(4);
        
        // Animate the glow
        this.tweens.add({
            targets: this.phorGlow,
            alpha: { from: 0.15, to: 0.05 },
            duration: 1800,
            yoyo: true,
            repeat: -1
        });
        
        // Add subtle swaying movement (like underwater movement)
        this.tweens.add({
            targets: this.phor,
            angle: { from: -0.5, to: 0.5 },
            duration: 3000,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });
        
        // Add occasional head movement (looking around)
        this.time.addEvent({
            delay: 6000,
            callback: () => {
                // Random head movement
                const lookDirection = Phaser.Math.Between(0, 2);
                let targetX = 0;
                
                if (lookDirection === 0) targetX = -4; // Look left
                else if (lookDirection === 1) targetX = 4; // Look right
                
                this.tweens.add({
                    targets: headContainer,
                    x: targetX,
                    duration: 1200,
                    ease: 'Power1',
                    yoyo: true,
                    hold: 2000
                });
            },
            callbackScope: this,
            loop: true
        });
        
        const hitArea = new Phaser.Geom.Rectangle(-40, -90, 80, 140);
        this.phor.setInteractive(hitArea, Phaser.Geom.Rectangle.Contains);
        
        // Add hover effect
        this.phor.on('pointerover', () => {
            this.phor.setScale(1.05);
            document.body.style.cursor = 'pointer';
            
            // Alert animation when hovered
            this.tweens.add({
                targets: headContainer,
                y: -48,
                duration: 300,
                ease: 'Power1',
                yoyo: true
            });
        });
        
        this.phor.on('pointerout', () => {
            this.phor.setScale(1);
            document.body.style.cursor = 'default';
            
            // Reset head position
            this.tweens.add({
                targets: headContainer,
                y: -45,
                duration: 300,
                ease: 'Power1'
            });
        });
        
        // Show dialog on click
        this.phor.on('pointerdown', () => {
            if (this.clickSound) {
                this.clickSound.play();
            }
            
            // Alert animation when clicked
            this.tweens.add({
                targets: this.phor,
                y: { from: this.phor.y, to: this.phor.y - 5 },
                duration: 100,
                ease: 'Power1',
                yoyo: true
            });
            
            this.showDialog('phorGreeting');
        });
    }

    update() {
        super.update();
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.TownhallScene = TownhallScene;
}

export { TownhallScene };
