/**
 * questScreens.js — the quest log in the two panel sets (ui/panelStyle.js; Settings: "Vzhled panelů: Učedník / Úřad").
 * QuestLog opens QUEST_SCREENS[panelSet()](scene, ctx) in the paper overlay scene.
 *
 *   apprentice  Nástěnka: a corkboard, the errands pinned on coloured slips in his handwriting; the chosen one is ringed
 *               in red pencil and a red thread runs from its pin to the note on the right with the whole errand; the
 *               steps done since are in green ink, the latest highlighted; a finished errand gets a SPLNĚNO stamp
 *   office      Úřední záznamy: numbered forms in a filing tray, each stamped VYŘIZUJE SE / SCHVÁLENO; the chosen one
 *               is bracketed in red ink; the record on the index card on the right (typed heads, the stamp, the steps
 *               added in blue biro)
 *
 * The detail sits on LOOK[set].DETAIL (detailCard), the tabs are drawTabs, the choice is markChosen, as in the other
 * panels. A quest the demo can't finish shows ctx.strings.demoNote and the traffic cone.
 *
 * ctx (ui/QuestLog.js screenCtx):
 *   scene, W, H, lang, t(key, params, fallback), title ('Úkoly')
 *   tabs: [{ key: 'active', label }, { key: 'finished', label }], tab() → key, setTab(key)  (then redraw yourself)
 *   quests() → the open tab's quests: [{ key, title, description, updates: [text, oldest first], done, demo }]
 *   all() → every quest, same shape
 *   empty() → the text for an empty tab, strings: { progress, demoNote, done, active }
 *   sound(key, vol), close()
 * screen: { refresh(), key(code, event) }  refresh() is called when a quest changes while it's open
 *
 * Both run on one engine (questScreen): the open tab's quests (one or more columns, they scroll), the chosen quest's
 * full text on the card (it scrolls too). Hover only lights a quest, a click chooses it; both come from the pointer's
 * position against hit boxes (rows re-made on every redraw would lose their pointerout). Keys: ↑ / ↓ the choice,
 * ← / → or Tab the tabs, PgUp / PgDn the text; the wheel scrolls whatever it's over.
 */
import { tex, rng, hash, put } from '../paperKit.js';
import { LOOK, detailCard, markChosen, drawTabs, dragRails } from '../panelStyle.js';

const MONO = 'Departure Mono', BEBAS = 'Bebas Neue';

// ---------------------------------------------------------------------------------------------------------------
// shared

function speckle(c, x0, y0, w, h, n, col, seed, a0 = 0.03, a1 = 0.1, s0 = 1, s1 = 2.5) {
    const r = rng(seed);
    for (let i = 0; i < n; i++) {
        c.fillStyle = `rgba(${col},${a0 + r() * (a1 - a0)})`;
        const s = s0 + r() * (s1 - s0);
        c.fillRect(x0 + r() * w, y0 + r() * h, s, s);
    }
}

/** cut a one-line text to maxW with an ellipsis */
function ell(t, maxW) {
    let s = t.text;
    while (t.width > maxW && s.length > 2) { s = s.slice(0, -1); t.setText(s.trimEnd() + '…'); }
    return t;
}

/** the traffic cone (the demo's closed way), standing at x, y (its foot), h px tall */
function cone(scene, c, x, y, h = 24) {
    if (!scene.textures.exists('trafficConeFar')) return null;
    const img = scene.add.image(x, y, 'trafficConeFar').setOrigin(0.5, 1);
    img.setScale(h / Math.max(1, img.height));
    c.add(img);
    return img;
}

