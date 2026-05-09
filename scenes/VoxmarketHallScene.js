import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class VoxmarketHallScene extends GameScene {
    constructor() {
        super({ key: 'VoxmarketHallScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        const hasThorne = !!this.symbiontSystem?.hasSymbiont('thorne-still');
        const hasNeme = !!this.symbiontSystem?.hasSymbiont('neme-crownmire');
        const hasUlvarex = !!this.symbiontSystem?.hasSymbiont('ulvarex-borrowed-horizon');
        const hasAuctionErrand = !!this.hasJournalEntry('seldo_auction_errand');
        const metTwins = !!this.hasJournalEntry('met_hesh_vell');
        const metCalyx = !!this.hasJournalEntry('met_sister_calyx');
        const metLune = !!this.hasJournalEntry('met_heartbroker_lune');
        const confusedTwins = !!this.hasJournalEntry('twins_brain_rot');
        const calyxRattled = !!this.hasJournalEntry('calyx_rattled');
        const calyxLieDetected = !!this.hasJournalEntry('calyx_lie_detected');
        const calyxMiraged = !!this.hasJournalEntry('calyx_miraged');
        const luneMisled = !!this.hasJournalEntry('lune_wrong_context');
        const luneExposed = !!this.hasJournalEntry('lune_true_value');
        const twinsStartTextKey = metTwins
            ? (confusedTwins ? 'twins_start_confused_return' : 'twins_start_return')
            : 'twins_start_first';
        const twinsToadletTextKey = confusedTwins
            ? 'twins_toadlet_confused'
            : 'twins_toadlet_normal';
        const calyxStartTextKey = metCalyx
            ? (calyxRattled ? 'calyx_start_rattled_return' : 'calyx_start_return')
            : 'calyx_start_first';
        const luneStartTextKey = luneExposed
            ? 'lune_start_exposed'
            : (luneMisled
                ? 'lune_start_misled'
                : (metLune ? 'lune_start_return' : 'lune_start_first'));

        return {
            ...super.dialogContent,

            // ——— Hesh & Vell, the Twin Auctioneers ———
            twins_start: {
                speaker: 'Hesh & Vell',
                textKey: twinsStartTextKey,
                text: metTwins
                    ? (confusedTwins
                        ? `"Welcome... back," says Hesh. Vell mouths the words a half-second late, but stumbles — the rhythm is off, the synchronization cracked. "The auction will... begin shortly," Hesh continues, and Vell's lips catch up too late.\n\nThey're still functional, but their famous pacing is compromised. The auctioneer's edge — dulled."`
                        : `"Welcome back," says Hesh. Vell mouths the same words half a second late, their lips forming each syllable in eerie delay. "The auction will begin shortly. Browse. Socialize. The lots are displayed along the far wall."`)
                    : `"Welcome to the Voxmarket Auction Hall," says Hesh — or is it Vell? One speaks, the other mouths the same words half a second behind, creating an unsettling echo effect without any actual echo.\n\n"I am Hesh," says the one on the left. "And I am Vell," mouths the one on the right, a beat too late. "We conduct the auction. All sales are final. All bids are binding. All regrets are your own."\n\nTheir synchronization is hypnotic — practiced, precise, and deeply wrong.`,
                options: [
                    { text: "How does the auction work?", key: 'how_does_the_auction_work', next: "twins_auction_rules" },
                    { text: "What's being auctioned today?", key: 'whats_being_auctioned_today', next: "twins_lots" },
                    ...(hasAuctionErrand ? [{ text: "I'm here for a specific lot — a Chrono-Slurry Toadlet.", key: 'im_here_for_a_specific_lot_a_chronoslurry_toadlet', next: "twins_toadlet" }] : []),
                    { text: "Why do you do that — the delayed mouthing?", key: 'why_do_you_do_that_the_delayed_mouthing', next: "twins_echo" },
                    ...(hasThorne && !confusedTwins ? [{ text: "[Brain Rot] Disrupt their synchronization.", key: 'brain_rot_disrupt_their_synchronization', next: "twins_brain_rot" }] : []),
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('met_hesh_vell')) {
                        this.addJournalEntry(
                            'met_hesh_vell',
                            'The Twin Auctioneers: Hesh & Vell',
                            'Met the twin auctioneers at the Voxmarket Auction Hall. One speaks, the other mouths the same words half a second late. Their synchronization is unsettling and precise — and likely deliberate. They run the auction together.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Hesh & Vell' }
                        );
                    }
                }
            },

            twins_auction_rules: {
                speaker: 'Hesh & Vell',
                text: `"The rules are simple," says Hesh. Vell's lips follow. "Lots are presented one by one. Bidding starts at the listed price. Raise your hand to bid. Highest bidder when we call 'Settled' wins the lot.\n\nPayment is immediate. Gold only — no barter, no vestigels, no promises. If you can't pay, you leave. If you cause a scene, you leave faster.\n\nThe pre-auction social period is just as important. Know your competition. Make friends. Or make them nervous."`,
                options: [
                    { text: "What's being auctioned today?", key: 'whats_being_auctioned_today', next: "twins_lots" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "twins_start" },
                ]
            },

            twins_lots: {
                speaker: 'Hesh & Vell',
                text: `"Today's lots include," Hesh begins, and Vell's delayed echo makes the list sound like a chant:\n\n"A jar of Compressed Nostalgia — memories of a place that never existed. Starting at 30 gold.\n\nOne Chrono-Slurry Toadlet — prophetic amphibian, three-minute foresight window. Starting at 60 gold.\n\nA set of Self-Sharpening Bureaucratic Quills — they fill in the correct answer on any official form. Starting at 45 gold.\n\nA Brine Scripture membrane — dormant symbiont tissue preserved in mineral saline. Starting price pending verification.\n\nAnd the evening's centerpiece: a Fossilized Dream Egg from the Cathedral excavation. Starting at 120 gold."\n\nVell finally catches up and both twins smile simultaneously. That part, at least, is perfectly synchronized.`,
                options: [
                    ...(hasAuctionErrand ? [{ text: "Tell me more about the Chrono-Slurry Toadlet.", key: 'tell_me_more_about_the_chronoslurry_toadlet', next: "twins_toadlet" }] : []),
                    { text: "Interesting selection. I'll look around first.", key: 'interesting_selection_ill_look_around_first', next: "closeDialog" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "twins_start" },
                ]
            },

            twins_toadlet: {
                speaker: 'Hesh & Vell',
                textKey: twinsToadletTextKey,
                text: confusedTwins
                    ? `"The Toadlet, yes," Hesh says. Vell's mouth moves but the timing is wrong — too early, then too late, then skipping words entirely. "Starting bid is... forty gold." Hesh frowns briefly, as if the number surprised even them. "It's a... popular lot. Several interested parties."\n\nTheir usual rhythm is broken. The price they quoted is lower than the listed amount — their pacing manipulation isn't working properly.`
                    : `"Ah, the Toadlet," says Hesh with practiced interest. Vell's lips form the words with theatrical precision. "A fine specimen. Three minutes of perfect foresight upon lingual contact. Very popular with bureaucrats, gamblers, and the chronically indecisive.\n\nStarting bid: 60 gold. But expect competition — we have at least two serious bidders already registered. The final price... well." Both twins smile. "That depends on the room."`,
                options: [
                    { text: "Who else is bidding on it?", key: 'who_else_is_bidding_on_it', next: "twins_competitors" },
                    { text: "I'll be ready when bidding starts.", key: 'ill_be_ready_when_bidding_starts', next: "closeDialog" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "twins_start" },
                ]
            },

            twins_competitors: {
                speaker: 'Hesh & Vell',
                text: `"We don't disclose bidder identities before the auction," says Hesh. Vell mouths along, but one eye drifts toward the far corner of the room — toward Sister Calyx.\n\n"However," Hesh continues, "the pre-auction social period exists for a reason. Observe. Introduce yourself. Draw your own conclusions about who wants what.\n\nThe auction rewards preparation as much as wealth."`,
                options: [
                    { text: "Understood. I'll mingle.", key: 'understood_ill_mingle', next: "closeDialog" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "twins_start" },
                ]
            },

            twins_echo: {
                speaker: 'Hesh & Vell',
                text: `"Do what?" says Hesh. Vell mouths "Do what?" precisely on delay. They look at each other — Hesh with a slight smirk, Vell with the ghost of the same smirk half a second later.\n\n"We've always been like this," Hesh says. "Born half a second apart. Lived half a second apart. Will probably die half a second apart. It's not an affectation — it's a condition.\n\nAlso, it makes our auction pacing impossible to interrupt. By the time you've processed what I've said, Vell has already reinforced it. Very effective for driving up bids."`,
                options: [
                    { text: "That's... honestly unsettling.", key: 'thats_honestly_unsettling', next: "twins_unsettling" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "twins_start" },
                ]
            },

            twins_unsettling: {
                speaker: 'Hesh & Vell',
                text: `"Thank you," they say — and for once, perfectly in unison. Then the delay resumes.\n\n"Unsettling is good for business," Hesh adds. "A nervous bidder is a generous bidder."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "twins_start" },
                ]
            },

            twins_brain_rot: {
                speaker: 'Hesh & Vell',
                text: `You reach inward and let Thorne-Still's decay seep outward — a subtle pulse of cognitive rot, targeted at the twin auctioneers' famous synchronization.\n\nThe effect is immediate. Vell's delayed echo stutters — mouthing the wrong words, then the right ones too early, then freezing entirely. Hesh keeps talking but glances sideways, visibly disturbed. For a moment, they're just two people standing next to each other. The hypnotic rhythm is broken.\n\n"I... excuse us," Hesh says. Vell mouths something entirely different. They retreat behind their podium, recalibrating.\n\nWhen the auction begins, their pacing — and their price manipulation — will be compromised.`,
                options: [],
                hideCloseOption: true,
                onTrigger: () => {
                    this.addJournalEntry(
                        'twins_brain_rot',
                        'Disrupted the Twin Auctioneers',
                        'Used Thorne-Still\'s Brain Rot to break the synchronization between Hesh and Vell. Their coordinated pacing — which they use to subtly inflate bid prices — is now compromised. This should lower the final auction prices.',
                        this.journalSystem.categories.EVENTS,
                        { character: 'Hesh & Vell' }
                    );
                    this.showNotification('Thorne-Still disrupted the twins\' synchronization.');
                    return 'twins_brain_rot_after';
                }
            },

            twins_brain_rot_after: {
                speaker: 'Hesh & Vell',
                text: `Hesh straightens up behind the podium, but the damage is done. Vell's mouthing is off by a full second now — sometimes two. The invisible rhythm that drives their auction pacing has been cracked.\n\n"We're fine," Hesh insists. Vell mouths "We're fine" far too late, contradicting the statement entirely.`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "twins_start" },
                ]
            },

            // ——— Sister Calyx of the Pith Reclaimers ———
            calyx_start: {
                speaker: 'Sister Calyx',
                textKey: calyxStartTextKey,
                text: metCalyx
                    ? (calyxRattled
                        ? `Sister Calyx stands rigidly, her composure cracked. She eyes you with visible wariness. "You again. I hope you're here to browse, not to... continue our earlier conversation."`
                        : `"Back again," Sister Calyx says, adjusting a small vial at her belt. "The auction draws all sorts. I'm here for Pith Reclaimer business — nothing more."`)
                    : `A tall woman in layered grey-green robes stands near the auction lots, examining them with clinical precision. Fungal filaments are woven into her vestments like silver thread, and her fingers end in faintly discolored nails — the mark of prolonged pith extraction work.\n\n"Sister Calyx," she says, noticing your approach. "Pith Reclaimers. I'm here on chapter business. And you are...?"`,
                options: [
                    { text: "Just browsing. What are the Pith Reclaimers?", key: 'just_browsing_what_are_the_pith_reclaimers', next: "calyx_pith" },
                    { text: "What are you bidding on?", key: 'what_are_you_bidding_on', next: "calyx_bidding" },
                    ...(hasAuctionErrand ? [{ text: "I'm here for the Chrono-Slurry Toadlet.", key: 'im_here_for_the_chronoslurry_toadlet', next: "calyx_toadlet_rival" }] : []),
                    ...(hasNeme && !calyxLieDetected ? [{ text: "[Photosentience] Read her bio-signals.", key: 'photosentience_read_her_biosignals', next: "calyx_neme" }] : []),
                    ...(hasUlvarex && !calyxMiraged ? [{ text: "[Mirage Weave] Create a distraction.", key: 'mirage_weave_create_a_distraction', next: "calyx_mirage" }] : []),
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('met_sister_calyx')) {
                        this.addJournalEntry(
                            'met_sister_calyx',
                            'Sister Calyx — Pith Reclaimers',
                            'Met Sister Calyx of the Pith Reclaimers at the Voxmarket Auction Hall. She\'s here on chapter business, examining the lots with clinical precision. Fungal filaments are woven into her vestments.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Sister Calyx' }
                        );
                    }
                }
            },

            calyx_pith: {
                speaker: 'Sister Calyx',
                text: `"The Pith Reclaimers extract fungal essence — pith — from living organisms. We refine it, study it, trade it. The Directorate calls us 'parasites,' the Rust Choir calls us 'thieves.' We call ourselves practical.\n\nEvery living thing in this city carries harvestable essence. We simply... collect what's already being wasted. The cathedral's eggs, the spore fields, even the city's living walls — all sources of raw pith.\n\nOur chapter here in Upper Morkezela is small but well-funded. Hence my presence at this auction."`,
                options: [
                    { text: "What are you bidding on?", key: 'what_are_you_bidding_on', next: "calyx_bidding" },
                    { text: "Essence extraction sounds invasive.", key: 'essence_extraction_sounds_invasive', next: "calyx_ethics" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "calyx_start" },
                ]
            },

            calyx_ethics: {
                speaker: 'Sister Calyx',
                text: `"Invasive?" She adjusts her fungal-threaded cuff. "Is it invasive when you breathe? You inhale spores with every breath. We simply do it with intention and precision.\n\nThe Lumen Directorate grows things and pretends they're natural. The Rust Choir lets things decay and calls it sacred. We extract what's useful and call it honest.\n\nBut I didn't come here to debate philosophy. I came here to bid."`,
                options: [
                    { text: "What are you bidding on?", key: 'what_are_you_bidding_on', next: "calyx_bidding" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "calyx_start" },
                ]
            },

            calyx_bidding: {
                speaker: 'Sister Calyx',
                text: `"The Fossilized Dream Egg, primarily. Cathedral artifacts carry concentrated pith — decades of accumulated essence compressed into stone. Our chapter could study it for years.\n\nBut I have secondary interest in the Chrono-Slurry Toadlet as well. Prophetic amphibians produce a unique pith signature when their foresight activates. Very valuable for our temporal extraction research.\n\nI have a budget of 150 gold. I intend to use it strategically."`,
                options: [
                    ...(hasAuctionErrand ? [{ text: "The Toadlet is mine. I'm bidding on it too.", key: 'the_toadlet_is_mine_im_bidding_on_it_too', next: "calyx_toadlet_rival" }] : []),
                    { text: "That's a serious budget.", key: 'thats_a_serious_budget', next: "calyx_budget" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "calyx_start" },
                ]
            },

            calyx_toadlet_rival: {
                speaker: 'Sister Calyx',
                text: `She narrows her eyes. "You want the Toadlet? Interesting. It's not exactly a casual purchase — prophetic amphibians require specialized care. Or do you just want to lick it and peer three minutes ahead like everyone else?\n\nI won't pretend I'll step aside. The chapter needs that pith signature. But the Dream Egg is my priority — if the Toadlet drives too high, I may have to choose.\n\nUnless you can convince me the Toadlet isn't worth my gold."`,
                options: [
                    { text: "What would convince you to drop the Toadlet bid?", key: 'what_would_convince_you_to_drop_the_toadlet_bid', next: "calyx_negotiate" },
                    { text: "May the best bidder win.", key: 'may_the_best_bidder_win', next: "calyx_challenge" },
                    ...(hasThorne ? [{ text: "[Brain Rot] Confuse her about which lot she wanted.", key: 'brain_rot_confuse_her_about_which_lot_she_wanted', next: "calyx_thorne" }] : []),
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "calyx_start" },
                ]
            },

            calyx_negotiate: {
                speaker: 'Sister Calyx',
                text: `"Convince me?" She crosses her arms, fungal threads catching the light. "The chapter sent me for pith sources. I need to return with something that justifies the travel costs.\n\nIf the Dream Egg goes for a reasonable price, I could focus my budget there and leave the Toadlet to you. But if someone drives the Egg too high, I'll pivot to the Toadlet as a secondary acquisition.\n\nSo your best strategy is to make sure I get the Dream Egg cheaply. Don't bid on it. Don't let anyone else drive it up. And I'll stay away from your amphibian."`,
                options: [
                    { text: "So we have an understanding — I avoid the Egg, you avoid the Toadlet.", key: 'so_we_have_an_understanding_i_avoid_the_egg_you_av', next: "calyx_deal" },
                    { text: "No promises. I'll bid as I see fit.", key: 'no_promises_ill_bid_as_i_see_fit', next: "calyx_no_deal" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "calyx_start" },
                ]
            },

            calyx_deal: {
                speaker: 'Sister Calyx',
                text: `"An understanding. Not a deal — the Pith Reclaimers don't make deals with strangers at auctions. But... an understanding. Yes.\n\nI'll focus on the Dream Egg. You focus on the Toadlet. And neither of us drives up the other's target. Efficient. Practical. Very Reclaimer of you."\n\nShe offers the faintest nod — acknowledgment, not warmth.`,
                options: [],
                onTrigger: () => {
                    this.addJournalEntry(
                        'calyx_truce',
                        'Arrangement with Sister Calyx',
                        'Reached an understanding with Sister Calyx of the Pith Reclaimers — she\'ll focus on the Dream Egg and leave the Chrono-Slurry Toadlet to me, as long as I don\'t drive up the Egg\'s price. Not a binding deal, but a practical arrangement.',
                        this.journalSystem.categories.EVENTS,
                        { character: 'Sister Calyx' }
                    );
                    this.showNotification('Reached an understanding with Sister Calyx.');
                }
            },

            calyx_no_deal: {
                speaker: 'Sister Calyx',
                text: `"Suit yourself. But don't be surprised when the bidding gets... energetic. The Pith Reclaimers don't lose auctions we've budgeted for.\n\nMay your pockets be deeper than your stubbornness."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "calyx_start" },
                ]
            },

            calyx_challenge: {
                speaker: 'Sister Calyx',
                text: `"May the best bidder win," she repeats, and her smile has edges. "I intend to. The Pith Reclaimers don't attend auctions for sport.\n\nBut the social period isn't over yet. There's still time to be persuasive — or to make mistakes."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "calyx_start" },
                ]
            },

            calyx_budget: {
                speaker: 'Sister Calyx',
                text: `"The chapter doesn't fund half-measures. When we identify a pith source worth acquiring, we acquire it. 150 gold is modest by Reclaimer standards — some chapters send delegations with ten times that.\n\nBut Upper Morkezela is a small chapter. We're... cautious with allocations. Which is why I need to bid strategically, not emotionally."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "calyx_start" },
                ]
            },

            // --- Symbiont interactions with Calyx ---
            calyx_neme: {
                speaker: 'Sister Calyx',
                text: `You let Neme's perception unfurl — tendrils of bio-awareness reaching toward Sister Calyx. Her signals bloom into focus: discipline, calculation, a carefully maintained facade of calm.\n\nBut underneath — anxiety. She's under pressure from her chapter. The budget is tight, tighter than she's letting on. And there's something else: she doesn't actually want the Toadlet for pith research. She wants it for herself. The temporal extraction story is cover.\n\nNeme whispers: "She reclaims from others what she cannot grow herself. But this time she wants to keep the harvest."`,
                options: [
                    { text: "Your chapter didn't send you for the Toadlet, did they?", key: 'your_chapter_didnt_send_you_for_the_toadlet_did_th', next: "calyx_caught" },
                    { text: "[Keep this to yourself for now.]", key: 'keep_this_to_yourself_for_now', next: "calyx_start" },
                ],
                onTrigger: () => {
                    this.addJournalEntry(
                        'calyx_lie_detected',
                        'Neme: Calyx\'s Real Motive',
                        'Used Neme\'s Photosentience on Sister Calyx. The temporal extraction research story is cover — she wants the Chrono-Slurry Toadlet for personal use. Her chapter\'s budget is also tighter than she claims. This leverage could be useful.',
                        this.journalSystem.categories.EVENTS,
                        { character: 'Sister Calyx' }
                    );
                }
            },

            calyx_caught: {
                speaker: 'Sister Calyx',
                text: `Her composure cracks — just for a moment. Her hand moves to the vial at her belt, then drops.\n\n"How did you — " She stops. Takes a breath. "You have a reader. Some kind of bio-sense symbiont. The Reclaimers have studied those."\n\nShe lowers her voice. "Fine. The Toadlet isn't for the chapter. I've been having... temporal vertigo. Losing time. Three minutes of foresight would help me anchor. The chapter doesn't know.\n\nDoes this change things between us?"`,
                options: [
                    { text: "It does. Drop the Toadlet bid, or I tell the room.", key: 'it_does_drop_the_toadlet_bid_or_i_tell_the_room', next: "calyx_blackmail" },
                    { text: "Your secret is safe. But stay away from the Toadlet.", key: 'your_secret_is_safe_but_stay_away_from_the_toadlet', next: "calyx_mercy" },
                    { text: "I won't use this against you. Bid as you wish.", key: 'i_wont_use_this_against_you_bid_as_you_wish', next: "calyx_respect" },
                ],
                onTrigger: () => {
                    this.addJournalEntry(
                        'calyx_rattled',
                        'Calyx Confessed: Temporal Vertigo',
                        'Confronted Sister Calyx with what Neme revealed. She admitted the Toadlet is for personal use — she suffers from temporal vertigo, losing time. The chapter doesn\'t know. She\'s vulnerable.',
                        this.journalSystem.categories.EVENTS,
                        { character: 'Sister Calyx' }
                    );
                }
            },

            calyx_blackmail: {
                speaker: 'Sister Calyx',
                text: `Her jaw tightens. The fungal threads in her vestments seem to darken.\n\n"You'd expose a medical condition to win an auction? That's... Rust Choir thinking. Decay as leverage."\n\nShe's silent for a long moment. "Fine. The Toadlet is yours. I'll focus on the Dream Egg. But remember — the Pith Reclaimers have long memories and very specific methods of extraction.\n\nDon't make an enemy of my chapter lightly."`,
                options: [],
                onTrigger: () => {
                    this.addJournalEntry(
                        'calyx_blackmailed',
                        'Forced Calyx to Drop the Toadlet',
                        'Used the knowledge of Calyx\'s temporal vertigo as leverage to force her out of the Toadlet bidding. She won\'t forget this — the Pith Reclaimers hold grudges.',
                        this.journalSystem.categories.EVENTS,
                        { character: 'Sister Calyx' }
                    );
                    this.modifyFactionReputation('PithReclaimers', -10);
                    this.showNotification('Sister Calyx will not bid on the Toadlet.');
                }
            },

            calyx_mercy: {
                speaker: 'Sister Calyx',
                text: `Relief flickers across her face before the professional mask returns. "I... appreciate the discretion. Temporal vertigo isn't something the chapter treats with sympathy. They'd recall me, reassign my duties to someone 'temporally stable.'\n\nThe Toadlet was a long shot anyway. The Dream Egg is the primary mission. I'll focus there.\n\nThank you. I don't say that often."`,
                options: [],
                onTrigger: () => {
                    this.addJournalEntry(
                        'calyx_shown_mercy',
                        'Calyx Withdrew — Shown Mercy',
                        'Kept Calyx\'s temporal vertigo secret and she agreed to drop the Toadlet bid in gratitude. A more compassionate approach — and one the Pith Reclaimers might remember favorably.',
                        this.journalSystem.categories.EVENTS,
                        { character: 'Sister Calyx' }
                    );
                    this.modifyFactionReputation('PithReclaimers', 5);
                    this.showNotification('Sister Calyx will not bid on the Toadlet.');
                }
            },

            calyx_respect: {
                speaker: 'Sister Calyx',
                text: `She studies you for a moment, reassessing. "That's... unexpected. Most people in this city use every advantage they find.\n\nVery well. I'll bid as I see fit, and you'll do the same. But know that I noticed your restraint. The Pith Reclaimers value those who understand the difference between extraction and exploitation."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "calyx_start" },
                ],
                onTrigger: () => {
                    this.modifyFactionReputation('PithReclaimers', 3);
                }
            },

            calyx_thorne: {
                speaker: 'Sister Calyx',
                text: `You let Thorne-Still's decay whisper outward — a targeted pulse of cognitive confusion aimed at Sister Calyx.\n\nHer eyes glaze for a moment. She blinks, touches her temple. "I... the Dream Egg. No — the Toadlet. No, the..." She trails off, her carefully prepared bidding strategy dissolving into fog.\n\n"Excuse me. I need a moment." She steps away from the lots, visibly confused about which items she came here for.\n\nHer bidding priorities are scrambled. She'll be less effective as a competitor for any lot.`,
                options: [],
                hideCloseOption: true,
                onTrigger: () => {
                    this.addJournalEntry(
                        'calyx_rattled',
                        'Scrambled Calyx\'s Bidding Strategy',
                        'Used Thorne-Still\'s Brain Rot on Sister Calyx. Her carefully prepared bidding priorities are now confused — she can\'t remember which lots she came for. This should weaken her as a competitor.',
                        this.journalSystem.categories.EVENTS,
                        { character: 'Sister Calyx' }
                    );
                    this.showNotification('Thorne-Still scrambled Calyx\'s bidding strategy.');
                    return 'calyx_thorne_after';
                }
            },

            calyx_thorne_after: {
                speaker: 'Sister Calyx',
                text: `Sister Calyx stands slightly apart from the other guests, massaging her temples. The fungal threads in her vestments pulse erratically — even they seem confused.\n\n"I'm fine," she says to no one in particular. "Just... adjusting to the atmosphere."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "calyx_start" },
                ]
            },

            calyx_mirage: {
                speaker: 'Sister Calyx',
                text: `You reach for Ulvarex's power and weave a subtle illusion — a phantom auction official approaching Sister Calyx with urgent news.\n\n"Sister Calyx? Message from your chapter. Priority recall — you're needed at the extraction lab immediately." The illusory official holds out a convincing pith-sealed letter.\n\nCalyx's face falls. "Now? But the auction—" She reaches for the letter and her hand passes through it. The illusion shimmers and dissolves.\n\nShe stares at where the official was. Then at you. She knows.\n\n"An illusionist. How... creative." Her composure remains, but she's rattled. If you can conjure phantom officials, what else might be fake? The lots? The other bidders? She'll second-guess everything now.`,
                options: [],
                hideCloseOption: true,
                onTrigger: () => {
                    this.addJournalEntry(
                        'calyx_miraged',
                        'Mirage Weave: Rattled Sister Calyx',
                        'Used Ulvarex\'s Mirage Weave to create a phantom chapter recall message for Sister Calyx. She saw through it — but now she\'ll second-guess everything at the auction. Trust is her weakness, and it\'s been undermined.',
                        this.journalSystem.categories.EVENTS,
                        { character: 'Sister Calyx' }
                    );
                    this.showNotification('Ulvarex\'s illusion rattled Sister Calyx.');
                    return 'calyx_mirage_after';
                }
            },

            calyx_mirage_after: {
                speaker: 'Sister Calyx',
                text: `Sister Calyx stands near the lots, but she's no longer examining them with clinical precision. Her eyes keep scanning the room — checking if anything else is an illusion.\n\n"Clever trick," she mutters when you approach. "But tricks work both ways. The Pith Reclaimers study illusions too, you know. We extract them."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "calyx_start" },
                ]
            },

            // ——— Heartbroker Lune ———
            lune_start: {
                speaker: 'Heartbroker Lune',
                textKey: luneStartTextKey,
                text: luneExposed
                    ? `Heartbroker Lune keeps one gloved hand over the smallest heart in her glass harness. It beats out of rhythm with the others, guarded now.\n\n"You listened too closely," she says. "Neme, was it? A rude talent. Very valuable. Please do not aim it at me again unless you intend to pay."`
                    : (luneMisled
                        ? `Heartbroker Lune studies the lots with narrowed eyes, her glass hearts tinting a doubtful grey.\n\n"The emotional provenance here is... less reliable than advertised," she murmurs. "Someone has salted the room with false context. Very tedious. Very effective."`
                        : (metLune
                            ? `"Back again," says Heartbroker Lune. A blue heart in her harness quickens, and for a moment you feel the anticipation before she does. She takes it back with a polite nod.\n\n"Forgive me. Habit."`
                            : `A woman in lacquered gloves stands beneath a harness of blown glass chambers, each one holding a different beating heart. Some are red and wet-looking, some pale as candle wax, one translucent and full of tiny bubbles.\n\n"Heartbroker Lune," she says. As she speaks, your irritation drains away and is replaced by someone else's mild nostalgia. She inhales, satisfied, and your irritation returns.\n\n"Apologies. I trade feelings conversationally. It keeps negotiations honest, or at least interesting."`)),
                options: [
                    { text: "What are emotion-linked artifacts?", key: 'what_are_emotionlinked_artifacts', next: "lune_artifacts" },
                    { text: "What are you bidding on?", key: 'what_are_you_bidding_on', next: "lune_bidding" },
                    { text: "Did you just trade my feelings?", key: 'did_you_just_trade_my_feelings', next: "lune_trade" },
                    ...(!luneMisled ? [{ text: "Offer the wrong emotional context for the lots.", key: 'offer_the_wrong_emotional_context_for_the_lots', next: "lune_wrong_context" }] : []),
                    ...(hasNeme && !luneExposed ? [{ text: "[Photosentience] Let Neme expose what she actually values.", key: 'photosentience_let_neme_expose_what_she_values', next: "lune_neme" }] : []),
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('met_heartbroker_lune')) {
                        this.addJournalEntry(
                            'met_heartbroker_lune',
                            'Heartbroker Lune',
                            'Met Heartbroker Lune at the Voxmarket Auction Hall. She carries multiple living hearts in a glass harness and trades feelings mid-conversation. She is looking for emotion-linked artifacts.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'Heartbroker Lune' }
                        );
                    }
                }
            },

            lune_artifacts: {
                speaker: 'Heartbroker Lune',
                text: `"Objects remember handling," Lune says. One of her glass hearts clouds with amber warmth. "A wedding knife remembers devotion. A divorce spoon remembers relief. A child's lost button may carry more grief than a battlefield relic, if the child loved the coat enough."\n\nShe taps the harness lightly. "I match artifacts to hearts that can digest them. The right pairing produces rare feelings. Bottled courage. Edible remorse. Nostalgia sharp enough to cut fruit."`,
                options: [
                    { text: "What are you bidding on?", key: 'what_are_you_bidding_on', next: "lune_bidding" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "lune_start" },
                ]
            },

            lune_bidding: {
                speaker: 'Heartbroker Lune',
                text: `"Compressed Nostalgia, obviously. A whole jar of homesickness for somewhere imaginary? Delicious. The Dream Egg, perhaps, if it carries enough cathedral dread. The Brine Scripture too, though it is less an artifact than a wet archive waiting for a body. Even the Toadlet interests me a little — foresight has a panic-flavor when used by cowards."\n\nA small green heart in her harness beats faster. Suddenly you feel proprietary excitement, then it vanishes from your chest and settles behind her ribs.\n\n"I will not buy everything. Only what sings in the correct emotional key."`,
                options: [
                    { text: "What makes an emotional key correct?", key: 'what_makes_an_emotional_key_correct', next: "lune_artifacts" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "lune_start" },
                ]
            },

            lune_trade: {
                speaker: 'Heartbroker Lune',
                text: `"Briefly," Lune says. "I sampled irritation, lent you nostalgia, and returned both with minimal bruising. Perfectly courteous."\n\nShe adjusts a valve on the harness. "Most people lie with words and confess with feelings. I prefer the cleaner document."\n\nFor half a second, you feel her boredom: old, polished, expensive. Then she takes it back.`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "lune_start" },
                ]
            },

            lune_wrong_context: {
                speaker: 'Heartbroker Lune',
                text: `You lean close and offer a confident lie: the Dream Egg is not dread-soaked at all. The auction staff mislabeled it. Its dominant context is bureaucratic satisfaction — forms approved, cabinets aligned, every stamp landing square.\n\nLune recoils slightly. Three hearts in her harness slow to a disappointed crawl.\n\n"Administrative content? In cathedral stone? How vulgar." She looks back toward the lots, recalculating. "I will need to verify everything. Slowly. With suspicion."\n\nHer certainty has been poisoned. She will be a less decisive bidder.`,
                options: [],
                hideCloseOption: true,
                onTrigger: () => {
                    this.addJournalEntry(
                        'lune_wrong_context',
                        'Misled Heartbroker Lune',
                        'Fed Heartbroker Lune the wrong emotional context for the auction lots. She now doubts the emotional provenance of the artifacts and should bid less decisively.',
                        this.journalSystem.categories.EVENTS,
                        { character: 'Heartbroker Lune' }
                    );
                    this.showNotification('Heartbroker Lune is second-guessing the lots.');
                    return 'lune_start';
                }
            },

            lune_neme: {
                speaker: 'Heartbroker Lune',
                text: `You let Neme's photosentience open like a quiet green eye. Lune's harness becomes a garden of borrowed pulses: appetite, vanity, professional delight. But beneath them sits a tiny unlit heart she never lets touch the air.\n\nNeme whispers: "She does not value strong feelings. She values the absence after them. A clean hollow. Silence where wanting used to live."\n\nLune's smile freezes. "That," she says softly, "was not available for trade."`,
                options: [
                    { text: "Then these lots are too noisy for you.", key: 'then_these_lots_are_too_noisy_for_you', next: "lune_exposed" },
                    { text: "I'll keep your secret for now.", key: 'ill_keep_your_secret_for_now', next: "lune_secret" },
                ],
                onTrigger: () => {
                    this.addJournalEntry(
                        'lune_true_value',
                        'Neme: Lune Values Emptiness',
                        'Used Neme to read Heartbroker Lune. Despite her trade in intense emotions, what she truly values is emotional absence — a clean hollow where wanting used to be.',
                        this.journalSystem.categories.EVENTS,
                        { character: 'Heartbroker Lune' }
                    );
                }
            },

            lune_exposed: {
                speaker: 'Heartbroker Lune',
                text: `For once, none of Lune's hearts trade places with anything. They simply beat, exposed and unsynchronized.\n\n"Too noisy," she repeats. "Yes. Perhaps they are."\n\nShe steps back from the display wall. "I came hunting delicacies and found a room full of shouting meat. Bid as you like. I need quieter merchandise."`,
                options: [],
                onTrigger: () => {
                    this.showNotification('Heartbroker Lune has lost interest in the loudest lots.');
                }
            },

            lune_secret: {
                speaker: 'Heartbroker Lune',
                text: `"How generous," Lune says, too quickly. A violet heart in her harness tries to offer gratitude; she clamps the valve before it reaches you.\n\n"Keep it, then. Secrets accrue interest. If you spend this one later, spend it elegantly."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "lune_start" },
                ]
            },
        };
    }

    preload() {
        super.preload();
        this.load.image('voxmarketHallBg', 'assets/images/backgrounds/VoxmarketHall.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        this.load.image('heshAndVell', 'assets/images/characters/heshAndVell.png');
        this.load.image('sisterCalyx', 'assets/images/characters/sisterCalyx.png');
        this.load.image('heartbrokerLune', 'assets/images/characters/HeartbrokerLune.png');
    }

    create() {
        super.create();
        
        this.playSceneMusic('marketTheme');
        
        const bg = this.add.image(400, 300, 'voxmarketHallBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        this.createHallGround();
        
        if (this.ground) {
            this.ground.destroy();
        }
        
        this.transitionManager = new SceneTransitionManager(this);
        
        this.priest.x = 100;
        this.priest.y = 470;
        
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }
        
        this.cameras.main.fadeIn(800, 0, 0, 0);
        
        this.transitionManager.createTransitionZone(
            50, 470, 50, 200, 'left', 'VoxMarket', 100, 470
        );
        
        const exitHint = this.add.text(100, 420, 'Back to Main Market', {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        exitHint.setOrigin(0.5);
        exitHint.setAlpha(0);
        exitHint.setDepth(10);
        
        this.input.on('pointermove', (pointer) => {
            if (Math.abs(pointer.x - 50) < 50 && Math.abs(pointer.y - 470) < 100) {
                exitHint.setAlpha(1);
            } else {
                exitHint.setAlpha(0);
            }
        });
        
        if (this.stranger) {
            this.stranger.destroy();
        }

        // Create NPCs
        this.createTwinAuctioneers();
        this.createHeartbrokerLune();
        this.createSisterCalyx();

        // Show arrival notification
        this.time.delayedCall(500, () => {
            this.showNotification('Voxmarket Auction Hall', 0x8B4513);
        });
    }

    createTwinAuctioneers() {
        this.twins = this.add.image(440, 345, 'heshAndVell');
        this.twins.setScale(0.16);
        this.twins.setDepth(5);
        this.twins.setInteractive({ useHandCursor: true });

        // Subtle idle sway — slightly offset to suggest desynchronization
        this.tweens.add({
            targets: this.twins,
            angle: { from: -0.5, to: 0.5 },
            duration: 3000,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });

        this.twins.on('pointerover', () => {
            this.twins.setScale(0.17);
            document.body.style.cursor = 'pointer';
        });

        this.twins.on('pointerout', () => {
            this.twins.setScale(0.16);
            document.body.style.cursor = 'default';
        });

        this.twins.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog('twins_start');
        });
    }

    createSisterCalyx() {
        this.calyx = this.add.image(650, 420, 'sisterCalyx');
        this.calyx.setScale(0.15);
        this.calyx.setDepth(5);
        this.calyx.setInteractive({ useHandCursor: true });

        this.calyx.on('pointerover', () => {
            this.calyx.setScale(0.16);
            document.body.style.cursor = 'pointer';
        });

        this.calyx.on('pointerout', () => {
            this.calyx.setScale(0.15);
            document.body.style.cursor = 'default';
        });

        this.calyx.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog('calyx_start');
        });
    }

    createHeartbrokerLune() {
        this.lune = this.add.image(250, 420, 'heartbrokerLune');
        this.lune.setScale(0.14);
        this.lune.setDepth(5);
        this.lune.setInteractive({ useHandCursor: true });

        this.tweens.add({
            targets: this.lune,
            y: this.lune.y - 4,
            duration: 2200,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });

        this.lune.on('pointerover', () => {
            this.lune.setScale(0.15);
            document.body.style.cursor = 'pointer';
        });

        this.lune.on('pointerout', () => {
            this.lune.setScale(0.14);
            document.body.style.cursor = 'default';
        });

        this.lune.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog('lune_start');
        });
    }

    shutdown() {
        // Restore background music when leaving the scene
        this.restoreBackgroundMusic();
        super.shutdown();
    }

    update() {
        // Call parent update for all standard mechanics
        super.update();
    }
    
    // Create a custom ground for the hall scene that matches the aesthetic
    createHallGround() {
        // Remove the original ground if it exists
        if (this.ground) {
            this.ground.destroy();
        }
        
        // Create a graphics object for the ground
        const groundGraphics = this.add.graphics();
        
        // Set the ground dimensions
        const groundWidth = 800;
        const groundHeight = 160;
        const groundY = 500;
        
        // Fill with dark reddish-brown base color to match hall floor
        groundGraphics.fillStyle(0x2a1a18, 1);
        groundGraphics.fillRect(0, groundY, groundWidth, groundHeight);
        
        // Add some texture with lines
        groundGraphics.lineStyle(1, 0x3c2824, 0.3);
        
        // Horizontal lines for floor boards
        for (let i = 0; i < 10; i++) {
            const y = groundY + Math.random() * groundHeight;
            groundGraphics.beginPath();
            groundGraphics.moveTo(0, y);
            groundGraphics.lineTo(groundWidth, y);
            groundGraphics.closePath();
            groundGraphics.strokePath();
        }
        
        // Vertical lines for texture
        for (let i = 0; i < 20; i++) {
            const x = Math.random() * groundWidth;
            groundGraphics.beginPath();
            groundGraphics.moveTo(x, groundY);
            groundGraphics.lineTo(x, groundY + groundHeight);
            groundGraphics.closePath();
            groundGraphics.strokePath();
        }
        
        // Add subtle glowing particles to match the hall atmosphere
        for (let i = 0; i < 30; i++) {
            const x = Math.random() * groundWidth;
            const y = groundY + Math.random() * (groundHeight - 10);
            const size = Math.random() * 2 + 1;
            
            const particle = this.add.circle(x, y, size, 0xcc6644, 0.2);
            particle.setDepth(1);
            
            // Add pulsating effect to some particles
            if (Math.random() > 0.7) {
                this.tweens.add({
                    targets: particle,
                    alpha: 0.1,
                    duration: 1500 + Math.random() * 1000,
                    yoyo: true,
                    repeat: -1,
                    ease: 'Sine.easeInOut'
                });
            }
        }
        
        // Set the ground depth
        groundGraphics.setDepth(0);
    }
}
