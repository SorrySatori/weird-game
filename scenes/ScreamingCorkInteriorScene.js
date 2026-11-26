import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import ShopSystem from '../systems/items/ShopSystem.js';
import { DEMO_BUILD } from '../config/build.js';
import { canWeave, spendWeave } from '../utils/ulvarexEncounter.js';

/** Spores for Ulvarex's mirage inspector of the Ink Tribunal (anchored in the real seal Ravla copies from) */
const AUDIT_COST = 10;

export default class ScreamingCorkInteriorScene extends GameScene {
    constructor() {
        super({ key: 'ScreamingCorkInteriorScene' });
        this.isTransitioning = false;
        this.shopSystem = null;
    }

    /**
     * Heliodor can only be asked about the Fermented Cap once the player has heard of it: Thaal's excuse in
     * EntryScene's whyNot (recorded as a dialog topic 'topic:EntryScene:<option>>whyNot' by
     * GameScene._dialogOptionTopic) or the last line of his equipment tutorial (onceFlag 'heard_fermented_cap').
     */
    heardOfFermentedCap() {
        if ((this.registry.get('onceFlags') || []).includes('heard_fermented_cap')) return true;
        const used = this.usedDialogOptions || new Map(this.registry.get('usedDialogOptions') || []);
        return [...used.keys()].some(k => typeof k === 'string' && k.startsWith('topic:EntryScene:') && k.endsWith('>whyNot'));
    }

