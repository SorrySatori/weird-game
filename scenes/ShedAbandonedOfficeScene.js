import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

const WALK_Y = 534 - 64;   // the priest's centre (128 px, origin 0.5) with his feet on the floor line y 534

export default class ShedAbandonedOfficeScene extends GameScene {
    constructor() {
        super({ key: 'ShedAbandonedOfficeScene' });
        this.isTransitioning = false;
    }

    preload() {
        super.preload();
        this.preloadMusic('shedLoop');
        this.load.image('office-bg', 'assets/images/backgrounds/ShedAbandonedOffice.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        this.playSceneMusic('shedLoop', { resume: true });
        
        // Native 1067×600 on the shared camera (tools/artgen/office_native_bg.py): the old room redrawn, the graffito
        // BETTER DECAY THAN CHANGE sprayed anew; Palinode's bricked opening on the graffito wall stays at canvas (662, 212)
        const bg = this.add.image(400, 300, 'office-bg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        // The background paints its own floor; the generic ground strip would cover it.
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }

        // The redrawn room uses the shared camera, so the priest is his usual size again (no setPriestScale)
        if (this.priest) {
            this.priest.x = 250;  // Match entrance position from Shed521FloorsScene
            this.priest.y = WALK_Y;
            this.priest.play('idle');
        }
        this.transitionManager = new SceneTransitionManager(this);

        // the whole left edge of the room: the stairwell door is just out of frame (its warm light falls on the floor)
        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            50, // width
            200, // height
            'left', // direction
            'Shed521FloorsScene',
            50, // walk to x
            WALK_Y, // walk to y
            'Back to the stairs' 
        )

        // The doorway in the back wall (canvas x 437..502 with its frame, y 293..416): the stair down to the Hall, lit
        // green from below; the zone takes in the threshold too
        this.transitionManager.createTransitionZone(
            352, // x position
            362, // y position
            50, // width
            140, // height
            'up', // direction
            'ShedHallScene',
            352, // walk to x
            WALK_Y, // walk to y
            'To the Hall'
        )

        // The graffiti BETTER DECAY THAN CHANGE (canvas x 700..975, y 135..345, so its hover label clears the HUD; clear of Palinode's arch at x 639..685)
        this.createObservable(628, 240, 206, 210, () => {
            const lean = this.getGDTendency ? this.getGDTendency() : 'balanced';
            if (lean === 'decayDominant') return this.t('observe.office_graffiti.decay');
            if (lean === 'growthDominant') return this.t('observe.office_graffiti.growth');
            return this.t('observe.office_graffiti.default');
        }, { hint: this.t('observe.office_graffiti.hint'), bubble: { maxWidth: 300 } });

        // Palinode's Seam-Sense: unsay the bricked-over tunnel behind the office. Others walk
        // straight past it; only the unsaying feels the honest draft behind the false wall.
        this.createSeamSenseTunnel();
    }

    /**
     * Seam-Sense hook. If the player carries Palinode, a bricked-over tunnel mouth behind the
     * abandoned office can be "unsaid" — revealing a lore pocket leading toward the Living Core.
     * Persisted via registry 'shed_tunnel_opened' and restored on re-entry.
     */
    createSeamSenseTunnel() {
        if (!this.symbiontSystem?.hasSymbiont('palinode')) return;

        const cx = 662, cy = 212;   // the patch of bare brick by the corner of the graffito wall (canvas coords)

        if (this.registry.get('shed_tunnel_opened')) {
            // Already unsaid — show the opened tunnel mouth exhaling cold air.
            this.showOpenedTunnel(cx, cy);
            return;
        }

        // A seam in the bricked wall: a shimmer wearing the shape of solid masonry.
        const glint = this.add.graphics().setDepth(6);
        glint.fillStyle(0xbfe6c8, 0.14);
        glint.fillCircle(cx, cy, 22);
        this.tweens.add({ targets: glint, alpha: { from: 0.14, to: 0.4 }, duration: 1600, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });

        const label = this.add.text(cx, cy - 42, 'A SEAM IN THE BRICKWORK', {
            fontSize: '12px', fill: '#cde6d6', backgroundColor: 'rgba(0,0,0,0.6)', padding: { x: 5, y: 3 }
        }).setOrigin(0.5).setDepth(8).setVisible(false);

        const zone = this.add.zone(cx - 30, cy - 45, 60, 90).setOrigin(0, 0);
        zone.setInteractive({ hitArea: new Phaser.Geom.Rectangle(0, 0, 60, 90), hitAreaCallback: Phaser.Geom.Rectangle.Contains, useHandCursor: true });
        zone.on('pointerover', () => { label.setVisible(true); document.body.style.cursor = 'pointer'; });
        zone.on('pointerout', () => { label.setVisible(false); document.body.style.cursor = 'default'; });
        zone.on('pointerdown', () => {
            if (this.dialogVisible) return;
            if (this.clickSound) this.clickSound.play();
            this.openBrickedTunnel(cx, cy, { glint, label, zone });
        });

        this.seamSenseTunnelSpot = { glint, label, zone };
    }

    /** Unsay the bricked tunnel: reveal the lore pocket, write the journal, small spore reward. */
    openBrickedTunnel(cx, cy, refs) {
        if (this.registry.get('shed_tunnel_opened')) return;
        this.registry.set('shed_tunnel_opened', true);

        if (refs) {
            refs.glint?.destroy();
            refs.label?.destroy();
            refs.zone?.destroy();
        }
        this.seamSenseTunnelSpot = null;

        if (!this.hasJournalEntry('seam_sense_shed_tunnel')) {
            this.addJournalEntry(
                'seam_sense_shed_tunnel',
                'Seam-Sense: The Bricked Tunnel',
                'Behind the abandoned office the Shape-Clerks walled off a run of the old corridors long ago and let everyone forget it. Palinode felt the honest draft behind the false wall and unsaid the brick. The tunnel exhales cold air and a slow, wet pulse — it runs down toward the Living Core, the artifact of living metal fused into Shed 521\'s walls that keeps the whole Bureau powered. It is still breathing, barely, and the deeper the tunnel goes the more the walls seem to breathe with it. In the rubble where the bricks gave way I found a cache of dried spores the masons left sealed inside. No wall is the last word.',
                this.journalSystem.categories.LORE,
                { location: 'Shed 521', via: 'palinode', related: 'Living Core' }
            );
        }

        if (typeof this.modifySpores === 'function') {
            this.modifySpores(12);
        }

        this.showNotification(this.t('gd.palinode_brick'));
        this.showOpenedTunnel(cx, cy);
    }

    /** Draw the opened tunnel mouth (restored on re-entry once the seam has been unsaid). */
    showOpenedTunnel(cx, cy) {
        const mouth = this.add.ellipse(cx, cy, 44, 84, 0x0a1410, 0.85).setDepth(0);
        const breath = this.add.circle(cx, cy, 6, 0xbfe6c8, 0.7).setDepth(1);
        this.tweens.add({ targets: breath, alpha: { from: 0.2, to: 0.7 }, duration: 1800, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        return { mouth, breath };
    }

    update() {
        super.update();
    }
}
