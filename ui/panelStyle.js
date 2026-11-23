/**
 * panelStyle.js — the two looks of the game's panels (the inventory, the shops, the journal, the quest log), one
 * setting for all four ('panelSet', systems/GameSettings.js; Settings: "Vzhled panelů: Učedník / Úřad"):
 *
 *   apprentice  the apprentice's things (default): the bag tipped out, his notebook, a corkboard of errands, a market
 *               stall. Handwriting (Caveat) for his notes, Georgia for print; cream paper; the chosen thing is ringed
 *               in RED PENCIL; whatever was learned or done later is in GREEN INK; tabs are coloured sticky notes
 *   office      the bureaucracy of Shed 521: the curiosity cabinet, typed dossiers, official forms, a mail-order
 *               catalogue. Typewriter (Departure Mono) and Georgia; lined index cards; the chosen thing is marked with
 *               RED INK brackets; later additions are in BLUE BIRO; tabs are manila folder tabs
 *
 * Every panel puts its detail (the chosen thing's text) on a paper on the RIGHT (DETAIL), and draws the shared pieces
 * with these helpers so the four panels match: detailCard, markChosen, drawTabs, plus the colours and text styles in
 * LOOK. Keys are the same everywhere: arrows move, Enter acts, ←/→ or Tab change tabs, PgUp / PgDn scroll or page.
 */
import { getSetting } from '../systems/GameSettings.js';

export const PANEL_SETS = ['apprentice', 'office'];
export function panelSet() {
    const s = getSetting('panelSet');
    return PANEL_SETS.includes(s) ? s : PANEL_SETS[0];
}

export const LOOK = {
    apprentice: {
        HAND: 'Caveat', PRINT: 'Georgia',
        PAPER: 0xefe3c8, INK: '#2a1d10', INK_SOFT: '#5a4630',
        MARK: 0xb3322a, MARK_CSS: '#b3322a',            // red pencil: the chosen thing
        LATER: '#2f6b3a', LATER_HEX: 0x2f6b3a,           // green ink: learned / done later
        DETAIL: { x: 790, y: 64, w: 250, h: 476 },
        text: {
            title: { fontFamily: 'Caveat', fontStyle: 'bold', fontSize: '28px', color: '#2a1d10' },
            kind: { fontFamily: 'Caveat', fontSize: '19px', color: '#8a6a45' },
            body: { fontFamily: 'Georgia', fontStyle: 'italic', fontSize: '14px', color: '#33241a', lineSpacing: 3 },
            hand: { fontFamily: 'Caveat', fontSize: '21px', color: '#2a1d10', lineSpacing: 0 },
            later: { fontFamily: 'Caveat', fontSize: '21px', color: '#2f6b3a', lineSpacing: 0 },
            small: { fontFamily: 'Caveat', fontSize: '18px', color: '#5a4630' },
            label: { fontFamily: 'Caveat', fontStyle: 'bold', fontSize: '18px', color: '#2a1d10' },
            button: { fontFamily: 'Caveat', fontStyle: 'bold', fontSize: '22px', color: '#f3e2c4' }
        }
    },
    office: {
        TYPE: 'Departure Mono', PRINT: 'Georgia',
        PAPER: 0xf1e9d4, INK: '#241a10', INK_SOFT: '#5a4a38',
        MARK: 0xa8322a, MARK_CSS: '#a8322a',            // red ink: the chosen thing
        LATER: '#2448a8', LATER_HEX: 0x2448a8,           // blue biro: added later
        DETAIL: { x: 728, y: 64, w: 312, h: 476 },
        text: {
            title: { fontFamily: 'Georgia', fontStyle: 'bold', fontSize: '19px', color: '#241a10' },
            kind: { fontFamily: 'Departure Mono', fontSize: '11px', color: '#6b5b45' },
            body: { fontFamily: 'Georgia', fontSize: '14px', color: '#2a2118', lineSpacing: 3 },
            hand: { fontFamily: 'Georgia', fontSize: '14px', color: '#2a2118', lineSpacing: 3 },
            later: { fontFamily: 'Georgia', fontSize: '14px', color: '#2448a8', lineSpacing: 3 },
            small: { fontFamily: 'Departure Mono', fontSize: '11px', color: '#6b5b45' },
            label: { fontFamily: 'Georgia', fontStyle: 'italic', fontSize: '11px', color: '#3b2b1c' },
            button: { fontFamily: 'Georgia', fontStyle: 'bold', fontSize: '14px', color: '#a8322a', letterSpacing: 2 }
        }
    }
};

