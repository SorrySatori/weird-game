import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

/**
 * ScraperCellarScene — the sealed cellar beneath the Scraper: Ortolan & Dr. Elphi's old
 * lab and workshop, where a master copy of the Infinite Loop still sits.
 *
 * For now this is the destination that proves the password puzzle worked; the actual
 * confrontation with the Loop copy (using Ortolan's "losing move") is a future task.
 */
export default class ScraperCellarScene extends GameScene {
    constructor() {
        super({ key: 'ScraperCellarScene' });
        this.isTransitioning = false;
    }

    get dialogContent() {
        return {
            ...super.dialogContent,

            loop_console: {
                speaker: 'The Loop Console',
                text: "A dream-console squats under a tarp gone stiff with dust. You pull it back. The Infinite Loop's master build — Ortolan's rules, Elphi's walls — still seated in the cradle, a single amber light breathing slow beneath the grime.\n\nIt is exactly as they described it, and it is waiting. You are not ready to wear this helmet yet. Not until you understand the losing move.",
                options: [
                    { text: "Leave it, for now.", key: 'leave_it_for_now', next: "closeDialog" }
                ]
            }
        };
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
                'The elevator took me down into the sealed cellar beneath the Scraper — Ortolan and Dr. Elphi\'s old lab. A master copy of the Infinite Loop is still here, seated in its cradle and quietly powered. I\'m not ready to enter it; first I need to understand the "losing move" that lets a trapped mind leave.',
                this.journalSystem.categories.EVENTS,
                { location: 'Scraper Cellar', related: 'The Infinite Loop' }
            );
            if (this.questSystem?.getQuest('find_loop_copy')) {
                this.questSystem.updateQuest(
                    'find_loop_copy',
                    'I reached the sealed cellar under the Scraper and found the Infinite Loop\'s master build. Next I need to learn how to safely enter it and free whoever the Loop is holding — the "losing move" Ortolan spoke of.',
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
