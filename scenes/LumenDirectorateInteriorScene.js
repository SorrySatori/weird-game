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
    }

    createAngleCorrector() {
        this.angleCorrector = this.add.image(530, 280, 'angleCorrector');
        this.angleCorrector.setScale(0.18);
        this.angleCorrector.setDepth(5);
        this.angleCorrector.setInteractive({ useHandCursor: true });

        // Olive-green glow effect
        this.angleCorrectorGlow = this.add.graphics();
        this.angleCorrectorGlow.fillStyle(0x556B2F, 0.15);
        this.angleCorrectorGlow.fillCircle(530, 280, 45);
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

    get dialogContent() {
        const hasLumenQuest = !!(this.questSystem?.getQuest('find_lumen_directorate') && !this.questSystem.getQuest('find_lumen_directorate').isComplete);
        const lumenQuestDone = !!this.questSystem?.getQuest('find_lumen_directorate')?.isComplete;
        const hasBishopQuest = !!(this.questSystem?.getQuest('who_killed_bishop') && !this.questSystem.getQuest('who_killed_bishop').isComplete);
        const hasEnterTownhallQuest = !!(this.questSystem?.getQuest('enter_townhall') && !this.questSystem.getQuest('enter_townhall').isComplete);
        const knowsSulkberries = !!this.hasJournalEntry('elphi_berries_analysis');
        const knowsLumenLead = !!this.hasJournalEntry('elphi_lumen_lead');
        const knowsBishopVisits = !!this.hasJournalEntry('gardener_bishop_visits');
        const metAngleCorrector = !!this.hasJournalEntry('met_angle_corrector');
        const passedGrowthTest = !!this.hasJournalEntry('ac_growth_test_passed');
        const knowsCathedralTension = !!this.hasJournalEntry('ac_cathedral_tension');
        const knowsSulkberryRecords = !!this.hasJournalEntry('ac_sulkberry_records');

        const lumenRep = this.factionSystem?.getReputation('LumenDirectorate') || 0;
        const hasThorne = !!this.symbiontSystem?.hasSymbiont('thorne-still');
        const hasNeme = !!this.symbiontSystem?.hasSymbiont('neme-crownmire');
        const growth = this.growthDecaySystem?.getGrowth() || 50;
        const decay = this.growthDecaySystem?.getDecay() || 50;

        return {
            ...super.dialogContent,

            // --- Entry point ---
            ac_start: {
                speaker: 'The Angle Corrector',
                text: metAngleCorrector
                    ? (passedGrowthTest
                        ? `"You return. Good — I prefer those who come back over those who linger. What brings you to the third floor this time?"`
                        : `"Ah, you again. Still circling, still uncertain. Have you decided what growth means to you yet?"`)
                    : `"Stop. Don't come any closer until I've had a look at you.\n\n...Interesting. You carry spores — everyone does — but yours have an unusual cadence. Like a song that hasn't decided what key it's in.\n\nI am the Angle Corrector. That is my title, my name, and my function. State your business."`,
                options: [
                    ...(hasLumenQuest && !passedGrowthTest ? [{ text: "Captain Liris sent me. I'm here to join the Directorate.", next: "ac_liris_recruit" }] : []),
                    ...(hasBishopQuest && (knowsLumenLead || knowsBishopVisits) ? [{ text: "I'm investigating the Bishop's death.", next: "ac_bishop_inquiry" }] : []),
                    ...(hasBishopQuest && knowsSulkberries && !knowsSulkberryRecords ? [{ text: "I need to ask about spiced Sulkberries.", next: "ac_sulkberries" }] : []),
                    ...(hasEnterTownhallQuest ? [{ text: "I need help getting into the Townhall.", next: "ac_townhall" }] : []),
                    { text: "Tell me about the Lumen Directorate.", next: "ac_about_directorate" },
                    ...(metAngleCorrector ? [{ text: "What's happening with the Egg Cathedral?", next: "ac_cathedral" }] : []),
                    ...(passedGrowthTest ? [{ text: "What can I do for the Directorate?", next: "ac_assignments" }] : []),
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
                text: `"Liris. Yes, she has a talent for spotting potential in unlikely places. She once recruited a navigator who couldn't tell port from starboard — turned out to be the best wind-reader the Verdigrace ever had.\n\nBut Liris's recommendation opens the door. It doesn't seat you at the table. For that, I need to understand something about you first."`,
                options: [
                    { text: "What do you need to know?", next: "ac_growth_test" },
                    { text: "I thought this was a formality.", next: "ac_not_formality" },
                ]
            },

            ac_not_formality: {
                speaker: 'The Angle Corrector',
                text: `"Nothing here is a formality. Formality is decay dressed in clean clothes. Every interaction in this building serves a purpose — even this one.\n\nSo. Are you ready for my question, or would you prefer to wander the atrium until the ferns claim you?"`,
                options: [
                    { text: "Ask your question.", next: "ac_growth_test" },
                ]
            },

            ac_growth_test: {
                speaker: 'The Angle Corrector',
                text: `"The Directorate's foundation is growth. Not just the sprouting of seeds or the spread of mycelium — though we value those deeply. Growth as principle. Growth as philosophy.\n\nSo tell me: what does growth mean to you? And think carefully — I can smell a rehearsed answer the way my ferns smell rain."`,
                hideCloseOption: true,
                options: [
                    { text: "Growth is change — becoming something you weren't before.", next: "ac_test_change" },
                    { text: "Growth is survival — spreading to ensure you endure.", next: "ac_test_survival" },
                    ...(hasThorne ? [{ text: "I carry the Thorne-Still. I know what it means to resist growth.", next: "ac_test_thorne" }] : []),
                    ...(hasNeme ? [{ text: "The Neme-Crownmire taught me — growth is connection.", next: "ac_test_neme" }] : []),
                    ...(growth > 65 ? [{ text: "I don't think about it. I just grow. It's what I do.", next: "ac_test_instinct" }] : []),
                    ...(decay > 65 ? [{ text: "Growth without decay is just accumulation. You need both.", next: "ac_test_balance" }] : []),
                ]
            },

            ac_test_change: {
                speaker: 'The Angle Corrector',
                text: `"Change. A safe answer, but not a wrong one. Change is the minimum condition for growth — necessary but not sufficient.\n\nA rock erodes. That is change. But it is not growth. Growth requires direction. Intent. A reaching-toward.\n\nStill... you didn't say 'power' or 'conquest.' That tells me something useful about you. The Directorate accepts your answer — provisionally."`,
                options: [
                    { text: "What happens now?", next: "ac_test_passed" },
                ],
            },

            ac_test_survival: {
                speaker: 'The Angle Corrector',
                text: `"Survival. The mushroom's answer — spread spores far enough and something will take root somewhere. There's pragmatism in that.\n\nThe Directorate was built on survival. After the Board Games War, when the Ludarchs consumed themselves, we grew from the wreckage. Survival first, then expansion, then purpose.\n\nYour honesty is noted. The Directorate accepts your answer."`,
                options: [
                    { text: "What happens now?", next: "ac_test_passed" },
                ],
            },

            ac_test_thorne: {
                speaker: 'The Angle Corrector',
                text: `"...You carry a Thorne-Still and you walked into the headquarters of the growth faction. Either you are very brave or very foolish.\n\nBut you understand something most don't — that growth defined by its opposition is still growth. The tension between the Thorne's decay and your own living pattern creates something... dynamic.\n\nThat is a more interesting answer than most recruits give. The Directorate accepts you — and your passenger."`,
                options: [
                    { text: "You're not bothered by the symbiont?", next: "ac_test_passed" },
                ],
            },

            ac_test_neme: {
                speaker: 'The Angle Corrector',
                text: `"The Neme-Crownmire. A growth-aligned symbiont — and a possessive one. It has taught you well.\n\nConnection is the root system beneath the visible forest. One tree is fragile. A thousand trees networked through mycorrhiza? That is power that endures.\n\nYes. The Directorate accepts you readily. The Neme-Crownmire's chosen carriers are always welcome here."`,
                options: [
                    { text: "What happens now?", next: "ac_test_passed" },
                ],
            },

            ac_test_instinct: {
                speaker: 'The Angle Corrector',
                text: `"Ha. You don't think about it, you say. And yet here you are, actively seeking to grow your connections, your influence, your understanding.\n\nInstinct is the oldest form of growth — the kind that predates philosophy. The root doesn't ask why it reaches for water. It simply reaches.\n\nThe Directorate has room for instinct. In fact, we prefer it to overthinking. Accepted."`,
                options: [
                    { text: "What happens now?", next: "ac_test_passed" },
                ],
            },

            ac_test_balance: {
                speaker: 'The Angle Corrector',
                text: `"...That is not an answer the Directorate would normally welcome. We are growth. Decay is what we oppose.\n\nBut you are not wrong. The forest that never sheds its leaves suffocates itself. The Rust Choir, for all their corrosion worship, understand something about necessary endings.\n\nI will not repeat your answer to the council. But between us — I find it refreshingly honest. Accepted."`,
                options: [
                    { text: "What happens now?", next: "ac_test_passed" },
                ],
            },

            ac_test_passed: {
                speaker: 'The Angle Corrector',
                text: `"Now? You are recognized by the Lumen Directorate as an associate — not a member, not yet. Membership requires time and proven dedication.\n\nBut you have access. You may move freely within these halls, consult our archives, and seek assignments from the Directorate's operatives.\n\nWelcome to the growth. Try not to wilt."`,
                options: [
                    { text: "I have questions.", next: "ac_start" },
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
                    { text: "What about the Rust Choir and the Pith Reclaimers?", next: "ac_other_factions" },
                    { text: "What is your role here?", next: "ac_role" },
                    { text: "I have other questions.", next: "ac_start" },
                ]
            },

            ac_other_factions: {
                speaker: 'The Angle Corrector',
                text: `"The Rust Choir worships entropy. They dress corrosion in sacred robes and call it 'the silence between.' Romantic nonsense — decay without purpose is just death.\n\nThe Pith Reclaimers are bureaucrats who believe they can manage chaos with enough forms and procedures. They emerged from the wreckage of the Ludarchs' administrative apparatus and never stopped filing.\n\nWe work with both when necessary. The Directorate is pragmatic above all."`,
                options: [
                    { text: "I have other questions.", next: "ac_start" },
                ]
            },

            ac_role: {
                speaker: 'The Angle Corrector',
                text: `"I correct angles. When the Directorate's growth bends in an unproductive direction, I straighten it. When external forces apply pressure — the Cathedral, the Choir, the Townhall — I adjust our trajectory.\n\nCultivation oversight, diplomatic liaison, recruit assessment. Every thread that requires a delicate touch passes through this office.\n\nI am, in essence, the Directorate's gardener — though Verrik downstairs would bristle at the comparison."`,
                options: [
                    { text: "I have other questions.", next: "ac_start" },
                ]
            },

            // --- Bishop investigation ---
            ac_bishop_inquiry: {
                speaker: 'The Angle Corrector',
                text: knowsBishopVisits
                    ? `"So the gardener has been talking. Verrik means well, but he sees packages and formal visits and imagines secrets. Some of what he told you is true. Some... requires context.\n\nYes, the Bishop visited regularly. Yes, the visits stopped. What would you like to know?"`
                    : `"The Bishop's death. I wondered when someone would come asking about the Directorate's connection.\n\nWe were not uninvolved. The Bishop and I had a professional relationship — regular meetings, mutual interests. I will answer what I can, within reason."`,
                options: [
                    { text: "What was your relationship with the Bishop?", next: "ac_bishop_relationship" },
                    ...(knowsBishopVisits ? [{ text: "What were the packages Verrik saw?", next: "ac_bishop_packages" }] : []),
                    { text: "Why did the visits stop?", next: "ac_bishop_stopped" },
                    { text: "Do you know who killed the Bishop?", next: "ac_bishop_killer" },
                    { text: "I have other questions.", next: "ac_start" },
                ]
            },

            ac_bishop_relationship: {
                speaker: 'The Angle Corrector',
                text: `"Professional. Cordial. Occasionally tense.\n\nThe Bishop represented the Egg Cathedral's interests. The Directorate has always monitored the Cathedral — the hatching is the most significant growth event in decades, and we intended to be present when it happened.\n\nOur meetings covered Cathedral access, cultivation samples, and the theological implications of bio-growth within sacred architecture. The Bishop tolerated our interest. Sometimes she even welcomed it."`,
                options: [
                    { text: "What changed?", next: "ac_bishop_stopped" },
                    { text: "I have other questions.", next: "ac_start" },
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('who_killed_bishop', 'The Angle Corrector confirmed a professional relationship with the Bishop — regular meetings about Cathedral access and the hatching. Something changed when the Cathedral was sealed.', 'ac_bishop_relationship');
                }
            },

            ac_bishop_packages: {
                speaker: 'The Angle Corrector',
                text: `"The packages were spiced Sulkberries. Premium cultivation — very specific alkaloid profiles. The Bishop ordered them regularly.\n\nThey are used in dream immersion rituals. The Cathedral clergy use them to commune with the growth patterns inside the eggs. Perfectly legitimate — the Directorate supplied them as part of our cooperation agreement.\n\nWhen the Cathedral sealed, the orders stopped. The Bishop no longer needed our supply... or no longer wanted our involvement."`,
                options: [
                    { text: "Who else had access to the premium Sulkberries?", next: "ac_sulkberry_access" },
                    { text: "I have other questions.", next: "ac_start" },
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
                    { text: "You think the Sulkberries were tampered with?", next: "ac_sulkberry_tamper" },
                    { text: "I have other questions.", next: "ac_start" },
                ]
            },

            ac_sulkberry_tamper: {
                speaker: 'The Angle Corrector',
                text: `"I think nothing. I correct angles — I do not speculate.\n\nBut the Bishop was found with neural trauma. Dream immersion, improperly administered or chemically altered, could cause exactly that kind of damage. The Cardinal Feast dream cartridge was found corrupted.\n\nDraw your own conclusions. I have given you what I can without compromising the Directorate's position."`,
                options: [
                    { text: "I have other questions.", next: "ac_start" },
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('who_killed_bishop', 'The Angle Corrector hinted that tampered Sulkberries could cause neural trauma matching the Bishop\'s condition. The premium client list is short — the killer may be among them.', 'ac_tamper_hint');
                }
            },

            ac_sulkberries: {
                speaker: 'The Angle Corrector',
                text: `"You've been doing your research. Spiced Sulkberries are a Directorate specialty — cultivated under precise conditions, alkaloid profiles calibrated for specific uses.\n\nThe Bishop was our primary client. Dream immersion — communing with the growth inside the Egg Cathedral's shell structure. The berries facilitated that connection.\n\nWhat specifically do you want to know?"`,
                options: [
                    { text: "Who else had access to the premium stock?", next: "ac_sulkberry_access" },
                    { text: "Could they be used to harm someone?", next: "ac_sulkberry_tamper" },
                    { text: "I have other questions.", next: "ac_start" },
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
                    { text: "Why did the Bishop seal the Cathedral?", next: "ac_bishop_seal_reason" },
                    { text: "Were you angry with the Bishop?", next: "ac_bishop_anger" },
                    { text: "I have other questions.", next: "ac_start" },
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
                    { text: "What do you think she saw?", next: "ac_bishop_what_saw" },
                    { text: "I have other questions.", next: "ac_start" },
                ]
            },

            ac_bishop_what_saw: {
                speaker: 'The Angle Corrector',
                text: `"I have theories. None I will share with a... recent acquaintance.\n\nWhat I will say is this: the growth patterns our sensors recorded before the sealing were unusual. Accelerating, yes, but not uniformly. Certain eggs showed activity that didn't match any known biological model.\n\nThe Bishop was afraid. And now the Bishop is dead. Whoever you are looking for — consider that the answer may lie inside the Cathedral itself."`,
                options: [
                    { text: "I have other questions.", next: "ac_start" },
                ]
            },

            ac_bishop_anger: {
                speaker: 'The Angle Corrector',
                text: `"Angry? No. Anger is a waste of metabolic energy.\n\nDisappointed. Concerned. The Bishop and I had built something productive — a bridge between the Cathedral's theology and the Directorate's biology. The sealing destroyed that bridge without consultation.\n\nDid I wish her harm? Never. She was more useful to us alive than dead. Her death has created complications that will take years to untangle.\n\nWhoever killed the Bishop did not do the Directorate any favors."`,
                options: [
                    { text: "I have other questions.", next: "ac_start" },
                ],
            },

            ac_bishop_killer: {
                speaker: 'The Angle Corrector',
                text: `"If I knew, I would have corrected that angle already.\n\nThe Bishop's death disrupts the Directorate's plans. We need the Cathedral accessible — the hatching cannot proceed without proper oversight. A dead Bishop means theological chaos, succession disputes, and the Cathedral remains sealed.\n\nLook at who benefits from continued chaos. Who thrives when institutions crumble. That is where you'll find your answer — not here."`,
                options: [
                    { text: "I have other questions.", next: "ac_start" },
                ],
            },

            // --- Egg Cathedral ---
            ac_cathedral: {
                speaker: 'The Angle Corrector',
                text: `"The Egg Cathedral is the single most important growth event in living memory. A structure literally hatching — bio-luminescent scripture flickering across shell walls, multiple faiths watching to see which deity claims it.\n\nThe Directorate has monitored every vibration, every thermal fluctuation, every spore emission from that structure for decades. And now it's sealed, and we are blind.\n\nThe Awakening — or the Fruiting, as we prefer to call it — is approaching. And we cannot see what's happening inside."`,
                options: [
                    { text: "What is the Fruiting?", next: "ac_cathedral_fruiting" },
                    { text: "Can't you find a way in?", next: "ac_cathedral_access" },
                    { text: "I have other questions.", next: "ac_start" },
                ]
            },

            ac_cathedral_fruiting: {
                speaker: 'The Angle Corrector',
                text: `"The prophesied moment when the Cathedral fully hatches. Shell cracks, the interior reveals itself, and whatever has been growing inside emerges.\n\nThe theologians call it the Awakening. We call it the Fruiting — because growth has stages, and the final stage is always the emergence of the fruit. The seed that carries the next generation forward.\n\nThe Directorate intends to be present when it happens. The question is whether anyone will be."`,
                options: [
                    { text: "I have other questions.", next: "ac_start" },
                ]
            },

            ac_cathedral_access: {
                speaker: 'The Angle Corrector',
                text: `"The Bishop's seal is theological, not physical. Our botanists could breach the walls in an afternoon. But doing so would unite every faith in the city against us — and the Pith Reclaimers would bury us in litigation for decades.\n\nNo. The seal must be undone properly. Through succession, through negotiation, or through someone who can walk in without breaking anything.\n\nSomeone... like an unaffiliated investigator, perhaps."`,
                options: [
                    { text: "Are you asking me to break into the Cathedral?", next: "ac_cathedral_hint" },
                    { text: "I have other questions.", next: "ac_start" },
                ]
            },

            ac_cathedral_hint: {
                speaker: 'The Angle Corrector',
                text: `"I am asking nothing. The Angle Corrector does not ask — that would imply the Directorate cannot solve its own problems.\n\nBut if, in the course of your investigations, you happened to find yourself inside the Cathedral... the Directorate would be very interested in what you observed. Very interested indeed.\n\n'Nothing Hidden. Nothing Lost.' Remember that."`,
                options: [
                    { text: "I'll keep that in mind.", next: "ac_start" },
                ]
            },

            // --- Townhall ---
            ac_townhall: {
                speaker: 'The Angle Corrector',
                text: `"The Townhall. Yes, that particular lock has been vexing everyone lately.\n\nI cannot help you directly — the Townhall falls under Pith Reclaimer jurisdiction, and the Directorate's influence there is... limited. But we have an operative who specializes in navigating bureaucratic obstacles.\n\nSeldo Thrice-Corrected. Second floor of this building. He maintains our liaison with the city's administrative apparatus. If anyone knows a way through the Townhall's doors, it's Seldo."`,
                options: [
                    { text: "Why is he called 'Thrice-Corrected'?", next: "ac_seldo_name" },
                    { text: "Thanks. I'll find him.", next: "ac_start" },
                ],
                onTrigger: () => {
                    this.questSystem.updateQuest('enter_townhall', 'The Angle Corrector directed me to Seldo Thrice-Corrected on the second floor of the Lumen Directorate. He handles bureaucratic liaison and may know a way into the Townhall.', 'ac_seldo_referral');
                }
            },

            ac_seldo_name: {
                speaker: 'The Angle Corrector',
                text: `"The Directorate reviews all members periodically. Loyalty assessments, philosophical alignment, productivity. Most pass on the first review. Some require two.\n\nSeldo required three. Not because he was disloyal, but because he is... complicated. His methods are circuitous. His allegiances are layered. But three reviews confirmed what I already knew — Seldo serves the Directorate completely, in his own particular way.\n\nThe name is a badge of honor. Or a warning. Depends on your perspective."`,
                options: [
                    { text: "I'll go find Seldo.", next: "ac_start" },
                ]
            },

            // --- Assignments for accepted associates ---
            ac_assignments: {
                speaker: 'The Angle Corrector',
                text: `"The Directorate always has work for willing hands. Growth doesn't maintain itself.\n\nAt present, our priorities are clear: the Cathedral must be accessed, the Bishop's death must be understood, and the balance of power in this city must tip toward life rather than stagnation.\n\nContribute to any of those goals, and the Directorate will remember. We always do."`,
                options: [
                    ...(hasBishopQuest ? [{ text: "Tell me more about the Bishop investigation.", next: "ac_bishop_inquiry" }] : []),
                    { text: "What about the Egg Cathedral?", next: "ac_cathedral" },
                    { text: "I have other questions.", next: "ac_start" },
                ],
                onTrigger: () => {
                    if (lumenRep < 5) {
                        this.modifyFactionReputation('LumenDirectorate', 3);
                    }
                }
            },
        };
    }

    update() {
        super.update();
    }
}

if (typeof window !== 'undefined') {
    window.LumenDirectorateInteriorScene = LumenDirectorateInteriorScene;
}

export { LumenDirectorateInteriorScene };
