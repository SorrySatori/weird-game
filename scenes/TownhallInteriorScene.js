import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

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

        return {
            ...super.dialogContent,

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
                ]
            },

            poet_intro_interrupt: {
                speaker: 'Townhall Clerk',
                hideCloseOption: true,
                text: `The clerk on the floor cracks first. The words spill out before fear can swallow them:

"Please — it's been three hours. My daughter is waiting at the registry window downstairs. She's six. She doesn't know how to—"

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

"This is the strange part. There is no official incident report under the Bishop's name. No filed doppelgänger complaint. No follow-up. What exists is a stationery issue record: she requested an Official Townhall Report Notebook three days before she died. I stamped it myself.

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
                ]
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
                ]
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
                ]
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
        };
    }

    preload() {
        super.preload();
        this.load.image('townhallInteriorBg', 'assets/images/backgrounds/townhall_interior.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        this.load.image('townhallPoet', 'assets/images/characters/poet.png');
        this.load.image('townhallClerk', 'assets/images/characters/townhall_clerk.png');
        this.load.image('complaintEater', 'assets/images/characters/complaint_eater.png');
        this.load.image('councilorSeraphelDune', 'assets/images/characters/councilor_seraphel_dune.png');
    }

    create() {
        super.create();
        this.playSceneMusic('genericMusic');

        const bg = this.add.image(400, 300, 'townhallInteriorBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

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

        this.priest.x = 400;
        this.priest.y = 520;

        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        this.completeEnterTownhallQuestOnFirstEntry();
        const firstPoetEntry = this.startPoetStandoffQuestIfNeeded();
        this.createTownhallPlaceholders();

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
            'I made it inside the Townhall. Now I can search the records for the Bishop\'s doppelgänger report and help Phor Calesta with his permits.',
            this.journalSystem.categories.EVENTS,
            { location: 'Townhall' }
        );

        this.questSystem.updateQuest(
            'enter_townhall',
            'I made it inside the Townhall. The locked-door problem is solved; now I can search the records inside.',
            'entered_townhall'
        );
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
        this.poet = this.createCharacterNpc({
            x: 400,
            y: 430,
            texture: 'townhallPoet',
            label: 'POET',
            dialog: 'poet_start',
            scale: 0.13,
            depth: 6,
            labelColor: '#ffdf7a'
        });
    }

    createHostageCharacters() {
        const positions = [
            { x: 170, y: 470, label: 'TOWNHALL CLERK', texture: 'townhallClerk', scale: 0.08, labelColor: '#ffffff' },
            { x: 620, y: 470, label: 'COMPLAINT EATER', texture: 'complaintEater', scale: 0.085, labelColor: '#d6bcff' },
            { x: 715, y: 450, label: 'SERAPHEL DUNE', texture: 'councilorSeraphelDune', scale: 0.09, labelColor: '#ffdf7a' },
        ];

        this.hostages = positions.map(pos =>
            this.createCharacterNpc({
                x: pos.x,
                y: pos.y,
                texture: pos.texture,
                label: pos.label,
                dialog: 'poet_start',
                scale: pos.scale,
                depth: 5,
                labelColor: pos.labelColor
            })
        );
    }

    createFreedClerkCharacter() {
        this.clerk = this.createCharacterNpc({
            x: 170,
            y: 470,
            texture: 'townhallClerk',
            label: 'TOWNHALL CLERK',
            dialog: 'clerk_after_poet',
            scale: 0.08,
            depth: 5,
            labelColor: '#d1fae5'
        });
    }

    createComplaintEaterCharacter() {
        this.complaintEater = this.createCharacterNpc({
            x: 620,
            y: 470,
            texture: 'complaintEater',
            label: 'COMPLAINT EATER',
            dialog: 'complaint_eater_start',
            scale: 0.085,
            depth: 5,
            labelColor: '#d6bcff'
        });
    }

    createCouncilorCharacter() {
        this.councilor = this.createCharacterNpc({
            x: 715,
            y: 450,
            texture: 'councilorSeraphelDune',
            label: 'SERAPHEL DUNE',
            dialog: 'councilor_start',
            scale: 0.09,
            depth: 5,
            labelColor: '#ffdf7a'
        });
    }

    createCharacterNpc({ x, y, texture, label, dialog, scale = 0.1, depth = 5, labelColor = '#ffffff' }) {
        const container = this.add.container(x, y);
        container.setDepth(depth);

        const sprite = this.add.image(0, 0, texture).setOrigin(0.5, 1).setScale(scale);

        container.add(sprite);

        const width = sprite.displayWidth + 12;
        const height = sprite.displayHeight + 12;
        container.setSize(width, height);
        container.setInteractive(new Phaser.Geom.Rectangle(-width / 2, -sprite.displayHeight - 6, width, height), Phaser.Geom.Rectangle.Contains);

        container.on('pointerover', () => {
            container.setScale(1.04);
            document.body.style.cursor = 'pointer';
        });
        container.on('pointerout', () => {
            container.setScale(1);
            document.body.style.cursor = 'default';
        });
        container.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog(dialog);
        });

        return container;
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
            'The freed Townhall clerk checked the Bishop\'s records after the hostage standoff. The doppelgänger memo was not a filed Townhall report; it was a personal note written in an Official Townhall Report Notebook the Bishop checked out shortly before her death. The rest of that notebook was never returned and may contain more about the doppelgänger, the changing spores, and why she sealed the Cathedral.',
            this.journalSystem.categories.EVENTS,
            { location: 'Townhall', character: 'Bishop', related: 'Doppelgänger' }
        );

        if (this.questSystem?.getQuest('who_killed_bishop')) {
            this.questSystem.updateQuest(
                'who_killed_bishop',
                'The Townhall clerk revealed that the Bishop\'s doppelgänger memo was not an official report. It was a personal note written in an Official Townhall Report Notebook she checked out shortly before death. The missing notebook is now the strongest lead.',
                'townhall_notebook_revelation'
            );
        }

        if (!this.questSystem?.getQuest('find_bishop_notebook')) {
            this.questSystem.addQuest(
                'find_bishop_notebook',
                'Find the Bishop\'s Notebook',
                'The Bishop used an Official Townhall Report Notebook as a private diary. A torn page about her doppelgänger survived, but the rest of the notebook was never returned to the Townhall. I should find it to learn what happened in her final days.'
            );
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
            'Councilor Seraphel Dune rewarded the peaceful end of the Townhall hostage crisis by granting access to the Godgraveyard level beneath the Townhall. Phor Calesta can now begin the divinography expedition there.',
            this.journalSystem.categories.EVENTS,
            { location: 'Townhall', character: 'Councilor Seraphel Dune', related: 'Godgraveyard' }
        );

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

        const overlay = this.add.rectangle(400, 300, 800, 600, 0x050000, 0.95);
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

        buttonBg.on('pointerdown', () => {
            this.sound.stopAll();
            this.scene.start('MainScene');
        });

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
