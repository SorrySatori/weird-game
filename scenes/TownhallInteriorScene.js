import GameScene from './GameScene.js';
import { returnToMainMenu } from '../utils/mainMenu.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import { GANG_QUEST_IDS, gangQuestStatus } from '../utils/GangOfLamps.js';

// Where the hall's people stand on the redrawn floor: the soles (x, y) in canvas coords.
const TH_SPOTS = {
    clerk: { x: 190, y: 528 },        // by the record cabinets on the left
    eater: { x: 762, y: 528 },        // right of the dais, by the toppled chair
    councilor: { x: 882, y: 528 },    // by the public bench under the lancets
    poet: { x: 533, y: 482 },         // on the public reading dais, by the lectern (depth ~17.6)
};

// The hall's people, redrawn (tools/artgen/townhall_cast.py, Aseprite Townhall_<file>): 8-frame idle sheets shown at
// scale 1, origin bottom-centre. sole = the soles' row in the frame; hit = the figure's box in frame coordinates;
// top = the bust portrait's first row; names = the dialog speakers (English + Czech) that get the bust.
// The poet's sheet is drawn ~15% smaller: he stands on the dais, further away than the walk line.
const TH_CAST = {
    clerk: {
        key: 'thClerkIdle', file: 'clerk', w: 128, h: 160, sole: 156, anim: 'th_clerk_idle', fps: 6,
        // 0/1 rest (two flame shapes, so the candle keeps flickering), 2 breath, 3 blink, 4/5 a look at the papers,
        // 6 a note scratched with the quill, 7 the flame gutters
        frames: [0, 1, 0, 1, 2, 2, 1, 0, 1, 0, 3, 1, 0, 1, 0, 7, 7, 1, 0, 1, 0, 4, 5, 4, 5, 6, 5, 6, 4, 5, 4, 0, 1, 0, 2, 1, 0, 1],
        hit: [34, 10, 64, 148], shadowW: 44, top: 8,
        names: ['Townhall Clerk', 'Freed Clerk', 'Radniční úředník', 'Osvobozený úředník'],
    },
    eater: {
        key: 'thEaterIdle', file: 'eater', w: 128, h: 144, sole: 141, anim: 'th_eater_idle', fps: 4,
        // played in order: it chews its complaint twice and swallows, the goggles whirr, the chimney puffs (the smoke rises throughout)
        frames: [0, 1, 2, 3, 4, 5, 6, 7],
        hit: [6, 22, 116, 120], shadowW: 104, top: 28,
        names: ['Complaint Eater', 'Požírač stížností'],
    },
    councilor: {
        key: 'thSeraphelIdle', file: 'seraphel', w: 128, h: 192, sole: 189, anim: 'th_seraphel_idle', fps: 5,
        // breath, the whiskers drift, the fingertips tap, the skull tilts, the seals sway, a glint in the sockets
        frames: [0, 0, 0, 1, 1, 7, 0, 0, 2, 2, 0, 0, 0, 3, 3, 0, 0, 4, 4, 4, 0, 0, 5, 5, 0, 0, 6, 0, 0],
        hit: [34, 0, 64, 190], shadowW: 58, top: 0,
        names: ['Councilor Seraphel Dune', 'Radní Seraphel Dune'],
    },
    poet: {
        key: 'thPoetIdle', file: 'poet', w: 128, h: 144, sole: 141, anim: 'th_poet_idle', fps: 5,
        // restless: breath, a twitchy blink, the gun hand trembles, he declaims, turns a page
        frames: [0, 1, 0, 2, 0, 3, 0, 1, 4, 5, 4, 5, 0, 6, 6, 0, 7, 0, 3],
        hit: [28, 16, 64, 126], shadowW: 40, top: 14,
        names: ['The Mad Poet', 'Šílený básník'],
    },
};

export default class TownhallInteriorScene extends GameScene {
    constructor() {
        super({ key: 'TownhallInteriorScene' });
        this.isTransitioning = false;
        this.poet = null;
        this.hostages = [];
        this.clerk = null;
        this.complaintEater = null;
        this.councilor = null;
    }

