import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import JournalSystem from '../systems/JournalSystem.js';
import { showDemoEnd } from '../utils/demo.js';
import { UI_FONT, UI_SMALL } from '../utils/pixelFrame.js';

// The Bishop: slumped against the rear bench under the torn roof (bottom-centre on the floor line)
const BX = 735, BY = 518;
// onceFlags (saved): the priest's words over her have been heard -- written when they close, so a game quit halfway
// through hears them again
const FOUND_FLAG = 'bus_found_bishop';
// In Cinema the bottom bar covers the floor where she lies: through the monologue the camera rises this far, so she
// lies above the bar with her feet clear (its top is at about y 378; the dialog and the HUD are pinned to the screen)
const CINEMA_LIFT = 170;

/**
 * The bus sunk in the Scraper's backyard, where the Bishop lies dead: the end of the demo. The first time in, the priest
 * walks up to her and thinks aloud (the monologue below); when he's done the credits and the end card roll
 * (utils/demo.js showDemoEnd). After "Keep exploring" she is only something to look at: no examination in the demo.
 */
export default class AbandonedBusScene extends GameScene {
    constructor() {
        super({ key: 'AbandonedBusScene' });
        this.isTransitioning = false;
        this.journalSystem = JournalSystem.getInstance();
    }

    preload() {
        super.preload();
        // tools/artgen/bus_bg.py: native 1067×600, the inside of the half-buried double-decker
        this.load.image('abandonedBusInteriorBg', 'assets/images/backgrounds/AbandonedBus.png');
        // tools/artgen/dead_bishop.py: 5 frames of 192×88 (0-3 the growth's pulse + the helmet screen's flicker,
        // 4 = a bust), shown at scale 1
        this.load.spritesheet('deadBishopIdle', 'assets/images/characters/dead_bishop.png', { frameWidth: 192, frameHeight: 88 });
    }

