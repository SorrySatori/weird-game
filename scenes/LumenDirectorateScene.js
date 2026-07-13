import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class LumenDirectorateScene extends GameScene {
    constructor() {
        super({ key: 'LumenDirectorateScene' });
        this.isTransitioning = false;
    }

    preload() {
        super.preload();
        this.load.image('lumenDirectorateBg', 'assets/images/backgrounds/LumenDirectorate.png');
        this.load.image('gardener', 'assets/images/characters/gardener.png');
        // Optional Growth/Decay alternate art — used automatically if the files exist, else the
        // base background is tinted. Missing files are handled by the loaderror handler.
        this.load.image('LumenDirectorate_growth', 'assets/images/backgrounds/LumenDirectorate_growth.png');
        this.load.image('LumenDirectorate_decay', 'assets/images/backgrounds/LumenDirectorate_decay.png');
        this.load.image('surplus_bloom', 'assets/images/items/surplus_bloom.png');
    }

    create() {
        super.create();
        this.playSceneMusic('genericMusic');

        const bg = this.add.image(400, 300, 'lumenDirectorateBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        this.transitionManager = new SceneTransitionManager(this);

        // Back to Town Square (right side)
        this.transitionManager.createTransitionZone(
            750,
            300,
            80,
            400,
            'right',
            'TownSquareScene',
            100,
            300,
        );

        // Enter the Lumen Directorate interior
        this.transitionManager.createTransitionZone(
            400,
            250,
            150,
            80,
            'up',
            'LumenDirectorateInteriorScene',
            400,
            450,
        );

        // Position the priest
        this.priest.x = 400;
        this.priest.y = 450;

        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        this.cameras.main.fadeIn(800, 0, 0, 0);

        // Show arrival notification
        this.time.delayedCall(500, () => {
            this.showNotification('Lumen Directorate Headquarters', 0x556B2F);
        });

        // Create the Gardener NPC
        this.createGardener();

        // Growth/Decay alternate scene state (assetless; hot-swaps to dedicated art if present).
        this.applyLumenGDState(bg);
    }

    /** Reskin the Directorate grounds to reflect a pronounced Growth/Decay balance. */
    applyLumenGDState(bg) {
        const t = this.getGDTendency ? this.getGDTendency() : 'balanced';
        if (t === 'balanced') return;
        const growth = t === 'growthDominant';
        const altKey = growth ? 'LumenDirectorate_growth' : 'LumenDirectorate_decay';
        if (this.textures.exists(altKey)) {
            bg.setTexture(altKey);
            bg.setDisplaySize(800, 600);
        } else {
            bg.setTint(growth ? 0xbfe8a0 : 0x9a8a6a); // lush green vs sickly sallow
        }
        if (growth) this._createLumenGrowthState();
        else this._createLumenDecayState();
    }

    _createLumenGrowthState() {
        // Extra bloom clusters spilling from the beds.
        for (const [x, y] of [[150, 470], [330, 500], [560, 485], [690, 465]]) {
            this.add.circle(x, y, 7 + Math.random() * 6, 0x9be86a, 0.85).setDepth(2);
        }
        // A ripe surplus bloom — harvestable once for spores while Growth runs high.
        if (!this.hasJournalEntry('lumen_surplus_harvested')) {
            const surplus = this.textures.exists('surplus_bloom')
                ? this.add.image(120, 430, 'surplus_bloom').setScale(0.2)
                : this.add.circle(120, 430, 15, 0xd6ff8a, 1).setStrokeStyle(2, 0x4caf50);
            surplus.setDepth(3);
            surplus.setInteractive({ useHandCursor: true });
            surplus.on('pointerover', () => { document.body.style.cursor = 'pointer'; });
            surplus.on('pointerout', () => { document.body.style.cursor = 'default'; });
            surplus.on('pointerdown', () => {
                if (this.dialogVisible || this.hasJournalEntry('lumen_surplus_harvested')) return;
                if (this.clickSound) this.clickSound.play();
                if (this.modifySpores) this.modifySpores(20);
                this.addJournalEntry(
                    'lumen_surplus_harvested',
                    'A Surplus Bloom',
                    "The Directorate's beds were so overgrown that a bloom had ripened with nothing left to feed. I harvested it — a windfall of living spores. The city's tilt toward growth had left more life than even the gardeners could use.",
                    this.journalSystem.categories.EVENTS,
                    { location: 'Lumen Directorate' }
                );
                this.showNotification('Harvested surplus bloom: +20 spores', 0x4caf50);
                surplus.destroy();
            });
        }
    }

    _createLumenDecayState() {
        // Curling, grey-edged growth.
        for (const [x, y] of [[150, 470], [330, 500], [560, 485]]) {
            this.add.circle(x, y, 6, 0x6b5a3a, 0.7).setDepth(2);
        }
        // A blighted bed you can examine.
        const blight = this.add.rectangle(200, 505, 100, 44, 0x4a3a24, 0.55).setStrokeStyle(1, 0x2a2418);
        blight.setDepth(2);
        blight.setInteractive({ useHandCursor: true });
        blight.on('pointerover', () => { document.body.style.cursor = 'pointer'; });
        blight.on('pointerout', () => { document.body.style.cursor = 'default'; });
        blight.on('pointerdown', () => {
            if (this.dialogVisible) return;
            this.showDialog('gardener_blight_bed');
        });
    }

    createGardener() {
        this.gardener = this.add.image(220, 430, 'gardener');
        this.gardener.setScale(0.15);
        this.gardener.setDepth(5);
        this.gardener.setInteractive({ useHandCursor: true });

        // Glow effect
        this.gardenerGlow = this.add.graphics();
        this.gardenerGlow.fillStyle(0x556B2F, 0.15);
        this.gardenerGlow.fillCircle(220, 430, 40);
        this.gardenerGlow.setDepth(4);

        this.tweens.add({
            targets: this.gardenerGlow,
            alpha: { from: 0.15, to: 0.05 },
            duration: 2000,
            yoyo: true,
            repeat: -1
        });

        // Subtle idle sway
        this.tweens.add({
            targets: this.gardener,
            angle: { from: -1, to: 1 },
            duration: 2500,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });

        // Hover effect
        this.gardener.on('pointerover', () => {
            this.gardener.setScale(0.16);
            document.body.style.cursor = 'pointer';
        });

        this.gardener.on('pointerout', () => {
            this.gardener.setScale(0.15);
            document.body.style.cursor = 'default';
        });

        // Click to talk
        this.gardener.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog('gardener_start');
        });
    }

    get dialogContent() {
        const hasLumenQuest = !!(this.questSystem?.getQuest('find_lumen_directorate') && !this.questSystem.getQuest('find_lumen_directorate').isComplete);
        const hasBishopQuest = !!(this.questSystem?.getQuest('who_killed_bishop') && !this.questSystem.getQuest('who_killed_bishop').isComplete);
        const hasEnterTownhallQuest = !!(this.questSystem?.getQuest('enter_townhall') && !this.questSystem.getQuest('enter_townhall').isComplete);
        const knowsSulkberries = !!this.hasJournalEntry('bishop_berries');
        const knowsLumenLead = !!this.hasJournalEntry('elphi_lumen_lead');
        const sulkberriesCleared = !!this.hasJournalEntry('sulkberries_cleared_verrik');
        const alreadyMetGardener = !!this.hasJournalEntry('met_gardener_verrik');
        const alreadyGrewMushroom = !!this.hasJournalEntry('grew_mushroom_verrik');
        // Lumen sabotage quest: Verrik hands over the restricted corrosive cultivar.
        const hasLumenSabotageQuest = !!(this.questSystem?.getQuest('join_lumen_directorate') && !this.questSystem.getQuest('join_lumen_directorate').isComplete);
        const gaveCultivar = !!this.hasJournalEntry('verrik_gave_cultivar');
        const hasCultivar = !!(this.hasItem && this.hasItem('corrosive_cultivar'));
        const passedGrowthTest = !!this.hasJournalEntry('ac_growth_test_passed');
        const joinedLumen = !!this.hasJournalEntry('lumen_directorate_joined');

        // Mushroom growing: gather game history for outcome determination
        const completedQuests = this.questSystem?.getAllQuests().filter(q => q.isComplete) || [];
        const journalEntries = this.journalSystem?.getAllEntries() || [];
        const hasThorne = !!this.symbiontSystem?.hasSymbiont('thorne-still');
        const hasNeme = !!this.symbiontSystem?.hasSymbiont('neme-crownmire');
        const hasUlvarex = !!this.symbiontSystem?.hasSymbiont('ulvarex-borrowed-horizon');
        const currentSpores = this.getSporeLevel() || 0;
        const growth = this.growthDecaySystem?.getGrowth() || 50;
        const decay = this.growthDecaySystem?.getDecay() || 50;

        // Determine spore cost tiers
        const canAfford10 = currentSpores >= 10;
        const canAfford25 = currentSpores >= 25;
        const canAfford50 = currentSpores >= 50;

        return {
            ...super.dialogContent,

            gardener_start: {
                speaker: 'Verrik the Gardener',
                moodNpc: 'verrik',
                text: alreadyMetGardener
                    ? `"Back again? The hedges don't trim themselves, but I can spare a moment."`
                    : `"Careful where you step — those root-tendrils took me three weeks to coax into spiral formation. Name's Verrik. I tend the living architecture here at the Directorate."`,
                options: [
                    { text: "What is this place?", key: 'what_is_this_place', next: "gardener_about_lumen" },
                    ...(growth >= 65 ? [{ text: "The beds are overflowing — the whole place is in bloom.", key: 'gardener_overflowing', next: "gardener_bloom_talk" }] : []),
                    ...(decay >= 65 ? [{ text: "Your beds look sick. What's turning in the soil?", key: 'gardener_beds_sick', next: "gardener_blight" }] : []),
                    ...(!passedGrowthTest && !joinedLumen ? [{ text: "How does someone join the Directorate?", key: 'i_was_told_to_come_here_about_joining_the_crew', next: "gardener_join" }] : []),
                    ...(hasEnterTownhallQuest ? [{ text: "I need to get into the Townhall. Any ideas?", key: 'i_need_to_get_into_the_townhall_any_ideas', next: "gardener_townhall" }] : []),
                    ...(hasLumenSabotageQuest && !hasCultivar && !gaveCultivar ? [{ text: "The Angle Corrector sent me — he said you keep a cultivar for... difficult problems.", key: 'the_angle_corrector_said_you_keep_a_cultivar', next: "gardener_cultivar" }] : []),
                    ...(knowsLumenLead ? [{ text: "I need to speak with someone about Cathedral oversight.", key: 'i_need_to_speak_with_someone_about_cathedral_overs', next: "gardener_bishop_lead" }] : []),
                    ...(knowsSulkberries && !sulkberriesCleared ? [{ text: "About those Sulkberries the Directorate supplied — were they clean?", key: 'about_those_sulkberries_the_directorate_supplied_w', next: "gardener_sulkberry_verify" }] : []),
                    ...(knowsSulkberries && !knowsLumenLead ? [{ text: "I'm looking into spiced Sulkberries. Who supplies them?", key: 'im_looking_into_spiced_sulkberries_who_supplies_th', next: "gardener_sulkberries" }] : []),
                    ...(hasBishopQuest && !knowsLumenLead && !knowsSulkberries ? [{ text: "I'm investigating the Bishop's death.", key: 'im_investigating_the_bishops_death', next: "gardener_bishop_vague" }] : []),
                    { text: "Looking for work. Anything I can help with?", key: 'looking_for_work_anything_i_can_help_with', next: "gardener_work_offer" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('met_gardener_verrik')) {
                        this.addJournalEntry(
                            'met_gardener_verrik',
                            'Met Verrik the Gardener',
                            'Met a gardener named Verrik outside the Lumen Directorate headquarters. He tends the living architecture around the building.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Verrik the Gardener' }
                        );
                    }
                }
            },

            gardener_about_lumen: {
                speaker: 'Verrik the Gardener',
                text: `"The Lumen Directorate. Keepers and protectors of everything that grows. That's the motto — well, the unofficial one. The official motto is 'Nothing Hidden. Nothing Lost.'\n\nThey run this city, more or less. Won the Board Games War, rebuilt half the districts, and now they make sure the green keeps spreading. Growth is everything to them — plants, fungi, ideas, influence. Especially influence."`,
                options: [
                    { text: "What do you do for them?", key: 'what_do_you_do_for_them', next: "gardener_role" },
                    { text: "Who's in charge here?", key: 'whos_in_charge_here', next: "gardener_leadership" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ]
            },

            gardener_role: {
                speaker: 'Verrik the Gardener',
                text: `"I cultivate. The walls, the walkways, the hedges — it's all alive, you know. The Directorate doesn't believe in dead architecture. Every surface should breathe, should grow.\n\nI'm low on the vine, so to speak. But I hear things. Plants are good listeners, and so am I."`,
                options: [
                    { text: "What kind of things do you hear?", key: 'what_kind_of_things_do_you_hear', next: "gardener_rumors" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ]
            },

            gardener_rumors: {
                speaker: 'Verrik the Gardener',
                text: `"Oh, this and that. The Directorate's been restless lately. Something about the Egg Cathedral being sealed — that's got them worried. They've had their eye on that place for years, waiting for the hatching.\n\nAnd there's been more traffic inside than usual. People going up to see the Angle Corrector. That's never a casual visit."`,
                options: [
                    { text: "Who is the Angle Corrector?", key: 'who_is_the_angle_corrector', next: "gardener_angle_corrector" },
                    { text: "They're worried about the Cathedral?", key: 'theyre_worried_about_the_cathedral', next: "gardener_cathedral" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ]
            },

            gardener_angle_corrector: {
                speaker: 'Verrik the Gardener',
                text: `"The Angle Corrector? That's... well, title and name all in one. Nobody knows their real name, or if they even have one. They handle the Directorate's more delicate affairs — cultivation oversight, Cathedral liaison, that sort of thing.\n\nIf you need answers about anything the Directorate touches, the Angle Corrector is who you want. Third floor, through the atrium. But they don't see just anyone. You'll need a reason."`,
                options: [
                    ...(hasLumenQuest ? [{ text: "Captain Liris sent me. That's my reason.", key: 'captain_liris_sent_me_thats_my_reason', next: "gardener_join_angle" }] : []),
                    ...(knowsLumenLead ? [{ text: "I'm here about the Bishop's dealings with the Directorate.", key: 'im_here_about_the_bishops_dealings_with_the_direct', next: "gardener_bishop_lead" }] : []),
                    { text: "I'll figure something out.", key: 'ill_figure_something_out', next: "gardener_angle_advice" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ]
            },

            gardener_angle_advice: {
                speaker: 'Verrik the Gardener',
                text: `"A word of advice — the Directorate values transparency, or at least the appearance of it. Don't try to be clever. State your business plainly. They respect directness.\n\nAnd don't touch the ferns in the atrium. They bite."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ]
            },

            gardener_cathedral: {
                speaker: 'Verrik the Gardener',
                text: `"The Egg Cathedral is the biggest growth event this city has seen in decades. Whatever's growing inside those eggs — the Directorate wants to be there when it hatches. They've been monitoring it, cataloguing every vibration.\n\nWhen the Bishop sealed the Cathedral... let's just say the mood around here got very tense. The Directorate doesn't like locked doors. 'Nothing Hidden,' remember?"`,
                options: [
                    { text: "Who is the Angle Corrector?", key: 'who_is_the_angle_corrector', next: "gardener_angle_corrector" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ]
            },

            gardener_leadership: {
                speaker: 'Verrik the Gardener',
                text: `"The Directorate isn't run by one person — it's a council. But the one you'll hear about most is the Angle Corrector. They handle the day-to-day, the sensitive matters, the things that need a... particular touch.\n\nCaptain Liris runs the skyship operations — the Verdigrace and its crew. She's Directorate through and through, but she's usually up in the clouds."`,
                options: [
                    { text: "Who is the Angle Corrector?", key: 'who_is_the_angle_corrector', next: "gardener_angle_corrector" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ]
            },

            gardener_join: {
                speaker: 'Verrik the Gardener',
                text: `"Joining up, eh? The Directorate's always growing — and it values dedication to growth in all its forms. Doesn't matter who sent you; the door's the same.\n\nYou'll want the Angle Corrector inside. Third floor, through the atrium. Tell them you're here to join and that the gardener pointed you up. That should get you through, at least."`,
                options: [
                    { text: "What should I expect?", key: 'what_should_i_expect', next: "gardener_join_expect" },
                    { text: "Thanks. I'll head inside.", key: 'thanks_ill_head_inside', next: "closeDialog" },
                ],
                onTrigger: () => {
                    const q = this.questSystem?.getQuest('find_lumen_directorate');
                    if (!q) {
                        this.questSystem.addQuest('find_lumen_directorate', 'Nothing Hidden. Nothing Lost', 'Verrik, the Directorate\'s gardener, pointed me to the Angle Corrector on the third floor. I should speak with them about joining the Lumen Directorate.');
                        this.showNotification('New quest: Nothing Hidden. Nothing Lost', 0x556B2F);
                    } else if (!q.isComplete) {
                        this.questSystem.updateQuest('find_lumen_directorate', 'The gardener Verrik directed me to speak with the Angle Corrector on the third floor of the Directorate about joining.', 'gardener_directions');
                    }
                }
            },

            gardener_join_angle: {
                speaker: 'Verrik the Gardener',
                text: `"Liris's name carries weight around here. Mention her, and the Angle Corrector will see you. Third floor. Don't dawdle in the atrium — it's beautiful, but it's also the Directorate's way of watching who comes and goes."`,
                options: [
                    { text: "Thanks for the tip.", key: 'thanks_for_the_tip', next: "gardener_start" },
                ],
                onTrigger: () => {
                    if (this.questSystem?.getQuest('find_lumen_directorate') && !this.questSystem.getQuest('find_lumen_directorate').isComplete) {
                        this.questSystem.updateQuest('find_lumen_directorate', 'The gardener Verrik directed me to speak with the Angle Corrector on the third floor of the Directorate. Captain Liris\'s name should get me through the door.', 'gardener_directions');
                    }
                }
            },

            gardener_join_expect: {
                speaker: 'Verrik the Gardener',
                text: `"The Angle Corrector will test you somehow — they always do. Not a fight or anything like that. More like... they'll want to know how you see growth. What it means to you.\n\nThe Directorate isn't just about plants and fungi. It's about potential. Expansion. Becoming more than what you are. If you can speak to that, you'll do fine."`,
                options: [
                    { text: "I'll keep that in mind.", key: 'ill_keep_that_in_mind', next: "gardener_start" },
                ]
            },

            gardener_bishop_lead: {
                speaker: 'Verrik the Gardener',
                text: `"The Bishop's dealings? That's above my pay grade, friend. But I can tell you this — the Bishop was a regular visitor here before she sealed the Cathedral. Came to see the Angle Corrector personally.\n\nAfter the sealing... the visits stopped. And the Angle Corrector's mood went from bad to worse. Something happened between them.\n\nYou'll want to go inside and ask directly. Third floor. Be respectful — and honest. The Directorate can smell a lie faster than my ferns can smell rain."`,
                options: [
                    { text: "The Bishop visited regularly?", key: 'the_bishop_visited_regularly', next: "gardener_bishop_visits" },
                    { text: "Thanks. I'll head inside.", key: 'thanks_ill_head_inside', next: "closeDialog" },
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('who_killed_bishop', 'The gardener Verrik at the Lumen Directorate mentioned the Bishop used to visit regularly — specifically to see the Angle Corrector. The visits stopped when the Cathedral was sealed. Something happened between them.', 'gardener_bishop_info');
                    if (!this.hasJournalEntry('gardener_bishop_visits')) {
                        this.addJournalEntry(
                            'gardener_bishop_visits',
                            'Bishop\'s Visits to the Lumen Directorate',
                            'Verrik the gardener at the Lumen Directorate revealed the Bishop visited regularly before sealing the Cathedral — specifically to see the Angle Corrector. After the sealing, the visits stopped abruptly. There seems to have been a falling out between the Bishop and the Angle Corrector.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Verrik the Gardener' }
                        );
                    }
                }
            },

            gardener_bishop_visits: {
                speaker: 'Verrik the Gardener',
                text: `"Oh yes, every week or so. Always very formal — the Bishop and the Angle Corrector behind closed doors. I'd see her leaving with packages sometimes. Small ones, carefully wrapped.\n\nThe Sulkberries, most likely. The spiced ones. The Directorate grows them in special conditions — very particular about who gets the good stock.\n\nBut then one day, the Cathedral sealed up and the Bishop stopped coming. The Angle Corrector started having longer meetings with the council. Something changed."`,
                options: [
                    { text: "I need to speak with the Angle Corrector.", key: 'i_need_to_speak_with_the_angle_corrector', next: "gardener_angle_advice" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ]
            },

            gardener_sulkberries: {
                speaker: 'Verrik the Gardener',
                text: `"Spiced Sulkberries? You've done your research. Those are a Directorate specialty — grown in controlled conditions, spiced with compounds only the cultivation team knows.\n\nThey don't sell them to just anyone. You'd need to talk to the Angle Corrector about who has access to the premium stock. That's cultivation oversight territory.\n\nThird floor, inside. But have a good reason ready — the Angle Corrector doesn't discuss client lists lightly."`,
                options: [
                    { text: "Thanks. I'll head inside.", key: 'thanks_ill_head_inside', next: "closeDialog" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ],
                onTrigger: () => {
                    if (this.questSystem?.getQuest('who_killed_bishop') && !this.questSystem.getQuest('who_killed_bishop').isComplete) {
                        this.questSystem.updateQuest('who_killed_bishop', 'The gardener at the Lumen Directorate confirmed spiced Sulkberries are a controlled commodity. The Angle Corrector on the third floor handles cultivation oversight and would know who has access.', 'gardener_sulkberry_info');
                    }
                }
            },

            // --- Sulkberry verification (Dead End investigation) ---
            gardener_sulkberry_verify: {
                speaker: 'Verrik the Gardener',
                text: `"The Sulkberries? I cultivate them personally — well, the lower-grade stock. The premium spiced batches go through the cultivation team upstairs, but I prepare the soil beds and monitor the early growth stages.\n\nI can tell you this: nothing was wrong with those berries. I'd have noticed contamination in the soil chemistry, in the spore patterns, in the color of the root-tips. A sick Sulkberry plant screams louder than a healthy one whispers.\n\nWhatever happened to the Bishop, it didn't come from our cultivation beds."`,
                options: [
                    ...(this.symbiontSystem?.nemeCanRead() ? [{ text: "[Photosentience] Sense whether Verrik is telling the truth.", key: 'photosentience_sense_whether_verrik_is_telling_the', next: "gardener_sulkberry_neme" }] : []),
                    { text: "You're certain? No contamination at all?", key: 'youre_certain_no_contamination_at_all', next: "gardener_sulkberry_certain" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('sulkberries_cleared_verrik')) {
                        this.addJournalEntry(
                            'sulkberries_cleared_verrik',
                            'Verrik: Sulkberries Were Clean',
                            'Verrik the gardener at the Lumen Directorate personally monitors the early growth stages of the Sulkberry plants. He confirmed there was no contamination in the soil, spore patterns, or root chemistry. Whatever killed the Bishop, it was not the Sulkberries.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Verrik the Gardener' }
                        );
                    }
                    if (this.questSystem?.getQuest('who_killed_bishop') && !this.questSystem.getQuest('who_killed_bishop').isComplete) {
                        this.questSystem.updateQuest('who_killed_bishop', 'Verrik the gardener confirmed the Sulkberries were cultivated properly — no contamination detected. The Directorate poisoning angle weakens.', 'verrik_sulkberry_clear');
                    }
                }
            },

            gardener_sulkberry_neme: {
                speaker: 'Verrik the Gardener',
                text: `You reach inward, letting Neme's tendrils unfurl through your perception. The gardener's bio-signals bloom into focus — earthy calm, professional pride, a faint anxiety about the investigation itself. But no deception. No hidden guilt. No chemical spike of a lie being told.\n\nNeme whispers: "He tends soil for a living. His truth grows like his plants — slowly, honestly, and with dirt under the fingernails."\n\nVerrik is telling the truth. The Sulkberries he cultivated were clean.`,
                options: [
                    { text: "Thank you, Verrik. That's helpful.", key: 'thank_you_verrik_thats_helpful', next: "gardener_start" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('sulkberries_neme_verrik')) {
                        this.addJournalEntry(
                            'sulkberries_neme_verrik',
                            'Neme Confirms: Verrik Is Truthful',
                            'Used Neme\'s Photosentience to verify Verrik\'s claim about the Sulkberries. No deception detected — his bio-signals showed only honest professional certainty. The berries from the Directorate\'s cultivation beds were clean.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Verrik the Gardener' }
                        );
                    }
                }
            },

            gardener_sulkberry_certain: {
                speaker: 'Verrik the Gardener',
                text: `"Certain as roots go down. I've been cultivating Sulkberries for the Directorate for eleven years. I know a contaminated batch the way you know a wrong note in a song you've heard a thousand times.\n\nIf someone wanted to poison the Bishop through the berries, they'd have had to tamper with them after they left our gardens. And the Angle Corrector's people handle transport security — that's not my department.\n\nBut the berries themselves? Clean. I'd stake my garden on it."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ]
            },

            gardener_bishop_vague: {
                speaker: 'Verrik the Gardener',
                text: `"The Bishop's death... yes, that shook things up around here. The Directorate doesn't show it publicly, but there's been a lot of emergency meetings since the news broke.\n\nI don't know the details — I'm just the gardener. But the people inside might. The Angle Corrector especially. If there's anyone who knew the Bishop's business with the Directorate, it's them.\n\nThird floor. Go in, state your business. Just don't expect easy answers."`,
                options: [
                    { text: "Who is the Angle Corrector?", key: 'who_is_the_angle_corrector', next: "gardener_angle_corrector" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ]
            },

            // --- Townhall quest branch ---
            gardener_townhall: {
                speaker: 'Verrik the Gardener',
                text: `"The Townhall? Ha. You and half the city. That place has been locked up tighter than a root-ball in winter.\n\nBut listen — if anyone can get you through those doors, it's Seldo Thrice-Corrected. He works inside, on the second floor. Handles Directorate business that overlaps with the city bureaucracy.\n\nSeldo knows every clerk, every stamp, every back door in this city's administration. If the Townhall can be opened, Seldo knows how."`,
                options: [
                    { text: "Seldo Thrice-Corrected? Unusual name.", key: 'seldo_thricecorrected_unusual_name', next: "gardener_seldo_name" },
                    { text: "Where exactly can I find him?", key: 'where_exactly_can_i_find_him', next: "gardener_seldo_where" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('enter_townhall', 'The gardener Verrik at the Lumen Directorate suggested I speak with Seldo Thrice-Corrected inside. He handles Directorate-city bureaucracy overlap and might know a way into the Townhall.', 'gardener_seldo_tip');
                }
            },

            gardener_seldo_name: {
                speaker: 'Verrik the Gardener',
                text: `"'Thrice-Corrected' means the Directorate reviewed his loyalties three times and found him acceptable each time. It's a mark of trust — or stubbornness, depending who you ask.\n\nSeldo's been with the Directorate longer than I have. He knows where every document goes, which clerk to bribe with Sulkberries, and which doors have locks that respond to a kind word. If the Townhall is your destination, he's your guide."`,
                options: [
                    { text: "Where can I find him inside?", key: 'where_can_i_find_him_inside', next: "gardener_seldo_where" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ]
            },

            gardener_seldo_where: {
                speaker: 'Verrik the Gardener',
                text: `"Second floor, past the reading rooms. You'll know his office by the stacks of paper — the man drowns in forms and permits. Tell him Verrik sent you. And bring patience. Seldo talks in circles sometimes, but he always arrives at the point."`,
                options: [
                    { text: "Thanks. I'll head inside.", key: 'thanks_ill_head_inside', next: "closeDialog" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ]
            },

            // --- Mushroom growing activity ---
            gardener_bloom_talk: {
                speaker: 'Verrik the Gardener',
                text: `Verrik beams, arms spread at the riot of growth around him. "Overflowing is the word! I've never seen the beds like this — the tendrils are three formations ahead of schedule and the walls are practically purring. When the city leans toward growth, this place answers first." He nods at a swollen cluster near the wall. "There's surplus I can't even use. If a bloom's come ripe out there, take it — better in a spore-carrier than left to burst on the vine."`,
                options: [
                    { text: "I'll help myself.", key: 'gardener_bloom_ok', next: "gardener_start" }
                ]
            },
            gardener_blight: {
                speaker: 'Verrik the Gardener',
                text: `Verrik's usual ease is gone. He crouches by a bed of curling, grey-edged shoots. "Sick, aye. The living architecture won't hold its pattern — the walls forget the shape I coaxed them into, the root-tendrils go slack overnight." He looks at you, and there's something wary in it. "It tracks the city. When the balance tips toward rot, the Directorate feels it before anyone. And you..." He decides not to finish. "Keep clear of the young beds, if you would."`,
                options: [
                    { text: "Can it be reversed?", key: 'gardener_blight_reverse', next: "gardener_blight_reverse" },
                    { text: "I'll keep my distance.", key: 'gardener_blight_ok', next: "gardener_start" }
                ]
            },
            gardener_blight_reverse: {
                speaker: 'Verrik the Gardener',
                text: `"Growth cures rot — that's the whole creed. Tip the city back toward the green and the beds will remember themselves. Until then..." He brushes a crumbling leaf from his palm. "I compost what I can't save. Honest work, even when it's grief."`,
                options: [
                    { text: "I understand.", key: 'gardener_blight_understood', next: "gardener_start" }
                ]
            },
            gardener_blight_bed: {
                speaker: 'Narrator',
                text: `A cultivation bed gone wrong: the soil crusted grey, the shoots curled in on themselves like fists. Where a Directorate bed should hum with slow green life, this one only ticks faintly, cooling. Something in the city's balance has reached even here.`,
                options: [{ text: "Step back.", key: 'blight_bed_back', next: "closeDialog" }]
            },
            gardener_cultivar: {
                speaker: 'Verrik the Gardener',
                text: `Verrik's easy manner cools. "...So the Angle Corrector's sending people to me for THAT now." He glances at a sealed cold-frame at the back of the bed. "We grow more than pretty walls here. There's a cultivar we keep behind glass — a controlled rot, bred to eat metal and only metal. 'Nothing Hidden,' they say. Mostly true. Some things we just... shelve."\n\nHe works a key, lifts out a squat, blackish-green bulb weeping faint verdigris, and wraps it in oilcloth. "Grind it into oil and whatever machine drinks it will corrode from the inside out. The Choir's shrine won't sing again." He presses it into your hands. "Don't spill it on anything you'd miss."`,
                options: [
                    { text: "Take the cultivar.", key: 'take_the_cultivar', next: "gardener_start" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('verrik_gave_cultivar')) {
                        this.addItemToInventory({
                            id: 'corrosive_cultivar',
                            name: 'Corrosive Cultivar',
                            description: "A restricted Lumen Directorate plant — a controlled rot bred to devour metal. Ground into oil and fed to a machine, it corrodes it from the inside. Handle with care.",
                            image: 'corrosive_cultivar',
                            stackable: false
                        });
                        this.addJournalEntry(
                            'verrik_gave_cultivar',
                            "The Directorate's Cultivar",
                            "Verrik gave me a restricted Directorate cultivar — a controlled rot bred to eat metal. Ground into oil and fed to the Rust Choir's machines, it will corrode them from within. I should have Ravla work it into the Rust Feast without the Choir noticing.",
                            this.journalSystem.categories.FACTIONS,
                            { character: 'Verrik the Gardener', related: 'Lumen Directorate' }
                        );
                        this.showNotification('Received: Corrosive Cultivar');
                    }
                }
            },

            gardener_work_offer: {
                speaker: 'Verrik the Gardener',
                text: alreadyGrewMushroom
                    ? `"Fancy another round of spore-growing? I always need fresh specimens for the Directorate's living walls. Same deal as before — your spores, my expertise, and whatever the mycelium decides to become.\n\nThe more spores you sacrifice, the more... interesting the results. What do you say?"`
                    : `"Work, eh? Well, I can always use an extra pair of hands — or more precisely, an extra source of spores.\n\nSee, the Directorate's living architecture needs constant feeding. Fresh fungi, new growth. And you — you carry spores, don't you? I can smell them. Everyone in this city does, but yours have a particular... resonance.\n\nHere's the deal: you sacrifice some spores into my cultivation bed, and I guide the growth. Whatever mushroom emerges, I'll buy it from you. The more spores you invest, the rarer the result. Interested?"`,
                options: [
                    ...(canAfford10 ? [{ text: "A small offering — 10 spores.", key: 'a_small_offering_10_spores', next: "gardener_grow_small" }] : []),
                    ...(canAfford25 ? [{ text: "A generous sacrifice — 25 spores.", key: 'a_generous_sacrifice_25_spores', next: "gardener_grow_medium" }] : []),
                    ...(canAfford50 ? [{ text: "Everything I can spare — 50 spores.", key: 'everything_i_can_spare_50_spores', next: "gardener_grow_large" }] : []),
                    ...(!canAfford10 ? [{ text: "I don't have enough spores right now.", key: 'i_dont_have_enough_spores_right_now', next: "gardener_no_spores" }] : []),
                    { text: "Not right now.", key: 'not_right_now', next: "gardener_start" },
                ]
            },

            gardener_no_spores: {
                speaker: 'Verrik the Gardener',
                text: `"No spores? Can't grow much without raw material, friend. Come back when you've gathered some. The city's full of spore sources — just keep your eyes open and your lungs breathing."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ]
            },

            gardener_grow_small: {
                speaker: 'Verrik the Gardener',
                text: `"Ten spores — a modest start. Let's see what your essence produces..."`,
                hideCloseOption: true,
                options: [
                    { text: "[Watch the cultivation bed]", key: 'watch_the_cultivation_bed', next: "gardener_mushroom_result",
                      onSelect: () => {
                        this.modifySpores(-10);
                        this.growMushroom(10, completedQuests, journalEntries, hasThorne, hasNeme, hasUlvarex, growth, decay);
                    }},
                ],
            },

            gardener_grow_medium: {
                speaker: 'Verrik the Gardener',
                text: `"Twenty-five spores — now that's commitment. The mycelium will have plenty to work with..."`,
                hideCloseOption: true,
                options: [
                    { text: "[Watch the cultivation bed]", key: 'watch_the_cultivation_bed', next: "gardener_mushroom_result",
                      onSelect: () => {
                        this.modifySpores(-25);
                        this.growMushroom(25, completedQuests, journalEntries, hasThorne, hasNeme, hasUlvarex, growth, decay);
                    }},
                ],
            },

            gardener_grow_large: {
                speaker: 'Verrik the Gardener',
                text: `"Fifty spores! You're either brave or desperate. Either way — the mycelium will feast. Stand back..."`,
                hideCloseOption: true,
                options: [
                    { text: "[Watch the cultivation bed]", key: 'watch_the_cultivation_bed', next: "gardener_mushroom_result",
                      onSelect: () => {
                        this.modifySpores(-50);
                        this.growMushroom(50, completedQuests, journalEntries, hasThorne, hasNeme, hasUlvarex, growth, decay);
                    }},
                ],
            },

            // --- Mushroom result dialogs (set dynamically by growMushroom) ---
            gardener_mushroom_result: {
                speaker: 'Verrik the Gardener',
                text: this.lastMushroomResult?.text || `"Interesting..."`,
                options: [
                    { text: "What does it mean?", key: 'what_does_it_mean', next: "gardener_mushroom_lore" },
                    { text: "I'll take the payment.", key: 'ill_take_the_payment', next: "gardener_mushroom_pay" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('grew_mushroom_verrik')) {
                        this.addJournalEntry(
                            'grew_mushroom_verrik',
                            'Grew a Mushroom for Verrik',
                            'Sacrificed spores at the Lumen Directorate and grew a mushroom with Verrik the gardener. He pays for each specimen — the rarer the result, the higher the price.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Verrik the Gardener' }
                        );
                    }
                    this.spawnMushroomVisual();
                }
            },

            gardener_mushroom_lore: {
                speaker: 'Verrik the Gardener',
                text: this.lastMushroomResult?.lore || `"Every mushroom tells a story about the one who grew it."`,
                options: [
                    { text: "I'll take the payment.", key: 'ill_take_the_payment', next: "gardener_mushroom_pay" },
                ]
            },

            gardener_mushroom_pay: {
                speaker: 'Verrik the Gardener',
                text: this.lastMushroomResult?.payText || `"Here's your payment."`,
                options: [
                    { text: "Grow another?", key: 'grow_another', next: "gardener_work_offer" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "gardener_start" },
                ],
                onTrigger: () => {
                    if (this.lastMushroomResult?.payment) {
                        this.addMoney(this.lastMushroomResult.payment, true);
                        this.modifyFactionReputation('LumenDirectorate', this.lastMushroomResult.repBonus || 0);
                        if (this.lastMushroomResult.growthEffect) {
                            this.growthDecaySystem?.modifyBalance(this.lastMushroomResult.growthEffect, 0);
                        }
                    }
                }
            },
        };
    }

    /**
     * Spawn a visual mushroom in the garden with a growing animation.
     */
    spawnMushroomVisual() {
        if (!this.lastMushroomResult) return;

        // Color name → hex mapping
        const colorMap = {
            'rust-veined': 0xB7410E, 'ashen grey': 0x8A8A8A, 'bruise-purple': 0x6B3FA0,
            'corroded bronze': 0x8B6914, 'vivid emerald': 0x50C878, 'sun-gold': 0xFFD700,
            'bright coral': 0xFF6F61, 'phosphor white': 0xE8F5E9, 'shifting opalescent': 0xC4A7E7,
            'translucent silver': 0xC0C0C0, 'mirage-pink': 0xFF69B4, 'chrome-rainbow': 0x88DDFF,
            'deep green': 0x1B5E20, 'amber': 0xFFBF00, 'forest brown': 0x5D4037,
            'moss-spotted': 0x6B8E23, 'pale grey': 0xBDBDBD, 'soot-black': 0x2E2E2E,
            'iron red': 0x8B0000, 'dust-yellow': 0xD4C36A, 'dull olive': 0x808000,
            'speckled tan': 0xD2B48C, 'faded blue': 0x7B9DB7, 'clay orange': 0xCC7722,
        };

        // Extract the color word(s) from the name (name = "color shape")
        const name = this.lastMushroomResult.name || '';
        let capColor = 0x7fff8e; // default green
        for (const [colorName, hex] of Object.entries(colorMap)) {
            if (name.startsWith(colorName)) {
                capColor = hex;
                break;
            }
        }

        // Rarity affects size
        const rarity = this.lastMushroomResult.rarity || 'Mundane';
        const sizeScale = rarity === 'Exceptional' ? 1.4 : rarity === 'Remarkable' ? 1.15 : rarity === 'Decent' ? 0.9 : 0.7;

        // Pick a garden position — scatter in the flower beds
        const gardenSpots = [
            { x: 120, y: 490 }, { x: 170, y: 500 }, { x: 90, y: 510 },
            { x: 640, y: 490 }, { x: 690, y: 500 }, { x: 720, y: 510 },
            { x: 300, y: 510 }, { x: 500, y: 510 },
            { x: 150, y: 475 }, { x: 660, y: 475 },
        ];
        if (!this.gardenMushroomIndex) this.gardenMushroomIndex = 0;
        const spot = gardenSpots[this.gardenMushroomIndex % gardenSpots.length];
        this.gardenMushroomIndex++;

        // Offset slightly so repeat grows don't overlap exactly
        const jitterX = Phaser.Math.Between(-8, 8);
        const jitterY = Phaser.Math.Between(-4, 4);
        const px = spot.x + jitterX;
        const py = spot.y + jitterY;

        // Stem color — darker version of cap
        const stemColor = Phaser.Display.Color.ValueToColor(capColor);
        const stemHex = Phaser.Display.Color.GetColor(
            Math.max(0, stemColor.red - 40),
            Math.max(0, stemColor.green - 40),
            Math.max(0, stemColor.blue - 40)
        );

        // Draw the mushroom
        const mushroom = this.add.container(px, py);
        mushroom.setDepth(6);

        const capW = 18 * sizeScale;
        const capH = 10 * sizeScale;
        const stemW = 4 * sizeScale;
        const stemH = 12 * sizeScale;

        // Stem
        const stem = this.add.graphics();
        stem.fillStyle(stemHex, 1);
        stem.fillRect(-stemW / 2, -stemH, stemW, stemH);
        mushroom.add(stem);

        // Cap
        const cap = this.add.graphics();
        cap.fillStyle(capColor, 1);
        cap.fillEllipse(0, -stemH, capW, capH);
        mushroom.add(cap);

        // Spots for higher rarity
        if (rarity === 'Remarkable' || rarity === 'Exceptional') {
            const spots = this.add.graphics();
            spots.fillStyle(0xffffff, 0.5);
            spots.fillCircle(-capW * 0.2, -stemH - capH * 0.1, 1.5 * sizeScale);
            spots.fillCircle(capW * 0.15, -stemH + capH * 0.05, 1 * sizeScale);
            if (rarity === 'Exceptional') {
                spots.fillCircle(0, -stemH - capH * 0.2, 1.2 * sizeScale);
            }
            mushroom.add(spots);
        }

        // Glow for exceptional
        if (rarity === 'Exceptional') {
            const glow = this.add.graphics();
            glow.fillStyle(capColor, 0.2);
            glow.fillCircle(0, -stemH, capW * 0.9);
            mushroom.addAt(glow, 0); // behind stem

            this.tweens.add({
                targets: glow,
                alpha: { from: 0.2, to: 0.05 },
                duration: 1500,
                yoyo: true,
                repeat: -1
            });
        }

        // Growing animation — scale from 0 to full
        mushroom.setScale(0);
        this.tweens.add({
            targets: mushroom,
            scaleX: 1,
            scaleY: 1,
            duration: 800,
            ease: 'Back.easeOut',
            delay: 200
        });

        // Gentle idle sway after growing
        this.time.delayedCall(1100, () => {
            this.tweens.add({
                targets: mushroom,
                angle: { from: -2, to: 2 },
                duration: 2000 + Phaser.Math.Between(0, 500),
                ease: 'Sine.easeInOut',
                yoyo: true,
                repeat: -1
            });
        });
    }

    /**
     * Determine mushroom outcome based on spore investment, game history, symbionts, and randomness.
     * Returns a dialog state key to navigate to.
     */
    growMushroom(sporeAmount, completedQuests, journalEntries, hasThorne, hasNeme, hasUlvarex, growth, decay) {
        // --- Scoring system ---
        // History score: how much the player has explored the world
        const questScore = Math.min(completedQuests.length * 5, 30); // 0-30
        const journalScore = Math.min(journalEntries.length * 2, 20); // 0-20
        const historyScore = questScore + journalScore; // 0-50

        // Symbiont influence
        let symbiontInfluence = 'none';
        if (hasThorne) symbiontInfluence = 'decay';
        if (hasNeme) symbiontInfluence = 'growth';
        if (hasUlvarex) symbiontInfluence = 'illusion';
        // Multiple symbionts: last one wins for primary, but we track all
        const symbiontCount = [hasThorne, hasNeme, hasUlvarex].filter(Boolean).length;

        // Investment tier
        const investmentTier = sporeAmount >= 50 ? 3 : sporeAmount >= 25 ? 2 : 1;

        // Random factor (0-100)
        const luck = Phaser.Math.Between(0, 100);

        // Total quality score (0-200 range)
        const qualityScore = historyScore + (investmentTier * 20) + (symbiontCount * 10) + luck;

        // --- Determine mushroom properties ---
        const mushroom = this.determineMushroom(qualityScore, investmentTier, symbiontInfluence, growth, decay, completedQuests, journalEntries);

        // Store result for dialog access
        this.lastMushroomResult = mushroom;

        return 'gardener_mushroom_result';
    }

    determineMushroom(score, tier, symbiontInfluence, growth, decay, completedQuests, journalEntries) {
        // --- Colour palette based on growth/decay balance and symbionts ---
        let colorPool;
        if (symbiontInfluence === 'decay') {
            colorPool = ['rust-veined', 'ashen grey', 'bruise-purple', 'corroded bronze'];
        } else if (symbiontInfluence === 'growth') {
            colorPool = ['vivid emerald', 'sun-gold', 'bright coral', 'phosphor white'];
        } else if (symbiontInfluence === 'illusion') {
            colorPool = ['shifting opalescent', 'translucent silver', 'mirage-pink', 'chrome-rainbow'];
        } else if (growth > 70) {
            colorPool = ['deep green', 'amber', 'forest brown', 'moss-spotted'];
        } else if (decay > 70) {
            colorPool = ['pale grey', 'soot-black', 'iron red', 'dust-yellow'];
        } else {
            colorPool = ['dull olive', 'speckled tan', 'faded blue', 'clay orange'];
        }
        const color = colorPool[Phaser.Math.Between(0, colorPool.length - 1)];

        // --- Shape based on quest history ---
        let shapePool;
        const hasRustHistory = completedQuests.some(q => q.id === 'rust_feast' || q.id === 'find_rust_choir');
        const hasBureaucracy = completedQuests.some(q => q.id === 'ortolan_arms' || q.id === 'excavation_permit');
        const hasBishopHistory = completedQuests.some(q => q.id === 'find_bishop' || q.id === 'who_killed_bishop');

        if (hasRustHistory && hasBishopHistory) {
            shapePool = ['spiralling helix', 'cathedral spire', 'branching coral', 'nested rings'];
        } else if (hasRustHistory) {
            shapePool = ['jagged crown', 'gear-toothed cap', 'industrial honeycomb', 'rusted bell'];
        } else if (hasBureaucracy) {
            shapePool = ['perfectly symmetrical dome', 'stacked disc', 'rolled scroll', 'stamped cylinder'];
        } else if (hasBishopHistory) {
            shapePool = ['weeping candle', 'cracked egg shell', 'hollow bell', 'drooping veil'];
        } else {
            shapePool = ['lumpy bulb', 'flat shelf', 'stubby button', 'crooked stem'];
        }
        const shape = shapePool[Phaser.Math.Between(0, shapePool.length - 1)];

        // --- Special traits (random + journal-influenced) ---
        const traits = [];
        const hasVisitedShed = journalEntries.some(e => e.id?.includes('shed') || e.content?.includes('Shed'));
        const hasVisitedHarbor = journalEntries.some(e => e.id?.includes('harbor') || e.content?.includes('harbor') || e.content?.includes('Harbor'));
        const hasMetElphi = journalEntries.some(e => e.id?.includes('elphi'));

        if (hasVisitedShed && Phaser.Math.Between(0, 1)) traits.push('faintly hums when touched');
        if (hasVisitedHarbor && Phaser.Math.Between(0, 1)) traits.push('smells of salt and deep water');
        if (hasMetElphi && Phaser.Math.Between(0, 1)) traits.push('leaks a thin dream-vapour');
        if (symbiontInfluence === 'illusion') traits.push('flickers between two shapes');
        if (symbiontInfluence === 'decay') traits.push('crumbles slightly at the edges');
        if (symbiontInfluence === 'growth') traits.push('pulses with a faint heartbeat');
        if (decay > 80) traits.push('already starting to decompose beautifully');
        if (growth > 80) traits.push('sprouting tiny secondary caps');

        // Ensure at least one trait
        if (traits.length === 0) {
            const defaultTraits = ['slightly warm to the touch', 'gives off a faint glow', 'perfectly ordinary-looking', 'wobbles gently on its stem'];
            traits.push(defaultTraits[Phaser.Math.Between(0, defaultTraits.length - 1)]);
        }

        // --- Rarity and payment ---
        let rarity, payment, repBonus, growthEffect;
        if (score >= 160) {
            rarity = 'Exceptional';
            payment = 30 + Phaser.Math.Between(0, 20);
            repBonus = 5;
            growthEffect = 3;
        } else if (score >= 120) {
            rarity = 'Remarkable';
            payment = 18 + Phaser.Math.Between(0, 12);
            repBonus = 3;
            growthEffect = 2;
        } else if (score >= 80) {
            rarity = 'Decent';
            payment = 8 + Phaser.Math.Between(0, 7);
            repBonus = 1;
            growthEffect = 1;
        } else {
            rarity = 'Mundane';
            payment = 3 + Phaser.Math.Between(0, 4);
            repBonus = 0;
            growthEffect = 0;
        }

        // Tier bonus
        payment += (tier - 1) * 5;
        // Decay-aligned bodies grow richer mushrooms — mirror of the Growth boost on Oltrac sales.
        // Boost only above 50 (no penalty below).
        payment = Math.round(payment * (1 + Math.max(0, (decay - 50) / 100)));
        // Directorate Clearance perk: members get a standing cultivation bonus.
        if (this.isLumenMember && this.isLumenMember()) {
            payment = Math.round(payment * 1.25);
        }

        const traitText = traits.length > 1
            ? traits.slice(0, -1).join(', ') + ' and ' + traits[traits.length - 1]
            : traits[0];

        const name = `${color} ${shape}`;

        // --- Build result texts ---
        const text = rarity === 'Exceptional'
            ? `"By the roots... look at that. A ${name}. ${rarity} quality. It ${traitText}.\n\nI've been cultivating for twenty years and I've seen maybe a handful like this. Your spores carry something special — the city has marked you, and the mycelium knows it."`
            : rarity === 'Remarkable'
                ? `"Well now. A ${name}. That's ${rarity.toLowerCase()} work. It ${traitText}.\n\nThe Directorate will want this one for the upper corridors. Your history in this city shows in the growth — the mycelium reads you like a journal."`
                : rarity === 'Decent'
                    ? `"A ${name}. ${rarity} specimen. It ${traitText}.\n\nNothing to write treatises about, but solid. The living walls always need feeding. You've got potential — come back with more spores and more stories, and the results will improve."`
                    : `"A ${name}. ${rarity}, I'm afraid. It ${traitText}.\n\nDon't take it personally — the mycelium is finicky. It responds to experience, to the weight of what you've done in this city. Keep exploring, keep living, and your spores will carry more... narrative."`;

        const lore = symbiontInfluence !== 'none'
            ? `"See how it ${traits[0]}? That's your symbiont's influence bleeding through. The creature living inside you — its essence mingles with your spores. Every mushroom you grow will carry its signature.\n\n${symbiontInfluence === 'decay' ? 'Decay-touched fungi are prized for their resilience. They feed the walls that face the worst weather.' : symbiontInfluence === 'growth' ? 'Growth-blessed specimens are the Directorate\'s favourite. Pure vitality in fungal form.' : 'Illusion-marked fungi are rare and deeply unsettling. The Directorate\'s researchers will pay well for those.'}"`
            : growth > 65
                ? `"Your spores lean toward growth — the mushroom reflects that. The Directorate values specimens grown from growth-aligned essence. They integrate better with the living architecture.\n\nKeep tending toward growth, and your harvests will only improve."`
                : decay > 65
                    ? `"There's a decay signature in this one. Not a bad thing — decay fungi have their own beauty. They break down what needs breaking, make room for what comes next.\n\nThe Rust Choir would love these, but the Directorate has uses for them too. Composting old walls, recycling dead architecture."`
                    : `"A balanced specimen. Neither strongly growth nor decay. The Directorate calls these 'neutral cultivars' — versatile, if unremarkable.\n\nIf you want more distinctive results, lean into one direction. Growth or decay — both produce more interesting fungi."`;

        const payText = `"Here's ${payment} gold for the ${name}. ${rarity === 'Exceptional' ? 'And a tip for the quality — the Directorate remembers generosity.' : rarity === 'Remarkable' ? 'Good work. The upper floors will appreciate this one.' : 'Fair pay for fair work. Come back anytime.'}"`;

        return { text, lore, payText, payment, repBonus, growthEffect, rarity, name };
    }

    update() {
        super.update();
    }
}

if (typeof window !== 'undefined') {
    window.LumenDirectorateScene = LumenDirectorateScene;
}

export { LumenDirectorateScene };
