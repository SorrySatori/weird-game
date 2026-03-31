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
        const knowsSulkberries = !!this.hasJournalEntry('elphi_berries_analysis');
        const knowsLumenLead = !!this.hasJournalEntry('elphi_lumen_lead');
        const alreadyMetGardener = !!this.hasJournalEntry('met_gardener_verrik');
        const alreadyGrewMushroom = !!this.hasJournalEntry('grew_mushroom_verrik');

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
                text: alreadyMetGardener
                    ? `"Back again? The hedges don't trim themselves, but I can spare a moment."`
                    : `"Careful where you step — those root-tendrils took me three weeks to coax into spiral formation. Name's Verrik. I tend the living architecture here at the Directorate."`,
                options: [
                    { text: "What is this place?", next: "gardener_about_lumen" },
                    ...(hasLumenQuest ? [{ text: "I was told to come here — about joining the crew.", next: "gardener_join" }] : []),
                    ...(hasEnterTownhallQuest ? [{ text: "I need to get into the Townhall. Any ideas?", next: "gardener_townhall" }] : []),
                    ...(knowsLumenLead ? [{ text: "I need to speak with someone about Cathedral oversight.", next: "gardener_bishop_lead" }] : []),
                    ...(knowsSulkberries && !knowsLumenLead ? [{ text: "I'm looking into spiced Sulkberries. Who supplies them?", next: "gardener_sulkberries" }] : []),
                    ...(hasBishopQuest && !knowsLumenLead && !knowsSulkberries ? [{ text: "I'm investigating the Bishop's death.", next: "gardener_bishop_vague" }] : []),
                    { text: "Looking for work. Anything I can help with?", next: "gardener_work_offer" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('met_gardener_verrik')) {
                        this.addJournalEntry(
                            'met_gardener_verrik',
                            'Met Verrik the Gardener',
                            'Met a gardener named Verrik outside the Lumen Directorate headquarters. He tends the living architecture around the building.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Verrik the Gardener' }
                        );
                    }
                }
            },

            gardener_about_lumen: {
                speaker: 'Verrik the Gardener',
                text: `"The Lumen Directorate. Keepers and protectors of everything that grows. That's the motto — well, the unofficial one. The official motto is 'Nothing Hidden. Nothing Lost.'\n\nThey run this city, more or less. Won the Board Games War, rebuilt half the districts, and now they make sure the green keeps spreading. Growth is everything to them — plants, fungi, ideas, influence. Especially influence."`,
                options: [
                    { text: "What do you do for them?", next: "gardener_role" },
                    { text: "Who's in charge here?", next: "gardener_leadership" },
                    { text: "I have other questions.", next: "gardener_start" },
                ]
            },

            gardener_role: {
                speaker: 'Verrik the Gardener',
                text: `"I cultivate. The walls, the walkways, the hedges — it's all alive, you know. The Directorate doesn't believe in dead architecture. Every surface should breathe, should grow.\n\nI'm low on the vine, so to speak. But I hear things. Plants are good listeners, and so am I."`,
                options: [
                    { text: "What kind of things do you hear?", next: "gardener_rumors" },
                    { text: "I have other questions.", next: "gardener_start" },
                ]
            },

            gardener_rumors: {
                speaker: 'Verrik the Gardener',
                text: `"Oh, this and that. The Directorate's been restless lately. Something about the Egg Cathedral being sealed — that's got them worried. They've had their eye on that place for years, waiting for the hatching.\n\nAnd there's been more traffic inside than usual. People going up to see the Angle Corrector. That's never a casual visit."`,
                options: [
                    { text: "Who is the Angle Corrector?", next: "gardener_angle_corrector" },
                    { text: "They're worried about the Cathedral?", next: "gardener_cathedral" },
                    { text: "I have other questions.", next: "gardener_start" },
                ]
            },

            gardener_angle_corrector: {
                speaker: 'Verrik the Gardener',
                text: `"The Angle Corrector? That's... well, title and name all in one. Nobody knows their real name, or if they even have one. They handle the Directorate's more delicate affairs — cultivation oversight, Cathedral liaison, that sort of thing.\n\nIf you need answers about anything the Directorate touches, the Angle Corrector is who you want. Third floor, through the atrium. But they don't see just anyone. You'll need a reason."`,
                options: [
                    ...(hasLumenQuest ? [{ text: "Captain Liris sent me. That's my reason.", next: "gardener_join_angle" }] : []),
                    ...(knowsLumenLead ? [{ text: "I'm here about the Bishop's dealings with the Directorate.", next: "gardener_bishop_lead" }] : []),
                    { text: "I'll figure something out.", next: "gardener_angle_advice" },
                    { text: "I have other questions.", next: "gardener_start" },
                ]
            },

            gardener_angle_advice: {
                speaker: 'Verrik the Gardener',
                text: `"A word of advice — the Directorate values transparency, or at least the appearance of it. Don't try to be clever. State your business plainly. They respect directness.\n\nAnd don't touch the ferns in the atrium. They bite."`,
                options: [
                    { text: "I have other questions.", next: "gardener_start" },
                ]
            },

            gardener_cathedral: {
                speaker: 'Verrik the Gardener',
                text: `"The Egg Cathedral is the biggest growth event this city has seen in decades. Whatever's growing inside those eggs — the Directorate wants to be there when it hatches. They've been monitoring it, cataloguing every vibration.\n\nWhen the Bishop sealed the Cathedral... let's just say the mood around here got very tense. The Directorate doesn't like locked doors. 'Nothing Hidden,' remember?"`,
                options: [
                    { text: "Who is the Angle Corrector?", next: "gardener_angle_corrector" },
                    { text: "I have other questions.", next: "gardener_start" },
                ]
            },

            gardener_leadership: {
                speaker: 'Verrik the Gardener',
                text: `"The Directorate isn't run by one person — it's a council. But the one you'll hear about most is the Angle Corrector. They handle the day-to-day, the sensitive matters, the things that need a... particular touch.\n\nCaptain Liris runs the skyship operations — the Verdigrace and its crew. She's Directorate through and through, but she's usually up in the clouds."`,
                options: [
                    { text: "Who is the Angle Corrector?", next: "gardener_angle_corrector" },
                    { text: "I have other questions.", next: "gardener_start" },
                ]
            },

            gardener_join: {
                speaker: 'Verrik the Gardener',
                text: `"Joining up, eh? Captain Liris sent you? She's always looking for promising recruits. The Directorate values dedication to growth — in all its forms.\n\nYou'll want to speak with the Angle Corrector inside. Third floor, through the atrium. Tell them Liris sent you. That should get you through the door, at least."`,
                options: [
                    { text: "What should I expect?", next: "gardener_join_expect" },
                    { text: "Thanks. I'll head inside.", next: "closeDialog" },
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('find_lumen_directorate', 'The gardener Verrik directed me to speak with the Angle Corrector on the third floor of the Directorate. Captain Liris\'s name should get me through the door.', 'gardener_directions');
                }
            },

            gardener_join_angle: {
                speaker: 'Verrik the Gardener',
                text: `"Liris's name carries weight around here. Mention her, and the Angle Corrector will see you. Third floor. Don't dawdle in the atrium — it's beautiful, but it's also the Directorate's way of watching who comes and goes."`,
                options: [
                    { text: "Thanks for the tip.", next: "gardener_start" },
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
                    { text: "I'll keep that in mind.", next: "gardener_start" },
                ]
            },

            gardener_bishop_lead: {
                speaker: 'Verrik the Gardener',
                text: `"The Bishop's dealings? That's above my pay grade, friend. But I can tell you this — the Bishop was a regular visitor here before she sealed the Cathedral. Came to see the Angle Corrector personally.\n\nAfter the sealing... the visits stopped. And the Angle Corrector's mood went from bad to worse. Something happened between them.\n\nYou'll want to go inside and ask directly. Third floor. Be respectful — and honest. The Directorate can smell a lie faster than my ferns can smell rain."`,
                options: [
                    { text: "The Bishop visited regularly?", next: "gardener_bishop_visits" },
                    { text: "Thanks. I'll head inside.", next: "closeDialog" },
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
                    { text: "I need to speak with the Angle Corrector.", next: "gardener_angle_advice" },
                    { text: "I have other questions.", next: "gardener_start" },
                ]
            },

            gardener_sulkberries: {
                speaker: 'Verrik the Gardener',
                text: `"Spiced Sulkberries? You've done your research. Those are a Directorate specialty — grown in controlled conditions, spiced with compounds only the cultivation team knows.\n\nThey don't sell them to just anyone. You'd need to talk to the Angle Corrector about who has access to the premium stock. That's cultivation oversight territory.\n\nThird floor, inside. But have a good reason ready — the Angle Corrector doesn't discuss client lists lightly."`,
                options: [
                    { text: "Thanks. I'll head inside.", next: "closeDialog" },
                    { text: "I have other questions.", next: "gardener_start" },
                ],
                onTrigger: () => {
                    if (this.questSystem?.getQuest('who_killed_bishop') && !this.questSystem.getQuest('who_killed_bishop').isComplete) {
                        this.questSystem.updateQuest('who_killed_bishop', 'The gardener at the Lumen Directorate confirmed spiced Sulkberries are a controlled commodity. The Angle Corrector on the third floor handles cultivation oversight and would know who has access.', 'gardener_sulkberry_info');
                    }
                }
            },

            gardener_bishop_vague: {
                speaker: 'Verrik the Gardener',
                text: `"The Bishop's death... yes, that shook things up around here. The Directorate doesn't show it publicly, but there's been a lot of emergency meetings since the news broke.\n\nI don't know the details — I'm just the gardener. But the people inside might. The Angle Corrector especially. If there's anyone who knew the Bishop's business with the Directorate, it's them.\n\nThird floor. Go in, state your business. Just don't expect easy answers."`,
                options: [
                    { text: "Who is the Angle Corrector?", next: "gardener_angle_corrector" },
                    { text: "I have other questions.", next: "gardener_start" },
                ]
            },

            // --- Townhall quest branch ---
            gardener_townhall: {
                speaker: 'Verrik the Gardener',
                text: `"The Townhall? Ha. You and half the city. That place has been locked up tighter than a root-ball in winter.\n\nBut listen — if anyone can get you through those doors, it's Seldo Thrice-Corrected. He works inside, on the second floor. Handles Directorate business that overlaps with the city bureaucracy.\n\nSeldo knows every clerk, every stamp, every back door in this city's administration. If the Townhall can be opened, Seldo knows how."`,
                options: [
                    { text: "Seldo Thrice-Corrected? Unusual name.", next: "gardener_seldo_name" },
                    { text: "Where exactly can I find him?", next: "gardener_seldo_where" },
                    { text: "I have other questions.", next: "gardener_start" },
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('enter_townhall', 'The gardener Verrik at the Lumen Directorate suggested I speak with Seldo Thrice-Corrected inside. He handles Directorate-city bureaucracy overlap and might know a way into the Townhall.', 'gardener_seldo_tip');
                }
            },

            gardener_seldo_name: {
                speaker: 'Verrik the Gardener',
                text: `"'Thrice-Corrected' means the Directorate reviewed his loyalties three times and found him acceptable each time. It's a mark of trust — or stubbornness, depending who you ask.\n\nSeldo's been with the Directorate longer than I have. He knows where every document goes, which clerk to bribe with Sulkberries, and which doors have locks that respond to a kind word. If the Townhall is your destination, he's your guide."`,
                options: [
                    { text: "Where can I find him inside?", next: "gardener_seldo_where" },
                    { text: "I have other questions.", next: "gardener_start" },
                ]
            },

            gardener_seldo_where: {
                speaker: 'Verrik the Gardener',
                text: `"Second floor, past the reading rooms. You'll know his office by the stacks of paper — the man drowns in forms and permits. Tell him Verrik sent you. And bring patience. Seldo talks in circles sometimes, but he always arrives at the point."`,
                options: [
                    { text: "Thanks. I'll head inside.", next: "closeDialog" },
                    { text: "I have other questions.", next: "gardener_start" },
                ]
            },

            // --- Mushroom growing activity ---
            gardener_work_offer: {
                speaker: 'Verrik the Gardener',
                text: alreadyGrewMushroom
                    ? `"Fancy another round of spore-growing? I always need fresh specimens for the Directorate's living walls. Same deal as before — your spores, my expertise, and whatever the mycelium decides to become.\n\nThe more spores you sacrifice, the more... interesting the results. What do you say?"`
                    : `"Work, eh? Well, I can always use an extra pair of hands — or more precisely, an extra source of spores.\n\nSee, the Directorate's living architecture needs constant feeding. Fresh fungi, new growth. And you — you carry spores, don't you? I can smell them. Everyone in this city does, but yours have a particular... resonance.\n\nHere's the deal: you sacrifice some spores into my cultivation bed, and I guide the growth. Whatever mushroom emerges, I'll buy it from you. The more spores you invest, the rarer the result. Interested?"`,
                options: [
                    ...(canAfford10 ? [{ text: "A small offering — 10 spores.", next: "gardener_grow_small" }] : []),
                    ...(canAfford25 ? [{ text: "A generous sacrifice — 25 spores.", next: "gardener_grow_medium" }] : []),
                    ...(canAfford50 ? [{ text: "Everything I can spare — 50 spores.", next: "gardener_grow_large" }] : []),
                    ...(!canAfford10 ? [{ text: "I don't have enough spores right now.", next: "gardener_no_spores" }] : []),
                    { text: "Not right now.", next: "gardener_start" },
                ]
            },

            gardener_no_spores: {
                speaker: 'Verrik the Gardener',
                text: `"No spores? Can't grow much without raw material, friend. Come back when you've gathered some. The city's full of spore sources — just keep your eyes open and your lungs breathing."`,
                options: [
                    { text: "I have other questions.", next: "gardener_start" },
                ]
            },

            gardener_grow_small: {
                speaker: 'Verrik the Gardener',
                text: `"Ten spores — a modest start. Let's see what your essence produces..."`,
                hideCloseOption: true,
                options: [
                    { text: "[Watch the cultivation bed]", next: "gardener_mushroom_result",
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
                    { text: "[Watch the cultivation bed]", next: "gardener_mushroom_result",
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
                    { text: "[Watch the cultivation bed]", next: "gardener_mushroom_result",
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
                    { text: "What does it mean?", next: "gardener_mushroom_lore" },
                    { text: "I'll take the payment.", next: "gardener_mushroom_pay" },
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
                    { text: "I'll take the payment.", next: "gardener_mushroom_pay" },
                ]
            },

            gardener_mushroom_pay: {
                speaker: 'Verrik the Gardener',
                text: this.lastMushroomResult?.payText || `"Here's your payment."`,
                options: [
                    { text: "Grow another?", next: "gardener_work_offer" },
                    { text: "I have other questions.", next: "gardener_start" },
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