    get dialogContent() {
        const hasFindRustQuest = (this.questSystem && this.questSystem.getQuest('find_rust_choir') && !this.questSystem.getQuest('find_rust_choir').isComplete && this.questSystem.getQuest('find_rust_choir').updates.some(update => update.key === 'talk_to_ravla'));
        const hasRustFeastQuest = !!(this.questSystem && this.questSystem.getQuest('rust_feast') && !this.questSystem.getQuest('rust_feast').isComplete);
        // where "I'll get to work on it" leads: in the demo, once, to Ravla's aside that the feast can't be made here yet
        const rustTaskDone = DEMO_BUILD && !this.questSystem?.getQuest('rust_feast')?.updates?.some(u => u.key === 'demo_not_yet')
            ? 'ravla_rust_demo' : 'closeDialog';

        // Ulvarex: an inspector of the Ink Tribunal woven at Ravla's elbow shows her the flaws in her "perfect" forgery
        // (Growth: her clients won't be caught with botched papers). Any time once the player knows she forges (her own
        // words or Heliodor's tip). While Ortolan's arms quest runs it's his permit: before she's paid she redoes it for
        // free, after, she gives the fifty back. Otherwise a sample from her pile, and she swears to redo the year's work.
        const ortolanOpen = !!this.questSystem?.getQuest('ortolan_arms') && !this.questSystem.getQuest('ortolan_arms').isComplete;
        const knowsForger = !!this.journalSystem?.hasFact('met_ravla', 'forger')
            || !!this.questSystem?.getQuest('ortolan_arms')?.updates?.some(u => ['ravla_forger_hint', 'ravla_forger_agreement'].includes(u.key));
        const audited = !!(this.journalSystem?.hasFact('met_ravla', 'audit') || this.journalSystem?.hasFact('met_ravla', 'audit_sample'));
        // (from her first menu only once he knows what she does; in the talk about Ortolan's permit she has just said it)
        const canAudit = !audited && canWeave(this, AUDIT_COST);
        const permitBought = ortolanOpen && !!(this.hasItem && this.hasItem('forged-arms-permission'));
        const auditFromStart = canAudit && (knowsForger || permitBought);

        const content = {
            ...super.dialogContent,

            // Ravla dialog - the forger
            ravla_start: {
                moodNpc: 'ravla',
                text: "Ravla looks up from her work, eyes sharp and calculating. \"Need something? I'm busy, so make it quick.\"",
                options: [
                    { text: "Who are you?", key: 'who_are_you', next: "ravla_who" },
                    { text: "What do you do here?", key: 'what_do_you_do_here', next: "ravla_job" },
                    ...(hasFindRustQuest ? [{ text: "I was told you can get me to Rust Choir base.", key: 'i_was_told_you_can_get_me_to_rust_choir_base', next: "ravla_rust_domain" }] : []),
                    ...(hasRustFeastQuest ? [{ text: "I'm still gathering the feast ingredients.", key: 'im_still_gathering_the_feast_ingredients', next: "ravla_feast_missing" }] : []),
                    ...(auditFromStart && permitBought ? [{ text: "[Ulvarex] About that perfect permit. Let's have it inspected.", key: 'ravla_ulvarex_inspect', next: "ravla_audit" }] : []),
                    ...(auditFromStart && ortolanOpen && !permitBought ? [{ text: "[Ulvarex] About Ortolan's permit. First let an inspector look at your work.", key: 'ravla_ulvarex_audit_start', next: "ravla_audit" }] : []),
                    ...(auditFromStart && !ortolanOpen ? [{ text: "[Ulvarex] Let's see how good your work really is.", key: 'ravla_ulvarex_audit_any', next: "ravla_audit" }] : [])
                ]
            },
            ravla_who: {
                text: "Name's Ravla. I'm an... artist of sorts. Been at the Cork a couple thousand digestions now. It's quiet, keeps the authorities at a distance.",
                options: [
                    { text: "Ask something else", key: 'back', next: "ravla_start" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('met_ravla')) {
                        this.addJournalEntry(
                            'met_ravla',
                            'Ravla',
                            "Ravla keeps a corner of the Screaming Cork and calls herself an artist of sorts. She likes it there: it's quiet, and the authorities keep their distance. Sharp-eyed, unsentimental, and unmoved by charm.",
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Ravla', location: 'Screaming Cork' }
                        );
                    }
                }
            },
            ravla_job: {
                text: "I provide services for those who need their paperwork adjusted. Nothing illegal, of course. Just creative interpretations of bureaucratic necessities.",
                onTrigger: () => {
                    this.addJournalFact('met_ravla', 'forger', "She forges documents: papers for anyone who can pay, no questions asked.");
                    this.addJournalFact('screaming_cork_place', 'ravla', "The woman in the corner is Ravla, and she forges papers.");
                },
                options: [
                    { text: "I need some documents...", key: 'i_need_some_documents', next: "ravla_documents" },
                    { text: "Ask something else", key: 'back', next: "ravla_start" }
                ]
            },
            ravla_documents: {
                text: "Hmm. What kind of documents are we talking about? I don't work for free, and I don't work for just anyone.",
                options: [
                    { text: "Just curious", key: 'just_curious', next: "ravla_curious" },
                    ...(this.registry.get('questSystem')?.getQuest('ortolan_arms')
                        && (this.registry.get('questSystem').getQuest('ortolan_arms').updates.some(update => ['forge_documents_suggestion', 'ravla_forger_hint'].includes(update.key))
                            || this.journalSystem?.hasFact('met_ravla', 'forger'))
                        && !this.registry.get('questSystem').getQuest('ortolan_arms').isComplete && !this.hasItem('forged-arms-permission') ? [
                        { text: "I need help with Ortolan's paperwork", key: 'i_need_help_with_ortolans_paperwork', next: "ravla_ortolan" }
                    ] : []),
                    { text: "Ask something else", key: 'back', next: "ravla_start" }
                ]
            },
            ravla_curious: {
                text: "Curiosity is expensive in this city. Come back when you have real business.",
                options: [
                    { text: "Ask something else", key: 'back', next: "ravla_start" }
                ]
            },
            ravla_ortolan: {
                text: "Ortolan? The game designer? Let me guess: the arms. That takes an Artisan's Exemption Form, and those have special seals that are hard to duplicate. But… I might be able to help.",
                options: [
                    { text: "What would you need?", key: 'what_would_you_need', next: "ravla_ortolan_need" },
                    { text: "Ask something else", key: 'back', next: "ravla_start" }
                ]
            },
            ravla_ortolan_need: {
                text: "It won't be cheap: 50 dinars. But I can make it perfect. No one would know the difference.",
                options: [
                    { text: "Here's the money", key: 'heres_the_money', next: "ravla_check_money" },
                    ...(canAudit && ortolanOpen && !permitBought ? [{ text: "[Ulvarex] Perfect? Let an inspector be the judge of that.", key: 'ravla_ulvarex_audit', next: "ravla_audit" }] : []),
                    { text: "I'll think about it", key: 'ill_think_about_it', next: "ravla_ortolan_agree" },
                    { text: "That's too expensive", key: 'thats_too_expensive', next: "ravla_start" }
                ]
            },
            ravla_check_money: {
                hideCloseOption: true,      // (its own way out is enough: no second "I should go")
                text: "",
                options: [],
                onShow: () => {
                    // Check if player has enough money
                    if (this.hasEnoughMoney(50)) {
                        this.subtractMoney(50);
                        
                        // Add forged document to inventory
                        this.addItemToInventory({
                            id: 'forged-arms-permission',
                            name: "Forged Multiple Arms Permission",
                            description: "A convincing forgery of an Artisan's Exemption Form that would allow the bearer to legally possess multiple arms for specialized work.",
                            stackable: false
                        });
                        
                        // Update quest
                        const questSystem = this.registry.get('questSystem');
                        if (questSystem) {
                            questSystem.updateQuest('ortolan_arms', "I got a forged permit for Ortolan's extra arms from Ravla. Now I just need to get it to him.", 'document_obtained');
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
                hideCloseOption: true,      // (its own way out is enough: no second "I should go")
                text: "Here you go. Perfect forgery, trust me. The official seals, the watermarks, even the special ink. All perfect. No one will question this. Just don't tell anyone where you got it.",
                options: [
                    { text: "Thank you", key: 'thank_you', next: "closeDialog" }
                ]
            },
            ravla_audit: {
                speaker: 'Narrator',
                hideCloseOption: true,
                textKey: permitBought ? 'bought' : 'sample',
                text: "You let Ulvarex focus on the seal Ravla keeps on her desk to copy from. By the desk an inspector of the Ink Tribunal takes shape: grey cuffs, ink up to the wrists, a loupe screwed into one eye. Without a word he "
                    + (permitBought ? "takes Ortolan's permit from your hand" : "picks up a sample permit from her pile") + " and holds it to the lamp.\n\n\"The cogwheel on this seal has eleven teeth. The real one has twelve,\" he says. \"The fish in the watermark swims upstream; ours have swum downstream since the reform. And this ink smells of beetroot.\" He lays the paper down and comes apart in a puff of orange light.",
                options: [
                    { text: "Watch Ravla.", key: 'ravla_audit_watch', next: "ravla_audit_shaken" }
                ],
                onTrigger: () => {
                    if (this._auditWoven) return;   // (the spores go once per weave)
                    this._auditWoven = true;
                    this._auditForOrtolan = ortolanOpen;
                    this._auditRefund = permitBought;
                    spendWeave(this, AUDIT_COST);
                }
            },
            ravla_audit_shaken: {
                hideCloseOption: true,      // (its own way out is enough: no second "I should go")
                speaker: 'Ravla',
                textKey: !this._auditForOrtolan ? 'humbled' : this._auditRefund ? 'refund' : 'free',
                text: "Ravla stares at the empty air where the inspector stood, then at the paper. She picks the real seal up off her desk and counts the teeth under her breath. Then she counts them again.\n\n\"Twelve,\" she says at last, very quietly. \"All these years I've been doing this.\" She doesn't look at you. \"That was you, wasn't it? Some trick. Doesn't matter. He was right.\" She sweeps the paper into the stove and pulls out a clean form. "
                    + (!this._auditForOrtolan
                        ? "\"Everything I've sold this year comes back across this desk and gets done again. Properly.\" Only now does she look at you. \"And not a word about this to the Rust Choir.\""
                        : this._auditRefund
                        ? "\"Ortolan gets a new one, done properly. And here's your fifty back. I don't take money for botched work.\""
                        : "\"Ortolan's permit gets done properly. And this one's on the house.\""),
                options: [
                    { text: "Thank you, Ravla.", key: 'ravla_audit_thanks', next: "closeDialog" }
                ],
                onTrigger: () => {
                    if (!this._auditWoven) return;
                    this._auditWoven = false;
                    if (this.journalSystem?.hasFact('met_ravla', 'audit') || this.journalSystem?.hasFact('met_ravla', 'audit_sample')) return;
                    this.gdChoiceOnce('ulvarex_ravla_audit', 2, 0);
                    // she knows she was tricked, even if she can't say how
                    if (this.registry.get('factionSystem')) this.modifyFactionReputation('RustChoir', -5);
                    if (!this._auditForOrtolan) {
                        this.addJournalFact('met_ravla', 'audit_sample', "Ulvarex wove an inspector of the Ink Tribunal, who found three flaws in one of Ravla's forgeries. Ravla went quiet and swore to redo everything she has sold this year.");
                        return;
                    }
                    const refund = this._auditRefund;
                    if (refund) {
                        this.removeItemFromInventory('forged-arms-permission');
                        this.addMoney(50);
                    }
                    this.addItemToInventory({
                        id: 'forged-arms-permission',
                        name: "Forged Multiple Arms Permission",
                        description: "A flawless forgery of an Artisan's Exemption Form. Ravla redid it after an \"inspection\": twelve teeth on the seal, the watermark fish swimming the right way.",
                        variant: 'audited',
                        stackable: false
                    });
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem && !questSystem.getQuest('ortolan_arms')?.updates?.some(u => u.key === 'document_obtained')) {
                        questSystem.updateQuest('ortolan_arms', "I got a forged permit for Ortolan's extra arms from Ravla. Now I just need to get it to him.", 'document_obtained');
                    }
                    this.addJournalFact('met_ravla', 'audit', "Ulvarex conjured an illusion of an Ink Tribunal inspector, who found three flaws in Ravla's \"perfect\" forgery. Ravla went quiet, then redid Ortolan's permit properly and wouldn't take my money for it.");
                }
            },
            ravla_not_enough_money: {
                hideCloseOption: true,      // (its own way out is enough: no second "I should go")
                text: "What are you trying to pull? You don't have 50 dinars. Come back when you have the money. I don't work for free.",
                options: [
                    { text: "Sorry, I'll be back", key: 'sorry_ill_be_back', next: "closeDialog" }
                ]
            },
            ravla_ortolan_agree: {
                hideCloseOption: true,      // (its own way out is enough: no second "I should go")
                text: "Good. Bring the money, and I'll have it ready in no time. Just don't tell anyone where you got it.",
                options: [
                    { text: "Deal", key: 'deal', next: "closeDialog" }
                ],
                onTrigger: () => {
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem) {
                        questSystem.updateQuest('ortolan_arms', 'Ravla at the Screaming Cork can forge the Artisan\'s Exemption Form for Ortolan, but she wants 50 dinars for the job.', 'ravla_forger_agreement');
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
            // DEMO_BUILD: the docks, the Delta and the rest of the task's places aren't in the demo -- Ravla says so, in character,
            // and the quest log keeps it; the task itself stays as a teaser for the full game
            ravla_rust_demo: {
                hideCloseOption: true,      // (its own way out is enough: no second "I should go")
                text: "*Ravla leans in and lowers her voice.* \"One more thing, just between us. The places you'd need for this (the docks, the Delta and a few more besides) aren't on any map yet. Not in this version of the city. A demo, they call it. I've forged a lot of things in my life, but I can't forge you a whole district.\" *She shrugs.* \"Keep the task anyway. When they finish building the rest of the city, come back. The Choir will be waiting, and Brukk never forgets a volunteer.\"",
                options: [
                    { text: "I'll hold you to that.", key: 'ill_hold_you_to_that', next: "closeDialog" }
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('rust_feast', "Ravla admitted the places I'd need for the feast aren't part of this demo yet. The Rust Choir will have to wait for the full game. Brukk never forgets a volunteer, she says.", 'demo_not_yet');
                }
            },
            ravla_rust_task: {
                hideCloseOption: true,      // (its own way out is enough: no second "I should go")
                text: "There's a small matter that needs attending to. You want to meet Brukk? Then feed the metal first. The machines are always hungry, go and prepare a feast for them. You will need oil, metal, and, most importantly, a redmass. Mix them together, bring it to me, and I'll arrange your meeting with Brukk.",
                options: [
                    { text: "I'll get to work on it.", key: 'ill_get_to_work_on_it', next: rustTaskDone },
                ],
                onTrigger: () => {
                    this.addJournalFact('met_ravla', 'rust_choir', "She speaks for the Rust Choir: nobody gets to Brukk or the machines without going through her, and she wants proof of loyalty first.");
                    this.questSystem.updateQuest('find_rust_choir', 'Ravla at the Screaming Cork wants me to prepare a feast for the Rust Choir machines to prove my commitment. I have to gather oil, metal, and a redmass, and bring them to her.', 'talked_to_ravla');
                    this.questSystem.addQuest('rust_feast', 'Rust Feast', 'Prepare a feast for the Rust Choir machines by gathering oil, metal, and a living redmass, and bring them to Ravla at the Screaming Cork.');
                },
            },

            // --- Rust Feast delivery ---
            ravla_feast_missing: {
                hideCloseOption: true,      // (its own way out is enough: no second "I should go")
                text: "Then don't waste my time. Come back when you have the oil, scrap metal, and a redmass. All three.",
                options: [
                    { text: "I'll keep looking.", key: 'ill_keep_looking', next: "closeDialog" }
                ]
            },

            // Heliodor dialog
            // the first conversation ever gets the welcome; every later one (this visit or another) a "back again"
            // (_heliodorGreeting is decided when he is clicked, so the hub keeps one text through a conversation)
            heliodor_start: {
                speaker: 'Heliodor',
                textKey: this._heliodorGreeting === 'return' ? 'return' : 'first',
                text: this._heliodorGreeting === 'return'
                    ? "Heliodor nods politely. \"Back again? Sit wherever you like. Most of us remember you.\""
                    : "Heliodor nods politely. \"Welcome to the Screaming Cork. First time? The name's a bit misleading. It's actually quite peaceful most nights.\"",
                options: [
                    { text: "Who are you?", key: 'who_are_you', next: "heliodor_who" },
                    { text: "Tell me about this place", key: 'tell_me_about_this_place', next: "heliodor_place" },
                    { text: "Heard any rumors lately?", key: 'heard_any_rumors_lately', next: "heliodor_rumors" },
                    { text: "What's that noise next door?", key: 'whats_that_noise_next_door', next: "heliodor_noise" },
                    // only once the name has come up (Thaal's excuse or his tutorial): heardOfFermentedCap
                    ...(this.heardOfFermentedCap() ? [
                        { text: "Do you know where the Fermented Cap tavern is?", key: 'do_you_know_where_the_fermented_cap_is', next: "heliodor_fermented_cap" }
                    ] : []),
                    {
                      text: "Do you have anything for sale?",
                      key: 'do_you_have_anything_for_sale',
                      next: 'heliodorMerchandise'
                    },
                ]
            },
            heliodor_who: {
                text: "We are Heliodor. We keep an eye on things here, make sure everyone behaves.",
                options: [
                    { text: "We?", key: 'we', next: "heliodor_explain" },
                    { text: "Ask something else", key: 'back', next: "heliodor_start" }
                ]
            },
            heliodor_explain: {
                text: "Yes, we. We are a colony of multiple creatures. But we identify as Heliodor *Donjon* Vaalstran for simplicity's sake. It's easier for introductions. Our body is made up of a whole community of creatures living in perfect symbiosis, which is advantageous for working behind the bar for several reasons. Each symbiont has its own talents, so some specialize in communicating with guests, others cook or mix drinks, and still others take care of the pub's operations. Another advantage is that we work in shifts, so while some are working, others are sleeping, so no one is too tired, even on hectic weekends. An extreme example is Oorarabaz the Green-faced, a rare type of organism originally endemic to the Nettle Mountains, similar to thick green moss, which sleeps practically all year round and is usually only woken up to do the company's financial statements.", 
                options: [
                    { text: "Fascinating. But I have other questions.", key: 'fascinating_but_i_have_other_questions', next: "heliodor_start" }
                ],
                onTrigger: () => {
                    this.addJournalFact('screaming_cork_place', 'heliodor', "The barkeep is Heliodor: many creatures wearing a single name.");
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
                text: "The Screaming Cork's been here longer than most of the city. Owner claims it was the first building erected after the Collapse. We doubt that's true, but it's certainly old. Good place to disappear for a while.",
                options: [
                    { text: "Ask something else", key: 'back', next: "heliodor_start" }
                ],
                onTrigger: () => {
                    this.addJournalFact('screaming_cork_place', 'oldest', "Its owner claims it was the first building raised after the Collapse. Heliodor doubts it, but the place is certainly old. A good place to disappear for a while.");
                }
            },
            // the muffled rehearsal heard through the wall (tavernRehearsal, see create())
            heliodor_noise: {
                text: "*Several of Heliodor's faces wince at once.* \"That's Feral Toast, rehearsing in the club out back for tonight's concert. They call it ultranoise futurepunk. We call it the reason our glasses keep walking off the shelves. Go and have a listen if you like. The door's at the back.\"",
                options: [
                    { text: "Ask something else", key: 'back', next: "heliodor_start" }
                ],
                onTrigger: () => {
                    this.addJournalFact('screaming_cork_place', 'feral_toast', "The band out back is called Feral Toast.");
                }
            },
            // Master Thaal's excuse in EntryScene ("a prior engagement at the Fermented Cap tavern")
            heliodor_fermented_cap: {
                text: "\"The Fermented Cap?\" *A low murmur passes through the colony as it confers with itself.* \"No. There's no such tavern. We know every bar, pub and back-room dive in this district. Half of us used to work in them. If somebody told you they'd be there, they most likely just wanted to be rid of you.\"",
                options: [
                    { text: "Ask something else", key: 'back', next: "heliodor_start" }
                ]
            },
            heliodor_rumors: {
                text: "Hmm. Word is the Rust Choir minions are getting more aggressive with their territory. And there's something strange happening at the Cathedral.",
                options: [
                    { text: "Anything else?", key: 'anything_else', next: "heliodor_more_rumors" },
                    { text: "Ask something else", key: 'back', next: "heliodor_start" }
                ]
            },
            heliodor_more_rumors: {
                text: "Well, if you're interested in less savory information... that woman in the corner, Ravla? She's the best document forger in the district. Just don't tell her we told you.",
                options: [
                    { text: "Thanks for the tip", key: 'thanks_for_the_tip', next: "heliodor_start" }
                ],
                onTrigger: () => {
                    this.addJournalFact('met_ravla', 'forger', "She forges documents: papers for anyone who can pay, no questions asked.");
                    this.addJournalFact('screaming_cork_place', 'ravla', "The woman in the corner is Ravla, and she forges papers.");
                    // Add a hint about Ravla to any relevant quests
                    const questSystem = this.registry.get('questSystem');
                    if (questSystem) {
                        const quest = questSystem.getQuest('ortolan_arms');
                        if (quest && !quest.updates.some(update => update.key === 'ravla_forger_hint')) {
                            questSystem.updateQuest('ortolan_arms', 'Heliodor at the Screaming Cork mentioned that Ravla is a skilled document forger. She might be able to help with the Ortolan situation.', 'ravla_forger_hint');
                        }
                    }
                }
            },
            openShop: {
                hideCloseOption: true,      // (its own way out is enough: no second "I should go")
                text: "Take your time browsing. Quality goods at fair prices!",
                options: [
                    {
                        text: "[Open Shop Interface]",
                        key: 'open_shop_interface',
                        next: 'shopInterface'
                    },
                    {
                        text: "Actually, never mind.",
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
                hideCloseOption: true,      // (its own way out is enough: no second "I should go")
                text: "We have connections with traders from all over. Some items come from distant lands, others from local craftsmen. We pride ourselves on offering only the finest goods.",
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
        // Explicit speaker per state: GameScene's fallback would label every Heliodor sub-state "Ravla".
        for (const [key, state] of Object.entries(content)) {
            if (!state || typeof state !== 'object' || state.speaker) continue;
            if (key.startsWith('ravla')) state.speaker = 'Ravla';
            else if (key.startsWith('heliodor') || key === 'openShop' || key === 'shopInterface') state.speaker = 'Heliodor';
        }
        return content;
    }

    preload() {
        super.preload();
        this.load.image('screamingCorkInteriorBg', 'assets/images/backgrounds/ScreamingCorkInterior.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        
        // what stands nearer than Heliodor (the counter, its stools) -- drawn over him (tools/artgen/corkin_bg.py)
        this.load.image('screamingCorkCounter', 'assets/images/backgrounds/ScreamingCorkInterior_counter.png');
        // the people: 8-frame idle sheets -- Heliodor from his old art (tools/artgen/corkfolk.py), Ravla redrawn at her
        // crate desk (tools/artgen/ravla.py); Aseprite sources Cork_<id>
        this.load.spritesheet('heliodor', 'assets/images/characters/heliodor_idle.png', { frameWidth: 128, frameHeight: 192 });
        this.load.spritesheet('ravla', 'assets/images/characters/ravla_idle.png', { frameWidth: 128, frameHeight: 144 });
        // Feral Toast rehearsing in the club, heard through the wall (muffled + room echo baked in)
        this.load.audio('tavernRehearsal', 'assets/sounds/tavern-rehearsal.mp3');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set background
        const bg = this.add.image(400, 300, 'screamingCorkInteriorBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        // The background paints its own floor; drop the generic ground strip
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }
        // The counter in front of Heliodor (between him at depth 5 and anyone walking along it)
        this.add.image(0, 0, 'screamingCorkCounter').setOrigin(0, 0).setDepth(5.5);
        
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

        // The band keeps rehearsing while you're away: coming back picks the take up where it would be
        this.playSceneMusic('tavernRehearsal', { resume: true });

        // Exits (canvas coords): the front door on the left (open, light behind it) and the red-lit doorway at the back
        // that leads down to the club; both light up whole
        this.transitionManager.createDoorZone({ points: [[38, 350], [128, 340], [132, 472], [38, 476]] }, {
            target: 'ScreamingCorkScene', walkX: 67, walkY: 470, label: 'Outside', direction: 'left'
        });
        this.transitionManager.createDoorZone({ rect: [816, 322, 66, 126] }, {
            target: 'ScreamingCorkClubScene', walkX: 848, walkY: 470, label: 'Into the Club'
        });
        
        if (!this.hasJournalEntry('screaming_cork_place')) {
            this.addJournalEntry(
                'screaming_cork_place',
                'The Screaming Cork',
                "An old, dim tavern. A many-faced figure tends the bar, a woman works at a desk in the corner, and from somewhere past the back room comes a band rehearsing something that isn't quite music.",
                this.journalSystem.categories.PLACES,
                { location: 'Screaming Cork' }
            );
        }

        // Create NPCs
        this.createNPCs();
    }

    createNPCs() {
        // Ravla (the forger) sits at a crate in the right corner, her tentacle holding a lantern over her work;
        // the crate's foot is 3 px above the frame's bottom
        this.ravla = this.add.sprite(960, 524, 'ravla', 0).setOrigin(0.5, 1).setDepth(6);
        this.addGroundShadow(966, 520, 100, 14);
        this.ravla.setInteractive({ useHandCursor: true });

        // Heliodor stands on the raised boards behind the counter, before the curtained doorway
        // (the counter overlay covers him from the waist down)
        this.heliodor = this.add.sprite(this.scale.width / 2, 492, 'heliodor', 0).setOrigin(0.5, 1).setDepth(5);
        this.heliodor.setInteractive({ useHandCursor: true });

        // idle loops, slow: Heliodor's colony (tools/artgen/heliodor.py) -- the Mixer's claw shakes (0-1), the tentacle turns
        // the glass (2), the Speaker blinks (3), Oorarabaz breathes in his sleep (4), the shift changes (5-6: the pocket
        // creature wakes, the Mixer's eyestalks sink) and Oorarabaz cracks an eye (7); Ravla writes a word (0-1-7), breathes and the
        // lantern drifts (6), dips the quill (2-3) and glances up at you with a blink (4-5)
        if (!this.anims.exists('heliodor_idle')) {
            this.anims.create({
                key: 'heliodor_idle',
                frames: this.anims.generateFrameNumbers('heliodor', { frames: [0, 1, 0, 1, 0, 1, 0, 0, 2, 2, 0, 0, 3, 0, 0, 4, 4, 4, 0, 1, 0, 1, 0, 0, 5, 5, 6, 6, 6, 6, 5, 0, 0, 2, 2, 0, 7, 7, 7, 0] }),
                frameRate: 4,
                repeat: -1
            });
        }
        if (!this.anims.exists('ravla_idle')) {
            this.anims.create({
                key: 'ravla_idle',
                frames: this.anims.generateFrameNumbers('ravla', { frames: [0, 1, 7, 0, 1, 7, 6, 6, 0, 1, 7, 0, 2, 3, 3, 2, 0, 1, 7, 0, 1, 7, 0, 6, 6, 4, 4, 4, 5, 4, 4, 0] }),
                frameRate: 4,
                repeat: -1
            });
        }
        this.heliodor.play('heliodor_idle');
        this.ravla.play('ravla_idle');
        this.dialogPortraits = { ...(this.dialogPortraits || {}),
            'Heliodor': { key: 'heliodor', frame: 0, zoom: 2, top: 24 },
            'Ravla': { key: 'ravla', frame: 4, zoom: 2, top: 28 } };
        
        // Initialize shop system
        this.initShopSystem();
        
        // Add dialog interactions
        this.ravla.on('pointerdown', () => {
            if (this.dialogVisible) return;
            this.showDialog('ravla_start');
        });
        
        this.heliodor.on('pointerdown', () => {
            if (this.dialogVisible) return;
            // "First time?" only in the very first conversation with him (heliodor_start)
            this._heliodorGreeting = (this.registry.get('onceFlags') || []).includes('heliodor_greeted') ? 'return' : 'first';
            this.onceEver('heliodor_greeted', () => {});
            this.showDialog('heliodor_start');
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
        if (this.inventorySystem) return super.addItemToInventory(item);
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
            shopKey: 'cork',
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
