import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class TownhallInteriorScene extends GameScene {
    constructor() {
        super({ key: 'TownhallInteriorScene' });
        this.isTransitioning = false;
        this.poet = null;
        this.hostages = [];
        this.clerk = null;
    }

    get dialogContent() {
        const poetResolved = !!this.hasJournalEntry('townhall_poet_resolved');
        const hasQuestUpdate = (questId, updateKey) => !!this.questSystem?.getQuest(questId)?.updates?.some(update => update.key === updateKey);
        const isQuestComplete = (questId) => !!this.questSystem?.getQuest(questId)?.isComplete;
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

        return {
            ...super.dialogContent,

            poet_start: {
                speaker: poetResolved ? 'Freed Clerk' : 'The Mad Poet',
                textKey: poetStartTextKey,
                text: poetResolved
                    ? `"The poet is gone. The hostages are safe. The Townhall is still shaking, but at least now it is shaking bureaucratically."`
                    : `A thin, ink-stained figure stands on the public reading dais, one hand clutching a long paper-knife, the other waving a sheaf of bleeding-edged poems. Three clerks sit rigidly beneath the seal of the Townhall.

"No one leaves until the city hears me correctly," the poet declares. "Not politely. Not bureaucratically. Correctly."`,
                options: [
                    ...(poetResolved ? [{ text: "What happens now?", key: 'what_happens_now', next: "clerk_after_poet" }] : []),
                    ...(!poetResolved ? [{ text: "Challenge him to a poetry battle.", key: 'challenge_him_to_a_poetry_battle', next: "poet_challenge" }] : []),
                    ...(!poetResolved ? [{ text: "Ask what he wants.", key: 'ask_what_he_wants', next: "poet_demands" }] : []),
                    ...(!poetResolved && hasBrine ? [{ text: "[Brine Scripture] Read the salt memory of the room.", key: 'brine_scripture_read_the_salt_memory', next: "poet_brine_read" }] : []),
                ]
            },

            poet_demands: {
                speaker: 'The Mad Poet',
                text: `"Wants? Wants are prose. I require witness. The clerks stamped my chapbook 'insufficiently civic.' They called my enjambment a zoning violation.

So now the public receives a reading. Every stanza. Every footnote. Every hostage-held breath."`,
                options: [
                    { text: "Then I'll answer in verse.", key: 'then_ill_answer_in_verse', next: "poet_challenge" },
                    { text: "I need a moment.", key: 'i_need_a_moment', next: "closeDialog" },
                ]
            },

            poet_brine_read: {
                speaker: 'Brine Scripture',
                text: `Salt wakes under your tongue. The floor remembers shoes grinding in panic, spilled ink drying into little black reefs, and one line repeated until it became a wound: "The city has no ear for me."

The Brine Scripture offers memory, not victory. It gives you material. You still need to make it sing.`,
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
                text: `"A challenger? Good. At last, the room develops a pulse. Three rounds. Image, wound, verdict. Bring me the city as you have lived it.

If your poem is alive, I release them. If it is dead, then we all learn what bad art costs."`,
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

The poet raises the paper-knife again, but uncertainty has entered his meter.

"End it," he whispers. "Tell me what the poem demands."`,
                hideCloseOption: true,
                options: [
                    { text: "The city has heard you. Now let it answer without your knife.", key: 'city_heard_you_without_knife', next: "poet_judgment" },
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
                text: `The paper-knife clatters onto the dais.

"Fine," the poet says, suddenly very tired. "The room has heard enough of me. Perhaps that is what I wanted. Perhaps that is what I feared."

He gathers his pages and walks out between the freed clerks, leaving only ink, sweat, and a silence that belongs to everyone.`,
                options: [
                    { text: "Check on the clerks.", key: 'check_on_the_clerks', next: "clerk_after_poet" },
                ],
                onTrigger: (option) => {
                    if (option) return 'clerk_after_poet';
                    this.completePoetStandoff();
                }
            },

            poet_defeat: {
                speaker: 'The Mad Poet',
                text: `The poet listens to your last line and smiles with terrible relief.

"Dead art," he says. "At last, honesty."

The paper-knife rises. The hostages scream. The reading becomes history in the worst possible meter.`,
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
                text: `"Thank you. The official minutes will call this a 'lyrical disruption with hostage characteristics.' That sounds less embarrassing than the truth.

The records office is still a mess, but the Townhall can breathe again."`,
                options: [
                    { text: "I need Townhall records.", key: 'i_need_townhall_records', next: "clerk_records_not_ready" },
                ]
            },

            clerk_records_not_ready: {
                speaker: 'Freed Clerk',
                text: `"Of course. Everyone does, once someone has waved a knife at us over meter. Give us a moment to unlock the archive cabinets and stop trembling in triplicate."`,
                options: [
                    { text: "I'll come back shortly.", key: 'ill_come_back_shortly', next: "closeDialog" },
                ]
            },
        };
    }

    preload() {
        super.preload();
        this.load.image('townhallInteriorBg', 'assets/images/backgrounds/townhall_interior.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
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
        this.startPoetStandoffQuestIfNeeded();
        this.createTownhallPlaceholders();

        this.cameras.main.fadeIn(800, 0, 0, 0);
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
        if (this.hasJournalEntry('townhall_poet_resolved')) return;

        if (!this.questSystem?.getQuest('townhall_poet_standoff')) {
            this.questSystem.addQuest(
                'townhall_poet_standoff',
                'The Mad Poet Standoff',
                'A mad poet has seized the Townhall reading chamber and is holding clerks hostage until the public properly hears his work. This cannot be solved with ordinary force; I need to defeat him in a poetry battle.'
            );
        }

        if (!this.hasJournalEntry('townhall_poet_standoff')) {
            this.addJournalEntry(
                'townhall_poet_standoff',
                'The Mad Poet Standoff',
                'Inside the Townhall, a mad poet is holding clerks hostage for a public reading. He seems obsessed with being truly heard. A poetry battle may be the only safe way to end this.',
                this.journalSystem.categories.EVENTS,
                { location: 'Townhall' }
            );
        }
    }

    createTownhallPlaceholders() {
        if (this.hasJournalEntry('townhall_poet_resolved')) {
            this.createFreedClerkPlaceholder();
            return;
        }

        this.createHostagePlaceholders();
        this.createPoetPlaceholder();
    }

    createPoetPlaceholder() {
        this.poet = this.add.container(400, 255);
        this.poet.setDepth(6);

        const body = this.add.rectangle(0, 30, 54, 96, 0x3b2444, 0.95);
        body.setStrokeStyle(2, 0xe6c25c);
        const head = this.add.circle(0, -30, 25, 0xd9c2a3, 1);
        head.setStrokeStyle(2, 0x3b2444);
        const knife = this.add.rectangle(42, 6, 10, 74, 0xd8d8d8, 1);
        knife.setAngle(-20);
        const papers = this.add.rectangle(-42, 10, 34, 48, 0xf2ead0, 1);
        papers.setStrokeStyle(2, 0x5c3a2e);
        const label = this.add.text(0, 92, 'MAD POET', {
            fontSize: '14px',
            fill: '#ffdf7a',
            stroke: '#000000',
            strokeThickness: 3
        }).setOrigin(0.5);

        this.poet.add([body, head, knife, papers, label]);
        this.poet.setSize(120, 150);
        this.poet.setInteractive(new Phaser.Geom.Rectangle(-60, -55, 120, 150), Phaser.Geom.Rectangle.Contains);

        this.poet.on('pointerover', () => {
            this.poet.setScale(1.04);
            document.body.style.cursor = 'pointer';
        });
        this.poet.on('pointerout', () => {
            this.poet.setScale(1);
            document.body.style.cursor = 'default';
        });
        this.poet.on('pointerdown', () => {
            if (this.clickSound) this.clickSound.play();
            this.showDialog('poet_start');
        });

        this.tweens.add({
            targets: papers,
            angle: { from: -4, to: 4 },
            duration: 900,
            yoyo: true,
            repeat: -1
        });
    }

    createHostagePlaceholders() {
        const positions = [
            { x: 300, y: 390, label: 'CLERK' },
            { x: 400, y: 405, label: 'CLERK' },
            { x: 500, y: 390, label: 'CLERK' },
        ];

        this.hostages = positions.map(pos => {
            const hostage = this.add.container(pos.x, pos.y);
            hostage.setDepth(5);

            const body = this.add.rectangle(0, 20, 42, 70, 0x5d6f8f, 0.9);
            body.setStrokeStyle(2, 0x111827);
            const head = this.add.circle(0, -25, 19, 0xcfae8a, 1);
            const label = this.add.text(0, 68, pos.label, {
                fontSize: '12px',
                fill: '#ffffff',
                stroke: '#000000',
                strokeThickness: 3
            }).setOrigin(0.5);

            hostage.add([body, head, label]);

            this.tweens.add({
                targets: hostage,
                x: pos.x + 3,
                duration: 110,
                yoyo: true,
                repeat: -1,
                repeatDelay: 900
            });

            return hostage;
        });
    }

    createFreedClerkPlaceholder() {
        this.clerk = this.add.container(430, 385);
        this.clerk.setDepth(5);

        const body = this.add.rectangle(0, 20, 48, 78, 0x4f7b64, 0.95);
        body.setStrokeStyle(2, 0xd1fae5);
        const head = this.add.circle(0, -28, 21, 0xcfae8a, 1);
        const label = this.add.text(0, 76, 'FREED CLERK', {
            fontSize: '13px',
            fill: '#d1fae5',
            stroke: '#000000',
            strokeThickness: 3
        }).setOrigin(0.5);

        this.clerk.add([body, head, label]);
        this.clerk.setSize(110, 130);
        this.clerk.setInteractive(new Phaser.Geom.Rectangle(-55, -50, 110, 130), Phaser.Geom.Rectangle.Contains);
        this.clerk.on('pointerover', () => {
            this.clerk.setScale(1.04);
            document.body.style.cursor = 'pointer';
        });
        this.clerk.on('pointerout', () => {
            this.clerk.setScale(1);
            document.body.style.cursor = 'default';
        });
        this.clerk.on('pointerdown', () => {
            if (this.clickSound) this.clickSound.play();
            this.showDialog('clerk_after_poet');
        });
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
            bishop_met_herself_breathless: `The poet's knife lowers by the width of a comma.\n\n"A self before the self arrives —\na mirror learning how one dies.\nAn image, then. Not merely decoration. A tooth-mark."`,
            egg_cathedral_hatching_scripture: `He touches the page to his forehead.\n\n"Shell-script, yolk-prayer, unborn nave —\nfaiths keep watch around a grave.\nGood. You have seen architecture trying to become a verdict."`,
            skyship_refusing_to_land: `He glances toward the ceiling as if the skyship might be listening.\n\n"A thought in rigging, cloud in chain —\nthe sky says yes, the city: remain.\nAn image with altitude. Continue."`,
            citizen_made_of_tiny_cities: `For one dangerous second, the poet smiles.\n\n"A million roofs in borrowed skin,\na crowd that says: I am one citizen.\nYes. Embarrassment is civic mortar."`,
            punk_chord_dead_god_keeps_time: `A hostage flinches as the poet taps a rhythm with the paper-knife.\n\n"Dead god, live amp, impossible beat —\nthe buried divine still moves its feet.\nThat image has teeth and volume."`,
            prophetic_toad_three_minutes_ahead: `He snorts despite himself.\n\n"A toad ahead of the auction bell —\nthree minutes of heaven in a jar of smell.\nComic, but alive. I accept the bite."`,
            thorne_refuses_the_garden: `The poet squints at the air around you.\n\n"A thorn outside the gardener's plan\nstill writes the hedge in the blood of a hand.\nUseful. Not enough alone, but useful."`,
            locked_townhall_digesting_citizens: `His pages tremble.\n\n"A door with offices for teeth,\na public stomach underneath.\nYes. This building deserved that."`,
            your_poem_is_bad_and_hat_worse: `The poet goes very still.\n\n"Hat? Hat?\nA fool mistakes the scalp for crown,\nand wonders why the line falls down.\nInsult is not image. It is failed weather."`,

            dream_device_bruised_the_dead: `The poet's voice drops until even the clerks lean in.\n\n"Dream loops. Temple bruises. Mercy redacts the bed.\nA program chews the sleeper and returns the sleeper dead.\nThat wound is real."`,
            redmass_begging_not_proof: `The paper-knife wavers.\n\n"Loyalty fed from another's scream\nis rust pretending it had a dream.\nYou name the wound without polishing it."`,
            rust_choir_machines_hum: `He answers in a hoarse half-song.\n\n"Empires forget. Engines repeat.\nIron keeps the last honest beat.\nThe wound hums. I hear it."`,
            shed_forms_amputate: `One clerk laughs once, then looks horrified at themselves.\n\n"Form seventeen, annex three: remove the hand that signs to be free.\nBureaucracy as blade. Good. Cruel and exact."`,
            misutkenn_writer_festival_fire: `The poet looks ashamed before he can hide it.\n\n"Bear-skin bonfire, author-heart —\nwhat they burned became his art.\nA wound that asks for a book instead of revenge."`,
            clean_sulkberries_accused_by_fear: `He grimaces as if tasting something medicinal.\n\n"Clean fruit in a guilty bowl —\nfear salts whatever it cannot control.\nA smaller wound, but a true one."`,
            divinographer_waiting_dead_gods: `Dust seems to settle over the dais.\n\n"Dead gods below, live stamps above —\nthe permit denies the fossil love.\nYes. The city can wound even its archaeologists."`,
            neme_hostages_roots_under_stone: `The poet hears the clerks breathing together.\n\n"Roots under stone do not cease to grow;\nthey carry the dark where the leaves cannot go.\nYour symbiont sees the room. You still had to say it."`,
            ulvarex_project_applause: `For a moment, phantom applause trembles in the room. The poet's eyes harden.\n\n"Borrowed hands make borrowed praise;\nmirrors cannot end hostage days.\nPretty. Too pretty."`,
            wound_is_boredom: `The poet smiles with terrible relief.\n\n"Boredom, says the empty cup,\nthen wonders why no one fills it up.\nYou have named your impatience, not the wound."`,

            city_heard_you_without_knife: `The poet lifts the paper-knife, then hears the weakness in that gesture.\n\n"If hearing must be held at blade,\nthe poem was already afraid.\nThe line lands cleanly. Now we see if it holds."`,
            story_someone_survives_to_revise: `He looks at his pages as if they have betrayed him by remaining editable.\n\n"A draft that kills its reader dies;\na living text survives replies.\nA generous verdict. Dangerous."`,
            city_of_smaller_cities_consent: `His expression fractures into attention.\n\n"Even one body may be a town;\nconsent is what keeps walls from falling down.\nYou bring civic theology to a knife fight. Good."`,
            redmass_given_freely_sings: `The knife sinks toward his side.\n\n"Torn metal screams and stains the hand;\ngiven metal joins the band.\nYou understand release."`,
            poem_noise_they_leave_humming: `Somewhere in the walls, pipes vibrate like a distant amplifier.\n\n"A song is proved by open doors,\nnot bodies counted on the floors.\nI hate how nearly beautiful that is."`,
            truth_needs_no_hostage: `He swallows. The clerks hear it.\n\n"Truth in chains becomes a lie;\nrelease the breath, or watch it die.\nA verdict with a spine."`,
            brine_ink_dries_into_salt: `Salt stings behind your teeth. The poet hears something older than flattery.\n\n"Ink to salt and hurt to shore —\nkeep the wound, but lock no door.\nMemory helps you. It does not replace you."`,
            neme_living_poem_releases: `Neme's presence opens like a green hush beneath your words.\n\n"A root that grips until roots break\nmust learn what living things forsake.\nA symbiont's wisdom, carried by your mouth."`,
            surrender_before_they_see_fear: `The poet's shame curdles into pride.\n\n"Name me coward, call it art —\nyou miss the wound and strike the heart.\nPerhaps true. Not useful."`,
            demands_blood_yours: `The poet's face becomes calm in the worst possible way.\n\n"Blood is the cheapest crimson word;\nevery butcher thinks himself heard.\nYou have mistaken violence for ending."`,
        };

        return responses[choiceKey] || this.getDefaultPoetryResponseText(round);
    }

    getDefaultPoetryResponseText(round) {
        const defaults = {
            round_one: `The poet's knife lowers by the width of a comma.\n\n"An image, then. Not merely decoration. A tooth-mark. Continue."`,
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
            city_heard_you_without_knife: 2,
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

    refreshTownhallAfterPoet() {
        if (this.poet) {
            this.poet.destroy();
            this.poet = null;
        }

        this.hostages.forEach(hostage => hostage.destroy());
        this.hostages = [];

        if (!this.clerk) {
            this.createFreedClerkPlaceholder();
        }
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
