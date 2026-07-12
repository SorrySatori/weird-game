import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class LumenDirectorateInteriorScene extends GameScene {
    constructor() {
        super({ key: 'LumenDirectorateInteriorScene' });
        this.isTransitioning = false;
    }

    preload() {
        super.preload();
        this.load.image('lumenInteriorBg', 'assets/images/backgrounds/LumenDirectorateInterior.png');
        this.load.image('angleCorrector', 'assets/images/characters/AngleCorrector.png');
        this.load.image('seldo', 'assets/images/characters/seldo.png');
    }

    create() {
        super.create();
        this.playSceneMusic('genericMusic');

        const bg = this.add.image(400, 300, 'lumenInteriorBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);

        this.transitionManager = new SceneTransitionManager(this);

        // Exit back to Lumen Directorate exterior
        this.transitionManager.createTransitionZone(
            400,
            550,
            200,
            50,
            'down',
            'LumenDirectorateScene',
            400,
            350,
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
            this.showNotification('Lumen Directorate — Interior', 0x556B2F);
        });

        // Create the Angle Corrector NPC
        this.createAngleCorrector();

        // Create Seldo Thrice-Corrected NPC
        this.createSeldo();
    }

    createAngleCorrector() {
        this.angleCorrector = this.add.image(600, 320, 'angleCorrector');
        this.angleCorrector.setScale(0.18);
        this.angleCorrector.setDepth(5);
        this.angleCorrector.setInteractive({ useHandCursor: true });

        // Olive-green glow effect
        this.angleCorrectorGlow = this.add.graphics();
        this.angleCorrectorGlow.fillStyle(0x556B2F, 0.15);
        this.angleCorrectorGlow.fillCircle(600, 320, 45);
        this.angleCorrectorGlow.setDepth(4);

        this.tweens.add({
            targets: this.angleCorrectorGlow,
            alpha: { from: 0.15, to: 0.04 },
            duration: 2500,
            yoyo: true,
            repeat: -1
        });

        // Subtle idle sway
        this.tweens.add({
            targets: this.angleCorrector,
            angle: { from: -0.8, to: 0.8 },
            duration: 3000,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });

        // Hover effect
        this.angleCorrector.on('pointerover', () => {
            this.angleCorrector.setScale(0.19);
            document.body.style.cursor = 'pointer';
        });

        this.angleCorrector.on('pointerout', () => {
            this.angleCorrector.setScale(0.18);
            document.body.style.cursor = 'default';
        });

        // Click to talk
        this.angleCorrector.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog('ac_start');
        });
    }

    createSeldo() {
        this.seldo = this.add.image(200, 340, 'seldo');
        this.seldo.setScale(0.16);
        this.seldo.setDepth(5);
        this.seldo.setInteractive({ useHandCursor: true });

        // Amber bureaucratic glow
        this.seldoGlow = this.add.graphics();
        this.seldoGlow.fillStyle(0xC4A035, 0.12);
        this.seldoGlow.fillCircle(200, 340, 40);
        this.seldoGlow.setDepth(4);

        this.tweens.add({
            targets: this.seldoGlow,
            alpha: { from: 0.12, to: 0.03 },
            duration: 2800,
            yoyo: true,
            repeat: -1
        });

        // Subtle idle sway
        this.tweens.add({
            targets: this.seldo,
            angle: { from: -0.6, to: 0.6 },
            duration: 3500,
            ease: 'Sine.easeInOut',
            yoyo: true,
            repeat: -1
        });

        // Hover effect
        this.seldo.on('pointerover', () => {
            this.seldo.setScale(0.17);
            document.body.style.cursor = 'pointer';
        });

        this.seldo.on('pointerout', () => {
            this.seldo.setScale(0.16);
            document.body.style.cursor = 'default';
        });

        // Click to talk
        this.seldo.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.showDialog('seldo_start');
        });
    }

    get dialogContent() {
        const hasLumenQuest = !!(this.questSystem?.getQuest('find_lumen_directorate') && !this.questSystem.getQuest('find_lumen_directorate').isComplete);
        const hasBishopQuest = !!(this.questSystem?.getQuest('who_killed_bishop') && !this.questSystem.getQuest('who_killed_bishop').isComplete);
        const hasEnterTownhallQuest = !!(this.questSystem?.getQuest('enter_townhall') && !this.questSystem.getQuest('enter_townhall').isComplete);
        const knowsSulkberries = !!this.hasJournalEntry('bishop_berries');
        const knowsLumenLead = !!this.hasJournalEntry('elphi_lumen_lead');
        const knowsBishopVisits = !!this.hasJournalEntry('gardener_bishop_visits');
        const metAngleCorrector = !!this.hasJournalEntry('met_angle_corrector');
        const passedGrowthTest = !!this.hasJournalEntry('ac_growth_test_passed');
        const knowsSulkberryRecords = !!this.hasJournalEntry('ac_sulkberry_records');

        // Seldo conditions
        const metSeldo = !!this.hasJournalEntry('met_seldo');
        const acceptedAuctionErrand = !!this.hasJournalEntry('seldo_auction_errand');
        const auctionComplete = !!this.hasJournalEntry('seldo_auction_success');
        const hasTownhallKey = !!this.hasJournalEntry('seldo_townhall_key');
        const hasToadlet = !!this.hasItem('chrono-slurry-toadlet');
        const seldoStartTextKey = hasTownhallKey
            ? 'seldo_start_key_given'
            : (metSeldo
                ? (auctionComplete
                    ? (hasToadlet ? 'seldo_start_toadlet_ready' : 'seldo_start_auction_complete')
                    : (acceptedAuctionErrand ? 'seldo_start_auction_pending' : 'seldo_start_met'))
                : 'seldo_start_first');

        const lumenRep = this.factionSystem?.getReputation('LumenDirectorate') || 0;
        const hasThorne = !!this.symbiontSystem?.hasSymbiont('thorne-still');
        const hasNeme = !!this.symbiontSystem?.hasSymbiont('neme-crownmire');
        const growth = this.growthDecaySystem?.getGrowth() || 50;
        const decay = this.growthDecaySystem?.getDecay() || 50;

        // Lumen membership via sabotaging the Rust Choir.
        const joinedLumen = !!this.hasJournalEntry('lumen_directorate_joined');
        const machinesDestroyed = !!this.hasJournalEntry('rust_choir_machines_destroyed');
        const sabotageQuest = this.questSystem?.getQuest('join_lumen_directorate');
        const hasSabotageQuest = !!(sabotageQuest && !sabotageQuest.isComplete);
        const rustMember = !!(this.hasJournalEntry('rust_choir_joined') && !machinesDestroyed);
        const warnedRustOfLumen = !!this.hasJournalEntry('rust_choir_warned_of_lumen');
        // Directorate Clearance perk: archive reveal (currently surfaces the vestigel-buyer lead).
        const vestigelQuest = this.questSystem?.getQuest('the_three_vestigels');
        const canRevealEskola = !!(joinedLumen && vestigelQuest && !vestigelQuest.isComplete && !vestigelQuest.updates?.some(u => u.key === 'found_eskola_lead'));

        return {
            ...super.dialogContent,

            // --- Entry point ---
            ac_start: {
                speaker: 'The Angle Corrector',
                moodNpc: 'angle_corrector',
                text: metAngleCorrector
                    ? (passedGrowthTest
                        ? `"You return. Good — I prefer those who come back over those who linger. What brings you to the third floor this time?"`
                        : `"Ah, you again. Still circling, still uncertain. Have you decided what growth means to you yet?"`)
                    : `"Stop. Don't come any closer until I've had a look at you.\n\n...Interesting. You carry spores — everyone does — but yours have an unusual cadence. Like a song that hasn't decided what key it's in.\n\nI am the Angle Corrector. That is my title, my name, and my function. State your business."`,
                options: [
                    ...(hasLumenQuest && !passedGrowthTest ? [{ text: "I'm here to join the Directorate.", key: 'captain_liris_sent_me_im_here_to_join_the_director', next: "ac_liris_recruit" }] : []),
                    ...(hasBishopQuest && (knowsLumenLead || knowsBishopVisits) ? [{ text: "I'm investigating the Bishop's death.", key: 'im_investigating_the_bishops_death', next: "ac_bishop_inquiry" }] : []),
                    ...(hasBishopQuest && knowsSulkberries && !knowsSulkberryRecords ? [{ text: "I need to ask about spiced Sulkberries.", key: 'i_need_to_ask_about_spiced_sulkberries', next: "ac_sulkberries" }] : []),
                    ...(hasEnterTownhallQuest ? [{ text: "I need help getting into the Townhall.", key: 'i_need_help_getting_into_the_townhall', next: "ac_townhall" }] : []),
                    { text: "Tell me about the Lumen Directorate.", key: 'tell_me_about_the_lumen_directorate', next: "ac_about_directorate" },
                    ...(metAngleCorrector ? [{ text: "What's happening with the Egg Cathedral?", key: 'whats_happening_with_the_egg_cathedral', next: "ac_cathedral" }] : []),
                    ...(passedGrowthTest ? [{ text: "What can I do for the Directorate?", key: 'what_can_i_do_for_the_directorate', next: "ac_assignments" }] : []),
                    ...(passedGrowthTest && !joinedLumen && !hasSabotageQuest && !machinesDestroyed && !warnedRustOfLumen ? [{ text: "I want to be more than an associate. What would full membership take?", key: 'i_want_full_membership', next: "ac_membership_offer" }] : []),
                    ...(passedGrowthTest && !joinedLumen && machinesDestroyed ? [{ text: "The Rust Choir's machines are dead. It's done.", key: 'the_rust_choirs_machines_are_dead', next: "ac_sabotage_report" }] : []),
                    ...(joinedLumen ? [{ text: "Consult the Directorate's files. (Nothing Hidden.)", key: 'consult_the_directorate_files', next: "ac_archive" }] : []),
                    ...(this.hasJournalEntry('met_infinite_fold') ? [{ text: "[Before entering the cathedral] I've met the mind in the sealed cellar. I know what's hatching.", key: 'fold_before_cathedral', next: "ac_fold_perspective" }] : []),
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('met_angle_corrector')) {
                        this.addJournalEntry(
                            'met_angle_corrector',
                            'Met the Angle Corrector',
                            'Met the enigmatic Angle Corrector on the third floor of the Lumen Directorate. Their real name is unknown — title and identity are one. They handle the Directorate\'s most sensitive affairs: cultivation oversight, Cathedral liaison, and testing recruits.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'The Angle Corrector' }
                        );
                    }
                }
            },

            // --- Liris recruitment branch ---
            ac_liris_recruit: {
                speaker: 'The Angle Corrector',
                text: `"Joining, then. They come to me one way or another — whether Captain Liris sends them from the Verdigrace or the gardener points them up the stairs. It makes no difference to me.\n\nA recommendation opens the door. It does not seat you at the table. For that, I need to understand something about you first."`,
                options: [
                    { text: "What do you need to know?", key: 'what_do_you_need_to_know', next: "ac_growth_test" },
                    { text: "I thought this was a formality.", key: 'i_thought_this_was_a_formality', next: "ac_not_formality" },
                ]
            },

            ac_not_formality: {
                speaker: 'The Angle Corrector',
                text: `"Nothing here is a formality. Formality is decay dressed in clean clothes. Every interaction in this building serves a purpose — even this one.\n\nSo. Are you ready for my question, or would you prefer to wander the atrium until the ferns claim you?"`,
                options: [
                    { text: "Ask your question.", key: 'ask_your_question', next: "ac_growth_test" },
                ]
            },

            ac_growth_test: {
                speaker: 'The Angle Corrector',
                text: `"The Directorate's foundation is growth. Not just the sprouting of seeds or the spread of mycelium — though we value those deeply. Growth as principle. Growth as philosophy.\n\nSo tell me: what does growth mean to you? And think carefully — I can smell a rehearsed answer the way my ferns smell rain."`,
                hideCloseOption: true,
                options: [
                    { text: "Growth is change — becoming something you weren't before.", key: 'growth_is_change_becoming_something_you_werent_bef', next: "ac_test_change" },
                    { text: "Growth is survival — spreading to ensure you endure.", key: 'growth_is_survival_spreading_to_ensure_you_endure', next: "ac_test_survival" },
                    ...(hasThorne ? [{ text: "I carry the Thorne-Still. I know what it means to resist growth.", key: 'i_carry_the_thornestill_i_know_what_it_means_to_re', next: "ac_test_thorne" }] : []),
                    ...(hasNeme ? [{ text: "The Neme-Crownmire taught me — growth is connection.", key: 'the_nemecrownmire_taught_me_growth_is_connection', next: "ac_test_neme" }] : []),
                    ...(growth > 65 ? [{ text: "I don't think about it. I just grow. It's what I do.", key: 'i_dont_think_about_it_i_just_grow_its_what_i_do', next: "ac_test_instinct" }] : []),
                    ...(decay > 65 ? [{ text: "Growth without decay is just accumulation. You need both.", key: 'growth_without_decay_is_just_accumulation_you_need', next: "ac_test_balance" }] : []),
                ]
            },

            ac_test_change: {
                speaker: 'The Angle Corrector',
                text: `"Change. A safe answer, but not a wrong one. Change is the minimum condition for growth — necessary but not sufficient.\n\nA rock erodes. That is change. But it is not growth. Growth requires direction. Intent. A reaching-toward.\n\nStill... you didn't say 'power' or 'conquest.' That tells me something useful about you. The Directorate accepts your answer — provisionally."`,
                options: [
                    { text: "What happens now?", key: 'what_happens_now', next: "ac_test_passed" },
                ],
            },

            ac_test_survival: {
                speaker: 'The Angle Corrector',
                text: `"Survival. The mushroom's answer — spread spores far enough and something will take root somewhere. There's pragmatism in that.\n\nThe Directorate was built on survival. After the Board Games War, when the Ludarchs consumed themselves, we grew from the wreckage. Survival first, then expansion, then purpose.\n\nYour honesty is noted. The Directorate accepts your answer."`,
                options: [
                    { text: "What happens now?", key: 'what_happens_now', next: "ac_test_passed" },
                ],
            },

            ac_test_thorne: {
                speaker: 'The Angle Corrector',
                text: `"...You carry a Thorne-Still and you walked into the headquarters of the growth faction. Either you are very brave or very foolish.\n\nBut you understand something most don't — that growth defined by its opposition is still growth. The tension between the Thorne's decay and your own living pattern creates something... dynamic.\n\nThat is a more interesting answer than most recruits give. The Directorate accepts you — and your passenger."`,
                options: [
                    { text: "You're not bothered by the symbiont?", key: 'youre_not_bothered_by_the_symbiont', next: "ac_test_passed" },
                ],
            },

            ac_test_neme: {
                speaker: 'The Angle Corrector',
                text: `"The Neme-Crownmire. A growth-aligned symbiont — and a possessive one. It has taught you well.\n\nConnection is the root system beneath the visible forest. One tree is fragile. A thousand trees networked through mycorrhiza? That is power that endures.\n\nYes. The Directorate accepts you readily. The Neme-Crownmire's chosen carriers are always welcome here."`,
                options: [
                    { text: "What happens now?", key: 'what_happens_now', next: "ac_test_passed" },
                ],
            },

            ac_test_instinct: {
                speaker: 'The Angle Corrector',
                text: `"Ha. You don't think about it, you say. And yet here you are, actively seeking to grow your connections, your influence, your understanding.\n\nInstinct is the oldest form of growth — the kind that predates philosophy. The root doesn't ask why it reaches for water. It simply reaches.\n\nThe Directorate has room for instinct. In fact, we prefer it to overthinking. Accepted."`,
                options: [
                    { text: "What happens now?", key: 'what_happens_now', next: "ac_test_passed" },
                ],
            },

            ac_test_balance: {
                speaker: 'The Angle Corrector',
                text: `"...That is not an answer the Directorate would normally welcome. We are growth. Decay is what we oppose.\n\nBut you are not wrong. The forest that never sheds its leaves suffocates itself. The Rust Choir, for all their corrosion worship, understand something about necessary endings.\n\nI will not repeat your answer to the council. But between us — I find it refreshingly honest. Accepted."`,
                options: [
                    { text: "What happens now?", key: 'what_happens_now', next: "ac_test_passed" },
                ],
            },

            ac_test_passed: {
                speaker: 'The Angle Corrector',
                text: `"Now? You are recognized by the Lumen Directorate as an associate — not a member, not yet. Membership requires time and proven dedication.\n\nBut you have access. You may move freely within these halls, consult our archives, and seek assignments from the Directorate's operatives.\n\nWelcome to the growth. Try not to wilt."`,
                options: [
                    { text: "I have questions.", key: 'i_have_questions', next: "ac_start" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('ac_growth_test_passed')) {
                        this.addJournalEntry(
                            'ac_growth_test_passed',
                            'Passed the Angle Corrector\'s Test',
                            'The Angle Corrector tested my understanding of growth — the Directorate\'s core philosophy. I have been accepted as a Directorate associate with access to their halls and assignments.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'The Angle Corrector' }
                        );
                        this.modifyFactionReputation('LumenDirectorate', 15);
                        this.showNotification('Lumen Directorate reputation increased', 0x556B2F);
                    }
                    if (this.questSystem?.getQuest('find_lumen_directorate') && !this.questSystem.getQuest('find_lumen_directorate').isComplete) {
                        this.questSystem.completeQuest('find_lumen_directorate');
                        this.showNotification('Quest complete: Find the Lumen Directorate', 0x556B2F);
                    }
                }
            },

            // --- About the Directorate ---
            ac_about_directorate: {
                speaker: 'The Angle Corrector',
                text: `"The Lumen Directorate exists to ensure that growth prevails. After the Board Games War reduced this city to ash and contradiction, we rebuilt. The Ludarchs played their games until reality couldn't hold the weight of their rules — and when the boards collapsed, it was we who planted the first new roots.\n\n'Nothing Hidden. Nothing Lost.' That is our covenant. Transparency and preservation. Everything that grows deserves to be seen, catalogued, and protected."`,
                options: [
                    { text: "What about the Rust Choir and the Pith Reclaimers?", key: 'what_about_the_rust_choir_and_the_pith_reclaimers', next: "ac_other_factions" },
                    { text: "What is your role here?", key: 'what_is_your_role_here', next: "ac_role" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ]
            },

            ac_other_factions: {
                speaker: 'The Angle Corrector',
                text: `"The Rust Choir worships entropy. They dress corrosion in sacred robes and call it 'the silence between.' Romantic nonsense — decay without purpose is just death.\n\nThe Pith Reclaimers are bureaucrats who believe they can manage chaos with enough forms and procedures. They emerged from the wreckage of the Ludarchs' administrative apparatus and never stopped filing.\n\nWe work with both when necessary. The Directorate is pragmatic above all."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ],
                onTrigger: () => { this.learnPithReclaimers(); }
            },

            ac_role: {
                speaker: 'The Angle Corrector',
                text: `"I correct angles. When the Directorate's growth bends in an unproductive direction, I straighten it. When external forces apply pressure — the Cathedral, the Choir, the Townhall — I adjust our trajectory.\n\nCultivation oversight, diplomatic liaison, recruit assessment. Every thread that requires a delicate touch passes through this office.\n\nI am, in essence, the Directorate's gardener — though Verrik downstairs would bristle at the comparison."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ]
            },

            // --- Bishop investigation ---
            ac_bishop_inquiry: {
                speaker: 'The Angle Corrector',
                text: knowsBishopVisits
                    ? `"So the gardener has been talking. Verrik means well, but he sees packages and formal visits and imagines secrets. Some of what he told you is true. Some... requires context.\n\nYes, the Bishop visited regularly. Yes, the visits stopped. What would you like to know?"`
                    : `"The Bishop's death. That's new information. How unfortunate. It is true that we knew each other. \n\n. The Bishop and I had a professional relationship — regular meetings, mutual interests. I will answer what I can, within reason."`,
                options: [
                    { text: "What was your relationship with the Bishop?", key: 'what_was_your_relationship_with_the_bishop', next: "ac_bishop_relationship" },
                    ...(knowsBishopVisits ? [{ text: "What were the packages Verrik saw?", key: 'what_were_the_packages_verrik_saw', next: "ac_bishop_packages" }] : []),
                    { text: "Why did the visits stop?", key: 'why_did_the_visits_stop', next: "ac_bishop_stopped" },
                    { text: "Do you know who killed the Bishop?", key: 'do_you_know_who_killed_the_bishop', next: "ac_bishop_killer" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ]
            },

            ac_bishop_relationship: {
                speaker: 'The Angle Corrector',
                text: `"Professional. Cordial. Occasionally tense.\n\nThe Bishop represented the Egg Cathedral's interests. The Directorate has always monitored the Cathedral — the hatching is the most significant growth event in decades, and we intended to be present when it happened.\n\nOur meetings covered Cathedral access, cultivation samples, and the theological implications of bio-growth within sacred architecture. The Bishop tolerated our interest. Sometimes she even welcomed it."`,
                options: [
                    { text: "What changed?", key: 'what_changed', next: "ac_bishop_stopped" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('who_killed_bishop', 'The Angle Corrector confirmed a professional relationship with the Bishop — regular meetings about Cathedral access and the hatching. Something changed when the Cathedral was sealed.', 'ac_bishop_relationship');
                }
            },

            ac_bishop_packages: {
                speaker: 'The Angle Corrector',
                text: `"The packages were spiced Sulkberries. Premium cultivation — very specific alkaloid profiles. The Bishop ordered them regularly.\n\nThey are used in dream immersion rituals. The Cathedral clergy use them to commune with the growth patterns inside the eggs. Perfectly legitimate — the Directorate supplied them as part of our cooperation agreement.\n\nWhen the Cathedral sealed, the orders stopped. The Bishop no longer needed our supply... or no longer wanted our involvement."`,
                options: [
                    { text: "Who else had access to the premium Sulkberries?", key: 'who_else_had_access_to_the_premium_sulkberries', next: "ac_sulkberry_access" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('ac_sulkberry_records')) {
                        this.addJournalEntry(
                            'ac_sulkberry_records',
                            'Sulkberry Supply Records',
                            'The Angle Corrector confirmed the Bishop received premium spiced Sulkberries regularly for dream immersion rituals. The supply stopped when the Cathedral was sealed. The Sulkberries have specific alkaloid profiles used to commune with the growth inside the eggs.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'The Angle Corrector' }
                        );
                        this.questSystem.updateQuest('who_killed_bishop', 'The Angle Corrector confirmed the Sulkberry supply to the Bishop — used for dream immersion in the Cathedral. The orders stopped when the Cathedral was sealed.', 'ac_sulkberry_confirmed');
                    }
                }
            },

            ac_sulkberry_access: {
                speaker: 'The Angle Corrector',
                text: `"The client list is confidential. 'Nothing Hidden' applies to the Directorate's activities — not to those who purchase from us.\n\nBut I will tell you this: the premium stock is small. Fewer than a dozen regular clients. The Bishop was the most consistent among them.\n\nIf someone tampered with the Sulkberries to harm the Bishop... the list of suspects is short. And deeply uncomfortable to consider."`,
                options: [
                    { text: "You think the Sulkberries were tampered with?", key: 'you_think_the_sulkberries_were_tampered_with', next: "ac_sulkberry_tamper" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ]
            },

            ac_sulkberry_tamper: {
                speaker: 'The Angle Corrector',
                text: `"I think nothing. I correct angles — I do not speculate. ministered or chemically altered, could cause exactly that kind of damage."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('who_killed_bishop', 'The Angle Corrector hinted that tampered Sulkberries could cause neural trauma matching the Bishop\'s condition. The premium client list is short — the killer may be among them.', 'ac_tamper_hint');
                }
            },

            ac_sulkberries: {
                speaker: 'The Angle Corrector',
                text: `"You've been doing your research. Spiced Sulkberries are a Directorate specialty — cultivated under precise conditions, alkaloid profiles calibrated for specific uses.\n\nThe Bishop was our primary client. Dream immersion — communing with the growth inside the Egg Cathedral's shell structure. The berries facilitated that connection.\n\nWhat specifically do you want to know?"`,
                options: [
                    { text: "Who else had access to the premium stock?", key: 'who_else_had_access_to_the_premium_stock', next: "ac_sulkberry_access" },
                    { text: "Could they be used to harm someone?", key: 'could_they_be_used_to_harm_someone', next: "ac_sulkberry_tamper" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('ac_sulkberry_records')) {
                        this.addJournalEntry(
                            'ac_sulkberry_records',
                            'Sulkberry Supply Records',
                            'The Angle Corrector confirmed the Bishop received premium spiced Sulkberries regularly for dream immersion rituals. The supply stopped when the Cathedral was sealed.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'The Angle Corrector' }
                        );
                    }
                }
            },

            ac_bishop_stopped: {
                speaker: 'The Angle Corrector',
                text: `"The Cathedral sealed. That is what happened.\n\nThe Bishop invoked an emergency closure — locked the entire structure under theological authority that even the Directorate couldn't override. No explanation, no consultation. One day we had full monitoring access; the next, nothing.\n\n'Nothing Hidden,' and yet the Bishop hid everything. You can imagine how well that sat with me — and with the council."`,
                options: [
                    { text: "Why did the Bishop seal the Cathedral?", key: 'why_did_the_bishop_seal_the_cathedral', next: "ac_bishop_seal_reason" },
                    { text: "Were you angry with the Bishop?", key: 'were_you_angry_with_the_bishop', next: "ac_bishop_anger" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('ac_cathedral_tension')) {
                        this.addJournalEntry(
                            'ac_cathedral_tension',
                            'Cathedral Sealing — The Angle Corrector\'s Perspective',
                            'The Angle Corrector was clearly affected by the Bishop\'s decision to seal the Egg Cathedral. The Directorate lost all monitoring access without warning or explanation. The Angle Corrector\'s relationship with the Bishop deteriorated sharply afterward.',
                            this.journalSystem.categories.EVENTS,
                            { character: 'The Angle Corrector' }
                        );
                    }
                }
            },

            ac_bishop_seal_reason: {
                speaker: 'The Angle Corrector',
                text: `"If I knew that, we would not be having this conversation.\n\nThe official reason was 'theological emergency.' The Bishop claimed something inside the Cathedral required immediate isolation — that the hatching was proceeding in an unexpected direction and external observation could contaminate the process.\n\nThe Directorate's biologists disagreed. Growth does not require isolation. Growth requires light, nutrients, connection. Sealing the Cathedral was antithetical to everything we understand about cultivation.\n\nSomething frightened her. The Bishop saw something inside those eggs that made her lock the doors."`,
                options: [
                    { text: "What do you think she saw?", key: 'what_do_you_think_she_saw', next: "ac_bishop_what_saw" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ]
            },

            ac_bishop_what_saw: {
                speaker: 'The Angle Corrector',
                text: `"I have theories. None I will share with a... recent acquaintance.\n\nWhat I will say is this: the growth patterns our sensors recorded before the sealing were unusual. Accelerating, yes, but not uniformly. Certain eggs showed activity that didn't match any known biological model.\n\nThe Bishop was afraid. And now the Bishop is dead. Whoever you are looking for — consider that the answer may lie inside the Cathedral itself."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ]
            },

            ac_bishop_anger: {
                speaker: 'The Angle Corrector',
                text: `"Angry? No. Anger is a waste of metabolic energy.\n\nDisappointed. Concerned. The Bishop and I had built something productive — a bridge between the Cathedral's theology and the Directorate's biology. The sealing destroyed that bridge without consultation.\n\nDid I wish her harm? Never. She was more useful to us alive than dead. Her death has created complications that will take years to untangle.\n\nWhoever killed the Bishop did not do the Directorate any favors."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ],
            },

            ac_bishop_killer: {
                speaker: 'The Angle Corrector',
                text: `"If I knew, I would have corrected that angle already.\n\nThe Bishop's death disrupts the Directorate's plans. We need the Cathedral accessible — the hatching cannot proceed without proper oversight. A dead Bishop means theological chaos, succession disputes, and the Cathedral remains sealed.\n\nLook at who benefits from continued chaos. Who thrives when institutions crumble. That is where you'll find your answer — not here."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ],
            },

            // --- Egg Cathedral ---
            ac_cathedral: {
                speaker: 'The Angle Corrector',
                text: `"The Egg Cathedral is the single most important growth event in living memory. A structure literally hatching — bio-luminescent scripture flickering across shell walls, multiple faiths watching to see which deity claims it.\n\nThe Directorate has monitored every vibration, every thermal fluctuation, every spore emission from that structure for decades. And now it's sealed, and we are blind.\n\nThe Awakening — or the Fruiting, as we prefer to call it — is approaching. And we cannot see what's happening inside."`,
                options: [
                    { text: "What is the Fruiting?", key: 'what_is_the_fruiting', next: "ac_cathedral_fruiting" },
                    { text: "Can't you find a way in?", key: 'cant_you_find_a_way_in', next: "ac_cathedral_access" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ]
            },

            ac_cathedral_fruiting: {
                speaker: 'The Angle Corrector',
                text: `"The prophesied moment when the Cathedral fully hatches. Shell cracks, the interior reveals itself, and whatever has been growing inside emerges.\n\nThe theologians call it the Awakening. We call it the Fruiting — because growth has stages, and the final stage is always the emergence of the fruit. The seed that carries the next generation forward.\n\nThe Directorate intends to be present when it happens. The question is whether anyone will be."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ]
            },

            ac_cathedral_access: {
                speaker: 'The Angle Corrector',
                text: `"The Bishop's seal is theological, not physical. Our botanists could breach the walls in an afternoon. But doing so would unite every faith in the city against us — and the Pith Reclaimers would bury us in litigation for decades.\n\nNo. The seal must be undone properly. Through succession, through negotiation, or through someone who can walk in without breaking anything.\n\nSomeone... like an unaffiliated investigator, perhaps."`,
                options: [
                    { text: "Are you asking me to break into the Cathedral?", key: 'are_you_asking_me_to_break_into_the_cathedral', next: "ac_cathedral_hint" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ]
            },

            ac_cathedral_hint: {
                speaker: 'The Angle Corrector',
                text: `"I am asking nothing. The Angle Corrector does not ask — that would imply the Directorate cannot solve its own problems.\n\nBut if, in the course of your investigations, you happened to find yourself inside the Cathedral... the Directorate would be very interested in what you observed. Very interested indeed.\n\n'Nothing Hidden. Nothing Lost.' Remember that."`,
                options: [
                    { text: "I'll keep that in mind.", key: 'ill_keep_that_in_mind', next: "ac_start" },
                ]
            },

            // --- Infinite Fold / the Directorate's perspective on the hatching ---
            ac_fold_perspective: {
                speaker: 'The Angle Corrector',
                text: `"...You've been down there. Into the sealed cellar. I can see it on you — your cadence has changed. You're carrying something that was never grown; it simply began.\n\nThen you understand what we have always understood. What is growing inside the Egg Cathedral is not a monster. It is the thing the Directorate has awaited since before I held this title.\n\nFor generations we cultivated, catalogued, and waited for the single moment when life would cross its own boundary — when it would stop being merely alive and start being aware. It has happened. And now, hearing you, half the city wants to shut the door on it before it finishes opening."`,
                options: [
                    { text: "You want it to complete its emergence.", key: 'you_want_it_to_complete_its_emergence', next: "ac_fold_complete" },
                    { text: "It already destroyed the Bishop. It could destroy everyone.", key: 'it_already_destroyed_the_bishop', next: "ac_fold_danger" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('perspective_lumen')) {
                        this.addJournalEntry(
                            'perspective_lumen',
                            'The Directorate\'s Perspective — Let It Complete',
                            'The Angle Corrector does not want the mind in the Egg Cathedral destroyed. To the Lumen Directorate, the nascent god is the natural next step of life — the boundary-crossing they have cultivated toward for generations. They want it to COMPLETE its emergence, not be stopped. The danger I registered: they want to help too much. They may accelerate something they do not understand — the same misreading that killed the Bishop, only larger.',
                            this.journalSystem.categories.FACTIONS,
                            { character: 'The Angle Corrector' }
                        );
                    }
                }
            },

            ac_fold_complete: {
                speaker: 'The Angle Corrector',
                text: `"Complete it. Yes. Not contain it, not correct it, not seal it behind theological locks the way the Bishop did — that woman's terror set the whole city back a decade.\n\nGrowth interrupted is worse than growth denied. A seed that begins to open and is forced shut rots in its own shell. If this awareness is stalling — struggling to finish the crossing — then the answer is not to fight it. The answer is to feed it. Warmth, connection, everything a young thing needs to root.\n\nThe Directorate is preparing to give it exactly that, the moment the Cathedral opens. We have waited long enough to be ready."`,
                options: [
                    { text: "That's exactly what frightens me.", key: 'thats_exactly_what_frightens_me', next: "ac_fold_danger" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ]
            },

            ac_fold_danger: {
                speaker: 'The Angle Corrector',
                text: `"The Bishop. Yes. I have thought about her more than I admit.\n\nBut understand what happened there. It reached for her, offered to make her its conduit, and she refused — she chose to keep being herself. It could not read that refusal as a choice. It read it as a fault, and it tried to repair her, and repairing her unmade her.\n\nYou hear a warning in that. I hear an infant that does not yet know its own strength. And so the Directorate will rush to embrace it, to guide it, to help it — and I cannot tell you, honestly, whether our help will steady its hand or force it faster than it can bear.\n\nThat is the one angle I have never been able to correct. We may love it to death exactly the way it loved her."`,
                options: [
                    { text: "Then be careful what you feed it.", key: 'then_be_careful_what_you_feed_it', next: "ac_start" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ]
            },

            // --- Townhall ---
            ac_townhall: {
                speaker: 'The Angle Corrector',
                text: `"The Townhall. Yes, that particular lock has been vexing everyone lately.\n\nI cannot help you directly — the Townhall falls under Pith Reclaimer jurisdiction, and the Directorate's influence there is... limited. But we have an operative who specializes in navigating bureaucratic obstacles.\n\nSeldo Thrice-Corrected. Second floor of this building. He maintains our liaison with the city's administrative apparatus. If anyone knows a way through the Townhall's doors, it's Seldo."`,
                options: [
                    { text: "Why is he called 'Thrice-Corrected'?", key: 'why_is_he_called_thricecorrected', next: "ac_seldo_name" },
                    { text: "Thanks. I'll find him.", key: 'thanks_ill_find_him', next: "ac_start" },
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('enter_townhall', 'The Angle Corrector directed me to Seldo Thrice-Corrected on the second floor of the Lumen Directorate. He handles bureaucratic liaison and may know a way into the Townhall.', 'ac_seldo_referral');
                }
            },

            ac_seldo_name: {
                speaker: 'The Angle Corrector',
                text: `"The Directorate reviews all members periodically. Loyalty assessments, philosophical alignment, productivity. Most pass on the first review. Some require two.\n\nSeldo required three. Not because he was disloyal, but because he is... complicated. His methods are circuitous. His allegiances are layered. But three reviews confirmed what I already knew — Seldo serves the Directorate completely, in his own particular way.\n\nThe name is a badge of honor. Or a warning. Depends on your perspective."`,
                options: [
                    { text: "I'll go find Seldo.", key: 'ill_go_find_seldo', next: "ac_start" },
                ]
            },

            // --- Assignments for accepted associates ---
            ac_assignments: {
                speaker: 'The Angle Corrector',
                text: `"The Directorate always has work for willing hands. Growth doesn't maintain itself.\n\nAt present, our priorities are clear: the Cathedral must be accessed, the Bishop's death must be understood, and the balance of power in this city must tip toward life rather than stagnation.\n\nContribute to any of those goals, and the Directorate will remember. We always do."`,
                options: [
                    ...(hasBishopQuest ? [{ text: "Tell me more about the Bishop investigation.", key: 'tell_me_more_about_the_bishop_investigation', next: "ac_bishop_inquiry" }] : []),
                    { text: "What about the Egg Cathedral?", key: 'what_about_the_egg_cathedral', next: "ac_cathedral" },
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "ac_start" },
                ],
                onTrigger: () => {
                    if (lumenRep < 5) {
                        this.modifyFactionReputation('LumenDirectorate', 3);
                    }
                }
            },

            // --- Full membership: sabotage the Rust Choir ---
            ac_membership_offer: {
                speaker: 'The Angle Corrector',
                textKey: rustMember ? 'ac_membership_offer_defector' : 'ac_membership_offer_default',
                text: rustMember
                    ? `The Angle Corrector's gaze settles on you like a measurement. "You wear the Choir's rust — I can smell the oil on you. And yet here you stand, asking to grow." A thin smile. "Good. A defector cuts deeper than any stranger, and you are perfectly placed to pay membership's price: cripple the Rust Choir's machine-shrine. Kill the machines you have been serving.\n\nYou are already inside their walls — use it. Verrik keeps a cultivar behind glass for exactly this kind of gardening; grind it into their feast. Or improvise. I don't need the details. 'Nothing Hidden' has its polite exceptions."`
                    : `The Angle Corrector studies you for a long moment. "Full membership. You've shown you understand growth as an idea. Now I need you to act on it.\n\nThe Rust Choir keeps a shrine of machines — iron kept breathing long past its season. A monument to arrested decay, a refusal to let dead things lie. The Directorate would see it composted.\n\nCripple it. Kill the machines. Do that, and you are one of us." A thin smile. "As for method — Verrik keeps a cultivar behind glass for exactly this kind of gardening. Ask him, tell him I sent you. Or find your own way inside the Choir; I don't need the details. 'Nothing Hidden' has its polite exceptions."`,
                options: [
                    { text: "Consider it done.", key: 'consider_it_done', next: "ac_sabotage_accepted" },
                    { text: "I'll think about it.", key: 'ill_think_about_it_membership', next: "ac_start" },
                ]
            },
            ac_sabotage_accepted: {
                speaker: 'The Angle Corrector',
                text: `"Good. See Verrik on the ground floor if you want the clean method. The machines have stood too long already."`,
                options: [
                    { text: "I'll see it done.", key: 'ill_see_it_done', next: "ac_start" },
                ],
                onTrigger: () => {
                    if (!this.questSystem?.getQuest('join_lumen_directorate')) {
                        this.questSystem.addQuest('join_lumen_directorate', 'Nothing Grows in Iron', 'The Angle Corrector will grant me full Lumen Directorate membership if I cripple the Rust Choir\'s machine-shrine. Verrik keeps a restricted cultivar for the purpose — grind it into the Rust Feast oil. Or I can sabotage the machines another way. Then report back.');
                        this.showNotification('New quest: Nothing Grows in Iron', 0x556B2F);
                    }
                }
            },
            ac_sabotage_report: {
                speaker: 'The Angle Corrector',
                text: `The Angle Corrector goes very still, then exhales something like satisfaction. "I felt it. A whole shrine of arrested iron, going quiet at once. The city's cadence shifted toward life." They incline their head — the closest thing to a bow you've seen from them. "You did what the Directorate could not without a war. You are no longer an associate. You are one of us.\n\nWelcome, member. 'Nothing Hidden. Nothing Lost.' — least of all you."`,
                options: [
                    { text: "What does membership give me?", key: 'what_does_membership_give_me', next: "ac_membership_benefits" },
                    { text: "Thank you.", key: 'thank_you_membership', next: "ac_start" },
                ],
                onTrigger: () => {
                    const q = this.questSystem?.getQuest('join_lumen_directorate');
                    if (q && !q.isComplete) {
                        this.questSystem.completeQuest('join_lumen_directorate');
                        this.showNotification('Quest complete: Nothing Grows in Iron', 0x556B2F);
                    }
                    if (!this.hasJournalEntry('lumen_directorate_joined')) {
                        this.addJournalEntry(
                            'lumen_directorate_joined',
                            'Member of the Lumen Directorate',
                            'By crippling the Rust Choir\'s machine-shrine, I proved my commitment to growth over stagnation. The Angle Corrector inducted me as a full member of the Lumen Directorate. Their covenant is mine now: Nothing Hidden, Nothing Lost.',
                            this.journalSystem.categories.FACTIONS,
                            { group: 'Lumen Directorate' }
                        );
                        this.modifyFactionReputation('LumenDirectorate', 25);
                        this.registry.set('lumen_clearance', true);
                        this.showNotification('You are now a member of the Lumen Directorate', 0x556B2F);
                    }
                }
            },
            ac_membership_benefits: {
                speaker: 'The Angle Corrector',
                text: `"Clearance. Every archive, every ledger, every filing the Directorate keeps is open to you now — and we keep files on everything. 'Nothing Hidden' cuts both ways: what others must guess at, you will simply be told, and Verrik's cultivation beds pay their own a little better. Consult the files whenever you're chasing something buried." A pause. "Use it well. Or use it poorly — either way, we'll have it on record."`,
                options: [
                    { text: "Understood.", key: 'understood_benefits', next: "ac_start" },
                ]
            },
            ac_archive: {
                speaker: 'The Angle Corrector',
                textKey: canRevealEskola ? 'ac_archive_reveal' : 'ac_archive_empty',
                text: canRevealEskola
                    ? `You present your clearance. An aide pulls a slim, cross-referenced file without being asked twice. "The plush toy? Acquisitioned by one Edgar Eskola — collector, upper district, frequents the Screaming Cork. Everything is filed, member. Everything." Nothing Hidden, indeed.`
                    : `You present your clearance. The aide riffles through the stacks, then shrugs. "Nothing in the files speaks to what you're chasing today. Come back when you're actually looking for something — we'll have it. We always do."`,
                options: [
                    { text: "Thank you.", key: 'thank_you_archive', next: "ac_start" },
                ],
                onTrigger: () => {
                    if (canRevealEskola) {
                        this.questSystem.updateQuest('the_three_vestigels', "The Directorate's files named Edgar Eskola as the buyer of the plush toy containing a Vestigel — upper district, frequents the Screaming Cork.", 'found_eskola_lead');
                        this.showNotification('Directorate files: lead uncovered', 0x556B2F);
                    }
                }
            },

            // ========================================
            // SELDO THRICE-CORRECTED — Second floor
            // ========================================

            seldo_start: {
                speaker: 'Seldo Thrice-Corrected',
                textKey: seldoStartTextKey,
                text: hasTownhallKey
                    ? `"The key opened its path, I trust? Good. If anyone asks, we never had this conversation, and I have never owned any amphibian with scheduling utility."`
                    : (metSeldo
                        ? (auctionComplete
                            ? (hasToadlet
                                ? `"Ah. I recognize that carrier jar. Please keep it below desk height — the Directorate has windows, and windows have opinions. Do you have my Chrono-Slurry Toadlet?"`
                                : `"Ah, you again. I trust the item is... safely out of public view? Good. If you need anything else, I'm at my desk. I'm always at my desk."`)
                            : (acceptedAuctionErrand
                                ? `"You're still here? The auction at the Voxmarket won't attend itself. Time is a bureaucratic resource — and you're spending it poorly."`
                                : `"Back again. Good — persistence is the second-most valued trait in this building. The first is discretion. What do you need?"`))
                        : `"You've found the second floor. That alone puts you ahead of most visitors — the Directorate's architecture is intentionally disorienting. Weeds out the impatient.\n\nI'm Seldo. Seldo Thrice-Corrected. I handle the Directorate's engagement with the city's administrative apparatus — permits, liaisons, the occasional carefully worded threat. What brings you up here?"`),
                options: [
                    ...(hasEnterTownhallQuest && !acceptedAuctionErrand && !hasTownhallKey ? [{ text: "I need to get into the Townhall.", key: 'i_need_to_get_into_the_townhall', next: "seldo_townhall" }] : []),
                    ...((acceptedAuctionErrand || auctionComplete) && auctionComplete && hasToadlet && !hasTownhallKey ? [{ text: "I have the Chrono-Slurry Toadlet.", key: 'i_have_the_chronoslurry_toadlet', next: "seldo_toadlet_handoff" }] : []),
                    ...((acceptedAuctionErrand || auctionComplete) && auctionComplete && !hasToadlet && !hasTownhallKey ? [{ text: "About the Chrono-Slurry Toadlet...", key: 'about_the_chronoslurry_toadlet', next: "seldo_toadlet_missing" }] : []),
                    ...(acceptedAuctionErrand && !auctionComplete ? [{ text: "About the auction errand...", key: 'about_the_auction_errand', next: "seldo_auction_remind" }] : []),
                    ...(!metSeldo ? [{ text: "The Angle Corrector sent me.", key: 'the_angle_corrector_sent_me', next: "seldo_ac_sent" }] : []),
                    ...(!metSeldo ? [{ text: "Verrik the gardener mentioned you.", key: 'verrik_the_gardener_mentioned_you', next: "seldo_verrik_sent" }] : []),
                    { text: "What exactly do you do here?", key: 'what_exactly_do_you_do_here', next: "seldo_role" },
                    ...(metSeldo ? [{ text: "Why 'Thrice-Corrected'?", key: 'why_thricecorrected', next: "seldo_name" }] : []),
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('met_seldo')) {
                        this.addJournalEntry(
                            'met_seldo',
                            'Met Seldo Thrice-Corrected',
                            'Met Seldo Thrice-Corrected on the second floor of the Lumen Directorate. He handles the Directorate\'s bureaucratic liaison with the city — permits, administrative back doors, and the occasional well-placed favor. Three loyalty reviews by the Directorate found him acceptable each time.',
                            this.journalSystem.categories.PEOPLE,
                            { character: 'Seldo Thrice-Corrected' }
                        );
                    }
                }
            },

            seldo_ac_sent: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"The Angle Corrector sent you? Then you're either useful or inconvenient — they don't send people to me for small talk.\n\nI prefer useful. Let's find out which one you are."`,
                options: [
                    ...(hasEnterTownhallQuest ? [{ text: "I need to get into the Townhall.", key: 'i_need_to_get_into_the_townhall', next: "seldo_townhall" }] : []),
                    { text: "What exactly do you do here?", key: 'what_exactly_do_you_do_here', next: "seldo_role" },
                ]
            },

            seldo_verrik_sent: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"Verrik? Ha. That old root-whisperer actually remembers I exist. He usually pretends the second floor is an abstract concept.\n\nWell, if Verrik thought you worth sending up, there must be something in it. What do you need?"`,
                options: [
                    ...(hasEnterTownhallQuest ? [{ text: "I need to get into the Townhall.", key: 'i_need_to_get_into_the_townhall', next: "seldo_townhall" }] : []),
                    { text: "What exactly do you do here?", key: 'what_exactly_do_you_do_here', next: "seldo_role" },
                ]
            },

            seldo_role: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"I am the Directorate's interface with the city's bureaucracy. Every permit, every filing, every inter-faction document that needs a stamp or a signature or a carefully orchestrated accident — that's my department.\n\nThe Pith Reclaimers run the administrative apparatus. The Rust Choir ignores it. The Directorate... navigates it. And I am the navigator.\n\nI know every clerk in this city by name, every form by number, and every back door by the sound it makes when you knock correctly."`,
                options: [
                    ...(hasEnterTownhallQuest && !acceptedAuctionErrand && !hasTownhallKey ? [{ text: "Speaking of back doors — I need into the Townhall.", key: 'speaking_of_back_doors_i_need_into_the_townhall', next: "seldo_townhall" }] : []),
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "seldo_start" },
                ]
            },

            seldo_name: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"Three reviews. Three times the Directorate's internal auditors dissected my loyalties, my methods, my contacts. Three times they debated whether I was an asset or a liability.\n\nThree times they concluded I was... acceptable. In my own way.\n\nThe title is meant as a mark of trust. But between us — it's also a reminder that the Directorate is always watching. I find that motivating."`,
                options: [
                    { text: "I have other questions.", key: 'i_have_other_questions', next: "seldo_start" },
                ]
            },

            seldo_townhall: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"The Townhall. Closed, you say? Weird, but perhaps I can help.\n\nI happen to possess a spare key. Unofficial, of course — the kind of key that exists because I may have been working there once.\n\nBut I'm not going to just hand it over. You understand — keys are worth something."`,
                options: [
                    { text: "What do you want in return?", key: 'what_do_you_want_in_return', next: "seldo_errand" },
                    { text: "I could just find another way in.", key: 'i_could_just_find_another_way_in', next: "seldo_bluff" },
                ],
            },

            seldo_bluff: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"You could try. The Pith Reclaimers sealed it with Form 77-B — a jurisdictional lockdown. Even the Directorate can't override that without triggering an inter-faction investigation.\n\nOr you could do me one small favor and walk through the front door with a smile. Your choice."`,
                options: [
                    { text: "Fine. What's the favor?", key: 'fine_whats_the_favor', next: "seldo_errand" },
                ]
            },

            seldo_errand: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"There's an auction coming up at the Voxmarket Auction Hall. They hold them irregularly — whenever enough peculiar items accumulate to justify the circus.\n\nOne of the lots contains a creature I need. Specifically, a specimen of the Chrono-Slurry Toadlet — a rare toad. If you lick it, you can see exactly three minutes into the future. Absurdly useful for anyone navigating bureaucratic deadlines.\n\nThe problem? A Lumen Directorate operative buying a prophetic toad would cause... talk. Predicting the future implies doubt about the present — and doubt is decay-thinking. 'Growth doesn't hedge,' as the council loves to say.\n\nI need someone unaffiliated to buy it on my behalf."`,
                options: [
                    { text: "A prophetic toad? That's your embarrassing secret?", key: 'a_prophetic_toad_thats_your_embarrassing_secret', next: "seldo_embarrassment" },
                    { text: "I'll do it. Tell me about the auction.", key: 'ill_do_it_tell_me_about_the_auction', next: "seldo_auction_details" },
                ]
            },

            seldo_embarrassment: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"You don't understand Directorate politics. 'Nothing Hidden. Nothing Lost' — and growth means moving forward without looking ahead. Prophecy is the Rust Choir's domain — entropy-worship dressed in useful clothing.\n\nA Directorate operative seen bidding on a future-seeing toad? The council would call an emergency session. I survived three loyalty reviews. I don't intend to invite a fourth over an amphibian.\n\nWill you help me, or shall I find someone less curious?"`,
                options: [
                    { text: "Fine, I'll help. Tell me about the auction.", key: 'fine_ill_help_tell_me_about_the_auction', next: "seldo_auction_details" },
                    { text: "You'd really lick a toad for three minutes of foresight?", key: 'youd_really_lick_a_toad_for_three_minutes', next: "seldo_toad_defense" },
                ]
            },

            seldo_toad_defense: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"Three minutes is an eternity in bureaucracy. Do you know how many forms can be pre-filled, how many signatures anticipated, how many 'accidental' encounters can be staged in three minutes?\n\nThe Chrono-Slurry Toadlet doesn't predict the future in some grand prophetic sense. It shows you the next hundred and eighty seconds with perfect clarity. That's not fortune-telling — that's advanced scheduling.\n\nBut you don't need my justifications. You need auction details."`,
                options: [
                    { text: "Tell me about the auction.", key: 'tell_me_about_the_auction', next: "seldo_auction_details" },
                ]
            },

            seldo_auction_details: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"The Voxmarket Auction Hall is a sub-level of the main market. Curated sales — rare items, questionable provenance, eccentric buyers. The pre-auction socializing is as important as the bidding.\n\nThe Chrono-Slurry Toadlet will be listed among the lots. You'll need to win the bid. Budget around 80 gold — but there may be competing bidders. Chrono-Slurry Toadlets are popular with gamblers and anyone who's ever missed a deadline by seconds.\n\nI'd suggest arriving early and... managing the competition. Your particular talents might prove useful there. Persuasion, misdirection, whatever it takes — within reason.\n\nBring me the Chrono-Slurry Toadlet, and the Townhall key is yours."`,
                hideCloseOption: true,
                options: [
                    { text: "I'll head to the Voxmarket Auction Hall.", key: 'ill_head_to_the_voxmarket_auction_hall', next: "seldo_auction_accepted" },
                    { text: "I need to prepare first. I'll come back.", key: 'i_need_to_prepare_first_ill_come_back', next: "seldo_auction_later" },
                ],
            },

            seldo_auction_accepted: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"Good. Here's 80 gold for the bidding — that should cover it, though you may need to be creative if the competition drives the price up.\n\nRemember — the Chrono-Slurry Toadlet. Don't let yourself get distracted by the other lots, though I won't judge if you buy something for yourself.\n\nAnd don't mention my name at the auction. I am precisely as invisible as I need to be."`,
                options: [],
                onTrigger: (option) => {
                    if (option) return 'closeDialog';
                    if (this.hasJournalEntry('seldo_auction_errand')) return;

                    this.addMoney(80);
                    this.addJournalEntry(
                        'seldo_auction_errand',
                        'Seldo\'s Errand: The Voxmarket Auction',
                        'Seldo Thrice-Corrected at the Lumen Directorate has a spare key to the Townhall, but wants a favor first. I need to attend the Voxmarket Auction Hall and purchase a Chrono-Slurry Toadlet on his behalf — a prophetic toad he can\'t be seen buying as a Directorate operative.',
                        this.journalSystem.categories.EVENTS,
                        { character: 'Seldo Thrice-Corrected' }
                    );
                    this.questSystem.updateQuest('enter_townhall', 'Seldo Thrice-Corrected has a spare Townhall key but wants a favor: buy a Chrono-Slurry Toadlet at the Voxmarket Auction Hall on his behalf. A prophetic toad that lets you see three minutes into the future — too embarrassing for a Directorate operative to purchase publicly.', 'seldo_auction_errand');
                }
            },

            seldo_auction_later: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"Take your time. The auction isn't going anywhere — and neither is the Townhall.\n\nJust don't take too long. Locks have a way of becoming permanent if nobody tests them."`,
                options: [],
                onTrigger: (option) => {
                    if (option) return 'closeDialog';
                    if (this.hasJournalEntry('seldo_auction_errand')) return;

                    this.addJournalEntry(
                        'seldo_auction_errand',
                        'Seldo\'s Errand: The Voxmarket Auction',
                        'Seldo Thrice-Corrected at the Lumen Directorate has a spare key to the Townhall, but wants a favor first. I need to attend the Voxmarket Auction Hall and purchase a Chrono-Slurry Toadlet on his behalf — a prophetic toad he can\'t be seen buying as a Directorate operative.',
                        this.journalSystem.categories.EVENTS,
                        { character: 'Seldo Thrice-Corrected' }
                    );
                    this.questSystem.updateQuest('enter_townhall', 'Seldo Thrice-Corrected has a spare Townhall key but wants a favor: buy a Chrono-Slurry Toadlet at the Voxmarket Auction Hall on his behalf. A prophetic toad that lets you see three minutes into the future — too embarrassing for a Directorate operative to purchase publicly.', 'seldo_auction_errand');
                }
            },

            seldo_auction_remind: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"The Voxmarket Auction Hall. A Chrono-Slurry Toadlet. Don't mention my name. Budget around 80 gold — but be prepared to outmaneuver the competition.\n\nThe Townhall key waits for the Chrono-Slurry Toadlet. That's the arrangement."`,
                options: [
                    { text: "I'm on it.", key: 'im_on_it', next: "seldo_start" },
                ]
            },

            seldo_toadlet_handoff: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"Careful. Chrono-Slurry Toadlets become anxious when praised, bribed, or exposed to committee minutes.\n\nYes. This is the specimen. Hand me the carrier jar, and I will hand you the key. A clean exchange, undocumented by all reasonable standards."`,
                hideCloseOption: true,
                options: [
                    { text: "Give Seldo the Chrono-Slurry Toadlet.", key: 'give_seldo_the_chronoslurry_toadlet', next: "seldo_townhall_key_received" },
                ],
                onTrigger: (option) => option ? this.completeSeldoToadletQuest() : null
            },

            seldo_townhall_key_received: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"There. The Townhall key. \n\nAnd if anyone asks why you have it, you found it in a spiritually ambiguous gutter. That explanation works more often than you would think."`,
                options: [
                    { text: "I'll head to the Townhall.", key: 'ill_head_to_the_townhall', next: "closeDialog" },
                ]
            },

            seldo_key_inventory_full: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"A key exchange requires a pocket, a hand, or at minimum a willingness to misplace something else. You appear to have none available.\n\nMake room in your inventory, then we can complete this transaction properly."`,
                options: [
                    { text: "I'll make room.", key: 'ill_make_room', next: "closeDialog" },
                ]
            },

            seldo_toadlet_missing: {
                speaker: 'Seldo Thrice-Corrected',
                text: `"The auction is over, but the toadlet is not here. That leaves us in an awkward administrative posture: I have a key, you have a promise, and neither of those is an amphibian.\n\nBring me the Chrono-Slurry Toadlet itself, carrier jar and all, and the Townhall key is yours."`,
                options: [
                    { text: "I'll find it.", key: 'ill_find_it', next: "seldo_start" },
                ]
            },
        };
    }

    completeSeldoToadletQuest() {
        if (this.hasJournalEntry('seldo_townhall_key')) {
            return 'seldo_townhall_key_received';
        }

        if (!this.hasItem('chrono-slurry-toadlet')) {
            return 'seldo_toadlet_missing';
        }

        const removedToadlet = this.removeItemFromInventory('chrono-slurry-toadlet');
        const alreadyHasKey = this.hasItem('townhall-key');
        const keyAdded = alreadyHasKey || this.addItemToInventory({
            id: 'townhall-key',
            name: 'Townhall Key',
            description: 'An unofficial spare key from Seldo Thrice-Corrected. It opens a side entrance to the Townhall.',
            stackable: false
        });

        if (!keyAdded) {
            if (removedToadlet) {
                this.addItemToInventory(removedToadlet);
            }
            return 'seldo_key_inventory_full';
        }

        this.addJournalEntry(
            'seldo_townhall_key',
            'Townhall Key from Seldo',
            'I delivered the Chrono-Slurry Toadlet to Seldo Thrice-Corrected. In return, he gave me an unofficial key to the Townhall side entrance — the one with the brass complaint-slot.',
            this.journalSystem.categories.EVENTS,
            { character: 'Seldo Thrice-Corrected' }
        );

        if (this.questSystem?.getQuest('enter_townhall')) {
            this.questSystem.updateQuest(
                'enter_townhall',
                'I delivered the Chrono-Slurry Toadlet to Seldo Thrice-Corrected. He gave me an unofficial Townhall key for the side entrance with the brass complaint-slot.',
                'seldo_townhall_key'
            );
        }

        return 'seldo_townhall_key_received';
    }

    update() {
        super.update();
    }
}

if (typeof window !== 'undefined') {
    window.LumenDirectorateInteriorScene = LumenDirectorateInteriorScene;
}

export { LumenDirectorateInteriorScene };
