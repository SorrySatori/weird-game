/**
 * Menu kit — the main menu, the ESC menu and their save / load / language panels share these drawn widgets:
 * enamel plaques in riveted, verdigrised bronze with an iron gear, fungi and mycelium growing over them.
 * Hover (or keyboard focus): the gear turns, a glow pulse runs down the mycelium, the caps light up.
 * Click: the plaque sinks, a puff of spores, then the action. Pixel art shown at 2x.
 * Art: tools/artgen/menu_ui.py (sizes there: BW/BH, BOX, SW/SH, PANELS) → assets/aseprite/UI_Menu*.aseprite →
 * menu_export.lua → assets/images/ui/menu/.
 */
const S = 2;                                   // pixel-art scale
const DIR = 'assets/images/ui/menu/';
const BTN = { w: 192, h: 48, frames: 11 };     // frames per variant: 0 idle, 1-8 hover loop, 9 pressed, 10 disabled
const BTN_VARIANTS = 3;
const SLOT = { w: 228, h: 26 };                // frames 0 idle, 1 hover, 2 pressed, 3 selected; +4 = slot holds a save
const SMALL = { left: 0, right: 3, close: 6 }; // + 0 idle / 1 hover / 2 pressed
const PANEL_MARGIN = 18;
const SLIDER = { w: 136, h: 16, glassX0: 4, glassX1: 132 };   // the glass tube's inside (menu_ui.py GLASS)
/** native inner size of each panel + its title plate (tools/artgen/menu_ui.py PANELS) */
export const MENU_PANELS = { pause: { w: 224, h: 196 }, slots: { w: 256, h: 210 }, lang: { w: 224, h: 108 }, settings: { w: 256, h: 140 } };

export const MENU_COLORS = {
    text: '#dccfa6', textHover: '#f2ffe6', textDisabled: '#77736a', title: '#e2c674',
    glow: 0x7fff8e, stroke: '#050806', dim: '#9fb59a'
};
export const MENU_FONT = 'Georgia';

// the button's clickable plaque (gear included), relative to the sprite centre, and where things sit on it
const BTN_HIT = { w: 358, h: 50 };
const BTN_SPRITE = { x: 7, y: -7 };            // sprite centre relative to the hit-area centre
const BTN_TEXT = { x: 27, y: -1 };             // centre of the free enamel (between the gear and the fungi)
const BTN_SPORES = [{ x: 145, y: -48 }, { x: 187, y: -10 }, { x: 131, y: -45 }];   // where each variant's fungi are

export function preloadMenuKit(scene) {
    scene.load.spritesheet('menuButton', DIR + 'menu_button.png', { frameWidth: BTN.w, frameHeight: BTN.h });
    scene.load.spritesheet('menuButtonGlow', DIR + 'menu_button_glow.png', { frameWidth: BTN.w, frameHeight: BTN.h });
    scene.load.spritesheet('menuSlot', DIR + 'menu_slot.png', { frameWidth: SLOT.w, frameHeight: SLOT.h });
    scene.load.spritesheet('menuSmall', DIR + 'menu_small.png', { frameWidth: 20, frameHeight: 20 });
    scene.load.image('menuSpore', DIR + 'menu_spore.png');
    scene.load.spritesheet('menuSlider', DIR + 'menu_slider.png', { frameWidth: SLIDER.w, frameHeight: SLIDER.h });
    scene.load.image('menuSliderFill', DIR + 'menu_slider_fill.png');
    scene.load.spritesheet('menuKnob', DIR + 'menu_knob.png', { frameWidth: 16, frameHeight: 16 });
    scene.load.spritesheet('menuToggle', DIR + 'menu_toggle.png', { frameWidth: 40, frameHeight: 20 });
    for (const key of Object.keys(MENU_PANELS)) {
        scene.load.image(`menuPanel_${key}`, DIR + `menu_panel_${key}.png`);
        scene.load.image(`menuPanelGlow_${key}`, DIR + `menu_panel_${key}_glow.png`);
    }
}

