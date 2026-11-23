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
 */
import { MenuNav, playMenuSound } from '../utils/menuKit.js';

export const ACID = 0xe6ff2e;
const ACID_CSS = '#e6ff2e';
export const RULE = 4;
const DEPTH = { title: 1.6, shade: 1.65, panel: 1.7, band: 1.8, ui: 2 };   // the title under a panel's shade
const LABEL = { fontFamily: 'Space Grotesk', fontStyle: 'bold', fontSize: '19px', color: '#ffffff', letterSpacing: 1 };
const SMALL = { fontFamily: 'Space Grotesk', fontStyle: 'bold', fontSize: '11px', color: '#8f8f8f', letterSpacing: 4 };

export function preloadMainMenuBand(scene) {
    scene.load.font('Bebas Neue', 'assets/fonts/BebasNeue.ttf', 'truetype');
    scene.load.font('Space Grotesk', 'assets/fonts/SpaceGrotesk.ttf', 'truetype', { weight: '300 700' });
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
    const TW = 262, PX = 26, PY = 16, TOP = 22;
    const w = TW + 2 * PX, x0 = Math.round(x - w / 2);
    const yU = TOP + PY;
    scene.add.text(x0 + PX, yU, 'UPPER', { fontFamily: 'Space Grotesk', fontStyle: 'bold', fontSize: '13px', color: ACID_CSS, letterSpacing: 9 })
        .setDepth(DEPTH.title);
    const { bottom } = gearTitle(scene, x0 + PX, yU + 19, TW, DEPTH.title);
    scene.add.rectangle(x0 + PX, bottom + 13, 30, 4, ACID).setOrigin(0, 0.5).setDepth(DEPTH.title);
    scene.add.text(x0 + PX + 40, bottom + 13, subtitle.toUpperCase(), { ...SMALL, color: '#d8d8d8' }).setOrigin(0, 0.5).setDepth(DEPTH.title);
    const h = bottom + 13 + 6 + PY - TOP;
    // the shade: a dark rectangle whose edges fade out (smoothstep over the outer third)
    const key = tex(scene, 'mmSoftRect', 128, 128, (c, tw, th) => {
        const img = c.createImageData(tw, th);
        const ramp = (t) => { const u = Math.min(1, Math.min(t, 1 - t) / 0.34); return u * u * (3 - 2 * u); };
        for (let yy = 0; yy < th; yy++) for (let xx = 0; xx < tw; xx++) {
            const i = (yy * tw + xx) * 4;
            img.data[i] = img.data[i + 1] = img.data[i + 2] = 0;
            img.data[i + 3] = Math.round(255 * ramp((xx + 0.5) / tw) * ramp((yy + 0.5) / th));
        }
        c.putImageData(img, 0, 0);
    });
    scene.add.image(x, TOP + h / 2, key).setDisplaySize(w + 110, h + 70).setAlpha(0.8).setDepth(DEPTH.title - 0.05);
}

/**
 * @param {{ width: number, items: {label, action, enabled}[] }} opts
 * @returns {{ nav: MenuNav, entries, latch(i|null) }}
 */