/** a worn rubber stamp: word in a double frame, ink missing in specks */
function stampTex(scene, word, color, w, h, seed = 7) {
    return tex(scene, `qs_stamp_${hash(word + color + w + 'x' + h)}`, w, h, (c) => {
        c.strokeStyle = color; c.fillStyle = color;
        c.lineWidth = 4; c.beginPath(); c.roundRect(4, 4, w - 8, h - 8, 8); c.stroke();
        c.lineWidth = 1.5; c.beginPath(); c.roundRect(10, 10, w - 20, h - 20, 5); c.stroke();
        c.textAlign = 'center'; c.textBaseline = 'middle';
        let fs = Math.floor(h * 0.5);
        do { c.font = `${fs}px "${BEBAS}", Georgia`; fs -= 1; } while (c.measureText(word).width > w - 32 && fs > 8);
        c.fillText(word, w / 2, h / 2 + 2);
        c.globalCompositeOperation = 'destination-out';
        const r = rng(seed);
        for (let i = 0; i < w * h / 18; i++) { c.fillStyle = `rgba(0,0,0,${0.3 + r() * 0.7})`; c.beginPath(); c.arc(r() * w, r() * h, r() * 1.6, 0, 7); c.fill(); }
        for (let i = 0; i < 8; i++) { c.fillStyle = 'rgba(0,0,0,0.5)'; c.fillRect(r() * w, r() * h, 14 + r() * 40, 1 + r() * 2); }
    });
}

const words = (ctx) => (cs, en) => (ctx.lang === 'cs' ? cs : en);
const progressLabel = (ctx) => (ctx.strings.progress || '').replace(/[:：]\s*$/, '');
const latest = (q) => (q.updates.length ? q.updates[q.updates.length - 1] : q.description || '');
const number = (ctx, q) => String(ctx.all().findIndex(a => a.key === q.key) + 1).padStart(4, '0');

/**
 * The engine both screens run on.
 * cfg: {
 *   bg(),                                   the static backdrop (opaque, full screen)
 *   list: { x, y, w, h, rowH, cols, gapX }, where the quests go (top-left boxes; it scrolls by rows)
 *   card,                                   the detail paper (panelStyle.detailCard)
 *   text: { x, y, w, h },                   the scrolling text's window on the card (card-local)
 *   tabs(layer, switchTab),                 draws the tabs (panelStyle.drawTabs; they take their own clicks)
 *   row(c, q, box, { on, hov, k }),         draws one quest in its box
 *   head?(c, q),                            fixed bits on the card (not scrolling), in card.body
 *   detailOf(c, q, w) → height,             draws the chosen quest's text from (0, 0)
 *   empty(c, text),                         the empty tab
 *   over?(c, chosenBox, q),                 drawn above everything (the thread)
 *   rail: colour of the scroll bars
 * }
 */