function ensureAnims(scene) {
    for (let v = 0; v < BTN_VARIANTS; v++) {
        const key = `menuButtonHover${v}`;
        if (scene.anims.exists(key)) continue;
        scene.anims.create({
            key,
            frames: scene.anims.generateFrameNumbers('menuButton', { start: v * BTN.frames + 1, end: v * BTN.frames + 8 }),
            frameRate: 9,
            repeat: -1
        });
    }
}

export function playMenuSound(scene, key, volume = 1) {
    if (scene.cache.audio.exists(key)) scene.sound.play(key, { volume });
}

function textStyle(size, color) {
    return { fontFamily: MENU_FONT, fontSize: `${size}px`, color, stroke: MENU_COLORS.stroke, strokeThickness: 4 };
}

/** depth for things spawned outside the widget's container (spore puffs) */
function rootDepth(obj) {
    let o = obj;
    while (o.parentContainer) o = o.parentContainer;
    return (o.depth || 0) + 1;
}

function sporePuff(scene, container, dx, dy) {
    const m = container.getWorldTransformMatrix();
    const emitter = scene.add.particles(m.tx + dx, m.ty + dy, 'menuSpore', {
        speed: { min: 12, max: 46 },
        angle: { min: 200, max: 340 },
        gravityY: -18,
        lifespan: { min: 600, max: 1100 },
        scale: { start: 2, end: 1 },
        alpha: { start: 1, end: 0 },
        blendMode: 'ADD',
        emitting: false
    }).setDepth(rootDepth(container));
    emitter.explode(14);
    scene.time.delayedCall(1300, () => emitter.destroy());
}

/**
 * The main menu plaque. Returns a handle the keyboard navigation drives the same way the mouse does.
 * @param {{ variant?: number, enabled?: boolean, fontSize?: number, nav?: MenuNav }} opts
 */
