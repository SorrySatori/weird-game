import SaveSystem from '../systems/SaveSystem.js';
import { playableScene } from '../utils/demo.js';
import LanguageSystem from '../systems/LanguageSystem.js';

import {
    preloadMenuKit, createMenuButton, createMenuPanel, addPanelClose, createMenuIconButton, createSlotRow, MenuNav,
    MENU_COLORS, MENU_FONT, saveLabel, formatSaveDate
} from '../utils/menuKit.js';
import { createSettingsPanel } from '../ui/SettingsPanel.js';
import { MENU_DESIGNS, preloadMenuDesigns, paintingLayout } from '../ui/menuDesigns.js';
import { PaintingIdleFX } from '../ui/paintingIdleFX.js';

const SLOTS_PER_PAGE = 6;

/**
 * TRIAL: the main menu's designs (L cycles them in the main menu, the choice is remembered; the scene restarts, as
 * a design may lay the painting out differently). 'kit' is the mechano-fungal plaques and pixel logo on soft dark
 * panels; the rest are ui/menuDesigns.js.
 */
const MENU_DESIGN_ORDER = ['bandRight', 'bandLeft', 'bandBottom', 'kit', 'paper', 'cabaret', 'glow', 'slab', 'office', 'glass'];
const DEFAULT_MENU_DESIGN = 'bandRight';
function readMenuDesign() {
    try {
        const d = localStorage.getItem('menuDesign');
        return MENU_DESIGN_ORDER.includes(d) ? d : DEFAULT_MENU_DESIGN;
    } catch (e) { return DEFAULT_MENU_DESIGN; }
}

