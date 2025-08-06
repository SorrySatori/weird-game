import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class ShedApplicationsScene extends GameScene {
    constructor() {
        super({ key: 'ShedApplicationsScene' });
        this.isTransitioning = false;
        this.visitedDialogs = new Set();
        this._dialogTextCache = {}; // Cache for dynamic dialog text
    }

    get dialogContent() {
        // Get base content
        const content = {
            ...super.dialogContent,
            start: {
                text: "(The clerk shuffles through a stack of papers, barely looking up)\nWelcome to Shed521 Applications. Forms in triplicate, please. No exceptions.",
                options: [
                    { text: "Tell me about Shed521", next: "about_shed" },
                    { text: "What's your role here?", next: "clerk_role" },
                    { text: "Goodbye", next: "end" }
                ]
            },
            about_shed: {
                text: "Shed521? (adjusts glasses) One of our most... productive facilities. It used to be just an ordinary warehouse, a storage, you kno. But now... it's much more. It's a place where... things happen. (smiles) Bureaucracy is really alive here, it flows like a river. It gives purpose to things, to every action, every decision. (puts away papers) We can be so productive and happy here.",
                options: [
                    { text: "That sounds like a lot of paperwork", next: "paperwork" },
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
                text: "(Visibly relieved) Good... good. The Pith Reclaimers will remember this. What Gnur promised you for the living core?",
                options: [
                    { text: "He promised me a to tell where to find the Bishop", next: "bishop_location" },
                    { text: "Sorry, but that's private information", next: "private"},
                    { text: "Who are the Pith Reclaimers?", next: "pith_reclaimers"},
                ],
                onShow: () => {
                    const factionSystem = this.registry.get('factionSystem');
                
                    if (factionSystem) {
                        factionSystem.modifyReputation('PithReclaimers', 20);
                        this.showNotification('Pith Reclaimers Reputation +20');
                    }
                    this.modifyGrowthDecay(2, 0);
                    this.showNotification('Growth +2');

                    const questSystem = this.registry.get('questSystem');
                    if (questSystem) {
                        questSystem.updateQuest(
                            'rust_reclamation', 
                            'I promised the clerk in Shed 521 I will not mess with the living core. It seems it is more important for the building than Gnur told me.',
                            'promise_made' // Adding a key to identify this specific update
                        );
                        this.showNotification('Quest updated: Rust Reclamation');
                    }
                }
            },
            bishop_location: {
                text: "The Bishop? Hmm... I can't tell you where she is. But look for Edgar Eskola at the Screaming Cork tavern. I think he might know something.",
                options: [
                    { text: "Back to other topics", next: "start" },
                    { text: "Who are the Pith Reclaimers?", next: "pith_reclaimers"},
                    { text: "Who is Edgar Eskola?", next: "edgar"}
                ],
                onShow: () => {
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && questSystem.getQuest('find_bishop')) {
                        questSystem.updateQuest('find_bishop', 'The clerk told me to find Edgar Eskola at the Screaming Cork tavern. He might know something.', 'edgar_eskola_clue');
                        this.showNotification('Quest updated: Find the Bishop of Threshold');
                    }
                }
            },
            private: {
                text: "I see, no problem. Is there anything else I can help you with?",
                options: [
                    { text: "Back to other topics", next: "start" },
                    { text: "Who are the Pith Reclaimers?", next: "pith_reclaimers"},
                ],
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
            edgar: {
                text: "Edgar Eskola? (raises eyebrow). He is one of the mišutkenn. Heard about them? They are semi-ursine, sentient humanoids with patchy fur, deep-set amber eyes, and dream-reactive physiology. Usually gentle souls, but they can be... unpredictable.",
                options: [
                    { text: "Back to other topics", next: "start" }
                ]
            },
            no_promise: {
                text: "(Straightens papers disapprovingly) Very well. But remember - proper protocols exist for a reason.",
                options: [
                    { text: "Back to other topics", next: "start" }
                ]
            },
            ortolan_inquiry: {
                text: "Extra Arms? (shuffles through papers) Additional arms, you say. Are they intentional?",
                options: [
                    { text: "My friend needs them. He’s an artisan.", next: "ortolan_artisan" },
                    { text: "My friend didn’t choose this. The arms were... a gift.", next: "ortolan_gift" },
                    { text: "They’re not his arms. He’s borrowing them.", next: "ortolan_borrow" },
                    { text: "Back to other topics", next: "start" }
                ]
            },
            ortolan_borrow: {
                text: "Then he is harboring a flesh-fugitive. I’ll need an Absentee Consent Signature. From the original owner.",
                options: [
                    { text: "Back to other topics", next: "start" },
                    { text: "Fine. I’ll lie. Or forge the documents?", next: "ortolan_lie" },
                    { text: "Uhh... sorry I mean he needs them. He’s an artisan.", next: "ortolan_artisan" },
                    { text: "Well, I was just joking. Of course they are his. But he didn’t choose this. The arms were... a gift.", next: "ortolan_gift" }
                ]
            },
            ortolan_gift: {
                text: "Unsolicited limbs are still taxable. But perhaps we can file under Inherited Deformity.",
                options: [
                    { text: "Can you process it today?", next: "ortolan_today" },
                    { text: "Fine. I’ll lie. Or forge the documents?", next: "ortolan_lie" }
                ],
            },
            ortolan_today: {
                text: "Not without permission from the Registration office. Go there and ask for the Inherited Deformity Form.",
                options: [
                    { text: "Back to other topics", next: "start" }
                ],
                onShow: () => {
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem) {
                        questSystem.updateQuest('ortolan_arms', 'The clerk told me to go to the Registration office to retrieve Inherited Deformity Form.', 'deformity_form_clue');
                        this.showNotification('Quest updated: Ortolan Arms Investigation');
                    }
                }
            },
            ortolan_lie: {
                text: "I’ll pretend not to hear that.",
                options: [
                    { text: "Back to other topics", next: "start" }
                ],
                onShow: () => {
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem) {
                        questSystem.updateQuest('ortolan_arms', 'When I suggest to the clerk to forge the documents for Ortolan, he looked at me with a mix of surprise and annoyance. But can it be done? Where can I find some forger?', 'forge_documents_suggestion');
                        this.showNotification('Quest updated: Ortolan Arms Investigation');
                    }
                }
            },
            ortolan_artisan: {
                text: "Art is no defense against anatomy. But we do have the Artisan’s Exemption Form. Of course, it expired last cycle.",
                options: [
                    { text: "Can it be renewed?", next: "ortolan_renew" },
                    { text: "What if I find another copy?", next: "ortolan_copy" },
                    { text: "Forget the form. What else can I offer?", next: "ortolan_offer" },
                    { text: "Back to other topics", next: "start" }
                ],
            },
            ortolan_renew: {
                text: "Only with a performance. Go ask to the Registration office.",
                options: [
                    { text: "Back to other topics", next: "start" }
                ],
                onShow: () => {
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem) {
                        questSystem.updateQuest('ortolan_arms', 'The clerk told me to go to the Registration office to retrieve Artisan\'s Exemption Form.', 'artisan_form_clue');
                        this.showNotification('Quest updated: Ortolan Arms Investigation');
                    }
                }
            },
            ortolan_copy: {
                text: "Are you deaf? I said, are you deaf? It expired last cycle.",
                options: [
                    { text: "Back to other topics", next: "start" },
                    { text: "Can it be renewed?", next: "ortolan_renew" },
                    { text: "Forget the form. What else can I offer?", next: "ortolan_offer" },
                ]
            },
            ortolan_offer: {
                text: "A gesture. Symbolic. Nonverbal. Go to the Registration office and do your best.",
                options: [
                    { text: "Uh... okay. Can I ask for other topics?", next: "start" }
                ],
                onShow: () => {
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem) {
                        questSystem.updateQuest('ortolan_arms', 'The clerk told me to go to the Registration office and do my best with nonverbal gesture. I am not sure if I understand completely... ', 'nonverbal_gesture_clue');
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

        if (questSystem) {
            if (questSystem.getQuest('rust_reclamation') && !this.visitedDialogs.has('living_core_inquiry')) {
                content.start.options.splice(1, 0, {
                    text: "What do you know about the living core?",
                    next: "living_core_inquiry"
                });
            }
            if (questSystem.getQuest('ortolan_arms') && !this.visitedDialogs.has('ortolan_inquiry')) {
                content.start.options.splice(1, 0, {
                    text: "How can I register for extra pair of arms?",
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
        this.load.image('applications-bg', 'assets/images/backgrounds/ShedApplications.png');
        this.load.image('door', 'assets/images/ui/door.png');
        this.load.image('clerk', './assets/images/characters/clerk.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set initial priest position
        if (this.priest) {
            this.priest.x = 650;  // Match entrance position from Shed521FloorsScene
            this.priest.y = 520;  // Ground level
            this.priest.setOrigin(0.5, 1);
            this.priest.play('idle');
        }

        // Set background
        const bg = this.add.image(400, 300, 'applications-bg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        // Add Clerk NPC with proper size
        this.clerk = this.add.sprite(100, 400, 'clerk');
        this.clerk.setFlipX(true);
        this.clerk.setDisplaySize(80, 180); // Set a fixed size
        this.clerk.setDepth(1); // Ensure it's above background
        this.clerk.setInteractive({ useHandCursor: true });
        
        // Initialize the transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Add exit back to Shed521FloorsScene using transition manager
        this.transitionManager.createTransitionZone(
            650, 520,  // x, y position
            100, 100,  // width, height
            'right',   // direction
            'Shed521FloorsScene', // target scene
            650, 520   // walk to coordinates
        );
        
        // Add left exit area using transition manager
        this.transitionManager.createTransitionZone(
            50, 470,   // x, y position
            50, 200,   // width, height
            'left',    // direction
            'Shed521FloorsScene', // target scene
            50, 465    // walk to coordinates
        );
                
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