function tex(scene, key, w, h, draw) {
    if (!scene.textures.exists(key)) {
        const t = scene.textures.createCanvas(key, w, h);
        draw(t.getContext(), w, h);
        t.refresh();
        t.setFilter(Phaser.Textures.FilterMode.LINEAR);
    }
    return key;
}
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
function speckle(c, w, h, n, col, seed, a0 = 0.03, a1 = 0.08) {
    const r = rng(seed);
    for (let i = 0; i < n; i++) {
        c.fillStyle = `rgba(${col},${a0 + r() * (a1 - a0)})`;
        c.fillRect(r() * w, r() * h, 1 + r() * 2, 1 + r() * 1.5);
    }
}

/**
 * The detail's paper in box { x, y, w, h } (default: LOOK[set].DETAIL): a pinned cream note (apprentice) or a lined index
 * card with a red head line at y 52 and a paper clip (office). Returns { frame, body } — put the texts into body (a
 * container whose 0,0 is the paper's top-left; the paper is tilted a hair).
 */
export function detailCard(scene, set, box = LOOK[set].DETAIL, depth = 2) {
    const { x, y, w, h } = box;
    const rot = set === 'office' ? 0 : -0.015;          // the office's card lies straight: a tilted pixel font shears
    const shadow = tex(scene, `psShadow_${w}_${h}`, w + 24, h + 24, (c, tw, th) => { c.filter = 'blur(6px)'; c.fillStyle = 'rgba(0,0,0,0.65)'; c.fillRect(12, 12, tw - 24, th - 24); });
    scene.add.image(x + w / 2 + 4, y + h / 2 + 7, shadow).setRotation(rot).setDepth(depth - 0.1);
    const frame = scene.add.container(x + w / 2, y + h / 2).setRotation(rot).setDepth(depth);
    frame.add(scene.add.image(0, 0, tex(scene, `psCard_${set}_${w}_${h}`, w, h, (c) => {
        if (set === 'office') {
            c.fillStyle = '#f1e9d4'; c.fillRect(0, 0, w, h);
            speckle(c, w, h, w * h / 50, '120,90,40', 4);
            c.strokeStyle = 'rgba(200,60,50,0.75)'; c.lineWidth = 1.5; c.beginPath(); c.moveTo(0, 52); c.lineTo(w, 52); c.stroke();
            c.strokeStyle = 'rgba(110,150,190,0.4)'; c.lineWidth = 1;
            for (let yy = 74; yy < h - 8; yy += 21) { c.beginPath(); c.moveTo(0, yy); c.lineTo(w, yy); c.stroke(); }
        } else {
            c.fillStyle = '#efe3c8'; c.fillRect(0, 0, w, h);
            speckle(c, w, h, w * h / 50, '120,80,30', 31);
            c.fillStyle = 'rgba(120,80,30,0.12)'; c.beginPath(); c.arc(w * 0.9, h * 0.97, 30, 0, Math.PI * 2); c.fill();     // a coffee ring
            c.strokeStyle = 'rgba(120,80,30,0.25)'; c.lineWidth = 2; c.beginPath(); c.arc(w * 0.9, h * 0.97, 30, 0, Math.PI * 2); c.stroke();
        }
    })));
    if (set === 'office') {                          // a paper clip on the top edge
        const g = scene.add.graphics().lineStyle(3, 0x8d949a, 1);
        g.strokeRoundedRect(-w / 2 + 30, -h / 2 - 12, 18, 44, 9).strokeRoundedRect(-w / 2 + 34, -h / 2 - 6, 10, 30, 5);
        frame.add(g);
    } else {
        frame.add(scene.add.circle(0, -h / 2 + 10, 6, 0xb0302a).setStrokeStyle(1, 0x501010));   // the pin
    }
    const body = scene.add.container(-w / 2, -h / 2);
    frame.add(body);
    return { frame, body, x, y, w, h };
}

/**
 * Mark the chosen thing around (cx, cy), w x h: a red pencil ring (apprentice) or red ink corner brackets (office).
 * Returns the game object (add it to your layer).
 */
