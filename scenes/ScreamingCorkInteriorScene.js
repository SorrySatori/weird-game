import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import ShopSystem from '../systems/items/ShopSystem.js';

export default class ScreamingCorkInteriorScene extends GameScene {
    constructor() {
        super({ key: 'ScreamingCorkInteriorScene' });
        this.isTransitioning = false;
        this.shopSystem = null;
    }

    get dialogContent() {
        const hasFindRustQuest = (this.questSystem && this.questSystem.getQuest('find_rust_choir') && !this.questSystem.getQuest('find_rust_choir').isComplete && this.questSystem.getQuest('find_rust_choir').updates.some(update => update.key === 'talk_to_ravla'));
        const hasRustFeastQuest = !!(this.questSystem && this.questSystem.getQuest('rust_feast') && !this.questSystem.getQuest('rust_feast').isComplete);
        const hasAllFeastItems = !!(this.hasItem && this.hasItem('oil') && this.hasItem('metal_scrap') && this.hasItem('redmass'));
        const hasVoluntaryRedmass = !!(hasAllFeastItems && this.hasJournalEntry('redmass_collected_voluntary'));
        const redmassSparedOnly = !!(this.registry.get('redmass_spared') && !(this.hasItem && this.hasItem('redmass')));
        const hasIllusionOption = !!(hasRustFeastQuest && this.hasItem && this.hasItem('oil') && this.hasItem('metal_scrap') && !this.hasItem('redmass') && this.symbiontSystem?.hasSymbiont('ulvarex-borrowed-horizon'));
        const rustFeastComplete = !!(this.questSystem && this.questSystem.getQuest('rust_feast')?.isComplete);
        const knowsSulkberries = !!this.hasJournalEntry('bishop_berries');
        const sulkberriesClearedHeliodor = !!this.hasJournalEntry('sulkberries_cleared_heliodor');
        const hasNeme = !!this.symbiontSystem?.hasSymbiont('neme-crownmire');
        const nemeCanRead = !!this.symbiontSystem?.nemeCanRead(); // false when silenced by high decay

        return {
            ...super.dialogContent,

            // ---- Finale epilogue (only reached via epilogue_mode; Thaal at the bar) ----
            epilogue_intro: {
                speaker: 'Narrator',
                hideCloseOption: true,
                text: "Later. The city breathes as it always has, indifferent and alive. The festival ashes are long cold. And here in the Screaming Cork — as at the very beginning — a familiar shape settles over a familiar drink.",
                options: [{ text: "Go to him.", key: 'epilogue_go_in', next: "epilogue_thaal_ask" }]
            },
            epilogue_thaal_ask: {
                speaker: 'Master Thaal',
                hideCloseOption: true,
                text: "He does not turn around. *\"So?\"*",
                options: [{ text: "It was complicated.", key: 'epilogue_complicated', next: "epilogue_thaal_good" }]
            },
            epilogue_thaal_good: {
                speaker: 'Master Thaal',
                hideCloseOption: true,
                text: "*\"Good.\"* A pause; he swirls whatever is in the cup. *\"Simple things rarely repay the journey.\"*",
                options: [{ text: "(Say nothing.)", key: 'epilogue_silence', next: "epilogue_thaal_bishop" }]
            },
            epilogue_thaal_bishop: {
                speaker: 'Master Thaal',
                hideCloseOption: true,
                text: "He finally half-turns, and there is something almost kind in it. *\"So...\"* A beat. *\"...did you find the Bishop?\"*",
                options: [{ text: "…", key: 'epilogue_finish', next: "epilogue_end" }]
            },
            epilogue_end: {
                speaker: 'Narrator',
                hideCloseOption: true,
                text: "You had. And you had not. And the city went on above the two held breaths, not knowing which of them it had chosen — or that it had chosen at all.",
                options: [{ text: "(End.)", key: 'epilogue_close', next: "closeDialog", onSelect: () => this.rollCredits() }]
            },
            speaker: 'Ravla',

            // Ravla dialog - the forger
            ravla_start: {
                text: "Ravla looks up from her work, eyes sharp and calculating. \"Need something? I'm busy, so make it quick.\"",
                options: [
                    { text: "Who are you?", key: 'who_are_you', next: "ravla_who" },
                    { text: "What do you do here?", key: 'what_do_you_do_here', next: "ravla_job" },
                    ...(hasFindRustQuest ? [{ text: "I was told you can get me to Rust Choir base.", key: 'i_was_told_you_can_get_me_to_rust_choir_base', next: "ravla_rust_domain" }] : []),
                    ...(hasRustFeastQuest && hasAllFeastItems && hasVoluntaryRedmass ? [{ text: "I have gathered everything for the Rust Feast.", key: 'i_have_gathered_everything_for_the_rust_feast', next: "ravla_feast_shard" }] : []),
                    ...(hasRustFeastQuest && hasAllFeastItems && !hasVoluntaryRedmass ? [{ text: "I have gathered everything for the Rust Feast.", key: 'i_have_gathered_everything_for_the_rust_feast', next: "ravla_feast_full_redmass" }] : []),
                    ...(hasIllusionOption ? [{ text: "[Mirage Weave] I have the oil and metal scrap... and something that looks like redmass.", key: 'mirage_weave_i_have_the_oil_and_metal_scrap_and_so', next: "ravla_feast_illusion" }] : []),
                    ...(hasRustFeastQuest && redmassSparedOnly && !hasIllusionOption ? [{ text: "I found a redmass, but I chose to leave it alive...", key: 'i_found_a_redmass_but_i_chose_to_leave_it_alive', next: "ravla_feast_spared_redmass" }] : []),
                    ...(hasRustFeastQuest && !hasAllFeastItems && !redmassSparedOnly && !hasIllusionOption ? [{ text: "I'm still gathering the feast ingredients.", key: 'im_still_gathering_the_feast_ingredients', next: "ravla_feast_missing" }] : []),
                    ...(rustFeastComplete ? [{ text: "About the Rust Feast...", key: 'about_the_rust_feast', next: "ravla_feast_done" }] : [])
                ]
            },
            ravla_who: {
                text: "Name's Ravla. I'm an... artist of sorts. Been at the Cork for years now. It's quiet, keeps the authorities at a distance.",
                options: [
                    { text: "Back", key: 'back', next: "ravla_start" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('met_ravla')) {
                        this.addJournalEntry(
                            'met_ravla',
                            'Ravla',
                            "Ravla holds a corner of the Screaming Cork, forging documents for anyone who can pay and keeping the authorities at arm's length. She is also the Rust Choir's gatekeeper — nothing reaches Brukk or the machines without passing her first. Sharp-eyed, unsentimental, and unmoved by charm.",
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Ravla', location: 'Screaming Cork' }
                        );
                    }
                }
            },
            ravla_job: {
                text: "I provide services for those who need certain... paperwork adjusted. Nothing illegal, of course. Just creative interpretations of bureaucratic necessities.",
                options: [
                    { text: "I need some documents...", key: 'i_need_some_documents', next: "ravla_documents" },
                    { text: "Back", key: 'back', next: "ravla_start" }
                ]
            },
            ravla_documents: {
                text: "Hmm. What kind of documents are we talking about? I don't work for free, and I don't work for just anyone.",
                options: [
                    { text: "Just curious", key: 'just_curious', next: "ravla_curious" },
                    ...(this.registry.get('questSystem')?.getQuest('ortolan_arms')?.updates.some(update => update.key === 'forge_documents_suggestion') ? [
                        { text: "I need help with Ortolan's paperwork", key: 'i_need_help_with_ortolans_paperwork', next: "ravla_ortolan" }
                    ] : [])
                ]
            },
            ravla_curious: {
                text: "Curiosity is expensive in this city. Come back when you have real business.",
                options: [
                    { text: "Back", key: 'back', next: "ravla_start" }
                ]
            },
            ravla_ortolan: {
                text: "Artisan's Exemption Form? For Ortolan? That game designer? Interesting. Those forms have special seals that are hard to duplicate. But... I might be able to help.",
                options: [
                    { text: "What would you need?", key: 'what_would_you_need', next: "ravla_ortolan_need" },
                    { text: "Back", key: 'back', next: "ravla_start" }
                ]
            },
            ravla_ortolan_need: {
                text: "It won't be cheap - 50 dinars. But I can make it perfect. No one would know the difference.",
                options: [
                    { text: "Here's the money", key: 'heres_the_money', next: "ravla_check_money" },
                    { text: "I'll think about it", key: 'ill_think_about_it', next: "ravla_ortolan_agree" },
                    { text: "That's too expensive", key: 'thats_too_expensive', next: "ravla_start" }
                ]
            },
            ravla_check_money: {
                text: "",
                options: [],
                onShow: () => {
                    // Check if player has enough money
                    if (this.hasEnoughMoney(50)) {
                        this.subtractMoney(50);
                        this.showNotification("-50 dinar");
                        
                        // Add forged document to inventory
                        this.addItemToInventory({
                            id: 'forged-arms-permission',
                            name: "Forged Multiple Arms Permission",
                            description: "A convincing forgery of an Artisan's Exemption Form that would allow the bearer to legally possess multiple arms for specialized work.",
                            stackable: false
                        });
                        this.showNotification('Received: Forged Multiple Arms Permission');
                        
                        // Update quest
                        const questSystem = this.registry.get('questSystem');
                        if (questSystem) {
                            questSystem.updateQuest('ortolan_arms', 'You obtained a forged Artisan\'s Exemption Form from Ravla. Deliver it to Ortolan at the Shed Courtyard.', 'document_obtained');
                            this.showNotification('Quest updated: Ortolan Arms Investigation');
                        }
                        
                        // Show success dialog
                        this.showDialog('ravla_forge_success');
                    } else {
                        // Not enough money
                        this.showDialog('ravla_not_enough_money');
                    }
                }
            },
            ravla_forge_success: {
                text: "Here you go. Perfect forgery, if I do say so myself. The official seals, the watermarks, even the special ink - all perfect. No one will question this. Just don't tell anyone where you got it.",
                options: [
                    { text: "Thank you", key: 'thank_you', next: "closeDialog" }
                ]
            },
            ravla_not_enough_money: {
                text: "What are you trying to pull? You don't have 50 dinars. Come back when you have the money. I don't work for free.",
                options: [
                    { text: "Sorry, I'll be back", key: 'sorry_ill_be_back', next: "closeDialog" }
                ]
            },
            ravla_ortolan_agree: {
                text: "Good. Bring the money, and I'll have it ready in no time. Just don't tell anyone where you got it.",
                options: [
                    { text: "Deal", key: 'deal', next: "closeDialog" }
                ],
                onTrigger: () => {
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem) {
                        questSystem.updateQuest('ortolan_arms', 'Ravla at the Screaming Cork can forge the Artisan\'s Exemption Form for Ortolan, but she wants 50 dinars for the job.', 'ravla_forger_agreement');
                        this.showNotification('Quest updated: Ortolan Arms Investigation');
                    }
                }
            },
            ravla_rust_domain: {
                text: "Ah, so you're looking to get into the Rust Choir's territory? That's tricky business. But I might be able to help you with that. But why should I?",
                options: [
                { text: "I want to join you.", key: 'i_want_to_join_you', next: "ravla_rust_join" },
                { text: "I need to speak with Brukk.", key: 'i_need_to_speak_with_brukk', next: "ravla_rust_brukk" },
                { text: "I am a big fan of machines and rust. Some of my best friends are rust machines.", key: 'i_am_a_big_fan_of_machines_and_rust_some_of_my_bes', next: "ravla_rust_fan" },
                { text: "Nevermind.", key: 'nevermind', next: "ravla_start" }
                ]
            },
            ravla_rust_join: {
                text: "Joining the Rust Choir isn't a decision to be taken lightly. You have to prove your dedication to our cause. Are you sure you're up to the task?",
                options: [
                { text: "Yes, I'm ready.", key: 'yes_im_ready', next: "ravla_rust_task" },
                { text: "On second thought, maybe not.", key: 'on_second_thought_maybe_not', next: "ravla_start" }
                ]
            },
            ravla_rust_brukk: {
                text: "Oh, really? That might be a problem. Not many people can speak with Brukk directly. If you have something important to discuss, I can arrange a meeting. It's possible. But first you have to prove you're trustworthy and do something for the Rust Choir first.",
                options: [
                { text: "What do you need me to do?", key: 'what_do_you_need_me_to_do', next: "ravla_rust_task" },
                { text: "I see. Maybe another time.", key: 'i_see_maybe_another_time', next: "ravla_start" }
                ]
            },
            ravla_rust_fan: {
                text: "Ha, I like that spirit! The Rust Choir does appreciate sense of humor and those who understand the beauty of decay and machinery. But joking won't get you in. You'll need to prove your commitment. I have a small test for you, if you're serious about this.",
                options: [
                { text: "How can I prove my commitment?", key: 'how_can_i_prove_my_commitment', next: "ravla_rust_task" },
                { text: "I've changed my mind. Maybe another time.", key: 'ive_changed_my_mind_maybe_another_time', next: "ravla_start" }
                ]
            },
            ravla_rust_task: {
                text: "There's a small matter that needs attending to. You want to meet Brukk? Then feed the metal first. The machines are always hungry, go and prepare a feast for them. You will need oil, metal, and, most importantly, a redmass. Mix them together, bring it to me, and I'll arrange your meeting with Brukk.",
                options: [
                    { text: "I'll get to work on it.", key: 'ill_get_to_work_on_it', next: "closeDialog" },
                    { text: "What is a redmass?", key: 'what_is_a_redmass', next: "ravla_rust_cluster" },
                    { text: "Where can I find the metal and oil?", key: 'where_can_i_find_the_metal_and_oil', next: "ravla_rust_materials" },
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('find_rust_choir', 'Ravla at the Screaming Cork wants me to prepare a feast for the Rust Choir machines to prove your commitment. I have to gather oil, metal, and a redmass, and bring them to her.', 'talked_to_ravla');
                    this.showNotification('Quest updated: Finding the Rust Choir');
                    this.questSystem.addQuest('rust_feast', 'Rust Feast', 'Prepare a feast for the Rust Choir machines by gathering oil, metal, and a living redmass, and bring them to Ravla at the Screaming Cork.');
                },
            },
            ravla_rust_cluster: {
                text: "A living redmass is a rare organism that thrives in decaying metal environments. It's semi-organic mass of oxidized iron tendrils, like coral made of blood-colored steel.",
                options: [
                    { text: "Where can I find it?", key: 'where_can_i_find_it', next: "ravla_cluster_where" },
                    { text: "Where can I find the metal and oil?", key: 'where_can_i_find_the_metal_and_oil', next: "ravla_rust_materials" },
                    { text: "I'll get to work on it.", key: 'ill_get_to_work_on_it', next: "closeDialog" },
                ]
            },
            ravla_cluster_where: {
                text: "Well, I cannot do everything for you, can I? This is a test, after all. Ahh... very well. I won't tell you directly, but go to talk to the weird archeologist who hangs around the townhall. He seems to know a lot about strange organisms. Maybe he can help you find what you're looking for.",
                options: [
                    { text: "Thanks for the tip. I'll get to work on it.", key: 'thanks_for_the_tip_ill_get_to_work_on_it', next: "closeDialog" },
                    { text: "Where can I find the metal and oil?", key: 'where_can_i_find_the_metal_and_oil', next: "ravla_rust_materials" },
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('rust_feast', 'Ravla suggested I speak with the archeologist near the townhall to learn more about redmass.', 'talked_to_archeologist_hint');
                }
            },
            ravla_rust_materials: {
                text: "I'm not your mother, am I? Figure it out. The city is full of scrap metal and oil leaks. Use your head. You can search around the Scraper or you can even buy metal scraps from the traders, you know. In exchange for money, heard about that concept? For the oil, I would check the Yolk Sea docks or Echo Drain Delta. Good luck.",
                options: [
                    { text: "Thanks for the advice. I'll get to work on it.", key: 'thanks_for_the_advice_ill_get_to_work_on_it', next: "closeDialog" },
                    { text: "Wait, what about the redmass? What is that?", key: 'wait_what_about_the_redmass_what_is_that', next: "ravla_rust_cluster" },
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('rust_feast', 'Ravla advised me to search around the Scraper for scrap metal (or I can simply buy it) and check the Yolk Sea docks or Echo Drain Delta for oil.', 'gathered_rust_materials_hint');
                }
            },

            // --- Rust Feast delivery ---
            ravla_feast_missing: {
                text: "Then don't waste my time. Come back when you have the oil, scrap metal, and a redmass. All three.",
                options: [
                    { text: "I'll keep looking.", key: 'ill_keep_looking', next: "closeDialog" }
                ]
            },
            ravla_feast_full_redmass: {
                text: `Ravla's eyes go wide as she takes the redmass from your hands. It twitches. She grins — a slow, satisfied thing. "Now THIS is redmass. Still alive. Still... present." She leans in, almost reverently. "The machines will feast well tonight. You've done good, pilgrim. Better than I expected."`,
                options: [
                    { text: "When do we begin?", key: 'when_do_we_begin', next: "ravla_feast_cook_full" }
                ]
            },
            ravla_feast_shard: {
                text: `Ravla squints at the small crystalline shard, turning it in her fingers. "...This is it? A bit of gristle scraped from the bone?" She sets it down carefully. A long pause. "...It's warm. It's alive, just barely." She exhales. "It's not much. But the machines haven't eaten in a long time. It will have to be enough."`,
                options: [
                    { text: "It was given willingly.", key: 'it_was_given_willingly', next: "ravla_feast_cook_shard" },
                    { text: "It's all I could get.", key: 'its_all_i_could_get', next: "ravla_feast_cook_shard" }
                ]
            },
            ravla_feast_cook_full: {
                text: `Ravla works quickly — oil first, then metal shavings, and finally the redmass folded in last, still twitching. The result is sealed in a dark container that rattles faintly. "There. The Rust Feast." She slides it across the table. "And for your trouble — the password to Lift Mother. Say 'Corrode' to the panel. Don't share it." She fixes you with a look that makes clear this is not a suggestion.`,
                options: [{ text: "I won't. Thank you, Ravla.", next: "closeDialog" }],
                onTrigger: () => {
                    this.removeItemFromInventory('oil');
                    this.removeItemFromInventory('metal_scrap');
                    this.removeItemFromInventory('redmass');
                    if (!this.hasItem('rust_feast')) {
                        this.addItemToInventory({
                            id: 'rust_feast',
                            name: 'Rust Feast',
                            description: 'A ceremonial meal prepared for the Rust Choir machines. A foul-smelling concoction of oil, metal shavings, and living redmass. The container rattles faintly, as if something inside is still alive.',
                            image: 'rust_feast',
                            stackable: false
                        });
                    }
                    this.modifyFactionReputation('RustChoir', 15);
                    this.questSystem.completeQuest('rust_feast');
                    const findQuest = this.questSystem.getQuest('find_rust_choir');
                    if (findQuest && !findQuest.isComplete) {
                        this.questSystem.updateQuest('find_rust_choir', 'The Rust Feast is complete. Ravla gave me the password for Lift Mother: "Corrode". I can now access the Rust Choir domain.', 'feast_complete');
                    }
                    this.addJournalEntry(
                        'rust_feast_completed_full',
                        'Rust Feast Prepared',
                        'Ravla prepared the Rust Feast with the living redmass I brought. She was greatly pleased. My standing with the Rust Choir improved significantly. She gave me the password for Lift Mother: "Corrode".',
                        this.journalSystem.categories.EVENTS
                    );
                }
            },
            ravla_feast_cook_shard: {
                text: `Ravla prepares the feast in silence — oil, metal dust, and the small shard eased in last. The container is sealed. She doesn't look at you. "Feast is done. Don't expect gratitude." She pushes it across the table. "Password for Lift Mother: 'Corrode'. Now get out." A pause. "...The machines will drink tonight. You did what you could."`,
                options: [{ text: "Thank you, Ravla.", next: "closeDialog" }],
                onTrigger: () => {
                    this.removeItemFromInventory('oil');
                    this.removeItemFromInventory('metal_scrap');
                    this.removeItemFromInventory('redmass');
                    if (!this.hasItem('rust_feast')) {
                        this.addItemToInventory({
                            id: 'rust_feast',
                            name: 'Rust Feast',
                            description: "A ceremonial meal prepared for the Rust Choir machines. Thin, barely adequate — a small shard of redmass mixed with oil and metal dust. It hums softly.",
                            image: 'rust_feast',
                            stackable: false
                        });
                    }
                    this.modifyFactionReputation('RustChoir', 5);
                    this.questSystem.completeQuest('rust_feast');
                    const findQuest = this.questSystem.getQuest('find_rust_choir');
                    if (findQuest && !findQuest.isComplete) {
                        this.questSystem.updateQuest('find_rust_choir', 'The Rust Feast is complete, though the offering was meager. Ravla gave me the password for Lift Mother: "Corrode".', 'feast_complete');
                    }
                    this.addJournalEntry(
                        'rust_feast_completed_shard',
                        'Rust Feast Prepared (Meager)',
                        "Ravla prepared the Rust Feast with the redmass shard I brought. She wasn't impressed, but it was enough. My standing with the Rust Choir improved slightly. She gave me the password for Lift Mother: \"Corrode\".",
                        this.journalSystem.categories.EVENTS
                    );
                }
            },
            ravla_feast_illusion: {
                text: `You focus inward, calling on Ulvarex. The air shimmers. Between your fingers, a shape coalesces — red, wet, twitching. It looks exactly like a living redmass. Ravla's eyes lock onto it. "Well, well. You actually found one." She takes it from you without hesitation, turning it over. "Still warm. Still breathing." She doesn't notice the faint shimmer at its edges, the way the light bends just slightly wrong.`,
                options: [
                    { text: "Let's prepare the feast.", key: 'lets_prepare_the_feast', next: "ravla_feast_cook_illusion" }
                ]
            },
            ravla_feast_cook_illusion: {
                text: `Ravla works with practiced hands — oil, metal shavings, and the illusory redmass folded in last. It holds its shape perfectly. Even you almost believe it's real. The result is sealed in a dark container. "There. The Rust Feast." She slides it across the table. "And the password to Lift Mother — say 'Corrode' to the panel." She fixes you with a look. "Don't share it."\n\nSomewhere deep inside you, Ulvarex pulses with quiet satisfaction. The deception was flawless. But you can't shake the feeling that illusions, however perfect, are not meant to feed machines.`,
                options: [{ text: "I won't. Thank you, Ravla.", next: "closeDialog" }],
                onTrigger: () => {
                    this.removeItemFromInventory('oil');
                    this.removeItemFromInventory('metal_scrap');
                    this.registry.set('rust_feast_illusory', true);
                    if (!this.hasItem('rust_feast')) {
                        this.addItemToInventory({
                            id: 'rust_feast',
                            name: 'Rust Feast',
                            description: 'A ceremonial meal prepared for the Rust Choir machines. Oil, metal shavings, and what appears to be living redmass — but you know the truth. The container hums faintly, but something feels hollow.',
                            image: 'rust_feast',
                            stackable: false
                        });
                    }
                    this.modifyFactionReputation('RustChoir', 10);
                    this.questSystem.completeQuest('rust_feast');
                    const findQuest = this.questSystem.getQuest('find_rust_choir');
                    if (findQuest && !findQuest.isComplete) {
                        this.questSystem.updateQuest('find_rust_choir', 'The Rust Feast is complete — though the redmass was an illusion woven by Ulvarex. Ravla gave me the password for Lift Mother: "Corrode".', 'feast_complete');
                    }
                    this.addJournalEntry(
                        'rust_feast_completed_illusion',
                        'Rust Feast Prepared (Illusory Redmass)',
                        'I used Ulvarex\'s Mirage Weave to create an illusion of redmass, fooling Ravla completely. The feast was prepared with false ingredients. Ravla gave me the password for Lift Mother: "Corrode". But illusions cannot truly feed machines — there may be consequences.',
                        this.journalSystem.categories.EVENTS
                    );
                }
            },
            ravla_feast_spared_redmass: {
                text: `Ravla's expression goes very still. Then: "You. Found a living redmass. And you left it there." She sets down her tools with deliberate care. "The machines are hungry. The feast was meant to prove you understand what the Rust Choir does — what WE do. Decay is not cruelty. It is process." Her eyes are cold. "Go back. Take the redmass. Or do not come back at all."`,
                options: [{ text: "I understand.", next: "closeDialog" }],
                onTrigger: () => {
                    this.modifyFactionReputation('RustChoir', -5);
                    this.addJournalEntry(
                        'ravla_feast_refused_spared',
                        'Ravla Refused — Redmass Spared',
                        'Ravla was furious that I spared the redmass. She told me to go back and take it, or not return. My standing with the Rust Choir has decreased.',
                        this.journalSystem.categories.EVENTS
                    );
                }
            },
            ravla_feast_done: {
                text: `Ravla glances up. "The feast is done. The machines have eaten." She returns to her work. "You have the password. Focus on what's next."`,
                options: [{ text: "Right.", next: "closeDialog" }]
            },

            // Heliodor dialog
            heliodor_start: {
                speaker: 'Heliodor',
                text: "Heliodor nods politely. \"Welcome to the Screaming Cork. First time? The name's a bit misleading - it's actually quite peaceful most nights.\"",
                options: [
                    { text: "Who are you?", key: 'who_are_you', next: "heliodor_who" },
                    { text: "Tell me about this place", key: 'tell_me_about_this_place', next: "heliodor_place" },
                    { text: "Heard any rumors lately?", key: 'heard_any_rumors_lately', next: "heliodor_rumors" },
                    ...(knowsSulkberries && !sulkberriesClearedHeliodor ? [{ text: "I need a biological opinion on some Sulkberries.", key: 'i_need_a_biological_opinion_on_some_sulkberries', next: "heliodor_sulkberry_check" }] : []),
                    {
                      text: "Do you have anything for sale?",
                      key: 'do_you_have_anything_for_sale',
                      next: 'openShop'
                    },
                ]
            },
            // --- Sulkberry biological check (Dead End investigation) ---
            heliodor_sulkberry_check: {
                speaker: 'Heliodor',
                text: `Several of Heliodor's component organisms lean forward in sequence — first the eyes narrow, then the nostrils flare, then fingers that seem to belong to a different personality reach out and accept the berry sample.\n\nA long pause. Various parts of Heliodor's composite body confer in whispered clicks and hums.\n\n"We have examined the specimen. Three of our components have tasted, two have analyzed the spore residue, and Oorarabaz — briefly roused — confirmed the alkaloid structure through membrane absorption.\n\nThe berry is clean. No toxins, no modifications, no parasitic interference. This is a Lumen Directorate premium product in perfect condition."`,
                options: [
                    ...(nemeCanRead
                        ? [{ text: "[Photosentience] Read Heliodor's bio-signals for deception.", key: 'photosentience_read_heliodors_biosignals_for_decep', next: "heliodor_sulkberry_neme" }]
                        : (hasNeme ? [{ text: "[Photosentience] Try to read Heliodor… (your sense gutters)", key: 'photosentience_silenced_heliodor', next: "heliodor_sulkberry_neme_silenced" }] : [])),
                    { text: "Thank you. That's very thorough.", key: 'thank_you_thats_very_thorough', next: "heliodor_start" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('sulkberries_cleared_heliodor')) {
                        this.addJournalEntry(
                            'sulkberries_cleared_heliodor',
                            'Heliodor: Sulkberries Are Clean',
                            'Heliodor\'s composite organisms performed a multi-sensory biological analysis of the Sulkberries. Multiple components tasted, analyzed spore residue, and confirmed the alkaloid structure. The berries are clean — no toxins, no modifications, no parasitic interference.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Heliodor' }
                        );
                    }
                    if (this.questSystem?.getQuest('who_killed_bishop') && !this.questSystem.getQuest('who_killed_bishop').isComplete) {
                        this.questSystem.updateQuest('who_killed_bishop', 'Heliodor\'s composite organisms confirmed the Sulkberries are clean — no toxins or modifications. The Sulkberry lead is a dead end.', 'heliodor_sulkberry_clear');
                    }
                }
            },