function questScreen(scene, ctx, cfg) {
    const st = { sel: null, hover: null, scroll: 0, dscroll: 0, follow: true };
    const LA = cfg.list, card = cfg.card, TA = cfg.text;
    const DA = { x: card.x + TA.x, y: card.y + TA.y, w: TA.w, h: TA.h };              // the text window on screen
    const cols = LA.cols || 1, gapX = LA.gapX || 0, colW = (LA.w - (cols - 1) * gapX) / cols;
    const visRows = Math.max(1, Math.floor(LA.h / LA.rowH));
    const listL = scene.add.container(0, 0).setDepth(2);
    const tabsL = scene.add.container(0, 0).setDepth(3);
    const overL = scene.add.container(0, 0).setDepth(4);
    const headL = scene.add.container(0, 0);
    card.body.add(headL);
    const rails = scene.add.graphics().setDepth(5);
    const mask = (x, y, w, h) => scene.make.graphics({ add: false }).fillRect(x, y, w, h).createGeometryMask();
    const pad = LA.maskPad ?? 12;
    listL.setMask(mask(LA.x - pad, LA.y, LA.w + 2 * pad, LA.h));
    const textMask = mask(DA.x - 10, DA.y, DA.w + 20, DA.h);
    let hits = [], inner = null, dHeight = 0, chosenBox = null;

    const fix = () => {
        const qs = ctx.quests();
        if (st.sel && !qs.some(q => q.key === st.sel)) st.sel = null;
        if (st.hover && !qs.some(q => q.key === st.hover)) st.hover = null;
        if (!st.sel && qs.length) { st.sel = qs[0].key; st.dscroll = 0; st.follow = true; }
        const nRows = Math.ceil(qs.length / cols);
        const i = qs.findIndex(q => q.key === st.sel);
        if (i >= 0 && st.follow) { const r = Math.floor(i / cols); st.scroll = Phaser.Math.Clamp(st.scroll, r - visRows + 1, r); }
        st.follow = false;
        st.scroll = Phaser.Math.Clamp(st.scroll, 0, Math.max(0, nRows - visRows));
        return qs;
    };
    const boxOf = (k) => {
        const c = k % cols, r = Math.floor(k / cols);
        return { x: LA.x + c * (colW + gapX), y: LA.y + (r - st.scroll) * LA.rowH, w: colW, h: LA.rowH };
    };
    let railsNow = [];                                 // the rails as drawn (dragRails reads them)
    const drawRails = (qs) => {
        rails.clear();
        railsNow = [];
        const col = cfg.rail ?? 0xffffff, nRows = Math.ceil(qs.length / cols);
        if (nRows > visRows) {
            const bh = Math.max(24, LA.h * visRows / nRows), x = LA.x + LA.w + (LA.railGap ?? 8), frac = st.scroll / (nRows - visRows);
            rails.fillStyle(col, 0.75).fillRect(x, LA.y + (LA.h - bh) * frac, 4, bh);
            railsNow.push({ x, y: LA.y, h: LA.h, thumb: bh, frac, set: (f) => { const v = Math.round(f * (nRows - visRows)); if (v !== st.scroll) { st.scroll = v; redraw(); } } });
        }
        const md = dHeight - DA.h;
        if (md > 0) {
            const bh = Math.max(24, DA.h * DA.h / dHeight), x = card.x + card.w + 8, frac = st.dscroll / md;
            rails.fillStyle(col, 0.75).fillRect(x, DA.y + (DA.h - bh) * frac, 4, bh);
            railsNow.push({ x, y: DA.y, h: DA.h, thumb: bh, frac, set: (f) => scrollD(f * md - st.dscroll) });
        }
    };
    const switchTab = (key) => {
        if (key === ctx.tab()) return;
        ctx.setTab(key); st.sel = null; st.hover = null; st.scroll = 0; st.dscroll = 0; st.follow = true;
        ctx.sound('clickSound'); redraw();
    };
    const redraw = () => {
        const qs = fix();
        listL.removeAll(true); tabsL.removeAll(true); overL.removeAll(true); headL.removeAll(true);
        inner?.destroy();
        hits = []; chosenBox = null;
        cfg.tabs(tabsL, switchTab);
        if (!qs.length) cfg.empty(listL, ctx.empty());
        qs.forEach((q, k) => {
            const b = boxOf(k);
            if (b.y + b.h < LA.y - LA.rowH || b.y > LA.y + LA.h + LA.rowH) return;
            cfg.row(listL, q, b, { on: q.key === st.sel, hov: q.key === st.hover, k });
            const top = Math.max(b.y, LA.y), bot = Math.min(b.y + b.h, LA.y + LA.h);
            if (bot - top > 6) hits.push({ key: q.key, x: b.x, y: top, w: b.w, h: bot - top });
            if (q.key === st.sel && b.y + b.h > LA.y && b.y < LA.y + LA.h) chosenBox = b;
        });
        const q = qs.find(x => x.key === st.sel);
        if (q && cfg.head) cfg.head(headL, q);
        inner = scene.add.container(TA.x, TA.y);
        card.body.add(inner);
        inner.setMask(textMask);
        dHeight = q ? cfg.detailOf(inner, q, TA.w) : 0;
        st.dscroll = Phaser.Math.Clamp(st.dscroll, 0, Math.max(0, dHeight - DA.h));
        inner.y = TA.y - st.dscroll;
        if (cfg.over && q) cfg.over(overL, chosenBox, q);
        drawRails(qs);
    };
    const scrollD = (d) => {
        st.dscroll = Phaser.Math.Clamp(st.dscroll + d, 0, Math.max(0, dHeight - DA.h));
        if (inner) inner.y = TA.y - st.dscroll;
        drawRails(ctx.quests());
    };

    const inBox = (p, b) => p.x >= b.x && p.x <= b.x + b.w && p.y >= b.y && p.y <= b.y + b.h;
    let cursorOn = null;
    const cursor = (on) => { if (on !== cursorOn) { cursorOn = on; scene.input.setDefaultCursor(on ? 'pointer' : 'default'); } };
    scene.events.once('shutdown', () => scene.input.setDefaultCursor('default'));
    scene.input.on('pointermove', (p) => {
        const h = hits.find(b => inBox(p, b)), key = h ? h.key : null;
        // over a tab (an interactive zone with its own hand cursor) leave the cursor to it
        if (scene.input.hitTestPointer(p).some(o => o.input?.cursor)) cursorOn = null; else cursor(!!h);
        if (key !== st.hover) { st.hover = key; if (key) ctx.sound('hoverSound', 0.25); redraw(); }
    });
    scene.input.on('pointerdown', (p) => {
        const h = hits.find(b => inBox(p, b));
        if (h && h.key !== st.sel) { st.sel = h.key; st.dscroll = 0; ctx.sound('clickSound'); redraw(); }
    });
    scene.input.on('gameout', () => { cursor(false); if (st.hover) { st.hover = null; redraw(); } });
    dragRails(scene, () => railsNow);                  // the rails can be dragged as well as wheeled
    scene.input.on('wheel', (p, o, dx, dy) => {
        if (inBox(p, { x: card.x, y: card.y, w: card.w + 20, h: card.h })) scrollD(Math.sign(dy) * 40);
        else if (inBox(p, { x: LA.x - 10, y: LA.y, w: LA.w + 30, h: LA.h })) { st.scroll += Math.sign(dy); redraw(); }
    });
    redraw();

    return {
        refresh: redraw,
        key(code, ev) {
            const qs = ctx.quests(), i = qs.findIndex(q => q.key === st.sel);
            if (code === 'ArrowDown' || code === 'KeyS' || code === 'ArrowUp' || code === 'KeyW') {
                if (!qs.length) return;
                const d = code === 'ArrowDown' || code === 'KeyS' ? 1 : -1;
                st.sel = qs[Phaser.Math.Clamp(i < 0 ? 0 : i + d, 0, qs.length - 1)].key;
                st.dscroll = 0; st.follow = true; st.hover = null;
                ctx.sound('hoverSound', 0.3); redraw();
            } else if (code === 'ArrowLeft' || code === 'KeyA' || code === 'ArrowRight' || code === 'KeyD' || code === 'Tab') {
                ev?.preventDefault?.();
                const keys = ctx.tabs.map(t => t.key), j = keys.indexOf(ctx.tab());
                const d = code === 'ArrowLeft' || code === 'KeyA' ? -1 : 1;
                switchTab(keys[(j + d + keys.length) % keys.length]);
            } else if (code === 'PageDown' || code === 'PageUp') {
                scrollD((code === 'PageDown' ? 1 : -1) * (DA.h - 60));
            }
        }
    };
}

