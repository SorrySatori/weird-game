import GameScene from './GameScene.js';

export default class ShedApplicationsScene extends GameScene {
    constructor() {
        super({ key: 'ShedApplicationsScene' });
        this.isTransitioning = false;
        this.visitedDialogs = new Set();
        this._dialogTextCache = {}; // Cache for dynamic dialog text
    }

    get dialogContent() {
        // Get base content
        const inventory = this.registry.get('inventory');
        const content = {
            ...super.dialogContent,
            start: {
                text: "(The clerk shuffles through a stack of papers, barely looking up)\nWelcome to Shed13 Applications. Forms in triplicate, please. No exceptions.",
                options: [
                    { text: "Tell me about Shed13", next: "about_shed" },
                    { text: "What's your role here?", next: "clerk_role" },
                    { text: "Goodbye", next: "end" }
                ]
            },
            about_shed: {
                text: "Shed13? (adjusts glasses) One of our most... productive facilities. Biotech research, augmentation services, and... other classified operations. All properly documented, of course. Three hundred and forty-two forms for each procedure.",
                options: [
                    { text: "That's a lot of paperwork", next: "paperwork" },
                    { text: "Back to other topics", next: "start" }
                ]
            },
            clerk_role: {
                text: "I maintain order in chaos. Every augmentation, every experiment, every... incident must be properly documented. The bureaucracy must flow, as they say. (straightens a perfectly straight stack of papers)",
                options: [
                    { text: "Back to other topics", next: "start" }
                ]
            },
            paperwork: {
                text: "Indeed. (eyes gleaming) Did you know we have seventeen different forms just for requesting a new form? Proper documentation is what separates us from the ferals in the wastes.",
                options: [
                    { text: "Back to other topics", next: "start" }
                ]
            },
            living_core_inquiry: {
                text: "(The clerk's eyes narrow) The living core? (lowers voice) Listen carefully. That technology is classified under Protocol 7B, subsection 13. (glances around) Why do you ask?",
                options: [
                    { text: "Gnur asked me to retrieve it", next: "expose_gnur" },
                    { text: "I am just interested in such technology.", next: "lie_living_core" },
                    { text: "Back to other topics", next: "start" }
                ]
            },
            lie_living_core: {
                text: "(Straightens papers disapprovingly) Very well. But remember - proper protocols exist for a reason. Don't you even think about messing with the living core. People usually think it's just a relict, but it is crucial for the Shed's energy maintenance.",
                options: [
                    { text: "Back to other topics", next: "start" }
                ],
                onShow: () => {
                    this.modifyGrowthDecay(0, 2);
                    this.showNotification('Decay +2');
                }
            },
            expose_gnur: {
                text: "I knew it! Thanks for telling me. (smiles) The Rust Choir scum has no right for such technology. (puts away papers) Please promise to not mess with the living core.",
                options: [
                    { text: "I promise to leave it alone", next: "promise_made" },
                    { text: "I'll think about it", next: "no_promise" }
                ],
            },
            promise_made: {
                text: "(Visibly relieved) Good... good. The Pith Reclaimers will remember this. If you're interested in learning more, find Edgar Eskola at the Screaming Cork. He has... perspectives on proper preservation protocols.",
                options: [
                    { text: "Back to other topics", next: "start" },
                    { text: "Who are the Pith Reclaimers?", next: "pith_reclaimers"}
                ],
                onShow: () => {
                    const factionSystem = this.registry.get('factionSystem');
                
                    if (factionSystem) {
                        factionSystem.modifyReputation('PithReclaimers', 20);
                        this.showNotification('Pith Reclaimers Reputation +20');
                    }
                    this.modifyGrowthDecay(2, 0);
                    this.showNotification('Growth +2');
                }
            },
            pith_reclaimers: {
                text: "The Pith Reclaimers are... guardians of neutrality. We preserve peace and order in the city. Some of us collect... unique items, but we don't sell them.",
                options: [
                    { text: "Back to other topics", next: "start" }
                ],
                onShow: () => {
                    const factionSystem = this.registry.get('factionSystem');
                
                    if (factionSystem) {
                        factionSystem.modifyReputation('PithReclaimers', 20);
                        this.showNotification('Pith Reclaimers Reputation +20');
                    }
                }
            },
            no_promise: {
                text: "(Straightens papers disapprovingly) Very well. But remember - proper protocols exist for a reason.",
                options: [
                    { text: "Back to other topics", next: "start" }
                ]
            },
            ortolan_inquiry: {
                text: "Ortolan Arms? (shuffles through papers) Ah yes, their permit applications are... concerning. Multiple violations of safety protocols. I've documented everything in triplicate, but our enforcement division is... understaffed.",
                options: [
                    { text: "I could help investigate", next: "ortolan_help" },
                    { text: "Back to other topics", next: "start" }
                ]
            },
            ortolan_help: {
                text: "Excellent! (pulls out a form) Just sign here... and here... and initial these 47 spots... Perfect! Now we can properly document any violations you find.",
                options: [
                    { text: "Back to other topics", next: "start" }
                ],
                onShow: () => {
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && questSystem.getQuest('ortolan_arms')) {
                        questSystem.updateQuest('ortolan_arms', 'The clerk has provided official documentation to investigate Ortolan Arms. Any evidence found will be properly filed.');
                        this.showNotification('Quest updated: Ortolan Arms Investigation');
                    }
                }
            },
            end: {
                text: "Please file your exit form in triplicate before leaving.",
                options: [],
                onShow: () => {
                    this.hideDialog();
                }
            }
        };

