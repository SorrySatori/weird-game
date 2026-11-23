/**
 * journalScreens.js — the JOURNAL screen in the two panel sets (ui/panelStyle.js, Settings "Vzhled panelů"):
 *
 *   apprentice  the apprentice's notebook: an open squared notebook, his handwriting (Caveat), coloured sticky tabs
 *               for the categories down its left edge, the entries running over both pages (more pages: turn over);
 *               the chosen entry ringed in red pencil, its text on the pinned note beside the notebook, what he
 *               learned later in green ink
 *   office      the dossiers: a manila folder with folder tabs, a typed index (number, name, the latest line); the
 *               chosen file in red ink brackets, its text on the office index card (typed head, Georgia text), the
 *               addenda stapled on in blue biro
 *
 * JournalUI builds it: JOURNAL_SCREENS[panelSet()](scene, ctx) → { refresh(), key(code, event) }.
 *
 * ctx (ui/JournalUI.js screenCtx):
 *   scene, W, H, lang, t(key, params, fallback), title ('Deník')
 *   categories() → [{ key: 'People' | 'Places' | 'Events' | 'Lore' | 'Dreams' | 'Factions', label, unread }]
 *   category() → the open category key, setCategory(key)  (marks it read; then redraw yourself)
 *   entries(category = open one) → newest first: [{ key, title, description, facts: [text], category, categoryLabel, updated }]
 *     (description = what the player knew when it was written; facts = what was learned since, oldest first)
 *   allEntries() → every entry, newest first
 *   factions() → the discovered factions: [{ key, name, value (-100..100), standing (word), status (line), description }]
 *     (the Factions category shows these as well as its entries)
 *   empty() → the text for an empty category, strings: { factionStanding, factionRecords, noFactions, noFactionRecords }
 *   sound(key, vol), close()
 * refresh() is called when something new is learned while it's open.
 *
 * Both share one engine (journalScreen): the state (the open category, the chosen row, the hovered one, the list's
 * and the text's scroll), the keys (↑ / ↓ choose, ← / → / Tab change the category, PgUp / PgDn scroll the text), and
 * the pointer (hover is worked out from 'pointermove' over the rows' boxes; a click chooses; the wheel scrolls the
 * list or the text, whichever it is over). A screen only draws: its backdrop, the tabs, a row, the chosen entry's
 * text on the detail card, the empty text.
 */
import { tex, rng, hash } from '../paperKit.js';
import { LOOK, detailCard, markChosen, drawTabs } from '../panelStyle.js';

const MONO = 'Departure Mono', SERIF = 'Georgia';

const STR = {
    cs: { later: 'Dopsáno později', addendum: 'DODATEK', confidential: 'DŮVĚRNÉ', file: 'SPIS Č.', index: 'REJSTŘÍK', rating: 'HODNOCENÍ', turn: 'otoč list ›' },
    en: { later: 'Added later', addendum: 'ADDENDUM', confidential: 'CONFIDENTIAL', file: 'FILE NO.', index: 'INDEX', rating: 'RATING', turn: 'turn the page ›' }
};

const sgn = (v) => `${v >= 0 ? '+' : ''}${v}`;
const num = (key) => String(hash(key) % 900 + 100);

/** cut a one-line text to maxW with an ellipsis */
function ellipsize(t, maxW) {
    let s = t.text;
    while (t.width > maxW && s.length > 3) { s = s.slice(0, -1); t.setText(s.trimEnd() + '…'); }
    return t;
}

function speckle(c, x, y, w, h, n, col, seed, a0 = 0.03, a1 = 0.09) {
    const r = rng(seed);
    for (let i = 0; i < n; i++) {
        c.fillStyle = `rgba(${col},${a0 + r() * (a1 - a0)})`;
        c.fillRect(x + r() * w, y + r() * h, 1 + r() * 2, 1 + r() * 1.5);
    }
}

/** a standing -100..100 as 20 cells: [░░░░░░░░░░|████░░░░░░] (Departure Mono has the block glyphs) */
function cellGauge(v) {
    const n = Math.round(Math.min(100, Math.abs(v)) / 10);
    const left = v < 0 ? '░'.repeat(10 - n) + '█'.repeat(n) : '░'.repeat(10);
    const right = v >= 0 ? '█'.repeat(n) + '░'.repeat(10 - n) : '░'.repeat(10);
    return `[${left}|${right}]`;
}

// ---------------------------------------------------------------------------------------------------------------
// the engine