    create() {
        // scene instances are re-used
        this.cutscene = false;
        this.monologueEnding = false;
        super.create();

        // the bus paints its own floor: no generic ground strip
        const bg = this.add.image(400, 300, 'abandonedBusInteriorBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }

        this.transitionManager = new SceneTransitionManager(this);

        // by the front door he came in through (feet on the walk line, y 534)
        if (this.priest) {
            this.priest.x = 190;
            this.priest.y = 470;
            this.priest.play('idle');
            if (this.priestGlow) {
                this.priestGlow.x = this.priest.x;
                this.priestGlow.y = this.priest.y;
            }
        }

        // the bus itself: the hollow where the upper deck fell in, its seats on the ledge (clear of the body)
        this.createObservable(270, 295, 260, 90, () => this.t('observe.abandoned_bus.default'), { hint: this.t('observe.abandoned_bus.hint') });

        // the way out: the open front door in the far wall (daylight from the dug-out trench), lit whole on hover
        const exitDoor = this.transitionManager.createDoorZone({ rect: [136, 370, 72, 112] }, {
            target: 'ScraperBackyardScene', walkX: 172, walkY: 470, direction: 'left'
        });
        // the arrow keys leave by the same door at the left edge (GameScene.registerEdgeExit)
        this.registerEdgeExit('left', () => this.leaveByEdge('left', 'ScraperBackyardScene'), exitDoor);

        this.createBishop();
        // the player (Thaal's apprentice, not a priest; the sprite key is historical) in the monologue: his bust in
        // the Cinema bar, his own figure in Bubbles
        const priestBust = { key: 'priest', frame: 0, zoom: 2, top: 4 };
        this.dialogPortraits = { ...(this.dialogPortraits || {}), Apprentice: priestBust, 'Učedník': priestBust };

        if (this.journalSystem && !this.journalSystem.hasEntry('abandoned_bus_interior')) {
            this.addJournalEntry(
                'abandoned_bus_interior',
                'Abandoned Bus Interior',
                'Inside the crumbling, half-buried bus, new life is pushing its way up. The seats are rotting, pale mushrooms sprout from the benches and patches of green light glow in the dark.',
                this.journalSystem.categories.PLACES,
                { location: 'Abandoned Bus' }
            );
        }

        this.cameras.main.fadeIn(800, 0, 0, 0);

        if (!(this.registry.get('onceFlags') || []).includes(FOUND_FLAG)) this.playDiscovery();
    }

    /** Her body, the growth on it pulsing; hover shows who she is (the green aura is automatic), a click a look. */
    createBishop() {
        if (!this.anims.exists('dead_bishop_pulse')) {
            this.anims.create({ key: 'dead_bishop_pulse', frames: this.anims.generateFrameNumbers('deadBishopIdle', { frames: [0, 0, 0, 1, 2, 2, 3, 0, 0, 0, 0, 1, 3, 0] }), frameRate: 3, repeat: -1 });
        }
        this.deadBishop = this.add.sprite(BX, BY, 'deadBishopIdle', 0).setOrigin(0.5, 1).setDepth(6);
        this.deadBishop.play('dead_bishop_pulse');
        // the hit area is the body itself (frame-local), not the whole 192×88 frame
        this.deadBishop.setInteractive({
            hitArea: new Phaser.Geom.Rectangle(40, 12, 146, 76),
            hitAreaCallback: Phaser.Geom.Rectangle.Contains,
            useHandCursor: true
        });
        // (the hotspot labels' look: GameScene.createObservable)
        const label = this.nameTag(this.add.text(BX + 10, BY - 104, this.t('ui.hotspots.deadBishop'), {
            fontFamily: UI_FONT, fontSize: UI_SMALL, fill: '#7fff8e', backgroundColor: 'rgba(12, 20, 16, 0.92)', padding: { x: 6, y: 4 }
        }).setOrigin(0.5).setAlpha(0).setDepth(100));
        this.deadBishop.on('pointerover', () => { if (!this.cutscene) label.setAlpha(1); });
        this.deadBishop.on('pointerout', () => label.setAlpha(0));
        this.deadBishop.on('pointerdown', (pointer, localX, localY, event) => {
            event?.stopPropagation?.();   // the click is the body's, not a walk to that spot
            if (this.cutscene || this.dialogVisible || this.isTransitioning || this.isInputBlocked()) return;
            this.showSpeechBubble(this.priest, this.t('observe.dead_bishop.default'), { persistent: true });
        });
    }

    /** While he walks up to her and speaks, the scene is his: no walking off, no exits, no hotspots. */
    isModalOpen() {
        return super.isModalOpen() || !!this.cutscene;
    }

    /** The first time in: a beat to take in the bus, then he walks up to her and the monologue starts. */
    playDiscovery() {
        this.cutscene = true;
        this.time.delayedCall(1200, () => {
            const priest = this.priest;
            if (!priest) { this.showDialog('bishop_found_1'); return; }
            const targets = this.priestGlow ? [priest, this.priestGlow] : [priest];
            const kneelX = BX - 110;   // to the left of the body, turned toward her
            const dir = kneelX > priest.x ? 1 : -1;
            priest.setScale(dir, 1);
            this.priestGlow?.setScale(dir * 1.05, 1.05);
            priest.play('walk', true);
            this.tweens.add({
                targets,
                x: kneelX,
                y: 470,
                duration: Math.max(300, Math.abs(kneelX - priest.x) * 4),
                onComplete: () => {
                    priest.play('idle');
                    this.time.delayedCall(500, () => this.showDialog('bishop_found_1'));
                }
            });
        });
    }

    /** She is found: the journal and the quest (once; the monologue's first line). */
    recordDiscovery() {
        if (this.journalSystem && !this.journalSystem.hasEntry('found_dead_bishop')) {
            this.addJournalEntry(
                'found_dead_bishop',
                "The Bishop's Fate",
                "I found the Bishop dead in an abandoned bus behind the Scraper. She looks as if she were only asleep. On her head is a helmet like the game helmets I saw at Dr. Elphi's, only somehow different. Did somebody want her silenced?",
                this.journalSystem.categories.EVENTS,
                { character: 'Bishop', location: 'Abandoned Bus' }
            );
        }
        const questSystem = this.questSystem || this.registry.get('questSystem');
        const quest = questSystem?.getQuest('find_bishop');
        if (quest && !quest.isComplete) {
            questSystem.updateQuest('find_bishop', 'I found the Bishop dead in an abandoned bus behind the Scraper.', 'found_dead_in_bus');
            questSystem.completeQuest('find_bishop');
        }
    }

    /**
     * Each line drawn (utils/dialogLayouts.js): through the monologue in Cinema the camera rises so she shows above the
     * bar; Bubbles are drawn where the figures stand at rest, so there it snaps back.
     */
    onDialogLayout(style) {
        if (this.cutscene && style === 'cinema') this.frameBishop(CINEMA_LIFT);
        else this.frameBishop(0, true);
    }

    frameBishop(lift, snap = false) {
        const cam = this.cameras.main;
        this.tweens.killTweensOf(cam);
        if (snap) cam.scrollY = lift;
        else if (cam.scrollY !== lift) this.tweens.add({ targets: cam, scrollY: lift, duration: 700, ease: 'Sine.easeInOut' });
    }

    /** The monologue's close (its last line, any way it closes): the credits and the end card of the demo. */
    hideDialog() {
        super.hideDialog();
        if (!this.monologueEnding) return;
        this.monologueEnding = false;
        this.frameBishop(0);   // the camera settles back (the credits wait 700 ms)
        this.onceEver(FOUND_FLAG, () => {});
        // the scene is his until the end card hands it back ("Keep exploring" resumes it)
        if (showDemoEnd(this)) this.events.once(Phaser.Scenes.Events.RESUME, () => { this.cutscene = false; });
        else this.cutscene = false;
    }

    get dialogContent() {
        return {
            ...super.dialogContent,
            bishop_found_1: {
                speaker: 'Apprentice',
                text: "That's... that's the Bishop! It has to be her. She looks like she's only asleep. But she isn't, is she? No. She's dead, no doubt about it.",
                hideCloseOption: true,
                options: [{ text: 'Continue', key: 'bus_mono_next', next: 'bishop_found_2' }],
                onTrigger: () => this.recordDiscovery()
            },
            bishop_found_2: {
                speaker: 'Apprentice',
                text: "What happened here? Did somebody want her silenced? And what's that on her head? It looks like one of those game helmets I saw at Dr. Elphi's, only somehow different.",
                hideCloseOption: true,
                options: [{ text: 'Continue', key: 'bus_mono_next', next: 'bishop_found_3' }]
            },
            bishop_found_3: {
                speaker: 'Apprentice',
                text: "Could the doctor herself have had a hand in this? But she sent me here herself, of her own free will.",
                hideCloseOption: true,
                options: [{ text: 'Continue', key: 'bus_mono_next', next: 'bishop_found_4' }]
            },
            bishop_found_4: {
                speaker: 'Apprentice',
                text: "So what now? The Master is waiting for news, and the one person who might have known anything about that call from the city is dead. And this is only my first day here. Who knows what comes next?",
                hideCloseOption: true,
                options: [{ text: '...', key: 'bus_mono_end', next: 'closeDialog' }],
                onTrigger: () => { this.monologueEnding = true; }
            },
        };
    }
}

if (typeof window !== 'undefined') window.AbandonedBusScene = AbandonedBusScene;
