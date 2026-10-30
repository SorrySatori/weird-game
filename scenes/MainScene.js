import SaveSystem from '../systems/SaveSystem.js';
import LanguageSystem from '../systems/LanguageSystem.js';

import { fitBackground } from '../utils/fitBackground.js';
import {
    preloadMenuKit, createMenuButton, createMenuPanel, addPanelClose, createMenuIconButton, createSlotRow, MenuNav,
    MENU_COLORS, MENU_FONT, saveLabel, formatSaveDate
} from '../utils/menuKit.js';
import { createSettingsPanel } from '../ui/SettingsPanel.js';

const SLOTS_PER_PAGE = 6;

export default class MainScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MainScene' });
        this.saveSystem = null;
    }

    preload() {
        // Load images
        this.load.image('background', 'assets/images/backgrounds/background.png');
        preloadMenuKit(this);
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

        // Add background — cover-fit (uniform scale, no distortion, bottom-anchored); see utils/fitBackground.js.
        const bg = this.add.image(CX, 300, 'background');
        fitBackground(this, bg);
        // darken the middle column a little so the title and the plaques read over the painting
        const shade = this.add.graphics();
        for (let i = 0; i < 24; i++) {
            const w = 760 - i * 24;
            shade.fillStyle(0x000000, 0.025);
            shade.fillRect(CX - w / 2, 0, w, H);
        }

        this.createAmbientSpores(W, H);

        // Title
        if (!this.anims.exists('menuLogoTurn')) {
            this.anims.create({ key: 'menuLogoTurn', frames: this.anims.generateFrameNumbers('menuLogo', { start: 0, end: 7 }), frameRate: 5, repeat: -1 });
        }
        const LOGO_Y = 118;
        this.add.sprite(CX, LOGO_Y, 'menuLogo', 0).setScale(2).play('menuLogoTurn');
        const logoGlow = this.add.image(CX, LOGO_Y, 'menuLogoGlow').setScale(2)
            .setBlendMode(Phaser.BlendModes.ADD).setTint(MENU_COLORS.glow).setAlpha(0.25);
        this.tweens.add({ targets: logoGlow, alpha: 0.55, duration: 2600, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        this.add.text(CX, 214, this.i18n.t('ui.menu.subtitle'), {
            fontFamily: MENU_FONT, fontSize: '20px', fontStyle: 'italic', color: '#c9b98a',
            stroke: MENU_COLORS.stroke, strokeThickness: 4
        }).setOrigin(0.5);

        // The plaques
        this.mainNav = new MenuNav(this);
        const items = [
            ['ui.menu.startGame', () => this.startNewGame()],
            ['ui.menu.loadGame', () => this.showLoadMenu()],
            ['ui.menu.settings', () => this.showSettings()]
        ];
        // Exit Game — only meaningful in the Electron build (a browser tab has nothing to quit).
        if (/Electron/i.test(navigator.userAgent)) items.push(['ui.menu.exitGame', () => this.exitGame()]);
        const hasSaves = this.saveSystem.listSaveFiles().length > 0;
        items.forEach(([key, action], i) => {
            const b = createMenuButton(this, CX, 300 + i * 66, this.i18n.t(key), action, { variant: i, nav: this.mainNav });
            if (key === 'ui.menu.loadGame' && !hasSaves) b.setEnabled(false);   // nothing to load yet
        });

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
        });
    }

    startNewGame() {
        this.mainNav.active = false;
        this.cameras.main.fadeOut(1000, 0, 0, 0);
        this.cameras.main.once('camerafadeoutcomplete', () => {
            SaveSystem.clearPersistedRegistry(this.registry);   // a new game starts with a clean world
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
                const targetScene = saveData.currentScene || 'GameScene';
                
                this.cameras.main.fadeOut(1000, 0, 0, 0);
                this.cameras.main.once('camerafadeoutcomplete', () => {
                    // Stop music
                    if (this.sceneMusic) {
                        this.sceneMusic.stop();
                    }
                    
                    // Start the scene with loaded data
                    this.scene.start(targetScene, { 
                        loadedPosition: saveData.player.position,
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
