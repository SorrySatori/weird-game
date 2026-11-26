import SaveSystem from '../systems/SaveSystem.js';
import { playableScene } from '../utils/demo.js';
import LanguageSystem from '../systems/LanguageSystem.js';

import { preloadMenuKit, saveLabel, formatSaveDate } from '../utils/menuKit.js';
import { getSetting, setSetting, isFullscreen } from '../systems/GameSettings.js';
import { currentDialogStyle, cycleDialogStyle } from '../utils/dialogLayouts.js';
import { preloadMainMenuBand, createMainMenuBand, createBandSettings, createBandLoad, createTopTitle, MENU_THEMES, menuTrials, menuLayout } from '../ui/mainMenuBand.js';
import { PaintingIdleFX } from '../ui/paintingIdleFX.js';
import { PANEL_SETS, panelSet } from '../ui/panelStyle.js';

const SLOTS_PER_PAGE = 6;
const PANEL_W = 470;           // the Load / Settings panels sliding out of the band
const TITLE_X = 457;           // the top title's centre on the painting (band.png px): between the spire and the Scraper
// the menu's layout (menuLayout() 'center'): the painting across the whole screen, only the entries in the middle
const CARD = { w: 264, y: 206, top: 26 };
// the painting at night: a light veil (0.25: the 2026-11-26 scan is lighter than the photos; 0.5 muddied the dark
// repaint) + darker toward the edges, its light left in a few places (fractions of the painting: the Egg Cathedral's shell, the
// green haze over the cemetery, the clock spider, the bear, Edgar; tools/storeart's POOLS)
const NIGHT = { colour: '4,3,14', alpha: 0.25, pools: [[0.17, 0.40, 0.17, 0.30, 1.0], [0.55, 0.30, 0.16, 0.16, 0.55],
    [0.92, 0.50, 0.07, 0.10, 0.7], [0.16, 0.82, 0.07, 0.14, 0.45], [0.89, 0.80, 0.06, 0.15, 0.45]] };