export function createMainMenuBand(scene, { width: BW, items }) {
    const H = scene.scale.height;
    const RX = BW - RULE;                         // the rule's left edge; the entries run from 0 to it
    const nav = new MenuNav(scene);
    const at = (o, d = DEPTH.ui) => o.setDepth(d);

    at(scene.add.rectangle(0, 0, BW, H, 0x000000).setOrigin(0), DEPTH.band);
    at(scene.add.rectangle(RX, 0, RULE, H, ACID).setOrigin(0), DEPTH.band + 0.05);

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
    myc.lineStyle(1, ACID, 1).fillStyle(ACID, 1);
    for (const [y0, dir] of [[40, 1], [120, -1], [200, 1], [290, 1], [330, -1], [420, 1], [470, -1], [560, -1]]) {
        thread(RX - 1, y0 + r() * 16, dir * Math.PI / 2 + dir * (0.25 + r() * 0.2), 40 + r() * 60, 0);
    }
    myc.setAlpha(0.3);
    scene.tweens.add({ targets: myc, alpha: 0.5, duration: 2600, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });

    // the fungus garden at the foot, and the spores a click puffs out of the focused entry's mushrooms
    const garden = createFungusGarden(scene, { RX, floorY: H - 4, depth: DEPTH.band + 0.05 });
    sporeTex(scene);
    const puff = at(scene.add.particles(0, 0, 'mmSpore', {
        emitting: false, speed: { min: 20, max: 70 }, angle: { min: 215, max: 325 }, lifespan: { min: 500, max: 900 },
        scale: { start: 1.3, end: 0.3 }, alpha: { start: 1, end: 0 }, tint: ACID, gravityY: -10
    }), DEPTH.ui + 0.1);

    // the focused entry's gear spins
    const entries = [];
    const update = () => entries.forEach(e => { if (e.spin) e.gear.angle += e.spin; });
    scene.events.on('update', update);
    scene.events.once('shutdown', () => scene.events.off('update', update));

    // the entries
    const ROW = 46, GAP = 12, top = 120;
    items.forEach((item, i) => {
        const y = top + i * (ROW + GAP) + ROW / 2;
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
                // a pulse runs down the rule into the garden, which stirs
                const p = at(scene.add.image(RX + RULE / 2, y, glowTex(scene)).setTint(ACID).setBlendMode(Phaser.BlendModes.ADD)
                    .setDisplaySize(26, 60), DEPTH.band + 0.06);
                scene.tweens.add({ targets: p, y: garden.top, alpha: { from: 1, to: 0.3 }, duration: 380, ease: 'Cubic.easeIn', onComplete: () => {
                    p.destroy();
                    garden.react();
                } });
            },
            enable: (on) => { label.setColor(on ? '#ffffff' : '#505050'); e.gear.setTint(on ? ACID : 0x3a3a3a); },
            action: item.action
        });
        h.container.setDepth(DEPTH.ui);
        h.setEnabled(item.enabled !== false);
        e.handle = h;
        entries.push(e);
    });

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

// ---------------------------------------------------------------------------------------------------------------
// the fungus garden: real odd species, drawn flat in the band's colours

const WHITE = '#efeee6', BONE = '#cfcdc2';

const FUNGI = {
    // Clathrus ruber, the basket stinkhorn: a hollow lattice ball on the cup it hatched from
    basket: { w: 46, h: 44, draw(c, w, h) {
        const cx = w / 2, cy = 20, rx = 20, ry = 19;
        c.fillStyle = ACID_CSS; c.beginPath(); c.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2); c.fill();
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
            c.fillStyle = ACID_CSS;
            c.beginPath(); c.moveTo(x - r, h - hh + r * 0.9); c.quadraticCurveTo(x, h - hh - r * 1.3, x + r, h - hh + r * 0.9); c.closePath(); c.fill();
        });
    } },
};