        // Add quest-specific dialog options
        const questSystem = this.registry.get('questSystem');
        console.log('Quest System:', questSystem);
        console.log('rust_reclamation:', questSystem.getQuest('rust_reclamation'));
        console.log('ortolan_arms:', questSystem.getQuest('ortolan_arms'));
        if (questSystem) {
            if (questSystem.getQuest('rust_reclamation') && !this.visitedDialogs.has('living_core_inquiry')) {
                content.start.options.splice(1, 0, {
                    text: "What do you know about the living core?",
                    next: "living_core_inquiry"
                });
            }
            if (questSystem.getQuest('ortolan_arms') && !this.visitedDialogs.has('ortolan_inquiry')) {
                content.start.options.splice(1, 0, {
                    text: "About Ortolan Arms...",
                    next: "ortolan_inquiry"
                });
            }
        }
        return content;

    }

    showDialog(dialogKey) {

        // Track visited dialogs
        this.visitedDialogs.add(dialogKey);

        // Show the dialog content
        super.showDialog(dialogKey);
    }

    preload() {
        super.preload();
        this.load.image('applications-bg', 'assets/images/ShedApplications.png');
        this.load.image('door', 'assets/images/door.png');
        this.load.image('clerk', './assets/images/clerk.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set initial priest position
        if (this.priest) {
            this.priest.x = 650;  // Match entrance position from Shed13FloorsScene
            this.priest.y = 520;  // Ground level
            this.priest.setOrigin(0.5, 1);
            this.priest.play('idle');
        }

        // Set background
        const bg = this.add.image(400, 300, 'applications-bg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        // Add Clerk NPC with proper size
        this.clerk = this.add.sprite(100, 440, 'clerk');
        this.clerk.setFlipX(true);
        this.clerk.setDisplaySize(80, 120); // Set a fixed size
        this.clerk.setDepth(1); // Ensure it's above background
        this.clerk.setInteractive({ useHandCursor: true });
        
        // Add exit back to Shed13FloorsScene
        this.exitToShed = this.add.image(650, 520, 'door')
            .setDisplaySize(100, 100)
            .setAlpha(0.01)
            .setInteractive();

        this.exitArea = this.add.image(50, 470, 'exitArea')
            .setDisplaySize(50, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);

        // Set up pointer events
        this.exitToShed.on('pointerover', () => {
            if (!this.isTransitioning) {
                this.setCursor('pointer');
            }
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
                    // Set position in Shed13FloorsScene near the applications entrance
                    return { x: 650, y: 450 };
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
                y: 465,
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
                
                // Add subtle bobbing animation for walking
                this.tweens.add({
                    targets: this.clerk,
                    y: this.clerk.y - 3, // Small up and down movement
                    duration: 500,
                    ease: 'Sine.easeInOut',
                    yoyo: true,
                    repeat: -1
                });
                
                this.time.addEvent({
                    delay: 5000,
                    callback: () => {
                        if (Math.random() > 0.5) {
                            this.tweens.add({
                                targets: this.clerk,
                                angle: Phaser.Math.Between(-5, 5),
                                duration: 1000,
                                ease: 'Sine.easeInOut',
                                yoyo: true
                            });
                        }
                    },
                    loop: true
                });
                this.clerk.setInteractive({ useHandCursor: true });
                
                // Add interaction with Clerk
                this.clerk.on('pointerdown', () => {
                    this.dialogState = 'start';  // Set initial dialog state
                    this.showDialog(this.dialogState);
                });
    }
    

    update() {
        super.update();
    }
}
