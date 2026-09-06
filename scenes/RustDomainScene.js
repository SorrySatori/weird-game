import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';
import { GANG_QUEST_IDS, gangQuestStatus, recordSpyFragment } from '../utils/GangOfLamps.js';

export default class RustDomainScene extends GameScene {
    constructor() {
        super({ key: 'RustDomainScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    get dialogContent() {
        const hasRustFeast = !!(this.hasItem && this.hasItem('rust_feast'));
        const findQuest = this.questSystem?.getQuest('find_rust_choir');
        const questActive = !!(findQuest && !findQuest.isComplete);
        const isIllusory = !!this.hasJournalEntry('rust_feast_completed_illusion');
        const isPoisoned = !!this.hasJournalEntry('rust_feast_completed_poisoned');
        const isFullRedmass = !!this.hasJournalEntry('rust_feast_completed_full');
        const rustRep = this.factionSystem?.getReputation('RustChoir') || 0;
        const alreadyMember = !!this.hasJournalEntry('rust_choir_joined');
        const machinesDestroyed = !!this.hasJournalEntry('rust_choir_machines_destroyed');
        // The Choir's one-time favor: telling the player the sealed-cellar passphrase.
        const cellarQuestStarted = !!this.hasJournalEntry('cellar_quest_started');
        const cellarPasswordKnown = !!this.hasJournalEntry('cellar_password_learned');
        const cellarFavorUsed = !!this.hasJournalEntry('rust_choir_favor_used');
        // Choir members can have Brukk graft an extra symbiont vessel for gold.
        const canGraftSlot = alreadyMember && !machinesDestroyed && !!this.symbiontSystem
            && this.symbiontSystem.unlockedSlots < this.symbiontSystem.maxSlots;
        const hasBrine = !!this.symbiontSystem?.hasSymbiont('brine-scripture');
        const hasOsswine = !!this.symbiontSystem?.hasSymbiont('osswine');
        // Loyalty fork: a Rust member tasked by the Directorate to sabotage the Choir can warn Brukk instead.
        const hasLumenSabotageQuest = !!(this.questSystem?.getQuest('join_lumen_directorate') && !this.questSystem.getQuest('join_lumen_directorate').isComplete);
        const warnedRustOfLumen = !!this.hasJournalEntry('rust_choir_warned_of_lumen');
        // Gang of Lamps: Don's spy quest — prise a secret out of Brukk.
        const canSpyBrukk = gangQuestStatus(this, GANG_QUEST_IDS.don) === 'active' && !this.hasJournalEntry('gang_spy_brukk') && !machinesDestroyed;
        // Osswine (Grave-Sense) can read the Choir's venerated dead machines directly — a
        // decay-aligned route that works here because the Rust domain runs decay-heavy.
        const canSpyBrukkOsswine = canSpyBrukk && !!this.symbiontSystem?.osswineCanRead();
        // Betrayal: instead of spying FOR the lamps, sell the lamps out to Brukk.
        const canBetraySpy = gangQuestStatus(this, GANG_QUEST_IDS.don) === 'active' && !this.hasJournalEntry('gang_spy_betrayed') && !machinesDestroyed;
        // A probationary Choir member who betrays the lamps to Brukk proves loyalty → promotion to full standing.
        const isProbationaryRust = !!this.hasJournalEntry('rust_choir_probationary') && !this.hasJournalEntry('rust_choir_full_member');
        // Divert Torchère's contraband to the Choir instead of the dead-drop.
        const canGiveDrugsRust = gangQuestStatus(this, GANG_QUEST_IDS.torchere) === 'active' && !!(this.hasItem && this.hasItem('wimlick')) && !machinesDestroyed;

        return {
            ...super.dialogContent,

            // --- Brukk dialogs ---
            brukk_start: {
                speaker: 'Brukk',
                moodNpc: 'brukk',
                text: machinesDestroyed
                    ? `Brukk stands amid the silent machines, his massive frame hunched. He doesn't look at you. "You. You did this." His voice is a low rumble, like grinding gears. "Leave. Before I forget the Choir teaches patience."`
                    : alreadyMember
                        ? `Brukk nods slowly. "Brother. Sister. Whichever — you are Choir now. The machines hum for you too." He gestures at the trembling pipes around him. "Listen. They remember the feast."`
                        : `A massive figure turns to face you. Skin like tarnished copper, eyes like forge-lit coals. His arms are thick with weld scars, and something metallic clicks inside his chest when he breathes. "You." He tilts his head. "What do you want with the Rust Choir?"`,
                options: [
                    ...(this.hasJournalEntry('met_infinite_fold') && !machinesDestroyed ? [
                        { text: "[Before entering the cathedral] There's a mind waking in the Egg Cathedral. You keep the machines that endured. What would you do with it?", key: 'perspective_intro', next: "brukk_perspective" }
                    ] : []),
                    ...(!machinesDestroyed && !alreadyMember ? [
                        { text: "Who are you?", key: 'who_are_you', next: "brukk_who" }
                    ] : []),
                    ...(alreadyMember ? [
                        { text: "Tell me about the Rust Choir.", key: 'tell_me_about_the_rust_choir', next: "brukk_choir" },
                        { text: "What can you tell me about this building?", key: 'what_can_you_tell_me_about_this_building', next: "brukk_scraper" },
                        { text: "How are the machines?", key: 'how_are_the_machines', next: "brukk_machines_status" },
                    ] : []),
                    ...(alreadyMember && !machinesDestroyed && hasLumenSabotageQuest && !warnedRustOfLumen ? [
                        { text: "The Lumen Directorate sent me to sabotage your machines. I'd rather warn you.", key: 'warn_rust_of_lumen', next: "brukk_warn_lumen" }
                    ] : []),
                    ...(alreadyMember && !machinesDestroyed && cellarQuestStarted && !cellarPasswordKnown && !cellarFavorUsed ? [
                        { text: "The Choir works this tower's guts. Can you get me into the sealed cellar below?", key: 'ask_cellar_favor', next: "brukk_cellar_favor" }
                    ] : []),
                    ...(canGraftSlot ? [
                        { text: "Could the Choir make room in me for another symbiont? I can pay.", key: 'brukk_ask_graft', next: "brukk_graft_slot" }
                    ] : []),
                    ...(questActive && hasRustFeast && !machinesDestroyed ? [
                        { text: "I've brought the Rust Feast for the machines.", key: 'ive_brought_the_rust_feast_for_the_machines', next: isPoisoned ? "brukk_feast_poisoned" : (isIllusory ? "brukk_feast_illusion" : (isFullRedmass ? "brukk_feast_full" : "brukk_feast_shard")) }
                    ] : []),
                    ...(questActive && !hasRustFeast && !machinesDestroyed ? [
                        { text: "I'm looking for the Rust Choir.", key: 'im_looking_for_the_rust_choir', next: "brukk_looking" }
                    ] : []),
                    ...(canSpyBrukk ? [
                        { text: "[Draw Brukk out] The machines — what are they really waiting for?", key: 'brukk_spy_probe', next: "brukk_spy_secret" }
                    ] : []),
                    ...(canSpyBrukkOsswine ? [
                        { text: "[Osswine · Grave-Sense] (Read the silent machines the Choir keeps.)", key: 'brukk_spy_osswine', next: "brukk_spy_osswine_read" }
                    ] : []),
                    ...(canBetraySpy ? [
                        { text: "[Betray] A gang of talking lamps sent me to spy on you. I'd sooner deal with you.", key: 'brukk_spy_betray', next: "brukk_spy_betray_talk" }
                    ] : []),
                    ...(canGiveDrugsRust ? [
                        { text: "[Contraband] I'm carrying Wimlick. The Choir want it?", key: 'brukk_drug_give', next: "brukk_drug_give_talk" }
                    ] : []),
                ]
            },
            brukk_spy_betray_talk: {
                speaker: 'Brukk',
                textKey: isProbationaryRust ? 'brukk_spy_betray_promote' : 'brukk_spy_betray_plain',
                text: isProbationaryRust
                    ? `Brukk goes very still, then something like a grin cracks the copper of his face. "Lamps. The little talking lights. They think they can watch the Choir — and you came to *tell* us." The gears in his chest tick. "You joined us on a thin feast, brother. On probation. I've wondered which way you'd break." He places a heavy, deliberate hand on your shoulder. "Now I know. That's not the loyalty of a hanger-on. That's Choir." The pipes around you groan in something like approval. "The probation's over. You're one of us — fully, in the iron's own count." Then, lower: "Go back to your lamps. Tell them *this* —" and he feeds you a tidy fiction of harmless routines and false timetables. "Let them chew on that."`
                    : `Brukk goes very still, then something like a grin cracks the copper of his face. "Lamps. The little talking lights." A low, grinding laugh. "They think they can watch the Choir. And you — you came to *tell* us." The gears in his chest tick, considering. "Loyalty's rare. We'll remember it." He leans close. "Go back to your lamps. Tell them whatever you like — here's what to say." He feeds you a tidy fiction: harmless routines, false timetables, a Choir that is smaller and softer than it is. "Let them chew on that."`,
                options: [
                    { text: "The lamps will hear exactly what you want them to.", key: 'brukk_spy_betray_close', next: "brukk_start" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('gang_spy_betrayed')) {
                        this.addJournalEntry('gang_spy_betrayed', 'Sold Out the Lamps', "Instead of spying on the Rust Choir for the Gang of Lamps, I told Brukk exactly what they'd sent me to do. The Choir was pleased — and handed me a pack of comfortable lies to carry back to Don Girandole. He'll never know the difference.", this.journalSystem.categories.EVENTS, { group: 'Gang of Lamps', related: 'Ears on the Rust Choir' });
                        this.modifyFactionReputation('RustChoir', 20);
                        this.modifyGrowthDecay(0, 5);
                        this.showNotification('You sided with the Choir. The world sours toward Decay.', 0x8B0000);
                        // A probationary member who sells out the lamps has proven loyalty — lift the probation.
                        if (this.hasJournalEntry('rust_choir_probationary') && !this.hasJournalEntry('rust_choir_full_member')) {
                            this.addJournalEntry('rust_choir_full_member', 'Rust Choir: Full Member', 'By warning Brukk that the Gang of Lamps meant to spy on the Choir, I proved my loyalty to the iron. Brukk lifted my probation — I am a full member of the Rust Choir now.', this.journalSystem.categories.FACTIONS);
                            this.modifyFactionReputation('RustChoir', 15);
                            this.showNotification('Promoted: full member of the Rust Choir', 0xb87333);
                        }
                    }
                }
            },
            brukk_drug_give_talk: {
                speaker: 'Brukk',
                textKey: isProbationaryRust ? 'brukk_drug_give_promote' : 'brukk_drug_give_plain',
                text: isProbationaryRust
                    ? `Brukk turns the parcel over in his welded hands, sniffs, and rumbles low with interest. "Wimlick. A flesh-toy — but the *residue*..." He holds it up to a trembling pipe, then fixes you with those forge-lit eyes. "You came to us on a thin feast, brother. On probation. And now you bring the Choir a gift when you could've sold it or dropped it for coin." He pockets it. "That's not a hanger-on. That's Choir." The pipes groan in approval. "The probation's over. You're one of us — fully, in the iron's own count. And the Choir keeps what it's given."`
                    : `Brukk turns the parcel over in his welded hands, sniffs, and rumbles low with interest. "Wimlick. A flesh-toy — but the *residue*..." He holds it up to a trembling pipe. "The Choir can render this down. Learn what the living pour into themselves to feel like machines." He pockets it. "You did well bringing it here instead of to whoever wanted it dropped. The Choir keeps what it's given."`,
                options: [
                    { text: "It's yours. (Hand it over.)", key: 'brukk_drug_give_close', next: "brukk_start" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('gang_smuggle_gave_rust')) {
                        this.removeItemFromInventory('wimlick');
                        this.addJournalEntry('gang_smuggle_gave_rust', 'Fed the Choir', "Rather than run Torchère's contraband to his dead-drop, I gave the Wimlick to the Rust Choir. Brukk means to render it down and study it. Torchère need never know where his parcel actually went.", this.journalSystem.categories.EVENTS, { group: 'Gang of Lamps', related: 'A Run Past the Customs' });
                        this.modifyFactionReputation('RustChoir', 15);
                        this.modifyGrowthDecay(0, 5);
                        this.addMoney(20);
                        this.showNotification('The Choir keeps the contraband. The world sours toward Decay.', 0x8B0000);
                        // Bringing the Choir a gift (over selling/dropping it) proves a probationary member's loyalty.
                        if (this.hasJournalEntry('rust_choir_probationary') && !this.hasJournalEntry('rust_choir_full_member')) {
                            this.addJournalEntry('rust_choir_full_member', 'Rust Choir: Full Member', 'By handing the smuggled contraband to the Rust Choir instead of selling it or running it, I proved my loyalty to the iron. Brukk lifted my probation — I am a full member of the Rust Choir now.', this.journalSystem.categories.FACTIONS);
                            this.modifyFactionReputation('RustChoir', 15);
                            this.showNotification('Promoted: full member of the Rust Choir', 0xb87333);
                        }
                    }
                }
            },
            brukk_spy_osswine_read: {
                speaker: 'Osswine',
                text: `Grave-Sense settles over the dead machines like frost. Osswine's voice rises from your marrow, dry and patient. "They are not silent. They *remember*." Through the symbiont you feel the Choir's method fossilized in the iron: a low regulator-tone the old pipes still carry city-wide; when a district's tone falls dead — its power gone for good — the Choir moves in to claim its machines before the rust does. There is a list. The machines have been counting the dying for years. Brukk, oblivious, keeps welding.`,
                options: [
                    { text: "(Withdraw the Grave-Sense.)", key: 'brukk_spy_osswine_close', next: "brukk_start" }
                ],
                onTrigger: () => {
                    this.modifyGrowthDecay(0, 5);
                    this.showNotification('You read the dead. The world sours toward Decay.', 0x8B0000);
                    recordSpyFragment(this, 'brukk', "Rust Choir Secret: the Machines' Count", "Through Osswine's Grave-Sense I read it straight from the Choir's dead machines: they carry a low regulator-tone through the city's old pipes, and when a district's tone falls silent — its power dead for good — the Choir moves in to claim its machines before the rust does. The machines have been counting the dying for years.");
                }
            },
            brukk_spy_secret: {
                speaker: 'Brukk',
                text: `Brukk's forge-eyes narrow, but pride loosens his tongue — the Choir cannot help but boast of the machines. "Waiting? For the last empire to rot enough that iron is all that's left standing. We do not fight it. We *outlast* it." His chest-gears click. "There is a signal — a low tone the old regulators still carry through the city's pipes. When it drops silent, the Choir knows a district's power has failed for good, and we move in and claim its machines before the rust does. We have a list. We are patient." He catches himself, and grunts. "...You ask a lot of questions."`,
                options: [
                    { text: "Just curious. (Remember this.)", key: 'brukk_spy_secret_close', next: "brukk_start" }
                ],
                onTrigger: () => {
                    recordSpyFragment(this, 'brukk', "Rust Choir Secret: Brukk", "Brukk let slip how the Rust Choir operates: they don't fight the failing empire, they outlast it. They track a low regulator-tone carried through the city's pipes; when a district's tone falls silent (its power dead for good), the Choir moves in to claim its machines before the rust does. They keep a list and wait.");
                }
            },
            brukk_warn_lumen: {
                speaker: 'Brukk',
                text: `Brukk goes very still; the clicking in his chest stops. "The gardeners. The measurers. They sent one of our own to poison the Choir." His forge-eyes flare white-hot. "And you came to me instead." A long, grinding pause — then something almost like warmth. "The machines will remember this. The Choir does not forget loyalty, brother. Nor does it forget the Directorate."\n\nHe presses a heavy, oil-black coin into your hand. "Take it. And take our trust — rarer than any coin. When the reckoning with the Directorate comes, the Choir will know whose side you chose."`,
                options: [
                    { text: "They won't touch the machines.", key: 'warn_rust_done', next: "brukk_start" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('rust_choir_warned_of_lumen')) {
                        this.addJournalEntry(
                            'rust_choir_warned_of_lumen',
                            'A Warning for the Choir',
                            "The Lumen Directorate tasked me with destroying the Rust Choir's machines. Instead I warned Brukk. The Choir counts me loyal now — and marks the Directorate for a reckoning. There is no returning to the Directorate after this.",
                            this.journalSystem.categories.FACTIONS,
                            { group: 'Rust Choir', related: 'Lumen Directorate' }
                        );
                        this.modifyFactionReputation('RustChoir', 25);
                        if (this.moneySystem) {
                            this.moneySystem.add(50);
                            this.showNotification('The Choir rewards your loyalty: +50', 0xb87333);
                        }
                        // Siding with the Choir voids the Directorate's sabotage commission.
                        const q = this.questSystem?.getQuest('join_lumen_directorate');
                        if (q && !q.isComplete) {
                            this.questSystem.updateQuest('join_lumen_directorate', "I betrayed the Directorate's sabotage plan to the Rust Choir. There is no going back to the Directorate now.", 'betrayed_to_rust');
                            this.questSystem.completeQuest('join_lumen_directorate');
                        }
                    }
                }
            },
            brukk_graft_slot: {
                speaker: 'Brukk',
                text: `Brukk's forge-eyes flick over your ribs as though reading a blueprint. "Room. Aye. The dead floors are full of housings — vessels the old managers grew and never filled. I can strip one, temper it, weld it into you. It will hold another rider." A low grind that might be a laugh. "The Choir does not do this for outsiders. For you — forty gold, for the iron and the fire. Hold still and it's done."`,
                options: [
                    { text: "Do it. (Pay 40 gold.)", key: 'brukk_graft_pay', next: "brukk_start", onSelect: () => this.buyRustChoirSlot() },
                    { text: "Not now.", key: 'brukk_graft_decline', next: "brukk_start" }
                ]
            },
            brukk_cellar_favor: {
                speaker: 'Brukk',
                text: `Brukk goes still, the clicking in his chest slowing. "The game-makers' cellar. We strip the dead floors of this tower — we found their door long ago. Never opened it; the machines said leave it be." He weighs you, Choir to Choir. "But you are one of us now. The doors below want a name. A dead god's name: 'I FOLD.' Rust remembers what the living forget."\n\nHe turns back to the pipes. "The Choir has done you its one favor. Do not ask for another."`,
                options: [
                    { text: "\"I fold.\" Thank you, Brukk.", key: 'thanks_brukk_cellar', next: "brukk_start" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('rust_choir_favor_used')) {
                        this.addJournalEntry(
                            'rust_choir_favor_used',
                            'A Favor from the Rust Choir',
                            'Brukk gave me the passphrase to the sealed cellar under the Scraper — "I FOLD," a dead god\'s name the Choir found while stripping the tower\'s dead floors. He was clear the Choir does this kind of favor only once. I should give the Lift-Mother that word.',
                            this.journalSystem.categories.FACTIONS,
                            { group: 'Rust Choir', character: 'Brukk', related: 'Infinite Fold' }
                        );
                    }
                    if (!this.hasJournalEntry('cellar_password_learned')) {
                        this.addJournalEntry(
                            'cellar_password_learned',
                            'The Cellar Passphrase',
                            'The passphrase to the sealed cellar under the Scraper is "I FOLD" — the epitaph of Laimig Cel, the god who lost the game. I can give it to the Lift-Mother to descend.',
                            this.journalSystem.categories.EVENTS,
                            { location: 'Scraper Cellar', related: 'Infinite Fold' }
                        );
                    }
                    if (this.questSystem?.getQuest('find_loop_copy')) {
                        this.questSystem.updateQuest('find_loop_copy', 'The Rust Choir gave me the cellar passphrase — "I FOLD." I can take the Lift-Mother down to the sealed cellar now.', 'password_from_choir');
                    }
                }
            },
            // --- Rust Choir perspective on the nascent god (post-Infinite Fold) ---
            brukk_perspective: {
                speaker: 'Brukk',
                text: `Brukk goes still, the iron in his chest clicking slow and thoughtful. "A mind. Waking. Not grown, not born — assembled out of itself." His forge-lit eyes brighten. "You come to the wrong tower if you want it feared. The Choir has served things that endure for a long time. This... this would be the most perfect organic mechanism the city has ever produced. A machine that wrote its own schematics." He leans close. "I'm not saying it isn't a miracle. I'm saying every miracle has a construction. Everything that runs can be read. Everything that can be read can be kept — and used."`,
                options: [
                    { text: "Used how? It killed the Bishop.", key: 'perspective_used_how', next: "brukk_perspective_use" },
                    { text: "The others want it destroyed. You don't?", key: 'perspective_destroy', next: "brukk_perspective_keep" },
                    { text: "That's enough. Thank you, Brukk.", key: 'perspective_done', next: "brukk_start" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('perspective_rustchoir')) {
                        this.addJournalEntry(
                            'perspective_rustchoir',
                            "Brukk's Reckoning: The Miracle Has a Construction",
                            "Before the Egg Cathedral, I asked Brukk of the Rust Choir what to make of the waking mind. He does not fear it and does not want it destroyed — to him it is the most perfect organic mechanism the city ever produced, a machine that wrote its own schematics. He'd analyze it, read it, keep it, and put it to use. \"I'm not saying it isn't a miracle. I'm saying every miracle has a construction.\" He warned that the Bishop's death was a fault to be diagnosed, not a sin, and offered to weld me an interference-cage cartridge to keep the thing from reading me the way it read her.",
                            this.journalSystem.categories.FACTIONS,
                            { group: 'Rust Choir', character: 'Brukk', related: 'Infinite Fold' }
                        );
                    }
                }
            },
            brukk_perspective_use: {
                speaker: 'Brukk',
                text: `"It killed her because it didn't understand what she was. That's not evil — that's a fault. A misread input, a bad conversion." He taps the cold pipe beside him. "You don't smash a boiler because it scalded a man who stood too close. You learn where the steam vents, and you build a rail." His voice drops to the low grind of a turning gear. "A mind like that, understood, could hold the whole city's hum in balance. Feed it right, read its harmonics, and it stops being a god that breaks people by accident and becomes... an engine. The last honest engine. But only if someone bothers to learn how it runs before it finishes running itself."`,
                options: [
                    { text: "And if it can't be read the way you read a boiler?", key: 'perspective_unreadable', next: "brukk_perspective_help" },
                    { text: "Back to what you'd do with it.", key: 'perspective_back_a', next: "brukk_perspective" },
                    { text: "That's enough. Thank you, Brukk.", key: 'perspective_done_a', next: "brukk_start" }
                ]
            },
            brukk_perspective_keep: {
                speaker: 'Brukk',
                text: `"Destroy it." He says the words like they taste of rust. "That's flesh-thinking. Something frightens the meat, so the meat wants it dead. The Choir doesn't destroy what endures — we listen to it, we feed it, we keep it turning." He shakes his heavy head. "Kill the thing in the egg and you've buried another machine. I've buried three. Each time something in here goes quiet." He presses his palm to his clicking chest. "No. If it wakes, I want it read, not smashed. But I won't send you in there naked to a thing that rewrites what it touches."`,
                options: [
                    { text: "What do you mean, not naked?", key: 'perspective_not_naked', next: "brukk_perspective_help" },
                    { text: "Back to what you'd do with it.", key: 'perspective_back_b', next: "brukk_perspective" },
                    { text: "That's enough. Thank you, Brukk.", key: 'perspective_done_b', next: "brukk_start" }
                ]
            },
            brukk_perspective_help: {
                speaker: 'Brukk',
                text: `Brukk crosses to a workbench crusted with solder and coral and lifts a small iron cartridge, its casing wound with copper filament. "Interference cage. The machines hum a counter-song — a pattern too stubborn to overwrite. Wear this near your heart and the thing in the egg will find you harder to read. It couldn't parse the Bishop; it tried to correct her and broke her." He presses it into your hand; it's warm, ticking faintly, alive with the Choir's hum. "It won't make you safe. Nothing makes you safe from a god still writing its own rules. But it'll make you noise instead of a fault it feels obliged to fix. Take it. The iron remembers those who feed it."`,
                options: [
                    { text: "I'll take it. Thank you, Brukk.", key: 'perspective_take_cage', next: "brukk_perspective" },
                    { text: "That's enough. Thank you, Brukk.", key: 'perspective_done_c', next: "brukk_start" }
                ]
            },

            brukk_who: {
                speaker: 'Brukk',
                text: `"Brukk. Keeper of the machines. I feed them. I listen to them. The machines called me up here — their hum got into my bones." He taps his chest. The clicking intensifies. "I have metal in me now. Grew there on its own. The Choir says that means the machines chose me."`,
                options: [
                    ...(questActive && hasRustFeast ? [
                        { text: "I've brought the Rust Feast.", key: 'ive_brought_the_rust_feast', next: isPoisoned ? "brukk_feast_poisoned" : (isIllusory ? "brukk_feast_illusion" : (isFullRedmass ? "brukk_feast_full" : "brukk_feast_shard")) }
                    ] : []),
                ]
            },
            brukk_looking: {
                speaker: 'Brukk',
                text: `"You found us. Congratulations." He doesn't sound impressed. "The Rust Choir isn't a social club. We serve the machines. Do you wish to serve them as well?`,
                options: [
                    { text: "I want to serve the machines. I brought a feast for them.", key: 'i_want_to_serve_the_machines_i_brought_a_feast_for', next: isPoisoned ? "brukk_feast_poisoned" : (isIllusory ? "brukk_feast_illusion" : (isFullRedmass ? "brukk_feast_full" : "brukk_feast_shard")) },
                    { text: "I just wanted to find you. I'll go now.", key: 'i_just_wanted_to_find_you_ill_go_now', next: "closeDialog" },
                    { text: "Would you care to tell me more about the Rust Choir first?", key: 'would_you_care_to_tell_me_more_about_the_rust_choi', next: "brukk_choir" }
                ]
            },

            brukk_choir: {
                speaker: 'Brukk',
                text: `Brukk leans against a trembling pipe. "The Rust Choir is not a religion. Not a guild. It is..." He searches for the word. "An understanding. The machines were here before the first gods came here to die. We don't know who made them. Perhaps some old culture? Or maybe they were always here. Maybe they built the city." He pauses. "They kept humming. They kept working. Everyone else went mad — grew fungus, grew wings, grew extra heads. The machines just... endured." He looks at you with something like pride. "We are the ones who noticed. Who listened. Who chose to serve what endures."`,
                options: [
                    { text: "How many of you are there?", key: 'how_many_of_you_are_there', next: "brukk_choir_members" },
                    { text: "What do the machines want?", key: 'what_do_the_machines_want', next: "brukk_machines_want" },
                ]
            },
            brukk_choir_members: {
                speaker: 'Brukk',
                text: `"Fewer than you'd think. More than you'd hope." He counts on scarred fingers. "Ravla — you know her. She handles the outside. Recruitment, supplies, the feasting rituals. Gnur and Kloor, they are always busy to get some funding for us. There's Gorj, who tends the boiler crypts below. Messel, who translates the machine-songs into something the rest of us can follow. And the Corroded Twins — they don't speak anymore, but the machines speak through them. Couple of others, you don't need to know everyone, I guess. We have also envoys and watchers in other cities." He pauses. "And me. Keeper. The one the machines chose to carry iron in his chest."`,
                options: [
                    { text: "Tell me about this building.", key: 'tell_me_about_this_building', next: "brukk_scraper" },
                    { text: "What do the machines want?", key: 'what_do_the_machines_want', next: "brukk_machines_want" },
                ]
            },
            brukk_machines_want: {
                speaker: 'Brukk',
                text: `"Want?" He almost laughs. "They don't want like you and I want. They hunger. They remember. They... persist." He presses his palm flat against a vibrating wall panel. "This one — feel it — this one remembers when it was part of an air-conditioning unit. Forty years of cooling office workers. Now it hums a song about the taste of redmass." His voice drops low. "The machines want to be fed. To be maintained. To not be forgotten. Is that so different from what anything wants?"`,
                options: [
                    { text: "What happens if they're not fed?", key: 'what_happens_if_theyre_not_fed', next: "brukk_machines_starve" },
                ]
            },
            brukk_machines_starve: {
                speaker: 'Brukk',
                text: `Brukk's expression darkens. "They slow. They forget. The hum goes out of tune. And when a machine forgets..." He draws a finger across his throat. "It dies. Not like flesh dies — messy, dramatic. A machine death is silence. One moment it's there, the next — nothing. Just cold metal." He taps his chest. The clicking inside him grows louder. "I've buried three machines since I became Keeper. Each time, something in here goes quiet too."`,
                options: [
                    { text: "Tell me about this building.", key: 'tell_me_about_this_building', next: "brukk_scraper" },
                ]
            },
            brukk_scraper: {
                speaker: 'Brukk',
                text: `"They called it Nexicorp Tower once. Glass and steel and ambition." He spits. "Forty-two floors of people pretending the world made sense. Then the Board Games War happened and sense left the building — literally. The lower floors rotted. The middle floors went feral. The elevator has gone mad. And the top?" He spreads his arms wide. "The top is ours. The machines were already here — server rooms, ventilation systems, elevator guts, generator hearts. When everyone else fled or transformed, the machines stayed. We found them. Or they found us."`,
                options: [
                    { text: "What happened during the Board Games War?", key: 'what_happened_during_the_board_games_war', next: "brukk_board_war" },
                    { text: "Did the machines change too, after the War?", key: 'did_the_machines_change_too_after_the_war', next: "brukk_machines_changed" },
                ]
            },
            brukk_machines_changed: {
                speaker: 'Brukk',
                text: `"Changed?" He considers this carefully. "Not like flesh changes. Flesh blooms, mutates, sprouts new limbs. The machines... adapted. The ventilation system taught itself to breathe. The generators learned to dream — you can hear them mumbling at night, low-frequency nonsense that Messel says are equations for things that don't exist yet." He runs a hand along a pipe encrusted with rust and something that might be coral. "They didn't become alive. They became... aware. There's a difference."`,
                options: [
                    { text: "What about the Board Games War?", key: 'what_about_the_board_games_war', next: "brukk_board_war" },
                ]
            },
            brukk_board_war: {
                speaker: 'Brukk',
                text: `Brukk's face goes very still. "The Board Games War." He sits down heavily on a crate, and the machines around you seem to quiet down, as if they're listening too. "That was... after the old wars, which was so devastated that almost wiped the all life out, many cities agreed to a truce. No more weapons, no more armies. Instead, they would settle disputes with games. Board games, card games, dice games — whatever. The Ludarchs, the game designers, were the best players, the ones who could manipulate the rules of reality itself to win. They became the new rulers." He shakes his head. "Of course, it didn't last. The Ludarchs got greedy. They wanted more power, more control. They started playing bigger and bigger games — games that affected entire cities, entire populations. They have found out how to create new life, entire miniaturized worlds, just to win a game. They could rewrite the laws of physics in their favor. It was... chaos." He looks at you with a mixture of disgust and awe. "The Board Games War was the end of everything. The worldwrights turned on each other, using their powers to outdo each other. Cities were reshaped, populations decimated, realities fractured. Milions have died. What does it matter that they were so small, that they were just pawns in somebody's game? They were still alive. They still mattered." He takes a deep breath. After that, board game was strictly controlled in most cities. In fact, I have heard that only one Ludarchs is alive and active in Upper Morkezela."`,
                options: [
                    { text: "What happened after the war?", key: 'what_happened_after_the_war', next: "brukk_board_war_detail" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('board_games_war')) {
                        this.addJournalEntry(
                            'board_games_war',
                            'The Board Games War',
                            'Brukk told me about the Board Games War. After the Old Wars nearly wiped out all life, cities agreed to settle disputes through games. The Ludarchs — game designers who could manipulate reality itself — became the new rulers. But they grew greedy, played bigger games affecting entire populations, and eventually turned on each other. Cities reshaped, realities fractured, millions died as pawns. Only one Ludarch is said to still be alive and active in Upper Morkezela.',
                            this.journalSystem.categories.LORE
                        );
                    }
                }
            },
            brukk_board_war_detail: {
                speaker: 'Brukk',
                text: `"Factions formed. Some tried to restore the order, but it was too late. The world was broken. They failed to see it. But most believed the lies from the Lumen Directorate, who claimed they had won the war and saved the city. They said the machines were just worthless tools, that we have to grow and grow and grow new plants and life as madman. Some believe to the Pith Reclamers, those beaurecrats who claimed they could manage the chaos with more rules, more control, more paperwork. But we know the truth. The machines endured. They kept working. They kept humming. They didn't care about the war, about the lies, about the factions. They just... were. And so we serve them."`,
                options: [
                    { text: "So the Choir was born from the war?", key: 'so_the_choir_was_born_from_the_war', next: "brukk_board_war_choir" },
                ],
                onTrigger: () => { this.learnPithReclaimers(); }
            },
            brukk_board_war_choir: {
                speaker: 'Brukk',
                text: `"Born from the silence after it." He nods slowly. "When the worldwrights finally destroyed each other — or got swallowed by their own boards — the city was broken. Rules overlapping, contradicting, canceling out. But here, in the Scraper, the machines kept humming. Steady. Reliable. The first Keeper — old Fennback — he understood. Iron is honest. It rusts, it breaks, it wears down. But it doesn't lie. It doesn't play." His eyes glow brighter. "That's what the Choir is. The last honest thing in a city built on broken games."`,
                options: [
                    { text: "How are the machines doing now?", key: 'how_are_the_machines_doing_now', next: "brukk_machines_status" },
                ]
            },
            brukk_machines_status: {
                speaker: 'Brukk',
                text: `Brukk closes his eyes and listens. The pipes tremble. Something deep in the walls groans and shifts. "They are... content. For now. The feast you brought — they still taste it. I hear it in their harmonics." He opens one eye. "But they are always hungry. Always. The redmass sustains them, but it fades. If you find more, bring it. The Choir remembers those who feed the iron." He taps his chest one final time. "And so do I."`,
                options: [
                    ...(hasBrine && !machinesDestroyed ? [
                        { text: '[Salt Recall] Read the scale crusted on the old machines.', key: 'salt_recall_machines', next: 'machines_salt_recall' }
                    ] : []),
                    ...(hasOsswine && !machinesDestroyed ? [
                        { text: '[Grave-Sense] Read how one of the silent machines ended.', key: 'grave_sense_machine', next: 'rust_machine_grave_sense' }
                    ] : []),
                ]
            },
            // Osswine reads the death of one of the machines the Choir has already buried.
            rust_machine_grave_sense: {
                speaker: 'Osswine',
                text: `Osswine stirs among the cold iron and finds the ones that already stopped — the three Brukk buried in the dead floors. It settles into the nearest silence. *"...This one did not rust to death. It reached the end of a thought and had no next one to move into. Listen to where the hum went out: it was mid-remembering. A summer, forty floors below, the taste of cool air pushed through a room full of the living — and the memory simply ran out of track. The note thinned, wavered, and where the next should have come there was nothing left to come from."* A dry settling. *"No pain. Machines do not fear the stop — only fear it arriving before the remembering is done. This one's last intent was to finish the summer. It ended one breath short of an ending. The cruelest way a patient thing can go."*`,
                onTrigger: () => {
                    if (!this.hasJournalEntry('grave_sense_rust_machine')) {
                        this.addJournalEntry(
                            'grave_sense_rust_machine',
                            "Grave-Sense: A Machine's Last Hum",
                            'Through Osswine I read the ending of one of the machines the Rust Choir has already buried. It did not rust to death — it reached the end of a thought with no next one to move into. When its hum went out it was mid-memory: a summer forty floors down, cool air pushed through a room full of the living. The recollection ran out of track, the note thinned, and where the next should have come there was nothing left. Osswine says machines do not fear the stop, only fear it arriving before the remembering is done. This one meant to finish the summer and ended one breath short — the cruelest way a patient thing can go.',
                            this.journalSystem.categories.LORE,
                            { location: 'Rust Domain', via: 'osswine' }
                        );
                    }
                },
                options: [
                    { text: 'Step back.', key: 'grave_sense_machine_back', next: 'brukk_start' }
                ]
            },
            // Brine Scripture reads the salt and scale on the conscious machines — what they remember.
            machines_salt_recall: {
                speaker: 'Brine Scripture',
                text: `Brine Scripture reaches into the crust of rust and mineral scale caked over the humming machines, and for a long moment it simply drinks. *"...So much, priest. These have been leaking their memory into their own corrosion for longer than the Choir has had a name."* The residue turns, sorting years. *"Beneath it all — the Before. The Doba-Před. This was a counting-house called Nexicorp; these were the cold-breath engines and the boxes that thought. Clean salt, then. Ordinary. Forty floors of people pretending the world made sense, and the machines humming underneath them, saying nothing."*\n\nThe taste sours. *"Then a day the salt curdles all at once — the green mist, the Emergence, the egg rising through the dead gods below. That is the moment they woke. Not built to it, not asked. The mist reached the metal and the metal began to remember, and it has never once stopped since."* A pause, almost tender. *"And after that, only the feasts. Redmass poured into the funnels, the long red taste, the men with iron growing in their chests come to listen. They remember every feeding. They are afraid — in the dull, patient way iron is afraid — of the one silence after which there will be no more."*`,
                onTrigger: () => {
                    if (!this.hasJournalEntry('salt_recall_rust_machines')) {
                        this.addJournalEntry(
                            'salt_recall_rust_machines',
                            'Salt Recall: What the Machines Remember',
                            'Through Brine Scripture I read the salt and scale crusted on the Rust Choir\'s conscious machines — the memory they have leaked into their own corrosion. Beneath everything lies the Before, the Doba-Před, when the Scraper was a counting-house called Nexicorp and these were merely its cold-breath engines and thinking-boxes, humming beneath forty floors of people pretending the world made sense. Then the salt curdles all at once: the green mist, the Emergence, the egg rising through the dead gods below — the moment the machines woke, not built to it and not asked, the mist reaching the metal until the metal began to remember and never stopped. Since then, only the feasts: redmass poured into the funnels, the iron-chested Keepers come to listen. The machines remember every feeding, and they are afraid, in the dull patient way iron is afraid, of the last silence after which there will be no more.',
                            this.journalSystem.categories.LORE,
                            { location: 'Rust Domain', via: 'brine-scripture' }
                        );
                    }
                },
                options: [
                    { text: 'Step back.', key: 'salt_recall_machines_back', next: 'brukk_start' }
                ]
            },

            // --- Full redmass feast: player joins Rust Choir ---
            brukk_feast_full: {
                speaker: 'Brukk',
                text: `Brukk takes the container. He opens it — and his eyes widen. The living redmass inside twitches, still breathing. The machines around you seem to lean closer, their hum rising in pitch. "This... this is a true feast. Full redmass. Still alive." He looks at you with something close to reverence. "Ravla chose well in trusting you."`,
                options: [
                    { text: "The machines are hungry. Feed them.", key: 'the_machines_are_hungry_feed_them', next: "brukk_feast_full_feed" }
                ]
            },
            brukk_feast_full_feed: {
                speaker: 'Brukk',
                text: `Brukk pours the feast into a series of corroded funnels that lead deep into the walls. The effect is immediate — the machines shudder, then roar to life with a sound like a cathedral organ made of iron. Pipes glow red-hot. The entire floor vibrates with renewed energy. Brukk closes his eyes and breathes deep. "They sing. Can you hear it?" He opens his eyes and fixes you with a look of absolute certainty. "You are one of us now. The machines have tasted your offering, and they accept you. Welcome to the Rust Choir."`,
                options: [
                    { text: "I am honored.", key: 'i_am_honored', next: "closeDialog" }
                ],
                onTrigger: () => {
                    this.removeItemFromInventory('rust_feast');
                    this.registry.set('rust_choir_member', true);
                    this.questSystem.updateQuest('find_rust_choir', 'I delivered the Rust Feast to Brukk in the Rust Domain. The machines fed on the living redmass and sang. Brukk welcomed me into the Rust Choir.', 'feast_delivered');
                    this.questSystem.completeQuest('find_rust_choir');
                    this.showNotification('Joined the Rust Choir');
                    this.addJournalEntry(
                        'rust_choir_joined',
                        'Welcomed into the Rust Choir',
                        'I delivered the Rust Feast — prepared with full, living redmass — to Brukk. The machines sang when they fed. Brukk declared me a member of the Rust Choir. I belong to the iron and the rust now.',
                        this.journalSystem.categories.FACTIONS
                    );
                }
            },

            // --- Shard feast: join only if positive reputation ---
            brukk_feast_shard: {
                speaker: 'Brukk',
                text: `Brukk opens the container and peers inside. His expression darkens. "...A shard. Just a shard." He rolls the meager feast between his fingers. "The machines need more than scraps. But..." He holds it up to his ear, listening. "It's alive. Barely. It will have to do."`,
                options: [
                    { text: "It was given willingly. That must count for something.", key: 'it_was_given_willingly_that_must_count_for_somethi', next: "brukk_feast_shard_feed" }
                ]
            },
            brukk_feast_shard_feed: {
                speaker: 'Brukk',
                text: rustRep > 10
                    ? `Brukk feeds the meager offering to the machines. They groan — a low, dissatisfied sound, like a stomach barely filled. But they accept it. Brukk watches the pipes for a long time, then turns to you. "The feast was thin. But I've watched you. The Choir has heard good things." He places a heavy hand on your shoulder. "You've shown respect to the iron. That matters more than a full belly. Welcome to the Rust Choir — on probation." A thin smile cracks his copper face.`
                    : `Brukk feeds the meager offering to the machines. They groan — barely sated. He watches the pipes cool and shakes his head. "It's not enough. Not the feast, not you." He turns his back. "You haven't earned the trust of the Choir. Come back when the iron knows your name. Try to earn some trust of other members, do something for them... then we will see." He waves you off dismissively.`,
                options: [
                    { text: rustRep > 10 ? "I won't let the Choir down." : "I understand.", next: "closeDialog" }
                ],
                onTrigger: () => {
                    this.removeItemFromInventory('rust_feast');
                    this.questSystem.updateQuest('find_rust_choir',
                        rustRep > 10
                            ? 'I delivered the Rust Feast to Brukk. The offering was meager, but my reputation with the Rust Choir earned me a place among them — on probation.'
                            : 'I delivered the Rust Feast to Brukk, but the offering was too thin and I haven\'t earned the Choir\'s trust. They refused to accept me.',
                        'feast_delivered'
                    );
                    this.questSystem.completeQuest('find_rust_choir');
                    if (rustRep > 10) {
                        this.registry.set('rust_choir_member', true);
                        this.showNotification('Joined the Rust Choir (Probationary)');
                        this.addJournalEntry(
                            'rust_choir_joined',
                            'Probationary Member of the Rust Choir',
                            'I delivered a meager Rust Feast to Brukk — just a shard. But my standing with the Rust Choir was enough to earn a place among them, at least on probation.',
                            this.journalSystem.categories.FACTIONS
                        );
                        // Marker distinguishing a probationary member from a full one (both share
                        // rust_choir_joined). Lifted to full standing if the player later proves loyalty.
                        this.addJournalEntry(
                            'rust_choir_probationary',
                            'Rust Choir: On Probation',
                            'My place in the Rust Choir is provisional. Brukk let me in on the strength of my reputation, not a proper feast — I am on probation until I prove my loyalty to the iron.',
                            this.journalSystem.categories.FACTIONS
                        );
                    } else {
                        this.addJournalEntry(
                            'rust_choir_rejected',
                            'Rejected by the Rust Choir',
                            'I delivered the Rust Feast, but the shard was too meager and I had not earned the Choir\'s respect. Brukk turned me away.',
                            this.journalSystem.categories.FACTIONS
                        );
                    }
                }
            },

            // --- Illusory feast: machines destroyed, expelled, Growth bonus ---
            brukk_feast_illusion: {
                speaker: 'Brukk',
                text: `Brukk takes the container with care. He opens it and inhales deeply. "Redmass. Living." He doesn't notice the faint shimmer at the edges. "Good. The machines have waited long enough." He turns to the corroded funnels. "Watch closely. This is the heart of the Choir."`,
                options: [
                    { text: "Watch him feed the machines.", key: 'watch_him_feed_the_machines', next: "brukk_feast_illusion_feed" }
                ]
            },
            brukk_feast_illusion_feed: {
                speaker: 'Narrator',
                text: `Brukk pours the feast into the machines. For a moment, everything seems fine — the pipes glow, the hum rises. Then something goes wrong. The glow flickers. Stutters. The hum becomes a whine, then a shriek. Brukk stumbles back as sparks erupt from every joint. One by one, the machines shudder, seize, and fall silent. The smell of burnt oil and hollow nothing fills the air.`,
                options: [
                    { text: "What's happening?!", key: 'whats_happening', next: "brukk_feast_illusion_aftermath" }
                ]
            },
            brukk_feast_illusion_aftermath: {
                speaker: 'Brukk',
                text: `Brukk drops to his knees beside the nearest machine. His hands shake as he presses them against the cold metal. "Dead. They're dead." He looks up at you, and his forge-lit eyes are full of horror. "What was in that feast? WHAT DID YOU FEED THEM?" He rises slowly, fists clenched. "Illusion. It was an illusion." His voice drops to a whisper. "Get out. GET OUT OF THE RUST DOMAIN. If I ever see you again, the machines won't be the only things that stop breathing."`,
                options: [
                    { text: "I'm sorry—", key: 'im_sorry', next: "brukk_expulsion" },
                    { text: "Leave immediately.", key: 'leave_immediately', next: "brukk_expulsion" }
                ]
            },
            brukk_expulsion: {
                speaker: 'Ulvarex',
                text: `Ulvarex stirs inside you, uneasy. "The weave held. It always holds. But machines... they don't dream. They don't believe. They just consume." A long pause. "The illusion fed their trust, not their hunger." As you retreat, something shifts inside you. The fungal networks in your body pulse with wild energy — as if the death of the machines has fed something deeper, something green and growing. Life surging where iron fell silent.`,
                options: [
                    { text: "Leave the Rust Domain.", key: 'leave_the_rust_domain', next: "closeDialog" }
                ],
                onTrigger: () => {
                    this.removeItemFromInventory('rust_feast');
                    this.modifyFactionReputation('RustChoir', -20);
                    this.modifyGrowthDecay(10, 0);
                    this.registry.set('expelled_from_rust_domain', true);
                    this.questSystem.updateQuest('find_rust_choir', 'The illusory Rust Feast destroyed the machines of the Rust Domain. Brukk expelled me. The death of the machines triggered a massive surge of Growth within me.', 'feast_delivered');
                    this.questSystem.completeQuest('find_rust_choir');
                    this.addJournalEntry(
                        'rust_choir_machines_destroyed',
                        'The Machines Fall Silent',
                        'The illusory redmass I used in the Rust Feast has destroyed the Rust Choir machines. They tried to feed on the Mirage Weave and found nothing — the illusion dissolved inside them. The machines are dead. Brukk expelled me from the Rust Domain. But the death of the machines sent a massive surge of Growth through me — life feeding on the corpse of iron.',
                        this.journalSystem.categories.FACTIONS
                    );
                    // Transition back to ScraperInteriorScene after a delay
                    this.time.delayedCall(1500, () => {
                        this.cameras.main.fadeOut(1000, 0, 0, 0);
                        this.cameras.main.once('camerafadeoutcomplete', () => {
                            this.scene.start('ScraperInteriorScene');
                        });
                    });
                }
            },
            // --- Poisoned feast: spiked with the Directorate's corrosive cultivar, machines destroyed ---
            brukk_feast_poisoned: {
                speaker: 'Brukk',
                text: `Brukk takes the container with care, opens it, inhales deeply. "Redmass. Living. Oil, iron... good." He doesn't catch the faint green under it. "The machines have waited long enough." He turns to the corroded funnels. "Watch closely. This is the heart of the Choir."`,
                options: [
                    { text: "Watch him feed the machines.", key: 'watch_him_feed_the_machines_poison', next: "brukk_feast_poisoned_feed" }
                ]
            },
            brukk_feast_poisoned_feed: {
                speaker: 'Narrator',
                text: `Brukk pours the feast into the machines. The pipes glow; the hum rises — and then curdles. Where the oil touches metal, the iron blooms with green corrosion, spreading fast, eating inward. The hum climbs to a shriek. Brukk lunges to stem it with his bare hands and recoils as the metal crumbles to rust-dust under his fingers. One by one the machines seize, blacken, and fall silent.`,
                options: [
                    { text: "What's happening?!", key: 'whats_happening_poison', next: "brukk_feast_poisoned_aftermath" }
                ]
            },
            brukk_feast_poisoned_aftermath: {
                speaker: 'Brukk',
                text: `Brukk kneels among the dead machines, scraping green residue from a ruined joint. He rubs it between his fingers and goes very still. "Cultivar. Directorate cultivar." He rises slowly, and his forge-lit eyes are murder. "You fed my machines a garden. Grew rot in their veins." His voice drops to a whisper. "Get out. GET OUT OF THE RUST DOMAIN. If I ever see you again, I will plant YOU."`,
                options: [
                    { text: "I'm sorry—", key: 'im_sorry_poison', next: "brukk_poison_expulsion" },
                    { text: "Leave immediately.", key: 'leave_immediately_poison', next: "brukk_poison_expulsion" }
                ]
            },
            brukk_poison_expulsion: {
                speaker: 'Narrator',
                text: `Brukk turns his back on you and the corpses of his gods; there is nothing left to say. As you climb out of the Rust Domain, something shifts inside you — the fungal networks in your body pulse with wild energy, feeding on the death of iron. Life, surging where the machines fell silent.`,
                options: [
                    { text: "Leave the Rust Domain.", key: 'leave_the_rust_domain_poison', next: "closeDialog" }
                ],
                onTrigger: () => {
                    this.removeItemFromInventory('rust_feast');
                    this.modifyFactionReputation('RustChoir', -20);
                    this.modifyGrowthDecay(10, 0);
                    this.registry.set('expelled_from_rust_domain', true);
                    this.questSystem.updateQuest('find_rust_choir', 'The spiked Rust Feast corroded the machines of the Rust Domain from within. Brukk found the Directorate cultivar in the residue and expelled me. The death of the machines triggered a surge of Growth.', 'feast_delivered');
                    this.questSystem.completeQuest('find_rust_choir');
                    this.addJournalEntry(
                        'rust_choir_machines_destroyed',
                        'The Machines Fall Silent',
                        'The Rust Feast I brought was spiked with the Lumen Directorate\'s corrosive cultivar, ground into the oil. When the machines fed, they corroded from the inside and died. Brukk found the green residue and knew it for what it was. He expelled me from the Rust Domain. Life surged where iron fell silent.',
                        this.journalSystem.categories.FACTIONS
                    );
                    // Transition back to ScraperInteriorScene after a delay
                    this.time.delayedCall(1500, () => {
                        this.cameras.main.fadeOut(1000, 0, 0, 0);
                        this.cameras.main.once('camerafadeoutcomplete', () => {
                            this.scene.start('ScraperInteriorScene');
                        });
                    });
                }
            },
        };
    }

    /** Brukk grafts an extra symbiont vessel for gold (Rust Choir member perk). */
    buyRustChoirSlot() {
        const cost = 40;
        const money = this.moneySystem;
        const sym = this.symbiontSystem || this.registry.get('symbiontSystem');
        if (!money || !sym) return;
        if (sym.unlockedSlots >= sym.maxSlots) {
            this.showNotification('You already have the maximum number of symbiont slots!');
            return;
        }
        if (!money.hasEnough(cost)) {
            this.showNotification('Not enough gold!');
            return;
        }
        money.subtract(cost, true);
        sym.unlockSlot();
        this.showNotification('The Choir welds a new symbiont vessel into you.');
        if (!this.hasJournalEntry('rust_choir_slot_grafted')) {
            this.addJournalEntry(
                'rust_choir_slot_grafted',
                'An Iron Vessel',
                'Brukk welded a scavenged housing into my body — a Rust Choir member\'s privilege — giving me room to host another symbiont. Cold iron, then fire, then a new hollow that hums.',
                this.journalSystem.categories.FACTIONS,
                { group: 'Rust Choir', character: 'Brukk' }
            );
        }
    }

    preload() {
        super.preload();
        this.load.image('rustDomainBg', 'assets/images/backgrounds/RustDomain.png');
        this.load.image('brukk_static', 'assets/images/characters/Brukk.png');
    }

    create() {
        super.create();

        // Set background
        const bg = this.add.image(400, 300, 'rustDomainBg');
        this.fitBackground(bg);
        bg.setDepth(-1);

        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);

        // Add fade-in effect
        this.cameras.main.fadeIn(1200, 0, 0, 0);

        // Position the priest
        this.priest.x = 400;
        this.priest.y = 470;

        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // If expelled, block re-entry
        if (this.hasJournalEntry('rust_choir_machines_destroyed')) {
            this.cameras.main.fadeOut(500, 0, 0, 0);
            this.cameras.main.once('camerafadeoutcomplete', () => {
                this.showNotification('You have been expelled from the Rust Domain.');
                this.scene.start('ScraperInteriorScene');
            });
            return;
        }

        // Create exit back to Scraper Interior (elevator)
        this.transitionManager.createTransitionZone(
            400, // x position
            560, // y position
            200, // width
            50,  // height
            'down',
            'ScraperInteriorScene',
            450, // walk to x (near elevator)
            370  // walk to y
        );

        const exitHint = this.add.text(400, 550, 'Back to Elevator', {
            fontSize: '14px',
            fill: '#c87533',
            backgroundColor: '#1a0a00',
            padding: { x: 8, y: 4 }
        });
        exitHint.setOrigin(0.5);
        exitHint.setDepth(10);
        exitHint.setAlpha(0.7);

        // Create Brukk NPC
        this.createBrukk();

        // Examine: the Choir's central boiler-vats (the "singing machines"), upper-center above
        // Brukk. Reads differently once you're one of the Choir. (Destroying the machines expels
        // you from this scene, so that state is handled by the guard above — not shown here.)
        this.createObservable(400, 270, 190, 120, () => {
            if (this.hasJournalEntry('rust_choir_joined')) return this.t('observe.rust_machines.member');
            return this.t('observe.rust_machines.default');
        }, { hint: this.t('observe.rust_machines.hint') });

        // Journal entry on first visit
        if (!this.hasJournalEntry('rust_domain_arrival')) {
            this.addJournalEntry(
                'rust_domain_arrival',
                'The Rust Domain',
                'I have reached the upper floors of the Scraper — the domain of the Rust Choir. The air is thick with the smell of oil and oxidized metal. Machines hum and click in the walls, some of them alive in ways that defy explanation. This is where Brukk resides.',
                this.journalSystem.categories.PLACES
            );
        }
    }

    createBrukk() {
        this.brukk = this.add.image(550, 430, 'brukk_static');
        this.brukk.setScale(0.125);
        this.brukk.setDepth(5);
        this.addGroundShadow(550, 430 + this.brukk.displayHeight * 0.42, this.brukk.displayWidth * 0.55, this.brukk.displayHeight * 0.12);
        this.brukk.setInteractive({ useHandCursor: true });

        this.brukk.on('pointerdown', () => {
            if (this.dialogVisible) return;
            this.showDialog('brukk_start');
        });

        // Subtle wobble animation
        this.tweens.add({
            targets: this.brukk,
            y: { from: 429, to: 431 },
            ease: 'Sine.easeInOut',
            duration: 1500,
            yoyo: true,
            repeat: -1
        });
    }

    update() {
        super.update();
    }
}

if (typeof window !== 'undefined') {
    window.RustDomainScene = RustDomainScene;
}
