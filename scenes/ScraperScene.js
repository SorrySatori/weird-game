import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';
import { createStreetLamp, meetLamp, lampsFoundCount, GANG_QUEST_IDS, gangQuestStatus, spyFragmentCount, spyReportable, allGangQuestsComplete, gangRewardClaimed, grantGangVestigel } from '../utils/GangOfLamps.js';

export default class ScraperScene extends GameScene {
    constructor() {
        super({ key: 'ScraperScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    get dialogContent() {
        const donMet = !!this.hasJournalEntry('met_lamp_don');
        // At the first meeting `found` counts the OTHER lamps already met (0–3); on a
        // return visit it includes Don himself. Drives the progress-aware greeting.
        const found = lampsFoundCount(this);
        const allLampsFound = found === 4;

        // --- L2: Don's spy quest + the Vestigel reward (only once all lamps are connected) ---
        const spyStatus = gangQuestStatus(this, GANG_QUEST_IDS.don);
        const fragments = spyFragmentCount(this);
        const knowsRustDomain = ['rust_choir_joined', 'cellar_password_learned', 'rust_feast_completed_full', 'rust_feast_completed_illusion', 'rust_feast_completed_poisoned'].some(f => this.hasJournalEntry(f));
        const toldLocation = !!this.hasJournalEntry('gang_spy_location_told');
        const allDone = allGangQuestsComplete(this);
        const rewardClaimed = gangRewardClaimed(this);
        const donConnectedOptions = rewardClaimed
            ? [{ text: "Rest easy, Don.", key: 'don_connected_close', next: "closeDialog" }]
            : allDone
                ? [{ text: "You said the family looks after its friends.", key: 'don_reward_ask', next: "don_reward" }]
                : [
                    ...(spyStatus === 'none'
                        ? [{ text: "You mentioned there'd be work.", key: 'don_spy_offer', next: "don_spy_brief" }]
                        : []),
                    ...(spyStatus === 'active' && (spyReportable(this) || fragments >= 1)
                        ? [{ text: "Let me tell you what I've dug up on the Rust Choir.", key: 'don_spy_deliver', next: "don_spy_report" }]
                        : []),
                    ...(spyStatus === 'active' && !spyReportable(this) && fragments === 0
                        ? [{ text: "Still poking around the Rust Choir.", key: 'don_spy_status', next: "don_spy_statusinfo" }]
                        : []),
                    ...(spyStatus === 'active' && knowsRustDomain && !toldLocation
                        ? [{ text: "[Tell the Don where the Rust Choir's domain actually is]", key: 'don_spy_tell_location', next: "don_spy_location" }]
                        : []),
                    ...(spyStatus === 'done'
                        ? [{ text: "How are the family's other errands?", key: 'don_other_jobs_ask', next: "don_other_jobs" }]
                        : []),
                    { text: "Rest easy, Don.", key: 'don_connected_close', next: "closeDialog" },
                ];
        return {
            ...super.dialogContent, // Include parent dialog content for symbiont dialogs

            // ===== Gang of Lamps: Don Girandole (the leader) — perched on the high walkway under Scraper 1140 =====
            don_lamp_start: {
                speaker: 'Don Girandole',
                textKey: donMet
                    ? (allLampsFound ? 'don_lamp_connected' : 'don_lamp_searching')
                    : (found === 3 ? 'don_lamp_first_last' : found >= 1 ? 'don_lamp_first_some' : 'don_lamp_first'),
                text: !donMet
                    ? (found === 3
                        ? `The gaudy old lamppost bolted to the walkway railing swings its head-lamp toward you — and its flame leaps, bright and startled. "Wait. *Wait.* I can feel them all on the wire behind you — every last one of my family, warm and humming." The light trembles. "You... you found every one of them before me. Then I'm the final light still dark, friend. Thread me in and the family is *whole* — first time in longer than I care to count. Bless your restless little legs." He is, unmistakably, moved.`
                        : found >= 1
                            ? `The gaudy old lamppost bolted to the walkway railing swivels its head-lamp toward you, flame guttering like a fat cigar. It flares with pleasure. "Ahh — I can feel it on the wire already. You've been talking to my family, haven't you? Some of them are warm again for the first time in years." The light dips, fond. "I'm Don Girandole, head of this scattered family of lamps — sentient, every one, and every one bolted to the spot. You've made a good start, errand-light. Bring the rest of us home."`
                            : `The gaudy old lamppost bolted to the walkway railing swivels its head-lamp toward you, flame guttering like a fat cigar. High over the city, the wind makes it hiss. "Come closer, friend. Don't be shy — a lamp can't come to *you*, eh? That's the whole tragedy of my family." The light dips, confidential. "I am Don Girandole. Head of a family of lamps — sentient, every one of us, and every one of us bolted to the spot. We cannot move. We cannot so much as call across the city to one another. Scattered like loose change down the gutters. It eats at a father, being cut off from his own.\n\nBut you — you have legs. You could be my little errand-light. Find the others. Carry our words between us. Do this favor for the family, and the family does not forget its friends."`)
                    : (allLampsFound
                        ? `The Don's flame burns steady and warm now, content as a hearth. "You did it. Every one of mine, back in the circuit. We can *feel* each other again — humming down the wires, the whole family whole." He dims, satisfied. "Rest a moment, friend. Enjoy the quiet. There will be work soon enough — a family like ours always has work — but tonight, you have earned a father's thanks."`
                        : `"Back already? Good, good — but the family's still scattered, friend. A chandelier putting on airs out in the town square, a sconce by the house of stamps, a torch down by the water. Keep those legs moving." The flame flares, impatient but fond.`),
                options: !donMet
                    ? (found === 3
                        ? [
                            { text: "That's everyone, Don. You're the last one.", key: 'don_last_close', next: "closeDialog" }
                        ]
                        : [
                            { text: "Who's still out there?", key: 'don_who', next: "don_lamp_family" },
                            { text: "...you're a talking lamp.", key: 'don_leave', next: "closeDialog" }
                        ])
                    : (allLampsFound
                        ? donConnectedOptions
                        : [
                            { text: "Remind me who's still out there.", key: 'don_remind', next: "don_lamp_family" },
                            { text: "I'll keep looking.", key: 'don_searching_close', next: "closeDialog" }
                        ]),
                onTrigger: () => { meetLamp(this, 'don', 'Don Girandole'); }
            },
            don_lamp_family: {
                speaker: 'Don Girandole',
                text: `"Three of mine are out there, waiting to be found. There's a *chandelier* — puts on airs, stood up on a fancy post out in the town square; she hears everything and repeats most of it. There's a jumpy little *sconce*, sweating on a wall in the house of stamps and forms, watching the clerks bury the city in paper. And there's a *torchère* — a hot-tempered dockhand of a lamp, rusting down by the water where the cargo comes in. Find them. Tell them the Don sends his regards."`,
                options: [
                    { text: "Consider it done, Don.", key: 'don_family_close', next: "closeDialog" }
                ]
            },

            // ===== L2: Don's quest — "Ears on the Rust Choir" =====
            don_spy_brief: {
                speaker: 'Don Girandole',
                text: `The Don's flame drops to a conspiratorial murmur. "Here's the work, friend. That Rust Choir — the ones who love their machines more than their neighbors — they've been humming louder lately, and a father likes to know what his street is singing. I can't exactly walk down there and ask." A dry crackle of a laugh. "You can. Get in among their people — Brukk keeps the domain, Gnur deals whispers down in Shed 521, Ravla forges papers behind the Screaming Cork. Lean on them, learn what the Choir's really about, and bring it back to me. I'll know when you've brought me enough. And if you turn up where their domain actually sits — well, that's a gift on top."`,
                options: [
                    { text: "I'll find out what the Choir's hiding.", key: 'don_spy_accept', next: "closeDialog" }
                ],
                onTrigger: () => {
                    if (!this.questSystem?.getQuest(GANG_QUEST_IDS.don)) {
                        this.questSystem.addQuest(GANG_QUEST_IDS.don, 'Ears on the Rust Choir', "Don Girandole wants me to spy on the Rust Choir — get in among their people (Brukk in their domain, Gnur in Shed 521, Ravla behind the Screaming Cork), learn what they're really up to, and bring it back to him. He'll tell me if I've dug up enough. If I find where their domain actually is, I can pass that along too.");
                    }
                }
            },
            don_spy_statusinfo: {
                speaker: 'Don Girandole',
                text: `"Still at it? Good. Lean on the Rust Choir's people — Brukk down in their domain, Gnur in the guts of Shed 521, Ravla forging behind the Screaming Cork. Get 'em talking, learn what you can, and come tell me what you've turned up. I'll know if it's enough."`,
                options: [
                    { text: "I'm on it.", key: 'don_spy_statusinfo_close', next: "closeDialog" }
                ]
            },
            don_spy_location: {
                speaker: 'Don Girandole',
                text: `The Don goes very still, then his flame swells with satisfaction. "Now *that* is worth knowing. The domain itself. I'll thread that down the family's wire tonight." A coin's worth of warmth. "Here — for your trouble. A father pays for good intelligence."`,
                options: [
                    { text: "Glad to help the family.", key: 'don_spy_location_close', next: "closeDialog" }
                ],
                onTrigger: () => {
                    if (!this.hasJournalEntry('gang_spy_location_told')) {
                        this.addJournalEntry('gang_spy_location_told', 'The Don Knows the Rust Domain', "I told Don Girandole where the Rust Choir's domain actually sits. He paid me for the intelligence.", this.journalSystem.categories.EVENTS, { group: 'Gang of Lamps' });
                        this.addMoney(40);
                        // Dragging the decay-faction's hidden seat into the light leans Growth.
                        this.modifyGrowthDecay(4, 0);
                    }
                }
            },
            don_spy_report: {
                speaker: 'Don Girandole',
                textKey: spyReportable(this) ? 'don_spy_report_full' : 'don_spy_report_partial',
                text: spyReportable(this)
                    ? `The Don listens without a flicker, drinking in every word. When you finish, the flame glows deep and approving. "Now *that's* more than I'd hoped for, friend. That's the sound of a street that can't surprise me anymore." He dims, pleased. "You did the family a service. Don't think it's forgotten — nothing is, with me."`
                    : `The Don listens, flame tilting as he weighs it. "Mm. A whisper. It's a start, friend — but one loose thread isn't the whole cloth." The light flickers, not unkind. "Get back in among them and prise loose a little more. I'll know when you've brought me enough."`,
                options: [
                    { text: "Understood, Don.", key: 'don_spy_report_close', next: "closeDialog" }
                ],
                onTrigger: () => {
                    // Only a report the Don judges sufficient (2 secrets, or false intel from a betrayal)
                    // completes the job. A single whisper just earns an encouraging "learn more."
                    if (!spyReportable(this)) return;
                    const q = this.questSystem?.getQuest(GANG_QUEST_IDS.don);
                    if (q && !q.isComplete) {
                        this.questSystem.completeQuest(GANG_QUEST_IDS.don);
                        this.addMoney(30);
                        // Shedding real light on what the Choir hid nudges Growth — but only if the
                        // intel is genuine. A betrayer feeds the Don lies (the decay was already paid).
                        if (!this.hasJournalEntry('gang_spy_betrayed')) {
                            this.modifyGrowthDecay(3, 0);
                        }
                    }
                }
            },
            don_other_jobs: {
                speaker: 'Don Girandole',
                text: `"My end's settled, thanks to you. But the family's still got irons out — the torch has a run he needs made, the chandelier wants some morsel of gossip only she'd treasure, and the little sconce has something the clerks buried that he'd dearly like back. See them all right, and come back to me. There's a reward waiting that a family only gives its truest friend."`,
                options: [
                    { text: "I'll finish their errands.", key: 'don_other_jobs_close', next: "closeDialog" }
                ]
            },
            don_reward: {
                speaker: 'Don Girandole',
                text: `The Don's flame rises tall and golden, and for a moment he looks less like a lamp than like an old man at the head of a full table. "Every errand run. Every one of my family lit and humming, and every debt they owed, paid through *you*." A long, warm pause. "A family keeps its promises. We've had this squirreled away in a gutter for longer than you've been alive — never trusted a soul enough to hand it over. Take it. One of the three alive-coins. A *Vestigel*." The object drops into your palm, faintly pulsing. "Whatever you do with it, friend — you did right by us."`,
                options: [
                    { text: "Thank you, Don. Truly.", key: 'don_reward_close', next: "closeDialog" }
                ],
                onTrigger: () => { grantGangVestigel(this); }
            }
        };
    }

    preload() {
        super.preload();
        this.load.image('scraperBg', 'assets/images/backgrounds/Scraper1140.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        this.load.image('lamp_don', 'assets/images/characters/don_girandole.png');
        this.load.image('vestigel', 'assets/images/items/vestigel.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set scraper background
        const bg = this.add.image(400, 300, 'scraperBg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        this.playSceneMusic('genericMusic');

        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        // Add invisible clickable exit area at the left side
        this.exitArea = this.add.image(50, 470, 'exitArea')
            .setDisplaySize(40, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        this.exitArea.setDepth(10);
        
        // Position the priest at the right side when entering
        this.priest.x = 700;
        this.priest.y = 470;
        
        // Update priest's glow position
        if (this.priestGlow) {
            this.priestGlow.x = this.priest.x;
            this.priestGlow.y = this.priest.y;
        }

        // Add fade-in effect
        this.cameras.main.fadeIn(800, 0, 0, 0);
        
        // Add entrance to the Scraper building interior
        const scraperEntrance = this.add.image(400, 470, 'exitArea')
            .setDisplaySize(100, 200)
            .setAlpha(0.01)
            .setInteractive({ useHandCursor: true });
        scraperEntrance.setDepth(5);
        
        // Add a hint about the scraper entrance
        const scraperHint = this.add.text(400, 380, 'Enter Scraper', {
            fontSize: '16px',
            fill: '#7fff8e',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            padding: { x: 10, y: 5 }
        });
        scraperHint.setOrigin(0.5);
        scraperHint.setAlpha(0);
        scraperHint.setDepth(10);
        
        // Show hint when hovering near the entrance
        this.input.on('pointermove', (pointer) => {
            // Check if pointer is near the scraper entrance
            if (Math.abs(pointer.x - 400) < 50 && Math.abs(pointer.y - 470) < 100) {
                scraperHint.setAlpha(1);
            } else {
                scraperHint.setAlpha(0);
            }
        });
        
        // Add scraper entrance click handler
        scraperEntrance.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;
            
            // Add journal entry about the Scraper
            if (!this.hasJournalEntry('scraper_building')) {
                this.addJournalEntry(
                    'scraper_building',
                    'The Scraper',
                    'The imposing structure known as "The Scraper" rises above the surrounding buildings. Once a corporate headquarters called Nexicorp Tower, it now stands as a living monument to transformation. Its lower floors house those who remember the old ways, while the middle floors have become wild ecosystems. No one knows how many floors it has. Elevators refuse to count them. Tenants report missing levels, duplicate floors, and entire wings dedicated to unrecognized languages or species. Most assume the building self-generates new strata in response to emotional entropy.',
                    this.journalSystem.categories.PLACES,
                    { location: 'The Scraper, Upper Morkezela' }
                );
            }
            
            // Move priest to scraper entrance
            const priest = this.priest;
            if (!priest) {
                // If priest doesn't exist, just transition immediately
                this.cameras.main.fadeOut(800, 0, 0, 0);
                this.cameras.main.once('camerafadeoutcomplete', () => {
                    this.scene.start('ScraperInteriorScene');
                    this.isTransitioning = false;
                });
                return;
            }
            
            // Create a variable to track if the tween completed
            let tweenCompleted = false;
            
            // Play walk animation
            priest.play('walk');
            
            // Kill any existing tweens
            this.tweens.killTweensOf(priest);
            
            this.tweens.add({
                targets: priest,
                x: 400,
                y: 470,
                duration: 1000,
                onComplete: () => {
                    tweenCompleted = true;
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('ScraperInteriorScene');
                        this.isTransitioning = false; // Reset transition flag
                    });
                }
            });
            
            // Add a safety timeout in case the tween doesn't complete
            this.time.delayedCall(2000, () => {
                if (!tweenCompleted) {
                    console.log('Scraper entrance transition timed out, forcing transition');
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('ScraperInteriorScene');
                        this.isTransitioning = false;
                    });
                }
            });
        });

        // Exit area click handler
        this.exitArea.on('pointerdown', () => {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const priest = this.priest;
            if (!priest) {
                // If priest doesn't exist, just transition immediately
                this.cameras.main.fadeOut(800, 0, 0, 0);
                this.cameras.main.once('camerafadeoutcomplete', () => {
                    this.scene.start('CrossroadScene');
                    this.isTransitioning = false;
                });
                return;
            }
            
            // Create a variable to track if the tween completed
            let tweenCompleted = false;
            
            // Play walk animation
            priest.play('walk');
            
            // Kill any existing tweens
            this.tweens.killTweensOf(priest);

            this.tweens.add({
                targets: priest,
                x: 50,
                y: 470,
                duration: 1000,
                onComplete: () => {
                    tweenCompleted = true;
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('CrossroadScene');
                        this.isTransitioning = false;
                    });
                }
            });
            
            // Add a safety timeout in case the tween doesn't complete
            this.time.delayedCall(2000, () => {
                if (!tweenCompleted) {
                    console.log('Exit transition timed out, forcing transition');
                    this.cameras.main.fadeOut(800, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        this.scene.start('CrossroadScene');
                        this.isTransitioning = false;
                    });
                }
            });
        });
        
        // Create exit to ScreamingCorkScene at the right edge
        this.transitionManager.createTransitionZone(
            750, // x position
            470, // y position
            80, // width
            200, // height
            'right', // direction
            'BurningBearStreetScene', // target scene
            750, // walk to x
            470 // walk to y
        );

        // Gang of Lamps: Don Girandole is bolted to a rooftop fixture on the far-right skyline
        // (the structure the player marked). Above the right-edge exit zone (y370-570), so no
        // click conflict. Depth 6 keeps him behind the walking priest.
        createStreetLamp(this, 'lamp_don', 750, 210, 0.13, 'don_lamp_start');

        // Examine: the tower & its "SCRAPER 1140" sign (upper-center, clear of Don at x750 and
        // the entrance below). Comment deepens once you've been inside / learned of the cellar lab.
        this.createObservable(430, 170, 240, 150, () => {
            if (this.hasJournalEntry('met_infinite_fold')) return this.t('observe.scraper.knows_cellar');
            if (this.hasJournalEntry('scraper_building')) return this.t('observe.scraper.been_inside');
            return this.t('observe.scraper.default');
        }, { hint: this.t('observe.scraper.hint') });
    }

    update() {
        super.update();
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.ScraperScene = ScraperScene;
}