    get dialogContent() {
        const poetResolved = !!this.hasJournalEntry('townhall_poet_resolved');
        const hasQuestUpdate = (questId, updateKey) => !!this.questSystem?.getQuest(questId)?.updates?.some(update => update.key === updateKey);
        const isQuestComplete = (questId) => !!this.questSystem?.getQuest(questId)?.isComplete;
        const hasExcavationPermitQuest = !!this.questSystem?.getQuest('excavation_permit');
        const hasGodgraveyardAccess = !!(this.hasJournalEntry('godgraveyard_access_granted') || this.hasItem('godgraveyard-access-permit'));
        const hasWorldLore = !!(this.hasJournalEntry('upper_morkezela') || this.hasJournalEntry('obazoba_cult'));
        const hasBishopMemo = !!(this.hasJournalEntry('bishop_memo') || this.hasJournalEntry('elphi_townhall_log'));
        const hasDreamDeathMemory = !!(this.hasJournalEntry('bishop_cartridge') || this.hasJournalEntry('bishop_helmet') || hasQuestUpdate('who_killed_bishop', 'elphi_dream_kill') || hasQuestUpdate('who_killed_bishop', 'elphi_cartridge'));
        const hasCathedralMemory = !!(this.questSystem?.getQuest('find_bishop') || this.hasJournalEntry('ac_cathedral_tension') || hasQuestUpdate('who_killed_bishop', 'ac_bishop_relationship'));
        const hasAuctionMemory = !!this.hasJournalEntry('seldo_auction_success');
        const hasRustMemory = !!(this.hasJournalEntry('rust_choir_info') || this.hasJournalEntry('rust_feast_completed_full') || this.hasJournalEntry('rust_feast_completed_illusion'));
        const hasRedmassMemory = !!(this.hasJournalEntry('redmass_encountered') || this.hasJournalEntry('redmass_spared') || this.hasJournalEntry('redmass_collected_force') || this.hasJournalEntry('redmass_collected_voluntary'));
        const hasShedMemory = !!(this.questSystem?.getQuest('ortolan_arms') || this.hasJournalEntry('extra_symbiont_slot_purchased'));
        const hasEdgarMemory = !!(this.hasJournalEntry('edgar_eskola_meeting') || this.hasJournalEntry('edgar_book_completed') || isQuestComplete('edgar_book'));
        const hasMagnekinMemory = !!(this.hasJournalEntry('magnekin_reveal') || this.hasJournalEntry('magnekin_hopsalot_church'));
        const hasNoiseGodMemory = !!(this.hasJournalEntry('noise_god_insight') || this.hasJournalEntry('feral_toast_performance'));
        const hasSkyshipMemory = !!(this.hasJournalEntry('floor_counter_tool') || this.questSystem?.getQuest('find_lumen_directorate'));
        const hasSulkberryClearMemory = !!(hasQuestUpdate('who_killed_bishop', 'verrik_sulkberry_clear') || hasQuestUpdate('who_killed_bishop', 'kloor_sulkberry_clear') || hasQuestUpdate('who_killed_bishop', 'heliodor_sulkberry_clear'));
        const hasGodgraveyardMemory = !!(this.questSystem?.getQuest('excavation_permit') || hasQuestUpdate('rust_feast', 'learned_rust_cluster_location'));
        const hasThorne = !!this.symbiontSystem?.hasSymbiont('thorne-still');
        const hasNeme = !!this.symbiontSystem?.hasSymbiont('neme-crownmire');
        const hasUlvarex = !!this.symbiontSystem?.hasSymbiont('ulvarex-borrowed-horizon');
        const hasBrine = !!this.symbiontSystem?.hasSymbiont('brine-scripture');
        const poetStartTextKey = poetResolved ? 'poet_start_resolved' : 'poet_start_hostage';
        const townhallRecordsChecked = !!this.hasJournalEntry('townhall_bishop_records_checked');
        const clerkAfterPoetTextKey = townhallRecordsChecked ? 'clerk_after_poet_records_checked' : 'clerk_after_poet_fresh';
        const councilorStartTextKey = hasGodgraveyardAccess ? 'councilor_start_access_granted' : 'councilor_start_needs_reward';
        const complaintEaterBishopTextKey = townhallRecordsChecked ? 'complaint_eater_bishop_records_checked' : 'complaint_eater_bishop_records_locked';

        // --- Ink Tribunal membership (Seraphel Dune) ---
        const pithKnown = !!this.hasJournalEntry('pith_reclaimers_faction');
        const pithJoined = !!this.hasJournalEntry('pith_reclaimers_joined');
        const pithQuestObj = this.questSystem?.getQuest('join_pith_reclaimers');
        const hasPithQuest = !!(pithQuestObj && !pithQuestObj.isComplete);
        const hasPithRecruit = !!(this.hasJournalEntry('pith_recruit_magnekin') || this.hasJournalEntry('pith_recruit_heir'));
        // Gang of Lamps: surrender Torchère's contraband to the Tribunal instead of running it.
        const canGiveDrugsPith = pithKnown && gangQuestStatus(this, GANG_QUEST_IDS.torchere) === 'active' && !!(this.hasItem && this.hasItem('wimlick'));

        // Gang of Lamps (Sconce's quest): route choices at the records drawers.
        const hasPalinode = !!this.symbiontSystem?.hasSymbiont('palinode');
        const hasBrineDossier = !!this.symbiontSystem?.hasSymbiont('brine-scripture');

        return {
            ...super.dialogContent,

            // Gang of Lamps (Sconce's quest): search the records drawers, with method choices.
            dossier_search: {
                speaker: 'Priest',
                text: `The records drawers run the length of the wall, thousands of case-numbers in a dead bureaucrat's order. Somewhere in here is the one dossier filed to be forgotten — a number that matches nothing. Finding it by hand could take all night.`,
                options: [
                    { text: "Search the drawers by hand until the wrong number turns up.", key: 'dossier_plain', next: "closeDialog", onSelect: () => this.deliverDossier('plain') },
                    ...(hasPalinode ? [{ text: "[Palinode] Unsay the seal on the drawer that refuses to belong.", key: 'dossier_palinode', next: "closeDialog", onSelect: () => this.deliverDossier('palinode') }] : []),
                    ...(hasBrineDossier ? [{ text: "[Brine · Salt Recall] Find it by the civic scar it left in the paper.", key: 'dossier_brine', next: "closeDialog", onSelect: () => this.deliverDossier('brine') }] : []),
                    { text: "Leave the drawers for now.", key: 'dossier_cancel', next: "closeDialog" },
                ]
            },

            poet_intro: {
                speaker: 'The Mad Poet',
                hideCloseOption: true,
                text: `The Townhall doors seal behind you with the soft, final sound of a drawer sliding shut. The air tastes of old ink and held breath.

On the public reading dais stands a thin, ink-blackened figure — a revolver in one fist, a sheaf of bleeding-edged poems in the other. The clerk, the councilor, and the Complaint Eater sit rigid beneath the seal of the Townhall. He does not stop reading as you enter.

"I read to empty halls for thirty years.
Tonight the hall is full, and cannot leave.
Behold the only honest audience —
captive, breathing, made at last to receive.

They stamped my life 'insufficiently civic,'
so I have penned the civic masterpiece:
a poem no clerk can file and no soul leaves politely.
The city is a draft. I am its final edit."`,
                options: [
                    { text: "(Someone in the room is about to break.)", key: 'someone_about_to_break', next: "poet_intro_interrupt" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('met_mad_poet')) {
                        this.addJournalEntry(
                            'met_mad_poet',
                            'The Mad Poet',
                            "A thin, ink-blackened figure who read to empty halls for thirty years — until he sealed the Townhall doors, drew a revolver, and made a captive audience of the clerks beneath the city seal. The city stamped his life 'insufficiently civic.' Now he means to deliver his masterpiece to a room that cannot leave.",
                            this.journalSystem.categories.PEOPLE,
                            { character: 'The Mad Poet', location: 'Townhall' }
                        );
                    }
                }
            },

            poet_intro_interrupt: {
                speaker: 'Townhall Clerk',
                hideCloseOption: true,
                text: `The clerk on the floor cracks first. The words spill out before fear can swallow them:

"Please — it's been a tenth of a digestion. My daughter is waiting at the registry window downstairs. She's six. She doesn't know how to—"

The revolver swings toward her, and yet the poet's voice never loses its meter. That is the terrifying part. He does not even raise it.`,
                options: [
                    { text: "(The poet answers her.)", key: 'the_poet_answers_her', next: "poet_intro_silence" },
                ]
            },

            poet_intro_silence: {
                speaker: 'The Mad Poet',
                hideCloseOption: true,
                text: `"Do not interrupt the reading.
Interruption is the only sin.
The poem does not pause for daughters;
the poem does not pause for anything living.

She will wait. You will all wait.
A held ear is the only ear that hears.
The doors are stamped shut — and so is the discussion."

He turns the barrel, slowly, until it finds you.

"But you. You came in late, off the street, unstamped. Tell me — can you answer me in kind? Or are you just one more reader who would rather leave?"`,
                options: [
                    { text: "Challenge him to a poetry battle.", key: 'challenge_him_to_a_poetry_battle', next: "poet_challenge" },
                    { text: "First — what do you actually want?", key: 'first_what_do_you_want', next: "poet_demands" },
                    ...(hasBrine ? [{ text: "[Brine Scripture] Read the salt memory of the room.", key: 'brine_scripture_read_the_salt_memory', next: "poet_brine_read" }] : []),
                ]
            },

            poet_start: {
                speaker: poetResolved ? 'Freed Clerk' : 'The Mad Poet',
                textKey: poetStartTextKey,
                hideCloseOption: !poetResolved,
                text: poetResolved
                    ? `"The poet is gone. The hostages are safe. The Townhall is still shaking, but at least now it is shaking bureaucratically."`
                    : `The poet keeps the revolver loosely trained on the room, waiting. The reading is not finished. It will not be finished until someone gives him what he wants — or proves him right about the world.

"No one leaves until the city hears me correctly," he says. "Not politely. Not bureaucratically. Correctly."`,
                options: [
                    ...(poetResolved ? [{ text: "What happens now?", key: 'what_happens_now', next: "clerk_after_poet" }] : []),
                    ...(!poetResolved ? [{ text: "Challenge him to a poetry battle.", key: 'challenge_him_to_a_poetry_battle', next: "poet_challenge" }] : []),
                    ...(!poetResolved ? [{ text: "Ask what he wants.", key: 'ask_what_he_wants', next: "poet_demands" }] : []),
                    ...(!poetResolved && hasBrine ? [{ text: "[Brine Scripture] Read the salt memory of the room.", key: 'brine_scripture_read_the_salt_memory', next: "poet_brine_read" }] : []),
                ]
            },

            poet_demands: {
                speaker: 'The Mad Poet',
                hideCloseOption: true,
                text: `"Wants? Wants are prose. I require witness.

For thirty years this city read me the way it reads a parking notice — if at all. The Townhall stamped my chapbook 'insufficiently civic.' They called my line breaks a zoning violation. They filed my grief under 'miscellaneous.'

So now the public receives a reading. Every stanza. Every footnote. Every hostage-held breath. They struck my name from the register, so I took a truer one: the Last Editor."`,
                options: [
                    { text: "Then I'll answer in verse.", key: 'then_ill_answer_in_verse', next: "poet_challenge" },
                    { text: "Why hostages? Why not simply publish?", key: 'why_hostages_not_publish', next: "poet_why" },
                ]
            },

            poet_why: {
                speaker: 'The Mad Poet',
                hideCloseOption: true,
                text: `"Publish?" He laughs, without any joy in it.

"A published poem is a poem you can put down. A poem you can put down is a poem that changed nothing.

A reader who is free will always leave
the moment that the verse asks something true.
So I removed the door. I removed the leaving.
What stays must finally listen it through.

A captive ear is the only honest ear. You will not leave — so you will finally hear me."`,
                options: [
                    { text: "Then I'll answer him in verse.", key: 'then_ill_answer_him_in_verse', next: "poet_challenge" },
                    { text: "And after the reading? What then?", key: 'and_after_the_reading', next: "poet_tabula_rasa" },
                ]
            },

            poet_tabula_rasa: {
                speaker: 'The Mad Poet',
                hideCloseOption: true,
                text: `For a moment his eyes go somewhere vast and empty, somewhere past the walls.

"After? After comes the clean ground.

Every great poem begins on a blank page —
and this city is no blank: a palimpsest of cowards,
old ink scrawled over old ink, nothing erased,
only stamped, and filed, and stamped again.

To write the new, I must first unwrite the old. Tabula rasa. Bare earth. A page wide enough, at last, for the only line that matters. This little reading? It is merely the title."`,
                options: [
                    { text: "That isn't poetry. That's a bomb with footnotes.", key: 'bomb_with_footnotes', next: "poet_challenge" },
                    { text: "Then I'll answer him in verse.", key: 'then_ill_answer_him_in_verse_2', next: "poet_challenge" },
                ]
            },

            poet_brine_read: {
                speaker: 'Brine Scripture',
                hideCloseOption: true,
                text: `Salt wakes under your tongue. The floor remembers shoes grinding in panic, spilled ink drying into little black reefs, and one line repeated until it wore a groove into the boards: "The city has no ear for me."

The Brine Scripture offers memory, not victory. It gives you material. You still have to make it sing.`,
                options: [
                    { text: "Use that memory in the contest.", key: 'use_that_memory_in_the_contest', next: "poet_challenge" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('townhall_brine_poet_read')) {
                        this.addJournalEntry(
                            'townhall_brine_poet_read',
                            'Salt Memory of the Townhall Reading',
                            'The Brine Scripture read residue from the Townhall floor: panic, ink, and the poet repeating that the city had no ear for him. It might help in the poetry battle, but it cannot win by itself.',
                            this.journalSystem.categories.EVENTS,
                            { location: 'Townhall' }
                        );
                    }
                }
            },

            poet_challenge: {
                speaker: 'The Mad Poet',
                text: `"A challenger?" Something flickers across his face — closer to hope than to fury. "Good. At last the room develops a pulse.

Three rounds, then. Image. Wound. Verdict. Bring me the city as you have actually lived it — not the version they keep on file.

If your poem is alive, I let them walk into the morning.
If your poem is dead, we all find out together what bad art costs."`,
                hideCloseOption: true,
                options: [
                    { text: "Begin the poetry battle.", key: 'begin_the_poetry_battle', next: "poet_round_one" },
                ],
                onTrigger: () => {
                    this.resetPoetryBattle();
                }
            },

            poet_round_one: {
                speaker: 'The Mad Poet',
                text: `Round One — IMAGE.

The poet snaps open a page. "Upper Morkezela is a mouth full of doors. Give me one image that proves you have been bitten."`,
                hideCloseOption: true,
                options: [
                    ...(hasWorldLore ? [{ text: "A second shadow watching the first, both pretending not to be afraid.", key: 'second_shadow_watching_first', next: "poet_round_one_result" }] : []),
                    ...(hasBishopMemo ? [{ text: "A confessional where the Bishop met herself, breathless and already speaking.", key: 'bishop_met_herself_breathless', next: "poet_round_one_result" }] : []),
                    ...(hasCathedralMemory ? [{ text: "An egg-shaped cathedral hatching scripture while every faith waits to be chosen.", key: 'egg_cathedral_hatching_scripture', next: "poet_round_one_result" }] : []),
                    ...(hasSkyshipMemory ? [{ text: "A skyship caught above the Crossroads like a thought refusing to land.", key: 'skyship_refusing_to_land', next: "poet_round_one_result" }] : []),
                    ...(hasMagnekinMemory ? [{ text: "A citizen made of tiny cities, held together by magnets and embarrassment.", key: 'citizen_made_of_tiny_cities', next: "poet_round_one_result" }] : []),
                    ...(hasNoiseGodMemory ? [{ text: "A punk chord where a dead god still keeps time under the floorboards.", key: 'punk_chord_dead_god_keeps_time', next: "poet_round_one_result" }] : []),
                    ...(hasAuctionMemory ? [{ text: "A prophetic toad in a brass jar, blinking three minutes ahead of the bids.", key: 'prophetic_toad_three_minutes_ahead', next: "poet_round_one_result" }] : []),
                    ...(hasThorne ? [{ text: "[Thorne-Still] A thorn that refuses the garden and still becomes part of its shape.", key: 'thorne_refuses_the_garden', next: "poet_round_one_result" }] : []),
                    { text: "A locked Townhall digesting every citizen who knocks.", key: 'locked_townhall_digesting_citizens', next: "poet_round_one_result" },
                    { text: "Your poem is bad and your hat is worse.", key: 'your_poem_is_bad_and_hat_worse', next: "poet_round_one_result" },
                ],
                onTrigger: (option) => option ? this.handlePoetryChoice('round_one', option.key) : null
            },

            poet_round_one_result: {
                speaker: 'The Mad Poet',
                textKey: this.getPoetryResponseKey('round_one'),
                text: this.getPoetryResponseText('round_one'),
                hideCloseOption: true,
                options: [
                    { text: "Continue to Round Two.", key: 'continue_to_round_two', next: "poet_round_two" },
                ]
            },

            poet_round_two: {
                speaker: 'The Mad Poet',
                text: `Round Two — WOUND.

"A city is not described by landmarks," he says. "It is described by what it does to the soft parts. Name the wound without making it smaller."`,
                hideCloseOption: true,
                options: [
                    ...(hasDreamDeathMemory ? [{ text: "A dream device turned comfort into a loop sharp enough to bruise the dead.", key: 'dream_device_bruised_the_dead', next: "poet_round_two_result" }] : []),
                    ...(hasRedmassMemory ? [{ text: "A living redmass begging not to become someone else's proof of loyalty.", key: 'redmass_begging_not_proof', next: "poet_round_two_result" }] : []),
                    ...(hasRustMemory ? [{ text: "The machines of the Rust Choir hum after every empire forgets its own tune.", key: 'rust_choir_machines_hum', next: "poet_round_two_result" }] : []),
                    ...(hasShedMemory ? [{ text: "Shed 521 taught me that forms can amputate more cleanly than knives.", key: 'shed_forms_amputate', next: "poet_round_two_result" }] : []),
                    ...(hasEdgarMemory ? [{ text: "A mišutkenn writer carrying a festival's fire in his ribs and still asking for a story.", key: 'misutkenn_writer_festival_fire', next: "poet_round_two_result" }] : []),
                    ...(hasSulkberryClearMemory ? [{ text: "Clean Sulkberries, accused because fear needed somewhere convenient to rot.", key: 'clean_sulkberries_accused_by_fear', next: "poet_round_two_result" }] : []),
                    ...(hasGodgraveyardMemory ? [{ text: "A divinographer waiting for permits while dead gods fossilize beneath the stamps.", key: 'divinographer_waiting_dead_gods', next: "poet_round_two_result" }] : []),
                    ...(hasNeme ? [{ text: "[Neme] The hostages are roots under stone: terrified, connected, still alive.", key: 'neme_hostages_roots_under_stone', next: "poet_round_two_result" }] : []),
                    ...(hasUlvarex ? [{ text: "[Ulvarex] Project applause over the room until fear looks like admiration.", key: 'ulvarex_project_applause', next: "poet_round_two_result" }] : []),
                    { text: "The wound is boredom. Everyone is tired of listening.", key: 'wound_is_boredom', next: "poet_round_two_result" },
                ],
                onTrigger: (option) => option ? this.handlePoetryChoice('round_two', option.key) : null
            },

            poet_round_two_result: {
                speaker: 'The Mad Poet',
                textKey: this.getPoetryResponseKey('round_two'),
                text: this.getPoetryResponseText('round_two'),
                hideCloseOption: true,
                options: [
                    { text: "Continue to the final round.", key: 'continue_to_final_round', next: "poet_round_three" },
                ]
            },

            poet_round_three: {
                speaker: 'The Mad Poet',
                text: `Round Three — VERDICT.

The poet raises the revolver again, but uncertainty has entered his meter.

"End it," he whispers. "Tell me what the poem demands."`,
                hideCloseOption: true,
                options: [
                    { text: "The city has heard you. Now let it answer without your gun.", key: 'city_heard_you_without_gun', next: "poet_judgment" },
                    ...(hasEdgarMemory ? [{ text: "Let this become a story someone survives to revise.", key: 'story_someone_survives_to_revise', next: "poet_judgment" }] : []),
                    ...(hasMagnekinMemory ? [{ text: "Even a city made of smaller cities survives by consent, not hostage law.", key: 'city_of_smaller_cities_consent', next: "poet_judgment" }] : []),
                    ...(hasRedmassMemory ? [{ text: "The redmass taught me: what is given freely sings longer than what is torn out.", key: 'redmass_given_freely_sings', next: "poet_judgment" }] : []),
                    ...(hasNoiseGodMemory ? [{ text: "Let your poem become noise they can leave humming, not a room they die inside.", key: 'poem_noise_they_leave_humming', next: "poet_judgment" }] : []),
                    ...(hasSulkberryClearMemory ? [{ text: "Truth does not need a hostage to be examined. Release them and remain true.", key: 'truth_needs_no_hostage', next: "poet_judgment" }] : []),
                    ...(hasBrine ? [{ text: "[Brine Scripture] Even ink dries into salt. Let the hurt remain, not the hostages.", key: 'brine_ink_dries_into_salt', next: "poet_judgment" }] : []),
                    ...(hasNeme ? [{ text: "[Neme] A living poem releases what it holds too tightly.", key: 'neme_living_poem_releases', next: "poet_judgment" }] : []),
                    { text: "The poem demands you surrender before everyone realizes you're afraid.", key: 'surrender_before_they_see_fear', next: "poet_judgment" },
                    { text: "It demands blood. Yours, if necessary.", key: 'demands_blood_yours', next: "poet_judgment" },
                ],
                onTrigger: (option) => option ? this.handlePoetryChoice('round_three', option.key) : null
            },

            poet_judgment: {
                speaker: 'The Mad Poet',
                textKey: this.getPoetryResponseKey('round_three'),
                text: this.getPoetryResponseText('round_three'),
                hideCloseOption: true,
                options: [
                    { text: "Let the line fall.", key: 'let_the_line_fall', next: "poet_judgment_result" },
                ],
                onTrigger: (option) => option ? this.resolvePoetryBattle() : null
            },

            poet_victory: {
                speaker: 'The Mad Poet',
                text: `The revolver clatters onto the dais. The sound is louder than any line he read all night.

"...Fine," the poet says, and the meter drains out of him all at once. "You answered. Someone finally answered.

Thirty years I mistook the silence for the city's verdict. Maybe the verdict was only ever that no one had said anything back."

He gathers his pages with shaking hands.

"Keep the gun. Burn the pages, if you like. I think I am done editing."

He steps down between the freed hostages and walks out into the unstamped morning, leaving only ink, sweat, and a silence that belongs to everyone now.`,
                options: [
                    { text: "Check on the hostages.", key: 'check_on_the_hostages', next: "clerk_after_poet" },
                ],
                onTrigger: (option) => {
                    if (option) return 'clerk_after_poet';
                    this.completePoetStandoff();
                }
            },

            poet_defeat: {
                speaker: 'The Mad Poet',
                text: `The poet listens to your last line, and something in his face settles into a terrible, grateful calm.

"Dead art," he murmurs. "At last — honesty. You have proved my thesis for me.

A line that cannot live
must end the way all dead lines end."

The revolver rises without hurry. The clerk's scream is the last thing the Townhall files tonight, and the reading becomes history in the worst possible meter.`,
                hideCloseOption: true,
                options: [
                    { text: "GAME OVER", key: 'game_over', next: "poet_game_over" },
                ]
            },

            poet_game_over: {
                onShow: () => this.showPoetryGameOver()
            },

            clerk_after_poet: {
                speaker: 'Freed Clerk',
                textKey: clerkAfterPoetTextKey,
                text: townhallRecordsChecked
                    ? `"The archive cabinets are open now. I already pulled the Bishop file for you — or what passes for a file after the Townhall has finished avoiding responsibility."`
                    : `"Thank you. The official minutes will call this a 'lyrical disruption with hostage characteristics.' That sounds less embarrassing than the truth.

The records office is still a mess, but the Townhall can breathe again. If you need the Bishop records, ask now before someone invents a recovery committee."`,
                options: [
                    ...(!townhallRecordsChecked ? [{ text: "I need the Bishop's Townhall records.", key: 'i_need_the_bishops_townhall_records', next: "clerk_bishop_records" }] : []),
                    ...(townhallRecordsChecked ? [{ text: "Remind me what the Bishop records showed.", key: 'remind_me_what_the_bishop_records_showed', next: "clerk_bishop_records_summary" }] : []),
                ]
            },

            clerk_bishop_records: {
                speaker: 'Freed Clerk',
                text: `"Right. Bishop, Obazoba representative, Cathedral Council, doppelgänger report... one moment."

The clerk unlocks three cabinets, rejects two drawers as "emotionally inaccurate," and finally produces a thin intake ledger.

"This is the strange part. There is no official incident report under the Bishop's name. No filed doppelgänger complaint. No follow-up. What exists is a stationery issue record: she requested an Official Townhall Report Notebook three digestions before she died. I stamped it myself.

That fragment you found was not an official report. It was a personal note written in official stationery."`,
                options: [
                    { text: "So the rest of the notebook exists.", key: 'so_the_rest_of_the_notebook_exists', next: "clerk_bishop_notebook_hook" },
                    { text: "Were there other doppelgänger reports?", key: 'were_there_other_doppelganger_reports', next: "clerk_other_doppelganger_reports" },
                ],
                onTrigger: () => this.completeTownhallBishopRecordsCheck()
            },

            clerk_bishop_notebook_hook: {
                speaker: 'Freed Clerk',
                text: `"Almost certainly. Townhall report notebooks are bound in numbered sections. If one page survived in her sleeve, the rest of that notebook went somewhere.

The checkout slip says she took it with her after closing. No return stamp. No archive copy. If she used official stationery as a private diary, the missing pages could explain the doppelgänger encounters, the changing spores, and why she sealed the Cathedral.

Find the notebook. The Townhall cannot misfile what it never got back."`,
                options: [
                    { text: "I'll find the Bishop's notebook.", key: 'ill_find_the_bishops_notebook', next: "closeDialog" },
                    { text: "What about other doppelgänger reports?", key: 'what_about_other_doppelganger_reports', next: "clerk_other_doppelganger_reports" },
                ],
                onTrigger: () => {
                    this.addJournalFact('townhall_bishop_records_checked', 'not_returned', "The notebook was never returned to the Townhall.");
                    this.addJournalFact('townhall_bishop_records_checked', 'missing_pages', "If she kept it as a private diary, the missing pages may hold more about the doppelgänger, the changing spores, and why she sealed the Cathedral.");
                    this.markNotebookNotReturned();
                }
            },

            clerk_other_doppelganger_reports: {
                speaker: 'Freed Clerk',
                text: `"No public reports under 'doppelgänger,' 'duplicate citizen,' 'non-breathing self,' or the old category 'mirror-related civic unease.' I checked because those are exactly the sort of categories clerks invent and then regret.

There is one sealed cross-reference: 'Cathedral-adjacent identity irregularity — theological emergency.' Same week. Same clerk stamp series. Whoever filed it wanted the Townhall to look away without technically lying.

So: no pattern I can prove. But the Bishop was not merely frightened. She was documenting something."`,
                options: [
                    { text: "Then the notebook is the next lead.", key: 'then_the_notebook_is_the_next_lead', next: "clerk_bishop_notebook_hook" },
                    { text: "That's enough for now.", key: 'thats_enough_for_now', next: "closeDialog" },
                ],
                onTrigger: () => this.completeTownhallBishopRecordsCheck()
            },

            clerk_bishop_records_summary: {
                speaker: 'Freed Clerk',
                text: `"Short version: the Bishop's doppelgänger note was not a filed Townhall report. It was a personal entry written in an Official Townhall Report Notebook she checked out shortly before death.

The notebook was never returned. If the torn page is real, the rest of the notebook is probably the next real clue."`,
                options: [
                    { text: "I'll keep looking.", key: 'ill_keep_looking', next: "closeDialog" },
                ],
                onTrigger: () => {
                    this.addJournalFact('townhall_bishop_records_checked', 'not_returned', "The notebook was never returned to the Townhall.");
                    this.markNotebookNotReturned();
                }
            },

            complaint_eater_start: {
                speaker: 'Complaint Eater',
                text: `The creature behind the counter folds a stack of grievance forms into its mouth. Every bite makes a tiny official stamp sound.

"Mmm. Appeals with fear sauce. Delicious. Are you here to file a complaint, withdraw one, or become one?"`,
                options: [
                    { text: "What are you?", key: 'what_are_you', next: "complaint_eater_identity" },
                    { text: "Have you eaten anything about the Bishop?", key: 'eaten_anything_about_the_bishop', next: "complaint_eater_bishop" },
                    { text: "Who is the councilor?", key: 'who_is_the_councilor', next: "complaint_eater_councilor" },
                ]
            },

            complaint_eater_identity: {
                speaker: 'Complaint Eater',
                text: `"Municipal digestion. Every city needs one. Citizens bring pain to the desk, clerks turn it into paper, and I make sure the paper does not learn to breed.

Do not pity the complaints. Most of them wanted to be eaten. It is the appeals that scream."`,
                options: [
                    { text: "That's useful, I suppose.", key: 'thats_useful_i_suppose', next: "complaint_eater_start" },
                ]
            },

            complaint_eater_bishop: {
                speaker: 'Complaint Eater',
                textKey: complaintEaterBishopTextKey,
                text: townhallRecordsChecked
                    ? `"The Bishop's paper tasted wrong: not filed, not digested, not ours. Personal ink in official clothing. The clerk has the truth of it. I only know what refuses my stomach."`
                    : `"Bishop-paper is locked behind frightened drawers. Ask the freed clerk. Clerks can open cabinets. I can only open consequences."`,
                options: [
                    { text: "I'll ask the clerk.", key: 'ill_ask_the_clerk', next: "clerk_after_poet" },
                    { text: "Ask something else.", key: 'ask_something_else', next: "complaint_eater_start" },
                ]
            },

            complaint_eater_councilor: {
                speaker: 'Complaint Eater',
                text: `"Seraphel Dune? A high-functioning apology in a formal coat. He signs what other officials only fear in cursive.

If the Townhall owes you a reward, make him say it out loud. Spoken debt is harder to misfile."`,
                options: [
                    { text: "I'll speak with Councilor Dune.", key: 'ill_speak_with_councilor_dune', next: "councilor_start" },
                    { text: "Ask something else.", key: 'ask_something_else', next: "complaint_eater_start" },
                ]
            },

            councilor_start: {
                speaker: 'Councilor Seraphel Dune',
                textKey: councilorStartTextKey,
                text: hasGodgraveyardAccess
                    ? `"The Godgraveyard access order is already sealed in your name. The lower doors will recognize the Townhall's apology, which is the closest thing this building has to a key."`
                    : `Councilor Seraphel Dune stands beside a cabinet of emergency seals, looking as if he has personally disappointed every law in the room.

"You ended a hostage crisis without adding bodies to the minutes. The Townhall is in your debt. I have authority to convert that debt into one useful impossibility."`,
                options: [
                    ...(!hasGodgraveyardAccess ? [{ text: "Grant access to the Godgraveyard.", key: 'grant_access_to_the_godgraveyard', next: "councilor_godgraveyard_reward" }] : []),
                    { text: "What happens to the poet?", key: 'what_happens_to_the_poet', next: "councilor_poet" },
                    { text: "What is wrong with this Townhall?", key: 'what_is_wrong_with_this_townhall', next: "councilor_townhall" },
                    ...(townhallRecordsChecked ? [{ text: "The Bishop's records were tampered with.", key: 'bishops_records_were_tampered_with', next: "councilor_bishop_records" }] : []),
                    ...(pithKnown && !pithJoined && !hasPithQuest ? [{ text: "The Tribunal takes in the city's strays. Could I be part of that?", key: 'ask_join_pith', next: "councilor_pith_offer" }] : []),
                    ...(hasPithQuest && !pithJoined && hasPithRecruit ? [{ text: "I've found a soul for the Tribunal.", key: 'present_pith_recruit', next: "councilor_pith_present" }] : []),
                    ...(canGiveDrugsPith ? [{ text: "[Contraband] I'm carrying smuggled narcotics. I want them off the street, on the record.", key: 'councilor_drug_surrender', next: "councilor_drug_surrender_talk" }] : []),
                ]
            },

            councilor_drug_surrender_talk: {
                speaker: 'Councilor Seraphel Dune',
                text: `Dune regards the parcel with the weariness of a man who has filed too many like it. "Wimlick. And you're bringing it to me rather than moving it." He produces a ledger seemingly from nowhere. "The Tribunal accounts for what the city discards — including the trade that discards people. This will be entered as recovered contraband, and the fact that it passed through your hands will be entered honestly alongside it. No profit for you. No hole in the record either." He takes the parcel. "That is the deal the Tribunal offers: you are neither hero nor criminal here. You are *accounted for*."`,
                options: [
                    { text: "Enter it. All of it.", key: 'councilor_drug_surrender_close', next: "councilor_start" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('gang_smuggle_gave_pith')) {
                        this.removeItemFromInventory('wimlick');
                        this.addJournalEntry('gang_smuggle_gave_pith', 'Surrendered to the Tribunal', "Rather than run Torchère's contraband, I surrendered the Wimlick to Councilor Dune. The Ink Tribunal logged it as recovered contraband — and logged my part in it honestly. Torchère will assume the drop was made.", this.journalSystem.categories.EVENTS, { group: 'Gang of Lamps', related: 'A Run Past the Customs' });
                        this.modifyFactionReputation('PithReclaimers', 15);
                        this.modifyGrowthDecay(5, 0);
                        this.notifyShift('contraband_recorded', 'growth');
                    }
                }
            },

            councilor_godgraveyard_reward: {
                speaker: 'Councilor Seraphel Dune',
                text: hasExcavationPermitQuest
                    ? `"Phor Calesta's excavation petition has been waiting for three committees, two theological impact studies, and one clerk brave enough to admit the lower doors exist.

Consider the waiting finished. I am granting you and your divinographer access to the Godgraveyard level beneath the Townhall. If anything down there asks who permitted you, show it my seal and do not accept its counteroffer."`
                    : `"You may not have asked for a divinography permit, but you have earned a dangerous favor. I am granting you access to the Godgraveyard level beneath the Townhall.

If anything down there asks who permitted you, show it my seal and do not accept its counteroffer."`,
                options: [
                    { text: "I'll use it carefully.", key: 'ill_use_it_carefully', next: "councilor_start" },
                ],
                onTrigger: () => this.grantGodgraveyardAccess()
            },

            councilor_poet: {
                speaker: 'Councilor Seraphel Dune',
                text: `"Officially: detainment, evaluation, restitution, and a ban from all public readings longer than seven minutes.

Unofficially: the Townhall created the pressure that made him explode. That does not excuse the gun. It does mean the minutes will have to learn shame."`,
                options: [
                    { text: "Ask something else.", key: 'ask_something_else', next: "councilor_start" },
                ]
            },

            councilor_townhall: {
                speaker: 'Councilor Seraphel Dune',
                text: `"This building was designed to turn public terror into indexed paper. It succeeded too well. Somewhere along the way, the archive began protecting the process instead of the people.

The Complaint Eater keeps it from choking on itself. Barely."`,
                options: [
                    { text: "Ask something else.", key: 'ask_something_else', next: "councilor_start" },
                ]
            },

            councilor_bishop_records: {
                speaker: 'Councilor Seraphel Dune',
                text: `"Tampered with, avoided, or filed under a category that bites anyone who pronounces it. I cannot yet tell which.

But if the Bishop used official stationery as a private notebook, she was hiding truth in the one place nobody here would willingly read: paperwork."`,
                options: [
                    { text: "The missing notebook is still the lead.", key: 'missing_notebook_is_still_the_lead', next: "councilor_start" },
                ]
            },

            // --- Ink Tribunal: joining ---
            councilor_pith_offer: {
                speaker: 'Councilor Seraphel Dune',
                text: `Seraphel Dune considers you the way an auditor considers a promising irregularity. "The Tribunal is not a faith, and not an army. We are the city's memory of order — we file what would otherwise be lost, and take in what would otherwise fall through the cracks. Souls with nowhere to be indexed.\n\nIf you would join us, prove you understand the work: find one such soul — unmoored, unfiled, adrift — and bring them into the fold. Give the city one more citizen it can account for. Do that, and a door opens."`,
                options: [
                    { text: "I'll find someone.", key: 'pith_accept', next: "councilor_pith_accepted" },
                    { text: "Who did you have in mind?", key: 'pith_who', next: "councilor_pith_who" },
                    { text: "Not my kind of work.", key: 'pith_decline', next: "councilor_start" },
                ]
            },
            councilor_pith_who: {
                speaker: 'Councilor Seraphel Dune',
                text: `"The city is full of the unaccounted. Pick one. Convince them that being written down is a kind of safety." A dry pause. "Most people spend their lives trying to stay un-filed. The ones who want in — those are ours."`,
                options: [
                    { text: "I'll find someone.", key: 'pith_accept_2', next: "councilor_pith_accepted" },
                    { text: "Let me think.", key: 'pith_think', next: "councilor_start" },
                ]
            },
            councilor_pith_accepted: {
                speaker: 'Councilor Seraphel Dune',
                text: `"Good. The Senior Clerk will handle the paperwork when you return with your candidate. Try to bring someone who can hold a pen — or approximate one."`,
                options: [
                    { text: "Understood.", key: 'pith_accepted_ok', next: "councilor_start" },
                ],
                onTrigger: () => {
                    if (!this.questSystem?.getQuest('join_pith_reclaimers')) {
                        this.questSystem.addQuest('join_pith_reclaimers', 'One More Citizen', 'Councilor Seraphel Dune will admit me to the Ink Tribunal if I bring him a soul — someone unmoored and unfiled — and convince them to be recorded as a citizen. Then return to Seraphel.');
                        this.showNotification('New quest: One More Citizen', 0xffdf7a);
                    }
                }
            },
            councilor_pith_present: {
                speaker: 'Councilor Seraphel Dune',
                text: `You explain who you've brought into the fold. Seraphel Dune's severe face does something unfamiliar — approval. "A citizen where there was a gap in the record. Good." He raps the cabinet twice; the Senior Clerk materializes with a ledger already open. "The paperwork is being done as we speak. Sign here, here, and — regrettably — here.\n\nIt is done. You are of the Tribunal now. There is a room beneath this building the committees pretend not to remember. It is yours now. Bring us more of the unaccounted, and the Tribunal will not forget who did the accounting."`,
                options: [
                    { text: "A room beneath the Townhall?", key: 'pith_room_ask', next: "councilor_pith_room" },
                    { text: "I'll bring you more.", key: 'pith_bring_more', next: "councilor_start" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('pith_reclaimers_joined')) {
                        this.addJournalEntry(
                            'pith_reclaimers_joined',
                            'Member of the Ink Tribunal',
                            'I brought the Ink Tribunal a soul to file, and Councilor Seraphel Dune admitted me to the faction. The Tribunal preserves the city\'s order by accounting for what would otherwise be lost — and it has opened a hidden room beneath the Townhall to me. The more souls I bring it, the more the Tribunal owes me.',
                            this.journalSystem.categories.FACTIONS,
                            { group: 'Ink Tribunal' }
                        );
                        this.modifyFactionReputation('PithReclaimers', 25);
                        this.registry.set('pith_room_unlocked', true);
                        this.showNotification('You are now a member of the Ink Tribunal', 0xffdf7a);
                        if (this.moneySystem) {
                            this.moneySystem.add(30);
                            this.showNotification('The Tribunal grants a filing stipend: +30', 0xffdf7a);
                        }
                    }
                    const q = this.questSystem?.getQuest('join_pith_reclaimers');
                    if (q && !q.isComplete) {
                        this.questSystem.completeQuest('join_pith_reclaimers');
                        this.showNotification('Quest complete: One More Citizen', 0xffdf7a);
                    }
                }
            },
            councilor_pith_room: {
                speaker: 'Councilor Seraphel Dune',
                text: `"A reading room. Archive-adjacent. Off the record, which in this building is the only kind of privacy that survives. You'll find the way down marked with the Tribunal's seal, now that your name is on it. Rest there. Store what you must. The room remembers its members — and grows more useful the more of the city we manage to account for."`,
                options: [
                    { text: "Understood.", key: 'pith_room_ok', next: "councilor_start" },
                ]
            },
        };
    }