/**
 * D: {
 *   list: { x, y, w, h, row, cols?, paged? }   paged: the columns are pages (filled one after the other, the list
 *                                              turns a whole spread at a time) instead of rows across; in the
 *                                              Factions category each page is a section (left the standings, right
 *                                              the records), otherwise the sections follow each other as rows
 *   card: detailCard(...), area: { x, y, w, h }  where the chosen entry's text scrolls, in the card's own coords
 *   railColor,
 *   backdrop(),                                 static things
 *   tabs(c, categories, current)                draws the tabs into c (drawTabs: their zones give the hit boxes)
 *   row(c, item, rect, { sel, hov, k }),        item: { kind: 'entry' | 'faction', key, title, sub, e | f }
 *   heading(c, text, rect), note(c, text, rect)  the Factions category's two sections: their headings and the line
 *                                              for a section with nothing in it (the standings, then the records)
 *   head?(c, item)                              the card's fixed head (not scrolling), in card coords
 *   detail(c, item, w) → height,                c sits at the area's top-left (it scrolls)
 *   empty(c, text), pager?(c, page, pages, turn)  (c: an unmasked layer)
 * }
 */
function journalScreen(scene, ctx, D) {
    const st = { sel: null, hover: null, scroll: 0, dscroll: 0, follow: true, dh: 0 };
    D.backdrop();
    const tabsC = scene.add.container(0, 0).setDepth(3);
    const listC = scene.add.container(0, 0).setDepth(2);
    const overC = scene.add.container(0, 0).setDepth(4);
    const LR = D.list, card = D.card, A = D.area;
    const maskOf = (x, y, w, h) => scene.add.graphics().setVisible(false).fillRect(x, y, w, h).createGeometryMask();
    listC.setMask(maskOf(LR.x - 40, LR.y - 6, (LR.paged ? LR.span : LR.w) + 60, LR.h + 12));
    // the card's text window, on screen (the card is tilted only a hair)
    const AS = { x: card.x + A.x, y: card.y + A.y, w: A.w, h: A.h };
    const detMask = maskOf(AS.x - 10, AS.y - 4, AS.w + 20, AS.h + 6);
    const headC = scene.add.container(0, 0);
    card.body.add(headC);
    let inner = null, tabHits = [], rowHits = [];

    const items = () => {
        const ents = ctx.entries().map(e => ({
            kind: 'entry', key: e.key, title: e.title, sub: (e.facts.length ? e.facts[e.facts.length - 1] : e.description || '').split('\n')[0], e
        }));
        if (ctx.category() !== 'Factions') return ents;
        return [...ctx.factions().map(f => ({ kind: 'faction', key: `f:${f.key}`, title: f.name, sub: `${f.standing} · ${sgn(f.value)}`, f })), ...ents];
    };
    const cols = LR.cols || 1, vis = Math.max(1, Math.floor(LR.h / LR.row));
    const cw = LR.paged ? LR.colStep : LR.w / cols;
    // the Factions category in two sections, so the same names don't read as a list given twice: the standings,
    // then the records (the general notes), each with a heading and a line of its own when it has nothing
    const groupsOf = (its) => (ctx.category() === 'Factions' ? [
        { heading: ctx.strings.factionStanding, empty: ctx.strings.noFactions, items: its.filter(i => i.kind === 'faction') },
        { heading: ctx.strings.factionRecords, empty: ctx.strings.noFactionRecords, items: its.filter(i => i.kind === 'entry') }
    ] : null);
    /**
     * Where everything goes: { place(scroll) → [{ it | heading | note, rect }], max (the scroll's range), pages,
     * at(i) → the scroll that shows item i, rows (scrolling by rows, not by spreads) }
     */
    const layout = (its) => {
        const groups = groupsOf(its);
        if (LR.paged) {
            const box = (c, r) => ({ x: LR.x + c * cw, y: LR.y + r * LR.row, w: LR.w, h: LR.row, inView: true });
            if (groups) {                                    // a page each, its heading on the top line
                const per = vis - 1;
                const pages = Math.max(1, ...groups.map(g => Math.ceil(g.items.length / per)));
                return {
                    pages, max: pages - 1,
                    at: (i) => { const g = groups.find(gr => gr.items.includes(its[i])); return Math.floor(g.items.indexOf(its[i]) / per); },
                    place: (p) => groups.flatMap((g, c) => [
                        { heading: g.heading, rect: box(c, 0) },
                        ...(g.items.length ? g.items.slice(p * per, (p + 1) * per).map((it, r) => ({ it, rect: box(c, r + 1) }))
                            : (p === 0 ? [{ note: g.empty, rect: box(c, 1) }] : []))
                    ])
                };
            }
            const per = cols * vis, pages = Math.max(1, Math.ceil(its.length / per));
            return { pages, max: pages - 1, at: (i) => Math.floor(i / per), place: (p) => its.slice(p * per, (p + 1) * per).map((it, j) => ({ it, rect: box(Math.floor(j / vis), j % vis) })) };
        }
        // rows: a heading or an empty line takes a row of its own
        const slots = groups ? groups.flatMap(g => [{ heading: g.heading }, ...(g.items.length ? g.items.map(it => ({ it })) : [{ note: g.empty }])]) : its.map(it => ({ it }));
        const rowsN = Math.ceil(slots.length / cols);
        return {
            pages: rowsN, max: Math.max(0, rowsN - vis), rows: true,
            at: (i) => Math.floor(slots.findIndex(sl => sl.it === its[i]) / cols),
            place: (s0) => slots.map((sl, j) => {
                const r = Math.floor(j / cols) - s0, c = j % cols;
                return r < -1 || r > vis ? null : { ...sl, rect: { x: LR.x + c * cw, y: LR.y + r * LR.row, w: cw, h: LR.row, inView: r >= 0 && r < vis } };
            }).filter(Boolean)
        };
    };

    const fix = (its, lay) => {
        if (st.sel && !its.some(i => i.key === st.sel)) st.sel = null;
        if (st.hover && !its.some(i => i.key === st.hover)) st.hover = null;
        if (!st.sel && its.length) { st.sel = its[0].key; st.follow = true; }
        const i = its.findIndex(x => x.key === st.sel);
        if (i >= 0 && st.follow) { const t = lay.at(i); st.scroll = lay.rows ? Phaser.Math.Clamp(st.scroll, t - vis + 1, t) : t; }
        st.follow = false;
        st.scroll = Phaser.Math.Clamp(st.scroll, 0, lay.max);
    };
    const rail = (x, y, h, frac, size) => overC.add(scene.add.rectangle(x, y + (h - h * size) * frac, 3, Math.max(20, h * size), D.railColor, 0.75).setOrigin(0));
    const turn = (d) => { st.scroll += d; redraw(); ctx.sound('clickSound'); };

    const redraw = () => {
        const its = items(), lay = layout(its);
        fix(its, lay);
        for (const c of [tabsC, listC, overC, headC]) c.removeAll(true);
        D.tabs(tabsC, ctx.categories(), ctx.category());
        tabHits = tabsC.list.filter(o => o.type === 'Zone').map(z => ({ key: z.getData('key'), x: z.x - z.width / 2, y: z.y - z.height / 2, w: z.width, h: z.height }));
        rowHits = [];
        lay.place(st.scroll).forEach(pl => {
            if (pl.heading) { D.heading(listC, pl.heading, pl.rect); return; }
            if (pl.note) { D.note(listC, pl.note, pl.rect); return; }
            const sel = pl.it.key === st.sel;
            D.row(listC, pl.it, pl.rect, { sel, hov: pl.it.key === st.hover && !sel, k: its.indexOf(pl.it) });
            if (pl.rect.inView) rowHits.push({ key: pl.it.key, x: pl.rect.x, y: pl.rect.y, w: pl.rect.w, h: pl.rect.h });
        });
        if (!its.length && !groupsOf(its)) D.empty(listC, ctx.empty());
        if (LR.paged) D.pager?.(overC, st.scroll, lay.pages, turn);
        else if (lay.max > 0) rail(LR.x + LR.w + (LR.railDx ?? 6), LR.y, LR.h, st.scroll / lay.max, vis / lay.pages);
        const it = its.find(x => x.key === st.sel);
        inner?.destroy();
        inner = scene.add.container(A.x, A.y).setMask(detMask);
        card.body.add(inner);
        if (it) D.head?.(headC, it);
        st.dh = it ? D.detail(inner, it, A.w) : 0;
        st.dscroll = Phaser.Math.Clamp(st.dscroll, 0, Math.max(0, st.dh - A.h));
        inner.y = A.y - st.dscroll;
        if (st.dh > A.h) rail(card.x + card.w + 6, AS.y, AS.h, st.dscroll / (st.dh - A.h), A.h / st.dh);
    };

    const scrollDetail = (d) => {
        const v = Phaser.Math.Clamp(st.dscroll + d, 0, Math.max(0, st.dh - A.h));
        if (v !== st.dscroll) { st.dscroll = v; redraw(); }
    };
    const pickCategory = (key) => {
        if (!key || key === ctx.category()) return;
        ctx.setCategory(key);
        st.sel = null; st.hover = null; st.scroll = 0; st.dscroll = 0; st.follow = true;
        ctx.sound('clickSound');
        redraw();
    };
    const inR = (p, r) => p.x >= r.x && p.x <= r.x + r.w && p.y >= r.y && p.y <= r.y + r.h;
    scene.input.on('pointermove', (p) => {
        const h = rowHits.find(r => inR(p, r)), key = h ? h.key : null;
        if (!tabHits.some(r => inR(p, r))) scene.input.setDefaultCursor(h ? 'pointer' : 'default');
        if (key !== st.hover) { st.hover = key; if (key && key !== st.sel) ctx.sound('hoverSound', 0.25); redraw(); }
    });
    scene.input.on('pointerdown', (p) => {
        const t = tabHits.find(r => inR(p, r));
        if (t) { pickCategory(t.key); return; }
        const h = rowHits.find(r => inR(p, r));
        if (h && h.key !== st.sel) { st.sel = h.key; st.dscroll = 0; ctx.sound('clickSound'); redraw(); }
    });
    scene.input.on('gameout', () => { if (st.hover) { st.hover = null; redraw(); } });
    scene.input.on('wheel', (p, o, dx, dy) => {
        if (inR(p, { x: card.x - 6, y: card.y - 6, w: card.w + 24, h: card.h + 12 })) scrollDetail(Math.sign(dy) * 40);
        else if (inR(p, { x: LR.x - 30, y: LR.y - 12, w: (LR.paged ? LR.span : LR.w) + 50, h: LR.h + 24 })) {
            const v = Phaser.Math.Clamp(st.scroll + Math.sign(dy), 0, layout(items()).max);
            if (v !== st.scroll) { st.scroll = v; redraw(); }
        }
    });
    scene.events.once('shutdown', () => scene.input.setDefaultCursor('default'));
    redraw();

    return {
        refresh: redraw,
        key(code, ev) {
            const its = items(), i = its.findIndex(x => x.key === st.sel);
            if (['ArrowDown', 'KeyS', 'ArrowUp', 'KeyW'].includes(code)) {
                if (!its.length) return;
                const d = code === 'ArrowDown' || code === 'KeyS' ? 1 : -1;
                const j = Phaser.Math.Clamp(i < 0 ? 0 : i + d, 0, its.length - 1);
                if (its[j].key === st.sel) return;
                st.sel = its[j].key; st.dscroll = 0; st.follow = true;
                ctx.sound('hoverSound', 0.3);
                redraw();
            } else if (['ArrowLeft', 'KeyA', 'ArrowRight', 'KeyD', 'Tab'].includes(code)) {
                ev?.preventDefault?.();
                const cats = ctx.categories(), j = cats.findIndex(c => c.key === ctx.category());
                const d = code === 'ArrowLeft' || code === 'KeyA' ? -1 : 1;
                pickCategory(cats[(j + d + cats.length) % cats.length].key);
            } else if (code === 'PageDown' || code === 'PageUp') {
                scrollDetail((code === 'PageDown' ? 1 : -1) * (A.h - 60));
            }
        }
    };
}