export default class MainScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MainScene' });
        this.saveSystem = null;
    }

    preload() {
        // Load images
        // Marti's painting (a photo of it straightened by tools/artgen/menu_painting.py): from just above the
        // cathedral's spire to just below the characters' feet, in a thin dark border at the sides; plus the bits
        // that move on it (tools/artgen/menu_painting_band.py; layers.json lists them and says where they go)
        const MP = 'assets/images/backgrounds/menu_painting/';
        this.load.image('menuPainting', MP + 'band.png');
        this.load.once('filecomplete-json-menuPaintingLayers', (key, type, layers) => {
            layers.files.forEach(n => this.load.image('menuPainting_' + n, MP + n + '.png'));
        });
        this.load.json('menuPaintingLayers', MP + 'layers.json');
        preloadMenuKit(this);
        preloadMenuDesigns(this);
        // the title: 8 frames, the gear-O turns (tools/artgen/menu_logo.py)
        this.load.spritesheet('menuLogo', 'assets/images/ui/menu/menu_logo.png', { frameWidth: 344, frameHeight: 100 });
        this.load.image('menuLogoGlow', 'assets/images/ui/menu/menu_logo_glow.png');

        // Load sound assets
        this.load.audio('hoverSound', 'assets/sounds/hover.wav');
        this.load.audio('clickSound', 'assets/sounds/click.mp3');
        this.load.audio('mainMenuMusic', 'assets/sounds/upper-morkezela.mp3');

        // Handle load errors
        this.load.on('loaderror', (fileObj) => {
            console.log('Error loading asset:', fileObj.key);
        });
    }

    create(data) {
        this.i18n = LanguageSystem.getInstance();
        this.langSystem = this.i18n;
        this.saveSystem = new SaveSystem(this);
        const W = this.scale.width, H = this.scale.height, CX = W / 2;

        // the painting, placed as the chosen design lays it out (whole beside a band, or the spire-to-feet band
        // across the screen), on a near-black frame; smooth filtering, as it may be scaled down
        this.menuDesign = readMenuDesign();
        const band = this.cache.json.get('menuPaintingLayers').band;
        const lay = paintingLayout(MENU_DESIGNS[this.menuDesign]?.layout || 'full', W, H, band);
        this.add.rectangle(0, 0, W, H, 0x141312).setOrigin(0);
        this.textures.get('menuPainting').setFilter(Phaser.Textures.FilterMode.LINEAR);
        const bg = this.add.image(lay.x, lay.y, 'menuPainting').setOrigin(0).setScale(lay.scale);
        this.paintingRect = { x: lay.x, y: lay.y, w: band.w * lay.scale, h: band.h * lay.scale };
        this.createPaintingLife(bg);
        this.createAirship(bg);
        this.createAmbientSpores(W, H);

        // the title and the menu: one of the trial designs
        this.mainNav = new MenuNav(this);
        const items = [
            ['ui.menu.startGame', () => this.startNewGame()],
            ['ui.menu.loadGame', () => this.showLoadMenu()],
            ['ui.menu.settings', () => this.showSettings()]
        ];
        // Exit Game — only meaningful in the Electron build (a browser tab has nothing to quit).
        if (/Electron/i.test(navigator.userAgent)) items.push(['ui.menu.exitGame', () => this.exitGame()]);
        const hasSaves = this.saveSystem.listSaveFiles().length > 0;
        this.menuItems = items.map(([key, action]) => ({
            key, action, label: this.i18n.t(key), enabled: !(key === 'ui.menu.loadGame' && !hasSaves)   // nothing to load yet
        }));
        this.menuBg = bg;
        this.buildMenuDesign(this.menuDesign);
        // TRIAL: L cycles the designs (remembered), to compare them in the running game
        this.input.keyboard.on('keydown-L', () => {
            if (!this.mainNav.active) return;
            const next = MENU_DESIGN_ORDER[(MENU_DESIGN_ORDER.indexOf(this.menuDesign) + 1) % MENU_DESIGN_ORDER.length];
            try { localStorage.setItem('menuDesign', next); } catch (e) { /* private window: just this session */ }
            this.scene.restart({ showDesign: true });
        });
        if (data?.showDesign) {
            const name = this.menuDesign === 'kit' ? 'Kit (současný)' : MENU_DESIGNS[this.menuDesign].name;
            const label = this.add.text(12, 10, `${MENU_DESIGN_ORDER.indexOf(this.menuDesign)}: ${name}`, {
                fontFamily: MENU_FONT, fontSize: '16px', color: '#f2ffe6', stroke: '#000', strokeThickness: 4
            }).setDepth(3000);
            this.tweens.add({ targets: label, alpha: 0, delay: 1800, duration: 600 });
        }

        this.createLoadPanel(CX, 330);
        this.settings = createSettingsPanel(this, CX, 330, {
            onClose: () => this.closeModals(),
            onLanguage: () => this.showLanguageModal()
        });
        this.settings.panel.container.setDepth(1000).setVisible(false);
        this.addModalShade(this.settings.panel.container);
        this.createLangPanel(CX, 330);
        // ESC: the language panel steps back to the settings, anything else closes
        this.input.keyboard.on('keydown-ESC', () => {
            if (this.langPanel.container.visible) this.showSettings(); else this.closeModals();
        });
        if (data?.panel === 'settings') this.showSettings();

        if (!this.sceneMusic || !this.sceneMusic.isPlaying) {
            this.sound.stopAll();                                   // never under a track left from a game
            this.sceneMusic = this.sound.add('mainMenuMusic', { loop: true });
            this.sceneMusic.play();
        }

        // Fullscreen is handled at the Electron window level (the app launches fullscreen and the
        // app menu's F11 toggles it). With Scale.FIT the canvas auto-refits, so we must NOT call
        // this.scale.resize() here — that would change the base game size and re-break the layout.
    }

    /**
     * The painting's green airship sets off from its painted spot and drifts right to left across the sky (behind the
     * title and the plaques), then comes round again from the right after a pause.
     */
    createAirship(bg) {
        const W = this.scale.width;
        const sx = bg.scaleX, sy = bg.scaleY;
        // its centre in the painting (layers.json)
        const home = this.cache.json.get('menuPaintingLayers').airship;
        const homeX = bg.x + home.x * sx;
        const homeY = bg.y + home.y * sy;
        const ship = this.airship = this.add.image(homeX, homeY, 'menuPainting_airship').setScale(sx, sy);
        const SPEED = 16;                        // px/s: about a minute across the sky
        const off = ship.displayWidth / 2 + 4;   // fully off screen
        const fly = (fromX) => {
            ship.x = fromX;
            this.tweens.add({
                targets: ship, x: -off, duration: (fromX + off) / SPEED * 1000, ease: 'Linear',
                onComplete: () => this.time.delayedCall(1000, () => fly(W + off))   // a second out of sight, then back from the right
            });
        };
        fly(homeX);
        // and rides the air a little
        this.tweens.add({ targets: ship, y: homeY + 3, duration: 3200, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    }

    /**
     * The painting lives a little. Edgar and Ortolan breathe and shift their weight (each as a whole, a shader warp).
     * Windows in the Scraper go on and off, the cathedral's light turns another colour
     * for a while, a green glow rises among the graves, and the town hall clock's minute hand jumps on a minute.
     * The layers are cut from the painting itself (tools/artgen/menu_painting_band.py) and sit on it pixel for pixel;
     * they go on before the middle-column shade, so it darkens them too.
     */
    createPaintingLife(bg) {
        const L = this.cache.json.get('menuPaintingLayers');
        const sx = bg.scaleX, sy = bg.scaleY, ox = bg.x, oy = bg.y;
        L.files.forEach(n => this.textures.get('menuPainting_' + n).setFilter(Phaser.Textures.FilterMode.LINEAR));
        const layer = (n) => this.add.image(ox + L[n].x * sx, oy + L[n].y * sy, 'menuPainting_' + n).setOrigin(0).setScale(sx, sy);
        const later = (min, max, fn) => this.time.delayedCall(Phaser.Math.Between(min, max), fn);
        const every = (min, max, fn, first = [min, max]) => {
            const go = () => { fn(); later(min, max, go); };
            later(first[0], first[1], go);
        };

        // Edgar and Ortolan breathe and shift their weight, each as a whole (a warp of the painting inside their soft
        // outlines, the feet anchored: ui/paintingIdleFX.js); WebGL only, the canvas renderer just shows them still
        if (this.renderer.pipelines) {
            if (!this.renderer.pipelines.postPipelineClasses.has('PaintingIdleFX')) {
                this.renderer.pipelines.addPostPipeline('PaintingIdleFX', PaintingIdleFX);
            }
            bg.setPostPipeline('PaintingIdleFX');
            const fx = bg.getPostPipeline('PaintingIdleFX');
            fx.weight = this.textures.get('menuPainting_idle_weight').source[0].glTexture;
            fx.band = [L.band.w, L.band.h];
            fx.origin = [ox, oy];
            fx.scale = sx;
            for (const who of ['edgar', 'ortolan']) {
                const g = L.idle[who];
                fx.geo[who] = [g.feetY, g.height, g.centreX, g.halfWidth];
            }
            const start = this.time.now;
            const tick = () => { fx.time = (this.time.now - start) / 1000; };
            this.events.on('update', tick);
            this.events.once('shutdown', () => this.events.off('update', tick));
        }

        // the Scraper: a window's light goes on or off (each patch = that window the other way), now and then with
        // a flicker first
        const windows = L.scraper_windows.map(w => layer(w.name).setVisible(false));
        every(4000, 9000, () => {
            const win = Phaser.Utils.Array.GetRandom(windows);
            const flip = () => win.setVisible(!win.visible);
            flip();
            if (Math.random() < 0.3) {
                this.time.delayedCall(90, flip);
                this.time.delayedCall(170, flip);
            }
        }, [2000, 5000]);

        // the cathedral's light fades to another colour, stays a while and fades back
        const lights = L.cathedral_lights.map(n => layer(n).setAlpha(0));
        every(12000, 22000, () => {
            this.tweens.add({
                targets: Phaser.Utils.Array.GetRandom(lights), alpha: 1, duration: 1600, ease: 'Sine.easeInOut',
                hold: Phaser.Math.Between(3000, 6000), yoyo: true
            });
        }, [5000, 12000]);

        // the graveyard: a mysterious green glow rises from a grave, a few motes drift up from it, and it dies away
        if (!this.textures.exists('menuGraveGlow')) {
            const R = 32, tex = this.textures.createCanvas('menuGraveGlow', R * 2, R * 2), ctx = tex.getContext();
            const g = ctx.createRadialGradient(R, R, 0, R, R, R);
            g.addColorStop(0, 'rgba(255,255,255,1)');
            g.addColorStop(0.35, 'rgba(255,255,255,0.55)');
            g.addColorStop(1, 'rgba(255,255,255,0)');
            ctx.fillStyle = g;
            ctx.fillRect(0, 0, R * 2, R * 2);
            tex.refresh();
        }
        const glow = this.graveGlow = this.add.image(0, 0, 'menuGraveGlow').setBlendMode(Phaser.BlendModes.ADD).setTint(0x7dffa0)
            .setAlpha(0).setScale(1.4 * sx, 0.9 * sy);
        const motes = this.graveMotes = this.add.particles(0, 0, 'menuSpore', {
            emitting: false, lifespan: { min: 1600, max: 2600 }, speedY: { min: -14, max: -6 }, speedX: { min: -3, max: 3 },
            scale: { start: 0.5, end: 0.1 }, alpha: { start: 0.9, end: 0 }, tint: 0x9dffb8, blendMode: 'ADD', frequency: 260,
            emitZone: { type: 'random', source: new Phaser.Geom.Ellipse(0, 0, 18 * sx, 8 * sy) }
        });
        every(7000, 15000, () => {
            const [x, y] = Phaser.Utils.Array.GetRandom(L.glow_spots);
            glow.setPosition(ox + x * sx, oy + y * sy);
            motes.setPosition(glow.x, glow.y);
            const hold = Phaser.Math.Between(1500, 3000);
            this.tweens.add({ targets: glow, alpha: 1, duration: 1400, ease: 'Sine.easeIn', hold, yoyo: true });
            this.time.delayedCall(700, () => motes.start());
            this.time.delayedCall(1400 + hold, () => motes.stop());
        }, [3000, 8000]);

        // the clock: hands about the pivot (smooth filtering, they turn); the minute hand jumps a minute and settles
        const hand = (n) => {
            this.textures.get('menuPainting_' + n).setFilter(Phaser.Textures.FilterMode.LINEAR);
            return this.add.image(ox + L[n].pivotX * sx, oy + L[n].pivotY * sy, 'menuPainting_' + n)
                .setOrigin(L[n].originX, L[n].originY).setScale(sx, sy);
        };
        const minute = hand('clock_minute'), hour = hand('clock_hour');
        const clock = { minutes: 0 };     // tweened as a plain number (angle wraps at 180°, a tween across it would spin)
        every(6000, 11000, () => this.tweens.add({
            targets: clock, minutes: Math.round(clock.minutes) + 1, duration: 260, ease: 'Back.easeOut',
            onUpdate: () => { minute.angle = clock.minutes * 6; hour.angle = clock.minutes * 0.5; }
        }), [3000, 6000]);
    }

    /** a few glowing spores drifting up through the painting */
    createAmbientSpores(W, H) {
        this.add.particles(0, 0, 'menuSpore', {
            x: { min: 0, max: W },
            y: H + 10,
            speedY: { min: -26, max: -12 },
            speedX: { min: -8, max: 8 },
            lifespan: 16000,
            frequency: 380,
            scale: { min: 1, max: 2 },
            alpha: { onEmit: () => 0, onUpdate: (particle, key, t) => Math.sin(t * Math.PI) * 0.7 },
            blendMode: 'ADD'
        }).setDepth(1.5);
    }

    /**
     * Puts up one design's title and menu (removing the previous one). Depths: the painting and its life 0, a design's
     * backing 1-1.9, the spores 1.5, the title and the menu 2+, the modal panels 1000.
     */
    buildMenuDesign(id) {
        this.mainNav.clear();                         // unfocuses the old entries while they still exist
        (this.designTweens || []).forEach(t => t.remove());
        (this.designObjs || []).forEach(o => { this.tweens.killTweensOf(o); o.destroy(); });
        this.designObjs = [];
        this.designTweens = [];
        this.menuDesign = MENU_DESIGN_ORDER.includes(id) ? id : DEFAULT_MENU_DESIGN;
        const W = this.scale.width, H = this.scale.height;
        const ctx = {
            W, H, CX: W / 2, items: this.menuItems, nav: this.mainNav, subtitle: this.i18n.t('ui.menu.subtitle'),
            painting: this.paintingRect,
            add: (o) => { this.designObjs.push(o); return o; },
            loop: (cfg) => { const t = this.tweens.add(cfg); this.designTweens.push(t); return t; }
        };
        if (this.menuDesign === 'kit') this.buildKitDesign(ctx);
        else MENU_DESIGNS[this.menuDesign].build(this, ctx);
    }

    /** the mechano-fungal kit: the pixel logo with its turning gear and the plaques, on soft dark panels */
    buildKitDesign(ctx) {
        const { CX, add } = ctx;
        if (!this.anims.exists('menuLogoTurn')) {
            this.anims.create({ key: 'menuLogoTurn', frames: this.anims.generateFrameNumbers('menuLogo', { start: 0, end: 7 }), frameRate: 5, repeat: -1 });
        }
        const LOGO_Y = 118;
        const logo = add(this.add.sprite(CX, LOGO_Y, 'menuLogo', 0).setScale(2).play('menuLogoTurn').setDepth(2));
        const logoGlow = add(this.add.image(CX, LOGO_Y, 'menuLogoGlow').setScale(2).setDepth(2)
            .setBlendMode(Phaser.BlendModes.ADD).setTint(0xffd27a).setAlpha(0.25));
        ctx.loop({ targets: logoGlow, alpha: 0.55, duration: 2600, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        const subtitle = add(this.add.text(CX, 214, ctx.subtitle, {
            fontFamily: MENU_FONT, fontSize: '20px', fontStyle: 'italic', color: '#efe0ac', stroke: '#000000', strokeThickness: 5
        }).setOrigin(0.5).setDepth(2).setShadow(0, 2, '#000', 4, true, true));
        const buttons = ctx.items.map((item, i) => {
            const b = createMenuButton(this, CX, 300 + i * 66, item.label, item.action, { variant: i, nav: this.mainNav });
            add(b.container.setDepth(2));
            if (!item.enabled) b.setEnabled(false);
            return b;
        });

        // what sets them off the painting (depth 1): soft dark bands behind the title and the plaques, a dark
        // blurred outline round the logo and each plaque, hard drop shadows, a small scrim behind the subtitle
        const back = (o) => add(o.setDepth(1));
        const tex = (key, w, h, paint) => {
            if (!this.textures.exists(key)) {
                const t = this.textures.createCanvas(key, w, h);
                paint(t.getContext(), w, h);
                t.refresh();
                t.setFilter(Phaser.Textures.FilterMode.LINEAR);
            }
            return key;
        };
        const softRect = tex('menuSoftRect', 128, 128, (c, w, h) => {
            const img = c.createImageData(w, h);
            const ramp = (t) => { const u = Math.min(1, Math.min(t, 1 - t) / 0.25); return u * u * (3 - 2 * u); };
            for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
                const i = (y * w + x) * 4;
                img.data[i] = img.data[i + 1] = img.data[i + 2] = 255;
                img.data[i + 3] = Math.round(255 * ramp((x + 0.5) / w) * ramp((y + 0.5) / h));
            }
            c.putImageData(img, 0, 0);
        });
        const softDot = tex('menuSoftDot', 256, 256, (c, w, h) => {
            const g = c.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
            [[0, 1], [0.45, 0.8], [0.75, 0.35], [1, 0]].forEach(([t, a]) => g.addColorStop(t, `rgba(255,255,255,${a})`));
            c.fillStyle = g; c.fillRect(0, 0, w, h);
        });
        const halo = (key, frame, blur) => {
            const f = this.textures.getFrame(key, frame), pad = blur * 3;
            return tex(`menuHalo_${key}_${frame}_${blur}`, f.cutWidth + pad * 2, f.cutHeight + pad * 2, (c, w, h) => {
                c.filter = `blur(${blur}px)`;
                for (let i = 0; i < 3; i++) c.drawImage(f.source.image, f.cutX, f.cutY, f.cutWidth, f.cutHeight, pad, pad, f.cutWidth, f.cutHeight);
                c.filter = 'none';
                c.globalCompositeOperation = 'source-in';
                c.fillStyle = '#000';
                c.fillRect(0, 0, w, h);
            });
        };
        back(this.add.image(CX, 128, softRect).setTint(0x000000).setDisplaySize(900, 250).setAlpha(0.62));
        back(this.add.image(CX + 8, 400, softRect).setTint(0x000000).setDisplaySize(500, 340).setAlpha(0.62));
        back(this.add.image(subtitle.x, subtitle.y + 1, softDot).setTint(0x000000).setDisplaySize(subtitle.width + 90, 44).setAlpha(0.6));
        back(this.add.image(logo.x, logo.y + 2, halo('menuLogo', 0, 5)).setScale(2).setAlpha(0.6));
        const shadow = back(this.add.image(logo.x, logo.y + 4, 'menuLogo', logo.frame.name).setScale(2).setTintFill(0x000000).setAlpha(0.4));
        const follow = (anim, frame) => shadow.setFrame(frame.textureFrame);     // the gear turns in the shadow too
        logo.on('animationupdate', follow);
        shadow.once('destroy', () => logo.off('animationupdate', follow));
        buttons.forEach(b => {
            const p = b.container.list[0], x = b.container.x + p.x, y = b.container.y + p.y;
            back(this.add.image(x, y + 3, halo(p.texture.key, p.frame.name, 4)).setScale(p.scaleX).setAlpha(0.6));
            back(this.add.image(x + 2, y + 5, p.texture.key, p.frame.name).setScale(p.scaleX).setTintFill(0x000000).setAlpha(0.4));
        });
    }

    startNewGame() {
        this.mainNav.active = false;
        this.cameras.main.fadeOut(1000, 0, 0, 0);
        this.cameras.main.once('camerafadeoutcomplete', () => {
            SaveSystem.clearPersistedRegistry(this.registry);   // a new game starts with a clean world (money included)
            this.registry.remove('savedMoney');                  // nor with a purse from a save loaded earlier this session
            this.scene.start('IntroScene');
        });
    }

    // Quits through the preload's IPC bridge; falls back to closing the window, which the
    // main process turns into app.quit() on Linux/Windows.
    exitGame() {
        this.mainNav.active = false;
        this.cameras.main.fadeOut(400, 0, 0, 0);
        this.cameras.main.once('camerafadeoutcomplete', () => {
            if (window.appControl && typeof window.appControl.quit === 'function') {
                window.appControl.quit();
            } else {
                window.close();
            }
        });
    }

    /** a dim layer under a panel; clicking it closes the panel */
    addModalShade(container) {
        const shade = this.add.rectangle(0, 0, this.scale.width * 2, this.scale.height * 2, 0x000000, 0.6).setInteractive();
        shade.on('pointerdown', () => this.closeModals());
        container.addAt(shade, 0);
    }

    createLoadPanel(x, y) {
        this.slotsNav = new MenuNav(this);
        this.slotsNav.active = false;
        this.loadPanel = createMenuPanel(this, 'slots', x, y, this.i18n.t('ui.saveLoad.loadTitle'));
        this.loadPanel.container.setDepth(1000).setVisible(false);
        this.addModalShade(this.loadPanel.container);
        addPanelClose(this, this.loadPanel, () => this.closeModals());
        this.slotRows = this.add.container(0, 0);
        this.noSavesText = this.add.text(0, -20, this.i18n.t('ui.saveLoad.noSaves'), {
            fontFamily: MENU_FONT, fontSize: '20px', color: MENU_COLORS.dim
        }).setOrigin(0.5);
        this.pageText = this.add.text(0, 180, '', { fontFamily: MENU_FONT, fontSize: '16px', color: MENU_COLORS.dim }).setOrigin(0.5);
        this.prevButton = createMenuIconButton(this, -96, 180, 'left', () => { this.loadPage--; this.populateLoadMenu(); });
        this.nextButton = createMenuIconButton(this, 96, 180, 'right', () => { this.loadPage++; this.populateLoadMenu(); });
        this.loadPanel.container.add([this.slotRows, this.noSavesText, this.pageText, this.prevButton, this.nextButton]);
    }

    createLangPanel(x, y) {
        this.langNav = new MenuNav(this);
        this.langNav.active = false;
        this.langPanel = createMenuPanel(this, 'lang', x, y, this.i18n.t('ui.menu.language'));
        this.langPanel.container.setDepth(1000).setVisible(false);
        this.addModalShade(this.langPanel.container);
        addPanelClose(this, this.langPanel, () => this.showSettings());
        const current = this.langSystem.getLanguage();
        this.langSystem.supportedLanguages.forEach((lang, i) => {
            const b = createMenuButton(this, 0, -29 + i * 64, lang.name, () => {
                if (lang.code === current) { this.showSettings(); return; }   // the active language: back to the settings
                this.langSystem.setLanguage(lang.code);
                this.scene.restart({ panel: 'settings' });   // back where the player was, now translated
            }, { variant: i, nav: this.langNav });
            if (lang.code === current) b.setLatched(true);
            this.langPanel.container.add(b.container);
        });
    }

    /**
     * Show the language selection modal
     */
    showLanguageModal() {
        this.closeModals();
        this.mainNav.active = false;
        this.langPanel.container.setVisible(true);
        this.langNav.active = true;
    }

    showSettings() {
        this.closeModals();
        this.mainNav.active = false;
        this.settings.panel.container.setVisible(true);
        this.settings.nav.active = true;
        this.settings.refresh();
    }

    closeModals() {
        this.loadPanel.container.setVisible(false);
        this.langPanel.container.setVisible(false);
        this.settings.panel.container.setVisible(false);
        this.slotsNav.active = false;
        this.langNav.active = false;
        this.settings.nav.active = false;
        this.mainNav.active = true;
    }

    /**
     * Show the load game menu
     */
    showLoadMenu() {
        this.mainNav.active = false;
        this.loadPage = 0;
        this.loadPanel.container.setVisible(true);
        this.slotsNav.active = true;
        this.populateLoadMenu();
    }

    /**
     * Populate the load menu with save files
     */
    populateLoadMenu() {
        this.slotRows.removeAll(true);
        this.slotsNav.clear();
        const files = (window.gameAPI ? this.saveSystem.listSaveFiles() : []).slice();
        // Sort by save-slot number ascending (save1, save2, …) so the list mirrors the numbered save slots;
        // files without a number (the quicksave) sort last.
        const slotNumber = (name) => {
            const match = /(\d+)\s*$/.exec(name || '');
            return match ? parseInt(match[1], 10) : Number.MAX_SAFE_INTEGER;
        };
        files.sort((a, b) => slotNumber(a.name) - slotNumber(b.name));
        const pageCount = Math.max(1, Math.ceil(files.length / SLOTS_PER_PAGE));
        this.loadPage = Math.max(0, Math.min(pageCount - 1, this.loadPage || 0));
        const pageFiles = files.slice(this.loadPage * SLOTS_PER_PAGE, (this.loadPage + 1) * SLOTS_PER_PAGE);

        this.noSavesText.setVisible(pageFiles.length === 0);
        pageFiles.forEach((file, i) => {
            const row = createSlotRow(this, 0, -148 + i * 54, {
                name: saveLabel(this.i18n, file.name),
                date: file.error ? '⚠' : formatSaveDate(file, this.i18n.getLanguage()),
                used: true
            }, () => this.loadGame(file.name), this.slotsNav);
            this.slotRows.add(row.container);
        });
        this.pageText.setText(pageCount > 1 ? this.i18n.t('ui.saveLoad.page', { n: this.loadPage + 1, total: pageCount }) : '');
        this.prevButton.setVisible(this.loadPage > 0);
        this.nextButton.setVisible(this.loadPage < pageCount - 1);
    }

    
    /**
     * Load a saved game
     */
    async loadGame(slotName) {
        try {
            console.log('Loading game from slot:', slotName);
            
            // Use the game API to load the game
            const result = window.gameAPI ? window.gameAPI.loadGame(slotName) : { success: false, error: 'Game API not available' };
            
            if (result.success) {
                const saveData = result.data;
                console.log('Save data loaded:', saveData);
                
                // Store save data in registry for access by other scenes
                this.registry.set('savedData', saveData);
                
                // Store individual system data in registry
                if (saveData.quests) this.registry.set('savedQuests', saveData.quests);
                if (saveData.journal) this.registry.set('savedJournal', saveData.journal);
                if (saveData.symbionts) this.registry.set('savedSymbionts', saveData.symbionts);
                if (saveData.factions) this.registry.set('savedFactions', saveData.factions);
                if (saveData.effects) this.registry.set('savedEffects', saveData.effects);
                if (saveData.spores) this.registry.set('savedSpores', saveData.spores);
                if (saveData.money) this.registry.set('savedMoney', saveData.money);
                if (saveData.inventory) this.registry.set('inventory', saveData.inventory);
                if (saveData.growthDecay) this.registry.set('growthDecayBalance', saveData.growthDecay);
                if (saveData.visitedScenes) this.registry.set('visitedScenes', saveData.visitedScenes);
                if (saveData.usedDialogOptions) this.registry.set('usedDialogOptions', new Map(saveData.usedDialogOptions));
                // Plain registry state (SaveSystem.PERSISTED_REGISTRY_KEYS: dream-queue choices, sold-out shop stock,
                // world flags). Cleared first, so nothing from a game played earlier in this session leaks in.
                SaveSystem.clearPersistedRegistry(this.registry);
                if (saveData.registry) {
                    for (const [key, value] of Object.entries(saveData.registry)) this.registry.set(key, value);
                }
                // one-time effects belong to the loaded playthrough, not to whatever was played before it
                this.registry.set('onceFlags', saveData.registry?.onceFlags || []);
                
                // Start the saved scene
                const savedScene = saveData.currentScene || 'GameScene';
                const targetScene = playableScene(this.scene.manager, savedScene);
                
                this.cameras.main.fadeOut(1000, 0, 0, 0);
                this.cameras.main.once('camerafadeoutcomplete', () => {
                    // Stop music
                    if (this.sceneMusic) {
                        this.sceneMusic.stop();
                    }
                    
                    // Start the scene with loaded data
                    this.scene.start(targetScene, { 
                        loadedPosition: targetScene === savedScene ? saveData.player.position : null,
                        loadedSave: true // Flag to indicate this is a loaded save
                    });
                });
                
                // Show notification
                if (this.showNotification) {
                    this.showNotification('Loading game...', 0x00ff00);
                }
            } else {
                console.error('Failed to load game:', result.error);
                if (this.showNotification) {
                    this.showNotification('Failed to load game: ' + result.error, 0xff0000);
                }
            }
        } catch (error) {
            console.error('Error loading game:', error);
            if (this.showNotification) {
                this.showNotification('Error loading game: ' + error.message, 0xff0000);
            }
        }
    }
}