    preload() {
        super.preload();
        this.load.image('townhallInteriorBg', 'assets/images/backgrounds/townhall_interior.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        for (const c of Object.values(TH_CAST)) {
            this.load.spritesheet(c.key, `assets/images/characters/townhall/${c.file}.png`, { frameWidth: c.w, frameHeight: c.h });
        }
        this.load.image('box', 'assets/images/items/box.png');
    }

    create() {
        super.create();
        this.playSceneMusic('genericMusic');
        // the scene instance is re-used: drop the people of the previous visit (their objects are gone)
        this.poet = null;
        this.hostages = [];
        this.clerk = null;
        this.complaintEater = null;
        this.councilor = null;

        // The council hall (native 1067x600, tools/artgen/townhall_int_bg.py)
        const bg = this.add.image(400, 300, 'townhallInteriorBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        // The background paints its own floor; drop the generic ground strip
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }

        this.transitionManager = new SceneTransitionManager(this);

        this.transitionManager.createTransitionZone(
            400,
            560,
            180,
            80,
            'down',
            'TownhallScene',
            400,
            540,
            'Townhall Exterior'
        );

        // Members-only: the hidden Tribunal's Room opens once you've joined the Tribunal. Its way
        // down is the low oak door in the left wall between the record cabinets (canvas polygon from
        // townhall_int_bg.py's fixed points); the door is painted always, it only opens for members.
        if (this.hasJournalEntry('pith_reclaimers_joined')) {
            this.transitionManager.createDoorZone({
                points: [[227, 450], [252, 437], [252, 355], [250, 348], [247, 342], [240, 339], [233, 338],
                    [229, 340], [227, 343]]
            }, { target: 'PithReclaimersRoomScene', walkX: 250, walkY: 470, label: "The Tribunal's Room" });
        }

        // the walk line of the redrawn hall: feet on y 534 (centre origin, 128 px tall)
        this.priest.x = 400;
        this.priest.y = 470;

        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // Bust portraits for the hall's people, from their idle sheets (keyed by the English and the Czech speaker name)
        this.dialogPortraits = { ...(this.dialogPortraits || {}) };
        for (const c of Object.values(TH_CAST)) {
            for (const name of c.names) this.dialogPortraits[name] = { key: c.key, frame: 0, zoom: 2, top: c.top };
        }

        this.completeEnterTownhallQuestOnFirstEntry();
        const firstPoetEntry = this.startPoetStandoffQuestIfNeeded();
        this.createTownhallPlaceholders();
        this.createMisfiledDossierSpot();

        this.cameras.main.fadeIn(800, 0, 0, 0);

        // On the very first entry, the standoff opens itself — the poet is
        // already mid-reading and will not let the player simply walk past it.
        if (firstPoetEntry && !this.hasJournalEntry('townhall_poet_resolved')) {
            this.time.delayedCall(900, () => this.showDialog('poet_intro'));
        }
    }

