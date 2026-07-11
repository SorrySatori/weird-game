import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';

export default class ShedAbandonedOfficeScene extends GameScene {
    constructor() {
        super({ key: 'ShedAbandonedOfficeScene' });
        this.isTransitioning = false;
    }

    preload() {
        super.preload();
        this.load.image('office-bg', 'assets/images/backgrounds/ShedAbandonedOffice.png');
        this.load.image('exitArea', 'assets/images/ui/door.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        
        // Set background
        const bg = this.add.image(400, 300, 'office-bg');
        bg.setDisplaySize(800, 600);
        bg.setDepth(-1);
        
        // Set initial priest position
        if (this.priest) {
            this.priest.x = 250;  // Match entrance position from Shed521FloorsScene
            this.priest.y = 520;  // Ground level
            this.priest.setOrigin(0.5, 1);
            this.priest.play('idle');
        }
        this.transitionManager = new SceneTransitionManager(this);

        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            50, // width
            200, // height
            'left', // direction
            'Shed521FloorsScene',
            700, // walk to x
            470, // walk to y
            'Back to the stairs' 
        )

        this.transitionManager.createTransitionZone(
            750, // x position
            470, // y position
            50, // width
            200, // height
            'right', // direction
            'ShedHallScene',
            100, // walk to x
            470, // walk to y
            'To the Hall'
        )

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

        const cx = 430, cy = 320;

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

        this.showNotification('Palinode unsays the brick — a walled tunnel exhales cold air toward the Living Core.');
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
