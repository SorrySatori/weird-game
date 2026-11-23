/**
 * GameMenu.js - the in-game menu (ESC). Drawn by ui/pauseMenu.js (PauseMenuScene) in the main menu's look: the band
 * with Resume / Save / Load / Settings / Main menu and the panels sliding out of it. This class opens and closes it,
 * handles the keys (ESC steps back from a panel, then closes the menu; it first closes an open inventory, shop,
 * journal or quest log; F5 / F9 quick save / load) and does the saving and loading.
 */
import { closeAnyPaperScreen } from './paperKit.js';
import LanguageSystem from '../systems/LanguageSystem.js';
import { returnToMainMenu } from '../utils/mainMenu.js';
import { saveLabel } from '../utils/menuKit.js';
import { PauseMenuScene } from './pauseMenu.js';

export default class GameMenu {
    /**
     * @param {Phaser.Scene} scene - The scene this menu belongs to
     */
    constructor(scene) {
        this.scene = scene;
        this.visible = false;
        this.saveSystem = null;
        this.lang = LanguageSystem.getInstance();
        this.setupKeyboardControls();
        // the menu's scene goes with this one (scene instances are re-used)
        this.scene.events.once('shutdown', () => { if (this.visible) this.hideMenu(); });
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
                if (!this.visible && closeAnyPaperScreen()) {
                    // ESC first closes an open inventory, shop, journal or quest log (ui/paperKit.js)
                } else if (this.visible) {
                    if (!this.menuScene()?.closePanel()) this.hideMenu();    // a panel steps back to the band first
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

    async ensureSaveSystem() {
        if (!this.saveSystem) {
            const module = await import('../systems/SaveSystem.js');
            this.saveSystem = new module.default(this.scene);
        }
        return this.saveSystem;
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
        // the saves are listed by the panels: have the save system ready
        this.ensureSaveSystem().catch(() => {});
        const mgr = this.scene.game.scene;
        if (!mgr.getScene('PauseMenuScene')) mgr.add('PauseMenuScene', PauseMenuScene, false);
        this.scene.scene.launch('PauseMenuScene', { menu: this });
        this.scene.scene.bringToTop('PauseMenuScene');
        // Don't pause the scene as it can cause issues -- the menu's scene swallows clicks and the movement system
        // ignores keys while the menu is open (PlayerMovementSystem.isInteractingWithUI)
    }

    /** the running menu scene, or null */
    menuScene() {
        const s = this.scene.game.scene.getScene('PauseMenuScene');
        return s && s.sys.isActive() ? s : null;
    }

    exitToMain() {
        this.hideMenu();
        returnToMainMenu(this.scene);                // a clean slate: no old quests / journal / map
    }

    /**
     * Hide the menu
     */
    hideMenu() {
        this.visible = false;
        this.scene.scene.stop('PauseMenuScene');
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
     * Save the current game into a slot; resolves true if it worked (the menu then closes its Save panel)
     */
    async saveGame(saveName) {
        if (!window.gameAPI) {
            console.error('Game API not available');
            this.scene.showNotification(this.lang.t('ui.saveLoad.saveUnavailable'), 0xff0000);
            return false;
        }
        await this.ensureSaveSystem();
        const result = await this.saveSystem.saveGame(saveName);
        if (result.success) {
            this.scene.showNotification(this.lang.t('ui.saveLoad.savedToSlot', { slot: saveLabel(this.lang, saveName) }));
            return true;
        }
        this.scene.showNotification(this.lang.t('ui.saveLoad.saveFailed', { error: result.message }), 0xff0000);
        return false;
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
        if (this.visible) this.hideMenu();
    }

    /**
     * Update the menu (called every frame)
     */
    update() {
        // Nothing to update every frame
    }
}
