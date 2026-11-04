import LanguageSystem from '../systems/LanguageSystem.js';
import { preloadMenuKit, createMenuButton, MenuNav, MENU_COLORS, MENU_FONT } from '../utils/menuKit.js';
import { openStorePage } from '../utils/demo.js';

/**
 * The end-of-demo card (DEMO_BUILD): shown once, over the paused game, after the first talk with Dr. Elphi -- the
 * point where the demo's main line stops. The title, a thank-you, "Wishlist on Steam" and "Keep exploring" (the side
 * quests stay playable). Launched by utils/demo.js showDemoEnd(); the scene it covers is resumed on close.
 */
export default class DemoEndScene extends Phaser.Scene {
    constructor() {
        super({ key: 'DemoEndScene' });
    }

    preload() {
        preloadMenuKit(this);
        if (!this.textures.exists('menuLogo')) {
            this.load.spritesheet('menuLogo', 'assets/images/ui/menu/menu_logo.png', { frameWidth: 344, frameHeight: 100 });
        }
        if (!this.textures.exists('menuLogoGlow')) this.load.image('menuLogoGlow', 'assets/images/ui/menu/menu_logo_glow.png');
        if (!this.cache.audio.exists('hoverSound')) this.load.audio('hoverSound', 'assets/sounds/hover.wav');
        if (!this.cache.audio.exists('clickSound')) this.load.audio('clickSound', 'assets/sounds/click.mp3');
    }

    create(data) {
        this.from = data?.from || null;
        this.closing = false;
        const t = (k) => LanguageSystem.getInstance().t(k);
        const W = this.scale.width, H = this.scale.height, CX = W / 2;

        const shade = this.add.rectangle(CX, H / 2, W, H, 0x050806, 0.95).setInteractive();   // swallows clicks
        const card = this.add.container(0, 0);

        if (!this.anims.exists('menuLogoTurn')) {
            this.anims.create({ key: 'menuLogoTurn', frames: this.anims.generateFrameNumbers('menuLogo', { start: 0, end: 7 }), frameRate: 5, repeat: -1 });
        }
        const LOGO_Y = 112;
        const logo = this.add.sprite(CX, LOGO_Y, 'menuLogo', 0).setScale(2).play('menuLogoTurn');
        const glow = this.add.image(CX, LOGO_Y, 'menuLogoGlow').setScale(2)
            .setBlendMode(Phaser.BlendModes.ADD).setTint(MENU_COLORS.glow).setAlpha(0.25);
        this.tweens.add({ targets: glow, alpha: 0.55, duration: 2600, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });

        const title = this.add.text(CX, 232, t('ui.demo.end.title'), {
            fontFamily: MENU_FONT, fontSize: '30px', color: MENU_COLORS.title,
            stroke: MENU_COLORS.stroke, strokeThickness: 5
        }).setOrigin(0.5);
        const body = this.add.text(CX, 262, t('ui.demo.end.body'), {
            fontFamily: MENU_FONT, fontSize: '17px', color: MENU_COLORS.text, align: 'center',
            stroke: MENU_COLORS.stroke, strokeThickness: 3, lineSpacing: 4, wordWrap: { width: 720 }
        }).setOrigin(0.5, 0);
        const note = this.add.text(CX, H - 18, '', {
            fontFamily: MENU_FONT, fontSize: '15px', fontStyle: 'italic', color: MENU_COLORS.dim,
            stroke: MENU_COLORS.stroke, strokeThickness: 3
        }).setOrigin(0.5, 1);
        card.add([logo, glow, title, body, note]);

        const nav = new MenuNav(this);
        const top = Math.max(452, body.y + body.height + 46);
        const wishlist = createMenuButton(this, CX, top, t('ui.demo.end.wishlist'), () => {
            openStorePage();
            note.setText(t('ui.demo.end.storeOpened'));
        }, { variant: 0, nav, fontSize: 18 });
        const keep = createMenuButton(this, CX, top + 66, t('ui.demo.end.continue'), () => this.close(), { variant: 1, nav });
        card.add([wishlist.container, keep.container]);
        // nothing focused up front: an Enter still held from the dialog mustn't throw the player into the store
        this.input.keyboard.on('keydown-ESC', () => this.close());

        shade.setAlpha(0);
        card.setAlpha(0);
        this.tweens.add({ targets: shade, alpha: 1, duration: 700, ease: 'Sine.easeOut' });
        this.tweens.add({ targets: card, alpha: 1, duration: 900, delay: 300, ease: 'Sine.easeOut' });
    }

    close() {
        if (this.closing) return;
        this.closing = true;
        this.tweens.add({
            targets: this.children.list, alpha: 0, duration: 400, ease: 'Sine.easeIn',
            onComplete: () => {
                if (this.from && this.scene.isPaused(this.from)) this.scene.resume(this.from);
                this.scene.stop();
            }
        });
    }
}

if (typeof window !== 'undefined') window.DemoEndScene = DemoEndScene;