export default class MainScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MainScene' });
        this.saveSystem = null;
    }

    preload() {
        // Marti's painting (a photo of it straightened by tools/artgen/menu_painting.py), whole, plus the bits that
        // move on it (tools/artgen/menu_painting_band.py; layers.json lists them and says where they go)
        const MP = 'assets/images/backgrounds/menu_painting/';
        this.load.image('menuPainting', MP + 'band.png');
        this.load.once('filecomplete-json-menuPaintingLayers', (key, type, layers) => {
            layers.files.forEach(n => this.load.image('menuPainting_' + n, MP + n + '.png'));
        });
        this.load.json('menuPaintingLayers', MP + 'layers.json');
        preloadMenuKit(this);          // menuSpore (the drifting spores) and the kit the game's ESC menu uses
        preloadMainMenuBand(this);

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

        // nothing here is pixel art: no snapping to whole pixels (pixelArt turns it on game-wide; it made turning
        // gears wobble, each corner snapping on its own)
        this.cameras.main.setRoundPixels(false);
        // the painting whole, full height, on the right; the menu band fills the rest on the left
        // (centred layout: the painting across the whole width, cut a little at the top and the foot)
        const center = menuLayout() === 'center';
        const band = this.cache.json.get('menuPaintingLayers').band;
        const scale = center ? W / band.w : H / band.h;
        const bandW = Math.ceil(W - band.w * scale);
        this.textures.get('menuPainting').setFilter(Phaser.Textures.FilterMode.LINEAR);     // it is scaled
        const bg = center
            ? this.add.image(0, Math.round((H - band.h * scale) * 0.45), 'menuPainting').setOrigin(0).setScale(scale)
            : this.add.image(W - band.w * scale, 0, 'menuPainting').setOrigin(0).setScale(scale);
        this.createPaintingLife(bg);
        this.createAirship(bg);
        this.createNight(bg);
        this.createAmbientSpores(W, H);

        const items = [
            ['ui.menu.startGame', () => this.startNewGame()],
            ['ui.menu.loadGame', () => this.togglePanel('load')],
            ['ui.menu.settings', () => this.togglePanel('settings')]
        ];
        // Exit Game — only meaningful in the Electron build (a browser tab has nothing to quit).
        if (/Electron/i.test(navigator.userAgent)) items.push(['ui.menu.exitGame', () => this.exitGame()]);
        const hasSaves = this.saveSystem.listSaveFiles().length > 0;
        createTopTitle(this, { x: center ? CX : bg.x + TITLE_X * scale, subtitle: this.i18n.t('ui.menu.subtitle') });
        const menuItems = items.map(([key, action]) => ({ label: this.i18n.t(key), action, enabled: !(key === 'ui.menu.loadGame' && !hasSaves) }));
        this.menu = center
            ? createMainMenuBand(this, {
                width: CARD.w, items: menuItems, top: CARD.top, height: CARD.top + items.length * 58 + 10, bare: true,
                place: { x: Math.round(CX - CARD.w / 2), y: CARD.y, depth: 1.62 }      // (over the title, under a panel's shade)
            })
            : createMainMenuBand(this, { width: bandW, items: menuItems });
        this.mainNav = this.menu.nav;
        this.panelEntry = { load: 1, settings: 2 };

        const t = (key, vars) => this.i18n.t(key, vars);
        // the panels slide out of the band; with the card in the middle they open in the middle over all of it, dimmed
        const panelAt = center ? { x: Math.round(CX - PANEL_W / 2), w: PANEL_W, shadeAll: true } : { x: bandW, w: PANEL_W };
        this.panels = {
            settings: createBandSettings(this, { ...panelAt, onClose: () => this.closePanel() }, {
                t, getSetting, setSetting, isFullscreen,
                languages: this.langSystem.supportedLanguages,
                language: () => this.langSystem.getLanguage(),
                // fade out, come back translated with the settings sliding gently back out (togglePanel slow)
                setLanguage: (code) => {
                    this.langSystem.setLanguage(code);
                    this.mainNav.active = false;
                    this.panels.settings.panel.nav.active = false;
                    this.cameras.main.fadeOut(260, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => this.scene.restart({ panel: 'settings', translated: true }));
                },
                dialogStyle: () => currentDialogStyle(),
                cycleDialogStyle: (dir) => cycleDialogStyle(this, dir),
                panelSet,
                cyclePanelSet: (dir) => {
                    const i = PANEL_SETS.indexOf(panelSet());
                    setSetting('panelSet', PANEL_SETS[(i + dir + PANEL_SETS.length) % PANEL_SETS.length]);
                }
            }),
            load: createBandLoad(this, { ...panelAt, onClose: () => this.closePanel(), perPage: SLOTS_PER_PAGE }, {
                t, list: () => this.saveList()
            })
        };
        this.openPanel = null;
        this.input.keyboard.on('keydown-ESC', () => this.closePanel());
        // the trial looks (tools/menu_trials/README.md), only in a run from the sources: L cycles the menu's look
        // (ui/mainMenuBand.js THEMES + ui/menuSkins.js), C the layout (band on the left / entries in the middle)
        if (menuTrials()) {
            this.input.keyboard.on('keydown-L', () => {
                if (this.openPanel) return;
                const i = MENU_THEMES.indexOf(getSetting('menuTrialTheme') || 'jungle');
                setSetting('menuTrialTheme', MENU_THEMES[(i + 1) % MENU_THEMES.length]);
                this.scene.restart();
            });
            this.input.keyboard.on('keydown-C', () => {
                if (this.openPanel) return;
                setSetting('menuTrialLayout', menuLayout() === 'center' ? 'band' : 'center');
                this.scene.restart();
            });
        }
        if (data?.panel === 'settings') {
            if (data.translated) this.cameras.main.fadeIn(450, 0, 0, 0);
            this.togglePanel('settings', { slow: !!data.translated });
        }

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

    /**
     * Night over the painting (2026-11-24, the user found it too bright beside the dark menus): a dark veil
     * (NIGHT.alpha, 0.25 over the scan), darker toward the edges, with the light left round
     * a few things (NIGHT.pools). Over the painting's life, under
     * the spores, the title and the menu.
     */
    createNight(bg) {
        const W = this.scale.width, H = this.scale.height;
        const pw = bg.displayWidth, ph = bg.displayHeight;
        const key = `menuNight_${Math.round(bg.x)}_${Math.round(bg.y)}_${Math.round(pw)}`;
        if (!this.textures.exists(key)) {
            const tex = this.textures.createCanvas(key, W, H), c = tex.getContext();
            c.fillStyle = `rgba(${NIGHT.colour},${NIGHT.alpha})`;
            c.fillRect(0, 0, W, H);
            const v = c.createRadialGradient(bg.x + pw * 0.5, bg.y + ph * 0.5, ph * 0.35, bg.x + pw * 0.5, bg.y + ph * 0.5, pw * 0.75);
            v.addColorStop(0, `rgba(${NIGHT.colour},0)`);
            v.addColorStop(1, `rgba(${NIGHT.colour},0.4)`);
            c.fillStyle = v;
            c.fillRect(0, 0, W, H);
            c.globalCompositeOperation = 'destination-out';
            for (const [fx, fy, rx, ry, k] of NIGHT.pools) {
                c.save();
                c.translate(bg.x + fx * pw, bg.y + fy * ph);
                c.scale(rx * pw, ry * ph);
                const g = c.createRadialGradient(0, 0, 0, 0, 0, 1);
                g.addColorStop(0, `rgba(0,0,0,${0.8 * k})`);
                g.addColorStop(1, 'rgba(0,0,0,0)');
                c.fillStyle = g;
                c.beginPath(); c.arc(0, 0, 1, 0, Math.PI * 2); c.fill();
                c.restore();
            }
            tex.refresh();
        }
        this.add.image(0, 0, key).setOrigin(0).setDepth(1.4);
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

    /** open the Load or Settings panel (closing the other); the same entry again closes it */
    togglePanel(name, { slow = false } = {}) {
        if (this.openPanel === name) { this.closePanel(); return; }
        if (this.openPanel) this.panels[this.openPanel].panel.hide(true);
        this.openPanel = name;
        this.mainNav.active = false;
        this.menu.latch(this.panelEntry[name]);
        const p = this.panels[name];
        if (name === 'settings') { p.panel.show({ slow }); p.refresh(); } else p.show();
    }

    closePanel() {
        if (!this.openPanel) return;
        const name = this.openPanel;
        this.panels[name].panel.hide();
        this.openPanel = null;
        this.menu.latch(null);
        this.mainNav.active = true;
        this.menu.focusEntry(this.panelEntry[name]);      // the keys carry on from where the player was
    }

    /** the saves for the Load panel, by slot number (save1, save2, ...; the quicksave last) */
    saveList() {
        const files = (window.gameAPI ? this.saveSystem.listSaveFiles() : []).slice();
        const slotNumber = (name) => {
            const match = /(\d+)\s*$/.exec(name || '');
            return match ? parseInt(match[1], 10) : Number.MAX_SAFE_INTEGER;
        };
        files.sort((a, b) => slotNumber(a.name) - slotNumber(b.name));
        return files.map(file => ({
            name: saveLabel(this.i18n, file.name).toUpperCase(),
            date: file.error ? '⚠' : formatSaveDate(file, this.i18n.getLanguage()),
            onLoad: () => this.loadGame(file.name)
        }));
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