    completeEnterTownhallQuestOnFirstEntry() {
        const quest = this.questSystem?.getQuest('enter_townhall');

        if (!quest || quest.isComplete) return;

        this.addJournalEntry(
            'entered_townhall',
            'Entered the Townhall',
            'I made it inside the Townhall.',
            this.journalSystem.categories.EVENTS,
            { location: 'Townhall' }
        );
        // The quest can come from Elphi or from Phor — only note the leads the player actually has.
        if (this.hasJournalEntry('bishop_memo') || this.hasJournalEntry('elphi_townhall_log')) {
            this.addJournalFact('entered_townhall', 'bishop_report', "Now I can search the records for the Bishop's doppelgänger report.");
        }
        if (this.questSystem?.getQuest('excavation_permit')) {
            this.addJournalFact('entered_townhall', 'phor_permits', "And I can try to get Phor Calesta his excavation permits.");
        }

        this.questSystem.updateQuest(
            'enter_townhall',
            'I made it inside the Townhall.',
            'entered_townhall'
        );
        // Same route split as the journal facts above: only name the leads the player actually has.
        if (this.hasJournalEntry('bishop_memo') || this.hasJournalEntry('elphi_townhall_log')) {
            this.questSystem.updateQuest('enter_townhall', "Now I can search the records for the Bishop's doppelgänger report.", 'entered_townhall_records');
        }
        if (this.questSystem?.getQuest('excavation_permit')) {
            this.questSystem.updateQuest('enter_townhall', 'Now I can try to get Phor Calesta his excavation permits.', 'entered_townhall_permits');
        }
        this.questSystem.completeQuest('enter_townhall');
    }

