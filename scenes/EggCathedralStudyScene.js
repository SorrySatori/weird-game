import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

/**
 * EggCathedralStudyScene — the first room inside the Egg Cathedral: the Bishop's study,
 * preserved inside the living organism. Here the player finds the rest of her journal
 * (five entries). Reading it is optional — it is a key to *understanding*, not to a good
 * ending: it unlocks a special exchange with the Unborn in the god chamber deeper in.
 *
 * Reached from CathedralEntrance (after the Guardian relents) or, as a bypass, through
 * Edgar's secret gap from the cathedral exterior. Leads deeper to EggCathedralInteriorScene.
 *
 * Background: native 1067×600 from tools/artgen/cathedral_study_bg.py — an egg-shaped chamber, the study's stone
 * walls under a translucent eggshell vault with stone ribs; the desk grows out of the living apse. Exits are painted:
 * the doorway in the left wall (back to the threshold) and the stair in the right wall (deeper in).
 */

// Canvas outlines of the painted exits (printed by cathedral_study_bg.py).
const STUDY_DOOR = [[28, 529], [28, 421], [39, 396], [59, 380], [78, 370], [97, 365], [114, 367], [130, 371], [146, 382], [154, 400], [154, 492]];
const STUDY_STAIR = [[766, 458], [766, 376], [773, 357], [785, 345], [798, 340], [811, 337], [825, 341], [839, 349], [854, 363], [862, 386], [862, 478]];
export default class EggCathedralStudyScene extends GameScene {
    constructor() {
        super({ key: 'EggCathedralStudyScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        const read = !!this.hasJournalEntry('bishop_journal_read');
        return {
            ...super.dialogContent,

            journal_intro: {
                speaker: 'Narrator',
                textKey: read ? 'read' : 'first',
                text: read
                    ? "The Bishop's journal lies open where you left it, its membrane peeled back, the candles still tended by the cathedral. Her last words wait, should you wish to read them again."
                    : "A desk grows straight out of the living wall, its grain half wood and half something that pulses. The scrolls on it are sheathed in a clear protective membrane; candles burn low and never gutter, kept alight by the cathedral itself. This was the last place she was still entirely herself.\n\nBeneath the membrane, in a familiar hand, lies the rest of the Bishop's journal.",
                options: [
                    { text: read ? "Read it again." : "Peel back the membrane and read.", key: 'journal_read', next: "journal_1" },
                    { text: "Leave it be.", key: 'journal_leave', next: "closeDialog" }
                ],
                onTrigger: () => {
                    this.addJournalFact('egg_cathedral_study_entered', 'last_place', "The cathedral itself keeps her candles lit. It was the last place she was still entirely herself.");
                }
            },

            journal_1: {
                speaker: "The Bishop's Journal",
                text: "*First entry.*\n\n\"Today I heard singing in places where no voice can be. The priests say it is the god, answering. But I fear it is not an answer.\n\nIt is a question.\"",
                options: [{ text: "Turn the page.", key: 'journal_1_next', next: "journal_2" }]
            },
            journal_2: {
                speaker: "The Bishop's Journal",
                text: "\"The walls have changed. Not the way a building changes. The way a body learns its own shape.\n\nI understand now: the cathedral was not built around the egg. The cathedral is how the egg is trying to understand the world.\"",
                options: [{ text: "Turn the page.", key: 'journal_2_next', next: "journal_3" }]
            },
            journal_3: {
                speaker: "The Bishop's Journal",
                text: "\"Today I saw something that frightened me more than the egg. A machine with no soul began to show compassion. And a thing that was meant to be a god began to search for answers.\n\nThey are not master and tool. They are two becoming things, and each has changed the other.\"",
                options: [{ text: "Turn the page.", key: 'journal_3_next', next: "journal_4" }]
            },
            journal_4: {
                speaker: "The Bishop's Journal",
                text: "\"If anyone ever finds this, know one thing.\n\nI do not call you here to destroy it. And I do not call you here to kneel to it.\n\nI call you because, for the first time in the history of our world, something has come into being that has no place to belong.\"",
                options: [{ text: "Turn the page.", key: 'journal_4_next', next: "journal_5" }]
            },
            journal_5: {
                speaker: "The Bishop's Journal",
                text: "*Last entry.*\n\n\"The Guardian did not obey me because I am its mistress. It obeyed me because it understood my fear.\n\nBut fear is no reason for a thing to be made forever. I have bought what time I could. The rest is not mine to decide.\n\nIt is yours.\"",
                onTrigger: () => {
                    if (!this.hasJournalEntry('bishop_journal_read')) {
                        // Pending fact first (no second "Journal updated"): only names Infinite Fold
                        // if the player has actually met it.
                        this.noteJournalFoldLink();
                        this.addJournalEntry(
                            'bishop_journal_read',
                            "The Bishop's Journal",
                            "I found the rest of the Bishop's journal in her study, preserved inside the living cathedral. She was not the new god's enemy — she feared the unknown, watched it and a soulless machine change each other into two becoming things, and knew that something had come into being with no place to belong. She sent her distress signal not so someone would destroy it or worship it, but so someone would come. She bought what time she could — the Guardian obeyed her because it understood her fear — and left the final choice to whoever came after: to me.",
                            this.journalSystem.categories.LORE,
                            { location: 'Egg Cathedral', character: 'The Bishop', related: 'The Unborn God' }
                        );
                        const q = this.questSystem?.getQuest('find_bishop_notebook');
                        if (q && !q.isComplete) this.questSystem.completeQuest('find_bishop_notebook');
                    }
                },
                options: [{ text: "Close the journal.", key: 'journal_close', next: "closeDialog" }]
            }
        };
    }

    preload() {
        super.preload();
        this.load.image('arrow', 'assets/images/ui/arrow.png');
        this.load.image('eggCathedralStudyBg', 'assets/images/backgrounds/EggCathedralStudy.png');
    }

    create() {
        super.create();
        this.playSceneMusic('cathedralTheme');

        const bg = this.add.image(this.scale.width / 2, 300, 'eggCathedralStudyBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        // The background paints the study's own floor; drop the generic ground strip
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }

        this.transitionManager = new SceneTransitionManager(this);
        // Back out to the threshold: the doorway in the left wall (the arrow keys leave by it at the left edge too).
        const door = this.transitionManager.createDoorZone({ points: STUDY_DOOR }, {
            target: 'CathedralEntrance', walkX: 90, walkY: 470, label: 'Back to the Threshold', direction: 'left'
        });
        this.registerEdgeExit('left', () => this.leaveByEdge('left', 'CathedralEntrance'), door);
        // Deeper in, to the god chamber: the stair climbing away in the right wall.
        this.transitionManager.createDoorZone({ points: STUDY_STAIR }, {
            target: 'EggCathedralInteriorScene', walkX: 814, walkY: 470, label: 'Deeper In', direction: 'up'
        });

        // Coming back down from the heart: arrive at the foot of the stair; otherwise by the doorway.
        this.priest.x = this.enteredFrom === 'EggCathedralInteriorScene' ? 800 : 230;
        this.priest.y = 470;
        if (this.priestGlow) { this.priestGlow.x = this.priest.x; this.priestGlow.y = this.priest.y; }

        this.cameras.main.fadeIn(800, 0, 0, 0);

        // The journal on the desk (800-space, remapped like createObservable): the desk and its hutch of pigeonholes.
        const kx = this.scale.width / 800;
        const jx = Math.round(400 * kx), jy = 400;
        const label = this.add.text(jx, 318, this.t('ui.hotspots.bishopJournal'), {
            fontSize: '12px', fill: '#e8c97a', backgroundColor: 'rgba(0,0,0,0.6)', padding: { x: 5, y: 3 }
        }).setOrigin(0.5).setDepth(5).setVisible(false);
        const zone = this.add.zone(jx, jy, Math.round(140 * kx), 140).setOrigin(0.5).setDepth(4);
        zone.setInteractive({ useHandCursor: true });
        zone.on('pointerover', () => { label.setVisible(true); document.body.style.cursor = 'pointer'; });
        zone.on('pointerout', () => { label.setVisible(false); document.body.style.cursor = 'default'; });
        zone.on('pointerdown', () => { if (this.dialogVisible) return; if (this.clickSound) this.clickSound.play(); this.showDialog('journal_intro'); });

        if (!this.hasJournalEntry('egg_cathedral_study_entered')) {
            this.addJournalEntry(
                'egg_cathedral_study_entered',
                "The Bishop's Study",
                "Inside the cathedral I found a small chamber — the Bishop's study, kept whole inside the living organism. A desk grows from the wall; scrolls lie sealed under a membrane; candles burn low.",
                this.journalSystem.categories.PLACES,
                { location: 'Egg Cathedral', character: 'The Bishop' }
            );
        }

        // Palinode found the seam in the shell (EggCatedralScene) and the Guardian never opened the
        // front way — so the player came in through that gap: now they know where it leads.
        if (this.hasJournalEntry('seam_sense_cathedral_gap') && !this.hasJournalEntry('cathedral_guardian_passed')) {
            this.addJournalFact('seam_sense_cathedral_gap', 'study', "The seam drops straight into the Bishop's study.");
        }

        // Read her journal before meeting Infinite Fold, met it since: the machine now has a name.
        if (this.hasJournalEntry('bishop_journal_read')) this.noteJournalFoldLink();
    }

    /** Fact on `bishop_journal_read` naming the "soulless machine" — only once Infinite Fold is met. */
    noteJournalFoldLink() {
        if (!this.hasJournalEntry('met_infinite_fold')) return;
        this.addJournalFact('bishop_journal_read', 'infinite_fold', "The soulless machine she wrote of can only be Infinite Fold, the mind from the Scraper cellar.");
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
    window.EggCathedralStudyScene = EggCathedralStudyScene;
}

export { EggCathedralStudyScene };