const FUNGUS_RES = 2;            // drawn at twice the size, shown scaled: crisp edges
function fungus(scene, name) {
    const f = FUNGI[name];
    return tex(scene, 'mmFungus_' + name, f.w * FUNGUS_RES, f.h * FUNGUS_RES, (c) => { c.scale(FUNGUS_RES, FUNGUS_RES); f.draw(c, f.w, f.h); });
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
        const g = scene.add.image(x, y, glowTex(scene)).setTint(ACID).setBlendMode(Phaser.BlendModes.ADD)
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
    [[-12, 0, 1.7], [3, 1, 1.35], [17, 0, 1.05], [30, 2, 1.4], [42, 1, 0.8]].forEach(([dx, kind, sc]) => {
        scene.add.image(cx + dx, floorY, shroom(scene, kind)).setOrigin(0.5, 1).setScale(sc).setTint(ACID).setDepth(depth);
    });
    scene.add.particles(0, 0, 'mmSpore', {
        x: { min: cx - 14, max: cx + 38 }, y: floorY - 16, speedY: { min: -22, max: -10 }, speedX: { min: -4, max: 4 },
        lifespan: { min: 2600, max: 4200 }, frequency: 650, scale: { start: 1, end: 0.4 }, alpha: { start: 0.9, end: 0 }, tint: ACID
    }).setDepth(depth + 0.01);
    const puff = scene.add.particles(0, 0, 'mmSpore', {
        emitting: false, speed: { min: 20, max: 70 }, angle: { min: 215, max: 325 }, lifespan: { min: 500, max: 900 },
        scale: { start: 1.3, end: 0.3 }, alpha: { start: 1, end: 0 }, tint: ACID, gravityY: -10
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
// the panels that slide out of the band

/**
 * A black panel x..x+w, full height, sliding out from under the band; the painting beside it dims (a click there
 * closes it). Rows are added with the helpers below; contents go into panel.body (local coords, x from the left edge).
 */
export function createBandPanel(scene, { x, w, title, onClose }) {
    const W = scene.scale.width, H = scene.scale.height;
    const shade = scene.add.rectangle(x, 0, W - x, H, 0x000000).setOrigin(0).setAlpha(0).setDepth(DEPTH.shade)
        .setVisible(false).setInteractive();
    shade.on('pointerdown', () => onClose?.());
    const body = scene.add.container(x, 0).setDepth(DEPTH.panel).setVisible(false);
    body.add(scene.add.rectangle(0, 0, w, H, 0x000000).setOrigin(0).setInteractive());   // clicks on the panel stay here
    body.add(scene.add.rectangle(w - RULE, 0, RULE, H, ACID).setOrigin(0));
    const head = scene.add.text(28, 34, title, { fontFamily: 'Bebas Neue', fontSize: '62px', color: '#ffffff', padding: { y: 4 } });
    body.add(head);
    body.add(scene.add.rectangle(28, head.y + head.height + 6, 30, 4, ACID).setOrigin(0, 0.5));
    // a cross to close it (for the mouse; ESC and a click on the painting do too)
    const cross = scene.add.graphics();
    const drawCross = (col) => { cross.clear().lineStyle(3, col, 1).lineBetween(-9, -9, 9, 9).lineBetween(-9, 9, 9, -9); };
    drawCross(0xffffff);
    const cz = scene.add.zone(w - RULE - 34, 56, 40, 40).setInteractive({ useHandCursor: true });
    cross.setPosition(cz.x, cz.y);
    cz.on('pointerover', () => drawCross(ACID));
    cz.on('pointerout', () => drawCross(0xffffff));
    cz.on('pointerdown', (p, lx, ly, ev) => { ev?.stopPropagation(); playMenuSound(scene, 'clickSound'); onClose?.(); });
    body.add([cross, cz]);

    const nav = new MenuNav(scene);
    nav.active = false;
    const panel = {
        body, nav, w, x, open: false,
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

const ROW_LABEL = { fontFamily: 'Space Grotesk', fontStyle: 'bold', fontSize: '16px', color: '#ffffff', letterSpacing: 1 };

/** a full-width button row in a panel (acid when focused); returns the nav handle */
function panelButton(scene, panel, y, text, action, { sub = '' } = {}) {
    const RW = panel.w - RULE;
    let fill, label, small, g;
    const h = navEntry(scene, panel.nav, RW / 2, y, RW, 46, {
        build: (c) => {
            fill = scene.add.rectangle(-RW / 2, 0, RW, 46, 0x000000).setOrigin(0, 0.5);
            g = scene.add.image(-RW / 2 + 32, 0, gear(scene, 8, 8, { hole: 0.32 })).setTint(ACID);
            label = scene.add.text(-RW / 2 + 52, 0, text, { ...ROW_LABEL, fontSize: '17px' }).setOrigin(0, 0.5);
            small = scene.add.text(RW / 2 - 28, 1, sub, { ...SMALL, letterSpacing: 1, fontSize: '12px' }).setOrigin(1, 0.5);
            c.add([fill, g, label, small]);
        },
        focus: (on) => {
            fill.fillColor = on ? ACID : 0x000000;
            label.setColor(on ? '#000000' : '#ffffff');
            small.setColor(on ? '#000000' : '#8f8f8f');
            g.setTint(on ? 0x000000 : ACID);
            if (on) tween(scene, g, { angle: g.angle + 45, duration: 240, ease: 'Back.easeOut' });
        },
        press: () => tween(scene, g, { angle: g.angle + 180, duration: 260 }),
        action
    });
    panel.body.add(h.container);
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
            band = scene.add.rectangle(-RW / 2, 0, RW, 46, 0x161616).setOrigin(0, 0.5).setVisible(false);
            tab = scene.add.rectangle(-RW / 2, 0, 6, 46, ACID).setOrigin(0, 0.5).setVisible(false);
            label = scene.add.text(-RW / 2 + 28, 0, text, ROW_LABEL).setOrigin(0, 0.5);
            c.add([band, tab, label]);
            control.build(c, -RW / 2 + 206, RW / 2 - 30);
        },
        focus: (on) => {
            band.setVisible(on); tab.setVisible(on);
            label.setColor(on ? ACID_CSS : '#ffffff');
            control.focus?.(on);
        },
        delay: 0,
        action: () => control.activate?.(),
        adjust: (dir) => control.adjust?.(dir)
    });
    panel.body.add(h.container);
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
            track = scene.add.rectangle(x0, 0, x1 - x0, 2, 0x4a4a4a).setOrigin(0, 0.5);
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
        knob.fillColor = on ? ACID : 0x6a6a6a;
        state.setText(words(on));
    };
    const flip = () => { on = !on; place(); playMenuSound(scene, 'clickSound'); onChange(on); };
    return {
        build(c, x0) {
            a = x0;
            box = scene.add.rectangle(a, 0, 42, 22).setOrigin(0, 0.5).setStrokeStyle(2, 0xffffff);
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
function chooser(scene, text, step) {
    let val, left, right;
    const arrow = (x, dir) => {
        const t = scene.add.triangle(x, 0, 0, -7, 0, 7, 10 * dir, 0, 0xffffff).setOrigin(dir > 0 ? 0 : 1, 0.5);
        const z = scene.add.zone(x, 0, 30, 34).setInteractive({ useHandCursor: true });
        z.on('pointerover', () => t.setFillStyle(ACID));
        z.on('pointerout', () => t.setFillStyle(0xffffff));
        z.on('pointerdown', (p, lx, ly, ev) => { ev?.stopPropagation(); playMenuSound(scene, 'clickSound'); step(dir); val?.setText(text()); });
        return [t, z];
    };
    return {
        build(c, a, b) {
            left = arrow(a + 4, -1); right = arrow(b - 4, 1);
            val = scene.add.text((a + b) / 2, 0, text(), { ...ROW_LABEL, fontSize: '16px' }).setOrigin(0.5);
            c.add([...left, ...right, val]);
        },
        focus(on) { val.setColor(on ? ACID_CSS : '#ffffff'); },
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
export function createBandSettings(scene, { x, w, onClose }, deps) {
    const panel = createBandPanel(scene, { x, w, title: deps.t('ui.settings.title'), onClose });
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
export function createBandLoad(scene, { x, w, onClose, perPage = 6, titleKey = 'ui.saveLoad.loadTitle' }, { t, list }) {
    const panel = createBandPanel(scene, { x, w, title: t(titleKey), onClose });
    const none = scene.add.text(28, 170, t('ui.saveLoad.noSaves'), { ...ROW_LABEL, color: '#8f8f8f' }).setVisible(false);
    panel.body.add(none);
    let page = 0, rows = [];
    const populate = () => {
        rows.forEach(r => r.container.destroy());
        panel.nav.clear();
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