    startPoetStandoffQuestIfNeeded() {
        if (this.hasJournalEntry('townhall_poet_resolved')) return false;

        // True only on the very first entry, before the standoff journal entry exists.
        const isFirstEntry = !this.hasJournalEntry('townhall_poet_standoff');

        if (!this.questSystem?.getQuest('townhall_poet_standoff')) {
            this.questSystem.addQuest(
                'townhall_poet_standoff',
                'The Mad Poet Standoff',
                'A mad poet has seized the Townhall reading chamber and is holding the clerk, councilor, and Complaint Eater hostage until the public properly hears his work. This cannot be solved with ordinary force; I need to defeat him in a poetry battle.'
            );
        }

        if (!this.hasJournalEntry('townhall_poet_standoff')) {
            this.addJournalEntry(
                'townhall_poet_standoff',
                'The Mad Poet Standoff',
                'Inside the Townhall, a mad poet is holding the clerk, councilor, and Complaint Eater hostage for a public reading. He seems obsessed with being truly heard. A poetry battle may be the only safe way to end this.',
                this.journalSystem.categories.EVENTS,
                { location: 'Townhall' }
            );
        }

        return isFirstEntry;
    }

    createTownhallPlaceholders() {
        if (this.hasJournalEntry('townhall_poet_resolved')) {
            this.createFreedClerkCharacter();
            this.createComplaintEaterCharacter();
            this.createCouncilorCharacter();
            return;
        }

        this.createHostageCharacters();
        this.createPoetCharacter();
    }

