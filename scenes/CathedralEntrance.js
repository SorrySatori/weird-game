import { notePlace } from '../utils/places.js';
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
                    { text: "Where can I find the Bishop?", key: 'where_can_i_find_the_bishop', next: "bishop_info" },
                    { text: "When will it open?", key: 'when_will_it_open', next: "templeGuardWhen" },
                    { text: "Why is it closed?", key: 'why_is_it_closed', next: "templeGuardWhy" },
                    { text: "Who are you?", key: 'who_are_you', next: "templeGuardWho" },
                    { text: "I need to speak with someone inside", key: 'i_need_to_speak_with_someone_inside', next: "speakWithSomeoneInside" },
                    { text: "I'm Master Thaal's apprentice. Surely I may pass.", key: 'im_a_master_thaals_apprentice_surely_i_may_pass', next: "iAmFungalApprentice" }
                ]
            },
            templeGuardAskSomethingElse: {
        text: "Is there anything else I can help you with?",
                options: [
                    { text: "Where can I find the Bishop?", key: 'where_can_i_find_the_bishop', next: "bishop_info" },
                    { text: "When will it open?", key: 'when_will_it_open', next: "templeGuardWhen" },
                    { text: "Why is it closed?", key: 'why_is_it_closed', next: "templeGuardWhy" },
                    { text: "Who are you?", key: 'who_are_you', next: "templeGuardWho" },
                    { text: "I need to speak with someone inside", key: 'i_need_to_speak_with_someone_inside', next: "speakWithSomeoneInside" },
                    { text: "I'm Master Thaal's apprentice. Surely I may pass.", key: 'im_a_master_thaals_apprentice_surely_i_may_pass', next: "iAmFungalApprentice" }
                ]
            },
            iAmFungalApprentice: {
        text: "(Tilts head) Even fungus-born clergy must heed the pulses. The Cathedral breathes its own rhythm. You must attune.",
                options: [
                    { text: "Where can I find the Bishop?", key: 'where_can_i_find_the_bishop', next: "bishop_info" },
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardWhen: {
        text: "I have no idea. When the great Council says so. It could be a single digestion, it could be a hundred thousand. We stand guard until the Awakening.",
                options: [
                    { text: "The Awakening?", key: 'the_awakening', next: "templeGuardAwakening" },
                    { text: "Where can I find the Bishop?", key: 'where_can_i_find_the_bishop', next: "bishop_info" },
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardAwakening: {
        text: "The Awakening is the moment when the cathedral is fully grown. Hatched. We stand guard until the Awakening.",
                options: [
                    // Leads into the guard's speculation about the hatching — the one place he nudges
                    // Growth/Decay (see showDialog below). Was unreachable before this option existed.
                    { text: "And what happens when it hatches?", key: 'what_happens_when_it_hatches', next: "templeGuardFruiting" },
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" }
                ]
            },
            speakWithSomeoneInside: {
                text: "No summons have been issued. No minds may enter without resonance. Wait. Or seek for your Bishop. She's one of the Council, I am sure you know.",
                options: [
                    { text: "I'm Master Thaal's apprentice. Surely I may pass.", key: 'im_a_master_thaals_apprentice_surely_i_may_pass', next: "iAmFungalApprentice" },
                    { text: "Where can I find the Bishop?", key: 'where_can_i_find_the_bishop', next: "bishop_info" },
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" }
                ]
            },
            bishop_info: {
        text: "She's not inside, if that's what you're hoping. She hasn't passed through this gate in many digestions. Probably at the Voxmarket, or around Shed 521. Look for the door that doesn’t open. Until it does.",
                options: [
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" },
                    { text: "What is the Voxmarket?", key: 'what_is_the_voxmarket', next: "templeGuardVoxmarket"},
                    {text: "What is the Shed 521?", key: 'what_is_the_shed_521', next: "templeGuardShed521"},
                ]
            },
            templeGuardVoxmarket: {
                text: "It's a sound market near Shed 521, where recorded voices, sounds, hisses, screams and static are sold. I've heard that every sound this city has ever made is filed away there somewhere by some trader, and can be bought. But that doesn't make sense.",
                options: [
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" },
                    { text: "What is the Shed 521?", key: 'what_is_the_shed_521', next: "templeGuardShed521" },
                ]
            },
            templeGuardShed521: {
                text: "Its official name is the Bureau of Shapes. If you want to change your body shape, you'll need a certificate. This is where you can get that certificate. You'll find it right next to Voxmarket.",
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
        text: "I am a Sentinel of the Veil, sworn to protect the sacred Egg Cathedral from contamination.",
                options: [
                    { text: "How long have you been here?", key: 'how_long_have_you_been_here', next: "templeGuardTime" },
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardFruiting: {
        text: "When the cathedral's fully hatched from its egg, something miraculous will happen. The walls will burst, spreading our consciousness across the stars... Or something like that. You know, nobody really knows, but I imagine it will be something truly magnificent.",
                options: [
                    { text: "That sounds apocalyptic", key: 'that_sounds_apocalyptic', next: "templeGuardApocalypse" },
                    { text: "That sounds fascinating", key: 'that_sounds_fascinating', next: "templeGuardFascinating" },
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardTime: {
                text: "I have stood at this post for three thousand digestions of the Stomach Clock. The city stopped counting years when the Tally-Keeper died. We count digestions now. My flesh has long since been partly replaced by plants. My consciousness is connected to the city. I think my left foot is made from rodents.",
                options: [
                    { text: "That's... familiar", key: 'thats_familiar', next: "templeGuardDisturbing" },
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" }
                ],
                // The one place the city's time unit gets explained.
                onTrigger: () => {
                    if (!this.hasJournalEntry('learned_digestions')) {
                        this.addJournalEntry(
                            'learned_digestions',
                            'Counting in Digestions',
                            "The Sentinel at the Egg Cathedral counts time in digestions of the Stomach Clock. He has stood at his post for three thousand of them. The city stopped counting years when the Tally-Keeper died. A digestion runs a little longer than a day and drifts against the sun; six make a week, three hundred make a year.",
                            this.journalSystem.categories.LORE,
                            { location: 'Egg Cathedral', related: 'The Stomach Clock' }
                        );
                    }
                }
            },
            templeGuardFascinating: {
                text: "Fascinating, isn't it? That's why all major faiths have their people here. No one wants to miss the chance that it will be their god to whom the cathedral will be devoted.",
                options: [
                    { text: "I see", key: 'i_see', next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardApocalypse: {
                text: "Apocalypse? No. Transformation. The cathedral will become something truly new, some say that it will become a birthplace of a new god. Nobody really knows, that's why all churches have their representatives present. It's all very interesting, see.",
                options: [
                    { text: "I see", key: 'i_see', next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardDisturbing: {
                text: "Glad you see it that way. I have gained immortality and purpose. I am never alone.",
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
        this.load.spritesheet('guard', 'assets/images/characters/guardian1.png', { frameWidth: 128, frameHeight: 176 });
        this.load.audio('cathedralSoundtrack', 'assets/sounds/cathedral.mp3'); // shared with EggCatedralScene
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        notePlace(this, 'place_egg_cathedral');   // the journal's Places tab, on the first visit
        
        // Set cathedral entrance background
        const bg = this.add.image(400, 300, 'cathedralEntranceBg');
        this.fitBackground(bg);
        bg.setDepth(-1);

        // The redrawn background (1067×600) paints its own paving, so drop the generic floor strip.
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);

        // Cathedral soundtrack — continues seamlessly from the exterior
        this.playSceneMusic('cathedralSoundtrack', { resume: true });

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

        // Examine: the glow through the glass above the cathedral door (the egg lies behind it).
        // Sits on the glowing transom (y≈241-313), above the Sentinel's hit area (~y332-508) so
        // the guard doesn't eat the click. 800-space coords; createObservable remaps x/width.
        this.createObservable(400, 277, 124, 72, () => this.t('observe.egg_cathedral.default'),
            { hint: this.t('observe.egg_cathedral.hint'), overObject: true }); // priest spawns far left; anchor the bubble to the glow
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
        // Container for the temple guard, standing on the steps in front of the cathedral door
        // (the door is centred on the canvas in the redrawn background).
        const guardX = this.scale.width / 2;
        this.templeGuard = this.add.container(guardX, 450);
        this.templeGuard.setDepth(5);
        this.addGroundShadow(guardX, 508, 72, 18);

        // Hand-drawn pixel-art guard (guardian1.png): a 6-frame idle animation laid out as a
        // 3×2 grid of 128×176 frames, shown at native size (scale 1). Origin is bottom-centre so
        // the feet rest on the shadow line (world y ≈ 508).
        const guardSprite = this.add.sprite(0, 58, 'guard').setOrigin(0.5, 1);
        this.templeGuard.add(guardSprite);
        if (!this.anims.exists('guardIdle')) {
            this.anims.create({
                key: 'guardIdle',
                frames: this.anims.generateFrameNumbers('guard', { start: 0, end: 5 }),
                frameRate: 6,
                repeat: -1,
            });
        }
        guardSprite.play('guardIdle');

        // Subtle green sentinel aura behind him (fungal-cathedral theme).
        this.guardGlow = this.add.graphics();
        this.guardGlow.fillStyle(0x7fff8e, 0.2);
        this.guardGlow.fillCircle(guardX, 450, 50);
        this.guardGlow.setDepth(4);
        this.tweens.add({
            targets: this.guardGlow,
            alpha: { from: 0.2, to: 0.1 },
            duration: 1500,
            yoyo: true,
            repeat: -1
        });

        // Interactive — hit area matches the 128×176 sprite footprint.
        const hitArea = new Phaser.Geom.Rectangle(-64, -118, 128, 176);
        this.templeGuard.setInteractive(hitArea, Phaser.Geom.Rectangle.Contains);

        // Hover effect
        this.templeGuard.on('pointerover', () => {
            this.templeGuard.setScale(1.05);
            document.body.style.cursor = 'pointer';
        });
        this.templeGuard.on('pointerout', () => {
            this.templeGuard.setScale(1);
            document.body.style.cursor = 'default';
        });

        // Show dialog on click, with a little acknowledging bob.
        this.templeGuard.on('pointerdown', () => {
            if (this.clickSound) this.clickSound.play();
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

        // First meeting: the guard goes into the People tab
        if (dialogKey === 'templeGuardGreeting' && !this.hasJournalEntry('temple_guard_meeting')) {
            this.addJournalEntry(
                'temple_guard_meeting',
                'The Temple Guard',
                "At the gate of the Egg Cathedral stands a guard who lets no one in. The cathedral is closed until further notice; the yolk, he says, sleeps uneasily.",
                this.journalSystem.categories.PEOPLE,
                { character: 'Temple Guard', location: 'Egg Cathedral' }
            );
        }

        // Handle quest updates
        if (dialogKey === 'templeGuardGreeting' && this.questSystem.getQuest('find_bishop')) {
            this.questSystem.updateQuest(
                'find_bishop',
                'The Egg Cathedral is closed and the guard at the gate lets no one in. He might know where to find the Bishop.',
                'guard_cathedral_closed'
            );
        } else if (dialogKey === 'bishop_info') {
            if (!this.questSystem.getQuest('find_bishop')) {
                this.questSystem.addQuest(
                    'find_bishop',
                    'Find the Bishop',
                    'The temple guard mentioned that the Bishop might help me gain access to the cathedral. I should seek her out.'
                );
            }
            this.questSystem.updateQuest(
                'find_bishop',
                "According to the guard, the Bishop isn't in the cathedral. I'll have to look for her around the city, most likely at the Voxmarket or around Shed 521.",
                'guard_bishop_not_inside'
            );
        } else if (dialogKey === 'templeGuardVoxmarket' && this.questSystem.getQuest('find_bishop')) {
            this.questSystem.updateQuest(
                'find_bishop',
                'The Voxmarket is an audio bazaar where recorded voices and sounds are traded. The Bishop might be found there.',
                'guard_voxmarket'
            );
        } else if (dialogKey === 'templeGuardShed521' && this.questSystem.getQuest('find_bishop')) {
            this.questSystem.updateQuest(
                'find_bishop',
                "Shed 521, officially the Bureau of Shapes, is where people get the certificate they need to change their body's shape. It's right next to the Voxmarket. The Bishop might be found there too.",
                'guard_shed521'
            );
        }

        // Show the dialog content
        super.showDialog(dialogKey);
    }
}
