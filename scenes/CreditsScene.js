import LanguageSystem from '../systems/LanguageSystem.js';

/**
 * CreditsScene — the real game-over. Reached after the finale epilogue (or the terminal
 * bad ending) inside the Egg Cathedral. Rolls a placeholder credits scroll with a
 * "TEMPURRA GAMES" text logo, then returns to the title (MainScene).
 *
 * PLACEHOLDER: names/roles are stand-ins and the logo is styled text (no art asset yet).
 */
export default class CreditsScene extends Phaser.Scene {
    constructor() {
        super({ key: 'CreditsScene' });
    }

    init(data) {
        this.ending = (data && data.ending) || null;
        this._phase = 'scroll';
        this._done = false;
    }

    preload() {
        this.load.audio('creditsMusic', 'assets/sounds/kdyz-brod-je-jeste-daleko.mp3');
        this.load.image('tempurraLogo', 'assets/images/ui/TempurraLogo.png');
    }

    create() {
        const W = this.scale.width;
        const H = this.scale.height;
        const cs = (LanguageSystem.getInstance && LanguageSystem.getInstance().getLanguage() === 'cs');

        this.cameras.main.setBackgroundColor('#05080a');
        this.cameras.main.fadeIn(1200, 0, 0, 0);

        // Credits theme.
        this.sound.stopAll();
        try {
            this.creditsMusic = this.sound.add('creditsMusic', { loop: true, volume: 0.6 });
            this.creditsMusic.play();
        } catch (e) { /* audio may be unavailable in some environments */ }

        // A soft breathing spore-mote or two behind the text, for atmosphere.
        for (let i = 0; i < 3; i++) {
            const mote = this.add.circle(W * (0.2 + 0.3 * i), H * 0.5, 3, 0x7fff8e, 0.5).setDepth(0);
            this.tweens.add({ targets: mote, alpha: { from: 0.1, to: 0.5 }, y: mote.y - 40, duration: 4000 + i * 800, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        }

        const endingTitle = this._endingTitle(cs);

        const lines = [
            '', '', '', '',
            'UPPER MORKEZELA',
            '', '',
            cs ? '— hra od —' : '— a game by —',
            '', '',
            'T E M P U R R A   G A M E S',
            '', '', '',
            ...(endingTitle ? [cs ? 'Tvůj konec' : 'Your ending', endingTitle, '', '', ''] : []),
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
            cs ? 'Zvláštní poděkování' : 'Special Thanks',
            cs ? 'Sporová rada' : 'The Spore Council',
            cs ? 'Všem, kdo čekali v Přízračné frontě' : 'Everyone who waited in the Phantom Queue',
            cs ? 'Biskupce' : 'The Bishop',
            '', '',
            cs ? 'Zvláštní zvláštní poděkování' : 'Special Special Thanks',
            cs ? 'Hedvice' : 'Hedvika',
            '', '', '', '',
            cs ? 'Děkujeme, že jsi hrál.' : 'Thank you for playing.',
            '', '', '', '', '', ''
        ];

        this.scrollText = this.add.text(W / 2, H + 20, lines.join('\n'), {
            fontFamily: 'serif',
            fontSize: '22px',
            color: '#e8f3ea',
            align: 'center',
            lineSpacing: 10,
            wordWrap: { width: Math.min(560, W - 60) }
        }).setOrigin(0.5, 0).setDepth(2);

        // Give the studio logo line a little more presence.
        // (Kept simple: the whole block is one text object for a smooth scroll.)

        const travel = this.scrollText.height + H + 40;
        this.scrollTween = this.tweens.add({
            targets: this.scrollText,
            y: -this.scrollText.height - 20,
            duration: Math.max(30000, travel * 32),
            ease: 'Linear',
            onComplete: () => this._showEnd(cs)
        });

        this.skipHint = this.add.text(W - 14, H - 12, cs ? 'Klikni pro přeskočení' : 'Click to skip', {
            fontFamily: 'sans-serif', fontSize: '12px', color: '#5f8f6f'
        }).setOrigin(1, 1).setDepth(5).setAlpha(0.6);

        this.input.on('pointerdown', () => this._advance(cs));
        if (this.input.keyboard) {
            this.input.keyboard.on('keydown-SPACE', () => this._advance(cs));
            this.input.keyboard.on('keydown-ENTER', () => this._advance(cs));
        }
    }

    _endingTitle(cs) {
        const map = {
            accept: cs ? 'Nový druh bytosti' : 'A New Kind of Being',
            pact: cs ? 'Nedokončený mír' : 'An Unfinished Peace',
            destroyed: cs ? 'Probuzená pečeť' : 'The Seal Rewoken',
            absorbed: cs ? 'Už ne pouze člověk' : 'No Longer Only Human',
            failed_merge: cs ? 'Hlas ve vejci' : 'The Voice in the Egg'
        };
        return this.ending ? (map[this.ending] || null) : null;
    }

    _advance(cs) {
        if (this._done) return;
        if (this._phase === 'scroll') {
            // Skip straight to the end card.
            if (this.scrollTween) this.scrollTween.stop();
            this._showEnd(cs);
        } else {
            this._finish();
        }
    }

    _showEnd(cs) {
        if (this._phase === 'end') return;
        this._phase = 'end';
        const W = this.scale.width;
        const H = this.scale.height;
        if (this.scrollText) this.scrollText.setVisible(false);
        if (this.skipHint) this.skipHint.setVisible(false);

        const logo = this.add.image(W / 2, H / 2 - 100, 'tempurraLogo').setDepth(3);
        logo.setDisplaySize(140, 140); // 1024×1024 source — scaled down to fit

        this.add.text(W / 2, H / 2 + 20, cs ? '— Konec —' : '— The End —', {
            fontFamily: 'serif', fontSize: '34px', color: '#e8f3ea', align: 'center'
        }).setOrigin(0.5).setDepth(3);

        const prompt = this.add.text(W / 2, H / 2 + 80, cs ? 'Klikni pro návrat do menu' : 'Click to return to the menu', {
            fontFamily: 'sans-serif', fontSize: '14px', color: '#9fc7ab', align: 'center'
        }).setOrigin(0.5).setDepth(3).setAlpha(0.35);
        this.tweens.add({ targets: prompt, alpha: { from: 0.35, to: 0.9 }, duration: 1200, yoyo: true, repeat: -1 });
    }

    _finish() {
        if (this._done) return;
        this._done = true;
        if (this.creditsMusic) {
            this.tweens.add({ targets: this.creditsMusic, volume: 0, duration: 900, onComplete: () => this.creditsMusic.stop() });
        }
        this.cameras.main.fadeOut(900, 0, 0, 0);
        this.time.delayedCall(950, () => this.scene.start('MainScene'));
    }
}

if (typeof window !== 'undefined') {
    window.CreditsScene = CreditsScene;
}

export { CreditsScene };
