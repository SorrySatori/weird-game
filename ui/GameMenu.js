/**
 * GameMenu.js - In-game menu system triggered by ESC key.
 * Drawn with the menu kit (utils/menuKit.js): the pause panel, one save / load panel, settings (ui/SettingsPanel.js)
 * and the language panel it opens. ESC steps back a panel, then closes the menu; ↑/↓ + Enter work as well as the mouse.
 */
import LanguageSystem from '../systems/LanguageSystem.js';
import { returnToMainMenu } from '../utils/mainMenu.js';
import { createSettingsPanel } from './SettingsPanel.js';
import {
    createMenuButton, createMenuPanel, addPanelClose, createMenuIconButton, createSlotRow, MenuNav,
    MENU_COLORS, MENU_FONT, saveLabel, formatSaveDate
} from '../utils/menuKit.js';

const SLOTS_PER_PAGE = 6;
const ROW_STEP = 54;

export default class GameMenu {
    /**
     * @param {Phaser.Scene} scene - The scene this menu belongs to
     */
    constructor(scene) {
        this.scene = scene;
        this.visible = false;
        this.container = null;
        this.saveSystem = null;
        this.lang = LanguageSystem.getInstance();

        // Create the menu
        this.create();

        // Set up ESC key handling
        this.setupKeyboardControls();
    }

