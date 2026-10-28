import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import { preloadGDProps, placeGDProps } from '../utils/GDProps.js';
import JournalSystem from '../systems/JournalSystem.js';

/** Frames of the `crossroad_corpse` sheet — the demigod's fate is shown by swapping one frame. */
const CORPSE_FRAME = { intact: 0, cut: 1, growth: 2 };

export default class CrossroadScene extends GameScene {
    constructor() {
        super({ key: 'CrossroadScene' });
        this.isTransitioning = false;
        // Use the persisted symbiont system
        this.symbiontSystem = null; // Will be set in create from registry
        this.journalSystem = JournalSystem.getInstance();
    }

    preload() {
        super.preload();
        this.load.image('crossroadBg', 'assets/images/backgrounds/crossroad.png');
        // The dead demigod is a separate sprite so its fate (cut open / spores planted) swaps one
        // frame instead of the whole background. Frames: 0 intact, 1 skull opened, 2 mycelium tree.
        this.load.spritesheet('crossroad_corpse', 'assets/images/backgrounds/crossroad_corpse.png', { frameWidth: 240, frameHeight: 500 });
        this.load.image('door', 'assets/images/ui/door.png');
        this.load.image('skyship', 'assets/images/backgrounds/skyship.png');
        preloadGDProps(this); // shared Growth/Decay scenery props (see applyCrossroadGDState)
    }