export function createMenuButton(scene, x, y, label, onClick, opts = {}) {
    ensureAnims(scene);
    const variant = (opts.variant ?? 0) % BTN_VARIANTS;
    const base = variant * BTN.frames;
    const container = scene.add.container(x, y);
    const sprite = scene.add.sprite(BTN_SPRITE.x, BTN_SPRITE.y, 'menuButton', base).setScale(S);
    const glow = scene.add.image(BTN_SPRITE.x, BTN_SPRITE.y, 'menuButtonGlow', variant)
        .setScale(S).setBlendMode(Phaser.BlendModes.ADD).setTint(MENU_COLORS.glow).setAlpha(0);
    const text = scene.add.text(BTN_TEXT.x, BTN_TEXT.y, label, textStyle(opts.fontSize || 20, MENU_COLORS.text)).setOrigin(0.5);
    container.add([sprite, glow, text]);
    container.setSize(BTN_HIT.w, BTN_HIT.h);

    let focused = false, busy = false, glowTween = null;
    const handle = {
        container, enabled: opts.enabled !== false,
        setFocus(on) {
            if (!handle.enabled || focused === on) return;
            focused = on;
            glowTween?.stop();
            if (on) {
                sprite.play(`menuButtonHover${variant}`);
                text.setColor(MENU_COLORS.textHover).setShadow(0, 0, '#7fff8e', 8, false, true);
                glow.setAlpha(0.15);
                glowTween = scene.tweens.add({ targets: glow, alpha: 0.6, duration: 900, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
            } else {
                sprite.stop(); sprite.setFrame(base);
                text.setColor(MENU_COLORS.text).setShadow(0, 0, '#000', 0);
                glowTween = scene.tweens.add({ targets: glow, alpha: 0, duration: 200 });
            }
        },
        activate() {
            if (!handle.enabled || busy) return;
            busy = true;
            sprite.stop(); sprite.setFrame(base + 9);
            text.y = BTN_TEXT.y + 2;
            playMenuSound(scene, 'clickSound');
            sporePuff(scene, container, BTN_SPORES[variant].x, BTN_SPORES[variant].y);
            scene.time.delayedCall(120, () => {
                busy = false;
                if (!container.active) return;
                text.y = BTN_TEXT.y;
                if (focused) sprite.play(`menuButtonHover${variant}`); else sprite.setFrame(base);
                onClick?.();
            });
        },
        setEnabled(on) {
            if (!on) handle.setFocus(false);
            handle.enabled = on;
            sprite.setFrame(on ? base : base + 10);
            text.setColor(on ? MENU_COLORS.text : MENU_COLORS.textDisabled);
            if (container.input) container.input.cursor = on ? 'pointer' : 'default';
        },
        setLabel(t) { text.setText(t); },
        /** pressed look held (e.g. the language already chosen) */
        setLatched(on) { sprite.stop(); sprite.setFrame(on ? base + 9 : base); text.y = BTN_TEXT.y + (on ? 2 : 0); text.setColor(on ? MENU_COLORS.textHover : MENU_COLORS.text); }
    };
    container.setInteractive({ useHandCursor: true });
    container.on('pointerover', () => {
        if (!handle.enabled) return;
        if (opts.nav) opts.nav.focus(handle); else handle.setFocus(true);
        playMenuSound(scene, 'hoverSound', 0.6);
    });
    container.on('pointerout', () => handle.setFocus(false));
    container.on('pointerdown', (pointer, lx, ly, event) => { event?.stopPropagation(); handle.activate(); });
    handle.setEnabled(handle.enabled);
    opts.nav?.add(handle);
    return handle;
}

/**
 * A panel: bronze frame, title plate, corner gears, fungi; its mycelium breathes (ADD glow).
 * @returns {{ container, title, inner: {left, right, top, bottom}, closeAt: {x, y} }} positions relative to the panel centre
 */
export function createMenuPanel(scene, key, x, y, titleText = '') {
    const { w, h } = MENU_PANELS[key];
    const fullH = h + 2 * PANEL_MARGIN;
    const container = scene.add.container(x, y);
    const img = scene.add.image(0, 0, `menuPanel_${key}`).setScale(S);
    const glow = scene.add.image(0, 0, `menuPanelGlow_${key}`).setScale(S)
        .setBlendMode(Phaser.BlendModes.ADD).setTint(MENU_COLORS.glow).setAlpha(0.3);
    scene.tweens.add({ targets: glow, alpha: 0.6, duration: 2400, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    const plateY = (PANEL_MARGIN + 2 - fullH / 2) * S;
    const title = scene.add.text(0, plateY, titleText, textStyle(17, MENU_COLORS.title)).setOrigin(0.5);
    container.add([img, glow, title]);
    // the panel swallows clicks, so nothing behind it (or the priest) reacts
    const blocker = scene.add.zone(0, 0, w * S, h * S).setInteractive();
    blocker.on('pointerdown', (pointer, lx, ly, event) => event?.stopPropagation());
    container.addAt(blocker, 0);
    return {
        container, title,
        inner: { left: -w, right: w, top: -h + 12 * S, bottom: h - 6 * S },
        closeAt: { x: w + 13 - (w + 2 * PANEL_MARGIN) / 2, y: 22 - fullH / 2 }   // native; scaled below
    };
}

/** the round bronze buttons: 'left' / 'right' arrows and 'close' */
export function createMenuIconButton(scene, x, y, kind, onClick) {
    const base = SMALL[kind];
    const img = scene.add.image(x, y, 'menuSmall', base).setScale(S).setInteractive({ useHandCursor: true });
    img.input.hitArea.setTo(1, 1, 18, 18);
    img.on('pointerover', () => { img.setFrame(base + 1); playMenuSound(scene, 'hoverSound', 0.6); });
    img.on('pointerout', () => img.setFrame(base));
    img.on('pointerdown', (pointer, lx, ly, event) => {
        event?.stopPropagation();
        img.setFrame(base + 2);
        playMenuSound(scene, 'clickSound');
        scene.time.delayedCall(110, () => { if (img.active) { img.setFrame(base + 1); onClick?.(); } });
    });
    return img;
}

/** the X on a panel's top-right corner plate */
export function addPanelClose(scene, panel, onClick) {
    const btn = createMenuIconButton(scene, panel.closeAt.x * S, panel.closeAt.y * S, 'close', onClick);
    panel.container.add(btn);
    return btn;
}

/**
 * A save / load row: porthole (glows when the slot holds a save), name on the left, date on the right.
 * @returns handle with setSelected(bool), setNote(text|null), container
 */
export function createSlotRow(scene, x, y, { name, date, used }, onClick, nav) {
    const base = used ? 4 : 0;
    const container = scene.add.container(x, y);
    const sprite = scene.add.image(0, 0, 'menuSlot', base).setScale(S);
    const nameText = scene.add.text(-170, -1, name, textStyle(18, used ? MENU_COLORS.text : MENU_COLORS.textDisabled)).setOrigin(0, 0.5);
    const dateText = scene.add.text(206, -1, date || '', textStyle(14, MENU_COLORS.dim)).setOrigin(1, 0.5);
    container.add([sprite, nameText, dateText]);
    container.setSize(SLOT.w * S - 8, SLOT.h * S - 8);
    let focused = false, selected = false;
    const frame = () => sprite.setFrame(base + (selected ? 3 : focused ? 1 : 0));
    const handle = {
        container, enabled: true,
        setFocus(on) {
            focused = on; frame();
            nameText.setColor(on || selected ? MENU_COLORS.textHover : used ? MENU_COLORS.text : MENU_COLORS.textDisabled);
        },
        setSelected(on) { selected = on; handle.setFocus(focused); },
        setNote(note) { dateText.setText(note ?? (date || '')).setColor(note ? MENU_COLORS.title : MENU_COLORS.dim); },
        activate() {
            sprite.setFrame(base + 2);
            playMenuSound(scene, 'clickSound');
            scene.time.delayedCall(110, () => { if (container.active) { frame(); onClick?.(handle); } });
        }
    };
    container.setInteractive({ useHandCursor: true });
    container.on('pointerover', () => { if (nav) nav.focus(handle); else handle.setFocus(true); playMenuSound(scene, 'hoverSound', 0.5); });
    container.on('pointerout', () => handle.setFocus(false));
    container.on('pointerdown', (pointer, lx, ly, event) => { event?.stopPropagation(); handle.activate(); });
    nav?.add(handle);
    return handle;
}

/**
 * A glass tube with glowing liquid; the gear knob rolls along it. Drag or click the tube; ←/→ step by 10 %.
 * @param {(value: number, final: boolean) => void} onChange  final = the drag ended (or a key / click step)
 */
export function createSlider(scene, x, y, value, onChange) {
    const container = scene.add.container(x, y);
    const track = scene.add.image(0, 0, 'menuSlider', 0).setScale(S);
    const fill = scene.add.image(0, 0, 'menuSliderFill').setScale(S);
    const knob = scene.add.image(0, 0, 'menuKnob', 0).setScale(S);
    container.add([track, fill, knob]);
    const x0 = (SLIDER.glassX0 - SLIDER.w / 2) * S, x1 = (SLIDER.glassX1 - SLIDER.w / 2) * S;
    let v = value, focused = false, dragging = false;
    const draw = () => {
        const kx = x0 + v * (x1 - x0);
        fill.setCrop(0, 0, SLIDER.glassX0 + v * (SLIDER.glassX1 - SLIDER.glassX0), SLIDER.h);
        knob.x = kx;
        knob.setFrame((Math.floor(kx / 6) % 4 + 4) % 4 + (focused || dragging ? 4 : 0));   // it rolls
        track.setFrame(focused ? 1 : 0);
    };
    const set = (nv, final) => {
        nv = Phaser.Math.Clamp(Math.round(nv * 100) / 100, 0, 1);
        if (nv === v && !final) return;
        v = nv; draw(); onChange?.(v, final);
    };
    const fromPointer = (pointer) => {
        const m = container.getWorldTransformMatrix();
        return (pointer.x - m.tx - x0) / (x1 - x0);
    };
    const hit = scene.add.zone(0, 0, SLIDER.w * S + 16, SLIDER.h * S + 8).setInteractive({ useHandCursor: true });
    container.addAt(hit, 0);
    hit.on('pointerdown', (pointer, lx, ly, event) => {
        event?.stopPropagation();
        dragging = true; set(fromPointer(pointer), false);
    });
    const onMove = (pointer) => { if (dragging) set(fromPointer(pointer), false); };
    const onUp = () => { if (dragging) { dragging = false; draw(); onChange?.(v, true); } };
    scene.input.on('pointermove', onMove);
    scene.input.on('pointerup', onUp);
    scene.input.on('pointerupoutside', onUp);
    container.once('destroy', () => {
        scene.input.off('pointermove', onMove); scene.input.off('pointerup', onUp); scene.input.off('pointerupoutside', onUp);
    });
    draw();
    return {
        container, hit,
        setFocus(on) { focused = on; draw(); },
        adjust(dir) { set(v + dir * 0.1, true); },
        setValue(nv) { v = nv; draw(); },
        get value() { return v; }
    };
}

/** a lever in a bronze slot; the groove fills with light when it's on */
export function createToggle(scene, x, y, on, onChange) {
    const img = scene.add.image(x, y, 'menuToggle', on ? 2 : 0).setScale(S).setInteractive({ useHandCursor: true });
    let state = !!on, focused = false;
    const draw = () => img.setFrame((state ? 2 : 0) + (focused ? 1 : 0));
    const set = (nv) => {
        if (nv === state) return;
        state = nv; draw();
        playMenuSound(scene, 'clickSound');
        onChange?.(state);
    };
    img.on('pointerdown', (pointer, lx, ly, event) => { event?.stopPropagation(); set(!state); });
    return {
        image: img,
        setFocus(f) { focused = f; draw(); },
        toggle() { set(!state); },
        adjust(dir) { set(dir > 0); },
        setValue(nv) { state = !!nv; draw(); },
        get value() { return state; }
    };
}

/** "save3" → "Save 3" / "Uložení 3", "quicksave" → "Quicksave" / "Rychlé uložení" */
export function saveLabel(lang, name) {
    if (name === 'quicksave') return lang.t('ui.saveLoad.quicksave');
    const m = /^save(\d+)$/.exec(name || '');
    return m ? lang.t('ui.saveLoad.slotName', { n: m[1] }) : name;
}

/** the save's date in the game's language (cs: 30. 10. 2026 10:13) */
export function formatSaveDate(file, langCode = 'en') {
    const d = new Date(file?.date);
    if (isNaN(d.getTime())) return file?.displayDate || '';
    const locale = langCode === 'cs' ? 'cs-CZ' : 'en-GB';
    return `${d.toLocaleDateString(locale)} ${d.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' })}`;
}

/**
 * Keyboard navigation over a list of widget handles: ↑/↓ (or W/S) move the focus, Enter / Space activate.
 * Mouse hover moves the same focus, so the two never disagree. Only reacts while `active`.
 */
export class MenuNav {
    constructor(scene) {
        this.scene = scene;
        this.items = [];
        this.index = -1;
        this.active = true;
        this.onKey = (event) => this.handleKey(event);
        scene.input.keyboard.on('keydown', this.onKey);
        scene.events.once('shutdown', () => this.destroy());
    }

    add(item) { this.items.push(item); }

    clear() {
        this.items.forEach(i => i.setFocus?.(false));
        this.items = [];
        this.index = -1;
    }

    focus(item) {
        this.index = this.items.indexOf(item);
        this.items.forEach(i => { if (i !== item) i.setFocus(false); });
        item?.setFocus(true);
    }

    move(step) {
        const n = this.items.length;
        if (!n) return;
        let i = this.index;
        for (let k = 0; k < n; k++) {
            i = i < 0 ? (step > 0 ? 0 : n - 1) : (i + step + n) % n;
            if (this.items[i].enabled !== false && this.items[i].container?.visible !== false) {
                this.focus(this.items[i]);
                playMenuSound(this.scene, 'hoverSound', 0.6);
                return;
            }
        }
    }

    handleKey(event) {
        if (!this.active || !this.items.length) return;
        switch (event.code) {
            case 'ArrowDown': case 'KeyS': this.move(1); break;
            case 'ArrowUp': case 'KeyW': this.move(-1); break;
            case 'Enter': case 'NumpadEnter': case 'Space':
                if (this.index >= 0) this.items[this.index].activate();
                break;
            case 'ArrowLeft': case 'KeyA': if (this.index >= 0) this.items[this.index].adjust?.(-1); break;
            case 'ArrowRight': case 'KeyD': if (this.index >= 0) this.items[this.index].adjust?.(1); break;
        }
    }

    destroy() {
        this.scene.input?.keyboard?.off('keydown', this.onKey);
        this.items = [];
    }
}