/** the panel set's tabs (Active / Completed) at x, y */
const tabsOf = (scene, set, ctx, x, y) => (layer, switchTab) => drawTabs(scene, set, layer, x, y,
    ctx.tabs.map(t => ({ label: t.label })), ctx.tabs.findIndex(t => t.key === ctx.tab()), (i) => switchTab(ctx.tabs[i].key));

// ---------------------------------------------------------------------------------------------------------------
// the apprentice: Nástěnka, a corkboard of errand slips

function buildBoard(scene, ctx) {
    const { W, H } = ctx, w = words(ctx), A = LOOK.apprentice, T = A.text;
    const SLIPS = ['#f3e9c8', '#f2cdc2', '#f3e39a', '#d3e8c9', '#cfe0ef', '#e7d6ee'];
    const PINS = [0xc0392b, 0x2e6fb0, 0x2f8a4a, 0xd4a017, 0x8e44ad];
    const pinAt = (c, x, y, col) => {
        put(c, scene.add.circle(x + 1.5, y + 2.5, 6, 0x000000, 0.35));
        put(c, scene.add.circle(x, y, 6, col).setStrokeStyle(1, 0x000000, 0.4));
        put(c, scene.add.circle(x - 2, y - 2, 2, 0xffffff, 0.7));
    };
    scene.add.image(0, 0, tex(scene, 'qs_board2', W, H, (c) => {
        c.fillStyle = '#3e2614'; c.fillRect(0, 0, W, H);                              // the frame
        const g = c.createLinearGradient(0, 0, W, H);
        g.addColorStop(0, '#b27c46'); g.addColorStop(1, '#94602f');
        c.fillStyle = g; c.fillRect(14, 14, W - 28, H - 28);                          // the cork
        speckle(c, 14, 14, W - 28, H - 28, 26000, '60,35,15', 11, 0.12, 0.35, 0.8, 2.2);
        speckle(c, 14, 14, W - 28, H - 28, 12000, '235,190,130', 12, 0.08, 0.25, 0.8, 1.8);
        speckle(c, 14, 14, W - 28, H - 28, 900, '40,22,8', 13, 0.2, 0.4, 2, 4);
        c.strokeStyle = 'rgba(255,220,170,0.25)'; c.lineWidth = 2; c.strokeRect(13, 13, W - 26, H - 26);
        c.fillStyle = 'rgba(0,0,0,0.35)'; c.fillRect(14, 14, W - 28, 6); c.fillRect(14, 14, 6, H - 28);
    })).setOrigin(0).setDepth(0);
    scene.add.text(W / 2, H - 7, ctx.title.toUpperCase(), { fontFamily: 'Georgia', fontSize: '10px', color: '#d9b58a', letterSpacing: 6 }).setOrigin(0.5).setDepth(1);
    const card = detailCard(scene, 'apprentice');
    const rotN = -0.015, py0 = -card.h / 2 + 10;
    const notePin = { x: card.x + card.w / 2 - py0 * Math.sin(rotN), y: card.y + card.h / 2 + py0 * Math.cos(rotN) };
    let pinPos = null;
    return questScreen(scene, ctx, {
        list: { x: 40, y: 74, w: 716, h: 490, rowH: 122, cols: 3, gapX: 12, maskPad: 16, railGap: 6 },
        card,
        text: { x: 20, y: 28, w: card.w - 38, h: card.h - 50 },
        rail: 0xf6f0dc,
        tabs: tabsOf(scene, 'apprentice', ctx, 44, 34),
        row: (c, q, b, { on, hov }) => {
            const r = rng(hash(q.key));
            const color = SLIPS[Math.floor(r() * SLIPS.length)], pin = PINS[Math.floor(r() * PINS.length)];
            const rot = (r() - 0.5) * 0.07, sw = b.w - 14, sh = b.h - 18;
            const lift = on ? 4 : hov ? 2 : 0;
            const slip = scene.add.container(b.x + b.w / 2, b.y + b.h / 2 - lift).setRotation(rot);
            slip.add(scene.add.rectangle(3 + lift, 5 + lift, sw, sh, 0x000000, on ? 0.45 : 0.3));
            slip.add(scene.add.rectangle(0, 0, sw, sh, Phaser.Display.Color.HexStringToColor(color).color).setStrokeStyle(1, 0x000000, 0.15));
            const title = scene.add.text(-sw / 2 + 12, -sh / 2 + 16, q.title, {
                ...T.hand, fontStyle: 'bold', fontSize: '20px', color: q.done ? '#7a6a55' : A.INK, wordWrap: { width: sw - 24 }, maxLines: 2
            });
            slip.add(title);
            slip.add(scene.add.text(-sw / 2 + 12, title.y + title.height + 1, latest(q), {
                ...T.later, fontSize: '16px', wordWrap: { width: sw - (q.demo ? 44 : 24) }, maxLines: 2
            }));
            if (q.done) slip.add(scene.add.image(sw / 2 - 52, sh / 2 - 22, stampTex(scene, w('SPLNĚNO', 'DONE'), '#2f7a3a', 104, 40, 3)).setRotation(-0.2).setAlpha(0.85));
            if (q.demo) cone(scene, slip, sw / 2 - 16, sh / 2 - 4, 22);
            put(c, slip);
            const px = b.x + b.w / 2 + Math.sin(rot) * (sh / 2 - 8), py = b.y + b.h / 2 - lift - Math.cos(rot) * (sh / 2 - 8);
            pinAt(c, px, py, pin);
            if (on) {
                put(c, markChosen(scene, 'apprentice', b.x + b.w / 2, b.y + b.h / 2 - lift, sw + 4, sh + 4).setRotation(rot));
                pinPos = { x: px, y: py };
            }
        },
        over: (c, box) => {
            if (!box || !pinPos) { pinPos = null; return; }
            // a red thread from the chosen slip's pin to the note's pin, sagging a little
            const a = pinPos, z = notePin;
            const m = { x: (a.x + z.x) / 2, y: Math.max(a.y, z.y) + 12 };      // nearly taut: over the other slips' pins, not their text
            const g = put(c, scene.add.graphics());
            g.lineStyle(2, 0xb3261e, 0.9).beginPath();
            for (let i = 0; i <= 24; i++) {
                const t = i / 24, u = 1 - t;
                const x = u * u * a.x + 2 * u * t * m.x + t * t * z.x, y = u * u * a.y + 2 * u * t * m.y + t * t * z.y;
                if (i) g.lineTo(x, y); else g.moveTo(x, y);
            }
            g.strokePath();
            pinPos = null;
        },
        detailOf: (c, q, dw) => {
            let y = 0;
            const t = put(c, scene.add.text(0, y, q.title, { ...T.title, wordWrap: { width: dw } }));
            y += t.height + 2;
            put(c, scene.add.graphics().lineStyle(1.5, 0x8a3a2a, 0.7).lineBetween(0, y + 2, dw - 6, y));
            y += 8;
            if (q.done) {
                put(c, scene.add.image(dw - 54, y + 20, stampTex(scene, w('SPLNĚNO', 'DONE'), '#2f7a3a', 108, 42, 5)).setRotation(-0.18));
                y += 44;
            }
            const d = put(c, scene.add.text(0, y, q.description, { ...T.body, wordWrap: { width: dw } }));
            y += d.height + 12;
            if (q.demo) {
                const n = put(c, scene.add.text(30, y, ctx.strings.demoNote, { ...T.body, color: '#b8601a', wordWrap: { width: dw - 32 } }));
                cone(scene, c, 12, y + Math.max(24, n.height), 24);
                y += Math.max(28, n.height) + 12;
            }
            if (q.updates.length) {
                put(c, scene.add.text(0, y, progressLabel(ctx), { ...T.small, fontStyle: 'bold', color: '#8a3a2a' }));
                y += 24;
                q.updates.forEach((u, i) => {
                    const last = i === q.updates.length - 1 && !q.done;
                    const line = scene.add.text(14, y, u, { ...T.later, wordWrap: { width: dw - 16 } });
                    if (last) put(c, scene.add.rectangle(10, y + 3, Math.min(dw - 10, line.width + 8), line.height - 2, 0xf3e05a, 0.5).setOrigin(0));   // a highlighter on the latest
                    put(c, scene.add.text(0, y, '•', { ...T.later }));
                    put(c, line);
                    y += line.height + 2;
                });
            }
            return y + 6;
        },
        empty: (c, text) => put(c, scene.add.text(40 + 358, 200, text, { ...T.hand, fontSize: '24px', color: '#fbf0dc', align: 'center', wordWrap: { width: 460 } })
            .setOrigin(0.5).setShadow(0, 2, '#000', 4, false, true))
    });
}

