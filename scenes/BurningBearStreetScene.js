import { notePlace } from '../utils/places.js';
import GameScene from './GameScene.js';
import SceneTransitionManager from '../utils/SceneTransitionManager.js';
import { preloadGDProps, applyGDBackground, placeGDProps } from '../utils/GDProps.js';

// Animated fire (tools/artgen/burningbear_bg.py): 6-frame loops packed in an atlas whose frames are trimmed against the
// full 1067×600 canvas, so a sprite at (0,0) / origin (0,0) lands exactly where that fire sits in the background.
// Frame names '<fire>_<n>': 'pit' (the fire pit, balanced + decay) and 'b0'..'b9' (the burning bears, decay only).
const FIRE_ATLAS = { balanced: 'bbs_fire_base', decayDominant: 'bbs_fire_decay' };

export default class BurningBearStreetScene extends GameScene {
    constructor() {
        super({ key: 'BurningBearStreetScene' });
        this.isTransitioning = false;
    }

    preload() {
        super.preload();
        this.preloadMusic('streetSong');
        this.load.image('burningBearStreetBg', 'assets/images/backgrounds/BurningBearStreet.png');   // native 1067×600 (redrawn)
        this.load.image('burningBearStreetBg_growth', 'assets/images/backgrounds/BurningBearStreet_growth.png');
        this.load.image('burningBearStreetBg_decay', 'assets/images/backgrounds/BurningBearStreet_decay.png');
        preloadGDProps(this);
        this.load.atlas('bbs_fire_base', 'assets/images/props/bbs_fire_base.png', 'assets/images/props/bbs_fire_base.json');
        this.load.atlas('bbs_fire_decay', 'assets/images/props/bbs_fire_decay.png', 'assets/images/props/bbs_fire_decay.json');
        this.load.image('exitArea', 'assets/images/ui/door.png');
        this.load.image('arrow', 'assets/images/ui/arrow.png');
    }

    create() {
        // Call parent create first to initialize mechanics
        super.create();
        notePlace(this, 'place_burning_bear_street');   // the journal's Places tab, on the first visit
        this.playSceneMusic('streetSong', { resume: true });
        
        // Set scraper background
        const bg = this.add.image(400, 300, 'burningBearStreetBg');
        this.fitBackground(bg);
        bg.setDepth(-1);
        this.applyBearStreetGDState(bg);
        // The background paints its own cobbles and pavements; the generic ground strip would cover them.
        if (this.ground) {
            this.ground.destroy();
            this.ground = null;
        }
        
        // Initialize the scene transition manager
        this.transitionManager = new SceneTransitionManager(this);
        
        
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

        this.transitionManager.createTransitionZone(
            50, // x position
            470, // y position
            80, // width
            200, // height
            'left', // direction
            'ScraperScene', // target scene
            60, // walk to x (into the left archway)
            470 // walk to y
        );

        this.transitionManager.createTransitionZone(
            400, // x position (800-space; the far end of the street, toward the Townhall tower)
            375, // y position — above the fire pit, so clicking the pit doesn't leave the scene
            90, // width
            110, // height
            'up', // direction
            'TownhallScene', // target scene
            400, // walk to x
            470 // walk to y
        );
        
        this.transitionManager.createTransitionZone(
            750, // x position
            470, // y position
            80, // width
            200, // height
            'right', // direction
            'ScreamingCorkScene', // target scene
            745, // walk to x (into the right archway)
            470 // walk to y
        );
    }

    // Growth/Decay: alt background (overgrown street / the bears burning) + scenery props.
    // Decay also gets live fire: flickering glow over every burning bear and the bonfire, and rising embers.
    applyBearStreetGDState(bg) {
        applyGDBackground(this, bg, 'burningBearStreetBg');
        placeGDProps(this, {
            growth: [                                             // flowering bushes by the archways (spring, not mould)
                { prop: 'bush', x: 112, y: 514 },
                { prop: 'bush', x: 962, y: 510, flipX: true, scale: 0.85 }
            ],
            decay: [
                { prop: 'trash', x: 168, y: 514 },
                { prop: 'rubble', x: 905, y: 508 },
                { prop: 'crate', x: 300, y: 470, scale: 0.8 }
            ]
        });
        this.addStreetFires(this.getGDTendency());
    }

    // Animated flames from the fire atlas (pit when balanced; pit + every hanging bear on Decay). On Decay each fire
    // also gets a flickering additive glow and rising embers. Growth: the pit is overgrown, no fire.
    addStreetFires(tendency) {
        const key = FIRE_ATLAS[tendency];
        if (!key || !this.textures.exists(key)) return;
        const tex = this.textures.get(key);
        const fires = [...new Set(tex.getFrameNames().map(n => n.replace(/_\d+$/, '')))];
        fires.forEach((name, i) => {
            const animKey = `${key}_${name}`;
            if (!this.anims.exists(animKey)) {
                const frames = tex.getFrameNames().filter(n => n.startsWith(name + '_')).sort((a, b) => parseInt(a.split('_').pop()) - parseInt(b.split('_').pop()));
                this.anims.create({ key: animKey, frames: frames.map(frame => ({ key, frame })), frameRate: 8, repeat: -1 });
            }
            const sprite = this.add.sprite(0, 0, key, `${name}_0`).setOrigin(0, 0).setDepth(0.55);
            sprite.play({ key: animKey, startFrame: i % 6 });
        });
        if (tendency === 'decayDominant') this.addBurningBearFX(tex, fires);
    }

    addBurningBearFX(tex, fireNames) {
        if (!this.textures.exists('bbs_ember')) {
            const g = this.make.graphics({ x: 0, y: 0, add: false });
            g.fillStyle(0xffffff, 1).fillRect(0, 0, 2, 2);
            g.generateTexture('bbs_ember', 2, 2);
            g.destroy();
        }
        // Glow + embers sit on each fire's trimmed box (spriteSourceSize = where the frame lies on the canvas).
        const fires = fireNames.map(name => {
            const fr = tex.get(`${name}_0`);
            const b = fr.customData?.spriteSourceSize || { x: fr.x, y: fr.y, w: fr.width, h: fr.height };
            return { x: b.x + b.w / 2, y: b.y + b.h * 0.6, w: b.w * 0.9, h: b.h * 0.8, top: b.y + b.h * 0.35 };
        });
        fires.forEach((f, i) => {
            const glow = this.add.graphics().setDepth(0.6).setBlendMode(Phaser.BlendModes.ADD);
            for (let k = 3; k >= 1; k--) {
                glow.fillStyle(0xd9ad52, 0.022);
                glow.fillEllipse(f.x, f.y, f.w * (k + 1) / 2, f.h * (k + 1) / 3);
            }
            this.tweens.add({ targets: glow, alpha: { from: 0.5, to: 1 }, duration: 180 + (i % 4) * 70, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
            this.add.particles(f.x, f.top + 6, 'bbs_ember', {
                x: { min: -f.w * 0.3, max: f.w * 0.3 },
                speedY: { min: -70, max: -25 }, speedX: { min: -14, max: 18 },
                lifespan: { min: 900, max: 1800 }, frequency: 120 + (i % 3) * 60, quantity: 1,
                alpha: { start: 1, end: 0 }, scale: { start: 1, end: 0.4 },
                tint: [0xefcb73, 0xd9ad52, 0xa24a37], blendMode: 'ADD'
            }).setDepth(0.7);
        });
    }

    update() {
        super.update();
    }
}

// Make the scene available globally
if (typeof window !== 'undefined') {
    window.BurningBearStreetScene = BurningBearStreetScene;
}
