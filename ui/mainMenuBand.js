/**
 * mainMenuBand.js — the main menu: a black band on the left of Marti's painting (which is shown whole beside it),
 * Brutal type (Bebas Neue, Space Grotesk, acid yellow) with the mechano-fungal life of the old menu redrawn flat:
 *
 *   - the title sits on top of the painting (createTopTitle), its O a gear that turns slowly
 *   - each entry has a small gear that spins while it is focused; little mushrooms sprout on the focused entry
 *     and glow; a click sends a pulse down the acid rule into the fungus garden and puffs spores
 *   - at the foot of the band: a basket stinkhorn with its flies and glowing mycenas in the left corner, a clump of
 *     little glowing mushrooms breathing spores on the right (createFungusGarden); mycelium creeps along the rule
 *
 * MainScene turns the camera's roundPixels off (the game's pixelArt sets it): each corner of a turning sprite
 * snapped to whole pixels on its own made the gears wobble.
 *
 * The Load and Settings panels slide out of the band over the painting (createBandPanel and the two builders).
 * Everything is drawn on canvases (white, tinted), crisp at any filtering. Keys: ↑/↓ (W/S) move, Enter/Space use,
 * ←/→ (A/D) adjust a slider or a choice, ESC closes a panel (MainScene).
 *
 * Fonts: assets/fonts/BebasNeue.ttf, SpaceGrotesk.ttf (OFL, the licences next to them); both have full Czech.
 *
 * THE LOOK (picked 2026-11-24): the skin 'jungle' (Městská džungle, ui/menuSkins.js) with the entries alone in the
 * middle of the painting (menuLayout() 'center'). The other looks below stay for a quick look back: in a run from the
 * sources (not the packaged game, menuTrials()) MainScene's L key cycles them and C the layout, remembered in the
 * settings 'menuTrialTheme' / 'menuTrialLayout'; stills of all of them: tools/menu_trials/README.md.
 *
 * The looks tried on 2026-11-24 ('menuTrialTheme'): 'brutal' (all of the above) or 'vitraz',
 * the same layout dressed as the Egg Cathedral's stained glass, after the trial design Marti liked (tools/menu_trials):
 * a dim glass band with a gold came for the rule, the entries as glass panes (amber / teal / rose / violet) that light
 * up, the title on a violet glass plate (UnifrakturMaguntia + Cinzel, both OFL in assets/fonts), the garden's
 * mushrooms in the glass colours. And 'glow', after the trial's Bioluminiscence: neon cyan and magenta on deep
 * indigo, no panes, the entries glowing type (Comfortaa), the title MORKEZELA in Monoton, the rule a neon tube.
 * Every create* reads the theme first (useTheme), so the pause menu follows it too. One display face for the title,
 * one face for everything else, in every theme. And four skins drawn as art (ui/menuSkins.js, the art from
 * tools/artgen/menu_skins.py): 'rust', 'biomech', 'jungle', 'crazy', 'tripe', 'panelak'.
 */
import { MenuNav, playMenuSound } from '../utils/menuKit.js';
import { getSetting } from '../systems/GameSettings.js';
import { SKINS } from './menuSkins.js';

export const RULE = 4;
const DEPTH = { title: 1.6, shade: 1.65, panel: 1.7, band: 1.8, ui: 2 };   // the title under a panel's shade

const css = (n) => '#' + n.toString(16).padStart(6, '0');
// the looks: accent (rules, focus, gears), backgrounds, text colours, fonts, the garden's colours
const THEMES = {
    brutal: {
        accent: 0xe6ff2e, bg: 0x000000, onFill: 0xe6ff2e, onText: '#000000', onIcon: 0x000000,
        text: 0xffffff, dim: 0x505050, note: 0x8f8f8f, rowBand: 0x161616, track: 0x4a4a4a, off: 0x6a6a6a,
        font: 'Space Grotesk', head: 'Bebas Neue', headBold: false, headScale: 1, labelPx: 19, rowPx: 16, smallSpacing: 4,
        thread: 0xe6ff2e, garden: [0xe6ff2e], glow: 0xe6ff2e, spore: 0xe6ff2e, basket: 0xe6ff2e, mycena: 0xe6ff2e
    },
    vitraz: {
        glass: true,
        accent: 0xe2b448, bg: 0x17121f, onFill: 0x55308a, onText: '#ffd86b', onIcon: 0xffd86b,
        text: 0xfff6dc, dim: 0x7a7286, note: 0xb5a9c7, rowBand: 0x2b2139, track: 0x4a4258, off: 0x6b6478,
        font: 'Cinzel', head: 'Cinzel', headBold: true, headScale: 0.62, labelPx: 17, rowPx: 15, smallSpacing: 3,
        thread: 0xb98fff, garden: [0xf0b23c, 0x3cb4aa, 0xd2577f, 0x9a6ad6], glow: 0xffc86a, spore: 0xffd86b,
        basket: 0xd2577f, mycena: 0x5fd6c8
    },
    glow: {
        neon: true,
        accent: 0x5ef2ff, bg: 0x0d0826, onFill: 0x251b58, onText: '#9ffaff', onIcon: 0x5ef2ff,
        text: 0xddd2ff, dim: 0x6b6294, note: 0xa497d6, rowBand: 0x1b1344, track: 0x3a3170, off: 0x5a5288,
        font: 'Comfortaa', head: 'Comfortaa', headBold: true, headScale: 0.6, labelPx: 19, rowPx: 15, smallSpacing: 3,
        thread: 0x5ef2ff, garden: [0x5ef2ff, 0xff4fd8, 0x9d7bff], glow: 0x5ef2ff, spore: 0x9ffaff,
        basket: 0xff4fd8, mycena: 0x5ef2ff
    },
    // the skins drawn as art by tools/artgen/menu_skins.py (ui/menuSkins.js): jungle (the menu) + the other trials
    ...Object.fromEntries(Object.entries(SKINS).map(([id, skin]) => [id, { ...skin.data, skin }]))
};
export const MENU_THEMES = Object.keys(THEMES);
const MENU_LOOK = { theme: 'jungle', layout: 'center' };
/** the trial looks can be switched to: a run from the sources (preload.js devBuild) or no Electron (a browser, tools/trailer) */
export const menuTrials = () => !window.appControl || !!window.appControl.devBuild;
const menuTheme = () => (menuTrials() && THEMES[getSetting('menuTrialTheme')] ? getSetting('menuTrialTheme') : MENU_LOOK.theme);
/** 'center' (the entries alone in the middle of the painting) or 'band' (the trial band down the left edge) */
export const menuLayout = () => (menuTrials() && getSetting('menuTrialLayout')) || MENU_LOOK.layout;
let TH = THEMES[MENU_LOOK.theme];
let THEME = MENU_LOOK.theme;
export let ACID = TH.accent;          // the theme's accent (a live binding: pauseMenu.js reads it after useTheme)
let ACID_CSS = css(ACID);
let LABEL, SMALL, ROW_LABEL;

/** read the theme setting into the module's colours and type styles; every create* calls it first */
export function useTheme() {
    THEME = menuTheme();
    TH = THEMES[THEME];
    ACID = TH.accent;
    ACID_CSS = css(ACID);
    const f = { fontFamily: TH.font, fontStyle: 'bold' };
    LABEL = { ...f, fontSize: TH.labelPx + 'px', color: css(TH.text), letterSpacing: 1 };
    SMALL = { ...f, fontSize: '11px', color: css(TH.note), letterSpacing: TH.smallSpacing };
    ROW_LABEL = { ...f, fontSize: TH.rowPx + 'px', color: css(TH.text), letterSpacing: 1 };
    return TH;
}
useTheme();

/** a band heading, `px` = its size in Brutal's Bebas Neue (the theme scales it to its own face) */
export function bandHeadStyle(px) {
    return { fontFamily: TH.head, fontStyle: TH.headBold ? 'bold' : 'normal', fontSize: Math.round(px * TH.headScale) + 'px', color: css(TH.text), padding: { y: 4 } };
}

/** small print in the theme's face */
export function bandSmallStyle(px, color) {
    return { ...SMALL, fontSize: px + 'px', letterSpacing: 1, ...(color ? { color } : {}) };
}