// ---------------------------------------------------------------------------------------------------------------
// the office: Úřední záznamy, numbered forms in a tray, the record on the index card

function buildForms(scene, ctx) {
    const { W, H } = ctx, w = words(ctx), O = LOOK.office, T = O.text;
    const BLUE = '#2d4fa0', RED = '#b0302a';
    const TRAY = { x: 26, y: 66, w: 676, h: 504 };
    scene.add.image(0, 0, tex(scene, 'qs_forms2', W, H, (c) => {
        const g = c.createLinearGradient(0, 0, 0, H);
        g.addColorStop(0, '#56645a'); g.addColorStop(1, '#3a453d');
        c.fillStyle = g; c.fillRect(0, 0, W, H);
        speckle(c, 0, 0, W, H, 14000, '0,0,0', 21, 0.03, 0.09);
        c.fillStyle = 'rgba(0,0,0,0.35)'; c.fillRect(TRAY.x + 4, TRAY.y + 4, TRAY.w, TRAY.h);
        c.fillStyle = '#2c3530'; c.fillRect(TRAY.x, TRAY.y, TRAY.w, TRAY.h);
        c.fillStyle = 'rgba(0,0,0,0.4)'; c.fillRect(TRAY.x, TRAY.y, TRAY.w, 8); c.fillRect(TRAY.x, TRAY.y, 8, TRAY.h);
        c.strokeStyle = '#8f9a90'; c.lineWidth = 2; c.strokeRect(TRAY.x, TRAY.y, TRAY.w, TRAY.h);
    })).setOrigin(0).setDepth(0);
    scene.add.text(TRAY.x + TRAY.w - 10, TRAY.y - 12, w('PODATELNA · BOUDA 521', 'REGISTRY · SHED 521'), { ...T.small, color: '#c8d0c4' }).setOrigin(1, 0.5).setDepth(1);
    const card = detailCard(scene, 'office');
    return questScreen(scene, ctx, {
        list: { x: TRAY.x + 14, y: TRAY.y + 14, w: TRAY.w - 28, h: TRAY.h - 28, rowH: 68, maskPad: 10, railGap: 2 },
        card,
        text: { x: 20, y: 62, w: card.w - 40, h: card.h - 80 },
        rail: 0x2f4a3a,
        tabs: tabsOf(scene, 'office', ctx, TRAY.x + 4, TRAY.y - 11),
        row: (c, q, b, { on, hov }) => {
            const x = b.x + 2, y = b.y + 4, rw = b.w - 4, rh = b.h - 8;
            put(c, scene.add.rectangle(x + 3, y + 3, rw, rh, 0x000000, 0.3).setOrigin(0));
            put(c, scene.add.rectangle(x, y, rw, rh, on ? 0xffffff : hov ? 0xf4f5ea : 0xe2e6d6).setOrigin(0).setStrokeStyle(1, 0x8f9a90));
            for (let py = y + 8; py < y + rh - 4; py += 10) put(c, scene.add.circle(x + 14, py, 2, 0x56645a));
            put(c, scene.add.text(x + 26, y + 6, `${w('Č.', 'No.')} ${number(ctx, q)}`, { ...T.small, letterSpacing: 1, color: '#4a5a4e' }));
            ell(put(c, scene.add.text(x + 26, y + 20, q.title, { ...T.title, fontSize: '15px', color: q.done ? '#5a6a5e' : '#1f2a22' })), rw - 170);
            ell(put(c, scene.add.text(x + 26, y + 40, latest(q), { ...T.later, fontSize: '12px' })), rw - (q.demo ? 70 : 40));
            const word = q.done ? w('SCHVÁLENO', 'APPROVED') : w('VYŘIZUJE SE', 'PENDING');
            put(c, scene.add.image(x + rw - 70, y + 22, stampTex(scene, word, q.done ? RED : BLUE, 116, 32, hash(q.key))).setRotation(-0.07).setAlpha(0.9));
            if (q.demo) cone(scene, c, x + rw - 16, y + rh - 4, 20);
            if (on) put(c, markChosen(scene, 'office', x + rw / 2, y + rh / 2, rw + 6, rh + 6));
        },
        head: (c, q) => {
            put(c, scene.add.text(60, 20, `${w('ZÁZNAM Č.', 'RECORD No.')} ${number(ctx, q)}`, T.small));      // (right of the paper clip)
            put(c, scene.add.image(card.w - 58, 30, stampTex(scene, q.done ? w('SCHVÁLENO', 'APPROVED') : w('VYŘIZUJE SE', 'PENDING'), q.done ? RED : BLUE, 108, 40, 9))
                .setRotation(-0.12).setAlpha(0.88));
        },
        detailOf: (c, q, dw) => {
            const label = (y, s) => put(c, scene.add.text(0, y, s, { ...T.small, color: '#6a7a6e' }));
            const rule = (y) => put(c, scene.add.rectangle(0, y, dw, 1, 0x2f4a3a, 0.3).setOrigin(0));
            let y = 0;
            label(y, w('PŘEDMĚT', 'SUBJECT'));
            const t = put(c, scene.add.text(0, y + 16, q.title, { ...T.title, wordWrap: { width: dw } }));
            y += 16 + t.height + 8;
            rule(y); y += 10;
            label(y, w('POPIS', 'DESCRIPTION'));
            const d = put(c, scene.add.text(0, y + 16, q.description, { ...T.body, wordWrap: { width: dw } }));
            y += 16 + d.height + 10;
            if (q.demo) {
                const n = scene.add.text(38, y + 9, ctx.strings.demoNote, { ...T.body, fontStyle: 'italic', fontSize: '13px', color: '#8a4a12', wordWrap: { width: dw - 50 } });
                const bh = Math.max(36, n.height + 18);
                put(c, scene.add.rectangle(0, y, dw, bh, 0xf6d9a0, 0.6).setOrigin(0).setStrokeStyle(1, 0xb8601a));
                cone(scene, c, 19, y + bh - 6, 24);
                put(c, n);
                y += bh + 12;
            }
            rule(y); y += 10;
            label(y, progressLabel(ctx).toUpperCase());
            y += 20;
            if (!q.updates.length) { label(y, '·'); y += 20; }
            q.updates.forEach((u, i) => {
                put(c, scene.add.text(0, y + 2, String(i + 1).padStart(2, '0'), { ...T.small, letterSpacing: 0, color: O.LATER }));
                const tx = put(c, scene.add.text(26, y, u, { ...T.later, wordWrap: { width: dw - 26 } }));
                y += tx.height + 5;
                put(c, scene.add.rectangle(26, y, dw - 26, 1, 0x2f4a3a, 0.15).setOrigin(0));
                y += 6;
            });
            if (q.done) {
                y += 8;
                label(y, w('VYŘÍZENO, ULOŽIT DO SPISU', 'SETTLED, TO BE FILED'));
                y += 20;
            }
            return y + 4;
        },
        empty: (c, text) => put(c, scene.add.text(TRAY.x + TRAY.w / 2, 220, text, { ...T.small, fontSize: '13px', color: '#d8dccb', align: 'center', wordWrap: { width: 420 } }).setOrigin(0.5))
    });
}

export const QUEST_SCREENS = { apprentice: buildBoard, office: buildForms };