/** the tabs through panelStyle's drawTabs; each zone remembers its category (the engine does the clicking) */
function tabsVia(scene, set, c, cats, cur, x, y, opts) {
    drawTabs(scene, set, c, x, y, cats.map(k => ({ label: k.label, badge: k.unread })), cats.findIndex(k => k.key === cur), () => {}, opts);
    c.list.filter(o => o.type === 'Zone').forEach((z, i) => z.setData('key', cats[i].key));
}

// ---------------------------------------------------------------------------------------------------------------
// apprentice: the notebook

function buildNotebook(scene, ctx) {
    const { W, H } = ctx, S = STR[ctx.lang] || STR.cs, L = LOOK.apprentice;
    // Caveat's strokes reach past its own box (a last letter lost its tail): pad every text
    const T = Object.fromEntries(Object.entries(L.text).map(([k, v]) => [k, { ...v, padding: { x: 5, y: 3 } }]));
    const add = (c, o) => { c.add(o); return o; };
    const NB = { x: 84, y: 22, w: 692, h: 556 };                     // the notebook, open
    const PG = [{ x: 96, w: 336 }, { x: 440, w: 324 }];               // its pages
    let card;
    return journalScreen(scene, ctx, {
        list: { x: 146, y: 102, w: 272, h: 440, row: 48, cols: 2, paged: true, colStep: 344, span: 616 },
        get card() { return card; },
        area: { x: 18, y: 30, w: 214, h: 430 },
        railColor: L.MARK,
        backdrop() {
            scene.add.image(0, 0, tex(scene, 'jn_nb_bg2', W, H, (c) => {
                c.fillStyle = '#1b130d'; c.fillRect(0, 0, W, H);
                const r = rng(4);
                for (let i = 0; i < 120; i++) {
                    c.strokeStyle = `rgba(0,0,0,${0.15 + r() * 0.2})`; c.lineWidth = 0.6 + r() * 1.4;
                    const y = r() * H; c.beginPath(); c.moveTo(0, y);
                    for (let x = 0; x <= W; x += 60) c.lineTo(x, y + Math.sin(x / 80 + i) * 4);
                    c.stroke();
                }
                c.save(); c.filter = 'blur(10px)'; c.fillStyle = 'rgba(0,0,0,0.75)'; c.fillRect(NB.x + 10, NB.y + 12, NB.w, NB.h); c.restore();
                c.fillStyle = '#2a4634'; c.beginPath(); c.roundRect(NB.x, NB.y, NB.w, NB.h, 10); c.fill();          // the cover
                for (const p of PG) {
                    c.fillStyle = '#f3ecd9'; c.fillRect(p.x, NB.y + 10, p.w, NB.h - 20);
                    speckle(c, p.x, NB.y + 10, p.w, NB.h - 20, 3000, '120,90,40', p.x, 0.02, 0.06);
                    c.strokeStyle = 'rgba(80,120,170,0.18)'; c.lineWidth = 1;
                    for (let x = p.x + 9; x < p.x + p.w; x += 18) { c.beginPath(); c.moveTo(x, NB.y + 10); c.lineTo(x, NB.y + NB.h - 10); c.stroke(); }
                    for (let y = NB.y + 19; y < NB.y + NB.h - 10; y += 18) { c.beginPath(); c.moveTo(p.x, y); c.lineTo(p.x + p.w, y); c.stroke(); }
                    c.strokeStyle = 'rgba(200,70,60,0.55)'; c.lineWidth = 1.5;
                    c.beginPath(); c.moveTo(p.x + 40, NB.y + 10); c.lineTo(p.x + 40, NB.y + NB.h - 10); c.stroke();
                }
                const g = c.createLinearGradient(418, 0, 456, 0);                                          // the gutter
                g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(0.45, 'rgba(0,0,0,0.28)'); g.addColorStop(0.55, 'rgba(0,0,0,0.28)'); g.addColorStop(1, 'rgba(0,0,0,0)');
                c.fillStyle = g; c.fillRect(418, NB.y + 10, 38, NB.h - 20);
                c.fillStyle = '#9a2a24'; c.fillRect(431, NB.y, 9, H - NB.y);                               // the ribbon
                // doodles at the top of the right page: a little clock (the Stomach Clock) and a spiral
                c.strokeStyle = 'rgba(34,64,122,0.45)'; c.lineWidth = 1.5;
                c.beginPath(); c.arc(726, 62, 15, 0, Math.PI * 2); c.stroke();
                c.beginPath(); c.moveTo(726, 62); c.lineTo(726, 52); c.moveTo(726, 62); c.lineTo(734, 66); c.stroke();
                c.beginPath(); for (let a = 0; a < 16; a += 0.2) { const rr = 1 + a * 0.9; const x = 680 + Math.cos(a) * rr, y = 62 + Math.sin(a) * rr; if (a) c.lineTo(x, y); else c.moveTo(x, y); } c.stroke();
            })).setOrigin(0).setDepth(0);
            card = detailCard(scene, 'apprentice');                     // the note pinned beside the notebook
        },
        tabs(c, cats, cur) {
            // the open category written at the top of the left page, the sticky tabs down the notebook's left edge
            const head = cats.find(x => x.key === cur);
            const h = add(c, scene.add.text(144, 34, head ? head.label : '', { ...T.title, fontSize: '38px' }));
            add(c, scene.add.graphics().lineStyle(2, L.MARK, 0.8).lineBetween(142, h.y + h.height - 2, 142 + h.width + 24, h.y + h.height - 5));
            tabsVia(scene, 'apprentice', c, cats, cur, 8, 60, { vertical: true });
        },
        row(c, it, r, { sel, hov }) {
            if (hov) add(c, scene.add.rectangle(r.x - 6, r.y + 5, r.w + 4, r.h - 8, 0xfff08a, 0.55).setOrigin(0));
            const t = add(c, scene.add.text(r.x + 4, r.y + 16, it.title, { ...T.hand, fontSize: '23px', color: '#22407a' }).setOrigin(0, 0.5));
            ellipsize(t, r.w - 14);
            ellipsize(add(c, scene.add.text(r.x + 6, r.y + 36, it.sub, { ...T.small, fontSize: '16px', color: it.kind === 'faction' ? L.LATER : '#5b6b85' }).setOrigin(0, 0.5)), r.w - 14);
            if (sel) add(c, markChosen(scene, 'apprentice', r.x + 4 + t.width / 2, r.y + 16, t.width + 12, 26));
        },
        detail(c, it, w) {
            let y = 0;
            y += add(c, scene.add.text(0, y, it.title, { ...T.title, wordWrap: { width: w, useAdvancedWrap: true } })).height;
            add(c, scene.add.graphics().lineStyle(1.5, L.MARK, 0.6).lineBetween(0, y + 1, w - 10, y - 1));
            y += 6;
            if (it.kind === 'faction') {
                const f = it.f, pos = f.value >= 0;
                y += add(c, scene.add.text(0, y, f.status, T.kind)).height + 10;
                const g = add(c, scene.add.graphics()), gw = w - 60, mid = gw / 2;
                g.lineStyle(2, 0x22407a, 0.8).lineBetween(0, y + 10, gw, y + 10);
                for (let k = 0; k <= 4; k++) g.lineBetween(gw * k / 4, y + 4, gw * k / 4, y + 16);
                g.fillStyle(pos ? L.LATER_HEX : L.MARK, 1).fillCircle(mid + mid * Phaser.Math.Clamp(f.value, -100, 100) / 100, y + 10, 6);
                add(c, scene.add.text(gw + 10, y + 10, sgn(f.value), { ...T.label, fontSize: '24px', color: pos ? L.LATER : L.MARK_CSS }).setOrigin(0, 0.5));
                y += 30;
                return y + add(c, scene.add.text(0, y, f.description, { ...T.hand, wordWrap: { width: w } })).height + 6;
            }
            const e = it.e;
            y += add(c, scene.add.text(0, y, e.categoryLabel, T.kind)).height + 6;
            if (e.description) y += add(c, scene.add.text(0, y, e.description, { ...T.hand, wordWrap: { width: w } })).height + 12;
            if (e.facts.length) {
                y += add(c, scene.add.text(0, y, `${S.later}:`, { ...T.later, fontStyle: 'bold' })).height + 2;
                for (const f of e.facts) {
                    const t = add(c, scene.add.text(12, y, f, { ...T.later, wordWrap: { width: w - 14 } }));
                    add(c, scene.add.rectangle(2, y + 4, 2.5, t.height - 6, L.LATER_HEX, 0.6).setOrigin(0));
                    y += t.height + 6;
                }
            }
            return y;
        },
        empty(c, text) { add(c, scene.add.text(148, 120, text, { ...T.hand, color: '#5b6b85', wordWrap: { width: 270 } })); },
        heading(c, text, r) {
            // the strings are capitals: written by hand in sentence case
            const t = add(c, scene.add.text(r.x, r.y + 18, text.charAt(0) + text.slice(1).toLowerCase(), { ...T.label, fontSize: '24px', color: '#8a3a2a' }).setOrigin(0, 0.5));
            add(c, scene.add.graphics().lineStyle(1.5, L.MARK, 0.55).lineBetween(r.x + 4, r.y + 34, r.x + t.width - 6, r.y + 32));
        },
        note(c, text, r) { add(c, scene.add.text(r.x + 4, r.y + 6, text, { ...T.small, color: '#5b6b85', wordWrap: { width: r.w - 10 } })); },
        pager(c, page, pages, turn) {
            // the page numbers at the bottom corners; "turn over" when there are more
            add(c, scene.add.text(PG[0].x + 22, NB.y + NB.h - 26, String(page * 2 + 1), { ...T.small, color: '#7a8aa5' }).setOrigin(0.5));
            add(c, scene.add.text(PG[1].x + PG[1].w - 22, NB.y + NB.h - 26, String(page * 2 + 2), { ...T.small, color: '#7a8aa5' }).setOrigin(0.5));
            if (page > 0) add(c, scene.add.text(PG[0].x + 60, NB.y + NB.h - 26, `‹ ${S.turn.replace(' ›', '')}`, { ...T.small, color: L.MARK_CSS }).setOrigin(0, 0.5))
                .setInteractive({ useHandCursor: true }).on('pointerdown', () => turn(-1));
            if (page < pages - 1) add(c, scene.add.text(PG[1].x + PG[1].w - 48, NB.y + NB.h - 26, S.turn, { ...T.small, color: L.MARK_CSS }).setOrigin(1, 0.5))
                .setInteractive({ useHandCursor: true }).on('pointerdown', () => turn(1));
        }
    });
}