            heliodor_sulkberry_neme: {
                speaker: 'Heliodor',
                text: `You extend Neme's awareness toward Heliodor — and immediately receive a cascade of overlapping signals. Not one mind but many, each broadcasting its own emotional frequency. Professional competence from the analytical components. Mild irritation from those awakened for the task. A deep, hibernating satisfaction from something that must be Oorarabaz, already drifting back to sleep.\n\nBut across all of them, one constant: no deception. A colony cannot lie in unison — each component's truth reinforces the others.\n\nNeme observes: "A chorus of honesty. Refreshing, if somewhat noisy."\n\nHeliodor's verdict is genuine. The Sulkberries are clean.`,
                options: [
                    { text: "Thank you, Heliodor.", key: 'thank_you_heliodor', next: "heliodor_start" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('sulkberries_neme_heliodor')) {
                        this.addJournalEntry(
                            'sulkberries_neme_heliodor',
                            'Neme Confirms: Heliodor Is Truthful',
                            'Used Neme\'s Photosentience on Heliodor\'s composite colony. Multiple overlapping bio-signals, all honest — a colony cannot lie in unison. The Sulkberry analysis is genuine.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Heliodor' }
                        );
                    }
                }
            },

            heliodor_sulkberry_neme_silenced: {
                speaker: 'Neme',
                text: `You reach for Neme's sight — and it slides away like a hand closing on smoke. *"Not here,"* Neme manages, faint and far off. *"There is too much rot in this air; I am nearly asleep. I cannot read him for you. Trust your own ears this time."* The bio-signals blur into meaningless noise.`,
                options: [
                    { text: "Understood.", key: 'neme_silenced_ok', next: "heliodor_sulkberry_check" }
                ]
            },

            heliodor_who: {
                text: "We are Heliodor. We keep an eye on things here, make sure everyone behaves.",
                options: [
                    { text: "We?", key: 'we', next: "heliodor_explain" },
                    { text: "Back", key: 'back', next: "heliodor_start" }
                ]
            },
            heliodor_explain: {
                text: "Yes, we. We are a colony of multiple creatures. But we identify as Heliodor *Donjon* Vaalstran for simplicity's sake. It's easier for introductions. Our body is made up of a whole community of creatures living in perfect symbiosis, which is advantageous for working behind the bar for several reasons. Each symbiont has its own talents, so some specialize in communicating with guests, others cook or mix drinks, and still others take care of the pub's operations. Another advantage is that we work in shifts, so while some are working, others are sleeping, so no one is too tired, even on hectic weekends. An extreme example is Oorarabaz the Green-faced, a rare type of organism originally endemic to the Nettle Mountains, similar to thick green moss, which sleeps practically all year round and is usually only woken up to do the company's financial statements.", 
                options: [
                    { text: "Fascinating. But I have other questions.", key: 'fascinating_but_i_have_other_questions', next: "heliodor_start" }
                ],
                onTrigger: () => {
                    // Add a lore entry about Heliodor to the player's journal
                    if (!this.hasJournalEntry('heliodor_lore')) {
                        this.addJournalEntry(
                        'heliodor_lore', 
                        'Heliodor *Donjon* Vaalstran',
                        'Heliodor is a unique individual composed of multiple symbiotic creatures living in harmony. They manage the Screaming Cork with a blend of talents from their various components, making them an efficient and intriguing bartender.',
                        this.journalSystem.categories.PEOPLE
                        );     
                    }
                },
            },
            heliodor_place: {
                text: "The Screaming Cork's been here longer than most of the city. Owner claims it was the first building erected after the Collapse. Doubt that's true, but it's certainly old. Good place to disappear for a while.",
                options: [
                    { text: "Back", key: 'back', next: "heliodor_start" }
                ]
            },
            heliodor_rumors: {
                text: "Hmm. Word is the Rust Choir minions are getting more aggressive with their territory. And there's something strange happening at the Cathedral.",
                options: [
                    { text: "Anything else?", key: 'anything_else', next: "heliodor_more_rumors" },
                    { text: "Back", key: 'back', next: "heliodor_start" }
                ]
            },
            heliodor_more_rumors: {
                text: "Well, if you're interested in less savory information... that woman in the corner, Ravla? She's the best document forger in the district. Just don't tell her I told you.",
                options: [
                    { text: "Thanks for the tip", key: 'thanks_for_the_tip', next: "heliodor_start" }
                ],
                onTrigger: () => {
                    // Add a hint about Ravla to any relevant quests
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem) {
                        const quest = questSystem.getQuest('ortolan_arms');
                        if (quest && !quest.updates.some(update => update.key === 'ravla_forger_hint')) {
                            questSystem.updateQuest('ortolan_arms', 'Heliodor at the Screaming Cork mentioned that Ravla is a skilled document forger. She might be able to help with the Ortolan situation.', 'ravla_forger_hint');
                            this.showNotification('Quest updated: Ortolan Arms Investigation');
                        }
                    }
                }
            },
            openShop: {
                text: "Take your time browsing. Quality goods at fair prices!",
                options: [
                    {
                        text: "[Open Shop Interface]",
                        key: 'open_shop_interface',
                        next: 'shopInterface'
                    },
                    {
                        text: "Actually, nevermind.",
                        key: 'actually_nevermind',
                        next: 'closeDialog'
                    }
                ]
            },
            shopInterface: {
                text: "",
                options: [],
                onShow: () => {
                    this.hideDialog();
                    if (this.shopSystem) {
                        this.shopSystem.open();
                    }
                }
            },
            heliodorMerchandise: {
                text: "I have connections with traders from all over. Some items come from distant lands, others from local craftsmen. I pride myself on offering only the finest goods.",
                options: [
                    {
                        text: "Show me what you have for sale.",
                        key: 'show_me_what_you_have_for_sale',
                        next: 'openShop'
                    },
                    {
                        text: "I'll come back later.",
                        key: 'ill_come_back_later',
                        next: 'closeDialog'
                    }
                ]
            },
        };
    }

    preload() {
        super.preload();
        this.load.image('screamingCorkInteriorBg', 'assets/images/backgrounds/ScreamingCorkInterior.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        this.load.image('redmass', 'assets/images/items/redmass.png');
        this.load.image('rust_feast', 'assets/images/items/rust_feast.png');
        
        // Load NPC sprites as static images first to ensure they exist
        this.load.image('ravla_static', 'assets/images/characters/ravla.png');
        this.load.image('heliodor_static', 'assets/images/characters/heliodor.png');
        this.load.image('fungal_master', 'assets/images/characters/fungal_master.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set background
        const bg = this.add.image(400, 300, 'screamingCorkInteriorBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Position the priest at the entrance
        this.priest.x = 100;
        this.priest.y = 470;
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);

        // Finale epilogue: a scripted cutscene (Thaal walks in), not the normal tavern.
        // Skip the usual exits and NPCs so the player can't wander off.
        if (this.registry.get('epilogue_mode')) {
            this.startEpilogueCutscene();
            return;
        }

        // Create exit back to ScreamingCorkScene at the left edge
        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            80, // width
            200, // height
            'left', // direction
            'ScreamingCorkScene', // target scene
            50, // walk to x
            470 // walk to y
        );
        
        // Create entrance to the club area (at the back of the tavern)
        this.transitionManager.createTransitionZone(
            650, // x position - back of the tavern
            350, // y position
            100, // width
            150, // height
            'up', // direction
            'ScreamingCorkClubScene', // target scene
            400, // walk to x - position inside the club
            520, // walk to y
            'Enter Club Area' // custom name
        );
        
        if (!this.hasJournalEntry('screaming_cork_place')) {
            this.addJournalEntry(
                'screaming_cork_place',
                'The Screaming Cork',
                "A tavern said to be the first building raised after the Collapse — old, dim, and a good place to disappear. Heliodor tends the bar as many creatures wearing a single name; Ravla forges papers in the corner; and somewhere past the back room a band called Feral Toast rehearses something that isn't quite music.",
                this.journalSystem.categories.PLACES,
                { location: 'Screaming Cork' }
            );
        }

        // Create NPCs
        this.createNPCs();
    }

    /**
     * Finale epilogue cutscene: the apprentice waits at the bar; Master Thaal walks in from
     * the side; once he reaches his place, the closing dialog opens.
     */
    startEpilogueCutscene() {
        // Apprentice, settled at the bar.
        this.priest.x = 300;
        this.priest.y = 470;
        if (this.priestGlow) { this.priestGlow.x = this.priest.x; this.priestGlow.y = this.priest.y; }

        // Master Thaal enters from the right (fungal_master image + green fungal glow).
        const startX = 860, endX = 470, y = 470;
        const thaal = this.add.image(startX, y, 'fungal_master').setScale(0.15).setDepth(6);
        const glow = this.add.image(startX, y, 'fungal_master').setScale(0.155).setTint(0x00ff00).setAlpha(0.3).setDepth(5);
        glow.setBlendMode(Phaser.BlendModes.ADD);
        this.tweens.add({ targets: glow, alpha: 0.5, duration: 1500, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });

        this.time.delayedCall(900, () => {
            this.tweens.add({
                targets: [thaal, glow],
                x: endX,
                duration: 2600,
                ease: 'Sine.easeInOut',
                onComplete: () => {
                    // Settle: a gentle breathing idle, then open the dialog.
                    this.tweens.add({ targets: thaal, scaleX: 0.153, scaleY: 0.153, duration: 2000, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
                    this.time.delayedCall(450, () => this.showDialog('epilogue_intro'));
                }
            });
        });
    }

    /** End the epilogue and roll the credits (the real game-over). */
    rollCredits() {
        if (this._creditsStarted) return;
        this._creditsStarted = true;
        this.registry.set('epilogue_mode', false);
        this.registry.set('game_finale_complete', true);
        this.cameras.main.fadeOut(1400, 0, 0, 0);
        this.time.delayedCall(1500, () => {
            this.scene.start('CreditsScene', { ending: this.registry.get('finale_ending') || null });
        });
    }

    createNPCs() {
        // Create Ravla NPC (the forger) using static image
        this.ravla = this.add.image(700, 470, 'ravla_static');
        this.ravla.setScale(0.125); // Further reduced scale to make sprite more proportional
        this.ravla.setDepth(5);
        this.ravla.setInteractive({ useHandCursor: true });
        
        // Create Heliodor NPC using static image
        this.heliodor = this.add.image(300, 470, 'heliodor_static');
        this.heliodor.setScale(0.125); // Further reduced scale to make sprite more proportional
        this.heliodor.setDepth(5);
        this.heliodor.setInteractive({ useHandCursor: true });
        
        // Initialize shop system
        this.initShopSystem();
        
        // Add dialog interactions
        this.ravla.on('pointerdown', () => {
            if (this.dialogVisible) return;
            this.showDialog('ravla_start');
        });
        
        this.heliodor.on('pointerdown', () => {
            if (this.dialogVisible) return;
            this.showDialog('heliodor_start');
        });
        
        // Add simple movement for NPCs
        this.addNPCMovement();
    }
    
    // We're using static images instead of animations for now
    createNPCAnimations() {
        // No animations needed as we're using static images
    }
    
    addNPCMovement() {
        // Ravla subtle wobble animation
        this.addWobbleEffect(this.ravla, 600, 450);
        
        // Heliodor subtle wobble animation
        this.addWobbleEffect(this.heliodor, 400, 430);
    }
    
    addWobbleEffect(sprite, baseX, baseY) {
        // Create a very subtle wobble effect
        this.tweens.add({
            targets: sprite,
            y: { from: baseY - 1, to: baseY + 1 },
            ease: 'Sine.easeInOut',
            duration: 1500,
            yoyo: true,
            repeat: -1
        });
        
        // Add a very slight rotation wobble
        this.tweens.add({
            targets: sprite,
            angle: { from: -1, to: 1 },
            ease: 'Sine.easeInOut',
            duration: 2000,
            yoyo: true,
            repeat: -1,
            delay: 5000 // Offset from the y-wobble for more natural movement
        });
    }

    update() {
        super.update();
        
        // Update money display if needed
        if (this.shopSystem && this.shopSystem.isOpen) {
            this.shopSystem.updateMoneyDisplay();
        }
    }
    
    // Helper method to add an item to inventory
    addItemToInventory(item) {
        const inventory = this.registry.get('inventory') || { items: [] };
        
        // Check if the item already exists (for stackable items)
        const existingItemIndex = inventory.items.findIndex(i => i.id === item.id);
        
        if (existingItemIndex !== -1 && item.stackable) {
            // Increment count for stackable items
            inventory.items[existingItemIndex].count = (inventory.items[existingItemIndex].count || 1) + (item.count || 1);
        } else {
            // Add new item
            inventory.items.push(item);
        }
        
        // Update inventory in registry
        this.registry.set('inventory', inventory);
    }
    
    /**
     * Initialize the shop system with inventory
     */
    initShopSystem() {
        // Sample shop inventory
        const shopInventory = [
            {
                id: 'pliers',
                name: 'Pliers',
                description: 'A pair of pliers. Useful for repairing or extracting.',
                price: 25,
                type: 'tool',
            },

        ];
        
        // Create shop system
        this.shopSystem = new ShopSystem(this, {
            shopName: 'Screaming Cork Shop',
            inventory: shopInventory,
            position: {
                x: 400,
                y: 300
            },
            buyMultiplier: 1.0,
            sellMultiplier: 0.5
        });
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.ScreamingCorkInteriorScene = ScreamingCorkInteriorScene;
}
