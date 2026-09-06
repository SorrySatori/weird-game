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
 * PLACEHOLDER ART: drawn procedurally (a study grown into living tissue).
 */
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
                ]
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
                        this.addJournalEntry(
                            'bishop_journal_read',
                            "The Bishop's Journal",
                            "I found the rest of the Bishop's journal in her study, preserved inside the living cathedral. She was not the new god's enemy — she feared the unknown, understood that it and Infinite Fold had changed each other into something with no place to belong, and sent her distress signal not so someone would destroy it or worship it, but so someone would come. She used her failing seal deliberately, to buy time, and left the final choice to whoever came after: to me.",
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
    }

    create() {
        super.create();
        this.playSceneMusic('cathedralTheme');

        // --- Procedural placeholder: a study grown into living tissue. ---
        const g = this.add.graphics().setDepth(-1);
        g.fillStyle(0x0b1512, 1); g.fillRect(0, 0, this.scale.width, this.scale.height);
        g.fillStyle(0x162a20, 1); g.fillEllipse(400, 300, 780, 580);
        g.fillStyle(0x203b2c, 1); g.fillEllipse(400, 330, 560, 420);
        // Desk growing out of the wall.
        g.fillStyle(0x3a2c1e, 1); g.fillRect(300, 330, 200, 26);
        g.fillStyle(0x2c2115, 1); g.fillRect(320, 356, 12, 90); g.fillRect(468, 356, 12, 90);
        // Membrane-wrapped scrolls.
        for (const sx of [330, 360, 452]) {
            this.add.rectangle(sx, 322, 16, 20, 0xbfe6c8, 0.22).setDepth(1);
        }
        // Candles the cathedral keeps lit.
        for (const cx2 of [312, 488]) {
            this.add.rectangle(cx2, 316, 4, 14, 0xd8c9a0, 0.9).setDepth(1);
            const flame = this.add.circle(cx2, 306, 4, 0xffcf7a, 0.95).setDepth(2);
            this.tweens.add({ targets: flame, alpha: { from: 0.5, to: 0.95 }, scaleX: { from: 0.8, to: 1.2 }, duration: 700, yoyo: true, repeat: -1 });
        }

        this.add.text(400, 578, '[ Egg Cathedral — study placeholder art ]', {
            fontSize: '11px', fill: '#5f8f6f', backgroundColor: 'rgba(0,0,0,0.4)', padding: { x: 5, y: 2 }
        }).setOrigin(0.5).setDepth(8);

        this.transitionManager = new SceneTransitionManager(this);
        // Back out to the threshold.
        this.transitionManager.createTransitionZone(
            120, 500, 120, 60, 'left', 'CathedralEntrance', 200, 470, 'Back to the Threshold'
        );
        // Deeper in, to the god chamber.
        this.transitionManager.createTransitionZone(
            400, 40, 220, 40, 'up', 'EggCathedralInteriorScene', 400, 80, 'Deeper In'
        );

        this.priest.x = 400;
        this.priest.y = 480;
        if (this.priestGlow) { this.priestGlow.x = this.priest.x; this.priestGlow.y = this.priest.y; }

        this.cameras.main.fadeIn(800, 0, 0, 0);

        // The journal on the desk.
        const jx = 400, jy = 322;
        const glow = this.add.circle(jx, jy, 6, 0xffcf7a, 0.9).setDepth(3);
        this.tweens.add({ targets: glow, alpha: { from: 0.3, to: 0.9 }, duration: 1500, yoyo: true, repeat: -1 });
        const label = this.add.text(jx, jy - 40, "The Bishop's Journal", {
            fontSize: '12px', fill: '#e8c97a', backgroundColor: 'rgba(0,0,0,0.6)', padding: { x: 5, y: 3 }
        }).setOrigin(0.5).setDepth(5).setVisible(false);
        const zone = this.add.zone(jx, jy, 150, 120).setOrigin(0.5).setDepth(4);
        zone.setInteractive({ useHandCursor: true });
        zone.on('pointerover', () => { label.setVisible(true); document.body.style.cursor = 'pointer'; });
        zone.on('pointerout', () => { label.setVisible(false); document.body.style.cursor = 'default'; });
        zone.on('pointerdown', () => { if (this.dialogVisible) return; if (this.clickSound) this.clickSound.play(); this.showDialog('journal_intro'); });

        if (!this.hasJournalEntry('egg_cathedral_study_entered')) {
            this.addJournalEntry(
                'egg_cathedral_study_entered',
                "The Bishop's Study",
                "Inside the cathedral, past the threshold, I found a small chamber — the Bishop's study, kept whole inside the living organism. A desk grows from the wall; her scrolls are sealed under a membrane; candles burn that no one lit. It was the last place she was still herself.",
                this.journalSystem.categories.PLACES,
                { location: 'Egg Cathedral', character: 'The Bishop' }
            );
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
    window.EggCathedralStudyScene = EggCathedralStudyScene;
}

export { EggCathedralStudyScene };
