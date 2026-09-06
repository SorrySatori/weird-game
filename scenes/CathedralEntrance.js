import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import LanguageSystem from '../systems/LanguageSystem.js';

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
                    { text: "I'm Master Thaal's apprentice. Surely I may pass.", key: 'im_a_master_thaals_apprentice_surely_i_may_pass', next: "iAmFungalApprentice" }
                ]
            },
            templeGuardAskSomethingElse: {
        text: "Is there anything else I can help you with?",
                options: [
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
                    { text: "Ask something else", key: 'ask_something_else', next: "templeGuardAskSomethingElse" }
                ]
            },
            templeGuardWhen: {
        text: "I have no idea. When the great Council says so. It could be days, it could be centuries. We stand guard until the Awakening.",
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
        text: "Probably at the Voxmarket, or around Shed 521. Look for the door that doesn’t open — until it does.",
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
                ]
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
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set cathedral entrance background
        const bg = this.add.image(400, 300, 'cathedralEntranceBg');
        this.fitBackground(bg);
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

        // Once the Guardian has granted passage, a way further in stands open (top of scene).
        if (this.hasJournalEntry('cathedral_guardian_passed')) {
            this.transitionManager.createTransitionZone(
                400, // x position
                40,  // y position (top — deeper into the cathedral)
                200, // width
                40,  // height
                'up', // direction
                'EggCathedralStudyScene', // target scene (first room: the Bishop's study)
                400, // walk to x
                80,  // walk to y
                'Into the Cathedral' // destination name
            );
        }

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

        // Examine: the glowing Egg in the arch (upper glow, clear of the Sentinel at the door).
        // What the protagonist says shifts once they've met the mind in the cellar / heard
        // Ortolan's "flawed make" read of it.
        // On the UPPER glow of the egg — the Sentinel (guard container at 380,450, hit area
        // ~y350-510) sits over the lower egg and would otherwise eat the click.
        this.createObservable(385, 250, 200, 130, () => {
            if (this.hasJournalEntry('perspective_ortolan')) return this.t('observe.egg_cathedral.ortolan');
            if (this.hasJournalEntry('met_infinite_fold')) return this.t('observe.egg_cathedral.knows');
            return this.t('observe.egg_cathedral.default');
        }, { hint: this.t('observe.egg_cathedral.hint'), overObject: true }); // priest spawns far left; anchor the bubble to the egg
    }
    
    // Override the dialogContent getter from GameScene
    get dialogContent() {
        // Combine parent dialog content with our temple guard dialog + the Guardian
        // encounter (unlocked once the player has met Infinite Fold in the cellar).
        const parentContent = super.dialogContent || {};
        return {
            ...parentContent,
            ...this._templeGuardDialogContent,
            ...this._guardianDialogContent()
        };
    }

    /**
     * The Guardian encounter. The Sentinel of the Veil IS the Guardian — the last
     * mechanism of the old religious order. Once the player has met Infinite Fold
     * (`met_infinite_fold`), the Sentinel steps aside and the cathedral's own charge
     * speaks through it. It does not test title or strength — only the reason in the
     * player's chest: to master (refuse), to know (hesitate), or to witness (accept).
     * Reacts to the player's whole path. Grants entry on the witness answer.
     */
    _guardianDialogContent() {
        const sys = this.symbiontSystem || this.registry.get('symbiontSystem');
        const symbiontCount = sys?.getSymbiontCount?.() ?? 0;  // ALL symbionts count toward "you are many"
        const foldJournal = this.getJournalEntry ? this.getJournalEntry('infinite_fold_ending') : null;
        const foldEnding = this.registry.get('infinite_fold_ending') || foldJournal?.metadata?.ending;
        const foldEngaged = !!foldEnding && foldEnding !== 'sealed';
        const edgarPath = !!this.hasJournalEntry('edgar_cathedral_path');
        const cs = (LanguageSystem.getInstance?.().getLanguage?.() === 'cs');

        // Guardian's reflection on the player's whole journey (history reactions).
        // Built dynamically, so localized here rather than via the (static) cs file.
        let reflect;
        if (cs) {
            reflect = "*\"Sleduji tě déle, než tušíš.\"*";
            if (foldEngaged) reflect += " *\"Setkal ses s myslí bez těla, a nesáhl jsi hned po nápravě. Nechal jsi ji být, ať už je podivná, jak chce.\"*";
            if (symbiontCount >= 1) reflect += " *\"Neseš v sobě jiný život, a nezmizel jsi v něm. Už víš, jaké to je být víc než jeden a přesto zůstat sám sebou.\"*";
            if (edgarPath) reflect += " *\"A naslouchal jsi hlasu, který město ignoruje — tomu, kdo hledá a nachází místa, jež se rozpadají.\"*";
            if (!foldEngaged && symbiontCount < 1 && !edgarPath) reflect += " *\"Přicházíš nalehko, s málem za sebou. To není chyba. Jen je toho míň k zvážení.\"*";
            reflect += " *\"Všechno jsem zvážil. Řekni, co potřebuješ, až budeš připraven.\"*";
        } else {
            reflect = "*\"I have watched you longer than you know.\"*";
            if (foldEngaged) reflect += " *\"You met a mind without a body, and did not reach at once for the cure. You let it be strange.\"*";
            if (symbiontCount >= 1) reflect += " *\"You carry another life inside your own, and have not vanished into it. You already know what it is to be more than one and remain yourself.\"*";
            if (edgarPath) reflect += " *\"And you listened to a voice the city taught itself to ignore — the one who finds the places that do not seal.\"*";
            if (!foldEngaged && symbiontCount < 1 && !edgarPath) reflect += " *\"You come lightly, with little behind you. That is not a fault. It is only less to weigh.\"*";
            reflect += " *\"All of it, I have weighed. Say what you have to say, when you are ready.\"*";
        }

        // The gate dissolving + the Guardian's farewell (dynamic → localized here).
        let farewell;
        if (cs) {
            farewell = "Brána se neotevře jako obyčejné dveře. Kámen se pomalu rozpouští jako stará jizva.\n\n*\"Půjdeš se mnou?\"* zeptáš se.\n\n*\"Ne.\"* Odmlka. *\"Vznikl jsem, abych hlídal dveře. Ne abych prošel.\"*";
            if (symbiontCount >= 1) farewell += " *\"Neseš něco, co nejsi ty — a přesto jsi zůstal celý. Snad právě proto jsi mohl vstoupit.\"*";
            if (foldEngaged) farewell += " *\"Setkal ses s myslí bez těla a nepokusil ses ji hned napravit. To si pamatuji.\"*";
            farewell += " Ustoupí stranou. *\"Tak tedy běž zjistit, co se tu zrodilo.\"*";
        } else {
            farewell = "The gate does not open like a gate. The stone slowly dissolves, like an old scar.\n\n*\"Will you come with me?\"* you ask.\n\n*\"No.\"* A pause. *\"I was made to guard the door. Not to pass beyond it.\"*";
            if (symbiontCount >= 1) farewell += " *\"You carry something that is not you — and yet you have stayed whole. Perhaps that is why it lets you enter.\"*";
            if (foldEngaged) farewell += " *\"You met a mind without a body, and did not try at once to correct it. That, I remember.\"*";
            farewell += " It steps aside. *\"Then go, and learn what has been born.\"*";
        }

        const testOptions = [
            { text: "Because someone must decide what happens here.", key: 'guardian_ans_power', next: "guardianPower" },
            { text: "Because I have to learn the whole truth.", key: 'guardian_ans_knowledge', next: "guardianKnowledge" },
            { text: "Because what is happening in there deserves to be heard.", key: 'guardian_ans_witness', next: "guardianWitness" }
        ];

        return {
            guardianGreeting: {
                speaker: 'The Guardian',
                text: "The Sentinel does not bar your way this time. Its glowing eyes find you and hold. When it speaks, the voice sounds ancient — as the cathedral's own, borrowed through its watchman.\n\n*\"You have been to the cellar. You carry almost the whole story now: the mind without a body, the truth of your Bishop, the shape of what grows behind these walls. I am what remains of the old order. I know why you have come. But you will say it, in your own words. Why do you wish to enter?\"*",
                options: [
                    ...testOptions,
                    { text: "What are you, truly?", key: 'guardian_nature', next: "guardianNature" },
                    { text: "You know what I did in the cellar of the Scraper?", key: 'guardian_reflect', next: "guardianReflect" },
                    { text: "Not yet. (Leave.)", key: 'guardian_leave', next: "closeDialog" }
                ]
            },

            guardianNature: {
                speaker: 'The Guardian',
                text: "*\"I am no priest, and no soldier. I am the last mechanism of a religious order that is already dust. They made me guard this place — but not, as the others believe, to keep out the unworthy. My charge was narrower, and very specific: to keep out anyone who would enter meaning to own what is born here. Titles do not move me. Nor strength. Only the reason.\"*",
                options: [
                    { text: "Why can't anyone own it?", key: 'guardian_why_own', next: "guardianOwn" },
                    { text: "Then let me answer. Why I wish to enter.", key: 'guardian_back_to_question', next: "guardianGreeting" }
                ]
            },

            guardianOwn: {
                speaker: 'The Guardian',
                text: "*\"Because a new life owned is not a life. It is a tool with a heartbeat. Your Bishop understood this — it is why she sealed the doors. Not to protect the cathedral, but to protect the world from the first hand that would reach in to possess what wakes. That hand has come before. It will come again. I am the power standing between.\"*",
                options: [
                    { text: "Let me answer your question, then.", key: 'guardian_own_back', next: "guardianGreeting" }
                ]
            },

            guardianReflect: {
                speaker: 'The Guardian',
                text: reflect,
                options: [
                    ...testOptions,
                    { text: "Give me a moment.", key: 'guardian_reflect_back', next: "guardianGreeting" }
                ]
            },

            guardianPower: {
                speaker: 'The Guardian',
                text: "*\"To decide.\"* The eyes dim. *\"You would enter as a hand that shapes, a will that settles the matter. That is the one reason I was made to refuse — for the one who decides is the one who owns. Come back when you know why that is not the same as helping. The way stays shut.\"*",
                options: [
                    { text: "Let me answer again.", key: 'guardian_power_retry', next: "guardianGreeting" },
                    { text: "Leave.", key: 'guardian_power_leave', next: "closeDialog" }
                ]
            },

            guardianKnowledge: {
                speaker: 'The Guardian',
                text: "*\"To learn.\"* A long pause; the staff-orb flickers. *\"Knowledge is not ownership — but it is not innocence either. Many have wished to know a thing only so they might use it. I do not refuse you. Nor do I open. Tell me the rest: what will you do with the truth once it is yours?\"*",
                options: [
                    { text: "Nothing. Carry it, and let what's inside speak for itself.", key: 'guardian_know_witness', next: "guardianWitness" },
                    { text: "Whatever must be done.", key: 'guardian_know_power', next: "guardianPower" },
                    { text: "Let me answer again.", key: 'guardian_know_retry', next: "guardianGreeting" }
                ]
            },

            guardianWitness: {
                speaker: 'The Guardian',
                text: "*\"To bear witness.\"* Something in the ancient voice eases, the way a held breath is finally let go. *\"Not to master it. Not to use it. To stand where it can be heard, and let it be what it is. That is the only reason I may open to.\n\nThen enter, apprentice. What waits within is neither the old god the pilgrims dreamed of, nor a monster. It is a beginning — and beginnings are fragile. Go gently.\"*",
                onTrigger: () => {
                    if (!this.hasJournalEntry('cathedral_guardian_passed')) {
                        this.registry.set('cathedral_entry_granted', true);
                        this.addJournalEntry(
                            'cathedral_guardian_passed',
                            'The Guardian Relents',
                            "I answered the Guardian — the Sentinel of the Veil, last mechanism of the old order — that I came only to bear witness, not to master or use what grows inside. It opened the way. It told me the truth it was set here to keep: the Bishop's seal was never to protect the cathedral, but to protect the world from the first hand that would reach in to own the new life waking there. And it told me its own end is bound to the birth — a thing to be decided within, with all present, not out here by it alone.",
                            this.journalSystem.categories.EVENTS,
                            { location: 'Egg Cathedral', related: 'The Guardian' }
                        );
                    }
                },
                options: [
                    { text: "Wait — what happens to you, when it's born?", key: 'guardian_witness_end', next: "guardianEnd" },
                    { text: "I'm ready. Open the way.", key: 'guardian_witness_enter', next: "guardianFarewell" }
                ]
            },

            guardianFarewell: {
                speaker: 'The Guardian',
                text: farewell,
                options: [
                    { text: "(Step through the threshold.)", key: 'guardian_farewell_enter', next: "closeDialog", onSelect: () => this.enterCathedralInterior() }
                ]
            },

            guardianEnd: {
                speaker: 'The Guardian',
                text: "*\"When it wakes fully, I end. The order that made me will have no more meaning, and neither will its last mechanism. I have known this longer than you have been alive.\"* The eyes blink. *\"Do not grieve it. My last charge may not be to prevent the birth — but to see that it happens rightly. Whether I am kept, or let go, is a thing to be decided in there. Not out here, by me alone. I have nothing else to say. Go. It is waiting.\"*",
                options: [
                    { text: "I'm ready. Open the way.", key: 'guardian_end_enter', next: "guardianFarewell" },
                    { text: "Not yet.", key: 'guardian_end_wait', next: "closeDialog" }
                ]
            }
        };
    }

    enterCathedralInterior() {
        if (this.isTransitioning) return;
        this.isTransitioning = true;
        if (this.clickSound) this.clickSound.play();
        this.cameras.main.fadeOut(600, 0, 0, 0);
        this.time.delayedCall(650, () => {
            this.scene.start('EggCathedralStudyScene');
        });
    }
    
    createTempleGuard() {
        // Container for the temple guard, standing just below the cathedral door.
        this.templeGuard = this.add.container(380, 450);
        this.templeGuard.setDepth(5);
        this.addGroundShadow(380, 508, 72, 18);

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
        this.guardGlow.fillCircle(380, 450, 50);
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
            this.showDialog(this.hasJournalEntry('met_infinite_fold') ? 'guardianGreeting' : 'templeGuardGreeting');
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
                'The Voxmarket is an audio bazaar where recorded voices and sounds are traded. The Bishop might be found there.',
                'guard_voxmarket'
            );
            this.showNotification('Quest updated: Find the Bishop');
        } else if (dialogKey === 'templeGuardShed521' && this.questSystem.getQuest('find_bishop')) {
            this.questSystem.updateQuest(
                'find_bishop',
                'Shed 521, also known as the Bureau of Shapes, is a bureaucratic maze where people register their forms. The Bishop is known to visit this place.',
                'guard_shed521'
            );
            this.showNotification('Quest updated: Find the Bishop');
        }

        // Show the dialog content
        super.showDialog(dialogKey);
    }
}