// ---------------------------------------------------------------------------------------------------------------
// office: the dossiers

function buildDossier(scene, ctx) {
    const { W, H } = ctx, S = STR[ctx.lang] || STR.cs, L = LOOK.office, T = L.text;
    const add = (c, o) => { c.add(o); return o; };
    const FOLDER = { x: 30, y: 64, w: 1010, h: 524 };
    const IDX = { x: 50, y: 86, w: 652, h: 488 };
    let card;
    const catLabel = (it) => (it.kind === 'faction' ? (ctx.categories().find(x => x.key === 'Factions')?.label || '') : it.e.categoryLabel);
    const fileNo = (it) => (it.kind === 'faction' ? `F${num(it.key).slice(1)}` : num(it.key));
    return journalScreen(scene, ctx, {
        list: { x: IDX.x + 18, y: IDX.y + 52, w: IDX.w - 40, h: IDX.h - 66, row: 34 },
        get card() { return card; },
        area: { x: 20, y: 62, w: L.DETAIL.w - 40, h: L.DETAIL.h - 78 },
        railColor: 0x8a6a3a,
        backdrop() {
            scene.add.image(0, 0, tex(scene, 'jn_dossier_bg2', W, H, (c) => {
                c.fillStyle = '#34413b'; c.fillRect(0, 0, W, H);
                c.strokeStyle = 'rgba(0,0,0,0.12)'; c.lineWidth = 1;
                for (let k = -H; k < W; k += 14) { c.beginPath(); c.moveTo(k, 0); c.lineTo(k + H, H); c.stroke(); }
                const g = c.createRadialGradient(260, 80, 20, 260, 80, 760);
                g.addColorStop(0, 'rgba(255,230,170,0.18)'); g.addColorStop(1, 'rgba(0,0,0,0.45)');
                c.fillStyle = g; c.fillRect(0, 0, W, H);
                c.save(); c.filter = 'blur(8px)'; c.fillStyle = 'rgba(0,0,0,0.6)'; c.fillRect(FOLDER.x + 6, FOLDER.y + 8, FOLDER.w, FOLDER.h); c.restore();
                c.fillStyle = '#d9b77a'; c.beginPath(); c.roundRect(FOLDER.x, FOLDER.y, FOLDER.w, FOLDER.h, 6); c.fill();
                speckle(c, FOLDER.x, FOLDER.y, FOLDER.w, FOLDER.h, 9000, '120,80,30', 11, 0.03, 0.09);
                c.strokeStyle = 'rgba(90,60,20,0.35)'; c.lineWidth = 2; c.beginPath(); c.moveTo(714, FOLDER.y); c.lineTo(714, FOLDER.y + FOLDER.h); c.stroke();
                c.fillStyle = 'rgba(0,0,0,0.25)'; c.fillRect(IDX.x + 4, IDX.y + 5, IDX.w, IDX.h);          // the typed index
                c.fillStyle = '#f5f2ea'; c.fillRect(IDX.x, IDX.y, IDX.w, IDX.h);
                speckle(c, IDX.x, IDX.y, IDX.w, IDX.h, 3000, '100,90,70', 12, 0.02, 0.05);
            })).setOrigin(0).setDepth(0);
            scene.add.text(IDX.x + 20, IDX.y + 16, S.index, { fontFamily: MONO, fontSize: '15px', color: '#222222', letterSpacing: 3 }).setDepth(1);
            scene.add.rectangle(IDX.x + 18, IDX.y + 40, IDX.w - 36, 2, 0x222222).setOrigin(0).setDepth(1);
            card = detailCard(scene, 'office');                          // the file: the office index card
        },
        tabs(c, cats, cur) { tabsVia(scene, 'office', c, cats, cur, 46, 53); },
        row(c, it, r, { sel, hov }) {
            if (hov) add(c, scene.add.rectangle(r.x - 8, r.y + 3, r.w + 16, r.h - 6, 0xe6e1d4).setOrigin(0));
            add(c, scene.add.text(r.x, r.y + r.h / 2, fileNo(it), { fontFamily: MONO, fontSize: '13px', color: '#8a8a8a' }).setOrigin(0, 0.5));
            ellipsize(add(c, scene.add.text(r.x + 48, r.y + r.h / 2, it.title.toUpperCase(), { fontFamily: MONO, fontSize: '13px', color: '#222222' }).setOrigin(0, 0.5)), 200);
            const subX = r.x + 268;
            if (it.kind === 'faction') {
                add(c, scene.add.text(subX, r.y + r.h / 2, it.f.standing, { fontFamily: SERIF, fontStyle: 'italic', fontSize: '12px', color: '#6a6a6a' }).setOrigin(0, 0.5));
                add(c, scene.add.text(r.x + r.w - 6, r.y + r.h / 2, sgn(it.f.value), { fontFamily: MONO, fontSize: '13px', color: it.f.value >= 0 ? L.LATER : L.MARK_CSS }).setOrigin(1, 0.5));
            } else {
                ellipsize(add(c, scene.add.text(subX, r.y + r.h / 2, it.sub, { fontFamily: SERIF, fontStyle: 'italic', fontSize: '12px', color: '#6a6a6a' }).setOrigin(0, 0.5)), r.w - 274);
            }
            if (sel) add(c, markChosen(scene, 'office', r.x + r.w / 2, r.y + r.h / 2, r.w + 16, r.h - 4));
        },
        head(c, it) {
            // the card's head: typed file number and category over the red line, a stamp on the right
            add(c, scene.add.text(58, 20, `${S.file} ${fileNo(it)}`, T.small));
            add(c, scene.add.text(58, 34, catLabel(it).toUpperCase(), T.small));
            const st = add(c, scene.add.text(L.DETAIL.w - 16, 30, S.confidential, { fontFamily: MONO, fontSize: '12px', color: '#c0302a', letterSpacing: 1 }).setOrigin(1, 0.5).setRotation(-0.08).setAlpha(0.55));
            add(c, scene.add.rectangle(st.x - st.width / 2, st.y, st.width + 12, st.height + 6).setStrokeStyle(2, 0xc0302a, 0.55).setRotation(-0.08));
        },
        detail(c, it, w) {
            let y = 0;
            y += add(c, scene.add.text(0, y, it.title.toUpperCase(), { fontFamily: MONO, fontSize: '17px', color: L.INK, wordWrap: { width: w, useAdvancedWrap: true } })).height + 10;
            if (it.kind === 'faction') {
                const f = it.f, pos = f.value >= 0;
                y += add(c, scene.add.text(0, y, `${S.rating}: ${f.standing.toUpperCase()}`, { fontFamily: MONO, fontSize: '12px', color: L.INK })).height + 6;
                y += add(c, scene.add.text(0, y, `${cellGauge(f.value)} ${sgn(f.value)}`, { fontFamily: MONO, fontSize: '12px', color: pos ? L.LATER : L.MARK_CSS })).height + 12;
                return y + add(c, scene.add.text(0, y, f.description, { ...T.body, wordWrap: { width: w } })).height + 6;
            }
            const e = it.e;
            if (e.description) y += add(c, scene.add.text(0, y, e.description, { ...T.body, wordWrap: { width: w } })).height + 14;
            e.facts.forEach((f, i) => {                                                                     // the addenda, stapled on, in blue biro
                const t = scene.add.text(12, 24, f, { ...T.later, wordWrap: { width: w - 26 } });
                const h = t.height + 34;
                add(c, scene.add.rectangle(0, y, w - 2, h, 0xeef2fb).setOrigin(0).setStrokeStyle(1, 0x9aa8d0, 0.8));
                add(c, scene.add.text(12, y + 8, `${S.addendum} ${i + 1}`, { fontFamily: MONO, fontSize: '11px', color: L.LATER, letterSpacing: 2 }));
                const g = add(c, scene.add.graphics().lineStyle(2, 0x8f969b, 1));
                g.lineBetween(w - 40, y - 3, w - 22, y - 3); g.lineBetween(w - 40, y + 3, w - 22, y + 3);
                t.y = y + 24; add(c, t);
                y += h + 10;
            });
            return y;
        },
        empty(c, text) { add(c, scene.add.text(IDX.x + 18, IDX.y + 64, text.toUpperCase(), { fontFamily: MONO, fontSize: '12px', color: '#8a8a8a', wordWrap: { width: IDX.w - 40 }, lineSpacing: 5 })); },
        heading(c, text, r) {
            add(c, scene.add.text(r.x, r.y + r.h / 2 + 4, text, { fontFamily: MONO, fontSize: '12px', color: L.MARK_CSS, letterSpacing: 2 }).setOrigin(0, 0.5));
            add(c, scene.add.rectangle(r.x, r.y + r.h - 4, r.w, 1, 0x8a8a8a).setOrigin(0));
        },
        note(c, text, r) { add(c, scene.add.text(r.x + 48, r.y + r.h / 2, text, { fontFamily: SERIF, fontStyle: 'italic', fontSize: '12px', color: '#8a8a8a' }).setOrigin(0, 0.5)); }
    });
}

export const JOURNAL_SCREENS = { apprentice: buildNotebook, office: buildDossier };
