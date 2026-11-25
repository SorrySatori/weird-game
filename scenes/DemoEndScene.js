import LanguageSystem from '../systems/LanguageSystem.js';
import { preloadMainMenuBand, createTopTitle, createMainMenuBand, bandHeadStyle, bandSmallStyle, useTheme, ACID } from '../ui/mainMenuBand.js';
import { openStorePage } from '../utils/demo.js';

const CARD_W = 300;       // the entries' width (wider than the main menu's 264: „Přidat do seznamu přání“ fits)
const ROW = 58;           // one entry with its gap (mainMenuBand.js ROW + GAP)
const css = (c) => '#' + c.toString(16).padStart(6, '0');

/**
 * The end-of-demo card (DEMO_BUILD): shown once, over the paused game, when the player finds the Bishop dead in the
 * bus behind the Scraper (scenes/AbandonedBusScene.js) -- the point where the demo's main line stops. In the main
 * menu's look (ui/mainMenuBand.js: its title on top, its entries alone in the middle): the heading, a thank-you,
 * "Wishlist on Steam", "Keep exploring" (the side quests stay playable) and, in the Electron build, "Exit Game".
 * Launched by CreditsScene (utils/demo.js showDemoEnd() rolls the credits first), whose title sits in the same spot:
 * the card's title appears at once over it, the rest fades in. The scene it covers is resumed on close.
 */
export default class DemoEndScene extends Phaser.Scene {
    constructor() {
        super({ key: 'DemoEndScene' });
    }

    preload() {
        preloadMainMenuBand(this);            // (LoadingScene has loaded it already: only what is missing)
        if (!this.cache.audio.exists('hoverSound')) this.load.audio('hoverSound', 'assets/sounds/hover.wav');
        if (!this.cache.audio.exists('clickSound')) this.load.audio('clickSound', 'assets/sounds/click.mp3');
    }

    create(data) {
        this.from = data?.from || null;
        this.closing = false;
        const t = (k) => LanguageSystem.getInstance().t(k);
        const TH = useTheme();
        const W = this.scale.width, H = this.scale.height, CX = W / 2;
        this.cameras.main.setRoundPixels(false);          // as in the main menu: nothing here is pixel art

        const shade = this.add.rectangle(0, 0, W, H, 0x050806, 0.97).setOrigin(0).setInteractive();   // swallows clicks
        createTopTitle(this, { x: CX, subtitle: t('ui.menu.subtitle') });
        const before = new Set(this.children.list);

        const head = this.add.text(CX, 160, t('ui.demo.end.title'), bandHeadStyle(52)).setOrigin(0.5, 0).setDepth(2);
        const bar = this.add.rectangle(CX, head.y + head.height + 4, 30, 4, ACID).setDepth(2);
        const body = this.add.text(CX, bar.y + 18, t('ui.demo.end.body'), {
            fontFamily: TH.font, fontSize: '16px', color: css(TH.text), align: 'center', lineSpacing: 5,
            stroke: '#0e120f', strokeThickness: 3, wordWrap: { width: 760 }
        }).setOrigin(0.5, 0).setDepth(2);
        const note = this.add.text(CX, H - 12, '', bandSmallStyle(13, css(TH.note))).setOrigin(0.5, 1).setDepth(2);

        const items = [
            { label: t('ui.demo.end.wishlist'), action: () => { openStorePage(); note.setText(t('ui.demo.end.storeOpened')); } },
            { label: t('ui.demo.end.continue'), action: () => this.close() }
        ];
        // Exit Game only in the Electron build, as in the main menu
        if (/Electron/i.test(navigator.userAgent)) items.push({ label: t('ui.menu.exitGame'), action: () => this.exitGame() });
        // the entries under the text, kept clear of the note at the foot (a long text gets a size smaller)
        const room = H - 34 - items.length * ROW;
        for (let fs = 16; body.y + body.height + 24 > room && fs > 14; fs--) body.setFontSize(fs - 1);
        const top = Math.min(Math.round(body.y + body.height + 24), room);
        createMainMenuBand(this, {
            width: CARD_W, items, top: 10, height: 10 + items.length * ROW + 10, bare: true,
            place: { x: Math.round(CX - CARD_W / 2), y: top - 10, depth: 1.62 }
        });
        // nothing focused up front: an Enter still held from the dialog mustn't throw the player into the store
        this.input.keyboard.on('keydown-ESC', () => this.close());

        const rest = this.children.list.filter(o => !before.has(o));
        shade.setAlpha(0);
        rest.forEach(o => o.setAlpha(0));
        this.tweens.add({ targets: shade, alpha: 1, duration: 700, ease: 'Sine.easeOut' });
        this.tweens.add({ targets: rest, alpha: 1, duration: 900, delay: 300, ease: 'Sine.easeOut' });
    }

    /** Quits like the main menu (MainScene.exitGame): the preload's IPC bridge, else closing the window. */
    exitGame() {
        if (this.closing) return;
        this.closing = true;
        this.cameras.main.fadeOut(400, 0, 0, 0);
        this.cameras.main.once('camerafadeoutcomplete', () => {
            if (window.appControl && typeof window.appControl.quit === 'function') window.appControl.quit();
            else window.close();
        });
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
