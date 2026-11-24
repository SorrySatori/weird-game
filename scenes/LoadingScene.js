import { ITEM_ICONS } from '../utils/itemIcons.js';
import { preloadRecordings } from '../utils/Recordings.js';
import { UI_FONT, UI_SIZE } from '../utils/pixelFrame.js';
import { GRIME_FILES } from '../ui/panelStyle.js';
import { preloadMainMenuBand } from '../ui/mainMenuBand.js';

export default class LoadingScene extends Phaser.Scene {
    constructor() {
        super({ key: 'LoadingScene' });
    }

    preload() {
        // The in-world UI's pixel font (Departure Mono, OFL: assets/fonts/DepartureMono-LICENSE.txt), drawn on an 11 px
        // grid, so it is shown at 22 px: one font pixel = 2x2 screen pixels like the rest of the game (utils/pixelFrame.js)
        this.load.font('Departure Mono', 'assets/fonts/DepartureMono-Regular.otf', 'opentype');
        // the apprentice's handwriting in the panels (ui/panelStyle.js; Caveat, OFL: assets/fonts/Caveat-OFL.txt)
        this.load.font('Caveat', 'assets/fonts/Caveat.ttf', 'truetype', { weight: '400 700' });
        // the apprentice's grubby hand (Mynerve), spray paint on the quest plate (Sedgwick Ave Display), a paint marker
        // (Mansalva); OFL: assets/fonts/*-OFL.txt
        this.load.font('Mynerve', 'assets/fonts/Mynerve-Regular.ttf', 'truetype');
        this.load.font('Sedgwick Ave Display', 'assets/fonts/SedgwickAveDisplay-Regular.ttf', 'truetype');
        this.load.font('Mansalva', 'assets/fonts/Mansalva-Regular.ttf', 'truetype');
        // the system UI's (the menu band: main menu, pause menu, settings, saves)
        preloadMainMenuBand(this);

        // Load the Tempurra logo
        this.load.image('tempurraLogo', 'assets/images/ui/TempurraLogo.png');

        // Load other essential assets needed for MainScene
        this.load.image('background', 'assets/images/backgrounds/background.png');
        this.load.audio('hoverSound', 'assets/sounds/hover.wav');
        this.load.audio('clickSound', 'assets/sounds/click.mp3');

        // Central item-icon registry. Loaded once here so every icon is available game-wide
        // (inventory in any scene, after a save load). An icon not yet drawn simply fails to
        // load and the item falls back to its lettered-circle placeholder — so we quietly
        // ignore load errors for these optional textures.
        const iconKeys = new Set(ITEM_ICONS.map(i => i.key));
        this.load.on('loaderror', (file) => { if (file && iconKeys.has(file.key)) { /* optional icon missing — placeholder is used */ } });
        ITEM_ICONS.forEach(({ key, path }) => this.load.image(key, path));

        // Oltrac drug-trip overlays (systems/EffectsSystem.js). Own *Fx keys: the item icons above own
        // grayOltrac / violetOltrac / amberOltrac, and the drug can be taken in any scene.
        ['gray', 'violet', 'amber'].forEach(c => this.load.image(`${c}OltracFx`, `assets/images/effects/${c}Oltrac.png`));

        // The panels' weathered pixel art (tools/artgen/ui_grime.py; ui/panelStyle.js GRIME), shown at 2x
        GRIME_FILES.forEach(n => this.load.image(`uiGrime_${n}`, `assets/images/ui/grime/${n}.png`));

        // Voxmarket sound ampules — playable from the inventory in any scene.
        preloadRecordings(this);
        
        // Create loading text
        const loadingText = this.add.text(this.scale.width / 2, 400, 'Loading...', {
            fontSize: UI_SIZE,
            fill: '#7fff8e',
            fontFamily: UI_FONT
        });
        loadingText.setOrigin(0.5);
        
        // Add loading progress bar
        const progressBar = this.add.graphics();
        const progressBox = this.add.graphics();
        const cx = this.scale.width / 2; // centre the bar on the (now 1067-wide) canvas
        progressBox.fillStyle(0x0a2712, 0.8);
        progressBox.fillRect(cx - 160, 430, 320, 30);

        // Register loading progress events
        this.load.on('progress', (value) => {
            progressBar.clear();
            progressBar.fillStyle(0x7fff8e, 1);
            progressBar.fillRect(cx - 150, 440, 300 * value, 10);
        });
    }

    create() {
        // Create a dark background
        this.add.rectangle(this.scale.width / 2, this.scale.height / 2, this.scale.width, this.scale.height, 0x000000).setOrigin(0.5);
        
        // Add the Tempurra logo
        const logo = this.add.image(this.scale.width / 2, 300, 'tempurraLogo');
        logo.setScale(0.4);
        
        // Add a subtle glow effect around the logo
        const glow = this.add.graphics();
        glow.fillStyle(0x7fff8e, 0.2);
        glow.fillCircle(this.scale.width / 2, 300, 150);
        glow.setDepth(-1);
        
        // Add pulsating animation to the glow
        this.tweens.add({
            targets: glow,
            alpha: { from: 0.2, to: 0.4 },
            duration: 1500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Add a subtle scale animation to the logo
        this.tweens.add({
            targets: logo,
            scale: { from: 0.4, to: 0.42 },
            duration: 1200,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
        
        // Back from a game (utils/mainMenu.js reloaded the page): straight to the menu, no splash
        let skipSplash = false;
        try { skipSplash = sessionStorage.getItem('skipSplash') === '1'; sessionStorage.removeItem('skipSplash'); } catch (e) { /* no storage */ }
        if (skipSplash) {
            this.scene.start('MainScene');
            return;
        }

        // Display for a few seconds then transition to MainScene
        this.time.delayedCall(3000, () => {
            this.cameras.main.fadeOut(1000, 0, 0, 0);
            this.cameras.main.once('camerafadeoutcomplete', () => {
                this.scene.start('MainScene');
            });
        });
    }
}