    /**
     * Set up keyboard controls for the menu
     */
    setupKeyboardControls() {
        this.escKey = this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.ESC);
        this.f5Key = this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.F5);
        this.f9Key = this.scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.F9);

        this.onUpdate = () => {
            // ESC: a sub-panel goes back one step (language → settings → pause), otherwise toggle the menu
            if (Phaser.Input.Keyboard.JustDown(this.escKey)) {
                if (this.visible && this.openPanel !== 'pause') {
                    this.showPanel(this.openPanel === 'lang' ? 'settings' : 'pause');
                } else if (this.visible) {
                    this.hideMenu();
                } else {
                    this.showMenu();
                }
            }
            if (Phaser.Input.Keyboard.JustDown(this.f5Key)) this.quickSave();
            if (Phaser.Input.Keyboard.JustDown(this.f9Key)) this.quickLoad();
        };
        this.scene.events.on('update', this.onUpdate);
        // scene instances are re-used: don't leave this menu's listener behind for the next run
        this.scene.events.once('shutdown', () => this.scene.events.off('update', this.onUpdate));
    }

    /**
     * Create the menu elements
     */
    create() {
        const scene = this.scene;
        const W = scene.scale.width, H = scene.scale.height, cx = W / 2;
        this.container = scene.add.container(0, 0).setDepth(1000).setScrollFactor(0);

        // Dim the scene and swallow clicks (no walking behind the menu)
        const bg = scene.add.rectangle(cx, H / 2, W, H, 0x000000, 0.65).setInteractive();
        bg.on('pointerdown', (pointer, lx, ly, event) => event?.stopPropagation());
        this.container.add(bg);

        this.createPausePanel(cx, 282);
        this.createSlotsPanel(cx, 290);
        this.settings = createSettingsPanel(scene, cx, 290, {
            onClose: () => this.showPanel('pause'),
            onLanguage: () => this.showPanel('lang')
        });
        this.container.add(this.settings.panel.container);
        this.createLangPanel(cx, 290);

        // Keyboard shortcut help
        this.helpText = scene.add.text(cx, H - 24, this.lang.t('ui.gameMenu.shortcuts'), {
            fontFamily: MENU_FONT, fontSize: '14px', color: MENU_COLORS.dim, align: 'center'
        }).setOrigin(0.5);
        this.container.add(this.helpText);

        this.container.setVisible(false);
    }

    createPausePanel(x, y) {
        const scene = this.scene;
        this.pauseNav = new MenuNav(scene);
        this.pause = createMenuPanel(scene, 'pause', x, y, this.lang.t('ui.gameMenu.title'));
        addPanelClose(scene, this.pause, () => this.hideMenu());
        const items = [
            ['ui.gameMenu.resume', () => this.hideMenu()],
            ['ui.gameMenu.save', () => this.showSlots('save')],
            ['ui.gameMenu.load', () => this.showSlots('load')],
            ['ui.menu.settings', () => this.showPanel('settings')],
            ['ui.gameMenu.exitToMain', () => returnToMainMenu(this.scene)]   // a clean slate: no old quests/journal/map
        ];
        items.forEach(([key, action], i) => {
            const b = createMenuButton(scene, 0, -124 + i * 64, this.lang.t(key), action, { variant: i, nav: this.pauseNav });
            this.pause.container.add(b.container);
        });
        this.container.add(this.pause.container);
    }

    /** one panel for both saving and loading: six rows per page, arrows, a page counter */
    createSlotsPanel(x, y) {
        const scene = this.scene;
        this.slotsNav = new MenuNav(scene);
        this.slots = createMenuPanel(scene, 'slots', x, y, '');
        addPanelClose(scene, this.slots, () => this.showPanel('pause'));
        this.slotRows = scene.add.container(0, 0);
        this.slots.container.add(this.slotRows);
        this.noSavesText = scene.add.text(0, -20, this.lang.t('ui.saveLoad.noSaves'), {
            fontFamily: MENU_FONT, fontSize: '20px', color: MENU_COLORS.dim, align: 'center'
        }).setOrigin(0.5);
        this.pageText = scene.add.text(0, 180, '', { fontFamily: MENU_FONT, fontSize: '16px', color: MENU_COLORS.dim }).setOrigin(0.5);
        this.prevButton = createMenuIconButton(scene, -96, 180, 'left', () => this.turnPage(-1));
        this.nextButton = createMenuIconButton(scene, 96, 180, 'right', () => this.turnPage(1));
        this.slots.container.add([this.noSavesText, this.pageText, this.prevButton, this.nextButton]);
        this.container.add(this.slots.container);
    }

    createLangPanel(x, y) {
        const scene = this.scene;
        this.langNav = new MenuNav(scene);
        this.langPanel = createMenuPanel(scene, 'lang', x, y, this.lang.t('ui.menu.language'));
        addPanelClose(scene, this.langPanel, () => this.showPanel('settings'));
        const current = this.lang.getLanguage();
        this.lang.supportedLanguages.forEach((l, i) => {
            const b = createMenuButton(scene, 0, -29 + i * 64, l.name, () => {
                if (l.code === current) { this.showPanel('settings'); return; }
                this.lang.setLanguage(l.code);
                this.hideMenu();
                this.scene.scene.restart();             // re-create the scene in the new language
            }, { variant: i, nav: this.langNav });
            if (l.code === current) b.setLatched(true);
            this.langPanel.container.add(b.container);
        });
        this.container.add(this.langPanel.container);
    }

    /** 'pause' | 'slots' | 'settings' | 'lang' */
    showPanel(name) {
        this.openPanel = name;
        this.pause.container.setVisible(name === 'pause');
        this.slots.container.setVisible(name === 'slots');
        this.settings.panel.container.setVisible(name === 'settings');
        this.langPanel.container.setVisible(name === 'lang');
        this.helpText.setVisible(name === 'pause');
        this.pauseNav.active = this.visible && name === 'pause';
        this.slotsNav.active = this.visible && name === 'slots';
        this.settings.nav.active = this.visible && name === 'settings';
        this.langNav.active = this.visible && name === 'lang';
        if (name === 'settings') this.settings.refresh();
    }

    async ensureSaveSystem() {
        if (!this.saveSystem) {
            const module = await import('../systems/SaveSystem.js');
            this.saveSystem = new module.default(this.scene);
        }
        return this.saveSystem;
    }

    /** open the slots panel for 'save' or 'load' */
    async showSlots(mode) {
        this.slotMode = mode;
        this.slotPage = 0;
        this.armedSlot = null;
        this.slots.title.setText(this.lang.t(mode === 'save' ? 'ui.saveLoad.saveTitle' : 'ui.saveLoad.loadTitle'));
        if (!window.gameAPI) {
            this.scene.showNotification(this.lang.t('ui.saveLoad.saveUnavailable'), 0xff0000);
            return;
        }
        await this.ensureSaveSystem();
        this.showPanel('slots');
        this.populateSlots();
    }

    turnPage(step) {
        this.slotPage = Math.max(0, Math.min(this.slotPageCount - 1, this.slotPage + step));
        this.armedSlot = null;
        this.populateSlots();
    }

    /**
     * Extract the numeric slot index from a save name like "save12".
     * Names without a trailing number sort to the end.
     * @param {string} name
     * @returns {number}
     */
    _saveSlotNumber(name) {
        const match = /(\d+)\s*$/.exec(name || '');
        return match ? parseInt(match[1], 10) : Number.MAX_SAFE_INTEGER;
    }

    /** rows for the current page: save = numbered slots (empty ones too), load = the existing saves */
    populateSlots() {
        this.slotRows.removeAll(true);
        this.slotsNav.clear();
        const files = this.saveSystem.listSaveFiles() || [];
        let rows;
        if (this.slotMode === 'save') {
            const byName = new Map(files.map(f => [f.name, f]));
            const highest = files.reduce((m, f) => /^save\d+$/.test(f.name) ? Math.max(m, this._saveSlotNumber(f.name)) : m, 0);
            this.slotPageCount = Math.max(3, Math.ceil((highest + 1) / SLOTS_PER_PAGE));
            rows = Array.from({ length: SLOTS_PER_PAGE }, (_, i) => {
                const name = `save${this.slotPage * SLOTS_PER_PAGE + i + 1}`;
                return { name, file: byName.get(name) || null };
            });
        } else {
            // Sort by save-slot number ascending (save1, save2, …) so the list mirrors the numbered slots.
            const sorted = files.slice().sort((a, b) => this._saveSlotNumber(a.name) - this._saveSlotNumber(b.name));
            this.slotPageCount = Math.max(1, Math.ceil(sorted.length / SLOTS_PER_PAGE));
            this.slotPage = Math.min(this.slotPage, this.slotPageCount - 1);
            rows = sorted.slice(this.slotPage * SLOTS_PER_PAGE, (this.slotPage + 1) * SLOTS_PER_PAGE)
                .map(file => ({ name: file.name, file }));
        }
        this.noSavesText.setVisible(this.slotMode === 'load' && rows.length === 0);
        rows.forEach(({ name, file }, i) => {
            const row = createSlotRow(this.scene, 0, -148 + i * ROW_STEP, {
                name: saveLabel(this.lang, name),
                date: file ? formatSaveDate(file, this.lang.getLanguage()) : this.lang.t('ui.saveLoad.emptySlot'),
                used: !!file
            }, (r) => this.onSlot(name, !!file, r), this.slotsNav);
            this.slotRows.add(row.container);
        });
        this.pageText.setText(this.slotPageCount > 1 ? this.lang.t('ui.saveLoad.page', { n: this.slotPage + 1, total: this.slotPageCount }) : '');
        this.prevButton.setVisible(this.slotPage > 0);
        this.nextButton.setVisible(this.slotPage < this.slotPageCount - 1);
    }

    /** load mode: load it. Save mode: an empty slot saves at once, a used one asks for a second click. */
    onSlot(name, used, row) {
        if (this.slotMode === 'load') { this.loadGame(name); return; }
        if (used && this.armedSlot?.name !== name) {
            if (this.armedSlot) { this.armedSlot.row.setSelected(false); this.armedSlot.row.setNote(null); }
            row.setSelected(true);
            row.setNote(this.lang.t('ui.saveLoad.confirmOverwrite'));
            this.armedSlot = { name, row };
            return;
        }
        this.armedSlot = null;
        this.saveGame(name);
    }

    /**
     * Toggle menu visibility
     * Note: We're not using this method directly anymore, but keeping it for compatibility
     */
    toggleMenu() {
        if (this.visible) this.hideMenu(); else this.showMenu();
    }

    /**
     * Show the menu
     */
    showMenu() {
        // Don't show menu if dialog is visible
        if (this.scene.dialogVisible) return;
        this.visible = true;
        this.container.setVisible(true);
        this.showPanel('pause');
        // Don't pause the scene as it can cause issues -- the overlay swallows clicks and the movement system
        // ignores keys while the menu is open (PlayerMovementSystem.isInteractingWithUI)
    }

    /**
     * Hide the menu
     */
    hideMenu() {
        this.visible = false;
        if (this.container) this.container.setVisible(false);
        [this.pauseNav, this.slotsNav, this.settings?.nav, this.langNav].forEach(n => { if (n) { n.active = false; n.items.forEach(i => i.setFocus(false)); } });
    }

    /**
     * Quick save the current game (F5 key)
     */
    async quickSave() {
        // Don't save if dialog is visible or menu is open
        if (this.scene.dialogVisible || this.visible) {
            return;
        }

        // Check if gameAPI is available
        if (!window.gameAPI) {
            console.error('Game API not available');
            this.scene.showNotification(this.lang.t('ui.saveLoad.saveUnavailable'), 0xff0000);
            return;
        }
        await this.ensureSaveSystem();

        const timeString = new Date().toLocaleTimeString();
        this.scene.showNotification(this.lang.t('ui.saveLoad.savingGame'), 0x7fff8e);

        const result = await this.saveSystem.saveGame('quicksave');
        if (result.success) {
            if (this.scene.sound.get('clickSound')) {
                this.scene.sound.play('clickSound');
            }
            this.scene.showNotification(this.lang.t('ui.saveLoad.gameSaved', { time: timeString }), 0x00ff00);
        } else {
            this.scene.showNotification(this.lang.t('ui.saveLoad.saveFailed', { error: result.message }), 0xff0000);
        }
    }

    /**
     * Save the current game into a slot, then back to the pause panel
     */
    async saveGame(saveName) {
        if (!window.gameAPI) {
            console.error('Game API not available');
            this.scene.showNotification(this.lang.t('ui.saveLoad.saveUnavailable'), 0xff0000);
            return;
        }
        await this.ensureSaveSystem();
        const result = await this.saveSystem.saveGame(saveName);
        if (result.success) {
            this.scene.showNotification(this.lang.t('ui.saveLoad.savedToSlot', { slot: saveLabel(this.lang, saveName) }));
            this.showPanel('pause');
        } else {
            this.scene.showNotification(this.lang.t('ui.saveLoad.saveFailed', { error: result.message }), 0xff0000);
        }
    }

    /**
     * Quick load the most recent quicksave (F9 key)
     */
    async quickLoad() {
        // Don't load if dialog is visible
        if (this.scene.dialogVisible) {
            return;
        }

        if (!window.gameAPI) {
            console.error('Game API not available');
            this.scene.showNotification(this.lang.t('ui.saveLoad.loadUnavailable'), 0xff0000);
            return;
        }

        const saveFiles = window.gameAPI.listSaveFiles();
        const quicksaveExists = saveFiles.success && saveFiles.files.some(file => file.name === 'quicksave');
        if (!quicksaveExists) {
            this.scene.showNotification(this.lang.t('ui.saveLoad.noQuicksave'), 0xff9900);
            return;
        }
        await this.ensureSaveSystem();

        this.scene.showNotification(this.lang.t('ui.saveLoad.loadingQuicksave'), 0x7fff8e);
        const result = await this.saveSystem.loadGame('quicksave');
        if (result.success) {
            if (this.scene.sound.get('clickSound')) {
                this.scene.sound.play('clickSound');
            }
            this.scene.showNotification(this.lang.t('ui.saveLoad.gameLoaded'), 0x00ff00);
            if (this.visible) {
                this.hideMenu();
            }
        } else {
            this.scene.showNotification(this.lang.t('ui.saveLoad.loadFailed', { error: result.message }), 0xff0000);
        }
    }

    /**
     * Load a saved game
     */
    async loadGame(slotName) {
        if (!window.gameAPI) {
            console.error('Game API not available');
            this.scene.showNotification(this.lang.t('ui.saveLoad.saveUnavailable'), 0xff0000);
            return;
        }
        await this.ensureSaveSystem();
        const result = await this.saveSystem.loadGame(slotName);
        if (result.success) {
            this.scene.showNotification(this.lang.t('ui.saveLoad.gameLoaded'));
            this.hideMenu();
        } else {
            this.scene.showNotification(this.lang.t('ui.saveLoad.loadFailed', { error: result.message }), 0xff0000);
        }
    }

    /**
     * Clean up resources
     */
    destroy() {
        this.scene.events.off('update', this.onUpdate);
        [this.pauseNav, this.slotsNav, this.settings?.nav, this.langNav].forEach(n => n?.destroy());
        if (this.container) {
            this.container.destroy(true);
        }
    }

    /**
     * Update the menu (called every frame)
     */
    update() {
        // Nothing to update every frame
    }
}