    createPoetCharacter() {
        this.poet = this.createCharacterNpc({ id: 'poet', ...TH_SPOTS.poet, dialog: 'poet_start', depth: 6 });
    }

    createHostageCharacters() {
        // the same people, held where they stood when he took the hall; each of them points you to the poet
        this.hostages = [
            this.createCharacterNpc({ id: 'clerk', ...TH_SPOTS.clerk, dialog: 'poet_start' }),
            this.createCharacterNpc({ id: 'eater', ...TH_SPOTS.eater, dialog: 'poet_start' }),
            this.createCharacterNpc({ id: 'councilor', ...TH_SPOTS.councilor, dialog: 'poet_start' }),
        ];
    }

    createFreedClerkCharacter() {
        this.clerk = this.createCharacterNpc({ id: 'clerk', ...TH_SPOTS.clerk, dialog: 'clerk_after_poet' });
    }

    createComplaintEaterCharacter() {
        this.complaintEater = this.createCharacterNpc({ id: 'eater', ...TH_SPOTS.eater, dialog: 'complaint_eater_start' });
    }

    // Gang of Lamps (Sconce's quest): the misfiled dossier buried in the records drawers.
    // Present only while Sconce's recover job is active and the dossier hasn't been pulled.
    // Clicking opens a route-choice dialog (plain / Palinode / Brine).
    createMisfiledDossierSpot() {
        const active = gangQuestStatus(this, GANG_QUEST_IDS.sconce) === 'active';
        const alreadyHas = this.hasItem('filed_dossier');
        const alreadyPulled = !!this.hasJournalEntry('gang_dossier_recovered');
        if (!active || alreadyHas || alreadyPulled) return;

        // the drawer bank of the nearest record cabinet on the left wall (canvas coords of the painted art)
        const x = 108, y = 418;
        const drawer = this.add.rectangle(x, y, 64, 52, 0xffe6a8, 0).setDepth(3);
        drawer.setStrokeStyle(2, 0xffd27a, 0);
        drawer.setInteractive({ useHandCursor: true });
        const hint = this.add.text(x, y - 40, 'Records drawers', {
            fontSize: '13px', fill: '#7fff8e', backgroundColor: 'rgba(0,0,0,0.5)', padding: { x: 5, y: 2 }
        }).setOrigin(0.5).setDepth(10).setAlpha(0);
        drawer.on('pointerover', () => { hint.setAlpha(1); drawer.setFillStyle(0xffe6a8, 0.12); drawer.setStrokeStyle(2, 0xffd27a, 0.9); document.body.style.cursor = 'pointer'; });
        drawer.on('pointerout', () => { hint.setAlpha(0); drawer.setFillStyle(0xffe6a8, 0); drawer.setStrokeStyle(2, 0xffd27a, 0); document.body.style.cursor = 'default'; });
        this._dossierCleanup = () => { drawer.disableInteractive(); drawer.destroy(); hint.destroy(); this._dossierCleanup = null; };
        drawer.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog('dossier_search');
        });
    }

    // Complete the dossier recovery. `mode`: 'plain' | 'palinode' | 'brine'. Dragging a record
    // that was buried to be forgotten back into the light leans the world toward Growth;
    // using a read/unseal power to do it cleanly leans it a touch further.
    deliverDossier(mode) {
        if (!this.hasJournalEntry('gang_dossier_recovered')) {
            this.addItemToInventory({ id: 'filed_dossier', name: 'Misfiled Dossier', description: "A sealed dossier the Townhall buried under a case-number that doesn't exist. Sconce wants it brought out where it can't be quietly unhappened.", texture: 'box', icon: 'box', stackable: false });
            this.addJournalEntry('gang_dossier_recovered', 'The Buried Dossier', "Under a case-number that matches nothing, I found a sealed dossier that plainly didn't belong, and pulled it. Time to get it out to Sconce by the steps.", this.journalSystem.categories.EVENTS, { group: 'Gang of Lamps', related: 'Recover What Was Filed' });
            if (this.questSystem?.getQuest(GANG_QUEST_IDS.sconce)) {
                this.questSystem.updateQuest(GANG_QUEST_IDS.sconce, "I found the misfiled dossier in the records drawers. Take it out to Sconce by the townhall steps.", 'gang_dossier_recovered');
            }
        }
        const growth = (mode === 'palinode' || mode === 'brine') ? 5 : 3;
        this.modifyGrowthDecay(growth, 0);
        this.notifyShift('buried_truth', 'growth');
        if (this._dossierCleanup) this._dossierCleanup();
    }

    createCouncilorCharacter() {
        this.councilor = this.createCharacterNpc({ id: 'councilor', ...TH_SPOTS.councilor, dialog: 'councilor_start' });
    }

    // One of the hall's people (TH_CAST[id]): the idle sheet at scale 1 with its soles on (x, y), a ground shadow that
    // goes with it, a hover glow, and a click that opens `dialog`.
    createCharacterNpc({ id, x, y, dialog, depth = 5 }) {
        const c = TH_CAST[id];
        if (!this.anims.exists(c.anim)) {
            this.anims.create({ key: c.anim, frames: this.anims.generateFrameNumbers(c.key, { frames: c.frames }), frameRate: c.fps, repeat: -1 });
        }
        // the bottom edge sits one pixel under the soles' row
        const npc = this.add.sprite(x, y + (c.h - 1 - c.sole), c.key, 0).setOrigin(0.5, 1).setDepth(depth);
        npc.play(c.anim);
        const shadow = this.addGroundShadow(x, y - 2, c.shadowW, 10);
        // the shadow goes when the person does (the hostages swap for the freed cast); on a scene shutdown the display list
        // destroys it itself -- destroying it from here then would pull it out of the list mid-iteration
        npc.once('destroy', () => { if (this.sys.isActive()) shadow.destroy(); });
        npc.setInteractive({ hitArea: new Phaser.Geom.Rectangle(...c.hit), hitAreaCallback: Phaser.Geom.Rectangle.Contains, useHandCursor: true });
        let hoverFx = null;
        npc.on('pointerover', () => {
            if (!hoverFx) hoverFx = npc.preFX?.addGlow(0x7fff8e, 2, 0, false, 0.1, 8);
        });
        npc.on('pointerout', () => {
            if (hoverFx) { npc.preFX?.remove(hoverFx); hoverFx = null; }
        });
        npc.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog(dialog);
        });
        return npc;
    }

    resetPoetryBattle() {
        this.registry.set('townhallPoetryBattle', {
            score: 0,
            choices: {}
        });
    }

    handlePoetryChoice(round, choiceKey) {
        const battle = this.registry.get('townhallPoetryBattle') || { score: 0, choices: {} };

        if (!battle.choices[round]) {
            battle.choices[round] = choiceKey;
            battle.score += this.getPoetryChoiceScore(choiceKey);
            this.registry.set('townhallPoetryBattle', battle);
        }

        const resultStates = {
            round_one: 'poet_round_one_result',
            round_two: 'poet_round_two_result',
            round_three: 'poet_judgment',
        };

        return resultStates[round] || 'poet_challenge';
    }

    getPoetryResponseKey(round) {
        const battle = this.registry.get('townhallPoetryBattle') || { choices: {} };
        const choiceKey = battle.choices?.[round];

        return choiceKey ? `poet_response_${choiceKey}` : `poet_response_${round}_default`;
    }

    getPoetryResponseText(round) {
        const battle = this.registry.get('townhallPoetryBattle') || { choices: {} };
        const choiceKey = battle.choices?.[round];

        const responses = {
            second_shadow_watching_first: `The poet inhales sharply, then answers with a line of his own:\n\n"Two shadows under one bad sun —\none flees, one follows, both are run.\nYes. The city has bitten you where the self keeps count."`,
            bishop_met_herself_breathless: `The poet's gun lowers by the width of a comma.\n\n"A self before the self arrives —\na mirror learning how one dies.\nAn image, then. Not merely decoration. A tooth-mark."`,
            egg_cathedral_hatching_scripture: `He touches the page to his forehead.\n\n"Shell-script, yolk-prayer, unborn nave —\nfaiths keep watch around a grave.\nGood. You have seen architecture trying to become a verdict."`,
            skyship_refusing_to_land: `He glances toward the ceiling as if the skyship might be listening.\n\n"A thought in rigging, cloud in chain —\nthe sky says yes, the city: remain.\nAn image with altitude. Continue."`,
            citizen_made_of_tiny_cities: `For one dangerous second, the poet smiles.\n\n"A million roofs in borrowed skin,\na crowd that says: I am one citizen.\nYes. Embarrassment is civic mortar."`,
            punk_chord_dead_god_keeps_time: `A hostage flinches as the poet taps a rhythm with the revolver barrel.\n\n"Dead god, live amp, impossible beat —\nthe buried divine still moves its feet.\nThat image has teeth and volume."`,
            prophetic_toad_three_minutes_ahead: `He snorts despite himself.\n\n"A toad ahead of the auction bell —\nthree minutes of heaven in a jar of smell.\nComic, but alive. I accept the bite."`,
            thorne_refuses_the_garden: `The poet squints at the air around you.\n\n"A thorn outside the gardener's plan\nstill writes the hedge in the blood of a hand.\nUseful. Not enough alone, but useful."`,
            locked_townhall_digesting_citizens: `His pages tremble.\n\n"A door with offices for teeth,\na public stomach underneath.\nYes. This building deserved that."`,
            your_poem_is_bad_and_hat_worse: `The poet goes very still.\n\n"Hat? Hat?\nA fool mistakes the scalp for crown,\nand wonders why the line falls down.\nInsult is not image. It is failed weather."`,

            dream_device_bruised_the_dead: `The poet's voice drops until even the hostages lean in.\n\n"Dream loops. Temple bruises. Mercy redacts the bed.\nA program chews the sleeper and returns the sleeper dead.\nThat wound is real."`,
            redmass_begging_not_proof: `The revolver wavers.\n\n"Loyalty fed from another's scream\nis rust pretending it had a dream.\nYou name the wound without polishing it."`,
            rust_choir_machines_hum: `He answers in a hoarse half-song.\n\n"Empires forget. Engines repeat.\nIron keeps the last honest beat.\nThe wound hums. I hear it."`,
            shed_forms_amputate: `One clerk laughs once, then looks horrified at themselves.\n\n"Form seventeen, annex three: remove the hand that signs to be free.\nBureaucracy as blade. Good. Cruel and exact."`,
            misutkenn_writer_festival_fire: `The poet looks ashamed before he can hide it.\n\n"Bear-skin bonfire, author-heart —\nwhat they burned became his art.\nA wound that asks for a book instead of revenge."`,
            clean_sulkberries_accused_by_fear: `He grimaces as if tasting something medicinal.\n\n"Clean fruit in a guilty bowl —\nfear salts whatever it cannot control.\nA smaller wound, but a true one."`,
            divinographer_waiting_dead_gods: `Dust seems to settle over the dais.\n\n"Dead gods below, live stamps above —\nthe permit denies the fossil love.\nYes. The city can wound even its archaeologists."`,
            neme_hostages_roots_under_stone: `The poet hears the hostages breathing together.\n\n"Roots under stone do not cease to grow;\nthey carry the dark where the leaves cannot go.\nYour symbiont sees the room. You still had to say it."`,
            ulvarex_project_applause: `For a moment, phantom applause trembles in the room. The poet's eyes harden.\n\n"Borrowed hands make borrowed praise;\nmirrors cannot end hostage days.\nPretty. Too pretty."`,
            wound_is_boredom: `The poet smiles with terrible relief.\n\n"Boredom, says the empty cup,\nthen wonders why no one fills it up.\nYou have named your impatience, not the wound."`,

            city_heard_you_without_gun: `The poet lifts the revolver, then hears the weakness in that gesture.\n\n"If hearing must be held at gun,\nthe poem was already afraid.\nThe line lands cleanly. Now we see if it holds."`,
            story_someone_survives_to_revise: `He looks at his pages as if they have betrayed him by remaining editable.\n\n"A draft that kills its reader dies;\na living text survives replies.\nA generous verdict. Dangerous."`,
            city_of_smaller_cities_consent: `His expression fractures into attention.\n\n"Even one body may be a town;\nconsent is what keeps walls from falling down.\nYou bring civic theology to a gunpoint recital. Good."`,
            redmass_given_freely_sings: `The gun sinks toward his side.\n\n"Torn metal screams and stains the hand;\ngiven metal joins the band.\nYou understand release."`,
            poem_noise_they_leave_humming: `Somewhere in the walls, pipes vibrate like a distant amplifier.\n\n"A song is proved by open doors,\nnot bodies counted on the floors.\nI hate how nearly beautiful that is."`,
            truth_needs_no_hostage: `He swallows. The hostages hear it.\n\n"Truth in chains becomes a lie;\nrelease the breath, or watch it die.\nA verdict with a spine."`,
            brine_ink_dries_into_salt: `Salt stings behind your teeth. The poet hears something older than flattery.\n\n"Ink to salt and hurt to shore —\nkeep the wound, but lock no door.\nMemory helps you. It does not replace you."`,
            neme_living_poem_releases: `Neme's presence opens like a green hush beneath your words.\n\n"A root that grips until roots break\nmust learn what living things forsake.\nA symbiont's wisdom, carried by your mouth."`,
            surrender_before_they_see_fear: `The poet's shame curdles into pride.\n\n"Name me coward, call it art —\nyou miss the wound and strike the heart.\nPerhaps true. Not useful."`,
            demands_blood_yours: `The poet's face becomes calm in the worst possible way.\n\n"Blood is the cheapest crimson word;\nevery butcher thinks himself heard.\nYou have mistaken violence for ending."`,
        };

        return responses[choiceKey] || this.getDefaultPoetryResponseText(round);
    }

    getDefaultPoetryResponseText(round) {
        const defaults = {
            round_one: `The poet's gun lowers by the width of a comma.\n\n"An image, then. Not merely decoration. A tooth-mark. Continue."`,
            round_two: `A clerk sobs once, quietly, as if punctuation has escaped them.\n\nThe poet hears it. For the first time, shame crosses his face without announcing itself as genius.`,
            round_three: `For a long second, the Townhall is nothing but breath.\n\nThe poet looks at the hostages, then at his pages, then at you. The poem has reached its final line.`,
        };

        return defaults[round] || defaults.round_one;
    }

    getPoetryChoiceScore(choiceKey) {
        const scores = {
            second_shadow_watching_first: 2,
            bishop_met_herself_breathless: 2,
            egg_cathedral_hatching_scripture: 1,
            skyship_refusing_to_land: 1,
            citizen_made_of_tiny_cities: 2,
            punk_chord_dead_god_keeps_time: 2,
            prophetic_toad_three_minutes_ahead: 1,
            thorne_refuses_the_garden: 1,
            locked_townhall_digesting_citizens: 1,
            your_poem_is_bad_and_hat_worse: -2,
            dream_device_bruised_the_dead: 2,
            redmass_begging_not_proof: 2,
            rust_choir_machines_hum: 2,
            shed_forms_amputate: 2,
            misutkenn_writer_festival_fire: 2,
            clean_sulkberries_accused_by_fear: 1,
            divinographer_waiting_dead_gods: 1,
            neme_hostages_roots_under_stone: 1,
            ulvarex_project_applause: 0,
            wound_is_boredom: -2,
            city_heard_you_without_gun: 2,
            story_someone_survives_to_revise: 2,
            city_of_smaller_cities_consent: 2,
            redmass_given_freely_sings: 2,
            poem_noise_they_leave_humming: 2,
            truth_needs_no_hostage: 2,
            brine_ink_dries_into_salt: 1,
            neme_living_poem_releases: 1,
            surrender_before_they_see_fear: 0,
            demands_blood_yours: -3,
        };

        return scores[choiceKey] || 0;
    }

    resolvePoetryBattle() {
        const battle = this.registry.get('townhallPoetryBattle') || { score: 0 };
        return battle.score >= 4 ? 'poet_victory' : 'poet_defeat';
    }

    completePoetStandoff() {
        if (this.hasJournalEntry('townhall_poet_resolved')) return;

        this.addJournalEntry(
            'townhall_poet_resolved',
            'Defeated the Mad Poet',
            'I defeated the mad poet in a poetry battle inside the Townhall. The hostages were released safely, and the Townhall can begin functioning again.',
            this.journalSystem.categories.EVENTS,
            { location: 'Townhall' }
        );

        if (this.questSystem?.getQuest('townhall_poet_standoff')) {
            this.questSystem.updateQuest(
                'townhall_poet_standoff',
                'I defeated the mad poet in a poetry battle. The hostages are free, and the Townhall can begin functioning again.',
                'poet_defeated'
            );
            this.questSystem.completeQuest('townhall_poet_standoff');
        }

        this.modifyGrowthDecay(1, 1);
        this.showNotification('Hostages freed');
        this.refreshTownhallAfterPoet();
    }

    completeTownhallBishopRecordsCheck() {
        if (this.hasJournalEntry('townhall_bishop_records_checked')) return;

        this.addJournalEntry(
            'townhall_bishop_records_checked',
            'Townhall Records: The Bishop\'s Notebook',
            'The freed Townhall clerk checked the Bishop\'s records after the hostage standoff. The doppelgänger memo was not a filed Townhall report; it was a personal note written in an Official Townhall Report Notebook the Bishop checked out shortly before her death.',
            this.journalSystem.categories.EVENTS,
            { location: 'Townhall', character: 'Bishop', related: 'Doppelgänger' }
        );

        if (this.questSystem?.getQuest('who_killed_bishop')) {
            this.questSystem.updateQuest(
                'who_killed_bishop',
                'The Townhall clerk revealed that the Bishop\'s doppelgänger memo was not an official report, but a personal note written in an Official Townhall Report Notebook she checked out shortly before her death.',
                'townhall_notebook_revelation'
            );
        }

        // "Never returned" is only said in clerk_bishop_notebook_hook / clerk_bishop_records_summary —
        // see markNotebookNotReturned().
        if (!this.questSystem?.getQuest('find_bishop_notebook')) {
            this.questSystem.addQuest(
                'find_bishop_notebook',
                'Find the Bishop\'s Notebook',
                'The Bishop wrote her doppelgänger note in an Official Townhall Report Notebook she checked out shortly before her death. Only the torn page from her sleeve has turned up; the rest of the notebook must be somewhere. I should find it to learn what happened in her final days.'
            );
        }
    }

    markNotebookNotReturned() {
        const q = this.questSystem?.getQuest('find_bishop_notebook');
        if (q && !q.isComplete) {
            this.questSystem.updateQuest('find_bishop_notebook', 'According to the clerk, the notebook was never returned to the Townhall.', 'notebook_not_returned');
        }
    }

    refreshTownhallAfterPoet() {
        if (this.poet) {
            this.poet.destroy();
            this.poet = null;
        }

        this.hostages.forEach(hostage => hostage.destroy());
        this.hostages = [];

        if (!this.clerk) this.createFreedClerkCharacter();
        if (!this.complaintEater) this.createComplaintEaterCharacter();
        if (!this.councilor) this.createCouncilorCharacter();
    }

    grantGodgraveyardAccess() {
        if (this.hasJournalEntry('godgraveyard_access_granted')) return;

        this.addJournalEntry(
            'godgraveyard_access_granted',
            'Access to the Godgraveyard',
            'Councilor Seraphel Dune rewarded the peaceful end of the Townhall hostage crisis by granting access to the Godgraveyard level beneath the Townhall.',
            this.journalSystem.categories.EVENTS,
            { location: 'Townhall', character: 'Councilor Seraphel Dune', related: 'Godgraveyard' }
        );
        // Dune names Phor's petition only if the player took it on (also added when telling Phor).
        if (this.questSystem?.getQuest('excavation_permit')) {
            this.addJournalFact('godgraveyard_access_granted', 'phor', "Phor Calesta can now begin his divinography expedition there.");
        }

        if (!this.hasItem('godgraveyard-access-permit')) {
            this.addItemToInventory({
                id: 'godgraveyard-access-permit',
                name: 'Godgraveyard Access Permit',
                description: 'Councilor Seraphel Dune\'s sealed order granting access to the Godgraveyard beneath the Townhall.',
                count: 1
            });
        }

        if (this.questSystem?.getQuest('excavation_permit') && !this.questSystem.getQuest('excavation_permit').isComplete) {
            this.questSystem.updateQuest(
                'excavation_permit',
                'Councilor Seraphel Dune granted access to the Godgraveyard level beneath the Townhall as thanks for resolving the hostage crisis. Phor Calesta finally has the permit needed for divinography work.',
                'godgraveyard_access_granted'
            );
            this.questSystem.completeQuest('excavation_permit');
        }

        this.showNotification('Godgraveyard access granted');
    }

    showPoetryGameOver() {
        this.hideDialog();

        const overlay = this.add.rectangle(this.scale.width / 2, this.scale.height / 2, this.scale.width, this.scale.height, 0x050000, 0.95);
        overlay.setDepth(5000);

        const title = this.add.text(400, 210, 'GAME OVER', {
            fontSize: '48px',
            fill: '#ff4d4d',
            stroke: '#000000',
            strokeThickness: 6
        }).setOrigin(0.5).setDepth(5001);

        const body = this.add.text(400, 300, 'The poetry battle is lost.\nThe Townhall remembers the line badly.', {
            fontSize: '22px',
            fill: '#f8d7da',
            align: 'center',
            wordWrap: { width: 620 }
        }).setOrigin(0.5).setDepth(5001);

        const buttonBg = this.add.rectangle(400, 405, 260, 50, 0x3b0f0f, 1);
        buttonBg.setStrokeStyle(2, 0xff4d4d);
        buttonBg.setDepth(5001);
        buttonBg.setInteractive({ useHandCursor: true });

        const buttonText = this.add.text(400, 405, 'Return to Main Menu', {
            fontSize: '18px',
            fill: '#ffffff'
        }).setOrigin(0.5).setDepth(5002);

        buttonBg.on('pointerdown', () => returnToMainMenu(this));

        this.tweens.add({
            targets: [title, body, buttonBg, buttonText],
            alpha: { from: 0.65, to: 1 },
            duration: 1000,
            yoyo: true,
            repeat: -1
        });
    }

    update() {
        super.update();
    }
}

if (typeof window !== 'undefined') {
    window.TownhallInteriorScene = TownhallInteriorScene;
}

export { TownhallInteriorScene };
