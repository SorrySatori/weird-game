import LanguageSystem from '../systems/LanguageSystem.js';
import { preloadMainMenuBand, createTopTitle, useTheme } from '../ui/mainMenuBand.js';

const BG = 0x05080a;
const FADE = { from: 150, to: 215 };      // the names fade out under the title between these y
const SPEED = 31;                         // px a second
const css = (c) => '#' + c.toString(16).padStart(6, '0');

/**
 * CreditsScene, demo cut: the full game's credits scroll (dev: scenes/CreditsScene.js) without "Your ending" and the
 * ending titles (no story leaks). Rolls once at the end of the demo over the paused game (utils/demo.js showDemoEnd),
 * then hands over to the end card (DemoEndScene), which resumes the game on "Keep exploring". The game's sounds are
 * paused, not stopped, so they carry on under the card.
 * In the main menu's look (ui/mainMenuBand.js): its title stays on top while the names rise from below and fade out
 * under it; the roles in the theme's heading face and accent, the names in its UI face, spores drifting up.
 * main.js lists this scene BEFORE DemoEndScene: the card fades in on top of the credits' dark backdrop.
 */
export default class CreditsScene extends Phaser.Scene {
    constructor() {
        super({ key: 'CreditsScene' });
    }

    init(data) {
        this.from = (data && data.from) || null;
        this._done = false;
    }

    preload() {
        preloadMainMenuBand(this);            // (LoadingScene has loaded it already: only what is missing)
        if (!this.cache.audio.exists('creditsMusic')) this.load.audio('creditsMusic', 'assets/sounds/kdyz-brod-je-jeste-daleko.mp3');
    }