export function markChosen(scene, set, cx, cy, w, h) {
    if (set === 'office') {
        const g = scene.add.graphics().lineStyle(2.5, LOOK.office.MARK, 1);
        const a = w / 2, b = h / 2, l = Math.min(14, w / 4, h / 3);
        for (const [sx, sy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
            g.lineBetween(cx + sx * a, cy + sy * b, cx + sx * (a - l), cy + sy * b);
            g.lineBetween(cx + sx * a, cy + sy * b, cx + sx * a, cy + sy * (b - l));
        }
        return g;
    }
    const W = Math.round(w + 16), H = Math.round(h + 12);
    return scene.add.image(cx, cy, tex(scene, `psRing_${W}_${H}`, W, H, (c) => {
        c.strokeStyle = 'rgba(179,50,42,0.9)'; c.lineWidth = 2.6; c.lineCap = 'round';
        const r = rng(W * 31 + H);
        c.beginPath();                                // a pencil loop: one and a bit turns, not quite closed
        for (let i = 0; i <= 70; i++) {
            const t = i / 62 * Math.PI * 2 - 0.6, j = 1 + (r() - 0.5) * 0.05 + (i > 60 ? 0.04 : 0);
            const x = W / 2 + Math.cos(t) * (W / 2 - 4) * j, y = H / 2 + Math.sin(t) * (H / 2 - 4) * j;
            if (i) c.lineTo(x, y); else c.moveTo(x, y);
        }
        c.stroke();
    }));
}

const STICKY = [0xf2d15c, 0x8fd0a8, 0x8ec3e6, 0xe9a3b8, 0xf0a868, 0xb8a3e0];

/**
 * Tabs at (x, y): sticky notes (apprentice) or manila folder tabs (office); vertical = stacked down a right edge
 * (the notebook). tabs = [{ label, badge }], active index, onPick(i). Adds to `layer` (a container or a scene);
 * returns the x / y after the last tab. Clicks only (pointerdown), so re-drawing them each redraw is fine.
 */
export function drawTabs(scene, set, layer, x, y, tabs, active, onPick, { vertical = false } = {}) {
    const add = (o) => { (layer.add ? layer : scene).add(o); return o; };
    let tx = x, ty = y;
    tabs.forEach((t, i) => {
        const on = i === active;
        const txt = scene.add.text(0, 0, set === 'office' ? t.label.toUpperCase() : t.label, set === 'office'
            ? { fontFamily: 'Departure Mono', fontSize: '11px', color: '#2a1d10' }      // (letter spacing breaks the pixel font's M)
            : { fontFamily: 'Caveat', fontStyle: 'bold', fontSize: '19px', color: '#2a1d10' }).setOrigin(0.5);
        const w = vertical ? 86 : txt.width + 26, h = vertical ? 34 : (set === 'office' ? 22 : 28);
        const cx = vertical ? tx + w / 2 + (on ? 0 : 8) : tx + w / 2, cy = vertical ? ty + h / 2 : ty + (on ? -3 : 0);
        let bg;
        if (set === 'office') {
            bg = scene.add.graphics().fillStyle(on ? 0xe8d39a : 0xc9b07a, 1).lineStyle(1, 0x6a5430, 1);
            const pts = [{ x: cx - w / 2, y: cy + h / 2 }, { x: cx - w / 2 + 6, y: cy - h / 2 }, { x: cx + w / 2 - 6, y: cy - h / 2 }, { x: cx + w / 2, y: cy + h / 2 }];
            bg.fillPoints(pts, true).strokePoints(pts, true);
        } else {
            bg = scene.add.rectangle(cx, cy, w, h, STICKY[i % STICKY.length]).setRotation(on ? 0 : ((i % 3) - 1) * 0.035)
                .setStrokeStyle(1, 0x000000, 0.15);
            if (!on) bg.setAlpha(0.88);
        }
        add(bg);
        txt.setPosition(cx, cy);
        add(txt);
        if (t.badge) add(scene.add.circle(cx + w / 2 - 6, cy - h / 2 + 5, 5, 0xb0302a).setStrokeStyle(1, 0x501010));
        const z = add(scene.add.zone(cx, cy, w, h + 4).setInteractive({ useHandCursor: true }));
        z.on('pointerdown', () => { if (i !== active) onPick(i); });
        if (vertical) ty += h + 6; else tx += w + (set === 'office' ? 2 : 8);
    });
    return vertical ? ty : tx;
}
