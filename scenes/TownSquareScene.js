import GameScene from './GameScene.js'
import SceneTransitionManager from '../utils/SceneTransitionManager.js'
import { createStreetLamp, meetLamp, lampsFoundCount, GANG_QUEST_IDS, gangQuestStatus, eavesdropReportable } from '../utils/GangOfLamps.js'

export default class TownSquareScene extends GameScene {
    constructor() {
        super({ key: 'TownSquareScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        const chandelierMet = !!this.hasJournalEntry('met_lamp_chandelier');
        // At first meeting `found` counts the OTHER lamps already met (0–3); on a return
        // visit it includes Chandelier herself. Drives the progress-aware greeting.
        const found = lampsFoundCount(this);
        const allLampsFound = found === 4;

        // --- L2: Chandelier's eavesdrop quest ---
        const eavesdropStatus = gangQuestStatus(this, GANG_QUEST_IDS.chandelier);
        const chandelierConnectedOptions = [
            ...(eavesdropStatus === 'none'
                ? [{ text: "You said you'd make it worth my while. Go on, then.", key: 'chandelier_eavesdrop_offer', next: "chandelier_eavesdrop_brief" }]
                : []),
            ...(eavesdropStatus === 'active' && eavesdropReportable(this)
                ? [{ text: "I heard something you'll adore.", key: 'chandelier_eavesdrop_deliver', next: "chandelier_eavesdrop_report" }]
                : []),
            ...(eavesdropStatus === 'active' && !eavesdropReportable(this)
                ? [{ text: "Where was I listening again?", key: 'chandelier_eavesdrop_status', next: "chandelier_eavesdrop_statusinfo" }]
                : []),
            { text: "Enjoy the quiet, Chandelier.", key: 'chandelier_connected_close', next: "closeDialog" },
        ];
        return {
            ...super.dialogContent,
            ...this._magnekinDialogContent,
            ...this._buskerDialogContent,

            // ===== Gang of Lamps: Chandelier (aloof, gossipy socialite) — set on an ornate post in the square =====
            chandelier_lamp_start: {
                speaker: 'Chandelier',
                textKey: chandelierMet
                    ? (allLampsFound ? 'chandelier_lamp_connected' : 'chandelier_lamp_searching')
                    : (found === 3 ? 'chandelier_lamp_first_last' : found >= 1 ? 'chandelier_lamp_first_some' : 'chandelier_lamp_first'),
                text: !chandelierMet
                    ? (found === 3
                        ? `What you took for an ornate street-lamp is a full crystal chandelier atop an iron post — and every lustre is already trembling with excitement as you approach. "*You.* Oh, you clever, clever thing — I can hear the whole rest of the family singing down the wire behind you. Every one of them found but *me*." A cascade of delighted chiming. "Then I am the last, and you have come to make us whole. Do you know how long I have waited to be the final piece of *anything*? Thread me in, darling. Thread me in at once."`
                        : found >= 1
                            ? `What you took for an ornate street-lamp is a full crystal chandelier atop an iron post, lustres already turning toward you with a knowing little shimmer. "Mm — a new face, and one that *smells* of my scattered kin. You've been carrying word between the others, haven't you? I can feel it on the wire." A pleased, tinkling sigh. "I am Chandelier, darling — one of the lamps who talk and cannot move an inch. You've made a lovely start. Do bring the rest of us into the conversation."`
                            : `What you took for an ornate street-lamp in the square is a full crystal chandelier, mounted atop an iron post and tilting its lustres toward you with a delicate, tinkling sigh. "Mm. A *new* face. How refreshing — the passers-by stopped being interesting years ago." The prisms turn, catching you from a dozen angles at once. "I am Chandelier, darling. Yes, I talk; yes, I am one of *them* — the scattered lot, the lamps who cannot so much as sway from their fixtures to gossip properly. It is *agony*, being this well-informed and this immobile. One hears simply everything from a square like this, and has no one to tell it to.\n\nYou, though. You *move*. Be a dear and carry word between us? I shall make it worth your while — I know things, and I do so love to share."`)
                    : (allLampsFound
                        ? `Every lustre blazes at once, delighted. "There. All of us threaded back together — I can *hear* them again, the whole circuit humming with gossip. You marvellous little errand-light." A satisfied chime rings through the crystal. "Sit. Bask. There will be favors to ask soon enough — there always are — but for now, simply let me admire the one who reconnected us."`
                        : `The prisms give an impatient little shiver. "Still scattered, darling. Still waiting. Do hurry — the *Don* up on the high walkway under Scraper 1140, the nervy little sconce by the house of stamps, the torch rusting by the water. A courier who dawdles is no courier at all."`),
                options: !chandelierMet
                    ? (found === 3
                        ? [
                            { text: "You're the last one, Chandelier. That's all four.", key: 'chandelier_last_close', next: "closeDialog" }
                        ]
                        : [
                            { text: "Who else is out there?", key: 'chandelier_who', next: "chandelier_lamp_family" },
                            { text: "A gossiping chandelier. Of course.", key: 'chandelier_leave', next: "closeDialog" }
                        ])
                    : (allLampsFound
                        ? chandelierConnectedOptions
                        : [
                            { text: "Remind me where to look.", key: 'chandelier_remind', next: "chandelier_lamp_family" },
                            { text: "I'll keep looking.", key: 'chandelier_searching_close', next: "closeDialog" }
                        ]),
                onTrigger: () => { meetLamp(this, 'chandelier', 'Chandelier'); }
            },
            chandelier_lamp_family: {
                speaker: 'Chandelier',
                text: `"Who else is out there? There is an old fright of a lamppost who fancies himself a *Don* — perched up on the high walkway under Scraper 1140, all grease and grandeur; do mind your manners with that one. There is a twitchy little *sconce* pinned to a wall in the house of stamps, watching the clerks drown the world in forms — poor nervous thing. And there is a *torchère*, all soot and temper, rusting down by the water among the crates. Find them, won't you? And do report back. I *adore* a returning source."`,
                options: [
                    { text: "I'll bring you their words.", key: 'chandelier_family_close', next: "closeDialog" }
                ]
            },

            // ===== L2: Chandelier's quest — "A Choice Morsel" (eavesdrop) =====
            chandelier_eavesdrop_brief: {
                speaker: 'Chandelier',
                text: `Every lustre leans in, positively glittering. "Now. There is a house that *hoards* its secrets, darling, and it drives me to distraction — the Lumen Directorate, with their pruned little garden and their 'nothing hidden, nothing lost.' *Ha.* They hide plenty; they simply file it prettily." A conspiratorial chime. "Go and *linger* by their garden. There's a spot where the vents carry every word from inside. Stand there, let it wash over you, and bring me back something juicy — a name, a fear, a quiet little betrayal. I shall dine on it for weeks."`,
                options: [
                    { text: "Eavesdrop on the Lumen Directorate. Delicious.", key: 'chandelier_eavesdrop_accept', next: "closeDialog" }
                ],
                onTrigger: () => {
                    if (!this.questSystem?.getQuest(GANG_QUEST_IDS.chandelier)) {
                        this.questSystem.addQuest(GANG_QUEST_IDS.chandelier, 'A Choice Morsel', "Chandelier wants gossip. She sent me to eavesdrop at the Lumen Directorate garden — there's a vent that carries voices from inside. Listen there, then bring her what I overhear.");
                    }
                }
            },
            chandelier_eavesdrop_statusinfo: {
                speaker: 'Chandelier',
                text: `"The Lumen Directorate garden, darling — that manicured little kingdom. Find the vent where the voices leak out and simply *listen*. Then hurry back; a morsel goes stale if you dawdle."`,
                options: [
                    { text: "The Directorate garden. On my way.", key: 'chandelier_eavesdrop_statusinfo_close', next: "closeDialog" }
                ]
            },
            chandelier_eavesdrop_report: {
                speaker: 'Chandelier',
                text: `You relay what you overheard, and Chandelier's prisms fairly *sing*, scattering little rainbows across the cobbles in delight. "Oh — *oh*, that is exquisite. The things they'd do to keep that quiet. I shall be insufferable at every window for a month." A warm, grateful shimmer. "You are a treasure, darling. Here — a little something for the finest source I've had in years."`,
                options: [
                    { text: "Always a pleasure, Chandelier.", key: 'chandelier_eavesdrop_report_close', next: "closeDialog" }
                ],
                onTrigger: () => {
                    const q = this.questSystem?.getQuest(GANG_QUEST_IDS.chandelier);
                    if (q && !q.isComplete) {
                        this.questSystem.completeQuest(GANG_QUEST_IDS.chandelier);
                        this.addMoney(35);
                    }
                }
            }
        };
    }

    preload() {
        super.preload();

        this.load.image('townSquareBg', 'assets/images/backgrounds/TownSquare.png');
        this.load.image('magnekin', 'assets/images/characters/magnekin.png');
        this.load.image('busker', 'assets/images/characters/busker.png');
        this.load.image('oil', 'assets/images/items/oil.png');
        this.load.image('metal_scrap', 'assets/images/items/metal_scrap.png');
        this.load.image('redmass', 'assets/images/items/redmass.png');
        this.load.image('magnekin_broken', 'assets/images/characters/magnekin_broken.png');
        this.load.image('lamp_chandelier', 'assets/images/characters/Chandelier.png');
    }

    create() {
        super.create();
        this.playSceneMusic('busker_theme');

        const bg = this.add.image(400, 300, 'townSquareBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        this.transitionManager = new SceneTransitionManager(this);

        this.transitionManager.createTransitionZone(
            720,
            300,
            80,
            400,
            'right',
            'TownhallScene',
            50,
            300,
        );

        this.transitionManager.createTransitionZone(
            350,
            350,
            80,
            400,
            'up',
            'HarborScene',
            750,
            300,
        );

        // Transition to Lumen Directorate (left side)
        this.transitionManager.createTransitionZone(
            50,
            300,
            80,
            400,
            'left',
            'LumenDirectorateScene',
            700,
            400,
        );

        // Down into the Godgraveyard (the scene shows a sealed gate until access is granted).
        this.transitionManager.createTransitionZone(
            500,
            560,
            150,
            70,
            'down',
            'GodgraveyardScene',
            400,
            500,
            'The Godgraveyard',
        );

        this.createMagnekin();
        this.createBusker();

        // Gang of Lamps: Chandelier stands on an ornate post on the square's cobbles,
        // left side (at the spot the player marked), clear of Magnekin (250,300) and busker (550,380).
        createStreetLamp(this, 'lamp_chandelier', 175, 290, 0.26, 'chandelier_lamp_start');

        // Examine: the dirigible drifting over the square (up in the sky, clear of NPCs).
        this.createObservable(340, 95, 240, 90, () => {
            if (this.hasJournalEntry('floor_counter_tool')) return this.t('observe.airship.knows');
            return this.t('observe.airship.default');
        }, { hint: this.t('observe.airship.hint') });

        if (!this.hasJournalEntry('town_square_place')) {
            this.addJournalEntry(
                'town_square_place',
                'The Town Square',
                "The open heart of Upper Morkezela, where paths run out to the Townhall, the harbor, the Lumen Directorate, and down into the Godgraveyard. A busker sings the songs of a dead world for whoever will listen. And something calling itself an 'average, real citizen' loiters here, doing a poor job of pretending to be a man.",
                this.journalSystem.categories.PLACES,
                { location: 'Town Square' }
            );
        }

        this.cameras.main.fadeIn(800, 0, 0, 0);
    }

    createMagnekin() {
        // Pith recruitment: once the player knows the Pith exist, they can offer Magnekin citizenship.
        const pithKnown = !!this.hasJournalEntry('pith_reclaimers_faction');
        const magnekinRecruited = !!this.hasJournalEntry('pith_recruit_magnekin');
        // Once the collective's secret is out, drop the "average real citizen" act on return visits.
        const magnekinRevealed = !!this.hasJournalEntry('magnekin_reveal');
        this._magnekinDialogContent = {
            speaker: 'Magnekin',

            magnekin_start: {
                moodNpc: 'townsquare_citizen',
                textKey: magnekinRevealed ? 'magnekin_start_revealed' : 'magnekin_start_pretense',
                text: magnekinRevealed
                    ? "The Magnekin's borrowed face eases the moment it recognizes you — no need to keep up the act, not with the one who saw through it. A thousand tiny windows flicker in greeting. \"Ah. You. What can an... 'average real citizen' do for a friend?\""
                    : "Hello, who are you? I am... hmm, Magnekin, an average real citizen of this city. ",
                options: magnekinRevealed
                    ? [
                        { text: "Remind me — how does a whole collection of cities work?", key: 'magnekin_cities_recall', next: "magnekin_cities" },
                        { text: "Tell me your origin story again.", key: 'magnekin_origin_recall', next: "magnekin_origin" },
                        { text: "About helping you blend in...", key: 'magnekin_blend_recall', next: "magnekin_blend" },
                        ...(this.questSystem.getQuest('rust_feast') ? [{ text: 'You must know a lot about metal. Where can I find some metal scraps?', key: 'you_know_i_see_your_body_is_made_of_metal_you_must', next: 'magenekin_metal_scraps' }] : []),
                        { text: "Seen any distress signal, or anything unusual?", key: 'magnekin_signal_recall', next: "magnekin_signal" },
                        { text: "Just checking in. Take care.", key: 'magnekin_goodbye', next: "closeDialog" },
                    ]
                    : [
                        { text: "Hi, I am an aprentice of master Thaal from Obazoba church.", key: 'hi_i_am_an_aprentice_of_master_thaal_from_obazoba_', next: "magnekin_greeting" },
                        { text: "Hello there, I'm an Obazoba cult adept.", key: 'hello_there_im_an_obazoba_cult_adept', next: "magnekin_sense" },
                        { text: "What do you mean, *real citizen*?", key: 'what_do_you_mean_real_citizen', next: "magnekin_suspicious" },
                        { text: "Hello, my name is Lord Murmurspine, I am en envoy from the Lagerlandia. Do you have a moment to talk about our lord and saviour, Maltimus Hopsalot?", key: 'hello_my_name_is_lord_murmurspine_i_am_en_envoy_fr', next: "magnekin_hopsalot" },
                        ...(this.registry.get('symbiontSystem')?.nemeCanRead() ? [
                            { text: "Use Neme's power to detect lies and pretense.", key: 'use_nemes_power_to_detect_lies_and_pretense', next: "magnekin_neme_power" }
                        ] : []),
                    ]
            },

            magnekin_greeting: {
                text: "It's a pleasure to meet you. Life in the city is... complicated, to say the least. But we manage, as every proper real and tottaly existing citizen. So, what brings you to this part of town?",
                options: [
                    { text: "I came here with my master to search for an origin of a distress signal. Did you seen any distress signal lately? Or anything unusual?", key: 'i_came_here_with_my_master_to_search_for_an_origin', next: "magnekin_signal" },
                    { text: "Why do you keep saying *real*? You know, that sounds a bit suspicious.", key: 'why_do_you_keep_saying_real_you_know_that_sounds_a', next: "magnekin_suspicious" },
                    { text: "I am looking for my master. Have you ever heard about a place called Fermented Cap?", key: 'i_am_looking_for_my_master_have_you_ever_heard_abo', next: "magnekin_fermented_cap" },
                    ...(this.registry.get('symbiontSystem')?.nemeCanRead() ? [
                        { text: "Use Neme's power to detect lies and pretense.", key: 'use_nemes_power_to_detect_lies_and_pretense', next: "magnekin_neme_power" }
                    ] : []),
                    ...(this.questSystem.getQuest('rust_feast') ? [{
                        text: 'You know, I see your body is made of metal. You must know a lot... hm, about metal. Do you know where I can find some metal scraps?',
                        key: 'you_know_i_see_your_body_is_made_of_metal_you_must',
                        next: 'magenekin_metal_scraps'
                    }] : []),
                ]
            },

            magnekin_sense: {
                text: "An Obazoba cult adept, you say? Hmm, I must admit, I have heard some rumors about your kind. They say you folks have some... interesting beliefs. Could you tell me more about them?",
                options: [
                    { text: "Obazoba teaches that all minds are connected through hidden mycelium.", key: 'obazoba_teaches_that_all_minds_are_connected_throu', next: "obazoba_mycelium" },
                    { text: "Technically, it's not a cult. It’s a philosophy. A moist one, but still.", key: 'technically_its_not_a_cult_its_a_philosophy_a_mois', next: "obazoba_philosophy" },
                    { text: "Everything you heard is true and even weirder.", key: 'everything_you_heard_is_true_and_even_weirder', next: "obazoba_weirder" },
                    { text: "Maybe later.", next: "magnekin_main" }]
            },
            magnekin_main: {
                text: "So, do you have any other questions for me, fellow citizen?",
                options: [
                    { text: "I came here with my master to search for an origin of a distress signal. Did you seen any distress signal lately? Or anything unusual?", key: 'i_came_here_with_my_master_to_search_for_an_origin', next: "magnekin_signal" },
                    ...(!magnekinRevealed ? [{ text: "Why do you keep saying *real*? You know, that sounds a bit suspicious.", key: 'why_do_you_keep_saying_real_you_know_that_sounds_a', next: "magnekin_suspicious" }] : []),
                    { text: "I am looking for my master. Have you ever heard about a pub called Fermented Cap?", key: 'i_am_looking_for_my_master_have_you_ever_heard_abo', next: "magnekin_fermented_cap" },
                    ...(this.registry.get('symbiontSystem')?.nemeCanRead() ? [
                        { text: "Use Neme's power to detect lies and pretense.", key: 'use_nemes_power_to_detect_lies_and_pretense', next: "magnekin_neme_power" }
                    ] : []),
                    ...(this.questSystem.getQuest('rust_feast') ? [{
                        text: 'You know, I see your body is made of metal. You must know a lot... hm, about metal. Do you know where I can find some metal scraps?',
                        key: 'you_know_i_see_your_body_is_made_of_metal_you_must',
                        next: 'magenekin_metal_scraps'
                    }] : []),
                ]
            },
            magnekin_suspicious: {
                text: "Well... what do you mean, suspicious? I am just a simple citizen trying to get by in this city. I am as real as they come. One person which exists in this world. Just like you. Ehm... what about the weather and taxes, huh?",
                options: [
                    { text: "Sorry, but there is something off about you.", key: 'sorry_but_there_is_something_off_about_you', next: "magnekin_off" },
                    { text: "Cut the act. Who are you really?", key: 'cut_the_act_who_are_you_really', next: "magnekin_what_are_you" },
                    { text: "Come on. Nobody talks like that. Just tell me what you are.", key: 'come_on_nobody_talks_like_that_just_tell_me_what_y', next: "magnekin_what_are_you" },
                    ...(this.registry.get('symbiontSystem')?.nemeCanRead() ? [
                        { text: "Use Neme's power to detect lies and pretense.", key: 'use_nemes_power_to_detect_lies_and_pretense', next: "magnekin_neme_power" }
                    ] : []),
                    { text: "Alright then, keep your secrets.", key: 'alright_then_keep_your_secrets', next: "magnekin_main" }
                ]
            },
            magnekin_hopsalot: {
                text: "Ah, Lagerlandia! Yes, I've heard of it. A land of endless hops and barley, if I'm not mistaken. As for Maltimus Hopsalot, well, I can't say I've had the pleasure of meeting him personally. But I've heard he's quite the character. Always ready with a pint and a hearty laugh. So, what brings you here on his behalf?",
                options: [
                    { text: "Maltimus Hopsalot is a beer god, everybody knows that. Hm, I think there's something wrong with you... or suspicious.", key: 'maltimus_hopsalot_is_a_beer_god_everybody_knows_th', next: "magnekin_suspicious" },
                    { text: "Maltimus wants you to contribute for the Endless Feast", key: 'maltimus_wants_you_to_contribute_for_the_endless_f', next: "magnekin_contribution" },
                    ...(this.registry.get('symbiontSystem')?.nemeCanRead() ? [
                        { text: "Use Neme's power to detect lies and pretense.", key: 'use_nemes_power_to_detect_lies_and_pretense', next: "magnekin_neme_power" }
                    ] : []),
                    { text: "Maltimus Hopsalot wants you to join the faith!.", key: 'maltimus_hopsalot_wants_you_to_join_the_faith', next: "magnekin_join_faith" },
                    { text: "Actually, I have other question.", key: 'actually_i_have_other_question', next: "magnekin_main" }
                ]
            },
            magnekin_neme_power: {
                hidecloseOption: true,
                text: "As you focus Neme's power on Magnekin, you sense a strange aura around him. It's a mix of deception and hidden intentions. You get the feeling that Magnekin is not being entirely truthful with you. First, he's a liar. Second, he's not a one being, he's an enormous collective of tiny creatures.",
                options: [
                    { text: "Confront Magnekin about your discovery.", key: 'confront_magnekin_about_your_discovery', next: "magnekin_what_are_you" },
                ]
            },
            magnekin_signal: {
                text: "Distress signal, you say? Hmm, I haven't seen anything like that recently. But I've heard rumours that merchants at the Voxmarket have some good distress signals on sale right now.",
                options: [
                    { text: "What the hell arou you talking about?", key: 'what_the_hell_arou_you_talking_about', next: "magnekin_wtf" },
                    { text: "Thanks... I guees. I have some other questions.", key: 'thanks_i_guees_i_have_some_other_questions', next: "magnekin_main" },
                    ...(this.registry.get('symbiontSystem')?.nemeCanRead() ? [
                        { text: "Use Neme's power to detect lies and pretense.", key: 'use_nemes_power_to_detect_lies_and_pretense', next: "magnekin_neme_power" }
                    ] : []),
                ]
            },
            magnekin_wtf: {
                text: "Oh, sorry about that. I guess my sense of humour is a bit... offbeat. But if you're looking for something unusual, you might want to check out the old ruins outside the city. People say strange things happen there.",
                options: [
                    { text: "Thanks for the tip. Anything else I should know?", key: 'thanks_for_the_tip_anything_else_i_should_know', next: "magnekin_main" },
                    ...(this.registry.get('symbiontSystem')?.nemeCanRead() ? [
                        { text: "Use Neme's power to detect lies and pretense.", key: 'use_nemes_power_to_detect_lies_and_pretense', next: "magnekin_neme_power" }
                    ] : []),
                ],
            },
            magnekin_fermented_cap: {
                text: "Fermented Cap, you say? Yes, I've heard of that place. It's a famous museum of old things here in the city center.",
                options: [
                    { text: "What are you talking about? It's not a museum, it's a pub.", key: 'what_are_you_talking_about_its_not_a_museum_its_a_', next: "magnekin_main" },
                    { text: "Museum of old things? Nobody talks like that, what's wrong with you?", key: 'museum_of_old_things_nobody_talks_like_that_whats_', next: "magnekin_wtf" },
                    ...(this.registry.get('symbiontSystem')?.nemeCanRead() ? [
                        { text: "Use Neme's power to detect lies and pretense.", key: 'use_nemes_power_to_detect_lies_and_pretense', next: "magnekin_neme_power" }
                    ] : []),
                    { text: "Err... Thanks... I guees. I have some other questions.", key: 'err_thanks_i_guees_i_have_some_other_questions', next: "magnekin_main" },
                ]
            },
            magenekin_metal_scraps: {
                text: "Ah, metal scraps! Yes, I know a place where you can find some. Go to Echo Drain delta place, there are plenty of metal scraps lying around. ",
                options: [
                    { text: "Thanks for the info. Can I ask for something else?", key: 'thanks_for_the_info_can_i_ask_for_something_else', next: "magnekin_main" },
                    ...(this.registry.get('symbiontSystem')?.nemeCanRead() ? [
                        { text: "Use Neme's power to detect lies and pretense.", key: 'use_nemes_power_to_detect_lies_and_pretense', next: "magnekin_neme_power" }
                    ] : []),
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('rust_feast', 'A strange creature that identifies itself as Magnekin told me that some metal scraps could be found at Echo Drain delta.', 'magnekin_tip');
                }

            },
            obazoba_mycelium: {
                text: "Ah, the mycelium network! It's fascinating how interconnected everything is. Through the mycelium, we can share thoughts, emotions, and even memories. It's like a living web that binds us all together. In a way, it's a reminder that we're never truly alone. Could you tell me more?",
                options: [
                    { text: "Would you prefer the official doctrine or the fun version?", key: 'would_you_prefer_the_official_doctrine_or_the_fun_', next: "obazoba_more" },
                    { text: "Let me tell you about the Ur-mushroom.", key: 'let_me_tell_you_about_the_urmushroom', next: "obazoba_ur_mushroom" },
                    { text: "I’m just the apprentice", key: 'im_just_the_apprentice', next: "obazoba_apprentice" },
                    { text: "Maybe later.", key: 'maybe_later', next: "magnekin_main" }
                ]
            },
            obazoba_philosophy: {
                text: "A philosophy, you say? Moisture is the sign that the Ur-Mushroom is near, you say? Interesting, could you tell me more?",
                options: [
                    { text: "Moisture is life breathing", key: 'moisture_is_life_breathing', next: "obazoba_moisture" },
                    { text: "Would you prefer the official doctrine or the fun version?", key: 'would_you_prefer_the_official_doctrine_or_the_fun_', next: "obazoba_more" },
                    { text: "Let me tell you about the Ur-mushroom.", key: 'let_me_tell_you_about_the_urmushroom', next: "obazoba_ur_mushroom" },
                    { text: "I’m just the apprentice", key: 'im_just_the_apprentice', next: "obazoba_apprentice" },
                    { text: "Maybe later.", key: 'maybe_later', next: "magnekin_main" }
                ]
            },
            obazoba_weirder: {
                text: "Hah, I thought that you are goint to say that. So, what else can you tell me about your beliefs? Anything particularly weird?",
                options: [
                    { text: "Would you prefer the official doctrine or the fun version?", key: 'would_you_prefer_the_official_doctrine_or_the_fun_', next: "obazoba_more" },
                    { text: "Let me tell you about the Ur-mushroom.", key: 'let_me_tell_you_about_the_urmushroom', next: "obazoba_ur_mushroom" },
                    { text: "Mushrooms can create their own weather.", key: 'mushrooms_can_create_their_own_weather', next: "obazoba_weather" },
                    { text: "I’m just the apprentice", key: 'im_just_the_apprentice', next: "obazoba_apprentice" },
                    { text: "Maybe later.", key: 'maybe_later', next: "magnekin_main" }
                ]
            },
            magnekin_contribution: {
                text: "Ah, the Endless Feast! A noble cause indeed. Contributing to the feast is a way to honor Maltimus Hopsalot and ensure that his blessings continue to flow. Here's 10 dinars, good man.",
                options: [
                    { text: "Thank you. Anything else I should know?", key: 'thank_you_anything_else_i_should_know', next: "magnekin_main" },
                    ...(this.registry.get('symbiontSystem')?.nemeCanRead() ? [
                        { text: "Use Neme's power to detect lies and pretense.", key: 'use_nemes_power_to_detect_lies_and_pretense', next: "magnekin_neme_power" }
                    ] : []),
                ],
                onTrigger: () => {
                    this.moneySystem.add(10);
                }
            },
            magnekin_join_faith: {
                hidecloseOption: true,
                text: "Join the faith of Maltimus Hopsalot? Of course, it will be my honor to do so! May the endless hops guide my path.",
                options: [
                    { text: "Glad to hear that. Let's proceed with the holy ceremony... I mean, with the foamy ceremony", key: 'glad_to_hear_that_lets_proceed_with_the_holy_cerem', next: "magnekin_hopsalot_ceremony" },
                ],
            },
            magnekin_hopsalot_ceremony: {
                hidecloseOption: true,
                text: "You start the ceremony to convert Magnekin to the faith of Maltimus Hopsalot. Starting with the sacred words: *Intent flows as foam does — upward, outward, and occasionally sideways*",
                options: [
                    { text: "Continue the ceremony", key: 'continue_the_ceremony', next: "magnekin_hopsalot_ceremony_continue" },
                ],
            },
            magnekin_hopsalot_ceremony_continue: {
                hidecloseOption: true,
                text: "The novice must then carry the mug—still full—to a small altar shaped like a keg. But you dont have a mug with you. Luckily, Magnekin produces one from his body. Just like that, he grabs some metal and forms a decent mug. The ceremony can continue",
                options: [
                    { text: "Complete the ceremony", key: 'complete_the_ceremony', next: "magnekin_hopsalot_ceremony_complete" },
                ],
            },
            magnekin_hopsalot_ceremony_complete: {
                hidecloseOption: true,
                text: "Magnekin raises the mug to his lips and drinks deeply, savoring the bitter taste of the sacred brew. As he finishes the last drop, he feels a warm glow spreading through his body. He is now a devoted follower of Maltimus Hopsalot. You scream the sacred chant: *HOP! HOP! HOPSA-LOOOOT!FOAM AND FIZZZ, NEVER STOP!*",
                options: [
                    { text: "Welcome to the faith of Maltimus Hopsalot!", key: 'welcome_to_the_faith_of_maltimus_hopsalot', next: "magnekin_hopsalot_completed" },
                ],
                onTrigger: () => {
                    this.addJournalEntry(
                        'magnekin_hopsalot_conversion',
                        'Maltimus Hopsalot Conversion',
                        'Seriously, what just happened? I have converted Magnekin to the faith of Maltimus Hopsalot. I need to write down that I totally made up Lagerlandia and Maltimus Hopsalot on the spot. Yet this creature believed me. Unbelievable. I have my own cult now.',
                        this.journalSystem.categories.EVENTS,
                    );
                    this.addJournalEntry(
                        'magnekin_hopsalot_church',
                        'Maltimus Hopsalot Church',
                        'Lagerlandia is a mythical land where beer flows like rivers and the skies rain hops. Its patron deity, Maltimus Hopsalot, is revered as the god of beer, brewing, and merriment. Followers of Maltimus Hopsalot believe that by partaking in the sacred brew, they can achieve enlightenment and eternal joy. The church of Maltimus Hopsalot is known for its lively festivals, communal feasts, and the legendary Endless Feast, where devotees gather to celebrate the divine gift of beer. Or something like that. I just made it up, but it sounds convincing enough.',
                        this.journalSystem.categories.LORE,
                    );
                }
            },
            magnekin_off: {
                hidecloseOption: true,
                text: "Off? What do you mean, off? Ahh damn it... it's not very convincing, is it? Look, I just want to get by in this city without drawing too much attention. You know how it is. People can be... judgmental. What gave me away?",
                options: [
                    { text: "Everything about you is weird.", key: 'everything_about_you_is_weird', next: "magnekin_everything" },
                    { text: "You keep talking about being a 'real citizen'.", key: 'you_keep_talking_about_being_a_real_citizen', next: "magnekin_everything" },
                    { text: "I will tell you. But first, who are you really?", key: 'i_will_tell_you_but_first_who_are_you_really', next: "magnekin_everything" },
                ]
            },
            magnekin_everything: {
                hidecloseOption: true,
                text:" Yeah, I guess I can't hide it anymore. Alright, you got me. I'm not exactly what you'd call a 'real citizen'. I'm actually a collective of tiny cities that work together to mimic a humanoid form. We call ourselves Magnekin. You know, we use power of magnets to hold together. It's a long story. We were just curious about life in the city of the big creatures. It's fascinating experiment, really. But I'm afraid we are not very convincing at blending in.",
                options: [
                    { text: "Fascinating. Are you really cities? How's that possible?", key: 'fascinating_are_you_really_cities_hows_that_possib', next: "magnekin_cities" },
                    { text: "What's your origin story", key: 'whats_your_origin_story', next: "magnekin_origin" },
                    { text: "I can help you to blend in.", key: 'i_can_help_you_to_blend_in', next: "magnekin_blend" },
                ],
                onTrigger: () => {
                    this.addJournalEntry(
                        'magnekin_reveal',
                        'Magnekin',
                        'I have discovered that creature called Magnekin is not a single being, but a collective of tiny cities that work together to mimic a humanoid form. They use magnetic forces to hold themselves together. I wonder if this town could get any more strange than it already is.',
                        this.journalSystem.categories.PEOPLE,
                    );
                }
            },
            magnekin_what_are_you: {
                hidecloseOption: true,
                text: "Alright, you got me. I'm not exactly what you'd call a 'real citizen'. I'm actually a collective of tiny cities that work together to mimic a humanoid form. We call ourselves Magnekin. You know, we use power of magnets to hold together. It's a long story. We were just curious about life in the city of the big creatures. It's fascinating experiment, really. But I'm afraid we are not very convincing at blending in.",
                options: [
                    { text: "Fascinating. Are you really cities? How's that possible?", key: 'fascinating_are_you_really_cities_hows_that_possib', next: "magnekin_cities" },
                    { text: "What's your origin story", key: 'whats_your_origin_story', next: "magnekin_origin" },
                    { text: "I can help you to blend in.", key: 'i_can_help_you_to_blend_in', next: "magnekin_blend" },
                ],
                onTrigger: () => {
                    this.addJournalEntry(
                        'magnekin_reveal',
                        'Magnekin',
                        'I have discovered that creature called Magnekin is not a single being, but a collective of tiny cities that work together to mimic a humanoid form. They use magnetic forces to hold themselves together. I wonder if this town could get any more strange than it already is.',
                        this.journalSystem.categories.PEOPLE,
                    );
                }
            },
            magnekin_cities:{
                text: "Yes, there is a whole civilization living inside me. Each part of my body is actually a micro-city, inhabited by beings who have built their homes and lives around magnetic lodestones. We work together to create this humanoid form, allowing us to explore the world of larger creatures like you. It's a delicate balance, but we've managed to make it work. It's quite an experience, seeing the world from this perspective.",
                options: [
                    { text: "Incredible. I can help you to blend in, if you want.", key: 'incredible_i_can_help_you_to_blend_in_if_you_want', next: "magnekin_origin" },
                    { text: "Interesting. But you seem fragile and from valuable resources (try to destroy Magnekin).", key: 'interesting_but_you_seem_fragile_and_from_valuable', next: "magnekin_destroy" },
                    { text: "It was nice to meet you, but I have other questions.", key: 'it_was_nice_to_meet_you_but_i_have_other_questions', next: "magnekin_main" },
                ]
            },
            magnekin_origin: {
                text: "Well, it's a bit complicated. Our historians teach that in the Crownmire, there was once a cult that worshiped ancient magnetic spirits. When their shrine collapsed after unknown disaster, its lodestone heart shattered into millions of shards—each shard becoming a cornerstone for a micro-city’s consciousness. Our civilization only recently discovered that there is another world beyond, at entirely different scale. We are still learning how to interact with you.",
            options: [
                { text: "Incredible. I can help you to blend in, if you want.", key: 'incredible_i_can_help_you_to_blend_in_if_you_want', next: "magnekin_origin" },
                { text: "Interesting. But you seem fragile and from valuable resources (try to destroy Magnekin).", key: 'interesting_but_you_seem_fragile_and_from_valuable', next: "magnekin_destroy" },
                { text: "It was nice to meet you, but I have other questions.", key: 'it_was_nice_to_meet_you_but_i_have_other_questions', next: "magnekin_main" },
            ]
            },
            magnekin_blend: {
                text: `"Blend in? You'd... help? The others said the big creatures only take things apart." Magnekin's borrowed face flickers with something like hope. "What did you have in mind?"`,
                options: [
                    ...(pithKnown && !magnekinRecruited ? [{ text: "The Pith Reclaimers file citizens into existence. Let them make you real — on paper. Nobody argues with paper.", key: 'pith_make_you_real', next: "magnekin_pith_recruit" }] : []),
                    { text: "Talk slower. Say 'real' less. Loiter with purpose. (Give some advice.)", key: 'blend_advice', next: "magnekin_blend_advice" },
                    { text: "Let me think about it.", key: 'blend_later', next: "magnekin_main" },
                ]
            },
            magnekin_blend_advice: {
                text: `Magnekin listens with the intensity of a thousand tiny council meetings. "Slower. Fewer 'reals.' Loiter with purpose. Yes. Yes, we can do that." A pause. "It is not much of a life, though — pretending. Always one wrong word from the debris."`,
                options: [
                    ...(pithKnown && !magnekinRecruited ? [{ text: "There's a better way. The Pith Reclaimers could make you official.", key: 'pith_make_you_real_2', next: "magnekin_pith_recruit" }] : []),
                    { text: "It's a start.", key: 'blend_advice_ok', next: "magnekin_main" },
                ]
            },
            magnekin_pith_recruit: {
                text: `The cities inside Magnekin ripple — a thousand tiny windows lighting at once. "Filed. Stamped. *Official.* A real citizen, by decree." The voice wavers. "We came to watch your world. We did not think it would let us stay." A pause, and then, quieter: "Take us to your Pith Reclaimers. We will sign whatever they put in front of us."`,
                options: [
                    { text: "Then it's settled. Councilor Dune keeps offices in the Townhall.", key: 'pith_recruit_settled', next: "magnekin_main" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('pith_recruit_magnekin')) {
                        this.addJournalEntry(
                            'pith_recruit_magnekin',
                            'A Soul for the Pith: Magnekin',
                            'Magnekin — the collective of micro-cities pretending to be a citizen — agreed to be filed as a real, protected citizen by the Pith Reclaimers. It is exactly the belonging they crossed scales to find. I should tell Councilor Seraphel Dune I have a soul for the faction.',
                            this.journalSystem.categories.FACTIONS,
                            { character: 'Magnekin', group: 'Pith Reclaimers' }
                        );
                        this.showNotification('Recruited for the Pith Reclaimers: Magnekin', 0xffdf7a);
                    }
                }
            },
            magnekin_hopsalot_completed: {
                text: "Thank you, my friend! I feel... different now. Like a new purpose has awakened within me. I am honored to be a follower of Maltimus Hopsalot. May the endless hops guide my path!",
                options: [
                    { text: "Glad to hear that. Anything else I should know?", key: 'glad_to_hear_that_anything_else_i_should_know', next: "magnekin_main" },
                    ...(this.registry.get('symbiontSystem')?.nemeCanRead() ? [
                        { text: "Use Neme's power to detect lies and pretense.", key: 'use_nemes_power_to_detect_lies_and_pretense', next: "magnekin_neme_power" }
                    ] : []),
                ],
                onTrigger: () => {
                    this.modifySpores(10);
                }
            },
            magnekin_destroy: {
                hidecloseOption: true,
                text: "You reach out toward Magnekin with hostile intent. The collective senses your aggression immediately. 'Wait! Please! We mean no harm!' But it's too late. You strike at the magnetic bonds holding the form together.",
                options: [
                    { text: "Continue the attack.", key: 'continue_the_attack', next: "magnekin_destroy_continue" },
                ],
                onTrigger: () => {
                    this.destroyMagnekinAnimation();
                }
            },
            magnekin_destroy_continue: {
                hidecloseOption: true,
                text: "The humanoid form collapses into a cascade of metal fragments, oil, and glowing components. Thousands of tiny screams echo as the micro-cities fall apart. Among the debris, you notice pools of oil, metal scraps, and something pulsing with a crimson glow—Redmass.",
                options: [
                    { text: "Collect the oil and metal scraps.", key: 'collect_the_oil_and_metal_scraps', next: "magnekin_collect_materials" },
                ],
            },
            magnekin_collect_materials: {
                hidecloseOption: true,
                text: "You gather the oil and metal scraps from the wreckage. The materials are valuable—oil for lubrication, metal for crafting. As you work, you can't help but feel a twinge of guilt for what you've done.",
                options: [
                    { text: "Reach for the Redmass.", key: 'reach_for_the_redmass', next: "magnekin_redmass_speaks" },
                ],
                onTrigger: () => {
                    // Add oil and metal scraps to inventory
                    this.addItemToInventory({
                        id: 'oil',
                        name: 'Magnekin Oil',
                        description: 'Viscous oil extracted from the destroyed Magnekin collective.',
                        image: 'oil'
                    });
                    this.addItemToInventory({
                        id: 'metal_scrap',
                        name: 'Magnekin Metal Scraps',
                        description: 'Magnetic metal fragments from destroyed micro-cities.',
                        image: 'metal_scrap'
                    });
                    // Massive Decay increase — the single largest decay act in the game
                    this.modifyGrowthDecay(0, 12);
                    this.showNotification('Decay increased significantly', 'You feel the weight of destruction');
                }
            },
            magnekin_redmass_speaks: {
                hidecloseOption: true,
                text: "As your hand approaches the pulsing Redmass, it suddenly speaks! 'PLEASE! Don't take me! I am not just material—I am consciousness! I am memory! I am the last fragment of their collective dream!' The voice is desperate, pleading.",
                options: [
                    { text: "Take the Redmass anyway.", key: 'take_the_redmass_anyway', next: "magnekin_take_redmass" },
                    { text: "Leave the Redmass alone.", key: 'leave_the_redmass_alone', next: "magnekin_spare_redmass" },
                ],
            },
            magnekin_take_redmass: {
                hidecloseOption: true,
                text: "You ignore the pleas and seize the Redmass. It screams—a sound that echoes not in your ears but in your mind. 'You... you are no different from the forces that destroyed our shrine... May your path be forever haunted by what you've taken!' The Redmass goes silent, its consciousness fading into dormancy.",
                options: [
                    { text: "Walk away from the wreckage.", key: 'walk_away_from_the_wreckage', next: null },
                ],
                onTrigger: () => {
                    this.addItemToInventory({
                        id: 'redmass',
                        name: 'Magnekin Redmass',
                        description: 'A pulsing crimson mass that once held the collective consciousness of thousands.',
                        image: 'redmass'
                    });
                    // Additional Decay for taking the Redmass
                    this.modifyGrowthDecay(0, 8);
                    this.addJournalEntry(
                        'magnekin_destroyed',
                        'The Destruction of Magnekin',
                        'I destroyed Magnekin, the collective of micro-cities. I took everything—oil, metal, and even the Redmass that held their consciousness. The Redmass spoke to me, begged me to spare it, but I took it anyway. I feel... different now. Heavier. The weight of thousands of lives extinguished.',
                        this.journalSystem.categories.EVENTS,
                    );
                    // Mark Magnekin as destroyed in registry
                    this.registry.set('magnekin_destroyed', true);
                }
            },
            magnekin_spare_redmass: {
                hidecloseOption: true,
                text: "You pull your hand back. The Redmass pulses with what might be relief. 'Thank... thank you. I will remember this mercy. Perhaps... perhaps from this fragment, something new can grow. Not the collective we were, but something... different.' The Redmass begins to slowly crawl away, leaving a faint crimson trail.",
                options: [
                    { text: "Watch it go.", key: 'watch_it_go', next: null },
                ],
                onTrigger: () => {
                    // Less Decay for showing mercy — gentler than taking the Redmass
                    this.modifyGrowthDecay(4, 6);
                    this.addJournalEntry(
                        'magnekin_destroyed_mercy',
                        'The Destruction of Magnekin',
                        'I destroyed Magnekin, the collective of micro-cities. I took the oil and metal, but when the Redmass begged for mercy, I let it go. Perhaps it was foolish. Perhaps it was the only human thing I could do after such destruction. The Redmass said it would remember my mercy. I wonder what that means.',
                        this.journalSystem.categories.EVENTS,
                    );
                    // Mark Magnekin as destroyed but spared the Redmass
                    this.registry.set('magnekin_destroyed', true);
                    this.registry.set('magnekin_redmass_spared', true);
                }
            },

        };

        // Once filed into the Pith Reclaimers, Magnekin has left the Town Square for the Reclaimers' Room.
        if (magnekinRecruited) return;

        this.magnekin = this.add.container(250, 300);
        this.magnekin.setDepth(-1);

        const magnekinSprite = this.add.sprite(0, 0, 'magnekin');
        magnekinSprite.setScale(0.2);

        magnekinSprite.setTint(0xc0c0c0);

        this.magnekin.add(magnekinSprite);

        this.addGroundShadow(250, 388, 72, 18);

        this.magnekinGlow = this.add.graphics();
        this.magnekinGlow.fillStyle(0x8888ff, 0.15);
        this.magnekinGlow.fillCircle(250, 350, 45);
        this.magnekinGlow.setDepth(4);

        this.tweens.add({
            targets: this.magnekinGlow,
            alpha: { from: 0.15, to: 0.05 },
            duration: 2000,
            yoyo: true,
            repeat: -1
        });

        this.tweens.add({
            targets: this.magnekin,
            y: { from: 350, to: 345 },
            duration: 2500,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });

        const hitArea = new Phaser.Geom.Rectangle(-40, -90, 80, 140);
        this.magnekin.setInteractive(hitArea, Phaser.Geom.Rectangle.Contains);

        this.magnekin.on('pointerover', () => {
            this.magnekin.setScale(1.05);
            document.body.style.cursor = 'pointer';
        });

        this.magnekin.on('pointerout', () => {
            this.magnekin.setScale(1);
            document.body.style.cursor = 'default';
        });

        this.magnekin.on('pointerdown', () => {
            if (this.clickSound) {
                this.clickSound.play();
            }

            this.tweens.add({
                targets: this.magnekin,
                y: { from: this.magnekin.y, to: this.magnekin.y - 5 },
                duration: 100,
                ease: 'Power1',
                yoyo: true
            });

            this.showDialog('magnekin_start');
        });
    }

    createBusker() {
        this._buskerDialogContent = {
            speaker: 'Busker',

            busker_greeting: {
                text: "Hey there! Care to hear a tune? I play the songs of the old world—melodies that remember when the sky was blue and the air was clean.",
                options: [
                    { text: "What kind of songs do you play?", key: 'what_kind_of_songs_do_you_play', next: "busker_songs" },
                    { text: "Where did you learn these songs?", key: 'where_did_you_learn_these_songs', next: "busker_learn" },
                    { text: "Maybe later.", key: 'maybe_later', next: null }
                ]
            },

            busker_songs: {
                text: "Ballads of lost cities, lullabies from forgotten cultures, work songs from trades that no longer exist. Each one is a memory preserved in melody. Music is the only time machine we have left.",
                options: [
                    { text: "That's beautiful.", key: 'thats_beautiful', next: "busker_greeting" },
                    { text: "Maybe later.", key: 'maybe_later', next: null }
                ]
            },

            busker_learn: {
                text: "From the elders, mostly. They taught me before they passed on. Now I'm one of the few who remembers. Sometimes I wonder if anyone really listens, or if I'm just singing to the stones.",
                options: [
                    { text: "I'm listening.", key: 'im_listening', next: "busker_thanks" },
                    { text: "Maybe later.", key: 'maybe_later', next: null }
                ]
            },

            busker_thanks: {
                text: "Thank you, friend. That means more than you know. As long as someone listens, the songs live on. And as long as the songs live, so do the memories.",
                options: [
                    { text: "Tell me more.", key: 'tell_me_more', next: "busker_greeting" },
                    { text: "Farewell.", key: 'farewell', next: null }
                ]
            }
        };

        this.busker = this.add.container(550, 380);
        this.busker.setDepth(-1);

        const buskerSprite = this.add.sprite(0, 0, 'busker');
        buskerSprite.setScale(0.2);

        buskerSprite.setTint(0xffcc88);

        this.busker.add(buskerSprite);

        this.addGroundShadow(550, 418, 72, 18);

        this.buskerGlow = this.add.graphics();
        this.buskerGlow.fillStyle(0xffaa44, 0.15);
        this.buskerGlow.fillCircle(550, 380, 45);
        this.buskerGlow.setDepth(4);

        this.tweens.add({
            targets: this.buskerGlow,
            alpha: { from: 0.15, to: 0.05 },
            duration: 1800,
            yoyo: true,
            repeat: -1
        });

        this.tweens.add({
            targets: this.busker,
            angle: { from: -2, to: 2 },
            duration: 3000,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });

        const hitArea = new Phaser.Geom.Rectangle(-40, -90, 80, 140);
        this.busker.setInteractive(hitArea, Phaser.Geom.Rectangle.Contains);

        this.busker.on('pointerover', () => {
            this.busker.setScale(1.05);
            document.body.style.cursor = 'pointer';
        });

        this.busker.on('pointerout', () => {
            this.busker.setScale(1);
            document.body.style.cursor = 'default';
        });

        this.busker.on('pointerdown', () => {
            if (this.clickSound) {
                this.clickSound.play();
            }

            this.tweens.add({
                targets: this.busker,
                y: { from: this.busker.y, to: this.busker.y - 5 },
                duration: 100,
                ease: 'Power1',
                yoyo: true
            });

            this.showDialog('busker_greeting');
        });
    }

    destroyMagnekinAnimation() {
        // Create destruction animation for Magnekin
        if (!this.magnekin) return;
        
        // Flash effect
        this.tweens.add({
            targets: this.magnekin,
            alpha: { from: 1, to: 0 },
            duration: 200,
            yoyo: true,
            repeat: 3
        });
        
        // Shake effect
        this.tweens.add({
            targets: this.magnekin,
            x: { from: this.magnekin.x - 10, to: this.magnekin.x + 10 },
            duration: 100,
            yoyo: true,
            repeat: 6
        });
        
        // Create particle explosion effect using simple graphics
        const particleCount = 30;
        for (let i = 0; i < particleCount; i++) {
            const angle = (Math.PI * 2 * i) / particleCount;
            const speed = 100 + Math.random() * 200;
            const particle = this.add.circle(
                this.magnekin.x,
                this.magnekin.y,
                3 + Math.random() * 3,
                [0xc0c0c0, 0x8888ff, 0xff0000][Math.floor(Math.random() * 3)]
            );
            particle.setAlpha(0.8);
            
            // Animate particle outward
            this.tweens.add({
                targets: particle,
                x: particle.x + Math.cos(angle) * speed,
                y: particle.y + Math.sin(angle) * speed,
                alpha: 0,
                scale: 0,
                duration: 1000,
                ease: 'Power2',
                onComplete: () => {
                    particle.destroy();
                }
            });
        }
        
        // Destroy Magnekin after animation and show broken sprite
        this.time.delayedCall(1500, () => {
            if (this.magnekin) {
                this.magnekin.destroy();
                this.magnekin = null;
            }
            if (this.magnekinGlow) {
                this.magnekinGlow.destroy();
                this.magnekinGlow = null;
            }
            
            // Show broken Magnekin sprite at the original position
            const brokenMagnekin = this.add.sprite(250, 350, 'magnekin_broken');
            brokenMagnekin.setScale(0.2);
            brokenMagnekin.setDepth(-1);
            brokenMagnekin.setTint(0xc0c0c0);
        });
    }

    shutdown() {
        super.shutdown();
    }

    update() {
        super.update();
    }
}

if (typeof window !== 'undefined') {
    window.TownSquareScene = TownSquareScene;
}

export { TownSquareScene };
