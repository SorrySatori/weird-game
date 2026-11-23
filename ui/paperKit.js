/**
 * paperKit.js — the overlay scene the game's panels open in (PaperScreenScene: one panel at a time above the game,
 * opening another closes the first) and the inventory's screen (gridScreen), in the look of the panel set chosen in
 * the Settings (ui/panelStyle.js): the apprentice's bag tipped out on a leather mat ('desk'), or the office's
 * curiosity cabinet, a walnut drawer under glass ('cabinet'). The shops, the journal and the quest log draw their own
 * screens (ui/panels/*) with the same shared pieces.
 *
 * gridScreen: hover shows an item while the pointer is over it, a click chooses it, and the detail falls back to the
 * chosen one (hover is worked out from the pointer's position: zones re-made on every redraw never send their
 * pointerout). Keys: arrows move, Enter acts, PgUp / PgDn page; ESC (GameMenu), the owner's key or the cross close.
 */
import { playMenuSound } from '../utils/menuKit.js';
import { panelSet, detailCard, markChosen, LOOK, grime, panelBackdrop, scrapTex } from './panelStyle.js';

/** the inventory's style for the panel set (ui/panelStyle.js): the apprentice's bag on a desk, the office's cabinet */
export function paperStyle() {
    return panelSet() === 'office' ? 'cabinet' : 'desk';
}

export const SERIF = 'Georgia', MONO = 'Departure Mono';
const INK = '#241a10', INK_SOFT = '#5a4a38', RED = '#a8322a';

// ---------------------------------------------------------------------------------------------------------------
// small helpers

export function tex(scene, key, w, h, draw) {
    if (!scene.textures.exists(key)) {
        const t = scene.textures.createCanvas(key, w, h);
        draw(t.getContext(), w, h);
        t.refresh();
        t.setFilter(Phaser.Textures.FilterMode.LINEAR);
    }
    return key;
}

