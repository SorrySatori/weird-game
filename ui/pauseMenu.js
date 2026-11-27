/**
 * pauseMenu.js — the in-game menu (ESC) in the main menu's look: the same black band on the left (ui/mainMenuBand.js:
 * entries with their gears and mushrooms, the fungus corner, the mycelium on the acid rule) over the dimmed game, and
 * the same panels sliding out of it: Save (numbered slots; a used one asks for a second click), Load, Settings.
 * It runs in its own scene above the game (PauseMenuScene) so nothing of the game draws over it and the gears turn
 * smoothly (the game's camera rounds to whole pixels). ui/GameMenu.js opens and closes it and does the saving and
 * loading; ESC there steps back from a panel, then closes the menu.
 */
import LanguageSystem from '../systems/LanguageSystem.js';
import { getSetting, setSetting, isFullscreen } from '../systems/GameSettings.js';
import { currentDialogStyle, cycleDialogStyle } from '../utils/dialogLayouts.js';
import { saveLabel, formatSaveDate } from '../utils/menuKit.js';
import { PANEL_SETS, panelSet } from './panelStyle.js';
import { createMainMenuBand, createBandSettings, createBandLoad, ACID, bandHeadStyle, bandSmallStyle } from './mainMenuBand.js';

const BAND_W = 320;                  // wider than the main menu's (no painting to make room for): the labels are longer
const PANEL_W = 470;
const SAVE_SLOTS_MIN = 18;           // the Save panel offers at least three pages of six numbered slots

export class PauseMenuScene extends Phaser.Scene {
    constructor() { super({ key: 'PauseMenuScene' }); }

    create({ menu, panel: reopen, translated }) {
        this.menu = menu;                                  // ui/GameMenu.js
        const game = menu.scene, lang = LanguageSystem.getInstance();
        const t = (key, vars) => lang.t(key, vars);
        this.cameras.main.setRoundPixels(false);
        const { width: W, height: H } = this.scale;

        // the game dimmed behind; a click on it goes nowhere (no walking behind the menu)
        this.add.rectangle(-8, -8, W + 16, H + 16, 0x000000, 0.62).setOrigin(0).setInteractive();

        const items = [
            ['ui.gameMenu.resume', () => menu.hideMenu()],
            ['ui.gameMenu.save', () => this.togglePanel('save')],
            ['ui.gameMenu.load', () => this.togglePanel('load')],
            ['ui.menu.settings', () => this.togglePanel('settings')],
            ['ui.gameMenu.exitToMain', () => menu.exitToMain()]
        ];
        this.band = createMainMenuBand(this, {
            width: BAND_W,
            items: items.map(([key, action]) => ({ label: t(key), action, enabled: true }))
        });
        this.nav = this.band.nav;
        this.panelEntry = { save: 1, load: 2, settings: 3 };
        // the band's heading
        const head = this.add.text(20, 30, t('ui.gameMenu.title'), bandHeadStyle(44)).setDepth(2);   // (the band's theme)
        const px = parseInt(head.style.fontSize, 10);
        if (head.width > BAND_W - 44) head.setFontSize(Math.floor(px * (BAND_W - 44) / head.width));
        this.add.rectangle(20, head.y + head.height + 4, 30, 4, ACID).setOrigin(0, 0.5).setDepth(2);
        // the shortcuts, at the foot of the dimmed game
        this.add.text(W - 16, H - 12, t('ui.gameMenu.shortcuts'), bandSmallStyle(11, '#9a9a9a')).setOrigin(1, 1).setDepth(1.6);

        const panel = { x: BAND_W, w: PANEL_W, onClose: () => this.closePanel() };
        this.panels = {
            settings: createBandSettings(this, panel, {
                t, getSetting, setSetting, isFullscreen,
                languages: lang.supportedLanguages,
                language: () => lang.getLanguage(),
                // as in the main menu: fade out, the game re-made in the new language, the menu back with the settings
                // sliding gently out (GameMenu reopens it after the restart)
                setLanguage: (code) => {
                    lang.setLanguage(code);
                    this.nav.active = false;
                    if (this.panels.settings.panel.nav) this.panels.settings.panel.nav.active = false;
                    this.cameras.main.fadeOut(260, 0, 0, 0);
                    this.cameras.main.once('camerafadeoutcomplete', () => {
                        game.registry.set('reopenGameMenu', 'settings');
                        menu.hideMenu();
                        game.scene.restart();
                    });
                },
                dialogStyle: () => currentDialogStyle(),
                cycleDialogStyle: (dir) => cycleDialogStyle(game, dir),
                panelSet,
                cyclePanelSet: (dir) => {
                    const i = PANEL_SETS.indexOf(panelSet());
                    setSetting('panelSet', PANEL_SETS[(i + dir + PANEL_SETS.length) % PANEL_SETS.length]);
                }
            }),
            save: createBandLoad(this, { ...panel, titleKey: 'ui.saveLoad.saveTitle' }, { t, list: () => this.saveRows() }),
            load: createBandLoad(this, panel, { t, list: () => this.loadRows() })
        };
        this.openPanel = null;
        this.armed = null;
        if (reopen === 'settings') {                       // back after a language change
            if (translated) this.cameras.main.fadeIn(450, 0, 0, 0);
            this.togglePanel('settings', { slow: !!translated });
        }
    }