    create() {
        super.create();

        // Phaser re-uses the scene instance on every start/restart: forget the previous run's objects and
        // the "already applied" guard, otherwise re-entering with growth would skip the glow + skyship zone.
        this.growthApplied = false;
        this.skyshipTransition = null;
        this.corpse = null;

        // Check if growth has happened
        this.hasGrowth = this.registry.get('crossroadGrowth') || false;
        
        // Initialize the journal system
        this.journalSystem = JournalSystem.getInstance();
        
        this.background = this.add.image(400, 300, 'crossroadBg'); // native 1067×600 — one picture for every corpse state
        this.fitBackground(this.background);
        this.background.setDepth(-1);
        // The background paints its own cobbled street; the generic ground strip would cover it.
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }
        this.playSceneMusic('genericMusic');

        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);

        this.createCorpse();
        if (this.hasGrowth) this.applyGrowth();
        this.applyCrossroadGDState();

        // Examine: the signpost/junction (placed on the upper post, clear of the corpse's own
        // interactive zone at center). Comment reflects the corpse's fate + how the world leans.
        this.createObservable(400, 196, 230, 110, () => { // 800-space coords; createObservable remaps X itself (the four boards, y 141–251)
            if (this.hasJournalEntry('crossroad_corpse_spores_planted')) return this.t('observe.crossroads.planted');
            if (this.getGDTendency && this.getGDTendency() === 'growthDominant') return this.t('observe.crossroads.overgrown');
            return this.t('observe.crossroads.default');
        }, { hint: this.t('observe.crossroads.hint') });

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);

        // Setup scene transitions using the transition manager
        this.setupSceneTransitions();

        // Load persisted symbiont system
        this.symbiontSystem = this.registry.get('symbiontSystem');

        // Add registry change listener to update the scene when growth state changes
        this.registry.events.on('changedata', this.handleRegistryChange, this);

        // Clean up event listener when scene is shut down
        this.events.on('shutdown', () => {
            this.registry.events.off('changedata', this.handleRegistryChange, this);
        });
    }

    setupSceneTransitions() {
        // Create transition zone for Shed521 entrance
        this.transitionManager.createTransitionZone(
            100, // x position
            400, // y position
            120, // width
            200, // height
            'left', // direction
            'Shed521Scene', // target scene
            100, // walk to x
            400 // walk to y
        );
        
        // Egg Cathedral: the road that comes TOWARD the viewer (bottom centre of the junction)
        this.transitionManager.createTransitionZone(
            400, // x position (800-space; remapped to the canvas centre)
            572, // y position
            150, // width
            56,  // height
            'down', // direction
            'EggCatedralScene', // target scene
            400, // walk to x
            470 // walk to y
        );
        
        // Create transition zone for VoxMarket entrance
        this.transitionManager.createTransitionZone(
            650, // x position
            400, // y position
            100, // width
            200, // height
            'right', // direction
            'VoxMarket', // target scene
            650, // walk to x
            470 // walk to y
        );
        
        // Scraper: the road that runs AWAY from the viewer, past the signpost toward the hazy skyline
        this.transitionManager.createTransitionZone(
            409, // x position (800-space ≈ canvas 545, the road's centre line right of the corpse)
            400, // y position
            52,  // width
            120, // height
            'up', // direction
            'ScraperScene', // target scene
            409, // walk to x
            470 // walk to y
        );
    }

    /** Growth/Decay scenery: props only (the background has no variants yet); feet stay behind the walk line. */
    applyCrossroadGDState() {
        placeGDProps(this, {
            growth: [
                { prop: 'bush', x: 214, y: 514, scale: 0.9 },
                { prop: 'mushrooms', x: 788, y: 500 },
                { prop: 'vine', x: 759, y: 302 }          // off the hangar's impost cornice, down the left pilaster
            ],
            decay: [
                { prop: 'fire', x: 724, y: 506 },
                { prop: 'trash', x: 326, y: 506 },
                { prop: 'crate', x: 992, y: 474, scale: 0.9 },
                { prop: 'rubble', x: 176, y: 500 }
            ]
        });
    }

    /** Which corpse frame the persisted state calls for (growth wins; a cut skull stays cut). */
    corpseFrame() {
        if (this.hasGrowth) return CORPSE_FRAME.growth;
        if (this.hasJournalEntry('symbiont_thorne_still_offered')) return CORPSE_FRAME.cut;
        return CORPSE_FRAME.intact;
    }

    createCorpse() {
        // Hangs impaled on a stake planted in a cairn at the junction, beside the signpost, just LEFT of the road that
        // runs away to the Scraper (so that road stays visible and clickable); the walk line (y≈534) passes in front.
        // The sprite's foot (y 496) is the cairn; the body hangs 60 px above it, the lolled head leans right.
        this.corpseX = Math.round(this.scale.width / 2) - 125; // clear of the CATHEDRAL board too
        this.corpse = this.add.sprite(this.corpseX, 496, 'crossroad_corpse', this.corpseFrame())
            .setOrigin(0.5, 1)
            .setDepth(6);
        // Only the figure + its stake are clickable (frame-local rect): the tree above must leave the skyship zone free.
        this.corpse.setInteractive({
            hitArea: new Phaser.Geom.Rectangle(56, 136, 128, 360),
            hitAreaCallback: Phaser.Geom.Rectangle.Contains,
            useHandCursor: true
        });
        this.corpse.on('pointerdown', () => {
            if (this.dialogVisible) return;
            this.showCorpseDialog();
        });
    }

    /** Spores took: swap the corpse to its overgrown frame, light it, open the way to the skyship. Idempotent. */
    applyGrowth() {
        if (this.growthApplied) return;
        this.growthApplied = true;
        this.hasGrowth = true;
        if (this.corpse) this.corpse.setFrame(CORPSE_FRAME.growth);
        this.createGrowthGlow();
        this.createSkyshipZone();
    }

    /** Soft bioluminescent light the tree throws on the junction (sits between background and corpse). */
    createGrowthGlow() {
        const cx = this.corpseX ?? this.scale.width / 2;
        const glow = this.add.graphics().setDepth(5).setBlendMode(Phaser.BlendModes.ADD);
        for (let i = 4; i >= 1; i--) {
            glow.fillStyle(0x3f8f5a, 0.05);
            glow.fillEllipse(cx + 28, 98, 110 * i, 110 * i);   // the caps (the tree rises from the lolled crown, right of centre)
            glow.fillEllipse(cx, 470, 120 * i, 36 * i);        // spill on the flagstones around the figure
        }
        this.tweens.add({ targets: glow, alpha: { from: 0.7, to: 1 }, duration: 2200, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    }

    /** Clickable zone over the mycelium tree that triggers the look-up at the skyship. */
    createSkyshipZone() {
        if (this.skyshipTransition) return;
        const cx = (this.corpseX ?? this.scale.width / 2) + 28, cy = 100; // the tree out of the lolled crown (game y ≈ 44–146)
        this.skyshipTransition = this.add.image(cx, cy, 'door')
            .setDisplaySize(110, 120)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true })
            .setDepth(10);

        // Pulsing hint that the tree can be examined
        const skyshipGlow = this.add.graphics();
        skyshipGlow.fillStyle(0x7fff8e, 0.2);
        skyshipGlow.fillCircle(cx, cy, 50);
        skyshipGlow.setDepth(9);
        this.tweens.add({
            targets: skyshipGlow,
            alpha: { from: 0.2, to: 0.4 },
            duration: 1500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        this.setupSkyshipTransition();
    }

    get dialogContent() {
        const hasBrine = !!this.symbiontSystem?.hasSymbiont('brine-scripture');
        const hasOsswine = !!this.symbiontSystem?.hasSymbiont('osswine');
        return {
            ...super.dialogContent,
            speaker: 'Giant Corpse',
            corpseMain: {
                text: `You find a strange, gigantic corpse. Its flesh seems to pulse with an otherworldly energy. It is clear that it's been here for a while, but surprisingly, it doesn't smell at all. What do you do?`,
                onTrigger: (option) => this.sporeGate(option),
                options: [
                    {
                        text: 'Plant spores in it (10 spores)',
                        key: 'plant_spores_in_it',
                        next: 'plantSpores'
                    },
                    {
                        text: 'Cut it open',
                        key: 'cut_it_open',
                        next: 'acceptSymbiont'
                    },
                    ...(hasBrine ? [{ text: '[Salt Recall] Read what remains in it.', key: 'salt_recall_corpse', next: 'corpse_salt_recall' }] : []),
                    ...(hasOsswine ? [{ text: '[Grave-Sense] Read how it died.', key: 'grave_sense_corpse', next: 'corpse_grave_sense' }] : []),
                    {
                        text: 'Leave it alone',
                        key: 'leave_it_alone',
                        next: 'closeDialog'
                    }
                ]
            },
            corpseExhausted: {
                text: `There is nothing more you can do with the old corpse. Its purpose has been fulfilled.`,
                options: [
                    ...(hasBrine ? [{ text: '[Salt Recall] Read what remains in it.', key: 'salt_recall_corpse', next: 'corpse_salt_recall' }] : []),
                    ...(hasOsswine ? [{ text: '[Grave-Sense] Read how it died.', key: 'grave_sense_corpse', next: 'corpse_grave_sense' }] : []),
                    {
                        text: 'Leave it alone',
                        key: 'leave_it_alone',
                        next: 'closeDialog'
                    }
                ]
            },
            corpse_grave_sense: {
                speaker: 'Osswine',
                text: `Osswine wakes up and reads the final moments of the immense creature before you. *"...A lot of violence. He was the illegitimate son of the god Lietus Kika, who came to the city to die and left his son at the mercy of the world. It seems the demigod had quite a successful career as a tyrant and the city's supreme ruler, hmm. But one day, an enraged mob put an end to his career — tough luck. They left the bastard's body to rot at the crossroads so that no divine being would ever again dare to try to rule Upper Morkezela. But they didn't know that a demigod's body would withstand the ravages of time and remain here forever. Then again, they said that was even better — at least the memento would be permanent."*`,
                onTrigger: () => {
                    if (!this.hasJournalEntry('grave_sense_crossroad_corpse')) {
                        this.addJournalEntry(
                            'grave_sense_crossroad_corpse',
                            'Grave-Sense: How the Corpse Died',
                            'Through Osswine I read the giant corpse\'s ending: a lot of violence. He was the illegitimate son of the god Lietus Kika, left to the world when his father came here to die. He made himself tyrant and supreme ruler of the city, until an enraged mob ended him and left the body at the crossroads as a warning to any divine being who would try to rule Upper Morkezela. A demigod\'s body does not rot — so the warning stands forever.',
                            this.journalSystem.categories.LORE,
                            { location: 'Crossroad', via: 'osswine' }
                        );
                    }
                },
                options: [
                    { text: 'Step back.', key: 'grave_sense_corpse_back', next: 'closeDialog' }
                ]
            },
            corpse_salt_recall: {
                speaker: 'Brine Scripture',
                text: `Brine Scripture stirs and tastes the salt the great body has been leaking into the crossroad for years. *"This one has come a long way. The illegitimate child of the god Lietus Kika. Not a god — a demigod, a divine bastard. Lietus, the god of temporal confusion, came to the city to die, bringing his bastard son with him. But in his typical state of confusion, he didn't have time to secure a future for his son."*\n\n*"The bastard son attempted to take control of the city. He became a tyrant, until finally an enraged mob lynched him, murdered him, and left his body to rot at the crossroads. However, his demigod-like body resisted decay, and so this place gained a new landmark. Today, the locals are proud of it and can no longer imagine the crossroads without the demigod's corpse."*`,
                onTrigger: () => {
                    if (!this.hasJournalEntry('salt_recall_crossroad_corpse')) {
                        this.addJournalEntry(
                            'salt_recall_crossroad_corpse',
                            'Salt Recall: The Crossroad Corpse',
                            'Through Brine Scripture I read the salt-memory of the giant corpse at the crossroad. Not a god but a demigod: the bastard son of Lietus Kika, god of temporal confusion, who brought him here to die and, in his usual confusion, never secured his future. The son tried to rule the city, became a tyrant and was lynched; his demigod body refused to rot, and the locals grew proud of their landmark.',
                            this.journalSystem.categories.LORE,
                            { location: 'Crossroad', via: 'brine-scripture' }
                        );
                    }
                },
                options: [
                    { text: 'Step back.', key: 'salt_recall_corpse_back', next: 'closeDialog' }
                ]
            },
            corpseReconsider: {
                text: `You approach the strange corpse again. From within, you hear a familiar voice: "Changed your mind, baby? I'm still here waiting for you."`,
                onTrigger: (option) => this.sporeGate(option),
                options: [
                    {
                        text: 'Accept Thorne-Still as your symbiont',
                        key: 'accept_thornestill_as_your_symbiont',
                        next: 'acceptSymbiontConfirm'
                    },
                    {
                        text: 'Plant spores in it instead (10 spores)',
                        key: 'plant_spores_in_it_instead',
                        next: 'plantSpores'
                    },
                    {
                        text: 'Leave it alone',
                        key: 'leave_it_alone',
                        next: 'closeDialog'
                    }
                ]
            },
            notEnoughSpores: {
                text: `You reach for your spores, but there aren't enough of them to seed something this large. You'd need at least ten.`,
                options: [
                    { text: 'Step back.', key: 'not_enough_spores_back', next: 'closeDialog' }
                ]
            },
            plantSpores: {
                text: 'You carefully plant spores in the corpse. They immediately take root, spreading a network of luminescent mycelium through the dead flesh. This area will never be the same.',
                options: [
                    {
                        text: 'Continue',
                        key: 'continue',
                        next: 'closeDialogAndGrow'
                    }
                ]
            },
            acceptSymbiont: {
                speaker: 'Thorne-Still',
                text: `As you cut into the corpse's head, you find something extraordinary — a symbiotic entity that calls itself Thorne-Still. "Hey there, baby, I'm Thorne-Still. How can I help you today?" it whispers in a strange voice. "Maybe we can share a road for some time? What do you say? That fungus of yours looks comfortable enough for me."`,
                options: [
                    {
                        text: 'Accept Thorne-Still as your symbiont',
                        key: 'accept_thornestill_as_your_symbiont',
                        next: 'acceptSymbiontConfirm'
                    },
                    {
                        text: 'Decline',
                        key: 'decline',
                        next: 'declineSymbiont'
                    }
                ],
                onTrigger: () => {
                    // The skull is open from now on, whatever the player decides about Thorne-Still
                    if (this.corpse && !this.hasGrowth) this.corpse.setFrame(CORPSE_FRAME.cut);
                    // Mark that the symbiont has been offered
                    this.addJournalEntry(
                        'symbiont_thorne_still_offered',
                        'Encountered Thorne-Still',
                        'In the strange corpse at the crossroads, I found a symbiotic entity calling itself Thorne-Still. It offered to merge with me.',
                        this.journalSystem.categories.EVENTS
                    );
                }
            },
            acceptSymbiontConfirm: {
                text: 'Thorne-Still merges with your being. It literally crawls into your stomach. You feel its calm presence in your mind, and with it comes the ability to perceive the threads of reality itself. You can now use the Brain Rot ability to make others confused, forgetful, or vulnerable to suggestion.',
                options: [
                    {
                        text: 'Continue',
                        key: 'continue',
                        next: 'closeDialogAndAcceptSymbiont'
                    }
                ]
            },
            declineSymbiont: {
                speaker: 'Thorne-Still',
                text: `"Your loss, baby," whispers the symbiont. "But don't worry, I'll be here if you need me."`,
                options: [
                    {
                        text: 'Continue',
                        key: 'continue',
                        next: 'closeDialogAndDeclineSymbiont'
                    }
                ]
            },
            closeDialog: {
                text: '',
                options: [],
                onShow: () => {
                    this.hideDialog();
                }
            },
            closeDialogAndGrow: {
                text: '',
                options: [],
                onTrigger: () => {
                    // Decrease spores by 10 (adjust as desired)
                    this.modifySpores(-10);

                    // Increase Growth by 2
                    this.modifyGrowthDecay(2, 0);
                    
                    // Add journal entry for planting spores
                    this.addJournalEntry(
                        'crossroad_corpse_spores_planted',
                        'Planted Spores in the Crossroad Corpse',
                        'I planted spores in the strange corpse at the crossroads. The mycelium quickly spread through the dead flesh, transforming the area with luminescent growth — and I noticed something up above it.',
                        this.journalSystem.categories.EVENTS
                    );
                    
                    // Persist the growth state (the registry listener keeps other scenes in step) and show it
                    const firstTime = !this.growthApplied;
                    this.registry.set('crossroadGrowth', true);
                    this.applyGrowth();
                    if (firstTime) this.showNotification(this.t('crossroad.plantGrows'));

                    this.hideDialog();
                }
            },
            closeDialogAndDeclineSymbiont: {
                text: '',
                options: [],
                onShow: () => {
                    // Mark that the symbiont has been declined using journal entry
                    this.addJournalEntry(
                        'symbiont_thorne_still_declined',
                        'Declined Thorne-Still',
                        'I declined the offer from the symbiotic entity Thorne-Still. It seemed disappointed but said it would wait for me if I changed my mind.',
                        this.journalSystem.categories.EVENTS
                    );
                    this.hideDialog();
                }
            },
            closeDialogAndAcceptSymbiont: {
                text: '',
                options: [],
                onShow: () => {
                    // Increase Decay by 2
                    this.modifyGrowthDecay(0, 2);
                    
                    // Mark that the symbiont has been accepted using journal entry
                    this.addJournalEntry(
                        'symbiont_thorne_still_accepted',
                        'Accepted Thorne-Still',
                        'I accepted the symbiotic entity Thorne-Still. It merged with me, crawling into my stomach. I can now use its Brain Rot ability to confuse and manipulate others.',
                        this.journalSystem.categories.EVENTS
                    );
                    
                    const success = this.symbiontSystem.addSymbiont('thorne-still', {
                        name: 'Thorne-Still',
                        power: 0,
                        ability: 'Brain Rot'
                    });

                    if (success) {
                        // Show notification about gaining the symbiont
                        this.showNotification(this.t('notifications.symbiontGained', { name: 'Thorne-Still' }));
                        
                        // Add symbiont icon
                        this.addSymbiontIcon('thorne-still', {
                            name: 'Thorne-Still',
                            power: 0,
                            ability: 'Brain Rot'
                        });
                    }
                    this.hideDialog();
                }
            }
        }
    }
    
    /** Planting spores costs 10; with fewer, the option explains instead of going negative. */
    sporeGate(option) {
        if (!option || !['plant_spores_in_it', 'plant_spores_in_it_instead'].includes(option.key)) return;
        const spores = this.sporeSystem?.currentSpores ?? this.registry.get('sporeSystem')?.currentSpores ?? 0;
        if (spores < 10) return 'notEnoughSpores';
    }

    showCorpseDialog() {
        // Determine which dialog to show based on journal entries
        if (this.hasJournalEntry('symbiont_thorne_still_accepted') || this.hasGrowth) {
            // Symbiont taken or spores planted — nothing left to do with the corpse
            this.showDialog('corpseExhausted');
        } else if (this.hasJournalEntry('symbiont_thorne_still_declined') || this.hasJournalEntry('symbiont_thorne_still_offered')) {
            // Offered (even if the player just closed the dialog) or declined — Thorne-Still is still waiting
            this.showDialog('corpseReconsider');
        } else {
            // First interaction
            this.showDialog('corpseMain');
        }
    }
    
    startSkyshipAnimation() {
        // Create a camera zoom effect to simulate looking up
        const originalZoom = this.cameras.main.zoom;
        
        // The skyship picture (native 1067×600, tools/artgen/skyship_bg.py) fills the screen once the camera has
        // tilted up: pinned to the screen and scaled by 1/zoom so it lands pixel-exact on the zoomed camera.
        const W = this.scale.width, H = this.scale.height;
        const skyship = this.add.image(W / 2, H / 2, 'skyship').setScrollFactor(0);
        skyship.setAlpha(0);
        skyship.setDepth(10000);
        
        // Create a text message (under the ship, pinned to the screen like the picture)
        const messageBox = this.add.rectangle(W / 2, H - 80, 600, 100, 0x0a2712, 0.9).setScrollFactor(0);
        messageBox.setStrokeStyle(2, 0x7fff8e);
        messageBox.setDepth(10100);
        messageBox.setAlpha(0);
        
        const messageText = this.add.text(W / 2, H - 80, "Looks like there is a skyship above the city...", {
            fontSize: '18px',
            fill: '#7fff8e',
            align: 'center',
            wordWrap: { width: 580 }
        });
        messageText.setOrigin(0.5).setScrollFactor(0);
        messageText.setDepth(10200);
        messageText.setAlpha(0);
        
        // Use sequential tweens instead of timeline
        // Step 1: First zoom out slightly to prepare for looking up
        this.tweens.add({
            targets: this.cameras.main,
            zoom: originalZoom * 0.9,
            duration: 1000,
            ease: 'Sine.easeInOut',
            onComplete: () => {
                // Add journal entry about skyship seen above the city
                if (!this.hasJournalEntry('skyship_sighting')) {
                    this.addJournalEntry(
                        'skyship_sighting',
                        'Strange Vessel in the Emerald Sky',
                        'A massive skyship hovers above Upper Morkezela, its hull gleaming with an unnatural light. Its purpose remains unknown, though spores seem to drift down from it on the wind.',
                        this.journalSystem.categories.EVENTS,
                        { location: 'Upper Morkezela skyline' }
                    );
                }
                // The growth from the planted corpse turns out to lead up to it
                this.addJournalFact('crossroad_corpse_spores_planted', 'skyship', "The growth has opened a path up to a skyship hanging above the crossroads.");
                // Step 2: Then zoom in and pan up to simulate looking up
                this.tweens.add({
                    targets: this.cameras.main,
                    zoom: originalZoom * 1.2,
                    scrollY: -150,
                    duration: 2000,
                    ease: 'Sine.easeInOut',
                    onComplete: () => {
                        // Step 3: Fade in the skyship (scaled against the zoom the camera ended on)
                        const inv = 1 / this.cameras.main.zoom;
                        [skyship, messageBox, messageText].forEach(o => o.setScale(inv));
                        messageBox.y = messageText.y = H / 2 + (H / 2 - 80) * inv;
                        this.tweens.add({
                            targets: skyship,
                            alpha: 1,
                            duration: 2000,
                            ease: 'Sine.easeOut',
                            onComplete: () => {
                                // Step 4: Show the message after the skyship appears
                                this.tweens.add({
                                    targets: [messageBox, messageText],
                                    alpha: 1,
                                    duration: 1000,
                                    ease: 'Sine.easeInOut',
                                    onComplete: () => {
                                        // Step 5: Wait a moment and then transition to the SkyshipBoardScene
                                        this.time.delayedCall(3000, () => {
                                            // Fade out to transition to the new scene
                                            this.cameras.main.fadeOut(1000, 0, 0, 0);
                                            this.cameras.main.once('camerafadeoutcomplete', () => {
                                                // Reset camera settings before changing scenes
                                                this.cameras.main.zoom = originalZoom;
                                                this.cameras.main.scrollX = 0;
                                                this.cameras.main.scrollY = 0;
                                                
                                                // Start the SkyshipBoardScene
                                                this.scene.start('SkyshipBoardScene');
                                                this.isTransitioning = false;
                                            });
                                        });
                                    }
                                });
                            }
                        });
                    }
                });
            }
        });
    }

    // Handle registry changes, particularly for crossroadGrowth
    handleRegistryChange(parent, key, data) {
        // If the crossroadGrowth registry key changes, update the scene
        if (key === 'crossroadGrowth' && data === true) this.applyGrowth();
    }
    
    // Setup the transition for the skyship area
    setupSkyshipTransition() {
        if (!this.skyshipTransition) return;
        
        console.log('Setting up skyship transition');
        
        this.skyshipTransition.on('pointerdown', () => {
            console.log('Skyship transition clicked');
            if (this.isTransitioning) return;
            this.isTransitioning = true;
            
            // Get priest position
            const priest = this.priest;
            if (!priest) {
                // If priest doesn't exist, just start the animation immediately
                console.log('No priest found, starting skyship animation directly');
                this.startSkyshipAnimation();
                return;
            }
            
            // Calculate distance to transition point
            const distance = Phaser.Math.Distance.Between(
                priest.x, priest.y,
                this.skyshipTransition.x, this.skyshipTransition.y
            );
            
            // Calculate duration based on distance (faster for closer distances)
            const duration = Math.min(Math.max(distance * 5, 500), 2000);
            
            // Create a variable to track if the tween completed
            let tweenCompleted = false;
            
            // Move priest to the transition point
            priest.play('walk');
            
            // Kill any existing tweens
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: this.skyshipTransition.x,
                y: 470,
                duration: duration,
                ease: 'Linear',
                onComplete: () => {
                    tweenCompleted = true;
                    priest.play('idle');
                    this.startSkyshipAnimation();
                }
            });
            
            // Add a safety timeout in case the tween doesn't complete
            this.time.delayedCall(2000, () => {
                if (!tweenCompleted) {
                    console.log('Skyship transition tween timed out, forcing transition');
                    if (priest.anims && priest.anims.exists('idle')) {
                        priest.play('idle');
                    }
                    this.startSkyshipAnimation();
                }
            });
        });
    }
    
    update() {
        super.update();

        // Check if player is at the right edge of the screen
        if (this.priest && this.priest.x > this.scale.width - 20 && !this.isTransitioning) { // right edge relative to the canvas (literal 780 misfired after the x-remap)
            this.isTransitioning = true;
            this.priest.play('idle');
            this.cameras.main.fadeOut(800, 0, 0, 0);
            this.cameras.main.once('camerafadeoutcomplete', () => {
                this.scene.start('ScraperScene'); // the signpost points SCRAPER to the right; Voxmarket has its own zone at the hangar doors
                this.isTransitioning = false; // Reset transition flag
            });
        }

        if (this.priest && this.priest.x < 80 && !this.isTransitioning) {
            this.isTransitioning = true;
            this.priest.play('idle');
            this.cameras.main.fadeOut(800, 0, 0, 0);
            this.cameras.main.once('camerafadeoutcomplete', () => {
                this.scene.start('EggCatedralScene');
                this.isTransitioning = false; // Reset transition flag
            });
        }

        // Check Growth/Decay effects on symbionts
        if (this.symbiontSystem) {
            const growth = this.registry.values.growth || 0;
            const decay = this.registry.values.decay || 0;
            const effect = this.symbiontSystem.checkDecayGrowthEffects(decay, growth);
            
            if (effect) {
                if (effect.type === 'leave') {
                    this.showNotification(effect.message, 0xff0000);
                }
            }
        }
    }
}
