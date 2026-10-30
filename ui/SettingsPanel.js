/**
 * SettingsPanel.js - music / sound volume, fullscreen and the language, shared by the main menu and the ESC menu.
 * Values live in systems/GameSettings.js (localStorage); the volumes apply live while the tube is dragged.
 */
import LanguageSystem from '../systems/LanguageSystem.js';
import { getSetting, setSetting, isFullscreen } from '../systems/GameSettings.js';
import {
    createMenuPanel, addPanelClose, createMenuIconButton, createSlider, createToggle, MenuNav, playMenuSound,
    MENU_COLORS, MENU_FONT
} from '../utils/menuKit.js';

const LABEL_X = -208;
const CONTROL_X = 92;
const ROW_Y = [-80, -26, 28, 82];
const ROW_W = 480;

/**
 * @param {{ onClose: () => void, onLanguage: () => void }} handlers
 * @returns {{ panel, nav: MenuNav, refresh: () => void }}
 */
export function createSettingsPanel(scene, x, y, { onClose, onLanguage }) {
    const lang = LanguageSystem.getInstance();
    const panel = createMenuPanel(scene, 'settings', x, y, lang.t('ui.settings.title'));
    addPanelClose(scene, panel, onClose);
    const nav = new MenuNav(scene);
    nav.active = false;

    /** one row: the label + a control; hovering anywhere on the row focuses it */
    const row = (i, labelKey, control, activate) => {
        const label = scene.add.text(LABEL_X, ROW_Y[i], lang.t(labelKey), {
            fontFamily: MENU_FONT, fontSize: '19px', color: MENU_COLORS.text, stroke: MENU_COLORS.stroke, strokeThickness: 4
        }).setOrigin(0, 0.5);
        const zone = scene.add.zone(0, ROW_Y[i], ROW_W, 48).setInteractive({ useHandCursor: true });
        // the focused row: a faint green band and a glowing spore before its label
        const band = scene.add.rectangle(0, ROW_Y[i], ROW_W, 44, MENU_COLORS.glow, 0.08).setVisible(false);
        const marker = scene.add.image(LABEL_X - 16, ROW_Y[i], 'menuSpore').setScale(2)
            .setBlendMode(Phaser.BlendModes.ADD).setVisible(false);
        scene.tweens.add({ targets: marker, alpha: 0.35, duration: 700, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        panel.container.add([zone, band, label, marker]);
        const handle = {
            container: zone, enabled: true,
            setFocus(on) {
                label.setColor(on ? MENU_COLORS.textHover : MENU_COLORS.text);
                marker.setVisible(on);
                band.setVisible(on);
                control.setFocus?.(on);
            },
            activate: () => activate?.(),
            adjust: (dir) => control.adjust?.(dir)
        };
        const focus = () => { if (nav.items[nav.index] !== handle) { nav.focus(handle); playMenuSound(scene, 'hoverSound', 0.5); } };
        zone.on('pointerover', focus);
        zone.on('pointerdown', (pointer, lx, ly, event) => { event?.stopPropagation(); activate?.(); });
        (control.hit || control.image)?.on('pointerover', focus);
        nav.add(handle);
        return handle;
    };

    const music = createSlider(scene, CONTROL_X, ROW_Y[0], getSetting('music'), (v) => setSetting('music', v));
    const sfx = createSlider(scene, CONTROL_X, ROW_Y[1], getSetting('sfx'), (v, final) => {
        setSetting('sfx', v);
        if (final) playMenuSound(scene, 'clickSound');            // hear the new level
    });
    const fullscreen = createToggle(scene, CONTROL_X - 96, ROW_Y[2], getSetting('fullscreen') !== false, (on) => {
        setSetting('fullscreen', on);
        stateText.setText(lang.t(on ? 'ui.settings.on' : 'ui.settings.off'));
    });
    const stateText = scene.add.text(CONTROL_X - 46, ROW_Y[2], lang.t(fullscreen.value ? 'ui.settings.on' : 'ui.settings.off'), {
        fontFamily: MENU_FONT, fontSize: '16px', color: MENU_COLORS.dim
    }).setOrigin(0, 0.5);
    const current = lang.supportedLanguages.find(l => l.code === lang.getLanguage());
    const langText = scene.add.text(CONTROL_X + 104, ROW_Y[3], current ? current.name : '', {
        fontFamily: MENU_FONT, fontSize: '18px', color: MENU_COLORS.title, stroke: MENU_COLORS.stroke, strokeThickness: 4
    }).setOrigin(1, 0.5);
    const langArrow = createMenuIconButton(scene, CONTROL_X + 130, ROW_Y[3], 'right', () => onLanguage?.());
    // rows first: their hover zones must lie under the controls, or they'd swallow the drags and clicks
    row(0, 'ui.settings.music', music);
    row(1, 'ui.settings.sounds', sfx);
    row(2, 'ui.settings.fullscreen', fullscreen, () => fullscreen.toggle());
    row(3, 'ui.settings.language', { setFocus: (on) => langText.setColor(on ? MENU_COLORS.textHover : MENU_COLORS.title) },
        () => { playMenuSound(scene, 'clickSound'); onLanguage?.(); });
    panel.container.add([music.container, sfx.container, fullscreen.image, stateText, langText, langArrow]);

    return {
        panel, nav,
        /** re-read the real state when shown (F11 can change fullscreen behind the setting's back) */
        refresh() {
            music.setValue(getSetting('music'));
            sfx.setValue(getSetting('sfx'));
            isFullscreen().then(on => {
                fullscreen.setValue(on);
                stateText.setText(lang.t(on ? 'ui.settings.on' : 'ui.settings.off'));
            });
        }
    };
}