    /** the Save panel's rows: numbered slots (empty ones too); a used slot armed for overwriting says so */
    saveRows() {
        const lang = LanguageSystem.getInstance();
        const files = this.menu.saveSystem?.listSaveFiles() || [];
        const byName = new Map(files.map(f => [f.name, f]));
        const highest = files.reduce((m, f) => /^save\d+$/.test(f.name) ? Math.max(m, this.menu._saveSlotNumber(f.name)) : m, 0);
        const n = Math.max(SAVE_SLOTS_MIN, Math.ceil((highest + 1) / 6) * 6);
        return Array.from({ length: n }, (_, i) => {
            const name = `save${i + 1}`, file = byName.get(name) || null;
            return {
                name: saveLabel(lang, name).toUpperCase(),
                date: this.armed === name ? lang.t('ui.saveLoad.confirmOverwrite') : file ? formatSaveDate(file, lang.getLanguage()) : lang.t('ui.saveLoad.emptySlot'),
                onLoad: () => this.onSaveSlot(name, !!file)
            };
        });
    }

    /** an empty slot saves at once; a used one asks for a second click */
    onSaveSlot(name, used) {
        if (used && this.armed !== name) { this.armed = name; this.panels.save.refresh(); return; }
        this.armed = null;
        this.menu.saveGame(name).then((ok) => { if (ok && this.sys.isActive()) this.closePanel(); });
    }

    /** the Load panel's rows: the saves, by slot number (the quicksave and the autosave last) */
    loadRows() {
        const lang = LanguageSystem.getInstance();
        const files = (this.menu.saveSystem?.listSaveFiles() || []).slice()
            .sort((a, b) => this.menu._saveSlotNumber(a.name) - this.menu._saveSlotNumber(b.name));
        return files.map(file => ({
            name: saveLabel(lang, file.name).toUpperCase(),
            date: file.error ? '⚠' : formatSaveDate(file, lang.getLanguage()),
            onLoad: () => this.menu.loadGame(file.name)
        }));
    }

    togglePanel(name, { slow = false } = {}) {
        if (this.openPanel === name) { this.closePanel(); return; }
        if (this.openPanel) this.panels[this.openPanel].panel.hide(true);
        this.openPanel = name;
        this.armed = null;
        this.nav.active = false;
        this.band.latch(this.panelEntry[name]);
        const p = this.panels[name];
        if (name === 'settings') { p.panel.show({ slow }); p.refresh(); } else p.show();
    }

    closePanel() {
        if (!this.openPanel) return false;
        const name = this.openPanel;
        this.panels[name].panel.hide();
        this.openPanel = null;
        this.armed = null;
        this.band.latch(null);
        this.nav.active = true;
        this.band.focusEntry(this.panelEntry[name]);
        return true;
    }
}
