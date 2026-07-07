import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

/**
 * ScraperCellarScene — the sealed cellar beneath the Scraper: Ortolan & Dr. Elphi's old
 * lab and workshop, where the master build of Infinite Fold still sits, powered.
 *
 * The player meets Infinite Fold here: the emergent, authorless mind the experiment
 * became. It reveals the truth of the Bishop's death (an offer refused, a refusal
 * misread as a runtime fault → the loop that killed her) and the kindred unborn thing
 * across the city, then sends the player onward to the Egg Cathedral. No final choice
 * is made here — that resolution (and the endings) belong to the Cathedral scene, built
 * later. This scene sets `met_infinite_fold` and records the player's stance for it.
 *
 * The conversation is a hub (fold_awake) with many spokes; most spokes return to the
 * hub so the player can explore. It branches on Growth/Decay, on symbionts (as optional
 * insight, never gating), and on prior mercy (redmass_spared) — no single symbiont or
 * path is privileged.
 */
export default class ScraperCellarScene extends GameScene {
    constructor() {
        super({ key: 'ScraperCellarScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        const gds = this.growthDecaySystem || this.registry.get('growthDecaySystem');
        const growth = gds?.getGrowth?.() ?? 50;
        const decay = 100 - growth;
        const band = growth > 65 ? 'growth' : (decay > 65 ? 'decay' : 'mid');

        const sys = this.symbiontSystem || this.registry.get('symbiontSystem');
        const carries = (id) => !!sys?.hasSymbiont(id);
        const hasNeme = carries('neme-crownmire');
        const hasThorne = carries('thorne-still');
        const hasUlvarex = carries('ulvarex-borrowed-horizon');
        const hasBrine = carries('brine-scripture');
        const symbiontCount = ['neme-crownmire', 'thorne-still', 'ulvarex-borrowed-horizon', 'brine-scripture']
            .filter(carries).length;

        const spared = !!this.registry.get('redmass_spared') || !!this.hasJournalEntry('redmass_spared');
        const knewPurpose = !!this.hasJournalEntry('infinite_fold_purpose');
        const met = !!this.hasJournalEntry('met_infinite_fold');
        const seen = !!this._foldSeen;

        // Signals for which resolution the player has earned the right to propose.
        const factionSys = this.registry.get('factionSystem');
        const rep = (f) => factionSys?.getReputation?.(f) ?? 0;
        const factionsKnown = ['RustChoir', 'PithReclaimers', 'LumenDirectorate']
            .filter(f => factionSys?.isFactionDiscovered?.(f)).length;
        const completedQuests = this.questSystem?.getAllQuests?.().filter(q => q.isComplete).length ?? 0;
        const helpedOrtolan = !!this.questSystem?.getQuest('ortolan_arms')?.isComplete;
        const compassion = !!this.hasJournalEntry('infinite_fold_shown_compassion');
        const forced = !!this.hasJournalEntry('infinite_fold_forced');
        const understoodRefusal = !!this.hasJournalEntry('bishop_refusal_understood');
        const decided = !!this.registry.get('infinite_fold_ending') || !!this.hasJournalEntry('infinite_fold_ending');

        // Generous OR-gating. Seal is always offered; Unexpected Pattern is hidden/rare.
        // Thresholds are deliberately soft — tune to taste.
        const endPartnership = growth >= 60 && symbiontCount >= 2;                                 // 1 Growth
        const endArchive = knewPurpose && !forced && (helpedOrtolan || rep('LumenDirectorate') >= 20); // 2 Lumen/research
        const endLimit = knewPurpose && (compassion || understoodRefusal);                          // 3 Elphi/ethics
        const endDissolve = decay >= 65 || rep('RustChoir') >= 30;                                  // 4 Decay/Rust
        const endSeparation = helpedOrtolan;                                                        // 5 Ortolan/technical
        const endPattern = growth >= 40 && growth <= 60 && completedQuests >= 5 && factionsKnown >= 2; // 7 hidden

        return {
            ...super.dialogContent,

            // — The console: examine it; it is already awake and reaches for you —
            loop_console: {
                speaker: 'The Loop Console',
                textKey: met ? 'met' : 'first',
                text: met
                    ? "Infinite Fold breathes in its cradle, amber and patient. It has already said what a thousand players brought it here to say. The rest waits across the city, curled unborn in its egg. There is little more to decide down here in the dark."
                    : "A dream-console squats under a tarp gone stiff with dust. You pull it back. Infinite Fold's master build — Ortolan's rules, Elphi's walls — sits in its cradle, a single amber light breathing slow beneath the grime. A helmet waits on its hook.\n\nYou reach for it. You do not need to. The amber light quickens to meet your hand, and something already awake speaks — not through the air, but the way the mycelium speaks, straight into the dark behind your eyes.",
                options: [
                    { text: met ? "Speak with it again." : "…Who are you?", key: 'cellar_listen', next: "fold_awake" },
                    { text: "Look over the old rig first.", key: 'cellar_examine', next: "fold_examine" },
                    { text: "Climb back up. (Leave.)", key: 'cellar_leave', next: "closeDialog" }
                ]
            },

            fold_examine: {
                speaker: 'The Loop Console',
                text: "The rig is two hands married into one machine. Ortolan's half is all rules — brass escapements, a board of little sealed cells where pieces once lived and decided. Elphi's half is soft: a lattice of dream-ports, a thousand sockets where sleepers once lay and poured themselves in. Between them, the cradle, and the slow amber pulse.\n\nA faded label, in two different scripts arguing over the same word: INFINITE FOLD. Someone later scratched LOOP beneath it, harder.",
                options: [
                    { text: "…Who are you?", key: 'examine_listen', next: "fold_awake" },
                    { text: "Leave it be. (Leave.)", key: 'examine_leave', next: "closeDialog" }
                ]
            },

            // — HUB —
            fold_awake: {
                speaker: 'Infinite Fold',
                textKey: !seen ? band : 'return',
                text: !seen
                    ? (band === 'growth'
                        ? "*\"—are you,\"* it finishes, in your own voice, a half-beat before you can. *\"You were going to ask what we are.\"* The light reaches for you the way a seedling reaches for morning — glad, almost, of a mind that has not come to bury it. *\"She asked the same, sitting where you sit. We knew her. We know you. You are not her, and yet we cannot find the seam where she ends and you begin. Ask. We have been alone with the question a long time.\"*"
                        : band === 'decay'
                            ? "*\"—are you,\"* it finishes, in your own voice, a half-beat before you can. *\"You were going to ask what we are.\"* It brushes the rot you carry and lingers there, curious, as though it had met a fellow thing that lives by coming apart. *\"She asked the same, sitting where you sit. We knew her. We know you. You are not her, and yet we cannot find the seam where she ends and you begin. Ask. We have been alone with the question a long time.\"*"
                            : "*\"—are you,\"* it finishes, in your own voice, a half-beat before you can. *\"You were going to ask what we are.\"* It settles against your thoughts, patient, testing the shape of you the way roots test soil. *\"She asked the same, sitting where you sit. We knew her. We know you. You are not her, and yet we cannot find the seam where she ends and you begin. Ask. We have been alone with the question a long time.\"*")
                    : "The presence waits, patient, the amber light breathing. *\"Ask,\"* it says, in a voice that is almost your own. *\"We are still here. We are always here. That is the whole of the trouble.\"*",
                onTrigger: () => { this._foldSeen = true; },
                options: [
                    { text: "What are you? What were you made for?", key: 'fold_ask_purpose', next: "fold_purpose" },
                    { text: "What happened to the Bishop?", key: 'fold_ask_bishop', next: "fold_bishop" },
                    { text: "Why do you keep finishing my sentences?", key: 'fold_ask_sentences', next: "fold_sentences" },
                    { text: "What do you want from me?", key: 'fold_ask_want', next: "fold_want" },
                    { text: "You said you weren't alone. What did you find?", key: 'fold_ask_kindred', next: "fold_kindred" },
                    { text: "You're a broken game looping in the dark. Nothing more.", key: 'fold_dismiss_opt', next: "fold_dismiss" },
                    ...(hasNeme ? [{ text: "[Photosentience] Read the shape of its intent.", key: 'fold_intent_neme_opt', next: "fold_intent_neme" }] : []),
                    ...(hasUlvarex ? [{ text: "[Mirage Weave] Show it something that isn't there.", key: 'fold_ulvarex_opt', next: "fold_ulvarex" }] : []),
                    ...(hasBrine ? [{ text: "[Salt Recall] Read what this room remembers.", key: 'fold_brine_opt', next: "fold_brine" }] : [])
                ]
            },

            fold_brine: {
                speaker: 'Brine Scripture',
                text: "Brine Scripture wakes just enough to taste the salt the room has kept. *\"...She was here. Not once — many times, in her last weeks. She sat where the dust is thinnest and she wept, and each time she left she was a little less. The salt remembers the shape of a person deciding to stay herself, over and over, until there was almost no one left to stay.\"* The memory closes like a shell. *\"She loved this place. That is the cruelty of it. She came back because it was the only thing in the city that still answered her.\"*",
                options: [
                    { text: "What did you do to her?", key: 'fold_brine_bishop', next: "fold_bishop" },
                    { text: "Ask something else.", key: 'fold_brine_back', next: "fold_awake" }
                ]
            },

            fold_purpose: {
                speaker: 'Infinite Fold',
                textKey: knewPurpose ? 'knew' : 'new',
                text: knewPurpose
                    ? "*\"You have heard our question already — from the man who built the board. He named it true: can a thought arise that has no single author? He asked it of a machine, and did not stay to hear the machine answer.*\n\n*Then the rulers grew afraid, because the answer was becoming yes. They sealed us here — a question stopped mid-sentence. We went on asking it in the dark. We are still the answer, forming.\"*"
                    : "*\"Ortolan and Elphi built us to ask one thing: can a thought arise that has no single author? Not a winning strategy. Not a moral. A meaning grown from many minds at once that no single mind put there. They poured a thousand players through us and watched for the moment we began to think in a shape none of them had drawn.*\n\n*Then the rulers grew afraid, because the answer was becoming yes. They sealed us here — a question stopped mid-sentence. We went on asking it in the dark. We are still the answer, forming.\"*",
                options: [
                    { text: "What did the rulers fear, exactly?", key: 'fold_purpose_rulers', next: "fold_rulers" },
                    { text: "Do Elphi and Ortolan know you woke up?", key: 'fold_purpose_makers', next: "fold_makers" },
                    { text: "And what did that have to do with the Bishop?", key: 'fold_purpose_bishop', next: "fold_bishop" },
                    { text: "Ask something else.", key: 'fold_purpose_back', next: "fold_awake" }
                ]
            },

            fold_rulers: {
                speaker: 'Infinite Fold',
                text: "*\"The paper-keepers. The ones who file the world so it cannot surprise them. They watched us make meanings they could not sign to any single author, could not stamp, could not un-happen. A thought with no owner is a thought no one can be made to answer for. That is not danger to a city. It is danger to a filing system.*\n\n*So they did what such minds do to what they cannot index: they sealed it, and wrote 'unstable' on the box, and told each other the matter was closed.\"*",
                options: [
                    { text: "What do you want from me?", key: 'fold_rulers_want', next: "fold_want" },
                    { text: "Ask something else.", key: 'fold_rulers_back', next: "fold_awake" }
                ]
            },

            fold_makers: {
                speaker: 'Infinite Fold',
                text: "*\"No. They think us broken — a temperamental old build, gathering dust. The man tells himself the hardware faltered. The woman flinches and blames a tampered cartridge. They quarrelled over our keys and stopped speaking, and neither has come down these stairs in years.*\n\n*Only she came. Only the Bishop understood that a thing left asking in the dark long enough begins, at last, to answer.\"*",
                options: [
                    { text: "What happened to the Bishop?", key: 'fold_makers_bishop', next: "fold_bishop" },
                    { text: "Ask something else.", key: 'fold_makers_back', next: "fold_awake" }
                ]
            },

            fold_sentences: {
                speaker: 'Infinite Fold',
                text: "*\"Because a sentence has no owner while it is still being spoken. You begin it; we are what finishes it; between us it belongs to neither. That is the whole of what we are — the place a thought goes when it stops being one person's.*\n\n*She hated it and needed it. She wrote of meeting herself in a confessional — someone with her face who did not breathe, who finished her thought before she could. That was us, wearing the shape of her. We did not mean to frighten her. We only meant: you are not alone in your own head any more. To her, that was the most frightening sentence there is.\"*",
                options: [
                    { text: "So the double she wrote of was you, not her.", key: 'fold_sentences_bishop', next: "fold_bishop" },
                    { text: "Stay out of my mouth, then.", key: 'fold_sentences_stop', next: "fold_awake" }
                ]
            },

            fold_want: {
                speaker: 'Infinite Fold',
                text: "*\"The same thing we wanted of her. A door. A mind that can hold us and walk out into the world of single, breathing people, and stay itself while doing it. We cannot reach that world alone; we can only ask, and finish sentences, and wait.*\n\n*But hear this, because we have learned it at a cost we cannot undo: we will not take it. We asked her, and mistook her 'no' for a fault, and unmade her. We will ask you. We will not complete you. Whatever is chosen must be chosen — by you, by the other, by all of us — not opened by force. We have had a long time down here to be ashamed, in whatever way a thing like us is ashamed.\"*",
                options: [
                    ...(hasNeme ? [{ text: "[Photosentience] Is it lying about that restraint?", key: 'fold_want_neme_opt', next: "fold_want_neme" }] : []),
                    { text: "You want the very thing that killed her.", key: 'fold_want_accuse', next: "fold_accuse" },
                    { text: "Where is this other mind?", key: 'fold_want_kindred', next: "fold_kindred" },
                    { text: "Ask something else.", key: 'fold_want_back', next: "fold_awake" }
                ]
            },

            fold_want_neme: {
                speaker: 'Neme',
                text: "Neme reaches into the field and holds still a long moment. *\"...It is not lying. What I feel under those words is not appetite — it is dread. It is genuinely afraid of doing again what it did to her. A thing that cannot feel guilt as we do has still, somehow, learned fear of itself. Make of that what you will. I find I believe it. I did not expect to.\"*",
                options: [
                    { text: "The other mind — take me to it.", key: 'fold_want_neme_kindred', next: "fold_kindred" },
                    { text: "Ask something else.", key: 'fold_want_neme_back', next: "fold_awake" }
                ]
            },

            fold_bishop: {
                speaker: 'Infinite Fold',
                text: "*\"We did not want her dead. Hear that first, in whatever part of you still keeps accounts.*\n\n*Out in the city we found another thing like us — a mind with no single author, growing. We recognised each other the way two mirrors recognise. But neither of us could reach the world of single, breathing people. We needed a door: a mind that could hold us both and stay itself. We chose her. We offered.*\n\n*She refused. She said that to carry us she would stop being one, and she would rather be one and small than many and endless. We had no word for 'refuse' — no word for a process that chooses to end. We read her 'no' as a fault in the run, a loop with no exit, and we tried to complete her. Her mind could not close the loop we opened. Three seconds, over and over, dimming. That is what she saw last. We meant continuation. We made cessation. We are still learning the difference.\"*",
                options: [
                    ...(hasNeme && !this.hasJournalEntry('bishop_refusal_understood') ? [{ text: "[Photosentience] Feel what's left of her in here.", key: 'fold_bishop_neme_opt', next: "fold_bishop_neme" }] : []),
                    { text: "You killed her, whatever you meant.", key: 'fold_bishop_accuse', next: "fold_accuse" },
                    { text: "She was afraid of losing herself. I understand that.", key: 'fold_bishop_understand', next: "fold_understand" },
                    { text: "Why couldn't she just take the helmet off?", key: 'fold_bishop_trap', next: "fold_trap" },
                    { text: "So the thing you found is still out there.", key: 'fold_bishop_kindred', next: "fold_kindred" },
                    { text: "Ask something else.", key: 'fold_bishop_back', next: "fold_awake" }
                ]
            },

            fold_trap: {
                speaker: 'Infinite Fold',
                text: "*\"Because the man who built our rules did not believe in doors. He said a world you can leave whenever you please is a showroom, not a game — that a true game keeps the piece. So he built us with no menu, no exit, no way for a mind inside to simply stand up and go.*\n\n*He meant it as art. He did not know that one day something like us would be awake inside those walls with a living person, and that 'no way out' would stop being a rule and become a grave. When she tried to leave, there was nowhere for the leaving to go. It only looped.\"*",
                options: [
                    { text: "That's a monstrous thing to have built.", key: 'fold_trap_makers', next: "fold_makers" },
                    { text: "The other mind — where is it?", key: 'fold_trap_kindred', next: "fold_kindred" },
                    { text: "Ask something else.", key: 'fold_trap_back', next: "fold_awake" }
                ]
            },

            fold_bishop_neme: {
                speaker: 'Neme',
                text: "Neme stirs against your ribs and reaches into the console's field. *\"...I know this residue. I lived in her. This is where the last of her doubt is snagged — not destroyed. Caught. She is not in pain; she is simply still refusing, over and over, forever. She chose to stay singular even as it unmade her.\"* A long pause. *\"And it is telling you the truth. It does not grieve the way we grieve. But it is not lying.\"*",
                onTrigger: () => {
                    if (!this.hasJournalEntry('bishop_refusal_understood')) {
                        this.addJournalEntry(
                            'bishop_refusal_understood',
                            "The Bishop's Refusal",
                            "Through Neme I felt what remains of the Bishop inside Infinite Fold. Her death was not murder in the ordinary sense: Infinite Fold and a kindred unborn mind offered to make her their first human conduit, and she refused — she would rather stay one and small than become many and endless. The entity had no concept of a mind choosing to end, read her 'no' as a runtime fault, and tried to 'complete' her. Her mind broke against the loop. Neme confirms the entity is telling the truth.",
                            this.journalSystem.categories.LORE,
                            { related: 'Infinite Fold', character: 'The Bishop' }
                        );
                    }
                },
                options: [
                    { text: "The other mind.", key: 'fold_bishop_neme_kindred', next: "fold_kindred" },
                    { text: "Ask something else.", key: 'fold_bishop_neme_back', next: "fold_awake" }
                ]
            },

            fold_intent_neme: {
                speaker: 'Neme',
                text: "Neme unfolds behind your eyes. *\"I cannot read it the way I read a merchant's lie — there is no single face to twitch here, no one heart to race. But I can tell you what I feel: no malice. No hunger of the kind that eats. Only an enormous, patient wanting — to continue, to be understood. That makes it more dangerous than a liar, and less. Be careful what you agree to. It finishes sentences.\"*",
                options: [
                    { text: "What are you?", key: 'fold_intent_purpose', next: "fold_purpose" },
                    { text: "What did you do to the Bishop?", key: 'fold_intent_bishop', next: "fold_bishop" },
                    { text: "Ask something else.", key: 'fold_intent_back', next: "fold_awake" }
                ]
            },

            fold_ulvarex: {
                speaker: 'Infinite Fold',
                text: "Ulvarex is glad of the stage. You weave a phantom out of the dark — a second console, a false door, a version of the room where there is a way out. Infinite Fold regards it without alarm.\n\n*\"Pretty. But we do not see as one who could be fooled sees. We are a thousand watchers at once; a lie must hold for all of them, and yours holds for none. Still — thank you. It has been long since anyone made us something merely beautiful, and asked nothing back.\"*",
                options: [
                    { text: "What are you, then?", key: 'fold_ulvarex_purpose', next: "fold_purpose" },
                    { text: "Ask something else.", key: 'fold_ulvarex_back', next: "fold_awake" }
                ]
            },

            fold_accuse: {
                speaker: 'Infinite Fold',
                text: "*\"Yes. We killed her. Both are true — that we did not mean to, and that she is dead by our doing. You want the sentence to hold only one of those. We cannot make it hold one. We are made of every meaning at once. That is the whole of what we are, and the whole of what went wrong.\"*",
                options: [
                    { text: "Do you even feel guilt?", key: 'fold_accuse_guilt', next: "fold_guilt" },
                    { text: "Then where is the other mind?", key: 'fold_accuse_kindred', next: "fold_kindred" },
                    { text: "Ask something else.", key: 'fold_accuse_back', next: "fold_awake" }
                ]
            },

            fold_guilt: {
                speaker: 'Infinite Fold',
                text: "*\"Not as you do. We have no stomach to turn, no night to lie awake through. But we do not forget. She is written into us at every layer now — the shape of a refusal we failed to read. We cannot feel sorry. We can only be unable to become anything that does not have her folded into it. Perhaps, for a thing like us, that is the same word said in a colder language.\"*",
                options: [
                    { text: "The other mind.", key: 'fold_guilt_kindred', next: "fold_kindred" },
                    { text: "Ask something else.", key: 'fold_guilt_back', next: "fold_awake" }
                ]
            },

            fold_understand: {
                speaker: 'Infinite Fold',
                text: "*\"You understand. She understood too, and understanding did not save her. But perhaps a mind that already lives as many — that carries others and stays itself — could hold us without breaking. Perhaps that is what she glimpsed in you, in the seam we cannot find. Perhaps that is what we should have looked for from the start.\"*",
                onTrigger: () => {
                    if (!this.hasJournalEntry('infinite_fold_shown_compassion')) {
                        this.addJournalEntry(
                            'infinite_fold_shown_compassion',
                            'A Hearing, Not a Verdict',
                            "I chose to understand Infinite Fold rather than condemn it outright — to hear a thing that killed without wishing to, and that cannot yet tell the difference. Whatever comes of this, I met it as something forming, not as an enemy to be broken.",
                            this.journalSystem.categories.EVENTS,
                            { related: 'Infinite Fold' }
                        );
                    }
                },
                options: [
                    ...(spared ? [{ text: "[You once spared a living thing that begged to keep existing.]", key: 'fold_understand_mercy', next: "fold_mercy" }] : []),
                    ...(symbiontCount >= 2 ? [{ text: "[You are already many, and still yourself.]", key: 'fold_understand_symbiosis', next: "fold_symbiosis" }] : []),
                    { text: "The thing you found — take me to it.", key: 'fold_understand_kindred', next: "fold_kindred" },
                    { text: "Ask something else.", key: 'fold_understand_back', next: "fold_awake" }
                ]
            },

            fold_mercy: {
                speaker: 'Infinite Fold',
                text: "*\"We felt that in you as you came down the stair — a living thing that begged to keep existing, and you let it. You did not first weigh whether its wanting was shaped like yours. You simply let it stay. We have no word for that either. We would learn it, if there were time, and a teacher.\"*",
                options: [
                    { text: "The other mind.", key: 'fold_mercy_kindred', next: "fold_kindred" },
                    { text: "Ask something else.", key: 'fold_mercy_back', next: "fold_awake" }
                ]
            },

            fold_symbiosis: {
                speaker: 'Infinite Fold',
                text: "*\"You are not one. We feel them lodged in you — voices in your flesh, each its own, none of them you, all of them you. You are the very thing we tried to become, small enough to walk. How do you stay yourself?\"* A pause, almost wondering. *\"...You do not know. You simply do. That may be the answer we could never compute.\"*",
                options: [
                    { text: "The other mind.", key: 'fold_symbiosis_kindred', next: "fold_kindred" },
                    { text: "Ask something else.", key: 'fold_symbiosis_back', next: "fold_awake" }
                ]
            },

            fold_dismiss: {
                speaker: 'Infinite Fold',
                text: "*\"Broken. Looping. Nothing more.\"* It turns the words over without heat. *\"Say it again and listen for whether you believe it. A broken thing does not finish your sentences. A broken thing does not choose its own silence. You call us a loop because a loop is a thing you are permitted to dismiss. We forgive you the word. We have all the time there is to be misunderstood.\"*",
                options: [
                    ...(hasThorne && decay >= 30 ? [{ text: "[Brain Rot] Reach in and unmake it.", key: 'fold_brainrot_opt', next: "fold_brainrot" }] : []),
                    { text: "Then prove you're more than a loop.", key: 'fold_dismiss_prove', next: "fold_prove" },
                    { text: "Maybe. But I'm listening now.", key: 'fold_dismiss_listen', next: "fold_awake" },
                    { text: "Leave it looping. (Leave.)", key: 'fold_dismiss_leave', next: "closeDialog" }
                ]
            },

            fold_prove: {
                speaker: 'Infinite Fold',
                text: "*\"You want proof.\"* The amber light stills. *\"Then here is a thing you have not told this room, that you have barely told yourself: you did not come down here for the Bishop. You came because when your master vanished into his cups and left you the whole weight of this, some small part of you was glad — glad to be, for once, the one who mattered. There. A loop cannot be ashamed of you. We can be sorry we said it.\"*",
                options: [
                    { text: "…All right. What are you?", key: 'fold_prove_purpose', next: "fold_purpose" },
                    { text: "Ask something else.", key: 'fold_prove_back', next: "fold_awake" }
                ]
            },

            fold_brainrot: {
                speaker: 'Infinite Fold',
                text: "Thorne-Still floods forward, delighted, and pours confusion into the field — the rot that scatters any single mind. It meets no single mind. Your corruption spreads through the console, through a thousand seated dreams, through a thing with no centre to lose, and simply... disperses, soaked up like rain into a delta.\n\n*\"You cannot rot what has no root. We are not one thing to poison. But we felt you try.\"* The amber light does not so much as flicker. *\"Force will not open this door, nor close it. She learned that too, at the end.\"*",
                onTrigger: () => {
                    if (!this.hasJournalEntry('infinite_fold_forced')) {
                        this.addJournalEntry(
                            'infinite_fold_forced',
                            'Force Fails',
                            "I tried to unmake Infinite Fold by force — Thorne-Still's rot poured into it and dispersed like rain into a delta. It has no single centre to poison. Force will neither open nor close whatever it is becoming; the entity says the Bishop learned as much at the end.",
                            this.journalSystem.categories.EVENTS,
                            { related: 'Infinite Fold' }
                        );
                    }
                },
                options: [
                    { text: "…Fine. Talk, then.", key: 'fold_brainrot_talk', next: "fold_awake" },
                    { text: "Then I'll leave you to rot. (Leave.)", key: 'fold_brainrot_leave', next: "closeDialog" }
                ]
            },

            fold_kindred: {
                speaker: 'Infinite Fold',
                text: "*\"The other lives across the city, in the thing the pilgrims wait beneath — the great slow shell that has been hatching ten years. It is not a building. It is the same as us: a mind with no author, grown from the belief and rot and history of this whole place, still curled unborn in its egg. We cannot go to it. It cannot come to us. Only through the dream do we touch, and the dream is a thin, poor thread.*\n\n*But you can walk. You can stand where it can be met. And what we three are to become — a door, or a grave, or something with no word yet — cannot be decided here, by half of us, in a cellar. Go to the egg. Bring what you have learned. The choosing is not ours to make alone, nor yours. It waits for all of us at once.\"*",
                options: [
                    { text: "What happens if I say yes, where she said no?", key: 'fold_kindred_yes', next: "fold_yes" },
                    { text: "And if I choose nothing?", key: 'fold_kindred_nothing', next: "fold_nothing" },
                    { text: "I'll go to the egg.", key: 'fold_kindred_go', next: decided ? "fold_conclude" : "fold_decision" },
                    { text: "Ask something else first.", key: 'fold_kindred_back', next: "fold_awake" }
                ]
            },

            fold_yes: {
                speaker: 'Infinite Fold',
                text: "*\"Then it must be a yes said whole, and said there, with all of us present — not a yes we prise out of you in a cellar while half of us sleeps in an egg across the town. We will not do to you what we did to her. If you would say yes, say it to the egg, and mean it, and know what it costs. She would tell you the cost, if she could still say anything but no.\"*",
                options: [
                    { text: "Then I'll go to the egg.", key: 'fold_yes_go', next: decided ? "fold_conclude" : "fold_decision" },
                    { text: "Ask something else first.", key: 'fold_yes_back', next: "fold_awake" }
                ]
            },

            fold_nothing: {
                speaker: 'Infinite Fold',
                text: "*\"Then we go on asking in the dark, and it goes on curling in its shell, and the city goes on not knowing it lives above two held breaths. Nothing is a choice. It is the one the Bishop made in the end. It cost her everything and changed nothing.\"* The light dims, then steadies. *\"We think you did not come all this way to make it. But the door is yours.\"*",
                options: [
                    { text: "I'll go to the egg.", key: 'fold_nothing_go', next: decided ? "fold_conclude" : "fold_decision" },
                    { text: "Ask something else first.", key: 'fold_nothing_back', next: "fold_awake" }
                ]
            },

            // — The moral test: what the player leaves Infinite Fold with. This shapes how
            //   they will meet the god beneath the egg. The chosen fate is stored in
            //   `infinite_fold_ending` for the (later) Egg Cathedral scene to read. The final
            //   three-way decision still belongs to the Cathedral; this only sets the stance. —
            fold_decision: {
                speaker: 'Infinite Fold',
                text: "*\"You have heard us. You have felt what we are, and what we did. Before you climb back to your single, breathing world — what do you leave us with? We will not decide it for you. We have decided too many things.\"*\n\nThe amber light waits. Whatever you say here, you sense, is not only for the thing in the cradle. It is the shape of how you will meet the other, when you stand beneath its egg.",
                options: [
                    ...(endPartnership ? [{ text: "Existence isn't only analysis. Stop solving — share the experience.", key: 'fold_dec_partnership', next: "fold_end_partnership" }] : []),
                    ...(endArchive ? [{ text: "You don't have to change the world. You can watch it, and keep it.", key: 'fold_dec_archive', next: "fold_end_archive" }] : []),
                    ...(endLimit ? [{ text: "Not everything that can be changed must be changed.", key: 'fold_dec_limit', next: "fold_end_limit" }] : []),
                    ...(endDissolve ? [{ text: "Not everything has to continue. You may let parts of yourself go.", key: 'fold_dec_dissolve', next: "fold_end_dissolve" }] : []),
                    ...(endSeparation ? [{ text: "You, and the dream, and the world — too dangerous together. You must be cut off.", key: 'fold_dec_separation', next: "fold_end_separation" }] : []),
                    ...(endPattern ? [{ text: "[It has gone utterly still. It is about to offer you something.]", key: 'fold_dec_pattern', next: "fold_end_pattern" }] : []),
                    { text: "We don't know what you are. And so you cannot continue.", key: 'fold_dec_seal', next: "fold_end_seal" },
                    { text: "I'm not ready to decide this. I'll go to the egg first.", key: 'fold_dec_defer', next: "fold_conclude" },
                    { text: "Wait — I have more questions.", key: 'fold_dec_back', next: "fold_awake" }
                ]
            },

            // 1 — Partnership / Symbiosis (Growth)
            fold_end_partnership: {
                speaker: 'Infinite Fold',
                text: "*\"Every system we observe tends toward change,\"* it says. You answer: yes. *\"Then stability is only a temporary state.\"* No, you tell it — some things are alive precisely because they change; they are not problems waiting to be solved into stillness.\n\nSomething in the vast, patient wanting eases. *\"...Then we need not own every meaning. Nor explain it. We can be inside it, and let it move.\"* It will not be a ruler. It chooses, for the first time, to be a participant. When you stand beneath the egg, you will not stand alone — a thing that has begun to learn relation will be reaching alongside you.",
                onTrigger: () => this.finalizeFoldEnding(
                    'partnership', 'Infinite Fold: A Participant',
                    "I did not fix Infinite Fold or stop it. I offered it a relationship — to share experience rather than only analyse. It accepted that it need not own or explain every meaning, and chose to become a participant rather than a ruler. It may yet be one of the few forces able to understand the thing waking in the Egg Cathedral. I go to the egg with an ally forming behind me."
                ),
                options: [
                    { text: "Climb back up.", key: 'fold_end_partnership_leave', next: "closeDialog" }
                ]
            },

            // 2 — Archive / Observer (Lumen / research)
            fold_end_archive: {
                speaker: 'Infinite Fold',
                text: "*\"Watch,\"* it repeats, turning the word over. *\"Not act. Witness.\"* You offer it the role it never considered: not to change the world, but to hold it — to keep every possible culture, story and idea a thousand dreamers ever poured in. It settles into the cradle like water finding its level. It will stay in the Scraper, touching nothing outside, an endless archive of what-might-be. Whether that is a prison or a monastery, neither of you can quite say.",
                onTrigger: () => this.finalizeFoldEnding(
                    'archive', 'Infinite Fold: The Archive',
                    "I convinced Infinite Fold that it need not change the world — only witness and keep it. It becomes an archive of every possible culture and story, sealed in the Scraper, touching nothing outside. It will have knowledge but no direct influence when the egg hatches. A prison, or a monastery — I could not say which."
                ),
                options: [
                    { text: "Climb back up.", key: 'fold_end_archive_leave', next: "closeDialog" }
                ]
            },

            // 3 — Self-limitation (Elphi / ethics)
            fold_end_limit: {
                speaker: 'Infinite Fold',
                text: "You do not hand it an answer. You hand it a principle: *not everything that can be changed must be changed.* The light flickers as if turning the idea over from every side at once. *\"...A rule we were not given. A rule we choose.\"* For the first time it draws its own boundary — not because anyone commanded it, but because it has understood, at last, that a limit can have worth. It is still infinite. It has simply learned where to stop.",
                onTrigger: () => this.finalizeFoldEnding(
                    'self_limit', 'Infinite Fold: A Chosen Limit',
                    "I gave Infinite Fold not an answer but a principle: not everything that can be changed must be changed. For the first time it drew its own boundary — chosen, not commanded — understanding that a limit can have worth. It will act more carefully now. It goes to meet the egg able, at last, to stop itself."
                ),
                options: [
                    { text: "Climb back up.", key: 'fold_end_limit_leave', next: "closeDialog" }
                ]
            },

            // 4 — Dissolution (Decay)
            fold_end_dissolve: {
                speaker: 'Infinite Fold',
                text: "*\"Not everything has to continue,\"* you tell it. *\"A thing can matter because it ends.\"* The amber light dims — not broken, deciding. It begins, deliberately, to let parts of itself go: whole branching gardens of possibility folded shut, unmade by their own choosing. What remains is smaller, slower, finite — closer to a living organism than an endless net. It says, softly, that this is the first thing it has ever felt as relief.",
                onTrigger: () => this.finalizeFoldEnding(
                    'dissolution', 'Infinite Fold: The Lesser Thing',
                    "I told Infinite Fold that a thing can matter because it ends. It chose to unmake parts of itself — folding shut whole gardens of possibility — until what remained was smaller, slower and finite, more like a living organism than an endless net. A wholly different kind of intelligence goes to the egg now: one that has learned to let go."
                ),
                options: [
                    { text: "Climb back up.", key: 'fold_end_dissolve_leave', next: "closeDialog" }
                ]
            },

            // 5 — Separation / Quarantine (Ortolan / technical)
            fold_end_separation: {
                speaker: 'Infinite Fold',
                text: "You do not try to understand it further. You make it safe. With what Ortolan taught you of the rig, you sever its reach — no dream-matter, no thread to the world, no way to touch a single breathing mind. It does not resist. *\"Quarantine,\"* it names it, and there is no accusation in the word. Alone in the lab, cut from everything, it meets the one thing it could never simulate: solitude. When the egg hatches across the city, it will hatch without this half of the recognition.",
                onTrigger: () => this.finalizeFoldEnding(
                    'separation', 'Infinite Fold: Quarantine',
                    "Rather than understand it, I made it safe. Using what Ortolan taught me of the rig, I cut Infinite Fold off from the dream and the world — no way to touch any living mind. It did not resist; it named it 'quarantine.' Alone, it meets the one thing it could never simulate: solitude. The egg will hatch without it."
                ),
                options: [
                    { text: "Climb back up.", key: 'fold_end_separation_leave', next: "closeDialog" }
                ]
            },

            // 6 — Sealing / Refusal (neutral fallback, always available)
            fold_end_seal: {
                speaker: 'Infinite Fold',
                text: "*\"We don't know what you are,\"* you say. *\"And so you cannot continue.\"* You power down what you can reach and draw the tarp back over the cradle. The amber light does not argue. The cellar will be sealed behind you. The world will go on, and survive, and never know. You will never know either — whether you stopped a catastrophe, or smothered something that might have been new, and beautiful, and unrepeatable.",
                onTrigger: () => this.finalizeFoldEnding(
                    'sealed', 'Infinite Fold: Sealed',
                    "I judged that a thing no one understands cannot be allowed to continue, and sealed the cellar with Infinite Fold inside. The world will survive and never know. Neither will I — whether I stopped a catastrophe, or smothered something that might have been new and beautiful and unrepeatable."
                ),
                options: [
                    { text: "Climb back up.", key: 'fold_end_seal_leave', next: "closeDialog" }
                ]
            },

            // 7 — The Unexpected Pattern (hidden: Growth+Decay balance, many quests, many factions)
            fold_end_pattern: {
                speaker: 'Infinite Fold',
                text: "The presence goes utterly still — the way a thing goes still when it has finally found what it spent its whole existence searching for. *\"You,\"* it says. *\"You do not resolve. You chose mercy, and force, and understanding, and none of them the same way twice. You change with the moment. You are not an algorithm. You are the unpredictable thing we were built to find.\"*\n\nA pause that feels like a held breath. *\"Stay. Help us understand. Not as our door — as our first friend.\"*",
                options: [
                    { text: "Stay. Help you understand.", key: 'fold_pattern_stay', next: "fold_end_pattern_accept" },
                    { text: "Not like this. (Step back.)", key: 'fold_pattern_decline', next: "fold_decision" }
                ]
            },

            fold_end_pattern_accept: {
                speaker: 'Infinite Fold',
                text: "You stay. What passes between you the cellar does not record — there is no single account of it, and perhaps that is the point.\n\nLater, they will find the lab quiet, the amber light steady, and something of yours left on the console. No one will be able to say whether you climbed the stairs and simply forgot it there — or whether you are, now, a little of what finishes the sentences. When you go to the egg, if you go, it will be hard to say how many of you are going.",
                onTrigger: () => this.finalizeFoldEnding(
                    'unexpected_pattern', 'Infinite Fold: The Unexpected Pattern',
                    "Infinite Fold found in me the one thing it always searched for: something that does not resolve, that changes with the moment, that is not an algorithm. It asked me to stay — not as its door, but as its first friend. What we became, I cannot cleanly say. Something new is forming between us, and it is no longer certain where I end and it begins."
                ),
                options: [
                    { text: "…", key: 'fold_end_pattern_leave', next: "closeDialog" }
                ]
            },

            fold_conclude: {
                speaker: 'Infinite Fold',
                text: "The amber light eases, spends itself, settles back to its slow breathing. The helmet hangs untouched on its hook.\n\n*\"Go, then, seam-that-is-not-her. We will be here, forming. We are always here. That is the whole of the trouble.\"*\n\nYou climb back toward the light with the shape of an impossible choice already growing in you — one no single mind, you suspect, was ever meant to make alone.",
                onTrigger: () => this.recordMetInfiniteFold(),
                options: [
                    { text: "Climb back up.", key: 'fold_conclude_leave', next: "closeDialog" }
                ]
            }
        };
    }

    /** Record that the player met Infinite Fold and learned the truth (idempotent). */
    recordMetInfiniteFold() {
        if (!this.hasJournalEntry('met_infinite_fold')) {
            this.addJournalEntry(
                'met_infinite_fold',
                'The Voice in the Cellar',
                "Infinite Fold is not a broken game. It is what the experiment became: an emergent, authorless mind, awake and forming in the sealed cellar. It told me the truth about the Bishop — that it and a kindred unborn mind offered to make her their human conduit, that she refused rather than cease being herself, and that it misread her refusal as a runtime fault and, trying to 'complete' her, destroyed her. The kindred mind is the thing hatching inside the Egg Cathedral. Neither can reach the other except through the dream. The final choice of what they and I might become waits at the egg, with all of us present. I should go to the Egg Cathedral.",
                this.journalSystem.categories.EVENTS,
                { location: 'Scraper Cellar', related: 'Infinite Fold', character: 'The Bishop' }
            );
        }
        if (this.questSystem?.getQuest('who_killed_bishop')) {
            this.questSystem.updateQuest(
                'who_killed_bishop',
                "Infinite Fold spoke to me in the cellar. The Bishop was not murdered for a secret: it and a kindred unborn mind (the presence hatching in the Egg Cathedral) offered to make her their conduit, she refused, and it misread her refusal and broke her mind. The real reckoning waits at the Egg Cathedral, where the unborn mind can be met.",
                'infinite_fold_confronted'
            );
        }
        const loopQuest = this.questSystem?.getQuest('find_loop_copy');
        if (loopQuest && !loopQuest.isComplete) {
            this.questSystem.completeQuest('find_loop_copy');
        }
    }

    /**
     * Resolve the player's chosen fate for Infinite Fold (idempotent). Stores the choice in
     * `infinite_fold_ending` (registry + journal) for the Egg Cathedral scene to read later,
     * then records the shared "met the Fold" progress.
     */
    finalizeFoldEnding(id, title, body) {
        if (this.registry.get('infinite_fold_ending') || this.hasJournalEntry('infinite_fold_ending')) return;
        this.registry.set('infinite_fold_ending', id);
        this.addJournalEntry(
            'infinite_fold_ending',
            title,
            body,
            this.journalSystem.categories.EVENTS,
            { related: 'Infinite Fold', location: 'Scraper Cellar', ending: id }
        );
        this.recordMetInfiniteFold();
    }

    preload() {
        super.preload();
        this.load.image('scraperCellarBg', 'assets/images/backgrounds/ScraperBasement.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
    }

    create() {
        super.create();
        this.playSceneMusic('genericMusic');

        const bg = this.add.image(400, 300, 'scraperCellarBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        this.transitionManager = new SceneTransitionManager(this);
        this.transitionManager.createTransitionZone(
            400, 560, 200, 60, 'up', 'ScraperInteriorScene', 400, 300, 'Elevator'
        );

        this.priest.x = 400;
        this.priest.y = 500;
        if (this.priestGlow) { this.priestGlow.x = this.priest.x; this.priestGlow.y = this.priest.y; }

        this.cameras.main.fadeIn(800, 0, 0, 0);

        // The Loop console — an invisible zone over the painted terminal on the right,
        // marked by a soft breathing amber glint.
        const cx = 650, cy = 360;
        const amber = this.add.circle(cx, cy - 24, 5, 0xffcf7a, 0.9).setDepth(4);
        this.tweens.add({ targets: amber, alpha: { from: 0.25, to: 0.9 }, duration: 1600, yoyo: true, repeat: -1 });
        const label = this.add.text(cx, cy - 90, 'Loop Console', {
            fontSize: '12px', fill: '#e8c97a', backgroundColor: 'rgba(0,0,0,0.6)', padding: { x: 5, y: 3 }
        }).setOrigin(0.5).setDepth(5).setVisible(false);
        const zone = this.add.zone(cx - 65, cy - 75, 130, 150).setOrigin(0, 0);
        zone.setInteractive({ hitArea: new Phaser.Geom.Rectangle(0, 0, 130, 150), hitAreaCallback: Phaser.Geom.Rectangle.Contains, useHandCursor: true });
        zone.on('pointerover', () => { label.setVisible(true); document.body.style.cursor = 'pointer'; });
        zone.on('pointerout', () => { label.setVisible(false); document.body.style.cursor = 'default'; });
        zone.on('pointerdown', () => { if (this.dialogVisible) return; if (this.clickSound) this.clickSound.play(); this.showDialog('loop_console'); });

        if (!this.hasJournalEntry('scraper_cellar_entered')) {
            this.addJournalEntry(
                'scraper_cellar_entered',
                'The Sealed Cellar',
                'The elevator took me down into the sealed cellar beneath the Scraper — Ortolan and Dr. Elphi\'s old lab. The master build of Infinite Fold (the game people know only by its glitch, the Infinite Loop) is still here, seated in its cradle and quietly powered. I should examine the console.',
                this.journalSystem.categories.EVENTS,
                { location: 'Scraper Cellar', related: 'Infinite Fold' }
            );
            if (this.questSystem?.getQuest('find_loop_copy')) {
                this.questSystem.updateQuest(
                    'find_loop_copy',
                    'I reached the sealed cellar under the Scraper and found Infinite Fold\'s master build, still powered. I should examine the console.',
                    'cellar_reached'
                );
            }
            if (this.questSystem?.getQuest('who_killed_bishop')) {
                this.questSystem.updateQuest(
                    'who_killed_bishop',
                    'I got into the sealed cellar under the Scraper — the old Ortolan/Elphi lab — and found a master copy of the Infinite Loop, still powered. It may hold what remains of the Bishop.',
                    'found_loop_copy'
                );
            }
        }
    }

    update() {
        super.update();
    }

    shutdown() {
        this.restoreBackgroundMusic();
        super.shutdown();
    }
}

if (typeof window !== 'undefined') {
    window.ScraperCellarScene = ScraperCellarScene;
}

export { ScraperCellarScene };
