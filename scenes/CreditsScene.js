import LanguageSystem from '../systems/LanguageSystem.js';
import { MENU_COLORS, MENU_FONT } from '../utils/menuKit.js';

/**
 * CreditsScene, demo cut: the full game's credits scroll (dev: scenes/CreditsScene.js) without "Your ending" and the
 * ending titles (no story leaks). Rolls once at the end of the demo over the paused game (utils/demo.js showDemoEnd),
 * then hands over to the end card (DemoEndScene), which resumes the game on "Keep exploring". The game's sounds are
 * paused, not stopped, so they carry on under the card.
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
        if (!this.cache.audio.exists('creditsMusic')) this.load.audio('creditsMusic', 'assets/sounds/kdyz-brod-je-jeste-daleko.mp3');
    }

    create() {
        const W = this.scale.width;
        const H = this.scale.height;
        const cs = (LanguageSystem.getInstance && LanguageSystem.getInstance().getLanguage() === 'cs');

        this.cameras.main.setBackgroundColor('#05080a');
        this.cameras.main.fadeIn(1200, 0, 0, 0);

        // Credits theme; the game's own sounds wait (paused) for the end card.
        this.pausedSounds = this.sound.getAllPlaying ? this.sound.getAllPlaying() : [];    // NoAudio has none
        this.pausedSounds.forEach((s) => s.pause());
        try {
            this.creditsMusic = this.sound.add('creditsMusic', { loop: true, volume: 0.6 });
            this.creditsMusic.play();
        } catch (e) { /* audio may be unavailable in some environments */ }

        // A soft breathing spore-mote or two behind the text, for atmosphere.
        for (let i = 0; i < 3; i++) {
            const mote = this.add.circle(W * (0.2 + 0.3 * i), H * 0.5, 3, MENU_COLORS.glow, 0.5).setDepth(0);
            this.tweens.add({ targets: mote, alpha: { from: 0.1, to: 0.5 }, y: mote.y - 40, duration: 4000 + i * 800, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        }

        const lines = [    // no blank lead-in (the full game's has one): the title rises right after the fade-in
            'UPPER MORKEZELA',
            '', '',
            cs ? 'hra od' : 'a game by',
            '', '',
            'T E M P U R R A   G A M E S',
            '', '', '',
            cs ? 'Návrh a scénář' : 'Design & Writing',
            'Matěj Antoš',
            '', '',
            cs ? 'Programování' : 'Programming',
            'Matěj Antoš',
            '', '',
            cs ? 'Svět a příběh' : 'World & Lore',
            'Matěj Antoš',
            '', '',
            '', '',
            cs ? 'Hudba' : 'Music',
            'Matěj Antoš',
            'Tomáš Kotásek',
            'Petr Ondráček',
            'Atomic Candy Creeps',
            '', '',
            '', '',
            cs ? 'Grafika a ilustrace' : 'Graphics & Artwork',
            'Matěj Antoš',
            'Martina Strakošová',
            '', '',
            '', '',
            cs ? 'Zvláštní poděkování' : 'Special Thanks',
            cs ? 'Rada Nejvyššího Humenia' : 'The Highest Humenium Council',
            cs ? 'Všem, kdo čekali v Přízračné frontě' : 'Everyone who waited in the Phantom Queue',
            cs ? 'Biskupce' : 'The Bishop',
            '', '',
            cs ? 'Zvláštní zvláštní poděkování' : 'Special Special Thanks',
            cs ? 'Hedvice' : 'Hedvika',
            '', '', '', '', '', ''
        ];

        this.scrollText = this.add.text(W / 2, H + 20, lines.join('\n'), {
            fontFamily: MENU_FONT,
            fontSize: '22px',
            color: MENU_COLORS.text,
            align: 'center',
            lineSpacing: 10,
            stroke: MENU_COLORS.stroke,
            strokeThickness: 3,
            wordWrap: { width: Math.min(560, W - 60) }
        }).setOrigin(0.5, 0).setDepth(2);

        const travel = this.scrollText.height + H + 40;
        this.scrollTween = this.tweens.add({
            targets: this.scrollText,
            y: -this.scrollText.height - 20,
            duration: Math.max(30000, travel * 32),
            ease: 'Linear',
            onComplete: () => this._toEndCard()
        });

        this.skipHint = this.add.text(W - 14, H - 12, cs ? 'Klikni pro přeskočení' : 'Click to skip', {
            fontFamily: MENU_FONT, fontSize: '13px', fontStyle: 'italic', color: MENU_COLORS.dim
        }).setOrigin(1, 1).setDepth(5).setAlpha(0.6);

        // The click / Enter that closed Elphi's dialog mustn't skip the credits: a short grace period, no key repeats.
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

    /** Fade the credits out and lay the end card over them; the game's sounds come back under the card. */
    _toEndCard() {
        if (this._done) return;
        this._done = true;
        if (this.scrollTween) this.scrollTween.stop();
        this.tweens.add({ targets: [this.scrollText, this.skipHint], alpha: 0, duration: 700, ease: 'Sine.easeIn' });
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