/** the band's fonts (LoadingScene, so the pause menu has them in a game started from a save too; MainScene) */
export function preloadMainMenuBand(scene) {
    useTheme();
    TH.skin?.preload(scene);                      // only the look in use: L in MainScene restarts it, loading the next
    const font = (family, file, desc) => {
        if ([...document.fonts].some(f => f.family.replace(/"/g, '') === family && f.status === 'loaded')) return;
        scene.load.font(family, 'assets/fonts/' + file, 'truetype', desc);
    };
    font('Bebas Neue', 'BebasNeue.ttf');
    font('Space Grotesk', 'SpaceGrotesk.ttf', { weight: '300 700' });
    font('Cinzel', 'Cinzel.ttf', { weight: '400 900' });
    font('UnifrakturMaguntia', 'UnifrakturMaguntia.ttf');
    font('Comfortaa', 'Comfortaa.ttf', { weight: '300 700' });
    font('Monoton', 'Monoton.ttf');
}

// ---------------------------------------------------------------------------------------------------------------
// drawn pieces

function tex(scene, key, w, h, draw) {
    if (!scene.textures.exists(key)) {
        const t = scene.textures.createCanvas(key, w, h);
        draw(t.getContext(), w, h);
        t.refresh();
        t.setFilter(Phaser.Textures.FilterMode.LINEAR);
    }
    return key;
}

/** a gear: `teeth` trapezoid teeth round a disc, a hole in the middle, optionally `windows` cut between spokes */
function gear(scene, ro, teeth, { hole = 0.3, windows = 0 } = {}) {
    const key = `mmGear_${ro}_${teeth}_${hole}_${windows}`;
    const s = Math.ceil(ro * 2 + 4);
    return tex(scene, key, s, s, (c) => {
        const cx = s / 2, ri = ro - Math.max(2.5, ro * 0.17), step = Math.PI * 2 / teeth;
        c.fillStyle = '#ffffff';
        c.beginPath();
        for (let i = 0; i < teeth; i++) {
            const a = i * step;
            [[ri, a - step * 0.5], [ri, a - step * 0.24], [ro, a - step * 0.13], [ro, a + step * 0.13], [ri, a + step * 0.24]]
                .forEach(([r, t], k) => {
                    const x = cx + Math.cos(t) * r, y = cx + Math.sin(t) * r;
                    if (i === 0 && k === 0) c.moveTo(x, y); else c.lineTo(x, y);
                });
        }
        c.closePath();
        c.fill();
        c.globalCompositeOperation = 'destination-out';
        c.beginPath(); c.arc(cx, cx, ro * hole, 0, Math.PI * 2); c.fill();
        for (let i = 0; i < windows; i++) {
            const a0 = i * Math.PI * 2 / windows + 0.2, a1 = (i + 1) * Math.PI * 2 / windows - 0.2;
            c.beginPath(); c.arc(cx, cx, ro * 0.66, a0, a1); c.arc(cx, cx, ro * 0.42, a1, a0, true); c.closePath(); c.fill();
        }
    });
}

/** three flat mushroom silhouettes (a mycena bell, a round cap, a flat cap), origin at the stem's foot */
const SHROOMS = [
    { w: 14, h: 24, draw: (c, w, h) => {
        c.fillRect(w / 2 - 1.5, h * 0.4, 3, h * 0.6);
        c.beginPath(); c.moveTo(1, h * 0.46); c.quadraticCurveTo(w / 2, -h * 0.12, w - 1, h * 0.46); c.closePath(); c.fill();
    } },
    { w: 16, h: 18, draw: (c, w, h) => {
        c.fillRect(w / 2 - 2, h * 0.45, 4, h * 0.55);
        c.beginPath(); c.ellipse(w / 2, h * 0.45, w / 2 - 1, h * 0.38, 0, Math.PI, 0); c.closePath(); c.fill();
    } },
    { w: 20, h: 14, draw: (c, w, h) => {
        c.fillRect(w / 2 - 2, h * 0.35, 4, h * 0.65);
        c.beginPath(); c.moveTo(1, h * 0.42); c.quadraticCurveTo(w / 2, -h * 0.05, w - 1, h * 0.42); c.lineTo(w - 3, h * 0.5);
        c.lineTo(3, h * 0.5); c.closePath(); c.fill();
    } }
];
function shroom(scene, i) {
    const m = SHROOMS[i % SHROOMS.length];
    return tex(scene, 'mmShroom' + (i % SHROOMS.length), m.w, m.h, (c, w, h) => { c.fillStyle = '#ffffff'; m.draw(c, w, h); });
}

function glowTex(scene) {
    return tex(scene, 'mmGlow', 64, 64, (c, w, h) => {
        const g = c.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
        g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.4, 'rgba(255,255,255,0.45)'); g.addColorStop(1, 'rgba(255,255,255,0)');
        c.fillStyle = g; c.fillRect(0, 0, w, h);
    });
}

function sporeTex(scene) {
    return tex(scene, 'mmSpore', 3, 3, (c) => { c.fillStyle = '#ffffff'; c.fillRect(0, 0, 3, 3); });
}

/** a small seeded random (the mycelium comes out the same every time) */
function rng(seed) {
    let a = seed >>> 0;
    return () => {
        a = (a + 0x6D2B79F5) >>> 0;
        let t = a;
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}

const tween = (scene, targets, props) => scene.tweens.add({ targets, duration: 160, ease: 'Sine.easeOut', ...props });

/**
 * A focusable entry for a MenuNav: a container (w x h hit area at x, y) the caller fills, and its look per state.
 * opts: build(c), focus(on), press(), enable(on), action(), adjust(dir), latchable
 */
function navEntry(scene, nav, x, y, w, h, opts) {
    const c = scene.add.container(x, y);
    opts.build(c);
    c.setSize(w, h).setInteractive({ useHandCursor: true });
    const handle = {
        container: c, enabled: true, focused: false, latched: false, busy: false,
        setFocus(on) {
            if ((on && !handle.enabled) || handle.focused === on || (!on && handle.latched)) return;
            handle.focused = on;
            opts.focus(on);
        },
        activate() {
            if (!handle.enabled || handle.busy) return;
            handle.busy = true;
            playMenuSound(scene, 'clickSound');
            opts.press?.();
            scene.time.delayedCall(opts.delay ?? 140, () => {
                handle.busy = false;
                if (c.active) opts.action?.();
            });
        },
        adjust(dir) { opts.adjust?.(dir); },
        setEnabled(on) {
            handle.enabled = on;
            opts.enable?.(on);
            if (c.input) c.input.cursor = on ? 'pointer' : 'default';
        },
        /** keep the focused look while a panel opened from here is up */
        latch(on) {
            handle.latched = on;
            if (on && !handle.focused) { handle.focused = true; opts.focus(true); }
        }
    };
    c.on('pointerover', () => {
        if (!handle.enabled || !nav.active) return;
        if (nav.items[nav.index] !== handle) playMenuSound(scene, 'hoverSound', 0.6);
        nav.focus(handle);
    });
    c.on('pointerout', () => { if (nav.active) handle.setFocus(false); });
    c.on('pointerdown', (p, lx, ly, ev) => { ev?.stopPropagation(); handle.activate(); });
    nav.add(handle);
    return handle;
}

// ---------------------------------------------------------------------------------------------------------------
// the band

/**
 * MORKEZELA in Bebas Neue, w px wide, its O a gear; top-left at x, y. The gear turns slowly.
 * @returns {{ bottom: number, gear }}
 */
function gearTitle(scene, x, y, w, depth) {
    const m = document.createElement('canvas').getContext('2d');
    m.font = '100px "Bebas Neue"';
    const wM = m.measureText('M').width, wR = m.measureText('RKEZELA').width;
    const cap = m.measureText('M').actualBoundingBoxAscent;
    const wO = cap * 1.08;                        // the gear's slot: as wide as the caps are tall, a hair more
    const k = w / (wM + wO + wR), F = 100 * k, capH = cap * k, TH = Math.ceil(capH) + 3;
    const key = tex(scene, `mmTitle_${Math.round(F * 10)}`, Math.ceil(w) + 2, TH, (c) => {
        c.font = `${F}px "Bebas Neue"`;
        c.fillStyle = '#ffffff';
        c.textBaseline = 'alphabetic';
        c.fillText('M', 0, TH - 1);
        c.fillText('RKEZELA', (wM + wO) * k, TH - 1);
    });
    scene.add.image(x, y, key).setOrigin(0).setDepth(depth);
    const g = scene.add.image(x + (wM + wO / 2) * k, y + TH - 1 - capH / 2, gear(scene, Math.round(capH / 2), 10, { hole: 0.46 }))
        .setDepth(depth);
    const t0 = scene.time.now;
    const turn = () => { g.angle = (scene.time.now - t0) / 1000 * 9; };
    scene.events.on('update', turn);
    scene.events.once('shutdown', () => scene.events.off('update', turn));
    return { bottom: y + TH, gear: g };
}

/**
 * The title on top of the painting, centred at x (MainScene: between the cathedral's spire and the Scraper):
 * UPPER / MORKEZELA (its O a turning gear) / the subtitle, a gap above it, on a soft dark shade whose edges fade
 * into the painting (chosen 2026-11-23 over a black card, a see-through card, frosted glass and a frame).
 */
export function createTopTitle(scene, { x, subtitle }) {
    const theme = useTheme();
    if (theme.skin) return theme.skin.title(scene, K, x, subtitle);
    if (theme.glass) return glassTitle(scene, x, subtitle);
    if (theme.neon) return neonTitle(scene, x, subtitle);
    const TW = 262, PX = 26, PY = 16, TOP = 22;
    const w = TW + 2 * PX, x0 = Math.round(x - w / 2);
    const yU = TOP + PY;
    scene.add.text(x0 + PX, yU, 'UPPER', { fontFamily: 'Space Grotesk', fontStyle: 'bold', fontSize: '13px', color: ACID_CSS, letterSpacing: 9 })
        .setDepth(DEPTH.title);
    const { bottom } = gearTitle(scene, x0 + PX, yU + 19, TW, DEPTH.title);
    scene.add.rectangle(x0 + PX, bottom + 13, 30, 4, ACID).setOrigin(0, 0.5).setDepth(DEPTH.title);
    scene.add.text(x0 + PX + 40, bottom + 13, subtitle.toUpperCase(), { ...SMALL, color: '#d8d8d8' }).setOrigin(0, 0.5).setDepth(DEPTH.title);
    const h = bottom + 13 + 6 + PY - TOP;
    scene.add.image(x, TOP + h / 2, softRect(scene)).setDisplaySize(w + 110, h + 70).setAlpha(0.8).setDepth(DEPTH.title - 0.05);
}

/** a dark rectangle whose edges fade out (smoothstep over the outer third): the shade under a title (white: to tint) */
function softRect(scene, white = false) {
    return tex(scene, white ? 'mmSoftRectW' : 'mmSoftRect', 128, 128, (c, tw, th) => {
        const img = c.createImageData(tw, th);
        const ramp = (t) => { const u = Math.min(1, Math.min(t, 1 - t) / 0.34); return u * u * (3 - 2 * u); };
        for (let yy = 0; yy < th; yy++) for (let xx = 0; xx < tw; xx++) {
            const i = (yy * tw + xx) * 4;
            img.data[i] = img.data[i + 1] = img.data[i + 2] = white ? 255 : 0;
            img.data[i + 3] = Math.round(255 * ramp((xx + 0.5) / tw) * ramp((yy + 0.5) / th));
        }
        c.putImageData(img, 0, 0);
    });
}

/**
 * The band down the screen's left edge (trial layout 'band'), or (menuLayout() 'center') a card in the middle of
 * the screen: `height` shorter than the screen, `top` where the entries start, `place` {x, y, depth} where the card
 * goes. Everything is built at 0, 0 as for the band, then gathered into a container at place; the card gets its rule
 * on all four sides and a soft shadow round it.
 * @param {{ width: number, items: {label, action, enabled}[], height?: number, top?: number, place?: {x, y, depth} }} opts
 * @returns {{ nav: MenuNav, entries, latch(i|null) }}
 */
export function createMainMenuBand(scene, { width: BW, items, height, top: entriesTop = 120, place = null, bare = false }) {
    useTheme();
    const H = height ?? scene.scale.height;
    const RX = BW - RULE;                         // the rule's left edge; the entries run from 0 to it
    const nav = new MenuNav(scene);
    const before = place ? new Set(scene.children.list) : null;
    let wrap = null;                              // the card's container (things made later go into it too)
    const at = (o, d = DEPTH.ui) => { o.setDepth(d); if (wrap) wrap.add(o); return o; };

    if (bare) {
        // only the entries (the centred layout): no band, no rule, no garden
    } else if (TH.skin) {
        TH.skin.band(scene, K, { BW, RX, H, depth: DEPTH.band });
    } else if (TH.glass) {
        at(scene.add.image(0, 0, glassBandTex(scene, RX, H)).setOrigin(0), DEPTH.band);
        came(scene, RX, H, DEPTH.band + 0.05);
    } else if (TH.neon) {
        at(scene.add.image(0, 0, neonBandTex(scene, RX, H)).setOrigin(0), DEPTH.band);
        neonRule(scene, RX, H, DEPTH.band + 0.05);
    } else {
        at(scene.add.rectangle(0, 0, BW, H, 0x000000).setOrigin(0), DEPTH.band);
        at(scene.add.rectangle(RX, 0, RULE, H, ACID).setOrigin(0), DEPTH.band + 0.05);
    }

    // the mycelium: fine threads creeping off the rule into the band, breathing
    const myc = at(scene.add.graphics(), DEPTH.band + 0.02);
    const r = rng(521);
    const thread = (x, y, a, len, depth) => {
        let turn = 0;
        myc.beginPath(); myc.moveTo(x, y);
        for (let k = 0; k < len; k += 2) {
            turn = turn * 0.8 + (r() - 0.5) * 0.08;
            a += turn;
            x = Math.min(RX - 1, x + Math.cos(a) * 2); y += Math.sin(a) * 2;
            myc.lineTo(x, y);
            if (depth < 1 && r() < 0.05) thread(x, y, a + (r() < 0.5 ? -0.6 : 0.6), len * 0.4, depth + 1);
        }
        myc.strokePath();
        myc.fillCircle(x, y, 1.2);
    };
    myc.lineStyle(1, TH.thread, 1).fillStyle(TH.thread, 1);
    for (const [y0, dir] of [[40, 1], [120, -1], [200, 1], [290, 1], [330, -1], [420, 1], [470, -1], [560, -1]].filter(([y0]) => y0 < H - 40)) {
        thread(RX - 1, y0 + r() * 16, dir * Math.PI / 2 + dir * (0.25 + r() * 0.2), 40 + r() * 60, 0);
    }
    myc.setAlpha(0.3);
    scene.tweens.add({ targets: myc, alpha: 0.5, duration: 2600, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    if (TH.glass) myc.setVisible(false);          // over the glass the threads read as cracks
    if (TH.neon) { scene.tweens.killTweensOf(myc); myc.setAlpha(0.2); scene.tweens.add({ targets: myc, alpha: 0.38, duration: 2600, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' }); }
    if (TH.skin) {
        scene.tweens.killTweensOf(myc);
        if (!TH.skin.myc) myc.setVisible(false);
        else { myc.setAlpha(TH.skin.myc[0]); scene.tweens.add({ targets: myc, alpha: TH.skin.myc[1], duration: 2600, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' }); }
    }

    // the fungus garden at the foot, and the spores a click puffs out of the focused entry's mushrooms
    const garden = bare ? { top: H, react() {}, bare: true } : createFungusGarden(scene, { RX, floorY: H - 4, depth: DEPTH.band + 0.05 });
    if (bare) myc.setVisible(false);
    sporeTex(scene);
    const puff = at(scene.add.particles(0, 0, 'mmSpore', {
        emitting: false, speed: { min: 20, max: 70 }, angle: { min: 215, max: 325 }, lifespan: { min: 500, max: 900 },
        scale: { start: 1.3, end: 0.3 }, alpha: { start: 1, end: 0 }, tint: TH.spore, gravityY: -10
    }), DEPTH.ui + 0.1);

    // the focused entry's gear spins
    const entries = [];
    const update = () => entries.forEach(e => { if (e.spin) e.gear.angle += e.spin; });
    scene.events.on('update', update);
    scene.events.once('shutdown', () => scene.events.off('update', update));

    // the entries
    const ROW = 46, GAP = 12, top = entriesTop;
    items.forEach((item, i) => {
        const y = top + i * (ROW + GAP) + ROW / 2;
        if (TH.skin) { entries.push(TH.skin.entry(scene, K, nav, { item, i, RX, y, ROW, puff, garden, at })); return; }
        if (TH.glass) { entries.push(glassEntry(scene, nav, { item, i, RX, y, ROW, puff, garden, at })); return; }
        if (TH.neon) { entries.push(neonEntry(scene, nav, { item, i, RX, y, ROW, puff, garden, at })); return; }
        const e = { spin: 0 };
        let fill, label, shrooms, glow;
        const h = navEntry(scene, nav, RX / 2, y, RX, ROW, {
            build: (c) => {
                fill = scene.add.rectangle(-RX / 2, 0, RX, ROW, 0x000000).setOrigin(0, 0.5);
                e.gear = scene.add.image(-RX / 2 + 30, 0, gear(scene, 8, 8, { hole: 0.32 })).setTint(ACID);
                label = scene.add.text(-RX / 2 + 48, 0, item.label.toUpperCase(), LABEL).setOrigin(0, 0.5);
                for (let fs = 19; label.width > RX - 64 && fs > 13; fs--) label.setFontSize(fs - 1);   // a long label fits the band
                // the mushrooms that sprout on the focused entry (they stand on its top edge, by the rule)
                glow = scene.add.image(RX / 2 - 30, -ROW / 2 - 4, glowTex(scene)).setTint(ACID).setBlendMode(Phaser.BlendModes.ADD)
                    .setDisplaySize(70, 34).setAlpha(0);
                shrooms = [[-48, 1, 0.8], [-36, 0, 1.0], [-24, 2, 0.75], [-12, 0, 0.7]].map(([dx, kind, s]) =>
                    scene.add.image(RX / 2 + dx, -ROW / 2 + 1, shroom(scene, kind)).setOrigin(0.5, 1).setTint(ACID).setScale(0).setData('s', s));
                c.add([glow, fill, e.gear, label, ...shrooms]);
            },
            focus: (on) => {
                fill.fillColor = on ? ACID : 0x000000;
                label.setColor(on ? '#000000' : '#ffffff');
                e.gear.setTint(on ? 0x000000 : ACID);
                e.spin = on ? 3 : 0;
                tween(scene, label, { x: -RX / 2 + 48 + (on ? 6 : 0), duration: 110 });
                shrooms.forEach((s, j) => {
                    scene.tweens.killTweensOf(s);
                    scene.tweens.add(on
                        ? { targets: s, scale: s.getData('s'), duration: 260, delay: j * 55, ease: 'Back.easeOut' }
                        : { targets: s, scale: 0, duration: 120, ease: 'Sine.easeIn' });
                });
                scene.tweens.killTweensOf(glow);
                if (on) scene.tweens.add({ targets: glow, alpha: { from: 0.2, to: 0.6 }, duration: 900, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
                else glow.setAlpha(0);
            },
            press: () => {
                tween(scene, e.gear, { angle: e.gear.angle + 180, duration: 260 });
                puff.explode(14, RX - 36, y - ROW / 2 - 6);
                pulseDown(scene, RX, y, garden, at);
            },
            enable: (on) => { label.setColor(on ? '#ffffff' : '#505050'); e.gear.setTint(on ? ACID : 0x3a3a3a); },
            action: item.action
        });
        h.container.setDepth(DEPTH.ui);
        h.setEnabled(item.enabled !== false);
        e.handle = h;
        entries.push(e);
    });

    if (place && bare) {
        // the bare entries: only a soft dark haze under them, no edges, so they read over the painting
        at(scene.add.image(BW / 2, H / 2, softRect(scene)).setDisplaySize(BW + 170, H + 120).setAlpha(0.55), DEPTH.band - 0.1);
    } else if (place) {
        // the card: the rule round all four sides (the top and bottom ones turned on their side), a shadow round it
        const rule = (x, len, left = false) => TH.skin ? TH.skin.rule(scene, K, x, len, left) : TH.glass ? came(scene, x, len)
            : TH.neon ? neonRule(scene, x, len) : scene.add.rectangle(x, 0, RULE, len, ACID).setOrigin(0);
        at(rule(-RULE, H, true), DEPTH.band + 0.05);
        for (const y of [0, H + RULE]) at(scene.add.container(-RULE, y, [rule(0, BW + RULE)]).setAngle(-90), DEPTH.band + 0.06);
        at(scene.add.image(BW / 2, H / 2, softRect(scene)).setDisplaySize(BW + 110, H + 110).setAlpha(0.85), DEPTH.band - 0.1);
    }
    if (place) {
        const made = scene.children.list.filter(o => !before.has(o)).sort((a, b) => a.depth - b.depth);
        wrap = scene.add.container(place.x, place.y, made).setDepth(place.depth ?? DEPTH.band);
    }

    let latched = null;
    return {
        nav, entries,
        /** keep entry i lit (a panel from it is open); null lets go */
        latch(i) {
            if (latched) latched.latch(false);
            nav.items.forEach(it => it.setFocus(false));
            latched = i == null ? null : entries[i].handle;
            latched?.latch(true);
        },
        focusEntry(i) { nav.focus(entries[i].handle); }
    };
}

/** what a skin (ui/menuSkins.js) gets to build with */
const K = {
    navEntry, tex, glowTex, shroom, sporeTex, tween, pulseDown, softRect, rng, css, DEPTH, RULE,
    get TH() { return TH; }, get ACID() { return ACID; }, get LABEL() { return LABEL; }
};

// ---------------------------------------------------------------------------------------------------------------
// the fungus garden: real odd species, drawn flat in the band's colours

const WHITE = '#efeee6', BONE = '#cfcdc2';

const FUNGI = {
    // Clathrus ruber, the basket stinkhorn: a hollow lattice ball on the cup it hatched from
    basket: { w: 46, h: 44, draw(c, w, h) {
        const cx = w / 2, cy = 20, rx = 20, ry = 19;
        c.fillStyle = css(TH.basket); c.beginPath(); c.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2); c.fill();
        c.globalCompositeOperation = 'destination-out';
        for (let row = -2; row <= 2; row++) for (let col = -3; col <= 3; col++) {
            const ox = col * 8.6 + (row % 2 ? 4.3 : 0), oy = row * 7.6, d = Math.hypot(ox / rx, oy / ry);
            if (d > 0.86) continue;
            const sz = 3.9 * (1 - d * 0.5);
            c.beginPath(); c.ellipse(cx + ox, cy + oy, sz * (1 - d * 0.35), sz, Math.atan2(oy, ox), 0, Math.PI * 2); c.fill();
        }
        c.globalCompositeOperation = 'source-over';
        c.fillStyle = WHITE;
        c.beginPath(); c.moveTo(cx - 13, h - 11); c.quadraticCurveTo(cx - 13, h, cx, h); c.quadraticCurveTo(cx + 13, h, cx + 13, h - 11);
        c.lineTo(cx + 8, h - 8); c.lineTo(cx, h - 10); c.lineTo(cx - 8, h - 8); c.closePath(); c.fill();
    } },
    // Mycena chlorophos: little bells on hair-thin stems that glow in the dark
    mycena: { w: 34, h: 46, draw(c, w, h) {
        [[6, 22, 4.5], [13, 38, 5.5], [20, 30, 4.8], [27, 42, 6], [31, 18, 3.6]].forEach(([x, hh, r]) => {
            c.fillStyle = BONE; c.fillRect(x - 0.75, h - hh + r * 0.6, 1.5, hh - r * 0.6);
            c.fillStyle = css(TH.mycena);
            c.beginPath(); c.moveTo(x - r, h - hh + r * 0.9); c.quadraticCurveTo(x, h - hh - r * 1.3, x + r, h - hh + r * 0.9); c.closePath(); c.fill();
        });
    } },
};

const FUNGUS_RES = 2;            // drawn at twice the size, shown scaled: crisp edges
function fungus(scene, name) {
    const f = FUNGI[name];
    return tex(scene, `mmFungus_${name}_${THEME}`, f.w * FUNGUS_RES, f.h * FUNGUS_RES, (c) => { c.scale(FUNGUS_RES, FUNGUS_RES); f.draw(c, f.w, f.h); });
}

/**
 * The foot of the band: in the left corner a basket stinkhorn (its flies circling) and glowing mycenas; on the right
 * the clump of little glowing mushrooms breathing spores. react() is a click's pulse arriving: the clump puffs, the
 * glows flare.
 * @returns {{ top: number, react(): void }}
 */
function createFungusGarden(scene, { RX, floorY, depth }) {
    const put = (name, x, sc, d = depth) =>
        scene.add.image(x, floorY, fungus(scene, name)).setOrigin(0.5, 1).setScale(sc / FUNGUS_RES).setDepth(d);
    const glowAt = (x, y, w, h, a0, a1) => {
        const g = scene.add.image(x, y, glowTex(scene)).setTint(TH.glow).setBlendMode(Phaser.BlendModes.ADD)
            .setDisplaySize(w, h).setAlpha(a0).setDepth(depth - 0.01);
        scene.tweens.add({ targets: g, alpha: a1, duration: 2300, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
        return g;
    };
    sporeTex(scene);

    // the left corner
    const mx = 60;
    const mGlow = glowAt(mx, floorY - 26, 76, 76, 0.28, 0.5);
    put('mycena', mx, 1.2, depth - 0.005);
    const basket = put('basket', 26, 1.2);
    const flies = [0, 1].map(() => scene.add.rectangle(0, 0, 2, 2, 0xd8d6cc).setDepth(depth + 0.02));   // it smells of carrion

    // the clump on the right
    const cx = RX - 55;                              // (by the rule, whatever the band's width)
    const cGlow = glowAt(cx + 10, floorY - 12, 90, 50, 0.25, 0.45);
    [[-12, 0, 1.7], [3, 1, 1.35], [17, 0, 1.05], [30, 2, 1.4], [42, 1, 0.8]].forEach(([dx, kind, sc], k) => {
        scene.add.image(cx + dx, floorY, shroom(scene, kind)).setOrigin(0.5, 1).setScale(sc)
            .setTint(TH.garden[k % TH.garden.length]).setDepth(depth);
    });
    scene.add.particles(0, 0, 'mmSpore', {
        x: { min: cx - 14, max: cx + 38 }, y: floorY - 16, speedY: { min: -22, max: -10 }, speedX: { min: -4, max: 4 },
        lifespan: { min: 2600, max: 4200 }, frequency: 650, scale: { start: 1, end: 0.4 }, alpha: { start: 0.9, end: 0 }, tint: TH.spore
    }).setDepth(depth + 0.01);
    const puff = scene.add.particles(0, 0, 'mmSpore', {
        emitting: false, speed: { min: 20, max: 70 }, angle: { min: 215, max: 325 }, lifespan: { min: 500, max: 900 },
        scale: { start: 1.3, end: 0.3 }, alpha: { start: 1, end: 0 }, tint: TH.spore, gravityY: -10
    }).setDepth(depth + 0.01);

    const t0 = scene.time.now;
    const update = () => {
        const t = (scene.time.now - t0) / 1000;
        flies.forEach((f, i) => {
            const a = t * (2.3 + i * 0.9) + i * 2;
            f.setPosition(basket.x + Math.cos(a) * (14 + i * 5) + Math.sin(t * 7 + i) * 1.5, floorY - 40 + Math.sin(a * 1.3) * (7 + i * 3));
        });
    };
    scene.events.on('update', update);
    scene.events.once('shutdown', () => scene.events.off('update', update));
    return {
        top: floorY - 30,
        react() {
            puff.explode(18, cx + 10, floorY - 18);
            [cGlow, mGlow].forEach(g => scene.tweens.add({ targets: g, alpha: 1, duration: 130, yoyo: true }));
        }
    };
}

// ---------------------------------------------------------------------------------------------------------------
// Vitráž (TRIAL): stained glass after the Egg Cathedral's windows; the glass drawing comes from the trial design
// (tools/menu_trials/menuDesigns_trial_backup.js glassPane / buildGlass)

const LEAD = 0x17121f, LEAD_CSS = '#17121f';
const GLASS = {
    violet: [[107, 58, 160], [83, 44, 140], [128, 76, 178], [70, 40, 120]],
    amber: [[240, 178, 60], [222, 150, 40], [250, 200, 90], [210, 130, 30]],
    teal: [[42, 140, 140], [30, 118, 128], [60, 160, 150], [24, 100, 112]],
    rose: [[201, 79, 124], [180, 60, 104], [220, 100, 140], [160, 50, 90]],
    grey: [[110, 106, 116], [96, 92, 102], [124, 120, 130], [86, 82, 92]]
};
const GLASS_HUES = ['amber', 'teal', 'rose', 'violet'];
const GLASS_GLOW = { amber: 0xffc65a, teal: 0x6fe6da, rose: 0xff8fb8, violet: 0xc39bff };

/** a pointed (stretched hexagon) outline, w x h, its points `tip` px deep, as a function that makes the path */
const pointed = (c, w, h, tip, inset = 4) => () => {
    c.beginPath();
    c.moveTo(inset, h / 2); c.lineTo(tip, inset); c.lineTo(w - tip, inset); c.lineTo(w - inset, h / 2);
    c.lineTo(w - tip, h - inset); c.lineTo(tip, h - inset); c.closePath();
};

/**
 * Glass: the shape filled with cells (nearest of `cells` seeds, each a colour of the palette, a little brighter or
 * darker), lead between them and `lead` px of it round the edge; `light` = the glow through the middle, `dim` darkens.
 */
function glassPane(c, w, h, shape, palette, seed, cells, { light = 0.28, dim = 1, lead = 7 } = {}) {
    const r = rng(seed);
    const seeds = Array.from({ length: cells }, () => [r() * w, r() * h, palette[Math.floor(r() * palette.length)], 0.85 + r() * 0.3]);
    const img = c.createImageData(w, h);
    const owner = new Int16Array(w * h);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        let best = 0, bd = 1e9;
        for (let k = 0; k < seeds.length; k++) {
            const dx = seeds[k][0] - x, dy = (seeds[k][1] - y) * 1.4, d = dx * dx + dy * dy;
            if (d < bd) { bd = d; best = k; }
        }
        owner[y * w + x] = best;
    }
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        const k = owner[y * w + x], i = (y * w + x) * 4;
        const seam = (x > 0 && owner[y * w + x - 1] !== k) || (y > 0 && owner[(y - 1) * w + x] !== k)
            || (x > 1 && owner[y * w + x - 2] !== k) || (y > 1 && owner[(y - 2) * w + x] !== k);
        const [cr, cg, cb] = seeds[k][2], b = dim * seeds[k][3] * (0.92 + 0.16 * Math.sin(x * 0.07 + y * 0.11 + k));
        img.data[i] = seam ? 23 : Math.min(255, cr * b);
        img.data[i + 1] = seam ? 18 : Math.min(255, cg * b);
        img.data[i + 2] = seam ? 31 : Math.min(255, cb * b);
        img.data[i + 3] = 255;
    }
    const tmp = document.createElement('canvas');
    tmp.width = w; tmp.height = h;
    tmp.getContext('2d').putImageData(img, 0, 0);
    c.save(); shape(); c.clip(); c.drawImage(tmp, 0, 0);
    if (light) {                                    // the light coming through the middle
        const g = c.createRadialGradient(w / 2, h * 0.35, 0, w / 2, h * 0.35, Math.max(w, h) * 0.6);
        g.addColorStop(0, `rgba(255,255,230,${light})`); g.addColorStop(1, 'rgba(255,255,230,0)');
        c.fillStyle = g; c.fillRect(0, 0, w, h);
    }
    c.restore();
    if (lead) { shape(); c.strokeStyle = LEAD_CSS; c.lineWidth = lead; c.stroke(); }
}

/** the band itself: a window at dusk, dim glass in lead, darker toward the garden at its foot */
function glassBandTex(scene, w, h) {
    return tex(scene, `mmGlassBand_${w}_${h}`, w, h, (c) => {
        c.fillStyle = LEAD_CSS; c.fillRect(0, 0, w, h);
        const palette = [...GLASS.violet, ...GLASS.violet, ...GLASS.teal, GLASS.rose[0], GLASS.rose[3], GLASS.amber[3]];
        glassPane(c, w, h, () => { c.beginPath(); c.rect(0, 0, w, h); }, palette, 77, Math.round(w * h / 2400), { light: 0, dim: 0.36, lead: 0 });
        const g = c.createLinearGradient(0, 0, 0, h);
        g.addColorStop(0, 'rgba(23,18,31,0.1)'); g.addColorStop(0.7, 'rgba(23,18,31,0.3)'); g.addColorStop(1, 'rgba(23,18,31,0.9)');
        c.fillStyle = g; c.fillRect(0, 0, w, h);
    });
}

/** the rule as a came: lead with a gold core (a container at x, its children from 0 to RULE) */
function came(scene, x, h, depth) {
    const c = scene.add.container(x, 0, [
        scene.add.rectangle(0, 0, RULE, h, LEAD).setOrigin(0),
        scene.add.rectangle(1, 0, 2, h, ACID).setOrigin(0)
    ]);
    if (depth != null) c.setDepth(depth);
    return c;
}

/**
 * A main-menu entry as a glass pane in the band (its hue by position): focus lights it from behind and grows it a
 * little, the label turns gold and mushrooms in the pane's colour sprout on its top edge; a click flashes the glass,
 * puffs spores and sends a pulse down the came into the garden. Disabled = grey glass.
 */
function glassEntry(scene, nav, { item, i, RX, y, ROW, puff, garden, at }) {
    const PW = RX - 22, hue = GLASS_HUES[i % GLASS_HUES.length];
    const e = { spin: 0 };
    let pane, grey, light, label, shrooms, glow;
    const paneTex = (palette, name) => tex(scene, `mmGlassPane_${name}_${PW}_${ROW}_${i}`, PW, ROW + 4,
        (c, w, h) => glassPane(c, w, h, pointed(c, w, h, 18), palette, 30 + i, 14, { lead: 5 }));
    const h = navEntry(scene, nav, RX / 2, y, RX, ROW, {
        build: (c) => {
            pane = scene.add.image(0, 0, paneTex(GLASS[hue], hue));
            grey = scene.add.image(0, 0, paneTex(GLASS.grey, 'grey')).setVisible(false);
            light = scene.add.image(0, 0, pane.texture.key).setTintFill(0xffffff).setBlendMode(Phaser.BlendModes.ADD).setAlpha(0);
            label = scene.add.text(0, 0, item.label, { ...LABEL, stroke: LEAD_CSS, strokeThickness: 5, padding: { x: 4, y: 3 } }).setOrigin(0.5);
            for (let fs = TH.labelPx; label.width > PW - 40 && fs > 12; fs--) label.setFontSize(fs - 1);   // a long label fits
            glow = scene.add.image(PW / 2 - 34, -ROW / 2 - 4, glowTex(scene)).setTint(GLASS_GLOW[hue]).setBlendMode(Phaser.BlendModes.ADD)
                .setDisplaySize(64, 30).setAlpha(0);
            shrooms = [[-48, 1, 0.7], [-37, 0, 0.85], [-26, 2, 0.65]].map(([dx, kind, s]) =>
                scene.add.image(PW / 2 + dx, -ROW / 2 + 3, shroom(scene, kind)).setOrigin(0.5, 1).setTint(GLASS_GLOW[hue]).setScale(0).setData('s', s));
            c.add([glow, ...shrooms, pane, grey, light, label]);
        },
        focus: (on) => {
            tween(scene, light, { alpha: on ? 0.26 : 0 });
            label.setColor(on ? '#ffd86b' : css(TH.text));
            tween(scene, label.parentContainer, { scale: on ? 1.04 : 1 });
            shrooms.forEach((s, j) => {
                scene.tweens.killTweensOf(s);
                scene.tweens.add(on
                    ? { targets: s, scale: s.getData('s'), duration: 260, delay: j * 55, ease: 'Back.easeOut' }
                    : { targets: s, scale: 0, duration: 120, ease: 'Sine.easeIn' });
            });
            scene.tweens.killTweensOf(glow);
            if (on) scene.tweens.add({ targets: glow, alpha: { from: 0.2, to: 0.6 }, duration: 900, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
            else glow.setAlpha(0);
        },
        press: () => {
            tween(scene, light, { alpha: 0.6, yoyo: true, duration: 80 });
            puff.explode(14, RX / 2 + PW / 2 - 36, y - ROW / 2 - 6);
            pulseDown(scene, RX, y, garden, at);
        },
        enable: (on) => { pane.setVisible(on); grey.setVisible(!on); label.setColor(on ? css(TH.text) : css(TH.dim)); },
        action: item.action
    });
    h.container.setDepth(DEPTH.ui);
    h.setEnabled(item.enabled !== false);
    e.handle = h;
    return e;
}

/**
 * The title on a violet glass plate, centred at x on top of the painting: U P P E R in Cinzel, Morkezela in gold
 * blackletter (UnifrakturMaguntia), the subtitle on a lead strip across the plate's foot; a soft shade behind.
 */
function glassTitle(scene, x, subtitle) {
    const PW = 452, PH = 104, TOP = 18, cy = TOP + PH / 2;
    scene.add.image(x, cy + 6, softRect(scene)).setDisplaySize(PW + 90, PH + 70).setAlpha(0.75).setDepth(DEPTH.title - 0.05);
    scene.add.image(x, cy, tex(scene, 'mmGlassTitle', PW, PH, (c, w, h) =>
        glassPane(c, w, h, pointed(c, w, h, 34), GLASS.violet, 11, 40, { lead: 6 }))).setDepth(DEPTH.title - 0.01);
    const at = (o) => o.setOrigin(0.5).setDepth(DEPTH.title);
    at(scene.add.text(x, TOP + 20, 'U P P E R', { fontFamily: 'Cinzel', fontStyle: 'bold', fontSize: '13px', color: '#fbeec8', stroke: LEAD_CSS, strokeThickness: 4, padding: { x: 4, y: 3 } }));
    at(scene.add.text(x, TOP + 58, 'Morkezela', { fontFamily: 'UnifrakturMaguntia', fontSize: '54px', color: '#ffcf5a', stroke: LEAD_CSS, strokeThickness: 7, padding: { x: 8, y: 6 } }));
    const sub = at(scene.add.text(x, TOP + PH + 4, subtitle.toUpperCase(), { fontFamily: 'Cinzel', fontStyle: 'bold', fontSize: '10px', color: '#e8d9ff', letterSpacing: 2, padding: { x: 4, y: 3 } }));
    scene.add.rectangle(x, sub.y, sub.width + 26, 20, LEAD).setDepth(DEPTH.title - 0.005);
}

/** a click's pulse runs down the rule into the garden at the band's foot, which stirs */
function pulseDown(scene, RX, y, garden, at) {
    if (garden.bare) return;                      // (no rule, no garden: the bare entries in the middle)
    const p = at(scene.add.image(RX + RULE / 2, y, glowTex(scene)).setTint(ACID).setBlendMode(Phaser.BlendModes.ADD)
        .setDisplaySize(24, 60), DEPTH.band + 0.06);
    scene.tweens.add({ targets: p, y: garden.top, alpha: { from: 1, to: 0.3 }, duration: 380, ease: 'Cubic.easeIn', onComplete: () => {
        p.destroy();
        garden.react();
    } });
}

// ---------------------------------------------------------------------------------------------------------------
// Bioluminiscence (TRIAL): neon on deep indigo, after the trial design (menuDesigns_trial_backup.js buildGlow)

const MAGENTA = 0xff4fd8, NEON_VIOLET = 0x9d7bff;

/** the band: deep indigo, a little lighter at the top, near black at the garden */
function neonBandTex(scene, w, h) {
    return tex(scene, `mmNeonBand_${w}_${h}`, w, h, (c) => {
        const g = c.createLinearGradient(0, 0, 0, h);
        g.addColorStop(0, '#191043'); g.addColorStop(0.55, '#0d0826'); g.addColorStop(1, '#040210');
        c.fillStyle = g; c.fillRect(0, 0, w, h);
    });
}

/** the rule as a neon tube: a pale core in a cyan halo that breathes (a container at x, the core from 0 to RULE) */
function neonRule(scene, x, h, depth) {
    const halo = scene.add.image(RULE / 2, 0, tex(scene, 'mmNeonHalo', 32, 4, (c, w, hh) => {
        const g = c.createLinearGradient(0, 0, w, 0);
        g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(0.5, 'rgba(255,255,255,1)'); g.addColorStop(1, 'rgba(255,255,255,0)');
        c.fillStyle = g; c.fillRect(0, 0, w, hh);
    })).setOrigin(0.5, 0).setDisplaySize(30, h).setTint(ACID).setBlendMode(Phaser.BlendModes.ADD).setAlpha(0.5);
    const core = scene.add.rectangle(1, 0, 2, h, 0xc8fbff).setOrigin(0);
    scene.tweens.add({ targets: halo, alpha: 0.8, duration: 2400, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    const c = scene.add.container(x, 0, [halo, core]);
    if (depth != null) c.setDepth(depth);
    return c;
}

/**
 * A main-menu entry as glowing type, no panel: focus turns its glow from violet to cyan and brighter, grows it,
 * lights two pulsing spore dots beside it and sprouts neon mushrooms on its top edge; a click squeezes it, puffs
 * spores and sends a pulse down the tube into the garden.
 */
function neonEntry(scene, nav, { item, i, RX, y, ROW, puff, garden, at }) {
    const e = { spin: 0 };
    let label, fx, dots, shrooms, glow;
    const h = navEntry(scene, nav, RX / 2, y, RX, ROW, {
        build: (c) => {
            label = scene.add.text(0, 0, item.label, { ...LABEL, padding: { x: 14, y: 10 } }).setOrigin(0.5);
            for (let fs = TH.labelPx; label.width - 28 > RX - 64 && fs > 12; fs--) label.setFontSize(fs - 1);
            fx = label.preFX?.addGlow(NEON_VIOLET, 1.5, 0, false, 0.1, 10);
            const half = (label.width - 28) / 2 + 14;
            dots = [-half, half].map(x => scene.add.image(x, 0, glowTex(scene)).setDisplaySize(16, 16).setTint(ACID)
                .setBlendMode(Phaser.BlendModes.ADD).setAlpha(0));
            dots.forEach(d => d.setData('k', d.scaleX));
            glow = scene.add.image(RX / 2 - 34, -ROW / 2 - 4, glowTex(scene)).setTint(MAGENTA).setBlendMode(Phaser.BlendModes.ADD)
                .setDisplaySize(64, 30).setAlpha(0);
            shrooms = [[-48, 1, 0.7, ACID], [-37, 0, 0.85, MAGENTA], [-26, 2, 0.65, NEON_VIOLET]].map(([dx, kind, s, col]) =>
                scene.add.image(RX / 2 + dx, -ROW / 2 + 3, shroom(scene, kind)).setOrigin(0.5, 1).setTint(col).setScale(0).setData('s', s));
            c.add([glow, ...shrooms, label, ...dots]);
        },
        focus: (on) => {
            label.setColor(on ? '#9ffaff' : css(TH.text));
            if (fx) { fx.color = on ? ACID : NEON_VIOLET; tween(scene, fx, { outerStrength: on ? 3 : 1.5 }); }
            tween(scene, label.parentContainer, { scale: on ? 1.06 : 1 });
            dots.forEach(d => {
                scene.tweens.killTweensOf(d);
                d.setAlpha(on ? 1 : 0).setScale(d.getData('k'));
                if (on) scene.tweens.add({ targets: d, scale: d.getData('k') * 1.4, alpha: 0.5, duration: 600, yoyo: true, repeat: -1 });
            });
            shrooms.forEach((s, j) => {
                scene.tweens.killTweensOf(s);
                scene.tweens.add(on
                    ? { targets: s, scale: s.getData('s'), duration: 260, delay: j * 55, ease: 'Back.easeOut' }
                    : { targets: s, scale: 0, duration: 120, ease: 'Sine.easeIn' });
            });
            scene.tweens.killTweensOf(glow);
            if (on) scene.tweens.add({ targets: glow, alpha: { from: 0.2, to: 0.6 }, duration: 900, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
            else glow.setAlpha(0);
        },
        press: () => {
            tween(scene, label, { scale: 0.94, yoyo: true, duration: 70 });
            puff.explode(14, RX - 40, y - ROW / 2 - 6);
            pulseDown(scene, RX, y, garden, at);
        },
        enable: (on) => { label.setColor(on ? css(TH.text) : css(TH.dim)); if (fx) fx.outerStrength = on ? 1.5 : 0; },
        action: item.action
    });
    h.container.setDepth(DEPTH.ui);
    h.setEnabled(item.enabled !== false);
    e.handle = h;
    return e;
}

/**
 * The title in neon over the painting's smoke, centred at x: U P P E R in magenta, MORKEZELA in cyan Monoton whose
 * glow breathes, the subtitle in lower case; a soft indigo shade behind.
 */
function neonTitle(scene, x, subtitle) {
    const TOP = 22, d = DEPTH.title;
    const up = scene.add.text(x, TOP + 12, 'U P P E R', { fontFamily: 'Comfortaa', fontStyle: 'bold', fontSize: '13px', color: '#ff8fe6', padding: { x: 14, y: 12 } })
        .setOrigin(0.5).setDepth(d);
    up.preFX?.addGlow(MAGENTA, 2.5, 0, false, 0.1, 10);
    // a near-white tube with the colour in its glow (as real neon), the glow kept low: Monoton's inline stripes blur
    // into the painting's pale smoke when it blooms
    const title = scene.add.text(x, TOP + 56, 'MORKEZELA', { fontFamily: 'Monoton', fontSize: '56px', color: '#e2fdff', padding: { x: 16, y: 14 } })
        .setOrigin(0.5).setDepth(d);
    if (title.width - 32 > 490) title.setFontSize(Math.floor(56 * 490 / (title.width - 32)));
    const fx = title.preFX?.addGlow(ACID, 2.2, 0, false, 0.3, 12);   // (quality 0.3: at 0.1 the glow smeared in streaks)
    if (fx) scene.tweens.add({ targets: fx, outerStrength: 3.4, duration: 2200, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    scene.add.text(x, TOP + 104, subtitle.toLowerCase(), { fontFamily: 'Comfortaa', fontStyle: 'bold', fontSize: '13px', color: '#d8ceff', letterSpacing: 4, padding: { x: 4, y: 3 } })
        .setOrigin(0.5).setDepth(d);
    // the night behind it: a wide soft indigo shade and a darker core right under the letters
    const shade = (w, h, a) => scene.add.image(x, TOP + 60, softRect(scene, true)).setTint(0x07041a).setDisplaySize(w, h).setAlpha(a).setDepth(d - 0.05);
    shade(title.width + 150, 210, 0.9);
    shade(title.width + 30, 120, 0.75);
}

// ---------------------------------------------------------------------------------------------------------------
// the panels that slide out of the band

/**
 * A black panel x..x+w, full height, sliding out from under the band; the painting beside it dims (a click there
 * closes it). Rows are added with the helpers below; contents go into panel.body (local coords, x from the left edge).
 */
export function createBandPanel(scene, { x, w, title, onClose, shadeAll = false }) {
    useTheme();
    const W = scene.scale.width, H = scene.scale.height;
    const shade = scene.add.rectangle(shadeAll ? 0 : x, 0, shadeAll ? W : W - x, H, 0x000000).setOrigin(0).setAlpha(0).setDepth(DEPTH.shade)
        .setVisible(false).setInteractive();
    shade.on('pointerdown', () => onClose?.());
    const body = scene.add.container(x, 0).setDepth(DEPTH.panel).setVisible(false);
    body.add(scene.add.rectangle(0, 0, w, H, TH.bg).setOrigin(0).setInteractive());   // clicks on the panel stay here
    if (TH.skin) body.add(TH.skin.panelBg(scene, K, w, H));
    // (kept on top of the rows added later: a row's fill would cover the neon tube's halo)
    const rule = TH.skin ? TH.skin.rule(scene, K, w - RULE, H) : TH.glass ? came(scene, w - RULE, H) : TH.neon ? neonRule(scene, w - RULE, H)
        : scene.add.rectangle(w - RULE, 0, RULE, H, ACID).setOrigin(0);
    body.add(rule);
    const head = scene.add.text(28, TH.glass || TH.neon || TH.skin ? 44 : 34, title, bandHeadStyle(62));
    body.add(head);
    body.add(scene.add.rectangle(28, head.y + head.height + 6, 30, 4, ACID).setOrigin(0, 0.5));
    // a cross to close it (for the mouse; ESC and a click on the painting do too)
    const cross = scene.add.graphics();
    const drawCross = (col) => { cross.clear().lineStyle(3, col, 1).lineBetween(-9, -9, 9, 9).lineBetween(-9, 9, 9, -9); };
    drawCross(TH.text);
    const cz = scene.add.zone(w - RULE - 34, 56, 40, 40).setInteractive({ useHandCursor: true });
    cross.setPosition(cz.x, cz.y);
    cz.on('pointerover', () => drawCross(ACID));
    cz.on('pointerout', () => drawCross(TH.text));
    cz.on('pointerdown', (p, lx, ly, ev) => { ev?.stopPropagation(); playMenuSound(scene, 'clickSound'); onClose?.(); });
    body.add([cross, cz]);

    const nav = new MenuNav(scene);
    nav.active = false;
    const panel = {
        body, nav, w, x, rule, open: false,
        /** slide out (slow: the gentler way, after the language changed and the menu came back translated) */
        show({ slow = false } = {}) {
            panel.open = true;
            scene.tweens.killTweensOf([body, shade]);
            body.setVisible(true);
            shade.setVisible(true);
            body.x = x - w;
            const duration = slow ? 700 : 340;
            scene.tweens.add({ targets: body, x, duration, ease: 'Sine.easeInOut' });
            scene.tweens.add({ targets: shade, alpha: 0.6, duration, ease: 'Sine.easeInOut' });
            nav.active = true;
            if (nav.items.length) nav.focus(nav.items.find(it => it.enabled !== false) || null);
        },
        hide(instant = false) {
            panel.open = false;
            nav.active = false;
            nav.items.forEach(it => it.setFocus(false));
            scene.tweens.killTweensOf([body, shade]);
            if (instant) { body.setVisible(false); shade.setVisible(false).setAlpha(0); return; }
            scene.tweens.add({ targets: body, x: x - w, duration: 260, ease: 'Sine.easeInOut', onComplete: () => body.setVisible(false) });
            scene.tweens.add({ targets: shade, alpha: 0, duration: 260, onComplete: () => shade.setVisible(false) });
        }
    };
    return panel;
}

/** a full-width button row in a panel (acid when focused); returns the nav handle */
function panelButton(scene, panel, y, text, action, { sub = '' } = {}) {
    const RW = panel.w - RULE;
    let fill, label, small, g;
    const h = navEntry(scene, panel.nav, RW / 2, y, RW, 46, {
        build: (c) => {
            fill = scene.add.rectangle(-RW / 2, 0, RW, 46, TH.bg).setOrigin(0, 0.5).setFillStyle(TH.bg, TH.skin ? 0 : 1);
            g = scene.add.image(-RW / 2 + 32, 0, gear(scene, 8, 8, { hole: 0.32 })).setTint(ACID);
            label = scene.add.text(-RW / 2 + 52, 0, text, { ...ROW_LABEL, fontSize: (TH.rowPx + 1) + 'px' }).setOrigin(0, 0.5);
            small = scene.add.text(RW / 2 - 28, 1, sub, { ...SMALL, letterSpacing: 1, fontSize: '12px' }).setOrigin(1, 0.5);
            c.add([fill, g, label, small]);
        },
        focus: (on) => {
            fill.setFillStyle(on ? TH.onFill : TH.bg, on ? (TH.skin ? 0.92 : 1) : (TH.skin ? 0 : 1));
            label.setColor(on ? TH.onText : css(TH.text));
            small.setColor(on ? TH.onText : css(TH.note));
            g.setTint(on ? TH.onIcon : ACID);
            if (on) tween(scene, g, { angle: g.angle + 45, duration: 240, ease: 'Back.easeOut' });
        },
        press: () => tween(scene, g, { angle: g.angle + 180, duration: 260 }),
        action
    });
    panel.body.add(h.container);
    panel.body.bringToTop(panel.rule);
    return h;
}

/**
 * A settings row: the label on the left, a control on the right; focused = an acid tab and label.
 * control: { build(c, cx), focus(on), adjust(dir), activate() }
 */
function panelRow(scene, panel, y, text, control) {
    const RW = panel.w - RULE;
    let band, tab, label;
    const h = navEntry(scene, panel.nav, RW / 2, y, RW, 46, {
        build: (c) => {
            band = scene.add.rectangle(-RW / 2, 0, RW, 46, TH.rowBand, TH.skin ? 0.85 : 1).setOrigin(0, 0.5).setVisible(false);
            tab = scene.add.rectangle(-RW / 2, 0, 6, 46, ACID).setOrigin(0, 0.5).setVisible(false);
            label = scene.add.text(-RW / 2 + 28, 0, text, ROW_LABEL).setOrigin(0, 0.5);
            c.add([band, tab, label]);
            control.build(c, -RW / 2 + 206, RW / 2 - 30);
        },
        focus: (on) => {
            band.setVisible(on); tab.setVisible(on);
            label.setColor(on ? ACID_CSS : css(TH.text));
            control.focus?.(on);
        },
        delay: 0,
        action: () => control.activate?.(),
        adjust: (dir) => control.adjust?.(dir)
    });
    panel.body.add(h.container);
    panel.body.bringToTop(panel.rule);
    return h;
}

/** a slider: a grey track, the acid part up to a gear knob that rolls along it; drag, click or ←/→ */
function slider(scene, panel, value, onChange) {
    let x0, x1, track, fillBar, knob, zone, v = value, dragging = false;
    const place = () => {
        const kx = x0 + (x1 - x0) * v;
        knob.x = kx;
        knob.angle = v * 540;
        fillBar.width = kx - x0;
    };
    const set = (nv, final) => { v = Phaser.Math.Clamp(nv, 0, 1); place(); onChange(v, final); };
    const fromPointer = (p) => {
        const c = zone.parentContainer;
        return (p.x - panel.body.x - c.x - x0) / (x1 - x0);
    };
    return {
        build(c, a, b) {
            x0 = a + 6; x1 = b - 6;
            track = scene.add.rectangle(x0, 0, x1 - x0, 2, TH.track).setOrigin(0, 0.5);
            fillBar = scene.add.rectangle(x0, 0, 0, 4, ACID).setOrigin(0, 0.5);
            knob = scene.add.image(x0, 0, gear(scene, 10, 8, { hole: 0.32 })).setTint(ACID);
            zone = scene.add.zone((x0 + x1) / 2, 0, x1 - x0 + 24, 40).setInteractive({ useHandCursor: true });
            zone.on('pointerdown', (p, lx, ly, ev) => { ev?.stopPropagation(); dragging = true; set(fromPointer(p), false); });
            scene.input.on('pointermove', (p) => { if (dragging && p.isDown) set(fromPointer(p), false); });
            scene.input.on('pointerup', () => { if (dragging) { dragging = false; set(v, true); } });
            c.add([track, fillBar, knob, zone]);
            place();
        },
        focus(on) { tween(scene, knob, { scale: on ? 1.25 : 1, duration: 120 }); },
        adjust(dir) { set(Math.round((v + dir * 0.05) * 20) / 20, true); },
        setValue(nv) { v = nv; place(); }
    };
}

/** an on/off switch: an outlined box, a square that slides, the state written beside it */
function toggle(scene, value, onChange, words) {
    let box, knob, state, on = value, a;
    const place = () => {
        knob.x = a + (on ? 31 : 11);
        knob.fillColor = on ? ACID : TH.off;
        state.setText(words(on));
    };
    const flip = () => { on = !on; place(); playMenuSound(scene, 'clickSound'); onChange(on); };
    return {
        build(c, x0) {
            a = x0;
            box = scene.add.rectangle(a, 0, 42, 22).setOrigin(0, 0.5).setStrokeStyle(2, TH.text);
            knob = scene.add.rectangle(a + 11, 0, 14, 14, ACID);
            state = scene.add.text(a + 56, 0, '', { ...SMALL, fontSize: '13px', letterSpacing: 1 }).setOrigin(0, 0.5);
            const z = scene.add.zone(a + 21, 0, 50, 34).setInteractive({ useHandCursor: true });
            z.on('pointerdown', (p, lx, ly, ev) => { ev?.stopPropagation(); flip(); });
            c.add([box, knob, state, z]);
            place();
        },
        activate: flip,
        adjust: () => flip(),
        setValue(nv) { on = nv; place(); }
    };
}

/** ‹ value ›: arrows step through the choices (click them, or ←/→, or Enter for the next) */
function chooser(scene, label, step) {
    // Cinzel's lowercase are small caps that smudge at this size (its h reads as II): capitals in the glass theme
    const text = () => (TH.glass ? label().toUpperCase() : label());
    let val, left, right;
    const arrow = (x, dir) => {
        const t = scene.add.triangle(x, 0, 0, -7, 0, 7, 10 * dir, 0, TH.text).setOrigin(dir > 0 ? 0 : 1, 0.5);
        const z = scene.add.zone(x, 0, 30, 34).setInteractive({ useHandCursor: true });
        z.on('pointerover', () => t.setFillStyle(ACID));
        z.on('pointerout', () => t.setFillStyle(TH.text));
        z.on('pointerdown', (p, lx, ly, ev) => { ev?.stopPropagation(); playMenuSound(scene, 'clickSound'); step(dir); val?.setText(text()); });
        return [t, z];
    };
    return {
        build(c, a, b) {
            left = arrow(a + 4, -1); right = arrow(b - 4, 1);
            val = scene.add.text((a + b) / 2, 0, text(), ROW_LABEL).setOrigin(0.5);
            c.add([...left, ...right, val]);
        },
        focus(on) { val.setColor(on ? ACID_CSS : css(TH.text)); },
        activate() { playMenuSound(scene, 'clickSound'); step(1); val.setText(text()); },
        adjust(dir) { playMenuSound(scene, 'clickSound'); step(dir); val.setText(text()); },
        refresh() { val.setText(text()); }
    };
}

/**
 * The settings in a band panel: music, sounds, fullscreen, language, dialog style, the panels' look, Confirm.
 * deps: { t, getSetting, setSetting, isFullscreen, languages: {code, name}[], language(), setLanguage(code),
 *         dialogStyle(), cycleDialogStyle(dir), panelSet(), cyclePanelSet(dir) }
 */
export function createBandSettings(scene, { x, w, onClose, shadeAll }, deps) {
    const panel = createBandPanel(scene, { x, w, title: deps.t('ui.settings.title'), onClose, shadeAll });
    const Y = [150, 200, 250, 300, 350, 400], CONFIRM = 476;
    const up = (s) => s.toUpperCase();
    const music = slider(scene, panel, deps.getSetting('music'), (v) => deps.setSetting('music', v));
    const sfx = slider(scene, panel, deps.getSetting('sfx'), (v, final) => {
        deps.setSetting('sfx', v);
        if (final) playMenuSound(scene, 'clickSound');
    });
    const full = toggle(scene, deps.getSetting('fullscreen') !== false, (on) => deps.setSetting('fullscreen', on),
        (on) => up(deps.t(on ? 'ui.settings.on' : 'ui.settings.off')));
    const langName = () => (deps.languages.find(l => l.code === deps.language()) || {}).name || '';
    const lang = chooser(scene, langName, (dir) => {
        const i = deps.languages.findIndex(l => l.code === deps.language());
        const next = deps.languages[(i + dir + deps.languages.length) % deps.languages.length];
        if (next && next.code !== deps.language()) deps.setLanguage(next.code);
    });
    const style = chooser(scene, () => deps.t(`ui.settings.dialogStyles.${deps.dialogStyle()}`), (dir) => deps.cycleDialogStyle(dir));
    const inv = chooser(scene, () => deps.t(`ui.settings.panelSets.${deps.panelSet()}`), (dir) => deps.cyclePanelSet(dir));
    panelRow(scene, panel, Y[0], up(deps.t('ui.settings.music')), music);
    panelRow(scene, panel, Y[1], up(deps.t('ui.settings.sounds')), sfx);
    panelRow(scene, panel, Y[2], up(deps.t('ui.settings.fullscreen')), full);
    panelRow(scene, panel, Y[3], up(deps.t('ui.settings.language')), lang);
    panelRow(scene, panel, Y[4], up(deps.t('ui.settings.dialogStyle')), style);
    panelRow(scene, panel, Y[5], up(deps.t('ui.settings.panels')), inv);
    panelButton(scene, panel, CONFIRM, up(deps.t('ui.settings.confirm')), () => onClose?.());
    return {
        panel,
        /** re-read the real state (F11 can change fullscreen behind the setting's back) */
        refresh() {
            music.setValue(deps.getSetting('music'));
            sfx.setValue(deps.getSetting('sfx'));
            style.refresh();
            inv.refresh();
            deps.isFullscreen().then(on => full.setValue(on));
        }
    };
}

/**
 * Save slots in a band panel: one row per slot (its name, its date or a note), a pager if there are more than fit;
 * the Load panel by default, the in-game Save panel with titleKey 'ui.saveLoad.saveTitle'.
 * list(): [{ name, date, onLoad }]  (onLoad: what a click on the row does)
 */
export function createBandLoad(scene, { x, w, onClose, perPage = 6, titleKey = 'ui.saveLoad.loadTitle', shadeAll }, { t, list }) {
    const panel = createBandPanel(scene, { x, w, title: t(titleKey), onClose, shadeAll });
    const none = scene.add.text(28, 170, t('ui.saveLoad.noSaves'), { ...ROW_LABEL, color: css(TH.note) }).setVisible(false);
    panel.body.add(none);
    let page = 0, rows = [];
    const populate = () => {
        // unfocus first, destroy after: clear() re-colours the focused row's texts, and a destroyed Text has no canvas
        // (the TypeError froze the whole game on every overwrite of a used save slot)
        panel.nav.clear();
        rows.forEach(r => r.container.destroy());
        rows = [];
        const saves = list();
        const pages = Math.max(1, Math.ceil(saves.length / perPage));
        page = Phaser.Math.Clamp(page, 0, pages - 1);
        none.setVisible(saves.length === 0);
        saves.slice(page * perPage, (page + 1) * perPage).forEach((s, i) => {
            rows.push(panelButton(scene, panel, 158 + i * 52, s.name, s.onLoad, { sub: s.date }));
        });
        if (pages > 1) {
            const pager = chooser(scene, () => t('ui.saveLoad.page', { n: page + 1, total: pages }).toUpperCase(), (dir) => {
                page = (page + dir + pages) % pages;
                scene.time.delayedCall(0, () => { populate(); panel.nav.focus(rows[rows.length - 1]); });
            });
            rows.push(panelRow(scene, panel, 158 + perPage * 52 + 20, '', pager));
        }
        if (panel.open && rows.length) panel.nav.focus(rows[0]);
    };
    return {
        panel,
        show() { page = 0; panel.show(); populate(); },
        /** re-draw the rows (a slot armed for overwriting), keeping the focus where it was */
        refresh() {
            const i = panel.nav.index;
            populate();
            if (i >= 0 && rows[i]) panel.nav.focus(rows[i]);
        }
    };
}