    create() {
        const W = this.scale.width;
        const H = this.scale.height;
        const lang = LanguageSystem.getInstance();
        const cs = lang.getLanguage() === 'cs';
        const TH = useTheme();

        this.cameras.main.setRoundPixels(false);          // as in the main menu: nothing here is pixel art
        this.cameras.main.setBackgroundColor(css(BG));
        this.cameras.main.fadeIn(1200, 0, 0, 0);

        // Credits theme; the game's own sounds wait (paused) for the end card.
        this.pausedSounds = this.sound.getAllPlaying ? this.sound.getAllPlaying() : [];    // NoAudio has none
        this.pausedSounds.forEach((s) => s.pause());
        try {
            this.creditsMusic = this.sound.add('creditsMusic', { loop: true, volume: 0.6 });
            this.creditsMusic.play();
        } catch (e) { /* audio may be unavailable in some environments */ }

        // spores drifting up through the dark, like over the menu's painting
        if (!this.textures.exists('creditsSpore')) {
            const tex = this.textures.createCanvas('creditsSpore', 8, 8), c = tex.getContext();
            const g = c.createRadialGradient(4, 4, 0, 4, 4, 4);
            g.addColorStop(0, 'rgba(255,255,255,1)');
            g.addColorStop(1, 'rgba(255,255,255,0)');
            c.fillStyle = g;
            c.fillRect(0, 0, 8, 8);
            tex.refresh();
        }
        this.add.particles(0, 0, 'creditsSpore', {
            x: { min: 0, max: W }, y: H + 10, speedY: { min: -26, max: -12 }, speedX: { min: -8, max: 8 },
            lifespan: 16000, frequency: 420, scale: { min: 0.4, max: 0.9 }, tint: TH.spore,
            alpha: { onEmit: () => 0, onUpdate: (_p, _k, t) => Math.sin(t * Math.PI) * 0.6 }, blendMode: 'ADD'
        }).setDepth(0);

        const role = { fontFamily: TH.head, fontStyle: TH.headBold ? 'bold' : 'normal', fontSize: '15px', color: css(TH.accent), letterSpacing: 3, padding: { y: 4 } };
        const name = { fontFamily: TH.font, fontStyle: 'bold', fontSize: '21px', color: css(TH.text), stroke: '#0e120f', strokeThickness: 3, padding: { y: 2 } };
        const small = { fontFamily: TH.font, fontSize: '15px', color: css(TH.note), padding: { y: 2 } };
        const studio = { ...name, fontFamily: TH.head, fontStyle: TH.headBold ? 'bold' : 'normal', fontSize: '26px', letterSpacing: 4 };
        const S = (head, ...names) => [[head, role, 8], ...names.map((n, i) => [n, name, i === names.length - 1 ? 56 : 6])];
        // [text, style, gap below]; no blank lead-in (the full game's has one): the names rise right after the fade-in
        const lines = [
            [cs ? 'hra od' : 'a game by', small, 6],
            ['TEMPURRA GAMES', studio, 70],
            ...S(cs ? 'Návrh a scénář' : 'Design & Writing', 'Matěj Antoš'),
            ...S(cs ? 'Programování' : 'Programming', 'Matěj Antoš'),
            ...S(cs ? 'Svět a příběh' : 'World & Lore', 'Matěj Antoš'),
            ...S(cs ? 'Hudba' : 'Music', 'Matěj Antoš', 'Tomáš Kotásek', 'Petr Ondráček', 'Atomic Candy Creeps', 'Ciao Miao'),
            ...S(cs ? 'Grafika a ilustrace' : 'Graphics & Artwork', 'Matěj Antoš', 'Martina Strakošová'),
            ...S(cs ? 'Zvláštní poděkování' : 'Special Thanks', cs ? 'Rada Nejvyššího Humenia' : 'The Highest Humenium Council',
                cs ? 'Všem, kdo čekali v Přízračné frontě' : 'Everyone who waited in the Phantom Queue', cs ? 'Biskupce' : 'The Bishop'),
            ...S(cs ? 'Zvláštní zvláštní poděkování' : 'Special Special Thanks', cs ? 'Hedvice' : 'Hedvika')
        ];
        this.roll = this.add.container(W / 2, H + 20).setDepth(1);
        let y = 0;
        for (const [text, style, gap] of lines) {
            const o = this.add.text(0, y, text, { ...style, align: 'center', wordWrap: { width: Math.min(560, W - 60) } }).setOrigin(0.5, 0);
            this.roll.add(o);
            y += o.height + gap;
        }

        // the title stays on top; the names fade out into the dark under it
        const fade = this.textures.exists('creditsFade') ? 'creditsFade' : (() => {
            const tex = this.textures.createCanvas('creditsFade', 4, FADE.to), c = tex.getContext();
            const g = c.createLinearGradient(0, 0, 0, FADE.to);
            const rgb = `${(BG >> 16) & 255},${(BG >> 8) & 255},${BG & 255}`;
            g.addColorStop(0, `rgba(${rgb},1)`);
            g.addColorStop(FADE.from / FADE.to, `rgba(${rgb},1)`);
            g.addColorStop(1, `rgba(${rgb},0)`);
            c.fillStyle = g;
            c.fillRect(0, 0, 4, FADE.to);
            tex.refresh();
            return 'creditsFade';
        })();
        this.add.image(0, 0, fade).setOrigin(0).setDisplaySize(W, FADE.to).setDepth(1.5);
        createTopTitle(this, { x: W / 2, subtitle: lang.t('ui.menu.subtitle') });

        const travel = this.roll.y - (FADE.from - y);
        this.scrollTween = this.tweens.add({
            targets: this.roll,
            y: FADE.from - y,
            duration: Math.max(30000, travel / SPEED * 1000),
            ease: 'Linear',
            onComplete: () => this._toEndCard()
        });

        this.skipHint = this.add.text(W - 14, H - 12, cs ? 'Klikni pro přeskočení' : 'Click to skip', {
            fontFamily: TH.font, fontSize: '13px', color: css(TH.note)
        }).setOrigin(1, 1).setDepth(5).setAlpha(0.6);

        // The click / Enter that closed the last dialog (the priest's words over the Bishop) mustn't skip the credits: a short grace period, no key repeats.
        this.inputReadyAt = this.time.now + 1200;
        const skip = (e) => { if (!e?.repeat) this._advance(); };
        this.input.on('pointerdown', skip);
        if (this.input.keyboard) {
            ['SPACE', 'ENTER', 'ESC'].forEach((k) => this.input.keyboard.on(`keydown-${k}`, skip));
        }
    }

    _advance() {
        if (this.time.now < this.inputReadyAt) return;
        this._toEndCard();
    }

    /** Fade the names out and lay the end card over them (the title stays: the card has it in the same spot); the
     *  game's sounds come back under the card. */
    _toEndCard() {
        if (this._done) return;
        this._done = true;
        if (this.scrollTween) this.scrollTween.stop();
        this.tweens.add({ targets: [this.roll, this.skipHint], alpha: 0, duration: 700, ease: 'Sine.easeIn' });
        const music = this.creditsMusic;
        const back = () => {
            if (music) music.stop();
            this.pausedSounds.forEach((s) => { if (s.isPaused) s.resume(); });
        };
        if (music) this.tweens.add({ targets: music, volume: 0, duration: 900, onComplete: back });
        else back();
        this.time.delayedCall(700, () => {
            this.scene.launch('DemoEndScene', { from: this.from });
            this.time.delayedCall(1600, () => this.scene.stop());    // the card's shade has faded in by then
        });
    }
}

if (typeof window !== 'undefined') {
    window.CreditsScene = CreditsScene;
}

export { CreditsScene };