export function rng(seed) {
    let a = seed >>> 0;
    return () => {
        a = (a + 0x6D2B79F5) >>> 0;
        let t = a;
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}
export const hash = (s) => [...String(s)].reduce((h, c) => Math.imul(h ^ c.charCodeAt(0), 16777619), 2166136261) >>> 0;

function speckle(c, w, h, n, col, seed, a0 = 0.03, a1 = 0.08) {
    const r = rng(seed);
    for (let i = 0; i < n; i++) {
        c.fillStyle = `rgba(${col},${a0 + r() * (a1 - a0)})`;
        c.fillRect(r() * w, r() * h, 1 + r() * 2, 1 + r() * 1.5);
    }
}

/** shrink a text's font until it fits maxH */
export function fitHeight(t, maxH, min = 10) {
    let s = parseFloat(t.style.fontSize);
    while (t.height > maxH && s > min) { s -= 1; t.setFontSize(s); }
    return t;
}

/** cut a one-line text to maxW with an ellipsis */
function ellipsize(t, maxW) {
    let s = t.text;
    while (t.width > maxW && s.length > 3) { s = s.slice(0, -1); t.setText(s.trimEnd() + '…'); }
    return t;
}

/** a spec value that may be a function (read each redraw) */
const val = (x) => (typeof x === 'function' ? x() : x);

/** add o to a container and hand back o (Container.add returns the container) */
export const put = (cont, o) => { cont.add(o); return o; };
const tween = (scene, targets, props) => scene.tweens.add({ targets, duration: 160, ease: 'Sine.easeOut', ...props });

/** a container rebuilt on every redraw */
function layer(scene, depth = 2) {
    const c = scene.add.container(0, 0).setDepth(depth);
    return { c, clear() { c.removeAll(true); }, add(o) { c.add(o); return o; } };
}

/** a black silhouette of an icon (a drop shadow) */
function shadowOf(icon, alpha) {
    if (icon.setTintFill) icon.setTintFill(0x000000); else icon.list?.forEach(o => o.setFillStyle?.(0x000000));
    return icon.setAlpha(alpha);
}

// ---------------------------------------------------------------------------------------------------------------
// the pieces: frames, papers, tabs

/** the walnut drawer (x, y, w, h), felt inside, optional compartment dividers (cols x rows); key = cache key */
function cabinetFrame(scene, key, x, y, w, h, { cols = 0, rows = 0, title = '' } = {}) {
    const IN = 24, IW = w - 2 * IN, IH = h - 2 * IN, DIV = 8;
    const art = w === 660 && h === 470 && cols === 5 && rows === 3 && grime(scene, 'cabinet');
    if (art) {                                        // the corroded cabinet (ui_grime.py: its 12 px margin is the overgrowth)
        scene.add.image(x - 24, y - 24, art).setOrigin(0).setScale(2);
        if (title) scene.add.text(x + w / 2, y + 13, title, { fontFamily: MONO, fontSize: '11px', color: '#1e1406' }).setOrigin(0.5).setDepth(1);
        return { IX: x + IN, IY: y + IN, IW, IH, DIV };
    }
    scene.add.image(x, y, tex(scene, key, w, h, (c) => {
        const g = c.createLinearGradient(0, 0, 0, h);
        g.addColorStop(0, '#5a3a22'); g.addColorStop(1, '#3b2414');
        c.fillStyle = g; c.fillRect(0, 0, w, h);
        const r = rng(3);
        for (let i = 0; i < 90; i++) {
            c.strokeStyle = `rgba(20,10,4,${0.12 + r() * 0.15})`; c.lineWidth = 0.6 + r();
            const yy = r() * h; c.beginPath(); c.moveTo(0, yy);
            for (let xx = 0; xx <= w; xx += 40) c.lineTo(xx, yy + Math.sin(xx / 60 + i) * 3);
            c.stroke();
        }
        c.strokeStyle = 'rgba(255,220,170,0.18)'; c.lineWidth = 2; c.strokeRect(2, 2, w - 4, h - 4);
        c.fillStyle = '#1d3024'; c.fillRect(IN, IN, IW, IH);
        c.save(); c.translate(IN, IN); speckle(c, IW, IH, IW * IH / 40, '255,255,255', 9, 0.01, 0.04); speckle(c, IW, IH, IW * IH / 70, '0,0,0', 10, 0.05, 0.12); c.restore();
        c.fillStyle = 'rgba(0,0,0,0.45)'; c.fillRect(IN, IN, IW, 6); c.fillRect(IN, IN, 6, IH);
        if (cols && rows) {
            const CW = (IW - (cols - 1) * DIV) / cols, CH = (IH - (rows - 1) * DIV) / rows;
            for (let i = 1; i < cols; i++) {
                const xx = IN + i * (CW + DIV) - DIV;
                c.fillStyle = '#6b4a2b'; c.fillRect(xx, IN, DIV, IH);
                c.fillStyle = 'rgba(255,220,170,0.25)'; c.fillRect(xx, IN, 2, IH);
            }
            for (let j = 1; j < rows; j++) {
                const yy = IN + j * (CH + DIV) - DIV;
                c.fillStyle = '#6b4a2b'; c.fillRect(IN, yy, IW, DIV);
                c.fillStyle = 'rgba(255,220,170,0.25)'; c.fillRect(IN, yy, IW, 2);
            }
        }
        const hx = w / 2 - 70, hy = h - 14;           // the brass handle
        c.fillStyle = '#7a5a26'; c.fillRect(hx, hy, 140, 12);
        c.fillStyle = '#c9a23a'; c.fillRect(hx + 2, hy + 1, 136, 7);
        c.fillStyle = 'rgba(255,245,200,0.6)'; c.fillRect(hx + 4, hy + 2, 132, 2);
    })).setOrigin(0);
    if (title) {
        const t = scene.add.text(x + w / 2, y + 12, title, { fontFamily: MONO, fontSize: '11px', color: '#2a1d08', letterSpacing: 3 }).setOrigin(0.5).setDepth(1);
        scene.add.rectangle(x + w / 2, y + 12, Math.max(190, t.width + 30), 18, 0xb8913a).setStrokeStyle(1, 0x5a4012).setDepth(0.9);
    }
    return { IX: x + IN, IY: y + IN, IW, IH, DIV };
}

/** the glass over the drawer's inside */
function cabinetGlass(scene, key, x, y, w, h) {
    const art = w === 612 && h === 422 && grime(scene, 'cabinet_glass');
    if (art) return scene.add.image(x, y, art).setOrigin(0).setScale(2).setDepth(3);
    return scene.add.image(x, y, tex(scene, key, w, h, (c) => {
        for (const [x0, ww, a] of [[0.12, 0.08, 0.07], [0.24, 0.03, 0.05], [0.62, 0.12, 0.05]]) {
            c.fillStyle = `rgba(255,255,255,${a})`;
            c.beginPath(); c.moveTo(w * x0, 0); c.lineTo(w * (x0 + ww), 0); c.lineTo(w * (x0 + ww) - h * 0.5, h); c.lineTo(w * x0 - h * 0.5, h); c.closePath(); c.fill();
        }
        c.strokeStyle = 'rgba(255,255,255,0.18)'; c.strokeRect(0.5, 0.5, w - 1, h - 1);
    })).setOrigin(0).setDepth(3);
}

/** a dark table under it all and the mat (leather, or a merchant's green baize) */
function deskMat(scene, key, x, y, w, h, { cloth = 'leather', bag = false } = {}) {
    const { width: W, height: H } = scene.scale;
    const art = cloth === 'leather' && bag && w === 720 && h === 540 && grime(scene, 'desk_mat');
    if (art) {                                        // the rotting workbench, the cracked mouldy mat and the satchel
        panelBackdrop(scene, 'apprentice');
        scene.add.image(x - 24, y - 24, art).setOrigin(0).setScale(2);
        return;
    }
    scene.add.image(0, 0, tex(scene, key, W, H, (c) => {
        c.fillStyle = '#1c130c'; c.fillRect(0, 0, W, H);
        const r = rng(21);
        for (let i = 0; i < 140; i++) {
            c.strokeStyle = `rgba(0,0,0,${0.1 + r() * 0.2})`; c.lineWidth = 0.5 + r() * 1.5;
            const yy = r() * H; c.beginPath(); c.moveTo(0, yy);
            for (let xx = 0; xx <= W; xx += 50) c.lineTo(xx, yy + Math.sin(xx / 90 + i) * 4);
            c.stroke();
        }
        c.fillStyle = 'rgba(0,0,0,0.5)'; c.fillRect(0, 0, W, H);
        c.save(); c.filter = 'blur(8px)'; c.fillStyle = 'rgba(0,0,0,0.7)'; c.fillRect(x + 6, y + 10, w, h); c.restore();
        const [c0, c1, dot] = cloth === 'baize' ? ['#2f5a3c', '#1a3524', '200,255,210'] : ['#5e2a22', '#341510', '255,200,170'];
        const g = c.createRadialGradient(x + w / 2, y + h / 2, 50, x + w / 2, y + h / 2, w * 0.7);
        g.addColorStop(0, c0); g.addColorStop(1, c1);
        c.fillStyle = g; c.beginPath(); c.roundRect(x, y, w, h, 14); c.fill();
        c.save(); c.translate(x, y); speckle(c, w, h, w * h / 55, '0,0,0', 22, 0.05, 0.14); speckle(c, w, h, w * h / 150, dot, 23, 0.02, 0.05); c.restore();
        c.strokeStyle = cloth === 'baize' ? 'rgba(220,200,140,0.5)' : 'rgba(230,190,140,0.55)'; c.lineWidth = 1.5; c.setLineDash([7, 5]);
        c.beginPath(); c.roundRect(x + 12, y + 12, w - 24, h - 24, 9); c.stroke(); c.setLineDash([]);
        if (bag) {                                    // the satchel, tipped over in the top-left corner
            c.save(); c.translate(x + 36, y + 32); c.rotate(-0.22);
            c.fillStyle = 'rgba(0,0,0,0.5)'; c.beginPath(); c.ellipse(70, 112, 82, 18, 0, 0, Math.PI * 2); c.fill();
            c.fillStyle = '#7a5530'; c.beginPath(); c.moveTo(0, 10); c.lineTo(150, 0); c.lineTo(160, 104); c.lineTo(8, 112); c.closePath(); c.fill();
            c.fillStyle = '#5e3f22'; c.beginPath(); c.moveTo(0, 10); c.lineTo(150, 0); c.lineTo(146, 40); c.quadraticCurveTo(76, 60, 4, 48); c.closePath(); c.fill();
            c.fillStyle = '#c9a23a'; c.fillRect(66, 38, 18, 14); c.fillStyle = '#3a2a12'; c.fillRect(72, 42, 6, 6);
            c.strokeStyle = 'rgba(240,200,150,0.5)'; c.setLineDash([4, 4]); c.beginPath(); c.moveTo(10, 100); c.lineTo(152, 94); c.stroke(); c.setLineDash([]);
            c.fillStyle = '#1a0f08'; c.beginPath(); c.ellipse(158, 56, 10, 44, 0.05, 0, Math.PI * 2); c.fill();
            c.restore();
        }
    })).setOrigin(0);
}

const TEXT = {
    cabinet: {
        title: { fontFamily: SERIF, fontStyle: 'bold', fontSize: '19px', color: INK },
        kind: { fontFamily: SERIF, fontStyle: 'italic', fontSize: '13px', color: '#7a6a55' },
        body: { fontFamily: SERIF, fontSize: '14px', color: '#2a2118', lineSpacing: 3 },
        small: { fontFamily: MONO, fontSize: '11px', color: '#6b5b45', letterSpacing: 2 },
        label: { fontFamily: SERIF, fontStyle: 'italic', fontSize: '11px', color: '#3b2b1c' },
        row: { fontFamily: SERIF, fontSize: '15px', color: '#2a1d10' },
        rowSub: { fontFamily: SERIF, fontStyle: 'italic', fontSize: '11px', color: '#6b5b45' }
    },
    desk: {
        title: { ...LOOK.apprentice.text.title, fontSize: '26px' },
        kind: LOOK.apprentice.text.kind,
        body: LOOK.apprentice.text.body,
        small: LOOK.apprentice.text.small,
        label: LOOK.apprentice.text.label,
        row: { fontFamily: SERIF, fontStyle: 'italic', fontSize: '15px', color: '#2a1a0e' },
        rowSub: { fontFamily: SERIF, fontStyle: 'italic', fontSize: '11px', color: '#7a5a3a' }
    }
};

/** an action button on the detail paper (red ink stamp on the card, a red slip on the note); bad = can't afford */
function paperButton(scene, style, cont, x, y, label, act, bad = false) {
    const w = Math.max(130, label.length * 9 + 30);
    if (style === 'cabinet') {
        const b = put(cont, scene.add.rectangle(x, y, w, 30).setStrokeStyle(2, bad ? 0x8a8070 : 0xa8322a).setInteractive({ useHandCursor: true }));
        put(cont, scene.add.text(x, y, label.toUpperCase(), { fontFamily: SERIF, fontStyle: 'bold', fontSize: '14px', color: bad ? '#8a8070' : RED, letterSpacing: 2 }).setOrigin(0.5));
        b.on('pointerover', () => b.setFillStyle(0xa8322a, 0.12));
        b.on('pointerout', () => b.setFillStyle(0xa8322a, 0));
        b.on('pointerdown', () => { playMenuSound(scene, 'clickSound'); act(); });
    } else {
        const b = put(cont, scene.add.rectangle(x, y, w, 32, bad ? 0x6a5a4a : 0x8a1f1a, 0.9).setInteractive({ useHandCursor: true }));
        put(cont, scene.add.text(x, y, label, LOOK.apprentice.text.button).setOrigin(0.5));
        b.on('pointerover', () => b.setFillStyle(bad ? 0x7a6a5a : 0xa8322a, 1));
        b.on('pointerout', () => b.setFillStyle(bad ? 0x6a5a4a : 0x8a1f1a, 0.9));
        b.on('pointerdown', () => { playMenuSound(scene, 'clickSound'); act(); });
    }
}

/**
 * Tabs along the top of the drawer / mat. tabs: [{ label, badge }], on = index; returns their hit boxes.
 * cabinet: paper tabs on the rail; desk: paper bookmarks sticking out of the mat's top edge.
 */
function drawTabs(scene, L, style, x, y, tabs, on, onPick) {
    let tx = x;
    tabs.forEach((t, i) => {
        const sel = i === on;
        const txt = L.add(scene.add.text(0, 0, t.label, style === 'cabinet'
            ? { fontFamily: SERIF, fontSize: '12px', color: '#2a1d10' }
            : { fontFamily: LOOK.apprentice.HAND, fontSize: '16px', color: '#1d140b', padding: { x: 3, y: 2 } }).setOrigin(0.5));
        const w = Math.ceil((txt.width + 24) / 2) * 2, h = style === 'cabinet' ? 20 : 26;
        const cx = tx + w / 2, cy = style === 'cabinet' ? y : y + (sel ? -4 : 0);
        const bg = style === 'desk'                    // a torn scrap (pixel art), the chosen one lighter
            ? scene.add.image(cx, cy, scrapTex(scene, w, h, i, 11 + i, sel ? 1 : 0)).setScale(2).setTint(sel ? 0xffffff : 0xcfc4b0)
            : scene.add.rectangle(cx, cy, w, h, sel ? 0xf1e9d4 : 0x9c8f72).setStrokeStyle(1, 0x5a4a30);
        L.c.addAt(bg, L.c.list.indexOf(txt));
        txt.setPosition(cx, cy);
        if (t.badge) L.add(scene.add.circle(cx + w / 2 - 5, cy - h / 2 + 3, 5, 0xb0302a).setStrokeStyle(1, 0x501010));
        const z = L.add(scene.add.zone(cx, cy, w, h + 6).setInteractive({ useHandCursor: true }));
        z.on('pointerdown', () => { if (i !== on) { playMenuSound(scene, 'clickSound'); onPick(i); } });
        tx += w + 6;
    });
    return tx;
}

/**
 * Hover and click by the pointer's position over hit boxes (hits() = [{ it, x, y, w, h }], centres): hover shows
 * an item while the pointer is over it, a click makes it the choice.
 */
function pointerPicking(scene, st, redraw, hits, { hoverSound = true } = {}) {
    const at = (p) => hits().find(h => Math.abs(p.x - h.x) <= h.w / 2 && Math.abs(p.y - h.y) <= h.h / 2) || null;
    scene.input.on('pointermove', (p) => {
        const h = at(p), it = h ? h.it : null;
        if (it !== st.hover) { st.hover = it; if (it && hoverSound) playMenuSound(scene, 'hoverSound', 0.3); redraw(); }
    });
    scene.input.on('pointerdown', (p) => {
        const h = at(p);
        if (h) { st.sel = h.it; st.hover = h.it; playMenuSound(scene, 'clickSound'); redraw(); }
    });
    scene.input.on('gameout', () => { if (st.hover) { st.hover = null; redraw(); } });
}

// ---------------------------------------------------------------------------------------------------------------
// gridScreen: items with icons

/**
 * spec: {
 *   title, cardHead, empty, hint                (strings, or functions read on every redraw),
 *   tabs?: () => [{ label, badge }], tab?: () => i, setTab?: (i) => void,
 *   items: () => item[],                         the current tab's items, in order
 *   name(it), qty(it), icon(it, x, y, k),        icon: an image / container, k times 60 px
 *   price?(it): string, priceBad?(it): bool      a price tag on each item (shops)
 *   mark?(it): null | 'usable' | 'playing'
 *   detail(it): { name, kind, desc, extra, button: { label, act, bad } | null }
 *   footer(): string,                            money
 *   bag?: true                                   desk: the satchel (a click tips out the next lot)
 *   cloth?: 'leather' | 'baize'
 * }
 */
export function gridScreen(scene, style, spec) {
    const { width: W, height: H } = scene.scale;
    const T = TEXT[style];
    if (style === 'cabinet') panelBackdrop(scene, 'office');
    else scene.add.rectangle(0, 0, W, H, 0x0b0906, 0.86).setOrigin(0);      // (deskMat lays the table over it)
    const st = { page: 0, sel: null, hover: null };
    let pageSize, slot, pageOf;
    const L = layer(scene, 2), tabsL = layer(scene, 2.5), det = layer(scene, 2.2);
    const hits = [];

    // the frame + where the items go
    if (style === 'cabinet') {
        const DX = 44, DY = 62, DW = 660, DH = 470, COLS = 5, ROWS = 3;
        const f = cabinetFrame(scene, 'ppCabinetGrid', DX, DY, DW, DH, { cols: COLS, rows: ROWS, title: spec.title });
        const CW = (f.IW - (COLS - 1) * f.DIV) / COLS, CH = (f.IH - (ROWS - 1) * f.DIV) / ROWS;
        cabinetGlass(scene, 'ppCabinetGlass', f.IX, f.IY, f.IW, f.IH);
        pageSize = COLS * ROWS;
        slot = (k) => ({ x: f.IX + (k % COLS) * (CW + f.DIV) + CW / 2, y: f.IY + Math.floor(k / COLS) * (CH + f.DIV) + CH / 2, w: CW, h: CH, a: 0 });
        st.frame = { DX, DY, DW, DH, f, CW, CH, COLS };
    } else {
        const MAT = { x: 34, y: 30, w: 720, h: 540 };
        deskMat(scene, `ppDesk_${spec.cloth || 'leather'}_${spec.bag ? 1 : 0}`, MAT.x, MAT.y, MAT.w, MAT.h, { cloth: spec.cloth, bag: spec.bag });
        const SLOTS = [];
        for (let row = 0; row < 3; row++) for (let col = 0; col < 5; col++) {
            if (spec.bag && row === 0 && col < 2) continue;
            SLOTS.push({ x: MAT.x + 90 + col * 134, y: MAT.y + 112 + row * 160 });
        }
        pageSize = SLOTS.length;
        slot = (k, it) => {
            const r = rng(hash((it && (it.id || spec.name(it))) || k));
            return { x: SLOTS[k].x + (r() - 0.5) * 40, y: SLOTS[k].y + (r() - 0.5) * 30, w: 120, h: 120, a: (r() - 0.5) * 0.36 };
        };
        st.frame = { MAT };
        if (spec.title) scene.add.text(MAT.x + MAT.w - 34, MAT.y + MAT.h - 30, spec.title, { fontFamily: LOOK.apprentice.HAND, fontSize: '18px', color: 'rgba(240,215,180,0.7)', padding: { x: 3, y: 2 } }).setOrigin(1, 0.5).setDepth(1);
    }
    pageOf = () => spec.items().slice(st.page * pageSize, (st.page + 1) * pageSize);
    const pages = () => Math.max(1, Math.ceil(spec.items().length / pageSize));
    const fix = () => {
        const all = spec.items();
        if (st.sel && !all.includes(st.sel)) st.sel = null;
        if (st.hover && !all.includes(st.hover)) st.hover = null;
        st.page = Phaser.Math.Clamp(st.page, 0, pages() - 1);
        if (!st.sel && all.length) st.sel = pageOf()[0] || all[0];
    };
    const shown = () => st.hover || st.sel;
    const turnPage = (p) => { st.page = p; st.sel = pageOf()[0] || null; st.hover = null; playMenuSound(scene, 'clickSound'); redraw(); };

    // the detail paper (ui/panelStyle.js: the same card / note, in the same place, as the other panels)
    const SET = style === 'cabinet' ? 'office' : 'apprentice';
    const P = LOOK[SET].DETAIL;
    const paper = detailCard(scene, SET, P);
    let footerText = null;

    const drawDetail = () => {
        det.clear();
        paper.body.removeAll(true);
        const b = paper.body, PW = P.w, PH = P.h, it = shown();
        footerText = put(b, scene.add.text(18, PH - 22, spec.footer?.() || '', T.small).setOrigin(0, 0.5));
        if (style === 'cabinet') put(b, scene.add.text(58, 16, val(spec.cardHead) || '', T.small));     // right of the paper clip
        if (!it) { put(b, scene.add.text(PW / 2, PH / 2 - 40, spec.items().length ? val(spec.hint) : val(spec.empty), { ...T.kind, fontSize: '15px', align: 'center', wordWrap: { width: PW - 50 } }).setOrigin(0.5)); return; }
        const d = spec.detail(it);
        let y;
        if (style === 'cabinet') {
            put(b, scene.add.rectangle(PW / 2, 108, 136, 136).setStrokeStyle(1, 0x5a4a3a, 0.5));
            put(b, spec.icon(it, PW / 2, 108, 2));
            if (spec.qty(it) > 1) put(b, scene.add.text(PW / 2 + 62, 168, `×${spec.qty(it)}`, { ...T.small, color: INK }).setOrigin(1, 1));
            const nm = put(b, scene.add.text(PW / 2, 188, d.name, { ...T.title, align: 'center', wordWrap: { width: PW - 40 } }).setOrigin(0.5, 0));
            fitHeight(nm, 50, 14);
            y = nm.y + nm.height + 2;
            if (d.kind) { const k = put(b, scene.add.text(PW / 2, y, d.kind, T.kind).setOrigin(0.5, 0)); y += k.height + 6; }
        } else {
            const nm = put(b, scene.add.text(18, 24, d.name, { ...T.title, wordWrap: { width: PW - 36 }, lineSpacing: -6 }));
            fitHeight(nm, 64, 18);
            y = nm.y + nm.height;
            put(b, scene.add.graphics().lineStyle(1.5, 0x8a3a2a, 0.7).lineBetween(18, y + 4, PW - 30, y + 2));
            if (d.kind) { const k = put(b, scene.add.text(18, y + 8, d.kind, T.kind)); y += k.height + 8; }
            y += 4;
        }
        const bottom = PH - (d.button ? 76 : 40) - (d.extra ? 24 : 0);
        const desc = put(b, scene.add.text(18, y + 4, d.desc || '', { ...T.body, wordWrap: { width: PW - 36 } }));
        fitHeight(desc, bottom - (y + 4), 10);
        if (d.extra) put(b, scene.add.text(PW / 2, bottom + 10, d.extra, { ...T.title, fontSize: '15px', color: d.extraBad ? RED : INK }).setOrigin(0.5, 0.5));
        if (d.button) paperButton(scene, style, b, PW / 2, PH - 56, d.button.label, d.button.act, d.button.bad);
    };

    const redraw = () => {
        fix();
        L.clear(); tabsL.clear();
        hits.length = 0;
        const page = pageOf();
        if (!page.length) {
            const c = style === 'cabinet' ? { x: st.frame.f.IX + st.frame.f.IW / 2, y: st.frame.f.IY + st.frame.f.IH / 2 } : { x: st.frame.MAT.x + 400, y: st.frame.MAT.y + 270 };
            L.add(scene.add.text(c.x, c.y, val(spec.empty), { fontFamily: SERIF, fontStyle: 'italic', fontSize: '18px', color: style === 'cabinet' ? '#b9c4b0' : '#e7cdb0' }).setOrigin(0.5));
        }
        const onTop = [];                                 // the hover tag: over every item, not only the earlier ones
        page.forEach((it, k) => {
            const s = slot(k, it), up = it === shown();
            if (style === 'cabinet') {
                const { CW, CH } = st.frame;
                L.add(shadowOf(spec.icon(it, s.x + 3, s.y - 10 + 4, 1), up ? 0.55 : 0.4));
                L.add(spec.icon(it, s.x, s.y - 10 - (up ? 4 : 0), 1));
                const lab = Math.round(CW) === 116 && grime(scene, `label_office_${k % 3}`);     // a stained paper strip, pinned
                L.add(lab ? scene.add.image(s.x, s.y + 46, lab).setScale(2) : scene.add.rectangle(s.x, s.y + 46, CW - 16, 18, 0xe9dfc4).setStrokeStyle(1, 0x8a7655));
                L.add(ellipsize(scene.add.text(s.x, s.y + 46, spec.name(it), T.label).setOrigin(0.5), CW - 22));
                if (spec.price) {
                    const pt = L.add(scene.add.text(s.x + CW / 2 - 8, s.y - CH / 2 + 7, spec.price(it), { fontFamily: MONO, fontSize: '11px', color: spec.priceBad?.(it) ? '#ffb0a0' : '#2a1d08' }).setOrigin(1, 0).setDepth(1));
                    L.c.addAt(scene.add.rectangle(pt.x + 4, pt.y - 2, pt.width + 10, pt.height + 4, spec.priceBad?.(it) ? 0x8a2a22 : 0xc9a23a).setOrigin(1, 0), L.c.list.indexOf(pt));
                } else if (spec.qty(it) > 1) L.add(scene.add.text(s.x + CW / 2 - 6, s.y - CH / 2 + 4, `×${spec.qty(it)}`, { fontFamily: MONO, fontSize: '11px', color: '#e9dfc4' }).setOrigin(1, 0));
                const m = spec.mark?.(it);
                if (m) L.add(scene.add.circle(s.x - CW / 2 + 10, s.y - CH / 2 + 10, 4, m === 'playing' ? 0xfff2b0 : 0xc9a23a).setStrokeStyle(1, 0x4a3410));
                if (it === st.sel) L.add(markChosen(scene, 'office', s.x, s.y, CW - 6, CH - 6));
            } else {
                L.add(shadowOf(spec.icon(it, s.x + (up ? 9 : 5), s.y + (up ? 12 : 7), 2), up ? 0.35 : 0.55)).setRotation(s.a);
                L.add(spec.icon(it, s.x, s.y - (up ? 6 : 0), 2)).setRotation(s.a);
                if (it === st.sel) L.add(markChosen(scene, 'apprentice', s.x, s.y + 2, 140, 124)).setRotation(s.a * 0.5);
                if (spec.price) {                         // a little price tag tied on
                    const bad = spec.priceBad?.(it);
                    const pt = scene.add.text(s.x + 36, s.y + 42, spec.price(it), { fontFamily: SERIF, fontStyle: 'bold italic', fontSize: '13px', color: bad ? '#ffd0c0' : '#2a1d10' }).setOrigin(0.5).setRotation(0.1);
                    L.add(scene.add.rectangle(pt.x, pt.y, pt.width + 14, 20, bad ? 0x8a2a22 : 0xe8d8b4).setStrokeStyle(1, 0x7a6040).setRotation(0.1));
                    L.add(pt);
                } else if (spec.qty(it) > 1) L.add(scene.add.text(s.x + 52, s.y + 44, `×${spec.qty(it)}`, { fontFamily: SERIF, fontStyle: 'bold', fontSize: '15px', color: '#f3e2c4', stroke: '#2a120c', strokeThickness: 3 }).setOrigin(1, 1));
                if (it === st.hover) {                    // the luggage tag on hover
                    const tg = scene.add.container(s.x + 62, s.y - 52).setRotation(-0.12);
                    const nm = scene.add.text(14, 0, spec.name(it), { ...T.label }).setOrigin(0, 0.5);
                    const tw = nm.width + 26, pts = [{ x: 0, y: 0 }, { x: 10, y: -12 }, { x: tw, y: -12 }, { x: tw, y: 12 }, { x: 10, y: 12 }];
                    tg.add(scene.add.graphics().fillStyle(0xe8d8b4).fillPoints(pts, true).lineStyle(1, 0x7a6040).strokePoints(pts, true));
                    tg.add(scene.add.circle(8, 0, 2.5, 0x3a2a1a));
                    tg.add(nm);
                    onTop.push(scene.add.graphics().lineStyle(1, 0xd8c8a0, 0.9).lineBetween(s.x + 30, s.y - 26, s.x + 70, s.y - 52), tg);
                }
            }
            L.add(scene.add.zone(s.x, s.y, s.w, s.h).setInteractive({ useHandCursor: true }));     // the hand cursor only
            hits.push({ it, x: s.x, y: s.y, w: s.w, h: s.h });
        });
        onTop.forEach(o => L.add(o));

        // tabs and pages
        const tabs = spec.tabs?.() || [];
        if (style === 'cabinet') {
            const { DX, DY, DW } = st.frame;
            if (tabs.length) drawTabs(scene, tabsL, style, DX + 16, DY - 10, tabs, spec.tab(), (i) => { spec.setTab(i); st.page = 0; st.sel = null; st.hover = null; redraw(); });
            for (let p = 0; pages() > 1 && p < pages(); p++) {
                const tx = DX + DW - 30 - (pages() - 1 - p) * 44, on = p === st.page;
                tabsL.add(scene.add.rectangle(tx, DY - 9, 38, 18, on ? 0xe9dfc4 : 0x9c8f72).setStrokeStyle(1, 0x5a4a30));
                tabsL.add(scene.add.text(tx, DY - 9, ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'][p] || `${p + 1}`, { fontFamily: SERIF, fontSize: '12px', color: '#2a1d10' }).setOrigin(0.5));
                tabsL.add(scene.add.zone(tx, DY - 9, 38, 20).setInteractive({ useHandCursor: true })).on('pointerdown', () => turnPage(p));
            }
        } else {
            const { MAT } = st.frame;
            if (tabs.length) drawTabs(scene, tabsL, style, MAT.x + 30, MAT.y - 2, tabs, spec.tab(), (i) => { spec.setTab(i); st.page = 0; st.sel = null; st.hover = null; redraw(); });
            if (pages() > 1) {
                if (spec.bag) {
                    tabsL.add(scene.add.zone(MAT.x + 116, MAT.y + 80, 170, 120).setInteractive({ useHandCursor: true })).on('pointerdown', () => turnPage((st.page + 1) % pages()));
                    tabsL.add(scene.add.text(MAT.x + 116, MAT.y + 156, `${spec.bagMore || 'další'} · ${st.page + 1}/${pages()}`, { ...T.small, color: '#f0d9b5' }).setOrigin(0.5).setRotation(-0.1));
                } else {
                    const t = tabsL.add(scene.add.text(MAT.x + MAT.w - 40, MAT.y + 30, `${st.page + 1}/${pages()}  ›`, { ...T.small, fontSize: '15px', color: '#f0d9b5' }).setOrigin(1, 0.5));
                    t.setInteractive({ useHandCursor: true }).on('pointerdown', () => turnPage((st.page + 1) % pages()));
                }
            }
        }
        drawDetail();
    };
    pointerPicking(scene, st, redraw, () => hits);
    scene.input.on('wheel', (p, o, dx, dy) => {
        const pg = Phaser.Math.Clamp(st.page + Math.sign(dy), 0, pages() - 1);
        if (pg !== st.page) turnPage(pg);
    });
    redraw();

    const cols = style === 'cabinet' ? 5 : 5;
    return {
        refresh: redraw,
        shown,
        reset() { st.page = 0; st.sel = null; st.hover = null; redraw(); },
        footer() { if (footerText?.active) footerText.setText(spec.footer?.() || ''); },
        key(code, ev) {
            const page = pageOf();
            const i = page.indexOf(st.sel);
            const tabs = spec.tabs?.() || [];
            const move = { ArrowRight: 1, KeyD: 1, ArrowLeft: -1, KeyA: -1, ArrowDown: cols, KeyS: cols, ArrowUp: -cols, KeyW: -cols }[code];
            if (code === 'Tab' && tabs.length > 1) {
                ev?.preventDefault?.();
                spec.setTab((spec.tab() + 1) % tabs.length); st.page = 0; st.sel = null; st.hover = null;
                playMenuSound(scene, 'clickSound'); redraw();
            } else if (move !== undefined && page.length) {
                st.hover = null;
                st.sel = page[Phaser.Math.Clamp(i < 0 ? 0 : i + move, 0, page.length - 1)];
                playMenuSound(scene, 'hoverSound', 0.35); redraw();
            } else if (code === 'PageDown' || code === 'PageUp') {
                const p = Phaser.Math.Clamp(st.page + (code === 'PageDown' ? 1 : -1), 0, pages() - 1);
                if (p !== st.page) turnPage(p);
            } else if (code === 'Enter' || code === 'NumpadEnter' || code === 'Space') {
                const it = st.sel;
                if (it) spec.detail(it).button?.act();
            }
        }
    };
}

// ---------------------------------------------------------------------------------------------------------------
// the overlay scene and who has it

let current = null;                                   // { owner } of the open screen

/** the running overlay, or null */
export function paperScene(game) {
    const s = game.scene.getScene('PaperScreenScene');
    return s && s.sys.isActive() && s.sys.settings.status === Phaser.Scenes.RUNNING ? s : null;
}

/**
 * Open owner's screen (closing whichever other one is open: that owner hears paperClosed()).
 * owner: { scene (the game scene), buildScreen(overlayScene, style) → screen, close(), paperClosed() }
 */
export function openPaperScreen(owner) {
    const game = owner.scene.game, mgr = game.scene;
    if (current && current !== owner) { const prev = current; current = null; prev.paperClosed?.(); }
    current = owner;
    if (!mgr.getScene('PaperScreenScene')) mgr.add('PaperScreenScene', PaperScreenScene, false);
    const overlay = mgr.getScene('PaperScreenScene');
    if (overlay.sys.isActive()) overlay.scene.restart({ owner });
    else owner.scene.scene.launch('PaperScreenScene', { owner });
    owner.scene.scene.bringToTop('PaperScreenScene');
    if (!owner._paperShutdownHooked) {
        owner._paperShutdownHooked = true;
        owner.scene.events.once('shutdown', () => { owner._paperShutdownHooked = false; closePaperScreen(owner); });
    }
}

export function closePaperScreen(owner) {
    if (current !== owner) return;
    current = null;
    owner.scene.scene.stop('PaperScreenScene');
}

export function isPaperScreenOpen(owner) { return current === owner; }
export function anyPaperScreenOpen() { return !!current; }

/** an item's icon at k times its 60 px: its texture (key), or a lettered disc (key null) */
export function itemIcon(scene, key, item, name, x, y, k = 1) {
    if (key) {
        const img = scene.add.image(x, y, key).setScale(k * 60 / Math.max(1, scene.textures.get(key).getSourceImage().width));
        if (item.tint) img.setTint(item.tint);
        return img;
    }
    const c = scene.add.container(x, y);
    c.add(scene.add.circle(0, 0, 22 * k, 0x2a2018).setStrokeStyle(2, 0xb08d4a));
    c.add(scene.add.text(0, 0, (name || '?').charAt(0), { fontFamily: SERIF, fontSize: `${20 * k}px`, color: '#e8d9b0' }).setOrigin(0.5));
    return c;
}

/** redraw owner's screen if it is the open one */
export function refreshPaperScreen(owner, what = 'refresh') {
    if (current !== owner) return;
    const s = owner.scene.game.scene.getScene('PaperScreenScene');
    s?.screen?.[what]?.();
}

/** ESC: close whatever screen is open; true if there was one */
export function closeAnyPaperScreen() {
    if (!current) return false;
    current.close();
    return true;
}

export class PaperScreenScene extends Phaser.Scene {
    constructor() { super({ key: 'PaperScreenScene' }); }

    /** a game notice while a panel is open (GameScene.showNotification sends it here: the game scene is under us) */
    notify(message, color = '#ffffff') {
        const { width: W } = this.scale;
        this.notices = (this.notices || []).filter(n => n.active);
        const y = 22 + this.notices.length * 30;
        const t = this.add.text(W / 2, y, message, { fontFamily: SERIF, fontSize: '15px', color, padding: { x: 12, y: 5 }, backgroundColor: 'rgba(12,10,8,0.92)' })
            .setOrigin(0.5).setDepth(30);
        this.notices.push(t);
        this.tweens.add({ targets: t, alpha: 0, delay: 1800, duration: 500, onComplete: () => t.destroy() });
    }

    create({ owner }) {
        this.owner = owner;
        this.notices = [];
        this.cameras.main.setRoundPixels(false);
        const { width: W, height: H } = this.scale;
        // a dark backing that overhangs the edges (a rect from x = 0 leaves the first pixel column uncovered), and
        // nothing under it gets clicks
        this.add.rectangle(-8, -8, W + 16, H + 16, 0x0b0906, 1).setOrigin(0).setDepth(-10).setInteractive();
        this.screen = owner.buildScreen(this, paperStyle());
        const x = this.add.text(W - 14, 8, '×', { fontFamily: SERIF, fontSize: '30px', color: '#d8d8d8' }).setOrigin(1, 0).setDepth(10)
            .setInteractive({ useHandCursor: true });
        x.on('pointerover', () => x.setColor('#ffffff'));
        x.on('pointerout', () => x.setColor('#d8d8d8'));
        x.on('pointerdown', () => { playMenuSound(this, 'clickSound'); owner.close(); });
        this.input.keyboard.on('keydown', (e) => {
            if (['Escape', 'KeyI', 'KeyJ', 'KeyQ', 'KeyM'].includes(e.code)) return;    // the game scene's own keys
            this.screen.key?.(e.code, e);
        });
    }
}
